# Active Directory Trust Tickets

Active Directory uses Kerberos trust relationships to allow authentication to cross domain boundaries.

When a user in one domain needs to access a service in another domain, the user's Key Distribution Center (KDC) does not normally issue the final service ticket directly.

Instead, Kerberos uses a referral process.

Conceptually:

```text
User
 |
 v
Source Domain KDC
 |
 v
Referral TGT
 |
 v
Target Domain KDC
 |
 v
Service Ticket
 |
 v
Target Service
```

These cross-domain Kerberos tickets are commonly referred to during offensive security discussions as:

```text
Inter-Realm Tickets
Referral Tickets
Trust Tickets
```

The underlying mechanism is legitimate Kerberos functionality.

From a security perspective, trust tickets become particularly important when an attacker obtains cryptographic material associated with an Active Directory trust.

Compromise of trust-related secrets can potentially allow forged cross-domain authentication material to be created.

!!! warning "Authorised testing only"
    Trust-ticket testing can affect multiple Active Directory domains or forests. A trust relationship does not automatically place the remote domain or forest within scope. Do not extract trust secrets, forge tickets or authenticate to another security boundary unless this activity is explicitly authorised.

---

# Trust Tickets at a Glance

Normal authentication inside one domain:

```text
User
 |
 v
AS-REQ
 |
 v
KDC
 |
 v
TGT
 |
 v
TGS-REQ
 |
 v
Service Ticket
 |
 v
Service
```

Cross-domain authentication introduces a referral:

```text
User
 |
 v
Source KDC
 |
 v
Source TGT
 |
 v
Referral Request
 |
 v
Inter-Domain Referral TGT
 |
 v
Target KDC
 |
 v
Target Service Ticket
 |
 v
Target Service
```

The trust allows the target domain to validate authentication information originating through the source domain.

---

# Prerequisites

Understanding trust tickets requires familiarity with:

```text
Kerberos
TGTs
Service Tickets
KDCs
SPNs
Domains
Forests
Trust Relationships
```

See:

[Kerberos](kerberos.md)

[Kerberos Tickets](kerberos-tickets.md)

[Domain and Forest Trusts](trusts.md)

[Trust Relationships](trust-relationships.md)

---

# Kerberos Components

The main components are:

```text
Client
KDC
Authentication Service
Ticket Granting Service
Service Principal
```

The KDC normally runs on a domain controller.

---

# Ticket Granting Ticket

A user initially obtains a:

```text
Ticket Granting Ticket
```

or:

```text
TGT
```

The TGT allows the user to request tickets for services without repeatedly supplying credentials.

---

# Service Ticket

When accessing a service such as:

```text
CIFS
HTTP
LDAP
MSSQLSvc
HOST
```

the client requests a:

```text
Service Ticket
```

from the KDC.

---

# Single-Domain Kerberos

Suppose:

```text
alice@CORP.EXAMPLE
```

wants to access:

```text
cifs/files01.corp.example
```

The simplified process is:

```text
Alice
 |
 v
CORP KDC
 |
 v
TGT
 |
 v
CORP KDC
 |
 v
CIFS Service Ticket
 |
 v
FILE01
```

The KDC responsible for Alice is also capable of issuing the required ticket for the service in the same domain.

---

# Cross-Domain Kerberos

Now suppose:

```text
alice@EMEA.CORP.EXAMPLE
```

wants to access:

```text
cifs/files01.corp.example
```

The source KDC belongs to:

```text
EMEA.CORP.EXAMPLE
```

while the service belongs to:

```text
CORP.EXAMPLE
```

The source KDC therefore provides a referral toward the destination domain.

---

# Referral Model

```text
Alice
 |
 v
EMEA.CORP.EXAMPLE KDC
 |
 v
Referral TGT
 |
 v
CORP.EXAMPLE KDC
 |
 v
CIFS/files01.corp.example
 |
 v
Service Ticket
 |
 v
FILE01
```

This allows Kerberos authentication to traverse the trust relationship.

---

# Inter-Realm TGT

A referral ticket is effectively an inter-realm Ticket Granting Ticket.

It identifies another Kerberos realm as the next destination.

Example conceptual service principal:

```text
krbtgt/CORP.EXAMPLE
```

when moving from:

```text
EMEA.CORP.EXAMPLE
```

toward:

```text
CORP.EXAMPLE
```

---

# Trust Account Concept

Active Directory maintains secret material associated with domain trust relationships.

This cryptographic material allows the participating domains to validate trust-related Kerberos information.

Conceptually:

```text
Domain A
   |
   | Shared Trust Relationship
   |
   v
Domain B
```

The trust relationship has associated secret material known to the relevant domain controllers.

---

# Trust Password

Trust relationships use automatically managed passwords.

These secrets are not intended to be manually used by administrators during normal operations.

Windows manages trust password changes as part of the relationship.

---

# Trust Secret

From an offensive security perspective, trust-related cryptographic material may sometimes be described as:

```text
Trust Key
Trust Secret
Trust Password Hash
Inter-Realm Key
```

The exact terminology depends on the tool and context.

---

# Trust Secret Security

Trust secrets should be considered highly sensitive.

Conceptually:

```text
Trust Secret
     |
     v
Validate Inter-Realm Authentication
     |
     v
Cross-Domain Security
```

Compromise can therefore affect more than one domain.

---

# Trust Direction and Tickets

Trust direction remains important.

Suppose:

```text
DOMAIN-A trusts DOMAIN-B
```

The potential access direction is:

```text
DOMAIN-B User
      |
      v
DOMAIN-A Resource
```

Kerberos referral behaviour must be interpreted together with:

```text
Trust Direction
Trust Type
Transitivity
Authentication Scope
```

---

# Trust Ticket Flow

A simplified cross-domain flow is:

```text
User in Domain A
       |
       v
Domain A KDC
       |
       v
TGT for Domain A
       |
       v
Request Service in Domain B
       |
       v
Domain A KDC
       |
       v
Referral TGT for Domain B
       |
       v
Domain B KDC
       |
       v
Service Ticket
       |
       v
Domain B Service
```

---

# Kerberos Referral Discovery

The client does not necessarily need to know the entire trust path in advance.

Kerberos referrals can direct the client toward the appropriate realm.

In complex forests:

```text
Domain A
   |
   v
Domain B
   |
   v
Domain C
```

the client may receive multiple referrals before reaching the domain responsible for the target service.

---

# Parent-Child Referral

Example:

```text
corp.example
      |
      v
emea.corp.example
```

A user in:

```text
emea.corp.example
```

accessing a service in:

```text
corp.example
```

can use the automatically established parent-child trust.

---

# Forest Referral

Inside a forest:

```text
Domain A
    |
    v
Forest Trust Topology
    |
    v
Domain B
```

Kerberos can navigate the domain hierarchy using referrals.

---

# Cross-Forest Referral

For separate forests:

```text
Forest A
   |
   | Forest Trust
   |
   v
Forest B
```

Kerberos referrals can cross the forest trust when:

```text
Trust Direction Allows It
Authentication Requirements Are Met
Name Resolution Works
Network Connectivity Exists
```

---

# DNS Requirements

Kerberos referrals depend heavily on DNS.

The client must be able to locate:

```text
Domain Controllers
KDCs
Services
```

in the appropriate domains.

---

# Kerberos SRV Records

Useful DNS records include:

```text
_kerberos._tcp.DOMAIN
```

and:

```text
_ldap._tcp.dc._msdcs.DOMAIN
```

Example:

```bash
dig _kerberos._tcp.corp.example SRV
```

Windows:

```powershell
Resolve-DnsName -Type SRV '_kerberos._tcp.corp.example'
```

Only query remote domains when they are within scope.

---

# Inspect Current Kerberos Tickets

Windows:

```cmd
klist
```

This displays tickets in the current logon session.

---

# Purging Tickets

Windows also supports:

```cmd
klist purge
```

However, this changes the current Kerberos session state.

Do not purge tickets on production systems merely for enumeration.

Use a dedicated test session if ticket lifecycle testing is required.

---

# Linux Ticket Cache

On Linux:

```bash
klist
```

The current cache location may be shown through:

```bash
echo "$KRB5CCNAME"
```

---

# Referral Tickets in the Cache

After accessing a cross-domain service, the ticket cache may contain entries conceptually resembling:

```text
krbtgt/CORP.EXAMPLE@EMEA.CORP.EXAMPLE
```

along with the final service ticket.

Exact ticket presentation varies by platform and tooling.

---

# Kerberos Ticket Analysis

Important fields include:

```text
Client
Server
Realm
Start Time
End Time
Renew Time
Encryption Type
Ticket Flags
```

These help establish:

```text
Who Authenticated?
To Which Realm?
For Which Service?
When?
```

---

# Windows Ticket Inspection

Basic:

```cmd
klist
```

Specific sessions can also be inspected by administrators using appropriate `klist` functionality.

Avoid interacting with unrelated user sessions during routine assessment.

---

# Linux Ticket Inspection

```bash
klist -e
```

can display encryption information where supported.

Example output may include:

```text
AES-256
AES-128
RC4
```

depending on environment and ticket.

---

# Trust Enumeration Before Ticket Analysis

Always understand the trust first.

PowerShell:

```powershell
Get-ADTrust -Filter * |
    Select-Object Name,Source,Target,Direction,TrustType,ForestTransitive,IntraForest,SelectiveAuthentication
```

Native Windows:

```cmd
nltest /domain_trusts /all_trusts
```

---

# Identify Domain SIDs

```powershell
Get-ADDomain | Select-Object DNSRoot,DomainSID
```

If the trusted domain is in scope and querying it is authorised:

```powershell
Get-ADDomain -Identity 'partner.example' |
    Select-Object DNSRoot,DomainSID
```

---

# Why Domain SIDs Matter

Kerberos authorisation information ultimately interacts with Windows SIDs.

Trust-ticket analysis therefore often intersects with:

```text
Domain SID
Group SID
SIDHistory
SID Filtering
```

See:

[SID History](sid-history.md)

---

# SID Filtering

SID filtering protects trust boundaries by controlling which SID information is accepted across the trust.

Conceptually:

```text
Kerberos Authentication Data
          |
          v
Trust Boundary
          |
          v
SID Filtering
          |
          +--> Permitted SID Information
          |
          X
          |
          +--> Filtered SID Information
```

---

# Trust Ticket Does Not Bypass Authorisation

A valid cross-domain ticket does not automatically provide administrative access.

The complete model remains:

```text
Valid Ticket
    |
    v
Authentication
    |
    v
Security Token
    |
    v
ACL / Group Membership
    |
    v
Authorisation
```

---

# Privilege Still Matters

A normal user from a trusted domain may authenticate successfully but have:

```text
No Access
```

to a particular resource.

The trust provides:

```text
Authentication Relationship
```

not:

```text
Automatic Privilege
```

---

# Selective Authentication

Selective authentication can further restrict where trusted-domain identities are permitted to authenticate.

Conceptually:

```text
Foreign Identity
      |
      v
Kerberos Trust
      |
      v
Allowed to Authenticate?
      |
      +--> No --> Stop
      |
      +--> Yes
             |
             v
      Resource Authorisation
```

---

# Forest-Wide Authentication

A forest trust may instead allow broader authentication.

This does not eliminate resource ACL checks, but it increases the number of systems to which trusted identities may potentially authenticate.

---

# Trust Ticket Abuse

The offensive security significance of trust tickets arises when an attacker obtains cryptographic material used by the trust.

The conceptual chain is:

```text
High Privilege in Domain
       |
       v
Trust Secret Compromised
       |
       v
Inter-Realm Ticket Material
       |
       v
Cross-Domain Authentication Attempt
```

This is fundamentally different from simply requesting a legitimate referral ticket as a normal user.

---

# Legitimate Referral vs Forged Trust Ticket

Legitimate:

```text
Normal User
   |
   v
Source KDC
   |
   v
Legitimate Referral
   |
   v
Target KDC
```

Forged:

```text
Compromised Trust Secret
        |
        v
Offline Ticket Construction
        |
        v
Target Trust Boundary
```

The second scenario represents a major security incident.

---

# Trust Ticket vs Golden Ticket

A Golden Ticket normally involves compromise of:

```text
krbtgt
```

key material for a domain.

Conceptually:

```text
krbtgt Key
    |
    v
Forge Domain TGT
    |
    v
Domain Persistence / Authentication
```

A trust-ticket scenario instead concerns:

```text
Trust Key
    |
    v
Inter-Realm Authentication
    |
    v
Trusted Domain
```

---

# Comparison

| Technique | Key Material | Primary Scope |
|---|---|---|
| Golden Ticket | Domain `krbtgt` key | Domain Kerberos authentication |
| Trust Ticket | Trust relationship key | Cross-domain trust authentication |
| Silver Ticket | Service account key | Specific service |
| Pass-the-Ticket | Existing ticket | Rights represented by captured ticket |

---

# Trust Ticket vs Pass-the-Ticket

Pass-the-Ticket uses:

```text
Existing Kerberos Ticket
```

whereas trust-ticket forgery involves constructing authentication material using compromised trust cryptographic material.

See:

[Pass-the-Ticket](pass-the-ticket.md)

---

# Trust Ticket vs Golden Certificate

Golden Certificate abuse involves:

```text
CA Private Key
```

and certificate-based authentication.

Trust tickets involve:

```text
Kerberos Trust Cryptographic Material
```

These compromise different parts of the identity infrastructure.

See:

[Golden Certificate](ad-cs/golden-certificate.md)

---

# Trust Ticket Security Boundary

Trust-ticket abuse can cross:

```text
Domain Boundaries
```

and potentially:

```text
Forest Boundaries
```

depending on the trust.

Therefore the first question before testing is:

```text
Is the Destination Security Boundary Explicitly In Scope?
```

---

# Trust Secret Exposure

Trust secrets normally require significant privilege to obtain.

Their exposure should therefore be treated as evidence of substantial compromise in the source environment.

Possible sources of exposure can include:

```text
Domain Controller Compromise
Directory Database Compromise
Credential Dumping
Highly Privileged Replication Access
Backup Exposure
```

---

# NTDS Context

Trust-related secrets may exist within the broader Active Directory credential material protected by domain controllers.

See:

[NTDS](ntds.md)

Access to this material should already be considered a critical security event.

---

# DCSync Context

An identity capable of replicating sensitive directory secrets may have highly privileged control.

Trust-secret extraction through replication should therefore not be treated as a low-impact enumeration technique.

---

# Trust Ticket Testing Philosophy

For normal penetration testing:

```text
Trust Found
    |
    v
Enumerate Direction
    |
    v
Identify Foreign Permissions
    |
    v
Validate Legitimate Authentication
```

is usually sufficient.

You generally do not need:

```text
Trust Secret Extraction
      |
      v
Ticket Forgery
```

to demonstrate that an excessive trust relationship creates risk.

---

# When Forgery Testing May Be Appropriate

Trust-ticket forgery may be appropriate in:

```text
Dedicated AD Lab
Red-Team Exercise
Adversary Simulation
Explicit Trust Compromise Scenario
```

where:

```text
Both Security Boundaries Are In Scope
```

and destructive or persistence-related restrictions are understood.

---

# Lab Architecture

A safe laboratory might contain:

```text
FORESTA.LOCAL
      |
      | Two-Way Forest Trust
      |
      v
FORESTB.LOCAL
```

with:

```text
DC-A
DC-B
CLIENT-A
SERVER-B
```

All systems should be disposable and controlled.

---

# Lab Testing Stages

A structured laboratory workflow is:

```text
Enumerate Trust
      |
      v
Observe Legitimate Referral
      |
      v
Inspect Ticket Cache
      |
      v
Study Trust Cryptography
      |
      v
Perform Controlled Forgery
      |
      v
Observe Target Logs
      |
      v
Destroy Lab State
```

The production assessment normally stops much earlier.

---

# Impacket Kerberos Tooling

Impacket provides several Kerberos-related utilities useful for authorised laboratories and troubleshooting.

See:

[Impacket](impacket.md)

Available commands depend on the installed version.

Always verify:

```bash
impacket-ticketConverter -h
```

or the relevant tool's help output before relying on remembered syntax.

---

# Ticket Cache Interoperability

Kerberos tickets may appear in formats such as:

```text
ccache
kirbi
```

Tooling exists to convert between formats.

This is useful for:

```text
Lab Analysis
Ticket Inspection
Interoperability
```

but does not itself create privilege.

---

# Rubeus Context

Rubeus is commonly encountered in Windows Kerberos research and red-team environments.

It can inspect and interact with Kerberos tickets.

Because functionality and command-line options vary across releases and forks, verify syntax against the specific version being used.

Do not execute ticket manipulation against production identity infrastructure without explicit authorisation.

---

# Mimikatz Context

Mimikatz historically demonstrated many Kerberos ticket and trust techniques.

It is useful for understanding:

```text
Kerberos Internals
Ticket Structure
Trust Authentication
```

but credential extraction and ticket-forgery functionality is highly intrusive.

Use such functionality only in explicitly authorised environments.

---

# Cross-Domain Access Validation

A safer production validation is to use legitimate credentials.

Example conceptual workflow:

```text
Approved User in Domain A
       |
       v
Authenticate Normally
       |
       v
Access Approved Resource in Domain B
       |
       v
Observe Referral Tickets
       |
       v
Stop
```

This proves the trust path without manipulating trust secrets.

---

# SMB Validation

If an approved foreign user has access to a test share:

```text
Domain A User
      |
      v
Kerberos Referral
      |
      v
Domain B CIFS Ticket
      |
      v
Approved Share
```

See:

[SMB](smb.md)

---

# WinRM Validation

Where remote management is explicitly part of the test:

```text
Foreign User
     |
     v
Kerberos Referral
     |
     v
HTTP Service Ticket
     |
     v
WinRM
```

See:

[WinRM](winrm.md)

---

# LDAP Validation

Read-only LDAP is often sufficient to demonstrate cross-domain authentication.

Conceptually:

```text
Foreign User
     |
     v
Kerberos
     |
     v
LDAP
     |
     v
Read Approved Directory Data
```

---

# SPNs Across Trusts

Kerberos relies on Service Principal Names.

Examples include:

```text
cifs/files01.partner.example
HTTP/web01.partner.example
ldap/dc01.partner.example
MSSQLSvc/sql01.partner.example
```

Correct:

```text
DNS
SPN
Realm
```

information is essential.

---

# Hostname vs IP Address

Kerberos normally depends on service names.

Using:

```text
Hostname
```

is therefore preferable to using:

```text
IP Address
```

for Kerberos validation.

Using an IP address can cause Kerberos to fail or another authentication mechanism to be attempted depending on the client and application.

---

# Time Synchronisation

Kerberos is time sensitive.

Cross-domain authentication therefore depends on acceptable clock synchronisation.

Windows:

```cmd
w32tm /query /status
```

Linux:

```bash
timedatectl
```

---

# Cross-Forest DNS

Separate forests may use:

```text
Conditional Forwarders
Stub Zones
Delegations
DNS Forwarding
```

to allow domain discovery.

A broken trust may actually be:

```text
DNS Failure
```

rather than:

```text
Kerberos Failure
```

---

# Troubleshooting Model

```text
Cross-Domain Authentication Fails
            |
            v
          DNS?
            |
            v
      KDC Reachable?
            |
            v
      Correct Hostname?
            |
            v
       Correct SPN?
            |
            v
      Clock Correct?
            |
            v
    Trust Direction?
            |
            v
      Trust Healthy?
            |
            v
Selective Authentication?
            |
            v
     Authorisation?
```

---

# Verify Trust Health

Administrators can use native tooling to investigate trust relationships.

Example:

```cmd
nltest /domain_trusts
```

Domain controller discovery:

```cmd
nltest /dsgetdc:partner.example
```

Avoid repair or reset operations during assessment.

---

# Do Not Reset Trusts

Native administrative tools can modify or reset trust relationships.

Do not perform operations such as:

```text
Trust Reset
Trust Password Reset
Trust Recreation
```

during normal penetration testing.

These can disrupt authentication between domains.

---

# Do Not Change Trust Direction

Changing:

```text
One-Way
```

to:

```text
Two-Way
```

or otherwise modifying trust direction is a production configuration change.

It is not required to validate trust security.

---

# Do Not Disable SID Filtering

SID filtering is a defensive control.

Do not weaken it to demonstrate a theoretical attack.

The correct assessment is:

```text
Observe Configuration
      |
      v
Determine Exposure
      |
      v
Report
```

---

# Trust Ticket Detection

Defenders should monitor both:

```text
Normal Cross-Domain Kerberos
```

and:

```text
Abnormal Trust-Related Authentication
```

The challenge is that legitimate trust authentication is common in some environments.

---

# Kerberos Event 4768

Event:

```text
4768
```

records Kerberos Authentication Service activity for TGT requests on domain controllers.

It can help establish:

```text
Account
Client Address
Encryption Type
Pre-Authentication
```

context.

---

# Kerberos Event 4769

Event:

```text
4769
```

records Kerberos service-ticket requests on domain controllers.

This is particularly useful for analysing:

```text
Service
Account
Client Address
Ticket Encryption
```

---

# Cross-Domain Kerberos Visibility

Monitoring should understand expected relationships such as:

```text
Domain A Users
      |
      v
Specific Services in Domain B
```

Unexpected relationships are more useful than raw ticket volume.

---

# Authentication Baseline

Example expected pattern:

```text
PARTNER\AppUsers
       |
       v
CORP\APP01
```

Unexpected:

```text
PARTNER\AppUsers
       |
       v
CORP\Domain Controller
```

The second deserves significantly more attention.

---

# Event 4624

Successful logons can produce:

```text
4624
```

on the target system.

Correlate:

```text
Account Domain
Account Name
Source Address
Logon Type
Authentication Package
Target Host
```

---

# Event 4625

Failed logons:

```text
4625
```

can reveal repeated or unexpected cross-domain authentication attempts.

---

# Event 4672

Event:

```text
4672
```

indicates special privileges assigned to a new logon.

Cross-domain identities receiving privileged logons should be reviewed carefully.

---

# Trust Changes

Trust-related administrative events include:

```text
4706
4707
4716
```

These cover trust creation, removal and modification.

See:

[Trust Relationships](trust-relationships.md)

---

# Directory Changes

Where appropriate auditing is enabled:

```text
5136
```

may provide additional visibility into Active Directory object modifications.

---

# Detecting Forged Tickets

Forged-ticket detection is difficult because:

```text
Cryptographically Valid
```

does not necessarily mean:

```text
Legitimately Issued
```

Detection therefore benefits from correlation.

---

# Correlation Model

```text
Kerberos Ticket Activity
        |
        v
Expected Account?
        |
        v
Expected Source?
        |
        v
Expected Domain?
        |
        v
Expected Service?
        |
        v
Expected Privilege?
        |
        v
Expected Trust Path?
```

---

# KDC vs Resource Correlation

Where telemetry permits, compare:

```text
KDC Events
```

with:

```text
Target Logon Events
```

and:

```text
Endpoint Process Activity
```

Unexpected inconsistencies can warrant investigation.

---

# Privileged Cross-Domain Authentication

High-value alerts include:

```text
Foreign User -> Domain Controller
Foreign User -> AD CS Server
Foreign User -> ADFS
Foreign User -> Privileged Management Host
Foreign User -> Backup Infrastructure
```

unless explicitly expected.

---

# Encryption Types

Kerberos encryption types may provide useful context.

Modern environments should generally prefer strong supported encryption such as:

```text
AES
```

Legacy environments may still expose:

```text
RC4
```

dependencies.

Do not infer compromise solely from RC4 use, but investigate why it remains necessary.

---

# Trust Encryption Compatibility

Some trust configurations and legacy environments can influence which encryption types are available.

Review:

```text
Domain Functional Level
Trust Configuration
Account Encryption Support
Legacy Dependencies
```

before making remediation recommendations.

---

# Trust Ticket Hardening

A strong trust-security model includes:

```text
Minimum Trusts
Minimum Trust Direction
Selective Authentication
SID Filtering
Strong Kerberos Configuration
Separate Privileged Accounts
Network Segmentation
Tier 0 Isolation
Trust Monitoring
Rapid Secret Rotation After Compromise
```

---

# Minimise Trust Relationships

Every trust creates an additional authentication relationship.

Maintain only trusts with:

```text
Documented Business Purpose
Owner
Required Direction
Required Scope
Review Date
```

---

# Prefer One-Way Trusts

Where only one direction is required:

```text
One-Way
```

may reduce exposure compared with:

```text
Two-Way
```

depending on the architecture.

---

# Use Selective Authentication

For high-risk forest relationships:

```text
Selective Authentication
```

can reduce the systems to which foreign identities may authenticate.

---

# Maintain SID Filtering

SID filtering should remain appropriately configured across trust boundaries.

See:

[SID History](sid-history.md)

---

# Separate Privileged Accounts

Avoid using one privileged identity across multiple forest security boundaries.

Prefer:

```text
Forest A Admin
Forest B Admin
```

rather than:

```text
Shared Cross-Forest Admin
```

---

# Protect Domain Controllers

Trust secrets are protected by the domain's identity infrastructure.

Domain controllers should therefore receive:

```text
Tier 0 Protection
Dedicated Administration
Credential Isolation
Network Restrictions
EDR
Security Monitoring
Secure Backups
```

---

# Protect Directory Backups

Backups containing Active Directory data may expose highly sensitive credential material.

Protect them using:

```text
Encryption
Access Control
Separation
Monitoring
Offline Protection
Retention Controls
```

---

# Protect Replication Rights

Accounts with directory replication privileges can represent substantial risk.

Review rights associated with:

```text
Replicating Directory Changes
Replicating Directory Changes All
```

and other sensitive replication capabilities.

---

# Trust Secret Compromise Response

If trust cryptographic material is believed compromised:

```text
Contain Source Domain
      |
      v
Assess Target Domain
      |
      v
Identify Trust
      |
      v
Rotate / Reset Trust Secret
      |
      v
Investigate Cross-Domain Authentication
      |
      v
Review Privileged Access
```

Trust reset procedures should be performed by qualified administrators following Microsoft guidance.

---

# Golden Ticket Relationship

If an attacker has obtained enough control to extract:

```text
krbtgt
```

and:

```text
Trust Secrets
```

the incident should be treated as:

```text
Major Identity Infrastructure Compromise
```

Rotating only normal user passwords is insufficient.

---

# Trust Secret Rotation

Trust passwords are normally rotated automatically by Windows.

After compromise, incident responders may need to deliberately reset trust credentials using supported administrative procedures.

Do not improvise trust-secret rotation.

Incorrect trust changes can disrupt cross-domain authentication.

---

# Incident Response Scope

A compromised trust should expand investigation to:

```text
Both Sides of the Trust
```

when organisational ownership and authority permit.

Example:

```text
Domain A Compromised
       |
       v
Trust Secret Exposed
       |
       v
Investigate Domain B Authentication
```

---

# Cross-Organisation Trusts

For a trust connecting separate organisations:

```text
Company A
   |
   v
Trust
   |
   v
Company B
```

incident response may require:

```text
Joint Coordination
Legal Review
Contractual Notification
Shared Timeline
Cross-Organisation IOC Exchange
```

---

# Reporting Trust Ticket Risk

Do not report:

```text
Kerberos Referrals Exist
```

as a vulnerability.

Referrals are normal Kerberos behaviour.

Likewise:

```text
Trust Tickets Exist
```

is not a finding.

Report the actual weakness.

---

# Potential Findings

Examples include:

```text
Excessive Cross-Domain Administrative Access
```

```text
Trust Secret Exposed Through Domain Controller Compromise
```

```text
Bidirectional Trust Unnecessarily Expands Authentication Scope
```

```text
Foreign Privileged Accounts Can Access Tier 0 Systems
```

```text
Legacy Trust Permits Unnecessary Cross-Domain Authentication
```

```text
Weak Trust Governance Allows Excessive Security Dependency
```

---

# Example Finding - Trust Secret Exposure

```text
Finding:
Active Directory Trust Secret Exposed Following Domain Controller Compromise

Description:
The assessment demonstrated access to highly sensitive Active
Directory credential material on a domain controller.

The affected material included cryptographic information associated
with an Active Directory trust relationship.

No forged trust ticket was created because sufficient evidence of the
cross-domain risk had already been established.

Impact:
Compromise of trust cryptographic material may allow an attacker with
the required knowledge and access to construct authentication material
associated with the affected trust.

Because the relationship crosses Active Directory security
boundaries, the impact may extend beyond the initially compromised
domain.

Recommendation:
Treat the affected domain as a major identity compromise.

Investigate authentication activity on both sides of the trust,
contain privileged access, rotate affected trust secrets using
supported administrative procedures and review whether the trust is
still required.

Protect domain controllers, directory backups and replication rights
as Tier 0 assets.
```

---

# Example Finding - Excessive Trust Direction

```text
Finding:
Bidirectional Trust Creates Unnecessary Cross-Domain Authentication Path

Description:
A bidirectional trust existed between two Active Directory
environments.

The documented business requirement required authentication in only
one direction.

Impact:
The additional trust direction unnecessarily increases the
authentication relationship between the environments.

Compromise or privilege misconfiguration in either environment may
therefore have broader consequences than required.

Recommendation:
Review whether the relationship can be converted to a one-way trust.

Where appropriate, combine the reduced trust direction with selective
authentication, SID filtering and network segmentation.
```

---

# Example Finding - Cross-Domain Tier 0 Access

```text
Finding:
Trusted-Domain Administrators Can Access Tier 0 Infrastructure

Description:
Administrative identities from a trusted domain were permitted to
authenticate to and administer identity infrastructure in the target
domain.

Affected systems included Tier 0 or equivalent assets.

Impact:
Compromise of privileged identities in the trusted domain could
directly affect the security of the target domain.

The target environment therefore depends on the security of the
trusted administrative environment.

Recommendation:
Separate privileged identities between security boundaries.

Remove unnecessary foreign administrative access to Tier 0 systems
and restrict identity-infrastructure administration to dedicated
management paths and privileged workstations.
```

---

# Example Finding - Legacy Trust

```text
Finding:
Legacy Trust Preserves Unnecessary Kerberos Authentication Relationship

Description:
A trust remained configured with a legacy Active Directory
environment after the associated migration had been completed.

No current application dependency requiring the trust was identified.

Impact:
The legacy environment remains part of the authentication topology.

Compromise of the legacy domain may therefore create additional
opportunities to interact with production resources through the
remaining trust.

Recommendation:
Confirm that the trust is no longer required and remove it through the
normal change-management process.

Review remaining foreign group memberships, ACLs and SID History
dependencies before removing the relationship.
```

---

# Trust Ticket Assessment Checklist

## Domain Context

- [ ] Identify current domain
- [ ] Identify current forest
- [ ] Identify domain SID
- [ ] Identify forest root
- [ ] Identify trusted domains
- [ ] Identify trusted forests
- [ ] Confirm scope before querying remote environments

## Trust

- [ ] Identify trust source
- [ ] Identify trust target
- [ ] Identify trust direction
- [ ] Identify trust type
- [ ] Identify transitivity
- [ ] Identify intra-forest status
- [ ] Review trust attributes
- [ ] Review selective authentication
- [ ] Review SID filtering

## Kerberos

- [ ] Understand source realm
- [ ] Understand target realm
- [ ] Identify KDCs
- [ ] Verify DNS
- [ ] Verify time synchronisation
- [ ] Identify target SPN
- [ ] Inspect legitimate ticket cache
- [ ] Identify referral tickets
- [ ] Identify final service ticket

## Authentication

- [ ] Determine whether Kerberos is used
- [ ] Identify NTLM fallback
- [ ] Determine authentication direction
- [ ] Identify expected cross-domain users
- [ ] Identify expected target services
- [ ] Review authentication scope

## Authorisation

- [ ] Review foreign group membership
- [ ] Review Domain Local groups
- [ ] Review Universal groups
- [ ] Review AD ACLs
- [ ] Review local groups
- [ ] Review application permissions
- [ ] Review Tier 0 access
- [ ] Confirm actual resource permissions

## SID Security

- [ ] Review domain SIDs
- [ ] Review SID History
- [ ] Review SID filtering
- [ ] Review migration exceptions
- [ ] Review privileged foreign SIDs
- [ ] Do not weaken filtering for testing

## Trust Secrets

- [ ] Treat trust secrets as highly sensitive
- [ ] Do not extract unless explicitly authorised
- [ ] Do not include raw secrets in reports
- [ ] Do not forge tickets when lower-impact evidence is sufficient
- [ ] Protect evidence containing credential material
- [ ] Remove sensitive test material after the engagement

## Safe Validation

- [ ] Prefer legitimate authentication
- [ ] Use approved test account
- [ ] Use approved target resource
- [ ] Inspect referral behaviour
- [ ] Validate minimum required access
- [ ] Avoid trust modification
- [ ] Avoid ticket forgery in production
- [ ] Stop when sufficient evidence exists

## Detection

- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4672
- [ ] Monitor 4706
- [ ] Monitor 4707
- [ ] Monitor 4716
- [ ] Monitor 5136 where applicable
- [ ] Baseline cross-domain authentication
- [ ] Monitor foreign Tier 0 access
- [ ] Correlate KDC and endpoint telemetry

## Hardening

- [ ] Remove unnecessary trusts
- [ ] Prefer minimum trust direction
- [ ] Use selective authentication where appropriate
- [ ] Maintain SID filtering
- [ ] Separate privileged accounts
- [ ] Protect domain controllers
- [ ] Protect AD backups
- [ ] Restrict replication privileges
- [ ] Segment trusted environments
- [ ] Monitor cross-domain authentication
- [ ] Review trust relationships periodically

## Incident Response

- [ ] Identify affected trust
- [ ] Identify affected domains
- [ ] Identify affected forests
- [ ] Investigate both sides where authorised
- [ ] Review cross-domain authentication
- [ ] Review foreign privileged access
- [ ] Review ticket activity
- [ ] Rotate compromised secrets using supported procedures
- [ ] Review trust necessity
- [ ] Coordinate across organisations where required

## Reporting

- [ ] Do not report normal Kerberos referrals as a vulnerability
- [ ] Identify actual weakness
- [ ] Record trust direction
- [ ] Record trust type
- [ ] Record authentication scope
- [ ] Record affected identity
- [ ] Record affected resource
- [ ] Explain cross-boundary impact
- [ ] Protect sensitive evidence
- [ ] Provide trust-specific remediation

---

# Trust Ticket Testing Model

The normal Kerberos model is:

```text
User
 |
 v
KDC
 |
 v
TGT
 |
 v
Service Ticket
 |
 v
Service
```

The referral model is:

```text
User
 |
 v
Source KDC
 |
 v
Referral TGT
 |
 v
Target KDC
 |
 v
Service Ticket
 |
 v
Target Service
```

The trust model is:

```text
Domain A
   |
   v
Trust Secret
   |
   v
Domain B
```

The authorisation model is:

```text
Valid Cross-Domain Ticket
          |
          v
Authentication
          |
          v
Security Token
          |
          v
Group / ACL
          |
          v
Resource
```

The SID-filtering model is:

```text
Cross-Domain Authentication
          |
          v
SID Information
          |
          v
Trust Boundary
          |
          v
SID Filtering
          |
          v
Authorisation
```

The selective-authentication model is:

```text
Foreign Identity
      |
      v
Trust
      |
      v
Allowed to Authenticate?
      |
      +--> No
      |
      +--> Yes
             |
             v
      Resource Permission
```

The legitimate referral model is:

```text
Normal Credentials
       |
       v
Source KDC
       |
       v
Referral
       |
       v
Target KDC
```

The trust-compromise model is:

```text
Domain Compromise
       |
       v
Trust Secret Exposure
       |
       v
Cross-Domain Authentication Risk
```

The comparison model is:

```text
krbtgt Key
   |
   v
Golden Ticket

Trust Key
   |
   v
Trust Ticket

Service Key
   |
   v
Silver Ticket

Existing Ticket
   |
   v
Pass-the-Ticket
```

The detection model is:

```text
Cross-Domain Ticket
       |
       v
KDC Activity
       |
       v
Target Logon
       |
       v
Privilege
       |
       v
Endpoint Activity
```

The defensive model is:

```text
Minimum Trust
     +
Selective Authentication
     +
SID Filtering
     +
Separate Administration
     +
Tier 0 Protection
     +
Strong Kerberos
     +
Network Segmentation
     +
Monitoring
     =
Reduced Trust Ticket Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I forge a trust ticket?"

Ask:
"Is ticket forgery actually necessary
to demonstrate the security impact?"
```

For defenders:

```text
Do Not Ask:
"Are trust tickets enabled?"

Ask:
"Which identities can authenticate
across this trust, to which systems,
and what happens if either side of
the trust is compromised?"
```

The complete model is:

```text
Identity
   |
   v
Source Domain
   |
   v
Kerberos
   |
   v
Trust Referral
   |
   v
Target Domain
   |
   v
Authentication
   |
   v
Authorisation
   |
   v
Resource
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Domain and Forest Trusts:

[Domain and Forest Trusts](trusts.md)

Trust Relationships:

[Trust Relationships](trust-relationships.md)

SID History:

[SID History](sid-history.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

NTLM:

[NTLM](ntlm.md)

NTDS:

[NTDS](ntds.md)

BloodHound:

[BloodHound](bloodhound.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

SMB:

[SMB](smb.md)

WinRM:

[WinRM](winrm.md)

Active Directory Certificate Services:

[Active Directory Certificate Services](ad-cs/index.md)

Golden Certificate:

[Golden Certificate](ad-cs/golden-certificate.md)

The next Active Directory section moves into infrastructure:

```text
docs/active-directory/adidns.md
```

followed by:

```text
docs/active-directory/shares.md
docs/active-directory/sccm.md
docs/active-directory/wsus.md
docs/active-directory/mdt.md
docs/active-directory/scom.md
docs/active-directory/adfs.md
docs/active-directory/rodc.md
```

---

# References

## Microsoft - Kerberos Authentication Overview

[Microsoft - Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Kerberos Technical Overview

[Microsoft - Kerberos Technical Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - How Domains and Forests Work

[Microsoft - How Domains and Forests Work](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc759073(v=ws.10)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-ADTrust

[Microsoft - Get-ADTrust](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adtrust){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - NLTest

[Microsoft - NLTest](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/nltest){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Klist

[Microsoft - Klist](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/klist){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4768

[Microsoft - 4768: A Kerberos Authentication Ticket Was Requested](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4768){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Security Event 4769

[Microsoft - 4769: A Kerberos Service Ticket Was Requested](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4769){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra - Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Steal or Forge Kerberos Tickets

[MITRE ATT&CK - T1558 Steal or Forge Kerberos Tickets](https://attack.mitre.org/techniques/T1558/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Golden Ticket

[MITRE ATT&CK - T1558.001 Golden Ticket](https://attack.mitre.org/techniques/T1558/001/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Pass the Ticket

[MITRE ATT&CK - T1550.003 Pass the Ticket](https://attack.mitre.org/techniques/T1550/003/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Trust tickets are a normal part of Kerberos authentication across Active Directory trust relationships.

The legitimate model is:

```text
User
 |
 v
Source KDC
 |
 v
Referral
 |
 v
Target KDC
 |
 v
Service Ticket
 |
 v
Resource
```

Their existence is not a vulnerability.

The security significance appears when:

```text
Trust Relationship
       |
       v
Trust Secret
       |
       v
Secret Compromise
       |
       v
Cross-Domain Authentication Risk
```

A penetration test should therefore not begin with ticket forgery.

The preferred workflow is:

```text
Enumerate Trust
      |
      v
Understand Direction
      |
      v
Confirm Scope
      |
      v
Observe Legitimate Referral
      |
      v
Identify Foreign Permissions
      |
      v
Validate Minimum Access
      |
      v
Report Actual Security Impact
```

Only explicitly authorised adversary simulations or dedicated laboratories should normally progress toward:

```text
Trust Secret Extraction
      |
      v
Ticket Forgery
```

The most important defensive controls remain:

```text
Minimum Trust Relationships
Selective Authentication
SID Filtering
Least Privilege
Separate Forest Administration
Tier 0 Protection
Network Segmentation
Kerberos Monitoring
```

The final question should always be:

```text
If one side of this trust is compromised,
what security impact can that compromise
have on the other side?
```

That question captures the real security significance of Active Directory trust tickets.
