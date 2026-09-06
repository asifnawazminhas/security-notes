---
title: Cheatsheets
description: Practical cybersecurity cheatsheets for penetration testing, red teaming, Active Directory, Windows, Linux, web application security, networking and security tooling.
---

# Cheatsheets

Quick operational references for **penetration testing**, **red teaming**, **Active Directory**, **Windows**, **Linux**, **web application security**, **networking** and commonly used security tools.

These cheatsheets are designed for use during authorised security assessments when you need to quickly answer:

```text
What should I check?

Which command should I use?

What does the result mean?

What should I investigate next?
```

Unlike the detailed topic notes, the cheatsheets focus on fast access to commands, workflows, validation steps and result interpretation.

!!! warning "Authorised Security Testing"

    The commands and techniques in these cheatsheets are intended for educational purposes, security research and authorised security testing only.

## Choose a Cheatsheet

<div class="grid cards" markdown>

-   :material-linux:{ .lg .middle } **Linux**

    ---

    Linux enumeration, privilege escalation triage, permissions, SUID/SGID, capabilities, sudo, services, cron, containers, credentials, networking, and evidence collection.

    [:octicons-arrow-right-24: Linux Cheatsheet](linux.md)

-   :material-microsoft-windows:{ .lg .middle } **Windows**

    ---

    Windows host enumeration, privileges, services, scheduled tasks, writable paths, AppLocker, App Control, Defender, credentials, local privilege escalation, and evidence collection.

    [:octicons-arrow-right-24: Windows Cheatsheet](windows.md)

-   :material-powershell:{ .lg .middle } **PowerShell**

    ---

    PowerShell syntax, host enumeration, files, ACLs, registry, networking, remoting, language modes, execution controls, logging, Defender, and security assessment commands.

    [:octicons-arrow-right-24: PowerShell Cheatsheet](powershell.md)

-   :material-lan:{ .lg .middle } **Networking**

    ---

    TCP/IP, DNS, routing, ports, sockets, Nmap, packet capture, HTTP/TLS, SSH tunnels, proxies, pivoting, VPNs, Active Directory networking, and troubleshooting.

    [:octicons-arrow-right-24: Networking Cheatsheet](networking.md)

-   :material-web:{ .lg .middle } **Web Application Security**

    ---

    Reconnaissance, authentication, authorisation, sessions, SQL injection, XSS, SSRF, file upload, path traversal, request smuggling, APIs, JWT, GraphQL, and Burp Suite workflows.

    [:octicons-arrow-right-24: Web Cheatsheet](web.md)

-   :material-microsoft-windows:{ .lg .middle } **Active Directory**

    ---

    Domain enumeration, users, groups, computers, Kerberos, NTLM, ACLs, delegation, AD CS, trusts, credential access, lateral movement, and privilege escalation.

    [:octicons-arrow-right-24: Active Directory Cheatsheet](active-directory.md)

-   :material-console:{ .lg .middle } **NetExec**

    ---

    Practical NetExec reference for SMB, LDAP, WinRM, MSSQL, authentication validation, share enumeration, password policies, local administrators, sessions, and Active Directory assessment workflows.

    [:octicons-arrow-right-24: NetExec Cheatsheet](netexec.md)

-   :material-tools:{ .lg .middle } **Impacket**

    ---

    Impacket reference for SMB, RPC, Kerberos, SPNs, ticket handling, MSSQL, remote administration, credential access, troubleshooting, evidence collection, and result interpretation.

    [:octicons-arrow-right-24: Impacket Cheatsheet](impacket.md)

-   :material-graph:{ .lg .middle } **BloodHound**

    ---

    BloodHound collection, graph analysis, attack paths, ACL relationships, administrative rights, sessions, Cypher queries, path validation, false positives, remediation, and retesting.

    [:octicons-arrow-right-24: BloodHound Cheatsheet](bloodhound.md)

</div>


## How to Use the Cheatsheets

The cheatsheets are intended to support a repeatable assessment workflow:

```text
Observation
    |
    v
Choose Relevant Cheatsheet
    |
    v
Locate Command or Technique
    |
    v
Check Prerequisites
    |
    v
Run Focused Test
    |
    v
Review Result
    |
    v
Interpret Security Meaning
    |
    v
Validate Further If Required
    |
    v
Capture Evidence
```

A command succeeding does not automatically mean a vulnerability exists.

The important question is:

> **What does the result actually prove?**


## Host Assessment

For host-level security testing:

<div class="grid cards" markdown>

-   :material-linux:{ .lg .middle } **Linux Assessment**

    ---

    Start with system identity, users, groups, sudo, permissions, services, scheduled jobs, SUID/SGID, capabilities, containers, credentials, networking, and privilege escalation candidates.

    [:octicons-arrow-right-24: Open Linux Cheatsheet](linux.md)

-   :material-microsoft-windows:{ .lg .middle } **Windows Assessment**

    ---

    Review identity, privileges, services, scheduled tasks, filesystem permissions, registry configuration, execution controls, credentials, Defender, and privilege escalation candidates.

    [:octicons-arrow-right-24: Open Windows Cheatsheet](windows.md)

-   :material-powershell:{ .lg .middle } **PowerShell Assessment**

    ---

    Use PowerShell for Windows enumeration, permissions analysis, registry inspection, networking, policy inspection, event logs, Defender configuration, and evidence collection.

    [:octicons-arrow-right-24: Open PowerShell Cheatsheet](powershell.md)

</div>


## Active Directory Assessment

For Active Directory environments, the cheatsheets can be combined into a workflow:

```text
Active Directory
       |
       v
Initial Enumeration
       |
       v
NetExec
       |
       +--> SMB
       +--> LDAP
       +--> WinRM
       +--> MSSQL
       |
       v
BloodHound
       |
       +--> Groups
       +--> ACLs
       +--> Sessions
       +--> Admin Rights
       +--> Attack Paths
       |
       v
Impacket
       |
       +--> Kerberos
       +--> SMB
       +--> RPC
       +--> MSSQL
       +--> Focused Validation
       |
       v
Manual Validation
       |
       v
Evidence
```

Use:

- [Active Directory Cheatsheet](active-directory.md) for the overall assessment workflow.
- [NetExec Cheatsheet](netexec.md) for broad protocol and access mapping.
- [BloodHound Cheatsheet](bloodhound.md) for relationship and attack-path analysis.
- [Impacket Cheatsheet](impacket.md) for focused protocol-level validation.


## Web Application Assessment

A typical web assessment workflow is:

```text
Target
  |
  v
Reconnaissance
  |
  v
Technology Identification
  |
  v
Content Discovery
  |
  v
Parameter Discovery
  |
  v
Authentication
  |
  v
Authorisation
  |
  v
Input Handling
  |
  v
Server-Side Behaviour
  |
  v
API Testing
  |
  v
Business Logic
  |
  v
Evidence and Reporting
```

Use the [Web Application Security Cheatsheet](web.md) as the operational reference and the detailed [Web Application Security Notes](../web/index.md) when deeper explanation is required.


## Networking

Networking supports nearly every other assessment area.

Use the [Networking Cheatsheet](networking.md) for:

```text
Interfaces

IP addressing

Routes

DNS

TCP

UDP

Ports

Nmap

HTTP

TLS

Packet capture

SSH

Tunnelling

Proxies

Pivoting

VPNs

Active Directory connectivity

Troubleshooting
```


## Tool-Specific Cheatsheets

The tool-specific references are intentionally more detailed than simple command lists.

### NetExec

Use the [NetExec Cheatsheet](netexec.md) when working with:

```text
SMB

LDAP

WinRM

MSSQL

Domain authentication

Local authentication

Shares

Password policies

Local administrators

Sessions

Active Directory enumeration
```

### Impacket

Use the [Impacket Cheatsheet](impacket.md) for focused protocol operations involving:

```text
SMB

RPC

Kerberos

SPNs

TGTs

Service tickets

MSSQL

Remote administration

Credential stores
```

### BloodHound

Use the [BloodHound Cheatsheet](bloodhound.md) for:

```text
Active Directory graph analysis

Group relationships

ACL relationships

Administrative rights

Sessions

Delegation

Attack paths

Cypher queries

Path validation

Remediation analysis
```


## Tool Selection

Choose the tool based on the question being investigated.

| Question | Starting Point |
|---|---|
| What is running on this Linux host? | [Linux](linux.md) |
| What privileges does my Windows account have? | [Windows](windows.md) |
| How can I query this Windows configuration? | [PowerShell](powershell.md) |
| Why can I not reach this service? | [Networking](networking.md) |
| What should I test in this web application? | [Web](web.md) |
| How should I approach this AD environment? | [Active Directory](active-directory.md) |
| Which systems accept this authorised domain credential? | [NetExec](netexec.md) |
| Which AD relationships create privilege paths? | [BloodHound](bloodhound.md) |
| Which protocol-specific tool should validate this AD relationship? | [Impacket](impacket.md) |


## From Observation to Conclusion

The cheatsheets should not be used as:

```text
Command
   |
   v
Interesting Output
   |
   v
Finding
```

Use:

```text
Observation
    |
    v
Command
    |
    v
Result
    |
    v
Interpretation
    |
    v
Alternative Explanation
    |
    v
Further Validation
    |
    v
Security Consequence
    |
    v
Finding
```


## Example - Windows Service

Suppose enumeration shows:

```text
Service:
ExampleService

Executable:
C:\Program Files\Example\Service.exe
```

An ACL check shows:

```text
BUILTIN\Users Allow ReadAndExecute
```

This does **not** demonstrate that a standard user can modify the executable.

The result supports:

```text
User can read and execute file.
```

It does not support:

```text
User can replace file.
```

If instead the ACL contains:

```text
BUILTIN\Users Allow Modify
```

the executable becomes security relevant, but further validation is still required:

```text
Who runs the service?

Can the executable actually be modified?

Can the service be restarted?

Will the modified executable execute under a more privileged identity?
```


## Example - BloodHound

BloodHound identifies:

```text
ASIF
 |
 | MemberOf
 v
HELPDESK
 |
 | GenericAll
 v
SERVER-ADMINS
```

Do not immediately conclude:

```text
Privilege escalation confirmed.
```

Instead:

```text
BloodHound Relationship
        |
        v
Verify Membership
        |
        v
Inspect ACL
        |
        v
Confirm GenericAll
        |
        v
Determine Server-Admins Privilege
        |
        v
Establish Security Consequence
```


## Example - Web Application

Suppose changing:

```text
GET /api/orders/1001
```

to:

```text
GET /api/orders/1002
```

returns another object.

Before concluding IDOR/BOLA, determine:

```text
Does object 1002 belong to another user?

Was the request authenticated?

Should the current user have access?

Does the response contain protected information?

Can the behaviour be reproduced with controlled accounts?
```

The result becomes defensible when the authorisation boundary is demonstrated rather than inferred.


## Evidence Collection

For important tests, record:

```text
Timestamp

Target

Source

Account

Tool

Tool version

Command or request

Relevant output

Interpretation

Security consequence

Cleanup

Retest result
```

Sensitive information should be redacted where appropriate.


## Cheatsheets vs Detailed Notes

Use the cheatsheets when you need:

```text
Fast command lookup

Assessment workflow

Common validation steps

Result interpretation

Troubleshooting

Operational reference
```

Use the detailed notes when you need:

```text
Background theory

Protocol explanation

Technique internals

Detailed attack scenarios

Detection engineering

Remediation guidance

Research context
```

The two sections are designed to complement each other:

```text
                 SECURITY NOTES
                       |
          +------------+------------+
          |                         |
          v                         v
     CHEATSHEETS               DETAILED NOTES
          |                         |
          v                         v
   Fast Operational          Deep Technical
      Reference                Explanation
          |                         |
          +------------+------------+
                       |
                       v
                 PRACTICAL TESTING
```


## Current Cheatsheets

| Cheatsheet | Focus |
|---|---|
| [Linux](linux.md) | Linux enumeration and privilege escalation |
| [Windows](windows.md) | Windows host assessment and privilege escalation |
| [PowerShell](powershell.md) | Windows and PowerShell security assessment commands |
| [Networking](networking.md) | Network enumeration, connectivity and pivoting |
| [Web](web.md) | Web application security testing |
| [Active Directory](active-directory.md) | Active Directory assessment methodology |
| [NetExec](netexec.md) | SMB, LDAP, WinRM and MSSQL assessment |
| [Impacket](impacket.md) | Windows and AD protocol tooling |
| [BloodHound](bloodhound.md) | Active Directory graph and attack-path analysis |


## Recommended Workflow

For an Active Directory engagement:

```text
Networking
    |
    v
Active Directory
    |
    v
NetExec
    |
    v
BloodHound
    |
    v
Impacket
    |
    v
Windows / PowerShell
```

For a web application engagement:

```text
Networking
    |
    v
Web
    |
    v
Detailed Web Notes
```

For a Windows host:

```text
Windows
   |
   v
PowerShell
   |
   v
Active Directory
   |
   v
NetExec / BloodHound / Impacket
```

For a Linux host:

```text
Linux
  |
  v
Networking
  |
  v
Service-Specific Testing
```


## Final Principle

A useful security cheatsheet should help answer more than:

> What command do I run?

It should help answer:

```text
Why am I running it?

When does it apply?

What should I expect?

What does the result mean?

What does the result not mean?

What should I validate next?

When do I have enough evidence?

How should the issue be remediated?

How should I retest it?
```

That is the model used throughout these cheatsheets.

<div class="terminal">
Identify. Test. Interpret. Validate. Document.
</div>


## Related Knowledge Base Sections

- [Web Application Security](../web/index.md)
- [Active Directory](../active-directory/index.md)
- [Windows](../windows/index.md)
- [Linux](../linux/index.md)
- [Red Teaming](../red-teaming/index.md)
- [Purple Teaming](../purple-teaming/index.md)
- [Vulnerability Research](../vulnerability-research/index.md)
- [Tools](../tools/index.md)
- [PrivEsc Explorer](../privesc/index.md)


## References

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }
- [BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }
- [NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }
- [Impacket GitHub](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Windows Security](https://learn.microsoft.com/en-us/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Learn - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }
