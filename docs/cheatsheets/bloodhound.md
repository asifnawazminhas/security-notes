# BloodHound Cheatsheet

Quick-reference guide for BloodHound collection, ingestion, graph analysis, attack-path analysis, validation, remediation, troubleshooting and evidence handling during authorised Active Directory security assessments.

This cheatsheet covers:

```text
BloodHound Community Edition
SharpHound CE
BloodHound.py CE
NetExec BloodHound collection
BloodBash
Legacy BloodHound / Neo4j
Cypher
Attack-path analysis
ACL analysis
Session analysis
Delegation
AD CS
Trusts
Path remediation
Evidence
Reporting
```

For detailed BloodHound methodology see:

[BloodHound](../active-directory/bloodhound.md)

Related cheatsheets:

[Active Directory](active-directory.md)

[NetExec](netexec.md)

[Impacket](impacket.md)

---

# Authorised Use

Use BloodHound and related collectors only for authorised:

```text
Penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Identity security reviews
Active Directory reviews
Training environments
CTFs
Security research
```

BloodHound collection can generate:

```text
LDAP queries
DNS queries
Kerberos activity
SMB connections
RPC connections
Session enumeration
Local group enumeration
Registry queries
Authentication events
Endpoint telemetry
```

Always remain within the agreed scope and rules of engagement.

---

# What BloodHound Does

BloodHound models identity relationships as a graph.

Instead of asking only:

```text
Who is Domain Admin?
```

BloodHound helps answer:

```text
Who can influence Domain Admin?

Who controls privileged groups?

Who controls computers used by privileged users?

Which identities have dangerous ACL rights?

Which identities can modify GPOs?

Where do privileged sessions exist?

Which delegation relationships create risk?

Which certificate relationships create privilege paths?

Which trusts create cross-domain paths?

Which permissions connect low privilege to high privilege?
```

---

# Core Mental Model

```text
Active Directory
      |
      v
Collection
      |
      +--> SharpHound CE
      |
      +--> BloodHound.py CE
      |
      +--> NetExec
      |
      v
JSON / ZIP
      |
      +------------------+
      |                  |
      v                  v
BloodHound CE        BloodBash
      |                  |
      v                  v
Visual Graph         CLI Analysis
      |                  |
      +--------+---------+
               |
               v
         Relationships
               |
               v
        Candidate Paths
               |
               v
          Prerequisites
               |
               v
          Verification
               |
               v
           Validation
               |
               v
            Evidence
               |
               v
             Report
```

---

# BloodHound Is Not an Exploit Tool

BloodHound primarily answers:

```text
What relationships exist?
```

It does not automatically prove:

```text
The relationship is currently usable

The target is reachable

The credential is valid

The service is exposed

The required protocol is allowed

Endpoint controls permit the action

The path is safe to validate

The path is authorised to validate
```

Use:

```text
Graph Relationship
       |
       v
Understand Edge
       |
       v
Verify Configuration
       |
       v
Check Preconditions
       |
       v
Check Reachability
       |
       v
Authorised Validation
```

---

# Starting Position Model

BloodHound usage changes depending on the access available.

```text
External / No Foothold
        |
        v
BloodHound Usually Not Yet Relevant

Internal / No Credentials
        |
        v
Discover AD Infrastructure
        |
        v
Obtain Approved Authentication Context

Authenticated Domain User
        |
        v
Directory Collection
        |
        v
Attack-Path Analysis

Local Windows User
        |
        v
Determine Domain Context
        |
        v
Use Available Domain Identity

Local Administrator
        |
        v
Additional Computer / Session Context
        |
        v
Re-Collect

Privileged Domain Identity
        |
        v
Targeted Collection
        |
        v
Defensive / Exposure Analysis
```

---

# Tool Selection

```text
Need official Windows collection?
        |
        +--> SharpHound CE

Need Linux / Kali collection?
        |
        +--> BloodHound.py CE

Already using NetExec?
        |
        +--> NetExec BloodHound collection

Need interactive graph analysis?
        |
        +--> BloodHound CE

Need offline CLI analysis?
        |
        +--> BloodBash

Working with legacy BloodHound?
        |
        +--> Neo4j / Legacy BloodHound

Need protocol-level validation?
        |
        +--> NetExec
        +--> Impacket
        +--> PowerView
        +--> Certipy
```

---

# Environment Variables

Useful Linux assessment variables:

```bash
export DOMAIN="example.local"
export DC="dc01.example.local"
export DC_IP="10.10.20.10"
export USER="alice"
```

Check:

```bash
printf 'DOMAIN=%s\nDC=%s\nDC_IP=%s\nUSER=%s\n' "$DOMAIN" "$DC" "$DC_IP" "$USER"
```

---

# DNS First

BloodHound collection frequently depends on correct DNS.

Domain Controller:

```bash
dig "$DC"
```

LDAP:

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

Kerberos:

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

Resolver:

```bash
cat /etc/resolv.conf
```

---

# Time

Kerberos requires reasonably synchronised time.

```bash
date
```

```bash
timedatectl
```

If Kerberos authentication fails unexpectedly, verify:

```text
DNS
Time
Domain
Realm
KDC
FQDN
Credential
Ticket
SPN
```

---

# Core Ports

Commonly relevant ports:

| Port | Protocol / Purpose |
|---:|---|
| 53 | DNS |
| 88 | Kerberos |
| 135 | RPC Endpoint Mapper |
| 389 | LDAP |
| 445 | SMB |
| 464 | Kerberos password operations |
| 636 | LDAPS |
| 3268 | Global Catalog |
| 3269 | Global Catalog over TLS |
| Dynamic | RPC |

Basic checks:

```bash
nc -vz "$DC" 389
```

```bash
nc -vz "$DC" 445
```

```bash
nc -vz "$DC" 88
```

---

# Collection Decision

```text
Where am I?
    |
    +--> Windows
    |      |
    |      +--> SharpHound CE
    |
    +--> Linux / Kali
           |
           +--> BloodHound.py CE
           |
           +--> NetExec
```

---

# Collection Strategy

Do not automatically begin with the broadest possible collection.

Prefer:

```text
Directory Relationships
       |
       v
Initial Analysis
       |
       v
Identify Interesting Systems
       |
       v
Focused Computer Collection
       |
       v
Session Collection
       |
       v
Re-Analyse
```

This can reduce unnecessary:

```text
SMB connections
RPC connections
Endpoint enumeration
Session queries
Authentication activity
```

---

# SharpHound CE

SharpHound CE is the official Active Directory collector for BloodHound CE.

Typical workflow:

```text
Windows Host
     |
     v
SharpHound CE
     |
     v
Collection
     |
     v
ZIP
     |
     v
BloodHound CE
```

---

# SharpHound Help

```powershell
.\SharpHound.exe --help
```

Always review the installed collector version before relying on a specific flag.

---

# Basic SharpHound Collection

```powershell
.\SharpHound.exe
```

---

# Specify Domain

```powershell
.\SharpHound.exe --Domain example.local
```

Short form:

```powershell
.\SharpHound.exe -d example.local
```

---

# DCOnly Collection

For directory-focused collection:

```powershell
.\SharpHound.exe --CollectionMethods DCOnly
```

This is useful for an initial directory-oriented pass.

Conceptually:

```text
Domain Controller
      |
      +--> Users
      +--> Groups
      +--> Computers
      +--> Trusts
      +--> ACLs
      +--> OUs
      +--> GPOs
      +--> Object Properties
      +--> Certificate Objects
```

---

# Session Collection

```powershell
.\SharpHound.exe --CollectionMethods Session
```

Session data can reveal:

```text
User
 |
 | HasSession
 v
Computer
```

Session information is highly time-sensitive.

---

# Session Loop

PowerShell example:

```powershell
.\SharpHound.exe --CollectionMethods Session --Loop
```

Custom duration:

```powershell
.\SharpHound.exe --CollectionMethods Session --Loop --LoopDuration 03:00:00
```

!!! warning
    Session looping can generate substantially more network and endpoint activity. Use it only when the assessment requires it.

---

# SharpHound Stealth Mode

Where supported by the installed version:

```powershell
.\SharpHound.exe --CollectionMethods Session --Stealth
```

Remember:

```text
Stealth
   !=
Invisible

Stealth
   !=
Undetectable
```

---

# SharpHound Collection Methods

Collection capabilities evolve.

Common concepts include:

```text
Default
All
DCOnly
ComputerOnly
Session
LoggedOn
Group
ACL
GPOLocalGroup
Trusts
Container
LocalGroup
LocalAdmin
RDP
DCOM
PSRemote
ObjectProps
UserRights
CertServices
```

Always confirm:

```powershell
.\SharpHound.exe --help
```

---

# SharpHound Collection Questions

Before running SharpHound ask:

```text
What data do I need?

Do I need endpoint contact?

Do I need session data?

Do I need local group data?

Do I need certificate data?

How long should collection run?

Which systems are excluded?

Which identity is being used?

How will the ZIP be protected?
```

---

# Preserve SharpHound Output

Suggested evidence structure:

```text
evidence/
└── bloodhound/
    └── collection/
        ├── original/
        └── working/
```

Do not modify the original collection archive.

---

# BloodHound.py

BloodHound.py provides Linux-native BloodHound collection.

Important distinction:

```text
Legacy BloodHound
       |
       +--> bloodhound-python

BloodHound CE
       |
       +--> bloodhound-ce-python
```

Do not accidentally use documentation for the wrong collector generation.

---

# Install BloodHound.py CE

Using pipx:

```bash
pipx install bloodhound-ce
```

Check:

```bash
bloodhound-ce-python --help
```

---

# Legacy BloodHound.py

Legacy environments may use:

```bash
pipx install bloodhound
```

Command:

```bash
bloodhound-python
```

Use the collector matching the BloodHound generation being analysed.

---

# BloodHound.py CE Help

```bash
bloodhound-ce-python --help
```

Treat the installed command's help as the version-specific reference.

---

# BloodHound.py Authentication

Depending on collector version, authentication can involve:

```text
Username + Password
NTLM
Kerberos
Kerberos Credential Cache
```

Confirm exact options:

```bash
bloodhound-ce-python --help
```

---

# Basic BloodHound.py CE Pattern

```bash
bloodhound-ce-python -u alice -p 'Password' -d example.local -ns 10.10.20.10 -c All
```

!!! warning
    Supplying passwords on the command line can expose them through shell history, screenshots and process inspection.

---

# ZIP Output

Where supported:

```bash
bloodhound-ce-python -u alice -p 'Password' -d example.local -ns 10.10.20.10 -c All --zip
```

---

# Specify Domain Controller

Typical pattern:

```bash
bloodhound-ce-python -u alice -p 'Password' -d example.local -dc dc01.example.local -ns 10.10.20.10 -c All --zip
```

Verify current syntax:

```bash
bloodhound-ce-python --help
```

---

# Focused BloodHound.py Collection

Instead of immediately using:

```text
-c All
```

consider focused methods such as:

```bash
bloodhound-ce-python -u alice -p 'Password' -d example.local -ns 10.10.20.10 -c Group,ACL,Trusts
```

Exact collection methods depend on collector version.

---

# Kerberos Collection

If using a credential cache:

```bash
export KRB5CCNAME="$PWD/alice.ccache"
```

Check:

```bash
echo "$KRB5CCNAME"
```

```bash
klist
```

Then inspect supported Kerberos options:

```bash
bloodhound-ce-python --help
```

---

# Kerberos Collection Model

```text
ccache
   |
   v
Correct Principal?
   |
   v
Correct Realm?
   |
   v
DNS Working?
   |
   v
DC FQDN?
   |
   v
Time Correct?
   |
   v
Collection
```

---

# BloodHound.py Troubleshooting

If collection fails:

```text
1. Verify CE vs legacy collector
2. Verify DNS
3. Verify domain
4. Verify DC FQDN
5. Verify credentials
6. Verify LDAP
7. Verify SMB if required
8. Verify Kerberos
9. Verify collection methods
10. Verify collector version
```

---

# Collector Differences

Do not assume:

```text
BloodHound.py All
       =
SharpHound All
```

Different collectors may have different capabilities or implementation details.

Therefore:

```text
Relationship Missing
       |
       v
Configuration Absent?
       |
       OR
       |
Collector Did Not Collect It?
```

---

# NetExec BloodHound Collection

NetExec can integrate BloodHound-oriented collection into an existing LDAP workflow.

Concept:

```text
NetExec
   |
   v
LDAP Authentication
   |
   v
Directory Collection
   |
   v
BloodHound Data
   |
   v
Analysis
```

---

# Validate LDAP First

```bash
nxc ldap "$DC" -d "$DOMAIN" -u "$USER" -p 'Password'
```

---

# NetExec LDAP Help

```bash
nxc ldap --help
```

Confirm the current BloodHound-related flags before using them.

---

# NetExec BloodHound Workflow

```text
nxc smb
   |
   v
Discover Hosts
   |
   v
Validate Credential
   |
   v
nxc ldap
   |
   v
Directory Context
   |
   v
BloodHound Collection
   |
   v
BloodHound CE / Offline Analysis
```

---

# Why Use NetExec?

Useful when:

```text
NetExec is already part of the assessment

LDAP access has already been confirmed

Credentials have already been validated

You want fewer tool transitions

You want collection integrated into the existing workflow
```

---

# Collector Comparison

| Collector | Platform | Primary Use |
|---|---|---|
| SharpHound CE | Windows | Official CE AD collection |
| BloodHound.py CE | Linux / Kali | Linux-native CE collection |
| NetExec | Linux / Kali | AD collection within NetExec workflows |

Remember:

```text
Different Collector
       |
       v
Potentially Different Coverage
```

---

# BloodHound CE

BloodHound CE provides interactive graph analysis.

Typical workflow:

```text
Collection
    |
    v
BloodHound CE
    |
    v
Ingest
    |
    v
Graph
    |
    v
Relationships
    |
    v
Paths
```

Follow the official CE installation documentation for the current deployment method.

Do not expose assessment infrastructure to untrusted networks.

---

# First Analysis Steps

After ingestion:

```text
1. Confirm domain
2. Confirm collection timestamp
3. Review collection health
4. Confirm collector and methods
5. Mark controlled principals
6. Identify high-value assets
7. Review group relationships
8. Review administrative relationships
9. Review ACLs
10. Review sessions
11. Review delegation
12. Review GPO control
13. Review AD CS
14. Review trusts
15. Review replication rights
16. Investigate candidate paths
```

---

# Mark Owned Principals

When an identity is confirmed under the assessment:

```text
Known Credential
      |
      v
Confirmed Identity
      |
      v
Mark Owned
      |
      v
Analyse Outbound Paths
```

Only mark identities as owned when control has actually been established.

---

# Mark High-Value Assets

Default high-value objects are useful, but also consider organisation-specific assets.

Examples:

```text
Domain Controllers
Domain Admins
Enterprise Admins
Certificate Authorities
Identity Servers
Backup Infrastructure
Virtualisation Platforms
SCCM
AD FS
Privileged Access Workstations
Tier-0 Systems
Critical Application Servers
```

---

# Graph Basics

```text
Node
   =
Object

Edge
   =
Relationship
```

Example:

```text
ALICE
  |
  | MemberOf
  v
HELPDESK
  |
  | AdminTo
  v
APP01
```

---

# Common Node Types

Examples include:

```text
User
Group
Computer
Domain
OU
GPO
Certificate Authority
Certificate Template
Root CA
Enterprise CA
```

The BloodHound schema evolves over time.

---

# Relationship Families

Think about edges in categories.

```text
Identity Relationships
    |
    +--> MemberOf
    +--> SIDHistory

Host Relationships
    |
    +--> AdminTo
    +--> HasSession
    +--> CanRDP
    +--> CanPSRemote
    +--> ExecuteDCOM

ACL Relationships
    |
    +--> GenericAll
    +--> GenericWrite
    +--> WriteDacl
    +--> WriteOwner
    +--> AddMember
    +--> ForceChangePassword

Kerberos Relationships
    |
    +--> Delegation
    +--> RBCD

Policy Relationships
    |
    +--> GPO Control
    +--> OU / Container Relationships

PKI Relationships
    |
    +--> Enrollment
    +--> Template Control
    +--> CA Control

Domain Relationships
    |
    +--> Trusts
    +--> Replication Rights
```

---

# Edge Interpretation Rule

Never use:

```text
Edge Exists
    =
Exploit Confirmed
```

Use:

```text
Edge
 |
 v
Read Edge Meaning
 |
 v
Identify Required Permission
 |
 v
Identify Target Object
 |
 v
Check Preconditions
 |
 v
Check Reachability
 |
 v
Check Controls
 |
 v
Determine Impact
 |
 v
Validate Only If Necessary
```

---

# MemberOf

```text
User
 |
 | MemberOf
 v
Group
```

Always account for nested membership:

```text
User
 |
 v
Group A
 |
 v
Group B
 |
 v
Privileged Group
```

---

# AdminTo

```text
Principal
   |
   | AdminTo
   v
Computer
```

This indicates an administrative relationship.

It does not automatically prove:

```text
Host reachable
SMB reachable
WinRM reachable
Remote execution possible
Endpoint controls permit execution
Testing is authorised
```

---

# HasSession

```text
User
 |
 | HasSession
 v
Computer
```

Treat session data as:

```text
Dynamic
Time-Sensitive
Collector-Dependent
```

A session observed yesterday may not exist today.

---

# CanRDP

```text
Principal
   |
   | CanRDP
   v
Computer
```

Validate separately:

```text
3389 reachable
RDP enabled
Network path exists
Identity accepted
NLA requirements
MFA requirements
Host restrictions
```

---

# CanPSRemote

```text
Principal
   |
   | CanPSRemote
   v
Computer
```

Check:

```text
WinRM reachable
5985 / 5986
Authentication
Remote management permissions
Network controls
PowerShell policy
Endpoint configuration
```

---

# ExecuteDCOM

```text
Principal
   |
   | ExecuteDCOM
   v
Computer
```

Usability can depend on:

```text
RPC
DCOM
Firewall
Permissions
Endpoint controls
```

---

# ACL Relationships

High-value ACL relationships can include:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
ForceChangePassword
AddMember
Owns
Property-Specific Rights
Extended Rights
```

---

# GenericAll

```text
Principal
   |
   | GenericAll
   v
Object
```

Impact depends on object type.

```text
User
Group
Computer
OU
GPO
Certificate Template
Other AD Object
```

Do not describe all `GenericAll` relationships as equivalent.

---

# GenericWrite

```text
Principal
   |
   | GenericWrite
   v
Object
```

Remember:

```text
GenericWrite
    !=
GenericAll
```

Determine which attributes are relevant to the target object.

---

# WriteDacl

```text
Principal
   |
   | WriteDacl
   v
Object
```

Potentially high impact because ACLs define who can perform actions on the object.

Validation that changes a DACL modifies directory state.

Prefer ACL inspection as evidence where possible.

---

# WriteOwner

```text
Principal
   |
   | WriteOwner
   v
Object
```

Changing ownership is a state-changing operation.

Ask:

```text
Who currently owns it?

Who can change ownership?

What can the new owner subsequently modify?

Is ownership change necessary to prove impact?
```

---

# ForceChangePassword

```text
Principal
   |
   | ForceChangePassword
   v
User
```

Do not reset a production user's password merely to prove the edge.

The ACL may already provide sufficient evidence.

---

# AddMember

Concept:

```text
Principal
   |
   | AddMember
   v
Group
```

Then ask:

```text
What does the group control?

Is membership nested?

Is the group privileged?

Would adding a member change production state?

Can the impact be demonstrated without modifying membership?
```

---

# Owns

```text
Principal
   |
   | Owns
   v
Object
```

Ownership can influence the ability to modify the object's security descriptor.

Investigate the actual ACL and owner semantics before determining impact.

---

# ACL Analysis Workflow

```text
Interesting ACL
      |
      v
Which Principal?
      |
      v
Which Object?
      |
      v
Which Right?
      |
      v
Inherited or Explicit?
      |
      v
What Can Actually Be Changed?
      |
      v
What Security Boundary Changes?
      |
      v
Evidence Sufficient?
```

---

# DCSync

BloodHound can identify principals with directory replication relationships.

Concept:

```text
Principal
   |
   +--> GetChanges
   |
   +--> GetChangesAll
   |
   v
Domain
```

Depending on configuration, additional replication-related rights can also matter.

Treat unexpected replication rights as high impact.

Do not replicate production credential material unless explicitly authorised.

---

# DCSync Analysis

Ask:

```text
Which identity has the rights?

Are the rights direct or inherited?

Were they intentionally delegated?

Is the identity Tier-0?

Can the rights access domain credential material?

Can the condition be demonstrated without dumping the domain?
```

---

# Kerberoastable Accounts

BloodHound can help identify service accounts and their relationships.

Do not report:

```text
Kerberoastable
```

as a vulnerability by itself.

Assess:

```text
SPN
 |
 v
Account
 |
 v
Password Age
 |
 v
Password Strength
 |
 v
Privileges
 |
 v
Reachable Assets
 |
 v
Security Impact
```

---

# AS-REP Roastable Accounts

Likewise:

```text
Preauthentication Disabled
        |
        v
Account Context
        |
        v
Password Security
        |
        v
Privileges
        |
        v
Impact
```

The configuration matters more when combined with weak credential hygiene or excessive privilege.

---

# Delegation

Review:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
S4U Relationships
```

BloodHound provides relationship context.

Use:

[Active Directory Cheatsheet](active-directory.md)

and the detailed delegation notes for prerequisite analysis.

---

# Unconstrained Delegation

Investigate:

```text
Which computer/account?

Domain Controller or non-DC?

Which users can authenticate there?

Are privileged identities protected?

Is the configuration still required?
```

---

# Constrained Delegation

Investigate:

```text
Delegating Principal
Target SPN
Protocol Transition
Who Controls Delegating Principal
Target Service
Security Boundary
```

---

# RBCD

Relevant relationships may involve:

```text
Computer Control
AllowedToAct
Object ACLs
Machine Accounts
```

Concept:

```text
Controlled Principal
       |
       v
RBCD Relationship
       |
       v
Target Computer
       |
       v
Kerberos S4U
       |
       v
Target Service
```

See:

[Resource-Based Constrained Delegation](../active-directory/rbcd.md)

---

# Machine Account Relationships

When a path involves computer creation or control, also consider:

```text
MachineAccountQuota
Existing Computer Objects
Computer ACLs
RBCD
Who Can Create Computer Objects
Which OU Receives Them
```

---

# Group Policy

Investigate:

```text
Who can modify the GPO?

Who owns the GPO?

Where is it linked?

Which OUs receive it?

Which computers receive it?

Which users receive it?

Can a low-privileged identity influence it?

Is the GPO Tier-0 relevant?
```

Concept:

```text
Principal
   |
   v
GPO
   |
   v
OU
   |
   v
Computers / Users
```

---

# GPO Path Analysis

```text
Write Right
    |
    v
GPO
    |
    v
Linked OU
    |
    v
Affected Objects
    |
    v
Privilege Context
```

Do not stop analysis at:

```text
Can modify GPO
```

Determine what the GPO actually influences.

---

# AD CS

Modern BloodHound can model certificate-related relationships.

Review:

```text
Certificate Authorities
Enterprise CAs
Certificate Templates
Enrollment Rights
Template Permissions
CA Permissions
Certificate Mappings
Authentication Relationships
```

Use Certipy and the dedicated AD CS notes for deeper validation.

---

# AD CS Analysis Model

```text
Principal
    |
    v
Enrollment / Control Right
    |
    v
Certificate Template
    |
    v
Certificate Authority
    |
    v
Authentication Capability
    |
    v
Privilege Boundary
```

Do not rely only on an ESC label.

Understand the underlying configuration.

---

# AD CS Questions

Ask:

```text
Who can enroll?

Who controls the template?

Who controls the CA?

What EKUs are configured?

Can the subject be supplied?

Is manager approval required?

Are authorised signatures required?

How are certificates mapped?

Which identities could be represented?

Is the CA trusted for authentication?
```

---

# Trusts

Review:

```text
Trust Direction
Trust Type
Transitivity
SID Filtering
Selective Authentication
Cross-Domain Groups
Cross-Domain ACLs
Cross-Domain Sessions
Cross-Domain Administrative Rights
```

---

# Trust Mental Model

```text
Domain A
   |
   | Trust
   v
Domain B
   |
   v
Authentication Boundary
   |
   v
Authorisation Relationships
```

A trust does not automatically mean:

```text
Domain A owns Domain B
```

---

# SIDHistory

SID history can create cross-object or cross-domain privilege relationships.

Investigate:

```text
Which object has SIDHistory?

Which SID is present?

Does the SID still map to a privileged object?

Is SID filtering relevant?

Is the value expected?
```

---

# High-Value Targets

Common examples:

```text
Domain Admins
Enterprise Admins
Domain Controllers
Tier-0 Systems
Certificate Authorities
Identity Infrastructure
Privileged Service Accounts
Backup Infrastructure
SCCM
AD FS
Virtualisation Management
Privileged Access Workstations
```

Also define organisation-specific high-value systems.

---

# Tier-0 Analysis

Do not limit Tier-0 to:

```text
Domain Controllers
```

Consider systems or identities capable of controlling:

```text
Active Directory
Domain Controllers
PKI
Identity Federation
Privileged Management
Virtualisation Hosting DCs
Backup / Restore of DCs
Security Management of Tier-0
```

---

# Sessions on Privileged Systems

Review:

```text
Privileged User
      |
      v
HasSession
      |
      v
Lower-Trust Computer
```

This may indicate a tiering issue even without constructing an offensive path.

---

# Local Administrator Sprawl

BloodHound is useful defensively for identifying:

```text
One User
   |
   +--> AdminTo Host A
   +--> AdminTo Host B
   +--> AdminTo Host C
   +--> AdminTo Host D
```

Questions:

```text
Is this expected?

Is a shared admin account used?

Are workstation and server tiers separated?

Could compromise of one credential affect many systems?
```

---

# Shortest Paths

Shortest paths are useful for triage.

```text
Owned Principal
      |
      v
Shortest Path
      |
      v
High-Value Target
```

But:

```text
Shortest
   !=
Safest

Shortest
   !=
Most Reliable

Shortest
   !=
Least Detectable

Shortest
   !=
Most Important
```

---

# Path Prioritisation

Consider:

```text
Path Length
Privileges Required
Credential Availability
Network Reachability
State Changes
Operational Impact
Detection Surface
Business Impact
Rules of Engagement
Reliability
Currentness of Data
```

---

# Path Validation

```text
Candidate Path
      |
      v
Relationship Current?
      |
      v
Correct Identity?
      |
      v
Reachable?
      |
      v
Prerequisites Present?
      |
      v
Security Controls?
      |
      v
Safe?
      |
      v
Authorised?
      |
      v
Minimal Validation
```

---

# Attack Path vs Finding

A path can contain multiple security conditions.

Example:

```text
Low-Privilege User
       |
       v
WriteDacl
       |
       v
Helpdesk Group
       |
       v
AdminTo
       |
       v
Application Server
```

Possible findings might concern:

```text
Excessive AD ACL
Excessive Group Privilege
Administrative Tiering
```

Do not automatically report the entire graph path as one vague finding.

---

# Choke Points

Some relationships appear in many paths.

Concept:

```text
Path A ---+
          |
Path B ---+--> Shared Relationship --> High Value
          |
Path C ---+
```

These are particularly useful for defensive remediation.

Removing one unnecessary relationship may eliminate many attack paths.

---

# Path Remediation Model

```text
Attack Paths
      |
      v
Common Relationship
      |
      v
Why Does It Exist?
      |
      v
Business Requirement?
      |
   +--+--+
   |     |
  Yes    No
   |     |
   v     v
Harden Remove
   |     |
   +--+--+
      |
      v
Re-Collect
      |
      v
Verify Paths Removed
```

---

# New Credential Workflow

```text
New Credential
      |
      v
Validate Identity
      |
      v
Mark Owned
      |
      v
Review Outbound Relationships
      |
      v
Paths to High Value
      |
      v
Need New Collection?
      |
      v
Re-Analyse
```

---

# New Privilege Workflow

```text
New Privilege
     |
     v
Update Controlled Context
     |
     v
Re-Collect if Required
     |
     v
Recalculate Paths
     |
     v
Investigate New Relationships
```

---

# New Subnet Workflow

```text
New Subnet
    |
    v
New Computers
    |
    v
Additional Collection
    |
    v
Import
    |
    v
Graph Expansion
    |
    v
New Relationships
```

---

# New Domain Workflow

```text
New Domain
    |
    v
Identify DC
    |
    v
Configure DNS
    |
    v
Understand Trust
    |
    v
Collect
    |
    v
Import
    |
    v
Cross-Domain Analysis
```

---

# BloodBash

BloodBash provides offline analysis of SharpHound and AzureHound collection data without requiring a BloodHound server.

It is useful for:

```text
Fast day-zero triage
Offline analysis
Terminal workflows
Attack-path analysis
Owned-user analysis
Collection comparison
AD / Entra analysis
Remediation analysis
Report generation
Large dataset triage
```

---

# BloodBash Installation

Using pipx:

```bash
pipx install git+https://github.com/DotNetRussell/BloodBash
```

Check:

```bash
bloodbash --help
```

Advanced help:

```bash
bloodbash --help-advanced
```

---

# BloodBash Standalone Binary

The project also publishes standalone binaries.

After obtaining the approved release:

```bash
chmod +x bloodbash-linux-x64
```

Run:

```bash
./bloodbash-linux-x64 ./sharpout --all
```

Verify release provenance before using downloaded security tooling.

---

# BloodBash Quick Analysis

Directory:

```bash
bloodbash ./sharpout
```

The default performs quick-win analysis.

Explicit:

```bash
bloodbash ./sharpout --quick-wins
```

ZIP:

```bash
bloodbash ./collection.zip --quick-wins
```

---

# BloodBash Quick-Wins Model

Current quick-win analysis can surface high-signal areas such as:

```text
Unexpected DCSync
AD CS
Dangerous ACLs
Interesting non-high-value ACLs
RBCD
Can-configure RBCD
Unconstrained Delegation
Constrained Delegation
Shadow Credentials
LAPS Readers
Trusts
Kerberoastable Accounts
AS-REP Accounts
Privileged Roastable Accounts
Password-in-Description
PasswordNotRequired
Sessions
Local Admin Relationships
Collection Health
Shortest Paths
Busiest Paths
Path Breaks
```

Treat these as analysis leads, not automatically confirmed vulnerabilities.

---

# BloodBash Full Analysis

```bash
bloodbash ./sharpout --all
```

Large graph:

```bash
bloodbash ./sharpout --all --fast
```

---

# BloodBash Wizard

```bash
bloodbash ./sharpout --wizard
```

Useful when exploring an unfamiliar collection.

---

# List Domains

```bash
bloodbash ./sharpout --list-domains
```

---

# Domain Filter

```bash
bloodbash ./sharpout --all --domain EXAMPLE.LOCAL
```

---

# Owned User Workflow

If `alice` is a confirmed controlled identity:

```bash
bloodbash ./sharpout --from-user alice --from-user-export
```

Concept:

```text
Owned User
    |
    v
Nested Groups
    |
    v
Administrative Rights
    |
    v
ACL Rights
    |
    v
Paths to High Value
```

---

# Inspect Owned User

```bash
bloodbash ./sharpout --from-user alice --inspect alice
```

---

# Explicit Path

```bash
bloodbash ./sharpout --path-from alice --path-to 'domain admins@corp.local'
```

Multiple sources:

```bash
bloodbash ./sharpout --path-from alice,bob --path-to 'domain admins,enterprise admins'
```

---

# Shortest Paths

```bash
bloodbash ./sharpout --shortest-paths
```

Include indirect relationships:

```bash
bloodbash ./sharpout --shortest-paths --indirect --fast
```

---

# Busiest Paths

```bash
bloodbash ./sharpout --busiest-paths short --busiest-paths-top 10
```

This can help identify principals or relationships appearing repeatedly across paths.

---

# Path Break Analysis

```bash
bloodbash ./sharpout --path-break --path-break-top 20
```

This is especially useful defensively.

```text
Many Paths
    |
    v
Shared Edge
    |
    v
Path Break Candidate
    |
    v
Business Review
    |
    v
Remediation
```

---

# Deep Analysis

```bash
bloodbash ./sharpout --deep-analysis
```

Useful for slower graph operations such as group nesting and cycle analysis.

---

# Inspect Node

```bash
bloodbash ./sharpout --inspect 'DOMAIN ADMINS@CORP.LOCAL'
```

---

# Merge Collections

```bash
bloodbash ./lowpriv.zip --merge ./additional.zip --all --fast
```

Multiple collections:

```bash
bloodbash ./forest-root --merge ./child-a.zip ./child-b.zip --quick-wins
```

---

# Why Merge Collections?

Useful when:

```text
Initial low-privilege collection exists

New privilege produced additional data

Another subnet became reachable

A child domain was discovered

Collection occurred at different stages

Multiple collectors produced complementary data
```

---

# Collection Comparison Model

```text
Collection A
    |
    +----+
         |
         v
      Merge
         ^
         |
    +----+
    |
Collection B
```

Be careful with time-sensitive relationships such as sessions when merging collections from different times.

---

# BloodBash Inventory

```bash
bloodbash ./sharpout --inventory
```

---

# Password Age

```bash
bloodbash ./sharpout --password-age
```

---

# Stale Accounts

```bash
bloodbash ./sharpout --stale-accounts
```

---

# Privilege Inventory

```bash
bloodbash ./sharpout --privilege-inventory
```

---

# Combined Inventory

```bash
bloodbash ./sharpout --stale-accounts --password-age --privilege-inventory
```

---

# Owned Inventory

```bash
bloodbash ./sharpout --owned alice --owned-inventory
```

Note the distinction:

```text
--from-user
    =
Outbound analysis from controlled principal

--owned
    =
Owned-principal-oriented path/inventory analysis
```

Use current help for exact semantics.

---

# BloodBash Profiles

Quick:

```bash
bloodbash ./sharpout --profile quick
```

Quick wins:

```bash
bloodbash ./sharpout --profile quick-wins
```

AD CS:

```bash
bloodbash ./sharpout --profile adcs-heavy
```

Hygiene:

```bash
bloodbash ./sharpout --profile hygiene
```

Custom:

```bash
bloodbash ./sharpout --profile ./my-engagement.yaml
```

---

# Trust Analysis

```bash
bloodbash ./sharpout --trust
```

Combined:

```bash
bloodbash ./sharpout --all --trust
```

---

# BloodBash Report Pack

```bash
bloodbash ./sharpout --inventory --busiest-paths short --path-break --report-pack ./reports
```

---

# Zip Report Pack

```bash
bloodbash ./sharpout --inventory --busiest-paths short --path-break --report-pack ./reports --export-zip bloodbash-reports.zip
```

---

# CSV Pack

```bash
bloodbash ./sharpout --csv-pack ./reports
```

ZIP:

```bash
bloodbash ./sharpout --csv-pack ./reports --export-zip reports.zip
```

---

# Markdown Export

```bash
bloodbash ./sharpout --all --export=md
```

---

# HTML Export

```bash
bloodbash ./sharpout --all --export=html
```

---

# CSV Export

```bash
bloodbash ./sharpout --all --export=csv
```

---

# JSON Export

```bash
bloodbash ./sharpout --all --export=json
```

---

# YAML Export

```bash
bloodbash ./sharpout --all --export=yaml
```

---

# Graphviz Export

```bash
bloodbash ./sharpout --all --dot graph.dot
```

---

# SQLite Graph Cache

```bash
bloodbash ./sharpout --all --db bloodbash.db
```

Later:

```bash
bloodbash . --db bloodbash.db --from-user alice --from-user-export
```

---

# BloodBash Engagement Workflow

```text
Collection
    |
    v
Quick Wins
    |
    v
Collection Health
    |
    v
Owned Principal?
    |
 +--+--+
 |     |
No    Yes
 |     |
 |     v
 |  Dossier
 |     |
 +-----+
    |
    v
Shortest Paths
    |
    v
Busiest Paths
    |
    v
Path Break
    |
    v
Inventory
    |
    v
Report Pack
```

---

# BloodBash vs BloodHound CE

```text
Need visual graph?
       |
       +--> BloodHound CE

Need interactive exploration?
       |
       +--> BloodHound CE

Need fast CLI triage?
       |
       +--> BloodBash

Need offline analysis?
       |
       +--> BloodBash

Need path-break analysis?
       |
       +--> BloodBash

Need serverless workflow?
       |
       +--> BloodBash
```

Using both can be useful.

---

# Legacy BloodHound and Neo4j

Legacy BloodHound commonly used Neo4j directly.

Concept:

```text
Legacy BloodHound
       |
       v
Neo4j
       |
       v
Graph Database
       |
       v
Cypher
```

This remains relevant when:

```text
Working with older BloodHound deployments

Reviewing historical assessment environments

Running custom Neo4j queries

Analysing older datasets
```

Do not assume BloodHound CE uses the same architecture or graph schema as legacy BloodHound.

---

# Cypher Basics

Legacy/general graph example:

```cypher
MATCH (n)
RETURN n
LIMIT 10
```

---

# List Users

```cypher
MATCH (u:User)
RETURN u
LIMIT 25
```

---

# List Groups

```cypher
MATCH (g:Group)
RETURN g
LIMIT 25
```

---

# List Computers

```cypher
MATCH (c:Computer)
RETURN c
LIMIT 25
```

---

# MemberOf Relationships

```cypher
MATCH (u:User)-[:MemberOf]->(g:Group)
RETURN u,g
LIMIT 50
```

---

# Nested Group Membership

```cypher
MATCH p=(u:User)-[:MemberOf*1..]->(g:Group)
RETURN p
LIMIT 50
```

---

# Administrative Relationships

```cypher
MATCH (u:User)-[:AdminTo]->(c:Computer)
RETURN u,c
LIMIT 50
```

---

# Sessions

```cypher
MATCH (u:User)-[:HasSession]->(c:Computer)
RETURN u,c
LIMIT 50
```

---

# Domain Admin Membership

Conceptual legacy query:

```cypher
MATCH p=(u)-[:MemberOf*1..]->(g:Group)
WHERE g.name CONTAINS 'DOMAIN ADMINS'
RETURN p
```

Graph schemas differ between BloodHound generations.

Always validate queries against the environment being used.

---

# Better Analysis Questions

Do not ask only:

```text
How do I reach Domain Admin?
```

Also ask:

```text
Which users have excessive ACL rights?

Which groups control many systems?

Which identities have broad local admin rights?

Where are privileged sessions appearing?

Who can modify GPOs?

Which principals have replication rights?

Which delegation relationships cross tiers?

Which AD CS relationships create identity risk?

Which trusts create cross-domain exposure?

Which identities can modify Tier-0 objects?

Which service accounts have excessive privilege?

Which computers create privilege concentration?

Which edges appear on many paths?

Which single remediation removes the most paths?
```

---

# Exposure Analysis

BloodHound is useful even when no exploitation is planned.

Examples:

```text
Administrative Sprawl
Privilege Concentration
Tiering Violations
Excessive ACL Delegation
Privileged Session Exposure
Weak GPO Delegation
Dangerous Trust Relationships
Excessive PKI Permissions
Replication Rights
Legacy Delegation
```

---

# Blast Radius Analysis

Ask:

```text
If this identity is compromised, what can it influence?
```

Concept:

```text
Identity
   |
   +--> Groups
   |
   +--> Computers
   |
   +--> ACLs
   |
   +--> GPOs
   |
   +--> PKI
   |
   +--> Domains
```

This is often more useful to management than a single attack path.

---

# Privilege Concentration

Look for identities that control many objects.

```text
One Principal
     |
     +--> Many Computers
     +--> Many Groups
     +--> Many ACLs
     +--> Critical GPOs
```

A compromise of such an identity can create disproportionate impact.

---

# Identity Tiering

Concept:

```text
Tier 0
  |
  | should not routinely authenticate to
  v
Lower-Trust Systems
```

BloodHound session and administrative relationships can help identify potential tiering violations.

---

# Collection Health

Record:

```text
Collector
Collector Version
Collection Date
Collection Time
Collection Methods
Identity Used
Domain
Domain Controller
DNS Server
Failed Hosts
Excluded Hosts
Scope Restrictions
Pivot / Route
```

---

# Collection Health Rule

```text
Incomplete Collection
        |
        v
Incomplete Graph
        |
        v
Missing Relationships
        |
        v
Potentially Missed Paths
```

Never interpret absence of an edge as proof that the relationship cannot exist unless collection coverage supports that conclusion.

---

# BloodHound Is a Snapshot

```text
Collection
    |
    v
Point in Time
```

Especially dynamic:

```text
Sessions
Computer Availability
Group Membership
ACLs
Delegation
Certificate Configuration
Trust Configuration
```

---

# Re-Collection Triggers

Consider re-collection after:

```text
New credential

New privilege

New subnet

New domain

New trust

New reachable systems

Previously inaccessible systems

New endpoint permissions

Major environment change

Remediation
```

---

# Re-Collection After Remediation

BloodHound can also validate remediation.

```text
Original Collection
       |
       v
Attack Path
       |
       v
Remediation
       |
       v
New Collection
       |
       v
Compare
       |
       v
Path Removed?
```

---

# Layered Collection

Prefer:

```text
Directory Collection
      |
      v
Analyse
      |
      v
Interesting Systems
      |
      v
Focused Computer Collection
      |
      v
Session Collection
      |
      v
Re-Analyse
```

rather than indiscriminately collecting everything from every endpoint.

---

# BloodHound + NetExec

```text
NetExec
   |
   v
Discover
   |
   v
Validate Credential
   |
   v
BloodHound Collection
   |
   v
Graph Analysis
   |
   v
Interesting Host / Identity
   |
   v
NetExec Focused Validation
```

See:

[NetExec Cheatsheet](netexec.md)

---

# BloodHound + Impacket

```text
BloodHound
    |
    v
Interesting Relationship
    |
    +--> SMB
    +--> RPC
    +--> Kerberos
    +--> Delegation
    +--> ACL
    |
    v
Impacket
```

Use Impacket for focused protocol-level validation.

See:

[Impacket Cheatsheet](impacket.md)

---

# BloodHound + PowerView

```text
BloodHound
    |
    v
Interesting AD Relationship
    |
    v
PowerView / Native AD Query
    |
    v
Independent Validation
```

Useful for:

```text
ACLs
Ownership
Groups
GPOs
Delegation
Object Properties
```

---

# BloodHound + Certipy

```text
BloodHound
    |
    v
AD CS Relationship
    |
    v
Certipy
    |
    v
Detailed Certificate Analysis
```

BloodHound provides graph context.

Certipy can provide certificate-specific configuration detail.

---

# BloodHound + BloodBash

```text
Collection
    |
    +----------+----------+
    |                     |
    v                     v
BloodHound CE          BloodBash
    |                     |
    v                     v
Visual Analysis        CLI Triage
    |                     |
    +----------+----------+
               |
               v
        Candidate Findings
```

---

# Collection Through a Pivot

First verify:

```bash
ip addr
```

```bash
ip route
```

```bash
cat /etc/resolv.conf
```

Then:

```bash
dig "$DC"
```

```bash
nc -vz "$DC" 389
```

```bash
nc -vz "$DC" 445
```

---

# Pivot Requirements

Depending on collection method, BloodHound may need:

```text
DNS
LDAP
SMB
Kerberos
RPC
Dynamic RPC
```

A working TCP route alone does not guarantee successful collection.

---

# TUN-Based Pivot

Concept:

```text
Kali
 |
 v
TUN Interface
 |
 v
Pivot
 |
 v
Internal AD
 |
 +--> DNS
 +--> LDAP
 +--> SMB
 +--> Kerberos
 +--> RPC
```

TUN-based routing can simplify multi-protocol AD tooling.

---

# Evidence Directory

Create:

```bash
mkdir -p evidence/bloodhound/{collection,analysis,queries,exports,screenshots,reports}
```

Suggested structure:

```text
evidence/
└── bloodhound/
    ├── collection/
    │   ├── original/
    │   └── working/
    ├── analysis/
    ├── queries/
    ├── exports/
    ├── screenshots/
    └── reports/
```

---

# Preserve Original Collection

Keep:

```text
Original ZIP / JSON
Collector Version
Collection Timestamp
Collection Methods
Identity
Domain
DC
Scope
```

Do not alter original collector output.

---

# Hash Collection Files

For evidence integrity:

```bash
sha256sum collection.zip
```

Save:

```bash
sha256sum collection.zip > collection.zip.sha256
```

---

# Screenshot Evidence

Capture focused paths.

Good:

```text
Starting Principal
       |
       v
Relationship
       |
       v
Intermediate Object
       |
       v
Relationship
       |
       v
Target
```

Avoid screenshots containing hundreds of unrelated nodes.

---

# Evidence for an Edge

Record:

```text
Source Principal:
Relationship:
Target Object:
Collector:
Collection Time:
Independent Validation:
Prerequisites:
Potential Impact:
State Change Required:
```

---

# Sensitive Information

BloodHound data can contain:

```text
Usernames
Computer Names
Group Membership
Sessions
Administrative Relationships
ACLs
Trusts
Certificate Infrastructure
Privileged Identities
Attack Paths
Internal Topology
```

Treat collections as sensitive assessment material.

---

# Reporting Principle

Do not report:

```text
BloodHound found an attack path.
```

Prefer:

```text
The tested user possesses permissions over a group that
provides administrative access to multiple application servers.
```

BloodHound is evidence.

The underlying security condition is the finding.

---

# Reporting an Attack Path

Document:

```text
Starting Identity
Relationship
Intermediate Object
Relationship
Target
Prerequisites
Validation
Impact
Remediation
```

---

# Reporting ACLs

Avoid:

```text
BloodHound shows GenericAll.
```

Prefer:

```text
The tested domain user possesses GenericAll permissions
over the target Active Directory group, providing broad
control over that directory object.
```

---

# Reporting Sessions

Avoid:

```text
BloodHound found Domain Admin on APP01.
```

Prefer:

```text
Collection data indicated that a privileged domain account
had an active session associated with APP01 at the time of
collection.
```

Always preserve the collection timestamp.

---

# Reporting Local Admin Sprawl

Instead of:

```text
BloodHound found lots of AdminTo edges.
```

Prefer:

```text
The tested administrative identity has local administrator
rights across a broad set of workstations and servers,
increasing the potential blast radius of credential compromise.
```

---

# Reporting Path Remediation

A useful defensive format:

```text
Observed path:
User -> Group -> Server -> Privileged Session

Root condition:
Excessive local administrator assignment

Recommended change:
Restrict administrative membership to systems required
for the user's operational role

Verification:
Re-collect and confirm the administrative relationship
and dependent attack paths are removed
```

---

# Detection

Collection may generate:

```text
LDAP Enumeration
SMB Connections
RPC Connections
Session Enumeration
Local Group Enumeration
Registry Queries
DNS Queries
Kerberos Requests
Authentication Events
Process Telemetry
EDR Alerts
```

---

# Detection Model

```text
Single Directory Query
        |
        v
Lower Signal

Broad LDAP Enumeration
        +
Many Endpoint Connections
        +
Session Queries
        +
Local Group Queries
        +
Unusual Source Host
        |
        v
Higher Signal
```

This is not a guarantee of detection.

---

# Defensive Monitoring Ideas

Defenders can consider monitoring:

```text
Unusual LDAP Query Breadth
Large Numbers of Computer Connections
Remote SAM / Local Group Queries
Session Enumeration
Unexpected RPC Activity
Unexpected SMB Enumeration
SharpHound Process Execution
Collector File Creation
Repeated Directory Queries from Workstations
```

Detection should focus on behaviour as well as tool names.

---

# Defensive Analysis

BloodHound can help defenders identify:

```text
Dangerous ACLs
Local Administrator Sprawl
Tiering Violations
Privileged Sessions
Dangerous Delegation
Weak GPO Permissions
AD CS Paths
Cross-Domain Exposure
Overprivileged Groups
Replication Rights
Privilege Concentration
Stale Privileged Accounts
```

---

# Remediation Prioritisation

Prioritise relationships that are:

```text
High Impact

Unnecessary

Widely Reused

Present on Many Paths

Connected to Tier-0

Easy to Remove

Easy to Monitor

Historically Stale
```

---

# Common Mistakes

```text
Edge exists
   !=
Exploit works

Shortest path
   !=
Best path

No edge
   !=
Relationship impossible

No session
   !=
No user logged on

Old collection
   !=
Current state

Collection completed
   !=
Collection complete

Owned
   !=
Permission to exploit everything

AdminTo
   !=
Remote execution confirmed

CanRDP
   !=
RDP currently reachable

WriteDacl
   !=
Permission to modify production

DCSync edge
   !=
Permission to dump all credentials during assessment
```

---

# Troubleshooting - DNS

```bash
dig "$DC"
```

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

---

# Troubleshooting - LDAP

```bash
nc -vz "$DC" 389
```

LDAPS:

```bash
nc -vz "$DC" 636
```

---

# Troubleshooting - SMB

```bash
nc -vz "$DC" 445
```

---

# Troubleshooting - Kerberos

```bash
nc -vz "$DC" 88
```

Check time:

```bash
date
```

Ticket:

```bash
klist
```

---

# BloodHound.py Fails

Check:

```text
Correct CE vs Legacy Collector
DNS
Domain
DC FQDN
Credentials
LDAP
SMB
Kerberos
Collection Methods
Collector Version
Routes
Firewall
```

---

# Missing Sessions

Possible reasons:

```text
Session ended
Session method omitted
Insufficient access
Endpoint unreachable
Firewall
Collector limitation
Collection timing
```

---

# Missing ACLs

Check:

```text
ACL collection enabled
LDAP access
Collector compatibility
Scope
Collection completeness
Object visibility
```

---

# Missing Computer Data

Check:

```text
Computer reachable
SMB
RPC
Firewall
Privileges
Collection method
Scope
Collector support
```

---

# Missing AD CS Data

Check:

```text
Collector version
Certificate collection enabled
Directory visibility
CA/template presence
BloodHound version
Ingestion compatibility
```

Use Certipy for independent certificate-specific enumeration where appropriate.

---

# Graph Appears Empty

Check:

```text
Correct collection imported
Import completed
Correct domain selected
Collection files valid
Collector generation compatible
Search filters
Time filters
Node type filters
```

---

# Quick Assessment Workflow

```text
1. Confirm scope
2. Identify domain
3. Identify DC
4. Configure DNS
5. Verify time
6. Choose collector
7. Select collection methods
8. Perform initial collection
9. Preserve original data
10. Import/analyse
11. Mark controlled identities
12. Mark organisation-specific high-value assets
13. Review groups
14. Review admin relationships
15. Review ACLs
16. Review sessions
17. Review delegation
18. Review GPO control
19. Review AD CS
20. Review trusts
21. Review replication rights
22. Identify candidate paths
23. Verify edge semantics
24. Validate prerequisites
25. Perform minimal authorised validation
26. Re-collect after context changes
27. Identify remediation choke points
28. Preserve evidence
29. Report underlying conditions
```

---

# Authenticated Domain User Workflow

```text
Domain User
    |
    v
Directory Collection
    |
    v
Mark Owned
    |
    v
Group Membership
    |
    v
Outbound ACLs
    |
    v
Computer Rights
    |
    v
GPO Rights
    |
    v
Delegation
    |
    v
AD CS
    |
    v
Trusts
    |
    v
Paths to High Value
```

---

# Local Administrator Workflow

```text
Local Admin
    |
    v
Which Computer?
    |
    v
BloodHound AdminTo?
    |
    v
Who Uses Computer?
    |
    v
Sessions
    |
    v
Other Administrative Relationships
    |
    v
Potential Blast Radius
```

Do not automatically collect credentials simply because administrative control exists.

---

# Privileged User Workflow

```text
Privileged Identity
       |
       v
Where Does It Log On?
       |
       v
Which Lower-Tier Systems?
       |
       v
Which Groups?
       |
       v
Which ACLs?
       |
       v
Which Delegation?
       |
       v
Which PKI Rights?
       |
       v
Tiering / Exposure Findings
```

---

# Defensive Review Workflow

```text
Full Collection
      |
      v
Tier-0 Assets
      |
      v
Inbound Paths
      |
      v
Privilege Concentration
      |
      v
Administrative Sprawl
      |
      v
Privileged Sessions
      |
      v
Dangerous ACLs
      |
      v
Delegation
      |
      v
AD CS
      |
      v
Trusts
      |
      v
Path Break Analysis
      |
      v
Remediation
      |
      v
Re-Collection
```

---

# One-Minute BloodHound Reference

```text
SharpHound help
    .\SharpHound.exe --help

SharpHound basic
    .\SharpHound.exe

SharpHound domain
    .\SharpHound.exe -d example.local

SharpHound DCOnly
    .\SharpHound.exe --CollectionMethods DCOnly

SharpHound sessions
    .\SharpHound.exe --CollectionMethods Session

BloodHound.py CE install
    pipx install bloodhound-ce

BloodHound.py CE help
    bloodhound-ce-python --help

BloodHound.py CE
    bloodhound-ce-python -u USER -p 'PASSWORD' -d DOMAIN -ns DNS -c All --zip

NetExec LDAP
    nxc ldap DC -d DOMAIN -u USER -p 'PASSWORD'

NetExec BloodHound options
    nxc ldap --help

BloodBash install
    pipx install git+https://github.com/DotNetRussell/BloodBash

BloodBash quick
    bloodbash ./sharpout

BloodBash full
    bloodbash ./sharpout --all --fast

BloodBash owned user
    bloodbash ./sharpout --from-user alice --from-user-export

BloodBash shortest paths
    bloodbash ./sharpout --shortest-paths

BloodBash explicit path
    bloodbash ./sharpout --path-from alice --path-to 'domain admins@corp.local'

BloodBash inspect
    bloodbash ./sharpout --inspect alice

BloodBash path break
    bloodbash ./sharpout --path-break --path-break-top 20

BloodBash merge
    bloodbash ./lowpriv.zip --merge ./additional.zip --all --fast

BloodBash report
    bloodbash ./sharpout --all --export=html
```

---

# Fast Collector Selection

```text
Windows
   |
   +--> SharpHound CE

Linux
   |
   +--> BloodHound.py CE
   |
   +--> NetExec

Existing Collection
   |
   +--> BloodHound CE
   |
   +--> BloodBash
```

---

# Fast Analysis Selection

```text
Need visual exploration?
        |
        +--> BloodHound CE

Need CLI triage?
        |
        +--> BloodBash

Need controlled-user paths?
        |
        +--> BloodHound CE
        |
        +--> BloodBash --from-user

Need custom graph queries?
        |
        +--> BloodHound / Cypher

Need offline analysis?
        |
        +--> BloodBash

Need remediation choke points?
        |
        +--> BloodBash --path-break
```

---

# Assessment Checklist

## Preparation

```text
[ ] Scope confirmed
[ ] Domain known
[ ] DC known
[ ] DNS configured
[ ] Time checked
[ ] Routes verified
[ ] Credential context understood
[ ] Collector selected
```

## Collection

```text
[ ] Correct collector generation
[ ] Collector version recorded
[ ] Collection methods recorded
[ ] Collection time recorded
[ ] Identity recorded
[ ] Failed systems recorded
[ ] Exclusions recorded
[ ] Scope restrictions recorded
[ ] Original data preserved
```

## Analysis

```text
[ ] Controlled principals marked
[ ] High-value targets reviewed
[ ] Organisation-specific Tier-0 assets reviewed
[ ] Group memberships reviewed
[ ] Local admin relationships reviewed
[ ] Sessions reviewed
[ ] ACLs reviewed
[ ] GPO relationships reviewed
[ ] Delegation reviewed
[ ] AD CS reviewed
[ ] Trusts reviewed
[ ] Replication rights reviewed
[ ] Cross-domain paths reviewed
[ ] Choke points reviewed
```

## Validation

```text
[ ] Edge semantics understood
[ ] Relationship current
[ ] Edge independently verified where necessary
[ ] Network reachability checked
[ ] Credentials checked
[ ] Required privileges understood
[ ] Security controls considered
[ ] State-changing validation authorised
[ ] Operational impact considered
```

## Evidence

```text
[ ] Original collection preserved
[ ] Collection hash recorded
[ ] Collection metadata recorded
[ ] Queries saved
[ ] Focused screenshots captured
[ ] Relevant exports saved
[ ] Sensitive data protected
```

## Reporting

```text
[ ] Underlying condition reported
[ ] Tool output not treated as finding
[ ] Attack path explained
[ ] Prerequisites documented
[ ] Impact documented
[ ] Root relationship identified
[ ] Remediation addresses root cause
[ ] Re-collection recommended where useful
```

---

# Relationship Interpretation Cheatsheet

```text
MemberOf
    -> Group membership relationship

AdminTo
    -> Administrative relationship to computer

HasSession
    -> Session relationship observed around collection time

CanRDP
    -> Potential RDP access relationship

CanPSRemote
    -> Potential PowerShell remoting relationship

ExecuteDCOM
    -> Potential DCOM access relationship

GenericAll
    -> Broad control over target object

GenericWrite
    -> Ability to modify supported target properties

WriteDacl
    -> Ability to modify target security descriptor permissions

WriteOwner
    -> Ability to change object ownership

ForceChangePassword
    -> Ability to reset target user's password

AddMember
    -> Ability to influence group membership

Owns
    -> Ownership relationship

AllowedToDelegate
    -> Kerberos delegation relationship

AllowedToAct
    -> RBCD-related relationship

DCSync
    -> Directory replication capability relationship
```

Always consult current BloodHound edge documentation for precise semantics.

---

# What Should I Investigate First?

```text
Controlled Low-Privilege User
          |
          v
Outbound Relationships
          |
          +--> ACL Rights
          +--> Group Rights
          +--> Computer Rights
          +--> GPO Rights
          +--> AD CS Rights
          |
          v
Shortest Paths
```

For defensive review:

```text
Tier-0 Asset
    |
    v
Inbound Relationships
    |
    +--> ACL Control
    +--> Group Membership
    +--> Administrative Access
    +--> Sessions
    +--> Delegation
    +--> PKI
    |
    v
Reduce Exposure
```

---

# Final Decision Tree

```text
                    ACTIVE DIRECTORY
                           |
                           v
                       COLLECTION
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        SharpHound   BloodHound.py     NetExec
             |             |             |
             +-------------+-------------+
                           |
                           v
                       JSON / ZIP
                           |
                 +---------+---------+
                 |                   |
                 v                   v
           BloodHound CE          BloodBash
                 |                   |
                 v                   v
           Visual Analysis       CLI Analysis
                 |                   |
                 +---------+---------+
                           |
                           v
                    RELATIONSHIPS
                           |
         +-----------------+-----------------+
         |                 |                 |
         v                 v                 v
        ACLs            Sessions          Groups
         |                 |                 |
         +-----------------+-----------------+
                           |
         +-----------------+-----------------+
         |                 |                 |
         v                 v                 v
     Delegation           AD CS            Trusts
         |                 |                 |
         +-----------------+-----------------+
                           |
                           v
                     TIER-0 / HIGH VALUE
                           |
                           v
                    CANDIDATE PATHS
                           |
                           v
                      CHOKE POINTS
                           |
                           v
                     PREREQUISITES
                           |
                           v
                       VALIDATION
                           |
                           v
                         IMPACT
                           |
                           v
                        EVIDENCE
                           |
                           v
                         REPORT
                           |
                           v
                      REMEDIATION
                           |
                           v
                      RE-COLLECTION
```

---

# Rules to Remember

```text
BloodHound visualises relationships.

SharpHound collects Windows/AD data.

BloodHound.py provides Linux-native collection.

NetExec can integrate collection into an existing AD workflow.

BloodBash provides offline CLI analysis.

Legacy Neo4j knowledge remains useful for older deployments.

An edge is evidence of a relationship, not automatic proof of exploitation.

A path is a hypothesis until its prerequisites are understood.

Collection is a point-in-time snapshot.

Session data is especially time-sensitive.

Incomplete collection means an incomplete graph.

Different collectors can produce different coverage.

Shortest path does not mean best path.

BloodHound is useful for offensive and defensive analysis.

Path-break analysis can identify high-value remediation opportunities.

Re-collect when security context changes.

Report the underlying security condition, not the tool output.
```

---

# Related Detailed Notes

Existing detailed notes:

```text
active-directory/bloodhound.md
active-directory/enumeration.md
active-directory/netexec.md
active-directory/impacket.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/acl-ace.md
active-directory/group-policy.md
active-directory/rbcd.md
active-directory/lateral-movement.md
active-directory/pivoting.md
```

Depending on the final filesystem cleanup, related material may also include:

```text
active-directory/trusts.md
active-directory/ad-cs/index.md
active-directory/powerview.md
```

Verify those paths against the repository before creating internal links.

---

# Related Cheatsheets

[Active Directory Cheatsheet](active-directory.md)

[NetExec Cheatsheet](netexec.md)

[Impacket Cheatsheet](impacket.md)

[Networking Cheatsheet](networking.md)

[Windows Cheatsheet](windows.md)

[PowerShell Cheatsheet](powershell.md)

---

# References

## BloodHound Documentation

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

Primary documentation for BloodHound.

---

## BloodHound Community Edition

[BloodHound Community Edition Quickstart](https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart){ target="_blank" rel="noopener noreferrer" }

Use the current CE documentation for installation and deployment.

---

## SharpHound CE

[SharpHound CE](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound){ target="_blank" rel="noopener noreferrer" }

Official SharpHound CE collection documentation.

---

## SharpHound Flags

[SharpHound Flags](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound-flags){ target="_blank" rel="noopener noreferrer" }

Check this alongside:

```powershell
.\SharpHound.exe --help
```

because collector options evolve.

---

## BloodHound.py

[BloodHound.py](https://github.com/dirkjanm/BloodHound.py){ target="_blank" rel="noopener noreferrer" }

Linux-native BloodHound collection project.

---

## NetExec

[NetExec](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

Useful for Active Directory enumeration and BloodHound-oriented LDAP workflows.

---

## NetExec BloodHound Ingestor

[NetExec BloodHound Ingestor](https://www.netexec.wiki/ldap-protocol/bloodhound-ingestor){ target="_blank" rel="noopener noreferrer" }

Verify current NetExec syntax against:

```bash
nxc ldap --help
```

---

## BloodBash

[BloodBash](https://github.com/DotNetRussell/BloodBash){ target="_blank" rel="noopener noreferrer" }

Offline SharpHound and AzureHound graph analysis, attack-path triage, owned-user analysis and remediation-oriented path analysis.

---

## BloodBash Releases

[BloodBash Releases](https://github.com/DotNetRussell/BloodBash/releases){ target="_blank" rel="noopener noreferrer" }

Use releases when obtaining standalone binaries.

---

## Neo4j

[Neo4j](https://neo4j.com/){ target="_blank" rel="noopener noreferrer" }

Relevant primarily to legacy BloodHound and general graph/Cypher workflows.

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Useful for detailed Active Directory Certificate Services analysis.

---

## NetExec GitHub

[NetExec GitHub](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }

Source repository for NetExec.

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

Useful for focused protocol-level validation of relationships discovered during AD analysis.

---

# Final Quick Reference

```text
                         BLOODHOUND
                             |
                             v
                          COLLECT
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
        SharpHound     BloodHound.py       NetExec
             |               |               |
             +---------------+---------------+
                             |
                             v
                         JSON / ZIP
                             |
                   +---------+---------+
                   |                   |
                   v                   v
             BloodHound CE          BloodBash
                   |                   |
                   v                   v
              Visual Graph         CLI Triage
                   |                   |
                   +---------+---------+
                             |
                             v
                        MARK OWNED
                             |
                             v
                    REVIEW RELATIONSHIPS
                             |
        +--------------------+--------------------+
        |                    |                    |
        v                    v                    v
       ACLs               Sessions            Groups
        |                    |                    |
        +--------------------+--------------------+
                             |
        +--------------------+--------------------+
        |                    |                    |
        v                    v                    v
    Delegation              AD CS               Trusts
        |                    |                    |
        +--------------------+--------------------+
                             |
                             v
                         TIER-0
                             |
                             v
                       ATTACK PATHS
                             |
                             v
                       CHOKE POINTS
                             |
                             v
                       VERIFY EDGES
                             |
                             v
                      PREREQUISITES
                             |
                             v
                   AUTHORISED VALIDATION
                             |
                             v
                          EVIDENCE
                             |
                             v
                           REPORT
                             |
                             v
                       REMEDIATION
                             |
                             v
                        RE-COLLECT
```

The operational principle is:

```text
Collect
   |
   v
Analyse
   |
   v
Understand Relationships
   |
   v
Mark Controlled Principals
   |
   v
Identify High-Value Assets
   |
   v
Find Candidate Paths
   |
   v
Verify Preconditions
   |
   v
Validate Minimally
   |
   v
Identify Choke Points
   |
   v
Report Root Conditions
   |
   v
Remediate
   |
   v
Re-Collect
```

The most important rule is:

```text
BloodHound does not tell you what to exploit.

BloodHound tells you which identity relationships deserve investigation.
```
