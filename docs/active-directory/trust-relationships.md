# Active Directory Trust Relationships

Active Directory trust relationships define how authentication can cross domain and forest boundaries.

The general trust model is:

```text
Identity
   |
   v
Source Domain
   |
   v
Trust Relationship
   |
   v
Target Domain
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

Trust relationships are commonly encountered in environments containing:

```text
Parent and Child Domains
Multiple Domain Trees
Multiple Forests
Mergers and Acquisitions
Legacy Domains
Partner Organisations
Resource Forests
Migration Environments
Kerberos Realms
```

Understanding the existence of a trust is only the beginning.

A complete assessment should determine:

```text
Source
Target
Direction
Type
Transitivity
Authentication Scope
SID Filtering
Trust Attributes
Foreign Principals
Cross-Domain Groups
Cross-Domain ACLs
Network Reachability
Actual Resource Access
```

!!! warning "Authorised testing only"
    Discovering a trusted domain or forest does not automatically place that environment within the penetration-testing scope. Treat every newly discovered domain, forest and organisation as a separate scope boundary until the rules of engagement explicitly confirm otherwise.

---

# Trust Relationships at a Glance

Suppose two domains exist:

```text
CORP.EXAMPLE
PARTNER.EXAMPLE
```

A trust might connect them:

```text
CORP.EXAMPLE
      |
      | Trust
      |
      v
PARTNER.EXAMPLE
```

But the security implications depend on:

```text
Who Trusts Whom?
Is It One-Way or Two-Way?
Is It Transitive?
Is It Intra-Forest or Cross-Forest?
Is Selective Authentication Enabled?
Is SID Filtering Applied?
Which Foreign Principals Have Permissions?
```

---

# Trusting and Trusted Domains

Trust terminology can initially appear backwards.

If:

```text
DOMAIN-A
trusts
DOMAIN-B
```

then:

```text
DOMAIN-A
=
Trusting Domain
```

and:

```text
DOMAIN-B
=
Trusted Domain
```

DOMAIN-A accepts authentication originating from DOMAIN-B.

---

# Authentication Direction

Therefore:

```text
DOMAIN-A trusts DOMAIN-B
```

allows the relationship:

```text
DOMAIN-B User
      |
      v
DOMAIN-A Resource
```

subject to authorisation.

A useful mental model is:

```text
Trust Arrow:
Resource Domain -> Identity Domain

Potential Access:
Identity Domain -> Resource Domain
```

---

# One-Way Trust

A one-way trust establishes trust in one direction.

Example:

```text
CORP.EXAMPLE
      |
      | trusts
      v
PARTNER.EXAMPLE
```

The potential authentication path is:

```text
PARTNER.EXAMPLE\User
          |
          v
CORP.EXAMPLE\Resource
```

CORP trusts identities from PARTNER.

PARTNER does not automatically trust identities from CORP.

---

# Two-Way Trust

A two-way trust establishes both directions:

```text
CORP.EXAMPLE
      <---->
PARTNER.EXAMPLE
```

Potential authentication relationships exist in both directions:

```text
CORP User
    |
    v
PARTNER Resource
```

and:

```text
PARTNER User
      |
      v
CORP Resource
```

Actual access still depends on authorisation.

---

# Trust Direction from the Querying Domain

Tools commonly report:

```text
Inbound
Outbound
Bidirectional
```

The meaning must be interpreted relative to the domain being queried.

This is one of the most important details to record correctly during trust enumeration.

---

# Inbound Trust

From the perspective of the current domain, an inbound trust generally means that the current domain trusts identities from the other domain.

Conceptually:

```text
Other Domain
     |
     | Identity
     v
Current Domain
```

Foreign identities may therefore be able to access resources in the current domain if authorised.

---

# Outbound Trust

From the perspective of the current domain, an outbound trust generally means the other domain trusts the current domain.

Conceptually:

```text
Current Domain
     |
     | Identity
     v
Other Domain
```

Users from the current domain may therefore be accepted by the other domain.

---

# Bidirectional Trust

A bidirectional trust combines both relationships:

```text
Current Domain
      <---->
Other Domain
```

---

# Why Direction Matters

Suppose an assessment identifies:

```text
CORP.EXAMPLE
```

and:

```text
ADMIN.EXAMPLE
```

A trust exists.

That alone does not answer:

```text
Can CORP users access ADMIN resources?
```

The direction must first be understood.

---

# Trust Type

Trust relationships also have a type.

Common Active Directory relationships include:

```text
Parent-Child
Tree-Root
Shortcut
External
Forest
Realm
```

The type affects:

```text
Transitivity
Scope
Authentication
Security Boundary
SID Filtering
```

---

# Parent-Child Relationships

A child domain automatically establishes a trust with its parent.

Example:

```text
corp.example
     |
     v
emea.corp.example
```

The relationship is normally:

```text
Two-Way
Transitive
Intra-Forest
```

---

# Parent-Child Authentication

Conceptually:

```text
emea.corp.example
        |
        v
corp.example
```

and:

```text
corp.example
        |
        v
emea.corp.example
```

can use the forest's trust infrastructure for authentication referrals.

---

# Tree-Root Relationships

A forest can contain multiple domain trees.

Example:

```text
             Forest
               |
       +-------+-------+
       |               |
corp.example      services.example
```

The root domains of separate trees within the same forest have a:

```text
Tree-Root Trust
```

which is normally:

```text
Two-Way
Transitive
```

---

# Shortcut Trusts

Large forests may contain long authentication paths.

Example:

```text
Domain A
   |
   v
Domain B
   |
   v
Domain C
   |
   v
Domain D
```

A shortcut trust may be created:

```text
Domain A
   |
   +------------------+
                      |
                      v
                   Domain D
```

This can reduce the Kerberos referral path.

---

# External Trusts

An external trust connects specific domains without establishing a forest-wide relationship.

Example:

```text
CORP.EXAMPLE
      |
      | External Trust
      |
      v
LEGACY.EXAMPLE
```

External trusts are generally:

```text
Non-Transitive
```

---

# Forest Trusts

A forest trust connects two Active Directory forests.

```text
Forest A
   |
   | Forest Trust
   |
   v
Forest B
```

Forest trusts can be:

```text
One-Way
Two-Way
```

and are important because they connect separate Active Directory security boundaries.

---

# Realm Trusts

Realm trusts connect Active Directory to a non-Windows Kerberos realm.

```text
Active Directory
       |
       v
Realm Trust
       |
       v
Kerberos Realm
```

Realm trusts may be:

```text
One-Way
Two-Way
Transitive
Non-Transitive
```

depending on configuration.

---

# Transitivity

Transitivity determines whether the trust relationship can extend through additional domains.

Consider:

```text
Domain A
   |
   v
Domain B
   |
   v
Domain C
```

If the relevant relationships are transitive, authentication relationships may extend beyond the directly connected pair.

---

# Transitive Trust

Conceptually:

```text
A trusts B
B trusts C
```

may allow a trust path involving:

```text
A
|
B
|
C
```

depending on the trust types and forest topology.

---

# Non-Transitive Trust

With a non-transitive relationship:

```text
A trusts B
```

does not automatically mean:

```text
A trusts domains trusted by B
```

This can significantly reduce the trust scope.

---

# Intra-Forest Relationships

Domains within the same forest have particularly strong relationships.

Common intra-forest trusts include:

```text
Parent-Child
Tree-Root
Shortcut
```

---

# Forest Security Boundary

A critical Active Directory principle is:

```text
Forest
=
Primary Security Boundary
```

Domains within a forest should not normally be treated as independent security boundaries against a sufficiently privileged compromise elsewhere in that forest.

---

# Domain Boundary vs Forest Boundary

A domain provides important:

```text
Administrative
Policy
Replication
Naming
```

boundaries.

However:

```text
Domain
!=
Strong Isolation Boundary
```

within the same forest.

---

# Cross-Forest Relationship

A trust between forests is different:

```text
Forest A
   |
   v
Trust Boundary
   |
   v
Forest B
```

Security controls such as:

```text
SID Filtering
Selective Authentication
Network Segmentation
Separate Administration
```

become particularly important.

---

# Trust Relationship Enumeration

A useful workflow is:

```text
Current Domain
      |
      v
Current Forest
      |
      v
Known Domains
      |
      v
Trust Objects
      |
      v
Direction
      |
      v
Type
      |
      v
Transitivity
      |
      v
Security Attributes
      |
      v
Foreign Principals
      |
      v
Actual Access
```

---

# Current Domain

Using the ActiveDirectory PowerShell module:

```powershell
Get-ADDomain
```

Useful properties include:

```text
DNSRoot
NetBIOSName
DomainSID
Forest
ParentDomain
ChildDomains
DomainMode
```

---

# Current Forest

```powershell
Get-ADForest
```

Useful properties include:

```text
Name
RootDomain
Domains
GlobalCatalogs
ForestMode
DomainNamingMaster
SchemaMaster
```

---

# Enumerate Forest Domains

```powershell
Get-ADForest | Select-Object -ExpandProperty Domains
```

---

# Native Windows Trust Enumeration

`nltest.exe` provides native trust enumeration.

```cmd
nltest /domain_trusts
```

For broader trust information:

```cmd
nltest /domain_trusts /all_trusts
```

---

# ActiveDirectory Module

Enumerate trusts:

```powershell
Get-ADTrust -Filter *
```

Focused output:

```powershell
Get-ADTrust -Filter * |
    Select-Object Name,Source,Target,Direction,TrustType,ForestTransitive,IntraForest,SelectiveAuthentication
```

---

# Query a Specific Relationship

```powershell
Get-ADTrust -Identity 'partner.example'
```

This is useful when investigating one known relationship.

---

# Trust Object Properties

Important properties can include:

```text
Source
Target
Direction
TrustType
ForestTransitive
IntraForest
SelectiveAuthentication
SIDFilteringForestAware
SIDFilteringQuarantined
```

The exact properties available depend on the environment and tooling.

---

# PowerView Trust Enumeration

PowerView versions commonly provide functions such as:

```powershell
Get-DomainTrust
```

Check first:

```powershell
Get-Command Get-DomainTrust -ErrorAction SilentlyContinue
```

If available:

```powershell
Get-DomainTrust
```

---

# Trust Mapping with PowerView

Some PowerView versions provide:

```powershell
Get-DomainTrustMapping
```

Verify before use:

```powershell
Get-Command Get-DomainTrustMapping -ErrorAction SilentlyContinue
```

Then:

```powershell
Get-DomainTrustMapping
```

Do not allow automated mapping to extend testing into out-of-scope domains.

---

# LDAP Trust Enumeration

Trusts are represented by:

```text
trustedDomain
```

objects.

They are commonly stored under:

```text
CN=System
```

in the domain naming context.

---

# LDAP Example

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=System,DC=corp,DC=example' \
  '(objectClass=trustedDomain)' \
  cn flatName trustPartner trustDirection trustType trustAttributes securityIdentifier
```

---

# Trusted Domain Object

A trustedDomain object may contain:

```text
cn
flatName
trustPartner
trustDirection
trustType
trustAttributes
securityIdentifier
```

These values can be used to reconstruct the relationship.

---

# trustPartner

`trustPartner` identifies the DNS name associated with the trusted domain.

Example:

```text
partner.example
```

---

# flatName

`flatName` commonly represents the NetBIOS-style name.

Example:

```text
PARTNER
```

---

# securityIdentifier

The:

```text
securityIdentifier
```

attribute can identify the SID associated with the trusted domain.

This can be useful when interpreting:

```text
Foreign Security Principals
SIDHistory
Cross-Domain ACLs
```

---

# trustDirection

Common numeric values are:

```text
0 = Disabled
1 = Inbound
2 = Outbound
3 = Bidirectional
```

Always interpret them relative to the domain containing the trustedDomain object.

---

# trustType

Common values include:

```text
1 = Downlevel / legacy Windows trust
2 = Active Directory trust
3 = MIT Kerberos realm
```

Trust type should be interpreted together with:

```text
trustAttributes
```

rather than in isolation.

---

# trustAttributes

`trustAttributes` is a bit field.

Depending on configuration, flags can represent characteristics such as:

```text
Non-Transitive
Uplevel
Quarantined Domain
Forest Transitive
Cross Organisation
Within Forest
Treat As External
Uses RC4 Encryption
Cross Organisation No TGT Delegation
PIM Trust
```

Multiple flags may be present simultaneously.

---

# Do Not Guess Trust Attributes

Instead of manually interpreting an unfamiliar decimal value during an assessment:

```text
Record Raw Value
      |
      v
Decode Flags
      |
      v
Confirm with Additional Tooling
```

Use multiple data sources where practical.

---

# LDAP and PowerShell Correlation

A useful workflow is:

```text
Get-ADTrust
     |
     v
High-Level Relationship
     |
     v
LDAP trustedDomain
     |
     v
Underlying Attributes
```

This provides both:

```text
Readable Interpretation
```

and:

```text
Raw Directory Data
```

---

# NetExec

NetExec can help establish:

```text
Domain
Hostname
Authentication Context
```

during broader Active Directory enumeration.

Check current options:

```bash
nxc ldap -h
```

A basic LDAP authentication check against an authorised DC may look like:

```bash
nxc ldap dc01.corp.example -u 'audituser' -p 'PASSWORD'
```

Use password prompting or other protected credential handling where practical.

---

# BloodHound Trust Mapping

BloodHound is particularly useful because a trust should rarely be analysed by itself.

See:

[BloodHound](bloodhound.md)

The more useful graph is often:

```text
Trust
  +
Group Membership
  +
ACL
  +
Session
  +
Administrative Rights
```

---

# BloodHound Relationship Model

Example:

```text
PARTNER\User
      |
      v
PARTNER\Helpdesk
      |
      v
CORP\Server-Support
      |
      v
AdminTo
      |
      v
CORP\APP01
```

The important finding is not simply:

```text
PARTNER trusts CORP
```

but the resulting privilege path.

---

# Foreign Security Principals

Foreign identities referenced in another domain can be represented by:

```text
ForeignSecurityPrincipal
```

objects.

These commonly exist under:

```text
CN=ForeignSecurityPrincipals
```

---

# Foreign Principal Model

```text
Foreign Domain
      |
      v
Foreign SID
      |
      v
ForeignSecurityPrincipal
      |
      v
Local Domain Group
      |
      v
Permission
```

---

# Enumerate Foreign Security Principals

Example:

```powershell
Get-ADObject `
    -SearchBase 'CN=ForeignSecurityPrincipals,DC=corp,DC=example' `
    -LDAPFilter '(objectClass=foreignSecurityPrincipal)' `
    -Properties objectSid
```

This is read-only enumeration.

---

# Resolve Foreign SIDs

A foreign principal may initially appear as:

```text
S-1-5-21-...
```

Resolution may require communication with the domain responsible for that SID.

Do not query an out-of-scope trusted domain merely to resolve the identity.

---

# Cross-Domain Group Membership

One of the highest-value trust checks is:

```text
Foreign Principal
      |
      v
Local Group
      |
      v
Privilege
```

---

# Domain Local Groups

Domain Local groups are particularly important because they can grant permissions to resources in the local domain while containing identities from trusted domains.

Example:

```text
PARTNER\App-Team
        |
        v
CORP\App-Server-Admins
        |
        v
APP01
```

---

# Enumerate Group Membership

For an authorised group:

```powershell
Get-ADGroupMember -Identity 'App-Server-Admins'
```

Recursive:

```powershell
Get-ADGroupMember -Identity 'App-Server-Admins' -Recursive
```

Investigate unexpected foreign identities.

---

# Universal Groups

Universal groups can span domains within a forest.

This creates paths such as:

```text
Domain A Global Group
        |
        v
Universal Group
        |
        v
Domain B Domain Local Group
        |
        v
Permission
```

---

# AGDLP

A common permissions model is:

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
A -> G -> DL -> P
```

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
A -> G -> U -> DL -> P
```

Trust assessment should therefore follow nested group relationships rather than looking only for direct assignments.

---

# Cross-Domain ACLs

Foreign principals can also appear directly in Active Directory ACLs.

Example:

```text
PARTNER\Helpdesk
       |
       v
GenericWrite
       |
       v
CORP\ServiceAccount
```

See:

[ACL and ACE](acl-ace.md)

---

# Cross-Domain ACL Model

```text
Foreign Identity
      |
      v
Trust
      |
      v
Directory ACL
      |
      v
Object Control
```

This can create a privilege path without any obvious foreign membership in a privileged group.

---

# Local Group Relationships

Foreign groups can also be members of local Windows groups.

Example:

```text
PARTNER\ServerAdmins
          |
          v
APP01\Administrators
```

This can provide direct administrative access to the target.

---

# Enumerate Local Administrators

Where authorised on the target:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

Look for:

```text
Foreign Domain Users
Foreign Domain Groups
Unexpected Domain Groups
```

---

# Trust Authentication

A trust primarily enables authentication.

Authorisation remains separate.

```text
Foreign Identity
      |
      v
Trust
      |
      v
Authenticated
      |
      v
ACL / Group
      |
      v
Authorised?
```

---

# Kerberos Referrals

Kerberos commonly handles cross-domain authentication using referrals.

Conceptually:

```text
User
 |
 v
Source KDC
 |
 v
Referral TGT
 |
 v
Target KDC
 |
 v
Service Ticket
 |
 v
Service
```

---

# Example Referral Path

Suppose:

```text
alice@EMEA.CORP.EXAMPLE
```

requests access to:

```text
cifs/files01.corp.example
```

The source KDC may provide a referral toward:

```text
CORP.EXAMPLE
```

The destination KDC can then issue the required service ticket if authentication and trust requirements are satisfied.

---

# Inspect Tickets

Windows:

```cmd
klist
```

Linux:

```bash
klist
```

Cross-domain authentication may result in referral-related tickets appearing in the cache.

See:

[Kerberos Tickets](kerberos-tickets.md)

---

# DNS Requirements

Trust relationships depend heavily on working name resolution.

Cross-domain DNS may use:

```text
Conditional Forwarders
Stub Zones
Delegation
Forest-Wide DNS
Other Enterprise DNS Integration
```

---

# Query Domain Controllers

Linux:

```bash
dig _ldap._tcp.dc._msdcs.partner.example SRV
```

Kerberos:

```bash
dig _kerberos._tcp.partner.example SRV
```

Windows:

```powershell
Resolve-DnsName -Type SRV '_ldap._tcp.dc._msdcs.partner.example'
```

Only perform remote-domain queries when within scope.

---

# Network Requirements

A correctly configured trust can still be unusable if network communication is blocked.

The complete model is:

```text
Trust
  +
DNS
  +
Network Reachability
  +
Authentication
  +
Authorisation
  =
Resource Access
```

---

# Trust Without Network Reachability

Example:

```text
Forest A
   |
   | Trust
   |
Forest B

Workstation A
     |
     X
     |
Server B
```

The trust exists, but the workstation cannot reach the remote service.

This can be an effective security control.

---

# Selective Authentication

Selective authentication adds another security decision to cross-boundary authentication.

Without selective authentication:

```text
Foreign Identity
      |
      v
Trust
      |
      v
Resource Authentication
```

With selective authentication:

```text
Foreign Identity
      |
      v
Trust
      |
      v
Allowed to Authenticate?
      |
      +--> No
      |
      +--> Yes
             |
             v
      Resource Authentication
```

---

# Enumerate Selective Authentication

```powershell
Get-ADTrust -Filter * |
    Select-Object Name,Direction,SelectiveAuthentication
```

---

# Allowed to Authenticate

When selective authentication is enabled, foreign identities require appropriate:

```text
Allowed to authenticate
```

rights on the relevant computer or service security principal.

This limits where foreign users may authenticate.

---

# Selective Authentication Benefit

Instead of:

```text
Partner Forest
      |
      v
Authenticate to Entire Corporate Forest
```

the environment can move toward:

```text
Partner Forest
      |
      v
Approved Application Servers Only
```

---

# SID Filtering

SID filtering protects trust boundaries from inappropriate SID information crossing the relationship.

Conceptually:

```text
Incoming Token
     |
     v
SID Filtering
     |
     +--> Permitted SID
     |
     X
     |
     +--> Filtered SID
```

---

# Why SID Filtering Matters

An access token can contain multiple SIDs.

These may include:

```text
Primary SID
Group SIDs
SIDHistory
```

The receiving environment must determine which SID information is valid across the trust boundary.

---

# SIDHistory

SIDHistory supports migrations by allowing a new account to retain an old SID.

Example:

```text
New Account
SID: NEW-SID

SIDHistory:
OLD-SID
```

An existing ACL referencing:

```text
OLD-SID
```

can continue to authorise the migrated account.

---

# SIDHistory and Trust Relationships

Trust analysis should therefore ask:

```text
Is SIDHistory Present?

Why Is It Present?

Is It Migration Related?

Is It Still Required?

How Does SID Filtering Treat It?
```

The dedicated page covers this in more detail:

```text
docs/active-directory/sid-history.md
```

---

# Trust Relationships and SID Filtering

Different trust types can have different SID-filtering behaviour.

Do not make assumptions based only on:

```text
External
```

or:

```text
Forest
```

labels.

Inspect the actual:

```text
Trust Attributes
SID Filtering State
Migration Requirements
```

---

# Trust Attributes and Security

Trust attributes can materially alter security behaviour.

Examples include characteristics related to:

```text
Forest Transitivity
SID Filtering
Treat-As-External
TGT Delegation
PIM Trust
Encryption Compatibility
```

These settings should be documented during high-value trust assessments.

---

# Treat-As-External

A forest trust can have behaviour altered so that it is treated more like an external trust for certain SID-filtering decisions.

This is security-sensitive configuration and should not be modified during testing.

---

# TGT Delegation Across Trusts

Kerberos delegation across trust boundaries requires careful security consideration.

Trust configuration can affect whether:

```text
Ticket Granting Tickets
```

may be delegated across an organisation boundary.

This becomes especially important for:

```text
Unconstrained Delegation
Cross-Forest Authentication
Privileged Accounts
```

See:

[Unconstrained Delegation](unconstrained-delegation.md)

---

# Cross-Organisation Trusts

Trust relationships connecting separate organisations should receive additional scrutiny.

Example:

```text
Company A
   |
   | Trust
   |
Company B
```

This creates a technical security dependency between organisations.

---

# Mergers and Acquisitions

Trusts are frequently created during:

```text
Acquisition
Migration
Consolidation
```

A common lifecycle is:

```text
Separate Forests
      |
      v
Temporary Trust
      |
      v
Migration
      |
      v
Migration Completed
      |
      v
Trust Should Be Reviewed
```

Temporary relationships sometimes become permanent through operational inertia.

---

# Legacy Trust Risk

A legacy forest may have:

```text
Older Operating Systems
Weak Password Policies
Legacy NTLM
Unsupported Applications
Reduced Monitoring
Broader Administrator Access
```

If that forest is trusted by production infrastructure, its compromise may affect the stronger environment.

---

# Security Dependency

Trust analysis should therefore measure:

```text
Security Dependency
```

not merely:

```text
Connectivity
```

Example:

```text
Production Forest
      |
      | trusts
      v
Legacy Forest
```

If legacy identities have privileged production access:

```text
Legacy Forest Security
        |
        v
Production Forest Security
```

becomes an important dependency.

---

# Cross-Forest Administrative Access

Particularly dangerous relationships include:

```text
Forest A Administrator
        |
        v
Forest B Domain Controller
```

or:

```text
Forest A Group
        |
        v
Forest B Tier 0 System
```

Separate forests provide limited security value if their privileged administration is tightly interconnected.

---

# Tier 0 Relationships

Pay particular attention to foreign identities with access to:

```text
Domain Controllers
AD CS
ADFS
Privileged Access Systems
Identity Synchronisation
Backup Infrastructure
Virtualisation Platforms Hosting DCs
```

These can effectively provide control over the identity plane.

---

# Enterprise Admins

Within a forest:

```text
Enterprise Admins
```

is a forest-wide privileged group located in the forest root domain.

Compromise of Enterprise Admin-level control should generally be considered:

```text
Forest Compromise
```

---

# Schema Admins

```text
Schema Admins
```

can modify the forest-wide Active Directory schema.

Membership should be tightly controlled.

---

# Trusts and AD CS

Trust relationships can affect certificate-based authentication and resource access.

Review:

```text
CA Location
Forest Membership
Enrollment Permissions
Certificate Mapping
Authentication Trust
Cross-Forest Access
```

See:

[Active Directory Certificate Services](ad-cs/index.md)

---

# Trusts and Lateral Movement

A trust can create a path:

```text
Compromised Identity
       |
       v
Trusted Domain
       |
       v
Cross-Domain Group
       |
       v
Remote Administration
       |
       v
Target System
```

See:

[Lateral Movement](lateral-movement.md)

---

# Trusts and SMB

Example:

```text
PARTNER\User
      |
      v
CORP\File-Access
      |
      v
FILE01
```

See:

[SMB](smb.md)

---

# Trusts and WinRM

A foreign identity may have:

```text
Remote Management Users
```

or administrative rights on a system in another domain.

See:

[WinRM](winrm.md)

---

# Trusts and WMI

Administrative cross-domain relationships may permit remote WMI.

See:

[WMI](wmi.md)

---

# Trusts and DCOM

The same excessive administrative relationship may permit DCOM.

See:

[DCOM](dcom.md)

---

# Trusts and Pivoting

A trust relationship does not guarantee a network path.

A pivot may be required to reach resources in the remote domain.

See:

[Pivoting](pivoting.md)

---

# Trusts and BloodHound

BloodHound can combine:

```text
Trust
Group Membership
ACL
Session
Local Administrator
Remote Management
```

relationships into a single graph.

This is usually more valuable than viewing the trust in isolation.

---

# Trusts and Group Policy

Cross-domain administrative relationships may be delivered through:

```text
Group Policy
Restricted Groups
Group Policy Preferences
Local Group Policy Configuration
```

See:

[Group Policy](group-policy.md)

---

# Trusts and Service Accounts

Cross-domain service dependencies should also be reviewed.

Examples:

```text
Backup Service
Monitoring Service
SQL Service
Application Service
Scheduled Task
Deployment Service
```

A highly privileged service account crossing a forest boundary can create a significant security dependency.

---

# Trust Relationships and Authentication Protocols

Do not assume all cross-domain access uses Kerberos.

Depending on the environment, authentication may involve:

```text
Kerberos
NTLM
```

The actual protocol should be determined from:

```text
Ticket Cache
Authentication Logs
Network Context
Application Behaviour
```

---

# Kerberos Preferred

For normal modern Active Directory environments:

```text
Kerberos
```

should generally be preferred over NTLM where supported.

Cross-domain Kerberos relies on:

```text
DNS
KDC Discovery
Trust
SPNs
Time
```

---

# NTLM Fallback

NTLM may appear when:

```text
Kerberos Cannot Be Used
Legacy Application
IP Address Used
SPN Problem
DNS Problem
Application Limitation
```

See:

[NTLM](ntlm.md)

---

# Trust Validation

A safe trust validation does not require administrative compromise.

A simple authorised test might validate:

```text
Foreign User
      |
      v
Trust Authentication
      |
      v
Approved Test Resource
```

Examples include:

```text
LDAP Read
Test File Share
Approved Application
```

---

# Minimal Validation Principle

Prefer:

```text
Can the approved account read the approved resource?
```

over:

```text
Can the approved account execute commands remotely?
```

unless command execution is specifically required to demonstrate the risk.

---

# Safe Trust Assessment Workflow

```text
Identify Domain
      |
      v
Identify Forest
      |
      v
Enumerate Trust
      |
      v
Interpret Direction
      |
      v
Interpret Type
      |
      v
Interpret Transitivity
      |
      v
Review Security Attributes
      |
      v
Confirm Scope
      |
      v
Enumerate Foreign Principals
      |
      v
Map Group Membership
      |
      v
Map ACLs
      |
      v
Map Network Reachability
      |
      v
Validate Minimum Access
      |
      v
Report Security Dependency
```

---

# Step 1 - Domain

```powershell
Get-ADDomain
```

---

# Step 2 - Forest

```powershell
Get-ADForest
```

---

# Step 3 - Trusts

```powershell
Get-ADTrust -Filter *
```

---

# Step 4 - Native Verification

```cmd
nltest /domain_trusts /all_trusts
```

---

# Step 5 - LDAP Verification

Query:

```text
(objectClass=trustedDomain)
```

under:

```text
CN=System
```

---

# Step 6 - Scope Check

Before contacting a newly discovered environment:

```text
Is Target Domain In Scope?
        |
        +--> No --> Record and Stop
        |
        +--> Yes --> Continue
```

---

# Step 7 - Foreign Principals

Review:

```text
ForeignSecurityPrincipals
Domain Local Groups
Universal Groups
Local Administrators
ACLs
```

---

# Step 8 - Security Controls

Review:

```text
Selective Authentication
SID Filtering
Network Segmentation
Administrative Separation
```

---

# Step 9 - Minimal Access Test

Validate only the access necessary to demonstrate the relationship.

---

# Step 10 - Evidence

Record:

```text
Source Domain
Target Domain
Source Forest
Target Forest
Trust Direction
Trust Type
Transitivity
Trust Attributes
Authentication Scope
SID Filtering
Foreign Principal
Group
Resource
Access Level
```

---

# Trust Relationship Evidence Checklist

Record:

```text
Current Domain
Current Forest
Forest Root
Trusted Domain
Trusted Forest
Trusting Domain
Trust Direction
Trust Type
Transitivity
Intra-Forest Status
Forest Transitive Status
Selective Authentication
SID Filtering
Trust Attributes
Domain SIDs
Foreign Security Principals
Foreign Group Membership
Cross-Domain ACLs
Cross-Domain Administrative Rights
Network Reachability
Authentication Protocol
Resource Tested
Access Obtained
Timestamp
Tool
Tool Version
```

---

# Sensitive Information

Do not unnecessarily store:

```text
Passwords
NTLM Hashes
Kerberos Tickets
Trust Secrets
Private Keys
```

in reports or screenshots.

---

# Trust Relationship Detection

Monitoring should focus on:

```text
Trust Creation
Trust Removal
Trust Modification
Foreign Privileged Membership
Cross-Domain Authentication
SIDHistory Changes
Unexpected Privileged Logons
```

---

# Event 4706

Security event:

```text
4706
```

indicates:

```text
A new trust was created to a domain
```

Trust creation should be rare in stable environments.

---

# Event 4707

Security event:

```text
4707
```

indicates:

```text
A trust to a domain was removed
```

---

# Event 4716

Security event:

```text
4716
```

indicates:

```text
Trusted domain information was modified
```

Unexpected changes should be investigated.

---

# Directory Changes

Where appropriate auditing is enabled:

```text
5136
```

may provide visibility into Active Directory object modifications.

Correlate with:

```text
Administrator
Source System
Change Window
Ticket
```

---

# Cross-Domain Logons

Authentication telemetry may include:

```text
4624
4625
4648
4672
4768
4769
4771
4776
```

depending on authentication protocol and operation.

---

# Monitoring Foreign Administrators

High-value monitoring includes:

```text
Foreign Identity
      |
      v
Privileged Group
```

and:

```text
Foreign Identity
      |
      v
Tier 0 System
```

---

# Monitoring SIDHistory

Unexpected modification of:

```text
sIDHistory
```

should receive particular attention.

Legitimate migration operations should be:

```text
Planned
Documented
Time-Bounded
Monitored
```

---

# Trust Relationship Hardening

A mature model includes:

```text
Minimum Number of Trusts
Minimum Direction
Minimum Transitivity
Selective Authentication
SID Filtering
Minimum Foreign Privilege
Separate Administrators
Network Segmentation
Trust Monitoring
Periodic Review
```

---

# Minimise Trust Count

Every trust creates:

```text
Operational Dependency
```

and:

```text
Security Dependency
```

Maintain only relationships that have a documented business requirement.

---

# Minimise Direction

If access is required in only one direction:

```text
One-Way
```

may be preferable to:

```text
Two-Way
```

where operationally appropriate.

---

# Minimise Authentication Scope

Where appropriate, use:

```text
Selective Authentication
```

instead of unnecessarily broad cross-forest authentication.

---

# Maintain SID Filtering

Do not disable SID filtering without understanding the full security consequences.

Migration exceptions should be temporary and documented.

---

# Minimise Foreign Privilege

Avoid:

```text
Foreign Domain
      |
      v
Broad Administrative Group
      |
      v
Entire Server Estate
```

Prefer narrowly scoped role-based access.

---

# Separate Forest Administrators

A stronger model is:

```text
Forest A Admin
      |
      v
Forest A

Forest B Admin
      |
      v
Forest B
```

rather than:

```text
Shared Admin
    |
    +--> Forest A
    |
    +--> Forest B
```

---

# Restrict Network Connectivity

A trust should not imply:

```text
Any Host in Forest A
        |
        v
Any Host in Forest B
```

Restrict communication to required:

```text
Systems
Protocols
Ports
Directions
```

---

# Protect Tier 0

Foreign identities should not have Tier 0 access unless there is a strong documented requirement.

Review access to:

```text
Domain Controllers
AD CS
ADFS
Identity Synchronisation
Privileged Access Systems
Backup Systems
Virtualisation Control Planes
```

---

# Periodic Review

Trust relationships should be reviewed periodically.

Ask:

```text
Who Owns This Trust?

Why Does It Exist?

Is the Direction Still Required?

Is Two-Way Still Required?

Is Transitivity Required?

Is Selective Authentication Appropriate?

Are Foreign Privileged Groups Still Required?

Is SIDHistory Still Required?

Is the Trusted Environment Still Maintained?
```

---

# Reporting Trust Relationship Findings

Do not report:

```text
A trust exists
```

as a vulnerability.

Report the actual weakness.

Examples:

```text
Unnecessary Bidirectional Forest Trust
```

```text
Foreign Domain Group Has Excessive Administrative Rights
```

```text
Legacy Domain Remains Trusted After Migration
```

```text
Selective Authentication Not Used Across High-Risk Trust
```

```text
Excessive Cross-Forest Administrative Dependency
```

```text
Unnecessary Cross-Forest Network Reachability
```

---

# Example Finding - Foreign Administrative Group

```text
Finding:
Foreign Domain Group Has Administrative Access to Corporate Servers

Description:
A group originating from the trusted PARTNER.EXAMPLE domain was a
member of an administrative group used across multiple systems in the
CORP.EXAMPLE domain.

The trust itself was required for application access, but the
administrative relationship was broader than the documented business
requirement.

Impact:
Compromise of an account with membership in the foreign group could
provide administrative access to systems in the corporate domain.

This increases the security dependency on the trusted environment.

Recommendation:
Remove unnecessary foreign identities from administrative groups.

Use narrowly scoped role-based groups and separate privileged
identities for administration across security boundaries.
```

---

# Example Finding - Unnecessary Bidirectional Trust

```text
Finding:
Forest Trust Is Bidirectional Without Business Requirement

Description:
The trust between the corporate and partner forests was configured as
bidirectional.

The documented requirement only required partner identities to access
specific corporate resources.

No requirement for corporate identities to authenticate to partner
resources was identified.

Impact:
The additional trust direction unnecessarily expands the
authentication relationship between two separate forest security
boundaries.

Recommendation:
Determine whether the trust can be converted to a one-way relationship
that matches the documented access requirement.

Test application compatibility through the organisation's normal
change-management process before modifying the production trust.
```

---

# Example Finding - Broad Authentication

```text
Finding:
Cross-Forest Authentication Scope Is Broader Than Required

Description:
Trusted-forest identities were permitted to authenticate broadly
across the corporate forest even though only a small number of
application systems required cross-forest access.

Impact:
Compromise of an identity in the trusted forest could expose a larger
authentication surface in the corporate environment than required.

Normal resource authorisation remains necessary, but the broad
authentication scope increases opportunities for configuration errors
and lateral movement.

Recommendation:
Evaluate selective authentication and permit foreign identities to
authenticate only to systems requiring cross-forest access.

Review existing cross-forest groups and ACLs before implementing the
change.
```

---

# Example Finding - Legacy Trust

```text
Finding:
Unused Legacy Forest Trust Remains Configured

Description:
A trust relationship remained between the production forest and a
legacy forest used during a previous migration.

No active application, user or administrative dependency requiring the
trust was identified.

Impact:
The trust preserves an unnecessary authentication relationship with a
legacy environment.

If the legacy forest is compromised, the trust and any remaining
cross-forest permissions may provide additional opportunities to
access production resources.

Recommendation:
Confirm the absence of business dependencies with the relevant
technical and business owners.

Remove the trust through the normal change-management process if it is
no longer required.
```

---

# Example Finding - Cross-Forest Tier 0 Dependency

```text
Finding:
Foreign Forest Administrators Have Access to Tier 0 Infrastructure

Description:
Administrative identities originating from another forest were
permitted to administer systems forming part of the corporate identity
control plane.

Affected systems included Tier 0 or equivalent identity
infrastructure.

Impact:
Compromise of privileged identities in the trusted forest could
directly affect the security of the corporate forest.

The two forests therefore do not operate as independent security
boundaries in practice.

Recommendation:
Use separate privileged identities for each forest.

Remove unnecessary foreign administrative access to Tier 0 systems and
restrict privileged management to dedicated administrative
workstations and approved management networks.
```

---

# Trust Relationship Assessment Checklist

## Domain

- [ ] Identify current domain
- [ ] Identify NetBIOS domain
- [ ] Identify domain SID
- [ ] Identify parent domain
- [ ] Identify child domains
- [ ] Identify domain functional level

## Forest

- [ ] Identify current forest
- [ ] Identify forest root
- [ ] Identify all forest domains
- [ ] Identify global catalogs
- [ ] Identify forest functional level
- [ ] Treat forest as primary AD security boundary

## Trust Enumeration

- [ ] Run `Get-ADTrust -Filter *`
- [ ] Run `nltest /domain_trusts`
- [ ] Review trustedDomain objects
- [ ] Identify trust partner
- [ ] Identify flat name
- [ ] Identify security identifier
- [ ] Record raw trust attributes

## Direction

- [ ] Identify inbound trusts
- [ ] Identify outbound trusts
- [ ] Identify bidirectional trusts
- [ ] Interpret direction from correct domain perspective
- [ ] Document potential authentication direction

## Type

- [ ] Identify parent-child
- [ ] Identify tree-root
- [ ] Identify shortcut
- [ ] Identify external
- [ ] Identify forest
- [ ] Identify realm

## Transitivity

- [ ] Identify transitive relationships
- [ ] Identify non-transitive relationships
- [ ] Identify intra-forest relationships
- [ ] Identify forest-transitive relationships
- [ ] Identify unnecessary trust scope

## Authentication

- [ ] Review Kerberos
- [ ] Review NTLM
- [ ] Review DNS
- [ ] Review KDC reachability
- [ ] Review referral path
- [ ] Review selective authentication
- [ ] Review forest-wide authentication

## SID Security

- [ ] Review SID filtering
- [ ] Review SIDHistory
- [ ] Identify migration exceptions
- [ ] Review Treat-As-External configuration
- [ ] Review trust attributes
- [ ] Avoid changing trust security during testing

## Foreign Principals

- [ ] Enumerate ForeignSecurityPrincipals
- [ ] Resolve in-scope foreign SIDs
- [ ] Review Domain Local groups
- [ ] Review Universal groups
- [ ] Review nested group membership
- [ ] Review local Administrators
- [ ] Review remote-management groups

## ACLs

- [ ] Identify foreign principals in AD ACLs
- [ ] Identify GenericAll
- [ ] Identify GenericWrite
- [ ] Identify WriteDACL
- [ ] Identify WriteOwner
- [ ] Identify object-specific rights
- [ ] Determine actual impact

## Privilege

- [ ] Review cross-domain administrators
- [ ] Review cross-forest administrators
- [ ] Review Tier 0 access
- [ ] Review Enterprise Admin relationships
- [ ] Review service accounts
- [ ] Review application administrators
- [ ] Review backup administrators
- [ ] Review management systems

## Network

- [ ] Identify cross-domain DNS
- [ ] Identify Kerberos paths
- [ ] Identify LDAP paths
- [ ] Identify SMB paths
- [ ] Identify RPC paths
- [ ] Identify WinRM paths
- [ ] Identify RDP paths
- [ ] Review segmentation
- [ ] Review management networks

## Safe Validation

- [ ] Confirm target domain is in scope
- [ ] Confirm target forest is in scope
- [ ] Use approved identity
- [ ] Prefer read-only validation
- [ ] Test approved resource
- [ ] Avoid unnecessary execution
- [ ] Do not modify trust
- [ ] Do not modify SID filtering
- [ ] Do not modify SIDHistory
- [ ] Stop when evidence is sufficient

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
- [ ] Monitor SIDHistory
- [ ] Monitor cross-forest administrative logons

## Hardening

- [ ] Remove unused trusts
- [ ] Minimise trust direction
- [ ] Minimise transitivity
- [ ] Use selective authentication where appropriate
- [ ] Maintain SID filtering
- [ ] Minimise foreign privilege
- [ ] Separate forest administrators
- [ ] Protect Tier 0
- [ ] Restrict network access
- [ ] Review migration exceptions
- [ ] Assign trust owner
- [ ] Review trusts periodically

## Reporting

- [ ] Do not report trust existence alone
- [ ] Identify actual security weakness
- [ ] Record source and target
- [ ] Record direction correctly
- [ ] Record type
- [ ] Record transitivity
- [ ] Record trust attributes
- [ ] Record security controls
- [ ] Identify affected identities
- [ ] Identify affected resources
- [ ] Explain security-boundary impact
- [ ] Provide targeted remediation

---

# Trust Relationship Testing Model

The basic model is:

```text
Domain A
   |
   v
Trust
   |
   v
Domain B
```

The direction model is:

```text
DOMAIN-A trusts DOMAIN-B

DOMAIN-B Identity
        |
        v
DOMAIN-A Resource
```

The two-way model is:

```text
DOMAIN-A
   <---->
DOMAIN-B
```

The authentication model is:

```text
Identity
   |
   v
Source KDC
   |
   v
Trust
   |
   v
Target KDC
   |
   v
Service
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

The group model is:

```text
Foreign Account
      |
      v
Global Group
      |
      v
Domain Local Group
      |
      v
Permission
```

The multi-domain model is:

```text
Account
   |
   v
Global Group
   |
   v
Universal Group
   |
   v
Domain Local Group
   |
   v
Permission
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
      +--> No
      |
      +--> Yes
             |
             v
      Resource Authorisation
```

The SID model is:

```text
Identity
   |
   v
Security Token
   |
   +--> User SID
   +--> Group SIDs
   +--> SIDHistory
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

The cross-forest model is:

```text
Forest A
   |
   v
Trust
   |
   v
Forest B
```

The privilege model is:

```text
Forest A Identity
       |
       v
Forest B Group
       |
       v
Forest B Privilege
       |
       v
Cross-Boundary Dependency
```

The network model is:

```text
Trust
  +
DNS
  +
Network Reachability
  +
Authentication
  +
Authorisation
  =
Access
```

The defensive model is:

```text
Minimum Trust
     +
Minimum Direction
     +
Minimum Transitivity
     +
Selective Authentication
     +
SID Filtering
     +
Minimum Foreign Privilege
     +
Network Segmentation
     +
Administrative Separation
     =
Reduced Trust Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I attack the trusted forest?"

Ask:
"Is the trusted forest in scope,
and what security dependency does
the trust create?"
```

For defenders:

```text
Do Not Ask:
"Is this trust working?"

Ask:
"Does this trust provide only the
minimum authentication relationship
required by the business?"
```

The complete model is:

```text
Business Requirement
       |
       v
Trust Relationship
       |
       v
Authentication Scope
       |
       v
Security Controls
       |
       v
Foreign Identity
       |
       v
Authorisation
       |
       v
Resource Access
       |
       v
Security Dependency
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Trusts:

[Domain and Forest Trusts](trusts.md)

Enumeration:

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

NTLM:

[NTLM](ntlm.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

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

Active Directory Certificate Services:

[Active Directory Certificate Services](ad-cs/index.md)

The next trust page is:

```text
docs/active-directory/sid-history.md
```

followed by:

```text
docs/active-directory/trust-tickets.md
```

---

# References

## Microsoft - How Domains and Forests Work

[Microsoft - How Domains and Forests Work](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc759073(v=ws.10)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADTrust

[Microsoft - Get-ADTrust](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adtrust){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADDomain

[Microsoft - Get-ADDomain](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomain){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADForest

[Microsoft - Get-ADForest](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adforest){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - NLTest

[Microsoft - NLTest](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/nltest){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Trusted-Domain Object

[Microsoft - Trusted-Domain Object](https://learn.microsoft.com/en-us/windows/win32/adschema/c-trusteddomain){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - trustDirection

[Microsoft - trustDirection Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-trustdirection){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - trustType

[Microsoft - trustType Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-trusttype){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - trustAttributes

[Microsoft - trustAttributes Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-trustattributes){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4706

[Microsoft - 4706: A New Trust Was Created to a Domain](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4706){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4707

[Microsoft - 4707: A Trust to a Domain Was Removed](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4707){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4716

[Microsoft - 4716: Trusted Domain Information Was Modified](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4716){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## PowerView / PowerSploit

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

PowerSploit is an older project. Verify functions and behaviour against the PowerView version used during the assessment.

---

## MITRE ATT&CK - Domain Trust Discovery

[MITRE ATT&CK - T1482 Domain Trust Discovery](https://attack.mitre.org/techniques/T1482/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Trust relationships should be analysed as:

```text
Security Dependencies
```

rather than merely:

```text
Active Directory Configuration
```

The correct assessment path is:

```text
Discover Trust
     |
     v
Understand Direction
     |
     v
Understand Type
     |
     v
Understand Transitivity
     |
     v
Confirm Scope
     |
     v
Review Security Controls
     |
     v
Identify Foreign Principals
     |
     v
Map Groups and ACLs
     |
     v
Validate Minimum Access
     |
     v
Determine Security Impact
```

The trust itself is rarely the vulnerability.

More important weaknesses include:

```text
Unnecessary Trust Direction
Excessive Transitivity
Broad Authentication
Disabled or Weakened SID Filtering
Excessive Foreign Group Membership
Cross-Forest Administrative Access
Legacy Trusts
Unnecessary Network Connectivity
```

A trust should provide only:

```text
The Minimum Authentication Relationship
Required by the Business
```

and should be reinforced with:

```text
Selective Authentication
SID Filtering
Least Privilege
Network Segmentation
Administrative Separation
Monitoring
```

The most important distinction remains:

```text
Authentication
!=
Authorisation
```

A trust may allow an identity to be recognised without granting access to any useful resource.

The assessment therefore should not stop at:

```text
Trust Found
```

It should continue to:

```text
Trust Found
    |
    v
Foreign Identity Identified
    |
    v
Permission Identified
    |
    v
Resource Identified
    |
    v
Security Impact Established
```

The next page focuses on one of the most important SID-related mechanisms affecting domain migrations and trust security:

```text
SID History
```
