# Active Directory Shadow Credentials

Shadow Credentials is an Active Directory attack technique that abuses write access to the `msDS-KeyCredentialLink` attribute of a user or computer object.

The attribute is used by legitimate certificate and key-based authentication mechanisms such as Windows Hello for Business.

If an attacker can modify this attribute on another security principal, they may be able to associate attacker-controlled key material with the victim account.

The simplified attack path is:

```text
Attacker
   |
   v
Write msDS-KeyCredentialLink
   |
   v
Victim User / Computer
   |
   v
Attacker-Controlled Key Credential
   |
   v
Kerberos PKINIT
   |
   v
Authenticate as Victim
```

This is commonly referred to as:

```text
Shadow Credentials
```

The technique is particularly important because it can turn seemingly indirect Active Directory object-control permissions into authentication as another principal.

!!! warning "Authorised testing only"
    Shadow Credentials modifies authentication-related data on an Active Directory object. During an authorised assessment, begin with ACL and attack-path analysis. Do not modify `msDS-KeyCredentialLink` on production identities unless active exploitation is explicitly authorised. Prefer a dedicated test account where possible, record the original attribute value before any modification, and restore the exact original state after validation.

---

# Core Concept

The attack relies on:

```text
msDS-KeyCredentialLink
```

This attribute can contain key credentials associated with an Active Directory object.

Conceptually:

```text
User / Computer
      |
      v
msDS-KeyCredentialLink
      |
      v
Key Credential
      |
      v
Public Key
      |
      v
Authentication
```

An attacker who can write a new key credential may create:

```text
Victim Account
      |
      +--> Legitimate Key
      |
      +--> Attacker Key
```

The victim's password does not need to be changed.

---

# Why It Is Called a Shadow Credential

The attacker adds another authentication credential behind the legitimate account.

Conceptually:

```text
Victim
 |
 +--> Password
 |
 +--> Existing Authentication Material
 |
 +--> Shadow Credential
          |
          v
      Attacker Key
```

The attacker's credential exists alongside the legitimate credentials.

This can make the technique useful for:

```text
Privilege Escalation
Lateral Movement
Alternative Authentication
Persistence
```

depending on the target and permissions.

---

# Important Distinction

Shadow Credentials does not normally mean:

```text
Password Reset
```

The victim's existing password remains unchanged.

Instead:

```text
Existing Account
      |
      v
Additional Key Credential
```

is created.

This is one reason the technique is important during Active Directory security assessments.

---

# Requirements

A typical Shadow Credentials attack requires several conditions.

Conceptually:

```text
Writable KeyCredentialLink
        +
Suitable Domain / PKINIT Environment
        +
Reachable KDC
        +
Usable Target Principal
        =
Potential Shadow Credentials Path
```

---

# Requirement 1 - Write Access

The attacker needs sufficient permission to modify:

```text
msDS-KeyCredentialLink
```

on the target object.

Potential paths may originate from rights such as:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

depending on the object's effective ACL and the exact ACEs involved.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# Requirement 2 - Target Object

The target is typically an Active Directory:

```text
User
```

or:

```text
Computer
```

object.

Example:

```text
CORP\alice
```

or:

```text
SERVER01$
```

---

# Requirement 3 - Kerberos PKINIT

The attack relies on Kerberos certificate/public-key authentication through:

```text
PKINIT
```

Conceptually:

```text
Certificate / Key
       |
       v
PKINIT
       |
       v
Kerberos AS-REQ
       |
       v
TGT
```

Therefore the domain must support the required certificate-based Kerberos authentication path.

---

# PKINIT

PKINIT stands for:

```text
Public Key Cryptography for Initial Authentication in Kerberos
```

Instead of proving knowledge of a traditional password-derived Kerberos key, the client can authenticate using public-key cryptography.

Conceptually:

```text
Traditional Kerberos

Password-Derived Key
        |
        v
AS-REQ
        |
        v
TGT
```

versus:

```text
PKINIT

Private Key + Certificate
        |
        v
AS-REQ
        |
        v
TGT
```

---

# Domain Controller Certificate Requirement

In many Active Directory environments, PKINIT requires the domain controller to possess an appropriate certificate that can be used for Kerberos authentication.

This commonly exists where:

```text
Active Directory Certificate Services
```

has been deployed and Domain Controllers have received appropriate certificates.

However:

```text
AD CS Exists
```

and:

```text
PKINIT Works
```

should not be treated as identical assumptions.

Validate the actual environment.

---

# Key Credential Link

The important attribute is:

```text
msDS-KeyCredentialLink
```

It contains one or more:

```text
KeyCredential
```

values.

Conceptually:

```text
msDS-KeyCredentialLink
        |
        +--> KeyCredential A
        |
        +--> KeyCredential B
        |
        +--> KeyCredential C
```

Each key credential can contain metadata describing the associated key.

---

# Key Credential Structure

The underlying KeyCredential data includes information associated with the authentication key.

Important concepts include:

```text
Key Identifier
Key Material
Key Usage
Key Source
Device Identifier
Creation Information
```

The exact binary structure is defined by Microsoft protocol specifications.

During normal assessment work, specialised tools generally parse and construct these values.

---

# DeviceID

Shadow Credentials tooling frequently refers to:

```text
DeviceID
```

or:

```text
DeviceId
```

associated with a KeyCredential.

This can help identify individual entries when reviewing or cleaning up:

```text
msDS-KeyCredentialLink
```

values.

---

# Legitimate Uses

The presence of:

```text
msDS-KeyCredentialLink
```

does not automatically indicate malicious activity.

Legitimate technologies can use key credentials.

One important example is:

```text
Windows Hello for Business
```

Therefore:

```text
KeyCredentialLink Present
       |
       X
Confirmed Compromise
```

Instead analyse:

```text
Who Added It?
When?
Which Account?
Which DeviceID?
Is It Expected?
```

---

# Windows Hello for Business

Windows Hello for Business can use key-based authentication associated with Active Directory identities.

Conceptually:

```text
User
 |
 v
Windows Hello for Business
 |
 v
Key-Based Credential
 |
 v
Active Directory
```

This legitimate use is important when detecting Shadow Credentials.

Defenders should avoid treating every KeyCredential as malicious.

---

# Attack Path

A common Shadow Credentials path is:

```text
Low-Privilege User
       |
       v
GenericWrite
       |
       v
Privileged User
       |
       v
Write msDS-KeyCredentialLink
       |
       v
Attacker Certificate
       |
       v
PKINIT
       |
       v
TGT as Privileged User
```

---

# Computer Attack Path

The target can also be a computer account.

```text
Attacker
   |
   v
Control Computer Object
   |
   v
msDS-KeyCredentialLink
   |
   v
Shadow Credential
   |
   v
Authenticate as COMPUTER$
```

This can become important when the computer account has:

```text
Local Privilege
Delegated Rights
RBCD Relationships
Service Access
AD CS Permissions
Other Directory Rights
```

---

# User vs Computer Targets

## User

```text
Shadow User
    |
    v
Authenticate as User
    |
    v
User's Privileges
```

## Computer

```text
Shadow Computer
      |
      v
Authenticate as COMPUTER$
      |
      v
Computer Account Privileges
```

Do not assume that a computer account has no useful privileges.

---

# Why Computer Accounts Matter

Computer accounts can participate in:

```text
Kerberos
LDAP
SMB
RBCD
AD CS
Directory ACLs
Service Authentication
```

and may possess delegated rights.

Therefore:

```text
Computer Account Compromise
```

can become an important Active Directory attack primitive.

---

# Common ACL Paths

Potential Shadow Credentials paths include:

```text
GenericAll
    |
    v
Target
```

```text
GenericWrite
     |
     v
Target
```

```text
WriteProperty
     |
     v
msDS-KeyCredentialLink
```

```text
WriteDACL
    |
    v
Grant Write Permission
    |
    v
msDS-KeyCredentialLink
```

```text
WriteOwner
    |
    v
Take Ownership
    |
    v
Modify DACL
    |
    v
Write KeyCredential
```

The exact effective permission should always be validated.

---

# GenericWrite

Suppose:

```text
alice
 |
 v
GenericWrite
 |
 v
bob
```

This may provide the ability to modify writable properties on Bob's object.

One possible abuse path may involve:

```text
msDS-KeyCredentialLink
```

depending on the effective permissions and object state.

---

# GenericAll

```text
alice
 |
 v
GenericAll
 |
 v
bob
```

represents broad control over Bob's object.

Shadow Credentials may be one of several possible abuse paths.

Other paths could include:

```text
Password Reset
SPN Modification
ACL Modification
Other Attribute Changes
```

depending on the target and environment.

Choose the least disruptive validation method.

---

# WriteProperty

An object-specific ACE may provide write access specifically to:

```text
msDS-KeyCredentialLink
```

This is a particularly direct Shadow Credentials relationship.

Conceptually:

```text
Alice
 |
 v
WriteProperty
 |
 v
msDS-KeyCredentialLink
 |
 v
Bob
```

---

# WriteDACL

A principal with:

```text
WriteDACL
```

may be able to modify the target object's discretionary ACL.

This can potentially create:

```text
WriteProperty
```

access to:

```text
msDS-KeyCredentialLink
```

The attack chain becomes:

```text
WriteDACL
    |
    v
Grant WriteProperty
    |
    v
Write KeyCredential
    |
    v
Authenticate as Target
```

---

# WriteOwner

A potential chain is:

```text
WriteOwner
    |
    v
Take Ownership
    |
    v
Modify DACL
    |
    v
Write KeyCredential
```

This introduces more directory modifications and should not be used merely because it is possible.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# Enumeration Strategy

Use:

```text
Enumerate Objects
      |
      v
Enumerate ACLs
      |
      v
Find KeyCredential Write Paths
      |
      v
Identify High-Value Targets
      |
      v
Validate Prerequisites
      |
      v
Decide Whether Active Validation Is Necessary
```

---

# PowerShell Enumeration

Retrieve the attribute for a user:

```powershell
Get-ADUser `
    -Identity 'alice' `
    -Properties msDS-KeyCredentialLink |
    Select-Object `
        SamAccountName,
        DistinguishedName,
        msDS-KeyCredentialLink
```

For a computer:

```powershell
Get-ADComputer `
    -Identity 'SERVER01' `
    -Properties msDS-KeyCredentialLink |
    Select-Object `
        SamAccountName,
        DistinguishedName,
        msDS-KeyCredentialLink
```

---

# Enumerate Users with Key Credentials

```powershell
Get-ADUser `
    -LDAPFilter '(msDS-KeyCredentialLink=*)' `
    -Properties msDS-KeyCredentialLink |
    Select-Object `
        SamAccountName,
        DistinguishedName,
        msDS-KeyCredentialLink
```

---

# Enumerate Computers with Key Credentials

```powershell
Get-ADComputer `
    -LDAPFilter '(msDS-KeyCredentialLink=*)' `
    -Properties msDS-KeyCredentialLink |
    Select-Object `
        SamAccountName,
        DistinguishedName,
        msDS-KeyCredentialLink
```

---

# Metadata First

The presence of values can be recorded without immediately modifying anything.

Use:

```text
Read
 |
 v
Understand
 |
 v
Correlate
 |
 v
Validate
```

before:

```text
Modify
```

---

# LDAP Enumeration

Using `ldapsearch`:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(msDS-KeyCredentialLink=*)' \
    sAMAccountName \
    objectClass \
    distinguishedName \
    msDS-KeyCredentialLink
```

The raw attribute may not be human-friendly.

Specialised tools can parse KeyCredential structures more effectively.

---

# ACL Enumeration

PowerShell:

```powershell
$target = Get-ADUser 'bob'

Get-Acl "AD:\$($target.DistinguishedName)"
```

Detailed:

```powershell
(Get-Acl "AD:\$($target.DistinguishedName)").Access |
    Format-Table `
        IdentityReference,
        ActiveDirectoryRights,
        AccessControlType,
        ObjectType,
        IsInherited `
        -AutoSize
```

---

# PowerView

PowerView can help identify writable Active Directory objects.

Example:

```powershell
Get-DomainObjectAcl `
    -Identity 'bob' `
    -ResolveGUIDs
```

Review for rights such as:

```text
GenericAll
GenericWrite
WriteProperty
WriteDacl
WriteOwner
```

Exact command behaviour depends on the PowerView version.

---

# Find Interesting ACLs

PowerView commonly provides:

```powershell
Find-InterestingDomainAcl `
    -ResolveGUIDs
```

Use this as an attack-path discovery mechanism rather than treating every result as exploitable.

---

# BloodHound

BloodHound is particularly useful for discovering Shadow Credentials attack paths.

Depending on the BloodHound version and collected data, an attack relationship may be represented as:

```text
AddKeyCredentialLink
```

Conceptually:

```text
Alice
 |
 v
AddKeyCredentialLink
 |
 v
Bob
```

This means Alice may be able to add key-based authentication material to Bob's account.

---

# BloodHound Path

Example:

```text
Owned User
    |
    v
MemberOf
    |
    v
Helpdesk
    |
    v
AddKeyCredentialLink
    |
    v
Server Admin
    |
    v
AdminTo
    |
    v
SERVER01
```

The important question is:

```text
What privilege does the target identity provide?
```

---

# BloodHound Validation

Use:

```text
BloodHound Edge
      |
      v
Identify Underlying ACE
      |
      v
Confirm Effective Permission
      |
      v
Check PKINIT Prerequisites
      |
      v
Determine Target Privilege
```

Do not assume graph presence guarantees successful exploitation.

---

# SharpHound

SharpHound can collect ACL and object information used to build these relationships.

See:

[BloodHound](bloodhound.md)

---

# Certipy

Certipy includes functionality useful for Shadow Credentials assessment in Active Directory certificate environments.

Before using:

```bash
certipy -h
```

and inspect the installed version's documentation.

Current syntax can change between major releases.

---

# Certipy Shadow Functionality

Modern Certipy versions provide a:

```text
shadow
```

command family for working with Key Credentials.

Check:

```bash
certipy shadow -h
```

before use.

Operations may include functionality for:

```text
Listing Key Credentials
Adding Key Credentials
Removing Key Credentials
Automatic Shadow Credential Workflows
```

depending on version.

---

# pyWhisker

`pyWhisker` is another tool specifically designed around Shadow Credentials and the `msDS-KeyCredentialLink` attribute.

It can support operations such as:

```text
List
Add
Remove
Clear
Export
Import
```

depending on the installed version.

Check:

```bash
python3 pywhisker.py -h
```

before use.

---

# Whisker

The original Windows-oriented tooling associated with this technique includes:

```text
Whisker
```

which can interact with KeyCredentialLink values.

Tool choice depends on:

```text
Windows vs Linux
Authentication Material
Assessment Workflow
Environment
```

---

# Read-Only Tool Use

During initial enumeration, prefer operations equivalent to:

```text
List
```

rather than:

```text
Add
Remove
Clear
```

This prevents unnecessary modification of authentication data.

---

# Never Use Clear Casually

A command that:

```text
Clears msDS-KeyCredentialLink
```

can remove legitimate key credentials.

This may disrupt:

```text
Windows Hello for Business
Key-Based Authentication
Other Authentication Workflows
```

Therefore:

```text
Clear
```

should not be used during routine penetration testing.

---

# Preserve Original State

Before active validation:

```text
Read Existing Values
      |
      v
Record Exact Original State
      |
      v
Add Test Credential
      |
      v
Validate
      |
      v
Remove Only Test Credential
      |
      v
Verify Original State
```

Do not replace the complete attribute if an additive operation is available.

---

# Dangerous Cleanup Pattern

Avoid:

```text
Attack
   |
   v
Clear Attribute
```

because legitimate credentials may have existed before testing.

The correct cleanup model is:

```text
Identify Added DeviceID
       |
       v
Remove That Entry Only
       |
       v
Preserve Existing Entries
```

---

# Active Validation

If active exploitation is explicitly authorised, the workflow conceptually becomes:

```text
Target
   |
   v
Add KeyCredential
   |
   v
Generate Certificate + Private Key
   |
   v
PKINIT
   |
   v
TGT
   |
   v
Authenticate as Target
```

The exact tooling may automate several of these steps.

---

# Certificate and Private Key

The attacker-controlled credential generally involves:

```text
Private Key
+
Certificate / Public Key Material
```

The public-key information is associated with the target account through:

```text
msDS-KeyCredentialLink
```

while the attacker retains the corresponding private key.

---

# Authentication Flow

```text
Attacker Private Key
        |
        v
Certificate
        |
        v
PKINIT AS-REQ
        |
        v
Domain Controller
        |
        v
TGT for Victim
```

The password is not required.

---

# TGT

Successful PKINIT can result in:

```text
Ticket Granting Ticket
```

for the target identity.

The attacker can then operate using normal Kerberos authentication according to the victim's privileges.

See:

[Kerberos Tickets](kerberos-tickets.md)

---

# Pass-the-Ticket

Once a TGT exists:

```text
Shadow Credential
      |
      v
PKINIT
      |
      v
TGT
      |
      v
Pass-the-Ticket
```

may become part of the workflow.

See:

[Pass-the-Ticket](pass-the-ticket.md)

---

# Credential Extraction Implications

Some tooling can use PKINIT-derived Kerberos material to obtain information that can ultimately result in the target account's NT hash under suitable Active Directory conditions.

Conceptually:

```text
Shadow Credential
      |
      v
PKINIT
      |
      v
Kerberos Session
      |
      v
Additional Kerberos Operations
      |
      v
Credential Material
```

This significantly increases the potential impact.

However, do not assume:

```text
Shadow Credential
      =
Guaranteed NT Hash Recovery
```

in every environment.

Tooling, protocol support, account type, encryption configuration, and domain behaviour matter.

---

# UnPAC-the-Hash

The technique commonly associated with obtaining an NT hash after PKINIT authentication is often referred to as:

```text
UnPAC-the-Hash
```

Conceptually:

```text
PKINIT
   |
   v
TGT
   |
   v
PAC Credential Information
   |
   v
NT Hash
```

This is different from:

```text
DCSync
```

and should not be described as directory replication.

---

# Why NT Hash Recovery Matters

If successful:

```text
Shadow Credential
      |
      v
NT Hash
```

may enable additional authentication paths such as:

```text
NTLM
Pass-the-Hash
Kerberos Key-Based Authentication
```

depending on target services and policy.

See:

[Pass-the-Hash](pass-the-hash.md)

---

# Shadow Credentials vs Password Reset

## Password Reset

```text
Attacker
   |
   v
Reset Victim Password
   |
   v
Victim Password Changes
```

Potential consequences:

```text
User Disruption
Helpdesk Alert
Authentication Failure
Immediate Visibility
```

## Shadow Credentials

```text
Attacker
   |
   v
Add Key Credential
   |
   v
Victim Password Unchanged
```

The second technique can be less disruptive to the victim.

---

# Shadow Credentials vs Kerberoasting

Kerberoasting:

```text
SPN
 |
 v
Service Ticket
 |
 v
Offline Password Guessing
```

Shadow Credentials:

```text
Write KeyCredential
      |
      v
PKINIT
      |
      v
Authenticate as Target
```

Shadow Credentials does not depend on cracking the target's password.

See:

[Kerberoasting](kerberoasting.md)

---

# Shadow Credentials vs AS-REP Roasting

AS-REP Roasting depends on:

```text
Kerberos Preauthentication Disabled
```

Shadow Credentials depends on:

```text
Writable msDS-KeyCredentialLink
```

They are fundamentally different attack primitives.

See:

[AS-REP Roasting](asrep-roasting.md)

---

# Shadow Credentials vs RBCD

RBCD:

```text
Write
msDS-AllowedToActOnBehalfOfOtherIdentity
        |
        v
Delegation
        |
        v
S4U
```

Shadow Credentials:

```text
Write
msDS-KeyCredentialLink
        |
        v
PKINIT
        |
        v
Direct Authentication as Target
```

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# Shadow Credentials vs gMSA

gMSA abuse:

```text
Read
msDS-ManagedPassword
        |
        v
Service Account Credential
```

Shadow Credentials:

```text
Write
msDS-KeyCredentialLink
        |
        v
Additional Authentication Credential
```

See:

[Group Managed Service Accounts](gmsa.md)

---

# Shadow Credentials vs LAPS

LAPS:

```text
Read LAPS Password
      |
      v
Local Administrator
```

Shadow Credentials:

```text
Write KeyCredential
      |
      v
Domain Principal Authentication
```

See:

[Active Directory LAPS](laps.md)

---

# Shadow Credentials vs AD CS

Shadow Credentials uses certificate/public-key authentication, but the technique is not identical to an AD CS certificate-template vulnerability.

AD CS abuse may involve:

```text
Certificate Template
      |
      v
Certificate Authority
      |
      v
Certificate Issuance
      |
      v
Authentication
```

Shadow Credentials instead abuses:

```text
Existing AD Object
      |
      v
msDS-KeyCredentialLink
```

A Certificate Authority does not necessarily need to issue the attacker-controlled certificate used by the technique.

However, PKINIT support in the environment remains important.

---

# AD CS Relationship

Because certificate-based Kerberos authentication is involved, Shadow Credentials should be considered alongside Active Directory Certificate Services during broader attack-path analysis.

Questions include:

```text
Does PKINIT work?

Which DC certificates exist?

Is AD CS deployed?

Which certificate templates exist?

Are certificate-based attack paths also present?
```

A dedicated AD CS section should cover those topics separately.

---

# Machine Account Quota

Machine Account Quota is not a direct prerequisite for Shadow Credentials.

However, computer-account creation can interact with other Active Directory attack chains.

Do not conflate:

```text
Create Computer
```

with:

```text
Write KeyCredential
```

See:

[Active Directory Machine Account Quota](machine-account-quota.md)

---

# Protected Users

Membership in:

```text
Protected Users
```

provides several authentication protections, but it should not be treated as a universal defence against every directory-object control path.

If an attacker can directly alter authentication-related attributes on a protected account, analyse the exact protocol behaviour rather than assuming group membership blocks the attack.

---

# AdminSDHolder

Privileged accounts protected by:

```text
AdminSDHolder
```

may have special ACL behaviour.

This can influence:

```text
Who Can Modify the Account?
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Remember:

```text
adminCount=1
```

alone is not definitive evidence that an account is currently protected.

---

# Persistence

Shadow Credentials can potentially be used for persistence.

Conceptually:

```text
Compromise Privileged Account
        |
        v
Add Shadow Credential
        |
        v
Lose Original Access
        |
        v
Shadow Credential Remains
        |
        v
Reauthenticate
```

This makes unexpected KeyCredential values particularly important during incident response.

---

# Persistence Risk

The victim may:

```text
Change Password
```

while the attacker's key credential remains present.

Therefore:

```text
Password Reset
      |
      X
Guaranteed Shadow Credential Removal
```

Incident responders should inspect authentication-related directory attributes separately.

---

# Password Rotation

Changing:

```text
Victim Password
```

does not necessarily remove:

```text
msDS-KeyCredentialLink
```

entries.

This is a key incident-response consideration.

---

# Detection

Shadow Credentials detection should focus on:

```text
msDS-KeyCredentialLink Changes
      +
Kerberos PKINIT Activity
      +
Unexpected Authentication
      +
ACL Changes
```

---

# Event 5136

Active Directory object modifications can generate:

```text
5136
```

when Directory Service Changes auditing is enabled.

This event is particularly relevant because Shadow Credentials requires modification of:

```text
msDS-KeyCredentialLink
```

---

# Monitor Attribute Changes

A useful detection target is:

```text
Attribute:
msDS-KeyCredentialLink
```

Correlate:

```text
Who Modified It?
Which Object?
When?
From Which System?
Was the Change Expected?
```

---

# 5136 Detection Model

```text
Event 5136
    |
    v
msDS-KeyCredentialLink
    |
    v
User / Computer Object
    |
    v
Unexpected Modifier
    |
    v
Investigate
```

---

# Event 4662

With suitable object-access auditing and SACL configuration:

```text
4662
```

may provide additional visibility into operations against directory objects.

Actual visibility depends on:

```text
Audit Policy
SACL
Operation
Directory Configuration
```

---

# Kerberos Event 4768

A successful Kerberos TGT request can generate:

```text
4768
```

on a Domain Controller.

Shadow Credentials authentication may therefore produce Kerberos authentication telemetry.

However:

```text
4768
```

alone does not identify Shadow Credentials.

Correlation is required.

---

# PKINIT Detection

Potential detection opportunities include:

```text
Certificate-Based TGT Request
        |
        +
Recent KeyCredential Modification
        |
        +
Unexpected Account / Host
        |
        v
Higher Confidence
```

---

# Detection Correlation

A strong sequence is:

```text
5136
 |
 v
msDS-KeyCredentialLink Modified
 |
 v
4768
 |
 v
Certificate-Based Kerberos Authentication
 |
 v
Privileged Account Activity
```

This is much stronger than alerting on one event independently.

---

# Short-Lived Attribute Changes

Attack tooling may:

```text
Add KeyCredential
      |
      v
Authenticate
      |
      v
Remove KeyCredential
```

quickly.

Therefore defenders should retain directory-change telemetry.

A short-lived modification may otherwise disappear before manual inspection.

---

# Add and Remove Pattern

```text
10:01 Add KeyCredential
10:02 PKINIT
10:03 Remove KeyCredential
```

This sequence should be considered suspicious unless explained by legitimate identity-management activity.

---

# Baseline Legitimate Usage

Before alerting aggressively, understand whether the organisation uses:

```text
Windows Hello for Business
Key Trust
Certificate Trust
Cloud Kerberos Trust
Other KeyCredential-Based Features
```

Detection should distinguish legitimate provisioning from suspicious manual or tool-driven modifications.

---

# Suspicious Indicators

Examples include:

```text
KeyCredential Added to Domain Admin
KeyCredential Added by Helpdesk User
KeyCredential Added from Workstation
KeyCredential Added Then Removed Quickly
KeyCredential Added to Server Computer by Unrelated User
PKINIT Immediately After Attribute Change
Unexpected DeviceID
Unexpected KeyCredential Count Increase
```

---

# High-Value Targets

Prioritise monitoring for:

```text
Domain Admins
Enterprise Admins
Privileged Service Accounts
Backup Accounts
Administrative Users
Domain Controllers
Certificate Authorities
Management Servers
Tier 0 Computers
```

---

# ACL Change Detection

Because an attacker might first gain:

```text
WriteDACL
```

and then grant themselves KeyCredential write access, monitor:

```text
ACL Modification
      |
      v
KeyCredential Modification
```

Relevant directory events may include:

```text
5136
4662
```

depending on auditing configuration.

---

# BloodHound for Defensive Review

BloodHound can also help defenders identify:

```text
AddKeyCredentialLink
```

paths before attackers exploit them.

Prioritise:

```text
Low-Privilege Principal
      |
      v
AddKeyCredentialLink
      |
      v
High-Value Principal
```

---

# Hardening

The primary defence is:

```text
Prevent Unauthorised Write Access
```

to:

```text
msDS-KeyCredentialLink
```

---

# ACL Hardening

Review:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

against sensitive users and computers.

Remove unnecessary delegation.

---

# Least Privilege

Helpdesk groups should receive only the permissions necessary for their operational responsibilities.

Avoid granting broad:

```text
GenericWrite
```

or:

```text
GenericAll
```

over large OUs merely for convenience.

---

# Protect Privileged Accounts

Apply additional scrutiny to ACLs on:

```text
Privileged Users
Service Accounts
Domain Controllers
Management Servers
Certificate Infrastructure
```

---

# Review OU Delegation

Permissions may be inherited:

```text
OU
 |
 v
User / Computer
 |
 v
msDS-KeyCredentialLink
```

Therefore inspecting only the target object's explicit ACL is insufficient.

Review:

```text
Parent OU
Inheritance
Nested Delegation
Object-Specific ACEs
```

---

# Administrative Tiering

Avoid:

```text
Tier 2 Helpdesk
      |
      v
Write Privileged User Objects
```

or:

```text
Tier 1 Server Admin
      |
      v
Modify Tier 0 Computer Objects
```

Apply administrative boundaries consistently.

---

# Monitor KeyCredentialLink

Create monitoring around modifications to:

```text
msDS-KeyCredentialLink
```

especially for high-value accounts.

---

# Protect Domain Controllers

Because PKINIT and Kerberos authentication depend on domain infrastructure:

```text
Domain Controllers
```

must remain strongly protected.

Apply:

```text
Patching
Administrative Tiering
Restricted Logon
EDR
Certificate Lifecycle Management
Directory Auditing
```

---

# Protect AD CS

Where AD CS supports domain authentication infrastructure, secure:

```text
Certification Authorities
Templates
Enrollment Permissions
CA Administrators
Private Keys
Web Enrollment
RPC Enrollment
```

Shadow Credentials should be considered within the wider certificate-based authentication threat model.

---

# Safe Validation Strategy

Use the following hierarchy:

```text
Level 1
Identify ACL Path

Level 2
Confirm Write Permission

Level 3
Confirm PKINIT Prerequisites

Level 4
Use Dedicated Test Target

Level 5
Record Existing KeyCredentials

Level 6
Add One Test KeyCredential

Level 7
Request TGT

Level 8
Remove Test KeyCredential

Level 9
Verify Original State
```

Stop as soon as sufficient evidence exists.

---

# Preferred Validation

Where possible:

```text
ACL Proof
+
BloodHound Path
+
PKINIT Capability
```

may already be sufficient to demonstrate risk.

Active modification is not always necessary.

---

# Controlled Test Account

Prefer:

```text
TEST-SHADOW-USER
```

rather than:

```text
Domain Administrator
```

for validating the mechanics.

The test account can be assigned a harmless privilege or controlled resource to demonstrate resulting authentication.

---

# Pre-Test Evidence

Before modification, record:

```text
Target DN
Target SID
Original msDS-KeyCredentialLink Values
Current Time
Current Operator
Current ACL
Expected Cleanup
```

---

# Post-Test Evidence

After cleanup, confirm:

```text
Test DeviceID Removed
Original Values Preserved
No Unexpected KeyCredentials
No ACL Changes
No Certificate Files Left Behind
No Kerberos Tickets Retained
```

---

# Credential Files

Shadow Credentials tools may create files such as:

```text
PFX
PEM
CCACHE
KEY
CERT
```

Treat these as sensitive authentication material.

Store them only in approved assessment locations.

---

# Cleanup

Cleanup should include:

```text
Remove Added KeyCredential
Delete Private Key
Delete Certificate
Delete PFX
Delete Kerberos Cache
Verify Directory Attribute
Verify Original Values
```

---

# Kerberos Cache

On Linux, inspect:

```bash
echo "$KRB5CCNAME"
```

and:

```bash
klist
```

Remove temporary assessment credential caches when no longer required.

---

# Windows Kerberos Cache

Windows:

```powershell
klist
```

can display Kerberos tickets.

Purging tickets:

```powershell
klist purge
```

is disruptive to the current logon session and should not be performed casually on production systems.

---

# Incident Response

If Shadow Credentials is suspected:

```text
Identify Modified Account
       |
       v
Identify Modifier
       |
       v
Collect KeyCredential Values
       |
       v
Determine Legitimate vs Suspicious
       |
       v
Review 5136
       |
       v
Review Kerberos Authentication
       |
       v
Remove Malicious Credential
       |
       v
Investigate Initial ACL Compromise
```

---

# Do Not Immediately Clear Everything

During incident response:

```text
Clear msDS-KeyCredentialLink
```

may disrupt legitimate Windows Hello for Business authentication.

Instead:

```text
Identify Suspicious Entry
      |
      v
Preserve Evidence
      |
      v
Remove Malicious Entry
```

where possible.

---

# Determine Initial Access

Shadow Credentials usually requires a prior privilege:

```text
GenericWrite
GenericAll
WriteProperty
WriteDACL
WriteOwner
```

Therefore removing the malicious KeyCredential alone is insufficient.

Investigate:

```text
How Did the Attacker Obtain Write Access?
```

---

# Incident Response Chain

```text
Initial Compromise
      |
      v
Directory Write Permission
      |
      v
Shadow Credential
      |
      v
Target Authentication
      |
      v
Privilege Use
```

Contain every stage.

---

# Password Reset Is Not Enough

Because Shadow Credentials are separate from the normal password:

```text
Reset Password
      |
      X
Remove Shadow Credential
```

Incident response should explicitly inspect:

```text
msDS-KeyCredentialLink
```

---

# Review Target Sessions

If a privileged identity was shadowed, investigate activity performed using that identity.

Review:

```text
Kerberos Tickets
Remote Logons
LDAP Activity
SMB
WinRM
RDP
WMI
Service Creation
Scheduled Tasks
Directory Changes
AD CS Activity
```

---

# Reporting

Possible finding titles include:

```text
Low-Privilege User Can Add Shadow Credentials to Privileged Account
```

```text
Excessive Active Directory Permissions Allow KeyCredentialLink Modification
```

```text
GenericWrite Permission Enables Shadow Credentials Attack
```

```text
Computer Object Permissions Permit Shadow Credentials Authentication
```

```text
Active Directory ACL Allows Alternative Authentication as Privileged User
```

---

# Example Finding

```text
Finding:
Low-Privilege User Can Add Shadow Credentials to Privileged Account

Source Principal:
CORP\alice

Target:
CORP\server-admin

Permission:
Write access affecting msDS-KeyCredentialLink

Description:
The CORP\alice account has effective Active Directory permissions that
allow modification of authentication-related attributes on the
server-admin user object.

The identified access permits modification of the
msDS-KeyCredentialLink attribute, which can be used to associate
attacker-controlled public-key credential material with the target
identity.

Where Kerberos PKINIT is supported, this can enable authentication as
the target account without changing or knowing the target's password.

Impact:
Compromise of CORP\alice could provide an attacker with an alternative
authentication path as CORP\server-admin.

The resulting impact is determined by the privileges assigned to the
server-admin account and may include access to systems administered by
that identity.

Recommendation:
Remove the unnecessary write permission from CORP\alice.

Review inherited and explicit ACLs affecting the target account and its
parent OU.

Restrict modification of authentication-related attributes to approved
identity-management processes.

Monitor changes to msDS-KeyCredentialLink and correlate them with
Kerberos certificate-based authentication.
```

---

# Example Finding - Computer Account

```text
Finding:
Delegated Permissions Allow Shadow Credentials Against Server Computer

Source:
CORP\helpdesk

Target:
APP01$

Description:
Members of CORP\helpdesk have effective write access to the APP01$
computer object that permits modification of msDS-KeyCredentialLink.

This permission can allow an attacker controlling a Helpdesk account to
associate attacker-controlled key material with APP01$ and potentially
authenticate as the computer account through Kerberos PKINIT.

Impact:
Compromise of a Helpdesk identity could lead to compromise of the
APP01$ computer identity.

The resulting access depends on privileges and trust relationships
associated with APP01$, including any delegated Active Directory
permissions or service relationships.

Recommendation:
Remove unnecessary write permissions over the APP01$ computer object.

Delegate only the specific properties required for Helpdesk operations
and review inherited permissions from the parent OU.
```

---

# Example Finding - Persistence

```text
Finding:
Unexpected Key Credential Present on Privileged Active Directory User

Target:
CORP\admin-user

Description:
The admin-user object contains an msDS-KeyCredentialLink value that
could not be associated with an approved Windows Hello for Business or
other key-based authentication deployment.

Directory change logs indicate that the value was added by an
unexpected principal.

Impact:
The key credential may provide an alternative authentication mechanism
for the privileged account.

Changing the user's password alone may not invalidate this
authentication path.

Recommendation:
Preserve the suspicious KeyCredential value for investigation.

Determine whether the credential is legitimate before removing it.

Review directory-change and Kerberos authentication logs around the
creation time.

Investigate the principal responsible for the modification and review
the ACL path that allowed the change.
```

---

# Severity

Severity depends on:

```text
Source Principal
      +
Target Principal
      +
Write Permission
      +
PKINIT Availability
      +
Target Privilege
      +
Downstream Access
      =
Risk
```

Example:

```text
Low-Privilege User
       |
       v
AddKeyCredentialLink
       |
       v
Low-Privilege Test User
```

may have limited impact.

Compare:

```text
Low-Privilege User
       |
       v
AddKeyCredentialLink
       |
       v
Privileged Server Administrator
       |
       v
Administrative Infrastructure
```

which may represent a severe escalation path.

---

# Do Not Overstate Findings

Finding:

```text
GenericWrite -> User
```

does not automatically prove:

```text
Shadow Credentials Successfully Exploitable
```

Validate:

```text
Can msDS-KeyCredentialLink Actually Be Modified?

Does PKINIT Work?

What Is the Target's Privilege?

Are Other Constraints Present?
```

Report the strongest claim supported by evidence.

---

# Evidence Checklist

Record:

```text
Domain
Source Principal
Source SID
Target Principal
Target SID
Target Type
Target DN
Exact ACL
Explicit / Inherited
ObjectType GUID
msDS-KeyCredentialLink State
Existing DeviceIDs
PKINIT Availability
Domain Controller
Target Privileges
BloodHound Edge
Validation Level
Credential Added?
TGT Requested?
Credential Removed?
Relevant Events
Cleanup Verification
```

Do not include:

```text
Private Key
PFX Password
Reusable Kerberos Ticket
NT Hash
```

in normal report evidence.

---

# Shadow Credentials Assessment Checklist

## Preparation

- [ ] Confirm directory modification is authorised
- [ ] Confirm certificate-based authentication testing is authorised
- [ ] Confirm credential extraction restrictions
- [ ] Confirm Tier 0 restrictions
- [ ] Define cleanup procedure
- [ ] Prepare secure credential storage

## Discovery

- [ ] Enumerate users
- [ ] Enumerate computers
- [ ] Identify existing KeyCredentialLink values
- [ ] Identify Windows Hello for Business usage
- [ ] Identify PKINIT support
- [ ] Identify AD CS deployment where relevant
- [ ] Identify privileged targets

## ACL Analysis

- [ ] Review GenericAll
- [ ] Review GenericWrite
- [ ] Review WriteProperty
- [ ] Review WriteDACL
- [ ] Review WriteOwner
- [ ] Review object-specific ACEs
- [ ] Review inherited permissions
- [ ] Review OU delegation
- [ ] Resolve nested groups
- [ ] Identify AddKeyCredentialLink paths

## BloodHound

- [ ] Collect ACL information
- [ ] Identify `AddKeyCredentialLink`
- [ ] Identify paths from owned principals
- [ ] Identify paths to high-value users
- [ ] Identify paths to high-value computers
- [ ] Validate graph edges against ACLs
- [ ] Analyse downstream target privilege

## PKINIT

- [ ] Identify suitable Domain Controller
- [ ] Confirm certificate-based Kerberos support
- [ ] Confirm DNS resolution
- [ ] Confirm time synchronisation
- [ ] Confirm KDC reachability
- [ ] Avoid assuming AD CS automatically means PKINIT works

## Validation

- [ ] Prefer read-only evidence first
- [ ] Prefer dedicated test target
- [ ] Record original KeyCredential values
- [ ] Add only one test credential
- [ ] Record test DeviceID
- [ ] Request only required authentication material
- [ ] Avoid unnecessary remote execution
- [ ] Remove only the test credential
- [ ] Verify original state

## Credential Handling

- [ ] Protect PFX files
- [ ] Protect PEM files
- [ ] Protect private keys
- [ ] Protect Kerberos caches
- [ ] Protect recovered hashes
- [ ] Do not commit credentials to Git
- [ ] Do not place reusable credentials in reports
- [ ] Delete temporary credentials after validation

## Detection

- [ ] Monitor event 5136
- [ ] Monitor event 4662 where configured
- [ ] Monitor `msDS-KeyCredentialLink`
- [ ] Monitor privileged user objects
- [ ] Monitor privileged computer objects
- [ ] Monitor rapid add/remove sequences
- [ ] Monitor event 4768
- [ ] Correlate PKINIT with directory changes
- [ ] Baseline legitimate Windows Hello provisioning
- [ ] Investigate unexpected DeviceIDs

## Hardening

- [ ] Remove unnecessary GenericAll
- [ ] Remove unnecessary GenericWrite
- [ ] Restrict WriteProperty
- [ ] Restrict WriteDACL
- [ ] Restrict WriteOwner
- [ ] Review OU inheritance
- [ ] Apply administrative tiering
- [ ] Protect privileged accounts
- [ ] Protect Domain Controllers
- [ ] Protect AD CS
- [ ] Monitor KeyCredential modifications

## Incident Response

- [ ] Identify affected account
- [ ] Preserve suspicious KeyCredential
- [ ] Identify modification time
- [ ] Identify modifying principal
- [ ] Review event 5136
- [ ] Review Kerberos authentication
- [ ] Identify suspicious PKINIT
- [ ] Review downstream activity
- [ ] Remove malicious KeyCredential
- [ ] Review original ACL weakness
- [ ] Contain source principal
- [ ] Do not rely only on password reset

## Cleanup

- [ ] Remove test KeyCredential
- [ ] Preserve legitimate KeyCredentials
- [ ] Delete temporary certificate
- [ ] Delete temporary private key
- [ ] Delete PFX
- [ ] Delete Kerberos cache
- [ ] Remove temporary tickets
- [ ] Verify original attribute state
- [ ] Verify ACL unchanged
- [ ] Record cleanup evidence

---

# Shadow Credentials Testing Model

The normal authentication model is:

```text
User
 |
 +--> Password
 |
 +--> Kerberos Keys
 |
 +--> Approved Key Credentials
```

The Shadow Credentials model is:

```text
User
 |
 +--> Legitimate Credentials
 |
 +--> Attacker-Controlled KeyCredential
```

The ACL model is:

```text
Attacker
   |
   v
GenericWrite / WriteProperty
   |
   v
msDS-KeyCredentialLink
   |
   v
Victim
```

The authentication model is:

```text
Private Key
    |
    v
PKINIT
    |
    v
Kerberos
    |
    v
TGT
```

The complete attack model is:

```text
Compromised Principal
        |
        v
Directory Write Permission
        |
        v
Add KeyCredential
        |
        v
PKINIT
        |
        v
TGT as Victim
        |
        v
Victim Privileges
```

The computer-account model is:

```text
Attacker
   |
   v
AddKeyCredentialLink
   |
   v
SERVER01$
   |
   v
Authenticate as SERVER01$
   |
   v
Computer Account Rights
```

The persistence model is:

```text
Initial Compromise
      |
      v
Add Shadow Credential
      |
      v
Password Changes
      |
      X
Shadow Credential Removed
      |
      v
Alternative Access Remains
```

The detection model is:

```text
5136
 |
 v
msDS-KeyCredentialLink Change
 |
 v
4768
 |
 v
PKINIT Authentication
 |
 v
Target Account Activity
```

The cleanup model is:

```text
Record Original Values
      |
      v
Add Test DeviceID
      |
      v
Validate
      |
      v
Remove Test DeviceID Only
      |
      v
Verify Original Values
```

The unsafe cleanup model is:

```text
Clear Attribute
      |
      v
Legitimate Credentials Removed
      |
      v
Authentication Disruption
```

The defensive model is:

```text
Least Privilege
      |
      v
Restrict Object Write Access
      |
      v
Monitor KeyCredentialLink
      |
      v
Monitor PKINIT
      |
      v
Protect Privileged Objects
```

The most important distinction is:

```text
Password Unknown
      |
      X
Account Cannot Be Authenticated As
```

If an attacker can create an alternative authentication credential:

```text
Password
   |
   X
Not Required
```

Another important distinction is:

```text
msDS-KeyCredentialLink Present
        |
        X
Malicious
```

because legitimate technologies such as Windows Hello for Business may use the attribute.

The correct detection model is:

```text
Attribute
   +
Modifier
   +
Time
   +
DeviceID
   +
Authentication
   +
Business Context
   =
Assessment
```

For penetration testers:

```text
Do Not Ask:
"Can I add a Shadow Credential?"

Ask:
"Which compromised principals can modify authentication
material for which identities, and what privilege would
those identities provide?"
```

For defenders:

```text
Do Not Ask:
"Does msDS-KeyCredentialLink exist?"

Ask:
"Who can modify it, who actually modified it,
and was the resulting authentication expected?"
```

The final attack-path model is:

```text
Source Principal
      |
      v
AddKeyCredentialLink
      |
      v
Target Principal
      |
      v
PKINIT
      |
      v
Target Identity
      |
      v
Resulting Privilege
```

That relationship determines the actual security impact of a Shadow Credentials path.

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

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[Kerberos S4U](s4u.md)

LAPS:

[Active Directory LAPS](laps.md)

gMSA:

[Group Managed Service Accounts](gmsa.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

The next Credential Access page is:

```text
active-directory/ntds.md
```

The later AD CS section should cover certificate-specific attack paths separately.

---

# References

## Microsoft - msDS-KeyCredentialLink

[Microsoft - msDS-KeyCredentialLink](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-keycredentiallink){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Protocol Documentation

[Microsoft - MS-ADTS Active Directory Technical Specification](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - KeyCredentialLink Structures](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/de61eb56-b75f-4743-b8af-e9be154b47af){ target="_blank" rel="noopener noreferrer" }

---

## Kerberos PKINIT

[IETF RFC 4556 - Public Key Cryptography for Initial Authentication in Kerberos](https://datatracker.ietf.org/doc/html/rfc4556){ target="_blank" rel="noopener noreferrer" }

---

## Windows Hello for Business

[Microsoft - Windows Hello for Business](https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

---

## pyWhisker

[pyWhisker](https://github.com/ShutdownRepo/pywhisker){ target="_blank" rel="noopener noreferrer" }

---

## Whisker

[Whisker](https://github.com/eladshamir/Whisker){ target="_blank" rel="noopener noreferrer" }

---

## PowerView

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Additional Cloud Credentials](https://attack.mitre.org/techniques/T1098/001/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Shadow Credentials demonstrates an important Active Directory security principle:

```text
Authentication Security
        |
        X
Only Password Security
```

An account may have:

```text
Strong Password
MFA Elsewhere
Password Rotation
```

and still be compromised if an attacker can modify authentication-related directory attributes.

The core relationship is:

```text
Principal
   |
   v
Write msDS-KeyCredentialLink
   |
   v
Target
```

That write permission can potentially become:

```text
Directory Permission
      |
      v
Authentication Credential
      |
      v
Kerberos TGT
      |
      v
Target Identity
```

This is why Active Directory ACL analysis is critical.

A seemingly simple:

```text
GenericWrite
```

relationship can represent much more than the ability to change harmless metadata.

For privileged identities:

```text
GenericWrite
      |
      v
Authentication Attribute
      |
      v
Privilege Escalation
```

may represent a severe attack path.

The technique also highlights why password resets are not a complete incident-response strategy.

```text
Password Reset
      |
      v
Password Credential Changed
```

does not necessarily affect:

```text
KeyCredentialLink
```

Therefore incident response must review alternative authentication mechanisms.

For penetration testers, the preferred workflow is:

```text
Enumerate ACL
      |
      v
Identify AddKeyCredentialLink
      |
      v
Determine Target Privilege
      |
      v
Validate PKINIT
      |
      v
Use Controlled Test Object
      |
      v
Modify Only If Necessary
      |
      v
Restore Exact Original State
```

For defenders:

```text
Restrict ACLs
      |
      v
Monitor msDS-KeyCredentialLink
      |
      v
Correlate Directory Changes
      |
      v
Monitor PKINIT
      |
      v
Investigate Unexpected Authentication
```

The central question is:

```text
Who can add authentication material
to which Active Directory identity?
```

The second question is:

```text
What can that identity access?
```

Together:

```text
Write Permission
      +
Target Privilege
      =
Attack Path
```

Shadow Credentials should therefore be analysed as part of the broader Active Directory relationship:

```text
ACL Control
   |
   v
Identity Control
   |
   v
Authentication
   |
   v
Privilege
```

rather than as an isolated certificate technique.
