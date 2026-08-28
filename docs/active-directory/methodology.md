# Active Directory Penetration Testing Methodology

Active Directory penetration testing should be performed as a structured process rather than as a collection of unrelated tools and commands.

The objective is to understand how an attacker could move from the starting position provided by the engagement to progressively more valuable identities, systems, network segments, and ultimately business-critical infrastructure.

A useful model is:

```text
Starting Position
       |
       v
Network Context
       |
       v
Domain Discovery
       |
       v
Enumeration
       |
       v
Attack Surface Mapping
       |
       v
Attack Path Analysis
       |
       v
Controlled Validation
       |
       v
New Access
       |
       v
Re-enumeration
       |
       v
Impact
       |
       v
Detection + Remediation
```

The methodology should remain applicable whether the assessment starts with:

```text
No credentials
Domain credentials
VPN access
A workstation
A shell
Local administrator access
A compromised server
An assumed breach scenario
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

Active Directory testing can affect authentication, endpoints, Domain Controllers, certificate services, and other critical infrastructure.

Before testing, confirm the rules of engagement for techniques such as:

```text
Password spraying
Credential capture
NTLM relay
Authentication coercion
Credential dumping
Remote command execution
Service creation
Scheduled task creation
Account creation
Group membership modification
ACL modification
GPO modification
Certificate enrolment
Persistence
Domain Controller interaction
Trust exploitation
```

Use the least intrusive technique necessary to demonstrate the security issue.

---

# Core Principle

Active Directory penetration testing is primarily:

```text
Attack Path Analysis
```

rather than:

```text
Run every AD tool
```

The central question is:

```text
What can the current identity reach or control?
```

Then:

```text
What new identity, system, permission,
credential, or network position does that provide?
```

The process repeats.

```text
Enumerate
   |
   v
Analyse
   |
   v
Validate
   |
   v
Gain New Context
   |
   v
Enumerate Again
```

---

# Assessment Phases

A practical Active Directory assessment can be divided into:

```text
 1. Scope and Rules of Engagement
 2. Starting Position
 3. Local Network Context
 4. Network Discovery
 5. Domain Discovery
 6. Unauthenticated Enumeration
 7. Authenticated Enumeration
 8. Identity Mapping
 9. Host and Service Mapping
10. Share and Data Discovery
11. BloodHound Collection
12. ACL and Permission Analysis
13. Authentication Analysis
14. Credential Exposure
15. Kerberos Analysis
16. NTLM and Relay Analysis
17. AD CS Analysis
18. Privilege Escalation
19. Lateral Movement
20. Pivoting
21. Re-enumeration
22. Trust Analysis
23. Enterprise Infrastructure
24. Domain / Forest Impact
25. Persistence Assessment
26. Detection Review
27. Evidence and Reporting
28. Retesting
```

Not every engagement will require every phase.

---

# Methodology Overview

```text
                    AUTHORISED ACCESS
                           |
                           v
                   STARTING POSITION
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       No Credentials   Domain User   Host Access
             |             |             |
             +-------------+-------------+
                           |
                           v
                    NETWORK CONTEXT
                           |
                           v
                   DOMAIN DISCOVERY
                           |
                           v
                      ENUMERATION
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
     Identities           Hosts          Infrastructure
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                      BLOODHOUND
                           |
                           v
                    ATTACK PATHS
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
     Kerberos             NTLM             ACL / GPO
        |                  |                  |
        +------------------+------------------+
                           |
                 +---------+---------+
                 |                   |
                 v                   v
            Credentials             AD CS
                 |                   |
                 +---------+---------+
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
                 NEW NETWORK CONTEXT
                           |
                           v
                    RE-ENUMERATION
                           |
                           v
                        TRUSTS
                           |
                           v
                DOMAIN / FOREST IMPACT
```

---

# 1. Scope and Rules of Engagement

Before interacting with the environment, establish exactly what is permitted.

Record:

```text
Target organisation
Target domains
Target forests
Allowed IP ranges
Excluded IP ranges
Provided credentials
Provided hosts
Testing window
Allowed tools
Restricted tools
Allowed protocols
Password spraying permission
Credential dumping permission
Relay permission
Coercion permission
Remote execution permission
Persistence permission
Social engineering permission
Data access restrictions
Production restrictions
```

Do not assume that because Active Directory is in scope, every system joined to the domain is also in scope.

---

# Define Intrusiveness

Classify planned activities.

Example:

| Activity | Typical Intrusiveness |
|---|---|
| DNS enumeration | Low |
| LDAP enumeration | Low |
| SMB share enumeration | Low |
| BloodHound collection | Low to Moderate |
| Kerberoasting | Low to Moderate |
| Password spraying | Moderate |
| Credential capture | Moderate |
| Authentication coercion | Moderate to High |
| NTLM relay | High |
| Credential dumping | High |
| Remote execution | High |
| Account modification | High |
| GPO modification | Very High |
| Persistence | Very High |

The actual risk depends on the environment and implementation.

---

# 2. Determine the Starting Position

Document the exact starting position.

Examples:

```text
Scenario A
---------
Internal network access
No credentials
Kali Linux

Scenario B
---------
Internal network access
Domain user credentials
Kali Linux

Scenario C
---------
Domain-joined Windows workstation
Standard domain user

Scenario D
---------
Windows server
Local administrator

Scenario E
---------
Compromised application server
Two network interfaces
Domain service account
```

The starting position determines the first enumeration strategy.

---

# Starting Position Questions

Ask:

```text
What identity do I have?

What host am I on?

Is the host domain joined?

What network am I on?

What DNS server am I using?

What routes exist?

What credentials are available?

What privileges does the current user have?

Can I reach the Domain Controllers?

Can I resolve the domain?

Can I authenticate to LDAP or SMB?
```

---

# 3. Local Network Context

Before scanning the network, understand the current host.

---

# Linux

Identify interfaces:

```bash
ip addr
```

Routes:

```bash
ip route
```

DNS:

```bash
cat /etc/resolv.conf
```

Hostname:

```bash
hostname
```

Current identity:

```bash
id
```

ARP/neighbour information:

```bash
ip neigh
```

---

# Windows

Identity:

```cmd
whoami
```

Full token information:

```cmd
whoami /all
```

Hostname:

```cmd
hostname
```

Network configuration:

```cmd
ipconfig /all
```

Routes:

```cmd
route print
```

ARP cache:

```cmd
arp -a
```

Domain:

```cmd
echo %USERDOMAIN%
```

DNS domain:

```cmd
echo %USERDNSDOMAIN%
```

Logon server:

```cmd
echo %LOGONSERVER%
```

---

# PowerShell

```powershell
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:LOGONSERVER
```

Network:

```powershell
Get-NetIPConfiguration
```

Routes:

```powershell
Get-NetRoute
```

Interfaces:

```powershell
Get-NetAdapter
```

---

# Record the Network Position

Example:

```text
Host: kali01
IP: 10.10.20.50
Subnet: 10.10.20.0/24
Gateway: 10.10.20.1
DNS: 10.10.20.10
Domain: corp.example.local
```

This becomes important when pivoting later.

---

# 4. Network Discovery

The objective is not immediately to scan every port on every host.

First determine:

```text
What networks are reachable?

Where are the likely Domain Controllers?

Which hosts expose Windows services?

Where are management services?

Which infrastructure systems are visible?
```

---

# Useful AD Services

Look for services such as:

```text
DNS
Kerberos
LDAP
LDAPS
SMB
RPC
Global Catalog
WinRM
RDP
MSSQL
HTTP/HTTPS
```

Common ports include:

| Port | Service |
|---:|---|
| 53 | DNS |
| 88 | Kerberos |
| 135 | RPC |
| 139 | NetBIOS |
| 389 | LDAP |
| 445 | SMB |
| 464 | Kerberos password operations |
| 636 | LDAPS |
| 3268 | Global Catalog |
| 3269 | Global Catalog TLS |
| 3389 | RDP |
| 5985 | WinRM HTTP |
| 5986 | WinRM HTTPS |

Port presence alone does not identify the security posture of the service.

---

# 5. Domain Discovery

Domain discovery should establish:

```text
Domain name
Forest name
Domain Controllers
DNS namespace
AD sites
Trust relationships
```

---

# Windows Domain Discovery

```cmd
echo %USERDOMAIN%
echo %USERDNSDOMAIN%
```

Find a Domain Controller:

```cmd
nltest /dsgetdc:example.local
```

List Domain Controllers:

```cmd
nltest /dclist:example.local
```

Trust information:

```cmd
nltest /domain_trusts
```

---

# DNS Discovery

Domain Controllers are advertised through DNS SRV records.

LDAP:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

Global Catalog:

```bash
dig SRV _gc._tcp.example.local
```

---

# RootDSE

LDAP RootDSE can reveal directory metadata.

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -s base \
  -b "" \
  defaultNamingContext \
  rootDomainNamingContext \
  configurationNamingContext \
  dnsHostName
```

Possible output may identify:

```text
Domain naming context
Forest root
Configuration partition
Domain Controller hostname
```

---

# 6. Unauthenticated Enumeration

If no credentials are available, determine what information can be obtained without authentication.

Potential areas include:

```text
DNS
SMB configuration
Anonymous SMB
LDAP RootDSE
RPC exposure
Kerberos username validation
Name-resolution behaviour
Web applications
Management interfaces
Certificate services
```

Do not immediately attempt password attacks.

Build the environment map first.

---

# SMB

Basic NetExec host identification:

```bash
nxc smb 10.10.20.10
```

Against a subnet:

```bash
nxc smb 10.10.20.0/24
```

This can help identify:

```text
Hostname
Domain
SMB signing configuration
SMB dialect information
```

depending on the target and tool version.

---

# Anonymous SMB

Where authorised, test whether anonymous or guest access is exposed.

For example:

```bash
smbclient -L //10.10.20.10 -N
```

Do not interpret a failed anonymous query as evidence that SMB is securely configured overall.

---

# RPC

RPC may expose useful information depending on server configuration.

Example:

```bash
rpcclient -U "" -N 10.10.20.10
```

If a connection succeeds, determine what operations are actually permitted.

---

# 7. Authenticated Enumeration

A normal domain account often provides significant directory visibility.

Once valid credentials are available, systematically enumerate:

```text
Domain
Users
Groups
Computers
Domain Controllers
SPNs
Delegation
Trusts
Password policy
Shares
Sessions
ACLs
GPOs
AD CS
```

---

# Credential Format

Keep authentication variables conceptually separate:

```text
DOMAIN
USERNAME
PASSWORD
NTLM HASH
KERBEROS TICKET
AES KEY
TARGET
DOMAIN CONTROLLER
```

This prevents mistakes when switching tools.

Example lab values:

```text
Domain: example.local
Username: alice
Target: dc01.example.local
DC IP: 10.10.20.10
```

---

# NetExec Workflow

NetExec is particularly useful for protocol-oriented enumeration.

Start with:

```bash
nxc smb 10.10.20.0/24
```

Then validate provided credentials:

```bash
nxc smb 10.10.20.0/24 \
  -d example.local \
  -u alice \
  -p 'Password'
```

LDAP:

```bash
nxc ldap dc01.example.local \
  -d example.local \
  -u alice \
  -p 'Password'
```

The dedicated NetExec note will cover its functionality in detail.

---

# Avoid Unnecessary Authentication Volume

Do not repeatedly authenticate the same credentials against hundreds or thousands of hosts without considering:

```text
Account lockout
SOC alerts
EDR telemetry
Authentication logs
Network load
Rules of engagement
```

Start narrow.

Expand deliberately.

---

# 8. Identity Mapping

Identify:

```text
Users
Groups
Privileged groups
Service accounts
Computer accounts
Managed service accounts
Disabled accounts
Stale accounts
Administrative accounts
```

---

# Users

Important questions:

```text
Which users exist?

Which are privileged?

Which have SPNs?

Which do not require Kerberos pre-authentication?

Which accounts are service identities?

Which accounts appear stale?

Which accounts have unusual descriptions?

Which accounts can access sensitive systems?
```

---

# Groups

Do not inspect only default privileged groups.

Custom groups frequently matter more.

Examples:

```text
SQL Administrators
Server Support
Backup Administrators
SCCM Administrators
VMware Administrators
Application Support
Certificate Managers
Helpdesk
Tier 0 Operators
```

---

# Nested Groups

Always investigate nested memberships.

```text
Alice
 |
 v
Helpdesk
 |
 v
Server Support
 |
 v
Production Administrators
```

A user may possess privilege indirectly.

---

# 9. Host and Service Mapping

Map computers to:

```text
Hostname
IP
Operating system
Role
Open services
Administrative relationships
Logged-on users
Network segments
```

---

# Host Categories

Useful categories include:

```text
Domain Controllers
Workstations
Application servers
File servers
Database servers
Management servers
Certificate authorities
Backup servers
Virtualisation hosts
Jump servers
Developer systems
Security systems
```

---

# Why Host Role Matters

A server may be more valuable than its local privileges suggest.

For example:

```text
SCCM Server
    |
    v
Endpoint Management
    |
    v
Hundreds of Computers
```

or:

```text
Backup Server
    |
    v
Domain Controller Backups
    |
    v
Domain Credentials
```

---

# 10. Share and Data Discovery

Enumerate accessible SMB shares.

Questions:

```text
Which shares exist?

Which shares can I read?

Which shares can I write?

What sensitive information exists?

Are scripts stored there?

Are credentials stored there?

Are deployment packages stored there?

Are backups exposed?
```

---

# NetExec Share Enumeration

Example:

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -p 'Password' \
  --shares
```

---

# smbclient

List shares:

```bash
smbclient -L //FILE01.example.local \
  -U 'EXAMPLE/alice'
```

Connect:

```bash
smbclient //FILE01.example.local/Share \
  -U 'EXAMPLE/alice'
```

---

# Sensitive Share Content

Look for:

```text
*.xml
*.ini
*.config
*.conf
*.ps1
*.bat
*.cmd
*.vbs
*.kdbx
*.pfx
*.p12
*.pem
*.key
*.rdp
*.sql
*.bak
*.zip
*.7z
```

Also consider:

```text
Passwords
API keys
Connection strings
Service credentials
Deployment credentials
Private keys
Certificates
Backup data
```

Do not collect unnecessary business data.

---

# 11. BloodHound Collection

BloodHound can convert AD relationships into a graph.

Conceptually:

```text
Collection
    |
    v
Directory Objects
    |
    v
Relationships
    |
    v
Graph
    |
    v
Attack Paths
```

---

# BloodHound Is Not a Vulnerability Scanner

Treat BloodHound output as:

```text
Attack Path Candidates
```

not:

```text
Confirmed Vulnerabilities
```

Validate important edges manually.

---

# Important Relationships

Examples include:

```text
MemberOf
AdminTo
HasSession
GenericAll
GenericWrite
WriteDACL
WriteOwner
ForceChangePassword
AddMember
Owns
CanRDP
CanPSRemote
Delegation relationships
Certificate relationships
```

---

# Attack Path Question

Instead of asking:

```text
What can Alice do?
```

ask:

```text
What can Alice reach after one relationship?

What can that new principal reach?

What happens after three relationships?
```

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
 | AdminTo
 v
BACKUP01
 |
 | Sensitive data
 v
Higher Privilege
```

---

# 12. ACL and Permission Analysis

Active Directory permissions are one of the most important attack surfaces.

Review:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
ResetPassword
AddMember
CreateChild
DeleteChild
Extended Rights
```

The exact impact depends on the target object and effective permissions.

---

# ACL Methodology

```text
Principal
    |
    v
Permission
    |
    v
Target Object
    |
    v
Security-Sensitive Attribute / Operation
    |
    v
Resulting Capability
```

Example:

```text
Helpdesk
    |
    | Reset Password
    v
Service Account
    |
    v
New Authentication Context
```

---

# Do Not Stop at the Permission Name

For every interesting ACL:

```text
Who has the permission?

Is it inherited?

What object does it apply to?

What property can be modified?

Can the principal actually exercise it?

What privilege would result?
```

---

# 13. Authentication Analysis

Analyse both:

```text
Kerberos
NTLM
```

and their associated security controls.

---

# Kerberos Questions

```text
Which accounts have SPNs?

Which accounts lack pre-authentication?

Which accounts use delegation?

Which services support Kerberos?

What ticket relationships exist?

Are service-account passwords appropriately managed?
```

---

# NTLM Questions

```text
Where is NTLM still accepted?

Is SMB signing required?

Is LDAP signing enforced?

Is channel binding used where appropriate?

Are systems susceptible to name-resolution poisoning?

Can authentication be coerced?

Are relay destinations available?
```

---

# 14. Credential Exposure

Credential exposure should be assessed systematically.

Potential sources include:

```text
Shares
Scripts
Configuration
Registry
Services
Scheduled tasks
Deployment systems
Backups
Managed accounts
User attributes
PowerShell history
Applications
Local credential stores
```

---

# Credential Access Model

```text
Credential Source
      |
      v
Who Can Read It?
      |
      v
Credential Type
      |
      v
Where Is It Valid?
      |
      v
What Privilege Does It Provide?
```

---

# Credential Reuse

A credential becomes more significant when it works elsewhere.

```text
Credential
   |
   +--> Host A
   |
   +--> Host B
   |
   +--> Host C
```

Avoid uncontrolled credential spraying.

Validate deliberately.

---

# 15. Kerberos Analysis

Important areas include:

```text
AS-REP Roasting
Kerberoasting
Tickets
Delegation
S4U
RBCD
Service accounts
```

---

# Kerberoasting Workflow

```text
Domain User
     |
     v
Enumerate SPNs
     |
     v
Identify Relevant Service Accounts
     |
     v
Request Service Ticket
     |
     v
Offline Analysis
     |
     v
Credential Validation
```

Do not assume every SPN represents a useful or weak credential.

---

# AS-REP Roasting Workflow

```text
Enumerate Users
      |
      v
Identify Accounts Without Pre-Authentication
      |
      v
Request AS-REP
      |
      v
Offline Analysis
```

The root issue is account configuration combined with password strength.

---

# 16. NTLM and Relay Analysis

Separate:

```text
Capture
Coercion
Relay
```

These are related but different.

---

# Capture

```text
Victim
   |
   v
Authentication Attempt
   |
   v
Attacker-Controlled Listener
   |
   v
Captured Challenge/Response Material
```

---

# Coercion

```text
Tester
   |
   v
Trigger
   |
   v
Target System
   |
   v
Outbound Authentication
```

---

# Relay

```text
Victim
   |
   | Authentication
   v
Relay Host
   |
   v
Target Service
```

A successful relay path depends on the destination and its protections.

---

# Responder

Responder can help assess name-resolution and authentication behaviour involving:

```text
LLMNR
NBT-NS
mDNS
```

Use carefully in production environments because poisoning can affect unrelated systems.

The dedicated Responder note will explain safe configuration and validation.

---

# Relay Protection Matrix

During an assessment, track protections.

Example:

| Host | SMB Signing | LDAP Signing | LDAPS | Notes |
|---|---|---|---|---|
| DC01 | Required | Enforced | Yes | DC |
| FILE01 | Not required | N/A | N/A | Review relay exposure |
| APP01 | Required | N/A | N/A | Application server |

Do not report relay exposure without validating the relevant conditions.

---

# 17. AD CS Analysis

If Active Directory Certificate Services is deployed, treat it as a major identity system.

Workflow:

```text
Discover AD CS
      |
      v
Enumerate CAs
      |
      v
Enumerate Templates
      |
      v
Analyse Permissions
      |
      v
Analyse Template Configuration
      |
      v
Identify ESC Conditions
      |
      v
Validate Safely
      |
      v
Determine Identity Impact
```

---

# Certipy

Certipy is commonly used for AD CS assessment.

Example discovery workflow conceptually:

```text
Credentials
    |
    v
Certipy Enumeration
    |
    v
Certificate Authorities
    |
    v
Templates
    |
    v
Candidate Misconfigurations
```

Tool findings should be manually reviewed.

---

# 18. Privilege Escalation

Privilege escalation in AD is usually relationship-driven.

Examples:

```text
Weak ACL
Credential Exposure
Group Membership
Service Account
Delegation
GPO Control
AD CS
Local Administrator Access
Session Exposure
Trust Relationship
```

---

# Escalation Model

```text
Current Principal
        |
        v
Security Relationship
        |
        v
New Capability
        |
        v
New Identity / Host
        |
        v
Higher Privilege
```

---

# Track Each Step

For each escalation:

```text
Source principal
Target object
Permission
Prerequisite
Validation
Result
Evidence
Detection
Remediation
```

---

# 19. Lateral Movement

After obtaining additional credentials or privileges, determine where they are valid.

Potential management protocols include:

```text
SMB
WinRM
WMI
DCOM
RDP
PowerShell Remoting
```

---

# Lateral Movement Decision

```text
Credential
    |
    v
Target Host
    |
    v
Network Reachable?
    |
    +-- No --> Pivot / Route
    |
    +-- Yes
          |
          v
Authentication Valid?
          |
          +-- No --> Stop
          |
          +-- Yes
                |
                v
Required Privilege?
                |
                +-- No --> Enumerate
                |
                +-- Yes
                      |
                      v
              Authorised Validation
```

---

# Administrative Access Mapping

NetExec can assist with identifying systems where credentials have administrative access.

Do not treat authentication success as administrative access.

Keep these states separate:

```text
Authentication Failed

Authentication Successful

Authentication Successful + User Access

Authentication Successful + Administrative Access
```

---

# 20. Pivoting

Pivoting is a core part of internal penetration testing.

After gaining access to a host, immediately inspect:

```text
Interfaces
Routes
DNS
ARP / neighbours
Listening services
Reachable networks
```

---

# Example

```text
Kali
10.10.10.50
   |
   v
WEB01
10.10.10.20
172.16.20.10
   |
   v
172.16.20.0/24
   |
   +--> DC02
   +--> SQL01
   +--> FILE02
```

Kali cannot directly reach:

```text
172.16.20.0/24
```

but WEB01 can.

WEB01 can therefore become a pivot.

---

# Pivoting Decision Tree

```text
Need one remote service?
        |
        +--> Port Forwarding

Need several TCP services?
        |
        +--> SOCKS Proxy

Need tools to treat subnet as routed?
        |
        +--> TUN-Based Pivot

Need access through another pivot?
        |
        +--> Double Pivot
```

---

# Common Pivoting Technologies

Our dedicated pivoting notes will cover:

```text
SSH
ProxyChains
Chisel
Ligolo-ng
socat
netsh portproxy
```

---

# Route Documentation

Always record pivot routes.

Example:

| Network | Reachable Through | Method |
|---|---|---|
| 10.10.10.0/24 | Direct | Local |
| 172.16.20.0/24 | WEB01 | Ligolo-ng |
| 10.50.30.0/24 | APP02 via WEB01 | Double pivot |

Without this documentation, complex internal assessments quickly become confusing.

---

# DNS Through a Pivot

Routing packets does not automatically solve DNS.

Ask:

```text
Which DNS server resolves the internal domain?

Can the tester reach it?

Does the pivot solution route DNS?

Should hostnames be added temporarily to /etc/hosts?

Does Kerberos require correct hostname resolution?
```

Kerberos frequently makes DNS and hostname accuracy particularly important.

---

# 21. Re-Enumeration

Every significant privilege or network change should trigger another enumeration cycle.

```text
New Credential
      |
      v
Re-enumerate

New Host
      |
      v
Re-enumerate

New Network
      |
      v
Re-enumerate

New Group
      |
      v
Re-enumerate

New Domain
      |
      v
Re-enumerate
```

This is one of the most important habits in internal testing.

---

# Why Re-Enumeration Matters

A new identity may reveal:

```text
Additional LDAP objects
Additional shares
Additional hosts
New BloodHound edges
New AD CS templates
New administrative access
New trust relationships
```

A new network position may reveal an entirely different environment.

---

# 22. Trust Analysis

Large AD environments may contain:

```text
Child domains
Parent domains
Multiple forests
External trusts
Forest trusts
```

Enumerate:

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

# Trust Model

```text
Domain A
   |
   | Trust
   v
Domain B
```

Do not interpret a trust as automatic compromise.

Determine what authentication and authorisation relationships actually cross the boundary.

---

# 23. Enterprise Infrastructure

AD assessments should not focus exclusively on Domain Controllers.

High-value infrastructure may include:

```text
AD CS
SCCM
WSUS
MDT
SCOM
ADFS
DNS
PXE
Backup systems
Virtualisation
Password-management systems
Jump hosts
```

These systems may provide broad administrative capability.

---

# Infrastructure Impact

For example:

```text
SCCM
  |
  v
Endpoint Management
  |
  v
Many Domain Computers
```

or:

```text
AD CS
  |
  v
Certificate Authentication
  |
  v
Identity Infrastructure
```

---

# 24. Domain / Forest Impact

The objective is to determine realistic impact, not necessarily to perform every possible action.

Potential high-impact positions include:

```text
Domain Admin
Enterprise Admin
Domain Controller control
Certificate Authority control
SCCM administrative control
Identity federation control
Backup infrastructure control
Tier-0 system control
```

---

# Minimum Necessary Proof

Prefer:

```text
Prove capability
```

rather than:

```text
Perform destructive action
```

For example, if an ACL clearly permits adding a principal to a privileged group, the rules of engagement may allow the attack path to be demonstrated without leaving the modification in place.

Always restore changes made during testing.

---

# 25. Persistence Assessment

Persistence should normally be considered only after impact has been established and only where explicitly authorised.

Review whether an attacker could persist through:

```text
Account manipulation
Group membership
ACL changes
GPO changes
Certificate authentication
Kerberos-related mechanisms
Directory object modification
Trust manipulation
```

The assessment may only need to demonstrate that persistence is possible.

---

# 26. Detection Review

A mature assessment should identify detection opportunities.

Ask:

```text
Would this activity be logged?

Would the SOC see it?

Would EDR detect it?

Would identity monitoring alert?

Would unusual LDAP enumeration be noticed?

Would account changes be detected?

Would certificate enrolment be monitored?

Would relay behaviour be visible?
```

---

# Important Telemetry

Potential sources include:

```text
Windows Security logs
Domain Controller logs
Directory Service logs
PowerShell logs
Sysmon
EDR
Microsoft Defender for Identity
Network telemetry
SMB telemetry
Certificate Services logs
Authentication logs
Firewall logs
DNS logs
```

---

# Purple Team Integration

Where permitted, confirmed paths can be replayed collaboratively.

```text
Red Team
   |
   v
Technique
   |
   v
Telemetry
   |
   v
Blue Team
   |
   v
Detection
   |
   v
Improvement
```

This can transform a penetration-test finding into a reusable detection capability.

---

# 27. Evidence Collection

Evidence collection should happen throughout the engagement.

Do not attempt to reconstruct the attack path at the end.

For every significant action record:

```text
Timestamp
Source host
Source IP
Identity
Target
Tool
Command
Result
Security implication
Evidence file
```

---

# Example Evidence Record

```text
Time:
2026-08-29 10:32

Source:
kali01 - 10.10.20.50

Identity:
EXAMPLE\alice

Target:
FILE01.example.local

Action:
SMB share enumeration

Result:
Authenticated successfully.
Readable share discovered.

Impact:
Share contains deployment configuration requiring review.

Evidence:
evidence/file01-shares.txt
```

---

# Save Tool Output

Example structure:

```text
engagement/
│
├── evidence/
│   ├── dns/
│   ├── ldap/
│   ├── smb/
│   ├── bloodhound/
│   ├── kerberos/
│   ├── adcs/
│   └── screenshots/
│
├── credentials/
├── targets/
├── attack-paths/
└── notes/
```

Protect all assessment data appropriately.

---

# Command Logging

A shell history is not a sufficient engagement record.

Consider logging important commands and results explicitly.

For example:

```bash
nxc smb 10.10.20.0/24 | tee evidence/smb/discovery.txt
```

Avoid storing plaintext passwords in shell history or evidence where possible.

---

# Credential Handling

Treat discovered credentials as sensitive client data.

Avoid unnecessary storage of:

```text
Plaintext passwords
NTLM hashes
Kerberos tickets
Private keys
Certificates
Session tokens
```

Where evidence requires demonstrating credential exposure, redact appropriately.

---

# 28. Retesting

After remediation, verify the root cause.

Do not simply verify that the original command fails.

Example:

```text
Original Finding
      |
      v
Excessive ACL
      |
      v
Remediation
      |
      v
Re-enumerate ACL
      |
      v
Verify Effective Permission Removed
      |
      v
Verify Attack Path Removed
```

This is stronger than:

```text
Tool no longer works.
```

---

# Windows Workflow

A domain-joined Windows assessment may follow:

```text
Current Identity
      |
      v
whoami /all
      |
      v
Network / Domain
      |
      v
Native Enumeration
      |
      v
PowerShell
      |
      v
PowerView
      |
      v
SharpHound
      |
      v
BloodHound
      |
      v
Manual Validation
```

---

# Windows Initial Commands

```cmd
whoami
whoami /all
hostname
ipconfig /all
route print
arp -a
set
```

Domain:

```cmd
echo %USERDOMAIN%
echo %USERDNSDOMAIN%
echo %LOGONSERVER%
```

---

# Native Domain Commands

```cmd
net user /domain
```

Groups:

```cmd
net group /domain
```

Domain Admins:

```cmd
net group "Domain Admins" /domain
```

Current tickets:

```cmd
klist
```

SPNs:

```cmd
setspn -Q */*
```

Use large queries carefully in production environments.

---

# PowerShell Workflow

PowerShell can be used for:

```text
Host enumeration
Domain enumeration
ACL analysis
Network analysis
File discovery
Configuration review
```

Prefer native cmdlets where practical.

---

# Linux / Kali Workflow

A Linux-based internal assessment commonly follows:

```text
Network Context
      |
      v
DNS
      |
      v
SMB Discovery
      |
      v
LDAP
      |
      v
NetExec
      |
      v
Impacket
      |
      v
BloodHound
      |
      v
Certipy
      |
      v
Manual Validation
```

---

# Linux Tool Model

```text
Discovery
  |
  +--> dig
  +--> nmap
  +--> NetExec
  |
Enumeration
  |
  +--> ldapsearch
  +--> NetExec
  +--> Impacket
  +--> bloodyAD
  |
Attack Path Analysis
  |
  +--> BloodHound
  |
AD CS
  |
  +--> Certipy
  |
Authentication Behaviour
  |
  +--> Responder
  +--> Impacket
```

---

# NetExec Methodology

Do not use NetExec merely as:

```text
nxc <protocol> <entire-network> <everything>
```

Use it progressively.

```text
Host Discovery
      |
      v
Protocol Identification
      |
      v
Credential Validation
      |
      v
Focused Enumeration
      |
      v
Privilege Identification
```

---

# NetExec Authentication Examples

Password:

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -p 'Password'
```

NTLM authentication may be possible where authorised and supported:

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -H '<NTLM-HASH>'
```

Use only credential material obtained or provided within the authorised assessment.

---

# NetExec Protocol Selection

Choose the protocol according to the question.

```text
SMB
 |
 +--> Shares
 +--> Host information
 +--> Authentication
 +--> Administrative access

LDAP
 |
 +--> Domain information
 +--> Users
 +--> Groups
 +--> Directory relationships

WinRM
 |
 +--> Remote management access

MSSQL
 |
 +--> SQL Server authentication / access

RDP
 |
 +--> Remote desktop exposure / authentication context
```

The dedicated NetExec page will contain the detailed command reference.

---

# Impacket Methodology

Impacket tools should be selected according to protocol and objective.

Examples:

```text
Kerberos
 |
 +--> GetNPUsers.py
 +--> GetUserSPNs.py
 +--> getTGT.py
 +--> getST.py
 +--> ticketer.py

SMB / Remote Management
 |
 +--> smbclient.py
 +--> psexec.py
 +--> smbexec.py
 +--> wmiexec.py

Credentials
 |
 +--> secretsdump.py

Relay
 |
 +--> ntlmrelayx.py
```

Do not treat Impacket as a single attack tool.

---

# Responder Methodology

Before using Responder, understand:

```text
What protocols will it answer?

What interfaces will it listen on?

Will it poison name-resolution traffic?

Could unrelated users be affected?

Are captures permitted?

Is relay permitted?
```

A safer assessment workflow is:

```text
Understand Environment
      |
      v
Confirm Scope
      |
      v
Configure Only Required Protocols
      |
      v
Observe
      |
      v
Collect Minimum Evidence
      |
      v
Stop
```

---

# BloodHound Methodology

Use BloodHound as an analysis platform.

```text
Collect
   |
   v
Import
   |
   v
Identify Candidate Path
   |
   v
Inspect Each Edge
   |
   v
Validate Permissions
   |
   v
Confirm Practical Path
```

Never report a multi-hop path without understanding the important edges.

---

# Tool Result != Finding

This rule applies throughout AD testing.

```text
NetExec says authentication succeeded
        !=
Administrative compromise

BloodHound shows GenericWrite
        !=
Confirmed escalation

Certipy identifies a template
        !=
Confirmed certificate escalation

Responder captures authentication
        !=
Password recovered

Impacket requests a ticket
        !=
Account compromised

Port 445 open
        !=
SMB vulnerability
```

---

# Attack Path Tracking

Maintain a simple graph while testing.

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
  | AdminTo
  v
BACKUP01
```

Then annotate:

```text
[1] alice -> Helpdesk
    Evidence: LDAP membership

[2] Helpdesk -> svc_backup
    Evidence: ACL

[3] svc_backup -> BACKUP01
    Evidence: administrative access
```

This makes reporting significantly easier.

---

# Attack Path Worksheet

For each path record:

```text
Starting Identity:
Target:
Relationship:
Prerequisite:
Technique:
Validation:
Result:
New Access:
Detection:
Remediation:
Evidence:
```

---

# Re-Enumeration Trigger List

Re-enumerate after obtaining:

```text
[ ] New domain credential
[ ] New local credential
[ ] New NTLM hash
[ ] New Kerberos ticket
[ ] New certificate
[ ] New group membership
[ ] New host access
[ ] Local administrator access
[ ] New network route
[ ] New domain access
[ ] New forest access
```

---

# OPSEC and Safety

Penetration testing and red teaming have different operational objectives, but both should consider the impact of testing.

Avoid unnecessary:

```text
Large-scale authentication attempts
Aggressive LDAP queries
Massive SMB scans
Uncontrolled poisoning
Unnecessary credential dumping
Repeated remote execution
Persistent modifications
Service disruption
Account lockouts
```

---

# Prefer Read-Only Enumeration First

A good progression is:

```text
Read
 |
 v
Understand
 |
 v
Analyse
 |
 v
Validate
 |
 v
Modify only if required
```

---

# Change Tracking

If an assessment requires modifying AD:

```text
Record original value
        |
        v
Perform change
        |
        v
Validate
        |
        v
Restore original value
        |
        v
Verify restoration
```

Examples include:

```text
Group membership
ACL
Attribute
Certificate mapping
Computer account
GPO
```

---

# Active Directory Assessment Checklist

## Scope

```text
[ ] Domains confirmed
[ ] Forests confirmed
[ ] IP ranges confirmed
[ ] Exclusions confirmed
[ ] Credentials documented securely
[ ] Password spraying permission confirmed
[ ] Relay permission confirmed
[ ] Coercion permission confirmed
[ ] Credential dumping permission confirmed
[ ] Remote execution permission confirmed
[ ] Persistence permission confirmed
```

## Starting Position

```text
[ ] Current host identified
[ ] Current identity identified
[ ] Privileges identified
[ ] Domain membership identified
[ ] Network interfaces identified
[ ] Routes identified
[ ] DNS identified
```

## Discovery

```text
[ ] Domain identified
[ ] Forest identified
[ ] Domain Controllers identified
[ ] DNS records reviewed
[ ] SMB identified
[ ] LDAP identified
[ ] Kerberos identified
[ ] Management services identified
```

## Unauthenticated

```text
[ ] RootDSE reviewed
[ ] Anonymous SMB considered
[ ] Anonymous RPC considered
[ ] DNS information reviewed
[ ] Kerberos username enumeration considered where authorised
[ ] Name-resolution behaviour considered
```

## Authenticated Enumeration

```text
[ ] Users enumerated
[ ] Groups enumerated
[ ] Nested groups reviewed
[ ] Computers enumerated
[ ] Domain Controllers enumerated
[ ] SPNs enumerated
[ ] Delegation reviewed
[ ] Trusts enumerated
[ ] Password policy reviewed
[ ] GPOs reviewed
```

## Attack Paths

```text
[ ] BloodHound collection performed where appropriate
[ ] Privileged groups reviewed
[ ] ACLs reviewed
[ ] Sessions considered
[ ] Local administrator relationships reviewed
[ ] Each important edge manually validated
```

## Credentials

```text
[ ] Shares reviewed
[ ] Scripts reviewed
[ ] Configuration reviewed
[ ] Service accounts reviewed
[ ] LAPS permissions reviewed
[ ] gMSA permissions reviewed
[ ] Deployment infrastructure considered
[ ] Credential dumping considered only if authorised
```

## Kerberos

```text
[ ] AS-REP candidates reviewed
[ ] SPN accounts reviewed
[ ] Delegation reviewed
[ ] RBCD reviewed
[ ] Ticket relationships considered
```

## NTLM / Relay

```text
[ ] NTLM usage reviewed
[ ] SMB signing reviewed
[ ] LDAP signing reviewed
[ ] Channel binding considered
[ ] Name-resolution behaviour reviewed
[ ] Coercion considered
[ ] Relay targets considered
```

## AD CS

```text
[ ] CA discovered
[ ] Templates enumerated
[ ] Template permissions reviewed
[ ] CA permissions reviewed
[ ] ESC conditions assessed
[ ] Findings manually validated
```

## Lateral Movement

```text
[ ] SMB administrative access reviewed
[ ] WinRM reviewed
[ ] WMI reviewed
[ ] RDP reviewed
[ ] DCOM reviewed
[ ] PowerShell Remoting reviewed
```

## Pivoting

```text
[ ] Interfaces checked after new host access
[ ] Routes checked
[ ] New subnets identified
[ ] DNS considered
[ ] Pivot method selected
[ ] Routes documented
[ ] Double pivot considered where relevant
```

## Trusts

```text
[ ] Domain trusts reviewed
[ ] Forest trusts reviewed
[ ] Direction reviewed
[ ] Transitivity reviewed
[ ] SID filtering considered
[ ] Cross-domain privileges reviewed
```

## Infrastructure

```text
[ ] AD CS considered
[ ] SCCM considered
[ ] WSUS considered
[ ] MDT considered
[ ] SCOM considered
[ ] ADFS considered
[ ] DNS considered
[ ] PXE considered
[ ] Backup infrastructure considered
```

## Reporting

```text
[ ] Starting privilege documented
[ ] Attack path documented
[ ] Evidence captured
[ ] Impact demonstrated
[ ] Root cause identified
[ ] Detection opportunities documented
[ ] Remediation documented
[ ] Changes reverted
```

---

# Quick Assessment Workflow

When time is limited, use:

```text
1. Identify current network and identity
2. Identify domain and Domain Controllers
3. Enumerate DNS, SMB, LDAP and Kerberos
4. Validate credentials
5. Enumerate users, groups and computers
6. Enumerate shares
7. Collect BloodHound data
8. Review privileged groups and ACLs
9. Review Kerberos attack surface
10. Review NTLM / relay protections
11. Review AD CS
12. Identify credential exposure
13. Identify administrative access
14. Validate the shortest meaningful attack paths
15. Re-enumerate after every access change
16. Check for additional network interfaces and routes
17. Pivot where necessary
18. Review trusts and management infrastructure
19. Determine realistic domain / forest impact
20. Document root causes, detection and remediation
```

---

# Methodology Decision Tree

```text
START
  |
  v
Do I know the domain?
  |
  +-- No --> DNS / RootDSE / SMB / Network Discovery
  |
  +-- Yes
        |
        v
Do I have credentials?
        |
        +-- No
        |     |
        |     v
        |  Unauthenticated Enumeration
        |     |
        |     +--> DNS
        |     +--> SMB
        |     +--> LDAP RootDSE
        |     +--> Kerberos
        |     +--> Name Resolution
        |
        +-- Yes
              |
              v
        Authenticated Enumeration
              |
              +--> Users
              +--> Groups
              +--> Computers
              +--> Shares
              +--> SPNs
              +--> Delegation
              +--> ACLs
              +--> GPO
              +--> Trusts
              +--> AD CS
              |
              v
           BloodHound
              |
              v
       Attack Path Exists?
              |
        +-----+-----+
        |           |
       No          Yes
        |           |
        v           v
  Expand Scope   Validate Edge
  of Analysis        |
        |            v
        |       New Access?
        |            |
        |       +----+----+
        |       |         |
        |      No        Yes
        |       |         |
        |       v         v
        |   Continue   Re-enumerate
        |   Analysis       |
        |                  v
        |             New Host?
        |                  |
        |             +----+----+
        |             |         |
        |            No        Yes
        |             |         |
        |             |         v
        |             |   Check Interfaces
        |             |   and Routes
        |             |         |
        |             |         v
        |             |   New Network?
        |             |         |
        |             |    +----+----+
        |             |    |         |
        |             |   No        Yes
        |             |    |         |
        |             |    |         v
        |             |    |      Pivot
        |             |    |         |
        +-------------+----+---------+
                           |
                           v
                      Re-enumerate
```

---

# Final Methodology Model

```text
                         SCOPE
                           |
                           v
                    STARTING POSITION
                           |
                           v
                    NETWORK CONTEXT
                           |
                           v
                    DOMAIN DISCOVERY
                           |
                           v
                      ENUMERATION
                           |
         +-----------------+-----------------+
         |                 |                 |
         v                 v                 v
      IDENTITY           HOSTS        INFRASTRUCTURE
         |                 |                 |
         +-----------------+-----------------+
                           |
                           v
                     ATTACK GRAPH
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       ACL/GPO          KERBEROS           NTLM
          |                |                |
          +----------------+----------------+
                           |
                 +---------+---------+
                 |                   |
                 v                   v
             CREDENTIALS            AD CS
                 |                   |
                 +---------+---------+
                           |
                           v
                    ATTACK PATH
                           |
                           v
                 CONTROLLED VALIDATION
                           |
                           v
                       NEW ACCESS
                           |
                           v
                     RE-ENUMERATE
                           |
              +------------+------------+
              |                         |
              v                         v
       LATERAL MOVEMENT              PIVOTING
              |                         |
              +------------+------------+
                           |
                           v
                     NEW NETWORK
                           |
                           v
                       TRUSTS
                           |
                           v
                 ENTERPRISE SYSTEMS
                           |
                           v
                DOMAIN / FOREST IMPACT
                           |
                           v
               DETECTION + REMEDIATION
```

The most important habit throughout an Active Directory assessment is:

```text
Every new identity,
every new host,
and every new network
creates a new enumeration opportunity.
```

---

# Related Notes

```text
active-directory/index.md
active-directory/enumeration.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/bloodhound.md
active-directory/lateral-movement.md
active-directory/privilege-escalation.md
active-directory/persistence.md
```

As the Active Directory section expands, these will also link to dedicated notes covering:

```text
ACL / ACE
Kerberoasting
AS-REP Roasting
Delegation
NTLM Relay
Responder
AD CS
Trusts
Pivoting
SCCM
WSUS
MDT
ADFS
```

---

# References

## Microsoft - Active Directory Domain Services

```text
https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/
```

## Microsoft - Active Directory Domain Services Overview

```text
https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview
```

## Microsoft - Kerberos Authentication

```text
https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview
```

## Microsoft - NTLM Overview

```text
https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview
```

## Microsoft - Group Policy

```text
https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview
```

## Microsoft - Active Directory Certificate Services

```text
https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview
```

## Microsoft - LDAP

```text
https://learn.microsoft.com/en-us/windows/win32/adsi/ldap-adspath
```

## BloodHound

```text
https://bloodhound.specterops.io/
```

## NetExec

```text
https://www.netexec.wiki/
```

## NetExec GitHub

```text
https://github.com/Pennyw0rth/NetExec
```

## Impacket

```text
https://github.com/fortra/impacket
```

## Responder

```text
https://github.com/lgandx/Responder
```

## Certipy

```text
https://github.com/ly4k/Certipy
```

## bloodyAD

```text
https://github.com/CravateRouge/bloodyAD
```

## PowerView

```text
https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon
```

## Rubeus

```text
https://github.com/GhostPack/Rubeus
```

## Ligolo-ng

```text
https://github.com/nicocha30/ligolo-ng
```

## Chisel

```text
https://github.com/jpillora/chisel
```

## InternalAllTheThings - Active Directory

```text
https://swisskyrepo.github.io/InternalAllTheThings/active-directory/
```
