---
title: Active Directory Penetration Testing
description: Practical Active Directory penetration testing notes covering domain discovery, enumeration, identity, authentication, Kerberos, NTLM, permissions, attack paths, AD CS, credential exposure, lateral movement, infrastructure, validation, detection, and remediation.
---

# Active Directory Penetration Testing

Active Directory (AD) is Microsoft's directory service for centrally managing identities, computers, authentication, authorisation, policies, services, and enterprise resources.

From a penetration-testing perspective, Active Directory should not be treated as a collection of isolated vulnerabilities.

It is better understood as a graph of relationships:

```text
Users
  |
  +--> Groups
  |
  +--> Computers
  |
  +--> Credentials
  |
  +--> Sessions
  |
  +--> ACLs
  |
  +--> Group Policy
  |
  +--> Kerberos
  |
  +--> NTLM
  |
  +--> Certificates
  |
  +--> Trusts
  |
  +--> Services
  |
  +--> Network Relationships
```

A low-privileged identity may become highly privileged by chaining several individually legitimate relationships.

For example:

```text
Low-Privileged User
        |
        v
Group Membership
        |
        v
Permission over Another Account
        |
        v
Account Control
        |
        v
Administrative Access
        |
        v
Higher Privilege
```

The objective is therefore not simply:

```text
Find Domain Admin credentials
```

It is to understand:

```text
What does this identity know?

What can it access?

What can it modify?

Which credentials can it reach?

Where can it authenticate?

Which systems trust it?

Which attack paths connect these relationships?

What security impact can actually be demonstrated?
```

!!! warning "Authorised Security Testing"
    The techniques documented in these notes are intended for authorised penetration testing, internal security assessments, red team and purple team exercises, security research, and controlled training environments. Active Directory testing can affect authentication and production infrastructure. Confirm the rules of engagement before performing intrusive actions such as password spraying, credential access, account modification, relaying, certificate enrolment, remote execution, coercion, or persistence testing.

---

## Start Here

<div class="grid cards" markdown>

-   :material-map-search-outline:{ .lg .middle } **AD Testing Methodology**

    ---

    Follow a structured engagement workflow from initial network access and domain discovery through attack-path analysis, validation, evidence, and remediation.

    [:octicons-arrow-right-24: Active Directory Methodology](methodology.md)

-   :material-graph-outline:{ .lg .middle } **Attack Path Analysis**

    ---

    Understand how identities, groups, hosts, permissions, sessions, credentials, and trusts combine to create privilege paths.

    [:octicons-arrow-right-24: BloodHound](bloodhound.md)

-   :material-certificate-outline:{ .lg .middle } **Active Directory Certificate Services**

    ---

    Assess certificate authorities, templates, enrolment rights, certificate authentication, and AD CS escalation paths.

    [:octicons-arrow-right-24: AD CS](ad-cs/index.md)

-   :material-server-network:{ .lg .middle } **Enterprise Infrastructure**

    ---

    Review supporting Windows infrastructure such as Configuration Manager and other systems that may influence large numbers of endpoints.

    [:octicons-arrow-right-24: SCCM / Configuration Manager](sccm.md)

-   :material-tools:{ .lg .middle } **Active Directory Tools**

    ---

    Understand when to use NetExec, Impacket, BloodHound, Certipy, and related tools without turning the methodology into a tool checklist.

    [:octicons-arrow-right-24: Active Directory Tools](../tools/active-directory/index.md)

-   :material-file-document-multiple-outline:{ .lg .middle } **Need Commands Quickly?**

    ---

    Use the Active Directory cheatsheet for quick enumeration, authentication, and assessment references.

    [:octicons-arrow-right-24: Active Directory Cheatsheet](../cheatsheets/active-directory.md)

</div>

---

# Active Directory Testing Model

A useful high-level model is:

```text
Initial Position
      |
      v
Network Discovery
      |
      v
Domain Discovery
      |
      v
Directory Enumeration
      |
      v
Identity + Host Mapping
      |
      v
Permission + Session Mapping
      |
      v
Attack Path Analysis
      |
      +-------------------+
      |                   |
      v                   v
Authentication       Authorisation
      |                   |
      v                   v
Kerberos / NTLM      ACL / ACE / GPO
      |                   |
      +---------+---------+
                |
                v
        Credential Access
                |
                v
       Privilege Escalation
                |
                v
        Lateral Movement
                |
                v
             Pivot
                |
                v
     Additional Networks
                |
                v
 Enterprise Infrastructure
                |
                v
          Trust Analysis
                |
                v
        Supported Impact
```

An Active Directory assessment is rarely completely linear.

A more realistic loop is:

```text
Enumerate
    |
    v
Identify Candidate
    |
    v
Validate
    |
    v
Gain New Access
    |
    v
Enumerate Again
```

Each new identity, host, session, credential, or network position can expose relationships that were not previously visible.

---

# Understand the Environment First

Before using specialist attack techniques, establish the basic environment.

Determine:

```text
Current identity
Current host
IP configuration
DNS servers
Routes
Domain
Forest
Domain Controllers
Reachable networks
Authentication protocols
Directory services
Management infrastructure
```

From Linux:

```bash
ip addr
ip route
cat /etc/resolv.conf
```

From Windows:

```powershell
ipconfig /all
route print
whoami /all
```

Environment variables may also reveal domain context:

```powershell
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:LOGONSERVER
```

The purpose is to establish the starting position before deeper enumeration.

---

# Active Directory Core Components

Important AD components include:

| Component | Security Relevance |
|---|---|
| Domain | Authentication and administration scope |
| Forest | Collection of one or more domains |
| Domain Controller | Hosts directory and authentication services |
| User | Human or service identity |
| Computer | Machine identity within AD |
| Group | Assigns permissions and administrative relationships |
| OU | Organises objects and receives delegated permissions/GPOs |
| GPO | Applies centralised configuration |
| ACL / ACE | Defines control over directory objects |
| Kerberos | Primary AD authentication protocol |
| NTLM | Legacy authentication mechanism still widely encountered |
| LDAP | Directory query and interaction protocol |
| DNS | Used to locate directory services |
| AD CS | Certificate-based identity and authentication infrastructure |
| Trust | Connects authentication across domains or forests |

These components interact.

The security issue often exists in the relationship between them rather than within one component in isolation.

---

# Domain Controllers

Domain Controllers are among the most security-sensitive systems in an AD environment.

They commonly provide:

```text
Kerberos
LDAP
LDAPS
DNS
SMB
RPC
Global Catalog
Directory services
Group Policy
Authentication
```

Common ports include:

| Port | Protocol | Typical Purpose |
|---:|---|---|
| 53 | TCP/UDP | DNS |
| 88 | TCP/UDP | Kerberos |
| 135 | TCP | RPC Endpoint Mapper |
| 389 | TCP/UDP | LDAP |
| 445 | TCP | SMB |
| 464 | TCP/UDP | Kerberos password operations |
| 636 | TCP | LDAPS |
| 3268 | TCP | Global Catalog |
| 3269 | TCP | Global Catalog over TLS |

Port presence is an indicator.

It is not by itself proof that a system is a Domain Controller.

---

# DNS and Domain Discovery

DNS is fundamental to Active Directory.

Clients use DNS to locate services including:

```text
Domain Controllers
Kerberos
LDAP
Global Catalog
Domain services
```

SRV records can therefore provide useful directory information.

Example:

```text
_ldap._tcp.dc._msdcs.example.local
```

Query:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

Domain discovery should normally precede broad attack-path enumeration.

---

# LDAP

LDAP provides access to directory information.

Depending on permissions and configuration, LDAP can expose information about:

```text
Users
Groups
Computers
Organisational Units
SPNs
Delegation
ACLs
Group Policy
Trusts
Domain configuration
Certificate services
```

A RootDSE query can help establish directory naming information.

Example:

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -s base \
  -b "" \
  defaultNamingContext \
  rootDomainNamingContext \
  dnsHostName
```

The amount of information available without authentication depends on the environment.

---

# Identities

AD security revolves around security principals.

Important identities include:

```text
Users
Computer accounts
Groups
Service accounts
Managed service accounts
Privileged accounts
Application identities
```

The assessment should determine:

```text
Who is the principal?

Which groups contain it?

Which privileges does it inherit?

Which systems accept its credentials?

Which directory objects can it modify?

Which credentials or sessions can it reach?
```

---

# Users and Service Accounts

User accounts may represent:

```text
Employees
Administrators
Applications
Services
Shared accounts
Legacy identities
Automation
```

Review relevant attributes such as:

```text
Group membership
SPNs
Account status
Delegation
Password-related settings
Description
Privilege
Administrative relationships
```

Service accounts deserve particular attention because they frequently connect:

```text
Identity
   |
   v
Application
   |
   v
Server
   |
   v
Privilege
```

---

# Computer Accounts

Computers are also AD security principals.

Typical names include:

```text
WORKSTATION01$
SERVER01$
DC01$
```

Computer accounts:

- possess credentials;
- participate in Kerberos;
- can receive permissions;
- can be members of relationships;
- can participate in delegation and certificate-based paths.

Do not treat them merely as inventory objects.

---

# Groups

Groups form a major part of AD authorisation.

Common privileged groups may include:

```text
Domain Admins
Enterprise Admins
Administrators
Server Operators
Backup Operators
Account Operators
DNSAdmins
Remote Desktop Users
Remote Management Users
```

Custom groups are often equally important.

For example:

```text
User
  |
  v
Helpdesk
  |
  v
Application Administrators
  |
  v
Server Administrators
```

Always evaluate nested membership.

---

# Organisational Units and Group Policy

OUs organise directory objects and often represent delegated administrative boundaries.

```text
Domain
  |
  +-- Domain Controllers
  |
  +-- Servers
  |
  +-- Workstations
  |
  +-- Users
```

OUs matter because:

```text
GPOs apply to them

Permissions may be delegated over them

Objects may inherit permissions

Administrative boundaries may depend on them
```

Group Policy can control:

```text
Security settings
Registry values
Scripts
Firewall rules
Software deployment
User configuration
Computer configuration
```

The assessment should therefore review both:

```text
What does the GPO configure?
```

and:

```text
Who can modify the GPO or its relevant resources?
```

---

# ACLs and ACEs

AD objects have Access Control Lists containing Access Control Entries.

Conceptually:

```text
AD Object
    |
    v
ACL
    |
    +--> ACE
    +--> ACE
    +--> ACE
```

Permissions may allow a principal to:

```text
Write attributes
Reset passwords
Modify group membership
Change ownership
Change permissions
Create child objects
Delete objects
Control another account
```

A permission should be interpreted according to the target object and resulting capability.

For example:

```text
Low-Privileged User
       |
       v
Control over Service Account
       |
       v
Service Account Privilege
       |
       v
Administrative Access
```

The security issue is the complete path.

---

# Authentication

The two most important authentication technologies encountered during AD assessments are:

```text
Kerberos
NTLM
```

Conceptually:

```text
             Authentication
                  |
        +---------+---------+
        |                   |
        v                   v
     Kerberos              NTLM
        |                   |
        v                   v
     Tickets        Challenge / Response
```

Both need to be understood because they expose different security behaviours and controls.

---

# Kerberos

Kerberos is the primary authentication protocol in modern AD environments.

Important concepts include:

```text
KDC
TGT
TGS
SPN
PAC
krbtgt
Service accounts
Delegation
```

Simplified flow:

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
 v
KDC
 |
 | TGS-REP
 v
Service Ticket
 |
 v
Service
```

Security assessment areas commonly include:

```text
Service accounts
SPNs
AS-REP roasting conditions
Kerberoasting conditions
Delegation
Ticket handling
Trusts
Certificate-backed authentication
```

The existence of one of these mechanisms does not automatically mean it is vulnerable.

---

# NTLM

NTLM uses challenge-response authentication.

Simplified:

```text
Client
   |
   v
Server Challenge
   |
   v
Client Response
   |
   v
Authentication Decision
```

NTLM commonly appears with:

```text
SMB
HTTP
LDAP
RPC
Legacy systems
Name-resolution behaviour
```

Relevant security areas can include:

```text
Authentication capture
Authentication relay
SMB signing
LDAP signing
Channel binding
Extended Protection for Authentication
Name-resolution protocols
Authentication coercion
```

Important distinction:

```text
NTLM Enabled
     !=
NTLM Relay Vulnerability
```

Relayability depends on the target protocol, security controls, authentication flow, and surrounding conditions.

---

# Attack Path Analysis

AD security testing is fundamentally attack-path analysis.

An attack path is a sequence of relationships that allows an identity to gain additional control.

Example:

```text
User
 |
 | MemberOf
 v
Helpdesk
 |
 | Write Permission
 v
Service Account
 |
 | Administrative Relationship
 v
Server
 |
 | Privileged Session
 v
Higher-Privilege Identity
```

Each individual relationship may look relatively minor.

The chain creates the risk.

The central questions are:

```text
What can this identity control?

What does the target control?

What becomes reachable after the next step?
```

---

# BloodHound

BloodHound represents AD relationships as a graph.

It can model nodes such as:

```text
Users
Groups
Computers
Domains
OUs
GPOs
Certificate infrastructure
```

and relationships such as:

```text
MemberOf
AdminTo
HasSession
GenericAll
GenericWrite
WriteDACL
WriteOwner
ForceChangePassword
Delegation
Certificate relationships
```

A useful workflow is:

```text
Collect
   |
   v
Graph
   |
   v
Identify Candidate Path
   |
   v
Understand Each Edge
   |
   v
Validate Permissions
   |
   v
Determine Reachability
   |
   v
Assess Impact
```

A graph edge is evidence of a relationship.

It should still be interpreted and, where appropriate, manually validated.

[BloodHound Notes](bloodhound.md)

---

# Active Directory Certificate Services

Active Directory Certificate Services introduces PKI and certificate-based authentication into AD.

Important components include:

```text
Certificate Authorities
Certificate Templates
Enrolment Permissions
Template Permissions
Certificate Authentication
PKINIT
Certificate Mapping
Web Enrolment
```

Simplified:

```text
Principal
    |
    v
Certificate Template
    |
    v
Certificate Authority
    |
    v
Certificate
    |
    v
Authentication
```

Security-relevant configurations can create privilege paths when certificate enrolment, identity information, permissions, or authentication mappings are insufficiently restricted.

The assessment should determine:

```text
Which CAs exist?

Which templates are published?

Who can enrol?

Who can modify templates?

What authentication properties exist?

Which identities can ultimately be impersonated or controlled?
```

[Active Directory Certificate Services](ad-cs/index.md)

---

# Enterprise Infrastructure

AD environments often include supporting infrastructure with broad administrative reach.

Examples include:

```text
Configuration Manager / SCCM
Software deployment
Patch management
Backup infrastructure
Federation
Certificate infrastructure
DNS
PXE / imaging
Virtualisation
Endpoint management
```

These systems may be highly security sensitive because compromise can affect many machines or identities.

For example:

```text
Management Infrastructure
          |
          v
Endpoint Administration
          |
          v
Large Number of Systems
```

The impact should be assessed according to actual scope and privileges rather than product presence alone.

[SCCM / Configuration Manager](sccm.md)

---

# Credential Exposure

Credentials may exist across many AD-connected systems.

Potential locations include:

```text
Shares
Scripts
Configuration
Services
Scheduled tasks
Deployment systems
Backup systems
Directory attributes
Managed accounts
Local credential stores
User profiles
PowerShell history
Applications
```

Credential testing should answer:

```text
What credential material exists?

Who can access it?

Is it current?

Where can it authenticate?

What privilege does it provide?
```

A credential only becomes meaningful when connected to access.

---

# LAPS and Managed Accounts

Managed-account technologies change how credential exposure should be analysed.

Relevant examples include:

```text
Windows LAPS
Legacy LAPS
gMSA
dMSA
```

The important question is not simply whether these technologies are deployed.

Ask:

```text
Who can retrieve the managed credential?

Which systems or services use it?

What privileges does the account have?
```

Permissions around managed credentials may themselves become attack-path relationships.

---

# Delegation

Kerberos delegation allows services to act in specific authentication contexts.

Important models include:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

Delegation should be treated as a relationship.

Review:

```text
Which principal is trusted?

Which target service is involved?

Who controls the relevant object?

Which identities can be delegated?

What effective authentication capability results?
```

---

# NTLM Relay and Coercion

Two concepts should be kept separate.

## Authentication Coercion

```text
Trigger
   |
   v
Target System
   |
   v
Outbound Authentication
```

## Relay

```text
Inbound Authentication
      |
      v
Relay Infrastructure
      |
      v
Target Service
```

A coercion primitive does not automatically provide an exploitable relay path.

A useful chain requires:

```text
Suitable Authentication
        +
Useful Relay Target
        +
Insufficient Target Protection
        +
Meaningful Authorisation
```

---

# Machine Account Relationships

Computer objects and machine-account creation permissions can contribute to attack paths.

Review:

```text
MachineAccountQuota
Delegated computer creation
OU permissions
Computer object control
Delegation relationships
Certificate relationships
```

A non-zero MachineAccountQuota is not automatically a vulnerability.

Its significance depends on what a created computer identity can subsequently influence.

---

# Trusts

Large environments may contain multiple domains or forests.

```text
Forest A
   |
   +-- Domain A
   |
   +-- Domain B
          |
          | Trust
          v
Forest B
   |
   +-- Domain C
```

Review:

```text
Direction
Transitivity
SID filtering
Selective authentication
Forest boundaries
Privileged principals
Cross-domain administration
```

The existence of a trust is expected.

The security question is what that trust permits.

---

# Lateral Movement

Lateral movement means using acquired access to reach additional systems.

Potential management technologies include:

```text
SMB
WinRM
WMI
DCOM
RDP
PowerShell Remoting
Services
Scheduled Tasks
```

The presence of a protocol does not imply that the current identity can use it.

Establish:

```text
Network reachability
Authentication
Authorisation
Local privilege
Host controls
Operational risk
```

before validation.

---

# Pivoting

A compromised host may provide access to networks that are not directly reachable from the tester.

```text
Tester
  |
  v
Compromised Host
  |
  +----------+----------+
  |                     |
  v                     v
Current Network     Internal Network
                         |
                         +--> DC
                         +--> Servers
                         +--> Applications
```

Before selecting a tunnelling tool, understand:

```text
Interfaces
Routes
DNS
Firewalls
Reachable networks
Required protocols
```

The network model should determine the pivoting technique.

---

# Domain Admin Is Not the Only Objective

Do not measure AD security only by whether Domain Admin can be reached.

Other high-impact targets may include:

```text
Certificate Authority
Configuration Manager
Federation infrastructure
Backup infrastructure
Virtualisation
Password-management systems
Security tooling
Tier-0 systems
Critical application servers
Cloud identity connectors
```

Impact should reflect the actual control obtained.

---

# Tooling

Tools help expose relationships.

They are not the methodology.

```text
Security Question
      |
      v
Choose Protocol / Data Source
      |
      v
Select Tool
      |
      v
Collect Evidence
      |
      v
Interpret Relationship
      |
      v
Validate
```

Useful tool families include:

```text
NetExec
Impacket
BloodHound
Certipy
PowerView
LDAP clients
Native Windows tools
```

The dedicated Tools section explains how these fit together:

[Active Directory Tools](../tools/active-directory/index.md)

---

# NetExec

NetExec is useful for protocol-oriented Windows and Active Directory assessment.

It can help answer questions such as:

```text
Which hosts expose SMB?

Which credentials authenticate?

Which shares are accessible?

Where does an identity have administrative access?

What directory information is available?
```

The important model is:

```text
Targets
   |
   v
Protocol
   |
   v
Authentication
   |
   v
Enumeration / Validation
```

Canonical note:

[NetExec](netexec.md)

---

# Impacket

Impacket provides implementations of protocols commonly used in Windows and Active Directory environments.

Rather than memorising individual script names, understand:

```text
Which protocol is being used?

Which authentication mechanism is involved?

What privilege is required?

What security control is being tested?

What does successful output prove?
```

This makes the tooling easier to adapt to different environments.

---

# Native Tools

Third-party tooling should not be the only source of evidence.

Useful Windows-native utilities may include:

```text
whoami
net
nltest
setspn
klist
certutil
PowerShell
AD cmdlets where available
```

Native tooling can be valuable when:

```text
Third-party tools cannot be transferred

Application control restricts binaries

Internet access is unavailable

A tool result needs independent confirmation
```

---

# Manual Validation

Automated results should generate candidates.

They should not generate conclusions automatically.

Example:

```text
BloodHound Edge
      |
      v
Understand Permission
      |
      v
Confirm Principal
      |
      v
Confirm Target
      |
      v
Check Effective Control
      |
      v
Determine Reachability
      |
      v
Assess Impact
```

Other examples:

```text
SPN Exists
     !=
Compromised Service Account
```

```text
NTLM Enabled
     !=
Relay Vulnerability
```

```text
Certificate Template Exists
     !=
AD CS Escalation Path
```

```text
Writable ACL
     !=
Automatic Domain Compromise
```

```text
SMB Available
     !=
Administrative Access
```

---

# Evidence Before Conclusions

Use a clear confidence model.

| State | Meaning |
|---|---|
| Observation | Something security relevant was identified |
| Candidate | A relationship may form part of an attack path |
| Validated | The effective permission or behaviour was confirmed |
| Reachable | The path can be exercised from the assessed position |
| Confirmed | Evidence supports a meaningful security impact |

Example:

```text
Directory Permission Identified
        |
        v
Candidate
        |
        v
Effective Permission Confirmed
        |
        v
Resulting Object Control Confirmed
        |
        v
New Privilege Becomes Reachable
        |
        v
Supported Security Impact
```

---

# Attack Path Tracking

Maintain an attack-path log throughout the assessment.

Example:

```text
alice
 |
 | MemberOf
 v
Helpdesk
 |
 | Write Permission
 v
svc_backup
 |
 | Administrative Access
 v
BACKUP01
```

For every edge record:

```text
Source Principal
Target Object
Relationship
Evidence
Required Conditions
Validation
Resulting Access
Impact
Remediation
```

This makes multi-step findings easier to defend and reproduce.

---

# Target Inventory

Maintain a basic inventory.

| Host | IP | Role | Services | Current Access |
|---|---|---|---|---|
| DC01 | 10.10.10.10 | Domain Controller | DNS/Kerberos/LDAP/SMB | Domain user |
| FILE01 | 10.10.10.20 | File Server | SMB | Share read |
| APP01 | 10.10.10.30 | Application Server | HTTP/WinRM | Unknown |

The purpose is to maintain context as access changes.

---

# Identity Inventory

Track identities without unnecessarily storing plaintext secrets.

Example:

| Identity | Type | Source | Known Access |
|---|---|---|---|
| alice | Domain user | Provided | LDAP / SMB |
| svc_app | Service account | Assessment finding | APP01 |
| admin1 | Privileged identity | Session observation | SERVER01 |

Assessment credential data should be protected according to engagement requirements.

---

# Assessment Workflow

A practical AD assessment can be divided into the following phases:

```text
1. Establish Initial Position

2. Discover Network and Domain

3. Identify Domain Controllers

4. Enumerate Identities

5. Enumerate Hosts

6. Map Groups and Permissions

7. Map Sessions and Administrative Relationships

8. Analyse Authentication

9. Analyse Credentials

10. Analyse Kerberos and Delegation

11. Analyse AD CS

12. Identify Attack Paths

13. Validate Privilege Escalation

14. Evaluate Lateral Movement

15. Identify Additional Networks

16. Review Enterprise Infrastructure

17. Analyse Trusts

18. Demonstrate Minimum Required Impact

19. Capture Evidence

20. Recommend Remediation and Retest
```

Detailed workflow:

[Active Directory Penetration Testing Methodology](methodology.md)

---

# Assessment Checklist

## Initial Position

```text
[ ] Current identity identified
[ ] Current privilege identified
[ ] Current host understood
[ ] IP configuration recorded
[ ] DNS servers identified
[ ] Routes identified
[ ] Reachable networks understood
```

## Domain Discovery

```text
[ ] Domain identified
[ ] Forest identified
[ ] Domain Controllers identified
[ ] DNS records reviewed
[ ] LDAP availability confirmed
[ ] Kerberos availability confirmed
[ ] SMB availability confirmed
```

## Identities

```text
[ ] Users enumerated
[ ] Groups enumerated
[ ] Nested groups reviewed
[ ] Privileged identities identified
[ ] Service accounts identified
[ ] Computer accounts identified
[ ] Managed service accounts considered
```

## Hosts

```text
[ ] Domain Controllers mapped
[ ] Servers identified
[ ] Workstations identified
[ ] File servers identified
[ ] Management infrastructure identified
[ ] Certificate infrastructure identified
```

## Authentication

```text
[ ] Kerberos configuration reviewed
[ ] NTLM behaviour reviewed
[ ] SPNs reviewed
[ ] AS-REP roasting conditions considered
[ ] Kerberoasting conditions considered
[ ] Password policy reviewed
[ ] Password spraying considered only where authorised
[ ] Relay protections reviewed
```

## Authorisation

```text
[ ] Group membership reviewed
[ ] Nested privileges understood
[ ] ACLs reviewed
[ ] GPO permissions reviewed
[ ] Delegated administration reviewed
[ ] Local administrative relationships reviewed
```

## Credentials

```text
[ ] Shares reviewed
[ ] Configuration reviewed
[ ] Scripts reviewed
[ ] Service-account exposure considered
[ ] Managed credentials reviewed
[ ] Deployment infrastructure reviewed
[ ] Credential-access testing limited to authorised scope
```

## Kerberos and Delegation

```text
[ ] SPNs enumerated
[ ] Delegation relationships mapped
[ ] Unconstrained delegation considered
[ ] Constrained delegation considered
[ ] RBCD considered
[ ] Relevant ticket relationships analysed
```

## AD CS

```text
[ ] Certificate Authorities identified
[ ] Templates enumerated
[ ] Enrolment permissions reviewed
[ ] Template permissions reviewed
[ ] Authentication properties reviewed
[ ] Relevant escalation conditions assessed
```

## Relay

```text
[ ] SMB signing reviewed
[ ] LDAP signing considered
[ ] Channel binding considered
[ ] EPA considered where relevant
[ ] Name-resolution behaviour reviewed
[ ] Coercion distinguished from relay
```

## Lateral Movement

```text
[ ] Administrative relationships identified
[ ] Network reachability established
[ ] SMB access reviewed
[ ] WinRM access reviewed
[ ] WMI/DCOM exposure considered
[ ] RDP access reviewed
[ ] PowerShell Remoting considered
```

## Pivoting

```text
[ ] Interfaces enumerated on newly accessed hosts
[ ] Routes enumerated
[ ] Additional networks identified
[ ] DNS requirements understood
[ ] Appropriate tunnel model selected where required
[ ] Pivot configuration documented
```

## Trusts

```text
[ ] Domain trusts enumerated
[ ] Forest trusts enumerated
[ ] Direction understood
[ ] Transitivity reviewed
[ ] SID filtering considered
[ ] Selective authentication considered
[ ] Cross-domain privileges reviewed
```

---

# Reporting Attack Paths

Avoid reporting only a tool or permission name.

For example, this is weak:

```text
GenericWrite was found.
```

A stronger explanation is:

```text
Low-Privileged Identity
        |
        v
Excessive Directory Permission
        |
        v
Control of Service Account
        |
        v
Administrative Access to Server
        |
        v
Resulting Security Impact
```

A strong AD finding should explain:

```text
Starting Privilege
      |
      v
Root Misconfiguration
      |
      v
Relationship
      |
      v
Resulting Capability
      |
      v
Next Reachable Privilege
      |
      v
Supported Impact
```

---

# Detection Perspective

Detection should be considered alongside offensive validation.

Potential telemetry includes:

```text
Windows Security Logs
Directory Service Logs
PowerShell Logs
Sysmon
Microsoft Defender for Identity
EDR
Network Telemetry
Kerberos Logs
NTLM Authentication Logs
Certificate Services Logs
Domain Controller Logs
```

The useful question is not merely:

```text
Was the technique detected?
```

Also ask:

```text
Was useful telemetry generated?

Was it collected?

Was it correlated?

Would the activity create an actionable alert?

Could the defender identify the complete attack path?
```

This connects AD assessment with purple teaming.

[Purple Teaming](../purple-teaming/index.md)

---

# Remediation Philosophy

Fix the root cause of the attack path.

Example:

```text
Excessive ACL
      |
      v
Service Account Control
      |
      v
Administrative Access
```

Possible remediation may involve:

```text
Remove excessive delegation

Reduce group membership

Separate administrative tiers

Rotate exposed credentials

Restrict remote administration

Harden authentication

Review certificate permissions

Monitor sensitive directory changes
```

Blocking the tool that discovered the condition does not fix the underlying security issue.

---

# Retesting

After remediation, retest the specific relationship.

```text
Original Attack Path
       |
       v
Remediation
       |
       v
Repeat Enumeration
       |
       v
Repeat Permission Validation
       |
       v
Confirm Path Is Broken
```

Retesting should verify:

- the original relationship no longer exists or is no longer useful;
- alternate paths were not introduced;
- legitimate administrative functionality still works;
- credentials were rotated where necessary;
- detection improvements operate as expected.

---

# Related Sections

## Active Directory

[Active Directory Methodology](methodology.md)

[BloodHound](bloodhound.md)

[NetExec](netexec.md)

[Active Directory Certificate Services](ad-cs/index.md)

[SCCM / Configuration Manager](sccm.md)

## Tools

[Active Directory Tools](../tools/active-directory/index.md)

[Security Tools](../tools/index.md)

## Supporting Sections

[Windows](../windows/index.md)

[Windows Privilege Escalation](../windows/privilege-escalation.md)

[PrivEsc Explorer](../privesc/index.md)

[Red Teaming](../red-teaming/index.md)

[Purple Teaming](../purple-teaming/index.md)

[Active Directory Cheatsheet](../cheatsheets/active-directory.md)

---

# External References

## Microsoft

[Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/){ target="_blank" rel="noopener noreferrer" }

[Kerberos Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[NTLM Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }

[Group Policy Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview){ target="_blank" rel="noopener noreferrer" }

[Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview){ target="_blank" rel="noopener noreferrer" }

## Tooling and Research

[BloodHound](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

[NetExec](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

[InternalAllTheThings - Active Directory](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/){ target="_blank" rel="noopener noreferrer" }

---

# Final Active Directory Model

Active Directory testing is not:

```text
Run Tool
   |
   v
Find Interesting Output
   |
   v
Report Vulnerability
```

Use this model:

```text
Establish Initial Position
          |
          v
Discover Domain
          |
          v
Enumerate Identities + Hosts
          |
          v
Map Permissions + Sessions
          |
          v
Understand Authentication
          |
          v
Identify Candidate Relationships
          |
          v
Build Attack Path
          |
          v
Validate Each Edge
          |
          v
Gain New Access
          |
          v
Enumerate Again
          |
          v
Determine Supported Impact
          |
          v
Capture Evidence
          |
          v
Report Root Cause
          |
          v
Remediate
          |
          v
Retest
```

The central principle is:

```text
Active Directory penetration testing
is attack-path analysis.
```

Do not ask only:

```text
What vulnerability exists?
```

Also ask:

```text
What can this identity reach?

What can it control?

Which systems trust it?

Which credentials can it access?

Where can it authenticate?

Which permissions become meaningful when chained?

What new information becomes visible after each step?

What security impact does the complete path actually support?
```
