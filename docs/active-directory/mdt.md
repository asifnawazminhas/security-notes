# Microsoft Deployment Toolkit - MDT

Microsoft Deployment Toolkit, commonly abbreviated:

```text
MDT
```

is a Microsoft deployment framework historically used to automate Windows operating-system and application deployment.

MDT can be used to manage deployment workflows involving:

```text
Windows Installation
Operating System Images
Applications
Drivers
Packages
Task Sequences
Scripts
Configuration
Domain Join
```

A simplified deployment model is:

```text
Administrator
      |
      v
MDT Deployment Share
      |
      v
Task Sequence
      |
      v
Windows PE
      |
      v
Target Computer
      |
      v
Windows Deployment
```

MDT is particularly interesting during Active Directory security assessments because deployment infrastructure can contain:

```text
Scripts
Configuration Files
Network Shares
Deployment Credentials
Domain Join Configuration
Administrative Accounts
Application Installers
```

These components can create paths from deployment infrastructure to managed Windows systems or Active Directory.

!!! warning "Authorised testing only"
    Deployment infrastructure can affect large numbers of systems. Do not modify deployment shares, task sequences, scripts, images, bootstrap configuration or deployment credentials during a production assessment unless explicitly authorised. Prefer read-only enumeration and permission analysis.

---

# MDT Lifecycle Status

MDT is legacy deployment technology.

Microsoft announced the retirement of Microsoft Deployment Toolkit in January 2026.

Organisations should therefore distinguish:

```text
MDT Still Present
```

from:

```text
MDT Recommended for New Deployment
```

Existing environments may continue to contain MDT infrastructure even while organisations migrate to newer deployment and provisioning technologies.

The presence of MDT should therefore trigger both:

```text
Security Assessment
```

and:

```text
Lifecycle Review
```

---

# Why MDT Matters

Deployment systems inherently possess significant capability.

Conceptually:

```text
Deployment Infrastructure
        |
        v
Operating System
        |
        v
Applications
        |
        v
Configuration
        |
        v
Domain Membership
```

A deployment platform may therefore interact with systems before normal endpoint security controls are fully operational.

---

# MDT Is Not Automatically a Vulnerability

Do not report:

```text
MDT Is Installed
```

or:

```text
Deployment Share Exists
```

as a vulnerability.

Instead determine:

```text
Who Can Access the Deployment Share?
Who Can Modify It?
What Credentials Are Present?
What Scripts Are Executed?
What Systems Use the Infrastructure?
Can Untrusted Users Modify Deployment Content?
Are Legacy Credentials Still Active?
Is MDT Still Operationally Required?
```

---

# Core Architecture

A simplified MDT environment can contain:

```text
MDT Server
   |
   +--> Deployment Share
   |
   +--> Operating Systems
   |
   +--> Applications
   |
   +--> Packages
   |
   +--> Drivers
   |
   +--> Task Sequences
   |
   +--> Scripts
   |
   +--> Control Files
   |
   v
Windows PE
   |
   v
Target Computer
```

MDT can also integrate with:

```text
Windows Deployment Services - WDS
Active Directory
DNS
DHCP
SMB
Windows PE
SQL Server
Configuration Manager
```

depending on the environment and deployment architecture.

---

# Deployment Share

The central MDT resource is commonly a:

```text
Deployment Share
```

Example:

```text
D:\DeploymentShare
```

The corresponding SMB share may resemble:

```text
\\MDT01\DeploymentShare$
```

The trailing:

```text
$
```

makes the SMB share hidden from ordinary share browsing.

It does not provide a security boundary.

---

# Hidden Shares

A hidden share such as:

```text
DeploymentShare$
```

is still accessible when:

```text
Share Name Is Known
+
Network Access Is Available
+
Permissions Permit Access
```

Therefore:

```text
Hidden Share
    !=
Secure Share
```

---

# Deployment Share Structure

A typical deployment share can contain directories resembling:

```text
DeploymentShare
├── Applications
├── Boot
├── Captures
├── Control
├── Operating Systems
├── Out-of-Box Drivers
├── Packages
├── Scripts
├── Servicing
├── Tools
└── USMT
```

The exact structure depends on MDT version and configuration.

---

# Important Directories

From a security perspective, particularly interesting locations include:

```text
Control
Scripts
Applications
Boot
Captures
Operating Systems
```

These may reveal:

```text
Deployment Logic
Credentials
Network Paths
Domain Information
Application Configuration
Task Sequences
```

---

# Control Directory

The:

```text
Control
```

directory contains important deployment configuration.

Files commonly encountered include:

```text
Bootstrap.ini
CustomSettings.ini
TaskSequences.xml
OperatingSystems.xml
Applications.xml
```

Not every file is equally sensitive, but the directory deserves careful review.

---

# Bootstrap.ini

One of the most important MDT configuration files is:

```text
Bootstrap.ini
```

It controls early deployment behaviour before the full deployment share has been accessed.

A simplified example might contain:

```ini
[Settings]
Priority=Default

[Default]
DeployRoot=\\MDT01\DeploymentShare$
UserDomain=CORP
UserID=MDT_Build
UserPassword=ExamplePassword
SkipBDDWelcome=YES
```

!!! danger "Credential exposure"
    Legacy MDT deployments may contain credentials in deployment configuration. Never place real credentials in documentation, screenshots or repositories.

---

# Why Bootstrap.ini Matters

Windows PE must often connect to the deployment share.

Conceptually:

```text
Windows PE
    |
    v
Bootstrap.ini
    |
    +--> DeployRoot
    +--> UserDomain
    +--> UserID
    +--> UserPassword
    |
    v
Deployment Share
```

If reusable credentials are embedded here, anyone able to obtain the relevant deployment material may potentially recover them.

---

# CustomSettings.ini

Another important configuration file is:

```text
CustomSettings.ini
```

It controls MDT deployment rules and automation.

Example:

```ini
[Settings]
Priority=Default

[Default]
OSInstall=Y
SkipComputerName=NO
SkipDomainMembership=NO
```

The file can contain much more extensive deployment logic.

---

# CustomSettings.ini Security Review

Search for:

```text
UserID
UserPassword
UserDomain
DomainAdmin
DomainAdminDomain
DomainAdminPassword
JoinDomain
MachineObjectOU
DeployRoot
BackupShare
BackupDir
```

The exact properties used depend on the deployment design.

---

# Domain Join

MDT can automate domain joining during deployment.

Conceptually:

```text
New Computer
     |
     v
MDT
     |
     v
Domain Join
     |
     v
Active Directory
```

Historically, deployments have sometimes used reusable domain credentials for this process.

That deserves careful review.

---

# Domain Join Account

A domain join account should have only the rights required to create or manage computer objects in the intended scope.

Avoid:

```text
Domain Admin
```

for routine machine joining.

A safer conceptual model is:

```text
Dedicated Join Account
       |
       v
Delegated OU
       |
       v
Computer Objects
```

---

# Domain Join Privilege

The required permission should normally be restricted to the intended:

```text
Organizational Unit
```

rather than:

```text
Entire Domain
```

See:

[ACL and ACE](acl-ace.md)

---

# MachineAccountQuota

Active Directory may separately permit ordinary domain users to create computer accounts through:

```text
ms-DS-MachineAccountQuota
```

This is different from MDT domain-join delegation.

See:

[MachineAccountQuota](machine-account-quota.md)

---

# Domain Join Security Model

```text
Deployment
    |
    v
Join Credential
    |
    v
OU Delegation
    |
    v
Computer Object
```

The key questions are:

```text
Where Is the Credential Stored?
Who Can Recover It?
What Rights Does It Have?
Where Can It Authenticate?
Is It Still Required?
```

---

# Deployment Credentials

Potential MDT-related credentials can include:

```text
Deployment Share Account
Domain Join Account
Application Installation Account
Database Account
Backup Account
Service Account
```

Not every environment uses all of these.

---

# Credential Risk Model

```text
Credential
   |
   v
Storage Location
   |
   v
Exposure
   |
   v
Privileges
   |
   v
Reachable Systems
   |
   v
Blast Radius
```

---

# Do Not Assume Credentials Are Privileged

Finding:

```text
Password Found in Bootstrap.ini
```

does not automatically mean:

```text
Domain Compromise
```

Determine:

```text
Account Identity
Account Status
Group Membership
Delegated Rights
Local Administrator Access
Network Logon Rights
Domain Join Rights
Password Reuse
```

---

# Deployment Share Discovery

MDT infrastructure may be discovered through:

```text
SMB
DNS
Active Directory
Computer Names
Group Policy
Documentation
PXE
Existing Clients
Scripts
Configuration Files
```

---

# Search Active Directory Computers

From an authorised domain context:

```powershell
Get-ADComputer -Filter * |
    Where-Object {
        $_.Name -match 'MDT|DEPLOY|WDS|BUILD'
    } |
    Select-Object Name,DNSHostName
```

Treat names only as leads.

A computer named:

```text
MDT01
```

does not prove MDT is installed.

---

# Search DNS

Once a likely server is identified:

```powershell
Resolve-DnsName 'mdt01.corp.example'
```

Linux:

```bash
dig mdt01.corp.example
```

See:

[Active Directory Integrated DNS](adidns.md)

---

# SMB Discovery

MDT commonly relies on SMB for deployment-share access.

From Windows:

```cmd
net view \\MDT01
```

Linux:

```bash
smbclient -L //mdt01.corp.example -U 'CORP/audituser'
```

See:

[SMB](smb.md)

---

# Enumerate Shares with PowerShell

On an authorised server:

```powershell
Get-SmbShare
```

Look for names resembling:

```text
DeploymentShare$
MDT$
Deploy$
Build$
```

Naming is environment specific.

---

# Remote Share Enumeration

If permissions allow:

```powershell
Get-ChildItem '\\MDT01\DeploymentShare$'
```

This is a read-only filesystem operation.

---

# Linux SMB Access

List a known share:

```bash
smbclient //mdt01.corp.example/DeploymentShare$ -U 'CORP/audituser'
```

Inside:

```text
ls
```

Use read-only browsing during initial assessment.

---

# Recursive SMB Enumeration

Avoid indiscriminately downloading an entire deployment share.

Deployment shares can contain:

```text
Large Operating System Images
Applications
Drivers
Packages
```

Instead target high-value configuration files first.

---

# High-Value Files

Prioritise:

```text
Control\Bootstrap.ini
Control\CustomSettings.ini
Control\TaskSequences.xml
Scripts\
Applications\
```

Then expand only where required.

---

# Search from Windows

If the deployment share is accessible:

```powershell
Get-ChildItem '\\MDT01\DeploymentShare$\Control' -File -ErrorAction SilentlyContinue
```

---

# Search Configuration for Credential Indicators

```powershell
Get-ChildItem '\\MDT01\DeploymentShare$\Control' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'UserPassword','DomainAdminPassword','Password','UserID','DomainAdmin'
```

Review results manually.

A match for:

```text
Password
```

does not automatically indicate a real credential.

---

# Search Scripts

```powershell
Get-ChildItem '\\MDT01\DeploymentShare$\Scripts' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','credential','username','token','secret'
```

False positives are expected.

---

# Linux Search

If an authorised copy of configuration files has been collected:

```bash
grep -RniE 'password|credential|username|token|secret' ./Control ./Scripts
```

Do not recursively copy operating-system images simply to search for strings.

---

# Bootstrap.ini Location

Inside the deployment share, a common source is:

```text
Control\Bootstrap.ini
```

The configuration is also incorporated into generated MDT boot media.

This is security relevant because:

```text
Boot Media
    |
    v
Bootstrap Configuration
    |
    v
Deployment Credentials
```

---

# MDT Boot Images

MDT generates Windows PE boot images used to start deployments.

Common output can include:

```text
LiteTouchPE_x64.wim
LiteTouchPE_x64.iso
```

Names can vary by architecture and deployment configuration.

---

# Boot Directory

Generated boot media commonly appears beneath:

```text
Boot
```

inside the deployment share.

Example:

```text
DeploymentShare\Boot
```

---

# Why Boot Images Matter

Boot images may contain deployment configuration required to reach the deployment infrastructure.

Conceptually:

```text
Boot Image
    |
    v
Windows PE
    |
    v
Deployment Configuration
    |
    v
Deployment Share
```

If configuration contains reusable credentials, possession of deployment media can become a credential-exposure concern.

---

# Boot Media Security

Treat:

```text
ISO Files
WIM Files
USB Deployment Media
PXE Boot Images
```

as potentially sensitive.

Protect them according to the credentials and configuration they contain.

---

# Offline Boot Image Review

Where explicitly authorised, a copy of deployment media can be reviewed offline.

The objective is to identify:

```text
Deployment Configuration
Server Names
Share Paths
Credentials
Scripts
Certificates
```

without booting production systems.

---

# Mounting WIM Files

On an authorised Windows analysis system, administrators can use DISM to inspect WIM content.

First inspect metadata:

```cmd
dism /Get-WimInfo /WimFile:C:\Analysis\LiteTouchPE_x64.wim
```

Mount an identified image index:

```cmd
dism /Mount-Image /ImageFile:C:\Analysis\LiteTouchPE_x64.wim /Index:1 /MountDir:C:\Analysis\Mount
```

After analysis:

```cmd
dism /Unmount-Image /MountDir:C:\Analysis\Mount /Discard
```

Use copies of deployment media rather than modifying production files.

---

# Windows PE

MDT uses:

```text
Windows Preinstallation Environment - Windows PE
```

to provide the deployment environment.

Windows PE typically:

```text
Boots
Loads Network Drivers
Obtains Network Configuration
Connects to Deployment Infrastructure
Starts MDT Deployment Logic
```

---

# PXE

MDT can be combined with Windows Deployment Services or other PXE infrastructure.

Conceptually:

```text
Client
 |
 v
PXE
 |
 v
Boot Server
 |
 v
Windows PE
 |
 v
MDT
```

---

# PXE Security Questions

Assess:

```text
Which Networks Can Reach PXE?
Can Unmanaged Devices Boot?
Is User Interaction Required?
Which Boot Images Are Exposed?
Do Boot Images Contain Credentials?
Are Deployment Shares Reachable Afterwards?
```

---

# DHCP and PXE

PXE deployments depend on network boot discovery.

Depending on network design, this can involve:

```text
DHCP
PXE Responder
IP Helpers
Boot Server
```

Do not modify DHCP or PXE configuration during ordinary assessment.

---

# WDS

Windows Deployment Services, commonly:

```text
WDS
```

has historically been used with MDT for PXE-based deployment.

Conceptually:

```text
WDS
 |
 v
LiteTouchPE
 |
 v
MDT Deployment Share
```

---

# MDT vs WDS

These technologies are related but not identical.

```text
WDS
```

primarily provides network boot and deployment-related services.

```text
MDT
```

provides deployment orchestration, task sequencing and automation.

---

# MDT vs SCCM

MDT and Configuration Manager historically supported different deployment scenarios and could also be integrated.

Conceptually:

```text
MDT
 |
 +--> Deployment Workbench
 +--> Deployment Shares
 +--> Lite Touch

Configuration Manager
 |
 +--> Enterprise Management
 +--> Collections
 +--> Applications
 +--> Task Sequences
 +--> Software Updates
```

See:

[Microsoft Configuration Manager - SCCM](sccm.md)

---

# Lite Touch Installation

A common MDT deployment model is:

```text
Lite Touch Installation - LTI
```

LTI uses MDT deployment shares and Windows PE to perform automated or semi-automated operating-system deployment.

---

# Zero Touch Installation

Historically:

```text
Zero Touch Installation - ZTI
```

referred to highly automated deployment through Configuration Manager integration.

Do not assume a modern environment still uses these historical deployment models.

---

# Deployment Workbench

MDT is commonly administered through:

```text
Deployment Workbench
```

Administrators use it to manage:

```text
Deployment Shares
Operating Systems
Applications
Packages
Drivers
Task Sequences
Selection Profiles
Advanced Configuration
```

---

# Task Sequences

Task sequences define deployment workflows.

Conceptually:

```text
Start
 |
 v
Partition Disk
 |
 v
Apply Operating System
 |
 v
Install Drivers
 |
 v
Join Domain
 |
 v
Install Applications
 |
 v
Apply Configuration
 |
 v
Finish
```

---

# Why Task Sequences Matter

Task sequences can execute:

```text
Commands
PowerShell
Scripts
Applications
Configuration Actions
Domain Join Operations
```

They therefore deserve careful security review.

---

# Task Sequence Files

Task sequence configuration is represented in the deployment share.

Important locations include:

```text
Control
```

and subdirectories associated with task sequence IDs.

Do not modify task sequence XML during an assessment.

---

# Enumerate Task Sequences

A basic read-only approach is:

```powershell
Get-ChildItem '\\MDT01\DeploymentShare$\Control' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'TaskSequence|ts.xml|Unattend.xml'
    } |
    Select-Object FullName
```

---

# TaskSequences.xml

The deployment share may contain:

```text
Control\TaskSequences.xml
```

which can provide metadata about available task sequences.

Review for:

```text
Task Sequence ID
Name
Description
Enabled State
```

---

# Task Sequence Subdirectories

Individual task sequences can have associated configuration beneath:

```text
Control\<TaskSequenceID>\
```

Potential files can include:

```text
ts.xml
Unattend.xml
```

depending on deployment design.

---

# Unattend.xml

Windows unattended-installation files deserve careful review.

Potentially sensitive settings may involve:

```text
Local Accounts
Domain Join
Product Configuration
Scripts
First Logon Commands
Auto Logon
```

---

# Search Unattend Files

```powershell
Get-ChildItem '\\MDT01\DeploymentShare$' -Recurse -Filter 'Unattend.xml' -ErrorAction SilentlyContinue |
    Select-Object FullName
```

Then review only the files required for the assessment.

---

# Credential Search in XML

For authorised offline copies:

```powershell
Select-String -Path '.\Unattend.xml' -Pattern 'Password','Credentials','Domain','Username'
```

Some unattended passwords may use encoded or protected representations depending on configuration.

Do not assume an encoded value is securely encrypted.

---

# Application Deployment

MDT can install applications during operating-system deployment.

The:

```text
Applications
```

directory may therefore contain:

```text
Installers
Scripts
Configuration Files
Response Files
License Files
```

---

# Application Security Review

Look for:

```text
Hard-Coded Credentials
API Keys
Connection Strings
Unattended Install Passwords
Writable Scripts
Writable Installers
```

Do not execute deployment applications during discovery.

---

# Deployment Script Security

Scripts can run with elevated deployment context.

Therefore:

```text
Writable Script
      |
      v
Deployment
      |
      v
Target System
```

may become security relevant.

The actual impact depends on:

```text
Who Can Modify It
Whether It Is Used
Which Task Sequence Uses It
Execution Context
Target Systems
```

---

# Share Permission vs NTFS Permission

SMB security depends on both:

```text
Share Permission
```

and:

```text
NTFS Permission
```

Effective access is constrained by both layers.

See:

[Windows and Active Directory Shares](shares.md)

---

# Review Share Permissions

On the MDT server:

```powershell
Get-SmbShareAccess -Name 'DeploymentShare$'
```

---

# Review NTFS Permissions

```powershell
Get-Acl 'D:\DeploymentShare' |
    Format-List Owner,AccessToString
```

Use the actual deployment-share path.

---

# Broad Read Access

Some deployment architectures intentionally permit broad read access to deployment content.

Whether this is acceptable depends on what the share contains.

If the share includes:

```text
Reusable Credentials
Sensitive Scripts
Private Keys
Configuration Secrets
```

broad read access can become a significant issue.

---

# Broad Write Access

Write access is generally more security sensitive.

Conceptually:

```text
Low-Privilege User
       |
       v
Write Deployment Script
       |
       v
Task Sequence
       |
       v
Managed Computer
```

Do not modify a production script to prove the path.

Permission evidence and task-sequence references may be sufficient.

---

# Safe Write-Permission Validation

Prefer inspecting ACLs:

```powershell
Get-SmbShareAccess -Name 'DeploymentShare$'
```

and:

```powershell
Get-Acl 'D:\DeploymentShare'
```

If actual write testing is required, use a dedicated approved test directory rather than a production task-sequence or application directory.

---

# Effective Permission Analysis

A finding should identify:

```text
Principal
    |
    v
Share Permission
    +
NTFS Permission
    |
    v
Writable Object
    |
    v
Deployment Reference
    |
    v
Affected Systems
```

---

# Deployment Share Credentials

Legacy MDT environments are especially worth checking for configuration such as:

```ini
UserID=
UserDomain=
UserPassword=
```

and:

```ini
DomainAdmin=
DomainAdminDomain=
DomainAdminPassword=
```

The property names do not guarantee that values are populated.

---

# Search Bootstrap.ini

```powershell
Select-String -Path '\\MDT01\DeploymentShare$\Control\Bootstrap.ini' -Pattern 'UserID','UserDomain','UserPassword'
```

---

# Search CustomSettings.ini

```powershell
Select-String -Path '\\MDT01\DeploymentShare$\Control\CustomSettings.ini' -Pattern 'DomainAdmin','Password','JoinDomain','MachineObjectOU'
```

---

# Credential Validation

If a credential is discovered, do not immediately attempt authentication across the domain.

First determine:

```text
Account Exists?
Account Enabled?
Account Purpose?
Account Privilege?
Authorised Validation Target?
```

Use the minimum authentication necessary to confirm the issue.

---

# Password Reuse

A deployment account becomes significantly more dangerous if its password is reused by:

```text
Local Administrator Accounts
Service Accounts
Other Deployment Accounts
Administrative Accounts
```

Do not perform broad password spraying with discovered credentials.

Validate only within approved scope.

---

# Local Administrator Credentials

Deployment processes may configure local accounts.

Review:

```text
Unattend.xml
Scripts
CustomSettings.ini
Application Scripts
```

for local account creation.

---

# LAPS

Modern environments should use appropriate local administrator password management rather than static deployment passwords.

See:

[LAPS](laps.md)

---

# Deployment Account Hardening

A deployment-share access account should ideally have:

```text
Read-Only Share Access
No Interactive Logon
No RDP
No Local Administrator Rights
No Domain Administrator Rights
Restricted Network Access
```

unless additional permissions are operationally required.

---

# Domain Join Account Hardening

A domain join identity should ideally have:

```text
Only Required Computer Object Rights
Only Required OUs
No Domain Admin
No Server Administrator Rights
No Interactive Logon
No Unnecessary Network Access
```

---

# Delegated Domain Join

Instead of:

```text
Domain Admin
```

use delegated rights on a specific OU.

Example architecture:

```text
MDT Join Account
       |
       v
Workstations OU
       |
       v
Create Computer Objects
```

---

# OU Security

Review the target OU:

```powershell
Get-Acl 'AD:\OU=Workstations,DC=corp,DC=example'
```

Interpret the resulting ACEs carefully.

See:

[ACL and ACE](acl-ace.md)

---

# MDT and Active Directory

MDT commonly interacts with AD through:

```text
Domain Join
DNS
SMB
Service Accounts
Group Policy
Computer Objects
```

It may therefore expose indirect Active Directory privilege paths.

---

# Example Attack Path

```text
Domain User
    |
    v
Read Deployment Share
    |
    v
Recover Deployment Credential
    |
    v
Credential Has Excessive Rights
    |
    v
Privileged Access
```

The weakness is not simply:

```text
MDT
```

It is:

```text
Credential Exposure
+
Excessive Credential Privilege
```

---

# Example Integrity Path

```text
Domain User
    |
    v
Write Deployment Script
    |
    v
Task Sequence Uses Script
    |
    v
Privileged Deployment Context
    |
    v
Managed Systems
```

Again, validate permissions and references rather than modifying production deployment logic.

---

# MDT and Tier 0

Determine whether MDT is used to deploy:

```text
Domain Controllers
Certificate Authorities
ADFS Servers
Administrative Workstations
Identity Servers
```

If so, deployment infrastructure may require Tier 0-equivalent protection.

---

# Tier 0 Model

```text
MDT Administrator
      |
      v
Deployment Content
      |
      v
Tier 0 System
      |
      v
Identity Infrastructure
```

---

# Deployment Server Local Administrators

Review:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

on the authorised MDT server.

Determine whether broad domain groups have administrative access.

---

# Service Enumeration

On a suspected deployment server:

```powershell
Get-Service |
    Where-Object {
        $_.Name -match 'WDS|Deployment' -or
        $_.DisplayName -match 'Deployment'
    }
```

MDT itself does not necessarily run as a single dedicated Windows service.

---

# Installed Software

Check installed applications:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Where-Object {
        $_.DisplayName -match 'Deployment Toolkit'
    } |
    Select-Object DisplayName,DisplayVersion,Publisher
```

Also check the 32-bit registry view where relevant:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Where-Object {
        $_.DisplayName -match 'Deployment Toolkit'
    } |
    Select-Object DisplayName,DisplayVersion,Publisher
```

---

# MDT Installation Directory

A commonly encountered MDT installation path is:

```text
C:\Program Files\Microsoft Deployment Toolkit
```

Check:

```powershell
Test-Path 'C:\Program Files\Microsoft Deployment Toolkit'
```

---

# Deployment Workbench Snap-In

MDT administration historically uses Microsoft Management Console components and PowerShell modules installed with the toolkit.

Do not assume management tooling is installed on every deployment-related server.

---

# MDT PowerShell

MDT includes PowerShell functionality for deployment administration.

Because MDT is retired and environments may contain different releases, inspect locally available commands rather than assuming a specific module version.

Example discovery:

```powershell
Get-Module -ListAvailable |
    Where-Object {
        $_.Name -match 'MDT'
    }
```

---

# MDT Provider

MDT administration historically provides a PowerShell provider that can expose deployment-share objects.

Use:

```powershell
Get-PSProvider
```

after the appropriate MDT module has been loaded.

Do not modify provider objects during initial assessment.

---

# Configuration Database

MDT can optionally use a database for deployment configuration.

Conceptually:

```text
MDT
 |
 v
SQL Database
 |
 v
Deployment Rules
```

Not every deployment uses this functionality.

---

# MDT Database Security

If an MDT database exists, review:

```text
SQL Server
Authentication
Database Permissions
Service Accounts
Network Exposure
Connection Strings
```

---

# Database Credentials

Configuration required to connect to an MDT database may appear in deployment rules.

Review:

```text
Database Server
Instance
Database Name
Authentication Method
```

Do not assume a password is required if Windows authentication is used.

---

# SQL Security Model

```text
Windows PE / MDT
        |
        v
SQL Server
        |
        v
Deployment Database
```

Network access to SQL should be restricted to systems that require it.

---

# MDT and Applications

Application installers may include:

```text
MSI
EXE
PowerShell
Batch Files
Configuration Files
Transforms
```

Assess both:

```text
Confidentiality
```

and:

```text
Integrity
```

of deployment content.

---

# Installer Integrity

An important question is:

```text
Who Can Replace the Installer?
```

Example:

```text
Application
   |
   v
setup.exe
   |
   v
Task Sequence
   |
   v
Managed Device
```

If unauthorised users can replace:

```text
setup.exe
```

the deployment path may be compromised.

---

# Hash Evidence

When reviewing sensitive deployment files, record hashes without modifying them.

PowerShell:

```powershell
Get-FileHash '\\MDT01\DeploymentShare$\Applications\App1\setup.exe' -Algorithm SHA256
```

Linux:

```bash
sha256sum setup.exe
```

---

# Script Integrity

For deployment scripts:

```powershell
Get-FileHash '\\MDT01\DeploymentShare$\Scripts\CustomDeploy.ps1' -Algorithm SHA256
```

Hashing provides useful evidence while preserving file content.

---

# MDT and PowerShell

Deployment scripts may use PowerShell extensively.

Review for:

```text
Credentials
Encoded Configuration
Network Paths
Download Locations
Execution Policy Changes
Security Control Changes
Domain Operations
```

The presence of PowerShell is normal and is not itself a finding.

---

# MDT and Command Files

Also inspect relevant:

```text
.cmd
.bat
.vbs
.wsf
.ps1
.xml
.ini
```

files.

Prioritise files referenced by active task sequences.

---

# ZTIGather

MDT includes scripts that gather deployment properties and process deployment rules.

This can expose useful information about how deployment settings are resolved.

Do not modify MDT's built-in scripts during assessment.

---

# BDD.log

MDT deployments generate logs that can contain valuable operational information.

A commonly encountered log is:

```text
BDD.log
```

Depending on deployment phase, logs may exist in temporary or persistent MDT log locations.

---

# MDT Logs

Logs can reveal:

```text
Server Names
Share Paths
Task Sequence Actions
Applications
Errors
Usernames
Domain Information
Deployment Properties
```

Treat collected deployment logs as potentially sensitive.

---

# Credential Logging

Do not assume MDT intentionally logs plaintext passwords.

However, custom scripts and poorly designed deployment automation may write sensitive values into logs.

Search authorised log copies carefully.

---

# Log Search

```powershell
Select-String -Path '.\BDD.log' -Pattern 'password','credential','username','domain'
```

False positives are expected.

---

# MDT and Windows PE Logs

During deployment, logs may initially exist in Windows PE and later be copied to the deployed operating system.

Exact paths vary according to deployment phase and configuration.

Use Microsoft's deployment troubleshooting documentation for the specific environment.

---

# Captures Directory

Deployment shares may contain a:

```text
Captures
```

directory for captured operating-system images.

Images can contain:

```text
Applications
Configuration
Files
Registry State
Local Accounts
Secrets Accidentally Included During Capture
```

Captured images should therefore be protected.

---

# Golden Images

An organisation may maintain reference or golden images.

A compromised image can create:

```text
Persistent Supply Chain Risk
```

because every system deployed from that image may inherit the modification.

---

# Image Security Model

```text
Reference Image
      |
      v
Deployment Share
      |
      v
Task Sequence
      |
      v
Many Systems
```

Protect:

```text
Image Creation
Image Storage
Image Modification
Image Approval
```

---

# Operating Systems Directory

The:

```text
Operating Systems
```

directory can contain imported Windows source files or operating-system images.

Ordinary domain users generally should not have modification rights unless there is a documented requirement.

---

# Driver Repository

The:

```text
Out-of-Box Drivers
```

directory contains imported drivers.

Drivers operate with significant privilege once installed.

Therefore driver-source integrity should also be protected.

---

# Driver Risk Model

```text
Driver Package
      |
      v
Deployment
      |
      v
Windows
      |
      v
Kernel
```

Do not modify production driver packages during testing.

---

# Packages

The:

```text
Packages
```

directory can contain Windows packages and related deployment content.

Review permissions and source integrity.

---

# USMT

MDT can integrate with:

```text
User State Migration Tool - USMT
```

for migration of user data.

Migration stores may contain sensitive user information.

Assess:

```text
Storage Location
Encryption
Permissions
Retention
```

where USMT is used.

---

# Deployment Share Backups

Backups of MDT infrastructure can be especially sensitive because they may preserve:

```text
Old Credentials
Old Scripts
Old Task Sequences
Old Boot Images
Historical Configuration
```

An organisation may have removed a password from the live deployment share while leaving it inside an old backup.

---

# Backup Discovery

Look for authorised evidence of:

```text
DeploymentShare.zip
MDT-Backup
OldDeploymentShare
Archive
Backup
```

Do not perform broad filesystem searches outside scope.

---

# Old Boot Media

Old:

```text
ISO
WIM
USB Media
```

can retain outdated deployment credentials.

Credential rotation should therefore consider historical deployment media.

---

# Credential Rotation After Exposure

If a deployment credential is exposed:

```text
Remove Credential
      |
      v
Rotate Password
      |
      v
Update MDT Configuration
      |
      v
Regenerate Boot Media
      |
      v
Replace PXE Images
      |
      v
Invalidate Old Media
```

Changing only:

```text
Bootstrap.ini
```

is not enough if old boot media still contains the previous credential.

---

# Regenerating Boot Media

After security-sensitive configuration changes, administrators should regenerate deployment boot images according to the supported deployment process.

This is an administrative remediation action, not a penetration-testing step.

---

# MDT and Credential Guard

Credential Guard protects credentials on running Windows systems.

It does not solve plaintext secrets intentionally embedded inside:

```text
Bootstrap.ini
CustomSettings.ini
Scripts
Unattend.xml
```

The problem must be fixed at the deployment architecture level.

---

# MDT and LAPS

Static local administrator passwords should be avoided.

Use modern Windows LAPS where appropriate.

See:

[LAPS](laps.md)

---

# MDT and gMSA

Where a Windows service requires a domain identity and supports managed service accounts, gMSA may reduce static-password management.

However, MDT deployment-share access and domain-join workflows do not automatically become suitable for gMSA simply because gMSA exists.

See:

[gMSA](gmsa.md)

---

# MDT and NTLM

SMB access to deployment shares may use:

```text
Kerberos
```

or:

```text
NTLM
```

depending on naming, authentication and environment configuration.

See:

[NTLM](ntlm.md)

---

# MDT and Kerberos

Using the server's proper domain name can facilitate Kerberos authentication.

Conceptually:

```text
Client
 |
 v
\\mdt01.corp.example\DeploymentShare$
 |
 v
CIFS Service
 |
 v
Kerberos
```

See:

[Kerberos](kerberos.md)

---

# IP Address vs Hostname

Connecting to SMB using:

```text
\\10.10.10.20\DeploymentShare$
```

can result in different authentication behaviour from:

```text
\\mdt01.corp.example\DeploymentShare$
```

because Kerberos service-ticket acquisition normally relies on service names.

Prefer proper DNS names in legitimate deployment architecture.

---

# SMB Signing

Review SMB signing on deployment infrastructure.

See:

[SMB](smb.md)

and:

[NTLM Relay](ntlm-relay.md)

Do not assume that MDT automatically creates a relay vulnerability.

---

# MDT and Network Segmentation

Deployment infrastructure should be reachable only from systems that require it.

A simplified model is:

```text
Deployment Clients
       |
       v
Firewall
       |
       v
MDT Server
```

Administrative access should be further restricted.

---

# Client vs Administrative Access

Separate:

```text
SMB Deployment Access
```

from:

```text
RDP
WinRM
Administrative SMB
SQL
Management Interfaces
```

where architecture permits.

---

# Deployment VLAN

Some organisations use dedicated deployment networks.

Example:

```text
Build VLAN
    |
    +--> PXE
    +--> DHCP
    +--> WDS
    +--> MDT
```

This can reduce exposure if properly segmented.

---

# PXE Network Exposure

Do not expose PXE services to network segments where they are unnecessary.

Review:

```text
User VLANs
Guest VLANs
Server VLANs
Wireless Networks
```

---

# MDT and Lateral Movement

Compromise of MDT infrastructure may provide relationships useful for lateral movement if deployment accounts or server privileges extend across the environment.

See:

[Lateral Movement](lateral-movement.md)

---

# MDT and Credential Access

MDT is particularly relevant to credential-access assessment because legacy deployment designs may intentionally store reusable credentials.

See:

[Credential Access](credential-access.md)

---

# MDT and Shares

Deployment shares are one of the central security components of MDT.

See:

[Windows and Active Directory Shares](shares.md)

---

# MDT and Group Policy

Group Policy may:

```text
Configure Deployment-Related Settings
Install Software
Configure Network Access
Delegate Administrative Behaviour
```

See:

[Group Policy](group-policy.md)

---

# MDT and ADIDNS

DNS is necessary for reliable deployment-share and domain-controller discovery.

See:

[Active Directory Integrated DNS](adidns.md)

---

# MDT and Trusts

Multi-domain environments may use deployment infrastructure across trust boundaries.

Conceptually:

```text
Domain A
   |
   v
MDT
   |
   v
Systems in Domain B
```

Assess:

```text
Trust Direction
Credential Scope
Share Access
Domain Join Rights
Administrative Reach
```

See:

[Trusts](trusts.md)

---

# Multi-Domain Credentials

Avoid using a single highly privileged credential for deployments across multiple domains.

This increases:

```text
Credential Exposure
Blast Radius
Cross-Domain Impact
```

---

# MDT and Configuration Manager

Some historical environments combine MDT functionality with Configuration Manager.

Where Configuration Manager is present, assess both technologies rather than treating MDT as an isolated deployment share.

See:

[Microsoft Configuration Manager - SCCM](sccm.md)

---

# MDT and WSUS

Deployment task sequences may also configure or interact with Windows Update infrastructure.

See:

[Windows Server Update Services - WSUS](wsus.md)

Do not assume the MDT server itself is the WSUS server.

---

# Common Security Weaknesses

Important MDT weaknesses can include:

```text
Plaintext Deployment Credentials
Overprivileged Domain Join Accounts
Broad Deployment Share Read Access
Broad Deployment Share Write Access
Writable Scripts
Writable Applications
Writable Task Sequence Content
Exposed Boot Images
Stale Deployment Credentials
Unprotected Backups
Overprivileged MDT Administrators
Insufficient Network Segmentation
Legacy Unsupported Deployment Architecture
```

---

# Plaintext Credentials

A classic deployment weakness is:

```text
Bootstrap.ini
      |
      v
UserPassword
```

or:

```text
CustomSettings.ini
      |
      v
DomainAdminPassword
```

The severity depends heavily on the affected account.

---

# Overprivileged Join Account

Example:

```text
MDT Join Account
      |
      v
Domain Admins
```

This is unnecessary for ordinary workstation domain joining and significantly increases impact if the credential is exposed.

---

# Writable Deployment Share

Example:

```text
Domain Users
      |
      v
Modify
      |
      v
DeploymentShare$
```

This deserves immediate review.

Determine which directories are writable and whether those files are referenced by active deployments.

---

# Writable Script

Example:

```text
Authenticated Users
       |
       v
Modify Deploy.ps1
       |
       v
Active Task Sequence
       |
       v
Deployment Clients
```

No production modification is necessary to demonstrate the path.

---

# Writable Application Installer

Example:

```text
Low-Privilege User
       |
       v
Replace setup.exe
       |
       v
Application Deployment
       |
       v
Managed Systems
```

Again, establish:

```text
Write Permission
+
Task Sequence Reference
+
Execution Context
```

without replacing the installer.

---

# Stale Credentials

Old deployment accounts may remain enabled after:

```text
Migration
Server Replacement
Task Sequence Retirement
MDT Retirement
```

Review whether discovered credentials are still required.

---

# Legacy Architecture

Because MDT is retired, continued use should be documented as an architectural lifecycle risk where appropriate.

Do not report retirement alone as:

```text
Critical Vulnerability
```

Instead assess:

```text
Operational Dependency
Support Status
Migration Plan
Security Controls
Exposure
```

---

# Safe Assessment Workflow

A low-impact MDT assessment can follow:

```text
Identify Infrastructure
       |
       v
Identify Deployment Share
       |
       v
Review Read Access
       |
       v
Review Configuration
       |
       v
Review Credentials
       |
       v
Review ACLs
       |
       v
Map Task Sequences
       |
       v
Map Affected Systems
       |
       v
Report
```

---

# Phase 1 - Discovery

Identify:

```text
MDT Server
Deployment Share
WDS
PXE
DNS
SCCM Integration
```

---

# Phase 2 - Read-Only Share Review

Inspect:

```text
Control
Scripts
Applications
Boot
```

Do not copy large operating-system images unnecessarily.

---

# Phase 3 - Configuration Review

Review:

```text
Bootstrap.ini
CustomSettings.ini
TaskSequences.xml
Unattend.xml
Custom Scripts
```

---

# Phase 4 - Credential Review

Identify potential:

```text
Deployment Credentials
Domain Join Credentials
Application Credentials
Database Credentials
```

Determine privilege before validation.

---

# Phase 5 - Permission Review

Assess:

```text
Share Permissions
NTFS Permissions
AD Delegation
Local Administrators
```

---

# Phase 6 - Integrity Analysis

Determine whether unauthorised identities can modify:

```text
Scripts
Applications
Task Sequences
Boot Images
Operating System Images
Drivers
```

---

# Phase 7 - Scope Analysis

Determine which systems use the affected deployment path.

Examples:

```text
Workstations
Servers
Domain Controllers
Privileged Workstations
```

---

# Phase 8 - Minimal Validation

Prefer:

```text
Read Access Evidence
ACL Evidence
Configuration Evidence
Task Sequence References
Account Privilege Evidence
```

over:

```text
Modifying Scripts
Replacing Installers
Changing Task Sequences
Booting Production PXE
```

---

# Phase 9 - Cleanup

Read-only testing usually requires no MDT cleanup.

If an explicitly authorised temporary test object was created:

```text
Remove Test Object
Verify Original State
Record Cleanup
```

---

# Evidence Collection

Useful evidence includes:

```text
Deployment Share UNC Path
Share ACL
NTFS ACL
Relevant Configuration Snippet
Task Sequence ID
Affected Account
Account Group Membership
Delegated OU Rights
Affected Device Population
File Hash
```

---

# Protect Credentials in Evidence

If a configuration contains:

```text
UserPassword=RealPassword
```

do not place the complete password in the report.

Use:

```text
UserPassword=[REDACTED]
```

Preserve enough information to demonstrate the issue.

---

# Screenshot Handling

Screenshots should avoid exposing:

```text
Passwords
Private Keys
Tokens
Personal Information
Unrelated Internal Data
```

---

# MDT Detection

Defensive monitoring should consider:

```text
Deployment Share Access
File Modifications
Administrative Logons
Task Sequence Changes
Boot Image Changes
Application Changes
Credential Use
Domain Join Activity
PXE Activity
```

---

# SMB Auditing

Where configured, Windows Security events such as:

```text
5140
5145
```

can provide visibility into SMB share access.

These events can help identify unusual access to:

```text
DeploymentShare$
```

---

# File-System Auditing

For particularly sensitive deployment files, consider auditing modifications to:

```text
Bootstrap.ini
CustomSettings.ini
Task Sequence XML
Deployment Scripts
Application Installers
Boot Images
```

Windows object-access auditing can generate:

```text
4663
```

when appropriately configured.

---

# Process Creation

On the MDT server, event:

```text
4688
```

can provide process-creation visibility when enabled.

Unexpected scripting or administrative tooling may deserve investigation.

---

# Logon Events

Relevant Windows Security events include:

```text
4624
4625
4648
4672
```

depending on activity and audit policy.

---

# Group Changes

Monitor changes to:

```text
Local Administrators
Deployment Administrative Groups
Domain Groups Controlling MDT
```

---

# Active Directory Computer Creation

Domain join activity results in computer-object creation or reuse.

Depending on auditing configuration, defenders can monitor:

```text
4741 - Computer account created
4742 - Computer account changed
4743 - Computer account deleted
```

Unexpected activity from a deployment account should be investigated.

---

# Domain Join Account Monitoring

A dedicated MDT join account should normally exhibit predictable behaviour.

Unexpected:

```text
Interactive Logon
RDP
PowerShell Remoting
General Server Administration
Access Outside Deployment OUs
```

may indicate misuse.

---

# Deployment Share Monitoring

A useful detection model is:

```text
File Change
    |
    v
Sensitive MDT Path?
    |
    +--> No --> Normal Monitoring
    |
    +--> Yes
           |
           v
     Authorised Administrator?
           |
           +--> Yes --> Validate Change
           |
           +--> No --> Investigate
```

---

# Boot Image Monitoring

Record hashes for production boot images.

Example:

```powershell
Get-FileHash 'D:\DeploymentShare\Boot\LiteTouchPE_x64.wim' -Algorithm SHA256
```

Unexpected changes should be investigated.

---

# Script Monitoring

Consider integrity monitoring for custom scripts used by active task sequences.

Example:

```powershell
Get-FileHash 'D:\DeploymentShare\Scripts\CustomDeploy.ps1' -Algorithm SHA256
```

---

# Application Integrity

High-value installers can also be monitored through:

```text
Hashing
Code Signing
Controlled Repository
Change Management
```

---

# MDT Hardening

A secure deployment architecture should include:

```text
Least Privilege
Protected Credentials
Restricted Share Access
Restricted Write Access
Protected Boot Media
Secure Domain Join
Network Segmentation
Integrity Monitoring
Lifecycle Management
```

---

# Remove Plaintext Credentials

Where possible, eliminate reusable plaintext credentials from:

```text
Bootstrap.ini
CustomSettings.ini
Scripts
Unattend.xml
```

Redesign the workflow rather than simply hiding the files.

---

# Minimise Deployment Account Privilege

Deployment-share accounts should not automatically receive:

```text
Local Administrator
Server Administrator
Domain Administrator
```

rights.

---

# Minimise Domain Join Rights

Delegate only the required computer-object permissions to the required OUs.

---

# Restrict Share Read Access

If deployment configuration contains sensitive information, restrict read access to systems and users that require it.

---

# Restrict Share Write Access

Only authorised deployment administrators should be able to modify production deployment content.

This includes:

```text
Control
Scripts
Applications
Operating Systems
Drivers
Boot
```

---

# Separate Read and Write Roles

Where practical:

```text
Deployment Clients
       |
       v
Read

Deployment Administrators
       |
       v
Modify
```

Do not grant clients write access simply because they require read access.

---

# Protect Boot Media

Control distribution of:

```text
ISO
WIM
USB
PXE Images
```

Retire old media after credential or configuration changes.

---

# Rotate Exposed Credentials

If credentials are found in deployment configuration:

```text
Rotate Credential
      |
      v
Reduce Privilege
      |
      v
Update Deployment Configuration
      |
      v
Regenerate Boot Media
      |
      v
Replace PXE Images
      |
      v
Remove Old Copies
```

---

# Protect Backups

Restrict access to:

```text
Deployment Share Backups
Old Server Backups
Boot Media Archives
Configuration Exports
```

---

# Protect MDT Administrators

Use:

```text
Dedicated Administrative Accounts
Least Privilege
Strong Authentication
Administrative Workstations
Monitoring
```

according to organisational requirements.

---

# Segment Deployment Infrastructure

Restrict:

```text
SMB
RDP
WinRM
SQL
PXE
Administrative Interfaces
```

to the systems and networks that require them.

---

# Protect DNS

Restrict unauthorised modification of deployment server DNS records.

See:

[Active Directory Integrated DNS](adidns.md)

---

# Secure SMB

Review:

```text
SMB Signing
NTLM Usage
Kerberos
Share Permissions
NTFS Permissions
```

See:

[SMB](smb.md)

---

# Secure PXE

Limit PXE availability to appropriate deployment networks.

Review:

```text
IP Helpers
DHCP
Boot Images
Deployment Access
Network Segmentation
```

---

# Protect Images

Use controlled processes for:

```text
Image Creation
Image Approval
Image Storage
Image Modification
```

---

# Protect Drivers

Restrict modification of deployment driver repositories.

Where possible, obtain drivers from trusted sources and validate signatures.

---

# Protect Applications

Maintain application installers in controlled repositories with:

```text
Restricted Write Access
Hash Validation
Code Signing
Change Control
```

---

# Monitor Configuration

Track changes to:

```text
Bootstrap.ini
CustomSettings.ini
Task Sequences
Unattend.xml
Scripts
Applications
Boot Images
```

---

# MDT Retirement Planning

Because MDT is retired, organisations still relying on it should create a migration plan.

A useful process is:

```text
Inventory MDT
    |
    v
Identify Dependencies
    |
    v
Identify Credentials
    |
    v
Identify Deployment Workflows
    |
    v
Select Replacement
    |
    v
Pilot Migration
    |
    v
Retire MDT
```

---

# Migration Security

Do not simply copy legacy weaknesses into the replacement platform.

For example:

```text
MDT
 |
 v
Plaintext Join Credential
 |
 v
Migration
 |
 v
New Platform
 |
 v
Same Plaintext Credential
```

is not a security improvement.

---

# Migration Review

During migration, review:

```text
Credentials
Task Sequences
Applications
Scripts
Drivers
Images
Domain Join
Local Administrator Management
Network Segmentation
Administrative Roles
```

---

# Decommissioning

When MDT is retired:

```text
Disable Deployment Workflows
      |
      v
Remove PXE Dependencies
      |
      v
Remove Deployment Shares
      |
      v
Rotate Credentials
      |
      v
Retire Service Accounts
      |
      v
Remove DNS Records
      |
      v
Remove Firewall Rules
      |
      v
Archive Securely
```

---

# Do Not Forget Old Credentials

Credential cleanup should include:

```text
Bootstrap.ini
CustomSettings.ini
Boot WIMs
ISO Files
USB Media
Backups
Old Deployment Servers
Documentation
Password Vault Entries
```

---

# Reporting MDT Findings

Do not report:

```text
MDT Exists
```

as a vulnerability.

Report the actual security weakness.

---

# Potential Findings

Examples include:

```text
Plaintext Domain Credential Stored in MDT Deployment Configuration
```

```text
MDT Domain Join Account Has Excessive Active Directory Privileges
```

```text
Low-Privilege Domain Users Can Modify MDT Deployment Scripts
```

```text
Broad Read Access Exposes MDT Deployment Credentials
```

```text
MDT Application Repository Is Writable by Unauthorised Users
```

```text
Legacy MDT Boot Images Contain Active Deployment Credentials
```

```text
MDT Deployment Infrastructure Managing Tier 0 Systems Is Insufficiently Protected
```

```text
Retired MDT Infrastructure Remains Operational Without Migration Plan
```

---

# Example Finding - Plaintext Credential

```text
Finding:
Plaintext Domain Credential Stored in MDT Deployment Configuration

Description:
The MDT deployment share contained a reusable domain credential within
deployment configuration accessible to domain users.

The password was present in configuration used by the deployment
environment.

The credential has been redacted from assessment evidence.

Impact:
A domain user able to access the deployment material may recover the
credential and authenticate as the associated account.

The resulting impact depends on the account's Active Directory,
network and local-system privileges.

Recommendation:
Remove reusable plaintext credentials from MDT deployment
configuration.

Rotate the exposed password and review the affected account for
unnecessary privileges.

Regenerate MDT boot media and PXE images after the credential has been
changed, and securely retire older copies containing the previous
credential.
```

---

# Example Finding - Overprivileged Join Account

```text
Finding:
MDT Domain Join Account Has Excessive Active Directory Privileges

Description:
The account used by MDT for domain-join operations had administrative
rights substantially exceeding those required to create computer
objects in the deployment OU.

Impact:
Exposure of the deployment credential could provide an attacker with
privileges unrelated to the account's intended domain-join function.

Recommendation:
Replace the current privilege assignment with narrowly delegated
computer-object permissions on only the organisational units required
for deployment.

The account should not be a Domain Administrator and should not have
unnecessary local-administrator or interactive-logon rights.
```

---

# Example Finding - Writable Deployment Script

```text
Finding:
Low-Privilege Users Can Modify an Active MDT Deployment Script

Description:
A script referenced by an active MDT task sequence was writable by a
broad domain group.

The assessment verified the share and NTFS permissions and confirmed
the script's task-sequence reference.

The production script was not modified.

Impact:
An attacker with write access could potentially alter deployment logic
executed during future operating-system deployments.

The resulting impact would depend on the task sequence execution
context and systems receiving the deployment.

Recommendation:
Restrict write access to MDT deployment content to dedicated deployment
administrators.

Review both SMB share permissions and NTFS permissions.

Implement change monitoring or integrity validation for scripts used by
production task sequences.
```

---

# Example Finding - Exposed Boot Media

```text
Finding:
Legacy MDT Boot Media Contains Active Deployment Credentials

Description:
An older MDT boot image remained accessible after deployment
configuration had changed.

Review of an authorised offline copy showed that it contained a
credential that remained valid in Active Directory.

Impact:
Anyone obtaining the legacy deployment media may be able to recover
the credential and use the access granted to that account.

Recommendation:
Rotate the affected credential.

Regenerate current deployment boot images and remove obsolete WIM,
ISO and removable-media copies.

Review backup locations and historical deployment servers for
additional copies of the exposed configuration.
```

---

# Example Finding - Broad Deployment Share Access

```text
Finding:
MDT Deployment Share Exposes Sensitive Configuration to Domain Users

Description:
The production MDT deployment share was readable by a broad domain
principal.

The share contained configuration and deployment material not required
by ordinary users, including sensitive deployment information.

Impact:
A compromised domain account could collect deployment configuration,
server information and potentially reusable credentials.

Recommendation:
Review whether broad read access is operationally required.

Restrict access to deployment systems and identities that require the
share, and remove reusable secrets from deployment content regardless
of filesystem permissions.
```

---

# Example Finding - Tier 0

```text
Finding:
MDT Infrastructure Managing Tier 0 Systems Is Insufficiently Protected

Description:
The same MDT infrastructure used for ordinary workstation deployment
was also capable of deploying or configuring Active Directory Tier 0
systems.

The deployment server and administrative model were not protected to a
comparable security level.

Impact:
Compromise of MDT administrative access or deployment content could
potentially affect security-critical identity infrastructure.

Recommendation:
Review whether Tier 0 systems should use the same deployment
infrastructure as ordinary endpoints.

Where MDT or its replacement manages Tier 0 systems, protect the
deployment platform, administrative identities, content repositories
and network paths to an equivalent security standard.
```

---

# MDT Assessment Checklist

## Discovery

- [ ] Identify MDT servers
- [ ] Identify deployment shares
- [ ] Identify WDS
- [ ] Identify PXE
- [ ] Identify DNS records
- [ ] Identify SCCM integration
- [ ] Identify deployment networks
- [ ] Identify active deployment workflows

## Deployment Share

- [ ] Identify UNC path
- [ ] Review share permissions
- [ ] Review NTFS permissions
- [ ] Review broad read access
- [ ] Review broad write access
- [ ] Identify hidden shares
- [ ] Identify backup shares

## Control

- [ ] Review `Bootstrap.ini`
- [ ] Review `CustomSettings.ini`
- [ ] Review `TaskSequences.xml`
- [ ] Review task sequence directories
- [ ] Review `Unattend.xml`
- [ ] Search for credentials
- [ ] Search for server paths
- [ ] Search for domain information

## Credentials

- [ ] Identify deployment-share account
- [ ] Identify domain-join account
- [ ] Identify application credentials
- [ ] Identify database credentials
- [ ] Determine account status
- [ ] Determine group membership
- [ ] Determine delegated rights
- [ ] Determine local-admin scope
- [ ] Check whether discovered credentials are still required
- [ ] Avoid broad authentication testing

## Domain Join

- [ ] Identify target domain
- [ ] Identify target OU
- [ ] Review delegated rights
- [ ] Confirm account is not Domain Admin
- [ ] Review interactive-logon rights
- [ ] Review network-logon scope
- [ ] Review account monitoring

## Task Sequences

- [ ] Enumerate active task sequences
- [ ] Identify referenced scripts
- [ ] Identify referenced applications
- [ ] Identify domain-join actions
- [ ] Identify custom commands
- [ ] Identify unattended files
- [ ] Review execution context
- [ ] Review write permissions

## Scripts

- [ ] Review PowerShell
- [ ] Review batch files
- [ ] Review command files
- [ ] Review VBScript
- [ ] Search for credentials
- [ ] Search for network paths
- [ ] Review write permissions
- [ ] Record hashes where useful

## Applications

- [ ] Identify installers
- [ ] Identify configuration files
- [ ] Review unattended installation files
- [ ] Review write permissions
- [ ] Review source integrity
- [ ] Record hashes where useful

## Boot Media

- [ ] Identify WIM files
- [ ] Identify ISO files
- [ ] Identify USB media
- [ ] Identify PXE boot images
- [ ] Review authorised offline copies
- [ ] Search for deployment configuration
- [ ] Identify stale credentials
- [ ] Remove obsolete media during remediation

## Operating System Images

- [ ] Identify production images
- [ ] Review modification rights
- [ ] Review image creation process
- [ ] Review storage permissions
- [ ] Review integrity controls
- [ ] Review old images

## Drivers

- [ ] Review driver repository permissions
- [ ] Review source trust
- [ ] Review signatures
- [ ] Restrict modification

## PXE

- [ ] Identify PXE-enabled networks
- [ ] Review WDS
- [ ] Review DHCP/IP helper architecture
- [ ] Determine whether unmanaged devices can boot
- [ ] Identify exposed boot images
- [ ] Review segmentation

## SQL

- [ ] Determine whether MDT database is used
- [ ] Identify SQL server
- [ ] Identify database
- [ ] Review authentication
- [ ] Review permissions
- [ ] Review network exposure
- [ ] Review connection configuration

## Active Directory

- [ ] Review domain join delegation
- [ ] Review computer-object permissions
- [ ] Review deployment groups
- [ ] Review deployment accounts
- [ ] Review Tier 0 relationships
- [ ] Review trust relationships where relevant

## Network

- [ ] Review SMB
- [ ] Review Kerberos
- [ ] Review NTLM
- [ ] Review SMB signing
- [ ] Review RDP exposure
- [ ] Review WinRM exposure
- [ ] Review SQL exposure
- [ ] Review PXE exposure
- [ ] Review segmentation

## Detection

- [ ] Monitor deployment share access
- [ ] Monitor deployment file changes
- [ ] Monitor task sequence changes
- [ ] Monitor application changes
- [ ] Monitor boot-image changes
- [ ] Monitor deployment account logons
- [ ] Monitor domain join activity
- [ ] Monitor local administrator changes
- [ ] Monitor server administrative logons

## Hardening

- [ ] Remove plaintext reusable credentials
- [ ] Rotate exposed credentials
- [ ] Minimise deployment account privilege
- [ ] Minimise domain join rights
- [ ] Restrict deployment-share read access
- [ ] Restrict deployment-share write access
- [ ] Protect scripts
- [ ] Protect applications
- [ ] Protect images
- [ ] Protect drivers
- [ ] Protect boot media
- [ ] Protect backups
- [ ] Segment MDT
- [ ] Secure SMB
- [ ] Secure PXE
- [ ] Monitor deployment integrity
- [ ] Plan MDT retirement

## Retirement

- [ ] Inventory MDT dependencies
- [ ] Identify replacement technology
- [ ] Migrate deployment workflows
- [ ] Remove plaintext credential dependencies
- [ ] Rotate MDT credentials
- [ ] Remove old deployment shares
- [ ] Remove old PXE images
- [ ] Remove obsolete boot media
- [ ] Disable unused accounts
- [ ] Remove obsolete DNS records
- [ ] Remove obsolete firewall rules
- [ ] Securely archive required historical data

## Reporting

- [ ] Do not report MDT presence alone
- [ ] Identify actual weakness
- [ ] Identify affected credential
- [ ] Identify affected task sequence
- [ ] Identify affected systems
- [ ] Identify privilege level
- [ ] Identify attack prerequisites
- [ ] Redact credentials
- [ ] Avoid modifying production deployments
- [ ] Provide migration-aware remediation

---

# MDT Testing Model

The basic model is:

```text
Administrator
      |
      v
MDT
      |
      v
Deployment Share
      |
      v
Task Sequence
      |
      v
Windows Client
```

The credential model is:

```text
Bootstrap.ini
      |
      v
Deployment Credential
      |
      v
Deployment Share
```

The domain join model is:

```text
Task Sequence
      |
      v
Domain Join Account
      |
      v
Delegated OU
      |
      v
Computer Object
```

The integrity model is:

```text
Principal
   |
   v
Write Permission
   |
   v
Deployment Content
   |
   v
Task Sequence
   |
   v
Managed System
```

The boot model is:

```text
PXE / ISO / USB
       |
       v
Windows PE
       |
       v
Bootstrap Configuration
       |
       v
Deployment Share
```

The image model is:

```text
Golden Image
     |
     v
Deployment
     |
     v
Many Systems
```

The Active Directory model is:

```text
MDT
 |
 v
Deployment Credential
 |
 v
Active Directory Rights
 |
 v
Security Impact
```

The Tier 0 model is:

```text
MDT
 |
 v
Tier 0 Deployment
 |
 v
Identity Infrastructure
```

The retirement model is:

```text
Legacy MDT
    |
    v
Inventory
    |
    v
Migration
    |
    v
Credential Rotation
    |
    v
Infrastructure Removal
```

The most important distinction is:

```text
MDT Presence
    !=
MDT Vulnerability
```

Another important distinction is:

```text
Readable Deployment Share
    !=
Automatic Domain Compromise
```

The actual path is:

```text
Read Access
    |
    v
Sensitive Material
    |
    v
Usable Credential / Configuration
    |
    v
Privilege
    |
    v
Impact
```

For integrity weaknesses:

```text
Write Access
    |
    v
Deployment Content
    |
    v
Active Deployment Reference
    |
    v
Execution Context
    |
    v
Affected Systems
```

For penetration testers:

```text
Do Not Ask:
"Can I modify this deployment?"

Ask:
"Can an unauthorised identity modify
deployment content that will be trusted
by managed systems?"
```

For defenders:

```text
Do Not Ask:
"Is the deployment share hidden?"

Ask:
"Who can read it, who can modify it,
what secrets does it contain, and what
systems trust its content?"
```

The complete model is:

```text
Identity
   |
   v
Deployment Access
   |
   +--> Read
   |      |
   |      v
   |   Credential Exposure
   |
   +--> Write
          |
          v
      Content Integrity
          |
          v
      Deployment
          |
          v
      Managed Systems
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Enumeration:

[Enumeration](enumeration.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Group Policy:

[Group Policy](group-policy.md)

MachineAccountQuota:

[MachineAccountQuota](machine-account-quota.md)

Credential Access:

[Credential Access](credential-access.md)

LAPS:

[LAPS](laps.md)

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

ADIDNS:

[Active Directory Integrated DNS](adidns.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

SCCM:

[Microsoft Configuration Manager - SCCM](sccm.md)

WSUS:

[Windows Server Update Services - WSUS](wsus.md)

AD CS:

[Active Directory Certificate Services](ad-cs/index.md)

The next infrastructure page is:

```text
docs/active-directory/scom.md
```

followed by:

```text
docs/active-directory/adfs.md
docs/active-directory/rodc.md
```

---

# References

## Microsoft - Microsoft Deployment Toolkit Retirement

[Microsoft Learn - Microsoft Deployment Toolkit Retirement](https://learn.microsoft.com/en-us/troubleshoot/mem/configmgr/mdt/mdt-retirement){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Deployment Resources

[Microsoft Learn - Windows Deployment](https://learn.microsoft.com/en-us/windows/deployment/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows PE

[Microsoft Learn - Windows PE](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-intro){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DISM Image Management

[Microsoft Learn - DISM Image Management Command-Line Options](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/dism-image-management-command-line-options-s14){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows Deployment Services

[Microsoft Learn - Windows Deployment Services](https://learn.microsoft.com/en-us/windows-server/administration/windows-deployment-services/windows-deployment-services){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft Learn - Windows LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Security

[Microsoft Learn - SMB Security Hardening](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security-hardening){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Group Policy

[Microsoft Learn - Group Policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Domain Services

[Microsoft Learn - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

MDT should be viewed as part of the Windows deployment trust chain.

The fundamental relationship is:

```text
Deployment Infrastructure
        |
        v
Deployment Content
        |
        v
Windows Installation
        |
        v
Managed System
```

The important security questions are:

```text
Who Can Read the Deployment Infrastructure?

Who Can Modify It?

What Credentials Does It Contain?

What Privileges Do Those Credentials Have?

Which Systems Trust the Deployment Content?
```

Legacy MDT environments deserve particular attention because reusable credentials may exist in:

```text
Bootstrap.ini
CustomSettings.ini
Unattend.xml
Scripts
Boot Images
Old Media
Backups
```

The credential path is:

```text
Deployment File
      |
      v
Credential
      |
      v
Account Privilege
      |
      v
Security Impact
```

The integrity path is:

```text
Write Permission
      |
      v
Deployment Content
      |
      v
Task Sequence
      |
      v
Managed System
```

The strongest assessment does not modify production deployment content.

Instead, establish:

```text
Permission
    +
Active Reference
    +
Execution Context
    +
Target Scope
    =
Demonstrated Risk
```

Because MDT is now retired, organisations still using it should also evaluate migration.

The objective should not simply be:

```text
Replace MDT
```

but:

```text
Remove Legacy Credential Exposure
        +
Preserve Least Privilege
        +
Protect Deployment Integrity
        +
Improve Administrative Separation
        +
Retire Old Infrastructure
```

The next infrastructure topic is:

```text
System Center Operations Manager - SCOM
```
