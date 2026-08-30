# Active Directory Groups

Active Directory groups are one of the primary mechanisms used to assign permissions, administrative roles, application access, and resource access across a Windows domain.

From a security perspective, group analysis answers a fundamental question:

```text
What privileges does this identity inherit?
```

A user may appear unprivileged when examined directly but inherit substantial access through one or more groups.

```text
User
 |
 v
Group
 |
 v
Nested Group
 |
 v
Privileged Group
 |
 v
Administrative Access
```

For example:

```text
alice
 |
 v
Helpdesk
 |
 v
IT Operations
 |
 v
Server Administrators
 |
 v
Administrative Access to Servers
```

The security relationship is therefore rarely limited to:

```text
User -> Direct Group
```

Instead, Active Directory commonly contains:

```text
User
 |
 +--> Direct Group
 |
 +--> Nested Group
 |
 +--> Domain Local Group
 |
 +--> Global Group
 |
 +--> Universal Group
 |
 +--> Privileged Group
 |
 +--> Local Group on Computer
 |
 +--> Application Role
```

Group enumeration should therefore be part of every Active Directory security assessment.

!!! warning "Authorised testing only"
    Group membership changes can immediately grant administrative or application privileges and may affect production systems. Prefer read-only enumeration and attack-path analysis first. Only add or remove members when explicitly authorised, use dedicated test accounts where possible, record the original membership, and restore all changes after validation.

---

# Why Groups Matter

Groups simplify administration.

Instead of assigning permissions directly to every user:

```text
Alice -> FILE01
Bob   -> FILE01
Carol -> FILE01
Dave  -> FILE01
```

administrators can create:

```text
File Server Users
```

and assign:

```text
Alice
Bob
Carol
Dave
```

to the group.

Then:

```text
File Server Users
        |
        v
      FILE01
```

This is operationally efficient.

However, it also means group membership becomes part of the security boundary.

---

# Group Security Model

The basic model is:

```text
Security Principal
       |
       v
Group Membership
       |
       v
Security Token
       |
       v
Permissions
       |
       v
Resource
```

When a user authenticates, Windows constructs an access token containing security identifiers associated with the user and applicable groups.

Conceptually:

```text
Alice
 |
 v
Authentication
 |
 v
Access Token
 |
 +--> Alice SID
 |
 +--> Domain Users SID
 |
 +--> Helpdesk SID
 |
 +--> Server Admins SID
 |
 v
AccessCheck
```

Permissions granted to those group SIDs may therefore become available to Alice.

---

# Security Groups vs Distribution Groups

Active Directory supports:

```text
Security Groups
Distribution Groups
```

The distinction is important.

---

# Security Groups

Security groups can be used to assign permissions.

Examples:

```text
Domain Admins
Server Admins
File Server Users
SQL Administrators
Helpdesk
Backup Operators
```

Conceptually:

```text
Security Group
      |
      v
ACL / Permission
      |
      v
Resource
```

---

# Distribution Groups

Distribution groups are primarily intended for email distribution.

Conceptually:

```text
Distribution Group
       |
       v
Email Distribution
```

They are not normally used as security principals for assigning access permissions.

---

# Enumerate Group Category

PowerShell:

```powershell
Get-ADGroup \
    -Filter * \
    -Properties GroupCategory |
    Select-Object \
        Name,
        GroupCategory
```

Example output:

```text
Name                 GroupCategory
----                 -------------
Domain Admins        Security
Helpdesk             Security
All Employees        Distribution
```

---

# Group Scope

Active Directory security groups have three principal scopes:

```text
Domain Local
Global
Universal
```

Understanding group scope is important when analysing:

```text
Membership
Trusts
Cross-Domain Access
Resource Permissions
Administrative Delegation
```

---

# Global Groups

Global groups are commonly used to collect users and computers from the same domain according to role.

Example:

```text
CORP\Domain Helpdesk
```

Conceptually:

```text
Users in CORP
     |
     v
Global Group
```

A global group can then be granted permissions to resources.

---

# Domain Local Groups

Domain local groups are commonly used to assign permissions to resources within the domain.

Conceptually:

```text
Global Groups
     |
     v
Domain Local Group
     |
     v
Resource Permission
```

Example:

```text
CORP\File Server Users
        |
        v
FILE01 Share
```

---

# Universal Groups

Universal groups can contain principals from multiple domains in the forest, subject to Active Directory membership rules.

They are useful in multi-domain environments.

Conceptually:

```text
Domain A Users
       |
       +------+
              |
Domain B Users|
       |      |
       +------+
              |
              v
       Universal Group
              |
              v
          Resource
```

Universal groups are particularly important when assessing:

```text
Multi-Domain Forests
Cross-Domain Privileges
Trust Relationships
```

---

# AGDLP

A common Microsoft group-design model is:

```text
Accounts
   |
   v
Global Groups
   |
   v
Domain Local Groups
   |
   v
Permissions
```

This is commonly abbreviated:

```text
AGDLP
```

or:

```text
A -> G -> DL -> P
```

Example:

```text
Alice
 |
 v
GG-Finance
 |
 v
DL-Finance-Share-RW
 |
 v
FILE01 Finance Share
```

---

# AGUDLP

In multi-domain environments, Universal groups may be added:

```text
Accounts
   |
   v
Global Groups
   |
   v
Universal Groups
   |
   v
Domain Local Groups
   |
   v
Permissions
```

This is commonly described as:

```text
AGUDLP
```

---

# Why Nested Groups Matter

Suppose Alice is only directly a member of:

```text
Helpdesk
```

However:

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
Server Admins
```

If:

```text
Server Admins
```

has administrative access to servers, Alice may indirectly inherit that capability.

Therefore:

```text
Direct Membership
```

is insufficient for complete privilege analysis.

---

# Direct vs Recursive Membership

Direct membership:

```text
Alice
 |
 v
Helpdesk
```

Recursive membership:

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
Server Admins
```

Always analyse both.

---

# Enumerate Groups with PowerShell

Using the Active Directory PowerShell module:

```powershell
Get-ADGroup -Filter *
```

Useful properties:

```powershell
Get-ADGroup \
    -Filter * \
    -Properties Description,GroupCategory,GroupScope,ManagedBy |
    Select-Object \
        Name,
        SamAccountName,
        GroupCategory,
        GroupScope,
        ManagedBy,
        Description
```

---

# Enumerate One Group

```powershell
Get-ADGroup \
    -Identity 'Domain Admins' \
    -Properties *
```

Useful fields include:

```text
DistinguishedName
GroupCategory
GroupScope
ManagedBy
Member
ObjectGUID
ObjectSID
SamAccountName
```

---

# Enumerate Group Members

```powershell
Get-ADGroupMember \
    -Identity 'Domain Admins'
```

Example:

```text
distinguishedName : CN=Administrator,CN=Users,DC=corp,DC=example
name              : Administrator
objectClass       : user
SamAccountName    : Administrator
```

---

# Recursive Group Membership

Use:

```powershell
Get-ADGroupMember \
    -Identity 'Domain Admins' \
    -Recursive
```

This expands nested group membership.

Compare:

```text
Direct Members
      |
      v
Nested Groups
      |
      v
Recursive Members
```

---

# Enumerate a User's Direct Groups

```powershell
Get-ADPrincipalGroupMembership \
    -Identity 'alice'
```

Readable output:

```powershell
Get-ADPrincipalGroupMembership \
    -Identity 'alice' |
    Select-Object \
        Name,
        GroupScope,
        GroupCategory
```

---

# memberOf Attribute

The user's:

```text
memberOf
```

attribute contains direct group memberships represented by distinguished names.

Example:

```powershell
Get-ADUser \
    -Identity 'alice' \
    -Properties memberOf |
    Select-Object \
        -ExpandProperty memberOf
```

Example:

```text
CN=Helpdesk,OU=Groups,DC=corp,DC=example
CN=VPN Users,OU=Groups,DC=corp,DC=example
```

---

# memberOf Is Not the Complete Effective Membership

Do not treat:

```text
memberOf
```

as a complete list of all effective groups.

Important reasons include:

```text
Nested Groups
Primary Group
Cross-Domain Membership
Token Construction
SIDHistory
```

Use recursive and token-aware analysis where necessary.

---

# LDAP Matching Rule in Chain

Active Directory supports recursive group membership queries using the LDAP matching rule:

```text
1.2.840.113556.1.4.1941
```

This is commonly known as:

```text
LDAP_MATCHING_RULE_IN_CHAIN
```

Example:

```powershell
Get-ADUser \
    -LDAPFilter '(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=corp,DC=example)'
```

This can identify users recursively associated with the specified group.

---

# Recursive Membership with LDAP

Conceptually:

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
Domain Admins
```

A normal:

```text
memberOf=Domain Admins
```

filter would not necessarily identify the indirect relationship.

The matching-rule-in-chain query follows the nested membership chain.

---

# Enumerate with ldapsearch

Basic group enumeration:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(objectClass=group)' \
    sAMAccountName \
    cn \
    groupType \
    member \
    managedBy
```

---

# Enumerate a Specific Group with ldapsearch

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectClass=group)(sAMAccountName=Domain Admins))' \
    distinguishedName \
    member \
    managedBy \
    groupType
```

---

# LDAP Group Attributes

Useful attributes include:

```text
cn
sAMAccountName
distinguishedName
member
memberOf
managedBy
groupType
objectSid
adminCount
description
whenCreated
whenChanged
```

---

# groupType

The:

```text
groupType
```

attribute stores group scope and security-group information as flags.

Most assessments do not require manually decoding every numeric value because tools such as PowerShell provide readable:

```text
GroupScope
GroupCategory
```

fields.

However, raw LDAP output may expose the integer representation.

---

# Net Commands

Built-in Windows commands can provide quick enumeration.

Domain groups:

```cmd
net group /domain
```

Members of Domain Admins:

```cmd
net group "Domain Admins" /domain
```

Specific user:

```cmd
net user alice /domain
```

These commands remain useful where the Active Directory PowerShell module is unavailable.

---

# whoami

For the current session:

```cmd
whoami
```

Groups in the current token:

```cmd
whoami /groups
```

This is particularly useful because it shows security groups associated with the current access token.

---

# Current Token vs Directory Membership

Remember:

```text
Directory Membership Changed
        |
        X
Current Token Automatically Updated
```

A newly added group may not appear in an already existing logon token.

A new authentication session may be required.

This matters during both testing and troubleshooting.

---

# PowerView Group Enumeration

PowerView can enumerate domain groups.

```powershell
Get-DomainGroup
```

Specific group:

```powershell
Get-DomainGroup \
    -Identity 'Domain Admins'
```

---

# PowerView Group Members

```powershell
Get-DomainGroupMember \
    -Identity 'Domain Admins'
```

Recursive behaviour and available parameters can vary by PowerView version.

Check:

```powershell
Get-Help Get-DomainGroupMember -Full
```

---

# PowerView User Membership

```powershell
Get-DomainGroup \
    -MemberIdentity 'alice'
```

Depending on the PowerView version, this can assist with identifying groups associated with a principal.

Always verify the loaded version's help before relying on exact parameters.

---

# BloodHound

BloodHound is extremely useful for analysing group membership because it represents membership as graph relationships.

Example:

```text
alice
 |
 v
MemberOf
 |
 v
Helpdesk
 |
 v
MemberOf
 |
 v
Server Admins
```

The graph can then continue:

```text
Server Admins
 |
 v
AdminTo
 |
 v
SERVER01
```

The complete attack path becomes:

```text
alice
 |
 v
Helpdesk
 |
 v
Server Admins
 |
 v
SERVER01
```

---

# Group Membership in BloodHound

BloodHound commonly represents group relationships using:

```text
MemberOf
```

This relationship may connect:

```text
User -> Group
Computer -> Group
Group -> Group
```

depending on the directory configuration.

---

# BloodHound Group Questions

Useful questions include:

```text
What groups is this user a member of?

What privileged groups are reachable recursively?

Who can modify this group?

Which users can reach Domain Admins?

Which groups provide local administrator rights?

Which groups control GPOs?

Which groups have DCSync rights?

Which groups control service accounts?

Which groups contain computers?
```

---

# Group Membership Is Only One Edge Type

Do not analyse:

```text
MemberOf
```

in isolation.

A group may also participate in relationships such as:

```text
AdminTo
GenericAll
GenericWrite
WriteDacl
WriteOwner
AddMember
Owns
GPO Control
DCSync
Delegation
```

The security impact comes from the complete graph.

---

# Privileged Groups

Some groups deserve immediate attention during Active Directory assessments.

Examples include:

```text
Domain Admins
Enterprise Admins
Schema Admins
Administrators
Account Operators
Backup Operators
Server Operators
Print Operators
DnsAdmins
Group Policy Creator Owners
Protected Users
```

The exact security impact depends on the domain configuration, Windows version, assigned privileges, and resource ACLs.

---

# Domain Admins

`Domain Admins` is one of the most important privileged groups in a domain.

Conceptually:

```text
Domain Admins
      |
      v
Broad Domain Administrative Control
```

Members commonly receive administrative control across domain systems through default and organisational configuration.

Any attack path reaching:

```text
Domain Admins
```

should receive immediate attention.

---

# Enterprise Admins

`Enterprise Admins` exists in the forest root domain.

Conceptually:

```text
Enterprise Admins
        |
        v
Forest-Wide Administrative Capability
```

This group is especially important in:

```text
Multi-Domain Forests
```

A compromise may affect more than one domain.

---

# Schema Admins

`Schema Admins` controls Active Directory schema modifications.

Conceptually:

```text
Schema Admins
      |
      v
AD Schema
```

Schema changes can have forest-wide consequences.

Membership should normally be tightly controlled and often temporary when legitimately required.

---

# Builtin Administrators

The domain's built-in:

```text
Administrators
```

group is highly privileged.

Do not confuse:

```text
BUILTIN\Administrators
```

with:

```text
Domain Admins
```

although default memberships and resulting privileges can overlap significantly.

---

# Account Operators

`Account Operators` historically provides delegated account-management capabilities over many non-protected users and groups.

The exact effective rights should be validated rather than inferred solely from the group name.

Investigate:

```text
Which accounts can they manage?

Which groups can they modify?

Are protected objects excluded?

Can managed accounts lead to higher privilege?
```

---

# Server Operators

`Server Operators` can have significant privileges on domain controllers under default configurations.

This group should be treated as highly sensitive.

Review actual assigned privileges and operational use.

---

# Backup Operators

`Backup Operators` is security-sensitive because backup-related privileges can bypass normal file ACL checks for legitimate backup and restore operations.

Conceptually:

```text
Backup Privilege
      |
      v
Read Protected Files
```

or:

```text
Restore Privilege
      |
      v
Write Protected Files
```

The practical impact depends on where the membership is effective.

---

# Print Operators

`Print Operators` has historically received significant privileges on domain controllers related to printer management.

Modern security configuration and service state can materially affect practical impact.

Do not assume exploitation solely from membership.

---

# DnsAdmins

`DnsAdmins` is an important group where Active Directory-integrated DNS is used.

Members can have substantial DNS administration capability.

Because DNS commonly runs on domain controllers, the group deserves careful review.

However:

```text
DnsAdmins Membership
```

should not automatically be reported as:

```text
Domain Admin
```

without demonstrating the relevant configuration and security impact.

---

# Group Policy Creator Owners

`Group Policy Creator Owners` can create Group Policy Objects.

This does not automatically mean the principal can:

```text
Link any GPO anywhere
```

or:

```text
Modify every existing GPO
```

Analyse:

```text
GPO Creation
GPO ACL
OU ACL
GPLink Rights
Existing GPO Control
```

separately.

---

# Protected Users

`Protected Users` is primarily a defensive group.

Members receive additional authentication protections designed to reduce credential exposure and legacy authentication risks.

This group should not be treated as an administrative group merely because it is security-sensitive.

---

# Domain Controllers

Computer accounts for domain controllers are members of:

```text
Domain Controllers
```

and other security contexts relevant to directory replication and domain operation.

Control of a domain-controller computer account is fundamentally different from control of an ordinary workstation account.

---

# Domain Computers

Computer accounts commonly belong to:

```text
Domain Computers
```

This can matter where resources grant permissions broadly to:

```text
Domain Computers
```

rather than individual systems.

---

# Domain Users

Most domain user accounts use:

```text
Domain Users
```

as their primary group by default.

This means permissions granted to:

```text
Domain Users
```

can have a very broad blast radius.

---

# Authenticated Users

`Authenticated Users` is broader than:

```text
Domain Users
```

and should be analysed carefully when found in ACLs.

Conceptually:

```text
Authenticated Identity
        |
        v
Authenticated Users
        |
        v
Permission
```

Broad permissions granted to this principal may expose resources to many authenticated security principals.

---

# Everyone

The:

```text
Everyone
```

security principal can represent a very broad scope.

Its exact token and anonymous-access implications depend on Windows version and configuration.

Do not assume:

```text
Everyone
 =
Unauthenticated Internet User
```

Instead determine the actual authentication and access context.

---

# Local Groups

Domain group analysis should also include local groups on member systems.

For example:

```text
CORP\Server Admins
        |
        v
SERVER01\Administrators
```

This may provide:

```text
Local Administrator on SERVER01
```

without providing domain-wide administrative privilege.

---

# Enumerate Local Administrators

On a Windows system:

```powershell
Get-LocalGroupMember \
    -Group 'Administrators'
```

Older environments may use:

```cmd
net localgroup Administrators
```

---

# Remote Local Group Enumeration

During authorised assessments, tools such as NetExec may help determine whether a supplied account has administrative access to remote systems.

For detailed NetExec usage:

[NetExec](netexec.md)

---

# Group Policy and Local Groups

Group Policy can manage local group membership using mechanisms such as:

```text
Restricted Groups
Group Policy Preferences
```

This means:

```text
Local Administrators
```

may be centrally controlled through Active Directory.

When unexpected local administrators are found, investigate the applicable GPOs.

---

# Group Membership and ACLs

Groups often receive rights through Active Directory ACLs.

Example:

```text
Helpdesk
 |
 v
ForceChangePassword
 |
 v
Users OU
```

Every member of:

```text
Helpdesk
```

may potentially inherit that delegated capability according to the effective ACL.

Therefore group analysis and ACL analysis should be performed together.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# Who Can Modify the Group?

For every privileged group, ask:

```text
Who can change its membership?
```

Potential control paths include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
AddMember
Self
Ownership
Inherited ACE
```

A low-privilege user who can modify a privileged group may effectively possess a privilege-escalation path.

---

# Group Control Model

```text
Alice
 |
 v
AddMember
 |
 v
Server Admins
 |
 v
Administrative Access
```

or:

```text
Alice
 |
 v
WriteDACL
 |
 v
Server Admins
 |
 v
Grant AddMember
 |
 v
Add Controlled Account
 |
 v
Administrative Access
```

---

# Enumerate Group ACL

Native PowerShell:

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

# Group Owner

Check:

```powershell
(Get-Acl "AD:\$($group.DistinguishedName)").Owner
```

Unexpected ownership of privileged groups should be investigated.

---

# managedBy

Groups may have a:

```text
managedBy
```

attribute.

Enumerate:

```powershell
Get-ADGroup \
    -Filter * \
    -Properties ManagedBy |
    Where-Object {
        $_.ManagedBy
    } |
    Select-Object \
        Name,
        ManagedBy
```

However:

```text
managedBy
```

does not by itself prove that the listed manager can modify membership.

The ACL remains authoritative.

---

# Manager Can Update Membership

Active Directory administration tools can configure a group so that the manager is permitted to update membership.

This is implemented through permissions rather than the `managedBy` attribute alone.

Therefore test:

```text
managedBy
      |
      v
Check DACL
      |
      v
Membership Write Right?
```

---

# Group Membership Attack Path

A common path is:

```text
Compromised User
      |
      v
Can Modify Group
      |
      v
Privileged Group
      |
      v
Administrative Capability
```

This is one of the simplest ACL-driven Active Directory privilege-escalation paths.

---

# Nested Group Attack Path

A less obvious path is:

```text
Alice
 |
 v
Can Modify
 |
 v
Application Support
 |
 v
MemberOf
 |
 v
IT Operations
 |
 v
MemberOf
 |
 v
Server Admins
```

The first group may not appear privileged by name.

The nested relationship creates the actual impact.

---

# Group Names Can Be Misleading

Do not determine privilege from names alone.

For example:

```text
Printer Support
Development
Application Team
Legacy Migration
Desktop Support
```

may possess substantial permissions.

Conversely:

```text
Security Admins
```

may only provide access to a specific application.

Always determine:

```text
What permissions does the group actually provide?
```

---

# Description Attribute

Group descriptions can provide useful context.

Enumerate:

```powershell
Get-ADGroup \
    -Filter * \
    -Properties Description |
    Select-Object \
        Name,
        Description
```

Descriptions may reveal:

```text
Business Purpose
Managed Systems
Application Name
Administrative Role
Legacy Function
```

Treat descriptions as hints, not proof.

---

# Empty Groups

Empty groups may still matter.

An empty group can have:

```text
Powerful ACL Rights
Local Administrator Rights
Application Permissions
GPO Permissions
```

If a low-privilege principal can modify the group, the empty state does not eliminate the attack path.

Example:

```text
Alice
 |
 v
AddMember
 |
 v
Empty Privileged Group
 |
 v
AdminTo SERVER01
```

---

# Disabled Users in Groups

A privileged group may contain disabled users.

Enumerate membership and account status separately.

Example:

```powershell
Get-ADGroupMember \
    -Identity 'Server Admins' \
    -Recursive |
    ForEach-Object {
        if ($_.objectClass -eq 'user') {
            Get-ADUser \
                -Identity $_.DistinguishedName \
                -Properties Enabled
        }
    } |
    Select-Object \
        SamAccountName,
        Enabled
```

Disabled membership may represent:

```text
Legacy Configuration
Dormant Privilege
Emergency Account
Poor Cleanup
```

---

# Stale Group Membership

Review privileged memberships for:

```text
Former Employees
Role Changes
Temporary Projects
Old Service Accounts
Disabled Accounts
Migration Accounts
Vendor Accounts
```

Group membership frequently accumulates over time.

---

# Service Accounts in Groups

Service accounts may be members of privileged groups.

Example:

```text
svc_backup
 |
 v
Backup Operators
```

or:

```text
svc_deploy
 |
 v
Server Admins
```

This can increase the impact of:

```text
Kerberoasting
Password Reuse
Credential Exposure
DCSync
Application Compromise
```

---

# Kerberoastable Privileged Group Members

A useful assessment question is:

```text
Which privileged users have SPNs?
```

PowerShell:

```powershell
Get-ADUser \
    -LDAPFilter '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' \
    -Properties ServicePrincipalName,MemberOf |
    Select-Object \
        SamAccountName,
        ServicePrincipalName,
        MemberOf
```

Then analyse recursive privileged memberships.

For detailed Kerberoasting:

[Kerberoasting](kerberoasting.md)

---

# Password-Not-Required Group Members

Look for unusual account settings among privileged identities.

Example:

```powershell
Get-ADUser \
    -Filter * \
    -Properties PasswordNotRequired |
    Where-Object {
        $_.PasswordNotRequired
    } |
    Select-Object \
        SamAccountName,
        Enabled,
        PasswordNotRequired
```

Configuration alone does not prove the account has a blank password.

It indicates that the directory does not require a password under that account flag.

---

# Password-Never-Expires Group Members

```powershell
Get-ADUser \
    -Filter * \
    -Properties PasswordNeverExpires |
    Where-Object {
        $_.PasswordNeverExpires
    } |
    Select-Object \
        SamAccountName,
        Enabled,
        PasswordNeverExpires
```

Prioritise privileged and service accounts for review.

---

# AS-REP Roastable Group Members

Identify accounts with:

```text
Do not require Kerberos preauthentication
```

and determine whether they belong to privileged groups.

For detailed enumeration:

[AS-REP Roasting](asrep-roasting.md)

---

# Group Membership and Password Spraying

Group membership can help prioritise accounts during an authorised password-security assessment.

However, do not create an aggressive spray list consisting only of privileged users.

The testing methodology should still respect:

```text
Lockout Policy
Scope
Rate Limits
Account Sensitivity
Operational Risk
```

See:

[Password Spraying](password-spraying.md)

---

# Primary Group

Active Directory users and computers have:

```text
primaryGroupID
```

The primary group relationship is not represented in exactly the same way as ordinary `memberOf` relationships.

For most users, the default primary group is:

```text
Domain Users
```

---

# Enumerate primaryGroupID

```powershell
Get-ADUser \
    -Identity 'alice' \
    -Properties primaryGroupID |
    Select-Object \
        SamAccountName,
        primaryGroupID
```

Do not rely only on:

```text
memberOf
```

when performing precise token or membership analysis.

---

# SIDHistory and Groups

`sIDHistory` can cause a principal to receive access associated with historical SIDs.

Conceptually:

```text
Current User SID
      |
      +
Historical SID
      |
      v
Access Token
      |
      v
Permissions
```

This becomes especially important in:

```text
Domain Migrations
Forest Migrations
Trust Relationships
Legacy Environments
```

A dedicated SID History page should cover this in detail.

---

# Foreign Security Principals

Cross-domain and cross-forest group memberships may be represented through:

```text
ForeignSecurityPrincipals
```

in Active Directory.

Example DN:

```text
CN=S-1-5-21-...,CN=ForeignSecurityPrincipals,DC=corp,DC=example
```

These objects represent security principals originating outside the local domain.

---

# Foreign Group Membership

A trust-related path might be:

```text
FOREST-A\Alice
      |
      v
FOREST-B\Domain Local Group
      |
      v
Resource in FOREST-B
```

This is why group analysis becomes essential when assessing Active Directory trusts.

---

# Cross-Domain Group Analysis

For multi-domain forests, investigate:

```text
Universal Groups
Domain Local Groups
Foreign Security Principals
Enterprise Admins
Nested Groups
SIDHistory
Trust Direction
Trust Transitivity
```

Group analysis should eventually be combined with dedicated trust analysis.

---

# TokenGroups

Active Directory exposes constructed attributes such as:

```text
tokenGroups
```

that can assist with determining security groups relevant to a principal's authorization context.

This can be useful where direct `memberOf` enumeration does not adequately represent effective group membership.

Specialised directory tooling usually handles this more conveniently than manually decoding raw LDAP values.

---

# AdminSDHolder and Groups

Certain privileged groups are protected by:

```text
AdminSDHolder
```

and:

```text
SDProp
```

This affects their ACL inheritance and protection model.

Conceptually:

```text
AdminSDHolder
      |
      v
Security Descriptor
      |
      v
Protected Groups
      |
      v
Protected Members
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# adminCount

Protected users and groups may have:

```text
adminCount=1
```

Enumerate groups:

```powershell
Get-ADGroup \
    -LDAPFilter '(adminCount=1)' \
    -Properties adminCount |
    Select-Object \
        Name,
        GroupScope,
        adminCount
```

Remember:

```text
adminCount=1
```

can remain after an account is removed from a protected group.

It is therefore useful context rather than definitive proof of current privilege.

---

# Group Membership Changes

Where authorised, PowerShell can modify group membership.

Add:

```powershell
Add-ADGroupMember \
    -Identity '<GROUP>' \
    -Members '<TEST_USER>'
```

Verify:

```powershell
Get-ADGroupMember \
    -Identity '<GROUP>'
```

Remove:

```powershell
Remove-ADGroupMember \
    -Identity '<GROUP>' \
    -Members '<TEST_USER>' \
    -Confirm:$false
```

Only perform these operations against approved groups and accounts.

---

# Minimum-Impact Membership Validation

A safe workflow is:

```text
Confirm Permission
       |
       v
Record Original Membership
       |
       v
Use Dedicated Test Account
       |
       v
Add Once
       |
       v
Verify Membership
       |
       v
Remove Immediately
       |
       v
Verify Original State
```

Do not leave temporary privileged membership in place.

---

# New Authentication Token

After membership changes:

```text
Existing Session
      |
      X
Automatically Contains New Group
```

A fresh authentication context may be required.

For validation, distinguish:

```text
Directory Membership Successfully Changed
```

from:

```text
New Privilege Successfully Exercised
```

The first may already prove the ACL weakness.

---

# Do Not Over-Test

Suppose:

```text
Alice
 |
 v
AddMember
 |
 v
Server Admins
```

and the group is already confirmed to provide administrator access to:

```text
SERVER01
```

It may be unnecessary to:

```text
Add Alice
   |
   v
Log into SERVER01
   |
   v
Execute Commands
```

when:

```text
ACL Evidence
     +
Membership Evidence
     +
Existing Group Privilege Evidence
```

already proves the attack path.

---

# Group Membership and Lateral Movement

Groups often define lateral movement opportunities.

Examples:

```text
Server Admins
Desktop Admins
SQL Admins
Backup Admins
Remote Management Users
RDP Users
```

The model is:

```text
User
 |
 v
Group
 |
 v
Remote Access Right
 |
 v
System
```

---

# Remote Desktop Users

Membership in:

```text
Remote Desktop Users
```

may provide RDP logon capability where other policy conditions permit it.

It does not automatically provide:

```text
Local Administrator
```

---

# Remote Management Users

Membership in:

```text
Remote Management Users
```

may be relevant to WinRM access.

Actual remote management access also depends on endpoint configuration and authorization.

---

# Local Administrators

A domain group placed into a remote computer's local:

```text
Administrators
```

group may create an administrative lateral-movement path.

Example:

```text
CORP\Server Admins
        |
        v
SERVER01\Administrators
        |
        v
Local Administrator
```

---

# NetExec and Group Context

NetExec can help evaluate remote administrative access using authorised credentials.

For example, an assessment may first identify:

```text
Alice
 |
 v
Server Admins
```

then determine:

```text
Which systems trust Server Admins?
```

For detailed commands and current syntax:

[NetExec](netexec.md)

---

# Groups and DCSync

Replication rights may be assigned to groups.

Example:

```text
Identity Management
        |
        +--> GetChanges
        |
        +--> GetChangesAll
        |
        v
Domain
```

Any member of the group may inherit the directory replication capability.

Therefore, when DCSync rights are identified, resolve:

```text
Direct Trustee
      |
      v
Group?
      |
      v
Recursive Members
```

---

# Groups and Delegation

Delegation-enabled accounts may be controlled indirectly through groups.

Example:

```text
Alice
 |
 v
Helpdesk
 |
 v
GenericAll
 |
 v
svc_web
 |
 v
Constrained Delegation
 |
 v
SERVER01
```

The group is part of the attack path even though the final technique is Kerberos delegation.

---

# Groups and RBCD

Similarly:

```text
Alice
 |
 v
Computer Management
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
```

Group membership can therefore expose indirect delegation paths.

---

# Groups and GPOs

Groups may have rights to:

```text
Create GPO
Modify GPO
Link GPO
Edit GPO Security
```

A group that appears unrelated to server administration may nevertheless control a GPO applied to privileged systems.

Always connect:

```text
Group
 |
 v
GPO Permission
 |
 v
GPO
 |
 v
Linked OU
 |
 v
Affected Systems
```

---

# Groups and AD CS

Active Directory Certificate Services can use groups for:

```text
Certificate Template Enrollment
Certificate Template ACLs
CA Administration
Enrollment Agent Restrictions
```

A seemingly ordinary group may therefore participate in an AD CS attack path.

Dedicated AD CS notes should analyse these relationships separately.

---

# Groups and Shares

File-share access frequently depends on domain groups.

Example:

```text
Finance Users
      |
      v
Finance Share
```

Review both:

```text
Share Permissions
```

and:

```text
NTFS Permissions
```

Effective access depends on the combination.

---

# Groups and Applications

Applications commonly map Active Directory groups to application roles.

Example:

```text
CORP\ERP-Admins
      |
      v
ERP Administrator
```

This privilege may not appear in native Active Directory administrative relationships.

Application-specific groups should therefore not be ignored.

---

# Groups and SQL Server

SQL Server environments may use Active Directory groups for:

```text
SQL Login
Database Role
sysadmin
Application Access
```

Example:

```text
CORP\SQL-Admins
      |
      v
SQL Server Login
      |
      v
sysadmin
```

The privilege exists outside normal AD group naming conventions.

---

# Groups and Azure / Hybrid Environments

Hybrid identity environments may synchronize groups between Active Directory and cloud identity systems.

This can create relationships involving:

```text
On-Prem AD Group
      |
      v
Synchronization
      |
      v
Cloud Group / Role Assignment
```

Do not assume that changing an on-premises group has only on-premises impact.

Hybrid identity should be assessed separately according to scope.

---

# Group Membership Enumeration Workflow

A practical workflow is:

```text
Enumerate All Groups
       |
       v
Identify Privileged Groups
       |
       v
Enumerate Direct Members
       |
       v
Expand Nested Membership
       |
       v
Identify Group Controllers
       |
       v
Map Resource Permissions
       |
       v
Identify Attack Paths
       |
       v
Prioritise High-Impact Paths
```

---

# Prioritising Groups

Start with:

```text
Tier 0 Groups
     |
     v
Server Administration Groups
     |
     v
Workstation Administration Groups
     |
     v
GPO Management Groups
     |
     v
Identity Management Groups
     |
     v
Backup Groups
     |
     v
Application Admin Groups
     |
     v
Remote Access Groups
```

Then expand into custom groups.

---

# Interesting Group Names

Names can help with initial triage.

Search for terms such as:

```text
admin
administrator
server
backup
helpdesk
support
sql
database
exchange
dns
gpo
policy
deploy
deployment
remote
rdp
winrm
security
identity
certificate
pki
azure
cloud
service
operator
```

Example:

```powershell
Get-ADGroup \
    -Filter * |
    Where-Object {
        $_.Name -match 'admin|server|backup|helpdesk|sql|gpo|deploy|remote|pki|identity'
    } |
    Select-Object Name
```

This is only triage.

Group names do not prove privilege.

---

# Find Large Groups

Large groups can create significant blast radius.

```powershell
Get-ADGroup \
    -Filter * |
    ForEach-Object {
        $group = $_
        $count = @(
            Get-ADGroupMember \
                -Identity $group \
                -ErrorAction SilentlyContinue
        ).Count

        [PSCustomObject]@{
            Group = $group.Name
            Members = $count
        }
    } |
    Sort-Object Members -Descending
```

Large membership is not automatically a vulnerability.

It is useful for prioritising broad access relationships.

---

# Find Empty Groups

```powershell
Get-ADGroup \
    -Filter * |
    ForEach-Object {
        $members = @(
            Get-ADGroupMember \
                -Identity $_ \
                -ErrorAction SilentlyContinue
        )

        if ($members.Count -eq 0) {
            $_
        }
    } |
    Select-Object Name
```

Then determine whether those groups still hold privileges.

---

# Find Groups with Managers

```powershell
Get-ADGroup \
    -Filter * \
    -Properties ManagedBy |
    Where-Object {
        $_.ManagedBy
    } |
    Select-Object \
        Name,
        ManagedBy
```

Again, verify the ACL before assuming the manager can alter membership.

---

# Find Groups with adminCount

```powershell
Get-ADGroup \
    -LDAPFilter '(adminCount=1)' \
    -Properties adminCount |
    Select-Object \
        Name,
        GroupScope,
        adminCount
```

This can help identify historically or currently protected groups.

---

# Group Membership Review Table

A useful assessment table is:

```text
Group
 |
 +--> Scope
 |
 +--> Category
 |
 +--> Direct Members
 |
 +--> Recursive Members
 |
 +--> Owner
 |
 +--> Manager
 |
 +--> Who Can Modify?
 |
 +--> Resource Access
 |
 +--> Tier
 |
 +--> Business Owner
```

Example:

```text
Group:
CORP\Server Admins

Scope:
Global

Direct Members:
4

Recursive Members:
7

Owner:
CORP\Domain Admins

ManagedBy:
CORP\IT Operations

Can Modify:
CORP\Identity Admins

Provides:
Local administrator access to production servers

Tier:
Tier 1
```

---

# Detection

Group security monitoring should focus on:

```text
Membership Additions
Membership Removals
Group Creation
Group Deletion
Group Changes
Privileged Group Changes
Group ACL Changes
Unexpected Administrative Logons
```

---

# Event 4727

Event:

```text
4727
```

records creation of a security-enabled global group.

---

# Event 4728

Event:

```text
4728
```

records a member being added to a security-enabled global group.

This is particularly important for groups such as:

```text
Domain Admins
Custom Administrative Groups
Server Administration Groups
```

---

# Event 4729

Event:

```text
4729
```

records a member being removed from a security-enabled global group.

Temporary membership abuse may therefore appear as:

```text
4728
 |
 v
Privilege Used
 |
 v
4729
```

---

# Event 4730

Event:

```text
4730
```

records deletion of a security-enabled global group.

---

# Event 4731

Event:

```text
4731
```

records creation of a security-enabled local group.

---

# Event 4732

Event:

```text
4732
```

records a member being added to a security-enabled local group.

---

# Event 4733

Event:

```text
4733
```

records a member being removed from a security-enabled local group.

---

# Event 4734

Event:

```text
4734
```

records deletion of a security-enabled local group.

---

# Event 4735

Event:

```text
4735
```

records changes to a security-enabled local group.

---

# Event 4737

Event:

```text
4737
```

records changes to a security-enabled global group.

---

# Event 4754

Event:

```text
4754
```

records creation of a security-enabled universal group.

---

# Event 4755

Event:

```text
4755
```

records changes to a security-enabled universal group.

---

# Event 4756

Event:

```text
4756
```

records a member being added to a security-enabled universal group.

---

# Event 4757

Event:

```text
4757
```

records a member being removed from a security-enabled universal group.

---

# Event 4758

Event:

```text
4758
```

records deletion of a security-enabled universal group.

---

# Privileged Group Monitoring

Prioritise monitoring for changes involving:

```text
Domain Admins
Enterprise Admins
Schema Admins
Administrators
Account Operators
Backup Operators
Server Operators
DnsAdmins
Custom Tier 0 Groups
GPO Administrators
PKI Administrators
Identity Management Groups
```

---

# Temporary Membership Detection

An important detection pattern is:

```text
Member Added
    |
    v
Privileged Authentication
    |
    v
Administrative Activity
    |
    v
Member Removed
```

An attacker may intentionally keep membership short-lived.

Therefore:

```text
Current Membership Review
```

alone may miss the activity.

Historical event monitoring is necessary.

---

# Correlate Authentication

After a privileged membership change, review:

```text
4624
4672
4768
4769
```

and relevant remote-service events.

The question is:

```text
Was the newly granted privilege actually used?
```

---

# Detect Unexpected Group Modifiers

Baseline:

```text
Who normally manages each privileged group?
```

Then alert when:

```text
Unexpected Principal
        |
        v
Changes Privileged Group
```

---

# Group ACL Monitoring

Membership events alone are insufficient.

An attacker may first modify:

```text
Group DACL
```

and then change membership.

Detection chain:

```text
ACL Change
   |
   v
New Membership Right
   |
   v
Member Added
   |
   v
Privilege Used
```

Monitor sensitive group ACLs as well as memberships.

---

# Purple Team Exercise

A controlled group exercise can use:

```text
Dedicated Test User
       |
       v
Delegated Test Group
       |
       v
Temporary Membership
       |
       v
Detection
       |
       v
Removal
       |
       v
Verification
```

Avoid production Tier 0 groups unless specifically required and authorised.

---

# Purple Team Questions

Defenders should determine:

```text
Which account changed the group?

Which group changed?

Which member was added?

Was the group privileged?

Who authorised the change?

Was the modifier expected?

Was the membership temporary?

Did a new logon follow?

Was administrative activity performed?

Was the group ACL changed first?

Was the change reverted?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect membership addition
Time to identify modifying account
Time to classify group privilege
Time to identify new member
Time to detect temporary membership
Time to correlate subsequent authentication
Time to identify ACL-based root cause
Time to containment
Time to restore membership
```

---

# Hardening

The group-security model is:

```text
Inventory
   |
   v
Classify
   |
   v
Minimise Membership
   |
   v
Restrict Membership Control
   |
   v
Protect Privileged Groups
   |
   v
Monitor Changes
   |
   v
Review Regularly
```

---

# Inventory Groups

Maintain an inventory containing:

```text
Group Name
Purpose
Owner
Manager
Scope
Category
Tier
Direct Members
Nested Groups
Resource Access
Who Can Modify
Review Date
```

Unknown-purpose groups should be investigated.

---

# Assign Owners

Privileged and business-critical groups should have identifiable owners.

The owner should understand:

```text
Why the group exists
Who should belong
What access it grants
How membership is approved
```

---

# Remove Unnecessary Members

Apply:

```text
Least Privilege
```

and:

```text
Role-Based Access
```

Remove:

```text
Former Employees
Old Service Accounts
Temporary Project Members
Unnecessary Administrators
Disabled Accounts
Legacy Migration Accounts
```

after appropriate review.

---

# Minimise Nested Privilege

Complex nesting makes privilege difficult to understand.

Example:

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
Group C
 |
 v
Privileged Group
```

Where possible, simplify administrative group structures.

---

# Separate Administrative Tiers

Avoid:

```text
Workstation Admins
       |
       v
Server Admins
       |
       v
Domain Admins
```

unless such inheritance is explicitly required.

A better model separates:

```text
Tier 0
Tier 1
Tier 2
```

administration.

---

# Use Dedicated Administrative Accounts

Human administrators should use separate privileged identities where appropriate.

Conceptually:

```text
Alice
 |
 +--> alice
 |     Standard Work
 |
 +--> alice-admin
       Administrative Work
```

This reduces exposure of privileged group memberships during ordinary activity.

---

# Just-in-Time Administration

Where organisational capabilities permit, prefer temporary privilege assignment rather than permanent privileged membership.

Conceptually:

```text
Administrator
     |
     v
Approved Task
     |
     v
Temporary Privilege
     |
     v
Task Completed
     |
     v
Privilege Removed
```

---

# Protected Users

Consider the:

```text
Protected Users
```

group for suitable privileged human accounts after compatibility testing.

This can reduce exposure to several legacy authentication behaviours.

---

# Protect Group ACLs

For privileged groups, review:

```text
Owner
GenericAll
GenericWrite
WriteDACL
WriteOwner
AddMember
Self
Inherited Permissions
```

Remove unnecessary control paths.

---

# Avoid Broad Membership Management

Bad:

```text
Authenticated Users
        |
        v
Modify Privileged Group
```

or:

```text
Large Helpdesk Group
        |
        v
GenericAll
        |
        v
Server Admins
```

Prefer narrowly scoped administration.

---

# Review managedBy

Ensure:

```text
managedBy
```

reflects the current business owner.

Also verify whether the manager has actual membership-modification rights and whether those rights remain necessary.

---

# Monitor Privileged Groups

Implement alerts for:

```text
Member Added
Member Removed
Group ACL Changed
Group Owner Changed
Nested Privileged Group Added
Privileged Group Created
```

---

# Review Service Account Membership

Service accounts should not receive broad administrative group membership merely for convenience.

Instead grant:

```text
Specific Required Rights
```

where practical.

---

# Review Application Groups

Do not focus only on built-in groups.

Custom groups may control:

```text
ERP
SQL
Backup Systems
Virtualisation
Cloud Platforms
Deployment Systems
Security Products
Certificate Services
```

These can be highly privileged.

---

# Incident Response

If unauthorised group modification is suspected:

```text
Group Change Detected
        |
        v
Identify Group
        |
        v
Identify Added / Removed Member
        |
        v
Identify Modifier
        |
        v
Determine Group Privilege
        |
        v
Review Modifier's ACL Rights
        |
        v
Review Authentication After Change
        |
        v
Contain Compromised Identity
        |
        v
Restore Membership
        |
        v
Restore ACL if Required
        |
        v
Hunt for Persistence
```

---

# Capture Evidence Before Remediation

Record:

```text
Group DN
Group SID
Group Scope
Group Category
Direct Membership
Recursive Membership
Owner
ManagedBy
DACL
Changed Member
Modifier
Timestamp
Relevant Event IDs
Resulting Privilege
```

before making changes where operationally possible.

---

# Review Nested Persistence

An attacker may not add themselves directly to:

```text
Domain Admins
```

Instead:

```text
Attacker
 |
 v
Low-Visibility Group
 |
 v
Nested Group
 |
 v
Privileged Group
```

Therefore incident response must recursively inspect group membership.

---

# Review ACL Persistence

An attacker may grant:

```text
AddMember
```

or:

```text
GenericAll
```

over a privileged group rather than leaving themselves as a member.

After removing malicious membership, review the group's ACL.

---

# Reporting

Possible finding titles include:

```text
Excessive Active Directory Group Membership Grants Administrative Access
```

```text
Low-Privilege Account Can Modify Privileged Active Directory Group
```

```text
Nested Group Membership Enables Privilege Escalation
```

```text
Excessive Active Directory Group Permissions Enable Administrative Access
```

```text
Service Account Holds Unnecessary Privileged Group Membership
```

```text
Stale Privileged Group Membership Increases Domain Attack Surface
```

---

# Report the Complete Path

Avoid:

```text
User Can Modify Group
```

Prefer:

```text
CORP\alice
   |
   v
AddMember
   |
   v
CORP\Server Admins
   |
   v
Local Administrator
   |
   v
Production Servers
```

This explains the actual impact.

---

# Example Finding

```text
Finding:
Low-Privilege Account Can Modify Privileged Active Directory Group

Affected Principal:
CORP\helpdesk-user

Affected Group:
CORP\Server Admins

Permission:
AddMember

Description:
The CORP\helpdesk-user account has permission to modify membership of
the CORP\Server Admins group.

Members of CORP\Server Admins receive local administrative privileges
on production Windows servers.

A user controlling CORP\helpdesk-user could therefore add a controlled
account to the group and inherit the administrative access assigned to
the group.

During controlled validation, the effective group permission and
resulting attack path were confirmed. No unnecessary remote command
execution was performed.

Impact:
Successful abuse would allow a low-privilege domain user to obtain
administrative access to systems managed through the affected group.

Depending on the systems accessible to the group, this could enable
credential access, lateral movement, access to sensitive data, and
further privilege escalation.

Recommendation:
Remove the unnecessary membership-modification permission from
CORP\helpdesk-user.

Review the complete ACL of CORP\Server Admins, identify whether the
permission was explicitly assigned or inherited, restrict group
membership management to dedicated administrative identities, review
all current and nested members, and monitor privileged group membership
and ACL changes.
```

---

# Evidence Checklist

Record:

```text
Source Principal
Source SID
Target Group
Target Group SID
Group Scope
Group Category
Group Owner
ManagedBy
Direct Members
Recursive Members
Relevant ACE
Inheritance
Resource Privilege
Systems Affected
Validation Performed
Original Membership
Final Membership
Relevant Events
Timestamp
```

---

# Group Assessment Checklist

## Preparation

- [ ] Confirm group enumeration is authorised
- [ ] Confirm whether membership modification is permitted
- [ ] Confirm privileged groups that must not be modified
- [ ] Identify dedicated test accounts
- [ ] Identify Tier 0 groups
- [ ] Record cleanup requirements

## Enumeration

- [ ] Enumerate all groups
- [ ] Enumerate security groups
- [ ] Enumerate distribution groups
- [ ] Enumerate group scopes
- [ ] Enumerate descriptions
- [ ] Enumerate managers
- [ ] Enumerate owners
- [ ] Enumerate direct members
- [ ] Enumerate recursive members
- [ ] Enumerate primary groups
- [ ] Identify foreign security principals
- [ ] Identify cross-domain memberships

## Privileged Groups

- [ ] Review Domain Admins
- [ ] Review Enterprise Admins
- [ ] Review Schema Admins
- [ ] Review Administrators
- [ ] Review Account Operators
- [ ] Review Backup Operators
- [ ] Review Server Operators
- [ ] Review Print Operators
- [ ] Review DnsAdmins
- [ ] Review Group Policy Creator Owners
- [ ] Review custom Tier 0 groups
- [ ] Review application administrator groups
- [ ] Review identity-management groups
- [ ] Review PKI groups

## Membership Analysis

- [ ] Identify nested groups
- [ ] Identify disabled members
- [ ] Identify stale members
- [ ] Identify service accounts
- [ ] Identify privileged service accounts
- [ ] Identify unusual cross-domain members
- [ ] Identify excessive permanent membership
- [ ] Review `adminCount`

## Group Control

- [ ] Review `GenericAll`
- [ ] Review `GenericWrite`
- [ ] Review `WriteDACL`
- [ ] Review `WriteOwner`
- [ ] Review `AddMember`
- [ ] Review `AddSelf`
- [ ] Review owner
- [ ] Review inherited ACEs
- [ ] Review `managedBy`
- [ ] Verify manager membership rights

## Resource Mapping

- [ ] Map groups to local administrators
- [ ] Map groups to RDP access
- [ ] Map groups to WinRM access
- [ ] Map groups to shares
- [ ] Map groups to GPOs
- [ ] Map groups to DCSync
- [ ] Map groups to delegation
- [ ] Map groups to AD CS
- [ ] Map groups to SQL
- [ ] Map groups to applications
- [ ] Map groups to Tier 0

## BloodHound

- [ ] Collect group relationships
- [ ] Review `MemberOf`
- [ ] Review outbound control
- [ ] Review inbound control
- [ ] Identify nested paths
- [ ] Identify shortest paths to high-value groups
- [ ] Identify groups with `AdminTo`
- [ ] Identify groups with replication rights
- [ ] Identify group ACL paths
- [ ] Independently confirm important findings

## Validation

- [ ] Choose minimum-impact proof
- [ ] Record original membership
- [ ] Use dedicated test account
- [ ] Add only where explicitly authorised
- [ ] Verify membership
- [ ] Avoid unnecessary privileged authentication
- [ ] Remove temporary member immediately
- [ ] Confirm original membership restored

## Detection

- [ ] Monitor 4727
- [ ] Monitor 4728
- [ ] Monitor 4729
- [ ] Monitor 4730
- [ ] Monitor 4731
- [ ] Monitor 4732
- [ ] Monitor 4733
- [ ] Monitor 4734
- [ ] Monitor 4735
- [ ] Monitor 4737
- [ ] Monitor 4754
- [ ] Monitor 4755
- [ ] Monitor 4756
- [ ] Monitor 4757
- [ ] Monitor 4758
- [ ] Monitor privileged group ACLs
- [ ] Correlate subsequent logons
- [ ] Detect temporary membership

## Hardening

- [ ] Inventory groups
- [ ] Assign owners
- [ ] Document business purpose
- [ ] Remove unnecessary members
- [ ] Remove stale accounts
- [ ] Review service-account membership
- [ ] Reduce nested privilege
- [ ] Separate administrative tiers
- [ ] Restrict membership control
- [ ] Harden privileged group ACLs
- [ ] Review group managers
- [ ] Implement periodic access reviews
- [ ] Monitor privileged changes
- [ ] Consider just-in-time administration

## Cleanup

- [ ] Remove test memberships
- [ ] Restore original group state
- [ ] Restore modified ACLs
- [ ] Confirm no temporary nested groups remain
- [ ] Verify final membership
- [ ] Verify final ACL
- [ ] Secure evidence

---

# Group Testing Model

The basic model is:

```text
User
 |
 v
Group
 |
 v
Permission
 |
 v
Resource
```

The nested model is:

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
Privileged Group
 |
 v
Privilege
```

The AGDLP model is:

```text
Accounts
   |
   v
Global Groups
   |
   v
Domain Local Groups
   |
   v
Permissions
```

The multi-domain model is:

```text
Accounts
   |
   v
Global Groups
   |
   v
Universal Groups
   |
   v
Domain Local Groups
   |
   v
Permissions
```

The ACL-driven group escalation model is:

```text
Controlled Principal
        |
        v
Group Modification Right
        |
        v
Privileged Group
        |
        v
Add Controlled Member
        |
        v
Inherited Privilege
```

The indirect ACL model is:

```text
Controlled Principal
        |
        v
WriteDACL
        |
        v
Privileged Group
        |
        v
Grant AddMember
        |
        v
Add Controlled Account
        |
        v
Privilege
```

The local administration model is:

```text
Domain User
    |
    v
Domain Group
    |
    v
Local Administrators
    |
    v
Member Server
```

The cross-domain model is:

```text
Domain A Principal
        |
        v
Domain A Group
        |
        v
Universal / Foreign Membership
        |
        v
Domain B Group
        |
        v
Domain B Resource
```

The detection model is:

```text
Group Change
    |
    v
Membership Event
    |
    v
New Authentication
    |
    v
Privilege Use
    |
    v
Optional Membership Removal
```

The defensive model is:

```text
Inventory
   |
   v
Classify
   |
   v
Identify Owners
   |
   v
Review Membership
   |
   v
Review Group ACL
   |
   v
Map Actual Privilege
   |
   v
Remove Excess Access
   |
   v
Monitor Changes
```

A mature group assessment should answer:

```text
Which groups exist?
       |
       v
Which are security groups?
       |
       v
Which groups are privileged?
       |
       v
Who belongs directly?
       |
       v
Who belongs recursively?
       |
       v
Who can modify membership?
       |
       v
Who owns the group?
       |
       v
Which resources trust the group?
       |
       v
Which systems become accessible?
       |
       v
Can the group reach Tier 0?
       |
       v
Can the privilege be demonstrated safely?
```

The most important principle is:

```text
Group Name
    |
    X
Actual Privilege
```

Instead:

```text
Membership
    +
Nesting
    +
ACLs
    +
Resource Permissions
    +
Administrative Relationships
    =
Actual Privilege
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

BloodHound:

[BloodHound](bloodhound.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

AS-REP Roasting:

[AS-REP Roasting](asrep-roasting.md)

Password Spraying:

[Password Spraying](password-spraying.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[S4U](s4u.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

The following topics complement group analysis and can be linked once their dedicated notes are available:

```text
active-directory/group-policy.md
active-directory/machine-account-quota.md
active-directory/shadow-credentials.md
active-directory/gmsa.md
active-directory/dcsync.md
active-directory/sid-history.md
active-directory/trusts/index.md
active-directory/ad-cs/index.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft Active Directory Groups

[Microsoft - Active Directory Security Groups](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Group Scope](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups#group-scope){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft PowerShell

[Microsoft - Get-ADGroup](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroup){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-ADGroupMember](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adgroupmember){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-ADPrincipalGroupMembership](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adprincipalgroupmembership){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Add-ADGroupMember](https://learn.microsoft.com/en-us/powershell/module/activedirectory/add-adgroupmember){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Remove-ADGroupMember](https://learn.microsoft.com/en-us/powershell/module/activedirectory/remove-adgroupmember){ target="_blank" rel="noopener noreferrer" }

---

## LDAP

[Microsoft - LDAP Matching Rule in Chain](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/1e889adc-b503-4423-8985-c28d5c7d4887){ target="_blank" rel="noopener noreferrer" }

---

## Protected Accounts

[Microsoft - Protected Accounts and Groups in Active Directory](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/appendix-c--protected-accounts-and-groups-in-active-directory){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Protected Users Security Group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## PowerView

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Additional Local or Cloud Groups](https://attack.mitre.org/techniques/T1098/007/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Additional Cloud Roles](https://attack.mitre.org/techniques/T1098/003/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Active Directory groups should be analysed as privilege containers rather than simply lists of users.

The basic model is:

```text
Identity
   |
   v
Group
   |
   v
Permission
   |
   v
Resource
```

However, real environments commonly contain:

```text
Identity
   |
   v
Group
   |
   v
Nested Group
   |
   v
Another Group
   |
   v
Resource Permission
```

Therefore:

```text
Direct Membership
```

is not sufficient.

Assess:

```text
Recursive Membership
Group Scope
Group ACL
Group Owner
Membership Control
Resource Permissions
Cross-Domain Relationships
```

The most important offensive question is:

```text
Which groups can my controlled
principal reach or modify?
```

The most important defensive question is:

```text
Which principals can reach or
modify our privileged groups?
```

A complete attack path may look like:

```text
Low-Privilege User
        |
        v
Helpdesk
        |
        v
AddMember
        |
        v
Server Admins
        |
        v
Local Administrator
        |
        v
Production Servers
```

or:

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
Privileged Group Membership
        |
        v
Administrative Access
```

Group names alone should never determine severity.

Instead:

```text
Membership
    +
Nesting
    +
ACL Control
    +
Resource Access
    +
Resulting Privilege
    =
Security Impact
```

The assessment workflow should therefore be:

```text
Enumerate Groups
      |
      v
Enumerate Members
      |
      v
Expand Nesting
      |
      v
Identify Privileged Groups
      |
      v
Identify Group Controllers
      |
      v
Map Resource Access
      |
      v
Build Attack Paths
      |
      v
Validate Safely
      |
      v
Collect Evidence
```

For defenders:

```text
Inventory
   |
   v
Assign Ownership
   |
   v
Review Membership
   |
   v
Review Nesting
   |
   v
Review ACLs
   |
   v
Reduce Privilege
   |
   v
Monitor Changes
   |
   v
Repeat
```

The strongest Active Directory group assessments therefore combine:

```text
PowerShell
   +
LDAP
   +
ACL Analysis
   +
BloodHound
   +
Host-Level Access Mapping
   +
Authentication Telemetry
```

to determine not simply:

```text
Who belongs to which group?
```

but the much more important question:

```text
What can each identity ultimately control?
```
