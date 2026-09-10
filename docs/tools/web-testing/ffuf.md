---
title: ffuf
description: Practical ffuf reference for authorised web content discovery, endpoint enumeration, virtual host discovery, parameter fuzzing, request replay, filtering, response analysis, evidence collection, and integration with wider web application testing methodology.
---

# ffuf

ffuf is a fast web fuzzer commonly used for authorised web application discovery and content enumeration.

It is especially useful for:

- directory discovery;
- file discovery;
- endpoint discovery;
- virtual host discovery;
- parameter-name discovery;
- parameter-value testing;
- extension discovery;
- API path discovery;
- replaying customised HTTP requests.

ffuf works by replacing a marker, usually:

```text
FUZZ
```

with values from a wordlist.

A basic model is:

```text
Target
  |
  v
Request Template
  |
  v
FUZZ Position
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
Interesting Candidates
```

!!! warning "Authorised testing only"
    Use ffuf only against applications and infrastructure that are explicitly authorised for testing. High request rates can affect production systems, trigger rate limiting, create large log volumes, or cause service instability. Start conservatively and increase speed only where appropriate.

---

# Where ffuf Fits

ffuf usually sits after initial reconnaissance and before deeper manual validation.

```text
Target Identified
      |
      v
Baseline Request
      |
      v
ffuf Discovery
      |
      v
Interesting Endpoint
      |
      v
Manual Validation
      |
      v
Burp / Browser Testing
```

Related notes:

[Web Application Testing Tools](index.md)

[Web Enumeration Tools](../web-enumeration/index.md)

[Burp Suite](burp-suite.md)

---

# Official Project

Official project:

[ffuf - GitHub](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }

Use the current official documentation and:

```bash
ffuf -h
```

to confirm exact options supported by the installed version.

---

# Verify Installation

Check:

```bash
ffuf -V
```

or:

```bash
ffuf -h
```

depending on the installed release.

On Kali Linux, ffuf is commonly available through the package manager or may already be installed.

---

# Basic Concept

Suppose the target is:

```text
https://example.test/FUZZ
```

and the wordlist contains:

```text
admin
login
api
uploads
```

ffuf sends requests conceptually like:

```text
https://example.test/admin
https://example.test/login
https://example.test/api
https://example.test/uploads
```

The task is then to distinguish meaningful responses from noise.

---

# Basic Directory Discovery

A common starting point is:

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ
```

This replaces:

```text
FUZZ
```

with each word from the wordlist.

---

# Wordlists

Wordlist quality strongly affects discovery quality.

Useful categories include:

```text
Common directories
Technology-specific paths
API endpoints
Administrative names
Backup filenames
Framework-specific locations
```

Do not rely on one giant wordlist for every application.

Targeted wordlists are often more effective.

---

# SecLists

SecLists is a widely used collection of security testing wordlists.

Official project:

[SecLists - GitHub](https://github.com/danielmiessler/SecLists){ target="_blank" rel="noopener noreferrer" }

Common categories include:

```text
Discovery/Web-Content/
Fuzzing/
Usernames/
Passwords/
```

Use only wordlists appropriate to the authorised task.

---

# Start with a Baseline

Before fuzzing, understand how the application responds to:

```text
Valid path
Invalid path
Trailing slash
Random filename
```

For example:

```bash
curl -i https://example.test/this-should-not-exist-834729
```

This helps identify:

- normal 404 behaviour;
- soft 404s;
- redirects;
- custom error pages;
- wildcard routing.

Without a baseline, ffuf results can be misleading.

---

# Default 404 Pages

Default server error pages can sometimes help identify technology.

For visual comparison, see:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

Do not rely on appearance alone.

Validate with headers, content, and other fingerprints.

---

# Soft 404s

A soft 404 occurs when a nonexistent resource returns something like:

```text
200 OK
```

instead of:

```text
404 Not Found
```

Example:

```text
GET /totally-random-12345

HTTP/1.1 200 OK
Content-Length: 4210
```

If every missing resource produces the same body, ffuf may report many false positives.

---

# Establish Random Baseline

Use a random path:

```bash
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://example.test/random-834723984
```

Then compare ffuf results against that baseline.

---

# Status Code Filtering

ffuf can filter or match responses by HTTP status.

Because exact flags evolve, confirm current syntax using:

```bash
ffuf -h
```

Typical analysis categories include:

```text
200
204
301
302
307
401
403
405
500
```

Interesting status does not automatically mean vulnerability.

---

# Response Size

Response size is one of the most useful ways to remove false positives.

If nonexistent paths consistently return:

```text
Content-Length: 4242
```

then responses with that size may represent the custom error page.

Use ffuf response-size filtering according to the current help output.

---

# Word Count

Applications may return pages of similar byte length but different word counts.

Word count can therefore be useful when filtering repeated error templates.

---

# Line Count

Line count may also help distinguish:

```text
Real page
```

from:

```text
Standard error response
```

Use multiple response characteristics rather than relying on one field.

---

# Auto-Calibration

ffuf supports calibration features intended to help identify repetitive false-positive responses.

Consult:

```bash
ffuf -h
```

for the exact options supported by the installed version.

Calibration can be useful against:

- wildcard routes;
- virtual host defaults;
- soft 404s.

Always inspect a sample manually.

---

# Recursion

ffuf can perform recursive discovery depending on configuration.

Conceptually:

```text
/
 |
 +-- admin/
 |     |
 |     +-- users/
 |
 +-- api/
       |
       +-- v1/
```

Recursion can create significant request volume.

Use it carefully.

---

# Directory Discovery Workflow

A strong process is:

```text
Baseline
   |
   v
Small Wordlist
   |
   v
Review Results
   |
   v
Technology-Specific Wordlist
   |
   v
Manual Validation
```

Avoid immediately using the largest possible list.

---

# File Discovery

ffuf can also discover filenames.

Example concept:

```text
https://example.test/FUZZ
```

Wordlist:

```text
config.php
backup.zip
robots.txt
sitemap.xml
```

Any discovered file should be reviewed according to scope and sensitivity.

---

# Extensions

Applications may expose files under technology-specific extensions.

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

Extension fuzzing should be based on observed technology.

Do not blindly test every extension.

---

# Extension Discovery Strategy

A useful process is:

```text
Technology Fingerprint
       |
       v
Likely File Types
       |
       v
Targeted Extension Testing
```

For example, an ASP.NET application deserves different guesses from a PHP application.

---

# Multiple Extensions

Depending on the installed version, ffuf supports extension expansion.

Check exact syntax using:

```bash
ffuf -h
```

Keep the extension list focused.

---

# Trailing Slash Differences

These may behave differently:

```text
/admin
```

and:

```text
/admin/
```

Framework routing and reverse proxies may treat them differently.

Test both when results are ambiguous.

---

# Redirects

A discovered path may return:

```text
301
302
307
308
```

Follow-up questions include:

```text
Where does it redirect?

Is destination in scope?

Does redirect reveal canonical path?

Is authentication involved?
```

Do not automatically follow redirects to third-party domains during automated testing.

---

# Authentication

Many interesting endpoints require authentication.

ffuf can send custom headers.

Example:

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ -H "Cookie: session=<REDACTED>"
```

Protect authentication material.

Do not save live session values in public notes or shell history unnecessarily.

---

# Authorization Header

For API testing:

```bash
ffuf -w wordlist.txt -u https://example.test/api/FUZZ -H "Authorization: Bearer <REDACTED>"
```

Ensure the token belongs to an approved test identity.

---

# Custom Headers

Custom headers may be necessary for:

- authentication;
- API versioning;
- content negotiation;
- virtual hosts;
- application routing.

Example:

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ -H "Accept: application/json"
```

---

# User-Agent

Some environments behave differently based on User-Agent.

If necessary:

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ -H "User-Agent: authorised-security-test"
```

Only add custom identification if this aligns with the engagement.

---

# POST Requests

ffuf can fuzz request bodies.

Example:

```bash
ffuf -w wordlist.txt -u https://example.test/api/search -X POST -H "Content-Type: application/json" -d '{"query":"FUZZ"}'
```

This sends each wordlist value in the JSON field.

Use controlled values.

---

# Form Data

Example:

```bash
ffuf -w values.txt -u https://example.test/search -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "q=FUZZ"
```

This can help test application behaviour around known input locations.

---

# Parameter Name Discovery

ffuf can be used to identify hidden parameter names.

Conceptually:

```text
GET /endpoint?FUZZ=test
```

Wordlist:

```text
debug
admin
redirect
callback
format
```

A discovered parameter is not automatically security relevant.

The next step is to understand what it controls.

---

# GET Parameter Example

```bash
ffuf -w parameters.txt -u 'https://example.test/page?FUZZ=test'
```

Compare responses for:

- status;
- size;
- content;
- headers;
- timing.

---

# Parameter Value Testing

If a known parameter accepts a set of possible values:

```bash
ffuf -w values.txt -u 'https://example.test/page?mode=FUZZ'
```

This can reveal:

- hidden modes;
- alternate formats;
- undocumented states.

Do not confuse functionality discovery with vulnerability confirmation.

---

# API Endpoint Discovery

ffuf is useful against API route structures.

Example:

```bash
ffuf -w api-endpoints.txt -u https://api.example.test/FUZZ
```

Potential findings may include:

```text
/api/v1/users
/api/v1/admin
/api/v2
/swagger
/openapi.json
```

Manually validate all interesting responses.

---

# API Baseline

APIs may return identical JSON for unknown routes.

Example:

```json
{
  "error": "Not found"
}
```

with:

```text
HTTP 200
```

This is another soft-404 pattern.

Filter based on body characteristics.

---

# JSON Responses

Do not rely only on byte length.

Inspect:

- response fields;
- status;
- error codes;
- headers;
- semantic differences.

A one-field difference may be important even when total size remains similar.

---

# Swagger and OpenAPI

Discovery may identify documentation paths such as:

```text
/swagger
/swagger-ui
/openapi.json
/api-docs
```

These can help map the application attack surface.

API documentation exposure is not automatically a vulnerability.

Assess whether it exposes sensitive internal information or simply documents intended public APIs.

---

# GraphQL

A GraphQL application may expose endpoints such as:

```text
/graphql
/api/graphql
```

ffuf can help discover likely locations.

GraphQL security assessment then requires GraphQL-specific methodology.

Related note:

[GraphQL](../../web/graphql.md)

---

# Virtual Host Discovery

Virtual host fuzzing attempts to identify additional hostnames served by the same IP or reverse proxy.

Conceptually:

```text
Host: FUZZ.example.test
```

while sending requests to the same server.

---

# VHost Example

A typical pattern is:

```bash
ffuf -w subdomains.txt -u https://example.test/ -H "Host: FUZZ.example.test"
```

This assumes the target server and domain are authorised.

Use an appropriate baseline because wildcard virtual hosts can create false positives.

---

# VHost Baseline

First test a random hostname:

```bash
curl -k -i https://example.test/ -H "Host: random-does-not-exist.example.test"
```

Record:

- status;
- length;
- title;
- body;
- redirect.

Then compare ffuf output.

---

# TLS and Virtual Hosts

HTTPS virtual host discovery can be complicated by:

- SNI;
- certificates;
- reverse proxies;
- load balancers.

The HTTP `Host` header and TLS SNI are related but separate concepts.

A request may reach one TLS virtual host and then supply a different HTTP host value.

Interpret results carefully.

---

# Wildcard Virtual Hosts

Some servers respond successfully for any hostname.

Example:

```text
foo.example.test -> same page
bar.example.test -> same page
random123.example.test -> same page
```

This creates false positives.

Compare:

- body size;
- title;
- headers;
- TLS;
- application behaviour.

---

# Host Header Testing

Virtual host discovery should not be confused with Host header vulnerability testing.

Discovery asks:

```text
Which virtual hosts exist?
```

Host header security testing asks:

```text
Does the application trust an attacker-controlled Host value in a
security-sensitive operation?
```

Related note:

[Host Header Attacks](../../web/host-header-attacks.md)

---

# Request Files

For complex requests, ffuf can work with request templates depending on the installed version and selected options.

This can be useful when reproducing requests from:

- Burp Suite;
- API clients;
- browser traffic.

Check:

```bash
ffuf -h
```

for the exact request-file functionality available.

---

# Burp Suite Integration

A strong workflow is:

```text
Burp
  |
  v
Capture Valid Request
  |
  v
Identify Fuzz Position
  |
  v
ffuf
  |
  v
Interesting Responses
  |
  v
Burp Repeater
```

ffuf provides scale.

Burp provides manual validation.

---

# Proxying Through Burp

For selected debugging workflows, ffuf traffic can be routed through an HTTP proxy if the current version supports the relevant proxy option.

Use:

```bash
ffuf -h
```

to confirm exact syntax.

This can help inspect unusual requests manually.

Do not send large fuzzing campaigns through Burp unless necessary.

---

# Match vs Filter

ffuf generally provides two conceptual approaches:

```text
Match interesting responses
```

or:

```text
Filter known noise
```

Filtering known baseline responses is often more effective against custom error pages.

---

# Filtering Philosophy

Suppose all invalid pages return:

```text
200
Size: 5301
Words: 842
Lines: 97
```

A useful approach is to filter that known response fingerprint.

Interesting results then stand out.

---

# Do Not Filter Too Aggressively

If you filter:

```text
Size 5301
```

but a real endpoint happens to have the same size, it may disappear from results.

Use multiple observations and spot-check manually.

---

# Response Timing

Timing differences can sometimes indicate:

- backend processing;
- database interaction;
- authentication logic;
- rate limiting.

However, network timing is noisy.

Do not treat timing differences alone as proof of functionality or vulnerability.

---

# Rate Limiting

ffuf can generate requests very quickly.

This may trigger:

- WAF;
- rate limiting;
- application throttling;
- account controls;
- infrastructure load.

Start conservatively.

---

# Threads / Concurrency

Higher concurrency means more simultaneous requests.

The correct setting depends on:

- target stability;
- network latency;
- engagement rules;
- WAF;
- production sensitivity.

Do not maximise concurrency by default.

---

# Delay

Some versions support request delays or rate controls.

Use:

```bash
ffuf -h
```

for current syntax.

A lower request rate may be necessary against fragile systems.

---

# WAF Interaction

A WAF may begin blocking ffuf traffic after repeated requests.

Symptoms may include:

```text
403 responses
429 responses
connection resets
challenge pages
same block page for every request
```

If this occurs, stop and understand the control.

Do not automatically attempt evasion.

---

# 429 Too Many Requests

A `429` response usually indicates rate limiting.

Treat this as an operational signal.

Reduce the request rate according to scope and engagement requirements.

Do not try to overwhelm the limit.

---

# 403 Responses

A `403 Forbidden` result can still be interesting.

It may indicate:

```text
Real endpoint exists
but
access denied
```

However, some WAFs also return 403 for generic invalid requests.

Compare against baseline.

---

# 401 Responses

A `401 Unauthorized` response often indicates an authentication-protected resource.

Useful follow-up:

```text
Which authentication mechanism?

Is the path expected?

Does current test account have access?
```

---

# 405 Responses

`405 Method Not Allowed` may indicate that the endpoint exists but does not accept the current HTTP method.

Manual testing with allowed methods may be appropriate.

Do not randomly submit state-changing methods.

---

# 500 Responses

A `500 Internal Server Error` deserves review.

But:

```text
500
```

does not automatically mean:

```text
vulnerability
```

It may indicate:

- invalid application input;
- backend error;
- WAF behaviour;
- temporary instability.

Reproduce carefully.

---

# Wordlist Selection

Wordlists should reflect context.

For example:

```text
Apache / PHP app
```

might justify different candidate paths from:

```text
ASP.NET application
```

or:

```text
REST API
```

Use reconnaissance to inform discovery.

---

# Technology-Guided Discovery

A good chain is:

```text
WhatWeb / Wappalyzer
       |
       v
Technology Identified
       |
       v
Technology-Specific Wordlist
       |
       v
ffuf
```

Related tools:

[WhatWeb](../web-enumeration/whatweb.md)

[Wappalyzer](../web-enumeration/wappalyzer.md)

---

# JavaScript-Guided Discovery

JavaScript may reveal:

- route names;
- API versions;
- endpoint fragments;
- feature names.

These can be converted into a focused wordlist.

Related note:

[JavaScript Analysis](../../reconnaissance/javascript-analysis.md)

---

# robots.txt

Always review:

```text
/robots.txt
```

before brute-force discovery.

It may disclose:

- administrative paths;
- staging content;
- crawler exclusions.

A listed path is not automatically sensitive.

---

# sitemap.xml

Review:

```text
/sitemap.xml
```

and related sitemap files.

These can provide intended application routes without fuzzing.

Use deterministic discovery before brute force where possible.

---

# Historical URLs

Historical application URLs can also provide valuable candidate paths.

Sources may include:

- documentation;
- archived application versions;
- known route naming;
- previous reconnaissance.

Only test the current authorised target.

---

# Backups

Potential backup filenames may include variations such as:

```text
config.bak
index.php.old
backup.zip
site.tar.gz
```

Discovery of backup files can expose sensitive data.

Do not download large archives unnecessarily.

First validate:

- file exists;
- size;
- sensitivity;
- scope.

---

# Source Control Files

Interesting locations may include:

```text
.git/
.svn/
```

If exposed, they may disclose source or metadata.

Do not recursively download repository contents unless needed and authorised.

The exposure itself may already be demonstrable with minimal evidence.

---

# Configuration Files

Potentially sensitive files can include:

```text
.env
web.config
application.properties
config.yml
```

Handle carefully.

If a response contains secrets:

- stop unnecessary collection;
- redact evidence;
- follow disclosure procedures.

---

# Wordlist Mutation

Application-specific terms can improve discovery.

For example:

```text
invoice
invoices
invoice-api
invoice_admin
invoice-v2
```

Generate focused mutations based on known naming conventions rather than massive blind lists.

---

# Case Sensitivity

Some servers treat:

```text
/admin
```

and:

```text
/Admin
```

differently.

This depends on:

- operating system;
- web server;
- framework;
- routing.

Only test variants where justified.

---

# URL Encoding

Applications may normalise encoded paths differently.

Do not broadly fuzz encoding tricks unless that is part of the specific testing objective.

For ordinary content discovery, use canonical paths first.

---

# Duplicate Routes

Different paths may map to the same application handler.

Example:

```text
/login
/signin
/auth/login
```

Treat them as separate attack-surface entries initially, then consolidate if behaviour is identical.

---

# Endpoint Inventory

A useful ffuf result inventory may contain:

| Path | Status | Size | Notes |
|---|---:|---:|---|
| `/admin/` | 403 | 1250 | Review manually |
| `/api/` | 200 | 431 | JSON response |
| `/old/` | 301 | 0 | Redirect |
| `/health` | 200 | 82 | Health endpoint |

The table is only a triage view.

---

# Save Output

ffuf supports output files and several formats depending on the version.

Check:

```bash
ffuf -h
```

for current options.

Structured output is useful for:

- automation;
- deduplication;
- reporting;
- later analysis.

---

# JSON Output

Where supported, JSON output is useful for scripting.

A processing workflow might be:

```text
ffuf
  |
  v
JSON
  |
  v
jq / Python
  |
  v
Interesting Endpoint List
```

---

# jq

`jq` is useful for processing JSON results.

Example concept:

```bash
jq '.results[]' ffuf-results.json
```

The exact JSON structure should be inspected first.

---

# Python Processing

For larger assessments, Python can help:

- merge results;
- remove duplicates;
- normalise URLs;
- classify status codes;
- produce reports.

Automation should not silently convert all results into findings.

---

# Deduplication

If ffuf discovers:

```text
/admin
/admin/
/admin/index
```

they may represent the same underlying application area.

Keep raw discovery data, then consolidate during analysis.

---

# Multiple Hosts

For multiple targets, avoid blindly running the same aggressive wordlist against every system.

A better workflow is:

```text
httpx inventory
      |
      v
Group by technology
      |
      v
Select wordlist
      |
      v
ffuf each target
```

Related tool:

[httpx](../web-enumeration/httpx.md)

---

# Per-Host Baselines

Each host may have different error behaviour.

Do not assume:

```text
404 size on host A
```

matches:

```text
404 size on host B
```

Calibrate each application separately.

---

# Virtual Hosting and CDN

A CDN or reverse proxy may cause many hostnames to return the same response.

This is particularly common during virtual host discovery.

Validate with:

- body;
- title;
- cookies;
- backend-specific headers;
- TLS;
- application behaviour.

---

# Reverse Proxies

Reverse proxies may rewrite:

- paths;
- status codes;
- redirects;
- Host headers.

This can make content discovery results look inconsistent.

Understand architecture where possible.

---

# Authentication State

Discovery results can differ significantly between:

```text
Unauthenticated user
Normal user
Administrator
```

Run separate discovery only where authorised and useful.

Label the session context in evidence.

---

# Role-Aware Discovery

Example:

```text
Normal User
     |
     v
/admin -> 403

Administrator
     |
     v
/admin -> 200
```

This may simply reflect correct access control.

It is useful attack-surface information, not necessarily a vulnerability.

---

# Session Expiry

Long ffuf runs may outlive an authenticated session.

Symptoms include many sudden:

```text
302 -> /login
```

or:

```text
401
```

responses.

Confirm the session is still valid before interpreting results.

---

# CSRF-Protected Requests

Some POST endpoints require dynamic CSRF tokens.

ffuf is less convenient when every request requires a fresh token.

In such cases:

- Burp extensions;
- custom scripts;
- application-specific tooling;

may be more appropriate.

Choose the right tool.

---

# Stateful Workflows

ffuf works best when requests are relatively independent.

Complex workflows such as:

```text
Create object
Get token
Submit step 2
Approve step 3
```

usually require custom automation or manual testing.

Do not force ffuf into workflows it does not fit well.

---

# Content Discovery vs Vulnerability Testing

Keep these stages separate.

```text
ffuf discovers:
 /admin
```

This means:

```text
Interesting endpoint identified
```

not:

```text
Access control vulnerability
```

The next stage determines whether security controls work correctly.

---

# Practical Directory Discovery Scenario

Suppose the baseline invalid response is:

```text
Status:
200

Size:
4137

Title:
Page Not Found
```

Run discovery:

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ
```

Then filter the known baseline response using the appropriate current ffuf option.

Interesting result:

```text
admin
Status: 403
Size: 729
```

Now manually validate:

```bash
curl -i https://example.test/admin
```

Interpretation:

```text
The /admin path appears to exist but access is forbidden to the current
request context.
```

Do not report a vulnerability yet.

---

# Practical API Scenario

Target:

```text
https://example.test/api/FUZZ
```

Run:

```bash
ffuf -w api.txt -u https://example.test/api/FUZZ -H "Accept: application/json"
```

Possible result:

```text
users     [Status: 401]
health    [Status: 200]
v1        [Status: 200]
internal  [Status: 403]
```

Next steps:

- inspect each response manually;
- understand authentication;
- determine whether endpoint exposure is intended.

---

# Practical Parameter Scenario

Known endpoint:

```text
https://example.test/report
```

Test parameter names:

```bash
ffuf -w parameters.txt -u 'https://example.test/report?FUZZ=test'
```

Suppose:

```text
format
```

changes the response.

Next:

```text
Determine accepted values
Understand server-side behaviour
Validate whether it creates a security-relevant path
```

---

# Practical Virtual Host Scenario

Known server:

```text
10.20.30.40
```

Known domain:

```text
example.test
```

Before fuzzing, establish wildcard behaviour using a random host value.

Then use an authorised vhost wordlist against the same target.

If:

```text
admin.example.test
```

returns a clearly different application response, validate it manually and add it to the authorised inventory if the scope definition includes such subdomains.

---

# Practical Authenticated Scenario

Capture a test-account session.

Run a focused endpoint list using the approved authentication header.

Then repeat only where necessary under another approved role.

Compare:

```text
Path
Status
Response
Role
```

This can identify role-specific attack surface.

Do not use ffuf as a substitute for detailed authorisation testing.

---

# False Positives

Common causes include:

- soft 404s;
- wildcard routes;
- WAF block pages;
- CDN defaults;
- redirects;
- authentication expiry;
- application catch-all routing;
- wildcard virtual hosts.

Always establish baseline behaviour.

---

# False Negatives

ffuf may miss resources because of:

- poor wordlists;
- case sensitivity;
- alternate extensions;
- authenticated-only routes;
- dynamic routing;
- JavaScript-generated paths;
- required headers;
- required HTTP methods;
- stateful workflows.

A clean ffuf result does not prove no hidden content exists.

---

# Troubleshooting No Results

Check:

```text
Correct URL?
FUZZ marker present?
DNS works?
TLS issue?
Proxy issue?
Wordlist valid?
Application reachable?
Filtering too aggressive?
```

Test one known value manually.

---

# Troubleshooting Too Many Results

Common causes:

```text
Soft 404
Wildcard routing
Generic 200 response
WAF block page
```

Use random baseline requests and compare:

- status;
- size;
- words;
- lines;
- body.

---

# TLS Errors

In authorised lab environments, certificate issues may arise from:

- self-signed certificates;
- internal PKI;
- test domains.

Use ffuf's current TLS-related options only when appropriate and verify syntax via:

```bash
ffuf -h
```

Do not disable certificate verification by default without understanding why.

---

# DNS Problems

Confirm:

```bash
dig example.test
```

or:

```bash
nslookup example.test
```

If using a lab-only domain, ensure the host resolves through:

- DNS;
- authorised hosts-file configuration.

---

# Proxy Problems

If using a proxy:

- confirm proxy address;
- confirm TLS handling;
- confirm target reachability;
- verify the proxy is not changing responses.

Compare one request directly and through the proxy.

---

# Request Reproducibility

For an interesting result, preserve a simple reproducible request.

Example:

```bash
curl -i https://example.test/admin
```

This is easier to include in evidence than relying solely on ffuf output.

---

# Evidence Collection

For significant discoveries, retain:

```text
Target:
Wordlist:
ffuf version:
Command:
Authentication context:
Baseline response:
Interesting path:
Status:
Response characteristics:
Timestamp:
Manual validation:
```

Do not retain unnecessary live credentials.

---

# Evidence Example

```text
Target:
https://example.test/

Current context:
Unauthenticated

Discovery:
ffuf content enumeration

Candidate:
/internal/

Response:
HTTP 403

Manual validation:
Direct GET reproduced the 403 response.

Conclusion:
The path appears to exist but access was denied to the unauthenticated
request context.
```

This is defensible and does not overstate the result.

---

# Reporting

ffuf is usually a discovery tool rather than the root cause of a finding.

Avoid:

```text
ffuf found a vulnerability.
```

Prefer:

```text
Content discovery identified an unauthenticated administrative endpoint
that exposed sensitive application configuration without requiring
authentication.
```

The vulnerability is the exposed behaviour.

---

# Reporting Hidden Endpoint Exposure

If an undocumented endpoint is discovered but securely protected:

```text
No vulnerability may exist.
```

Hidden is not equivalent to secure or insecure.

Evaluate actual access controls and information exposure.

---

# Reporting Sensitive File Exposure

If ffuf discovers a readable configuration backup:

```text
The application exposed a backup configuration file beneath the public
web root. The file was retrievable without authentication and contained
sensitive deployment information.
```

The issue is the exposed file.

---

# Reporting Directory Listing

If a discovered directory exposes file indexes:

```text
Directory indexing was enabled on the affected path, allowing
unauthenticated users to enumerate files stored within the directory.
```

Again, the finding describes server behaviour.

---

# Remediation

Remediation depends on the actual discovered condition.

Potential controls include:

- remove obsolete files;
- move sensitive files outside web root;
- disable directory listing;
- enforce authentication;
- enforce authorisation;
- remove backup artefacts;
- disable unused endpoints;
- configure reverse proxy routing correctly.

Do not recommend:

```text
Block ffuf
```

as the primary remediation.

---

# Detection Considerations

High-volume content discovery may be visible through:

- web server logs;
- WAF;
- reverse proxy;
- IDS;
- SIEM.

Patterns may include:

```text
Large number of unique paths
Short time window
Same source IP
Repeated 404/403 responses
```

This can be useful during purple-team exercises.

---

# Purple Teaming

A controlled ffuf exercise can validate web discovery detection.

```text
Approved ffuf Run
      |
      v
Web / WAF Logs
      |
      v
SIEM
      |
      v
Detection Review
```

Use a controlled wordlist and agreed request rate.

Related note:

[Purple Teaming](../../purple-teaming/index.md)

---

# Operational Safety

Before starting a larger run ask:

```text
Is this production?

What rate is acceptable?

Could requests trigger expensive backend operations?

Could authentication attempts lock accounts?

Does the wordlist contain destructive route names?
```

Discovery should minimise application state changes.

---

# Avoid State-Changing Paths

A GET request should ideally be safe, but poorly designed applications may expose state-changing behaviour over GET.

If unusual effects are observed:

```text
Stop
Document
Validate manually
```

Do not continue brute forcing blindly.

---

# Destructive Endpoint Risk

Avoid automatically sending methods such as:

```text
DELETE
PUT
PATCH
```

across unknown paths.

Use passive or read-only discovery first.

---

# Large Wordlists

Very large wordlists can:

- consume hours;
- create excessive traffic;
- increase log noise;
- provide diminishing returns.

Use staged discovery.

---

# Staged Discovery

A strong model is:

```text
Small Common List
      |
      v
Interesting Results
      |
      v
Technology-Specific List
      |
      v
Application-Specific Mutations
```

This usually produces better value than blindly using millions of entries.

---

# Tool Chaining

ffuf works well with other web tools.

Example:

```text
httpx
  |
  v
Alive Host
  |
  v
WhatWeb / Wappalyzer
  |
  v
Technology
  |
  v
ffuf
  |
  v
Endpoint
  |
  v
Burp Suite
```

---

# ffuf and Katana

Katana discovers links through crawling.

ffuf discovers candidate paths through wordlists.

```text
Katana
  |
  +-- linked/discovered routes

ffuf
  |
  +-- guessed/unlinked routes
```

Together they improve attack-surface coverage.

Related tool:

[Katana](katana.md)

---

# ffuf and Nuclei

A useful order is:

```text
ffuf
  |
  v
Interesting Endpoint
  |
  v
Manual Validation
  |
  v
Nuclei where appropriate
```

Do not automatically send broad template sets to every discovered path.

Related tool:

[Nuclei](nuclei.md)

---

# ffuf and sqlmap

If manual testing identifies a plausible SQL injection candidate:

```text
ffuf discovers endpoint
      |
      v
Burp identifies parameter
      |
      v
Manual SQLi validation
      |
      v
sqlmap where authorised
```

Related tool:

[sqlmap](sqlmap.md)

---

# ffuf and Interactsh

ffuf itself does not require out-of-band testing for normal discovery.

However, endpoints found by ffuf may later expose functionality involving:

- callbacks;
- webhooks;
- URL fetchers.

Interactsh can then support controlled OOB validation.

Related tool:

[Interactsh](interactsh.md)

---

# Quick Command Reference

## Basic Discovery

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ
```

## API Discovery

```bash
ffuf -w api.txt -u https://example.test/api/FUZZ -H "Accept: application/json"
```

## Authenticated Discovery

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ -H "Authorization: Bearer <REDACTED>"
```

## Cookie-Based Session

```bash
ffuf -w wordlist.txt -u https://example.test/FUZZ -H "Cookie: session=<REDACTED>"
```

## Parameter Name Discovery

```bash
ffuf -w parameters.txt -u 'https://example.test/page?FUZZ=test'
```

## Parameter Value Testing

```bash
ffuf -w values.txt -u 'https://example.test/page?mode=FUZZ'
```

## POST JSON

```bash
ffuf -w values.txt -u https://example.test/api/search -X POST -H "Content-Type: application/json" -d '{"query":"FUZZ"}'
```

## VHost Discovery

```bash
ffuf -w subdomains.txt -u https://example.test/ -H "Host: FUZZ.example.test"
```

## Version / Help

```bash
ffuf -h
```

---

# ffuf Checklist

## Preparation

- [ ] Target explicitly authorised.
- [ ] Scope confirmed.
- [ ] Wordlist appropriate.
- [ ] Baseline response understood.
- [ ] Random nonexistent path tested.
- [ ] Authentication context documented.
- [ ] Rate appropriate for environment.

## Discovery

- [ ] Directory paths reviewed.
- [ ] Files reviewed where relevant.
- [ ] Extensions selected based on technology.
- [ ] API routes considered.
- [ ] robots.txt reviewed.
- [ ] sitemap.xml reviewed.
- [ ] JavaScript-derived routes considered.

## Filtering

- [ ] Soft 404 checked.
- [ ] Status baseline checked.
- [ ] Response size baseline checked.
- [ ] Word/line differences considered.
- [ ] WAF block response identified.
- [ ] Filtering not overly aggressive.

## Authentication

- [ ] Approved test account used.
- [ ] Session still valid.
- [ ] Secrets redacted.
- [ ] Different roles kept separate.
- [ ] Account lockout risk avoided.

## Virtual Hosts

- [ ] Base domain authorised.
- [ ] Random vhost baseline tested.
- [ ] Wildcard behaviour checked.
- [ ] TLS/SNI context considered.
- [ ] New host manually validated.
- [ ] Scope confirmed before deeper testing.

## Operational Safety

- [ ] Concurrency appropriate.
- [ ] Rate limits respected.
- [ ] No destructive methods sprayed.
- [ ] Unexpected state changes trigger stop.
- [ ] Large downloads avoided.
- [ ] Third-party redirects not automatically tested.

## Validation

- [ ] Interesting endpoints reproduced manually.
- [ ] Burp/curl used for validation.
- [ ] Hidden endpoint not automatically called vulnerable.
- [ ] 403/401 interpreted correctly.
- [ ] 500 errors investigated carefully.
- [ ] Actual security impact established separately.

## Evidence

- [ ] ffuf version retained.
- [ ] Command retained.
- [ ] Wordlist recorded.
- [ ] Baseline recorded.
- [ ] Candidate path recorded.
- [ ] Authentication context recorded.
- [ ] Manual validation retained.
- [ ] Sensitive information redacted.

---

# Related Tool Notes

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

[Katana](katana.md)

[Nuclei](nuclei.md)

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

[Authentication Testing](../../web/authentication.md)

[Authorisation Testing](../../web/authorisation.md)

[API Security](../../web/api-security.md)

[Host Header Attacks](../../web/host-header-attacks.md)

[GraphQL](../../web/graphql.md)

---

# External References

## ffuf

[ffuf - GitHub](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }

## Wordlists

[SecLists - GitHub](https://github.com/danielmiessler/SecLists){ target="_blank" rel="noopener noreferrer" }

## Practical References

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use ffuf like this:

```text
Run Huge Wordlist
      |
      v
See 200 / 403 / 500
      |
      v
Call Everything Interesting a Finding
```

Use it like this:

```text
Understand Target
      |
      v
Establish Invalid-Path Baseline
      |
      v
Choose Focused Wordlist
      |
      v
Run Controlled ffuf Discovery
      |
      v
Filter Known Noise
      |
      v
Identify Interesting Difference
      |
      v
Reproduce Manually
      |
      v
Understand Endpoint Purpose
      |
      v
Test Authentication / Authorisation Where Relevant
      |
      v
Determine Actual Security Impact
      |
      v
Capture Evidence
```

ffuf is most valuable when it helps discover attack surface that normal navigation, crawling, or documentation did not reveal.

The tool identifies candidate resources.

The tester determines whether those resources create a real security issue.
