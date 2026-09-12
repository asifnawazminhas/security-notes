---
title: Security Tools
description: Practical security tooling reference for web enumeration, web application testing, Active Directory, privilege escalation, tunnelling, command and control, source code review, red teaming, vulnerability research, network analysis, and AI-assisted security workflows.
---

# Security Tools

Security tools are most useful when they are connected to a clear testing objective.

This section is not intended to be a collection of commands without context.

The purpose is to connect:

```text
Security Question
      |
      v
Methodology
      |
      v
Appropriate Tool
      |
      v
Observation
      |
      v
Interpretation
      |
      v
Manual Validation
      |
      v
Evidence
      |
      v
Security Conclusion
```

A tool can help collect evidence.

It does not determine the final security conclusion.

!!! warning "Authorised testing only"
    The tools documented in this knowledge base are intended for systems, applications, networks, software and environments that you own or are explicitly authorised to assess. Some tools can generate significant traffic, change system state, interact with sensitive data, establish command-and-control channels, access authentication material, pivot between networks or affect availability. Confirm scope, testing restrictions, rate limits, permitted techniques and operational risk before use.

---

## Start Here

Choose the tool category based on the security question you are trying to answer.

<div class="grid cards" markdown>

-   :material-web:{ .lg .middle } **Web Enumeration**

    ---

    Identify technologies, HTTP services, titles, redirects, headers and other application-surface indicators.

    [:octicons-arrow-right-24: Web Enumeration Tools](web-enumeration/index.md)

-   :material-bug-outline:{ .lg .middle } **Web Application Testing**

    ---

    Intercept, crawl, discover, scan and validate web application behaviour using Burp Suite, ffuf, Katana, Nuclei, sqlmap and Interactsh.

    [:octicons-arrow-right-24: Web Testing Tools](web-testing/index.md)

-   :material-microsoft-windows:{ .lg .middle } **Active Directory**

    ---

    Select tooling for directory enumeration, authentication, Kerberos, relationship analysis, certificate services and protocol-specific assessment.

    [:octicons-arrow-right-24: Active Directory Tools](active-directory/index.md)

-   :material-lan-connect:{ .lg .middle } **Tunnelling and Pivoting**

    ---

    Build controlled network paths through authorised systems using Ligolo-ng and Chisel.

    [:octicons-arrow-right-24: Ligolo-ng](ligolo-ng.md)

-   :material-key-chain:{ .lg .middle } **Windows and AD Operations**

    ---

    Investigate Windows authentication, Kerberos and certificate services using Mimikatz, Rubeus, Certify and Certipy.

    [:octicons-arrow-right-24: Rubeus](rubeus.md)

-   :material-access-point-network:{ .lg .middle } **Command and Control**

    ---

    Understand authorised command-and-control infrastructure, sessions, beacons, pivoting, evidence and defensive visibility using Sliver and Cobalt Strike.

    [:octicons-arrow-right-24: Cobalt Strike](cobalt-strike.md)

-   :material-shield-key:{ .lg .middle } **Privilege Escalation**

    ---

    Accelerate Windows and Linux privilege escalation enumeration with WinPEAS, LinPEAS, PowerUp, PrivescCheck and linux-smart-enumeration.

    [:octicons-arrow-right-24: Privilege Escalation Tools](privilege-escalation/index.md)

-   :material-code-braces:{ .lg .middle } **Source Code Review**

    ---

    Use ripgrep, Semgrep, OpenGrep and CodeQL to support manual source-to-sink analysis and variant research.

    [:octicons-arrow-right-24: Source Code Review Tools](source-code-review/index.md)

-   :material-sword-cross:{ .lg .middle } **Red Teaming**

    ---

    Connect red team tooling to objectives, infrastructure, command and control, operational safety, detection and evidence.

    [:octicons-arrow-right-24: Red Teaming Tools](red-teaming/index.md)

-   :material-shield-search:{ .lg .middle } **Vulnerability Research**

    ---

    Select debuggers, reverse-engineering tools, fuzzers, tracing utilities and supporting analysis tools.

    [:octicons-arrow-right-24: Vulnerability Research Tools](vulnerability-research/index.md)

-   :material-robot-outline:{ .lg .middle } **AI-Assisted Security**

    ---

    Use LLMs to assist security analysis while maintaining independent validation, scope controls and evidence quality.

    [:octicons-arrow-right-24: AI-Assisted Security](ai/index.md)

</div>

---

# Tool Selection

Do not begin with:

> Which tool should I run?

Begin with:

> What security question am I trying to answer?

| Security Question | Useful Tools |
|---|---|
| What technologies are exposed by this website? | WhatWeb, Wappalyzer, httpx |
| Which discovered hosts respond over HTTP or HTTPS? | httpx |
| Which content or routes are not directly linked? | ffuf, Katana |
| What does this HTTP request actually do? | Burp Suite |
| Can a suspected web issue be reproduced manually? | Burp Suite |
| Can repeatable checks identify additional candidates? | Nuclei |
| Does a parameter appear vulnerable to SQL injection? | Burp Suite, sqlmap |
| Did the server perform an out-of-band interaction? | Interactsh |
| What Active Directory relationships exist? | BloodHound |
| Which AD protocols and services are accessible? | NetExec, Impacket |
| What Kerberos behaviour needs focused validation? | Rubeus |
| How should Windows authentication material be investigated? | Mimikatz |
| Are AD CS configurations security relevant? | Certify, Certipy |
| Do I need routed access through an authorised pivot? | Ligolo-ng |
| Do I need focused TCP/UDP forwarding or SOCKS over HTTP/WebSockets? | Chisel |
| Do I need collaborative authorised C2 infrastructure? | Sliver, Cobalt Strike |
| What privilege escalation candidates exist on Windows? | WinPEAS, PowerUp, PrivescCheck |
| What privilege escalation candidates exist on Linux? | LinPEAS, linux-smart-enumeration |
| Where does untrusted input reach sensitive code? | ripgrep, Semgrep, OpenGrep, CodeQL |
| How does a crashing program behave? | GDB, WinDbg, x64dbg |
| Can the same vulnerable code pattern exist elsewhere? | CodeQL, Semgrep, ripgrep |
| Can an LLM help explain unfamiliar code or output? | LLM-assisted analysis followed by independent validation |

A tool is an **evidence collection mechanism**, not the conclusion itself.

---

# Web Enumeration

Web enumeration attempts to understand what is exposed before deeper testing begins.

Typical objectives include:

- identifying web servers;
- identifying frameworks and CMS platforms;
- identifying JavaScript technologies;
- identifying live HTTP services;
- collecting status codes and titles;
- examining redirects;
- identifying unusual headers;
- recognising default error pages;
- prioritising targets for deeper testing.

```text
Assets
  |
  v
HTTP Services
  |
  v
Technology Indicators
  |
  v
Manual Correlation
  |
  v
Prioritised Targets
```

## WhatWeb

WhatWeb fingerprints technologies based on indicators in HTTP responses and page content.

Useful for:

- server identification;
- framework indicators;
- CMS indicators;
- cookies;
- page metadata;
- characteristic HTML.

[WhatWeb](web-enumeration/whatweb.md)

## Wappalyzer

Wappalyzer provides technology identification while browsing an application.

Useful for:

- frameworks;
- JavaScript libraries;
- CMS platforms;
- infrastructure;
- analytics;
- frontend technologies.

[Wappalyzer](web-enumeration/wappalyzer.md)

## httpx

ProjectDiscovery httpx enriches discovered hosts and URLs with HTTP information.

Useful for:

- live HTTP services;
- status codes;
- page titles;
- technologies;
- redirects;
- TLS information;
- service prioritisation.

[httpx](web-enumeration/httpx.md)

## Fingerprints Beyond Tools

Automated fingerprinting should be combined with:

- default 404 pages;
- default 403 pages;
- HTTP headers;
- cookie names;
- error templates;
- static asset paths;
- JavaScript bundles;
- favicon behaviour;
- API error formats.

A useful visual reference is:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

Related methodology:

[Web Reconnaissance](../web/reconnaissance/index.md)

[Technology Identification](../web/reconnaissance/technology-identification.md)

[Attack Surface Analysis](../web/attack-surface-analysis.md)

---

# Web Application Testing

Enumeration identifies what may exist.

Web application testing investigates how the application behaves and whether a security boundary can be crossed.

```text
Application Surface
      |
      v
Candidate Behaviour
      |
      v
Focused Tool
      |
      v
Manual Reproduction
      |
      v
Impact Validation
```

## Burp Suite

Burp Suite is the central interactive tool for many web application testing workflows.

Useful for:

- intercepting requests;
- modifying requests;
- replaying requests;
- comparing responses;
- authentication testing;
- authorisation testing;
- session analysis;
- APIs;
- WebSockets;
- GraphQL;
- extension-assisted testing.

[Burp Suite](web-testing/burp-suite.md)

## ffuf

ffuf is useful for focused content and input discovery.

Typical uses include:

- directories;
- files;
- extensions;
- virtual hosts;
- parameters;
- API paths.

Its effectiveness depends heavily on understanding the baseline response and filtering noise correctly.

[ffuf](web-testing/ffuf.md)

## Katana

Katana is a crawler from ProjectDiscovery.

It helps discover:

- linked routes;
- forms;
- JavaScript-referenced resources;
- API endpoints;
- additional application surface.

[Katana](web-testing/katana.md)

## Nuclei

Nuclei uses templates to perform repeatable security checks.

It can identify candidates related to:

- known vulnerabilities;
- exposures;
- misconfiguration;
- technologies;
- exposed files.

A template match should be manually understood and validated before becoming a finding.

[Nuclei](web-testing/nuclei.md)

## sqlmap

sqlmap automates SQL injection testing.

It is most useful after manual testing has identified a plausible SQL injection candidate.

```text
Candidate Parameter
      |
      v
Manual SQLi Hypothesis
      |
      v
Focused sqlmap Validation
      |
      v
Manual Confirmation
```

[sqlmap](web-testing/sqlmap.md)

## Interactsh

Interactsh provides out-of-band interaction infrastructure.

It is useful for investigating behaviour such as:

- blind SSRF;
- blind XXE;
- asynchronous callbacks;
- DNS interactions;
- HTTP interactions.

A callback confirms an interaction occurred.

The tester must still establish which component caused it and what security boundary was affected.

[Interactsh](web-testing/interactsh.md)

Related section:

[Web Application Security](../web/index.md)

---

# Active Directory Tools

Active Directory testing often requires combining information from several protocols and data sources.

The purpose of this tool category is to help answer:

```text
What should I use
for this AD question?
```

rather than duplicate the full Active Directory methodology.

[Active Directory Tools](active-directory/index.md)

## NetExec

Useful for protocol-oriented Windows and Active Directory assessment involving areas such as:

- SMB;
- LDAP;
- WinRM;
- authentication;
- hosts;
- shares;
- users;
- groups.

The detailed canonical page remains:

[NetExec](../active-directory/netexec.md)

## Impacket

Impacket provides Python implementations of many protocols encountered in Windows and Active Directory environments.

Its scripts are commonly associated with:

- SMB;
- MSRPC;
- Kerberos;
- NTLM;
- authentication;
- remote administration.

Canonical page:

[Impacket](../active-directory/impacket.md)

## BloodHound

BloodHound models identity and privilege relationships as a graph.

```text
Directory Data
      |
      v
Relationships
      |
      v
Candidate Attack Paths
      |
      v
Manual Validation
```

Canonical page:

[BloodHound](../active-directory/bloodhound.md)

## Mimikatz

Mimikatz supports authorised investigation of Windows authentication material and security boundaries.

It is useful for understanding areas such as:

- logon-session context;
- Windows authentication material;
- Kerberos;
- DPAPI;
- certificate and key material;
- LSA-related security behaviour.

[Mimikatz](mimikatz.md)

A successful command does not by itself establish privilege escalation or broader compromise. Interpret the result in the context of the current token, host protections and the specific authentication boundary being tested.

## Rubeus

Rubeus is a .NET toolkit focused on Kerberos interaction and assessment.

Useful areas include:

- ticket enumeration;
- TGT and TGS workflows;
- ticket properties;
- Kerberoasting and AS-REP roasting assessment;
- delegation-related Kerberos behaviour;
- ticket cache analysis.

[Rubeus](rubeus.md)

Keep separate:

```text
Kerberos Behaviour Observed
        !=
Privilege Obtained
```

## Certify

Certify is a Windows/.NET-focused tool for Active Directory Certificate Services assessment.

It can assist with:

- CA discovery;
- certificate-template enumeration;
- enrolment analysis;
- AD CS permission analysis;
- controlled certificate request validation.

[Certify](certify.md)

## Certipy

Certipy is a Python toolkit for Active Directory Certificate Services assessment.

It can assist with:

- CA and template enumeration;
- certificate requests;
- certificate authentication;
- certificate handling;
- AD CS privilege-path analysis;
- Shadow Credentials assessment;
- relay-related AD CS analysis.

[Certipy](certipy.md)

Related section:

[Active Directory Certificate Services](../active-directory/ad-cs/index.md)

---

# Tunnelling and Pivoting

Tunnelling and pivoting tools create controlled paths between an operator and otherwise unreachable in-scope services.

The important reasoning model is:

```text
Additional Network Observed
        |
        v
Scope Confirmed
        |
        v
Pivot Host Reachability Confirmed
        |
        v
Appropriate Tunnel Selected
        |
        v
Specific Service Validated
        |
        v
Evidence
```

A tunnel cannot create network reachability that the pivot host itself does not possess.

## Ligolo-ng

Ligolo-ng provides TUN-based tunnelling and routed access through an authorised agent.

Useful for:

- accessing internal networks;
- using tools that expect normal routed connectivity;
- multi-hop pivoting;
- listener forwarding;
- TCP, UDP and ICMP-oriented workflows.

[Ligolo-ng](ligolo-ng.md)

Its routed model is particularly useful when multiple tools and services must operate across the pivot.

## Chisel

Chisel provides TCP/UDP tunnelling over HTTP/WebSockets with SSH-based security.

Useful for:

- forward port forwarding;
- reverse port forwarding;
- SOCKS;
- reverse SOCKS;
- proxy-aware tunnelling;
- focused service access.

[Chisel](chisel.md)

A useful selection model is:

```text
Broad Routed Access
        |
        +--> Ligolo-ng

Focused Port Forwarding / SOCKS
        |
        +--> Chisel
```

---

# Command and Control

Command-and-control frameworks provide an operator channel for controlled adversary simulation.

The existence of a C2 session proves only the security boundaries actually demonstrated.

```text
Code Execution
        +
C2 Communication
        =
C2 Capability
```

It does not automatically prove:

```text
Privilege Escalation
Credential Access
Lateral Movement
Persistence
Domain Compromise
Data Exfiltration
```

Each requires separate validation.

## Sliver

Sliver is an open-source C2 framework from Bishop Fox.

Its capabilities include concepts such as:

- central C2 infrastructure;
- sessions;
- asynchronous beacons;
- multiple communication protocols;
- SOCKS;
- port forwarding;
- multiplayer operation;
- Armory extensions.

[Sliver](sliver.md)

## Cobalt Strike

Cobalt Strike is a commercial adversary-simulation and red-team operations platform from Fortra.

Its architecture includes:

- Team Server;
- Beacon;
- listeners;
- Malleable C2;
- SOCKS and forwarding;
- peer-to-peer communication;
- BOFs;
- Aggressor Script;
- multiplayer operation;
- reporting and automation.

[Cobalt Strike](cobalt-strike.md)

Use only legitimate licensed Cobalt Strike software obtained through authorised channels.

## C2 Selection

Choose a framework according to the assessment requirement rather than popularity.

Consider:

```text
Assessment Objective
        |
        v
Target Environment
        |
        v
Required Transport
        |
        v
Operator Model
        |
        v
Required Capability
        |
        v
Defensive Visibility
        |
        v
Operational Risk
```

Related overview:

[C2 Frameworks](red-teaming/c2-frameworks.md)

---

# Privilege Escalation Tools

Privilege escalation tools can quickly enumerate large numbers of system settings.

They should be used to identify **candidates**, not to automatically declare vulnerabilities.

```text
Enumeration
    |
    v
Candidate
    |
    v
Manual Configuration Review
    |
    v
Effective Permission Check
    |
    v
Execution Context
    |
    v
Controlled Validation
```

[Privilege Escalation Tools](privilege-escalation/index.md)

## Windows

### WinPEAS

Broad Windows privilege escalation enumeration.

[WinPEAS](privilege-escalation/winpeas.md)

### PowerUp

PowerShell-based Windows privilege escalation checks.

[PowerUp](privilege-escalation/powerup.md)

### PrivescCheck

PowerShell-based Windows privilege escalation enumeration with structured security checks.

[PrivescCheck](privilege-escalation/privesccheck.md)

## Linux

### LinPEAS

Broad Linux privilege escalation enumeration.

[LinPEAS](privilege-escalation/linpeas.md)

### linux-smart-enumeration

An additional Linux enumeration perspective that complements LinPEAS and manual investigation.

[linux-smart-enumeration](privilege-escalation/linux-smart-enumeration.md)

Related sections:

[PrivEsc Explorer](../privesc/index.md)

[Windows Privilege Escalation](../windows/privilege-escalation.md)

[Linux Privilege Escalation](../linux/privilege-escalation.md)

---

# Source Code Review Tools

Source code review tools help locate and prioritise interesting code.

They do not replace manual data-flow analysis.

```text
Entry Point
    |
    v
User-Controlled Data
    |
    v
Transformation
    |
    v
Validation
    |
    v
Sensitive Sink
```

[Source Code Review Tools](source-code-review/index.md)

The detailed static-analysis pages remain canonical under Source Code Review.

## ripgrep

Useful for rapidly locating:

- routes;
- security-sensitive APIs;
- authentication logic;
- authorisation logic;
- secrets;
- configuration;
- file operations;
- process execution;
- database queries.

[ripgrep](../source-code-review/static-analysis/ripgrep.md)

## Semgrep

Useful for language-aware security pattern matching across larger repositories.

[Semgrep](../source-code-review/static-analysis/semgrep.md)

## OpenGrep

Useful for static-analysis workflows based on rule-driven source inspection.

[OpenGrep](../source-code-review/static-analysis/opengrep.md)

## CodeQL

Useful for deeper semantic analysis, data-flow analysis and variant research.

[CodeQL](../source-code-review/static-analysis/codeql.md)

Related methodology:

[Source Code Review](../source-code-review/index.md)

[Source-to-Sink Analysis](../source-code-review/source-to-sink-analysis.md)

---

# Red Teaming Tools

Red team tooling should be selected according to:

```text
Objective
   |
   v
Technique
   |
   v
Operational Requirement
   |
   v
Tool
   |
   v
Controlled Execution
   |
   v
Evidence + Detection
```

[Red Teaming Tools](red-teaming/index.md)

## Network Access

The completed tunnelling tools are:

- [Ligolo-ng](ligolo-ng.md)
- [Chisel](chisel.md)

## Windows and Active Directory Operations

The completed Windows and AD-focused tool pages are:

- [Mimikatz](mimikatz.md)
- [Rubeus](rubeus.md)
- [Certify](certify.md)
- [Certipy](certipy.md)

## Command-and-Control Frameworks

The detailed C2 tool pages are:

- [Sliver](sliver.md)
- [Cobalt Strike](cobalt-strike.md)

The broader framework comparison remains:

[C2 Frameworks](red-teaming/c2-frameworks.md)

Related section:

[Red Teaming](../red-teaming/index.md)

---

# Vulnerability Research Tools

Vulnerability research requires tools that help answer questions about software behaviour rather than simply target exposure.

[Vulnerability Research Tools](vulnerability-research/index.md)

Typical categories include:

| Activity | Example Tools |
|---|---|
| Linux debugging | GDB |
| GDB enhancement | GEF, pwndbg |
| Windows debugging | WinDbg |
| Windows user-mode debugging | x64dbg |
| Reverse engineering | Ghidra, IDA, Binary Ninja |
| Coverage-guided fuzzing | AFL++ |
| Compiler-integrated fuzzing | libFuzzer |
| Runtime instrumentation | Frida |
| Linux tracing | strace, ltrace |
| Windows runtime observation | Process Monitor, Process Explorer |
| Network analysis | Wireshark, tcpdump |

The research workflow is:

```text
Input / Trigger
      |
      v
Program Behaviour
      |
      v
Crash / Security Anomaly
      |
      v
Debugger / Tracing
      |
      v
Root Cause
      |
      v
Variant Analysis
      |
      v
Minimal PoC
```

Related methodology:

[Vulnerability Research](../vulnerability-research/index.md)

[Vulnerability Research Methodology](../vulnerability-research/methodology.md)

[Debugging and Dynamic Analysis](../vulnerability-research/debugging-dynamic-analysis.md)

[Fuzzing](../vulnerability-research/fuzzing.md)

[Crash Analysis](../vulnerability-research/crash-analysis.md)

[Patch Diffing](../vulnerability-research/patch-diffing.md)

---

# Network and Protocol Analysis

Some tools support several security disciplines rather than belonging to one category.

Examples include:

- Nmap;
- Wireshark;
- TShark;
- tcpdump;
- curl;
- OpenSSL;
- protocol-specific clients.

These are useful because many security conclusions depend on understanding how systems communicate.

## Nmap

Nmap supports:

- host discovery;
- port discovery;
- service identification;
- protocol investigation.

```text
Scope
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
Manual Protocol Validation
```

Version detection should be treated cautiously because banners may be:

- modified;
- proxied;
- incomplete;
- affected by backported patches.

Official documentation:

[Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }

## Wireshark and TShark

Packet analysis can help determine:

- which hosts communicated;
- which protocol was used;
- whether DNS resolution occurred;
- whether TCP completed;
- whether TLS negotiated;
- which requests were transmitted;
- whether resets or retransmissions occurred.

Official documentation:

[Wireshark Documentation](https://www.wireshark.org/docs/){ target="_blank" rel="noopener noreferrer" }

Related cheatsheets:

[Networking Cheatsheet](../cheatsheets/networking.md)

[Nmap Cheatsheet](../cheatsheets/nmap.md)

[Wireshark and tshark Cheatsheet](../cheatsheets/wireshark-tshark.md)

---

# AI-Assisted Security

Large language models can assist with security analysis and knowledge work.

They should not be treated as authoritative security evidence.

[AI-Assisted Security](ai/index.md)

[LLM-Assisted Security Testing](ai/llm-assisted-security-testing.md)

Useful applications include:

- explaining unfamiliar source code;
- reviewing tool output;
- generating search ideas;
- comparing configurations;
- summarising logs;
- assisting with research;
- developing test hypotheses;
- structuring findings;
- supporting variant-analysis workflows.

The correct model is:

```text
Security Data / Code
        |
        v
       LLM
        |
        v
Hypothesis / Explanation
        |
        v
Independent Validation
        |
        v
Evidence
        |
        v
Conclusion
```

Important considerations include:

- hallucinations;
- missing context;
- confidentiality;
- source-code sensitivity;
- credentials and secrets;
- prompt injection;
- organisational policy;
- reproducibility.

---

# Tool Output Is Not a Finding

One of the core principles of this knowledge base is:

> A tool finding is not automatically a security finding.

Examples:

```text
Nuclei template match
        !=
Confirmed vulnerability
```

```text
WinPEAS warning
        !=
Privilege escalation
```

```text
BloodHound edge
        !=
Confirmed compromise path
```

```text
Certipy ESC classification
        !=
Confirmed certificate abuse
```

```text
Rubeus output
        !=
Privilege obtained
```

```text
C2 session
        !=
Administrative access
```

```text
LLM explanation
        !=
Verified fact
```

Tools provide observations.

The tester provides interpretation.

---

# Failed Commands Are Also Not Findings

A failed command does not automatically prove that a security control blocked it.

Possible causes include:

```text
Wrong Syntax
Missing Dependency
Network Failure
Permissions
Tool Bug
Version Difference
Security Control
```

The tester should identify the actual cause before reporting a control as effective.

This distinction is especially important when assessing:

- Defender;
- EDR;
- WDAC;
- AppLocker;
- CLM;
- AMSI;
- network filtering;
- Kerberos;
- certificate services;
- C2 communications.

---

# Manual Validation

A useful validation process is:

```text
Tool Output
    |
    v
What Exactly Was Observed?
    |
    v
What Does the Tool Assume?
    |
    v
Can I Verify the Condition Manually?
    |
    v
Can I Demonstrate the Security Boundary?
    |
    v
Can I Reproduce It Reliably?
```

Manual validation may involve:

- repeating a request;
- reviewing effective permissions;
- checking configuration;
- comparing authenticated users;
- inspecting raw packets;
- examining source code;
- reproducing a crash;
- validating an AD relationship;
- confirming a certificate mapping condition;
- confirming the effective execution context;
- correlating endpoint and network telemetry.

---

# Tool Chaining

Tools are often most useful when they contribute different forms of evidence.

## Web Example

```text
httpx
  |
  v
Live Service
  |
  v
WhatWeb / Wappalyzer
  |
  v
Technology Hypothesis
  |
  v
Burp Suite
  |
  v
Manual Testing
```

## Content Discovery Example

```text
Katana
  |
  v
Discovered Routes
  |
  v
ffuf
  |
  v
Additional Candidates
  |
  v
Burp Suite
  |
  v
Manual Validation
```

## Active Directory Example

```text
NetExec
   |
   v
Protocol / Host Context
   |
   v
BloodHound
   |
   v
Candidate Relationship
   |
   v
Manual Permission Validation
```

## Kerberos Example

```text
Directory / Identity Context
        |
        v
Rubeus
        |
        v
Kerberos Observation
        |
        v
KDC / Ticket Validation
        |
        v
Security Conclusion
```

## AD CS Example

```text
Certipy / Certify
        |
        v
Candidate AD CS Condition
        |
        v
Template + CA + ACL Review
        |
        v
Controlled Validation
        |
        v
Authentication Behaviour
        |
        v
Security Conclusion
```

## Pivoting Example

```text
Internal Interface Observed
        |
        v
Scope Confirmed
        |
        v
Ligolo-ng / Chisel
        |
        v
Specific Service Reachability
        |
        v
Dedicated Assessment Tool
```

## C2 Example

```text
Authorised Test Artifact
        |
        v
Execution
        |
        v
Sliver / Cobalt Strike
        |
        v
Session Context
        |
        v
Approved Test Action
        |
        v
Endpoint + Network Telemetry
        |
        v
Security Conclusion
```

## Privilege Escalation Example

```text
WinPEAS
   |
   v
Candidate Misconfiguration
   |
   v
Manual ACL Review
   |
   v
Privileged Consumer
   |
   v
Controlled Validation
```

## Source Review Example

```text
ripgrep
   |
   v
Candidate Sink
   |
   v
Manual Data Flow
   |
   v
Semgrep / CodeQL
   |
   v
Variant Search
```

The tools complement each other.

They should not blindly confirm each other's assumptions.

---

# Operational Safety

Before running a tool, understand what it will do.

## Traffic Generation

Determine whether it:

- sends concurrent requests;
- performs recursion;
- retries automatically;
- brute-forces inputs;
- follows redirects;
- processes large wordlists;
- creates long-lived connections;
- generates periodic beacon traffic;
- forwards traffic into another network.

## Authentication

Avoid unintentionally:

- locking accounts;
- invalidating sessions;
- repeatedly triggering MFA;
- exhausting quotas;
- testing unintended identities;
- changing certificate or Kerberos state unnecessarily.

## State Changes

Determine whether it can:

- upload files;
- create accounts;
- modify configuration;
- execute code;
- write database content;
- alter services;
- trigger background workflows;
- request certificates;
- modify directory objects;
- create pivot listeners;
- establish command-and-control channels.

## Third Parties

A third-party domain referenced by an in-scope application is not automatically in scope.

Likewise, a network reachable through an authorised pivot is not automatically in scope.

---

# Reproducibility

Record relevant tool context:

```text
Tool:
Version:
Date/time:
Target:
Input:
Command:
Configuration:
Authentication context:
Relevant output:
Manual validation:
Conclusion:
```

For generated assessment artifacts, also consider:

```text
SHA256:
Generation time:
Deployment host:
Deployment time:
Removal time:
```

Tool versions matter because:

- flags change;
- APIs change;
- templates change;
- defaults change;
- output formats change;
- detection logic changes;
- supported protocols change.

---

# Evidence Collection

Useful evidence may include:

- exact command;
- tool version;
- affected target;
- timestamp;
- request and response;
- selected terminal output;
- packet capture;
- screenshot;
- authentication context;
- relevant configuration;
- manual reproduction;
- file hash;
- session identifier;
- certificate request identifier;
- relevant endpoint telemetry;
- relevant network telemetry.

Do not attach enormous raw tool outputs without interpretation.

Extract the evidence that supports the security conclusion.

---

# False Positives

False positives may be caused by:

- wildcard DNS;
- generic responses;
- catch-all routes;
- authentication redirects;
- reverse proxies;
- WAF behaviour;
- CDNs;
- stale signatures;
- misleading banners;
- scanner assumptions;
- incomplete directory context;
- outdated attack-path assumptions;
- certificate mapping changes;
- tool-version differences.

A useful process is:

```text
Tool Match
    |
    v
Inspect Raw Evidence
    |
    v
Establish Baseline
    |
    v
Reproduce Independently
    |
    v
Compare Results
    |
    v
Confirm or Reject
```

---

# False Negatives

Security tools can also miss real issues because of:

- authentication;
- unusual workflows;
- JavaScript-heavy applications;
- WAF interference;
- missing routes;
- custom protocols;
- business logic;
- state-dependent behaviour;
- environment-specific conditions;
- network segmentation;
- tool-version limitations;
- modern platform mitigations;
- incomplete privileges.

A clean scan does not prove that the target is secure.

---

# Reporting Tool-Assisted Findings

Avoid:

```text
Nuclei found a vulnerability.
```

Prefer:

```text
Automated testing identified behaviour consistent with the suspected
condition. Manual validation subsequently reproduced the behaviour and
confirmed the security impact.
```

Avoid:

```text
WinPEAS found privilege escalation.
```

Prefer:

```text
Enumeration identified a security-relevant configuration. Manual
validation confirmed that the current user could influence the affected
resource and that it participated in a privileged execution path.
```

Avoid:

```text
Certipy found ESC1.
```

Prefer describing:

```text
Who can enrol
        +
Which certificate identity can be controlled
        +
Whether the certificate supports authentication
        +
How the environment maps that certificate
        =
Supported security impact
```

Avoid:

```text
Cobalt Strike worked.
```

Prefer describing the actual boundary demonstrated, such as:

```text
Code execution was possible in the tested user context and the process
established an outbound command-and-control connection to authorised
assessment infrastructure.
```

The report should describe the **security condition** rather than the tool.

---

# Tool Documentation Model

Detailed tool pages in this knowledge base generally follow:

```text
Purpose
   |
   v
When to Use It
   |
   v
Installation / Verification
   |
   v
Core Workflow
   |
   v
Practical Examples
   |
   v
Representative Result
   |
   v
Interpretation
   |
   v
Common Mistakes
   |
   v
Manual Validation
   |
   v
Evidence
   |
   v
Detection / Defence
   |
   v
Cleanup
   |
   v
Related Security Topics
```

This keeps tooling connected to methodology.

---

# External References

External resources are used where they add specialist depth rather than duplicating local notes.

Priority is generally given to:

1. official documentation;
2. official repositories;
3. vendor documentation;
4. PortSwigger for web application security;
5. Microsoft Learn for Windows and Active Directory;
6. ProjectDiscovery documentation;
7. strong specialist references such as 0xdf;
8. HackTricks where broader offensive-security context is useful.

Useful references:

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

[ProjectDiscovery Documentation](https://docs.projectdiscovery.io/){ target="_blank" rel="noopener noreferrer" }

[Microsoft Learn](https://learn.microsoft.com/){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

[HackTricks](https://book.hacktricks.wiki/){ target="_blank" rel="noopener noreferrer" }

---

# Related Knowledge Base Sections

[Web Application Security](../web/index.md)

[Source Code Review](../source-code-review/index.md)

[Active Directory](../active-directory/index.md)

[Windows](../windows/index.md)

[Linux](../linux/index.md)

[Privilege Escalation Explorer](../privesc/index.md)

[Red Teaming](../red-teaming/index.md)

[Purple Teaming](../purple-teaming/index.md)

[Vulnerability Research](../vulnerability-research/index.md)

[Cheatsheets](../cheatsheets/index.md)

---

# Final Tooling Model

Do not use security tools like this:

```text
Run Tool
   |
   v
Read Highlight
   |
   v
Report Finding
```

Use them like this:

```text
Security Question
       |
       v
Understand Methodology
       |
       v
Choose Appropriate Tool
       |
       v
Collect Observation
       |
       v
Interpret Context
       |
       v
Validate Manually
       |
       v
Correlate Evidence
       |
       v
Determine Supported Impact
       |
       v
Report
       |
       v
Remediate
       |
       v
Retest
```

The most valuable skill is not knowing the largest number of security tools.

It is knowing:

- what question to ask;
- which tool can help answer it;
- what the output actually means;
- when that output may be misleading;
- how to validate it;
- how it connects to the underlying security concept;
- and when enough evidence exists to support a defensible conclusion.
