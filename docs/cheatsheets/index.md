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

The AD cheatsheet will continue to grow as the detailed Active Directory notes are built.

[Open Active Directory Cheatsheet](active-directory.md)

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
        |       +--> PowerShell
        |       +--> Networking
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

Avoid unnecessarily storing:

```text
Plaintext passwords
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

SMB Signing Not Required
   !=
Successful NTLM Relay

BloodHound Edge
   !=
Confirmed Attack Path

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
Change system state
Interrupt services
Expose sensitive information
```

Use the least intrusive technique that answers the assessment question.

---

# Cheatsheet Index

| Cheatsheet | Path |
|---|---|
| Linux | `cheatsheets/linux.md` |
| Windows | `cheatsheets/windows.md` |
| PowerShell | `cheatsheets/powershell.md` |
| Networking | `cheatsheets/networking.md` |
| Web Application Security | `cheatsheets/web.md` |
| Active Directory | `cheatsheets/active-directory.md` |

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

Use the cheatsheets for speed.

Use the detailed notes for understanding.

Use both for a structured assessment.
