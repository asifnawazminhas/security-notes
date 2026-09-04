# Read-Only Domain Controller - RODC

A Read-Only Domain Controller, commonly abbreviated:

```text
RODC
```

is an Active Directory Domain Services domain controller designed for locations where the physical or administrative security of a normal writable domain controller cannot be guaranteed.

An RODC contains a:

```text
Read-Only Copy
```

of most Active Directory database data.

A simplified architecture is:

```text
Writable Domain Controller
          |
          | Replication
          v
         RODC
          |
          v
   Branch Office Users
```

Unlike a standard writable domain controller, an RODC does not normally accept originating Active Directory changes.

Changes must be made against a writable domain controller and then replicated to the RODC.

RODCs introduce several important security concepts:

```text
Read-Only Directory Database
Password Replication Policy
Credential Caching
Filtered Attribute Set
Unidirectional Replication
Administrator Role Separation
RODC Computer Account
krbtgt_<RODC-ID>
```

These mechanisms make RODCs particularly relevant during assessments of:

```text
Branch Offices
Remote Locations
Physical Security
Credential Exposure
Kerberos
Replication
Privileged Accounts
```

!!! warning "Authorised testing only"
    Domain controllers are critical identity infrastructure. Do not modify Password Replication Policy settings, trigger password replication for privileged accounts, alter RODC replication, extract `ntds.dit`, access cached secrets, modify the RODC krbtgt account or perform replication abuse against production domain controllers unless explicitly authorised. Prefer read-only enumeration and configuration analysis.

---

# Why RODCs Exist

A traditional writable domain controller contains sensitive Active Directory information and can originate directory changes.

Deploying one in a location with weak physical security creates risk.

Examples include:

```text
Branch Office
Retail Location
Remote Site
Manufacturing Facility
Temporary Site
Edge Location
```

Microsoft introduced RODCs to reduce this risk.

Conceptually:

```text
Head Office
   |
   +--> Secure Data Centre
   |       |
   |       v
   |    Writable DC
   |
   v
Branch Office
       |
       v
      RODC
```

If the branch server is physically compromised, the security objective is to reduce the credentials and directory capabilities exposed compared with a writable DC.

---

# RODC Is Not Automatically a Vulnerability

Do not report:

```text
RODC Exists
```

as a security finding.

An RODC can be an intentional security control.

Instead determine:

```text
Why Is the RODC Deployed?
Where Is It Located?
Which Credentials Can It Cache?
Which Credentials Has It Cached?
Who Administers It?
Which Writable DC Replicates to It?
Is the Filtered Attribute Set Appropriate?
Is the RODC Properly Patched?
Is Physical Access Controlled?
```

---

# Writable DC vs RODC

A normal domain controller provides:

```text
Writable AD Database
Bidirectional Replication
Credential Storage
Kerberos
LDAP
DNS
Authentication
```

An RODC changes several of these properties.

```text
Writable DC
    |
    +--> Writable Directory
    +--> Originates Changes
    +--> Replicates Changes
    +--> Stores Required Credentials

RODC
    |
    +--> Read-Only Directory
    +--> Normally Does Not Originate AD Changes
    +--> Receives Replication
    +--> Selectively Caches Credentials
```

---

# High-Level Security Model

```text
Writable DC
     |
     | Directory Replication
     v
    RODC
     |
     +--> Read-Only AD Database
     |
     +--> Selected Cached Credentials
     |
     +--> DNS
     |
     +--> LDAP
     |
     +--> Kerberos
     |
     +--> Authentication
```

The central security principle is:

```text
Limit What a Compromised RODC Exposes
```

---

# Read-Only Active Directory Database

An RODC stores a local copy of:

```text
ntds.dit
```

like other domain controllers.

However, its directory partitions are primarily read-only.

Conceptually:

```text
Client
 |
 v
RODC
 |
 X
Direct AD Modification
```

Instead:

```text
Client
 |
 v
Writable DC
 |
 v
Directory Change
 |
 v
Replication
 |
 v
RODC
```

---

# Read-Only Does Not Mean Low Value

An RODC still contains substantial Active Directory information.

Potentially visible information includes:

```text
Users
Groups
Computers
Organisational Units
Group Policy References
SPNs
Trust Information
Directory Metadata
DNS Information
```

Therefore:

```text
Read-Only
!=
Non-Sensitive
```

---

# Authentication

An RODC can authenticate users locally when the required credential material has been cached.

Conceptually:

```text
User
 |
 v
RODC
 |
 +--> Credential Cached?
        |
        +--> Yes
        |     |
        |     v
        |  Local Authentication
        |
        +--> No
              |
              v
        Writable DC
```

The exact behaviour depends on:

```text
Connectivity
Password Replication Policy
Credential State
Authentication Protocol
```

---

# Password Replication Policy

One of the most important RODC security controls is the:

```text
Password Replication Policy - PRP
```

The PRP determines which account credentials may be cached on an RODC.

Conceptually:

```text
Account
   |
   v
Password Replication Policy
   |
   +--> Allowed
   |      |
   |      v
   |   May Be Cached
   |
   +--> Denied
          |
          v
      Must Not Be Cached
```

---

# Why PRP Matters

A branch-office RODC may serve:

```text
50 Local Users
```

but the domain may contain:

```text
50,000 Users
```

There is normally no reason for the RODC to cache all 50,000 credentials.

The preferred model is:

```text
RODC
 |
 +--> Branch Users
 +--> Branch Computers
 |
 X--> Domain Admins
 X--> Enterprise Admins
 X--> Sensitive Service Accounts
```

---

# PRP Allow and Deny Groups

RODC deployments commonly use groups that control password replication.

Two important built-in groups are:

```text
Allowed RODC Password Replication Group
```

and:

```text
Denied RODC Password Replication Group
```

---

# Allowed RODC Password Replication Group

Accounts associated with:

```text
Allowed RODC Password Replication Group
```

may be eligible for credential caching by RODCs, subject to the effective PRP.

Do not interpret membership alone as proof that a password is currently cached.

The distinction is:

```text
Allowed to Cache
!=
Already Cached
```

---

# Denied RODC Password Replication Group

Sensitive accounts should generally be prevented from having their credentials cached on RODCs.

The built-in:

```text
Denied RODC Password Replication Group
```

helps protect privileged identities.

---

# Typical Sensitive Accounts

Examples that should receive particular attention include:

```text
Domain Admins
Enterprise Admins
Schema Admins
Domain Controllers
krbtgt
Highly Privileged Service Accounts
Tier 0 Administrators
```

The exact effective policy should always be enumerated rather than assumed.

---

# Deny Should Win

When evaluating the effective Password Replication Policy, remember that a denial can override an allow relationship.

Therefore do not simply inspect:

```text
Allowed Group Membership
```

in isolation.

Determine the:

```text
Effective PRP
```

for the account.

---

# Credential Caching

An RODC does not necessarily contain every domain user's password-derived credential material.

Credential caching is selective.

Conceptually:

```text
Domain
 |
 +--> User01 --> Cached
 |
 +--> User02 --> Cached
 |
 +--> User03 --> Not Cached
 |
 +--> Admin01 --> Denied
```

---

# Why Cached Credentials Matter

If an RODC is compromised, cached credentials may become part of the compromise scope.

The security question becomes:

```text
Which Accounts Had Credential Material
Stored on This RODC?
```

This is particularly important during incident response.

---

# Allowed vs Revealed Accounts

RODC analysis should distinguish between:

```text
Accounts Allowed to Cache
```

and:

```text
Accounts Whose Passwords Were Actually Revealed to the RODC
```

These are not equivalent.

---

# msDS-RevealOnDemandGroup

The RODC computer object can contain:

```text
msDS-RevealOnDemandGroup
```

This attribute contributes to defining identities whose passwords may be cached.

---

# msDS-NeverRevealGroup

Another important attribute is:

```text
msDS-NeverRevealGroup
```

This identifies principals whose password information should not be revealed to the RODC.

---

# msDS-RevealedList

The RODC computer object can also expose:

```text
msDS-RevealedList
```

which can help identify accounts whose credentials have been revealed to the RODC.

This is highly useful during security assessment and incident response.

---

# PRP Model

```text
msDS-RevealOnDemandGroup
           |
           v
       May Cache
           |
           v
          RODC

msDS-NeverRevealGroup
           |
           v
       Must Not Cache
```

Actual cached credential history can then be assessed separately.

---

# Enumerating RODCs

Using the Active Directory PowerShell module:

```powershell
Get-ADDomainController -Filter * |
    Select-Object HostName,Site,IsReadOnly,IPv4Address
```

RODCs should have:

```text
IsReadOnly = True
```

---

# Enumerate Only RODCs

```powershell
Get-ADDomainController -Filter * |
    Where-Object {
        $_.IsReadOnly -eq $true
    } |
    Select-Object HostName,Site,IPv4Address
```

---

# Enumerate a Specific RODC

```powershell
Get-ADDomainController -Identity 'RODC01'
```

Review:

```text
HostName
Site
IPv4Address
IsReadOnly
OperatingSystem
```

where available.

---

# Enumerate Domain Controllers

A broader domain-controller inventory:

```powershell
Get-ADDomainController -Filter * |
    Format-Table HostName,Site,IsReadOnly,IPv4Address
```

This helps compare writable DC and RODC placement.

---

# nltest

Native Windows tooling can also identify domain controllers.

Example:

```cmd
nltest /dclist:corp.example
```

This provides a useful domain-controller inventory.

---

# DNS SRV Records

Domain controllers can also be discovered through DNS.

Linux:

```bash
dig _ldap._tcp.dc._msdcs.corp.example SRV
```

Kerberos:

```bash
dig _kerberos._tcp.corp.example SRV
```

See:

[Active Directory Integrated DNS](adidns.md)

---

# RODC Computer Object

An RODC has a computer object in Active Directory.

Example:

```powershell
Get-ADComputer -Identity 'RODC01' -Properties *
```

This can expose RODC-specific attributes.

---

# Enumerate PRP Attributes

```powershell
Get-ADComputer -Identity 'RODC01' -Properties msDS-RevealOnDemandGroup,msDS-NeverRevealGroup,msDS-RevealedList |
    Select-Object Name,msDS-RevealOnDemandGroup,msDS-NeverRevealGroup,msDS-RevealedList
```

This is a useful read-only assessment command.

---

# Get-ADDomainControllerPasswordReplicationPolicy

Microsoft's Active Directory PowerShell module provides:

```powershell
Get-ADDomainControllerPasswordReplicationPolicy
```

for examining an RODC's Password Replication Policy.

---

# Accounts Allowed by PRP

Example:

```powershell
Get-ADDomainControllerPasswordReplicationPolicy -Identity 'RODC01' -Allowed
```

This identifies accounts represented by the allowed side of the PRP.

---

# Accounts Denied by PRP

```powershell
Get-ADDomainControllerPasswordReplicationPolicy -Identity 'RODC01' -Denied
```

This identifies accounts represented by the denied side.

---

# Effective PRP

For a specific account, use:

```powershell
Get-ADDomainControllerPasswordReplicationPolicyUsage -Identity 'RODC01'
```

Microsoft provides PRP-related cmdlets for examining resulting password-replication state and usage.

Use:

```powershell
Get-Help Get-ADDomainControllerPasswordReplicationPolicy -Full
```

and:

```powershell
Get-Help Get-ADDomainControllerPasswordReplicationPolicyUsage -Full
```

on the assessment host to confirm syntax for the installed Active Directory module.

---

# Replicated Accounts

A particularly useful assessment question is:

```text
Which Accounts Have Actually Had Credentials
Replicated to This RODC?
```

Use the supported PRP usage cmdlets and RODC attributes rather than assuming that every allowed identity is cached.

---

# Why Effective PRP Analysis Matters

Consider:

```text
Branch-Users
    |
    v
Allowed

Domain Admin
    |
    v
Nested Group
    |
    v
Unexpectedly Allowed?
```

Simply reviewing the visible top-level groups may miss nested relationships.

---

# Group Membership

Review built-in PRP groups:

```powershell
Get-ADGroupMember -Identity 'Allowed RODC Password Replication Group' -Recursive
```

and:

```powershell
Get-ADGroupMember -Identity 'Denied RODC Password Replication Group' -Recursive
```

---

# Group Names and Localisation

Built-in group display names can differ in localised Windows environments.

Where necessary, identify the groups by Active Directory object properties rather than relying exclusively on English display names.

---

# Nested Groups

Nested group membership is particularly important.

Conceptually:

```text
Allowed PRP Group
      |
      v
Branch Users
      |
      v
Nested Group
      |
      v
Sensitive Account
```

Review recursive membership.

---

# RODC Account Security

Each RODC has a domain controller computer account.

The RODC also has an associated Kerberos service account with a unique identity.

This is an important difference from writable domain controllers.

---

# RODC krbtgt Account

Writable domain controllers rely on the domain:

```text
krbtgt
```

account for Kerberos ticket-granting operations.

RODCs additionally have a dedicated RODC-specific krbtgt account.

It commonly appears using a naming convention resembling:

```text
krbtgt_12345
```

where the numeric value corresponds to the RODC relationship.

---

# Why the RODC krbtgt Account Exists

The RODC-specific krbtgt account helps limit the impact of an RODC compromise.

Conceptually:

```text
Writable DC
   |
   v
Domain krbtgt

RODC
   |
   v
RODC-Specific krbtgt
```

The RODC does not possess the normal domain-wide krbtgt secret in the same way as a writable DC.

---

# Kerberos Isolation

The objective is:

```text
Compromised RODC
      |
      v
RODC-Specific Kerberos Secret
      |
      X
Should Not Automatically Become
Domain-Wide krbtgt Compromise
```

This limits the blast radius.

---

# RODC Kerberos Tickets

Tickets associated with RODC authentication contain information that allows writable domain controllers to distinguish tickets associated with an RODC.

This helps enforce the RODC trust model.

---

# RODC Identifier

RODCs have identifiers used in Kerberos and replication-related logic.

The associated RODC krbtgt account is linked to the RODC.

Do not manually manipulate this relationship during routine testing.

---

# Enumerate RODC krbtgt Accounts

A read-only search can identify RODC-specific krbtgt accounts:

```powershell
Get-ADUser -Filter 'SamAccountName -like "krbtgt_*"' -Properties *
```

For concise output:

```powershell
Get-ADUser -Filter 'SamAccountName -like "krbtgt_*"' -Properties Enabled,PasswordLastSet |
    Select-Object SamAccountName,Enabled,PasswordLastSet
```

---

# Do Not Confuse krbtgt Accounts

```text
krbtgt
```

and:

```text
krbtgt_<number>
```

serve different roles.

Compromise of:

```text
Domain krbtgt
```

has different implications from compromise of an RODC-specific krbtgt secret.

---

# RODC and Golden Tickets

Traditional Golden Ticket attacks rely on:

```text
Domain krbtgt Secret
```

An RODC-specific krbtgt compromise does not provide the same domain-wide trust position.

The scope is constrained by the RODC security model.

Do not describe an RODC krbtgt compromise as equivalent to compromise of the domain krbtgt account.

---

# RODC and Password Replication

An RODC requests password replication from a writable domain controller when required and permitted.

Conceptually:

```text
User Authenticates
      |
      v
RODC Has Credential?
      |
      +--> Yes
      |
      +--> No
            |
            v
       Writable DC
            |
            v
      Check PRP
            |
            +--> Allowed
            |      |
            |      v
            |   Replicate
            |
            +--> Denied
                   |
                   v
              Do Not Cache
```

---

# Prepopulation

Administrators can intentionally prepopulate credentials on an RODC.

This can be useful before deploying an RODC to a location with unreliable WAN connectivity.

Conceptually:

```text
Branch Users
     |
     v
Prepopulate
     |
     v
RODC
```

---

# Security Impact of Prepopulation

Prepopulation should be limited to identities that genuinely need local authentication at the site.

Avoid unnecessarily prepopulating:

```text
Privileged Administrators
Service Accounts
Users from Other Sites
Tier 0 Identities
```

---

# Do Not Prepopulate During Assessment

Do not trigger password prepopulation merely to test whether it works.

The assessment should review:

```text
PRP Configuration
Existing Cached State
Business Requirement
```

without increasing credential exposure.

---

# Unidirectional Replication

A major RODC security feature is that replication primarily flows:

```text
Writable DC
    |
    v
RODC
```

rather than allowing the RODC to originate normal directory updates back into Active Directory.

---

# Why This Matters

If an attacker changes the local directory database on a compromised RODC, the design aims to prevent those modifications from becoming authoritative changes replicated throughout the domain.

Conceptually:

```text
Compromised RODC
      |
      X
Malicious Directory Change
      |
      X
Writable DC
```

---

# RODC Replication Partner

Identify the writable DC used as a replication source.

Native tools can help inspect replication topology.

Example:

```cmd
repadmin /showrepl RODC01
```

This should be performed from an authorised administrative context.

---

# Repadmin

Useful read-only commands include:

```cmd
repadmin /showrepl RODC01
```

and:

```cmd
repadmin /replsummary
```

Avoid commands that force or modify replication unless explicitly authorised.

---

# Active Directory Sites

RODCs are commonly deployed according to:

```text
Active Directory Sites and Services
```

Review the RODC's site:

```powershell
Get-ADDomainController -Identity 'RODC01' |
    Select-Object HostName,Site,IsReadOnly
```

---

# Site Security

A branch site's design can affect:

```text
Authentication
Replication
DNS
Network Routing
Failover
```

Determine whether clients actually use the intended local RODC.

---

# DNS

An RODC can host:

```text
Read-Only DNS
```

when the DNS Server role and AD-integrated DNS are used.

This allows branch clients to resolve Active Directory-related names locally.

---

# Read-Only DNS

The DNS data is derived from Active Directory-integrated zones.

Conceptually:

```text
Writable DNS / AD
       |
       v
      RODC
       |
       v
Read-Only DNS Data
```

---

# DNS Updates

Because the RODC does not normally originate writable AD changes, dynamic DNS update behaviour differs from a writable DNS server.

Clients may be referred to a writable DNS server when an update is required.

---

# ADIDNS

See:

[Active Directory Integrated DNS](adidns.md)

when assessing:

```text
Dynamic Updates
Zone Permissions
DNS Records
Name Resolution
```

---

# Filtered Attribute Set

Another important RODC security mechanism is the:

```text
RODC Filtered Attribute Set - FAS
```

Certain attributes can be configured so that their values are not replicated to RODCs.

---

# Why the Filtered Attribute Set Exists

Some directory attributes may contain information that should not be present on a physically less secure domain controller.

Conceptually:

```text
Writable DC
   |
   +--> Normal Attribute ------> RODC
   |
   +--> Sensitive FAS Attribute -X-> RODC
```

---

# Confidential Attributes vs FAS

Do not assume that:

```text
Confidential Attribute
```

and:

```text
RODC Filtered Attribute Set
```

are the same mechanism.

An attribute specifically configured for RODC filtering must have the appropriate schema configuration.

---

# Schema Security

Changes to schema attribute behaviour are highly privileged.

Do not modify the Filtered Attribute Set during a routine penetration test.

Instead review whether sensitive custom attributes have been intentionally designed for RODC replication.

---

# Search Schema Attributes

From an appropriately authorised account, schema attributes can be reviewed through:

```text
Active Directory Schema
```

or LDAP/PowerShell.

Avoid modifying:

```text
searchFlags
```

or other schema properties during assessment.

---

# Administrator Role Separation

RODCs support:

```text
Administrator Role Separation
```

This allows a local branch administrator to administer the RODC server without automatically granting broad domain privileges.

Conceptually:

```text
Branch Administrator
       |
       v
Local RODC Administration
       |
       X
Domain Administration
```

---

# Why Role Separation Matters

A branch office may require someone to:

```text
Restart Server
Install Approved Hardware
Perform Local Maintenance
```

without making that person:

```text
Domain Admin
```

---

# ManagedBy

RODC administrative delegation can be represented through configuration associated with the RODC computer object.

Review the RODC's administrative delegation and management model.

---

# Enumerate ManagedBy

```powershell
Get-ADComputer -Identity 'RODC01' -Properties ManagedBy |
    Select-Object Name,ManagedBy
```

Do not assume `ManagedBy` alone represents every effective local administrative permission.

Validate local group membership and RODC-specific delegated administration.

---

# Local Administrators

From the RODC itself:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

Domain controllers handle local security differently from ordinary member servers, so interpret results in the context of domain-controller architecture and RODC role separation.

---

# Role Separation Risk

The intended model is:

```text
Branch Admin
     |
     v
RODC Only
```

A weakness exists if the delegated account also obtains:

```text
Domain Admin
Enterprise Admin
Writable DC Administration
Broad Server Administration
```

without business justification.

---

# Physical Security

RODCs are designed partly for locations where physical security may be weaker.

That does not mean:

```text
Physical Security Does Not Matter
```

Instead the architecture assumes:

```text
Reduced Trust
+
Reduced Credential Exposure
```

---

# Physical Access Assessment

Review:

```text
Server Room
Rack Security
Boot Security
Disk Encryption
Removable Media
Console Access
BIOS / UEFI Security
Hardware Disposal
Backup Media
```

where physical security is within scope.

---

# BitLocker

Disk encryption can reduce offline access to RODC data when a server or disk is stolen.

Assess whether:

```text
BitLocker
```

or equivalent controls protect branch-domain-controller storage.

---

# TPM

Where BitLocker uses TPM-based protection, review the overall threat model.

Physical access plus unrestricted boot paths can still create risk depending on configuration.

---

# RODC Compromise

A compromised RODC should not automatically be treated exactly like compromise of a writable domain controller.

The incident scope depends heavily on:

```text
Cached Credentials
RODC krbtgt Secret
Local Administrative Access
Replication Configuration
Other Secrets on Server
Network Access
```

---

# Compromise Scope Model

```text
RODC Compromise
      |
      +--> Cached User Credentials
      |
      +--> Cached Computer Credentials
      |
      +--> RODC krbtgt
      |
      +--> Local Secrets
      |
      +--> Directory Information
      |
      v
Assess Blast Radius
```

---

# Cached Privileged Credential Risk

A critical misconfiguration would be:

```text
Privileged Account
      |
      v
Allowed by PRP
      |
      v
Credential Cached on RODC
```

This defeats an important part of the RODC security model.

---

# Example High-Risk Condition

```text
Domain Admin
    |
    v
Branch Admin Group
    |
    v
Allowed RODC PRP
    |
    v
Cached on RODC
```

Nested membership can make this less obvious.

---

# Service Accounts

Service accounts can also create risk.

A service account used throughout the enterprise may authenticate at the branch and become cached if the PRP permits it.

Assess:

```text
Privilege
Usage
PRP
Caching
Password Management
```

---

# gMSA

Review whether gMSAs interact with the RODC environment.

See:

[gMSA](gmsa.md)

Credential behaviour for managed service accounts should be evaluated according to the actual service placement and AD configuration.

---

# Computer Accounts

Computer-account credentials can also be relevant to RODC caching.

Branch workstations and servers may legitimately need local authentication capability.

Review whether the cached population corresponds to the systems assigned to the branch.

---

# RODC and LAPS

If LAPS is deployed, consider whether the relevant password attributes are replicated to RODCs and who can read them.

See:

[LAPS](laps.md)

Modern Windows LAPS and legacy Microsoft LAPS use different attributes and security models.

Do not assume identical behaviour.

---

# RODC and AD CS

If an RODC exists at a branch that also contains certificate infrastructure, assess the systems independently.

See:

[Active Directory Certificate Services](ad-cs/index.md)

Do not assume that RODC status protects a Certificate Authority private key.

---

# RODC and Kerberos

RODC security is closely tied to Kerberos.

See:

[Kerberos](kerberos.md)

Important concepts include:

```text
RODC-Specific krbtgt
Credential Caching
Ticket Issuance
Writable DC Referrals
```

---

# RODC and NTLM

NTLM authentication may also be relevant depending on client and application behaviour.

See:

[NTLM](ntlm.md)

PRP and credential caching remain important when considering the compromise scope.

---

# RODC and Trusts

RODCs exist within the domain and forest trust architecture.

See:

[Trusts](trusts.md)

An RODC does not create a separate Active Directory security boundary merely because it is read-only.

---

# RODC and Credential Access

RODC assessment is highly relevant to:

[Credential Access](credential-access.md)

However, routine assessment should focus on:

```text
Which Credentials Could Be Cached?
Which Credentials Are Cached?
Are Privileged Accounts Protected?
```

rather than extracting credential material.

---

# RODC and NTDS

An RODC still contains:

```text
ntds.dit
```

See:

[NTDS](ntds.md)

The key difference is that the credential material present in an RODC database is constrained by its password-replication design.

---

# RODC and DCSync

Traditional replication-based credential extraction should not be treated as equivalent across writable DCs and RODCs.

RODCs have intentionally restricted replication behaviour.

See:

[NTDS](ntds.md)

Do not attempt replication abuse against production domain controllers without explicit authorisation.

---

# RODC and Lateral Movement

An RODC may exist in a remote network segment and have connectivity to writable domain controllers.

See:

[Lateral Movement](lateral-movement.md)

Do not assume that:

```text
RODC Can Reach Writable DC
```

means:

```text
RODC Automatically Controls Writable DC
```

The security impact depends on credentials, privileges and exposed protocols.

---

# RODC and Pivoting

Branch RODCs may sit between:

```text
Branch Network
```

and:

```text
Core Infrastructure
```

See:

[Pivoting](pivoting.md)

Review unnecessary network access without using the domain controller as an unauthorised pivot.

---

# RODC and SMB

Domain controllers expose SMB-related functionality required by Active Directory.

See:

[SMB](smb.md)

Do not report SMB exposure on an RODC solely because:

```text
TCP 445
```

is open.

Determine whether unnecessary administrative access exists.

---

# RODC and DNS

If the RODC provides DNS:

```text
Client
 |
 v
RODC DNS
 |
 v
Active Directory Resolution
```

Review DNS configuration as part of the overall branch architecture.

---

# RODC and Group Policy

An RODC provides access to Active Directory and SYSVOL information required by clients.

See:

[Group Policy](group-policy.md)

Group Policy remains controlled through writable Active Directory infrastructure.

---

# RODC and SYSVOL

RODCs maintain a read-only replicated copy of:

```text
SYSVOL
```

for client use.

Conceptually:

```text
Writable DC
    |
    v
SYSVOL Replication
    |
    v
RODC
```

The RODC should not become an authoritative source for malicious SYSVOL modifications.

---

# Branch Office Threat Model

A useful RODC threat model is:

```text
Attacker Gains Physical Access
            |
            v
          RODC
            |
            +--> Directory Data
            |
            +--> Cached Credentials
            |
            +--> RODC Kerberos Secret
            |
            +--> Local Configuration
            |
            v
       Limited Blast Radius
```

The effectiveness of this design depends heavily on PRP configuration.

---

# Security Assessment Priorities

Prioritise:

```text
Password Replication Policy
Cached Credentials
Privileged Accounts
RODC Administrators
Physical Security
Disk Encryption
Replication Topology
Patch Level
Network Exposure
```

---

# Safe RODC Assessment Workflow

A safe workflow is:

```text
Discover RODCs
      |
      v
Map Sites
      |
      v
Review PRP
      |
      v
Review Cached Population
      |
      v
Review Privileged Accounts
      |
      v
Review Administration
      |
      v
Review Replication
      |
      v
Review Physical / Network Security
      |
      v
Report
```

---

# Phase 1 - Discover RODCs

```powershell
Get-ADDomainController -Filter * |
    Where-Object {
        $_.IsReadOnly -eq $true
    } |
    Select-Object HostName,Site,IPv4Address
```

Record:

```text
Hostname
Site
IP Address
Operating System
Location
```

---

# Phase 2 - Identify RODC Computer Objects

```powershell
Get-ADComputer -Identity 'RODC01' -Properties *
```

Review RODC-specific configuration.

---

# Phase 3 - Review PRP

Review:

```text
Allowed Principals
Denied Principals
Nested Membership
Effective Policy
```

---

# Phase 4 - Review Cached Credentials

Determine:

```text
Which Accounts Have Been Revealed?
```

using supported PRP usage information and RODC attributes.

Do not extract password hashes merely to establish that credential caching occurred.

---

# Phase 5 - Review Privileged Accounts

Specifically search for:

```text
Domain Admins
Enterprise Admins
Schema Admins
Tier 0 Accounts
Privileged Service Accounts
```

within the effective cached or cacheable population.

---

# Phase 6 - Review Administration

Determine:

```text
Who Administers the RODC?
Who Has Local Maintenance Rights?
Who Has Domain Privilege?
Who Can Change PRP?
```

---

# Phase 7 - Review Replication

Use:

```cmd
repadmin /showrepl RODC01
```

Identify:

```text
Replication Partner
Replication Health
Directory Partitions
```

---

# Phase 8 - Review DNS

If DNS is installed, determine:

```text
Zones
Forwarders
Client Usage
Replication
Network Exposure
```

---

# Phase 9 - Review Physical Controls

Where in scope:

```text
Server Location
Rack Access
Console Access
Disk Encryption
Boot Security
Media Security
```

---

# Phase 10 - Review Network Controls

Assess connectivity between:

```text
Branch Clients
RODC
Writable DCs
Management Networks
Internet
Other Branches
```

---

# Phase 11 - Review Logging

Verify:

```text
Security Auditing
Directory Service Auditing
Kerberos Logging
Authentication Logging
EDR
Central Log Forwarding
```

---

# Phase 12 - Minimal Validation

Prefer:

```text
PRP Evidence
Group Membership
RODC Attributes
Replication Information
Configuration Evidence
Network Reachability
```

over:

```text
Credential Extraction
Ticket Forgery
Replication Abuse
Directory Modification
```

---

# Common Security Weaknesses

Potential RODC weaknesses include:

```text
Privileged Accounts Allowed by PRP
Privileged Credentials Cached on RODC
Excessively Broad Allowed PRP Group
Weak RODC Administrative Delegation
RODC Administrator Has Excessive Domain Privilege
Insufficient Physical Security
Unencrypted RODC Storage
Unsupported Operating System
Unnecessary Administrative Network Exposure
Poor Monitoring
Stale Cached Credentials
```

---

# Privileged Account Allowed by PRP

Example:

```text
Domain Admin
    |
    v
Allowed RODC Password Replication
```

Even if the credential has not yet been cached, the configuration can create future exposure.

---

# Privileged Credential Already Cached

Higher risk:

```text
Privileged Account
      |
      v
Credential Revealed
      |
      v
RODC
```

This means compromise of the RODC may expose credential material associated with the privileged identity.

---

# Broad Allowed Group

Example:

```text
Domain Users
    |
    v
Allowed PRP
```

Such broad configuration can undermine the purpose of selective credential caching.

The actual risk depends on effective deny relationships and cached state.

---

# Excessive Branch Administrator

Example:

```text
Branch Technician
      |
      +--> RODC Administrator
      |
      +--> Domain Admin
```

Role separation provides little security benefit if the delegated administrator already possesses domain-wide privilege.

---

# Weak Physical Security

Example:

```text
RODC
 |
 v
Unlocked Office
 |
 v
No Disk Encryption
```

This increases the likelihood of offline access if the server is stolen or physically accessed.

---

# Stale Credential Cache

Users transferred away from the branch may remain represented in the RODC's historical cached population.

Review whether incident-response and operational processes appropriately account for stale cached identities.

---

# Unsupported RODC

An RODC running an unsupported Windows Server release should be prioritised for remediation.

Domain controllers are critical infrastructure and should run supported, patched operating systems.

---

# Excessive Network Exposure

Example:

```text
User VLAN
   |
   +--> RDP
   +--> WinRM
   +--> Administrative RPC
   |
   v
RODC
```

Normal domain-controller services do not justify exposing every administrative interface to ordinary client networks.

---

# Detection

Monitor RODCs as domain controllers, while accounting for their specialised security model.

Important areas include:

```text
Authentication
Kerberos
PRP Changes
Administrative Access
Replication
Account Changes
Group Changes
RODC Computer Object Changes
```

---

# Authentication Events

Useful Windows Security events include:

```text
4624
4625
4648
4672
```

depending on audit configuration.

---

# Kerberos Events

Useful events include:

```text
4768
4769
4771
```

for Kerberos authentication activity.

Correlate activity with the domain controller processing the request.

---

# NTLM

Event:

```text
4776
```

can provide visibility into NTLM credential validation.

---

# Directory Changes

Where Directory Service Changes auditing is enabled:

```text
5136
```

can provide evidence of Active Directory object modification.

Monitor changes to RODC-related attributes and PRP configuration.

---

# Group Changes

Security group membership changes may affect PRP.

Relevant events can include:

```text
4728
4729
4732
4733
4756
4757
```

depending on group scope and operation.

---

# Privileged Group Changes

Changes involving:

```text
Denied RODC Password Replication Group
Allowed RODC Password Replication Group
```

should be monitored where these groups form part of the organisation's RODC control model.

---

# Administrative Logons

Unexpected privileged logons to an RODC should be investigated.

Particularly important:

```text
Domain Admin
Enterprise Admin
Tier 0 Administrator
```

because routine branch administration should generally not require such identities.

---

# Replication Monitoring

Monitor:

```text
Replication Failures
Unexpected Replication Partners
Topology Changes
Long-Term Replication Failure
```

RODCs depend on healthy connectivity to writable domain controllers.

---

# Physical Compromise Indicators

Potential signals include:

```text
Unexpected Reboots
Boot Configuration Changes
BitLocker Recovery Events
EDR Tampering
Unexpected Local Administrative Activity
Hardware Changes
```

where telemetry is available.

---

# RODC Theft or Loss

If an RODC is stolen or believed compromised, incident response should identify:

```text
RODC Identity
Cached Accounts
RODC krbtgt Account
Certificates
Local Secrets
Service Accounts
Network Credentials
```

---

# Credential Reset Planning

The RODC's cached-account information helps determine which credentials may require reset after compromise.

Conceptually:

```text
Compromised RODC
      |
      v
Identify Cached Accounts
      |
      v
Prioritise Credential Reset
```

This is one of the major operational benefits of selective credential caching.

---

# RODC krbtgt Reset

A compromised RODC may require resetting its RODC-specific krbtgt account as part of incident response.

This should be performed using supported Microsoft procedures.

Do not manually manipulate the account during routine testing.

---

# Do Not Reset Domain krbtgt Without Need

Compromise of an RODC does not automatically mean:

```text
Domain krbtgt
```

has been compromised.

Incident response should determine actual scope before performing disruptive domain-wide recovery actions.

---

# Hardening RODCs

A secure RODC deployment should combine:

```text
Restrictive PRP
Role Separation
Disk Encryption
Physical Security
Network Segmentation
Patch Management
Monitoring
Minimal Credential Caching
```

---

# Restrict PRP

Allow only accounts that genuinely require local branch authentication.

A preferred conceptual model is:

```text
Branch Users
      |
      v
Allowed

Privileged Accounts
      |
      v
Denied
```

---

# Protect Privileged Accounts

Ensure highly privileged identities cannot have passwords replicated to branch RODCs.

Review both:

```text
Direct Membership
Nested Membership
```

---

# Minimise Cached Credentials

The goal is not:

```text
Cache Everything Just in Case
```

Instead:

```text
Cache Only What the Site Requires
```

---

# Separate Branch Administration

Use RODC administrator role separation where branch personnel require server maintenance but do not require domain administration.

---

# Avoid Privileged Logons

Avoid using Tier 0 administrative accounts interactively on RODCs unless operationally necessary.

This reduces the chance of sensitive authentication material becoming exposed through other mechanisms.

---

# Encrypt Storage

Use appropriate disk encryption such as:

```text
BitLocker
```

for RODCs in physically exposed environments.

---

# Secure Boot Configuration

Restrict:

```text
External Boot
Firmware Changes
Recovery Environment Access
Removable Media
```

according to the physical threat model.

---

# Patch RODCs

Maintain current:

```text
Windows Updates
Domain Controller Security Updates
EDR
Security Configuration
```

---

# Segment Branch Networks

Permit only required connectivity.

Conceptually:

```text
Branch Clients
      |
      v
Required AD Services
      |
      v
RODC
      |
      v
Required Replication
      |
      v
Writable DC
```

---

# Restrict Administrative Interfaces

Limit:

```text
RDP
WinRM
SMB Administration
Remote Registry
Administrative RPC
```

to authorised management systems where possible.

---

# Monitor PRP Changes

Changes to:

```text
Allowed Principals
Denied Principals
```

can materially change the impact of a future RODC compromise.

Treat these as security-sensitive changes.

---

# Monitor Cached Population

Periodically review which credentials have been cached.

Unexpected privileged or cross-site accounts should be investigated.

---

# Protect Backups

RODC backups can contain sensitive information corresponding to the state of the RODC.

Protect:

```text
System State Backups
Disk Images
Virtual Machine Backups
Snapshots
```

---

# Virtualised RODCs

If an RODC runs as a virtual machine, the physical-security model also includes:

```text
Hypervisor Administrators
Storage Administrators
Backup Administrators
Snapshot Access
```

A locked branch server does not help if unrestricted VM copies exist elsewhere.

---

# Reporting RODC Findings

Do not report:

```text
RODC Is Installed
```

as a weakness.

Report the actual configuration issue.

---

# Potential Findings

Examples include:

```text
Privileged Accounts Are Permitted by the RODC Password Replication Policy
```

```text
Privileged Credentials Have Been Cached on a Branch RODC
```

```text
RODC Password Replication Policy Is Excessively Broad
```

```text
RODC Administrative Role Separation Is Ineffective
```

```text
Branch RODC Storage Is Not Protected Against Offline Access
```

```text
RODC Administrative Services Are Accessible from Untrusted Networks
```

```text
RODC Is Running an Unsupported Windows Server Version
```

---

# Example Finding - Privileged PRP

```text
Finding:
Privileged Accounts Are Permitted by the RODC Password Replication
Policy

Description:
The Password Replication Policy configured for the branch RODC allowed
a group containing privileged Active Directory accounts to have
credential material replicated to the RODC.

The assessment reviewed the effective policy and group membership
without triggering password replication.

Impact:
If an affected privileged account authenticates in circumstances that
cause its credential material to be cached, compromise of the RODC
could expose credentials with privileges extending beyond the branch
site.

This reduces the security isolation provided by the RODC architecture.

Recommendation:
Exclude privileged identities from RODC password replication.

Review direct and nested membership of the relevant PRP groups and
ensure Tier 0 administrators and highly privileged service accounts are
explicitly protected from RODC credential caching.
```

---

# Example Finding - Cached Privileged Credential

```text
Finding:
Privileged Credential Has Been Cached on a Branch RODC

Description:
Read-only Active Directory configuration evidence showed that
credential material for a privileged account had previously been
revealed to the branch RODC.

No password hash or other credential material was extracted during the
assessment.

Impact:
Compromise or theft of the RODC could potentially expose credential
material associated with the privileged identity.

The resulting impact may extend beyond the branch environment.

Recommendation:
Investigate why the privileged identity authenticated through the RODC
and why the effective Password Replication Policy permitted caching.

Remove the account from the cacheable population and follow the
organisation's credential-reset process for affected identities.

Review the remaining cached-account population for equivalent
exposure.
```

---

# Example Finding - Broad PRP

```text
Finding:
RODC Password Replication Policy Is Excessively Broad

Description:
The RODC Password Replication Policy permitted credential caching for
a broad population substantially larger than the users and computers
assigned to the branch location.

Impact:
Compromise of the RODC could expose credential material for more
accounts than operationally necessary.

This increases the potential blast radius of physical or administrative
compromise of the branch domain controller.

Recommendation:
Restrict password replication to users, computers and service
identities that genuinely require local authentication at the site.

Review nested group membership and periodically compare the permitted
population with current branch ownership.
```

---

# Example Finding - Role Separation

```text
Finding:
RODC Administrative Role Separation Is Ineffective

Description:
The account delegated to perform local administration of the branch
RODC also possessed broad administrative privileges elsewhere in the
Active Directory environment.

Impact:
The intended security benefit of RODC administrator role separation is
reduced because compromise of the branch administrator can affect
systems outside the RODC.

Recommendation:
Use a dedicated branch administration identity with privileges limited
to the RODC and required branch-management functions.

Remove unnecessary domain-wide and server-wide administrative rights.
```

---

# Example Finding - Physical Protection

```text
Finding:
Branch RODC Storage Is Not Protected Against Offline Access

Description:
The RODC was deployed in a location with limited physical security and
its operating-system volume was not protected using full-disk
encryption.

Impact:
An attacker obtaining physical possession of the server or its storage
could attempt offline analysis of Active Directory data and credential
material cached on the RODC.

Recommendation:
Protect RODC storage using an appropriate full-disk encryption
solution such as BitLocker.

Combine disk encryption with secure boot configuration, restricted
physical access and a restrictive Password Replication Policy.
```

---

# Example Finding - Network Exposure

```text
Finding:
RODC Administrative Services Are Accessible from Untrusted Networks

Description:
Administrative interfaces on the branch RODC were reachable directly
from ordinary user network segments.

The exposed services exceeded those required for normal Active
Directory client authentication.

Impact:
A compromised branch workstation could directly interact with
additional administrative services on identity infrastructure.

Recommendation:
Restrict administrative access to dedicated management systems and
approved administrator networks.

Permit normal client access only to the Active Directory services
required by the branch architecture.
```

---

# RODC Assessment Checklist

## Discovery

- [ ] Enumerate all domain controllers
- [ ] Identify RODCs
- [ ] Identify RODC hostnames
- [ ] Identify IP addresses
- [ ] Identify AD sites
- [ ] Identify operating systems
- [ ] Identify physical locations
- [ ] Identify writable replication partners

## Password Replication Policy

- [ ] Enumerate allowed PRP
- [ ] Enumerate denied PRP
- [ ] Review `msDS-RevealOnDemandGroup`
- [ ] Review `msDS-NeverRevealGroup`
- [ ] Review nested membership
- [ ] Determine effective PRP
- [ ] Identify broad groups
- [ ] Identify privileged accounts
- [ ] Identify service accounts
- [ ] Identify cross-site accounts

## Cached Credentials

- [ ] Review `msDS-RevealedList`
- [ ] Review supported PRP usage information
- [ ] Identify accounts actually revealed
- [ ] Identify privileged cached accounts
- [ ] Identify stale cached accounts
- [ ] Identify unnecessary cached computers
- [ ] Avoid extracting password material

## Kerberos

- [ ] Identify RODC-specific krbtgt account
- [ ] Distinguish it from domain `krbtgt`
- [ ] Review account state
- [ ] Review RODC Kerberos architecture
- [ ] Avoid ticket forgery during routine assessment

## Administration

- [ ] Identify delegated RODC administrator
- [ ] Review local administrative access
- [ ] Review domain privileges
- [ ] Review nested group membership
- [ ] Review management accounts
- [ ] Validate role separation
- [ ] Identify excessive privileges

## Replication

- [ ] Identify writable replication partner
- [ ] Review `repadmin /showrepl`
- [ ] Review replication health
- [ ] Review AD site topology
- [ ] Review network path
- [ ] Avoid forcing replication unnecessarily

## DNS

- [ ] Determine whether DNS is installed
- [ ] Review AD-integrated zones
- [ ] Review client DNS usage
- [ ] Review forwarders
- [ ] Review DNS network exposure
- [ ] Review dynamic update architecture

## SYSVOL

- [ ] Review SYSVOL availability
- [ ] Confirm read-only replication model
- [ ] Review branch GPO requirements
- [ ] Review replication health

## Filtered Attribute Set

- [ ] Identify sensitive custom attributes
- [ ] Determine whether RODC replication is appropriate
- [ ] Review schema design
- [ ] Avoid schema changes during assessment

## Physical Security

- [ ] Review server-room access
- [ ] Review rack security
- [ ] Review console access
- [ ] Review removable media
- [ ] Review firmware security
- [ ] Review external boot
- [ ] Review disk encryption
- [ ] Review backup storage
- [ ] Review hardware disposal

## Virtualisation

- [ ] Identify hypervisor
- [ ] Review hypervisor administrators
- [ ] Review storage administrators
- [ ] Review snapshots
- [ ] Review VM backups
- [ ] Review console access

## Network

- [ ] Review branch client access
- [ ] Review writable DC connectivity
- [ ] Review management connectivity
- [ ] Review RDP
- [ ] Review WinRM
- [ ] Review SMB
- [ ] Review RPC
- [ ] Review Internet access
- [ ] Review segmentation

## Monitoring

- [ ] Review authentication logging
- [ ] Review Kerberos logging
- [ ] Review NTLM logging
- [ ] Review Directory Service auditing
- [ ] Review group changes
- [ ] Review PRP changes
- [ ] Review privileged logons
- [ ] Review replication failures
- [ ] Review EDR coverage
- [ ] Review central log forwarding

## Incident Response

- [ ] Maintain RODC compromise procedure
- [ ] Identify cached accounts after compromise
- [ ] Identify RODC-specific krbtgt
- [ ] Identify certificates
- [ ] Identify local secrets
- [ ] Determine credential reset scope
- [ ] Determine whether domain `krbtgt` was actually affected
- [ ] Rebuild compromised RODC where appropriate
- [ ] Review branch administrator credentials
- [ ] Review physical compromise

## Hardening

- [ ] Restrict PRP
- [ ] Deny privileged identities
- [ ] Minimise credential caching
- [ ] Review cached population regularly
- [ ] Use administrator role separation
- [ ] Avoid Tier 0 logons
- [ ] Encrypt storage
- [ ] Secure boot configuration
- [ ] Protect backups
- [ ] Patch RODCs
- [ ] Deploy EDR
- [ ] Restrict administrative interfaces
- [ ] Segment branch networks
- [ ] Monitor PRP changes
- [ ] Monitor privileged authentication

## Reporting

- [ ] Do not report RODC presence alone
- [ ] Identify actual PRP weakness
- [ ] Distinguish allowed from cached
- [ ] Identify affected identities
- [ ] Identify privilege
- [ ] Identify branch location
- [ ] Identify compromise prerequisites
- [ ] Avoid extracting credentials unnecessarily
- [ ] Explain blast radius
- [ ] Provide architecture-specific remediation

---

# RODC Testing Model

The basic architecture is:

```text
Writable DC
    |
    v
   RODC
    |
    v
Branch Clients
```

The replication model is:

```text
Writable DC
    |
    | Replication
    v
   RODC
```

The credential model is:

```text
Account
   |
   v
PRP
   |
   +--> Allowed
   |      |
   |      v
   |   May Cache
   |
   +--> Denied
          |
          v
      Must Not Cache
```

The authentication model is:

```text
User
 |
 v
RODC
 |
 +--> Cached
 |      |
 |      v
 |  Authenticate
 |
 +--> Not Cached
        |
        v
   Writable DC
```

The compromise model is:

```text
RODC Compromise
      |
      +--> Directory Information
      |
      +--> Cached Credentials
      |
      +--> RODC krbtgt
      |
      +--> Local Secrets
      |
      v
Limited Compromise Scope
```

The administrator model is:

```text
Branch Administrator
        |
        v
      RODC
        |
        X
Domain-Wide Administration
```

The intended security objective is:

```text
Local Administration
without
Domain Administration
```

The physical-security model is:

```text
Lower-Trust Location
       |
       v
      RODC
       |
       +--> Restricted Credentials
       |
       +--> Read-Only Directory
       |
       +--> Role Separation
       |
       v
Reduced Exposure
```

The Kerberos model is:

```text
Domain
 |
 +--> krbtgt
 |
 +--> krbtgt_RODC
          |
          v
         RODC
```

The critical distinction is:

```text
RODC-Specific krbtgt
       !=
Domain krbtgt
```

Another important distinction is:

```text
Allowed to Cache
       !=
Actually Cached
```

For penetration testers:

```text
Do Not Ask:
"Can I dump the RODC?"

Ask:
"Which credentials would be exposed
if this RODC were compromised, and
does that exposure exceed the intended
branch security boundary?"
```

For defenders:

```text
Do Not Ask:
"Is the domain controller read-only?"

Ask:
"Which credentials can it cache,
which credentials has it cached,
who administers it, and what would
be exposed if the server were stolen?"
```

The complete assessment model is:

```text
Branch Location
      |
      v
Physical Security
      |
      v
RODC
      |
      +--> PRP
      |
      +--> Cached Credentials
      |
      +--> RODC krbtgt
      |
      +--> Directory Data
      |
      +--> DNS
      |
      +--> SYSVOL
      |
      v
Potential Blast Radius
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Enumeration:

[Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Credential Access:

[Credential Access](credential-access.md)

NTDS:

[NTDS](ntds.md)

Groups:

[Groups](groups.md)

Group Policy:

[Group Policy](group-policy.md)

gMSA:

[gMSA](gmsa.md)

LAPS:

[LAPS](laps.md)

Trusts:

[Trusts](trusts.md)

Active Directory Integrated DNS:

[Active Directory Integrated DNS](adidns.md)

SMB:

[SMB](smb.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

Pivoting:

[Pivoting](pivoting.md)

AD CS:

[Active Directory Certificate Services](ad-cs/index.md)

AD FS:

[Active Directory Federation Services - AD FS](adfs.md)

---

# References

## Microsoft - RODC Planning and Deployment

[Microsoft Learn - Read-Only Domain Controller Planning and Deployment Guide](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/planning-domain-controller-placement){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Password Replication Policy

[Microsoft Learn - Password Replication Policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password){ target="_blank" rel="noopener noreferrer" }

Use Microsoft's current AD DS documentation for the Windows Server version deployed in the environment when validating PRP behaviour.

---

## Microsoft - Get-ADDomainController

[Microsoft Learn - Get-ADDomainController](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomaincontroller){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADDomainControllerPasswordReplicationPolicy

[Microsoft Learn - Get-ADDomainControllerPasswordReplicationPolicy](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomaincontrollerpasswordreplicationpolicy){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADDomainControllerPasswordReplicationPolicyUsage

[Microsoft Learn - Get-ADDomainControllerPasswordReplicationPolicyUsage](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addomaincontrollerpasswordreplicationpolicyusage){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Add-ADDomainControllerPasswordReplicationPolicy

[Microsoft Learn - Add-ADDomainControllerPasswordReplicationPolicy](https://learn.microsoft.com/en-us/powershell/module/activedirectory/add-addomaincontrollerpasswordreplicationpolicy){ target="_blank" rel="noopener noreferrer" }

This command changes PRP configuration and should not be used during a read-only assessment.

---

## Microsoft - Repadmin

[Microsoft Learn - Repadmin](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc770963(v=ws.11)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Domain Services

[Microsoft Learn - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft Learn - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - OS Credential Dumping: NTDS

[MITRE ATT&CK - OS Credential Dumping: NTDS](https://attack.mitre.org/techniques/T1003/003/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

An RODC should be understood as:

```text
Domain Controller
+
Reduced Write Capability
+
Selective Credential Storage
+
Branch Security Controls
```

not simply:

```text
A Domain Controller That Cannot Write
```

The most important security mechanism is:

```text
Password Replication Policy
```

because it determines the potential credential exposure associated with the RODC.

The fundamental distinction is:

```text
Allowed by PRP
      |
      v
Could Be Cached
```

versus:

```text
Revealed to RODC
      |
      v
Was Cached
```

Both should be assessed.

The credential-security objective is:

```text
Branch Users
     |
     v
May Be Cached

Privileged Users
     |
     X
Must Not Be Cached
```

The RODC-specific Kerberos design provides another containment mechanism:

```text
RODC
 |
 v
RODC-Specific krbtgt
```

rather than exposing the normal domain:

```text
krbtgt
```

secret.

Administrator role separation provides another layer:

```text
Branch Administrator
       |
       v
Local RODC Management
       |
       X
Domain Administration
```

The security benefit of the architecture depends on all of these controls working together:

```text
Restrictive PRP
      +
Minimal Credential Caching
      +
RODC-Specific Kerberos Trust
      +
Administrator Role Separation
      +
Physical Security
      +
Disk Encryption
      +
Network Segmentation
      =
Reduced Branch Compromise Impact
```

A well-designed RODC should therefore answer:

```text
Which Accounts Can Be Cached?

Which Accounts Have Been Cached?

Are Privileged Accounts Explicitly Protected?

Who Can Administer the RODC?

Can That Administrator Control Anything Else?

What Happens If the Server Is Physically Stolen?

Which Writable DC Does It Depend On?

How Quickly Can Cached Credentials Be Identified
and Reset After Compromise?
```

The value of an RODC is not that compromise becomes harmless.

Its purpose is to make the compromise:

```text
Smaller
More Contained
More Recoverable
```

than compromise of a fully writable domain controller.
