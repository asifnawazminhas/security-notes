# Active Directory Penetration Testing

Active Directory (AD) is Microsoft's directory service used by organisations to centrally manage identities, computers, authentication, authorisation, policies, services, and other resources.

From a penetration-testing perspective, Active Directory should not be viewed as a collection of isolated vulnerabilities.

It is better understood as a graph of:

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

An attacker may begin with a low-privileged account and reach a highly privileged position through several individually legitimate relationships.

For example:

```text
Low-Privileged User
        |
        v
Group Membership
        |
        v
Write Permission over User
        |
        v
Credential / Account Control
        |
        v
Administrative Group
        |
        v
Domain Privileges
```

The objective of an Active Directory penetration test is therefore not simply:

```text
Find Domain Admin credentials
```

It is to understand:

```text
How is the domain configured?

What identities exist?

What systems exist?

What trust relationships exist?

Where are credentials exposed?

Where are permissions excessive?

Which authentication mechanisms are available?

Which attack paths connect low privilege to high privilege?

How far could an attacker realistically move through the environment?

What controls prevent or enable that movement?
```

---

# Authorised Testing

The techniques described in these notes are intended for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Training laboratories
CTFs
Security research
```

Active Directory testing can affect production authentication and infrastructure.

Techniques involving:

```text
Password spraying
Authentication relaying
Credential dumping
Account modification
Group membership changes
Certificate enrolment
Kerberos tickets
Service creation
Remote execution
Coercion
Persistence
```

must be performed only when permitted by the engagement scope and rules of engagement.

Prefer passive or read-only enumeration before intrusive validation.

---

# Active Directory Testing Model

A useful high-level methodology is:

```text
Initial Network Access
        |
        v
Network Discovery
        |
        v
Domain Discovery
        |
        v
Active Directory Enumeration
        |
        v
Identity and Host Mapping
        |
        v
Attack Path Analysis
        |
        +----------------------+
        |                      |
        v                      v
Authentication             Authorisation
        |                      |
        v                      v
Kerberos / NTLM            ACL / ACE / GPO
        |                      |
        +----------+-----------+
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
              Pivoting
                   |
                   v
       Additional Network Segments
                   |
                   v
            Domain Control
                   |
                   v
          Trust Relationships
                   |
                   v
       Persistence / Wider Impact
```

This is not necessarily a linear process.

An engagement frequently loops between:

```text
Enumerate
   |
   v
Identify Opportunity
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

---

# What Is Active Directory?

Active Directory Domain Services (AD DS) provides centralised management for resources such as:

```text
Users
Computers
Groups
Organisational Units
Policies
Services
Authentication
Authorisation
```

A typical environment may look like:

```text
                 example.local
                       |
              +--------+--------+
              |                 |
             DC01              DC02
              |
      +-------+-------+
      |               |
    Users          Computers
      |               |
    Groups          Servers
      |               |
     OUs          Workstations
      |
     GPOs
```

---

# Core Active Directory Components

Important components include:

| Component | Purpose |
|---|---|
| Domain | Administrative and authentication boundary within AD |
| Forest | Collection of one or more AD domains |
| Domain Controller | Server hosting AD DS and authenticating identities |
| User | Identity representing a person or service |
| Computer | AD identity representing a computer |
| Group | Collection of security principals |
| OU | Container used to organise AD objects |
| GPO | Group Policy configuration applied to users/computers |
| ACL | Defines permissions over an object |
| Kerberos | Primary AD authentication protocol |
| NTLM | Legacy/challenge-response authentication protocol still encountered in AD |
| LDAP | Protocol used to query and interact with directory information |
| DNS | Critical service used to locate AD services |
| AD CS | Microsoft's Active Directory Certificate Services |
| Trust | Relationship allowing authentication between domains or forests |

---

# Domain Controllers

Domain Controllers are among the most important systems in an AD environment.

They commonly provide:

```text
Kerberos
LDAP
LDAPS
DNS
SMB
RPC
Active Directory database services
Group Policy
Authentication
```

A compromise of a Domain Controller can result in compromise of the domain.

---

# Common Domain Controller Ports

Common ports include:

| Port | Protocol | Purpose |
|---:|---|---|
| 53 | TCP/UDP | DNS |
| 88 | TCP/UDP | Kerberos |
| 135 | TCP | RPC Endpoint Mapper |
| 139 | TCP | NetBIOS |
| 389 | TCP/UDP | LDAP |
| 445 | TCP | SMB |
| 464 | TCP/UDP | Kerberos password operations |
| 636 | TCP | LDAPS |
| 3268 | TCP | Global Catalog |
| 3269 | TCP | Global Catalog over TLS |

Additional dynamic RPC ports may also be used.

Port presence should be treated as evidence of services, not proof that a host is a Domain Controller.

---

# DNS and Active Directory

DNS is fundamental to Active Directory.

Clients use DNS to discover:

```text
Domain Controllers
Kerberos services
LDAP services
Global Catalog servers
Domain services
```

Important records include SRV records.

Example:

```text
_ldap._tcp.dc._msdcs.example.local
```

Query from Linux:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

---

# Active Directory Authentication

The two authentication technologies most frequently encountered during AD testing are:

```text
Kerberos
NTLM
```

Conceptually:

```text
            Authentication
                 |
        +--------+--------+
        |                 |
        v                 v
     Kerberos            NTLM
        |                 |
        v                 v
      Tickets       Challenge/Response
```

Understanding both is essential.

---

# Kerberos

Kerberos is the primary authentication protocol used by modern Active Directory environments.

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

Simplified authentication flow:

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
Target Service
```

Kerberos configuration and identity relationships create several important assessment areas, including:

```text
AS-REP Roasting
Kerberoasting
Delegation
Ticket abuse
Service account exposure
SPN configuration
Trust relationships
```

These topics are covered individually in the Active Directory notes.

---

# NTLM

NTLM uses challenge-response authentication.

Simplified:

```text
Client
   |
   | Authentication Request
   v
Server
   |
   | Challenge
   v
Client
   |
   | Response
   v
Server
```

NTLM remains important because it can interact with:

```text
SMB
HTTP
LDAP
RPC
Name resolution
Authentication relay scenarios
Legacy systems
```

Important assessment areas include:

```text
NTLM capture
NTLM relay
SMB signing
LDAP signing
Channel binding
LLMNR
NBT-NS
mDNS
Authentication coercion
```

---

# LDAP

LDAP is one of the primary ways to query Active Directory.

LDAP can expose information about:

```text
Users
Groups
Computers
Organisational Units
Service Principal Names
Delegation
ACLs
Group Policy
Domain configuration
Trusts
Certificate services
```

LDAP therefore plays a major role in AD enumeration.

---

# Distinguished Names

Active Directory objects are represented using Distinguished Names.

Example:

```text
CN=Alice Smith,OU=Users,DC=example,DC=local
```

Breakdown:

```text
CN = Common Name
OU = Organisational Unit
DC = Domain Component
```

Domain:

```text
example.local
```

becomes:

```text
DC=example,DC=local
```

---

# Security Principals

Important security principals include:

```text
Users
Computers
Groups
Managed service accounts
Service accounts
```

Security principals have Security Identifiers (SIDs).

Example conceptual SID:

```text
S-1-5-21-111111111-222222222-333333333-1105
```

---

# Users

User accounts may represent:

```text
Employees
Administrators
Service accounts
Application identities
Legacy accounts
Shared accounts
```

Important attributes may include:

```text
Username
Display name
Description
Group membership
SPNs
Password settings
Account status
Delegation configuration
Last logon information
```

---

# Computer Accounts

Computers also have AD accounts.

Typical format:

```text
WORKSTATION01$
SERVER01$
DC01$
```

Computer accounts possess credentials and can participate in Kerberos authentication.

They should not be ignored during attack-path analysis.

---

# Groups

Groups are central to AD authorisation.

Examples include:

```text
Domain Admins
Enterprise Admins
Administrators
Account Operators
Server Operators
Backup Operators
Remote Desktop Users
Remote Management Users
DNSAdmins
```

However, custom organisational groups can be just as important.

For example:

```text
Application Administrators
        |
        v
Server Administrators
        |
        v
Tier-0 Management
```

Group nesting can create indirect privilege.

---

# Group Nesting

Example:

```text
Alice
  |
  v
Helpdesk
  |
  v
Server Operators
  |
  v
Privileged Server Access
```

Always evaluate nested membership.

---

# Organisational Units

Organisational Units organise directory objects.

Example:

```text
example.local
│
├── Domain Controllers
│
├── Servers
│   ├── Production
│   └── Development
│
├── Workstations
│
└── Users
    ├── Administrators
    └── Employees
```

OUs matter because:

```text
GPOs can apply to OUs
Permissions can be delegated over OUs
Objects inherit permissions
Administrative boundaries may depend on OU structure
```

---

# Group Policy

Group Policy is used to centrally configure:

```text
Security settings
Windows settings
Scripts
Registry values
Firewall settings
Software deployment
User configuration
Computer configuration
```

GPO permissions and writable policy paths can become security-relevant.

A simplified model:

```text
GPO
 |
 v
OU
 |
 +--> Users
 |
 +--> Computers
```

---

# ACLs and ACEs

Active Directory objects have Access Control Lists.

An ACL contains Access Control Entries.

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

An ACE may grant a principal permission to:

```text
Read
Write
Reset password
Modify membership
Modify owner
Modify permissions
Write attributes
Create child objects
Delete objects
```

These permissions can create powerful attack paths.

---

# Why ACLs Matter

Suppose:

```text
User A
   |
   | GenericAll
   v
User B
```

User A may effectively control User B.

If User B is privileged:

```text
Low Privilege User
       |
       v
Control User B
       |
       v
Privileged Group
       |
       v
Privilege Escalation
```

This is why AD should be treated as a graph rather than a flat list of accounts.

---

# BloodHound Model

BloodHound represents Active Directory relationships as a graph.

Conceptually:

```text
Nodes
 |
 +--> Users
 +--> Groups
 +--> Computers
 +--> Domains
 +--> GPOs
 +--> OUs
 +--> Certificate authorities

Edges
 |
 +--> MemberOf
 +--> AdminTo
 +--> HasSession
 +--> GenericAll
 +--> GenericWrite
 +--> WriteDACL
 +--> WriteOwner
 +--> ForceChangePassword
 +--> delegation relationships
 +--> certificate relationships
```

This allows questions such as:

```text
How can this user reach Domain Admin?

Who can control this computer?

Which principals can modify this group?

Where do privileged users have sessions?

Which certificate relationships create escalation paths?
```

---

# Attack Paths

An attack path is a chain of relationships that produces meaningful privilege.

Example:

```text
User
 |
 | MemberOf
 v
Helpdesk
 |
 | GenericWrite
 v
Service Account
 |
 | Kerberoastable
 v
Credential
 |
 | AdminTo
 v
Server
 |
 | Session
 v
Administrator
```

Each individual relationship may appear harmless.

The combination creates the risk.

---

# Initial Access States

An internal AD assessment may begin from several positions.

## Unauthenticated Network Access

```text
Network access
No domain credentials
No compromised workstation
```

Initial objectives:

```text
Discover hosts
Discover DNS
Identify domain
Locate Domain Controllers
Identify SMB/LDAP/Kerberos
Assess anonymous exposure
```

---

## Domain User

```text
Username
+
Password / Hash / Ticket
```

This dramatically increases enumeration capability.

A normal domain account can often query substantial directory information.

---

## Compromised Workstation

You may have:

```text
Shell
User context
Domain context
Local files
Network access
Cached information
Sessions
```

The host becomes both:

```text
A target
```

and potentially:

```text
A pivot point
```

---

## Local Administrator

Local administrator privileges may provide access to:

```text
Local credential material
Service configuration
Registry secrets
Processes
Sessions
Remote administration
```

But:

```text
Local Administrator
        !=
Domain Administrator
```

The next objective is understanding how local compromise connects to the wider domain.

---

# AD Enumeration Philosophy

Do not begin by firing every tool at the domain.

Start with:

```text
What do I know?
```

Then:

```text
What can I safely learn?
```

Then:

```text
What relationships matter?
```

A good workflow is:

```text
Domain
  |
  v
Domain Controllers
  |
  v
Users
  |
  v
Groups
  |
  v
Computers
  |
  v
Sessions
  |
  v
Permissions
  |
  v
Trusts
  |
  v
Attack Paths
```

---

# Network Discovery

Before deep AD enumeration, understand the network.

Identify:

```text
Your IP address
Subnet
Default gateway
DNS servers
Routes
Accessible networks
```

Linux:

```bash
ip addr
ip route
cat /etc/resolv.conf
```

Windows:

```powershell
ipconfig /all
route print
```

---

# Domain Discovery from Windows

Useful native commands include:

```cmd
whoami
whoami /user
whoami /groups
hostname
systeminfo
```

Domain information:

```cmd
echo %USERDOMAIN%
echo %USERDNSDOMAIN%
```

Domain Controller discovery:

```cmd
nltest /dsgetdc:example.local
```

List Domain Controllers:

```cmd
nltest /dclist:example.local
```

---

# PowerShell Domain Information

```powershell
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:LOGONSERVER
```

Current identity:

```powershell
whoami /all
```

---

# Linux Domain Discovery

DNS is often the first source.

```bash
cat /etc/resolv.conf
```

Then:

```bash
dig example.local
```

and:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

# LDAP RootDSE

RootDSE can reveal useful directory information.

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

Depending on server policy, some RootDSE information may be available without authenticated LDAP enumeration.

---

# SMB Discovery

SMB is a major AD assessment surface.

Important questions include:

```text
Is SMB available?

What SMB dialects are supported?

Is SMB signing required?

Are shares accessible?

Is anonymous access possible?

Which credentials authenticate?

Where do accounts have administrative access?
```

---

# NetExec

NetExec is one of the most useful tools for internal Windows and Active Directory assessments.

It supports multiple protocols and can assist with:

```text
Host enumeration
SMB enumeration
LDAP enumeration
Authentication validation
Share enumeration
User/group enumeration
Administrative access identification
Kerberos-related enumeration
```

Example basic SMB query:

```bash
nxc smb 10.10.10.10
```

Authenticated example:

```bash
nxc smb 10.10.10.10 \
  -u 'alice' \
  -p 'Password'
```

Domain context:

```bash
nxc smb 10.10.10.10 \
  -d example.local \
  -u 'alice' \
  -p 'Password'
```

NetExec will receive its own dedicated tool note.

---

# Impacket

Impacket is a collection of Python implementations of network protocols commonly encountered in Windows and Active Directory environments.

Important utilities include:

```text
GetUserSPNs.py
GetNPUsers.py
GetADUsers.py
lookupsid.py
secretsdump.py
smbclient.py
smbserver.py
psexec.py
wmiexec.py
smbexec.py
dcomexec.py
atexec.py
ntlmrelayx.py
getTGT.py
getST.py
ticketer.py
```

Rather than memorising isolated commands, understand what protocol and security mechanism each tool interacts with.

Impacket will receive its own dedicated note.

---

# Responder

Responder is commonly used during internal assessments to analyse and interact with name-resolution and authentication behaviour.

Relevant protocols may include:

```text
LLMNR
NBT-NS
mDNS
```

Conceptually:

```text
Client cannot resolve resource
          |
          v
Local Name Resolution
          |
          v
Attacker-controlled response
          |
          v
Authentication attempt
          |
          +--> Capture
          |
          +--> Potential relay path
```

Capture and relay must be treated separately:

```text
Credential Capture
       !=
Authentication Relay
```

Responder and relay techniques will receive dedicated notes.

---

# BloodHound

BloodHound is used to analyse relationships in Active Directory.

Typical workflow:

```text
Collect AD Data
      |
      v
Import
      |
      v
Graph Relationships
      |
      v
Identify Attack Paths
      |
      v
Manually Validate
```

BloodHound should not replace manual understanding.

A graph edge should be investigated to determine:

```text
What permission exists?

Why does it exist?

Can it actually be used?

What does it provide?

What is the operational impact?
```

---

# PowerView

PowerView provides PowerShell-based AD enumeration capabilities.

Common categories include:

```text
Domain information
Users
Groups
Computers
ACLs
Sessions
Trusts
GPOs
SPNs
```

Where possible, understand equivalent native or LDAP queries rather than depending exclusively on one tool.

---

# Kerberoasting

Kerberoasting concerns Kerberos service tickets associated with service accounts.

Conceptually:

```text
Domain User
     |
     v
Identify SPN
     |
     v
Request Service Ticket
     |
     v
Ticket Material
     |
     v
Offline Password Analysis
```

The important security issue is often the strength and management of service-account credentials.

---

# AS-REP Roasting

Certain accounts may be configured without Kerberos pre-authentication.

Conceptually:

```text
Account
   |
   | Pre-authentication not required
   v
AS-REQ
   |
   v
AS-REP Material
   |
   v
Offline Password Analysis
```

This is configuration-dependent.

---

# Password Spraying

Password spraying tests a small number of candidate passwords against multiple accounts.

It differs from traditional brute force:

```text
Brute Force

One account
    |
    +--> password1
    +--> password2
    +--> password3
    +--> ...
```

versus:

```text
Password Spray

Candidate Password
       |
       +--> User A
       +--> User B
       +--> User C
       +--> User D
```

Password spraying can lock accounts or trigger security controls.

Only perform it when explicitly permitted.

---

# Credential Sources

Credentials may exist in many locations:

```text
LSASS
SAM
LSA Secrets
NTDS.dit
Registry
Configuration files
Scripts
Scheduled tasks
Services
Group Policy
Shares
User descriptions
PowerShell history
Deployment systems
Backups
Password managers
Browsers
Service accounts
LAPS
gMSA
dMSA
```

Credential discovery should be systematic rather than tool-driven.

---

# LAPS

Local Administrator Password Solution technologies are designed to manage local administrator credentials.

During authorised assessments, review:

```text
Is LAPS deployed?

Which systems use it?

Who can read the managed password?

Are permissions appropriately restricted?

Are legacy and modern LAPS configurations understood?
```

The security question is not merely:

```text
Does LAPS exist?
```

but:

```text
Who can retrieve which credentials?
```

---

# gMSA

Group Managed Service Accounts provide managed credentials for services.

Important questions include:

```text
Which gMSAs exist?

Which hosts use them?

Which principals can retrieve their managed password material?

What privileges do those accounts possess?
```

---

# Shadow Credentials

Active Directory certificate-based authentication relationships can create paths involving the `msDS-KeyCredentialLink` attribute.

The important review questions include:

```text
Who can modify the target object?

Can key credentials be added?

What authentication capability would that provide?

How should the change be detected and remediated?
```

This topic will receive a dedicated note.

---

# Active Directory Certificate Services

AD CS adds a Public Key Infrastructure to Active Directory.

It introduces:

```text
Certificate Authorities
Certificate Templates
Enrolment permissions
Certificate authentication
PKINIT
Web enrolment
Certificate mappings
```

Simplified:

```text
User / Computer
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

Misconfiguration can create privilege-escalation paths.

---

# AD CS ESC Paths

AD CS research commonly describes certificate-service escalation conditions using ESC identifiers.

Our AD CS section will cover:

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
```

Each page should explain:

```text
What the condition is
Why it matters
Prerequisites
Enumeration
Safe validation
Attack-path implications
Detection
Remediation
```

rather than merely presenting a command.

---

# NTLM Relay

NTLM authentication can become relayable depending on the protocol and protections involved.

Conceptually:

```text
Victim
  |
  | NTLM Authentication
  v
Attacker
  |
  | Relay
  v
Target Service
```

Important protections include, depending on the target protocol:

```text
SMB signing
LDAP signing
Channel binding
EPA
Protocol-specific protections
```

Do not assume:

```text
NTLM enabled
    =
NTLM relay vulnerability
```

The target service and protections matter.

---

# Authentication Coercion

Some techniques can cause a Windows system to initiate authentication to another host.

Conceptually:

```text
Attacker
   |
   v
Trigger Authentication Behaviour
   |
   v
Target System
   |
   v
Outbound Authentication
   |
   v
Attacker-Controlled / Relay Destination
```

Coercion and relay are separate concepts.

A coercion primitive is not automatically exploitable without a useful authentication destination and suitable target conditions.

---

# Delegation

Kerberos delegation allows services to act on behalf of users.

Important models include:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

Delegation relationships should be mapped during enumeration.

---

# Unconstrained Delegation

Conceptually:

```text
User
 |
 v
Service
 |
 v
Delegated Authentication Material
```

Systems trusted for unconstrained delegation require particular attention.

---

# Constrained Delegation

Constrained delegation limits the services to which delegation is allowed.

Review:

```text
Which account is trusted?

Which target SPNs are permitted?

Which users are protected?

What protocol transition settings exist?
```

---

# Resource-Based Constrained Delegation

RBCD moves part of the delegation decision to the target resource.

Important objects and permissions should be analysed as relationships rather than as isolated settings.

---

# Machine Account Quota

Active Directory can allow ordinary users to create a limited number of computer accounts depending on domain configuration.

Review:

```text
Current MachineAccountQuota
Who can create computer objects
Where they can be created
Whether those objects can participate in other attack paths
```

A non-zero value is not automatically an exploitable vulnerability.

Context matters.

---

# Trusts

Large environments may contain multiple domains and forests.

Example:

```text
Forest A
   |
   +--> Domain A
   |
   +--> Domain B

          |
          | Trust
          v

Forest B
   |
   +--> Domain C
```

Trust analysis should consider:

```text
Direction
Transitivity
SID filtering
Selective authentication
Forest boundaries
Privileged identities
```

---

# Lateral Movement

Lateral movement means using obtained access to reach additional systems.

Potential administration technologies include:

```text
SMB
WinRM
WMI
DCOM
RDP
PowerShell Remoting
Scheduled Tasks
Services
```

The presence of a protocol does not mean the current account can use it.

Always determine:

```text
Credentials
Privileges
Network reachability
Host protections
Logging/detection impact
```

---

# Pivoting

Pivoting becomes necessary when a compromised system can access networks that the tester cannot directly reach.

Example:

```text
Tester
  |
  v
10.10.10.20
Compromised Host
  |
  +------------------+
  |                  |
  v                  v
10.10.10.0/24    172.16.50.0/24
                     |
                     +--> DC02
                     +--> SQL01
                     +--> FILE02
```

The compromised host becomes a network pivot.

---

# Pivoting Models

Important models include:

```text
Local Port Forwarding
Remote Port Forwarding
Dynamic SOCKS Proxy
TUN-Based Routing
Double Pivoting
```

---

# Port Forwarding

Conceptually:

```text
Local Port
    |
    v
Tunnel
    |
    v
Remote Service
```

Useful when only one or a few services need to be reached.

---

# SOCKS Proxy

Conceptually:

```text
Tool
 |
 v
SOCKS Proxy
 |
 v
Pivot Host
 |
 v
Internal Network
```

Tools that support SOCKS directly, or through ProxyChains, can then communicate through the pivot.

---

# TUN-Based Pivoting

Tools such as Ligolo-ng can create a routing-oriented workflow.

Conceptually:

```text
Linux Routing Table
        |
        v
TUN Interface
        |
        v
Ligolo Tunnel
        |
        v
Pivot Host
        |
        v
Internal Network
```

This can be convenient because many tools can communicate with the target subnet using normal IP networking.

---

# Common Pivoting Tools

The pivoting section will cover:

```text
SSH
ProxyChains
Ligolo-ng
Chisel
socat
Windows netsh portproxy
```

The objective is to understand the network model first and tool syntax second.

---

# Double Pivoting

Sometimes the target network contains multiple inaccessible layers.

```text
Tester
  |
  v
Pivot 1
10.10.10.20
  |
  v
Pivot 2
172.16.50.30
  |
  v
10.50.20.0/24
```

At each stage record:

```text
Interfaces
Routes
Reachable networks
DNS
Firewall restrictions
Tunnel direction
```

---

# Shares

SMB shares can expose:

```text
Configuration
Scripts
Backups
Credentials
Deployment packages
Documents
Source code
Certificates
Keys
Installation files
```

Share enumeration should include both:

```text
Share existence
```

and:

```text
Actual permissions
```

---

# Deployment Infrastructure

Enterprise Windows environments may contain:

```text
SCCM
MDT
WSUS
SCOM
PXE
```

These systems can be security-sensitive because they may manage large numbers of endpoints.

Review:

```text
Credentials
Deployment permissions
Network exposure
Service accounts
Administrative roles
Configuration
```

---

# Active Directory Integrated DNS

AD-integrated DNS stores DNS information in Active Directory.

Review areas can include:

```text
DNS records
Record permissions
Dynamic updates
Name-resolution behaviour
ADIDNS permissions
```

---

# ADFS

Active Directory Federation Services may connect AD identities to federated applications.

Review:

```text
Federation configuration
Certificates
Service accounts
Trust relationships
Authentication policies
Endpoints
```

---

# Privilege Escalation

AD privilege escalation rarely consists of only one technique.

Think in chains:

```text
Current Principal
       |
       v
Available Relationships
       |
       v
New Principal / Host
       |
       v
New Permissions
       |
       v
Higher Privilege
```

Examples of contributing relationships may include:

```text
Group membership
ACL permissions
Credential exposure
Kerberos configuration
Delegation
Certificate templates
Local administrator reuse
Sessions
GPO permissions
Trust relationships
```

---

# Domain Admin Is Not the Only Objective

Do not evaluate security solely by asking whether Domain Admin was obtained.

High-impact access may include:

```text
Certificate Authority control
Identity infrastructure
SCCM control
Backup infrastructure
Virtualisation infrastructure
Tier-0 systems
Password management
Federation infrastructure
Security tooling
Critical application servers
```

---

# Persistence

Persistence techniques should only be tested when explicitly authorised.

Potential AD persistence areas include:

```text
Privileged group membership
ACL modifications
GPO modification
Certificate-based persistence
Account manipulation
Kerberos-related persistence
Directory object modification
Trust manipulation
```

For many assessments, demonstrating the ability to establish persistence may be sufficient without actually implementing long-lived persistence.

---

# Tooling Model

Our AD notes will separate techniques from tools.

```text
                  Technique
                     |
        +------------+-------------+
        |            |             |
        v            v             v
     Windows       Linux        Graph
        |            |             |
        v            v             v
   PowerShell     NetExec      BloodHound
   PowerView      Impacket
   Rubeus         Certipy
   Native tools   bloodyAD
                  ldapsearch
                  Responder
```

---

# Planned AD Tool Notes

Dedicated tool notes will cover:

```text
NetExec
Impacket
Responder
BloodHound
SharpHound
Certipy
bloodyAD
PowerView
ldapsearch
Kerbrute
Mimikatz
Rubeus
Evil-WinRM
```

This prevents every technique page from becoming a duplicate tool manual.

---

# NetExec Role

Think of NetExec primarily as:

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

It can help answer questions such as:

```text
Which hosts speak SMB?

Which credentials authenticate?

Where does an account have local administrative access?

Which shares are accessible?

What domain information is available through LDAP?
```

---

# Impacket Role

Think of Impacket as:

```text
Protocol Implementations
         |
         v
Windows / AD Operations
```

Different Impacket examples target different protocols and authentication mechanisms.

Understanding those differences is more valuable than memorising command names.

---

# Responder Role

Think of Responder as part of:

```text
Name Resolution
      |
      v
Authentication Behaviour
      |
      v
Credential Capture Analysis
```

and potentially:

```text
Authentication
      |
      v
Relay Analysis
```

when used with appropriate relay tooling and authorised scope.

---

# Certipy Role

Certipy is commonly used to assess Active Directory Certificate Services.

Typical workflow:

```text
Discover CA
    |
    v
Discover Templates
    |
    v
Analyse Permissions
    |
    v
Identify Misconfiguration
    |
    v
Validate Attack Path
```

---

# BloodHound Role

BloodHound answers:

```text
How are all these relationships connected?
```

while tools such as NetExec, PowerView and LDAP queries often help answer:

```text
What objects and relationships exist?
```

---

# Manual Validation

Automated tools should produce:

```text
Candidates
```

not unquestioned conclusions.

For example:

```text
BloodHound Edge
      |
      v
Read Permission Semantics
      |
      v
Confirm Principal
      |
      v
Confirm Target
      |
      v
Confirm Effective Permission
      |
      v
Determine Exploitability
```

---

# Evidence Collection

Maintain evidence throughout the assessment.

Useful evidence includes:

```text
Command
Timestamp
Source host
Target host
Authenticated identity
Output
Relevant object
Permission
Attack path
Runtime validation
```

---

# Maintain a Target Inventory

Example:

| Host | IP | Role | Services | Access |
|---|---|---|---|---|
| DC01 | 10.10.10.10 | Domain Controller | DNS/Kerberos/LDAP/SMB | Domain user |
| FILE01 | 10.10.10.20 | File Server | SMB | Read share |
| APP01 | 10.10.10.30 | Application | HTTP/WinRM | Unknown |

---

# Maintain a Credential Inventory

Do not store unnecessary plaintext credentials in engagement notes.

A conceptual inventory can track:

| Identity | Type | Source | Access |
|---|---|---|---|
| alice | Domain user | Provided | LDAP/SMB |
| svc_app | Service account | Assessment finding | APP01 |
| admin1 | Privileged user | Session observation | SERVER01 |

Protect assessment data appropriately.

---

# Maintain an Attack Path Log

Example:

```text
alice
 |
 | MemberOf
 v
Helpdesk
 |
 | GenericWrite
 v
svc_backup
 |
 | Administrative access
 v
BACKUP01
```

For each edge record:

```text
Evidence
Required permissions
Validation
Impact
Remediation
```

---

# Windows and Linux Workflows

The notes will show both approaches where practical.

Example:

```text
              Enumerate Domain
                     |
          +----------+----------+
          |                     |
          v                     v
       Windows                Linux
          |                     |
          v                     v
     Native tools            LDAP
     PowerShell              NetExec
     PowerView               Impacket
     SharpHound              bloodyAD
          |                     |
          +----------+----------+
                     |
                     v
                  Analyse
```

---

# Native Tools Matter

Do not rely exclusively on third-party tooling.

Useful Windows-native commands include:

```text
whoami
net
nltest
setspn
klist
dsquery
certutil
PowerShell AD cmdlets where installed
```

Native tooling can be useful when:

```text
EDR blocks tooling
Internet access is unavailable
Tools cannot be transferred
You need to verify automated results
```

---

# Active Directory Assessment Phases

A practical assessment can be divided into:

```text
Phase 1 - Network Discovery
Phase 2 - Domain Discovery
Phase 3 - Identity Enumeration
Phase 4 - Host Enumeration
Phase 5 - Permission Enumeration
Phase 6 - Attack Path Analysis
Phase 7 - Credential Exposure
Phase 8 - Authentication Testing
Phase 9 - Privilege Escalation
Phase 10 - Lateral Movement
Phase 11 - Pivoting
Phase 12 - Infrastructure Assessment
Phase 13 - Trust Analysis
Phase 14 - Impact Validation
Phase 15 - Detection and Remediation
```

---

# Phase 1 - Network Discovery

Identify:

```text
IP configuration
DNS
Routes
Subnets
Domain Controllers
Windows hosts
Management services
```

---

# Phase 2 - Domain Discovery

Identify:

```text
Domain name
Forest name
Domain Controllers
DNS namespace
Trusts
Sites
```

---

# Phase 3 - Identity Enumeration

Identify:

```text
Users
Groups
Service accounts
Computer accounts
Managed service accounts
Privileged identities
Disabled accounts
```

---

# Phase 4 - Host Enumeration

Identify:

```text
Servers
Workstations
Domain Controllers
File servers
Management servers
Certificate authorities
Deployment infrastructure
```

---

# Phase 5 - Permission Enumeration

Identify:

```text
Group membership
ACLs
ACE inheritance
GPO permissions
Local administrator relationships
Remote management permissions
Certificate permissions
```

---

# Phase 6 - Attack Path Analysis

Use:

```text
Manual analysis
BloodHound
LDAP
PowerView
bloodyAD
```

to identify relationships that may connect the current identity to additional privilege.

---

# Phase 7 - Credential Exposure

Review:

```text
Shares
Configuration
Scripts
Services
Scheduled tasks
Managed accounts
Local credentials
Backups
Deployment systems
Directory attributes
```

---

# Phase 8 - Authentication Testing

Review:

```text
Kerberos
NTLM
Password policy
Password spraying where authorised
Roasting conditions
Relay protections
Certificate authentication
```

---

# Phase 9 - Privilege Escalation

Investigate confirmed relationships such as:

```text
ACL control
Group control
Credential access
Delegation
AD CS
GPO control
Service account access
Local administrative access
```

---

# Phase 10 - Lateral Movement

Determine:

```text
Where can the current identity authenticate?

Where is it administrator?

Which remote management protocol is available?

What new network position does the host provide?
```

---

# Phase 11 - Pivoting

After obtaining access to a host:

```text
Enumerate interfaces
Enumerate routes
Enumerate DNS
Identify new subnets
Determine reachability
```

Then choose an appropriate pivoting method.

---

# Phase 12 - Infrastructure Assessment

Review:

```text
AD CS
SCCM
WSUS
MDT
ADFS
DNS
Shares
PXE
Backup infrastructure
```

where these systems are within scope.

---

# Phase 13 - Trust Analysis

Identify:

```text
Domain trusts
Forest trusts
Trust direction
Transitivity
SID filtering
Cross-domain privileges
```

---

# Phase 14 - Impact Validation

The objective is not to cause disruption.

Demonstrate the minimum required to prove:

```text
Unauthorised access
Privilege escalation
Credential exposure
Lateral movement
Domain impact
Cross-domain impact
```

---

# Phase 15 - Detection and Remediation

For each confirmed attack path identify:

```text
Root cause
Affected objects
Relevant logs
Detection opportunities
Preventive control
Remediation
Regression test
```

---

# Active Directory Testing Checklist

## Initial Position

```text
[ ] Current IP identified
[ ] Network interfaces identified
[ ] Routes identified
[ ] DNS servers identified
[ ] Current identity identified
[ ] Domain membership identified
[ ] Privilege level identified
```

## Domain

```text
[ ] Domain identified
[ ] Forest identified
[ ] Domain Controllers identified
[ ] DNS records reviewed
[ ] LDAP reachable
[ ] Kerberos reachable
[ ] SMB reachable
```

## Identities

```text
[ ] Users enumerated
[ ] Groups enumerated
[ ] Nested groups reviewed
[ ] Privileged users identified
[ ] Service accounts identified
[ ] Computer accounts identified
[ ] Managed service accounts considered
```

## Hosts

```text
[ ] Servers enumerated
[ ] Workstations enumerated
[ ] Domain Controllers enumerated
[ ] File servers identified
[ ] Management infrastructure identified
[ ] Certificate authorities identified
```

## Authentication

```text
[ ] Kerberos configuration reviewed
[ ] NTLM behaviour reviewed
[ ] AS-REP roasting conditions reviewed
[ ] Kerberoasting conditions reviewed
[ ] Password policy reviewed
[ ] Password spraying considered only if authorised
[ ] Relay protections reviewed
```

## Authorisation

```text
[ ] Group memberships reviewed
[ ] ACLs reviewed
[ ] ACE inheritance considered
[ ] GPO permissions reviewed
[ ] Delegated administration reviewed
[ ] Local administrator relationships reviewed
```

## Credentials

```text
[ ] Shares reviewed
[ ] Configuration files reviewed
[ ] Scripts reviewed
[ ] Service credentials considered
[ ] Scheduled tasks considered
[ ] LAPS permissions reviewed
[ ] gMSA permissions reviewed
[ ] Credential dumping considered only if authorised
```

## Kerberos

```text
[ ] SPNs enumerated
[ ] Delegation enumerated
[ ] Unconstrained delegation reviewed
[ ] Constrained delegation reviewed
[ ] RBCD reviewed
[ ] Ticket-related attack paths considered
```

## AD CS

```text
[ ] Certificate Authorities discovered
[ ] Templates enumerated
[ ] Enrolment permissions reviewed
[ ] Template permissions reviewed
[ ] ESC conditions assessed
[ ] Certificate authentication paths reviewed
```

## Relay

```text
[ ] SMB signing reviewed
[ ] LDAP signing considered
[ ] Channel binding considered
[ ] Name-resolution protocols reviewed
[ ] Coercion paths considered
[ ] Capture distinguished from relay
```

## Lateral Movement

```text
[ ] Administrative relationships identified
[ ] SMB access reviewed
[ ] WinRM access reviewed
[ ] WMI access reviewed
[ ] RDP access reviewed
[ ] PowerShell Remoting reviewed
```

## Pivoting

```text
[ ] Interfaces enumerated on compromised hosts
[ ] Routes enumerated
[ ] Additional networks identified
[ ] Network reachability tested safely
[ ] Appropriate pivot method selected
[ ] Tunnel routes documented
[ ] DNS requirements considered
```

## Trusts

```text
[ ] Domain trusts enumerated
[ ] Forest trusts enumerated
[ ] Direction reviewed
[ ] Transitivity reviewed
[ ] SID filtering considered
[ ] Cross-domain privileges reviewed
```

---

# Finding Validation

A tool result does not automatically prove a vulnerability.

Use:

```text
Tool Output
    |
    v
Candidate Relationship
    |
    v
Manual Verification
    |
    v
Effective Permission
    |
    v
Reachable Attack Path
    |
    v
Security Impact
```

Examples:

```text
SPN exists
    !=
Compromised service account

Writable ACL
    !=
Automatically exploitable path

NTLM enabled
    !=
Relay vulnerability

Certificate template exists
    !=
ESC vulnerability

SMB available
    !=
Administrative access

Non-zero MachineAccountQuota
    !=
Domain compromise
```

---

# Reporting

A strong AD finding should explain:

```text
Initial privilege
        |
        v
Misconfiguration / Exposure
        |
        v
Attack Path
        |
        v
Resulting Privilege
        |
        v
Business Impact
```

For example:

```text
Low-privileged domain user
        |
        v
Excessive directory permission
        |
        v
Control of service account
        |
        v
Administrative access to server
```

This is more useful than simply reporting:

```text
GenericWrite found.
```

---

# Detection

Detection should be considered alongside offensive testing.

Potential data sources include:

```text
Windows Security logs
Directory Service logs
PowerShell logs
Sysmon
Defender for Identity
EDR
Network telemetry
Certificate Services logs
Domain Controller logs
Authentication logs
```

Each detailed technique page should include relevant detection considerations.

---

# Remediation Philosophy

Prefer fixing the root cause of the attack path.

Example:

```text
Attack Path
   |
   v
Excessive ACL
   |
   v
Credential Control
   |
   v
Server Administration
```

The correct remediation may involve:

```text
Removing excessive ACL
Reducing group membership
Separating administrative tiers
Rotating credentials
Hardening authentication
Restricting remote administration
Monitoring sensitive changes
```

rather than simply blocking the tool used to discover the path.

---

# Cheatsheet Strategy

The detailed AD notes explain:

```text
Why
How
Prerequisites
Security model
Detection
Remediation
```

The Active Directory cheatsheet will provide:

```text
Quick commands
Enumeration syntax
Tool syntax
Common queries
Authentication formats
Assessment reminders
```

Conceptually:

```text
Detailed AD Notes
       |
       v
Understanding
       |
       +------------------+
       |                  |
       v                  v
Assessment            Cheatsheet
Methodology          Quick Reference
```

The cheatsheet should not replace the detailed notes.

---

# Planned Active Directory Notes

The section will progressively cover:

```text
Active Directory Overview
Methodology
Enumeration

Authentication
  Kerberos
  NTLM
  AS-REP Roasting
  Kerberoasting
  Pass-the-Hash
  Overpass-the-Hash
  Pass-the-Key

Access Control
  ACL / ACE
  Groups
  Group Policy
  Machine Account Quota

Credentials
  Password Spraying
  Credential Exposure
  NTDS
  Group Policy Preferences
  LAPS
  gMSA
  dMSA
  DSRM
  Shadow Credentials

Kerberos
  Tickets
  S4U
  Unconstrained Delegation
  Constrained Delegation
  Resource-Based Constrained Delegation

Relay
  Responder
  NTLM Capture
  NTLM Relay
  Kerberos Relay
  Coercion

AD CS
  Enumeration
  ESC1-ESC15
  Golden Certificates

Lateral Movement
  SMB
  WinRM
  WMI
  DCOM
  RDP
  PowerShell Remoting

Pivoting
  SSH
  ProxyChains
  Chisel
  Ligolo-ng
  socat
  Windows portproxy

Trusts
  Relationships
  SID-related paths
  Trust Tickets

Infrastructure
  Shares
  ADIDNS
  ADFS
  SCCM
  WSUS
  MDT
  SCOM
  PXE
  RODC

Privilege Escalation
Persistence
```

---

# Planned Tool Notes

Separate tool notes will cover:

```text
NetExec
Impacket
Responder
BloodHound
SharpHound
Certipy
bloodyAD
PowerView
ldapsearch
Kerbrute
Mimikatz
Rubeus
Evil-WinRM
```

This keeps:

```text
Technique
```

separate from:

```text
Tool
```

while linking them together where appropriate.

---

# Final Active Directory Model

```text
                         NETWORK ACCESS
                              |
                              v
                         DISCOVERY
                              |
                              v
                       DOMAIN DISCOVERY
                              |
                              v
                        ENUMERATION
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       IDENTITIES           HOSTS              TRUSTS
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                        BLOODHOUND
                              |
                              v
                       ATTACK PATHS
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       KERBEROS              NTLM              ACL / GPO
          |                   |                   |
          +-------------------+-------------------+
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
        CREDENTIALS                           AD CS
             |                                 |
             +----------------+----------------+
                              |
                              v
                    PRIVILEGE ESCALATION
                              |
                              v
                     LATERAL MOVEMENT
                              |
                              v
                         PIVOTING
                              |
                              v
                  ADDITIONAL NETWORKS
                              |
                              v
                    INFRASTRUCTURE
                              |
                              v
                         TRUSTS
                              |
                              v
                    DOMAIN / FOREST IMPACT
```

The central principle is:

```text
Active Directory penetration testing
is attack-path analysis.
```

Do not ask only:

```text
"What vulnerability exists?"
```

Also ask:

```text
"What can this identity reach?"

"What does it control?"

"What credentials can it access?"

"What authentication paths are available?"

"What trusts it?"

"What network can it reach?"

"What happens if these relationships are chained together?"
```

---

# References

## Microsoft Active Directory Domain Services

[Microsoft Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/)

## Microsoft Active Directory Domain Services Overview

[Microsoft Active Directory Domain Services Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview)

## Microsoft Kerberos Authentication

[Microsoft Kerberos Authentication](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)

## Microsoft NTLM

[Microsoft NTLM](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview)

## Microsoft LDAP

[Microsoft LDAP](https://learn.microsoft.com/en-us/windows/win32/adsi/ldap-adspath)

## Microsoft Group Policy

[Microsoft Group Policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview)

## Microsoft Active Directory Certificate Services

[Microsoft Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview)

## BloodHound

[BloodHound](https://bloodhound.specterops.io/)

## NetExec

[NetExec](https://www.netexec.wiki/)

## NetExec GitHub

[NetExec GitHub](https://github.com/Pennyw0rth/NetExec)

## Impacket

[Impacket](https://github.com/fortra/impacket)

## Responder

[Responder](https://github.com/lgandx/Responder)

## Certipy

[Certipy](https://github.com/ly4k/Certipy)

## bloodyAD

[bloodyAD](https://github.com/CravateRouge/bloodyAD)

## PowerView

[PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon)

## Rubeus

[Rubeus](https://github.com/GhostPack/Rubeus)

## Ligolo-ng

[Ligolo-ng](https://github.com/nicocha30/ligolo-ng)

## Chisel

[Chisel](https://github.com/jpillora/chisel)

## InternalAllTheThings - Active Directory

[InternalAllTheThings - Active Directory](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/)

---

# Next

Continue with:

```text
docs/active-directory/methodology.md
```

The methodology page should turn this overview into a practical engagement workflow:

```text
Unauthenticated
      |
      v
Domain User
      |
      v
Local Admin
      |
      v
New Host
      |
      v
New Network
      |
      v
Higher Privilege
```

with separate **Kali/Linux and Windows workflows**, evidence collection, NetExec/Impacket/PowerView/BloodHound integration, OPSEC considerations, pivoting decisions, attack-path tracking, and a reusable assessment checklist.
