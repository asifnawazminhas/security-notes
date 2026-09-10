---
title: Web Application Testing Tools
description: Practical overview of tools used during authorised web application security assessments, including interception, crawling, content discovery, automated testing, injection validation, and out-of-band interaction testing.
---

# Web Application Testing Tools

Web application testing tools help inspect, manipulate, automate, and validate application behaviour.

They are most useful when connected to a specific testing objective.

The goal is not:

```text
Run every tool
      |
      v
Collect scanner output
      |
      v
Report everything
```

The goal is:

```text
Security Question
      |
      v
Choose Appropriate Tool
      |
      v
Perform Focused Test
      |
      v
Observe Behaviour
      |
      v
Interpret Result
      |
      v
Validate Manually
      |
      v
Capture Evidence
      |
      v
Reach Defensible Conclusion
```

This section focuses on tools commonly used for:

- intercepting HTTP traffic;
- manually replaying requests;
- modifying parameters and headers;
- content discovery;
- crawling;
- automated vulnerability checks;
- SQL injection testing;
- out-of-band validation;
- response comparison;
- application mapping;
- authenticated testing;
- API testing.

!!! warning "Authorised testing only"
    Use these tools only against applications and systems that are explicitly within scope. Some features can generate large request volumes, alter application state, trigger account lockouts, invoke backend functionality, or interact with third-party systems. Confirm rules of engagement before using intrusive or automated functionality.

---

# Where These Tools Fit

A typical web assessment might use several tools at different stages.

```text
Scope
  |
  v
Reconnaissance
  |
  v
Technology Identification
  |
  v
Attack Surface Mapping
  |
  +--> Burp Suite
  +--> Katana
  +--> ffuf
  |
  v
Focused Testing
  |
  +--> Burp Suite
  +--> sqlmap
  +--> Nuclei
  +--> Interactsh
  |
  v
Manual Validation
  |
  v
Evidence
  |
  v
Reporting
```

Related methodology:

[Web Application Security](../../web/index.md)

[Web Application Testing Methodology](../../web/methodology.md)

[Web Application Pentesting Checklist](../../web/checklist.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

---

# Core Tool Categories

| Category | Tools |
|---|---|
| Interception and manual testing | Burp Suite |
| Content discovery | ffuf |
| Crawling and endpoint discovery | Katana |
| Automated checks | Nuclei |
| SQL injection testing | sqlmap |
| Out-of-band validation | Interactsh |
| Supporting HTTP validation | curl |
| Supporting reconnaissance | WhatWeb, Wappalyzer, httpx |

Each tool answers a different question.

---

# Burp Suite

Burp Suite is one of the most important tools in manual web application security testing.

It is used to intercept, inspect, modify, and replay HTTP and WebSocket traffic.

Typical uses include:

- understanding application requests;
- modifying parameters;
- testing authentication;
- testing authorisation;
- analysing sessions;
- testing APIs;
- replaying requests;
- comparing responses;
- inspecting redirects;
- reviewing cookies;
- testing request headers;
- testing application state;
- working with WebSockets;
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

Detailed note:

[Burp Suite](burp-suite.md)

Official documentation:

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

---

# Burp Suite Community vs Professional

Burp Suite Community Edition supports many important manual-testing workflows.

Burp Suite Professional adds additional functionality intended for larger, more automated, and more advanced workflows.

A simplified comparison is:

| Area | Community | Professional |
|---|---|---|
| Proxy | Yes | Yes |
| Repeater | Yes | Yes |
| Decoder | Yes | Yes |
| Comparer | Yes | Yes |
| Sequencer | Yes | Yes |
| Intruder | Limited compared with Professional | Enhanced |
| Scanner | No | Yes |
| Burp Collaborator | Limited availability depending on feature/workflow | Integrated |
| Crawl and audit workflows | No full Scanner workflow | Yes |
| Extensions | Yes | Yes |

Exact product capabilities can change, so verify current differences against PortSwigger documentation.

The important point is that **manual testing remains essential in both editions**.

---

# Burp Proxy

Burp Proxy allows the tester to observe browser and application traffic.

Typical questions include:

```text
What requests does the browser send?

Which parameters are client controlled?

Which cookies are used?

Which API calls occur?

Which authentication tokens are present?

Which headers affect application behaviour?
```

A normal workflow is:

```text
Browser
  |
  v
Burp Proxy
  |
  v
Application
```

Captured traffic becomes the foundation for deeper testing.

---

# HTTP History

HTTP History provides a chronological record of proxied requests and responses.

Useful observations include:

- endpoints;
- parameters;
- HTTP methods;
- cookies;
- tokens;
- API calls;
- response codes;
- redirects;
- content types;
- background JavaScript requests.

HTTP History is particularly useful during application mapping.

---

# Burp Repeater

Repeater is one of the most useful tools for focused manual testing.

It allows a captured request to be replayed repeatedly while individual values are modified.

Typical workflow:

```text
Capture Request
      |
      v
Send to Repeater
      |
      v
Establish Baseline
      |
      v
Modify One Variable
      |
      v
Compare Response
      |
      v
Interpret Behaviour
```

This supports testing of:

- authentication;
- authorisation;
- IDOR/BOLA;
- injection;
- business logic;
- headers;
- cookies;
- API parameters;
- request methods.

---

# Burp Intruder

Intruder helps automate repeated requests with changing inputs.

Possible uses include:

- parameter enumeration;
- value testing;
- response comparison;
- limited fuzzing;
- payload insertion;
- application behaviour analysis.

Intruder should not be used blindly.

Before sending large request sets, consider:

- account lockouts;
- rate limits;
- application stability;
- testing scope;
- request volume.

---

# Burp Decoder

Decoder can help transform data between common representations.

Examples include:

- URL encoding;
- Base64;
- hexadecimal;
- HTML encoding.

It is useful when reviewing or modifying application values.

Do not assume encoded data is encrypted.

---

# Burp Comparer

Comparer helps identify differences between requests or responses.

This can be useful for:

- role comparison;
- authentication differences;
- error analysis;
- parameter behaviour;
- response-based injection testing.

Example:

```text
User A Response
       |
       v
Comparer
       ^
       |
User B Response
```

Small response differences can reveal meaningful authorisation or application-state changes.

---

# Burp Extensions

Burp extensions can add specialised functionality.

Examples of commonly useful categories include:

- authorisation testing;
- request logging;
- JWT analysis;
- hidden parameter discovery;
- request smuggling testing;
- GraphQL support;
- API analysis.

The exact extension should be chosen according to the technique being tested.

Related web pages should link to relevant extensions where useful.

---

# Useful Burp Extensions by Topic

Examples include:

| Topic | Example Extension |
|---|---|
| Authorisation | Autorize |
| Hidden parameters | Param Miner |
| Request smuggling | HTTP Request Smuggler |
| JWT testing | JWT Editor |
| Logging | Logger++ |
| GraphQL | GraphQL-related extensions where appropriate |

Always verify current extension availability in the BApp Store.

Official resource:

[Burp Suite BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }

---

# ffuf

ffuf is a fast web fuzzer commonly used for discovery.

Typical uses include:

- directory discovery;
- file discovery;
- extension discovery;
- virtual host discovery;
- parameter discovery;
- input fuzzing;
- API route discovery.

Detailed note:

[ffuf](ffuf.md)

Official repository:

[ffuf - GitHub](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }

---

# ffuf Workflow

A good ffuf workflow begins with a baseline.

```text
Request Known Page
      |
      v
Request Random Non-Existing Page
      |
      v
Understand Default Response
      |
      v
Run ffuf
      |
      v
Filter Noise
      |
      v
Validate Interesting Results
```

Without this baseline, content discovery often produces false positives.

---

# Directory Discovery

A common use is discovering hidden directories.

Conceptually:

```text
https://example.test/FUZZ
```

with candidates such as:

```text
admin
api
backup
internal
uploads
```

The goal is not to assume every different response is important.

Instead inspect:

- status;
- size;
- words;
- lines;
- redirect;
- response body.

---

# File Discovery

File discovery may identify resources such as:

```text
backup.zip
config.old
test.txt
debug.log
```

File discovery should remain within scope and avoid excessive request volume.

Any discovered sensitive content should be handled according to the engagement rules.

---

# Extension Discovery

Applications may expose different resources depending on extension.

Examples:

```text
.php
.aspx
.jsp
.json
.xml
.txt
.bak
```

Extension discovery can help identify application structure.

---

# Virtual Host Discovery

ffuf can also help identify virtual hosts where authorised.

The conceptual model is:

```text
Host Header
   |
   v
FUZZ.example.test
```

However, wildcard virtual hosting can create large numbers of false positives.

Always test a random hostname baseline.

---

# Parameter Discovery

Parameter discovery may identify undocumented inputs.

Example conceptual targets:

```text
?FUZZ=value
```

or:

```text
parameter-name: value
```

Discovered parameters should be manually validated to determine whether they affect behaviour.

---

# Response Filtering

ffuf is powerful because results can be filtered by response characteristics.

Useful properties include:

```text
Status
Size
Words
Lines
```

Suppose random paths consistently return:

```text
200
5234 bytes
812 words
104 lines
```

Then responses matching that baseline may represent soft 404s.

The objective is to separate signal from noise.

---

# Katana

Katana is a ProjectDiscovery crawler used to discover web endpoints and application resources.

It can help identify:

- links;
- forms;
- JavaScript-referenced endpoints;
- paths;
- API routes;
- linked resources.

Detailed note:

[Katana](katana.md)

Official documentation:

[ProjectDiscovery Katana](https://docs.projectdiscovery.io/opensource/katana/overview){ target="_blank" rel="noopener noreferrer" }

---

# Crawling vs Fuzzing

Crawling and fuzzing solve different problems.

```text
Crawler
   |
   v
Follow Known Links and Application Structure
```

versus:

```text
Fuzzer
   |
   v
Try Candidate Paths or Inputs
```

Therefore:

```text
Katana
```

and:

```text
ffuf
```

are complementary.

---

# Katana Workflow

Example:

```text
Target
  |
  v
Katana
  |
  +-- HTML links
  +-- JavaScript
  +-- forms
  +-- endpoints
  |
  v
URL Inventory
  |
  v
Manual Review
```

The resulting URL list can support:

- Burp testing;
- parameter discovery;
- API mapping;
- content review;
- Nuclei scanning where authorised.

---

# JavaScript-Aware Crawling

Modern applications frequently expose important routes through JavaScript.

Examples include:

```text
/api/users
/api/account
/graphql
/internal/search
```

A JavaScript-aware crawler can help surface these endpoints.

Related note:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

---

# Crawl Scope

Crawlers can follow many links rapidly.

Always constrain:

- hostname;
- domain;
- path;
- depth;
- third-party navigation.

Do not automatically follow links to external providers.

---

# Nuclei

Nuclei is a template-driven security scanner maintained by ProjectDiscovery.

It is useful for repeatable checks across many targets.

Potential uses include:

- known vulnerability detection;
- exposed files;
- configuration issues;
- technology detection;
- common security weaknesses;
- organisation-specific checks.

Detailed note:

[Nuclei](nuclei.md)

Official documentation:

[ProjectDiscovery Nuclei](https://docs.projectdiscovery.io/opensource/nuclei/overview){ target="_blank" rel="noopener noreferrer" }

---

# How Nuclei Works

Conceptually:

```text
Target
  |
  v
Template
  |
  +-- Request
  +-- Matcher
  +-- Extractor
  |
  v
Response
  |
  v
Match / No Match
```

The important distinction is:

```text
Template Match
      !=
Confirmed Vulnerability
```

A match needs interpretation.

---

# Nuclei Validation Workflow

```text
Nuclei Match
      |
      v
Read Template
      |
      v
Understand Request
      |
      v
Understand Matcher
      |
      v
Reproduce Manually
      |
      v
Assess Impact
      |
      v
Confirm or Reject
```

Never report a vulnerability based only on the template name.

---

# Template Severity

Template severity is useful for triage.

It is not a substitute for assessing actual impact.

A template may be labelled:

```text
critical
```

but the target-specific context may differ.

Likewise, a low-severity technical condition may have greater business impact in a specific environment.

---

# Custom Nuclei Templates

Custom templates can be useful for:

- organisation-specific checks;
- regression testing;
- recurring exposure detection;
- known configuration patterns;
- post-remediation validation.

Custom templates should be:

- reviewed;
- version controlled;
- tested safely;
- documented;
- limited to approved behaviour.

---

# Nuclei and httpx

A common workflow is:

```text
Subdomains
    |
    v
httpx
    |
    v
Reachable URLs
    |
    v
Nuclei
```

Only send authorised targets into automated scanners.

---

# sqlmap

sqlmap automates many aspects of SQL injection testing.

Typical uses include:

- validating suspected SQL injection;
- characterising database behaviour;
- comparing injection techniques;
- reproducing a known injection condition.

Detailed note:

[sqlmap](sqlmap.md)

Official resources:

[sqlmap](https://sqlmap.org/){ target="_blank" rel="noopener noreferrer" }

[sqlmap - GitHub](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }

---

# Manual SQL Injection First

A good workflow is:

```text
Interesting Parameter
       |
       v
Manual Testing
       |
       v
Suspicious Behaviour
       |
       v
sqlmap
       |
       v
Automated Validation
       |
       v
Manual Confirmation
```

Do not begin with aggressive automation without understanding the request.

---

# Why Manual Understanding Matters

sqlmap may generate many requests.

Before using it, understand:

- request method;
- parameter location;
- authentication;
- CSRF behaviour;
- session handling;
- application state;
- rate limits;
- WAF behaviour.

This reduces noise and operational risk.

---

# Request Files

Complex authenticated requests are often easier to reproduce from captured HTTP requests.

A common workflow is:

```text
Browser
   |
   v
Burp Suite
   |
   v
Captured Request
   |
   v
sqlmap
```

This helps preserve:

- cookies;
- headers;
- POST bodies;
- custom parameters;
- authentication context.

---

# SQL Injection Is a Security Condition

The finding should describe:

```text
Untrusted input influences database query behaviour
```

not:

```text
sqlmap worked
```

The tool is only part of the validation process.

Related note:

[SQL Injection](../../web/sql-injection.md)

---

# Interactsh

Interactsh provides out-of-band interaction infrastructure.

It is useful when a vulnerability cannot be confirmed directly from the immediate response.

Detailed note:

[Interactsh](interactsh.md)

Official documentation:

[ProjectDiscovery Interactsh](https://docs.projectdiscovery.io/opensource/interactsh/overview){ target="_blank" rel="noopener noreferrer" }

---

# Out-of-Band Testing

Some application behaviour occurs asynchronously.

Example:

```text
HTTP Request
      |
      v
Application
      |
      v
Backend Makes DNS/HTTP Request
      |
      v
Interactsh
```

This can help validate suspected:

- blind SSRF;
- blind XXE;
- asynchronous callbacks;
- backend fetch behaviour.

---

# Correlation Matters

An external callback is only useful evidence if it can be correlated to the triggering test.

Record:

```text
Request
Unique interaction identifier
Timestamp
Protocol
Source information where appropriate
Observed callback
```

This helps establish causality.

---

# Blind SSRF Example Model

```text
Controlled Request
      |
      v
Application Parameter
      |
      v
Backend Fetch
      |
      v
Interactsh DNS/HTTP Interaction
      |
      v
Correlate to Original Request
```

Related note:

[Server Side Request Forgery](../../web/ssrf.md)

---

# Blind XXE Example Model

```text
XML Input
   |
   v
XML Parser
   |
   v
External Resource Lookup
   |
   v
Interactsh
```

Related note:

[XML External Entity Injection](../../web/xxe.md)

---

# curl as a Supporting Tool

curl is useful throughout web testing for focused HTTP validation.

Examples:

```bash
curl -i https://example.test
```

```bash
curl -I https://example.test
```

```bash
curl -v https://example.test
```

It is especially useful for:

- reproducing simple requests;
- checking redirects;
- inspecting headers;
- API testing;
- verifying scanner observations.

Quick reference:

[curl Cheatsheet](../../cheatsheets/curl.md)

---

# Browser Developer Tools

Browser developer tools are also important web-testing tools.

Useful tabs include:

```text
Network
Sources
Application
Storage
Console
Elements
```

They can reveal:

- API calls;
- JavaScript;
- cookies;
- storage;
- application state;
- source maps;
- frontend routes.

Browser analysis complements Burp rather than replacing it.

---

# Automated vs Manual Testing

Different tools provide different strengths.

```text
Automation
    |
    +-- breadth
    +-- repeatability
    +-- scale

Manual Testing
    |
    +-- context
    +-- logic
    +-- interpretation
    +-- impact
```

Strong web assessments combine both.

---

# Baseline First

Before fuzzing or comparing behaviour, establish a baseline.

For example:

```bash
curl -i https://example.test/
```

Then:

```bash
curl -i https://example.test/random-not-found-728361
```

Compare:

| Property | Normal | Random |
|---|---|---|
| Status | ? | ? |
| Length | ? | ? |
| Words | ? | ? |
| Lines | ? | ? |
| Title | ? | ? |
| Redirect | ? | ? |

This helps interpret ffuf, Nuclei, crawler, and manual results.

---

# Authentication Context

Many web-testing tools behave differently depending on authentication.

An unauthenticated view may expose:

```text
/login
/public
```

while authentication may reveal:

```text
/dashboard
/api
/admin
/account
```

Document:

```text
Which identity was used?

Which role?

Which session?

Was MFA completed?

Which tenant?
```

This matters during result interpretation.

---

# Role-Based Testing

For authorisation testing, compare roles.

Example:

```text
User A
  |
  +--> request

User B
  |
  +--> same request
```

Use Burp Repeater or Comparer to isolate meaningful differences.

Related notes:

[Authorisation Testing](../../web/authorisation.md)

[IDOR and BOLA](../../web/idor-bola.md)

---

# Session Handling

Tools should not accidentally invalidate or corrupt test sessions.

Watch for:

- rotating cookies;
- CSRF tokens;
- expired tokens;
- session-bound parameters;
- anti-automation state.

Related note:

[Session Management](../../web/session-management.md)

---

# MFA

Automation may interact poorly with MFA-protected flows.

Do not repeatedly trigger:

- push notifications;
- OTP delivery;
- account verification;
- recovery workflows.

Related note:

[Multi-Factor Authentication Security](../../web/mfa.md)

---

# Rate Limiting

Automated tools can trigger rate limiting.

Possible response:

```text
429 Too Many Requests
```

This may affect:

- ffuf;
- Intruder;
- Nuclei;
- sqlmap;
- crawlers.

Control:

- request rate;
- concurrency;
- retry behaviour.

Related note:

[Rate Limiting and Anti-Automation](../../web/rate-limiting.md)

---

# WAF Behaviour

A WAF can affect almost every tool in this section.

Potential effects include:

- request blocking;
- status-code changes;
- connection resets;
- challenge pages;
- rate limiting;
- modified responses.

A scanner result may therefore reflect:

```text
WAF behaviour
```

rather than:

```text
Application behaviour
```

Inspect raw requests and responses.

---

# Reverse Proxies

Reverse proxies may also affect:

- headers;
- paths;
- redirects;
- request normalisation;
- HTTP versions.

This matters particularly for:

- request smuggling;
- host-header testing;
- cache behaviour.

Related notes:

[HTTP Request Smuggling](../../web/http-request-smuggling.md)

[HTTP Host Header Attacks](../../web/host-header-attacks.md)

[Web Cache Poisoning](../../web/web-cache-poisoning.md)

---

# API Testing

Most tools in this section can be used with APIs.

Useful tools include:

- Burp Suite;
- curl;
- ffuf;
- Katana;
- Nuclei;
- sqlmap.

API testing requires attention to:

```text
HTTP method
Content type
Authentication
Object identifiers
Pagination
Versioning
Error handling
Rate limits
```

Related note:

[API Security](../../web/api-security.md)

---

# GraphQL

GraphQL applications may benefit from:

- Burp Suite;
- GraphQL-specific extensions;
- manual query analysis;
- introspection review;
- schema analysis.

Related note:

[GraphQL API Security](../../web/graphql.md)

---

# WebSockets

Burp Suite can help inspect WebSocket traffic.

Testing should consider:

- authentication;
- authorisation;
- message structure;
- server-side validation;
- cross-site WebSocket hijacking.

Related note:

[WebSocket Security](../../web/websockets.md)

---

# Business Logic

Automated tools are particularly weak at understanding business logic.

Examples include:

```text
Workflow abuse
Price manipulation
State-transition issues
Approval bypasses
Multi-step process flaws
```

These require manual reasoning.

Related note:

[Business Logic Vulnerabilities](../../web/business-logic.md)

---

# Race Conditions

Testing race conditions often requires carefully timed concurrent requests.

Tools may help generate concurrency, but the tester must understand:

- state transitions;
- transaction boundaries;
- expected invariant;
- resulting impact.

Related note:

[Race Conditions](../../web/race-conditions.md)

---

# File Upload Testing

Burp Suite is particularly useful for manipulating upload requests.

Inspect:

- multipart boundaries;
- filename;
- content type;
- file content;
- response;
- storage path.

Related note:

[File Upload Security](../../web/file-upload.md)

---

# Path Traversal

Repeater and other HTTP clients can help systematically compare path-handling behaviour.

Related note:

[Path Traversal](../../web/path-traversal.md)

---

# Server-Side Template Injection

Testing SSTI requires identifying whether user-controlled data reaches a template engine.

Automation can help generate candidates, but manual validation is important.

Related note:

[Server-Side Template Injection](../../web/ssti.md)

---

# Cross-Site Scripting

Burp Suite is commonly used to inspect reflection, encoding, and context.

Browser execution remains important for validating client-side impact.

Related note:

[Cross-Site Scripting](../../web/xss.md)

---

# DOM-Based Vulnerabilities

DOM testing relies heavily on:

- browser developer tools;
- JavaScript review;
- Burp;
- source analysis.

Related note:

[DOM-Based Vulnerabilities](../../web/dom-based-vulnerabilities.md)

---

# Open Redirect

Burp Repeater and curl are useful for testing redirect behaviour.

Related note:

[Open Redirect](../../web/open-redirect.md)

---

# Host Header Testing

Burp Repeater is particularly useful because Host and related headers can be modified directly.

Related note:

[HTTP Host Header Attacks](../../web/host-header-attacks.md)

---

# Security Headers

curl and Burp can inspect security-related headers.

Related note:

[HTTP Security Headers](../../web/http-security-headers.md)

---

# Evidence Collection

For important tool-assisted tests, capture:

```text
Tool
Tool version
Target
Test identity
Exact request
Exact response
Command or configuration
Timestamp
Relevant output
Manual validation
Impact
```

Avoid relying only on screenshots of scanner interfaces.

Raw technical evidence is usually stronger.

---

# Tool Output vs Finding

Keep the distinction clear.

```text
ffuf discovers /admin
        !=
Authorisation vulnerability

Nuclei reports CVE
        !=
Confirmed exploitability

sqlmap indicates injection
        !=
Complete impact analysis

Interactsh receives DNS request
        !=
Full SSRF impact established

Burp Scanner reports issue
        !=
Automatically reportable finding
```

Each result requires interpretation.

---

# Confidence Model

A useful result-confidence model is:

| Stage | Meaning |
|---|---|
| Observation | Tool produced interesting behaviour |
| Candidate | Behaviour suggests a security condition |
| Validated | Behaviour reproduced independently |
| Confirmed | Technical condition and impact sufficiently demonstrated |

Example:

```text
Nuclei match
      |
      v
Candidate

Burp reproduction
      |
      v
Validated

Impact demonstrated
      |
      v
Confirmed
```

---

# False Positives

Possible causes include:

- soft 404 pages;
- wildcard routing;
- shared WAF responses;
- generic template matching;
- authentication redirects;
- stale signatures;
- ambiguous response differences.

Always investigate the underlying evidence.

---

# False Negatives

Tools may miss vulnerabilities because of:

- authentication;
- multi-step workflows;
- client-side state;
- business logic;
- WAF behaviour;
- unusual parameters;
- hidden application routes;
- custom protocols.

A clean automated scan does not prove an application is secure.

---

# Tool Chaining

Tools can be connected into efficient workflows.

Example:

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
URLs
    |
    +--> ffuf
    |
    +--> Nuclei
    |
    +--> Burp
```

Another:

```text
Browser
   |
   v
Burp
   |
   v
Interesting Request
   |
   +--> Repeater
   |
   +--> sqlmap
   |
   +--> Interactsh
```

Each transition should have a clear reason.

---

# Practical Web Testing Workflow

A strong workflow can be:

```text
1. Confirm scope
      |
      v
2. Map application
      |
      +-- browser
      +-- Burp
      +-- Katana
      |
      v
3. Establish baselines
      |
      v
4. Discover additional content
      |
      +-- ffuf
      |
      v
5. Run focused automated checks
      |
      +-- Nuclei
      |
      v
6. Investigate parameters
      |
      +-- Repeater
      +-- sqlmap where appropriate
      |
      v
7. Validate blind behaviour
      |
      +-- Interactsh
      |
      v
8. Reproduce findings manually
      |
      v
9. Capture evidence
      |
      v
10. Report
```

---

# Tool Selection Examples

## Need to Understand a Request

Use:

```text
Burp Suite
```

---

## Need to Replay a Request

Use:

```text
Burp Repeater
```

---

## Need to Find Hidden Paths

Use:

```text
ffuf
Katana
```

---

## Need to Crawl Linked Content

Use:

```text
Katana
```

---

## Need Repeatable Known Checks

Use:

```text
Nuclei
```

---

## Need to Validate Suspected SQL Injection

Use:

```text
Burp Repeater
sqlmap
```

---

## Need to Detect an Out-of-Band Callback

Use:

```text
Interactsh
```

---

## Need Simple Raw HTTP Validation

Use:

```text
curl
```

---

# Operational Safety Checklist

Before running automated tooling:

- [ ] Target is in scope.
- [ ] Testing window is valid.
- [ ] Authentication state is understood.
- [ ] Request rate is appropriate.
- [ ] Concurrency is appropriate.
- [ ] Account lockout risk is understood.
- [ ] MFA triggering risk is understood.
- [ ] State-changing actions are understood.
- [ ] Third-party interactions are understood.
- [ ] Scanner templates/options are reviewed.
- [ ] Logs will not expose secrets unnecessarily.

---

# Burp Suite Checklist

- [ ] Browser proxy configured.
- [ ] Correct target scope configured.
- [ ] HTTP history reviewed.
- [ ] Important requests sent to Repeater.
- [ ] Authentication requests identified.
- [ ] Session cookies identified.
- [ ] API calls identified.
- [ ] Relevant extensions selected.
- [ ] Scanner findings manually validated where Professional is used.

---

# ffuf Checklist

- [ ] Random-path baseline established.
- [ ] Wordlist appropriate.
- [ ] Extensions appropriate.
- [ ] Status filtering understood.
- [ ] Size/word/line filtering understood.
- [ ] Soft 404 behaviour considered.
- [ ] Rate controlled.
- [ ] Interesting results manually validated.

---

# Katana Checklist

- [ ] Crawl scope defined.
- [ ] Depth appropriate.
- [ ] Third-party links controlled.
- [ ] JavaScript endpoints considered.
- [ ] Output deduplicated.
- [ ] Important routes manually reviewed.

---

# Nuclei Checklist

- [ ] Target list authorised.
- [ ] Template source trusted.
- [ ] Relevant template categories selected.
- [ ] Scan intensity appropriate.
- [ ] Matchers understood.
- [ ] Important matches reproduced manually.
- [ ] Template severity not treated as final risk rating.

---

# sqlmap Checklist

- [ ] Suspected parameter understood.
- [ ] Request captured accurately.
- [ ] Session maintained.
- [ ] CSRF/state requirements understood.
- [ ] Request volume acceptable.
- [ ] Database interaction risk understood.
- [ ] Result reproduced manually where appropriate.
- [ ] Finding describes injection condition, not tool output.

---

# Interactsh Checklist

- [ ] OOB testing permitted.
- [ ] Unique interaction identifier used.
- [ ] Triggering request retained.
- [ ] Timestamp retained.
- [ ] DNS/HTTP interaction correlated.
- [ ] Third-party interactions understood.
- [ ] Callback interpreted carefully.

---

# Related Tool Sections

[Security Tools](../index.md)

[Web Enumeration Tools](../web-enumeration/index.md)

Detailed tool pages:

[Burp Suite](burp-suite.md)

[ffuf](ffuf.md)

[Nuclei](nuclei.md)

[sqlmap](sqlmap.md)

[Katana](katana.md)

[Interactsh](interactsh.md)

---

# Related Security Notes

[Web Application Security](../../web/index.md)

[Web Application Testing Methodology](../../web/methodology.md)

[Web Application Pentesting Checklist](../../web/checklist.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

[Authentication Testing](../../web/authentication.md)

[Authorisation Testing](../../web/authorisation.md)

[IDOR and BOLA](../../web/idor-bola.md)

[Session Management](../../web/session-management.md)

[SQL Injection](../../web/sql-injection.md)

[Cross-Site Scripting](../../web/xss.md)

[Server Side Request Forgery](../../web/ssrf.md)

[XML External Entity Injection](../../web/xxe.md)

[Server-Side Template Injection](../../web/ssti.md)

[File Upload Security](../../web/file-upload.md)

[API Security](../../web/api-security.md)

[GraphQL API Security](../../web/graphql.md)

[WebSocket Security](../../web/websockets.md)

[Business Logic Vulnerabilities](../../web/business-logic.md)

[Race Conditions](../../web/race-conditions.md)

---

# External References

## PortSwigger

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[Burp Suite BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }

## ffuf

[ffuf - GitHub](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }

## ProjectDiscovery

[Nuclei Documentation](https://docs.projectdiscovery.io/opensource/nuclei/overview){ target="_blank" rel="noopener noreferrer" }

[Katana Documentation](https://docs.projectdiscovery.io/opensource/katana/overview){ target="_blank" rel="noopener noreferrer" }

[Interactsh Documentation](https://docs.projectdiscovery.io/opensource/interactsh/overview){ target="_blank" rel="noopener noreferrer" }

## sqlmap

[sqlmap](https://sqlmap.org/){ target="_blank" rel="noopener noreferrer" }

[sqlmap - GitHub](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }

## General Web Security

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use web-testing tools like this:

```text
Burp
ffuf
Nuclei
sqlmap
Katana
Interactsh
      |
      v
Run everything
      |
      v
Copy results
```

Use them like this:

```text
Understand Application
        |
        v
Choose Testing Question
        |
        v
Choose Appropriate Tool
        |
        v
Perform Focused Test
        |
        v
Observe Behaviour
        |
        v
Interpret Evidence
        |
        v
Validate Independently
        |
        v
Demonstrate Security Impact
        |
        v
Report Defensible Finding
```

The value of these tools is not the amount of output they produce.

Their value is how effectively they help answer a specific security question and support a technically defensible conclusion.
