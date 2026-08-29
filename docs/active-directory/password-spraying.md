# Password Spraying

Password spraying is an authentication attack in which a small number of candidate passwords are tested against multiple user accounts.

Unlike traditional brute-force attacks, which repeatedly test many passwords against a single account, password spraying distributes authentication attempts across multiple accounts.

This distinction is important in Active Directory environments because account lockout policies commonly limit the number of failed authentication attempts permitted for an individual account.

```text
Traditional brute force

User
 |
 +--> Password1
 +--> Password2
 +--> Password3
 +--> Password4
 +--> Password5


Password spraying

Password1
 |
 +--> UserA
 +--> UserB
 +--> UserC
 +--> UserD
 +--> UserE
```

Password spraying is particularly relevant to Active Directory because organisations may have:

- predictable initial passwords
- weak password policies
- seasonal password patterns
- shared onboarding passwords
- passwords derived from organisation names
- passwords derived from locations
- passwords derived from years or months
- legacy accounts
- service accounts
- stale accounts
- accounts excluded from modern authentication controls
- inconsistent MFA coverage

During an authorised penetration test, password spraying should be performed carefully because incorrect planning can cause account lockouts or disrupt production services.

!!! warning "Authorised testing only"
    Password spraying directly interacts with authentication systems and can lock accounts or affect production services. Only perform password spraying where it is explicitly authorised. Determine the effective account lockout policy before testing, use conservative attempt counts, avoid privileged or sensitive accounts unless specifically approved, and stop immediately if unexpected lockouts or service impact occurs.

---

# Password Spraying at a Glance

The basic workflow is:

```text
Enumerate users
      |
      v
Determine lockout policy
      |
      v
Validate username list
      |
      v
Select a small number
of authorised passwords
      |
      v
Calculate safe timing
      |
      v
Perform controlled spray
      |
      v
Identify valid credentials
      |
      v
Validate minimum required impact
      |
      v
Stop spraying successful accounts
      |
      v
Collect evidence
```

The most important step is not selecting passwords.

It is understanding the lockout policy.

---

# Password Spraying vs Brute Force

These techniques should not be treated as equivalent.

## Brute Force

Traditional brute force commonly looks like:

```text
alice
 |
 +--> Password1
 +--> Password2
 +--> Password3
 +--> Password4
 +--> Password5
 +--> Password6
```

This can quickly trigger account lockout controls.

---

## Password Spraying

Password spraying instead distributes attempts:

```text
Password1
 |
 +--> alice
 +--> bob
 +--> charlie
 +--> david
 +--> emma
```

After an appropriate waiting period:

```text
Password2
 |
 +--> alice
 +--> bob
 +--> charlie
 +--> david
 +--> emma
```

This reduces the number of consecutive failures associated with each individual account.

It does **not** make password spraying safe automatically.

---

# Why Password Spraying Works

Password spraying becomes effective when users choose predictable passwords.

Common organisational patterns can include:

```text
CompanyName + Year
Season + Year
Month + Year
Welcome + Number
Location + Number
Department + Number
Product + Number
```

Examples should only be derived from information legitimately available during the assessment.

The objective is not to generate enormous password lists.

Instead:

```text
Context
   |
   v
Small number of
high-probability passwords
   |
   v
Controlled authentication
```

This is generally safer and more representative of password-spraying risk.

---

# Active Directory Account Lockout

Before spraying passwords, determine the effective Active Directory account lockout policy.

Important settings include:

```text
Account lockout threshold
Account lockout duration
Reset account lockout counter after
Minimum password length
Password history
Password complexity
Minimum password age
Maximum password age
```

For password spraying, the most important settings are:

```text
Account lockout threshold
        |
        v
How many failures can occur?


Reset account lockout counter after
        |
        v
How long before failures reset?


Account lockout duration
        |
        v
How long is an account locked?
```

---

# Example Lockout Policy

Suppose the domain policy is:

```text
Account lockout threshold:
5 failed attempts

Reset account lockout counter after:
30 minutes

Account lockout duration:
30 minutes
```

This does **not** mean:

```text
4 passwords every 30 minutes is always safe
```

Other authentication failures may already exist.

For example:

```text
User typo
    |
    v
1 failed attempt

Mobile device with stale password
    |
    v
1 failed attempt

Scheduled task with old credential
    |
    v
1 failed attempt

Password spray
    |
    v
Additional failure
```

The tester may not know the current bad-password count for every account.

A safety margin is therefore essential.

---

# Safe Spray Planning

A conservative approach is:

```text
Lockout threshold
      |
      v
Subtract safety margin
      |
      v
Limit assessment attempts
      |
      v
Wait longer than reset window
```

For example:

```text
Threshold = 5

Do NOT automatically use:
4 attempts

Instead consider:
1 controlled attempt
      |
      v
Wait for reset interval
      |
      v
Next attempt
```

The exact strategy depends on:

- engagement rules
- production sensitivity
- account population
- lockout configuration
- monitoring
- existing authentication failures
- client approval

---

# Fine-Grained Password Policies

A major Active Directory consideration is that the Default Domain Policy may not represent the effective password and lockout policy for every account.

Active Directory supports **Fine-Grained Password Policies**.

Conceptually:

```text
Domain
 |
 +--> Default password policy
 |
 +--> Fine-Grained Password Policy A
 |       |
 |       +--> Group A
 |
 +--> Fine-Grained Password Policy B
         |
         +--> Group B
```

Different users may therefore have different:

- password requirements
- lockout thresholds
- lockout durations
- reset intervals

Always determine whether Fine-Grained Password Policies exist before assuming one domain-wide lockout threshold.

---

# Windows - Domain Password Policy

From a domain-connected Windows system:

```cmd
net accounts /domain
```

Typical information includes:

```text
Minimum password age
Maximum password age
Minimum password length
Length of password history
Lockout threshold
Lockout duration
Lockout observation window
```

Example:

```cmd
net accounts /domain
```

This is a useful initial check but should not be treated as sufficient when Fine-Grained Password Policies are present.

---

# PowerShell - Default Domain Password Policy

If the Active Directory PowerShell module is available:

```powershell
Get-ADDefaultDomainPasswordPolicy
```

Useful properties include:

```text
ComplexityEnabled
LockoutDuration
LockoutObservationWindow
LockoutThreshold
MaxPasswordAge
MinPasswordAge
MinPasswordLength
PasswordHistoryCount
ReversibleEncryptionEnabled
```

Select relevant properties:

```powershell
Get-ADDefaultDomainPasswordPolicy |
    Select-Object `
        LockoutThreshold,
        LockoutDuration,
        LockoutObservationWindow,
        MinPasswordLength,
        MaxPasswordAge,
        PasswordHistoryCount
```

---

# PowerShell - Fine-Grained Password Policies

Enumerate Fine-Grained Password Policies:

```powershell
Get-ADFineGrainedPasswordPolicy -Filter *
```

Display useful properties:

```powershell
Get-ADFineGrainedPasswordPolicy -Filter * |
    Select-Object `
        Name,
        Precedence,
        LockoutThreshold,
        LockoutDuration,
        LockoutObservationWindow,
        MinPasswordLength,
        MaxPasswordAge
```

Determine which users or groups a policy applies to:

```powershell
Get-ADFineGrainedPasswordPolicySubject -Identity '<POLICY_NAME>'
```

Determine the resultant password policy for a specific user:

```powershell
Get-ADUserResultantPasswordPolicy -Identity '<USERNAME>'
```

This is particularly important when the assessment includes accounts belonging to different administrative or business groups.

---

# LDAP Enumeration

Password policy information can also be investigated through LDAP.

The exact attributes and approach depend on:

- domain configuration
- permissions
- LDAP tooling
- Fine-Grained Password Policies
- whether anonymous or authenticated LDAP access is available

Useful policy-related attributes can include:

```text
lockoutThreshold
lockoutDuration
lockOutObservationWindow
minPwdLength
maxPwdAge
minPwdAge
pwdHistoryLength
```

Do not assume the domain-level attributes represent the effective policy for every account.

---

# NetExec Password Policy Enumeration

NetExec can assist with domain policy enumeration where appropriate access is available.

Start by identifying the domain:

```bash
nxc smb 10.10.10.10
```

With authorised credentials:

```bash
nxc smb 10.10.10.10 -u '<USER>' -p '<PASSWORD>'
```

Depending on the current NetExec version and protocol support, modules or enumeration functionality may provide additional domain information.

Always verify the current NetExec command syntax before relying on a specific module during an assessment.

For detailed NetExec usage, see:

[NetExec](netexec.md)

---

# Username Enumeration

Password spraying requires a reliable username list.

Possible authorised sources include:

```text
Active Directory LDAP
        |
        +--> Users
        +--> Groups
        +--> Service accounts

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

The quality of the username list directly affects:

- number of authentication attempts
- detection footprint
- lockout risk
- test accuracy

---

# Active Directory PowerShell User Enumeration

If the Active Directory module is available:

```powershell
Get-ADUser -Filter *
```

Only usernames:

```powershell
Get-ADUser -Filter * |
    Select-Object -ExpandProperty SamAccountName
```

Write them to a file:

```powershell
Get-ADUser -Filter * |
    Select-Object -ExpandProperty SamAccountName |
    Out-File users.txt
```

Useful additional properties:

```powershell
Get-ADUser -Filter * -Properties Enabled,LockedOut,PasswordLastSet |
    Select-Object SamAccountName,Enabled,LockedOut,PasswordLastSet
```

---

# Exclude Disabled Accounts

Disabled accounts generally provide little value for password spraying and unnecessarily increase authentication noise.

PowerShell:

```powershell
Get-ADUser -Filter 'Enabled -eq $true' |
    Select-Object -ExpandProperty SamAccountName
```

---

# Identify Locked Accounts

Where permissions allow:

```powershell
Search-ADAccount -LockedOut
```

A tester should avoid spraying accounts already experiencing lockout problems.

---

# Identify Password-Never-Expires Accounts

Accounts configured with passwords that never expire can warrant additional review:

```powershell
Get-ADUser -Filter * -Properties PasswordNeverExpires |
    Where-Object PasswordNeverExpires -eq $true |
    Select-Object SamAccountName
```

These accounts are not automatically vulnerable.

However, long-lived passwords can increase risk when password hygiene is poor.

---

# Service Accounts

Service accounts require special caution.

A service account may be used by:

```text
Windows service
Scheduled task
Application pool
Database
Backup software
Monitoring platform
Integration service
```

Locking a service account can cause production disruption.

Unless specifically authorised, consider excluding:

- service accounts
- backup accounts
- application accounts
- privileged service accounts
- cluster accounts
- emergency accounts

---

# Privileged Accounts

Privileged accounts should generally receive additional protection during password spraying.

Examples include:

```text
Domain Admins
Enterprise Admins
Administrators
Backup Operators
Account Operators
Server Operators
DNSAdmins
Group Policy administrators
Tier 0 administrative accounts
```

Depending on the rules of engagement, these may be:

```text
Excluded entirely
        |
        or
        v
Tested separately with explicit approval
```

---

# Machine Accounts

Active Directory computer accounts normally end with:

```text
$
```

Examples:

```text
DC01$
FILE01$
WS001$
```

These should normally be removed from human-user spray lists.

For example:

```bash
grep -v '\$$' users.txt > human-users.txt
```

---

# Clean Username Lists

Before spraying:

```bash
sort -u users.txt > users-unique.txt
```

Remove blank lines:

```bash
sed '/^[[:space:]]*$/d' users-unique.txt > users-clean.txt
```

Inspect:

```bash
wc -l users-clean.txt
head users-clean.txt
tail users-clean.txt
```

A clean username list reduces unnecessary authentication attempts.

---

# Username Validation with Kerberos

Kerberos can sometimes be used to validate whether candidate usernames exist without attempting a password.

Conceptually:

```text
Candidate username
       |
       v
Kerberos request
       |
       v
KDC response
       |
       +--> User likely exists
       |
       +--> User not found
```

This can improve the quality of a spray list before authentication testing begins.

However, username enumeration still generates authentication-related traffic and should remain within scope.

---

# Kerbrute

Kerbrute is commonly used during Active Directory assessments for Kerberos-based username validation and controlled password-spraying operations.

Project:

[Kerbrute](https://github.com/ropnop/kerbrute){ target="_blank" rel="noopener noreferrer" }

Typical username enumeration syntax:

```bash
kerbrute userenum \
    -d corp.example \
    --dc 10.10.10.10 \
    users.txt
```

The exact command options can vary by version.

Always review:

```bash
kerbrute --help
```

before testing.

---

# Kerberos Username Enumeration Workflow

A useful workflow is:

```text
Large candidate list
       |
       v
Kerberos username validation
       |
       v
Valid users
       |
       v
Remove sensitive accounts
       |
       v
Review lockout policy
       |
       v
Controlled password spray
```

This reduces unnecessary password attempts against nonexistent accounts.

For Kerberos fundamentals, see:

[Kerberos](kerberos.md)

---

# Kerberos Password Spraying

Password spraying can be performed against Kerberos authentication.

Conceptually:

```text
Username + Password
        |
        v
Kerberos KDC
        |
        v
Authentication response
        |
        +--> Valid
        |
        +--> Invalid
```

A common advantage during assessment is that authentication can be evaluated directly against the domain controller rather than attempting SMB authentication across numerous hosts.

---

# Kerbrute Password Spray

After:

- determining the lockout policy
- validating usernames
- excluding sensitive accounts
- selecting one approved candidate password

a controlled Kerbrute spray can conceptually use:

```bash
kerbrute passwordspray \
    -d corp.example \
    --dc 10.10.10.10 \
    users-clean.txt \
    '<PASSWORD>'
```

Do not supply a large password list without calculating safe timing.

A safer assessment model is:

```text
One password
    |
    v
Approved user list
    |
    v
Wait
    |
    v
Review results
    |
    v
Only continue when safe
```

---

# NetExec Password Spraying

NetExec can test credentials against services such as SMB.

Basic pattern:

```bash
nxc smb 10.10.10.10 \
    -u users.txt \
    -p '<PASSWORD>'
```

Specify the domain when appropriate:

```bash
nxc smb 10.10.10.10 \
    -d CORP \
    -u users.txt \
    -p '<PASSWORD>'
```

This should only be performed after understanding the lockout policy.

---

# Stop on Success

Once an account successfully authenticates, it should generally be removed from subsequent password sprays.

Conceptually:

```text
alice -> failed
bob   -> SUCCESS
carol -> failed
david -> failed
```

Next spray:

```text
alice
carol
david
```

not:

```text
alice
bob       <-- unnecessary
carol
david
```

Continuing to spray a successfully compromised account:

- adds unnecessary risk
- creates unnecessary logs
- provides little assessment value
- may expose the account to lockout later

---

# One Password at a Time

A conservative workflow is:

```text
Password candidate 1
        |
        v
Spray
        |
        v
Record successes
        |
        v
Remove successful users
        |
        v
Wait for safe interval
        |
        v
Password candidate 2
```

Avoid:

```text
100 passwords
     |
     v
1000 users
     |
     v
Immediate spray
```

This is brute-force behaviour rather than controlled password spraying.

---

# Timing

Password-spraying timing should be based on the effective lockout policy.

Suppose:

```text
Lockout threshold:
5

Observation window:
30 minutes
```

A conservative test may use:

```text
1 attempt
   |
   v
Wait > observation window
   |
   v
Next attempt
```

For example:

```text
09:00 - Candidate password 1
09:35 - Candidate password 2
10:10 - Candidate password 3
```

The additional buffer helps account for:

- clock differences
- replication
- processing delays
- existing authentication failures

The exact timing must be agreed for the engagement.

---

# Lockout Safety Margin

Never assume:

```text
Threshold = 5
```

means:

```text
4 attempts are safe
```

A safer mental model is:

```text
Unknown existing failures
          +
Assessment failures
          <
Lockout threshold
```

Because the first value may not be known, use a conservative margin.

---

# Bad Password Count

Active Directory maintains information related to failed password attempts.

Where permissions and environment behaviour permit, this can provide additional context during an assessment.

However, account lockout behaviour involves replication and domain controller-specific considerations.

Do not design an aggressive spray strategy based solely on a single observed counter.

Treat lockout policy plus conservative timing as the primary safety control.

---

# Domain Controllers

In environments with multiple domain controllers:

```text
           Domain
             |
      +------+------+
      |             |
      v             v
     DC01          DC02
```

Authentication behaviour and bad-password tracking can involve replication and special handling between domain controllers.

Do not attempt to bypass lockout protections by deliberately distributing authentication attempts between domain controllers.

The objective of an authorised assessment is to validate password risk, not defeat safety controls.

---

# Selecting Candidate Passwords

Candidate passwords should be:

- few in number
- evidence-based
- relevant to the organisation
- explicitly permitted by the engagement
- unlikely to cause unnecessary authentication volume

Potential sources can include:

```text
Known password policy
Public organisation name
Public product names
Public locations
Known onboarding conventions
Previously provided test credentials
Client-approved password patterns
```

Do not collect unnecessary personal information about employees merely to generate password guesses.

---

# Seasonal Passwords

A common password pattern in some environments is:

```text
Season + Year
```

Examples conceptually include:

```text
<Season><Year>
<Season><Year>!
<Season>@<Year>
```

The security issue is not the exact pattern.

The issue is predictable organisational password construction.

---

# Organisation-Based Passwords

Another common pattern is:

```text
OrganisationName + Number
OrganisationName + Year
OrganisationName + SpecialCharacter
```

If one predictable password succeeds across multiple users, the finding may indicate a broader password-policy or onboarding weakness.

---

# Default and Onboarding Passwords

Particularly important patterns include:

```text
Welcome123...
ChangeMe...
CompanyName...
Temporary password formats
```

An assessment should determine whether:

- temporary passwords are unique
- users must change them
- temporary passwords expire
- MFA protects first login
- onboarding credentials are communicated securely

---

# Password Spraying Through SMB

SMB is commonly used for credential validation.

Conceptually:

```text
Tester
  |
  v
TCP/445
  |
  v
SMB
  |
  v
NTLM / Kerberos
  |
  v
Domain authentication
```

However, SMB spraying can create significant authentication telemetry.

Where a single domain controller or Kerberos service can provide the required validation, avoid unnecessarily spraying large numbers of endpoints.

---

# Password Spraying and NTLM

Password spraying and NTLM are related but separate concepts.

```text
Password spraying
       |
       v
Authentication attempt
       |
       +--> Kerberos
       |
       +--> NTLM
```

The attack technique is password spraying.

NTLM or Kerberos is the authentication mechanism being tested.

For NTLM fundamentals, see:

[NTLM](ntlm.md)

---

# Password Spraying and MFA

Successful password authentication does not necessarily mean an attacker can complete application authentication.

For example:

```text
Correct password
      |
      v
Application
      |
      v
MFA challenge
      |
      X
Access blocked
```

However, a valid password remains security-sensitive because it may work against:

- services without MFA
- legacy authentication
- SMB
- LDAP
- VPN services
- internal applications
- remote management interfaces

Therefore:

```text
MFA present
```

does not automatically make weak passwords harmless.

---

# Password Spraying and Legacy Authentication

Legacy protocols and applications may not enforce modern controls consistently.

During an assessment, identify whether successful credentials can authenticate through:

```text
SMB
LDAP
IMAP
POP
SMTP
VPN
WinRM
RDP gateways
Legacy web applications
```

Only test protocols explicitly included in scope.

---

# Password Spraying from Windows

Where domain authentication testing is authorised, Windows-native mechanisms can sometimes validate credentials.

However, repeated interactive authentication attempts through commands such as:

```text
runas
net use
PowerShell remoting
```

may create sessions, access resources, or produce side effects.

Purpose-built assessment tooling is usually preferable because it allows more controlled behaviour and logging.

---

# Controlled SMB Validation

For a single credential pair, Windows can validate access to a controlled SMB resource.

Example:

```cmd
net use \\SERVER\IPC$ /user:CORP\testuser *
```

The password can then be entered interactively.

Clean up:

```cmd
net use \\SERVER\IPC$ /delete
```

This should not be scripted across large account lists as a substitute for proper spray tooling.

---

# Valid Credential Handling

When valid credentials are identified:

```text
Valid credential
      |
      v
Record securely
      |
      v
Remove account from spray
      |
      v
Determine authorised validation scope
      |
      v
Perform minimum required validation
```

Do not immediately attempt:

```text
Every host
Every service
Every administrative protocol
```

unless that activity is explicitly part of the engagement.

---

# Determine Account Privileges

A successful password spray only proves:

```text
Valid username + password
```

It does not prove:

```text
Administrator
Domain Admin
Remote access
Lateral movement
```

Privilege analysis should be performed separately.

Possible follow-up questions include:

```text
What groups is the account in?

What systems can it access?

Does it have remote logon rights?

Does it have local administrator rights?

Does BloodHound identify useful relationships?
```

For graph-based privilege analysis, see:

[BloodHound](bloodhound.md)

---

# BloodHound Relationship

BloodHound can help determine the potential significance of an account recovered during a password spray.

Conceptually:

```text
Spray
  |
  v
Valid account
  |
  v
BloodHound
  |
  +--> Group membership
  +--> Local admin
  +--> Remote access
  +--> ACL relationships
  +--> Session relationships
  +--> Paths to privileged assets
```

This allows the assessment to move from:

```text
Credential discovered
```

to:

```text
Credential impact understood
```

without blindly attempting authentication against every system.

---

# Password Spraying vs Password Reuse

Password spraying tests:

```text
One candidate password
       |
       v
Many accounts
```

Password reuse testing may instead examine:

```text
One known credential
       |
       v
Multiple authorised services
```

These are different assessment activities and should be reported separately where appropriate.

---

# Password Spraying vs Credential Stuffing

Credential stuffing generally involves credentials obtained from another source:

```text
Known username/password pairs
          |
          v
Target service
```

Password spraying instead commonly uses:

```text
One password
     |
     v
Many usernames
```

The distinction matters when describing the finding.

---

# Detection

Password spraying can often be detected by analysing authentication failures across many accounts.

Traditional brute force:

```text
One account
    |
    +--> Many failures
```

Password spraying:

```text
One source
    |
    +--> Failure for UserA
    +--> Failure for UserB
    +--> Failure for UserC
    +--> Failure for UserD
```

Detection therefore requires correlation across accounts.

---

# Relevant Windows Events

Useful events can include:

```text
4624 - Successful logon
4625 - Failed logon
4771 - Kerberos pre-authentication failed
4776 - Credential validation
4740 - User account locked out
```

The exact event depends on:

- authentication protocol
- target system
- domain controller
- logon type
- audit configuration

---

# Event 4625

Event `4625` records failed logon attempts.

Useful fields can include:

```text
Account Name
Account Domain
Logon Type
Failure Reason
Status
Sub Status
Workstation Name
Source Network Address
Authentication Package
```

A password spray may produce:

```text
Same source
     |
     +--> UserA failure
     +--> UserB failure
     +--> UserC failure
     +--> UserD failure
```

within a relatively short period.

---

# Event 4771

Event `4771` records Kerberos pre-authentication failures.

This can be particularly relevant for Kerberos password spraying.

Potential detection model:

```text
Source IP
   |
   +--> many usernames
   |
   +--> repeated pre-auth failures
   |
   +--> similar timestamps
```

Correlate the event with:

- source IP
- user
- failure code
- domain controller
- timestamp

---

# Event 4776

Event `4776` records credential validation attempts and can be useful for NTLM-related authentication analysis.

A spray pattern may resemble:

```text
Single workstation/source
          |
          v
Many account validation failures
```

This can be particularly valuable where authentication occurs through NTLM.

---

# Event 4740

Event `4740` indicates an account was locked out.

During an authorised password spray:

```text
4740 generated
      |
      v
STOP
      |
      v
Investigate immediately
```

Unexpected account lockouts should be treated as a safety event.

---

# Detecting Low-and-Slow Sprays

Attackers may intentionally spread attempts over long periods.

For example:

```text
09:00 -> 20 users
10:00 -> 20 users
11:00 -> 20 users
12:00 -> 20 users
```

Simple short detection windows may miss this behaviour.

Defenders should consider:

```text
Source
   +
Unique usernames
   +
Authentication failures
   +
Longer time window
```

---

# Distributed Password Spraying

A spray can also originate from multiple sources.

Conceptually:

```text
Source A --> User1
Source B --> User2
Source C --> User3
Source D --> User4
```

Detection therefore should not rely exclusively on:

```text
many failures from one IP
```

Other useful correlations include:

- common password-related failure patterns
- unusual authentication geography
- common infrastructure
- targeted account population
- timing
- device identity
- application
- user-agent characteristics where applicable

---

# Successful Spray Detection

The most important event may be the successful authentication after a series of failures.

Conceptually:

```text
UserA -> failure
UserB -> failure
UserC -> failure
UserD -> SUCCESS
```

Defenders should correlate:

```text
Authentication failures
        |
        v
Successful authentication
        |
        v
Post-authentication activity
```

This can reveal a successful password spray.

---

# Post-Authentication Behaviour

After a successful spray, suspicious activity may include:

- SMB enumeration
- LDAP enumeration
- BloodHound collection
- remote management
- share enumeration
- privilege discovery
- group enumeration
- session discovery
- lateral movement

Detection should therefore connect authentication telemetry with subsequent activity.

---

# Purple Team Validation

Password spraying is useful for controlled purple-team exercises because the technique produces measurable authentication telemetry.

Example:

```text
Red Team
   |
   | Controlled spray
   v
Domain Controller
   |
   | Authentication events
   v
SIEM / EDR
   |
   v
Blue Team
   |
   +--> Detect source?
   +--> Identify targeted users?
   +--> Identify authentication protocol?
   +--> Identify successful account?
   +--> Respond appropriately?
```

Useful metrics include:

```text
Time to detect
Time to triage
Number of targeted accounts identified
Successful account identified?
Source identified?
Authentication protocol identified?
Account locked unnecessarily?
Response escalated correctly?
```

---

# Safe Purple Team Exercise

A controlled exercise can use dedicated test accounts.

For example:

```text
PT-Test-User01
PT-Test-User02
PT-Test-User03
PT-Test-User04
PT-Test-User05
```

Then:

```text
One approved incorrect password
       |
       v
Controlled Kerberos authentication
       |
       v
Generate expected failures
       |
       v
Blue-team investigation
```

A separate test account can intentionally use the candidate password if a successful-authentication signal is required.

This avoids risking production user accounts while still validating detection logic.

---

# Hardening

Password spraying is best mitigated through multiple controls.

```text
Password Spraying
       |
       +--> Strong passwords
       |
       +--> MFA
       |
       +--> Smart lockout
       |
       +--> Disable legacy authentication
       |
       +--> Conditional access
       |
       +--> Password blocklists
       |
       +--> Monitor authentication
       |
       +--> Protect privileged accounts
```

---

# Strong Passwords

Long, unique passwords significantly reduce the probability that a small number of guessed passwords will succeed.

Avoid organisational password patterns such as:

```text
Company2026!
Summer2026!
Welcome123!
```

Password policy should focus on resistance to guessing rather than merely satisfying predictable complexity transformations.

---

# Password Blocklists

Organisations should prevent passwords based on:

- organisation name
- product names
- common passwords
- predictable seasonal patterns
- known breached passwords
- common password mutations

Conceptually:

```text
User selects password
        |
        v
Password policy
        |
        +--> Length
        +--> Known weak password?
        +--> Organisation-specific term?
        +--> Breached password?
        |
        v
Accept / Reject
```

---

# Multi-Factor Authentication

MFA significantly reduces the impact of a successfully guessed password for services that enforce it correctly.

However:

```text
Password compromised
       +
MFA enabled
```

still requires investigation.

The password may remain usable against services that do not enforce MFA.

---

# Protect Legacy Protocols

Review services that may accept username/password authentication without modern controls.

Examples can include:

```text
SMB
LDAP
VPN
Legacy web applications
Older mail protocols
Remote management services
```

Disable unnecessary services and authentication mechanisms where possible.

---

# Account Lockout

Account lockout policies can slow password attacks but must balance:

```text
Security
   |
   v
Prevent guessing

vs

Availability
   |
   v
Prevent attacker-triggered denial of service
```

An overly aggressive lockout policy can allow attackers to intentionally lock large numbers of accounts.

---

# Privileged Account Protection

Administrative accounts should use stronger controls.

Consider:

- dedicated administrative accounts
- MFA
- privileged access workstations
- authentication silos where appropriate
- restricted logon locations
- separate administrative tiers
- strong unique passwords
- monitoring

Privileged accounts should not use predictable passwords.

---

# Service Account Protection

Where possible:

- use gMSA for compatible Windows services
- use long randomly generated credentials
- rotate credentials
- avoid interactive logon
- restrict logon locations
- monitor authentication
- remove unused service accounts

Service accounts should not rely on human-generated predictable passwords.

---

# Reporting

A successful password spray should be reported based on the actual weakness demonstrated.

Possible finding titles include:

```text
Predictable Passwords Permit Domain Account Compromise
```

```text
Weak Password Policy Permits Password Spraying
```

```text
Shared Onboarding Password Allows Multiple Account Compromise
```

```text
Insufficient Authentication Controls Permit Password Spraying
```

Avoid simply calling the finding:

```text
Password Spraying
```

Password spraying is the testing technique.

The underlying security weakness is usually:

```text
Weak/predictable passwords
        |
        +
Insufficient authentication protection
```

---

# Example Finding

```text
Finding:
Predictable Password Permits Domain Account Compromise

Affected Environment:
corp.example

Technique:
Controlled password spraying

Accounts Tested:
42 authorised standard user accounts

Candidate Passwords:
1

Successful Accounts:
2

Lockouts:
0

Impact:
An attacker who identifies valid usernames could potentially compromise
domain accounts using a small number of predictable password guesses.

Validation:
Authentication was confirmed using controlled domain authentication.
No lateral movement was required to demonstrate the issue.

Recommendation:
Require stronger passwords, prevent organisation-specific predictable
password patterns, deploy MFA where applicable, and monitor authentication
failures across multiple accounts.
```

Do not include plaintext passwords in the final report unless explicitly required.

---

# Evidence Collection

Record:

```text
Domain
Domain controller
Date/time
Source system
Authentication protocol
Lockout threshold
Lockout observation window
Lockout duration
Number of accounts tested
Number of candidate passwords
Number of successful accounts
Number of failed attempts
Any account lockouts
Tool
Command
Sanitised output
```

Do not store unnecessary credential material.

---

# Password Redaction

Instead of:

```text
Password: Summer2026!
```

prefer:

```text
Password:
[REDACTED]
```

or:

```text
Candidate password:
Organisation-derived seasonal password
```

Screenshots should also redact passwords and sensitive authentication material.

---

# Troubleshooting

## Every Authentication Attempt Fails

Check:

```text
Domain name
Domain controller
Username format
DNS
Time synchronisation
Authentication protocol
Account state
Password
Firewall
```

---

## Valid Credential Fails with NetExec

Verify whether the account is:

```text
Domain account
```

or:

```text
Local account
```

Domain example:

```bash
nxc smb 10.10.10.25 \
    -d CORP \
    -u testuser \
    -p '<PASSWORD>'
```

Local example:

```bash
nxc smb 10.10.10.25 \
    --local-auth \
    -u testuser \
    -p '<PASSWORD>'
```

---

## Kerbrute Cannot Reach the KDC

Check:

```text
Domain controller address
Port 88/TCP
Port 88/UDP
Firewall
VPN routing
DNS
Domain name
```

Test connectivity:

```bash
nc -vz 10.10.10.10 88
```

---

## Unexpected Account Lockout

Immediately stop the spray.

```text
Lockout detected
      |
      v
STOP
      |
      v
Record timestamp
      |
      v
Identify affected account
      |
      v
Notify engagement contact
      |
      v
Investigate cause
```

Do not continue simply because other accounts remain unlocked.

---

# Common Mistakes

## Mistake 1 - Not Checking Lockout Policy

Never start with:

```text
users.txt
passwords.txt
      |
      v
SPRAY
```

Start with:

```text
Lockout policy
      |
      v
User validation
      |
      v
Safe timing
      |
      v
Spray
```

---

## Mistake 2 - Using the Lockout Threshold as the Spray Limit

If:

```text
Threshold = 5
```

do not assume:

```text
4 attempts = safe
```

Existing authentication failures may already exist.

---

## Mistake 3 - Ignoring Fine-Grained Password Policies

The domain default may not apply to every account.

Always consider:

```text
Default Domain Policy
        +
Fine-Grained Password Policies
```

---

## Mistake 4 - Spraying Service Accounts

Service account lockout can cause production outages.

Identify and exclude them unless specifically approved.

---

## Mistake 5 - Spraying Disabled Accounts

Disabled accounts add noise without useful validation.

Clean the user list first.

---

## Mistake 6 - Spraying Machine Accounts

Computer accounts normally end in:

```text
$
```

Remove them from normal user spray lists.

---

## Mistake 7 - Continuing to Spray Successful Accounts

Once an account succeeds:

```text
Remove it
```

from subsequent rounds.

---

## Mistake 8 - Testing Too Many Passwords

Password spraying should use a small number of high-confidence candidates.

Large password lists turn the activity into brute-force testing.

---

## Mistake 9 - Assuming MFA Eliminates the Finding

A valid password may remain useful against services without MFA.

Determine actual exposure.

---

## Mistake 10 - Assuming a Valid Password Means Administrator

Authentication success proves credential validity.

Privilege must be assessed separately.

---

# Assessment Checklist

## Preparation

- [ ] Confirm password spraying is explicitly in scope
- [ ] Identify production sensitivity
- [ ] Confirm emergency contact
- [ ] Confirm stop conditions
- [ ] Determine whether privileged accounts may be tested
- [ ] Determine whether service accounts may be tested
- [ ] Confirm permitted authentication protocols

## Lockout Policy

- [ ] Determine account lockout threshold
- [ ] Determine lockout duration
- [ ] Determine observation/reset window
- [ ] Identify Fine-Grained Password Policies
- [ ] Determine resultant policies where necessary
- [ ] Establish a conservative safety margin

## User Enumeration

- [ ] Build candidate username list
- [ ] Remove duplicates
- [ ] Remove machine accounts
- [ ] Remove disabled accounts
- [ ] Identify service accounts
- [ ] Identify privileged accounts
- [ ] Validate usernames where appropriate
- [ ] Record final authorised spray population

## Password Selection

- [ ] Use a small number of candidates
- [ ] Base candidates on legitimate assessment context
- [ ] Avoid unnecessary personal information
- [ ] Consider organisation-specific weak patterns
- [ ] Consider onboarding patterns
- [ ] Confirm candidate list is authorised

## Execution

- [ ] Use one candidate password at a time
- [ ] Respect observation/reset window
- [ ] Add a safety buffer
- [ ] Monitor for lockouts
- [ ] Record timestamps
- [ ] Remove successful accounts
- [ ] Stop if unexpected behaviour occurs

## Validation

- [ ] Confirm successful authentication
- [ ] Determine local vs domain account
- [ ] Determine authentication protocol
- [ ] Determine account privileges separately
- [ ] Validate only minimum required impact
- [ ] Avoid unnecessary lateral movement

## Detection

- [ ] Review Event 4625
- [ ] Review Event 4771
- [ ] Review Event 4776
- [ ] Review Event 4740
- [ ] Correlate failures across users
- [ ] Correlate successful authentication
- [ ] Review post-authentication activity
- [ ] Test longer detection windows

## Reporting

- [ ] Record domain
- [ ] Record lockout policy
- [ ] Record number of accounts tested
- [ ] Record number of password candidates
- [ ] Record successful accounts
- [ ] Record any lockouts
- [ ] Redact passwords
- [ ] Describe actual underlying weakness
- [ ] Provide remediation

---

# Password Spraying Testing Model

A useful mental model is:

```text
                  Password Spraying
                         |
                         v
                  Authorised Scope
                         |
                         v
                  Lockout Policy
                         |
             +-----------+-----------+
             |                       |
             v                       v
      Default Policy          Fine-Grained Policy
             |                       |
             +-----------+-----------+
                         |
                         v
                    User List
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          Disabled    Service     Privileged
          accounts    accounts    accounts
             |           |           |
             +------ Exclude / Review
                         |
                         v
                 Valid User Population
                         |
                         v
                Candidate Password
                         |
                         v
               Authentication Protocol
                         |
                  +------+------+
                  |             |
                  v             v
              Kerberos        NTLM
                  |             |
                  +------+------+
                         |
                         v
                    Result
                         |
             +-----------+-----------+
             |                       |
             v                       v
           Failure                 Success
             |                       |
             v                       v
       Monitor lockout        Remove from spray
             |                       |
             v                       v
          Wait safely         Validate impact
             |
             v
        Next candidate
```

The assessment should therefore answer:

```text
What is the effective lockout policy?
        |
        v
Which accounts can safely be tested?
        |
        v
Which password patterns are realistic?
        |
        v
How many attempts are necessary?
        |
        v
Can valid credentials be identified?
        |
        v
What privileges do those credentials actually provide?
        |
        v
Can defenders detect the spray?
        |
        v
Which controls would prevent recurrence?
```

The goal is not to generate the largest number of authentication attempts.

The goal is to determine whether a small number of predictable password guesses can compromise Active Directory accounts while maintaining a controlled, measurable, and safe assessment.

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

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement password spraying and can be linked once their dedicated notes are available:

```text
active-directory/asrep-roasting.md
active-directory/kerberoasting.md
active-directory/pass-the-hash.md
active-directory/responder.md
active-directory/ntlm-relay.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft

[Microsoft - Account lockout threshold](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/account-lockout-threshold){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Account lockout duration](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/account-lockout-duration){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Reset account lockout counter after](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/reset-account-lockout-counter-after){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Fine-Grained Password Policies](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/fine-grained-password-policies){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-ADDefaultDomainPasswordPolicy](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-addefaultdomainpasswordpolicy){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-ADFineGrainedPasswordPolicy](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adfinegrainedpasswordpolicy){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-ADUserResultantPasswordPolicy](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-aduserresultantpasswordpolicy){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Password Spraying T1110.003](https://attack.mitre.org/techniques/T1110/003/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

[NetExec SMB Protocol](https://www.netexec.wiki/smb-protocol){ target="_blank" rel="noopener noreferrer" }

---

## Kerbrute

[Kerbrute - GitHub](https://github.com/ropnop/kerbrute){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Password spraying is best understood as an authentication testing methodology rather than simply a command executed by a particular tool.

The critical distinctions are:

```text
Password spraying != brute force

Valid password != administrative access

Domain default policy != every user's effective policy

Lockout threshold != safe attempt count

MFA != permission to ignore weak passwords
```

A mature Active Directory password-spraying assessment follows:

```text
Authorisation
      |
      v
Lockout Policy
      |
      v
Fine-Grained Policies
      |
      v
User Enumeration
      |
      v
Account Exclusions
      |
      v
Password Selection
      |
      v
Safe Timing
      |
      v
Controlled Spray
      |
      v
Valid Credential
      |
      v
Minimum Impact Validation
      |
      v
Detection Review
      |
      v
Remediation
```

The objective is to demonstrate whether predictable credentials expose the organisation to account compromise while minimising operational risk and generating evidence that can be used to improve both preventive and detective controls.
