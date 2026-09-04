# Group Managed Service Accounts - gMSA

Group Managed Service Accounts, commonly abbreviated as gMSA, are Active Directory accounts designed for running services and scheduled tasks without administrators having to manually manage long-lived service account passwords.

A traditional service account might use:

```text
CORP\svc_sql
        |
        v
Manually Managed Password
        |
        +--> Windows Service
        +--> Scheduled Task
        +--> IIS Application Pool
        +--> Other Service
```

This creates several common security problems:

```text
Static Password
Password Never Expires
Password Reuse
Password Stored in Scripts
Password Shared with Administrators
Weak Password Rotation
```

A gMSA changes the model:

```text
gMSA
 |
 v
Active Directory
 |
 v
Automatically Managed Password
 |
 v
Authorised Computers Retrieve Password
 |
 v
Service Runs Using gMSA
```

The password is automatically generated and maintained by Active Directory.

From a penetration-testing perspective, the central security question is:

```text
Who can retrieve the gMSA password?
```

If an attacker controls a principal that is authorised to retrieve a gMSA password, the gMSA may become usable as another domain identity.

A simplified attack path is:

```text
Compromised Principal
        |
        v
Can Retrieve gMSA Password
        |
        v
gMSA Credential Material
        |
        v
Authenticate as gMSA
        |
        v
gMSA Privileges
```

The resulting impact depends entirely on what the gMSA can access.

!!! warning "Authorised testing only"
    gMSA password material is sensitive domain credential material. Begin with directory enumeration and permission analysis. Do not retrieve production gMSA password material unless credential-access validation is explicitly authorised. Where retrieval is necessary, collect the minimum evidence required and avoid unnecessary authentication, lateral movement, or credential persistence.

---

# What Is a Service Account?

Services frequently require an identity.

Examples include:

```text
SQL Server
IIS
Backup Software
Monitoring Agents
Scheduled Tasks
Application Services
Automation Platforms
Management Services
```

A service account allows the application to authenticate to:

```text
Local Resources
Network Shares
Databases
Active Directory
Remote Servers
Other Applications
```

Traditional domain service accounts are usually normal Active Directory user objects.

Example:

```text
CORP\svc_backup
```

---

# Traditional Service Account Problem

A traditional service account commonly requires:

```text
Username
+
Password
```

Administrators must then manage:

```text
Password Creation
Password Storage
Password Distribution
Password Rotation
Service Configuration
```

This often results in:

```text
PasswordNeverExpires = True
```

or passwords stored in:

```text
Scripts
Configuration Files
Documentation
Password Vaults
Deployment Systems
```

---

# Managed Service Accounts

Microsoft introduced Managed Service Accounts to reduce this problem.

There are two related account types:

```text
sMSA
gMSA
```

where:

```text
sMSA = Standalone Managed Service Account
gMSA = Group Managed Service Account
```

---

# sMSA

A standalone Managed Service Account is primarily associated with a single computer.

Conceptually:

```text
sMSA
 |
 v
Single Computer
 |
 v
Service
```

---

# gMSA

A Group Managed Service Account can be used by multiple authorised computers.

Conceptually:

```text
             gMSA
              |
       +------+------+
       |             |
       v             v
   SERVER01       SERVER02
       |             |
       v             v
    Service        Service
```

This makes gMSAs useful for:

```text
Server Farms
Load-Balanced Services
Scheduled Tasks
Multi-Server Applications
```

---

# gMSA Object

A gMSA is represented in Active Directory as an object of class:

```text
msDS-GroupManagedServiceAccount
```

The account typically has a name ending in:

```text
$
```

For example:

```text
WEB-SVC$
```

This resembles a computer account name, but the object is a managed service account.

---

# Important gMSA Attributes

Important attributes include:

```text
sAMAccountName
servicePrincipalName
msDS-ManagedPassword
msDS-ManagedPasswordId
msDS-ManagedPasswordInterval
msDS-GroupMSAMembership
userAccountControl
memberOf
```

The most security-sensitive attribute is:

```text
msDS-ManagedPassword
```

---

# msDS-ManagedPassword

The managed password information is stored in:

```text
msDS-ManagedPassword
```

This is not a normal plaintext string attribute.

It contains a structured managed-password blob.

Conceptually:

```text
gMSA
 |
 v
msDS-ManagedPassword
 |
 v
Managed Password Blob
 |
 v
Credential Material
```

An authorised system can retrieve the information required to use the gMSA.

---

# Managed Password Blob

The managed-password blob can contain information related to:

```text
Current Password
Previous Password
Password Update Interval
Query Interval
```

depending on the state of the account and password rollover.

Security tools can parse this structure and derive usable authentication material.

---

# Password Generation

gMSA passwords are automatically managed by Active Directory.

The service administrator does not normally need to know or manually type the password.

Conceptually:

```text
Active Directory
      |
      v
Generate Managed Password
      |
      v
gMSA
      |
      v
Authorised Host Retrieves It
      |
      v
Service Authentication
```

---

# Password Rotation

The managed password is periodically changed.

Conceptually:

```text
Password A
    |
    v
Automatic Rotation
    |
    v
Password B
    |
    v
Automatic Rotation
    |
    v
Password C
```

This reduces the risks associated with manually maintained static service-account passwords.

---

# KDS Root Key

gMSA password generation depends on the:

```text
Key Distribution Service
```

commonly:

```text
KDS
```

and a KDS root key.

The KDS root key provides cryptographic material used by domain controllers to derive managed service account passwords.

Conceptually:

```text
KDS Root Key
     |
     v
Domain Controller
     |
     v
Password Derivation
     |
     v
gMSA Password
```

---

# KDS Root Key Enumeration

Administrators can inspect KDS root keys using:

```powershell
Get-KdsRootKey
```

This is normally administrative information rather than a routine penetration-testing target.

Do not attempt to alter or recreate KDS root keys during an assessment.

---

# Creating a KDS Root Key

Administrators can create a KDS root key using:

```powershell
Add-KdsRootKey
```

This changes domain infrastructure and should never be performed during a penetration test unless explicitly part of a controlled lab exercise.

---

# gMSA Password Retrieval Security

The important security relationship is:

```text
Principal
   |
   v
Authorised to Retrieve
Managed Password
   |
   v
gMSA
```

The permission is represented through:

```text
msDS-GroupMSAMembership
```

on the gMSA object.

---

# msDS-GroupMSAMembership

The:

```text
msDS-GroupMSAMembership
```

attribute contains a security descriptor controlling which principals are permitted to retrieve the gMSA managed password.

Conceptually:

```text
gMSA
 |
 v
msDS-GroupMSAMembership
 |
 v
Security Descriptor
 |
 v
Authorised Principals
```

This is one of the most important attributes to review during a gMSA assessment.

---

# PrincipalsAllowedToRetrieveManagedPassword

When administrators create or configure a gMSA through PowerShell, the authorised principals are commonly managed through:

```text
PrincipalsAllowedToRetrieveManagedPassword
```

Example conceptual configuration:

```text
gMSA:
WEB-SVC$

Allowed:
WEB-SERVERS
```

where:

```text
WEB-SERVERS
```

is a group containing the computers that legitimately run the service.

---

# Secure Model

A well-scoped configuration looks like:

```text
WEB-SERVERS
    |
    +--> WEB01$
    +--> WEB02$
    |
    v
Can Retrieve
    |
    v
WEB-SVC$
```

---

# Weak Model

A dangerous configuration might look like:

```text
Domain Computers
       |
       v
Can Retrieve
       |
       v
HIGHVALUE-SVC$
```

Compromise of any authorised computer could potentially provide access to the gMSA credential material.

---

# Why gMSA Permissions Matter

A gMSA might have:

```text
No Interactive User
Strong Managed Password
Automatic Rotation
```

and still present a serious attack path if too many principals can retrieve its password.

The correct security model is:

```text
Strong Password
      +
Weak Retrieval Permissions
      =
Weak Credential Boundary
```

---

# Initial gMSA Assessment

Determine:

```text
Which gMSAs exist?

Which services use them?

Which SPNs belong to them?

Which groups contain them?

Who can retrieve their passwords?

Which computers are authorised?

What privileges do the gMSAs have?

Are any gMSAs Tier 0?

Are retrieval permissions excessively broad?
```

---

# Enumerate gMSAs with PowerShell

Using the ActiveDirectory module:

```powershell
Get-ADServiceAccount \
    -Filter *
```

A more useful query:

```powershell
Get-ADServiceAccount \
    -Filter * \
    -Properties *
```

Avoid displaying every property unnecessarily in large environments.

---

# Selected gMSA Properties

```powershell
Get-ADServiceAccount \
    -Filter * \
    -Properties \
        DistinguishedName,
        Enabled,
        ServicePrincipalNames,
        PrincipalsAllowedToRetrieveManagedPassword,
        MemberOf |
    Select-Object \
        Name,
        SamAccountName,
        Enabled,
        DistinguishedName,
        ServicePrincipalNames,
        PrincipalsAllowedToRetrieveManagedPassword,
        MemberOf
```

---

# Enumerate One gMSA

```powershell
Get-ADServiceAccount \
    -Identity 'WEB-SVC' \
    -Properties *
```

---

# Find gMSA Objects Directly

Another approach:

```powershell
Get-ADObject \
    -LDAPFilter '(objectClass=msDS-GroupManagedServiceAccount)' \
    -Properties *
```

For a cleaner result:

```powershell
Get-ADObject \
    -LDAPFilter '(objectClass=msDS-GroupManagedServiceAccount)' \
    -Properties \
        sAMAccountName,
        servicePrincipalName,
        msDS-ManagedPasswordInterval |
    Select-Object \
        Name,
        sAMAccountName,
        servicePrincipalName,
        msDS-ManagedPasswordInterval
```

---

# LDAP Filter

The core LDAP filter is:

```text
(objectClass=msDS-GroupManagedServiceAccount)
```

This is useful across:

```text
PowerShell
ldapsearch
Custom LDAP Tools
Directory Browsers
```

---

# Linux Enumeration with ldapsearch

Example:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(objectClass=msDS-GroupManagedServiceAccount)' \
    sAMAccountName \
    distinguishedName \
    servicePrincipalName \
    msDS-ManagedPasswordInterval
```

This performs metadata enumeration without requesting:

```text
msDS-ManagedPassword
```

---

# Prefer Metadata Enumeration First

Use:

```text
Metadata
   |
   v
Permission Analysis
   |
   v
Impact Analysis
```

before:

```text
Credential Retrieval
```

A good sequence is:

```text
Enumerate gMSAs
      |
      v
Identify SPNs
      |
      v
Identify Group Membership
      |
      v
Identify Password Readers
      |
      v
Determine Privilege
      |
      v
Retrieve Only If Required
```

---

# Enumerate SPNs

PowerShell:

```powershell
Get-ADServiceAccount \
    -Filter * \
    -Properties ServicePrincipalNames |
    Select-Object \
        Name,
        SamAccountName,
        ServicePrincipalNames
```

SPNs can reveal the services associated with the account.

Examples:

```text
HTTP/web01.corp.example
MSSQLSvc/sql01.corp.example:1433
HOST/server01.corp.example
```

---

# gMSA and Kerberos

gMSAs are domain security principals and can participate in Kerberos authentication.

Conceptually:

```text
gMSA Credential
      |
      v
Kerberos
      |
      v
TGT
      |
      v
Service Tickets
```

Therefore compromise of a gMSA can enable access to resources available to that account.

See:

[Kerberos](kerberos.md)

---

# gMSA and Kerberoasting

A gMSA may have:

```text
SPNs
```

and therefore be technically Kerberoastable.

However, gMSA passwords are automatically generated and highly random.

Therefore conventional offline password cracking against a properly managed gMSA is generally impractical.

The distinction is:

```text
Traditional Service Account
      |
      v
Human Password
      |
      v
Potential Kerberoasting Risk
```

versus:

```text
gMSA
 |
 v
Long Random Managed Password
 |
 v
Kerberoasting Cracking Impractical
```

This is one of the security advantages of gMSAs.

See:

[Kerberoasting](kerberoasting.md)

---

# Do Not Report Every gMSA SPN as Vulnerable

Finding:

```text
gMSA Has SPN
```

does not mean:

```text
Weak Kerberoasting Finding
```

The managed password characteristics fundamentally change the cracking risk.

Instead review:

```text
Password Retrieval Permissions
Account Privileges
Delegated Rights
Service Access
```

---

# Enumerate Group Membership

```powershell
Get-ADServiceAccount \
    -Identity 'WEB-SVC' \
    -Properties MemberOf |
    Select-Object \
        Name,
        MemberOf
```

Also investigate nested group relationships.

See:

[Active Directory Groups](groups.md)

---

# Privileged Group Membership

A gMSA should not normally be granted unnecessary membership in groups such as:

```text
Domain Admins
Enterprise Admins
Administrators
Backup Operators
Server Operators
Account Operators
```

The exact risk depends on the environment.

Do not assume every service account requires administrative privilege.

---

# gMSA Privilege Model

```text
gMSA
 |
 v
Group Membership
 |
 v
Rights
 |
 v
Resources
```

But group membership is only part of the picture.

Also analyse:

```text
ACLs
Local Groups
GPO Rights
Application Permissions
Database Permissions
AD CS Permissions
Delegated Directory Rights
```

---

# BloodHound

BloodHound can help identify attack paths involving gMSAs.

Depending on BloodHound version and collected data, relationships may show that a principal can retrieve a gMSA password.

A conceptual path is:

```text
Alice
 |
 v
ReadGMSAPassword
 |
 v
WEB-SVC$
```

This means Alice may be able to obtain credential material associated with the gMSA.

---

# ReadGMSAPassword

The BloodHound relationship commonly associated with gMSA retrieval is:

```text
ReadGMSAPassword
```

The important model is:

```text
Source Principal
      |
      v
ReadGMSAPassword
      |
      v
gMSA
```

Then determine:

```text
What Can the gMSA Do?
```

---

# BloodHound Attack Path

Example:

```text
alice
 |
 v
MemberOf
 |
 v
WEB-SERVERS
 |
 v
ReadGMSAPassword
 |
 v
WEB-SVC$
 |
 v
AdminTo
 |
 v
APP01
```

The gMSA retrieval permission becomes one step in a larger attack path.

---

# High-Value gMSA Example

```text
Low-Privilege User
       |
       v
ReadGMSAPassword
       |
       v
BACKUP-SVC$
       |
       v
Backup Infrastructure
       |
       v
Domain Controller Backups
```

This may represent a significant escalation path even if the gMSA is not a member of:

```text
Domain Admins
```

---

# Validate BloodHound Findings

Use:

```text
BloodHound
     |
     v
Identify Relationship
     |
     v
Validate Directory Permission
     |
     v
Determine gMSA Privilege
     |
     v
Assess Impact
```

Do not report a graph relationship without understanding its underlying permission.

---

# SharpHound

SharpHound can collect directory information used by BloodHound.

Collection should be performed according to the authorised scope and environment size.

See:

[BloodHound](bloodhound.md)

---

# gMSA ACL Analysis

gMSA objects have normal Active Directory security descriptors in addition to their managed-password retrieval security model.

Therefore review:

```text
Object ACL
      |
      +--> GenericAll
      +--> GenericWrite
      +--> WriteDACL
      +--> WriteOwner
      +--> WriteProperty
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# GenericAll over gMSA

If a principal has:

```text
GenericAll
```

over a gMSA object, it may be able to modify sensitive aspects of that object.

Do not reduce analysis to:

```text
Can Read Password?
```

Object control may provide alternative attack paths.

---

# WriteDACL

A principal with:

```text
WriteDACL
```

may potentially modify the gMSA object's permissions.

Conceptually:

```text
Attacker
   |
   v
WriteDACL
   |
   v
Modify Permission
   |
   v
Gain Additional Control
```

The exact resulting capability should be validated carefully.

---

# WriteOwner

A principal with:

```text
WriteOwner
```

may be able to take ownership and subsequently alter the object's discretionary ACL under applicable Windows access-control rules.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# Principals Allowed to Retrieve

PowerShell provides a convenient representation through:

```text
PrincipalsAllowedToRetrieveManagedPassword
```

Example:

```powershell
Get-ADServiceAccount \
    -Identity 'WEB-SVC' \
    -Properties PrincipalsAllowedToRetrieveManagedPassword |
    Select-Object \
        Name,
        PrincipalsAllowedToRetrieveManagedPassword
```

---

# Expand Reader Groups

If the result contains:

```text
CORP\WEB-SERVERS
```

enumerate its membership:

```powershell
Get-ADGroupMember \
    -Identity 'WEB-SERVERS' \
    -Recursive
```

The effective access may be much broader than the first group name suggests.

---

# Reader Group Model

```text
gMSA
 |
 v
WEB-SERVERS
 |
 +--> WEB01$
 +--> WEB02$
 +--> ADMIN01$
```

If:

```text
ADMIN01$
```

should not host the service, its membership may unnecessarily expose the gMSA credential.

---

# Computer Accounts Can Be Attack Principals

Do not focus only on user accounts.

If:

```text
WEB01$
```

is authorised to retrieve:

```text
WEB-SVC$
```

then compromise of:

```text
WEB01
```

may provide a path to the gMSA.

Conceptually:

```text
Compromise WEB01
       |
       v
Control WEB01$
       |
       v
Retrieve WEB-SVC$
       |
       v
Use gMSA Privileges
```

---

# Why Computer Membership Matters

This is a key gMSA design characteristic.

The account needs to be usable by computers hosting the service.

Therefore:

```text
Authorised Computer
```

is effectively part of the credential trust boundary.

Protecting the gMSA therefore also requires protecting those computers.

---

# Trust Boundary

```text
gMSA
 |
 v
Authorised Computers
 |
 v
Security Boundary
```

If one authorised computer is compromised:

```text
Computer Compromise
       |
       v
Potential gMSA Credential Exposure
```

depending on local privileges and implementation.

---

# gMSA Password Retrieval

Actual retrieval of:

```text
msDS-ManagedPassword
```

is credential access.

Do not retrieve it merely to prove that a gMSA exists.

Prefer:

```text
ACL Evidence
+
Reader Membership
+
BloodHound Relationship
```

where sufficient.

---

# LDAP Retrieval Concept

An authorised principal may be able to request:

```text
msDS-ManagedPassword
```

through LDAP.

Conceptually:

```text
LDAP Query
    |
    v
gMSA Object
    |
    v
msDS-ManagedPassword
```

If the caller lacks the necessary access, the sensitive attribute should not be available.

---

# Linux Tooling

Common tools used during authorised gMSA assessment may include:

```text
ldapsearch
BloodHound.py
NetExec
bloodyAD
Impacket
gMSADumper
```

Tool support and syntax can change.

Always verify the installed version before use.

---

# gMSADumper

A commonly used open-source utility for gMSA assessment is:

```text
gMSADumper
```

It can enumerate and retrieve gMSA password information where the supplied identity has the necessary permissions.

Before using:

```bash
python3 gMSADumper.py -h
```

or follow the current project documentation.

Because this tool retrieves credential material, use it only when:

```text
Credential Retrieval Is Authorised
```

---

# NetExec

NetExec versions may provide LDAP modules or functionality related to gMSA enumeration.

Check:

```bash
nxc ldap --help
```

and:

```bash
nxc ldap -L
```

before relying on module names from older NetExec or CrackMapExec documentation.

See:

[NetExec](netexec.md)

---

# bloodyAD

bloodyAD can interact with Active Directory through LDAP and is useful for validating directory permissions.

Check:

```bash
bloodyAD --help
```

and the current project documentation before using version-specific syntax.

Prefer read-only enumeration until modification is specifically authorised.

---

# Impacket

Impacket becomes useful after credential material has been legitimately recovered because the resulting authentication material may be usable with standard Kerberos or NTLM tooling.

See:

[Impacket](impacket.md)

---

# Managed Password to NT Hash

The managed password can be used to derive authentication material.

Conceptually:

```text
gMSA Password
      |
      v
NT Hash
      |
      v
NTLM Authentication
```

This means:

```text
Read gMSA Password
```

can potentially become:

```text
Pass-the-Hash
```

where NTLM authentication and target configuration permit it.

See:

[Pass-the-Hash](pass-the-hash.md)

---

# Managed Password to Kerberos Key

The gMSA password can also correspond to Kerberos key material.

Conceptually:

```text
gMSA Password
      |
      v
Kerberos Keys
      |
      v
TGT
      |
      v
Kerberos Authentication
```

See:

[Pass-the-Key](pass-the-key.md)

---

# gMSA Credential Abuse Model

The complete model is:

```text
ReadGMSAPassword
       |
       v
Managed Password
       |
       +--> NT Hash
       |
       +--> Kerberos Keys
       |
       v
Authenticate as gMSA
```

---

# Authentication as gMSA

If credential material is recovered during an authorised test, determine whether authentication validation is actually necessary.

A safer sequence is:

```text
Retrieve
   |
   v
Parse Credential Material
   |
   v
Determine Privilege
   |
   v
Stop If Evidence Is Sufficient
```

Do not automatically proceed to:

```text
Remote Execution
```

---

# Kerberos Validation

Where permitted, requesting a Kerberos TGT can demonstrate that the recovered gMSA credential material is valid without executing commands on a remote server.

Conceptually:

```text
gMSA Key
   |
   v
AS-REQ
   |
   v
TGT
```

This can be less intrusive than remote service execution.

---

# gMSA Account Name

Remember that gMSA account names commonly end with:

```text
$
```

Example:

```text
WEB-SVC$
```

Some tools require the trailing `$` to be escaped or quoted by the shell.

For Bash:

```bash
'WEB-SVC$'
```

prevents shell variable interpretation.

---

# gMSA and Pass-the-Hash

Suppose an authorised assessment recovers an NT hash corresponding to:

```text
WEB-SVC$
```

If NTLM authentication is supported:

```text
WEB-SVC$
   |
   v
NT Hash
   |
   v
NTLM
```

may provide access according to the gMSA's privileges.

This is a normal consequence of credential compromise, not a separate weakness in gMSA itself.

---

# gMSA and Pass-the-Key

Kerberos key material may allow authentication without knowing a human-readable password.

Conceptually:

```text
ReadGMSAPassword
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

# gMSA and OverPass-the-Hash

Depending on available credential material and environment configuration, password-derived key material may also interact with Kerberos authentication techniques.

See:

[OverPass-the-Hash](overpass-the-hash.md)

---

# gMSA and Delegation

A gMSA may also participate in Kerberos delegation configurations.

Review:

```text
TrustedForDelegation
TrustedToAuthForDelegation
msDS-AllowedToDelegateTo
RBCD Relationships
```

where applicable.

A service account should not receive unnecessary delegation privileges.

---

# Unconstrained Delegation

If a gMSA is associated with an account configured for unconstrained delegation, this represents a separate high-risk Kerberos configuration.

See:

[Unconstrained Delegation](unconstrained-delegation.md)

---

# Constrained Delegation

Review:

```text
msDS-AllowedToDelegateTo
```

and relevant account flags.

See:

[Constrained Delegation](constrained-delegation.md)

---

# Resource-Based Constrained Delegation

RBCD is controlled from the target computer or service object's:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# S4U

Delegation attack paths involving service accounts may use:

```text
S4U2Self
S4U2Proxy
```

See:

[Kerberos S4U](s4u.md)

---

# gMSA and SPN Ownership

Because gMSAs frequently represent services, they commonly own SPNs.

Review:

```text
Which SPNs?
Which Servers?
Which Applications?
```

An unexpected SPN can indicate:

```text
Misconfiguration
Legacy Configuration
Service Migration
Duplicate SPN
```

---

# SPN Enumeration

```powershell
Get-ADServiceAccount \
    -Filter * \
    -Properties ServicePrincipalNames |
    ForEach-Object {
        [PSCustomObject]@{
            Account = $_.SamAccountName
            SPNs    = $_.ServicePrincipalNames -join '; '
        }
    }
```

---

# gMSA and Local Administrator Rights

A gMSA might be placed in:

```text
Local Administrators
```

on one or more servers.

This can create:

```text
ReadGMSAPassword
       |
       v
gMSA
       |
       v
Local Administrator
       |
       v
Server
```

BloodHound may help identify this relationship.

---

# Group Policy and gMSA

Group Policy can influence:

```text
Local Group Membership
User Rights Assignments
Service Configuration
Scheduled Tasks
```

Therefore a gMSA's effective privilege may come from:

```text
GPO
```

rather than direct domain group membership.

See:

[Active Directory Group Policy](group-policy.md)

---

# gMSA and Scheduled Tasks

gMSAs can be used with supported scheduled tasks.

The security model is:

```text
Scheduled Task
      |
      v
gMSA
      |
      v
Domain Resources
```

Review what the task executes and where the account can authenticate.

---

# gMSA and Services

A common deployment is:

```text
Windows Service
      |
      v
gMSA
```

The gMSA may require:

```text
Log on as a service
```

and access to application resources.

Do not grant local administrator rights merely because an account runs a service.

---

# gMSA and IIS

gMSAs can be used for application pools or web applications where supported.

The account may consequently have access to:

```text
Web Application Files
Databases
Network Shares
Certificates
Application Secrets
```

This should be included in impact analysis.

---

# gMSA and SQL Server

A SQL Server service may use a gMSA.

Potential privileges include:

```text
SQL Service Access
Database Files
Network Shares
SPNs
Backup Locations
Service Resources
```

Do not automatically assume:

```text
SQL gMSA = Domain Admin
```

Analyse actual rights.

---

# gMSA and Backup Systems

Backup service identities deserve particular attention.

They may have:

```text
Read Access to Sensitive Servers
Backup Operator Rights
Access to Backup Repositories
Application Credentials
Domain Controller Backup Access
```

Therefore:

```text
ReadGMSAPassword
       |
       v
Backup gMSA
```

can be a high-impact relationship.

---

# gMSA and AD CS

A gMSA may have permissions related to:

```text
Certificate Enrollment
Certificate Templates
Certification Authorities
```

If so, compromise of the gMSA may expose an AD CS attack path.

A dedicated AD CS section should analyse these relationships separately.

---

# gMSA and Directory Replication

If a gMSA has replication rights such as those required for DCSync:

```text
ReadGMSAPassword
       |
       v
gMSA
       |
       v
Replication Rights
       |
       v
Domain Credential Exposure
```

This could represent a critical attack path.

Do not rely solely on group membership.

Inspect ACL-derived replication rights.

---

# gMSA and DCSync

Relevant replication rights commonly include:

```text
Replicating Directory Changes
Replicating Directory Changes All
```

and, depending on the operation:

```text
Replicating Directory Changes In Filtered Set
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

A dedicated NTDS/DCSync page should cover the technique in depth.

---

# gMSA and Shadow Credentials

If an attacker has sufficient control over a gMSA object to modify:

```text
msDS-KeyCredentialLink
```

a Shadow Credentials path may exist independently of managed-password retrieval.

Conceptually:

```text
Control gMSA Object
       |
       v
Write Key Credential
       |
       v
Alternative Authentication
```

A dedicated page should cover:

```text
active-directory/shadow-credentials.md
```

---

# gMSA and Password Reset

Do not attempt to manually reset a gMSA password using normal user-account procedures.

The password lifecycle is managed by Active Directory.

Administrative changes should use supported gMSA management mechanisms.

---

# gMSA Installation on a Host

Administrators can install a gMSA on an authorised computer using:

```powershell
Install-ADServiceAccount \
    -Identity 'WEB-SVC'
```

This is an administrative change.

Do not perform it during a penetration test unless explicitly authorised.

---

# Test-ADServiceAccount

Administrators can test whether a managed service account is usable on the current computer:

```powershell
Test-ADServiceAccount \
    -Identity 'WEB-SVC'
```

A successful result generally indicates that the local system can use the account.

This can be useful during administrative troubleshooting.

---

# Remove-ADServiceAccount

Administrators can remove a managed service account from a computer using:

```powershell
Uninstall-ADServiceAccount \
    -Identity 'WEB-SVC'
```

Do not perform configuration changes during an assessment.

---

# Safe Validation Strategy

Use the following hierarchy:

```text
Level 1
Enumerate gMSA Objects

Level 2
Enumerate SPNs and Group Membership

Level 3
Enumerate Password Retrieval Principals

Level 4
Validate ACL / Security Descriptor

Level 5
Determine gMSA Privilege

Level 6
Retrieve Credential Material

Level 7
Authenticate as gMSA

Level 8
Use Resulting Privilege
```

Stop at the lowest level that demonstrates the issue.

---

# Example Safe Validation

Suppose:

```text
CORP\alice
```

is unexpectedly able to retrieve:

```text
BACKUP-SVC$
```

The assessment can proceed:

```text
Confirm Alice's Permission
        |
        v
Determine BACKUP-SVC$ Privilege
        |
        v
Document ReadGMSAPassword Path
        |
        v
Retrieve Credential Only If Required
        |
        v
Perform Single Controlled Validation
        |
        v
Stop
```

---

# Avoid Broad Credential Collection

Do not:

```text
Dump Every gMSA Password
```

when:

```text
ACL Evidence
```

already demonstrates excessive access.

Credential minimisation is especially important because gMSAs may have significant service privileges.

---

# Detection

gMSA monitoring should focus on:

```text
Password Retrieval
Directory ACL Changes
Reader Group Changes
gMSA Object Changes
Unexpected Authentication
Kerberos Activity
NTLM Activity
Service Configuration Changes
```

---

# Directory Service Access

Access to sensitive gMSA attributes can potentially be monitored using directory service auditing.

Relevant event:

```text
4662
```

when appropriate SACL and audit policy configuration exists.

---

# Event 4662

Event:

```text
4662
```

records operations performed on Active Directory objects where auditing is configured.

Potentially useful fields include:

```text
Subject
Object
Operation
Properties
Access Mask
```

Detecting gMSA password retrieval requires appropriate auditing configuration and understanding of the relevant property identifiers.

---

# Directory Object Changes

Changes to gMSA configuration may generate:

```text
5136
```

where Directory Service Changes auditing is enabled.

Monitor changes to:

```text
msDS-GroupMSAMembership
servicePrincipalName
memberOf
Delegation Attributes
Other Sensitive gMSA Properties
```

---

# Group Membership Monitoring

If retrieval permission is delegated through groups, monitor membership changes.

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

---

# Authentication Monitoring

After gMSA credential compromise, activity may appear through:

```text
4624
4625
4768
4769
4771
4776
```

depending on:

```text
Kerberos
NTLM
Success
Failure
```

---

# Kerberos Events

Because gMSAs commonly use Kerberos, monitor:

```text
4768
4769
```

for unusual authentication patterns.

Examples:

```text
gMSA authenticating from unexpected host
gMSA requesting unusual service tickets
gMSA used interactively
gMSA authenticating outside expected server set
```

---

# Expected Host Baseline

One of the strongest detection models is:

```text
gMSA
 |
 v
Expected Hosts
```

For example:

```text
WEB-SVC$
 |
 +--> WEB01
 +--> WEB02
```

If authentication appears from:

```text
WORKSTATION37
```

this should be investigated.

---

# Interactive Logon

gMSAs are intended for managed service scenarios.

Unexpected:

```text
Interactive Logon
Remote Interactive Logon
Administrative Shell Activity
```

using a gMSA should receive additional scrutiny.

---

# Service Baseline

Record:

```text
gMSA
Service
Expected Hosts
Expected SPNs
Expected Network Destinations
```

This allows defenders to detect deviations.

---

# Detect Password Reader Changes

Monitor modifications to:

```text
PrincipalsAllowedToRetrieveManagedPassword
```

or the underlying:

```text
msDS-GroupMSAMembership
```

security descriptor.

An attacker who gains object-control permissions may attempt to broaden the retrieval scope.

---

# Detection Model

```text
Attacker
   |
   v
Gain Directory Permission
   |
   v
Access gMSA Password
   |
   v
Authenticate as gMSA
   |
   v
Access Service / Server
```

Detection should attempt to correlate these stages.

---

# Hardening

A strong gMSA deployment follows:

```text
Use gMSA
   |
   v
Restrict Retrieval
   |
   v
Restrict Service Privilege
   |
   v
Restrict Host Scope
   |
   v
Monitor Authentication
   |
   v
Monitor Directory Changes
```

---

# Prefer gMSA over Static Service Accounts

Where supported:

```text
Traditional Service Account
        |
        v
Static Human-Managed Password
```

should be replaced by:

```text
gMSA
 |
 v
Automatically Managed Password
```

This reduces:

```text
Password Reuse
Password Sharing
PasswordNeverExpires
Manual Rotation
Secret Storage
```

---

# Restrict Retrieval Principals

Avoid broad groups such as:

```text
Domain Users
Domain Computers
Authenticated Users
Large Operations Groups
```

unless there is a specifically justified architectural requirement.

Prefer dedicated groups containing only the systems that run the service.

---

# Dedicated Host Group

Example:

```text
WEB-SVC-HOSTS
      |
      +--> WEB01$
      +--> WEB02$
```

then:

```text
WEB-SVC-HOSTS
      |
      v
Can Retrieve WEB-SVC$
```

---

# Avoid User Accounts as Readers

Normally, computers running the service require access to the managed password.

Human user accounts should not generally need direct gMSA password retrieval.

If users appear in:

```text
PrincipalsAllowedToRetrieveManagedPassword
```

investigate why.

---

# Least Privilege for the gMSA

The gMSA itself should receive only the rights necessary for the service.

Avoid:

```text
Domain Admin
Local Admin Everywhere
Broad Share Access
Broad Database Access
Unnecessary Delegation
Directory Replication Rights
```

---

# Separate gMSAs

Avoid using one gMSA for unrelated applications.

Poor model:

```text
GLOBAL-SVC$
   |
   +--> SQL
   +--> IIS
   +--> Backup
   +--> Monitoring
```

Prefer:

```text
SQL-SVC$
WEB-SVC$
BACKUP-SVC$
MONITOR-SVC$
```

where operationally appropriate.

This reduces blast radius.

---

# Protect Authorised Hosts

Because authorised hosts can legitimately use the gMSA:

```text
Protect gMSA
      =
Protect Authorised Hosts
```

Apply appropriate:

```text
Patching
EDR
Administrative Tiering
Credential Guard
Application Control
Least Privilege
```

to those systems.

---

# Tiering

A Tier 0 gMSA should only be retrievable by:

```text
Tier 0 Systems
```

and managed by:

```text
Tier 0 Administrators
```

Avoid:

```text
Tier 1 Server
     |
     v
Retrieve Tier 0 gMSA
```

---

# Review Nested Groups

A narrow-looking reader group may hide broad access.

Example:

```text
GMSA-Readers
     |
     v
Server-Admins
     |
     v
Legacy-Operations
     |
     v
Large User Population
```

Always resolve nested membership.

---

# Review SPNs

Remove:

```text
Stale SPNs
Duplicate SPNs
Legacy SPNs
```

where appropriate.

Incorrect SPNs can cause:

```text
Kerberos Authentication Problems
Unexpected Service Mapping
Operational Confusion
```

---

# Review Unused gMSAs

Identify gMSAs that:

```text
Have No Active Service
Have No Recent Use
Reference Decommissioned Servers
Have Stale SPNs
Have Obsolete Reader Groups
```

Remove unused accounts through approved change-management procedures.

---

# Review Privileged gMSAs

Prioritise accounts with:

```text
Privileged Group Membership
Local Administrator Rights
Backup Access
Virtualisation Access
Certificate Infrastructure Access
Directory Replication Rights
Management Platform Access
Delegation Configuration
```

---

# Incident Response

If unauthorised gMSA password retrieval is suspected:

```text
Identify gMSA
      |
      v
Identify Reader
      |
      v
Identify Authorised Hosts
      |
      v
Review Authentication
      |
      v
Review Service Access
      |
      v
Review Directory Changes
      |
      v
Rotate / Recover as Required
      |
      v
Remove Excessive Permission
```

---

# Determine Exposure

Ask:

```text
Who could retrieve the password?

Who actually retrieved it?

Which hosts could legitimately retrieve it?

Where was the gMSA used?

What resources can the gMSA access?

Did authentication originate from an unexpected host?
```

---

# Investigate Authentication

Review:

```text
4624
4625
4768
4769
4771
4776
```

and relevant EDR/network telemetry.

Look for:

```text
Unexpected Source Hosts
Unexpected Services
Interactive Usage
New Remote Administration
Unusual Authentication Times
```

---

# Investigate Downstream Access

If the gMSA is privileged, investigate:

```text
Servers Accessed
Shares Accessed
Databases Accessed
Administrative Tools
Scheduled Tasks
Service Creation
Directory Modifications
Certificate Requests
```

---

# Rotate Credentials

gMSA password lifecycle is managed automatically.

Use supported administrative procedures if an emergency password change or account recovery is required.

Do not attempt to manually assign a static password.

---

# Review Reader ACL

After an incident:

```text
msDS-GroupMSAMembership
```

and the object's normal ACL should be reviewed for unauthorised modifications.

---

# Purple Team Exercise

A controlled gMSA exercise can test:

```text
ReadGMSAPassword Detection
Authentication Detection
Unexpected Host Detection
Privilege Escalation Analysis
```

Prefer a dedicated lab or test gMSA.

---

# Purple Team Model

```text
Test User
   |
   v
Controlled ReadGMSAPassword Permission
   |
   v
Test gMSA
   |
   v
Controlled Authentication
   |
   v
Detection
```

---

# Purple Team Questions

Defenders should be able to answer:

```text
Which principal retrieved the password?

Which gMSA was accessed?

From which system?

Was the principal authorised?

Where should the gMSA normally authenticate?

Where did it authenticate?

What privileges does it have?

Was its retrieval permission modified?

Was downstream access detected?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect gMSA retrieval
Time to identify source principal
Time to identify affected gMSA
Time to identify expected hosts
Time to detect unexpected authentication
Time to determine gMSA privileges
Time to contain access
```

---

# Reporting

Possible finding titles include:

```text
Low-Privilege User Can Retrieve gMSA Password
```

```text
Excessive gMSA Password Retrieval Permissions
```

```text
Domain Computers Can Retrieve Privileged gMSA Credential
```

```text
gMSA Retrieval Permission Creates Privilege Escalation Path
```

```text
Privileged gMSA Can Be Retrieved by Non-Privileged Systems
```

```text
gMSA Has Excessive Domain Privileges
```

---

# Example Finding - ReadGMSAPassword

```text
Finding:
Low-Privilege Principal Can Retrieve Privileged gMSA Credential

Source Principal:
CORP\alice

Target:
CORP\BACKUP-SVC$

Description:
The CORP\alice account has effective permission to retrieve the managed
password associated with the BACKUP-SVC$ group Managed Service Account.

The permission was confirmed through Active Directory security
descriptor analysis.

BACKUP-SVC$ is used by the organisation's backup infrastructure and has
access to multiple sensitive servers.

During the authorised assessment, the permission relationship was
validated without broadly retrieving additional gMSA credentials.

Impact:
Compromise of CORP\alice could allow an attacker to obtain credential
material for BACKUP-SVC$ and authenticate using the service account's
identity.

The resulting access may include resources available to the backup
service and could provide a path to additional privileged systems.

Recommendation:
Remove the unnecessary managed-password retrieval permission.

Restrict gMSA password retrieval to the minimum set of computer
accounts that legitimately host the associated service.

Review nested group membership and the privileges assigned to
BACKUP-SVC$.

Monitor gMSA authentication for activity originating from systems
outside the expected service-host set.
```

---

# Example Finding - Broad Computer Access

```text
Finding:
Broad Computer Group Can Retrieve Privileged gMSA Password

Target:
CORP\SQL-SVC$

Reader:
CORP\Domain Computers

Description:
The SQL-SVC$ gMSA permits a broad computer population to retrieve its
managed password.

Only a small number of SQL servers require the credential.

Impact:
Compromise of any authorised computer account may provide a path to
SQL-SVC$ credential material.

This unnecessarily expands the trust boundary of the service account
and increases the impact of endpoint compromise.

Recommendation:
Create a dedicated security group containing only the computer accounts
that legitimately host the SQL service.

Configure SQL-SVC$ so that only this group can retrieve its managed
password.

Review historical authentication for SQL-SVC$ from unexpected systems.
```

---

# Example Finding - Excessive gMSA Privilege

```text
Finding:
Group Managed Service Account Has Excessive Domain Privileges

Account:
CORP\APP-SVC$

Description:
APP-SVC$ is used by an application service but has been assigned
privileges substantially beyond those required for the application's
documented function.

The account is retrievable by multiple application servers.

Impact:
Compromise of any system authorised to use APP-SVC$ could expose a
highly privileged domain identity.

The excessive rights increase the impact of compromise of both the
service account and every computer authorised to retrieve its managed
password.

Recommendation:
Review the application's actual access requirements and remove
unnecessary group memberships, delegated rights, local administrator
permissions, and directory permissions.

Maintain separate gMSAs for services with different privilege
requirements.
```

---

# Severity

Severity depends on:

```text
Who Can Retrieve
      +
gMSA Privilege
      +
Authorised Host Scope
      +
Accessible Resources
      +
Downstream Attack Paths
      =
Risk
```

Example:

```text
Application Server
      |
      v
Read Low-Privilege gMSA
      |
      v
Single Application
```

may represent moderate exposure.

Compare:

```text
Low-Privilege User
       |
       v
ReadGMSAPassword
       |
       v
Privileged Backup gMSA
       |
       v
Domain Controller Backup Access
```

which can represent a severe attack path.

---

# Do Not Overstate gMSA Findings

Finding:

```text
Alice Can Read WEB-SVC$
```

does not automatically mean:

```text
Alice Is Domain Admin
```

The correct analysis is:

```text
Alice
 |
 v
WEB-SVC$
 |
 v
What Can WEB-SVC$ Access?
```

The privilege of the target identity determines the downstream impact.

---

# Evidence Checklist

Record:

```text
Domain
gMSA Name
gMSA SID
Distinguished Name
SPNs
Managed Password Interval
Reader Principal
Reader SID
Reader Group
Nested Membership
msDS-GroupMSAMembership
Relevant ACLs
Group Membership
Local Administrator Rights
Delegation Configuration
Directory Rights
Expected Service Hosts
Credential Retrieved?
Authentication Validated?
Resulting Access
Relevant Events
Cleanup
```

Do not record reusable credential material in ordinary report evidence.

---

# gMSA Assessment Checklist

## Preparation

- [ ] Confirm gMSA enumeration is authorised
- [ ] Confirm credential retrieval restrictions
- [ ] Confirm authentication testing restrictions
- [ ] Confirm Tier 0 restrictions
- [ ] Prepare secure evidence storage
- [ ] Define credential redaction procedure

## Discovery

- [ ] Enumerate gMSA objects
- [ ] Enumerate sMSAs where relevant
- [ ] Record distinguished names
- [ ] Record account SIDs
- [ ] Record SPNs
- [ ] Record password intervals
- [ ] Identify service purpose
- [ ] Identify expected service hosts

## Password Retrieval Permissions

- [ ] Review `msDS-GroupMSAMembership`
- [ ] Review `PrincipalsAllowedToRetrieveManagedPassword`
- [ ] Identify direct readers
- [ ] Identify reader groups
- [ ] Expand nested groups
- [ ] Identify computer readers
- [ ] Identify user readers
- [ ] Identify unexpectedly broad groups
- [ ] Identify cross-tier access

## Object ACL

- [ ] Review owner
- [ ] Review GenericAll
- [ ] Review GenericWrite
- [ ] Review WriteDACL
- [ ] Review WriteOwner
- [ ] Review WriteProperty
- [ ] Review inherited ACEs
- [ ] Review explicit ACEs

## Privilege Analysis

- [ ] Review domain group membership
- [ ] Review nested groups
- [ ] Review local administrator rights
- [ ] Review GPO-derived rights
- [ ] Review service permissions
- [ ] Review share access
- [ ] Review database access
- [ ] Review backup access
- [ ] Review AD CS access
- [ ] Review replication rights
- [ ] Review delegation configuration

## Kerberos

- [ ] Enumerate SPNs
- [ ] Review unconstrained delegation
- [ ] Review constrained delegation
- [ ] Review RBCD
- [ ] Review S4U relationships
- [ ] Review expected Kerberos services
- [ ] Do not report normal gMSA SPNs as weak Kerberoasting

## BloodHound

- [ ] Identify `ReadGMSAPassword`
- [ ] Identify paths from owned principals
- [ ] Identify paths to high-value gMSAs
- [ ] Identify downstream paths from gMSA
- [ ] Validate graph relationships
- [ ] Review expected service hosts

## Validation

- [ ] Prefer permission evidence
- [ ] Retrieve credential only if necessary
- [ ] Use dedicated test account where possible
- [ ] Avoid dumping all gMSA passwords
- [ ] Avoid unnecessary authentication
- [ ] Prefer controlled validation
- [ ] Stop once impact is demonstrated
- [ ] Redact credential material

## Detection

- [ ] Review event 4662
- [ ] Review event 5136
- [ ] Monitor reader group changes
- [ ] Monitor gMSA object changes
- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Monitor 4771
- [ ] Monitor 4776
- [ ] Baseline expected source hosts
- [ ] Alert on unexpected gMSA authentication
- [ ] Review interactive gMSA usage

## Hardening

- [ ] Prefer gMSA over static service accounts
- [ ] Restrict password retrieval
- [ ] Use dedicated host groups
- [ ] Remove unnecessary user readers
- [ ] Remove broad reader groups
- [ ] Protect authorised hosts
- [ ] Apply administrative tiering
- [ ] Apply least privilege to gMSA
- [ ] Separate unrelated services
- [ ] Remove stale SPNs
- [ ] Remove unused gMSAs
- [ ] Review privileged gMSAs
- [ ] Monitor directory changes
- [ ] Monitor authentication

## Incident Response

- [ ] Identify affected gMSA
- [ ] Identify retrieval principal
- [ ] Identify expected hosts
- [ ] Identify actual authentication sources
- [ ] Review Kerberos activity
- [ ] Review NTLM activity
- [ ] Review downstream access
- [ ] Review directory changes
- [ ] Review reader permissions
- [ ] Remove unauthorised readers
- [ ] Use supported password recovery/rotation procedures
- [ ] Investigate authorised host compromise

## Cleanup

- [ ] Remove exported credential material
- [ ] Remove temporary Kerberos tickets
- [ ] Remove temporary credential caches
- [ ] Remove plaintext notes
- [ ] Secure retained evidence
- [ ] Confirm no gMSA configuration was changed
- [ ] Confirm no ACLs were changed
- [ ] Confirm no service configuration was changed

---

# gMSA Testing Model

The traditional service-account model is:

```text
Service
   |
   v
Domain User
   |
   v
Static Password
   |
   v
Administrator Manages Secret
```

The gMSA model is:

```text
Service
   |
   v
gMSA
   |
   v
Automatically Managed Password
   |
   v
Active Directory
```

The retrieval model is:

```text
gMSA
 |
 v
msDS-GroupMSAMembership
 |
 v
Authorised Principal
 |
 v
Managed Password
```

The trust-boundary model is:

```text
gMSA
 |
 +--> SERVER01$
 +--> SERVER02$
 |
 v
Every Authorised Host
Is Part of Credential Boundary
```

The attack model is:

```text
Compromised User / Computer
          |
          v
ReadGMSAPassword
          |
          v
gMSA Credential Material
          |
          v
Authenticate as gMSA
          |
          v
gMSA Privilege
```

The authentication model is:

```text
Managed Password
      |
      +--> NT Hash
      |
      +--> Kerberos Keys
      |
      v
Authentication
```

The privilege model is:

```text
ReadGMSAPassword
       |
       v
gMSA
       |
       +--> Groups
       +--> ACLs
       +--> Local Admin
       +--> Services
       +--> Shares
       +--> Databases
       +--> Delegation
       +--> AD CS
       +--> Replication Rights
```

The BloodHound model is:

```text
Owned Principal
      |
      v
ReadGMSAPassword
      |
      v
gMSA
      |
      v
Attack Path
      |
      v
High-Value Target
```

The host-compromise model is:

```text
Compromise Authorised Host
          |
          v
Control Computer Context
          |
          v
Potential gMSA Retrieval
          |
          v
Service Identity Compromise
```

The defensive model is:

```text
gMSA
 |
 v
Dedicated Service
 |
 v
Dedicated Host Group
 |
 v
Minimal Retrieval Scope
 |
 v
Least Privilege
 |
 v
Expected Authentication Hosts
 |
 v
Monitoring
```

The safe testing model is:

```text
Enumerate
   |
   v
Identify Readers
   |
   v
Identify gMSA Privilege
   |
   v
Validate Permission
   |
   v
Retrieve Only If Required
   |
   v
Authenticate Only If Required
   |
   v
Stop
```

The most important distinction is:

```text
gMSA Uses Strong Managed Password
          |
          X
gMSA Cannot Be Compromised
```

The stronger model is:

```text
Strong Managed Password
        +
Weak Retrieval Permission
        =
Credential Exposure
```

Another important distinction is:

```text
gMSA Has SPN
     |
     X
Weak Kerberoasting Target
```

because:

```text
gMSA
 |
 v
Long Random Managed Password
 |
 v
Offline Password Guessing Generally Impractical
```

Instead, the more relevant question is:

```text
Who Can Retrieve the Managed Password?
```

For penetration testers:

```text
Do Not Ask:
"Can I dump every gMSA?"

Ask:
"Which compromised principals can retrieve which gMSAs,
and what privilege would those identities provide?"
```

For defenders:

```text
Do Not Ask:
"Are we using gMSAs?"

Ask:
"Which systems can retrieve each gMSA,
are those systems appropriately trusted,
and what happens if one is compromised?"
```

The final model is:

```text
Principal
   |
   v
Password Retrieval Permission
   |
   v
gMSA
   |
   v
Privileges
   |
   v
Reachable Systems
```

The security of a gMSA therefore depends not only on its automatically generated password, but also on the identities and computers trusted to retrieve that password and the privileges granted to the service account.

---

# Related Notes

Credential Access:

[Active Directory Credential Access](credential-access.md)

LAPS:

[Active Directory LAPS](laps.md)

Group Policy Preferences Passwords:

`Group Policy Preferences Passwords`

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Groups:

[Active Directory Groups](groups.md)

Group Policy:

[Active Directory Group Policy](group-policy.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

OverPass-the-Hash:

[OverPass-the-Hash](overpass-the-hash.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

Constrained Delegation:

[Constrained Delegation](constrained-delegation.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[Kerberos S4U](s4u.md)

BloodHound:

[BloodHound](bloodhound.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

The next Credential Access topics include:

```text
active-directory/shadow-credentials.md
active-directory/ntds.md
```

---

# References

## Microsoft - Group Managed Service Accounts

[Microsoft - Group Managed Service Accounts Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Create a Group Managed Service Account](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/create-the-key-distribution-services-kds-root-key){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Managed Service Accounts

[Microsoft - Get-ADServiceAccount](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adserviceaccount){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Install-ADServiceAccount](https://learn.microsoft.com/en-us/powershell/module/activedirectory/install-adserviceaccount){ target="_blank" rel="noopener noreferrer" }

[Test-ADServiceAccount](https://learn.microsoft.com/en-us/powershell/module/activedirectory/test-adserviceaccount){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - gMSA Schema

[Microsoft - msDS-ManagedPassword](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-ada2/72e57e8d-9a2a-479b-96b0-4b9eaa6ca729){ target="_blank" rel="noopener noreferrer" }

[Microsoft - msDS-GroupMSAMembership](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-groupmsamembership){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Managed Password Protocol

[Microsoft - MS-ADTS: Group Managed Service Accounts](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## PowerSploit

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - OS Credential Dumping](https://attack.mitre.org/techniques/T1003/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Group Managed Service Accounts solve one of the most persistent Windows service-account problems:

```text
Long-Lived Static Passwords
```

The traditional model is:

```text
Service Account
      |
      v
Human-Managed Password
      |
      v
Password Never Expires
      |
      v
Credential Exposure Risk
```

The gMSA model is:

```text
Service
   |
   v
gMSA
   |
   v
Automatically Managed Password
   |
   v
Automatic Rotation
```

This provides substantial security benefits.

However:

```text
Strong Password
```

does not solve:

```text
Weak Authorization
```

The central gMSA security relationship is:

```text
Principal
   |
   v
Can Retrieve Managed Password
   |
   v
gMSA
```

If that relationship is overly broad:

```text
Low-Privilege Principal
        |
        v
ReadGMSAPassword
        |
        v
Privileged gMSA
```

the automatically generated password does not prevent compromise.

The assessment should therefore examine:

```text
gMSA
 |
 +--> Password Retrieval Permissions
 |
 +--> Authorised Computers
 |
 +--> Nested Reader Groups
 |
 +--> SPNs
 |
 +--> Group Membership
 |
 +--> ACLs
 |
 +--> Local Administrator Rights
 |
 +--> Delegation
 |
 +--> Application Permissions
 |
 +--> Directory Rights
```

A particularly important relationship is:

```text
Authorised Computer
       |
       v
Can Retrieve gMSA
```

because every authorised computer becomes part of the gMSA trust boundary.

Therefore:

```text
Compromise Authorised Host
          |
          v
Potential gMSA Compromise
```

must be considered during attack-path analysis.

For Kerberoasting, remember:

```text
gMSA Has SPN
```

does not automatically mean:

```text
Useful Kerberoasting Target
```

because gMSA passwords are generated and managed specifically to avoid the weak human-password problem associated with traditional service accounts.

The more relevant attack path is usually:

```text
ReadGMSAPassword
```

rather than:

```text
Crack Service Ticket
```

For authorised testing, follow:

```text
Enumerate
   |
   v
Analyse Retrieval Permissions
   |
   v
Determine gMSA Privilege
   |
   v
Validate Permission
   |
   v
Retrieve Credential Only If Necessary
   |
   v
Stop When Impact Is Demonstrated
```

For defenders:

```text
Use gMSA
   |
   v
Restrict Readers
   |
   v
Restrict Authorised Hosts
   |
   v
Apply Least Privilege
   |
   v
Monitor Authentication
   |
   v
Monitor Directory Changes
```

The final question should always be:

```text
If this principal or authorised computer is compromised,
which gMSA credentials become available,
and what can those gMSAs access?
```

That is the relationship that determines the real security impact of a gMSA configuration.
