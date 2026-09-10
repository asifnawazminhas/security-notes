---
title: Content Discovery Cheatsheet
description: Detailed practical cheatsheet for authorised web content discovery using ffuf, Gobuster and feroxbuster, covering directory discovery, file discovery, extensions, recursion, filtering, virtual hosts, parameter discovery, output interpretation, validation and evidence collection.
---

# Content Discovery Cheatsheet

Content discovery attempts to identify web resources that are not immediately visible through normal application navigation.

Common targets include:

```text
Directories

Files

API endpoints

Administrative interfaces

Backup files

Configuration files

Development endpoints

Documentation

Legacy applications

Hidden functionality

Virtual hosts
```

Three commonly used tools are:

```text
ffuf

Gobuster

feroxbuster
```

They overlap, but each has strengths.

```text
ffuf
 |
 +--> Flexible fuzzing
 +--> Directories and files
 +--> Virtual hosts
 +--> Parameters
 +--> Values
 +--> Request templates
 +--> Powerful filtering

Gobuster
 |
 +--> Directory discovery
 +--> DNS discovery
 +--> Virtual hosts
 +--> Simple predictable CLI

feroxbuster
 |
 +--> Recursive content discovery
 +--> Automatic link extraction
 +--> Large application trees
 +--> Fast recursive enumeration
```

!!! warning "Authorised Security Testing"

    Content discovery can generate substantial numbers of HTTP requests. Only enumerate systems that are explicitly within scope. Configure request rates, recursion depth, wordlists and concurrency according to the rules of engagement and the capacity of the target.


# Quick Reference

## ffuf Directory Discovery

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ
```

## ffuf File Extensions

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -e .php,.html,.txt
```

## Gobuster Directory Discovery

```bash
gobuster dir -u https://example.com/ -w wordlist.txt
```

## Gobuster Extensions

```bash
gobuster dir -u https://example.com/ -w wordlist.txt -x php,html,txt
```

## feroxbuster

```bash
feroxbuster -u https://example.com/
```

## feroxbuster With Wordlist

```bash
feroxbuster -u https://example.com/ -w wordlist.txt
```

## ffuf Virtual Hosts

```bash
ffuf -w subdomains.txt -u https://example.com/ -H "Host: FUZZ.example.com"
```

## Gobuster Virtual Hosts

```bash
gobuster vhost -u https://example.com/ -w subdomains.txt --append-domain
```

## ffuf POST Parameter Names

```bash
ffuf -w parameters.txt -u https://example.com/api/search -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "FUZZ=test"
```


# Install Tools

## ffuf

On Kali Linux:

```bash
sudo apt update
sudo apt install ffuf
```

Verify:

```bash
ffuf -V
```

Help:

```bash
ffuf -h
```


# Gobuster

Install:

```bash
sudo apt update
sudo apt install gobuster
```

Verify:

```bash
gobuster version
```

Help:

```bash
gobuster --help
```


# feroxbuster

Install:

```bash
sudo apt update
sudo apt install feroxbuster
```

Verify:

```bash
feroxbuster --version
```

Help:

```bash
feroxbuster --help
```


# Wordlists

Wordlist selection strongly affects content discovery.

On Kali Linux, useful wordlists may be available under:

```text
/usr/share/wordlists/
```

SecLists is commonly used for web discovery.

Typical location when installed:

```text
/usr/share/seclists/
```


# Install SecLists

```bash
sudo apt install seclists
```

Explore:

```bash
ls /usr/share/seclists/
```

Web content lists:

```bash
ls /usr/share/seclists/Discovery/Web-Content/
```


# Useful SecLists Wordlists

Examples commonly useful for initial discovery include:

```text
common.txt

directory-list-2.3-small.txt

directory-list-2.3-medium.txt

raft-small-words.txt

raft-medium-words.txt

raft-large-words.txt

raft-small-directories.txt

raft-medium-directories.txt

raft-small-files.txt

raft-medium-files.txt
```


# Wordlist Strategy

Do not immediately use the largest available wordlist.

Prefer:

```text
Small Targeted List
        |
        v
Review Results
        |
        v
Technology-Specific List
        |
        v
Medium List
        |
        v
Larger List If Needed
```

This reduces unnecessary traffic.


# Start With Application Mapping

Before brute-force discovery:

```text
Browse Application
      |
      v
Review robots.txt
      |
      v
Review sitemap.xml
      |
      v
Review JavaScript
      |
      v
Review Proxy History
      |
      v
Crawl
      |
      v
Content Discovery
```

Brute-force discovery should complement normal application mapping rather than replace it.


# Manual Checks First

Useful initial requests:

```text
/robots.txt

/sitemap.xml

/.well-known/

/security.txt
```

For example:

```bash
curl -i https://example.com/robots.txt
```

```bash
curl -i https://example.com/sitemap.xml
```


# Establish a Baseline

Before enumeration, request a path that almost certainly does not exist:

```bash
curl -i https://example.com/this-path-should-not-exist-938475
```

Observe:

```text
Status code

Content length

Response body

Redirect

Headers
```

This is important because applications may return:

```text
200 OK
```

for nonexistent resources.


# Standard 404

Example:

```http
HTTP/1.1 404 Not Found
Content-Type: text/html
Content-Length: 153
```

This makes filtering relatively straightforward.


# Soft 404

A soft 404 may look like:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 4217

<html>
...
Page not found
...
</html>
```

The HTTP status says:

```text
200
```

but the application behaviour means:

```text
Resource does not exist.
```

This must be accounted for during enumeration.


# Redirect-Based Not Found

Another application may respond:

```http
HTTP/1.1 302 Found
Location: /not-found
```

Every invalid path could therefore appear interesting unless the baseline is understood.


# Content Discovery Model

```text
Wordlist Entry
      |
      v
HTTP Request
      |
      v
Response
      |
      v
Status + Size + Words + Lines
      |
      v
Filter Known Noise
      |
      v
Candidate Resource
      |
      v
Manual Validation
```


# ffuf

ffuf uses the keyword:

```text
FUZZ
```

to identify the location where values from the wordlist should be inserted.


# Basic ffuf Directory Discovery

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ
```

Possible output:

```text
admin                   [Status: 302, Size: 0, Words: 1, Lines: 1]
api                     [Status: 200, Size: 812, Words: 93, Lines: 24]
assets                  [Status: 301, Size: 178, Words: 6, Lines: 8]
login                   [Status: 200, Size: 3481, Words: 421, Lines: 87]
```


# Interpret ffuf Output

Example:

```text
api [Status: 200, Size: 812, Words: 93, Lines: 24]
```

This means the request using:

```text
/api
```

returned:

```text
Status: 200

Response size: 812 bytes

Words: 93

Lines: 24
```

It does not mean `/api` is vulnerable.

It means:

```text
/api is a discovery candidate worth reviewing.
```


# ffuf File Discovery

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -u https://example.com/FUZZ
```


# Extensions

If the application uses PHP:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -e .php
```

Multiple extensions:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/common.txt -u https://example.com/FUZZ -e .php,.html,.txt,.json
```


# Technology-Specific Extensions

Possible extensions depend on the application.

```text
PHP

.php
.inc

ASP.NET

.aspx
.ashx
.asmx
.config

Java

.jsp
.do
.action

Static

.html
.htm
.js
.json
.xml
.txt
```


# Do Not Guess Extensions Blindly

Determine technology first using:

```text
HTTP headers

Cookies

HTML

JavaScript

Wappalyzer

WhatWeb

Application behaviour
```

Then select relevant extensions.


# ffuf Status Filtering

Match specific status codes:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -mc 200,204,301,302,307,401,403
```


# Status Codes Worth Reviewing

Common interesting responses:

```text
200

204

301

302

307

308

401

403
```

But context matters.

A:

```text
403
```

can be highly interesting because it may confirm that a resource exists but access is restricted.


# 403 Interpretation

Example:

```text
admin [Status: 403, Size: 287]
```

This supports:

```text
The server handles /admin differently from a nonexistent path.
```

It does not automatically prove:

```text
/admin exists as an accessible application interface.
```

Manually verify the behaviour.


# Filter Status

Exclude a status:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -fc 404
```

Multiple:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -fc 404,400
```


# Filter by Size

Suppose invalid paths always return:

```text
Size: 4217
```

Filter:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -fs 4217
```


# Why Size Filtering Matters

Suppose:

```text
random123     200 4217
doesnotexist  200 4217
fakepage      200 4217
admin         200 9281
```

The common:

```text
4217
```

response is probably the application's soft 404.

Filtering it makes:

```text
admin 200 9281
```

stand out.


# Filter Words

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -fw 42
```


# Filter Lines

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -fl 15
```


# Match Size

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -ms 812
```


# Auto Calibration

ffuf provides automatic calibration functionality.

A common invocation is:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -ac
```

Automatic calibration can help reduce repetitive baseline responses.

Still manually understand the application's not-found behaviour rather than relying exclusively on automatic filtering.


# ffuf Recursion

Where appropriate:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -recursion
```

Control depth:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -recursion -recursion-depth 2
```


# Recursion Risk

Without careful controls:

```text
/
 |
 +-- api/
 |    |
 |    +-- v1/
 |         |
 |         +-- users/
 |
 +-- assets/
 |    |
 |    +-- js/
 |
 +-- admin/
```

can rapidly produce a large request volume.

Set reasonable depth.


# ffuf Threads

ffuf supports concurrency configuration.

Before increasing concurrency, consider:

```text
Target capacity

Rules of engagement

WAF

Rate limiting

Monitoring

Production impact
```

Faster is not automatically better.


# ffuf Delay

Where request pacing is needed, review the current ffuf help for the supported delay/rate controls:

```bash
ffuf -h
```

Use conservative rates on production systems.


# ffuf Headers

Add a header:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -H "X-Test: authorised-assessment"
```


# Authenticated Discovery

Cookie example:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -H "Cookie: session=<session>"
```

Bearer token:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -H "Authorization: Bearer <token>"
```

Do not place real credentials in shell history unnecessarily.


# Authenticated vs Unauthenticated Discovery

Comparing both views can be useful:

```text
Unauthenticated
      |
      v
Discovered Paths

Authenticated
      |
      v
Discovered Paths

      |
      v
Compare
```

This may reveal functionality exposed only after authentication.


# ffuf Output

Save JSON:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -o ffuf-results.json -of json
```

HTML output where supported:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -o ffuf-results.html -of html
```

CSV:

```bash
ffuf -w wordlist.txt -u https://example.com/FUZZ -o ffuf-results.csv -of csv
```


# Preserve Assessment Results

Useful naming:

```text
example.com-ffuf-root.json

example.com-ffuf-api.json

example.com-ffuf-authenticated.json
```


# ffuf Virtual Host Discovery

Some applications use multiple virtual hosts on the same IP.

Conceptually:

```text
IP Address
   |
   +--> www.example.com
   |
   +--> api.example.com
   |
   +--> admin.example.com
```


# Host Header Fuzzing

```bash
ffuf -w subdomains.txt -u https://example.com/ -H "Host: FUZZ.example.com"
```


# Virtual Host Baseline

Before trusting results, send a random hostname:

```bash
curl -k -i https://example.com/ -H "Host: random-does-not-exist.example.com"
```

Observe the default response.


# VHost False Positives

A web server may return the same default site for every Host header.

Example:

```text
admin.example.com   -> 200 / 8124 bytes
fake.example.com    -> 200 / 8124 bytes
random.example.com  -> 200 / 8124 bytes
```

This does not demonstrate three valid virtual hosts.

Filter the default response.


# ffuf VHost Size Filter

If the default response is:

```text
8124 bytes
```

use:

```bash
ffuf -w subdomains.txt -u https://example.com/ -H "Host: FUZZ.example.com" -fs 8124
```


# Validate VHost Candidate

Suppose:

```text
admin [Status: 200, Size: 12831]
```

Manually test:

```bash
curl -k -i https://example.com/ -H "Host: admin.example.com"
```

Then compare against the baseline.


# DNS vs Virtual Host

Do not confuse:

```text
DNS enumeration
```

with:

```text
HTTP virtual-host discovery.
```

A hostname may:

```text
exist in DNS but not host a unique web application
```

or:

```text
be recognised by the web server without public DNS.
```


# ffuf Parameter Name Discovery

Suppose an endpoint is:

```text
/search
```

A controlled parameter-name test could use:

```bash
ffuf -w parameters.txt -u 'https://example.com/search?FUZZ=test'
```

Compare responses against a random parameter.


# Parameter Baseline

```bash
curl -i 'https://example.com/search?randomparameter=test'
```

Then compare discovered candidates.


# POST Parameter Discovery

```bash
ffuf -w parameters.txt \
  -u https://example.com/search \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "FUZZ=test"
```


# JSON Parameter Discovery

Example:

```bash
ffuf -w parameters.txt \
  -u https://example.com/api/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"FUZZ":"test"}'
```

Use only where the request format and endpoint are already understood.


# Parameter Discovery Interpretation

Suppose:

```text
randomparameter -> 400 / 91 bytes
debug           -> 200 / 812 bytes
```

This suggests:

```text
debug
```

may be recognised differently.

It does not prove the parameter creates a security issue.


# Parameter Value Fuzzing

Suppose the parameter is known:

```text
?format=json
```

Values can be tested:

```bash
ffuf -w values.txt -u 'https://example.com/export?format=FUZZ'
```

Use targeted value lists rather than arbitrary high-volume fuzzing.


# Multiple FUZZ Positions

ffuf can support more advanced workflows using multiple wordlists and keywords.

For complex testing, check:

```bash
ffuf -h
```

and use named input keywords deliberately rather than creating uncontrolled combinatorial request volumes.


# Request From File

For complex authenticated requests, saving the request from Burp can be useful.

A raw request might look like:

```http
POST /api/search HTTP/1.1
Host: example.com
Authorization: Bearer <token>
Content-Type: application/json

{"query":"FUZZ"}
```

ffuf supports raw request-based workflows. Confirm the exact options supported by your installed version:

```bash
ffuf -h
```

This is especially useful when:

```text
Cookies

Custom headers

JSON bodies

Authentication

Complex request structure
```

are involved.


# Burp + ffuf Workflow

```text
Browser
   |
   v
Burp Proxy
   |
   v
Interesting Request
   |
   v
Save Request
   |
   v
Replace Input With FUZZ
   |
   v
ffuf
   |
   v
Candidates
   |
   v
Burp Repeater
   |
   v
Manual Validation
```


# Proxy ffuf Through Burp

For selected controlled tests, proxying through Burp can make requests visible for analysis.

Check the current proxy option:

```bash
ffuf -h
```

This can be useful when debugging a small test, but sending a large fuzzing run through Burp may create enormous HTTP history.


# Gobuster

Gobuster provides several enumeration modes.

Display available commands:

```bash
gobuster --help
```


# Gobuster Directory Mode

Basic:

```bash
gobuster dir -u https://example.com/ -w /usr/share/seclists/Discovery/Web-Content/common.txt
```


# Gobuster Extensions

```bash
gobuster dir \
  -u https://example.com/ \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -x php,html,txt
```


# Gobuster Status Codes

Review the installed version's directory-mode options:

```bash
gobuster dir --help
```

Use status filtering based on the target's baseline behaviour.


# Gobuster Cookies

For authenticated discovery, inspect:

```bash
gobuster dir --help
```

and use the supported cookie/header options for your installed version.

Avoid copying sensitive session tokens into shared terminal logs.


# Gobuster Headers

Custom headers are useful for:

```text
Authentication

Assessment identifiers

Application-specific headers
```

Check:

```bash
gobuster dir --help
```

for exact syntax supported by the installed release.


# Gobuster Output

Save output:

```bash
gobuster dir \
  -u https://example.com/ \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -o gobuster-results.txt
```


# Gobuster VHost Mode

```bash
gobuster vhost \
  -u https://example.com/ \
  -w subdomains.txt \
  --append-domain
```

Again, establish the default Host response first.


# Gobuster VHost Validation

```text
Candidate
   |
   v
Manual curl Request
   |
   v
Compare Against Random Host
   |
   v
Distinct Application?
```


# Gobuster DNS Mode

Gobuster also provides DNS enumeration functionality.

Check:

```bash
gobuster dns --help
```

Use DNS mode only for domains included within the authorised scope.


# Gobuster Strength

Gobuster is useful when you want:

```text
Simple CLI

Predictable directory discovery

VHost discovery

DNS enumeration

Easy text output
```


# feroxbuster

feroxbuster focuses heavily on recursive web content discovery.

Basic:

```bash
feroxbuster -u https://example.com/
```


# Custom Wordlist

```bash
feroxbuster \
  -u https://example.com/ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
```


# Extensions

```bash
feroxbuster \
  -u https://example.com/ \
  -x php,html,txt,json
```


# Recursion

Recursive enumeration is a core feroxbuster feature.

Conceptually:

```text
/
 |
 +-- admin/
 |     |
 |     +-- users/
 |     |
 |     +-- settings/
 |
 +-- api/
       |
       +-- v1/
             |
             +-- accounts/
```

This is useful for larger hierarchical applications.


# Depth

Limit recursion depth according to the assessment.

Check supported options:

```bash
feroxbuster --help
```

Avoid unnecessary deep recursion.


# feroxbuster Filters

Filtering may be based on characteristics such as:

```text
Status

Size

Words

Lines
```

Use:

```bash
feroxbuster --help
```

to confirm exact options for the installed release.


# feroxbuster Headers

Authenticated or custom-header discovery is possible.

Check:

```bash
feroxbuster --help
```

and use only the options required for the assessment.


# feroxbuster Output

Save results according to the options supported by the installed version.

A useful naming pattern is:

```text
example.com-ferox-root.txt
```


# feroxbuster Strength

feroxbuster is especially useful for:

```text
Recursive discovery

Large site trees

Link extraction

Finding nested content

Automated traversal
```


# Choosing the Tool

| Requirement | ffuf | Gobuster | feroxbuster |
|---|---:|---:|---:|
| Directory discovery | Excellent | Excellent | Excellent |
| File discovery | Excellent | Excellent | Excellent |
| Extension discovery | Excellent | Excellent | Excellent |
| Recursion | Good | Limited workflow | Excellent |
| Parameter fuzzing | Excellent | Not primary use | Not primary use |
| Value fuzzing | Excellent | Not primary use | Not primary use |
| Virtual hosts | Excellent | Excellent | Not primary use |
| DNS enumeration | Not primary use | Yes | No |
| Flexible request body | Excellent | Limited | Limited |
| Response filtering | Excellent | Good | Excellent |
| Large recursive site mapping | Good | Basic | Excellent |


# Recommended Workflow

A useful assessment sequence is:

```text
Browser / Burp
      |
      v
Passive Discovery
      |
      v
robots.txt / sitemap.xml
      |
      v
JavaScript Analysis
      |
      v
Crawler
      |
      v
Small Wordlist
      |
      v
Review
      |
      v
Technology-Specific Discovery
      |
      v
Recursive Discovery
      |
      v
Manual Validation
```


# Root Discovery

Start:

```bash
ffuf \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -u https://example.com/FUZZ
```


# Then Target Interesting Directories

Suppose:

```text
/api
```

is discovered.

Run targeted discovery:

```bash
ffuf \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -u https://example.com/api/FUZZ
```

This is usually better than blindly increasing the global wordlist size.


# Recursive Strategy

```text
/
 |
 +--> api/
 |      |
 |      +--> Targeted discovery
 |
 +--> admin/
 |      |
 |      +--> Targeted discovery
 |
 +--> assets/
        |
        +--> Usually lower priority
```

Prioritise based on security relevance.


# Prioritising Results

Higher-priority candidates often include:

```text
/admin

/api

/internal

/debug

/manage

/management

/swagger

/api-docs

/graphql

/upload

/download

/export

/import

/backup

/config

/health

/metrics
```

But the significance depends entirely on application context.


# API Documentation

Potentially useful discovery candidates:

```text
/swagger

/swagger-ui

/api-docs

/openapi.json

/swagger.json
```

If found, review whether documentation exposure is intended and whether it reveals security-relevant functionality.


# GraphQL

Common paths:

```text
/graphql

/api/graphql
```

Discovery alone does not establish insecure GraphQL configuration.

See [GraphQL Notes](../web/graphql.md).


# Health and Metrics

Possible paths:

```text
/health

/healthz

/status

/metrics
```

These may be intentional operational endpoints.

Review:

```text
Information disclosed

Authentication

Network exposure

Environment details
```


# Development and Debug Endpoints

Potential terms:

```text
/debug

/dev

/test

/console

/internal
```

A name is only a clue.

Determine actual functionality and access control.


# Administrative Paths

Potential:

```text
/admin

/administrator

/manage

/management

/control
```

A discovered login page is not automatically a vulnerability.


# Backup Files

Backup files can sometimes expose source or configuration.

Possible naming patterns include:

```text
file.bak

file.old

file.backup

file~
```

Use targeted discovery where justified rather than indiscriminately multiplying every path by many extensions.


# Source Maps

JavaScript source maps may use:

```text
.js.map
```

Review JavaScript references and deployed static assets.

Source maps can improve source analysis but their presence alone is not necessarily a vulnerability.


# Response Interpretation

Do not classify only by status code.

Use:

```text
Status

Size

Words

Lines

Title

Headers

Redirect

Body

Authentication state
```


# Example Results

```text
admin       403  287
api         200  812
random123   200  4217
debug       302  0
backup      404  153
```


# Interpretation

```text
admin
 |
 +--> 403 differs from baseline
 |
 +--> Validate manually

api
 |
 +--> 200 and distinct size
 |
 +--> Review content

random123
 |
 +--> Matches known soft 404
 |
 +--> Ignore/filter

debug
 |
 +--> Redirect
 |
 +--> Follow redirect manually

backup
 |
 +--> Standard 404
 |
 +--> No evidence of resource
```


# 401 vs 403

Typical interpretation:

```text
401
 |
 +--> Authentication required

403
 |
 +--> Request understood but access denied
```

Actual application behaviour may vary.

Both can identify interesting attack surface.


# Redirects

Suppose:

```text
/admin -> 302 /login
```

This may indicate:

```text
/admin exists and requires authentication
```

or:

```text
the application redirects all unknown paths to /login.
```

Test a random path:

```bash
curl -i https://example.com/random-does-not-exist-283746
```

Compare.


# Response Size Clustering

Suppose results contain:

```text
200 4217
200 4217
200 4217
200 4217
200 9281
200 4217
```

The outlier:

```text
9281
```

deserves attention.


# Size Is Not Everything

Dynamic pages may change response length because of:

```text
CSRF tokens

Timestamps

Request IDs

Advertisements

User information

Random content
```

Use multiple response characteristics.


# Wildcard Responses

Some servers respond successfully for any path.

Example:

```text
/a123      -> 200
/b456      -> 200
/random    -> 200
/admin     -> 200
```

Compare bodies and sizes before trusting results.


# Authentication Context

Content discovery results may change between:

```text
Unauthenticated

Standard User

Privileged User
```

This can reveal role-specific application surfaces.


# Controlled Comparison

```text
Unauthenticated Crawl
         |
         v
Paths A

Standard User Crawl
         |
         v
Paths B

Admin Crawl
         |
         v
Paths C
```

Compare these sets during an authorised role-based assessment.


# Discovered Does Not Mean Accessible

A resource may return:

```text
401

403

302 -> login
```

and still be valuable for mapping.

The finding is not:

```text
"Hidden endpoint exists."
```

The security question is:

```text
Is the endpoint exposed inappropriately?

Does it disclose sensitive information?

Are authentication and authorisation correct?

Does it contain vulnerable functionality?
```


# Content Discovery and Authorisation

Suppose you discover:

```text
/api/admin/users
```

Do not immediately attempt arbitrary modifications.

First:

```text
Capture baseline

Determine expected role

Use controlled test account

Send GET where safe

Compare role behaviour

Validate authorisation
```


# Burp Repeater Validation

Every high-value candidate should usually be manually reviewed.

```text
ffuf / Gobuster / feroxbuster
            |
            v
         Candidate
            |
            v
       Burp Repeater
            |
            v
         Baseline
            |
            v
       Controlled Test
            |
            v
       Interpretation
```


# Validate With curl

Example:

```bash
curl -k -i https://example.com/admin
```

Authenticated:

```bash
curl -k -i https://example.com/admin \
  -H "Cookie: session=<session>"
```


# Content Discovery and JavaScript

JavaScript often reveals endpoints more efficiently than brute force.

Search downloaded JavaScript:

```bash
rg -ni '/api/|/admin|/internal|graphql|upload|download' .
```

Then validate discovered routes.


# Crawler + Content Discovery

A strong workflow:

```text
Crawler
   |
   v
Known URLs
   |
   v
Extract Directories
   |
   v
Targeted Wordlists
   |
   v
ffuf / feroxbuster
```

This is more efficient than treating every target identically.


# Wordlist Customisation

Build application-specific words from:

```text
Company terminology

Feature names

JavaScript

API routes

Page titles

Technology

Product names

Documentation
```

Example:

```text
invoice

billing

customer

employee

portal

reports

exports
```

Save:

```text
custom.txt
```


# Combine Wordlists

```bash
cat common.txt custom.txt | sort -u > combined.txt
```

Then:

```bash
ffuf -w combined.txt -u https://example.com/FUZZ
```


# Extract Candidate Words From URLs

If you already have URLs in:

```text
urls.txt
```

manual processing can help build a targeted list.

For example:

```bash
cat urls.txt | sed 's/[?#].*$//' | tr '/' '\n' | sort -u
```

Review the output before using it as a wordlist.


# Avoid Blind Wordlist Expansion

Do not automatically combine:

```text
100,000 words
x
20 extensions
x
multiple hosts
x
deep recursion
```

This can create millions of requests.

Estimate impact first.


# Request Estimate

Conceptually:

```text
Requests =
Wordlist Entries
x
Extensions
x
Targets
x
Recursive Locations
```

Example:

```text
20,000 words
x
5 extensions
x
4 discovered directories

= approximately 400,000 candidate requests
```

This matters during production assessments.


# Rate Control

Before large enumeration establish:

```text
Maximum acceptable rate

Maximum concurrency

Testing window

Monitoring expectations

Stop conditions
```

If the application begins returning:

```text
429

502

503

504
```

investigate whether your testing is contributing to instability.


# WAF Behaviour

Content discovery may trigger:

```text
WAF

Rate limiting

Bot protection

IP blocking
```

Do not attempt to evade defensive controls unless that behaviour is explicitly part of the assessment scope.


# 429 Responses

Example:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

Reduce request rate.

Do not treat rate limiting as an obstacle that must automatically be bypassed.


# 503 Responses

Repeated:

```text
503 Service Unavailable
```

during enumeration may indicate service stress or defensive throttling.

Stop or reduce activity according to the rules of engagement.


# TLS Errors

For a lab or authorised target using a self-signed certificate, tools may require configuration to handle certificate verification appropriately.

Do not globally disable certificate validation on your system merely to simplify testing.


# DNS Resolution

If:

```text
https://app.internal.example.com
```

does not resolve, first verify:

```bash
dig app.internal.example.com
```

or:

```bash
host app.internal.example.com
```

In lab environments, a hosts entry may be required:

```text
192.0.2.10 app.internal.example.com
```

Only modify resolution for known authorised targets.


# Proxy and VPN

If discovery works in the browser but not the CLI, check:

```text
VPN route

DNS

Proxy configuration

Host resolution

TLS

Authentication
```


# Content Discovery Through a VPN

Confirm target connectivity before fuzzing:

```bash
curl -I https://example.com/
```

Then run discovery.


# Common Mistake - No Baseline

Bad:

```text
Run ffuf
 |
 v
Thousands of 200 responses
 |
 v
Assume thousands of files
```

Better:

```text
Random Path
 |
 v
Understand 404 Behaviour
 |
 v
Configure Filters
 |
 v
Run Discovery
```


# Common Mistake - Filtering Every 403

Do not automatically discard:

```text
403
```

A forbidden resource may reveal important application structure.

Keep useful 403 responses and investigate manually.


# Common Mistake - Treating Every 200 as Valid

Soft 404 pages frequently return:

```text
200 OK
```

Compare:

```text
Size

Words

Lines

Body

Title
```


# Common Mistake - Using Only One Wordlist

Different wordlists contain different naming styles.

Use wordlists based on:

```text
Technology

Application type

Initial results

Target terminology
```


# Common Mistake - Starting With Huge Lists

Large wordlists increase:

```text
Traffic

Time

Noise

Rate-limit risk

Operational impact
```

Start targeted.


# Common Mistake - Ignoring Extensions

A directory wordlist might test:

```text
config
```

but the actual resource could be:

```text
config.php
```

Use technology-appropriate extensions.


# Common Mistake - Too Much Recursion

Recursive enumeration can explode:

```text
/
 |
 +-- a/
 |   +-- a/
 |   +-- b/
 |
 +-- b/
     +-- a/
     +-- b/
```

Limit depth.


# Common Mistake - Not Saving Results

Always save significant enumeration results.

Otherwise:

```text
Interesting Resource
       |
       v
Terminal Scrollback Lost
       |
       v
Cannot Reproduce Evidence
```


# Common Mistake - Reporting Discovery Alone

Weak:

> `/admin` exists.

Better assessment reasoning:

```text
/admin discovered
       |
       v
Authentication required?
       |
       v
Authorisation correct?
       |
       v
Sensitive functionality?
       |
       v
Security consequence?
```


# Common Mistake - Ignoring Scope

A discovered redirect may lead to:

```text
thirdparty.example.net
```

Do not continue testing it unless explicitly authorised.


# Common Mistake - Fuzzing Destructive Endpoints

Be careful with:

```text
/delete

/reset

/logout

/payment

/checkout

/admin/actions
```

Automated requests may change application state.


# Discovery Evidence

Record:

```text
Target

Timestamp

Tool

Tool version

Command

Wordlist

Authentication context

Request rate

Filters

Result

Manual validation
```


# Example Evidence

```text
Target:
https://example.com/

Tool:
ffuf

Wordlist:
common.txt

Authentication:
Unauthenticated

Candidate:
/api

Automated Result:
200 / 812 bytes

Manual Validation:
GET /api returned JSON API metadata.

Security Conclusion:
Attack-surface discovery only. No vulnerability established by discovery alone.
```


# Finding vs Observation

Content discovery often produces:

```text
Assessment Observation
```

rather than:

```text
Security Finding.
```

Example:

```text
/swagger discovered
```

is an observation.

If it exposes sensitive internal API documentation without intended access controls, that may support a finding depending on context and impact.


# Reporting Example - Exposed Backup

Weak:

> backup.zip found.

Better:

> An unauthenticated request to `/backup.zip` returned an application backup archive. The archive contained server-side application source and configuration information. The file was accessible without authentication and was not linked through the normal application interface.


# Reporting Example - Admin Interface

Weak:

> Hidden admin panel.

Better:

> Content discovery identified the `/admin/` application route. Manual validation confirmed that the route presents the administrative authentication interface. No authentication bypass was identified; therefore the route itself was treated as attack-surface information rather than a vulnerability.


# Reporting Example - Debug Endpoint

Weak:

> `/debug` exists.

Better:

> The `/debug` endpoint was accessible without authentication and returned application environment information including internal service names and runtime configuration. The exposure was manually reproduced independently of the discovery tool.


# Reporting Example - API Documentation

Weak:

> Swagger exposed.

Better:

> The application exposed its OpenAPI documentation without authentication at `/openapi.json`. The documentation enumerated internal administrative API operations not otherwise visible to unauthenticated users. The security significance depends on whether this documentation is intended to be public and whether the disclosed information materially assists unauthorised access.


# Retesting

After remediation, repeat the exact original request first.

Example:

```bash
curl -i https://example.com/backup.zip
```

Expected:

```text
404
```

or another intended secure response.


# Do Not Retest Only With ffuf

For a reported resource:

```text
Original Exact Request
       |
       v
Manual Retest
       |
       v
Confirm Secure Behaviour
```

Then optionally rerun discovery to identify equivalent exposures.


# Equivalent Resources

If:

```text
backup.zip
```

was exposed, consider safe searches for equivalent deployment artefacts according to scope.

The root cause may be:

```text
Deployment process publishes backup files
```

rather than one specific filename.


# Discovery Comparison

Save results over time:

```text
before.txt

after.txt
```

Compare:

```bash
diff -u before.txt after.txt
```

This can assist remediation validation.


# Tool Selection Workflow

```text
Need Flexible Fuzzing?
       |
      Yes
       |
       v
      ffuf

Need Simple Directory / VHost / DNS?
       |
      Yes
       |
       v
    Gobuster

Need Recursive Site Discovery?
       |
      Yes
       |
       v
  feroxbuster
```


# Practical Assessment Workflow

```text
                         TARGET
                            |
                            v
                       SCOPE CHECK
                            |
                            v
                      BASELINE REQUEST
                            |
                            v
                  robots.txt / sitemap.xml
                            |
                            v
                      NORMAL BROWSING
                            |
                            v
                        BURP PROXY
                            |
                            v
                       CRAWL / JS
                            |
                            v
                    CONTENT DISCOVERY
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
            ffuf        Gobuster      feroxbuster
             |              |              |
             +--------------+--------------+
                            |
                            v
                       FILTER NOISE
                            |
                            v
                    PRIORITISE RESULTS
                            |
                            v
                     MANUAL VALIDATION
                            |
                   +--------+--------+
                   |                 |
                   v                 v
             ATTACK SURFACE      SECURITY ISSUE
                   |                 |
                   v                 v
               DOCUMENT          EVIDENCE
                                     |
                                     v
                                  REPORT
```


# Quick ffuf Workflow

```text
Random Path
    |
    v
Determine Baseline
    |
    v
Select Wordlist
    |
    v
Run ffuf
    |
    v
Filter Baseline
    |
    v
Review Outliers
    |
    v
Validate With curl/Burp
```


# Quick feroxbuster Workflow

```text
Target
  |
  v
Set Wordlist
  |
  v
Set Depth
  |
  v
Run
  |
  v
Recursive Results
  |
  v
Prioritise
  |
  v
Manual Validation
```


# Quick VHost Workflow

```text
Target IP / Host
      |
      v
Random Host Header
      |
      v
Baseline Response
      |
      v
VHost Wordlist
      |
      v
ffuf / Gobuster
      |
      v
Filter Baseline
      |
      v
Distinct Response
      |
      v
Manual Validation
```


# Quick Parameter Workflow

```text
Known Endpoint
     |
     v
Random Parameter
     |
     v
Baseline
     |
     v
Parameter Wordlist
     |
     v
ffuf
     |
     v
Response Outlier
     |
     v
Manual Validation
```


# Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| `200` response | Request succeeded | Resource is security sensitive |
| `301/308` | Redirect exists | Vulnerability |
| `302` | Redirect behaviour | Authentication bypass |
| `401` | Authentication-related restriction | Secure authorisation |
| `403` | Access denied / distinct handling | Resource exploitable |
| Different size | Different response | Valid resource |
| Different word count | Response changed | Vulnerability |
| Soft 404 | Custom not-found behaviour | Resource exists |
| VHost size differs | Host handled differently | Valid production hostname |
| Parameter changes response | Parameter may be recognised | Security issue |
| `/admin` discovered | Administrative attack surface | Admin bypass |
| Swagger found | API documentation exposed | Sensitive disclosure |
| `/debug` found | Debug-named route exists | Debug information exposed |


# Content Discovery Checklist

## Before Discovery

- [ ] Scope confirmed
- [ ] Target reachable
- [ ] DNS verified
- [ ] VPN verified
- [ ] Technology identified where possible
- [ ] Random nonexistent path tested
- [ ] 404 behaviour understood
- [ ] Redirect behaviour understood
- [ ] Soft 404 checked
- [ ] Authentication context recorded
- [ ] Request rate considered

## Passive Discovery

- [ ] `robots.txt` checked
- [ ] `sitemap.xml` checked
- [ ] HTML reviewed
- [ ] JavaScript reviewed
- [ ] Burp HTTP history reviewed
- [ ] Existing crawler results reviewed

## Wordlists

- [ ] Small initial wordlist selected
- [ ] Technology-specific words considered
- [ ] Application-specific words considered
- [ ] Extensions selected based on technology
- [ ] Duplicate words removed
- [ ] Request count considered

## ffuf

- [ ] Correct `FUZZ` position selected
- [ ] Status filtering configured
- [ ] Size filtering considered
- [ ] Word filtering considered
- [ ] Line filtering considered
- [ ] Authentication headers added where required
- [ ] Recursion depth controlled
- [ ] Results saved

## Gobuster

- [ ] Correct mode selected
- [ ] Wordlist selected
- [ ] Extensions considered
- [ ] VHost baseline established if applicable
- [ ] Results saved

## feroxbuster

- [ ] Wordlist selected
- [ ] Recursion understood
- [ ] Depth controlled
- [ ] Filters reviewed
- [ ] Results saved

## Validation

- [ ] High-value results manually requested
- [ ] Random-path baseline compared
- [ ] Redirect destination reviewed
- [ ] Authentication requirement reviewed
- [ ] Authorisation reviewed where relevant
- [ ] Response body reviewed
- [ ] Third-party targets excluded
- [ ] Security consequence established before reporting

## Evidence

- [ ] Tool recorded
- [ ] Version recorded
- [ ] Command recorded
- [ ] Wordlist recorded
- [ ] Filters recorded
- [ ] Authentication context recorded
- [ ] Candidate URL recorded
- [ ] Manual request captured
- [ ] Manual response captured
- [ ] Security interpretation documented

## Retest

- [ ] Exact original resource retested
- [ ] Intended secure response confirmed
- [ ] Equivalent resources considered
- [ ] Legitimate functionality confirmed
- [ ] Evidence captured


# Command Reference

| Objective | Example |
|---|---|
| ffuf basic | `ffuf -w wordlist.txt -u https://example.com/FUZZ` |
| ffuf extensions | `ffuf -w wordlist.txt -u https://example.com/FUZZ -e .php,.html` |
| ffuf filter status | `ffuf -w wordlist.txt -u https://example.com/FUZZ -fc 404` |
| ffuf filter size | `ffuf -w wordlist.txt -u https://example.com/FUZZ -fs 4217` |
| ffuf filter words | `ffuf -w wordlist.txt -u https://example.com/FUZZ -fw 42` |
| ffuf filter lines | `ffuf -w wordlist.txt -u https://example.com/FUZZ -fl 15` |
| ffuf auto-calibration | `ffuf -w wordlist.txt -u https://example.com/FUZZ -ac` |
| ffuf recursion | `ffuf -w wordlist.txt -u https://example.com/FUZZ -recursion` |
| ffuf recursion depth | `ffuf -w wordlist.txt -u https://example.com/FUZZ -recursion -recursion-depth 2` |
| ffuf header | `ffuf -w wordlist.txt -u https://example.com/FUZZ -H "X-Test: value"` |
| ffuf VHost | `ffuf -w hosts.txt -u https://example.com/ -H "Host: FUZZ.example.com"` |
| ffuf save JSON | `ffuf -w wordlist.txt -u https://example.com/FUZZ -o results.json -of json` |
| Gobuster dir | `gobuster dir -u https://example.com/ -w wordlist.txt` |
| Gobuster extensions | `gobuster dir -u https://example.com/ -w wordlist.txt -x php,html` |
| Gobuster VHost | `gobuster vhost -u https://example.com/ -w hosts.txt --append-domain` |
| Gobuster output | `gobuster dir -u https://example.com/ -w wordlist.txt -o results.txt` |
| feroxbuster basic | `feroxbuster -u https://example.com/` |
| feroxbuster wordlist | `feroxbuster -u https://example.com/ -w wordlist.txt` |
| feroxbuster extensions | `feroxbuster -u https://example.com/ -x php,html,txt` |


# Final Testing Principle

Content discovery is **attack-surface discovery**, not vulnerability confirmation.

Do not stop at:

```text
Wordlist
   |
   v
Tool
   |
   v
/admin Found
   |
   v
Finding
```

Use:

```text
Wordlist
   |
   v
Discovery Tool
   |
   v
Candidate
   |
   v
Compare With Baseline
   |
   v
Manual Request
   |
   v
Understand Function
   |
   v
Authentication?
   |
   v
Authorisation?
   |
   v
Sensitive Information?
   |
   v
Security Consequence?
   |
   +--> No  -> Attack-Surface Note
   |
   +--> Yes -> Validate -> Evidence -> Finding
```

For every interesting result ask:

```text
Does the path actually exist?

How does it differ from a random path?

Is this a soft 404?

Is the response unique?

What does the resource do?

Is authentication required?

Is authorisation enforced?

Does the resource expose sensitive information?

Is the functionality intended to be public?

Is this host actually in scope?

Could the response be a wildcard?

Could the result be caused by a generic redirect?

Can I reproduce it manually?

What security consequence exists?
```

The tool should help answer:

```text
WHAT EXISTS?
```

Manual testing should then answer:

```text
DOES IT MATTER?
```


# Related Cheatsheets

- [Burp Suite Cheatsheet](burp-suite.md)
- [Web Application Security Cheatsheet](web.md)
- [curl Cheatsheet](curl.md)
- [Nmap Cheatsheet](nmap.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)
- [Networking Cheatsheet](networking.md)


# Related Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [Reconnaissance](../web/reconnaissance/index.md)
- [Content Discovery](../web/reconnaissance/content-discovery.md)
- [Parameter Discovery](../web/reconnaissance/parameter-discovery.md)
- [JavaScript Analysis](../web/reconnaissance/javascript-analysis.md)
- [Technology Identification](../web/reconnaissance/technology-identification.md)
- [Authentication](../web/authentication.md)
- [Authorisation](../web/authorisation.md)
- [API Security](../web/api-security.md)
- [GraphQL](../web/graphql.md)


# References

- [ffuf GitHub Repository](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }
- [Gobuster GitHub Repository](https://github.com/OJ/gobuster){ target="_blank" rel="noopener noreferrer" }
- [feroxbuster Documentation](https://epi052.github.io/feroxbuster-docs/){ target="_blank" rel="noopener noreferrer" }
- [feroxbuster GitHub Repository](https://github.com/epi052/feroxbuster){ target="_blank" rel="noopener noreferrer" }
- [SecLists GitHub Repository](https://github.com/danielmiessler/SecLists){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger - Content Discovery](https://portswigger.net/web-security/learning-paths/server-side-vulnerabilities-apprentice/content-discovery-apprentice){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Baseline before filtering"

    Request a random nonexistent resource before starting enumeration. Knowing how the application responds to nonexistent content makes status, size, word and line filters much more reliable.


!!! tip "Use discovery to build the attack surface"

    `/admin`, `/api`, `/debug` or `/swagger` are not vulnerabilities simply because a discovery tool finds them. Move interesting resources into Burp Repeater or curl and determine what they actually expose.


!!! tip "Targeted discovery beats blind volume"

    Information from JavaScript, application terminology, observed routes and technology identification can produce much better wordlists than immediately sending hundreds of thousands of generic requests.


!!! warning "Control recursion"

    Recursive discovery can increase request volume extremely quickly. Limit depth and prioritise security-relevant branches of the application rather than recursively enumerating every static directory.


!!! warning "Do not discard every 403"

    A `403 Forbidden` response can be valuable attack-surface information because it may indicate that the server handles a path differently from a nonexistent resource. Validate it manually before deciding whether it is relevant.
