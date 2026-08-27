# Cross-Origin Resource Sharing (CORS)

Cross-Origin Resource Sharing (CORS) is a browser security mechanism that allows a web application to selectively permit other origins to access its resources.

CORS is not a vulnerability by itself.

A vulnerability occurs when an application's CORS policy incorrectly trusts an attacker-controlled or otherwise untrusted origin, potentially allowing that origin to read sensitive responses from the victim's browser.

A simplified model is:

```text
Attacker-Controlled Origin
          ↓
Victim Browser
          ↓
Cross-Origin Request
          ↓
Target Application
          ↓
CORS Policy Evaluated
          ↓
Browser Allows Response?
          ↓
Sensitive Data Read
```

The central testing question is:

> Can an untrusted origin cause a victim's browser to make an authenticated or otherwise sensitive request and then read the response?

!!! warning "Authorised Security Testing"
    Perform CORS testing only against applications included in the authorised assessment scope. Use controlled accounts and controlled origins when demonstrating cross-origin access to sensitive information.

---

# Same-Origin Policy

Understanding CORS requires understanding the Same-Origin Policy.

The Same-Origin Policy restricts how content from one origin can interact with resources from another origin.

An origin consists primarily of:

```text
Scheme
Host
Port
```

For example:

```text
https://app.example.com:443
```

contains:

```text
Scheme → https
Host   → app.example.com
Port   → 443
```

Changing one of these components can create a different origin.

---

# Origin Examples

Consider:

```text
https://example.com
```

The following are different origins:

```text
http://example.com
https://sub.example.com
https://example.com:8443
https://another.example
```

Even though some may belong to the same organisation, they are not necessarily the same browser origin.

---

# Same-Origin Policy Model

Without CORS:

```text
Origin A
   ↓
JavaScript Request
   ↓
Origin B
   ↓
Response
   ↓
Browser Blocks Origin A
from Reading Response
```

The request may still reach the server.

The Same-Origin Policy primarily controls whether the requesting JavaScript can access the response.

---

# What CORS Changes

CORS allows the server to tell the browser:

```text
This origin is permitted to read this response.
```

For example:

```http
Access-Control-Allow-Origin: https://trusted.example
```

The browser compares the requesting origin with the value returned by the server.

If the policy permits the origin, JavaScript may be allowed to access the response.

---

# Basic CORS Request

Suppose JavaScript running on:

```text
https://client.example
```

requests:

```text
https://api.example/account
```

The browser may send:

```http
GET /account HTTP/1.1
Host: api.example
Origin: https://client.example
```

The server may respond:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: https://client.example
```

The browser then determines whether the response can be exposed to the calling JavaScript.

---

# Origin Header

The primary request header during CORS testing is:

```http
Origin:
```

Example:

```http
Origin: https://example.com
```

When testing manually with Burp Suite, changing the `Origin` header is one of the easiest ways to understand the server's CORS policy.

---

# Access-Control-Allow-Origin

The most important response header is:

```http
Access-Control-Allow-Origin:
```

Examples include:

```http
Access-Control-Allow-Origin: https://trusted.example
```

```http
Access-Control-Allow-Origin: *
```

```http
Access-Control-Allow-Origin: null
```

The security implications depend on the complete policy and the type of resource being accessed.

---

# Access-Control-Allow-Credentials

Another important response header is:

```http
Access-Control-Allow-Credentials: true
```

This indicates that the response may be exposed to credentialed cross-origin requests when the rest of the CORS requirements are satisfied.

Credentials may include browser-managed authentication information such as cookies.

A particularly important combination to investigate is:

```http
Access-Control-Allow-Origin: https://attacker-controlled.example
Access-Control-Allow-Credentials: true
```

if the origin is not legitimately trusted.

---

# Important CORS Headers

During testing, look for:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Access-Control-Allow-Methods
Access-Control-Allow-Headers
Access-Control-Expose-Headers
Access-Control-Max-Age
Vary
```

Each reveals part of the application's CORS behaviour.

---

# Access-Control-Allow-Methods

Example:

```http
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
```

This tells the browser which methods may be permitted for relevant cross-origin requests.

This header alone does not establish a vulnerability.

---

# Access-Control-Allow-Headers

Example:

```http
Access-Control-Allow-Headers: Authorization, Content-Type
```

This can permit requests containing headers that are not automatically allowed in simple cross-origin requests.

---

# Access-Control-Expose-Headers

Browsers expose only certain response headers to cross-origin JavaScript by default.

An application can expose additional headers:

```http
Access-Control-Expose-Headers: X-Request-ID
```

or:

```http
Access-Control-Expose-Headers: X-Custom-Header
```

Review whether sensitive information is placed in exposed response headers.

---

# Access-Control-Max-Age

Example:

```http
Access-Control-Max-Age: 600
```

This allows the browser to cache the result of a preflight request for a period of time.

It is generally not a vulnerability by itself.

---

# Vary: Origin

When a server dynamically returns different CORS responses depending on the request origin, responses should generally account for the `Origin` header in caching behaviour.

For example:

```http
Vary: Origin
```

This can be important when responses pass through:

```text
CDNs
Reverse proxies
Shared caches
```

Incorrect caching can create unexpected cross-origin behaviour.

---

# Simple Requests

Some cross-origin requests can be sent without a preflight.

These are often referred to as:

```text
Simple requests
```

A simplified example:

```http
GET /profile HTTP/1.1
Host: target.example
Origin: https://client.example
```

The server responds normally.

The browser then decides whether JavaScript is allowed to read the response.

---

# Preflight Requests

Certain cross-origin requests cause the browser to send an `OPTIONS` request first.

This is called a:

```text
Preflight request
```

A simplified flow is:

```text
JavaScript
    ↓
Browser
    ↓
OPTIONS Request
    ↓
Server CORS Policy
    ↓
Browser Evaluates Policy
    ↓
Actual Request
```

---

# Example Preflight

Request:

```http
OPTIONS /api/account HTTP/1.1
Host: target.example
Origin: https://client.example
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Authorization, Content-Type
```

Possible response:

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://client.example
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Authorization, Content-Type
```

The browser evaluates this response before deciding whether to make the actual request.

---

# Access-Control-Request-Method

During a preflight, the browser may send:

```http
Access-Control-Request-Method: PUT
```

This tells the server which method the subsequent request intends to use.

---

# Access-Control-Request-Headers

The browser may also send:

```http
Access-Control-Request-Headers: authorization, content-type
```

The server then determines whether those headers are allowed.

---

# CORS Testing Methodology

A structured workflow looks like:

```text
Identify Endpoint
      ↓
Determine Whether Response Is Sensitive
      ↓
Add Origin Header
      ↓
Observe CORS Response
      ↓
Test Trusted Origin
      ↓
Test Untrusted Origin
      ↓
Test Origin Validation
      ↓
Check Credentials
      ↓
Check null Origin
      ↓
Check Subdomains
      ↓
Check Preflight Behaviour
      ↓
Verify in Browser
      ↓
Assess Impact
```

---

# Start With Sensitive Endpoints

CORS matters most when the affected response contains information that should not be readable by an untrusted origin.

Prioritise endpoints such as:

```text
/api/account
/api/profile
/api/user
/api/me
/api/settings
/api/orders
/api/payments
/api/messages
/api/admin
/api/notifications
/api/documents
```

The exact endpoints depend on the application.

---

# Baseline Request

Start with the normal request.

Example:

```http
GET /api/account HTTP/1.1
Host: target.example
Cookie: session=CONTROLLED_SESSION
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "username": "test-user",
    "email": "test@example.com"
}
```

Establish that the endpoint contains information worth protecting.

---

# Add an Origin Header

Now add:

```http
Origin: https://example.com
```

Request:

```http
GET /api/account HTTP/1.1
Host: target.example
Origin: https://example.com
Cookie: session=CONTROLLED_SESSION
```

Inspect the response.

---

# Secure Example

The application may return:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

without:

```http
Access-Control-Allow-Origin:
```

The server still returns the response to Burp because Burp is not enforcing browser CORS restrictions.

A browser, however, would not expose that response to JavaScript from the untrusted origin.

This distinction is critical.

---

# Potentially Vulnerable Example

Request:

```http
GET /api/account HTTP/1.1
Host: target.example
Origin: https://example.com
Cookie: session=CONTROLLED_SESSION
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Credentials: true
```

If:

```text
https://example.com
```

represents an untrusted or attacker-controlled origin, investigate further.

---

# Origin Reflection

One common implementation pattern is reflecting the supplied `Origin` value.

For example:

Request:

```http
Origin: https://random.example
```

Response:

```http
Access-Control-Allow-Origin: https://random.example
```

Then:

```http
Origin: https://another.example
```

Response:

```http
Access-Control-Allow-Origin: https://another.example
```

This suggests the server may be dynamically reflecting arbitrary origins.

---

# Origin Reflection Workflow

Test several clearly distinct origins:

```text
https://example.com
https://test.example
https://untrusted.invalid
```

Observe whether:

```text
No origins are reflected
Only trusted origins are reflected
All origins are reflected
Some pattern is reflected
```

Do not infer arbitrary reflection from a single request.

---

# Arbitrary Origin Reflection

A dangerous policy may conceptually behave like:

```text
Request Origin
      ↓
Copy Value
      ↓
Access-Control-Allow-Origin
```

without validating whether the origin belongs to a trusted allowlist.

Example:

```http
Origin: https://untrusted.example
```

Response:

```http
Access-Control-Allow-Origin: https://untrusted.example
Access-Control-Allow-Credentials: true
```

If sensitive authenticated data is accessible, this may allow cross-origin data theft.

---

# Credentialed CORS

Credentialed CORS is particularly important.

A browser request may conceptually look like:

```javascript
fetch("https://target.example/api/account", {
    credentials: "include"
});
```

The target must return an appropriate CORS policy before the browser exposes the response to the calling origin.

If an attacker-controlled origin is trusted and credentials are included, sensitive authenticated responses may become readable.

---

# Browser Proof of Concept

For an authorised controlled test, a simple page can demonstrate whether a target response is readable cross-origin.

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>CORS Test</title>
</head>

<body>

<h1>Authorised CORS Test</h1>

<pre id="output">Waiting...</pre>

<script>

fetch("https://target.example/api/account", {
    credentials: "include"
})
.then(response => response.text())
.then(data => {
    document.getElementById("output").textContent = data;
})
.catch(error => {
    document.getElementById("output").textContent = error;
});

</script>

</body>

</html>
```

Use this only with controlled accounts and controlled origins.

The objective is to demonstrate whether the browser exposes the response, not to collect information belonging to other users.

---

# Why Browser Verification Matters

Burp Suite does not enforce the Same-Origin Policy.

Therefore:

```text
Burp receives response
```

does not mean:

```text
Cross-origin JavaScript can read response
```

The browser is the security enforcement point.

A good workflow is:

```text
Burp
 ↓
Understand Policy
 ↓
Browser
 ↓
Verify Exploitability
```

---

# Wildcard Origin

An application may return:

```http
Access-Control-Allow-Origin: *
```

This allows any origin to access certain cross-origin responses.

However, the security impact depends on the resource and credential requirements.

---

# Wildcard and Credentials

Browsers do not permit the combination:

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

to provide credentialed access in the same way as an explicitly allowed origin.

Therefore, do not automatically report:

```text
ACAO: *
```

as a critical CORS vulnerability.

Determine:

```text
Is the endpoint public?

Does it contain sensitive information?

Does it require credentials?

Are bearer tokens used separately?

Can an attacker access anything they should not?
```

---

# Public APIs

A public endpoint may intentionally return:

```http
Access-Control-Allow-Origin: *
```

Example:

```text
Public product catalogue
Public documentation
Public status data
Public search API
```

This is not necessarily a vulnerability.

Always evaluate the sensitivity of the response.

---

# Bearer Tokens

Some applications authenticate using:

```http
Authorization: Bearer TOKEN
```

instead of cookies.

Cross-origin exploitation may then depend on whether an attacker can cause the browser to include the required token.

If the token is only accessible to trusted JavaScript and not automatically attached cross-origin, a permissive CORS response may have different practical impact.

Analyse the complete authentication model.

---

# Testing Trusted Origins

Determine which origins are intentionally trusted.

Examples:

```text
https://app.example.com
https://portal.example.com
https://admin.example.com
```

Then test how the application validates them.

The goal is not simply to enumerate accepted strings.

The goal is to understand the trust model.

---

# Weak Origin Validation

A weak implementation may use string operations such as:

```text
startsWith()
endsWith()
contains()
regular expressions
```

instead of properly parsing the origin.

This can create trust-boundary mistakes.

---

# Prefix Matching

Suppose the intended trusted origin is:

```text
https://trusted.example
```

A weak policy might conceptually accept anything beginning with:

```text
https://trusted.example
```

The tester should determine whether the implementation validates the complete parsed origin or only a string prefix.

---

# Suffix Matching

Similarly, an implementation may attempt to trust:

```text
example.com
```

using a suffix check.

The important question is whether hostname boundaries are correctly enforced.

Do not assume:

```text
contains example.com
```

means:

```text
is a subdomain of example.com
```

---

# Origin Parsing

An origin should be interpreted using proper URL parsing.

Security decisions should consider:

```text
Scheme
Hostname
Port
```

rather than arbitrary string fragments.

---

# Subdomain Trust

Some applications intentionally trust:

```text
*.example.com
```

This should immediately raise another question:

> Are all subdomains equally trusted?

Potential subdomains may include:

```text
Production applications
Development environments
Legacy systems
Marketing sites
User-generated content
Third-party services
Abandoned DNS records
```

A broad subdomain trust policy can become dangerous if one trusted subdomain is compromised or attacker-controlled.

---

# CORS and Subdomain Takeover

Consider:

```text
Target API trusts *.example.com
```

and:

```text
old.example.com
```

is vulnerable to subdomain takeover.

Conceptually:

```text
Attacker Controls old.example.com
          ↓
Origin Is Still Trusted
          ↓
Victim Visits Attacker-Controlled Subdomain
          ↓
Cross-Origin Request to API
          ↓
API Trusts Origin
          ↓
Sensitive Response Exposed
```

This demonstrates why CORS trust should not automatically extend to every organisational subdomain.

---

# CORS and XSS on Trusted Origins

A similar issue can occur if:

```text
API trusts portal.example.com
```

and:

```text
portal.example.com
```

contains an exploitable XSS vulnerability.

Conceptually:

```text
XSS on Trusted Origin
       ↓
JavaScript Executes
       ↓
Trusted Origin Makes API Request
       ↓
CORS Allows Response
       ↓
Sensitive Data Accessible
```

The CORS policy may be functioning as configured, but the overall trust model may still create a vulnerability chain.

---

# null Origin

Browsers can sometimes send:

```http
Origin: null
```

in certain contexts.

Therefore test:

```http
Origin: null
```

Request:

```http
GET /api/account HTTP/1.1
Host: target.example
Origin: null
Cookie: session=CONTROLLED_SESSION
```

Potentially interesting response:

```http
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```

This deserves further investigation.

---

# What Can Produce a null Origin?

Depending on browser behaviour and context, a `null` origin may be associated with situations such as:

```text
Sandboxed documents
Certain local files
Opaque origins
Data URLs
Some isolated browser contexts
```

Because of these possibilities, blindly trusting:

```text
null
```

can be dangerous.

---

# Testing null Origin

Do not report:

```http
Access-Control-Allow-Origin: null
```

alone.

Determine whether a practical browser context can generate the required origin and read the sensitive response.

Again:

```text
Header observation
        ↓
Browser verification
        ↓
Impact
```

---

# CORS and HTTPS

Suppose:

```text
https://api.example.com
```

trusts:

```text
http://trusted.example.com
```

The HTTP origin lacks transport security.

This can weaken the overall trust model because an attacker capable of interfering with the HTTP connection may potentially influence content loaded from that origin.

Avoid trusting insecure origins for sensitive credentialed CORS access.

---

# CORS and Mixed Trust

A policy may trust:

```text
https://example.com
http://example.com
```

These are different origins.

The security properties are also different.

Treat scheme as part of the trust boundary.

---

# Ports

These are different origins:

```text
https://example.com
https://example.com:8443
```

An application that dynamically trusts arbitrary ports on a hostname should be reviewed carefully.

Different ports may expose completely different services.

---

# Preflight Testing

Do not stop after testing simple GET requests.

If the application uses:

```text
PUT
PATCH
DELETE
Custom headers
Authorization headers
JSON content types
```

test preflight behaviour.

---

# Example Preflight Test

```http
OPTIONS /api/profile HTTP/1.1
Host: target.example
Origin: https://example.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: content-type
```

Inspect:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Methods
Access-Control-Allow-Headers
Access-Control-Allow-Credentials
```

---

# Preflight Does Not Equal Authorisation

A permissive preflight response is not a replacement for server-side authorisation.

For example:

```http
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
```

does not mean every user is authorised to use those methods.

CORS controls browser cross-origin access.

Authorisation controls whether the user may perform the action.

Refer to:

```text
docs/web/authorisation.md
```

---

# CORS and CSRF

CORS and CSRF are frequently confused.

CORS controls:

```text
Can cross-origin JavaScript read the response?
```

CSRF concerns:

```text
Can another site cause the victim's browser to perform an unwanted authenticated action?
```

A request can sometimes be sent cross-site even when its response cannot be read.

Therefore:

```text
No CORS vulnerability
```

does not automatically mean:

```text
No CSRF vulnerability
```

Refer to:

```text
docs/web/csrf.md
```

---

# CORS and SameSite

SameSite cookie attributes can influence whether cookies are included in cross-site requests.

Possible values include:

```text
Strict
Lax
None
```

However, CORS and SameSite solve different problems.

A proper assessment should examine:

```text
Cookie policy
CORS policy
CSRF controls
Origin relationships
Browser behaviour
```

together.

---

# CORS and Clickjacking

CORS does not prevent Clickjacking.

CORS:

```text
Controls JavaScript access to cross-origin responses
```

Clickjacking:

```text
Controls whether a user can be tricked into interacting with a framed interface
```

A site can have strict CORS and still be vulnerable to Clickjacking.

Refer to:

```text
docs/web/clickjacking.md
```

---

# CORS and SOP

CORS relaxes parts of the Same-Origin Policy.

It should therefore be considered a:

```text
Trust declaration
```

rather than merely a collection of HTTP headers.

When an application returns:

```http
Access-Control-Allow-Origin: https://portal.example
```

it is effectively saying:

```text
I trust JavaScript executing at portal.example
to access this response.
```

That trust should be justified.

---

# CORS and APIs

CORS is particularly common with APIs.

Architecture:

```text
Frontend
   ↓
https://app.example.com

API
   ↓
https://api.example.com
```

Because these are different origins, the API may need to permit the frontend using CORS.

A secure configuration might be:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

provided:

```text
app.example.com
```

is the intended trusted application.

---

# Multiple Frontends

Some APIs legitimately support several origins:

```text
https://app.example.com
https://portal.example.com
https://admin.example.com
```

The server should validate the request origin against an explicit trusted list.

Conceptually:

```text
Request Origin
      ↓
Exact Allowlist
      ↓
Trusted?
  ↓         ↓
Yes        No
 ↓          ↓
Return      Do Not Return
ACAO        ACAO
```

---

# Development Origins

Look for development origins such as:

```text
http://localhost
http://127.0.0.1
https://dev.example.com
https://test.example.com
https://staging.example.com
```

These may have been left in production CORS allowlists.

Their risk depends on whether an attacker can actually control or meaningfully use the trusted origin.

---

# Localhost Trust

Applications sometimes allow:

```text
http://localhost
```

for development purposes.

Whether this is exploitable depends on:

```text
Exact origin matching
Port restrictions
Victim environment
Local services
Browser behaviour
```

Treat it as a trust-boundary question rather than automatically reporting it.

---

# Regex-Based CORS Policies

Some applications use regular expressions.

Conceptually:

```text
if origin matches regex:
    allow origin
```

Review:

```text
Anchoring
Escaping
Hostname boundaries
Scheme validation
Port validation
Case handling
```

Regex-based origin validation can easily become broader than intended.

---

# Case Sensitivity

Hostnames are case-insensitive, while other URL components may have different parsing rules.

Security checks should rely on proper URL/origin parsing rather than assumptions about raw string casing.

---

# Trailing Dots

DNS names can sometimes be represented with a trailing dot.

Example:

```text
example.com.
```

Different components may canonicalise hostnames differently.

This can matter where:

```text
Validation component
```

and:

```text
Browser/server interpretation
```

do not agree.

The broader lesson is:

> Validate canonical parsed origins, not hand-written string variations.

---

# Redirects and CORS

Cross-origin requests may encounter redirects.

Conceptually:

```text
Attacker Origin
      ↓
Request
      ↓
Endpoint A
      ↓
Redirect
      ↓
Endpoint B
```

Browser CORS behaviour around redirects can affect whether the final response is exposed.

Test the actual browser flow instead of reasoning only from individual HTTP responses.

---

# CORS and Open Redirect

An Open Redirect on a trusted origin may become relevant in broader trust chains, but it does not automatically bypass CORS.

CORS decisions are based on origins and browser behaviour.

Do not assume:

```text
Trusted redirect
```

means:

```text
Trusted CORS destination
```

Verify the complete flow.

Refer to:

```text
docs/web/open-redirect.md
```

---

# CORS and Web Cache Poisoning

Dynamic CORS responses may interact with shared caching.

Example:

```text
Request Origin
      ↓
Server Reflects Trusted Origin
      ↓
Response Cached
      ↓
Another Request Receives Cached Headers
```

The presence or absence of:

```http
Vary: Origin
```

can be relevant.

This should be investigated as part of cache behaviour rather than assuming a vulnerability from the header alone.

Refer to:

```text
docs/web/web-cache-poisoning.md
```

once that page is added.

---

# CORS and CDN Configuration

CORS may be implemented at multiple layers:

```text
Application
Reverse proxy
API gateway
CDN
Load balancer
Web server
```

This can create inconsistencies.

For example:

```text
Application rejects origin
       ↓
CDN adds ACAO header
```

or:

```text
Application returns ACAO
       ↓
Proxy overwrites it
```

Always inspect the final response received by the browser.

---

# Endpoint-Specific CORS

Do not assume one CORS policy applies to the entire application.

For example:

```text
/                     → No CORS
/api/public            → ACAO: *
/api/account           → Trusted origins
/api/admin             → Misconfigured reflection
```

Test endpoints individually.

---

# Method-Specific CORS

Policies may also differ by method.

Example:

```text
GET     → Allowed
POST    → Allowed
PUT     → Restricted
DELETE  → Restricted
```

Preflight testing can reveal these differences.

---

# Error Responses

Test CORS behaviour on:

```text
200
201
204
400
401
403
404
500
```

Error responses may expose:

```text
Stack traces
Internal identifiers
Validation details
Debug information
```

and may use different CORS middleware.

---

# Unauthenticated vs Authenticated

Test both states.

Example matrix:

| Endpoint | Unauthenticated | Authenticated |
|---|---:|---:|
| `/api/public` | Public | Public |
| `/api/profile` | 401 | Sensitive data |
| `/api/settings` | 401 | Sensitive data |
| `/api/admin` | 403 | Role-dependent |

CORS impact is often much greater for authenticated responses.

---

# Role-Based Testing

Use controlled accounts representing different roles where authorised:

```text
Normal user
Privileged user
Administrator
Support user
```

The same endpoint may expose different data depending on role.

A CORS issue affecting an administrative response may have greater impact.

---

# Burp Suite Workflow

A practical Burp workflow:

```text
Proxy
  ↓
Browse Application
  ↓
HTTP History
  ↓
Identify API Requests
  ↓
Send to Repeater
  ↓
Add Origin
  ↓
Observe ACAO
  ↓
Change Origin
  ↓
Check Credentials
  ↓
Test null
  ↓
Test Trusted-Origin Boundaries
  ↓
Check Preflight
  ↓
Verify in Browser
```

---

# Burp Repeater

Suppose the baseline request is:

```http
GET /api/me HTTP/1.1
Host: target.example
Cookie: session=CONTROLLED_SESSION
```

Add:

```http
Origin: https://example.com
```

Then inspect:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Vary
```

Repeat with multiple origins.

---

# Suggested Origin Test Set

A useful controlled set is:

```text
https://example.com
https://untrusted.invalid
null
https://subdomain.target.example
http://target.example
https://target.example:8443
```

The objective is to understand:

```text
Exact match?
Subdomain match?
Scheme validation?
Port validation?
null trusted?
Arbitrary reflection?
```

Do not treat this as a blind payload list.

Each test should answer a specific policy question.

---

# Burp Intruder

For applications with many endpoints, Burp Intruder can help compare CORS behaviour.

Potential payload positions include:

```http
Origin: §https://example.com§
```

A controlled list can contain different origin classes.

Review:

```text
Status code
Response length
ACAO value
ACAC value
Vary header
```

Avoid high-volume testing when a small number of targeted requests is sufficient.

---

# Burp Extensions

Burp extensions can assist with identifying CORS misconfigurations.

However:

> Automated extension output should be treated as a lead, not proof of exploitability.

Always verify:

```text
Sensitive endpoint
Trusted origin behaviour
Credential requirements
Browser exploitability
Impact
```

manually.

---

# Browser Developer Tools

Use browser Developer Tools to inspect:

```text
Console
Network
Application
Storage
Cookies
```

CORS failures often appear clearly in the Console.

The browser may indicate that a response was blocked because the required CORS header was missing or invalid.

---

# Browser Console vs Network

A useful distinction:

```text
Network tab
```

may show that the HTTP request occurred.

But:

```text
JavaScript
```

may still be unable to read the response.

This demonstrates the difference between:

```text
Request transmission
```

and:

```text
Response exposure
```

---

# JavaScript Fetch Test

A simple controlled test:

```javascript
fetch("https://target.example/api/me", {
    credentials: "include"
})
.then(r => r.text())
.then(data => console.log(data))
.catch(error => console.error(error));
```

The browser determines whether the calling origin may access the returned data.

---

# XMLHttpRequest

Legacy applications may use `XMLHttpRequest`.

Conceptually:

```javascript
var xhr = new XMLHttpRequest();

xhr.open(
    "GET",
    "https://target.example/api/me",
    true
);

xhr.withCredentials = true;

xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
        console.log(xhr.responseText);
    }
};

xhr.send();
```

The same CORS principles apply.

---

# Controlled CORS PoC

For a controlled account:

```html
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<title>CORS PoC</title>
</head>

<body>

<h1>Authorised CORS Test</h1>

<button id="test">Test CORS</button>

<pre id="result"></pre>

<script>

document.getElementById("test").addEventListener("click", async () => {

    const output = document.getElementById("result");

    try {

        const response = await fetch(
            "https://target.example/api/me",
            {
                credentials: "include"
            }
        );

        const data = await response.text();

        output.textContent = data;

    } catch (error) {

        output.textContent = String(error);

    }

});

</script>

</body>

</html>
```

This demonstrates whether the response is actually accessible from the test origin.

---

# Serving the PoC

Save as:

```text
cors-poc.html
```

Serve it from a controlled origin.

For a basic local test:

```bash
python3 -m http.server 8000
```

Then browse to:

```text
http://127.0.0.1:8000/cors-poc.html
```

Remember that:

```text
http://127.0.0.1:8000
```

becomes the test origin.

The target must trust that exact origin for the browser to expose the response.

---

# Credentials in Fetch

The important option for cookie-based authenticated testing is:

```javascript
credentials: "include"
```

Without it, cross-origin requests may not include credentials in the manner required by the test.

Browser cookie policies still apply.

---

# Third-Party Cookie Restrictions

Modern browsers increasingly restrict third-party cookies and cross-site tracking.

Therefore a CORS configuration that appears theoretically vulnerable may behave differently depending on:

```text
Browser
Cookie attributes
SameSite
Storage partitioning
Third-party cookie settings
Site relationships
```

Always test the actual browser environment relevant to the application.

---

# CORS Testing Matrix

Create a matrix such as:

| Endpoint | Origin | ACAO | ACAC | Sensitive Data | Browser Readable |
|---|---|---|---|---:|---:|
| `/api/public` | `https://example.com` | `*` | No | No | Yes |
| `/api/me` | `https://example.com` | Reflected | Yes | Yes | Yes |
| `/api/me` | `null` | Missing | No | Yes | No |
| `/api/admin` | `https://example.com` | Missing | No | Yes | No |

This makes the actual risk much easier to understand.

---

# Origin Validation Matrix

You can also map the policy:

| Origin Type | Example | Allowed |
|---|---|---:|
| Exact trusted | `https://app.target.example` | Yes |
| Random external | `https://example.com` | No |
| Target subdomain | `https://test.target.example` | ? |
| HTTP version | `http://app.target.example` | ? |
| Alternate port | `https://app.target.example:8443` | ? |
| null | `null` | ? |

This is more useful than randomly modifying origins.

---

# Common Misconfiguration: Arbitrary Reflection

Pattern:

```text
Origin supplied
      ↓
Server reflects it
      ↓
Credentials allowed
```

Example:

```http
Origin: https://example.com
```

Response:

```http
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Credentials: true
```

If the endpoint contains sensitive authenticated information, this can be serious.

---

# Common Misconfiguration: Broad Subdomain Trust

Pattern:

```text
*.target.example
```

is trusted.

Potential problem:

```text
Attacker gains control of one subdomain
          ↓
Subdomain is trusted by API
          ↓
CORS trust compromised
```

Review whether every allowed subdomain has an equivalent security posture.

---

# Common Misconfiguration: null Trusted

Pattern:

```http
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```

Investigate whether a browser context under attacker influence can generate a `null` origin and access the response.

---

# Common Misconfiguration: Insecure Trusted Origin

Pattern:

```text
HTTPS API
   ↓
Trusts
   ↓
HTTP Origin
```

An insecure trusted origin can undermine the security assumptions of the CORS policy.

---

# Common Misconfiguration: Development Origin

Pattern:

```text
Production API
     ↓
Trusts
     ↓
Development / Staging Origin
```

Investigate whether that environment is:

```text
Still active
Less protected
Externally accessible
Attacker-controllable
```

---

# Common Misconfiguration: Incorrect Regex

Pattern:

```text
Origin
 ↓
Weak regex
 ↓
Unexpected origin accepted
```

Review regex boundaries and URL parsing.

---

# Common Misconfiguration: Trusting Every Origin

Some applications effectively implement:

```text
Origin received?
      ↓
Yes
      ↓
Return same Origin
```

This defeats the purpose of restricting cross-origin access.

---

# CORS Is Not an Access Control Mechanism

CORS should never be used as server-side authorisation.

A server must still enforce:

```text
Authentication
Authorisation
Object-level permissions
Function-level permissions
```

An API endpoint should not reason:

```text
Request came from trusted Origin
therefore user is authorised
```

The `Origin` header is not an authentication credential.

---

# Origin Header Trust

Applications may use:

```http
Origin:
```

as one signal in CSRF protection.

That is different from treating it as an identity mechanism.

Security decisions should clearly distinguish:

```text
Browser origin validation
```

from:

```text
User authentication and authorisation
```

---

# CORS and Mobile Applications

Native mobile applications are not governed by browser CORS in the same way as ordinary browser JavaScript.

Therefore:

```text
CORS
```

should not be relied upon to prevent direct API access from arbitrary clients.

Server-side security controls remain essential.

---

# CORS and curl

Tools such as:

```text
curl
Burp Suite
Postman
Python requests
```

do not enforce browser CORS restrictions.

For example:

```bash
curl \
  -H "Origin: https://example.com" \
  -i \
  https://target.example/api/me
```

is useful for inspecting headers.

But it does not demonstrate that a browser can exploit the policy.

---

# curl Example

```bash
curl -s -D - \
  -H "Origin: https://example.com" \
  -o /dev/null \
  https://target.example/api/me
```

Look for:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Vary
```

---

# OPTIONS with curl

A preflight can be inspected using:

```bash
curl -i \
  -X OPTIONS \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: PUT" \
  -H "Access-Control-Request-Headers: content-type" \
  https://target.example/api/profile
```

This is useful for understanding the policy before browser verification.

---

# CORS Testing Checklist

## Discovery

```text
[ ] Identify API endpoints
[ ] Identify sensitive responses
[ ] Identify authenticated endpoints
[ ] Identify privileged endpoints
[ ] Identify CORS headers
[ ] Identify frontend/API origin relationships
```

## Origin Testing

```text
[ ] Test intended trusted origin
[ ] Test unrelated external origin
[ ] Test null origin
[ ] Test trusted subdomains
[ ] Test HTTP vs HTTPS
[ ] Test alternate ports
[ ] Review origin parsing
```

## Response Headers

```text
[ ] Access-Control-Allow-Origin
[ ] Access-Control-Allow-Credentials
[ ] Access-Control-Allow-Methods
[ ] Access-Control-Allow-Headers
[ ] Access-Control-Expose-Headers
[ ] Access-Control-Max-Age
[ ] Vary: Origin
```

## Authentication

```text
[ ] Test unauthenticated response
[ ] Test authenticated response
[ ] Check cookie authentication
[ ] Check bearer-token authentication
[ ] Review SameSite cookies
[ ] Review third-party cookie behaviour
```

## Preflight

```text
[ ] Test OPTIONS
[ ] Test allowed methods
[ ] Test allowed headers
[ ] Test custom headers
[ ] Test JSON requests
[ ] Test privileged methods
```

## Trust Relationships

```text
[ ] Review all trusted origins
[ ] Review development origins
[ ] Review staging origins
[ ] Review subdomain trust
[ ] Review third-party origins
[ ] Review HTTP origins
[ ] Consider takeover risk
[ ] Consider XSS on trusted origins
```

## Browser Verification

```text
[ ] Create controlled PoC
[ ] Use controlled account
[ ] Use controlled origin
[ ] Verify browser sends request
[ ] Verify credentials
[ ] Verify JavaScript can read response
[ ] Record Console output
[ ] Record Network behaviour
```

## Impact

```text
[ ] Identify exposed information
[ ] Identify affected role
[ ] Determine whether credentials are required
[ ] Determine attacker origin requirements
[ ] Determine user interaction
[ ] Determine realistic exploitation
[ ] Avoid hypothetical severity inflation
```

---

# CORS Decision Tree

```text
Sensitive Endpoint
       ↓
Send Origin Header
       ↓
ACAO Returned?
       ↓
      NO
       ↓
No CORS Access Through Tested Origin

       OR

      YES
       ↓
Is Origin Trusted?
       ↓
      YES
       ↓
Expected Policy?
       ↓
Review Trust Boundary

       OR

      NO
       ↓
Untrusted Origin Allowed
       ↓
Credentials Required?
       ↓
      YES
       ↓
ACAC true?
       ↓
      YES
       ↓
Will Browser Send Credentials?
       ↓
      YES
       ↓
Can JavaScript Read Response?
       ↓
      YES
       ↓
Sensitive Data Exposed?
       ↓
      YES
       ↓
CORS Vulnerability Confirmed
       ↓
Assess Impact
       ↓
Report
```

---

# CORS Quick Reference

```text
REQUEST

Origin: https://example.com
```

```text
IMPORTANT RESPONSE HEADERS

Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Access-Control-Allow-Methods
Access-Control-Allow-Headers
Access-Control-Expose-Headers
Vary
```

```text
HIGH-VALUE CONDITION

Untrusted Origin
       +
Access-Control-Allow-Credentials: true
       +
Sensitive Authenticated Response
       +
Browser Can Read Response
```

```text
TEST ORIGINS

https://example.com
https://untrusted.invalid
null
https://subdomain.target.example
http://target.example
https://target.example:8443
```

```text
PREFLIGHT

OPTIONS
Origin
Access-Control-Request-Method
Access-Control-Request-Headers
```

---

# Evidence Collection

For a confirmed CORS vulnerability, record:

```text
Affected endpoint
Affected method
Authentication state
Affected user role
Test origin
Access-Control-Allow-Origin value
Access-Control-Allow-Credentials value
Relevant preflight response
Sensitive information exposed
Browser tested
Proof-of-concept page
Request
Response
Screenshot
```

The strongest evidence demonstrates that the browser actually exposes sensitive information to the controlled untrusted origin.

---

# Example Finding

```text
Finding:
Arbitrary Origin Reflection Allows Credentialed Cross-Origin Access

Affected Endpoint:
/api/account

Authentication:
Authenticated user session

Expected:
Only explicitly trusted application origins should be permitted to read authenticated account information cross-origin.

Observed:
The API reflected an arbitrary Origin value into the Access-Control-Allow-Origin response header and returned Access-Control-Allow-Credentials: true.

A browser-based proof of concept hosted on a controlled origin successfully read the authenticated test user's account response.

Impact:
An attacker who can cause an authenticated user to visit an attacker-controlled origin may be able to read information returned by the affected API using the victim's authenticated browser session, subject to the browser's applicable cookie policies.
```

---

# Example Broad Subdomain Finding

```text
Finding:
Overly Broad CORS Trust Extends to Untrusted Subdomains

Affected Endpoint:
/api/profile

Observed:
The API permits credentialed cross-origin access from a broad set of organisational subdomains.

One of the permitted origins is not maintained to the same security standard as the primary application.

Impact:
Compromise or attacker control of a trusted subdomain may allow that origin to access authenticated API responses that would otherwise be protected by the Same-Origin Policy.
```

Only use this impact statement when the weaker trusted origin has actually been demonstrated.

---

# Example Informational Observation

```text
Observation:
Wildcard CORS Policy on Public API

Affected Endpoint:
/api/public/products

Observed:
The endpoint returns:

Access-Control-Allow-Origin: *

The endpoint is accessible without authentication and returns information already intended for public consumption.

Impact:
No sensitive cross-origin data exposure was identified.

Recommendation:
Confirm that the endpoint is intentionally public and ensure that authenticated or sensitive API endpoints use a more restrictive CORS policy.
```

This prevents harmless public CORS configurations from being exaggerated.

---

# Reporting Titles

Prefer precise titles:

```text
Credentialed CORS Misconfiguration Allows Arbitrary Origins

Arbitrary Origin Reflection on Authenticated API

CORS Policy Trusts Attacker-Controlled Subdomain

Sensitive API Permits Credentialed null Origin

Overly Broad CORS Allowlist Exposes Account Data

Insecure HTTP Origin Trusted by Sensitive API
```

Avoid titles such as:

```text
CORS Header Missing
```

or:

```text
CORS Enabled
```

Neither describes a vulnerability.

---

# Severity

Severity depends on:

```text
Data sensitivity
Authentication
Victim requirements
Browser behaviour
Attacker origin requirements
Affected user role
Trusted-origin requirements
Available actions
Exploit reliability
```

For example:

```text
ACAO: *
```

on a public API may have no security impact.

While:

```text
Arbitrary Origin Reflection
+
Credentials
+
Sensitive Account Data
+
Browser-Verified Access
```

may represent a significant vulnerability.

---

# Remediation

CORS should be configured around an explicit trust model.

A good design is:

```text
Request Origin
      ↓
Parse Origin
      ↓
Compare Against Explicit Allowlist
      ↓
Trusted?
   ↓       ↓
 Yes      No
 ↓         ↓
Return    Do Not Return
ACAO      ACAO
```

---

# Explicit Allowlist

For example:

```text
https://app.example.com
https://admin.example.com
```

Only origins with a legitimate requirement should be trusted.

Avoid broad wildcard subdomain policies where possible.

---

# Exact Origin Validation

Validation should account for:

```text
Scheme
Hostname
Port
```

For example:

```text
https://app.example.com
```

should not automatically imply trust for:

```text
http://app.example.com
https://app.example.com:8443
https://anything.app.example.com
```

unless those origins are explicitly required.

---

# Do Not Reflect Arbitrary Origins

Avoid logic conceptually equivalent to:

```text
Read Origin
    ↓
Return Same Origin
```

without validation.

This effectively allows arbitrary origins.

---

# Avoid null Unless Required

Do not trust:

```text
Origin: null
```

unless the application has a clearly understood and justified requirement.

---

# Restrict Credentials

Only use:

```http
Access-Control-Allow-Credentials: true
```

where cross-origin credentialed requests are genuinely necessary.

Avoid exposing authenticated resources to origins that do not require access.

---

# Restrict Methods

Allow only required methods.

For example:

```http
Access-Control-Allow-Methods: GET, POST
```

rather than unnecessarily exposing:

```text
PUT
PATCH
DELETE
```

to cross-origin browser workflows.

This is defence in depth and does not replace authorisation.

---

# Restrict Headers

Allow only headers required by legitimate clients.

Avoid overly broad configurations without a clear business need.

---

# Protect Every Endpoint

CORS middleware should be applied consistently.

Do not configure:

```text
Public API → correct policy
Account API → correct policy
Admin API → accidental arbitrary reflection
```

Centralised and well-tested CORS handling reduces configuration drift.

---

# Review Trusted Origins

Trusted origins should be periodically reviewed.

Remove:

```text
Retired applications
Development environments
Old staging environments
Unused third-party integrations
Abandoned subdomains
HTTP origins
```

that no longer require access.

---

# CORS Is Defence in Depth

Even with a correct CORS policy, sensitive APIs still require:

```text
Authentication
Authorisation
Secure session management
CSRF protection where applicable
Input validation
Output handling
Secure transport
```

CORS is not a substitute for any of these controls.

---

# References

## PortSwigger Web Security Academy: CORS

https://portswigger.net/web-security/cors

PortSwigger provides detailed material covering CORS fundamentals, origin reflection, credentialed requests, `null` origins and trust relationships.

---

## PortSwigger CORS Labs

https://portswigger.net/web-security/all-labs#cross-origin-resource-sharing-cors

Useful practical labs for understanding common CORS misconfigurations.

---

## OWASP WSTG: Testing Cross Origin Resource Sharing

https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/07-Testing_Cross_Origin_Resource_Sharing

Provides a structured testing methodology for reviewing CORS policies.

---

## MDN: Cross-Origin Resource Sharing

https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS

Useful reference documentation for browser CORS behaviour.

---

## MDN: Access-Control-Allow-Origin

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Origin

Reference for the `Access-Control-Allow-Origin` response header.

---

## MDN: Access-Control-Allow-Credentials

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Credentials

Reference for credentialed cross-origin requests.

---

## OWASP HTML5 Security Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html

Contains additional browser and cross-origin security guidance.

---

# Final CORS Testing Model

```text
                       ENDPOINT
                           ↓
                  IS DATA SENSITIVE?
                           ↓
                          YES
                           ↓
                    ADD ORIGIN
                           ↓
                INSPECT CORS POLICY
                           ↓
       ┌───────────────────┼───────────────────┐
       ↓                   ↓                   ↓
      ACAO                ACAC              PREFLIGHT
       ↓                   ↓                   ↓
       └───────────────────┼───────────────────┘
                           ↓
                  TEST TRUST MODEL
                           ↓
       ┌───────────────────┼───────────────────┐
       ↓                   ↓                   ↓
    EXTERNAL           SUBDOMAIN             NULL
     ORIGIN              ORIGIN             ORIGIN
       ↓                   ↓                   ↓
       └───────────────────┼───────────────────┘
                           ↓
                  ORIGIN ACCEPTED?
                           ↓
                          YES
                           ↓
                  CREDENTIALS REQUIRED?
                           ↓
                          YES
                           ↓
                 WILL BROWSER SEND THEM?
                           ↓
                          YES
                           ↓
                  BROWSER-BASED PoC
                           ↓
                CAN JAVASCRIPT READ DATA?
                           ↓
                          YES
                           ↓
                  SENSITIVE DATA EXPOSED?
                           ↓
                          YES
                           ↓
               CORS VULNERABILITY CONFIRMED
                           ↓
                    ASSESS IMPACT
                           ↓
                        REPORT
```

The key principle is:

> CORS testing is not about finding `Access-Control-Allow-Origin` headers. Map the application's cross-origin trust relationships, determine whether an untrusted origin is accepted, establish whether credentials are available, and verify in a real browser whether sensitive information can actually cross the intended origin boundary.
