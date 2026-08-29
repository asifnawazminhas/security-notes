# HTTP Security Headers

HTTP security headers allow a web application to instruct browsers how content should be handled and which browser security mechanisms should be enforced.

They provide an additional defensive layer against vulnerabilities such as:

```text
Cross-Site Scripting
Clickjacking
MIME Sniffing
HTTPS Downgrade
Information Leakage
Cross-Origin Data Exposure
Uncontrolled Browser Features
```

Security headers do not replace secure application development.

Conceptually:

```text
Secure Application
      +
Secure Browser Policy
      ↓
Defence in Depth
```

A typical response may contain:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

The main security headers covered in this note are:

```text
Content-Security-Policy
Content-Security-Policy-Report-Only
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
X-Frame-Options
Cross-Origin-Opener-Policy
Cross-Origin-Embedder-Policy
Cross-Origin-Resource-Policy
Cache-Control
Clear-Site-Data
```

Related headers and controls include:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Set-Cookie
Reporting-Endpoints
```

These require additional context and should not simply be evaluated as present or absent.

!!! warning "Authorised Security Testing"
    Perform security-header testing only against applications explicitly authorised for assessment. Header analysis is generally low impact, but active validation of CSP bypasses, CORS behaviour, framing, cross-origin isolation, cache behaviour, or related vulnerabilities should remain within the approved scope.

---

# Security Headers Testing Model

The basic workflow is:

```text
HTTP Response
      ↓
Enumerate Headers
      ↓
Identify Missing Controls
      ↓
Analyse Existing Values
      ↓
Determine Application Context
      ↓
Test Browser Behaviour
      ↓
Identify Practical Security Impact
      ↓
Report Relevant Weaknesses
```

The most important principle is:

```text
Missing Header
      ≠
Vulnerability Automatically
```

Instead:

```text
Missing / Weak Header
        +
Relevant Attack Surface
        +
Demonstrable Security Impact
        ↓
Meaningful Finding
```

---

# Why Security Headers Matter

Browsers implement many security controls.

Applications can influence those controls through response headers.

For example:

```text
Application
     ↓
Content-Security-Policy
     ↓
Browser
     ↓
Restrict Script Execution
```

Another example:

```text
Application
     ↓
X-Frame-Options
     ↓
Browser
     ↓
Restrict Framing
```

Security headers therefore operate at the boundary between:

```text
Application Security
```

and:

```text
Browser Security
```

---

# Initial Reconnaissance

Start by retrieving the application response headers.

Using curl:

```bash
curl -I https://target.example/
```

For full headers:

```bash
curl -s -D - -o /dev/null https://target.example/
```

Follow redirects:

```bash
curl -s -L -D - -o /dev/null https://target.example/
```

---

# Important Limitation of HEAD Requests

`curl -I` sends:

```text
HEAD
```

instead of:

```text
GET
```

Some applications return different headers for HEAD requests.

Therefore verify interesting findings with:

```bash
curl -s -D - -o /dev/null https://target.example/
```

which performs a GET request.

---

# Burp Suite Workflow

Burp is particularly useful because security headers can vary by:

```text
Endpoint
Response type
Authentication state
Error condition
Application component
HTTP method
```

Recommended workflow:

```text
Burp Proxy
    ↓
Browse Application
    ↓
HTTP History
    ↓
Inspect Response Headers
    ↓
Send Interesting Requests to Repeater
    ↓
Compare Endpoints
    ↓
Test Browser Behaviour
    ↓
Assess Practical Impact
```

---

# Do Not Test Only the Homepage

Security headers may differ between:

```text
/
```

and:

```text
/login
/account
/admin
/api/
/upload/
/reset-password
/error
```

A reverse proxy may add headers globally while individual applications override them.

Alternatively:

```text
Main Application
→ Strong Headers

Legacy Application
→ Weak Headers
```

---

# Header Coverage Matrix

A useful assessment matrix:

| Endpoint | CSP | HSTS | XCTO | Referrer | Permissions | Framing |
|---|---:|---:|---:|---:|---:|---:|
| `/` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/login` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/account` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/admin` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/error` | ? | ? | ? | ? | ? | ? |

Also consider:

```text
HTML responses
JSON responses
File downloads
Static resources
Redirect responses
Error pages
```

---

# Burp Proxy

Use Burp Proxy to inspect security headers naturally while browsing.

Interesting headers can be searched in HTTP history:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
X-Frame-Options
Cross-Origin-Opener-Policy
Cross-Origin-Embedder-Policy
Cross-Origin-Resource-Policy
Cache-Control
```

---

# Burp Repeater

Repeater allows controlled comparison between:

```text
Authenticated
Unauthenticated

GET
POST

Normal page
Error page

HTML
JSON
Download
```

This is useful for identifying inconsistent header deployment.

---

# Burp Comparer

Comparer can help compare response headers from:

```text
Main application
Legacy endpoint

Authenticated page
Unauthenticated page

Normal response
Error response
```

---

# Content-Security-Policy

Content Security Policy is one of the most important browser security controls.

Header:

```http
Content-Security-Policy: ...
```

CSP allows an application to define which resources the browser may load or execute.

Conceptually:

```text
HTML
 ↓
Browser
 ↓
CSP
 ↓
Is Resource Allowed?
   ↓          ↓
  YES         NO
   ↓          ↓
 LOAD        BLOCK
```

CSP is primarily a:

```text
Defence-in-depth mechanism
```

against client-side attacks such as XSS.

Refer to:

```text
docs/web/xss.md
docs/web/dom-based-vulnerabilities.md
```

---

# Example CSP

A basic policy:

```http
Content-Security-Policy: default-src 'self'
```

A more detailed example:

```http
Content-Security-Policy:
    default-src 'self';
    script-src 'self';
    style-src 'self';
    img-src 'self' data:;
    object-src 'none';
    base-uri 'self';
    frame-ancestors 'none';
```

Actual policies should be designed according to application requirements.

---

# CSP Directives

Important CSP directives include:

```text
default-src
script-src
script-src-elem
script-src-attr
style-src
style-src-elem
style-src-attr
img-src
font-src
connect-src
media-src
object-src
frame-src
child-src
worker-src
manifest-src
base-uri
form-action
frame-ancestors
upgrade-insecure-requests
```

---

# default-src

`default-src` provides a fallback for several resource types.

Example:

```http
Content-Security-Policy: default-src 'self'
```

This does not automatically replace every specialised directive.

Always evaluate the complete policy.

---

# script-src

Controls JavaScript sources.

Example:

```http
Content-Security-Policy:
    script-src 'self'
```

Potentially risky configurations include:

```text
'unsafe-inline'
'unsafe-eval'
*
data:
Broad third-party origins
Untrusted CDNs
```

However, CSP security cannot be judged from one keyword alone.

Analyse the complete policy.

---

# unsafe-inline

Example:

```http
script-src 'self' 'unsafe-inline'
```

`'unsafe-inline'` can permit inline JavaScript in policies where it remains effective.

Example inline code:

```html
<script>
alert(1)
</script>
```

or inline event handlers such as:

```html
<img src=x onerror=alert(1)>
```

Whether these execute depends on the complete CSP and browser interpretation.

---

# unsafe-eval

Example:

```http
script-src 'self' 'unsafe-eval'
```

`'unsafe-eval'` permits certain string-to-code execution mechanisms such as:

```javascript
eval()
```

and related constructs.

Its presence weakens protection against some JavaScript injection scenarios.

It does not automatically mean:

```text
XSS exists
```

---

# CSP and XSS

Important distinction:

```text
Weak CSP
    ≠
XSS
```

CSP is generally:

```text
Mitigation
```

while XSS is:

```text
Underlying Vulnerability
```

If an application contains exploitable XSS and CSP fails to prevent exploitation:

```text
Primary Finding
→ XSS
```

The weak CSP may be:

```text
Contributing Control Weakness
```

depending on reporting methodology.

---

# CSP Nonces

A stronger approach can use nonces.

Example:

```http
Content-Security-Policy:
    script-src 'nonce-randomValue'
```

HTML:

```html
<script nonce="randomValue">
    applicationCode();
</script>
```

The nonce should be:

```text
Unpredictable
Generated per response
Not attacker controlled
```

---

# Reused CSP Nonces

A nonce should generally not be a static application-wide value.

Check several responses.

Example:

```text
Request 1
nonce=ABC123

Request 2
nonce=ABC123

Request 3
nonce=ABC123
```

Persistent reuse may undermine the intended nonce security model.

---

# Extract CSP Nonces

A simple command:

```bash
curl -s https://target.example/ |
grep -oE 'nonce="[^"]+"'
```

Repeat requests and compare values.

---

# CSP Hashes

CSP can allow specific inline scripts using cryptographic hashes.

Example concept:

```text
script-src 'sha256-...'
```

Only scripts matching the permitted hash should execute.

---

# strict-dynamic

A modern CSP may use:

```text
'strict-dynamic'
```

with:

```text
nonces
```

or:

```text
hashes
```

to establish trust in dynamically loaded scripts.

Do not evaluate `'strict-dynamic'` independently from the rest of the policy.

---

# object-src

A strong CSP often includes:

```http
object-src 'none'
```

This restricts plugin content such as:

```text
<object>
<embed>
```

Modern browsers have significantly reduced plugin exposure, but explicitly restricting object sources remains useful.

---

# base-uri

Example:

```http
base-uri 'none'
```

or:

```http
base-uri 'self'
```

This restricts:

```html
<base>
```

which can influence how relative URLs resolve.

---

# form-action

Example:

```http
form-action 'self'
```

This restricts destinations to which HTML forms may submit.

This can reduce the impact of certain HTML injection scenarios.

Refer to:

```text
docs/web/html-injection.md
```

---

# frame-ancestors

Example:

```http
Content-Security-Policy:
    frame-ancestors 'none'
```

This prevents framing.

Alternative:

```http
frame-ancestors 'self'
```

This is the modern CSP mechanism for controlling framing.

It is generally preferable to relying only on:

```text
X-Frame-Options
```

Refer to:

```text
docs/web/clickjacking.md
```

---

# connect-src

Controls destinations available to APIs such as:

```text
fetch()
XMLHttpRequest
WebSocket
EventSource
```

Example:

```http
connect-src 'self' https://api.example.com
```

This can restrict some post-XSS network communication but should not be considered a replacement for preventing XSS.

---

# img-src

Controls image sources.

Example:

```http
img-src 'self' data:
```

Broad image policies can sometimes enable data exfiltration techniques after HTML injection or other client-side compromise.

Assess them in context.

---

# style-src

Controls stylesheet sources.

Potentially risky:

```text
'unsafe-inline'
```

but inline styles and inline scripts have different security implications.

Do not automatically treat:

```text
style-src 'unsafe-inline'
```

as equivalent to:

```text
script-src 'unsafe-inline'
```

---

# CSP Wildcards

Example:

```http
script-src *
```

is extremely broad.

Similarly:

```text
https:
```

may allow scripts from any HTTPS origin.

Whether this creates a practical bypass depends on the policy and available sources.

---

# Broad Trusted Domains

Example:

```http
script-src 'self' https://*.example-cdn.com
```

Ask:

```text
Can users upload JavaScript there?

Is any subdomain attacker controllable?

Does the trusted service host JSONP?

Can arbitrary files be served?
```

CSP security depends on the security of trusted origins.

---

# CSP Bypass Analysis

When reviewing CSP, think:

```text
Policy
 ↓
Trusted Sources
 ↓
Can Attacker Control Any?
 ↓
Can Executable Content Be Loaded?
```

Do not reduce CSP testing to:

```text
unsafe-inline present?
```

---

# CSP and JSONP

Historically, trusted JSONP endpoints have sometimes enabled CSP bypasses.

If a CSP trusts a third-party domain:

```text
script-src trusted.example
```

and that domain exposes attacker-influenced executable responses, the trust relationship may weaken the policy.

Test only where relevant.

---

# CSP and File Upload

If CSP includes:

```text
'self'
```

and the application allows users to upload:

```text
JavaScript
HTML
SVG
```

to the same origin, the upload functionality may influence CSP security.

Refer to:

```text
docs/web/file-upload.md
```

---

# CSP and Open Redirects

Open redirects alone do not automatically bypass CSP.

CSP evaluates the final resource according to browser CSP rules.

However, redirect chains and trusted services can create complex interactions.

Refer to:

```text
docs/web/open-redirect.md
```

---

# CSP Report-Only

Header:

```http
Content-Security-Policy-Report-Only:
```

Example:

```http
Content-Security-Policy-Report-Only:
    default-src 'self'
```

Report-only mode:

```text
Detects Violations
        ↓
Does Not Enforce Policy
```

This is useful during deployment but should not be mistaken for active CSP protection.

---

# Report-Only Finding

If an application has:

```text
Content-Security-Policy-Report-Only
```

but no:

```text
Content-Security-Policy
```

then CSP is:

```text
Monitoring Only
```

not:

```text
Enforced
```

---

# CSP Meta Tags

CSP can also appear as:

```html
<meta
    http-equiv="Content-Security-Policy"
    content="default-src 'self'">
```

However, HTTP response headers provide stronger and more complete policy delivery.

Some CSP directives are not supported through meta delivery.

Inspect both.

---

# Multiple CSP Headers

An application can return multiple CSP headers.

Example:

```http
Content-Security-Policy: default-src 'self'
Content-Security-Policy: script-src 'self'
```

Browsers enforce all applicable policies.

Do not simply concatenate them mentally as though they were one policy.

---

# CSP Testing Tools

Useful CSP analysis tools include:

```text
Burp Suite
Browser DevTools
Google CSP Evaluator
Manual policy review
```

---

# CSP Evaluator

Google provides CSP Evaluator:

```text
https://csp-evaluator.withgoogle.com/
```

It can help identify potentially unsafe CSP configurations.

Scanner output should still be manually validated.

---

# Browser DevTools CSP Testing

Open:

```text
Developer Tools
    ↓
Console
```

CSP violations commonly appear as browser console messages.

This helps verify whether:

```text
Inline script
External script
Frame
Connection
```

was blocked.

---

# CSP Reporting

Modern CSP deployments can report policy violations.

Potential mechanisms include:

```text
report-uri
report-to
Reporting-Endpoints
```

`report-uri` is older and may still be encountered.

Do not expose sensitive data unnecessarily in CSP reports.

---

# Strict-Transport-Security

Header:

```http
Strict-Transport-Security:
```

commonly abbreviated:

```text
HSTS
```

HSTS tells supporting browsers to use HTTPS for a host for a defined period.

Example:

```http
Strict-Transport-Security:
    max-age=31536000
```

---

# HSTS Flow

Without HSTS:

```text
User Enters
http://example.com
      ↓
HTTP Request
      ↓
Redirect
      ↓
HTTPS
```

The initial HTTP request exists.

With an established HSTS policy:

```text
User Enters
http://example.com
      ↓
Browser
      ↓
Automatically Upgrades
      ↓
https://example.com
```

---

# HSTS Syntax

Example:

```http
Strict-Transport-Security:
    max-age=31536000; includeSubDomains
```

Possible directives:

```text
max-age
includeSubDomains
preload
```

---

# max-age

Example:

```text
max-age=31536000
```

means the browser should remember the HSTS policy for approximately one year.

---

# max-age=0

Example:

```http
Strict-Transport-Security: max-age=0
```

removes the HSTS policy from supporting browsers.

Therefore:

```text
Header Present
```

does not necessarily mean:

```text
HSTS Enabled
```

Always inspect the value.

---

# includeSubDomains

Example:

```text
includeSubDomains
```

extends HSTS protection to subdomains.

Before enabling it operationally, organisations must ensure all relevant subdomains support HTTPS correctly.

From a testing perspective, its absence is not automatically a vulnerability.

---

# preload

Example:

```text
preload
```

indicates intent to meet browser preload requirements.

Actual preload status is not determined merely by the presence of the directive.

Preloading requires submission and acceptance into browser preload infrastructure.

---

# HSTS on HTTP

Browsers ignore HSTS headers delivered over insecure HTTP.

HSTS must be received over:

```text
HTTPS
```

---

# HSTS Testing

Using curl:

```bash
curl -s -D - -o /dev/null \
  https://target.example/ |
grep -i strict-transport-security
```

---

# HTTP Redirect Testing

Also test:

```bash
curl -I http://target.example/
```

Determine whether HTTP redirects to HTTPS.

Example:

```http
HTTP/1.1 301 Moved Permanently
Location: https://target.example/
```

---

# HSTS and Redirects

These are related but different controls.

```text
HTTP → HTTPS Redirect
```

helps direct users to HTTPS.

```text
HSTS
```

instructs browsers to avoid future HTTP connections.

Ideally:

```text
HTTPS Everywhere
+
Correct Redirect
+
HSTS
```

---

# HSTS False Positive

Missing HSTS does not automatically demonstrate:

```text
Sensitive data interception
```

The practical risk depends on:

```text
HTTP availability
Redirect behaviour
Cookies
User navigation
Preload status
Application sensitivity
```

---

# X-Content-Type-Options

Header:

```http
X-Content-Type-Options: nosniff
```

This instructs browsers not to perform certain MIME-type sniffing behaviours.

Recommended value:

```text
nosniff
```

---

# MIME Sniffing

Without appropriate protection, browsers may attempt to infer content type rather than strictly respecting:

```http
Content-Type:
```

This can create security problems when attacker-controlled files are served with incorrect MIME types.

---

# Example

Response:

```http
Content-Type: text/plain
```

but content contains:

```html
<script>
...
</script>
```

`nosniff` helps ensure browsers respect declared MIME types in relevant contexts.

---

# File Upload Interaction

This is especially relevant for applications that serve:

```text
User uploads
Attachments
Generated files
```

Refer to:

```text
docs/web/file-upload.md
```

---

# Correct Header

```http
X-Content-Type-Options: nosniff
```

Unexpected values should not be assumed to provide protection.

---

# Referrer-Policy

Header:

```http
Referrer-Policy:
```

controls how much referrer information is sent when navigating or loading resources.

Example:

```http
Referrer-Policy:
    strict-origin-when-cross-origin
```

---

# Referer Header

When navigating from:

```text
https://target.example/account/reset?token=SECRET
```

to another origin, the browser may send some referrer information depending on policy.

Sensitive URLs may contain:

```text
Reset tokens
Document IDs
Internal paths
Search terms
Identifiers
```

---

# Referrer-Policy Values

Common values include:

```text
no-referrer
no-referrer-when-downgrade
origin
origin-when-cross-origin
same-origin
strict-origin
strict-origin-when-cross-origin
unsafe-url
```

---

# no-referrer

```http
Referrer-Policy: no-referrer
```

sends no Referer information.

This is highly restrictive.

---

# same-origin

```http
Referrer-Policy: same-origin
```

sends referrer information only for same-origin requests.

---

# strict-origin

Cross-origin requests receive only the origin when allowed by the policy.

Example:

```text
https://target.example/
```

rather than:

```text
https://target.example/private/document?id=123
```

---

# strict-origin-when-cross-origin

A commonly suitable modern policy:

```http
Referrer-Policy:
    strict-origin-when-cross-origin
```

It provides full referrer information for same-origin requests while limiting information sent cross-origin.

---

# unsafe-url

```http
Referrer-Policy: unsafe-url
```

may send full URL information to other origins.

This can expose sensitive URL data and deserves review.

---

# Password Reset Interaction

Referrer policy is particularly important on pages containing:

```text
Password reset tokens
Email verification tokens
Magic login links
Recovery identifiers
```

Refer to:

```text
docs/web/password-reset.md
```

---

# Permissions-Policy

Header:

```http
Permissions-Policy:
```

allows applications to restrict browser features.

Example:

```http
Permissions-Policy:
    camera=(),
    microphone=(),
    geolocation=()
```

This disables these features for the document and, depending on policy, embedded contexts.

---

# Browser Features

Permissions Policy can control capabilities such as:

```text
camera
microphone
geolocation
fullscreen
payment
usb
accelerometer
gyroscope
magnetometer
```

Available directives vary as browser standards evolve.

---

# Example Restrictive Policy

```http
Permissions-Policy:
    camera=(),
    microphone=(),
    geolocation=()
```

Applications requiring certain features can selectively allow them.

---

# Permissions Policy Context

Do not blindly recommend:

```text
Disable everything
```

An application may legitimately require:

```text
Camera
Microphone
Location
Payment
```

The policy should match:

```text
Application Requirements
```

while following:

```text
Least Privilege
```

---

# Feature-Policy

Older applications may use:

```http
Feature-Policy:
```

This is the predecessor to:

```text
Permissions-Policy
```

Modern applications should use the current mechanism supported by their browser targets.

---

# X-Frame-Options

Header:

```http
X-Frame-Options:
```

provides protection against framing and clickjacking.

Common values:

```text
DENY
SAMEORIGIN
```

---

# DENY

```http
X-Frame-Options: DENY
```

prevents the page from being framed.

---

# SAMEORIGIN

```http
X-Frame-Options: SAMEORIGIN
```

allows framing by pages from the same origin.

---

# ALLOW-FROM

Legacy value:

```text
ALLOW-FROM
```

has inconsistent or obsolete browser support and should not be relied upon.

Use CSP:

```text
frame-ancestors
```

for modern granular framing policy.

---

# X-Frame-Options vs CSP

Modern protection:

```http
Content-Security-Policy:
    frame-ancestors 'none'
```

Legacy defence-in-depth:

```http
X-Frame-Options: DENY
```

Using both can provide compatibility where required.

---

# Framing Test

Create a local HTML page:

```html
<!doctype html>
<html>
<body>

<iframe
    src="https://target.example/"
    width="1200"
    height="800">
</iframe>

</body>
</html>
```

Open it in a browser.

If the page loads in the frame:

```text
Framing Allowed
```

Whether that creates a vulnerability depends on:

```text
Sensitive actions
UI design
Clickjacking feasibility
```

Refer to:

```text
docs/web/clickjacking.md
```

---

# Cross-Origin-Opener-Policy

Header:

```http
Cross-Origin-Opener-Policy:
```

commonly abbreviated:

```text
COOP
```

COOP controls relationships between browsing contexts.

Example:

```http
Cross-Origin-Opener-Policy:
    same-origin
```

It can isolate the document's browsing context group from cross-origin documents.

---

# COOP Values

Common values include:

```text
unsafe-none
same-origin-allow-popups
same-origin
```

Exact behaviour should be checked against current browser standards.

---

# window.opener

Cross-origin windows can sometimes interact through:

```javascript
window.opener
```

subject to same-origin restrictions.

COOP provides additional isolation between browsing contexts.

---

# COOP and XS-Leaks

COOP can help mitigate certain cross-origin information leaks.

This becomes particularly relevant to:

```text
XS-Leaks
```

which will be covered in:

```text
docs/web/xs-leaks.md
```

---

# Cross-Origin-Embedder-Policy

Header:

```http
Cross-Origin-Embedder-Policy:
```

abbreviated:

```text
COEP
```

Example:

```http
Cross-Origin-Embedder-Policy:
    require-corp
```

COEP controls loading of cross-origin resources in contexts requiring cross-origin isolation.

---

# Cross-Origin-Resource-Policy

Header:

```http
Cross-Origin-Resource-Policy:
```

abbreviated:

```text
CORP
```

Possible values include:

```text
same-site
same-origin
cross-origin
```

CORP allows resources to state which origins may load them in certain contexts.

---

# COOP + COEP

Cross-origin isolation commonly involves:

```text
COOP
+
COEP
```

Conceptually:

```text
Cross-Origin-Opener-Policy
        +
Cross-Origin-Embedder-Policy
        ↓
Cross-Origin Isolated Context
```

This is required for some powerful browser capabilities.

---

# SharedArrayBuffer

Cross-origin isolation is relevant to APIs such as:

```text
SharedArrayBuffer
```

due to historical side-channel concerns.

---

# CORS Is Different

Do not confuse:

```text
CORS
```

with:

```text
COOP
COEP
CORP
```

CORS primarily controls whether JavaScript can read certain cross-origin responses.

Refer to:

```text
docs/web/cors.md
```

---

# Access-Control-Allow-Origin

Example:

```http
Access-Control-Allow-Origin:
    https://trusted.example
```

This is a CORS header.

It should not be assessed simply as:

```text
Present = secure
Missing = insecure
```

CORS requires dedicated origin and credential testing.

Refer to:

```text
docs/web/cors.md
```

---

# Cache-Control

Caching headers are highly relevant for sensitive application responses.

Example:

```http
Cache-Control:
    no-store
```

Sensitive pages may require restrictive caching depending on the application's threat model.

---

# Sensitive Responses

Potentially sensitive responses include:

```text
Account pages
Banking data
Medical information
Authentication responses
Password reset pages
One-time tokens
Private documents
```

---

# no-store

Example:

```http
Cache-Control: no-store
```

instructs caches not to store the response.

---

# no-cache

Important distinction:

```text
no-cache
```

does not mean:

```text
Do Not Store
```

It generally requires revalidation before reuse.

For highly sensitive data:

```text
no-store
```

may be more appropriate.

---

# private

Example:

```http
Cache-Control: private
```

indicates that the response is intended for a private cache rather than a shared cache.

---

# Cache Security

Caching vulnerabilities can become much more serious than a missing header.

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# Clear-Site-Data

Header:

```http
Clear-Site-Data:
```

allows a server to instruct the browser to remove certain stored data.

Example:

```http
Clear-Site-Data:
    "cache", "cookies", "storage"
```

Potential categories include:

```text
cache
cookies
storage
executionContexts
```

Support may vary.

---

# Logout Use Case

A security-sensitive logout process may use Clear-Site-Data as additional defence to remove browser state.

Example:

```http
Clear-Site-Data:
    "cache", "cookies", "storage"
```

This does not replace correct server-side session invalidation.

---

# Clear-Site-Data Limitation

Never treat:

```text
Clear-Site-Data
```

as equivalent to:

```text
Session Revocation
```

Secure logout requires:

```text
Server-Side Session Invalidation
```

where applicable.

Refer to:

```text
docs/web/session-management.md
```

---

# Set-Cookie Security

Although technically not normally grouped with browser policy headers, cookie attributes are critical response security controls.

Example:

```http
Set-Cookie:
    session=ABC;
    Secure;
    HttpOnly;
    SameSite=Lax
```

Important attributes:

```text
Secure
HttpOnly
SameSite
Domain
Path
Expires
Max-Age
```

Refer to:

```text
docs/web/session-management.md
```

---

# Secure

```text
Secure
```

restricts cookie transmission to secure contexts over HTTPS.

---

# HttpOnly

```text
HttpOnly
```

prevents normal JavaScript access to the cookie.

This helps protect session cookies from direct theft through some XSS scenarios.

It does not prevent XSS from performing actions as the victim.

---

# SameSite

Common values:

```text
Strict
Lax
None
```

`SameSite=None` requires:

```text
Secure
```

in modern browsers.

SameSite can provide protection against some CSRF scenarios.

Refer to:

```text
docs/web/csrf.md
```

---

# Legacy Security Headers

Some older headers are still frequently reported by automated scanners.

Examples:

```text
X-XSS-Protection
X-Permitted-Cross-Domain-Policies
Expect-CT
```

Their relevance should be assessed carefully.

---

# X-XSS-Protection

Historical header:

```http
X-XSS-Protection:
```

was associated with browser XSS filters.

Modern browsers have deprecated or removed these mechanisms.

Do not recommend enabling it as the primary XSS defence.

Use:

```text
Output encoding
Safe DOM APIs
CSP
```

instead.

---

# X-XSS-Protection: 0

Modern guidance may intentionally use:

```http
X-XSS-Protection: 0
```

to disable legacy browser XSS filtering behaviour.

Therefore an automated scanner claiming:

```text
X-XSS-Protection Missing
```

should not automatically become a finding.

---

# Expect-CT

Historical header:

```http
Expect-CT:
```

related to Certificate Transparency enforcement.

Modern browsers have largely moved beyond this header as Certificate Transparency requirements became integrated into browser policy.

Do not recommend it automatically.

---

# X-Permitted-Cross-Domain-Policies

Header:

```http
X-Permitted-Cross-Domain-Policies:
```

historically controlled policy files used by products such as Adobe Flash and Acrobat.

Example restrictive value:

```http
X-Permitted-Cross-Domain-Policies:
    none
```

Its relevance is much lower for modern web applications.

Assess according to application context.

---

# Server Header

Example:

```http
Server: nginx/1.18.0
```

This is not a browser security header but frequently appears during header reviews.

Version disclosure can assist reconnaissance.

However:

```text
Version disclosure
```

does not prove:

```text
Known vulnerability exploitable
```

Refer to:

```text
docs/web/information-disclosure.md
```

---

# X-Powered-By

Example:

```http
X-Powered-By: Express
```

or:

```http
X-Powered-By: PHP/8.x
```

This may reveal technology information.

It can often be removed as hardening.

Again:

```text
Information Disclosure
```

should be assessed according to actual impact.

---

# Header Duplication

Look for duplicate security headers.

Example:

```http
X-Frame-Options: DENY
X-Frame-Options: SAMEORIGIN
```

Conflicting values can lead to inconsistent behaviour.

---

# Conflicting CSP

Example:

```http
Content-Security-Policy: default-src 'self'
Content-Security-Policy-Report-Only: default-src *
```

This is not necessarily conflicting because:

```text
One Enforces
One Reports
```

Understand header semantics before reporting.

---

# Reverse Proxy Headers

Security headers may be added by:

```text
Nginx
Apache
Cloudflare
CDN
Load balancer
API gateway
Application framework
```

This can cause inconsistent deployment.

---

# Error Pages

Test:

```text
404
403
500
```

where safely possible.

Example:

```bash
curl -s -D - -o /dev/null \
  https://target.example/this-page-does-not-exist
```

Compare security headers with the normal application response.

---

# Authentication Pages

Prioritise:

```text
/login
/logout
/forgot-password
/reset-password
/mfa
```

because these pages process or expose security-sensitive state.

---

# File Downloads

Inspect headers on:

```text
PDF
CSV
JSON
Images
Uploaded files
Attachments
```

Relevant controls may include:

```text
Content-Type
X-Content-Type-Options
Content-Disposition
Cache-Control
Content-Security-Policy
```

depending on context.

---

# HTML Uploads

If uploaded files can contain:

```text
HTML
SVG
JavaScript
```

then headers become particularly important.

Questions:

```text
Are uploads served from the main origin?

What Content-Type is used?

Is nosniff present?

Is Content-Disposition attachment used?

Does CSP restrict active content?
```

Refer to:

```text
docs/web/file-upload.md
```

---

# SVG Security

SVG can contain active content in some browser contexts.

Serving user-controlled SVG from:

```text
Main Application Origin
```

can create security concerns.

Header review should include:

```text
Content-Type
Content-Disposition
CSP
X-Content-Type-Options
```

---

# JSON Responses

Security headers needed for JSON APIs differ from HTML pages.

For example:

```text
X-Frame-Options
```

may provide little value on a pure JSON endpoint.

Do not apply a universal checklist without context.

---

# API Security Headers

For APIs, prioritise controls such as:

```text
Content-Type
X-Content-Type-Options
Cache-Control
CORS
HSTS
Cookie attributes
```

depending on authentication and response type.

Refer to:

```text
docs/web/api-security.md
```

---

# Header Testing with curl

Basic scriptable inspection:

```bash
curl -s -D - -o /dev/null \
  https://target.example/
```

Filter important headers:

```bash
curl -s -D - -o /dev/null \
  https://target.example/ |
grep -Ei \
'content-security-policy|strict-transport-security|x-content-type-options|referrer-policy|permissions-policy|x-frame-options|cross-origin|cache-control|clear-site-data'
```

---

# Multiple Endpoint Testing

Example:

```bash
for path in \
  / \
  /login \
  /account \
  /forgot-password \
  /api/me
do
    echo
    echo "=== $path ==="

    curl -s -D - -o /dev/null \
      "https://target.example$path" |
    grep -Ei \
    'content-security-policy|strict-transport-security|x-content-type-options|referrer-policy|permissions-policy|x-frame-options|cross-origin|cache-control'
done
```

Use only paths within scope.

---

# Python Header Audit Helper

The following helper checks selected security headers across controlled endpoints.

```python
#!/usr/bin/env python3

import argparse
import requests
from urllib.parse import urljoin


SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Content-Security-Policy-Report-Only",
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "X-Frame-Options",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Embedder-Policy",
    "Cross-Origin-Resource-Policy",
    "Cache-Control",
    "Clear-Site-Data",
]


DEFAULT_PATHS = [
    "/",
    "/login",
    "/account",
    "/forgot-password",
]


def main():

    parser = argparse.ArgumentParser(
        description=(
            "HTTP security header comparison "
            "helper for authorised testing."
        )
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Base URL."
    )

    parser.add_argument(
        "--paths",
        nargs="*",
        default=DEFAULT_PATHS,
        help="Paths to inspect."
    )

    parser.add_argument(
        "--cookie",
        help="Optional Cookie header."
    )

    parser.add_argument(
        "--proxy",
        help=(
            "Optional HTTP proxy, for example "
            "http://127.0.0.1:8080"
        )
    )

    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS verification."
    )

    args = parser.parse_args()

    headers = {
        "User-Agent":
            "Security-Header-Audit/1.0"
    }

    if args.cookie:
        headers["Cookie"] = args.cookie

    proxies = None

    if args.proxy:

        proxies = {
            "http": args.proxy,
            "https": args.proxy,
        }

    for path in args.paths:

        target = urljoin(
            args.url.rstrip("/") + "/",
            path.lstrip("/")
        )

        print()
        print("=" * 80)
        print(target)
        print("=" * 80)

        try:

            response = requests.get(
                target,
                headers=headers,
                timeout=10,
                verify=not args.insecure,
                proxies=proxies,
                allow_redirects=False,
            )

        except requests.RequestException as exc:

            print(
                f"[!] Request failed: {exc}"
            )

            continue

        print(
            f"Status: {response.status_code}"
        )

        print()

        for header in SECURITY_HEADERS:

            value = response.headers.get(
                header
            )

            if value is None:

                print(
                    f"[-] {header}: MISSING"
                )

            else:

                print(
                    f"[+] {header}: {value}"
                )


if __name__ == "__main__":
    main()
```

---

# Usage

```bash
python3 security_headers.py \
  --url https://target.example
```

Custom endpoints:

```bash
python3 security_headers.py \
  --url https://target.example \
  --paths / /login /admin /api/me
```

Through Burp:

```bash
python3 security_headers.py \
  --url https://target.example \
  --proxy http://127.0.0.1:8080 \
  --insecure
```

This creates:

```text
Python
  ↓
Burp Proxy
  ↓
Target
```

allowing every request to remain visible in Burp.

---

# Important Script Limitation

The script reports:

```text
Header Presence
```

not:

```text
Header Security
```

For example:

```text
Content-Security-Policy: script-src *
```

would appear:

```text
Present
```

but may still provide weak protection.

Manual analysis remains essential.

---

# Header Comparison Script

A useful extension is to compare headers across endpoints.

```python
#!/usr/bin/env python3

import argparse
import requests
from urllib.parse import urljoin


HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "x-frame-options",
    "cross-origin-opener-policy",
    "cross-origin-embedder-policy",
    "cross-origin-resource-policy",
    "cache-control",
]


def short(value, length=40):

    if value is None:
        return "MISSING"

    value = value.replace(
        "\n",
        " "
    )

    if len(value) > length:

        return (
            value[:length - 3]
            + "..."
        )

    return value


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        required=True
    )

    parser.add_argument(
        "--paths",
        nargs="+",
        required=True
    )

    parser.add_argument(
        "--insecure",
        action="store_true"
    )

    args = parser.parse_args()

    results = {}

    for path in args.paths:

        url = urljoin(
            args.url.rstrip("/") + "/",
            path.lstrip("/")
        )

        response = requests.get(
            url,
            timeout=10,
            verify=not args.insecure,
            allow_redirects=False,
        )

        results[path] = {
            key: response.headers.get(key)
            for key in HEADERS
        }

    print(
        f"{'HEADER':<38}",
        end=""
    )

    for path in args.paths:

        print(
            f"{path:<45}",
            end=""
        )

    print()

    print(
        "-" * (
            38 +
            (45 * len(args.paths))
        )
    )

    for header in HEADERS:

        print(
            f"{header:<38}",
            end=""
        )

        for path in args.paths:

            value = short(
                results[path][header]
            )

            print(
                f"{value:<45}",
                end=""
            )

        print()


if __name__ == "__main__":
    main()
```

---

# Usage

```bash
python3 compare_headers.py \
  --url https://target.example \
  --paths / /login /account /admin
```

This makes inconsistencies easy to identify.

---

# Nuclei

Nuclei contains templates capable of identifying various:

```text
Missing security headers
Technology disclosures
Misconfigurations
```

Example:

```bash
nuclei \
  -u https://target.example \
  -tags misconfig
```

Template sets change over time.

Always inspect what templates will execute before using them.

Do not automatically report every missing-header result.

---

# testssl.sh

For transport-layer security, `testssl.sh` complements HTTP header testing.

Example:

```bash
./testssl.sh \
  https://target.example
```

It can assist with reviewing:

```text
TLS versions
Cipher suites
Certificates
HSTS
Protocol configuration
```

HTTP security headers and TLS configuration should remain conceptually separate.

---

# SecurityHeaders.com

An external service can provide a quick public header assessment:

```text
https://securityheaders.com/
```

Use only when:

```text
The target is public
External scanning is permitted
Assessment policy allows third-party services
```

Do not submit:

```text
Internal applications
Private hosts
Sensitive customer environments
```

to third-party scanning services without permission.

---

# Mozilla Observatory

Mozilla Observatory provides another public web-security configuration assessment service:

```text
https://developer.mozilla.org/en-US/observatory
```

The same external-service caution applies.

---

# Burp Extensions

Security-header testing generally does not require many specialised extensions because Burp already exposes all response headers.

Useful capabilities include:

```text
Proxy
Repeater
Comparer
Scanner
Logger
Decoder
```

Extensions can supplement these workflows.

---

# Param Miner

Param Miner is primarily designed for discovering hidden:

```text
Headers
Parameters
Cookies
```

It is not a security-header scanner.

However, it can be highly relevant when testing whether hidden request headers influence:

```text
Caching
Routing
Host handling
CORS
Security-header generation
```

Official BApp Store:

```text
https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943
```

Refer to:

```text
docs/web/host-header-attacks.md
docs/web/web-cache-poisoning.md
```

---

# CSP Analysis in Burp

For CSP:

```text
Proxy
  ↓
Find Content-Security-Policy
  ↓
Send Response / Policy for Review
  ↓
Identify Directives
  ↓
Identify Broad Sources
  ↓
Identify Nonces / Hashes
  ↓
Identify unsafe-inline / unsafe-eval
  ↓
Identify Trusted Third Parties
  ↓
Test Relevant XSS Context
```

---

# CSP Testing Checklist

```text
[ ] CSP present
[ ] Enforcement policy present
[ ] Report-only distinguished from enforcement
[ ] default-src reviewed
[ ] script-src reviewed
[ ] unsafe-inline reviewed
[ ] unsafe-eval reviewed
[ ] wildcard sources reviewed
[ ] data: reviewed
[ ] blob: reviewed
[ ] trusted domains reviewed
[ ] nonce usage reviewed
[ ] nonce reuse tested
[ ] hashes reviewed
[ ] strict-dynamic reviewed
[ ] object-src reviewed
[ ] base-uri reviewed
[ ] form-action reviewed
[ ] frame-ancestors reviewed
[ ] connect-src reviewed
[ ] upload origin interaction reviewed
```

---

# HSTS Testing Checklist

```text
[ ] HTTPS available
[ ] HTTP behaviour tested
[ ] HTTP redirects to HTTPS
[ ] HSTS present on HTTPS
[ ] max-age reviewed
[ ] max-age not zero
[ ] includeSubDomains considered
[ ] preload status not inferred from directive alone
[ ] sensitive subdomains considered
```

---

# X-Content-Type-Options Checklist

```text
[ ] nosniff present
[ ] Correct value
[ ] HTML responses reviewed
[ ] JavaScript responses reviewed
[ ] Stylesheets reviewed
[ ] User uploads reviewed
[ ] File downloads reviewed
[ ] MIME types correct
```

---

# Referrer-Policy Checklist

```text
[ ] Policy present
[ ] Policy value reviewed
[ ] Sensitive URLs identified
[ ] Reset-token pages reviewed
[ ] Cross-origin navigation tested where relevant
[ ] Third-party resources reviewed
[ ] unsafe-url avoided where inappropriate
```

---

# Permissions-Policy Checklist

```text
[ ] Policy present where useful
[ ] Camera requirement reviewed
[ ] Microphone requirement reviewed
[ ] Geolocation requirement reviewed
[ ] Payment requirement reviewed
[ ] Unused powerful features restricted
[ ] Embedded content considered
```

---

# Framing Checklist

```text
[ ] X-Frame-Options reviewed
[ ] CSP frame-ancestors reviewed
[ ] Policies consistent
[ ] Sensitive pages tested
[ ] Framing manually tested
[ ] Clickjacking impact assessed
```

---

# Cross-Origin Isolation Checklist

```text
[ ] COOP reviewed
[ ] COEP reviewed
[ ] CORP reviewed
[ ] Application requirements understood
[ ] SharedArrayBuffer use considered
[ ] XS-Leak relevance considered
[ ] CORS not confused with COOP/COEP/CORP
```

---

# Cache Checklist

```text
[ ] Sensitive responses identified
[ ] Cache-Control reviewed
[ ] no-store considered
[ ] private considered
[ ] Authentication responses reviewed
[ ] Reset pages reviewed
[ ] Personal data responses reviewed
[ ] Shared cache behaviour considered
```

---

# Cookie Checklist

```text
[ ] Secure
[ ] HttpOnly
[ ] SameSite
[ ] Domain
[ ] Path
[ ] Expiration
[ ] Session rotation
[ ] Authentication state
```

Refer to:

```text
docs/web/session-management.md
```

for complete cookie testing.

---

# Full Security Header Checklist

## Discovery

```text
[ ] Homepage
[ ] Login
[ ] Logout
[ ] Account
[ ] Admin
[ ] Password reset
[ ] MFA
[ ] API
[ ] Error pages
[ ] File downloads
[ ] User uploads
```

## CSP

```text
[ ] Content-Security-Policy
[ ] Report-only
[ ] default-src
[ ] script-src
[ ] unsafe-inline
[ ] unsafe-eval
[ ] nonces
[ ] hashes
[ ] strict-dynamic
[ ] object-src
[ ] base-uri
[ ] form-action
[ ] frame-ancestors
[ ] connect-src
[ ] Trusted origins
```

## Transport

```text
[ ] HTTPS
[ ] HTTP redirect
[ ] HSTS
[ ] max-age
[ ] includeSubDomains
```

## MIME

```text
[ ] Content-Type
[ ] X-Content-Type-Options
[ ] User uploads
[ ] Downloads
```

## Referrer

```text
[ ] Referrer-Policy
[ ] Sensitive URLs
[ ] External links
[ ] Third-party resources
```

## Browser Features

```text
[ ] Permissions-Policy
[ ] Camera
[ ] Microphone
[ ] Geolocation
[ ] Other required capabilities
```

## Framing

```text
[ ] X-Frame-Options
[ ] frame-ancestors
[ ] Manual frame test
```

## Cross-Origin Isolation

```text
[ ] COOP
[ ] COEP
[ ] CORP
```

## Caching

```text
[ ] Cache-Control
[ ] Sensitive responses
[ ] Shared caches
```

## Browser Storage

```text
[ ] Clear-Site-Data where relevant
[ ] Logout behaviour
```

## Cookies

```text
[ ] Secure
[ ] HttpOnly
[ ] SameSite
```

## Information Disclosure

```text
[ ] Server
[ ] X-Powered-By
[ ] Framework headers
[ ] Internal proxy headers
```

## Consistency

```text
[ ] Normal pages
[ ] Error pages
[ ] Authenticated pages
[ ] Unauthenticated pages
[ ] Legacy endpoints
[ ] APIs
[ ] Static content
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Comparer
[ ] Scanner
[ ] Logger
[ ] Decoder
[ ] Param Miner where relevant
```

## External Tools

```text
[ ] curl
[ ] testssl.sh
[ ] Nuclei where authorised
[ ] CSP Evaluator
[ ] Browser DevTools
[ ] External scanning services only when permitted
```

---

# Common Findings

Examples include:

```text
Content Security Policy Allows Unsafe Script Execution

Content Security Policy Is Configured in Report-Only Mode

Content Security Policy Trusts Broad Script Sources

Static CSP Nonce Reused Across Responses

Missing Strict-Transport-Security Header

Strict-Transport-Security Configured with Zero max-age

Missing X-Content-Type-Options Header

Sensitive Pages Use Weak Referrer Policy

Application Can Be Framed Due to Missing Framing Restrictions

Sensitive Responses Are Cacheable

Inconsistent Security Headers Across Application Endpoints

Security Headers Missing from Error Responses
```

---

# Finding: Weak CSP

Example:

```text
Finding:
Content Security Policy Allows Unsafe Script Execution

Observed:
The application returns a Content-Security-Policy header containing script-src directives that permit unsafe script execution mechanisms.

The policy includes unsafe-inline and unsafe-eval, which significantly reduce the protection CSP can provide against certain client-side injection attacks.

Impact:
The configuration weakens the application's defence-in-depth protection against cross-site scripting and related client-side attacks.

The presence of these directives does not itself create XSS, but may increase the impact of an independently exploitable injection vulnerability.

Recommendation:
Refactor the application to avoid inline JavaScript and string-based code execution where practical. Use external scripts from explicitly trusted origins and consider a nonce- or hash-based Content Security Policy. Test the resulting policy thoroughly before enforcement.
```

---

# Finding: CSP Report-Only

```text
Finding:
Content Security Policy Is Not Enforced

Observed:
The application returns a Content-Security-Policy-Report-Only header but does not return an enforcing Content-Security-Policy header.

Report-only policies generate violation reports but do not instruct the browser to block policy violations.

Impact:
The application does not currently receive the preventative security benefits of Content Security Policy.

An existing cross-site scripting or client-side injection vulnerability would therefore not be blocked by the report-only policy.

Recommendation:
Use report-only mode during policy development and compatibility testing, then deploy a tested Content-Security-Policy enforcement header. Continue report-only monitoring separately if required.
```

---

# Finding: Missing HSTS

```text
Finding:
HTTP Strict Transport Security Is Not Enabled

Observed:
The application is available over HTTPS but does not return a Strict-Transport-Security header.

Impact:
Users who have not established another browser-level HTTPS protection may be more exposed to HTTP downgrade or SSL-stripping scenarios if they initially attempt to access the application over an insecure connection.

The practical risk depends on HTTP availability, redirect behaviour, browser preload status and the application's sensitivity.

Recommendation:
After confirming that the application and relevant subdomains operate correctly over HTTPS, configure an appropriate Strict-Transport-Security policy. Select max-age and includeSubDomains according to the organisation's deployment requirements and consider HSTS preloading only after confirming all preload requirements can be safely maintained.
```

---

# Finding: Missing nosniff

```text
Finding:
MIME Sniffing Protection Is Not Enabled

Observed:
Application responses do not include:

X-Content-Type-Options: nosniff

Impact:
In relevant browser contexts, MIME-type sniffing may cause content to be interpreted differently from the declared Content-Type.

The security impact is particularly relevant where user-controlled or uploaded content is served by the application.

Recommendation:
Return X-Content-Type-Options: nosniff and ensure all resources are served with accurate Content-Type headers.
```

---

# Finding: Weak Referrer Policy

```text
Finding:
Sensitive URL Information May Be Disclosed Through Referrer Headers

Observed:
The application uses a permissive Referrer-Policy on pages containing security-sensitive URL parameters.

Navigation from these pages to external origins may disclose more URL information than required.

Impact:
Sensitive values contained in URLs may be exposed to third-party origins through the Referer header.

Depending on the affected functionality, this could include identifiers or temporary security tokens.

Recommendation:
Avoid placing sensitive information in URLs where possible and configure an appropriately restrictive Referrer-Policy, such as strict-origin-when-cross-origin or a stricter policy where application requirements permit.
```

---

# Finding: Missing Framing Protection

```text
Finding:
Application Can Be Framed by External Origins

Observed:
The affected page does not return an effective Content-Security-Policy frame-ancestors directive or X-Frame-Options header.

Testing confirmed that the page could be embedded within an iframe hosted on an external origin.

Impact:
If sensitive user actions can be visually overlaid or manipulated, an attacker may be able to construct a clickjacking attack.

Recommendation:
Define an appropriate framing policy using the Content-Security-Policy frame-ancestors directive. Where legacy browser compatibility is required, also configure X-Frame-Options consistently.
```

For complete clickjacking validation:

```text
docs/web/clickjacking.md
```

---

# Finding: Sensitive Response Cacheable

```text
Finding:
Sensitive Authenticated Responses May Be Stored in Browser or Intermediate Caches

Observed:
Authenticated responses containing sensitive account information were returned without a restrictive caching policy.

Impact:
Sensitive information may remain available in browser or intermediary cache storage depending on the surrounding caching architecture.

Recommendation:
Review caching requirements for authenticated and sensitive responses. Use appropriate Cache-Control directives, including no-store where responses must not be retained, and ensure shared caches do not store user-specific content.
```

---

# Reporting Severity

Do not automatically rate:

```text
Missing Security Header
```

as:

```text
Medium
```

or:

```text
High
```

Severity depends on actual security impact.

Example:

```text
Missing Permissions-Policy
with no sensitive browser capabilities
→ Informational / Hardening
```

```text
Missing X-Frame-Options
but CSP frame-ancestors 'none'
→ No issue
```

```text
Missing X-Frame-Options
and no frame-ancestors
but no actionable UI
→ Low / Informational
```

```text
Missing framing protection
with exploitable sensitive action
→ Clickjacking finding
```

```text
Weak CSP
without XSS
→ Hardening / Low depending on policy
```

```text
Weak CSP
combined with exploitable XSS
→ XSS severity driven by demonstrated impact
```

---

# Avoid Header Checklist Reporting

A poor assessment approach is:

```text
Header Missing
     ↓
Automatically Report
```

A stronger approach:

```text
Header Missing / Weak
        ↓
What Security Property
Would It Provide?
        ↓
Does the Application Need It?
        ↓
Can Relevant Behaviour
Be Demonstrated?
        ↓
Security Impact?
   ↓             ↓
  YES            NO
   ↓             ↓
REPORT       HARDENING /
            NO FINDING
```

---

# Remediation Strategy

Security headers should ideally be configured centrally.

Possible locations:

```text
Reverse Proxy
Web Server
Application Framework
API Gateway
CDN
```

Central configuration reduces inconsistent deployment.

---

# Example Nginx Configuration

Conceptual example:

```nginx
add_header X-Content-Type-Options "nosniff" always;

add_header Referrer-Policy
    "strict-origin-when-cross-origin"
    always;

add_header X-Frame-Options
    "DENY"
    always;

add_header Strict-Transport-Security
    "max-age=31536000; includeSubDomains"
    always;
```

CSP should be application-specific rather than blindly copied.

Example:

```nginx
add_header Content-Security-Policy
    "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    always;
```

Do not deploy this without compatibility testing.

---

# Example Apache Configuration

Conceptual example:

```apache
Header always set X-Content-Type-Options "nosniff"

Header always set Referrer-Policy \
"strict-origin-when-cross-origin"

Header always set X-Frame-Options "DENY"

Header always set Strict-Transport-Security \
"max-age=31536000; includeSubDomains"
```

CSP again requires application-specific design.

---

# Example Express Configuration

Node.js applications commonly use middleware such as Helmet.

Conceptually:

```javascript
const helmet = require("helmet");

app.use(
    helmet()
);
```

Then customise policies according to application requirements.

Do not assume framework defaults match every threat model.

---

# Example Spring Security

Spring Security can configure browser security headers centrally.

The exact configuration depends on:

```text
Spring Security version
Application architecture
Existing proxy configuration
```

Avoid duplicating conflicting policies between:

```text
Spring
Nginx
CDN
```

---

# Header Deployment Architecture

A common secure pattern:

```text
Internet
   ↓
CDN / WAF
   ↓
Reverse Proxy
   ↓
Application
```

Security headers may be generated at:

```text
CDN
Proxy
Application
```

Choose clear ownership.

Otherwise:

```text
Application Header
       +
Proxy Header
       +
CDN Header
       ↓
Duplicates / Conflicts
```

---

# Test After Remediation

Never stop at:

```text
Header Added
```

Retest:

```text
Normal pages
Authentication pages
Error pages
APIs
Downloads
Uploads
Redirects
```

For CSP specifically:

```text
Application still works?
Scripts load?
Styles load?
API calls work?
Frames work as intended?
XSS vectors blocked?
```

---

# CSP Deployment Strategy

A practical CSP deployment workflow:

```text
Inventory Resources
        ↓
Create Initial Policy
        ↓
Report-Only
        ↓
Collect Violations
        ↓
Fix Application Dependencies
        ↓
Reduce Trusted Sources
        ↓
Introduce Nonces / Hashes
        ↓
Test
        ↓
Enforce CSP
        ↓
Continue Monitoring
```

---

# Security Headers Quick Reference

| Header | Primary Purpose |
|---|---|
| Content-Security-Policy | Restrict browser resource execution/loading |
| Strict-Transport-Security | Enforce HTTPS usage |
| X-Content-Type-Options | Prevent MIME sniffing |
| Referrer-Policy | Limit referrer information |
| Permissions-Policy | Restrict browser capabilities |
| X-Frame-Options | Legacy framing restriction |
| CSP frame-ancestors | Modern framing restriction |
| COOP | Browsing-context isolation |
| COEP | Cross-origin embedding policy |
| CORP | Resource embedding policy |
| Cache-Control | Control caching |
| Clear-Site-Data | Clear browser site data |
| Set-Cookie attributes | Protect cookies |

---

# Recommended Baseline

A general modern baseline might include:

```http
Strict-Transport-Security:
    max-age=31536000

X-Content-Type-Options:
    nosniff

Referrer-Policy:
    strict-origin-when-cross-origin

Permissions-Policy:
    camera=(), microphone=(), geolocation=()
```

and an application-specific:

```http
Content-Security-Policy:
```

with an appropriate:

```text
frame-ancestors
```

directive.

However:

```text
There Is No Universal Header Template
```

that should be copied to every application.

---

# Pentester Quick Workflow

```text
curl Headers
     ↓
Burp Proxy
     ↓
Browse Major Endpoints
     ↓
Build Header Matrix
     ↓
CSP Deep Review
     ↓
HSTS Review
     ↓
MIME Review
     ↓
Referrer Review
     ↓
Permissions Review
     ↓
Framing Test
     ↓
COOP / COEP / CORP
     ↓
Cache Review
     ↓
Cookie Review
     ↓
Error Pages
     ↓
Uploads / Downloads
     ↓
API Responses
     ↓
Manual Impact Validation
     ↓
Report Only Relevant Findings
```

---

# References

## OWASP HTTP Headers Cheat Sheet

[OWASP HTTP Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)

Primary OWASP guidance for HTTP response security headers.

---

## OWASP Content Security Policy Cheat Sheet

[OWASP Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

Guidance for deploying CSP.

---

## OWASP HTTP Strict Transport Security Cheat Sheet

[OWASP HTTP Strict Transport Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html)

Guidance for HSTS deployment.

---

## OWASP Clickjacking Defense Cheat Sheet

[OWASP Clickjacking Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)

Relevant to:

```text
X-Frame-Options
frame-ancestors
```

---

## OWASP Cross-Site Scripting Prevention Cheat Sheet

[OWASP Cross-Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

Important for understanding CSP as defence in depth rather than a substitute for correct output handling.

---

## MDN Content-Security-Policy

[MDN Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy)

---

## MDN Strict-Transport-Security

[MDN Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security)

---

## MDN X-Content-Type-Options

[MDN X-Content-Type-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Content-Type-Options)

---

## MDN Referrer-Policy

[MDN Referrer-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy)

---

## MDN Permissions-Policy

[MDN Permissions-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Permissions-Policy)

---

## MDN X-Frame-Options

[MDN X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options)

---

## MDN Cross-Origin-Opener-Policy

[MDN Cross-Origin-Opener-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy)

---

## MDN Cross-Origin-Embedder-Policy

[MDN Cross-Origin-Embedder-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy)

---

## MDN Cross-Origin-Resource-Policy

[MDN Cross-Origin-Resource-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy)

---

## PortSwigger Content Security Policy

[PortSwigger Content Security Policy](https://portswigger.net/web-security/cross-site-scripting/content-security-policy)

Useful for understanding CSP behaviour and its relationship with XSS.

---

## PortSwigger Clickjacking

[PortSwigger Clickjacking](https://portswigger.net/web-security/clickjacking)

Relevant to framing protections.

---

## PortSwigger CORS

[PortSwigger CORS](https://portswigger.net/web-security/cors)

Relevant to cross-origin response headers.

---

## PortSwigger Web Cache Poisoning

[PortSwigger Web Cache Poisoning](https://portswigger.net/web-security/web-cache-poisoning)

Relevant when headers interact with caching behaviour.

---

## Param Miner

[Param Miner](https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943)

Useful for identifying hidden headers and parameters that influence server behaviour.

---

## Google CSP Evaluator

[Google CSP Evaluator](https://csp-evaluator.withgoogle.com/)

Useful for assisting with CSP analysis.

---

## Security Headers

[Security Headers](https://securityheaders.com/)

External header analysis service. Use only for public targets where third-party scanning is permitted.

---

## Mozilla Observatory

[Mozilla Observatory](https://developer.mozilla.org/en-US/observatory)

External web-security configuration analysis service.

---

# Final HTTP Security Headers Testing Model

```text
                       HTTP RESPONSE
                             ↓
                      ENUMERATE HEADERS
                             ↓
             ┌───────────────┼─────────────────┐
             ↓               ↓                 ↓
            CSP             HSTS             MIME
             ↓               ↓                 ↓
         SCRIPT /         HTTPS            NOSNIFF
         RESOURCE        ENFORCEMENT           ↓
         CONTROL             ↓             CONTENT TYPE
             │               │                 │
             └───────────────┼─────────────────┘
                             ↓
                       PRIVACY CONTROLS
                             ↓
               ┌─────────────┼──────────────┐
               ↓             ↓              ↓
           REFERRER      PERMISSIONS      CACHE
            POLICY         POLICY          CONTROL
               └─────────────┼──────────────┘
                             ↓
                        FRAMING POLICY
                             ↓
                    ┌────────┴────────┐
                    ↓                 ↓
              frame-ancestors   X-Frame-Options
                    └────────┬────────┘
                             ↓
                    CROSS-ORIGIN POLICY
                             ↓
                 ┌───────────┼───────────┐
                 ↓           ↓           ↓
                COOP        COEP        CORP
                 └───────────┼───────────┘
                             ↓
                       COOKIE SECURITY
                             ↓
                 ┌───────────┼───────────┐
                 ↓           ↓           ↓
               Secure      HttpOnly    SameSite
                 └───────────┼───────────┘
                             ↓
                    CONSISTENCY TESTING
                             ↓
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
        NORMAL             ERROR              AUTH
        PAGES              PAGES              PAGES
          ↓                  ↓                  ↓
        API              DOWNLOADS           UPLOADS
          └──────────────────┼──────────────────┘
                             ↓
                      HEADER MISSING?
                         ↓         ↓
                        NO        YES
                         ↓         ↓
                   VALUE SAFE?   SECURITY
                     ↓    ↓      PROPERTY?
                    YES   NO       ↓
                     ↓    ↓    RELEVANT?
                  CONTINUE ↓      ↓    ↓
                          WEAK   YES   NO
                           ↓     ↓     ↓
                           └──┬──┘  HARDENING
                              ↓
                       PRACTICAL IMPACT?
                         ↓          ↓
                        YES         NO
                         ↓          ↓
                       REPORT    CONTEXTUAL
                                  REVIEW
                             ↓
                       REMEDIATION
                             ↓
                  CENTRAL CONFIGURATION
                             ↓
                         RETEST
```

The central principle is:

> HTTP security headers should be assessed according to the browser security property they provide and the application's actual attack surface, not through a simple presence-or-absence checklist. CSP requires detailed policy analysis, HSTS must be evaluated alongside HTTPS behaviour, framing controls must be validated against clickjacking risk, and caching, referrer, MIME and cross-origin policies should be tested where they protect sensitive application behaviour. Missing headers without meaningful security impact are generally hardening observations rather than automatically exploitable vulnerabilities.
