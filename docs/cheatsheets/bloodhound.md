---
title: BloodHound Cheatsheet
description: Detailed practical BloodHound reference for authorised Active Directory security assessments covering collection, SharpHound, NetExec, BloodHound CE, data import, graph analysis, attack paths, Cypher queries, edge interpretation, validation, false positives, evidence, remediation and retesting.
---

# BloodHound Cheatsheet

BloodHound maps relationships between Active Directory identities, computers, groups, sessions, permissions and other security objects into a graph that can be analysed for privilege and attack paths.

Instead of looking at Active Directory as isolated objects:

```text
User

Group

Computer

Session

ACL

GPO

Domain

OU
```

BloodHound focuses on the relationships between them:

```text
User
 |
 v
MemberOf
 |
 v
Group
 |
 v
AdminTo
 |
 v
Server
 |
 v
HasSession
 |
 v
Privileged User
```

This makes it particularly useful for understanding **how apparently low-privileged access can connect to more privileged systems or identities**.

The core methodology should be:

```text
Collect
   |
   v
Import
   |
   v
Verify Dataset
   |
   v
Identify Relationship
   |
   v
Understand Edge
   |
   v
Validate Preconditions
   |
   v
Confirm Real-World Access
   |
   v
Determine Impact
   |
   v
Capture Evidence
   |
   v
Remediate
   |
   v
Retest
```

!!! warning "Authorised Security Testing"
    BloodHound and its collectors should only be used in environments you are authorised to assess. Collection can generate substantial LDAP, SMB and other Active Directory traffic depending on the selected methods. Session and local-group collection can be significantly more intrusive than basic directory enumeration.


# Quick Start

A practical BloodHound workflow is:

```text
Identify Domain
      |
      v
Identify Domain Controller
      |
      v
Choose Collection Method
      |
      v
Collect Data
      |
      v
Import Data
      |
      v
Verify Import
      |
      v
Search Owned / Controlled User
      |
      v
Find Interesting Paths
      |
      v
Understand Every Edge
      |
      v
Validate Important Relationships
      |
      v
Report Root Cause
```


# What BloodHound Answers

BloodHound is particularly useful for questions such as:

```text
Which users can become administrators?

Which systems can this user administer?

Which groups indirectly grant privilege?

Where are privileged users logged on?

Which ACLs provide escalation opportunities?

Which computers expose paths to privileged identities?

Which accounts can modify sensitive groups?

Which objects have dangerous delegated permissions?

Which trust relationships create cross-domain paths?

Which principals can control another principal?
```


# What BloodHound Does Not Automatically Prove

A graph path does not automatically mean:

```text
Compromise succeeded.

The entire path is currently exploitable.

Every edge is current.

Every session still exists.

The target is online.

Network connectivity exists.

Required protocols are reachable.

EDR controls can be bypassed.

Credentials are available.

The operator has satisfied every prerequisite.
```

BloodHound identifies **relationships and potential paths**.

Important paths should be independently validated.


# BloodHound Graph Model

A simplified graph:

```text
             +------------+
             |   USER A   |
             +-----+------+
                   |
                   | MemberOf
                   v
             +------------+
             |   GROUP A  |
             +-----+------+
                   |
                   | AdminTo
                   v
             +------------+
             |   SERVER1  |
             +-----+------+
                   |
                   | HasSession
                   v
             +------------+
             |   USER B   |
             +------------+
```

BloodHound analyses both:

```text
Nodes
```

and:

```text
Edges
```


# Nodes

Common nodes include:

```text
Users

Groups

Computers

Domains

Organisational Units

Group Policy Objects

Containers

Certificate Authorities

Certificate Templates
```

Available object types depend on BloodHound version, collector and imported dataset.


# Edges

Edges describe relationships.

Examples include:

```text
MemberOf

AdminTo

HasSession

GenericAll

GenericWrite

WriteDacl

WriteOwner

AddMember

ForceChangePassword

CanRDP

CanPSRemote

ExecuteDCOM

AllowedToDelegate

AllowedToAct

Owns
```

The exact edge set depends on BloodHound version and available data.


# Edge Interpretation Model

For every interesting edge ask:

```text
1. What does the edge represent?

2. What permission or observation created it?

3. Is the source object controlled?

4. Is the destination object reachable?

5. Are additional prerequisites required?

6. Is the relationship current?

7. Can it be independently verified?

8. What security boundary does it cross?
```


# Example Environment

Examples throughout this page use:

```text
Domain:
corp.local

Domain Controller:
dc01.corp.local

DC IP:
10.10.10.10

User:
CORP\asif

Workstation:
WS01

Server:
SRV01

Privileged Group:
Domain Admins
```

These are placeholders for a controlled environment.


# BloodHound Components

A BloodHound deployment generally consists of:

```text
Collector
   |
   v
Active Directory
   |
   v
Collection Data
   |
   v
BloodHound
   |
   v
Graph Database / Application
   |
   v
Queries and Analysis
```

Collection and analysis should be considered separate phases.


# BloodHound Community Edition

BloodHound Community Edition is the modern BloodHound platform maintained by SpecterOps.

Before following older installation guides, determine whether the guide refers to:

```text
BloodHound Legacy

BloodHound Community Edition

Older Neo4j-based deployment

Current BloodHound deployment model
```

Do not mix installation instructions from different generations.


# Verify BloodHound Version

Use the version information exposed by the deployment or installation method.

Record the version in assessment evidence when graph behaviour or edge definitions matter.


# Collector Selection

Common collection approaches include:

```text
SharpHound

BloodHound.py

NetExec BloodHound collection

Other compatible collectors
```

The correct collector depends on:

```text
Operating system

Available credentials

Network position

Assessment restrictions

Required data

BloodHound version
```


# Collection Strategy

Do not immediately collect everything.

Use:

```text
Assessment Objective
       |
       v
Required Relationships
       |
       v
Minimum Collection Methods
       |
       v
Collect
       |
       v
Analyse
       |
       v
Expand Collection If Required
```


# Collection Categories

Collection may include information about:

```text
Directory objects

Group memberships

ACLs

Local administrators

Remote-management rights

Sessions

Trusts

Containers

GPO relationships

Object properties
```

Different collection methods have different network and operational footprints.


# Collection Safety

Before collecting ask:

```text
How many domain objects exist?

How many computers exist?

Will hosts be contacted directly?

Will SMB be used?

Will session enumeration occur?

Will local groups be queried?

Could endpoint security alert?

Could unavailable systems cause delays?

Is the SOC aware where required?

Do I actually need every collection method?
```


# SharpHound

SharpHound is the official BloodHound data collector for Active Directory environments.

Before using it, review the options for the installed version:

```powershell
.\SharpHound.exe --help
```

Do not rely solely on old blog posts because collection method names and behaviour can change.


# SharpHound Basic Methodology

```text
SharpHound
    |
    v
Authenticate as Current User
    |
    v
Query Active Directory
    |
    v
Collect Selected Relationships
    |
    v
Create Output
    |
    v
Import into BloodHound
```


# Check Current Identity

Before collection:

```powershell
whoami
```

Domain information:

```powershell
$env:USERDOMAIN
```

Current DNS domain:

```powershell
$env:USERDNSDOMAIN
```

This helps document which identity performed the collection.


# SharpHound Help

```powershell
.\SharpHound.exe --help
```

Review available collection methods rather than assuming an old command remains valid.


# Collection Method Selection

Conceptually:

```text
Need Basic Directory Relationships?
             |
             v
      Directory Collection
             |
             v
Need ACL Relationships?
             |
             v
        ACL Collection
             |
             v
Need Local Admin Information?
             |
             v
     Host-Based Collection
             |
             v
Need Session Information?
             |
             v
       Session Collection
```

Increase collection depth only when it supports the assessment objective.


# SharpHound Output

Collection commonly produces archive or JSON data suitable for import into BloodHound.

After collection, record:

```text
Collector version

Collection methods

Domain

Identity

Timestamp

Output filename

Number of objects if available
```


# Do Not Modify Collection Data

Preserve the original collection archive where evidence requirements justify it.

Use a copy for:

```text
Analysis

Processing

Testing

Screenshots
```


# Linux-Based Collection

When collecting from Linux, options may include:

```text
BloodHound.py

NetExec-supported BloodHound collection
```

Linux collection can be particularly useful when the assessment workstation is Kali Linux and domain credentials are available.


# BloodHound.py

Check the installed tool:

```bash
bloodhound-python -h
```

Depending on installation, the command name may differ.

Review:

```text
Domain

Username

Password

Nameserver

Domain controller

Collection methods
```

before execution.


# DNS Is Critical

Linux BloodHound collection frequently fails because of DNS configuration.

Check:

```bash
cat /etc/resolv.conf
```

Resolve the domain controller:

```bash
getent hosts dc01.corp.local
```

Query:

```bash
dig dc01.corp.local
```

Query LDAP SRV records:

```bash
dig _ldap._tcp.dc._msdcs.corp.local SRV
```

Query Kerberos:

```bash
dig _kerberos._tcp.corp.local SRV
```


# Example DNS Model

Your assessment host should ideally be able to resolve:

```text
corp.local

dc01.corp.local

srv01.corp.local

ws01.corp.local
```

Using only IP addresses can create problems for:

```text
Kerberos

LDAP discovery

SPNs

Collector domain discovery
```


# BloodHound.py Collection

Because collection flags can change, start with:

```bash
bloodhound-python -h
```

A collection command generally needs to establish:

```text
Domain

Credential

Domain controller / nameserver

Collection methods
```

Use the current tool help to build the exact command.


# NetExec BloodHound Collection

Some NetExec versions expose BloodHound collection through LDAP.

Check:

```bash
nxc ldap --help
```

Look for the installed version's BloodHound options.

Do not copy an old NetExec or CrackMapExec BloodHound command without verifying the available flags.


# NetExec Collection Workflow

```text
Domain Credential
       |
       v
Validate LDAP
       |
       v
Check nxc ldap --help
       |
       v
Select BloodHound Collection
       |
       v
Specify Correct DNS / DC
       |
       v
Collect
       |
       v
Import
       |
       v
Verify Dataset
```


# Why `--help` Matters Here

BloodHound integration has changed across:

```text
CrackMapExec

Early NetExec versions

Current NetExec releases

BloodHound Legacy

BloodHound CE
```

The stable lesson is therefore:

```text
Understand required inputs
+
Verify current syntax locally
+
Record the exact command used
```


# Importing Data

After collection, import the resulting dataset into BloodHound.

The exact interface depends on the BloodHound deployment.

After import, do **not** immediately begin analysing paths.

First verify the dataset.


# Dataset Verification

Check that expected object categories exist.

For example:

```text
Users

Groups

Computers

Domain

OUs

GPOs
```

Then check relationships such as:

```text
MemberOf

AdminTo

ACL edges

Sessions
```

where those collection methods were expected.


# Why Dataset Verification Matters

Suppose BloodHound shows:

```text
0 HasSession relationships
```

This could mean:

```text
No sessions existed.
```

But it could also mean:

```text
Session collection was not performed.

Hosts were unreachable.

SMB was blocked.

Collector lacked permissions.

Collection failed.

Endpoint controls interfered.

Data was not imported correctly.
```

Therefore:

```text
No Edge
```

does not always mean:

```text
No Relationship
```


# Dataset Completeness Model

```text
Graph Result
    |
    v
Was Relevant Data Collected?
    |
   / \
 No   Yes
 |     |
 v     v
Cannot  Analyse
Conclude
```


# Record Collection Metadata

For every dataset record:

```text
Collector:
SharpHound

Collector Version:
<version>

Collection Date:
<timestamp>

Collection Identity:
CORP\asif

Domain:
corp.local

Collection Methods:
<methods used>

Known Limitations:
<unreachable hosts / blocked protocols / permissions>
```


# Search for a User

In BloodHound, begin with a principal you actually control or are authorised to assess.

Example:

```text
ASIF@CORP.LOCAL
```

Review:

```text
Group memberships

Outbound control

Local administrative relationships

Remote-management rights

Sessions

Object permissions
```


# Marking Owned Principals

Where the interface supports ownership marking, mark only identities actually controlled during the assessment.

Do not mark:

```text
Hypothetical users

Unverified credentials

Accounts you merely discovered
```

as owned.


# Owned vs Compromised

A useful assessment distinction:

```text
Discovered
```

means:

```text
Account exists.
```

```text
Credential Found
```

means:

```text
Potential authentication material exists.
```

```text
Owned
```

should mean:

```text
Control has been established within the authorised assessment.
```


# Search for Domain Admins

A useful high-value group is:

```text
DOMAIN ADMINS@CORP.LOCAL
```

But do not focus exclusively on Domain Admin.

Other sensitive groups may include:

```text
Enterprise Admins

Administrators

Account Operators

Backup Operators

Server administration groups

Virtualisation administrators

Application administrators

PKI administrators

Custom delegated groups
```


# Shortest Paths

One of BloodHound's most useful concepts is:

```text
Shortest Path
```

For example:

```text
Owned User
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
Domain Admin
```


# Do Not Blindly Trust Shortest Path

The shortest graph path is not necessarily:

```text
The easiest path

The safest path

The most reliable path

The least detectable path

The currently exploitable path
```

A longer path may be more realistic.


# Path Validation Model

For a path:

```text
A -> B -> C -> D
```

validate:

```text
A -> B
```

then:

```text
B -> C
```

then:

```text
C -> D
```

Do not jump directly from:

```text
A
```

to:

```text
D
```

in the report.


# Worked Example

Assume BloodHound identifies:

```text
ASIF@CORP.LOCAL
       |
       | MemberOf
       v
HELPDESK@CORP.LOCAL
       |
       | GenericAll
       v
SERVER-ADMINS@CORP.LOCAL
       |
       | AdminTo
       v
SRV01.CORP.LOCAL
```

This is an interesting path.

Now interpret each edge.


# Step 1 - MemberOf

```text
ASIF
 |
 | MemberOf
 v
HELPDESK
```

This means the user is a member of the Helpdesk group.

Verify with directory tooling where necessary.

From Windows:

```powershell
whoami /groups
```

or appropriate Active Directory queries.

The important question:

```text
Is this membership current and expected?
```


# Step 2 - GenericAll

```text
HELPDESK
   |
   | GenericAll
   v
SERVER-ADMINS
```

This is much more security relevant.

It indicates broad control over the destination object in the graph model.

Questions:

```text
What object grants the permission?

Is it direct or inherited?

Which ACE provides it?

Is Helpdesk supposed to manage this group?

Can group membership actually be changed?

Are protected-object behaviours relevant?
```


# Step 3 - AdminTo

```text
SERVER-ADMINS
      |
      | AdminTo
      v
SRV01
```

This indicates the group has administrative control over the computer according to collected data.

Validate:

```text
Is SRV01 online?

Is the group still a local administrator?

Which mechanism grants access?

GPO?

Local group?

Manual assignment?
```


# Worked Example Conclusion

Do **not** report:

> BloodHound says ASIF can become admin on SRV01.

Prefer:

> BloodHound identified a path from `CORP\asif` to administrative control of `SRV01` through membership of `CORP\Helpdesk`, delegated control over `CORP\Server-Admins`, and the administrative rights of `Server-Admins` on `SRV01`. Independent validation should confirm the delegated directory permission and the current local administrative assignment before the complete privilege path is treated as confirmed.


# Common Edge - MemberOf

```text
USER
 |
 | MemberOf
 v
GROUP
```

Meaning:

```text
The source principal is a member of the destination group.
```

Security significance depends on the group's privileges.


# Nested Group Membership

Example:

```text
ASIF
 |
 v
HELPDESK
 |
 v
IT-USERS
 |
 v
SERVER-OPERATORS
```

Nested groups can make effective privileges difficult to identify manually.

BloodHound is particularly useful for exposing these chains.


# Common Edge - AdminTo

```text
USER/GROUP
     |
     | AdminTo
     v
COMPUTER
```

Meaning:

```text
The principal has administrative-level rights over the computer
according to the collected relationship.
```

Validate the current local group or policy configuration where the edge is important.


# AdminTo Does Not Mean Online

A computer object may be:

```text
Offline

Decommissioned

Firewalled

Unreachable

Stale
```

BloodHound describes the relationship represented by the dataset, not necessarily current network reachability.


# Common Edge - HasSession

```text
COMPUTER
   |
   | HasSession
   v
USER
```

This indicates the collector observed a session relationship.

Session data is especially time-sensitive.


# Session Data Can Become Stale Quickly

A session observed at:

```text
09:00
```

may not exist at:

```text
15:00
```

Always record:

```text
Collection timestamp

Session collection method

Host

User
```


# Session Edge Interpretation

A session relationship can be security relevant when:

```text
You control the computer
+
A privileged user has a session
```

But additional questions remain:

```text
Can credential material actually be accessed?

What protections exist?

Is Credential Guard enabled?

Is the session still active?

What privilege does the user hold?
```


# Common Edge - GenericAll

```text
PRINCIPAL
    |
    | GenericAll
    v
OBJECT
```

`GenericAll` generally represents broad control over the destination object.

The practical impact depends heavily on object type.


# GenericAll Over User

Potential implications may include account-control operations depending on effective permissions and environment configuration.

Validate the actual ACE and allowed operations before reporting a specific impact.


# GenericAll Over Group

Potentially relevant to group membership management.

Questions:

```text
Can the controlled principal modify membership?

Is the target group privileged?

Is the permission inherited?

Is the object protected?

Would modification cross a security boundary?
```


# GenericAll Over Computer

Potential implications differ from user/group objects.

Do not apply a generic "GenericAll exploit" without understanding the destination object's semantics.


# Common Edge - GenericWrite

```text
PRINCIPAL
    |
    | GenericWrite
    v
OBJECT
```

This indicates write access to certain attributes of the destination object.

The security consequence depends on:

```text
Object type

Writable attributes

Existing configuration

Effective permissions
```


# Common Edge - WriteDacl

```text
PRINCIPAL
    |
    | WriteDacl
    v
OBJECT
```

This indicates the principal can modify the object's discretionary access-control list.

This can be highly security relevant because permissions may potentially be delegated to another principal.


# WriteDacl Validation

Before reporting:

```text
Confirm the ACE.

Confirm effective permission.

Identify target object.

Determine whether the permission is inherited.

Determine whether changing the DACL would create meaningful control.
```


# Common Edge - WriteOwner

```text
PRINCIPAL
    |
    | WriteOwner
    v
OBJECT
```

Ownership can influence an object's security descriptor.

Again, the important issue is the resulting security control, not simply the edge label.


# Common Edge - Owns

```text
PRINCIPAL
    |
    | Owns
    v
OBJECT
```

Ownership should be analysed together with:

```text
DACL

Object type

Inheritance

Effective rights
```


# Common Edge - AddMember

```text
PRINCIPAL
    |
    | AddMember
    v
GROUP
```

This can indicate the ability to add members to a group.

If the destination is privileged, this may create a direct privilege-escalation path.


# AddMember Validation

Confirm:

```text
Exact group

Exact source principal

Permission source

Inheritance

Current membership-management controls

Privilege granted by the group
```


# Common Edge - ForceChangePassword

```text
PRINCIPAL
    |
    | ForceChangePassword
    v
USER
```

This indicates a password-management relationship.

Security significance depends on:

```text
Target account privilege

Whether the permission is expected

Operational consequences

Identity protections
```


# Common Edge - CanRDP

```text
PRINCIPAL
    |
    | CanRDP
    v
COMPUTER
```

This indicates remote desktop rights represented in the graph.

It does not automatically mean:

```text
RDP is reachable.

Interactive logon will succeed.

The user is administrator.
```


# Validate RDP Relationship

Check:

```text
Network reachability

RDP service

Authentication

Logon rights

NLA

Firewall

Account restrictions
```


# Common Edge - CanPSRemote

```text
PRINCIPAL
    |
    | CanPSRemote
    v
COMPUTER
```

This indicates PowerShell remoting/WinRM-related access.

Validate:

```text
WinRM reachable?

Account authorised?

Which group grants access?

Administrative or non-administrative session?
```


# Common Edge - ExecuteDCOM

```text
PRINCIPAL
    |
    | ExecuteDCOM
    v
COMPUTER
```

This indicates a DCOM-related remote execution relationship.

Validate:

```text
RPC reachability

DCOM configuration

Account permission

Firewall

Target availability
```

See [DCOM](../active-directory/dcom.md).


# Delegation Edges

BloodHound can identify delegation relationships including configurations related to:

```text
Unconstrained Delegation

Constrained Delegation

Resource-Based Constrained Delegation
```

These relationships require careful Kerberos interpretation.

See:

- [Unconstrained Delegation](../active-directory/unconstrained-delegation.md)
- [Constrained Delegation](../active-directory/constrained-delegation.md)
- [RBCD](../active-directory/rbcd.md)
- [S4U](../active-directory/s4u.md)


# AllowedToDelegate

Conceptually:

```text
ACCOUNT
   |
   | AllowedToDelegate
   v
SERVICE
```

Do not treat the edge as a complete exploitation path without understanding:

```text
Delegation type

Controlled account

SPN

Target service

Kerberos requirements

Account flags
```


# AllowedToAct

This relationship is relevant to resource-based constrained delegation.

Again:

```text
Graph Edge
   !=
Complete Exploit
```

Validate the actual directory configuration before drawing conclusions.


# ACL Analysis

ACL edges are among the most valuable BloodHound relationships.

Examples:

```text
GenericAll

GenericWrite

WriteDacl

WriteOwner

AddMember

ForceChangePassword
```

Use BloodHound to locate them, then independently inspect the underlying directory permission for important findings.


# ACL Validation Workflow

```text
BloodHound Edge
      |
      v
Identify Source
      |
      v
Identify Destination
      |
      v
Identify Permission
      |
      v
Determine Direct / Inherited
      |
      v
Inspect Actual ACE
      |
      v
Determine Effective Rights
      |
      v
Determine Security Consequence
```


# ACL False Positives

Potential reasons an apparent path may not produce the expected outcome:

```text
Stale collection

Permission inherited differently than expected

Protected object behaviour

Permission removed after collection

Object disabled

Target group no longer privileged

Application-specific controls

Collector interpretation differs from current state
```


# Group Policy Relationships

BloodHound may expose relationships involving:

```text
GPOs

OUs

Computers

Users

Groups
```

GPO-related paths can be highly significant because a single GPO may affect many systems.


# GPO Analysis Questions

Ask:

```text
Who can modify the GPO?

Where is it linked?

Which systems/users receive it?

Is inheritance blocked?

Are security filters present?

Is the GPO actually applied?

What privilege would modification provide?
```


# Do Not Assume Linked Means Applied

A GPO relationship may be affected by:

```text
Security filtering

WMI filtering

Inheritance

Enforced links

Blocked inheritance

Object location
```

Validate effective application where it matters.


# Computer Analysis

For an interesting computer review:

```text
Local administrators

Inbound administrative relationships

Outbound relationships

Sessions

Remote-management rights

Operating system

Group memberships

GPO relationships
```


# High-Value Computers

Do not limit analysis to domain controllers.

High-value systems may include:

```text
Certificate authorities

SCCM infrastructure

Backup servers

Virtualisation hosts

Identity-management servers

Jump hosts

Management servers

Database servers

Deployment systems

Monitoring systems
```


# User Analysis

For an interesting user review:

```text
Group memberships

Outbound object control

Inbound control

Sessions

SPNs

Delegation

Administrative relationships

Password-related properties

Certificate relationships
```


# Group Analysis

For an interesting group:

```text
Direct members

Nested members

Object control

Systems administered

GPO rights

Delegated directory rights

Inbound control
```


# Domain Analysis

Review:

```text
Domain trusts

High-value groups

Domain controllers

Privilege paths

ACL delegation

GPO relationships

Certificate services

Administrative tiers
```


# Trust Analysis

BloodHound can help visualise trust relationships between domains.

Trust alone does not automatically create a privilege path.

Analyse:

```text
Trust direction

Trust type

Transitivity

SID filtering

Selective authentication

Cross-domain group memberships

Actual privileged relationships
```


# Path to Domain Admin

A common query objective is:

```text
Owned Principal
      |
      v
Shortest Path
      |
      v
Domain Admin
```

This is useful, but not sufficient by itself.


# Better Question

Instead of only asking:

> How do I get Domain Admin?

also ask:

```text
Which security control failed?

Why can this low-privileged principal control this object?

Which delegation created the path?

Which group assignment is excessive?

Which system creates credential exposure?

How can the organisation break the path?
```


# Path Breaking

BloodHound is valuable defensively because an attack path can often be broken at several locations.

Example:

```text
USER
 |
 v
HELPDESK
 |
 v
SERVER-ADMINS
 |
 v
SRV01
 |
 v
PRIVILEGED SESSION
```

Potential remediation points:

```text
Remove unnecessary Helpdesk membership

Remove excessive ACL over Server-Admins

Remove unnecessary Server-Admins local admin

Prevent privileged sessions on SRV01
```


# Attack Path Choke Points

A choke point is a relationship that appears in many attack paths.

Examples:

```text
Over-privileged group

Management server

Shared administrator account

Dangerous ACL

Tier-crossing system

GPO

Certificate template
```

These can be higher remediation priorities than fixing individual paths one by one.


# Cypher Queries

BloodHound uses graph queries for advanced analysis.

The exact query language and supported schema can differ between BloodHound generations.

Verify the current BloodHound documentation before relying on old query collections.


# Basic Cypher Concept

A conceptual graph query looks for:

```text
Node
 |
 v
Relationship
 |
 v
Node
```

Example conceptual pattern:

```cypher
MATCH (u:User)-[:MemberOf]->(g:Group)
RETURN u, g
```


# Find Users

```cypher
MATCH (u:User)
RETURN u
LIMIT 25
```

Use this as a simple graph exploration example where supported by the deployment.


# Find Groups

```cypher
MATCH (g:Group)
RETURN g
LIMIT 25
```


# Find Computers

```cypher
MATCH (c:Computer)
RETURN c
LIMIT 25
```


# Membership Relationships

```cypher
MATCH (u:User)-[r:MemberOf]->(g:Group)
RETURN u, r, g
LIMIT 50
```

This helps visualise direct membership relationships.


# GenericAll Relationships

```cypher
MATCH (a)-[r:GenericAll]->(b)
RETURN a, r, b
LIMIT 50
```

Do not assume every returned relationship is exploitable without validating object type and current permissions.


# GenericWrite Relationships

```cypher
MATCH (a)-[r:GenericWrite]->(b)
RETURN a, r, b
LIMIT 50
```


# WriteDacl Relationships

```cypher
MATCH (a)-[r:WriteDacl]->(b)
RETURN a, r, b
LIMIT 50
```


# WriteOwner Relationships

```cypher
MATCH (a)-[r:WriteOwner]->(b)
RETURN a, r, b
LIMIT 50
```


# Administrative Relationships

A conceptual query:

```cypher
MATCH (a)-[r:AdminTo]->(c:Computer)
RETURN a, r, c
LIMIT 50
```


# Session Relationships

A conceptual query:

```cypher
MATCH (c:Computer)-[r:HasSession]->(u:User)
RETURN c, r, u
LIMIT 50
```

Remember that session data is highly time-sensitive.


# Query Results Are Leads

The correct process is:

```text
Cypher Result
    |
    v
Interesting Relationship
    |
    v
Inspect Object
    |
    v
Inspect Edge
    |
    v
Validate Outside BloodHound
    |
    v
Determine Impact
```


# Built-In Queries

Depending on BloodHound version, built-in analysis may provide queries for areas such as:

```text
Shortest paths to high-value targets

Domain Admin relationships

Kerberoastable accounts

AS-REP roastable accounts

Local administrative rights

Sessions

Dangerous object control
```

Treat built-in queries as investigation starting points.


# BloodHound + NetExec Workflow

A strong combination is:

```text
BloodHound
    |
    v
ASIF AdminTo SRV01
    |
    v
NetExec
    |
    v
Validate Authentication / Admin Context
    |
    v
Confirm Relationship
```


# Example

BloodHound suggests:

```text
ASIF@CORP.LOCAL
      |
      | AdminTo
      v
SRV01.CORP.LOCAL
```

A narrow validation can then determine whether the tested account currently has administrative access to that host.

Do not test every host merely because the graph contains many relationships.


# BloodHound + Impacket Workflow

```text
BloodHound
    |
    v
Specific Protocol Relationship
    |
    v
Understand Preconditions
    |
    v
Impacket
    |
    v
Focused Validation
```

For example, a Kerberos or remote-administration relationship may justify selecting one specialised Impacket utility.

See the [Impacket Cheatsheet](impacket.md).


# BloodHound + PowerView

PowerView can be useful for independently validating directory relationships discovered in BloodHound.

Conceptually:

```text
BloodHound
    |
    v
Interesting ACL
    |
    v
PowerView / Native AD Query
    |
    v
Actual ACE
    |
    v
Interpretation
```


# BloodHound + Native PowerShell

Native Windows tooling can also verify many relationships.

Current groups:

```powershell
whoami /groups
```

Local administrators where authorised:

```powershell
Get-LocalGroupMember -Group Administrators
```

Domain information where AD tooling is available can provide additional validation.


# BloodHound + Active Directory Users and Computers

For some findings, graphical administrative tools can provide useful supporting evidence.

Examples:

```text
Group membership

OU placement

Delegation

Object properties
```

Do not rely on a single interface if the finding depends on subtle ACL behaviour.


# Data Freshness

BloodHound data is a snapshot.

It should always be associated with:

```text
Collection time
```

rather than interpreted as permanently current.


# Stale Users

Possible indicators:

```text
Disabled accounts

Old logon timestamps

Legacy service accounts

Accounts no longer used
```

A stale object can still be security relevant, but its current operational role must be verified.


# Stale Computers

Computer objects may represent:

```text
Decommissioned systems

Offline systems

Reimaged systems

Old test systems

Cloud-hosted systems no longer active
```

Validate reachability before using them in an attack-path conclusion.


# Stale Sessions

Session data should be treated as especially volatile.

```text
Collection at 10:00
```

does not prove:

```text
Session exists at 16:00
```


# Incomplete Collection

Common reasons include:

```text
DNS failure

Firewall restrictions

SMB blocked

RPC blocked

Insufficient privileges

Collector errors

EDR interference

Offline systems

Collection method not selected

Timeouts
```


# Recognising Incomplete Data

Warning signs:

```text
Very few computers

No local admin edges

No sessions

No ACL edges

Missing expected domain controllers

Missing expected groups

Collection errors
```


# Incomplete Dataset Example

Suppose the organisation has:

```text
2,500 computers
```

but BloodHound contains:

```text
183 computers
```

Do not conclude:

```text
The remaining systems have no attack paths.
```

The dataset is likely incomplete.


# Collection Coverage

Track:

```text
Expected Computers:
2500

Collected Computers:
183

Coverage:
7.3%
```

This changes the confidence level of the analysis.


# Confidence Levels

You can classify BloodHound conclusions as:

```text
Observed

Validated

Incomplete

Stale

Unconfirmed
```


# Observed

Example:

```text
BloodHound contains an AdminTo relationship between
CORP\asif and SRV01.
```


# Validated

Example:

```text
The relationship was independently confirmed against the
current local administrator configuration.
```


# Incomplete

Example:

```text
Session collection failed against a significant portion of
workstations.
```


# Stale

Example:

```text
The session was collected several hours before validation and
could no longer be reproduced.
```


# Unconfirmed

Example:

```text
The relationship could not be independently validated within
the assessment window.
```


# False Positive Example - AdminTo

BloodHound:

```text
HELPDESK
   |
   | AdminTo
   v
WS01
```

Independent validation:

```text
HELPDESK is no longer present in the local Administrators group.
```

Possible explanation:

```text
Collection predates a policy change.
```

Conclusion:

```text
Do not report current administrative access.
```


# False Positive Example - Session

BloodHound:

```text
SRV01
 |
 | HasSession
 v
DOMAIN ADMIN
```

Later validation:

```text
Session no longer exists.
```

Conclusion:

```text
The session was observed during collection but was transient.
```


# Alternative Explanation Example - Missing Sessions

BloodHound:

```text
No sessions found.
```

Collector log:

```text
Host enumeration failed because SMB was blocked.
```

Correct conclusion:

```text
Session state could not be determined.
```

Incorrect conclusion:

```text
No privileged users have sessions.
```


# Attack Path Validation

For every significant path create a table.

| Step | BloodHound Edge | Validation | Result |
|---|---|---|---|
| 1 | `ASIF -> MemberOf -> HELPDESK` | Directory membership | Confirmed |
| 2 | `HELPDESK -> GenericAll -> SERVER-ADMINS` | ACL review | Confirmed |
| 3 | `SERVER-ADMINS -> AdminTo -> SRV01` | Local admin review | Confirmed |
| 4 | `SRV01 -> HasSession -> ADMIN1` | Session recheck | Not confirmed |

This prevents a partially valid path from being reported as fully exploitable.


# Evidence Capture

For each important path record:

```text
Collection timestamp

Collector

Collector version

Collection methods

BloodHound version

Source principal

Destination

Path

Edges

Independent validation

Limitations
```


# Screenshot Evidence

A useful BloodHound screenshot should show:

```text
Source principal

Destination

Complete relevant path

Edge names
```

Avoid screenshots containing:

```text
Unrelated user data

Large unreadable graphs

Sensitive usernames not relevant to the finding
```


# Evidence Example

```text
Test ID:
AD-BH-004

Timestamp:
2026-09-06 16:00 UTC

Tool:
BloodHound

Collector:
SharpHound

Collection Identity:
CORP\asif

Domain:
corp.local

Source:
ASIF@CORP.LOCAL

Target:
SRV01.CORP.LOCAL

Observed Path:
ASIF
 -> MemberOf
HELPDESK
 -> GenericAll
SERVER-ADMINS
 -> AdminTo
SRV01

Validation:
Membership confirmed.
GenericAll ACE independently confirmed.
SERVER-ADMINS local administrative assignment confirmed.

Conclusion:
The tested user can influence a group that provides
administrative access to SRV01.

Limitations:
No modification was performed during validation.
```


# Reporting BloodHound Findings

Do not report:

> BloodHound found an attack path.

BloodHound is evidence and analysis tooling, not the root cause.


# Better Finding Title

Instead of:

```text
BloodHound Attack Path to Server
```

prefer:

```text
Excessive Active Directory Delegation Enables Privilege Escalation
```

or:

```text
Helpdesk Group Can Modify Privileged Server Administration Group
```


# Reporting Example

## Observation

```text
Members of the CORP\Helpdesk group have excessive directory
permissions over CORP\Server-Admins.
```

## Evidence

```text
BloodHound identified a GenericAll relationship from Helpdesk
to Server-Admins. Independent ACL review confirmed the
permission.
```

## Security Consequence

```text
Server-Admins provides administrative access to SRV01.
Consequently, compromise of a Helpdesk account could permit
unauthorised administrative access to the server.
```

## Recommendation

```text
Remove unnecessary delegated control over Server-Admins and
review other privileged groups for similar permissions.
```


# Do Not Report the Tool

Avoid:

```text
BloodHound vulnerability
```

Report:

```text
Excessive ACL

Excessive group membership

Unnecessary local administrator rights

Unsafe delegation

Privileged session exposure

Insecure GPO permissions
```

BloodHound reveals the condition.


# Remediation - ACL Paths

Review:

```text
GenericAll

GenericWrite

WriteDacl

WriteOwner

AddMember

ForceChangePassword
```

Remove permissions that are not required by the principal's operational role.


# Remediation - Group Membership

Apply:

```text
Least privilege

Role-based administration

Separate privileged identities

Regular membership review

Remove nested privilege where unnecessary
```


# Remediation - Local Administrators

Review:

```text
Domain groups in local Administrators

Legacy helpdesk access

Shared administrator groups

Application service accounts

Deployment accounts
```

Use appropriate privileged-access management.


# Remediation - Privileged Sessions

Reduce unnecessary privileged logons to lower-trust systems.

Consider:

```text
Administrative tiering

Privileged Access Workstations

Dedicated administration hosts

Remote Credential Guard where appropriate

Credential Guard

Restricted administrative workflows
```


# Remediation - GPO Control

Restrict:

```text
Who can modify GPOs

Who can modify GPO links

Who can modify related files

Who controls sensitive OUs
```


# Remediation - Delegation

Review:

```text
Unconstrained delegation

Constrained delegation

RBCD

Legacy delegation

Service-account privilege
```

Remove delegation that is no longer required.


# Retesting BloodHound Findings

A good retest verifies the root cause rather than merely importing a new graph.


# Example Retest - GenericAll

Before:

```text
HELPDESK
   |
   | GenericAll
   v
SERVER-ADMINS
```

Remediation:

```text
Excessive ACE removed.
```

Retest:

```text
1. Inspect the target object's ACL.
2. Confirm the ACE is absent.
3. Recollect relevant BloodHound ACL data.
4. Import the new dataset.
5. Confirm the edge is absent.
6. Confirm no equivalent privilege path remains.
```


# Example Retest - Local Admin

Before:

```text
HELPDESK
   |
   | AdminTo
   v
SRV01
```

Retest:

```text
1. Confirm Helpdesk is no longer a local administrator.
2. Recollect local-group information.
3. Confirm BloodHound no longer produces the edge.
4. Validate that another nested group does not recreate access.
```


# Why Edge Disappearance Is Not Enough

Suppose an edge disappears because:

```text
Collection failed.
```

That is not remediation.

Therefore:

```text
No Edge
    |
    v
Was Data Successfully Collected?
    |
   / \
 No   Yes
 |     |
 v     v
Unknown Remediation
        Candidate
```


# Retest Dataset Comparison

Track:

| Metric | Before | After |
|---|---:|---:|
| Users | 5,200 | 5,198 |
| Groups | 1,120 | 1,121 |
| Computers | 2,480 | 2,477 |
| GenericAll edges | 83 | 62 |
| WriteDacl edges | 41 | 29 |
| High-value attack paths | 17 | 5 |

Counts alone do not prove security improvement, but they can help measure changes when collection conditions are comparable.


# BloodHound for Purple Teaming

BloodHound can support purple-team exercises by helping select realistic privilege paths.

Example:

```text
BloodHound Path
      |
      v
Select One Relationship
      |
      v
Define Expected Telemetry
      |
      v
Controlled Validation
      |
      v
Blue Team Observation
      |
      v
Detection Gap
      |
      v
Remediation
```


# Purple Team Example

Path:

```text
Helpdesk User
     |
     v
Dangerous ACL
     |
     v
Server Admin Group
```

Exercise objective:

```text
Can defenders detect and investigate unauthorised modification
of a privileged Active Directory group?
```


# Detection Questions

Ask:

```text
Was the directory modification logged?

Was the initiating account identified?

Was the target object identified?

Was an alert generated?

Did the SOC understand the privilege consequence?

Could analysts reconstruct the complete path?
```


# Defensive BloodHound Analysis

Blue teams can use BloodHound to identify:

```text
Privilege concentration

Dangerous ACLs

Excessive administrative access

Tier violations

Privileged session exposure

Attack-path choke points

Overly broad delegation

High-value systems with excessive inbound control
```


# Continuous Analysis

A mature defensive workflow could be:

```text
Scheduled Collection
       |
       v
Graph Analysis
       |
       v
Identify New Privilege Relationships
       |
       v
Validate Change
       |
       v
Remediate
       |
       v
Recollect
```


# Compare Snapshots

Useful questions:

```text
Which new AdminTo edges appeared?

Which new ACL edges appeared?

Which accounts gained control over privileged groups?

Which new systems became high value?

Which attack paths disappeared?

Which privileged session patterns changed?
```


# Common BloodHound Mistakes

## Collect Everything Immediately

Problem:

```text
Unnecessary traffic and noise.
```

Better:

```text
Collect what is needed for the current objective.
```


## Assume No Edge Means No Risk

Problem:

```text
Dataset may be incomplete.
```

Better:

```text
Check collection coverage.
```


## Assume Every Path Is Exploitable

Problem:

```text
Edges may be stale or have unmet prerequisites.
```

Better:

```text
Validate important edges independently.
```


## Focus Only on Domain Admin

Problem:

```text
Other identities and systems may be equally important.
```

Better:

```text
Define organisational high-value assets.
```


## Report BloodHound Instead of Root Cause

Problem:

```text
"BloodHound found..."
```

Better:

```text
"Excessive delegated ACL..."
```


## Ignore Collection Time

Problem:

```text
Sessions and relationships may change.
```

Better:

```text
Record collection timestamps.
```


## Ignore Collector Errors

Problem:

```text
Missing data can appear as missing relationships.
```

Better:

```text
Review collector output and coverage.
```


## Use Giant Graph Screenshots

Problem:

```text
Evidence becomes unreadable.
```

Better:

```text
Capture the smallest graph that demonstrates the relationship.
```


# Troubleshooting

# BloodHound Contains No Data

Check:

```text
Was import successful?

Was the correct archive imported?

Did collection complete?

Did the collector produce objects?

Are filters hiding results?
```


# Users Exist but Computers Are Missing

Possible causes:

```text
Collection method

LDAP query limitations

Domain selection

Collector failure

Import issue
```


# Computers Exist but No Sessions

Possible causes:

```text
Session collection not selected

SMB blocked

Hosts unreachable

Permission restrictions

No sessions observed

Collection errors
```

Do not assume the last explanation without checking the others.


# No AdminTo Edges

Possible causes:

```text
Local-group collection not performed

Hosts unreachable

Permissions insufficient

Firewall

Collector errors

No such relationships
```


# Linux Collector Cannot Find Domain

Check:

```bash
cat /etc/resolv.conf
```

```bash
dig corp.local
```

```bash
dig _ldap._tcp.dc._msdcs.corp.local SRV
```

```bash
getent hosts dc01.corp.local
```


# Kerberos Errors During Collection

Check:

```bash
date
```

```bash
klist
```

```bash
echo "$KRB5CCNAME"
```

and verify DNS.


# Collection Is Very Slow

Possible reasons:

```text
Large domain

Unreachable hosts

Timeouts

Session collection

Local-group enumeration

Network filtering

DNS delays
```

Reduce collection scope if appropriate rather than repeatedly restarting broad collection.


# Collector Produces Errors for Some Hosts

Record them.

Example:

```text
Total Computers:
2000

Successfully Contacted:
1480

Failed:
520
```

This is important context for the confidence of host-level analysis.


# Graph Looks Different After New Collection

Possible reasons:

```text
Environment changed

Sessions changed

Groups changed

Permissions changed

Different collection methods used

Different collector version

Different scope

Previous data remained in database
```

Make sure snapshot comparisons use comparable collection conditions.


# BloodHound Assessment Checklist

## Preparation

- [ ] Assessment scope confirmed
- [ ] Domain identified
- [ ] Domain controller identified
- [ ] Collection identity recorded
- [ ] Collector selected
- [ ] Collector version recorded
- [ ] BloodHound version recorded
- [ ] DNS verified
- [ ] Kerberos time checked where relevant
- [ ] Collection methods understood
- [ ] Operational impact considered

## Collection

- [ ] Minimum required collection selected
- [ ] Directory data collected
- [ ] ACL data collected where required
- [ ] Local-group data collected where required
- [ ] Session data collected only where required
- [ ] Collector errors reviewed
- [ ] Output preserved
- [ ] Timestamp recorded

## Import

- [ ] Correct dataset imported
- [ ] Users present
- [ ] Groups present
- [ ] Computers present
- [ ] Domain present
- [ ] Expected edge types present
- [ ] Import errors reviewed

## Dataset Quality

- [ ] Expected object count considered
- [ ] Computer coverage considered
- [ ] Session coverage considered
- [ ] Host failures recorded
- [ ] Missing edges not automatically interpreted as absence
- [ ] Collection limitations documented

## User Analysis

- [ ] Owned users marked accurately
- [ ] Group memberships reviewed
- [ ] Outbound control reviewed
- [ ] Administrative rights reviewed
- [ ] Sessions reviewed
- [ ] Delegation reviewed
- [ ] SPNs considered where relevant

## Group Analysis

- [ ] Privileged groups identified
- [ ] Nested membership reviewed
- [ ] Inbound control reviewed
- [ ] Outbound control reviewed
- [ ] Administrative relationships reviewed
- [ ] Delegated permissions reviewed

## Computer Analysis

- [ ] High-value computers identified
- [ ] Local admin relationships reviewed
- [ ] Sessions reviewed
- [ ] Remote-management rights reviewed
- [ ] GPO relationships reviewed
- [ ] Reachability considered

## ACL Analysis

- [ ] GenericAll reviewed
- [ ] GenericWrite reviewed
- [ ] WriteDacl reviewed
- [ ] WriteOwner reviewed
- [ ] AddMember reviewed
- [ ] ForceChangePassword reviewed
- [ ] Important ACEs independently validated
- [ ] Inheritance considered

## Attack Paths

- [ ] Source principal actually controlled
- [ ] Destination actually high value
- [ ] Every edge understood
- [ ] Every important edge validated
- [ ] Stale relationships considered
- [ ] Network prerequisites considered
- [ ] Security consequence established
- [ ] Path not overstated

## Evidence

- [ ] Collection timestamp recorded
- [ ] Collector recorded
- [ ] Collector version recorded
- [ ] Collection methods recorded
- [ ] BloodHound version recorded
- [ ] Source principal recorded
- [ ] Target recorded
- [ ] Path recorded
- [ ] Important edges recorded
- [ ] Validation recorded
- [ ] Limitations recorded
- [ ] Screenshot readable

## Reporting

- [ ] Root cause reported instead of tool
- [ ] Excessive permission identified
- [ ] Privilege boundary explained
- [ ] Path validated
- [ ] Alternative explanations considered
- [ ] Remediation targets root cause
- [ ] Retest procedure documented

## Retest

- [ ] Original edge reviewed
- [ ] Underlying configuration checked
- [ ] New collection performed
- [ ] Collection success confirmed
- [ ] Edge removed where expected
- [ ] Equivalent alternative path checked
- [ ] Evidence captured


# Quick Reference

## SharpHound Help

```powershell
.\SharpHound.exe --help
```

## Current Windows Identity

```powershell
whoami
```

## Current Groups

```powershell
whoami /groups
```

## Domain

```powershell
$env:USERDNSDOMAIN
```

## Linux Collector Help

```bash
bloodhound-python -h
```

## NetExec LDAP Help

```bash
nxc ldap --help
```

## DNS Configuration

```bash
cat /etc/resolv.conf
```

## Resolve DC

```bash
getent hosts dc01.corp.local
```

## LDAP SRV

```bash
dig _ldap._tcp.dc._msdcs.corp.local SRV
```

## Kerberos SRV

```bash
dig _kerberos._tcp.corp.local SRV
```

## Kerberos Cache

```bash
klist
```

## GenericAll Cypher

```cypher
MATCH (a)-[r:GenericAll]->(b)
RETURN a, r, b
LIMIT 50
```

## GenericWrite Cypher

```cypher
MATCH (a)-[r:GenericWrite]->(b)
RETURN a, r, b
LIMIT 50
```

## WriteDacl Cypher

```cypher
MATCH (a)-[r:WriteDacl]->(b)
RETURN a, r, b
LIMIT 50
```

## WriteOwner Cypher

```cypher
MATCH (a)-[r:WriteOwner]->(b)
RETURN a, r, b
LIMIT 50
```

## AdminTo Cypher

```cypher
MATCH (a)-[r:AdminTo]->(c:Computer)
RETURN a, r, c
LIMIT 50
```

## Session Cypher

```cypher
MATCH (c:Computer)-[r:HasSession]->(u:User)
RETURN c, r, u
LIMIT 50
```


# Quick Edge Reference

| Edge | General Meaning | Validate |
|---|---|---|
| `MemberOf` | Group membership | Current directory membership |
| `AdminTo` | Administrative rights over computer | Current local/group policy |
| `HasSession` | Session observed on computer | Session still active |
| `GenericAll` | Broad object control | Actual ACE and object type |
| `GenericWrite` | Attribute write rights | Writable attributes |
| `WriteDacl` | Can modify DACL | Effective ACL permission |
| `WriteOwner` | Can modify owner | Effective ownership rights |
| `Owns` | Owns object | DACL/object context |
| `AddMember` | Can influence group membership | Effective group permission |
| `ForceChangePassword` | Password-management relationship | Current effective right |
| `CanRDP` | RDP logon relationship | Reachability and logon rights |
| `CanPSRemote` | PowerShell remoting relationship | WinRM and authorisation |
| `ExecuteDCOM` | DCOM execution relationship | RPC/DCOM access |
| `AllowedToDelegate` | Delegation relationship | Kerberos configuration |
| `AllowedToAct` | RBCD-related relationship | Actual AD attribute/configuration |


# Quick Result Interpretation

| Observation | What It Means | What It Does Not Prove |
|---|---|---|
| User node exists | User was collected | Credential available |
| `MemberOf` | Membership relationship exists in dataset | Group is privileged |
| `AdminTo` | Administrative relationship represented | Host online |
| `HasSession` | Session observed during collection | Session still exists |
| `GenericAll` | Broad object-control relationship | Complete privilege escalation |
| `WriteDacl` | DACL modification relationship | ACL has been modified |
| Shortest path exists | Graph relationship connects objects | Entire path currently exploitable |
| No session edges | No sessions represented | No sessions exist |
| No AdminTo edges | No such edges represented | No administrators exist |
| Edge disappears after recollection | Relationship no longer represented | Remediation succeeded unless collection also succeeded |


# BloodHound Validation Matrix

Use a matrix like this during an assessment:

| Graph Observation | Independent Validation | Security Conclusion |
|---|---|---|
| User `MemberOf` Helpdesk | AD membership query | Membership confirmed |
| Helpdesk `GenericAll` Server-Admins | ACL review | Excessive delegated control confirmed |
| Server-Admins `AdminTo` SRV01 | Local admin/GPO review | Administrative access confirmed |
| SRV01 `HasSession` Admin1 | Session recheck | Time-sensitive, validate current state |
| User `CanRDP` SRV02 | RDP rights + network validation | Interactive access candidate |
| User `CanPSRemote` SRV03 | WinRM validation | Remote-management candidate |


# BloodHound Path Quality Model

A high-quality path should satisfy:

```text
Controlled Source
      |
      v
Current Relationship
      |
      v
Validated Permission
      |
      v
Reachable Destination
      |
      v
Required Service Available
      |
      v
Security Boundary Crossed
      |
      v
Meaningful Impact
```

If one component is unknown, state that limitation.


# Collection Quality Model

```text
                         COLLECTION
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
          DIRECTORY         ACLS          HOST DATA
              |              |              |
              |              |        +-----+-----+
              |              |        |           |
              v              v        v           v
           USERS          CONTROL   ADMINS      SESSIONS
           GROUPS          EDGES       |           |
           OUs                         |           |
           GPOs                        |           |
              |                        |           |
              +------------+-----------+-----------+
                           |
                           v
                    VERIFY COVERAGE
                           |
                           v
                     IMPORT DATASET
                           |
                           v
                      GRAPH ANALYSIS
```


# Attack Path Analysis Model

```text
                     CONTROLLED USER
                           |
                           v
                    GROUP MEMBERSHIP
                           |
                           v
                    OBJECT CONTROL
                           |
                           v
                   ADMIN RELATIONSHIP
                           |
                           v
                    TARGET COMPUTER
                           |
                           v
                   PRIVILEGED CONTEXT
                           |
                           v
                    HIGH-VALUE ASSET
```

At every transition ask:

```text
Is this relationship current?

Can I independently prove it?

What prerequisite is required?

What does it actually grant?
```


# Defensive Path-Breaking Model

```text
                         ATTACK PATH
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
       IDENTITY           DIRECTORY           HOST
          |                  |                  |
          v                  v                  v
    Group Membership      ACL / GPO       Local Admin
    Privileged Account    Delegation      Sessions
    Credential Reuse      Ownership       Remote Rights
          |                  |                  |
          +------------------+------------------+
                             |
                             v
                       BREAK THE PATH
```


# Final BloodHound Workflow

```text
                        AUTHORISED DOMAIN
                               |
                               v
                         DEFINE OBJECTIVE
                               |
                               v
                       CHOOSE COLLECTION
                               |
                               v
                            COLLECT
                               |
                               v
                     REVIEW COLLECTOR LOGS
                               |
                               v
                         IMPORT DATA
                               |
                               v
                      VERIFY COMPLETENESS
                               |
                               v
                    IDENTIFY OWNED PRINCIPAL
                               |
                               v
                     SEARCH INTERESTING PATHS
                               |
                               v
                      INSPECT EVERY EDGE
                               |
                               v
                  VALIDATE IMPORTANT RELATIONSHIPS
                               |
                               v
                      PATH STILL COMPLETE?
                          /           \
                        No             Yes
                        |               |
                        v               v
                  DOCUMENT LIMIT     ESTABLISH IMPACT
                                        |
                                        v
                                 CAPTURE EVIDENCE
                                        |
                                        v
                                  IDENTIFY ROOT CAUSE
                                        |
                                        v
                                     REMEDIATE
                                        |
                                        v
                                     RECOLLECT
                                        |
                                        v
                                      RETEST
```


# Command-to-Conclusion Model

Do not use BloodHound like this:

```text
Run Collector
     |
     v
Import ZIP
     |
     v
Click Shortest Path
     |
     v
Screenshot
     |
     v
Critical Finding
```

Use:

```text
Define Question
     |
     v
Choose Collection
     |
     v
Collect
     |
     v
Verify Coverage
     |
     v
Identify Path
     |
     v
Understand Edge Semantics
     |
     v
Validate Current Configuration
     |
     v
Validate Preconditions
     |
     v
Determine Security Boundary
     |
     v
Establish Impact
     |
     v
Report Root Cause
```


# Final Testing Principle

BloodHound should help answer:

```text
Who controls what?

Why do they control it?

Through which relationship?

Is the relationship current?

What does the relationship permit?

What additional prerequisite exists?

Can the relationship be independently confirmed?

What security boundary can be crossed?

Which configuration created the path?

Where should the organisation break the path?
```

The graph is the beginning of the analysis, not the end.


# Related Cheatsheets

- [Active Directory Cheatsheet](active-directory.md)
- [NetExec Cheatsheet](netexec.md)
- [Impacket Cheatsheet](impacket.md)
- [Windows Cheatsheet](windows.md)
- [PowerShell Cheatsheet](powershell.md)
- [Networking Cheatsheet](networking.md)


# Detailed Notes

## Active Directory

- [Active Directory Overview](../active-directory/index.md)
- [Methodology](../active-directory/methodology.md)
- [Enumeration](../active-directory/enumeration.md)
- [BloodHound](../active-directory/bloodhound.md)
- [NetExec](../active-directory/netexec.md)
- [Impacket](../active-directory/impacket.md)

## Permissions and Privilege

- [ACL and ACE](../active-directory/acl-ace.md)
- [Groups](../active-directory/groups.md)
- [Privilege Escalation](../active-directory/privilege-escalation.md)
- [Group Policy](../active-directory/group-policy.md)

## Remote Access

- [SMB](../active-directory/smb.md)
- [WinRM](../active-directory/winrm.md)
- [WMI](../active-directory/wmi.md)
- [DCOM](../active-directory/dcom.md)
- [Lateral Movement](../active-directory/lateral-movement.md)

## Kerberos and Delegation

- [Kerberos](../active-directory/kerberos.md)
- [Unconstrained Delegation](../active-directory/unconstrained-delegation.md)
- [Constrained Delegation](../active-directory/constrained-delegation.md)
- [Resource-Based Constrained Delegation](../active-directory/rbcd.md)
- [S4U](../active-directory/s4u.md)

## Trusts

- [Trusts](../active-directory/trusts.md)
- [Trust Relationships](../active-directory/trust-relationships.md)

## Active Directory Certificate Services

- [AD CS](../active-directory/ad-cs/index.md)
- [AD CS Enumeration](../active-directory/ad-cs/enumeration.md)


# References

- [BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }
- [BloodHound GitHub](https://github.com/SpecterOps/BloodHound){ target="_blank" rel="noopener noreferrer" }
- [SharpHound GitHub](https://github.com/SpecterOps/SharpHound){ target="_blank" rel="noopener noreferrer" }
- [BloodHound.py GitHub](https://github.com/dirkjanm/BloodHound.py){ target="_blank" rel="noopener noreferrer" }
- [NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Active Directory Security Groups](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Group Policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Kerberos Authentication](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Enterprise](https://attack.mitre.org/matrices/enterprise/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Validate the edge, not just the path"
    A BloodHound path is made of individual relationships. Validate the security-relevant edges independently before treating the complete path as confirmed.


!!! tip "Missing data is not negative evidence"
    If host collection failed, the absence of `AdminTo` or `HasSession` relationships does not prove those relationships do not exist. Record collection coverage and limitations alongside the graph analysis.


!!! tip "Report the root cause"
    BloodHound is the analysis tool. The finding is usually the excessive ACL, unnecessary group membership, administrative assignment, unsafe delegation, GPO permission or privileged-session exposure that created the path.


!!! warning "Session information is volatile"
    `HasSession` data represents an observation made during collection. Treat it as time-sensitive and revalidate important session relationships before relying on them in an attack-path conclusion.


!!! warning "Do not optimise for the shortest graph"
    The shortest path is mathematically interesting, but it is not automatically the most realistic security path. Prefer paths whose prerequisites, permissions, reachability and current state can be defensibly established.
