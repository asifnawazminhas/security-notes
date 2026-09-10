<div class="security-hero" markdown>

![Asif's Security Notes](assets/security-notes-banner.png)

<div class="hero-intro" markdown>

# Security Knowledge Base

Practical notes for **offensive security**, **penetration testing**, **red teaming**, **purple teaming**, **vulnerability research**, **source code review**, **Active Directory**, **Windows** and **Linux**.

<span class="security-badge">OFFENSIVE SECURITY</span>
<span class="security-badge">SECURITY RESEARCH</span>
<span class="security-badge">RED TEAMING</span>
<span class="security-badge">PURPLE TEAMING</span>

</div>

</div>

!!! warning "Authorised Security Testing"

    The material in these notes is intended for educational purposes, security research and authorised security testing only.


## Start Here

Use the knowledge base to study a security topic in depth or jump directly into practical references during an authorised assessment, lab or research project.

<div class="grid cards" markdown>

-   :material-book-open-page-variant:{ .lg .middle } **Learn a Topic**

    ---

    Study security concepts, methodology, testing approaches, impact, detection, remediation and retesting.

    [:octicons-arrow-right-24: Explore the Knowledge Base](#explore-the-knowledge-base)

-   :material-tools:{ .lg .middle } **Need a Security Tool?**

    ---

    Practical tooling workflows for web enumeration, application testing, privilege escalation, red teaming, vulnerability research and AI-assisted security testing.

    [:octicons-arrow-right-24: Open Tools](tools/index.md)

-   :material-file-document-multiple-outline:{ .lg .middle } **Testing Right Now?**

    ---

    Use practical cheatsheets for commands, workflows, expected results, interpretation and next steps.

    [:octicons-arrow-right-24: Open Cheatsheets](cheatsheets/index.md)

-   :material-shield-key:{ .lg .middle } **Found a PrivEsc Candidate?**

    ---

    Investigate Windows and Linux privilege escalation candidates including services, permissions, scheduled execution, SUID binaries, capabilities and credentials.

    [:octicons-arrow-right-24: Open PrivEsc Explorer](privesc/index.md)

-   :material-sword-cross:{ .lg .middle } **Running a Red Team Assessment?**

    ---

    Follow the red team lifecycle from infrastructure and reconnaissance through execution, lateral movement, C2, detection validation, cleanup and reporting.

    [:octicons-arrow-right-24: Red Teaming](red-teaming/index.md)

-   :material-shield-half-full:{ .lg .middle } **Validating Detection?**

    ---

    Connect offensive techniques with detection engineering, knowledge transfer, measurement and continuous security improvement.

    [:octicons-arrow-right-24: Purple Teaming](purple-teaming/index.md)

</div>


## Explore the Knowledge Base

<div class="grid cards" markdown>

-   :material-web:{ .lg .middle } **Web Application Security**

    ---

    Reconnaissance, authentication, authorisation, injection, server-side attacks, APIs, HTTP security, browser security and application logic.

    [:octicons-arrow-right-24: Web Security Notes](web/index.md)

-   :material-code-braces:{ .lg .middle } **Source Code Review**

    ---

    Routes and entry points, source-to-sink analysis, authentication, authorisation, secrets, variant analysis and static analysis.

    [:octicons-arrow-right-24: Source Code Review](source-code-review/index.md)

-   :material-microsoft-windows:{ .lg .middle } **Active Directory**

    ---

    Enumeration, Kerberos, NTLM, AD CS, delegation, credential access, attack paths, privilege escalation and lateral movement.

    [:octicons-arrow-right-24: Active Directory Notes](active-directory/index.md)

-   :material-microsoft-windows-classic:{ .lg .middle } **Windows**

    ---

    Windows enumeration, PowerShell, services, scheduled tasks, credentials, permissions, security controls and privilege escalation.

    [:octicons-arrow-right-24: Windows Notes](windows/index.md)

-   :material-linux:{ .lg .middle } **Linux**

    ---

    Linux enumeration, services, scheduled jobs, filesystem permissions, sudo, SUID/SGID, capabilities, credentials and privilege escalation.

    [:octicons-arrow-right-24: Linux Notes](linux/index.md)

-   :material-shield-key:{ .lg .middle } **PrivEsc Explorer**

    ---

    Interactive Windows and Linux privilege escalation reference for investigating discovered services, permissions, capabilities, scheduled execution and other candidates.

    [:octicons-arrow-right-24: PrivEsc Explorer](privesc/index.md)

-   :material-console:{ .lg .middle } **Red Teaming**

    ---

    Infrastructure, OPSEC, reconnaissance, initial access, execution, discovery, credential access, lateral movement, persistence, C2, exfiltration and reporting.

    [:octicons-arrow-right-24: Red Team Notes](red-teaming/index.md)

-   :material-shield-half-full:{ .lg .middle } **Purple Teaming**

    ---

    Exercises, MITRE ATT&CK, detection engineering, knowledge transfer, measurement, after-action review and continuous validation.

    [:octicons-arrow-right-24: Purple Team Notes](purple-teaming/index.md)

-   :material-shield-search:{ .lg .middle } **Vulnerability Research**

    ---

    Attack-surface analysis, debugging, fuzzing, crash analysis, patch diffing, variant analysis, PoC development, CVE research and responsible disclosure.

    [:octicons-arrow-right-24: Vulnerability Research](vulnerability-research/index.md)

-   :material-tools:{ .lg .middle } **Tools**

    ---

    Practical workflows for web enumeration, web testing, privilege escalation, Active Directory, red teaming, vulnerability research and AI-assisted security testing.

    [:octicons-arrow-right-24: Security Tools](tools/index.md)

-   :material-file-document-multiple-outline:{ .lg .middle } **Cheatsheets**

    ---

    Fast practical references for commands, tools, workflows, prerequisites, representative output, interpretation and next steps.

    [:octicons-arrow-right-24: Cheatsheets](cheatsheets/index.md)

</div>


## Practical Reference Layer

The knowledge base is designed around several complementary layers.

```text
Need to understand a security topic?
        |
        v
Detailed Security Notes


Need a practical tool workflow?
        |
        v
Tools


Testing something right now?
        |
        v
Cheatsheets


Found a privilege escalation candidate?
        |
        v
PrivEsc Explorer


Need a complete offensive workflow?
        |
        v
Red Teaming


Need to validate detection and learning?
        |
        v
Purple Teaming
```

The detailed notes explain the security concept.

The Tools section explains how individual tools fit into practical assessment workflows.

The Cheatsheets provide fast command and procedure references.

The PrivEsc Explorer helps convert enumeration results into structured privilege escalation validation paths.


## Practical Cheatsheets

The cheatsheets are the fast-reference layer of the knowledge base.

They are designed for situations where you already understand the underlying topic and need to quickly answer:

```text
What should I check?

Which command should I use?

What prerequisites are required?

What should the result look like?

What does the result mean?

What should I verify next?
```

<div class="grid cards" markdown>

-   :material-linux:{ .lg .middle } **Linux**

    ---

    Enumeration, users, permissions, services, networking, credentials and privilege escalation.

    [:octicons-arrow-right-24: Linux Cheatsheet](cheatsheets/linux.md)

-   :material-microsoft-windows-classic:{ .lg .middle } **Windows**

    ---

    Enumeration, users, groups, services, processes, permissions, security controls and privilege escalation.

    [:octicons-arrow-right-24: Windows Cheatsheet](cheatsheets/windows.md)

-   :material-powershell:{ .lg .middle } **PowerShell**

    ---

    PowerShell commands for Windows enumeration, files, processes, services, networking, permissions and security assessment workflows.

    [:octicons-arrow-right-24: PowerShell Cheatsheet](cheatsheets/powershell.md)

-   :material-web:{ .lg .middle } **Web Application Security**

    ---

    Practical web testing workflows covering authentication, authorisation, injection, server-side vulnerabilities, APIs and HTTP security.

    [:octicons-arrow-right-24: Web Cheatsheet](cheatsheets/web.md)

-   :material-network:{ .lg .middle } **Networking**

    ---

    Network discovery, DNS, ports, connectivity, routing and traffic-analysis references.

    [:octicons-arrow-right-24: Networking Cheatsheet](cheatsheets/networking.md)

-   :material-microsoft-windows:{ .lg .middle } **Active Directory**

    ---

    Enumeration, authentication, Kerberos, NTLM, AD CS, delegation, credential access and attack-path workflows.

    [:octicons-arrow-right-24: Active Directory Cheatsheet](cheatsheets/active-directory.md)

-   :material-lan:{ .lg .middle } **NetExec**

    ---

    Authentication, SMB, hosts, shares, users, groups and Active Directory assessment workflows.

    [:octicons-arrow-right-24: NetExec Cheatsheet](cheatsheets/netexec.md)

-   :material-console-line:{ .lg .middle } **Impacket**

    ---

    SMB, Kerberos, authentication, remote administration and Active Directory tooling.

    [:octicons-arrow-right-24: Impacket Cheatsheet](cheatsheets/impacket.md)

-   :material-graph-outline:{ .lg .middle } **BloodHound**

    ---

    Collection, data import, analysis, attack paths, Cypher queries and interpretation.

    [:octicons-arrow-right-24: BloodHound Cheatsheet](cheatsheets/bloodhound.md)

</div>

[:octicons-arrow-right-24: Browse All Cheatsheets](cheatsheets/index.md)


## How to Use These Notes

### Detailed Security Notes

Use the main topic sections when you want to understand:

- how a vulnerability or technique works;
- where it applies;
- required conditions;
- security impact;
- testing methodology;
- defensive considerations;
- remediation;
- retesting;
- related techniques.

The objective is to understand the underlying security behaviour rather than memorise individual commands.


### Tools

Use the [Tools](tools/index.md) section when you know which type of activity you need to perform and want a practical tool workflow.

Examples include:

```text
Technology identification
        |
        v
WhatWeb / Wappalyzer / httpx


Web application testing
        |
        v
Burp Suite / ffuf / Katana / Nuclei / sqlmap / Interactsh


Windows privilege escalation enumeration
        |
        v
WinPEAS / PowerUp / PrivescCheck


Linux privilege escalation enumeration
        |
        v
LinPEAS / linux-smart-enumeration


Red team operations
        |
        v
C2 framework selection and operational planning


Vulnerability research
        |
        v
Debugging / reverse engineering / fuzzing / tracing
```

A tool result is not automatically a vulnerability.

The result should feed back into the underlying methodology and security concept.


### Cheatsheets

Use the [Cheatsheets](cheatsheets/index.md) when you need a fast practical reference during testing.

The general model is:

```text
Prerequisites
     |
     v
Command / Procedure
     |
     v
Representative Result
     |
     v
Interpretation
     |
     v
Next Step
```

The objective is not simply to provide commands.

The practical references should explain what the result means and what should be verified next.


### PrivEsc Explorer

Use the [PrivEsc Explorer](privesc/index.md) after enumeration identifies something potentially interesting.

For example:

```text
Writable Service
        |
        v
Windows PrivEsc Explorer


Scheduled Task
        |
        v
Windows PrivEsc Explorer


SUID Binary
        |
        v
Linux PrivEsc Explorer


Linux Capability
        |
        v
Linux PrivEsc Explorer
```

The explorer helps turn enumeration findings into structured validation paths.


## Core Security Areas

The different sections are designed to connect rather than operate as isolated collections of notes.

```text
                         SECURITY TESTING
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
       Web                Infrastructure          Source Code
        |                      |                      |
        v                      v                      v
 Applications           Windows / Linux       Static + Manual Review
        |                      |                      |
        |                      v                      |
        |               Active Directory             |
        |                      |                      |
        +-----------+----------+----------------------+
                    |
                    v
               Red Teaming
                    |
          +---------+---------+
          |                   |
          v                   v
    Purple Teaming      Vulnerability Research
          |                   |
          +---------+---------+
                    |
                    v
          Security Improvement
```


## Assessment Philosophy

The notes follow a practical validation model:

```text
Enumerate
    |
    v
Identify Candidate
    |
    v
Understand Context
    |
    v
Validate Safely
    |
    v
Interpret Evidence
    |
    v
Determine Impact
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

A discovered configuration, permission, endpoint, service, tool result or security-control behaviour should not automatically be treated as a confirmed vulnerability.

The surrounding context and evidence determine what the observation actually proves.


## Evidence Before Conclusions

A recurring principle throughout the knowledge base is to distinguish between:

```text
Candidate
   |
   v
Potentially interesting observation


Likely
   |
   v
Multiple required conditions appear to exist


Confirmed
   |
   v
Controlled validation demonstrates the security impact
```

This distinction is particularly important when assessing:

- authentication;
- authorisation;
- permissions;
- privilege escalation;
- credential access;
- network exposure;
- application behaviour;
- security controls;
- attack paths;
- scanner findings.


## From Tool Output to Finding

Security tools produce observations.

The assessment process determines whether those observations represent a vulnerability.

```text
Tool Output
     |
     v
Observation
     |
     v
Context
     |
     v
Hypothesis
     |
     v
Controlled Validation
     |
     v
Evidence
     |
     v
Security Conclusion
```

For example:

```text
WinPEAS reports writable directory
              |
              v
Check exact ACL
              |
              v
Determine execution context
              |
              v
Identify privileged dependency
              |
              v
Validate controlled impact
```

or:

```text
Nuclei reports CVE candidate
              |
              v
Read template
              |
              v
Verify product/version
              |
              v
Reproduce manually
              |
              v
Confirm or reject
```

This is the difference between collecting tool output and performing security testing.


## Offensive and Defensive Perspective

The notes connect offensive testing with defensive understanding.

```text
Offensive Technique
        |
        v
System Behaviour
        |
        v
Telemetry
        |
        v
Detection
        |
        v
Response
        |
        v
Remediation
        |
        v
Retest
```

This is especially important for red teaming and purple teaming, where successful technique execution is only one part of the assessment.

The broader objective is measurable security improvement.


## Vulnerability Research Perspective

Vulnerability research follows a similar evidence-driven process:

```text
Attack Surface
      |
      v
Interesting Component
      |
      v
Static / Dynamic Analysis
      |
      v
Security Hypothesis
      |
      v
Controlled Testing / Fuzzing
      |
      v
Reproducible Condition
      |
      v
Root Cause
      |
      v
Supported Impact
      |
      v
Variant Analysis
      |
      v
PoC
      |
      v
Responsible Disclosure
```

Related section:

[Vulnerability Research](vulnerability-research/index.md)


## Source Code Review Perspective

Source code review helps connect externally visible behaviour to implementation.

```text
Entry Point
    |
    v
User-Controlled Data
    |
    v
Validation / Transformation
    |
    v
Sensitive Sink
    |
    v
Security Decision
```

Static analysis tools help identify candidates.

Manual source-to-sink analysis determines whether the path is meaningful.

Related section:

[Source Code Review](source-code-review/index.md)


## About This Knowledge Base

This knowledge base documents practical techniques, methodology, tooling and research across offensive and defensive cybersecurity.

It is intended to support several complementary activities:

```text
Study
  |
  v
Understand security concepts


Reference
  |
  v
Find commands, tools and procedures


Assess
  |
  v
Support authorised security testing


Research
  |
  v
Investigate vulnerabilities and software behaviour


Interpret
  |
  v
Understand what evidence actually proves


Improve
  |
  v
Connect offensive findings with defensive improvements


Document
  |
  v
Preserve reusable security knowledge
```

The detailed notes provide background, methodology and interpretation.

The Tools section connects security tooling to practical workflows.

The Cheatsheets provide fast operational references.

The PrivEsc Explorer helps investigate privilege escalation candidates.

The Red Teaming section connects individual techniques into complete offensive workflows.

The Purple Teaming section connects offensive activity with detection, learning, measurement and continuous improvement.

The Vulnerability Research section focuses on identifying, understanding, validating and responsibly documenting software vulnerabilities.


<div class="terminal">
Research. Learn. Test. Understand. Improve. Share.
</div>


!!! info "Living Knowledge Base"

    These notes are continuously expanded as new techniques, research, tooling and defensive approaches are explored.


!!! tip "Need a practical tool?"

    Start with the [Tools](tools/index.md) section for practical workflows involving web enumeration, web testing, privilege escalation, red teaming, vulnerability research and AI-assisted security testing.


!!! tip "Looking for commands?"

    Start with the [Cheatsheets](cheatsheets/index.md) for quick access to practical commands, workflows, expected results and interpretation.


!!! tip "Found a privilege escalation candidate?"

    Use the [PrivEsc Explorer](privesc/index.md) to investigate Windows and Linux privilege escalation opportunities and determine what additional validation is required.
