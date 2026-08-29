# BloodHound

BloodHound is an identity security and attack-path analysis platform used to model relationships between users, groups, computers, permissions, sessions, trusts, certificate services, and other identity objects.

During an authorised Active Directory assessment, BloodHound helps answer questions such as:

```text
What can this user control?

Who can administer this computer?

Which principals can modify this group?

Who can reach Domain Admin?

Which systems contain privileged sessions?

Which ACLs create privilege escalation paths?

Which delegation relationships are dangerous?

Which certificate services relationships create attack paths?

Which paths become available after obtaining a new credential?

What should be investigated next?
```

BloodHound should not be treated simply as:

```text
Run collector
    |
    v
Click "Shortest Path to Domain Admin"
    |
    v
Exploit everything
```

A better methodology is:

```text
Collect
   |
   v
Build Identity Graph
   |
   v
Understand Relationships
   |
   v
Identify Interesting Paths
   |
   v
Verify Prerequisites
   |
   v
Validate Safely
   |
   v
Re-Collect / Re-Analyse
   |
   v
Evidence
   |
   v
Report
```

---

# Authorised Use

Use BloodHound and related collectors only for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Identity security assessments
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
Registry access
Kerberos activity
DNS queries
Authentication events
Endpoint telemetry
```

Always remain within the agreed scope and rules of engagement.

---

# BloodHound Ecosystem

BloodHound is better understood as an ecosystem rather than a single executable.

```text
                    Active Directory
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      SharpHound      BloodHound.py      NetExec
          |                |                |
          |                |                |
          +----------------+----------------+
                           |
                           v
                    Collection Data
                           |
                 JSON / ZIP / Graph
                           |
             +-------------+-------------+
             |                           |
             v                           v
       BloodHound CE                 BloodBash
             |                           |
             v                           v
       Graph Analysis              Offline Analysis
             |
             v
       Attack Paths
```

Depending on the environment, collection may be performed using:

```text
SharpHound CE
BloodHound.py CE
NetExec BloodHound ingestor
Other compatible collectors
```

Analysis may then be performed using:

```text
BloodHound CE
BloodHound / Neo4j legacy environments
BloodBash
Custom graph analysis
```

---

# BloodHound Community Edition

BloodHound Community Edition (BloodHound CE) is the current community platform from SpecterOps.

It provides:

```text
Graph-based identity analysis
Attack path visualisation
Active Directory analysis
AD CS relationships
Hybrid identity analysis
Cypher-based graph querying
Data ingestion
Attack path exploration
```

The basic architecture is:

```text
Collector
   |
   v
JSON / ZIP
   |
   v
BloodHound CE
   |
   v
Graph Database
   |
   v
Web Interface
   |
   v
Attack Path Analysis
```

---

# BloodHound CE Installation

Current BloodHound CE deployments commonly use the BloodHound CLI and containerised services.

Follow the official BloodHound CE documentation for the current installation process.

After installation, the interface is commonly exposed locally through:

```text
http://localhost:8080
```

Do not expose a local BloodHound instance to untrusted networks without appropriate authentication and network controls.

---

# Data Collection

BloodHound is only as useful as the data supplied to it.

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
Potentially Missed Attack Paths
```

Collection strategy therefore matters.

---

# Collection Options

A practical AD assessment may use several collection methods.

```text
Windows foothold
     |
     +--> SharpHound CE
     |
Linux foothold
     |
     +--> BloodHound.py CE
     |
     +--> NetExec
     |
Existing JSON / ZIP
     |
     +--> BloodHound CE
     |
     +--> BloodBash
```

The collector should be chosen based on:

```text
Operating system
Network position
Credentials
Privileges
Endpoint controls
Available protocols
Assessment scope
Required data
Operational impact
```

---

# SharpHound CE

SharpHound CE is the official Active Directory collector for BloodHound CE.

It is written in C# and collects information through mechanisms including:

```text
LDAP
Windows APIs
SMB
RPC
Registry access
Session enumeration
Local group enumeration
```

depending on the selected collection methods.

---

# Basic SharpHound Collection

From a domain-joined Windows system:

```powershell
.\SharpHound.exe
```

Without additional collection flags, SharpHound uses its default collection method.

The resulting data is normally written into a ZIP archive containing BloodHound-compatible JSON.

---

# Specify a Domain

```powershell
.\SharpHound.exe --Domain example.local
```

Short form:

```powershell
.\SharpHound.exe -d example.local
```

DNS must be able to resolve the target domain correctly.

---

# SharpHound Collection Methods

Important collection methods include:

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
CARegistry
DCRegistry
CertServices
```

Always check the current SharpHound documentation because collection capabilities evolve.

---

# Default Collection

A default SharpHound CE collection gathers important information including:

```text
Group memberships
Domain trusts
AD object permissions
AD CS object permissions
OU structure
Group Policy links
Object properties
Local group relationships
User sessions
```

depending on accessibility and permissions.

---

# DCOnly

For a lower-impact directory-focused collection:

```powershell
.\SharpHound.exe --CollectionMethods DCOnly
```

Conceptually:

```text
SharpHound
    |
    v
Domain Controller
    |
    +--> Groups
    +--> Trusts
    +--> ACLs
    +--> AD CS objects
    +--> OUs
    +--> GPO links
    +--> Object properties
```

`DCOnly` avoids directly querying every domain-joined workstation/server for computer-specific data.

This can be useful when:

```text
Reducing endpoint connections
Performing initial collection
Working under restrictive ROE
Performing directory-only analysis
```

---

# Session Collection

Sessions are more dynamic than many directory relationships.

```powershell
.\SharpHound.exe --CollectionMethods Session
```

Sessions can reveal relationships such as:

```text
User
 |
 v
Logged onto
 |
 v
Computer
```

These relationships may change frequently.

---

# Session Loop

SharpHound can repeatedly collect session information:

```powershell
.\SharpHound.exe --CollectionMethods Session --Loop
```

A custom loop duration can be supplied:

```powershell
.\SharpHound.exe \
    --CollectionMethods Session \
    --Loop \
    --LoopDuration 03:00:00
```

Session looping can significantly increase network and endpoint activity.

Use it only when authorised.

---

# Stealth Collection

SharpHound provides:

```text
--Stealth
```

for supported collection workflows.

Example:

```powershell
.\SharpHound.exe \
    --CollectionMethods Session \
    --Stealth
```

"Stealth" should not be interpreted as:

```text
Undetectable
```

It changes collection behaviour but still generates observable activity.

---

# Scope Collection

Limit collection where possible.

For example, collection can be constrained using:

```text
Domain
Distinguished Name
Computer list
LDAP filter
```

This is useful for:

```text
Large environments
Restricted assessment scope
Sensitive networks
Phased assessments
Testing specific OUs
```

---

# Track Computer Calls

SharpHound can track computer collection attempts.

This can help answer:

```text
Which systems were contacted?

Which requests failed?

Which systems were unreachable?
```

This is useful for both troubleshooting and evidence.

---

# SharpHound Workflow

```text
Windows Access
      |
      v
Confirm Domain
      |
      v
Confirm DNS
      |
      v
Choose Collection Method
      |
      v
Run SharpHound
      |
      v
Collect ZIP
      |
      v
Transfer Securely
      |
      v
BloodHound CE
```

---

# BloodHound.py

BloodHound.py is a Python-based BloodHound ingestor originally developed for performing BloodHound collection from Linux systems.

It is based heavily on Python Active Directory protocol implementations and is useful when:

```text
No Windows foothold exists

You are testing from Kali Linux

LDAP and SMB are reachable

You possess domain credentials

SharpHound cannot be executed

A Linux-native collector is preferable
```

---

# BloodHound.py Legacy vs CE

This distinction is important.

The primary BloodHound.py branch targets legacy BloodHound versions.

For BloodHound Community Edition, use the CE-compatible version.

Conceptually:

```text
BloodHound Legacy
       |
       +--> bloodhound-python

BloodHound CE
       |
       +--> bloodhound-ce-python
```

Do not assume data generated for one version is automatically correct for another.

---

# Install BloodHound.py for BloodHound CE

Using pipx:

```bash
pipx install bloodhound-ce
```

Check:

```bash
bloodhound-ce-python --help
```

---

# Install BloodHound.py Legacy

For legacy BloodHound:

```bash
pipx install bloodhound
```

Command:

```bash
bloodhound-python
```

Do not confuse this with the CE collector.

---

# BloodHound.py Authentication

BloodHound.py supports authentication using mechanisms including:

```text
Username + password
NTLM hash
AES key
Kerberos TGT / ccache
```

The exact options depend on the installed version.

Always inspect:

```bash
bloodhound-ce-python --help
```

before running a collection.

---

# BloodHound.py Basic Context

Set useful variables:

```bash
export DOMAIN="example.local"
export DC="dc01.example.local"
export DC_IP="10.10.20.10"
export USER="alice"
```

Verify DNS:

```bash
dig "$DC"
```

Verify LDAP SRV:

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

Verify Kerberos:

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

---

# BloodHound.py Collection

The exact command should always be based on the installed CE version.

General structure:

```bash
bloodhound-ce-python \
    -u <username> \
    -p '<password>' \
    -d <domain> \
    -ns <dns-server> \
    -c <collection-methods>
```

Check:

```bash
bloodhound-ce-python --help
```

for current options.

---

# Collection Methods

BloodHound.py supports many BloodHound collection categories.

Examples include:

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

Support may not be identical to SharpHound.

When complete coverage matters, understand the limitations of the collector being used.

---

# BloodHound.py Workflow

```text
Kali
 |
 v
Domain Credential
 |
 v
DNS
 |
 v
LDAP / SMB
 |
 v
bloodhound-ce-python
 |
 v
JSON Collection
 |
 v
BloodHound CE
```

---

# Kerberos with BloodHound.py

Kerberos collection requires correct:

```text
DNS
Time
Domain
KDC
FQDN
Credential cache
```

Check:

```bash
date
```

```bash
dig "$DC"
```

If using a ccache:

```bash
export KRB5CCNAME=/path/to/user.ccache
```

Check:

```bash
echo "$KRB5CCNAME"
```

---

# NetExec BloodHound Ingestor

NetExec can also perform BloodHound-oriented LDAP collection.

This is particularly useful when NetExec is already being used during an internal assessment.

Conceptually:

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
JSON / ZIP
   |
   v
BloodHound
```

This can reduce tool switching during an assessment.

---

# NetExec LDAP Context

Start by validating LDAP access:

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'
```

Check the current BloodHound options:

```bash
nxc ldap --help
```

NetExec syntax changes over time, so use the installed version's help output rather than assuming older command syntax.

---

# NetExec BloodHound Collection

The NetExec LDAP protocol contains BloodHound collection functionality.

Before collection, confirm:

```text
Domain
Domain Controller
DNS
Credentials
BloodHound edition
Collection scope
```

Then inspect:

```bash
nxc ldap --help
```

for the current BloodHound collection options.

---

# NetExec BloodHound Workflow

```text
nxc smb
   |
   v
Discover Environment
   |
   v
Validate Credential
   |
   v
nxc ldap
   |
   v
Directory Access
   |
   v
BloodHound Collection
   |
   v
BloodHound CE
```

This integrates naturally with the broader NetExec methodology.

---

# Choosing a Collector

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

Then consider:

```text
Need maximum official compatibility?
        |
        +--> SharpHound CE

Need Linux-native collection?
        |
        +--> BloodHound.py CE

Already using NetExec heavily?
        |
        +--> NetExec BloodHound ingestor

Only have collected JSON/ZIP?
        |
        +--> BloodHound CE
        |
        +--> BloodBash
```

---

# Collector Comparison

| Collector | Platform | Best Use |
|---|---|---|
| SharpHound CE | Windows | Official BloodHound CE AD collection |
| BloodHound.py CE | Linux / Kali | Linux-native AD collection |
| NetExec | Linux / Kali | Integrated LDAP/BloodHound collection during NetExec workflows |

Collection capabilities are not necessarily identical.

---

# Importing Data into BloodHound CE

SharpHound and compatible collectors generate:

```text
JSON
ZIP
```

BloodHound CE can ingest collection data through the web interface.

Typical workflow:

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
Upload JSON / ZIP
```

The exact interface may change between releases.

---

# BloodHound Graph Model

BloodHound represents identity relationships as a graph.

```text
Node
 |
 +--> User
 +--> Group
 +--> Computer
 +--> Domain
 +--> OU
 +--> GPO
 +--> Certificate Authority
 +--> Certificate Template
```

Relationships are represented as edges.

```text
User
 |
 | MemberOf
 v
Group
```

or:

```text
User
 |
 | AdminTo
 v
Computer
```

---

# Nodes and Edges

A graph contains:

```text
Nodes = objects

Edges = relationships
```

Example:

```text
ALICE
  |
  | MemberOf
  v
HELPDESK
  |
  | GenericAll
  v
SERVER ADMINS
  |
  | AdminTo
  v
APP01
```

The value of BloodHound comes from chaining relationships.

---

# Attack Paths

An attack path is a sequence of relationships that may allow one identity to influence another security object.

```text
User
 |
 v
Group
 |
 v
Computer
 |
 v
Privileged Session
 |
 v
Tier-0 Identity
```

BloodHound helps identify these relationships.

It does not automatically prove that every path is exploitable.

---

# Edge Interpretation

For every interesting edge ask:

```text
What does this edge mean?

What security control creates it?

What permissions are required?

Is the relationship current?

Can I independently verify it?

Does exploitation require state changes?

What is the impact?

Is validation authorised?
```

---

# Common Relationships

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
Owns
DCSync-related rights
AllowedToDelegate
AllowedToAct
GPO relationships
AD CS relationships
Trust relationships
```

The exact BloodHound edge model evolves over time.

---

# MemberOf

Example:

```text
ALICE
 |
 | MemberOf
 v
HELPDESK
```

Nested membership matters.

```text
ALICE
 |
 v
HELPDESK
 |
 v
SERVER ADMINS
 |
 v
ADMINISTRATORS
```

Do not only examine direct memberships.

---

# AdminTo

```text
User / Group
     |
     | AdminTo
     v
Computer
```

This indicates an administrative relationship.

It does not necessarily mean:

```text
The user is currently logged on

The host is reachable

Remote administration is enabled

Execution is authorised
```

Those conditions should be verified separately.

---

# HasSession

```text
User
 |
 | HasSession
 v
Computer
```

Session data is highly useful but dynamic.

A session discovered earlier may no longer exist.

Treat session information as:

```text
Potentially Time Sensitive
```

---

# CanRDP

```text
Principal
   |
   | CanRDP
   v
Computer
```

This indicates an RDP-related relationship.

Still verify:

```text
RDP reachable
Account permitted
Network path
Authentication restrictions
MFA / NLA controls
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
Authentication works
Remote management rights
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

This represents a DCOM-related relationship.

Actual usability depends on:

```text
Permissions
Firewall
RPC
DCOM configuration
Endpoint controls
```

---

# ACL Relationships

BloodHound is particularly useful for finding dangerous ACL relationships.

Examples include:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
ForceChangePassword
AddMember
```

These may form paths such as:

```text
User
 |
 | GenericAll
 v
Group
 |
 | MemberOf
 v
Privileged Group
```

---

# GenericAll

Conceptually:

```text
Principal
   |
   | GenericAll
   v
Object
```

This represents broad control over the target object.

The exact security impact depends on the object type.

For example:

```text
User
Group
Computer
OU
GPO
```

can each produce different attack possibilities.

---

# GenericWrite

```text
Principal
   |
   | GenericWrite
   v
Object
```

This represents permission to modify certain properties.

Do not automatically equate:

```text
GenericWrite
```

with:

```text
Full Control
```

The exploitable effect depends on the target object's writable attributes.

---

# WriteDacl

```text
Principal
   |
   | WriteDacl
   v
Object
```

This can allow modification of the object's access control list.

This is often a high-impact relationship because new permissions may be introduced.

---

# WriteOwner

```text
Principal
   |
   | WriteOwner
   v
Object
```

Ownership changes can affect the ability to alter permissions.

Treat validation carefully because changing ownership modifies directory state.

---

# ForceChangePassword

```text
Principal
   |
   | ForceChangePassword
   v
User
```

This indicates a password reset relationship.

Do not validate against real users without explicit approval because it can disrupt access and business operations.

---

# DCSync Relationships

BloodHound can identify principals with directory replication rights.

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

These relationships may indicate DCSync capability.

Treat them as high impact.

Validation should be explicitly authorised.

---

# Delegation

BloodHound can help identify:

```text
Unconstrained delegation
Constrained delegation
Resource-Based Constrained Delegation
```

Graph relationships should then be analysed together with:

```text
SPNs
Accounts
Computers
Privileges
Protocol transition
S4U configuration
```

---

# RBCD

Resource-Based Constrained Delegation relationships may appear as paths involving control over:

```text
Computer objects
msDS-AllowedToActOnBehalfOfOtherIdentity
```

BloodHound can help reveal who controls the objects involved.

Detailed analysis belongs in:

```text
active-directory/rbcd.md
```

---

# Group Policy

BloodHound models:

```text
OU
 |
 v
GPO
 |
 v
Computers / Users
```

and potentially permissions over the GPO itself.

Interesting questions include:

```text
Who can modify the GPO?

Where is the GPO linked?

Which computers receive it?

Which users receive it?

Can a low-privilege identity influence it?
```

---

# AD CS

Modern BloodHound collection includes Active Directory Certificate Services relationships.

This can help identify relationships involving:

```text
Certificate Authorities
Certificate Templates
Enrollment permissions
Template permissions
Certificate services configuration
```

BloodHound should complement, not replace, dedicated AD CS analysis.

Use tools such as Certipy where detailed certificate-service enumeration is required.

---

# Trusts

BloodHound can model trust relationships between domains.

```text
Domain A
   |
   | Trust
   v
Domain B
```

Analyse:

```text
Direction
Transitivity
Trust type
SID filtering
Selective authentication
Cross-domain group membership
Cross-domain ACLs
```

---

# High-Value Targets

High-value objects commonly include:

```text
Domain Admins
Enterprise Admins
Domain Controllers
Tier-0 systems
Certificate Authorities
Privileged service accounts
Identity management infrastructure
```

But environment-specific critical systems may be equally important.

Do not rely solely on BloodHound's default high-value marking.

---

# Owned Principals

When a credential or identity has been confirmed under the assessment scope, mark it appropriately in BloodHound.

Conceptually:

```text
Known Controlled Identity
        |
        v
Mark as Owned
        |
        v
Analyse Outbound Paths
```

This helps answer:

```text
What can I reach from here?
```

---

# Re-Analyse After New Access

```text
New Credential
      |
      v
Mark Owned
      |
      v
Search Outbound Paths
      |
      v
New Relationships
      |
      v
Validate
```

---

# Shortest Paths

Shortest paths can be useful for triage.

```text
Owned User
    |
    v
Shortest Path
    |
    v
High Value Target
```

However:

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

A longer path may be more realistic or less disruptive.

---

# Path Prioritisation

Evaluate paths using:

```text
Path length
Required privileges
Operational impact
Detection likelihood
Credential requirements
Network reachability
State changes
Business risk
Rules of engagement
```

A useful model:

```text
Candidate Path
      |
      v
Technically Possible?
      |
      v
Reachable?
      |
      v
Credentials Available?
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

# Neo4j

BloodHound historically used Neo4j directly as its graph database, and legacy BloodHound deployments are often encountered with Neo4j.

This remains relevant when:

```text
Using legacy BloodHound

Reviewing older assessment environments

Working with existing Neo4j databases

Performing custom Cypher analysis
```

Conceptually:

```text
BloodHound Data
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

BloodHound CE architecture has evolved beyond the older "BloodHound desktop application + manually managed Neo4j" model.

Do not assume modern BloodHound CE installation instructions are identical to legacy BloodHound.

---

# Cypher

Cypher is a graph query language associated with Neo4j and graph-based BloodHound analysis.

Conceptually:

```cypher
MATCH (n)
RETURN n
LIMIT 10
```

This returns graph nodes.

---

# Find Users

Example conceptual query:

```cypher
MATCH (u:User)
RETURN u
LIMIT 25
```

---

# Find Computers

```cypher
MATCH (c:Computer)
RETURN c
LIMIT 25
```

---

# Find Groups

```cypher
MATCH (g:Group)
RETURN g
LIMIT 25
```

---

# Find Domain Admin Members

A conceptual relationship query may look like:

```cypher
MATCH (u)-[:MemberOf*1..]->(g:Group)
WHERE g.name CONTAINS 'DOMAIN ADMINS'
RETURN u,g
```

Schema and query behaviour can vary between BloodHound versions.

Validate queries against the installed version.

---

# Find Administrative Relationships

Conceptually:

```cypher
MATCH (u:User)-[:AdminTo]->(c:Computer)
RETURN u,c
```

---

# Find Sessions

Conceptually:

```cypher
MATCH (u:User)-[:HasSession]->(c:Computer)
RETURN u,c
```

---

# Custom Queries

Custom graph queries are valuable when investigating:

```text
Specific groups
Specific users
Specific servers
Delegation
ACL relationships
Cross-domain relationships
Privileged sessions
Certificate services
```

Do not rely only on pre-built queries.

---

# BloodBash

BloodBash is an open-source offline analyser for SharpHound and AzureHound data.

It is useful when you want to:

```text
Analyse SharpHound data quickly

Avoid running a BloodHound server

Avoid maintaining Neo4j

Perform offline triage

Analyse collected JSON or ZIP files

Generate prioritised findings

Inspect attack paths from the terminal
```

Conceptually:

```text
SharpHound
    |
    v
JSON / ZIP
    |
    v
BloodBash
    |
    v
Offline Graph
    |
    v
Prioritised Analysis
```

No BloodHound UI or Neo4j server is required.

---

# BloodBash Installation

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

# BloodBash Standalone Binary

BloodBash also provides standalone binaries.

After obtaining the appropriate binary from the official releases:

```bash
chmod +x bloodbash-linux-x64
```

Run:

```bash
./bloodbash-linux-x64 ./sharpout
```

---

# BloodBash Quick Analysis

Given a directory containing SharpHound output:

```bash
bloodbash ./sharpout
```

The default workflow performs quick-win analysis.

Equivalent:

```bash
bloodbash ./sharpout --quick-wins
```

---

# BloodBash ZIP Analysis

```bash
bloodbash ./collection.zip --quick-wins
```

This makes BloodBash particularly useful immediately after a collection.

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

This provides an interactive analysis workflow.

---

# BloodBash Owned User Analysis

If a user has been obtained during an authorised assessment:

```bash
bloodbash ./sharpout \
    --from-user alice \
    --from-user-export
```

Conceptually:

```text
Owned User
    |
    v
BloodBash
    |
    v
Outbound Relationships
    |
    v
Potential Paths
```

---

# BloodBash Merge Collections

Multiple collections can be merged.

```bash
bloodbash ./lowpriv.zip \
    --merge ./additional.zip \
    --all \
    --fast
```

This is useful when:

```text
New privileges produce better collection

Multiple domains are collected

Collection occurs at different stages

Different network segments are assessed
```

---

# BloodBash Domain Filtering

```bash
bloodbash ./sharpout \
    --all \
    --domain EXAMPLE.LOCAL
```

Useful in multi-domain datasets.

---

# BloodBash Inspection

BloodBash supports focused node inspection.

Conceptually:

```bash
bloodbash ./sharpout \
    --inspect <NODE>
```

This can help understand:

```text
Properties
Inbound edges
Outbound edges
Relationships
```

---

# BloodBash Path Analysis

BloodBash supports path-oriented analysis including:

```text
Paths from owned principals
Paths to high-value targets
Arbitrary source-to-target paths
Indirect relationships
```

Use:

```bash
bloodbash --help
```

and:

```bash
bloodbash --help-advanced
```

for the current syntax.

---

# BloodBash Reporting

BloodBash can export findings into several formats.

Supported formats include:

```text
Markdown
JSON
HTML
CSV
YAML
```

This can be useful for:

```text
Assessment evidence
Triage
Review
Reporting preparation
Comparing collections
```

Review generated reports before including information in a client deliverable.

---

# BloodBash vs BloodHound

```text
Need visual interactive graph?
        |
        +--> BloodHound

Need full attack-path exploration?
        |
        +--> BloodHound

Need fast terminal triage?
        |
        +--> BloodBash

Need offline analysis?
        |
        +--> BloodBash

Need Neo4j / custom graph environment?
        |
        +--> Legacy BloodHound / Neo4j

Need quick analysis without server setup?
        |
        +--> BloodBash
```

These tools can complement each other.

---

# BloodBash Workflow

```text
SharpHound / BloodHound.py / NetExec
                 |
                 v
             JSON / ZIP
                 |
         +-------+-------+
         |               |
         v               v
    BloodHound        BloodBash
         |               |
         v               v
    Visual Graph      CLI Triage
         |               |
         +-------+-------+
                 |
                 v
            Investigation
```

---

# Collection Completeness

Before trusting the graph, ask:

```text
Which domains were collected?

Which OUs were included?

Were ACLs collected?

Were sessions collected?

Were local groups collected?

Were trusts collected?

Was AD CS collected?

Were inaccessible hosts skipped?

Was collection performed with low privilege?

How old is the data?
```

Incomplete data can produce misleading conclusions.

---

# Collection Health

Keep a record of:

```text
Collection date
Collector
Collector version
Collection methods
Identity used
Domain
DNS server
Failed hosts
Excluded hosts
Scope restrictions
```

This information makes graph interpretation more reliable.

---

# BloodHound Is a Snapshot

Treat BloodHound data as:

```text
Environment
     |
     v
Collection Time
     |
     v
Snapshot
```

not:

```text
Permanent Truth
```

Relationships can change.

Especially:

```text
Sessions
Group membership
ACLs
Computer availability
Trust configuration
Certificates
Delegation
```

---

# Re-Collection

Re-collect when:

```text
New credentials are obtained

New privileges are obtained

A new subnet becomes reachable

A new domain is discovered

A trust is discovered

Previously inaccessible computers become reachable

Assessment conditions change
```

---

# Layered Collection Strategy

A practical strategy is:

```text
Phase 1
   |
   v
Directory Collection
   |
   v
Analyse
   |
   v
Identify Interesting Systems
   |
   v
Phase 2
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

This can reduce unnecessary endpoint activity.

---

# BloodHound and NetExec Workflow

```text
nxc smb <range>
      |
      v
Discover Windows Systems
      |
      v
Validate Approved Credential
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
BloodHound / BloodBash
      |
      v
Interesting Relationships
      |
      v
NetExec / Impacket / PowerView
      |
      v
Focused Validation
```

---

# BloodHound and Impacket

BloodHound identifies relationships.

Impacket can help investigate some of the underlying protocols.

```text
BloodHound
    |
    v
Interesting Edge
    |
    +--> Kerberos
    |
    +--> SMB
    |
    +--> RPC
    |
    +--> Delegation
    |
    v
Impacket
```

Do not automatically execute an Impacket operation simply because BloodHound displays an edge.

---

# BloodHound and PowerView

PowerView is useful for independently validating directory relationships.

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
Verify Directory Permission
```

This is particularly useful for:

```text
ACLs
Group memberships
Delegation
Object ownership
GPO permissions
```

---

# BloodHound and Certipy

For AD CS:

```text
BloodHound
    |
    v
Certificate Relationship
    |
    v
Certipy
    |
    v
Detailed AD CS Analysis
```

BloodHound provides graph context.

Certipy provides specialised certificate-services analysis.

---

# BloodHound and Responder

Responder and BloodHound solve different problems.

```text
Responder
    |
    v
Authentication Behaviour

BloodHound
    |
    v
Identity Relationships
```

Information obtained during one part of an assessment may influence analysis in the other, but they should not be treated as interchangeable tools.

---

# BloodHound and Pivoting

When BloodHound collection is performed through a pivot, verify:

```text
Routing
DNS
LDAP
SMB
Kerberos
RPC
Dynamic RPC
```

before assuming collection will work.

---

# TUN-Based Pivot

A routed pivot can simplify BloodHound.py or NetExec collection.

```text
Kali
 |
 v
TUN
 |
 v
Pivot
 |
 v
Internal Network
 |
 +--> LDAP
 +--> SMB
 +--> Kerberos
```

DNS still needs to resolve the target domain correctly.

---

# Evidence

Create:

```bash
mkdir -p evidence/bloodhound/{collection,analysis,queries,exports,screenshots}
```

Suggested structure:

```text
evidence/
└── bloodhound/
    ├── collection/
    ├── analysis/
    ├── queries/
    ├── exports/
    └── screenshots/
```

---

# Preserve Original Collection

Keep the original collector output unchanged.

```text
collection/
├── original/
└── working/
```

Do analysis against a copy where practical.

This helps preserve evidence integrity.

---

# Sensitive Data

BloodHound data can reveal:

```text
Usernames
Computer names
Group memberships
Administrative relationships
Sessions
Domain trusts
ACLs
Certificate infrastructure
Network structure
Privileged accounts
Potential attack paths
```

Treat collection files as sensitive assessment data.

---

# Reporting

Do not report:

```text
BloodHound found a path.
```

Report the underlying security condition.

For example:

```text
A standard domain user possessed permission to modify
membership of a group that provides administrative access
to multiple application servers.
```

BloodHound is evidence supporting the finding.

It is not the finding itself.

---

# Reporting Attack Paths

A useful structure is:

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
      |
      v
Security Impact
```

Document:

```text
Affected objects
Required privileges
Prerequisites
Evidence
Validation performed
Potential impact
Recommended remediation
```

---

# Reporting Screenshots

A BloodHound screenshot should clearly show:

```text
Starting principal
Relationship edges
Target object
Relevant path
```

Avoid enormous graphs with hundreds of unrelated nodes.

A small focused graph is better evidence.

---

# Detection

BloodHound itself is primarily an analysis platform.

Collection is what normally produces observable activity.

Potential telemetry includes:

```text
LDAP queries
SMB connections
RPC connections
Session enumeration
Local group enumeration
Registry queries
DNS requests
Kerberos requests
Authentication events
Process execution
Endpoint security alerts
```

---

# Detecting SharpHound

Potential indicators include:

```text
SharpHound process execution
Large LDAP enumeration
Repeated host connections
Session enumeration
Local group enumeration
Known binary signatures
Command-line telemetry
EDR detections
```

However, defenders should avoid relying solely on binary names or hashes.

Behavioural detection is more resilient.

---

# Detecting Linux-Based Collection

BloodHound.py and NetExec may produce patterns such as:

```text
LDAP enumeration from unusual systems
SMB enumeration
Kerberos authentication
Repeated connections across many hosts
Directory queries from non-standard management systems
```

Correlate:

```text
Source host
Identity
Volume
Protocols
Targets
Time window
```

---

# Detection Model

```text
Single LDAP Query
       |
       v
Usually Normal

Large Breadth
       +
Multiple Object Classes
       +
Host Enumeration
       +
Session Queries
       +
Unusual Source
       |
       v
Higher Signal
```

---

# Defensive Use

BloodHound is also valuable defensively.

Blue teams can use it to identify:

```text
Privilege escalation paths
Excessive ACL permissions
Dangerous delegation
Tiering violations
Privileged sessions
Excessive local admin rights
Weak group design
AD CS attack paths
Cross-domain exposure
```

---

# Remediation

Remediation should target the underlying relationship.

Examples:

```text
Dangerous ACL
   |
   +--> Remove unnecessary ACE

Excessive Group Membership
   |
   +--> Reduce membership

Local Admin Sprawl
   |
   +--> Remove unnecessary local admin

Privileged Sessions
   |
   +--> Improve administrative tiering

Dangerous Delegation
   |
   +--> Reconfigure delegation

AD CS Path
   |
   +--> Correct template / CA permissions

Trust Exposure
   |
   +--> Harden trust configuration
```

Do not "remediate BloodHound."

Remediate the identity relationships BloodHound reveals.

---

# Common Mistakes

## Treating Every Edge as Exploitable

Wrong:

```text
Edge exists
   =
Finding
```

Correct:

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
Assess Impact
```

---

## Using Only Shortest Path

Shortest path is useful for discovery, but not sufficient for a complete assessment.

Also investigate:

```text
ACL exposure
Delegation
Sessions
Local admin sprawl
GPO control
AD CS
Trusts
Kerberoastable privileged accounts
AS-REP candidates
RBCD
Tiering violations
```

---

## Ignoring Collection Failures

If half the environment was unreachable:

```text
Graph
  !=
Complete Environment
```

Document collection limitations.

---

## Using Old Data

An old graph may contain:

```text
Expired sessions
Removed users
Changed groups
Changed ACLs
Retired computers
Modified delegation
```

Always record collection time.

---

## Assuming BloodHound Proves Exploitation

BloodHound primarily proves:

```text
Relationship
```

not necessarily:

```text
Successful exploitation
```

---

# Troubleshooting

## No Domain Found

Check:

```bash
cat /etc/resolv.conf
```

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

# LDAP Fails

Check:

```bash
nc -vz dc01.example.local 389
```

For LDAPS:

```bash
nc -vz dc01.example.local 636
```

---

# SMB Collection Fails

Check:

```bash
nc -vz server01.example.local 445
```

Then verify:

```text
Credential
Firewall
SMB availability
Privileges
Network route
```

---

# Kerberos Fails

Check:

```bash
date
```

```bash
dig dc01.example.local
```

```bash
nc -vz dc01.example.local 88
```

Then verify:

```text
Domain
FQDN
KDC
Time
Ticket
SPN
```

---

# Missing Session Data

Possible causes:

```text
Insufficient privileges
Firewall
Endpoint unreachable
Collection method
User not currently logged on
Session collection limitations
```

Do not assume:

```text
No session edge
   =
No session exists
```

---

# Missing ACL Data

Verify:

```text
Collection method
Collector version
LDAP access
Object permissions
Collection scope
```

---

# Collector Decision Tree

```text
Need BloodHound data
        |
        v
Where are you running?
        |
    +---+---+
    |       |
 Windows   Linux
    |       |
    v       v
SharpHound BloodHound.py CE
    |       |
    |       +--> NetExec
    |
    v
Official CE Collector
        |
        v
JSON / ZIP
        |
    +---+---+
    |       |
    v       v
BloodHound BloodBash
```

---

# Analysis Decision Tree

```text
Collection Complete
        |
        v
Need visual graph?
        |
     +--+--+
     |     |
    Yes    No
     |     |
     v     v
BloodHound BloodBash
     |
     v
Mark Owned Principals
     |
     v
High-Value Targets
     |
     v
Outbound Paths
     |
     v
ACLs
     |
     v
Sessions
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
Validate Interesting Relationships
```

---

# Assessment Workflow

```text
                     BLOODHOUND WORKFLOW
                             |
                             v
                           SCOPE
                             |
                             v
                         AD CONTEXT
                             |
                  +----------+----------+
                  |                     |
                  v                     v
               Windows                Linux
                  |                     |
                  v                     v
             SharpHound          BloodHound.py CE
                                        |
                                        +--> NetExec
                  |                     |
                  +----------+----------+
                             |
                             v
                        COLLECTION
                             |
                             v
                         JSON / ZIP
                             |
                  +----------+----------+
                  |                     |
                  v                     v
             BloodHound              BloodBash
                  |                     |
                  v                     v
             Visual Graph            CLI Triage
                  |                     |
                  +----------+----------+
                             |
                             v
                         ANALYSIS
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
             ACLs         Sessions      Delegation
              |              |              |
              +--------------+--------------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
            AD CS           GPOs          Trusts
              |              |              |
              +--------------+--------------+
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
                         EVIDENCE
                             |
                             v
                          REPORT
```

---

# Assessment Checklist

## Context

```text
[ ] Scope confirmed
[ ] Domain identified
[ ] Domain Controller identified
[ ] DNS configured
[ ] Routes verified
[ ] Credential context understood
```

## Collection

```text
[ ] Collector selected
[ ] Collector version recorded
[ ] Collection methods recorded
[ ] Scope restrictions recorded
[ ] Collection time recorded
[ ] Failed hosts recorded
[ ] Original output preserved
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
[ ] Cross-domain relationships reviewed
```

## Validation

```text
[ ] Interesting edges independently verified
[ ] Network reachability confirmed
[ ] Credentials confirmed
[ ] Required privileges confirmed
[ ] State-changing actions separately authorised
[ ] Operational impact considered
```

## Evidence

```text
[ ] Collection files protected
[ ] Focused screenshots captured
[ ] Queries recorded
[ ] Starting principal recorded
[ ] Target recorded
[ ] Relationships recorded
[ ] Validation evidence recorded
```

## Reporting

```text
[ ] Underlying security condition described
[ ] Tool output not treated as the finding
[ ] Prerequisites documented
[ ] Impact documented
[ ] Remediation targets root cause
```

---

# Tool Selection

```text
Need official Windows collection?
        |
        +--> SharpHound CE

Need Linux collection?
        |
        +--> BloodHound.py CE

Already working heavily with NetExec?
        |
        +--> NetExec BloodHound ingestor

Need interactive visual graph?
        |
        +--> BloodHound CE

Need fast offline terminal analysis?
        |
        +--> BloodBash

Need specialised Kerberos/SMB/RPC validation?
        |
        +--> Impacket

Need Windows-side AD validation?
        |
        +--> PowerView

Need detailed AD CS analysis?
        |
        +--> Certipy
```

---

# Mental Model

```text
BloodHound does not create the attack path.

The relationships already exist in Active Directory.

BloodHound makes those relationships visible.
```

Therefore:

```text
BloodHound Edge
      |
      v
Understand Relationship
      |
      v
Verify Configuration
      |
      v
Determine Prerequisites
      |
      v
Assess Reachability
      |
      v
Controlled Validation
      |
      v
Impact
```

---

# Related Notes

```text
active-directory/index.md
active-directory/methodology.md
active-directory/enumeration.md
active-directory/netexec.md
active-directory/impacket.md
active-directory/powerview.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/acl-ace.md
active-directory/group-policy.md
active-directory/unconstrained-delegation.md
active-directory/constrained-delegation.md
active-directory/rbcd.md
active-directory/trusts.md
active-directory/lateral-movement.md
active-directory/pivoting.md
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

## BloodHound Community Edition Quickstart

[BloodHound Community Edition Quickstart](https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart){ target="_blank" rel="noopener noreferrer" }

## SharpHound Community Edition

[SharpHound Community Edition](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound){ target="_blank" rel="noopener noreferrer" }

## SharpHound Collection Flags

[SharpHound Collection Flags](https://bloodhound.specterops.io/collect-data/ce-collection/sharphound-flags){ target="_blank" rel="noopener noreferrer" }

## BloodHound JSON Formats

[BloodHound JSON Formats](https://bloodhound.specterops.io/integrations/bloodhound-api/json-formats){ target="_blank" rel="noopener noreferrer" }

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

# Final Model

```text
                           ACTIVE DIRECTORY
                                  |
                                  v
                              COLLECTION
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
         SharpHound        BloodHound.py CE        NetExec
              |                   |                   |
              +-------------------+-------------------+
                                  |
                                  v
                              JSON / ZIP
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
              BloodHound CE                 BloodBash
                    |                           |
                    v                           v
               Visual Graph                CLI Analysis
                    |                           |
                    +-------------+-------------+
                                  |
                                  v
                           RELATIONSHIPS
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
         Delegation             AD CS                Trusts
             |                    |                    |
             +--------------------+--------------------+
                                  |
                                  v
                           ATTACK PATHS
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

The key principle is:

```text
Collect broadly enough to understand the environment.

Analyse relationships rather than individual objects.

Treat graph edges as hypotheses that require interpretation.

Validate only what is necessary and authorised.

Re-collect when the security context changes.
```
