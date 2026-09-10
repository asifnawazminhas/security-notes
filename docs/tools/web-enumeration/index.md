---
title: Web Enumeration Tools
description: Practical web enumeration tooling for identifying technologies, live services, application behaviour, and useful reconnaissance indicators before deeper web application testing.
---

# Web Enumeration Tools

Web enumeration is the process of collecting and validating information about web applications before deeper testing begins.

The objective is not simply to run several fingerprinting tools.

The objective is to answer questions such as:

- Which hosts actually expose HTTP or HTTPS?
- Which applications are reachable?
- Which technologies appear to be in use?
- Which frameworks, CMS platforms, or libraries may be present?
- Which ports expose web services?
- Which redirects occur?
- Which TLS endpoints exist?
- Which application titles and response patterns are interesting?
- Are there default error pages or framework-specific responses?
- Are multiple applications hosted behind the same IP address?
- Which targets deserve deeper manual testing?
- Which observations can be independently validated?

A useful web enumeration workflow is:

```text
Domains / IP Addresses
        |
        v
Identify Web Services
        |
        v
Collect HTTP Metadata
        |
        +-- Status Codes
        +-- Titles
        +-- Headers
        +-- Redirects
        +-- TLS
        |
        v
Technology Fingerprinting
        |
        +-- WhatWeb
        +-- Wappalyzer
        +-- httpx
        |
        v
Manual Validation
        |
        +-- HTML
        +-- Headers
        +-- Cookies
        +-- Asset Paths
        +-- Error Pages
        |
        v
Prioritised Web Targets
        |
        v
Deeper Web Testing
```

!!! warning "Authorised testing only"
    Perform web enumeration only against systems and applications that are explicitly within the authorised assessment scope. Enumeration tools can generate large numbers of requests, follow redirects, probe multiple ports, or interact with third-party infrastructure. Review the rules of engagement before increasing concurrency, recursion, or scan coverage.

---

# Where Web Enumeration Fits

Web enumeration normally takes place after initial asset discovery and before deeper application testing.

```text
Scope
  |
  v
Asset Discovery
  |
  v
Web Enumeration
  |
  v
Attack Surface Analysis
  |
  v
Content and Endpoint Discovery
  |
  v
Application Testing
  |
  v
Validation
```

Related methodology:

[Web Reconnaissance](../../web/reconnaissance/index.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

[Web Application Testing Methodology](../../web/methodology.md)

---

# Primary Tools

The core tools in this section are:

| Tool | Primary Purpose |
|---|---|
| WhatWeb | Fingerprint web technologies |
| Wappalyzer | Identify technologies during browser-based inspection |
| httpx | Probe HTTP services and collect structured metadata |
| Nmap | Identify open ports and web services |
| curl | Manually inspect HTTP behaviour |
| Burp Suite | Interactively inspect and validate application responses |

The first three are the primary web enumeration tools documented in this section.

---

# WhatWeb

WhatWeb is designed specifically for website fingerprinting.

It identifies indicators associated with technologies such as:

- web servers;
- frameworks;
- CMS platforms;
- JavaScript libraries;
- analytics platforms;
- application components;
- HTTP headers;
- cookies;
- HTML patterns;
- page metadata.

Basic usage:

```bash
whatweb https://example.test
```

Typical workflow:

```text
Target
  |
  v
WhatWeb
  |
  +-- Headers
  +-- HTML
  +-- Cookies
  +-- Metadata
  +-- Known Patterns
  |
  v
Technology Candidates
  |
  v
Manual Validation
```

A WhatWeb result is generally a fingerprinting indicator rather than definitive proof.

For example:

```text
WhatWeb:
Apache

Response header:
Server: Apache

Default error page:
Apache-style response

Asset structure:
Consistent with candidate stack

Result:
Higher-confidence fingerprint
```

Detailed note:

[WhatWeb](whatweb.md)

Official project:

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

---

# Wappalyzer

Wappalyzer identifies technologies associated with websites and web applications.

It is especially useful during interactive browser-based reconnaissance.

Depending on the interface being used, Wappalyzer may identify:

- web frameworks;
- CMS platforms;
- JavaScript frameworks;
- analytics systems;
- CDN providers;
- server technologies;
- e-commerce platforms;
- tag managers;
- development frameworks;
- security-related infrastructure.

A typical workflow is:

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
  +-- CMS
  +-- Libraries
  +-- Infrastructure
  |
  v
Candidate Technologies
  |
  v
Manual Validation
```

Wappalyzer findings should be correlated with other observations.

Useful supporting evidence includes:

- response headers;
- cookies;
- HTML source;
- JavaScript bundles;
- asset paths;
- application behaviour;
- error pages;
- WhatWeb results;
- httpx results.

Detailed note:

[Wappalyzer](wappalyzer.md)

Official resource:

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

---

# httpx

ProjectDiscovery httpx is designed for HTTP probing and enrichment.

It is particularly useful when reconnaissance produces a large set of domains or subdomains.

A simple workflow is:

```text
subdomains.txt
      |
      v
    httpx
      |
      +-- Reachable hosts
      +-- HTTP status
      +-- Title
      +-- Technology
      +-- Redirect
      +-- TLS
      |
      v
alive-web.txt
```

This allows a large discovery set to be reduced into a more useful collection of reachable web services.

Useful output may include:

- URL;
- HTTP status code;
- page title;
- content length;
- content type;
- redirect location;
- server information;
- technology indicators;
- IP address;
- TLS information;
- response hashes;
- favicon information.

Detailed note:

[httpx](httpx.md)

Official documentation:

[ProjectDiscovery httpx](https://docs.projectdiscovery.io/opensource/httpx/overview){ target="_blank" rel="noopener noreferrer" }

[httpx Usage](https://docs.projectdiscovery.io/opensource/httpx/usage){ target="_blank" rel="noopener noreferrer" }

---

# Supporting Tools

Web enumeration frequently involves additional tools.

These may not be dedicated fingerprinting tools, but they can provide important supporting evidence.

---

## Nmap

Nmap can identify open ports and services before HTTP-specific probing begins.

For example:

```bash
nmap -sV -p 80,443,8000,8080,8443 example.test
```

Potential observations include:

```text
80/tcp    open  http
443/tcp   open  https
8080/tcp  open  http-proxy
8443/tcp  open  https-alt
```

These results indicate where additional HTTP enumeration may be useful.

A useful workflow is:

```text
Host
 |
 v
Nmap
 |
 +-- 80
 +-- 443
 +-- 8080
 +-- 8443
 |
 v
HTTP Probing
```

Nmap service detection should not automatically be treated as definitive technology identification.

Banners can be:

- removed;
- modified;
- proxied;
- misleading;
- affected by backported software.

Official documentation:

[Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }

---

## curl

curl is extremely useful for validating individual HTTP observations manually.

Examples:

```bash
curl -i https://example.test/
```

```bash
curl -I https://example.test/
```

```bash
curl -v https://example.test/
```

curl can help inspect:

- HTTP headers;
- redirects;
- cookies;
- TLS behaviour;
- server headers;
- response content;
- virtual host behaviour;
- API responses.

For reconnaissance, curl is particularly useful for confirming whether an automated fingerprint corresponds to the actual HTTP response.

Example:

```text
WhatWeb
   |
   v
Candidate technology
   |
   v
curl
   |
   +-- inspect headers
   +-- inspect response
   +-- inspect redirect
   |
   v
Manual confirmation
```

Quick reference:

[curl Cheatsheet](../../cheatsheets/curl.md)

---

## Burp Suite

Burp Suite is useful when web enumeration becomes interactive.

For example, after initial fingerprinting, Burp can help inspect:

- complete HTTP history;
- unusual redirects;
- cookies;
- authentication flows;
- API calls;
- JavaScript requests;
- hidden endpoints;
- headers;
- error behaviour.

Related tool section:

[Web Application Testing Tools](../web-testing/index.md)

---

# Passive and Active Enumeration

Web enumeration can be broadly divided into passive and active activities.

## Passive Enumeration

Passive techniques attempt to collect information without directly interacting with the target application or by minimising direct interaction.

Examples include:

- examining previously collected asset information;
- reviewing DNS data;
- reviewing certificate transparency information;
- reviewing publicly indexed resources;
- analysing known technology information;
- examining historical URLs.

Passive techniques can provide useful context but may contain stale data.

---

## Active Enumeration

Active techniques interact directly with the target.

Examples include:

- HTTP probing;
- requesting application pages;
- examining headers;
- fingerprinting technologies;
- requesting non-existing resources;
- following redirects;
- probing known web ports.

Examples:

```bash
whatweb https://example.test
```

```bash
curl -I https://example.test
```

```bash
httpx -u https://example.test
```

Active enumeration generally produces more current information but must remain within the agreed scope and testing constraints.

---

# HTTP Status Codes

HTTP status codes are useful enumeration signals.

Common examples include:

| Status | General Meaning |
|---|---|
| 200 | Request succeeded |
| 201 | Resource created |
| 204 | Successful response without body |
| 301 | Permanent redirect |
| 302 | Temporary redirect |
| 307 | Temporary redirect preserving request method |
| 308 | Permanent redirect preserving request method |
| 400 | Bad request |
| 401 | Authentication required |
| 403 | Request understood but access denied |
| 404 | Resource not found |
| 405 | HTTP method not allowed |
| 429 | Rate limit or request throttling |
| 500 | Internal server error |
| 502 | Gateway or upstream error |
| 503 | Service unavailable |

A status code is useful context, but it should not be interpreted in isolation.

For example:

```text
403
```

may represent:

- genuine authorisation denial;
- WAF blocking;
- IP restrictions;
- missing authentication;
- reverse proxy behaviour;
- virtual host mismatch;
- application routing.

Similarly:

```text
404
```

may be:

- genuine resource absence;
- custom application response;
- soft 404;
- wildcard routing;
- intentional security behaviour.

---

# Response Titles

HTML page titles are useful for quickly understanding a large set of HTTP targets.

For example:

```text
200  Admin Portal
200  Grafana
302  Login
403  Forbidden
200  Jenkins
```

Titles may reveal:

- administrative interfaces;
- development systems;
- monitoring platforms;
- application names;
- product names;
- login interfaces;
- default applications.

Titles should be combined with other evidence because custom applications can use arbitrary titles.

---

# HTTP Headers

HTTP headers can provide valuable fingerprinting indicators.

Examples include:

```text
Server:
X-Powered-By:
Via:
X-AspNet-Version:
X-Generator:
X-Drupal-Cache:
X-Runtime:
X-Request-ID:
```

Example:

```http
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
```

Another example:

```http
HTTP/1.1 200 OK
X-Powered-By: Express
Content-Type: text/html; charset=utf-8
```

Headers may indicate a candidate technology, but they may also be:

- disabled;
- rewritten;
- inserted by proxies;
- removed by CDNs;
- intentionally misleading.

The absence of a technology header does not prove the technology is absent.

---

# Cookie Fingerprinting

Cookie names can sometimes provide useful application or framework indicators.

Examples may include session cookies, CSRF cookies, or framework-specific defaults.

A useful methodology is:

```text
Observe Cookie
      |
      v
Identify Possible Framework Association
      |
      v
Check Other Indicators
      |
      +-- Headers
      +-- HTML
      +-- JavaScript
      +-- Paths
      |
      v
Determine Confidence
```

Do not rely solely on cookie names.

Applications frequently rename default cookies.

---

# HTML Source

HTML can contain useful fingerprinting information.

Review:

- comments;
- generator tags;
- asset paths;
- script names;
- framework markers;
- template structure;
- application names;
- build identifiers;
- JavaScript framework artefacts.

Example:

```html
<meta name="generator" content="WordPress">
```

Another possible indicator might be characteristic asset paths.

Automated tools often perform this analysis internally, but manual inspection is valuable for confirming their results.

---

# JavaScript Fingerprinting

JavaScript files can reveal:

- frameworks;
- libraries;
- build systems;
- application routes;
- API endpoints;
- versions;
- source maps;
- package names;
- internal paths.

Related note:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

Useful questions include:

```text
Which bundles are loaded?

Which framework generated them?

Are source maps exposed?

Which API endpoints are referenced?

Are version strings visible?

Which third-party libraries are used?
```

JavaScript fingerprinting should be part of broader application analysis rather than a standalone conclusion.

---

# Default Error Pages

Default error pages are often useful technology indicators.

Useful responses include:

- 404 Not Found;
- 403 Forbidden;
- 500 Internal Server Error;
- framework routing errors;
- application exception pages;
- default container error pages.

A simple testing pattern is:

```text
Request random resource
      |
      v
/nonexistent-8472631
      |
      v
Observe response
      |
      +-- Status
      +-- HTML
      +-- Headers
      +-- Cookies
      +-- Error wording
      |
      v
Compare with known fingerprints
```

Example request:

```bash
curl -i https://example.test/nonexistent-8472631
```

A useful external comparison reference is:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

Default error pages can suggest a technology but should not be treated as definitive identification.

---

# Custom Error Pages

Applications frequently replace default framework error pages.

For example:

```text
Default framework response
        |
        v
Custom application template
        |
        v
Fingerprint hidden
```

This means failure to recognise a default 404 page does not mean the application cannot be fingerprinted.

Other indicators may still reveal the stack:

- cookies;
- headers;
- HTML structure;
- asset names;
- JavaScript bundles;
- application routes;
- TLS;
- response behaviour.

---

# Soft 404 Responses

Some applications return a `200 OK` response even when a requested resource does not exist.

Example:

```http
HTTP/1.1 200 OK
Content-Type: text/html
```

with body:

```text
Sorry, the page you requested does not exist.
```

This is commonly called a soft 404.

Soft 404 behaviour matters because it can affect:

- content discovery;
- automated scanners;
- response filtering;
- endpoint discovery;
- crawler output.

Always establish a baseline for non-existing resources.

Example:

```bash
curl -i https://example.test/random-not-found-918273
```

Record:

```text
Status:
Content length:
Word count:
Line count:
Title:
Body pattern:
```

This baseline becomes useful when interpreting tools such as ffuf.

---

# Redirect Analysis

Redirects frequently reveal application structure.

Examples include:

```text
http://example.test
        |
        v
https://example.test
```

or:

```text
/
 |
 v
/login
```

or:

```text
/app
 |
 v
/auth/signin
```

Useful observations include:

- destination;
- status code;
- hostname changes;
- scheme changes;
- path changes;
- authentication redirects;
- external redirects.

Example:

```bash
curl -I https://example.test
```

Example response:

```http
HTTP/1.1 302 Found
Location: /login
```

Following redirects can reveal the final application, but the intermediate redirect chain can also contain useful information.

---

# Virtual Hosts

Several websites may share the same IP address.

```text
             +--> app.example.test
IP Address --+--> admin.example.test
             +--> api.example.test
```

This is often implemented through HTTP virtual hosting.

Therefore:

```text
IP address
```

and:

```text
hostname
```

may return completely different applications.

When validating a web service, preserve the hostname where possible.

---

# TLS Information

TLS can provide additional reconnaissance information.

Useful observations include:

- certificate subject;
- Subject Alternative Names;
- issuer;
- validity period;
- protocol support;
- hostname relationships.

Certificate information may reveal additional hostnames.

However, certificate names must still be validated against scope before further testing.

```text
Certificate
    |
    v
Additional Hostname
    |
    v
Scope Check
    |
    +-- In scope -> investigate
    |
    +-- Out of scope -> record only
```

---

# Favicon Fingerprinting

Favicons can provide additional technology fingerprints.

A favicon can be:

- downloaded;
- hashed;
- compared with known fingerprints;
- correlated with product-specific behaviour.

This can sometimes assist in identifying:

- administrative products;
- monitoring tools;
- dashboards;
- frameworks;
- appliances.

Favicon matches should be treated as supporting evidence rather than definitive proof.

---

# Framework Asset Paths

Frameworks and applications often expose characteristic asset paths.

Examples of useful categories include:

```text
Static resources
Build assets
Framework bundles
Generated JavaScript
CSS
Image directories
Application-specific paths
```

These patterns can assist technology identification.

However, applications may:

- proxy assets;
- rename paths;
- bundle multiple technologies;
- retain legacy files;
- serve static resources through a CDN.

Therefore, path-based fingerprinting should be correlated with behavioural evidence.

---

# API Fingerprinting

APIs often reveal technology information differently from traditional web pages.

Useful indicators include:

- JSON error formats;
- response headers;
- default documentation endpoints;
- structured validation errors;
- route behaviour;
- authentication headers.

Example:

```json
{
  "detail": "Not Found"
}
```

This may resemble the default behaviour of particular frameworks, but additional evidence is required.

Related notes:

[API Security](../../web/api-security.md)

[GraphQL API Security](../../web/graphql.md)

[gRPC Security](../../web/grpc-security.md)

---

# Administrative Interfaces

Enumeration may reveal administrative or management interfaces.

Examples include:

```text
/admin
/login
/dashboard
/console
/manager
/manage
```

The existence of an administrative interface is not automatically a vulnerability.

It may still be useful attack-surface information.

Assess:

- authentication;
- exposure;
- network restrictions;
- MFA;
- authorisation;
- version information;
- default configuration.

Do not perform credential guessing unless specifically authorised.

---

# Technology Identification Confidence

Technology identification should be treated as a confidence problem.

A single indicator might provide low confidence:

```text
Server: nginx
```

Multiple independent indicators provide stronger confidence:

```text
WhatWeb
   |
   +-- nginx

HTTP Headers
   |
   +-- Server: nginx

404 Response
   |
   +-- nginx-style error page

TLS / Behaviour
   |
   +-- consistent architecture

Result
   |
   v
Higher Confidence
```

A useful confidence model is:

| Confidence | Evidence |
|---|---|
| Low | Single weak indicator |
| Moderate | Several related indicators |
| High | Multiple independent indicators |
| Confirmed | Direct technical evidence establishes the technology |

Avoid presenting low-confidence fingerprints as confirmed facts.

---

# Version Detection

Version identification requires additional caution.

For example:

```text
Server: Apache/2.4.x
```

does not automatically mean that every vulnerability associated with the upstream Apache version is exploitable.

Reasons include:

- vendor backports;
- distribution-specific patches;
- reverse proxies;
- modified banners;
- custom builds;
- security patches without version changes.

The correct workflow is:

```text
Version Indicator
       |
       v
Candidate Version
       |
       v
Vendor / Distribution Context
       |
       v
Security Advisory Review
       |
       v
Behavioural Validation
```

Do not report vulnerabilities solely because a banner appears to match an affected version.

---

# Establishing a Baseline

Before fuzzing or content discovery, establish normal application behaviour.

Request:

```text
/
```

then request a deliberately non-existing resource:

```text
/random-resource-482719
```

Compare:

| Property | Normal Page | Non-Existing Page |
|---|---|---|
| Status | ? | ? |
| Length | ? | ? |
| Words | ? | ? |
| Lines | ? | ? |
| Title | ? | ? |
| Redirect | ? | ? |

This helps distinguish real discoveries from generic application responses.

---

# Wildcard Behaviour

Some applications or infrastructure respond similarly for every requested path or hostname.

For example:

```text
/random-one
/random-two
/admin
/test
```

may all return:

```text
200 OK
Content-Length: 5234
```

This can create false positives during automated discovery.

Similarly, wildcard DNS may cause every hostname to resolve.

```text
random-123.example.test
random-456.example.test
admin.example.test
```

If they all resolve to the same infrastructure, subdomain discovery results require additional validation.

---

# Reverse Proxies and CDNs

Web enumeration may identify the technology directly exposed to the internet rather than the underlying application.

Example:

```text
Internet
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

A header might reveal:

```text
Server: cloud proxy
```

while the backend application uses a completely different technology.

Therefore, distinguish:

- edge technology;
- reverse proxy;
- application server;
- application framework.

---

# WAF Influence

A Web Application Firewall can influence enumeration output.

Possible effects include:

- blocked requests;
- altered status codes;
- generic error pages;
- connection termination;
- CAPTCHA responses;
- rate limiting;
- response replacement.

Example:

```text
Enumeration Request
       |
       v
      WAF
       |
       +-- Blocked
       +-- Modified
       +-- Allowed
       |
       v
Application
```

Unexpected behaviour should therefore be interpreted carefully.

---

# Authentication State

Fingerprinting results can differ before and after authentication.

Unauthenticated:

```text
/login
```

Authenticated:

```text
/dashboard
/api/
/admin/
/account/
```

Authentication can reveal a much larger attack surface.

Where authorised credentials are available, repeat relevant enumeration after authentication.

Do not assume anonymous reconnaissance represents the entire application.

---

# Multiple User Roles

Different application roles may expose different features.

Example:

```text
User
 |
 +-- Standard User
 |
 +-- Manager
 |
 +-- Administrator
```

Technology fingerprinting may remain the same, but:

- routes;
- APIs;
- JavaScript bundles;
- administrative functionality;
- integrations;

may differ.

Enumeration should therefore support later role-based testing.

---

# Output Normalisation

When working with many tools, consistent output becomes important.

Useful fields include:

```text
hostname
url
scheme
port
status
title
server
technology
redirect
ip
tls
notes
```

Example:

```text
https://portal.example.test
443
200
Customer Portal
nginx
React
-
192.0.2.10
TLS enabled
```

Structured output is especially useful when combining reconnaissance tools.

---

# Example Enumeration Pipeline

A common authorised reconnaissance workflow might look like:

```text
Known Domain
    |
    v
Subdomain Discovery
    |
    v
Resolved Hosts
    |
    v
httpx
    |
    +-- status
    +-- title
    +-- technology
    |
    v
Interesting Web Targets
    |
    +--> WhatWeb
    |
    +--> Wappalyzer
    |
    +--> curl
    |
    v
Manual Validation
    |
    v
Attack Surface Analysis
```

The important part is that each step reduces uncertainty.

---

# Manual Validation Workflow

For an interesting target:

```text
1. Record URL
2. Record HTTP status
3. Record redirect behaviour
4. Inspect headers
5. Inspect cookies
6. Inspect HTML source
7. Inspect JavaScript assets
8. Request a non-existing page
9. Compare default/error behaviour
10. Review WhatWeb/Wappalyzer/httpx results
11. Correlate the indicators
12. Record likely technologies and confidence
```

This produces more reliable reconnaissance than depending on a single tool.

---

# Example Evidence Record

A useful enumeration record may look like:

```text
Target:
https://portal.example.test

Observed:
HTTP 200

Title:
Customer Portal

Headers:
Server: nginx

WhatWeb:
nginx
JavaScript

Wappalyzer:
React
nginx

404 Behaviour:
Custom application error page

Additional Evidence:
React-style application bundle structure

Assessment:
nginx is strongly indicated.
React is likely used by the client-side application.

Confidence:
High for nginx.
Moderate to high for React.
```

Notice that this does not claim more than the evidence supports.

---

# Common Mistakes

## Trusting One Fingerprint

Bad approach:

```text
Wappalyzer says React
        |
        v
Technology confirmed
```

Better:

```text
Wappalyzer
    |
    v
Candidate
    |
    +--> JavaScript inspection
    +--> asset analysis
    +--> application behaviour
    |
    v
Higher confidence
```

---

## Treating Version Detection as Vulnerability Proof

Bad:

```text
Apache version found
        |
        v
CVE reported
```

Better:

```text
Version indicator
      |
      v
Candidate exposure
      |
      v
Vendor patch status
      |
      v
Technical validation
      |
      v
Finding if supported
```

---

## Ignoring Redirects

A redirect may reveal:

- canonical hostname;
- authentication boundary;
- application base path;
- HTTPS enforcement;
- another application.

Always inspect redirect chains.

---

## Ignoring Error Pages

Error responses may reveal:

- server;
- framework;
- backend behaviour;
- proxy layers;
- application routing.

Do not inspect only successful `200` responses.

---

## Ignoring Non-Standard Ports

Web services may exist on ports such as:

```text
8000
8080
8081
8443
8888
9000
9443
```

Port numbers alone do not prove a service type, so validate the protocol.

---

## Ignoring Scope Boundaries

Reconnaissance frequently discovers additional hostnames.

Discovery does not automatically grant permission to test them.

```text
New Hostname
    |
    v
Check Scope
    |
    +-- Authorised -> continue
    |
    +-- Not authorised -> record only
```

---

# False Positives

Fingerprinting tools may produce false positives because of:

- generic HTML patterns;
- shared JavaScript libraries;
- reused templates;
- reverse proxies;
- stale assets;
- copied error pages;
- custom headers;
- CDN behaviour;
- intentionally misleading banners.

Always inspect the evidence behind a fingerprint where the conclusion matters.

---

# False Negatives

Technologies may remain undetected because:

- headers are removed;
- error pages are customised;
- JavaScript is bundled;
- frameworks are hidden behind proxies;
- CDN behaviour masks the origin;
- fingerprint signatures are incomplete;
- applications use custom builds.

Absence from WhatWeb or Wappalyzer output does not prove absence from the application.

---

# Evidence to Capture

For important enumeration results, capture:

- target;
- date and time;
- tool;
- tool version where relevant;
- exact command;
- HTTP status;
- title;
- relevant headers;
- relevant cookies;
- redirect chain;
- technology indicators;
- screenshots where useful;
- raw response where useful;
- confidence;
- manual validation notes.

Do not retain unnecessary sensitive information.

---

# Reporting

Web enumeration results normally support later findings rather than becoming findings themselves.

For example:

```text
Technology fingerprinting indicated that the application was served
through nginx and used a client-side JavaScript framework. These
observations were used to guide subsequent testing.
```

Avoid statements such as:

```text
Wappalyzer proved the site uses framework X.
```

unless stronger evidence confirms the claim.

---

# Web Enumeration Checklist

## Scope

- [ ] Target is explicitly authorised.
- [ ] Hostnames are within scope.
- [ ] IP ranges are within scope.
- [ ] Third-party services are identified.
- [ ] Testing restrictions are understood.

## HTTP Services

- [ ] HTTP services identified.
- [ ] HTTPS services identified.
- [ ] Non-standard web ports reviewed.
- [ ] Redirect chains reviewed.
- [ ] Virtual hosting considered.

## Technology Fingerprinting

- [ ] WhatWeb used where appropriate.
- [ ] Wappalyzer used where appropriate.
- [ ] httpx metadata reviewed.
- [ ] Headers inspected.
- [ ] Cookies inspected.
- [ ] HTML inspected.
- [ ] JavaScript assets reviewed.
- [ ] Error pages reviewed.
- [ ] Version claims validated carefully.

## Application Behaviour

- [ ] Normal page baseline collected.
- [ ] Non-existing resource tested.
- [ ] Soft 404 behaviour considered.
- [ ] Authentication redirects reviewed.
- [ ] WAF behaviour considered.
- [ ] CDN/proxy behaviour considered.

## Validation

- [ ] Important fingerprints corroborated.
- [ ] Automated output manually reviewed.
- [ ] False-positive explanations considered.
- [ ] Confidence recorded appropriately.

## Evidence

- [ ] Relevant requests retained.
- [ ] Relevant responses retained.
- [ ] Commands recorded.
- [ ] Tool versions recorded where useful.
- [ ] Findings are based on technical evidence rather than tool labels.

---

# Related Tool Sections

[Security Tools](../index.md)

Planned detailed tool notes:

```text
docs/tools/web-enumeration/whatweb.md
docs/tools/web-enumeration/wappalyzer.md
docs/tools/web-enumeration/httpx.md
```

Related web testing tools:

[Web Application Testing Tools](../web-testing/index.md)

---

# Related Security Notes

[Web Application Security](../../web/index.md)

[Web Reconnaissance](../../web/reconnaissance/index.md)

[Subdomain Enumeration](../../web/reconnaissance/subdomain-enumeration.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Content Discovery](../../web/reconnaissance/content-discovery.md)

[Parameter Discovery](../../web/reconnaissance/parameter-discovery.md)

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

[API Security](../../web/api-security.md)

---

# References

## Official Tool Documentation

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

[ProjectDiscovery httpx](https://docs.projectdiscovery.io/opensource/httpx/overview){ target="_blank" rel="noopener noreferrer" }

[httpx Usage](https://docs.projectdiscovery.io/opensource/httpx/usage){ target="_blank" rel="noopener noreferrer" }

[Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }

[curl Documentation](https://curl.se/docs/){ target="_blank" rel="noopener noreferrer" }

## Web Security References

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Model

Web enumeration is not:

```text
Run WhatWeb
Run Wappalyzer
Run httpx
Copy output
```

It is:

```text
Define Scope
    |
    v
Identify Web Services
    |
    v
Collect HTTP Information
    |
    v
Fingerprint Technologies
    |
    v
Inspect Application Behaviour
    |
    v
Correlate Indicators
    |
    v
Validate Manually
    |
    v
Assign Confidence
    |
    v
Prioritise Testing
```

The strongest enumeration result is not the one produced by the largest number of tools.

It is the one where the available evidence has been interpreted correctly and can be used to make the next stage of testing more focused.
