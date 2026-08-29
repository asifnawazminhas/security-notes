# BloodHound Cheatsheet

Quick-reference commands and workflows for BloodHound collection, ingestion, attack-path analysis, validation, troubleshooting, and evidence handling during authorised Active Directory security assessments.

This cheatsheet covers:

```text
BloodHound Community Edition
SharpHound CE
BloodHound.py CE
NetExec BloodHound collection
BloodBash
Neo4j / legacy BloodHound
Cypher
Attack-path analysis
Evidence and reporting
```

For the detailed methodology and explanation of BloodHound relationships, see:

[BloodHound](../active-directory/bloodhound.md)

---

# Authorised Use

Use BloodHound and related collectors only for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Identity security reviews
Training environments
CTFs
Security research
```

Collection can generate:

```text
LDAP queries
SMB connections
RPC activity
Session enumeration
Local group enumeration
Registry queries
Kerberos activity
DNS queries
Authentication events
Endpoint telemetry
```

Always remain within the agreed scope and rules of engagement.

---

# BloodHound Mental Model

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
   +--+----------------+
   |                   |
   v                   v
BloodHound CE       BloodBash
   |                   |
   v                   v
Visual Graph        CLI Analysis
   |                   |
   +---------+---------+
             |
             v
      Relationships
             |
             v
       Attack Paths
             |
             v
        Validation
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
        +--> NetExec BloodHound ingestor

Need interactive graph analysis?
        |
        +--> BloodHound CE

Need fast offline analysis?
        |
        +--> BloodBash

Need legacy graph / Neo4j workflow?
        |
        +--> Legacy BloodHound + Neo4j

Need focused protocol validation?
        |
        +--> NetExec / Impacket / PowerView / Certipy
```

---

# Environment Variables

Useful assessment variables:

```bash
export DOMAIN="example.local"
export DC="dc01.example.local"
export DC_IP="10.10.20.10"
export USER="alice"
```

Check:

```bash
echo "$DOMAIN"
echo "$DC"
echo "$DC_IP"
echo "$USER"
```

---

# DNS First

BloodHound collection frequently depends on correct DNS.

Check the Domain Controller:

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

Check resolver configuration:

```bash
cat /etc/resolv.conf
```

---

# Time

Kerberos requires reasonably synchronised time.

Check:

```bash
date
```

If Kerberos authentication fails unexpectedly, verify:

```text
DNS
Time
Domain
KDC
FQDN
Credential
Ticket
```

---

# Core Ports

Commonly relevant ports:

```text
53      DNS
88      Kerberos
135     RPC Endpoint Mapper
389     LDAP
445     SMB
464     Kerberos password operations
636     LDAPS
3268    Global Catalog
3269    Global Catalog over TLS
```

Check:

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
    +--> Windows foothold
    |       |
    |       +--> SharpHound CE
    |
    +--> Kali / Linux
            |
            +--> BloodHound.py CE
            |
            +--> NetExec
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

Always review the installed version's help before collection.

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

Useful when you initially want to focus on directory relationships without broadly contacting endpoints.

Conceptually:

```text
Domain Controller
      |
      +--> Groups
      +--> Trusts
      +--> ACLs
      +--> OUs
      +--> GPOs
      +--> AD CS objects
      +--> Object properties
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

Session information is time-sensitive.

---

# Session Loop

```powershell
.\SharpHound.exe \
    --CollectionMethods Session \
    --Loop
```

Custom duration:

```powershell
.\SharpHound.exe `
    --CollectionMethods Session `
    --Loop `
    --LoopDuration 03:00:00
```

!!! warning
    Session looping can generate considerably more network and endpoint activity. Use it only when authorised.

---

# SharpHound Stealth Option

```powershell
.\SharpHound.exe \
    --CollectionMethods Session \
    --Stealth
```

Remember:

```text
Stealth
   !=
Undetectable
```

---

# SharpHound Collection Methods

Common collection categories include:

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

Collector capabilities evolve.

Always check:

```powershell
.\SharpHound.exe --help
```

---

# SharpHound Workflow

```text
Domain Context
      |
      v
DNS
      |
      v
Select Collection
      |
      v
SharpHound
      |
      v
ZIP
      |
      v
Secure Transfer
      |
      v
BloodHound CE
```

---

# Preserve SharpHound Output

Do not modify the original collection archive.

Suggested structure:

```text
evidence/
└── bloodhound/
    └── collection/
        ├── original/
        └── working/
```

---

# BloodHound.py

BloodHound.py provides Linux-native BloodHound collection.

Important distinction:

```text
BloodHound Legacy
       |
       +--> bloodhound-python

BloodHound CE
       |
       +--> bloodhound-ce-python
```

Do not confuse the two.

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

For legacy BloodHound:

```bash
pipx install bloodhound
```

Command:

```bash
bloodhound-python
```

The legacy collector and CE collector target different BloodHound generations.

---

# BloodHound.py CE Help

```bash
bloodhound-ce-python --help
```

Use this as the authoritative reference for the installed collector version.

---

# BloodHound.py Authentication

Supported authentication models include:

```text
Username + password
NTLM hash
AES key
Kerberos ticket / ccache
```

Exact flags should be confirmed with:

```bash
bloodhound-ce-python --help
```

---

# Basic BloodHound.py CE Pattern

```bash
bloodhound-ce-python \
    -u alice \
    -p 'Password' \
    -d example.local \
    -ns 10.10.20.10 \
    -c All
```

---

# Create ZIP Output

Where supported by the installed version:

```bash
bloodhound-ce-python \
    -u alice \
    -p 'Password' \
    -d example.local \
    -ns 10.10.20.10 \
    -c All \
    --zip
```

---

# Specify Domain Controller

A typical CE collection may specify the DC:

```bash
bloodhound-ce-python \
    -u alice \
    -p 'Password' \
    -d example.local \
    -dc dc01.example.local \
    -ns 10.10.20.10 \
    -c All \
    --zip
```

---

# BloodHound.py Collection Methods

Common collection methods include:

```text
Group
LocalAdmin
Session
Trusts
ACL
Container
RDP
DCOM
PSRemote
ObjectProps
All
```

Multiple methods are commonly comma-separated:

```bash
-c Group,ACL,Session
```

Always verify supported methods in the installed CE version.

---

# BloodHound.py Focused Collection

Instead of immediately using:

```bash
-c All
```

consider collecting only what is needed:

```bash
-c Group,ACL,Trusts
```

This can reduce unnecessary collection activity.

---

# BloodHound.py with Kerberos

If using a Kerberos ccache:

```bash
export KRB5CCNAME=/path/to/alice.ccache
```

Check:

```bash
echo "$KRB5CCNAME"
```

Then inspect Kerberos options:

```bash
bloodhound-ce-python --help
```

Kerberos depends on:

```text
DNS
FQDN
KDC
Time
Domain
Ticket
```

---

# BloodHound.py Troubleshooting

If collection fails:

```text
1. Check DNS
2. Check domain
3. Check DC FQDN
4. Check credentials
5. Check LDAP
6. Check SMB
7. Check Kerberos
8. Check collector version
9. Check collection methods
```

---

# BloodHound.py Limitations

BloodHound.py implements most, but not necessarily every SharpHound collection capability.

Therefore:

```text
BloodHound.py All
      !=
Guaranteed identical SharpHound data
```

When a relationship appears unexpectedly absent, consider collector differences before concluding that the relationship does not exist.

---

# NetExec BloodHound Ingestor

NetExec can perform BloodHound-oriented collection through its LDAP protocol.

This fits naturally into an assessment already using NetExec.

```text
NetExec
   |
   v
LDAP Authentication
   |
   v
BloodHound Collection
   |
   v
Collection Data
   |
   v
BloodHound CE
```

---

# Check LDAP

```bash
nxc ldap "$DC" \
    -d "$DOMAIN" \
    -u "$USER" \
    -p 'Password'
```

---

# NetExec LDAP Help

```bash
nxc ldap --help
```

Use this to confirm the current BloodHound collection flags.

---

# NetExec BloodHound Workflow

```text
nxc smb <range>
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
BloodHound Ingestor
      |
      v
BloodHound CE
```

---

# Why Use NetExec for BloodHound?

Useful when:

```text
NetExec is already part of the workflow

LDAP access has already been confirmed

Credentials have already been validated

You want to minimise tool switching

You want collection integrated into NetExec operations
```

---

# Collector Comparison

| Collector | Platform | Use |
|---|---|---|
| SharpHound CE | Windows | Official BloodHound CE AD collection |
| BloodHound.py CE | Linux / Kali | Linux-native collection |
| NetExec | Linux / Kali | Collection integrated with NetExec LDAP workflows |

Remember:

```text
Different collector
      |
      v
Potentially Different Coverage
```

---

# BloodHound CE

BloodHound CE provides the interactive graph-analysis platform.

Typical flow:

```text
Collection ZIP
      |
      v
BloodHound CE
      |
      v
Data Ingest
      |
      v
Graph
      |
      v
Relationships
      |
      v
Attack Paths
```

---

# BloodHound CE Quickstart

Follow the official BloodHound CE installation documentation for the current deployment method.

A local CE instance is commonly accessed through a web interface after the required services are running.

Do not expose assessment infrastructure to untrusted networks.

---

# Import Collection

Conceptually:

```text
BloodHound CE
      |
      v
Administration
      |
      v
Data Collection
      |
      v
File Ingest
      |
      v
JSON / ZIP
```

The interface can change between releases.

---

# First Analysis Steps

After importing data:

```text
1. Confirm domain
2. Confirm collection timestamp
3. Review collection health
4. Mark confirmed controlled principals
5. Identify high-value targets
6. Review outbound relationships
7. Review ACLs
8. Review sessions
9. Review delegation
10. Review AD CS
11. Review trusts
12. Investigate candidate paths
```

---

# Mark Owned Principals

When an identity is confirmed under the assessment:

```text
Known Credential
      |
      v
Mark Principal Owned
      |
      v
Analyse Outbound Paths
```

This makes the graph easier to reason about.

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
Outbound Relationships
      |
      v
Paths to High Value
      |
      v
New Collection?
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
Update Owned Context
     |
     v
Re-Collect if Needed
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
New Paths
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
DNS
    |
    v
Collect
    |
    v
Import
    |
    v
Trust Analysis
    |
    v
Cross-Domain Paths
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

# Common Nodes

```text
User
Group
Computer
Domain
OU
GPO
Certificate Authority
Certificate Template
```

---

# Common Edges

Important relationships may include:

```text
MemberOf
AdminTo
HasSession
CanRDP
CanPSRemote
ExecuteDCOM
GenericAll
GenericWrite
WriteDacl
WriteOwner
ForceChangePassword
AddMember
AllowedToDelegate
AllowedToAct
Owns
GPO relationships
AD CS relationships
Trust relationships
```

The graph schema evolves over time.

---

# Edge Interpretation Rule

Never use:

```text
Edge Exists
    =
Exploit Works
```

Use:

```text
Edge
 |
 v
Understand
 |
 v
Verify
 |
 v
Check Prerequisites
 |
 v
Check Reachability
 |
 v
Authorised Validation
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

Always consider nested groups.

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

This does not automatically prove:

```text
Host reachable
Remote management enabled
Session exists
Execution authorised
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

Session data is dynamic.

Treat it as time-sensitive.

---

# CanRDP

```text
Principal
   |
   | CanRDP
   v
Computer
```

Verify separately:

```text
3389 reachable
RDP enabled
Identity accepted
Network path
NLA / MFA restrictions
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

Verify:

```text
WinRM reachable
Authentication
Remote management permissions
Network controls
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

Actual usability can depend on:

```text
RPC
DCOM
Firewall
Permissions
Endpoint controls
```

---

# ACL Relationships

Prioritise relationships such as:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
ForceChangePassword
AddMember
Owns
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

Impact depends on object type:

```text
User
Group
Computer
OU
GPO
```

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

The security impact depends on which attributes can be modified.

---

# WriteDacl

```text
Principal
   |
   | WriteDacl
   v
Object
```

Potentially high impact because the ACL may be modified.

Validation modifies directory state and should be separately authorised.

---

# WriteOwner

```text
Principal
   |
   | WriteOwner
   v
Object
```

Changing ownership modifies AD state.

Do not validate casually.

---

# ForceChangePassword

```text
Principal
   |
   | ForceChangePassword
   v
User
```

Do not reset a production user's password simply to prove the edge.

The ACL itself may be sufficient evidence.

---

# DCSync

Look for principals with directory replication rights.

Conceptually:

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

Treat DCSync-related paths as high impact.

Do not perform credential replication unless explicitly authorised.

---

# Delegation

Review:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
S4U relationships
```

BloodHound provides graph context.

Use dedicated analysis to understand actual prerequisites.

---

# RBCD

Relevant relationships may involve:

```text
Computer control
AllowedToAct
Object ACLs
Machine accounts
```

See:

```text
active-directory/rbcd.md
```

for detailed methodology.

---

# Group Policy

Investigate:

```text
Who can modify GPO?

Where is GPO linked?

Which users receive it?

Which computers receive it?

Can a low-privileged identity influence it?
```

Conceptually:

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
Computers
```

---

# AD CS

Review relationships involving:

```text
Certificate Authorities
Certificate Templates
Enrollment permissions
Template permissions
CA permissions
Certificate mappings
```

BloodHound provides graph context.

Use dedicated tooling such as Certipy for deeper AD CS assessment.

---

# Trusts

Review:

```text
Trust direction
Trust type
Transitivity
SID filtering
Selective authentication
Cross-domain groups
Cross-domain ACLs
```

---

# High-Value Targets

Common examples:

```text
Domain Admins
Enterprise Admins
Domain Controllers
Tier-0 infrastructure
Certificate Authorities
Privileged service accounts
Identity infrastructure
```

Also identify organisation-specific critical systems.

---

# Shortest Paths

Shortest paths are useful for triage.

Conceptually:

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
Best

Shortest
   !=
Safest

Shortest
   !=
Most Reliable
```

---

# Path Prioritisation

Prioritise using:

```text
Path length
Privileges required
Network reachability
Credential availability
State changes
Operational impact
Detection likelihood
Business impact
Rules of engagement
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
Reachable?
      |
      v
Prerequisites Present?
      |
      v
Credential Available?
      |
      v
Safe?
      |
      v
Authorised?
      |
      v
Validate
```

---

# BloodBash

BloodBash performs offline analysis of SharpHound and AzureHound data without requiring BloodHound or Neo4j.

Useful for:

```text
Fast day-zero triage
Offline analysis
Terminal-based workflows
Attack-path analysis
Owned-user analysis
Collection comparison
Report generation
Large dataset triage
```

---

# Install BloodBash

Using pipx:

```bash
pipx install git+https://github.com/SquidSec/BloodBash
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

# BloodBash Basic Analysis

Directory:

```bash
bloodbash ./sharpout
```

This performs the default quick-win analysis.

Equivalent:

```bash
bloodbash ./sharpout --quick-wins
```

---

# BloodBash ZIP Analysis

```bash
bloodbash ./collection.zip
```

or:

```bash
bloodbash ./collection.zip --quick-wins
```

---

# BloodBash Full Analysis

```bash
bloodbash ./sharpout --all
```

For larger graphs:

```bash
bloodbash ./sharpout --all --fast
```

---

# BloodBash Interactive Mode

```bash
bloodbash ./sharpout --wizard
```

---

# BloodBash List Domains

```bash
bloodbash ./sharpout --list-domains
```

Useful before analysing multi-domain collections.

---

# BloodBash Domain Filter

```bash
bloodbash ./sharpout \
    --all \
    --domain EXAMPLE.LOCAL
```

---

# BloodBash Owned User Workflow

If `alice` is a confirmed controlled identity:

```bash
bloodbash ./sharpout \
    --from-user alice \
    --from-user-export
```

This creates an outbound compromise-oriented dossier.

Conceptually:

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

# BloodBash Inspect User

```bash
bloodbash ./sharpout \
    --from-user alice \
    --inspect alice
```

---

# BloodBash Explicit Path

```bash
bloodbash ./sharpout \
    --path-from alice \
    --path-to 'domain admins@corp.local'
```

---

# Multiple Sources

```bash
bloodbash ./sharpout \
    --path-from alice,bob \
    --path-to 'domain admins,enterprise admins'
```

---

# BloodBash Shortest Paths

```bash
bloodbash ./sharpout --shortest-paths
```

Include indirect relationships:

```bash
bloodbash ./sharpout \
    --shortest-paths \
    --indirect \
    --fast
```

---

# BloodBash Busiest Paths

Rank principals appearing frequently in paths:

```bash
bloodbash ./sharpout \
    --busiest-paths short \
    --busiest-paths-top 10
```

---

# BloodBash Path Break Analysis

```bash
bloodbash ./sharpout \
    --path-break \
    --path-break-top 20
```

This is particularly interesting defensively because it can help identify relationships whose removal may disrupt many attack paths.

---

# BloodBash Path Remediation Workflow

```text
Attack Paths
      |
      v
Common Relationship
      |
      v
Path Break Analysis
      |
      v
Candidate Remediation
      |
      v
Validate Business Requirement
      |
      v
Remove Excessive Relationship
```

---

# BloodBash Deep Analysis

```bash
bloodbash ./sharpout --deep-analysis
```

Useful for slower group nesting and cycle analysis.

---

# BloodBash Inspect Node

```bash
bloodbash ./sharpout \
    --inspect 'DOMAIN ADMINS@CORP.LOCAL'
```

---

# Merge Collections

```bash
bloodbash ./lowpriv.zip \
    --merge ./additional.zip \
    --all \
    --fast
```

Multiple collections:

```bash
bloodbash ./forest-root \
    --merge ./child-a.zip ./child-b.zip \
    --quick-wins
```

---

# Why Merge Collections?

Useful when:

```text
Initial low-privilege collection exists

New privilege produces more data

Additional subnet becomes reachable

Child domain is discovered

Collection occurred at multiple stages
```

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
bloodbash ./sharpout \
    --stale-accounts \
    --password-age \
    --privilege-inventory
```

---

# Owned Inventory

```bash
bloodbash ./sharpout \
    --owned alice \
    --owned-inventory
```

---

# BloodBash Profiles

Quick profile:

```bash
bloodbash ./sharpout --profile quick
```

Quick wins:

```bash
bloodbash ./sharpout --profile quick-wins
```

AD CS-focused:

```bash
bloodbash ./sharpout --profile adcs-heavy
```

Hygiene:

```bash
bloodbash ./sharpout --profile hygiene
```

Custom profile:

```bash
bloodbash ./sharpout \
    --profile ./my-engagement.yaml
```

---

# BloodBash Report Pack

```bash
bloodbash ./sharpout \
    --inventory \
    --busiest-paths short \
    --path-break \
    --report-pack ./reports
```

---

# Zip Report Pack

```bash
bloodbash ./sharpout \
    --inventory \
    --busiest-paths short \
    --path-break \
    --report-pack ./reports \
    --export-zip bloodbash-reports.zip
```

---

# BloodBash CSV Pack

```bash
bloodbash ./sharpout \
    --csv-pack ./reports
```

With ZIP:

```bash
bloodbash ./sharpout \
    --csv-pack ./reports \
    --export-zip reports.zip
```

---

# BloodBash Markdown Export

```bash
bloodbash ./sharpout \
    --all \
    --export=md
```

---

# HTML Export

```bash
bloodbash ./sharpout \
    --all \
    --export=html
```

---

# CSV Export

```bash
bloodbash ./sharpout \
    --all \
    --export=csv
```

---

# JSON Export

```bash
bloodbash ./sharpout \
    --all \
    --export=json
```

---

# YAML Export

```bash
bloodbash ./sharpout \
    --all \
    --export=yaml
```

---

# Graphviz Export

```bash
bloodbash ./sharpout \
    --all \
    --dot graph.dot
```

---

# SQLite Graph Cache

Create/use a graph database:

```bash
bloodbash ./sharpout \
    --all \
    --db bloodbash.db
```

Later:

```bash
bloodbash . \
    --db bloodbash.db \
    --from-user alice \
    --from-user-export
```

---

# BloodBash Engagement Workflow

```text
Collection
    |
    v
bloodbash ./sharpout
    |
    v
Quick Wins
    |
    v
Owned User?
    |
 +--+--+
 |     |
No    Yes
 |     |
 |     v
 |  --from-user
 |     |
 +-----+
    |
    v
Shortest Paths
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

# BloodBash vs BloodHound

```text
Need visual graph?
       |
       +--> BloodHound CE

Need interactive relationship exploration?
       |
       +--> BloodHound CE

Need quick CLI triage?
       |
       +--> BloodBash

Need no server?
       |
       +--> BloodBash

Need offline analysis?
       |
       +--> BloodBash

Need custom report packs?
       |
       +--> BloodBash
```

Use both where useful.

---

# Neo4j

Legacy BloodHound environments commonly use Neo4j directly.

Conceptually:

```text
BloodHound
    |
    v
Neo4j
    |
    v
Graph
    |
    v
Cypher
```

This remains useful when:

```text
Working with legacy BloodHound
Reviewing an existing assessment environment
Running custom Neo4j queries
Analysing older BloodHound datasets
```

BloodHound CE should not be assumed to use the same deployment architecture as legacy BloodHound.

---

# Cypher Basics

Conceptual query:

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

Conceptually:

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

Conceptually:

```cypher
MATCH p=(u)-[:MemberOf*1..]->(g:Group)
WHERE g.name CONTAINS 'DOMAIN ADMINS'
RETURN p
```

Graph schemas can differ between BloodHound generations.

Validate custom queries against the installed version.

---

# Useful Analysis Questions

Instead of asking only:

```text
How do I reach Domain Admin?
```

also ask:

```text
Which users have excessive ACL rights?

Which groups control computers?

Which computers have privileged sessions?

Who can modify GPOs?

Which principals have replication rights?

Which systems have local admin sprawl?

Which delegation relationships exist?

Which AD CS relationships are dangerous?

Which trusts introduce cross-domain exposure?

Which relationships appear on many attack paths?
```

---

# Collection Health

Record:

```text
Collector
Collector version
Collection date
Collection methods
Identity used
Domain
Domain Controller
DNS server
Failed hosts
Excluded hosts
Scope restrictions
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
Computer availability
Group membership
ACLs
Delegation
Certificate configuration
```

Re-collect when appropriate.

---

# Re-Collection Triggers

```text
New credential
New privilege
New subnet
New domain
New trust
New reachable systems
Previously inaccessible systems
Major environment change
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

rather than indiscriminately collecting everything from every host.

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
    |
    v
Impacket
```

Use Impacket to investigate protocols, not automatically to exploit every displayed relationship.

---

# BloodHound + PowerView

```text
BloodHound
    |
    v
Interesting ACL
    |
    v
PowerView
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
        Candidate Paths
```

---

# BloodHound Through a Pivot

Verify:

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

BloodHound collection may require:

```text
DNS
LDAP
SMB
Kerberos
RPC
Dynamic RPC
```

depending on collector and collection method.

A working TCP route alone does not guarantee successful collection.

---

# TUN-Based Pivot

Conceptually:

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
 +--> LDAP
 +--> SMB
 +--> Kerberos
```

TUN-based routing can simplify multi-protocol AD tooling.

---

# Evidence Directory

Create:

```bash
mkdir -p evidence/bloodhound/{collection,analysis,queries,exports,screenshots,reports}
```

Result:

```text
evidence/
└── bloodhound/
    ├── collection/
    ├── analysis/
    ├── queries/
    ├── exports/
    ├── screenshots/
    └── reports/
```

---

# Preserve Originals

Recommended:

```text
collection/
├── original/
└── working/
```

Do not modify the original collector data.

---

# Screenshot Evidence

Capture a focused graph:

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

# Sensitive Information

BloodHound collections can contain:

```text
Usernames
Computer names
Group membership
Sessions
Administrative relationships
ACLs
Trusts
AD CS information
Privileged identities
Potential attack paths
```

Treat the data as sensitive assessment material.

---

# Reporting

Do not report:

```text
BloodHound found an attack path.
```

Prefer:

```text
The tested user can modify membership of a group that
provides administrative access to multiple application
servers.
```

Report the security condition.

BloodHound is supporting evidence.

---

# Reporting Path

Document:

```text
Starting identity
Relationship
Intermediate object
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

Remember that session data is time-sensitive.

---

# Detection

Collector activity may generate:

```text
LDAP enumeration
SMB connections
RPC connections
Session enumeration
Local group enumeration
Registry queries
DNS queries
Kerberos requests
Authentication events
Process telemetry
EDR alerts
```

---

# Detection Model

```text
Single LDAP Query
      |
      v
Low Signal

Large LDAP Breadth
      +
Host Enumeration
      +
Session Queries
      +
Local Group Queries
      +
Unusual Source
      |
      v
Higher Signal
```

---

# Defensive Analysis

BloodHound can help defenders identify:

```text
Dangerous ACLs
Local administrator sprawl
Tiering violations
Privileged sessions
Dangerous delegation
Weak GPO permissions
AD CS paths
Cross-domain exposure
Overprivileged groups
Replication rights
```

---

# Remediation Model

```text
Attack Path
    |
    v
Relationship
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
Verify Path Removed
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
```

---

# Troubleshooting Checklist

## DNS

```bash
dig "$DC"
```

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

---

## LDAP

```bash
nc -vz "$DC" 389
```

---

## LDAPS

```bash
nc -vz "$DC" 636
```

---

## SMB

```bash
nc -vz "$DC" 445
```

---

## Kerberos

```bash
nc -vz "$DC" 88
```

Check:

```bash
date
```

---

# BloodHound.py Fails

Check:

```text
Correct CE vs legacy collector
DNS
Domain
DC FQDN
Credentials
LDAP
SMB
Kerberos
Collection methods
Collector version
```

---

# Missing Sessions

Possible reasons:

```text
Session no longer exists
Collection method omitted
Insufficient access
Endpoint unreachable
Firewall
Collector limitation
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
```

---

# Quick Assessment Workflow

```text
1. Identify domain
2. Identify DC
3. Fix DNS
4. Choose collector
5. Perform initial collection
6. Import/analyse
7. Mark owned identities
8. Review high-value targets
9. Review ACLs
10. Review admin relationships
11. Review sessions
12. Review delegation
13. Review AD CS
14. Review trusts
15. Investigate candidate paths
16. Validate prerequisites
17. Re-collect after context changes
18. Preserve evidence
19. Report underlying conditions
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
    bloodhound-ce-python -u USER -p 'PASSWORD' \
        -d DOMAIN -ns DNS -c All --zip

NetExec LDAP
    nxc ldap DC -d DOMAIN -u USER -p 'PASSWORD'

NetExec BloodHound options
    nxc ldap --help

BloodBash install
    pipx install git+https://github.com/SquidSec/BloodBash

BloodBash quick
    bloodbash ./sharpout

BloodBash full
    bloodbash ./sharpout --all --fast

BloodBash owned user
    bloodbash ./sharpout --from-user alice --from-user-export

BloodBash shortest paths
    bloodbash ./sharpout --shortest-paths

BloodBash explicit path
    bloodbash ./sharpout --path-from alice \
        --path-to 'domain admins@corp.local'

BloodBash inspect
    bloodbash ./sharpout --inspect alice

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

Existing ZIP
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

Need fast terminal analysis?
        |
        +--> BloodBash

Need owned-user paths?
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
```

---

# Assessment Checklist

## Preparation

```text
[ ] Scope confirmed
[ ] Domain known
[ ] DC known
[ ] DNS configured
[ ] Routes verified
[ ] Credential context understood
```

## Collection

```text
[ ] Correct collector selected
[ ] Collector version recorded
[ ] Collection methods recorded
[ ] Collection time recorded
[ ] Failed systems recorded
[ ] Scope restrictions recorded
[ ] Original data preserved
```

## Analysis

```text
[ ] Owned principals marked
[ ] High-value targets reviewed
[ ] Group memberships reviewed
[ ] Local admin relationships reviewed
[ ] Sessions reviewed
[ ] ACLs reviewed
[ ] GPO relationships reviewed
[ ] Delegation reviewed
[ ] AD CS reviewed
[ ] Trusts reviewed
[ ] Cross-domain paths reviewed
```

## Validation

```text
[ ] Interesting edges understood
[ ] Edge independently verified where needed
[ ] Network reachability checked
[ ] Credentials checked
[ ] Required privileges understood
[ ] State-changing validation authorised
[ ] Operational impact considered
```

## Evidence

```text
[ ] Original collection preserved
[ ] Collection metadata recorded
[ ] Queries saved
[ ] Focused screenshots captured
[ ] Relevant exports saved
[ ] Sensitive data protected
```

## Reporting

```text
[ ] Underlying condition reported
[ ] Tool name not treated as finding
[ ] Attack path explained
[ ] Prerequisites documented
[ ] Impact documented
[ ] Remediation addresses root relationship
```

---

# Relationship Interpretation Cheatsheet

```text
MemberOf
    -> Group membership relationship

AdminTo
    -> Administrative relationship to computer

HasSession
    -> Session relationship at collection time

CanRDP
    -> Potential RDP access relationship

CanPSRemote
    -> Potential PowerShell remoting relationship

ExecuteDCOM
    -> Potential DCOM execution relationship

GenericAll
    -> Broad control over target object

GenericWrite
    -> Ability to modify supported properties

WriteDacl
    -> Ability to modify target ACL

WriteOwner
    -> Ability to change object ownership

ForceChangePassword
    -> Ability to reset target user's password

AllowedToDelegate
    -> Kerberos delegation relationship

AllowedToAct
    -> RBCD-related relationship
```

Always investigate the current BloodHound edge documentation for precise semantics.

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
                    CANDIDATE PATH
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
```

---

# Rules to Remember

```text
BloodHound visualises relationships.

SharpHound collects data.

BloodHound.py provides Linux-native collection.

NetExec can integrate collection into an existing AD workflow.

BloodBash provides offline CLI analysis.

Neo4j remains relevant to legacy BloodHound and graph-query workflows.

An edge is evidence of a relationship, not automatic proof of exploitation.

Collection is a point-in-time snapshot.

Incomplete collection means an incomplete graph.

Re-collect when the security context changes.

Report the underlying security condition, not the tool output.
```

---

# Related Detailed Notes

```text
active-directory/bloodhound.md
active-directory/enumeration.md
active-directory/netexec.md
active-directory/impacket.md
active-directory/powerview.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/acl-ace.md
active-directory/group-policy.md
active-directory/rbcd.md
active-directory/lateral-movement.md
active-directory/pivoting.md
active-directory/trusts.md
active-directory/adcs/index.md
```

---

# Related Cheatsheets

```text
cheatsheets/active-directory.md
cheatsheets/netexec.md
cheatsheets/impacket.md
cheatsheets/networking.md
cheatsheets/windows.md
cheatsheets/powershell.md
```

---

# References

## BloodHound Documentation

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

## BloodHound Community Edition

[BloodHound Community Edition](https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart){ target="_blank" rel="noopener noreferrer" }

## SharpHound CE

[SharpHound CE](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound){ target="_blank" rel="noopener noreferrer" }

## SharpHound Flags

[SharpHound Flags](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound-flags){ target="_blank" rel="noopener noreferrer" }

## BloodHound.py

[BloodHound.py](https://github.com/dirkjanm/BloodHound.py){ target="_blank" rel="noopener noreferrer" }

## NetExec BloodHound Ingestor

[NetExec BloodHound Ingestor](https://www.netexec.wiki/ldap-protocol/bloodhound-ingestor){ target="_blank" rel="noopener noreferrer" }

## NetExec

[NetExec](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

## BloodBash

[BloodBash](https://github.com/SquidSec/BloodBash){ target="_blank" rel="noopener noreferrer" }

## Neo4j

[Neo4j](https://neo4j.com/){ target="_blank" rel="noopener noreferrer" }

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
                       ATTACK PATHS
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
                       RE-COLLECT
```

The operational principle is:

```text
Collect -> Analyse -> Mark Owned -> Find Relationships
   -> Verify -> Validate -> Re-Collect -> Report
```
