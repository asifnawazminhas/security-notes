---
title: Security Tools
description: Practical security tooling reference for web application testing, reconnaissance, Active Directory, privilege escalation, source code review, red teaming, vulnerability research, network analysis, and AI-assisted security workflows.
---

# Security Tools

Security tools are most useful when they are connected to a clear testing objective.

This section is not intended to be a collection of commands without context. Each tool should answer questions such as:

- What problem does the tool help solve?
- At what stage of an assessment should it be used?
- What information does it require?
- What does useful output look like?
- What conclusions can and cannot be drawn from the output?
- What manual validation should follow?
- Which security topic explains the underlying technique?
- What evidence should be retained for reporting?
- What other tools can confirm or complement the result?

The goal is to connect **methodology, tooling, interpretation, validation, and evidence**.

```text
Security Objective
       |
       v
Choose Appropriate Tool
       |
       v
Collect Result
       |
       v
Interpret Result
       |
       v
Validate Manually
       |
       v
Correlate With Other Evidence
       |
       v
Security Conclusion
```

!!! warning "Authorised testing only"
    The tools documented in this knowledge base are intended for systems, applications, networks, and environments that you own or are explicitly authorised to assess. Some tools can generate significant traffic or perform intrusive actions. Confirm scope, testing restrictions, rate limits, and operational risk before use.

---

## How This Section Is Organised

Tools are grouped by the security activity they support rather than by programming language, operating system, or popularity.

```text
Tools
|
+-- Web Enumeration
|   +-- WhatWeb
|   +-- Wappalyzer
|   +-- httpx
|
+-- Web Application Testing
|   +-- Burp Suite
|   +-- ffuf
|   +-- Nuclei
|   +-- sqlmap
|   +-- Katana
|   +-- Interactsh
|
+-- Active Directory
|   +-- NetExec
|   +-- Impacket
|   +-- BloodHound
|   +-- Certipy
|
+-- Privilege Escalation
|   +-- WinPEAS
|   +-- LinPEAS
|   +-- PowerUp
|   +-- PrivescCheck
|   +-- linux-smart-enumeration
|
+-- Source Code Review
|   +-- ripgrep
|   +-- Semgrep
|   +-- OpenGrep
|   +-- CodeQL
|
+-- Red Teaming
|   +-- Command-and-Control Frameworks
|   +-- Supporting Infrastructure
|
+-- Vulnerability Research
|   +-- Debuggers
|   +-- Fuzzers
|   +-- Binary Analysis
|
+-- Network and Protocol Analysis
|   +-- Nmap
|   +-- Wireshark
|   +-- TShark
|   +-- tcpdump
|
+-- AI-Assisted Security
    +-- LLM-Assisted Security Testing
```

The categories are intentionally connected to the main sections of this knowledge base.

---

# Tool Selection

Do not start an assessment by asking:

> Which tool should I run?

Start with:

> What security question am I trying to answer?

Examples:

| Security Question | Possible Tools |
|---|---|
| What technologies are exposed by this website? | WhatWeb, Wappalyzer, httpx |
| Which hosts respond over HTTP or HTTPS? | httpx, Nmap |
| Which content is exposed but not directly linked? | ffuf, Katana |
| What does the application do with this request? | Burp Suite |
| Can a suspected issue be reproduced manually? | Burp Suite, curl |
| Can known checks identify additional candidates? | Nuclei |
| What subdomains belong to the target scope? | Subfinder, Amass |
| What Active Directory relationships exist? | BloodHound |
| What AD protocols and services are accessible? | NetExec, Impacket |
| Are certificate services exposed or misconfigured? | Certipy |
| What privilege escalation opportunities exist on Windows? | WinPEAS, PowerUp, PrivescCheck |
| What privilege escalation opportunities exist on Linux? | LinPEAS, linux-smart-enumeration |
| Where does untrusted input reach dangerous functionality? | ripgrep, Semgrep, OpenGrep, CodeQL |
| What is happening on the network? | Wireshark, TShark, tcpdump |
| How does a binary behave when it crashes? | GDB, WinDbg, x64dbg |
| Can a suspected code pattern occur elsewhere? | CodeQL, Semgrep, ripgrep |
| Can an LLM help understand unfamiliar code or output? | LLM-assisted analysis followed by independent validation |

A tool is an **evidence collection mechanism**, not the conclusion itself.

---

# Web Enumeration

Web enumeration attempts to understand what is exposed before deeper testing begins.

Typical objectives include:

- identifying web servers;
- identifying frameworks and CMS platforms;
- identifying JavaScript technologies;
- collecting HTTP status codes;
- identifying page titles;
- examining redirects;
- identifying TLS configuration;
- detecting virtual hosts;
- discovering default application behaviour;
- identifying unusual headers;
- identifying technologies that require more focused testing.

Related methodology:

[Technology Identification](../web/reconnaissance/technology-identification.md)

[Web Reconnaissance](../web/reconnaissance/index.md)

[Attack Surface Analysis](../web/attack-surface-analysis.md)

---

## WhatWeb

**WhatWeb** fingerprints technologies used by websites.

It can identify indicators associated with:

- web servers;
- frameworks;
- CMS platforms;
- JavaScript libraries;
- analytics platforms;
- application components;
- HTTP headers;
- cookies;
- page metadata;
- characteristic HTML content.

A basic authorised assessment might begin with:

```bash
whatweb https://example.test
```

More aggressive fingerprinting modes may perform additional requests and should only be used where permitted by the engagement rules.

The important workflow is:

```text
Target
  |
  v
WhatWeb
  |
  +-- Server indicators
  +-- Framework indicators
  +-- CMS indicators
  +-- Header indicators
  +-- JavaScript indicators
  |
  v
Candidate Technology
  |
  v
Manual Validation
```

A WhatWeb result should normally be treated as a **technology hypothesis** until corroborated.

For example, a response header, cookie name, HTML structure, JavaScript path, or default error page may provide additional evidence.

Planned detailed note:

```text
docs/tools/web-enumeration/whatweb.md
```

Official project:

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

---

## Wappalyzer

**Wappalyzer** identifies technologies associated with websites and web applications.

Depending on the interface being used, it may identify:

- CMS platforms;
- frameworks;
- JavaScript libraries;
- analytics products;
- CDN providers;
- web servers;
- e-commerce platforms;
- tag managers;
- development technologies;
- infrastructure components.

Wappalyzer is particularly useful during interactive browsing because technologies can be reviewed while navigating an application.

```text
Browser
   |
   v
Application
   |
   v
Wappalyzer
   |
   +-- Framework
   +-- Libraries
   +-- CMS
   +-- Infrastructure
   |
   v
Validate Indicators
```

Technology identification should not rely on Wappalyzer alone.

Combine results with:

- HTTP headers;
- cookies;
- HTML source;
- JavaScript bundles;
- asset paths;
- default responses;
- application behaviour;
- WhatWeb;
- httpx;
- manual inspection.

Planned detailed note:

```text
docs/tools/web-enumeration/wappalyzer.md
```

Official resource:

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

---

## httpx

ProjectDiscovery **httpx** is useful for probing HTTP services and enriching discovered assets.

It can collect information such as:

- HTTP status code;
- content length;
- content type;
- redirect location;
- page title;
- detected technologies;
- response hashes;
- favicon information;
- TLS information;
- IP address;
- ASN information;
- server information.

A common workflow is:

```text
Domains / Subdomains
        |
        v
      httpx
        |
        +-- Alive HTTP services
        +-- Status codes
        +-- Titles
        +-- Technologies
        +-- Redirects
        +-- TLS information
        |
        v
Prioritised Web Targets
```

This makes httpx particularly useful between asset discovery and deeper web testing.

Related methodology:

[Technology Identification](../web/reconnaissance/technology-identification.md)

[Subdomain Enumeration](../web/reconnaissance/subdomain-enumeration.md)

[Attack Surface Analysis](../web/attack-surface-analysis.md)

Planned detailed note:

```text
docs/tools/web-enumeration/httpx.md
```

Official documentation:

[ProjectDiscovery httpx](https://docs.projectdiscovery.io/opensource/httpx/overview){ target="_blank" rel="noopener noreferrer" }

[httpx Usage](https://docs.projectdiscovery.io/opensource/httpx/usage){ target="_blank" rel="noopener noreferrer" }

---

## Default Error Pages and Other Fingerprints

Technology fingerprinting is not limited to automated tools.

Useful indicators can include:

- default 404 pages;
- default 403 pages;
- framework exception pages;
- server error templates;
- cookie names;
- HTTP headers;
- favicon hashes;
- default login interfaces;
- static asset paths;
- JavaScript bundle names;
- API error formats;
- framework-specific response structures.

For example:

```text
Unknown Application
       |
       v
Request Non-Existing Resource
       |
       v
Observe 404 Response
       |
       +-- HTML structure
       +-- Error wording
       +-- Response headers
       +-- Cookies
       +-- Server behaviour
       |
       v
Candidate Technology
       |
       v
Confirm With Additional Evidence
```

A useful external reference for visually comparing common default 404 pages is:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

This should be used as a comparison reference rather than as proof that a particular technology is present.

---

# Web Application Testing

Enumeration identifies what may exist.

Web application testing determines how the application behaves and whether security controls can be bypassed or misused.

Related sections:

[Web Application Security](../web/index.md)

[Web Application Testing Methodology](../web/methodology.md)

[Web Application Pentesting Checklist](../web/checklist.md)

---

## Burp Suite

Burp Suite is one of the central tools used throughout web application security testing.

Its capabilities support activities such as:

- intercepting HTTP requests and responses;
- modifying requests;
- replaying requests;
- comparing responses;
- analysing parameters;
- encoding and decoding data;
- testing authentication;
- testing authorisation;
- examining sessions;
- testing APIs;
- testing WebSockets;
- testing GraphQL;
- analysing application behaviour;
- extending functionality through extensions.

```text
Browser
   |
   v
Burp Proxy
   |
   +--> HTTP History
   |
   +--> Repeater
   |
   +--> Intruder
   |
   +--> Comparer
   |
   +--> Decoder
   |
   +--> Extensions
```

### Community and Professional Editions

Both Burp Suite Community Edition and Professional can support manual testing.

Burp Suite Professional additionally provides functionality intended to support larger and more automated testing workflows, including Burp Scanner and other Professional-only capabilities.

The correct approach is not:

```text
Scanner finds issue
        |
        v
Report issue
```

It should be:

```text
Scanner / Manual Observation
            |
            v
Candidate Finding
            |
            v
Manual Reproduction
            |
            v
Impact Validation
            |
            v
Evidence
            |
            v
Finding
```

Planned detailed note:

```text
docs/tools/web-testing/burp-suite.md
```

Official documentation:

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

---

## ffuf

**ffuf** is commonly used for content, parameter, host, and input discovery.

Typical uses include:

- directory discovery;
- file discovery;
- extension discovery;
- virtual host discovery;
- parameter discovery;
- value fuzzing;
- API route discovery.

Its usefulness depends heavily on understanding the application's baseline response.

```text
Baseline
   |
   v
Candidate Requests
   |
   v
Filter Noise
   |
   +-- Status
   +-- Size
   +-- Words
   +-- Lines
   |
   v
Interesting Responses
   |
   v
Manual Validation
```

Automated discovery without baseline comparison often produces misleading results.

Planned detailed note:

```text
docs/tools/web-testing/ffuf.md
```

Official project:

[ffuf - GitHub](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }

---

## Nuclei

**Nuclei** is a template-driven scanner commonly used for repeatable security checks.

It can assist with:

- exposed services;
- known vulnerabilities;
- configuration issues;
- technology detection;
- exposed files;
- security misconfigurations;
- custom organisational checks.

The result of a Nuclei template should be considered a **candidate security observation** until validated.

```text
Nuclei Match
    |
    v
Inspect Template
    |
    v
Understand Matcher
    |
    v
Reproduce Manually
    |
    v
Validate Security Impact
```

Planned detailed note:

```text
docs/tools/web-testing/nuclei.md
```

Official documentation:

[ProjectDiscovery Nuclei](https://docs.projectdiscovery.io/opensource/nuclei/overview){ target="_blank" rel="noopener noreferrer" }

---

## sqlmap

**sqlmap** automates many aspects of SQL injection testing.

It may assist with:

- confirming suspected SQL injection;
- determining database behaviour;
- identifying DBMS characteristics;
- reproducing injection behaviour;
- evaluating injection techniques.

It should generally complement manual understanding rather than replace it.

```text
Suspicious Parameter
        |
        v
Manual Behaviour Analysis
        |
        v
sqlmap Validation
        |
        v
Manual Confirmation
        |
        v
Impact Assessment
```

Planned detailed note:

```text
docs/tools/web-testing/sqlmap.md
```

Official project:

[sqlmap](https://sqlmap.org/){ target="_blank" rel="noopener noreferrer" }

[sqlmap - GitHub](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }

---

## Katana

ProjectDiscovery **Katana** is a web crawler useful for discovering endpoints and application content.

It can assist with:

- crawling application paths;
- discovering linked endpoints;
- analysing JavaScript-referenced resources;
- collecting URLs;
- identifying additional application surface;
- feeding discovered URLs into other tooling.

```text
Target
  |
  v
Katana
  |
  +-- HTML links
  +-- Forms
  +-- Scripts
  +-- Endpoints
  |
  v
Normalised URL Set
  |
  v
Further Testing
```

Planned detailed note:

```text
docs/tools/web-testing/katana.md
```

Official documentation:

[ProjectDiscovery Katana](https://docs.projectdiscovery.io/opensource/katana/overview){ target="_blank" rel="noopener noreferrer" }

---

## Interactsh

**Interactsh** provides out-of-band interaction infrastructure.

It can be useful when the vulnerable behaviour occurs away from the direct HTTP response.

Typical authorised testing scenarios include validation of suspected:

- blind SSRF;
- blind XXE;
- asynchronous callbacks;
- DNS interactions;
- HTTP interactions;
- other out-of-band behaviour.

```text
Application
    |
    +--> Outbound Interaction
                |
                v
            Interactsh
                |
                v
       Correlated Evidence
```

An interaction should still be correlated to the exact request that caused it.

Planned detailed note:

```text
docs/tools/web-testing/interactsh.md
```

Official documentation:

[ProjectDiscovery Interactsh](https://docs.projectdiscovery.io/opensource/interactsh/overview){ target="_blank" rel="noopener noreferrer" }

---

# Active Directory Tools

Active Directory testing often requires combining information from several protocols and data sources.

The canonical methodology and technical notes remain in:

[Active Directory](../active-directory/index.md)

The Tools section should help readers understand **which tool is appropriate for which AD task** without duplicating the detailed Active Directory content.

```text
Active Directory
       |
       +-- Enumeration
       |      +-- NetExec
       |      +-- Impacket
       |
       +-- Relationship Analysis
       |      +-- BloodHound
       |
       +-- Certificate Services
       |      +-- Certipy
       |
       +-- Kerberos / Authentication
              +-- Impacket
              +-- specialised tooling
```

---

## NetExec

NetExec provides protocol-oriented functionality useful during authorised Windows and Active Directory assessments.

Typical uses include:

- SMB enumeration;
- LDAP enumeration;
- WinRM testing;
- authentication validation;
- host enumeration;
- share discovery;
- domain information collection;
- protocol-specific checks.

Where a detailed NetExec note already exists in the Active Directory section, that page should remain the canonical technical reference rather than duplicating the same material here.

[NetExec Active Directory Notes](../active-directory/netexec.md)

Official documentation:

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

**Impacket** is a collection of Python classes and scripts for working with network protocols commonly encountered in Windows and Active Directory environments.

Its tools cover areas such as:

- SMB;
- MSRPC;
- LDAP-related workflows;
- Kerberos;
- NTLM;
- authentication;
- remote service interaction;
- credential and ticket-related assessment workflows.

Impacket contains many independent utilities, so it is usually more useful to document them in the context of the technique they support rather than treat Impacket as one command.

Official project:

[Impacket - GitHub](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

BloodHound models Active Directory relationships as a graph.

Its value is not merely collecting objects but understanding relationships between:

- users;
- groups;
- computers;
- sessions;
- permissions;
- delegation;
- administration rights;
- trust relationships;
- potential attack paths.

```text
Directory Data
      |
      v
BloodHound Graph
      |
      +-- Nodes
      +-- Relationships
      +-- Permissions
      |
      v
Candidate Paths
      |
      v
Manual Validation
```

Related notes:

[BloodHound](../active-directory/bloodhound.md)

Official project:

[BloodHound](https://github.com/SpecterOps/BloodHound){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

Certipy assists with authorised assessment of Active Directory Certificate Services.

Its output may help identify:

- certificate authorities;
- certificate templates;
- enrolment configuration;
- security descriptors;
- potentially risky certificate-service configurations.

The result must be interpreted in the context of AD CS permissions and configuration.

Related section:

[Active Directory Certificate Services](../active-directory/ad-cs/index.md)

Official project:

[Certipy - GitHub](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

---

# Privilege Escalation Tools

Privilege escalation enumeration tools are particularly useful because Windows and Linux systems contain a large number of security-relevant configuration locations.

However:

> A highlighted line from an enumeration script is not automatically a privilege escalation vulnerability.

The correct model is:

```text
Enumeration Tool
      |
      v
Candidate Condition
      |
      v
Understand Configuration
      |
      v
Check Effective Permissions
      |
      v
Validate Reachability
      |
      v
Determine Security Impact
```

Related sections:

[Privilege Escalation Explorer](../privesc/index.md)

[Windows Privilege Escalation](../windows/privilege-escalation.md)

[Linux Privilege Escalation](../linux/privilege-escalation.md)

---

## WinPEAS

**WinPEAS** is part of the PEASS-ng project and performs extensive Windows privilege escalation enumeration.

It can inspect areas such as:

- system information;
- users and groups;
- services;
- scheduled tasks;
- file permissions;
- registry permissions;
- credentials;
- environment configuration;
- installed applications;
- networking;
- security products;
- potentially interesting files.

Use WinPEAS as an enumeration accelerator.

Do not assume that coloured or highlighted output confirms exploitability.

```text
WinPEAS Output
     |
     v
Interesting Condition
     |
     v
Manual Permission Check
     |
     v
Understand Execution Context
     |
     v
Validate Impact
```

Planned detailed note:

```text
docs/tools/privilege-escalation/winpeas.md
```

Official project:

[PEASS-ng - GitHub](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

---

## LinPEAS

**LinPEAS** performs broad Linux privilege escalation enumeration.

It can assist with identifying:

- sudo configuration;
- SUID and SGID binaries;
- Linux capabilities;
- cron jobs;
- writable locations;
- credentials;
- containers;
- services;
- processes;
- environment configuration;
- interesting files.

Related notes:

[Linux Privilege Escalation](../linux/privilege-escalation.md)

[Linux sudo](../linux/sudo.md)

[Linux SUID and SGID](../linux/suid-sgid.md)

[Linux Capabilities](../linux/capabilities.md)

[Linux Scheduled Jobs](../linux/scheduled-jobs.md)

Planned detailed note:

```text
docs/tools/privilege-escalation/linpeas.md
```

Official project:

[PEASS-ng - GitHub](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

---

## PowerUp

**PowerUp** is a PowerShell-based collection of Windows privilege escalation checks associated with PowerSploit.

It can help assess Windows configuration areas related to potential privilege escalation opportunities.

The important distinction is between:

```text
Check reports condition
        |
        v
Condition is technically present
        |
        v
Current user can influence it
        |
        v
Privileged execution path exists
        |
        v
Security impact is demonstrated
```

Planned detailed note:

```text
docs/tools/privilege-escalation/powerup.md
```

Project reference:

[PowerUp - PowerSploit](https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc){ target="_blank" rel="noopener noreferrer" }

---

## PrivescCheck

**PrivescCheck** is a PowerShell-based Windows privilege escalation enumeration tool.

It performs a broad set of checks intended to identify security-relevant configurations that warrant further analysis.

Use its findings as investigation leads rather than automatic conclusions.

Planned detailed note:

```text
docs/tools/privilege-escalation/privesccheck.md
```

Official project:

[PrivescCheck - GitHub](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

---

## linux-smart-enumeration

**linux-smart-enumeration**, commonly referred to as LSE, provides Linux enumeration aimed at identifying information relevant to privilege escalation.

It is useful as an additional perspective alongside:

- manual enumeration;
- LinPEAS;
- system-specific investigation.

Planned detailed note:

```text
docs/tools/privilege-escalation/linux-smart-enumeration.md
```

Official project:

[linux-smart-enumeration - GitHub](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

---

# Source Code Review Tools

Source code review tools can accelerate discovery, but the objective remains understanding how data and trust move through the application.

```text
Source
  |
  v
Transformation
  |
  v
Validation
  |
  v
Security-Sensitive Sink
```

Related methodology:

[Source Code Review](../source-code-review/index.md)

[Source Code Review Methodology](../source-code-review/methodology.md)

[Source-to-Sink Analysis](../source-code-review/source-to-sink-analysis.md)

The detailed tool pages already belong to the Source Code Review section and should remain canonical there.

---

## ripgrep

ripgrep is extremely useful during manual source review for quickly locating:

- routes;
- dangerous functions;
- authentication logic;
- authorisation checks;
- configuration;
- secrets;
- database queries;
- file operations;
- process execution;
- deserialisation;
- cryptographic operations;
- security-sensitive APIs.

[Security Source Review with ripgrep](../source-code-review/static-analysis/ripgrep.md)

---

## Semgrep

Semgrep combines pattern matching with language-aware analysis and is useful for finding security-relevant code patterns across large codebases.

[Semgrep for Security Source Code Review](../source-code-review/static-analysis/semgrep.md)

Official documentation:

[Semgrep Documentation](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

---

## OpenGrep

OpenGrep provides static-analysis capabilities that can be incorporated into security source review workflows.

[OpenGrep for Security Source Code Review](../source-code-review/static-analysis/opengrep.md)

Official resource:

[OpenGrep](https://opengrep.dev/){ target="_blank" rel="noopener noreferrer" }

---

## CodeQL

CodeQL treats source code as data that can be queried.

It is particularly useful for deeper semantic analysis and variant analysis across larger codebases.

[CodeQL for Security Source Code Review](../source-code-review/static-analysis/codeql.md)

Official documentation:

[GitHub CodeQL Documentation](https://docs.github.com/en/code-security/code-scanning/managing-your-code-scanning-configuration/about-code-scanning-with-codeql){ target="_blank" rel="noopener noreferrer" }

---

# Red Teaming Tools

Red team tooling should be connected to an objective, control hypothesis, and engagement scenario.

Related section:

[Red Teaming](../red-teaming/index.md)

A red team operation may involve tooling for:

- command and control;
- infrastructure;
- payload delivery;
- identity operations;
- lateral movement;
- situational awareness;
- collection;
- detection testing;
- operational logging.

The tool should never become the methodology.

```text
Objective
   |
   v
Technique
   |
   v
Tool Selection
   |
   v
Controlled Execution
   |
   v
Evidence
   |
   v
Blue-Team Observation
```

---

## Command-and-Control Frameworks

Command-and-control platforms provide infrastructure for managing controlled red team agents and interactions during authorised exercises.

Different frameworks vary in:

- architecture;
- supported operating systems;
- communication protocols;
- extensibility;
- operator workflow;
- payload formats;
- team collaboration;
- logging;
- infrastructure requirements;
- defensive visibility.

Rather than declaring one framework universally best, the detailed C2 page should compare frameworks according to the engagement requirements.

Potential frameworks covered in that comparison may include:

- Sliver;
- Mythic;
- Havoc;
- other actively maintained and relevant frameworks.

Planned detailed note:

```text
docs/tools/red-teaming/c2-frameworks.md
```

---

# Vulnerability Research Tools

Vulnerability research requires a different toolset from normal application penetration testing.

Related section:

[Vulnerability Research](../vulnerability-research/index.md)

[Debugging and Dynamic Analysis](../vulnerability-research/debugging-dynamic-analysis.md)

[Fuzzing](../vulnerability-research/fuzzing.md)

[Crash Analysis](../vulnerability-research/crash-analysis.md)

[Patch Diffing](../vulnerability-research/patch-diffing.md)

[Variant Analysis](../vulnerability-research/variant-analysis.md)

Typical tool categories include:

| Activity | Example Tools |
|---|---|
| Linux debugging | GDB |
| GDB enhancements | GEF, pwndbg |
| Windows debugging | WinDbg |
| Windows user-mode debugging | x64dbg |
| Coverage-guided fuzzing | AFL++ |
| Compiler-integrated fuzzing | libFuzzer |
| Disassembly / reverse engineering | Ghidra |
| Binary inspection | objdump, readelf |
| Windows binary inspection | dumpbin and debugger tooling |
| Patch analysis | diffing and reverse-engineering tools |

The objective is to connect each tool to the research process:

```text
Input / Trigger
      |
      v
Program Behaviour
      |
      v
Crash / Unexpected State
      |
      v
Debugger
      |
      v
Root Cause
      |
      v
Variant Analysis
      |
      v
Proof of Concept
```

Detailed vulnerability-research tool coverage should be added only where it improves the existing methodology rather than duplicating it.

---

# Network and Protocol Analysis

Some tools cross multiple security disciplines.

These include:

- Nmap;
- Wireshark;
- TShark;
- tcpdump;
- curl;
- Netcat;
- OpenSSL;
- protocol-specific clients.

They are useful because many security findings ultimately depend on understanding how systems communicate.

---

## Nmap

Nmap supports host and service discovery, port scanning, service identification, and protocol-oriented investigation.

A typical workflow is:

```text
Target Scope
    |
    v
Host Discovery
    |
    v
Port Discovery
    |
    v
Service Identification
    |
    v
Manual Protocol Validation
```

Scanner output is not automatically proof of vulnerability.

Version detection in particular should be treated carefully because:

- banners may be modified;
- vendors may backport security fixes;
- proxies may obscure backend services;
- protocol behaviour may differ from the reported banner;
- network controls may alter responses.

Official documentation:

[Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }

---

## Wireshark and TShark

Wireshark and TShark support packet-level protocol analysis.

They can help answer questions such as:

- Which hosts communicated?
- Which protocol was used?
- Was DNS resolution performed?
- Was TCP connectivity established?
- Did TLS negotiation complete?
- Which HTTP requests were transmitted?
- Was a connection reset?
- Was traffic retransmitted?
- Did an application send unexpected network traffic?

```text
Capture
   |
   v
Filter
   |
   v
Protocol Analysis
   |
   v
Conversation / Stream
   |
   v
Interpretation
```

Official documentation:

[Wireshark Documentation](https://www.wireshark.org/docs/){ target="_blank" rel="noopener noreferrer" }

---

# AI-Assisted Security Workflows

Large language models can assist security professionals with analysis and knowledge work, but LLM output should not be treated as verified security evidence.

Useful applications may include:

- understanding unfamiliar source code;
- explaining APIs;
- identifying candidate sources and sinks;
- generating search patterns;
- reviewing tool output;
- comparing configurations;
- explaining protocol behaviour;
- assisting with log analysis;
- generating test cases;
- summarising large bodies of technical information;
- supporting variant-analysis hypotheses;
- helping structure reports and remediation guidance.

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
Independent Technical Validation
        |
        v
Evidence
        |
        v
Conclusion
```

Not:

```text
LLM says vulnerable
        |
        v
Report vulnerability
```

Important considerations include:

- hallucinations;
- incomplete context;
- outdated technical knowledge;
- incorrect assumptions;
- confidentiality;
- source-code sensitivity;
- credential and secret handling;
- organisational policy;
- data retention;
- reproducibility;
- independent validation.

Planned detailed note:

```text
docs/tools/ai/llm-assisted-security-testing.md
```

---

# Tool Output Is Not a Finding

One of the most important principles throughout this knowledge base is:

> A tool finding is not automatically a security finding.

For example:

```text
Scanner reports:
"Potential SQL injection"

This means:

Candidate behaviour requires validation.

It does NOT yet mean:

Confirmed exploitable SQL injection.
```

Similarly:

```text
WinPEAS highlights service
        !=
Confirmed privilege escalation

Nuclei template matches
        !=
Confirmed vulnerability

BloodHound displays path
        !=
Path is currently exploitable

Wappalyzer detects framework
        !=
Framework identification is certain

Semgrep finds pattern
        !=
Code is definitely vulnerable
```

Tool output is evidence that contributes to a conclusion.

---

# Evidence Strength

Tool observations can be considered at different confidence levels.

| Level | Meaning |
|---|---|
| Observation | Something interesting was seen |
| Indicator | Evidence suggests a particular condition |
| Candidate | A potential security issue warrants investigation |
| Validated | The technical behaviour has been reproduced |
| Confirmed | Sufficient evidence demonstrates the security condition and impact |

For example:

```text
WhatWeb says "nginx"
        |
        v
Indicator

Server header says "nginx"
        |
        v
Additional Indicator

Behaviour matches nginx
        |
        v
Higher Confidence
```

Another example:

```text
Nuclei template matches
        |
        v
Candidate

Manual request reproduces behaviour
        |
        v
Validated

Impact demonstrated
        |
        v
Confirmed Finding
```

---

# Correlating Tools

Confidence generally increases when independent observations agree.

```text
WhatWeb --------+
                |
Wappalyzer -----+----> Candidate Framework
                |
httpx ----------+
                |
Manual Review --+
                |
                v
          Higher Confidence
```

The same principle applies elsewhere.

```text
WinPEAS --------+
                |
PowerUp --------+
                |
Manual ACL -----+----> Privilege Escalation Condition
                |
Service Config -+
```

And source review:

```text
ripgrep --------+
                |
Semgrep --------+
                |
CodeQL ---------+----> Candidate Data Flow
                |
Manual Review --+
```

Tool correlation should increase understanding, not merely increase the number of scanner findings.

---

# Tool Chaining

Security tools are often most useful when used as components of a workflow.

For example:

```text
Subfinder
    |
    v
httpx
    |
    v
Katana
    |
    v
Interesting URLs
    |
    +--> Burp Suite
    |
    +--> Nuclei
    |
    +--> Manual Testing
```

Another example:

```text
Source Repository
      |
      +--> ripgrep
      |
      +--> Semgrep
      |
      +--> CodeQL
      |
      v
Candidate Code Paths
      |
      v
Manual Source-to-Sink Review
```

And privilege escalation:

```text
System Access
    |
    +--> WinPEAS / LinPEAS
    |
    +--> Manual Enumeration
    |
    v
Candidate Conditions
    |
    v
Focused Validation
```

Tool chaining should remain within the defined assessment scope.

---

# Choosing Between Automated and Manual Testing

Automation is useful when:

- there are many assets;
- checks are repetitive;
- results can be filtered;
- a technique can be safely repeated;
- consistent output is useful;
- coverage would otherwise be impractical.

Manual analysis is particularly important when:

- business logic is involved;
- user roles matter;
- authentication state matters;
- context changes the interpretation;
- several systems interact;
- automated output is ambiguous;
- the security impact depends on application-specific behaviour.

Most strong assessments combine both.

```text
Automation
    |
    +--> Breadth
    |
    +--> Repeatability

Manual Testing
    |
    +--> Context
    |
    +--> Depth

Together
    |
    v
Better Assessment
```

---

# Safe Defaults

Before running security tooling, consider:

### Scope

Confirm:

- target domains;
- IP ranges;
- applications;
- APIs;
- cloud resources;
- accounts;
- environments;
- exclusions.

### Rate

Understand whether the tool:

- sends requests concurrently;
- performs recursion;
- retries automatically;
- follows redirects;
- brute-forces content;
- enumerates large wordlists;
- creates significant network load.

### Authentication

Avoid accidentally:

- locking accounts;
- invalidating sessions;
- changing passwords;
- triggering MFA repeatedly;
- exhausting API quotas;
- testing unintended identities.

### State Changes

Determine whether the tool may:

- upload files;
- create users;
- change configuration;
- execute code;
- create scheduled tasks;
- modify services;
- write database content;
- trigger workflows.

### Third Parties

Do not assume that a third-party service referenced by the target is automatically in scope.

---

# Reproducibility

Useful tool notes should make results reproducible.

Record where appropriate:

```text
Tool:
Tool version:
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

For example:

```bash
whatweb --version
```

```bash
nmap --version
```

```bash
nuclei -version
```

```bash
httpx -version
```

Version information matters because:

- flags change;
- templates change;
- detection logic changes;
- APIs change;
- output formats change;
- default behaviour changes.

---

# Evidence Collection

Useful evidence may include:

- the exact command;
- relevant tool version;
- request and response;
- selected terminal output;
- packet capture;
- screenshot;
- affected asset;
- timestamp;
- authentication context;
- manual reproduction;
- relevant configuration;
- explanation of security impact.

Avoid attaching massive raw scanner output to a report without interpretation.

Extract the evidence that supports the conclusion.

---

# False Positives

False positives can result from:

- generic response matching;
- wildcard DNS;
- custom error pages;
- catch-all routing;
- reverse proxies;
- WAF behaviour;
- authentication redirects;
- CDN responses;
- shared infrastructure;
- stale signatures;
- version backporting;
- scanner assumptions;
- misleading banners.

A useful validation workflow is:

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
Compare Responses
    |
    v
Determine Whether Condition Is Real
```

---

# False Negatives

Tools can also fail to identify real security issues.

Causes include:

- authentication requirements;
- unusual application flows;
- custom protocols;
- JavaScript-heavy applications;
- WAF interference;
- inaccessible routes;
- missing scanner signatures;
- business logic;
- multi-step vulnerabilities;
- state-dependent behaviour;
- environment-specific conditions.

A clean scanner result does not prove that the target is secure.

---

# Reporting Tool-Assisted Findings

Avoid report statements such as:

```text
Nuclei found a vulnerability.
```

Prefer:

```text
Automated testing identified behaviour consistent with the suspected
condition. The behaviour was subsequently reproduced manually and the
affected request, response, and security impact were validated.
```

Similarly, avoid:

```text
WinPEAS reported a privilege escalation vulnerability.
```

Prefer:

```text
Enumeration identified a potentially security-relevant configuration.
Manual validation confirmed that the current user could modify the
affected resource and that the resource participated in a privileged
execution path.
```

The finding should describe the **security condition**, not the name of the tool.

---

# Tool Documentation Model

Detailed tool pages in this knowledge base should generally follow this model:

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
Representative Output
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
Evidence Collection
   |
   v
Related Security Topics
   |
   v
Official and External References
```

This keeps tool documentation connected to security methodology rather than turning it into a command dump.

---

# External References

External resources are used when they provide strong specialist material that does not need to be duplicated locally.

Priority is generally given to:

1. official project documentation;
2. official project repositories;
3. vendor documentation;
4. PortSwigger Web Security Academy for web security;
5. Microsoft Learn for Windows and Active Directory;
6. ProjectDiscovery documentation for ProjectDiscovery tools;
7. specialist practical references such as 0xdf;
8. HackTricks where broader offensive-security context is useful.

Examples:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

[ProjectDiscovery Documentation](https://docs.projectdiscovery.io/){ target="_blank" rel="noopener noreferrer" }

[Microsoft Learn](https://learn.microsoft.com/){ target="_blank" rel="noopener noreferrer" }

[HackTricks](https://book.hacktricks.wiki/){ target="_blank" rel="noopener noreferrer" }

External references complement these notes; they do not replace validation of the target environment.

---

# Related Knowledge Base Sections

The Tools section connects directly to the main security disciplines documented on this site.

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

# Final Testing Model

Use tools to improve visibility, consistency, and coverage.

Do not allow the tool to become the conclusion.

```text
Question
   |
   v
Methodology
   |
   v
Tool
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
Corroborating Evidence
   |
   v
Conclusion
   |
   v
Remediation
   |
   v
Retest
```

The most valuable skill is not knowing the largest number of security tools.

It is knowing:

- what question to ask;
- which tool can help answer it;
- what the output actually means;
- when the output may be wrong;
- how to validate it;
- how it connects to the underlying security concept;
- and when enough evidence exists to support a defensible conclusion.
