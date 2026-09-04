# Cheatsheets

Quick-reference material for penetration testing, red teaming, purple teaming, security assessments, and authorised security research.

The cheatsheets are designed for situations where you already understand the underlying technique and need to quickly answer:

> **What should I check next, and what command or tool can help me validate it?**

For detailed explanations, methodology, prerequisites, attack paths, defensive considerations, and remediation guidance, use the main topic-specific notes.

---

# Available Cheatsheets

<div class="grid cards" markdown>

-   :fontawesome-brands-linux:{ .lg .middle } **Linux**

    ---

    Linux enumeration, privilege escalation triage, permissions, SUID/SGID, capabilities, sudo, services, cron, containers, credentials, networking, and evidence collection.

    [:octicons-arrow-right-24: Linux Cheatsheet](linux.md)

-   :fontawesome-brands-windows:{ .lg .middle } **Windows**

    ---

    Windows host enumeration, privileges, services, scheduled tasks, writable paths, AppLocker, App Control, Defender, credentials, local privilege escalation, and evidence collection.

    [:octicons-arrow-right-24: Windows Cheatsheet](windows.md)

-   :simple-powershell:{ .lg .middle } **PowerShell**

    ---

    PowerShell syntax, host enumeration, files, ACLs, registry, networking, remoting, language modes, execution controls, logging, Defender, and security assessment commands.

    [:octicons-arrow-right-24: PowerShell Cheatsheet](powershell.md)

-   :material-lan:{ .lg .middle } **Networking**

    ---

    TCP/IP, DNS, routing, ports, sockets, Nmap, packet capture, HTTP/TLS, SSH tunnels, proxies, pivoting, VPNs, Active Directory networking, and troubleshooting.

    [:octicons-arrow-right-24: Networking Cheatsheet](networking.md)

-   :material-web:{ .lg .middle } **Web**

    ---

    Web reconnaissance, technology identification, content discovery, authentication, authorisation, APIs, injection, business logic, HTTP-layer testing, caching, LLM applications, and evidence collection.

    [:octicons-arrow-right-24: Web Cheatsheet](web.md)

-   :material-microsoft-windows:{ .lg .middle } **Active Directory**

    ---

    External, internal unauthenticated, authenticated domain-user, Windows-host, privilege escalation, Kerberos, NTLM, delegation, AD CS, trusts, lateral movement, and infrastructure assessment workflows.

    [:octicons-arrow-right-24: Active Directory Cheatsheet](active-directory.md)

-   :material-console:{ .lg .middle } **NetExec**

    ---

    NetExec workflows for SMB, LDAP, WinRM, MSSQL, SSH, Kerberos, shares, users, groups, sessions, AD enumeration, credential validation, relay-target discovery, and evidence collection.

    [:octicons-arrow-right-24: NetExec Cheatsheet](netexec.md)

-   :material-tools:{ .lg .middle } **Impacket**

    ---

    Impacket tool selection and workflows for SMB, Kerberos, LDAP, MSSQL, credential validation, remote administration, ticket operations, secrets assessment, and Active Directory testing.

    [:octicons-arrow-right-24: Impacket Cheatsheet](impacket.md)

-   :material-graph-outline:{ .lg .middle } **BloodHound**

    ---

    BloodHound collection, graph analysis, privilege-path discovery, ACL relationships, delegation, sessions, AD CS, attack-path reasoning, Cypher queries, and remediation validation.

    [:octicons-arrow-right-24: BloodHound Cheatsheet](bloodhound.md)

</div>

---

# Quick Navigation

| Area | Cheatsheet | Primary Use |
|---|---|---|
| Linux | [Linux](linux.md) | Linux enumeration and privilege escalation |
| Windows | [Windows](windows.md) | Windows host assessment and privilege escalation |
| PowerShell | [PowerShell](powershell.md) | Windows and PowerShell operational reference |
| Networking | [Networking](networking.md) | Network discovery, troubleshooting and pivoting |
| Web | [Web](web.md) | Web application and API assessments |
| Active Directory | [Active Directory](active-directory.md) | AD assessment methodology and attack-path analysis |
| NetExec | [NetExec](netexec.md) | Multi-protocol Windows and AD enumeration |
| Impacket | [Impacket](impacket.md) | Windows and AD protocol tooling |
| BloodHound | [BloodHound](bloodhound.md) | AD relationship and attack-path analysis |

---

# Cheatsheet vs Detailed Notes

The cheatsheets are not intended to replace the detailed documentation.

Use:

```text
Cheatsheet
    =
Quick operational reference

Detailed Notes
    =
Concepts
Methodology
Attack mechanics
Prerequisites
Validation
Impact
Detection
Mitigation
References
```

A typical workflow is:

```text
Assessment
    |
    v
Cheatsheet
    |
    v
Interesting Observation
    |
    v
Detailed Topic Page
    |
    v
Understand Technique
    |
    v
Validate Safely
    |
    v
Collect Evidence
    |
    v
Report
```

---

# General Assessment Workflow

A consistent methodology is more valuable than memorising commands.

```text
Scope
  |
  v
Starting Position
  |
  v
Enumeration
  |
  v
Attack Surface
  |
  v
Trust Boundaries
  |
  v
Hypothesis
  |
  v
Safe Validation
  |
  v
Impact
  |
  v
Evidence
  |
  v
Remediation
  |
  v
Re-Test
```

---

# Starting Position Matters

Before running tools, determine what access you actually have.

```text
External / Internet
        |
        v
No Internal Access

Internal Network
        |
        +--> Unauthenticated
        |
        +--> Authenticated

Endpoint Access
        |
        +--> Standard User
        |
        +--> Local Administrator

Directory Access
        |
        +--> Domain User
        |
        +--> Privileged User

Application Access
        |
        +--> Unauthenticated
        |
        +--> Authenticated
        |
        +--> Multiple Roles
        |
        +--> Administrator
```

The same command or observation can have very different meaning depending on the starting position.

---

# Scope First

Before testing, establish:

```text
What is in scope?

What is out of scope?

Which credentials are provided?

Which user roles are available?

Are production systems included?

Are disruptive techniques prohibited?

Are password attacks permitted?

Are relay attacks permitted?

Are credential extraction techniques permitted?

Are external callbacks permitted?

Are third-party systems excluded?

Are availability tests permitted?

What evidence may be collected?
```

---

# Linux

Use the [Linux Cheatsheet](linux.md) for Linux host assessment.

Core areas:

```text
Identity
OS / Kernel
Users
Groups
sudo
Processes
Services
Networking
Filesystems
Permissions
SUID / SGID
Capabilities
Cron
systemd Timers
SSH
Credentials
Configuration
Containers
NFS
Shared Libraries
Kernel Exposure
Security Controls
Logs
```

Typical model:

```text
Current User
     |
     v
Groups / sudo
     |
     v
Services / Processes
     |
     v
Files / Permissions
     |
     v
Scheduled Execution
     |
     v
Credentials
     |
     v
Containers / Mounts
     |
     v
Privilege Boundary
```

Useful references include:

```text
GTFOBins
Exploit Notes
HackTricks
PEASS-ng
Linux Smart Enumeration
Linux Exploit Suggester
```

---

# Windows

Use the [Windows Cheatsheet](windows.md) for Windows host assessment.

Core areas:

```text
Identity
Privileges
Local Groups
UAC
Processes
Services
Scheduled Tasks
Autoruns
Registry
Filesystem ACLs
Writable Locations
Credential Storage
PowerShell
Defender
ASR
AppLocker
App Control
Software
Drivers
IIS
SMB
RDP
WinRM
Event Logs
```

Typical model:

```text
Current User
     |
     v
Privileges
     |
     v
Local Groups
     |
     v
Services
     |
     v
Scheduled Tasks
     |
     v
Writable Paths
     |
     v
Credentials
     |
     v
Application Control
     |
     v
Privilege Boundary
```

---

# PowerShell

Use the [PowerShell Cheatsheet](powershell.md) when working from PowerShell or assessing PowerShell security controls.

Core areas:

```text
Language Mode
PowerShell Version
Execution Policy
Modules
Profiles
Files
ACLs
Registry
Processes
Services
Networking
HTTP
Remoting
CIM
Active Directory
Logging
AMSI
Defender
AppLocker
App Control
```

Security-control model:

```text
PowerShell
    |
    +--> Language Mode
    |
    +--> Logging
    |
    +--> AMSI
    |
    +--> Defender
    |
    +--> ASR
    |
    +--> AppLocker
    |
    +--> App Control
```

Do not treat one control as the complete security boundary.

---

# Networking

Use the [Networking Cheatsheet](networking.md) for network discovery, protocol testing, troubleshooting, and pivoting.

Core areas:

```text
Interfaces
IP Addresses
Routes
ARP / Neighbours
DNS
TCP
UDP
Ports
Sockets
HTTP
TLS
Nmap
Packet Capture
Firewalls
Proxies
SSH
Tunnels
Pivoting
VPNs
Containers
Active Directory Networking
```

Typical model:

```text
Interface
    |
    v
Address
    |
    v
Route
    |
    v
DNS
    |
    v
Reachability
    |
    v
Port
    |
    v
Protocol
    |
    v
Application
```

---

# Web

Use the [Web Cheatsheet](web.md) for web application and API assessments.

Core areas:

```text
Reconnaissance
Subdomains
HTTP Probing
Technology Identification
404 Fingerprinting
Content Discovery
Crawling
JavaScript
Parameters
Authentication
Session Management
Authorisation
Business Logic
APIs
GraphQL
gRPC
WebSockets
JWT
OAuth
SAML
XSS
SQLi
NoSQLi
Command Injection
SSTI
XXE
SSRF
File Upload
Path Traversal
Deserialization
Prototype Pollution
Request Smuggling
Cache Poisoning
Cache Deception
Race Conditions
Rate Limiting
LLM Applications
```

Assessment model:

```text
Discover
   |
   v
Understand
   |
   v
Map Trust
   |
   v
Hypothesise
   |
   v
Test
   |
   v
Validate
   |
   v
Assess Impact
```

---

# Active Directory

Use the [Active Directory Cheatsheet](active-directory.md) as the main quick-reference entry point for Active Directory assessments.

It is organised around the tester's starting position.

```text
External
   |
   v
Internal Unauthenticated
   |
   v
Authenticated Domain User
   |
   v
Windows Host Access
   |
   v
Local Administrator
   |
   v
Privileged Domain Context
```

Core areas include:

```text
Domain Discovery
Domain Controllers
DNS
Users
Groups
Computers
Password Policy
Kerberos
NTLM
Password Spraying
AS-REP Roasting
Kerberoasting
Tickets
ACLs
GPO
MachineAccountQuota
LAPS
gMSA
Delegation
RBCD
S4U
Shadow Credentials
NTLM Relay
Kerberos Relay
Authentication Coercion
AD CS
Trusts
SID History
Shares
ADIDNS
Lateral Movement
Credential Access
NTDS
SCCM
WSUS
MDT
SCOM
AD FS
RODC
Privilege Escalation
Persistence
```

---

# Active Directory Starting Positions

## External - No Credentials

Focus on:

```text
DNS
Public Infrastructure
VPN
RD Gateway
OWA / Exchange
AD FS
SSO
Entra ID Integration
Citrix
VMware Horizon
Password Reset
Autodiscover
Certificates
Public Authentication Portals
```

Goal:

```text
Understand exposed identity infrastructure
without assuming internal access.
```

---

## Internal - Unauthenticated

Focus on:

```text
Network Configuration
DNS
Domain Discovery
Domain Controllers
Kerberos
LDAP
SMB
RPC
SMB Signing
Anonymous Access
Guest Access
Null Sessions
Relay Conditions
```

Goal:

```text
Determine what the internal network exposes
before valid domain credentials are available.
```

---

## Internal - Authenticated Domain User

This is one of the most important AD assessment perspectives.

Focus on:

```text
Users
Groups
Computers
SPNs
Password Policy
Fine-Grained Password Policies
Shares
SYSVOL
NETLOGON
ACLs
Delegation
AD CS
Trusts
LAPS
gMSA
MachineAccountQuota
BloodHound Relationships
Sessions
Local Administrative Rights
```

Goal:

```text
Understand what a normal domain user can discover,
reach, influence, or escalate toward.
```

---

# Windows Host Assessment During AD Testing

Do not assess only the directory.

A domain-joined Windows host can expose additional paths.

Check:

```text
Current User
Groups
Privileges
PowerShell Language Mode
PowerShell Logging
AMSI
Defender
ASR
AppLocker
App Control
Writable Directories
Writable PATH Entries
Services
Scheduled Tasks
Startup Locations
Installed Software
Credential Manager
PowerShell History
RDP
WinRM
SMB
Local Administrators
Network Connections
Security Products
```

The combination of controls matters more than any individual control.

---

# Active Directory Attack-Path Model

Avoid viewing AD techniques as isolated tricks.

Use:

```text
Identity
   |
   v
Group Membership
   |
   v
ACL
   |
   v
Computer
   |
   v
Session
   |
   v
Credential
   |
   v
Delegation
   |
   v
Certificate
   |
   v
Trust
   |
   v
Higher Privilege
```

An attack path is often a chain of individually ordinary relationships.

---

# Active Directory Certificate Services

AD CS should be treated as a dedicated attack surface.

Core areas:

```text
Certificate Authorities
Certificate Templates
Enrollment Rights
Template Permissions
EKUs
Subject Name Control
Manager Approval
Authorised Signatures
CA Configuration
Web Enrollment
HTTP Enrollment
NTLM Relay Exposure
Certificate Mapping
Authentication Certificates
```

ESC coverage in the detailed notes includes:

```text
ESC1
ESC2
ESC3
ESC4
ESC5
ESC6
ESC7
ESC8
ESC9
ESC10
ESC11
ESC12
ESC13
ESC14
ESC15
ESC16
ESC17
Golden Certificate
```

Use the detailed AD CS notes when a potentially vulnerable certificate path is identified.

---

# Active Directory Tool Selection

A useful mental model:

```text
Need broad Windows / AD enumeration?
    -> NetExec

Need protocol-level tooling?
    -> Impacket

Need relationship / path analysis?
    -> BloodHound

Need AD CS analysis?
    -> Certipy

Need Windows host enumeration?
    -> PowerShell / Seatbelt / winPEAS

Need Linux-side AD queries?
    -> ldapsearch / Kerberos tools / Samba tools
```

No single tool provides a complete AD assessment.

---

# NetExec

Use the [NetExec Cheatsheet](netexec.md) for quick NetExec workflows.

NetExec is particularly useful when the assessment involves many hosts.

Common areas:

```text
SMB
LDAP
WinRM
MSSQL
SSH
Credential Validation
Kerberos
Users
Groups
Computers
Shares
Sessions
Local Administrators
Password Policy
Relay Target Discovery
Modules
Command Execution
Evidence Collection
```

Typical workflow:

```text
Targets
   |
   v
Protocol Discovery
   |
   v
Authentication
   |
   v
Enumeration
   |
   v
Privilege Context
   |
   v
Interesting Hosts
   |
   v
Focused Validation
```

---

# NetExec Result Interpretation

Do not confuse:

```text
Authentication Success
```

with:

```text
Administrative Access
```

Always distinguish:

```text
Credential Valid
Service Accessible
User Authorised
Administrative Rights
Remote Execution Available
```

These are different security conditions.

---

# NetExec and Password Testing

Before password spraying or credential testing:

```text
Retrieve Password Policy
        |
        v
Understand Lockout Threshold
        |
        v
Understand Observation Window
        |
        v
Determine Safe Test Rate
        |
        v
Use Approved Accounts / Scope
```

Avoid indiscriminate authentication attempts.

---

# Impacket

Use the [Impacket Cheatsheet](impacket.md) when protocol-specific Windows and Active Directory tooling is needed.

Common tools and areas include:

```text
GetUserSPNs
GetNPUsers
GetADUsers
Get-GPPPassword
GetLAPSPassword
lookupsid
rpcdump
samrdump
smbclient
smbserver
mssqlclient
GetUserSPNs
secretsdump
ticketer
getTGT
getST
ticketConverter
ntlmrelayx
psexec
wmiexec
smbexec
atexec
dcomexec
```

The exact tool selection depends on:

```text
Protocol
Credential Type
Privilege Level
Kerberos Availability
Target Service
Assessment Objective
```

---

# Impacket Tool Selection Model

```text
Need SMB interaction?
    -> smbclient

Need MSSQL interaction?
    -> mssqlclient

Need SPN / Kerberoast enumeration?
    -> GetUserSPNs

Need AS-REP Roast candidates?
    -> GetNPUsers

Need SID discovery?
    -> lookupsid

Need TGT?
    -> getTGT

Need service ticket?
    -> getST

Need ticket format conversion?
    -> ticketConverter

Need relay assessment?
    -> ntlmrelayx

Need authorised secrets assessment?
    -> secretsdump

Need remote administration validation?
    -> psexec / wmiexec / smbexec / atexec / dcomexec
```

High-impact tools should be used only when they are required to answer an authorised assessment question.

---

# BloodHound

Use the [BloodHound Cheatsheet](bloodhound.md) to understand Active Directory relationships and privilege paths.

BloodHound is not simply a visualisation tool.

It helps answer:

```text
Who can control what?

Which relationships create privilege?

Where are privileged sessions?

Which computers are strategically important?

Which ACLs create attack paths?

Which delegation relationships matter?

Which certificate relationships matter?

What is the shortest path to a sensitive object?

What should defenders remediate first?
```

---

# BloodHound Model

```text
Directory Data
      |
      v
Collection
      |
      v
Graph
      |
      v
Nodes + Edges
      |
      v
Relationships
      |
      v
Attack Paths
      |
      v
Validation
      |
      v
Remediation
```

---

# BloodHound Collection

Collection should be deliberate.

Consider:

```text
Users
Groups
Computers
Domains
OUs
GPOs
Containers
ACLs
Sessions
Local Groups
Trusts
Certificate Services
```

More collection is not automatically better.

Balance:

```text
Coverage
   vs
Network Traffic
   vs
Assessment Requirements
```

---

# BloodHound Analysis

High-value questions include:

```text
What can the current user control?

What can the current user's groups control?

Where does the user have local administrator rights?

Where are privileged users logged on?

Which principals can modify privileged groups?

Which computers have paths to domain control?

Which ACL relationships are exploitable?

Which delegation paths exist?

Which certificate paths exist?

Which trust relationships expand the attack surface?
```

---

# BloodHound Edge Interpretation

Never report an edge solely because it exists.

For each relationship determine:

```text
Source
Target
Edge Type
Required Privilege
Prerequisites
Reachability
Operational Constraints
Security Impact
```

Then validate the relationship independently where appropriate.

---

# Combining the AD Tools

The three primary AD cheatsheets complement each other.

```text
                 ACTIVE DIRECTORY
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
     NetExec         Impacket       BloodHound
        |               |               |
        v               v               v
   Enumeration      Protocols        Graph
   Validation       Kerberos         Paths
   Host Triage      SMB / RPC        ACLs
   Shares           Tickets          Sessions
   Services         Relay            Delegation
   Modules          Remote Ops       Relationships
        |               |               |
        +---------------+---------------+
                        |
                        v
                 Manual Validation
                        |
                        v
                     Evidence
```

A common workflow is:

```text
NetExec
   |
   v
Identify Hosts / Users / Services
   |
   v
Impacket
   |
   v
Focused Protocol Validation
   |
   v
BloodHound
   |
   v
Understand Relationships
   |
   v
Return to NetExec / Impacket
   |
   v
Validate Specific Path
```

---

# Re-Enumeration

Re-enumeration is essential.

After obtaining:

```text
New Credentials
New Group Membership
New Host Access
New Network Segment
New Certificate
New Kerberos Ticket
New API Role
New Application Role
```

repeat relevant enumeration.

```text
Initial Access
     |
     v
Enumerate
     |
     v
New Access
     |
     v
Re-Enumerate
     |
     v
New Attack Surface
```

Do not assume the original attack surface remains complete after privilege changes.

---

# Context Before Commands

A command without context is easy to misuse.

Before using a command ask:

```text
What question am I answering?

What permissions do I currently have?

What protocol does this use?

What traffic will it generate?

Could it modify state?

Could it expose credentials?

Could it affect another user?

Could it trigger account lockout?

Could it cause service disruption?

What evidence do I need?
```

---

# Safe Validation

Prefer the least intrusive test that proves the issue.

```text
Observation
    |
    v
Hypothesis
    |
    v
Low-Impact Test
    |
    v
Confirmed?
    |
    +--> No -> Reassess
    |
    +--> Yes
           |
           v
      Minimum Evidence
```

Do not automatically escalate from:

```text
Can enumerate
```

to:

```text
Can exploit
```

if enumeration already proves the relevant security weakness.

---

# Evidence Collection

Good evidence should answer:

```text
What was tested?

When was it tested?

From where?

As which user?

Against which target?

What command or request was used?

What was the relevant output?

What changed?

What security boundary was crossed?
```

---

# Evidence Directory

A useful structure:

```text
evidence/
├── linux/
├── windows/
├── powershell/
├── networking/
├── web/
└── active-directory/
    ├── enumeration/
    ├── kerberos/
    ├── ntlm/
    ├── acl/
    ├── delegation/
    ├── adcs/
    ├── trusts/
    ├── lateral-movement/
    ├── netexec/
    ├── impacket/
    └── bloodhound/
```

---

# Evidence Quality

Prefer:

```text
Relevant Command
Relevant Output
Target
Identity
Timestamp
Short Explanation
```

Avoid:

```text
Huge terminal dumps
Unrelated secrets
Full credential databases
Unnecessary personal data
Screenshots without context
Scanner output without validation
```

---

# Reporting Model

A defensible finding should connect:

```text
Observation
     +
Prerequisites
     +
Security Boundary
     +
Reproducibility
     +
Impact
     =
Finding
```

---

# Do Not Overreport

Examples of observations that require context:

```text
Port 445 is open
PowerShell is installed
PowerShell uses FullLanguage
rundll32.exe exists
A directory is writable
A domain user can query LDAP
SMB signing is disabled
A certificate template exists
A BloodHound edge exists
A technology version is visible
A security header is missing
A tool authenticates successfully
```

The question is:

```text
What security boundary can be crossed because of this condition?
```

---

# Remediation Thinking

Do not stop at:

```text
Disable Feature
```

Consider:

```text
Why does the feature exist?

Who requires it?

What security boundary failed?

Can permissions be reduced?

Can access be segmented?

Can stronger authentication be applied?

Can monitoring detect abuse?

Can the dangerous relationship be removed?

Can the architecture eliminate the path?
```

---

# Purple Team Perspective

The same cheatsheets can support purple teaming.

For each technique:

```text
Red Team
    |
    v
Perform Controlled Action
    |
    v
Blue Team
    |
    v
Observe Telemetry
    |
    v
Detection?
    |
    +--> Yes -> Evaluate Quality
    |
    +--> No  -> Identify Gap
                    |
                    v
                 Improve
                    |
                    v
                  Re-Test
```

Useful questions:

```text
Was the activity logged?

Which host produced telemetry?

Which identity was visible?

Which process was visible?

Which protocol was visible?

Did the SIEM receive the event?

Was an alert generated?

Was the alert actionable?

Could the analyst reconstruct the activity?
```

---

# Quick Tool Map

| Objective | Useful Starting Tool |
|---|---|
| Linux host enumeration | Linux shell / PEASS-ng |
| Windows host enumeration | PowerShell / Seatbelt / winPEAS |
| PowerShell assessment | PowerShell |
| Network discovery | Nmap |
| DNS | dig / nslookup |
| HTTP inspection | curl / Burp Suite |
| Web fingerprinting | WhatWeb / Wappalyzer |
| Web content discovery | ffuf / feroxbuster |
| Web crawling | Katana / Burp Suite |
| AD broad enumeration | NetExec |
| AD protocol operations | Impacket |
| AD graph analysis | BloodHound |
| AD CS | Certipy |
| LDAP | ldapsearch / NetExec |
| SMB | NetExec / Impacket |
| Kerberos | Impacket / native Kerberos tools |
| Packet capture | Wireshark / tcpdump |
| HTTP probing at scale | httpx |

Tools should support the methodology, not define it.

---

# Core Cheatsheet Set

The current core cheatsheet collection is:

```text
docs/cheatsheets/
├── index.md
├── linux.md
├── windows.md
├── powershell.md
├── networking.md
├── web.md
├── active-directory.md
├── netexec.md
├── impacket.md
└── bloodhound.md
```

This provides three layers of reference:

```text
Operating Systems
    |
    +--> Linux
    +--> Windows
    +--> PowerShell

Assessment Domains
    |
    +--> Networking
    +--> Web
    +--> Active Directory

AD Tooling
    |
    +--> NetExec
    +--> Impacket
    +--> BloodHound
```

---

# Detailed Notes

The cheatsheets should act as gateways into the detailed knowledge base.

Primary sections:

```text
Web Application Security
Active Directory
Source Code Review
Research
```

For Active Directory, detailed coverage includes:

```text
Enumeration
Methodology
Kerberos
NTLM
Password Spraying
AS-REP Roasting
Kerberoasting
Pass-the-Hash
Pass-the-Key
Pass-the-Ticket
Kerberos Tickets
Delegation
RBCD
S4U
ACL / ACE
Groups
Group Policy
MachineAccountQuota
Credential Access
LAPS
gMSA
Shadow Credentials
NTDS
NTLM Relay
Kerberos Relay
Authentication Coercion
AD CS
ESC1-ESC17
Golden Certificate
Lateral Movement
SMB
WinRM
WMI
DCOM
Pivoting
Trusts
SID History
ADIDNS
Shares
SCCM
WSUS
MDT
SCOM
AD FS
RODC
Privilege Escalation
Persistence
```

For Web Application Security, detailed coverage includes:

```text
Reconnaissance
Technology Identification
Content Discovery
Parameter Discovery
JavaScript Analysis
Authentication
Authorisation
Session Management
IDOR / BOLA
Business Logic
XSS
DOM-Based Vulnerabilities
SQL Injection
NoSQL Injection
LDAP Injection
Command Injection
SSTI
XXE
SSRF
Path Traversal
File Inclusion
File Upload
Deserialization
Prototype Pollution
Host Header Attacks
HTTP Request Smuggling
Cache Poisoning
Cache Deception
CORS
CSRF
Clickjacking
Open Redirect
OAuth / OIDC
JWT
SAML
API Security
GraphQL
gRPC
WebSockets
Mass Assignment
Race Conditions
Rate Limiting
Secrets Exposure
Dependency Security
Web LLM Attacks
```

---

# Reference Philosophy

These cheatsheets intentionally combine:

```text
Commands
    +
Methodology
    +
Decision Points
    +
Security Context
    +
Evidence Guidance
```

A useful security reference should not simply answer:

```text
What command do I run?
```

It should also help answer:

```text
Why am I running it?

What should I expect?

What does the result mean?

What should I test next?

What would constitute a real finding?

What evidence should I preserve?
```

---

# Final Assessment Model

Use the cheatsheets as a map rather than a checklist that must always be completed from top to bottom.

```text
                         ASSESSMENT
                              |
                              v
                            SCOPE
                              |
                              v
                      STARTING POSITION
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
            HOST            NETWORK       APPLICATION
              |               |               |
         +----+----+          |          +----+----+
         |         |          |          |         |
         v         v          v          v         v
       Linux    Windows   Networking    Web        API
                    |
                    v
               PowerShell
                              |
                              v
                    ACTIVE DIRECTORY
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
          NetExec          Impacket        BloodHound
             |                |                |
             +----------------+----------------+
                              |
                              v
                         ENUMERATION
                              |
                              v
                        ATTACK SURFACE
                              |
                              v
                       TRUST BOUNDARIES
                              |
                              v
                          HYPOTHESIS
                              |
                              v
                       SAFE VALIDATION
                              |
                              v
                           IMPACT
                              |
                              v
                          EVIDENCE
                              |
                              v
                         REMEDIATION
                              |
                              v
                           RE-TEST
```

The objective is not to run every command in every cheatsheet.

The objective is to understand:

```text
Where am I?

What can I see?

What can I reach?

What does my current identity control?

Which trust relationships exist?

Which security boundary might fail?

What is the minimum safe test that proves it?

What should the organisation change?
```

That turns a collection of commands into a repeatable security assessment methodology.
