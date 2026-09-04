# Active Directory Privilege Escalation

Active Directory privilege escalation is the process of moving from a lower-privileged identity or security context to one with greater control over:

```text
Users
Groups
Computers
Servers
Applications
Domain Controllers
Active Directory Objects
The Domain
The Forest
```

Privilege escalation in Active Directory is rarely limited to a single technique.

A typical path looks like:

```text
Initial User
    |
    v
Local Access
    |
    v
Credential / Configuration Discovery
    |
    v
Additional Identity
    |
    v
Delegated AD Permission
    |
    v
Privileged Group / System
    |
    v
Domain or Forest Control
```

The important concept is:

```text
Privilege Escalation
!=
Only Exploiting Software Vulnerabilities
```

Active Directory privilege escalation frequently results from legitimate functionality combined with excessive permissions, credential exposure, weak delegation or poor administrative architecture.

!!! warning "Authorised testing only"
    Active Directory privilege escalation testing can affect identities, computers and domain-wide security controls. Prefer read-only path discovery first. Do not modify privileged groups, ACLs, delegation, Group Policy, certificates, directory replication permissions or production credentials unless the assessment scope explicitly authorises active validation.

---

# Why Privilege Escalation Matters

A normal domain account may initially have limited privileges:

```text
Domain User
```

but still have relationships with other objects.

For example:

```text
Domain User
    |
    v
Helpdesk Group
    |
    v
Reset Password
    |
    v
Server Administrator
    |
    v
Management Server
    |
    v
Domain Administration
```

No software vulnerability is required.

The weakness is the:

```text
Privilege Path
```

---

# Privilege Escalation Is a Graph Problem

Active Directory contains relationships between:

```text
Users
Groups
Computers
OUs
GPOs
Domains
Certificates
Sessions
Credentials
ACLs
Trusts
```

These relationships form a graph.

Conceptually:

```text
User
 |
 v
Group
 |
 v
ACL
 |
 v
Computer
 |
 v
Session
 |
 v
Administrator
```

Tools such as BloodHound are useful because they model these relationships as attack paths.

See:

[BloodHound](bloodhound.md)

---

# Direct vs Indirect Privilege

Direct privilege:

```text
User
 |
 v
Domain Admins
```

Indirect privilege:

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
Local Admin
 |
 v
Server
 |
 v
Privileged Session
```

Indirect relationships are often more difficult to identify manually.

---

# Privilege Escalation Categories

Common Active Directory privilege escalation categories include:

```text
Group Membership
ACL Abuse
Credential Exposure
Kerberos Abuse
NTLM Abuse
Delegation
Group Policy
Machine Account Configuration
Service Accounts
LAPS
gMSA
AD CS
Trust Relationships
Local Administrator Reuse
Domain Controller Rights
Misconfigured Infrastructure
```

---

# Assessment Model

A useful model is:

```text
Current Identity
      |
      v
Current Rights
      |
      v
Reachable Objects
      |
      v
Controllable Objects
      |
      v
Credentials / Sessions
      |
      v
New Identity
      |
      v
Repeat
```

Privilege escalation is often iterative.

---

# Start With the Current Identity

Before looking for escalation paths, understand the current security context.

Windows:

```cmd
whoami
```

```cmd
whoami /user
```

```cmd
whoami /groups
```

```cmd
whoami /priv
```

PowerShell:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

---

# Current Domain

```powershell
$env:USERDOMAIN
```

Using the Active Directory module:

```powershell
Get-ADDomain
```

---

# Current User Object

```powershell
Get-ADUser -Identity $env:USERNAME -Properties *
```

For focused output:

```powershell
Get-ADUser -Identity $env:USERNAME -Properties MemberOf,PrimaryGroupID |
    Select-Object SamAccountName,MemberOf,PrimaryGroupID
```

---

# Current Group Membership

```powershell
Get-ADPrincipalGroupMembership -Identity $env:USERNAME |
    Select-Object Name,GroupScope,GroupCategory
```

Recursive group relationships should also be considered.

---

# Domain Enumeration

Privilege escalation analysis depends on good enumeration.

See:

[Active Directory Enumeration](enumeration.md)

Important areas include:

```text
Users
Groups
Computers
OUs
ACLs
GPOs
SPNs
Delegation
Service Accounts
Trusts
Certificate Services
```

---

# BloodHound

BloodHound can model many privilege relationships.

Typical workflow:

```text
Collect
   |
   v
Import
   |
   v
Identify Current User
   |
   v
Search Paths
   |
   v
Validate Relationships
```

Do not treat every BloodHound edge as automatically exploitable.

Verify:

```text
Permissions
Network Reachability
Authentication
Endpoint Controls
Object State
```

---

# Shortest Path Analysis

A conceptual path may look like:

```text
USER01
 |
 | MemberOf
 v
HELPDESK
 |
 | GenericAll
 v
SERVER-ADMINS
 |
 | AdminTo
 v
MGMT01
 |
 | HasSession
 v
DOMAIN-ADMIN
```

The graph reveals the relationship.

The assessor still needs to determine whether the path is practically valid.

---

# Privileged Groups

Important groups can include:

```text
Domain Admins
Enterprise Admins
Schema Admins
Administrators
Account Operators
Server Operators
Backup Operators
Print Operators
Group Policy Creator Owners
DnsAdmins
```

The actual security impact depends on:

```text
Domain
Operating System
Configuration
Delegation
Group Usage
```

Do not assume every historical escalation technique still works on every modern environment.

---

# Domain Admins

Membership of:

```text
Domain Admins
```

normally provides extensive administrative control within the domain.

Review:

```powershell
Get-ADGroupMember -Identity 'Domain Admins' -Recursive
```

---

# Enterprise Admins

In a forest root domain:

```powershell
Get-ADGroupMember -Identity 'Enterprise Admins' -Recursive
```

Enterprise Admins have forest-wide significance.

---

# Schema Admins

```powershell
Get-ADGroupMember -Identity 'Schema Admins' -Recursive
```

Schema administration is highly privileged and should normally have minimal standing membership.

---

# Built-In Administrators

```powershell
Get-ADGroupMember -Identity 'Administrators' -Recursive
```

Interpret this group in the correct domain and built-in container context.

---

# Group Nesting

Privilege can be hidden through nested groups.

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

Recursive enumeration is therefore important.

---

# Group Management Rights

A user does not need to already belong to a privileged group if they can control the group.

Example:

```text
User
 |
 | WriteMembers
 v
Privileged Group
```

This can represent an escalation path.

See:

[Groups](groups.md)

and:

[ACL and ACE](acl-ace.md)

---

# ACL-Based Privilege Escalation

Active Directory objects are protected by:

```text
Access Control Lists - ACLs
```

An ACL contains:

```text
Access Control Entries - ACEs
```

Misconfigured permissions can allow lower-privileged users to control sensitive objects.

---

# Common Dangerous Rights

Security-relevant rights include:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
WriteProperty
AllExtendedRights
ForceChangePassword
WriteMembers
```

Specific object types may expose additional security-sensitive extended rights.

---

# GenericAll

Conceptually:

```text
User
 |
 | GenericAll
 v
Target Object
```

This can provide broad control over the target object.

The exact security consequence depends on whether the target is a:

```text
User
Group
Computer
OU
GPO
Domain
```

---

# GenericWrite

```text
User
 |
 | GenericWrite
 v
Target
```

GenericWrite can allow modification of writable attributes.

Whether that becomes privilege escalation depends on which attributes can be changed and how they are used.

---

# WriteDacl

```text
User
 |
 | WriteDacl
 v
Object
 |
 v
Modify Permissions
```

Control over an object's DACL can allow the attacker to grant additional permissions.

---

# WriteOwner

```text
User
 |
 | WriteOwner
 v
Object
 |
 v
Ownership
 |
 v
Potential Permission Control
```

Ownership can provide a path toward modifying the object's permissions.

---

# ForceChangePassword

An identity may have the extended right to reset another user's password.

Conceptually:

```text
Helpdesk User
      |
      v
Reset Password
      |
      v
Privileged User
```

This is security-sensitive when the target has greater privilege.

---

# ACL Enumeration

See the dedicated:

[ACL and ACE](acl-ace.md)

page for detailed enumeration.

With PowerView loaded, common discovery commands include:

```powershell
Get-DomainObjectAcl -ResolveGUIDs
```

Always confirm syntax against the PowerView version being used.

---

# BloodHound ACL Edges

BloodHound may represent rights such as:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
ForceChangePassword
AddMember
```

Use these edges as leads for validation rather than automatic findings.

---

# Credential-Based Privilege Escalation

Privilege often follows credentials.

```text
Low-Privilege User
      |
      v
Credential Discovery
      |
      v
Privileged Credential
      |
      v
Privileged Context
```

See:

[Credential Access](credential-access.md)

---

# Common Credential Sources

Examples include:

```text
Configuration Files
Scripts
Scheduled Tasks
Services
Registry
Credential Manager
Shares
Backups
Deployment Systems
Service Accounts
PowerShell History
Application Configuration
```

---

# Credential Reuse

A password may belong to an ordinary domain user but provide administrative access elsewhere.

Example:

```text
USER01
 |
 | Same Password / Credential
 v
Local Administrator
 |
 v
SERVER01
```

The resulting server may contain additional privileged credentials.

---

# Local Administrator Reuse

A common historical escalation pattern is:

```text
Compromised Workstation
       |
       v
Local Admin Credential
       |
       v
Same Credential on Server
       |
       v
Server Compromise
```

Unique local administrator passwords reduce this risk.

See:

[LAPS](laps.md)

---

# LAPS

Windows LAPS or legacy Microsoft LAPS can reduce local administrator password reuse.

However, the key security question becomes:

```text
Who Can Read the Managed Password?
```

If a low-privileged identity can read LAPS credentials for a sensitive system:

```text
User
 |
 v
Read LAPS Password
 |
 v
Local Administrator
 |
 v
Sensitive Server
```

See:

[LAPS](laps.md)

---

# gMSA

Group Managed Service Accounts can reduce static service-account password management.

However:

```text
Who Can Retrieve the Managed Password?
```

remains important.

Conceptually:

```text
User / Computer
      |
      v
Allowed to Retrieve gMSA Secret
      |
      v
Service Identity
```

See:

[gMSA](gmsa.md)

---

# Service Accounts

Service accounts frequently have:

```text
SPNs
Server Access
Database Access
Application Rights
Delegated AD Permissions
```

A service account should therefore be assessed based on:

```text
Credential Exposure
Privilege
Reachability
Delegation
Group Membership
```

---

# Kerberoasting

Accounts with Service Principal Names may be relevant to Kerberoasting.

See:

[Kerberoasting](kerberoasting.md)

Conceptually:

```text
Domain User
    |
    v
Request Service Ticket
    |
    v
Offline Password Analysis
    |
    v
Service Account
```

The escalation occurs only if the recovered service identity provides greater privilege.

---

# AS-REP Roasting

Accounts without Kerberos preauthentication may expose material suitable for offline password analysis.

See:

[AS-REP Roasting](asrep-roasting.md)

Again:

```text
Roastable Account
!=
Privilege Escalation
```

The account must provide meaningful additional privilege.

---

# Kerberos Tickets

Existing Kerberos tickets can represent valuable authentication material.

See:

[Kerberos Tickets](kerberos-tickets.md)

and:

[Pass the Ticket](pass-the-ticket.md)

---

# Pass the Hash

NTLM hash material can sometimes be used for authentication without recovering the plaintext password.

See:

[Pass the Hash](pass-the-hash.md)

The security impact depends on:

```text
Target
Privileges
Protocol
Endpoint Controls
```

---

# Pass the Key

Kerberos keys can also be used in authentication workflows.

See:

[Pass the Key](pass-the-key.md)

---

# Overpass the Hash

See:

[Overpass the Hash](overpass-the-hash.md)

for the relationship between NTLM-derived key material and Kerberos authentication.

---

# Delegation

Kerberos delegation is another major privilege-escalation area.

Common models include:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

---

# Unconstrained Delegation

See:

[Unconstrained Delegation](unconstrained-delegation.md)

A system trusted for unconstrained delegation can create significant credential exposure when privileged users authenticate to it.

---

# Constrained Delegation

See:

[Constrained Delegation](constrained-delegation.md)

The security impact depends on:

```text
Delegating Principal
Allowed Services
Protocol Transition
Target
```

---

# Resource-Based Constrained Delegation

See:

[Resource-Based Constrained Delegation](rbcd.md)

RBCD shifts delegation configuration to the target resource.

Control over the relevant computer-object attributes can therefore become security-sensitive.

---

# S4U

Kerberos Service-for-User extensions are central to several delegation workflows.

See:

[S4U](s4u.md)

---

# Machine Account Quota

Historically, Active Directory domains commonly allowed ordinary authenticated users to create a limited number of computer accounts through:

```text
ms-DS-MachineAccountQuota
```

See:

[Machine Account Quota](machine-account-quota.md)

Check the current value:

```powershell
Get-ADDomain |
    Select-Object DistinguishedName
```

Then:

```powershell
Get-ADObject -Identity (Get-ADDomain).DistinguishedName -Properties ms-DS-MachineAccountQuota |
    Select-Object ms-DS-MachineAccountQuota
```

A non-zero value is not automatically a vulnerability.

Its relevance depends on other privilege relationships.

---

# Shadow Credentials

Control over key credential attributes can enable certificate-backed authentication paths.

See:

[Shadow Credentials](shadow-credentials.md)

The important relationship is:

```text
Attacker
 |
 v
Write Relevant Key Credential Attribute
 |
 v
Target Identity
```

This is particularly important when the target identity is privileged.

---

# Group Policy

Group Policy can control:

```text
Security Settings
Scripts
Scheduled Tasks
Services
Registry
Local Groups
Software
```

Control over a GPO linked to sensitive systems can therefore represent substantial privilege.

See:

[Group Policy](group-policy.md)

---

# GPO Privilege Path

```text
User
 |
 | Can Modify
 v
GPO
 |
 | Linked To
 v
Servers OU
 |
 v
Privileged Servers
```

The existence of GPO write access should be evaluated together with:

```text
Link Scope
Security Filtering
WMI Filtering
Target Computers
```

---

# OU Control

Delegated control over an Organisational Unit can create escalation opportunities.

Example:

```text
User
 |
 | Delegated Rights
 v
Servers OU
 |
 +--> SERVER01
 +--> SERVER02
```

Review the exact ACEs inherited by objects within the OU.

---

# Computer Object Control

Control over a computer object can matter because computer objects contain security-sensitive attributes.

Potentially relevant areas include:

```text
Delegation
SPNs
Key Credentials
Group Membership
DNS Relationships
```

The exact escalation path depends on the permissions granted.

---

# User Object Control

Control over another user may include:

```text
Password Reset
Attribute Modification
ACL Modification
Key Credential Modification
Group Relationships
```

Prioritise targets with higher privilege.

---

# Group Object Control

Control over group membership can directly change authorisation.

Example:

```text
User
 |
 | AddMember
 v
Server Admins
```

The target group's effective privilege determines impact.

---

# Domain Object Control

Permissions on the domain root can be extremely sensitive.

Particularly important are replication-related extended rights.

---

# Directory Replication Rights

The rights commonly associated with directory replication include:

```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

and, in some environments and scenarios:

```text
DS-Replication-Get-Changes-In-Filtered-Set
```

Accounts with sufficient replication rights may be able to request sensitive directory replication data.

---

# DCSync

DCSync refers to abusing directory replication permissions to request credential data from a domain controller.

Conceptually:

```text
Account
 |
 | Replication Rights
 v
Domain Controller
 |
 v
Directory Secrets
```

This is a high-impact capability.

Do not perform DCSync in production merely to prove that the required rights exist unless explicitly authorised.

Permission evidence can often establish the finding.

See:

[NTDS](ntds.md)

---

# Backup Operators

Backup-related privileges can provide access to data that ordinary file permissions would otherwise protect.

On sensitive systems this can expose:

```text
Registry Hives
System State
Application Data
Directory Data
```

Membership should therefore be reviewed carefully.

---

# Server Operators

Server Operators can possess significant server-management capabilities on domain controllers in applicable environments.

Do not assume the group is harmless simply because it is not:

```text
Domain Admins
```

---

# Account Operators

Account Operators can manage certain users and groups subject to Active Directory protections and object scope.

Assess what the group can actually control in the current environment.

---

# DNS Administrators

DNS administration can be highly sensitive on domain controllers and AD-integrated DNS infrastructure.

Review:

```text
DnsAdmins
```

membership and actual DNS server permissions.

See:

[Active Directory Integrated DNS](adidns.md)

Historical DNS privilege-escalation techniques are configuration and version dependent, so validate current behaviour before reporting exploitability.

---

# AD CS

Active Directory Certificate Services can introduce powerful authentication paths.

See:

[Active Directory Certificate Services](ad-cs/index.md)

Common areas include:

```text
Certificate Templates
Enrollment Rights
CA Configuration
Certificate Mapping
Web Enrollment
RPC Enrollment
CA Security
```

---

# ESC Paths

The AD CS section contains detailed notes for:

```text
ESC1
ESC2
ESC3
ESC4
ESC5
ESC6
ESC7
ESC8
ESC9
ESC10
ESC11
ESC12
ESC13
ESC14
ESC15
ESC16
ESC17
```

Do not assume every ESC condition is exploitable merely because a scanner reports it.

Validate:

```text
Enrollment Rights
Template State
CA State
Authentication Mapping
Patch Level
Certificate Purpose
Target Privilege
```

---

# AD CS Privilege Model

Conceptually:

```text
Low-Privilege Identity
       |
       v
Certificate Misconfiguration
       |
       v
Certificate for Higher-Privilege Identity
       |
       v
Authentication
       |
       v
Privilege Escalation
```

The exact path depends on the specific ESC condition.

---

# NTLM Relay

NTLM authentication can sometimes be relayed to another service when protections are insufficient.

See:

[NTLM Relay](ntlm-relay.md)

The privilege impact depends on:

```text
Relayed Identity
Target Service
Signing
Channel Binding
EPA
Target Permissions
```

---

# Authentication Coercion

Authentication coercion can cause a system or identity to authenticate to another location.

See:

[Authentication Coercion](authentication-coercion.md)

Coercion alone is not privilege escalation.

A full path may be:

```text
Coercion
   |
   v
Authentication
   |
   v
Relay
   |
   v
Privileged Target
```

---

# Kerberos Relay

See:

[Kerberos Relay](kerberos-relay.md)

Kerberos relay scenarios depend heavily on:

```text
Protocol
SPN
Target
Signing
Authentication Context
```

---

# NTLM Relay Path

A conceptual path is:

```text
Privileged Machine
      |
      v
Authentication
      |
      v
Relay
      |
      v
Target Service
      |
      v
Privilege
```

Do not treat captured NTLM authentication as equivalent to successful relay.

---

# Trusts

Active Directory trusts can extend authentication relationships across domains or forests.

See:

[Trusts](trusts.md)

A trust itself is not a vulnerability.

Review:

```text
Direction
Transitivity
Authentication Scope
SID Filtering
Foreign Principals
Privileged Group Membership
```

---

# Cross-Domain Privilege

A conceptual cross-domain path may look like:

```text
DOMAIN-A\User
      |
      v
Foreign Security Principal
      |
      v
DOMAIN-B Group
      |
      v
Resource Administration
```

This may be completely intentional.

The assessment should determine whether the resulting privilege is appropriate.

---

# SID History

SID History can affect authorisation decisions across migrations and trust relationships.

A dedicated page should evaluate:

```text
SIDHistory Population
Migration Requirement
Privileged Historical SIDs
Trust Controls
Monitoring
```

Do not assume the presence of SID History is malicious.

---

# Trust Tickets

Inter-domain Kerberos trust material is highly sensitive.

Compromise of trust secrets can create authentication risks across trust boundaries.

This should be assessed separately from ordinary user-level privilege escalation.

---

# Local Privilege Escalation

Active Directory escalation frequently depends on first escalating privileges on a Windows endpoint.

Conceptually:

```text
Domain User
    |
    v
Workstation
    |
    v
Local Administrator
    |
    v
Credential Discovery
    |
    v
Domain Identity
```

Local Windows privilege escalation should therefore be analysed alongside Active Directory relationships.

---

# Local Administrator Enumeration

From the target:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

Remote administrative rights can also be modelled with BloodHound.

---

# Privileged Sessions

A low-value server can become important when a privileged user logs into it.

```text
SERVER01
   |
   v
Domain Admin Session
```

If another identity controls SERVER01, the server may become part of a privilege path.

---

# Session Exposure

The security model is:

```text
Control Computer
      |
      v
Privileged User Uses Computer
      |
      v
Credential / Session Exposure
```

Modern credential protections can significantly affect practical exploitability.

Do not assume that every administrative session exposes reusable credentials.

---

# Administrative Tiering

A strong administrative model separates:

```text
Tier 0
Tier 1
Tier 2
```

or equivalent modern privileged-access tiers.

Conceptually:

```text
Tier 0
 |
 X
Must Not Log Into
 |
 v
Tier 2 Workstation
```

This prevents lower-trust systems from becoming credential stepping stones.

---

# Privileged Access Workstations

Dedicated administrative workstations reduce exposure of privileged credentials.

A privileged administrator should avoid using high-value credentials from ordinary endpoints.

---

# Credential Guard

Windows Defender Credential Guard can reduce exposure of certain credential material.

Its presence can change the practicality of credential-based escalation paths.

Do not assume:

```text
Local Administrator
=
All Credentials Available
```

---

# Protected Users

The:

```text
Protected Users
```

group provides additional authentication protections for high-value accounts.

Assess whether appropriate privileged identities use modern protections.

---

# Authentication Policies

Authentication Policies and Authentication Policy Silos can further restrict where sensitive accounts authenticate.

These controls can reduce credential exposure.

---

# Protected Objects

Some privileged Active Directory objects are affected by:

```text
AdminSDHolder
```

and:

```text
SDProp
```

These mechanisms help protect permissions on certain privileged accounts and groups.

---

# AdminCount

Protected accounts may have:

```text
adminCount = 1
```

but do not treat this attribute alone as definitive proof of current privilege.

Historical privileged membership can leave `adminCount` set.

---

# Enumerate adminCount

```powershell
Get-ADUser -LDAPFilter '(adminCount=1)' -Properties adminCount |
    Select-Object SamAccountName,Enabled,adminCount
```

Review results manually.

---

# AdminSDHolder

AdminSDHolder provides a protected security descriptor used for certain privileged objects.

A simplified model:

```text
AdminSDHolder
     |
     v
Protected ACL
     |
     v
Privileged Objects
```

Permissions on AdminSDHolder are therefore extremely sensitive.

---

# AdminSDHolder Assessment

Review:

```text
Unexpected ACEs
Delegated Control
Non-Administrative Principals
WriteDacl
WriteOwner
GenericAll
```

Do not modify AdminSDHolder during ordinary assessment.

---

# Domain Controller Access

Any path that results in administrative control of a domain controller should be considered highly significant.

Conceptually:

```text
User
 |
 v
Server Admin
 |
 v
Domain Controller
 |
 v
Domain Control
```

However, establish exactly what administrative rights exist rather than assuming them from network reachability.

---

# Domain Controller Services

Sensitive services include:

```text
LDAP
LDAPS
Kerberos
SMB
RPC
DNS
WinRM
RDP
```

Availability of these services is normal.

The security question is:

```text
Can the Current Identity Perform Privileged Operations?
```

---

# Infrastructure Privilege Paths

Active Directory environments often depend on management infrastructure such as:

```text
SCCM
WSUS
MDT
SCOM
AD FS
AD CS
Backup Platforms
Virtualisation
Monitoring
Deployment Systems
```

Compromise of these systems can indirectly affect large numbers of domain computers.

---

# SCCM

Systems management platforms may have extensive access to managed endpoints.

A privilege path can conceptually be:

```text
SCCM Administrator
      |
      v
Managed Servers
      |
      v
Privileged Systems
```

See:

[SCCM](sccm.md)

---

# WSUS

WSUS is part of the software-update trust chain.

See:

[WSUS](wsus.md)

Assess:

```text
Administrative Rights
Transport Security
Update Approval
Server Security
```

---

# MDT

Deployment infrastructure may contain:

```text
Deployment Credentials
Scripts
Configuration
Images
```

See:

[MDT](mdt.md)

---

# SCOM

Monitoring infrastructure can possess broad visibility and agent relationships.

See:

[SCOM](scom.md)

Review whether its administrative model creates paths to higher-value systems.

---

# AD FS

Federation infrastructure is highly trusted.

See:

[AD FS](adfs.md)

Administrative control over AD FS or federation signing material can have consequences across relying-party applications.

---

# RODC

RODCs intentionally limit the impact of branch-domain-controller compromise.

See:

[RODC](rodc.md)

Important questions include:

```text
Which Credentials Can Be Cached?
Which Credentials Have Been Cached?
Who Administers the RODC?
```

---

# Shares

File shares can reveal:

```text
Credentials
Scripts
Configuration
Backups
Deployment Files
Keys
```

Review:

[Shares](shares.md)

---

# Privilege Escalation Through Scripts

Administrative scripts can contain:

```text
Passwords
API Keys
Service Credentials
Mapped Drive Credentials
Deployment Credentials
```

Search only locations authorised within scope.

---

# PowerShell History

On a system where access is authorised:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath -ErrorAction SilentlyContinue
```

Treat any discovered credentials as sensitive evidence.

Avoid unnecessarily reproducing them in reports.

---

# Scheduled Tasks

Review:

```powershell
Get-ScheduledTask
```

Look for:

```text
Privileged Run Context
Writable Scripts
Writable Executables
Credentials
Weak Paths
```

---

# Services

Review:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```

Relevant questions include:

```text
Who Runs the Service?
Who Can Modify the Binary?
Who Can Modify the Directory?
Who Can Modify the Service Configuration?
```

---

# Writable Administrative Paths

A generic privilege relationship is:

```text
Low-Privilege User
      |
      v
Writable File
      |
      v
Privileged Process
```

This is a local privilege escalation concept but may become part of an AD escalation chain.

---

# Software Deployment

Determine whether lower-privileged identities can modify:

```text
Software Packages
Deployment Scripts
Installation Sources
Login Scripts
Management Packages
```

that execute on higher-value systems.

---

# Login Scripts

Active Directory logon scripts can be referenced through user or Group Policy configuration.

If a low-privileged user can modify a script executed by privileged identities, a privilege relationship may exist.

Validate:

```text
Script Location
ACL
Execution Context
Affected Users
```

---

# SYSVOL

SYSVOL contains domain-wide policy and script information.

Normal users generally have read access.

The key security question is:

```text
Who Can Write?
```

Unexpected write access to security-sensitive SYSVOL content can create substantial risk.

---

# Group Policy Preferences

Historical Group Policy Preferences deployments could expose recoverable passwords through:

```text
cpassword
```

in SYSVOL XML files.

Modern environments should not create new GPP password entries.

Existing legacy artefacts may still be present.

---

# GPP Search

A read-only authorised search can identify legacy references:

```powershell
Get-ChildItem "\\$env:USERDNSDOMAIN\SYSVOL" -Recurse -Filter '*.xml' -ErrorAction SilentlyContinue |
    Select-String -Pattern 'cpassword'
```

Finding a `cpassword` value warrants investigation.

Do not expose recovered credentials in reports.

---

# Password Spraying

Password spraying can sometimes identify additional accounts, but it carries:

```text
Account Lockout
Detection
Operational
User Impact
```

risk.

See:

[Password Spraying](password-spraying.md)

Do not use spraying as the default escalation technique.

---

# Privilege Escalation Through Password Reuse

If credentials are obtained legitimately within scope, determine where they are authorised rather than blindly attempting them across the domain.

A safer workflow is:

```text
Credential
    |
    v
Identify Account
    |
    v
Determine Group Membership
    |
    v
Determine Known Administrative Scope
    |
    v
Minimal Validation
```

---

# NetExec

NetExec can help assess administrative access across authorised systems.

See:

[NetExec](netexec.md)

Avoid uncontrolled domain-wide authentication attempts.

Use a scoped host list.

---

# Impacket

Impacket provides many tools relevant to Active Directory assessment.

See:

[Impacket](impacket.md)

The presence of an Impacket technique in a playbook does not mean it should automatically be executed.

Use the least invasive validation method that establishes the security impact.

---

# PowerView

PowerView can help enumerate:

```text
Users
Groups
Computers
ACLs
Trusts
Sessions
Delegation
```

Verify commands against the specific PowerView version loaded into the assessment environment.

---

# Native Tools First

Where possible, use:

```text
ActiveDirectory PowerShell Module
whoami
nltest
dsquery
repadmin
Group Policy Tools
Windows Event Logs
```

for read-only validation.

This often produces cleaner evidence than immediately using offensive tooling.

---

# Privilege Escalation Methodology

A structured methodology is:

```text
Establish Context
      |
      v
Enumerate Identity
      |
      v
Enumerate Groups
      |
      v
Enumerate ACLs
      |
      v
Enumerate Credentials
      |
      v
Enumerate Delegation
      |
      v
Enumerate GPOs
      |
      v
Enumerate AD CS
      |
      v
Enumerate Trusts
      |
      v
Model Paths
      |
      v
Validate Safely
      |
      v
Report
```

---

# Phase 1 - Establish Current Context

Record:

```text
Username
SID
Domain
Groups
Privileges
Host
Network
Authentication Context
```

---

# Phase 2 - Identify High-Value Targets

Examples:

```text
Domain Controllers
Certificate Authorities
AD FS
Management Servers
Backup Servers
Virtualisation Platforms
Tier 0 Systems
Privileged Groups
```

---

# Phase 3 - Enumerate Group Paths

Look for:

```text
Direct Membership
Nested Membership
Group Management Rights
Foreign Group Membership
```

---

# Phase 4 - Enumerate ACL Paths

Review:

```text
Users
Groups
Computers
OUs
GPOs
Domain Root
AdminSDHolder
```

for rights held by the current identity and its groups.

---

# Phase 5 - Enumerate Credential Paths

Review authorised sources such as:

```text
Shares
Scripts
Configuration Files
Services
Scheduled Tasks
Deployment Infrastructure
Managed Credentials
```

---

# Phase 6 - Enumerate Kerberos Paths

Review:

```text
SPNs
Kerberoasting
AS-REP Roasting
Delegation
Tickets
Service Accounts
```

---

# Phase 7 - Enumerate NTLM Paths

Review:

```text
NTLM Usage
Signing
Relay Exposure
Authentication Coercion
Credential Reuse
```

---

# Phase 8 - Enumerate AD CS

Determine:

```text
Enterprise CAs
Templates
Enrollment Rights
Template Permissions
CA Permissions
Web Enrollment
Authentication Mapping
```

---

# Phase 9 - Enumerate Infrastructure

Review:

```text
SCCM
WSUS
MDT
SCOM
AD FS
RODC
Shares
DNS
Backup Systems
```

---

# Phase 10 - Enumerate Trusts

Determine whether privilege extends into:

```text
Other Domains
Other Forests
Partner Environments
```

through legitimate trust and authorisation relationships.

---

# Phase 11 - Build Attack Paths

Combine relationships:

```text
Identity
   |
   v
Permission
   |
   v
Object
   |
   v
New Capability
   |
   v
Higher Privilege
```

---

# Phase 12 - Prioritise Paths

Prefer paths that are:

```text
High Confidence
Low Impact
Easy to Explain
Easy to Remediate
```

Avoid unnecessary destructive validation.

---

# Phase 13 - Validate

Use the minimum action required to prove:

```text
Permission Exists
+
Target Is Sensitive
+
Privilege Path Is Real
```

Examples of low-impact evidence include:

```text
ACL Output
Group Membership
BloodHound Relationship
Read Permission
Configuration Evidence
Effective Policy
```

---

# Phase 14 - Cleanup

If explicit active validation required temporary changes:

```text
Remove Test Membership
Restore ACL
Remove Test Object
Remove Test Certificate
Restore Configuration
Verify Original State
```

Record cleanup evidence.

---

# Phase 15 - Report the Root Cause

Do not report only:

```text
Domain Admin Was Obtained
```

Explain the actual weakness.

For example:

```text
Helpdesk Group Can Modify Membership of Server Administrators
```

or:

```text
Low-Privilege User Can Modify a GPO Applied to Privileged Servers
```

---

# Attack Path vs Finding

An attack path may contain several weaknesses:

```text
User
 |
 v
Writable Group
 |
 v
Server Admin
 |
 v
Credential Exposure
 |
 v
Domain Admin
```

Possible findings could include:

```text
Excessive Group Management Permission
Privileged Credentials Used on Lower-Tier Server
Administrative Tiering Failure
```

Report root causes rather than only the final outcome.

---

# Detection

Privilege escalation detection requires visibility across:

```text
Identity
Endpoint
Directory
Authentication
Network
Certificate Infrastructure
```

---

# Group Membership Changes

Relevant Security events include:

```text
4728
4729
4732
4733
4756
4757
```

depending on group type and scope.

Monitor privileged groups particularly closely.

---

# User Account Changes

Relevant events can include:

```text
4723
4724
4738
```

depending on the action performed.

---

# Directory Object Changes

With Directory Service Changes auditing:

```text
5136
```

can provide visibility into modified Active Directory attributes.

This is particularly useful for:

```text
ACL Changes
Delegation Changes
Key Credential Changes
Object Attribute Changes
```

when appropriate SACLs are configured.

---

# Object Creation

Events such as:

```text
4741
```

can provide visibility into computer-account creation.

This can be useful when monitoring unexpected machine-account creation.

---

# GPO Changes

Monitor:

```text
GPO Creation
GPO Modification
GPO Links
SYSVOL Changes
```

and correlate changes with authorised administration.

---

# Authentication Events

Relevant events include:

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

depending on the authentication path.

---

# Special Privileges

Event:

```text
4672
```

can indicate special privileges assigned to a new logon.

It is useful context but should not be treated as malicious by itself.

---

# Kerberos Monitoring

Monitor unusual:

```text
TGT Requests
Service Ticket Requests
Encryption Types
Service Accounts
Source Hosts
```

Correlate Kerberos events with identity and endpoint telemetry.

---

# Certificate Monitoring

For AD CS environments, monitor:

```text
Enrollment
Template Changes
CA Changes
Certificate Authentication
Privileged Certificate Use
```

See the AD CS notes for detailed detection guidance.

---

# ACL Monitoring

Sensitive objects should have auditing appropriate to their risk.

Examples:

```text
Domain Root
AdminSDHolder
Privileged Groups
Tier 0 OUs
Certificate Templates
GPOs
```

---

# BloodHound for Defenders

BloodHound can also be used defensively to identify:

```text
Unexpected Paths
Excessive ACLs
Nested Privilege
Local Administrator Relationships
Session Exposure
```

Attack-path reduction is a useful hardening objective.

---

# Hardening

Active Directory privilege escalation is best reduced through multiple controls.

```text
Least Privilege
      +
Administrative Tiering
      +
Credential Protection
      +
ACL Hygiene
      +
Group Hygiene
      +
Secure Delegation
      +
AD CS Hardening
      +
Monitoring
```

---

# Reduce Privileged Membership

Keep membership of:

```text
Domain Admins
Enterprise Admins
Schema Admins
Administrators
```

as small as operationally possible.

Avoid permanent privileged membership where just-in-time models are available.

---

# Review Nested Groups

A privileged group may appear clean while containing another broadly managed group.

Review:

```text
Direct Members
Nested Members
Who Can Modify Each Group
```

---

# Review ACLs

Periodically identify non-standard permissions on:

```text
Domain
OUs
Users
Groups
Computers
GPOs
AdminSDHolder
Certificate Infrastructure
```

---

# Restrict WriteDacl and WriteOwner

These permissions can create indirect object control.

Grant them only where operationally necessary.

---

# Protect Group Management

Separate:

```text
Helpdesk Functions
```

from:

```text
Privileged Group Management
```

A password-reset role should not automatically provide control over Tier 0 accounts.

---

# Protect Service Accounts

Use:

```text
gMSA
Long Random Passwords
Least Privilege
Restricted Logon
Minimal Group Membership
```

where appropriate.

---

# Deploy LAPS

Use Windows LAPS to reduce local administrator password reuse.

Then protect:

```text
Who Can Read LAPS Passwords
```

with least privilege.

---

# Harden Kerberos

Review:

```text
Preauthentication
Service Accounts
Delegation
Encryption Types
SPNs
Privileged Authentication
```

---

# Reduce NTLM

Where operationally feasible, reduce NTLM dependency and apply protections such as:

```text
SMB Signing
LDAP Signing
LDAP Channel Binding
Extended Protection for Authentication
```

where applicable.

---

# Harden AD CS

Review:

```text
Templates
Enrollment Rights
CA Permissions
Web Enrollment
Authentication Mapping
Private Keys
```

AD CS should be treated as identity infrastructure.

---

# Protect Management Infrastructure

Systems capable of administering large portions of the environment should be treated as high-value assets.

Examples:

```text
SCCM
MDT
Backup Platforms
Virtualisation
Monitoring
AD FS
Certificate Authorities
```

---

# Administrative Tiering

Do not allow Tier 0 identities to routinely authenticate to:

```text
Workstations
User Servers
Internet-Facing Systems
Lower-Tier Management Systems
```

---

# Dedicated Admin Accounts

Separate:

```text
Daily User Account
```

from:

```text
Administrative Account
```

and further separate privilege tiers where appropriate.

---

# Privileged Workstations

Use dedicated hardened management endpoints for sensitive administration.

---

# Remove Stale Privilege

Regularly review:

```text
Old Groups
Former Administrators
Unused Delegations
Old Service Accounts
Legacy GPO Rights
Stale ACL Entries
```

---

# Protect Domain Controllers

Restrict:

```text
Interactive Logon
RDP
WinRM
SMB Administration
Management Tools
Internet Access
```

according to the domain-controller management model.

---

# Monitor Attack Paths

Privilege is dynamic.

Changes to:

```text
Group Membership
ACLs
Sessions
Computers
Trusts
Certificates
```

can create new escalation paths.

Continuous or periodic path analysis is therefore valuable.

---

# Reporting Privilege Escalation

A useful finding explains:

```text
Starting Identity
      |
      v
Misconfiguration
      |
      v
Affected Object
      |
      v
Resulting Privilege
      |
      v
Business Impact
```

---

# Example Finding - Group Control

```text
Finding:
Low-Privilege Group Can Modify Membership of a Privileged Server Group

Description:
Members of the Helpdesk group were able to modify the membership of a
group that grants administrative access to sensitive management
servers.

The assessment confirmed the Active Directory permission through
read-only ACL analysis.

No production group membership was modified.

Impact:
A compromised Helpdesk account could potentially grant an attacker
administrative access to sensitive servers.

Those systems may contain privileged sessions, credentials or
management capabilities that provide additional paths through the
Active Directory environment.

Recommendation:
Remove the unnecessary group-management permission.

Delegate Helpdesk functionality through dedicated least-privileged
groups that cannot modify administrative groups.

Review equivalent ACL relationships throughout Active Directory.
```

---

# Example Finding - GPO Control

```text
Finding:
Non-Privileged Users Can Modify a GPO Applied to Privileged Servers

Description:
A non-administrative Active Directory group had modification rights
over a Group Policy Object linked to an OU containing sensitive
servers.

The assessment verified the ACL and GPO link without modifying the
policy.

Impact:
A principal capable of modifying the GPO could potentially influence
configuration applied to the affected computers.

If the policy is processed by privileged systems, this may provide a
path to administrative code execution or security-control
modification.

Recommendation:
Restrict modification of the GPO to dedicated authorised
administrators.

Review all GPO ACLs and links associated with privileged systems.
```

---

# Example Finding - LAPS

```text
Finding:
Excessive Users Can Read Local Administrator Credentials for Sensitive Servers

Description:
A broad Active Directory group had permission to retrieve managed local
administrator credentials for servers outside its operational
responsibility.

The assessment validated the directory permission without using the
credential to authenticate to production systems.

Impact:
Compromise of any account in the affected group could provide local
administrative access to sensitive servers.

Those systems may expose additional credentials or privileged
management capabilities.

Recommendation:
Restrict LAPS password-read permissions to dedicated administrative
roles with a documented operational requirement.

Review inherited permissions and audit access to managed local
administrator credentials.
```

---

# Example Finding - Replication Rights

```text
Finding:
Non-Domain-Controller Account Has Excessive Directory Replication Rights

Description:
An account outside the expected domain-controller and identity
management roles possessed directory replication permissions on the
domain object.

The assessment verified the permissions through ACL analysis and did
not request password data through directory replication.

Impact:
Sufficient replication permissions may allow an account to request
sensitive Active Directory credential material from a domain
controller.

This can lead to compromise of highly privileged identities and
potential domain-wide impact.

Recommendation:
Remove unnecessary directory replication permissions.

Restrict replication rights to domain controllers and explicitly
approved identity-management systems.

Review historical delegation to identify additional accounts with
equivalent permissions.
```

---

# Example Finding - Privileged Credential Exposure

```text
Finding:
Privileged Credentials Are Exposed on a Lower-Tier Management Server

Description:
A highly privileged administrative identity routinely authenticated to
a management server administered by a broader group of operators.

The server was outside the intended privileged administrative tier.

Impact:
Compromise of the lower-tier server may expose authentication material,
sessions or administrative workflows associated with the privileged
identity.

This can create a path from lower-tier server administration to
higher-value Active Directory assets.

Recommendation:
Prevent Tier 0 identities from authenticating to lower-trust systems.

Use dedicated administrative accounts and privileged access
workstations appropriate to each administrative tier.
```

---

# Example Finding - AD CS Path

```text
Finding:
Certificate Template Configuration Provides a Path to Privileged Authentication

Description:
A certificate template available to a lower-privileged population
contained a combination of permissions and authentication properties
that could permit authentication in a higher-privileged identity
context.

The assessment validated the template and CA configuration without
requesting a certificate for a privileged production identity.

Impact:
A compromised low-privilege account could potentially obtain
certificate-based authentication material that provides additional
Active Directory privilege.

Recommendation:
Restrict template enrollment and modification rights.

Review certificate subject configuration, authentication purposes,
mapping behaviour and CA settings according to the specific AD CS
misconfiguration identified.
```

---

# Privilege Escalation Checklist

## Current Identity

- [ ] Identify current username
- [ ] Identify SID
- [ ] Identify domain
- [ ] Enumerate groups
- [ ] Enumerate token privileges
- [ ] Identify current host
- [ ] Identify authentication context

## Domain

- [ ] Enumerate domain
- [ ] Enumerate forest
- [ ] Enumerate domain controllers
- [ ] Enumerate sites
- [ ] Identify Tier 0 systems

## Groups

- [ ] Enumerate privileged groups
- [ ] Enumerate nested membership
- [ ] Identify group owners
- [ ] Identify group-management rights
- [ ] Identify stale privileged members
- [ ] Identify foreign members

## ACLs

- [ ] Review user ACLs
- [ ] Review group ACLs
- [ ] Review computer ACLs
- [ ] Review OU ACLs
- [ ] Review GPO ACLs
- [ ] Review domain ACL
- [ ] Review AdminSDHolder
- [ ] Identify GenericAll
- [ ] Identify GenericWrite
- [ ] Identify WriteDacl
- [ ] Identify WriteOwner
- [ ] Identify password-reset rights
- [ ] Identify group membership rights
- [ ] Identify replication rights

## Credentials

- [ ] Review authorised shares
- [ ] Review scripts
- [ ] Review configuration files
- [ ] Review scheduled tasks
- [ ] Review services
- [ ] Review deployment systems
- [ ] Review PowerShell history where appropriate
- [ ] Review service accounts
- [ ] Avoid unnecessary credential extraction

## Kerberos

- [ ] Identify SPNs
- [ ] Review Kerberoastable accounts
- [ ] Review AS-REP roastable accounts
- [ ] Review unconstrained delegation
- [ ] Review constrained delegation
- [ ] Review RBCD
- [ ] Review S4U relationships
- [ ] Review privileged ticket exposure

## NTLM

- [ ] Identify NTLM dependencies
- [ ] Review SMB signing
- [ ] Review LDAP signing
- [ ] Review LDAP channel binding
- [ ] Review EPA where applicable
- [ ] Review relay exposure
- [ ] Review authentication coercion
- [ ] Review credential reuse

## Managed Credentials

- [ ] Review LAPS
- [ ] Review LAPS read permissions
- [ ] Review gMSA
- [ ] Review gMSA retrieval permissions
- [ ] Review service-account privilege

## Machine Accounts

- [ ] Review MachineAccountQuota
- [ ] Review computer creation permissions
- [ ] Review computer object ACLs
- [ ] Review delegation attributes
- [ ] Review key credential attributes

## Group Policy

- [ ] Enumerate GPOs
- [ ] Review GPO ACLs
- [ ] Review GPO links
- [ ] Review security filtering
- [ ] Review privileged targets
- [ ] Review SYSVOL permissions
- [ ] Search for legacy GPP credentials

## AD CS

- [ ] Enumerate CAs
- [ ] Enumerate templates
- [ ] Review enrollment rights
- [ ] Review template ACLs
- [ ] Review CA permissions
- [ ] Review certificate mapping
- [ ] Review web enrollment
- [ ] Review ESC conditions
- [ ] Validate current patch behaviour

## Trusts

- [ ] Enumerate domain trusts
- [ ] Enumerate forest trusts
- [ ] Review direction
- [ ] Review transitivity
- [ ] Review authentication scope
- [ ] Review foreign principals
- [ ] Review SID History
- [ ] Review privileged cross-domain membership

## Infrastructure

- [ ] Review ADIDNS
- [ ] Review shares
- [ ] Review SCCM
- [ ] Review WSUS
- [ ] Review MDT
- [ ] Review SCOM
- [ ] Review AD FS
- [ ] Review RODCs
- [ ] Review backup infrastructure
- [ ] Review virtualisation infrastructure

## Attack Paths

- [ ] Run BloodHound analysis
- [ ] Identify shortest paths
- [ ] Validate each edge
- [ ] Check network reachability
- [ ] Check authentication requirements
- [ ] Check endpoint controls
- [ ] Prioritise low-impact validation
- [ ] Identify root causes

## Detection

- [ ] Monitor privileged group changes
- [ ] Monitor ACL changes
- [ ] Monitor GPO changes
- [ ] Monitor privileged logons
- [ ] Monitor Kerberos
- [ ] Monitor NTLM
- [ ] Monitor certificate activity
- [ ] Monitor computer creation
- [ ] Monitor service-account activity
- [ ] Centralise logs

## Hardening

- [ ] Reduce privileged membership
- [ ] Review nested groups
- [ ] Remove stale privilege
- [ ] Harden ACLs
- [ ] Protect AdminSDHolder
- [ ] Restrict replication rights
- [ ] Deploy LAPS
- [ ] Use gMSA where appropriate
- [ ] Harden delegation
- [ ] Harden AD CS
- [ ] Reduce NTLM
- [ ] Apply administrative tiering
- [ ] Use dedicated admin accounts
- [ ] Use privileged workstations
- [ ] Protect management infrastructure
- [ ] Restrict Domain Controller administration

## Reporting

- [ ] Identify starting identity
- [ ] Identify exact permission
- [ ] Identify affected object
- [ ] Identify resulting capability
- [ ] Identify privilege gained
- [ ] Explain complete attack path
- [ ] Report root cause
- [ ] Avoid unnecessary active exploitation
- [ ] Redact credentials
- [ ] Provide targeted remediation
- [ ] Record cleanup where applicable

---

# Privilege Escalation Testing Model

The basic model is:

```text
Current Identity
      |
      v
Permission
      |
      v
Target
      |
      v
New Capability
      |
      v
Higher Privilege
```

The group model is:

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
Privilege
```

The ACL model is:

```text
User
 |
 v
ACE
 |
 v
Object Control
 |
 v
Privilege
```

The credential model is:

```text
Low-Privilege Context
       |
       v
Credential Exposure
       |
       v
Higher-Privilege Identity
```

The delegation model is:

```text
Principal
    |
    v
Kerberos Delegation
    |
    v
Target Service
    |
    v
Additional Privilege
```

The GPO model is:

```text
User
 |
 v
GPO Control
 |
 v
Linked Computers
 |
 v
Privileged Execution Context
```

The certificate model is:

```text
Identity
 |
 v
Certificate Configuration
 |
 v
Authentication Certificate
 |
 v
Privileged Identity
```

The replication model is:

```text
Account
 |
 v
Replication Rights
 |
 v
Directory Secrets
 |
 v
Domain Impact
```

The infrastructure model is:

```text
User
 |
 v
Management Platform
 |
 v
Managed Systems
 |
 v
Privileged Infrastructure
```

The attack-path model is:

```text
User
 |
 +--> Group
 |
 +--> ACL
 |
 +--> Credential
 |
 +--> Computer
 |
 +--> Session
 |
 +--> Certificate
 |
 +--> Trust
 |
 v
Privilege
```

The most important distinction is:

```text
Potential Path
!=
Confirmed Exploitability
```

Validate each relationship.

Another important distinction is:

```text
Privilege Escalation
!=
Only Domain Admin
```

Escalation can mean moving from:

```text
User
```

to:

```text
Local Administrator
```

or:

```text
Application Administrator
```

or:

```text
Server Administrator
```

or:

```text
Certificate Administrator
```

or:

```text
Domain Administrator
```

or:

```text
Forest Administrator
```

The security objective is to prevent unintended transitions between these privilege levels.

For penetration testers:

```text
Do Not Ask:
"What exploit gives me Domain Admin?"

Ask:
"What relationships allow my current
identity to obtain additional control,
and what is the least invasive way to
prove that path?"
```

For defenders:

```text
Do Not Ask:
"Who is currently Domain Admin?"

Ask:
"Who can become privileged through
groups, ACLs, credentials, delegation,
certificates, management systems or
trust relationships?"
```

The complete model is:

```text
Identity
   |
   v
Groups
   |
   v
Permissions
   |
   v
Systems
   |
   v
Credentials
   |
   v
Delegation
   |
   v
Certificates
   |
   v
Trust
   |
   v
Privilege
```

Privilege escalation should therefore be assessed as a chain of security relationships rather than as a collection of isolated exploits.

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Methodology:

[Methodology](methodology.md)

Enumeration:

[Enumeration](enumeration.md)

BloodHound:

[BloodHound](bloodhound.md)

Groups:

[Groups](groups.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Group Policy:

[Group Policy](group-policy.md)

Credential Access:

[Credential Access](credential-access.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

AS-REP Roasting:

[AS-REP Roasting](asrep-roasting.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

Constrained Delegation:

[Constrained Delegation](constrained-delegation.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[S4U](s4u.md)

Machine Account Quota:

[Machine Account Quota](machine-account-quota.md)

Shadow Credentials:

[Shadow Credentials](shadow-credentials.md)

LAPS:

[LAPS](laps.md)

gMSA:

[gMSA](gmsa.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

Authentication Coercion:

[Authentication Coercion](authentication-coercion.md)

Active Directory Certificate Services:

[Active Directory Certificate Services](ad-cs/index.md)

Trusts:

[Trusts](trusts.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

Pivoting:

[Pivoting](pivoting.md)

Shares:

[Shares](shares.md)

SCCM:

[SCCM](sccm.md)

WSUS:

[WSUS](wsus.md)

MDT:

[MDT](mdt.md)

SCOM:

[SCOM](scom.md)

AD FS:

[AD FS](adfs.md)

RODC:

[RODC](rodc.md)

---

# References

## Microsoft - Active Directory Domain Services

[Microsoft Learn - Active Directory Domain Services Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Security Groups

[Microsoft Learn - Active Directory Security Groups](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Delegation of Control

[Microsoft Learn - Delegating Administration](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/delegating-administration-by-using-ou-objects){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Securing Privileged Access

[Microsoft Learn - Securing Privileged Access](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft Learn - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Group Managed Service Accounts

[Microsoft Learn - Group Managed Service Accounts](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Kerberos

[Microsoft Learn - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Protected Users

[Microsoft Learn - Protected Users Security Group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - BloodHound

[SpecterOps - BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Account Manipulation

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Valid Accounts

[MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Steal or Forge Kerberos Tickets

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - OS Credential Dumping

[MITRE ATT&CK - OS Credential Dumping](https://attack.mitre.org/techniques/T1003/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Abuse Elevation Control Mechanism

[MITRE ATT&CK - Abuse Elevation Control Mechanism](https://attack.mitre.org/techniques/T1548/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Active Directory privilege escalation should be approached as:

```text
Relationship Analysis
```

rather than simply:

```text
Exploit Execution
```

The fundamental question is:

```text
What Can My Current Identity Control?
```

Then:

```text
What Does That Control Give Me?
```

Then:

```text
Can That New Capability Reach
Something More Privileged?
```

This produces the iterative model:

```text
Identity
   |
   v
Permission
   |
   v
Capability
   |
   v
New Identity / System
   |
   v
Permission
   |
   v
Capability
   |
   v
Privilege
```

A seemingly harmless permission can become critical when chained with another relationship.

For example:

```text
Helpdesk
   |
   v
Can Modify Group
   |
   v
Server Administrators
   |
   v
Management Server
   |
   v
Privileged Session
   |
   v
Tier 0
```

The root cause is not necessarily:

```text
Privileged Session
```

It may instead be:

```text
Excessive Group Delegation
+
Administrative Tiering Failure
```

The strongest Active Directory assessments therefore combine:

```text
Enumeration
+
BloodHound
+
ACL Analysis
+
Credential Analysis
+
Kerberos
+
NTLM
+
Delegation
+
Group Policy
+
AD CS
+
Trusts
+
Infrastructure
```

with:

```text
Minimal Validation
```

The goal is to establish the complete privilege path while creating as little production impact as possible.

The defensive objective is equally clear:

```text
Remove Unnecessary Paths
```

because an identity does not need to be a member of:

```text
Domain Admins
```

to represent a path to domain compromise.

The next major Active Directory topic is:

```text
Persistence
```
