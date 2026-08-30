# Unconstrained Delegation

Unconstrained Kerberos delegation is an Active Directory configuration that allows a trusted service to act on behalf of an authenticated user when accessing other Kerberos services.

It was designed to solve the Kerberos "double-hop" problem.

A simplified legitimate use case is:

```text
User
 |
 v
Front-End Server
 |
 | Needs to access another resource
 | as the user
 v
Back-End Server
```

Without delegation:

```text
User
 |
 v
Front-End Server
 |
 X
Cannot automatically reuse the
user's authentication context
for another Kerberos service
```

With delegation:

```text
User
 |
 v
Delegation-Enabled Server
 |
 | Acts on behalf of user
 v
Back-End Service
```

Unconstrained delegation is the broadest and least restrictive form of Kerberos delegation.

Microsoft describes it as allowing the front-end service to access other services on the client's behalf without restricting the destination services, and recommends against using unconstrained delegation because of this broad trust model.

The security concern is therefore:

```text
Unconstrained Delegation
        |
        v
Broad Delegation Capability
        |
        v
High-Value User Authenticates
        |
        v
Delegated Authentication Material
        |
        v
Compromise of Delegation Host
        |
        v
Potential Impersonation
```

!!! warning "Authorised testing only"
    Unconstrained delegation testing can expose reusable Kerberos authentication material belonging to other users. Only perform active validation against accounts and systems explicitly included in scope. Avoid coercing privileged production identities to authenticate unless this has been specifically approved. A configuration finding can often be demonstrated through enumeration and controlled test accounts without interacting with real administrator credentials.

---

# Delegation Types

Active Directory supports several Kerberos delegation models.

```text
Kerberos Delegation
       |
       +--> Unconstrained Delegation
       |
       +--> Constrained Delegation
       |
       +--> Resource-Based
            Constrained Delegation
```

A useful comparison is:

| Delegation Type | Where Trust Is Defined | Scope |
|---|---|---|
| Unconstrained Delegation | Front-end service account | Broad |
| Constrained Delegation | Front-end service account | Specific services |
| RBCD | Back-end resource | Specific principals |

Microsoft currently describes unconstrained delegation as the easiest model to implement but the least secure because the services to which the front-end can act on behalf of the user are not restricted.

---

# The Double-Hop Problem

The purpose of delegation is easiest to understand through the double-hop problem.

Consider:

```text
User
 |
 | Hop 1
 v
Web Server
 |
 | Hop 2
 v
Database Server
```

The user authenticates to:

```text
WEB01
```

The application on `WEB01` then needs to access:

```text
SQL01
```

as the user.

Without delegation:

```text
User
 |
 v
WEB01
 |
 X
No suitable delegated user
authentication for SQL01
```

Delegation provides a mechanism for:

```text
WEB01
 |
 v
Act on behalf of User
 |
 v
SQL01
```

---

# Why Unconstrained Delegation Exists

Legacy enterprise applications commonly required:

```text
Client
 |
 v
Application Server
 |
 v
Database / File Server
```

while preserving the user's identity through the entire transaction.

Examples might include:

```text
IIS
 |
 v
SQL Server
```

or:

```text
Application Server
 |
 v
File Server
```

Unconstrained delegation provided a simple solution.

The problem is that its trust boundary is extremely broad.

---

# Unconstrained Delegation Model

The core concept is:

```text
User
 |
 | Kerberos Authentication
 v
Server Trusted for
Unconstrained Delegation
 |
 | Delegated user context
 v
Other Kerberos Services
```

Unlike constrained delegation:

```text
Unconstrained
     |
     v
Any suitable Kerberos service
```

rather than:

```text
Constrained
     |
     v
Explicitly configured services
```

---

# Security Impact

The main security risk appears when the delegation-enabled system itself is compromised.

```text
Privileged User
      |
      v
Authenticates to
Delegation Server
      |
      v
Delegated Kerberos
Authentication Material
      |
      v
Attacker Controls Server
      |
      v
Authentication Material Exposed
      |
      v
Potential Impersonation
```

The problem is therefore not simply:

```text
Delegation enabled
```

but:

```text
Delegation enabled
       +
Sensitive identity authenticates
       +
Delegation host compromised
```

---

# Why It Is Dangerous

A server configured for unconstrained delegation becomes an important credential boundary.

Consider:

```text
DC01
 |
 | Administrator authenticates
 v
APP01
 |
 | Unconstrained Delegation
 v
Reusable delegated context
```

If:

```text
APP01
```

is compromised, the attacker may gain access to authentication material belonging to identities that authenticate to it.

The compromise can therefore expand from:

```text
APP01
```

to:

```text
Other resources accessible
by those identities
```

---

# Delegation Trust Flag

Unconstrained delegation is represented through the:

```text
TRUSTED_FOR_DELEGATION
```

flag.

The corresponding `userAccountControl` bit is:

```text
0x00080000
```

or:

```text
524288
```

Microsoft documents this as:

```text
ADS_UF_TRUSTED_FOR_DELEGATION
```

This flag indicates that the account is trusted for Kerberos delegation.

---

# Important Distinction

Do not confuse:

```text
TRUSTED_FOR_DELEGATION
```

with:

```text
TRUSTED_TO_AUTH_FOR_DELEGATION
```

They represent different delegation configurations.

A useful model is:

```text
TRUSTED_FOR_DELEGATION
        |
        v
Unconstrained Delegation


TRUSTED_TO_AUTH_FOR_DELEGATION
        |
        v
Protocol Transition
within Constrained Delegation
```

The second flag will be covered in the constrained delegation notes.

---

# User and Computer Accounts

Delegation configuration exists on the account under which the service operates.

This may be:

```text
Computer Account
```

or:

```text
User / Service Account
```

Examples:

```text
WEB01$
APP01$
svc_web
svc_app
```

Therefore, enumeration should inspect both:

```text
Computers
```

and:

```text
Users
```

---

# Domain Controllers

Domain controllers are normally trusted for delegation because of their role in Active Directory.

Therefore:

```text
TRUSTED_FOR_DELEGATION
```

on a domain controller is not automatically a security finding.

When enumerating unconstrained delegation, separate:

```text
Domain Controllers
```

from:

```text
Non-DC Systems
```

The latter are generally the systems of greatest interest.

---

# Enumeration Strategy

A practical enumeration model is:

```text
Active Directory
       |
       v
Find TRUSTED_FOR_DELEGATION
       |
       v
Identify Accounts
       |
   +---+---+
   |       |
   v       v
Users   Computers
   |       |
   +---+---+
       |
       v
Exclude / Identify DCs
       |
       v
Determine Services
       |
       v
Determine Privilege
       |
       v
Identify Authentication Paths
```

---

# Windows - Active Directory PowerShell

The Active Directory PowerShell module can identify computer accounts trusted for delegation.

Example:

```powershell
Get-ADComputer \
    -Filter {TrustedForDelegation -eq $true} \
    -Properties TrustedForDelegation,DNSHostName,OperatingSystem |
    Select-Object \
        Name,
        DNSHostName,
        OperatingSystem,
        TrustedForDelegation
```

---

# Enumerate User Accounts

Service accounts configured for unconstrained delegation may also exist as user objects.

```powershell
Get-ADUser \
    -Filter {TrustedForDelegation -eq $true} \
    -Properties TrustedForDelegation,ServicePrincipalName |
    Select-Object \
        SamAccountName,
        TrustedForDelegation,
        ServicePrincipalName
```

---

# Enumerate Using userAccountControl

The raw UAC bit can also be queried.

```powershell
Get-ADComputer \
    -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=524288)' \
    -Properties userAccountControl,DNSHostName |
    Select-Object \
        Name,
        DNSHostName,
        userAccountControl
```

For users:

```powershell
Get-ADUser \
    -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=524288)' \
    -Properties userAccountControl,ServicePrincipalName |
    Select-Object \
        SamAccountName,
        userAccountControl,
        ServicePrincipalName
```

---

# LDAP Matching Rule

The LDAP matching rule:

```text
1.2.840.113556.1.4.803
```

performs a bitwise comparison.

The relevant filter is:

```text
(userAccountControl:1.2.840.113556.1.4.803:=524288)
```

Conceptually:

```text
userAccountControl
       |
       v
Contains 0x80000?
       |
   +---+---+
   |       |
  No      Yes
           |
           v
Trusted for Delegation
```

---

# ldapsearch

From Linux, LDAP can be used to search for delegation-enabled objects.

A general filter is:

```text
(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=524288))
```

Example:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=524288))' \
    sAMAccountName \
    dNSHostName \
    userAccountControl
```

For service accounts:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=524288))' \
    sAMAccountName \
    servicePrincipalName \
    userAccountControl
```

---

# PowerView

PowerView can be useful for Active Directory delegation enumeration.

A common conceptual workflow is:

```text
PowerView
    |
    v
Enumerate Domain Computers
    |
    v
Inspect userAccountControl
    |
    v
Find TRUSTED_FOR_DELEGATION
```

Depending on the PowerView version, delegation-specific switches or LDAP filters may be available.

When working with different PowerView forks or versions, verify:

```powershell
Get-Help Get-DomainComputer -Full
```

before relying on copied syntax.

A direct LDAP-filter approach is generally less ambiguous:

```powershell
Get-DomainComputer \
    -LDAPFilter '(userAccountControl:1.2.840.113556.1.4.803:=524288)' \
    -Properties samaccountname,dnshostname,useraccountcontrol
```

---

# SPN Analysis

After identifying a delegation-enabled account, determine which services run under it.

For a user/service account:

```powershell
Get-ADUser \
    -Identity '<SERVICE_ACCOUNT>' \
    -Properties ServicePrincipalName |
    Select-Object \
        SamAccountName,
        ServicePrincipalName
```

For a computer:

```powershell
Get-ADComputer \
    -Identity '<COMPUTER>' \
    -Properties ServicePrincipalName |
    Select-Object \
        Name,
        ServicePrincipalName
```

---

# setspn

Native Windows tooling can enumerate SPNs.

For a computer:

```powershell
setspn -L APP01
```

For a service account:

```powershell
setspn -L CORP\svc_app
```

This helps determine what Kerberos services are associated with the delegation-enabled identity.

---

# Linux - Impacket findDelegation

Impacket includes:

```text
findDelegation.py
```

commonly installed as:

```text
impacket-findDelegation
```

Check the installed syntax:

```bash
impacket-findDelegation -h
```

A typical domain enumeration pattern is:

```bash
impacket-findDelegation \
    'corp.example/alice:<PASSWORD>' \
    -dc-ip 10.10.10.10
```

The tool can help identify delegation relationships including:

```text
Unconstrained
Constrained
Resource-Based Constrained Delegation
```

depending on the environment and current Impacket version.

---

# Password Prompting

Where possible, avoid placing real passwords directly in shell history.

Prefer supported prompting mechanisms when available.

At minimum:

```text
Do not place production credentials
in documentation or Git repositories.
```

---

# Kerberos Authentication with Impacket

Where a valid Kerberos context already exists, review the tool's current options:

```bash
impacket-findDelegation -h
```

Many Impacket tools support combinations of:

```text
-k
-no-pass
-dc-ip
```

depending on the specific utility.

Always verify the installed version.

---

# NetExec

NetExec LDAP can assist with Active Directory enumeration.

Start by reviewing:

```bash
nxc ldap --help
```

and available modules:

```bash
nxc ldap -L
```

Delegation-related module names and options can change between releases, so avoid relying on old examples without checking the installed version.

The general workflow is:

```text
NetExec LDAP
      |
      v
Delegation Enumeration
      |
      v
Identify Trusted Systems
      |
      v
Correlate with Privilege
```

For detailed NetExec coverage:

[NetExec](netexec.md)

---

# BloodHound

BloodHound is particularly useful because delegation is not only a configuration issue.

The important question is:

```text
Who can compromise the delegation host?
```

and:

```text
Which high-value identities authenticate to it?
```

A BloodHound analysis model is:

```text
Unconstrained Delegation Host
          |
          +--> Who administers it?
          |
          +--> Who can compromise it?
          |
          +--> Who has sessions?
          |
          +--> Is it on a path to Tier 0?
          |
          +--> Does a privileged identity use it?
```

For detailed BloodHound coverage:

[BloodHound](bloodhound.md)

---

# BloodHound Risk Analysis

A delegation-enabled host becomes much more interesting when:

```text
Attacker-Controlled User
         |
         v
Can Compromise APP01
         |
         v
APP01 Has Unconstrained Delegation
         |
         v
Privileged User Authenticates to APP01
         |
         v
Potential Credential Exposure
```

The delegation configuration alone does not establish the complete attack path.

---

# Prioritising Delegation Hosts

Not every unconstrained delegation host presents equal risk.

Prioritise based on:

```text
Delegation Host
      |
      +--> Non-DC?
      |
      +--> Internet-facing?
      |
      +--> User-accessible?
      |
      +--> Weakly administered?
      |
      +--> High-value sessions?
      |
      +--> Tier 0 connectivity?
      |
      +--> Legacy software?
      |
      +--> Broad inbound access?
```

---

# Domain Controller vs Member Server

A useful triage model is:

```text
TRUSTED_FOR_DELEGATION
          |
      +---+---+
      |       |
      v       v
     DC    Member Server
      |       |
      v       v
 Expected   Investigate
 by role    carefully
```

This does not mean domain-controller delegation should be ignored.

It means the configuration has a different security context.

---

# Ticket Behaviour

When a user authenticates using Kerberos to a service trusted for unconstrained delegation, the Kerberos delegation design can provide the service with delegated authentication capability that allows it to act as the client toward other services.

The security implication is:

```text
User
 |
 v
Delegation Host
 |
 v
Delegated Authentication Context
 |
 v
Other Kerberos Services
```

This is why compromise of the delegation host is dangerous.

---

# Forwardable Tickets

Kerberos tickets can carry ticket flags such as:

```text
forwardable
forwarded
renewable
```

Microsoft's Event 4769 documentation describes the `Forwardable` ticket option as allowing the ticket-granting service to issue a new TGT based on the presented TGT.

Ticket flags are therefore useful context when investigating delegation behaviour.

---

# Sensitive Accounts

Some accounts should not be delegated.

Active Directory provides the:

```text
NOT_DELEGATED
```

account-control flag.

Its UAC bit is:

```text
0x00100000
```

or:

```text
1048576
```

Microsoft documents this as:

```text
ADS_UF_NOT_DELEGATED
```

---

# Account Is Sensitive and Cannot Be Delegated

In Active Directory Users and Computers, the defensive setting is commonly displayed as:

```text
Account is sensitive and cannot be delegated
```

Conceptually:

```text
Sensitive User
      |
      v
NOT_DELEGATED
      |
      v
Delegation Restricted
```

This is useful for suitable privileged identities.

---

# PowerShell - AccountNotDelegated

The Active Directory PowerShell module exposes:

```text
AccountNotDelegated
```

For example:

```powershell
Get-ADUser \
    -Identity '<USERNAME>' \
    -Properties AccountNotDelegated |
    Select-Object \
        SamAccountName,
        AccountNotDelegated
```

Microsoft also provides:

```powershell
Set-ADAccountControl \
    -Identity '<USERNAME>' \
    -AccountNotDelegated $true
```

for configuring this protection where appropriate.

Do not modify production accounts during an assessment unless explicitly authorised.

---

# Protected Users

Suitable privileged accounts can also be considered for membership in:

```text
Protected Users
```

after compatibility testing.

Protected Users introduces additional authentication protections and can help reduce credential exposure associated with legacy authentication and delegation scenarios.

It is not appropriate for every service or application identity.

---

# Delegation and Privileged Accounts

A dangerous configuration is:

```text
Privileged Admin
      |
      v
Authenticates to
Legacy Application Server
      |
      v
Unconstrained Delegation
```

A safer model is:

```text
Privileged Admin
      |
      v
Dedicated Administrative Host
      |
      v
Tier 0 Resource
```

while avoiding authentication to delegation-enabled lower-tier systems.

---

# Credential Exposure vs Delegation

Keep the stages distinct.

```text
Delegation Configuration
        |
        v
Authentication Material May
Become Available to Service
        |
        v
Host Compromise
        |
        v
Credential Exposure
        |
        v
Ticket Reuse
```

Unconstrained delegation itself does not mean:

```text
Attacker automatically owns
every authenticating account
```

The attacker generally needs control over the trusted service or system.

---

# Relationship to Pass-the-Ticket

If reusable Kerberos ticket material becomes available:

```text
Ticket
 |
 v
Pass-the-Ticket
 |
 v
Authentication
```

For detailed coverage:

[Pass-the-Ticket](pass-the-ticket.md)

---

# Relationship to Kerberos Tickets

Understanding:

```text
TGT
Service Ticket
Forwardable Ticket
Ticket Cache
```

is essential before analysing delegation.

See:

[Kerberos Tickets](kerberos-tickets.md)

---

# Relationship to Pass-the-Key

Unconstrained delegation is primarily concerned with delegated ticket-based authentication.

Pass-the-Key instead begins with:

```text
Kerberos Key
```

and obtains a new ticket.

See:

[Pass-the-Key](pass-the-key.md)

---

# Relationship to Constrained Delegation

Unconstrained delegation:

```text
Front-End
   |
   v
Broad Delegation
   |
   v
Other Services
```

Constrained delegation:

```text
Front-End
   |
   v
Explicit Allowed Services
   |
   +--> CIFS/server01
   |
   +--> HTTP/app01
```

Constrained delegation was introduced to reduce the broad trust inherent in unconstrained delegation.

---

# Relationship to RBCD

Resource-Based Constrained Delegation reverses where the delegation decision is configured.

Traditional constrained delegation:

```text
Front-End
     |
     v
Defines backend services
it may delegate to
```

RBCD:

```text
Back-End Resource
       |
       v
Defines which principals
may delegate to it
```

This difference becomes extremely important during ACL analysis.

---

# Relationship to S4U

Constrained delegation and RBCD frequently involve Kerberos Service-for-User extensions:

```text
S4U2Self
S4U2Proxy
```

Unconstrained delegation operates differently and should not be conflated with S4U-based delegation paths.

---

# Active Validation Strategy

Prefer:

```text
Enumeration
    |
    v
Configuration Confirmed
    |
    v
Privilege Analysis
    |
    v
Controlled Test Account
    |
    v
Authentication to Test Service
    |
    v
Observe Delegation Behaviour
```

over:

```text
Immediately target privileged
production authentication
```

---

# Minimum-Impact Validation

If the objective is simply to prove:

```text
APP01 is trusted for
unconstrained delegation
```

the following may already be sufficient:

```text
LDAP evidence
      +
PowerShell evidence
      +
BloodHound evidence
      +
Configuration screenshot
```

Active credential exposure may not be necessary.

---

# Controlled Validation

Where the engagement requires behavioural proof, use:

```text
Dedicated Test User
       |
       v
Controlled Authentication
       |
       v
Delegation-Enabled Test Host
       |
       v
Observe Kerberos Behaviour
       |
       v
Stop
```

Avoid using:

```text
Domain Admin
Enterprise Admin
Production Service Admin
```

unless the test specifically requires it and has explicit approval.

---

# Coercion

In offensive-security research, unconstrained delegation is sometimes combined with authentication-coercion techniques.

Conceptually:

```text
High-Value System
       |
       | Authentication induced
       v
Unconstrained Delegation Host
       |
       v
Delegated Authentication Material
       |
       v
Potential Impersonation
```

This creates a much higher-impact attack path.

Because coercion can affect production services and privileged systems, it should be treated as a separate active-testing phase requiring explicit scope approval.

The dedicated authentication-coercion notes should cover individual techniques.

---

# Do Not Assume Coercion Is Required

Unconstrained delegation risk can exist without coercion.

For example:

```text
Administrator
      |
      v
Legitimately accesses APP01
      |
      v
Delegation Host
```

If the host is already compromised, normal authentication may create the relevant exposure.

Coercion merely attempts to deliberately trigger authentication.

---

# Privileged Authentication Paths

During an assessment, ask:

```text
Who normally connects to this server?
```

Look for:

```text
Administrators
Backup Operators
Deployment Accounts
Monitoring Accounts
Domain Admins
Server Admins
Service Accounts
Domain Controllers
```

The answer can substantially change the severity.

---

# Service Exposure

Determine why users authenticate to the delegation-enabled host.

Examples:

```text
SMB
HTTP
MSSQL
WinRM
Custom Application
```

Map:

```text
SPN
 |
 v
Service
 |
 v
Who uses it?
 |
 v
Which identities authenticate?
```

---

# Network Reachability

Delegation risk should also consider:

```text
Who can reach the service?
```

A host reachable from:

```text
Entire User Network
```

may present a different risk from one reachable only from:

```text
Dedicated Management Network
```

---

# Host Privilege

Determine who can compromise or administer the delegation host.

Relevant relationships include:

```text
Local Administrators
Server Operators
Application Administrators
Deployment Accounts
Service Control Permissions
Remote Management Rights
Software Deployment Systems
```

---

# Attack Path Model

A complete attack path might look like:

```text
Low-Privilege User
        |
        v
Weak Application
        |
        v
APP01 Compromised
        |
        v
APP01 Trusted for
Unconstrained Delegation
        |
        v
Privileged User Authenticates
        |
        v
Delegated Kerberos Material
        |
        v
Privileged Authentication
        |
        v
Additional Systems
```

The vulnerability chain should be reported as a chain rather than treating each stage as isolated.

---

# Detection

Detection should cover both:

```text
Delegation Configuration
```

and:

```text
Delegation Abuse
```

A useful model is:

```text
Configuration Monitoring
        |
        +--> Which accounts are trusted?
        |
        +--> Was delegation recently enabled?
        |
        v
Authentication Monitoring
        |
        +--> Who authenticates?
        |
        +--> Which source?
        |
        +--> Which services?
        |
        v
Endpoint Monitoring
        |
        +--> Ticket access?
        |
        +--> Credential access?
        |
        +--> Suspicious processes?
```

---

# Event 4768

Event:

```text
4768
```

records Kerberos TGT requests.

This can help identify:

```text
Account
Client Address
Ticket Encryption Type
Pre-Authentication Type
```

depending on the Windows version and audit configuration.

---

# Event 4769

Event:

```text
4769
```

records Kerberos service-ticket requests on domain controllers.

Microsoft's newer event format can include useful information such as:

```text
Target User
Service Name
Client Address
Ticket Options
Ticket Encryption Type
Supported Encryption Types
```

This can help reconstruct delegation-related Kerberos activity.

---

# Event 4770

Event:

```text
4770
```

records Kerberos service-ticket renewal where the corresponding auditing is enabled.

It may provide additional context for long-running Kerberos sessions.

---

# Event 4624

Successful Windows logons may generate:

```text
4624
```

Correlate:

```text
Kerberos Ticket Activity
        |
        v
Target Authentication
        |
        v
4624
```

---

# Delegation Configuration Changes

Changes that enable delegation should be monitored as high-value Active Directory configuration changes.

Relevant attributes include:

```text
userAccountControl
msDS-AllowedToDelegateTo
msDS-AllowedToActOnBehalfOfOtherIdentity
```

For unconstrained delegation specifically, focus on changes introducing:

```text
TRUSTED_FOR_DELEGATION
```

---

# Event 5136

Where Directory Service Changes auditing is enabled, Active Directory object modifications can generate:

```text
5136
```

This can be useful for detecting changes to delegation-related attributes.

A monitoring model is:

```text
AD Object
   |
   v
userAccountControl Modified
   |
   v
5136
   |
   v
Did TRUSTED_FOR_DELEGATION change?
```

---

# Configuration Baseline

Maintain an inventory of all systems trusted for unconstrained delegation.

Example:

```text
Hostname    Type        Delegation
----------------------------------------
DC01        DC          Expected by role
DC02        DC          Expected by role
APP01       Member      Investigate
WEB01       Member      Investigate
```

Changes to this baseline should generate review.

---

# Detect New Delegation Hosts

A useful defensive workflow is:

```text
Daily / Scheduled AD Query
        |
        v
TRUSTED_FOR_DELEGATION
        |
        v
Compare to Baseline
        |
    +---+---+
    |       |
 Same      New
            |
            v
         Investigate
```

---

# Monitor Privileged Authentication

High-value users should not routinely authenticate to unconstrained delegation hosts.

Monitor:

```text
Privileged Account
       |
       v
Authentication
       |
       v
Delegation Host?
       |
    +--+--+
    |     |
   No    Yes
          |
          v
       Investigate
```

---

# Endpoint Detection

If a delegation-enabled server is compromised, defenders should monitor for:

```text
Credential-access activity
LSASS access
Kerberos ticket enumeration
Ticket export
Suspicious security tooling
Unusual child processes
Remote administration
```

The exact telemetry depends on the endpoint security platform.

---

# Network Detection

Kerberos traffic itself is legitimate.

Therefore:

```text
Kerberos Traffic
       |
       X
Proof of Delegation Abuse
```

Detection should combine:

```text
Kerberos events
       +
Host telemetry
       +
Identity context
       +
Delegation configuration
```

---

# Purple Team Exercise

A controlled exercise can validate whether defenders recognise the risk.

Example:

```text
Test User
    |
    v
APP-PT01
Unconstrained Delegation
    |
    v
Controlled Authentication
    |
    v
Kerberos Telemetry
    |
    v
Blue Team Investigation
```

---

# Purple Team Questions

The blue team should determine:

```text
Which host has unconstrained delegation?

Is the host a DC or member server?

Which account controls the service?

Which SPNs are registered?

Which user authenticated?

Was the user privileged?

Which Kerberos tickets were requested?

Was delegation configuration recently changed?

Can the host access Tier 0 resources?

Who can administer the delegation host?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to identify delegation host
Time to identify user
Time to identify service
Time to identify privileged authentication
Time to identify configuration
Time to containment decision
Correct attack-path reconstruction?
Correct remediation selected?
```

---

# Hardening

The primary recommendation is:

```text
Remove Unconstrained Delegation
where it is not strictly required
```

Microsoft recommends avoiding unconstrained delegation because it does not restrict which services can be accessed on behalf of the authenticated user.

---

# Migration Strategy

A safe migration model is:

```text
Inventory
   |
   v
Identify Unconstrained Delegation
   |
   v
Identify Application Dependency
   |
   v
Determine Required Backend Services
   |
   v
Choose Safer Delegation Model
   |
   +--> Constrained Delegation
   |
   +--> RBCD
   |
   v
Test
   |
   v
Deploy
   |
   v
Remove Unconstrained Delegation
```

Do not simply disable delegation on production applications without understanding their authentication requirements.

---

# Constrained Delegation

Where delegation is genuinely required, constrained delegation may reduce the trust scope.

Instead of:

```text
APP01
 |
 v
Any Kerberos Service
```

configure:

```text
APP01
 |
 +--> MSSQLSvc/SQL01
```

where operationally appropriate.

---

# Resource-Based Constrained Delegation

Modern architectures may also use RBCD.

```text
SQL01
 |
 v
Defines which front-end
principals may delegate to it
```

This can provide a clearer resource-side trust model.

RBCD still requires careful ACL management.

---

# Protect Sensitive Accounts

For suitable privileged accounts, consider:

```text
Account is sensitive and cannot be delegated
```

Conceptually:

```text
Privileged User
      |
      v
NOT_DELEGATED
      |
      v
Delegation Restricted
```

---

# Protected Users

Where compatible, Protected Users can provide additional safeguards for high-value identities.

Always evaluate:

```text
Legacy Applications
Service Dependencies
Authentication Requirements
```

before broad deployment.

---

# Administrative Tiering

Do not allow Tier 0 credentials onto lower-tier delegation hosts.

Bad:

```text
Domain Admin
     |
     v
Legacy APP01
     |
     v
Unconstrained Delegation
```

Better:

```text
Domain Admin
     |
     v
PAW
     |
     v
Tier 0
```

---

# Privileged Access Workstations

Use dedicated administrative systems for privileged access.

This reduces:

```text
Privileged Ticket
      |
      v
Exposure on Application Servers
```

---

# Least Privilege

Reduce who can administer delegation-enabled servers.

Review:

```text
Local Administrators
Remote Desktop Users
WinRM Rights
Service Control Rights
Deployment Rights
Application Administration
```

A delegation host should be treated as a sensitive credential boundary.

---

# Network Segmentation

Restrict access to delegation-enabled systems.

Example:

```text
User Network
     |
     X
Administrative Services
     |
     v
Delegation Server
```

Allow only required application traffic.

---

# Service Hardening

Because compromise of the delegation host is central to exploitation, harden the server itself.

Priorities include:

```text
Patch management
Application hardening
EDR
Least privilege
Service isolation
Restricted administration
Network segmentation
Secure configuration
```

---

# Monitor Delegation Changes

Alert on newly configured:

```text
TRUSTED_FOR_DELEGATION
```

for non-domain-controller systems.

This is particularly important because unconstrained delegation should be uncommon in modern environments.

---

# Incident Response

If an unconstrained delegation host is compromised:

```text
Compromised Delegation Host
          |
          v
Isolate Host
          |
          v
Identify Authenticated Users
          |
          v
Identify Privileged Sessions
          |
          v
Review Kerberos Activity
          |
          v
Determine Ticket Exposure
          |
          v
Investigate Ticket Reuse
          |
          v
Reset / Rotate Credentials
where required
          |
          v
Remove Unsafe Delegation
          |
          v
Rebuild / Remediate Host
```

---

# Assume Credential Exposure Carefully

Do not automatically claim:

```text
Every user who ever connected
is compromised
```

Instead determine:

```text
Which identities authenticated?
When?
Which authentication protocol?
Was delegation applicable?
Was reusable material exposed?
Was it accessed?
```

Evidence should drive the conclusion.

---

# Reporting

Possible finding titles include:

```text
Unconstrained Kerberos Delegation Enabled on Member Server
```

```text
Unconstrained Delegation Exposes Privileged Kerberos Authentication Material
```

```text
Legacy Kerberos Delegation Configuration Creates Credential Exposure Risk
```

```text
Compromised Delegation Host Could Enable Privileged User Impersonation
```

---

# Severity

Severity should consider:

```text
Delegation Host
      |
      +--> DC or Member Server?
      |
      +--> Compromisable?
      |
      +--> Internet-facing?
      |
      +--> High-value users connect?
      |
      +--> Tier 0 connectivity?
      |
      +--> Privileged service?
      |
      +--> Network exposure?
```

Example:

```text
Unconstrained Delegation
on isolated legacy member server
with no privileged authentication
```

may present a different risk from:

```text
Unconstrained Delegation
on widely accessible application server
regularly used by Domain Admins
```

---

# Do Not Report the Flag Alone

Avoid:

```text
TRUSTED_FOR_DELEGATION found
therefore Critical
```

Instead report:

```text
Configuration
      +
Host Exposure
      +
Privilege Relationships
      +
Authentication Paths
      +
Demonstrated Impact
```

---

# Example Finding

```text
Finding:
Unconstrained Kerberos Delegation Enabled on Member Server

Affected System:
APP01.corp.example

Affected Account:
APP01$

Description:
The affected member server is configured as trusted for unconstrained
Kerberos delegation.

This configuration allows the server to act on behalf of users that
authenticate to its Kerberos services without restricting delegation
to a predefined set of backend services.

Risk:
If the affected server is compromised, Kerberos authentication material
associated with users authenticating to the server may become exposed.

This is particularly significant if privileged users authenticate to
the affected system because their delegated authentication context may
provide access to additional systems within the domain.

Validation:
The TRUSTED_FOR_DELEGATION account-control flag was confirmed through
Active Directory enumeration.

BloodHound analysis identified the affected server as reachable by
administrative identities and demonstrated that compromise of the host
would create a credential-exposure path.

No production administrator authentication was deliberately induced
during testing.

Recommendation:
Determine whether Kerberos delegation is still operationally required.

Where delegation is necessary, migrate the application to constrained
delegation or resource-based constrained delegation where compatible.

Prevent privileged accounts from authenticating to the affected server,
apply the sensitive-and-cannot-be-delegated protection to appropriate
high-value accounts, restrict administrative access to the server, and
monitor changes to delegation-related Active Directory attributes.
```

---

# Evidence Collection

Record:

```text
Account
Object Type
Hostname
Distinguished Name
userAccountControl
TRUSTED_FOR_DELEGATION
SPNs
Operating System
Domain Controller?
Service Purpose
Network Exposure
Administrators
Privileged Sessions
BloodHound Relationships
Authentication Paths
Relevant Event IDs
Enumeration Tool
Command
Timestamp
```

---

# Evidence Example

```text
Account:
APP01$

Hostname:
APP01.corp.example

Object Type:
Computer

TRUSTED_FOR_DELEGATION:
True

userAccountControl:
[VALUE]

Domain Controller:
No

SPNs:
HOST/APP01
HOST/APP01.corp.example
[REDACTED AS REQUIRED]

Privilege Analysis:
[SUMMARY]

Validation:
Configuration only
```

---

# Credential Evidence

If controlled validation results in ticket material:

```text
TGT
.ccache
.kirbi
```

treat it as a credential.

Do not place it in:

```text
Git
Public screenshots
Issue trackers
Shared chat
Unencrypted evidence folders
```

---

# Cleanup

After controlled ticket testing:

```bash
unset KRB5CCNAME
```

Where appropriate:

```bash
kdestroy
```

Remove temporary ticket files according to evidence-retention requirements:

```bash
rm -f testuser.ccache
```

For dedicated Windows test sessions:

```powershell
klist purge
```

may be appropriate, but remember that it can disrupt authentication in the current session.

---

# Troubleshooting

## No Delegation Hosts Found

Possible explanations:

```text
Environment does not use
unconstrained delegation

LDAP query incorrect

Insufficient directory access

Wrong search base

Wrong domain

Only DCs match
```

Validate using more than one enumeration method where practical.

---

# Only Domain Controllers Found

This may be normal.

```text
TRUSTED_FOR_DELEGATION
        |
        v
Only DC accounts
```

means there may be no non-DC unconstrained delegation systems.

Document the result rather than forcing an attack path.

---

# PowerShell Filter Fails

Check whether the Active Directory module is available:

```powershell
Get-Module -ListAvailable ActiveDirectory
```

Then:

```powershell
Import-Module ActiveDirectory
```

If unavailable, use:

```text
LDAP
PowerView
Impacket
BloodHound
NetExec
```

as appropriate.

---

# LDAP Authentication Fails

Check:

```text
Username format
Password
Domain
LDAP vs LDAPS
Network access
DNS
Domain controller
```

---

# Impacket findDelegation Fails

Check:

```bash
impacket-findDelegation -h
```

Then validate:

```text
Credential format
Domain name
DNS
DC address
Kerberos vs NTLM mode
Clock synchronisation
```

---

# Delegation Exists but No Ticket Exposure Observed

Possible explanations include:

```text
No relevant user authenticated

Authentication used NTLM

Ticket not forwardable

Account protected from delegation

Protected Users restrictions

Application does not use expected
delegation path

Wrong logon/session context
```

Do not assume the configuration is broken without understanding the authentication flow.

---

# User Is Sensitive and Cannot Be Delegated

If:

```text
AccountNotDelegated = True
```

the user's authentication context is protected against delegation even when the service is trusted for delegation.

This is a defensive control, not a testing failure.

---

# Authentication Uses NTLM

Kerberos delegation requires Kerberos.

If:

```text
User
 |
 v
APP01
 |
 v
NTLM
```

the expected Kerberos delegation behaviour may not occur.

Verify the protocol rather than assuming.

---

# Kerberos Troubleshooting

Use:

```text
DNS
Time
SPN
Realm
Ticket
KDC
```

as the troubleshooting sequence.

On Windows:

```powershell
klist
```

On Linux:

```bash
klist
```

---

# Common Mistakes

## Mistake 1 - Calling Every Delegation Setting Unconstrained

Distinguish:

```text
Unconstrained
Constrained
RBCD
```

---

## Mistake 2 - Confusing Delegation Flags

```text
TRUSTED_FOR_DELEGATION
        =
Unconstrained


TRUSTED_TO_AUTH_FOR_DELEGATION
        =
Protocol transition capability
associated with constrained delegation
```

---

## Mistake 3 - Reporting Domain Controllers as Unexpected

Domain controllers have special Kerberos requirements.

Identify them separately.

---

## Mistake 4 - Assuming Delegation Means Immediate Compromise

The complete path normally requires:

```text
Delegation Host
       +
Host Compromise
       +
Interesting Authentication
```

---

## Mistake 5 - Ignoring Service Accounts

Unconstrained delegation can be configured on:

```text
Computer accounts
```

and:

```text
User/service accounts
```

Enumerate both.

---

## Mistake 6 - Ignoring SPNs

SPNs help identify what service the delegation-enabled account represents.

---

## Mistake 7 - Ignoring Privileged Authentication

The most important question is often:

```text
Who authenticates here?
```

---

## Mistake 8 - Automatically Coercing a Domain Controller

Authentication coercion can create substantial operational and security impact.

Do not perform it without explicit approval.

---

## Mistake 9 - Confusing Ticket Theft with Delegation

Delegation creates the authentication relationship.

Ticket theft is a subsequent credential-access activity.

---

## Mistake 10 - Confusing Pass-the-Ticket with Unconstrained Delegation

```text
Unconstrained Delegation
       |
       v
Potential Ticket Exposure


Pass-the-Ticket
       |
       v
Use of Ticket
```

---

## Mistake 11 - Assuming RC4 Is Required

Kerberos delegation is not fundamentally dependent on RC4.

Modern AES-based Kerberos environments can still have delegation risk.

---

## Mistake 12 - Ignoring `NOT_DELEGATED`

Sensitive accounts may have delegation protections that alter the attack path.

---

## Mistake 13 - Ignoring Protected Users

Protected identities can behave differently from ordinary accounts.

---

## Mistake 14 - Disabling Delegation Without Application Testing

Delegation may support legitimate multi-tier authentication.

Remediation must consider application dependencies.

---

# Assessment Checklist

## Preparation

- [ ] Confirm delegation testing is authorised
- [ ] Confirm permitted domains
- [ ] Confirm permitted accounts
- [ ] Confirm permitted systems
- [ ] Confirm whether active ticket testing is allowed
- [ ] Confirm whether authentication coercion is allowed
- [ ] Identify domain controllers
- [ ] Confirm DNS
- [ ] Confirm Kerberos connectivity

## Enumeration

- [ ] Query `TRUSTED_FOR_DELEGATION`
- [ ] Enumerate computer accounts
- [ ] Enumerate user/service accounts
- [ ] Identify domain controllers
- [ ] Identify non-DC delegation systems
- [ ] Record `userAccountControl`
- [ ] Enumerate SPNs
- [ ] Identify operating systems
- [ ] Identify service purpose

## Windows

- [ ] Query `TrustedForDelegation`
- [ ] Query UAC bit `524288`
- [ ] Enumerate service SPNs
- [ ] Review sensitive accounts
- [ ] Review `AccountNotDelegated`
- [ ] Review Protected Users where authorised

## Linux

- [ ] Query LDAP
- [ ] Run `impacket-findDelegation`
- [ ] Review NetExec LDAP capabilities
- [ ] Compare results between tools
- [ ] Validate DNS and time

## BloodHound

- [ ] Identify unconstrained delegation systems
- [ ] Identify who controls them
- [ ] Identify local administrators
- [ ] Identify active sessions where authorised
- [ ] Identify paths to high-value assets
- [ ] Identify Tier 0 relationships
- [ ] Identify privileged users likely to authenticate

## Risk Analysis

- [ ] Is the system a domain controller?
- [ ] Is the system externally exposed?
- [ ] Is the system reachable by users?
- [ ] Is the system easy to compromise?
- [ ] Do privileged users authenticate?
- [ ] Does it have Tier 0 connectivity?
- [ ] Can lower-privileged users administer it?
- [ ] Is delegation still operationally required?

## Validation

- [ ] Prefer configuration evidence first
- [ ] Use dedicated test identity
- [ ] Use dedicated test target
- [ ] Verify Kerberos is used
- [ ] Avoid production privileged credentials
- [ ] Avoid coercion unless explicitly approved
- [ ] Stop once impact is demonstrated
- [ ] Protect any resulting tickets

## Detection

- [ ] Review 4768
- [ ] Review 4769
- [ ] Review 4770 where relevant
- [ ] Review 4624
- [ ] Monitor delegation configuration changes
- [ ] Review 5136 where available
- [ ] Baseline delegation-enabled accounts
- [ ] Monitor privileged authentication to delegation hosts
- [ ] Correlate endpoint credential-access telemetry

## Remediation

- [ ] Determine whether delegation is required
- [ ] Remove unnecessary unconstrained delegation
- [ ] Migrate to constrained delegation where appropriate
- [ ] Consider RBCD where appropriate
- [ ] Protect sensitive accounts from delegation
- [ ] Consider Protected Users
- [ ] Implement administrative tiering
- [ ] Use PAWs
- [ ] Restrict administration of delegation hosts
- [ ] Segment delegation-enabled services
- [ ] Harden delegation hosts
- [ ] Monitor future delegation changes

## Cleanup

- [ ] Remove temporary ticket caches
- [ ] Remove `.kirbi` files
- [ ] Remove `.ccache` files
- [ ] Unset `KRB5CCNAME`
- [ ] Purge dedicated test-session tickets where appropriate
- [ ] Secure retained evidence
- [ ] Remove temporary test configuration
- [ ] Confirm no production configuration was changed

---

# Unconstrained Delegation Testing Model

The normal delegation model is:

```text
                           User
                            |
                            | Kerberos
                            v
                    Front-End Service
                            |
                            | Delegation
                            v
                     Back-End Service
```

The unconstrained model is:

```text
                           User
                            |
                            v
                Unconstrained Delegation Host
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
          Service A      Service B      Service C
```

The security problem is:

```text
                     Privileged Identity
                            |
                            v
                 Delegation-Enabled Host
                            |
                            v
                Delegated Authentication
                         Material
                            |
                            v
                     Host Compromise
                            |
                            v
                  Credential Exposure
                            |
                            v
                  Ticket Authentication
                            |
                            v
                   Additional Systems
```

The configuration model is:

```text
                     Active Directory Object
                              |
                              v
                       userAccountControl
                              |
                              v
                TRUSTED_FOR_DELEGATION
                              |
                              v
                           0x80000
                              |
                              v
                  Unconstrained Delegation
```

The privilege model is:

```text
              Unconstrained Delegation Host
                         |
          +--------------+--------------+
          |                             |
          v                             v
Who Can Compromise It?        Who Authenticates to It?
          |                             |
          v                             v
Low-Privilege Path?            Privileged Identity?
          |                             |
          +--------------+--------------+
                         |
                         v
                    Attack Path
```

The attack-chain model is:

```text
Low-Privilege Access
        |
        v
Delegation Host Compromised
        |
        v
Wait for / Receive
Kerberos Authentication
        |
        v
Delegated Credential Material
        |
        v
Credential Reuse
        |
        v
Privilege Expansion
```

The safer delegation model is:

```text
Unconstrained Delegation
          |
          v
       Migrate
          |
     +----+----+
     |         |
     v         v
Constrained   RBCD
Delegation
     |         |
     +----+----+
          |
          v
Explicit Delegation Scope
```

The defensive model is:

```text
Unconstrained Delegation
          |
          +--> Remove where unnecessary
          |
          +--> Restrict delegation scope
          |
          +--> Protect privileged accounts
          |       |
          |       +--> NOT_DELEGATED
          |       +--> Protected Users
          |       +--> PAWs
          |
          +--> Protect delegation hosts
          |       |
          |       +--> Patching
          |       +--> EDR
          |       +--> Least Privilege
          |       +--> Segmentation
          |
          +--> Monitor
                  |
                  +--> Delegation Configuration
                  +--> 4768
                  +--> 4769
                  +--> 4624
                  +--> 5136
                  +--> Privileged Authentication
```

The assessment should answer:

```text
Which accounts are trusted for
unconstrained delegation?
        |
        v
Which are domain controllers?
        |
        v
Which are non-DC systems?
        |
        v
What services run on them?
        |
        v
Who can compromise or administer them?
        |
        v
Which identities authenticate to them?
        |
        v
Do privileged identities authenticate?
        |
        v
Are those identities protected
from delegation?
        |
        v
Can the configuration be replaced
with a safer delegation model?
        |
        v
Can defenders identify both the
configuration and abuse path?
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos tickets:

[Kerberos Tickets](kerberos-tickets.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

OverPass-the-Hash:

[OverPass-the-Hash](overpass-the-hash.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The following topics complement unconstrained delegation and can be linked once their dedicated notes are available:

```text
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/s4u.md
active-directory/authentication-coercion.md
active-directory/golden-ticket.md
active-directory/silver-ticket.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft Kerberos Delegation

[Microsoft - Kerberos authentication troubleshooting guidance](https://learn.microsoft.com/en-us/troubleshoot/windows-server/windows-security/kerberos-authentication-troubleshooting-guidance){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Kerberos Protocol Extensions](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-kile/){ target="_blank" rel="noopener noreferrer" }

---

## Active Directory Account Control

[Microsoft - userAccountControl Bits](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/dd302fd1-0aa7-406b-ad91-2a6b35738557){ target="_blank" rel="noopener noreferrer" }

[Microsoft - ADS_USER_FLAG_ENUM](https://learn.microsoft.com/en-us/windows/win32/api/iads/ne-iads-ads_user_flag_enum){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Set-ADAccountControl](https://learn.microsoft.com/en-us/powershell/module/activedirectory/set-adaccountcontrol){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Kerberos Auditing

[Microsoft - Advanced Audit Policy Configuration](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/advanced-audit-policy-configuration){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4769](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4769){ target="_blank" rel="noopener noreferrer" }

---

## Credential Protection

[Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Pass the Ticket](https://attack.mitre.org/techniques/T1550/003/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket findDelegation](https://github.com/fortra/impacket/blob/master/examples/findDelegation.py){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Unconstrained delegation is a legacy Kerberos delegation model that grants a service broad ability to act on behalf of authenticated users.

The fundamental architecture is:

```text
User
 |
 v
Delegation-Enabled Service
 |
 v
Other Kerberos Services
```

The Active Directory configuration is associated with:

```text
TRUSTED_FOR_DELEGATION
        |
        v
userAccountControl
        |
        v
0x00080000
```

The security risk becomes significant when:

```text
Unconstrained Delegation
        +
Compromised Host
        +
Privileged Authentication
        |
        v
Potential Credential Exposure
        |
        v
User Impersonation
```

The most important distinction is:

```text
Unconstrained Delegation
        =
Broad service delegation


Constrained Delegation
        =
Explicit destination services


RBCD
        =
Resource controls which
principals may delegate to it
```

Do not treat every system with the delegation flag as equally vulnerable.

A mature assessment should determine:

```text
Which systems are trusted?
        |
        v
Which are non-DC systems?
        |
        v
Why is delegation required?
        |
        v
Which services use it?
        |
        v
Who can compromise the host?
        |
        v
Which users authenticate?
        |
        v
Are privileged users exposed?
        |
        v
Can a safer delegation model replace it?
```

From a defensive perspective, the preferred strategy is:

```text
Remove Unconstrained Delegation
             |
             v
Use Explicit Delegation
Where Required
             |
             +
Protect Privileged Accounts
             |
             +
Protect Delegation Hosts
             |
             +
Monitor Delegation Changes
             |
             +
Monitor Privileged Authentication
```

Unconstrained delegation should therefore be assessed as part of a broader identity and attack-path model rather than as an isolated Active Directory flag. The meaningful risk comes from the combination of the delegation configuration, compromise potential of the trusted system, identities that authenticate to it, privileges associated with those identities, and the controls available to prevent or detect subsequent credential reuse.
