# Microsoft Configuration Manager - SCCM

Microsoft Configuration Manager is an enterprise endpoint-management platform used to deploy software, operating systems, updates, configuration and administrative actions across Windows environments.

The product has historically been known as:

```text
Systems Management Server
        |
        v
System Center Configuration Manager
        |
        v
Microsoft Endpoint Configuration Manager
        |
        v
Microsoft Configuration Manager
```

The abbreviation:

```text
SCCM
```

remains widely used in security tooling and documentation.

Configuration Manager is especially important during Active Directory security assessments because it may manage:

```text
Workstations
Servers
Administrative Systems
Applications
Operating System Deployment
Software Packages
Configuration
Scripts
```

An SCCM hierarchy can therefore represent a highly privileged management plane.

A simplified security model is:

```text
Active Directory
      |
      v
Configuration Manager
      |
      +--> Site Server
      +--> Site Database
      +--> Management Points
      +--> Distribution Points
      +--> Clients
      |
      v
Managed Windows Estate
```

A compromise of sufficiently privileged Configuration Manager infrastructure can have consequences far beyond the SCCM server itself.

!!! warning "Authorised testing only"
    Configuration Manager can deploy applications, scripts and configuration to large numbers of systems. Do not create deployments, modify collections, alter task sequences, change client settings or execute CMPivot queries against production systems unless explicitly authorised. Prefer read-only discovery and configuration review.

---

# Why SCCM Matters

Traditional Active Directory assessment often focuses on:

```text
Domain Admins
Enterprise Admins
Domain Controllers
Kerberos
NTLM
ACLs
Delegation
AD CS
```

However, enterprise management platforms can create additional paths to privileged systems.

Conceptually:

```text
SCCM Administrator
        |
        v
Configuration Manager
        |
        v
Managed Device
        |
        v
Privileged System
```

If Configuration Manager manages a domain controller or another Tier 0 system, control of the relevant SCCM administrative path can become extremely security sensitive.

---

# SCCM Is Not Automatically a Vulnerability

The presence of Configuration Manager is not a security finding.

Do not report:

```text
SCCM Is Installed
```

as a vulnerability.

The assessment should instead determine:

```text
Who Controls SCCM?
Which Systems Does SCCM Control?
Which Credentials Does SCCM Use?
How Are Clients Authenticated?
Which Roles Are Exposed?
Which Accounts Are Overprivileged?
Which SCCM Components Reach Tier 0?
Are Known SCCM Misconfigurations Present?
```

---

# Core Architecture

A simplified Configuration Manager architecture is:

```text
                    Active Directory
                          |
                          v
                    SCCM Hierarchy
                          |
              +-----------+-----------+
              |                       |
              v                       v
         Site Server              Site Database
              |
      +-------+-------+
      |               |
      v               v
Management Point   Distribution Point
      |               |
      +-------+-------+
              |
              v
           Clients
```

Larger environments can contain:

```text
Central Administration Site
Primary Sites
Secondary Sites
Multiple Management Points
Multiple Distribution Points
Remote Site Databases
Cloud Management Components
```

---

# SCCM Hierarchy

A Configuration Manager hierarchy consists of one or more sites.

Common site types include:

```text
Central Administration Site - CAS
Primary Site
Secondary Site
```

---

# Central Administration Site

A Central Administration Site can be used in large hierarchies containing multiple primary sites.

Conceptually:

```text
CAS
 |
 +--> Primary Site A
 |
 +--> Primary Site B
 |
 +--> Primary Site C
```

A CAS does not directly manage clients in the same way as a primary site.

---

# Primary Site

The primary site is a major administrative and management component.

It can contain or interact with:

```text
Management Points
Distribution Points
Site Database
Clients
Collections
Applications
Packages
Task Sequences
```

---

# Secondary Site

Secondary sites can support management of remote locations.

They operate beneath a primary site.

Conceptually:

```text
Primary Site
     |
     v
Secondary Site
     |
     v
Remote Clients
```

---

# Site Code

Each Configuration Manager site has a three-character site code.

Example:

```text
ABC
```

or:

```text
PR1
```

The site code appears throughout:

```text
Active Directory
Registry
WMI
Logs
Database
Configuration Manager Console
```

Discovering the site code is useful during enumeration.

---

# Site Server

The site server hosts core Configuration Manager functionality.

Example:

```text
SCCM01.corp.example
```

Depending on the architecture, additional roles may be installed on the same or separate systems.

---

# Site Database

Configuration Manager stores significant configuration and management information in SQL Server.

Conceptually:

```text
SCCM
 |
 v
SQL Server
 |
 v
Site Database
```

The database may reside:

```text
Locally on Site Server
```

or:

```text
Remote SQL Server
```

A remote site database creates additional network and authentication relationships that should be assessed carefully.

---

# Management Point

A Management Point, commonly abbreviated:

```text
MP
```

provides policy and management information to Configuration Manager clients.

Conceptually:

```text
Client
  |
  v
Management Point
  |
  v
Site
```

Management Points are particularly important during SCCM security assessments because they are client-facing site-system roles.

---

# Distribution Point

A Distribution Point, commonly abbreviated:

```text
DP
```

provides content to clients.

Content can include:

```text
Applications
Packages
Operating System Images
Boot Images
Software Updates
Task Sequence Content
```

Conceptually:

```text
Site
 |
 v
Distribution Point
 |
 v
Client
```

---

# Software Update Point

A Software Update Point integrates Configuration Manager with software-update infrastructure.

It is commonly associated with:

```text
WSUS
```

See the planned page:

```text
docs/active-directory/wsus.md
```

---

# Reporting Services Point

Configuration Manager can integrate with SQL Server Reporting Services.

This can provide reporting capabilities for SCCM administrators.

The role should be included when mapping:

```text
Administrative Interfaces
Service Accounts
SQL Relationships
```

---

# PXE-Enabled Distribution Points

Distribution Points can provide:

```text
PXE
```

services for operating-system deployment.

Conceptually:

```text
New Device
   |
   v
PXE
   |
   v
Distribution Point
   |
   v
Boot Image
   |
   v
Task Sequence
   |
   v
Operating System
```

PXE configuration can introduce additional credential and deployment-security considerations.

---

# Configuration Manager Client

Managed endpoints typically run the Configuration Manager client.

The client communicates with site-system roles to obtain:

```text
Policy
Applications
Packages
Configuration
Inventory Instructions
```

---

# SCCM Client Service

A commonly encountered Windows service is:

```text
CcmExec
```

Display name:

```text
SMS Agent Host
```

Check:

```powershell
Get-Service -Name CcmExec -ErrorAction SilentlyContinue
```

---

# Client Installation Directory

A commonly encountered directory is:

```text
C:\Windows\CCM
```

Other SCCM-related locations may include:

```text
C:\Windows\CCMSetup
C:\Windows\CCMCache
```

The exact paths can vary with configuration.

---

# CCMCache

Configuration Manager clients cache deployment content locally.

A common location is:

```text
C:\Windows\CCMCache
```

The cache may contain:

```text
Installers
Scripts
Configuration Files
Deployment Content
```

Do not assume cached files contain credentials.

Review them only where local file access is authorised.

---

# SCCM and Active Directory

Configuration Manager can publish information into Active Directory.

A particularly important location is:

```text
CN=System Management,CN=System,DC=corp,DC=example
```

This container can contain SCCM-related objects that assist clients and administrators in discovering site infrastructure.

---

# System Management Container

Conceptually:

```text
Active Directory
      |
      v
CN=System
      |
      v
CN=System Management
      |
      +--> Site Information
      +--> Management Points
      +--> SCCM Service Information
```

This container is a useful source for read-only SCCM discovery.

---

# LDAP Enumeration

A domain-authenticated user may be able to query published Configuration Manager objects through LDAP.

First determine the domain naming context:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -s base \
  -b '' \
  defaultNamingContext
```

Example:

```text
defaultNamingContext: DC=corp,DC=example
```

---

# Enumerate System Management

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=System Management,CN=System,DC=corp,DC=example'
```

This can reveal published Configuration Manager infrastructure where the current identity has read access.

---

# SCCM LDAP Object Classes

Configuration Manager publishes several object classes in Active Directory.

Important examples include:

```text
mSSMSSite
mSMSManagementPoint
```

These can help identify:

```text
Site Codes
Management Points
SCCM Infrastructure
```

---

# Enumerate SCCM Sites

Example LDAP query:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=System Management,CN=System,DC=corp,DC=example' \
  '(objectClass=mSSMSSite)' \
  cn mSSMSSiteCode mSSMSSourceForest
```

Interesting attributes can include:

```text
mSSMSSiteCode
mSSMSSourceForest
```

---

# Enumerate Management Points

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=System Management,CN=System,DC=corp,DC=example' \
  '(objectClass=mSMSManagementPoint)' \
  dNSHostName mSSMSSiteCode
```

This can reveal:

```text
Management Point Hostname
Site Code
```

---

# PowerShell Active Directory Enumeration

If the Active Directory module is available:

```powershell
Get-ADObject -SearchBase 'CN=System Management,CN=System,DC=corp,DC=example' -LDAPFilter '(objectClass=*)' -Properties *
```

For a large environment, request only the attributes needed rather than every property.

---

# Search for Management Points

```powershell
Get-ADObject -SearchBase 'CN=System Management,CN=System,DC=corp,DC=example' -LDAPFilter '(objectClass=mSMSManagementPoint)' -Properties dNSHostName,mSSMSSiteCode |
    Select-Object Name,dNSHostName,mSSMSSiteCode
```

---

# Search for SCCM Sites

```powershell
Get-ADObject -SearchBase 'CN=System Management,CN=System,DC=corp,DC=example' -LDAPFilter '(objectClass=mSSMSSite)' -Properties mSSMSSiteCode,mSSMSSourceForest |
    Select-Object Name,mSSMSSiteCode,mSSMSSourceForest
```

---

# Search Computer Names

Naming conventions can reveal additional infrastructure.

Example:

```powershell
Get-ADComputer -Filter * |
    Where-Object {
        $_.Name -match 'SCCM|MECM|CONFIGMGR|CM'
    } |
    Select-Object Name,DNSHostName
```

Treat naming conventions only as leads.

A server named:

```text
SCCM01
```

is not proof that it currently hosts Configuration Manager.

---

# Search Groups

```powershell
Get-ADGroup -Filter * |
    Where-Object {
        $_.Name -match 'SCCM|MECM|CONFIGMGR'
    } |
    Select-Object Name,GroupScope,GroupCategory
```

This may identify:

```text
Administrative Groups
Deployment Groups
Service Groups
Legacy Groups
```

---

# Search Accounts

```powershell
Get-ADUser -Filter * -Properties Description |
    Where-Object {
        $_.SamAccountName -match 'SCCM|MECM|CM' -or
        $_.Description -match 'SCCM|Configuration Manager'
    } |
    Select-Object SamAccountName,Description
```

Again, naming is only an indicator.

---

# DNS Enumeration

SCCM infrastructure may also be discoverable through DNS.

Examples:

```bash
dig sccm.corp.example
```

```bash
dig configmgr.corp.example
```

Do not rely on guessed names alone.

See:

[Active Directory Integrated DNS](adidns.md)

---

# Local Client Discovery

If assessing a Windows endpoint, determine whether the Configuration Manager client is installed.

Check the service:

```powershell
Get-Service -Name CcmExec -ErrorAction SilentlyContinue
```

---

# Process Discovery

```powershell
Get-Process -Name CcmExec -ErrorAction SilentlyContinue
```

---

# Client Directory

```powershell
Test-Path 'C:\Windows\CCM'
```

---

# CCMSetup Directory

```powershell
Test-Path 'C:\Windows\CCMSetup'
```

---

# Client Cache

```powershell
Test-Path 'C:\Windows\CCMCache'
```

---

# Registry Enumeration

Configuration Manager information can be present beneath:

```text
HKLM\SOFTWARE\Microsoft\CCM
HKLM\SOFTWARE\Microsoft\SMS
```

Availability depends on the role and system.

Read-only query:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\CCM' -ErrorAction SilentlyContinue
```

---

# Client Site Code

A client may expose its assigned site information through local Configuration Manager configuration.

Where available:

```powershell
Get-CimInstance -Namespace 'root\ccm' -ClassName SMS_Client -ErrorAction SilentlyContinue
```

Use local read-only queries before considering remote management interfaces.

---

# WMI and CIM

Configuration Manager relies extensively on WMI.

Important namespaces can include:

```text
root\ccm
root\sms
root\sms\site_<SITECODE>
```

Not every namespace exists on every system.

---

# Site Server Namespace

A site server commonly exposes a namespace resembling:

```text
root\sms\site_ABC
```

where:

```text
ABC
```

is the site code.

Access normally requires appropriate SCCM permissions.

---

# Do Not Brute Force WMI

Avoid repeatedly querying guessed namespaces across large numbers of systems.

First establish:

```text
Likely SCCM Role
Site Code
Authorised Access
```

then perform targeted queries.

---

# Configuration Manager Console

Administrators commonly manage SCCM through the Configuration Manager console.

The console provides access to areas such as:

```text
Assets and Compliance
Software Library
Monitoring
Administration
```

The privileges available depend on SCCM Role-Based Administration.

---

# SCCM RBAC

Configuration Manager implements its own role-based administration model.

This is separate from ordinary Active Directory group membership.

Conceptually:

```text
Administrative User
       |
       v
Security Role
       +
Security Scope
       +
Collection Scope
       |
       v
Effective SCCM Permission
```

---

# Security Roles

Configuration Manager includes administrative roles that can grant different capabilities.

One particularly powerful role is:

```text
Full Administrator
```

Membership should be highly restricted.

---

# Effective SCCM Privilege

Do not evaluate an SCCM administrator only by role name.

Effective authority depends on:

```text
Security Role
Security Scope
Collections
Objects
Delegated Permissions
```

---

# Collections

Configuration Manager uses collections to group devices and users.

Examples:

```text
All Systems
Workstations
Servers
Finance Devices
Domain Controllers
```

A deployment can target a collection.

Conceptually:

```text
Application / Script
        |
        v
Collection
        |
        v
Managed Devices
```

---

# Collection Security Importance

An administrator who can control deployments to:

```text
Domain Controllers
```

has a very different security impact from an administrator restricted to:

```text
Test Workstations
```

Therefore, always map:

```text
Privilege
        +
Collection Scope
        =
Potential Impact
```

---

# SCCM and Tier 0

A central security question is whether Configuration Manager manages:

```text
Domain Controllers
Certificate Authorities
Identity Servers
Privileged Access Workstations
ADFS Servers
Other Tier 0 Systems
```

If it does, SCCM may become part of the Tier 0 management plane.

---

# Management Plane Risk

Conceptually:

```text
SCCM Admin
    |
    v
Deployment Authority
    |
    v
Domain Controller
    |
    v
Active Directory
```

This is why SCCM administration should be evaluated as a privileged identity path.

---

# SCCM Service Accounts

Configuration Manager deployments can use several accounts depending on configuration.

Potentially important examples include:

```text
Client Push Installation Accounts
Network Access Accounts
SQL Service Accounts
Site System Installation Accounts
Reporting Accounts
Task Sequence Accounts
```

Not every environment uses all of these.

---

# Client Push Installation Account

Client push can use an account with administrative access to target computers.

The security relationship is:

```text
Client Push Account
       |
       v
Local Administrator
       |
       v
Managed Endpoints
```

Microsoft specifically advises against placing a client push installation account in:

```text
Domain Admins
```

---

# Client Push Risk

Client push has several security dependencies, including potentially:

```text
Administrative Access
ADMIN$
Firewall Access
Remote Management
Authentication
```

Microsoft describes client push as the least secure client-installation method because of these dependencies.

---

# Client Push Scope

A safer architecture limits each client push account to a restricted subset of systems.

Conceptually:

```text
Push Account A
     |
     +--> Workstation Group A

Push Account B
     |
     +--> Workstation Group B
```

rather than:

```text
One Domain-Wide Administrative Account
```

---

# Client Push and NTLM

Where client push is used, Microsoft supports requiring Kerberos mutual authentication and preventing fallback to NTLM for the connection.

This can reduce NTLM-related attack surface.

See:

[NTLM](ntlm.md)

and:

[NTLM Relay](ntlm-relay.md)

---

# Network Access Account

A Network Access Account may be configured in some environments for clients that need access to distribution-point content when they cannot use their computer account.

The security importance depends on:

```text
Whether It Exists
Privileges
Where It Can Authenticate
How It Is Protected
Whether Legacy Workflows Still Require It
```

Avoid granting it unnecessary rights.

---

# Network Access Account Is Not an Administrator by Design

A Network Access Account should not be treated as a general administrative account.

If it has:

```text
Local Administrator
Domain Administrator
Server Administrator
```

privileges, that should receive close review.

---

# Task Sequence Credentials

Operating-system deployment can involve task sequences and associated configuration.

Review:

```text
Task Sequences
Boot Media
PXE
Deployment Accounts
Scripts
Configuration Files
```

for unnecessary credentials.

---

# PXE Security

PXE-enabled Distribution Points deserve special attention.

Potential assessment questions include:

```text
Is PXE Enabled?
Is a PXE Password Used?
Who Can Reach the PXE Service?
What Boot Images Are Available?
Do Deployment Materials Contain Credentials?
```

---

# PXE Credential Exposure

Security research has demonstrated scenarios where deployment material exposed through PXE can reveal credentials or other sensitive configuration.

Do not assume:

```text
PXE Enabled
=
Credential Exposure
```

The actual configuration must be assessed.

---

# Distribution Point Content

Distribution Points can host:

```text
Applications
Packages
Scripts
Operating System Images
Boot Images
Drivers
Task Sequence Content
```

Access to this content should be reviewed from both:

```text
Confidentiality
Integrity
```

perspectives.

---

# Content Integrity

A particularly important question is:

```text
Who Can Modify Deployment Content?
```

Conceptually:

```text
Writable Package
      |
      v
Distribution
      |
      v
Managed Clients
```

Do not modify production SCCM packages to prove this risk.

Permission evidence is usually sufficient.

---

# SCCM Shares

Configuration Manager systems may expose SMB shares associated with content and management operations.

Enumerate shares only on approved systems.

Windows:

```cmd
net view \\SCCM01
```

Linux:

```bash
smbclient -L //sccm01.corp.example -U 'CORP/audituser'
```

See:

[Windows and Active Directory Shares](shares.md)

---

# Administrative Shares

SCCM workflows may interact with:

```text
ADMIN$
```

especially during client installation.

The existence of `ADMIN$` is normal.

The security issue is excessive access to it.

---

# SQL Server

The SCCM site database is one of the most security-sensitive components of the hierarchy.

Map:

```text
Site Server
     |
     v
SQL Server
     |
     v
Site Database
```

Determine whether SQL is:

```text
Local
Remote
Clustered
Highly Available
```

---

# SQL Security Questions

Assess:

```text
Who Can Connect?
Who Is Sysadmin?
Which SCCM Accounts Have SQL Rights?
Is SQL Reachable from User Networks?
Does SQL Use Windows Authentication?
Are Service Accounts Overprivileged?
```

---

# Remote Site Database

A remote SQL server creates additional relationships:

```text
Site Server
     |
     v
Network
     |
     v
SQL Server
```

This may introduce:

```text
Authentication Paths
Firewall Rules
Service Accounts
Relay Considerations
Administrative Dependencies
```

---

# SCCM and NTLM Relay

Configuration Manager can expose several services that interact with Windows authentication.

Research has identified SCCM-related NTLM relay attack paths involving:

```text
Site Systems
Management Points
SMB
SQL
```

depending on configuration.

The correct assessment is:

```text
Authentication Source
       |
       v
Relay Possible?
       |
       v
Target Service
       |
       v
Signing / Channel Protection
       |
       v
Privilege Obtained
```

Do not assume every SCCM environment is relayable.

---

# SMB Signing

Review SMB signing on SCCM infrastructure.

See:

[SMB](smb.md)

and:

[NTLM Relay](ntlm-relay.md)

---

# LDAP Signing and Channel Binding

SCCM infrastructure exists inside the wider Active Directory authentication environment.

Therefore also consider:

```text
LDAP Signing
LDAP Channel Binding
NTLM Restrictions
Kerberos
SMB Signing
```

where relevant to identified paths.

---

# HTTPS and Enhanced HTTP

Microsoft recommends secure Configuration Manager client communication.

Sites allowing plain HTTP client communication have been deprecated since Configuration Manager version 2103.

Modern environments should use:

```text
HTTPS
```

or:

```text
Enhanced HTTP
```

according to supported Configuration Manager architecture.

---

# PKI

Configuration Manager can use PKI certificates for client and site-system communication.

A PKI-based design can provide:

```text
Client Authentication
Server Authentication
Transport Protection
```

depending on the configured role.

---

# Enhanced HTTP

Enhanced HTTP reduces some of the PKI deployment burden while improving security over legacy plain HTTP communication.

Do not confuse:

```text
Enhanced HTTP
```

with:

```text
Every SCCM Connection Uses Full PKI HTTPS
```

The exact communication model depends on the site-system role and configuration.

---

# Client Approval

Configuration Manager can use client approval to identify trusted clients.

Microsoft recommends automatically approving computers from trusted domains and manually reviewing other systems when PKI authentication is not used.

Avoid:

```text
Automatically Approve All Computers
```

unless other controls make that configuration appropriate.

---

# SCCM Client Trust

A management platform should not automatically trust every system merely because it can reach SCCM infrastructure.

Conceptually:

```text
Device
 |
 v
Identity / Approval
 |
 v
Configuration Manager
```

---

# SCCM Discovery Workflow

A safe assessment can follow:

```text
Active Directory
      |
      v
Identify SCCM Presence
      |
      v
Identify Site Codes
      |
      v
Identify Management Points
      |
      v
Identify Site Servers
      |
      v
Identify Distribution Points
      |
      v
Identify Site Database
      |
      v
Map Administrative Accounts
      |
      v
Map Managed Systems
      |
      v
Review Misconfigurations
```

---

# Step 1 - Identify SCCM Presence

Search:

```text
System Management Container
SCCM Computer Names
SCCM Groups
SCCM Accounts
Installed Clients
DNS
```

---

# Step 2 - Enumerate Published Sites

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=System Management,CN=System,DC=corp,DC=example' \
  '(objectClass=mSSMSSite)' \
  cn mSSMSSiteCode mSSMSSourceForest
```

---

# Step 3 - Enumerate Management Points

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=System Management,CN=System,DC=corp,DC=example' \
  '(objectClass=mSMSManagementPoint)' \
  dNSHostName mSSMSSiteCode
```

---

# Step 4 - Resolve Infrastructure

```bash
dig sccm01.corp.example
```

or:

```powershell
Resolve-DnsName 'sccm01.corp.example'
```

---

# Step 5 - Identify Exposed Services

Use approved connectivity checks.

Windows:

```powershell
Test-NetConnection 'sccm01.corp.example' -Port 445
```

```powershell
Test-NetConnection 'sccm01.corp.example' -Port 80
```

```powershell
Test-NetConnection 'sccm01.corp.example' -Port 443
```

Only test ports relevant to the discovered role and authorised scope.

---

# Step 6 - Identify Client Installation

On an authorised endpoint:

```powershell
Get-Service -Name CcmExec -ErrorAction SilentlyContinue
```

---

# Step 7 - Identify Site Assignment

Where supported:

```powershell
Get-CimInstance -Namespace 'root\ccm' -ClassName SMS_Client -ErrorAction SilentlyContinue
```

---

# Step 8 - Map Administrative Groups

Search Active Directory:

```powershell
Get-ADGroup -Filter * |
    Where-Object {
        $_.Name -match 'SCCM|MECM|CONFIGMGR'
    }
```

Then determine:

```text
Group Membership
SCCM Role
Security Scope
Collection Scope
```

---

# Step 9 - Map Service Accounts

Look for accounts associated with:

```text
Client Push
SQL
Reporting
Site Systems
Deployment
Network Access
```

Do not assume account purpose solely from its name.

---

# Step 10 - Determine Tier 0 Exposure

Ask:

```text
Does SCCM Manage Domain Controllers?
Does SCCM Manage Certificate Authorities?
Does SCCM Manage ADFS?
Does SCCM Manage Privileged Workstations?
```

This is one of the most important SCCM security questions.

---

# Misconfiguration Manager

SpecterOps maintains:

```text
Misconfiguration Manager
```

a living knowledge base for Microsoft Configuration Manager attack and defense techniques.

It should be treated as an important reference when assessing modern SCCM security.

The project groups SCCM attack paths into categories such as:

```text
Reconnaissance
Credential Access
Privilege Elevation
Takeover
Execution
Persistence
Collection
```

The exact technique catalogue evolves as research develops.

---

# Why Use Misconfiguration Manager

Configuration Manager attack paths are often more complex than:

```text
One Misconfiguration
      |
      v
Domain Admin
```

A more realistic model is:

```text
Configuration Weakness
      |
      v
SCCM Capability
      |
      v
Administrative Relationship
      |
      v
Managed System
      |
      v
Privilege
```

Misconfiguration Manager helps map these relationships.

---

# Misconfiguration Manager Audit Script

The project includes defensive auditing capabilities for identifying documented SCCM security weaknesses.

Use the current project documentation rather than copying old command syntax.

Before using any audit tooling:

```text
Confirm Scope
Confirm Permissions
Review Source
Review Collection Behaviour
Test in Lab
```

---

# ConfigManBearPig

SpecterOps also maintains:

```text
ConfigManBearPig
```

for collecting Configuration Manager security information and visualising SCCM attack paths in BloodHound.

As of 2026, ConfigManBearPig 2.0 uses a Python-based collector architecture and can produce data suitable for BloodHound/OpenGraph analysis.

Use the project's current documentation because installation and collection syntax can change.

---

# BloodHound and SCCM

Modern BloodHound/OpenGraph capabilities can be used to visualise Configuration Manager relationships collected by compatible SCCM tooling.

Conceptually:

```text
User
 |
 v
SCCM Role
 |
 v
Collection
 |
 v
Managed Computer
 |
 v
Privilege
```

This can reveal management-plane attack paths that ordinary Active Directory collection may not make obvious.

See:

[BloodHound](bloodhound.md)

---

# SCCMHunter

SCCMHunter is another project designed to identify and profile Configuration Manager infrastructure.

Its functionality includes SCCM-specific:

```text
Discovery
Enumeration
Profiling
Security Testing
```

Because the project includes active attack functionality, use only the modules and actions permitted by the engagement.

Check current documentation rather than relying on old examples.

---

# SCCM Tooling Strategy

A useful tooling model is:

```text
Native LDAP
     |
     v
Identify SCCM
     |
     v
Misconfiguration Manager
     |
     +--> Defensive Audit
     |
     +--> Technique Reference
     |
     v
ConfigManBearPig / BloodHound
     |
     v
Attack Path Analysis
```

Use active exploitation tooling only when required to validate an approved finding.

---

# SCCM Attack Surface Categories

A practical review should consider:

```text
Active Directory Publication
Administrative Roles
Service Accounts
Client Push
Management Points
Distribution Points
PXE
Task Sequences
Site Database
SQL
SMB
HTTP / HTTPS
Client Authentication
Deployment Permissions
Collections
Content Integrity
```

---

# Credential Exposure

Configuration Manager can create credential exposure risks when:

```text
Privileged Accounts Are Used
Credentials Are Stored for Legacy Workflows
Deployment Content Contains Secrets
PXE Material Exposes Secrets
Service Accounts Are Overprivileged
```

The existence of an SCCM account is not itself a finding.

---

# Credential Risk Model

```text
SCCM Credential
      |
      v
Where Is It Stored?
      |
      v
Who Can Retrieve It?
      |
      v
Where Can It Authenticate?
      |
      v
What Privilege Does It Have?
```

---

# Client Push Account Finding

A high-risk configuration may resemble:

```text
Client Push Account
      |
      v
Domain Admins
```

This creates unnecessary domain-wide privilege.

Microsoft explicitly recommends against using Domain Admin membership for client push.

---

# Better Client Push Design

Prefer:

```text
Dedicated Account
      |
      v
Local Administrator
      |
      v
Limited Device Set
```

with separate accounts where necessary to limit blast radius.

---

# Application Deployment

Configuration Manager can deploy applications to managed systems.

Conceptually:

```text
Administrator
      |
      v
Application
      |
      v
Deployment
      |
      v
Collection
      |
      v
Clients
```

This is normal product functionality.

It becomes security sensitive when an inappropriate identity can create or modify deployments to privileged systems.

---

# Script Deployment

Configuration Manager also provides administrative mechanisms capable of running scripts or management actions.

Do not demonstrate SCCM compromise by deploying arbitrary scripts to production endpoints unless explicitly authorised.

A safer finding may be established through:

```text
Role Permission
+
Collection Scope
+
Deployment Capability
```

without executing anything.

---

# CMPivot

CMPivot provides near-real-time querying of managed devices.

It is useful for legitimate administration and incident response.

From a security perspective, access to CMPivot can expose:

```text
System Information
Processes
Files
Registry Information
Configuration
```

depending on query and environment.

Treat CMPivot access as sensitive administrative capability.

---

# CMPivot Testing

Do not run broad production queries merely to demonstrate access.

Prefer reviewing:

```text
Assigned SCCM Role
Security Scope
Collection Scope
```

If query validation is authorised, use a minimal non-sensitive query against an approved test collection.

---

# SCCM Console Access

Console access does not automatically mean:

```text
Full Administrator
```

Record:

```text
Role
Scope
Collections
Available Actions
```

---

# SCCM and Shares

SCCM deployment infrastructure may expose network shares containing:

```text
Packages
Scripts
Drivers
Boot Images
Applications
```

See:

[Windows and Active Directory Shares](shares.md)

The critical question is:

```text
Who Can Modify the Content?
```

---

# SCCM and Group Policy

Group Policy may be used to:

```text
Deploy SCCM Clients
Configure Firewall Rules
Assign Groups
Configure Client Push Dependencies
```

See:

[Group Policy](group-policy.md)

---

# SCCM and Local Administrators

Client push and administrative workflows can create local-administrator relationships.

Review:

```text
Which SCCM Accounts Are Local Administrators?
```

and:

```text
On Which Systems?
```

A single SCCM account with administrative access across the entire estate creates a large credential blast radius.

---

# SCCM and Lateral Movement

Configuration Manager relationships can facilitate lateral movement when an attacker compromises:

```text
Administrative Account
Site System
Deployment Authority
Privileged Service Account
```

See:

[Lateral Movement](lateral-movement.md)

---

# SCCM and Credential Access

Configuration Manager infrastructure may expose credential material through:

```text
Deployment Configuration
Legacy Accounts
PXE
Task Sequences
Service Accounts
Database Configuration
```

See:

[Credential Access](credential-access.md)

---

# SCCM and Kerberos

Where possible, SCCM administrative communication should use secure authentication mechanisms.

Kerberos can reduce reliance on NTLM in supported workflows.

See:

[Kerberos](kerberos.md)

---

# SCCM and NTLM

Legacy or fallback authentication can create additional risk.

Review:

```text
Where NTLM Is Used
Why It Is Required
Whether Kerberos Can Be Enforced
Whether Relay Protections Exist
```

See:

[NTLM](ntlm.md)

---

# SCCM Across Forests

Configuration Manager can operate across complex domain and forest architectures.

Cross-forest relationships should be mapped carefully.

Conceptually:

```text
Forest A
   |
   v
SCCM Infrastructure
   |
   v
Account from Forest B
```

A credential used across forest boundaries can increase compromise impact.

See:

[Trust Relationships](trust-relationships.md)

---

# SCCM Security Boundaries

Do not assume that:

```text
Different AD Domain
```

automatically isolates SCCM administration.

The actual security boundary depends on:

```text
SCCM Hierarchy
Account Placement
Trusts
SQL
Administrative Roles
Managed Systems
Network Connectivity
```

---

# SCCM Attack Path Analysis

A useful model is:

```text
Principal
   |
   v
SCCM Permission
   |
   v
SCCM Object
   |
   v
Collection
   |
   v
Managed System
   |
   v
Privilege
```

Another is:

```text
Credential
   |
   v
SCCM Infrastructure
   |
   v
Administrative Access
   |
   v
Site / Database
   |
   v
Managed Estate
```

---

# Do Not Stop at Domain Admin

SCCM can manage systems that are valuable even without direct Domain Admin access.

Examples:

```text
Database Servers
Backup Servers
Virtualisation Hosts
Developer Systems
Security Infrastructure
Management Servers
```

Assess business impact, not only domain privilege.

---

# Safe SCCM Assessment Workflow

A low-impact workflow is:

```text
Read AD Publication
       |
       v
Identify Infrastructure
       |
       v
Identify Roles
       |
       v
Map Accounts
       |
       v
Map Permissions
       |
       v
Map Collections
       |
       v
Identify Misconfigurations
       |
       v
Validate Without Deployment
       |
       v
Report
```

---

# Phase 1 - Passive Discovery

Collect:

```text
Site Codes
Management Points
Likely Site Servers
SCCM Groups
SCCM Accounts
Client Presence
```

Avoid configuration changes.

---

# Phase 2 - Architecture Mapping

Determine:

```text
CAS
Primary Sites
Secondary Sites
Management Points
Distribution Points
Site Database
PXE
Software Update Points
```

---

# Phase 3 - Identity Mapping

Identify:

```text
SCCM Administrators
Service Accounts
Client Push Accounts
SQL Accounts
Deployment Accounts
Network Access Accounts
```

---

# Phase 4 - Privilege Mapping

Determine:

```text
SCCM Role
Security Scope
Collection Scope
AD Privilege
Local Administrator Rights
SQL Privilege
```

---

# Phase 5 - Tier 0 Mapping

Identify whether SCCM manages:

```text
Domain Controllers
Certificate Authorities
ADFS
Privileged Workstations
Other Identity Infrastructure
```

---

# Phase 6 - Misconfiguration Review

Compare the environment against:

```text
Microsoft Security Guidance
Misconfiguration Manager
Current SCCM Security Research
Organisational Hardening Standards
```

---

# Phase 7 - Minimal Validation

Prefer:

```text
Read Permission
Configuration Evidence
Role Evidence
Collection Evidence
ACL Evidence
```

over:

```text
Deploying Payload
Changing Application
Executing Script
Changing Client Configuration
```

---

# Phase 8 - Cleanup

If no SCCM objects were modified:

```text
No SCCM Cleanup Required
```

If an approved test object was created:

```text
Record Original State
Remove Test Object
Verify Removal
Record Final State
```

---

# SCCM Detection

Defensive monitoring should consider:

```text
Administrative Logons
Console Activity
RBAC Changes
Application Changes
Package Changes
Collection Changes
Client Settings Changes
Task Sequence Changes
Account Changes
SQL Activity
Management Point Activity
Distribution Point Activity
Unexpected Deployments
```

---

# SCCM Audit Status Messages

Configuration Manager itself records extensive operational information.

Defenders should understand normal administrative activity so they can distinguish:

```text
Expected Administration
```

from:

```text
Unexpected Privileged Change
```

---

# SCCM Logs

Configuration Manager produces numerous log files across:

```text
Site Servers
Site Systems
Clients
```

The exact log depends on the component.

Common client logs can be found beneath:

```text
C:\Windows\CCM\Logs
```

---

# Client Logs

Examples commonly encountered include logs associated with:

```text
Client Operations
Policy
Applications
Content
Inventory
```

Use Microsoft's current log-file reference when troubleshooting or designing detection.

---

# Windows Security Logs

Correlate SCCM activity with Windows telemetry such as:

```text
4624
4625
4648
4672
4688
```

where relevant and auditing is configured.

---

# SMB Monitoring

SCCM may use SMB for some management operations.

Relevant telemetry can include:

```text
5140
5145
```

See:

[Windows and Active Directory Shares](shares.md)

---

# SQL Monitoring

For remote SCCM databases, monitor:

```text
Unexpected SQL Logons
Privilege Changes
Configuration Changes
New Administrative Users
Unusual Queries
```

according to the organisation's SQL auditing capabilities.

---

# Active Directory Monitoring

Monitor changes to:

```text
System Management Container
SCCM Service Accounts
SCCM Administrative Groups
Delegated ACLs
```

Directory Service auditing may provide additional visibility when configured.

---

# System Management Container Changes

Unexpected modification of:

```text
CN=System Management,CN=System
```

should be investigated.

Normal SCCM publication creates legitimate activity, so baseline expected behaviour.

---

# Administrative Group Monitoring

Monitor additions to groups associated with:

```text
SCCM Administration
SQL Administration
Server Administration
Deployment Administration
```

---

# Client Push Account Monitoring

Client push accounts should not normally perform interactive administration.

Investigate unexpected:

```text
Interactive Logon
RDP
PowerShell Administration
General Server Access
```

using those identities.

---

# Deployment Monitoring

High-value events include unexpected creation or modification of:

```text
Applications
Packages
Scripts
Task Sequences
Deployments
Collections
```

especially when targeting privileged systems.

---

# Tier 0 Collection Monitoring

If SCCM manages Tier 0 systems, administrative changes affecting those collections deserve enhanced monitoring.

Conceptually:

```text
SCCM Change
     |
     v
Tier 0 Collection
     |
     v
High-Priority Alert
```

---

# SCCM Hardening

A strong Configuration Manager security model includes:

```text
Least Privilege
Secure Client Communication
Restricted Administrative Roles
Restricted Service Accounts
Protected Site Servers
Protected SQL
Protected Distribution Points
Secure Client Push
Deployment Integrity
Tier Separation
Monitoring
```

---

# Use Least Privilege

SCCM administrators should receive only the permissions necessary for their responsibilities.

Avoid excessive assignment of:

```text
Full Administrator
```

---

# Restrict Security Scopes

Use:

```text
Security Roles
Security Scopes
Collections
```

to limit administrative reach.

---

# Separate Administrative Responsibilities

Where practical:

```text
Application Administrators
Endpoint Administrators
Server Administrators
Operating System Deployment Administrators
```

should not automatically receive equivalent control over every managed system.

---

# Protect Full Administrators

Treat SCCM Full Administrator identities as highly privileged.

Use:

```text
Dedicated Administrative Accounts
Strong Authentication
Privileged Workstations
Credential Isolation
Monitoring
```

according to organisational policy.

---

# Protect the Site Server

The site server should be treated as security-sensitive management infrastructure.

Restrict:

```text
Interactive Logon
Local Administrators
Remote Management
Network Access
Software Installation
```

---

# Protect the Site Database

Restrict:

```text
SQL Sysadmin
Database Access
Network Connectivity
Service Accounts
Backup Access
```

---

# Protect Distribution Points

Distribution Points should not expose unnecessary:

```text
Anonymous Access
Write Access
Administrative Access
```

---

# Protect Deployment Content

Only authorised deployment identities should be able to modify:

```text
Packages
Applications
Scripts
Boot Images
Task Sequences
```

---

# Secure Client Push

If client push is required:

```text
Use Dedicated Accounts
Limit Administrative Scope
Do Not Use Domain Admin
Prefer Kerberos Mutual Authentication
Prevent NTLM Fallback Where Supported
Monitor Account Use
```

---

# Prefer Safer Client Installation Methods

Microsoft notes that client installation methods such as:

```text
Group Policy
Software Update-Based Installation
```

can have fewer security dependencies than client push.

Choose the method appropriate for the environment.

---

# Secure Client Communication

Use:

```text
HTTPS
```

or:

```text
Enhanced HTTP
```

according to Microsoft's supported configuration guidance.

Legacy plain HTTP client communication should not be treated as the preferred design.

---

# PKI Where Appropriate

PKI can provide strong client authentication and secure communication.

Where PKI is deployed:

```text
Protect CA
Protect Private Keys
Monitor Certificates
Maintain Revocation
```

See the AD CS notes:

```text
docs/active-directory/ad-cs/index.md
```

---

# Client Approval

Prefer trusted-domain approval and controlled manual approval over unrestricted automatic client approval where PKI authentication is unavailable.

---

# Reduce NTLM

Where supported:

```text
Prefer Kerberos
Require Mutual Authentication
Restrict NTLM Fallback
```

This should be implemented only after compatibility testing.

---

# Separate SCCM from User Networks

Restrict direct access to SCCM infrastructure based on actual operational requirements.

Consider segmentation for:

```text
Site Servers
SQL
Management Interfaces
Distribution Infrastructure
```

---

# Tier 0 Considerations

If possible, carefully evaluate whether ordinary endpoint-management infrastructure should manage Tier 0 systems.

If SCCM does manage Tier 0:

```text
SCCM
```

may need equivalent protection.

---

# SCCM Backup Security

Configuration Manager backups may contain highly sensitive:

```text
Configuration
Database Information
Deployment Information
Secrets
```

Protect them accordingly.

---

# Service Account Hardening

For SCCM-related accounts:

```text
Use Dedicated Purpose
Minimum Privilege
Restrict Logon
Restrict Administrative Reach
Monitor Use
Rotate Where Applicable
```

Where supported, consider managed service-account technologies.

See:

[gMSA](gmsa.md)

---

# SCCM Security Review Questions

Ask:

```text
Who Are the Full Administrators?

Who Can Deploy Applications?

Who Can Deploy Scripts?

Who Can Modify Task Sequences?

Who Can Change Collections?

Who Can Manage Domain Controllers?

Who Can Modify Distribution Content?

Which Accounts Have Local Admin Everywhere?

Which Accounts Have SQL Sysadmin?

Which Accounts Cross Forest Boundaries?

Where Is NTLM Still Used?

Is Client Push Required?

Is PXE Enabled?

Are Deployment Credentials Present?

Is Plain HTTP Still Used?

Are SCCM Changes Monitored?
```

---

# Reporting SCCM Findings

Do not report:

```text
SCCM Exists
```

or:

```text
Management Point Exists
```

or:

```text
Distribution Point Exists
```

as vulnerabilities.

Report the actual misconfiguration and its reachable impact.

---

# Potential Findings

Examples include:

```text
SCCM Client Push Account Has Domain Administrator Privileges
```

```text
Low-Privilege SCCM Administrator Can Deploy to Tier 0 Systems
```

```text
Excessive SCCM Full Administrator Membership
```

```text
SCCM Deployment Content Writable by Unauthorised Users
```

```text
Legacy SCCM Client Communication Uses Insecure Configuration
```

```text
SCCM Service Account Has Unnecessary Administrative Rights
```

```text
PXE Deployment Configuration Exposes Sensitive Credentials
```

```text
SCCM Infrastructure Permits High-Risk NTLM Relay Path
```

```text
SCCM Site Database Is Exposed to Untrusted Network Segments
```

---

# Example Finding - Client Push Account

```text
Finding:
SCCM Client Push Account Has Excessive Domain Privileges

Description:
The Configuration Manager client push installation account was a
member of a highly privileged Active Directory administrative group.

Client push requires administrative access to managed endpoints but
does not require Domain Administrator privileges.

Impact:
Compromise of the client push account could provide substantially more
access than required for its intended function and may result in
domain-wide compromise.

Recommendation:
Remove the client push account from highly privileged domain groups.

Use one or more dedicated client push accounts with administrative
access limited to only the systems they are required to manage.

Where client push remains necessary, require Kerberos mutual
authentication and prevent NTLM fallback where supported and
operationally appropriate.
```

---

# Example Finding - Tier 0 Deployment Rights

```text
Finding:
Delegated SCCM Administrator Can Deploy Content to Domain Controllers

Description:
A delegated Configuration Manager administrator had permissions that
allowed deployments to a collection containing domain controllers.

The administrator's business role was intended to manage workstation
applications only.

No deployment was created or executed during testing.

Impact:
The delegated SCCM permissions create an administrative path from a
workstation-management identity to Tier 0 systems.

Compromise of the affected administrative account could therefore
have consequences for the Active Directory security boundary.

Recommendation:
Separate Tier 0 systems from ordinary endpoint-management scopes.

Restrict deployment permissions and collection access so delegated
workstation administrators cannot manage domain controllers or other
identity infrastructure.

Review all SCCM roles, security scopes and collection assignments for
similar privilege paths.
```

---

# Example Finding - Writable Deployment Content

```text
Finding:
SCCM Deployment Content Writable by Low-Privilege Domain Users

Description:
A network location containing Configuration Manager deployment content
was writable by a broad domain group.

The assessment verified the excessive file-system permission without
modifying any production deployment files.

Impact:
If Configuration Manager clients consume content from the affected
location without sufficient integrity controls, an attacker with write
access may be able to influence software distributed to managed
systems.

The resulting impact depends on the affected package, deployment
context and target collection.

Recommendation:
Restrict modification of SCCM deployment content to dedicated
administrative and service identities.

Review both share and NTFS permissions and remove broad write access.

Monitor deployment-content changes and use integrity validation where
supported.
```

---

# Example Finding - Excessive Full Administrators

```text
Finding:
Excessive Membership in SCCM Full Administrator Role

Description:
Multiple identities were assigned the Configuration Manager Full
Administrator role despite performing responsibilities that required
only limited endpoint-management permissions.

Impact:
Compromise of any unnecessarily privileged identity could provide
broad control over the Configuration Manager hierarchy and managed
systems.

Where SCCM manages privileged servers, the impact may extend to
security-critical infrastructure.

Recommendation:
Review all Configuration Manager administrative users.

Replace Full Administrator assignments with narrowly scoped security
roles, security scopes and collections based on job requirements.

Periodically recertify SCCM administrative access.
```

---

# Example Finding - Legacy Client Communication

```text
Finding:
Configuration Manager Uses Legacy Client Communication Configuration

Description:
The Configuration Manager site permitted client communication using a
legacy configuration instead of HTTPS or Enhanced HTTP.

Microsoft has deprecated sites that allow plain HTTP client
communication.

Impact:
Legacy communication settings can reduce the authentication and
transport-security protections available between clients and site
systems.

The exact impact depends on the roles, authentication configuration
and network position of an attacker.

Recommendation:
Plan migration to HTTPS or Enhanced HTTP according to current
Microsoft Configuration Manager guidance.

Validate certificate, application and legacy-client dependencies in a
test environment before enforcing the change.
```

---

# Example Finding - PXE Exposure

```text
Finding:
SCCM PXE Deployment Configuration Exposes Sensitive Deployment Material

Description:
The Configuration Manager PXE deployment service was reachable from a
network segment that did not require operating-system deployment
access.

Assessment of the approved deployment workflow identified sensitive
material accessible through the PXE configuration.

Impact:
An unauthorised system with network access to the PXE-enabled
Distribution Point may obtain deployment information or credentials,
depending on the exposed configuration.

Recommendation:
Restrict network access to PXE-enabled Distribution Points.

Review deployment credentials, boot-image configuration and task
sequences for unnecessary secrets.

Apply the current Microsoft and Misconfiguration Manager hardening
guidance for PXE deployment.
```

---

# SCCM Assessment Checklist

## Discovery

- [ ] Search `System Management`
- [ ] Identify SCCM site codes
- [ ] Identify Management Points
- [ ] Identify site servers
- [ ] Identify Distribution Points
- [ ] Identify Software Update Points
- [ ] Identify PXE-enabled roles
- [ ] Identify site database
- [ ] Identify Configuration Manager clients
- [ ] Review DNS
- [ ] Review naming conventions

## Active Directory

- [ ] Enumerate `mSSMSSite`
- [ ] Enumerate `mSMSManagementPoint`
- [ ] Review System Management ACLs
- [ ] Identify SCCM-related groups
- [ ] Identify SCCM-related users
- [ ] Identify service accounts
- [ ] Identify cross-forest accounts

## Architecture

- [ ] Identify CAS if present
- [ ] Identify primary sites
- [ ] Identify secondary sites
- [ ] Identify remote site systems
- [ ] Identify remote SQL
- [ ] Map site relationships
- [ ] Map management points
- [ ] Map distribution points

## Client

- [ ] Check `CcmExec`
- [ ] Check `C:\Windows\CCM`
- [ ] Check `CCMSetup`
- [ ] Check `CCMCache`
- [ ] Identify assigned site
- [ ] Review client communication
- [ ] Review client approval

## Administrative Security

- [ ] Enumerate SCCM administrators
- [ ] Identify Full Administrators
- [ ] Review security roles
- [ ] Review security scopes
- [ ] Review collection scopes
- [ ] Identify excessive privileges
- [ ] Identify stale administrators
- [ ] Review administrative group nesting

## Tier 0

- [ ] Determine whether SCCM manages domain controllers
- [ ] Determine whether SCCM manages certificate authorities
- [ ] Determine whether SCCM manages ADFS
- [ ] Determine whether SCCM manages privileged workstations
- [ ] Identify administrators able to target Tier 0
- [ ] Identify service accounts with Tier 0 access

## Accounts

- [ ] Identify client push accounts
- [ ] Identify Network Access Accounts
- [ ] Identify SQL service accounts
- [ ] Identify reporting accounts
- [ ] Identify site-system accounts
- [ ] Identify deployment credentials
- [ ] Review account privileges
- [ ] Review local-administrator scope
- [ ] Review cross-forest use

## Client Push

- [ ] Determine whether client push is enabled
- [ ] Identify client push accounts
- [ ] Confirm accounts are not Domain Admins
- [ ] Determine local-administrator scope
- [ ] Review Kerberos mutual authentication
- [ ] Review NTLM fallback
- [ ] Review firewall exposure

## Distribution

- [ ] Identify deployment shares
- [ ] Review share permissions
- [ ] Review NTFS permissions
- [ ] Identify writable content
- [ ] Review packages
- [ ] Review applications
- [ ] Review scripts
- [ ] Review task sequences
- [ ] Review boot images
- [ ] Review operating-system images

## PXE

- [ ] Determine whether PXE is enabled
- [ ] Identify PXE-enabled DPs
- [ ] Review network exposure
- [ ] Review PXE protection
- [ ] Review boot images
- [ ] Review deployment credentials
- [ ] Review task sequences
- [ ] Avoid booting production deployments without approval

## SQL

- [ ] Identify SQL server
- [ ] Identify database location
- [ ] Review network exposure
- [ ] Review authentication
- [ ] Review sysadmin membership
- [ ] Review SCCM database permissions
- [ ] Review service accounts
- [ ] Review SQL auditing

## Authentication

- [ ] Review Kerberos use
- [ ] Review NTLM use
- [ ] Review SMB signing
- [ ] Review LDAP protections where relevant
- [ ] Review HTTPS
- [ ] Review Enhanced HTTP
- [ ] Review PKI
- [ ] Review client approval

## Misconfiguration Manager

- [ ] Review current attack-technique catalogue
- [ ] Review current defense techniques
- [ ] Use defensive auditing where authorised
- [ ] Validate findings manually
- [ ] Avoid assuming every technique applies
- [ ] Record tool version
- [ ] Record collection scope

## BloodHound

- [ ] Consider SCCM OpenGraph collection
- [ ] Map SCCM administrators
- [ ] Map SCCM roles
- [ ] Map collections
- [ ] Map managed systems
- [ ] Identify Tier 0 paths
- [ ] Validate graph findings against configuration

## Detection

- [ ] Monitor SCCM administrative changes
- [ ] Monitor Full Administrator changes
- [ ] Monitor collection changes
- [ ] Monitor deployment changes
- [ ] Monitor task sequence changes
- [ ] Monitor package changes
- [ ] Monitor application changes
- [ ] Monitor client settings
- [ ] Monitor service-account use
- [ ] Monitor SQL activity
- [ ] Monitor SMB activity
- [ ] Monitor Tier 0 deployments

## Hardening

- [ ] Apply SCCM least privilege
- [ ] Restrict Full Administrators
- [ ] Restrict security scopes
- [ ] Restrict collection scopes
- [ ] Protect site server
- [ ] Protect SQL
- [ ] Protect distribution points
- [ ] Protect deployment content
- [ ] Secure client push
- [ ] Avoid Domain Admin client push accounts
- [ ] Prefer Kerberos
- [ ] Reduce NTLM
- [ ] Use HTTPS or Enhanced HTTP
- [ ] Review PKI
- [ ] Review client approval
- [ ] Segment SCCM infrastructure
- [ ] Review Tier 0 management

## Reporting

- [ ] Do not report SCCM presence alone
- [ ] Identify exact misconfiguration
- [ ] Identify affected SCCM role
- [ ] Identify affected identity
- [ ] Identify collection scope
- [ ] Identify managed systems
- [ ] Explain realistic attack path
- [ ] Avoid unnecessary active deployment
- [ ] Record evidence
- [ ] Provide SCCM-specific remediation

---

# SCCM Testing Model

The architecture model is:

```text
Active Directory
      |
      v
Configuration Manager
      |
      +--> Site Server
      +--> SQL
      +--> Management Point
      +--> Distribution Point
      +--> Client
```

The administrative model is:

```text
Administrator
      |
      v
SCCM Role
      |
      v
Security Scope
      |
      v
Collection
      |
      v
Managed Device
```

The deployment model is:

```text
Content
   |
   v
SCCM
   |
   v
Distribution Point
   |
   v
Collection
   |
   v
Client
```

The client push model is:

```text
Client Push Account
       |
       v
Administrative Access
       |
       v
Managed Endpoint
```

The SQL model is:

```text
SCCM Site
    |
    v
Site Database
    |
    v
Configuration and Authority
```

The credential model is:

```text
SCCM Account
     |
     v
Credential Exposure
     |
     v
Account Privilege
     |
     v
Managed Systems
```

The Tier 0 model is:

```text
SCCM Administrator
        |
        v
Deployment Capability
        |
        v
Tier 0 Collection
        |
        v
Identity Infrastructure
```

The relay model is:

```text
Authentication
      |
      v
SCCM Service
      |
      v
Relay Preconditions
      |
      v
Target Service
      |
      v
Obtained Privilege
```

The security model is:

```text
Least Privilege
      +
Protected Accounts
      +
Secure Communication
      +
Protected SQL
      +
Protected Deployment Content
      +
Tier Separation
      +
Monitoring
      =
Reduced SCCM Risk
```

The most important distinction is:

```text
SCCM Presence
    !=
SCCM Vulnerability
```

Another important distinction is:

```text
SCCM Administrator
      !=
Automatically Domain Admin
```

The actual question is:

```text
What Can That Administrator Control?
```

For penetration testers:

```text
Do Not Ask:
"Can SCCM execute code?"

That is normal product functionality.

Ask:
"Which identities can use SCCM
management functionality against
systems they should not control?"
```

For defenders:

```text
Do Not Ask:
"Is SCCM working?"

Ask:
"Who controls SCCM, which systems
can they control, and is SCCM itself
protected at the same level as the
systems it manages?"
```

The complete model is:

```text
Identity
   |
   v
SCCM Permission
   |
   v
Management Capability
   |
   v
Collection
   |
   v
Managed System
   |
   v
Privilege
   |
   v
Security Impact
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Enumeration:

[Enumeration](enumeration.md)

Groups:

[Groups](groups.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Group Policy:

[Group Policy](group-policy.md)

Credential Access:

[Credential Access](credential-access.md)

gMSA:

[gMSA](gmsa.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

SMB:

[SMB](smb.md)

Shares:

[Windows and Active Directory Shares](shares.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

ADIDNS:

[Active Directory Integrated DNS](adidns.md)

Trust Relationships:

[Trust Relationships](trust-relationships.md)

AD CS:

[Active Directory Certificate Services](ad-cs/index.md)

The next infrastructure page is:

```text
docs/active-directory/wsus.md
```

followed by:

```text
docs/active-directory/mdt.md
docs/active-directory/scom.md
docs/active-directory/adfs.md
docs/active-directory/rodc.md
```

---

# References

## Microsoft - Configuration Manager Documentation

[Microsoft - Configuration Manager](https://learn.microsoft.com/en-us/intune/configmgr/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Configuration Manager Core Infrastructure

[Microsoft - Core Infrastructure](https://learn.microsoft.com/en-us/intune/configmgr/core/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Planning for Configuration Manager

[Microsoft - Plan for Security](https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/security/plan-for-security){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Client Security and Privacy

[Microsoft - Security and Privacy for Configuration Manager Clients](https://learn.microsoft.com/en-us/intune/configmgr/core/clients/deploy/plan/security-and-privacy-for-clients){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Configuration Manager Certificates

[Microsoft - Certificates Overview](https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/security/certificates-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Configuration Manager Logs

[Microsoft - Configuration Manager Log Files](https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/hierarchy/log-files){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Misconfiguration Manager

[SpecterOps - Misconfiguration Manager](https://docs.specterops.io/misconfiguration-manager-docs/README){ target="_blank" rel="noopener noreferrer" }

Misconfiguration Manager is a living knowledge base of Configuration Manager attack techniques and corresponding defensive guidance. :contentReference[oaicite:0]{index=0}

---

## SpecterOps - ConfigManBearPig

[SpecterOps - ConfigManBearPig 2.0](https://specterops.io/blog/2026/08/03/configmanbearpig-2-0/){ target="_blank" rel="noopener noreferrer" }

ConfigManBearPig 2.0 provides Python-based SCCM data collection that can be used with BloodHound/OpenGraph to visualise Configuration Manager attack paths. :contentReference[oaicite:1]{index=1}

---

## SpecterOps - SCCMHunter

[SpecterOps - SCCMHunter Documentation](https://docs.specterops.io/sccmhunter-docs/overview){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - SCCM LDAP Discovery

[SpecterOps - Misconfiguration Manager RECON-1](https://docs.specterops.io/misconfiguration-manager-docs/attack-techniques/RECON/RECON-1/recon-1_description){ target="_blank" rel="noopener noreferrer" }

The documented discovery technique covers SCCM publication in Active Directory, including `mSSMSSite`, `mSMSManagementPoint`, site codes and management-point hostnames. :contentReference[oaicite:2]{index=2}

---

## SpecterOps - SCCM Least Privilege

[SpecterOps - Misconfiguration Manager PREVENT-10](https://docs.specterops.io/misconfiguration-manager-docs/defense-techniques/PREVENT/PREVENT-10/prevent-10_description){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Software Discovery

[MITRE ATT&CK - T1518 Software Discovery](https://attack.mitre.org/techniques/T1518/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - System Network Configuration Discovery

[MITRE ATT&CK - T1016 System Network Configuration Discovery](https://attack.mitre.org/techniques/T1016/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Microsoft Configuration Manager should be treated as a security-sensitive management plane.

The fundamental relationship is:

```text
Administrator
      |
      v
Configuration Manager
      |
      v
Managed Estate
```

The critical security question is not:

```text
Is SCCM Installed?
```

It is:

```text
Who Controls SCCM?
      |
      v
What Can They Manage?
      |
      v
Which Systems Are Included?
      |
      v
What Privilege Does That Create?
```

SCCM can become particularly important when it manages:

```text
Domain Controllers
Certificate Authorities
Identity Servers
Privileged Workstations
Other Tier 0 Infrastructure
```

The assessment should therefore connect:

```text
SCCM Role
    +
Security Scope
    +
Collection
    +
Managed Device
    =
Actual Privilege
```

Service accounts should similarly be evaluated as:

```text
Account
   |
   v
Where Can It Authenticate?
   |
   v
What Privilege Does It Have?
   |
   v
What Is the Blast Radius?
```

Modern SCCM assessment should incorporate Microsoft's current security guidance together with dedicated Configuration Manager attack-path research such as Misconfiguration Manager. Microsoft currently recommends HTTPS or Enhanced HTTP rather than legacy plain HTTP client communication, and specifically warns against using Domain Admin privileges for client push accounts. :contentReference[oaicite:3]{index=3}

The defensive objective is:

```text
Least Privilege
      |
      v
Secure Accounts
      |
      v
Secure Communication
      |
      v
Protected Site Infrastructure
      |
      v
Protected Deployment Content
      |
      v
Tier Separation
      |
      v
Monitoring
```

The next infrastructure page covers another Windows management technology closely connected to enterprise patching:

```text
Windows Server Update Services - WSUS
```
