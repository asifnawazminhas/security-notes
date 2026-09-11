---
title: WhatWeb
description: Practical WhatWeb reference for web technology fingerprinting, reconnaissance, output interpretation, validation, plugins, automation, evidence collection, and integration with wider web assessment workflows.
---

# WhatWeb

WhatWeb is a web technology fingerprinting tool used to identify technologies and implementation clues exposed by websites and web applications.

It can help identify indicators associated with:

- web servers;
- application frameworks;
- content management systems;
- JavaScript libraries;
- analytics platforms;
- blogging platforms;
- development technologies;
- cookies;
- HTTP headers;
- HTML content;
- page metadata;
- embedded scripts;
- characteristic application patterns.

WhatWeb is particularly useful during the early stages of a web assessment because it can quickly turn an unknown HTTP endpoint into a set of technology hypotheses for further investigation.

```text
Unknown Web Application
        |
        v
      WhatWeb
        |
        +-- Server
        +-- Framework
        +-- CMS
        +-- Libraries
        +-- Cookies
        +-- Headers
        +-- HTML Patterns
        |
        v
Technology Hypotheses
        |
        v
Manual Validation
        |
        v
Focused Testing
```

!!! warning "Authorised testing only"
    Run WhatWeb only against web applications and infrastructure that are explicitly within the authorised assessment scope. Higher aggression levels can generate additional requests and should only be used when permitted by the rules of engagement.

---

## Where WhatWeb Fits

WhatWeb normally fits between identifying reachable web services and performing deeper application testing.

```text
Asset Discovery
      |
      v
HTTP Probing
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
      v
Attack Surface Analysis
      |
      v
Focused Web Testing
```

Related methodology:

[Web Enumeration Tools](index.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Web Reconnaissance](../../web/reconnaissance/index.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

---

# What WhatWeb Actually Does

WhatWeb uses plugins containing fingerprints for known technologies.

A fingerprint may be based on indicators such as:

```text
HTTP Header
Cookie
HTML Pattern
Meta Tag
Script Reference
Text String
HTML Attribute
URL Pattern
Version Pattern
```

For example:

```text
HTTP Response
      |
      +-- Server: nginx
      |
      +-- WordPress asset path
      |
      +-- WordPress generator metadata
      |
      +-- jQuery reference
      |
      v
WhatWeb Plugins
      |
      v
Technology Matches
```

The important point is that WhatWeb does not magically determine the full architecture of an application.

It matches observable characteristics against known fingerprints.

Therefore:

```text
WhatWeb Match
      !=
Absolute Proof
```

Instead:

```text
WhatWeb Match
      |
      v
Technology Indicator
      |
      v
Corroborate
```

---

# Installation

WhatWeb is commonly available in penetration-testing distributions such as Kali Linux.

Check whether it is installed:

```bash
which whatweb
```

Check the installed version:

```bash
whatweb --version
```

Display help:

```bash
whatweb --help
```

If the tool is not installed, use the package-management method appropriate for the assessment workstation or follow the upstream installation instructions.

Official installation information:

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

---

# Basic Usage

The simplest form is:

```bash
whatweb https://example.test
```

WhatWeb can also accept multiple targets:

```bash
whatweb https://app.example.test https://portal.example.test
```

Representative output may resemble:

```text
https://example.test [200 OK] Country[RESERVED][ZZ], HTML5, HTTPServer[nginx], JQuery, Script, Title[Example Application]
```

The exact output depends on the target and installed WhatWeb version.

This output should be interpreted as a collection of detected indicators.

---

# Reading the Output

Consider:

```text
https://example.test [200 OK] HTTPServer[nginx], JQuery, Title[Portal]
```

This tells us several different things.

| Result | Interpretation |
|---|---|
| `200 OK` | The requested resource returned a successful HTTP response |
| `HTTPServer[nginx]` | WhatWeb observed evidence consistent with nginx |
| `JQuery` | A fingerprint associated with jQuery was identified |
| `Title[Portal]` | The HTML title was extracted as `Portal` |

The strongest output is usually the output that can be independently confirmed.

For example:

```text
WhatWeb:
HTTPServer[nginx]

Manual response:
Server: nginx

Result:
nginx is strongly indicated
```

---

# Inspecting a Single Target

Start with a normal fingerprint:

```bash
whatweb https://example.test
```

Then inspect the application manually.

For example:

```bash
curl -I https://example.test
```

or:

```bash
curl -i https://example.test
```

Compare the observations.

```text
WhatWeb
   |
   +-- nginx
   +-- jQuery
   +-- application title

curl
   |
   +-- Server header
   +-- cookies
   +-- redirect behaviour

Browser
   |
   +-- HTML
   +-- JavaScript
   +-- asset paths
```

The combined evidence is more useful than any individual tool result.

---

# Verbose Mode

Verbose mode provides more detail about detected plugins and fingerprints.

```bash
whatweb -v https://example.test
```

This is useful when the normal compact output does not explain why a technology was detected.

Use verbose output when asking:

> What caused WhatWeb to produce this fingerprint?

Verbose mode is especially useful during false-positive analysis.

---

# Aggression Levels

WhatWeb supports different aggression levels.

A normal assessment should generally begin with the default behaviour.

Example:

```bash
whatweb https://example.test
```

A more aggressive scan can be requested with:

```bash
whatweb -a 3 https://example.test
```

The important distinction is conceptual:

```text
Lower Aggression
      |
      +-- fewer requests
      +-- mostly passive fingerprinting
      +-- lower operational impact

Higher Aggression
      |
      +-- additional requests
      +-- deeper plugin checks
      +-- greater interaction
      +-- potentially greater operational impact
```

Do not automatically use aggressive scanning against every discovered host.

First consider:

- scope;
- target sensitivity;
- rate restrictions;
- application stability;
- number of hosts;
- testing window;
- engagement rules.

---

# Multiple Targets

WhatWeb can fingerprint multiple targets in one invocation.

For example:

```bash
whatweb https://app.example.test https://api.example.test https://portal.example.test
```

For a larger assessment, input from a file is generally easier to reproduce.

---

# Input Files

Targets can be supplied from a file.

Example:

```text
https://app.example.test
https://portal.example.test
https://api.example.test
```

Save the targets as:

```text
targets.txt
```

Then run:

```bash
whatweb -i targets.txt
```

This can fit into a larger reconnaissance workflow:

```text
Subdomain Discovery
        |
        v
HTTP Validation
        |
        v
targets.txt
        |
        v
WhatWeb
        |
        v
Technology Inventory
```

---

# Using WhatWeb After httpx

A useful workflow is to first identify reachable web endpoints using httpx.

For example:

```bash
httpx -l subdomains.txt -silent > alive-web.txt
```

Then:

```bash
whatweb -i alive-web.txt
```

Conceptually:

```text
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
WhatWeb
    |
    v
Technology Fingerprints
```

This prevents WhatWeb from spending time on hosts that do not appear to expose reachable HTTP services.

Related planned note:

[httpx](httpx.md)

---

# Suppressing Error Messages

During larger enumerations, unreachable endpoints can produce unnecessary console noise.

WhatWeb supports:

```bash
whatweb --no-errors https://example.test
```

It can also be useful with multiple targets:

```bash
whatweb --no-errors -i targets.txt
```

Do not confuse suppressed error messages with successful scans.

If an important target produces unexpected results, rerun it without suppression and inspect the error.

---

# Plugins

WhatWeb's detection capabilities are implemented through plugins.

List available plugins:

```bash
whatweb --list-plugins
```

The short form is:

```bash
whatweb -l
```

Plugins may identify technologies based on characteristics such as:

```text
HTML
Headers
Cookies
Scripts
Meta Tags
Text
URLs
Version Strings
```

Understanding plugins is useful when investigating why a particular technology was detected.

---

# Plugin Information

Information about plugins can be inspected using:

```bash
whatweb --info-plugins
```

A search can be supplied when supported by the installed version.

For example:

```bash
whatweb --info-plugins WordPress
```

The short option is commonly:

```bash
whatweb -I WordPress
```

This helps answer:

```text
WhatWeb reported WordPress
        |
        v
Which plugin produced that match?
        |
        v
Which fingerprint matched?
        |
        v
Can I reproduce the indicator manually?
```

This is much stronger than blindly accepting the detection.

---

# Focused Plugin Use

Where appropriate, WhatWeb can be restricted to selected plugins.

For example, a tester may want to focus on a specific technology family rather than load every available fingerprint.

Before using plugin-selection options:

```bash
whatweb --help
```

and inspect the installed version's supported syntax.

This is important because command-line behaviour can evolve between tool versions.

---

# Identifying Web Servers

One common use of WhatWeb is web-server fingerprinting.

Potential technologies may include:

```text
nginx
Apache HTTP Server
Microsoft IIS
LiteSpeed
other HTTP servers or proxies
```

Example:

```bash
whatweb https://example.test
```

Possible observation:

```text
HTTPServer[nginx]
```

Validate with:

```bash
curl -I https://example.test
```

Possible response:

```http
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
```

This provides independent supporting evidence.

---

# Framework Fingerprinting

WhatWeb can identify evidence associated with web frameworks.

A framework fingerprint may come from:

- cookies;
- characteristic headers;
- HTML patterns;
- generated content;
- framework assets;
- error messages.

Example workflow:

```text
WhatWeb
   |
   v
Candidate Framework
   |
   +--> Inspect cookies
   +--> Inspect headers
   +--> Inspect assets
   +--> Inspect JavaScript
   +--> Inspect error pages
   |
   v
Confidence Assessment
```

Framework identification is valuable because it can guide:

- attack-surface review;
- source-code expectations;
- framework-specific configuration checks;
- relevant security documentation.

---

# CMS Fingerprinting

WhatWeb is commonly used to identify Content Management Systems.

Potential clues include:

- generator metadata;
- static asset paths;
- application-specific directories;
- cookies;
- login pages;
- HTML structures;
- plugin-related resources.

Example:

```text
WhatWeb
    |
    v
Candidate CMS
    |
    +-- HTML metadata
    +-- asset paths
    +-- characteristic files
    |
    v
Manual Confirmation
```

Do not move immediately from:

```text
CMS detected
```

to:

```text
CMS is vulnerable
```

Technology presence and vulnerability are separate questions.

---

# JavaScript Libraries

WhatWeb may identify JavaScript libraries referenced by a page.

Examples of questions to ask after a detection include:

- Is the library actually used?
- Is the version exposed?
- Is it first-party or third-party?
- Is the detected version reliable?
- Is the asset locally hosted or externally hosted?
- Are multiple versions present?

Related notes:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

[Third-Party JavaScript Security](../../web/third-party-javascript.md)

---

# Version Identification

Some WhatWeb plugins may identify apparent version information.

For example:

```text
Technology[1.2.3]
```

Treat version detection with caution.

```text
Version Fingerprint
       |
       v
Candidate Version
       |
       v
Validate Source
       |
       +-- HTML
       +-- JavaScript
       +-- headers
       +-- package artefacts
       +-- direct behavioural evidence
```

A detected version does not automatically prove vulnerability.

---

# Backported Security Fixes

Server version numbers can be particularly misleading on operating systems that backport security patches.

For example:

```text
Software banner
      |
      v
Old-looking version
      |
      X
Do not immediately conclude:
"All upstream CVEs apply"
```

Instead consider:

```text
Banner
   |
   v
Operating System / Distribution
   |
   v
Vendor Package Version
   |
   v
Vendor Security Advisory
   |
   v
Technical Validation
```

This is important when interpreting fingerprints from Apache, nginx, OpenSSH, PHP, and other packaged software.

---

# HTTP Headers

WhatWeb can derive fingerprints from HTTP headers.

Potentially useful headers include:

```text
Server
X-Powered-By
Via
X-AspNet-Version
X-Generator
X-Runtime
```

Example:

```http
HTTP/1.1 200 OK
Server: nginx
X-Powered-By: Express
```

These may suggest multiple architectural layers:

```text
nginx
  |
  v
Reverse Proxy
  |
  v
Express Application
```

Do not assume every header describes the same component.

---

# Cookies

Cookies may also expose technology clues.

A fingerprint may come from:

- default session-cookie names;
- CSRF cookie names;
- framework-generated cookies;
- CMS-specific identifiers.

However:

```text
Cookie Name
    |
    v
Possible Framework
```

does not necessarily mean:

```text
Cookie Name
    |
    v
Confirmed Framework
```

Applications can rename cookies, and unrelated applications can reuse common names.

---

# HTML Metadata

HTML can reveal technologies through:

```html
<meta name="generator" content="Example CMS">
```

or characteristic comments and markup.

When WhatWeb identifies a technology from HTML:

1. inspect the page source;
2. locate the relevant indicator;
3. determine whether it appears intentional or stale;
4. corroborate it with other evidence.

---

# Static Asset Paths

Frameworks and CMS platforms often expose characteristic static resources.

Examples of useful categories include:

```text
JavaScript bundles
CSS paths
Image locations
CMS content directories
Framework-generated assets
Build artefacts
```

These can help corroborate WhatWeb output.

However, static artefacts may remain after a technology has been removed.

Therefore:

```text
Old Asset
   |
   v
Possible Historical Technology
```

is not necessarily:

```text
Current Technology
```

---

# Error Page Fingerprinting

Default error pages can provide additional fingerprinting evidence.

Request a deliberately non-existing path:

```bash
curl -i https://example.test/random-page-827361
```

Observe:

```text
Status
Headers
HTML
Error wording
Footer
Server identifier
Response structure
```

Then compare the result with known framework or server behaviours.

A useful external visual reference is:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

Use the reference for comparison, not as standalone proof.

---

# Combining WhatWeb with 404 Fingerprinting

A useful manual workflow is:

```text
WhatWeb
   |
   v
Candidate Technology
   |
   v
Request Random 404
   |
   v
Inspect Error Page
   |
   +-- wording
   +-- HTML
   +-- headers
   +-- footer
   |
   v
Compare with Known Defaults
   |
   v
Corroborate
```

For example:

```text
WhatWeb suggests nginx

404 page resembles nginx default response

Server header indicates nginx

Result:
High confidence that nginx is exposed at this layer
```

---

# Custom Error Pages

Many production applications replace framework and server default error pages.

Example:

```text
nginx
  |
  v
Application
  |
  v
Custom 404 template
```

In that case, the absence of a recognisable default 404 does not contradict the WhatWeb result.

Other indicators may still be available.

---

# Soft 404 Pages

Some applications return a successful HTTP status for resources that do not exist.

For example:

```http
HTTP/1.1 200 OK
```

with:

```text
The requested page does not exist.
```

This is commonly called a soft 404.

Before performing large-scale web discovery, establish how the application responds to random resources.

Example:

```bash
curl -i https://example.test/not-real-5837291
```

Record:

```text
Status
Content-Length
Title
Body pattern
Redirect
```

This baseline helps interpret later enumeration results.

---

# Redirects

WhatWeb may encounter applications that redirect from one endpoint to another.

Examples:

```text
HTTP
 |
 v
HTTPS
```

```text
example.test
 |
 v
www.example.test
```

```text
/
 |
 v
/login
```

The final application and the redirecting endpoint can expose different information.

Manually inspect:

```bash
curl -I https://example.test
```

and, where appropriate:

```bash
curl -IL https://example.test
```

Review the complete redirect chain rather than only the final page.

---

# Virtual Hosts

Fingerprinting by IP address may produce different results from fingerprinting the intended hostname.

Example:

```text
192.0.2.10
   |
   +-- app.example.test
   |
   +-- admin.example.test
   |
   +-- portal.example.test
```

Therefore prefer:

```bash
whatweb https://app.example.test
```

over blindly fingerprinting only:

```bash
whatweb https://192.0.2.10
```

when the hostname is known.

Virtual hosting can significantly affect:

- content;
- TLS;
- routing;
- application behaviour;
- technology fingerprints.

---

# Non-Standard Web Ports

Web services are not limited to ports 80 and 443.

Potential examples include:

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

If Nmap or another discovery mechanism identifies HTTP on an unusual port, WhatWeb can inspect the complete URL.

Example:

```bash
whatweb http://example.test:8080
```

or:

```bash
whatweb https://example.test:8443
```

Do not assume the protocol purely from the port number.

---

# HTTPS and TLS

When fingerprinting HTTPS services, TLS is part of the overall application exposure.

WhatWeb focuses primarily on web technologies, so complement it with tools appropriate for TLS analysis where necessary.

Useful observations may include:

- certificate subject;
- certificate SANs;
- issuer;
- hostname;
- proxy/CDN behaviour.

New hostnames discovered in certificates must still be checked against the authorised scope before further testing.

---

# Reverse Proxies

WhatWeb may fingerprint the edge component rather than the backend application.

For example:

```text
Internet
   |
   v
nginx
   |
   v
Application Server
   |
   v
Framework
```

A single request may therefore expose indicators for multiple technologies.

This is not necessarily contradictory.

Instead, consider whether they represent separate architectural layers.

---

# CDNs

Content Delivery Networks may alter or mask:

- server headers;
- response headers;
- error pages;
- TLS;
- caching;
- IP addresses.

Architecture may look like:

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

A WhatWeb fingerprint might identify characteristics from more than one layer.

---

# WAF Influence

A Web Application Firewall may affect fingerprinting.

Possible behaviours include:

- request blocking;
- CAPTCHA;
- rate limiting;
- altered error pages;
- generic responses;
- injected headers;
- connection termination.

Therefore:

```text
Unexpected WhatWeb Result
        |
        v
Inspect Raw HTTP
        |
        +-- WAF?
        +-- CDN?
        +-- Proxy?
        +-- Application?
```

---

# Authentication

Unauthenticated and authenticated parts of the same application may reveal different technologies.

For example:

```text
Unauthenticated
     |
     +-- login portal

Authenticated
     |
     +-- dashboard
     +-- administration
     +-- API
     +-- additional JavaScript
```

If authorised credentials are available, technology identification may need to be repeated after authentication.

WhatWeb itself is only one part of that analysis.

---

# Page-Specific Technologies

Different routes can expose different application components.

For example:

```text
/
    -> frontend

/api/
    -> API framework

/admin/
    -> administration application

/legacy/
    -> older application
```

Fingerprinting only the root page can therefore miss relevant technologies.

When reconnaissance reveals significant application components, inspect those components separately.

---

# WhatWeb and Wappalyzer

WhatWeb and Wappalyzer complement each other.

```text
WhatWeb
   |
   +-- command-line
   +-- automation-friendly
   +-- plugin-based fingerprints

Wappalyzer
   |
   +-- browser-oriented
   +-- interactive inspection
   +-- technology categories
```

When they agree:

```text
WhatWeb: React
Wappalyzer: React
JavaScript assets: React indicators
```

confidence increases.

When they disagree:

```text
WhatWeb: Technology A
Wappalyzer: Technology B
```

do not choose one arbitrarily.

Investigate the underlying fingerprints.

Detailed note:

[Wappalyzer](wappalyzer.md)

---

# WhatWeb and httpx

httpx is particularly useful for breadth.

WhatWeb is useful for deeper fingerprint enrichment.

Example:

```text
1,000 discovered hostnames
        |
        v
      httpx
        |
        v
120 live HTTP endpoints
        |
        v
      WhatWeb
        |
        v
Technology enrichment
```

This is generally more efficient than attempting detailed fingerprinting against every discovered hostname immediately.

Detailed note:

[httpx](httpx.md)

---

# WhatWeb and Nmap

Nmap and WhatWeb answer different questions.

Nmap:

```text
Which ports and services are exposed?
```

WhatWeb:

```text
What web technologies appear to be exposed by this HTTP endpoint?
```

Combined workflow:

```text
Nmap
  |
  +-- 80/tcp
  +-- 443/tcp
  +-- 8080/tcp
  |
  v
WhatWeb
  |
  v
Technology Fingerprinting
```

---

# WhatWeb and Burp Suite

WhatWeb provides quick fingerprinting.

Burp Suite provides deeper interactive validation.

```text
WhatWeb
   |
   v
Technology Hypothesis
   |
   v
Browser through Burp
   |
   +-- requests
   +-- responses
   +-- cookies
   +-- API calls
   +-- JavaScript
   |
   v
Application Understanding
```

This transition from automated reconnaissance to manual analysis is important.

---

# WhatWeb and curl

curl provides a simple way to inspect WhatWeb observations manually.

Example:

```bash
whatweb https://example.test
```

Then:

```bash
curl -I https://example.test
```

or:

```bash
curl -i https://example.test
```

For detailed request debugging:

```bash
curl -v https://example.test
```

Related quick reference:

[curl Cheatsheet](../../cheatsheets/curl.md)

---

# Logging Results

For repeatable assessments, save WhatWeb output rather than relying entirely on terminal history.

WhatWeb supports several logging mechanisms depending on the installed version.

Common examples include brief and verbose logs.

Example:

```bash
whatweb --log-brief=whatweb.txt -i targets.txt
```

For more detailed investigation:

```bash
whatweb --log-verbose=whatweb-verbose.txt -i targets.txt
```

Always check:

```bash
whatweb --help
```

for the exact logging formats supported by the installed version.

---

# JSON Output

Where supported by the installed version, WhatWeb can produce JSON-formatted logs.

This can be useful when results need to be processed programmatically.

Conceptually:

```text
WhatWeb
   |
   v
JSON
   |
   +--> jq
   |
   +--> Python
   |
   +--> custom reporting
   |
   v
Normalised Results
```

Check the available logging flags:

```bash
whatweb --help
```

before building automation around a particular output format.

---

# Separating Standard Output and Evidence

For large engagements, separate:

```text
Console output
```

from:

```text
assessment evidence
```

Console output may be useful during exploration.

Evidence should contain only the information necessary to support the assessment.

For example:

```text
Target:
https://portal.example.test

Tool:
WhatWeb

Relevant fingerprint:
nginx
React

Manual validation:
Server header indicated nginx.
Client-side assets contained React-related application bundles.

Confidence:
High for nginx.
Moderate to high for React.
```

---

# Automation Workflow

A practical automation pipeline might be:

```text
domains.txt
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
WhatWeb
    |
    v
Technology Inventory
```

Automation should make reconnaissance more manageable, not remove manual analysis.

---

# Large Target Sets

When dealing with many targets:

1. deduplicate targets;
2. confirm scope;
3. identify live HTTP services;
4. control request volume;
5. fingerprint the reduced set;
6. save structured results;
7. prioritise interesting technologies;
8. manually validate important targets.

Avoid:

```text
Huge scope
    |
    v
Run every tool at maximum intensity
```

Prefer:

```text
Huge scope
    |
    v
Reduce
    |
    v
Enrich
    |
    v
Prioritise
    |
    v
Investigate
```

---

# Prioritising Results

Some fingerprints may warrant earlier investigation.

Examples include:

- administrative products;
- legacy frameworks;
- uncommon technologies;
- exposed development interfaces;
- management platforms;
- CMS platforms;
- unusual server combinations;
- applications revealing detailed version information.

Prioritisation does not mean declaring them vulnerable.

It means deciding where deeper assessment effort may provide the most value.

---

# Interpreting Multiple Technologies

A single page may legitimately contain many technologies.

For example:

```text
nginx
PHP
WordPress
jQuery
Google Analytics
Cloudflare
```

These may represent:

```text
Cloud / Edge
   |
   v
Web Server
   |
   v
Server-Side Runtime
   |
   v
Application / CMS
   |
   v
Client-Side Libraries
   |
   v
Third-Party Services
```

Do not interpret the result as if all technologies perform the same role.

---

# Technology Inventory

For a larger environment, build a technology inventory.

Example:

| Target | Status | Server | Framework/CMS | Client Technology | Confidence |
|---|---:|---|---|---|---|
| `portal.example.test` | 200 | nginx | Unknown | React | High / Moderate |
| `blog.example.test` | 200 | Apache | WordPress | jQuery | High |
| `api.example.test` | 401 | nginx | API framework candidate | N/A | Moderate |

This can help prioritise later testing.

---

# False Positives

A WhatWeb fingerprint can be incorrect.

Possible causes include:

- generic strings;
- copied HTML;
- stale assets;
- reused templates;
- reverse proxies;
- shared libraries;
- common cookie names;
- custom server headers;
- legacy files.

Example:

```text
WhatWeb:
WordPress

Reason:
Old /wp-content/ reference remains

Current application:
No longer WordPress
```

Therefore investigate why the fingerprint matched.

---

# False Negatives

WhatWeb can also miss technologies.

Possible causes include:

- removed headers;
- bundled assets;
- customised error pages;
- renamed cookies;
- reverse proxies;
- custom builds;
- unsupported fingerprints;
- JavaScript rendering;
- authentication boundaries.

Therefore:

```text
WhatWeb did not identify framework X
```

does not prove:

```text
Framework X is absent
```

---

# JavaScript-Heavy Applications

Modern single-page applications can make traditional fingerprinting more difficult.

Initial HTML may contain little more than:

```html
<div id="root"></div>
```

with most application functionality loaded through JavaScript.

In these cases combine WhatWeb with:

- browser inspection;
- Wappalyzer;
- JavaScript analysis;
- asset inspection;
- source maps;
- network traffic;
- API discovery.

Related note:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

---

# APIs

WhatWeb is primarily useful for web technology fingerprinting and may provide less context on API-only endpoints.

For APIs, inspect:

- response headers;
- content types;
- authentication behaviour;
- JSON error formats;
- API documentation;
- routing patterns.

Related notes:

[API Security](../../web/api-security.md)

[GraphQL API Security](../../web/graphql.md)

[gRPC Security](../../web/grpc-security.md)

---

# Unknown Fingerprints

Sometimes WhatWeb produces little or no meaningful technology information.

Do not interpret this as failure.

Instead switch to manual fingerprinting:

```text
WhatWeb
   |
   v
Little Information
   |
   +--> headers
   +--> cookies
   +--> source
   +--> JavaScript
   +--> 404
   +--> TLS
   +--> application behaviour
   |
   v
Manual Technology Analysis
```

Strong reconnaissance is methodology-driven rather than tool-dependent.

---

# Representative Validation Scenario

Suppose WhatWeb reports:

```text
HTTPServer[nginx]
JQuery
Title[Customer Portal]
```

## Step 1 - Inspect Headers

```bash
curl -I https://example.test
```

Representative result:

```http
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
```

### Step 2 - Inspect HTML

Review the page source for script references.

Representative example:

```html
<script src="/assets/jquery.min.js"></script>
```

### Step 3 - Test an Unknown Path

```bash
curl -i https://example.test/not-real-937251
```

Review whether the error response contains additional server or framework information.

### Step 4 - Compare Results

```text
WhatWeb
    -> nginx
    -> jQuery

Headers
    -> nginx

HTML
    -> jQuery asset

Result
    -> fingerprints corroborated
```

### Interpretation

The combination of independent observations provides stronger evidence than the original WhatWeb result alone.

---

# Example Where WhatWeb Is Wrong

Suppose WhatWeb identifies:

```text
TechnologyX
```

Manual investigation finds that the fingerprint comes from:

```html
<!-- Migrated from TechnologyX in 2022 -->
```

No other technology-specific indicators are present.

The correct conclusion is not:

```text
Application uses TechnologyX
```

Instead:

```text
WhatWeb produced a TechnologyX fingerprint based on residual page
content, but manual validation did not confirm that TechnologyX is
currently used by the application.
```

This is why understanding the fingerprint matters.

---

# Troubleshooting

## No Output

First confirm the endpoint is reachable:

```bash
curl -I https://example.test
```

Then check WhatWeb:

```bash
whatweb -v https://example.test
```

Possible causes include:

- DNS failure;
- connection failure;
- TLS problems;
- proxy requirements;
- WAF blocking;
- unsupported response;
- no matching fingerprints.

---

## Connection Errors

Check DNS:

```bash
getent hosts example.test
```

Check connectivity:

```bash
curl -I https://example.test
```

Where appropriate:

```bash
nmap -p 80,443 example.test
```

---

## Unexpected Redirects

Inspect manually:

```bash
curl -I https://example.test
```

Then review:

```text
Location:
```

The hostname or destination may explain the unexpected fingerprint.

---

## Fingerprint Differs from Browser

Possible reasons include:

- browser-specific responses;
- JavaScript rendering;
- cookies;
- authentication;
- user-agent differences;
- WAF logic;
- geographic routing;
- CDN caching.

Compare the exact requests before deciding that one tool is incorrect.

---

## Missing Technology

Possible explanations include:

- no plugin fingerprint exists;
- fingerprint is hidden;
- technology is behind a reverse proxy;
- application has been heavily customised;
- required resources are only loaded after authentication;
- client-side rendering is involved.

Use other evidence.

---

# Evidence Collection

For an important fingerprint, capture:

```text
Target:
Tool:
Tool version:
Command:
Date/time:
HTTP status:
Fingerprint:
Supporting headers:
Supporting HTML:
Supporting assets:
Manual validation:
Confidence:
```

Example:

```text
Target:
https://portal.example.test

Tool:
WhatWeb

Observed:
HTTPServer[nginx]
JQuery

Supporting evidence:
Server header returned nginx.
HTML included a jQuery script asset.

Confidence:
High for nginx.
High for jQuery being loaded by the page.
```

---

# Reporting

Technology fingerprinting normally supports the assessment rather than becoming a vulnerability finding itself.

Useful wording:

```text
Technology fingerprinting and manual response analysis indicated that
the application was served through nginx. The identification was
supported by both automated fingerprinting and the HTTP Server header.
```

Avoid:

```text
WhatWeb proved that nginx is installed.
```

The first statement describes the evidence.

The second overstates what the tool knows.

---

# When Technology Disclosure Becomes Relevant

Technology identification itself is usually normal reconnaissance.

However, excessive exposure may become security-relevant where the application unnecessarily discloses:

- detailed product versions;
- internal hostnames;
- development framework errors;
- stack traces;
- backend implementation details;
- internal paths.

Related note:

[Information Disclosure](../../web/information-disclosure.md)

Technology disclosure should still be assessed according to actual risk and context.

---

# Tool Result vs Security Finding

Keep this distinction clear:

```text
WhatWeb says:
nginx

This is:
Technology information

This is NOT automatically:
A vulnerability
```

Likewise:

```text
WhatWeb says:
WordPress 6.x

This is:
Candidate technology/version information

This is NOT automatically:
A vulnerable WordPress installation
```

Further security validation is required.

---

# Practical Workflow

A strong WhatWeb workflow can be summarised as:

```text
1. Confirm scope
       |
       v
2. Identify reachable web service
       |
       v
3. Run default WhatWeb fingerprinting
       |
       v
4. Review output
       |
       v
5. Investigate interesting plugins
       |
       v
6. Inspect headers and HTML
       |
       v
7. Inspect cookies and assets
       |
       v
8. Compare error pages
       |
       v
9. Correlate with Wappalyzer/httpx
       |
       v
10. Assign confidence
       |
       v
11. Use result to guide deeper testing
```

---

# Quick Command Reference

## Version

```bash
whatweb --version
```

## Help

```bash
whatweb --help
```

## Single Target

```bash
whatweb https://example.test
```

## Multiple Targets

```bash
whatweb https://app.example.test https://portal.example.test
```

## Input File

```bash
whatweb -i targets.txt
```

## Verbose Output

```bash
whatweb -v https://example.test
```

## Aggression Level 3

```bash
whatweb -a 3 https://example.test
```

## Suppress Errors

```bash
whatweb --no-errors -i targets.txt
```

## List Plugins

```bash
whatweb --list-plugins
```

or:

```bash
whatweb -l
```

## Plugin Information

```bash
whatweb --info-plugins WordPress
```

## Brief Log

```bash
whatweb --log-brief=whatweb.txt -i targets.txt
```

## Verbose Log

```bash
whatweb --log-verbose=whatweb-verbose.txt -i targets.txt
```

Always confirm options against the installed version:

```bash
whatweb --help
```

---

# WhatWeb Checklist

## Preparation

- [ ] Target is authorised.
- [ ] Hostname is within scope.
- [ ] Correct scheme is known.
- [ ] Relevant ports are known.
- [ ] WhatWeb version is recorded where useful.
- [ ] Rules of engagement permit active fingerprinting.

## Initial Fingerprinting

- [ ] Run default fingerprinting first.
- [ ] Record HTTP status.
- [ ] Review identified technologies.
- [ ] Review server fingerprint.
- [ ] Review framework/CMS indicators.
- [ ] Review JavaScript/library indicators.

## Validation

- [ ] Inspect HTTP headers.
- [ ] Inspect cookies.
- [ ] Inspect HTML source.
- [ ] Inspect static assets.
- [ ] Inspect JavaScript where relevant.
- [ ] Review default/error pages.
- [ ] Compare WhatWeb with Wappalyzer where useful.
- [ ] Compare WhatWeb with httpx where useful.
- [ ] Investigate conflicting fingerprints.

## Version Analysis

- [ ] Treat versions as candidates.
- [ ] Consider vendor backports.
- [ ] Consider reverse proxies.
- [ ] Consider stale assets.
- [ ] Validate security advisories independently.
- [ ] Do not infer vulnerability solely from a version string.

## Larger Assessments

- [ ] Deduplicate targets.
- [ ] Probe HTTP services first.
- [ ] Store target lists.
- [ ] Save useful logs.
- [ ] Prioritise interesting fingerprints.
- [ ] Control request intensity.

## Evidence

- [ ] Exact target recorded.
- [ ] Command recorded.
- [ ] Relevant output retained.
- [ ] Supporting evidence retained.
- [ ] Confidence documented.
- [ ] Tool output distinguished from confirmed findings.

---

# Related Tool Notes

[Web Enumeration Tools](index.md)

[Wappalyzer](wappalyzer.md)

[httpx](httpx.md)

Related web testing tools:

[Web Application Testing Tools](../web-testing/index.md)

---

# Related Security Notes

[Web Application Security](../../web/index.md)

[Web Reconnaissance](../../web/reconnaissance/index.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

[Content Discovery](../../web/reconnaissance/content-discovery.md)

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

[Information Disclosure](../../web/information-disclosure.md)

[Third-Party JavaScript Security](../../web/third-party-javascript.md)

---

# External References

## Official WhatWeb Resources

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

The installed command-line help should also be treated as an authoritative reference for the exact version in use:

```bash
whatweb --help
```

---

## Supporting Fingerprinting References

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

WhatWeb should not be used like this:

```text
Run WhatWeb
    |
    v
Copy Technology Names
    |
    v
Assume Everything Is Correct
```

Use it like this:

```text
Identify Web Target
        |
        v
Run WhatWeb
        |
        v
Review Fingerprints
        |
        v
Understand Why They Matched
        |
        +-- Headers
        +-- Cookies
        +-- HTML
        +-- Assets
        +-- JavaScript
        +-- Error Pages
        |
        v
Correlate With Other Tools
        |
        +-- Wappalyzer
        +-- httpx
        +-- curl
        +-- Browser
        |
        v
Assign Confidence
        |
        v
Use the Result to Guide Testing
```

The value of WhatWeb is not simply that it prints technology names.

Its value is that it quickly provides hypotheses about an application's technology stack that can then be verified and used to make the rest of the assessment more focused.
