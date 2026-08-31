# Active Directory Credential Access

Credential Access is the process of identifying, obtaining, or recovering authentication material that can be used to authenticate as users, computers, or services within an Active Directory environment.

Active Directory environments contain many different forms of authentication material.

Examples include:

```text
Passwords
NT Hashes
Kerberos Keys
Kerberos Tickets
Certificates
Private Keys
Service Account Credentials
Computer Account Credentials
Managed Service Account Secrets
Cached Credentials
LSASS Credentials
DPAPI-Protected Secrets
NTDS.dit Credential Data
Group Policy Preference Credentials
LAPS Passwords
Application Credentials
Configuration File Secrets
```

From an attack-path perspective:

```text
Initial Access
     |
     v
Credential Access
     |
     v
Additional Identity
     |
     v
Additional Permissions
     |
     v
Lateral Movement
     |
     v
Privilege Escalation
```

Credential Access is therefore not a single technique.

It is a collection of techniques for discovering and obtaining authentication material from:

```text
Active Directory
Endpoints
Domain Controllers
SYSVOL
Memory
Registry
Files
Applications
Certificates
Backups
Management Platforms
```

A useful assessment model is:

```text
Identity
   |
   v
Accessible Credential Source
   |
   v
Credential Material
   |
   v
Authentication Capability
   |
   v
Resulting Access
```

!!! warning "Authorised testing only"
    Credential-access testing can expose highly sensitive authentication material and may affect many systems beyond the original test target. Prefer read-only enumeration and dedicated test identities wherever possible. Do not dump production credentials merely to demonstrate that a permission exists when the exposure can be proven through ACLs, metadata, configuration, or controlled test credentials. Treat hashes, tickets, certificates, private keys, passwords, credential databases, and memory dumps as sensitive evidence and securely remove temporary copies after the engagement.

---

# Credential Access Is Broader Than Passwords

A common mistake is to think:

```text
Credential
    =
Password
```

In Active Directory, many objects can function as credentials.

For example:

```text
Password
   |
   +--> Interactive Authentication
   |
   +--> NTLM
   |
   +--> Kerberos Key Derivation
```

But authentication may also occur using:

```text
NT Hash
Kerberos AES Key
TGT
Service Ticket
Certificate + Private Key
Computer Account Password
```

Therefore:

```text
No Plaintext Password
```

does not mean:

```text
No Credential Compromise
```

---

# Credential Material Model

A useful classification is:

```text
Credential Material
      |
      +--> Knowledge
      |
      |     +--> Password
      |
      +--> Password-Derived Material
      |
      |     +--> NT Hash
      |     +--> Kerberos AES Keys
      |
      +--> Tickets
      |
      |     +--> TGT
      |     +--> TGS
      |
      +--> Certificates
      |
      |     +--> Certificate
      |     +--> Private Key
      |
      +--> Managed Secrets
      |
      |     +--> LAPS
      |     +--> gMSA
      |
      +--> Stored Credentials
            |
            +--> DPAPI
            +--> Credential Manager
            +--> Configuration Files
```

---

# Credential Sources

During an Active Directory assessment, credentials may exist in several layers:

```text
Domain
 |
 +--> NTDS.dit
 +--> AD Attributes
 +--> LAPS
 +--> gMSA
 +--> Certificates
 |
Endpoints
 |
 +--> LSASS
 +--> SAM
 +--> LSA Secrets
 +--> Cached Logons
 +--> DPAPI
 +--> Credential Manager
 |
SYSVOL
 |
 +--> GPP
 +--> Scripts
 +--> Configuration Files
 |
Applications
 |
 +--> Service Credentials
 +--> Database Credentials
 +--> API Secrets
 +--> Deployment Credentials
```

---

# Credential Access Assessment Workflow

A structured workflow is:

```text
Enumerate Identity
      |
      v
Enumerate Accessible Sources
      |
      v
Identify Credential Material
      |
      v
Determine Access Requirements
      |
      v
Assess Resulting Identity
      |
      v
Map Attack Path
      |
      v
Validate Safely
      |
      v
Collect Minimum Evidence
      |
      v
Cleanup
```

---

# Start with the Controlled Identity

Before searching for credentials, understand the identity already controlled.

Record:

```text
Username
Domain
SID
Group Membership
Privileges
Local Rights
Directory ACLs
Computer Access
Share Access
```

Example:

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
[System.Security.Principal.WindowsIdentity]::GetCurrent()
```

---

# Why Identity Context Matters

Suppose the controlled identity is:

```text
CORP\alice
```

The correct question is not:

```text
Can credentials be dumped somewhere?
```

Instead:

```text
What credential sources can Alice legitimately reach?
```

For example:

```text
Alice
 |
 +--> Read SYSVOL
 |
 +--> Read Deployment Share
 |
 +--> Read LAPS Password for CLIENT01
 |
 +--> Read gMSA Password
 |
 +--> Local Admin on SERVER01
```

Each relationship creates a different credential-access opportunity.

---

# Credential Access and BloodHound

BloodHound can help identify credential-related attack paths.

Examples include relationships involving:

```text
AdminTo
HasSession
ReadLAPSPassword
ReadGMSAPassword
AddKeyCredentialLink
DCSync
Certificate Relationships
```

depending on BloodHound version and collected data.

A useful model is:

```text
Controlled User
      |
      v
BloodHound
      |
      v
Credential-Relevant Relationship
      |
      v
Target Identity / System
```

See:

[BloodHound](bloodhound.md)

---

# Credential Access and Active Directory ACLs

Many credential exposures are fundamentally authorization problems.

Examples:

```text
User
 |
 v
Read LAPS Password
 |
 v
Computer
```

```text
User
 |
 v
Read gMSA Password
 |
 v
Service Account
```

```text
User
 |
 v
Replication Rights
 |
 v
Domain
 |
 v
DCSync
```

```text
User
 |
 v
Write Key Credential Link
 |
 v
Target Account
```

Therefore credential-access testing should be closely connected to ACL analysis.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# Credential Access Categories

A practical Active Directory credential-access review can be divided into:

```text
1. Directory-Stored Credentials
2. SYSVOL Credentials
3. Managed Passwords
4. Endpoint Credentials
5. Domain Controller Credentials
6. Kerberos Credentials
7. Certificate Credentials
8. Application Credentials
9. Backup Credentials
10. Cloud / Hybrid Credentials
```

---

# Directory-Stored Credential Material

Active Directory contains information that may directly or indirectly expose authentication material.

Examples include:

```text
LAPS Password Attributes
gMSA Managed Passwords
Password-Related Metadata
Certificate Credentials
Key Credentials
Replication Secrets
```

Access is normally controlled through directory ACLs.

---

# SYSVOL Credential Sources

SYSVOL is intentionally accessible to domain members because Group Policy must be distributed throughout the domain.

Typical location:

```text
\\corp.example\SYSVOL
```

Potentially sensitive content includes:

```text
Group Policy Preferences
PowerShell Scripts
Batch Scripts
VBScript
Configuration Files
Deployment Scripts
Legacy Passwords
Service Credentials
```

---

# Enumerate SYSVOL

Windows:

```cmd
dir \\corp.example\SYSVOL
```

PowerShell:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL' \
    -Recurse \
    -File \
    -ErrorAction SilentlyContinue
```

---

# Search SYSVOL for Credential Keywords

A read-only search:

```powershell
Get-ChildItem \
    '\\corp.example\SYSVOL' \
    -Recurse \
    -File \
    -ErrorAction SilentlyContinue |
    Select-String \
        -Pattern 'password|passwd|pwd|secret|token|apikey|cpassword' \
        -CaseSensitive:$false \
        -ErrorAction SilentlyContinue
```

Matches require manual validation.

A string containing:

```text
password
```

does not automatically contain a real credential.

---

# Group Policy Preference Passwords

Historical Group Policy Preferences could store passwords using:

```text
cpassword
```

inside XML configuration.

Potential files include:

```text
Groups.xml
Services.xml
ScheduledTasks.xml
Drives.xml
DataSources.xml
Printers.xml
```

Example path:

```text
\\corp.example\SYSVOL\corp.example\Policies\
{GPO-GUID}\Machine\Preferences\Groups\Groups.xml
```

A dedicated page should cover this issue:

```text
active-directory/gpp-passwords.md
```

---

# Search for cpassword

Windows:

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

This is read-only.

---

# LAPS

Local Administrator Password Solution technologies provide managed local administrator passwords.

Two broad implementations may be encountered:

```text
Legacy Microsoft LAPS
Windows LAPS
```

The security question is:

```text
Who can read the password?
```

Conceptually:

```text
Computer
 |
 v
LAPS Password Attribute
 |
 v
Directory ACL
 |
 v
Authorised Reader
```

An excessive read permission can become:

```text
Controlled User
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

LAPS should be covered in detail in:

```text
active-directory/laps.md
```

---

# Legacy LAPS Attributes

Legacy Microsoft LAPS commonly uses attributes including:

```text
ms-Mcs-AdmPwd
ms-Mcs-AdmPwdExpirationTime
```

The password attribute is sensitive.

Do not retrieve production LAPS passwords unless required for authorised validation.

---

# Windows LAPS Attributes

Windows LAPS introduces attributes including:

```text
msLAPS-Password
msLAPS-PasswordExpirationTime
msLAPS-EncryptedPassword
msLAPS-EncryptedPasswordHistory
```

depending on configuration.

Windows LAPS can also protect password information through encryption.

---

# LAPS Enumeration

Where the Windows LAPS PowerShell module is available, administrators and authorised testers can inspect configured rights using supported LAPS cmdlets.

Always inspect the installed module:

```powershell
Get-Command *Laps*
```

and:

```powershell
Get-Help Find-LapsADExtendedRights -Full
```

where available.

The goal during assessment is initially:

```text
Identify Readers
```

not:

```text
Retrieve Every Password
```

---

# gMSA

Group Managed Service Accounts provide automatically managed service-account passwords.

They are commonly used for:

```text
Windows Services
Scheduled Tasks
IIS Application Pools
Enterprise Applications
```

The relevant credential material is represented through:

```text
msDS-ManagedPassword
```

for authorised principals.

---

# gMSA Security Model

```text
gMSA
 |
 v
msDS-ManagedPassword
 |
 v
Directory ACL
 |
 v
Authorised Computer / Principal
```

If an attacker controls a principal authorised to retrieve the managed password:

```text
Controlled Principal
        |
        v
Read Managed Password
        |
        v
Derive Authentication Material
        |
        v
Authenticate as gMSA
```

A dedicated page should cover:

```text
active-directory/gmsa.md
```

---

# Shadow Credentials

Key Credential Link abuse involves the:

```text
msDS-KeyCredentialLink
```

attribute.

This is different from stealing an existing password.

Instead, an attacker with sufficient write permissions may be able to introduce alternative key-based authentication material for a target account.

Conceptually:

```text
Controlled User
      |
      v
Write msDS-KeyCredentialLink
      |
      v
Target Account
      |
      v
Attacker-Controlled Key Credential
      |
      v
Certificate-Based Authentication
```

This should be treated as credential-access and persistence-related behaviour.

A dedicated page should cover:

```text
active-directory/shadow-credentials.md
```

---

# Endpoint Credential Sources

Windows endpoints may contain credentials or credential-derived material in:

```text
LSASS
SAM
SECURITY Hive
Credential Manager
DPAPI
Registry
Configuration Files
Browser Data
PowerShell History
Application Files
Scheduled Tasks
Services
```

The ability to access these sources depends heavily on local privilege.

---

# Local Administrator Context

Credential access changes substantially when the controlled principal becomes:

```text
Local Administrator
```

Conceptually:

```text
Domain User
    |
    v
Local Administrator
    |
    v
Protected Local Resources
    |
    v
Potential Credential Material
```

This is why local administrative relationships are important during Active Directory attack-path analysis.

---

# LSASS

The Local Security Authority Subsystem Service:

```text
lsass.exe
```

plays a central role in Windows authentication.

Depending on:

```text
Windows Version
Authentication Packages
Credential Guard
LSA Protection
Logged-On Sessions
Security Configuration
```

LSASS may contain authentication material useful to an attacker.

---

# LSASS Credential Exposure

Potential material historically associated with LSASS includes:

```text
NT Hashes
Kerberos Tickets
Kerberos Keys
Authentication Package Data
```

The exact material available depends on system configuration and current sessions.

Do not assume plaintext passwords will be available.

---

# LSASS Testing Safety

Dumping LSASS is intrusive and frequently triggers endpoint security controls.

During an assessment:

```text
Local Admin Confirmed
       |
       v
Is Credential Dump Required?
       |
       +--> No
       |     |
       |     v
       |   Stop
       |
       +--> Yes
             |
             v
      Explicitly Authorised?
             |
             +--> No -> Stop
             |
             +--> Yes
                   |
                   v
             Controlled Validation
```

Often the existence of local administrative access is already sufficient evidence for the primary finding.

---

# Credential Guard

Windows Defender Credential Guard uses virtualization-based security to help isolate secrets.

Credential Guard can reduce exposure of certain credential material.

Its presence should be recorded during endpoint security assessment.

PowerShell/system configuration methods can be used to determine whether virtualization-based security protections are configured and running.

---

# LSA Protection

LSA protection can run LSASS as a protected process.

This raises the barrier for unauthorized access to LSASS memory.

Credential Guard and LSA protection are complementary but distinct controls.

---

# SAM

The local Security Account Manager database stores local account password hashes.

Relevant registry hive:

```text
SAM
```

Access to the raw hive normally requires elevated privileges.

The associated boot/system key material is required to interpret protected secrets.

---

# Local SAM Model

```text
Local User Password
       |
       v
NT Hash
       |
       v
SAM
```

This is separate from domain credential storage.

---

# Local vs Domain Credentials

A local account:

```text
.\Administrator
```

is different from:

```text
CORP\Administrator
```

Likewise:

```text
Local SAM Hash
```

is not automatically:

```text
Domain NT Hash
```

This distinction is essential during reporting.

---

# LSA Secrets

Windows can store system and service-related secrets protected by the Local Security Authority.

Potential examples include:

```text
Service Account Secrets
Machine Account Secrets
Cached Authentication Material
```

Access normally requires elevated privileges.

---

# Cached Domain Logons

Windows may cache information that allows users to log on when a domain controller is unavailable.

These cached values are not equivalent to reusable NT hashes.

Conceptually:

```text
Cached Domain Credential
       |
       v
Offline Logon Verification
```

They are designed differently from normal NTLM credential material.

Do not report cached domain logon values as:

```text
NT Hashes
```

---

# DPAPI

Windows Data Protection API:

```text
DPAPI
```

protects many user and system secrets.

Applications can use DPAPI to encrypt data tied to:

```text
User Context
```

or:

```text
Machine Context
```

Potential DPAPI-protected data includes:

```text
Credential Manager Secrets
Browser Credentials
Application Secrets
Certificates
Private Keys
Wi-Fi Credentials
```

depending on application and system configuration.

---

# DPAPI Model

```text
User Credential / Machine Secret
          |
          v
DPAPI Key Hierarchy
          |
          v
Master Key
          |
          v
Protected Application Secret
```

Obtaining a DPAPI blob does not necessarily mean the plaintext secret has been recovered.

---

# Credential Manager

Windows Credential Manager can store:

```text
Windows Credentials
Generic Credentials
Application Credentials
```

Native enumeration:

```cmd
cmdkey /list
```

This shows stored credential targets but does not normally reveal plaintext passwords.

---

# PowerShell History

PowerShell command history may reveal sensitive information if administrators entered secrets directly on the command line.

Common location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Review:

```powershell
Get-Content \
    (Get-PSReadLineOption).HistorySavePath
```

where authorised.

Search carefully for:

```text
-password
-credential
token
secret
key
```

---

# Configuration Files

Common credential locations include:

```text
web.config
appsettings.json
app.config
*.ini
*.xml
*.yml
*.yaml
*.conf
*.config
.env
```

Searches should be targeted rather than indiscriminately copying entire file systems.

---

# Example PowerShell Search

```powershell
Get-ChildItem \
    'C:\inetpub' \
    -Recurse \
    -File \
    -ErrorAction SilentlyContinue |
    Select-String \
        -Pattern 'password|passwd|pwd|secret|token|connectionString' \
        -CaseSensitive:$false \
        -ErrorAction SilentlyContinue
```

Use application-specific paths whenever possible.

---

# Service Credentials

Windows services may run under:

```text
LocalSystem
LocalService
NetworkService
Domain User
gMSA
Virtual Account
```

Enumerate:

```powershell
Get-CimInstance Win32_Service |
    Select-Object \
        Name,
        StartName,
        State,
        PathName
```

Domain user service accounts deserve further review.

---

# Scheduled Task Credentials

Scheduled tasks may run under domain or local identities.

Native enumeration:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask |
    Select-Object \
        TaskName,
        TaskPath,
        State
```

The presence of a privileged task does not mean its password is directly retrievable.

---

# IIS Application Pools

IIS applications may use:

```text
ApplicationPoolIdentity
NetworkService
LocalSystem
Domain Service Account
gMSA
```

Review application-pool identities when assessing Windows web servers.

Avoid extracting secrets unless required.

---

# Network Shares

Credential material frequently appears on administrative or deployment shares.

Examples:

```text
Software
Deployment
Scripts
Backups
IT
Install
Config
DevOps
```

The attack model is:

```text
Domain User
     |
     v
Readable Share
     |
     v
Configuration / Script
     |
     v
Credential
```

---

# Share Enumeration

NetExec can help identify accessible SMB shares.

General pattern:

```bash
nxc smb <TARGET> \
    -u '<USER>' \
    -p '<PASSWORD>' \
    --shares
```

For a domain account:

```bash
nxc smb fileserver.corp.example \
    -d corp.example \
    -u alice \
    -p '<PASSWORD>' \
    --shares
```

Check:

```bash
nxc smb --help
```

for the installed version.

---

# Impacket smbclient

Impacket can also be used:

```bash
impacket-smbclient \
    'corp.example/alice:<PASSWORD>@fileserver.corp.example'
```

This can support manual inspection of authorised shares.

See:

[Impacket](impacket.md)

---

# Backups

Backups may contain highly sensitive Active Directory data.

Potential sources include:

```text
System State Backups
Domain Controller Images
VM Snapshots
NTDS.dit Copies
Registry Hives
Configuration Backups
Application Backups
```

A backup containing domain-controller state should be treated as Tier 0 material.

---

# NTDS.dit

The Active Directory database is stored in:

```text
NTDS.dit
```

on domain controllers.

It contains directory information including password-derived credential data.

Conceptually:

```text
Domain Controller
      |
      v
NTDS.dit
      |
      +
SYSTEM Secrets
      |
      v
Domain Credential Material
```

Access to this data represents severe credential exposure.

A dedicated page should cover:

```text
active-directory/ntds.md
```

---

# NTDS Access Is High Impact

Obtaining credential material from NTDS can potentially expose:

```text
Domain Users
Service Accounts
Privileged Accounts
Computer Accounts
Historical Password Material
```

depending on the technique and data.

This should not be performed merely to prove domain administrative access.

---

# DCSync

DCSync is conceptually different from copying:

```text
NTDS.dit
```

Instead, a principal with the required directory replication permissions can request password-related data through domain replication protocols.

Conceptually:

```text
Controlled Principal
       |
       v
Replication Rights
       |
       v
Domain Controller
       |
       v
Directory Replication
       |
       v
Credential Data
```

---

# DCSync Rights

Important replication rights commonly include:

```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

Additional rights may matter depending on the data and domain configuration.

These permissions should be tightly restricted.

---

# DCSync Attack Path

```text
Alice
 |
 v
Replication Rights
 |
 v
Domain
 |
 v
DCSync Capability
 |
 v
Domain Credential Material
```

This is generally a high-impact or critical attack path.

---

# DCSync Validation

In many assessments, it is unnecessary to retrieve every domain credential.

A safer model is:

```text
Confirm Replication Rights
       |
       v
Confirm Attack Path
       |
       v
If Required:
Request Dedicated Test Account
```

Avoid dumping all domain credentials when a test identity can demonstrate the issue.

---

# secretsdump

Impacket provides:

```text
secretsdump.py
```

commonly exposed as:

```text
impacket-secretsdump
```

It supports several credential extraction scenarios involving Windows systems and Active Directory.

Because its use can retrieve highly sensitive credentials, it should only be used where specifically authorised.

Inspect current options:

```bash
impacket-secretsdump -h
```

before use.

---

# Scope secretsdump Validation

Where DCSync validation is explicitly required, prefer targeting a dedicated account rather than retrieving the complete domain credential set.

The objective is:

```text
Prove Replication Capability
```

not:

```text
Collect Maximum Credentials
```

---

# Kerberos Tickets

Kerberos tickets are credentials.

Important types include:

```text
TGT
TGS
```

A stolen or otherwise controlled valid ticket may permit authentication without knowing the user's plaintext password.

See:

[Kerberos Tickets](kerberos-tickets.md)

and:

[Pass-the-Ticket](pass-the-ticket.md)

---

# Kerberos Keys

Long-term Kerberos keys can also function as reusable authentication material.

Examples include:

```text
RC4 / NT-derived Key
AES128
AES256
```

See:

[Pass-the-Key](pass-the-key.md)

---

# NT Hashes

The NT hash can be security-sensitive because it may be used by authentication protocols or to derive/use Kerberos-compatible key material in appropriate circumstances.

Relevant techniques include:

[Pass-the-Hash](pass-the-hash.md)

and:

[OverPass-the-Hash](overpass-the-hash.md)

---

# NetNTLM Challenge-Response

Do not confuse:

```text
NT Hash
```

with:

```text
NetNTLMv2 Challenge-Response
```

The relationship is:

```text
NT Hash
   |
   v
Used Internally in NTLM Authentication
```

while:

```text
Captured NetNTLMv2
   |
   +--> Offline Guessing
   |
   +--> Potential Relay
```

A captured NetNTLMv2 response is not itself an NT hash.

See:

[NTLM](ntlm.md)

---

# Kerberoasting

Kerberoasting is a credential-access technique involving Kerberos service tickets for accounts with SPNs.

Conceptually:

```text
Domain User
    |
    v
Request Service Ticket
    |
    v
TGS
    |
    v
Offline Password Guessing
    |
    v
Service Account Password
```

See:

[Kerberoasting](kerberoasting.md)

---

# AS-REP Roasting

AS-REP Roasting applies to accounts where Kerberos pre-authentication is disabled.

Conceptually:

```text
Account
 |
 v
Pre-Authentication Disabled
 |
 v
AS-REP
 |
 v
Offline Password Guessing
```

See:

[AS-REP Roasting](asrep-roasting.md)

---

# Password Spraying

Password spraying attempts a small number of candidate passwords across multiple accounts.

Conceptually:

```text
One Password
    |
    +--> User A
    +--> User B
    +--> User C
    +--> User D
```

It differs from credential extraction but may provide the initial identity required to reach other credential sources.

See:

[Password Spraying](password-spraying.md)

---

# Certificates as Credentials

In Active Directory environments using AD CS, certificates can become authentication credentials.

Conceptually:

```text
Certificate
    +
Private Key
    |
    v
Authentication
```

Therefore:

```text
Certificate + Private Key
```

should be protected similarly to passwords, hashes, and Kerberos keys.

---

# Certificate Credential Model

```text
Certificate Template
       |
       v
Certificate Issued
       |
       v
Private Key Controlled
       |
       v
Authentication Capability
```

AD CS misconfiguration can therefore become a credential-access and privilege-escalation path.

---

# Private Keys

A certificate without the associated private key generally does not provide the same authentication capability as possession of both.

Therefore evidence should distinguish:

```text
Certificate Only
```

from:

```text
Certificate + Private Key
```

---

# PFX / PKCS#12

Certificates and private keys may be stored in containers such as:

```text
.pfx
.p12
```

These files may themselves be password protected.

Treat them as highly sensitive.

---

# Credential Access and Delegation

Kerberos delegation can expose authentication capability under specific conditions.

Relevant areas include:

[Unconstrained Delegation](unconstrained-delegation.md)

[Constrained Delegation](constrained-delegation.md)

[Resource-Based Constrained Delegation](rbcd.md)

[S4U](s4u.md)

Delegation should be understood as an authentication relationship rather than simply a credential dump.

---

# Unconstrained Delegation

A compromised unconstrained delegation host may become particularly sensitive when privileged users authenticate to it.

Conceptually:

```text
Privileged User
      |
      v
Delegation Host
      |
      v
Delegated Kerberos Material
      |
      v
Potential Reuse
```

See:

[Unconstrained Delegation](unconstrained-delegation.md)

---

# Credential Reuse

Once a credential is obtained, determine:

```text
Where is it valid?
```

Do not automatically attempt it against every system.

A safe process is:

```text
Credential
   |
   v
Identify Intended Scope
   |
   v
Identify Authorised Targets
   |
   v
Validate Minimum Necessary Access
```

---

# Credential Blast Radius

Credential value depends on:

```text
Identity
 +
Privilege
 +
Reuse
 +
Reachability
 +
Authentication Protocol
 =
Blast Radius
```

Examples:

```text
Local Administrator Password
```

may affect one system if unique.

The same password reused across 100 servers can create a much larger risk.

---

# Local Administrator Password Reuse

A common historical weakness is:

```text
SERVER01\Administrator
        |
        v
Same Password
        |
        +--> SERVER02
        +--> SERVER03
        +--> SERVER04
```

LAPS is designed to reduce this risk by providing unique managed local administrator passwords.

---

# Service Account Password Reuse

Service accounts may be used across:

```text
Services
Scheduled Tasks
Applications
Servers
Databases
```

A compromised service account can therefore have a broad blast radius.

During assessment, determine:

```text
Where is this account used?
```

rather than indiscriminately authenticating everywhere.

---

# Privileged Credential Exposure

Prioritise credentials belonging to:

```text
Domain Admins
Enterprise Admins
Administrators
Backup Operators
Server Administrators
Certificate Administrators
Virtualisation Administrators
Management Platform Accounts
High-Privilege Service Accounts
Tier 0 Operators
```

But avoid retrieving such credentials unless necessary.

---

# Privileged Sessions

A compromised server may become more significant when privileged administrators log on to it.

Conceptually:

```text
Compromised Server
       |
       v
Privileged Admin Logs On
       |
       v
Credential / Ticket Exposure
       |
       v
Privilege Escalation
```

This is one reason administrative tiering is important.

---

# BloodHound HasSession

Session information can help identify where users are currently or recently authenticated.

However:

```text
HasSession
```

should not automatically be interpreted as:

```text
Credential Available
```

It is an indicator that requires further validation.

---

# Credential Hunting Priorities

A useful prioritisation model is:

```text
1. Directory ACL-Based Credential Access
2. Managed Password Exposure
3. SYSVOL / Share Secrets
4. Service Configuration
5. Endpoint Credential Exposure
6. Domain Controller Credential Access
```

Start with lower-impact sources.

---

# Low-Impact Credential Discovery

Prefer:

```text
Directory Enumeration
ACL Analysis
Configuration Review
Metadata
Group Membership
BloodHound
```

before:

```text
Memory Dumping
Registry Hive Extraction
NTDS Extraction
Mass Credential Collection
```

---

# Credential Access Validation Levels

A useful hierarchy is:

```text
Level 1
Identify Potential Credential Source

Level 2
Confirm Read Permission

Level 3
Read Metadata

Level 4
Retrieve Dedicated Test Credential

Level 5
Authenticate with Test Credential

Level 6
Retrieve Production Credential

Level 7
Use Production Credential for Lateral Movement
```

Use the lowest level that proves the issue.

---

# Example - LAPS

Instead of:

```text
Read Every LAPS Password
```

prefer:

```text
Identify Excessive Reader
       |
       v
Confirm ACL
       |
       v
Retrieve One Approved Test Password
       |
       v
Validate Test Computer
```

where active proof is required.

---

# Example - gMSA

Instead of:

```text
Dump Every gMSA Secret
```

prefer:

```text
Identify gMSA
     |
     v
Identify Password Readers
     |
     v
Confirm Controlled Principal Has Read Access
     |
     v
Retrieve Only if Required
```

---

# Example - DCSync

Instead of:

```text
Replicate All Domain Hashes
```

prefer:

```text
Confirm Replication Rights
       |
       v
Request Dedicated Test Account
       |
       v
Replicate Only Test Account
```

where tooling and scope permit.

---

# Example - LSASS

Instead of:

```text
Dump LSASS from Production Server
```

prefer:

```text
Confirm Local Administrator
       |
       v
Confirm Privileged Session
       |
       v
Document Potential Exposure
```

unless credential extraction is explicitly required.

---

# Credential Evidence Handling

Credentials should not be placed unnecessarily in:

```text
Screenshots
Tickets
Chat Messages
Email
Git Repositories
Plaintext Notes
Final Reports
```

Use redaction.

Example:

```text
Password:
Sup3rSecretPassword!
```

should become:

```text
Password:
[REDACTED]
```

---

# Hash Redaction

Instead of storing:

```text
Administrator:500:<FULL_HASH>
```

use:

```text
Administrator:500:[REDACTED]
```

or, where correlation is necessary:

```text
NT Hash:
8846f7... [truncated]
```

Do not retain more credential material than required.

---

# Ticket Handling

Files such as:

```text
.ccache
.kirbi
```

may contain reusable authentication material.

Treat them as credentials.

Cleanup should include:

```text
Delete Test Tickets
Unset KRB5CCNAME
Purge Test Sessions
Remove Temporary Files
```

---

# Certificate Handling

Files such as:

```text
.pfx
.p12
.pem
.key
```

may contain private keys.

Treat them as credentials.

Do not commit them to:

```text
Git
Documentation
Shared Repositories
```

---

# Memory Dumps

Memory dumps may contain far more information than the credential being tested.

They can expose:

```text
Other Users
Tokens
Keys
Application Data
Personal Data
Secrets
```

This makes them particularly sensitive evidence.

---

# Credential Storage During Assessment

Use:

```text
Encrypted Storage
Restricted Permissions
Minimum Retention
Controlled Evidence Directory
```

Avoid:

```text
World-Readable Files
Shared Folders
Public Git Repositories
Cloud Sync Without Approval
```

---

# Credential Cleanup

At the end of testing:

```text
Credential Artefacts
      |
      +--> Password Notes
      +--> Hash Files
      +--> Kerberos Tickets
      +--> PFX Files
      +--> Private Keys
      +--> Memory Dumps
      +--> Registry Hives
      +--> NTDS Copies
      +--> Temporary Scripts
```

should be handled according to the agreed evidence-retention policy.

---

# Detection

Credential Access detection should combine:

```text
Identity Telemetry
     +
Endpoint Telemetry
     +
Directory Auditing
     +
Kerberos Events
     +
NTLM Events
     +
File Access
     +
Process Activity
```

No single event detects all credential-access techniques.

---

# Credential Access Detection Model

```text
Credential Source
      |
      v
Access Attempt
      |
      v
Collection
      |
      v
Authentication
      |
      v
Lateral Movement
```

Detection opportunities exist at each stage.

---

# Detect Directory Credential Access

Monitor unusual access to:

```text
LAPS Attributes
gMSA Password Attributes
Replication Rights
Key Credential Link
Certificate Configuration
```

especially from principals that do not normally perform administrative operations.

---

# Event 4662

Security event:

```text
4662
```

can record operations performed on Active Directory objects when the appropriate auditing and SACL configuration is enabled.

This can be useful for detecting certain directory credential-access techniques, including replication-related activity.

---

# Event 5136

Event:

```text
5136
```

can record directory object modifications.

Relevant examples include changes to:

```text
msDS-KeyCredentialLink
msDS-AllowedToActOnBehalfOfOtherIdentity
Delegation Configuration
Sensitive ACL-Related Attributes
```

depending on auditing configuration.

---

# Kerberos Events

Important Kerberos events include:

```text
4768
4769
4770
4771
```

These can help identify:

```text
TGT Requests
Service Ticket Requests
Ticket Renewals
Pre-Authentication Failures
```

depending on the event.

---

# NTLM Events

Useful authentication events include:

```text
4624
4625
4648
4776
```

depending on the authentication path and audit configuration.

See:

[NTLM](ntlm.md)

---

# Event 4688

Where process creation auditing is enabled:

```text
4688
```

can help identify processes associated with credential-access activity.

Command-line logging can significantly improve context.

---

# Endpoint Detection

EDR telemetry can help identify:

```text
Unexpected LSASS Access
Memory Dump Creation
Registry Hive Access
Credential Tool Execution
Suspicious PowerShell
Unusual Certificate Export
DPAPI Access
```

Detection should focus on behaviour rather than only tool names.

---

# Do Not Detect Only Mimikatz

A weak detection model is:

```text
Process Name = mimikatz.exe
```

Attackers can:

```text
Rename Tools
Use Different Tools
Use Native APIs
Use Remote Techniques
Use Custom Implementations
```

Prefer behavioural detections.

---

# LSASS Detection Model

```text
Process
 |
 v
Opens LSASS
 |
 v
Requests Sensitive Access
 |
 v
Reads Memory
 |
 v
Credential Material
```

Investigate unusual processes obtaining sensitive handles to LSASS.

---

# DCSync Detection Model

```text
Non-DC Principal / Host
       |
       v
Directory Replication Request
       |
       v
Replication Rights Used
       |
       v
Credential Data
```

Replication activity originating from unexpected systems or identities deserves investigation.

---

# LAPS Detection Model

```text
User
 |
 v
Reads LAPS Password
 |
 v
Is User an Expected Reader?
 |
 +--> Yes -> Baseline
 |
 +--> No -> Investigate
```

---

# gMSA Detection Model

```text
Principal
 |
 v
Retrieves gMSA Managed Password
 |
 v
Expected Host / Service?
 |
 +--> Yes -> Baseline
 |
 +--> No -> Investigate
```

---

# Credential Reuse Detection

The second half of credential-access detection is:

```text
Was the credential subsequently used?
```

Correlate:

```text
Credential Access
      |
      v
Authentication Event
      |
      v
New Source Host
      |
      v
Privileged Access
```

---

# Hardening

Credential Access prevention requires multiple layers.

A useful model is:

```text
Reduce Stored Credentials
        |
        v
Protect Credential Stores
        |
        v
Restrict Credential Readers
        |
        v
Protect Privileged Sessions
        |
        v
Use Strong Authentication
        |
        v
Segment Administration
        |
        v
Monitor Credential Access
```

---

# Use LAPS

Use Windows LAPS or another approved solution to provide unique, managed local administrator passwords.

This reduces:

```text
Local Administrator Password Reuse
```

and therefore reduces lateral-movement blast radius.

---

# Use gMSA

Where compatible, use:

```text
gMSA
```

instead of long-lived manually managed service-account passwords.

Benefits include:

```text
Automatic Password Management
Long Random Passwords
Reduced Human Knowledge of Password
Controlled Retrieval
```

---

# Protect gMSA Readers

A gMSA is only as secure as the principals authorised to retrieve its password.

Review:

```text
PrincipalsAllowedToRetrieveManagedPassword
```

and related directory permissions.

---

# Protect LAPS Readers

Restrict LAPS password access to the minimum required administrative identities.

Avoid unnecessarily broad groups.

---

# Protect LSASS

Consider controls such as:

```text
Credential Guard
LSA Protection
EDR
Attack Surface Reduction
Administrative Tiering
```

where compatible with the environment.

---

# Reduce Privileged Logons

Avoid logging privileged identities onto lower-trust systems.

The model should be:

```text
Tier 0 Account
      |
      X
Workstation
```

and:

```text
Tier 0 Account
      |
      v
Tier 0 Administrative System
```

where practical.

---

# Privileged Access Workstations

Privileged Access Workstations can reduce exposure of administrative credentials to compromised endpoints.

Conceptually:

```text
Privileged Identity
       |
       v
Dedicated Administrative Device
       |
       v
Privileged Resource
```

---

# Protect Service Accounts

Service accounts should have:

```text
Minimum Privilege
No Interactive Logon Where Unnecessary
Long Random Passwords
Managed Rotation
Limited Host Scope
Limited Network Access
Monitoring
```

Prefer gMSA where compatible.

---

# Remove Credentials from Scripts

Do not store credentials in:

```text
PowerShell
Batch Files
VBScript
XML
YAML
JSON
INI
```

where domain users can read them.

Use appropriate secret-management mechanisms.

---

# Protect Deployment Shares

Deployment infrastructure frequently contains highly privileged secrets.

Restrict:

```text
Read Access
Write Access
Administrative Access
```

and monitor access to sensitive files.

---

# Protect Backups

Treat:

```text
Domain Controller Backup
```

as equivalent in sensitivity to:

```text
Domain Controller
```

because it may contain Active Directory credential material.

---

# Protect Replication Rights

Review principals with:

```text
DS-Replication-Get-Changes
DS-Replication-Get-Changes-All
```

and related replication permissions.

Only legitimate replication and tightly controlled administrative identities should possess them.

---

# Protect Certificate Infrastructure

Treat:

```text
CA Private Keys
Enrollment Agent Certificates
Authentication Certificates
Certificate Templates
```

as security-sensitive identity infrastructure.

---

# Use Strong Passwords

Offline credential attacks such as:

```text
Kerberoasting
AS-REP Roasting
Cached Credential Cracking
```

become substantially harder when accounts use long, randomly generated passwords.

Service accounts are particularly important.

---

# Reduce NTLM

Where operationally feasible, reduce unnecessary NTLM usage.

This can reduce exposure to:

```text
Pass-the-Hash
NTLM Relay
Captured Challenge-Response
```

Migration should be carefully planned and monitored.

---

# Prefer Kerberos AES

Modern Kerberos environments should prefer stronger AES encryption types where compatible.

Legacy RC4 dependencies should be identified and remediated carefully.

---

# Credential Access Incident Response

A credential-access incident should answer:

```text
What credential was exposed?
       |
       v
Which identity?
       |
       v
How was it obtained?
       |
       v
Where was it stored?
       |
       v
Where can it authenticate?
       |
       v
Was it used?
       |
       v
What did it access?
       |
       v
How do we invalidate it?
```

---

# Credential Invalidation

Different credentials require different response actions.

Example:

```text
Password
   |
   v
Password Reset
```

```text
NT Hash
   |
   v
Password Reset
```

```text
Kerberos Key
   |
   v
Password / Key Rotation
```

```text
TGT / TGS
   |
   v
Ticket Expiration + Credential Rotation Where Required
```

```text
Certificate
   |
   v
Revoke Certificate + Protect / Rotate Key
```

```text
Computer Account
   |
   v
Reset Machine Password
```

The exact response depends on the credential type and compromise scenario.

---

# Domain Credential Compromise

If highly privileged domain credentials are compromised, response may require significantly more than:

```text
Reset One Password
```

Investigate:

```text
Persistence
Replication Rights
Certificates
Delegation
Scheduled Tasks
Services
New Accounts
ACL Changes
Kerberos Tickets
Domain Controller Access
```

---

# krbtgt

The:

```text
krbtgt
```

account is fundamental to Kerberos ticket signing in an Active Directory domain.

Compromise of its key material is a severe incident.

Recovery procedures may involve controlled rotation of the `krbtgt` password according to Microsoft's guidance.

Do not casually rotate `krbtgt` during testing or incident response.

---

# Credential Rotation Order

Where multiple credentials are compromised, rotation order matters.

Conceptually:

```text
Contain Attacker
      |
      v
Remove Persistence
      |
      v
Secure Administrative Plane
      |
      v
Rotate Credentials
      |
      v
Monitor Reauthentication
```

Rotating credentials before removing attacker persistence may allow credentials to be stolen again.

---

# Reporting

Credential-access findings should identify:

```text
Credential Source
Credential Type
Affected Identity
Required Access
Exposure Mechanism
Resulting Authentication Capability
Privilege
Scope
Evidence
Remediation
```

Avoid unnecessarily including the credential itself.

---

# Finding Titles

Examples include:

```text
Excessive Permissions Allow Reading LAPS Passwords
```

```text
Domain User Can Retrieve gMSA Credential Material
```

```text
Credentials Exposed in SYSVOL Script
```

```text
Service Account Password Stored in Readable Configuration File
```

```text
Excessive Replication Rights Enable DCSync
```

```text
Privileged Credentials Exposed on Lower-Trust Server
```

```text
Domain Controller Backup Exposes Active Directory Credential Material
```

---

# Example Credential Exposure Finding

```text
Finding:
Service Account Credential Stored in Domain-Readable SYSVOL Script

Affected File:
\\corp.example\SYSVOL\corp.example\scripts\deployment.ps1

Affected Account:
CORP\svc_deploy

Description:
A PowerShell deployment script stored in SYSVOL contains reusable
authentication material for the CORP\svc_deploy service account.

The script is readable by ordinary authenticated domain users through
the normal SYSVOL share.

The credential was identified during read-only review of domain policy
and deployment files.

The credential value has been omitted from this report.

Impact:
A compromised domain user able to read the script could obtain the
service-account credential and authenticate as CORP\svc_deploy.

The resulting impact depends on the account's privileges and the
systems on which the credential is accepted.

Recommendation:
Immediately rotate the exposed credential.

Remove the credential from SYSVOL and replace plaintext credential
storage with an approved secret-management mechanism.

Review the privileges and authentication history of CORP\svc_deploy,
search for other copies of the credential, and review SYSVOL for
additional exposed secrets.
```

---

# Example LAPS Finding

```text
Finding:
Excessive Directory Permissions Allow Reading LAPS Passwords

Source Principal:
CORP\helpdesk-user

Affected Scope:
OU=Servers,DC=corp,DC=example

Description:
The CORP\helpdesk-user account has directory permissions that permit
access to managed local administrator password information for systems
within the Servers OU.

The permission was confirmed through Active Directory ACL analysis.

Where active validation was required, access was tested only against
an approved test computer.

Production LAPS passwords were not collected.

Impact:
Successful abuse could provide local administrative access to affected
systems.

The resulting impact depends on the systems within scope and whether
additional credential or privilege-escalation opportunities exist on
those hosts.

Recommendation:
Restrict LAPS password retrieval to dedicated administrative identities
that require access.

Review delegated permissions throughout the directory and monitor
access to LAPS password attributes.
```

---

# Example DCSync Finding

```text
Finding:
Excessive Active Directory Replication Rights Enable Credential Replication

Source Principal:
CORP\svc_backup

Affected Scope:
DC=corp,DC=example

Description:
The CORP\svc_backup account possesses Active Directory replication
permissions that can allow it to request sensitive directory
credential data using domain replication protocols.

The relevant directory permissions were independently confirmed.

The complete domain credential database was not retrieved during
validation.

Impact:
Successful abuse could expose password-derived credential material for
domain identities, potentially including privileged accounts.

This could result in domain-wide compromise.

Recommendation:
Remove unnecessary directory replication permissions from the affected
account.

Restrict replication rights to Domain Controllers and explicitly
approved identity-management services.

Investigate the authentication and directory activity of the affected
account and monitor replication operations originating from unexpected
systems or identities.
```

---

# Severity Assessment

Credential findings should not be rated solely according to:

```text
Credential Exists
```

Consider:

```text
Credential Type
     +
Credential Privilege
     +
Ease of Retrieval
     +
Number of Readers
     +
Authentication Scope
     +
Credential Reuse
     +
Network Reachability
     =
Actual Risk
```

---

# Example Severity Model

```text
Readable Password
      |
      v
Low-Privilege Test Account
      |
      v
Single Non-Sensitive System
```

may have relatively limited impact.

Compare:

```text
Readable Credential
      |
      v
Tier 0 Service Account
      |
      v
Domain-Wide Administrative Access
```

which can be critical.

---

# Credential Access Checklist

## Preparation

- [ ] Confirm credential-access testing is authorised
- [ ] Confirm whether credential extraction is permitted
- [ ] Confirm whether memory dumping is permitted
- [ ] Confirm whether NTDS access is permitted
- [ ] Confirm whether DCSync validation is permitted
- [ ] Confirm whether production credentials may be retrieved
- [ ] Define credential evidence handling
- [ ] Define credential retention period
- [ ] Prepare encrypted evidence storage

## Identity Enumeration

- [ ] Identify controlled user
- [ ] Record SID
- [ ] Enumerate groups
- [ ] Enumerate privileges
- [ ] Enumerate directory ACLs
- [ ] Enumerate local administrative access
- [ ] Identify accessible systems
- [ ] Identify accessible shares

## Directory Credentials

- [ ] Review LAPS readers
- [ ] Review Windows LAPS configuration
- [ ] Review legacy LAPS configuration
- [ ] Review gMSA readers
- [ ] Review replication rights
- [ ] Review `msDS-KeyCredentialLink`
- [ ] Review certificate-related permissions
- [ ] Review computer-account control

## SYSVOL

- [ ] Enumerate SYSVOL
- [ ] Search for `cpassword`
- [ ] Review scripts
- [ ] Review XML files
- [ ] Review configuration files
- [ ] Search for credential keywords
- [ ] Review referenced external resources
- [ ] Review file permissions

## Shares

- [ ] Enumerate readable shares
- [ ] Review deployment shares
- [ ] Review backup shares
- [ ] Review script repositories
- [ ] Review configuration shares
- [ ] Review administrative shares where authorised
- [ ] Search targeted locations for secrets

## Endpoints

- [ ] Identify local administrative access
- [ ] Review logged-on users
- [ ] Review services
- [ ] Review scheduled tasks
- [ ] Review application configuration
- [ ] Review PowerShell history
- [ ] Review Credential Manager metadata
- [ ] Review DPAPI-relevant artefacts where authorised
- [ ] Determine Credential Guard status
- [ ] Determine LSA protection status
- [ ] Avoid LSASS dumping unless required

## Kerberos

- [ ] Review available tickets
- [ ] Review service accounts
- [ ] Review Kerberoasting exposure
- [ ] Review AS-REP roasting exposure
- [ ] Review delegation
- [ ] Protect collected `.ccache`
- [ ] Protect collected `.kirbi`

## Domain Controllers

- [ ] Review replication rights
- [ ] Review DCSync paths
- [ ] Review DC administrative access
- [ ] Review backup access
- [ ] Review NTDS exposure
- [ ] Avoid mass credential extraction
- [ ] Use dedicated test account where possible

## Certificates

- [ ] Enumerate authentication certificates
- [ ] Review private-key access
- [ ] Review certificate templates
- [ ] Review certificate enrollment rights
- [ ] Review key credential links
- [ ] Protect PFX/P12 files
- [ ] Protect private keys

## Validation

- [ ] Use lowest-impact validation
- [ ] Prefer ACL proof
- [ ] Prefer metadata proof
- [ ] Prefer dedicated test credentials
- [ ] Retrieve minimum necessary credential material
- [ ] Validate only authorised targets
- [ ] Avoid broad credential reuse testing
- [ ] Record resulting privilege

## Detection

- [ ] Monitor directory credential access
- [ ] Monitor 4662
- [ ] Monitor 5136
- [ ] Monitor Kerberos events
- [ ] Monitor NTLM events
- [ ] Monitor process creation
- [ ] Monitor LSASS access
- [ ] Monitor registry hive access
- [ ] Monitor DCSync
- [ ] Monitor LAPS reads
- [ ] Monitor gMSA retrieval
- [ ] Monitor certificate export
- [ ] Correlate credential access with authentication

## Hardening

- [ ] Deploy Windows LAPS
- [ ] Restrict LAPS readers
- [ ] Use gMSA where appropriate
- [ ] Restrict gMSA readers
- [ ] Protect LSASS
- [ ] Enable Credential Guard where appropriate
- [ ] Enable LSA protection where appropriate
- [ ] Reduce privileged logons
- [ ] Use administrative tiering
- [ ] Use PAWs
- [ ] Remove secrets from SYSVOL
- [ ] Protect deployment shares
- [ ] Protect backups
- [ ] Restrict replication rights
- [ ] Protect certificate infrastructure
- [ ] Reduce NTLM where feasible
- [ ] Prefer strong Kerberos encryption
- [ ] Use long random service-account passwords

## Cleanup

- [ ] Delete temporary password files
- [ ] Delete hash files
- [ ] Delete memory dumps
- [ ] Delete registry hive copies
- [ ] Delete NTDS copies
- [ ] Delete temporary certificates
- [ ] Delete temporary private keys
- [ ] Delete Kerberos caches
- [ ] Unset `KRB5CCNAME`
- [ ] Remove test accounts where required
- [ ] Remove test certificates
- [ ] Verify test directory changes were reverted
- [ ] Secure retained evidence

---

# Credential Access Testing Model

The basic model is:

```text
Controlled Identity
       |
       v
Credential Source
       |
       v
Credential Material
       |
       v
Additional Identity
       |
       v
Additional Privilege
```

The directory model is:

```text
User
 |
 v
Directory Permission
 |
 v
Sensitive Attribute
 |
 +--> LAPS
 +--> gMSA
 +--> Replication
 +--> Key Credential
```

The endpoint model is:

```text
User
 |
 v
Local Administrator
 |
 v
Protected Credential Source
 |
 +--> LSASS
 +--> SAM
 +--> LSA Secrets
 +--> DPAPI
```

The SYSVOL model is:

```text
Domain User
    |
    v
SYSVOL
    |
    v
Readable Script / XML
    |
    v
Stored Credential
```

The DCSync model is:

```text
Controlled Principal
       |
       v
Replication Rights
       |
       v
Domain Controller
       |
       v
Directory Replication
       |
       v
Credential Material
```

The Kerberos model is:

```text
Kerberos Credential
       |
       +--> Password-Derived Key
       |
       +--> TGT
       |
       +--> Service Ticket
       |
       v
Kerberos Authentication
```

The certificate model is:

```text
Certificate
    +
Private Key
    |
    v
Authentication
```

The credential-reuse model is:

```text
Credential
    |
    v
Where Is It Valid?
    |
    +--> One Host
    |
    +--> Multiple Hosts
    |
    +--> Domain
    |
    +--> Tier 0
```

The validation model is:

```text
Potential Exposure
       |
       v
Confirm Permission
       |
       v
Confirm Source
       |
       v
Retrieve Minimum Evidence
       |
       v
Validate Minimum Access
```

The detection model is:

```text
Credential Source
      |
      v
Suspicious Access
      |
      v
Credential Retrieval
      |
      v
Authentication
      |
      v
Privilege / Lateral Movement
```

The defensive model is:

```text
Reduce Credential Storage
        |
        v
Restrict Credential Readers
        |
        v
Protect Credential Stores
        |
        v
Protect Privileged Sessions
        |
        v
Rotate Credentials
        |
        v
Monitor Access and Reuse
```

A mature credential-access assessment should answer:

```text
What credential sources exist?
       |
       v
Who can access them?
       |
       v
What credential type is exposed?
       |
       v
Which identity does it represent?
       |
       v
Where is it valid?
       |
       v
What privilege does it provide?
       |
       v
Can the exposure be proven safely?
```

The most important principle is:

```text
Can Access Credential Source
        |
        X
Must Dump Everything
```

Instead:

```text
Identify Exposure
      |
      v
Confirm Permission
      |
      v
Retrieve Minimum Necessary Evidence
      |
      v
Determine Resulting Impact
```

Credential-access testing should therefore optimise for:

```text
Minimum Collection
        +
Maximum Evidence Quality
        +
Clear Attack-Path Analysis
```

rather than:

```text
Maximum Number of Credentials Collected
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Active Directory ACLs:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Group Policy:

[Active Directory Group Policy](group-policy.md)

Machine Account Quota:

[Active Directory Machine Account Quota](machine-account-quota.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Password Spraying:

[Password Spraying](password-spraying.md)

AS-REP Roasting:

[AS-REP Roasting](asrep-roasting.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

OverPass-the-Hash:

[OverPass-the-Hash](overpass-the-hash.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Unconstrained Delegation:

[Unconstrained Delegation](unconstrained-delegation.md)

Constrained Delegation:

[Constrained Delegation](constrained-delegation.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[S4U](s4u.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The dedicated Credential Access pages following this overview are:

```text
active-directory/gpp-passwords.md
active-directory/laps.md
active-directory/gmsa.md
active-directory/shadow-credentials.md
active-directory/ntds.md
```

---

# References

## Microsoft - Credential Protection

[Microsoft - Windows Credential Theft Mitigation Guide](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/credentials-protection-and-management){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Configure Added LSA Protection](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows LAPS Concepts](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-concepts-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows LAPS PowerShell](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-management-powershell){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - gMSA

[Microsoft - Group Managed Service Accounts Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - msDS-ManagedPassword](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/9cd2fc5e-7305-4fb8-b233-2a60bc3eec68){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory

[Microsoft - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Audit Directory Service Access](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-directory-service-access){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4662](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4662){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 5136](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5136){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Kerberos

[Microsoft - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos Authentication Troubleshooting Guidance](https://learn.microsoft.com/en-us/troubleshoot/windows-server/windows-security/kerberos-authentication-troubleshooting-guidance){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DPAPI

[Microsoft - CryptProtectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata){ target="_blank" rel="noopener noreferrer" }

[Microsoft - CryptUnprotectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptunprotectdata){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket secretsdump.py](https://github.com/fortra/impacket/blob/master/examples/secretsdump.py){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Credential Access](https://attack.mitre.org/tactics/TA0006/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - OS Credential Dumping](https://attack.mitre.org/techniques/T1003/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - DCSync](https://attack.mitre.org/techniques/T1003/006/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Credentials from Password Stores](https://attack.mitre.org/techniques/T1555/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Credential Access should be treated as an identity-expansion problem.

The fundamental model is:

```text
Controlled Identity
       |
       v
Credential Source
       |
       v
Additional Credential
       |
       v
Additional Identity
       |
       v
Additional Access
```

The most important question is not:

```text
How many credentials can I dump?
```

It is:

```text
Which credential can this identity access,
and what additional privilege does that provide?
```

A mature assessment therefore follows:

```text
Enumerate
   |
   v
Identify Exposure
   |
   v
Confirm Permission
   |
   v
Understand Credential Type
   |
   v
Map Authentication Scope
   |
   v
Determine Resulting Privilege
   |
   v
Validate Minimally
```

Different credential types should remain clearly separated:

```text
Password
   !=
NT Hash
   !=
NetNTLMv2 Response
   !=
Kerberos Key
   !=
Kerberos Ticket
   !=
Certificate
   !=
Private Key
```

Even though several of them may ultimately provide authentication capability.

The Active Directory credential-access landscape can be visualised as:

```text
                   Active Directory
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
     Directory          SYSVOL          Endpoints
        |                 |                 |
        v                 v                 v
      LAPS              GPP              LSASS
      gMSA              Scripts           SAM
    DCSync              Config            DPAPI
 Key Credentials                         Secrets
        |
        +-----------------+-----------------+
                          |
                          v
                  Credential Material
                          |
                          v
                     Authentication
                          |
                          v
                  Effective Privilege
```

For penetration testing:

```text
Credential Source
       |
       v
Can I Access It?
       |
       +--> No
       |     |
       |     v
       |   Document Boundary
       |
       +--> Yes
             |
             v
      Can I Prove It Safely?
             |
             +--> Yes
             |     |
             |     v
             |   Minimum Evidence
             |
             +--> No
                   |
                   v
             Stop and Document
```

For defenders:

```text
Where Are Credentials Stored?
        |
        v
Who Can Read Them?
        |
        v
Who Can Modify Authentication?
        |
        v
Where Are Privileged Users Logging On?
        |
        v
Can Credential Access Be Detected?
        |
        v
Can Compromised Credentials Be Rotated Quickly?
```

The strongest defensive strategy combines:

```text
Least Privilege
      +
Managed Credentials
      +
Administrative Tiering
      +
Credential Guard
      +
LSA Protection
      +
Strong Kerberos Configuration
      +
Reduced NTLM
      +
Protected Backups
      +
Directory Auditing
      +
Endpoint Detection
```

Credential Access should ultimately be analysed as part of the complete Active Directory attack graph:

```text
Identity
   |
   v
Credential
   |
   v
Identity
   |
   v
Privilege
   |
   v
Credential
   |
   v
Higher Privilege
```

Breaking any link in that chain can prevent a small credential exposure from becoming domain compromise.
