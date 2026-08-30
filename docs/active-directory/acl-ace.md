# Active Directory ACL and ACE Abuse

Active Directory uses Access Control Lists (ACLs) to determine which security principals are permitted to perform operations on directory objects.

These permissions control actions such as:

```text
Reading object properties
Writing object properties
Resetting passwords
Changing group membership
Modifying permissions
Changing object ownership
Creating child objects
Deleting objects
Modifying delegation
Modifying SPNs
Modifying certificate-related attributes
```

ACLs are fundamental to Active Directory administration.

They are also one of the most important sources of privilege-escalation paths in complex Active Directory environments.

A simplified model is:

```text
Active Directory Object
        |
        v
Security Descriptor
        |
        +--> Owner
        |
        +--> DACL
        |     |
        |     +--> ACE
        |     +--> ACE
        |     +--> ACE
        |
        +--> SACL
```

The central security question during an assessment is:

```text
Who can control what?
```

For example:

```text
Low-Privilege User
        |
        v
GenericWrite
        |
        v
Service Account
        |
        v
Modify Security-Relevant Property
        |
        v
Privilege Escalation
```

or:

```text
Helpdesk Group
      |
      v
GenericAll
      |
      v
Server Admin Group
      |
      v
Modify Membership
      |
      v
Administrative Access
```

ACL analysis therefore connects:

```text
Identity
   +
Permission
   +
Target Object
   +
Security-Relevant Operation
   +
Resulting Privilege
```

!!! warning "Authorised testing only"
    Active Directory ACL testing can modify passwords, group memberships, object ownership, permissions, delegation settings, SPNs, and other security-sensitive attributes. Prefer read-only enumeration first. Only perform modifications explicitly permitted by the engagement scope, record the exact original state before making changes, use dedicated test objects where possible, and restore the environment after validation.

---

# Core Terminology

The most important terms are:

```text
Security Descriptor
ACL
DACL
SACL
ACE
SID
Owner
Trustee
Inheritance
Object-Specific ACE
```

Understanding these concepts makes BloodHound attack paths significantly easier to interpret.

---

# Security Descriptor

Every securable Active Directory object has a security descriptor.

Conceptually:

```text
Security Descriptor
        |
        +--> Owner SID
        |
        +--> Primary Group
        |
        +--> DACL
        |
        +--> SACL
```

The security descriptor describes:

```text
Who owns the object?

Who is allowed access?

Who is denied access?

Which actions can be audited?
```

---

# DACL

The:

```text
Discretionary Access Control List
```

or:

```text
DACL
```

determines which principals are allowed or denied access to the object.

Conceptually:

```text
DACL
 |
 +--> Allow Alice - Read
 |
 +--> Allow Helpdesk - Reset Password
 |
 +--> Allow ServerAdmins - GenericAll
 |
 +--> Deny Bob - Write
```

The DACL is the primary ACL of interest when analysing privilege-escalation paths.

---

# SACL

The:

```text
System Access Control List
```

or:

```text
SACL
```

controls auditing.

Conceptually:

```text
SACL
 |
 +--> Audit successful writes
 |
 +--> Audit failed writes
 |
 +--> Audit permission changes
```

The SACL does not normally grant access.

It determines which access attempts may generate security audit events.

---

# ACE

An:

```text
Access Control Entry
```

or:

```text
ACE
```

is an individual entry inside an ACL.

An ACE generally describes:

```text
Principal
   +
Allow / Deny
   +
Permission
   +
Optional Object Type
   +
Inheritance
```

Example:

```text
CORP\Helpdesk
      |
      v
ALLOW
      |
      v
Reset Password
      |
      v
CORP\Alice
```

---

# ACL vs ACE

The distinction is:

```text
ACL
 |
 +--> ACE 1
 +--> ACE 2
 +--> ACE 3
```

Therefore:

```text
ACL = collection of entries
ACE = individual entry
```

---

# SID

Permissions are fundamentally assigned to:

```text
Security Identifiers
```

rather than human-readable account names.

Example:

```text
S-1-5-21-111111111-222222222-333333333-1105
```

The SID may resolve to:

```text
CORP\alice
```

When reviewing raw ACLs, SID resolution is therefore important.

---

# Trustee

The principal to which an ACE applies is commonly called the:

```text
Trustee
```

For example:

```text
ACE
 |
 +--> Trustee: CORP\Helpdesk
 |
 +--> Right: Reset Password
 |
 +--> Target: CORP\Alice
```

---

# Object Owner

Active Directory objects have an owner.

Conceptually:

```text
Object
 |
 v
Owner SID
```

Ownership is security-sensitive because the owner can generally modify the object's discretionary ACL.

This creates attack paths involving:

```text
WriteOwner
```

---

# AccessCheck Concept

When a principal attempts an operation, Windows evaluates the security descriptor.

A simplified model is:

```text
Security Token
      |
      v
User SID
Group SIDs
Privileges
      |
      v
AccessCheck
      |
      +--> Object Security Descriptor
      |
      +--> DACL
      |
      +--> ACEs
      |
      v
Allowed / Denied
```

Effective permissions therefore depend on more than one ACE.

---

# Effective Permissions

Do not analyse an ACE in isolation.

Effective access can depend on:

```text
User SID
Group Membership
Nested Groups
Inherited ACEs
Explicit ACEs
Deny ACEs
Object-Specific ACEs
Ownership
AdminSDHolder
Protected Objects
```

The important question is:

```text
Can this principal actually perform
the security-sensitive operation?
```

rather than simply:

```text
Does an interesting ACE exist?
```

---

# Common Active Directory Rights

Frequently encountered rights include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
Self
CreateChild
DeleteChild
ExtendedRight
ReadProperty
GenericRead
```

Some tools present higher-level names such as:

```text
ForceChangePassword
AddMember
AddSelf
WriteSPN
DCSync
AllExtendedRights
```

These may represent specific underlying Active Directory rights or combinations of rights.

---

# GenericAll

`GenericAll` represents broad control over an object.

Conceptually:

```text
Principal
   |
   v
GenericAll
   |
   v
Target Object
```

This can often permit many operations against the target.

The exact practical impact depends on the object type.

---

# GenericAll over a User

Example:

```text
Alice
 |
 v
GenericAll
 |
 v
Bob
```

Potential security-relevant operations may include:

```text
Password reset
Attribute modification
SPN modification
Delegation-related changes
ACL modification
```

depending on effective permissions and directory protections.

The attack-path question becomes:

```text
What is Bob's privilege?
```

If Bob is:

```text
Domain Admin
```

the path may be highly significant.

---

# GenericAll over a Group

Example:

```text
Alice
 |
 v
GenericAll
 |
 v
Server Admins
```

If effective permissions permit group membership modification:

```text
Alice
 |
 v
Add Controlled Account
 |
 v
Server Admins
 |
 v
Inherited Administrative Access
```

This can create direct privilege escalation.

---

# GenericAll over a Computer

Example:

```text
Alice
 |
 v
GenericAll
 |
 v
SERVER01$
```

Potential attack paths may involve security-sensitive computer-object properties.

Examples include:

```text
RBCD
Shadow Credentials
SPN changes
ACL modification
```

depending on the environment and effective rights.

---

# GenericAll over an OU

Broad control over an Organizational Unit can be especially important.

```text
Alice
 |
 v
GenericAll
 |
 v
Servers OU
 |
 +--> SERVER01
 +--> SERVER02
 +--> SERVER03
```

Inheritance and child-object permissions determine the resulting impact.

Do not automatically assume:

```text
GenericAll on OU
 =
GenericAll on every child
```

without evaluating inheritance.

---

# GenericWrite

`GenericWrite` provides broad write capability but is more limited than `GenericAll`.

Conceptually:

```text
Principal
   |
   v
GenericWrite
   |
   v
Target
```

The security impact depends strongly on which target attributes can be modified.

---

# GenericWrite over a User

Potentially relevant attributes can include:

```text
servicePrincipalName
msDS-KeyCredentialLink
```

and other security-sensitive properties depending on the effective rights and environment.

This can potentially lead to techniques such as:

```text
Targeted Kerberoasting
Shadow Credentials
```

---

# GenericWrite over a Computer

A writable computer object may provide paths involving:

```text
Resource-Based Constrained Delegation
Shadow Credentials
SPN-related modifications
```

depending on effective rights.

For RBCD:

```text
GenericWrite
     |
     v
Computer Object
     |
     v
msDS-AllowedToActOnBehalfOfOtherIdentity
     |
     v
Potential Delegation Path
```

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# GenericWrite over a Group

Whether GenericWrite allows practical membership modification should be validated against the effective permissions and group object configuration.

Do not assume every generic-looking graph edge results in the same operation.

---

# WriteProperty

`WriteProperty` permits modification of one or more object properties.

The critical question is:

```text
Which property?
```

For example:

```text
WriteProperty
      |
      v
servicePrincipalName
```

has very different security implications from:

```text
WriteProperty
      |
      v
description
```

Therefore object-specific ACE analysis is essential.

---

# Object-Specific ACE

An ACE can apply to a specific property or property set.

Conceptually:

```text
ACE
 |
 +--> Principal: Alice
 |
 +--> Right: WriteProperty
 |
 +--> Object Type GUID
 |
 +--> servicePrincipalName
```

Tools such as PowerView can resolve many GUIDs into readable names.

---

# WriteSPN

If a principal can modify:

```text
servicePrincipalName
```

on a user account, the account may potentially be made Kerberoastable.

Conceptually:

```text
Attacker
   |
   v
WriteSPN
   |
   v
Target User
   |
   v
Add Temporary SPN
   |
   v
Request Service Ticket
   |
   v
Offline Password Guessing
```

This is commonly called:

```text
Targeted Kerberoasting
```

---

# Targeted Kerberoasting

Suppose:

```text
Alice
 |
 v
WriteSPN
 |
 v
Bob
```

and Bob has no SPN.

An authorised attack-path validation could conceptually be:

```text
Record Bob's SPNs
       |
       v
Add Temporary Test SPN
       |
       v
Request Ticket
       |
       v
Restore Original SPNs
```

This modifies Active Directory and should only be performed where explicitly authorised.

For Kerberoasting fundamentals:

[Kerberoasting](kerberoasting.md)

---

# WriteDACL

`WriteDACL` permits modification of the target object's discretionary ACL.

This is extremely security-sensitive.

Conceptually:

```text
Alice
 |
 v
WriteDACL
 |
 v
Target
 |
 v
Modify DACL
 |
 v
Grant Additional Permission
 |
 v
Control Target
```

For example:

```text
Alice
 |
 v
WriteDACL
 |
 v
Bob
 |
 v
Grant Alice GenericAll
 |
 v
Alice Controls Bob
```

This creates an indirect privilege-escalation path.

---

# WriteDACL Is a Permission-Granting Primitive

The important model is:

```text
WriteDACL
    |
    v
Change Permissions
    |
    v
Grant Useful Right
    |
    v
Perform Useful Operation
```

Examples of useful rights might include:

```text
Reset Password
WriteProperty
GenericAll
Replication Rights
Group Membership Rights
```

depending on the target.

---

# WriteOwner

`WriteOwner` permits changing the owner of an object.

Conceptually:

```text
Alice
 |
 v
WriteOwner
 |
 v
Bob Object
 |
 v
Alice Becomes Owner
```

Ownership can then provide a path toward DACL modification.

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
Grant Permission
    |
    v
Control Object
```

This makes `WriteOwner` a potentially powerful indirect privilege-escalation primitive.

---

# Ownership Does Not Automatically Mean Immediate Full Control

Keep the stages separate:

```text
Become Owner
     |
     v
Modify DACL
     |
     v
Grant Desired Right
     |
     v
Perform Operation
```

This distinction is useful for both testing and reporting.

---

# ForceChangePassword

Some principals may have the extended right to reset another user's password without knowing the current password.

BloodHound commonly represents this as:

```text
ForceChangePassword
```

Conceptually:

```text
Alice
 |
 v
ForceChangePassword
 |
 v
Bob
```

The resulting security impact depends on Bob's privileges and whether changing Bob's password would disrupt services.

---

# Password Reset Risk

Password resets can be highly disruptive.

The target may be:

```text
Service Account
Scheduled Task Account
Application Pool Identity
Database Service Account
Automation Account
Human User
```

Changing the password can cause:

```text
Service Outage
Account Lockout
Authentication Failures
Scheduled Task Failures
Application Failure
```

Therefore, avoid resetting production credentials merely to prove ACL control.

---

# Safe Password-Reset Validation

Prefer:

```text
ACL Evidence
    +
BloodHound Path
    +
Native Permission Confirmation
```

over:

```text
Actually Reset Production Password
```

unless the engagement specifically requires active validation.

---

# AddMember

A principal may have rights to modify a group's membership.

Conceptually:

```text
Alice
 |
 v
AddMember
 |
 v
Server Admins
```

Potential validation:

```text
Controlled Test Account
        |
        v
Add to Group
        |
        v
Confirm Membership
        |
        v
Remove Immediately
```

Only perform this where explicitly authorised.

---

# AddSelf

Some group ACLs allow a principal to add itself to a group.

Conceptually:

```text
Alice
 |
 v
AddSelf
 |
 v
Group
```

This is different from unrestricted control over group membership.

---

# Group Membership Privilege

Always determine what the group actually provides.

```text
Group
 |
 +--> Local Administrator?
 |
 +--> GPO Management?
 |
 +--> Server Access?
 |
 +--> Domain Admin?
 |
 +--> Backup Privileges?
 |
 +--> Application Privileges?
```

The name alone may not accurately describe the security impact.

---

# AllExtendedRights

`AllExtendedRights` can provide broad access to extended rights supported by an object.

For a user object, this may include security-sensitive operations such as password-reset rights depending on the object's effective ACL.

Do not translate:

```text
AllExtendedRights
```

directly into:

```text
Full Control
```

The exact impact remains object-specific.

---

# Extended Rights

Active Directory defines extended rights for operations that do not map neatly to ordinary property access.

Examples include:

```text
User-Force-Change-Password
Replication-Get-Changes
Replication-Get-Changes-All
Replication-Get-Changes-In-Filtered-Set
```

These rights can be extremely security-sensitive.

---

# DCSync Rights

DCSync is an important example of ACL-based privilege.

A principal may obtain replication rights such as:

```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

and, depending on the environment and objective:

```text
DS-Replication-Get-Changes-In-Filtered-Set
```

Conceptually:

```text
Principal
   |
   v
Directory Replication Rights
   |
   v
Domain Naming Context
   |
   v
Replicate Credential Data
```

This can expose highly sensitive domain credential material.

---

# DCSync Is Not Domain Admin Membership

A principal does not need to be:

```text
Domain Admin
```

if it has been delegated sufficient directory replication rights.

Therefore:

```text
Group Membership Analysis
```

alone is insufficient.

ACL analysis is necessary.

---

# DCSync BloodHound Path

A conceptual BloodHound path may appear as:

```text
Alice
 |
 +--> GetChanges
 |
 +--> GetChangesAll
 |
 v
CORP.EXAMPLE
```

The combination can represent replication capability against the domain naming context.

---

# DCSync Testing

DCSync can retrieve reusable credential material and is therefore highly sensitive.

During an assessment, prefer proving:

```text
Replication Rights Exist
```

without retrieving unnecessary production credential data.

If active validation is explicitly required, target the minimum authorised account and handle all resulting credential material according to the engagement evidence policy.

---

# CreateChild

`CreateChild` permits creation of specified object types beneath a container.

Example:

```text
Alice
 |
 v
CreateChild
 |
 v
Workstations OU
 |
 v
Computer Object
```

The resulting security impact depends on:

```text
Child Type
Container
Inherited ACLs
Automatic Group Membership
GPO Scope
Delegation
Provisioning Processes
```

---

# DeleteChild

`DeleteChild` can permit deletion of child objects.

This may be operationally severe even where it does not provide privilege escalation.

For example:

```text
DeleteChild
     |
     v
Production Computer Object
     |
     v
Potential Service Disruption
```

Avoid destructive validation.

---

# Delete

A principal with delete rights over an object may cause availability or recovery impact.

This is normally demonstrated through ACL evidence rather than deleting production directory objects.

---

# WriteAccountRestrictions

Modern BloodHound graphs may expose more specific permission relationships associated with sets of account-related attributes.

Treat these as property-specific capabilities.

Determine:

```text
Which underlying attributes?
        |
        v
What can actually be changed?
        |
        v
Which attack path becomes possible?
```

Do not infer arbitrary account control from the edge name alone.

---

# WriteGPLink

Control over Group Policy links can create significant privilege-escalation paths.

Conceptually:

```text
Alice
 |
 v
WriteGPLink
 |
 v
OU
 |
 v
Link Attacker-Controlled GPO
 |
 v
Affected Computers / Users
```

This is separate from control over the GPO itself.

---

# GPO Control

A GPO consists of both Active Directory and SYSVOL components.

Conceptually:

```text
Group Policy Object
       |
       +--> AD Object
       |
       +--> SYSVOL Files
```

Practical GPO abuse therefore requires careful analysis of:

```text
GPO Permissions
SYSVOL Permissions
GPO Links
OU Scope
Security Filtering
WMI Filters
Inheritance
```

A dedicated Group Policy page should cover these mechanics in detail.

---

# AdminSDHolder

Active Directory protects certain privileged accounts and groups using:

```text
AdminSDHolder
```

and:

```text
SDProp
```

Protected objects can have their permissions periodically reset based on the AdminSDHolder security descriptor.

Conceptually:

```text
AdminSDHolder
      |
      v
Security Descriptor
      |
      v
SDProp
      |
      v
Protected Accounts / Groups
```

---

# adminCount

Objects that have been subject to protected-group processing may have:

```text
adminCount=1
```

This is useful context but should not be treated as perfect proof of current privileged membership.

Accounts can retain:

```text
adminCount=1
```

after being removed from protected groups.

---

# Enumerate adminCount

PowerShell:

```powershell
Get-ADUser \
    -LDAPFilter '(adminCount=1)' \
    -Properties adminCount |
    Select-Object \
        SamAccountName,
        Enabled,
        adminCount
```

Groups:

```powershell
Get-ADGroup \
    -LDAPFilter '(adminCount=1)' \
    -Properties adminCount |
    Select-Object \
        Name,
        GroupScope,
        adminCount
```

---

# AdminSDHolder Security Importance

Unexpected write control over:

```text
CN=AdminSDHolder,CN=System,<DOMAIN_DN>
```

can be extremely significant because changes may propagate to protected objects.

Do not modify AdminSDHolder during routine validation.

Read-only evidence and attack-path analysis are normally sufficient.

---

# Inheritance

Active Directory permissions can be inherited from parent containers.

Conceptually:

```text
OU=Servers
   |
   +--> ACE: Helpdesk WriteProperty
   |
   v
SERVER01
SERVER02
SERVER03
```

If the ACE is inheritable, child objects may receive the permission.

---

# Explicit vs Inherited ACE

An ACE can be:

```text
Explicit
```

or:

```text
Inherited
```

Example:

```text
SERVER01
 |
 +--> Explicit ACE
 |
 +--> Inherited ACE from Servers OU
```

Understanding the source of a permission is important for remediation.

---

# Inheritance Flags

Raw ACLs may expose inheritance-related fields such as:

```text
InheritanceType
IsInherited
InheritanceFlags
PropagationFlags
```

Interpret them carefully.

The effective permission may apply to:

```text
This object only
Child objects only
This object and descendants
Specific child object types
```

---

# Object-Type Inheritance

An inherited ACE may apply only to specific child classes.

For example:

```text
OU
 |
 v
ACE
 |
 v
InheritedObjectType = User
```

This might apply to user objects but not computer objects.

Therefore:

```text
Inherited ACE Exists
```

does not automatically mean:

```text
Every Child Object Is Affected
```

---

# Deny ACEs

DACLs can contain:

```text
ALLOW
```

and:

```text
DENY
```

entries.

A simplified model is:

```text
DACL
 |
 +--> DENY
 |
 +--> ALLOW
```

Effective access depends on Windows access-check semantics, ACE ordering, explicit versus inherited entries, requested rights, and token membership.

Do not manually infer complex effective access from one displayed line where native tooling can validate it.

---

# Nested Groups

Suppose:

```text
Alice
 |
 v
Helpdesk
 |
 v
IT Operations
 |
 v
ACL on SERVER01
```

Alice may receive the permission through nested group membership.

Therefore ACL analysis should resolve:

```text
Direct Membership
Nested Membership
Domain Local Groups
Global Groups
Universal Groups
Cross-Domain Groups
```

---

# SIDHistory

A user's token can also contain SIDs derived from:

```text
sIDHistory
```

where configured.

This can influence effective access.

Therefore:

```text
Visible Current Group Membership
```

may not always explain every permission.

SID History should be analysed separately in trust and migration contexts.

---

# Native Windows ACL Enumeration

The Active Directory PowerShell module provides a useful starting point.

Identify the object's distinguished name:

```powershell
$user = Get-ADUser 'alice'
$user.DistinguishedName
```

Example:

```text
CN=Alice Smith,OU=Users,DC=corp,DC=example
```

---

# Get-Acl with the AD Provider

Where the Active Directory PowerShell provider is available:

```powershell
Get-Acl "AD:\CN=Alice Smith,OU=Users,DC=corp,DC=example"
```

More readable output:

```powershell
(Get-Acl "AD:\CN=Alice Smith,OU=Users,DC=corp,DC=example").Access |
    Format-Table \
        IdentityReference,
        ActiveDirectoryRights,
        AccessControlType,
        ObjectType,
        InheritanceType,
        IsInherited \
        -AutoSize
```

---

# Enumerate a Computer ACL

```powershell
$computer = Get-ADComputer 'SERVER01'

(Get-Acl "AD:\$($computer.DistinguishedName)").Access |
    Format-Table \
        IdentityReference,
        ActiveDirectoryRights,
        AccessControlType,
        ObjectType,
        InheritanceType,
        IsInherited \
        -AutoSize
```

---

# Enumerate a Group ACL

```powershell
$group = Get-ADGroup 'Server Admins'

(Get-Acl "AD:\$($group.DistinguishedName)").Access |
    Format-Table \
        IdentityReference,
        ActiveDirectoryRights,
        AccessControlType,
        ObjectType,
        InheritanceType,
        IsInherited \
        -AutoSize
```

---

# Enumerate an OU ACL

```powershell
$ou = Get-ADOrganizationalUnit \
    -Filter "Name -eq 'Servers'"

(Get-Acl "AD:\$($ou.DistinguishedName)").Access |
    Format-Table \
        IdentityReference,
        ActiveDirectoryRights,
        AccessControlType,
        ObjectType,
        InheritanceType,
        IsInherited \
        -AutoSize
```

---

# Enumerate the Owner

```powershell
(Get-Acl "AD:\$($user.DistinguishedName)").Owner
```

For a computer:

```powershell
$computer = Get-ADComputer 'SERVER01'

(Get-Acl "AD:\$($computer.DistinguishedName)").Owner
```

Unexpected ownership should be investigated.

---

# PowerView

PowerView is particularly useful for offensive ACL analysis.

A common command is:

```powershell
Get-DomainObjectAcl \
    -Identity 'alice' \
    -ResolveGUIDs
```

This can expose fields such as:

```text
AceQualifier
ObjectDN
ActiveDirectoryRights
ObjectAceType
SecurityIdentifier
IsInherited
```

---

# ResolveGUIDs

The:

```text
-ResolveGUIDs
```

option is useful because Active Directory ACLs frequently contain schema GUIDs.

Without resolution:

```text
bf9679c0-0de6-11d0-a285-00aa003049e2
```

With resolution, tooling may translate the GUID into a meaningful object or property type.

This makes analysis considerably easier.

---

# Find Interesting ACLs with PowerView

PowerView versions differ, but commonly used approaches include:

```powershell
Find-InterestingDomainAcl \
    -ResolveGUIDs
```

Check the loaded PowerView version:

```powershell
Get-Help Find-InterestingDomainAcl -Full
```

Do not assume every fork exposes identical parameters.

---

# Filter ACLs for a Principal

A practical workflow is:

```text
Resolve User SID
      |
      v
Enumerate ACLs
      |
      v
Filter SecurityIdentifier
      |
      v
Analyse Targets
```

Example:

```powershell
$user = Get-DomainUser -Identity 'alice'
$sid = $user.objectsid

Get-DomainObjectAcl \
    -ResolveGUIDs |
    Where-Object {
        $_.SecurityIdentifier -eq $sid
    }
```

Large domains can produce significant output, so targeted enumeration is preferable where possible.

---

# BloodHound

BloodHound is one of the best tools for understanding ACL attack paths.

Instead of analysing permissions as isolated entries:

```text
Alice -> GenericWrite -> Bob
```

BloodHound can connect them:

```text
Alice
 |
 v
GenericWrite
 |
 v
Bob
 |
 v
MemberOf
 |
 v
Server Admins
 |
 v
AdminTo
 |
 v
SERVER01
```

This converts raw permissions into:

```text
Attack Paths
```

---

# Useful BloodHound ACL Edges

Depending on the BloodHound version and collected data, relevant relationships can include:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
ForceChangePassword
AddMember
AddSelf
AllExtendedRights
WriteSPN
AddKeyCredentialLink
AllowedToAct
AllowedToDelegate
GetChanges
GetChangesAll
GetChangesInFilteredSet
WriteGPLink
```

Not every edge applies to every object type.

---

# BloodHound Workflow

A useful methodology is:

```text
Collect
   |
   v
Find Owned / Controlled Principals
   |
   v
Search Outbound Object Control
   |
   v
Identify ACL Edges
   |
   v
Follow Resulting Privilege
   |
   v
Validate Effective Permission
   |
   v
Choose Minimum-Impact Proof
```

---

# Outbound Object Control

For each controlled principal, ask:

```text
What objects can this principal control?
```

For example:

```text
Alice
 |
 +--> GenericWrite -> Bob
 |
 +--> AddMember -> Server Admins
 |
 +--> GenericAll -> SERVER01
 |
 +--> WriteDACL -> Helpdesk
```

This is often more useful than beginning with a random high-value target and working backwards.

---

# Inbound Object Control

For a sensitive target, ask:

```text
Who can control this object?
```

For example:

```text
Domain Admins
      ^
      |
 +----+----------+
 |               |
Alice          Helpdesk
AddMember      GenericAll
```

This is valuable for defensive review.

---

# BloodHound Does Not Replace Validation

BloodHound should be treated as:

```text
Attack-Path Analysis
```

not:

```text
Absolute Proof of Effective Access
```

For important findings:

```text
BloodHound
    |
    v
Identify Candidate Path
    |
    v
Native / LDAP / PowerView Confirmation
    |
    v
Controlled Validation
```

---

# Linux ACL Enumeration

Linux-based Active Directory testing can use tools such as:

```text
BloodHound.py
bloodyAD
Impacket
ldapsearch
NetExec
```

The most appropriate tool depends on the exact operation.

---

# BloodHound.py

BloodHound.py can collect Active Directory information from Linux.

Check:

```bash
bloodhound-python -h
```

For BloodHound Community Edition, use the collector/version appropriate to the environment and verify its current CLI before collection.

A typical collection concept is:

```text
Domain Credentials
      |
      v
LDAP / DNS / SMB
      |
      v
BloodHound Collector
      |
      v
JSON
      |
      v
BloodHound
```

For detailed usage:

[BloodHound](bloodhound.md)

---

# bloodyAD

`bloodyAD` is an Active Directory privilege-escalation and object-manipulation utility.

Check:

```bash
bloodyAD --help
```

It can assist with operations involving:

```text
Users
Groups
Computers
ACLs
Object Ownership
Attributes
Passwords
Delegation
```

Because syntax changes between versions, always inspect the help for the installed release before performing a write operation.

---

# ldapsearch

LDAP can enumerate object security descriptors, but raw ACL analysis is more complicated than ordinary attribute enumeration.

A normal LDAP query might identify the object:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(sAMAccountName=SERVER01$)' \
    distinguishedName \
    objectSid
```

Retrieving and decoding:

```text
nTSecurityDescriptor
```

requires appropriate LDAP controls and security-descriptor parsing.

Specialised tooling is generally easier for large-scale ACL analysis.

---

# nTSecurityDescriptor

The primary Active Directory attribute containing an object's security descriptor is:

```text
nTSecurityDescriptor
```

Conceptually:

```text
Object
 |
 v
nTSecurityDescriptor
 |
 +--> Owner
 |
 +--> DACL
 |
 +--> SACL
```

Access to different parts of the descriptor can depend on permissions and LDAP controls.

---

# LDAP_SERVER_SD_FLAGS_OID

LDAP clients can use the Security Descriptor Flags control:

```text
1.2.840.113556.1.4.801
```

to specify which portions of the security descriptor should be returned.

This is useful when implementing custom ACL enumeration or analysis tooling.

---

# ACL Attack Path - User Password Reset

Example:

```text
Alice
 |
 v
ForceChangePassword
 |
 v
Bob
 |
 v
MemberOf
 |
 v
Server Admins
```

Potential impact:

```text
Control Bob
    |
    v
Server Admin Privileges
```

Safe validation should avoid resetting Bob's production password where graph and ACL evidence already proves the path.

---

# ACL Attack Path - Group Membership

Example:

```text
Alice
 |
 v
AddMember
 |
 v
Backup Admins
 |
 v
Privileged Servers
```

A controlled proof may use a dedicated test account if membership changes are authorised.

---

# ACL Attack Path - Targeted Kerberoasting

```text
Alice
 |
 v
WriteSPN
 |
 v
svc_backup
 |
 v
Temporary SPN
 |
 v
Kerberos Service Ticket
 |
 v
Offline Password Guessing
```

The root cause is:

```text
Unauthorized SPN Write Capability
```

not Kerberoasting itself.

---

# ACL Attack Path - RBCD

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
RBCD Attribute
 |
 v
Controlled Principal
 |
 v
S4U
 |
 v
SERVER01
```

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# ACL Attack Path - Shadow Credentials

Conceptually:

```text
Alice
 |
 v
Write msDS-KeyCredentialLink
 |
 v
Bob
 |
 v
Add Key Credential
 |
 v
Certificate-Based Authentication
 |
 v
Authenticate as Bob
```

This is commonly known as:

```text
Shadow Credentials
```

Detailed coverage belongs in:

```text
active-directory/shadow-credentials.md
```

---

# ACL Attack Path - DCSync

```text
Alice
 |
 +--> GetChanges
 |
 +--> GetChangesAll
 |
 v
Domain
 |
 v
Directory Replication
 |
 v
Credential Material
```

This can result in domain-wide impact depending on the rights and accounts accessed.

---

# ACL Attack Path - WriteDACL

```text
Alice
 |
 v
WriteDACL
 |
 v
Bob
 |
 v
Grant GenericAll
 |
 v
Control Bob
```

The intermediate DACL modification should be documented.

---

# ACL Attack Path - WriteOwner

```text
Alice
 |
 v
WriteOwner
 |
 v
Bob
 |
 v
Become Owner
 |
 v
Modify DACL
 |
 v
Grant GenericAll
 |
 v
Control Bob
```

This is a multi-stage ACL escalation chain.

---

# ACL Attack Path - Group ACL

```text
Alice
 |
 v
GenericAll
 |
 v
Privileged Group
 |
 v
Add Controlled User
 |
 v
Privilege
```

The group's effective privileges determine severity.

---

# ACL Attack Path - OU

```text
Alice
 |
 v
Control OU
 |
 v
Inherited Permissions
 |
 v
Computer Objects
 |
 v
Sensitive Servers
```

OU-level ACL weaknesses can have a large blast radius.

---

# ACL Attack Path - GPO

```text
Alice
 |
 v
Control GPO
 |
 v
GPO Linked to Servers OU
 |
 v
SERVER01
SERVER02
SERVER03
 |
 v
Potential Code / Configuration Impact
```

GPO modification is highly intrusive and should normally not be used for routine proof-of-concept validation in production.

---

# ACL Attack Path - AdminSDHolder

Conceptually:

```text
Attacker
 |
 v
Control AdminSDHolder
 |
 v
Modify Security Descriptor
 |
 v
SDProp
 |
 v
Protected Objects
```

This can provide persistence or broad privileged-object control.

Do not actively modify AdminSDHolder during normal production testing.

---

# Object Type Matters

The same right can have different consequences depending on the target.

Example:

```text
GenericAll
```

over:

```text
User
```

may lead to:

```text
Account Control
```

while GenericAll over:

```text
Group
```

may lead to:

```text
Membership Control
```

and GenericAll over:

```text
Computer
```

may lead to:

```text
Delegation / Attribute Abuse
```

Therefore always record:

```text
Principal
Right
Target
Target Type
Resulting Operation
Resulting Privilege
```

---

# Attack Path Analysis Methodology

For every interesting ACE:

```text
ACE
 |
 v
Who Has the Right?
 |
 v
Do We Control Them?
 |
 v
What Is the Target?
 |
 v
What Operation Does the Right Permit?
 |
 v
Can That Operation Be Performed?
 |
 v
What Privilege Results?
 |
 v
Can It Be Proven Safely?
```

---

# Step 1 - Identify Controlled Principals

Controlled principals may include:

```text
Compromised User
Compromised Computer
Service Account
Test Account
Owned BloodHound Node
```

Do not assume that every low-privileged user is equivalent.

Group memberships and delegated permissions can differ significantly.

---

# Step 2 - Enumerate Outbound Rights

Determine:

```text
What can the controlled principal modify?
```

Prioritise:

```text
Users
Groups
Computers
OUs
GPOs
Domain Object
AdminSDHolder
Certificate-Related Objects
```

---

# Step 3 - Determine the Exact Right

Do not stop at:

```text
Write Access
```

Determine:

```text
GenericAll?
GenericWrite?
WriteProperty?
Which property?
WriteDACL?
WriteOwner?
Extended Right?
CreateChild?
```

---

# Step 4 - Determine Target Value

A writable account with no meaningful privileges may be low impact.

A writable account that controls:

```text
Tier 0 Infrastructure
```

may be critical.

Analyse:

```text
Group Membership
AdminTo
Sessions
Delegation
DCSync
GPO Rights
Local Admin
Certificate Authority Roles
Trust Relationships
```

---

# Step 5 - Determine the Security Primitive

Map the ACL to the actual operation.

Example:

```text
GenericWrite -> User
```

is too vague.

A stronger analysis is:

```text
GenericWrite -> User
        |
        v
Write servicePrincipalName
        |
        v
Targeted Kerberoasting
```

or:

```text
GenericWrite -> User
        |
        v
Write msDS-KeyCredentialLink
        |
        v
Shadow Credentials
```

---

# Step 6 - Choose Minimum-Impact Validation

Possible validation levels are:

```text
Level 1 - ACL Evidence
Level 2 - Independent Permission Confirmation
Level 3 - Benign Attribute Change
Level 4 - Controlled Security Operation
Level 5 - Full Privilege Demonstration
```

Use the lowest level that proves the finding.

---

# Level 1 - ACL Evidence

Example:

```text
BloodHound:
Alice -> GenericAll -> Server Admins
```

plus:

```text
PowerView:
ActiveDirectoryRights = GenericAll
```

may already provide strong evidence.

---

# Level 2 - Independent Confirmation

Confirm using native tools:

```powershell
Get-Acl "AD:\<DISTINGUISHED_NAME>"
```

This reduces reliance on a single offensive tool.

---

# Level 3 - Benign Attribute Change

Where authorised, modify a non-security-critical test attribute on a dedicated test object.

For example:

```text
description
```

This can prove generic write capability without modifying credentials or group membership.

Do not assume success against a benign property proves access to a separately protected object-specific property.

---

# Level 4 - Controlled Security Operation

Examples:

```text
Add test user to test group
Add temporary SPN to test account
Add test RBCD principal
Add test key credential
```

Only perform the operation relevant to the actual finding.

---

# Level 5 - Full Privilege Demonstration

Examples:

```text
Administrative Authentication
Sensitive Group Membership
Service Impersonation
Domain Replication
```

This level should be used only when necessary and explicitly authorised.

---

# ACL Evidence

Strong ACL evidence should show:

```text
Source Principal
Source SID
Target Object
Target DN
Target SID
ACE Type
Access Type
ActiveDirectoryRights
ObjectAceType
Inheritance
Owner
Resulting Attack Path
```

---

# Example Evidence

```text
Source:
CORP\alice

Source SID:
S-1-5-21-[REDACTED]-1105

Target:
CORP\svc_backup

Target DN:
CN=svc_backup,OU=Service Accounts,DC=corp,DC=example

Permission:
WriteProperty

Object Type:
servicePrincipalName

Inherited:
False

Security Impact:
The source account can modify the servicePrincipalName attribute of the
target account, enabling the target to be made Kerberoastable.
```

---

# Evidence Redaction

Usually safe to include:

```text
Account Names
Group Names
Object Names
Permission Names
Object Types
```

depending on report sensitivity.

Redact:

```text
Passwords
NT Hashes
AES Keys
TGTs
Service Tickets
Private Keys
Reusable Certificates
```

---

# Detection

ACL abuse detection should combine:

```text
Directory Changes
      +
ACL Changes
      +
Sensitive Attribute Changes
      +
Group Membership Changes
      +
Password Resets
      +
Kerberos Activity
      +
Endpoint Activity
```

---

# Event 5136

Where Directory Service Changes auditing is configured:

```text
5136
```

can record modifications to Active Directory objects.

This is highly useful for detecting changes to security-sensitive attributes.

Examples include:

```text
servicePrincipalName
msDS-AllowedToActOnBehalfOfOtherIdentity
msDS-KeyCredentialLink
```

depending on auditing configuration.

---

# Event 5136 Model

```text
5136
 |
 +--> Who changed the object?
 |
 +--> Which object?
 |
 +--> Which attribute?
 |
 +--> Add or delete?
 |
 +--> What value?
 |
 +--> When?
```

Correlate this with authentication and endpoint telemetry.

---

# Event 4670

Event:

```text
4670
```

records permissions on an object being changed for supported audited object types.

Its usefulness for Active Directory investigations depends on the object and audit configuration.

Directory Service Changes and directory-specific auditing should also be used.

---

# Event 4662

Event:

```text
4662
```

can record operations performed on Active Directory objects when appropriate auditing and SACLs are configured.

This is particularly important for monitoring certain directory rights, including replication-related activity.

---

# DCSync Detection

DCSync detection commonly involves monitoring directory replication operations associated with replication-right GUIDs.

A strong detection strategy asks:

```text
Who is performing replication?
        |
        v
Is the source a Domain Controller?
        |
   +----+----+
   |         |
  Yes        No
             |
             v
        Investigate
```

Legitimate replication normally originates from expected domain controllers and authorised directory-management systems.

---

# Event 4728

For security-enabled global groups:

```text
4728
```

records a member being added.

This can help detect ACL abuse resulting in group membership changes.

---

# Event 4729

```text
4729
```

records a member being removed from a security-enabled global group.

This can be useful for identifying temporary privilege escalation followed by cleanup.

---

# Event 4732

```text
4732
```

records a member being added to a security-enabled local group.

---

# Event 4733

```text
4733
```

records a member being removed from a security-enabled local group.

---

# Event 4756

```text
4756
```

records a member being added to a security-enabled universal group.

---

# Event 4757

```text
4757
```

records a member being removed from a security-enabled universal group.

---

# Event 4724

```text
4724
```

records an attempt to reset an account's password.

This can be relevant to:

```text
ForceChangePassword
```

abuse.

---

# Event 4738

```text
4738
```

records changes to user accounts.

It can provide supporting context for certain attribute modifications.

---

# Event 4742

```text
4742
```

records changes to computer accounts.

This may provide context for computer-object abuse.

---

# Detection Chain - Targeted Kerberoasting

```text
5136
 |
 v
servicePrincipalName Changed
 |
 v
4769
 |
 v
Service Ticket Requested
 |
 v
5136
 |
 v
SPN Restored
```

This sequence can be a strong signal when the SPN change is unusual.

---

# Detection Chain - RBCD

```text
5136
 |
 v
msDS-AllowedToActOnBehalfOfOtherIdentity
Modified
 |
 v
4768 / 4769
 |
 v
S4U Activity
 |
 v
4624
 |
 v
Target Authentication
```

---

# Detection Chain - Group Abuse

```text
4728 / 4732 / 4756
        |
        v
Unexpected Member Added
        |
        v
Privileged Authentication
        |
        v
4729 / 4733 / 4757
        |
        v
Member Removed
```

Temporary membership is particularly important to detect.

---

# Detection Chain - Password Reset

```text
4724
 |
 v
Password Reset
 |
 v
Authentication as Target
 |
 v
Privilege Use
```

---

# Detection Chain - DACL Abuse

```text
ACL Change
   |
   v
New Permission
   |
   v
Security-Sensitive Object Modification
   |
   v
Privilege Escalation
```

Directory auditing should focus especially on high-value objects.

---

# Monitor Sensitive Objects

High-value monitoring targets include:

```text
Domain Object
Domain Admins
Enterprise Admins
Administrators
AdminSDHolder
Domain Controllers OU
Tier 0 Servers
Privileged Service Accounts
GPOs
Certificate Authorities
Delegation-Enabled Accounts
```

---

# Baseline ACLs

Maintain known-good ACL baselines for:

```text
Domain Root
Privileged Groups
AdminSDHolder
Tier 0 OUs
Domain Controllers
Critical GPOs
Critical Service Accounts
Certificate Infrastructure
```

Then detect:

```text
New ACE
Removed ACE
Changed Owner
Changed Inheritance
Unexpected Trustee
Unexpected Extended Right
```

---

# Purple Team Exercise

A controlled ACL exercise can use:

```text
Dedicated Test User
       |
       v
Test ACL
       |
       v
Test Object
       |
       v
Benign Security Operation
       |
       v
Blue Team Detection
       |
       v
Cleanup
```

Examples:

```text
Add test user to test group
Temporary test SPN
Temporary RBCD on test computer
Temporary DACL entry on test object
```

Avoid using production Tier 0 objects for routine exercises.

---

# Purple Team Questions

Defenders should determine:

```text
Which principal performed the change?

Which object was modified?

What permission enabled the change?

Was the permission explicit or inherited?

Who granted the permission?

Which attribute changed?

Was ownership changed?

Was the DACL modified?

Did privilege increase?

Was the change temporary?

What authentication followed?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect ACL change
Time to identify source principal
Time to identify target object
Time to identify exact ACE
Time to identify inherited source
Time to detect group membership change
Time to detect sensitive attribute change
Time to reconstruct attack path
Time to containment
Time to restore ACL
```

---

# Hardening

The ACL defensive model is:

```text
Least Privilege
      |
      v
Controlled Delegation
      |
      v
Minimal ACEs
      |
      v
Protected Tier 0
      |
      v
ACL Monitoring
      |
      v
Regular Review
```

---

# Apply Least Privilege

Grant only the permissions required for the operational task.

Avoid:

```text
GenericAll
```

where:

```text
Reset Password
```

is sufficient.

Avoid:

```text
GenericWrite
```

where:

```text
Write one specific property
```

is sufficient.

---

# Prefer Specific Rights

Bad:

```text
Helpdesk
   |
   v
GenericAll
   |
   v
Users OU
```

Better:

```text
Helpdesk
   |
   v
Specific Required Rights
   |
   v
Specific User Scope
```

---

# Review Delegated Administration

Active Directory delegation accumulates over time.

Common causes include:

```text
Old Helpdesk Roles
Migration Projects
Temporary Administrators
Application Deployments
Consultants
Legacy Automation
Organisational Restructuring
```

Review delegated permissions regularly.

---

# Review OU Permissions

OU ACLs are particularly important because inherited permissions may affect large numbers of objects.

For each OU:

```text
Who has permissions?
        |
        v
What rights?
        |
        v
Which child types?
        |
        v
Inherited how far?
        |
        v
Are they still required?
```

---

# Protect Tier 0

Tier 0 includes security principals and systems capable of controlling the identity infrastructure.

Examples include:

```text
Domain Controllers
Domain Admins
Enterprise Admins
Domain Root
AdminSDHolder
PKI Infrastructure
Identity Management Systems
Privileged GPOs
```

Low-tier administrative identities should not have control paths into Tier 0.

---

# Separate Administrative Roles

Avoid using one broad administrative group for unrelated responsibilities.

Prefer:

```text
Helpdesk Password Reset
Server Administration
Workstation Administration
GPO Administration
Identity Administration
PKI Administration
```

with carefully scoped permissions.

---

# Remove Orphaned ACEs

ACLs may contain SIDs that no longer resolve.

Example:

```text
S-1-5-21-...-1437
```

This may represent:

```text
Deleted Account
Old Domain
Migration Artifact
Trust Artifact
```

Investigate before removal.

Do not automatically delete unresolved SIDs.

---

# Review Object Owners

Unexpected ownership should be corrected through controlled administration.

Pay particular attention to:

```text
Privileged Groups
Service Accounts
Computer Objects
GPOs
OUs
AdminSDHolder
Domain Root
```

---

# Monitor WriteDACL

`WriteDACL` should be treated as highly privileged because it can provide a path to grant additional permissions.

Ask:

```text
Who can modify permissions
on this object?
```

not only:

```text
Who currently has full control?
```

---

# Monitor WriteOwner

Ownership-changing rights can create indirect control paths.

Review:

```text
WriteOwner
```

on sensitive objects.

---

# Protect Replication Rights

Directory replication rights should normally be restricted to:

```text
Domain Controllers
Approved Identity Systems
Explicitly Required Administrative Services
```

Unexpected principals with:

```text
GetChanges
GetChangesAll
```

should be investigated.

---

# Group Management Hardening

For privileged groups:

```text
Restrict Membership Modification
Monitor Additions
Monitor Removals
Review Nested Groups
Review Group Owners
Review Delegated Group Management
```

---

# Protect Service Accounts

Service accounts frequently become ACL escalation targets because they may have:

```text
Server Privileges
Delegation
SPNs
Application Access
Database Access
Scheduled Tasks
```

Use:

```text
gMSA
```

where suitable and restrict who can modify service-account attributes.

---

# Incident Response

If ACL abuse is suspected:

```text
Suspicious AD Change
        |
        v
Identify Target
        |
        v
Identify Source Principal
        |
        v
Identify Changed ACE / Attribute
        |
        v
Determine Original Permission
        |
        v
Determine Resulting Privilege
        |
        v
Review Authentication
        |
        v
Contain Compromised Principal
        |
        v
Restore ACL / Attribute
        |
        v
Rotate Credentials if Required
        |
        v
Hunt for Persistence
```

---

# Do Not Remove Evidence Immediately

Before remediation:

```text
Capture:
    Object DN
    Owner
    DACL
    Relevant ACEs
    Changed Attributes
    Event Logs
    Source Principal
    Timestamp
```

Then perform controlled remediation.

---

# Persistence Through ACLs

Attackers may establish persistence by granting themselves or controlled principals access to sensitive objects.

Conceptually:

```text
Compromise
   |
   v
Modify DACL
   |
   v
Add Hidden / Unexpected ACE
   |
   v
Retain Control
```

Therefore incident response should compare current ACLs against known-good baselines.

---

# AdminSDHolder Persistence

Unexpected permissions on:

```text
AdminSDHolder
```

deserve urgent investigation.

A malicious ACE may propagate to protected accounts and groups.

---

# Reporting

Possible finding titles include:

```text
Excessive Active Directory Permissions Enable Privilege Escalation
```

```text
GenericWrite Permission Enables Control of Privileged Account
```

```text
WriteDACL Permission Enables Active Directory Privilege Escalation
```

```text
WriteOwner Permission Enables Control of Privileged Directory Object
```

```text
Excessive Group Permissions Permit Unauthorised Membership Modification
```

```text
Active Directory ACL Misconfiguration Enables Targeted Kerberoasting
```

```text
Computer Object Permissions Enable Resource-Based Constrained Delegation Abuse
```

```text
Directory Replication Rights Expose Domain Credential Material
```

---

# Report the Actual Path

Avoid reporting:

```text
GenericWrite Found
```

Instead:

```text
CORP\alice
   |
   v
WriteProperty
   |
   v
servicePrincipalName
   |
   v
CORP\svc_backup
   |
   v
Targeted Kerberoasting
   |
   v
Potential Control of Backup Service Account
```

This communicates the actual security impact.

---

# Example Finding

```text
Finding:
Active Directory ACL Misconfiguration Enables Privilege Escalation

Affected Principal:
CORP\helpdesk-user

Affected Object:
CORP\svc_backup

Permission:
WriteProperty - servicePrincipalName

Description:
The CORP\helpdesk-user account has permission to modify the
servicePrincipalName attribute of the CORP\svc_backup account.

This permission allows the affected account to assign an SPN to the
target service account. A Kerberos service ticket can subsequently be
requested for the modified account, creating an offline password
guessing opportunity against the service account credential.

The issue represents a targeted Kerberoasting path caused by excessive
Active Directory object permissions.

During controlled validation, the effective ACL was independently
confirmed. No production password was changed and no unnecessary
privileged operations were performed.

Impact:
Successful recovery or compromise of the target service-account
credential could provide the privileges assigned to CORP\svc_backup,
including access to systems and services where that identity is trusted.

Recommendation:
Remove the unnecessary servicePrincipalName write permission from the
affected principal.

Review the target object's complete ACL, determine whether the
permission was explicitly assigned or inherited, review the parent OU
for excessive delegated rights, protect service accounts using strong
managed credentials where possible, and monitor unexpected SPN changes
and Kerberos service-ticket requests.
```

---

# Severity Assessment

Severity should consider the complete chain:

```text
Source Principal
       |
       v
ACL Right
       |
       v
Target Object
       |
       v
Security Primitive
       |
       v
Resulting Identity / Privilege
       |
       v
Affected Systems
```

Questions include:

```text
Is the source already privileged?

Is exploitation authenticated?

Does exploitation require AD modification?

Is the target privileged?

Does the target control Tier 0?

Can the path expose credentials?

Can the path be exploited without user interaction?

Is the permission inherited across many objects?

What is the blast radius?
```

---

# Evidence Checklist

Record:

```text
Source Principal
Source SID
Source Group Membership
Target Object
Target Object Type
Target DN
Target SID
Object Owner
ActiveDirectoryRights
AccessControlType
ObjectAceType
InheritedObjectType
IsInherited
Parent Container
Resulting Attack Primitive
Resulting Privilege
BloodHound Path
Independent ACL Confirmation
Validation Performed
Original State
Final State
Timestamp
```

---

# ACL Assessment Checklist

## Preparation

- [ ] Confirm Active Directory ACL testing is authorised
- [ ] Confirm permitted modification level
- [ ] Confirm password-reset restrictions
- [ ] Confirm group-membership restrictions
- [ ] Confirm delegation-change restrictions
- [ ] Confirm GPO testing restrictions
- [ ] Confirm DCSync restrictions
- [ ] Confirm cleanup requirements
- [ ] Identify test accounts
- [ ] Identify Tier 0 objects

## Enumeration

- [ ] Enumerate domain structure
- [ ] Enumerate users
- [ ] Enumerate groups
- [ ] Enumerate computers
- [ ] Enumerate OUs
- [ ] Enumerate GPOs
- [ ] Enumerate object owners
- [ ] Enumerate DACLs
- [ ] Resolve SIDs
- [ ] Resolve object GUIDs
- [ ] Identify inherited ACEs
- [ ] Identify explicit ACEs

## High-Value Rights

- [ ] Review `GenericAll`
- [ ] Review `GenericWrite`
- [ ] Review `WriteProperty`
- [ ] Review `WriteDACL`
- [ ] Review `WriteOwner`
- [ ] Review `ForceChangePassword`
- [ ] Review `AddMember`
- [ ] Review `AddSelf`
- [ ] Review `AllExtendedRights`
- [ ] Review `WriteSPN`
- [ ] Review key-credential write paths
- [ ] Review RBCD write paths
- [ ] Review replication rights
- [ ] Review GPO rights
- [ ] Review child-object creation rights

## Target Analysis

- [ ] Determine target object type
- [ ] Determine target privilege
- [ ] Review target group membership
- [ ] Review target administrative access
- [ ] Review target delegation
- [ ] Review target SPNs
- [ ] Review target service role
- [ ] Review Tier 0 relationship
- [ ] Determine blast radius

## BloodHound

- [ ] Mark controlled principals
- [ ] Review outbound object control
- [ ] Review inbound control on high-value objects
- [ ] Identify shortest ACL paths
- [ ] Review indirect paths
- [ ] Review group nesting
- [ ] Review inherited control
- [ ] Confirm important edges independently

## Validation

- [ ] Choose minimum-impact validation
- [ ] Capture original state
- [ ] Confirm effective permission
- [ ] Avoid production password resets
- [ ] Avoid unnecessary group changes
- [ ] Avoid unnecessary GPO changes
- [ ] Avoid unnecessary AdminSDHolder changes
- [ ] Avoid unnecessary replication of credentials
- [ ] Use dedicated test objects where possible
- [ ] Stop once impact is proven

## Detection

- [ ] Review 5136
- [ ] Review 4662
- [ ] Review 4670 where applicable
- [ ] Review 4724
- [ ] Review 4728 / 4729
- [ ] Review 4732 / 4733
- [ ] Review 4756 / 4757
- [ ] Review 4738
- [ ] Review 4742
- [ ] Monitor SPN changes
- [ ] Monitor RBCD changes
- [ ] Monitor key-credential changes
- [ ] Monitor privileged ACL changes
- [ ] Monitor replication activity

## Remediation

- [ ] Remove unnecessary ACEs
- [ ] Replace generic rights with specific rights
- [ ] Review OU delegation
- [ ] Review inherited permissions
- [ ] Review object owners
- [ ] Review privileged-group ACLs
- [ ] Review AdminSDHolder
- [ ] Protect replication rights
- [ ] Protect service accounts
- [ ] Protect computer objects
- [ ] Protect GPOs
- [ ] Apply administrative tiering
- [ ] Establish ACL baselines
- [ ] Implement change monitoring

## Cleanup

- [ ] Restore modified attributes
- [ ] Remove temporary group memberships
- [ ] Remove temporary SPNs
- [ ] Remove temporary RBCD entries
- [ ] Remove temporary key credentials
- [ ] Restore modified owners
- [ ] Restore modified DACLs
- [ ] Verify legitimate ACEs remain
- [ ] Verify final object state
- [ ] Secure evidence

---

# ACL Testing Model

The basic security model is:

```text
Active Directory Object
        |
        v
Security Descriptor
        |
        +--> Owner
        |
        +--> DACL
        |     |
        |     +--> ACE
        |     +--> ACE
        |     +--> ACE
        |
        +--> SACL
```

The access model is:

```text
Security Principal
       |
       v
Security Token
       |
       +--> User SID
       |
       +--> Group SIDs
       |
       +--> Other Token Data
       |
       v
AccessCheck
       |
       v
Object DACL
       |
       v
Allow / Deny
```

The attack-path model is:

```text
Controlled Principal
        |
        v
Interesting ACE
        |
        v
Security-Sensitive Object
        |
        v
Security Primitive
        |
        v
Privilege Expansion
```

The `GenericAll` model is:

```text
Principal
   |
   v
GenericAll
   |
   v
Target
   |
   v
Broad Object Control
```

The `GenericWrite` model is:

```text
Principal
   |
   v
GenericWrite
   |
   v
Target Attribute
   |
   +--> SPN
   |
   +--> Key Credential
   |
   +--> Delegation Property
   |
   v
Technique-Specific Impact
```

The `WriteDACL` model is:

```text
Principal
   |
   v
WriteDACL
   |
   v
Target DACL
   |
   v
Grant Additional Right
   |
   v
Control Target
```

The `WriteOwner` model is:

```text
Principal
   |
   v
WriteOwner
   |
   v
Become Owner
   |
   v
Modify DACL
   |
   v
Grant Right
   |
   v
Control Target
```

The targeted Kerberoasting model is:

```text
WriteSPN
   |
   v
User Account
   |
   v
Temporary SPN
   |
   v
Service Ticket
   |
   v
Offline Password Guessing
```

The RBCD model is:

```text
Write Computer Object
        |
        v
RBCD Attribute
        |
        v
Controlled Principal
        |
        v
S4U
        |
        v
Service Impersonation
```

The Shadow Credentials model is:

```text
Write Key Credential
        |
        v
msDS-KeyCredentialLink
        |
        v
Controlled Key
        |
        v
Certificate Authentication
        |
        v
Target Identity
```

The DCSync model is:

```text
Replication Rights
       |
       v
Domain Naming Context
       |
       v
Directory Replication
       |
       v
Credential Material
```

The inheritance model is:

```text
Parent OU
   |
   v
Inherited ACE
   |
   +--> User
   +--> Group
   +--> Computer
   |
   v
Potential Large Blast Radius
```

The detection model is:

```text
ACL / Attribute Change
        |
        v
Directory Audit
        |
        v
Security-Sensitive Operation
        |
        v
Authentication / Privilege Use
        |
        v
Correlation
```

The defensive model is:

```text
Least Privilege
      |
      v
Specific Delegated Rights
      |
      v
Controlled Inheritance
      |
      v
Protected Tier 0
      |
      v
ACL Baseline
      |
      v
Change Monitoring
      |
      v
Periodic Review
```

A mature ACL assessment should answer:

```text
Which principals do we control?
        |
        v
What objects can they control?
        |
        v
What exact ACE provides control?
        |
        v
Is the ACE explicit or inherited?
        |
        v
Which property or extended right?
        |
        v
What object type is affected?
        |
        v
What security operation is possible?
        |
        v
What privilege does the target have?
        |
        v
Can the path reach Tier 0?
        |
        v
Can the condition be proven safely?
        |
        v
Can defenders detect the change?
        |
        v
What is the actual root cause?
```

The most important principle is:

```text
Interesting ACE
      |
      X
Automatically Critical
```

Instead:

```text
Principal
    +
Permission
    +
Target
    +
Security Primitive
    +
Resulting Privilege
    =
Actual Risk
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

BloodHound:

[BloodHound](bloodhound.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[S4U](s4u.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The following topics complement ACL and ACE analysis and can be linked once their dedicated notes are available:

```text
active-directory/groups.md
active-directory/group-policy.md
active-directory/machine-account-quota.md
active-directory/shadow-credentials.md
active-directory/gmsa.md
active-directory/ntds.md
active-directory/dcsync.md
active-directory/ad-cs/index.md
active-directory/trusts/index.md
active-directory/sid-history.md
```

---

# References

## Microsoft Access Control

[Microsoft - Access Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Access Control Lists](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-lists){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Access Control Entries](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-entries){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Security Descriptors](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptors){ target="_blank" rel="noopener noreferrer" }

---

## Active Directory Security Descriptors

[Microsoft - nTSecurityDescriptor](https://learn.microsoft.com/en-us/windows/win32/adschema/a-ntsecuritydescriptor){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Security Descriptor Flags Control](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/3888c2b7-35b9-45b7-afeb-b772aa932dd0){ target="_blank" rel="noopener noreferrer" }

---

## Active Directory Rights

[Microsoft - ActiveDirectoryRights Enum](https://learn.microsoft.com/en-us/dotnet/api/system.directoryservices.activedirectoryrights){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Extended Rights](https://learn.microsoft.com/en-us/windows/win32/adschema/extended-rights){ target="_blank" rel="noopener noreferrer" }

---

## AdminSDHolder

[Microsoft - AdminSDHolder, Protected Groups and SDProp](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-c--protected-accounts-and-groups-in-active-directory){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## PowerView

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

---

## bloodyAD

[bloodyAD](https://github.com/CravateRouge/bloodyAD){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Additional Cloud Roles](https://attack.mitre.org/techniques/T1098/003/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - OS Credential Dumping: DCSync](https://attack.mitre.org/techniques/T1003/006/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Active Directory ACLs define one of the most important security boundaries in the domain.

The basic relationship is:

```text
Principal
   |
   v
ACE
   |
   v
Permission
   |
   v
Object
```

The important question is not merely:

```text
Who is Domain Admin?
```

It is:

```text
Who can control
something that can control
something privileged?
```

For example:

```text
Alice
 |
 v
GenericWrite
 |
 v
svc_backup
 |
 v
Administrative Access
 |
 v
Critical Server
```

or:

```text
Alice
 |
 v
WriteDACL
 |
 v
Privileged Group
 |
 v
Grant Membership Right
 |
 v
Privilege Escalation
```

or:

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
S4U
 |
 v
Privileged Service Access
```

The most important rights to recognise include:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
ForceChangePassword
AddMember
AddSelf
AllExtendedRights
WriteSPN
Replication Rights
```

but their significance depends on:

```text
Target Object Type
        +
Exact Property / Right
        +
Target Privilege
        +
Inheritance
        +
Effective Permissions
```

Therefore:

```text
GenericWrite
```

should never be interpreted without asking:

```text
GenericWrite over what?
```

Likewise:

```text
WriteProperty
```

requires:

```text
Which property?
```

and:

```text
WriteDACL
```

requires:

```text
What useful permission
could be granted?
```

ACL attack paths should therefore be analysed as chains:

```text
Controlled Principal
        |
        v
ACL Permission
        |
        v
Security Primitive
        |
        v
Target Identity / Object
        |
        v
Resulting Privilege
```

BloodHound is particularly effective at identifying these chains:

```text
Raw ACEs
   |
   v
Graph Relationships
   |
   v
Attack Paths
```

but important paths should be independently confirmed using:

```text
Native PowerShell
PowerView
LDAP
Other Directory Tooling
```

before reporting exploitation as proven.

A mature testing strategy follows:

```text
Enumerate
   |
   v
Identify Interesting ACE
   |
   v
Resolve Principal
   |
   v
Resolve Target
   |
   v
Determine Exact Right
   |
   v
Determine Security Primitive
   |
   v
Determine Resulting Privilege
   |
   v
Choose Minimum-Impact Validation
   |
   v
Collect Evidence
   |
   v
Restore State
```

The defensive equivalent is:

```text
Inventory ACLs
      |
      v
Identify Excessive Rights
      |
      v
Reduce Delegation
      |
      v
Protect Tier 0
      |
      v
Monitor Changes
      |
      v
Review Continuously
```

Finally, ACL weaknesses should be reported according to the actual attack path rather than the raw permission alone.

Instead of:

```text
GenericWrite exists
```

report:

```text
Low-Privilege Account
        |
        v
WriteProperty over SPN
        |
        v
Privileged Service Account
        |
        v
Targeted Kerberoasting
        |
        v
Potential Administrative Credential Compromise
```

This provides developers, administrators, defenders, and management with the information needed to understand both the technical root cause and the real security impact.
