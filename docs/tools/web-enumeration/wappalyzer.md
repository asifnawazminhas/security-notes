---
title: Wappalyzer
description: Practical Wappalyzer reference for web technology fingerprinting, browser-based reconnaissance, validation, interpretation, evidence collection, and integration with wider web assessment workflows.
---

# Wappalyzer

Wappalyzer is a technology profiling platform used to identify technologies associated with websites and web applications.

It can help identify categories such as:

- web frameworks;
- content management systems;
- JavaScript libraries;
- analytics platforms;
- tag managers;
- CDN providers;
- web servers;
- e-commerce platforms;
- development technologies;
- advertising platforms;
- customer-support platforms;
- infrastructure technologies;
- security technologies.

Wappalyzer is especially useful during interactive web reconnaissance because it can provide technology context while the tester is browsing the application.

```text
Browser
   |
   v
Target Application
   |
   v
Wappalyzer
   |
   +-- Framework
   +-- CMS
   +-- JavaScript
   +-- Server
   +-- CDN
   +-- Analytics
   +-- Other Technologies
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
    Use Wappalyzer only while assessing systems and applications that are explicitly authorised. Technology discovery may reveal third-party services, external domains, or infrastructure that is not automatically part of the assessment scope.

---

# Where Wappalyzer Fits

Wappalyzer normally fits into the technology-identification stage of web reconnaissance.

```text
Scope
  |
  v
Identify Reachable Web Application
  |
  v
Browse Application
  |
  v
Wappalyzer
  |
  +-- Technologies
  +-- Libraries
  +-- Infrastructure
  |
  v
Validate Indicators
  |
  v
Attack Surface Analysis
  |
  v
Focused Testing
```

Related methodology:

[Web Enumeration Tools](index.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Web Reconnaissance](../../web/reconnaissance/index.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

---

# What Wappalyzer Actually Does

Wappalyzer identifies technologies by looking for recognisable patterns in publicly observable web content.

Potential indicators can include:

```text
HTML
HTTP Headers
Cookies
JavaScript
Script URLs
Meta Tags
DOM Elements
CSS
Asset Paths
Response Behaviour
```

Conceptually:

```text
HTTP Response
      |
      +-- HTML
      +-- Headers
      +-- Cookies
      +-- Scripts
      +-- Metadata
      |
      v
Technology Detection Rules
      |
      v
Technology Matches
```

The important point is:

```text
Wappalyzer Match
      !=
Absolute Proof
```

Instead:

```text
Wappalyzer Match
      |
      v
Technology Indicator
      |
      v
Corroborate
```

---

# Browser-Based Use

A common way to use Wappalyzer is through browser-based technology detection.

The general workflow is:

```text
Open Application
      |
      v
Browse Important Pages
      |
      v
Review Wappalyzer Results
      |
      +-- Frontend Framework
      +-- CMS
      +-- Libraries
      +-- Infrastructure
      |
      v
Investigate Interesting Indicators
```

This is useful because technologies may only become visible after navigating specific parts of the application.

For example:

```text
/
    -> public frontend technologies

/login
    -> authentication technologies

/dashboard
    -> authenticated frontend

/admin
    -> separate administration application
```

Do not assume the technology profile from the homepage represents the entire application.

---

# Installation and Access

Wappalyzer is available through several interfaces and services.

Depending on the workflow, this may include:

- browser integration;
- hosted technology lookup;
- APIs;
- other Wappalyzer-supported products or interfaces.

Because available products and browser integrations can change over time, refer to the current official documentation for installation and usage options.

Official resource:

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

---

# Basic Reconnaissance Workflow

A practical workflow is:

```text
1. Open target in browser
       |
       v
2. Browse relevant pages
       |
       v
3. Review Wappalyzer
       |
       v
4. Record candidate technologies
       |
       v
5. Validate important matches
       |
       v
6. Use results to guide testing
```

For example:

```text
Wappalyzer:
React
nginx
Google Analytics
```

The next question is not:

> Which vulnerabilities affect React and nginx?

The next question is:

> Which of these technologies are actually present, where are they used, and what evidence supports the identification?

---

# Reading Technology Categories

Wappalyzer commonly groups detected technologies by category.

Examples may include:

| Category | Examples of What It Can Represent |
|---|---|
| JavaScript frameworks | Client-side application technologies |
| CMS | Content management platforms |
| Web servers | HTTP-serving technologies |
| CDN | Edge or content delivery infrastructure |
| Analytics | Tracking and analytics services |
| Tag managers | Client-side tag management |
| E-commerce | Shopping and payment-related platforms |
| Programming languages | Server-side or client-side language indicators |
| UI frameworks | Frontend presentation frameworks |

These categories help organise observations but do not necessarily reveal the full application architecture.

---

# Architecture Matters

A target may expose several technology layers at once.

For example:

```text
Cloudflare
    |
    v
nginx
    |
    v
Node.js
    |
    v
Express
    |
    v
React
```

These technologies may represent:

```text
Edge
 |
 v
Reverse Proxy
 |
 v
Runtime
 |
 v
Server Framework
 |
 v
Client Framework
```

Do not treat all detections as if they perform the same role.

---

# Wappalyzer vs WhatWeb

Wappalyzer and WhatWeb complement each other.

WhatWeb is particularly useful for command-line-driven fingerprinting.

Wappalyzer is particularly useful during interactive browser reconnaissance.

```text
WhatWeb
   |
   +-- CLI
   +-- automation-friendly
   +-- plugin-based fingerprinting

Wappalyzer
   |
   +-- interactive
   +-- browser context
   +-- broad technology categories
```

When both agree:

```text
WhatWeb:
React

Wappalyzer:
React

JavaScript assets:
React-related bundles
```

confidence increases.

When they disagree:

```text
WhatWeb:
Technology A

Wappalyzer:
Technology B
```

investigate the evidence rather than arbitrarily choosing one result.

Related note:

[WhatWeb](whatweb.md)

---

# Wappalyzer vs httpx

httpx is useful for large-scale HTTP discovery and enrichment.

Wappalyzer is useful for deeper interactive inspection.

A typical workflow is:

```text
Subdomains
    |
    v
httpx
    |
    v
Reachable Web Applications
    |
    v
Prioritised Targets
    |
    v
Browser + Wappalyzer
    |
    v
Technology Validation
```

This is usually more practical than manually browsing every discovered hostname.

Related note:

[httpx](httpx.md)

---

# Wappalyzer and Burp Suite

Wappalyzer can help identify technologies while Burp Suite provides request-level evidence.

```text
Browser
   |
   +--> Wappalyzer
   |
   +--> Burp Proxy
```

Wappalyzer may indicate:

```text
React
Express
nginx
```

Burp may then reveal:

```text
HTTP Headers
Cookies
API Calls
JavaScript Assets
Redirects
Authentication Flow
```

Combined analysis provides better context.

Related tool section:

[Web Application Testing Tools](../web-testing/index.md)

---

# Wappalyzer and curl

curl is useful for manually verifying HTTP-level indicators.

For example, Wappalyzer may identify nginx.

Check:

```bash
curl -I https://example.test
```

Representative output:

```http
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
```

This provides an additional independent indicator.

Another useful request is:

```bash
curl -i https://example.test
```

which shows both headers and response body.

Quick reference:

[curl Cheatsheet](../../cheatsheets/curl.md)

---

# Web Server Fingerprinting

Wappalyzer may identify web-server technologies.

Possible examples include:

```text
nginx
Apache HTTP Server
Microsoft IIS
LiteSpeed
```

A web-server fingerprint may come from:

- HTTP headers;
- error pages;
- characteristic response behaviour;
- other observable indicators.

Validate manually where the exact technology matters.

Example:

```bash
curl -I https://example.test
```

Possible output:

```http
Server: nginx
```

This increases confidence in the detection.

---

# Framework Fingerprinting

Framework detection may be based on several clues.

Potential indicators include:

- JavaScript globals;
- generated HTML;
- asset paths;
- cookies;
- response headers;
- DOM structures;
- framework-specific metadata.

Example workflow:

```text
Wappalyzer
     |
     v
Candidate Framework
     |
     +-- JavaScript
     +-- HTML
     +-- Assets
     +-- Cookies
     |
     v
Manual Confirmation
```

Framework identification should guide testing, not replace it.

---

# Client-Side Frameworks

Wappalyzer is particularly useful for identifying client-side frameworks.

Potential categories include:

```text
React
Vue
Angular
Svelte
other JavaScript frameworks
```

After detecting a frontend framework, review:

- JavaScript bundles;
- source maps;
- frontend routes;
- API calls;
- client-side state;
- third-party dependencies.

Related notes:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

[DOM-Based Vulnerabilities](../../web/dom-based-vulnerabilities.md)

[Third-Party JavaScript Security](../../web/third-party-javascript.md)

---

# CMS Detection

Wappalyzer may identify Content Management Systems.

Possible indicators include:

- HTML metadata;
- known resource paths;
- page structures;
- asset names;
- JavaScript;
- cookies.

A detected CMS should be validated.

For example:

```text
Wappalyzer
   |
   v
WordPress candidate
   |
   +-- HTML generator metadata
   +-- /wp-content/
   +-- /wp-includes/
   |
   v
Higher confidence
```

Do not immediately infer vulnerability from the CMS name.

---

# JavaScript Library Detection

Wappalyzer may identify JavaScript libraries.

Examples include:

```text
jQuery
React
Vue
Angular
Bootstrap
other libraries
```

Important questions include:

- Is the library actually used?
- Is a version detectable?
- Is it first-party or third-party?
- Is the identified version reliable?
- Are multiple versions present?
- Is the library loaded only on certain routes?

Related note:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

---

# Version Detection

Version information should be treated carefully.

If Wappalyzer reports:

```text
Technology X
Version 1.2.3
```

treat it as:

```text
Candidate Version
```

until independently validated.

Potential validation sources include:

- JavaScript filenames;
- package metadata;
- source maps;
- headers;
- HTML;
- documented application assets;
- direct behavioural evidence.

Do not report a vulnerability solely because a detected version appears in a CVE advisory.

---

# Why Version Detection Can Be Wrong

Version fingerprinting can be affected by:

- stale assets;
- cached JavaScript;
- copied libraries;
- customised builds;
- vendor backports;
- altered banners;
- reverse proxies;
- bundled dependencies.

Therefore:

```text
Detected Version
      |
      v
Candidate
      |
      v
Independent Validation
```

---

# HTTP Headers

Wappalyzer can use response headers as detection indicators.

Useful headers may include:

```text
Server
X-Powered-By
Via
X-AspNet-Version
X-Generator
```

Example:

```http
HTTP/1.1 200 OK
Server: nginx
X-Powered-By: Express
```

This may indicate multiple layers:

```text
nginx
  |
  v
Reverse Proxy
  |
  v
Express
```

Do not assume these represent conflicting results.

---

# Cookies

Cookie names can provide technology clues.

Examples of useful questions include:

```text
Does the cookie name match a framework default?

Is the cookie used for authentication?

Is it related to CSRF?

Is the name application-specific?

Could the application have renamed the default?
```

Cookie-based fingerprints should be considered supporting evidence.

---

# HTML Metadata

Some technologies expose metadata in HTML.

For example:

```html
<meta name="generator" content="Example CMS">
```

This can provide strong evidence, but still consider whether it may be:

- stale;
- manually added;
- copied from another template;
- intentionally misleading.

Manual inspection is valuable.

---

# JavaScript Globals

Some frontend technologies expose characteristic JavaScript objects or runtime behaviour.

Wappalyzer may use such indicators for detection.

Manual investigation may include:

- browser developer tools;
- loaded JavaScript;
- DOM inspection;
- network requests;
- framework-specific properties.

The exact indicator depends on the technology.

---

# Asset Paths

Asset paths may reveal framework or CMS information.

Useful categories include:

```text
Static JavaScript
CSS
Images
Framework bundles
CMS resource directories
Generated build artefacts
```

For example:

```text
/assets/
/static/
/_next/
/wp-content/
```

may contribute to technology identification depending on the broader context.

A path alone should not always be considered conclusive.

---

# Default Error Pages

Error pages provide an additional fingerprinting source.

Request a random path:

```bash
curl -i https://example.test/not-real-819273
```

Review:

```text
Status
Headers
HTML
Error wording
Footer
Cookies
```

The response may reveal:

- web server;
- framework;
- application server;
- routing behaviour.

A useful external reference is:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

Use it as a comparison aid rather than definitive proof.

---

# Combining Wappalyzer with 404 Fingerprinting

Example:

```text
Wappalyzer
    |
    v
Candidate Technology
    |
    v
Random 404 Request
    |
    v
Default Error Page
    |
    v
Compare Known Behaviour
    |
    v
Additional Evidence
```

Suppose:

```text
Wappalyzer:
Express

404 response:
Cannot GET /random-path

Headers:
X-Powered-By: Express
```

The combined evidence provides a stronger fingerprint than any one indicator alone.

---

# Custom Error Pages

A production application may hide default framework error pages.

```text
Framework
   |
   v
Custom Error Handler
   |
   v
Branded 404
```

In this case, error-page fingerprinting may provide little useful information.

Other indicators may still identify the technology.

---

# Response Behaviour

Technology identification can also come from behaviour rather than static strings.

Examples include:

- redirect patterns;
- routing behaviour;
- API error structures;
- authentication responses;
- default methods;
- content types;
- status-code behaviour.

For example:

```text
GET /nonexistent
        |
        v
JSON response
        |
        v
Characteristic API error format
```

This may help identify a framework family when combined with other evidence.

---

# API Fingerprinting

Traditional Wappalyzer detections may be less useful when an endpoint exposes only an API.

In that case, inspect:

- response headers;
- JSON error structures;
- OpenAPI endpoints;
- GraphQL endpoints;
- authentication headers;
- cookies;
- routing patterns.

Related notes:

[API Security](../../web/api-security.md)

[GraphQL API Security](../../web/graphql.md)

[gRPC Security](../../web/grpc-security.md)

---

# Authentication Changes Technology Visibility

Some technologies may only be visible after login.

For example:

```text
Unauthenticated
     |
     +-- generic login page

Authenticated
     |
     +-- React dashboard
     +-- API requests
     +-- analytics
     +-- administration modules
```

If authorised credentials are available, repeat technology review after authentication.

---

# Different Routes May Use Different Stacks

Modern applications are often composed of several components.

Example:

```text
/
   -> frontend application

/api/
   -> API service

/admin/
   -> administration interface

/legacy/
   -> older application
```

Wappalyzer results may vary between these routes.

Do not assume the root page represents the entire target.

---

# Microservices and Reverse Proxies

A single public hostname may route to multiple backend systems.

```text
Internet
   |
   v
Reverse Proxy
   |
   +--> Frontend
   |
   +--> API
   |
   +--> Authentication
   |
   +--> Legacy Application
```

Wappalyzer may identify technologies from several layers or only from the visible frontend.

This is why fingerprinting should be interpreted in architectural context.

---

# CDN Influence

CDNs can affect observable technology information.

They may:

- rewrite headers;
- terminate TLS;
- cache responses;
- serve error pages;
- hide backend addresses;
- inject their own indicators.

Therefore distinguish:

```text
Edge Technology
```

from:

```text
Application Technology
```

---

# WAF Influence

A Web Application Firewall may also affect what Wappalyzer observes.

Possible effects include:

- altered headers;
- generic block pages;
- CAPTCHA;
- denied resources;
- JavaScript challenges;
- bot-detection responses.

If the browser receives a WAF page rather than the application, Wappalyzer may profile the intermediary instead.

---

# Third-Party Technologies

Wappalyzer often identifies third-party technologies loaded by the application.

Examples include:

```text
Analytics
Tag Managers
Chat Widgets
Advertising
CDNs
Customer Support
Payment Providers
```

These detections may be useful for architecture understanding.

However:

> A third-party domain referenced by an in-scope application is not automatically in scope.

Do not test external providers without explicit authorisation.

---

# Tracking and Analytics Technologies

Analytics detections can reveal:

- tracking providers;
- tag managers;
- marketing platforms;
- monitoring scripts.

These are normally architecture observations rather than vulnerabilities.

They can, however, help identify third-party JavaScript dependencies that may deserve security review.

Related note:

[Third-Party JavaScript Security](../../web/third-party-javascript.md)

---

# Security Technologies

Wappalyzer may identify technologies related to:

- CDN protection;
- WAFs;
- bot management;
- security headers;
- identity providers.

Such detections can help explain application behaviour.

For example:

```text
Unexpected 403
      |
      v
WAF technology detected
      |
      v
Possible security-control response
```

The detection itself does not prove exactly how the control is configured.

---

# Login Page Profiling

Login pages often reveal technologies not visible elsewhere.

Review:

- identity-provider branding;
- cookies;
- JavaScript;
- authentication redirects;
- OAuth/OIDC endpoints;
- SAML endpoints;
- third-party identity services.

Related notes:

[Authentication Testing](../../web/authentication.md)

[OAuth 2.0 and OpenID Connect Security](../../web/oauth-oidc.md)

[SAML Security](../../web/saml.md)

---

# Administrative Interfaces

An administrative interface may use a different technology stack from the main application.

For example:

```text
Main Site:
React

Admin:
Angular

API:
Java
```

Browse authorised administration interfaces separately when they are in scope.

Do not assume a detected administration technology represents a security issue by itself.

---

# Technology Inventory

Wappalyzer results can contribute to a technology inventory.

Example:

| Target | Category | Technology | Supporting Evidence | Confidence |
|---|---|---|---|---|
| `portal.example.test` | Web server | nginx | Header + Wappalyzer | High |
| `portal.example.test` | Frontend | React | Wappalyzer + JS assets | High |
| `api.example.test` | API framework | Candidate | Error behaviour | Moderate |
| `blog.example.test` | CMS | WordPress | Wappalyzer + asset paths | High |

This is more useful than storing screenshots of technology names without context.

---

# Technology Confidence

A useful confidence model is:

| Confidence | Meaning |
|---|---|
| Low | One weak indicator |
| Moderate | Several related indicators |
| High | Multiple independent indicators |
| Confirmed | Direct evidence establishes the technology |

Example:

```text
Wappalyzer:
nginx

Confidence:
Low to Moderate
```

Then:

```text
HTTP header:
Server: nginx

404:
nginx default response
```

Now:

```text
Confidence:
High
```

---

# Correlation Workflow

Use several complementary data sources.

```text
Wappalyzer --------+
                   |
WhatWeb -----------+
                   |
HTTP Headers ------+----> Technology Hypothesis
                   |
JavaScript --------+
                   |
Error Page --------+
                   |
Manual Analysis ---+
```

The objective is not to maximise the number of tools.

The objective is to reduce uncertainty.

---

# False Positives

A Wappalyzer detection can be wrong.

Possible causes include:

- generic JavaScript;
- reused templates;
- copied HTML;
- stale resources;
- old framework assets;
- third-party libraries;
- proxy-generated content;
- shared page components;
- misleading headers.

Example:

```text
Wappalyzer:
WordPress

Manual review:
Only an old WordPress image path remains

Current application:
Custom application
```

Correct interpretation:

```text
A WordPress-related fingerprint was observed, but current use of
WordPress was not confirmed.
```

---

# False Negatives

Wappalyzer can also miss technologies.

Possible reasons include:

- headers removed;
- JavaScript bundled;
- framework identifiers stripped;
- custom application builds;
- authentication required;
- server-side technology hidden behind a proxy;
- technology not covered by current fingerprints.

Therefore:

```text
Not detected
```

does not mean:

```text
Not present
```

---

# Conflicting Results

Suppose:

```text
WhatWeb:
Apache

Wappalyzer:
nginx
```

Possible explanations include:

- reverse proxy in front of Apache;
- stale fingerprint;
- inconsistent responses;
- load-balanced backend systems;
- WAF or CDN behaviour;
- one tool producing a false positive.

Investigate:

```bash
curl -I https://example.test
```

Then compare multiple responses and routes.

The correct architecture may be:

```text
nginx
   |
   v
Apache
   |
   v
Application
```

Both tools could therefore have observed valid but different layers.

---

# JavaScript-Heavy Applications

Single-page applications may expose technology indicators primarily through JavaScript.

A useful workflow is:

```text
Wappalyzer
    |
    v
Frontend Framework Candidate
    |
    v
Browser DevTools
    |
    +-- Network
    +-- Sources
    +-- JavaScript
    +-- Source Maps
    |
    v
Manual Validation
```

Related note:

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

---

# Source Maps

Source maps can reveal:

- original source filenames;
- framework structure;
- development code;
- package information;
- application routes.

A framework detected by Wappalyzer may sometimes be corroborated through exposed source maps.

Source-map exposure should be evaluated separately for information-disclosure impact.

Related note:

[Information Disclosure](../../web/information-disclosure.md)

---

# Dependency Identification

A technology detection may reveal a library or framework that should be reviewed for dependency risk.

But:

```text
Library Detected
       |
       X
Do not immediately report CVEs
```

Instead:

```text
Library Detected
       |
       v
Version Validation
       |
       v
Deployment Context
       |
       v
Vendor Advisory
       |
       v
Technical Validation
```

Related note:

[Dependency Security](../../web/dependency-security.md)

---

# Browser Developer Tools

Browser developer tools complement Wappalyzer well.

Useful areas include:

```text
Network
Sources
Application
Storage
Console
Elements
```

Review:

- loaded scripts;
- API requests;
- cookies;
- local storage;
- application bundles;
- source maps;
- response headers.

Wappalyzer can indicate what to investigate, while developer tools show the underlying evidence.

---

# Wappalyzer and Source Code Review

Technology identification can also guide source code review.

For example:

```text
Wappalyzer:
Django
```

may suggest prioritising Django-specific source review when source access exists.

Related note:

[Django Source Code Review](../../source-code-review/django.md)

Similarly:

```text
Wappalyzer:
Flask
```

Related note:

[Flask Source Code Review](../../source-code-review/flask.md)

Technology fingerprinting can therefore connect black-box reconnaissance with white-box analysis.

---

# Wappalyzer and Attack Surface Analysis

A detected technology can guide the next phase.

Example:

```text
Wappalyzer
    |
    +-- React
    |
    +-- nginx
    |
    +-- identity provider
    |
    v
Attack Surface Questions
    |
    +-- JavaScript/API surface?
    +-- Reverse proxy behaviour?
    +-- OAuth/OIDC?
```

Related note:

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

The tool should help generate better questions.

---

# Practical Validation Scenario

Suppose Wappalyzer reports:

```text
React
nginx
Google Analytics
```

## Step 1 - Inspect HTTP Headers

```bash
curl -I https://example.test
```

Representative output:

```http
HTTP/1.1 200 OK
Server: nginx
Content-Type: text/html
```

This supports the nginx detection.

## Step 2 - Inspect HTML

Review the page source.

Representative example:

```html
<script src="/static/js/main.js"></script>
```

## Step 3 - Inspect JavaScript

Review the loaded bundle and browser developer tools for React-related runtime or build indicators.

## Step 4 - Review Third Parties

Confirm whether the analytics technology is loaded from an external service.

## Step 5 - Assign Confidence

```text
nginx:
High

React:
Moderate to High

Analytics:
High if script source is directly observed
```

This produces a more defensible technology profile than copying the Wappalyzer display alone.

---

# Example of a Misleading Detection

Suppose Wappalyzer reports a CMS.

Manual investigation finds:

```text
/legacy-assets/cms-logo.png
```

but no other evidence of the CMS.

The correct conclusion is:

```text
A fingerprint associated with the CMS was observed, but manual
validation did not establish that the current application is running
that CMS.
```

Do not overstate the result.

---

# Manual Validation Checklist for a Technology

When a technology matters to later testing, check several sources.

```text
Technology Candidate
        |
        +-- Headers?
        +-- Cookies?
        +-- HTML?
        +-- JavaScript?
        +-- Static Assets?
        +-- Error Pages?
        +-- Routing Behaviour?
        +-- Independent Tool?
        |
        v
Confidence
```

Not every technology requires exhaustive validation.

Focus effort where the identification affects:

- vulnerability research;
- testing strategy;
- attack surface;
- report conclusions;
- remediation.

---

# Larger Assessments

For large environments, Wappalyzer is usually better used selectively.

Example:

```text
2,000 hostnames
     |
     v
Subdomain Resolution
     |
     v
httpx
     |
     v
150 interesting HTTP endpoints
     |
     v
Prioritisation
     |
     v
Interactive Wappalyzer Review
```

This avoids spending manual browsing time on low-value or duplicate hosts.

---

# Prioritisation

Technology findings can help prioritise:

- legacy platforms;
- administrative systems;
- uncommon frameworks;
- development applications;
- externally exposed management tools;
- applications disclosing detailed versions.

Prioritisation is not the same as vulnerability confirmation.

---

# Evidence Collection

For relevant Wappalyzer results, capture:

```text
Target:
Date/time:
Page:
Detected technology:
Technology category:
Supporting header:
Supporting HTML:
Supporting JavaScript:
Supporting asset:
Additional tool result:
Confidence:
```

Example:

```text
Target:
https://portal.example.test

Page:
/

Wappalyzer:
React
nginx

Supporting evidence:
HTTP Server header indicated nginx.
JavaScript application bundles were consistent with a React frontend.

Confidence:
High for nginx.
Moderate to high for React.
```

---

# Screenshots

Screenshots can be useful when showing:

- the detected technology list;
- a corresponding application page;
- a relevant header or browser view.

However, a screenshot of the Wappalyzer interface alone is weak technical evidence.

Where a fingerprint matters, retain the underlying response or other supporting evidence.

---

# Reporting

Technology identification normally belongs in:

- reconnaissance notes;
- architecture observations;
- assessment methodology;
- supporting evidence.

Example wording:

```text
Technology fingerprinting indicated that the application used a
React-based client and was served through nginx. These observations
were corroborated through JavaScript asset analysis and HTTP response
headers.
```

Avoid:

```text
Wappalyzer proved that the application uses React and nginx.
```

The first statement explains the evidence.

---

# Technology Disclosure as a Finding

Technology information itself is not automatically a vulnerability.

Potentially security-relevant disclosure may include:

- exact vulnerable version information;
- internal infrastructure names;
- development error pages;
- stack traces;
- internal paths;
- sensitive framework configuration.

Evaluate actual impact.

Related note:

[Information Disclosure](../../web/information-disclosure.md)

---

# Common Mistakes

## Treating Wappalyzer as Proof

Bad:

```text
Wappalyzer -> Technology X
             |
             v
Technology X confirmed
```

Better:

```text
Wappalyzer
    |
    v
Candidate
    |
    v
Supporting Evidence
    |
    v
Confidence
```

---

## Looking Only at the Homepage

A homepage may expose only part of the application.

Review important routes where authorised.

---

## Ignoring Authenticated Areas

Authenticated functionality may expose different technologies.

---

## Ignoring Third Parties

Not every detected technology belongs to the organisation being assessed.

---

## Reporting CVEs from a Technology Name

A technology name alone does not establish:

- version;
- patch level;
- vulnerable configuration;
- exploitability.

---

## Ignoring Architectural Layers

A CDN, proxy, application server, framework, and frontend library may all appear in the same result.

Interpret them according to their role.

---

# Troubleshooting

## Wappalyzer Detects Nothing

Possible causes include:

- limited fingerprint exposure;
- unusual application stack;
- custom frontend;
- minimal HTML;
- bundled JavaScript;
- authentication boundary.

Use:

- WhatWeb;
- curl;
- browser developer tools;
- JavaScript analysis;
- manual response inspection.

---

## Detection Changes Between Pages

This may be normal.

Different routes may use different components.

Map the technologies to the routes where they appear.

---

## Browser Result Differs from CLI Tooling

Possible causes include:

- JavaScript execution;
- cookies;
- browser-specific responses;
- authentication;
- user-agent differences;
- dynamic content.

Compare equivalent requests.

---

## Technology Appears Only After Login

Repeat browser-based profiling after authentication if that activity is authorised.

---

## Third-Party Technology Dominates Results

Separate:

```text
Application Technology
```

from:

```text
Embedded Third-Party Technology
```

This avoids misrepresenting the target architecture.

---

# Wappalyzer Workflow

A strong workflow can be summarised as:

```text
1. Confirm authorised target
       |
       v
2. Open application
       |
       v
3. Browse representative routes
       |
       v
4. Review Wappalyzer technologies
       |
       v
5. Group by architectural role
       |
       v
6. Validate important matches
       |
       +-- HTTP headers
       +-- HTML
       +-- JavaScript
       +-- assets
       +-- cookies
       +-- error pages
       |
       v
7. Correlate with WhatWeb/httpx
       |
       v
8. Assign confidence
       |
       v
9. Use technology knowledge to guide testing
```

---

# Quick Validation Commands

Wappalyzer itself is commonly used interactively, but supporting validation can be performed with other tools.

## Headers

```bash
curl -I https://example.test
```

## Full Response

```bash
curl -i https://example.test
```

## Verbose HTTP/TLS Interaction

```bash
curl -v https://example.test
```

## Random 404

```bash
curl -i https://example.test/not-real-928173
```

## WhatWeb Comparison

```bash
whatweb https://example.test
```

## Nmap Service Identification

```bash
nmap -sV -p 80,443,8080,8443 example.test
```

Use supporting tools to investigate specific questions rather than automatically running every command.

---

# Wappalyzer Checklist

## Scope

- [ ] Target is authorised.
- [ ] Related third-party domains are recognised.
- [ ] Newly discovered domains are checked against scope before testing.

## Initial Review

- [ ] Homepage reviewed.
- [ ] Important application routes reviewed.
- [ ] Authenticated areas reviewed where authorised.
- [ ] Detected technologies recorded.
- [ ] Categories understood.

## Validation

- [ ] HTTP headers inspected where relevant.
- [ ] Cookies reviewed.
- [ ] HTML inspected.
- [ ] JavaScript assets inspected.
- [ ] Error pages reviewed.
- [ ] WhatWeb compared where useful.
- [ ] httpx information compared where useful.
- [ ] Conflicting results investigated.

## Version Analysis

- [ ] Version information treated as a candidate.
- [ ] Version evidence independently validated.
- [ ] Vendor patching/backports considered.
- [ ] CVEs not inferred solely from a detected product/version.

## Architecture

- [ ] Edge/CDN distinguished from backend.
- [ ] Reverse proxy distinguished from application server.
- [ ] Server-side and client-side technologies separated.
- [ ] Third-party technologies separated from target-owned components.

## Evidence

- [ ] Relevant page recorded.
- [ ] Relevant fingerprint recorded.
- [ ] Supporting technical evidence retained.
- [ ] Confidence documented.
- [ ] Tool output not presented as proof without validation.

---

# Related Tool Notes

[Web Enumeration Tools](index.md)

[WhatWeb](whatweb.md)

[httpx](httpx.md)

Related web testing:

[Web Application Testing Tools](../web-testing/index.md)

---

# Related Security Notes

[Web Application Security](../../web/index.md)

[Web Reconnaissance](../../web/reconnaissance/index.md)

[Technology Identification](../../web/reconnaissance/technology-identification.md)

[Attack Surface Analysis](../../web/attack-surface-analysis.md)

[JavaScript Analysis](../../web/reconnaissance/javascript-analysis.md)

[Information Disclosure](../../web/information-disclosure.md)

[Dependency Security](../../web/dependency-security.md)

[Third-Party JavaScript Security](../../web/third-party-javascript.md)

[Authentication Testing](../../web/authentication.md)

[API Security](../../web/api-security.md)

---

# External References

## Official Wappalyzer Resource

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

## Supporting Web Fingerprinting References

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use Wappalyzer like this:

```text
Open Wappalyzer
      |
      v
Copy Technology Names
      |
      v
Assume Architecture
```

Use it like this:

```text
Browse Target
      |
      v
Wappalyzer
      |
      v
Technology Candidates
      |
      v
Understand Architectural Role
      |
      +-- Edge?
      +-- Server?
      +-- Backend?
      +-- Framework?
      +-- Frontend?
      +-- Third Party?
      |
      v
Validate Indicators
      |
      +-- Headers
      +-- HTML
      +-- JavaScript
      +-- Cookies
      +-- Error Pages
      |
      v
Correlate With Other Tools
      |
      +-- WhatWeb
      +-- httpx
      +-- curl
      +-- Browser DevTools
      |
      v
Assign Confidence
      |
      v
Use Results to Guide Testing
```

The value of Wappalyzer is not simply identifying product names.

Its value is that it provides fast technology context during interactive reconnaissance, which can then be validated and used to make the remainder of the assessment more focused.
