# Web Pentesting Cheatsheet

Quick-reference methodology, commands, tools and checks for authorised web application penetration testing, vulnerability research and bug bounty assessments.

This cheatsheet is intended to answer:

```text
What is the target?
      |
      v
What technology is running?
      |
      v
What content exists?
      |
      v
Where does input enter?
      |
      v
How is authentication enforced?
      |
      v
How is authorisation enforced?
      |
      v
Can server-side behaviour be influenced?
      |
      v
Can client-side behaviour be influenced?
      |
      v
What security impact can be demonstrated?
```

!!! warning "Authorised testing only"
    Use these techniques only against applications and infrastructure you own or are explicitly authorised to assess. Respect the defined scope, rate limits, excluded functionality, data-handling requirements and rules of engagement.

---

# Quick Start

For a new web target:

```bash
export TARGET="https://example.com"
export DOMAIN="example.com"
```

Initial response:

```bash
curl -skI "$TARGET"
```

Technology fingerprinting:

```bash
whatweb "$TARGET"
```

More detailed WhatWeb fingerprinting:

```bash
whatweb -a 3 "$TARGET"
```

Nmap:

```bash
nmap -Pn -sV -p 80,443 "$DOMAIN"
```

HTTP probing:

```bash
echo "$DOMAIN" | httpx -silent -status-code -title -tech-detect
```

Common files:

```bash
curl -sk "$TARGET/robots.txt"
curl -sk "$TARGET/sitemap.xml"
curl -sk "$TARGET/.well-known/security.txt"
```

Response headers:

```bash
curl -skI "$TARGET"
```

TLS:

```bash
openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN"
```

The first goal is not exploitation.

The first goal is understanding the application.

---

# Methodology

```text
Scope
  |
  v
Asset Discovery
  |
  v
Technology Identification
  |
  v
HTTP / TLS Analysis
  |
  v
Content Discovery
  |
  v
Crawling
  |
  v
Parameter Discovery
  |
  v
JavaScript Analysis
  |
  v
Authentication
  |
  v
Authorisation
  |
  v
Input Handling
  |
  v
Server-Side Testing
  |
  v
Client-Side Testing
  |
  v
Business Logic
  |
  v
API Testing
  |
  v
Evidence
  |
  v
Reporting
```

For every discovered:

```text
Domain
Subdomain
Virtual Host
Application
API
Administrative Interface
```

restart the relevant portions of the methodology.

---

# Scope First

Before testing record:

```text
Domains
Subdomains
IP Addresses
Applications
APIs
Authentication Contexts
Test Accounts
Allowed Techniques
Excluded Techniques
Rate Limits
Testing Window
Data Restrictions
```

Do not assume:

```text
*.example.com
```

is in scope because:

```text
example.com
```

is in scope.

---

# Target Variables

Useful Bash variables:

```bash
export TARGET="https://example.com"
export DOMAIN="example.com"
```

Check:

```bash
echo "$TARGET"
echo "$DOMAIN"
```

---

# DNS

A record:

```bash
dig A "$DOMAIN"
```

AAAA:

```bash
dig AAAA "$DOMAIN"
```

Name servers:

```bash
dig NS "$DOMAIN"
```

Mail:

```bash
dig MX "$DOMAIN"
```

TXT:

```bash
dig TXT "$DOMAIN"
```

Short:

```bash
dig +short "$DOMAIN"
```

---

# Reverse DNS

```bash
dig -x 192.0.2.10
```

---

# DNS Zone Transfer

Where explicitly authorised:

```bash
dig AXFR example.com @ns1.example.com
```

A successful unauthorised zone transfer may expose:

```text
Hosts
Subdomains
Infrastructure
Mail Systems
Internal Naming
Service Records
```

---

# Subdomain Enumeration

Subfinder:

```bash
subfinder -d example.com -silent
```

Save:

```bash
subfinder -d example.com -silent -o subdomains.txt
```

---

# Probe Discovered Web Services

```bash
httpx -l subdomains.txt -silent
```

Useful metadata:

```bash
httpx -l subdomains.txt \
    -silent \
    -status-code \
    -title \
    -tech-detect
```

Save:

```bash
httpx -l subdomains.txt \
    -silent \
    -status-code \
    -title \
    -tech-detect \
    -o alive.txt
```

Remember:

```text
httpx Responsive
      =
HTTP/HTTPS Service Responsive
```

not necessarily:

```text
Host Alive for Every Protocol
```

---

# Technology Identification

Technology identification should happen early.

Look for:

```text
Web Server
Framework
Programming Language
CMS
JavaScript Framework
Reverse Proxy
CDN
WAF
Analytics
Authentication Platform
API Gateway
Hosting Platform
Version Information
```

Useful tools:

```text
WhatWeb
Wappalyzer
httpx
curl
Browser Developer Tools
Burp Suite
Nmap
Manual Response Inspection
404 Fingerprinting
```

---

# WhatWeb

WhatWeb fingerprints technologies exposed by web applications.

Basic:

```bash
whatweb https://example.com
```

Aggression level:

```bash
whatweb -a 3 https://example.com
```

More aggressive:

```bash
whatweb -a 4 https://example.com
```

Use higher aggression levels only when appropriate for the assessment.

Multiple targets:

```bash
whatweb https://example.com https://www.example.com
```

Input file:

```bash
whatweb -i targets.txt
```

JSON output:

```bash
whatweb --log-json=whatweb.json https://example.com
```

Verbose:

```bash
whatweb -v https://example.com
```

List plugins:

```bash
whatweb -l
```

Search plugins:

```bash
whatweb -l | grep -i wordpress
```

Technology fingerprinting is evidence, not proof.

For example:

```text
WhatWeb says Apache
        |
        v
Confirm Headers
        |
        v
Confirm Behaviour
        |
        v
Check Other Fingerprints
```

Do not report a vulnerability solely because a fingerprinting tool identifies a technology or version.

---

# Wappalyzer

Wappalyzer can identify technologies from public website signals such as:

```text
HTML
JavaScript
Headers
Cookies
Framework Patterns
CMS Patterns
Analytics Tags
Infrastructure Indicators
```

Useful categories include:

```text
CMS
Web Framework
JavaScript Framework
Web Server
Reverse Proxy
CDN
Analytics
Tag Manager
E-commerce Platform
Authentication Technology
Programming Language
```

Use the browser extension or Wappalyzer technology lookup during manual reconnaissance.

Technology lookup:

[Wappalyzer - Technology Lookup](https://www.wappalyzer.com/lookup/){ target="_blank" rel="noopener noreferrer" }

Do not assume every identified version is exact.

Use multiple signals.

---

# Technology Validation

Use several sources:

```text
WhatWeb
   |
   +--> Fingerprints

Wappalyzer
   |
   +--> Browser / Public Signals

httpx
   |
   +--> HTTP Metadata

Headers
   |
   +--> Server / Framework Clues

Cookies
   |
   +--> Framework Clues

404 Pages
   |
   +--> Framework Fingerprints

HTML / JavaScript
   |
   +--> Application Stack
```

Then correlate.

---

# 404 Fingerprinting

A default error page can reveal the underlying technology.

Request a random path:

```bash
curl -sk https://example.com/this-path-should-not-exist-839274
```

Headers:

```bash
curl -skI https://example.com/this-path-should-not-exist-839274
```

Save response:

```bash
curl -sk https://example.com/this-path-should-not-exist-839274 \
    -o 404.html
```

Look for:

```text
Framework-specific templates
Server signatures
Error formatting
Default text
Generated HTML structure
Headers
Cookies
Debug information
Stack traces
```

Possible technologies that can expose recognisable default error behaviour include:

```text
Apache
nginx
IIS
Tomcat
Jetty
Express
Django
Flask
ASP.NET
Spring
Rails
PHP frameworks
```

Do not identify technology from the HTTP status alone.

Use the content and behaviour of the response.

---

# 0xdf Default 404 Reference

0xdf maintains a useful reference showing default 404 pages from different technologies.

This can help correlate:

```text
Unknown Application
       |
       v
Random Invalid Path
       |
       v
Default Error Response
       |
       v
Compare Fingerprint
       |
       v
Technology Hypothesis
       |
       v
Validate Using Other Evidence
```

Reference:

[0xdf - Cheatsheets](https://0xdf.gitlab.io/cheatsheets/){ target="_blank" rel="noopener noreferrer" }

Use the **Default 404 Pages** reference from the Enumeration section.

Do not treat visual similarity as definitive proof.

---

# Manual Fingerprinting

Response:

```bash
curl -sk -D - https://example.com/ -o /dev/null
```

Look for:

```text
Server
X-Powered-By
Via
X-AspNet-Version
X-Generator
Set-Cookie
X-Cache
X-Varnish
CF-Ray
```

Headers can be removed, changed or spoofed.

---

# HTTP Status Codes

Common:

| Code | Meaning |
|---:|---|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 301 | Permanent Redirect |
| 302 | Temporary Redirect |
| 303 | See Other |
| 307 | Temporary Redirect |
| 308 | Permanent Redirect |
| 400 | Bad Request |
| 401 | Unauthenticated |
| 403 | Forbidden |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 409 | Conflict |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 502 | Bad Gateway |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

Do not interpret:

```text
403
```

as:

```text
Resource Does Not Exist
```

A 403 can reveal that routing or authorisation reached a real resource.

---

# curl

Basic:

```bash
curl https://example.com/
```

Headers:

```bash
curl -I https://example.com/
```

Verbose:

```bash
curl -v https://example.com/
```

Follow redirects:

```bash
curl -L https://example.com/
```

Include response headers:

```bash
curl -i https://example.com/
```

Save response:

```bash
curl -o response.html https://example.com/
```

---

# Ignore TLS Validation

For authorised testing of systems with expected certificate problems:

```bash
curl -k https://example.com/
```

Do not use `-k` when the objective is to validate certificate trust.

---

# Custom Header

```bash
curl -H 'X-Test: value' https://example.com/
```

Multiple:

```bash
curl \
    -H 'X-Test: value' \
    -H 'Accept: application/json' \
    https://example.com/
```

---

# User-Agent

```bash
curl -A 'Mozilla/5.0' https://example.com/
```

---

# Cookie

```bash
curl -b 'session=value' https://example.com/
```

Cookie jar:

```bash
curl -c cookies.txt https://example.com/
```

Reuse:

```bash
curl -b cookies.txt https://example.com/account
```

Treat session cookies as credentials.

---

# POST Form

```bash
curl \
    -X POST \
    -d 'username=test&password=test' \
    https://example.com/login
```

Only perform authentication testing according to the rules of engagement.

---

# POST JSON

```bash
curl \
    -X POST \
    -H 'Content-Type: application/json' \
    -d '{"name":"test"}' \
    https://example.com/api/example
```

---

# PUT

Where authorised:

```bash
curl \
    -X PUT \
    -H 'Content-Type: application/json' \
    -d '{"name":"test"}' \
    https://example.com/api/example/1
```

---

# DELETE

Do not issue state-changing DELETE requests against real production records merely to test method support.

Prefer:

```text
Disposable Test Record
Dedicated Test Account
Non-production Environment
```

where possible.

---

# OPTIONS

```bash
curl -i -X OPTIONS https://example.com/
```

This may reveal supported HTTP methods.

It is not guaranteed to represent every method accepted by application routing.

---

# TRACE

Check only if explicitly required:

```bash
curl -i -X TRACE https://example.com/
```

Do not report TRACE solely because the server responds unless meaningful security impact exists.

---

# HTTP Headers

Inspect:

```bash
curl -skI https://example.com/
```

Review:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
Cross-Origin-Opener-Policy
Cross-Origin-Resource-Policy
Cache-Control
Set-Cookie
Access-Control-Allow-Origin
```

Also investigate information-disclosure headers:

```text
Server
X-Powered-By
Via
X-Backend
X-Generator
```

---

# Security Headers

Useful manual check:

```bash
curl -skI https://example.com/
```

Security headers are defence-in-depth.

Missing headers should be evaluated in context.

For example:

```text
Missing CSP
```

does not itself prove XSS.

---

# Cookies

Inspect:

```bash
curl -skI https://example.com/
```

Look for:

```text
Secure
HttpOnly
SameSite
Domain
Path
Expires
Max-Age
```

Important:

```text
Cookie Attribute Missing
        |
        v
Determine Cookie Purpose
        |
        v
Determine Attack Scenario
        |
        v
Assess Impact
```

---

# TLS

```bash
openssl s_client \
    -connect example.com:443 \
    -servername example.com
```

Certificate:

```bash
openssl s_client \
    -connect example.com:443 \
    -servername example.com \
    </dev/null 2>/dev/null |
    openssl x509 -noout -subject -issuer -dates
```

SAN:

```bash
openssl s_client \
    -connect example.com:443 \
    -servername example.com \
    </dev/null 2>/dev/null |
    openssl x509 -noout -ext subjectAltName
```

---

# Nmap Web Enumeration

```bash
nmap -Pn -sV -p 80,443 example.com
```

Default scripts:

```bash
nmap -Pn -sC -sV -p 80,443 example.com
```

HTTP title:

```bash
nmap -p 80,443 --script http-title example.com
```

Headers:

```bash
nmap -p 80,443 --script http-headers example.com
```

Methods:

```bash
nmap -p 80,443 --script http-methods example.com
```

Review NSE script behaviour before using it.

---

# robots.txt

```bash
curl -sk https://example.com/robots.txt
```

Look for:

```text
Administrative Paths
Internal Paths
Staging Content
Uploads
Backups
API Paths
Disallowed Directories
```

`Disallow` is not access control.

---

# sitemap.xml

```bash
curl -sk https://example.com/sitemap.xml
```

Potential discoveries:

```text
Hidden Content
Legacy Paths
Product IDs
Language Paths
API Documentation
Unlinked Pages
```

---

# security.txt

```bash
curl -sk https://example.com/.well-known/security.txt
```

Useful for identifying:

```text
Security Contact
Disclosure Policy
Acknowledgements
Encryption Keys
Canonical Policy
```

---

# Common Interesting Files

Check selectively:

```text
/robots.txt
/sitemap.xml
/.well-known/security.txt
/favicon.ico
/manifest.json
/asset-manifest.json
/openapi.json
/swagger.json
/api-docs
/swagger
/swagger-ui/
/graphql
/graphiql
```

Do not blindly request sensitive files outside scope.

---

# Content Discovery

Useful tools:

```text
ffuf
feroxbuster
gobuster
dirsearch
Burp Suite
Katana
```

---

# ffuf

Basic:

```bash
ffuf \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -u https://example.com/FUZZ
```

Extensions:

```bash
ffuf \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -u https://example.com/FUZZ \
    -e .php,.html,.txt,.json
```

Status filtering:

```bash
ffuf \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -u https://example.com/FUZZ \
    -mc 200,204,301,302,307,401,403
```

---

# ffuf Auto Calibration

```bash
ffuf \
    -ac \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -u https://example.com/FUZZ
```

Useful when applications return soft 404 responses.

---

# Soft 404

Some applications return:

```text
HTTP 200
```

for nonexistent resources.

Example:

```text
GET /this-definitely-does-not-exist
HTTP/1.1 200 OK

Page Not Found
```

Therefore filtering only by status code can produce large numbers of false positives.

Compare:

```text
Status
Length
Words
Lines
Title
Body Fingerprint
Redirect
```

---

# Establish Baseline 404

```bash
curl -sk \
    -o /tmp/notfound \
    -w 'status=%{http_code} size=%{size_download}\n' \
    https://example.com/random-invalid-path-739281
```

This helps determine the application's normal nonexistent-page behaviour.

---

# feroxbuster

Basic:

```bash
feroxbuster \
    -u https://example.com \
    -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Extensions:

```bash
feroxbuster \
    -u https://example.com \
    -x php,html,txt,json
```

Use recursion and concurrency appropriate to the target.

---

# Gobuster

```bash
gobuster dir \
    -u https://example.com \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

Extensions:

```bash
gobuster dir \
    -u https://example.com \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -x php,html,txt
```

---

# Wordlists

SecLists:

```text
/usr/share/seclists/
```

Common web content:

```text
/usr/share/seclists/Discovery/Web-Content/
```

Useful categories:

```text
Common
Raft
Apache
IIS
API
CMS
Backup Files
Parameters
```

Choose wordlists based on technology and context.

---

# Technology-Specific Discovery

After fingerprinting:

```text
WordPress
   |
   +--> WordPress-specific content

IIS / ASP.NET
   |
   +--> ASPX / config conventions

PHP
   |
   +--> PHP extensions

Java
   |
   +--> JSP / servlet conventions

API
   |
   +--> API wordlists

Framework
   |
   +--> Framework-specific routes
```

This is more efficient than blindly using one giant wordlist.

---

# Virtual Host Discovery

Where the target architecture and scope allow it:

```bash
ffuf \
    -w subdomains.txt \
    -u https://192.0.2.10/ \
    -H 'Host: FUZZ.example.com'
```

Filter the baseline/default response.

Verify discovered virtual hosts are within scope before deeper testing.

---

# Crawling

Useful tools:

```text
Katana
Burp Suite
hakrawler
gau
waybackurls
Browser
```

---

# Katana

```bash
katana -u https://example.com
```

Save:

```bash
katana -u https://example.com -o katana.txt
```

JavaScript crawling:

```bash
katana -u https://example.com -jc
```

Crawling can discover:

```text
Endpoints
Parameters
JavaScript
Forms
API Calls
Static Assets
Hidden Routes
```

---

# Historical URLs

Where permitted:

```bash
echo example.com | gau
```

Save:

```bash
echo example.com | gau > gau.txt
```

Wayback:

```bash
echo example.com | waybackurls
```

Historical URLs can reveal:

```text
Old Endpoints
Removed Parameters
Legacy APIs
Backup Paths
Previous Technologies
```

Historical presence does not prove current reachability.

---

# URL Deduplication

```bash
sort -u urls.txt > urls-unique.txt
```

---

# Extract URLs from HTML

Simple:

```bash
curl -sk https://example.com/ |
    grep -Eo 'https?://[^" ]+'
```

For comprehensive crawling, use a crawler rather than regex alone.

---

# Parameter Discovery

Look for parameters in:

```text
GET
POST
JSON
XML
Headers
Cookies
Path Segments
GraphQL Variables
Multipart Forms
WebSocket Messages
```

---

# Extract Parameterised URLs

```bash
grep '?' urls.txt
```

Unique:

```bash
grep '?' urls.txt | sort -u
```

---

# ParamSpider

Typical use:

```bash
python3 paramspider.py -d example.com
```

Review the installed version's documentation because command-line options can change.

Historical URLs can generate false positives and dead endpoints.

Validate before testing.

---

# Arjun

Parameter discovery:

```bash
arjun -u https://example.com/endpoint
```

GET:

```bash
arjun -u https://example.com/endpoint -m GET
```

POST:

```bash
arjun -u https://example.com/endpoint -m POST
```

Do not generate excessive traffic against production endpoints.

---

# JavaScript Discovery

Find JavaScript URLs:

```bash
grep -Ei '\.js([?#].*)?$' urls.txt
```

Crawl:

```bash
katana -u https://example.com -jc
```

---

# Download JavaScript

```bash
curl -sk https://example.com/assets/app.js -o app.js
```

Search:

```bash
grep -Ein \
    'api|token|secret|key|password|admin|internal|graphql|swagger' \
    app.js
```

Treat matches as leads, not findings.

---

# JavaScript Review

Look for:

```text
API Endpoints
Hidden Routes
WebSocket URLs
GraphQL Endpoints
Feature Flags
Internal Hostnames
Source Maps
Cloud Storage
Authentication Logic
Client-side Roles
Debug Functions
Hardcoded Credentials
Secrets
Third-party Integrations
```

---

# Source Maps

Look for:

```text
.js.map
```

Example:

```bash
curl -skI https://example.com/assets/app.js.map
```

Source maps can expose original source structure and developer comments.

Do not report source maps solely because they exist.

Assess what they disclose.

---

# Browser Developer Tools

Use:

```text
Network
Sources
Application
Storage
Cookies
Console
DOM Inspector
Security
```

Important questions:

```text
Which APIs are called?
Which parameters are sent?
Which tokens are stored?
Which routes exist?
Which JavaScript files load?
Which cookies change?
What happens when roles change?
```

---

# Burp Suite

Core workflow:

```text
Browser
   |
   v
Proxy
   |
   v
HTTP History
   |
   +--> Repeater
   +--> Intruder
   +--> Decoder
   +--> Comparer
   +--> Sequencer
```

Burp Suite should be central to manual web testing.

---

# Burp Proxy

Use Proxy to:

```text
Capture Requests
Inspect Responses
Map Application
Understand Authentication
Identify Parameters
Observe API Calls
```

---

# Burp Repeater

Use Repeater for:

```text
Parameter Modification
Authorisation Testing
Input Validation
Header Testing
Cookie Testing
API Testing
Response Comparison
```

Repeater is usually preferable to repeatedly modifying requests through the browser.

---

# Burp Intruder

Useful for:

```text
Controlled Enumeration
Parameter Testing
ID Enumeration
Content Discovery
Small Targeted Payload Sets
```

Respect rate limits and avoid account lockouts.

---

# Burp Decoder

Useful for:

```text
URL Encoding
Base64
Hex
HTML Encoding
```

---

# Burp Comparer

Useful for comparing:

```text
Admin vs User
Authenticated vs Unauthenticated
Valid vs Invalid ID
Original vs Modified Request
```

---

# Useful Burp Extensions

Depending on the target:

```text
Logger++
Autorize
AuthMatrix
JWT Editor
JSON Web Tokens
HTTP Request Smuggler
Param Miner
Turbo Intruder
Collaborator Everywhere
Backslash Powered Scanner
JS Link Finder
Software Vulnerability Scanner
GraphQL Raider
Content Type Converter
Upload Scanner
```

Review extension permissions and source before installing third-party extensions.

---

# Authentication

Test:

```text
Registration
Login
Logout
Password Reset
Password Change
MFA
Remember Me
Session Creation
Session Rotation
Session Expiration
Account Recovery
Email Change
Username Change
Device Trust
SSO
OAuth / OIDC
```

---

# Authentication Matrix

Create:

| Function | Anonymous | User A | User B | Admin |
|---|---|---|---|---|
| View profile | No | Own | Own | Any |
| Edit profile | No | Own | Own | Any |
| View invoice | No | Own | Own | Any |
| Admin panel | No | No | No | Yes |

Then validate each security boundary.

---

# Username Enumeration

Compare:

```text
Valid Username + Wrong Password
Invalid Username + Wrong Password
```

Look for differences in:

```text
Status
Body
Length
Headers
Timing
Workflow
Lockout Behaviour
```

Do not perform high-volume username enumeration unless authorised.

---

# Password Reset

Check:

```text
Token Entropy
Token Expiry
Single Use
Account Binding
Host Header Handling
Rate Limiting
User Enumeration
Session Invalidation
Password Policy
MFA Interaction
```

---

# MFA

Check:

```text
Is MFA required for every login path?
Can recovery bypass MFA?
Can remembered devices bypass policy?
Is MFA required for sensitive changes?
Are backup codes protected?
Is step-up authentication enforced?
```

Avoid destructive lockout testing.

---

# Session Management

Check:

```text
Session Cookie Attributes
Rotation After Login
Rotation After Privilege Change
Logout Invalidation
Timeout
Concurrent Sessions
Password Change Invalidation
Password Reset Invalidation
Server-Side Revocation
```

---

# Session Fixation

Compare the session identifier:

```text
Before Login
    |
    v
Authentication
    |
    v
After Login
```

A sensitive session identifier should generally rotate when authentication state changes.

---

# Authorisation

Test horizontally:

```text
User A
  |
  v
Object A

User B
  |
  X
  |
Object A
```

Test vertically:

```text
Normal User
    |
    X
    |
Admin Function
```

---

# IDOR / BOLA

Example pattern:

```text
GET /api/invoices/1001
```

Do not immediately brute-force IDs.

Use controlled objects created by authorised test accounts.

Example:

```text
User A -> Object A
User B -> Object B
```

Test whether:

```text
User A -> Object B
```

is incorrectly allowed.

---

# Authorisation Testing Model

```text
Identity
   |
   v
Role
   |
   v
Action
   |
   v
Object
   |
   v
Expected Decision
   |
   v
Actual Decision
```

---

# HTTP Method Authorisation

If:

```text
GET /admin/user/10
```

is denied, also consider whether the same function is exposed through:

```text
POST
PUT
PATCH
DELETE
API Endpoint
Alternate Route
```

Only use state-changing requests on disposable test data where possible.

---

# Business Logic

Business logic vulnerabilities often require understanding the application rather than payloads.

Look for:

```text
Workflow Skipping
State Manipulation
Price Manipulation
Quantity Manipulation
Negative Values
Duplicate Actions
Race Conditions
Coupon Reuse
Approval Bypass
Limit Bypass
Role Workflow Errors
Order Manipulation
Trust in Client-side Values
```

---

# Business Logic Workflow

```text
Understand Normal Workflow
        |
        v
Identify Assumptions
        |
        v
Modify Sequence
        |
        v
Modify Values
        |
        v
Repeat Actions
        |
        v
Compare Server Behaviour
```

---

# Input Mapping

For every input determine:

```text
Source
 |
 v
Validation
 |
 v
Transformation
 |
 v
Sink
```

Sources include:

```text
Query Parameters
POST Fields
JSON
XML
Headers
Cookies
Path Values
Uploaded Files
WebSocket Messages
GraphQL Variables
```

---

# XSS

Contexts:

```text
HTML
Attribute
JavaScript
URL
CSS
DOM
```

The correct test depends on context.

---

# Basic XSS Marker

Start with a harmless unique marker:

```text
xsstest839274
```

Determine:

```text
Is it reflected?
Where?
How is it encoded?
What context?
```

Then select context-appropriate testing.

Do not jump directly to complex payloads.

---

# Reflected XSS Flow

```text
Input
 |
 v
Reflection
 |
 v
HTML Context
 |
 v
Encoding
 |
 v
Execution Possible?
```

---

# Stored XSS

Determine:

```text
Where is input stored?
Who views it?
What privilege does the viewer have?
Which page renders it?
Is output encoding applied?
```

Stored XSS affecting privileged users can have significantly greater impact.

---

# DOM XSS

Review sources:

```text
location
location.hash
location.search
document.URL
document.referrer
postMessage
localStorage
sessionStorage
```

Potential sinks include unsafe DOM-writing or code-execution functions.

Use browser developer tools and dedicated DOM analysis rather than relying only on server responses.

---

# XSS Resources

[PortSwigger - Cross-site scripting](https://portswigger.net/web-security/cross-site-scripting){ target="_blank" rel="noopener noreferrer" }

[PortSwigger - XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet){ target="_blank" rel="noopener noreferrer" }

[OWASP - XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

# SQL Injection

Start by identifying:

```text
Parameter
   |
   v
Database Interaction?
   |
   v
Response Difference?
   |
   v
Error?
   |
   v
Boolean Difference?
   |
   v
Timing Difference?
```

Avoid immediately extracting database contents.

Prove the vulnerability with minimal impact.

---

# SQL Injection Indicators

Look for:

```text
Database Errors
Different Response Length
Different Status
Different Records
Timing Differences
Unexpected Application Errors
```

---

# SQLmap

For authorised testing:

```bash
sqlmap -u 'https://example.com/item?id=1'
```

Use a captured request:

```bash
sqlmap -r request.txt
```

Specify parameter:

```bash
sqlmap -r request.txt -p id
```

Do not immediately use:

```text
--dump
--os-shell
--file-read
```

unless explicitly required by the assessment.

A minimal proof is usually preferable.

---

# Command Injection

Identify inputs reaching:

```text
Operating System Commands
Shell Scripts
System Utilities
Image Processing
Archive Tools
Network Utilities
Document Conversion
```

Start with non-destructive validation.

Do not use destructive commands or establish shells merely to prove command execution.

---

# Commix

Project:

[commixproject/commix](https://github.com/commixproject/commix){ target="_blank" rel="noopener noreferrer" }

Use only where command-injection testing is explicitly authorised.

---

# Path Traversal

Potential inputs:

```text
file=
path=
page=
template=
download=
document=
folder=
```

Determine:

```text
User Input
   |
   v
Path Construction
   |
   v
Canonicalisation
   |
   v
Allowed Directory?
```

Use harmless known files appropriate to the target environment.

---

# File Inclusion

Distinguish:

```text
Path Traversal
Local File Inclusion
Remote File Inclusion
Template Inclusion
```

Do not assume traversal automatically means code execution.

---

# File Upload

Review:

```text
Extension
Content-Type
Magic Bytes
Filename
Storage Location
Execution
Retrieval
Authorisation
Malware Scanning
Image Processing
Archive Handling
Metadata
```

---

# Upload Testing Flow

```text
Upload
  |
  v
Validation
  |
  v
Storage
  |
  v
Retrieval
  |
  v
Interpretation
```

A secure upload can still store attacker-controlled content safely.

The key question is how the server processes and serves it.

---

# Harmless Upload Validation

Use:

```text
Plain Text
Small Images
Controlled PDFs
EICAR only where explicitly permitted
```

Avoid uploading active malware to production systems.

---

# SSRF

Potential parameters:

```text
url=
uri=
endpoint=
callback=
webhook=
image=
feed=
proxy=
redirect=
next=
```

Look for functionality that causes the server to retrieve another resource.

---

# SSRF Flow

```text
User-Controlled URL
        |
        v
Server Request
        |
        v
Destination Control
        |
        v
Internal / External Reachability
```

Use controlled infrastructure when proving outbound requests.

Do not target unrelated internal services merely to demonstrate SSRF.

---

# SSTI

Potential locations:

```text
Email Templates
PDF Generation
CMS Templates
Notification Templates
User Profile Rendering
Custom Themes
Server-side Rendering
```

Begin with harmless arithmetic or rendering differences appropriate to the suspected template engine.

Do not jump directly to command execution.

---

# XXE

Relevant where the application parses XML.

Review:

```text
Content-Type: application/xml
Content-Type: text/xml
SOAP
SVG
Office Formats
XML Uploads
```

Determine parser behaviour using safe controlled entities before attempting file access or network callbacks.

---

# Deserialization

Potential indicators:

```text
Serialized Cookies
Binary Blobs
Base64 Objects
Java Serialization
.NET Serialization
PHP Serialization
Signed State Objects
```

Do not assume encoded data is serialized object data.

---

# CORS

Inspect:

```bash
curl -skI \
    -H 'Origin: https://example.org' \
    https://example.com/
```

Look for:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Access-Control-Allow-Methods
Access-Control-Allow-Headers
```

CORS findings require a realistic browser-based data-access scenario.

---

# CSRF

Review state-changing actions:

```text
Password Change
Email Change
Profile Update
Payment
Account Linking
Administrative Actions
API Key Creation
```

Determine:

```text
Is authentication cookie-based?
Is SameSite protective?
Is there an anti-CSRF token?
Is Origin/Referer checked?
Can an attacker construct the request?
```

---

# Clickjacking

Review:

```text
Content-Security-Policy: frame-ancestors
X-Frame-Options
```

Not every page requires framing protection.

Focus on sensitive interactive functionality.

---

# Open Redirect

Common parameters:

```text
url=
redirect=
redirect_uri=
next=
return=
returnUrl=
continue=
destination=
```

Assess impact in context:

```text
Phishing
OAuth
SSO
Token Leakage
Trusted-domain Abuse
```

An arbitrary redirect alone may be low severity.

---

# Host Header

Test carefully with Burp Repeater.

Potential areas:

```text
Password Reset URLs
Absolute URL Generation
Cache Keys
Routing
Virtual Hosts
Security Links
```

Do not send password-reset emails to real users.

Use dedicated test accounts.

---

# HTTP Request Smuggling

Relevant when:

```text
Front End
   |
   v
Back End
```

interpret HTTP request boundaries differently.

Use:

```text
Burp HTTP Request Smuggler
```

Request smuggling testing can disrupt production services.

Use only when explicitly authorised and with appropriate precautions.

---

# Cache Poisoning

Review:

```text
Cache Key
Unkeyed Headers
Query Parameters
Host
Path
Content Negotiation
CDN Behaviour
```

Use unique markers and avoid poisoning content seen by real users.

---

# Prototype Pollution

Relevant primarily to JavaScript applications and libraries.

Look for unsafe recursive object merge behaviour and attacker-controlled property names.

Test first with harmless properties.

---

# API Testing

Map:

```text
Base URL
Version
Authentication
Endpoints
Methods
Parameters
Objects
Roles
Rate Limits
Documentation
```

---

# OpenAPI / Swagger

Look for:

```text
/openapi.json
/swagger.json
/swagger/
/swagger-ui/
/api-docs
/v1/api-docs
/v2/api-docs
/v3/api-docs
```

Documentation exposure is not automatically a vulnerability.

It may significantly improve attack-surface discovery.

---

# jq

Pretty-print JSON:

```bash
curl -sk https://example.com/api/data | jq
```

Specific property:

```bash
curl -sk https://example.com/api/data |
    jq '.name'
```

---

# API Authorisation

Create a matrix:

| Endpoint | Anonymous | User A | User B | Admin |
|---|---|---|---|---|
| GET /profile | No | Own | Own | Any |
| GET /users/ID | No | Own | Own | Any |
| PUT /users/ID | No | Own | Own | Any |
| DELETE /users/ID | No | No | No | Yes |

---

# GraphQL

Common endpoints:

```text
/graphql
/graphiql
/api/graphql
/v1/graphql
```

Identify GraphQL by:

```text
Content-Type
Request Structure
Errors
JavaScript
Documentation
```

Review:

```text
Authentication
Object Authorisation
Field Authorisation
Introspection
Batching
Aliases
Depth
Complexity
Rate Limits
Error Disclosure
```

---

# GraphQL Burp Extensions

Useful:

```text
GraphQL Raider
InQL
```

Verify compatibility with the current Burp version.

---

# JWT

JWT structure:

```text
HEADER.PAYLOAD.SIGNATURE
```

Decode locally:

```bash
python3 - <<'PY'
import base64
import json

token = "HEADER.PAYLOAD.SIGNATURE"

for part in token.split(".")[:2]:
    part += "=" * (-len(part) % 4)
    print(json.dumps(json.loads(base64.urlsafe_b64decode(part)), indent=2))
PY
```

Decoding is not verification.

---

# JWT Review

Check:

```text
Algorithm
Signature Validation
Issuer
Audience
Expiration
Not Before
Subject
Key Selection
Key Rotation
Claims Authorisation
Token Revocation
```

Do not treat readable JWT claims as information disclosure merely because JWT payloads are Base64URL encoded.

---

# OAuth / OIDC

Map:

```text
Authorization Endpoint
Token Endpoint
Redirect URI
Client ID
Scopes
State
Nonce
PKCE
Issuer
JWKS
UserInfo
```

Common discovery:

```text
/.well-known/openid-configuration
```

Example:

```bash
curl -sk \
    https://example.com/.well-known/openid-configuration |
    jq
```

---

# OAuth Testing

Review:

```text
Redirect URI Validation
State
Nonce
PKCE
Scope Enforcement
Token Audience
Issuer Validation
Account Linking
Open Redirect Interaction
Token Leakage
```

---

# WebSockets

Look for:

```text
ws://
wss://
```

Review:

```text
Authentication
Authorisation
Origin Validation
Message Validation
Object Access
Session Handling
```

Burp Suite can intercept WebSocket messages.

---

# Web Cache

Useful headers:

```text
Age
Cache-Control
Vary
ETag
X-Cache
CF-Cache-Status
Via
```

Determine:

```text
What is cached?
What forms the cache key?
Can user-specific data be cached?
Can unkeyed input affect cached content?
```

---

# Reverse Proxy / CDN

Possible technologies:

```text
Cloudflare
Akamai
Fastly
CloudFront
nginx
HAProxy
Varnish
IIS
Apache
Traefik
```

Use:

```text
Headers
DNS
TLS
WhatWeb
Wappalyzer
httpx
Behaviour
```

for identification.

Do not assume the origin technology based only on edge-server headers.

---

# WAF Identification

Potential tools:

```text
wafw00f
Nmap
WhatWeb
Manual Response Comparison
```

Example:

```bash
wafw00f https://example.com
```

WAF detection is fingerprinting, not proof of protection.

---

# Nikto

For authorised baseline assessment:

```bash
nikto -h https://example.com
```

Nikto can generate substantial traffic and false positives.

Use findings as leads requiring manual validation.

---

# Nuclei

ProjectDiscovery Nuclei can perform template-based checks.

Example:

```bash
nuclei -u https://example.com
```

Restrict severity:

```bash
nuclei \
    -u https://example.com \
    -severity medium,high,critical
```

Before using broad template sets:

```text
Review Scope
Review Templates
Review Rate
Understand Potential Side Effects
```

Automated results require manual validation.

---

# Known Vulnerability Research

After technology identification:

```text
Technology
    |
    v
Version
    |
    v
Deployment Context
    |
    v
Vendor Advisory
    |
    v
CVE
    |
    v
Applicability
    |
    v
Safe Validation
```

Useful sources:

```text
Vendor Advisories
NVD
CISA KEV
GitHub Security Advisories
Exploit-DB
Project Repositories
Security Research
```

Never conclude:

```text
Version String
      =
Vulnerable
```

without validating configuration, patch backports and affected-version conditions.

---

# Searchsploit

```bash
searchsploit nginx
```

Specific technology:

```bash
searchsploit "Apache 2.4"
```

Copy a public reference locally:

```bash
searchsploit -m <ID>
```

Review any public proof of concept before execution.

---

# Error Handling

Trigger only harmless malformed requests.

Look for:

```text
Stack Traces
Framework Names
Source Paths
Database Errors
Internal Hosts
Library Versions
Debug Data
Environment Names
```

Do not intentionally cause resource exhaustion.

---

# Verbose Errors

Potential evidence:

```text
/home/application/
/var/www/
/srv/app/
C:\inetpub\
Framework Version
Database Driver
Internal IP
Internal Hostname
Source File
Line Number
```

Report sensitive disclosure, not merely the existence of an error page.

---

# Backup Files

When a known file exists:

```text
config.php
```

possible backup naming patterns can include:

```text
config.php~
config.php.bak
config.php.old
config.php.save
config.php.orig
```

Test selectively.

Do not brute-force massive backup extension combinations without reason.

---

# Git Exposure

Check:

```bash
curl -skI https://example.com/.git/HEAD
```

A reachable `.git` path requires careful validation.

Do not automatically download an entire repository containing production secrets unless necessary and authorised.

---

# Environment Files

A targeted request may include:

```bash
curl -skI https://example.com/.env
```

Do not broadly download secrets if exposure can be proven safely.

If sensitive credentials are exposed:

```text
Stop
Preserve Minimal Evidence
Do Not Reuse Credentials Without Authorisation
Report Promptly
```

---

# Information Disclosure

Look for:

```text
Internal Hostnames
Internal IP Addresses
Source Paths
Stack Traces
Credentials
Tokens
API Keys
Cloud Keys
Database Names
User Data
Debug Information
Build Information
Repository Metadata
```

Not every version banner is a vulnerability.

---

# Favicon Fingerprinting

Download:

```bash
curl -sk https://example.com/favicon.ico -o favicon.ico
```

Hash:

```bash
sha256sum favicon.ico
```

Favicons can help correlate applications and technologies.

Do not treat a favicon match alone as definitive identification.

---

# Screenshots

For large authorised target sets, screenshots can assist triage.

Useful tools include:

```text
gowitness
EyeWitness
Aquatone
```

Visual review can quickly reveal:

```text
Login Portals
Admin Interfaces
Default Pages
Development Applications
Monitoring Platforms
Duplicate Applications
```

---

# Default Pages

Look for:

```text
Apache Default Page
nginx Default Page
IIS Default Page
Tomcat
Jetty
Application Server Consoles
Framework Welcome Pages
Cloud Default Pages
```

A default page is primarily reconnaissance information unless it exposes additional security impact.

---

# 401 vs 403 vs 404

```text
401
 |
 +--> Authentication required

403
 |
 +--> Request understood but forbidden

404
 |
 +--> Resource not found
      or deliberately hidden
```

Applications may intentionally return 404 for unauthorised resources.

Compare behaviour rather than trusting status codes blindly.

---

# Response Comparison

When testing:

```text
Authentication
Authorisation
Enumeration
Filtering
Input Validation
```

compare:

```text
Status
Length
Words
Lines
Headers
Cookies
Redirect
Body
Timing
```

---

# curl Response Metrics

```bash
curl -sk \
    -o /dev/null \
    -w 'status=%{http_code} size=%{size_download} time=%{time_total}\n' \
    https://example.com/
```

Useful for identifying subtle differences.

---

# Web Recon Workflow

```text
Domain
 |
 v
DNS
 |
 v
Subdomains
 |
 v
HTTP Probe
 |
 v
WhatWeb / Wappalyzer
 |
 v
Headers
 |
 v
404 Fingerprint
 |
 v
robots / sitemap
 |
 v
Crawl
 |
 v
Content Discovery
 |
 v
Parameters
 |
 v
JavaScript
 |
 v
Application Mapping
```

---

# Testing Workflow

After reconnaissance:

```text
Authentication
      |
      v
Session Management
      |
      v
Authorisation
      |
      v
Input Validation
      |
      +--> XSS
      +--> SQLi
      +--> Command Injection
      +--> SSTI
      +--> XXE
      +--> Traversal
      +--> Upload
      +--> SSRF
      |
      v
Business Logic
      |
      v
API
      |
      v
Client Side
```

---

# Tool Map

```text
Technology
 |
 +--> WhatWeb
 +--> Wappalyzer
 +--> httpx

Content
 |
 +--> ffuf
 +--> feroxbuster
 +--> Gobuster

Crawling
 |
 +--> Katana
 +--> Burp
 +--> gau
 +--> waybackurls

Parameters
 |
 +--> Arjun
 +--> ParamSpider

HTTP
 |
 +--> curl
 +--> Burp Repeater

TLS
 |
 +--> OpenSSL
 +--> Nmap

Scanning
 |
 +--> Nmap
 +--> Nuclei
 +--> Nikto

WAF
 |
 +--> wafw00f

SQLi
 |
 +--> Burp
 +--> sqlmap

Command Injection
 |
 +--> Burp
 +--> Commix

JavaScript
 |
 +--> Browser DevTools
 +--> Katana
 +--> grep

Authorisation
 |
 +--> Burp Repeater
 +--> Autorize
 +--> AuthMatrix

JWT
 |
 +--> Burp
 +--> JWT Editor

GraphQL
 |
 +--> Burp
 +--> GraphQL Raider
 +--> InQL
```

---

# Burp Workflow

```text
Proxy
  |
  v
HTTP History
  |
  v
Map Endpoints
  |
  v
Send Interesting Request
  |
  v
Repeater
  |
  +--> Change User
  +--> Change Object
  +--> Change Method
  +--> Change Parameter
  +--> Change Header
  +--> Change Cookie
  |
  v
Compare
```

---

# Evidence

For each finding record:

```text
Target
Endpoint
Method
Parameter
Account
Role
Timestamp
Request
Response
Expected Behaviour
Actual Behaviour
Impact
```

---

# Request Evidence

Capture:

```http
GET /example HTTP/1.1
Host: example.com
```

Redact:

```text
Authorization
Cookie
API Keys
Passwords
Tokens
Personal Data
```

unless the exact value is essential evidence.

---

# Response Evidence

Include only the minimum necessary response.

Avoid copying:

```text
Entire Databases
Large User Lists
Unnecessary Personal Data
Production Secrets
```

into reports.

---

# Proof of Concept Principle

Prefer:

```text
Minimum Action
     |
     v
Maximum Confidence
```

Examples:

```text
Read one controlled object
instead of
dumping every object

Demonstrate harmless command execution
instead of
opening a shell

Demonstrate one controlled callback
instead of
scanning the internal network

Read minimal known file
instead of
collecting credentials
```

---

# Reporting

A good finding contains:

```text
Title
Severity
Affected Asset
Description
Prerequisites
Reproduction
Evidence
Impact
Remediation
References
```

---

# Weak Finding

```text
Server header reveals nginx.
```

Better question:

```text
Does the disclosed information materially enable an attack?
```

---

# Strong Finding

```text
A standard authenticated user can modify the object identifier
in GET /api/invoices/{id} and retrieve invoices belonging to
other users because the server does not perform object-level
authorisation.
```

This demonstrates:

```text
Principal
   |
   v
Action
   |
   v
Security Boundary
   |
   v
Impact
```

---

# Web Assessment Checklist

## Scope

- [ ] Confirm domains
- [ ] Confirm subdomains
- [ ] Confirm IPs
- [ ] Confirm test accounts
- [ ] Confirm excluded functionality
- [ ] Confirm rate limits
- [ ] Confirm destructive testing restrictions

## Reconnaissance

- [ ] DNS
- [ ] Subdomains
- [ ] HTTP probing
- [ ] Titles
- [ ] Technologies
- [ ] WhatWeb
- [ ] Wappalyzer
- [ ] Headers
- [ ] Cookies
- [ ] 404 fingerprint
- [ ] TLS
- [ ] CDN / WAF
- [ ] Virtual hosts

## Discovery

- [ ] robots.txt
- [ ] sitemap.xml
- [ ] security.txt
- [ ] Content discovery
- [ ] Crawling
- [ ] Historical URLs
- [ ] Parameters
- [ ] JavaScript
- [ ] Source maps
- [ ] API documentation
- [ ] GraphQL

## Authentication

- [ ] Registration
- [ ] Login
- [ ] Logout
- [ ] Enumeration
- [ ] Password reset
- [ ] Password change
- [ ] MFA
- [ ] Recovery
- [ ] SSO
- [ ] OAuth / OIDC

## Sessions

- [ ] Cookie attributes
- [ ] Session rotation
- [ ] Expiration
- [ ] Logout invalidation
- [ ] Password-change invalidation
- [ ] Password-reset invalidation
- [ ] Concurrent sessions

## Authorisation

- [ ] Horizontal access
- [ ] Vertical access
- [ ] IDOR / BOLA
- [ ] Hidden functions
- [ ] Administrative endpoints
- [ ] HTTP methods
- [ ] API object access
- [ ] File access

## Input Validation

- [ ] XSS
- [ ] SQL injection
- [ ] Command injection
- [ ] Path traversal
- [ ] File inclusion
- [ ] SSTI
- [ ] XXE
- [ ] Deserialization
- [ ] SSRF
- [ ] File upload
- [ ] Header injection

## Browser Security

- [ ] CORS
- [ ] CSRF
- [ ] Clickjacking
- [ ] CSP
- [ ] DOM security
- [ ] postMessage
- [ ] Cookies
- [ ] Storage

## HTTP

- [ ] Methods
- [ ] Host header
- [ ] Request smuggling where appropriate
- [ ] Cache behaviour
- [ ] Redirects
- [ ] Security headers
- [ ] Error handling

## API

- [ ] Endpoint inventory
- [ ] Authentication
- [ ] Object authorisation
- [ ] Function authorisation
- [ ] Rate limiting
- [ ] Mass assignment
- [ ] Excessive data exposure
- [ ] Input validation
- [ ] Versioning
- [ ] Documentation

## Business Logic

- [ ] Workflow bypass
- [ ] State manipulation
- [ ] Price manipulation
- [ ] Quantity manipulation
- [ ] Limit bypass
- [ ] Duplicate actions
- [ ] Race conditions
- [ ] Approval workflows
- [ ] Role transitions

## Evidence

- [ ] Exact request
- [ ] Relevant response
- [ ] User context
- [ ] Role
- [ ] Timestamp
- [ ] Expected behaviour
- [ ] Actual behaviour
- [ ] Minimal data collection
- [ ] Secrets redacted

---

# Quick Recon Commands

```bash
export TARGET="https://example.com"
export DOMAIN="example.com"

dig "$DOMAIN"

subfinder -d "$DOMAIN" -silent -o subdomains.txt

httpx \
    -l subdomains.txt \
    -silent \
    -status-code \
    -title \
    -tech-detect \
    -o alive.txt

whatweb "$TARGET"

curl -skI "$TARGET"

curl -sk "$TARGET/robots.txt"

curl -sk "$TARGET/sitemap.xml"

curl -sk "$TARGET/.well-known/security.txt"

curl -sk \
    "$TARGET/random-invalid-path-839274" \
    -o 404.html

katana -u "$TARGET" -o katana.txt
```

---

# Quick Content Discovery

```bash
ffuf \
    -ac \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -u https://example.com/FUZZ
```

Alternative:

```bash
feroxbuster \
    -u https://example.com \
    -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

---

# Quick Technology Workflow

```text
WhatWeb
   |
   v
Wappalyzer
   |
   v
httpx
   |
   v
Headers
   |
   v
Cookies
   |
   v
404 Fingerprint
   |
   v
HTML / JS
   |
   v
Technology Hypothesis
   |
   v
Manual Validation
```

---

# Quick Input Workflow

```text
Parameter
   |
   v
Unique Marker
   |
   v
Observe Response
   |
   v
Determine Context
   |
   v
Select Test
   |
   v
Minimal Validation
   |
   v
Impact
```

---

# Quick Authorisation Workflow

```text
User A -> Object A
User B -> Object B

        |
        v

User A -> Object B ?

        |
        v

Expected Deny
        |
        v
Actual Allow?
```

---

# Do Not Overreport

Do not automatically report:

```text
Server Header Present
Technology Detected
Wappalyzer Identified Framework
WhatWeb Identified CMS
Default 404 Page
robots.txt Exists
Swagger Exists
GraphQL Exists
Port 443 Open
HTTP OPTIONS Enabled
Missing CSP
Missing Security Header
Cookie Exists
JavaScript Contains Endpoint
Source Map Exists
```

Instead determine:

```text
What is exposed?
      |
      v
Who can access it?
      |
      v
What security boundary exists?
      |
      v
Can that boundary be crossed?
      |
      v
What is the actual impact?
```

---

# Safe Testing Model

Prefer:

```text
Observe
   |
   v
Understand
   |
   v
Compare
   |
   v
Modify Minimally
   |
   v
Validate
   |
   v
Collect Evidence
```

before:

```text
Exploit
Dump Data
Execute Commands
Upload Active Payload
Establish Shell
Scan Internal Networks
Modify Production Data
```

---

# Final Testing Model

```text
Reconnaissance
      |
      v
Application Mapping
      |
      v
Attack Surface
      |
      v
Trust Boundaries
      |
      v
Security Controls
      |
      v
Controlled Validation
      |
      v
Impact
      |
      v
Remediation
```

A useful mental model is:

```text
Input
  |
  v
Processing
  |
  v
Trust Decision
  |
  v
Sensitive Operation
```

Ask:

```text
Can the attacker influence the input?

Does the application trust it?

Is validation performed?

Is authorisation performed?

What sensitive operation follows?
```

---

# References

## 0xdf Cheatsheets

[0xdf - Cheatsheets](https://0xdf.gitlab.io/cheatsheets/){ target="_blank" rel="noopener noreferrer" }

Especially useful for the **Default 404 Pages** fingerprinting reference and practical enumeration notes.

---

## WhatWeb

[WhatWeb - GitHub](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

Use WhatWeb for web technology fingerprinting and correlation.

---

## Wappalyzer

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

[Wappalyzer - Technology Lookup](https://www.wappalyzer.com/lookup/){ target="_blank" rel="noopener noreferrer" }

Useful for identifying publicly observable:

```text
CMS
Frameworks
JavaScript Libraries
Analytics
Infrastructure
Web Servers
CDNs
E-commerce Platforms
```

---

## HackTricks

[HackTricks - Web Pentesting Methodology](https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

Useful as a broad methodology and coverage reference.

---

## InternalAllTheThings

[InternalAllTheThings](https://swisskyrepo.github.io/InternalAllTheThings/){ target="_blank" rel="noopener noreferrer" }

Useful for internal, web, Active Directory and red-team assessment methodology.

---

## PayloadsAllTheThings

[PayloadsAllTheThings](https://swisskyrepo.github.io/PayloadsAllTheThings/){ target="_blank" rel="noopener noreferrer" }

Useful as a vulnerability-specific testing reference.

Always understand and adapt a test rather than blindly copying payloads.

---

## PortSwigger Web Security Academy

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

Major reference for:

```text
Authentication
Access Control
XSS
SQL Injection
CSRF
CORS
SSRF
XXE
SSTI
Request Smuggling
Web Cache
OAuth
JWT
GraphQL
Business Logic
```

---

## PortSwigger XSS Cheat Sheet

[PortSwigger - XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Web Security Testing Guide

[OWASP - Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

Use as a structured testing methodology reference.

---

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

Especially useful for remediation and defensive guidance.

---

## OWASP API Security

[OWASP API Security Project](https://owasp.org/www-project-api-security/){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery httpx

[ProjectDiscovery - httpx](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery Nuclei

[ProjectDiscovery - Nuclei](https://github.com/projectdiscovery/nuclei){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery Katana

[ProjectDiscovery - Katana](https://github.com/projectdiscovery/katana){ target="_blank" rel="noopener noreferrer" }

---

## SecLists

[SecLists](https://github.com/danielmiessler/SecLists){ target="_blank" rel="noopener noreferrer" }

---

## ffuf

[ffuf](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }

---

## feroxbuster

[feroxbuster](https://github.com/epi052/feroxbuster){ target="_blank" rel="noopener noreferrer" }

---

## sqlmap

[sqlmap](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }

---

## Commix

[Commix](https://github.com/commixproject/commix){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

For a new target:

```text
Domain
 |
 v
Subdomains
 |
 v
HTTP Services
 |
 v
Technology
 |
 v
404 / Headers / Cookies
 |
 v
Content
 |
 v
Parameters
 |
 v
JavaScript
 |
 v
Authentication
 |
 v
Authorisation
 |
 v
Input
 |
 v
Business Logic
 |
 v
Impact
```

Start with:

```bash
whatweb https://example.com
```

and correlate with:

```text
Wappalyzer
httpx
Headers
Cookies
404 Fingerprinting
HTML
JavaScript
```

Then discover:

```text
robots.txt
sitemap.xml
Directories
Files
Historical URLs
Parameters
JavaScript
APIs
```

Then test the application's trust boundaries:

```text
Who am I?
   |
   v
What can I access?
   |
   v
What input can I control?
   |
   v
What does the server trust?
   |
   v
Can I cross a security boundary?
```

The objective is not:

```text
Run Every Tool
Try Every Payload
```

The objective is:

```text
Understand
   |
   v
Form Hypothesis
   |
   v
Test
   |
   v
Validate
   |
   v
Demonstrate Impact
```

Technology fingerprinting is the start of the process:

```text
WhatWeb
   +
Wappalyzer
   +
404 Fingerprinting
   +
Headers
   +
JavaScript
   =
Technology Hypothesis
```

and not the conclusion.

A strong web assessment combines:

```text
Automation
    +
Manual Testing
    +
Application Understanding
    +
Security Boundary Analysis
```

rather than relying on scanners alone.
