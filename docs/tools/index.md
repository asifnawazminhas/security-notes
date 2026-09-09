---
title: Security Tools
description: Practical reference for cybersecurity, penetration testing, red teaming and security assessment tools, including tool selection, workflows, evidence collection, validation and responsible usage.
---

# Security Tools

Security tools help automate, accelerate and standardise security assessment activities.

They can assist with:

```text
Reconnaissance

Enumeration

Service Discovery

Web Application Testing

Vulnerability Discovery

Validation

Traffic Analysis

Exploitation in Authorised Environments

Post-Exploitation Assessment

Detection Validation

Evidence Collection

Reporting
```

However, tools should support the methodology rather than replace it.

A useful security workflow is:

```text
Objective
   |
   v
Understand Target
   |
   v
Choose Technique
   |
   v
Select Tool
   |
   v
Configure Tool
   |
   v
Execute
   |
   v
Review Raw Result
   |
   v
Validate
   |
   v
Correlate Evidence
   |
   v
Security Conclusion
   |
   v
Report
```

The most important question is not:

```text
Which tool should I run?
```

It is:

```text
What security question am I trying to answer?
```

---

# 1. Tools in Security Testing

Security tools can perform many different functions.

A simplified model is:

```text
                    SECURITY ASSESSMENT
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
 Reconnaissance       Enumeration        Validation
        |                  |                  |
        v                  v                  v
Attack Surface        Services          Manual Testing
Discovery             Applications      Exploit Validation
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                        Evidence
                           |
                           v
                        Analysis
                           |
                           v
                        Reporting
```

Tools automate parts of this process.

They do not automatically determine whether a security issue exists.

---

# 2. Current Tool Notes

The following dedicated tool notes are available.

| Tool | Primary Use | Notes |
|---|---|---|
| Burp Suite | Web application security testing | [Burp Suite](burp-suite.md) |
| Nmap | Network and service discovery | [Nmap](nmap.md) |
| Nuclei | Template-based security testing | [Nuclei](nuclei.md) |
| ffuf | Content and parameter discovery | [ffuf](ffuf.md) |
| sqlmap | SQL injection validation | [sqlmap](sqlmap.md) |
| Metasploit | Exploit development and validation framework | [Metasploit](metasploit.md) |

These pages should be used together with the relevant methodology and vulnerability notes.

---

# 3. Tool Selection

Do not select tools only because they are popular.

Choose tools based on:

```text
Objective

Target

Protocol

Technology

Access Level

Scope

Testing Phase

Required Evidence

Operational Constraints

Rules of Engagement
```

Example:

```text
Objective:
Identify exposed TCP services

Appropriate Tool:
Nmap

Objective:
Inspect and modify HTTP requests

Appropriate Tool:
Burp Suite

Objective:
Discover hidden web content

Appropriate Tool:
ffuf

Objective:
Validate suspected SQL injection

Possible Tool:
sqlmap
```

The tool follows the objective.

---

# 4. Tool Selection Model

```text
What am I testing?
        |
        v
What question must be answered?
        |
        v
Which protocol / technology is involved?
        |
        v
What evidence is required?
        |
        v
Which tool can generate or inspect that evidence?
        |
        v
Is the tool permitted by the Rules of Engagement?
        |
        v
Execute
```

This reduces unnecessary scanning and tool usage.

---

# 5. Methodology Before Tooling

Weak workflow:

```text
Run Tool
   |
   v
Receive Output
   |
   v
Call Everything a Finding
```

Better workflow:

```text
Define Objective
      |
      v
Form Hypothesis
      |
      v
Select Tool
      |
      v
Collect Evidence
      |
      v
Validate Result
      |
      v
Exclude Alternatives
      |
      v
Determine Impact
      |
      v
Report
```

A scanner result is normally a lead for investigation rather than the final conclusion.

---

# 6. Understand the Tool

Before using a tool, understand:

```text
What does it send?

What does it modify?

How does it determine a result?

What assumptions does it make?

What privileges does it require?

Does it create files?

Does it create accounts?

Does it modify configuration?

Does it generate significant traffic?

Does it execute code?

Does it require cleanup?
```

This is particularly important when using automated exploitation or post-exploitation tooling.

---

# 7. Tool Categories

Security tools can be grouped into several broad categories.

```text
Reconnaissance

Network Discovery

Web Testing

Content Discovery

Vulnerability Scanning

Exploitation

Credential Testing

Directory Services

Traffic Analysis

Source Code Analysis

Cloud Security

Container Security

Detection Engineering

Reporting
```

Many tools span several categories.

---

# 8. Reconnaissance Tools

Reconnaissance tools help identify the external or internal attack surface.

Typical objectives include:

```text
Domain discovery

Subdomain enumeration

DNS analysis

IP discovery

ASN discovery

Technology identification

Certificate discovery

Service identification
```

Typical workflow:

```text
Known Asset
    |
    v
Passive Discovery
    |
    v
Candidate Assets
    |
    v
DNS Resolution
    |
    v
Reachability
    |
    v
Service Discovery
    |
    v
Technology Identification
```

See:

- [Reconnaissance](../reconnaissance/index.md)
- [Subdomain Enumeration](../reconnaissance/subdomain-enumeration.md)
- [Technology Identification](../reconnaissance/technology-identification.md)

---

# 9. Network Discovery Tools

Network discovery tools help identify:

```text
Hosts

Ports

Protocols

Services

Service versions

Network exposure
```

A common workflow is:

```text
Target Range
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
Version Detection
    |
    v
Manual Validation
```

[Nmap](nmap.md) is one of the primary tools used for this purpose.

---

# 10. Web Application Testing Tools

Web testing often requires interaction with:

```text
HTTP requests

HTTP responses

Headers

Cookies

Sessions

Parameters

APIs

Authentication

Authorisation

WebSockets
```

A typical workflow is:

```text
Application
    |
    v
Proxy Traffic
    |
    v
Understand Requests
    |
    v
Identify Input
    |
    v
Modify Request
    |
    v
Observe Response
    |
    v
Validate Security Behaviour
```

[Burp Suite](burp-suite.md) is commonly used as the central interception and testing platform.

See also:

- [Web Application Security](../web/index.md)
- [Web Methodology](../web/methodology.md)

---

# 11. Content Discovery

Content discovery attempts to identify resources that are not immediately visible through normal application navigation.

Potential targets include:

```text
Directories

Files

API endpoints

Backup files

Administrative interfaces

Development resources

Legacy paths
```

A typical workflow is:

```text
Base URL
   |
   v
Wordlist
   |
   v
Requests
   |
   v
Response Analysis
   |
   v
Interesting Resources
   |
   v
Manual Validation
```

[ffuf](ffuf.md) can be used for controlled content discovery.

See:

- [Content Discovery](../reconnaissance/content-discovery.md)

---

# 12. Template-Based Testing

Template-based scanners can automate checks for known patterns.

A simplified workflow is:

```text
Target
   |
   v
Template
   |
   v
Request
   |
   v
Matcher
   |
   v
Potential Result
   |
   v
Manual Validation
```

[Nuclei](nuclei.md) is an example of this approach.

Template matches should normally be validated before being reported as confirmed vulnerabilities.

---

# 13. SQL Injection Tooling

SQL injection testing may involve:

```text
Manual request analysis

Parameter identification

Response comparison

Database behaviour

Automated validation
```

A good workflow is:

```text
Suspicious Parameter
        |
        v
Manual Testing
        |
        v
Evidence of SQL Behaviour?
        |
       Yes
        |
        v
Controlled Automated Validation
        |
        v
Confirm Scope and Impact
```

[sqlmap](sqlmap.md) can assist with controlled validation.

See:

- [SQL Injection](../web/sql-injection.md)

---

# 14. Exploitation Frameworks

Exploitation frameworks provide reusable modules and supporting infrastructure for security testing.

Potential capabilities include:

```text
Exploit modules

Payload generation

Auxiliary modules

Protocol testing

Post-exploitation modules

Session management
```

[Metasploit](metasploit.md) is a widely used example.

Use exploitation frameworks carefully.

The existence of an exploit module does not mean:

```text
Target is vulnerable
```

and a version match alone is not sufficient proof.

---

# 15. Tool Output Is Evidence, Not Truth

Tool output should be treated as evidence requiring interpretation.

Example:

```text
Scanner:
Port 443 open
```

This supports:

```text
A TCP service responded on port 443 under the tested conditions.
```

It does not automatically prove:

```text
The application is vulnerable.
```

Similarly:

```text
Scanner:
Possible SQL Injection
```

does not automatically prove:

```text
Confirmed SQL Injection
```

Validation is required.

---

# 16. Automated Findings

Automated tools may produce:

```text
True Positives

False Positives

Informational Results

Configuration Observations

Version Matches

Uncertain Results
```

Each result should be evaluated.

---

# 17. False Positives

A false positive occurs when a tool reports a condition that does not represent the claimed security issue.

Possible causes include:

```text
Generic response matching

Unexpected application behaviour

WAF responses

Authentication redirects

Version inference

Custom error pages

Proxy behaviour

Caching

Rate limiting
```

Always inspect the evidence behind automated conclusions.

---

# 18. False Negatives

Tools can also miss vulnerabilities.

Possible reasons include:

```text
Authentication required

Custom application logic

Non-standard parameters

Unexpected encoding

JavaScript-generated requests

Rate limiting

WAF interference

Unsupported technology

Missing templates

Incorrect scanner configuration
```

Therefore:

```text
Scanner found nothing
```

does not mean:

```text
Application is secure
```

---

# 19. Manual Validation

Manual validation should determine whether the result is:

```text
Reproducible

Security Relevant

Within Scope

Correctly Classified

Supported by Evidence
```

Example:

```text
Automated Result
      |
      v
Reproduce Manually
      |
      v
Understand Behaviour
      |
      v
Compare Baseline
      |
      v
Exclude Alternatives
      |
      v
Confirm Security Impact
```

---

# 20. Establish a Baseline

Before modifying behaviour, understand the normal result.

For web testing:

```text
Normal Request
     |
     v
Normal Response
```

Then compare:

```text
Modified Request
     |
     v
Modified Response
```

For network testing:

```text
Known Reachable Service

Known Closed Port

Known Filtered Path
```

can help interpret scanner behaviour.

---

# 21. Positive and Negative Controls

Where practical, use both positive and negative controls.

Example:

```text
Test Input A
Expected:
Normal response

Test Input B
Expected:
Security behaviour triggered
```

This helps distinguish meaningful effects from normal application variation.

---

# 22. Reproducibility

A useful finding should be reproducible.

Record:

```text
Target

Timestamp

Tool

Tool Version

Configuration

Command

Input

Relevant Output

Manual Validation

Environment
```

This allows another assessor to repeat the test.

---

# 23. Record Tool Versions

Tool behaviour can change between versions.

Record versions for important evidence.

Examples:

```bash
nmap --version
```

```bash
nuclei -version
```

```bash
ffuf -V
```

```bash
sqlmap --version
```

For tools without a standard version flag, use the tool's documented method.

---

# 24. Commands as Evidence

Record important commands used during testing.

Example:

```bash
nmap -sV -p 80,443 example.test
```

The command provides context about:

```text
Target

Ports

Scan type

Version detection
```

Without it, the output may be difficult to interpret later.

---

# 25. Preserve Raw Output

Where appropriate, preserve raw tool output.

Example:

```bash
mkdir -p evidence/nmap
```

```bash
nmap -sV -p 80,443 example.test -oA evidence/nmap/service-scan
```

This may produce multiple output formats useful for later analysis.

Do not store sensitive evidence in insecure locations.

---

# 26. Evidence Structure

A simple assessment structure might be:

```text
engagement/
├── scope/
├── recon/
├── scans/
│   ├── nmap/
│   ├── nuclei/
│   └── web/
├── evidence/
├── screenshots/
├── requests/
├── responses/
├── notes/
└── reporting/
```

The exact structure is less important than consistency.

---

# 27. Timestamp Evidence

Timestamps help correlate activity across:

```text
Scanner output

Application logs

SIEM events

EDR events

Firewall logs

SOC alerts
```

For purple team exercises this can be particularly important.

```text
Execution Time
      |
      v
Telemetry Time
      |
      v
Detection Time
      |
      v
Alert Time
```

---

# 28. Tool Logging

Where available, enable useful tool logging.

Useful information may include:

```text
Request

Response

Timestamp

Target

Error

Result

Module

Template

Thread
```

Logging improves reproducibility and troubleshooting.

---

# 29. Output Formats

Many tools support several output formats.

Common formats include:

```text
Plain text

JSON

XML

CSV

HTML
```

Choose formats based on how the data will be used.

Example:

```text
Human Review:
Text

Automation:
JSON

Tool Integration:
XML / JSON

Spreadsheet Analysis:
CSV
```

---

# 30. Structured Output

Structured output is useful for automation.

Example concept:

```text
Tool
  |
  v
JSON
  |
  v
jq
  |
  v
Filtered Results
  |
  v
Validation Queue
```

Structured output can reduce fragile text parsing.

---

# 31. Tool Chaining

Security tools are often combined into pipelines.

Example:

```text
Discovery
    |
    v
Resolution
    |
    v
Reachability
    |
    v
Service Identification
    |
    v
Application Testing
```

Each stage should have a defined purpose.

Avoid building large pipelines where nobody understands why each tool is present.

---

# 32. Pipeline Design

A good pipeline should answer:

```text
What enters this stage?

What does the tool do?

What output is produced?

How is failure handled?

What goes to the next stage?
```

Example:

```text
Domains
   |
   v
DNS Resolution
   |
   v
Resolved Hosts
   |
   v
HTTP Probing
   |
   v
Live Web Applications
```

---

# 33. Deduplication

Automated pipelines frequently produce duplicate results.

Examples:

```text
Same hostname from multiple sources

Same URL with different formatting

Same IP mapped to multiple hostnames

Same finding from multiple templates
```

Deduplicate carefully without removing meaningful context.

---

# 34. Normalisation

Normalise data before comparing or merging it.

Examples:

```text
HTTP://EXAMPLE.COM

http://example.com/

http://example.com
```

may represent the same application depending on context.

Similarly:

```text
example.com:443

https://example.com
```

may need normalisation for some workflows.

Do not remove protocol or port information when it changes meaning.

---

# 35. Error Handling

Tool failures should not silently become empty results.

Distinguish:

```text
No findings

No response

Timeout

Tool error

Authentication failure

Rate limit

Permission failure

Configuration error
```

Example:

```text
0 results
```

is not useful unless the pipeline can distinguish:

```text
0 discovered
```

from:

```text
tool failed
```

---

# 36. Exit Codes

Automation should inspect exit codes where supported.

Example:

```bash
command
echo $?
```

Conceptually:

```text
Exit 0
   |
   v
Successful Execution

Non-Zero
   |
   v
Review Error
```

Do not assume every tool uses exit codes in exactly the same way.

Check its documentation.

---

# 37. Timeouts

Network tools can hang or take much longer than expected.

Use controlled timeouts where appropriate.

Consider:

```text
Connection timeout

Read timeout

Tool timeout

Per-host timeout

Pipeline timeout
```

Timeouts should be selected based on the environment rather than copied blindly.

---

# 38. Rate Limiting

High request rates can:

```text
Affect availability

Trigger defensive controls

Distort results

Create excessive logs

Cause account lockouts

Overload applications
```

Respect:

```text
Rules of Engagement

Approved request rates

Application capacity

Lockout policy

SOC coordination
```

Start conservatively when the environment is unknown.

---

# 39. Concurrency

Many tools support:

```text
Threads

Workers

Parallel requests

Concurrent targets
```

Higher concurrency can improve speed but increase operational impact.

A useful principle is:

```text
Use the minimum concurrency required to achieve the testing
objective within the approved window.
```

---

# 40. Authentication

Some tools support authenticated testing.

Examples:

```text
HTTP cookies

Bearer tokens

API keys

Basic authentication

Client certificates

SSH credentials
```

Authenticated testing may reveal functionality that unauthenticated scanners cannot reach.

Handle credentials securely.

---

# 41. Secrets in Commands

Avoid placing sensitive secrets directly into shell history where possible.

Potentially sensitive values include:

```text
Passwords

API tokens

Session cookies

Bearer tokens

Private keys
```

Use supported secure input methods, environment controls or temporary configuration where appropriate.

---

# 42. Shell History

Remember that commands may be stored in:

```text
Bash history

PowerShell history

Terminal logs

CI/CD logs

Screen recordings

Assessment notes
```

Do not expose customer credentials unnecessarily.

---

# 43. Temporary Files

Tools may create:

```text
Temporary payloads

Scan databases

Logs

Session files

Screenshots

Request files

Generated reports
```

Know where these are stored.

Clean them up when required by the engagement.

---

# 44. Data Sensitivity

Security tools can collect sensitive information.

Examples:

```text
Credentials

Tokens

Personal data

Internal hostnames

Source code

Configuration

Database content

Session information
```

Follow the engagement's data-handling requirements.

---

# 45. Scope Control

Before running a tool, confirm:

```text
Target in scope?

Port in scope?

Protocol in scope?

Authentication allowed?

Automated scanning allowed?

Exploit validation allowed?

Denial-of-service testing allowed?

Third-party systems excluded?
```

Tools do not understand contractual scope unless you configure them accordingly.

---

# 46. Target Files

For larger engagements, maintain explicit target files.

Example:

```text
scope/
├── domains.txt
├── urls.txt
├── ips.txt
└── excluded.txt
```

Review them before automated testing.

---

# 47. Scope Filtering

A discovery pipeline may identify assets outside the authorised scope.

Use:

```text
Discovery Results
       |
       v
Scope Filter
       |
       +---- In Scope -> Continue
       |
       +---- Out of Scope -> Stop
```

Discovery does not automatically authorise testing.

---

# 48. Third-Party Infrastructure

A target application may depend on:

```text
CDNs

Cloud services

Payment providers

Analytics platforms

Authentication providers

SaaS platforms
```

Do not assume these systems are included in the engagement scope.

---

# 49. Safe Defaults

Where possible, configure tools conservatively.

Examples:

```text
Reasonable request rates

Explicit targets

Explicit ports

Known wordlists

Controlled recursion

Limited scan depth

Non-destructive checks
```

Increase aggressiveness only when required and authorised.

---

# 50. Destructive Testing

Some modules or options may:

```text
Delete data

Modify data

Create accounts

Change configuration

Restart services

Crash services

Consume resources
```

Review tool documentation and module behaviour before execution.

Do not assume a module is safe because it is included in a security framework.

---

# 51. Exploit Validation

Exploit validation should answer a specific security question.

For example:

```text
Does this vulnerability permit unauthorised access under the
tested conditions?
```

The objective is not:

```text
How far can the tool go?
```

Use the minimum action necessary to demonstrate the impact agreed in the Rules of Engagement.

---

# 52. Cleanup

Before testing, identify whether cleanup is required.

Potential artifacts include:

```text
Files

Accounts

Services

Scheduled tasks

Registry entries

Database records

Cloud resources

Sessions
```

Record cleanup requirements as part of the test plan.

---

# 53. Cleanup Verification

Do not assume cleanup succeeded.

Validate:

```text
Artifact removed?

Account removed?

Configuration restored?

Service state restored?

Temporary file removed?

Test data removed?
```

Record evidence where required.

---

# 54. Tool Installation

Prefer installation from:

```text
Official project repository

Official release page

Trusted operating-system repository

Official package registry
```

Verify the source before executing downloaded security tools.

---

# 55. Tool Authenticity

For important tooling, consider verifying:

```text
Repository ownership

Release signatures

Checksums

Package origin

Release history
```

Security tools themselves are high-value supply-chain targets.

---

# 56. Avoid Random Binaries

Avoid downloading precompiled security tools from untrusted file-sharing sites.

Prefer:

```text
Official release

Trusted package

Source build
```

where practical.

---

# 57. Python Tools

Python-based security tools commonly benefit from isolated environments.

Example:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

This reduces dependency conflicts.

---

# 58. pipx

For Python command-line applications, `pipx` can provide isolated environments.

Example workflow:

```bash
pipx install <package>
```

Use the package name documented by the project's official installation instructions.

---

# 59. Go Tools

Many modern security tools are written in Go.

Typical installation patterns may use:

```bash
go install example.com/project/cmd/tool@latest
```

Always use the official project's documented package path.

Do not guess Go module paths.

---

# 60. Go Binary Location

Go-installed binaries commonly appear under:

```bash
$(go env GOPATH)/bin
```

Check:

```bash
go env GOPATH
```

and:

```bash
go env GOBIN
```

If the binary is not found, inspect the environment before reinstalling it.

---

# 61. PATH

A tool may be installed but unavailable because its directory is not in `PATH`.

Check:

```bash
echo "$PATH"
```

Locate a command:

```bash
command -v nmap
```

or:

```bash
which nmap
```

`command -v` is generally preferable in shell scripts.

---

# 62. Kali Linux Tooling

Kali Linux includes many security tools through its repositories and metapackages.

Do not assume every security tool is installed by default.

Check first:

```bash
command -v nmap
```

Then use the appropriate trusted installation method if required.

---

# 63. Tool Updates

Tool updates can introduce:

```text
New features

New checks

Changed defaults

Changed syntax

Bug fixes

Breaking changes
```

Record versions during assessments where reproducibility matters.

---

# 64. Pinning Versions

Automation may require version pinning.

Conceptually:

```text
Known Tool Version
       |
       v
Known Behaviour
       |
       v
Repeatable Pipeline
```

Automatically using the latest version can unexpectedly change behaviour.

---

# 65. Containerised Tools

Containers can help isolate tool dependencies.

Potential advantages:

```text
Reproducibility

Dependency isolation

Easy cleanup

Version pinning
```

Potential considerations:

```text
Network access

Mounted evidence

Permissions

Secrets

Container privileges
```

Do not run privileged containers unless necessary and authorised.

---

# 66. Tool Configuration

Keep reusable configuration separate from commands where practical.

Example:

```text
config/
├── nuclei/
├── nmap/
├── burp/
└── wordlists/
```

This can improve consistency across assessments.

---

# 67. Wordlists

Wordlists are inputs, not magic vulnerability databases.

Select them based on:

```text
Technology

Language

Application type

Environment

Testing objective
```

A huge wordlist is not automatically better.

---

# 68. Custom Wordlists

Application-specific information can create better discovery inputs.

Potential sources include:

```text
Application routes

JavaScript files

API documentation

Source code

Known naming conventions

Previous versions
```

Only derive and use such data where authorised.

---

# 69. Wordlist Quality

Evaluate:

```text
Relevance

Duplication

Case

Extensions

Technology

Language

Size
```

A focused wordlist may outperform a massive generic list.

---

# 70. Proxies

Many tools can route traffic through a proxy.

This can help:

```text
Inspect requests

Record evidence

Debug behaviour

Apply authentication

Control traffic
```

For web testing, routing a tool through Burp Suite can make automated activity easier to inspect.

---

# 71. Proxy Validation

When using a proxy, confirm:

```text
Traffic actually passes through proxy

TLS configuration works

Authentication is preserved

Target receives expected Host header

Proxy does not alter the test unintentionally
```

---

# 72. User-Agent

Some tools allow a custom User-Agent.

This may be useful for:

```text
Exercise identification

Traffic correlation

Application compatibility
```

However, do not assume User-Agent identification makes potentially disruptive testing safe.

---

# 73. Custom Headers

Security tools may need custom headers.

Examples:

```text
Authorization

Cookie

X-API-Key

Custom tenant headers

Application routing headers
```

Protect sensitive values in logs and shell history.

---

# 74. HTTP Request Files

For complex web testing, storing the complete request can improve reproducibility.

Conceptual file:

```text
requests/
└── login-request.txt
```

This may preserve:

```text
Method

Path

Headers

Cookies

Body
```

Sensitive values should be handled appropriately.

---

# 75. Burp Suite as a Central Workflow Tool

Burp Suite can connect:

```text
Browser
   |
   v
Proxy
   |
   +---- HTTP History
   |
   +---- Repeater
   |
   +---- Intruder
   |
   +---- Extensions
   |
   +---- Scanner where available
```

See [Burp Suite](burp-suite.md).

---

# 76. Nmap as a Discovery Tool

Nmap can assist with:

```text
Host discovery

Port scanning

Service detection

Version detection

Scripted service checks
```

A useful progression is:

```text
Host
   |
   v
Ports
   |
   v
Services
   |
   v
Versions
   |
   v
Manual Validation
```

See [Nmap](nmap.md).

---

# 77. Nuclei as a Validation Accelerator

Nuclei uses templates to automate checks.

A useful workflow is:

```text
Relevant Targets
      |
      v
Relevant Templates
      |
      v
Controlled Execution
      |
      v
Matches
      |
      v
Manual Review
      |
      v
Confirmed Findings
```

See [Nuclei](nuclei.md).

---

# 78. ffuf as a Discovery Tool

ffuf can help with:

```text
Directory discovery

File discovery

Virtual-host discovery

Parameter discovery

Value fuzzing
```

Use filters carefully.

A poor filter can hide meaningful results.

See [ffuf](ffuf.md).

---

# 79. sqlmap as a Validation Tool

sqlmap can automate many SQL injection testing tasks.

Use it after understanding:

```text
Request

Parameter

Authentication

Application behaviour

Scope

Potential impact
```

See [sqlmap](sqlmap.md).

---

# 80. Metasploit as a Framework

Metasploit can support:

```text
Exploit research

Controlled validation

Auxiliary protocol testing

Lab reproduction

Post-exploitation testing
```

Modules should be reviewed before execution.

See [Metasploit](metasploit.md).

---

# 81. Tool Correlation

A single tool may not provide enough evidence.

Example:

```text
Nmap
  |
  v
Service Identified
  |
  v
Manual Protocol Check
  |
  v
Application Tool
  |
  v
Validated Behaviour
```

Correlating independent evidence can strengthen conclusions.

---

# 82. Example Network Workflow

```text
Target:
10.10.10.10
```

First determine service exposure:

```bash
nmap -sV -p 22,80,443 10.10.10.10
```

Representative output:

```text
22/tcp  open  ssh
80/tcp  open  http
443/tcp open  https
```

Interpretation:

```text
Three tested TCP ports responded as open.

Service detection suggests SSH and HTTP-related services.
```

This is not yet a vulnerability finding.

Next:

```text
Validate services

Identify applications

Review versions carefully

Inspect configuration

Test relevant security controls
```

---

# 83. Example Web Workflow

```text
Application
    |
    v
Burp Proxy
    |
    v
Map Requests
    |
    v
Identify Parameters
    |
    v
Manual Testing
    |
    v
Targeted Automation
    |
    v
Validate
```

Possible tool combination:

```text
Burp Suite

ffuf

Nuclei

sqlmap
```

Each tool should have a specific purpose.

---

# 84. Example Content Discovery Workflow

Start with:

```text
https://example.test/
```

Discovery may identify:

```text
/admin

/api

/backup

/uploads
```

Do not report these simply because they exist.

Determine:

```text
Is authentication required?

Is access authorised correctly?

Is sensitive information exposed?

Is the endpoint intended to be public?

Does the resource create security impact?
```

---

# 85. Example Scanner Validation

Suppose a scanner reports:

```text
Potentially vulnerable software version
```

Validation process:

```text
Scanner Result
      |
      v
Verify Service
      |
      v
Verify Version
      |
      v
Verify Product
      |
      v
Review Affected Versions
      |
      v
Check Configuration Preconditions
      |
      v
Controlled Validation
      |
      v
Determine Actual Exposure
```

Do not report a CVE solely because a banner resembles an affected version.

---

# 86. Version Detection Limitations

Version detection may be affected by:

```text
Backported patches

Custom builds

Hidden banners

Reverse proxies

Load balancers

Vendor modifications

Incorrect service fingerprinting
```

Therefore:

```text
Version appears vulnerable
```

and:

```text
Vulnerability confirmed
```

are different conclusions.

---

# 87. Tool Confidence

It can be useful to classify automated results by confidence.

Example:

```text
High:
Direct behavioural evidence

Medium:
Strong fingerprint requiring validation

Low:
Heuristic or weak pattern match
```

Confidence does not replace validation.

---

# 88. Evidence Strength

A rough evidence model is:

```text
Weak
 |
 +---- Banner only
 |
 +---- Version inference
 |
 +---- Automated pattern match
 |
 +---- Reproducible behavioural evidence
 |
 +---- Reproducible impact
 |
Strong
```

The required evidence depends on the finding.

---

# 89. Screenshots

Screenshots can support evidence but should not replace raw technical data.

Capture:

```text
Relevant request

Relevant response

Important UI state

Tool result

Timestamp where useful
```

Avoid screenshots containing unrelated sensitive information.

---

# 90. Raw Requests and Responses

For web findings, raw requests and responses are often more useful than screenshots.

They provide:

```text
Method

Endpoint

Headers

Parameters

Body

Status

Response content
```

Sanitise secrets before placing them in reports.

---

# 91. Tool Output in Reports

Do not paste massive scanner output into the main finding.

Instead include:

```text
Relevant Result

Manual Validation

Security Impact

Evidence

Remediation
```

Large raw outputs can be retained separately as supporting evidence.

---

# 92. Reporting Tool Findings

Weak:

```text
Nuclei found CVE-XXXX-YYYY.
```

Better:

```text
Automated testing identified behaviour consistent with
CVE-XXXX-YYYY. Manual validation confirmed that the affected
functionality was reachable and reproduced the relevant
security impact under the tested conditions.
```

Only use the stronger conclusion when the evidence actually supports it.

---

# 93. Negative Results

Negative results can also be useful.

Example:

```text
The tested unauthenticated request returned HTTP 401 and no
protected content was observed.
```

This supports a conclusion about that specific test.

It does not prove every authorisation path is secure.

---

# 94. Tool Failure Versus Security Result

Distinguish:

```text
Tool timed out
```

from:

```text
Target did not respond
```

and:

```text
Security control blocked request
```

These can look similar from a poorly designed automation pipeline.

---

# 95. WAF Effects

A Web Application Firewall may affect tool results.

Possible effects include:

```text
403 responses

Connection resets

Rate limiting

Challenge pages

Modified responses

Blocked payloads
```

Record WAF behaviour as context.

Do not automatically classify a blocked scanner request as proof that the underlying application is not vulnerable.

---

# 96. EDR Effects

Endpoint security may affect authorised tool execution.

Possible outcomes:

```text
Execution blocked

File quarantined

Process terminated

Network connection blocked

Alert generated
```

For purple team exercises these may be expected security outcomes.

For other assessments they may affect the test methodology.

---

# 97. Tooling and Purple Teaming

Tools can generate representative behaviour for defensive validation.

```text
Tool
  |
  v
Representative Behaviour
  |
  v
Telemetry
  |
  v
Detection
  |
  v
Investigation
```

The purpose is to validate defensive capability rather than simply execute a tool.

See [Purple Teaming](../purple-teaming/index.md).

---

# 98. Tooling and Detection Engineering

Detection engineering may use tools to create repeatable tests.

```text
Detection
   |
   v
Test Procedure
   |
   v
Tool
   |
   v
Telemetry
   |
   v
Detection Result
```

See [Detection Engineering](../purple-teaming/detection-engineering.md).

---

# 99. Tooling and Red Teaming

Red team tooling may support:

```text
Reconnaissance

Initial Access

Execution

Persistence

Privilege Escalation

Credential Access

Discovery

Lateral Movement

Collection

Command and Control
```

Tool selection should follow the operation's objectives, scope and Rules of Engagement.

See [Red Teaming](../red-teaming/index.md).

---

# 100. Tooling and Source Code Review

Source code review tools may help identify:

```text
Dangerous functions

Secrets

Dependency risks

Data flows

Injection paths

Authentication logic

Authorisation logic
```

Automated results should be interpreted in the context of the application.

See [Source Code Review](../source-code-review/index.md).

---

# 101. Tooling and Vulnerability Research

Vulnerability research may use:

```text
Debuggers

Disassemblers

Fuzzers

Static analysis

Dynamic analysis

Patch diffing

Crash analysis
```

The objective is to understand root cause and security impact rather than simply generate crashes.

See [Vulnerability Research](../vulnerability-research/index.md).

---

# 102. Tool Documentation

For every regularly used tool, useful notes should include:

```text
Purpose

Installation

Core concepts

Common options

Workflows

Output interpretation

False positives

Evidence collection

Safety considerations

References
```

This is the model used by this Tools section.

---

# 103. Tool Page Quality Model

A useful tool page should answer:

```text
WHEN SHOULD I USE IT?

        |
        v

WHAT INPUT DOES IT NEED?

        |
        v

HOW DO I RUN IT?

        |
        v

WHAT SHOULD I EXPECT?

        |
        v

HOW DO I INTERPRET THE OUTPUT?

        |
        v

WHAT CAN GO WRONG?

        |
        v

HOW DO I VALIDATE THE RESULT?

        |
        v

WHAT EVIDENCE SHOULD I SAVE?
```

A list of commands alone is not enough.

---

# 104. Tool Troubleshooting Model

When a tool fails:

```text
Tool Failed
    |
    v
Installed?
    |
    v
Correct Version?
    |
    v
Correct Syntax?
    |
    v
Target Reachable?
    |
    v
DNS Working?
    |
    v
Proxy Correct?
    |
    v
Authentication Valid?
    |
    v
Permissions Correct?
    |
    v
Rate Limited?
    |
    v
Tool Error?
```

Troubleshoot from basic dependencies upward.

---

# 105. Installation Troubleshooting

Useful commands include:

```bash
command -v <tool>
```

```bash
<tool> --help
```

```bash
<tool> --version
```

where supported.

For package-managed tools, also inspect the package manager.

---

# 106. Network Troubleshooting

Before blaming the security tool, verify connectivity.

Examples:

```bash
ping -c 1 example.test
```

where ICMP testing is appropriate and permitted.

Check DNS:

```bash
getent hosts example.test
```

Check TCP connectivity:

```bash
nc -vz example.test 443
```

Only test authorised systems.

---

# 107. HTTP Troubleshooting

A simple HTTP request can establish a baseline.

```bash
curl -I https://example.test/
```

or:

```bash
curl -v https://example.test/
```

Verbose output may reveal:

```text
DNS resolution

TCP connection

TLS negotiation

HTTP request

HTTP response
```

This can help isolate tool-specific problems.

---

# 108. TLS Troubleshooting

TLS issues may involve:

```text
Certificate trust

Hostname mismatch

Protocol version

Cipher support

Client certificate

Interception proxy
```

Do not disable certificate verification permanently just to make a tool work.

Understand the reason first.

---

# 109. Proxy Troubleshooting

If a tool works directly but not through a proxy, inspect:

```text
Proxy address

Proxy port

TLS interception

Certificate trust

Authentication

HTTP version

DNS behaviour
```

Capture a simple known-good request before testing complex traffic.

---

# 110. Tool Comparison

Avoid asking:

```text
Which tool is best?
```

without context.

Instead compare:

```text
Purpose

Protocol

Accuracy

Control

Output

Automation

Performance

Extensibility

Safety

Evidence Quality
```

Different tools may be better at different stages.

---

# 111. Automation Versus Manual Testing

Automation is strong for:

```text
Scale

Repetition

Known patterns

Regression

Inventory

Consistency
```

Manual testing is strong for:

```text
Context

Business logic

Complex workflows

Unexpected behaviour

Chained vulnerabilities

Interpretation
```

A mature assessment uses both.

---

# 112. Recommended Workflow

```text
Manual Understanding
        |
        v
Targeted Automation
        |
        v
Automated Results
        |
        v
Manual Validation
        |
        v
Focused Follow-Up
        |
        v
Evidence
        |
        v
Conclusion
```

This keeps automation focused.

---

# 113. Tool Safety Checklist

Before running a security tool:

- [ ] Target is authorised
- [ ] Scope is confirmed
- [ ] Tool purpose is understood
- [ ] Tool source is trusted
- [ ] Tool version is known where relevant
- [ ] Command has been reviewed
- [ ] Target list has been reviewed
- [ ] Excluded systems have been removed
- [ ] Request rate is appropriate
- [ ] Authentication impact is understood
- [ ] Account lockout risk is understood
- [ ] Destructive functionality is disabled unless approved
- [ ] Cleanup requirements are understood
- [ ] Evidence destination is prepared
- [ ] Sensitive data handling is understood
- [ ] Stop conditions are known

---

# 114. Tool Result Checklist

For each important result:

- [ ] Confirm the tool completed successfully
- [ ] Confirm the target
- [ ] Confirm the timestamp
- [ ] Review raw output
- [ ] Understand why the tool matched
- [ ] Establish baseline behaviour
- [ ] Reproduce where practical
- [ ] Check alternative explanations
- [ ] Determine security relevance
- [ ] Determine impact
- [ ] Capture evidence
- [ ] Record limitations
- [ ] Avoid overclaiming

---

# 115. Evidence Checklist

Capture where relevant:

- [ ] Tool name
- [ ] Tool version
- [ ] Command
- [ ] Configuration
- [ ] Target
- [ ] Timestamp
- [ ] Raw output
- [ ] Relevant request
- [ ] Relevant response
- [ ] Screenshot
- [ ] Manual validation
- [ ] Security interpretation
- [ ] Cleanup evidence

---

# 116. Reporting Checklist

Before reporting a tool-derived finding:

- [ ] Is the issue reproducible?
- [ ] Is it within scope?
- [ ] Was the tool result manually reviewed?
- [ ] Is the vulnerability classification correct?
- [ ] Is the impact demonstrated?
- [ ] Are false positives excluded?
- [ ] Are alternative explanations considered?
- [ ] Is evidence sufficient?
- [ ] Are sensitive values sanitised?
- [ ] Is remediation relevant to the root cause?
- [ ] Is the conclusion limited to what was actually tested?

---

# 117. Practical Tool Workflow

A reusable workflow is:

```text
1. Define the security objective.

2. Confirm scope.

3. Identify the target technology.

4. Select the technique.

5. Select the appropriate tool.

6. Verify the tool source.

7. Record the tool version.

8. Review tool behaviour.

9. Configure conservative settings.

10. Establish a baseline.

11. Execute the tool.

12. Confirm successful execution.

13. Preserve raw output.

14. Review results.

15. Reproduce important results.

16. Compare against baseline.

17. Exclude alternative explanations.

18. Determine security impact.

19. Capture evidence.

20. Perform cleanup where required.

21. Report defensible conclusions.

22. Retest remediation where applicable.
```

---

# 118. Tooling Maturity

A simple maturity model is:

## Level 1 - Ad Hoc

```text
Tools run manually

Little documentation

Commands not retained

Results copied directly into reports
```

## Level 2 - Repeatable

```text
Standard tools

Documented commands

Consistent evidence structure

Basic validation
```

## Level 3 - Integrated

```text
Tool pipelines

Structured output

Scope filtering

Deduplication

Manual validation workflow
```

## Level 4 - Engineered

```text
Version-controlled configuration

Automated error handling

Reproducible environments

Structured evidence

Quality gates
```

## Level 5 - Continuously Improved

```text
Tool effectiveness measured

Pipelines regularly reviewed

False positives tracked

Tool changes tested

Knowledge shared across teams
```

The objective is not maximum automation.

The objective is reliable and defensible security testing.

---

# 119. Common Tooling Mistakes

Avoid:

```text
Running every tool against every target

Using default settings without understanding them

Assuming scanner output is correct

Reporting version matches as confirmed vulnerabilities

Ignoring tool errors

Ignoring rate limits

Ignoring scope expansion

Using outdated tools

Downloading binaries from untrusted sources

Leaving temporary artifacts

Storing secrets in shell history

Using huge wordlists without purpose

Adding more tools instead of improving methodology
```

---

# 120. A Tool Is Not a Methodology

This distinction is fundamental.

```text
Nmap
```

is not:

```text
Network Security Methodology
```

```text
Burp Suite
```

is not:

```text
Web Application Security Methodology
```

```text
Metasploit
```

is not:

```text
Penetration Testing Methodology
```

```text
Nuclei
```

is not:

```text
Vulnerability Management Methodology
```

Tools implement parts of a methodology.

---

# 121. Know What the Tool Actually Proved

After every important command, ask:

```text
What did this result actually demonstrate?
```

Example:

```text
Result:
HTTP 200

Supports:
The tested HTTP request received a successful HTTP response.

Does not automatically prove:
The user was authorised to access the returned resource.
```

Another example:

```text
Result:
Port 445 open

Supports:
The tested TCP port responded as open.

Does not automatically prove:
SMB is vulnerable.
```

This habit significantly improves assessment quality.

---

# 122. Tool Output Interpretation Model

```text
RAW OUTPUT
    |
    v
WHAT WAS TESTED?
    |
    v
WHAT WAS OBSERVED?
    |
    v
WHAT DOES IT SUPPORT?
    |
    v
WHAT DOES IT NOT SUPPORT?
    |
    v
WHAT ELSE COULD EXPLAIN IT?
    |
    v
WHAT SHOULD BE TESTED NEXT?
    |
    v
DEFENSIBLE CONCLUSION
```

---

# 123. Tool Knowledge

A security professional should understand both:

```text
How to use the tool
```

and:

```text
What the tool is doing
```

For example, knowing:

```bash
nmap -sS example.test
```

is less valuable without understanding:

```text
TCP

SYN

SYN/ACK

RST

Filtered responses

Timeout behaviour
```

The underlying protocol knowledge remains essential.

---

# 124. Build Tool Knowledge Progressively

A useful learning progression is:

```text
Protocol / Technology
        |
        v
Manual Interaction
        |
        v
Tool Basics
        |
        v
Tool Options
        |
        v
Output Interpretation
        |
        v
Automation
        |
        v
Advanced Workflows
```

Learning the tool before the underlying technology can create blind spots.

---

# 125. Tool Notes Strategy

The Tools section should remain focused.

A dedicated page is useful when a tool has enough depth to justify:

```text
Installation

Core concepts

Important options

Practical workflows

Output interpretation

Troubleshooting

Evidence handling

Integration with other tools
```

Small utilities can instead be covered in [Cheatsheets](../cheatsheets/index.md).

This avoids creating hundreds of shallow tool pages.

---

# 126. Final Tooling Model

The complete model is:

```text
AUTHORISATION
      |
      v
SCOPE
      |
      v
SECURITY OBJECTIVE
      |
      v
UNDERSTAND TECHNOLOGY
      |
      v
SELECT TECHNIQUE
      |
      v
SELECT TOOL
      |
      v
UNDERSTAND TOOL BEHAVIOUR
      |
      v
CONFIGURE
      |
      v
BASELINE
      |
      v
EXECUTE
      |
      v
VERIFY EXECUTION
      |
      v
COLLECT RAW OUTPUT
      |
      v
INTERPRET
      |
      v
MANUAL VALIDATION
      |
      v
CORRELATE
      |
      v
DETERMINE IMPACT
      |
      v
CAPTURE EVIDENCE
      |
      v
CLEANUP
      |
      v
REPORT
      |
      v
RETEST
```

Tools accelerate security testing.

They do not replace:

```text
Knowledge

Methodology

Critical thinking

Validation

Evidence

Professional judgement
```

A strong security practitioner should therefore be able to explain not only:

```text
Which command was executed?
```

but also:

```text
Why was it executed?

What did it test?

How did the tool perform the test?

What did the output mean?

What alternative explanations exist?

What evidence confirms the conclusion?

What should happen next?
```

---

# Tool Notes

## Web Application Testing

- [Burp Suite](burp-suite.md)
- [ffuf](ffuf.md)
- [sqlmap](sqlmap.md)

## Network Testing

- [Nmap](nmap.md)

## Automated Security Testing

- [Nuclei](nuclei.md)

## Exploitation and Validation

- [Metasploit](metasploit.md)

---

# Related Notes

- [Web Application Security](../web/index.md)
- [Source Code Review](../source-code-review/index.md)
- [Active Directory](../active-directory/index.md)
- [Windows](../windows/index.md)
- [Linux](../linux/index.md)
- [Privilege Escalation Explorer](../privesc/index.md)
- [Red Teaming](../red-teaming/index.md)
- [Purple Teaming](../purple-teaming/index.md)
- [Vulnerability Research](../vulnerability-research/index.md)
- [Cheatsheets](../cheatsheets/index.md)

---

# References

- [Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }
- [Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }
- [Nuclei Documentation](https://docs.projectdiscovery.io/tools/nuclei/overview){ target="_blank" rel="noopener noreferrer" }
- [ffuf](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }
- [sqlmap](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }
- [Metasploit Documentation](https://docs.rapid7.com/metasploit/){ target="_blank" rel="noopener noreferrer" }
- [Kali Linux Tools](https://www.kali.org/tools/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

!!! tip "Start with the objective"

    Select a tool only after determining what security question needs to be answered. This keeps testing focused and makes the resulting evidence easier to interpret.

!!! tip "Preserve raw evidence"

    Important automated results should be retained with the command, configuration, target, timestamp and tool version where appropriate. This makes validation and later reproduction significantly easier.

!!! tip "Understand why a result occurred"

    Do not stop when a scanner reports a match. Determine which request, response, event or observable caused the result and whether that evidence actually supports the claimed vulnerability.

!!! tip "Use automation to increase consistency"

    Automation is most valuable when it makes a well-understood methodology repeatable. Automating an unclear process usually makes unclear results appear faster.

!!! warning "Scanner output is not automatically a finding"

    Automated results may contain false positives, false negatives and incomplete conclusions. Validate important results before reporting them as confirmed security issues.

!!! warning "Keep tooling within scope"

    Discovery tools can identify systems outside the authorised target set. Apply scope controls before passing discovered assets into later scanning or validation stages.
