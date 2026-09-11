---
title: Nuclei
description: Practical Nuclei reference for authorised template-based web and infrastructure testing, including target preparation, template selection, severity filtering, tags, rate control, result validation, false-positive analysis, evidence handling, and integration with wider web application testing methodology.
---

# Nuclei

Nuclei is a template-driven security scanner from ProjectDiscovery.

It is designed to automate checks for known or repeatable security conditions across authorised targets.

Typical uses include:

- known vulnerability checks;
- exposed panels;
- default configurations;
- sensitive file exposure;
- technology-specific checks;
- misconfiguration detection;
- CVE-oriented testing;
- DNS, HTTP, TCP, SSL, file, and other supported template workflows depending on version.

Nuclei is most useful when it is treated as a **candidate discovery tool**.

It can rapidly answer:

> Does this target exhibit behaviour matching this template?

It cannot automatically answer:

> Is this a confirmed, exploitable vulnerability in this environment?

```text
Target
  |
  v
Nuclei Template
  |
  v
Matcher / Extractor
  |
  v
Template Match
  |
  v
Manual Validation
  |
  v
Security Conclusion
```

!!! warning "Authorised testing only"
    Use Nuclei only against systems that are explicitly authorised for testing. Template collections can include high-volume, intrusive, or state-changing checks depending on the selected templates. Review template behaviour, scope, rate, and target sensitivity before execution.

---

# Where Nuclei Fits

Nuclei usually follows asset discovery and technology identification.

```text
Subdomains
    |
    v
httpx
    |
    v
Alive Hosts
    |
    v
Technology / Endpoint Discovery
    |
    v
Nuclei
    |
    v
Candidate Matches
    |
    v
Manual Validation
```

Related tools:

[Web Enumeration Tools](../web-enumeration/index.md)

[httpx](../web-enumeration/httpx.md)

[Katana](katana.md)

[ffuf](ffuf.md)

[Burp Suite](burp-suite.md)

---

# Official Project

Official project:

[Nuclei - GitHub](https://github.com/projectdiscovery/nuclei){ target="_blank" rel="noopener noreferrer" }

Official documentation:

[Nuclei Documentation](https://docs.projectdiscovery.io/tools/nuclei/overview){ target="_blank" rel="noopener noreferrer" }

Official template repository:

[Nuclei Templates - GitHub](https://github.com/projectdiscovery/nuclei-templates){ target="_blank" rel="noopener noreferrer" }

Because Nuclei changes frequently, always verify the exact syntax supported by the installed version:

```bash
nuclei -h
```

---

# Verify Installation

Check the installed version:

```bash
nuclei -version
```

If syntax differs:

```bash
nuclei -h
```

The local help output should be preferred over old examples.

---

# Template Version Matters

Nuclei behaviour depends on both:

```text
Nuclei engine version
```

and:

```text
Template repository version
```

Record both where reproducibility matters.

---

# Update Templates

Nuclei provides mechanisms for maintaining its template collection.

Because exact update syntax may evolve, check:

```bash
nuclei -h
```

and current official documentation.

Do not assume a template set is current simply because the Nuclei binary is current.

---

# Basic Scan

A basic target pattern is:

```bash
nuclei -u https://example.test
```

Depending on configuration and version, Nuclei applies templates available to the engine.

For assessment work, explicit template selection is usually preferable to uncontrolled broad scanning.

---

# Scan from a List

A common workflow is:

```bash
nuclei -l urls.txt
```

Use:

```bash
nuclei -h
```

to confirm exact list-input syntax for the installed version.

---

# Why Target Preparation Matters

Nuclei performs best when input targets are already:

- alive;
- in scope;
- normalized;
- deduplicated.

A useful workflow is:

```text
Subdomain Enumeration
      |
      v
DNS Validation
      |
      v
httpx
      |
      v
alive.txt
      |
      v
Nuclei
```

---

# Example Pipeline

A common reconnaissance chain is conceptually:

```bash
httpx -l subdomains.txt -silent > alive.txt
nuclei -l alive.txt
```

Saving the intermediate host list improves reproducibility.

---

# Do Not Feed Raw Subdomains Blindly

A raw subdomain list may contain:

- dead hosts;
- stale DNS;
- duplicates;
- non-HTTP systems.

Use reachability validation first where the template workflow expects HTTP.

---

# Nuclei Templates

Templates describe the security condition to test.

A template may define:

- protocol;
- request;
- path;
- headers;
- payloads;
- matchers;
- extractors;
- metadata;
- severity;
- tags.

Conceptually:

```text
Template
   |
   +-- Metadata
   +-- Request
   +-- Matchers
   +-- Extractors
   |
   v
Target
   |
   v
Result
```

---

# Template Matchers

Matchers determine whether a response satisfies expected conditions.

Potential matcher concepts include:

- status;
- words;
- regex;
- binary values;
- DSL conditions.

A template match depends heavily on matcher quality.

---

# Extractors

Extractors retrieve interesting data from responses.

Examples may include:

- version strings;
- tokens;
- identifiers;
- response values.

An extracted value is not automatically sensitive.

Interpret it in context.

---

# Severity

Templates commonly use severity labels such as:

```text
info
low
medium
high
critical
```

These labels come from template metadata.

They are not automatically the final risk rating for the target environment.

---

# Template Severity Is Not Final Severity

For example:

```text
Template:
high
```

does not automatically mean:

```text
Pentest finding:
High
```

Final severity should consider:

- exploitability;
- prerequisites;
- target sensitivity;
- available controls;
- actual impact.

---

# Tags

Tags help select template families.

Conceptually:

```text
cve
exposure
misconfig
panel
tech
```

The exact available tags depend on the installed template repository.

Inspect templates rather than assuming a tag exists.

---

# Template Selection

Prefer focused template selection.

A useful model is:

```text
Technology Identified
      |
      v
Relevant Template Family
      |
      v
Focused Nuclei Scan
```

rather than:

```text
Run every template everywhere
```

---

# Technology-Aware Scanning

Suppose reconnaissance identifies:

```text
WordPress
```

A targeted scan against relevant WordPress templates may be more useful than a large unrelated template set.

Similarly:

```text
Exchange
Jenkins
Grafana
Kubernetes
```

should lead to context-specific template selection.

---

# Discovery Before Scanning

A mature workflow is:

```text
WhatWeb / Wappalyzer / httpx
       |
       v
Technology Inventory
       |
       v
Choose Relevant Nuclei Templates
```

Related tools:

[WhatWeb](../web-enumeration/whatweb.md)

[Wappalyzer](../web-enumeration/wappalyzer.md)

[httpx](../web-enumeration/httpx.md)

---

# Template Categories

Common conceptual template categories include:

```text
Known CVEs
Misconfigurations
Exposures
Panels
Default Credentials
Technology Detection
Network Services
SSL / TLS
DNS
```

Some categories can be more intrusive than others.

Review them before use.

---

# Informational Templates

Informational templates can identify:

- technologies;
- services;
- panels;
- metadata.

These are useful for attack-surface enrichment but are not vulnerabilities by default.

---

# Exposure Templates

Exposure-oriented templates may identify:

- configuration files;
- debug endpoints;
- backups;
- source maps;
- internal metadata.

A template match still requires manual confirmation.

---

# CVE Templates

CVE templates aim to test behaviour associated with known vulnerabilities.

Do not report a CVE solely because a template matched.

Confirm:

```text
Product
Version
Affected condition
Response behaviour
Patch status
Exploit prerequisites
```

---

# CVE Match Example

Suppose Nuclei returns:

```text
CVE-20XX-XXXX
```

The next process should be:

```text
Verify target product
      |
      v
Verify affected version / condition
      |
      v
Understand template logic
      |
      v
Reproduce manually
      |
      v
Consult vendor advisory
      |
      v
Confirm finding
```

---

# Vendor Advisories

For known vulnerabilities, prefer the vendor advisory where available.

Use Nuclei as:

```text
Detection mechanism
```

not:

```text
Primary source of vulnerability truth
```

---

# False Positive Risk

Nuclei may produce false positives because of:

- generic matchers;
- custom error pages;
- reverse proxies;
- WAFs;
- version banners;
- shared hosting;
- redirects;
- application rewrites;
- stale templates.

Manual validation is required.

---

# False Negative Risk

Nuclei can also miss vulnerabilities because of:

- custom paths;
- authentication requirements;
- WAF interference;
- altered responses;
- non-default configuration;
- unsupported versions;
- incomplete template coverage.

A clean Nuclei run does not prove the target is secure.

---

# Baseline Behaviour

Before trusting a match, understand the target's normal response.

For HTTP templates inspect:

```text
Status
Headers
Body
Redirects
Content length
Application behaviour
```

This helps distinguish genuine matches from generic responses.

---

# Custom 404 Pages

A custom 404 page may contain words that accidentally satisfy weak template matchers.

Reference:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

Compare the matched path against a random nonexistent path.

---

# Soft 404s

If every random path returns:

```text
HTTP 200
```

with the same application body, exposure templates may produce misleading results.

Use manual validation.

---

# WAF Block Pages

A WAF may return the same block page for many requests.

Example:

```text
403
Access denied
```

A matcher looking only for status or a common phrase may produce false positives.

Compare with normal blocked traffic.

---

# Reverse Proxy Effects

A reverse proxy may:

- rewrite status codes;
- rewrite headers;
- normalize paths;
- serve generic errors.

Understand which layer generated the response.

---

# Authenticated Targets

Some findings only exist after login.

Nuclei supports custom headers and other input mechanisms depending on version.

For authenticated testing, use approved test accounts and protect secrets.

---

# Authorization Header

Conceptual example:

```text
Authorization: Bearer <REDACTED>
```

Use exact current header-input options from:

```bash
nuclei -h
```

Avoid exposing tokens in shell history.

---

# Cookies

Authenticated web applications may require session cookies.

Use:

```text
Cookie: session=<REDACTED>
```

only with approved test sessions.

Session state may expire during long scans.

---

# Role-Specific Testing

Different roles may expose different vulnerabilities.

Example:

```text
Unauthenticated
Normal user
Administrator
```

Keep each scan context separate.

Label evidence clearly.

---

# Template Intrusiveness

Not all templates are equivalent.

Potential behaviour may include:

```text
Simple GET
POST
Special headers
Payload generation
OOB interaction
State-changing request
```

Review high-impact templates before running them.

---

# Read Template Source

Before using a sensitive template:

1. open the YAML;
2. inspect the request;
3. inspect matchers;
4. inspect payloads;
5. identify whether state changes are possible.

Templates are readable security logic.

---

# Safe Default Principle

Prefer:

```text
Read-only or low-impact templates
```

before:

```text
intrusive templates
```

Increase test intensity only when necessary.

---

# Request Volume

Nuclei can generate large volumes of traffic.

Request count depends on:

- number of targets;
- number of templates;
- number of requests per template;
- payload combinations.

Estimate scale before starting.

---

# Rate Limiting

Control request rate according to:

- rules of engagement;
- production sensitivity;
- WAF;
- target capacity.

Consult:

```bash
nuclei -h
```

for current rate-control options.

---

# Concurrency

Higher concurrency improves speed but increases target load.

Do not maximize concurrency by default.

Start conservatively.

---

# 429 Responses

If the target begins returning:

```text
429 Too Many Requests
```

reduce the scanning rate.

Do not try to overwhelm rate controls.

---

# 500 Errors

If scanning causes increasing:

```text
500 Internal Server Error
```

responses:

```text
Stop
Review
Reduce intensity
```

Nuclei scanning is not load testing.

---

# Timeouts

Slow targets may create false negatives if request timeouts are too short.

However, increasing timeouts significantly can make broad scans very slow.

Tune based on target behaviour.

---

# Retries

Retries can improve reliability against unstable connections but increase request volume.

Use them carefully.

---

# Template Workflows

Nuclei supports workflow and chaining concepts depending on version.

These can conditionally run relevant templates based on prior results.

Conceptually:

```text
Detect Technology
      |
      v
Run Relevant Checks
```

This can reduce unnecessary scanning.

Use current official documentation for exact workflow support.

---

# Custom Templates

One of Nuclei's strongest features is custom templates.

Custom templates can encode repeatable checks discovered during an assessment.

Example use cases:

- organisation-specific exposures;
- regression testing;
- known internal misconfiguration;
- recurring response patterns.

---

# Custom Template Workflow

```text
Manual Finding
      |
      v
Understand Exact Behaviour
      |
      v
Write Template
      |
      v
Test Against Known Positive
      |
      v
Test Against Known Negative
      |
      v
Use for Regression
```

---

# Known Positive

A custom template should first be tested against a target known to exhibit the condition.

Confirm:

```text
Expected match occurs
```

---

# Known Negative

Then test against a target known not to exhibit the condition.

Confirm:

```text
No match
```

This helps reduce false positives.

---

# Matcher Quality

Weak matcher:

```text
status == 200
```

Stronger matcher concept:

```text
status == expected
AND
unique response marker exists
AND
known error marker absent
```

Template quality determines scanner quality.

---

# Multiple Match Conditions

When possible, require multiple independent indicators.

For example:

```text
Specific status
+
Unique response string
+
Header
```

This is stronger than one generic word match.

---

# Template Metadata

Useful metadata may include:

```text
name
author
severity
description
reference
tags
```

Keep custom templates well documented.

---

# References in Templates

For known vulnerabilities, include authoritative references such as:

- vendor advisory;
- CVE record;
- original research.

Avoid relying solely on copied blogs.

---

# Template Naming

Use descriptive template names.

Example:

```text
internal-backup-config-exposure
```

instead of:

```text
test123
```

This improves maintenance.

---

# Custom Template Repository

For organisation-specific testing, store approved templates in a controlled repository.

Example:

```text
templates/
├── exposures/
├── misconfigurations/
├── regression/
└── internal/
```

Use version control.

---

# Template Review

Treat Nuclei templates like executable test logic.

Review changes before merging them into shared repositories.

---

# Third-Party Templates

Community templates can be useful but should be trusted carefully.

Before running third-party templates:

- inspect source;
- inspect payloads;
- inspect OOB actions;
- confirm target impact.

Do not blindly run unknown template packs.

---

# Signed Templates

Nuclei has introduced template integrity and signing-related capabilities over time.

Use current official documentation to understand the exact behaviour of the installed version.

Template trust matters when scanning sensitive environments.

---

# Out-of-Band Testing

Some templates may rely on external interaction.

This can support testing for vulnerabilities where the application causes:

- DNS lookup;
- HTTP callback;
- other supported interaction.

Interactsh is commonly used in this context.

Related tool:

[Interactsh](interactsh.md)

---

# OOB Template Model

```text
Nuclei Request
      |
      v
Target
      |
      v
Target Makes Callback
      |
      v
Interactsh
      |
      v
Correlation
```

This can help identify blind server-side behaviour.

---

# OOB Does Not Automatically Mean SSRF

A callback may result from:

- URL fetch;
- XML parser;
- template processing;
- email security scanner;
- asynchronous backend job.

Determine which application component caused it.

---

# DNS Interaction

A DNS lookup proves:

```text
Some component resolved the supplied domain
```

It does not automatically prove:

```text
HTTP access
```

or:

```text
internal network access
```

Interpret the observed interaction accurately.

---

# HTTP Interaction

An HTTP callback provides stronger evidence that a component made an outbound web request.

Still determine:

- source;
- headers;
- timing;
- application function.

---

# Nuclei and Interactsh

A useful workflow is:

```text
Focused Nuclei Template
      |
      v
OOB Payload
      |
      v
Interactsh Interaction
      |
      v
Manual Reproduction
```

Never rely solely on the scanner label.

---

# Nuclei and Katana

Katana can generate a richer URL inventory.

```text
Katana
  |
  v
Discovered URLs
  |
  v
Filter High-Value Targets
  |
  v
Nuclei
```

Related tool:

[Katana](katana.md)

---

# Nuclei and ffuf

ffuf may discover hidden resources.

Then:

```text
ffuf
  |
  v
Hidden Endpoint
  |
  v
Manual Validation
  |
  v
Relevant Nuclei Check
```

Related tool:

[ffuf](ffuf.md)

---

# Nuclei and Burp Suite

Burp is useful for validating Nuclei results manually.

```text
Nuclei Match
      |
      v
Capture Request
      |
      v
Burp Repeater
      |
      v
Modify One Variable
      |
      v
Confirm Behaviour
```

Related tool:

[Burp Suite](burp-suite.md)

---

# Nuclei and sqlmap

Nuclei may identify a candidate SQL-related issue through a template.

Do not automatically hand every parameter to sqlmap.

Instead:

```text
Nuclei candidate
      |
      v
Manual SQLi validation
      |
      v
sqlmap where justified
```

Related tool:

[sqlmap](sqlmap.md)

---

# Nuclei and httpx

A strong broad workflow is:

```text
Subdomains
   |
   v
httpx
   |
   v
Alive Web Hosts
   |
   v
Nuclei
```

httpx helps reduce dead-target noise.

---

# Nuclei and WhatWeb/Wappalyzer

Technology discovery can improve template selection.

```text
Technology
   |
   v
Relevant Templates
   |
   v
Lower Noise
```

This is more efficient than indiscriminate scanning.

---

# Output

Nuclei supports several output formats depending on version.

For reproducible work, structured output is useful.

Check:

```bash
nuclei -h
```

for exact current options.

---

# Plain Output

Plain output is convenient for quick review.

A result may conceptually contain:

```text
template-id
protocol
severity
target
```

Exact formatting varies by version.

---

# JSON Output

Structured JSON output can support:

- ingestion;
- deduplication;
- reporting;
- correlation;
- automation.

Inspect the actual schema produced by your installed version.

---

# Save Results

A practical approach is to preserve:

```text
raw Nuclei output
```

and separately maintain:

```text
validated findings
```

Do not overwrite raw evidence with a manually edited result file.

---

# Result Deduplication

The same underlying issue may match several templates.

Example:

```text
exposed-config
sensitive-file
framework-config-exposure
```

all point to the same file.

Do not report three vulnerabilities.

Consolidate around the root cause.

---

# Duplicate CVE Templates

Different template variants may identify the same CVE.

Use:

```text
one confirmed vulnerability
```

not:

```text
one finding per template match
```

---

# Severity Deduplication

If duplicate templates use different severities, do not select the highest one automatically.

Assess actual risk independently.

---

# Result Prioritisation

A useful triage order may be:

```text
Potential authentication bypass
Remote code execution candidate
Sensitive credential exposure
High-impact misconfiguration
Known CVE
Interesting exposure
Technology information
```

But environment and scope may change priorities.

---

# Informational Noise

Informational results can be valuable during reconnaissance but should not automatically appear in the findings section.

Examples include:

- technology detection;
- server banner;
- panel identification.

Keep them in the attack-surface inventory.

---

# Practical CVE Validation Scenario

Suppose Nuclei returns:

```text
CVE-20XX-YYYY
Target: https://example.test
Severity: high
```

Validation process:

1. open the template;
2. identify the exact request;
3. identify matchers;
4. review vendor advisory;
5. confirm target product;
6. reproduce request manually;
7. compare response against unaffected behaviour;
8. determine actual impact.

Only then report the CVE if supported.

---

# Practical Exposure Scenario

Nuclei reports:

```text
configuration-file
```

on:

```text
https://example.test/.env
```

Validate manually:

```bash
curl -i https://example.test/.env
```

If the response contains actual application configuration, stop unnecessary collection.

Redact secrets.

The finding is:

```text
public exposure of sensitive configuration
```

not:

```text
Nuclei matched a template.
```

---

# Practical Panel Scenario

Nuclei identifies:

```text
administration panel
```

This may simply mean:

```text
/admin
```

exists.

Next determine:

- authentication required;
- intended exposure;
- version disclosure;
- security controls.

An admin panel is not automatically a vulnerability.

---

# Practical Misconfiguration Scenario

Suppose a template reports:

```text
directory listing enabled
```

Validate manually.

If confirmed, determine:

```text
Which files are exposed?

Are they sensitive?

Is indexing intended?
```

The impact depends on exposed content.

---

# Practical OOB Scenario

A template sends a unique external interaction value.

An interaction is observed.

Do not stop at:

```text
callback received
```

Correlate:

```text
request timestamp
callback timestamp
interaction protocol
unique correlation value
application action
```

Then reproduce manually where appropriate.

---

# Result Validation Questions

For every Nuclei result ask:

```text
What exact request caused the match?

Which matcher succeeded?

Could a generic page produce the same result?

Is the product/version correct?

Is authentication required?

Does a WAF or proxy affect the response?

What actual security boundary is crossed?
```

---

# False Positive Example

Template expects:

```text
200
+
"dashboard"
```

The target's generic 404 page contains:

```text
Return to dashboard
```

Result:

```text
Template matches nonexistent path
```

Manual baseline testing reveals the false positive.

---

# False Negative Example

A vulnerable admin endpoint exists at:

```text
/custom-admin/
```

but the template tests only:

```text
/admin/
```

No match occurs.

The application may still be vulnerable.

---

# Authentication False Negative

A template checks only unauthenticated behaviour.

The vulnerable feature exists only for a normal authenticated user.

Nuclei may miss it unless the correct session context is supplied.

---

# Reporting

Avoid:

```text
Nuclei found CVE-20XX-YYYY.
```

Prefer:

```text
The application exhibited the vulnerable behaviour described in
CVE-20XX-YYYY. Manual reproduction confirmed that the affected endpoint
accepted the crafted request and produced the expected vulnerable
response on the tested product version.
```

---

# Reporting an Unconfirmed Match

Example:

```text
Nuclei initially identified a possible exposed configuration file.
Manual validation showed that the matched response was the
application's generic soft-404 page and did not contain configuration
data. The candidate was therefore rejected as a false positive.
```

---

# Reporting a Version-Only Match

Avoid:

```text
Vulnerable because version banner is X.
```

Prefer:

```text
The application disclosed version X. The version may fall within a
published affected range, but vulnerability applicability was not
confirmed through behavioural testing.
```

If version disclosure alone is not a finding, keep it as reconnaissance context.

---

# Reporting a Known Vulnerability

A strong report includes:

```text
Product
Affected version/build
CVE
Vendor advisory
Affected endpoint/component
Prerequisites
Manual reproduction
Observed impact
Remediation
```

Nuclei should be listed as supporting detection evidence if useful.

---

# Remediation

Remediation depends on the underlying issue.

Examples include:

- apply vendor patch;
- upgrade affected software;
- remove exposed configuration;
- disable unused service;
- restrict administration interfaces;
- correct TLS configuration;
- add authentication;
- fix access control.

Do not recommend:

```text
Block Nuclei
```

as the root remediation.

---

# Retesting

After remediation:

```text
Original Manual Test
      |
      v
Expected Safe Behaviour
```

Then optionally:

```text
Nuclei Regression Template
```

Use the manual test as primary validation.

---

# Nuclei for Regression Testing

Nuclei is particularly useful after a confirmed issue has been converted into a reliable custom template.

```text
Finding
   |
   v
Custom Template
   |
   v
Fix
   |
   v
Retest
   |
   v
Future Regression Scan
```

This can support continuous validation.

---

# CI/CD Use

Nuclei can be incorporated into controlled CI/CD or security automation workflows.

Potential use cases include:

- staging checks;
- regression testing;
- known exposure detection.

Avoid automatically launching intrusive template collections against production on every pipeline run.

---

# Template Governance

For organisation-wide automation, define:

```text
Approved template sources
Approved severity/tags
Excluded intrusive templates
Rate limits
Target environment
Exception process
```

This improves predictability.

---

# Production vs Staging

Staging may tolerate:

- broader scans;
- experimental templates;
- more verbose diagnostics.

Production should generally use more conservative, reviewed checks.

---

# Detection and Telemetry

Nuclei activity may be visible through:

- web server logs;
- WAF;
- reverse proxy logs;
- network IDS;
- DNS logs;
- SIEM.

Large template collections can create recognisable request patterns.

---

# Purple Teaming

A controlled Nuclei scan can test:

- vulnerability-scanner detection;
- suspicious path enumeration;
- exploit-attempt visibility;
- WAF response.

```text
Nuclei
  |
  v
HTTP Requests
  |
  v
WAF / Web Logs
  |
  v
SIEM
  |
  v
Detection Review
```

Related section:

[Purple Teaming](../../purple-teaming/index.md)

---

# Detection Should Focus on Behaviour

Blocking the string:

```text
Nuclei
```

or a particular User-Agent may be fragile.

More useful detection may consider:

- unusual path combinations;
- known exploit request structures;
- high request rates;
- suspicious protocol behaviour.

Tool-specific detection can still supplement behavioural coverage.

---

# Operational Safety

Before scanning ask:

```text
How many targets?

How many templates?

How many requests per template?

Are templates state-changing?

Could OOB callbacks leave artefacts?

Can target handle this rate?
```

Estimate scan impact.

---

# High-Risk Templates

Templates involving:

- authentication attempts;
- uploads;
- write operations;
- destructive requests;
- heavy payload sets;

deserve additional review.

Do not assume every community template is safe for production.

---

# Read-Only First

Use:

```text
Technology / Exposure / Low-Impact Checks
```

before:

```text
Intrusive Behavioural Templates
```

unless the engagement specifically requires deeper validation.

---

# Stop Conditions

Stop or reduce scanning if:

- service instability appears;
- 429 responses increase;
- 500 responses increase significantly;
- unexpected data is exposed;
- third-party targets appear;
- security team requests a stop.

---

# Third-Party Scope

Templates may follow or interact with external services.

Always enforce scope.

A discovered SaaS URL is not automatically authorised.

---

# DNS Scope

DNS templates can affect a different set of targets than HTTP templates.

Confirm which domains are authorised for DNS testing.

---

# Network Templates

Nuclei supports non-HTTP protocols through relevant template types.

These can interact directly with:

- TCP services;
- TLS endpoints;
- DNS;
- other supported protocols.

Use only against explicitly authorised hosts and ports.

---

# Host and Port Scope

If scope is defined as:

```text
https://example.test
```

do not automatically assume every network port on the resolved IP is authorised.

Scope definition matters.

---

# Cloud and Shared Infrastructure

A hostname may resolve to:

- CDN;
- shared cloud;
- reverse proxy.

Do not scan unrelated infrastructure based solely on IP ownership or reachability.

---

# Evidence Collection

For each validated Nuclei result, retain:

```text
Target:
Nuclei version:
Template ID:
Template revision/source:
Command:
Timestamp:
Authentication context:
Raw match:
Template request:
Matcher logic:
Manual reproduction:
Vendor reference:
Conclusion:
```

---

# Evidence Example

```text
Target:
https://example.test

Template:
example-config-exposure

Nuclei result:
Template matched /config.json

Manual validation:
Direct GET reproduced the response and confirmed that internal
configuration values were publicly accessible.

Conclusion:
Public exposure of sensitive configuration confirmed.
```

---

# Reproducibility

Record:

```text
Nuclei version
Template version
Target list
Template selection
Rate settings
Authentication context
```

Without these, repeating a scan later may produce different results.

---

# Raw vs Validated Output

Maintain separation:

```text
results/
├── nuclei-raw.json
└── validated-findings.md
```

Raw scanner results are evidence candidates.

Validated findings contain conclusions.

---

# Quick Command Reference

## Help

```bash
nuclei -h
```

## Version

```bash
nuclei -version
```

## Single Target

```bash
nuclei -u https://example.test
```

## Target List

```bash
nuclei -l alive.txt
```

## Pipeline Preparation

```bash
httpx -l subdomains.txt -silent > alive.txt
```

Then:

```bash
nuclei -l alive.txt
```

For exact template, severity, tag, rate, output, and authentication options, always confirm the current syntax with:

```bash
nuclei -h
```

---

# Nuclei Checklist

## Preparation

- [ ] Targets explicitly authorised.
- [ ] Target list validated.
- [ ] Dead targets removed where practical.
- [ ] Nuclei version recorded.
- [ ] Template collection version recorded.
- [ ] Scope documented.
- [ ] Authentication context documented.
- [ ] Production sensitivity understood.

## Template Selection

- [ ] Relevant technology known where possible.
- [ ] Templates selected deliberately.
- [ ] Intrusive templates reviewed.
- [ ] Third-party templates inspected.
- [ ] Custom templates tested against known positives.
- [ ] Custom templates tested against known negatives.

## Rate and Stability

- [ ] Rate selected conservatively.
- [ ] Concurrency appropriate.
- [ ] 429 responses monitored.
- [ ] 500 response spikes monitored.
- [ ] Timeouts appropriate.
- [ ] Scan stopped if instability occurs.

## Authentication

- [ ] Approved test identity used.
- [ ] Tokens/cookies protected.
- [ ] Session expiry monitored.
- [ ] Role-specific scans separated.
- [ ] Secrets excluded from public logs.

## Scope

- [ ] HTTP scope confirmed.
- [ ] DNS scope confirmed where relevant.
- [ ] Host/port scope confirmed.
- [ ] Third-party systems excluded.
- [ ] CDN/shared infrastructure handled carefully.
- [ ] Redirect destinations reviewed.

## Result Validation

- [ ] Exact template reviewed.
- [ ] Request understood.
- [ ] Matcher understood.
- [ ] Extracted values understood.
- [ ] Generic error page ruled out.
- [ ] Soft 404 ruled out.
- [ ] WAF block page ruled out.
- [ ] Product/version confirmed where relevant.
- [ ] Vendor advisory checked for CVEs.
- [ ] Manual reproduction performed.

## OOB

- [ ] Interaction mechanism understood.
- [ ] Unique correlation value used.
- [ ] Timestamp retained.
- [ ] Protocol identified.
- [ ] Callback source interpreted carefully.
- [ ] OOB callback not automatically labelled SSRF.

## Evidence

- [ ] Target retained.
- [ ] Nuclei version retained.
- [ ] Template ID retained.
- [ ] Template source/revision retained.
- [ ] Command retained.
- [ ] Raw output retained.
- [ ] Manual validation retained.
- [ ] Sensitive values redacted.
- [ ] Final conclusion separated from scanner result.

## Reporting

- [ ] Scanner match not treated as root cause.
- [ ] CVE not reported from banner alone.
- [ ] Severity independently assessed.
- [ ] Finding describes actual behaviour.
- [ ] Remediation addresses root cause.
- [ ] Retest criteria explicit.

---

# Template Selection and Result Validation

## Select and Review Templates

Choose templates based on confirmed scope, technology, endpoint behavior, assessment objective, and risk. Record the template source, version or commit, author, tags, severity, variables, request method, matcher, extractor, and whether the template can alter state or generate external interactions. Prefer the official ProjectDiscovery collection or an approved reviewed repository; read the template before using an unfamiliar or intrusive check.

Severity is a prioritisation signal from the template, not the final severity of the finding. A template may match a version, banner, header, default page, or generic response without proving exposure or exploitability in the target context.

## Controlled Scanning

Confirm target scope before every run, exclude third-party infrastructure unless explicitly included, and use conservative rate, concurrency, timeout, retry, and host-error settings. Authenticated scanning should use dedicated least-privilege accounts and approved test data; protect cookies, tokens, and output files.

Interpret matcher and extractor behavior:

```text
Template request
      -> Matcher condition
      -> Extracted value or evidence
      -> Candidate result
      -> Manual reproduction
      -> Security conclusion
```

A matcher may depend on status, word, regex, DSL, headers, body, or a combination. An extractor may only display a value; it does not prove that the value is sensitive or usable. Check generic pages, soft 404s, WAF/CDN responses, redirects, cached content, authentication state, version backports, and template assumptions before accepting a result.

## Manual Validation and Evidence

Read the template and reproduce the request with Burp Suite, `curl`, the relevant client, or another approved tool. Establish a baseline, change one condition where appropriate, and validate the smallest non-destructive proof. Confirm product/version, configuration, authorization, reachability, and impact with a safe read-back or owner-approved test.

Capture target and scope, template path and hash or commit, Nuclei version, command options, timestamp, request and response with secrets redacted, matcher or extractor that fired, baseline comparison, manual validation, and evidence of the actual security consequence. A Nuclei match is a candidate, not an automatic vulnerability.

## Troubleshooting, Remediation, and Retesting

For inconsistent results, check template version, target normalization, redirects, virtual hosts, TLS verification, rate limits, authentication headers, cookies, WAF behavior, concurrency, retries, and whether the response came from a shared cache or intermediary. Run the template alone at low rate and compare the raw response with a manual request.

Use the vendor advisory, product configuration, or application owner to remediate the underlying weakness. Retest with the same template version and options, then manually confirm the old response is absent or the vulnerable behavior is no longer reachable. Run a relevant neighboring template or manual check to detect a narrow fix without treating unrelated matches as proof.

# Related Tool Notes

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

[ffuf](ffuf.md)

[Katana](katana.md)

[sqlmap](sqlmap.md)

[Interactsh](interactsh.md)

---

# Related Enumeration Tools

[Web Enumeration Tools](../web-enumeration/index.md)

[WhatWeb](../web-enumeration/whatweb.md)

[Wappalyzer](../web-enumeration/wappalyzer.md)

[httpx](../web-enumeration/httpx.md)

---

# Related Web Notes

[Web Application Security](../../web/index.md)

[Web Testing Methodology](../../web/methodology.md)

[Web Security Checklist](../../web/checklist.md)

[API Security](../../web/api-security.md)

[Authentication Testing](../../web/authentication.md)

[Authorisation Testing](../../web/authorisation.md)

[Server Side Request Forgery](../../web/ssrf.md)

---

# Related Purple Team Notes

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

[Continuous Validation](../../purple-teaming/continuous-validation.md)

---

# External References

## Nuclei

[Nuclei - GitHub](https://github.com/projectdiscovery/nuclei){ target="_blank" rel="noopener noreferrer" }

[Nuclei Documentation](https://docs.projectdiscovery.io/tools/nuclei/overview){ target="_blank" rel="noopener noreferrer" }

[Nuclei Templates - GitHub](https://github.com/projectdiscovery/nuclei-templates){ target="_blank" rel="noopener noreferrer" }

## ProjectDiscovery

[ProjectDiscovery Documentation](https://docs.projectdiscovery.io/){ target="_blank" rel="noopener noreferrer" }

## Vulnerability References

[CVE Program](https://www.cve.org/){ target="_blank" rel="noopener noreferrer" }

[NIST National Vulnerability Database](https://nvd.nist.gov/){ target="_blank" rel="noopener noreferrer" }

## Practical References

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use Nuclei like this:

```text
Run All Templates
      |
      v
Receive Match
      |
      v
Copy Severity
      |
      v
Report Vulnerability
```

Use it like this:

```text
Confirm Scope
      |
      v
Prepare Valid Targets
      |
      v
Understand Technology
      |
      v
Select Relevant Templates
      |
      v
Review Intrusive Behaviour
      |
      v
Run Controlled Nuclei Scan
      |
      v
Identify Template Match
      |
      v
Read Template
      |
      v
Understand Request and Matcher
      |
      v
Rule Out Generic / WAF / Soft-404 Behaviour
      |
      v
Validate Product and Version
      |
      v
Consult Vendor Advisory Where Relevant
      |
      v
Reproduce Manually
      |
      v
Determine Actual Security Impact
      |
      v
Capture Evidence
      |
      v
Report Underlying Weakness
```

Nuclei is most valuable as a fast and repeatable way to identify security conditions that deserve deeper validation.

The template provides the hypothesis.

The target behaviour and manual evidence determine whether a real vulnerability exists.
