# Attack Surface Analysis

Attack Surface Analysis is the process of identifying, mapping, classifying, and prioritising the parts of an application or system that may be exposed to an attacker.

The goal is to understand:

```text
What can an attacker reach?

What can an attacker control?

What data enters the application?

What data leaves the application?

Which interfaces are exposed?

Which functions require authentication?

Which functions require elevated privileges?

Where are trust boundaries crossed?

Which components protect sensitive data?

Which areas deserve the most security testing?
```

A simplified model is:

```text
                    ATTACKER
                       |
                       v
              EXTERNAL ATTACK SURFACE
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
     Web UI           APIs         Services
        |              |              |
        +--------------+--------------+
                       |
                       v
                  APPLICATION
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
    Databases       Internal       Third-Party
                    Services        Services
```

Attack Surface Analysis should be performed before and during detailed vulnerability testing.

It helps answer:

```text
Where should I test?

What have I not tested?

Which parts are highest risk?

Which assets or interfaces may have been forgotten?
```

!!! warning "Authorised Security Testing"
    Attack Surface Analysis can involve DNS enumeration, crawling, content discovery, port identification, virtual-host discovery, API enumeration, JavaScript analysis, parameter discovery, and other reconnaissance techniques. Only perform active discovery against assets explicitly covered by the authorised scope and rules of engagement. Passive discovery may reveal related infrastructure that is not authorised for active testing.

---

# Why Attack Surface Analysis Matters

A penetration test can only assess what the tester discovers.

Consider:

```text
Known Application
       |
       v
https://www.example.com
```

But the organisation may also operate:

```text
api.example.com
admin.example.com
old.example.com
staging.example.com
files.example.com
auth.example.com
```

If testing covers only:

```text
www.example.com
```

then significant parts of the attack surface may remain untested.

Conceptually:

```text
Incomplete Discovery
        |
        v
Incomplete Testing
        |
        v
Potential Vulnerabilities Missed
```

OWASP therefore treats attack-surface identification and application mapping as important information-gathering activities before deeper testing.

---

# What Is an Attack Surface?

The attack surface consists of the points where an attacker may interact with a system or where data crosses a security boundary.

For a web application this may include:

```text
Domains
Subdomains
Virtual hosts
IP addresses
Ports
Web applications
URLs
API endpoints
Parameters
HTTP headers
Cookies
Forms
File uploads
WebSockets
GraphQL
gRPC
Authentication interfaces
Administrative interfaces
Third-party integrations
Cloud storage
Callbacks
Webhooks
Background services
```

It also includes the valuable data and security controls associated with these interfaces.

---

# Entry Points

An entry point is a location through which data or commands enter the application.

Examples:

```text
GET parameters
POST parameters
JSON properties
XML elements
HTTP headers
Cookies
File uploads
GraphQL arguments
WebSocket messages
gRPC messages
Path parameters
API tokens
OAuth callbacks
SAML responses
Webhooks
Email
Imported files
```

Conceptually:

```text
Untrusted Input
      |
      v
Entry Point
      |
      v
Application Logic
      |
      v
Sensitive Operation
```

Every entry point is a potential security-testing target.

---

# Exit Points

Attack Surface Analysis should also consider where information leaves the application.

Examples:

```text
HTTP responses
API responses
File downloads
Redirects
Error messages
Logs
Email
Webhooks
External API calls
Analytics
Cloud storage
Exports
Reports
```

Conceptually:

```text
Sensitive Data
      |
      v
Application
      |
      v
Exit Point
      |
      v
External Consumer
```

Exit points are particularly relevant to:

```text
Information disclosure
SSRF
Open redirects
Data exfiltration
Logging exposure
Third-party data sharing
```

---

# Attack Surface vs Attack Vector

These terms are related but different.

Attack surface:

```text
All possible places an attacker could interact
with or influence the system.
```

Attack vector:

```text
A particular path or technique used to attack
the system.
```

Example:

```text
Attack Surface:

File upload functionality
```

Possible attack vectors:

```text
Malicious file upload
Stored XSS through filename
Path traversal through filename
Content-type confusion
Parser exploitation
```

---

# Attack Surface vs Vulnerability

An exposed feature is not automatically vulnerable.

For example:

```text
/admin
```

is part of the attack surface.

It becomes a security finding only if there is an actual security weakness, such as:

```text
Missing authentication
Broken authorisation
Default credentials
Information disclosure
```

Therefore:

```text
Attack Surface
      !=
Vulnerability
```

Attack Surface Analysis identifies where vulnerabilities may exist.

---

# Attack Surface vs Reconnaissance

Reconnaissance discovers information.

Attack Surface Analysis organises that information into a security model.

Example:

```text
Subfinder
   |
   v
150 subdomains
```

is reconnaissance.

Then:

```text
150 subdomains
     |
     v
Identify live systems
     |
     v
Classify applications
     |
     v
Identify authentication
     |
     v
Identify admin systems
     |
     v
Identify APIs
     |
     v
Prioritise testing
```

is Attack Surface Analysis.

---

# External Attack Surface

The external attack surface contains assets reachable from outside the organisation or trust boundary.

Examples:

```text
Internet-facing websites
APIs
VPN gateways
Authentication portals
Cloud applications
Public storage
Mail gateways
Remote access
CDNs
Public repositories
DNS infrastructure
```

For web testing, the primary focus is often:

```text
Internet
   |
   v
Domains
   |
   v
Applications
   |
   v
Endpoints
   |
   v
Parameters
```

---

# Internal Attack Surface

The internal attack surface may include:

```text
Internal applications
Administrative interfaces
Internal APIs
Databases
Message queues
Monitoring systems
Developer portals
CI/CD
Internal package repositories
Management services
```

The internal and external attack surfaces may differ substantially.

An authenticated employee or compromised internal host may have access to interfaces unavailable from the Internet.

---

# Authenticated Attack Surface

Authentication often reveals additional functionality.

Example:

```text
Unauthenticated
      |
      +-- /
      +-- /login
      +-- /register
      +-- /forgot-password

Authenticated User
      |
      +-- /profile
      +-- /orders
      +-- /documents
      +-- /api/account

Administrator
      |
      +-- /admin
      +-- /api/admin
      +-- /reports
      +-- /users
```

Therefore attack-surface mapping should be performed across different roles.

---

# Role-Based Attack Surface

Build a role matrix.

Example:

```text
Endpoint              Anonymous   User   Manager   Admin
--------------------------------------------------------
/login                    Y         Y       Y        Y
/profile                  N         Y       Y        Y
/orders                   N         Y       Y        Y
/reports                  N         N       Y        Y
/admin                    N         N       N        Y
/api/users                N         N       N        Y
```

This immediately creates testing opportunities for:

```text
Broken access control
IDOR / BOLA
Privilege escalation
Forced browsing
Function-level authorisation
```

---

# High-Privilege Attack Surface

OWASP recommends paying particular attention to privilege extremes.

Important roles include:

```text
Anonymous user
Lowest privileged authenticated user
Normal user
Privileged user
Administrator
System administrator
Service account
```

The highest privileged interfaces often provide the greatest potential impact.

---

# Attack Surface Layers

A useful model is:

```text
Level 1
Infrastructure

Level 2
Applications

Level 3
Interfaces

Level 4
Endpoints

Level 5
Parameters

Level 6
Business Operations

Level 7
Data
```

For example:

```text
api.example.com
      |
      v
REST API
      |
      v
/api/users/{id}
      |
      v
id
      |
      v
Retrieve user
      |
      v
Personal information
```

---

# Layer 1: Infrastructure

Identify infrastructure exposed to the application.

Examples:

```text
IP addresses
Ports
Protocols
Load balancers
Reverse proxies
CDNs
WAFs
Web servers
API gateways
Ingress controllers
Cloud services
```

Architecture may resemble:

```text
Internet
   |
   v
CDN
   |
   v
WAF
   |
   v
Load Balancer
   |
   v
Reverse Proxy
   |
   v
Application
   |
   v
Database
```

Understanding these layers can explain unexpected behaviour during testing.

---

# Layer 2: Applications

One organisation may expose many separate applications.

Examples:

```text
Main website
Customer portal
Partner portal
Admin portal
Mobile API
Legacy application
Developer portal
Documentation
Authentication service
```

Each application may have a different:

```text
Technology stack
Authentication mechanism
Development team
Security maturity
Deployment lifecycle
```

---

# Layer 3: Interfaces

Applications may expose different interface types.

Examples:

```text
HTML
REST
GraphQL
WebSocket
gRPC
SOAP
XML-RPC
File transfer
Webhook
OAuth
SAML
```

Each interface introduces different testing requirements.

---

# Layer 4: Endpoints

Endpoints include:

```text
/login
/register
/profile
/api/users
/api/orders
/graphql
/upload
/download
/admin
```

Do not focus only on visible navigation.

Important endpoints may be:

```text
Unlinked
Legacy
Referenced only by JavaScript
Mobile-only
API-only
Administrative
Debug-related
```

---

# Layer 5: Parameters

Parameters are critical attack-surface elements.

Example:

```http
GET /api/user?id=123 HTTP/1.1
```

Attack surface:

```text
Endpoint:
/api/user

Parameter:
id
```

Potential test categories include:

```text
IDOR
Injection
Type confusion
Parameter pollution
Business logic
```

---

# Layer 6: Business Operations

Endpoints should also be mapped to business actions.

Examples:

```text
Transfer money
Create account
Reset password
Change email
Add administrator
Generate invoice
Upload document
Delete user
Approve payment
Apply discount
```

Business operations are often more important than individual URLs.

---

# Layer 7: Data

Identify valuable data.

Examples:

```text
Credentials
Session tokens
API keys
Personal data
Financial data
Documents
Source code
Intellectual property
Customer records
Payment information
Recovery codes
```

Then map:

```text
Where is it entered?

Where is it stored?

Where is it returned?

Who can access it?

Which systems receive it?
```

---

# Attack Surface Categories

A practical classification model is:

```text
Network Surface
Application Surface
API Surface
Authentication Surface
Authorisation Surface
Input Surface
File Surface
Client-Side Surface
Administrative Surface
Data Surface
Third-Party Surface
Cloud Surface
Development Surface
```

---

# Network Surface

Map:

```text
Hosts
IP addresses
Ports
Protocols
TLS services
Virtual hosts
```

For a web application:

```text
443/tcp HTTPS
80/tcp HTTP
8443/tcp Admin?
8080/tcp Alternate application?
```

Non-standard ports should not automatically be treated as vulnerabilities.

They are discovery targets.

---

# Domain Surface

Start with the authorised root domain.

Example:

```text
example.com
```

Possible related assets:

```text
www.example.com
api.example.com
auth.example.com
admin.example.com
dev.example.com
staging.example.com
cdn.example.com
files.example.com
```

---

# Passive Subdomain Discovery

Useful sources include:

```text
Certificate Transparency
Search engines
DNS datasets
Public archives
Public repositories
Passive DNS
```

Tools commonly used include:

```text
subfinder
amass
assetfinder
```

Example:

```bash
subfinder -d example.com -silent
```

Save:

```bash
subfinder -d example.com \
  -silent \
  -o subdomains.txt
```

!!! warning
    Discovery of a hostname does not automatically place it in scope. Apply the engagement's scope rules before active probing.

---

# Certificate Transparency

Certificate Transparency can reveal hostnames contained in public certificates.

Conceptually:

```text
Certificate
     |
     v
Subject Alternative Names
     |
     +-- www.example.com
     +-- api.example.com
     +-- auth.example.com
```

CT is particularly useful for passive discovery.

---

# DNS Resolution

After collecting authorised hostnames:

```bash
dnsx -l subdomains.txt -silent
```

This can help determine which names currently resolve.

A DNS record existing does not prove that an application is alive.

---

# HTTP Probing

For authorised targets:

```bash
httpx -l subdomains.txt \
  -silent
```

Useful enrichment may include:

```bash
httpx -l subdomains.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect
```

This helps transform:

```text
DNS inventory
```

into:

```text
HTTP application inventory
```

---

# Keep Reconnaissance Stages Separate

A useful pipeline is:

```text
Subdomain Discovery
       |
       v
subdomains.txt
       |
       v
DNS Resolution
       |
       v
resolved.txt
       |
       v
HTTP Probing
       |
       v
alive-web.txt
```

Do not treat:

```text
Discovered
```

as equivalent to:

```text
Resolvable
```

or:

```text
HTTP alive
```

---

# Virtual Hosts

Multiple applications may share one IP address.

Conceptually:

```text
               203.0.113.10
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
 www.example   api.example   admin.example
```

Requesting:

```text
https://203.0.113.10/
```

may not reveal these applications.

The correct hostname may be required.

This is why OWASP includes virtual-host identification in attack-surface discovery.

---

# Non-Standard Ports

Applications may run on:

```text
80
443
8080
8443
8000
8888
```

or other ports.

Where infrastructure scanning is explicitly authorised, identify exposed services rather than assuming all web applications use 80/443.

---

# Application Architecture Mapping

Attack Surface Analysis should produce an architecture model.

Example:

```text
                     Internet
                        |
                        v
                       CDN
                        |
                        v
                       WAF
                        |
                        v
                  Load Balancer
                        |
              +---------+---------+
              |                   |
              v                   v
          Frontend             API Gateway
              |                   |
              |             +-----+-----+
              |             |           |
              v             v           v
          Web App        User API    Order API
              |             |           |
              +-------------+-----------+
                            |
                            v
                         Database
```

OWASP's WSTG recommends understanding the application's architecture and technologies because these components influence both security and testing scope.

---

# Architecture Questions

Ask:

```text
Where does TLS terminate?

Is there a CDN?

Is there a WAF?

Is there a reverse proxy?

Is there an API gateway?

Are there multiple application servers?

Where does authentication occur?

Where is authorisation enforced?

Which systems store sensitive data?

Which external services are used?

Which internal services are reachable?
```

---

# Trust Boundaries

A trust boundary exists where data moves between systems or security contexts with different trust assumptions.

Example:

```text
Internet
   |
   | Trust Boundary
   v
Web Application
   |
   | Trust Boundary
   v
Internal API
   |
   | Trust Boundary
   v
Database
```

Every boundary deserves review.

---

# Common Trust Boundaries

Examples:

```text
Browser -> Web application

Web application -> API

API -> Database

Application -> Cloud storage

Application -> Third-party service

User -> Administrator functionality

Internet -> Internal network

Tenant A -> Tenant B

Container -> Host
```

---

# Entry Point Identification

OWASP WSTG recommends analysing requests and responses to identify application entry points.

During normal browsing, capture:

```text
GET parameters
POST parameters
JSON
XML
Headers
Cookies
Path parameters
Multipart fields
File uploads
HTTP methods
```

Example:

```http
POST /api/profile HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "displayName": "Alice",
  "email": "alice@example.com"
}
```

Entry points:

```text
displayName
email
```

---

# HTTP Method Mapping

Record methods used by endpoints:

```text
GET
POST
PUT
PATCH
DELETE
OPTIONS
HEAD
```

Example:

```text
GET     /api/users/123
PUT     /api/users/123
DELETE  /api/users/123
```

The same route may expose significantly different functionality through different methods.

---

# OPTIONS

Where supported, an authorised request such as:

```http
OPTIONS /api/users/123 HTTP/1.1
Host: target.example
```

may provide information about permitted methods.

Do not assume the `Allow` header provides a complete or security-relevant method inventory.

Verify actual application behaviour.

---

# Hidden Parameters

Applications may accept parameters not visible in the normal UI.

Example:

```http
POST /profile

name=Alice
```

but backend code may also accept:

```text
role
admin
isVerified
accountType
```

This creates potential attack surface for:

```text
Mass assignment
Privilege escalation
Business logic vulnerabilities
```

---

# Param Miner

Burp's BApp Store contains:

```text
Param Miner
```

which can help identify hidden parameters and related input behaviours.

It is particularly useful for discovering unlinked:

```text
Headers
Cookies
Parameters
```

that may influence application behaviour.

BApp Store:

```text
https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943
```

Use results as discovery leads and manually verify behaviour.

---

# ParaForge

The BApp Store also contains:

```text
ParaForge
```

which can extract parameters and endpoints from observed requests to help create customised wordlists.

This can be useful when building an application-specific attack-surface dictionary.

Check the current BApp Store before installation:

```text
https://portswigger.net/bappstore
```

---

# Burp Proxy Mapping

Burp Proxy should be one of the primary tools for application-level Attack Surface Analysis.

Workflow:

```text
Browser
   |
   v
Burp Proxy
   |
   v
Application
   |
   v
HTTP History
   |
   v
Attack Surface Inventory
```

Browse every accessible feature and role.

Record:

```text
Host
Method
Path
Parameters
Authentication
Role
Content type
Response type
Function
```

---

# Burp Target Site Map

Burp's Target site map helps visualise discovered content.

It can reveal:

```text
Hosts
Directories
Endpoints
Parameters
Requests
Responses
```

A useful workflow is:

```text
Browse manually
      |
      v
Populate Site Map
      |
      v
Review untested branches
      |
      v
Discover additional content
      |
      v
Update attack-surface map
```

---

# Burp Scope

Configure Burp's target scope before extensive testing.

This helps separate:

```text
In-scope traffic
```

from:

```text
Third-party traffic
Analytics
CDNs
External services
Out-of-scope infrastructure
```

This is particularly important when automated functionality is enabled.

---

# Burp Crawler and Scanner

Where authorised and available, Burp's automated crawling can supplement manual mapping.

However:

```text
Crawler
```

does not guarantee:

```text
Complete attack surface
```

Applications may contain:

```text
Role-specific functionality
Hidden APIs
JavaScript-only routes
Mobile endpoints
Unlinked content
Business workflows
```

Manual analysis remains necessary.

---

# Content Discovery

Hidden content may significantly increase the attack surface.

Examples:

```text
/admin
/backup
/debug
/internal
/api
/swagger
/openapi.json
/graphql
/actuator
/metrics
/health
```

Content discovery should use application-specific wordlists where possible.

Refer to:

```text
docs/web/reconnaissance/content-discovery.md
```

---

# robots.txt

Review:

```text
/robots.txt
```

Example:

```text
User-agent: *
Disallow: /admin/
Disallow: /internal/
```

`robots.txt` is not an access-control mechanism.

It may provide discovery clues.

---

# sitemap.xml

Review:

```text
/sitemap.xml
```

It may reveal:

```text
Application routes
Legacy pages
Unlinked content
Localised routes
```

---

# security.txt

Review:

```text
/.well-known/security.txt
```

This is generally not an attack vector itself but can provide security-contact and disclosure-policy information.

---

# Common Metadata Files

Depending on the application, useful discovery targets may include:

```text
/robots.txt
/sitemap.xml
/.well-known/security.txt
/manifest.json
/openapi.json
/swagger.json
```

Do not blindly assume every file should exist.

---

# JavaScript Attack Surface

Modern web applications frequently expose much of their functionality through JavaScript.

JavaScript may reveal:

```text
API endpoints
Hidden routes
Feature flags
Parameter names
WebSocket URLs
GraphQL endpoints
Internal hostnames
Third-party services
Authentication flows
```

Therefore:

```text
JavaScript Analysis
```

is a major part of attack-surface mapping.

---

# Collect JavaScript

Burp can identify JavaScript responses.

Other approaches include:

```text
Browser DevTools
Crawlers
Katana
Manual HTML analysis
```

Example:

```bash
katana -u https://target.example \
  -jc \
  -silent
```

Use active crawling only within authorised scope and rate limits.

---

# Search JavaScript

After collecting authorised JavaScript:

```bash
rg -n \
'/api/|https?://|wss?://|graphql|admin|upload|download' \
js/
```

This can reveal candidate attack-surface elements.

---

# JS Link Finder

Burp's BApp Store contains:

```text
JS Link Finder
```

which passively scans JavaScript for endpoint links.

It can help identify:

```text
API paths
Hidden routes
External services
Unlinked endpoints
```

BApp Store:

```text
https://portswigger.net/bappstore
```

The BApp Store entry should be checked before installation because extension versions and maintenance status can change.

---

# JS Miner

Another useful Burp extension is:

```text
JS Miner
```

It analyses static files, particularly JavaScript and JSON, for potentially interesting information.

Useful discoveries may include:

```text
URLs
Endpoints
Configuration
Interesting strings
Potential secrets
```

Treat all output as leads requiring validation.

---

# Source Maps

Look for:

```text
//# sourceMappingURL=
```

Source maps may reveal:

```text
Original source files
Route definitions
API clients
Internal modules
Comments
Configuration
```

Refer to:

```text
docs/web/reconnaissance/javascript-analysis.md
```

---

# API Attack Surface

APIs frequently expose more functionality than the graphical user interface.

Example:

```text
Web UI
   |
   v
/api/profile
/api/orders
```

but JavaScript may reveal:

```text
/api/admin/users
/api/export
/api/internal/search
/api/v2/accounts
```

Therefore always map APIs independently.

---

# REST API Mapping

Record:

```text
Method
Path
Parameters
Authentication
Role
Request content type
Response content type
Business function
```

Example:

```text
GET    /api/users/{id}
POST   /api/users
PATCH  /api/users/{id}
DELETE /api/users/{id}
```

---

# OpenAPI

Look for authorised access to API descriptions such as:

```text
/openapi.json
/openapi.yaml
/swagger.json
/api-docs
```

An OpenAPI document can provide a highly useful attack-surface inventory.

It may contain:

```text
Endpoints
Methods
Parameters
Schemas
Authentication
Response models
```

---

# OpenAPI Is Not Automatically Sensitive

Public API documentation may be intentional.

The security value is:

```text
Attack-surface discovery
```

not automatically:

```text
Information disclosure vulnerability
```

Assess whether genuinely sensitive or unintended information is exposed.

---

# GraphQL

GraphQL may consolidate significant functionality into:

```text
/graphql
```

The URL count may be small while the logical attack surface is large.

Conceptually:

```text
/graphql
   |
   +-- Queries
   +-- Mutations
   +-- Fields
   +-- Arguments
   +-- Types
```

Therefore endpoint counting alone can underestimate the attack surface.

Refer to:

```text
docs/web/graphql.md
```

---

# WebSockets

WebSocket functionality creates persistent message-based attack surface.

Example:

```text
wss://target.example/socket
```

Map:

```text
Handshake
Authentication
Message types
Actions
Identifiers
Authorisation
```

Refer to:

```text
docs/web/websockets.md
```

---

# gRPC

gRPC may expose services and methods rather than conventional REST paths.

Conceptually:

```text
gRPC Server
    |
    +-- UserService
    |      |
    |      +-- GetUser
    |      +-- UpdateUser
    |
    +-- AdminService
           |
           +-- CreateUser
```

Attack Surface Analysis should therefore inventory:

```text
Services
Methods
Messages
Metadata
Authentication
```

Refer to:

```text
docs/web/grpc-security.md
```

---

# Authentication Attack Surface

Identify every authentication-related function.

Examples:

```text
/login
/register
/logout
/forgot-password
/reset-password
/mfa
/oauth/callback
/saml
/api/login
```

Do not assume there is only one authentication mechanism.

Applications may support:

```text
Password
SSO
OAuth
OIDC
SAML
Magic link
API key
Client certificate
```

---

# Password Reset Surface

Map:

```text
Reset request
      |
      v
Token generation
      |
      v
Email
      |
      v
Reset endpoint
      |
      v
Password change
```

Every step creates potential attack surface.

Refer to:

```text
docs/web/password-reset.md
```

---

# MFA Surface

Map:

```text
MFA enrolment
MFA verification
MFA reset
Recovery codes
Backup methods
Trusted devices
```

MFA bypasses frequently occur in surrounding workflows rather than the OTP verification algorithm itself.

Refer to:

```text
docs/web/mfa.md
```

---

# OAuth and OIDC Surface

Map:

```text
Authorization endpoint
Token endpoint
Redirect URI
Callback
state
nonce
PKCE
Scopes
Claims
```

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# SAML Surface

Map:

```text
Identity Provider
Service Provider
ACS endpoint
Metadata
SAMLResponse
RelayState
Logout
```

Refer to:

```text
docs/web/saml.md
```

---

# Authorisation Attack Surface

Attack Surface Analysis should identify:

```text
Objects
Actions
Roles
Permissions
Identifiers
```

Example:

```text
User
 |
 +-- View own profile
 +-- Edit own profile
 +-- View own invoices

Admin
 |
 +-- View all users
 +-- Edit users
 +-- Delete users
```

Then test whether these boundaries are enforced server-side.

---

# Object Inventory

Identify objects such as:

```text
Users
Orders
Invoices
Documents
Projects
Tickets
Messages
Accounts
Tenants
API keys
```

Then identify object references:

```text
id=123
user_id=42
/order/5001
/document/abc123
```

This creates an IDOR/BOLA testing map.

---

# Administrative Attack Surface

Administrative functionality deserves special attention.

Examples:

```text
/admin
/management
/dashboard
/console
/internal
/support
/operator
```

Admin functionality may expose:

```text
User management
Role management
Configuration
Logs
File access
Exports
System commands
Integration settings
Secrets
```

---

# Hidden Administrative Interfaces

Administrative interfaces may exist on:

```text
Separate subdomain
Separate port
Separate path
VPN-only service
Internal network
```

Example:

```text
admin.example.com
management.example.com:8443
```

Do not actively test internal or excluded interfaces unless they are part of the authorised scope.

---

# File Attack Surface

Map every place files can enter or leave the system.

Examples:

```text
Avatar upload
Document upload
CSV import
ZIP import
PDF upload
Image upload
Attachment
Report download
Export
Backup restore
```

Potential vulnerability classes include:

```text
File upload vulnerabilities
Path traversal
Parser vulnerabilities
Stored XSS
XXE
Archive extraction issues
Information disclosure
```

---

# Upload Flow Mapping

Example:

```text
User
 |
 v
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
Download / Rendering
```

Test each stage independently.

Refer to:

```text
docs/web/file-upload.md
```

---

# Download Attack Surface

Map parameters controlling file retrieval.

Example:

```http
GET /download?file=report.pdf
```

Potential areas include:

```text
Path traversal
IDOR
Authorisation
Information disclosure
Content-Disposition handling
```

---

# Search Functions

Search interfaces are high-value entry points because they process user-controlled data.

Examples:

```text
/search?q=
/api/search
/graphql search
```

Potential testing areas:

```text
SQL injection
NoSQL injection
LDAP injection
SSTI
XSS
Business logic
Denial of service
```

---

# Import and Export Functions

Imports:

```text
CSV
XML
JSON
ZIP
Excel
```

Exports:

```text
CSV
PDF
Excel
JSON
Reports
```

These features may introduce:

```text
Parser attack surface
Formula injection
XXE
File handling
Information disclosure
Authorisation issues
```

---

# HTTP Headers

Headers are also input channels.

Examples:

```text
Host
Origin
Referer
X-Forwarded-For
X-Forwarded-Host
User-Agent
Content-Type
Authorization
Accept-Language
```

Some applications trust proxy-related headers unexpectedly.

Refer to:

```text
docs/web/host-header-attacks.md
docs/web/cors.md
```

---

# Cookies

Map every cookie.

Record:

```text
Name
Purpose
Domain
Path
Secure
HttpOnly
SameSite
```

Determine whether the cookie controls:

```text
Session
Role
Preference
Feature
Tenant
Authentication state
```

Never assume a cookie is merely cosmetic.

---

# Client-Side Attack Surface

The browser introduces its own attack surface.

Examples:

```text
DOM
JavaScript
Web Storage
postMessage
Web Workers
Service Workers
IndexedDB
Third-party scripts
WebSockets
```

Relevant vulnerability classes include:

```text
XSS
DOM vulnerabilities
Prototype pollution
XS-Leaks
Third-party JavaScript risk
```

---

# Third-Party Attack Surface

Applications often depend on external services.

Examples:

```text
Payment provider
Analytics
Support chat
CAPTCHA
Maps
CDN
Authentication provider
Email service
Cloud storage
```

Map:

```text
What data is sent?

What trust exists?

Can the third party call back?

Does it execute JavaScript?

What credentials are used?

What happens if it is unavailable?
```

Refer to:

```text
docs/web/third-party-javascript.md
```

---

# Webhooks

Webhooks create server-to-server attack surface.

Example:

```text
Third Party
    |
    v
POST /webhook/payment
    |
    v
Application
```

Review:

```text
Authentication
Signature validation
Replay protection
Input validation
Idempotency
Source assumptions
```

Do not attack the third-party sender unless explicitly authorised.

---

# Callback URLs

Applications may accept callback or destination URLs.

Examples:

```text
webhook_url
callback
redirect_uri
return_url
image_url
feed_url
```

These parameters may introduce:

```text
SSRF
Open redirect
OAuth issues
Webhook abuse
```

---

# Cloud Attack Surface

Modern web applications may expose cloud resources.

Examples:

```text
Object storage
CDNs
Serverless endpoints
API gateways
Cloud load balancers
Managed databases
Secrets managers
Container registries
```

A web assessment should record discovered cloud-related infrastructure even when cloud-platform testing itself is outside scope.

---

# Storage Attack Surface

Examples:

```text
S3-style object storage
Azure Blob Storage
Google Cloud Storage
CDN origins
File shares
```

Determine whether the application exposes:

```text
Public objects
Signed URLs
Upload URLs
Download URLs
Bucket names
Container names
```

Do not enumerate unrelated cloud resources unless authorised.

---

# Development Attack Surface

Development infrastructure can sometimes become externally exposed.

Examples:

```text
Git repositories
CI/CD
Artifact repositories
Package registries
Debug endpoints
Source maps
Staging systems
Developer portals
```

These may contain:

```text
Source code
Secrets
Build artifacts
Internal documentation
```

---

# Environment Discovery

Look for environment indicators such as:

```text
dev
development
test
testing
qa
uat
staging
stage
preprod
prod
production
```

Example:

```text
dev.example.com
staging.example.com
api-test.example.com
```

A non-production environment is not automatically authorised simply because it shares the target's parent domain.

---

# Legacy Attack Surface

Legacy functionality often increases risk.

Examples:

```text
/v1/
/old/
/legacy/
/backup/
/api/v1/
```

OWASP specifically notes that old or backward-compatible interfaces can increase attack-surface risk because older protocols and code may be harder to maintain.

---

# Backup Attack Surface

Backups can expose:

```text
Source code
Credentials
Databases
Configuration
Personal data
```

Potentially interesting filenames may include:

```text
backup.zip
site.tar.gz
database.sql
config.old
index.php.bak
```

Discovery of exposed backups should be handled carefully because downloaded data may contain sensitive information.

Collect only the minimum evidence necessary.

---

# Error Surface

Error handling can expose additional information.

Examples:

```text
Stack traces
Filesystem paths
SQL errors
Framework versions
Internal hostnames
Debug information
```

Errors can reveal hidden architecture and components.

Refer to:

```text
docs/web/information-disclosure.md
```

---

# Business Logic Attack Surface

Attack Surface Analysis should map workflows, not only endpoints.

Example:

```text
Add Item
   |
   v
Apply Discount
   |
   v
Checkout
   |
   v
Payment
   |
   v
Refund
```

Potential vulnerabilities may occur between steps.

Examples:

```text
Skip payment
Reuse discount
Negative quantity
Multiple refund
Race condition
State manipulation
```

---

# Workflow Mapping

For each important business function, record:

```text
Preconditions
User role
Steps
Endpoints
Parameters
State transitions
Sensitive actions
Expected restrictions
```

Example:

```text
Password Change

1. Authenticate
2. Open settings
3. Submit current password
4. Submit new password
5. Session handling
6. Notification
```

Each step becomes part of the attack surface.

---

# State Machine

Some applications are best represented as states.

Example:

```text
CREATED
   |
   v
PENDING
   |
   v
APPROVED
   |
   v
PAID
   |
   v
COMPLETED
```

Security testing should ask:

```text
Can states be skipped?

Can transitions occur backwards?

Can a low-privileged user trigger privileged transitions?

Can concurrent requests corrupt the state?
```

---

# Map Execution Paths

OWASP recommends understanding principal application workflows and execution paths.

Example:

```text
/login
   |
   v
/dashboard
   |
   v
/order
   |
   v
/payment
   |
   v
/confirmation
```

Documenting these paths helps demonstrate which application functionality was actually tested.

---

# Attack Surface Inventory

A useful inventory might contain:

```text
Asset
Host
Path
Method
Interface
Authentication
Role
Parameters
Data
Technology
Risk
Test Status
Notes
```

Example:

```text
Host:
api.example.com

Endpoint:
/api/users/{id}

Method:
GET

Authentication:
Bearer token

Roles:
User / Admin

Input:
id

Data:
User profile

Risk:
High

Testing:
IDOR, authorisation, input validation
```

---

# Attack Surface Table

Example:

| Asset | Interface | Auth | Role | Function | Risk |
|---|---|---|---|---|---|
| `/login` | Web | No | Anonymous | Authentication | High |
| `/api/users/{id}` | REST | Yes | User | User data | High |
| `/upload` | Web | Yes | User | File upload | High |
| `/admin` | Web | Yes | Admin | Administration | Critical |
| `/health` | HTTP | No | Anonymous | Monitoring | Low |

Risk should be determined by context rather than endpoint name alone.

---

# Risk Classification

OWASP recommends prioritising high-risk areas.

Common high-risk categories include:

```text
Internet-facing interfaces
Anonymous functionality
Authentication
Authorisation
Administrative interfaces
File handling
Custom APIs
Sensitive data
Security controls
Legacy interfaces
External integrations
```

---

# Risk Scoring Model

A simple internal prioritisation model can use:

```text
Exposure
Privilege
Data sensitivity
Function sensitivity
Input complexity
Technology
History
```

For example:

```text
Exposure

0 = Internal
1 = Authenticated external
2 = Anonymous external

Privilege

0 = Low
1 = Normal
2 = Administrative

Data

0 = Public
1 = Internal
2 = Sensitive

Function

0 = Read-only
1 = Modification
2 = Security-critical
```

Then:

```text
Priority Score =
Exposure +
Privilege +
Data +
Function
```

This is not a vulnerability severity score.

It is only a way to prioritise testing effort.

---

# Example

```text
/admin/users

Exposure: 1
Privilege: 2
Data: 2
Function: 2

Score: 7
```

versus:

```text
/about

Exposure: 2
Privilege: 0
Data: 0
Function: 0

Score: 2
```

The administrative function should receive more intensive testing.

---

# Do Not Confuse Attack Surface Score With CVSS

Attack-surface prioritisation answers:

```text
Where should we focus testing?
```

CVSS attempts to describe characteristics of a discovered vulnerability.

They serve different purposes.

---

# Attack Surface Reduction

Attack Surface Analysis should also identify unnecessary exposure.

Examples:

```text
Unused endpoint
Old API
Unused subdomain
Legacy admin portal
Unnecessary port
Deprecated integration
Unused JavaScript
Old environment
```

Conceptually:

```text
Feature no longer needed
        |
        v
Still exposed
        |
        v
Unnecessary attack surface
```

---

# Remove Unused Features

OWASP recommends reducing attack surface where possible.

For example:

```text
Unused API
    |
    v
Disable
```

rather than:

```text
Unused API
    |
    v
Leave available indefinitely
```

---

# Feature Flags

Disabled features may still be reachable.

Example:

```text
UI hides feature
```

but:

```text
/api/feature
```

still works.

Therefore test whether feature flags are enforced:

```text
Client-side only
```

or:

```text
Server-side
```

---

# Hidden Does Not Mean Protected

Examples:

```text
No menu link
Obscure URL
JavaScript hidden
robots.txt disallow
Feature flag
```

None of these replace:

```text
Authentication
Authorisation
```

---

# Attack Surface Drift

Attack surfaces change over time.

Example:

```text
Version 1

10 endpoints
```

then:

```text
Version 2

15 endpoints
New API
New third party
New admin role
```

Security teams should ask:

```text
What changed?
```

OWASP specifically recommends reassessing risk when the attack surface changes.

---

# Change Detection

Useful events include:

```text
New subdomain
New endpoint
New role
New API version
New integration
New port
New cloud resource
New file type
New authentication method
```

These should trigger appropriate security review.

---

# Continuous Attack Surface Management

A mature process looks like:

```text
Discover
   |
   v
Inventory
   |
   v
Classify
   |
   v
Prioritise
   |
   v
Test
   |
   v
Remediate
   |
   v
Monitor
   |
   +------+
          |
          v
       Discover
```

Attack Surface Analysis is therefore not necessarily a one-time penetration-testing task.

---

# Differential Analysis

Comparing attack surfaces between releases can be valuable.

Example:

```text
Previous Release
       |
       v
attack-surface-old.txt

Current Release
       |
       v
attack-surface-new.txt
```

Then:

```bash
diff \
  attack-surface-old.txt \
  attack-surface-new.txt
```

New entries become review candidates.

---

# URL Normalisation

Before comparing endpoint inventories, normalise them.

For example:

```text
/api/user/123
/api/user/456
/api/user/789
```

may represent one logical route:

```text
/api/user/{id}
```

Otherwise endpoint counts can become misleading.

---

# Simple Endpoint Extractor

For an authorised Burp-exported or crawler-generated URL list:

```python
#!/usr/bin/env python3

import sys
from urllib.parse import urlsplit, parse_qsl


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <urls.txt>")
    sys.exit(1)

seen = set()

with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        url = line.strip()

        if not url:
            continue

        try:
            parsed = urlsplit(url)
        except ValueError:
            continue

        parameters = sorted(
            set(name for name, _ in parse_qsl(
                parsed.query,
                keep_blank_values=True
            ))
        )

        key = (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            tuple(parameters)
        )

        if key in seen:
            continue

        seen.add(key)

        params = ",".join(parameters) if parameters else "-"

        print(
            f"{parsed.scheme}://{parsed.netloc}"
            f"{parsed.path} | params={params}"
        )
```

Save as:

```text
attack_surface_urls.py
```

Usage:

```bash
python3 attack_surface_urls.py urls.txt
```

This helps convert large URL collections into a more manageable endpoint inventory.

---

# Parameter Inventory Script

A simple helper:

```python
#!/usr/bin/env python3

from collections import defaultdict
from urllib.parse import urlsplit, parse_qsl
import sys


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <urls.txt>")
    sys.exit(1)

parameters = defaultdict(set)

with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        url = line.strip()

        if not url:
            continue

        try:
            parsed = urlsplit(url)
        except ValueError:
            continue

        endpoint = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        for name, _ in parse_qsl(
            parsed.query,
            keep_blank_values=True
        ):
            parameters[endpoint].add(name)

for endpoint in sorted(parameters):
    print(endpoint)

    for parameter in sorted(parameters[endpoint]):
        print(f"  - {parameter}")
```

Usage:

```bash
python3 parameter_inventory.py urls.txt
```

---

# Crawl Data

Useful sources for endpoint inventories include:

```text
Burp
Katana
Application sitemap
OpenAPI
JavaScript
Browser history
Server logs
Source code
```

Combining sources generally gives better coverage than relying on one crawler.

---

# Katana

For authorised crawling:

```bash
katana \
  -u https://target.example \
  -silent
```

JavaScript crawling can be enabled where appropriate:

```bash
katana \
  -u https://target.example \
  -jc \
  -silent
```

Set depth, rate, and other options according to the engagement.

Always review:

```bash
katana -h
```

against the installed version because command options can evolve.

---

# Historical URLs

Historical URL sources may reveal:

```text
Old endpoints
Removed parameters
Legacy APIs
Old file names
Deprecated functionality
```

Tools such as:

```text
waybackurls
urlfinder
```

can assist with passive or archive-based discovery.

Historical presence does not prove that an endpoint currently exists.

---

# waybackurls

Example:

```bash
echo example.com \
| waybackurls
```

Then:

```bash
echo example.com \
| waybackurls \
| sort -u \
> historical-urls.txt
```

Only actively request URLs if they fall within authorised scope.

---

# Parameter Discovery

Parameters can come from:

```text
Burp traffic
JavaScript
Historical URLs
OpenAPI
Forms
GraphQL
Mobile APIs
Source code
```

Refer to:

```text
docs/web/reconnaissance/parameter-discovery.md
```

---

# Wordlist Generation

Application-specific wordlists are often more effective than generic lists.

Sources include:

```text
Observed paths
JavaScript strings
API names
Parameter names
Technology names
Business terminology
```

Example:

```text
invoice
customer
account
claim
document
export
```

These can guide controlled content discovery.

---

# White-Box Attack Surface Analysis

With source-code access, mapping becomes more precise.

Search for:

```text
Routes
Controllers
Endpoints
API definitions
Authentication middleware
Authorisation checks
File handlers
Templates
WebSockets
GraphQL resolvers
gRPC services
```

Conceptually:

```text
Source Code
    |
    v
Route Definitions
    |
    v
Attack Surface
```

---

# Route Mapping

Examples by technology may include searching for framework-specific route declarations.

The exact patterns depend on:

```text
Language
Framework
Version
Application architecture
```

Do not assume one regex can correctly identify every route.

---

# Compare Source Routes With Runtime Routes

A powerful approach is:

```text
Source Route Inventory
          |
          v
Compare
          |
          v
Runtime Route Inventory
```

Differences may reveal:

```text
Dead code
Unreachable routes
Undocumented endpoints
Environment-specific features
Reverse-proxy routing
```

---

# Security Middleware Mapping

Identify where:

```text
Authentication
Authorisation
CSRF
Validation
Rate limiting
Logging
```

are applied.

Example:

```text
/api/public
    |
    v
No authentication middleware

/api/account
    |
    v
Authentication middleware

/api/admin
    |
    v
Authentication
+
Admin authorisation
```

This helps identify inconsistent protection.

---

# Input-to-Sink Mapping

For white-box analysis:

```text
Entry Point
    |
    v
Transformation
    |
    v
Validation
    |
    v
Sensitive Sink
```

Example:

```text
HTTP parameter
      |
      v
Controller
      |
      v
Service
      |
      v
SQL query
```

This connects Attack Surface Analysis with taint analysis and vulnerability discovery.

---

# Microservices

Microservice architectures create distributed attack surfaces.

Example:

```text
Internet
   |
   v
API Gateway
   |
   +-----------+-----------+
   |           |           |
   v           v           v
User       Orders       Payment
Service    Service      Service
```

Not every service is necessarily directly exposed.

Prioritise components reachable from the relevant attacker position.

OWASP specifically notes that cloud-native environments may place services behind:

```text
Proxies
Load balancers
Ingress controllers
Service meshes
```

---

# Internal Microservice Surface

Even if:

```text
payment-service
```

is not Internet-facing, it may still matter if:

```text
Compromised frontend
      |
      v
Internal service
```

is a realistic attack path.

Attack surface therefore depends on the attacker model.

---

# Kubernetes

Cloud-native environments may contain:

```text
Ingress
Services
Pods
Service mesh
Internal APIs
Load balancers
```

Application testing should understand which components are externally reachable and which are internal.

Do not perform cluster-level testing unless explicitly authorised.

---

# Threat Modelling Relationship

Attack Surface Analysis and threat modelling reinforce each other.

```text
Attack Surface Analysis
        |
        v
What is exposed?
        |
        v
Threat Modelling
        |
        v
How could it be attacked?
        |
        v
Attack Surface Review
```

Changes to the attack surface should trigger threat review.

---

# Coverage Tracking

A penetration test should track what was actually assessed.

Example:

```text
Endpoint              Discovered   Tested
------------------------------------------
/login                    Y          Y
/profile                  Y          Y
/upload                   Y          Y
/admin                    Y          N
/api/export               Y          N
```

This makes gaps explicit.

---

# Test Status

Useful states include:

```text
Discovered
Mapped
In Scope
Out of Scope
Tested
Partially Tested
Not Tested
Blocked
Not Reachable
```

This is more informative than a simple list of URLs.

---

# Attack Surface Coverage

A simple metric might be:

```text
Tested High-Risk Functions
--------------------------
Known High-Risk Functions
```

However:

```text
100% endpoint count
```

does not prove:

```text
100% security coverage
```

because endpoints vary greatly in complexity.

---

# Common Mapping Mistakes

## Only Testing Visible Links

This misses:

```text
APIs
JavaScript routes
Admin functionality
Hidden content
Historical endpoints
```

---

## Only Running a Crawler

Crawlers may miss:

```text
Authenticated workflows
Role-specific functionality
Complex state
API-only endpoints
Unlinked routes
```

---

## Only Enumerating Subdomains

Subdomains are only one level of the attack surface.

You still need:

```text
Applications
Endpoints
Parameters
Roles
Data
Business functions
```

---

## Treating Every Discovered Asset as In Scope

This is dangerous.

Discovery:

```text
related.example.com
```

does not automatically equal:

```text
authorised target
```

Apply scope rules before active testing.

---

## Treating Every Endpoint Equally

A public static page and an administrative user-management API should not receive identical testing effort.

Prioritise by risk.

---

## Ignoring Authenticated Areas

Unauthenticated mapping alone frequently misses most application functionality.

Map every authorised role.

---

## Ignoring Business Workflows

Testing isolated endpoints can miss vulnerabilities involving:

```text
State
Order
Timing
Role transitions
Multi-step processes
```

---

# Evidence Collection

Attack Surface Analysis evidence may include:

```text
Subdomain inventory
Resolved hostnames
Live HTTP services
Port inventory
Technology inventory
Burp site map
Endpoint list
Parameter list
Role matrix
API specification
JavaScript endpoints
Architecture diagram
Trust-boundary diagram
Data-flow diagram
Coverage matrix
```

---

# Example Attack Surface Record

```text
Asset:
api.example.com

Interface:
REST API

Endpoint:
PATCH /api/users/{id}

Authentication:
Bearer token

Roles:
User
Administrator

Inputs:
id
displayName
email

Sensitive data:
Email
Profile information

Trust boundary:
Internet -> API

Potential test categories:
IDOR
BOLA
Mass assignment
Input validation
Rate limiting
Business logic

Status:
Mapped
```

---

# Example Finding: Unnecessary Legacy Interface

```text
Finding:
Legacy Application Interface Remains Externally Accessible

Observed:
An older application interface remains reachable from the Internet despite no longer being required for normal business operations.

The interface exposes functionality that duplicates features available through the current application.

Impact:
Maintaining unused externally accessible functionality increases the application's attack surface and creates additional components that require patching, monitoring, authentication, authorisation, and security testing.

Recommendation:
Remove or disable the legacy interface if it is no longer required. If continued access is necessary, restrict exposure to authorised users and networks and include the interface in normal security maintenance and testing processes.
```

---

# Example Finding: Exposed Administrative Interface

```text
Finding:
Administrative Interface Exposed to the Internet

Observed:
The application exposes an administrative management interface directly to the Internet.

Authentication is required and no authentication bypass was demonstrated during testing.

Impact:
Internet exposure increases the opportunity for attacks against the administrative authentication mechanism and any vulnerabilities present in the management application.

Recommendation:
Where operationally possible, restrict administrative interfaces to trusted management networks, VPN access, or other appropriately controlled access paths. Maintain strong MFA and monitoring for privileged access.
```

This should not automatically be rated High merely because an admin interface exists.

Context matters.

---

# Example Finding: Deprecated API Version

```text
Finding:
Deprecated API Version Remains Accessible

Observed:
The application continues to expose an older API version alongside the current API.

Example:

/api/v1/
/api/v2/

The older API remains functional.

Impact:
Legacy API versions increase the application attack surface and may not receive the same security improvements or testing coverage as current functionality.

Recommendation:
Remove deprecated API versions when clients no longer require them. Where continued support is necessary, apply equivalent authentication, authorisation, validation, monitoring, and security testing to all supported versions.
```

---

# Example Finding: Unauthenticated Sensitive Endpoint

```text
Finding:
Sensitive Application Endpoint Accessible Without Authentication

Observed:
Attack Surface Analysis identified an unlinked endpoint that returns sensitive application information without requiring authentication.

Impact:
An unauthenticated attacker may access information that should be restricted to authorised users.

Recommendation:
Enforce authentication and appropriate server-side authorisation before returning sensitive information. Review similar endpoints for inconsistent access-control enforcement.
```

---

# Example Finding: Unused Public Subdomain

```text
Finding:
Unused Publicly Accessible Application Increases External Attack Surface

Observed:
A publicly resolvable subdomain hosts an application that appears to be obsolete and is not linked from the organisation's current services.

The application remains externally accessible.

Impact:
Forgotten or unused applications can receive less maintenance and monitoring while remaining available to attackers.

Recommendation:
Confirm whether the application is still required. Decommission unnecessary assets and remove associated DNS records and infrastructure after verifying that they are no longer needed.
```

---

# Reporting Attack Surface Observations

Not every attack-surface item needs to become a vulnerability.

Useful assessment documentation may include:

```text
Attack Surface Overview

Hosts discovered:
25

Web applications:
8

API hosts:
3

Administrative interfaces:
2

Authentication mechanisms:
2

External integrations:
7

High-risk functions:
12
```

This can help communicate assessment coverage.

---

# Finding Titles

Useful titles include:

```text
Legacy Application Interface Remains Externally Accessible

Deprecated API Version Remains Accessible

Unused Public Application Increases Attack Surface

Administrative Interface Exposed to the Internet

Unnecessary Service Exposed Externally

Unlinked Sensitive Endpoint Accessible Without Authentication

Legacy Authentication Interface Remains Enabled

Unused Third-Party Integration Increases Attack Surface

Development Environment Exposed Externally

Debug Interface Exposed in Production

Sensitive Management Endpoint Exposed Externally
```

---

# Remediation Principles

Attack-surface remediation generally follows:

```text
Remove
Restrict
Isolate
Authenticate
Authorise
Validate
Monitor
Maintain
```

---

# Remove

If functionality is not required:

```text
Disable it
Remove it
Decommission it
```

This is often stronger than attempting to secure unused functionality indefinitely.

---

# Restrict

Where public access is unnecessary:

```text
VPN
Management network
Firewall
Identity-aware proxy
Access control
```

may reduce exposure.

Architecture should reflect the application's operational requirements.

---

# Isolate

Separate sensitive components from lower-trust systems.

Example:

```text
Internet
   |
   v
Frontend
   |
   v
API
   |
   X
Direct database access
```

Use appropriate network and application boundaries.

---

# Authenticate

Sensitive functionality should require appropriate authentication.

But remember:

```text
Authentication
```

does not replace:

```text
Authorisation
```

---

# Authorise

Every sensitive object and action should enforce server-side authorisation.

Refer to:

```text
docs/web/authorisation.md
docs/web/idor-bola.md
```

---

# Validate

All untrusted input crossing entry points should be validated according to its expected structure and semantics.

Refer to:

```text
docs/web/input-validation.md
```

---

# Monitor

High-risk attack-surface components should generate useful security telemetry.

Examples:

```text
Authentication failures
Administrative actions
Access-control failures
Sensitive exports
Configuration changes
API abuse
```

---

# Maintain

Every exposed component requires:

```text
Patching
Dependency management
Configuration management
Monitoring
Security testing
```

Therefore unnecessary components create recurring security cost.

---

# Pentesting Checklist

## Scope

```text
[ ] Scope reviewed
[ ] Root domains identified
[ ] IP ranges identified where applicable
[ ] Explicit exclusions recorded
[ ] Third-party assets identified
[ ] Rules for discovered assets understood
```

---

## External Assets

```text
[ ] Domains enumerated
[ ] Subdomains enumerated
[ ] DNS records reviewed
[ ] Certificate Transparency considered
[ ] Live HTTP services identified
[ ] Virtual hosts considered
[ ] Non-standard ports considered where authorised
```

---

## Applications

```text
[ ] Main application mapped
[ ] Admin applications mapped
[ ] APIs mapped
[ ] Legacy applications considered
[ ] Development environments considered
[ ] Staging environments considered
[ ] Mobile backends considered
```

---

## Architecture

```text
[ ] CDN identified
[ ] WAF identified
[ ] Reverse proxy identified
[ ] Load balancer identified
[ ] API gateway identified
[ ] Application servers understood
[ ] Authentication system understood
[ ] External services identified
[ ] Trust boundaries mapped
```

---

## Endpoints

```text
[ ] Visible routes mapped
[ ] Hidden routes considered
[ ] Content discovery performed
[ ] robots.txt reviewed
[ ] sitemap.xml reviewed
[ ] API documentation reviewed
[ ] JavaScript endpoints reviewed
[ ] Historical endpoints considered
```

---

## Parameters

```text
[ ] Query parameters mapped
[ ] Form parameters mapped
[ ] JSON properties mapped
[ ] XML elements mapped
[ ] Path parameters mapped
[ ] Headers mapped
[ ] Cookies mapped
[ ] Hidden parameters considered
[ ] File fields mapped
```

---

## Authentication

```text
[ ] Login mapped
[ ] Registration mapped
[ ] Logout mapped
[ ] Password reset mapped
[ ] MFA mapped
[ ] OAuth/OIDC mapped
[ ] SAML mapped
[ ] API authentication mapped
```

---

## Authorisation

```text
[ ] Roles identified
[ ] Permissions identified
[ ] Objects identified
[ ] Object identifiers mapped
[ ] Administrative functions identified
[ ] Role matrix created
```

---

## APIs

```text
[ ] REST mapped
[ ] GraphQL considered
[ ] WebSockets considered
[ ] gRPC considered
[ ] SOAP considered
[ ] API versions identified
[ ] OpenAPI documentation checked
```

---

## Files

```text
[ ] Upload functions mapped
[ ] Import functions mapped
[ ] Download functions mapped
[ ] Export functions mapped
[ ] Backup functionality considered
```

---

## Client Side

```text
[ ] JavaScript inventoried
[ ] External scripts identified
[ ] Source maps checked
[ ] DOM functionality reviewed
[ ] postMessage reviewed
[ ] Web Storage considered
[ ] Service Workers considered
[ ] Third-party JavaScript identified
```

---

## Business Logic

```text
[ ] Important workflows mapped
[ ] State transitions documented
[ ] Financial actions identified
[ ] Account actions identified
[ ] Privileged operations identified
[ ] Multi-step workflows identified
```

---

## Data

```text
[ ] Sensitive data identified
[ ] Entry points identified
[ ] Storage locations understood where possible
[ ] Exit points identified
[ ] Third-party data flows considered
```

---

## Attack Surface Reduction

```text
[ ] Legacy interfaces identified
[ ] Unused applications identified
[ ] Deprecated APIs identified
[ ] Unnecessary ports identified
[ ] Unused third parties identified
[ ] Old environments identified
[ ] Debug interfaces identified
```

---

## Coverage

```text
[ ] Discovered assets recorded
[ ] In-scope assets marked
[ ] Out-of-scope assets marked
[ ] Tested endpoints recorded
[ ] Untested endpoints recorded
[ ] Blocked functionality recorded
[ ] High-risk areas prioritised
```

---

# Burp Suite Workflow

A practical Burp workflow is:

```text
1. Configure Target Scope
        |
        v
2. Browse Application
        |
        v
3. Populate Site Map
        |
        v
4. Review HTTP History
        |
        v
5. Map Hosts
        |
        v
6. Map Endpoints
        |
        v
7. Map Parameters
        |
        v
8. Map Authentication
        |
        v
9. Map Roles
        |
        v
10. Analyse JavaScript
        |
        v
11. Identify Hidden Inputs
        |
        v
12. Identify High-Risk Functions
        |
        v
13. Track Test Coverage
```

Useful Burp capabilities include:

```text
Proxy
Target Site Map
Repeater
Comparer
Logger
Search
Crawler
Scanner
```

Relevant optional BApps include:

```text
Param Miner
ParaForge
JS Link Finder
JS Miner
```

Do not install extensions unnecessarily on sensitive engagements. BApps are third-party code and should be reviewed before use.

---

# Quick Recon Workflow

For an authorised domain:

```text
example.com
    |
    v
subfinder
    |
    v
subdomains.txt
    |
    v
dnsx
    |
    v
resolved hosts
    |
    v
httpx
    |
    v
live web applications
    |
    v
katana / Burp
    |
    v
URLs
    |
    v
JavaScript analysis
    |
    v
API / parameter discovery
    |
    v
Attack Surface Inventory
```

Example:

```bash
subfinder \
  -d example.com \
  -silent \
  -o subdomains.txt
```

Then:

```bash
dnsx \
  -l subdomains.txt \
  -silent \
  -o resolved.txt
```

Then:

```bash
httpx \
  -l resolved.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect \
  -o alive-web.txt
```

Then perform crawling only against the authorised targets selected from the resulting inventory.

---

# Attack Surface Analysis Workflow

```text
                  AUTHORISED SCOPE
                         |
                         v
                    DISCOVERY
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
        DNS            HTTP         Historical
          |              |              |
          +--------------+--------------+
                         |
                         v
                       ASSETS
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Web Apps         APIs          Services
          |              |              |
          +--------------+--------------+
                         |
                         v
                    ARCHITECTURE
                         |
                         v
                  TRUST BOUNDARIES
                         |
                         v
                    ENTRY POINTS
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Routes         Parameters       Files
          |              |              |
          +--------------+--------------+
                         |
                         v
                       ROLES
                         |
                         v
                 BUSINESS FUNCTIONS
                         |
                         v
                    SENSITIVE DATA
                         |
                         v
                     PRIORITISE
                         |
                         v
                       TEST
                         |
                         v
                 COVERAGE REVIEW
```

---

# Final Testing Model

```text
                        ATTACK SURFACE
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
           ASSETS          INTERFACES         DATA
             |                |                |
      +------+------+    +----+----+      +----+----+
      |      |      |    |    |    |      |         |
      v      v      v    v    v    v      v         v
    DNS    Hosts   Apps  Web  API  Files  Input    Output
      |      |      |    |    |    |      |         |
      +------+------+    +----+----+      +----+----+
             |                |                |
             v                v                v
        ARCHITECTURE      ENTRY POINTS      DATA FLOW
             |                |                |
             +----------------+----------------+
                              |
                              v
                       TRUST BOUNDARIES
                              |
                              v
                            ROLES
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
          Anonymous          User           Admin
              |               |               |
              +---------------+---------------+
                              |
                              v
                     BUSINESS FUNCTIONS
                              |
                              v
                         PRIORITISATION
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       Exposure            Privilege          Data Value
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                           TESTING
                              |
                              v
                       COVERAGE REVIEW
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                  GAPS              FINDINGS
                    |                   |
                    v                   v
                MORE TESTING       REMEDIATION
                                        |
                                        v
                              ATTACK SURFACE REDUCTION
                                        |
                                        v
                                   MONITORING
```

The central principle is:

> **You cannot meaningfully assess the security of an application until you understand what the application exposes, who can reach it, what data crosses its boundaries, and which functionality matters most.**

For every discovered attack-surface element ask:

```text
What is it?

Who owns it?

Is it in scope?

Who can reach it?

Does it require authentication?

Which roles can use it?

What inputs does it accept?

What data does it return?

What business function does it perform?

What sensitive data does it handle?

Which trust boundary does it cross?

What technology implements it?

Is it still required?

Is it legacy?

Is there another version?

Is there an administrative equivalent?

Is it referenced by JavaScript?

Is it documented by an API specification?

What other services does it communicate with?

What happens if an attacker controls its input?

What happens if its authorisation fails?

Has it actually been tested?
```

A strong attack-surface analysis therefore combines:

```text
Scope Review
      +
Subdomain Discovery
      +
DNS Analysis
      +
HTTP Probing
      +
Technology Identification
      +
Content Discovery
      +
Burp Mapping
      +
JavaScript Analysis
      +
API Enumeration
      +
Parameter Discovery
      +
Role Mapping
      +
Workflow Mapping
      +
Architecture Mapping
      +
Trust-Boundary Analysis
      +
Sensitive-Data Mapping
      +
Coverage Tracking
```

The result should not simply be:

```text
A giant list of URLs
```

It should become:

```text
A structured model of what can be attacked,
how it can be reached,
what it protects,
and where security testing should focus.
```

---

# References

## OWASP Attack Surface Analysis Cheat Sheet

[OWASP Attack Surface Analysis Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Attack_Surface_Analysis_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Web Security Testing Guide - Information Gathering

[OWASP Web Security Testing Guide - Information Gathering](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/01-Information_Gathering/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP WSTG - Attack Surface Identification

[OWASP WSTG - Attack Surface Identification](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/01-Information_Gathering/04-Attack_Surface_Identification/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP WSTG - Identify Application Entry Points

[OWASP WSTG - Identify Application Entry Points](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/01-Information_Gathering/06-Identify_Application_Entry_Points/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP WSTG - Map Execution Paths Through Application

[OWASP WSTG - Map Execution Paths Through Application](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/01-Information_Gathering/07-Map_Execution_Paths_Through_Application/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP WSTG - Map Application Architecture

[OWASP WSTG - Map Application Architecture](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/01-Information_Gathering/10-Map_Application_Architecture/){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger Burp Target Scope

[PortSwigger Burp Target Scope](https://portswigger.net/burp/documentation/desktop/tools/target/scope){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger Burp Target Site Map

[PortSwigger Burp Target Site Map](https://portswigger.net/burp/documentation/desktop/tools/target/site-map){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger BApp Store

[PortSwigger BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery Subfinder

[ProjectDiscovery Subfinder](https://github.com/projectdiscovery/subfinder){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery DNSX

[ProjectDiscovery DNSX](https://github.com/projectdiscovery/dnsx){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery HTTPX

[ProjectDiscovery HTTPX](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery Katana

[ProjectDiscovery Katana](https://github.com/projectdiscovery/katana){ target="_blank" rel="noopener noreferrer" }

---

# Related Notes

```text
docs/web/methodology.md
docs/web/checklist.md

docs/web/reconnaissance/index.md
docs/web/reconnaissance/subdomain-enumeration.md
docs/web/reconnaissance/technology-identification.md
docs/web/reconnaissance/content-discovery.md
docs/web/reconnaissance/parameter-discovery.md
docs/web/reconnaissance/javascript-analysis.md

docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md

docs/web/authentication.md
docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/mfa.md

docs/web/file-upload.md
docs/web/information-disclosure.md
docs/web/business-logic.md
docs/web/race-conditions.md

docs/web/dependency-security.md
docs/web/secrets-exposure.md
docs/web/third-party-javascript.md
```
