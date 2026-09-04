# Active Directory Persistence

Active Directory persistence refers to techniques, configurations and access paths that allow an attacker or unauthorised administrator to retain privileged access after the original compromise has been discovered or remediated.

Persistence can exist at multiple layers:

```text
Account
   |
   v
Group
   |
   v
ACL
   |
   v
Kerberos
   |
   v
Certificate
   |
   v
GPO
   |
   v
Domain Controller
   |
   v
Forest / Trust
```

Active Directory persistence is particularly important because a single hidden change can provide a long-term path back into the environment.

A simplified model is:

```text
Initial Compromise
       |
       v
Privileged Access
       |
       v
Persistence Established
       |
       v
Original Access Removed
       |
       v
Persistent Path Remains
       |
       v
Re-entry
```

Persistence is not limited to creating a new administrator account.

It can involve:

```text
Group Membership
ACL Changes
Directory Replication Rights
Kerberos Keys
Certificates
Key Credentials
Delegation
Group Policy
Service Accounts
Scheduled Tasks
Trust Material
Identity Infrastructure
```

!!! warning "Authorised testing only"
    Persistence testing can create long-lived access to an Active Directory environment and may affect domain-wide security. During routine assessments, prefer read-only discovery and configuration analysis. Do not create persistent administrator accounts, modify privileged ACLs, forge long-lived authentication material, change trust relationships, alter certificate infrastructure or install production persistence unless explicitly authorised. If temporary changes are permitted, document the original state and remove every test artefact during cleanup.

---

# Why Persistence Matters

Privilege escalation answers:

```text
How Can I Gain More Privilege?
```

Persistence answers:

```text
How Could That Privilege Survive?
```

For example:

```text
Compromised Admin
       |
       v
Add Hidden Permission
       |
       v
Admin Password Reset
       |
       v
Attacker Still Has Control
```

The original credential can be rotated while the persistence mechanism remains.

---

# Persistence vs Privilege Escalation

Privilege escalation:

```text
User
 |
 v
Higher Privilege
```

Persistence:

```text
Higher Privilege
 |
 v
Long-Term Access Path
 |
 v
Future Re-entry
```

A technique can serve both purposes.

For example:

```text
WriteDacl
```

might first be used to gain control and later be used to preserve that control.

---

# Persistence vs Credential Access

Credential access obtains authentication material:

```text
Credential
   |
   v
Authentication
```

Persistence attempts to maintain a future authentication or control path:

```text
Persistent Mechanism
       |
       v
Future Authentication / Control
```

A stolen password alone is usually fragile persistence because it can be rotated.

A hidden ACL or certificate-based path may survive an ordinary password reset.

---

# Persistence Layers

A useful Active Directory persistence model is:

```text
Identity Persistence
       |
       +--> Accounts
       +--> Groups
       +--> Service Accounts
       |
       v
Directory Persistence
       |
       +--> ACLs
       +--> Delegation
       +--> Replication Rights
       +--> Key Credentials
       |
       v
Authentication Persistence
       |
       +--> Kerberos
       +--> Certificates
       +--> Trust Secrets
       |
       v
Configuration Persistence
       |
       +--> GPO
       +--> Scripts
       +--> Scheduled Tasks
       |
       v
Infrastructure Persistence
       |
       +--> Domain Controllers
       +--> AD CS
       +--> AD FS
       +--> Management Platforms
```

---

# Persistence Assessment Methodology

A structured assessment can follow:

```text
Identify Privileged Identities
          |
          v
Review Privileged Groups
          |
          v
Review Sensitive ACLs
          |
          v
Review Kerberos Trust Material
          |
          v
Review Certificates
          |
          v
Review Delegation
          |
          v
Review Group Policy
          |
          v
Review Domain Controllers
          |
          v
Review Trusts
          |
          v
Review Management Infrastructure
          |
          v
Correlate With Change History
```

---

# Establish the Baseline

Persistence is difficult to detect without knowing what should exist.

Create an inventory of:

```text
Privileged Users
Privileged Groups
Service Accounts
Domain Controllers
Certificate Authorities
Federation Servers
Management Servers
Trusts
Delegated Permissions
GPOs
Authentication Policies
```

The objective is to identify:

```text
Unexpected Privilege
```

rather than simply:

```text
Unfamiliar Objects
```

---

# Identity Persistence

The simplest persistence mechanism is an account.

Examples include:

```text
New User
Existing User
Dormant User
Service Account
Computer Account
Cloud-Synchronised Identity
```

---

# Enumerate Users

```powershell
Get-ADUser -Filter * -Properties Enabled,Created,Modified,PasswordLastSet |
    Select-Object SamAccountName,Enabled,Created,Modified,PasswordLastSet
```

Useful questions include:

```text
Was the account expected?
When was it created?
Is it enabled?
Who owns it?
What groups is it in?
Does it have an SPN?
Does it have delegated permissions?
```

---

# Recently Created Accounts

Where the `Created` attribute is available:

```powershell
$Since = (Get-Date).AddDays(-30)

Get-ADUser -Filter * -Properties Created |
    Where-Object {
        $_.Created -ge $Since
    } |
    Select-Object SamAccountName,Created
```

A recently created account is not automatically malicious.

Correlate it with:

```text
Change Ticket
HR Process
Service Deployment
Administrator
Source Host
```

---

# Disabled and Dormant Accounts

Dormant identities can become persistence opportunities if they are unexpectedly re-enabled.

Review:

```powershell
Search-ADAccount -AccountInactive -UsersOnly -TimeSpan 90.00:00:00
```

Interpret inactivity according to the organisation's account lifecycle.

---

# Privileged Group Persistence

Adding an identity to a privileged group is one of the most obvious persistence mechanisms.

Important groups include:

```text
Domain Admins
Enterprise Admins
Schema Admins
Administrators
```

and environment-specific administrative groups.

---

# Domain Admins

```powershell
Get-ADGroupMember -Identity 'Domain Admins' -Recursive
```

Review:

```text
Expected Members
Nested Groups
Service Accounts
Dormant Accounts
Temporary Accounts
```

---

# Enterprise Admins

From the forest root domain:

```powershell
Get-ADGroupMember -Identity 'Enterprise Admins' -Recursive
```

Standing membership should normally be highly restricted.

---

# Schema Admins

```powershell
Get-ADGroupMember -Identity 'Schema Admins' -Recursive
```

Unexpected standing membership warrants investigation.

---

# Nested Group Persistence

Persistence can be less obvious when privilege is obtained indirectly.

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

Review recursive membership rather than only direct members.

---

# Group Ownership

An identity may not currently belong to a privileged group but may control it.

Conceptually:

```text
User
 |
 | Owner / ACL
 v
Privileged Group
```

This can be more subtle than direct membership.

See:

[Groups](groups.md)

and:

[ACL and ACE](acl-ace.md)

---

# ACL Persistence

Active Directory ACLs are a major persistence surface.

A principal can retain control without being visibly present in an administrative group.

Example:

```text
User
 |
 | GenericAll
 v
Privileged User
```

or:

```text
User
 |
 | WriteDacl
 v
Privileged Group
```

---

# Why ACL Persistence Is Dangerous

Administrators may investigate:

```text
Domain Admins
```

and find nothing unusual.

But an attacker-controlled identity may still possess:

```text
GenericAll
WriteDacl
WriteOwner
GenericWrite
Reset Password
WriteMembers
```

over privileged objects.

---

# Sensitive ACL Targets

Prioritise:

```text
Domain Root
AdminSDHolder
Privileged Groups
Privileged Users
Domain Controllers OU
Tier 0 OUs
GPOs
Certificate Templates
Certificate Authorities
Service Accounts
Management Servers
```

---

# Read-Only ACL Review

Native PowerShell can inspect an object's security descriptor.

For example:

```powershell
$DomainDN = (Get-ADDomain).DistinguishedName
$Path = "AD:\$DomainDN"

(Get-Acl -Path $Path).Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

This does not modify the ACL.

---

# PowerView

With an authorised PowerView version loaded, ACL enumeration can include:

```powershell
Get-DomainObjectAcl -ResolveGUIDs
```

Filter and validate results according to the PowerView version being used.

See:

[ACL and ACE](acl-ace.md)

---

# WriteDacl Persistence

A principal with:

```text
WriteDacl
```

can potentially change permissions on the target object.

Conceptually:

```text
Controlled Identity
       |
       v
WriteDacl
       |
       v
Sensitive Object
       |
       v
Future Control
```

This is a high-value persistence relationship.

---

# WriteOwner Persistence

```text
Controlled Identity
       |
       v
WriteOwner
       |
       v
Sensitive Object
```

Ownership can provide a route toward changing the object's permissions.

---

# AdminSDHolder

AdminSDHolder is particularly important when reviewing privileged-object persistence.

Conceptually:

```text
AdminSDHolder
      |
      v
Protected Security Descriptor
      |
      v
Protected Accounts / Groups
```

Unexpected permissions on AdminSDHolder can affect protected privileged objects.

---

# Enumerate AdminSDHolder ACL

```powershell
$DomainDN = (Get-ADDomain).DistinguishedName
$AdminSDHolder = "AD:\CN=AdminSDHolder,CN=System,$DomainDN"

(Get-Acl -Path $AdminSDHolder).Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,IsInherited
```

Do not modify this ACL during ordinary assessment.

---

# adminCount

Protected or historically protected accounts may have:

```text
adminCount = 1
```

Enumerate:

```powershell
Get-ADUser -LDAPFilter '(adminCount=1)' -Properties adminCount |
    Select-Object SamAccountName,Enabled,adminCount
```

Do not interpret `adminCount=1` as definitive proof of current privileged membership.

---

# Domain ACL Persistence

Permissions on the domain root are highly sensitive.

Review:

```text
GenericAll
WriteDacl
WriteOwner
Replication Rights
```

and other non-standard delegation.

---

# Replication Rights Persistence

Directory replication permissions can provide access to sensitive Active Directory data.

Important rights include:

```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

and, where applicable:

```text
DS-Replication-Get-Changes-In-Filtered-Set
```

---

# DCSync Persistence

Conceptually:

```text
Controlled Account
       |
       v
Replication Rights
       |
       v
Domain
       |
       v
Directory Credential Data
```

An attacker does not need permanent Domain Admin membership if an identity retains sufficient replication permissions.

See:

[NTDS](ntds.md)

---

# Safe DCSync Assessment

During normal assessment:

```text
Enumerate Replication Rights
        |
        v
Identify Principal
        |
        v
Determine Whether Expected
        |
        v
Report
```

Do not request production credential material merely to prove that the permissions exist unless explicitly authorised.

---

# Kerberos Persistence

Kerberos is a major persistence area because long-term authentication trust is based on cryptographic secrets.

Important concepts include:

```text
krbtgt
Service Account Keys
Computer Account Keys
Trust Keys
RODC krbtgt Keys
```

---

# krbtgt

The domain:

```text
krbtgt
```

account is central to Kerberos ticket-granting operations.

Compromise of its long-term secret is a domain-level incident.

---

# Golden Ticket Concept

A Golden Ticket refers to forged Kerberos Ticket Granting Ticket material created using the domain's `krbtgt` secret.

Conceptually:

```text
krbtgt Secret
      |
      v
Forge TGT
      |
      v
Kerberos Authentication
```

This is a persistence concept because changing an ordinary administrator password does not invalidate knowledge of the `krbtgt` secret.

---

# Do Not Forge Tickets During Routine Assessment

If evidence establishes that the domain `krbtgt` secret was exposed, forging a production ticket is usually unnecessary to establish impact.

Prefer:

```text
Evidence of Secret Exposure
+
Domain Context
+
Kerberos Architecture
```

---

# Golden Ticket Recovery

If the domain `krbtgt` secret is believed compromised, incident response typically requires a carefully planned `krbtgt` password reset process.

Because Kerberos maintains current and previous key material for ticket validation, recovery guidance commonly involves resetting the password twice with appropriate replication and timing considerations.

Follow current Microsoft forest-recovery guidance rather than improvising this procedure.

---

# RODC krbtgt

RODCs have RODC-specific Kerberos trust material.

See:

[RODC](rodc.md)

The distinction is:

```text
Domain krbtgt
     !=
RODC-Specific krbtgt
```

An RODC-specific compromise should not automatically be described as domain-wide Golden Ticket capability.

---

# Silver Ticket Concept

A Silver Ticket refers to forged Kerberos service-ticket material associated with a service account or computer account secret.

Conceptually:

```text
Service Account Secret
        |
        v
Service Ticket
        |
        v
Specific Service
```

Its scope differs from a Golden Ticket.

---

# Service Account Persistence

Long-lived service-account credentials can provide durable access.

Review:

```text
SPNs
Password Age
Privilege
Group Membership
Delegation
Logon Rights
Managed Systems
```

---

# Service Account Password Age

```powershell
Get-ADUser -Filter {ServicePrincipalName -like "*"} -Properties ServicePrincipalName,PasswordLastSet |
    Select-Object SamAccountName,PasswordLastSet,ServicePrincipalName
```

A long password age alone is not proof of compromise.

For randomly generated managed secrets, age should be interpreted differently from human-managed passwords.

---

# gMSA

Group Managed Service Accounts automatically manage their password lifecycle.

See:

[gMSA](gmsa.md)

Important questions include:

```text
Who Can Retrieve the Managed Password?
Which Systems Use the Account?
What Privileges Does It Have?
```

---

# Certificate-Based Persistence

Certificates can provide authentication independently of an account's current password.

This makes certificate-based access particularly important during persistence reviews.

```text
Certificate
    |
    v
Authentication
    |
    v
Account
```

Changing:

```text
User Password
```

does not necessarily invalidate:

```text
Existing Authentication Certificate
```

---

# AD CS

Active Directory Certificate Services should therefore be treated as identity infrastructure.

See:

[Active Directory Certificate Services](ad-cs/index.md)

Review:

```text
Issued Certificates
Certificate Templates
Enrollment Rights
CA Permissions
Private Keys
Certificate Validity
Authentication Mapping
```

---

# Certificate Lifetime

A long-lived authentication certificate can outlive:

```text
Password Changes
Helpdesk Resets
Credential Rotation
```

depending on revocation and account state.

Therefore certificate inventory is important during incident response.

---

# Golden Certificate Concept

If a Certification Authority's private signing key is compromised, an attacker may be able to create certificates that appear to have been issued by that trusted CA.

This is commonly described as:

```text
Golden Certificate
```

See:

[Golden Certificate](ad-cs/golden-certificate.md)

---

# Golden Certificate Model

```text
CA Private Key
     |
     v
Certificate Signature
     |
     v
Trusted Certificate
     |
     v
Authentication
```

This is significantly different from compromising one issued certificate.

---

# CA Private Key Protection

Protect CA private keys using appropriate controls such as:

```text
Hardware Security Modules
Strong Private-Key Protection
Restricted CA Administration
Offline Root CA Design
Secure Backups
Auditing
```

according to the PKI architecture.

---

# Certificate Revocation

Incident response may require:

```text
Certificate Revocation
CRL Publication
CA Key Rollover
Template Remediation
Account Remediation
```

depending on the type of compromise.

If the CA signing key itself is compromised, revoking one certificate is not sufficient to address the trust problem.

---

# Shadow Credentials

Shadow Credentials abuse relates to:

```text
msDS-KeyCredentialLink
```

and certificate/key-based authentication.

See:

[Shadow Credentials](shadow-credentials.md)

---

# Shadow Credential Persistence Model

```text
Controlled Account
       |
       v
Write Key Credential
       |
       v
Target Identity
       |
       v
Alternative Authentication Material
```

This can survive an ordinary password reset if the malicious key credential remains configured.

---

# Safe Shadow Credential Assessment

Prefer identifying:

```text
Who Can Write msDS-KeyCredentialLink?
```

and:

```text
Are Unexpected Key Credentials Present?
```

rather than adding a key credential to a production privileged account.

---

# Enumerate Key Credential Information

Using appropriate Active Directory tooling, review accounts with unexpected:

```text
msDS-KeyCredentialLink
```

values.

Native query example:

```powershell
Get-ADObject -LDAPFilter '(msDS-KeyCredentialLink=*)' -Properties msDS-KeyCredentialLink |
    Select-Object Name,ObjectClass,DistinguishedName
```

The presence of this attribute is not automatically malicious because legitimate Windows authentication technologies can use key credentials.

---

# Delegation Persistence

Kerberos delegation relationships can provide durable access paths.

Review:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

---

# Unconstrained Delegation

See:

[Unconstrained Delegation](unconstrained-delegation.md)

Systems trusted for unconstrained delegation deserve particular attention because privileged authentication to those systems can create credential exposure.

---

# Constrained Delegation

See:

[Constrained Delegation](constrained-delegation.md)

Review:

```text
msDS-AllowedToDelegateTo
TrustedToAuthForDelegation
Service Account
Target Services
```

---

# RBCD

Resource-Based Constrained Delegation is configured on the target computer object.

See:

[Resource-Based Constrained Delegation](rbcd.md)

The relevant attribute is:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

Unexpected values can represent a persistence path.

---

# Search for RBCD Configuration

A read-only query:

```powershell
Get-ADComputer -Filter * -Properties msDS-AllowedToActOnBehalfOfOtherIdentity |
    Where-Object {
        $_.'msDS-AllowedToActOnBehalfOfOtherIdentity'
    } |
    Select-Object Name,DistinguishedName
```

Investigate whether each relationship is authorised.

---

# Group Policy Persistence

Group Policy can provide persistent configuration across many systems.

A principal capable of modifying a GPO can potentially influence every system processing that GPO.

Conceptually:

```text
GPO
 |
 v
OU
 |
 +--> Computer
 +--> Computer
 +--> Computer
```

---

# GPO Persistence Surfaces

Review:

```text
Startup Scripts
Shutdown Scripts
Logon Scripts
Logoff Scripts
Scheduled Tasks
Services
Registry Settings
Security Settings
Software Deployment
Local Group Configuration
```

See:

[Group Policy](group-policy.md)

---

# GPO ACL Persistence

A hidden persistence path can simply be:

```text
Controlled Identity
       |
       v
Can Modify GPO
       |
       v
Privileged Systems
```

The malicious configuration does not need to exist yet.

The permission itself may provide future control.

---

# Enumerate GPOs

```powershell
Get-GPO -All |
    Select-Object DisplayName,Id,CreationTime,ModificationTime
```

Requires the Group Policy PowerShell module.

---

# Recently Modified GPOs

```powershell
Get-GPO -All |
    Sort-Object ModificationTime -Descending |
    Select-Object DisplayName,Id,ModificationTime
```

Correlate changes with authorised change records.

---

# SYSVOL Persistence

GPOs and scripts depend on SYSVOL content.

Review:

```text
Scripts
Policy Files
Scheduled Task XML
Configuration Files
```

for unexpected modifications.

---

# SYSVOL Permissions

Normal users require read access to significant SYSVOL content.

The more important security question is:

```text
Who Has Write Access?
```

Unexpected write access can create persistent control over policy or scripts.

---

# Logon Script Persistence

A script used by privileged users can become a persistence mechanism if an unauthorised principal can modify it.

```text
Writable Script
     |
     v
Privileged User Logs On
     |
     v
Script Executes
```

Validate:

```text
Script Path
ACL
Affected Users
Execution Context
```

---

# Scheduled Task Persistence

Group Policy Preferences and local configuration can create scheduled tasks.

Review:

```powershell
Get-ScheduledTask |
    Select-Object TaskPath,TaskName,State
```

On sensitive systems, investigate unexpected tasks running as:

```text
SYSTEM
Administrator
Service Account
```

---

# Service Persistence

Windows services can provide durable execution.

Review:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,StartMode,PathName
```

Look for:

```text
Unexpected Service
Unusual Binary Path
Privileged Account
Writable Binary
Writable Directory
```

---

# Domain Controller Persistence

Domain controllers are among the highest-value persistence targets.

Review:

```text
Services
Scheduled Tasks
Drivers
Security Packages
Registry
SYSVOL
Directory Objects
Authentication Configuration
EDR Health
```

A compromised domain controller should generally be treated as a major incident rather than remediated through a single password reset.

---

# DCShadow Concept

DCShadow is a technique that abuses Active Directory replication concepts to introduce directory changes through rogue domain-controller-like behaviour.

Conceptually:

```text
Privileged Control
      |
      v
Rogue Replication Behaviour
      |
      v
Directory Modification
```

It is important from a persistence and detection perspective because the resulting directory changes may be the artefact of interest.

---

# DCShadow Testing

Do not perform DCShadow against a production domain merely to verify that a highly privileged account is highly privileged.

Detection and assessment should instead focus on:

```text
Unexpected Directory Changes
Unexpected Replication Configuration
Unexpected SPNs
Unexpected Server Objects
Unexpected Privileged ACLs
```

unless explicit testing of replication abuse is authorised.

---

# Directory Service Objects

Review unexpected changes beneath sensitive Active Directory containers such as:

```text
CN=System
OU=Domain Controllers
Configuration Partition
Sites
Services
Public Key Services
```

according to the incident or assessment scope.

---

# SID History Persistence

The:

```text
sIDHistory
```

attribute is used legitimately during migrations.

However, historical SIDs can affect authorisation.

Conceptually:

```text
Current Account
      |
      v
SID History
      |
      v
Historical SID
      |
      v
Access
```

---

# Enumerate SID History

```powershell
Get-ADUser -Filter * -Properties SIDHistory |
    Where-Object {
        $_.SIDHistory
    } |
    Select-Object SamAccountName,SIDHistory
```

Do not assume every result is malicious.

Validate against migration history.

---

# Privileged SID History

Prioritise accounts whose SID History maps to:

```text
Privileged Groups
Privileged Users
Historical Administrative Domains
```

Unexpected privileged SID History warrants investigation.

---

# Trust Persistence

Domain and forest trusts rely on sensitive trust relationships and secrets.

See:

[Trusts](trusts.md)

Review:

```text
Trust Direction
Trust Type
Transitivity
SID Filtering
Selective Authentication
Trust Account
Unexpected Trusts
```

---

# Enumerate Trusts

```powershell
Get-ADTrust -Filter * |
    Select-Object Name,Source,Target,Direction,ForestTransitive,IntraForest
```

Validate the output against the documented forest architecture.

---

# Trust Secret Compromise

Knowledge of inter-domain trust secrets can have serious authentication implications.

Changing an individual user's password does not address compromise of:

```text
Trust Material
```

Trust recovery should follow supported Active Directory procedures.

---

# AD FS Persistence

AD FS is federation infrastructure.

See:

[AD FS](adfs.md)

High-value persistence areas include:

```text
Token-Signing Certificates
Token-Decrypting Certificates
Service Account
Federation Configuration
Relying Party Trusts
Claims Rules
```

---

# Golden SAML Concept

If federation signing material is compromised, an attacker may potentially create forged federation assertions accepted by relying parties that trust the compromised federation service.

This concept is commonly called:

```text
Golden SAML
```

The trust model is:

```text
Federation Signing Key
        |
        v
Signed Assertion
        |
        v
Relying Party Trust
        |
        v
Application Access
```

---

# AD FS Assessment

Review:

```text
Signing Certificate Protection
Certificate Exportability
AD FS Administrator Access
Service Account
Configuration Backups
Relying Parties
Claims Rules
Audit Logging
```

Do not export production federation signing private keys merely to demonstrate impact.

---

# AD CS Persistence

AD CS persistence can occur through more than certificate issuance.

Review:

```text
CA Permissions
Template Permissions
Enrollment Agent Rights
CA Private Keys
Template Configuration
Certificate Mapping
Enrollment Services
```

A hidden permission on certificate infrastructure can provide a future path even after issued certificates are revoked.

---

# Certificate Template ACLs

A principal capable of modifying an authentication template may have a durable privilege path.

See:

[ESC4](ad-cs/esc4.md)

The important relationship is:

```text
Controlled Identity
       |
       v
Template Modification Rights
       |
       v
Authentication Template
```

---

# CA Administration

Unexpected:

```text
ManageCA
ManageCertificates
```

or equivalent CA administrative permissions should be investigated.

See:

[ESC7](ad-cs/esc7.md)

---

# Certificate Mapping

Certificate mapping behaviour is security-sensitive because certificates can authenticate identities independently of passwords.

Review current domain-controller patching and certificate mapping behaviour when assessing persistence through certificates.

---

# Management Infrastructure Persistence

Enterprise management systems can provide indirect persistence.

Examples include:

```text
SCCM
MDT
WSUS
SCOM
Backup Platforms
Virtualisation Platforms
Remote Management Systems
```

---

# SCCM

See:

[SCCM](sccm.md)

Review:

```text
SCCM Administrators
Security Roles
Collections
Client Push Accounts
Site Server
Distribution Points
Task Sequences
```

A persistent SCCM administrative identity may provide broad control over managed endpoints.

---

# MDT

See:

[MDT](mdt.md)

Review:

```text
Deployment Share ACLs
Bootstrap Credentials
Task Sequences
Scripts
Applications
Boot Images
```

Write access to deployment content can provide durable control over newly deployed systems.

---

# WSUS

See:

[WSUS](wsus.md)

Review:

```text
WSUS Administrators
Update Approval
Server Security
Content Integrity
TLS Configuration
SUSDB Access
```

---

# SCOM

See:

[SCOM](scom.md)

Monitoring infrastructure may have extensive access to managed systems.

Review:

```text
SCOM Administrators
Run As Accounts
Management Servers
Agent Relationships
Automation
```

---

# Backup Infrastructure

Backup platforms are particularly sensitive because they may contain:

```text
Domain Controller Backups
System State
Certificate Authority Backups
AD FS Configuration
Server Images
Secrets
```

Persistence through backup administration may survive remediation of the production server.

---

# Virtualisation Infrastructure

A virtualisation administrator may be able to access:

```text
Domain Controller VM
Certificate Authority VM
AD FS VM
Management Servers
Snapshots
Virtual Disks
Console
```

Therefore hypervisor administration should be included in Tier 0 path analysis where it can control Tier 0 workloads.

---

# DNS Persistence

Active Directory-integrated DNS can influence name resolution.

See:

[Active Directory Integrated DNS](adidns.md)

Review:

```text
Unexpected DNS Records
Delegations
Name Servers
Zone Permissions
Dynamic Update Rights
```

Do not treat every manually created DNS record as suspicious.

---

# SPN Persistence

Service Principal Names affect Kerberos service identity.

Review unusual SPNs on:

```text
Users
Computers
Service Accounts
```

Example:

```powershell
Get-ADUser -Filter {ServicePrincipalName -like "*"} -Properties ServicePrincipalName |
    Select-Object SamAccountName,ServicePrincipalName
```

Unexpected SPN changes should be correlated with directory change events.

---

# UserAccountControl

Security-sensitive account behaviour can also be affected by:

```text
userAccountControl
```

Review unexpected changes involving:

```text
Delegation
Preauthentication
Account State
```

rather than relying only on the current value.

---

# Authentication Policy Persistence

Review changes to:

```text
Authentication Policies
Authentication Policy Silos
Protected Users
Logon Restrictions
```

An attacker with sufficient directory control may attempt to weaken controls that constrain privileged authentication.

---

# Machine Account Persistence

Computer accounts are security principals.

Review unexpected:

```text
New Computer Accounts
Computer Account Owners
SPNs
Delegation
Key Credentials
Group Membership
```

---

# Recently Created Computers

```powershell
$Since = (Get-Date).AddDays(-30)

Get-ADComputer -Filter * -Properties Created |
    Where-Object {
        $_.Created -ge $Since
    } |
    Select-Object Name,Created,DistinguishedName
```

Correlate results with provisioning records.

---

# Machine Account Quota

See:

[Machine Account Quota](machine-account-quota.md)

A non-zero MachineAccountQuota can allow ordinary users to create computer accounts under certain conditions.

The setting alone is not a persistence finding.

Determine whether unexpected machine accounts or additional privilege relationships exist.

---

# Local Persistence on Tier 0 Systems

Active Directory persistence is not limited to directory objects.

Local persistence on:

```text
Domain Controllers
Certificate Authorities
AD FS Servers
Management Servers
Privileged Workstations
```

can provide equivalent strategic impact.

---

# Autoruns

On authorised Windows systems, Microsoft Sysinternals Autoruns can help review persistence locations such as:

```text
Services
Scheduled Tasks
Logon Entries
Drivers
Winlogon
AppInit
Explorer Extensions
```

Use trusted administrative tooling and preserve evidence.

---

# Registry Run Keys

Common user-level persistence locations include:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

and machine-level locations such as:

```text
HKLM\Software\Microsoft\Windows\CurrentVersion\Run
```

On Tier 0 systems, unexpected entries warrant investigation.

---

# Services

Unexpected auto-start services on identity infrastructure should be investigated.

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.StartMode -eq 'Auto'
    } |
    Select-Object Name,StartName,PathName
```

---

# Scheduled Tasks

```powershell
Get-ScheduledTask |
    Select-Object TaskPath,TaskName,State
```

Focus on:

```text
Unexpected Authors
Privileged Run Context
Unusual Executables
User-Writable Paths
Recently Modified Tasks
```

---

# WMI Persistence

WMI permanent event subscriptions can provide local persistence.

Defensive enumeration can review:

```text
__EventFilter
CommandLineEventConsumer
ActiveScriptEventConsumer
__FilterToConsumerBinding
```

in the:

```text
root\subscription
```

namespace.

---

# Enumerate WMI Event Filters

```powershell
Get-CimInstance -Namespace root/subscription -ClassName __EventFilter
```

---

# Enumerate Command-Line Consumers

```powershell
Get-CimInstance -Namespace root/subscription -ClassName CommandLineEventConsumer
```

---

# Enumerate Active Script Consumers

```powershell
Get-CimInstance -Namespace root/subscription -ClassName ActiveScriptEventConsumer
```

---

# Enumerate Bindings

```powershell
Get-CimInstance -Namespace root/subscription -ClassName __FilterToConsumerBinding
```

Unexpected permanent WMI subscriptions on domain controllers or management servers should be investigated.

---

# PowerShell Profiles

PowerShell profiles can provide persistence for specific users or hosts.

Enumerate profile paths:

```powershell
$PROFILE | Format-List *
```

Check only where relevant to the assessed administrative workflow.

---

# Security Support Provider Persistence

Authentication components on domain controllers are extremely sensitive.

Unexpected changes involving:

```text
LSA
Security Packages
Authentication Packages
Notification Packages
```

should be investigated as potential compromise indicators.

Do not modify authentication packages during routine assessment.

---

# Directory Change Detection

Event:

```text
5136
```

can record Active Directory object modifications when appropriate auditing and SACLs are configured.

This is particularly valuable for persistence detection.

---

# Important Directory Changes

Monitor modifications to:

```text
member
nTSecurityDescriptor
servicePrincipalName
msDS-KeyCredentialLink
msDS-AllowedToDelegateTo
msDS-AllowedToActOnBehalfOfOtherIdentity
userAccountControl
sIDHistory
```

where appropriate.

---

# Group Change Events

Relevant events include:

```text
4728
4729
4732
4733
4756
4757
```

depending on group scope.

Prioritise privileged groups.

---

# Account Creation

Event:

```text
4720
```

indicates user account creation.

Correlate:

```text
Account
Creator
Source Host
Timestamp
Change Record
```

---

# Computer Account Creation

Event:

```text
4741
```

can provide visibility into computer account creation.

Unexpected computer creation by ordinary user accounts should be investigated in context.

---

# User Account Changes

Event:

```text
4738
```

can provide visibility into user-account changes.

---

# Password Resets

Event:

```text
4724
```

can indicate an attempt to reset another account's password.

Unexpected resets involving privileged accounts are high-value signals.

---

# Kerberos Events

Important events include:

```text
4768
4769
4771
```

Correlate:

```text
Account
Source
Service
Encryption
Ticket Activity
```

with expected behaviour.

---

# Special Privileges

Event:

```text
4672
```

indicates special privileges assigned to a new logon.

It is useful context for investigating privileged persistence activity.

---

# Process Creation

Event:

```text
4688
```

can provide process-creation telemetry when auditing is enabled.

On Tier 0 systems, combine it with EDR telemetry.

---

# Service Installation

Event:

```text
7045
```

in the System log is commonly useful for identifying newly installed services.

Unexpected services on domain controllers should be investigated immediately.

---

# Scheduled Task Events

Task Scheduler operational logs can provide visibility into task creation and modification.

Centralise these logs for high-value servers where practical.

---

# Certificate Events

AD CS environments should monitor:

```text
Certificate Requests
Certificate Issuance
Certificate Revocation
Template Changes
CA Configuration Changes
```

See the AD CS section for detailed event coverage.

---

# AD FS Monitoring

Monitor:

```text
Certificate Changes
Configuration Changes
Claims Rule Changes
Relying Party Changes
Service Account Activity
Administrative Access
```

on federation infrastructure.

---

# Persistence Hunting Workflow

A useful defensive hunting workflow is:

```text
Baseline
   |
   v
Privileged Accounts
   |
   v
Privileged Groups
   |
   v
Sensitive ACLs
   |
   v
Replication Rights
   |
   v
Delegation
   |
   v
Key Credentials
   |
   v
Certificates
   |
   v
GPOs
   |
   v
Trusts
   |
   v
Tier 0 Hosts
   |
   v
Correlate Changes
```

---

# BloodHound for Persistence Hunting

BloodHound can identify persistent control relationships such as:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
AddMember
AdminTo
AllowedToDelegate
AllowedToAct
DCSync
```

depending on collected data and BloodHound version.

Use BloodHound to answer:

```text
Which non-Tier-0 identities can still control Tier 0?
```

---

# Compare Historical BloodHound Data

Historical graph snapshots can be valuable.

```text
Yesterday
   |
   v
No Path

Today
   |
   v
New ACL
   |
   v
Tier 0 Path
```

A newly introduced relationship may indicate:

```text
Misconfiguration
Administrative Change
Persistence
```

---

# Persistence After Password Reset

An incident-response mistake is assuming:

```text
Password Reset
=
Persistence Removed
```

Potential surviving mechanisms include:

```text
Certificates
Key Credentials
ACLs
Group Membership
Replication Rights
Trust Secrets
CA Keys
Federation Keys
Scheduled Tasks
Services
```

---

# Persistence After Account Disablement

Disabling one compromised account may still leave:

```text
Second Account
Computer Account
Service Account
ACL Delegation
Certificate
Trust Material
Local Persistence
```

Therefore remediation should focus on the entire attack path.

---

# Persistence After Rebuild

Rebuilding one compromised endpoint may not remove persistence stored in:

```text
Active Directory
Group Policy
AD CS
AD FS
Management Platforms
Trusts
Backups
```

---

# Persistence After Domain Admin Removal

Removing an attacker-controlled account from:

```text
Domain Admins
```

does not address:

```text
WriteDacl on Domain
DCSync Rights
AdminSDHolder ACL
Certificate Authentication
Shadow Credentials
GPO Control
```

---

# Incident Response Model

When privileged compromise is suspected:

```text
Contain
   |
   v
Preserve Evidence
   |
   v
Identify Initial Access
   |
   v
Identify Privilege Escalation
   |
   v
Identify Persistence
   |
   v
Identify Credential Exposure
   |
   v
Remediate Trust
   |
   v
Monitor for Re-entry
```

---

# Persistence Scope

Determine whether persistence exists at:

```text
Endpoint
Server
Domain
Forest
PKI
Federation
Management Infrastructure
Cloud Identity
```

The recovery scope should match the highest affected trust layer.

---

# Hardening Against Persistence

Persistence prevention depends on reducing unnecessary control over identity infrastructure.

A strong model is:

```text
Least Privilege
      +
Administrative Tiering
      +
Change Monitoring
      +
Credential Protection
      +
PKI Protection
      +
Secure Management
      +
Regular Baselines
```

---

# Minimise Standing Privilege

Reduce permanent membership in:

```text
Domain Admins
Enterprise Admins
Schema Admins
```

and equivalent privileged groups.

Use time-bound or just-in-time privilege where supported.

---

# Protect Tier 0

Treat systems capable of controlling domain identity as Tier 0 or equivalent high-value infrastructure.

This can include:

```text
Domain Controllers
Certificate Authorities
AD FS
Privileged Access Systems
Management Platforms
Backup Systems
Virtualisation Hosting Tier 0
```

depending on architecture.

---

# Restrict ACL Delegation

Regularly review:

```text
WriteDacl
WriteOwner
GenericAll
GenericWrite
Replication Rights
Group Management Rights
```

on sensitive objects.

---

# Protect AdminSDHolder

Maintain a known-good baseline for:

```text
AdminSDHolder
```

and investigate unexpected permission changes.

---

# Protect krbtgt

Restrict access to domain controllers and credential material that could expose the `krbtgt` secret.

A `krbtgt` password reset should be an incident-response procedure, not routine pentest activity.

---

# Protect Certificate Authorities

Treat CA private keys as highly sensitive authentication trust material.

Protect:

```text
CA Servers
Private Keys
Backups
HSMs
Templates
CA Administration
Enrollment Services
```

---

# Protect Federation Infrastructure

Treat AD FS signing keys and federation administration as high-value trust assets.

---

# Secure Service Accounts

Prefer managed identities such as gMSAs where appropriate.

Apply:

```text
Least Privilege
Restricted Logon
Strong Credential Management
Minimal Group Membership
Monitoring
```

---

# Protect Group Policy

Restrict:

```text
GPO Creation
GPO Modification
GPO Linking
SYSVOL Write Access
```

to authorised administrators.

---

# Secure Management Platforms

Apply strong administrative controls to:

```text
SCCM
WSUS
MDT
SCOM
Backup
Virtualisation
Remote Management
```

because these platforms can indirectly control privileged systems.

---

# Monitor Changes

Alert on changes to:

```text
Privileged Groups
Sensitive ACLs
Replication Rights
Delegation
Key Credentials
Certificate Templates
CA Configuration
GPOs
Trusts
Tier 0 Services
```

---

# Maintain Known-Good Baselines

Baselines should include:

```text
Privileged Group Membership
Sensitive ACLs
GPO Hashes / Versions
Trusts
Certificate Templates
CA Configuration
Delegation
Tier 0 Scheduled Tasks
Tier 0 Services
```

This makes hidden persistence substantially easier to identify.

---

# Reporting Persistence

A good persistence finding should identify:

```text
Persistent Mechanism
       |
       v
Controlled Principal
       |
       v
Sensitive Target
       |
       v
Survives Normal Remediation?
       |
       v
Potential Impact
```

---

# Example Finding - Hidden ACL Persistence

```text
Finding:
Non-Administrative Account Retains Control Over a Privileged Group

Description:
A non-administrative account had an explicit Active Directory access
control entry that allowed it to modify the security configuration of
a privileged group.

The account was not itself a member of the privileged group, making
the control relationship less visible during ordinary membership
reviews.

The assessment validated the ACL without modifying the privileged
group or its permissions.

Impact:
Compromise of the affected account could provide a path to restore or
obtain privileged access even after existing privileged group
membership is reviewed or removed.

Recommendation:
Remove the unnecessary access control entry.

Review ACLs on other privileged users, groups, OUs, GPOs and the
domain root for equivalent delegated permissions.

Maintain a baseline of security descriptors for Tier 0 objects.
```

---

# Example Finding - Replication Persistence

```text
Finding:
Unexpected Account Retains Active Directory Replication Rights

Description:
A non-domain-controller account possessed directory replication rights
on the domain object.

The assessment confirmed the permissions through read-only ACL
analysis and did not request credential data through replication.

Impact:
If the permissions are sufficient for sensitive directory replication,
the account may provide continued access to domain credential material
without requiring membership of Domain Admins.

Removing ordinary administrator group membership would therefore not
fully remove the privilege path.

Recommendation:
Remove unnecessary directory replication permissions.

Restrict these rights to domain controllers and explicitly approved
identity-management systems.

Review equivalent rights across all domains in the forest.
```

---

# Example Finding - Shadow Credential Persistence

```text
Finding:
Unexpected Key Credential Provides Alternative Authentication Path

Description:
A privileged Active Directory identity contained an unexpected key
credential configuration.

The configuration could not be associated with the organisation's
documented authentication deployment.

No new key credential was added during the assessment.

Impact:
An unauthorised key credential may provide an alternative
certificate-backed authentication path that can survive an ordinary
password reset.

Recommendation:
Validate the key credential against legitimate Windows Hello for
Business or other approved key-trust deployments.

Remove unauthorised key credentials, investigate the account's change
history and review permissions allowing modification of
msDS-KeyCredentialLink.
```

---

# Example Finding - GPO Persistence

```text
Finding:
Non-Privileged Account Can Modify a GPO Applied to Tier 0 Systems

Description:
A non-privileged Active Directory principal had modification rights
over a Group Policy Object processed by sensitive administrative
systems.

The assessment verified the GPO ACL and links without changing the
policy.

Impact:
The account could potentially introduce persistent configuration that
is repeatedly applied to affected systems.

Removing a previously compromised local account would not address the
underlying GPO control path.

Recommendation:
Restrict modification of the GPO to dedicated Tier 0 administrators.

Review GPO ownership, ACLs, links and SYSVOL permissions for all
policies applied to privileged infrastructure.
```

---

# Example Finding - Certificate Persistence

```text
Finding:
Long-Lived Authentication Certificate Remains Valid After Credential Reset

Description:
An authentication certificate associated with a privileged identity
remained valid independently of the account's recently changed
password.

Impact:
Password rotation alone may not invalidate previously issued
certificate-based authentication material.

If the certificate or its private key has been compromised, an
attacker may retain access after conventional password remediation.

Recommendation:
Include certificate inventory and revocation in the privileged account
incident-response process.

Investigate certificate issuance, protect private keys and review the
relevant AD CS template and enrollment configuration.
```

---

# Example Finding - Management Infrastructure Persistence

```text
Finding:
Excessive SCCM Administrative Rights Provide Persistent Control Over Sensitive Systems

Description:
An account outside the approved privileged administration team
possessed SCCM rights over collections containing sensitive servers.

Impact:
The management relationship may provide a persistent path to systems
with greater Active Directory privilege.

Removing the account from Active Directory administrative groups would
not remove its SCCM management capability.

Recommendation:
Review SCCM security roles, scopes and collection permissions.

Restrict management of sensitive systems to dedicated privileged
administrators and include management-platform permissions in Tier 0
access reviews.
```

---

# Persistence Assessment Checklist

## Accounts

- [ ] Enumerate privileged accounts
- [ ] Review recently created users
- [ ] Review recently enabled users
- [ ] Review dormant accounts
- [ ] Review service accounts
- [ ] Review unexpected computer accounts
- [ ] Review account owners
- [ ] Review account creation history

## Groups

- [ ] Review Domain Admins
- [ ] Review Enterprise Admins
- [ ] Review Schema Admins
- [ ] Review Administrators
- [ ] Review environment-specific privileged groups
- [ ] Review nested membership
- [ ] Review group ownership
- [ ] Review group modification rights
- [ ] Compare with known-good membership

## ACLs

- [ ] Review domain root ACL
- [ ] Review AdminSDHolder
- [ ] Review privileged users
- [ ] Review privileged groups
- [ ] Review Domain Controllers OU
- [ ] Review Tier 0 OUs
- [ ] Review GPO ACLs
- [ ] Review certificate infrastructure ACLs
- [ ] Review GenericAll
- [ ] Review GenericWrite
- [ ] Review WriteDacl
- [ ] Review WriteOwner
- [ ] Review explicit non-standard ACEs

## Replication

- [ ] Review replication rights
- [ ] Identify non-DC replication principals
- [ ] Review DCSync-capable paths
- [ ] Validate business justification
- [ ] Avoid extracting credentials unnecessarily

## Kerberos

- [ ] Assess whether `krbtgt` was exposed
- [ ] Review service-account secrets
- [ ] Review computer-account secrets
- [ ] Review RODC-specific krbtgt exposure
- [ ] Review trust material
- [ ] Follow supported recovery guidance

## Certificates

- [ ] Inventory authentication certificates
- [ ] Review certificate validity
- [ ] Review privileged certificates
- [ ] Review certificate templates
- [ ] Review template ACLs
- [ ] Review CA permissions
- [ ] Review CA private-key protection
- [ ] Review certificate revocation
- [ ] Review CA backups

## Key Credentials

- [ ] Review `msDS-KeyCredentialLink`
- [ ] Identify unexpected key credentials
- [ ] Identify who can modify key credentials
- [ ] Validate legitimate Windows Hello usage
- [ ] Review privileged identities

## Delegation

- [ ] Review unconstrained delegation
- [ ] Review constrained delegation
- [ ] Review RBCD
- [ ] Review `msDS-AllowedToDelegateTo`
- [ ] Review `msDS-AllowedToActOnBehalfOfOtherIdentity`
- [ ] Review delegation-related ACLs
- [ ] Compare with architecture baseline

## Group Policy

- [ ] Inventory GPOs
- [ ] Review recently modified GPOs
- [ ] Review GPO ACLs
- [ ] Review GPO ownership
- [ ] Review GPO links
- [ ] Review startup scripts
- [ ] Review logon scripts
- [ ] Review scheduled tasks
- [ ] Review services
- [ ] Review SYSVOL write permissions

## SID History

- [ ] Enumerate SID History
- [ ] Validate migration requirements
- [ ] Identify privileged historical SIDs
- [ ] Review unexpected SID History
- [ ] Correlate with trust configuration

## Trusts

- [ ] Inventory trusts
- [ ] Review trust direction
- [ ] Review trust type
- [ ] Review SID filtering
- [ ] Review selective authentication
- [ ] Review unexpected trusts
- [ ] Review trust account changes
- [ ] Consider trust-secret exposure during incidents

## Domain Controllers

- [ ] Review services
- [ ] Review scheduled tasks
- [ ] Review WMI subscriptions
- [ ] Review autoruns
- [ ] Review authentication packages
- [ ] Review unexpected binaries
- [ ] Review EDR health
- [ ] Review privileged logons
- [ ] Review directory changes
- [ ] Review replication configuration

## AD CS

- [ ] Review CA administrators
- [ ] Review certificate managers
- [ ] Review template administrators
- [ ] Review enrollment rights
- [ ] Review issued privileged certificates
- [ ] Review private-key security
- [ ] Review CA backups
- [ ] Review enrollment services
- [ ] Review certificate mapping

## AD FS

- [ ] Review AD FS administrators
- [ ] Review service account
- [ ] Review token-signing certificates
- [ ] Review token-decrypting certificates
- [ ] Review relying parties
- [ ] Review claims rules
- [ ] Review configuration changes
- [ ] Review federation backups

## Infrastructure

- [ ] Review SCCM
- [ ] Review MDT
- [ ] Review WSUS
- [ ] Review SCOM
- [ ] Review backup systems
- [ ] Review virtualisation
- [ ] Review deployment systems
- [ ] Review privileged remote-management systems

## Detection

- [ ] Monitor account creation
- [ ] Monitor account changes
- [ ] Monitor privileged group changes
- [ ] Monitor ACL changes
- [ ] Monitor delegation changes
- [ ] Monitor key credential changes
- [ ] Monitor GPO changes
- [ ] Monitor trust changes
- [ ] Monitor certificate activity
- [ ] Monitor privileged logons
- [ ] Monitor service installation
- [ ] Monitor scheduled tasks
- [ ] Monitor Tier 0 process execution

## Incident Response

- [ ] Identify initial access
- [ ] Identify privilege escalation
- [ ] Identify persistence
- [ ] Identify affected trust layer
- [ ] Inventory exposed credentials
- [ ] Inventory certificates
- [ ] Inventory key credentials
- [ ] Review ACLs
- [ ] Review groups
- [ ] Review trusts
- [ ] Review GPOs
- [ ] Review management platforms
- [ ] Preserve evidence
- [ ] Remove persistence
- [ ] Rotate affected secrets
- [ ] Validate recovery
- [ ] Monitor for re-entry

## Reporting

- [ ] Identify persistent mechanism
- [ ] Identify controlling principal
- [ ] Identify sensitive target
- [ ] Explain why ordinary password reset is insufficient
- [ ] Explain blast radius
- [ ] Include read-only evidence where possible
- [ ] Avoid exposing secrets
- [ ] Document active validation
- [ ] Document cleanup
- [ ] Provide root-cause remediation

---

# Persistence Testing Model

The account model is:

```text
Controlled Identity
       |
       v
Persistent Account
       |
       v
Future Access
```

The group model is:

```text
Controlled Identity
       |
       v
Privileged Group
       |
       v
Persistent Privilege
```

The ACL model is:

```text
Controlled Identity
       |
       v
Hidden ACE
       |
       v
Sensitive Object
       |
       v
Future Control
```

The replication model is:

```text
Controlled Identity
       |
       v
Replication Rights
       |
       v
Directory Secrets
       |
       v
Domain-Level Access
```

The Kerberos model is:

```text
Long-Term Secret
       |
       v
Kerberos Trust
       |
       v
Authentication
```

The certificate model is:

```text
Certificate / Private Key
          |
          v
Trusted PKI
          |
          v
Authentication
```

The Shadow Credential model is:

```text
Key Credential
      |
      v
Target Account
      |
      v
Alternative Authentication
```

The GPO model is:

```text
GPO Control
    |
    v
Persistent Configuration
    |
    v
Managed Systems
```

The trust model is:

```text
Trust Material
     |
     v
Cross-Domain Authentication
     |
     v
Persistent Access Path
```

The infrastructure model is:

```text
Management Platform
       |
       v
Managed Systems
       |
       v
Persistent Administrative Reach
```

The complete persistence model is:

```text
Privileged Compromise
        |
        +--> Account
        |
        +--> Group
        |
        +--> ACL
        |
        +--> Replication Rights
        |
        +--> Kerberos Secret
        |
        +--> Certificate
        |
        +--> Key Credential
        |
        +--> Delegation
        |
        +--> GPO
        |
        +--> Trust
        |
        +--> Management Platform
        |
        +--> Tier 0 Host
        |
        v
Persistent Access
```

The most important distinction is:

```text
Credential Rotation
       !=
Persistence Removal
```

Another important distinction is:

```text
No Unknown Domain Admins
       !=
No Domain Persistence
```

A domain may have completely normal privileged group membership while an unauthorised identity retains:

```text
WriteDacl
DCSync
GPO Control
Certificate Authentication
Shadow Credentials
Delegation
```

For penetration testers:

```text
Do Not Ask:
"How many persistence mechanisms
can I install?"

Ask:
"Which existing permissions or trust
relationships would allow persistence,
and can I demonstrate the risk without
creating durable production access?"
```

For defenders:

```text
Do Not Ask:
"Did we reset the compromised password?"

Ask:
"What other authentication material,
permissions, certificates, groups,
delegations and management relationships
did the compromised identity control?"
```

For incident responders:

```text
Compromised Account
       |
       v
Determine Reach
       |
       v
Determine Privilege
       |
       v
Determine Persistence
       |
       v
Determine Trust Compromise
       |
       v
Recover
```

The security objective is:

```text
Remove the Persistence Mechanism
+
Remove the Root Cause
+
Rotate Exposed Trust Material
+
Validate the Environment
```

rather than simply:

```text
Delete the Attacker's Account
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Methodology:

[Methodology](methodology.md)

Enumeration:

[Enumeration](enumeration.md)

Privilege Escalation:

[Privilege Escalation](privilege-escalation.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Groups:

[Groups](groups.md)

Group Policy:

[Group Policy](group-policy.md)

Credential Access:

[Credential Access](credential-access.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

NTDS:

[NTDS](ntds.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

Constrained Delegation:

[Constrained Delegation](constrained-delegation.md)

Resource-Based Constrained Delegation:

[RBCD](rbcd.md)

Shadow Credentials:

[Shadow Credentials](shadow-credentials.md)

Machine Account Quota:

[Machine Account Quota](machine-account-quota.md)

gMSA:

[gMSA](gmsa.md)

LAPS:

[LAPS](laps.md)

Active Directory Certificate Services:

[Active Directory Certificate Services](ad-cs/index.md)

Golden Certificate:

[Golden Certificate](ad-cs/golden-certificate.md)

Trusts:

[Trusts](trusts.md)

Active Directory Integrated DNS:

[ADIDNS](adidns.md)

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

## Microsoft - Security Groups

[Microsoft Learn - Active Directory Security Groups](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Privileged Access

[Microsoft Learn - Enterprise Access Model](https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Protected Users

[Microsoft Learn - Protected Users Security Group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Kerberos

[Microsoft Learn - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Forest Recovery

[Microsoft Learn - Active Directory Forest Recovery Guide](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Reset the krbtgt Password

[Microsoft Learn - Reset the krbtgt Password](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft Learn - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Group Managed Service Accounts

[Microsoft Learn - Group Managed Service Accounts Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD FS

[Microsoft Learn - Active Directory Federation Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/ad-fs-overview){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - BloodHound

[SpecterOps - BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Account Manipulation

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Additional Cloud Roles

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Create Account

[MITRE ATT&CK - Create Account](https://attack.mitre.org/techniques/T1136/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Scheduled Task / Job

[MITRE ATT&CK - Scheduled Task / Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Server Software Component

[MITRE ATT&CK - Server Software Component](https://attack.mitre.org/techniques/T1505/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Steal or Forge Kerberos Tickets

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Golden Ticket

[MITRE ATT&CK - Golden Ticket](https://attack.mitre.org/techniques/T1558/001/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Silver Ticket

[MITRE ATT&CK - Silver Ticket](https://attack.mitre.org/techniques/T1558/002/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Additional Container Cluster Roles

[MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Active Directory persistence should be treated as a:

```text
Trust Problem
```

rather than simply an:

```text
Account Problem
```

A compromised administrator can potentially influence:

```text
Accounts
Groups
ACLs
Kerberos
Certificates
Delegation
Group Policy
Trusts
Management Infrastructure
```

This means:

```text
Reset Password
```

may address only one layer.

A useful persistence review asks:

```text
Who Can Authenticate?

Who Can Become Privileged?

Who Can Modify Privileged Objects?

Who Can Replicate Directory Secrets?

Who Holds Authentication Certificates?

Who Can Modify Key Credentials?

Who Controls Kerberos Delegation?

Who Controls GPOs?

Who Controls Certificate Authorities?

Who Controls Federation?

Who Controls Tier 0 Management Systems?
```

The strongest persistence mechanisms often rely on legitimate Active Directory functionality.

For example:

```text
ACL
Certificate
Group Membership
Delegation
Replication
```

may all be normal features.

The security issue is:

```text
Who Controls Them?
```

A complete recovery model is therefore:

```text
Compromise
    |
    v
Identify Initial Access
    |
    v
Identify Escalation
    |
    v
Identify Persistence
    |
    v
Identify Exposed Trust Material
    |
    v
Remove Unauthorised Control
    |
    v
Rotate Affected Secrets
    |
    v
Revoke Affected Certificates
    |
    v
Restore Known-Good Configuration
    |
    v
Monitor for Re-entry
```

For security assessments, the preferred approach is:

```text
Discover
   |
   v
Analyse
   |
   v
Validate Minimally
   |
   v
Report
```

rather than:

```text
Install Persistence
   |
   v
Prove It Works
```

In many environments, demonstrating that an unauthorised principal possesses:

```text
WriteDacl
DCSync
GPO Control
Certificate Control
Key Credential Control
```

already provides sufficient evidence of the persistence risk without introducing a durable production backdoor.

The final objective is not merely to ensure:

```text
No Attacker Account Exists
```

but to ensure:

```text
No Unauthorised Path Back to Privilege Exists
```
