---
title: httpx
description: Practical ProjectDiscovery httpx reference for HTTP probing, live-host validation, technology enrichment, TLS inspection, structured output, filtering, evidence collection, and integration with wider reconnaissance workflows.
---

# httpx

ProjectDiscovery httpx is an HTTP toolkit commonly used during reconnaissance to identify reachable web services and enrich them with useful metadata.

It is particularly valuable after asset discovery because raw domain and subdomain lists often contain:

- hosts that do not resolve;
- hosts with no reachable HTTP service;
- HTTP-only services;
- HTTPS-only services;
- redirects;
- administrative interfaces;
- APIs;
- development systems;
- services on non-standard ports.

httpx helps turn those raw assets into a more useful web-target inventory.

```text
Discovered Assets
       |
       v
      httpx
       |
       +-- Reachable HTTP Services
       +-- Status Codes
       +-- Titles
       +-- Technologies
       +-- Redirects
       +-- TLS Information
       +-- IP Addresses
       +-- Server Metadata
       |
       v
Prioritised Web Targets
```

!!! warning "Authorised testing only"
    Run httpx only against assets that are explicitly within the authorised assessment scope. Some options increase concurrency, probe additional ports, perform additional requests, or enrich results using further network interaction. Review the rules of engagement before increasing scan breadth or request rate.

---

# Where httpx Fits

httpx normally sits between asset discovery and deeper application testing.

```text
Known Domain
    |
    v
Subdomain Discovery
    |
    v
Resolved / Candidate Hosts
    |
    v
httpx
    |
    v
Reachable Web Services
    |
    v
Technology Enrichment
    |
    v
Prioritisation
    |
    v
Manual Web Testing
```

Related methodology:

[Web Enumeration Tools](index.md)

[Subdomain Enumeration](../../web/reconnaissance/subdomain-enumeration.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

---

# What httpx Does

httpx performs HTTP probing and can collect information about reachable web services.

Depending on the options and installed version, useful output may include:

- URL;
- scheme;
- hostname;
- port;
- HTTP status code;
- page title;
- content length;
- content type;
- redirect location;
- server header;
- technology fingerprints;
- IP address;
- CNAME;
- CDN information;
- TLS information;
- certificate data;
- favicon data;
- response hashes;
- JSON output.

The important distinction is:

```text
Asset Discovery
      |
      v
Hostname Exists
```

versus:

```text
httpx
      |
      v
HTTP Service Responds
```

These are different stages of reconnaissance.

---

# Installation

httpx is maintained by ProjectDiscovery.

Check whether it is installed:

```bash
which httpx
```

Check the version:

```bash
httpx -version
```

Display help:

```bash
httpx -h
```

Official installation and usage documentation:

[ProjectDiscovery httpx](https://docs.projectdiscovery.io/opensource/httpx/overview){ target="_blank" rel="noopener noreferrer" }

[httpx Usage](https://docs.projectdiscovery.io/opensource/httpx/usage){ target="_blank" rel="noopener noreferrer" }

Official repository:

[ProjectDiscovery httpx - GitHub](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }

---

# Basic Usage

Probe a single URL:

```bash
httpx -u https://example.test
```

Probe a hostname:

```bash
httpx -u example.test
```

A common file-based workflow is:

```bash
httpx -l targets.txt
```

A quieter form that is useful in pipelines is:

```bash
httpx -l targets.txt -silent
```

Representative output may look like:

```text
https://portal.example.test
https://api.example.test
http://legacy.example.test
```

The exact behaviour depends on the version and supplied flags.

---

# Input from Standard Input

httpx works particularly well in Unix-style pipelines.

Example:

```bash
cat targets.txt | httpx -silent
```

Another common pattern is:

```bash
subfinder -d example.test -silent | httpx -silent
```

This allows one tool's output to become another tool's input.

---

# Input Files

A repeatable workflow is usually easier to manage with files.

Example:

```text
subdomains.txt
```

containing:

```text
app.example.test
portal.example.test
api.example.test
admin.example.test
```

Probe them with:

```bash
httpx -l subdomains.txt
```

Save reachable endpoints:

```bash
httpx -l subdomains.txt -silent > alive-web.txt
```

This creates a useful transition from subdomain discovery to web testing.

---

# Basic Reconnaissance Pipeline

A common workflow is:

```text
Domain
  |
  v
Subfinder
  |
  v
subdomains.txt
  |
  v
httpx
  |
  v
alive-web.txt
  |
  v
WhatWeb / Browser / Burp
```

Example:

```bash
subfinder -d example.test -silent > subdomains.txt
```

Then:

```bash
httpx -l subdomains.txt -silent > alive-web.txt
```

Then:

```bash
whatweb -i alive-web.txt
```

The purpose of httpx here is to reduce the asset list to services that appear to respond over HTTP or HTTPS.

---

# Status Codes

HTTP status codes are among the most useful enrichment fields.

Example:

```bash
httpx -l targets.txt -status-code
```

Representative output:

```text
https://portal.example.test [200]
https://admin.example.test [403]
https://old.example.test [301]
https://api.example.test [401]
```

These status codes provide useful prioritisation information.

However:

```text
403
```

does not automatically mean:

```text
Interesting hidden application
```

and:

```text
404
```

does not automatically mean:

```text
Nothing exists
```

Interpret status codes with the application context.

---

# Page Titles

Page titles can quickly reveal what a web service appears to be.

Example:

```bash
httpx -l targets.txt -title
```

Representative output:

```text
https://portal.example.test [Customer Portal]
https://grafana.example.test [Grafana]
https://admin.example.test [Admin Login]
```

Titles may reveal:

- product names;
- application names;
- administrative portals;
- dashboards;
- monitoring systems;
- default applications;
- authentication portals.

Titles are useful for prioritisation but can be arbitrary or misleading.

---

# Status Code and Title Together

A common reconnaissance combination is:

```bash
httpx -l targets.txt -status-code -title
```

Representative output:

```text
https://portal.example.test [200] [Customer Portal]
https://admin.example.test [302] [Sign In]
https://grafana.example.test [200] [Grafana]
```

This is much more useful than a simple list of URLs.

---

# Technology Detection

httpx can perform technology detection.

A common option is:

```bash
httpx -l targets.txt -tech-detect
```

Representative output may resemble:

```text
https://portal.example.test [nginx,React]
https://blog.example.test [Apache,WordPress,jQuery]
```

Technology detection should be treated as fingerprinting evidence rather than absolute proof.

Use it to generate hypotheses.

---

# Correlating Technology Detection

A strong workflow is:

```text
httpx
  |
  +-- React
  +-- nginx
  |
  v
WhatWeb
  |
  +-- React
  +-- nginx
  |
  v
Wappalyzer
  |
  +-- React
  |
  v
Manual HTTP / JS Review
  |
  v
Higher Confidence
```

Related notes:

[WhatWeb](whatweb.md)

[Wappalyzer](wappalyzer.md)

---

# Web Server Information

Server information can sometimes be displayed as part of httpx enrichment.

For example:

```text
Server: nginx
```

or:

```text
Server: Apache
```

This can help identify edge technologies.

However, server headers may be:

- removed;
- rewritten;
- inserted by reverse proxies;
- provided by CDNs;
- intentionally changed.

Treat them as indicators.

---

# Content Length

Content length is useful for grouping and filtering responses.

For example:

```bash
httpx -l targets.txt -content-length
```

Representative output:

```text
https://portal.example.test [200] [4812]
https://admin.example.test [403] [153]
```

Content length becomes particularly useful when many endpoints return the same generic response.

Example:

```text
/admin        403  153 bytes
/internal     403  153 bytes
/management   403  153 bytes
```

This may indicate a shared block page rather than three unique applications.

---

# Content Type

Content type helps distinguish different kinds of applications.

Examples include:

```text
text/html
application/json
application/xml
text/plain
```

An API endpoint returning:

```text
application/json
```

may deserve different follow-up testing than a normal HTML page.

---

# Redirects

Redirect behaviour is important reconnaissance information.

For example:

```text
http://example.test
       |
       v
https://example.test
```

or:

```text
https://example.test
       |
       v
https://login.example.test/
```

Redirects can reveal:

- canonical hostnames;
- HTTPS enforcement;
- authentication portals;
- application base paths;
- external services.

Use redirect information as part of attack-surface analysis.

---

# Following Redirects

Following redirects can be useful when the final application is more relevant than the initial endpoint.

However, preserve the original redirect information.

Example:

```text
Initial:
http://portal.example.test

Redirect:
https://portal.example.test/

Final:
200 OK
```

The redirect itself is useful evidence.

Be cautious when redirects lead to third-party infrastructure that may be outside scope.

---

# HTTP and HTTPS Discovery

A hostname may support:

```text
HTTP only
HTTPS only
Both
```

httpx can help determine the reachable scheme.

For example:

```text
portal.example.test
      |
      +--> https://portal.example.test
```

This makes later tooling more reliable because the correct scheme is already known.

---

# Non-Standard Ports

Web applications are frequently exposed on non-standard ports.

Examples include:

```text
8000
8008
8080
8081
8443
8888
9000
9443
```

When the assessment scope includes them, httpx can be combined with port discovery.

Conceptually:

```text
Nmap / Port Discovery
       |
       v
Host:Port Pairs
       |
       v
httpx
       |
       v
HTTP Services
```

Do not assume a service is HTTP simply because its port number commonly hosts web traffic.

---

# Probe Common Web Ports

Where explicitly authorised, it may be useful to probe selected web ports.

Always check the installed version's port-related flags:

```bash
httpx -h
```

before building automation around them.

The workflow should be:

```text
Known Hosts
    |
    v
Known / Approved Ports
    |
    v
httpx
    |
    v
Validated HTTP Services
```

Avoid indiscriminately probing large port ranges without assessment justification.

---

# IP Addresses

httpx can enrich HTTP endpoints with IP-address information.

This can help identify:

- several hostnames sharing the same infrastructure;
- separate application clusters;
- CDN-backed hosts;
- unexpected infrastructure differences.

Example:

```text
app.example.test       -> 192.0.2.10
portal.example.test    -> 192.0.2.10
api.example.test       -> 192.0.2.20
```

This can guide architecture analysis.

---

# CNAME Information

CNAME information can reveal:

- cloud platforms;
- SaaS services;
- CDN providers;
- delegated infrastructure;
- third-party hosting.

A hostname such as:

```text
portal.example.test
```

may point to:

```text
provider.example.net
```

This is useful reconnaissance information, but the external provider is not automatically authorised for testing.

---

# CDN Detection

httpx can help identify when an endpoint appears to use a CDN or similar edge service.

This matters because the architecture may be:

```text
Client
  |
  v
CDN
  |
  v
Reverse Proxy
  |
  v
Application
```

The IP address or server behaviour observed externally may therefore belong to the CDN rather than the origin application.

---

# TLS Information

TLS metadata can provide additional reconnaissance information.

Useful details may include:

- certificate subject;
- issuer;
- Subject Alternative Names;
- validity;
- hostname information.

Certificate data may reveal additional hostnames.

Always apply a scope check before investigating newly discovered certificate names.

```text
Certificate SAN
      |
      v
New Hostname
      |
      v
Scope Check
      |
      +-- In scope -> investigate
      |
      +-- Out of scope -> record only
```

---

# TLS Certificate Names

Certificate SAN entries can sometimes expose:

- legacy hostnames;
- administrative hostnames;
- alternate application names;
- development systems.

These are discovery leads, not automatic authorisation.

---

# Favicon Fingerprinting

Favicons can be useful for identifying web products and application families.

A typical fingerprinting model is:

```text
Target
  |
  v
/favicon.ico
  |
  v
Hash
  |
  v
Known Fingerprint
```

httpx can assist with favicon-related metadata depending on the installed version.

A favicon match should be treated as supporting evidence.

---

# Response Hashing

Response hashes can help group similar applications.

For example:

```text
Host A -> same response hash
Host B -> same response hash
Host C -> different hash
```

This may suggest that Host A and Host B serve the same application or template.

Hash equality does not always prove identical backend systems.

Dynamic content can also alter hashes between requests.

---

# Duplicate Applications

Large organisations often expose many hostnames that lead to the same application.

Example:

```text
app.example.test
portal.example.test
customer.example.test
```

all redirecting to:

```text
login.example.test
```

httpx metadata can help identify and deduplicate these patterns.

This can reduce unnecessary repetitive testing.

---

# JSON Output

Structured output is extremely useful for automation and analysis.

Depending on the installed version, JSON line output can be enabled.

Check:

```bash
httpx -h
```

for the exact JSON output option supported by that version.

A typical pipeline concept is:

```text
httpx
  |
  v
JSONL
  |
  +--> jq
  |
  +--> Python
  |
  +--> spreadsheet/report pipeline
```

Structured output is generally preferable to parsing coloured terminal output.

---

# Working with jq

When httpx produces JSONL, jq can be used to extract specific fields.

Conceptually:

```bash
cat httpx.jsonl | jq
```

For example, one might extract:

```text
URL
Status
Title
Technologies
IP
```

The exact JSON field names should be checked against output produced by the installed version rather than assumed.

---

# Saving Output

Basic output can be saved using shell redirection:

```bash
httpx -l targets.txt -silent > alive-web.txt
```

For richer assessments, preserve structured output where possible.

A useful evidence directory might contain:

```text
recon/
|
+-- subdomains.txt
+-- resolved.txt
+-- alive-web.txt
+-- httpx.jsonl
+-- whatweb.txt
```

This makes the reconnaissance process reproducible.

---

# Filtering Status Codes

For some workflows, specific response categories may be more relevant.

Examples:

```text
200
301
302
401
403
500
```

Before applying filters, think about what might be lost.

For example, keeping only `200` responses can discard:

```text
401 -> authenticated API
403 -> restricted administration portal
302 -> login redirect
500 -> unusual application behaviour
```

Therefore:

```text
Filter
```

should follow:

```text
Objective
```

not convenience.

---

# Interesting Status Codes

A useful triage model is:

| Status | Why It May Be Interesting |
|---|---|
| 200 | Reachable content |
| 301/302 | Redirect destination may reveal application structure |
| 401 | Authentication boundary |
| 403 | Restricted resource or edge control |
| 404 | Error-page fingerprinting or routing behaviour |
| 405 | Endpoint exists but method may differ |
| 429 | Rate limiting |
| 500 | Server-side error or unexpected input handling |

No status code is automatically a vulnerability.

---

# Filtering by Content Length

Generic block or error pages often have identical lengths.

Example:

```text
host1 -> 403 -> 153
host2 -> 403 -> 153
host3 -> 403 -> 153
```

This may indicate:

```text
Shared WAF / proxy response
```

Grouping by response size can therefore reduce noise.

---

# Silent Output

The `-silent` option is useful for pipelines:

```bash
httpx -l targets.txt -silent
```

It avoids unnecessary banners and status information when the output is being passed into another tool.

For manual analysis, additional metadata flags are often more useful.

---

# Combining Useful Fields

A typical enrichment command may include several fields.

For example:

```bash
httpx -l targets.txt -status-code -title -tech-detect
```

This produces a compact view of:

```text
URL
Status
Title
Technology
```

For larger assessments, structured output is usually preferable.

---

# httpx and Subfinder

A very common combination is:

```bash
subfinder -d example.test -silent | httpx -silent
```

Conceptually:

```text
Domain
  |
  v
Subfinder
  |
  v
Candidate Subdomains
  |
  v
httpx
  |
  v
Reachable Web Applications
```

This is useful because passive subdomain discovery alone does not tell you whether a hostname currently hosts an accessible web application.

---

# httpx and WhatWeb

After identifying live web applications:

```bash
httpx -l subdomains.txt -silent > alive-web.txt
```

feed them into WhatWeb:

```bash
whatweb -i alive-web.txt
```

Workflow:

```text
httpx
   |
   v
Live Web Services
   |
   v
WhatWeb
   |
   v
Detailed Fingerprints
```

Related note:

[WhatWeb](whatweb.md)

---

# httpx and Wappalyzer

For large scopes:

```text
Thousands of Hosts
      |
      v
httpx
      |
      v
Interesting Web Targets
      |
      v
Browser + Wappalyzer
```

This is generally more practical than manually browsing every hostname discovered during reconnaissance.

Related note:

[Wappalyzer](wappalyzer.md)

---

# httpx and Nuclei

httpx output is frequently suitable as input for further automated checks.

Conceptually:

```text
Subdomains
    |
    v
httpx
    |
    v
Reachable Web Services
    |
    v
Nuclei
```

However:

```text
Reachable
```

does not mean:

```text
Safe to scan aggressively
```

Confirm that the rules of engagement allow the intended Nuclei templates and scan intensity.

---

# httpx and Katana

httpx can identify reachable applications.

Katana can then crawl selected applications.

```text
Candidate Hosts
      |
      v
httpx
      |
      v
Reachable URLs
      |
      v
Katana
      |
      v
Discovered Endpoints
```

This is a natural transition from broad reconnaissance to endpoint discovery.

---

# httpx and Burp Suite

httpx is useful for breadth.

Burp Suite is useful for depth.

```text
httpx
   |
   v
Interesting Target
   |
   v
Browser through Burp
   |
   +-- Requests
   +-- Responses
   +-- Authentication
   +-- APIs
   +-- Sessions
```

Do not attempt to replace manual application understanding with httpx metadata.

---

# httpx and curl

curl is useful for verifying individual httpx results.

Example:

```text
httpx:
https://admin.example.test [403]
```

Check manually:

```bash
curl -i https://admin.example.test
```

Review:

- response body;
- headers;
- cookies;
- WAF behaviour;
- server details.

Quick reference:

[curl Cheatsheet](../../cheatsheets/curl.md)

---

# httpx and Nmap

Nmap can identify network services.

httpx can determine whether discovered services behave as HTTP.

Example:

```text
Nmap
 |
 +-- 80
 +-- 443
 +-- 8080
 +-- 8443
 |
 v
httpx
 |
 v
Validated Web Services
```

This is particularly useful for non-standard ports.

---

# Establishing a Web Inventory

A mature reconnaissance workflow should produce more than `alive.txt`.

Useful inventory fields include:

```text
Hostname
URL
Scheme
Port
Status
Title
Technology
Server
IP
CNAME
CDN
Redirect
TLS
Notes
```

Example:

| URL | Status | Title | Technology | IP | Notes |
|---|---:|---|---|---|---|
| `https://portal.example.test` | 200 | Customer Portal | nginx, React | `192.0.2.10` | Main application |
| `https://api.example.test` | 401 | - | nginx | `192.0.2.20` | API |
| `https://admin.example.test` | 403 | Forbidden | CDN | `192.0.2.30` | Restricted |

This is more useful than an unstructured URL list.

---

# Prioritising Targets

httpx metadata can help prioritise web applications.

Potentially interesting characteristics include:

- administrative titles;
- development systems;
- login portals;
- unusual status codes;
- management products;
- uncommon technologies;
- legacy servers;
- exposed APIs;
- uncommon ports;
- detailed version information.

Prioritisation means:

```text
Investigate earlier
```

not:

```text
Assume vulnerable
```

---

# Authentication Boundaries

A `401` or authentication redirect can be valuable attack-surface information.

Example:

```text
https://api.example.test [401]
```

This tells us:

```text
HTTP service exists
Authentication is required
```

It does not tell us:

```text
Authentication is secure
```

That requires deeper application testing.

Related note:

[Authentication Testing](../../web/authentication.md)

---

# 403 Responses

A `403 Forbidden` response may come from:

- application authorisation;
- WAF;
- CDN;
- reverse proxy;
- IP restriction;
- access-control policy;
- virtual host behaviour.

Example:

```text
httpx:
https://admin.example.test [403]
```

Manual validation:

```bash
curl -i https://admin.example.test
```

Inspect the actual response before drawing conclusions.

---

# 404 Responses

A `404` response can still provide useful information.

It may expose:

- server fingerprint;
- framework error format;
- routing behaviour;
- default error page.

A useful external reference for comparison is:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

A 404 should not automatically be discarded from reconnaissance.

---

# Soft 404 Behaviour

A host may return `200 OK` for unknown resources.

This can make automated enumeration misleading.

Example:

```text
/random-a -> 200 5234 bytes
/random-b -> 200 5234 bytes
/admin    -> 200 5234 bytes
```

This may represent one generic soft-404 page.

Before using httpx results to drive content discovery, establish the target's unknown-resource baseline manually.

---

# 500 Responses

A `500 Internal Server Error` may represent:

- temporary backend failure;
- unexpected routing;
- application error;
- proxy failure;
- target instability.

Do not assume it is a vulnerability.

It may still be worth prioritising for manual investigation.

---

# Redirect Chains

A service may pass through several redirects.

Example:

```text
http://example.test
        |
        v
https://example.test
        |
        v
https://login.example.test/
```

Each stage may provide useful architecture information.

Preserve the original endpoint even if the final destination is the most relevant application.

---

# Virtual Hosting

Different hostnames sharing one IP address may serve different applications.

```text
192.0.2.10
   |
   +-- app.example.test
   +-- admin.example.test
   +-- api.example.test
```

Therefore, probe hostnames rather than relying only on IP addresses when virtual hosts are known.

---

# Wildcard DNS

Wildcard DNS can cause nonexistent subdomains to resolve.

Example:

```text
random-123.example.test
random-456.example.test
anything.example.test
```

all resolving to the same IP.

httpx may then show them all as reachable if the web server uses a catch-all virtual host.

This can create false-positive asset lists.

Validate random hostname behaviour when results look suspicious.

---

# Catch-All Virtual Hosts

A reverse proxy or web server may return the same application for every hostname.

Example:

```text
a.example.test -> same title
b.example.test -> same title
c.example.test -> same title
random.example.test -> same title
```

Compare:

- status;
- title;
- length;
- response hash;
- redirect;
- IP.

This can help distinguish genuine applications from catch-all routing.

---

# WAF Influence

A WAF can affect httpx results.

Possible behaviours include:

- `403`;
- `429`;
- CAPTCHA;
- JavaScript challenge;
- connection reset;
- generic body;
- altered headers.

Therefore:

```text
httpx result
```

may represent:

```text
WAF behaviour
```

rather than:

```text
Application behaviour
```

---

# CDN Influence

A CDN may also change:

- IP address;
- headers;
- TLS certificate;
- error pages;
- caching;
- status behaviour.

When interpreting results, separate:

```text
Edge Layer
```

from:

```text
Origin Application
```

---

# DNS Resolution Problems

If httpx produces no result for an expected host, verify DNS.

```bash
getent hosts example.test
```

or:

```bash
dig example.test
```

Then test directly:

```bash
curl -I https://example.test
```

A missing httpx result should be investigated before assuming the service is offline.

---

# TLS Problems

HTTPS services may fail because of:

- certificate problems;
- hostname mismatch;
- unsupported protocols;
- interception;
- network controls.

Use curl for detailed investigation:

```bash
curl -v https://example.test
```

Do not disable TLS verification casually.

For legitimate internal PKI or interception environments, prefer adding the appropriate trusted CA where feasible.

---

# Timeouts

Large reconnaissance runs can encounter:

- slow hosts;
- dead hosts;
- filtered ports;
- unstable services.

httpx provides timeout and retry controls depending on version.

Check:

```bash
httpx -h
```

before adjusting them.

A shorter timeout increases speed but may increase false negatives.

A longer timeout improves patience but may make large scans much slower.

---

# Rate Limiting

Concurrency and request rate matter operationally.

High request rates may:

- trigger WAF controls;
- overload fragile systems;
- produce unreliable responses;
- trigger monitoring alerts;
- violate engagement restrictions.

Always tune scans to the target and rules of engagement.

---

# Concurrency

Parallel requests make httpx efficient.

They also increase load.

A suitable value depends on:

- number of targets;
- network conditions;
- application sensitivity;
- target infrastructure;
- testing restrictions.

Do not treat maximum concurrency as the correct default.

---

# Retries

Retries can help compensate for unstable networks.

Too many retries can also:

- increase load;
- lengthen scans;
- duplicate evidence;
- trigger rate controls.

Use them intentionally.

---

# Proxying httpx Traffic

In some assessment workflows, HTTP traffic may need to pass through a proxy for inspection or network requirements.

Check the installed version:

```bash
httpx -h
```

for proxy-related options.

For individual request validation, curl or Burp Suite may provide easier inspection.

---

# Custom Headers

Some applications require specific headers.

Examples might include:

```text
Authorization
Accept
User-Agent
Host
Custom organisation headers
```

When adding headers during authorised testing, document them so that results remain reproducible.

Do not accidentally expose authentication tokens in:

- shell history;
- logs;
- screenshots;
- shared output files.

---

# User-Agent Differences

Applications may return different results based on User-Agent.

Possible reasons include:

- bot detection;
- CDN logic;
- device-specific rendering;
- security controls.

If httpx output differs significantly from browser behaviour, compare the requests.

---

# Authentication and httpx

httpx is primarily useful for broad probing rather than full authenticated application testing.

Authenticated application mapping is usually better handled with:

- browser;
- Burp Suite;
- application-specific scripts;
- API clients.

A `401`, login redirect, or unauthenticated landing page does not represent the full authenticated attack surface.

---

# API Endpoints

httpx can help identify API services through clues such as:

- JSON content type;
- `401` status;
- API-specific titles or headers;
- unusual routes.

After discovery, move to appropriate API testing.

Related note:

[API Security](../../web/api-security.md)

---

# JSON Responses

A web endpoint that returns:

```http
Content-Type: application/json
```

may be:

- API;
- authentication service;
- backend endpoint;
- framework-generated error response.

Inspect the body manually.

---

# JavaScript Applications

httpx may identify the page title and technology but cannot replace browser-based analysis of JavaScript-heavy applications.

Continue with:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

and interactive testing through Burp Suite.

---

# Fingerprinting Confidence

A single httpx technology match should usually be treated as:

```text
Indicator
```

not:

```text
Confirmed fact
```

Confidence increases when independent evidence agrees.

```text
httpx:
nginx

WhatWeb:
nginx

HTTP Header:
Server: nginx

Result:
High confidence
```

---

# False Positives

Possible causes include:

- generic fingerprint strings;
- shared assets;
- CDN pages;
- catch-all hosts;
- reverse proxies;
- misleading headers;
- wildcard DNS.

Always manually validate important observations.

---

# False Negatives

Possible causes include:

- timeouts;
- DNS problems;
- blocked probes;
- unusual ports;
- TLS errors;
- authentication requirements;
- WAF behaviour;
- non-standard HTTP implementations.

A host missing from httpx output should not automatically be considered dead.

---

# Representative Reconnaissance Scenario

Suppose subdomain enumeration produces:

```text
portal.example.test
api.example.test
admin.example.test
legacy.example.test
```

Run:

```bash
httpx -l subdomains.txt -status-code -title -tech-detect
```

Representative result:

```text
https://portal.example.test [200] [Customer Portal] [nginx,React]
https://api.example.test [401] [] [nginx]
https://admin.example.test [403] [Forbidden] [Cloudflare]
http://legacy.example.test [301] [] [Apache]
```

Interpretation:

```text
portal
  -> reachable main application
  -> likely React frontend
  -> good manual-testing target

api
  -> reachable API
  -> authentication boundary exists

admin
  -> reachable restricted service
  -> edge/WAF behaviour needs interpretation

legacy
  -> redirects
  -> inspect destination and server behaviour
```

This is much more useful than treating every hostname equally.

---

# Prioritised Follow-Up

Based on the example above:

```text
portal
  |
  +--> Browser + Burp
  +--> Wappalyzer
  +--> WhatWeb
  +--> JavaScript Analysis

api
  |
  +--> API mapping
  +--> Authentication review

admin
  |
  +--> Manual 403 inspection
  +--> Scope validation

legacy
  |
  +--> Redirect analysis
  +--> Technology validation
```

httpx helps decide where to spend deeper testing effort.

---

# Evidence Collection

For useful httpx observations, retain:

```text
Target list
Tool version
Exact command
Date/time
Output format
Relevant URLs
Status codes
Titles
Technology indicators
Redirects
IP information
TLS information
Manual validation
```

Example:

```text
Tool:
httpx

Target:
portal.example.test

Result:
https://portal.example.test
200
Customer Portal
nginx
React

Manual validation:
Browser confirmed application availability.
HTTP response contained nginx Server header.
JavaScript assets supported React identification.
```

---

# Reporting

httpx output is normally reconnaissance evidence rather than a finding.

Example wording:

```text
HTTP probing identified the externally reachable web applications and
was used to prioritise endpoints for further manual testing. Relevant
services were subsequently validated through direct HTTP requests and
interactive application review.
```

Avoid:

```text
httpx found vulnerabilities on these hosts.
```

unless separate security validation actually supports that conclusion.

---

# Common Mistakes

## Keeping Only HTTP 200

This can discard:

```text
401 APIs
403 management interfaces
302 authentication portals
500 unusual services
```

Keep enough data to understand the attack surface.

---

## Treating Every Resolving Host as Unique

Wildcard DNS and catch-all virtual hosts can produce large amounts of duplicate noise.

---

## Treating Technology Detection as Proof

Use WhatWeb, Wappalyzer, headers, assets, and manual inspection to corroborate important fingerprints.

---

## Ignoring Redirects

A redirect can reveal the canonical application or authentication architecture.

---

## Ignoring Non-Standard Ports

Relevant web applications may not use 80 or 443.

---

## Scanning Too Aggressively

High concurrency can affect reliability and target stability.

---

## Ignoring Structured Output

For large assessments, JSONL is usually more useful than parsing human-readable terminal output.

---

# Practical Workflow

A mature httpx workflow can be:

```text
1. Define scope
      |
      v
2. Collect candidate domains/subdomains
      |
      v
3. Resolve and deduplicate
      |
      v
4. Probe with httpx
      |
      v
5. Collect metadata
      |
      +-- status
      +-- title
      +-- technology
      +-- IP
      +-- TLS
      +-- redirects
      |
      v
6. Identify wildcard/catch-all behaviour
      |
      v
7. Prioritise interesting applications
      |
      v
8. Validate manually
      |
      +-- curl
      +-- WhatWeb
      +-- Wappalyzer
      +-- Browser/Burp
      |
      v
9. Feed selected targets into deeper workflows
```

---

# Quick Command Reference

## Version

```bash
httpx -version
```

## Help

```bash
httpx -h
```

## Single Target

```bash
httpx -u https://example.test
```

## Input File

```bash
httpx -l targets.txt
```

## Silent Output

```bash
httpx -l targets.txt -silent
```

## Save Reachable URLs

```bash
httpx -l targets.txt -silent > alive-web.txt
```

## Status Codes

```bash
httpx -l targets.txt -status-code
```

## Titles

```bash
httpx -l targets.txt -title
```

## Technology Detection

```bash
httpx -l targets.txt -tech-detect
```

## Combined Enrichment

```bash
httpx -l targets.txt -status-code -title -tech-detect
```

## Pipeline from Subfinder

```bash
subfinder -d example.test -silent | httpx -silent
```

## Feed Reachable Endpoints to WhatWeb

```bash
httpx -l subdomains.txt -silent > alive-web.txt
whatweb -i alive-web.txt
```

Because ProjectDiscovery tools evolve, verify advanced options against:

```bash
httpx -h
```

before using them in reusable scripts.

---

# httpx Checklist

## Preparation

- [ ] Scope confirmed.
- [ ] Target input deduplicated.
- [ ] Newly discovered third-party infrastructure treated separately.
- [ ] Rules of engagement reviewed.
- [ ] httpx version recorded where useful.

## Probing

- [ ] Reachable HTTP services identified.
- [ ] HTTPS considered.
- [ ] Relevant non-standard ports considered.
- [ ] Status codes retained.
- [ ] Redirects retained.
- [ ] Titles collected where useful.
- [ ] Technology detection used where useful.

## Infrastructure

- [ ] IP information reviewed.
- [ ] CNAME information reviewed where relevant.
- [ ] CDN/proxy behaviour considered.
- [ ] TLS information reviewed where relevant.
- [ ] Wildcard DNS considered.
- [ ] Catch-all virtual hosts considered.

## Interpretation

- [ ] 401 responses not discarded.
- [ ] 403 responses manually reviewed where useful.
- [ ] 404 responses considered for fingerprinting.
- [ ] 500 responses investigated where relevant.
- [ ] Technology matches treated as indicators.
- [ ] Duplicate applications identified where possible.

## Operational Safety

- [ ] Request rate appropriate.
- [ ] Concurrency appropriate.
- [ ] Timeouts appropriate.
- [ ] Retries appropriate.
- [ ] Sensitive authentication headers protected.

## Evidence

- [ ] Input list retained.
- [ ] Exact command retained.
- [ ] Output retained.
- [ ] Structured output used for large assessments where useful.
- [ ] Manual validation recorded.
- [ ] Tool output not confused with vulnerability confirmation.

---

# Related Tool Notes

[Web Enumeration Tools](index.md)

[WhatWeb](whatweb.md)

[Wappalyzer](wappalyzer.md)

Related web testing:

[Web Application Testing Tools](../web-testing/index.md)

---

# Related Security Notes

[Web Application Security](../../web/index.md)

[Web Reconnaissance](../../web/reconnaissance/index.md)

[Subdomain Enumeration](../../web/reconnaissance/subdomain-enumeration.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

[Content Discovery](../../web/reconnaissance/content-discovery.md)

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

[API Security](../../web/api-security.md)

[Authentication Testing](../../web/authentication.md)

---

# External References

## Official httpx Resources

[ProjectDiscovery httpx Documentation](https://docs.projectdiscovery.io/opensource/httpx/overview){ target="_blank" rel="noopener noreferrer" }

[httpx Usage](https://docs.projectdiscovery.io/opensource/httpx/usage){ target="_blank" rel="noopener noreferrer" }

[ProjectDiscovery httpx - GitHub](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }

## Supporting Reconnaissance References

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use httpx like this:

```text
Subdomains
    |
    v
httpx
    |
    v
Discard Everything Except 200
```

Use it like this:

```text
Candidate Assets
      |
      v
httpx
      |
      +-- Reachability
      +-- Status
      +-- Title
      +-- Technology
      +-- Redirect
      +-- IP
      +-- TLS
      |
      v
Interpret Results
      |
      +-- 200 application?
      +-- 401 API?
      +-- 403 restricted service?
      +-- 302 authentication flow?
      +-- duplicate application?
      +-- wildcard host?
      |
      v
Prioritise
      |
      v
Validate Manually
      |
      +-- curl
      +-- WhatWeb
      +-- Wappalyzer
      +-- Browser/Burp
      |
      v
Deeper Testing
```

The value of httpx is not simply identifying which hosts respond.

Its value is turning a large, noisy asset list into a structured and prioritised inventory of web services that can be investigated more intelligently.
