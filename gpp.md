# Group Policy Preferences Passwords

Group Policy Preferences, commonly abbreviated as GPP, historically allowed administrators to configure local users, services, scheduled tasks, mapped drives, and other settings through Group Policy.

Some legacy Group Policy Preference configurations allowed administrators to store credentials inside XML files distributed through:

```text
SYSVOL
```

The password was stored in an attribute named:

```text
cpassword
```

Although the password was encrypted, Microsoft published the AES key used by Group Policy Preferences. Consequently, anyone who can read the XML file can decrypt the stored password.

The basic attack path is:

```text
Domain User
    |
    v
Read SYSVOL
    |
    v
GPP XML File
    |
    v
cpassword
    |
    v
Decrypt Password
    |
    v
Credential
    |
    v
Authenticate as Configured Account
```

This is fundamentally different from password cracking.

```text
cpassword
    |
    v
Known GPP AES Key
    |
    v
Decryption
```

rather than:

```text
Password Hash
    |
    v
Guess Password
    |
    v
Hash Comparison
```

Because SYSVOL is normally readable by authenticated domain users, any legacy GPP XML file containing a `cpassword` can potentially expose its associated credential to a large portion of the domain.

!!! warning "Authorised testing only"
    GPP password discovery is normally read-only, but the resulting plaintext credentials can provide privileged access. During an assessment, retrieve only the minimum credential material necessary to demonstrate the issue. Do not broadly authenticate recovered credentials against systems unless credential reuse testing is explicitly authorised. Redact passwords from screenshots and reports, store recovered credentials securely, and recommend immediate credential rotation.

---

# What Is Group Policy?

Group Policy provides centralised configuration management for Active Directory environments.

A simplified model is:

```text
Active Directory
      |
      v
Group Policy Object
      |
      +--> Directory Configuration
      |
      +--> SYSVOL Files
              |
              v
        Domain Computers
```

Group Policy Objects are commonly referred to as:

```text
GPOs
```

Each GPO has two important components:

```text
Group Policy Object
      |
      +--> Group Policy Container
      |       |
      |       v
      |   Active Directory
      |
      +--> Group Policy Template
              |
              v
            SYSVOL
```

The Group Policy Template contains file-based policy information.

---

# SYSVOL

SYSVOL is a domain-wide share hosted by domain controllers.

Typical UNC path:

```text
\\corp.example\SYSVOL
```

Another common path is:

```text
\\dc01.corp.example\SYSVOL
```

Domain members generally require read access because Group Policy configuration must be distributed to systems throughout the domain.

Conceptually:

```text
Domain Controller
      |
      v
SYSVOL
      |
      +--> Policies
      |
      +--> Scripts
      |
      +--> Group Policy Preferences
```

---

# SYSVOL Is Replicated

In modern Active Directory environments, SYSVOL is normally replicated between domain controllers using DFS Replication.

Therefore a credential-containing GPP file may exist across multiple domain controllers.

Conceptually:

```text
DC01
 |
 | SYSVOL Replication
 v
DC02
 |
 | SYSVOL Replication
 v
DC03
```

Removing the file from only one manually selected location is not an appropriate remediation strategy.

The GPO itself should be corrected through supported administrative mechanisms.

---

# What Are Group Policy Preferences?

Group Policy Preferences extended Group Policy with configurable preference items.

Examples include:

```text
Local Users and Groups
Mapped Drives
Services
Scheduled Tasks
Data Sources
Printers
```

Historically, some preference items supported credentials.

Those credentials could be represented in XML using:

```text
userName
```

and:

```text
cpassword
```

---

# Example

A historical preference file could contain content conceptually similar to:

```xml
<Properties
    action="U"
    userName="CORP\svc_example"
    cpassword="[ENCRYPTED_GPP_VALUE]" />
```

The security problem is:

```text
cpassword
```

is not protected using a secret unique to the organisation.

---

# Why cpassword Is Recoverable

Microsoft documented the cryptographic key used to protect Group Policy Preference passwords.

Therefore:

```text
Encrypted cpassword
        |
        +
Publicly Known Key
        |
        v
Recoverable Password
```

The confidentiality of the password does not depend on knowledge of a secret key possessed only by the organisation.

---

# Encryption Is Not the Same as Hashing

This distinction is important.

A hash is generally used as:

```text
Password
   |
   v
One-Way Function
   |
   v
Hash
```

Recovering the password generally requires guessing or another weakness.

GPP `cpassword` uses reversible encryption:

```text
Password
   |
   v
AES Encryption
   |
   v
cpassword
```

and because the relevant key is publicly documented:

```text
cpassword
   |
   v
AES Decryption
   |
   v
Password
```

No password cracking is required.

---

# MS14-025

Microsoft addressed the unsafe storage of passwords in Group Policy Preferences through:

```text
MS14-025
```

The update prevents administrators from creating or modifying affected Group Policy Preference items that store passwords using the vulnerable mechanism.

However, an important limitation is:

```text
Patch Installed
      |
      X
Existing cpassword Automatically Removed
```

Existing preference files containing passwords can remain in SYSVOL.

Therefore:

```text
Fully Patched Domain
```

can still contain:

```text
Legacy GPP Password Exposure
```

if old XML files were never removed.

---

# Historical vs Current Risk

GPP password exposure should generally be understood as a legacy configuration problem.

The vulnerability may survive because:

```text
Old GPO
 |
 v
Old Preference XML
 |
 v
cpassword
 |
 v
Still Present in SYSVOL
```

rather than because administrators can currently create new password-bearing GPP configurations through normal patched management interfaces.

---

# Why This Still Matters

Active Directory domains can exist for many years.

During that time:

```text
Administrators Change
Servers Change
Applications Change
GPOs Change
```

but old files may remain.

Common reasons include:

```text
Legacy GPOs
Disabled GPOs
Old Migration Files
Forgotten Preference Items
Backup Copies
Old Scripts
Manual SYSVOL Copies
```

Therefore SYSVOL should always be reviewed during an authorised Active Directory assessment.

---

# Common GPP XML Files

Historically interesting files include:

```text
Groups.xml
Services.xml
ScheduledTasks.xml
Drives.xml
DataSources.xml
Printers.xml
```

Additional preference XML files may exist depending on configuration.

The important indicator is:

```text
cpassword=
```

not merely the filename.

---

# Groups.xml

`Groups.xml` was commonly associated with local user and local group preference configuration.

Example conceptual path:

```text
\\corp.example\SYSVOL\
corp.example\
Policies\
{GPO-GUID}\
Machine\
Preferences\
Groups\
Groups.xml
```

Potential content:

```text
Local Administrator Configuration
        |
        v
Groups.xml
        |
        v
username + cpassword
```

---

# Services.xml

Historical service preference configuration may appear under:

```text
Machine\Preferences\Services\Services.xml
```

Potential security impact:

```text
Service
   |
   v
Domain Service Account
   |
   v
cpassword
```

If the service account is privileged or reused elsewhere, the impact can extend beyond the original service.

---

# ScheduledTasks.xml

Scheduled task preference configuration may historically contain credentials.

Possible paths include preference directories associated with:

```text
ScheduledTasks
```

The exact XML structure depends on the preference type and Windows generation.

Always search for:

```text
cpassword
```

rather than relying solely on a fixed filename list.

---

# Drives.xml

Mapped drive preferences could historically contain alternate credentials.

Potential path:

```text
User\Preferences\Drives\Drives.xml
```

A recovered credential may correspond to:

```text
File Server User
Service Account
Legacy Domain Account
```

---

# DataSources.xml

Data source preferences could historically contain credentials used to access databases or other data sources.

Potential impact may include:

```text
Database Access
Application Access
Domain Authentication
```

depending on the identity.

---

# Printers.xml

Printer preference configuration should also be included in broad searches for historical `cpassword` data.

Again:

```text
Search Attribute
```

is more reliable than:

```text
Assume Fixed File
```

---

# GPO Directory Structure

A typical policy path looks like:

```text
\\corp.example\SYSVOL\corp.example\Policies\{GUID}
```

Example:

```text
\\corp.example\SYSVOL\
corp.example\
Policies\
{31B2F340-016D-11D2-945F-00C04FB984F9}
```

Inside the GPO:

```text
Machine
User
GPT.INI
```

Preference configuration can appear below:

```text
Machine\Preferences
```

or:

```text
User\Preferences
```

---

# Initial SYSVOL Enumeration

Windows:

```cmd
dir \\corp.example\SYSVOL
```

PowerShell:

```powershell
Get-ChildItem '\\corp.example\SYSVOL'
```

Recursive enumeration:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL' \
    -Recurse \
    -ErrorAction SilentlyContinue
```

---

# Enumerate Policy XML Files

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL\corp.example\Policies' \
    -Recurse \
    -Filter '*.xml' \
    -ErrorAction SilentlyContinue |
    Select-Object FullName
```

---

# Search for cpassword with PowerShell

A direct read-only search:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL\corp.example\Policies' \
    -Recurse \
    -Filter '*.xml' \
    -ErrorAction SilentlyContinue |
    Select-String \
        -Pattern 'cpassword' \
        -CaseSensitive:$false
```

---

# Search Entire SYSVOL

If the assessment permits broader read-only searching:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL' \
    -Recurse \
    -File \
    -ErrorAction SilentlyContinue |
    Select-String \
        -Pattern 'cpassword' \
        -CaseSensitive:$false \
        -ErrorAction SilentlyContinue
```

---

# findstr

A simple Windows-native search can use:

```cmd
findstr /S /I /M "cpassword" \\corp.example\SYSVOL\*.xml
```

The `/M` option displays matching filenames rather than the matching content.

This can reduce accidental exposure of credential material in the terminal.

---

# Search Specific XML Types

```powershell
$files = @(
    'Groups.xml',
    'Services.xml',
    'ScheduledTasks.xml',
    'Drives.xml',
    'DataSources.xml',
    'Printers.xml'
)

Get-ChildItem \
    '\\corp.example\SYSVOL' \
    -Recurse \
    -File \
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -in $files
    } |
    Select-Object FullName
```

Then inspect only relevant files.

---

# Linux SYSVOL Access

From Linux, SYSVOL can be accessed over SMB using authorised domain credentials.

Useful tools include:

```text
smbclient
Impacket smbclient
NetExec
```

---

# smbclient

List domain controller shares:

```bash
smbclient \
    -L //dc01.corp.example \
    -U 'CORP/alice'
```

Access SYSVOL:

```bash
smbclient \
    //dc01.corp.example/SYSVOL \
    -U 'CORP/alice'
```

Inside the client:

```text
ls
```

and:

```text
recurse ON
```

can assist with navigation.

---

# Kerberos smbclient

Where Kerberos authentication is configured correctly, the installed Samba client may support Kerberos-based access.

Check:

```bash
smbclient --help
```

because Kerberos-related command-line options vary between Samba versions.

Ensure:

```text
DNS
Time Synchronisation
Kerberos Configuration
```

are correct before troubleshooting the application layer.

---

# Impacket smbclient

Impacket:

```bash
impacket-smbclient \
    'corp.example/alice:<PASSWORD>@dc01.corp.example'
```

Then access:

```text
SYSVOL
```

from the interactive client.

Check:

```bash
impacket-smbclient -h
```

for the installed version.

---

# NetExec SYSVOL Enumeration

NetExec can enumerate SMB shares:

```bash
nxc smb dc01.corp.example \
    -d corp.example \
    -u alice \
    -p '<PASSWORD>' \
    --shares
```

This can confirm access to:

```text
SYSVOL
NETLOGON
```

Check the current version:

```bash
nxc --version
```

and:

```bash
nxc smb --help
```

before using version-specific modules.

---

# Mount SYSVOL on Linux

Where appropriate, SYSVOL can also be mounted for read-only analysis.

For example, after creating an authorised mount point:

```bash
sudo mkdir -p /mnt/sysvol
```

a CIFS mount can be used according to the environment's authentication requirements.

Avoid placing plaintext passwords directly on a shared shell command line where they may enter:

```text
Shell History
Process Listings
Logs
```

Prefer safer credential mechanisms supported by the environment.

---

# Search Downloaded SYSVOL

If an authorised copy of SYSVOL has been obtained for offline analysis:

```bash
grep \
    -Rni \
    --include='*.xml' \
    'cpassword' \
    ./SYSVOL
```

To show only filenames:

```bash
grep \
    -Ril \
    --include='*.xml' \
    'cpassword' \
    ./SYSVOL
```

The filename-only approach is preferable during initial discovery.

---

# Search with ripgrep

Where `rg` is installed:

```bash
rg \
    -i \
    -l \
    'cpassword' \
    ./SYSVOL
```

This recursively lists matching files.

---

# Manual XML Inspection

Once a relevant file is identified:

```bash
less Groups.xml
```

or:

```bash
xmllint \
    --format Groups.xml
```

where `xmllint` is installed.

Avoid copying the plaintext credential into unnecessary terminals or logs.

---

# Example GPP Record

A historical record may resemble:

```xml
<User name="LegacyAdmin">
    <Properties
        action="U"
        userName="LegacyAdmin"
        cpassword="[REDACTED]" />
</User>
```

Relevant fields may include:

```text
userName
cpassword
changed
newName
action
```

depending on the preference item.

---

# Username Context

Do not assume the username always represents:

```text
Domain Account
```

It may represent:

```text
Local User
Domain User
Service Account
Application Account
Legacy Account
```

Determine the context of the preference.

---

# Local User Example

Suppose the preference configures:

```text
Administrator
```

on workstations.

The credential might represent:

```text
.\Administrator
```

rather than:

```text
CORP\Administrator
```

This distinction changes the impact significantly.

---

# Domain User Example

If the XML explicitly references:

```text
CORP\svc_deploy
```

the recovered password may correspond to a domain account.

Then investigate:

```text
Group Membership
SPNs
Logon Rights
Service Usage
Password Reuse
Privilege
```

without immediately authenticating across the environment.

---

# Determine GPO Scope

Finding a credential in a GPO is only part of the assessment.

Determine where the GPO applies.

The model is:

```text
GPP Credential
      |
      v
GPO
      |
      v
Linked Container
      |
      v
Users / Computers
```

Understanding scope helps determine:

```text
Where was the credential intended to be used?
```

---

# Identify the GPO

The path contains a GUID such as:

```text
{6AC1786C-016F-11D2-945F-00C04FB984F9}
```

This GUID can be correlated with the corresponding Group Policy Object.

PowerShell:

```powershell
Get-GPO -Guid '6AC1786C-016F-11D2-945F-00C04FB984F9'
```

where the GroupPolicy module is available.

---

# Enumerate All GPOs

```powershell
Get-GPO -All |
    Select-Object \
        DisplayName,
        Id,
        GpoStatus,
        CreationTime,
        ModificationTime
```

---

# GPO Report

A useful read-only command is:

```powershell
Get-GPOReport \
    -All \
    -ReportType Xml \
    -Path '.\all-gpos.xml'
```

The resulting report can help correlate:

```text
GPO
Settings
Links
Security Filtering
```

Treat the report as assessment evidence.

---

# Group Policy Management

Administrators can also inspect GPOs using:

```text
Group Policy Management Console
```

commonly launched as:

```text
gpmc.msc
```

Useful information includes:

```text
GPO Name
GUID
Links
Security Filtering
Delegation
Settings
```

---

# GPP Password Discovery Tools

Several security tools can identify historical GPP credentials.

Common examples include:

```text
NetExec
Impacket
PowerShell
Manual SYSVOL Search
```

Tool availability and exact options vary by version.

Always verify installed help before relying on remembered syntax.

---

# Impacket Get-GPPPassword

Impacket includes tooling for locating Group Policy Preference passwords.

Depending on the installation, it may be available as:

```text
Get-GPPPassword.py
```

or:

```text
impacket-Get-GPPPassword
```

Check:

```bash
impacket-Get-GPPPassword -h
```

if available in the installed package.

A typical authorised usage pattern is:

```bash
impacket-Get-GPPPassword \
    'corp.example/alice:<PASSWORD>@dc01.corp.example'
```

Exact syntax should be confirmed against the installed Impacket version.

---

# NetExec GPP Modules

NetExec versions may provide modules related to GPP password discovery.

Enumerate available modules rather than assuming a module name:

```bash
nxc smb -L
```

Then inspect the relevant module:

```bash
nxc smb -M <MODULE> --options
```

This avoids relying on syntax from an older CrackMapExec or NetExec release.

---

# gpp-decrypt

Kali and other penetration-testing distributions may include utilities commonly called:

```text
gpp-decrypt
```

These accept a GPP `cpassword` and decrypt it using the publicly documented key.

Check:

```bash
gpp-decrypt --help
```

or:

```bash
man gpp-decrypt
```

where available.

---

# Manual Decryption Is Usually Unnecessary

During an assessment, the presence of:

```text
cpassword
```

already demonstrates that recoverable credential material has been stored in a domain-readable location.

If the account identity and impact can be established without decrypting the credential:

```text
Do Not Decrypt
```

may be the safer option.

---

# When Decryption Is Useful

Decryption may be justified where:

```text
Credential Validity Is Uncertain
Account Identity Requires Confirmation
Impact Cannot Otherwise Be Established
Client Explicitly Requests Validation
```

Use the minimum validation necessary.

---

# Decryption Does Not Require Cracking

Do not use terminology such as:

```text
Cracked the GPP Password
```

when the password was decrypted.

Prefer:

```text
Decrypted the GPP cpassword
```

because the distinction is technically important.

---

# Safe Validation Workflow

A recommended workflow is:

```text
Locate cpassword
      |
      v
Identify Associated Account
      |
      v
Determine GPO Context
      |
      v
Determine Whether Account Still Exists
      |
      v
Review Account Privilege
      |
      v
Decide Whether Decryption Is Necessary
      |
      v
If Required, Decrypt
      |
      v
Validate Minimum Necessary Access
```

---

# Check Whether the Account Exists

PowerShell:

```powershell
Get-ADUser \
    -Identity 'svc_example' \
    -Properties \
        Enabled,
        PasswordLastSet,
        LastLogonDate,
        MemberOf,
        ServicePrincipalName
```

For computer accounts:

```powershell
Get-ADComputer \
    -Identity 'COMPUTER01' \
    -Properties *
```

---

# Disabled Accounts

A GPP credential may reference an account that is now:

```text
Disabled
Deleted
Renamed
Expired
```

This reduces immediate exploitability but does not remove the historical security concern.

The file should still be removed because:

```text
Credential Exposure
```

has already occurred.

---

# Password Rotation

Check:

```text
PasswordLastSet
```

where appropriate.

If the exposed credential predates the most recent password change, the current password may no longer match the GPP value.

Example:

```text
GPP File Modified:
2020

PasswordLastSet:
2026
```

This can indicate that the exposed password has since been rotated.

Do not assume this conclusively proves no password reuse occurred elsewhere.

---

# Account Privilege

Determine:

```text
Group Membership
Nested Group Membership
Delegated Rights
Local Administrator Rights
Service Usage
Kerberos SPNs
BloodHound Paths
```

The recovered password's impact depends on the associated account.

---

# BloodHound

BloodHound can help answer:

```text
What happens if this account is compromised?
```

Conceptually:

```text
GPP Credential
      |
      v
svc_deploy
      |
      v
BloodHound
      |
      v
Attack Paths
```

Possible relationships may include:

```text
AdminTo
MemberOf
GenericAll
GenericWrite
WriteDacl
WriteOwner
CanRDP
CanPSRemote
```

depending on BloodHound version and collection.

See:

[BloodHound](bloodhound.md)

---

# GPP and Local Administrator Password Reuse

One historically significant scenario is:

```text
Groups.xml
    |
    v
Local Administrator Password
    |
    v
Same Password on Many Computers
```

This can produce:

```text
One Exposed Password
      |
      +--> CLIENT01
      +--> CLIENT02
      +--> CLIENT03
      +--> SERVER01
```

The blast radius can therefore be much larger than the GPO itself.

---

# Windows LAPS

Modern environments should avoid shared static local administrator passwords.

Windows LAPS provides managed local administrator passwords.

Conceptually:

```text
Computer A
 |
 v
Unique Password A

Computer B
 |
 v
Unique Password B

Computer C
 |
 v
Unique Password C
```

This breaks the common reuse model:

```text
One Local Admin Password
        |
        +--> Every Computer
```

A dedicated page should cover:

```text
active-directory/laps.md
```

---

# GPP and Service Accounts

A GPP password may belong to a domain service account.

Example:

```text
Services.xml
     |
     v
CORP\svc_backup
     |
     v
Backup Service
```

The security impact may extend to:

```text
Servers
Backups
Databases
Network Shares
Management Platforms
```

depending on the account.

---

# Service Account Analysis

For a recovered service account:

```powershell
Get-ADUser \
    -Identity 'svc_backup' \
    -Properties \
        MemberOf,
        ServicePrincipalName,
        PasswordLastSet,
        PasswordNeverExpires,
        Enabled
```

Review:

```text
Is the account enabled?
Does it have SPNs?
Does the password expire?
Which groups contain it?
Where is it used?
```

---

# GPP and Kerberoasting

If the exposed account also has an SPN:

```text
GPP Credential
     |
     v
Service Account
     |
     +--> Plaintext Password Exposure
     |
     +--> Kerberoasting Exposure
```

These are separate weaknesses.

The plaintext GPP exposure is usually the more direct credential compromise.

See:

[Kerberoasting](kerberoasting.md)

---

# GPP and Pass-the-Hash

If a plaintext password is recovered, an attacker may derive authentication material from it.

Depending on the environment:

```text
Password
   |
   +--> Normal Authentication
   |
   +--> NT Hash
   |
   +--> Kerberos Keys
```

This can enable other authentication techniques.

See:

[Pass-the-Hash](pass-the-hash.md)

and:

[Pass-the-Key](pass-the-key.md)

---

# GPP and Kerberos

A recovered domain password may support normal Kerberos authentication.

Conceptually:

```text
Password
   |
   v
Kerberos Key
   |
   v
AS-REQ
   |
   v
TGT
```

See:

[Kerberos](kerberos.md)

---

# GPP and NTLM

The same password may also support NTLM authentication where NTLM remains enabled.

See:

[NTLM](ntlm.md)

---

# GPP and Password Reuse

Do not automatically test a recovered password against:

```text
Every User
Every Server
Every Service
```

That becomes password reuse testing and can create:

```text
Account Lockouts
Monitoring Noise
Unexpected Service Behaviour
```

Credential reuse testing should be separately authorised.

---

# Safe Credential Validation

If validation is necessary, prefer:

```text
Known Account
    |
    v
Known Intended Service
    |
    v
Single Authentication Attempt
```

rather than:

```text
Credential
    |
    v
Spray Entire Domain
```

---

# NetExec Validation

Where SMB authentication is an approved validation method:

```bash
nxc smb <APPROVED_TARGET> \
    -d corp.example \
    -u svc_example \
    -p '<RECOVERED_PASSWORD>'
```

Only use an explicitly authorised target.

Do not use broad target ranges merely to determine where the credential works.

---

# Kerberos Validation

A lower-impact validation for a domain account can sometimes be to request a TGT.

Using Impacket:

```bash
impacket-getTGT \
    'corp.example/svc_example:<RECOVERED_PASSWORD>'
```

A successful TGT request demonstrates that the domain credential is valid without requiring remote execution on another system.

Check:

```bash
impacket-getTGT -h
```

for current syntax.

---

# Authentication Failure

If the recovered credential no longer works, determine whether:

```text
Password Rotated
Account Disabled
Account Deleted
Account Locked
Credential Is Local
Domain Context Incorrect
```

before concluding that the GPP file is harmless.

---

# Historical Exposure

Even an invalid credential may indicate historical exposure.

Example:

```text
2019
GPP Password Published in SYSVOL
       |
       v
2025
Password Rotated
```

The current password may be safe, but the old credential was potentially accessible for years.

Incident-response review may therefore still be appropriate.

---

# Search Beyond Policies

Do not limit SYSVOL review to:

```text
Policies
```

Also inspect authorised locations such as:

```text
Scripts
NETLOGON
Legacy Folders
Deployment Files
```

for plaintext secrets.

These may not be GPP vulnerabilities, but they are relevant credential-access findings.

---

# GPP vs Plaintext SYSVOL Credential

Keep finding types distinct.

```text
cpassword in GPP XML
```

is:

```text
Legacy GPP Password Exposure
```

while:

```text
$password = 'Secret123!'
```

inside:

```text
logon.ps1
```

is:

```text
Plaintext Credential in SYSVOL
```

The remediation and root cause overlap, but the technical mechanisms differ.

---

# GPP vs GPO ACL Abuse

Also distinguish:

```text
Read GPP Password
```

from:

```text
Modify GPO
```

The first is credential access.

The second can enable privilege escalation through Group Policy modification.

See:

[Active Directory Group Policy](group-policy.md)

---

# GPP vs SYSVOL Write Access

A user with write access to SYSVOL presents a different and potentially more severe problem.

Conceptually:

```text
Read SYSVOL
    |
    v
Expected for Domain Users
```

versus:

```text
Write SYSVOL
    |
    v
Potential Policy / Script Modification
```

Do not report normal SYSVOL read access as the vulnerability.

The vulnerability is:

```text
Sensitive Recoverable Credential
        |
        v
Stored in Domain-Readable SYSVOL
```

---

# Root Cause

The root cause is not:

```text
Authenticated Users Can Read SYSVOL
```

because SYSVOL read access is generally required for normal Group Policy operation.

The root cause is:

```text
Recoverable Credential Stored in SYSVOL
```

This distinction matters for remediation.

---

# Do Not Recommend Blocking SYSVOL

A poor remediation is:

```text
Remove Domain Users' SYSVOL Read Access
```

This can disrupt Group Policy.

Instead:

```text
Remove Credential
Rotate Credential
Remove Legacy Preference
Review SYSVOL for Additional Secrets
Use Supported Credential Management
```

---

# Detection

GPP password discovery is difficult to detect solely through authentication logs because the initial activity may be ordinary file reads from SYSVOL.

Detection should therefore combine:

```text
SYSVOL Access
     +
Endpoint Telemetry
     +
Credential Use
     +
Account Authentication
```

---

# Detection Model

```text
Domain User
    |
    v
Reads SYSVOL
    |
    v
Finds cpassword
    |
    v
Decrypts Credential
    |
    v
Authenticates as New Account
```

The strongest detection opportunity may occur at:

```text
Credential Reuse
```

rather than the initial SYSVOL read.

---

# Baseline SYSVOL Access

Normal systems access SYSVOL frequently.

Therefore:

```text
SYSVOL Read
```

alone is generally a weak signal.

More useful indicators may include:

```text
Recursive Enumeration
Large Numbers of XML Reads
Unusual Interactive Workstation Access
Security Tool Execution
Immediate Authentication as Referenced Account
```

---

# SMB Telemetry

Depending on auditing configuration, SMB-related events can provide visibility into file-share access.

Potentially relevant events include:

```text
5140
5145
```

where the applicable auditing is enabled.

---

# Event 5140

Event:

```text
5140
```

records network share access under applicable audit configuration.

SYSVOL activity may appear as access to:

```text
\\*\SYSVOL
```

However, because legitimate SYSVOL access is common, this event should not be used alone as a high-confidence alert.

---

# Event 5145

Event:

```text
5145
```

can provide more detailed share-object access information where detailed file share auditing is configured.

This can potentially help identify unusual access to:

```text
Groups.xml
Services.xml
ScheduledTasks.xml
```

and similar files.

Again, baseline legitimate Group Policy activity.

---

# Endpoint Detection

EDR may identify:

```text
Recursive SYSVOL Searching
Known GPP Discovery Utilities
PowerShell Searching for cpassword
gpp-decrypt Execution
Unusual XML Collection
```

Detection should not rely only on executable names.

---

# Detect Credential Reuse

Suppose:

```text
Alice
```

reads:

```text
Groups.xml
```

and shortly afterwards:

```text
svc_deploy
```

authenticates from Alice's workstation.

That correlation is much stronger:

```text
SYSVOL Discovery
      |
      v
Credential Recovery
      |
      v
New Identity Authentication
```

---

# Authentication Events

Relevant events may include:

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
Kerberos
NTLM
Explicit Credentials
Success / Failure
```

---

# Event 4648

Event:

```text
4648
```

can indicate that a process attempted to log on using explicitly supplied credentials.

This can be useful when a recovered GPP password is subsequently used from a Windows system.

It should be correlated with:

```text
Source Process
Source Host
Target Server
Account
```

---

# Kerberos Correlation

For a domain credential:

```text
GPP Discovery
      |
      v
4768
      |
      v
New Account TGT
      |
      v
4769
      |
      v
Service Access
```

may reveal credential use.

---

# NTLM Correlation

Where the recovered credential is used through NTLM:

```text
GPP Discovery
      |
      v
4624 / 4776
      |
      v
New Identity
```

may provide evidence.

---

# Defensive Hunt

A defensive hunt should answer:

```text
Does SYSVOL contain cpassword?
        |
        +--> No
        |     |
        |     v
        |   Continue Periodic Review
        |
        +--> Yes
              |
              v
       Identify Credential
              |
              v
       Identify Account
              |
              v
       Rotate Credential
              |
              v
       Remove GPP Artefact
              |
              v
       Hunt for Historical Use
```

---

# Enterprise-Wide Search

Administrators should search all domains in the forest where appropriate.

For each domain:

```text
Domain
 |
 v
SYSVOL
 |
 v
Search cpassword
```

Do not assume checking one domain covers:

```text
Child Domains
Separate Forests
Legacy Domains
```

---

# Search Backups

Removing the live GPP file does not remove copies from:

```text
Backups
File Archives
Git Repositories
Ticket Attachments
Documentation
Old SYSVOL Copies
```

Sensitive credential artefacts should be identified and protected or removed according to retention requirements.

---

# Hardening

The primary remediation model is:

```text
Find cpassword
      |
      v
Identify Credential
      |
      v
Rotate Credential
      |
      v
Remove Legacy GPP Configuration
      |
      v
Verify SYSVOL
      |
      v
Review Account Privilege
      |
      v
Search for Additional Copies
```

---

# Rotate the Credential

Deleting the XML file is not sufficient.

The password should be considered exposed.

Therefore:

```text
Delete File
    |
    X
Credential Secured
```

Instead:

```text
Remove Exposure
      +
Rotate Credential
      =
Remediation
```

---

# Remove Legacy Preference Configuration

Use supported Group Policy management procedures to remove obsolete preference configuration.

Do not simply manipulate replicated SYSVOL content manually without understanding the GPO.

---

# Use Windows LAPS

For local administrator passwords, use:

```text
Windows LAPS
```

instead of static credentials embedded in Group Policy Preferences.

See:

```text
active-directory/laps.md
```

---

# Use gMSA

For compatible Windows services, consider:

```text
gMSA
```

instead of static domain service-account passwords.

See:

```text
active-directory/gmsa.md
```

---

# Use Secret Management

For application and deployment secrets, use an approved secret-management solution rather than:

```text
SYSVOL
Scripts
GPO XML
Shared Configuration Files
```

---

# Least Privilege

Review the recovered account.

Ask:

```text
Does it need these groups?
Does it need local administrator rights?
Does it need interactive logon?
Does it need access to every server?
Does it need a static password?
```

Reducing account privilege limits the impact of future credential exposure.

---

# Password Rotation Policy

Service accounts with manually managed passwords should have:

```text
Long Random Passwords
Managed Rotation
Documented Ownership
Limited Scope
Monitoring
```

Where practical, replace them with managed identities such as gMSA.

---

# Local Administrator Password Uniqueness

Do not use one static local administrator password across many systems.

Prefer:

```text
Unique Password Per Computer
```

managed through Windows LAPS.

---

# Remove Disabled Legacy GPOs

Disabled GPOs may still leave files in SYSVOL.

Therefore:

```text
GPO Disabled
```

does not automatically mean:

```text
Credential Removed
```

Review and clean up obsolete policy artefacts.

---

# Review Unlinked GPOs

An unlinked GPO may still contain:

```text
cpassword
```

and remain readable in SYSVOL.

Therefore:

```text
GPO Not Applied
```

does not equal:

```text
Credential Not Exposed
```

---

# Review Old Domain Migrations

Domains that have undergone:

```text
Migration
Acquisition
Restructuring
Upgrade
```

may contain old GPOs and legacy preference files.

These should be specifically included in reviews.

---

# Incident Response

If a GPP password is discovered:

```text
Locate GPP File
      |
      v
Preserve Evidence
      |
      v
Identify Account
      |
      v
Determine Password Validity
      |
      v
Determine Privilege
      |
      v
Rotate Credential
      |
      v
Remove GPP Exposure
      |
      v
Search Authentication History
      |
      v
Search for Additional Copies
```

---

# Preserve Evidence Safely

Record:

```text
GPO Name
GPO GUID
File Path
Preference Type
Username
File Modification Time
cpassword Present
Account Status
Account Privilege
PasswordLastSet
```

Avoid storing:

```text
Full Plaintext Password
```

unless required by evidence-handling procedures.

---

# Investigate Authentication History

If the credential was valid, determine whether it may have been abused.

Review:

```text
4624
4625
4648
4768
4769
4776
```

and relevant endpoint telemetry.

Ask:

```text
Which systems authenticated the account?
Which source hosts were used?
Were these expected?
Did activity occur outside normal hours?
Was the account used interactively?
```

---

# Investigate Account Changes

Review:

```text
Password Changes
Group Membership Changes
Delegated Rights
Service Configuration
Scheduled Tasks
Logon Rights
```

to determine whether the exposed identity was further abused.

---

# Search for the Same Credential Elsewhere

If permitted, investigate whether the same exposed credential was stored in:

```text
Scripts
Configuration Files
Deployment Systems
Password Vault Imports
Documentation
Backups
```

Avoid broad password spraying unless explicitly authorised.

---

# Purple Team Exercise

A safe GPP detection exercise can use:

```text
Dedicated Test GPO Artefact
      |
      v
Synthetic cpassword Indicator
      |
      v
Read-Only Discovery
      |
      v
Defender Detection
```

However, modern Group Policy management tools should not be intentionally configured to recreate the insecure legacy mechanism in production.

Prefer a controlled lab or synthetic file for detection engineering.

---

# Purple Team Workflow

```text
Red Team
   |
   v
Enumerate SYSVOL
   |
   v
Locate Controlled Test Artefact
   |
   v
Blue Team
   |
   v
Identify Recursive Enumeration
   |
   v
Correlate Subsequent Test Authentication
```

---

# Purple Team Questions

Defenders should be able to answer:

```text
Who accessed the file?
From which host?
Which GPO contained it?
Which credential was exposed?
Was the credential still valid?
Where was the credential used?
Was the account privileged?
Was the file removed?
Was the credential rotated?
Are additional cpassword values present?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect SYSVOL enumeration
Time to identify cpassword access
Time to identify exposed account
Time to detect credential reuse
Time to disable or rotate credential
Time to locate additional GPP passwords
Time to complete remediation
```

---

# Reporting

Possible finding titles include:

```text
Recoverable Password Stored in Group Policy Preferences
```

```text
Legacy Group Policy Preference Exposes Domain Credential
```

```text
GPP cpassword Exposes Service Account Credential
```

```text
Domain-Readable SYSVOL File Contains Recoverable Credential
```

---

# Example Finding

```text
Finding:
Recoverable Service Account Password Stored in Group Policy Preferences

Affected GPO:
Legacy Server Configuration

GPO GUID:
{EXAMPLE-GUID}

Affected File:
\\corp.example\SYSVOL\corp.example\Policies\
{EXAMPLE-GUID}\Machine\Preferences\Services\Services.xml

Affected Account:
CORP\svc_legacy

Description:
A legacy Group Policy Preference file stored within SYSVOL contains a
cpassword value associated with the CORP\svc_legacy account.

SYSVOL is readable by ordinary authenticated domain users as part of
normal Group Policy operation.

The cpassword value uses the historical Group Policy Preferences
encryption mechanism for which the cryptographic key is publicly
documented. Consequently, the stored password is recoverable by users
who can access the file.

The credential was recovered during the authorised assessment to
confirm the exposure. The plaintext password has been omitted from this
report.

Impact:
A compromised domain user could recover the password associated with
CORP\svc_legacy.

The resulting impact depends on the privileges, group memberships,
service usage, and systems accessible by the affected account.

If the same credential is reused across multiple systems or services,
the exposure could enable lateral movement or privilege escalation.

Recommendation:
Immediately rotate the affected credential.

Remove the legacy Group Policy Preference configuration containing the
cpassword value.

Search the entire domain SYSVOL for additional cpassword values and
other embedded credentials.

Review the privileges and authentication history of the affected
account.

Where applicable, replace static local administrator passwords with
Windows LAPS and service-account passwords with managed identities such
as gMSA.
```

---

# Example Historical Finding

```text
Finding:
Legacy GPP Password Artefact Remains in SYSVOL

Affected Account:
CORP\svc_old

Current Account Status:
Disabled

Description:
A legacy Group Policy Preference XML file containing a cpassword value
was identified in SYSVOL.

The referenced account is currently disabled and the exposed password
was determined to be historical.

Although immediate exploitation of the referenced account was not
demonstrated, the file contains recoverable credential material and has
been accessible to domain users.

Impact:
The artefact represents historical credential exposure and may reveal
password patterns or credentials that were previously valid.

If the password was reused by other accounts or systems, residual risk
may remain.

Recommendation:
Remove the obsolete GPP credential artefact, verify that the exposed
password is not reused, review historical authentication activity where
appropriate, and search SYSVOL for additional legacy credentials.
```

---

# Severity

Severity depends on the exposed credential.

A useful model is:

```text
GPP Exposure
     +
Account Privilege
     +
Credential Validity
     +
Credential Reuse
     +
Reachability
     =
Severity
```

Example:

```text
Old cpassword
     |
     v
Deleted Account
```

may have limited current impact.

Compare:

```text
cpassword
   |
   v
Active Domain Service Account
   |
   v
Local Admin on Many Servers
```

which may represent high or critical risk depending on the resulting attack path.

---

# Evidence Checklist

Record:

```text
Domain
Domain Controller
SYSVOL Path
GPO Name
GPO GUID
Preference File
Preference Type
Username
Account Type
cpassword Present
File Creation / Modification Time
Account Enabled
PasswordLastSet
Group Membership
SPNs
Resulting Privilege
Credential Validity
Validation Performed
Authentication Target
Relevant Events
Cleanup Actions
```

Do not include the full recovered password unless explicitly required by the evidence-handling process.

---

# GPP Password Assessment Checklist

## Preparation

- [ ] Confirm SYSVOL enumeration is authorised
- [ ] Confirm credential decryption is authorised
- [ ] Confirm credential validation is authorised
- [ ] Confirm credential reuse testing restrictions
- [ ] Prepare secure evidence storage
- [ ] Define credential redaction procedure

## SYSVOL Enumeration

- [ ] Identify domain
- [ ] Identify domain controllers
- [ ] Access SYSVOL
- [ ] Enumerate `Policies`
- [ ] Enumerate `Scripts`
- [ ] Search XML files
- [ ] Search for `cpassword`
- [ ] Search for plaintext credential keywords
- [ ] Review legacy directories
- [ ] Review disabled GPOs
- [ ] Review unlinked GPOs

## GPP Files

- [ ] Review `Groups.xml`
- [ ] Review `Services.xml`
- [ ] Review scheduled-task preference XML
- [ ] Review `Drives.xml`
- [ ] Review `DataSources.xml`
- [ ] Review `Printers.xml`
- [ ] Review other files containing `cpassword`

## Context

- [ ] Identify GPO GUID
- [ ] Resolve GPO name
- [ ] Determine GPO status
- [ ] Determine GPO links
- [ ] Determine affected users
- [ ] Determine affected computers
- [ ] Determine preference purpose

## Credential Analysis

- [ ] Identify username
- [ ] Determine local vs domain account
- [ ] Determine whether account exists
- [ ] Determine whether account is enabled
- [ ] Review `PasswordLastSet`
- [ ] Review group membership
- [ ] Review nested privileges
- [ ] Review SPNs
- [ ] Review BloodHound paths
- [ ] Determine likely credential scope

## Validation

- [ ] Determine whether decryption is necessary
- [ ] Decrypt only where required
- [ ] Do not call decryption cracking
- [ ] Prefer single controlled authentication
- [ ] Prefer Kerberos TGT validation for domain account where appropriate
- [ ] Avoid domain-wide password reuse testing
- [ ] Avoid remote execution unless specifically required
- [ ] Record minimum evidence
- [ ] Redact plaintext credential

## Detection

- [ ] Review 5140
- [ ] Review 5145
- [ ] Review 4624
- [ ] Review 4625
- [ ] Review 4648
- [ ] Review 4768
- [ ] Review 4769
- [ ] Review 4776
- [ ] Correlate SYSVOL access with new identity authentication
- [ ] Review EDR telemetry
- [ ] Baseline legitimate Group Policy activity

## Remediation

- [ ] Rotate exposed credential
- [ ] Remove legacy GPP password configuration
- [ ] Search entire SYSVOL
- [ ] Search for other copies
- [ ] Review backups
- [ ] Review account privilege
- [ ] Review account authentication history
- [ ] Deploy Windows LAPS for local administrator passwords
- [ ] Consider gMSA for services
- [ ] Use approved secret management
- [ ] Remove obsolete GPOs
- [ ] Review legacy migration artefacts

## Cleanup

- [ ] Delete local SYSVOL copies
- [ ] Delete plaintext password notes
- [ ] Delete temporary credential files
- [ ] Remove Kerberos test caches
- [ ] Secure retained evidence
- [ ] Verify no directory changes were made
- [ ] Confirm client notified of credential requiring rotation

---

# GPP Password Testing Model

The basic model is:

```text
Authenticated Domain User
          |
          v
SYSVOL
          |
          v
GPP XML
          |
          v
cpassword
          |
          v
Recoverable Password
```

The encryption model is:

```text
Password
   |
   v
AES Encryption
   |
   v
cpassword
   |
   +
Publicly Documented Key
   |
   v
Password Recovery
```

The account model is:

```text
cpassword
    |
    v
Associated Username
    |
    v
Account
    |
    v
Privileges
```

The GPO context model is:

```text
GPP File
   |
   v
GPO GUID
   |
   v
GPO
   |
   v
Linked OU / Domain
   |
   v
Affected Systems
```

The attack-path model is:

```text
Low-Privilege User
       |
       v
Read SYSVOL
       |
       v
Recover Credential
       |
       v
Service Account
       |
       v
Privileged Access
```

The local password reuse model is:

```text
Groups.xml
    |
    v
Local Administrator Password
    |
    +--> Workstation 1
    |
    +--> Workstation 2
    |
    +--> Server 1
    |
    +--> Server 2
```

The remediation model is:

```text
Find cpassword
      |
      v
Identify Account
      |
      v
Rotate Password
      |
      v
Remove GPP Artefact
      |
      v
Search SYSVOL
      |
      v
Review Historical Use
```

The detection model is:

```text
SYSVOL Enumeration
       |
       v
Credential Discovery
       |
       v
Credential Decryption
       |
       v
Authentication as New Identity
       |
       v
Privilege / Lateral Movement
```

The most important distinction is:

```text
Domain Users Can Read SYSVOL
        |
        X
Vulnerability
```

because normal SYSVOL read access is required.

Instead:

```text
Domain-Readable SYSVOL
        +
Recoverable Credential
        =
Credential Exposure
```

Another important distinction is:

```text
MS14-025 Installed
       |
       X
Existing cpassword Removed
```

The correct model is:

```text
MS14-025
   |
   v
Prevents Creation / Modification
of Affected Password Preferences
   |
   X
Does Not Automatically Remove
Existing Legacy Password Artefacts
```

For penetration testing:

```text
Enumerate SYSVOL
      |
      v
Search cpassword
      |
      v
Identify Account
      |
      v
Determine Privilege
      |
      v
Determine Whether Decryption Is Needed
      |
      v
Validate Minimum Necessary Impact
```

For defenders:

```text
Search Entire SYSVOL
      |
      v
Remove Legacy GPP Credentials
      |
      v
Rotate Every Exposed Credential
      |
      v
Review Historical Authentication
      |
      v
Deploy Managed Credential Solutions
```

The final question should always be:

```text
What privilege does the exposed credential provide?
```

rather than simply:

```text
Did we find cpassword?
```

That distinction turns a legacy artefact into a properly understood Active Directory attack path.

---

# Related Notes

Credential Access overview:

[Active Directory Credential Access](credential-access.md)

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Group Policy:

[Active Directory Group Policy](group-policy.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Password Spraying:

[Password Spraying](password-spraying.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

BloodHound:

[BloodHound](bloodhound.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

The following Credential Access pages complement GPP Passwords:

```text
active-directory/laps.md
active-directory/gmsa.md
active-directory/shadow-credentials.md
active-directory/ntds.md
```

---

# References

## Microsoft - MS14-025

[Microsoft Security Bulletin MS14-025](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Group Policy Preferences

[Microsoft - Group Policy Preferences](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn581922(v=ws.11)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Group Policy

[Microsoft - Group Policy Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SYSVOL

[Microsoft - DFS Replication for SYSVOL](https://learn.microsoft.com/en-us/windows-server/storage/dfs-replication/migrate-sysvol-to-dfsr){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - gMSA

[Microsoft - Group Managed Service Accounts](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Auditing

[Microsoft - Event 5140](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5140){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 5145](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5145){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4648](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4648){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket Get-GPPPassword.py](https://github.com/fortra/impacket/blob/master/examples/Get-GPPPassword.py){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Unsecured Credentials: Group Policy Preferences](https://attack.mitre.org/techniques/T1552/006/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Credentials from Password Stores](https://attack.mitre.org/techniques/T1555/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Group Policy Preference password exposure is a legacy Active Directory weakness that remains relevant because old credential-bearing files can survive long after the vulnerable configuration mechanism has been patched.

The fundamental relationship is:

```text
Domain User
    |
    v
SYSVOL Read Access
    |
    v
Legacy GPP XML
    |
    v
cpassword
    |
    v
Recoverable Credential
```

The key technical point is:

```text
cpassword
    |
    v
Reversible Encryption
```

and:

```text
Required AES Key
    |
    v
Publicly Documented
```

Therefore:

```text
Possession of cpassword
        |
        v
Potential Plaintext Password Recovery
```

without requiring conventional password cracking.

The patching model is equally important:

```text
MS14-025
   |
   v
Stops Administrators Creating
Affected Password Preferences
```

but:

```text
MS14-025
   |
   X
Automatically Cleans Historical SYSVOL
```

This means every mature Active Directory assessment should include a read-only search for:

```text
cpassword
```

across SYSVOL.

The assessment should then move beyond discovery:

```text
cpassword
    |
    v
Which Account?
    |
    v
Still Enabled?
    |
    v
Password Still Valid?
    |
    v
What Privilege?
    |
    v
Where Is It Used?
```

The correct security interpretation is not:

```text
SYSVOL Is Readable
      =
Vulnerability
```

It is:

```text
SYSVOL Is Readable
      +
Recoverable Credential Stored There
      =
Credential Exposure
```

For penetration testers:

```text
Discover
   |
   v
Contextualise
   |
   v
Determine Privilege
   |
   v
Decrypt Only If Necessary
   |
   v
Validate Minimally
   |
   v
Protect Evidence
```

For defenders:

```text
Search
 |
 v
Identify
 |
 v
Rotate
 |
 v
Remove
 |
 v
Hunt
 |
 v
Replace with Managed Credentials
```

Where the exposed password belongs to a local administrator account, the preferred modern design is:

```text
Static Shared Password
        |
        X

Windows LAPS
     |
     v
Unique Managed Password
     |
     v
Per Computer
```

Where it belongs to a service account, consider:

```text
Static Service Password
        |
        X

gMSA
 |
 v
Automatically Managed Credential
```

where the application supports it.

The final objective is not merely to remove:

```text
cpassword
```

but to eliminate the broader credential-management pattern that allowed a reusable secret to be stored in a domain-readable location.
