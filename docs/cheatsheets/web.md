# Web Application Security Cheatsheet

Quick-reference workflows, commands, testing ideas, tools, and validation checklists for authorised web application and API security assessments.

This cheatsheet is designed for the question:

> **What should I check next during a web assessment?**

For detailed explanations, prerequisites, impact, remediation, and vulnerability-specific methodology, use the main Web Application Security notes.

---

# Authorised Use

Use these techniques only for:

```text
Authorised penetration testing
Web application security assessments
API security assessments
Red team exercises
Purple team exercises
Bug bounty programmes within scope
Training environments
CTFs
Security research
```

Always follow:

```text
Scope
Rules of Engagement
Rate Limits
Test Account Restrictions
Data Handling Requirements
Third-Party Restrictions
Production Safety Requirements
```

Some techniques can:

```text
Create accounts
Send email
Trigger SMS
Lock users out
Modify application state
Upload files
Generate large numbers of requests
Cause backend requests
Interact with internal services
Create database records
Affect caches
Consume application resources
Trigger monitoring
```

Use the least intrusive test that answers the security question.

---

# Core Assessment Model

```text
Scope
  |
  v
Reconnaissance
  |
  v
Technology Identification
  |
  v
Attack Surface Mapping
  |
  v
Content Discovery
  |
  v
Parameter Discovery
  |
  v
Authentication
  |
  v
Authorisation
  |
  v
Session Management
  |
  v
Input Handling
  |
  v
Business Logic
  |
  v
API / Client-Side Features
  |
  v
Infrastructure Behaviour
  |
  v
Manual Validation
  |
  v
Evidence
  |
  v
Reporting
```

The important principle is:

```text
Discover
   |
   v
Understand
   |
   v
Hypothesise
   |
   v
Test
   |
   v
Validate
   |
   v
Assess Impact
```

rather than:

```text
Run Scanner
    |
    v
Report Everything
```

---

# Starting Position

Web testing changes significantly depending on the access provided.

```text
Internet / Unauthenticated
        |
        v
External Attack Surface

Authenticated Low-Privilege User
        |
        v
Authorisation + Business Logic

Multiple User Roles
        |
        v
Horizontal + Vertical Access Control

Administrator Account
        |
        v
Administrative Trust Boundaries

API Token
        |
        v
API Object + Function Authorisation

Source Code Available
        |
        v
White-Box Testing

Internal Application
        |
        v
Internal Trust + Identity + Infrastructure
```

---

# Assessment Perspectives

Always consider at least these perspectives:

```text
Unauthenticated User
Authenticated User A
Authenticated User B
Higher-Privilege User
Administrator
API Client
Mobile Client
Internal Service
Third-Party Integration
```

A vulnerability may only become visible when comparing two contexts.

---

# Initial Target Setup

Useful shell variables:

```bash
export TARGET="https://app.example.com"
export HOST="app.example.com"
export DOMAIN="example.com"
```

Check:

```bash
printf 'TARGET=%s\nHOST=%s\nDOMAIN=%s\n' "$TARGET" "$HOST" "$DOMAIN"
```

---

# DNS

```bash
dig "$HOST"
```

```bash
dig A "$HOST"
```

```bash
dig AAAA "$HOST"
```

```bash
dig CNAME "$HOST"
```

Nameservers:

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

---

# Quick HTTP Inspection

Headers:

```bash
curl -I "$TARGET"
```

Verbose:

```bash
curl -v "$TARGET"
```

Follow redirects:

```bash
curl -L "$TARGET"
```

Headers and body:

```bash
curl -i "$TARGET"
```

Save response:

```bash
curl -sS "$TARGET" -o response.html
```

---

# HTTP Methods

OPTIONS:

```bash
curl -i -X OPTIONS "$TARGET"
```

HEAD:

```bash
curl -I "$TARGET"
```

Do not report unusual methods solely because they are advertised.

Determine whether they create meaningful unintended behaviour.

---

# Technology Identification

Technology fingerprinting helps guide testing.

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
Authentication Platform
API Framework
Cloud Platform
Version Information
Third-Party Components
```

---

# WhatWeb

Basic:

```bash
whatweb "$TARGET"
```

Verbose:

```bash
whatweb -v "$TARGET"
```

Higher aggression:

```bash
whatweb -a 3 "$TARGET"
```

Input file:

```bash
whatweb -i urls.txt
```

JSON logging:

```bash
whatweb --log-json=whatweb.json "$TARGET"
```

Treat fingerprinting as evidence, not proof.

```text
WhatWeb Result
      |
      v
Verify Manually
      |
      v
Search Known Behaviour
      |
      v
Version Relevant?
      |
      v
Test Configuration
```

---

# Wappalyzer

Wappalyzer can identify technologies using public application signals such as:

```text
HTML
JavaScript
Headers
Cookies
Meta Tags
Script Paths
Framework Patterns
```

Useful for identifying:

```text
CMS
Framework
Analytics
CDN
Web Server
JavaScript Libraries
E-Commerce Platforms
Authentication Technology
```

Verify results independently.

---

# Technology Fingerprinting Sources

Combine:

```text
WhatWeb
Wappalyzer
HTTP Headers
HTML Source
Cookies
JavaScript
Favicon
Error Pages
Default Pages
TLS Certificates
URL Structure
Static Asset Paths
```

---

# Default 404 Fingerprinting

Request a random path:

```bash
curl -i "$TARGET/this-page-should-not-exist-928374"
```

Inspect:

```text
Status Code
Server Header
Framework Error Page
Page Title
HTML Structure
Response Length
Cookies
Debug Information
```

Default error pages can reveal:

```text
Framework
CMS
Reverse Proxy
Application Server
Hosting Platform
```

The 0xdf Default 404 Pages reference is useful for visual fingerprinting.

---

# Favicon Fingerprinting

Download:

```bash
curl -sS "$TARGET/favicon.ico" -o favicon.ico
```

Hash:

```bash
md5sum favicon.ico
```

```bash
sha256sum favicon.ico
```

Favicon hashes can support technology identification but should not be treated as definitive proof.

---

# Subdomain Enumeration

Common sources:

```text
Certificate Transparency
DNS
Search Engines
Passive DNS
Subfinder
Amass
Assetfinder
crt.sh
```

Subfinder:

```bash
subfinder -d "$DOMAIN" -silent
```

Save:

```bash
subfinder -d "$DOMAIN" -silent -o subdomains.txt
```

---

# Probe Discovered Hosts

```bash
httpx -l subdomains.txt
```

Useful metadata:

```bash
httpx -l subdomains.txt -status-code -title -tech-detect
```

Add IP:

```bash
httpx -l subdomains.txt -status-code -title -tech-detect -ip
```

---

# Attack Surface Inventory

Record:

```text
Hostname
IP
Port
Protocol
Status
Title
Technology
Authentication Required?
Application Purpose
Environment
Interesting Paths
Notes
```

Example:

```text
app.example.com
api.example.com
admin.example.com
dev.example.com
staging.example.com
files.example.com
auth.example.com
sso.example.com
```

---

# Virtual Host Enumeration

A single IP may host multiple applications.

Check:

```text
Host Header
TLS Certificate
DNS
Reverse DNS
Application Redirects
Error Responses
```

Fuzzing example:

```bash
ffuf -w subdomains.txt -u https://10.10.10.10/ -H 'Host: FUZZ.example.com'
```

Use response filtering to remove the default virtual-host response.

---

# robots.txt

```bash
curl -sS "$TARGET/robots.txt"
```

Look for:

```text
Disallowed Paths
Administrative Paths
Old Endpoints
Uploads
Backups
Internal Features
```

Remember:

```text
Disallow
   !=
Access Control
```

---

# sitemap.xml

```bash
curl -sS "$TARGET/sitemap.xml"
```

Useful for discovering:

```text
Routes
Products
Profiles
Legacy URLs
Localized Paths
Application Sections
```

---

# security.txt

```bash
curl -sS "$TARGET/.well-known/security.txt"
```

Useful for understanding:

```text
Security Contact
Disclosure Policy
Acknowledgements
Scope Information
```

---

# Common Interesting Files

Check where appropriate:

```text
/robots.txt
/sitemap.xml
/.well-known/security.txt
/favicon.ico
/manifest.json
/asset-manifest.json
/openapi.json
/swagger.json
/swagger-ui/
/api-docs
/graphql
/graphiql
/.git/
/.env
/server-status
/phpinfo.php
```

Do not assume these paths exist.

---

# Content Discovery

Useful tools:

```text
ffuf
feroxbuster
gobuster
dirsearch
Burp Content Discovery
```

---

# ffuf

Basic:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt -u "$TARGET/FUZZ"
```

Extensions:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt -u "$TARGET/FUZZ" -e .php,.asp,.aspx,.jsp,.json,.txt,.xml,.bak
```

---

# feroxbuster

```bash
feroxbuster -u "$TARGET"
```

With wordlist:

```bash
feroxbuster -u "$TARGET" -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

---

# gobuster

```bash
gobuster dir -u "$TARGET" -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

---

# Soft 404s

Do not rely only on status codes.

Compare:

```text
Status
Length
Words
Lines
Title
Body Similarity
Redirect Location
```

Example:

```text
/random-1234 -> 200, 4812 bytes
/admin       -> 200, 4812 bytes
```

This may indicate a soft 404.

---

# Discovery Workflow

```text
Known URL
   |
   v
Random 404 Baseline
   |
   v
Wordlist
   |
   v
Filter Baseline
   |
   v
Interesting Responses
   |
   v
Manual Inspection
```

---

# Backup Files

Look for accidental copies such as:

```text
.bak
.old
.orig
.save
.tmp
~
.zip
.tar
.tar.gz
.7z
```

Focus on known filenames rather than generating excessive requests.

---

# Git Repository Exposure

Check:

```bash
curl -I "$TARGET/.git/HEAD"
```

Potential exposure can reveal:

```text
Source Code
Commit History
Deleted Secrets
Configuration
Internal URLs
Credentials
API Keys
```

Do not download an entire repository unless authorised and necessary.

---

# JavaScript Discovery

JavaScript frequently reveals hidden application functionality.

Look for:

```text
API Endpoints
Routes
Parameters
Feature Flags
Internal Hosts
WebSocket URLs
GraphQL Endpoints
Authentication Logic
Source Maps
Secrets
Debug Features
Third-Party Integrations
```

---

# Find JavaScript References

From downloaded HTML:

```bash
grep -Eo 'src="[^"]+\.js[^"]*"' response.html
```

---

# Search Downloaded JavaScript

```bash
grep -RniE 'api|token|secret|password|graphql|websocket|admin|internal|debug' js/
```

Use findings as leads.

Do not automatically report every string containing `token` or `secret`.

---

# Source Maps

Look for:

```text
.js.map
sourceMappingURL
```

Example:

```bash
grep -Rni 'sourceMappingURL' js/
```

Source maps may reveal:

```text
Original Source
Component Names
Internal Routes
API Calls
Developer Comments
```

---

# Crawling

Useful tools:

```text
Katana
Burp Suite
gau
waybackurls
hakrawler
```

---

# Katana

```bash
katana -u "$TARGET"
```

Save:

```bash
katana -u "$TARGET" -o katana.txt
```

JavaScript crawling:

```bash
katana -u "$TARGET" -jc
```

---

# Historical URLs

gau:

```bash
gau "$DOMAIN"
```

waybackurls:

```bash
echo "$DOMAIN" | waybackurls
```

Historical URLs may reveal:

```text
Old Endpoints
Old Parameters
Deprecated APIs
Legacy File Names
Removed Features
```

Historical availability does not prove the endpoint still exists.

---

# Parameter Discovery

Parameters can appear in:

```text
Query Strings
POST Forms
JSON
XML
Headers
Cookies
Path Segments
GraphQL Variables
Multipart Requests
WebSocket Messages
```

---

# Arjun

```bash
arjun -u "$TARGET"
```

---

# ParamSpider

Typical workflow:

```bash
python3 paramspider.py -d example.com
```

Review discovered URLs before sending additional probes.

---

# Parameter Inventory

Record:

```text
Endpoint
Method
Parameter
Location
Type
Authentication Required
Observed Behaviour
Potential Sink
```

---

# Input Location Model

```text
User Input
   |
   +--> Query
   +--> Body
   +--> JSON
   +--> XML
   +--> Header
   +--> Cookie
   +--> Path
   +--> File
   +--> WebSocket
   |
   v
Application
```

Do not test only URL parameters.

---

# Burp Suite Core Workflow

```text
Proxy
  |
  v
HTTP History
  |
  v
Target Map
  |
  v
Repeater
  |
  v
Compare Behaviour
  |
  v
Intruder / Extensions
  |
  v
Manual Validation
```

---

# Burp Repeater

Use Repeater for:

```text
Parameter Modification
Role Comparison
Header Testing
Cookie Testing
Method Changes
Content-Type Changes
API Testing
Authentication Testing
Business Logic
Race Condition Preparation
Cache Testing
```

---

# Burp Comparer

Useful for comparing:

```text
User A vs User B
Authenticated vs Unauthenticated
Valid vs Invalid ID
GET vs POST
Different Content Types
Different Host Headers
Cache Hit vs Miss
```

---

# Useful Burp Extensions

Depending on the test:

```text
Autorize
AuthMatrix
Logger++
Param Miner
HTTP Request Smuggler
Turbo Intruder
JWT Editor
JSON Web Tokens
Backslash Powered Scanner
Collaborator Everywhere
Upload Scanner
Java Deserialization Scanner
Software Vulnerability Scanner
GraphQL Raider
JS Link Finder
Content Type Converter
```

Install only trusted extensions and review what traffic they generate.

---

# Burp Param Miner

Useful for discovering:

```text
Hidden Headers
Unkeyed Headers
Hidden Parameters
Cache Inputs
Host Header Behaviour
```

Especially useful during:

```text
Cache Poisoning
Host Header Testing
Parameter Discovery
```

---

# Collaborator / Out-of-Band Testing

Useful for validating blind interactions such as:

```text
SSRF
XXE
Blind XSS
Blind Command Injection
External Service Interaction
```

Use only an approved callback service.

Avoid exposing sensitive application data to third-party infrastructure.

---

# Authentication Testing

Map:

```text
Registration
Login
Logout
Password Reset
Password Change
MFA
Remember Me
Account Recovery
Email Verification
SSO
OAuth
SAML
API Authentication
Session Creation
```

---

# Login Checklist

Check:

```text
[ ] Username enumeration
[ ] Email enumeration
[ ] Error-message differences
[ ] Response-length differences
[ ] Timing differences
[ ] Rate limiting
[ ] Lockout behaviour
[ ] MFA
[ ] CAPTCHA
[ ] Session rotation
[ ] Password policy
[ ] Remember-me behaviour
[ ] SSO fallback paths
```

---

# Username Enumeration

Compare:

```text
Known User
Unknown User
Wrong Password
Locked User
Disabled User
```

Look for differences in:

```text
Message
Status
Length
Timing
Headers
Redirects
Cookies
```

Avoid high-volume enumeration unless explicitly authorised.

---

# Password Policy

Assess:

```text
Minimum Length
Maximum Length
Character Requirements
Common Password Blocking
Breached Password Detection
Password Reuse
Password History
Password Change Controls
```

Do not equate complexity requirements with strong password security.

---

# Rate Limiting

Test carefully.

Questions:

```text
Is limiting per IP?

Per account?

Per session?

Per device?

Per endpoint?

Global?

Does it apply across equivalent endpoints?

Does it reset unexpectedly?

Can concurrent requests bypass the intended control?
```

Avoid intentionally locking accounts unless authorised.

---

# Anti-Automation

Review:

```text
CAPTCHA
Rate Limiting
Progressive Delay
Account Lockout
Device Signals
Risk-Based Authentication
MFA
Transaction Limits
```

A CAPTCHA alone is not a complete anti-automation control.

---

# Password Reset

Map:

```text
Request Reset
    |
    v
Token Creation
    |
    v
Token Delivery
    |
    v
Token Validation
    |
    v
Password Change
    |
    v
Session Handling
```

Check:

```text
User Enumeration
Token Entropy
Token Lifetime
Single Use
Account Binding
Host Header Dependence
Email Change Interaction
Session Invalidation
MFA Interaction
Rate Limiting
```

---

# Registration

Check:

```text
Duplicate Accounts
Email Verification
Username Normalisation
Case Sensitivity
Reserved Names
Role Assignment
Invite Codes
Tenant Assignment
Referral Logic
Registration Limits
Domain Restrictions
```

---

# Account Recovery

Ask:

```text
Can recovery bypass MFA?

Can recovery change account identity?

Can recovery tokens be reused?

Does recovery invalidate sessions?

Are old email addresses trusted?

Are security questions predictable?
```

---

# MFA

Check:

```text
Enrollment
Activation
Challenge
Recovery
Backup Codes
Device Trust
Remember Device
MFA Reset
Alternative Login Paths
SSO Paths
API Paths
```

The key question is:

```text
Can authentication reach the same privilege without satisfying MFA?
```

---

# Session Management

Inspect:

```text
Session Cookie
Session Token
Refresh Token
CSRF Token
Remember-Me Token
Device Token
```

---

# Cookie Attributes

Look for:

```text
Secure
HttpOnly
SameSite
Path
Domain
Expires
Max-Age
```

Example:

```bash
curl -I "$TARGET"
```

Missing attributes should be interpreted in application context.

---

# Session Rotation

Check whether the session identifier changes after:

```text
Login
Privilege Change
Password Change
MFA
Account Recovery
Role Change
```

---

# Session Fixation

Concept:

```text
Pre-Authentication Session
          |
          v
Victim Authenticates
          |
          v
Same Session Identifier?
```

Secure behaviour normally involves appropriate session regeneration at authentication boundaries.

---

# Logout

Check:

```text
Server-Side Session Invalidated?
Cookie Removed?
Refresh Token Revoked?
Back Button Behaviour?
Multiple Sessions?
API Token Still Valid?
```

---

# Concurrent Sessions

Determine:

```text
Are multiple sessions allowed?

Can users view sessions?

Can sessions be revoked?

Does password change revoke old sessions?

Does MFA reset revoke old sessions?
```

---

# Authorisation

Always test authorisation independently from authentication.

```text
Authentication
      !=
Authorisation
```

Use at least:

```text
Unauthenticated
User A
User B
Administrator
```

where permitted.

---

# Horizontal Authorisation

Example concept:

```text
User A -> /account/1001
User B -> /account/1002
```

Test whether User A can access User B's object.

---

# Vertical Authorisation

Example:

```text
Normal User
    |
    v
Administrative Function
```

Check whether server-side authorisation prevents access.

---

# IDOR / BOLA

Look for identifiers in:

```text
URL Paths
Query Parameters
JSON
GraphQL Variables
Headers
Cookies
File Names
UUIDs
Numeric IDs
Encoded Values
```

Use two controlled accounts where possible.

---

# IDOR Testing Model

```text
User A
   |
   v
Object A
   |
   v
Capture Request
   |
   v
Change Identifier
   |
   v
Object B
   |
   v
Server-Side Authorisation?
```

Do not access unrelated real-user data unnecessarily.

---

# Function-Level Authorisation

Check:

```text
GET vs POST
UI-hidden endpoints
Admin APIs
Bulk actions
Export functions
Import functions
Delete operations
Role-management endpoints
```

Removing a button from the UI is not authorisation.

---

# Method-Based Access Control

Compare:

```text
GET
POST
PUT
PATCH
DELETE
```

Do not assume an endpoint applies identical authorisation to every method.

---

# Content-Type Differences

Compare where appropriate:

```text
application/json
application/x-www-form-urlencoded
multipart/form-data
application/xml
text/plain
```

Different parsers may reach different validation or authorisation paths.

---

# Business Logic

Business logic vulnerabilities often require understanding what the application is supposed to do.

Map:

```text
Workflow
State
Role
Limit
Price
Quantity
Ownership
Approval
Sequence
Trust Boundary
```

---

# Business Logic Questions

Ask:

```text
Can steps be skipped?

Can steps be repeated?

Can steps occur out of order?

Can values become negative?

Can limits be exceeded?

Can the same benefit be claimed twice?

Can another user's state be referenced?

Can client-controlled values override server values?

Can approval be bypassed?

Can stale state be reused?
```

---

# Workflow Testing

```text
Step 1
  |
  v
Step 2
  |
  v
Step 3
```

Try:

```text
1 -> 3
2 -> 1
3 directly
2 twice
3 twice
Old Step 2 after Step 3
```

Only where safe and authorised.

---

# Client-Side Validation

If validation exists only in:

```text
JavaScript
HTML Attributes
Mobile Client
Frontend Framework
```

verify whether the server independently enforces it.

---

# Server-Side Validation

Test:

```text
Boundary Values
Unexpected Types
Missing Fields
Duplicate Fields
Null Values
Empty Values
Negative Values
Large Values
Alternative Encodings
```

Avoid resource-exhaustion testing unless explicitly permitted.

---

# Race Conditions

Race conditions occur when concurrent requests interact with shared state incorrectly.

Common areas:

```text
Coupon Redemption
Gift Cards
Balance Transfers
Inventory
Invitations
Password Reset
Email Verification
MFA
Account Registration
Voting
Promo Codes
Single-Use Tokens
File Processing
```

---

# Race Condition Model

```text
Check State
    |
    v
Action Allowed?
    |
    v
Update State
```

If multiple requests reach the vulnerable window:

```text
Request A ----\
               > Check Before Update
Request B ----/
```

both may be accepted.

---

# Race Condition Testing

Prefer controlled test data.

Use Burp Repeater's parallel request functionality or Turbo Intruder where appropriate.

Start with a very small number of requests.

Do not perform uncontrolled concurrency against production systems.

---

# Rate-Limit Race Conditions

A limit may be correctly enforced sequentially but fail under concurrency.

Check carefully:

```text
Sequential Requests
        |
        v
Limit Works

Parallel Requests
        |
        v
Same Limit?
```

---

# HTTP Basics

Understand:

```text
Request Line
Headers
Body
```

Example:

```http
POST /api/profile HTTP/1.1
Host: app.example.com
Content-Type: application/json
Cookie: session=...

{"displayName":"test"}
```

---

# Response Analysis

Inspect:

```text
Status
Headers
Cookies
Redirect
Content-Type
Content-Length
Body
Timing
Cache Headers
Security Headers
```

---

# Security Headers

Common headers:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
Cross-Origin-Opener-Policy
Cross-Origin-Resource-Policy
```

Legacy:

```text
X-Frame-Options
```

Do not report missing headers without understanding application context and actual risk.

---

# TLS

Basic inspection:

```bash
openssl s_client -connect "$HOST:443" -servername "$HOST"
```

Certificate:

```bash
echo | openssl s_client -connect "$HOST:443" -servername "$HOST" 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```

Nmap:

```bash
nmap -p443 --script ssl-cert,ssl-enum-ciphers "$HOST"
```

---

# CORS

Inspect:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Access-Control-Allow-Methods
Access-Control-Allow-Headers
Vary
```

Test with a controlled Origin:

```bash
curl -i "$TARGET" -H 'Origin: https://example.invalid'
```

---

# CORS Model

```text
Attacker-Controlled Origin
        |
        v
Browser Sends Request
        |
        v
Server CORS Policy
        |
        v
Browser Permits Response Reading?
```

A permissive-looking header is not automatically exploitable.

Consider:

```text
Credentials
Sensitive Response
Origin Reflection
Browser Behaviour
Preflight
```

---

# CSRF

Ask:

```text
Does request change state?

Does browser automatically attach authentication?

Is there an unpredictable CSRF token?

Is token bound appropriately?

Are SameSite cookies relevant?

Does Origin/Referer validation exist?

Can content type be changed?
```

---

# CSRF Testing Model

```text
State-Changing Request
       |
       v
Authentication via Browser?
       |
       v
Anti-CSRF Control?
       |
       v
Can Cross-Site Request Be Sent?
       |
       v
Impact
```

---

# Clickjacking

Inspect:

```text
Content-Security-Policy: frame-ancestors
X-Frame-Options
```

Check whether sensitive UI can be framed.

Do not report frameability alone without considering what user actions could be induced.

---

# Open Redirect

Look for parameters such as:

```text
url
uri
redirect
redirect_uri
return
returnUrl
next
continue
dest
destination
callback
```

Assess impact in context:

```text
Phishing
OAuth
SSO
Trusted-Domain Bypass
Security-Control Bypass
```

---

# XSS

Types:

```text
Reflected
Stored
DOM-Based
```

Identify:

```text
Source
Context
Sink
Encoding
Sanitisation
CSP
Execution
Impact
```

---

# XSS Contexts

```text
HTML
HTML Attribute
JavaScript
URL
CSS
DOM
Template
```

Payloads are context-dependent.

Do not blindly paste large payload lists.

---

# Safe XSS Validation

Start with harmless markers:

```text
XSS_TEST_12345
```

Determine:

```text
Reflected?
Encoded?
Stored?
Context?
```

Then use the minimum harmless proof needed to demonstrate script execution in the authorised test environment.

---

# DOM-Based Vulnerabilities

Review sources such as:

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

Potential sinks include:

```text
innerHTML
outerHTML
document.write
eval
setTimeout with string
setInterval with string
location assignment
```

Context determines whether the flow is dangerous.

---

# DOM Clobbering

DOM clobbering abuses HTML elements and named properties to influence JavaScript assumptions about global variables or object properties.

Look for code patterns that trust:

```text
window.someName
document.someName
element.id
element.name
```

without verifying the expected object type.

Testing model:

```text
Attacker-Controlled HTML
        |
        v
Named DOM Element
        |
        v
JavaScript Property Resolution
        |
        v
Unexpected Object / Value
        |
        v
Security-Relevant Sink?
```

Do not report clobbering unless it affects meaningful application behaviour.

---

# HTML Injection

Test whether attacker-controlled HTML is rendered as markup.

Differentiate:

```text
HTML Injection
      !=
JavaScript Execution
```

Assess impact such as:

```text
UI Manipulation
Content Spoofing
Phishing
Form Injection
Security Messaging Manipulation
```

---

# Blind XSS

Potential sinks include:

```text
Admin Panels
Support Tickets
Log Viewers
CRM Systems
Moderation Interfaces
Analytics Dashboards
Back-Office Applications
```

Use only approved callback infrastructure.

Do not send sensitive data to third-party collectors.

---

# XS-Leaks

Cross-site leaks can use browser side channels to infer information about another origin.

Areas include:

```text
Framing
Window References
Resource Loading
Cache State
Timing
Navigation
Browser APIs
```

Assess browser protections and whether sensitive cross-origin state can actually be inferred.

---

# Third-Party JavaScript

Review:

```text
Analytics
Chat Widgets
Tag Managers
Payment Scripts
CDN Libraries
Advertising
Support Widgets
```

Questions:

```text
Who controls the script?

Does it execute in the application's origin?

Is integrity checking used where appropriate?

What data can it access?

What happens if the supplier is compromised?
```

---

# SQL Injection

Look for database-backed input in:

```text
Query Parameters
Search
Filters
Sorting
Login
IDs
JSON
Headers
Cookies
API Parameters
```

Start with controlled behavioural testing.

---

# SQLi Signals

Compare:

```text
Normal Input
Special Character
Boolean Condition
Type Mismatch
Unexpected Value
```

Observe:

```text
Error
Status
Length
Timing
Returned Rows
Application Behaviour
```

---

# sqlmap

Use only after manual evidence suggests SQL injection.

Basic:

```bash
sqlmap -u 'https://app.example.com/item?id=1'
```

Request file:

```bash
sqlmap -r request.txt
```

Avoid aggressive options by default.

Do not dump production databases simply because a tool can.

---

# SQLi Validation Model

```text
Input
  |
  v
Database Query?
  |
  v
Behaviour Difference
  |
  v
Repeatable?
  |
  v
Injection Confirmed?
  |
  v
Minimum Evidence
```

---

# NoSQL Injection

Potential technologies:

```text
MongoDB
CouchDB
Elasticsearch
Other document/query stores
```

Look for:

```text
JSON Objects
Filter Parameters
Search
Authentication
Nested Objects
Operator Handling
Type Confusion
```

---

# NoSQL Testing Questions

Ask:

```text
Can scalar input become an object?

Are query operators accepted from user input?

Are types enforced?

Are filters constructed directly from JSON?

Does authentication compare user-controlled query objects?
```

Use harmless differential testing before attempting broader extraction.

---

# LDAP Injection

LDAP-backed functionality may include:

```text
Authentication
Directory Search
Employee Lookup
Group Search
Address Books
Internal Portals
```

Look for unsafely constructed LDAP filters.

Test with controlled syntax changes and observe whether directory query behaviour changes.

---

# OS Command Injection

Potential sinks:

```text
Ping
Traceroute
DNS Lookup
File Conversion
Backup
Archive
Image Processing
Git Operations
System Utilities
Administrative Features
```

Start with non-destructive behavioural tests.

---

# Command Injection Model

```text
Input
  |
  v
Application
  |
  v
Shell / Process?
  |
  v
User Input Reaches Command?
  |
  v
Observable Behaviour?
```

Avoid destructive commands.

---

# Commix

Where command injection is already suspected:

```bash
commix --url='https://app.example.com/example?parameter=value'
```

Review tool behaviour before using automated exploitation options.

---

# SSTI

Potential template engines include:

```text
Jinja2
Twig
Freemarker
Velocity
Smarty
Handlebars
ERB
```

Start with simple arithmetic/template-expression detection appropriate to the suspected engine.

Determine:

```text
Template Engine
Evaluation Context
Sandbox
Available Objects
Impact
```

Do not immediately attempt command execution.

---

# XXE

Potential XML entry points:

```text
SOAP
XML APIs
SAML
SVG
Document Upload
RSS
XML Configuration
```

Check:

```text
DOCTYPE handling
External entity resolution
XInclude
Parser configuration
Out-of-band interaction
```

Use controlled resources.

---

# Blind XXE

When output is not reflected:

```text
XML Input
   |
   v
External Reference
   |
   v
Approved Callback
   |
   v
Interaction?
```

Do not request sensitive local files merely to prove external entity processing if a harmless callback is sufficient.

---

# SSRF

Potential URL-taking functionality:

```text
URL Preview
Webhook
Import
Image Fetch
PDF Generator
Proxy
Callback
Avatar
Feed Import
Cloud Integration
Document Conversion
```

---

# SSRF Testing

Start with an approved controlled URL.

```text
Application
    |
    v
Fetch URL
    |
    v
Controlled Server
    |
    v
Observe Request
```

Then determine:

```text
Protocol Restrictions
Redirect Handling
DNS Resolution
Allowlist
Blocklist
Internal Reachability
Response Visibility
```

Avoid probing sensitive internal services unless explicitly authorised.

---

# Blind SSRF

Use approved out-of-band infrastructure.

Evidence can be as simple as:

```text
Timestamp
Source IP
Hostname
Requested Path
Headers
```

Do not escalate to internal metadata access unless required and permitted.

---

# Path Traversal

Potential parameters:

```text
file
path
page
template
download
document
folder
filename
```

Start with known harmless application files where possible.

Assess:

```text
Canonicalisation
Encoding
Path Normalisation
Allowlist
Base Directory Enforcement
```

---

# File Inclusion

Differentiate:

```text
Path Traversal
Local File Inclusion
Remote File Inclusion
Template Inclusion
```

Determine what the application actually does with the supplied path.

---

# File Upload

Map the complete pipeline:

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
Processing
  |
  v
Retrieval
  |
  v
Rendering / Execution
```

---

# File Upload Checklist

Check:

```text
Extension
MIME Type
Magic Bytes
Filename
Path Handling
Storage Location
Randomisation
Overwrite
Access Control
Direct Access
Content-Disposition
Image Processing
Archive Extraction
Antivirus
Execution
Public Exposure
Metadata
```

---

# Safe Upload Validation

Prefer harmless files.

For antivirus validation, the EICAR test file may be appropriate where explicitly approved.

Do not upload executable malware to production systems merely to prove that file validation is incomplete.

---

# Image Processing

Upload pipelines may invoke:

```text
ImageMagick
GraphicsMagick
ExifTool
Ghostscript
PDF Libraries
Office Converters
Thumbnail Generators
```

Fingerprint processing behaviour carefully.

A component version alone does not prove vulnerability.

---

# Dynamic PDF / Document Generation

Features such as:

```text
Print to PDF
Invoice Generation
Report Export
HTML to PDF
Document Preview
Screenshot Generation
```

may introduce additional server-side processing.

Assess:

```text
External Resource Loading
Internal URL Fetching
HTML Interpretation
Template Injection
File Access
JavaScript Handling
Metadata Exposure
```

Use harmless controlled resources for validation.

---

# Insecure Deserialization

Potential formats:

```text
Java Serialization
.NET Serialization
PHP Serialization
Python Pickle
Ruby Marshal
Custom Binary Formats
Signed Application Objects
```

Look for:

```text
Opaque Encoded Blobs
Serialized Cookies
State Parameters
Base64 Objects
Binary Request Bodies
Framework-Specific Markers
```

Do not send gadget chains to production systems without explicit authorisation.

---

# Prototype Pollution

Relevant primarily to JavaScript ecosystems.

Distinguish:

```text
Client-Side Prototype Pollution
Server-Side Prototype Pollution
```

Look for unsafe recursive merging or property assignment involving attacker-controlled keys.

Interesting keys conceptually include:

```text
__proto__
constructor
prototype
```

Start with non-destructive property behaviour.

---

# HTTP Host Header

Test whether application behaviour trusts:

```text
Host
X-Forwarded-Host
Forwarded
X-Host
X-Original-Host
```

Potentially affected functionality:

```text
Password Reset
Absolute URL Generation
Routing
Cache Keys
Virtual Hosting
Security Links
```

---

# Host Header Testing

Controlled example:

```bash
curl -i "$TARGET" -H 'Host: example.invalid'
```

Proxy environments may behave differently.

Do not report Host reflection unless it leads to meaningful security impact.

---

# HTTP Header Injection / CRLF

Potential sinks include:

```text
Redirect Locations
Download Filenames
Custom Headers
Logging
Proxy Headers
Email Headers
```

Look for unsafe inclusion of user-controlled data in response headers.

Assess whether newline characters can alter:

```text
Response Headers
Cookies
Redirects
Body Interpretation
```

Use harmless custom-header proofs.

---

# HTTP Request Smuggling

Request smuggling involves disagreement between HTTP components about request boundaries.

Concept:

```text
Client
  |
  v
Front End
  |
  v
Back End
```

If they parse boundaries differently:

```text
Request Desynchronisation
```

can occur.

---

# Request Smuggling Safety

This testing can affect other users.

Prefer:

```text
Burp HTTP Request Smuggler
Dedicated Test Environment
Single-User Test Host
Non-Destructive Detection
```

Do not perform aggressive desynchronisation testing against production unless explicitly approved.

---

# Web Cache Poisoning

Model:

```text
Attacker Input
      |
      v
Application Response
      |
      v
Cache
      |
      v
Other Users
```

Look for:

```text
Unkeyed Headers
Unkeyed Parameters
Host Variations
Forwarded Headers
Path Normalisation
Cache-Key Differences
```

---

# Cache Poisoning Workflow

```text
Identify Cache
     |
     v
Find Unkeyed Input
     |
     v
Observe Response Influence
     |
     v
Determine Cacheability
     |
     v
Controlled Cache Test
```

Avoid poisoning shared production responses.

---

# Web Cache Deception

Cache deception differs from cache poisoning.

```text
Cache Poisoning
    =
Attacker influences cached content

Cache Deception
    =
Cache stores sensitive victim-specific content
```

Test whether URL/path transformations cause private responses to become publicly cacheable.

Use only controlled accounts and your own sensitive test data.

---

# Cache Indicators

Inspect:

```text
Age
Cache-Control
Vary
ETag
X-Cache
CF-Cache-Status
Via
Server-Timing
CDN-Specific Headers
```

Headers vary by platform.

---

# Broken Link Hijacking

Broken-link hijacking occurs when an application references an external resource whose destination can potentially be re-registered or reclaimed.

Look for:

```text
Dead Social Links
Expired Domains
Deleted GitHub Repositories
Removed Package Names
Unused Cloud Resources
External JavaScript
External CSS
Documentation Links
```

Assessment model:

```text
Application Reference
       |
       v
External Resource Missing
       |
       v
Can Resource Be Reclaimed?
       |
       v
What Trust Does Application Place In It?
       |
       v
Impact
```

Do not register third-party domains or resources unless explicitly authorised.

---

# HTML Smuggling

HTML smuggling uses browser-side functionality to construct files locally rather than transferring the final file directly from the server.

During defensive web assessments, review whether:

```text
JavaScript constructs Blob objects
Data is embedded or encoded client-side
Downloads are generated dynamically
Security controls depend only on network-layer file inspection
```

Do not generate malicious payloads.

The relevant question is whether security architecture assumes that every downloaded file crosses the network in its final form.

---

# WebDAV

Check whether WebDAV is exposed:

```bash
curl -i -X OPTIONS "$TARGET"
```

Look for methods such as:

```text
PROPFIND
MKCOL
COPY
MOVE
LOCK
UNLOCK
PUT
DELETE
```

Exposure alone is not a vulnerability.

Assess:

```text
Authentication
Authorisation
Writable Locations
File Types
Execution Context
Information Disclosure
```

---

# Information Disclosure

Look for:

```text
Stack Traces
Debug Pages
Internal IPs
Internal Hostnames
Source Paths
Database Errors
Framework Versions
Secrets
API Keys
Tokens
Credentials
Environment Variables
Cloud Metadata
Source Code
Backups
Comments
```

---

# Error Handling

Compare malformed requests.

Look for:

```text
Framework Error
Stack Trace
SQL Error
Filesystem Path
Internal Host
Source File
Line Number
Debug Mode
```

Avoid causing repeated server errors.

---

# Debug Interfaces

Potential examples:

```text
/debug
/console
/actuator
/server-status
/phpinfo.php
/swagger
/graphiql
```

Do not assume a debug-looking endpoint is vulnerable.

Assess actual information or functionality exposed.

---

# API Security

First inventory:

```text
Base URL
Version
Authentication
Endpoints
Methods
Objects
Identifiers
Roles
Scopes
Rate Limits
Documentation
```

---

# API Discovery

Look for:

```text
/api/
/api/v1/
/api/v2/
/rest/
/graphql
/swagger.json
/openapi.json
/api-docs
```

Also inspect:

```text
JavaScript
Mobile Applications
Network Traffic
Documentation
Historical URLs
```

---

# OpenAPI / Swagger

If documentation is exposed, review:

```text
Endpoints
Methods
Parameters
Schemas
Authentication
Deprecated Endpoints
Administrative Operations
Hidden Functionality
```

Documentation exposure alone is not necessarily a vulnerability.

---

# API Authorisation

Test:

```text
Object-Level Authorisation
Function-Level Authorisation
Property-Level Authorisation
Tenant Isolation
Role Enforcement
```

---

# BOLA

```text
User A
   |
   v
/api/orders/1001
   |
   v
Change Object ID
   |
   v
/api/orders/1002
   |
   v
Server Checks Ownership?
```

Use controlled accounts and controlled objects.

---

# BFLA

Broken Function Level Authorisation:

```text
Normal User
    |
    v
Administrative API Function
    |
    v
Server-Side Role Check?
```

---

# Property-Level Authorisation

Look for sensitive fields such as:

```text
role
isAdmin
owner
tenantId
accountId
status
verified
permissions
credit
price
```

Determine whether clients can read or modify fields beyond their intended privilege.

---

# Mass Assignment

Mass assignment occurs when application frameworks automatically bind user-controlled object properties.

Testing model:

```text
Expected Fields
      |
      v
Add Non-UI Field
      |
      v
Server Accepts?
      |
      v
Security-Relevant Property Changed?
```

Use harmless account/profile properties first.

---

# API Versioning

Check:

```text
/v1/
/v2/
/v3/
```

Older API versions may have:

```text
Weaker Authorisation
Missing Rate Limits
Deprecated Authentication
Additional Fields
Legacy Endpoints
```

---

# GraphQL

Common endpoints:

```text
/graphql
/api/graphql
/graphql/v1
```

Check:

```text
Introspection
Schema
Queries
Mutations
Subscriptions
Authorisation
Object Access
Field Access
Aliases
Batching
Depth
Complexity
```

---

# GraphQL Introspection

Where permitted, determine whether introspection is available.

Introspection exposure itself is not necessarily a vulnerability.

The schema is useful for mapping:

```text
Objects
Fields
Queries
Mutations
Arguments
Types
```

---

# GraphQL Authorisation

Do not assume resolver-level authorisation is consistent.

Test:

```text
Same Object via Different Query
Nested Object
Direct Object Query
Mutation
Alternative Field
Different Role
```

---

# GraphQL DoS Safety

Avoid aggressive:

```text
Deeply Nested Queries
Huge Alias Sets
Large Batches
Recursive Queries
```

unless availability testing is explicitly authorised.

---

# gRPC

Identify:

```text
HTTP/2
gRPC Content-Type
Protocol Buffers
Reflection
Service Definitions
```

Security testing should consider:

```text
Authentication
Authorisation
Method Exposure
Message Validation
Metadata
Streaming
Rate Limiting
Reflection
```

Do not assume traditional REST controls automatically apply.

---

# WebSockets

Identify upgrade:

```text
Connection: Upgrade
Upgrade: websocket
```

Test:

```text
Authentication
Authorisation
Origin Validation
Message-Level Access Control
Input Validation
Session Expiry
Reconnect Behaviour
```

---

# WebSocket Model

```text
HTTP Handshake
      |
      v
WebSocket Connection
      |
      v
Messages
      |
      v
Application Actions
```

Authorisation must often be enforced at the message/action level, not only during the handshake.

---

# JWT

JWT structure:

```text
HEADER.PAYLOAD.SIGNATURE
```

Decode for inspection:

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

---

# JWT Checklist

Review:

```text
alg
kid
typ
iss
aud
sub
exp
nbf
iat
jti
roles
scope
permissions
```

Check:

```text
Signature Verification
Algorithm Enforcement
Key Selection
Issuer
Audience
Expiry
Role Trust
Revocation
Key Rotation
```

Do not treat base64 decoding as token compromise.

---

# OAuth 2.0 / OpenID Connect

Map:

```text
Client
Authorisation Server
Resource Server
Redirect URI
State
Nonce
PKCE
Scopes
Tokens
UserInfo
Logout
```

---

# OAuth Testing

Review:

```text
Redirect URI Validation
state
nonce
PKCE
Scope Enforcement
Client Binding
Token Audience
Token Leakage
Account Linking
SSO Session
Open Redirect Interaction
```

---

# OAuth Mental Model

```text
User
 |
 v
Client
 |
 v
Authorisation Server
 |
 v
Code / Token
 |
 v
Client
 |
 v
Resource Server
```

Understand which party trusts which value.

---

# SAML

Review:

```text
Service Provider
Identity Provider
Assertion
Signature
Audience
Recipient
Destination
InResponseTo
NameID
Attributes
Session
```

Prefer dedicated SAML tooling and controlled test identities.

---

# Web LLM Applications

Modern applications may expose LLM-backed functionality through:

```text
Chatbots
Support Assistants
Search
Document Analysis
Agentic Workflows
Tool Calling
RAG
Automated Actions
AI-Powered Scanners
```

---

# LLM Security Model

```text
User Prompt
    |
    v
Model
    |
    +--> System Instructions
    +--> Retrieved Data
    +--> Tools
    +--> APIs
    +--> Internal Services
    |
    v
Application Action
```

The primary security question is not:

```text
Can I make the model say something strange?
```

It is:

```text
Can untrusted input cross a security boundary?
```

---

# LLM Testing Areas

Review:

```text
Direct Prompt Injection
Indirect Prompt Injection
Tool Authorisation
Data Leakage
RAG Poisoning
Cross-User Data Isolation
Sensitive System Prompts
Excessive Agency
Unsafe Output Handling
SSRF Through Tools
Privilege Boundaries
External Content Trust
```

Use harmless instructions and controlled documents.

---

# LLM Tool Calling

For agentic applications ask:

```text
Which tools can the model invoke?

Which arguments can it control?

Does the server independently authorise each action?

Can retrieved content instruct the model?

Can one user influence another user's context?

Can tools access internal services?

Are dangerous actions confirmed?
```

Never assume model instructions are an authorisation boundary.

---

# Secrets Exposure

Search:

```text
JavaScript
Source Maps
Git History
Configuration
Backups
Environment Files
CI/CD Files
Documentation
Error Messages
API Responses
```

Useful local search:

```bash
grep -RniE 'api[_-]?key|secret|token|password|passwd|authorization|bearer' .
```

Validate whether a discovered value is:

```text
Real
Current
Sensitive
In Scope
Privileged
Revoked
Test Data
```

Do not use third-party credentials outside scope.

---

# Dependency Security

Identify:

```text
Framework
Library
Plugin
CMS
Package
Version
```

Then determine:

```text
Is version accurate?

Is component actually reachable?

Is vulnerable feature enabled?

Does configuration mitigate it?

Is authentication required?

Is the known vulnerability applicable?
```

---

# Known Vulnerability Research

Useful sources:

```text
Vendor Advisories
NVD
GitHub Security Advisories
CISA KEV
Exploit-DB
Packet Storm
Project Repositories
Security Research Blogs
```

Prioritise vendor and primary research sources.

---

# searchsploit

```bash
searchsploit nginx
```

Specific product:

```bash
searchsploit 'Apache Tomcat'
```

Do not execute public exploit code without reviewing it.

---

# Nuclei

Basic:

```bash
nuclei -u "$TARGET"
```

List:

```bash
nuclei -l urls.txt
```

Use focused templates where possible.

Treat scanner results as leads requiring validation.

---

# Nikto

```bash
nikto -h "$TARGET"
```

Useful for broad web-server checks, but findings require manual validation.

---

# WAF Detection

Possible tools include:

```text
wafw00f
Nmap
HTTP Response Analysis
```

Example:

```bash
wafw00f "$TARGET"
```

A WAF fingerprint should guide testing, not become a finding by itself.

---

# CDN / Reverse Proxy

Look for:

```text
Cloudflare
Akamai
Fastly
CloudFront
Azure Front Door
Application Gateway
NGINX
HAProxy
Traefik
Varnish
```

Understand:

```text
Client
  |
  v
CDN / WAF
  |
  v
Reverse Proxy
  |
  v
Application
```

Many advanced HTTP vulnerabilities involve disagreement between layers.

---

# Origin Exposure

Assess whether an application behind a CDN/WAF has a directly reachable origin.

Sources can include:

```text
Historical DNS
Certificates
Old Records
Email Headers
Other Subdomains
Infrastructure Reuse
```

Do not attempt to bypass protection unless explicitly authorised.

---

# Server Misconfiguration

Review:

```text
Directory Listing
Default Files
Debug Mode
Verbose Errors
Dangerous Methods
Backup Files
Default Credentials
Exposed Admin Interfaces
Weak TLS
Unnecessary Services
Sensitive Headers
Source Code Exposure
```

---

# Product-Specific Testing

If fingerprinting identifies a product such as:

```text
Apache Tomcat
ActiveMQ
Jenkins
WordPress
Drupal
Next.js
Grafana
GitLab
Confluence
Exchange
WebLogic
JBoss
```

use this workflow:

```text
Fingerprint
    |
    v
Confirm Product
    |
    v
Confirm Version if Possible
    |
    v
Review Vendor Documentation
    |
    v
Review Security Advisories
    |
    v
Check Exposed Features
    |
    v
Determine Applicability
    |
    v
Safe Validation
```

Do not build a finding solely from a banner.

---

# Web Server Fingerprinting

Nmap:

```bash
nmap -sV -p80,443 "$HOST"
```

HTTP scripts:

```bash
nmap -p80,443 --script http-title,http-headers "$HOST"
```

---

# Apache

Check:

```text
Version Disclosure
Directory Listing
server-status
HTTP Methods
Virtual Hosts
Proxy Configuration
CGI
WebDAV
.htaccess Behaviour
```

---

# NGINX

Check:

```text
Version Disclosure
Alias Configuration
Path Normalisation
Reverse Proxy Behaviour
Cache Behaviour
Host Handling
```

---

# IIS

Check:

```text
Version
WebDAV
Short Name Behaviour where relevant
Authentication
Handler Mappings
Static/Dynamic Content
Request Filtering
Error Pages
```

---

# PHP Applications

Look for:

```text
phpinfo()
Exposed Source
Backup Files
Session Configuration
File Inclusion
Upload Handling
Type Juggling
Framework Debug Pages
Composer Metadata
```

Do not assume a PHP application is vulnerable because PHP is used.

---

# Java Applications

Look for:

```text
Tomcat
Spring
Struts
JBoss
WebLogic
JSP
Serialized Objects
Actuator
Error Pages
Management Interfaces
```

---

# .NET Applications

Look for:

```text
ASP.NET
ASP.NET Core
IIS
ViewState
Machine Keys
Debug Information
Trace
Web.config Exposure
Authentication Configuration
```

---

# Node.js Applications

Look for:

```text
Express
Next.js
NestJS
Prototype Pollution
Source Maps
npm Dependencies
Debug Endpoints
Server-Side JavaScript Behaviour
```

---

# Broken Access Control vs Business Logic

Use:

```text
Access Control
    =
Can this identity perform this action?

Business Logic
    =
Should this action be possible in this state?
```

Both should be tested independently.

---

# Input Validation vs Output Encoding

```text
Input Validation
    =
Is supplied data acceptable?

Output Encoding
    =
Is data safely represented in its destination context?
```

Do not treat them as interchangeable.

---

# Client vs Server Trust

```text
Browser
   |
   | Untrusted
   v
Server
```

Values controlled by the client can include:

```text
Price
Role
User ID
Tenant ID
Feature Flags
Hidden Fields
Disabled Fields
JavaScript Variables
Headers
Cookies
```

The server must enforce security-sensitive decisions.

---

# Multi-Tenant Applications

Always test tenant isolation where authorised.

```text
Tenant A
   |
   v
Object A

Tenant B
   |
   v
Object B
```

Check isolation across:

```text
Objects
Users
Files
Exports
Search
APIs
Reports
Invitations
Administration
Billing
Logs
```

---

# File Download Functions

Check:

```text
Authorisation
Path Handling
Filename
Content-Type
Content-Disposition
Caching
Range Requests
Signed URLs
Expiry
Tenant Isolation
```

---

# Export Functions

Exports can reveal more data than the UI.

Check:

```text
CSV
PDF
Excel
JSON
ZIP
Reports
Bulk Exports
```

Compare exported fields with what the user is authorised to view.

---

# Import Functions

Imports may introduce:

```text
File Upload
Parser Vulnerabilities
Formula Injection
Mass Assignment
Business Logic Abuse
Duplicate Processing
External Resource Loading
```

Use harmless test data.

---

# CSV Injection

If user-controlled values are exported to spreadsheets, assess whether spreadsheet formula interpretation creates risk.

Use harmless formula-like test markers.

Do not trigger external commands.

---

# Email Functionality

Review:

```text
Recipient Control
Template Injection
Header Handling
HTML Rendering
Links
Password Reset
Invitations
Verification
Rate Limiting
```

Avoid sending unsolicited messages to real users.

---

# Webhook Security

Check:

```text
URL Validation
SSRF
Authentication
Signature Verification
Replay Protection
Secret Rotation
Event Authorisation
Tenant Isolation
Retry Behaviour
```

---

# Webhook Signature Model

```text
Sender
  |
  v
Signed Event
  |
  v
Receiver
  |
  v
Verify Signature
  |
  v
Verify Timestamp / Replay
  |
  v
Process Event
```

---

# Search Functionality

Search can expose:

```text
SQLi
NoSQLi
LDAP Injection
XSS
Authorisation Issues
Information Leakage
Search Index Leakage
Tenant Isolation Issues
```

Compare results across roles.

---

# Pagination

Manipulate safely:

```text
page
offset
limit
size
cursor
```

Check:

```text
Maximum Limit
Negative Values
Very Large Values
Authorisation Across Pages
Cursor Integrity
```

Avoid resource-exhaustion testing.

---

# Sorting and Filtering

Parameters such as:

```text
sort
order
filter
fields
include
expand
search
q
```

may influence backend queries or expose additional fields.

---

# Hidden Fields

Do not trust:

```html
<input type="hidden">
```

Security decisions must be enforced server-side.

---

# Duplicate Parameters

Applications and proxies may interpret duplicate parameters differently.

Concept:

```text
?id=1&id=2
```

Assess parser behaviour carefully.

This can matter for:

```text
Validation
WAF Behaviour
Caching
Authorisation
Backend Routing
```

---

# Parameter Pollution

Different layers may interpret parameters differently.

```text
Proxy
   |
   v
Framework
   |
   v
Application
```

Check only where there is evidence that parser disagreement may matter.

---

# Encoding

Common encodings:

```text
URL Encoding
Double URL Encoding
HTML Entities
Unicode
Base64
JSON Escaping
XML Entities
```

Encoding is not encryption.

Use encoding variations to understand parser and validation behaviour, not merely to bypass controls.

---

# Normalisation

Check whether components disagree about:

```text
Case
Slashes
Backslashes
Dots
Percent Encoding
Unicode
Duplicate Separators
Trailing Characters
Path Segments
```

Relevant to:

```text
Routing
Access Control
Caching
Path Traversal
Proxy Behaviour
```

---

# HTTP Parameter Locations

Always inspect:

```text
GET Query
POST Form
JSON
XML
Multipart
Headers
Cookies
Path
Fragment - client-side only
```

---

# Response Difference Analysis

When testing a hypothesis compare:

```text
Status Code
Response Length
Word Count
Line Count
Headers
Cookies
Redirect
Body
Timing
Cache Behaviour
```

Do not rely on one signal.

---

# Baseline First

Before fuzzing:

```text
Normal Request
      |
      v
Record Baseline
      |
      v
Change One Variable
      |
      v
Compare
```

Changing one variable at a time makes results easier to interpret.

---

# Safe Proof Principle

Prefer:

```text
Can I prove the issue without:
    accessing unrelated data?
    executing OS commands?
    dumping a database?
    changing another user's password?
    poisoning a shared cache?
    causing downtime?
```

If yes, use the lower-impact proof.

---

# Scanner Result Model

```text
Scanner Finding
      |
      v
Understand Detection
      |
      v
Reproduce Manually
      |
      v
Check Context
      |
      v
Assess Exploitability
      |
      v
Determine Impact
      |
      v
Report
```

---

# False Positives

Common causes:

```text
Generic Error Pages
WAF Responses
Soft 404s
Reflected but Encoded Input
Version Fingerprinting
Rate-Limit Responses
Authentication Redirects
CDN Behaviour
Scanner Heuristics
```

---

# Evidence Directory

```bash
mkdir -p evidence/web/{recon,http,auth,access-control,input,api,business-logic,files,screenshots,requests,responses}
```

Suggested:

```text
evidence/
└── web/
    ├── recon/
    ├── http/
    ├── auth/
    ├── access-control/
    ├── input/
    ├── api/
    ├── business-logic/
    ├── files/
    ├── screenshots/
    ├── requests/
    └── responses/
```

---

# Save HTTP Evidence

Request:

```text
POST /api/example HTTP/1.1
Host: app.example.com
...
```

Response:

```text
HTTP/1.1 200 OK
...
```

Remove:

```text
Passwords
Session Tokens
API Keys
Personal Data
Unrelated Sensitive Data
```

where they are not required for evidence.

---

# Evidence Record

For each confirmed issue record:

```text
Timestamp:
Target:
Endpoint:
Method:
User / Role:
Preconditions:
Request:
Response:
Observed Behaviour:
Expected Behaviour:
Security Impact:
State Changed:
Cleanup:
```

---

# Screenshot Naming

Useful naming:

```text
01-login-page.png
02-user-a-object.png
03-user-b-object-access.png
04-server-response.png
```

Keep screenshots focused.

---

# Reporting

A good web finding explains:

```text
What is wrong?

Where is it?

Who can reach it?

What prerequisites exist?

What can an attacker actually do?

What evidence proves it?

What should be changed?
```

---

# Do Not Overreport

Do not automatically report:

```text
Server Header Present
Technology Detected
Old-Looking Version
Missing Security Header
robots.txt Entry
Swagger Documentation
GraphQL Introspection
WebDAV OPTIONS Response
CORS Header
Open Port
Debug-Looking Path
SPF/DMARC Issue During Web Scope
Cookie Without Attribute
WAF Detected
Directory Exists
```

Determine actual security impact.

---

# Better Finding Model

```text
Observation
    +
Reachability
    +
Prerequisites
    +
Security Boundary
    +
Impact
    =
Finding
```

---

# Example - IDOR

Weak:

```text
The ID parameter can be changed.
```

Better:

```text
An authenticated standard user can modify the object identifier
in the order-details API request and retrieve another test user's
order information because the server does not enforce object-level
authorisation.
```

---

# Example - Technology

Weak:

```text
The application uses Apache.
```

Better:

```text
No finding unless the identified Apache configuration or version
creates a demonstrable security condition relevant to the application.
```

---

# Example - CORS

Weak:

```text
The Origin header is reflected.
```

Better:

```text
Determine whether an attacker-controlled origin can read a
credentialed response containing sensitive information.
```

---

# Example - File Upload

Weak:

```text
PDF files can be uploaded.
```

Better:

```text
Determine whether the upload pipeline permits a file to cross a
security boundary, become publicly accessible, execute, trigger unsafe
server-side processing, or expose other users to active content.
```

---

# Example - Rate Limiting

Weak:

```text
No rate limiting header exists.
```

Better:

```text
Demonstrate whether the security-sensitive operation can be repeated
at a rate that creates a realistic authentication, recovery, abuse,
or resource-consumption risk.
```

---

# Quick Unauthenticated Workflow

```text
Target
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
Technology
  |
  v
404 Fingerprint
  |
  v
robots / sitemap
  |
  v
Content Discovery
  |
  v
Crawl
  |
  v
JavaScript
  |
  v
Parameters
  |
  v
Authentication Surface
  |
  v
Public APIs
  |
  v
Input Testing
  |
  v
Infrastructure Behaviour
```

---

# Quick Authenticated Workflow

```text
Login
  |
  v
Map User Functions
  |
  v
Capture Requests
  |
  v
Session
  |
  v
Authorisation
  |
  v
User A vs User B
  |
  v
Role Boundaries
  |
  v
Business Logic
  |
  v
API
  |
  v
Files / Exports / Imports
  |
  v
Re-Enumerate
```

---

# Multi-Role Workflow

```text
Unauthenticated
      |
      v
User A
      |
      v
User B
      |
      v
Manager
      |
      v
Administrator
```

At every level compare:

```text
Endpoints
Methods
Objects
Fields
Actions
Exports
Search
API
Files
```

---

# API Workflow

```text
Discover API
    |
    v
Documentation
    |
    v
Authentication
    |
    v
Endpoint Inventory
    |
    v
Object IDs
    |
    v
BOLA
    |
    v
Function Authorisation
    |
    v
Property Authorisation
    |
    v
Mass Assignment
    |
    v
Business Logic
    |
    v
Rate Limiting
```

---

# Business Logic Workflow

```text
Understand Intended Process
          |
          v
Identify Invariants
          |
          v
Identify State Transitions
          |
          v
Change Sequence
          |
          v
Change Values
          |
          v
Repeat Actions
          |
          v
Parallelise Carefully
          |
          v
Cross Roles / Accounts
          |
          v
Assess Impact
```

---

# Recon Tool Selection

```text
Subdomains
    -> subfinder / amass

Alive HTTP
    -> httpx

Technology
    -> WhatWeb / Wappalyzer

Content
    -> ffuf / feroxbuster / gobuster

Crawling
    -> Katana / Burp

Historical URLs
    -> gau / waybackurls

Parameters
    -> Arjun / ParamSpider

WAF
    -> wafw00f

Known patterns
    -> Nuclei

Manual HTTP
    -> Burp / curl
```

---

# Vulnerability Tool Selection

```text
SQL Injection
    -> Burp Repeater / sqlmap

Command Injection
    -> Burp Repeater / Commix

XSS
    -> Burp / browser / PortSwigger cheat sheet

Request Smuggling
    -> HTTP Request Smuggler

Cache
    -> Burp / Param Miner

JWT
    -> JWT Editor

Race Conditions
    -> Burp Repeater / Turbo Intruder

GraphQL
    -> Burp / GraphQL Raider

Blind Interactions
    -> Burp Collaborator / approved OAST

General Checks
    -> Nuclei / Nikto
```

Automation should support manual reasoning rather than replace it.

---

# One-Minute Reference

```text
DNS
    dig app.example.com

Headers
    curl -I https://app.example.com

Verbose HTTP
    curl -v https://app.example.com

Technology
    whatweb https://app.example.com

Subdomains
    subfinder -d example.com -silent

Alive
    httpx -l subdomains.txt -status-code -title -tech-detect

Content
    ffuf -w WORDLIST -u https://app.example.com/FUZZ

Crawl
    katana -u https://app.example.com

Historical
    gau example.com

404 fingerprint
    curl -i https://app.example.com/random-928374

TLS
    openssl s_client -connect app.example.com:443 -servername app.example.com

WAF
    wafw00f https://app.example.com

OPTIONS
    curl -i -X OPTIONS https://app.example.com

CORS
    curl -i https://app.example.com -H 'Origin: https://example.invalid'

Nuclei
    nuclei -u https://app.example.com

Nikto
    nikto -h https://app.example.com
```

---

# Master Testing Checklist

## Scope

```text
[ ] Domains
[ ] Subdomains
[ ] IPs
[ ] APIs
[ ] Mobile APIs
[ ] Test accounts
[ ] Roles
[ ] Third parties
[ ] Production restrictions
[ ] Rate restrictions
[ ] OAST restrictions
```

## Reconnaissance

```text
[ ] DNS
[ ] Subdomains
[ ] HTTP services
[ ] Virtual hosts
[ ] Technologies
[ ] WAF/CDN
[ ] TLS
[ ] Error pages
[ ] Favicon
[ ] robots.txt
[ ] sitemap.xml
[ ] security.txt
```

## Attack Surface

```text
[ ] Content discovery
[ ] Crawling
[ ] Historical URLs
[ ] Parameters
[ ] JavaScript
[ ] Source maps
[ ] API documentation
[ ] GraphQL
[ ] WebSockets
[ ] gRPC
[ ] Uploads
[ ] Imports
[ ] Exports
[ ] Webhooks
[ ] Admin interfaces
```

## Authentication

```text
[ ] Login
[ ] Enumeration
[ ] Rate limiting
[ ] Lockout
[ ] Password policy
[ ] Registration
[ ] Email verification
[ ] Password reset
[ ] Account recovery
[ ] MFA
[ ] SSO
[ ] OAuth
[ ] SAML
```

## Session

```text
[ ] Cookie attributes
[ ] Session rotation
[ ] Session fixation
[ ] Logout
[ ] Expiry
[ ] Concurrent sessions
[ ] Password-change invalidation
[ ] MFA-reset invalidation
[ ] Refresh tokens
```

## Authorisation

```text
[ ] Unauthenticated access
[ ] Horizontal access
[ ] Vertical access
[ ] IDOR / BOLA
[ ] Function-level access
[ ] Property-level access
[ ] Tenant isolation
[ ] Method differences
[ ] Hidden endpoints
[ ] Export access
[ ] File access
```

## Input / Injection

```text
[ ] XSS
[ ] DOM-based issues
[ ] HTML injection
[ ] SQL injection
[ ] NoSQL injection
[ ] LDAP injection
[ ] Command injection
[ ] SSTI
[ ] XXE
[ ] SSRF
[ ] Path traversal
[ ] File inclusion
[ ] Deserialization
[ ] Prototype pollution
[ ] Header injection
```

## Files

```text
[ ] Upload validation
[ ] Storage
[ ] Retrieval
[ ] Access control
[ ] Processing
[ ] Image handling
[ ] Archive handling
[ ] PDF generation
[ ] Downloads
[ ] Exports
[ ] Imports
```

## HTTP / Infrastructure

```text
[ ] Host header
[ ] Security headers
[ ] CORS
[ ] CSRF
[ ] Clickjacking
[ ] Open redirect
[ ] Request smuggling
[ ] Cache poisoning
[ ] Cache deception
[ ] WebDAV
[ ] Information disclosure
[ ] Debug interfaces
[ ] Reverse proxy behaviour
```

## Business Logic

```text
[ ] Step skipping
[ ] Step repetition
[ ] Out-of-order actions
[ ] Negative values
[ ] Boundary values
[ ] Limit bypass
[ ] Duplicate actions
[ ] Race conditions
[ ] Rate limits
[ ] Approval workflows
[ ] Client-controlled trust
```

## APIs

```text
[ ] Endpoint inventory
[ ] Authentication
[ ] BOLA
[ ] BFLA
[ ] Property authorisation
[ ] Mass assignment
[ ] Versioning
[ ] Rate limiting
[ ] GraphQL
[ ] WebSockets
[ ] gRPC
```

## Modern Web

```text
[ ] Prototype pollution
[ ] Third-party JavaScript
[ ] Dependency security
[ ] Secrets exposure
[ ] LLM / chatbot security
[ ] Tool calling
[ ] RAG trust boundaries
[ ] Supply-chain exposure
```

## Evidence

```text
[ ] Request saved
[ ] Response saved
[ ] Role recorded
[ ] Preconditions recorded
[ ] Timestamp recorded
[ ] Screenshot focused
[ ] Sensitive values redacted
[ ] State changes recorded
[ ] Cleanup completed
```

---

# Detailed Notes

Use the detailed pages for deeper testing.

```text
web/index.md
web/methodology.md
web/checklist.md
web/attack-surface-analysis.md

web/reconnaissance/index.md
web/reconnaissance/subdomain-enumeration.md
web/reconnaissance/technology-identification.md
web/reconnaissance/content-discovery.md
web/reconnaissance/parameter-discovery.md
web/reconnaissance/javascript-analysis.md

web/burp-suite/extensions.md
web/burp-suite/workflows.md

web/authentication.md
web/authorisation.md
web/idor-bola.md
web/session-management.md
web/password-reset.md
web/mfa.md
web/saml.md

web/xss.md
web/dom-based-vulnerabilities.md
web/html-injection.md
web/csrf.md
web/clickjacking.md
web/cors.md
web/open-redirect.md
web/xs-leaks.md
web/third-party-javascript.md

web/sql-injection.md
web/nosql-injection.md
web/ldap-injection.md
web/command-injection.md
web/ssti.md
web/xxe.md

web/ssrf.md
web/path-traversal.md
web/file-inclusion.md
web/file-upload.md
web/deserialization.md
web/input-validation.md

web/http-security-headers.md
web/http-request-smuggling.md
web/host-header-attacks.md
web/web-cache-poisoning.md
web/web-cache-deception.md
web/information-disclosure.md

web/business-logic.md
web/race-conditions.md
web/rate-limiting.md

web/oauth-oidc.md
web/jwt.md

web/api-security.md
web/graphql.md
web/grpc-security.md
web/websockets.md
web/mass-assignment.md

web/dependency-security.md
web/secrets-exposure.md

web/prototype-pollution.md
web/web-llm-attacks.md
```

Only turn these into clickable internal links after confirming the files exist in the repository.

---

# References

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

Comprehensive methodology for web application and web-service security testing.

---

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

Defensive guidance covering authentication, sessions, input handling, APIs, cryptography, file uploads, OAuth and many other web-security topics.

---

## OWASP API Security

[OWASP API Security Project](https://owasp.org/www-project-api-security/){ target="_blank" rel="noopener noreferrer" }

Useful for API-specific security risks and testing methodology.

---

## PortSwigger Web Security Academy

[Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

High-quality web-security learning material and interactive labs.

---

## PortSwigger Web Security Topics

[Web Security Academy Topics](https://portswigger.net/web-security/all-topics){ target="_blank" rel="noopener noreferrer" }

Useful index covering classic and modern web vulnerability classes.

---

## PortSwigger Web Security Academy - Detailed Materials

[Web Security Academy Detailed Materials](https://portswigger.net/web-security/all-materials/detailed){ target="_blank" rel="noopener noreferrer" }

Detailed testing material including race conditions, APIs, NoSQL injection, cache behaviour and other advanced topics.

---

## PortSwigger XSS Cheat Sheet

[Cross-Site Scripting Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet){ target="_blank" rel="noopener noreferrer" }

Useful context-aware XSS reference.

---

## PortSwigger Burp Documentation

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

Official Burp Suite documentation.

---

## Exploit Notes - Web

[Exploit Notes - Web](https://exploitnotes.org/exploit/web/){ target="_blank" rel="noopener noreferrer" }

Broad practical web-security reference covering vulnerability classes, technologies and assessment techniques.

---

## HackTricks - Web

[HackTricks - Web Pentesting Methodology](https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

Broad web enumeration and testing reference.

---

## PayloadsAllTheThings

[PayloadsAllTheThings](https://swisskyrepo.github.io/PayloadsAllTheThings/){ target="_blank" rel="noopener noreferrer" }

Reference material covering many web vulnerability classes.

---

## InternalAllTheThings

[InternalAllTheThings](https://swisskyrepo.github.io/InternalAllTheThings/){ target="_blank" rel="noopener noreferrer" }

Useful security assessment reference, especially where web applications interact with internal infrastructure and identity systems.

---

## 0xdf Cheatsheets

[0xdf Cheatsheets](https://0xdf.gitlab.io/cheatsheets/){ target="_blank" rel="noopener noreferrer" }

Includes useful enumeration references such as Default 404 Pages.

---

## WhatWeb

[WhatWeb](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }

Web technology fingerprinting tool.

---

## Wappalyzer

[Wappalyzer](https://www.wappalyzer.com/){ target="_blank" rel="noopener noreferrer" }

Technology identification and web application fingerprinting.

---

## Wappalyzer Lookup

[Wappalyzer Technology Lookup](https://www.wappalyzer.com/lookup/){ target="_blank" rel="noopener noreferrer" }

Useful for quickly reviewing detected web technologies.

---

## ProjectDiscovery httpx

[httpx](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }

HTTP probing and web-service metadata collection.

---

## ProjectDiscovery Katana

[Katana](https://github.com/projectdiscovery/katana){ target="_blank" rel="noopener noreferrer" }

Web crawling and endpoint discovery.

---

## ProjectDiscovery Nuclei

[Nuclei](https://github.com/projectdiscovery/nuclei){ target="_blank" rel="noopener noreferrer" }

Template-based security scanning.

---

## ffuf

[ffuf](https://github.com/ffuf/ffuf){ target="_blank" rel="noopener noreferrer" }

Fast web fuzzing and content-discovery tool.

---

## feroxbuster

[feroxbuster](https://github.com/epi052/feroxbuster){ target="_blank" rel="noopener noreferrer" }

Recursive web content-discovery tool.

---

## SecLists

[SecLists](https://github.com/danielmiessler/SecLists){ target="_blank" rel="noopener noreferrer" }

Useful wordlists for content discovery, fuzzing and security testing.

---

## Arjun

[Arjun](https://github.com/s0md3v/Arjun){ target="_blank" rel="noopener noreferrer" }

HTTP parameter discovery.

---

## ParamSpider

[ParamSpider](https://github.com/devanshbatham/ParamSpider){ target="_blank" rel="noopener noreferrer" }

Parameter-oriented URL discovery.

---

## gau

[gau](https://github.com/lc/gau){ target="_blank" rel="noopener noreferrer" }

Fetches known URLs from several historical/public sources.

---

## waybackurls

[waybackurls](https://github.com/tomnomnom/waybackurls){ target="_blank" rel="noopener noreferrer" }

Historical URL discovery from the Wayback Machine.

---

## sqlmap

[sqlmap](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }

Automated SQL injection testing tool. Use after manual evidence indicates SQL injection.

---

## Commix

[Commix](https://github.com/commixproject/commix){ target="_blank" rel="noopener noreferrer" }

Automated command-injection assessment tool.

---

## wafw00f

[wafw00f](https://github.com/EnableSecurity/wafw00f){ target="_blank" rel="noopener noreferrer" }

Web Application Firewall fingerprinting.

---

## Nikto

[Nikto](https://github.com/sullo/nikto){ target="_blank" rel="noopener noreferrer" }

Web-server assessment scanner.

---

## MDN HTTP

[MDN HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP){ target="_blank" rel="noopener noreferrer" }

Excellent reference for HTTP semantics, headers, methods, cookies, caching and browser behaviour.

---

## curl

[curl Documentation](https://curl.se/docs/){ target="_blank" rel="noopener noreferrer" }

Official curl documentation.

---

## Mozilla Web Security Guidelines

[Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security){ target="_blank" rel="noopener noreferrer" }

Useful defensive web-security configuration reference.

---

# Final Testing Model

Do not test web applications as:

```text
Run WhatWeb
    |
    v
Run Directory Scanner
    |
    v
Run Nuclei
    |
    v
Run Payload Lists
    |
    v
Report Scanner Output
```

Use:

```text
                         WEB APPLICATION
                                |
                                v
                              SCOPE
                                |
                                v
                        RECONNAISSANCE
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
         Subdomains         Technology          Content
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                         ATTACK SURFACE
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
       Authentication      Authorisation       Input
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                         BUSINESS LOGIC
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
            API             Client Side       HTTP Layers
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                          HYPOTHESIS
                                |
                                v
                         MANUAL TEST
                                |
                                v
                         REPRODUCIBLE?
                                |
                          +-----+-----+
                          |           |
                         No          Yes
                          |           |
                          v           v
                       Discard     IMPACT
                                      |
                                      v
                              MINIMUM SAFE PROOF
                                      |
                                      v
                                  EVIDENCE
                                      |
                                      v
                                   REPORT
```

The goal is not:

```text
How many payloads can I send?
```

The goal is:

```text
How does this application establish trust,
and can an untrusted user cross one of those
security boundaries?
```

A strong web assessment therefore combines:

```text
Reconnaissance
      +
Protocol Understanding
      +
Application Understanding
      +
Role Comparison
      +
Business Logic
      +
Manual Validation
      +
Minimal Evidence
      =
Defensible Security Finding
```
