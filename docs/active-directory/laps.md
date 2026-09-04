# Active Directory LAPS

Local Administrator Password Solution, commonly abbreviated as LAPS, is Microsoft's solution for securely managing local administrator passwords on Windows systems.

The fundamental problem LAPS addresses is local administrator password reuse.

Without password management, an organisation might have:

```text
WORKSTATION01\Administrator
Password: SamePassword

WORKSTATION02\Administrator
Password: SamePassword

SERVER01\Administrator
Password: SamePassword

SERVER02\Administrator
Password: SamePassword
```

If one local administrator credential is compromised:

```text
Compromise One Host
        |
        v
Recover Local Administrator Credential
        |
        v
Same Credential on Other Hosts
        |
        v
Lateral Movement
```

LAPS changes this model to:

```text
WORKSTATION01
      |
      v
Unique Password A

WORKSTATION02
      |
      v
Unique Password B

SERVER01
      |
      v
Unique Password C

SERVER02
      |
      v
Unique Password D
```

The security model becomes:

```text
Windows Computer
      |
      v
Generate / Manage Local Admin Password
      |
      v
Back Up Password
      |
      +--> Active Directory
      |
      +--> Microsoft Entra ID
```

For an Active Directory assessment, the key question is not simply:

```text
Is LAPS deployed?
```

It is:

```text
Who can retrieve the managed passwords?
```

A poorly delegated LAPS deployment can create an attack path:

```text
Low-Privilege Domain User
        |
        v
Read LAPS Password
        |
        v
Local Administrator
        |
        v
Target Computer
```

Therefore LAPS should be assessed from two perspectives:

```text
LAPS Deployment
      |
      +--> Does it prevent password reuse?
      |
      +--> Are password readers restricted?
      |
      +--> Are passwords encrypted where appropriate?
      |
      +--> Are privileged systems separated?
      |
      +--> Is password retrieval monitored?
```

!!! warning "Authorised testing only"
    LAPS passwords provide local administrative access to managed systems. During an assessment, begin by enumerating the LAPS deployment and identifying principals that have password-read permissions. Do not retrieve every production LAPS password simply because the current account can do so. Where active validation is required, use an approved test computer or retrieve the minimum credential necessary to demonstrate the issue. Never include complete LAPS passwords in screenshots, tickets, chat messages, Git repositories, or final reports.

---

# Windows LAPS vs Legacy Microsoft LAPS

Two implementations may be encountered:

```text
Legacy Microsoft LAPS
```

and:

```text
Windows LAPS
```

They are related but different implementations.

Microsoft now recommends Windows LAPS for supported Windows platforms.

---

# Legacy Microsoft LAPS

Legacy Microsoft LAPS was a separate Microsoft product.

It extended the Active Directory schema with attributes commonly including:

```text
ms-Mcs-AdmPwd
ms-Mcs-AdmPwdExpirationTime
```

The basic model was:

```text
Computer
   |
   v
Local Administrator Password
   |
   v
ms-Mcs-AdmPwd
   |
   v
Active Directory
```

The password was protected primarily through Active Directory ACLs.

---

# Windows LAPS

Windows LAPS is built into supported modern Windows versions.

It provides additional capabilities compared with legacy Microsoft LAPS.

Examples include:

```text
Active Directory Password Backup
Microsoft Entra ID Password Backup
Password Encryption in AD
Password History
DSRM Password Management
Dedicated Event Logging
PowerShell Management
```

Microsoft states that Windows LAPS is available on supported Windows 10, Windows 11, Windows Server 2019, Windows Server 2022, Windows Server 2025, and later supported platforms.

---

# Legacy LAPS Is Deprecated

Legacy Microsoft LAPS is deprecated on newer Microsoft operating systems.

Modern assessments should therefore determine whether the organisation is using:

```text
Legacy LAPS
Windows LAPS
Both During Migration
No LAPS
```

Do not assume that finding:

```text
ms-Mcs-AdmPwd
```

means Windows LAPS is not also deployed.

---

# LAPS Comparison

| Feature | Legacy Microsoft LAPS | Windows LAPS |
|---|---|---|
| Local administrator password management | Yes | Yes |
| AD password backup | Yes | Yes |
| Microsoft Entra ID backup | No | Yes |
| AD password encryption | No | Yes |
| Password history | No | Yes |
| DSRM password management | No | Yes |
| Native modern Windows implementation | No | Yes |
| Legacy schema attributes | Yes | Compatibility scenarios |
| Dedicated modern LAPS PowerShell module | No | Yes |

---

# Legacy LAPS Attributes

Important legacy attributes include:

```text
ms-Mcs-AdmPwd
ms-Mcs-AdmPwdExpirationTime
```

The most security-sensitive attribute is:

```text
ms-Mcs-AdmPwd
```

because it contains the managed local administrator password.

---

# Windows LAPS Attributes

Important Windows LAPS Active Directory attributes include:

```text
msLAPS-PasswordExpirationTime
msLAPS-Password
msLAPS-EncryptedPassword
msLAPS-EncryptedPasswordHistory
msLAPS-EncryptedDSRMPassword
msLAPS-EncryptedDSRMPasswordHistory
```

Not every environment will use every attribute.

The exact attributes populated depend on:

```text
Policy
Backup Location
Encryption Configuration
Device Type
Windows Version
```

---

# msLAPS-Password

When Windows LAPS stores a clear-text password in Active Directory, it uses:

```text
msLAPS-Password
```

Microsoft documents this attribute as containing a JSON string.

Conceptually:

```json
{
  "n": "Administrator",
  "t": "<password-update-time>",
  "p": "<managed-password>"
}
```

Where:

```text
n = managed local account name
t = password update time
p = plaintext password
```

The attribute itself is protected as a confidential Active Directory attribute.

---

# msLAPS-EncryptedPassword

Windows LAPS can instead store the current password using:

```text
msLAPS-EncryptedPassword
```

The value is encrypted.

Conceptually:

```text
Local Administrator Password
        |
        v
Windows LAPS Encryption
        |
        v
msLAPS-EncryptedPassword
        |
        v
Active Directory
```

An authorised principal must be able to decrypt the value before the password can be used.

---

# Cleartext vs Encrypted AD Storage

The distinction is important.

```text
msLAPS-Password
      |
      v
Cleartext Password Stored in Protected AD Attribute
```

versus:

```text
msLAPS-EncryptedPassword
      |
      v
Encrypted Password Blob
```

Both still rely on correct Active Directory security configuration.

Encryption provides an additional protection layer.

---

# Password History

Windows LAPS can support encrypted password history.

Relevant attribute:

```text
msLAPS-EncryptedPasswordHistory
```

This can be useful for recovery scenarios but increases the importance of tightly controlling decryption permissions.

---

# DSRM Password Management

Windows LAPS can also manage:

```text
Directory Services Restore Mode
```

passwords on domain controllers.

Relevant attributes include:

```text
msLAPS-EncryptedDSRMPassword
msLAPS-EncryptedDSRMPasswordHistory
```

DSRM credentials are highly sensitive.

Access to these values should be treated as:

```text
Tier 0
```

security access.

---

# LAPS Security Model

The general security model is:

```text
Computer Object
      |
      v
LAPS Password Attribute
      |
      v
Active Directory ACL
      |
      v
Authorised Reader
```

For encrypted Windows LAPS:

```text
Computer Object
      |
      v
Encrypted LAPS Password
      |
      v
Authorised Decryption Principal
      |
      v
Plaintext Password
```

---

# LAPS Is an ACL Problem

From a penetration-testing perspective, LAPS exposure is primarily an authorization problem.

The important question is:

```text
Which principals can read the password?
```

For example:

```text
Helpdesk
   |
   v
Read LAPS Password
   |
   v
Workstations OU
```

may be legitimate.

Compare:

```text
Domain Users
   |
   v
Read LAPS Password
   |
   v
Servers OU
```

which could represent severe overdelegation.

---

# LAPS Attack Path

A typical attack path is:

```text
Compromised User
      |
      v
LAPS Read Permission
      |
      v
Computer Password
      |
      v
Local Administrator
      |
      v
Target Computer
```

If the target contains additional credentials:

```text
Target Computer
      |
      v
Local Administrator
      |
      v
Credential Access
      |
      v
Additional Domain Identity
```

the path can continue.

---

# LAPS Does Not Give Domain Administrator

A LAPS password normally provides access to a:

```text
Local Account
```

on the managed computer.

Therefore:

```text
Read LAPS Password
       |
       X
Automatic Domain Admin
```

Instead:

```text
Read LAPS Password
       |
       v
Local Administrator on Target
       |
       v
Potential Further Attack Path
```

The distinction should be clear in reporting.

---

# LAPS and Local Accounts

A managed account might be:

```text
Administrator
```

or another configured local administrator account.

For example:

```text
SERVER01\Administrator
```

is different from:

```text
CORP\Administrator
```

The LAPS password should normally authenticate the local account on the managed computer, not the domain account with a similar name.

---

# Local Account Syntax

Common Windows syntax:

```text
.\Administrator
```

or:

```text
SERVER01\Administrator
```

For remote tools, local account handling depends on the protocol and tool.

Do not accidentally interpret:

```text
Administrator
```

as:

```text
CORP\Administrator
```

---

# Why LAPS Matters for Lateral Movement

Without LAPS:

```text
HOST01
 |
 v
Local Admin Password
 |
 +--> HOST02
 +--> HOST03
 +--> HOST04
```

With properly configured LAPS:

```text
HOST01 Password
      |
      X
HOST02

HOST02 Password
      |
      X
HOST03
```

Compromise of one local administrator password should therefore have a much smaller blast radius.

---

# Initial Assessment Questions

Determine:

```text
Is LAPS deployed?

Which implementation?

Which computers are managed?

Which account is managed?

Where are passwords backed up?

Are passwords encrypted?

Who can read passwords?

Who can decrypt passwords?

Who can modify LAPS configuration?

Are Tier 0 systems included?

Are password reads audited?

Are passwords rotated after use?
```

---

# Enumerate Windows LAPS PowerShell Module

Check whether the Windows LAPS module is available:

```powershell
Get-Module -ListAvailable LAPS
```

List commands:

```powershell
Get-Command -Module LAPS
```

Common commands include:

```text
Find-LapsADExtendedRights
Get-LapsADPassword
Get-LapsAADPassword
Get-LapsDiagnostics
Invoke-LapsPolicyProcessing
Reset-LapsPassword
Set-LapsADComputerSelfPermission
Set-LapsADPasswordExpirationTime
Set-LapsADReadPasswordPermission
Set-LapsADResetPasswordPermission
Update-LapsADSchema
```

Available commands depend on the installed Windows version and management components.

Always verify:

```powershell
Get-Command -Module LAPS
```

before relying on remembered syntax.

---

# Identify LAPS Schema Attributes

PowerShell:

```powershell
Get-ADObject \
    -SearchBase (Get-ADRootDSE).SchemaNamingContext \
    -LDAPFilter '(|(lDAPDisplayName=msLAPS-Password)(lDAPDisplayName=ms-Mcs-AdmPwd))' \
    -Properties lDAPDisplayName |
    Select-Object \
        Name,
        lDAPDisplayName
```

This can help determine which schema extensions are present.

---

# Enumerate Windows LAPS Attributes

Search for computer objects with Windows LAPS expiration metadata:

```powershell
Get-ADComputer \
    -Filter * \
    -Properties msLAPS-PasswordExpirationTime |
    Where-Object {
        $_.'msLAPS-PasswordExpirationTime'
    } |
    Select-Object \
        Name,
        DistinguishedName,
        msLAPS-PasswordExpirationTime
```

This does not retrieve the password.

---

# Enumerate Legacy LAPS

For legacy LAPS:

```powershell
Get-ADComputer \
    -Filter * \
    -Properties ms-Mcs-AdmPwdExpirationTime |
    Where-Object {
        $_.'ms-Mcs-AdmPwdExpirationTime'
    } |
    Select-Object \
        Name,
        DistinguishedName,
        ms-Mcs-AdmPwdExpirationTime
```

Again, this identifies likely managed computers without requesting the sensitive password attribute.

---

# Prefer Metadata First

A safe workflow is:

```text
Find LAPS Deployment
      |
      v
Identify Managed Computers
      |
      v
Identify Password Readers
      |
      v
Determine Exposure
      |
      v
Retrieve Password Only If Required
```

Avoid starting with:

```text
Dump Every LAPS Password
```

---

# Find-LapsADExtendedRights

Windows LAPS provides:

```powershell
Find-LapsADExtendedRights
```

This cmdlet helps identify principals with extended rights over an OU that may permit access to Windows LAPS confidential password attributes.

Example:

```powershell
Find-LapsADExtendedRights \
    -Identity 'OU=Workstations,DC=corp,DC=example'
```

or, depending on environment and identity resolution:

```powershell
Find-LapsADExtendedRights \
    -Identity 'Workstations'
```

Check:

```powershell
Get-Help Find-LapsADExtendedRights -Full
```

before use.

---

# Why Extended Rights Matter

Microsoft specifically warns that users or groups with broad extended rights over an OU can potentially read confidential attributes, including Windows LAPS password attributes.

Therefore:

```text
OU
 |
 v
Extended Rights
 |
 v
Confidential Attributes
 |
 v
LAPS Password
```

should be reviewed carefully.

---

# Enumerate Multiple OUs

A structured review can start with:

```powershell
Get-ADOrganizationalUnit \
    -Filter * |
    Select-Object \
        Name,
        DistinguishedName
```

Then inspect sensitive OUs using:

```powershell
Find-LapsADExtendedRights \
    -Identity '<OU-DN>'
```

Prioritise:

```text
Domain Controllers
Servers
Workstations
Privileged Workstations
Management Servers
Certificate Infrastructure
```

---

# Legacy LAPS PowerShell

Legacy Microsoft LAPS used the:

```text
AdmPwd.PS
```

PowerShell module.

Common historical cmdlets include:

```text
Find-AdmPwdExtendedRights
Get-AdmPwdPassword
Set-AdmPwdReadPasswordPermission
Set-AdmPwdResetPasswordPermission
```

Check availability:

```powershell
Get-Module -ListAvailable AdmPwd.PS
```

and:

```powershell
Get-Command -Module AdmPwd.PS
```

---

# Find Legacy LAPS Readers

Where the legacy module is installed:

```powershell
Find-AdmPwdExtendedRights \
    -Identity 'OU=Workstations,DC=corp,DC=example'
```

Check:

```powershell
Get-Help Find-AdmPwdExtendedRights -Full
```

for installed syntax.

---

# Active Directory ACL Enumeration

LAPS permissions can also be analysed through normal Active Directory ACLs.

Get the computer DN:

```powershell
$computer = Get-ADComputer 'SERVER01'
$computer.DistinguishedName
```

Read the ACL:

```powershell
Get-Acl \
    "AD:\$($computer.DistinguishedName)"
```

Detailed view:

```powershell
(Get-Acl "AD:\$($computer.DistinguishedName)").Access |
    Format-Table \
        IdentityReference,
        ActiveDirectoryRights,
        AccessControlType,
        ObjectType,
        IsInherited \
        -AutoSize
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# OU ACLs

Because permissions are frequently inherited:

```text
OU ACL
  |
  v
Computer Object
  |
  v
LAPS Password Read
```

analyse the parent OU as well as the individual computer.

Example:

```powershell
Get-Acl \
    'AD:\OU=Servers,DC=corp,DC=example'
```

---

# Explicit vs Inherited Rights

A computer may have:

```text
Explicit ACE
```

or:

```text
Inherited ACE
```

that provides password access.

Record:

```text
Principal
Right
Object
Inherited?
Source OU
```

This makes remediation substantially easier.

---

# PowerView

PowerView can assist with ACL analysis.

Typical read-only usage:

```powershell
Get-DomainObjectAcl \
    -Identity 'SERVER01$' \
    -ResolveGUIDs
```

For an OU:

```powershell
Get-DomainObjectAcl \
    -Identity 'OU=Servers,DC=corp,DC=example' \
    -ResolveGUIDs
```

Exact syntax varies between PowerView versions.

Always inspect:

```powershell
Get-Help Get-DomainObjectAcl -Full
```

---

# BloodHound

BloodHound can identify LAPS-related attack relationships when the relevant data has been collected.

A typical conceptual edge is:

```text
ReadLAPSPassword
```

The graph may reveal:

```text
Alice
 |
 v
ReadLAPSPassword
 |
 v
SERVER01
```

This indicates that Alice can potentially obtain the managed local administrator credential for the target computer.

---

# BloodHound Attack Path

```text
Low-Privilege User
       |
       v
ReadLAPSPassword
       |
       v
SERVER01
       |
       v
Local Administrator
       |
       v
Credential / Session Exposure
       |
       v
Higher Privilege
```

The important point is:

```text
ReadLAPSPassword
```

may be only one edge in a longer path.

---

# BloodHound Validation

Do not interpret every graph edge as guaranteed exploitation.

Use:

```text
BloodHound Edge
      |
      v
Identify Permission
      |
      v
Validate ACL
      |
      v
Confirm LAPS Deployment
      |
      v
Confirm Target
      |
      v
Assess Resulting Access
```

---

# Linux Enumeration

Linux-based assessment can use:

```text
LDAP
BloodHound Collection
NetExec
bloodyAD
Other LDAP-Aware Tools
```

Exact LAPS support varies by tool version.

Prefer raw LDAP and ACL evidence when a tool's behaviour is uncertain.

---

# ldapsearch for Legacy LAPS Metadata

A metadata-only query:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=computer)(ms-Mcs-AdmPwdExpirationTime=*))' \
    sAMAccountName \
    distinguishedName \
    ms-Mcs-AdmPwdExpirationTime
```

This avoids requesting:

```text
ms-Mcs-AdmPwd
```

during initial discovery.

---

# ldapsearch for Windows LAPS Metadata

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=computer)(msLAPS-PasswordExpirationTime=*))' \
    sAMAccountName \
    distinguishedName \
    msLAPS-PasswordExpirationTime
```

---

# Do Not Start by Querying Password Attributes

Avoid initial commands that request:

```text
ms-Mcs-AdmPwd
msLAPS-Password
msLAPS-EncryptedPassword
```

across every computer.

The first objective should be:

```text
Map Exposure
```

not:

```text
Collect Credentials
```

---

# NetExec

NetExec versions may provide LAPS-related functionality.

Because syntax and modules change, first inspect:

```bash
nxc --version
```

```bash
nxc ldap --help
```

and:

```bash
nxc ldap -L
```

where module listing is supported by the installed version.

Do not rely on historical CrackMapExec syntax without checking the current NetExec release.

See:

[NetExec](netexec.md)

---

# LAPS Password Retrieval

Retrieving a LAPS password is credential access.

Only do so when:

```text
Read Permission Confirmed
       |
       v
Active Validation Required
       |
       v
Explicitly Authorised
```

---

# Get-LapsADPassword

Windows LAPS provides:

```powershell
Get-LapsADPassword
```

to retrieve Windows LAPS credentials from Active Directory.

A safe first query can request the object without forcing plaintext display:

```powershell
Get-LapsADPassword \
    -Identity 'SERVER01'
```

Check:

```powershell
Get-Help Get-LapsADPassword -Full
```

for the installed version.

---

# Plaintext Retrieval

Where explicitly required and authorised, the cmdlet supports retrieval of the managed password.

Depending on the current module, options can allow the password to be returned in plaintext form.

Because this exposes a reusable administrative credential:

```text
Get Password
     |
     v
Sensitive Evidence
```

do not display it unnecessarily.

---

# Encrypted Password Handling

Windows LAPS can store encrypted password values.

Microsoft's supported LAPS tooling can automatically decrypt the password when the calling identity is authorised to do so.

This means:

```text
Encrypted Attribute
       |
       X
No Security Risk
```

is incorrect.

The correct question is:

```text
Who Can Decrypt It?
```

---

# Legacy Password Retrieval

Where legacy Microsoft LAPS is deployed and the current identity has the necessary rights, historical tooling may retrieve:

```text
ms-Mcs-AdmPwd
```

For example, legacy environments may provide:

```powershell
Get-AdmPwdPassword \
    -ComputerName 'SERVER01'
```

Do not retrieve production passwords unless necessary.

---

# Direct Attribute Read

A direct AD query can technically request legacy LAPS password data:

```powershell
Get-ADComputer \
    -Identity 'SERVER01' \
    -Properties ms-Mcs-AdmPwd
```

However, during an assessment, prefer permission analysis before sensitive attribute retrieval.

If the current principal lacks permission, the password value should not be returned.

---

# Windows LAPS Direct Attribute

Similarly:

```powershell
Get-ADComputer \
    -Identity 'SERVER01' \
    -Properties msLAPS-Password
```

may expose the Windows LAPS clear-text password attribute when the caller is authorised to read it.

This is credential retrieval.

Use only where required.

---

# Safe Validation Hierarchy

A good LAPS validation hierarchy is:

```text
Level 1
Confirm LAPS Schema

Level 2
Identify Managed Computers

Level 3
Identify Password Readers

Level 4
Confirm Current User Has Read Permission

Level 5
Retrieve Password for Dedicated Test Computer

Level 6
Validate Local Administrative Access

Level 7
Retrieve Production Password
```

Stop at the lowest level sufficient to demonstrate the finding.

---

# Example Safe Test

Suppose:

```text
CORP\helpdesk-test
```

has unexpected LAPS read access to:

```text
TEST-SERVER01
```

The validation can be:

```text
Confirm ACL
    |
    v
Retrieve TEST-SERVER01 Password
    |
    v
Authenticate Once
    |
    v
Confirm Local Administrator
    |
    v
Stop
```

There is no need to retrieve:

```text
SERVER01
SERVER02
SERVER03
SERVER04
```

passwords.

---

# Authentication with a LAPS Password

A LAPS credential usually represents a local account.

Example:

```text
SERVER01\Administrator
```

A remote authentication test must therefore use the correct local-account context.

---

# NetExec Local Authentication

Where SMB authentication testing is explicitly authorised, current NetExec versions can be used according to their local-authentication syntax.

Always inspect:

```bash
nxc smb --help
```

before use.

The conceptual model is:

```text
Target:
SERVER01

Account:
SERVER01\Administrator

Password:
LAPS-managed password
```

Only validate against the computer whose password was retrieved.

---

# Do Not Spray LAPS Passwords

A LAPS password should be unique.

Therefore:

```text
SERVER01 LAPS Password
       |
       X
SERVER02
```

Testing it broadly is unnecessary and contrary to the security model LAPS is designed to provide.

If the same password works elsewhere, investigate whether:

```text
LAPS Is Not Applied
Password Management Failed
Local Password Was Manually Reused
Systems Were Cloned Incorrectly
```

---

# LAPS and Pass-the-Hash

If a local administrator password is known, its NT hash could also potentially become usable in NTLM-based authentication scenarios.

Conceptually:

```text
LAPS Password
     |
     v
Local Account NT Hash
     |
     v
NTLM Authentication
```

However, the main purpose of LAPS is that the local password should be unique to that computer.

Therefore:

```text
Pass-the-Hash
```

using one machine's local administrator hash should not provide broad lateral movement if LAPS is correctly implemented.

See:

[Pass-the-Hash](pass-the-hash.md)

---

# LAPS and NTLM

LAPS does not disable NTLM.

It reduces the blast radius associated with reusable local credentials.

The relationship is:

```text
NTLM Enabled
     |
     +
Unique LAPS Password Per Host
     |
     v
Reduced Credential Reuse
```

See:

[NTLM](ntlm.md)

---

# LAPS and Kerberos

Local accounts do not normally authenticate to the Active Directory KDC as domain principals.

Therefore:

```text
SERVER01\Administrator
```

is not equivalent to:

```text
CORP\Administrator
```

and should not be treated as a normal domain Kerberos principal.

---

# LAPS and Credential Access

LAPS passwords are credential material.

Therefore excessive LAPS permissions belong within:

```text
Credential Access
```

analysis.

See:

[Active Directory Credential Access](credential-access.md)

---

# LAPS and ACL Abuse

A LAPS exposure often begins with an ACL.

Example:

```text
Alice
 |
 v
OU Permission
 |
 v
Read Confidential Attributes
 |
 v
LAPS Password
 |
 v
SERVER01
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# LAPS and Group Membership

LAPS read permissions are frequently delegated to groups.

Example:

```text
Helpdesk-LAPS-Readers
       |
       v
Read LAPS Password
       |
       v
Workstations OU
```

Therefore investigate:

```text
Who Is in the Reader Group?
```

including nested membership.

See:

[Active Directory Groups](groups.md)

---

# Nested Group Risk

Suppose:

```text
Domain Users
      |
      v
Helpdesk-Contractors
      |
      v
LAPS-Readers
```

A seemingly restricted reader group may effectively include a much broader population through nested membership.

The complete authorization path matters.

---

# LAPS and Group Policy

LAPS configuration can be deployed using Group Policy.

Relevant settings may control:

```text
Backup Directory
Password Age
Password Length
Password Complexity
Managed Account
Password Encryption
Password History
Post-Authentication Actions
```

depending on Windows LAPS version and deployment.

See:

[Active Directory Group Policy](group-policy.md)

---

# LAPS Policy Location

Windows LAPS Group Policy settings are typically configured through the applicable Windows LAPS administrative templates.

During assessment, review:

```text
Which GPO Configures LAPS?
Where Is It Linked?
Which Computers Receive It?
Is Configuration Consistent?
```

---

# Policy Application

A LAPS GPO existing in Active Directory does not guarantee:

```text
Every Computer Is Managed
```

Validate actual coverage.

The model is:

```text
LAPS GPO
   |
   v
GPO Link
   |
   v
Security Filtering
   |
   v
WMI Filtering
   |
   v
Computer
   |
   v
Policy Processing
```

---

# Identify Coverage Gaps

Look for:

```text
Computers Without LAPS Metadata
Servers Outside Managed OUs
Stale Computer Objects
Legacy Systems
Exceptions
Misconfigured GPO Links
Policy Processing Failures
```

---

# Coverage Analysis

A useful comparison is:

```text
All Active Computers
        |
        v
Compare
        |
        +--> Windows LAPS Managed
        |
        +--> Legacy LAPS Managed
        |
        +--> Not Managed
```

Unmanaged systems deserve investigation.

---

# Example Coverage Query

Windows LAPS:

```powershell
$computers = Get-ADComputer \
    -Filter * \
    -Properties \
        Enabled,
        LastLogonDate,
        msLAPS-PasswordExpirationTime

$computers |
    Select-Object \
        Name,
        Enabled,
        LastLogonDate,
        msLAPS-PasswordExpirationTime
```

---

# Identify Potentially Unmanaged Computers

```powershell
Get-ADComputer \
    -Filter 'Enabled -eq $true' \
    -Properties \
        LastLogonDate,
        msLAPS-PasswordExpirationTime |
    Where-Object {
        -not $_.'msLAPS-PasswordExpirationTime'
    } |
    Select-Object \
        Name,
        DistinguishedName,
        LastLogonDate
```

This is an indicator, not definitive proof that LAPS is absent.

Different backup modes and migration states may require additional analysis.

---

# Legacy Coverage Query

```powershell
Get-ADComputer \
    -Filter 'Enabled -eq $true' \
    -Properties \
        LastLogonDate,
        ms-Mcs-AdmPwdExpirationTime |
    Where-Object {
        -not $_.'ms-Mcs-AdmPwdExpirationTime'
    } |
    Select-Object \
        Name,
        DistinguishedName,
        LastLogonDate
```

---

# Windows LAPS Password Generation

Windows LAPS can generate random passwords according to configured complexity and length policies.

Microsoft currently documents configurable password lengths from:

```text
8
```

through:

```text
64
```

characters.

Do not assume the default password length is the organisation's configured value.

Review the actual policy.

---

# Password Length

The defensive goal should be:

```text
Long
Random
Unique
Automatically Rotated
```

rather than merely satisfying minimum password complexity rules.

---

# Passphrases

Modern Windows LAPS versions can support generated passphrases on supported operating systems.

Availability depends on platform and policy version.

Do not assume passphrase support exists on every Windows LAPS-capable endpoint.

---

# Password Rotation

LAPS automatically manages password rotation according to policy.

Conceptually:

```text
Password A
   |
   v
Expiration
   |
   v
Password B
   |
   v
Expiration
   |
   v
Password C
```

This limits the useful lifetime of a compromised credential.

---

# Password Expiration Metadata

Windows LAPS:

```text
msLAPS-PasswordExpirationTime
```

Legacy LAPS:

```text
ms-Mcs-AdmPwdExpirationTime
```

These attributes help determine when rotation is expected.

---

# Forced Rotation

Windows LAPS provides supported administrative mechanisms for forcing or scheduling password rotation.

For example:

```powershell
Set-LapsADPasswordExpirationTime
```

can be used by authorised administrators.

Check:

```powershell
Get-Help Set-LapsADPasswordExpirationTime -Full
```

before use.

Do not alter password expiration during a penetration test unless specifically authorised.

---

# Post-Authentication Actions

Windows LAPS can support post-authentication actions.

These can help reduce the period during which a retrieved password remains useful after administrative use.

Exact capabilities depend on supported platform and policy configuration.

Review the organisation's configuration rather than assuming automatic rotation occurs immediately after every use.

---

# Password Encryption

Where Windows LAPS is backed up to Windows Server Active Directory, password encryption can provide stronger protection.

Conceptually:

```text
Password
   |
   v
Encrypt
   |
   v
Active Directory
   |
   v
Authorised Decryption Identity
```

This reduces reliance solely on confidential-attribute ACL protection.

---

# Encryption Principal

When encrypted password storage is used, determine:

```text
Who Can Decrypt the Password?
```

The encryption principal should be tightly controlled.

Avoid broad groups.

---

# Tiered LAPS Reader Groups

A mature environment may separate readers.

Example:

```text
Workstation LAPS Readers
        |
        v
Workstations

Server LAPS Readers
        |
        v
Member Servers

Tier 0 LAPS Readers
        |
        v
Tier 0 Systems
```

This is preferable to:

```text
One Helpdesk Group
       |
       v
Every Computer
```

---

# Domain Controllers

Domain controllers require special treatment.

A normal member-server local administrator model does not apply to domain controllers in the same way.

Windows LAPS can manage:

```text
DSRM
```

credentials on domain controllers.

DSRM password access should be highly restricted.

---

# DSRM Risk

A path such as:

```text
Helpdesk User
      |
      v
Read DSRM Password
      |
      v
Domain Controller
```

should be treated as a serious Tier 0 authorization issue.

---

# LAPS and Protected Systems

Prioritise review of:

```text
Domain Controllers
Certificate Authorities
AD FS Servers
Identity Management Servers
Backup Servers
Virtualisation Hosts
SCCM Infrastructure
Privileged Access Workstations
Management Servers
```

LAPS reader permissions on these systems should be extremely restricted.

---

# LAPS and Server Administrators

A server administration team may legitimately require LAPS passwords for member servers.

The assessment should determine:

```text
Does the group need all servers?
```

Prefer:

```text
Application Team A
      |
      v
Application A Servers
```

instead of:

```text
Application Team A
      |
      v
All Servers
```

where operationally feasible.

---

# Helpdesk Access

Helpdesk teams commonly require local administrative access to workstations.

This can justify:

```text
Read LAPS Password
```

for:

```text
Workstations
```

but not necessarily:

```text
Servers
Domain Controllers
Certificate Authorities
Management Infrastructure
```

---

# Delegation Scope

The principle is:

```text
Administrative Responsibility
        |
        v
Matching LAPS Scope
```

Avoid:

```text
Convenience
   |
   v
Domain-Wide LAPS Read
```

---

# LAPS and Machine Account Quota

Machine Account Quota and LAPS are separate concepts.

```text
MAQ
 |
 v
Computer Account Creation
```

versus:

```text
LAPS
 |
 v
Local Administrator Password Management
```

However, both involve computer objects and their Active Directory permissions.

See:

[Active Directory Machine Account Quota](machine-account-quota.md)

---

# LAPS and RBCD

LAPS access and RBCD are different attack paths.

```text
ReadLAPSPassword
       |
       v
Local Administrator on Computer
```

versus:

```text
Write RBCD Attribute
       |
       v
Kerberos Delegation
```

A principal may possess both relationships, creating multiple ways to compromise the same target.

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# LAPS and Shadow Credentials

If a principal controls a computer object's:

```text
msDS-KeyCredentialLink
```

that represents a separate authentication attack path from reading its LAPS password.

Conceptually:

```text
Computer Object
      |
      +--> LAPS Password
      |
      +--> Key Credential Link
```

Each permission should be evaluated independently.

A dedicated page should cover:

```text
active-directory/shadow-credentials.md
```

---

# LAPS and gMSA

LAPS protects:

```text
Local Administrator Credentials
```

while gMSA protects:

```text
Domain Service Account Credentials
```

Conceptually:

```text
LAPS
 |
 v
Local Accounts
```

```text
gMSA
 |
 v
Domain Service Accounts
```

Both reduce reliance on manually managed reusable passwords.

A dedicated page should cover:

```text
active-directory/gmsa.md
```

---

# LAPS and GPP Passwords

Historically, organisations sometimes used Group Policy Preferences to deploy local administrator passwords.

This created:

```text
Shared Static Password
      |
      v
cpassword
      |
      v
SYSVOL
```

LAPS provides a fundamentally better model:

```text
Unique Password
      |
      v
Per Computer
      |
      v
Automatic Rotation
```

See:

`Group Policy Preferences Passwords`

---

# LAPS and Local Administrator Password Reuse

A useful assessment test is not necessarily:

```text
Try One Password Everywhere
```

Instead determine:

```text
Is LAPS Coverage Complete?
```

and:

```text
Are Local Administrator Passwords Unique?
```

Prefer configuration evidence over broad credential testing.

---

# LAPS Failure Scenarios

Common weaknesses include:

```text
LAPS Not Deployed
Incomplete Coverage
Excessive Password Readers
Broad Extended Rights
Password Encryption Disabled Where Desired
Overly Broad Decryption Principal
Legacy LAPS Still Used
Stale Passwords
Password Rotation Failures
Privileged Systems in Low-Trust Reader Scope
Weak Monitoring
```

---

# Excessive Reader Example

```text
Domain Users
      |
      v
Read LAPS Password
      |
      v
Servers OU
```

This can provide every ordinary domain user with local administrative credentials for servers.

This is significantly different from:

```text
Dedicated Server Admins
      |
      v
Read LAPS Password
      |
      v
Servers OU
```

---

# Nested Reader Example

```text
LAPS-Server-Readers
        |
        v
Helpdesk
        |
        v
Contractors
```

Always expand nested group membership.

---

# Stale LAPS Passwords

If expiration metadata indicates that a password should have rotated long ago, investigate:

```text
Client Offline
Policy Processing Failure
Permissions Problem
LAPS Misconfiguration
Unsupported Client
Replication Problem
```

Do not immediately assume compromise.

---

# LAPS Client Processing

Windows LAPS processing depends on:

```text
Policy
Computer
Directory Connectivity
Permissions
Supported Windows Version
```

A failure in any component can prevent expected password backup or rotation.

---

# LAPS Diagnostics

Windows LAPS provides:

```powershell
Get-LapsDiagnostics
```

for troubleshooting.

This can collect diagnostic information useful to administrators.

Because diagnostics may contain sensitive system information, handle the resulting data carefully.

---

# Invoke Policy Processing

Windows LAPS provides:

```powershell
Invoke-LapsPolicyProcessing
```

to trigger policy processing.

Check:

```powershell
Get-Help Invoke-LapsPolicyProcessing -Full
```

Do not trigger configuration changes on production endpoints during assessment unless explicitly authorised.

---

# LAPS Event Logs

Windows LAPS includes a dedicated event log channel.

A common location is:

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
LAPS
    |
    v
Operational
```

This can provide visibility into:

```text
Policy Processing
Password Updates
Backup Operations
Errors
```

---

# Query LAPS Event Log

PowerShell:

```powershell
Get-WinEvent \
    -LogName 'Microsoft-Windows-LAPS/Operational' \
    -ErrorAction SilentlyContinue |
    Select-Object \
        -First 50 \
        TimeCreated,
        Id,
        LevelDisplayName,
        Message
```

This is useful during troubleshooting and defensive validation.

---

# Detection

LAPS security monitoring should cover:

```text
Password Retrieval
Permission Changes
Reader Group Changes
Policy Changes
Unexpected Administrative Authentication
Password Rotation Failures
```

---

# Detection Model

```text
User
 |
 v
LAPS Password Retrieval
 |
 v
Local Administrator Authentication
 |
 v
Target Computer
 |
 v
Administrative Activity
```

Correlating these stages provides stronger detection than monitoring any single event.

---

# Monitor LAPS Reader Groups

If access is delegated through:

```text
LAPS-Readers
```

monitor membership changes.

Relevant group membership events can include:

```text
4728
4732
4756
```

depending on whether the group is:

```text
Global
Local
Universal
```

and the environment's auditing configuration.

---

# Monitor ACL Changes

Changes to LAPS-related directory permissions can potentially appear through directory service auditing.

Relevant events may include:

```text
4662
5136
```

depending on:

```text
Audit Policy
SACL Configuration
Type of Change
```

---

# Monitor GPO Changes

If LAPS is configured through Group Policy, monitor:

```text
GPO Modification
GPO ACL Changes
LAPS Policy Changes
```

A malicious or accidental policy change could:

```text
Disable LAPS
Change Backup Directory
Change Managed Account
Change Password Policy
```

---

# Monitor Administrative Authentication

After a LAPS password is retrieved, local account authentication may generate events such as:

```text
4624
4625
```

on the target or associated systems.

Correlate:

```text
LAPS Retrieval
      |
      v
Local Administrator Authentication
      |
      v
Administrative Activity
```

---

# Local vs Domain Authentication Detection

When analysing:

```text
4624
```

determine whether the account was:

```text
SERVER01\Administrator
```

rather than:

```text
CORP\Administrator
```

This prevents incorrect incident conclusions.

---

# LAPS Retrieval Baseline

Legitimate LAPS retrieval may occur during:

```text
Helpdesk Support
Server Maintenance
Incident Response
Recovery
```

Baseline:

```text
Who retrieves passwords?
Which systems?
How often?
From which workstations?
At what times?
```

---

# Suspicious LAPS Retrieval

Potential indicators include:

```text
User Reads Passwords Outside Their Support Scope
Large Number of Passwords Retrieved
Tier 0 Password Retrieval by Helpdesk
Retrieval from Unusual Workstation
Retrieval Immediately Followed by Remote Admin Activity
New Reader Group Membership Followed by Retrieval
```

---

# Password Retrieval Should Be Rare

A mature administrative model should minimise how often humans need to retrieve local administrator passwords.

Where possible:

```text
Central Management
Remote Administration
JIT / JEA
Automated Support Workflows
```

can reduce manual password handling.

---

# Hardening

A strong LAPS design follows:

```text
Deploy Broadly
     |
     v
Use Unique Passwords
     |
     v
Use Strong Password Policy
     |
     v
Encrypt Where Appropriate
     |
     v
Restrict Readers
     |
     v
Separate Administrative Tiers
     |
     v
Monitor Retrieval
     |
     v
Rotate After Use
```

---

# Deploy Windows LAPS

For supported systems, prefer:

```text
Windows LAPS
```

over legacy Microsoft LAPS.

Microsoft recommends migration from legacy LAPS to Windows LAPS on capable systems.

---

# Extend the Schema

Windows Server Active Directory deployments require the Windows LAPS schema extensions.

Microsoft provides:

```powershell
Update-LapsADSchema
```

for this purpose.

This is an administrative operation and should not be performed during a penetration test.

---

# Computer Self-Permission

Managed computers require appropriate permissions to update their own LAPS attributes.

Microsoft provides:

```powershell
Set-LapsADComputerSelfPermission
```

for administrative configuration.

Example conceptual scope:

```text
Workstations OU
      |
      v
Computer SELF Permission
      |
      v
Write Own LAPS Attributes
```

---

# Password Reader Permission

Windows LAPS provides:

```powershell
Set-LapsADReadPasswordPermission
```

for granting password-read permissions.

Use dedicated groups.

Conceptually:

```text
LAPS-Workstation-Readers
       |
       v
Read Password
       |
       v
Workstations OU
```

---

# Reset Permission

Windows LAPS also supports delegated password-reset permission using:

```powershell
Set-LapsADResetPasswordPermission
```

Separate:

```text
Read Password
```

from:

```text
Force Password Expiration / Reset
```

where operational roles differ.

---

# Least Privilege Reader Model

Avoid:

```text
Domain Admins
Helpdesk
Server Admins
Desktop Admins
Application Teams
     |
     v
One Giant LAPS Reader Group
```

Prefer:

```text
Desktop Support
      |
      v
Workstations

Server Operations
      |
      v
Member Servers

Tier 0 Admins
      |
      v
Tier 0 Systems
```

---

# Protect Tier 0

For systems such as:

```text
Domain Controllers
Certificate Authorities
Privileged Management Servers
Identity Infrastructure
```

LAPS or DSRM retrieval rights should remain within the appropriate Tier 0 administrative boundary.

---

# Use Password Encryption

Where Windows LAPS is backed up to Active Directory and the environment supports it, consider encrypted password storage.

Then tightly control:

```text
Decryption Principal
```

---

# Protect the Decryption Principal

A configuration such as:

```text
Broad Helpdesk Group
      |
      v
Decrypt Every LAPS Password
```

defeats much of the benefit of tiered access.

Use narrow security groups.

---

# Strong Password Policy

Configure sufficiently strong:

```text
Password Length
Password Complexity
Password Age
```

according to organisational requirements and supported Windows LAPS capabilities.

Because LAPS passwords are machine-generated, there is little reason to make them human-memorable.

---

# Rotation Frequency

Balance:

```text
Security
```

with:

```text
Operational Recovery Requirements
```

Passwords should rotate regularly and after suspected exposure.

---

# Rotate After Exposure

If a LAPS password is retrieved during:

```text
Pentest
Incident
Helpdesk Operation
Unexpected Access
```

consider rotating it according to organisational policy.

A password that has been exposed to a human or external tester should no longer be considered unknown.

---

# Avoid Password Sharing

Do not distribute LAPS passwords through:

```text
Email
Teams Chat
Slack
Tickets
Spreadsheets
Documentation
```

unless an approved secure workflow specifically supports protected secret handling.

---

# Protect Administrative Workstations

LAPS passwords should preferably be retrieved from:

```text
Approved Administrative Workstations
```

rather than:

```text
General User Workstations
```

This reduces credential exposure.

---

# Logging and Monitoring

Monitor:

```text
Password Retrieval
Reader Group Membership
ACL Changes
LAPS Policy Changes
Password Rotation Failures
Local Administrator Authentication
```

and send appropriate events to the central monitoring platform.

---

# Incident Response

If unauthorised LAPS access is identified:

```text
Identify Reader
      |
      v
Identify Passwords Accessed
      |
      v
Identify Affected Computers
      |
      v
Rotate Passwords
      |
      v
Review Authentication
      |
      v
Review Administrative Activity
      |
      v
Remove Excessive Permission
      |
      v
Investigate Initial Compromise
```

---

# Determine Exposure Scope

Ask:

```text
Which OU could the user read?

Which computers were in that OU?

Which passwords were actually retrieved?

Which systems were subsequently accessed?

Did the account have access to Tier 0?
```

Do not assume:

```text
Read Permission over OU
```

means every password was actually retrieved.

Distinguish:

```text
Potential Exposure
```

from:

```text
Confirmed Retrieval
```

---

# Rotate Affected Passwords

Where password access is confirmed or cannot be ruled out, rotate affected local administrator passwords through supported LAPS mechanisms.

Avoid manually setting the same replacement password across multiple systems.

---

# Review Authentication

Search target systems for:

```text
4624
4625
4672
4688
```

where applicable and auditing is enabled.

Look for authentication using the managed local account from unexpected sources.

---

# Event 4672

Event:

```text
4672
```

can indicate special privileges assigned to a new logon.

A local administrator session may generate privileged-logon telemetry useful during investigation.

---

# Review Remote Administration

Investigate:

```text
SMB
WinRM
RDP
WMI
DCOM
Remote Services
Scheduled Tasks
```

where relevant to the affected systems.

---

# Review Credential Access on the Target

If an attacker gained local administrator access:

```text
LAPS Password
      |
      v
Local Administrator
      |
      v
Credential Access
```

investigate whether the target contained:

```text
Privileged Sessions
Service Credentials
Kerberos Tickets
Application Secrets
```

See:

[Active Directory Credential Access](credential-access.md)

---

# Reporting

Possible finding titles include:

```text
Excessive Active Directory Permissions Allow LAPS Password Retrieval
```

```text
Low-Privilege Domain Users Can Read LAPS Passwords
```

```text
Helpdesk Group Can Retrieve LAPS Passwords for Privileged Servers
```

```text
Incomplete LAPS Deployment Allows Local Administrator Password Reuse
```

```text
Windows LAPS Password Readers Are Excessively Broad
```

```text
Legacy Microsoft LAPS Remains Deployed
```

---

# Example Finding - Excessive LAPS Read Access

```text
Finding:
Excessive Permissions Allow Retrieval of LAPS Passwords

Source Principal:
CORP\Helpdesk

Affected Scope:
OU=Servers,DC=corp,DC=example

Description:
Members of the CORP\Helpdesk group have Active Directory permissions
that allow them to retrieve managed local administrator passwords for
computer objects within the Servers OU.

The delegated permission was confirmed through Active Directory ACL
analysis and Windows LAPS extended-right enumeration.

During validation, the password for one approved test computer was
retrieved and used to confirm local administrative access.

No additional production LAPS passwords were collected.

Impact:
A compromised Helpdesk account could obtain local administrator
credentials for servers within the affected OU.

This could provide administrative access to those systems and may
enable further credential access or lateral movement where privileged
sessions or reusable secrets exist on the affected servers.

Recommendation:
Restrict LAPS password retrieval to dedicated server administration
identities that require access.

Separate workstation, server, and Tier 0 LAPS reader scopes.

Review nested membership of all LAPS reader groups and monitor password
retrieval activity.

Rotate any passwords that may have been exposed.
```

---

# Example Finding - Domain Users

```text
Finding:
Domain Users Can Retrieve Managed Local Administrator Passwords

Affected Principal:
CORP\Domain Users

Affected Scope:
OU=Workstations,DC=corp,DC=example

Description:
Active Directory permissions allow members of Domain Users to retrieve
managed local administrator passwords for computer objects within the
Workstations OU.

As Domain Users contains the majority of authenticated user accounts,
the configuration significantly broadens access to local administrative
credentials.

Impact:
Compromise of an ordinary domain account could allow an attacker to
retrieve local administrator credentials for affected workstations.

This may enable lateral movement, endpoint compromise, and access to
credentials belonging to users logged on to those systems.

Recommendation:
Remove LAPS password-read permissions from Domain Users.

Delegate access only to approved support or administration groups with
a documented operational requirement.

Review historical password retrieval activity and rotate affected
passwords where exposure is suspected.
```

---

# Example Finding - Incomplete Coverage

```text
Finding:
Incomplete Windows LAPS Deployment Leaves Systems Without Managed Local
Administrator Passwords

Affected Systems:
Multiple enabled domain computers

Description:
Windows LAPS is deployed within the domain; however, multiple active
computer objects do not contain expected LAPS password-expiration
metadata and are outside the currently identified LAPS policy scope.

The affected systems were reviewed to exclude obviously stale computer
objects where possible.

Impact:
Systems that do not use LAPS may retain manually configured or reused
local administrator passwords.

Credential compromise on one such system could therefore enable
lateral movement to other systems using the same local administrator
credential.

Recommendation:
Review the identified systems and extend Windows LAPS coverage to all
supported workstations and member servers where operationally
appropriate.

Investigate policy-processing failures and document any required
exceptions.

Periodically compare active computer inventory against LAPS deployment
coverage.
```

---

# Example Finding - Tiering

```text
Finding:
Workstation Support Group Can Retrieve LAPS Passwords for Privileged
Servers

Source Principal:
CORP\Desktop-Support

Affected Systems:
Privileged management servers

Description:
The Desktop-Support group is authorised to retrieve Windows LAPS
passwords for systems used for privileged administration.

This crosses the intended administrative trust boundary between
workstation support and privileged infrastructure.

Impact:
Compromise of a desktop support identity could provide local
administrative access to privileged management systems.

Credentials, sessions, or administrative tooling present on those
systems could enable further privilege escalation.

Recommendation:
Separate LAPS reader permissions according to administrative tier.

Remove workstation support identities from privileged server LAPS
reader groups and restrict retrieval to dedicated privileged
administrators using approved administrative workstations.
```

---

# Severity

Severity depends on:

```text
Reader Principal
      +
Target Scope
      +
Target Sensitivity
      +
Resulting Local Privilege
      +
Downstream Attack Paths
      =
Risk
```

For example:

```text
Helpdesk
   |
   v
Read LAPS
   |
   v
Single Test Workstation
```

may have limited risk.

Compare:

```text
Domain Users
    |
    v
Read LAPS
    |
    v
All Servers
    |
    v
Local Administrator
```

which can represent a serious privilege-escalation path.

---

# Do Not Overstate LAPS

Finding:

```text
User Can Read SERVER01 LAPS Password
```

does not automatically mean:

```text
Domain Compromise
```

The correct model is:

```text
LAPS Password
      |
      v
Local Administrator on SERVER01
      |
      v
What Does SERVER01 Provide?
```

Analyse:

```text
Sessions
Credentials
Applications
Network Access
Directory Rights
Management Roles
```

before assigning impact.

---

# Evidence Checklist

Record:

```text
Domain
LAPS Implementation
Computer
Computer DN
Computer OU
Managed Account
Password Backup Location
Password Encryption Status
Reader Principal
Reader SID
Reader Group Membership
Exact Permission
Inherited / Explicit
Source OU
Password Retrieved?
Authentication Validated?
Resulting Privilege
Target Sensitivity
LAPS Policy GPO
Relevant Events
Cleanup Actions
```

Do not include:

```text
Full LAPS Password
```

in ordinary report evidence.

---

# LAPS Assessment Checklist

## Preparation

- [ ] Confirm LAPS enumeration is authorised
- [ ] Confirm password retrieval restrictions
- [ ] Confirm authentication validation restrictions
- [ ] Confirm Tier 0 testing restrictions
- [ ] Prepare secure credential evidence handling
- [ ] Identify dedicated test computer if available

## Deployment Discovery

- [ ] Determine whether Windows LAPS is deployed
- [ ] Determine whether legacy LAPS is deployed
- [ ] Identify LAPS schema attributes
- [ ] Identify managed computers
- [ ] Identify unmanaged computers
- [ ] Identify migration state
- [ ] Identify backup location
- [ ] Identify managed local account
- [ ] Identify DSRM management

## Policy

- [ ] Identify LAPS GPO
- [ ] Identify GPO links
- [ ] Review security filtering
- [ ] Review WMI filtering
- [ ] Review password length
- [ ] Review password complexity
- [ ] Review password age
- [ ] Review encryption configuration
- [ ] Review password history
- [ ] Review post-authentication actions
- [ ] Review backup directory

## Permissions

- [ ] Enumerate LAPS reader groups
- [ ] Enumerate extended rights
- [ ] Review OU ACLs
- [ ] Review computer ACLs
- [ ] Identify inherited rights
- [ ] Identify explicit rights
- [ ] Expand nested groups
- [ ] Review decryption principals
- [ ] Review reset permissions
- [ ] Review computer SELF permissions

## Scope Review

- [ ] Review workstation readers
- [ ] Review server readers
- [ ] Review Tier 0 readers
- [ ] Review Domain Controller / DSRM permissions
- [ ] Review Certificate Authority systems
- [ ] Review management servers
- [ ] Review privileged workstations
- [ ] Identify administrative-tier violations

## BloodHound

- [ ] Collect LAPS-related data
- [ ] Review `ReadLAPSPassword`
- [ ] Identify paths from low-privilege users
- [ ] Identify paths to privileged computers
- [ ] Validate graph edges with directory ACLs
- [ ] Review downstream paths from affected computers

## Validation

- [ ] Prefer ACL proof
- [ ] Prefer metadata proof
- [ ] Use dedicated test computer
- [ ] Retrieve only one password where sufficient
- [ ] Confirm correct local account
- [ ] Authenticate only to approved target
- [ ] Avoid password spraying
- [ ] Avoid unnecessary remote execution
- [ ] Rotate test credential where required
- [ ] Redact password evidence

## Detection

- [ ] Monitor LAPS reader group membership
- [ ] Monitor OU ACL changes
- [ ] Monitor computer ACL changes
- [ ] Monitor LAPS policy changes
- [ ] Monitor password retrieval
- [ ] Monitor local administrator authentication
- [ ] Monitor privileged logons
- [ ] Monitor password rotation failures
- [ ] Collect Windows LAPS Operational logs
- [ ] Correlate retrieval with target access

## Hardening

- [ ] Prefer Windows LAPS
- [ ] Migrate legacy LAPS where appropriate
- [ ] Deploy LAPS broadly
- [ ] Remove unmanaged exceptions
- [ ] Use long random passwords
- [ ] Enable encryption where appropriate
- [ ] Restrict decryption principal
- [ ] Separate workstation readers
- [ ] Separate server readers
- [ ] Separate Tier 0 readers
- [ ] Review nested group membership
- [ ] Protect DSRM credentials
- [ ] Use administrative workstations
- [ ] Monitor retrieval
- [ ] Rotate after exposure

## Incident Response

- [ ] Identify affected reader
- [ ] Identify reader scope
- [ ] Determine passwords actually retrieved
- [ ] Identify affected computers
- [ ] Rotate affected passwords
- [ ] Review local authentication
- [ ] Review privileged activity
- [ ] Review credential access on affected hosts
- [ ] Remove excessive rights
- [ ] Investigate initial compromise
- [ ] Review historical reader membership

## Cleanup

- [ ] Remove locally stored LAPS passwords
- [ ] Remove screenshots containing passwords
- [ ] Remove temporary credential files
- [ ] Rotate test password if required
- [ ] Remove temporary sessions
- [ ] Confirm no ACL changes were made
- [ ] Confirm no GPO changes were made
- [ ] Secure retained evidence

---

# LAPS Testing Model

The basic LAPS model is:

```text
Computer
   |
   v
Unique Local Administrator Password
   |
   v
Directory Backup
   |
   v
Authorised Reader
```

The legacy model is:

```text
Computer
   |
   v
Legacy LAPS
   |
   v
ms-Mcs-AdmPwd
   |
   v
Active Directory ACL
```

The Windows LAPS cleartext model is:

```text
Computer
   |
   v
Windows LAPS
   |
   v
msLAPS-Password
   |
   v
Confidential AD Attribute
```

The encrypted model is:

```text
Computer
   |
   v
Windows LAPS
   |
   v
msLAPS-EncryptedPassword
   |
   v
Authorised Decryption Principal
   |
   v
Password
```

The attack model is:

```text
Compromised User
      |
      v
Read LAPS Permission
      |
      v
Managed Password
      |
      v
Local Administrator
      |
      v
Target Computer
```

The downstream model is:

```text
Local Administrator
      |
      v
Target Computer
      |
      +--> Sessions
      |
      +--> Service Credentials
      |
      +--> Application Secrets
      |
      +--> Kerberos Tickets
      |
      +--> Network Access
```

The password-reuse prevention model is:

```text
Without LAPS:

Password A
   |
   +--> HOST01
   +--> HOST02
   +--> HOST03

With LAPS:

Password A -> HOST01
Password B -> HOST02
Password C -> HOST03
```

The authorization model is:

```text
Principal
   |
   v
OU ACL
   |
   v
LAPS Read Permission
   |
   v
Computer Password
```

The tiering model is:

```text
Desktop Support
      |
      v
Workstations

Server Admins
      |
      v
Servers

Tier 0 Admins
      |
      v
Tier 0
```

instead of:

```text
One Reader Group
      |
      v
Everything
```

The safe testing model is:

```text
Discover Deployment
      |
      v
Identify Managed Computers
      |
      v
Identify Readers
      |
      v
Validate ACL
      |
      v
Retrieve Test Password If Required
      |
      v
Validate One Target
      |
      v
Stop
```

The detection model is:

```text
Password Retrieval
      |
      v
Local Authentication
      |
      v
Privileged Session
      |
      v
Administrative Activity
```

The incident-response model is:

```text
Unexpected LAPS Access
       |
       v
Determine Scope
       |
       v
Rotate Passwords
       |
       v
Review Authentication
       |
       v
Remove Excessive Permission
       |
       v
Investigate Downstream Activity
```

The defensive model is:

```text
Windows LAPS
      |
      v
Unique Passwords
      |
      v
Strong Random Passwords
      |
      v
Restricted Readers
      |
      v
Encrypted Storage
      |
      v
Administrative Tiering
      |
      v
Monitoring
      |
      v
Rotation
```

The most important security distinction is:

```text
LAPS Deployed
      |
      X
LAPS Secure
```

A secure deployment requires:

```text
LAPS
 +
Complete Coverage
 +
Correct ACLs
 +
Restricted Readers
 +
Strong Password Policy
 +
Appropriate Encryption
 +
Monitoring
 =
Effective Protection
```

For penetration testers:

```text
Do Not Ask:
"How many LAPS passwords can I dump?"

Ask:
"Which principals can access which LAPS passwords,
and what privilege does that provide?"
```

For defenders:

```text
Do Not Ask:
"Is LAPS installed?"

Ask:
"Is every relevant computer managed,
who can retrieve each password,
and can that retrieval be detected?"
```

The final assessment model is:

```text
Identity
   |
   v
LAPS Permission
   |
   v
Computer
   |
   v
Local Administrator
   |
   v
Resulting Attack Path
```

That relationship determines the actual security impact of a LAPS permission.

---

# Related Notes

Credential Access:

[Active Directory Credential Access](credential-access.md)

Group Policy Preference Passwords:

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

Machine Account Quota:

[Active Directory Machine Account Quota](machine-account-quota.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

NTLM:

[NTLM](ntlm.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

BloodHound:

[BloodHound](bloodhound.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

The following Credential Access pages complement LAPS:

```text
active-directory/gmsa.md
active-directory/shadow-credentials.md
active-directory/ntds.md
```

---

# References

## Microsoft - Windows LAPS

[Microsoft - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows LAPS and Windows Server Active Directory](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-scenarios-windows-server-active-directory){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows LAPS Technical Reference](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-technical-reference){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS PowerShell

[Microsoft - Windows LAPS PowerShell Cmdlets](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-management-powershell){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-LapsADPassword](https://learn.microsoft.com/en-us/powershell/module/laps/get-lapsadpassword){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Find-LapsADExtendedRights](https://learn.microsoft.com/en-us/powershell/module/laps/find-lapsadextendedrights){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS Concepts

[Microsoft - Windows LAPS Passwords and Passphrases](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-concepts-passwords-passphrases){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows LAPS Account Management Modes](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-concepts-account-management-modes){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Credential Protection

[Microsoft - Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## PowerSploit

[PowerSploit - PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Credentials from Password Stores](https://attack.mitre.org/techniques/T1555/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - OS Credential Dumping](https://attack.mitre.org/techniques/T1003/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

LAPS is one of the most important controls for reducing Windows local administrator credential reuse.

The fundamental problem is:

```text
Shared Local Administrator Password
        |
        v
Compromise One Computer
        |
        v
Compromise Many Computers
```

LAPS changes this to:

```text
Computer
   |
   v
Unique Managed Password
```

so that:

```text
HOST01 Credential
      |
      X
HOST02
```

However, deploying LAPS does not automatically make the environment secure.

The password still needs an authorization model:

```text
LAPS Password
      |
      v
Who Can Read It?
```

The assessment must therefore combine:

```text
Deployment
   +
Coverage
   +
ACL Analysis
   +
Reader Analysis
   +
Administrative Tiering
   +
Monitoring
```

The critical attack relationship is:

```text
Low-Privilege Identity
        |
        v
ReadLAPSPassword
        |
        v
Privileged Computer
        |
        v
Local Administrator
```

A mature assessment should expand this into:

```text
Who has the right?
      |
      v
Why do they have it?
      |
      v
Which computers are affected?
      |
      v
What privilege does the password provide?
      |
      v
What credentials or sessions exist there?
      |
      v
Can the path reach higher privilege?
```

For legacy environments:

```text
ms-Mcs-AdmPwd
```

should be recognised as the historical LAPS password attribute.

For modern Windows LAPS:

```text
msLAPS-Password
```

and:

```text
msLAPS-EncryptedPassword
```

must be distinguished.

The stronger model is:

```text
Windows LAPS
      |
      v
Encrypted Password
      |
      v
Restricted Decryption Principal
      |
      v
Tiered Administration
```

where appropriate.

Testing should remain minimal:

```text
Enumerate
   |
   v
Identify Readers
   |
   v
Validate ACL
   |
   v
Retrieve One Test Password If Needed
   |
   v
Confirm One Approved Target
   |
   v
Stop
```

rather than:

```text
Dump Every Password
      |
      X
Unnecessary Credential Collection
```

For defenders, LAPS should be treated as an identity-security system rather than merely a password generator:

```text
Password Generation
      |
      v
Directory Storage
      |
      v
Authorization
      |
      v
Retrieval
      |
      v
Administrative Authentication
      |
      v
Rotation
```

Every stage requires protection.

The final security model is therefore:

```text
Unique Passwords
      +
Complete Coverage
      +
Restricted Readers
      +
Encryption
      +
Administrative Tiering
      +
Monitoring
      +
Rotation
      =
Strong LAPS Deployment
```

The central assessment question remains:

```text
Who can retrieve the local administrator password
for which computer, and what can they reach from there?
```
