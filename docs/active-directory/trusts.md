# Active Directory Domain and Forest Trusts

Active Directory trusts allow authentication and resource access to cross domain or forest boundaries.

Trusts are fundamental to many enterprise Active Directory environments because organisations may operate:

```text
Multiple Domains
Child Domains
Multiple Forests
Legacy Domains
Acquired Companies
Partner Environments
Resource Forests
Administrative Forests
```

A trust creates a relationship in which one domain or forest may accept authentication originating from another.

Conceptually:

```text
Domain A
   |
   | Trust
   v
Domain B
```

However, a trust does not automatically mean:

```text
Every User in Domain A
        |
        v
Full Access to Domain B
```

Authentication and authorisation remain separate concepts.

The important security question is:

```text
Which identities from one security boundary
can authenticate to and access resources
inside another security boundary?
```

During an authorised Active Directory assessment, trust analysis should determine:

```text
Which Trusts Exist?
What Type Are They?
Which Direction Do They Operate?
Are They Transitive?
What Authentication Model Is Used?
What SID Filtering Is Applied?
What Resources Are Accessible?
Are Privileged Relationships Crossing the Trust?
```

!!! warning "Authorised testing only"
    Trust enumeration can reveal relationships with domains, forests, subsidiaries or partner organisations that are outside the assessment scope. The existence of a trust does not automatically authorise testing of the trusted or trusting environment. Treat every domain and forest as a separate scope boundary unless explicitly stated otherwise.

---

# Trusts at a Glance

A trust relationship can be represented as:

```text
Domain A
   |
   v
Trust Relationship
   |
   v
Domain B
```

The practical security path is:

```text
Identity
   |
   v
Authentication
   |
   v
Trust
   |
   v
Remote Domain / Forest
   |
   v
Authorisation
   |
   v
Resource
```

The existence of a trust establishes an authentication relationship.

Actual access still depends on:

```text
Groups
ACLs
Local Permissions
Share Permissions
Application Permissions
Authentication Policies
SID Filtering
Selective Authentication
```

---

# Why Trusts Exist

Organisations use trusts to provide controlled access between administrative boundaries.

Examples include:

```text
Parent and Child Domains
Corporate Forests
Resource Forests
Mergers and Acquisitions
Legacy Environments
Partner Organisations
Migration Environments
```

Without a trust, identities from one domain normally cannot automatically authenticate to resources in another independent domain.

---

# Trust Terminology

Several terms must be understood before analysing trust relationships:

```text
Trusting Domain
Trusted Domain
Trust Direction
Transitivity
Trust Type
Forest Trust
External Trust
Realm Trust
Parent-Child Trust
Tree-Root Trust
SID Filtering
Selective Authentication
```

---

# Trusted Domain

The:

```text
Trusted Domain
```

contains the identities that are trusted.

Conceptually:

```text
Domain A trusts Domain B
```

means:

```text
Users from Domain B
may be accepted by Domain A
```

Therefore:

```text
Domain B
=
Trusted Domain
```

---

# Trusting Domain

The:

```text
Trusting Domain
```

contains resources that may accept identities from the trusted domain.

If:

```text
Domain A trusts Domain B
```

then:

```text
Domain A
=
Trusting Domain
```

and:

```text
Domain B
=
Trusted Domain
```

---

# Trust Direction

Trust direction is one of the most commonly misunderstood Active Directory concepts.

Suppose:

```text
CORP.LOCAL
trusts
PARTNER.LOCAL
```

The authentication relationship is:

```text
PARTNER.LOCAL users
        |
        v
CORP.LOCAL resources
```

because CORP trusts identities from PARTNER.

---

# One-Way Trust

A one-way trust operates in one direction.

Example:

```text
CORP.LOCAL
    |
    | trusts
    v
PARTNER.LOCAL
```

Authentication flows conceptually in the opposite direction:

```text
PARTNER users
      |
      v
CORP resources
```

This distinction is essential during trust analysis.

---

# Two-Way Trust

A two-way trust allows both domains to trust identities from the other.

```text
Domain A
   <---->
Domain B
```

Conceptually:

```text
Domain A Users
      |
      v
Domain B Resources
```

and:

```text
Domain B Users
      |
      v
Domain A Resources
```

subject to authorisation.

---

# Trust Direction Values

Active Directory tools may display trust direction using values such as:

```text
Inbound
Outbound
Bidirectional
```

Always interpret the value from the perspective of the domain being queried.

Do not rely solely on visual arrows without understanding the querying context.

---

# Transitive Trusts

A transitive trust can extend beyond the two directly connected domains.

Example:

```text
Domain A
   |
   v
Domain B
   |
   v
Domain C
```

A transitive trust relationship may allow authentication relationships to extend across the chain.

---

# Non-Transitive Trusts

A non-transitive trust applies only between the directly configured domains.

```text
Domain A
   |
   v
Domain B
```

does not automatically extend to:

```text
Domain C
```

---

# Trust Types

Important Active Directory trust types include:

```text
Parent-Child Trust
Tree-Root Trust
External Trust
Forest Trust
Shortcut Trust
Realm Trust
```

Each has different security implications.

---

# Parent-Child Trust

When a child domain is created inside an existing forest, Active Directory automatically creates a:

```text
Two-Way
Transitive
Parent-Child Trust
```

Example:

```text
corp.example
     |
     v
emea.corp.example
```

The domains belong to the same forest.

---

# Parent-Child Trust Model

```text
corp.example
      ^
      |
Two-Way Transitive Trust
      |
      v
emea.corp.example
```

This supports authentication across the forest.

---

# Tree-Root Trust

When a new domain tree is created inside an existing forest, Active Directory creates a:

```text
Two-Way
Transitive
Tree-Root Trust
```

Example:

```text
corp.example
      |
      | Forest
      |
      +------ example-services.net
```

The DNS namespaces differ, but both domain trees belong to the same forest.

---

# Forest Trust

A forest trust connects:

```text
Forest A
```

and:

```text
Forest B
```

Example:

```text
corp.example
     |
     | Forest Trust
     |
partner.example
```

Forest trusts can be:

```text
One-Way
Two-Way
```

and can provide transitive authentication relationships between domains in the participating forests according to the trust configuration.

---

# Forest Trust Security Boundary

A forest is generally the primary Active Directory security boundary.

Therefore:

```text
Domain Boundary
```

and:

```text
Forest Boundary
```

should not be treated as equivalent.

Within a single forest, domains have strong trust relationships and share forest-wide infrastructure.

---

# External Trust

An external trust is commonly used between:

```text
Domains in Different Forests
```

without establishing a forest-wide trust.

External trusts are generally:

```text
Non-Transitive
```

and apply to the specific domains involved.

---

# External Trust Model

```text
corp.example
      |
      | External Trust
      |
legacy.example
```

The relationship does not automatically extend to every domain in either forest.

---

# Shortcut Trust

Shortcut trusts can be created between domains in the same forest to shorten authentication paths.

Example:

```text
child-a.corp.example
          |
          | Shortcut Trust
          |
child-b.corp.example
```

This may improve authentication efficiency in complex domain trees.

---

# Realm Trust

Realm trusts allow Active Directory to establish trust relationships with non-Windows Kerberos realms.

Conceptually:

```text
Active Directory
      |
      | Realm Trust
      |
      v
Kerberos Realm
```

Realm trusts can have different:

```text
Direction
Transitivity
Authentication
```

properties.

---

# Trust Enumeration Strategy

A structured trust assessment should follow:

```text
Identify Current Domain
        |
        v
Identify Current Forest
        |
        v
Enumerate Domain Trusts
        |
        v
Enumerate Forest Trusts
        |
        v
Determine Direction
        |
        v
Determine Transitivity
        |
        v
Review Trust Attributes
        |
        v
Identify Cross-Domain Groups
        |
        v
Identify Cross-Domain ACLs
        |
        v
Identify Accessible Resources
        |
        v
Assess Security Controls
```

---

# Identify Current Domain

Native Windows:

```powershell
$env:USERDNSDOMAIN
```

Alternative:

```cmd
whoami /fqdn
```

Domain controller discovery:

```cmd
nltest /dsgetdc:corp.example
```

---

# Identify Current Forest

With the ActiveDirectory PowerShell module:

```powershell
Get-ADForest
```

Useful properties include:

```text
Name
RootDomain
Domains
GlobalCatalogs
DomainNamingMaster
SchemaMaster
ForestMode
```

---

# Enumerate Forest Domains

```powershell
Get-ADForest | Select-Object -ExpandProperty Domains
```

Example:

```text
corp.example
emea.corp.example
na.corp.example
```

---

# Get Current Domain

```powershell
Get-ADDomain
```

Useful properties include:

```text
DNSRoot
NetBIOSName
DomainSID
ParentDomain
ChildDomains
Forest
DomainMode
```

---

# Enumerate Child Domains

```powershell
Get-ADDomain | Select-Object -ExpandProperty ChildDomains
```

---

# Native Trust Enumeration

Windows provides:

```text
nltest.exe
```

which can help inspect trust relationships.

Example:

```cmd
nltest /domain_trusts
```

This can display known trust relationships for the current domain.

---

# Detailed NLTest Output

```cmd
nltest /domain_trusts /all_trusts
```

Review the returned trust information carefully.

Do not assume every displayed domain is within assessment scope.

---

# Domain Controller Discovery

For a known trusted domain:

```cmd
nltest /dsgetdc:partner.example
```

This performs domain controller discovery.

Use only where querying the domain is within the approved scope.

---

# ActiveDirectory PowerShell Trust Enumeration

The ActiveDirectory module provides:

```powershell
Get-ADTrust -Filter *
```

Useful properties include:

```text
Name
Source
Target
Direction
ForestTransitive
IntraForest
SelectiveAuthentication
SIDFilteringForestAware
SIDFilteringQuarantined
TrustType
```

---

# Focused Trust Output

```powershell
Get-ADTrust -Filter * |
    Select-Object Name,Source,Target,Direction,TrustType,ForestTransitive,IntraForest,SelectiveAuthentication
```

This provides a useful high-level trust inventory.

---

# Query a Specific Trust

```powershell
Get-ADTrust -Identity 'partner.example'
```

Use this when reviewing a known relationship rather than repeatedly enumerating every trust.

---

# PowerView

PowerView can enumerate domain trust relationships.

Depending on the PowerView version, commonly used functions include:

```powershell
Get-DomainTrust
```

and:

```powershell
Get-DomainTrustMapping
```

Always verify the available functions in the version being used.

Example:

```powershell
Get-Command Get-DomainTrust -ErrorAction SilentlyContinue
```

---

# PowerView Domain Trusts

Where available:

```powershell
Get-DomainTrust
```

can provide information about trust relationships known to the current domain.

---

# Trust Mapping

Where supported:

```powershell
Get-DomainTrustMapping
```

can help visualise relationships across domains.

Do not automatically query domains outside the authorised scope.

---

# BloodHound

BloodHound is particularly useful for understanding how trust relationships interact with:

```text
Group Membership
ACLs
Sessions
Administrative Rights
Cross-Domain Principals
```

See:

[BloodHound](bloodhound.md)

---

# Trusts in BloodHound

Trust relationships can provide context for paths such as:

```text
User
 |
 v
Group
 |
 v
Foreign Group Membership
 |
 v
Trusted Domain
 |
 v
Administrative Relationship
```

The trust itself is only part of the path.

---

# BloodHound Trust Analysis

Useful questions include:

```text
Which Domains Exist?

Which Forests Exist?

Which Trusts Connect Them?

Are Foreign Principals Members of Privileged Groups?

Do Cross-Domain ACLs Exist?

Can One Domain Administer Systems in Another?
```

---

# Linux Trust Enumeration

Trust information can also be queried from Linux using LDAP and Active Directory tooling.

Useful tools include:

```text
ldapsearch
NetExec
Impacket
BloodHound Collectors
```

---

# LDAP Trusted Domain Objects

Active Directory stores trust relationships as:

```text
trustedDomain
```

objects.

These are normally located beneath:

```text
CN=System
```

in the domain naming context.

---

# LDAP Trust Search

Example:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=System,DC=corp,DC=example' \
  '(objectClass=trustedDomain)' \
  cn trustDirection trustType trustAttributes securityIdentifier
```

This is enumeration only.

---

# Important Trust Attributes

Useful LDAP attributes include:

```text
trustDirection
trustType
trustAttributes
securityIdentifier
flatName
trustPartner
```

These values help determine the nature of the trust.

---

# Trust Direction Values in LDAP

The `trustDirection` attribute is represented numerically.

Common values are:

```text
0 = Disabled
1 = Inbound
2 = Outbound
3 = Bidirectional
```

Interpret direction from the perspective of the domain containing the trust object.

---

# Trust Type Values

The `trustType` attribute identifies the trust mechanism.

Common values include:

```text
1 = Windows non-Active Directory
2 = Active Directory
3 = MIT Kerberos realm
```

Do not rely on the numeric value alone.

Also evaluate:

```text
trustAttributes
```

and the environment.

---

# Trust Attributes

`trustAttributes` is a bit field describing trust characteristics.

Possible characteristics can include:

```text
Non-Transitive
Uplevel
Quarantined Domain
Forest Transitive
Cross-Organisation
Within Forest
Treat-As-External
Uses RC4 Encryption
Cross-Organisation No TGT Delegation
PIM Trust
```

Interpret these carefully because multiple flags can exist simultaneously.

---

# Trust Analysis

Trust enumeration should produce a table similar to:

| Source | Target | Direction | Type | Transitive | Selective Authentication |
|---|---|---|---|---|---|
| corp.example | emea.corp.example | Bidirectional | Parent-Child | Yes | No |
| corp.example | partner.example | Bidirectional | Forest | Yes | Yes |
| corp.example | legacy.example | Outbound | External | No | No |

The values above are illustrative only.

---

# Authentication vs Authorisation

A trust answers:

```text
Can this identity be recognised?
```

It does not automatically answer:

```text
What can this identity access?
```

The full model is:

```text
Identity
   |
   v
Trust
   |
   v
Authentication
   |
   v
Authorisation
   |
   v
Resource
```

---

# Cross-Domain Group Membership

One of the most important trust assessment areas is:

```text
Foreign Principal
      |
      v
Local Domain Group
      |
      v
Privilege
```

For example:

```text
PARTNER\User
      |
      v
CORP\Server-Admins
      |
      v
Administrative Access
```

This may be more important than the trust configuration itself.

---

# Foreign Security Principals

Active Directory can represent security principals from trusted domains using:

```text
Foreign Security Principals
```

typically beneath:

```text
CN=ForeignSecurityPrincipals
```

---

# ForeignSecurityPrincipals Container

Conceptually:

```text
CN=ForeignSecurityPrincipals
        |
        +--> Foreign SID
        |
        +--> Foreign SID
        |
        +--> Foreign SID
```

These objects can represent users or groups from trusted domains that have been referenced in the local domain.

---

# Enumerate Foreign Security Principals

With the ActiveDirectory module:

```powershell
Get-ADObject -SearchBase 'CN=ForeignSecurityPrincipals,DC=corp,DC=example' -LDAPFilter '(objectClass=foreignSecurityPrincipal)' -Properties *
```

Review:

```text
Name
ObjectSID
MemberOf
```

where available.

---

# Foreign Group Membership

A foreign identity may be added to a local domain group.

Example:

```text
PARTNER\Domain Admins
         |
         v
CORP\Application-Admins
         |
         v
Server Administration
```

This can create a significant cross-boundary privilege path.

---

# Enumerate Group Members

```powershell
Get-ADGroupMember -Identity 'Application-Admins'
```

Investigate unexpected:

```text
ForeignSecurityPrincipal
```

entries.

---

# Recursive Membership

```powershell
Get-ADGroupMember -Identity 'Application-Admins' -Recursive
```

Recursive membership can help reveal nested cross-domain relationships.

---

# Domain Local Groups

Domain Local groups are particularly relevant to cross-domain access because they can contain principals from trusted domains and grant access to resources in the local domain.

Conceptually:

```text
Trusted Domain User
        |
        v
Domain Local Group
        |
        v
Local Resource
```

---

# AGDLP

A common Active Directory permissions model is:

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

or:

```text
A
|
G
|
DL
|
P
```

Trust analysis should therefore include:

```text
Domain Local Group Membership
```

rather than looking only for direct ACL assignments.

---

# AGUDLP

Multi-domain environments may use:

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

or:

```text
A
|
G
|
U
|
DL
|
P
```

This can make privilege relationships span several domains.

---

# Universal Groups

Universal groups can contain principals from multiple domains within the forest.

They are therefore important when reviewing forest-wide privilege relationships.

---

# Enterprise Admins

The:

```text
Enterprise Admins
```

group exists in the forest root domain.

It has highly privileged capabilities across the forest.

A compromise involving Enterprise Admin-level control should therefore be treated as:

```text
Forest-Wide Security Impact
```

rather than merely a compromise of one domain.

---

# Schema Admins

The:

```text
Schema Admins
```

group also exists in the forest root domain.

Schema modifications affect the forest-wide Active Directory schema.

Membership should be extremely limited.

---

# Forest Is the Security Boundary

A critical principle is:

```text
Forest
=
Primary Active Directory Security Boundary
```

Domains within a forest provide:

```text
Administrative Organisation
Policy Boundaries
Replication Boundaries
Naming Boundaries
```

but should not normally be treated as strong isolation boundaries against a fully compromised domain with sufficiently privileged control.

---

# Intra-Forest Trusts

Within a forest:

```text
Parent-Child
Tree-Root
```

trusts are automatically:

```text
Two-Way
Transitive
```

This allows authentication throughout the forest.

---

# Cross-Forest Trusts

Between separate forests, security controls become especially important.

Relevant controls include:

```text
SID Filtering
Selective Authentication
Authentication Policies
Network Segmentation
Group Membership
ACL Review
```

---

# SID Filtering

SID filtering is designed to prevent inappropriate SIDs from one trust boundary being accepted across another.

Conceptually:

```text
Authentication Token
       |
       v
SID Filtering
       |
       +--> Expected SIDs
       |
       X
       |
       +--> Disallowed SIDs
```

---

# Why SID Filtering Matters

Windows access tokens can contain multiple SIDs.

Without appropriate filtering, manipulated or inappropriate SID information crossing a trust could potentially affect authorisation decisions.

SID filtering therefore protects trust boundaries.

---

# SIDHistory

Active Directory supports:

```text
sIDHistory
```

to assist migration scenarios.

A migrated account can retain SIDs associated with previous identities so that existing permissions continue to work.

Conceptually:

```text
New Account SID
      +
Old SID in SIDHistory
      |
      v
Existing Resource ACL
```

---

# SIDHistory Security Relevance

SIDHistory is legitimate functionality.

However, excessive or inappropriate SIDHistory values can create unexpected privilege relationships.

Trust analysis should therefore consider:

```text
SID Filtering
SIDHistory
Migration Configuration
Cross-Domain Permissions
```

A dedicated SIDHistory page will cover this topic in more depth.

---

# Enumerate SIDHistory

Where authorised:

```powershell
Get-ADUser -Filter * -Properties SIDHistory |
    Where-Object { $_.SIDHistory } |
    Select-Object SamAccountName,SID,SIDHistory
```

For groups:

```powershell
Get-ADGroup -Filter * -Properties SIDHistory |
    Where-Object { $_.SIDHistory } |
    Select-Object Name,SID,SIDHistory
```

Large environments should use appropriately scoped LDAP filters rather than unnecessarily retrieving every account.

---

# Selective Authentication

Forest and external trusts can use:

```text
Selective Authentication
```

to restrict which trusted identities are permitted to authenticate to specific systems.

Without selective authentication, the trust may permit broader authentication across the trusting environment, subject to resource authorisation.

---

# Selective Authentication Model

Without selective authentication:

```text
Trusted Domain
      |
      v
Broad Authentication Relationship
      |
      v
Resource Authorisation
```

With selective authentication:

```text
Trusted Domain
      |
      v
Allowed to Authenticate?
      |
      +--> No --> Stop
      |
      +--> Yes
             |
             v
      Resource Authorisation
```

---

# Allowed to Authenticate

Selective authentication uses the:

```text
Allowed to authenticate
```

extended right on computer objects and other applicable security principals.

This provides an additional boundary before normal resource authorisation.

---

# Enumerate Selective Authentication

Using the ActiveDirectory module:

```powershell
Get-ADTrust -Filter * |
    Select-Object Name,Direction,SelectiveAuthentication
```

A value indicating selective authentication is enabled should then be evaluated alongside actual delegated authentication rights.

---

# Trust Authentication Scope

During assessment, determine:

```text
Can Foreign Users Authenticate Everywhere?

Or:

Can Foreign Users Authenticate Only to Approved Systems?
```

The latter generally provides stronger cross-boundary isolation.

---

# Forest-Wide Authentication

Forest trusts can be configured for broader forest-wide authentication.

This may be operationally convenient but increases the importance of:

```text
Resource ACLs
Group Membership
Network Controls
Privilege Separation
```

---

# Trust Passwords

Active Directory trusts maintain secret material used to support authentication between domains.

These secrets should be treated as highly sensitive.

Trust account compromise can have serious security implications.

---

# Trusted Domain Objects

Trust relationships are represented by:

```text
trustedDomain
```

objects in Active Directory.

Conceptually:

```text
CN=System
   |
   v
Trusted Domain Object
   |
   +--> Trust Partner
   +--> Direction
   +--> Type
   +--> Attributes
   +--> Security Information
```

---

# Trust Accounts

Inter-domain trust relationships can involve special trust account representations.

These are not normal user accounts and should not be managed as ordinary identities.

---

# Trust Secret Rotation

Trust passwords are managed by Windows as part of the trust relationship.

Administrators should avoid manually manipulating trust secrets unless following documented Microsoft procedures.

---

# Trust Tickets

Kerberos trust relationships allow referral tickets to support authentication across domains.

Conceptually:

```text
User
 |
 v
Domain A KDC
 |
 v
Referral
 |
 v
Domain B KDC
 |
 v
Service Ticket
 |
 v
Resource
```

---

# Cross-Domain Kerberos

Suppose:

```text
user@CHILD.CORP.EXAMPLE
```

needs access to:

```text
fileserver.corp.example
```

Kerberos can use trust referrals to move authentication toward the domain responsible for the destination service.

---

# Kerberos Referral Model

```text
User
 |
 v
Source KDC
 |
 v
Inter-Domain Referral
 |
 v
Target KDC
 |
 v
Service Ticket
 |
 v
Target Service
```

See:

[Kerberos](kerberos.md)

and:

[Kerberos Tickets](kerberos-tickets.md)

---

# Inspect Kerberos Tickets

Windows:

```cmd
klist
```

Linux:

```bash
klist
```

Cross-domain activity may result in referral-related tickets appearing in the cache.

---

# Trust Tickets and Security Testing

Trust-ticket abuse can have significant cross-domain consequences when sufficiently privileged trust material is compromised.

This should be tested only in:

```text
Dedicated Labs
Explicitly Approved Scenarios
```

because the impact can cross domain and forest boundaries.

A dedicated Trust Tickets page should contain the detailed methodology.

---

# Trusts and DNS

Cross-domain authentication often depends on DNS.

Important records can include:

```text
Domain Controllers
Kerberos
LDAP
Global Catalog
```

---

# SRV Records

Example:

```bash
dig _ldap._tcp.dc._msdcs.partner.example SRV
```

Kerberos:

```bash
dig _kerberos._tcp.partner.example SRV
```

Only query trusted domains included in the authorised scope.

---

# Windows DNS Lookup

```powershell
Resolve-DnsName -Type SRV '_ldap._tcp.dc._msdcs.partner.example'
```

---

# Trusts and Network Connectivity

A trust may exist while network controls prevent direct access.

Example:

```text
Forest A
   |
   | Trust
   |
Forest B

but:

Forest A Workstation
        |
        X
        |
Forest B Server
```

This can be an intentional and effective control.

---

# Trust Does Not Equal Network Reachability

The full relationship is:

```text
Trust
  +
Network Path
  +
Authentication
  +
Authorisation
  =
Resource Access
```

Removing any required component can prevent access.

---

# Trusts and Lateral Movement

A trust can expand the potential lateral-movement graph.

Example:

```text
Compromised User
      |
      v
Domain A Group
      |
      v
Foreign Group Membership
      |
      v
Domain B Server
```

See:

[Lateral Movement](lateral-movement.md)

---

# Trusts and Pivoting

Network segmentation may require a pivot before systems in another trusted domain are reachable.

```text
Domain A
   |
   v
Pivot
   |
   v
Domain B Network
```

See:

[Pivoting](pivoting.md)

The trust and network path should be assessed separately.

---

# Trusts and ACLs

Cross-domain principals may appear in Active Directory ACLs.

Example:

```text
PARTNER\Security-Team
          |
          v
GenericAll
          |
          v
CORP\ServiceAccount
```

This could create an unexpected cross-domain privilege path.

See:

[ACL and ACE](acl-ace.md)

---

# Trusts and Group Policy

Foreign principals may receive administrative rights through:

```text
Group Policy
```

For example:

```text
Foreign Group
      |
      v
GPO
      |
      v
Local Administrators
      |
      v
Servers
```

See:

[Group Policy](group-policy.md)

---

# Trusts and Local Administrators

Check whether trusted-domain groups have been added to local administrative groups.

Example:

```text
PARTNER\IT-Support
       |
       v
Local Administrators
       |
       v
CORP Server
```

This may be legitimate, but it significantly expands the security dependency between environments.

---

# Trusts and Service Accounts

Service accounts from one domain may be granted access to resources in another.

Review:

```text
Service Accounts
gMSAs
Application Pools
Scheduled Tasks
SQL Services
Backup Accounts
Monitoring Accounts
```

for cross-domain dependencies.

See:

[gMSA](gmsa.md)

---

# Trusts and SQL Server

SQL Server deployments can introduce cross-domain access through:

```text
Windows Authentication
Service Accounts
Linked Servers
Administrative Groups
```

These relationships should be included when analysing trust exposure.

---

# Trusts and File Servers

Cross-domain access frequently exists on file servers.

Review:

```text
Share Permissions
NTFS Permissions
Domain Local Groups
Foreign Security Principals
```

Do not assume that trust access is limited to Active Directory objects.

---

# Trusts and RDP

Foreign users may have:

```text
Remote Desktop Users
```

or local administrator rights on systems in another domain.

This can create direct cross-domain interactive access.

---

# Trusts and WinRM

Trusted-domain users may also have WinRM rights through:

```text
Local Administrators
Remote Management Users
JEA Configuration
Custom Endpoint Permissions
```

See:

[WinRM](winrm.md)

---

# Trusts and SMB

Cross-domain SMB access may occur through:

```text
Share ACL
NTFS ACL
Domain Local Group
Foreign Principal
```

See:

[SMB](smb.md)

---

# Trusts and WMI / DCOM

Administrative identities from trusted domains may also have remote WMI or DCOM access.

See:

[WMI](wmi.md)

and:

[DCOM](dcom.md)

---

# Trusts and NTLM

Trust relationships are primarily associated with domain authentication mechanisms, but NTLM may still appear in cross-domain environments depending on:

```text
Name Resolution
Application Behaviour
Legacy Systems
Trust Type
Authentication Configuration
```

See:

[NTLM](ntlm.md)

---

# Trusts and Kerberos

Kerberos is central to normal Active Directory cross-domain authentication.

Trust analysis should therefore understand:

```text
Referral TGTs
SPNs
KDC Discovery
DNS
Trust Direction
```

See:

[Kerberos](kerberos.md)

---

# Cross-Forest Administrative Dependencies

A major security concern is:

```text
Forest A
   |
   v
Privileged Account
   |
   v
Administration
   |
   v
Forest B
```

This means compromise of Forest A may have security consequences for Forest B even if the forests are technically separate security boundaries.

---

# Privileged Cross-Forest Groups

Review whether foreign principals are members of:

```text
Administrators
Server Admin Groups
Backup Operators
Remote Management Groups
Application Admin Groups
Database Admin Groups
Virtualisation Admin Groups
```

in another forest.

---

# Shared Administrative Accounts

Avoid designs where the same privileged account is used across independent forests.

A stronger model is:

```text
Forest A Admin
      |
      X
      |
Forest B

Forest B Admin
      |
      v
Forest B
```

with dedicated credentials for each boundary.

---

# Trust and Tier 0

Any trust relationship that provides access to:

```text
Domain Controllers
AD CS
Identity Infrastructure
Federation Services
Privileged Access Systems
```

should receive particular scrutiny.

These systems may effectively belong to:

```text
Tier 0
```

or an equivalent privileged control plane.

---

# AD CS Across Trusts

Certificate authentication can also interact with multi-domain and multi-forest environments.

Review:

```text
Enterprise CAs
Certificate Templates
Enrollment Permissions
Certificate Mapping
Forest Membership
Trust Relationships
```

See:

[Active Directory Certificate Services](ad-cs/index.md)

---

# Forest Trust Authentication Controls

When separate forests require a trust, consider:

```text
One-Way Trust Where Possible
Selective Authentication
SID Filtering
Minimal Group Membership
Network Segmentation
Dedicated Administrative Accounts
Monitoring
```

---

# Trust Direction Principle

If only:

```text
Forest B users
```

need access to:

```text
Forest A resources
```

do not automatically create:

```text
Two-Way Trust
```

if a:

```text
One-Way Trust
```

meets the business requirement.

---

# Minimise Transitivity

Where a trust does not need to extend beyond specific domains, avoid unnecessarily broad transitive relationships.

This reduces the authentication scope.

---

# Selective Authentication Principle

For higher-risk forest relationships, consider:

```text
Selective Authentication
```

so that foreign identities cannot authenticate broadly across the trusting forest.

---

# SID Filtering Principle

SID filtering should remain enabled where appropriate.

Do not disable SID filtering merely to make a legacy application work without first understanding the security consequences.

---

# Migration Considerations

Some trust controls are weakened temporarily during:

```text
Domain Migration
Forest Migration
Mergers
Acquisitions
```

For example, migration designs may rely on:

```text
SIDHistory
```

These temporary configurations should have:

```text
Documented Purpose
Defined Owner
Expiration Date
Post-Migration Review
```

---

# Legacy Trusts

Trusts frequently remain after the original business requirement has disappeared.

Examples:

```text
Completed Migration
Old Subsidiary
Retired Application
Former Partner
Legacy Forest
```

Unused trusts should be reviewed and removed through controlled administrative procedures.

---

# Trust Enumeration Is Not Exploitation

Discovering:

```text
partner.example
```

through a trust does not mean the tester should:

```text
Enumerate Every Partner Host
```

The correct workflow is:

```text
Discover Trust
      |
      v
Record Relationship
      |
      v
Check Scope
      |
      +--> Out of Scope --> Stop
      |
      +--> In Scope
             |
             v
      Continue Assessment
```

---

# Safe Trust Assessment Workflow

A controlled trust assessment should follow:

```text
Identify Current Domain
        |
        v
Identify Forest
        |
        v
Enumerate Trust Objects
        |
        v
Map Direction
        |
        v
Map Transitivity
        |
        v
Identify Security Controls
        |
        v
Identify Foreign Principals
        |
        v
Identify Cross-Domain Groups
        |
        v
Identify Cross-Domain ACLs
        |
        v
Validate Minimum Access
        |
        v
Document Security Impact
```

---

# Step 1 - Identify Domain

```powershell
Get-ADDomain
```

---

# Step 2 - Identify Forest

```powershell
Get-ADForest
```

---

# Step 3 - Enumerate Trusts

```powershell
Get-ADTrust -Filter *
```

---

# Step 4 - Record Direction

For every trust, determine:

```text
Inbound
Outbound
Bidirectional
```

from the perspective of the current domain.

---

# Step 5 - Record Type

Determine whether the relationship is:

```text
Parent-Child
Tree-Root
Forest
External
Shortcut
Realm
```

---

# Step 6 - Record Transitivity

Determine:

```text
Transitive
```

or:

```text
Non-Transitive
```

---

# Step 7 - Review Controls

Review:

```text
SID Filtering
Selective Authentication
Forest-Wide Authentication
Network Segmentation
```

---

# Step 8 - Review Foreign Principals

Identify foreign identities referenced by:

```text
Groups
ACLs
Local Administrators
Applications
File Shares
```

---

# Step 9 - Validate Access

If validation is required, use the minimum safe action.

For example:

```text
Read an Approved Test Share
```

or:

```text
Query an Approved LDAP Object
```

may be sufficient.

Do not jump directly to remote command execution.

---

# Step 10 - Document Boundary

Record exactly which security boundary was crossed.

Example:

```text
Source:
CORP.EXAMPLE

Target:
PARTNER.EXAMPLE

Trust:
One-Way Forest Trust

Authentication:
Selective Authentication Enabled

Authorisation:
CORP\App-Support granted access to PARTNER\APP01
```

---

# Trust Evidence Checklist

Record:

```text
Source Domain
Source Forest
Target Domain
Target Forest
Trust Name
Trust Type
Trust Direction
Transitivity
Trust Attributes
Selective Authentication
SID Filtering
Forest-Wide Authentication
Source Domain SID
Target Domain SID
Foreign Security Principals
Cross-Domain Group Membership
Cross-Domain ACLs
Cross-Domain Local Admin Rights
Accessible Resources
Authentication Protocol
Network Path
Timestamp
Tool
Exact Validation
```

---

# Evidence Handling

Avoid including unnecessary:

```text
Passwords
NTLM Hashes
Kerberos Tickets
Trust Secrets
Private Keys
```

in assessment evidence.

If sensitive material must be retained:

```text
Encrypt
Restrict
Redact
Delete When No Longer Required
```

---

# Trust Detection

Trust-related security monitoring should focus on:

```text
Trust Creation
Trust Modification
Cross-Domain Authentication
Foreign Privileged Membership
SIDHistory Changes
Unexpected Kerberos Referrals
Privileged Cross-Forest Logons
```

---

# Trust Modification Events

Security monitoring should detect administrative changes to trust relationships.

Relevant auditing can include:

```text
Trusted Domain Object Changes
Directory Service Changes
Administrative Activity
```

Event availability depends on audit policy and the specific modification.

---

# Event 4706

Windows Security Event:

```text
4706
```

indicates:

```text
A new trust was created to a domain
```

This should be rare and reviewed.

---

# Event 4707

Event:

```text
4707
```

indicates:

```text
A trust to a domain was removed
```

Unexpected trust removal should be investigated.

---

# Event 4716

Event:

```text
4716
```

indicates:

```text
Trusted domain information was modified
```

This is particularly important for detecting trust configuration changes.

---

# Directory Service Changes

Where Directory Service Changes auditing is configured, events such as:

```text
5136
```

may provide visibility into modifications of Active Directory objects, including relevant trust-related objects.

---

# Cross-Domain Authentication

Relevant authentication events may include:

```text
4624
4625
4648
4768
4769
4771
4776
```

depending on:

```text
Protocol
Authentication Type
Domain
Target
```

---

# Kerberos Service Tickets

Event:

```text
4769
```

can provide useful context for cross-domain Kerberos activity.

Analyse:

```text
Account
Service
Client Address
Ticket Encryption
Domain
```

in combination with trust information.

---

# Privileged Logons

Event:

```text
4672
```

may indicate assignment of special privileges to a new logon.

Cross-domain privileged logons should be correlated with:

```text
Source Domain
Source Host
Target Host
Group Membership
Business Purpose
```

---

# SIDHistory Monitoring

Changes involving:

```text
sIDHistory
```

should be tightly controlled and monitored.

Unexpected SIDHistory values can create hidden or non-obvious access relationships.

---

# Group Membership Monitoring

Monitor changes to privileged groups that introduce:

```text
Foreign Security Principals
```

or groups from trusted domains.

Important examples include:

```text
Administrators
Domain Admins
Enterprise Admins
Server Administration Groups
Application Administration Groups
```

---

# Trust Detection Model

```text
Trust Change
    |
    v
Cross-Domain Identity
    |
    v
Authentication
    |
    v
Privileged Group / ACL
    |
    v
Sensitive Resource
```

Detection should correlate these layers.

---

# Trust Hardening

A strong trust security model includes:

```text
Minimise Trusts
Use One-Way Trusts Where Possible
Limit Transitivity
Use Selective Authentication
Maintain SID Filtering
Minimise Foreign Privileged Membership
Separate Administrative Accounts
Segment Networks
Monitor Trust Changes
Review SIDHistory
Review Trusts Regularly
```

---

# Remove Unnecessary Trusts

Every trust should have:

```text
Business Owner
Technical Owner
Documented Purpose
Required Direction
Required Scope
Review Date
```

Trusts without a valid business requirement should be considered for controlled removal.

---

# Prefer One-Way Trusts

Do not create:

```text
Two-Way
```

relationships merely for convenience when:

```text
One-Way
```

access meets the requirement.

---

# Use Selective Authentication

For security-sensitive forest relationships, selective authentication can reduce the number of systems to which trusted-domain users may authenticate.

---

# Maintain SID Filtering

SID filtering provides important protection across trust boundaries.

Disabling it can significantly alter the trust's security properties.

---

# Review Foreign Privileged Membership

Regularly search for:

```text
Foreign Principal
       |
       v
Privileged Group
```

relationships.

These can silently expand the effective security boundary.

---

# Separate Privileged Identities

Avoid:

```text
One Admin Account
      |
      +--> Forest A
      +--> Forest B
      +--> Forest C
```

Prefer:

```text
Forest A Admin
Forest B Admin
Forest C Admin
```

with appropriate privileged-access controls.

---

# Network Segmentation

A trust does not require every host in both environments to communicate with every other host.

Restrict:

```text
Source
Destination
Protocol
Port
```

according to documented requirements.

---

# Trust Monitoring

Alert on:

```text
New Trust
Removed Trust
Modified Trust
SIDHistory Change
Foreign Principal Added to Privileged Group
Unexpected Cross-Forest Administrative Logon
```

---

# Periodic Trust Review

Review trust relationships periodically.

Ask:

```text
Does the Business Relationship Still Exist?

Is the Direction Still Required?

Is Two-Way Access Required?

Is Transitivity Required?

Is Selective Authentication Enabled?

Are Foreign Admin Relationships Still Required?

Are Legacy SIDHistory Values Still Required?
```

---

# Reporting Trust Findings

Do not report:

```text
Forest Trust Exists
```

as a vulnerability by itself.

Report the actual security weakness.

Examples include:

```text
Unnecessary Bidirectional Forest Trust
```

```text
Selective Authentication Not Enabled Across High-Risk Forest Trust
```

```text
Foreign Domain Group Has Excessive Administrative Rights
```

```text
Legacy Trust Remains After Migration
```

```text
Excessive Cross-Forest Administrative Dependencies
```

```text
SID Filtering Disabled Across External Trust
```

---

# Example Finding - Excessive Cross-Forest Privilege

```text
Finding:
Foreign Domain Group Has Administrative Access to Internal Servers

Description:
A security group originating from the trusted partner forest was a
member of a local administrative group used across multiple internal
servers.

The trust itself is required for business operations, but the foreign
group's administrative access was broader than necessary.

Impact:
Compromise of a member account in the trusted forest could provide
administrative access to systems in the internal forest.

This increases the security dependency between otherwise separate
forest security boundaries.

Recommendation:
Remove unnecessary foreign principals from privileged groups and
replace broad administrative assignments with role-specific access.

Use dedicated administrative identities and restrict cross-forest
authentication to systems where it is explicitly required.
```

---

# Example Finding - Unnecessary Two-Way Trust

```text
Finding:
Forest Trust Provides Unnecessary Bidirectional Authentication

Description:
A bidirectional forest trust was configured between the corporate and
partner forests.

The documented business requirement required partner users to access
specific corporate resources but did not require corporate identities
to access partner resources.

Impact:
The bidirectional relationship unnecessarily expands authentication
relationships between the two forest security boundaries.

A compromise or configuration error in either environment may
therefore have broader security implications than required by the
business use case.

Recommendation:
Review the trust design and determine whether a one-way trust can meet
the documented business requirement.

Apply selective authentication and network restrictions to further
limit cross-forest access.
```

---

# Example Finding - Selective Authentication

```text
Finding:
Broad Forest-Wide Authentication Permitted Across External Security Boundary

Description:
The forest trust allowed trusted-forest identities to authenticate
broadly to systems in the corporate forest.

Only a limited number of application servers required access from the
trusted forest.

Impact:
A compromised trusted-forest identity may be able to authenticate to a
larger number of corporate systems than required.

Although resource authorisation remains necessary, broad
authentication increases the available attack surface.

Recommendation:
Consider enabling selective authentication and grant the Allowed to
authenticate right only on systems that require cross-forest access.

Validate application compatibility before making production changes.
```

---

# Example Finding - Legacy Trust

```text
Finding:
Legacy Domain Trust Remains After Migration

Description:
An Active Directory trust remained configured with a legacy domain
that was originally used during a completed migration.

No current business application or documented operational process
required the trust.

Impact:
Unused trust relationships increase Active Directory complexity and
may preserve unnecessary authentication paths to legacy environments.

If the legacy environment is less securely maintained, compromise of
that environment may create additional risk to the production domain.

Recommendation:
Confirm the trust is no longer required with the relevant system and
business owners.

Remove the trust through the organisation's normal change-management
process and verify that no applications or identities depend on it.
```

---

# Example Finding - Cross-Domain Administrative Dependency

```text
Finding:
Privileged Administration Crosses Forest Security Boundaries

Description:
Administrative identities from one forest were used to manage Tier 0
or equivalent infrastructure in another forest.

This creates a direct privileged dependency between otherwise separate
forest security boundaries.

Impact:
Compromise of the source forest or its privileged administrative
accounts could affect the security of the target forest.

Recommendation:
Use separate privileged identities for each forest and prevent
privileged credentials from crossing forest security boundaries where
possible.

Use dedicated privileged administrative workstations and tightly
controlled management paths for Tier 0 administration.
```

---

# Trust Assessment Checklist

## Environment

- [ ] Identify current domain
- [ ] Identify forest root
- [ ] Identify all in-scope domains
- [ ] Identify all in-scope forests
- [ ] Identify domain SIDs
- [ ] Identify forest functional level
- [ ] Identify DNS relationships

## Trust Enumeration

- [ ] Run `Get-ADTrust -Filter *`
- [ ] Review `nltest /domain_trusts`
- [ ] Enumerate trustedDomain objects
- [ ] Identify source
- [ ] Identify target
- [ ] Identify direction
- [ ] Identify trust type
- [ ] Identify transitivity
- [ ] Review trust attributes

## Trust Types

- [ ] Identify parent-child trusts
- [ ] Identify tree-root trusts
- [ ] Identify forest trusts
- [ ] Identify external trusts
- [ ] Identify shortcut trusts
- [ ] Identify realm trusts
- [ ] Identify legacy trusts

## Authentication

- [ ] Determine Kerberos use
- [ ] Determine NTLM use
- [ ] Review referral behaviour
- [ ] Verify DNS
- [ ] Verify KDC reachability
- [ ] Review selective authentication
- [ ] Review forest-wide authentication

## SID Security

- [ ] Review SID filtering
- [ ] Review SIDHistory
- [ ] Identify migration-related SIDHistory
- [ ] Investigate unexpected SIDHistory
- [ ] Review trust attributes affecting SID filtering
- [ ] Do not disable filtering for testing

## Foreign Principals

- [ ] Enumerate ForeignSecurityPrincipals
- [ ] Identify foreign users
- [ ] Identify foreign groups
- [ ] Review domain local groups
- [ ] Review universal groups
- [ ] Review nested membership
- [ ] Identify privileged foreign principals

## Privilege

- [ ] Review local Administrators
- [ ] Review server administration groups
- [ ] Review application administrators
- [ ] Review backup administrators
- [ ] Review remote-management groups
- [ ] Review cross-domain ACLs
- [ ] Review Group Policy assignments
- [ ] Review service accounts
- [ ] Review Tier 0 access

## Network

- [ ] Identify cross-domain network paths
- [ ] Identify cross-forest network paths
- [ ] Review workstation-to-forest access
- [ ] Review management network access
- [ ] Review DNS access
- [ ] Review Kerberos access
- [ ] Review LDAP access
- [ ] Review SMB access
- [ ] Review RPC access
- [ ] Review RDP access
- [ ] Review WinRM access

## Safe Validation

- [ ] Confirm remote domain is in scope
- [ ] Confirm remote forest is in scope
- [ ] Use approved identity
- [ ] Prefer read-only validation
- [ ] Validate minimum required resource
- [ ] Avoid remote execution unless necessary
- [ ] Avoid trust modification
- [ ] Avoid SID filtering changes
- [ ] Avoid SIDHistory changes
- [ ] Stop after sufficient evidence

## Detection

- [ ] Monitor 4706
- [ ] Monitor 4707
- [ ] Monitor 4716
- [ ] Monitor 5136 where applicable
- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4648
- [ ] Monitor 4672
- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Monitor 4771
- [ ] Monitor 4776
- [ ] Monitor foreign privileged membership
- [ ] Monitor SIDHistory changes
- [ ] Monitor cross-forest administrative logons
- [ ] Monitor trust-object modifications

## Hardening

- [ ] Remove unnecessary trusts
- [ ] Prefer one-way trusts where possible
- [ ] Minimise transitivity
- [ ] Enable selective authentication where appropriate
- [ ] Maintain SID filtering
- [ ] Minimise foreign privileged membership
- [ ] Separate forest administrator identities
- [ ] Restrict network paths
- [ ] Protect Tier 0
- [ ] Review legacy migration configuration
- [ ] Review trusts periodically
- [ ] Assign business and technical owners

## Reporting

- [ ] Do not report trust existence alone
- [ ] Identify actual configuration weakness
- [ ] Record trust direction correctly
- [ ] Record trust type
- [ ] Record transitivity
- [ ] Record security controls
- [ ] Identify affected principals
- [ ] Identify affected resources
- [ ] Explain security-boundary impact
- [ ] Provide targeted remediation

---

# Trust Testing Model

The basic trust model is:

```text
Trusted Domain
      |
      v
Trusting Domain
```

The authentication model is:

```text
Trusted Identity
      |
      v
Trust
      |
      v
Authentication
      |
      v
Trusting Domain
```

The authorisation model is:

```text
Foreign Identity
      |
      v
Trust
      |
      v
Authentication
      |
      v
Group / ACL
      |
      v
Resource
```

The one-way model is:

```text
Domain A
trusts
Domain B

Domain B User
      |
      v
Domain A Resource
```

The two-way model is:

```text
Domain A
   <---->
Domain B
```

The forest model is:

```text
Forest A
   |
   | Forest Trust
   |
   v
Forest B
```

The selective-authentication model is:

```text
Foreign Identity
      |
      v
Trust
      |
      v
Allowed to Authenticate?
      |
      +--> No --> Stop
      |
      +--> Yes
             |
             v
      Resource ACL
```

The SID-filtering model is:

```text
Authentication Token
       |
       v
SID Filtering
       |
       +--> Valid SIDs
       |
       X
       |
       +--> Disallowed SIDs
```

The group-membership model is:

```text
Foreign User
     |
     v
Foreign Group
     |
     v
Domain Local Group
     |
     v
Permission
     |
     v
Resource
```

The Kerberos referral model is:

```text
User
 |
 v
Source KDC
 |
 v
Trust Referral
 |
 v
Target KDC
 |
 v
Service Ticket
 |
 v
Target Service
```

The cross-forest privilege model is:

```text
Forest A Identity
       |
       v
Trust
       |
       v
Forest B Privileged Group
       |
       v
Forest B Server
```

The defensive model is:

```text
Minimum Trust Direction
        +
Selective Authentication
        +
SID Filtering
        +
Minimal Foreign Privilege
        +
Network Segmentation
        +
Separate Admin Identities
        +
Monitoring
        =
Reduced Cross-Boundary Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I see another domain?"

Ask:
"What security dependency does this trust
create between the two environments?"
```

For defenders:

```text
Do Not Ask:
"Do we need the trust?"

Ask:
"What is the minimum trust direction,
authentication scope and privilege required
to satisfy the business requirement?"
```

The complete relationship is:

```text
Business Requirement
       |
       v
Trust
       |
       v
Authentication Boundary
       |
       v
Group / ACL
       |
       v
Resource Access
       |
       v
Cross-Boundary Security Dependency
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Active Directory Enumeration:

[Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

NTLM:

[NTLM](ntlm.md)

Groups:

[Groups](groups.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Group Policy:

[Group Policy](group-policy.md)

BloodHound:

[BloodHound](bloodhound.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

Pivoting:

[Pivoting](pivoting.md)

SMB:

[SMB](smb.md)

WinRM:

[WinRM](winrm.md)

WMI:

[WMI](wmi.md)

DCOM:

[DCOM](dcom.md)

gMSA:

[gMSA](gmsa.md)

Active Directory Certificate Services:

[Active Directory Certificate Services](ad-cs/index.md)

The next trust-specific page should cover:

```text
docs/active-directory/trust-relationships.md
```

followed by:

```text
docs/active-directory/sid-history.md
docs/active-directory/trust-tickets.md
```

---

# References

## Microsoft - How Domains and Forests Work

[Microsoft - How Domains and Forests Work](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc759073(v=ws.10)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Forest Design Models

[Microsoft - Forest Design Models](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/forest-design-models){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADTrust

[Microsoft - Get-ADTrust](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adtrust){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADForest

[Microsoft - Get-ADForest](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adforest){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADDomain

[Microsoft - Get-ADDomain](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomain){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - NLTest

[Microsoft - NLTest](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/nltest){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Selective Authentication

[Microsoft - Selective Authentication](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc755321(v=ws.10)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SID Filtering

[Microsoft - Security Considerations for Trusts](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc755321(v=ws.10)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4706

[Microsoft - 4706 A New Trust Was Created to a Domain](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4706){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4707

[Microsoft - 4707 A Trust to a Domain Was Removed](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4707){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4716

[Microsoft - 4716 Trusted Domain Information Was Modified](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4716){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## PowerView

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

PowerSploit is an older project and should be treated accordingly when comparing examples with current Windows and Active Directory environments.

---

## MITRE ATT&CK - Account Discovery: Domain Account

[MITRE ATT&CK - T1087.002 Domain Account](https://attack.mitre.org/techniques/T1087/002/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Permission Groups Discovery: Domain Groups

[MITRE ATT&CK - T1069.002 Domain Groups](https://attack.mitre.org/techniques/T1069/002/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Active Directory trusts are:

```text
Authentication Relationships
```

not automatic:

```text
Administrative Relationships
```

The correct analysis is therefore not:

```text
Trust Exists
   |
   v
Vulnerable
```

Instead:

```text
Trust Exists
   |
   v
What Direction?
   |
   v
What Type?
   |
   v
What Transitivity?
   |
   v
What Authentication Scope?
   |
   v
What SID Controls?
   |
   v
Which Foreign Principals?
   |
   v
Which Groups and ACLs?
   |
   v
Which Resources?
   |
   v
What Security Impact?
```

A forest should generally be treated as the primary Active Directory security boundary.

When separate forests are connected, carefully evaluate:

```text
Trust Direction
Selective Authentication
SID Filtering
Foreign Privileged Membership
Administrative Accounts
Network Connectivity
Tier 0 Dependencies
```

A trust can be technically configured correctly while still creating unnecessary risk through:

```text
Broad Group Membership
Excessive ACLs
Shared Administrators
Unrestricted Network Paths
Legacy Migration Configuration
```

Likewise, discovering a trust to another organisation does not extend the penetration-testing scope.

The safe workflow remains:

```text
Discover
   |
   v
Understand
   |
   v
Check Scope
   |
   v
Map Authentication
   |
   v
Map Authorisation
   |
   v
Validate Minimum Access
   |
   v
Report the Actual Weakness
```

For high-security forest relationships, the target architecture should move toward:

```text
Minimum Required Trust
        |
        v
One-Way Where Possible
        |
        v
Selective Authentication
        |
        v
SID Filtering
        |
        v
Minimal Foreign Privilege
        |
        v
Restricted Network Access
        |
        v
Separate Privileged Administration
```

The next page drills further into how individual trust relationships are structured and interpreted:

```text
Trust Relationships
```
