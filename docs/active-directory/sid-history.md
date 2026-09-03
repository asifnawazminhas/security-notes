# Active Directory SID History

SID History is an Active Directory migration feature that allows an account to retain security identifiers from a previous account or domain.

The attribute is:

```text
sIDHistory
```

Its legitimate purpose is to preserve access during migrations.

Conceptually:

```text
Old Domain
   |
   v
Old Account SID
   |
   v
Migration
   |
   v
New Domain Account
   |
   +--> New SID
   |
   +--> Old SID stored in sIDHistory
```

This allows resources that still contain access control entries for the old SID to continue recognising the migrated identity.

From a security perspective, SID History is important because Windows authorisation decisions can consider SIDs carried in an access token.

A high-value SID appearing in `sIDHistory` can therefore create privileges that are not obvious from normal group membership alone.

!!! warning "Authorised testing only"
    SID History analysis can reveal relationships with migrated, legacy or trusted domains. Do not modify `sIDHistory`, trust settings or SID filtering during an assessment unless the rules of engagement explicitly permit it. Read-only enumeration is normally sufficient to identify risky configurations.

---

# SID History at a Glance

Normal account:

```text
User
 |
 v
Current SID
 |
 v
Group Membership
 |
 v
Access Token
 |
 v
Resource ACL
```

Migrated account:

```text
User
 |
 +--> Current SID
 |
 +--> sIDHistory
          |
          v
       Old SID
 |
 v
Access Token
 |
 v
Resource ACL
```

The resource may still contain:

```text
Allow OLD-DOMAIN\User
```

and the migrated user can continue accessing it because the old SID is represented through SID History.

---

# Security Identifier

A Security Identifier, or SID, uniquely identifies a Windows security principal.

Examples include:

```text
User
Group
Computer
Domain
Local Account
Service
```

A typical domain account SID resembles:

```text
S-1-5-21-1111111111-2222222222-3333333333-1105
```

The structure can be viewed as:

```text
S-1-5-21-1111111111-2222222222-3333333333-1105
|-----------------------------------------|  |
               Domain SID                   RID
```

---

# Domain SID

Accounts belonging to the same domain share the domain portion of the SID.

Example:

```text
Domain SID:

S-1-5-21-1111111111-2222222222-3333333333
```

User:

```text
S-1-5-21-1111111111-2222222222-3333333333-1105
```

Group:

```text
S-1-5-21-1111111111-2222222222-3333333333-2101
```

The final component is the:

```text
Relative Identifier
```

or:

```text
RID
```

---

# Why SIDs Matter

Windows authorisation is fundamentally based on security identifiers rather than account names.

An ACL may visually display:

```text
CORP\alice
```

but the security descriptor ultimately references Alice's SID.

This matters during migrations because:

```text
Account Name
```

can remain similar while:

```text
SID
```

changes.

---

# Migration Problem

Suppose an old domain contains:

```text
LEGACY\alice
```

with SID:

```text
S-1-5-21-100-200-300-1105
```

A file server ACL contains:

```text
Allow S-1-5-21-100-200-300-1105 Read
```

Alice is migrated to:

```text
CORP\alice
```

with a new SID:

```text
S-1-5-21-400-500-600-2107
```

Without migration handling:

```text
New SID
   |
   X
   |
Old ACL
```

Alice may lose access.

---

# SID History Solution

The migrated account can contain:

```text
Current SID:
S-1-5-21-400-500-600-2107

sIDHistory:
S-1-5-21-100-200-300-1105
```

The effective model becomes:

```text
CORP\alice
   |
   +--> Current SID
   |
   +--> Legacy SID
           |
           v
       Old Resource ACL
```

This allows access to continue while ACLs are migrated.

---

# SID History Lifecycle

SID History should normally be considered transitional.

A healthy migration lifecycle is:

```text
Migration Begins
      |
      v
SID History Added
      |
      v
Legacy Access Continues
      |
      v
Resource ACLs Migrated
      |
      v
Dependencies Validated
      |
      v
SID History Reviewed
      |
      v
Legacy Values Removed When No Longer Required
```

A common problem is:

```text
Migration Completed
      |
      v
SID History Never Reviewed
      |
      v
Legacy Access Persists
```

---

# Why SID History Is Security Sensitive

The security significance comes from the relationship:

```text
SID
 |
 v
Access Token
 |
 v
ACL
 |
 v
Privilege
```

If an account possesses a SID associated with a privileged identity, authorisation may treat that SID as relevant when evaluating access.

Therefore:

```text
Current Group Membership
```

does not always reveal the complete privilege picture.

---

# Privilege Visibility Problem

Consider:

```text
CORP\migration-user
```

Normal group enumeration may show:

```text
Domain Users
Migration Users
```

Nothing appears privileged.

But:

```text
sIDHistory
```

could contain a SID that maps to a privileged legacy principal.

The actual security path becomes:

```text
Migration User
      |
      v
sIDHistory
      |
      v
Privileged SID
      |
      v
Resource ACL
      |
      v
Unexpected Access
```

---

# SID History Is Not Automatically a Vulnerability

The existence of:

```text
sIDHistory
```

is not inherently a vulnerability.

It is legitimate Active Directory functionality.

A meaningful finding requires additional context such as:

```text
Unexpected Privileged SID
Stale Migration Data
Unnecessary Legacy Access
Weak Trust Configuration
Missing Migration Cleanup
Unexpected Cross-Domain Privilege
```

---

# Assessment Questions

During an authorised assessment, ask:

```text
Which Accounts Have SID History?

Which Groups Have SID History?

Which Domains Do Those SIDs Belong To?

Are Those Domains Still Active?

Was SID History Created for Migration?

Are the Legacy Permissions Still Required?

Do Any Historical SIDs Represent Privileged Identities?

Does SID Filtering Protect the Trust Boundary?

Has the Migration Been Completed?
```

---

# Enumerating SID History

The safest starting point is read-only directory enumeration.

Using the ActiveDirectory PowerShell module:

```powershell
Get-ADUser -Filter * -Properties SIDHistory |
    Where-Object { $_.SIDHistory } |
    Select-Object SamAccountName,SID,SIDHistory
```

---

# Scoped User Enumeration

In large environments, avoid retrieving every user unnecessarily.

Example:

```powershell
Get-ADUser -LDAPFilter '(sIDHistory=*)' -Properties SIDHistory |
    Select-Object SamAccountName,SID,SIDHistory
```

This directly requests users containing SID History.

---

# Enumerate Groups

Groups can also contain SID History.

```powershell
Get-ADGroup -LDAPFilter '(sIDHistory=*)' -Properties SIDHistory |
    Select-Object Name,SID,SIDHistory
```

Do not limit the assessment to user objects.

---

# Enumerate All Relevant Objects

LDAP can be used when broader object coverage is required.

Example:

```powershell
Get-ADObject -LDAPFilter '(sIDHistory=*)' -Properties sIDHistory,objectSid |
    Select-Object Name,ObjectClass,ObjectSid,sIDHistory
```

---

# Query a Specific User

```powershell
Get-ADUser -Identity 'migration-user' -Properties SIDHistory |
    Select-Object SamAccountName,SID,SIDHistory
```

---

# Query a Specific Group

```powershell
Get-ADGroup -Identity 'Legacy-App-Users' -Properties SIDHistory |
    Select-Object Name,SID,SIDHistory
```

---

# LDAP Enumeration from Linux

SID History can also be queried through LDAP.

Example:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'DC=corp,DC=example' \
  '(sIDHistory=*)' \
  sAMAccountName objectSid sIDHistory
```

Binary SID values may require additional conversion before they are human-readable.

---

# LDAP Filter

The important LDAP filter is:

```text
(sIDHistory=*)
```

This can significantly reduce unnecessary directory retrieval.

---

# Raw LDAP Representation

LDAP tooling may return SID values in binary or escaped form.

Therefore:

```text
LDAP Result
    |
    v
Binary SID
    |
    v
Convert SID
    |
    v
Readable S-1-5-21-...
```

Do not mistake binary output for malformed data.

---

# PowerShell SID Conversion

A binary SID can be converted using .NET.

Example:

```powershell
$sid = New-Object System.Security.Principal.SecurityIdentifier($bytes,0)
$sid.Value
```

where `$bytes` contains the binary SID value.

---

# Current User SID

To inspect the current identity:

```cmd
whoami /user
```

---

# Current Group SIDs

```cmd
whoami /groups
```

This is useful when understanding the SIDs present in the current security context.

---

# Complete Token Context

```cmd
whoami /all
```

This can display:

```text
User SID
Group SIDs
Privileges
Integrity Information
```

---

# Domain SID Enumeration

Using PowerShell:

```powershell
Get-ADDomain | Select-Object DNSRoot,DomainSID
```

Example:

```text
DNSRoot   : corp.example
DomainSID : S-1-5-21-400-500-600
```

---

# Identify SID Origin

Suppose SID History contains:

```text
S-1-5-21-100-200-300-512
```

Separate:

```text
Domain SID:
S-1-5-21-100-200-300

RID:
512
```

This helps determine the possible origin and significance.

---

# Well-Known Domain RIDs

Some commonly encountered domain-relative RIDs include:

| RID | Typical Group |
|---:|---|
| 500 | Administrator account |
| 501 | Guest account |
| 512 | Domain Admins |
| 513 | Domain Users |
| 514 | Domain Guests |
| 515 | Domain Computers |
| 516 | Domain Controllers |
| 517 | Cert Publishers |
| 518 | Schema Admins |
| 519 | Enterprise Admins |
| 520 | Group Policy Creator Owners |
| 521 | Read-only Domain Controllers |

These values provide useful context when analysing historical SIDs.

!!! note
    A RID alone does not prove effective privilege. Confirm the SID's domain, object type, trust context and resulting authorisation before assigning impact.

---

# Example Privileged SID History

Suppose:

```text
Current Account:
CORP\migration-user

Current SID:
S-1-5-21-400-500-600-2107

SID History:
S-1-5-21-100-200-300-512
```

RID:

```text
512
```

commonly corresponds to:

```text
Domain Admins
```

in the domain represented by:

```text
S-1-5-21-100-200-300
```

This requires investigation.

---

# Do Not Infer Impact from RID Alone

The correct process is:

```text
Historical SID Found
      |
      v
Identify Domain SID
      |
      v
Identify Original Principal
      |
      v
Determine Trust Context
      |
      v
Determine Whether SID Is Accepted
      |
      v
Identify Resource / ACL
      |
      v
Validate Actual Access
```

---

# SID Resolution

Windows can resolve a SID when the corresponding authority is reachable and trusted.

PowerShell example:

```powershell
$sid = New-Object System.Security.Principal.SecurityIdentifier(
    'S-1-5-21-100-200-300-1105'
)

$sid.Translate([System.Security.Principal.NTAccount])
```

This may return something such as:

```text
LEGACY\alice
```

Resolution can fail when:

```text
Domain No Longer Exists
Trust Removed
Network Unreachable
SID Unknown
```

---

# Unresolved Historical SIDs

An unresolved SID should not automatically be dismissed.

It may represent:

```text
Retired Domain
Removed Account
Old Migration
Disconnected Forest
Deleted Group
Legacy Resource
```

Document the unresolved value and investigate using approved data sources.

---

# SID History and Groups

SID History on a group can be especially important.

Conceptually:

```text
New Group
   |
   v
Old Group SID in sIDHistory
   |
   v
Legacy ACL
   |
   v
Access for All New Group Members
```

A single historical group SID can therefore affect multiple users.

---

# Group Migration

Example:

```text
LEGACY\File-Admins
```

is migrated to:

```text
CORP\File-Admins
```

The new group may retain:

```text
LEGACY\File-Admins SID
```

in:

```text
sIDHistory
```

This preserves access to resources still secured using the legacy group.

---

# SID History and ACLs

SID History becomes meaningful when the SID intersects with an ACL.

Example:

```text
Historical SID
      |
      v
NTFS ACL
      |
      v
Sensitive Directory
```

or:

```text
Historical SID
      |
      v
Active Directory ACL
      |
      v
Privileged AD Object
```

---

# File System Permissions

A legacy file server may contain:

```text
Allow LEGACY\File-Admins Full Control
```

After migration:

```text
CORP\File-Admins
```

may continue receiving access through SID History.

The long-term fix is generally to migrate the ACL rather than retain historical dependencies indefinitely.

---

# Active Directory ACLs

Historical SIDs can also remain relevant to directory permissions.

Review:

```text
Users
Groups
OUs
GPOs
Computers
Service Accounts
Domain Objects
```

See:

[ACL and ACE](acl-ace.md)

---

# SID History and Group Policy

Legacy SIDs may appear in:

```text
GPO Security Filtering
Delegation
Restricted Groups
User Rights Assignments
File Permissions
Registry Permissions
```

See:

[Group Policy](group-policy.md)

---

# SID History and Local Groups

A historical domain group may still appear in:

```text
Local Administrators
Remote Desktop Users
Remote Management Users
Backup Operators
```

on member systems.

Example:

```text
Legacy Group SID
      |
      v
Server Local Administrators
      |
      v
Migrated Group via SID History
```

---

# SID History and SMB

Legacy file permissions are one of the most common reasons SID History exists.

Review:

```text
Share ACL
NTFS ACL
Historical Group SID
Current Migrated Group
```

See:

[SMB](smb.md)

---

# SID History and Trusts

SID History becomes especially important when it crosses domain or forest boundaries.

See:

[Domain and Forest Trusts](trusts.md)

and:

[Trust Relationships](trust-relationships.md)

---

# Trust Boundary

Consider:

```text
Domain A
   |
   v
Trust
   |
   v
Domain B
```

A user token may contain:

```text
Current SID
Group SIDs
Historical SIDs
```

The receiving domain must decide which SIDs should be accepted across the trust.

This is where:

```text
SID Filtering
```

becomes important.

---

# SID Filtering

SID filtering is designed to prevent inappropriate SID information from being honoured across certain trust boundaries.

Conceptually:

```text
Security Token
      |
      +--> Current SID
      +--> Group SID
      +--> SID History
      |
      v
Trust Boundary
      |
      v
SID Filtering
      |
      +--> Allowed
      |
      X
      |
      +--> Filtered
```

---

# SID Filtering Is Context Dependent

The exact filtering behaviour depends on factors including:

```text
Trust Type
Trust Attributes
Forest Relationship
SID Namespace
Migration Configuration
```

Do not reduce SID filtering to:

```text
Enabled
=
Everything Safe
```

or:

```text
Disabled
=
Automatically Exploitable
```

Analyse the actual trust and authorisation path.

---

# Intra-Forest Context

Domains inside the same forest have a much stronger trust relationship than separate forests.

The forest should generally be treated as the primary Active Directory security boundary.

Therefore:

```text
Child Domain
```

should not be assumed to provide strong isolation from:

```text
Forest Root Domain
```

simply because they have different domain SIDs.

---

# Cross-Forest Context

Separate forests provide a stronger security boundary.

For cross-forest relationships, carefully review:

```text
SID Filtering
Selective Authentication
Foreign Group Membership
Cross-Forest ACLs
Administrative Dependencies
Network Reachability
```

---

# External Trust Context

External trusts connect specific domains rather than entire forests.

SID filtering is particularly relevant because the receiving domain should not blindly accept arbitrary SID information from another security boundary.

---

# Forest Trust Context

Forest trusts provide broader authentication relationships.

The security assessment should evaluate:

```text
Forest Trust Direction
Forest Transitivity
Selective Authentication
SID Filtering
Foreign Privilege
```

---

# Selective Authentication

Selective authentication and SID filtering solve different problems.

SID filtering asks:

```text
Which SIDs should be accepted?
```

Selective authentication asks:

```text
Where may this foreign identity authenticate?
```

---

# Combined Model

```text
Foreign Identity
      |
      v
Trust
      |
      v
SID Filtering
      |
      v
Selective Authentication
      |
      v
Resource Authorisation
```

Both controls can contribute to reducing cross-boundary risk.

---

# SID History and Migration Trusts

Migration environments may intentionally configure trusts to support:

```text
Account Migration
Resource Migration
SID History
Temporary Legacy Access
```

These environments require careful interpretation.

A configuration that appears unusual may be:

```text
Temporary Migration Requirement
```

rather than:

```text
Security Misconfiguration
```

---

# Migration Exceptions

Temporary migration exceptions should have:

```text
Documented Purpose
Business Owner
Technical Owner
Start Date
Expected End Date
Cleanup Plan
```

---

# Migration Completion

Once migration is complete:

```text
Old ACLs
```

should ideally be replaced with:

```text
Current SIDs
```

and unnecessary historical dependencies removed.

---

# SID History and BloodHound

BloodHound can help reveal privilege relationships involving historical identities and cross-domain paths.

See:

[BloodHound](bloodhound.md)

A useful analysis model is:

```text
Account
   |
   v
Historical Identity
   |
   v
Group / ACL
   |
   v
Privilege
```

Do not rely on a graph alone.

Confirm the underlying directory attributes and effective access.

---

# SID History and Lateral Movement

SID History can contribute to lateral movement when it provides access to:

```text
Local Administrators
Remote Management Users
File Shares
Applications
Administrative Services
```

See:

[Lateral Movement](lateral-movement.md)

---

# SID History and WinRM

Example:

```text
Migrated Account
      |
      v
Historical Group SID
      |
      v
Remote Management Permission
      |
      v
WinRM Access
```

See:

[WinRM](winrm.md)

---

# SID History and RDP

A historical SID may also map to a principal that remains authorised for Remote Desktop access.

The assessment should distinguish:

```text
Authentication
```

from:

```text
Actual RDP Authorisation
```

---

# SID History and WMI

Administrative permissions derived through historical SIDs may indirectly enable remote WMI access.

See:

[WMI](wmi.md)

---

# SID History and DCOM

The same applies to DCOM where the resulting identity has the required permissions.

See:

[DCOM](dcom.md)

---

# SID History and Privileged Accounts

Pay particular attention when historical SIDs correspond to:

```text
Domain Admins
Enterprise Admins
Schema Admins
Administrators
Server Administrators
Backup Administrators
Application Administrators
```

The question is not simply:

```text
Does the SID look privileged?
```

but:

```text
Does the SID create effective privilege?
```

---

# High-Value RID Review

Historical SIDs ending in values such as:

```text
-500
-512
-518
-519
```

deserve additional investigation.

However:

```text
Interesting RID
!=
Confirmed Vulnerability
```

---

# Current Group Membership

For a specific user:

```powershell
Get-ADPrincipalGroupMembership -Identity 'migration-user' |
    Select-Object Name,GroupScope,GroupCategory
```

Compare this with:

```text
SIDHistory
```

to identify privilege that may not be apparent from current group membership.

---

# Current User Token

On a controlled test system:

```cmd
whoami /groups
```

can help confirm the SIDs represented in the user's current token.

---

# Token Validation

A safe validation sequence is:

```text
Directory Attribute
      |
      v
Historical SID Identified
      |
      v
Relevant Resource Identified
      |
      v
Controlled Logon
      |
      v
Token Inspected
      |
      v
Minimum Access Tested
```

---

# Do Not Modify SID History for Testing

Avoid changing:

```text
sIDHistory
```

merely to prove that Windows uses SIDs for authorisation.

This introduces unnecessary directory changes and can create privilege.

Read-only evidence is usually sufficient.

---

# Do Not Disable SID Filtering

Similarly, do not modify:

```text
SID Filtering
```

during normal penetration testing.

Changing trust security controls can affect authentication across entire domains or forests.

---

# Avoid Destructive Migration Tests

Do not:

```text
Delete SID History
Modify Trust Attributes
Change Resource ACLs
Remove Migration Groups
```

during assessment unless explicitly approved.

These changes may break production access.

---

# Safe Validation Example

Suppose:

```text
CORP\migration-user
```

contains an old SID associated with:

```text
LEGACY\File-Readers
```

and an approved test share still grants:

```text
Read
```

to that old SID.

A safe test can be:

```text
Authenticate as CORP\migration-user
      |
      v
Access Approved Share
      |
      v
Read Approved Test File
      |
      v
Stop
```

There is no need to:

```text
Modify Files
Execute Code
Change ACLs
```

to demonstrate the relationship.

---

# Safe Administrative Validation

If a historical SID appears privileged:

```text
Do Not Immediately Perform Administrative Actions
```

First establish:

```text
Original SID
Current Account
Trust Context
Target Permission
```

Then use the least intrusive approved action capable of demonstrating impact.

---

# Evidence Collection

For each relevant SID History entry, record:

```text
Current Account
Current SID
Historical SID
Historical Domain
Historical Principal
Object Type
Current Group Membership
Trust Relationship
SID Filtering Context
Affected Resource
Permission
Validation Performed
Timestamp
```

---

# Example Evidence Table

| Current Principal | Current SID | Historical Principal | Historical SID | Resource | Access |
|---|---|---|---|---|---|
| CORP\migration-user | S-1-5-21-400-500-600-2107 | LEGACY\App-Users | S-1-5-21-100-200-300-2201 | APP01 | Read |

Use:

```text
Redacted
```

or:

```text
Representative
```

values where appropriate in public reports.

---

# Evidence Quality

Strong evidence should establish:

```text
SID History Exists
      |
      v
Historical SID Identified
      |
      v
Permission Identified
      |
      v
Effective Access Confirmed
```

Weak evidence is merely:

```text
Account Has SID History
```

---

# SID History Detection

Defenders should monitor:

```text
SID History Changes
Unexpected Migration Activity
Privileged Historical SIDs
Cross-Domain Authentication
Foreign Privileged Access
Trust Changes
```

---

# Directory Service Auditing

Changes to Active Directory attributes can be visible through Directory Service Changes auditing.

Event:

```text
5136
```

can record modifications to directory objects when the relevant auditing and SACL configuration are present.

---

# Event 5136

Event 5136 indicates:

```text
A directory service object was modified
```

Relevant details can include:

```text
Object
Attribute
Actor
Operation
```

Monitoring should look for unexpected changes involving:

```text
sIDHistory
```

where sufficient audit detail is available.

---

# Account Migration Events

Windows provides security events associated with SID History migration activity.

Depending on the operation and auditing configuration, events such as:

```text
4765
4766
```

may be relevant.

---

# Event 4765

Security event:

```text
4765
```

is associated with:

```text
SID History being added to an account
```

This should normally correspond to authorised migration activity.

---

# Event 4766

Security event:

```text
4766
```

is associated with an attempt to add SID History that failed.

Unexpected occurrences may warrant investigation.

---

# Authentication Events

Correlate SID History observations with authentication telemetry such as:

```text
4624
4625
4672
4768
4769
```

where relevant.

---

# Privileged Logons

Event:

```text
4672
```

indicates that special privileges were assigned to a new logon.

If a migrated identity unexpectedly generates privileged logons, investigate:

```text
Current Groups
SID History
Local Groups
ACLs
Trust Relationships
```

---

# Trust Monitoring

Relevant trust events can include:

```text
4706
4707
4716
```

See:

[Trust Relationships](trust-relationships.md)

---

# Detection Model

```text
SID History Change
       |
       v
Account
       |
       v
Authentication
       |
       v
Privileged Resource
       |
       v
Unexpected Access
```

Correlation provides more value than monitoring a single event in isolation.

---

# Baseline SID History

Organisations using SID History legitimately should maintain an inventory of:

```text
Expected Accounts
Expected Groups
Source Domain
Migration Project
Migration Date
Business Owner
Cleanup Date
```

This makes unexpected values easier to detect.

---

# Detect Privileged Historical SIDs

Defenders can periodically enumerate SID History and identify values corresponding to privileged domain-relative RIDs.

Example read-only review:

```powershell
Get-ADObject -LDAPFilter '(sIDHistory=*)' -Properties sIDHistory |
    Select-Object Name,ObjectClass,sIDHistory
```

The resulting SIDs should then be correlated with known domains and migration records.

---

# Do Not Alert on Every SID History Entry

In migration-heavy environments:

```text
SID History Present
```

may be normal.

Better detection focuses on:

```text
New SID History
Unexpected Source Domain
Privileged SID
Account Outside Migration Scope
Post-Migration Changes
Unusual Administrative Access
```

---

# SID History Hardening

A strong defensive model includes:

```text
Controlled Migration
SID Filtering
Least Privilege
Migration Inventory
ACL Migration
SID History Cleanup
Trust Review
Monitoring
```

---

# Restrict Migration Privileges

Only authorised migration systems and administrators should be capable of performing operations related to SID History.

Protect:

```text
Migration Accounts
Migration Servers
Domain Controllers
Trust Configuration
```

---

# Use Dedicated Migration Accounts

Migration activities should use:

```text
Dedicated
Controlled
Audited
Time-Bounded
```

administrative identities.

Avoid using normal daily administrative accounts for migration operations.

---

# Protect Migration Infrastructure

Migration tooling can be highly privileged.

Treat migration servers as sensitive systems.

Apply:

```text
Network Restrictions
Privileged Access Controls
Logging
EDR
Credential Protection
Administrative Separation
```

---

# Maintain SID Filtering

Appropriate SID filtering should remain in place across trust boundaries.

Any migration-related exceptions should be:

```text
Documented
Approved
Temporary
Monitored
Removed
```

---

# Migrate Resource ACLs

The long-term objective should generally be:

```text
Legacy SID ACL
      |
      v
Current SID ACL
```

rather than indefinitely depending on:

```text
sIDHistory
```

---

# Remove Stale Dependencies

After migration:

```text
Find Legacy ACLs
      |
      v
Replace with Current Principals
      |
      v
Validate Applications
      |
      v
Review SID History
```

---

# Review Privileged SID History

Historical SIDs associated with privileged groups require particular attention.

Examples include SIDs corresponding to:

```text
Domain Admins
Enterprise Admins
Schema Admins
Administrators
```

These should have a clear documented migration justification.

---

# Review Legacy Domains

If SID History references a domain that:

```text
No Longer Exists
```

determine whether the historical SID still provides access through existing ACLs.

A retired domain does not automatically make the SID harmless.

---

# Review Trust Lifecycle

Migration trusts should not remain indefinitely without justification.

The lifecycle should be:

```text
Create Trust
    |
    v
Perform Migration
    |
    v
Migrate Permissions
    |
    v
Validate
    |
    v
Remove Legacy Dependency
    |
    v
Review / Remove Trust
```

---

# Reporting SID History Findings

Do not report:

```text
SID History Enabled
```

as a vulnerability.

`SIDHistory` is an attribute and migration capability, not a simple global feature that is either safely enabled or disabled.

Report the actual weakness.

Examples:

```text
Privileged Legacy SID Remains Assigned After Migration
```

```text
Stale SID History Preserves Unnecessary Access
```

```text
Migration Account Retains Historical Administrative Privileges
```

```text
Legacy ACLs Continue to Depend on SID History
```

```text
Unnecessary Cross-Domain Privilege Persists Through SID History
```

---

# Example Finding - Privileged SID History

```text
Finding:
Migrated Account Retains Privileged Legacy SID

Description:
A migrated account in the corporate domain retained a historical SID
associated with a privileged group in the legacy domain.

The migration project had already been completed and no documented
requirement for the historical administrative access was identified.

Impact:
The account may retain access to systems or resources that continue to
authorise the historical privileged SID.

This can provide privileges that are not apparent from the account's
current group membership.

Recommendation:
Identify all resources that still reference the historical SID and
replace those permissions with current role-based groups where access
remains required.

After validating that no legitimate dependencies remain, remove the
obsolete SID History value through the organisation's approved Active
Directory migration and change-management procedures.
```

---

# Example Finding - Stale Migration Access

```text
Finding:
SID History Preserves Legacy Resource Access After Migration

Description:
Multiple migrated accounts retained SID History values associated with
the previous domain.

Several production file-system ACLs continued to reference these
legacy SIDs even though the migration had been completed.

Impact:
Legacy access relationships remain active and increase the complexity
of permission management.

Access may persist even when current group membership suggests that an
account should no longer have access.

Recommendation:
Inventory resources that continue to reference legacy SIDs.

Replace legacy ACL entries with current domain groups, validate
application and user access, and remove unnecessary SID History values
after dependencies have been eliminated.
```

---

# Example Finding - Missing Migration Cleanup

```text
Finding:
Historical SIDs Remain Without Documented Migration Requirement

Description:
SID History was present on accounts migrated from a legacy domain.

The organisation could not identify an active migration project,
business requirement or remaining resource dependency requiring the
historical values.

Impact:
Unnecessary historical security identifiers can preserve access paths
that are difficult to identify through standard group-membership
reviews.

Recommendation:
Establish an inventory of accounts containing SID History and map each
historical SID to the resources that continue to depend on it.

Remove obsolete permissions and historical SID values through a
controlled migration-cleanup process.
```

---

# Example Finding - Privileged Group SID History

```text
Finding:
Migrated Group Retains Historical Administrative Group SID

Description:
A current domain group retained the SID of an administrative group
from the legacy domain in its SID History.

Members of the current group could therefore potentially inherit
permissions assigned to the historical administrative SID.

Impact:
Adding a user to the current group may grant access to legacy
administrative resources that is not obvious from the group's current
name or documented purpose.

Recommendation:
Identify every permission associated with the historical SID.

Replace required access with explicitly named current administrative
groups and remove the historical dependency after validation.
```

---

# SID History Assessment Checklist

## Domain Context

- [ ] Identify current domain
- [ ] Identify domain SID
- [ ] Identify forest
- [ ] Identify trusted domains
- [ ] Identify legacy domains
- [ ] Identify migration history
- [ ] Confirm all domains are in scope before querying them

## User Enumeration

- [ ] Search for users with `sIDHistory`
- [ ] Record current SID
- [ ] Record historical SID
- [ ] Identify historical domain
- [ ] Identify original principal where possible
- [ ] Review current group membership
- [ ] Identify privileged historical SIDs

## Group Enumeration

- [ ] Search groups with `sIDHistory`
- [ ] Record current group SID
- [ ] Record historical group SID
- [ ] Review group members
- [ ] Review nested groups
- [ ] Identify historical administrative groups

## SID Analysis

- [ ] Separate domain SID and RID
- [ ] Identify SID origin
- [ ] Resolve SID where authorised
- [ ] Investigate unresolved SIDs
- [ ] Review high-value RIDs
- [ ] Do not infer impact from RID alone

## Trusts

- [ ] Identify trust type
- [ ] Identify trust direction
- [ ] Identify transitivity
- [ ] Review SID filtering
- [ ] Review selective authentication
- [ ] Review migration exceptions
- [ ] Review legacy trusts

## Permissions

- [ ] Search NTFS ACLs
- [ ] Search share permissions
- [ ] Search AD ACLs
- [ ] Search GPO permissions
- [ ] Search local groups
- [ ] Search application permissions
- [ ] Identify actual historical-SID dependencies

## Privilege

- [ ] Review Domain Admin-related SIDs
- [ ] Review Enterprise Admin-related SIDs
- [ ] Review Schema Admin-related SIDs
- [ ] Review local administrator relationships
- [ ] Review remote-management permissions
- [ ] Review Tier 0 access
- [ ] Confirm effective privilege

## Safe Validation

- [ ] Use read-only enumeration first
- [ ] Do not add SID History
- [ ] Do not modify SID filtering
- [ ] Do not change trust attributes
- [ ] Do not remove SID History during testing
- [ ] Identify approved resource
- [ ] Validate minimum required access
- [ ] Stop after sufficient evidence

## Detection

- [ ] Monitor 5136 where applicable
- [ ] Monitor 4765
- [ ] Monitor 4766
- [ ] Correlate 4624
- [ ] Correlate 4625
- [ ] Correlate 4672
- [ ] Correlate 4768
- [ ] Correlate 4769
- [ ] Monitor trust changes
- [ ] Monitor privileged historical SIDs
- [ ] Baseline legitimate migration activity

## Hardening

- [ ] Maintain migration inventory
- [ ] Restrict migration privileges
- [ ] Protect migration infrastructure
- [ ] Maintain SID filtering
- [ ] Migrate legacy ACLs
- [ ] Remove stale resource dependencies
- [ ] Review privileged historical SIDs
- [ ] Review legacy domains
- [ ] Review migration trusts
- [ ] Remove obsolete SID History through controlled procedures

## Reporting

- [ ] Do not report SID History existence alone
- [ ] Identify current principal
- [ ] Identify historical SID
- [ ] Identify historical principal
- [ ] Identify affected resource
- [ ] Identify effective permission
- [ ] Explain migration context
- [ ] Explain trust context
- [ ] Explain security impact
- [ ] Provide dependency-aware remediation

---

# SID History Testing Model

The SID model is:

```text
Domain
  |
  v
Domain SID
  |
  +--> RID
  |
  v
Principal SID
```

The migration model is:

```text
Old Account
    |
    v
Old SID
    |
    v
Migration
    |
    v
New Account
    |
    +--> New SID
    |
    +--> Old SID in sIDHistory
```

The compatibility model is:

```text
New Account
    |
    v
SID History
    |
    v
Old SID
    |
    v
Legacy ACL
    |
    v
Access
```

The privilege model is:

```text
Current Account
      |
      v
Historical SID
      |
      v
Privileged ACL
      |
      v
Unexpected Access
```

The group model is:

```text
Current Group
      |
      v
Historical Group SID
      |
      v
Legacy Permission
      |
      v
All Current Group Members
```

The trust model is:

```text
Identity
   |
   v
SID Set
   |
   v
Trust Boundary
   |
   v
SID Filtering
   |
   v
Authorisation
```

The selective-authentication model is:

```text
Foreign Identity
      |
      v
Trust
      |
      v
SID Filtering
      |
      v
Allowed to Authenticate
      |
      v
Resource ACL
```

The migration lifecycle is:

```text
Migration
   |
   v
SID History
   |
   v
Temporary Compatibility
   |
   v
ACL Migration
   |
   v
Validation
   |
   v
Cleanup
```

The unhealthy lifecycle is:

```text
Migration
   |
   v
SID History
   |
   v
Migration Completed
   |
   v
No Cleanup
   |
   v
Legacy Permissions Persist
```

The detection model is:

```text
SID History Change
       |
       v
Account
       |
       v
Authentication
       |
       v
Historical Permission
       |
       v
Sensitive Resource
```

The defensive model is:

```text
Controlled Migration
       +
SID Filtering
       +
Migration Inventory
       +
ACL Migration
       +
Least Privilege
       +
Monitoring
       +
Cleanup
       =
Reduced SID History Risk
```

For penetration testers:

```text
Do Not Ask:
"Does this account have SID History?"

Ask:
"What access does the historical SID
still provide?"
```

For defenders:

```text
Do Not Ask:
"Can we delete every SID History value?"

Ask:
"Which resources still depend on each
historical SID, and how can those
dependencies be safely removed?"
```

The complete model is:

```text
Historical Identity
       |
       v
SID History
       |
       v
Current Identity
       |
       v
Authentication
       |
       v
Historical ACL
       |
       v
Effective Access
       |
       v
Security Impact
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Domain and Forest Trusts:

[Domain and Forest Trusts](trusts.md)

Trust Relationships:

[Trust Relationships](trust-relationships.md)

Active Directory Enumeration:

[Enumeration](enumeration.md)

Groups:

[Groups](groups.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Group Policy:

[Group Policy](group-policy.md)

BloodHound:

[BloodHound](bloodhound.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

SMB:

[SMB](smb.md)

WinRM:

[WinRM](winrm.md)

WMI:

[WMI](wmi.md)

DCOM:

[DCOM](dcom.md)

The next trust-specific page is:

```text
docs/active-directory/trust-tickets.md
```

---

# References

## Microsoft - sIDHistory Attribute

[Microsoft - sIDHistory Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-sidhistory){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Identifiers

[Microsoft - Security Identifiers](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Identifier Architecture

[Microsoft - Security Identifier Architecture](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADUser

[Microsoft - Get-ADUser](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-aduser){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADGroup

[Microsoft - Get-ADGroup](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroup){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADObject

[Microsoft - Get-ADObject](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adobject){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 4765

[Microsoft - 4765: SID History Was Added to an Account](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4765){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 4766

[Microsoft - 4766: An Attempt to Add SID History to an Account Failed](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4766){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 5136

[Microsoft - 5136: A Directory Service Object Was Modified](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5136){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Account Manipulation: Additional Cloud Roles

SID History does not map neatly to a single current ATT&CK sub-technique in every scenario. Use the ATT&CK technique that corresponds to the demonstrated behaviour rather than assigning a technique solely because `sIDHistory` exists.

[MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

SID History exists to solve a legitimate migration problem:

```text
Identity Changes
      |
      v
SID Changes
      |
      v
Existing ACLs Break
```

SID History temporarily bridges that gap:

```text
New Identity
      |
      v
Old SID Preserved
      |
      v
Legacy Access Continues
```

The security problem appears when:

```text
Temporary Compatibility
```

becomes:

```text
Permanent Hidden Privilege
```

A proper assessment therefore follows:

```text
Find SID History
      |
      v
Identify Historical SID
      |
      v
Identify Historical Principal
      |
      v
Understand Migration Context
      |
      v
Understand Trust Context
      |
      v
Find Remaining Permission
      |
      v
Validate Effective Access
      |
      v
Determine Security Impact
```

The presence of `sIDHistory` alone should not be reported as a vulnerability.

The important question is:

```text
What does this SID still authorise?
```

Defenders should work toward:

```text
Migration
   |
   v
Temporary SID History
   |
   v
Resource ACL Migration
   |
   v
Validation
   |
   v
Removal of Legacy Dependencies
```

while maintaining:

```text
SID Filtering
Least Privilege
Migration Monitoring
Trust Governance
Administrative Separation
```

The next page covers the Kerberos side of Active Directory trust relationships:

```text
Trust Tickets
```
