# Kerberoasting

Kerberoasting is an Active Directory credential attack that targets accounts associated with **Service Principal Names (SPNs)**.

An authenticated domain user can normally request Kerberos service tickets for services they are permitted to access. Parts of those service tickets are encrypted using key material associated with the account running the service.

If that account uses a weak password, the captured service ticket can be subjected to offline password guessing.

```text
Domain User
    |
    | Request service ticket
    v
KDC
    |
    | TGS-REP
    v
Service Ticket
    |
    v
Password-derived encrypted material
    |
    v
Offline password cracking
    |
    v
Service account credential
```

Kerberoasting does not exploit a vulnerability in Kerberos itself.

The practical risk usually results from a combination of:

```text
SPN-enabled account
        +
Password-derived Kerberos key
        +
Weak or predictable password
        +
Excessive account privileges
```

!!! warning "Authorised testing only"
    Kerberoasting obtains password-derived authentication material that can be subjected to offline password cracking. Only perform this testing against accounts and domains explicitly included in the assessment scope. Protect collected tickets and recovered credentials, use controlled cracking strategies, and validate only the minimum impact necessary.

---

# Kerberoasting at a Glance

A typical assessment workflow is:

```text
Identify Active Directory domain
          |
          v
Obtain authorised domain access
          |
          v
Enumerate SPNs
          |
          v
Identify user-based service accounts
          |
          v
Review account characteristics
          |
          v
Request service tickets
          |
          v
Export cracking material
          |
          v
Identify encryption type
          |
          v
Offline password assessment
          |
     +----+----+
     |         |
     v         v
 Not cracked  Cracked
     |         |
     v         v
Record        Validate minimum
exposure      required impact
     |         |
     +----+----+
          |
          v
Detection and remediation
```

---

# Kerberos Refresher

Kerberoasting occurs during the service-ticket stage of Kerberos authentication.

A simplified Kerberos workflow is:

```text
User
 |
 | AS-REQ
 v
KDC
 |
 | AS-REP
 v
TGT
 |
 | TGS-REQ
 | Request service ticket
 v
KDC
 |
 | TGS-REP
 v
Service Ticket
 |
 v
Target Service
```

The important distinction is:

```text
TGT
 |
 +--> Represents authentication to the domain
 |
 v
Used to request service tickets


Service Ticket
 |
 +--> Intended for a specific service
 |
 v
Protected using service-account key material
```

For detailed Kerberos architecture, see:

[Kerberos](kerberos.md)

---

# What Is an SPN?

A **Service Principal Name** identifies a service instance for Kerberos authentication.

Conceptually:

```text
Service
   |
   v
SPN
   |
   v
Active Directory account
```

Common SPN forms include:

```text
service/hostname
service/hostname:port
```

Examples include:

```text
MSSQLSvc/sql01.corp.example:1433
HTTP/web01.corp.example
CIFS/fileserver.corp.example
LDAP/dc01.corp.example
```

The SPN allows Kerberos to determine which account represents the requested service.

---

# SPN Components

A simplified SPN can be viewed as:

```text
MSSQLSvc/sql01.corp.example:1433
    |            |            |
    |            |            +--> Port
    |            |
    |            +--> Host
    |
    +--> Service class
```

Not every SPN includes a port.

---

# SPNs and Accounts

SPNs can be associated with:

```text
Computer accounts
```

or:

```text
User accounts
```

For Kerberoasting assessments, user-based service accounts are usually particularly interesting because they may use administrator-selected passwords.

Conceptually:

```text
SPN
 |
 +--> Computer Account
 |       |
 |       +--> Machine-managed password
 |
 +--> User Service Account
         |
         +--> Potentially human-managed password
```

This distinction is important when prioritising targets.

---

# Why Service Accounts Are Attractive Targets

Traditional service accounts can have characteristics such as:

- long-lived passwords
- passwords that rarely change
- `PasswordNeverExpires`
- human-generated passwords
- predictable naming conventions
- access to servers
- database permissions
- application privileges
- local administrator rights
- delegated Active Directory rights
- membership in privileged groups

A service account might therefore look like:

```text
svc_sql
   |
   +--> SPN
   +--> Password never expires
   +--> Password unchanged for years
   +--> SQL administrative access
   +--> Local administrator on SQL servers
```

If the password is weak enough to recover, the resulting impact may extend beyond the individual service.

---

# Kerberoasting Requirements

The typical requirements are:

```text
Valid domain account
       |
       +
Reachable domain controller
       |
       +
Kerberos access
       |
       +
Target SPN
```

Unlike AS-REP Roasting, Kerberoasting generally starts from authenticated domain access.

The requesting user does not normally need administrative privileges.

---

# Why Any Domain User Can Be Relevant

Kerberos is designed so authenticated users can request tickets for services they need to access.

Conceptually:

```text
Authenticated User
        |
        v
Request ticket for MSSQLSvc/sql01
        |
        v
KDC
        |
        v
Service Ticket
```

The KDC cannot require the requesting user to know the service account's password because that would defeat the Kerberos service-ticket model.

The defensive objective is therefore not to prevent legitimate ticket issuance.

Instead, organisations should ensure service accounts use credential material that resists offline recovery and have only the privileges they require.

---

# Kerberoasting vs AS-REP Roasting

These techniques target different parts of Kerberos.

```text
AS-REP Roasting
      |
      v
AS-REQ
      |
      v
AS-REP
      |
      v
Pre-authentication disabled


Kerberoasting
      |
      v
TGS-REQ
      |
      v
TGS-REP
      |
      v
Account has SPN
```

Comparison:

| Property | AS-REP Roasting | Kerberoasting |
|---|---|---|
| Target | User without pre-authentication | Account with SPN |
| Common account type | User | Service account |
| Authentication required | Not necessarily | Generally yes |
| Ticket stage | AS-REP | TGS-REP |
| Offline cracking | Yes | Yes |
| Password strength important | Yes | Yes |

For detailed AS-REP coverage, see:

[AS-REP Roasting](asrep-roasting.md)

---

# Kerberoasting vs Password Spraying

Password spraying performs online password guesses:

```text
Password
   |
   v
Many accounts
   |
   v
Authentication service
```

Kerberoasting instead obtains service-ticket material:

```text
SPN
 |
 v
TGS request
 |
 v
Service ticket
 |
 v
Offline password guessing
```

The offline stage avoids repeated password authentication attempts against the target account.

For password-spraying methodology, see:

[Password Spraying](password-spraying.md)

---

# Enumerating SPNs from Windows

Windows provides several ways to identify SPNs.

---

# setspn

The native `setspn.exe` utility can query SPNs.

Query SPNs associated with a specific account:

```cmd
setspn -L <ACCOUNT>
```

Example:

```cmd
setspn -L svc_sql
```

Query registered SPNs within the domain:

```cmd
setspn -Q */*
```

This can generate substantial output in large environments.

---

# Query a Specific Service Class

For example:

```cmd
setspn -Q MSSQLSvc/*
```

HTTP:

```cmd
setspn -Q HTTP/*
```

CIFS:

```cmd
setspn -Q CIFS/*
```

This can help focus enumeration on particular service types.

---

# PowerShell - Active Directory Module

Enumerate users with SPNs:

```powershell
Get-ADUser `
    -LDAPFilter '(servicePrincipalName=*)' `
    -Properties ServicePrincipalName
```

Display usernames and SPNs:

```powershell
Get-ADUser `
    -LDAPFilter '(servicePrincipalName=*)' `
    -Properties ServicePrincipalName |
    Select-Object SamAccountName,ServicePrincipalName
```

---

# Useful Service Account Properties

Expand enumeration:

```powershell
Get-ADUser `
    -LDAPFilter '(servicePrincipalName=*)' `
    -Properties `
        ServicePrincipalName,
        Enabled,
        PasswordLastSet,
        PasswordNeverExpires,
        MemberOf |
    Select-Object `
        SamAccountName,
        Enabled,
        PasswordLastSet,
        PasswordNeverExpires,
        ServicePrincipalName
```

This helps prioritise accounts based on actual risk.

---

# Enabled SPN Accounts

Filter disabled accounts:

```powershell
Get-ADUser `
    -LDAPFilter '(servicePrincipalName=*)' `
    -Properties ServicePrincipalName,Enabled |
    Where-Object Enabled -eq $true |
    Select-Object SamAccountName,ServicePrincipalName
```

---

# Password-Never-Expires SPN Accounts

Identify accounts where passwords never expire:

```powershell
Get-ADUser `
    -LDAPFilter '(servicePrincipalName=*)' `
    -Properties `
        ServicePrincipalName,
        PasswordNeverExpires,
        PasswordLastSet |
    Where-Object PasswordNeverExpires -eq $true |
    Select-Object `
        SamAccountName,
        PasswordLastSet,
        ServicePrincipalName
```

This configuration is not automatically exploitable.

It can, however, increase the practical risk of weak service-account passwords remaining valid for long periods.

---

# LDAP Enumeration

SPN-bearing users can be identified using:

```text
(servicePrincipalName=*)
```

A more focused LDAP filter for user objects is:

```text
(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))
```

---

# ldapsearch

Where LDAP access is available:

```bash
ldapsearch \
    -x \
    -H ldap://10.10.10.10 \
    -D 'CORP\testuser' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=person)(objectClass=user)(servicePrincipalName=*))' \
    sAMAccountName servicePrincipalName pwdLastSet userAccountControl
```

The exact bind format depends on the environment.

---

# PowerView

PowerView can enumerate SPN-enabled user accounts where its use is authorised.

A commonly used command is:

```powershell
Get-DomainUser -SPN
```

Useful properties may include:

```powershell
Get-DomainUser -SPN |
    Select-Object `
        samaccountname,
        serviceprincipalname,
        pwdlastset,
        useraccountcontrol
```

Exact functionality depends on the PowerView version.

---

# BloodHound

BloodHound can help identify service accounts and determine their significance.

A useful workflow is:

```text
SPN-enabled account
       |
       v
BloodHound
       |
       +--> Group membership
       +--> Local administrator rights
       +--> Remote management rights
       +--> ACL relationships
       +--> Sessions
       +--> Paths to privileged assets
```

This is valuable because not every roastable account has the same risk.

For detailed BloodHound coverage, see:

[BloodHound](bloodhound.md)

---

# Impacket GetUserSPNs

Impacket's `GetUserSPNs.py` is commonly used for Kerberoasting assessments.

Depending on installation, it may be available as:

```text
GetUserSPNs.py
```

or:

```text
impacket-GetUserSPNs
```

Check:

```bash
which impacket-GetUserSPNs
```

Review current options:

```bash
impacket-GetUserSPNs -h
```

---

# Enumerating SPNs with GetUserSPNs

With authorised domain credentials:

```bash
impacket-GetUserSPNs \
    'corp.example/testuser:<PASSWORD>' \
    -dc-ip 10.10.10.10
```

This can enumerate accounts associated with SPNs.

Output may include information such as:

```text
ServicePrincipalName
Name
MemberOf
PasswordLastSet
LastLogon
Delegation
```

depending on the tool version and directory information available.

---

# Requesting Service Tickets

To request roastable service-ticket material:

```bash
impacket-GetUserSPNs \
    'corp.example/testuser:<PASSWORD>' \
    -dc-ip 10.10.10.10 \
    -request
```

Conceptually:

```text
GetUserSPNs
    |
    v
Enumerate SPNs
    |
    v
TGS-REQ
    |
    v
Domain Controller
    |
    v
TGS-REP
    |
    v
Cracking format
```

---

# Requesting a Specific Account

Where a specific service account has already been identified, use targeted requests where supported by the installed version rather than requesting tickets for every account.

This reduces:

- authentication noise
- unnecessary ticket requests
- evidence volume
- cracking workload

Review:

```bash
impacket-GetUserSPNs -h
```

for the installed version's targeting options.

---

# Output to a File

Where supported:

```bash
impacket-GetUserSPNs \
    'corp.example/testuser:<PASSWORD>' \
    -dc-ip 10.10.10.10 \
    -request \
    -outputfile kerberoast.hashes
```

Protect this file as credential-sensitive assessment evidence.

---

# Password Prompting

Avoid placing plaintext passwords directly in shell history where possible.

Instead of:

```bash
impacket-GetUserSPNs 'corp.example/testuser:Password123!'
```

prefer authentication methods that allow interactive prompting where supported by the installed tool.

If credentials must be supplied through a command during a controlled lab, ensure shell-history and evidence-handling requirements are understood.

---

# Kerberos Authentication with Impacket

If Kerberos authentication is already available, Impacket tools may support options such as:

```text
-k
-no-pass
```

depending on the current credential and ticket environment.

For detailed Impacket authentication methods, see:

[Impacket](impacket.md)

---

# NetExec Enumeration

NetExec can also contribute to Active Directory and LDAP enumeration.

With authorised credentials, start by identifying available protocols and domain information.

Example:

```bash
nxc ldap 10.10.10.10 \
    -d CORP \
    -u '<USER>' \
    -p '<PASSWORD>'
```

NetExec modules and protocol functionality evolve, so inspect the installed version:

```bash
nxc ldap --help
```

and available modules:

```bash
nxc ldap -L
```

before relying on a particular Kerberoasting-related command.

For detailed usage, see:

[NetExec](netexec.md)

---

# Service Ticket Output

Kerberoasting material commonly appears in a format beginning with:

```text
$krb5tgs$...
```

The exact format depends on the Kerberos encryption type.

Treat this material as sensitive.

Do not commit real ticket material to:

```text
Git
GitHub
Documentation repositories
Issue trackers
Public notes
```

---

# Kerberos Encryption Types

Kerberos service tickets may use different encryption types.

Commonly encountered types include:

```text
RC4-HMAC
AES128
AES256
```

The encryption type has a major effect on offline password-cracking cost.

A useful model is:

```text
Service account
      |
      v
Supported encryption types
      |
      v
Ticket encryption type
      |
      v
Offline cracking characteristics
```

Do not assume every Kerberoasting ticket uses RC4.

---

# RC4 and Kerberoasting

RC4-based Kerberos service tickets have historically been especially relevant to Kerberoasting because password guessing against RC4-HMAC service-ticket material is comparatively efficient.

Conceptually:

```text
SPN account
   |
   v
RC4 service ticket
   |
   v
Offline candidate password
   |
   v
Derive candidate key
   |
   v
Test ticket
```

Modern environments should reduce unnecessary RC4 dependencies where compatibility permits.

---

# AES and Kerberoasting

AES-enabled Kerberos does not eliminate Kerberoasting.

Service-ticket material protected using AES can still potentially be subjected to offline password guessing.

However, the computational characteristics differ from RC4.

Therefore:

```text
AES
 |
 X
Not automatically immune to Kerberoasting
```

Strong service-account credentials remain essential.

---

# Do Not Force Downgrades Unnecessarily

During an assessment, avoid manipulating encryption types merely to obtain easier-to-crack ticket material unless downgrade testing is explicitly part of the authorised scope.

Prefer observing and reporting the environment's natural authentication configuration first.

This provides a more representative assessment.

---

# Identifying the Ticket Type

Hashcat can list supported Kerberos modes:

```bash
hashcat --help | grep -i kerberos
```

The captured value itself can also indicate the format:

```text
$krb5tgs$...
```

Select the cracking mode that corresponds to the actual encryption type.

Do not blindly reuse a mode from an old write-up.

---

# Hashcat

Hashcat can perform authorised offline password-strength testing against Kerberos service-ticket material.

General pattern:

```bash
hashcat \
    -m <MODE> \
    kerberoast.hashes \
    wordlist.txt
```

Show recovered results:

```bash
hashcat \
    -m <MODE> \
    kerberoast.hashes \
    --show
```

Determine the correct mode from:

```bash
hashcat --help | grep -i kerberos
```

or the current Hashcat example-hash documentation.

---

# John the Ripper

John the Ripper can also support Kerberos service-ticket formats.

List Kerberos-related formats:

```bash
john --list=formats | grep -i krb
```

General workflow:

```bash
john \
    --wordlist=wordlist.txt \
    kerberoast.hashes
```

Show recovered results:

```bash
john --show kerberoast.hashes
```

Verify compatibility with the installed version before beginning the assessment.

---

# Controlled Password Cracking

Password cracking should answer a security question.

For example:

```text
Does this privileged service account
use a realistically recoverable password?
```

A sensible progression is:

```text
Small common-password list
        |
        v
Organisation-relevant candidates
        |
        v
Approved rule set
        |
        v
Larger dictionary if required
```

Do not automatically run extremely large cracking campaigns when a smaller controlled test already demonstrates the weakness.

---

# Password Rules

Password mutation rules can model predictable human password changes such as:

```text
word
  |
  +--> Capitalisation
  +--> Number suffix
  +--> Year suffix
  +--> Special character
```

For example, a weak organisational password pattern may evolve as:

```text
Service
Service1
Service2026
Service2026!
```

The security issue is the predictable construction, not a particular cracking tool.

---

# Cracking Strategy

A useful assessment workflow is:

```text
Ticket
  |
  v
Identify account
  |
  v
Review password age
  |
  v
Review account purpose
  |
  v
Review password policy
  |
  v
Select realistic candidates
  |
  v
Controlled cracking
```

This is generally preferable to blindly applying enormous wordlists to every service ticket.

---

# Password Age

Old passwords can increase practical Kerberoasting risk.

PowerShell:

```powershell
Get-ADUser \
    -LDAPFilter '(servicePrincipalName=*)' \
    -Properties PasswordLastSet |
    Select-Object SamAccountName,PasswordLastSet
```

Look for service-account passwords that have remained unchanged for unusually long periods.

Do not assume age alone means the password is weak.

A long randomly generated password can remain resistant to offline guessing.

---

# Password Never Expires

Review:

```powershell
Get-ADUser \
    -LDAPFilter '(servicePrincipalName=*)' \
    -Properties PasswordNeverExpires |
    Select-Object SamAccountName,PasswordNeverExpires
```

The risk is:

```text
PasswordNeverExpires
        +
Weak password
        +
SPN
```

rather than `PasswordNeverExpires` by itself.

---

# Privilege Analysis

After identifying a roastable account, determine what the account can actually do.

Questions include:

```text
Is it a Domain Admin?

Is it a local administrator?

Can it use WinRM?

Does it control another AD object?

Can it modify groups?

Does it have delegation rights?

Can it access databases?

Does it own sensitive shares?

Does it have a path to Tier 0?
```

BloodHound is particularly useful for this analysis.

---

# High-Value Service Accounts

Potentially high-impact accounts can include:

- SQL service accounts
- backup service accounts
- application deployment accounts
- monitoring accounts
- automation accounts
- web application service accounts
- privileged middleware accounts
- legacy domain service accounts

The account name alone does not determine risk.

Validate actual privileges.

---

# Domain Admin Service Accounts

A service account should rarely require Domain Admin membership.

If an SPN-enabled service account is a Domain Admin:

```text
SPN
  +
Domain Admin
  +
Weak password
  |
  v
Potential domain compromise
```

This represents both:

```text
Credential weakness
```

and:

```text
Excessive privilege
```

These may warrant separate remediation considerations.

---

# Managed Service Accounts

Windows provides managed service-account technologies designed to reduce dependence on manually managed service passwords.

These include:

```text
sMSA
```

and:

```text
gMSA
```

A major security advantage is automated password management.

---

# Group Managed Service Accounts

A gMSA uses a long, automatically managed password maintained through Active Directory.

Conceptually:

```text
Active Directory
      |
      v
Managed password
      |
      v
gMSA
      |
      v
Authorised hosts
```

This substantially improves resistance to traditional password cracking compared with weak human-generated service-account passwords.

---

# gMSA Is Not a Universal Fix

gMSAs introduce their own security considerations.

The organisation must still protect:

- permissions to retrieve managed passwords
- hosts authorised to use the account
- Active Directory ACLs
- service configuration
- account privileges

Therefore:

```text
gMSA
 |
 +--> Strong managed password
 |
 +--> Reduced manual rotation
 |
 X
Not automatically risk-free
```

---

# Service Account Migration

A useful remediation process is:

```text
Traditional service account
         |
         v
Identify application requirements
         |
         v
Can gMSA be used?
      +--+--+
      |     |
     Yes    No
      |     |
      v     v
 Migrate   Generate strong
           random password
              |
              v
        Automated rotation
```

---

# Validating a Recovered Password

If a password is recovered and credential validation is authorised, use the minimum necessary test.

Example:

```bash
nxc smb 10.10.10.25 \
    -d CORP \
    -u 'svc_sql' \
    -p '<PASSWORD>'
```

This can confirm credential validity.

Do not automatically test the credential against every domain system.

---

# Authentication Success vs Privilege

Always maintain:

```text
Valid password
      |
      X
Administrator
```

A successful service-account login only confirms authentication.

Privilege requires separate validation.

---

# BloodHound Impact Analysis

BloodHound can help minimise unnecessary active testing.

```text
Recovered account
       |
       v
BloodHound
       |
       +--> MemberOf
       +--> AdminTo
       +--> CanRDP
       +--> CanPSRemote
       +--> ACL relationships
       +--> Session relationships
       +--> Paths to high-value targets
```

This helps answer:

```text
What could this credential provide access to?
```

before attempting broad lateral movement.

---

# Kerberoasting and Lateral Movement

A recovered service-account credential may later support:

```text
SMB
WinRM
WMI
RDP
SQL
Application authentication
```

depending on privileges and environment configuration.

These are post-compromise activities and should not be conflated with Kerberoasting itself.

```text
Kerberoasting
      |
      v
Credential recovery
      |
      v
Privilege analysis
      |
      v
Potential lateral movement
```

---

# Kerberoasting and NTLM

The password recovered through Kerberoasting may subsequently be used through:

```text
Kerberos
```

or:

```text
NTLM
```

depending on the service and environment.

If the account's NT hash becomes available through another authorised technique, Pass-the-Hash may also become relevant.

Kerberoasting itself does not return an NT hash.

For NTLM fundamentals, see:

[NTLM](ntlm.md)

---

# Kerberoasting and Pass-the-Hash

Maintain the distinction:

```text
Kerberoast ticket
       |
       v
Offline password cracking
       |
       v
Plaintext password
```

versus:

```text
NT hash
   |
   v
Pass-the-Hash
```

A `$krb5tgs$` value cannot simply be used as an NT hash.

---

# Ticket Request Scope

Avoid requesting every available service ticket simply because the tool permits it.

A targeted approach is preferable:

```text
Enumerate SPNs
      |
      v
Prioritise accounts
      |
      +--> Privilege
      +--> Password age
      +--> Service type
      +--> Business importance
      |
      v
Request selected tickets
```

This reduces unnecessary noise and sensitive data collection.

---

# Detection

Kerberoasting produces Kerberos service-ticket requests that can be visible on domain controllers.

A central event is:

```text
4769 - A Kerberos service ticket was requested
```

---

# Event 4769

Event `4769` can provide information such as:

```text
Account Name
Service Name
Service ID
Ticket Options
Ticket Encryption Type
Client Address
Status
```

Field availability can vary with Windows versions and logging enhancements.

This event is useful for identifying unusual service-ticket request patterns.

---

# Detecting Bulk Ticket Requests

A basic Kerberoasting pattern may look like:

```text
Single user
    |
    +--> MSSQLSvc/service1
    +--> HTTP/service2
    +--> custom/service3
    +--> MSSQLSvc/service4
    +--> HTTP/service5
```

within a short period.

Detection logic can correlate:

```text
Requesting account
        +
Source host
        +
Unique SPNs
        +
Time window
```

---

# Targeted Kerberoasting

A sophisticated or cautious assessment may request only one or two high-value service tickets.

This means:

```text
High volume detection
```

alone is insufficient.

Defenders should also consider:

- unusual requesting hosts
- unusual requesting users
- unusual service-ticket encryption types
- sensitive SPNs
- service accounts with weak configurations
- baseline deviations

---

# Encryption-Type Monitoring

Ticket encryption type can be useful detection context.

A useful model is:

```text
4769
 |
 +--> Requesting user
 +--> Service account
 +--> Service
 +--> Client IP
 +--> Encryption type
```

Unexpected use of legacy encryption types may warrant investigation.

However, encryption type alone should not be treated as proof of Kerberoasting.

---

# RC4 Detection

Where an environment normally uses AES, unexpected RC4 service tickets may deserve attention.

Conceptually:

```text
Environment baseline
       |
       +--> Mostly AES
       |
       v
Unexpected RC4 ticket
       |
       v
Investigate
```

Possible legitimate compatibility requirements must be considered.

---

# Configuration-Based Detection

Defenders should maintain an inventory of SPN-enabled user accounts.

PowerShell:

```powershell
Get-ADUser \
    -LDAPFilter '(servicePrincipalName=*)' \
    -Properties \
        ServicePrincipalName,
        PasswordLastSet,
        PasswordNeverExpires,
        Enabled |
    Select-Object \
        SamAccountName,
        Enabled,
        PasswordLastSet,
        PasswordNeverExpires,
        ServicePrincipalName
```

Review:

```text
Is the account required?

Is the SPN required?

How old is the password?

Is the password managed?

What privileges does the account have?

Can it be migrated to gMSA?
```

---

# Monitor SPN Changes

Changes to SPNs can also be security relevant.

An attacker with sufficient permissions could potentially modify an account's SPNs as part of other Active Directory attack paths.

Monitor changes to:

```text
servicePrincipalName
```

especially on privileged accounts.

---

# Directory Change Monitoring

Useful monitoring can include:

```text
Account modified
       |
       v
SPN added or changed
       |
       v
Review actor
       |
       v
Review target
       |
       v
Validate change request
```

Directory auditing should be configured appropriately before relying on these events.

---

# Offline Cracking Detection

Once the service ticket has been obtained:

```text
Domain Controller
       |
       X
No interaction required for cracking
```

The password-cracking stage happens offline.

Therefore defenders should focus on:

```text
Strong service passwords
       +
Secure account configuration
       +
Service-ticket monitoring
```

rather than expecting to detect the cracking process itself through Active Directory logs.

---

# Post-Credential Detection

If the service-account password is recovered and used, additional events may appear.

Examples include:

```text
4624 - Successful logon
4768 - Kerberos authentication ticket
4769 - Kerberos service ticket
4776 - Credential validation where NTLM is used
```

Correlate:

```text
Unusual service-ticket request
       |
       v
Service account credential use
       |
       v
New source host
       |
       v
Administrative activity
```

---

# Purple Team Validation

Kerberoasting can be tested safely using a dedicated service account.

Example:

```text
PT-Kerberoast
      |
      +--> Controlled SPN
      |
      +--> Known test password
      |
      +--> No production privilege
```

The red team requests a service ticket while the blue team validates telemetry.

---

# Purple Team Exercise Flow

```text
Red Team
   |
   | Enumerate controlled SPN
   v
Domain Controller
   |
   | TGS request
   v
Event 4769
   |
   v
SIEM
   |
   v
Blue Team
   |
   +--> Identify requester?
   +--> Identify source?
   +--> Identify target SPN?
   +--> Identify encryption type?
   +--> Recognise Kerberoasting pattern?
```

---

# Purple Team Metrics

Useful measurements include:

```text
Time to detect
Time to triage
Requesting account identified?
Source host identified?
Service account identified?
SPN identified?
Encryption type identified?
Technique correctly classified?
Response correctly escalated?
```

---

# Hardening

Kerberoasting should be addressed using layered controls.

```text
Kerberoasting
      |
      +--> Strong service credentials
      |
      +--> gMSA
      |
      +--> Remove unnecessary SPNs
      |
      +--> Least privilege
      |
      +--> Modern encryption
      |
      +--> Password rotation
      |
      +--> Ticket monitoring
```

---

# Strong Service Account Passwords

Because Kerberoasting enables offline guessing, service-account passwords should be resistant to large-scale guessing.

Prefer:

```text
Long
Random
Unique
Machine-generated
```

over:

```text
Company2026!
SQLService1!
ServicePassword!
```

Password complexity alone does not guarantee sufficient resistance.

Length and unpredictability are critical.

---

# Use gMSA Where Possible

Where applications support them, group Managed Service Accounts can substantially reduce Kerberoasting password-recovery risk.

Benefits include:

- automatically managed passwords
- long random passwords
- automatic rotation
- reduced administrative handling
- reduced password reuse

---

# Remove Unnecessary SPNs

Review SPNs periodically.

```text
SPN
 |
 +--> Is service still present?
 |
 +--> Is account still used?
 |
 +--> Is duplicate SPN present?
 |
 +--> Is user account required?
```

Remove obsolete service registrations through controlled change management.

---

# Least Privilege

Service accounts should have only the permissions required by their applications.

Avoid:

```text
Service Account
      |
      v
Domain Admins
```

unless an exceptional, documented technical requirement exists.

Review:

- domain groups
- local administrator rights
- delegated AD permissions
- database privileges
- application roles
- remote logon rights

---

# Prefer Modern Kerberos Encryption

Where compatibility permits:

```text
Reduce RC4 dependency
       |
       v
Support AES
```

This improves Kerberos security more broadly.

However, AES does not make weak passwords acceptable.

---

# Rotate Legacy Service Passwords

Where gMSA cannot be used:

```text
Generate strong random password
       |
       v
Store securely
       |
       v
Automate rotation where possible
       |
       v
Monitor service health
```

Avoid manually constructed passwords.

---

# Remove Password-Never-Expires Where Possible

Review whether:

```text
PasswordNeverExpires = True
```

is genuinely required.

If not, migrate to an appropriate managed credential solution.

Do not simply enable password expiration without understanding how the application receives updated credentials.

---

# Protect Privileged Service Accounts

High-value service accounts should receive additional controls.

Consider:

- dedicated service identity
- gMSA
- minimal privileges
- restricted logon rights
- network segmentation
- monitoring
- protected administrative tiers
- denial of interactive logon where appropriate

---

# Reporting

The finding should describe the actual weakness demonstrated.

Possible titles include:

```text
Weak Service Account Password Permits Kerberoasting
```

```text
Kerberoasting Permits Offline Recovery of Privileged Service Account Credentials
```

```text
Legacy Service Accounts Use Weak Passwords Vulnerable to Offline Kerberos Attacks
```

If the password was not recovered, a more accurate title may be:

```text
Kerberos Service Accounts Expose Password-Derived Material for Offline Guessing
```

depending on the organisation's risk model.

---

# Avoid Overstatement

Do not report:

```text
SPN exists = Vulnerable
```

An SPN is a normal Kerberos feature.

The meaningful risk is determined by:

```text
SPN
 |
 +--> Account type
 +--> Password strength
 +--> Encryption
 +--> Password age
 +--> Privileges
 +--> Monitoring
```

---

# Severity Considerations

Consider:

```text
Can ticket material be obtained?
       |
       v
Which encryption type?
       |
       v
How strong is the password?
       |
       v
Was the password recovered?
       |
       v
What privileges does the account have?
       |
       v
What business systems can it access?
```

A low-privilege service account with a strong random password has a different risk profile from a Domain Admin service account with a predictable password.

---

# Example Finding

```text
Finding:
Weak Service Account Password Permits Kerberoasting

Affected Account:
svc_sql

SPN:
MSSQLSvc/sql01.corp.example:1433

Password Age:
Approximately 3 years

Password Expiration:
Disabled

Validation:
An authenticated standard domain user was able to request a Kerberos
service ticket for the affected SPN.

Offline Password Assessment:
The account password was recovered using an approved password dictionary.

Privileges:
The account had administrative access to the SQL server.

Impact:
An attacker with standard domain credentials could obtain password-derived
Kerberos ticket material and recover the service account password offline,
potentially gaining the privileges assigned to the service account.

Recommendation:
Migrate the service to a gMSA where supported. Otherwise use a long,
randomly generated service password with managed rotation. Remove
unnecessary privileges and review legacy Kerberos encryption requirements.
```

---

# Evidence Collection

Useful evidence includes:

```text
Domain
Domain controller
Requesting account
Target service account
SPN
Service class
Target hostname
PasswordLastSet
PasswordNeverExpires
Account enabled/disabled
Group membership
Ticket encryption type
Request timestamp
Source assessment host
Tool
Command
Password recovered?
Validated privileges
```

---

# Protect Sensitive Evidence

Kerberoasting output is credential-sensitive.

Protect:

```text
$krb5tgs$...
Recovered passwords
Credential files
Kerberos tickets
Screenshots
Tool output
```

Use:

- encrypted assessment storage
- restricted access
- evidence retention procedures
- password redaction
- secure deletion after the engagement

---

# Troubleshooting

## GetUserSPNs Cannot Resolve the Domain

Check:

```text
DNS
Domain name
Domain controller
VPN routing
/etc/resolv.conf
/etc/hosts
```

Where appropriate:

```bash
-dc-ip 10.10.10.10
```

can explicitly identify the domain controller.

---

# KDC Unreachable

Check:

```bash
nc -vz 10.10.10.10 88
```

Review:

```text
Routing
Firewall
VPN
Domain controller address
```

---

# LDAP Authentication Fails

Check:

```text
Username
Password
Domain
Bind format
LDAP port
TLS requirements
Account state
```

---

# Clock Skew

Kerberos requires reasonably synchronised clocks.

Check:

```bash
date
```

Large time differences between the assessment host and domain controller can cause authentication errors.

---

# No SPNs Found

Possible explanations include:

- insufficient directory access
- incorrect domain
- LDAP problems
- no user-based SPNs
- only computer-account SPNs
- incorrect query
- tool configuration issue

Verify using multiple methods where appropriate.

---

# Ticket Obtained but Password Not Cracked

This does not mean the test failed.

Record:

```text
Service ticket obtained
Password not recovered within approved effort
```

This is materially different from:

```text
Credential compromised
```

Do not claim password compromise without evidence.

---

# Recovered Password Does Not Authenticate

Possible reasons include:

```text
Password changed after ticket issuance
Account disabled
Authentication restrictions
Incorrect domain context
Service-specific restrictions
Credential parsing error
```

Validate carefully before drawing conclusions.

---

# Common Mistakes

## Mistake 1 - Treating Every SPN as a Vulnerability

SPNs are required for normal Kerberos service authentication.

```text
SPN != Vulnerability
```

The surrounding account configuration determines risk.

---

## Mistake 2 - Confusing Kerberoasting with AS-REP Roasting

Remember:

```text
Kerberoasting
     |
     +--> SPN
     +--> TGS


AS-REP Roasting
     |
     +--> Pre-auth disabled
     +--> AS-REP
```

---

## Mistake 3 - Calling a Kerberos Ticket an NT Hash

A Kerberoasting value is not an NT hash.

```text
$krb5tgs$
    |
    X
NT hash
```

---

## Mistake 4 - Assuming Kerberoasting Requires Administrator Rights

A normal authenticated domain user can generally request legitimate service tickets.

Administrative rights are not inherently required.

---

## Mistake 5 - Assuming the Password Will Be Recovered

Offline cracking is not guaranteed.

A sufficiently strong random password may remain impractical to recover.

---

## Mistake 6 - Ignoring Encryption Type

Always identify the ticket encryption type before evaluating cracking feasibility.

---

## Mistake 7 - Ignoring Account Privilege

A cracked password matters in the context of what the account can access.

Analyse:

```text
Credential
    +
Privileges
    =
Impact
```

---

## Mistake 8 - Requesting Every Ticket

Targeted enumeration and prioritisation generally provide a cleaner assessment.

---

## Mistake 9 - Immediately Using the Password Everywhere

A recovered credential does not justify unrestricted lateral movement.

Validate only the required impact.

---

## Mistake 10 - Recommending Only Password Rotation

Changing the password may address the immediate credential compromise but not the underlying service-account management problem.

Review:

```text
Password generation
Rotation
gMSA compatibility
Privileges
SPNs
Encryption
Monitoring
```

---

# Assessment Checklist

## Preparation

- [ ] Confirm Kerberoasting is authorised
- [ ] Identify domain
- [ ] Identify domain controllers
- [ ] Confirm Kerberos connectivity
- [ ] Confirm DNS
- [ ] Confirm time synchronisation
- [ ] Establish evidence-handling requirements

## SPN Enumeration

- [ ] Enumerate user-based SPNs
- [ ] Identify service accounts
- [ ] Identify service classes
- [ ] Identify target hosts
- [ ] Remove disabled accounts where appropriate
- [ ] Record SPNs
- [ ] Identify duplicate or obsolete SPNs

## Account Analysis

- [ ] Review `PasswordLastSet`
- [ ] Review `PasswordNeverExpires`
- [ ] Review group membership
- [ ] Review delegated privileges
- [ ] Review local administrator relationships
- [ ] Review BloodHound paths
- [ ] Identify gMSA opportunities

## Ticket Requests

- [ ] Prioritise targets
- [ ] Avoid unnecessary bulk requests
- [ ] Record requesting account
- [ ] Record source host
- [ ] Record timestamp
- [ ] Record encryption type
- [ ] Store ticket material securely

## Password Assessment

- [ ] Identify correct cracking format
- [ ] Identify correct Hashcat/John mode
- [ ] Use approved wordlists
- [ ] Use realistic rules
- [ ] Record cracking duration/effort where relevant
- [ ] Record whether password was recovered
- [ ] Stop when sufficient evidence exists

## Impact

- [ ] Validate recovered credential only if authorised
- [ ] Determine actual privileges
- [ ] Review BloodHound relationships
- [ ] Avoid unnecessary lateral movement
- [ ] Record minimum demonstrated impact

## Detection

- [ ] Review Event 4769
- [ ] Correlate requesting account
- [ ] Correlate source host
- [ ] Review unique SPNs requested
- [ ] Review encryption types
- [ ] Monitor SPN changes
- [ ] Correlate post-compromise authentication

## Remediation

- [ ] Use strong random service credentials
- [ ] Migrate to gMSA where possible
- [ ] Rotate compromised passwords
- [ ] Remove unnecessary SPNs
- [ ] Remove excessive privileges
- [ ] Review password-expiration configuration
- [ ] Reduce legacy RC4 dependencies
- [ ] Monitor service-ticket activity

---

# Kerberoasting Testing Model

A useful mental model is:

```text
                    Active Directory
                           |
                           v
                     Domain Users
                           |
                           v
                    SPN Enumeration
                           |
                 +---------+---------+
                 |                   |
                 v                   v
          Computer Account      User Account
                 |                   |
                 v                   v
          Machine-managed      Service account
            credential              |
                                     v
                              Prioritise target
                                     |
                                     v
                                  TGS-REQ
                                     |
                                     v
                                    KDC
                                     |
                                     v
                                  TGS-REP
                                     |
                                     v
                              Service Ticket
                                     |
                                     v
                           Identify encryption
                                     |
                                     v
                           Offline password test
                                     |
                           +---------+---------+
                           |                   |
                           v                   v
                     Not recovered         Recovered
                           |                   |
                           v                   v
                    Record exposure       Credential
                                             |
                                             v
                                      Privilege analysis
                                             |
                                             v
                                      Minimum validation
```

The defensive model is:

```text
Kerberoasting
      |
      +--> Credential strength
      |       |
      |       +--> Long random passwords
      |       +--> gMSA
      |
      +--> Reduce exposure
      |       |
      |       +--> Remove unused SPNs
      |       +--> Remove stale accounts
      |       +--> Modern encryption
      |
      +--> Limit impact
      |       |
      |       +--> Least privilege
      |       +--> Restricted logon
      |
      +--> Detect
              |
              +--> Event 4769
              +--> Ticket-request patterns
              +--> Encryption-type monitoring
              +--> SPN change monitoring
```

The assessment should answer:

```text
Which user accounts have SPNs?
        |
        v
Are those SPNs still required?
        |
        v
How are the service credentials managed?
        |
        v
How old are the passwords?
        |
        v
Which Kerberos encryption types are used?
        |
        v
Can service-ticket material be obtained?
        |
        v
Is the password realistically recoverable?
        |
        v
What privileges does the account possess?
        |
        v
Can defenders detect the ticket requests?
        |
        v
Can the account migrate to a managed identity?
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Password spraying:

[Password Spraying](password-spraying.md)

AS-REP Roasting:

[AS-REP Roasting](asrep-roasting.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement Kerberoasting and can be linked once their dedicated notes are available:

```text
active-directory/pass-the-hash.md
active-directory/overpass-the-hash.md
active-directory/pass-the-key.md
active-directory/lateral-movement.md
active-directory/gmsa.md
```

---

# References

## Microsoft Kerberos

[Microsoft - Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Service Principal Names](https://learn.microsoft.com/en-us/windows/win32/ad/service-principal-names){ target="_blank" rel="noopener noreferrer" }

[Microsoft - setspn](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/setspn){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos encryption type selection](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-supported-encryption-types){ target="_blank" rel="noopener noreferrer" }

---

## Managed Service Accounts

[Microsoft - Group Managed Service Accounts overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Kerberos Tickets: Kerberoasting](https://attack.mitre.org/techniques/T1558/003/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket GetUserSPNs](https://github.com/fortra/impacket/blob/master/examples/GetUserSPNs.py){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## Hashcat

[Hashcat](https://hashcat.net/hashcat/){ target="_blank" rel="noopener noreferrer" }

[Hashcat Example Hashes](https://hashcat.net/wiki/doku.php?id=example_hashes){ target="_blank" rel="noopener noreferrer" }

---

## John the Ripper

[Openwall - John the Ripper](https://www.openwall.com/john/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Kerberoasting is best understood as the interaction between normal Kerberos service-ticket functionality and weak service-account credential management.

The critical distinctions are:

```text
SPN != Vulnerability

Kerberoasting != AS-REP Roasting

Kerberos service ticket != NT hash

Ticket obtained != Password recovered

Password recovered != Administrator

AES != Immunity from Kerberoasting
```

The attack path is:

```text
Authenticated domain user
        |
        v
Enumerate SPNs
        |
        v
Identify service account
        |
        v
Request service ticket
        |
        v
TGS-REP
        |
        v
Password-derived encrypted material
        |
        v
Offline password assessment
        |
        v
Credential recovery
        |
        v
Privilege analysis
        |
        v
Minimum impact validation
```

A mature defence focuses on:

```text
Strong service credentials
        +
gMSA where possible
        +
Modern Kerberos encryption
        +
Least privilege
        +
SPN hygiene
        +
Service-ticket monitoring
```

The objective of an authorised Kerberoasting assessment is not simply to collect as many service tickets as possible. It is to identify service identities whose credential management creates realistic offline password-recovery risk, understand the privileges attached to those identities, validate only the necessary impact, and provide remediation that improves the long-term management of service credentials.
