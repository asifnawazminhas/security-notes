# Cheatsheets

Quick-reference commands, workflows, syntax, and testing checklists for penetration testing, red teaming, vulnerability research, and security assessments.

The cheatsheets are designed for use during an assessment when the question is:

> **What command or workflow do I need right now?**

For detailed explanations of vulnerabilities, techniques, prerequisites, attack paths, detection, and remediation, use the main sections of the notes.

---

## Cheatsheets

<div class="grid cards" markdown>

-   :material-linux:{ .lg .middle } **Linux**

    ---

    Linux enumeration, networking, services, permissions, processes, credentials, and privilege escalation commands.

    [:octicons-arrow-right-24: Linux Cheatsheet](linux.md)

-   :material-microsoft-windows:{ .lg .middle } **Windows**

    ---

    Windows enumeration, users, groups, services, permissions, networking, credentials, and privilege escalation commands.

    [:octicons-arrow-right-24: Windows Cheatsheet](windows.md)

-   :material-powershell:{ .lg .middle } **PowerShell**

    ---

    PowerShell syntax and commands for Windows and Active Directory enumeration, system administration, filtering, networking, and security testing.

    [:octicons-arrow-right-24: PowerShell Cheatsheet](powershell.md)

-   :material-lan:{ .lg .middle } **Networking**

    ---

    Network discovery, DNS, ports, routing, connectivity testing, service enumeration, tunnelling, and troubleshooting.

    [:octicons-arrow-right-24: Networking Cheatsheet](networking.md)

-   :material-web:{ .lg .middle } **Web Application Security**

    ---

    Quick-reference workflows and commands for reconnaissance, HTTP testing, authentication, access control, injection, APIs, and common web vulnerabilities.

    [:octicons-arrow-right-24: Web Cheatsheet](web.md)

-   :material-microsoft-windows-classic:{ .lg .middle } **Active Directory**

    ---

    Active Directory discovery, SMB, LDAP, Kerberos, users, groups, computers, shares, ACLs, delegation, BloodHound, NetExec, Impacket, trusts, AD CS, and pivoting.

    [:octicons-arrow-right-24: Active Directory Cheatsheet](active-directory.md)

-   :material-tools:{ .lg .middle } **Impacket**

    ---

    Quick-reference commands for Active Directory enumeration, Kerberos, SMB, RPC, delegation, tickets, credential access, remote administration, and NTLM relay testing.

    [:octicons-arrow-right-24: Impacket Cheatsheet](impacket.md)

</div>

---

# Quick Navigation

| Area | Cheatsheet | Use When |
|---|---|---|
| Linux | [Linux](linux.md) | Working on a Linux host |
| Windows | [Windows](windows.md) | Working on a Windows host |
| PowerShell | [PowerShell](powershell.md) | Using PowerShell for enumeration or administration |
| Networking | [Networking](networking.md) | Discovering hosts, services, routes, or network paths |
| Web | [Web Application Security](web.md) | Testing web applications and APIs |
| Active Directory | [Active Directory](active-directory.md) | Assessing Windows domain environments |
| Impacket | [Impacket](impacket.md) | Using Impacket for focused Windows and Active Directory protocol operations |

---

# How the Cheatsheets Fit the Notes

The notes are organised into two complementary layers.

```text
                     Security Notes
                          |
              +-----------+-----------+
              |                       |
              v                       v
        Detailed Notes            Cheatsheets
              |                       |
              v                       v
        Why does it work?       What do I run?
              |
              v
        How does it work?
              |
              v
        What does the
        result mean?
              |
              v
        How do I validate it?
              |
              v
        How is it detected?
              |
              v
        How is it remediated?
```

Use the detailed notes when learning or investigating a technique.

Use the cheatsheets when you already understand the technique and need a quick operational reference.

---

# General Assessment Workflow

A useful high-level workflow is:

```text
Scope
  |
  v
Discovery
  |
  v
Enumeration
  |
  v
Attack Surface
  |
  v
Authentication
  |
  v
Authorisation
  |
  v
Validation
  |
  v
Privilege Analysis
  |
  v
Lateral Movement
  |
  v
Re-Enumeration
  |
  v
Evidence
  |
  v
Reporting
```

Not every assessment follows this exact sequence.

The important principle is:

```text
Understand
    |
    v
Enumerate
    |
    v
Analyse
    |
    v
Validate
```

rather than immediately attempting exploitation.

---

# Linux

Use the Linux cheatsheet for quick reference when working from or assessing Linux systems.

Typical areas include:

```text
System information
Users and groups
Processes
Services
Networking
Routes
DNS
Filesystems
Permissions
SUID / SGID
Capabilities
Cron
Credentials
SSH
Logs
Containers
Privilege escalation
```

[Open Linux Cheatsheet](linux.md)

---

# Windows

Use the Windows cheatsheet for:

```text
System information
Users
Groups
Privileges
Processes
Services
Scheduled tasks
Networking
Routes
Firewall
Shares
Credentials
Registry
Permissions
Execution controls
Privilege escalation
```

[Open Windows Cheatsheet](windows.md)

---

# PowerShell

PowerShell is useful across:

```text
Windows enumeration
Active Directory
Networking
File analysis
Permissions
Services
Processes
Registry
Event logs
Remote administration
Object filtering
```

Typical workflow:

```text
Get Data
   |
   v
Select Properties
   |
   v
Filter Objects
   |
   v
Sort / Group
   |
   v
Export Evidence
```

[Open PowerShell Cheatsheet](powershell.md)

---

# Networking

Use the networking cheatsheet when determining:

```text
Where am I?

What interfaces exist?

What routes exist?

What DNS server is being used?

Which hosts are reachable?

Which ports are open?

Which services are exposed?

Is another network reachable?

Do I need to pivot?
```

Typical workflow:

```text
Interface
    |
    v
Routes
    |
    v
DNS
    |
    v
Neighbours
    |
    v
Hosts
    |
    v
Ports
    |
    v
Services
    |
    v
Network Paths
```

[Open Networking Cheatsheet](networking.md)

---

# Web Application Security

Use the Web cheatsheet for quick access to testing workflows covering areas such as:

```text
Reconnaissance
Technology identification
Content discovery
Parameter discovery
Authentication
Authorisation
Session management
XSS
SQL injection
Command injection
SSRF
XXE
SSTI
File upload
Path traversal
APIs
GraphQL
JWT
OAuth
HTTP behaviour
Security headers
```

Typical workflow:

```text
Target
  |
  v
Recon
  |
  v
Map Application
  |
  v
Identify Inputs
  |
  v
Identify Trust Boundaries
  |
  v
Test Controls
  |
  v
Validate Findings
```

[Open Web Application Security Cheatsheet](web.md)

---

# Active Directory

Use the Active Directory cheatsheet when assessing Windows domain environments.

It currently covers quick-reference workflows for:

```text
Domain discovery
Domain Controller discovery
DNS
SMB
LDAP
RPC
Users
Groups
Computers
Password policy
SPNs
AS-REP candidates
Delegation
OUs
Group Policy
SYSVOL
NETLOGON
ACLs
Trusts
LAPS
gMSA
Machine Account Quota
AD CS discovery
BloodHound
NetExec
Impacket
Responder
Remote management
Pivoting
Re-enumeration
```

The Active Directory cheatsheet acts as the general operational reference for AD assessments.

As individual tools and techniques grow large enough, they can have their own dedicated cheatsheets.

[Open Active Directory Cheatsheet](active-directory.md)

---

# Impacket

Use the Impacket cheatsheet when you need a quick reference for focused Windows and Active Directory protocol operations.

It covers:

```text
Installation
Command naming
Authentication syntax
Password authentication
NTLM hash authentication
Kerberos authentication
AES keys
Kerberos credential caches
GetADUsers
GetNPUsers
GetUserSPNs
lookupsid
findDelegation
rpcdump
samrdump
smbclient
smbserver
getTGT
getST
ticketConverter
ticketer
secretsdump
psexec
wmiexec
smbexec
dcomexec
atexec
ntlmrelayx
Troubleshooting
Pivoting considerations
Evidence collection
```

A useful mental model is:

```text
NetExec
   |
   v
Broad Discovery
   |
   v
Interesting Target
   |
   v
Impacket
   |
   v
Focused Protocol Operation
```

Impacket should not be treated as a random collection of scripts.

Select the appropriate tool based on:

```text
Protocol
Identity
Authentication method
Target
Privileges
Required operation
Rules of engagement
```

[Open Impacket Cheatsheet](impacket.md)

---

# Active Directory Tool Cheatsheets

The Active Directory cheatsheet provides the broad workflow.

Dedicated tool cheatsheets provide deeper operational references.

```text
Active Directory Cheatsheet
          |
          +--> General AD workflow
          +--> Discovery
          +--> Enumeration
          +--> Authentication
          +--> Relationships
          +--> Re-enumeration
          |
          v
Dedicated Tool Cheatsheets
          |
          +--> Impacket
          |
          +--> NetExec
          |
          +--> BloodHound
          |
          +--> Responder
          |
          +--> Additional tools as required
```

Currently available:

| Tool | Cheatsheet | Primary Use |
|---|---|---|
| Impacket | [Impacket](impacket.md) | Focused SMB, LDAP, RPC, Kerberos, delegation, remote administration, and relay operations |

Additional dedicated tool cheatsheets can be added when their command surface becomes large enough to justify a separate operational reference.

---

# Choosing Between Active Directory and Impacket

Use the general Active Directory cheatsheet when asking:

```text
What should I enumerate?

What should I check next?

What relationships should I investigate?

What does this new credential change?

What should I re-enumerate?
```

Use the Impacket cheatsheet when asking:

```text
Which Impacket tool do I need?

What is the authentication syntax?

How do I enumerate SPNs?

Which tool enumerates delegation?

How do I use a Kerberos ccache?

Which tool interacts with SMB?

Which remote administration mechanism does this tool use?
```

Conceptually:

```text
Active Directory Cheatsheet
           |
           v
     WHAT TO TEST
           |
           v
     Select Technique
           |
           v
   Impacket Cheatsheet
           |
           v
      HOW TO RUN IT
```

---

# Tool Selection

A simple way to select the appropriate cheatsheet:

```text
What am I testing?
        |
        +--> Linux host
        |       |
        |       +--> Linux
        |
        +--> Windows host
        |       |
        |       +--> Windows
        |       |
        |       +--> PowerShell
        |
        +--> Active Directory
        |       |
        |       +--> Active Directory
        |       |
        |       +--> PowerShell
        |       |
        |       +--> Networking
        |       |
        |       +--> Using Impacket?
        |               |
        |               +--> Impacket
        |
        +--> Web application
        |       |
        |       +--> Web
        |
        +--> Network
                |
                +--> Networking
```

In practice, multiple cheatsheets are often used during the same assessment.

---

# Active Directory Tool Selection

For an AD assessment:

```text
Need broad AD workflow?
        |
        +--> Active Directory Cheatsheet

Need broad credential/access validation?
        |
        +--> NetExec

Need focused protocol operations?
        |
        +--> Impacket

Need identity relationship analysis?
        |
        +--> BloodHound

Need Windows-side directory enumeration?
        |
        +--> PowerShell / PowerView

Need name-resolution authentication testing?
        |
        +--> Responder
```

As dedicated cheatsheets are added, this section can link directly to each one.

---

# Impacket Tool Selection

A quick Impacket map:

```text
What do I need?
      |
      +--> Users
      |      |
      |      +--> GetADUsers
      |
      +--> AS-REP candidates
      |      |
      |      +--> GetNPUsers
      |
      +--> SPNs
      |      |
      |      +--> GetUserSPNs
      |
      +--> SIDs / RIDs
      |      |
      |      +--> lookupsid
      |
      +--> Delegation
      |      |
      |      +--> findDelegation
      |
      +--> SMB
      |      |
      |      +--> smbclient
      |      +--> smbserver
      |
      +--> Kerberos TGT
      |      |
      |      +--> getTGT
      |
      +--> Kerberos service ticket
      |      |
      |      +--> getST
      |
      +--> Ticket conversion
      |      |
      |      +--> ticketConverter
      |
      +--> Credential access
      |      |
      |      +--> secretsdump
      |
      +--> Remote administration
      |      |
      |      +--> psexec
      |      +--> wmiexec
      |      +--> smbexec
      |      +--> dcomexec
      |      +--> atexec
      |
      +--> NTLM relay
             |
             +--> ntlmrelayx
```

For commands and syntax:

[Open Impacket Cheatsheet](impacket.md)

---

# Start With Context

Before running specialised tools, establish context.

## Linux

```bash
id
hostname
ip addr
ip route
cat /etc/resolv.conf
```

## Windows

```cmd
whoami /all
hostname
ipconfig /all
route print
arp -a
```

## PowerShell

```powershell
whoami /all
hostname
Get-NetIPConfiguration
Get-NetRoute
Get-DnsClientServerAddress
```

These simple commands often determine which testing workflow makes sense next.

---

# Active Directory Context

Before running specialised AD tooling, establish:

```text
Domain
Domain Controller
Domain Controller FQDN
Domain Controller IP
DNS server
Current identity
Current privileges
Network routes
Reachable services
```

From Linux:

```bash
ip addr
ip route
cat /etc/resolv.conf
```

Find LDAP:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

Find Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

This context is particularly important before using Kerberos-aware Impacket tooling.

---

# Keep Evidence

Where useful, save command output.

Linux:

```bash
command | tee evidence.txt
```

PowerShell:

```powershell
Get-Something |
    Out-File evidence.txt
```

Create structured evidence directories for larger assessments:

```text
evidence/
├── discovery/
├── enumeration/
├── authentication/
├── network/
├── web/
├── active-directory/
├── screenshots/
└── findings/
```

Tool-specific directories can be useful:

```text
evidence/
└── active-directory/
    ├── netexec/
    ├── impacket/
    ├── bloodhound/
    └── responder/
```

Avoid unnecessarily storing:

```text
Plaintext passwords
NTLM hashes
Kerberos tickets
AES keys
Private keys
Authentication tokens
Sensitive business data
Personal information
```

---

# Interpret Results Carefully

A tool result is not automatically a vulnerability.

Examples:

```text
Open Port
   !=
Vulnerability

Authentication Success
   !=
Administrative Access

Administrative Access
   !=
Domain Administrator

SPN
   !=
Weak Service Account

AS-REP Candidate
   !=
Weak Password

Delegation
   !=
Exploitable Attack Path

SMB Signing Not Required
   !=
Successful NTLM Relay

Captured Authentication
   !=
Successful NTLM Relay

BloodHound Edge
   !=
Confirmed Attack Path

Kerberos Ticket
   !=
Access to Every Service

Writable Directory
   !=
Privilege Escalation

Outdated Component
   !=
Confirmed Exploitable CVE

Missing Security Header
   !=
Exploitable Vulnerability
```

The general model should be:

```text
Observation
    |
    v
Security Condition
    |
    v
Prerequisites
    |
    v
Controlled Validation
    |
    v
Impact
```

---

# Re-Enumerate

One of the most important habits during an assessment is re-enumeration.

```text
New Credential
      |
      v
Re-Enumerate

New User
      |
      v
Re-Enumerate

New Privilege
      |
      v
Re-Enumerate

New Host
      |
      v
Re-Enumerate

New Network
      |
      v
Re-Enumerate

New Domain
      |
      v
Re-Enumerate
```

A previously inaccessible resource may become accessible after the security context changes.

---

# Active Directory Re-Enumeration

When a new AD credential is obtained:

```text
New Credential
      |
      v
Domain or Local?
      |
      v
Validate Carefully
      |
      +--> SMB
      |
      +--> LDAP
      |
      +--> Kerberos
      |
      v
Users / Groups
      |
      v
Shares
      |
      v
SPNs
      |
      v
Delegation
      |
      v
BloodHound
      |
      v
Administrative Relationships
```

When a new subnet becomes reachable:

```text
New Network
     |
     v
Routes
     |
     v
DNS
     |
     v
Hosts
     |
     v
Services
     |
     v
AD Infrastructure
     |
     v
Re-Enumerate
```

---

# Cheatsheet Philosophy

The cheatsheets should remain:

```text
Fast
Practical
Structured
Searchable
Operational
```

They should not become copies of the detailed notes.

The model is:

```text
Detailed Page
     |
     | Distil useful commands
     v
Cheatsheet
```

For example:

```text
Detailed Impacket Note
        |
        +--> Protocol explanation
        +--> Authentication model
        +--> Prerequisites
        +--> Interpretation
        +--> Troubleshooting
        +--> Detection
        +--> Reporting
        |
        v
Impacket Cheatsheet
        |
        +--> Tool map
        +--> Authentication syntax
        +--> Commands
        +--> Fast workflows
        +--> Troubleshooting
```

Likewise:

```text
Active Directory Enumeration
        |
        +--> Detailed explanation
        +--> Security model
        +--> Interpretation
        +--> Detection
        +--> Remediation
        |
        v
Active Directory Cheatsheet
        |
        +--> Commands
        +--> Syntax
        +--> Quick workflow
```

---

# When to Create a Dedicated Cheatsheet

Not every tool needs its own cheatsheet.

Use:

```text
Does the detailed note contain
enough recurring operational syntax?
             |
         +---+---+
         |       |
        No      Yes
         |       |
         v       v
      Keep in   Dedicated
      general   cheatsheet
      sheet
```

Good candidates include tools or topics with:

```text
Many commands
Multiple authentication methods
Multiple protocols
Complex workflows
Frequent troubleshooting
Repeated assessment use
```

This is why Impacket benefits from a dedicated cheatsheet.

---

# During an Assessment

When unsure what to do next, ask:

```text
Who am I?

Where am I?

What can I reach?

What services are available?

What credentials do I have?

What privileges do I have?

What can those privileges access?

What relationships exist?

Has my security context changed?

Has my network position changed?

What should I re-enumerate?
```

For Active Directory, also ask:

```text
What domain am I in?

Which Domain Controllers exist?

What authentication methods are available?

What groups does this identity belong to?

Which systems accept this identity?

Which services run under domain identities?

What delegation relationships exist?

What ACL relationships exist?

Which trusts exist?

Which certificate services exist?
```

---

# Quick Assessment Model

```text
                         START
                           |
                           v
                         SCOPE
                           |
                           v
                        CONTEXT
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
           HOST          NETWORK      APPLICATION
             |             |             |
             +-------------+-------------+
                           |
                           v
                       ENUMERATE
                           |
                           v
                        ANALYSE
                           |
                           v
                        VALIDATE
                           |
                           v
                     NEW INFORMATION
                           |
                           v
                     RE-ENUMERATE
                           |
                           v
                        EVIDENCE
                           |
                           v
                        REPORT
```

---

# Active Directory Assessment Model

```text
                    ACTIVE DIRECTORY
                           |
                           v
                       DISCOVERY
                           |
                           v
                      ENUMERATION
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       Identity          Hosts          Services
          |                |                |
          +----------------+----------------+
                           |
                           v
                     RELATIONSHIPS
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
         ACLs          Delegation        Trusts
          |                |                |
          +----------------+----------------+
                           |
                           v
                      ATTACK PATHS
                           |
                           v
                    PREREQUISITES
                           |
                           v
                CONTROLLED VALIDATION
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

# Authorised Use

These cheatsheets are intended for:

```text
Authorised penetration testing
Red team exercises
Purple team exercises
Security assessments
Training environments
CTFs
Security research
```

Always remain within the agreed scope and rules of engagement.

Some techniques may:

```text
Generate significant logs
Trigger monitoring
Lock user accounts
Request large numbers of Kerberos tickets
Change system state
Create services
Create scheduled tasks
Execute commands remotely
Expose credential material
Interrupt services
Expose sensitive information
```

Use the least intrusive technique that answers the assessment question.

---

# Cheatsheet Index

| Cheatsheet | Path | Purpose |
|---|---|---|
| Linux | `cheatsheets/linux.md` | Linux host assessment |
| Windows | `cheatsheets/windows.md` | Windows host assessment |
| PowerShell | `cheatsheets/powershell.md` | PowerShell quick reference |
| Networking | `cheatsheets/networking.md` | Network discovery and troubleshooting |
| Web Application Security | `cheatsheets/web.md` | Web and API security testing |
| Active Directory | `cheatsheets/active-directory.md` | General AD assessment workflow |
| Impacket | `cheatsheets/impacket.md` | Focused Windows and AD protocol operations |

---

# Planned Active Directory Cheatsheets

As the Active Directory notes grow, dedicated operational references can be added where justified.

```text
Active Directory
│
├── Active Directory        DONE
│
├── Impacket                DONE
│
├── NetExec                 NEXT
│
├── BloodHound
│
├── Responder
│
├── Kerberos
│
├── AD CS
│
└── Pivoting
```

These should only be created when there is enough recurring operational content to justify a dedicated cheatsheet.

The general Active Directory cheatsheet remains the central workflow reference.

---

# Cheatsheet Structure

The growing structure is:

```text
docs/cheatsheets/
│
├── index.md
│
├── linux.md
├── windows.md
├── powershell.md
├── networking.md
├── web.md
│
├── active-directory.md
├── impacket.md
│
└── additional focused cheatsheets
    added as the notes grow
```

---

# Navigation Model

```text
                        CHEATSHEETS
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
     Operating           Networking            Web
      Systems
          |
    +-----+-----+
    |     |     |
    v     v     v
 Linux Windows PowerShell

                             |
                             v
                     Active Directory
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
          General         Impacket        NetExec
                                             |
                                      future dedicated
                                         cheatsheet
```

As additional tool cheatsheets are created:

```text
Active Directory
      |
      +--> General AD
      |
      +--> NetExec
      |
      +--> Impacket
      |
      +--> BloodHound
      |
      +--> Responder
      |
      +--> Kerberos
      |
      +--> AD CS
      |
      +--> Pivoting
```

---

# Final Model

```text
                         CHEATSHEETS
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
        Linux              Windows              Web
          |                   |                   |
          |                   +--> PowerShell     |
          |                                       |
          +-------------------+-------------------+
                              |
                              v
                          Networking
                              |
                              v
                      Active Directory
                              |
                 +------------+------------+
                 |                         |
                 v                         v
             General AD               Tool-Specific
                                           |
                              +------------+------------+
                              |                         |
                              v                         v
                          Impacket                   NetExec
                                                       |
                                                       v
                                                 More Tools
                              |
                              v
                         Assessment
                              |
                              v
                    Detailed Investigation
                              |
                              v
                           Evidence
                              |
                              v
                           Reporting
```

Use the general cheatsheets to decide **what to test**.

Use dedicated tool cheatsheets to determine **which command or syntax to use**.

Use the detailed notes to understand **why the technique works, what the result means, and how to validate it safely**.
