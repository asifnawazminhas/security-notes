# Active Directory Group Policy

Group Policy is one of the primary mechanisms used to centrally configure Windows users and computers in an Active Directory environment.

Administrators use Group Policy to manage settings such as:

```text
Security Policies
Windows Defender
Firewall Rules
User Rights
Local Group Membership
Registry Settings
Scripts
Software Deployment
Windows Update
PowerShell
Audit Policies
Credential Protection
Remote Access
Scheduled Tasks
Services
```

From a security perspective, Group Policy is important because control over a Group Policy Object (GPO), or control over where a GPO is linked, can potentially provide control over every user or computer affected by that policy.

A simplified model is:

```text
Active Directory
      |
      v
Group Policy Object
      |
      v
Organizational Unit
      |
      +--> User
      +--> User
      +--> Computer
      +--> Computer
```

An important attack-path model is:

```text
Controlled Principal
        |
        v
Control GPO
        |
        v
GPO Applied to OU
        |
        v
Privileged Computers
        |
        v
Potential Privilege Escalation
```

Another possible path is:

```text
Controlled Principal
        |
        v
Can Link GPO
        |
        v
Sensitive OU
        |
        v
Controlled GPO
        |
        v
Affected Systems
```

Group Policy testing therefore requires understanding several separate components:

```text
GPO
 +
GPO ACL
 +
GPO Link
 +
OU
 +
Inheritance
 +
Security Filtering
 +
SYSVOL
 +
Client Processing
 =
Effective Group Policy
```

!!! warning "Authorised testing only"
    Modifying Group Policy can affect large numbers of production systems and users. A single GPO change may result in scripts, scheduled tasks, registry settings, services, security settings, or other configuration being deployed throughout the environment. Prefer read-only enumeration and attack-path analysis. Only modify GPOs or GPO links where explicitly authorised, use dedicated test GPOs and test OUs where possible, record the complete original state, and restore all changes immediately after validation.

---

# What Is Group Policy?

Group Policy provides centralised configuration management for:

```text
Users
Computers
```

within an Active Directory environment.

A policy is stored in a:

```text
Group Policy Object
```

or:

```text
GPO
```

A GPO can then be linked to:

```text
Site
Domain
Organizational Unit
```

Conceptually:

```text
GPO
 |
 v
Linked Container
 |
 v
Users / Computers
 |
 v
Policy Processing
 |
 v
Configuration Applied
```

---

# Group Policy Architecture

A Group Policy Object consists of two major components:

```text
Group Policy Object
       |
       +--> Group Policy Container
       |
       +--> Group Policy Template
```

These are commonly abbreviated:

```text
GPC
GPT
```

Understanding this distinction is essential during security testing.

---

# Group Policy Container

The:

```text
Group Policy Container
```

is stored in Active Directory.

It contains directory-side information about the GPO.

Conceptually:

```text
Active Directory
      |
      v
CN=Policies
      |
      v
GPO Object
```

The GPC contains information such as:

```text
GPO GUID
Display Name
Version Information
Extension Information
GPO Status
Directory ACL
```

---

# Group Policy Template

The:

```text
Group Policy Template
```

is stored in:

```text
SYSVOL
```

Conceptually:

```text
\\corp.example\SYSVOL
        |
        v
corp.example
        |
        v
Policies
        |
        v
{GPO-GUID}
```

The GPT contains policy files used by Group Policy client-side extensions.

---

# GPO Dual-Component Model

The complete GPO therefore looks like:

```text
              GPO
               |
       +-------+-------+
       |               |
       v               v
      GPC             GPT
       |               |
       v               v
Active Directory     SYSVOL
```

Security analysis should consider both.

---

# SYSVOL

SYSVOL is a domain-wide replicated share hosted by domain controllers.

Typical UNC path:

```text
\\corp.example\SYSVOL
```

Policies are commonly located under:

```text
\\corp.example\SYSVOL\corp.example\Policies\
```

Each GPO normally has a GUID-based directory:

```text
{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
```

Example:

```text
\\corp.example\SYSVOL\corp.example\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}
```

---

# Default Domain Policy

A normal Active Directory domain contains:

```text
Default Domain Policy
```

This policy commonly contains domain-wide security settings.

The well-known GPO GUID is:

```text
{31B2F340-016D-11D2-945F-00C04FB984F9}
```

Do not modify the Default Domain Policy during routine penetration testing.

---

# Default Domain Controllers Policy

Active Directory also normally contains:

```text
Default Domain Controllers Policy
```

with the well-known GUID:

```text
{6AC1786C-016F-11D2-945F-00C04FB984F9}
```

This policy affects the Domain Controllers OU by default.

Control of this policy would be extremely security-sensitive.

Do not actively modify it during routine validation.

---

# GPO Identification

A GPO has:

```text
Display Name
GUID
Distinguished Name
File-System Path
Version
Owner
ACL
```

Example:

```text
Display Name:
Server Security Policy

GUID:
{11111111-2222-3333-4444-555555555555}

AD Object:
CN={11111111-2222-3333-4444-555555555555},
CN=Policies,
CN=System,
DC=corp,
DC=example

SYSVOL:
\\corp.example\SYSVOL\corp.example\Policies\
{11111111-2222-3333-4444-555555555555}
```

---

# Group Policy Processing

Group Policy follows the general processing order:

```text
Local
  |
  v
Site
  |
  v
Domain
  |
  v
Organizational Unit
```

This is commonly remembered as:

```text
LSDOU
```

---

# LSDOU

The basic order is:

```text
Local
 |
 v
Site
 |
 v
Domain
 |
 v
OU
 |
 v
Child OU
```

Policies processed later can override conflicting settings from policies processed earlier, depending on the policy setting and configuration.

---

# Simplified Processing Example

```text
Local Policy
      |
      v
Domain Policy
      |
      v
Workstations OU Policy
      |
      v
Engineering OU Policy
```

A computer in:

```text
OU=Engineering,
OU=Workstations,
DC=corp,
DC=example
```

may therefore receive settings from multiple GPOs.

---

# GPO Links

Creating a GPO does not automatically apply it to users or computers.

The GPO must normally be linked to a:

```text
Site
Domain
OU
```

Example:

```text
Server Security GPO
        |
        v
Servers OU
        |
        +--> SERVER01
        +--> SERVER02
        +--> SERVER03
```

---

# gpLink

Active Directory containers can contain the:

```text
gPLink
```

attribute.

This attribute identifies linked GPOs.

Conceptually:

```text
OU
 |
 v
gPLink
 |
 +--> GPO A
 +--> GPO B
```

---

# gpOptions

The:

```text
gPOptions
```

attribute can contain Group Policy inheritance-related configuration for a container.

This is relevant when determining effective GPO application.

---

# Link Order

Multiple GPOs may be linked to the same container.

Example:

```text
Servers OU
 |
 +--> Baseline Policy
 |
 +--> Firewall Policy
 |
 +--> Server Admin Policy
```

Link order can affect precedence.

Do not infer effective policy merely from the presence of a link.

---

# Enforced Links

A GPO link can be configured as:

```text
Enforced
```

Historically this was referred to as:

```text
No Override
```

An enforced GPO has stronger inheritance behaviour and can affect how conflicting lower-level policies are processed.

---

# Block Inheritance

An OU can be configured to:

```text
Block Inheritance
```

Conceptually:

```text
Domain GPO
    |
    v
Parent OU
    |
    X
Block Inheritance
    |
    v
Child OU
```

However, enforced links can interact differently with blocked inheritance.

Effective policy should therefore be determined rather than assumed.

---

# Security Filtering

A linked GPO does not necessarily apply to every principal inside the linked container.

Security filtering can restrict application.

Conceptually:

```text
GPO
 |
 v
Linked to Servers OU
 |
 +--> SERVER01
 +--> SERVER02
 +--> SERVER03
```

but:

```text
Security Filtering:
Web Servers
```

may restrict which systems actually process the GPO.

---

# Apply Group Policy Permission

GPO application depends on permissions including the ability to:

```text
Read
```

the GPO and:

```text
Apply Group Policy
```

Security filtering therefore needs to be considered during attack-path analysis.

---

# WMI Filters

GPOs can also be associated with:

```text
WMI Filters
```

These allow policy application to depend on system properties.

Example concept:

```text
GPO
 |
 v
WMI Filter
 |
 +--> Windows Server?
 |
 +--> OS Version?
 |
 +--> Hardware Property?
 |
 v
Apply / Do Not Apply
```

Therefore:

```text
GPO Linked to OU
```

does not always mean:

```text
GPO Applies to Every Object
```

---

# Computer Configuration

GPOs can contain:

```text
Computer Configuration
```

settings.

These affect computer objects and the operating system.

Examples include:

```text
Security Settings
Services
Registry
Firewall
Scripts
Scheduled Tasks
Software
Audit Policy
Local Groups
User Rights
```

---

# User Configuration

GPOs can also contain:

```text
User Configuration
```

settings.

Examples include:

```text
Desktop Settings
Registry Settings
Scripts
Drive Mappings
Application Settings
Security Restrictions
```

---

# Computer vs User Impact

When analysing a GPO, determine:

```text
Does it contain:
    Computer settings?
    User settings?
    Both?
```

A GPO linked to an OU containing computers may be highly significant if it contains computer-side administrative configuration.

---

# Group Policy Preferences

Group Policy Preferences extend Group Policy with additional configuration capabilities.

Examples include:

```text
Local Users and Groups
Scheduled Tasks
Services
Registry
Drive Maps
Files
Folders
Environment Variables
Data Sources
Printers
Shortcuts
```

Preferences are especially important during security assessments because they may expose credentials or provide privileged configuration paths.

---

# Group Policy Preferences Files

Relevant XML files may appear inside SYSVOL under paths such as:

```text
Machine\Preferences\
User\Preferences\
```

Potential directories include:

```text
Groups
Services
ScheduledTasks
Drives
DataSources
Printers
```

---

# Historical GPP Password Exposure

Older Group Policy Preferences could store passwords using the:

```text
cpassword
```

attribute.

Example concept:

```xml
<User
    name="localadmin"
    cpassword="[ENCRYPTED_VALUE]"
/>
```

Microsoft published the AES key used for this mechanism, making stored `cpassword` values recoverable.

This is why historical GPP password files remain important during Active Directory assessments.

A dedicated Credential Access page should cover:

```text
GPP Passwords
```

in detail.

---

# Search SYSVOL for cpassword

Read-only search from Windows:

```cmd
findstr /S /I "cpassword" \\corp.example\SYSVOL\corp.example\Policies\*.xml
```

PowerShell:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL\corp.example\Policies' \
    -Recurse \
    -Filter '*.xml' \
    -ErrorAction SilentlyContinue |
    Select-String \
        -Pattern 'cpassword'
```

This is a read-only discovery technique.

---

# Search SYSVOL from Linux

Where SMB access is authorised, SYSVOL can be reviewed from Linux using SMB tooling.

For example, using Impacket:

```bash
impacket-smbclient 'corp.example/alice:<PASSWORD>@dc01.corp.example'
```

Then inspect:

```text
SYSVOL
```

For broader SMB enumeration, see:

[Impacket](impacket.md)

and:

[NetExec](netexec.md)

---

# GPO Scripts

Group Policy can configure:

```text
Startup Scripts
Shutdown Scripts
Logon Scripts
Logoff Scripts
```

Conceptually:

```text
GPO
 |
 v
Startup Script
 |
 v
Computer
 |
 v
Execution During Startup
```

A writable script used by privileged systems can create a significant security issue.

---

# Script Security Model

```text
GPO
 |
 v
Script Path
 |
 v
Writable by Attacker?
 |
 +--> No -> Normal
 |
 +--> Yes
       |
       v
Potential Script Modification
       |
       v
Execution on GPO Targets
```

The critical question is therefore not only:

```text
Who can modify the GPO?
```

but also:

```text
Who can modify resources referenced by the GPO?
```

---

# External Script Paths

A GPO may reference scripts stored outside the GPO's own SYSVOL directory.

Example:

```text
\\fileserver\scripts\startup.ps1
```

If the referenced file or directory is writable by an untrusted principal:

```text
GPO
 |
 v
Trusted Script Path
 |
 v
Weak File ACL
 |
 v
Script Modification
 |
 v
Execution on Targets
```

This can create an indirect Group Policy attack path.

---

# Scheduled Tasks

Group Policy Preferences can deploy scheduled tasks.

Conceptually:

```text
GPO
 |
 v
Scheduled Task
 |
 v
Target Computer
 |
 v
Configured Security Context
 |
 v
Command
```

If an attacker controls a GPO applied to privileged computers, scheduled-task configuration may provide a potential code-execution primitive.

This is highly intrusive and should not normally be used for routine production validation.

---

# Services

Group Policy Preferences can configure services.

Conceptually:

```text
GPO
 |
 v
Service Configuration
 |
 v
Target Computer
```

Security impact depends on:

```text
Service Account
Executable Path
Permissions
Startup Type
Target Systems
```

---

# Registry Settings

Group Policy can modify registry settings.

This makes GPO control powerful even without directly deploying scripts.

Examples include configuration related to:

```text
Security Controls
Authentication
Remote Management
Application Behaviour
Windows Defender
Firewall
Credential Protection
```

Changing security-related registry configuration on production systems is intrusive.

---

# Local Users and Groups

Group Policy can manage local group membership.

For example:

```text
CORP\Server Admins
        |
        v
Local Administrators
        |
        v
Production Servers
```

This can be implemented using:

```text
Restricted Groups
```

or Group Policy Preferences depending on the environment.

---

# Restricted Groups

Restricted Groups can centrally manage membership of security groups.

A common use is controlling:

```text
Local Administrators
```

on domain-joined systems.

During an assessment, identify which domain groups are placed into local privileged groups through GPOs.

---

# GPO to Local Administrator Path

Example:

```text
CORP\Server Admins
        |
        v
GPO
        |
        v
Servers OU
        |
        v
Local Administrators
        |
        v
SERVER01
SERVER02
SERVER03
```

This relationship can explain lateral-movement paths found in BloodHound.

---

# Enumerating GPOs with PowerShell

The GroupPolicy PowerShell module provides native enumeration.

List all GPOs:

```powershell
Get-GPO -All
```

Useful output:

```powershell
Get-GPO -All |
    Select-Object \
        DisplayName,
        Id,
        GpoStatus,
        CreationTime,
        ModificationTime,
        Owner
```

---

# Enumerate a Specific GPO

```powershell
Get-GPO \
    -Name 'Server Security Policy'
```

or by GUID:

```powershell
Get-GPO \
    -Guid '{11111111-2222-3333-4444-555555555555}'
```

---

# Generate a GPO Report

HTML:

```powershell
Get-GPOReport \
    -Name 'Server Security Policy' \
    -ReportType Html \
    -Path '.\server-security-policy.html'
```

XML:

```powershell
Get-GPOReport \
    -Name 'Server Security Policy' \
    -ReportType Xml \
    -Path '.\server-security-policy.xml'
```

This is extremely useful during read-only assessment.

---

# Report All GPOs

```powershell
Get-GPOReport \
    -All \
    -ReportType Html \
    -Path '.\all-gpos.html'
```

For machine-readable analysis:

```powershell
Get-GPOReport \
    -All \
    -ReportType Xml \
    -Path '.\all-gpos.xml'
```

---

# Enumerate GPO Links

The GroupPolicy module can query inheritance for a target container.

Example:

```powershell
Get-GPInheritance \
    -Target 'OU=Servers,DC=corp,DC=example'
```

This can reveal:

```text
GPO Links
Inherited GPOs
Blocked Inheritance
Link Order
Enforcement
```

---

# Enumerate Domain-Level Inheritance

```powershell
Get-GPInheritance \
    -Target 'DC=corp,DC=example'
```

---

# Resultant Set of Policy

The most useful question is often not:

```text
Which GPOs exist?
```

but:

```text
Which policies actually apply?
```

Windows provides Resultant Set of Policy capabilities.

---

# gpresult

On Windows:

```cmd
gpresult /r
```

This provides a summary of applied Group Policy.

For detailed HTML output:

```cmd
gpresult /h gpresult.html
```

---

# Computer-Specific gpresult

From an elevated command prompt:

```cmd
gpresult /scope computer /v
```

User policy:

```cmd
gpresult /scope user /v
```

---

# RSOP

Another native mechanism is:

```cmd
rsop.msc
```

This provides a graphical Resultant Set of Policy view.

During assessments, `gpresult` is often easier to capture as evidence.

---

# Get-GPResultantSetOfPolicy

PowerShell can generate Resultant Set of Policy reports.

Example:

```powershell
Get-GPResultantSetOfPolicy \
    -ReportType Html \
    -Path '.\rsop.html'
```

Availability and remote-query requirements depend on the environment and permissions.

---

# Enumerate GPOs Through Active Directory

GPO directory objects are located beneath:

```text
CN=Policies,
CN=System,
DC=corp,
DC=example
```

PowerShell:

```powershell
Get-ADObject \
    -SearchBase 'CN=Policies,CN=System,DC=corp,DC=example' \
    -LDAPFilter '(objectClass=groupPolicyContainer)' \
    -Properties displayName,gPCFileSysPath,versionNumber |
    Select-Object \
        DisplayName,
        Name,
        gPCFileSysPath,
        versionNumber,
        DistinguishedName
```

---

# Enumerate with ldapsearch

Linux:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'CN=Policies,CN=System,DC=corp,DC=example' \
    '(objectClass=groupPolicyContainer)' \
    displayName \
    name \
    gPCFileSysPath \
    versionNumber
```

---

# Enumerate OU GPO Links with LDAP

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(objectClass=organizationalUnit)' \
    distinguishedName \
    gPLink \
    gPOptions
```

This provides a useful read-only mapping of:

```text
OU -> GPO Links
```

---

# PowerView

PowerView includes functions for Group Policy enumeration.

Common functions include:

```powershell
Get-DomainGPO
```

List GPOs:

```powershell
Get-DomainGPO
```

Specific GPO:

```powershell
Get-DomainGPO \
    -Identity 'Server Security Policy'
```

Exact behaviour can differ between PowerView versions.

Always check:

```powershell
Get-Help Get-DomainGPO -Full
```

---

# Get-DomainGPOLocalGroup

PowerView can help identify local-group modifications configured through GPO.

Where supported:

```powershell
Get-DomainGPOLocalGroup
```

This can help answer:

```text
Which GPOs modify local groups?
```

Check the installed PowerView version:

```powershell
Get-Help Get-DomainGPOLocalGroup -Full
```

---

# Get-DomainGPOUserLocalGroupMapping

Some PowerView versions expose:

```powershell
Get-DomainGPOUserLocalGroupMapping
```

This can help determine whether a user receives local-group privileges through Group Policy.

Check:

```powershell
Get-Help Get-DomainGPOUserLocalGroupMapping -Full
```

before use.

---

# Get-DomainGPOComputerLocalGroupMapping

Where supported:

```powershell
Get-DomainGPOComputerLocalGroupMapping
```

can assist with mapping GPO-controlled local administrative relationships to computers.

Again, verify syntax against the loaded PowerView version.

---

# GPO ACL Enumeration

The security of a GPO depends heavily on its ACL.

Native approach:

```powershell
$gpo = Get-GPO \
    -Name 'Server Security Policy'

$gpo.Id
```

Then locate its Active Directory object:

```powershell
$guid = $gpo.Id.Guid

$gpoObject = Get-ADObject \
    -Identity "CN={$guid},CN=Policies,CN=System,DC=corp,DC=example"
```

Review the ACL:

```powershell
(Get-Acl "AD:\$($gpoObject.DistinguishedName)").Access |
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

# Get-GPPermission

The GroupPolicy module provides:

```powershell
Get-GPPermission
```

Example:

```powershell
Get-GPPermission \
    -Name 'Server Security Policy' \
    -All
```

This provides a higher-level view of GPO permissions.

---

# GPO Permission Types

Depending on context and tooling, permissions may be represented using concepts such as:

```text
GpoRead
GpoApply
GpoEdit
GpoEditDeleteModifySecurity
```

The exact underlying directory and SYSVOL rights should be considered when analysing unusual cases.

---

# GPO Owners

Enumerate owners:

```powershell
Get-GPO -All |
    Select-Object \
        DisplayName,
        Owner
```

Unexpected ownership should be investigated.

---

# GPO ACL Security Model

```text
Principal
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
Affected Objects
```

The security impact depends on all parts of the chain.

---

# GPO Control Is Not Automatically Domain Compromise

Suppose:

```text
Alice
 |
 v
Can Edit
 |
 v
Printer Configuration GPO
```

If that GPO applies only to:

```text
Low-Privilege Kiosk Computers
```

the impact may be limited.

Compare:

```text
Alice
 |
 v
Can Edit
 |
 v
Domain Controllers Policy
 |
 v
Domain Controllers
```

The second relationship is vastly more significant.

Therefore:

```text
GPO Control
     +
GPO Scope
     +
Target Privilege
     =
Security Impact
```

---

# Who Can Edit GPOs?

During an assessment, identify principals with rights such as:

```text
Edit
Edit Settings
Modify Security
Delete
GenericAll
GenericWrite
WriteDACL
WriteOwner
```

over GPO objects.

Then determine:

```text
Where is the GPO linked?
```

---

# GPO Attack Path

A generic attack path is:

```text
Controlled User
      |
      v
Can Edit GPO
      |
      v
GPO
      |
      v
Linked OU
      |
      v
Computers
      |
      v
Potential Code Execution
```

---

# GPO Attack Path Through Group Membership

```text
Alice
 |
 v
MemberOf
 |
 v
GPO Editors
 |
 v
Can Edit
 |
 v
Server Policy
 |
 v
Servers OU
 |
 v
Production Servers
```

The group relationship is part of the attack path.

See:

[Active Directory Groups](groups.md)

---

# GPO Attack Path Through ACL

```text
Alice
 |
 v
GenericAll
 |
 v
Server Policy
 |
 v
Servers OU
 |
 v
SERVER01
SERVER02
SERVER03
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# WriteDACL over GPO

A principal with:

```text
WriteDACL
```

over a GPO may potentially grant itself additional GPO rights.

Conceptually:

```text
Alice
 |
 v
WriteDACL
 |
 v
GPO
 |
 v
Grant Edit Rights
 |
 v
Modify GPO
```

This is an indirect control path.

---

# WriteOwner over GPO

Similarly:

```text
Alice
 |
 v
WriteOwner
 |
 v
GPO
 |
 v
Become Owner
 |
 v
Modify DACL
 |
 v
Grant Edit Rights
 |
 v
Control GPO
```

The stages should be documented separately.

---

# GPO Link Control

Control over a GPO and control over GPO linking are separate privileges.

A principal may have:

```text
No Control over GPO
```

but:

```text
Control over OU gPLink
```

This can still become security-relevant if the principal also controls another suitable GPO.

---

# WriteGPLink

BloodHound may represent the ability to modify Group Policy links using a relationship such as:

```text
WriteGPLink
```

Conceptually:

```text
Alice
 |
 v
WriteGPLink
 |
 v
Servers OU
```

This means the OU's GPO-link configuration deserves investigation.

---

# WriteGPLink Attack Model

```text
Controlled Principal
        |
        v
Control GPO Link
        |
        +
Control Suitable GPO
        |
        v
Link GPO to Sensitive OU
        |
        v
Affected Systems
```

Do not report `WriteGPLink` alone as arbitrary code execution.

The complete prerequisites must be analysed.

---

# OU Control

If a principal controls an OU, determine whether the control includes:

```text
gPLink
gPOptions
Child Objects
Inherited Permissions
```

The exact ACE determines what can actually be changed.

---

# BloodHound

BloodHound is extremely useful for identifying GPO relationships.

Conceptually:

```text
User
 |
 v
GPO Control
 |
 v
GPO
 |
 v
GPLink
 |
 v
OU
 |
 v
Contains
 |
 v
Computer
```

This transforms GPO permissions into attack paths.

---

# BloodHound GPO Relationships

Depending on BloodHound version and data, relevant relationships can include concepts such as:

```text
GpLink
Contains
GenericAll
GenericWrite
WriteDacl
WriteOwner
Owns
WriteGPLink
```

The exact available edges depend on BloodHound version and collection.

---

# BloodHound Workflow

```text
Mark Controlled Principals
        |
        v
Review Outbound Control
        |
        v
Identify GPO Rights
        |
        v
Identify GPO Links
        |
        v
Identify Affected OUs
        |
        v
Identify Computers / Users
        |
        v
Determine Resulting Privilege
```

---

# High-Value GPO Targets

Prioritise GPOs linked to:

```text
Domain Controllers
Tier 0 Servers
Identity Infrastructure
Certificate Authorities
Management Servers
Backup Servers
Virtualisation Platforms
Production Servers
Administrator Workstations
```

---

# GPO Names Are Not Sufficient

A GPO named:

```text
Wallpaper Policy
```

could contain more than wallpaper settings.

Likewise:

```text
Security Baseline
```

may not apply to sensitive systems.

Always inspect:

```text
Actual Settings
Links
ACLs
Security Filtering
```

---

# Orphaned GPOs

A GPO may exist without any links.

Conceptually:

```text
GPO
 |
 X
No Active Link
```

This is commonly referred to as an:

```text
Unlinked GPO
```

An unlinked GPO may still matter if:

```text
It can later be linked
It contains sensitive data
It has weak permissions
It is used by automation
```

but its current direct impact may be lower.

---

# Identify Unlinked GPOs

PowerShell can compare:

```text
All GPOs
```

against:

```text
GPO Links
```

Rather than assuming an unlinked policy is harmless, determine why it exists and who controls it.

---

# Disabled GPO Sections

A GPO can have:

```text
Computer Configuration Disabled
User Configuration Disabled
All Settings Disabled
```

depending on GPO status.

Enumerate:

```powershell
Get-GPO -All |
    Select-Object \
        DisplayName,
        GpoStatus
```

A disabled section affects practical exploitability.

---

# GPO Versioning

GPOs maintain version information for:

```text
Computer Configuration
User Configuration
```

Clients use version information when determining whether policy processing is required.

This is important when investigating GPO changes.

---

# GPT.ini

Inside the Group Policy Template, a file named:

```text
GPT.ini
```

contains version-related information.

Example location:

```text
\\corp.example\SYSVOL\corp.example\Policies\
{GPO-GUID}\GPT.ini
```

---

# Replication

Group Policy depends on replication of:

```text
Active Directory GPC
```

and:

```text
SYSVOL GPT
```

across domain controllers.

This means changes may not become visible everywhere immediately.

During testing, do not repeatedly modify a GPO simply because one DC has not yet reflected the change.

---

# SYSVOL Permissions

Review permissions on:

```text
SYSVOL
```

and individual GPO directories.

Conceptually:

```text
GPO AD Object
       |
       +
SYSVOL Directory
       |
       v
Effective GPO Control
```

Unexpected file-system write access may be security-sensitive even if the AD-side ACL appears restrictive.

---

# Search for Writable GPO Content

During an authorised assessment, determine whether controlled principals have write access to relevant policy files.

Do not modify files merely to test writability where ACL inspection is sufficient.

A safe model is:

```text
Inspect ACL
    |
    v
Identify Write Permission
    |
    v
Map File to GPO
    |
    v
Map GPO to Targets
```

---

# SYSVOL Script Review

Search for script types such as:

```text
.ps1
.bat
.cmd
.vbs
.js
.wsf
```

PowerShell:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL\corp.example' \
    -Recurse \
    -Include *.ps1,*.bat,*.cmd,*.vbs,*.js,*.wsf \
    -ErrorAction SilentlyContinue
```

Review scripts for:

```text
Credentials
Secrets
Writable Dependencies
Insecure Paths
Network Shares
Legacy Commands
Sensitive Configuration
```

---

# Search for Potential Secrets

Read-only search:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL\corp.example' \
    -Recurse \
    -File \
    -ErrorAction SilentlyContinue |
    Select-String \
        -Pattern 'password|passwd|pwd|secret|token|apikey|cpassword' \
        -CaseSensitive:$false \
        -ErrorAction SilentlyContinue
```

Treat matches as candidates requiring manual review.

Do not assume every occurrence is a credential.

---

# Group Policy and Credentials

Potential credential exposure sources include:

```text
GPP cpassword
Scripts
Configuration Files
Mapped Drive Credentials
Scheduled Task Configuration
Service Configuration
Legacy Deployment Scripts
```

Credential findings should be handled according to the engagement's evidence policy.

---

# Group Policy and Machine Account Quota

GPO control and Machine Account Quota are separate Active Directory concepts.

However, they can participate in larger attack paths involving:

```text
Computer Objects
Delegation
RBCD
ACLs
```

Machine Account Quota should therefore be assessed separately.

---

# Group Policy and LAPS

Group Policy historically played an important role in deploying and configuring Microsoft LAPS.

Modern Windows LAPS also uses policy configuration.

Review:

```text
Who controls LAPS-related GPOs?
```

because weakening password-management policy can increase credential risk.

A dedicated LAPS page should cover the complete security model.

---

# Group Policy and Defender

GPOs may centrally configure Microsoft Defender.

Examples include:

```text
Real-Time Protection
Exclusions
Cloud Protection
Attack Surface Reduction
Controlled Folder Access
```

Control over security-product GPOs can therefore be highly sensitive.

During production testing, do not disable security controls merely to demonstrate GPO edit access.

---

# Group Policy and Firewall

Windows Defender Firewall configuration may be controlled through GPO.

A compromised firewall GPO could potentially alter network exposure across many systems.

Again:

```text
Ability to Modify GPO
```

can normally be demonstrated without actually weakening firewall rules.

---

# Group Policy and Audit Policy

Advanced audit policy can be centrally managed through GPO.

Control of audit-policy GPOs may allow security visibility to be reduced.

This increases the significance of GPOs applied to:

```text
Domain Controllers
Servers
Privileged Workstations
```

---

# Group Policy and PowerShell

GPOs can influence PowerShell security and logging configuration.

Examples include:

```text
Script Block Logging
Module Logging
Transcription
Execution Policy
```

Do not confuse:

```text
Execution Policy
```

with a security boundary.

However, control over PowerShell logging policies may affect detection visibility.

---

# Group Policy and WinRM

GPOs can configure:

```text
Windows Remote Management
```

and associated firewall or service settings.

This can affect lateral-movement opportunities.

---

# Group Policy and RDP

GPOs may control:

```text
Remote Desktop
User Rights
Firewall Rules
Local Group Membership
```

These can determine who can remotely access systems.

---

# Group Policy and User Rights

GPOs can assign user rights such as:

```text
Log on locally
Log on as a service
Log on as a batch job
Access this computer from the network
Back up files and directories
Restore files and directories
Debug programs
Impersonate a client after authentication
```

These rights can be highly security-sensitive.

---

# User Rights Assignment Analysis

A useful model is:

```text
GPO
 |
 v
User Right
 |
 v
Group
 |
 v
Members
 |
 v
Affected Systems
```

Example:

```text
Server Baseline GPO
       |
       v
SeBackupPrivilege
       |
       v
Backup Operators
       |
       v
Production Servers
```

---

# Group Policy and Local Administrators

One of the most important GPO relationships is:

```text
GPO
 |
 v
Local Group Membership
 |
 v
Administrators
 |
 v
Domain Group
```

This can reveal why a domain group has administrative access across many systems.

---

# GPO Attack Surface

A complete GPO attack-surface review should consider:

```text
GPO ACL
GPO Owner
SYSVOL ACL
GPO Links
OU ACL
Security Filtering
WMI Filtering
Referenced Scripts
Referenced Shares
Local Group Configuration
Scheduled Tasks
Services
Registry
Security Controls
Credentials
```

---

# Safe GPO Validation

Group Policy is a high-impact administrative mechanism.

A safe validation hierarchy is:

```text
Level 1
Read-Only Enumeration

Level 2
ACL Confirmation

Level 3
Attack-Path Confirmation

Level 4
Dedicated Test GPO / Test OU

Level 5
Production GPO Modification
```

Use the lowest level that proves the issue.

---

# Level 1 - Read-Only Enumeration

Collect:

```text
GPO Name
GUID
Owner
ACL
Links
Target OUs
Security Filtering
Settings
```

This may already prove excessive control.

---

# Level 2 - ACL Confirmation

Confirm the suspected permission using:

```text
Get-GPPermission
```

and/or:

```text
Get-Acl AD:\...
```

This provides independent evidence.

---

# Level 3 - Attack-Path Confirmation

Map:

```text
Controlled Principal
       |
       v
GPO Permission
       |
       v
GPO
       |
       v
OU
       |
       v
Privileged Systems
```

BloodHound plus native evidence may be sufficient.

---

# Level 4 - Dedicated Test GPO

Where active validation is required, prefer:

```text
Dedicated Test User
       |
       v
Dedicated Test GPO
       |
       v
Dedicated Test OU
       |
       v
Dedicated Test Computer
```

This avoids production-wide impact.

---

# Level 5 - Production Modification

Production GPO modification should only occur when:

```text
Explicitly Required
       +
Explicitly Authorised
       +
Rollback Prepared
       +
Affected Systems Understood
```

In many penetration tests this level is unnecessary.

---

# Do Not Use Production Code Execution as Default Proof

If:

```text
Alice
 |
 v
Can Edit GPO
 |
 v
GPO Applied to Domain Controllers
```

has been independently confirmed, it is generally unnecessary to:

```text
Deploy Script
       |
       v
Wait for DC
       |
       v
Execute as SYSTEM
```

merely to prove severity.

The attack path itself may already demonstrate the risk.

---

# Evidence

For every GPO finding record:

```text
Source Principal
Source SID
GPO Name
GPO GUID
GPO Owner
GPO ACL
Permission
GPO Status
GPO Links
Link Order
Enforced Status
Security Filtering
WMI Filter
Affected OU
Affected Users
Affected Computers
Target Privilege
SYSVOL Path
SYSVOL Permissions
Validation Performed
```

---

# Example Evidence

```text
Source:
CORP\helpdesk-user

GPO:
Production Server Baseline

GUID:
{11111111-2222-3333-4444-555555555555}

Permission:
GpoEdit

Linked To:
OU=Production Servers,DC=corp,DC=example

Affected Computers:
SERVER01
SERVER02
SERVER03

Security Filtering:
Authenticated Users

Impact:
The source account can modify a GPO applied to production servers.

Validation:
GPO permissions, GPO links, affected computer objects, and effective
scope were confirmed using read-only directory queries. The production
GPO was not modified.
```

---

# Detection

Group Policy monitoring should combine:

```text
Directory Changes
      +
SYSVOL Changes
      +
GPO Version Changes
      +
OU Link Changes
      +
Security Filtering Changes
      +
Endpoint Policy Processing
```

---

# Event 5136

Where Directory Service Changes auditing is configured:

```text
5136
```

can record modifications to Active Directory objects.

Relevant changes may include:

```text
GPO Objects
gPLink
gPOptions
GPO ACL-Related Attributes
```

depending on auditing configuration.

---

# GPO Link Change Detection

A suspicious sequence may be:

```text
5136
 |
 v
gPLink Modified
 |
 v
New GPO Linked
 |
 v
Sensitive OU
```

This deserves investigation.

---

# GPO Object Change Detection

Conceptually:

```text
GPO Object Changed
      |
      v
Unexpected Principal
      |
      v
Sensitive GPO
      |
      v
Potential Policy Modification
```

Directory audit events should be correlated with SYSVOL changes.

---

# Event 5145

Where detailed file-share auditing is appropriately configured:

```text
5145
```

may provide information about access to network share objects.

This can assist with investigation of SYSVOL activity, depending on audit configuration and event volume.

---

# SYSVOL Monitoring

Monitor changes beneath:

```text
SYSVOL\<domain>\Policies
```

especially for:

```text
Scripts
XML Files
Registry Policy Files
Scheduled Task Definitions
Group Preference Files
GPT.ini
```

---

# GPO Version Changes

Unexpected changes to GPO version information can indicate policy modification.

Baseline:

```text
GPO
 |
 +--> Last Modified
 |
 +--> Version
 |
 +--> Modifier
```

and alert on unexpected changes to sensitive GPOs.

---

# Group Policy Operational Logs

Windows provides Group Policy operational logging that can assist with troubleshooting and investigations.

Relevant logs can be found beneath:

```text
Applications and Services Logs
    |
    v
Microsoft
    |
    v
Windows
    |
    v
GroupPolicy
```

These logs can help determine:

```text
Which GPOs were processed?
Was processing successful?
Which extensions ran?
Were errors encountered?
```

---

# Detection Chain - GPO Abuse

A potential chain is:

```text
Directory / SYSVOL Change
        |
        v
GPO Version Change
        |
        v
Client Policy Refresh
        |
        v
New Configuration
        |
        v
Process / Service / Task Activity
```

Correlating these layers improves detection confidence.

---

# Detection Chain - GPO Link Abuse

```text
5136
 |
 v
gPLink Changed
 |
 v
Sensitive OU
 |
 v
Policy Processing
 |
 v
Endpoint Configuration Change
```

---

# Detection Chain - Group Membership Deployment

```text
GPO Changed
    |
    v
Local Group Preference
    |
    v
Policy Refresh
    |
    v
New Local Administrator
    |
    v
Privileged Authentication
```

---

# Baseline Sensitive GPOs

Maintain a baseline for GPOs controlling:

```text
Domain Controllers
Authentication
Audit Policy
Defender
Firewall
LAPS
Local Administrators
PowerShell Logging
WinRM
RDP
Certificate Services
Privileged Workstations
Tier 0 Systems
```

---

# Hardening

The GPO defensive model is:

```text
Inventory
   |
   v
Classify
   |
   v
Restrict Editors
   |
   v
Protect Links
   |
   v
Protect SYSVOL
   |
   v
Monitor Changes
   |
   v
Review Regularly
```

---

# Inventory GPOs

Maintain:

```text
GPO Name
GUID
Purpose
Owner
Editors
Links
Security Filtering
WMI Filter
Affected Tier
Last Review
```

Unidentified or undocumented GPOs should be investigated.

---

# Assign GPO Owners

Every security-sensitive GPO should have a clear administrative and business owner.

The owner should understand:

```text
Why the GPO exists
Where it applies
Who can edit it
What security controls it manages
```

---

# Restrict GPO Editors

Avoid large general-purpose groups with GPO edit permissions.

Prefer:

```text
Dedicated GPO Administrators
```

with:

```text
Least Privilege
Separate Administrative Accounts
Strong Authentication
Privileged Workstations
```

---

# Protect Tier 0 GPOs

GPOs applied to Tier 0 should be treated as Tier 0 assets.

Examples:

```text
Domain Controllers Policy
PKI Server Policy
Identity Management Policy
Privileged Access Workstation Policy
```

Principals that can modify these GPOs may effectively possess Tier 0 influence.

---

# Protect OU Link Permissions

Review who can modify:

```text
gPLink
```

and related OU configuration.

A tightly protected GPO can still become part of an attack path if an attacker can manipulate where controlled GPOs are linked.

---

# Protect SYSVOL

Review SYSVOL permissions.

Avoid writable paths where:

```text
Low-Privilege Principal
        |
        v
Modify Trusted Script
        |
        v
Execution on Privileged Systems
```

---

# Protect Referenced Resources

If GPOs reference:

```text
Scripts
Executables
MSI Packages
Configuration Files
Network Shares
```

review the permissions on those resources.

A secure GPO pointing to an insecure resource can still be exploitable.

---

# Minimise GPO Editors

Regularly review:

```text
Who can edit?
Who can delete?
Who can modify security?
Who owns the GPO?
Who can link it?
```

Remove stale administrative access.

---

# Separate Creation from Linking

Where operationally practical, separate:

```text
GPO Creation / Editing
```

from:

```text
GPO Linking
```

This can reduce the impact of a single compromised administrative role.

---

# Avoid Shared Administrative Accounts

GPO changes should be attributable to individual administrators.

Avoid shared identities such as:

```text
gpo-admin
domain-admin
it-admin
```

where accountability is lost.

---

# Use Change Management

Security-sensitive GPO modifications should follow:

```text
Request
 |
 v
Approval
 |
 v
Change
 |
 v
Validation
 |
 v
Monitoring
```

Unexpected changes should be investigated.

---

# Backup GPOs

Maintain recoverable backups of important GPOs.

PowerShell supports:

```powershell
Backup-GPO
```

Example:

```powershell
Backup-GPO \
    -Name 'Server Security Policy' \
    -Path 'C:\GPOBackups'
```

Backups themselves should be protected because they may contain sensitive configuration.

---

# Do Not Store Secrets in GPO Scripts

Avoid:

```text
Passwords
API Keys
Tokens
Private Keys
Database Credentials
```

inside:

```text
Scripts
XML Files
Registry Preferences
Configuration Files
```

stored in SYSVOL.

SYSVOL is intentionally readable by broad sets of domain users in many environments.

---

# Group Policy Review Frequency

High-value GPOs should be reviewed regularly.

Review:

```text
Owner
Editors
Links
Security Filtering
Settings
SYSVOL ACL
Referenced Files
Last Modification
```

---

# Incident Response

If Group Policy abuse is suspected:

```text
GPO Change Detected
        |
        v
Identify GPO
        |
        v
Identify Modifier
        |
        v
Determine Changed Settings
        |
        v
Identify Links
        |
        v
Identify Affected Systems
        |
        v
Inspect SYSVOL
        |
        v
Review Endpoint Activity
        |
        v
Contain Identity
        |
        v
Restore Known-Good GPO
        |
        v
Force / Await Safe Policy Refresh
        |
        v
Hunt for Persistence
```

---

# Do Not Blindly Restore

Before reverting a GPO:

```text
Capture Current State
       |
       v
Determine Malicious Change
       |
       v
Determine Legitimate Concurrent Changes
       |
       v
Restore Correct State
```

Blind restoration may overwrite legitimate administrative changes.

---

# Incident Evidence

Capture:

```text
GPO Name
GUID
Current Version
Previous Version
Modification Time
GPO ACL
Owner
GPO Links
SYSVOL Files
File Hashes
Relevant Directory Events
Relevant Share Events
Group Policy Operational Logs
Affected Systems
Processes / Tasks / Services Created
```

---

# Persistence Through Group Policy

Group Policy can provide persistence because configuration may repeatedly apply to systems.

Conceptually:

```text
Malicious GPO Setting
       |
       v
Policy Refresh
       |
       v
Configuration Applied
       |
       v
Administrator Removes Local Change
       |
       v
Next Policy Refresh
       |
       v
Configuration Returns
```

Therefore incident response must identify the:

```text
Policy Source
```

rather than only removing the endpoint artefact.

---

# Group Policy Refresh

Windows periodically refreshes Group Policy.

Administrators can also request a refresh using:

```cmd
gpupdate
```

For example:

```cmd
gpupdate /force
```

During testing, do not force policy refresh across production systems without approval.

---

# Troubleshooting

Common GPO-assessment issues include:

```text
GPO Exists but Does Not Apply
GPO Linked to Wrong OU
Security Filtering Excludes Target
WMI Filter Excludes Target
Computer Configuration Disabled
User Configuration Disabled
Block Inheritance
Link Precedence
Replication Delay
DNS Problems
SYSVOL Problems
Permission Problems
Stale Authentication Token
```

---

# GPO Exists but Does Not Apply

Check:

```text
Link
Security Filtering
WMI Filter
GPO Status
Inheritance
Target Object Location
```

Then verify using:

```cmd
gpresult /r
```

---

# Wrong OU

Determine the computer's distinguished name:

```powershell
Get-ADComputer \
    -Identity 'SERVER01' |
    Select-Object DistinguishedName
```

Example:

```text
CN=SERVER01,
OU=Production,
OU=Servers,
DC=corp,
DC=example
```

Then inspect GPO inheritance for the relevant OU.

---

# Replication Delay

If a GPO was legitimately changed:

```text
DC01
 |
 v
Change
 |
 v
AD / SYSVOL Replication
 |
 v
DC02
DC03
```

Clients contacting different DCs may temporarily observe different states.

---

# DNS

Group Policy depends heavily on healthy Active Directory DNS.

Verify:

```cmd
nslookup corp.example
```

and:

```cmd
nltest /dsgetdc:corp.example
```

where appropriate.

---

# SYSVOL Availability

Check:

```text
\\corp.example\SYSVOL
```

and:

```text
\\corp.example\NETLOGON
```

from the affected system.

---

# Reporting

Possible finding titles include:

```text
Low-Privilege Account Can Modify Security-Sensitive Group Policy Object
```

```text
Excessive Group Policy Permissions Enable Privilege Escalation
```

```text
Group Policy Link Permissions Enable Control of Sensitive Systems
```

```text
Writable SYSVOL Script Enables Code Execution on Domain Systems
```

```text
Group Policy Preferences Expose Reusable Credentials
```

```text
Excessive GPO Permissions Affect Tier 0 Systems
```

```text
Insecure Group Policy Delegation Enables Administrative Access
```

---

# Report the Actual Attack Path

Avoid:

```text
User Can Edit GPO
```

Prefer:

```text
CORP\helpdesk-user
        |
        v
GpoEdit
        |
        v
Production Server Baseline
        |
        v
Linked to Production Servers OU
        |
        v
27 Production Servers
        |
        v
Potential SYSTEM-Level Configuration
```

This communicates the actual impact.

---

# Example Finding

```text
Finding:
Low-Privilege Account Can Modify Group Policy Applied to Production Servers

Affected Principal:
CORP\helpdesk-user

Affected GPO:
Production Server Baseline

GPO GUID:
{11111111-2222-3333-4444-555555555555}

Permission:
GpoEdit

Linked Container:
OU=Production Servers,DC=corp,DC=example

Affected Systems:
27 production Windows servers

Description:
The CORP\helpdesk-user account has permission to edit the Production
Server Baseline Group Policy Object.

The GPO is linked to the Production Servers OU and applies computer-side
configuration to production Windows servers.

Control of the GPO could allow a principal with the affected account to
modify security-sensitive computer configuration across systems within
the GPO's effective scope.

The GPO permission, link, security filtering, and affected computer
objects were independently confirmed using read-only Active Directory
and Group Policy queries.

The production GPO was not modified during validation.

Impact:
Successful abuse could result in unauthorised configuration changes
across production servers.

Depending on the settings introduced, this could potentially enable
administrative code execution, security-control weakening, credential
access, persistence, or lateral movement.

Recommendation:
Remove the unnecessary GPO edit permission from CORP\helpdesk-user.

Restrict modification of the affected GPO to dedicated administrative
identities, review the GPO's complete ACL and owner, review permissions
on the associated SYSVOL directory, verify all GPO links and security
filters, and monitor future modifications to the GPO and its linked
containers.
```

---

# Severity Assessment

Severity depends on:

```text
Source Principal
      +
GPO Permission
      +
GPO Settings
      +
GPO Scope
      +
Affected Systems
      +
Affected Privilege
      =
Actual Risk
```

Questions include:

```text
Is the source low privileged?

Can the source edit settings?

Can the source modify security?

Can the source modify GPO links?

Is the GPO currently linked?

Is computer configuration enabled?

Which OU receives the policy?

How many systems are affected?

Are Domain Controllers affected?

Are Tier 0 systems affected?

Does security filtering limit scope?

Is a WMI filter present?

Can referenced scripts be modified?

Can the path be exploited without user interaction?
```

---

# Evidence Checklist

Record:

```text
Source Principal
Source SID
GPO Display Name
GPO GUID
GPO DN
GPO Owner
GPO Permission
GPO Status
Creation Time
Modification Time
GPO Version
SYSVOL Path
SYSVOL ACL
GPO Links
Link Order
Enforced Status
Block Inheritance
Security Filtering
WMI Filter
Affected OUs
Affected Users
Affected Computers
Affected Tier
Relevant Settings
Referenced Scripts
Referenced Resources
Validation Performed
Original State
Final State
Timestamp
```

---

# Group Policy Assessment Checklist

## Preparation

- [ ] Confirm GPO enumeration is authorised
- [ ] Confirm whether GPO modification is permitted
- [ ] Confirm whether GPO link modification is permitted
- [ ] Identify GPOs that must never be modified
- [ ] Identify Tier 0 OUs
- [ ] Identify test GPO
- [ ] Identify test OU
- [ ] Identify test computer
- [ ] Confirm rollback requirements

## Enumeration

- [ ] Enumerate all GPOs
- [ ] Record GPO GUIDs
- [ ] Record GPO owners
- [ ] Record GPO status
- [ ] Record modification times
- [ ] Enumerate GPO links
- [ ] Enumerate link order
- [ ] Identify enforced links
- [ ] Identify blocked inheritance
- [ ] Enumerate security filtering
- [ ] Enumerate WMI filters
- [ ] Identify unlinked GPOs
- [ ] Enumerate affected OUs
- [ ] Enumerate affected computers
- [ ] Enumerate affected users

## GPO Permissions

- [ ] Review GPO ACLs
- [ ] Review `GpoEdit`
- [ ] Review modify-security permissions
- [ ] Review `GenericAll`
- [ ] Review `GenericWrite`
- [ ] Review `WriteDACL`
- [ ] Review `WriteOwner`
- [ ] Review GPO owner
- [ ] Identify inherited permissions
- [ ] Identify unexpected editors

## OU Permissions

- [ ] Review `gPLink`
- [ ] Review `gPOptions`
- [ ] Review `WriteGPLink`
- [ ] Review OU `GenericAll`
- [ ] Review OU `GenericWrite`
- [ ] Review OU `WriteDACL`
- [ ] Review OU `WriteOwner`
- [ ] Identify who can link GPOs to sensitive OUs

## SYSVOL

- [ ] Enumerate GPO directories
- [ ] Review SYSVOL permissions
- [ ] Review GPO directory permissions
- [ ] Search for scripts
- [ ] Search for XML preference files
- [ ] Search for `cpassword`
- [ ] Search for potential secrets
- [ ] Identify referenced network resources
- [ ] Review permissions on referenced resources
- [ ] Record sensitive file hashes where appropriate

## GPO Settings

- [ ] Review local users and groups
- [ ] Review Restricted Groups
- [ ] Review scheduled tasks
- [ ] Review services
- [ ] Review startup scripts
- [ ] Review shutdown scripts
- [ ] Review logon scripts
- [ ] Review logoff scripts
- [ ] Review registry configuration
- [ ] Review Defender configuration
- [ ] Review firewall configuration
- [ ] Review audit policy
- [ ] Review PowerShell logging
- [ ] Review WinRM configuration
- [ ] Review RDP configuration
- [ ] Review user-right assignments
- [ ] Review LAPS-related settings

## BloodHound

- [ ] Collect GPO relationships
- [ ] Identify GPO control paths
- [ ] Identify `GpLink`
- [ ] Identify `WriteGPLink`
- [ ] Identify GPO `GenericAll`
- [ ] Identify GPO `GenericWrite`
- [ ] Identify GPO `WriteDACL`
- [ ] Identify GPO `WriteOwner`
- [ ] Map GPOs to OUs
- [ ] Map OUs to computers
- [ ] Identify Tier 0 GPO paths
- [ ] Independently confirm high-impact paths

## Validation

- [ ] Choose minimum-impact validation
- [ ] Prefer read-only proof
- [ ] Confirm ACL independently
- [ ] Confirm GPO link
- [ ] Confirm effective scope
- [ ] Confirm security filtering
- [ ] Confirm affected systems
- [ ] Use test GPO where active validation is required
- [ ] Use test OU where active validation is required
- [ ] Avoid production GPO code execution
- [ ] Record original state
- [ ] Restore all changes

## Detection

- [ ] Monitor directory changes
- [ ] Monitor 5136
- [ ] Monitor sensitive `gPLink` changes
- [ ] Monitor GPO ACL changes
- [ ] Monitor GPO owner changes
- [ ] Monitor SYSVOL changes
- [ ] Monitor GPO version changes
- [ ] Monitor referenced scripts
- [ ] Monitor Group Policy operational logs
- [ ] Correlate endpoint changes
- [ ] Correlate scheduled tasks
- [ ] Correlate service changes
- [ ] Correlate privileged authentication

## Hardening

- [ ] Inventory GPOs
- [ ] Assign owners
- [ ] Document GPO purpose
- [ ] Remove stale GPOs after review
- [ ] Remove unnecessary editors
- [ ] Restrict modify-security permissions
- [ ] Protect Tier 0 GPOs
- [ ] Protect OU link permissions
- [ ] Protect SYSVOL
- [ ] Protect referenced scripts
- [ ] Remove credentials from SYSVOL
- [ ] Separate administrative roles
- [ ] Use dedicated admin accounts
- [ ] Implement change management
- [ ] Back up critical GPOs
- [ ] Monitor changes continuously

## Cleanup

- [ ] Restore modified GPO settings
- [ ] Restore GPO ACL
- [ ] Restore GPO owner
- [ ] Restore GPO links
- [ ] Restore security filtering
- [ ] Restore WMI filter
- [ ] Remove test scripts
- [ ] Remove test scheduled tasks
- [ ] Remove test preference entries
- [ ] Verify SYSVOL state
- [ ] Verify GPO version
- [ ] Verify effective policy
- [ ] Secure evidence

---

# Group Policy Testing Model

The basic architecture is:

```text
Group Policy Object
        |
        +--> Group Policy Container
        |          |
        |          v
        |     Active Directory
        |
        +--> Group Policy Template
                   |
                   v
                 SYSVOL
```

The application model is:

```text
GPO
 |
 v
Link
 |
 v
Site / Domain / OU
 |
 v
Security Filtering
 |
 v
WMI Filter
 |
 v
User / Computer
 |
 v
Policy Processing
```

The LSDOU model is:

```text
Local
 |
 v
Site
 |
 v
Domain
 |
 v
OU
 |
 v
Child OU
```

The GPO-control model is:

```text
Controlled Principal
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

The GPO-link model is:

```text
Controlled Principal
        |
        v
WriteGPLink
        |
        v
Sensitive OU
        |
        +
Controlled GPO
        |
        v
New GPO Link
        |
        v
Affected Systems
```

The indirect ACL model is:

```text
Controlled Principal
        |
        v
WriteDACL
        |
        v
GPO
        |
        v
Grant Edit Permission
        |
        v
Modify GPO
```

The ownership model is:

```text
Controlled Principal
        |
        v
WriteOwner
        |
        v
GPO
        |
        v
Become Owner
        |
        v
Modify DACL
        |
        v
Grant Edit Permission
```

The SYSVOL model is:

```text
GPO
 |
 v
SYSVOL Resource
 |
 v
Writable Script / File
 |
 v
Policy Processing
 |
 v
Target System
```

The local administrator model is:

```text
GPO
 |
 v
Local Group Configuration
 |
 v
Domain Group
 |
 v
Local Administrators
 |
 v
Target Computers
```

The persistence model is:

```text
GPO Change
    |
    v
Policy Refresh
    |
    v
Malicious Configuration
    |
    v
Endpoint Cleanup
    |
    v
Next Policy Refresh
    |
    v
Configuration Returns
```

The detection model is:

```text
AD / SYSVOL Change
        |
        v
GPO Version Change
        |
        v
Policy Processing
        |
        v
Endpoint Change
        |
        v
Security Telemetry
```

The defensive model is:

```text
Inventory
   |
   v
Classify GPOs
   |
   v
Restrict Editors
   |
   v
Restrict Link Control
   |
   v
Protect SYSVOL
   |
   v
Monitor Changes
   |
   v
Review Continuously
```

A mature GPO assessment should answer:

```text
Which GPOs exist?
       |
       v
Who owns them?
       |
       v
Who can edit them?
       |
       v
Who can modify their ACLs?
       |
       v
Who can link them?
       |
       v
Where are they linked?
       |
       v
Which settings are enabled?
       |
       v
Which principals pass security filtering?
       |
       v
Which WMI filters apply?
       |
       v
Which users and computers receive them?
       |
       v
Are any targets privileged?
       |
       v
Are SYSVOL resources writable?
       |
       v
Are external referenced resources writable?
       |
       v
What is the actual resulting privilege?
```

The most important principle is:

```text
Can Edit GPO
     |
     X
Automatically Domain Compromise
```

Instead:

```text
GPO Control
    +
GPO Scope
    +
Effective Application
    +
Target Privilege
    =
Actual Security Impact
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Groups:

[Active Directory Groups](groups.md)

BloodHound:

[BloodHound](bloodhound.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

The following topics complement Group Policy analysis and can be linked once their dedicated notes are available:

```text
active-directory/machine-account-quota.md
active-directory/gpp-passwords.md
active-directory/laps.md
active-directory/gmsa.md
active-directory/shadow-credentials.md
active-directory/lateral-movement.md
active-directory/privilege-escalation.md
active-directory/persistence.md
```

---

# References

## Microsoft Group Policy

[Microsoft - Group Policy Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Group Policy Processing](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-processing){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Group Policy PowerShell

[Microsoft - Get-GPO](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/get-gpo){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-GPOReport](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/get-gporeport){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-GPPermission](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/get-gppermission){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-GPInheritance](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/get-gpinheritance){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-GPResultantSetOfPolicy](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/get-gpresultantsetofpolicy){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Backup-GPO](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/backup-gpo){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Group Policy Preferences

[Microsoft - Group Policy Preferences](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn581922(v=ws.11)){ target="_blank" rel="noopener noreferrer" }

[Microsoft Security Bulletin MS14-025](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025){ target="_blank" rel="noopener noreferrer" }

---

## Active Directory Schema

[Microsoft - Group-Policy-Container Class](https://learn.microsoft.com/en-us/windows/win32/adschema/c-grouppolicycontainer){ target="_blank" rel="noopener noreferrer" }

[Microsoft - gPLink Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-gplink){ target="_blank" rel="noopener noreferrer" }

[Microsoft - gPOptions Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-gpoptions){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## PowerView

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Group Policy Modification](https://attack.mitre.org/techniques/T1484/001/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Domain Policy Modification](https://attack.mitre.org/techniques/T1484/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Group Policy should be treated as a central administrative control plane.

The basic relationship is:

```text
Administrator
      |
      v
GPO
      |
      v
OU
      |
      v
Users / Computers
```

This means a permission that initially appears limited to:

```text
Can Edit GPO
```

may actually represent:

```text
Can Influence Hundreds of Systems
```

depending on where the GPO applies.

The correct security model is therefore:

```text
Principal
    +
GPO Permission
    +
GPO Link
    +
Effective Scope
    +
Target Privilege
    =
Security Impact
```

A complete assessment should analyse both halves of the GPO:

```text
              GPO
               |
       +-------+-------+
       |               |
       v               v
Active Directory     SYSVOL
```

It should then determine:

```text
Who Can Edit?
      |
      v
What Can They Edit?
      |
      v
Where Is It Linked?
      |
      v
Who Receives It?
      |
      v
What Privilege Results?
```

Do not stop at GPO enumeration.

Map:

```text
GPO
 |
 v
OU
 |
 v
Computer / User
 |
 v
Security Role
```

Likewise, do not assume that a linked GPO necessarily applies.

Evaluate:

```text
Link
 +
Inheritance
 +
Security Filtering
 +
WMI Filtering
 +
GPO Status
 =
Effective Application
```

The offensive attack-path model is:

```text
Controlled Principal
        |
        v
GPO Control
        |
        v
Sensitive GPO
        |
        v
Sensitive OU
        |
        v
Privileged Systems
```

The defensive model is:

```text
Inventory
   |
   v
Classify
   |
   v
Restrict Control
   |
   v
Protect Links
   |
   v
Protect SYSVOL
   |
   v
Monitor
   |
   v
Review
```

The strongest Group Policy assessment therefore combines:

```text
Active Directory Enumeration
        +
ACL Analysis
        +
Group Analysis
        +
GPO Reports
        +
SYSVOL Review
        +
BloodHound
        +
Resultant Set of Policy
```

to answer the most important question:

```text
Which identities can use Group Policy
to influence which systems?
```

For a penetration tester, this becomes:

```text
What GPOs can the controlled identity influence?
        |
        v
Where do those GPOs apply?
        |
        v
What privilege exists on those targets?
        |
        v
Can the impact be proven without
modifying production policy?
```

For defenders:

```text
Who can modify our security policy?
        |
        v
Who can modify where it applies?
        |
        v
Who can modify the files it trusts?
        |
        v
Would we detect those changes?
```

Those questions turn Group Policy enumeration into meaningful Active Directory security analysis.
