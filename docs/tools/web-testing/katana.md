---
title: Katana
description: Practical Katana reference for authorised web crawling, endpoint discovery, JavaScript-aware reconnaissance, scope control, filtering, output handling, evidence collection, and integration with wider web application testing methodology.
---

# Katana

Katana is a web crawler from ProjectDiscovery designed for fast attack-surface discovery across web applications.

It is especially useful for identifying:

- reachable URLs;
- linked endpoints;
- parameters;
- JavaScript-referenced paths;
- API routes;
- forms;
- application resources;
- client-side navigation;
- deeper application structure.

Katana is most valuable when used after initial host discovery and before deeper manual testing.

```text
Alive Web Host
    |
    v
Katana Crawl
    |
    +-- Links
    +-- JavaScript
    +-- Parameters
    +-- Forms
    +-- Resources
    |
    v
Endpoint Inventory
    |
    v
Manual Validation
    |
    v
Burp / Focused Testing
```

!!! warning "Authorised testing only"
    Use Katana only against web applications and infrastructure that are explicitly authorised for testing. Crawling can generate significant request volume and may traverse state-changing or sensitive application functionality. Start conservatively, define scope carefully, and review discovered destinations before expanding the crawl.

---

# Where Katana Fits

A common workflow is:

```text
Subdomain Enumeration
      |
      v
httpx
      |
      v
Alive Web Hosts
      |
      v
Katana
      |
      v
Discovered URLs
      |
      v
Filtering / Deduplication
      |
      v
Manual Testing
```

Related tools:

[Web Enumeration Tools](../web-enumeration/index.md)

[httpx](../web-enumeration/httpx.md)

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

---

# Official Project

Official project:

[Katana - GitHub](https://github.com/projectdiscovery/katana){ target="_blank" rel="noopener noreferrer" }

Official documentation:

[Katana Documentation](https://docs.projectdiscovery.io/opensource/katana/overview){ target="_blank" rel="noopener noreferrer" }

Because Katana evolves quickly, verify exact current flags using:

```bash
katana -h
```

---

# Verify Installation

Check:

```bash
katana -version
```

If the installed build uses different version syntax, use:

```bash
katana -h
```

The help output is the most reliable source for the current installed version.

---

# Basic Crawl

A simple starting point is:

```bash
katana -u https://example.test
```

This crawls the target and outputs discovered URLs.

Conceptually:

```text
https://example.test
      |
      +-- /login
      +-- /account
      +-- /api/users
      +-- /assets/app.js
      +-- /admin
```

The discovered URLs become candidates for later testing.

---

# Crawl from a List

Katana can also process multiple targets.

A common pattern is:

```bash
katana -list urls.txt
```

or the equivalent supported by the installed version.

Always confirm exact syntax with:

```bash
katana -h
```

---

# Pipeline with httpx

A useful reconnaissance pipeline is:

```bash
cat subdomains.txt | httpx -silent | katana
```

Conceptually:

```text
Subdomains
   |
   v
httpx
   |
   v
Alive URLs
   |
   v
Katana
   |
   v
Endpoint Inventory
```

For production assessments, consider saving each stage separately for reproducibility.

---

# Prefer Reproducible Pipelines

Instead of:

```bash
subfinder -d example.test | httpx -silent | katana
```

for all cases, consider:

```text
subdomains.txt
alive.txt
katana.txt
```

This allows each stage to be reviewed independently.

---

# Save Alive Hosts First

Example:

```bash
httpx -l subdomains.txt -silent > alive.txt
```

Then:

```bash
katana -list alive.txt > katana.txt
```

Use the exact current input option supported by the installed version.

This provides a clear evidence chain.

---

# Crawling vs Fuzzing

Katana and ffuf perform different jobs.

```text
Katana
  |
  +-- follows discovered links

ffuf
  |
  +-- guesses candidate paths
```

Katana discovers:

```text
linked attack surface
```

ffuf discovers:

```text
potentially unlinked attack surface
```

Related tool:

[ffuf](ffuf.md)

---

# Why Use Both

Suppose the application exposes:

```text
/
/login
/api/profile
```

through navigation.

Katana may discover all three.

But:

```text
/admin-old
```

may not be linked anywhere.

ffuf may discover it.

A combined workflow improves coverage.

---

# Crawl Depth

Crawl depth controls how far Katana follows discovered relationships.

Conceptually:

```text
Depth 0:
/

Depth 1:
 /login
 /products

Depth 2:
 /products/123
 /account/settings
```

Deeper crawling can improve coverage but also increases traffic.

Use the smallest depth that supports the objective.

---

# Depth Selection

Start with a moderate depth.

Increase only when:

- the application is heavily nested;
- important sections are missed;
- the target can tolerate additional requests;
- the engagement allows it.

Do not use deep crawling automatically against fragile production applications.

---

# Scope Control

Scope control is critical.

A crawler may encounter:

```text
example.test
      |
      +-- api.example.test
      +-- auth.thirdparty.com
      +-- payments.example-payments.com
```

Do not automatically crawl all discovered domains.

Reachability does not equal authorisation.

---

# In-Scope vs Out-of-Scope Destinations

A useful mental model is:

```text
Discovered URL
      |
      v
Scope Check
      |
      +-- In Scope -> crawl
      |
      +-- Out of Scope -> record only / ignore
```

Scope should be explicit.

---

# Third-Party Services

Modern applications often link to:

- identity providers;
- CDNs;
- payment providers;
- analytics;
- support platforms;
- SaaS services.

These should normally be excluded unless explicitly authorised.

---

# Scope Regex / Filters

Katana supports scope and filtering functionality.

Because exact flags may evolve, inspect:

```bash
katana -h
```

for the current options.

Use allowlists rather than relying only on broad exclusions where practical.

---

# Host Scope

If testing:

```text
example.test
```

and scope explicitly includes:

```text
*.example.test
```

then crawling multiple subdomains may be appropriate.

If scope contains only:

```text
www.example.test
```

do not assume:

```text
admin.example.test
```

is authorised.

---

# Redirect Scope

A crawler may follow:

```text
https://example.test/login
```

to:

```text
https://login.identity-provider.com/
```

The second host may be out of scope.

Review redirect behaviour carefully.

---

# Query Parameters

Katana may discover URLs containing parameters.

Example:

```text
https://example.test/search?q=test
```

Parameters can help identify:

- search features;
- object identifiers;
- filters;
- redirects;
- API inputs.

Do not treat every parameter as security sensitive.

---

# Parameter Inventory

A useful endpoint record might look like:

| URL | Parameters | Source |
|---|---|---|
| `/search` | `q` | HTML form |
| `/user` | `id` | JavaScript |
| `/redirect` | `url` | anchor |
| `/api/report` | `format` | JS request |

This provides a useful starting point for manual review.

---

# Parameter Names Matter

Interesting parameter names may include:

```text
id
user
account
file
path
url
redirect
callback
template
query
search
format
lang
```

Names are only hints.

The security relevance depends on server-side behaviour.

---

# JavaScript Discovery

JavaScript is a major source of hidden attack surface.

Scripts may reveal:

- API routes;
- feature flags;
- internal endpoints;
- parameter names;
- versioned routes;
- WebSocket URLs;
- GraphQL endpoints.

Katana can help surface these references.

---

# JavaScript Example

A script may contain:

```javascript
fetch("/api/v2/users/" + userId)
```

This may reveal:

```text
/api/v2/users/
```

even when no visible link exists.

The endpoint still requires manual validation.

---

# JavaScript-Aware Crawling

ProjectDiscovery has added JavaScript-aware crawling capabilities over time.

Use:

```bash
katana -h
```

to verify the exact options supported by the installed version.

Do not rely on old examples for current headless/JavaScript flags.

---

# Static JavaScript vs Runtime Navigation

There is an important distinction between:

```text
Static JS endpoint extraction
```

and:

```text
Executing JavaScript in a browser context
```

Some application routes only become visible after runtime execution.

---

# Headless Crawling

Katana can support headless-style crawling in supported configurations.

This can be useful for:

- single-page applications;
- JavaScript routing;
- runtime DOM generation;
- client-side navigation.

Headless crawling is generally heavier than normal HTTP crawling.

Use it selectively.

---

# When Headless Crawling Helps

Consider headless crawling when:

```text
Normal crawl finds almost nothing
```

but the browser shows:

```text
large client-side application
```

Examples include:

- React;
- Angular;
- Vue;
- complex SPA frameworks.

---

# Headless Crawling Risks

A real browser context may:

- execute JavaScript;
- submit background requests;
- interact with application logic;
- load third-party services.

Scope and operational impact should therefore be reviewed carefully.

---

# Forms

Forms can reveal:

- endpoints;
- methods;
- parameter names;
- workflows.

Example:

```html
<form action="/login" method="POST">
```

This exposes:

```text
POST /login
```

and potentially fields such as:

```text
username
password
```

---

# Form Discovery Is Not Form Submission

There is a major distinction between:

```text
Identify form
```

and:

```text
Submit form
```

A crawler should not blindly execute state-changing application actions.

---

# State-Changing Routes

Potentially dangerous operations include:

```text
/delete
/logout
/reset
/purchase
/submit
/approve
/upload
```

Path names alone do not prove they change state, but they deserve caution.

---

# Safe Crawling Principle

Prefer:

```text
GET-oriented discovery
```

before:

```text
state-changing interaction
```

especially on production systems.

---

# HTTP Methods

Katana may identify methods through forms or application references.

Examples include:

```text
GET
POST
PUT
DELETE
PATCH
```

Do not automatically replay state-changing methods.

---

# Authentication

Authenticated applications require session context for complete crawling.

Potential approaches include supplying:

- cookies;
- authorization headers;
- other approved headers.

The exact Katana options should be checked using:

```bash
katana -h
```

---

# Cookie-Based Crawling

Conceptually:

```text
Katana
  |
  +-- Cookie: approved test session
  |
  v
Authenticated Application
```

This can reveal:

- account pages;
- private APIs;
- role-specific routes.

Protect live session values.

---

# Bearer Tokens

For APIs:

```text
Authorization: Bearer <REDACTED>
```

may be required.

Use only test-account tokens and avoid committing them to shell history or repositories.

---

# Role-Aware Crawling

The same application may expose different routes to different roles.

Example:

```text
User
  |
  +-- /profile
  +-- /orders

Admin
  |
  +-- /profile
  +-- /orders
  +-- /admin
  +-- /audit
```

Run role-specific crawls only where needed and authorised.

---

# Session Expiry

Long crawls may outlive the session.

Symptoms include:

```text
302 -> /login
401
403
```

appearing suddenly across many routes.

Check authentication before interpreting later results.

---

# CSRF and Stateful Workflows

Applications with dynamic CSRF tokens or multi-step workflows may not crawl cleanly.

Examples include:

```text
Step 1 -> get token
Step 2 -> submit form
Step 3 -> receive next token
```

Manual Burp testing or custom automation may be more appropriate.

---

# API Discovery

Katana is useful for finding API endpoints referenced by:

- JavaScript;
- HTML;
- documentation;
- linked resources.

Example:

```text
/api/v1/profile
/api/v1/orders
/api/v2/admin
```

Each endpoint should be classified by:

- authentication;
- method;
- parameters;
- content type.

---

# API Versions

Versioned routes may include:

```text
/api/v1/
/api/v2/
/api/internal/
```

Older versions deserve attention because they may have weaker controls.

Do not assume an older version is vulnerable solely because it exists.

---

# OpenAPI

Katana may discover:

```text
/openapi.json
/swagger.json
/api-docs
```

These can reveal significant API structure.

Treat documentation exposure according to intended design.

---

# GraphQL Discovery

Katana may identify:

```text
/graphql
/api/graphql
```

through JavaScript or application links.

Related note:

[GraphQL](../../web/graphql.md)

---

# WebSockets

JavaScript may reveal:

```text
ws://
wss://
```

endpoints.

These represent a different protocol surface.

Manual testing may require Burp or another WebSocket-capable client.

---

# Static Assets

Katana may enumerate:

- CSS;
- JavaScript;
- images;
- fonts;
- source maps.

Not every static file needs deeper review.

Prioritise files that can reveal:

- application logic;
- routes;
- configuration;
- secrets;
- debugging data.

---

# Source Maps

Source map files may expose original client-side source.

Common pattern:

```text
app.js.map
```

If accessible, determine whether they reveal sensitive source or internal information.

Source maps are not automatically vulnerabilities.

---

# JavaScript Secrets

Client-side JavaScript may contain:

- API keys;
- environment values;
- internal URLs.

Many API keys embedded in frontend code are intentionally public identifiers.

Do not report every key-looking string as a secret.

Determine its actual privilege and intended exposure.

---

# Endpoint Sources

When possible, retain where each endpoint came from.

Example:

```text
Endpoint:
/api/export

Source:
app.js

Reference:
fetch("/api/export")
```

This improves reproducibility.

---

# Filtering

Large crawls often produce significant noise.

Common low-value resources include:

```text
images
fonts
CSS
static media
tracking URLs
logout routes
third-party assets
```

Filtering can make results easier to review.

---

# Extension Filtering

Katana supports filtering functionality for extensions and other patterns.

Use:

```bash
katana -h
```

for exact current syntax.

Potential low-priority extensions include:

```text
.png
.jpg
.gif
.svg
.woff
.woff2
.ico
```

Do not exclude JavaScript if endpoint discovery is important.

---

# Avoid Over-Filtering

Filtering:

```text
.json
```

could hide:

```text
/openapi.json
```

Filtering:

```text
.js
```

could hide valuable JavaScript.

Choose filters according to the goal.

---

# Deduplication

Crawlers may discover equivalent URLs repeatedly.

Examples:

```text
/page?id=1
/page?id=2
/page?id=3
```

Depending on the objective, these may represent:

```text
same endpoint, different values
```

rather than three independent attack-surface items.

---

# Normalisation

Useful URL normalisation may include:

- lowercasing hostnames;
- removing fragments;
- sorting parameters where appropriate;
- removing duplicates;
- separating path from value variants.

Do not alter URLs in a way that changes application semantics.

---

# Fragments

Browser fragments such as:

```text
/page#section
```

are not normally sent to the server.

For server-side endpoint inventory, fragments can often be ignored.

Client-side SPA routing may still use them.

---

# Duplicate Query Values

These:

```text
/item?id=1
/item?id=2
```

may map to the same route.

For attack-surface inventory, record:

```text
/item?id=
```

while preserving example values separately.

---

# Crawling Loops

Applications may create infinite navigation patterns.

Examples:

```text
/calendar/2026/01
/calendar/2026/02
/calendar/2026/03
...
```

or:

```text
?page=1
?page=2
?page=3
...
```

Use depth and filtering controls to prevent runaway crawling.

---

# Calendar and Pagination Traps

Common crawler traps include:

- calendars;
- pagination;
- session IDs in URLs;
- search results;
- faceted filtering.

Watch for rapidly growing URL counts.

---

# Stop Unexpected Expansion

If a target begins generating thousands of low-value paths:

```text
Stop
Review
Refine scope/filtering
Resume
```

Do not let the crawler run indefinitely.

---

# Request Rate

Katana can generate substantial traffic.

Control:

- concurrency;
- rate;
- depth;
- target count.

Check current rate-related options:

```bash
katana -h
```

Start conservatively.

---

# Production Systems

For production applications:

- keep depth moderate;
- avoid excessive concurrency;
- exclude state-changing paths;
- monitor error rates;
- stop if instability appears.

Crawling should not become load testing.

---

# 429 Responses

If the server returns:

```text
429 Too Many Requests
```

the crawler is being rate limited.

Reduce request volume.

Do not attempt to bypass rate controls unless specifically authorised.

---

# WAF Behaviour

A WAF may respond with:

- 403;
- challenge pages;
- connection resets;
- CAPTCHA;
- rate limiting.

This can distort crawler results.

Record the control instead of automatically attempting evasion.

---

# Robots.txt

Review:

```text
/robots.txt
```

before large-scale crawling.

It may identify interesting paths.

Remember:

```text
robots.txt
```

is crawler guidance, not an access control mechanism.

---

# sitemap.xml

Sitemaps can provide high-quality deterministic endpoint discovery.

Use:

```text
/sitemap.xml
```

before relying solely on crawler exploration.

---

# Default 404 Behaviour

Before interpreting discovered unusual routes, understand missing-page behaviour.

Reference:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

Validate technology with multiple signals.

---

# Soft 404s

A crawler may encounter catch-all routes returning:

```text
200 OK
```

for any path.

Example:

```text
/random-test-123 -> SPA index page
```

This does not mean every path is a real endpoint.

---

# SPA Catch-All

Single-page applications often serve the same frontend HTML for:

```text
/
/users
/admin
/nonexistent
```

The client-side router then decides what to display.

Separate:

```text
server route
```

from:

```text
client route
```

---

# Manual Validation

For an interesting URL:

```bash
curl -i https://example.test/api/internal
```

or use Burp Repeater.

Check:

- method;
- response;
- authentication;
- content type;
- redirects;
- actual functionality.

---

# Burp Integration

A strong workflow is:

```text
Katana
  |
  v
Interesting URL
  |
  v
Burp Repeater
  |
  v
Understand Behaviour
  |
  v
Security Testing
```

Katana finds the route.

Burp helps understand it.

---

# Katana and ffuf

A practical order is:

```text
Katana
  |
  v
Linked Attack Surface
  |
  v
ffuf
  |
  v
Unlinked Candidate Paths
```

or run both independently and merge the results.

---

# Katana and Nuclei

Nuclei can consume known URLs for template-based checks.

A controlled chain may be:

```text
Katana
  |
  v
Deduplicated URLs
  |
  v
Select Relevant Targets
  |
  v
Nuclei
```

Do not automatically run every template against every discovered URL.

Related tool:

[Nuclei](nuclei.md)

---

# Katana and sqlmap

Katana may reveal parameterized URLs.

Example:

```text
/report?id=123
```

This does not justify immediately running sqlmap.

Use:

```text
Katana
  |
  v
Parameterized Endpoint
  |
  v
Manual Review
  |
  v
SQLi Hypothesis
  |
  v
sqlmap if appropriate
```

Related tool:

[sqlmap](sqlmap.md)

---

# Katana and Interactsh

Katana may discover features such as:

- webhooks;
- callback URLs;
- import-from-URL;
- image fetchers.

Those features may later be appropriate for controlled OOB testing.

Related tool:

[Interactsh](interactsh.md)

---

# JavaScript Analysis Workflow

A useful chain is:

```text
Katana
  |
  v
JavaScript URLs
  |
  v
Download / Inspect Relevant Scripts
  |
  v
Extract Endpoints
  |
  v
Manual Validation
```

Related note:

[JavaScript Analysis](../../reconnaissance/javascript-analysis.md)

---

# Parameter Discovery Workflow

Katana can provide existing parameter names.

For additional unknown parameters, use tools such as:

```text
ffuf
ParamSpider-style workflows
manual analysis
```

depending on the task.

---

# URL Inventory

A useful final crawl inventory might contain:

| URL | Method | Parameters | Source | Auth |
|---|---|---|---|---|
| `/login` | GET/POST | `username`, `password` | form | No |
| `/api/profile` | GET | none | JS | Yes |
| `/report` | GET | `id` | link | Yes |
| `/graphql` | POST | GraphQL | JS | Yes |

This is far more useful than a raw URL dump.

---

# Classify Endpoints

Useful categories include:

```text
Authentication
Account
Administration
API
Upload
Download
Search
Reporting
Webhook
Redirect
Internal
Debug
Health
```

Classification helps prioritise testing.

---

# High-Value Endpoint Types

Prioritise routes involving:

- authentication;
- authorisation;
- administration;
- file handling;
- URL fetching;
- exports;
- imports;
- secrets;
- account recovery;
- identity changes.

---

# Health Endpoints

Crawlers may discover:

```text
/health
/status
/metrics
```

These can be intended operational endpoints.

Assess:

- information exposed;
- authentication;
- environment.

Do not automatically report them.

---

# Debug Endpoints

Potentially interesting routes include:

```text
/debug
/trace
/dev
/internal
```

Again, validate actual behaviour.

A route name alone is not evidence.

---

# Error Endpoints

Some frameworks expose internal error handlers.

These may reveal:

- stack traces;
- framework versions;
- file paths.

Test safely and avoid intentionally causing large numbers of server errors.

---

# Authentication Paths

Crawling may identify:

```text
/login
/logout
/register
/reset-password
/mfa
/oauth/callback
```

These should be mapped as one authentication surface.

Related note:

[Authentication Testing](../../web/authentication.md)

---

# Authorisation Paths

Look for routes containing:

```text
/admin
/manage
/users
/accounts
/roles
/permissions
```

But route names are only hints.

The actual security control must be tested.

Related note:

[Authorisation Testing](../../web/authorisation.md)

---

# File Operations

Interesting endpoints may include:

```text
/upload
/download
/export
/import
/attachment
```

These can map to:

- file upload;
- traversal;
- insecure direct object reference;
- SSRF;
- parser attack surface.

---

# URL Fetching Features

Potential endpoint names include:

```text
/webhook
/callback
/fetch
/import-url
/preview
/image
```

These deserve further SSRF-oriented analysis where appropriate.

Related note:

[Server Side Request Forgery](../../web/ssrf.md)

---

# Output Handling

Katana supports multiple output modes depending on version.

Check:

```bash
katana -h
```

Structured output is preferable for larger assessments.

---

# JSON Output

Where supported, JSON output can preserve richer metadata than plain URLs.

Possible useful fields include:

- URL;
- source;
- method;
- request;
- response metadata.

Inspect the actual version's output structure before writing parsers.

---

# Plain URL Output

Plain output is useful for simple pipelines.

Example concept:

```bash
katana -u https://example.test -silent > urls.txt
```

Confirm the exact `-silent` behaviour using the installed version.

---

# Sort and Deduplicate

A basic Unix pattern is:

```bash
sort -u katana.txt > katana-unique.txt
```

This is appropriate for plain URL output.

Do not use it on JSON output.

---

# Extract Hosts

For authorised analysis, URL-processing tools or Python can help extract:

```text
scheme
host
path
query parameters
```

This can help identify accidental out-of-scope discoveries.

---

# Scope QA

After a crawl, check whether output includes unexpected domains.

Conceptually:

```text
cat katana.txt
      |
      v
Extract Hostnames
      |
      v
Compare with Scope
```

Remove out-of-scope targets from downstream automation.

---

# Evidence Collection

For a significant discovered endpoint, retain:

```text
Target:
Katana version:
Crawl command:
Scope:
Authentication context:
Depth:
Endpoint:
Discovery source:
Timestamp:
Manual validation:
```

This makes the result reproducible.

---

# Evidence Example

```text
Target:
https://portal.example.test

Context:
Authenticated standard user

Discovery:
Katana

Endpoint:
/api/export

Source:
Referenced by application JavaScript

Manual validation:
GET returned JSON metadata and required the standard user's active
session.

Conclusion:
Endpoint added to the authorised API attack-surface inventory.
```

No vulnerability is claimed unless later testing demonstrates one.

---

# Reporting

Katana itself usually does not produce findings.

Avoid:

```text
Katana found a vulnerability.
```

Prefer:

```text
Application crawling identified an undocumented administrative API
endpoint that was subsequently confirmed to expose sensitive
functionality without the expected authorisation control.
```

The finding comes from the endpoint behaviour.

---

# Hidden Endpoint Is Not a Vulnerability

An endpoint may be:

```text
not linked in UI
```

but still intentionally available.

Security depends on:

- authentication;
- authorisation;
- data exposure;
- functionality.

Do not rely on obscurity as the finding.

---

# Sensitive JavaScript Exposure

If JavaScript exposes internal details, describe what was actually disclosed.

For example:

```text
Client-side JavaScript disclosed an internal administrative API base
URL that was not otherwise referenced by the public user interface.
```

Then determine whether the endpoint itself is accessible.

---

# Source Map Reporting

If a source map exposes proprietary source:

```text
A production JavaScript source map was publicly accessible and contained
the original client-side source code and internal file structure.
```

The security significance depends on the disclosed information.

---

# Operational Safety

Before crawling ask:

```text
Is the target production?

What depth is necessary?

Does the application contain destructive GET routes?

Will JavaScript execution trigger actions?

Are third-party domains present?

What request rate is acceptable?
```

---

# Start Small

A good approach is:

```text
Single Target
     |
     v
Moderate Depth
     |
     v
Review Output
     |
     v
Expand If Needed
```

rather than immediately crawling every host deeply.

---

# Monitor Errors

During the crawl, watch for:

- 500 errors;
- timeouts;
- connection resets;
- rate limits;
- service degradation.

If instability appears, stop and reassess.

---

# Crawling Is Not Load Testing

The objective is:

```text
discover attack surface
```

not:

```text
maximize request throughput
```

Use appropriate limits.

---

# False Positives

Common crawler interpretation mistakes include:

- SPA catch-all routes;
- duplicate query values;
- third-party URLs;
- stale JavaScript references;
- inactive features;
- tracking endpoints;
- resources that redirect to login.

Manual validation resolves these.

---

# False Negatives

Katana may miss endpoints because of:

- authentication;
- complex JavaScript;
- WebSockets;
- unlinked routes;
- dynamic state;
- required user interaction;
- nonstandard protocols;
- depth limits.

A clean crawl does not prove the attack surface is complete.

---

# Combine Discovery Methods

A strong web attack-surface workflow uses multiple sources.

```text
Browser
   |
   +-- visible routes

Katana
   |
   +-- crawled routes

ffuf
   |
   +-- guessed paths

JavaScript analysis
   |
   +-- hidden API references

Documentation
   |
   +-- intended endpoints
```

Merge and deduplicate these.

---

# Practical Crawl Workflow

```text
1. Confirm scope
      |
      v
2. Confirm target responds
      |
      v
3. Understand baseline application
      |
      v
4. Run moderate Katana crawl
      |
      v
5. Save output
      |
      v
6. Check for out-of-scope URLs
      |
      v
7. Deduplicate
      |
      v
8. Review JavaScript/API paths
      |
      v
9. Classify high-value endpoints
      |
      v
10. Validate manually
      |
      v
11. Run authenticated crawl if required
      |
      v
12. Merge with ffuf/browser discovery
      |
      v
13. Feed validated inventory into testing
```

---

# Quick Command Reference

## Basic Crawl

```bash
katana -u https://example.test
```

## Help

```bash
katana -h
```

## Version

```bash
katana -version
```

## Crawl from Alive Hosts

```bash
katana -list alive.txt
```

Verify exact list-input syntax with the installed version.

## Pipeline from httpx

```bash
cat subdomains.txt | httpx -silent | katana
```

## Save Plain Output

```bash
katana -u https://example.test > katana.txt
```

## Deduplicate Plain URLs

```bash
sort -u katana.txt > katana-unique.txt
```

## Validate One URL

```bash
curl -i https://example.test/api/example
```

---

# Katana Checklist

## Preparation

- [ ] Target explicitly authorised.
- [ ] Scope documented.
- [ ] Third-party domains understood.
- [ ] Authentication requirements known.
- [ ] Katana version recorded.
- [ ] Request rate appropriate.
- [ ] Crawl depth selected deliberately.

## Crawl

- [ ] Basic crawl performed.
- [ ] Output saved.
- [ ] JavaScript endpoints considered.
- [ ] Forms reviewed.
- [ ] Query parameters retained.
- [ ] API routes reviewed.
- [ ] Redirects reviewed.
- [ ] Third-party destinations excluded.

## Authentication

- [ ] Approved test account used where required.
- [ ] Authentication data protected.
- [ ] Session expiry monitored.
- [ ] Role-specific crawls separated.
- [ ] Admin context used only when authorised.

## JavaScript

- [ ] Relevant JS files reviewed.
- [ ] Hidden API routes extracted.
- [ ] Source maps considered.
- [ ] Client-side secrets interpreted carefully.
- [ ] Stale references manually validated.

## Scope

- [ ] Output hostnames reviewed.
- [ ] Wildcard scope interpreted correctly.
- [ ] Redirect targets checked.
- [ ] Third-party SaaS excluded unless authorised.
- [ ] Downstream automation receives in-scope URLs only.

## Noise Reduction

- [ ] Static assets filtered only where appropriate.
- [ ] Duplicate URLs removed.
- [ ] SPA catch-all behaviour understood.
- [ ] Calendar/pagination traps checked.
- [ ] Filtering did not remove valuable `.js` or `.json` resources.

## Operational Safety

- [ ] Crawl is not excessive.
- [ ] State-changing routes treated cautiously.
- [ ] 429 responses respected.
- [ ] 500 spikes investigated.
- [ ] Application stability monitored.
- [ ] Crawl stopped if unexpected impact occurs.

## Validation

- [ ] High-value endpoints manually requested.
- [ ] Burp used where appropriate.
- [ ] Authentication checked.
- [ ] Authorisation checked separately.
- [ ] Hidden routes not automatically treated as vulnerabilities.
- [ ] Endpoint purpose understood.

## Evidence

- [ ] Target retained.
- [ ] Version retained.
- [ ] Command retained.
- [ ] Scope retained.
- [ ] Authentication context retained.
- [ ] Discovery source retained.
- [ ] Timestamp retained.
- [ ] Manual validation retained.

---

# Related Tool Notes

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

[ffuf](ffuf.md)

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

[GraphQL](../../web/graphql.md)

[Server Side Request Forgery](../../web/ssrf.md)

[JavaScript Analysis](../../reconnaissance/javascript-analysis.md)

---

# External References

## Katana

[Katana - GitHub](https://github.com/projectdiscovery/katana){ target="_blank" rel="noopener noreferrer" }

[Katana Documentation](https://docs.projectdiscovery.io/opensource/katana/overview){ target="_blank" rel="noopener noreferrer" }

## Supporting References

[ProjectDiscovery Documentation](https://docs.projectdiscovery.io/){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[HackTricks - Pentesting Web](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use Katana like this:

```text
Run Deep Crawl
      |
      v
Collect Thousands of URLs
      |
      v
Treat Every URL as Interesting
```

Use it like this:

```text
Confirm Scope
      |
      v
Identify Alive Web Target
      |
      v
Select Appropriate Crawl Depth
      |
      v
Run Controlled Katana Crawl
      |
      v
Check Scope of Discovered URLs
      |
      v
Extract Useful Paths / Parameters / JS
      |
      v
Deduplicate and Classify
      |
      v
Identify High-Value Endpoints
      |
      v
Validate Manually
      |
      v
Combine With ffuf / Browser Discovery
      |
      v
Feed Confirmed Attack Surface Into Testing
```

Katana is most valuable as an attack-surface discovery tool.

It helps show what the application links to, references, and exposes through normal or JavaScript-driven navigation.

The crawler discovers the routes.

The tester determines which routes matter, whether they are in scope, and whether any of them contain an actual security weakness.
