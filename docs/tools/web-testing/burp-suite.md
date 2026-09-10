---
title: Burp Suite
description: Practical Burp Suite reference for authorised web application testing, including Community and Professional editions, Proxy, Repeater, Intruder, Comparer, Decoder, Sequencer, Scanner, Collaborator, extensions, authenticated workflows, evidence collection, and validation.
---

# Burp Suite

Burp Suite is one of the most widely used platforms for manual and semi-automated web application security testing.

Its main strength is that it sits directly between the tester and the application, allowing HTTP and WebSocket traffic to be inspected, modified, replayed, compared, automated, and extended.

```text
Browser
   |
   v
Burp Suite
   |
   +-- Proxy
   +-- HTTP History
   +-- Repeater
   +-- Intruder
   +-- Decoder
   +-- Comparer
   +-- Sequencer
   +-- Extensions
   +-- Scanner            [Professional]
   +-- Collaborator       [Professional workflows]
   |
   v
Target Application
```

Burp Suite should not be treated as a scanner that replaces methodology.

The strongest workflow is:

```text
Understand Application
        |
        v
Capture Request
        |
        v
Establish Baseline
        |
        v
Modify One Variable
        |
        v
Observe Difference
        |
        v
Interpret Behaviour
        |
        v
Validate Security Impact
        |
        v
Capture Evidence
```

!!! warning "Authorised testing only"
    Use Burp Suite only against applications and APIs that are explicitly authorised for testing. Automated scanning, Intruder attacks, out-of-band testing, and repeated authenticated requests can create significant traffic or alter application state. Confirm the rules of engagement before using high-volume or intrusive functionality.

---

# Where Burp Suite Fits

Burp Suite is useful throughout most phases of a web assessment.

```text
Reconnaissance
      |
      v
Application Mapping
      |
      v
Proxy Traffic
      |
      v
Identify Interesting Requests
      |
      v
Manual Testing
      |
      +-- Repeater
      +-- Comparer
      +-- Decoder
      +-- Intruder
      |
      v
Automated Assistance
      |
      +-- Scanner
      +-- Extensions
      |
      v
Manual Validation
      |
      v
Evidence
```

Related methodology:

[Web Application Testing Tools](index.md)

[Web Application Security](../../web/index.md)

[Web Application Testing Methodology](../../web/methodology.md)

[Web Application Pentesting Checklist](../../web/checklist.md)

---

# Community vs Professional

Burp Suite is available in multiple editions.

For practical security work, the most important distinction is usually between Community Edition and Professional.

## Community Edition

Community Edition is suitable for many manual testing activities.

Useful capabilities include:

- Proxy;
- HTTP history;
- Repeater;
- Decoder;
- Comparer;
- Sequencer;
- extensions;
- manual WebSocket inspection;
- manual request manipulation.

It is entirely possible to perform serious manual testing with Community Edition.

## Professional Edition

Professional adds functionality intended for larger, faster, and more automated assessment workflows.

Important examples include:

- Burp Scanner;
- crawling and auditing;
- enhanced Intruder capability;
- Burp Collaborator integration;
- additional automated discovery and testing workflows.

Exact edition differences can change over time.

Always verify current product capabilities against:

[Burp Suite Editions](https://portswigger.net/burp){ target="_blank" rel="noopener noreferrer" }

---

# A Better Way to Think About Editions

Do not think:

```text
Community
   =
Weak

Professional
   =
Powerful
```

A better model is:

```text
Community
   |
   +-- strong manual testing
   +-- learning workflows
   +-- request manipulation
   +-- protocol understanding

Professional
   |
   +-- everything above
   +-- automation
   +-- scanner
   +-- faster repeated testing
   +-- Collaborator integration
```

The core testing skill remains understanding application behaviour.

---

# Initial Setup

A normal setup places Burp between the browser and target application.

```text
Browser
   |
   v
Burp Proxy
   |
   v
Application
```

The browser sends requests through Burp.

Burp can then:

- intercept them;
- inspect them;
- modify them;
- forward them;
- store them in HTTP history.

---

# Burp Browser

Burp provides an embedded browser configured to work with Burp's proxy.

This is often the easiest way to begin testing because:

- proxy settings are already configured;
- HTTPS interception is handled;
- requests immediately appear in Proxy history.

For many assessments:

```text
Burp
   |
   v
Proxy
   |
   v
Open Browser
```

is enough to begin application mapping.

---

# External Browser Setup

A separate browser can also be configured to use Burp as an HTTP proxy.

A common local proxy configuration is:

```text
127.0.0.1:8080
```

The exact listener should be confirmed in:

```text
Proxy
  -> Proxy settings
  -> Proxy listeners
```

The browser must trust Burp's CA certificate if HTTPS interception is required.

---

# Burp CA Certificate

HTTPS interception works because Burp acts as a local TLS interception proxy.

Conceptually:

```text
Browser
   |
 TLS
   |
   v
Burp
   |
 TLS
   |
   v
Application
```

The browser sees certificates generated by Burp.

For a dedicated testing browser, install the Burp CA according to the official documentation.

Do not install testing CA certificates broadly across production workstations unless there is a justified need.

Official documentation:

[Installing Burp's CA Certificate](https://portswigger.net/burp/documentation/desktop/external-browser-config/certificate){ target="_blank" rel="noopener noreferrer" }

---

# Proxy Intercept

Intercept allows requests to be paused before they are forwarded.

This provides an opportunity to modify:

- parameters;
- headers;
- cookies;
- HTTP methods;
- request bodies;
- content types;
- tokens.

Example conceptual flow:

```text
Browser Request
      |
      v
Intercept
      |
      +-- modify
      +-- forward
      +-- drop
      |
      v
Application
```

Intercept is useful for focused testing.

For normal browsing, leaving interception off while reviewing HTTP history is often more convenient.

---

# HTTP History

HTTP history records proxied HTTP traffic.

It is one of the most useful areas for mapping an application.

Review:

```text
Host
Method
URL
Status
MIME type
Extension
Length
Comment
Highlight
```

Typical interesting requests include:

- login;
- logout;
- password reset;
- user profile;
- admin endpoints;
- file uploads;
- API calls;
- role changes;
- object access;
- search;
- export functions;
- state-changing actions.

---

# Application Mapping

A practical mapping workflow is:

```text
Browse Application
       |
       v
HTTP History
       |
       +-- Pages
       +-- APIs
       +-- Static Assets
       +-- Authentication
       +-- Background Requests
       |
       v
Identify Security-Sensitive Endpoints
```

Map the application before deeply testing individual parameters.

---

# Site Map

Burp can build a hierarchical view of observed application content.

This can help identify:

- paths;
- endpoints;
- parameters;
- APIs;
- hostnames;
- files;
- application structure.

Use the site map together with HTTP history rather than relying on one view alone.

---

# Scope

Burp scope configuration is important.

Without scope control, HTTP history can become noisy with:

- analytics domains;
- CDNs;
- browser background traffic;
- third-party APIs;
- advertising;
- update services.

Define the assessment target appropriately.

Conceptually:

```text
All Browser Traffic
      |
      v
Burp Scope
      |
      +-- In Scope
      |
      +-- Out of Scope
```

This also helps avoid accidental interaction with third-party systems.

---

# Scope Is Not Authorisation

An important distinction:

```text
Burp Scope
     !=
Legal / Contractual Scope
```

Adding a hostname to Burp scope does not grant authorisation to test it.

The rules of engagement remain authoritative.

---

# Repeater

Repeater is one of the most important Burp tools.

It allows the tester to manually replay HTTP requests repeatedly.

A strong testing pattern is:

```text
Capture Valid Request
        |
        v
Send to Repeater
        |
        v
Send Baseline
        |
        v
Change One Variable
        |
        v
Send Again
        |
        v
Compare Result
```

This isolates cause and effect.

---

# Sending Requests to Repeater

From HTTP history or Proxy:

```text
Right-click request
    |
    v
Send to Repeater
```

The request can then be modified and resent.

Commonly modified values include:

```text
URL
Path
Method
Query parameters
POST parameters
JSON properties
Headers
Cookies
Tokens
Object IDs
Host
Content-Type
```

---

# Establishing a Baseline in Repeater

Before testing an input, send the original request unchanged.

Record:

```text
Status
Response length
Response body
Headers
Timing
Application state
```

Then modify a single input.

Example:

```text
Original:
user_id=100

Modified:
user_id=101
```

Compare the result.

---

# One Variable at a Time

Changing too many things at once makes interpretation difficult.

Bad:

```text
Change:
ID
Role
Method
Cookie
Header
```

Then observe a different response.

You may not know what caused the difference.

Better:

```text
Baseline
   |
   v
Change ID only
   |
   v
Observe
   |
   v
Change role only
   |
   v
Observe
```

---

# Authorisation Testing

Repeater is especially useful for authorisation testing.

Example model:

```text
User A
  |
  v
GET /api/account/100
```

Capture the request.

Then use another authorised test account:

```text
User B
  |
  v
GET /api/account/100
```

Compare behaviour.

Questions include:

- Can another user's object be accessed?
- Does changing the object identifier matter?
- Is the server checking ownership?
- Is access enforced server-side?

Related notes:

[Authorisation Testing](../../web/authorisation.md)

[IDOR and BOLA](../../web/idor-bola.md)

---

# Authentication Testing

Burp helps inspect:

- login requests;
- session creation;
- authentication cookies;
- tokens;
- logout behaviour;
- password reset;
- MFA flows;
- remember-me functionality.

Related notes:

[Authentication Testing](../../web/authentication.md)

[Password Reset Security](../../web/password-reset.md)

[Multi-Factor Authentication Security](../../web/mfa.md)

---

# Session Testing

Burp makes session behaviour visible.

Review:

```text
Set-Cookie
Cookie
Authorization
JWT
CSRF tokens
Refresh tokens
Session identifiers
```

Questions include:

- Does the token rotate after login?
- Does logout invalidate the session?
- Does privilege change rotate session state?
- Are sessions scoped correctly?
- Are cookies protected appropriately?

Related note:

[Session Management](../../web/session-management.md)

---

# Cookies

Cookies can be inspected in both requests and responses.

Example response:

```http
Set-Cookie: session=abc123; Secure; HttpOnly; SameSite=Lax
```

Useful properties include:

```text
Secure
HttpOnly
SameSite
Domain
Path
Expires
Max-Age
```

Cookie configuration must be interpreted according to application context.

---

# JSON Requests

Many modern applications send JSON.

Example:

```http
POST /api/profile HTTP/1.1
Host: example.test
Content-Type: application/json

{
  "name": "Alice",
  "email": "alice@example.test"
}
```

Repeater allows individual JSON properties to be changed and tested.

This is useful for:

- APIs;
- mass assignment;
- authorisation;
- business logic;
- injection testing.

Related notes:

[API Security](../../web/api-security.md)

[Mass Assignment](../../web/mass-assignment.md)

---

# HTTP Methods

Burp makes it easy to experiment with HTTP methods when relevant.

Examples include:

```text
GET
POST
PUT
PATCH
DELETE
OPTIONS
HEAD
```

Changing a method may reveal:

- alternate endpoint behaviour;
- API functionality;
- authorisation differences;
- method restrictions.

Do not assume changing a method alone creates a vulnerability.

---

# Headers

Security-relevant headers may include:

```text
Host
Origin
Referer
Authorization
Cookie
X-Forwarded-For
X-Forwarded-Host
Content-Type
Accept
```

Burp Repeater is useful because these values can be modified precisely.

Related notes:

[HTTP Host Header Attacks](../../web/host-header-attacks.md)

[CORS](../../web/cors.md)

[HTTP Security Headers](../../web/http-security-headers.md)

---

# Content-Type Testing

Applications sometimes parse input differently depending on `Content-Type`.

Examples:

```text
application/json
application/x-www-form-urlencoded
multipart/form-data
application/xml
```

A request may behave differently when the content type changes.

The test should be based on a specific hypothesis rather than random format changes.

---

# Comparer

Comparer highlights differences between two pieces of data.

This can be useful for:

- role comparison;
- authenticated vs unauthenticated responses;
- injection response differences;
- session comparison;
- cache behaviour;
- access-control testing.

Conceptually:

```text
Response A
    |
    v
Comparer
    ^
    |
Response B
```

---

# Word Comparison

Comparer can compare content by words.

This is useful where responses contain the same general structure with subtle textual differences.

---

# Byte Comparison

Byte-level comparison can identify very small differences.

This is useful when:

- token values change;
- binary data differs;
- whitespace or encoding differences matter.

---

# Decoder

Decoder can transform data between common formats.

Useful operations include:

- URL encoding;
- URL decoding;
- HTML encoding;
- HTML decoding;
- Base64 encoding;
- Base64 decoding;
- hexadecimal conversions.

Example:

```text
admin%40example.test
```

decode to:

```text
admin@example.test
```

Encoding does not imply encryption.

---

# Sequencer

Sequencer helps analyse the randomness of tokens.

Potential candidates include:

- session identifiers;
- CSRF tokens;
- password-reset tokens;
- anti-automation values.

A token that looks random should not automatically be assumed secure.

Sequencer can assist statistical analysis, but the security conclusion should also consider:

- token length;
- entropy;
- predictability;
- generation method;
- lifecycle;
- binding.

---

# Intruder

Intruder automates repeated requests with varying payload positions.

Conceptually:

```text
Request Template
      |
      v
Payload Positions
      |
      v
Payload List
      |
      v
Repeated Requests
      |
      v
Compare Responses
```

Use Intruder where repeated controlled testing is justified.

---

# Intruder Attack Types

Burp Intruder supports different payload-placement strategies.

The exact available options and terminology should be checked in current PortSwigger documentation.

Typical concepts include:

- one payload position at a time;
- multiple positions with coordinated payloads;
- combinations across positions.

The right mode depends on the test objective.

---

# Intruder for Enumeration

Intruder can assist with controlled enumeration of:

- IDs;
- parameters;
- values;
- endpoints;
- roles.

For large content-discovery tasks, dedicated tools such as ffuf may be faster.

Use the tool best suited to the problem.

---

# Intruder and Authentication

Be careful when using Intruder against authentication workflows.

Potential consequences include:

- account lockout;
- MFA triggering;
- rate limiting;
- security alerts;
- password-reset email generation.

Do not perform password attacks unless explicitly authorised.

---

# Intruder Grep and Response Analysis

Repeated requests are only useful when the results can be interpreted.

Compare:

```text
Status
Length
Words
Headers
Redirect
Response body
Timing
```

A small response difference can indicate meaningful application behaviour.

---

# Burp Scanner

Burp Scanner is available in Burp Suite Professional.

It can automate portions of:

- crawling;
- passive analysis;
- active security testing;
- issue identification.

Scanner results should be treated as:

```text
Candidates
```

until manually validated.

---

# Passive Scanning

Passive scanning analyses traffic without sending additional attack requests for that analysis.

It may identify issues such as:

- missing headers;
- information disclosure;
- insecure cookies;
- suspicious application behaviour.

Passive findings still require context.

---

# Active Scanning

Active scanning sends additional requests designed to test application behaviour.

This can be more intrusive.

Before active scanning, confirm:

```text
Scope
Authentication
Request rate
Application stability
State-changing risk
Testing window
```

---

# Scanner Validation Workflow

Do not do this:

```text
Burp Scanner
     |
     v
Issue
     |
     v
Report
```

Do this:

```text
Burp Scanner
     |
     v
Candidate
     |
     v
Read Issue Detail
     |
     v
Inspect Request/Response
     |
     v
Reproduce in Repeater
     |
     v
Validate Impact
     |
     v
Report
```

---

# Crawl and Audit

Burp Professional supports automated crawl and audit workflows.

Crawling helps discover:

- pages;
- routes;
- forms;
- APIs;
- application states.

Auditing tests discovered attack surface.

Automated crawling may miss:

- complex workflows;
- multi-role functionality;
- unusual JavaScript;
- stateful business logic.

Manual mapping remains valuable.

---

# Burp Collaborator

Burp Collaborator supports out-of-band interaction testing.

It can help identify behaviour where the application communicates externally rather than returning direct evidence.

Examples may include:

- blind SSRF;
- blind XXE;
- asynchronous interactions;
- backend callbacks.

Conceptually:

```text
Burp Request
    |
    v
Application
    |
    v
Outbound DNS / HTTP
    |
    v
Collaborator
```

Related notes:

[Server Side Request Forgery](../../web/ssrf.md)

[XML External Entity Injection](../../web/xxe.md)

---

# Collaborator Correlation

An out-of-band event is useful only when it can be correlated with the request that caused it.

Retain:

```text
Triggering request
Unique Collaborator address
Timestamp
Interaction protocol
Observed callback
```

This helps demonstrate causality.

---

# Interactsh as an Alternative

ProjectDiscovery Interactsh can provide similar out-of-band interaction functionality in appropriate workflows.

Related tool note:

[Interactsh](interactsh.md)

---

# Extensions

Burp extensions expand functionality.

Extensions can be installed from:

[Burp Suite BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }

Use extensions selectively.

Too many extensions can:

- slow Burp;
- generate noise;
- modify traffic;
- create duplicated findings;
- complicate troubleshooting.

---

# Autorize

Autorize is commonly used to help test authorisation differences between sessions.

Conceptually:

```text
Privileged Request
       |
       v
Replay with Lower-Privilege Context
       |
       v
Compare Response
```

This can accelerate horizontal and vertical authorisation testing.

Manual validation remains essential.

Related notes:

[Authorisation Testing](../../web/authorisation.md)

[IDOR and BOLA](../../web/idor-bola.md)

---

# Param Miner

Param Miner helps identify hidden or undocumented input parameters and headers.

It is particularly relevant to:

- hidden parameters;
- cache poisoning;
- header discovery;
- unkeyed input discovery.

Related note:

[Web Cache Poisoning](../../web/web-cache-poisoning.md)

Official extension:

[Param Miner - BApp Store](https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943){ target="_blank" rel="noopener noreferrer" }

---

# HTTP Request Smuggler

HTTP Request Smuggler assists with request-smuggling testing.

Use it only where this testing is explicitly permitted because malformed request behaviour can affect shared infrastructure.

Related note:

[HTTP Request Smuggling](../../web/http-request-smuggling.md)

Official extension:

[HTTP Request Smuggler - BApp Store](https://portswigger.net/bappstore/aaaa60ef945341e8a450217a54a11646){ target="_blank" rel="noopener noreferrer" }

---

# JWT Editor

JWT Editor assists with inspecting and testing JSON Web Tokens.

It can help with:

- decoding;
- modifying claims;
- key handling;
- signature-related testing.

Related note:

[JSON Web Token Security](../../web/jwt.md)

Official extension:

[JWT Editor - BApp Store](https://portswigger.net/bappstore/26aaa5a68d7a4c59bfa3e12e9d50f72a){ target="_blank" rel="noopener noreferrer" }

---

# Logger++

Logger++ provides enhanced request and response logging.

It can be useful during larger assessments where detailed traffic searching and filtering are important.

Official extension:

[Logger++ - BApp Store](https://portswigger.net/bappstore/470b7057b86f41c995fef2a4e1dab292){ target="_blank" rel="noopener noreferrer" }

---

# GraphQL Extensions

Burp extensions can assist with GraphQL mapping and testing.

Use them alongside:

- schema understanding;
- manual query review;
- authorisation testing;
- API methodology.

Related note:

[GraphQL API Security](../../web/graphql.md)

---

# WebSockets

Burp can intercept and manipulate WebSocket messages.

A simplified model is:

```text
Browser
   |
   v
WebSocket
   |
   v
Burp
   |
   v
Application
```

Relevant testing areas include:

- authentication;
- message authorisation;
- input validation;
- state management;
- cross-site WebSocket hijacking.

Related note:

[WebSocket Security](../../web/websockets.md)

---

# API Testing

Burp is highly useful for API security testing.

Typical requests may contain:

```text
JSON
XML
GraphQL
Form data
JWT
API keys
Bearer tokens
```

Burp helps inspect:

- method;
- route;
- parameters;
- authentication;
- object identifiers;
- headers;
- response differences.

Related note:

[API Security](../../web/api-security.md)

---

# REST APIs

For REST-style APIs, map:

```text
GET    /api/users/100
POST   /api/users
PATCH  /api/users/100
DELETE /api/users/100
```

Test:

- object access;
- role restrictions;
- field validation;
- method enforcement;
- mass assignment.

---

# GraphQL

A GraphQL request may resemble:

```http
POST /graphql HTTP/1.1
Host: example.test
Content-Type: application/json
```

with a query in the request body.

Burp can help modify:

- queries;
- variables;
- operation names;
- headers;
- authentication.

Related note:

[GraphQL API Security](../../web/graphql.md)

---

# File Upload Testing

Burp is very useful for file upload testing because multipart requests can be manipulated manually.

Review:

```text
Filename
Content-Type
Multipart field name
File content
Other parameters
Response
Storage location
```

Related note:

[File Upload Security](../../web/file-upload.md)

---

# CORS Testing

Burp can test Cross-Origin Resource Sharing by modifying:

```http
Origin: https://example-attacker.test
```

Then inspect:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
```

Interpret the result in the context of credentials and sensitive data.

Related note:

[CORS](../../web/cors.md)

---

# CSRF Testing

Burp can help analyse CSRF protections.

Review:

- anti-CSRF tokens;
- SameSite cookies;
- Origin validation;
- Referer validation;
- state-changing methods.

Related note:

[Cross-Site Request Forgery](../../web/csrf.md)

---

# Host Header Testing

Repeater is ideal for Host-header manipulation.

Relevant headers may include:

```text
Host
X-Forwarded-Host
Forwarded
X-Host
```

Related note:

[HTTP Host Header Attacks](../../web/host-header-attacks.md)

---

# Open Redirect Testing

Repeater can help change redirect-related parameters.

Example:

```text
?next=/dashboard
```

may be changed during a controlled test.

Related note:

[Open Redirect](../../web/open-redirect.md)

---

# Path Traversal Testing

Burp can be used to modify path parameters and compare responses.

The important question is whether user-controlled path input reaches filesystem access without appropriate restriction.

Related note:

[Path Traversal](../../web/path-traversal.md)

---

# File Inclusion

Burp can help identify and manipulate parameters associated with server-side file loading.

Related note:

[File Inclusion](../../web/file-inclusion.md)

---

# SQL Injection

Repeater provides a controlled way to investigate potential SQL injection.

Workflow:

```text
Original Request
      |
      v
Baseline
      |
      v
Focused Input Change
      |
      v
Response Difference
      |
      v
Additional Validation
```

Automation such as sqlmap may follow once a candidate is understood.

Related note:

[SQL Injection](../../web/sql-injection.md)

Related tool:

[sqlmap](sqlmap.md)

---

# NoSQL Injection

Burp is also useful for testing JSON and structured inputs that may reach NoSQL queries.

Related note:

[NoSQL Injection](../../web/nosql-injection.md)

---

# Command Injection

Burp Repeater can help manipulate parameters suspected of reaching operating-system commands.

Testing should begin with low-impact indicators and remain within engagement restrictions.

Related note:

[OS Command Injection](../../web/command-injection.md)

---

# SSTI

Server-Side Template Injection often requires careful response analysis.

Burp Repeater is useful for controlled input changes.

Related note:

[Server-Side Template Injection](../../web/ssti.md)

---

# XSS

Burp can help identify reflection and encoding behaviour.

The browser remains essential for confirming client-side execution and context.

Related note:

[Cross-Site Scripting](../../web/xss.md)

---

# DOM-Based Testing

For DOM vulnerabilities, combine Burp with:

- browser developer tools;
- JavaScript source review;
- source/sink analysis.

Related note:

[DOM-Based Vulnerabilities](../../web/dom-based-vulnerabilities.md)

---

# XXE

Burp can manipulate XML requests and inspect direct or out-of-band parser behaviour.

Related note:

[XML External Entity Injection](../../web/xxe.md)

---

# SSRF

Burp is useful for manipulating URLs, hostnames, redirect parameters, and backend-fetch inputs.

Out-of-band infrastructure such as Collaborator or Interactsh may help where direct responses are unavailable.

Related note:

[Server Side Request Forgery](../../web/ssrf.md)

---

# Deserialisation

Burp can capture and modify application data formats that may be deserialised server-side.

The test depends heavily on the technology and format involved.

Related note:

[Insecure Deserialization](../../web/deserialization.md)

---

# Request Smuggling

Request smuggling testing involves differences in how HTTP intermediaries parse message boundaries.

Use dedicated tooling and careful methodology.

Related note:

[HTTP Request Smuggling](../../web/http-request-smuggling.md)

---

# Cache Poisoning

Burp can help identify whether unkeyed request components influence cached responses.

Param Miner can help identify candidate inputs.

Related note:

[Web Cache Poisoning](../../web/web-cache-poisoning.md)

---

# Cache Deception

Burp helps compare caching behaviour between paths, extensions, and authenticated resources.

Related note:

[Web Cache Deception](../../web/web-cache-deception.md)

---

# Business Logic

Burp is extremely useful for business-logic testing because Repeater gives full control over application workflow requests.

Examples include:

- quantity manipulation;
- approval bypass;
- order sequencing;
- role transitions;
- state changes.

Related note:

[Business Logic Vulnerabilities](../../web/business-logic.md)

---

# Race Conditions

Burp Professional includes functionality that can assist with sending requests in parallel.

Race-condition testing requires understanding:

```text
Expected invariant
State transition
Concurrency window
Resulting impact
```

Related note:

[Race Conditions](../../web/race-conditions.md)

---

# Password Reset

Capture the full password-reset process.

Map:

```text
Request reset
      |
      v
Token issued
      |
      v
Token consumed
      |
      v
Password changed
```

Review:

- token lifetime;
- token reuse;
- account binding;
- host-dependent links;
- session invalidation.

Related note:

[Password Reset Security](../../web/password-reset.md)

---

# OAuth and OIDC

Burp can help map:

```text
Authorization request
Redirect URI
State
Nonce
Authorization code
Token exchange
UserInfo
```

Related note:

[OAuth 2.0 and OpenID Connect Security](../../web/oauth-oidc.md)

---

# SAML

Burp can inspect SAML-related browser flows.

Depending on the workflow, encoded SAML messages may need to be decoded for analysis.

Related note:

[SAML Security](../../web/saml.md)

---

# HTTP Security Headers

Burp passive analysis and manual response inspection can identify security headers.

Examples include:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
```

Related note:

[HTTP Security Headers](../../web/http-security-headers.md)

---

# Information Disclosure

HTTP history often reveals information that is easy to overlook in a browser.

Examples include:

- internal headers;
- stack traces;
- debug data;
- internal paths;
- version strings;
- secrets in API responses.

Related note:

[Information Disclosure](../../web/information-disclosure.md)

---

# Secrets Exposure

Burp can help identify exposed credentials or tokens in HTTP traffic.

Handle such data carefully.

Avoid copying sensitive secrets into:

- screenshots;
- issue descriptions;
- shared notes;
- public reports.

Related note:

[Secrets Exposure](../../web/secrets-exposure.md)

---

# Burp Search

Burp's search functionality is valuable on larger applications.

Useful terms may include:

```text
token
admin
password
secret
api
internal
debug
upload
role
```

Search both requests and responses where appropriate.

---

# Highlighting and Comments

Burp allows requests to be highlighted and commented.

This is useful during long assessments.

Example scheme:

```text
Yellow -> needs review
Red    -> confirmed issue
Green  -> tested / no issue
```

Use any consistent system that works for the assessment.

---

# Organising Repeater Tabs

Large assessments can create many Repeater tabs.

Use meaningful tab names such as:

```text
Login
IDOR - Profile
Admin API
Password Reset
Upload
GraphQL
CORS
```

This makes workflows easier to resume and review.

---

# Request Naming

Good request organisation improves evidence quality.

Instead of:

```text
Repeater 19
Repeater 20
Repeater 21
```

prefer:

```text
IDOR - Baseline
IDOR - User B
IDOR - Modified Object
```

---

# Match and Replace

Burp supports Match and Replace rules for modifying traffic automatically.

Possible legitimate uses include:

- adding a testing header;
- modifying a User-Agent;
- replacing a hostname;
- adding custom environment markers.

Use these carefully because they affect many requests automatically.

---

# Proxy Rules

Proxy rules can control which traffic is intercepted or modified.

This can help reduce noise and avoid accidental third-party interaction.

---

# Upstream Proxies

Burp can be configured to send traffic through an upstream proxy when required by the environment.

This may be relevant for:

- corporate proxy networks;
- assessment jump hosts;
- controlled network paths.

Document proxy configuration if it affects reproducibility.

---

# SOCKS Proxy

Burp can also be used with SOCKS proxying in applicable environments.

This can be useful when web applications are accessible through a controlled pivot or test network.

Ensure the network path itself is authorised.

---

# TLS Troubleshooting

If HTTPS traffic fails through Burp, check:

```text
Browser trusts Burp CA?
Correct proxy listener?
Correct hostname?
TLS interception permitted?
Client certificate required?
Certificate pinning involved?
```

For normal web applications, the embedded Burp browser often avoids most setup problems.

---

# Client Certificates

Some applications require mutual TLS.

Burp supports client certificate configuration.

Where mTLS is in scope, ensure:

- certificate is authorised;
- private key is handled securely;
- test identity is documented.

---

# Certificate Pinning

Mobile or thick-client applications may use certificate pinning.

This is a different testing problem from normal browser-based web applications.

Do not weaken production client security outside an authorised test environment.

---

# Logging Sensitive Data

Burp may capture:

- passwords;
- session tokens;
- API keys;
- personal information;
- application secrets.

Assessment workspaces should therefore be protected appropriately.

Avoid unnecessary retention.

---

# Project Files

Burp Professional can use project files to retain assessment state.

Depending on workflow, retained state may include:

- HTTP history;
- site map;
- Scanner data;
- configuration.

Project files may contain sensitive information and should be protected accordingly.

---

# Temporary vs Project-Based Work

For quick labs:

```text
Temporary project
```

may be sufficient.

For longer engagements:

```text
Saved project
```

can help preserve testing state.

Consider organisational retention requirements.

---

# Configuration Files

Burp configuration can be exported and reused.

This can help standardise:

- proxy settings;
- extension configuration;
- scope behaviour;
- Scanner configuration.

Do not distribute configurations containing secrets.

---

# Burp and curl

curl is useful for reproducing simple HTTP behaviour outside Burp.

Example:

```text
Burp
  |
  v
Identify interesting request
  |
  v
curl
  |
  v
Independent reproduction
```

Quick reference:

[curl Cheatsheet](../../cheatsheets/curl.md)

---

# Burp and ffuf

Burp and ffuf serve different purposes.

```text
ffuf
  |
  v
Discover content
  |
  v
Burp
  |
  v
Understand and test discovered content
```

Related note:

[ffuf](ffuf.md)

---

# Burp and Katana

Katana can discover application URLs.

Burp can then provide deeper manual inspection.

```text
Katana
   |
   v
URL Inventory
   |
   v
Burp
   |
   v
Manual Testing
```

Related note:

[Katana](katana.md)

---

# Burp and Nuclei

Nuclei can identify candidate issues at scale.

Burp is useful for validating important matches.

```text
Nuclei
   |
   v
Candidate
   |
   v
Burp Repeater
   |
   v
Manual Validation
```

Related note:

[Nuclei](nuclei.md)

---

# Burp and sqlmap

Burp can capture complex authenticated requests.

sqlmap can consume request data for focused SQL injection validation.

Conceptually:

```text
Burp
  |
  v
Captured Request
  |
  v
sqlmap
  |
  v
Automated SQLi Testing
```

Related note:

[sqlmap](sqlmap.md)

---

# Burp and Interactsh

Where Burp Community or an external OOB workflow is preferred:

```text
Burp Request
    |
    v
Interactsh Identifier
    |
    v
Application Callback
```

Related note:

[Interactsh](interactsh.md)

---

# Burp and Browser Developer Tools

Burp shows HTTP traffic.

Developer tools show client-side execution.

Together:

```text
Burp
  |
  +-- requests
  +-- responses
  +-- cookies

DevTools
  |
  +-- JavaScript
  +-- DOM
  +-- console
  +-- storage
```

This combination is particularly useful for modern JavaScript applications.

---

# Testing Workflow

A mature Burp workflow may look like:

```text
1. Confirm scope
       |
       v
2. Configure Burp project
       |
       v
3. Configure browser
       |
       v
4. Browse application normally
       |
       v
5. Build site map
       |
       v
6. Review HTTP history
       |
       v
7. Identify security-sensitive requests
       |
       v
8. Send candidates to Repeater
       |
       v
9. Establish baselines
       |
       v
10. Test one variable at a time
       |
       v
11. Use extensions/automation where appropriate
       |
       v
12. Validate findings manually
       |
       v
13. Capture reproducible evidence
```

---

# Representative Authorisation Scenario

Suppose a user requests:

```http
GET /api/orders/1001 HTTP/1.1
Host: example.test
Cookie: session=user-a-session
```

The response returns User A's order.

Send the request to Repeater.

Change:

```text
1001
```

to another authorised test object's identifier:

```text
1002
```

Observe:

```text
Status
Response body
Object owner
Sensitive fields
```

Then repeat using another authorised test account if needed.

The conclusion should be based on actual server-side authorisation behaviour.

---

# Representative CORS Scenario

Original request:

```http
GET /api/profile HTTP/1.1
Host: example.test
```

Test with:

```http
Origin: https://example-attacker.test
```

Inspect the response headers.

Questions include:

```text
Is the Origin reflected?

Are credentials permitted?

Is sensitive data returned?

Can a browser exploit the combination?
```

Do not report CORS merely because one permissive header exists.

---

# Representative Scanner Scenario

Burp Scanner reports a candidate issue.

Workflow:

```text
Scanner Issue
     |
     v
Open Request
     |
     v
Send to Repeater
     |
     v
Reproduce
     |
     v
Determine Preconditions
     |
     v
Determine Impact
     |
     v
Capture Evidence
```

If manual reproduction fails, investigate:

- authentication;
- application state;
- scanner assumption;
- intermittent behaviour;
- WAF;
- false positive.

---

# False Positives

Burp-generated findings can be false positives because of:

- generic error messages;
- reflection without execution;
- WAF responses;
- soft 404s;
- misleading headers;
- ambiguous timing;
- application state;
- Scanner heuristics.

Manual validation is required.

---

# False Negatives

Burp can also miss issues.

Possible causes include:

- hidden functionality;
- incomplete crawling;
- business logic;
- multiple user roles;
- complex state;
- WebSocket-only functionality;
- unusual protocols;
- client-side-only behaviour;
- authentication barriers.

A clean Scanner result does not prove the application is secure.

---

# Evidence Collection

Strong Burp evidence should usually include:

```text
Target
Test account / role
Request
Response
Timestamp
Modified value
Expected behaviour
Observed behaviour
Manual validation
Impact
```

For screenshots, include only what helps the reader understand the issue.

Raw requests and responses are generally more useful than screenshots alone.

---

# Exporting Requests

Requests can be copied in several useful formats.

One common workflow is copying a request as a curl command for external reproduction.

Always review copied commands before sharing them because they may contain:

- cookies;
- bearer tokens;
- API keys;
- passwords.

Redact secrets where necessary.

---

# Reporting

The finding should describe the vulnerability, not the Burp feature that discovered it.

Avoid:

```text
Burp Scanner found an IDOR.
```

Prefer:

```text
The application did not enforce server-side ownership checks when
accessing order objects. Changing the order identifier in an
authenticated request allowed one test account to retrieve an object
belonging to another authorised test account.
```

Burp is the testing mechanism.

The security condition is the finding.

---

# Burp Evidence Example

A useful evidence structure might be:

```text
Request A:
User A requests /api/orders/1001

Result:
200 OK
User A object returned

Request B:
User A requests /api/orders/1002

Result:
200 OK
User B object returned

Control:
User A should not have access to User B object

Conclusion:
Server-side object-level authorisation was not enforced.
```

This is much stronger than:

```text
Burp showed 200 OK.
```

---

# Troubleshooting

## No Browser Traffic Appears

Check:

```text
Proxy configured?
Correct listener?
Browser using Burp?
Scope filter hiding traffic?
```

Try the embedded Burp browser first.

---

## HTTPS Errors

Check:

```text
Burp CA trusted?
Hostname correct?
TLS interception permitted?
Client certificate required?
```

---

## Repeater Request Behaves Differently

Possible causes include:

- expired session;
- CSRF token;
- one-time token;
- changing state;
- missing browser-generated header;
- anti-automation controls.

Compare the Repeater request with the original browser request.

---

## Authentication Keeps Expiring

Review:

- session lifetime;
- refresh tokens;
- CSRF state;
- authentication cookies;
- token rotation.

For complicated workflows, Burp session-handling features may help.

---

## Scanner Produces Too Much Noise

Reduce scope.

Review:

- crawl configuration;
- audit configuration;
- insertion points;
- issue definitions.

Do not scan everything indiscriminately.

---

## Burp Becomes Slow

Possible causes include:

- very large HTTP history;
- too many extensions;
- large responses;
- Scanner activity;
- insufficient system resources.

Disable unnecessary extensions and restrict scope.

---

# Burp Suite Checklist

## Setup

- [ ] Correct Burp edition identified.
- [ ] Burp version recorded where relevant.
- [ ] Proxy listener configured.
- [ ] Dedicated browser configured.
- [ ] CA certificate configured where required.
- [ ] Assessment scope configured.
- [ ] Third-party traffic excluded where appropriate.

## Mapping

- [ ] Main application browsed.
- [ ] Authentication flow captured.
- [ ] Important roles reviewed.
- [ ] HTTP history reviewed.
- [ ] Site map reviewed.
- [ ] API traffic identified.
- [ ] WebSocket traffic identified where relevant.
- [ ] File uploads identified.
- [ ] Administrative functionality identified.

## Repeater

- [ ] Original request retained.
- [ ] Baseline response established.
- [ ] One variable changed at a time.
- [ ] Relevant response properties compared.
- [ ] Authentication context retained.
- [ ] Application state considered.

## Authentication

- [ ] Login analysed.
- [ ] Logout analysed.
- [ ] Session rotation considered.
- [ ] Password reset reviewed.
- [ ] MFA reviewed where relevant.
- [ ] Multiple roles used where authorised.

## Authorisation

- [ ] Horizontal access tested.
- [ ] Vertical access tested.
- [ ] Object identifiers reviewed.
- [ ] Function-level access reviewed.
- [ ] API endpoints reviewed.

## Extensions

- [ ] Only relevant extensions installed.
- [ ] Extension behaviour understood.
- [ ] Autorize used where appropriate.
- [ ] Param Miner used where appropriate.
- [ ] Request Smuggler used only where appropriate.
- [ ] JWT tooling used where appropriate.
- [ ] Extension output manually validated.

## Professional Edition

- [ ] Scanner scope reviewed.
- [ ] Crawl scope reviewed.
- [ ] Active scanning authorised.
- [ ] Scanner findings manually validated.
- [ ] Collaborator interactions correlated.
- [ ] Automated activity kept within rate constraints.

## Evidence

- [ ] Exact request retained.
- [ ] Exact response retained.
- [ ] Account/role identified.
- [ ] Modified value identified.
- [ ] Timestamp retained where useful.
- [ ] Impact explained.
- [ ] Secrets redacted from shared evidence.
- [ ] Finding describes vulnerability rather than tool output.

---

# Related Tool Notes

[Web Application Testing Tools](index.md)

[ffuf](ffuf.md)

[Nuclei](nuclei.md)

[sqlmap](sqlmap.md)

[Katana](katana.md)

[Interactsh](interactsh.md)

[Web Enumeration Tools](../web-enumeration/index.md)

[WhatWeb](../web-enumeration/whatweb.md)

[Wappalyzer](../web-enumeration/wappalyzer.md)

[httpx](../web-enumeration/httpx.md)

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

[Password Reset Security](../../web/password-reset.md)

[Multi-Factor Authentication Security](../../web/mfa.md)

[Cross-Site Request Forgery](../../web/csrf.md)

[CORS](../../web/cors.md)

[SQL Injection](../../web/sql-injection.md)

[NoSQL Injection](../../web/nosql-injection.md)

[OS Command Injection](../../web/command-injection.md)

[Cross-Site Scripting](../../web/xss.md)

[DOM-Based Vulnerabilities](../../web/dom-based-vulnerabilities.md)

[Server Side Request Forgery](../../web/ssrf.md)

[XML External Entity Injection](../../web/xxe.md)

[Server-Side Template Injection](../../web/ssti.md)

[Path Traversal](../../web/path-traversal.md)

[File Inclusion](../../web/file-inclusion.md)

[File Upload Security](../../web/file-upload.md)

[Insecure Deserialization](../../web/deserialization.md)

[HTTP Host Header Attacks](../../web/host-header-attacks.md)

[HTTP Request Smuggling](../../web/http-request-smuggling.md)

[Web Cache Poisoning](../../web/web-cache-poisoning.md)

[Web Cache Deception](../../web/web-cache-deception.md)

[GraphQL API Security](../../web/graphql.md)

[WebSocket Security](../../web/websockets.md)

[Business Logic Vulnerabilities](../../web/business-logic.md)

[Race Conditions](../../web/race-conditions.md)

---

# External References

## Official Burp Documentation

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

[Burp Suite](https://portswigger.net/burp){ target="_blank" rel="noopener noreferrer" }

[Burp Proxy](https://portswigger.net/burp/documentation/desktop/tools/proxy){ target="_blank" rel="noopener noreferrer" }

[Burp Repeater](https://portswigger.net/burp/documentation/desktop/tools/repeater){ target="_blank" rel="noopener noreferrer" }

[Burp Intruder](https://portswigger.net/burp/documentation/desktop/tools/intruder){ target="_blank" rel="noopener noreferrer" }

[Burp Scanner](https://portswigger.net/burp/documentation/scanner){ target="_blank" rel="noopener noreferrer" }

[Burp Collaborator](https://portswigger.net/burp/documentation/collaborator){ target="_blank" rel="noopener noreferrer" }

[Burp Suite BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger Web Security Academy

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

The Web Security Academy is especially useful because its labs connect Burp functionality directly to security techniques.

---

## Additional Practical References

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

[0xdf](https://0xdf.gitlab.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use Burp like this:

```text
Open Burp
   |
   v
Run Scanner
   |
   v
Copy Findings
```

Use Burp like this:

```text
Understand Application
        |
        v
Capture Real Traffic
        |
        v
Map Attack Surface
        |
        v
Identify Security Question
        |
        v
Send Request to Repeater
        |
        v
Establish Baseline
        |
        v
Change One Variable
        |
        v
Observe Behaviour
        |
        v
Use Automation Where Helpful
        |
        +-- Intruder
        +-- Scanner
        +-- Extensions
        +-- Collaborator
        |
        v
Validate Manually
        |
        v
Demonstrate Impact
        |
        v
Capture Evidence
        |
        v
Report the Security Condition
```

Burp Suite is most valuable when it helps the tester understand exactly how the application behaves.

The platform provides the visibility and control.

The tester provides the methodology, interpretation, and security conclusion.
