# HTTP Host Header Attacks

HTTP Host header attacks occur when an application, reverse proxy, cache, load balancer, or another infrastructure component incorrectly trusts attacker-controlled host information.

The HTTP `Host` header tells the receiving server which hostname the client wants to access.

Example:

```http
GET / HTTP/1.1
Host: target.example
```

Modern infrastructure frequently hosts multiple applications behind the same:

```text
IP address
Reverse proxy
Load balancer
CDN
API gateway
Web server
```

The `Host` header can therefore influence:

```text
Application routing
Virtual host selection
Absolute URL generation
Password reset links
Redirects
Cache keys
Backend routing
Security decisions
Internal service access
```

The central security question is:

> What happens when attacker-controlled host information reaches application logic or infrastructure that assumes it can be trusted?

A simplified attack model is:

```text
Attacker
   ↓
Manipulated Host Information
   ↓
Proxy / CDN / Load Balancer
   ↓
Application
   ↓
Host Value Trusted
   ↓
Security-Relevant Behaviour
```

Potential consequences include:

```text
Password reset poisoning
Web cache poisoning
Routing-based SSRF
Access control bypass
Internal virtual host access
Open redirects
Incorrect absolute URLs
Business logic manipulation
Unexpected backend routing
```

!!! warning "Authorised Security Testing"
    Perform Host header testing only against systems included in the authorised assessment scope. Be particularly careful with cache poisoning, password reset workflows, backend routing and out-of-band interactions because they can affect other users or infrastructure.

---

# What Is the Host Header?

HTTP/1.1 requests normally contain a `Host` header.

Example:

```http
GET /account HTTP/1.1
Host: target.example
```

The server may use this value to determine which application should process the request.

Consider a server hosting:

```text
www.example.com
api.example.com
admin.example.com
support.example.com
```

All four may resolve to the same infrastructure.

The server needs some way to determine which application the client intended to reach.

Conceptually:

```text
Client
   ↓
Shared IP Address
   ↓
Reverse Proxy
   ↓
Read Host Header
   ↓
Select Application
```

---

# Virtual Hosting

Virtual hosting allows multiple websites to share the same server or IP address.

For example:

```text
203.0.113.10
      ↓
   Web Server
      ↓
 ┌────┼────┐
 ↓    ↓    ↓
www  api  admin
```

Requests may contain:

```http
Host: www.example.com
```

or:

```http
Host: api.example.com
```

The infrastructure uses the supplied hostname to select the appropriate virtual host.

---

# Reverse Proxies

A common modern architecture is:

```text
Internet
   ↓
CDN
   ↓
Load Balancer
   ↓
Reverse Proxy
   ↓
Application
```

Different components may interpret host information differently.

For example:

```text
CDN
 ↓
Host

Reverse Proxy
 ↓
X-Forwarded-Host

Application
 ↓
Framework Request Host
```

This creates opportunities for inconsistencies.

---

# Why Host Header Vulnerabilities Occur

The underlying problem is usually:

```text
User-Controlled Header
        ↓
Application Assumes Trusted
        ↓
Security-Relevant Operation
```

Developers sometimes assume:

```text
Host = server configuration
```

when in reality:

```text
Host = request input
```

An attacker can modify it.

---

# Basic Testing Methodology

A structured Host header workflow looks like:

```text
Baseline Request
      ↓
Modify Host
      ↓
Observe Response
      ↓
Test Host Override Headers
      ↓
Check Reflection
      ↓
Check Redirects
      ↓
Check Absolute URLs
      ↓
Check Password Reset
      ↓
Check Cache Behaviour
      ↓
Check Routing
      ↓
Check Internal Virtual Hosts
      ↓
Check OOB Interaction
      ↓
Assess Impact
```

Do not simply send random headers.

Each test should answer a specific question about how the application handles host information.

---

# Establish the Baseline

Start with a normal request:

```http
GET / HTTP/1.1
Host: target.example
```

Record:

```text
Status code
Response length
Page title
Redirect location
Response headers
Cookies
Cache headers
Body content
```

Then modify one element at a time.

---

# Arbitrary Host Header

Start with a controlled hostname.

Example:

```http
GET / HTTP/1.1
Host: example.com
```

Observe whether the application:

```text
Rejects request
Redirects request
Returns normal application
Returns another virtual host
Reflects hostname
Generates URLs using hostname
Changes cache behaviour
Changes routing
```

A secure configuration may return:

```http
HTTP/1.1 400 Bad Request
```

or otherwise reject an unrecognised hostname.

---

# Host Reflection

Look for the supplied host value in:

```text
HTML
JavaScript
Redirects
Canonical links
Forms
Emails
API responses
Headers
Generated URLs
```

Example request:

```http
GET / HTTP/1.1
Host: host-test.example
```

Potential response:

```html
<link rel="canonical" href="https://host-test.example/">
```

Reflection alone is not necessarily a vulnerability.

Determine where the value is used and whether it affects a security boundary.

---

# Unique Canary Values

Use unique harmless markers when investigating reflection.

Example:

```http
Host: am-host-001.example
```

Then search the response for:

```text
am-host-001
```

This makes correlation easier.

---

# Host Header Override Headers

Even when the application validates `Host`, another header may override the value used by downstream components.

Interesting headers include:

```text
X-Forwarded-Host
X-Host
X-Forwarded-Server
X-HTTP-Host-Override
Forwarded
X-Original-Host
```

Support varies between frameworks and infrastructure.

---

# X-Forwarded-Host

A particularly important header is:

```http
X-Forwarded-Host:
```

Example:

```http
GET / HTTP/1.1
Host: target.example
X-Forwarded-Host: host-test.example
```

The front-end server may validate:

```text
Host: target.example
```

while the backend application uses:

```text
X-Forwarded-Host: host-test.example
```

for URL generation.

Conceptually:

```text
Proxy Validates Host
        ↓
Host = target.example
        ↓
Application Reads X-Forwarded-Host
        ↓
host-test.example
        ↓
Security-Relevant Behaviour
```

---

# Forwarded Header

RFC-style forwarding information may appear as:

```http
Forwarded: host=target.example
```

A controlled test might use:

```http
Forwarded: host=host-test.example
```

Check whether the application or proxy honours this value.

---

# Multiple Host Headers

Different infrastructure components may interpret duplicate headers differently.

For example:

```http
GET / HTTP/1.1
Host: target.example
Host: host-test.example
```

Possible outcomes include:

```text
Request rejected
First Host used
Second Host used
Proxy and backend disagree
```

This class of testing should be performed carefully because malformed requests can interact unpredictably with intermediaries.

---

# Absolute Request Targets

Some HTTP requests can contain an absolute URI.

For example:

```http
GET https://target.example/account HTTP/1.1
Host: target.example
```

Different infrastructure components may derive the effective host from different parts of the request.

This becomes interesting when:

```text
Request Target Host
```

and:

```text
Host Header
```

disagree.

---

# Password Reset Poisoning

One of the best-known Host header vulnerabilities involves password reset functionality.

A normal reset workflow may be:

```text
User Requests Password Reset
          ↓
Application Generates Token
          ↓
Application Builds Absolute URL
          ↓
Email Sent
          ↓
User Opens Link
```

A secure reset link might be:

```text
https://target.example/reset?token=ABC123
```

The important question is:

> Where does the application obtain `target.example`?

---

# Vulnerable Password Reset Logic

A vulnerable application may effectively do:

```text
scheme + Host header + reset path + token
```

For example:

```text
Host Header
    ↓
host-test.example
    ↓
Generated Reset URL
    ↓
https://host-test.example/reset?token=...
```

If attacker-controlled host information appears in the reset email, the reset token may be sent to an attacker-controlled destination when the victim follows the link.

---

# Controlled Password Reset Test

Use only an account and email address you control.

Request:

```http
POST /forgot-password HTTP/1.1
Host: target.example
X-Forwarded-Host: host-test.example
Content-Type: application/x-www-form-urlencoded

username=controlled-user
```

Then inspect the reset email.

Look for:

```text
https://host-test.example/reset?token=...
```

The test should stop once the behaviour has been demonstrated.

Do not target another user's account.

---

# Password Reset Testing Workflow

```text
Controlled Account
       ↓
Request Password Reset
       ↓
Baseline Email
       ↓
Identify Generated URL
       ↓
Modify Host Information
       ↓
Request Another Reset
       ↓
Inspect Controlled Mailbox
       ↓
Host Modified?
       ↓
Assess Token Exposure
```

---

# Absolute URL Generation

Host information may also affect:

```text
Registration links
Email verification links
Invitation links
Password reset links
Magic login links
OAuth callback links
Download links
Share links
Canonical URLs
API links
```

Search application workflows that generate absolute URLs.

---

# Redirect Poisoning

A response may use the Host header when constructing redirects.

Example:

```http
GET /login HTTP/1.1
Host: host-test.example
```

Response:

```http
HTTP/1.1 302 Found
Location: https://host-test.example/account
```

Determine whether the behaviour creates a meaningful redirect vulnerability.

Refer to:

[Open Redirect](open-redirect.md)

---

# Host Header and Web Cache Poisoning

Host header manipulation becomes particularly important when:

```text
Host-derived content
```

is included in a cached response.

Conceptually:

```text
Attacker Request
      ↓
Manipulated Host Information
      ↓
Application Generates Response
      ↓
Response Cached
      ↓
Victim Receives Poisoned Response
```

---

# Cache Poisoning Example

Suppose:

```http
GET / HTTP/1.1
Host: target.example
X-Forwarded-Host: host-test.example
```

produces:

```html
<script src="https://host-test.example/app.js"></script>
```

If this response is cached and later served to other users, the impact becomes significantly greater.

Do not attempt shared cache poisoning against production users unless explicitly authorised.

Use safe cache-busting techniques and controlled verification where possible.

---

# Cache Indicators

Look for headers such as:

```text
Age
Cache-Control
X-Cache
CF-Cache-Status
Via
X-Served-By
X-Cache-Hits
```

These can help identify caching infrastructure.

Refer to:

[Web Cache Poisoning](web-cache-poisoning.md)

once that page is added.

---

# Cache Key Questions

Ask:

```text
Is Host part of the cache key?

Is X-Forwarded-Host part of the cache key?

Is the response cached?

Can host-derived content enter the response?

Can another user receive that response?
```

A reflected header does not automatically imply cache poisoning.

---

# Routing-Based SSRF

Host information may sometimes influence backend routing.

Conceptually:

```text
Request
   ↓
Proxy
   ↓
Read Host
   ↓
Determine Backend
   ↓
Connect to Backend
```

If arbitrary hostnames are accepted:

```text
Attacker-Controlled Host
        ↓
Proxy Attempts Backend Connection
        ↓
Potential Internal Service Access
```

This can create routing-based SSRF.

---

# Routing-Based SSRF Testing

Use controlled destinations or an authorised out-of-band interaction service.

Conceptually:

```http
GET / HTTP/1.1
Host: controlled-callback.example
```

If the infrastructure attempts a server-side connection to the supplied hostname, an interaction may be observed.

Do not target arbitrary internal systems.

---

# Burp Collaborator

Burp Collaborator can help determine whether host manipulation causes server-side network interaction.

A workflow can be:

```text
Burp Repeater
      ↓
Generate Collaborator Domain
      ↓
Insert Controlled Domain
      ↓
Send Request
      ↓
Poll Collaborator
      ↓
DNS / HTTP Interaction?
```

A callback can provide evidence that the supplied hostname influenced server-side networking.

Refer to:

[Server Side Request Forgery](ssrf.md)

for broader SSRF methodology.

---

# Internal Virtual Hosts

A public server may host internal virtual hosts on the same infrastructure.

Example:

```text
203.0.113.10
      ↓
Reverse Proxy
      ↓
 ┌────┼─────────┐
 ↓    ↓         ↓
www  api     internal-admin
```

The internal application may not have public DNS.

However, the shared server might still route requests based on:

```http
Host: internal-admin.example.local
```

---

# Virtual Host Discovery

If authorised scope includes virtual host discovery, compare responses using candidate hostnames.

Useful sources include:

```text
DNS records
Certificate Transparency
JavaScript
Error messages
Documentation
Internal URL disclosures
Source maps
Configuration leaks
```

Avoid random internal hostname guessing when scope does not permit it.

---

# Virtual Host Response Differences

Compare:

```text
Status code
Content length
Title
Headers
Redirect
Body hash
```

For example:

```text
Host: random.example
→ 404
→ 1,240 bytes

Host: admin.internal.example
→ 200
→ 14,320 bytes
```

This suggests a different virtual host may have been reached.

---

# Host Header and Access Control

Some applications incorrectly use host information for security decisions.

Conceptually:

```text
if Host == localhost:
    allow_admin()
```

or:

```text
if Host == internal.example:
    expose_debug_interface()
```

This is dangerous because the Host header is attacker-controlled.

---

# localhost Testing

Where authorised, test whether:

```http
Host: localhost
```

changes application behaviour.

Other common local host representations may include:

```text
127.0.0.1
[::1]
```

The purpose is to determine whether application functionality incorrectly trusts the requested hostname.

---

# Example Restricted Feature

Normal request:

```http
GET /admin HTTP/1.1
Host: target.example
```

Response:

```http
HTTP/1.1 403 Forbidden
```

Controlled test:

```http
GET /admin HTTP/1.1
Host: localhost
```

If the response becomes:

```http
HTTP/1.1 200 OK
```

investigate whether host-based trust is being used as an access control mechanism.

---

# Host Header Is Not Authentication

Applications should never assume:

```text
Host: localhost
```

means:

```text
Request originated locally
```

These are different concepts.

Similarly:

```text
Host: internal.example
```

does not prove that the request came from an internal network.

---

# Host Header and Business Logic

Host information may affect business logic beyond routing.

Examples include:

```text
Tenant selection
Brand selection
Regional behaviour
Language
Payment environment
Customer portal
Email templates
Callback URLs
API environment
```

For multi-tenant applications:

```text
tenant-a.example
tenant-b.example
```

the Host header may determine which tenant is selected.

Test whether manipulating the hostname can cross tenant boundaries.

---

# Multi-Tenant Applications

Conceptually:

```text
Host
 ↓
Determine Tenant
 ↓
Load Tenant Configuration
 ↓
Process Request
```

Security questions include:

```text
Can arbitrary tenant names be supplied?

Can one tenant access another tenant's data?

Does authentication bind the session to a tenant?

Does the backend trust Host independently from the authenticated identity?
```

---

# Host Header and Authentication

Authentication flows may depend on absolute URLs.

Examples include:

```text
Password reset
Magic links
Email verification
OAuth
OIDC
SAML
SSO
```

Host manipulation may affect:

```text
Callback URL
Issuer URL
Redirect URL
Email link
Metadata URL
```

Review the complete authentication flow.

---

# Host Header and OAuth

An application might derive OAuth-related URLs from incoming request information.

Potential areas include:

```text
redirect_uri generation
callback URL generation
issuer URLs
discovery metadata
logout redirects
```

However, Host header manipulation alone does not automatically imply an OAuth vulnerability.

Verify whether attacker-controlled host information actually reaches a security-sensitive OAuth parameter.

Refer to:

[OAuth 2.0 and OpenID Connect Security](oauth-oidc.md)

---

# Host Header and WebSockets

WebSocket handshakes include host information.

Example:

```http
GET /chat HTTP/1.1
Host: target.example
Upgrade: websocket
Connection: Upgrade
```

Infrastructure may apply different routing or validation to WebSocket endpoints.

Review host validation consistently across:

```text
HTTP
HTTPS
WebSockets
API gateways
```

Refer to:

[WebSocket Security](websockets.md)

---

# Host Header and CORS

CORS and Host validation address different trust boundaries.

CORS considers:

```http
Origin:
```

while Host routing considers:

```http
Host:
```

Do not confuse:

```text
Origin validation
```

with:

```text
Host validation
```

Refer to:

[Cross-Origin Resource Sharing (CORS)](cors.md)

---

# Host Header and Information Disclosure

Host manipulation may trigger unusual error responses.

Example:

```http
Host: invalid.example
```

might produce:

```text
Unknown virtual host.

Available backend:
app-prod-03.internal
```

This can reveal internal infrastructure.

Refer to:

[Information Disclosure](information-disclosure.md)

---

# Port Handling

Host headers can include ports:

```http
Host: target.example:443
```

or:

```http
Host: target.example:8443
```

Test whether port handling affects:

```text
Validation
URL generation
Redirects
Routing
Cache behaviour
```

where relevant.

---

# Hostname Validation

Secure validation should consider the complete expected hostname.

For example:

```text
target.example
```

should not automatically trust arbitrary strings merely because they contain:

```text
target.example
```

Avoid security logic based on weak substring checks.

---

# Prefix and Suffix Validation

Weak logic may conceptually perform:

```text
host contains "target.example"
```

rather than validating the hostname correctly.

The objective of testing is to determine whether the implementation recognises only explicitly authorised hosts.

---

# Burp Suite Testing Workflow

Burp Suite is particularly useful for Host header testing.

A practical workflow:

```text
Proxy
  ↓
HTTP History
  ↓
Interesting Request
  ↓
Send to Repeater
  ↓
Baseline
  ↓
Modify Host
  ↓
Modify Override Headers
  ↓
Compare Responses
  ↓
Check Reflection
  ↓
Check Redirects
  ↓
Check Cache
  ↓
Check OOB Interaction
```

---

# Burp Repeater

Start with:

```http
GET / HTTP/1.1
Host: target.example
```

Then test controlled variations such as:

```http
Host: host-test.example
```

and:

```http
Host: target.example
X-Forwarded-Host: host-test.example
```

Compare each response against the baseline.

---

# Burp Comparer

Comparer can help identify subtle differences between:

```text
Normal Host
Modified Host
X-Forwarded-Host
localhost
Alternative virtual host
```

Compare:

```text
Headers
Body
Length
Redirects
```

---

# Burp Intruder

For controlled testing of multiple host-related headers, Intruder can be used to iterate through a small targeted list.

Example payload position:

```http
X-Forwarded-Host: §host-test.example§
```

Avoid unnecessarily large payload sets.

Manual reasoning is usually more valuable than brute force.

---

# Burp Collaborator

Collaborator is particularly useful for:

```text
Routing-based SSRF
Server-side DNS resolution
Backend HTTP connections
Out-of-band host processing
```

Use a unique Collaborator payload for each test so callbacks can be correlated with the originating request.

---

# Host Header Inchecktion Burp Extension

The PortSwigger BApp Store includes:

```text
Host Header Inchecktion
```

This extension can assist with Host header injection testing directly from Burp Suite.

Install it through:

```text
Burp Suite
   ↓
Extensions
   ↓
BApp Store
   ↓
Search:
Host Header Inchecktion
```

The extension can perform several useful test types.

These include:

```text
Host header injection testing
Collaborator payload testing
localhost testing
canary reflection testing
```

The extension can also create Burp Scanner issues when a successful injection is detected.

---

# Host Header Inchecktion Workflow

A practical workflow is:

```text
Proxy
   ↓
HTTP History
   ↓
Select Interesting Request
   ↓
Right Click
   ↓
Extensions
   ↓
Host Header Inchecktion
   ↓
Select Test Type
   ↓
Review Result
   ↓
Manually Verify in Repeater
```

The important principle remains:

> Extension output is a testing lead, not final proof of a vulnerability.

Always manually verify the security impact.

---

# Collaborator Test

The extension can use a Collaborator payload to investigate whether host manipulation causes a server-side interaction.

Conceptually:

```text
Host Header Inchecktion
        ↓
Collaborator Payload
        ↓
Target Infrastructure
        ↓
DNS / HTTP Interaction
        ↓
Potential Routing-Based SSRF
```

Any callback should be correlated with the exact request that generated it.

---

# localhost Test

The extension can also test:

```text
localhost
```

to identify applications where Host-based trust may expose restricted functionality.

Conceptually:

```text
External Request
      ↓
Host Modified
      ↓
localhost
      ↓
Application Believes Request Is Local?
      ↓
Restricted Feature Exposed?
```

Manually verify any reported behaviour.

---

# Canary Reflection Test

A harmless canary value can be used to determine whether attacker-controlled host information appears in the response.

Conceptually:

```text
Unique Canary
      ↓
Host-Related Header
      ↓
Application
      ↓
Response
      ↓
Canary Reflected?
```

Reflection may become relevant to:

```text
Cache poisoning
Absolute URL generation
Redirect poisoning
HTML generation
```

but reflection alone is not proof of exploitability.

---

# HostInject

Another useful tool is:

```text
hostinject
```

by `pikpikcu`.

It is a Python tool designed to automate Host header injection testing.

It supports testing:

```text
Single URLs
Lists of URLs
Custom header wordlists
Controlled attacker domains
Different HTTP methods
POST bodies
Redirect behaviour
Proxy configurations
Custom User-Agent values
```

---

# Installing HostInject

Clone the project:

```bash
git clone https://github.com/pikpikcu/hostinject.git
```

Enter the directory:

```bash
cd hostinject
```

Install requirements:

```bash
pip3 install -r requirements.txt
```

View available options:

```bash
python3 hostinject.py -h
```

---

# HostInject Single Target

Example:

```bash
python3 hostinject.py \
  -u https://target.example \
  -w headers.txt \
  -a controlled.example \
  -o results.txt
```

Where:

```text
-u
```

specifies the target.

```text
-w
```

specifies the header wordlist.

```text
-a
```

specifies the controlled test domain.

```text
-o
```

specifies the output file.

---

# HostInject URL List

For multiple authorised targets:

```bash
python3 hostinject.py \
  -l urls.txt \
  -w headers.txt \
  -a controlled.example \
  -o results.txt
```

This can be useful after reconnaissance when multiple in-scope web applications have been identified.

---

# HostInject Through Burp

HostInject supports proxies.

This makes it useful to route automated testing through Burp Suite.

Conceptually:

```text
HostInject
    ↓
Burp Proxy
    ↓
Target
```

This allows requests to remain visible in Burp for later manual analysis.

Example proxy configuration:

```text
http://127.0.0.1:8080
```

Check the current HostInject help output for the exact proxy syntax supported by the installed version.

---

# Recommended Tool Workflow

Automation should assist manual analysis rather than replace it.

A good workflow is:

```text
Burp Proxy
     ↓
Identify Interesting Endpoint
     ↓
Manual Repeater Testing
     ↓
Host Header Inchecktion
     ↓
HostInject
     ↓
Interesting Behaviour
     ↓
Return to Repeater
     ↓
Manual Verification
     ↓
Browser / Collaborator Verification
     ↓
Impact Assessment
     ↓
Report
```

---

# Tool Comparison

| Tool | Best Use |
|---|---|
| Burp Repeater | Manual Host manipulation |
| Burp Collaborator | OOB interaction detection |
| Burp Comparer | Response comparison |
| Burp Intruder | Controlled payload iteration |
| Host Header Inchecktion | Burp-assisted Host injection checks |
| HostInject | Automated Host header testing |
| Browser | Application workflow validation |
| curl | Quick manual header testing |

---

# curl Testing

A basic test:

```bash
curl -k -i \
  -H "Host: host-test.example" \
  https://target.example/
```

When TLS is involved, remember that:

```text
TLS SNI
```

and:

```text
HTTP Host
```

are separate concepts.

The TLS connection may be established for one hostname while the HTTP request contains another Host value.

---

# X-Forwarded-Host with curl

```bash
curl -k -i \
  -H "X-Forwarded-Host: host-test.example" \
  https://target.example/
```

Search the response for:

```text
host-test.example
```

---

# Multiple Headers

A controlled test can compare several host-related headers:

```bash
curl -k -i \
  -H "Host: target.example" \
  -H "X-Forwarded-Host: host-test.example" \
  https://target.example/
```

Again, change one variable at a time when trying to understand which header controls the behaviour.

---

# Testing Matrix

Create a matrix such as:

| Test | Host | Override | Result |
|---|---|---|---|
| Baseline | `target.example` | None | 200 |
| Arbitrary Host | `host-test.example` | None | 400 |
| XFH | `target.example` | `host-test.example` | 200 |
| localhost | `localhost` | None | 403 |
| Forwarded | `target.example` | Controlled host | 200 |

Then record whether the supplied value appears in:

```text
Response body
Location header
Absolute links
Cacheable content
Emails
Backend interactions
```

---

# Header Testing Matrix

Useful host-related headers to investigate where appropriate:

```text
Host
X-Forwarded-Host
Forwarded
X-Host
X-Forwarded-Server
X-HTTP-Host-Override
X-Original-Host
```

Support is infrastructure-specific.

Do not assume every header is meaningful.

---

# High-Value Functionality

Prioritise Host header testing around functionality that generates or relies on absolute URLs.

Examples:

```text
Password reset
Registration
Email verification
Invitations
Magic links
OAuth
OIDC
SSO
Share links
Download links
Redirects
Canonical links
Multi-tenant routing
```

---

# Password Reset Checklist

```text
[ ] Use controlled account
[ ] Request normal reset
[ ] Record baseline email
[ ] Test Host
[ ] Test X-Forwarded-Host
[ ] Test Forwarded
[ ] Inspect generated link
[ ] Determine token exposure
[ ] Stop once demonstrated
```

---

# Cache Checklist

```text
[ ] Identify cache
[ ] Check cache headers
[ ] Identify host-derived reflection
[ ] Determine cache key
[ ] Use cache buster
[ ] Avoid poisoning shared production cache
[ ] Verify with controlled requests
[ ] Assess victim impact
```

---

# Routing Checklist

```text
[ ] Modify Host
[ ] Observe status changes
[ ] Observe response changes
[ ] Test controlled callback
[ ] Check Collaborator
[ ] Investigate virtual host routing
[ ] Avoid arbitrary internal targeting
```

---

# Access Control Checklist

```text
[ ] Test normal Host
[ ] Test localhost
[ ] Test known internal hostname
[ ] Compare restricted endpoint
[ ] Determine whether Host affects authorisation
[ ] Verify with controlled account
```

---

# General Host Header Checklist

## Discovery

```text
[ ] Identify application hostname
[ ] Identify reverse proxy/CDN
[ ] Identify redirects
[ ] Identify absolute URLs
[ ] Identify password reset functionality
[ ] Identify caching
[ ] Identify multi-tenant behaviour
```

## Host Manipulation

```text
[ ] Test arbitrary Host
[ ] Test X-Forwarded-Host
[ ] Test Forwarded
[ ] Test X-Host
[ ] Test X-Original-Host where relevant
[ ] Test localhost
[ ] Test controlled callback hostname
```

## Response Analysis

```text
[ ] Check response body
[ ] Check Location
[ ] Check canonical URL
[ ] Check scripts
[ ] Check forms
[ ] Check API responses
[ ] Check cookies
[ ] Check cache headers
```

## Application Workflows

```text
[ ] Password reset
[ ] Registration
[ ] Email verification
[ ] Invitations
[ ] Magic links
[ ] OAuth/OIDC
[ ] Redirects
```

## Infrastructure

```text
[ ] Virtual host routing
[ ] Reverse proxy behaviour
[ ] CDN behaviour
[ ] Backend routing
[ ] Internal host access
[ ] OOB interactions
```

## Tools

```text
[ ] Burp Repeater
[ ] Burp Collaborator
[ ] Burp Comparer
[ ] Burp Intruder
[ ] Host Header Inchecktion
[ ] HostInject
[ ] curl
```

## Impact

```text
[ ] Password reset token exposure
[ ] Cache poisoning
[ ] Routing-based SSRF
[ ] Restricted functionality
[ ] Internal virtual host access
[ ] Redirect manipulation
[ ] Tenant boundary issue
[ ] Information disclosure
```

---

# Decision Tree

```text
Modify Host Information
        ↓
Behaviour Changes?
        ↓
       NO
        ↓
Test Override Headers
        ↓
Behaviour Changes?
        ↓
       NO
        ↓
No Obvious Host Trust Issue

        OR

       YES
        ↓
Where Is Value Used?
        ↓
┌────────────┬────────────┬────────────┐
↓            ↓            ↓            ↓
Response    Redirect     Email       Routing
↓            ↓            ↓            ↓
Reflection  Redirect     Reset       Backend
↓            ↓            ↓            ↓
Cache?      Impact?      Token?       OOB?
↓            ↓            ↓            ↓
Assess      Assess       Assess       Assess
        ↓
Security Boundary Crossed?
        ↓
       YES
        ↓
Confirm Safely
        ↓
Document
        ↓
Report
```

---

# Evidence Collection

For a confirmed Host header vulnerability, record:

```text
Affected endpoint
HTTP method
Host header used
Override header used
Authentication state
Affected functionality
Baseline request
Modified request
Baseline response
Modified response
Generated URL
Email evidence where applicable
Cache evidence where applicable
Collaborator evidence where applicable
Affected user role
Security impact
```

---

# Example Finding: Password Reset Poisoning

```text
Finding:
Password Reset Poisoning via X-Forwarded-Host

Affected Endpoint:
/forgot-password

Observed:
The application generated password reset URLs using the value supplied in the X-Forwarded-Host request header.

Using a controlled test account, supplying:

X-Forwarded-Host: controlled.example

caused the password reset email to contain a reset URL referencing the controlled hostname.

Impact:
An attacker may be able to cause password reset tokens to be included in links pointing to an attacker-controlled host. If a victim follows such a link, the token may be disclosed to the attacker and potentially used to compromise the affected account.

Recommendation:
Generate password reset URLs using a trusted application base URL configured server-side rather than deriving the hostname from request headers.
```

---

# Example Finding: Host-Based Access Control

```text
Finding:
Host Header Manipulation Bypasses Restricted Functionality

Affected Endpoint:
/admin

Observed:
Requests using the normal application hostname returned HTTP 403.

Changing the Host header to a locally trusted hostname caused the endpoint to return the restricted application functionality.

Impact:
An external user may be able to access functionality intended only for trusted or internal requests by manipulating attacker-controlled HTTP host information.

Recommendation:
Do not use the Host header to determine whether a request originated from a trusted network or system. Enforce authentication and authorisation independently of user-controlled request headers.
```

---

# Example Finding: Internal Host Disclosure

```text
Finding:
Host Header Error Response Discloses Internal Backend Hostname

Observed:
Supplying an invalid Host header caused the application to return an error containing an internal backend hostname.

Impact:
The information reveals internal infrastructure naming and may assist further testing, particularly where SSRF or internal routing vulnerabilities are present.

Recommendation:
Return generic client-facing errors and keep internal routing information within protected server-side logs.
```

---

# Example Finding: Routing-Based SSRF

```text
Finding:
Host Header Manipulation Triggers Server-Side Network Requests

Observed:
Supplying a unique authorised out-of-band hostname through host-related request information resulted in a DNS or HTTP interaction from the target infrastructure.

Impact:
The behaviour indicates that attacker-controlled host information influences server-side routing or network communication. Depending on network access and filtering, this may enable access to otherwise unreachable services.

Recommendation:
Restrict backend routing to an explicit allowlist of expected destinations and reject unrecognised Host values before they reach routing logic.
```

---

# Reporting Titles

Prefer precise titles such as:

```text
Password Reset Poisoning via X-Forwarded-Host

Host Header Manipulation Bypasses Restricted Functionality

Arbitrary Host Header Used in Absolute URL Generation

Host Header Injection Enables Web Cache Poisoning

Host Header Manipulation Enables Routing-Based SSRF

Internal Virtual Host Accessible Through Host Manipulation

Untrusted Host Header Controls Tenant Selection

Internal Backend Hostname Disclosed Through Invalid Host Handling
```

Avoid vague titles such as:

```text
Host Header Issue
```

---

# Severity

Severity depends entirely on the resulting behaviour.

For example:

```text
Host reflection only
```

may be informational.

While:

```text
Host manipulation
       +
Password reset token exposure
```

may have substantial account compromise impact.

Similarly:

```text
Host manipulation
       +
Internal routing
       +
Sensitive internal service
```

may become significantly more serious.

Assess the demonstrated impact rather than the header manipulation itself.

---

# Remediation

The strongest approach is:

```text
Do Not Trust Request Host Information
             ↓
Use Configured Application Origin
             ↓
Validate Required Host Values
             ↓
Restrict Proxy Override Headers
             ↓
Restrict Backend Routing
```

---

# Use a Configured Base URL

Security-sensitive absolute URLs should be generated from trusted server-side configuration.

For example:

```text
APPLICATION_BASE_URL=https://target.example
```

Then:

```text
Password Reset
      ↓
Configured Base URL
      ↓
https://target.example/reset?token=...
```

rather than:

```text
Incoming Host
      ↓
Generate URL
```

---

# Validate Host

Where the Host header is required, compare it against an explicit allowlist.

Conceptually:

```text
Incoming Host
      ↓
Exact Validation
      ↓
Known Host?
   ↓        ↓
 Yes       No
 ↓          ↓
Process    Reject
```

Example allowed hosts:

```text
target.example
www.target.example
api.target.example
```

---

# Reject Unknown Hosts

Unknown Host values should not silently reach the application.

Where possible:

```text
Unknown Host
     ↓
Reject Early
```

This can be enforced at:

```text
CDN
Load balancer
Reverse proxy
Web server
Application
```

Defence in depth is preferable.

---

# Do Not Trust Override Headers From the Internet

Headers such as:

```text
X-Forwarded-Host
Forwarded
```

should only be trusted when they originate from known infrastructure components.

External clients should not be able to control trusted proxy metadata.

---

# Proxy Configuration

A secure architecture should distinguish:

```text
Client-Controlled Headers
```

from:

```text
Proxy-Generated Headers
```

For example:

```text
Internet Client
      ↓
Reverse Proxy
      ↓
Remove Untrusted Forwarding Headers
      ↓
Generate Trusted Forwarding Headers
      ↓
Application
```

---

# Restrict Backend Routing

Reverse proxies and load balancers should route only to expected destinations.

Conceptually:

```text
Host
 ↓
Explicit Routing Table
 ↓
Known Destination?
 ↓
Yes → Route
No  → Reject
```

Avoid treating arbitrary Host values as backend destinations.

---

# Internal Virtual Hosts

Avoid exposing internal-only applications through the same externally reachable routing layer where possible.

If this architecture is necessary:

```text
Authentication
Network restrictions
Explicit host validation
Backend access controls
```

must remain effective independently.

---

# Password Reset Security

Password reset links should use:

```text
Trusted configured domain
```

not:

```text
Host
X-Forwarded-Host
Forwarded
```

from the incoming request.

The same principle applies to:

```text
Magic links
Email verification
Invitations
Account activation
```

---

# References

## PortSwigger Web Security Academy: HTTP Host Header Attacks

https://portswigger.net/web-security/host-header

PortSwigger covers Host header fundamentals, testing methodologies, password reset poisoning, cache poisoning, routing-based SSRF, authentication bypass and virtual host attacks.

---

## PortSwigger HTTP Host Header Labs

https://portswigger.net/web-security/all-labs#http-host-header-attacks

Practical labs for Host header vulnerability testing.

---

## PortSwigger BApp Store: Host Header Inchecktion

https://portswigger.net/bappstore/3908768b9ae945d8adf583052ad2e3b3

The Burp extension can assist with:

```text
Host header injection testing
Collaborator-based SSRF checks
localhost restricted-feature checks
Canary reflection checks
```

Use extension findings as leads and manually validate them.

---

## HostInject

https://github.com/pikpikcu/hostinject

HostInject is a Python-based Host header injection testing tool supporting single targets, URL lists, custom header wordlists, controlled attacker domains, multiple HTTP methods, request bodies and proxy configurations.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

Useful broader methodology for testing HTTP behaviour, application configuration and infrastructure trust boundaries.

---

## MDN: Host Header

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Host

Reference documentation for the HTTP `Host` request header.

---

# Final Host Header Testing Model

```text
                    HTTP REQUEST
                         ↓
                  HOST INFORMATION
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
      Host        X-Forwarded-Host      Forwarded
       ↓                 ↓                 ↓
       └─────────────────┼─────────────────┘
                         ↓
                 WHO TRUSTS THE VALUE?
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
   Application         Proxy              Cache
       ↓                 ↓                 ↓
       └─────────────────┼─────────────────┘
                         ↓
                  HOW IS IT USED?
                         ↓
    ┌──────────┬─────────┼─────────┬──────────┐
    ↓          ↓         ↓         ↓          ↓
 Password    Cache     Routing   Access     Tenant
 Reset                           Control    Selection
    ↓          ↓         ↓         ↓          ↓
 Token      Poison     SSRF      Bypass     Boundary
 Exposure
    ↓          ↓         ↓         ↓          ↓
    └──────────┴─────────┼─────────┴──────────┘
                         ↓
                SECURITY IMPACT?
                         ↓
                        YES
                         ↓
                  VERIFY SAFELY
                         ↓
                    DOCUMENT
                         ↓
                      REPORT
```

The key principle is:

> The Host header and related forwarding headers are attacker-controlled input unless trusted infrastructure has explicitly normalised them. Host header testing should therefore focus on where that input crosses a security boundary, such as password reset URL generation, cache behaviour, backend routing, internal virtual hosts, access control or tenant selection.
