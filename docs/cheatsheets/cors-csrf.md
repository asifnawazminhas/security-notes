---
title: CORS and CSRF Security Testing Cheatsheet
description: Practical CORS and CSRF security testing cheatsheet covering origins, preflight requests, credentials, Access-Control headers, SameSite cookies, CSRF tokens, Origin and Referer validation, APIs, Burp Suite workflows, source review, evidence, remediation and retesting.
---

# CORS and CSRF Security Testing Cheatsheet

Cross-Origin Resource Sharing (CORS) and Cross-Site Request Forgery (CSRF) are closely related to browser security, but they address different problems.

```text
CORS
 |
 v
Can JavaScript running on another origin
read or interact with this response?

CSRF
 |
 v
Can another site cause the victim browser
to perform an authenticated action?
```

Understanding this distinction is essential.

!!! warning "Authorised Security Testing"

    Test CORS and CSRF only against applications, APIs, accounts and actions included in the assessment scope. Use dedicated test accounts and reversible state changes where possible. Avoid destructive operations, mass requests or actions affecting unrelated users.


# Core Mental Model

Browser security begins with the same-origin policy.

```text
Browser
   |
   v
Same-Origin Policy
   |
   +--> Same Origin
   |       |
   |       v
   |     Allowed
   |
   +--> Cross Origin
           |
           v
      Browser Restrictions
           |
           v
        CORS Policy
```

CSRF operates differently:

```text
Attacker Site
     |
     v
Victim Browser
     |
     +--> Automatically Attached Credentials
     |
     v
Target Application
     |
     v
State-Changing Request
```


# Origin

An origin consists of:

```text
Scheme
+
Host
+
Port
```


# Example

```text
https://app.example.com:443
```

contains:

```text
Scheme: https
Host: app.example.com
Port: 443
```


# Different Origins

These are different origins:

```text
https://example.com

http://example.com

https://api.example.com

https://example.com:8443
```


# Same-Origin Examples

These URLs are normally the same origin:

```text
https://example.com/account

https://example.com/api/profile

https://example.com/images/logo.png
```


# Path Does Not Define Origin

These remain the same origin:

```text
https://example.com/a

https://example.com/b
```


# Subdomains Are Different Origins

```text
https://app.example.com
```

and:

```text
https://api.example.com
```

are different origins.


# Same-Origin Policy

The same-origin policy restricts how documents and scripts from one origin interact with resources from another origin.


# Important

The same-origin policy does not simply mean:

```text
Cross-origin requests cannot be sent.
```

Browsers can send many cross-origin requests.

The restrictions often concern:

```text
Reading responses

JavaScript access

Credential behaviour

Certain request types
```


# CORS

CORS allows a server to relax browser same-origin restrictions for selected origins.


# Basic CORS Response

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.example.com
```


# Meaning

The server tells the browser:

```text
JavaScript from https://app.example.com
may access this response.
```


# CORS Is Enforced by Browsers

CORS is primarily a browser security mechanism.

Tools such as:

```text
curl

Burp Repeater

Postman

Server-side scripts
```

do not enforce browser CORS policy in the same way.


# Critical Testing Principle

Seeing a sensitive response in Burp after adding:

```http
Origin: https://attacker.example
```

does not by itself prove exploitable CORS.

You must evaluate the returned CORS headers and browser behaviour.


# CORS Request

Example:

```http
GET /api/profile HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Cookie: session=SESSION_VALUE
```


# CORS Response

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Content-Type: application/json

{
  "username": "testuser"
}
```


# Important CORS Headers

| Header | Purpose |
|---|---|
| `Access-Control-Allow-Origin` | Allowed requesting origin |
| `Access-Control-Allow-Credentials` | Whether credentialed CORS requests are permitted |
| `Access-Control-Allow-Methods` | Methods permitted during preflight |
| `Access-Control-Allow-Headers` | Request headers permitted during preflight |
| `Access-Control-Expose-Headers` | Response headers exposed to JavaScript |
| `Access-Control-Max-Age` | Preflight cache lifetime |


# Access-Control-Allow-Origin

Example:

```http
Access-Control-Allow-Origin: https://app.example.com
```


# Wildcard

```http
Access-Control-Allow-Origin: *
```


# Wildcard Is Not Automatically Vulnerable

A wildcard can be appropriate for genuinely public resources.

Example:

```text
Public documentation API

Public static data

Unauthenticated public content
```


# Ask

```text
Is sensitive data returned?

Are credentials involved?

Should arbitrary origins be able to read it?
```


# Access-Control-Allow-Credentials

Example:

```http
Access-Control-Allow-Credentials: true
```


# Meaning

The response permits credentialed cross-origin access when the rest of the browser's CORS and cookie requirements are satisfied.


# Credentials Can Include

```text
Cookies

HTTP authentication

Client certificates
```

depending on the request and browser context.


# Important

This combination is invalid for credentialed browser access:

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

Browsers do not allow wildcard origin to authorize credentialed CORS response access.


# Dynamic Origin Reflection

A common CORS weakness occurs when the server reflects arbitrary origins.

Request:

```http
Origin: https://attacker.example
```


# Vulnerable Response Pattern

```http
Access-Control-Allow-Origin: https://attacker.example
Access-Control-Allow-Credentials: true
```


# Security Question

Does the application:

```text
Trust arbitrary origins
+
Allow credentials
+
Return sensitive data
```

If yes, the issue may permit another origin to read authenticated responses in the victim's browser.


# Baseline CORS Workflow

Start with a normal request.

```http
GET /api/profile HTTP/1.1
Host: api.example.com
Cookie: session=SESSION_VALUE
```


# Add Trusted Origin

```http
Origin: https://app.example.com
```


# Record Response

Look for:

```text
Access-Control-Allow-Origin

Access-Control-Allow-Credentials

Vary: Origin
```


# Test Untrusted Origin

```http
Origin: https://attacker.example
```


# Compare

```text
Trusted origin response

vs

Untrusted origin response
```


# Secure Behaviour

Possible secure results include:

```text
No Access-Control-Allow-Origin header
```

or:

```text
Access-Control-Allow-Origin only for an approved origin
```


# Origin Reflection Test

Request:

```http
Origin: https://cors-test.invalid
```


# Potentially Interesting Response

```http
Access-Control-Allow-Origin: https://cors-test.invalid
```


# Do Not Stop Here

Determine:

```text
Are credentials allowed?

Is sensitive information returned?

Can a real browser read it?

Are cookies actually sent cross-site?
```


# Origin Allowlist

Secure applications commonly maintain an explicit list.

Example:

```text
https://app.example.com

https://admin.example.com
```


# Weak Validation Patterns

Dangerous conceptual checks include:

```text
Origin contains "example.com"

Origin ends with "example.com"

Origin starts with "https://example.com"
```


# Why Substring Matching Fails

A check such as:

```text
contains "example.com"
```

may incorrectly trust:

```text
https://example.com.attacker.example
```


# Why Suffix Matching Can Fail

A naive suffix check for:

```text
example.com
```

may trust:

```text
https://notexample.com
```

depending on implementation.


# Better Validation

Parse the origin and compare against exact trusted origins.

Conceptually:

```text
Parse Origin
    |
    v
Scheme + Host + Port
    |
    v
Exact Trusted Entry?
    |
 +--+--+
 |     |
Yes    No
 |     |
 v     v
Allow Reject
```


# Subdomain Trust

Some applications intentionally allow:

```text
https://*.example.com
```

This creates a broader trust boundary.


# Review All Trusted Subdomains

Ask whether any trusted subdomain is:

```text
User-controlled

Abandoned

Vulnerable to takeover

Hosting untrusted content

Weakly isolated
```


# CORS Trust Inherits Origin Security

If:

```text
https://legacy.example.com
```

is trusted by CORS, compromise of that origin may affect the CORS security boundary.


# `null` Origin

Browsers can send:

```http
Origin: null
```

in certain contexts.


# Possible Sources

Depending on browser behaviour and context:

```text
Sandboxed documents

Local files

Opaque origins

Certain embedded documents
```


# Test

```http
Origin: null
```


# Interesting Response

```http
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
```


# Interpretation

Do not report this based solely on the header.

Determine whether an attacker can create a relevant browser context that:

```text
Produces null origin

Sends required credentials

Reads sensitive response
```


# Multiple Origin Header Values

Malformed or duplicate Origin headers may reveal parser differences.

Example controlled testing:

```http
Origin: https://trusted.example
Origin: https://untrusted.example
```


# Caution

Behaviour can vary between:

```text
Reverse proxy

CDN

Application server

Framework
```

Test at low volume and interpret parser differences carefully.


# Preflight Requests

Some cross-origin requests trigger a browser preflight request.


# Preflight

The browser sends:

```http
OPTIONS /api/profile HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: authorization,content-type
```


# Example Response

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
```


# Preflight Mental Model

```text
Browser
   |
   v
OPTIONS Preflight
   |
   v
Server CORS Policy
   |
   +--> Allowed
   |       |
   |       v
   |   Actual Request
   |
   +--> Denied
           |
           v
      Browser Blocks
```


# Requests That May Trigger Preflight

Common reasons include:

```text
Non-simple methods

Custom request headers

Certain Content-Type values
```


# Examples

Methods such as:

```text
PUT

PATCH

DELETE
```

normally trigger preflight in cross-origin JavaScript requests.


# Authorization Header

A request containing:

```http
Authorization: Bearer TOKEN
```

normally requires preflight for cross-origin browser requests.


# Content-Type

These content types are relevant to simple-request rules:

```text
application/x-www-form-urlencoded

multipart/form-data

text/plain
```


# JSON

```text
application/json
```

normally causes a preflight in cross-origin JavaScript requests.


# Preflight Is Not Authentication

A successful:

```http
OPTIONS
```

response does not mean the actual request will be authorized.


# Test Actual Request

Always verify:

```text
Preflight policy

Actual response

Credentials

Authorization
```


# Access-Control-Allow-Methods

Example:

```http
Access-Control-Allow-Methods: GET, POST, PUT
```


# Do Not Report Broad Methods Alone

A response advertising:

```text
DELETE
```

does not prove an attacker can successfully perform a privileged DELETE operation.

Validate actual authorization.


# Access-Control-Allow-Headers

Example:

```http
Access-Control-Allow-Headers: Authorization, Content-Type
```


# Security Context

Broad header allowance matters only when combined with an origin that should not be trusted and an exploitable browser interaction.


# Access-Control-Expose-Headers

Browsers expose only certain response headers to JavaScript by default.

Applications can expose additional headers:

```http
Access-Control-Expose-Headers: X-Request-ID
```


# Sensitive Headers

Review whether the application exposes headers containing:

```text
Tokens

Internal identifiers

Sensitive metadata
```


# Vary Origin

Dynamic CORS responses often need:

```http
Vary: Origin
```


# Why

Caches need to distinguish responses based on the request Origin.


# Missing Vary

Missing:

```http
Vary: Origin
```

can create caching problems when responses dynamically vary CORS headers.


# Do Not Automatically Report

Demonstrate actual cache behaviour before claiming cache poisoning or cross-user impact.


# CORS Testing Matrix

Test origins such as:

```text
Expected trusted origin

Completely unrelated origin

Lookalike origin

Trusted-domain prefix

Trusted-domain suffix

Sibling subdomain

HTTPS vs HTTP

Different port

null
```


# Example Matrix

| Origin | Question |
|---|---|
| `https://app.example.com` | Expected trusted origin |
| `https://attacker.example` | Arbitrary external origin |
| `https://example.com.attacker.example` | Prefix validation |
| `https://notexample.com` | Naive suffix validation |
| `https://dev.example.com` | Sibling subdomain trust |
| `http://app.example.com` | Scheme validation |
| `https://app.example.com:8443` | Port validation |
| `null` | Null-origin trust |


# Browser Proof

When a CORS issue appears exploitable, validate with a controlled browser page.


# Read-Only CORS Test Page

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CORS Test</title>
</head>
<body>
  <pre id="output">Testing...</pre>

  <script>
    fetch("https://target.example/api/profile", {
      credentials: "include"
    })
      .then(response => response.text())
      .then(data => {
        document.getElementById("output").textContent = data;
      })
      .catch(error => {
        document.getElementById("output").textContent = String(error);
      });
  </script>
</body>
</html>
```


# Use a Read-Only Endpoint First

Prefer:

```text
Profile

Current-user information

Non-destructive account data
```

rather than state-changing actions.


# Expected Vulnerable Behaviour

The attacker-origin page can:

```text
Send request

Include relevant victim credentials

Read sensitive response
```


# Evidence

Capture:

```text
Attacker origin

Request Origin header

Target response

Access-Control-Allow-Origin

Access-Control-Allow-Credentials

Browser-readable response
```


# CSRF

Cross-Site Request Forgery causes a victim browser to submit an unwanted authenticated request.


# CSRF Model

```text
Victim Authenticated to Target
          |
          v
      Session Cookie
          |
          v
Victim Visits Attacker Site
          |
          v
Cross-Site Request
          |
          v
Browser Sends Credentials
          |
          v
Target Accepts Action
```


# CSRF Requires Context

A useful CSRF assessment asks:

```text
Does the browser send authentication automatically?

Can the attacker construct the request?

Does the server require unpredictable authorization data?

Does SameSite prevent the request?

Does Origin/Referer validation prevent it?

Does the action have meaningful impact?
```


# Common CSRF Targets

Examples:

```text
Change email address

Change profile data

Add shipping address

Modify notification settings

Link external account

Create API key

Change application configuration

Invite user

Modify permissions
```


# High-Risk Actions

Actions such as:

```text
Change password

Disable MFA

Add privileged user

Change payment destination
```

deserve careful testing but should only be exercised in controlled accounts and within scope.


# Baseline CSRF Workflow

Capture a legitimate state-changing request.

Example:

```http
POST /account/email HTTP/1.1
Host: target.example
Cookie: session=SESSION_VALUE
Content-Type: application/x-www-form-urlencoded

email=test2@example.com
```


# Identify Authentication

Ask whether authentication comes from:

```text
Cookie

HTTP authentication

Client certificate

Bearer token manually added by JavaScript
```


# Automatically Attached Credentials

CSRF is particularly relevant when browsers automatically attach authentication credentials.


# Cookie Authentication

Typical example:

```http
Cookie: session=SESSION_VALUE
```


# Bearer Token Header

If the application requires JavaScript to add:

```http
Authorization: Bearer TOKEN
```

an external site normally cannot simply force the victim browser to attach that header.

This can significantly change CSRF exposure.


# Do Not Assume

```text
API endpoint
```

means:

```text
Not vulnerable to CSRF
```

Check how authentication actually works.


# CSRF Tokens

A common defense is an unpredictable token tied to the user session or transaction.


# Form Example

```html
<input type="hidden" name="csrf_token" value="RANDOM_VALUE">
```


# Request

```http
POST /account/email HTTP/1.1
Host: target.example
Cookie: session=SESSION_VALUE
Content-Type: application/x-www-form-urlencoded

email=test2@example.com&csrf_token=RANDOM_VALUE
```


# CSRF Token Properties

A robust token should be:

```text
Unpredictable

Validated server-side

Bound appropriately to the session

Unavailable to unrelated origins

Required on protected actions
```


# Test Missing Token

Remove:

```text
csrf_token
```


# Expected

```text
Request rejected
```


# Test Empty Token

```text
csrf_token=
```


# Expected

```text
Rejected
```


# Test Invalid Token

```text
csrf_token=invalid-test-value
```


# Expected

```text
Rejected
```


# Test Another Session's Token

With two controlled accounts:

```text
Account A token

Account B session
```


# Expected

If tokens are session-bound:

```text
Rejected
```


# Why Two Accounts Help

This distinguishes:

```text
Globally valid token
```

from:

```text
Session-bound token
```


# Token Reuse

Some applications intentionally allow a CSRF token to remain valid for the session.

Therefore:

```text
Token reusable
```

is not automatically a vulnerability.


# Security Property

The important question is whether an attacker can obtain or predict a valid token for the victim's request.


# Predictable CSRF Tokens

If tokens follow a predictable pattern, assess whether that predictability allows unauthorized cross-site requests.


# Do Not Infer From Appearance

A short token is not automatically predictable.

A long token is not automatically secure.

Test actual entropy only when justified.


# Token in Cookie and Request

Some applications use a double-submit cookie pattern.

Example:

```http
Cookie: csrf=ABC123
```

and:

```text
csrf=ABC123
```

in the request.


# Double-Submit Model

```text
CSRF Cookie
     |
     +--> Browser Cookie
     |
     +--> Request Parameter/Header
              |
              v
           Compare
```


# Security Considerations

Review:

```text
Can attacker set the cookie?

Is token cryptographically bound?

Are subdomains trusted?

Is cookie scope safe?
```


# Signed Double-Submit

A stronger design can bind the CSRF token to session-specific information using a server-side secret.


# Custom Header Defense

APIs may require a custom header:

```http
X-CSRF-Token: RANDOM_VALUE
```


# Why It Helps

Cross-origin JavaScript cannot normally add arbitrary custom headers without passing CORS preflight.


# Important

If CORS trusts an attacker-controlled origin, a custom-header CSRF defense may become ineffective.

This is why CORS and CSRF should sometimes be reviewed together.


# CORS + CSRF Interaction

```text
Attacker Origin
      |
      v
CORS Allows Origin
      |
      v
Browser Permits Custom Header
      |
      v
CSRF Header Added
      |
      v
Authenticated Request
```


# Origin Validation

Servers can validate:

```http
Origin: https://app.example.com
```


# State-Changing Request

Example:

```http
POST /account/email HTTP/1.1
Host: target.example
Origin: https://app.example.com
```


# Secure Policy

For protected state-changing requests:

```text
Expected trusted origin
        |
        v
Allow

Unexpected origin
        |
        v
Reject
```


# Test Untrusted Origin

Using Repeater:

```http
Origin: https://attacker.example
```


# Expected

```text
Rejected
```

when Origin validation is part of the CSRF defense.


# Missing Origin

Test:

```text
No Origin header
```


# Interpretation

Some legitimate requests may omit Origin depending on browser/request context.

Applications using Origin validation should have a carefully designed fallback policy.


# Referer Validation

Applications may inspect:

```http
Referer: https://app.example.com/account
```


# Secure Parsing

Do not validate with naive substring matching.


# Dangerous Concept

```text
Referer contains "example.com"
```


# Better

Parse the URL and verify the expected:

```text
Scheme

Host

Port
```


# Origin Preferred

For CSRF origin checks, `Origin` is often easier to validate because it contains only the origin rather than a full URL.


# Referer Privacy

Referer may be omitted or reduced due to:

```text
Referrer-Policy

Browser privacy behaviour

Navigation context
```


# SameSite Cookies

SameSite controls when cookies are sent with cross-site requests.


# Values

```text
Strict

Lax

None
```


# Cookie Example

```http
Set-Cookie: session=VALUE; Secure; HttpOnly; SameSite=Lax
```


# SameSite Strict

Conceptually:

```text
Cross-site request
      |
      v
Cookie generally withheld
```


# SameSite Lax

Lax allows cookies in some top-level navigation scenarios while restricting many cross-site subrequests.


# Important

Do not reduce SameSite behaviour to:

```text
Lax = no CSRF
```

Request method and navigation context matter.


# SameSite None

```http
SameSite=None; Secure
```


# Meaning

The cookie may be sent in cross-site contexts, subject to browser cookie rules.


# Secure Requirement

Modern browsers require:

```text
Secure
```

with:

```text
SameSite=None
```


# Same-Site vs Same-Origin

These concepts are different.

```text
Same Origin
```

is stricter than:

```text
Same Site
```


# Example

Depending on scheme and registrable domain:

```text
app.example.com

api.example.com
```

may be:

```text
Cross-origin
```

while still:

```text
Same-site
```


# Why It Matters

SameSite cookie protections are based on:

```text
Site
```

not the exact same-origin definition used by CORS.


# Sibling Subdomains

A compromised sibling subdomain can therefore matter in CSRF and SameSite threat modelling.


# SameSite Is Defense-in-Depth

Do not rely exclusively on SameSite for every sensitive application action.

Robust applications commonly combine appropriate controls such as:

```text
CSRF token

Origin validation

SameSite cookies

Reauthentication
```


# GET Requests

State-changing actions should not normally be implemented through GET.


# Dangerous Pattern

```http
GET /account/delete?id=123 HTTP/1.1
```


# Why

GET requests can be triggered through many browser mechanisms:

```html
<img src="https://target.example/account/delete?id=123">
```


# Correct Design

Use appropriate state-changing methods such as:

```text
POST

PUT

PATCH

DELETE
```

with suitable CSRF defenses.


# Important

Using POST alone does not prevent CSRF.


# Simple POST

An attacker page can submit a normal HTML form.

Example:

```html
<form action="https://target.example/account/email" method="POST">
  <input type="hidden" name="email" value="controlled@example.com">
</form>

<script>
  document.forms[0].submit();
</script>
```


# Browser Request

This can produce:

```http
POST /account/email HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
```


# CSRF Proof of Concept

For a controlled account:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CSRF Test</title>
</head>
<body>
  <form action="https://target.example/account/email" method="POST">
    <input type="hidden" name="email" value="csrf-test@example.com">
    <button type="submit">Submit controlled test</button>
  </form>
</body>
</html>
```


# Prefer Manual Submission Initially

A button is useful during assessment because it avoids accidental repeated actions.


# After Confirming Safety

Automatic submission may be used for a controlled demonstration if appropriate:

```html
<script>
  document.forms[0].submit();
</script>
```


# JSON CSRF

An endpoint requiring:

```http
Content-Type: application/json
```

is harder to invoke using a traditional HTML form with that exact content type.


# Example Target

```http
POST /api/profile HTTP/1.1
Content-Type: application/json

{"name":"test"}
```


# Browser Constraint

Cross-origin JavaScript using:

```text
application/json
```

normally triggers CORS preflight.


# Security Benefit

If the server:

```text
Rejects simple content types

Requires application/json

Does not trust attacker origins through CORS
```

this can reduce CSRF exposure.


# But Test Parsing

Some APIs accept JSON-like bodies using:

```text
text/plain

application/x-www-form-urlencoded
```

or ignore Content-Type.


# Example Test

Change:

```http
Content-Type: application/json
```

to:

```http
Content-Type: text/plain
```


# Interpretation

If the server still processes the body, an attacker may be able to create a simple cross-site request.


# Content-Type Enforcement

Review whether the API genuinely requires the intended content type.


# Multipart Forms

HTML forms can submit:

```text
multipart/form-data
```

without CORS preflight.


# File Upload CSRF

Upload or import functionality can therefore require CSRF review when authentication uses cookies.


# PUT / DELETE

Traditional HTML forms support:

```text
GET

POST
```

rather than arbitrary methods.


# However

Applications may implement method override parameters such as:

```text
_method=DELETE
```

or headers.


# Test Method Override

Look for:

```text
_method

X-HTTP-Method-Override

X-Method-Override
```


# Security Question

Can a simple POST be transformed server-side into a privileged operation?


# Login CSRF

CSRF can affect authentication itself.


# Model

```text
Attacker Authenticates
      |
      v
Attacker Login Request
      |
      v
Victim Browser Submits It
      |
      v
Victim Logged Into Attacker Account
```


# Impact

The victim may unknowingly add:

```text
Personal data

Search history

Payment information

Documents
```

to the attacker's account.


# Test Only With Controlled Accounts

Never use unrelated user credentials for login CSRF testing.


# Logout CSRF

An attacker may be able to cause:

```text
Victim logout
```


# Severity

Logout CSRF is usually much lower impact than account-changing CSRF, but context matters.


# Password Change

Review whether password changes require:

```text
Current password

CSRF protection

Recent authentication
```


# CSRF Token Alone Is Not Reauthentication

These controls solve different problems.


# Sensitive Action Model

```text
Authenticated Session
        |
        v
CSRF Validation
        |
        v
Recent Authentication
        |
        v
Sensitive Action
```


# MFA Changes

Sensitive actions such as:

```text
Disable MFA

Add new factor

Regenerate recovery codes
```

should receive stronger protection appropriate to the application risk.


# Account Linking CSRF

External account linking can be especially sensitive.

Example:

```text
Victim Session
     |
     v
Link External Identity
     |
     v
Attacker-Controlled Identity
```


# OAuth Interaction

Review account-linking flows alongside:

[OAuth 2.0 and OpenID Connect Security Testing Cheatsheet](oauth-oidc.md)


# CSRF and IDOR

These are separate controls.

```text
CSRF
 |
 v
Who initiated the browser request?

IDOR / BOLA
 |
 v
Is this authenticated user allowed
to access this object?
```


# Both Must Be Enforced

A request can pass CSRF validation and still violate object authorization.


# CSRF and XSS

XSS can often undermine CSRF protections because script executing in the trusted origin may:

```text
Read CSRF tokens

Submit same-origin requests

Read responses
```


# Therefore

Strong CSRF protection does not reduce the importance of fixing XSS.


# CORS and XSS

A trusted CORS origin that has XSS may become a route to access another application's sensitive cross-origin data.


# Trust Boundary

```text
Sensitive API
     |
     v
Trusts Origin A
     |
     v
Origin A Has XSS
     |
     v
Attacker Script Uses CORS Trust
```


# CORS Is Not Authorization

Never use CORS as the primary API authorization mechanism.


# Example Bad Assumption

```text
Only our frontend origin is allowed by CORS,
therefore the API is protected.
```


# Reality

Non-browser clients can call the API directly.


# API Must Enforce

```text
Authentication

Authorization

Object ownership

Scopes

Tenant boundaries
```


# Burp Suite CORS Workflow

Use:

```text
Proxy

HTTP History

Repeater

Comparer
```


# Step 1 - Capture Baseline

```http
GET /api/profile HTTP/1.1
Host: api.example.com
```


# Step 2 - Add Origin

```http
Origin: https://app.example.com
```


# Step 3 - Send to Repeater

Record:

```text
Status

ACAO

ACAC

Vary

Response data
```


# Step 4 - Change Origin

```http
Origin: https://cors-test.invalid
```


# Step 5 - Compare

Determine whether the server:

```text
Rejects

Omits CORS headers

Reflects origin

Returns wildcard

Allows credentials
```


# Step 6 - Browser Validation

If potentially exploitable, validate actual browser behaviour from a controlled origin.


# Burp Suite CSRF Workflow

Capture the state-changing request.


# Step 1

Send it to Repeater.


# Step 2

Identify:

```text
Session cookie

CSRF token

Origin

Referer

Content-Type

Custom headers
```


# Step 3

Test one control at a time.

```text
Remove CSRF token

Empty CSRF token

Invalid CSRF token

Other-session token

Remove Origin

Change Origin

Remove Referer

Change Referer
```


# Step 4

Record whether the action actually occurred.


# Do Not Rely Only on Status

A response:

```text
200 OK
```

does not necessarily mean the state changed.

A response:

```text
302 Found
```

does not necessarily mean the request failed.


# Verify State

Check:

```text
Profile

Database-backed value

Account page

API response

Audit entry
```

where appropriate.


# Burp Engagement Tools

For CSRF testing, useful Burp capabilities include:

```text
Repeater

Comparer

Proxy

Logger

Browser
```


# Burp PoC Generation

Burp may provide CSRF proof-of-concept generation for suitable requests.

Always review generated HTML before using it.


# Why

Generated forms may:

```text
Omit required fields

Handle encodings differently

Trigger real state changes

Not represent browser behaviour accurately
```


# CORS Browser Testing

Burp Repeater is useful for identifying server policy.

A browser is required to prove browser-enforced CORS behaviour.


# curl for CORS

Trusted origin:

```bash
curl -i \
  -H 'Origin: https://app.example.com' \
  https://api.example.com/profile
```


# Untrusted Origin

```bash
curl -i \
  -H 'Origin: https://cors-test.invalid' \
  https://api.example.com/profile
```


# Null Origin

```bash
curl -i \
  -H 'Origin: null' \
  https://api.example.com/profile
```


# Preflight

```bash
curl -i \
  -X OPTIONS \
  -H 'Origin: https://app.example.com' \
  -H 'Access-Control-Request-Method: PUT' \
  -H 'Access-Control-Request-Headers: authorization,content-type' \
  https://api.example.com/profile
```


# Remember

curl shows:

```text
Server response
```

not:

```text
Browser enforcement
```


# Source Code Review - CORS

Search:

```bash
rg -ni 'cors|Access-Control-Allow-Origin|allow.?origin|allowed.?origin|Origin' .
```


# Credentials

```bash
rg -ni 'allow.?credentials|Access-Control-Allow-Credentials|credentials.*true' .
```


# Origin Validation

```bash
rg -ni 'origin.*contains|origin.*startsWith|origin.*endsWith|origin.*includes|origin.*match' .
```


# Wildcards

```bash
rg -ni 'allow.?origin.*\*|origins?.*\*' .
```


# Environment Configuration

```bash
rg -ni 'CORS|ALLOWED_ORIGINS|TRUSTED_ORIGINS|FRONTEND_URL|APP_URL' -g '.env*' -g '*.yaml' -g '*.yml' -g '*.json' -g '*.toml' .
```


# Source Code Review - CSRF

Search:

```bash
rg -ni 'csrf|xsrf|anti.?forgery|request.?verification|forgery' .
```


# Tokens

```bash
rg -ni 'csrf.?token|xsrf.?token|anti.?forgery.?token' .
```


# Origin / Referer

```bash
rg -ni 'Origin|Referer|referrer|trusted.?origin' .
```


# SameSite

```bash
rg -ni 'SameSite|same_site|samesite' .
```


# Cookie Configuration

```bash
rg -ni 'HttpOnly|Secure|SameSite|Set-Cookie|cookie' .
```


# Node.js - CORS

Common package:

```text
cors
```


# Search

```bash
rg -ni 'require\(.cors.|from .cors.|cors\(' -g '*.js' -g '*.ts' .
```


# Example Configuration

```javascript
app.use(cors({
  origin: "https://app.example.com",
  credentials: true
}));
```


# Review

Determine whether:

```text
origin
```

is static or dynamically validated.


# Dangerous Concept

```javascript
origin: true
```

can reflect the requesting origin depending on framework/library usage.

Whether this is vulnerable depends on the application's intended trust model and credential/data exposure.


# Express CSRF

Search:

```bash
rg -ni 'csrf|csurf|csrfSync|csrfToken' -g '*.js' -g '*.ts' .
```


# Python - Flask CORS

Common package:

```text
flask-cors
```


# Search

```bash
rg -ni 'CORS\(|cross_origin|flask_cors' -g '*.py' .
```


# Django CORS

Common package:

```text
django-cors-headers
```


# Search

```bash
rg -ni 'CORS_ALLOWED_ORIGINS|CORS_ALLOW_ALL_ORIGINS|CORS_ALLOW_CREDENTIALS|corsheaders' -g '*.py' .
```


# Django CSRF

Search:

```bash
rg -ni 'csrf_exempt|csrf_protect|CSRF_TRUSTED_ORIGINS|CsrfViewMiddleware' -g '*.py' .
```


# High-Value Django Review

Pay attention to:

```text
@csrf_exempt
```


# Important

`@csrf_exempt` is not automatically a vulnerability.

Determine:

```text
Endpoint authentication

Request type

Alternative protections

State-changing behaviour
```


# Java / Spring CORS

Search:

```bash
rg -ni '@CrossOrigin|CorsConfiguration|allowedOrigins|allowedOriginPatterns|setAllowCredentials' -g '*.java' .
```


# Spring CSRF

Search:

```bash
rg -ni 'csrf\(|csrf\.disable|CsrfToken|CsrfTokenRepository|CookieCsrfTokenRepository' -g '*.java' .
```


# Security Review

Pay attention to configurations conceptually equivalent to:

```text
CSRF disabled globally
```

but determine whether the application is:

```text
Cookie-authenticated browser application
```

or:

```text
Stateless bearer-token API
```

before concluding it is vulnerable.


# .NET CORS

Search:

```bash
rg -ni 'AddCors|UseCors|AllowAnyOrigin|WithOrigins|AllowCredentials|SetIsOriginAllowed' -g '*.cs' .
```


# Dangerous Combination

Review configurations involving:

```text
AllowCredentials
```

and overly broad origin validation.


# .NET Antiforgery

Search:

```bash
rg -ni 'ValidateAntiForgeryToken|AutoValidateAntiforgeryToken|IgnoreAntiforgeryToken|IAntiforgery|AddAntiforgery' -g '*.cs' .
```


# PHP

Search:

```bash
rg -ni 'Access-Control-Allow-Origin|HTTP_ORIGIN|csrf|xsrf|SameSite' -g '*.php' .
```


# Go

Search:

```bash
rg -ni 'cors|AllowOrigins|AllowedOrigins|AllowCredentials|csrf|SameSite' -g '*.go' .
```


# Ruby on Rails

Search:

```bash
rg -ni 'rack-cors|origins|credentials|protect_from_forgery|skip_forgery_protection|SameSite' -g '*.rb' .
```


# Rails CSRF

Pay attention to:

```text
protect_from_forgery
```

and exceptions around state-changing controller actions.


# Reverse Proxy CORS

CORS may be configured at:

```text
Nginx

Apache

API gateway

CDN

Load balancer
```

rather than application code.


# Nginx Search

```bash
rg -ni 'Access-Control-Allow-Origin|add_header.*Access-Control|OPTIONS|http_origin' -g '*.conf' .
```


# Infrastructure as Code

Search:

```bash
rg -ni 'cors|allowed_origins|allow_origins|Access-Control' -g '*.tf' -g '*.yaml' -g '*.yml' -g '*.json' .
```


# API Gateways

Review CORS configuration for:

```text
AWS API Gateway

Azure API Management

Google Cloud API Gateway

Kong

Traefik

NGINX

Envoy
```


# Multiple Layers

A request may pass through:

```text
CDN
 |
 v
Reverse Proxy
 |
 v
API Gateway
 |
 v
Application
```


# Conflicting CORS Headers

Multiple layers can produce duplicate headers.

Example:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Origin: *
```


# Browser Behaviour

Duplicate CORS headers may cause the browser to reject the response rather than expand access.

Do not assume duplicate headers create a vulnerability.


# Source-to-Behaviour Validation

Source code alone is insufficient.

```text
Configuration
     |
     v
Expected Behaviour
     |
     v
Live Request
     |
     v
Browser Behaviour
```


# CSRF Framework Defaults

Modern frameworks often provide CSRF protections automatically.

Review whether developers have:

```text
Disabled middleware

Excluded routes

Created custom API endpoints

Bypassed validation

Misconfigured trusted origins
```


# Authentication Architecture First

Before reporting missing CSRF protection, determine:

```text
Cookie session?

Bearer token?

Mutual TLS?

HTTP Basic?

Custom authentication?
```


# Cookie Session

```text
Browser automatically attaches cookie
```

which can create CSRF exposure.


# Bearer Token

```text
JavaScript manually adds Authorization header
```

which generally changes the cross-site request model.


# Basic Authentication

Browsers may automatically send cached HTTP authentication credentials in some contexts.

Include this in CSRF threat modelling when applicable.


# WebSockets

WebSocket handshakes can also involve browser origin security.


# Example

```http
GET /socket HTTP/1.1
Host: target.example
Upgrade: websocket
Connection: Upgrade
Origin: https://app.example.com
Cookie: session=SESSION_VALUE
```


# Cross-Site WebSocket Hijacking

If authentication relies on cookies and the server does not validate Origin appropriately, another site may potentially initiate an authenticated WebSocket connection.


# Test Model

```text
Victim Session Cookie
       |
       v
Attacker Origin
       |
       v
WebSocket Handshake
       |
       v
Origin Validation?
```


# Review

```text
Origin validation

Cookie SameSite behaviour

Authentication

Per-message authorization

Sensitive data returned
```


# GraphQL

GraphQL commonly uses:

```http
POST /graphql
Content-Type: application/json
```


# CSRF Question

Does the endpoint also accept:

```text
GET

application/x-www-form-urlencoded

text/plain
```

for state-changing operations?


# Query Over GET

If mutations can be triggered through GET, review CSRF exposure carefully.


# APIs

For REST APIs, document:

```text
Authentication mechanism

Accepted content types

Allowed methods

CORS policy

CSRF protection
```


# File Uploads

File uploads using cookie authentication may require CSRF protection.

HTML forms can submit:

```text
multipart/form-data
```

cross-site.


# Administrative Interfaces

Administrative actions deserve particular attention because CSRF impact can be higher.

Examples:

```text
Create account

Assign role

Change SSO settings

Generate API key

Change webhook

Modify network allowlist
```


# Reauthentication

For highly sensitive operations, consider whether the application requires:

```text
Current password

MFA

Recent authentication
```

in addition to CSRF defenses.


# CSRF Is Not User Confirmation

A valid CSRF token proves request context, not necessarily deliberate user intent.


# Clickjacking Interaction

CSRF and clickjacking are different.

```text
CSRF
 |
 v
Attacker causes request

Clickjacking
 |
 v
Attacker tricks user into clicking framed UI
```


# Strong CSRF Does Not Prevent Clickjacking

Review frame protections separately where relevant.


# Content Security Policy

CSP is not a replacement for CSRF protection.


# Security Headers

Useful browser controls may include:

```text
Content-Security-Policy

X-Frame-Options

Referrer-Policy

Set-Cookie attributes
```

but none alone replaces proper request authorization.


# CORS Finding Evidence

Strong evidence includes:

```text
Sensitive endpoint

Victim test account

Untrusted controlled origin

Credentialed browser request

ACAO permitting controlled origin

ACAC where required

Sensitive response readable by attacker-origin JavaScript
```


# Weak Evidence

This alone is insufficient:

```http
Access-Control-Allow-Origin: *
```

on a public endpoint.


# CSRF Finding Evidence

Strong evidence includes:

```text
Authenticated test account

State-changing endpoint

Cross-site request

No valid anti-CSRF authorization

Victim credentials automatically attached

State change confirmed
```


# Weak Evidence

This alone is insufficient:

```text
No csrf_token parameter visible
```


# Alternative Defenses

The application may use:

```text
Origin validation

Custom request headers

SameSite cookies

Reauthentication

Framework-specific protection
```


# Reporting CORS Origin Reflection

> The API dynamically trusts arbitrary request origins and permits credentialed cross-origin access to authenticated responses. A page hosted on a controlled external origin was able to issue a request using the test user's browser credentials and read sensitive account data. The API should permit credentialed CORS access only from explicitly trusted origins.


# Reporting Weak Origin Validation

> The CORS allowlist uses insufficient origin matching and accepts origins that are not part of the intended trust boundary. A controlled lookalike origin was returned in `Access-Control-Allow-Origin` and could read the authenticated response in a browser. Origin values should be parsed and compared against explicit trusted scheme, host and port combinations.


# Reporting Null-Origin Trust

> The application permits credentialed cross-origin access from the `null` origin. A controlled browser context capable of generating a null origin successfully read authenticated response data. The application should remove `null` from the trusted origin policy unless it is explicitly required and supported by an equivalent security control.


# Reporting CSRF

> The account update endpoint accepts authenticated state-changing requests without verifying that they originated from the legitimate application. A controlled cross-site form caused the test user's browser to submit its existing session credentials and modify the account email address without a valid anti-CSRF token. State-changing browser requests should require robust CSRF protection such as a session-bound anti-CSRF token and appropriate origin validation.


# Reporting Missing CSRF Validation

> The application includes an anti-CSRF token in legitimate requests but does not enforce it server-side. Removing the token from a controlled state-changing request did not prevent the operation from completing. The server must reject protected requests when the expected CSRF token is missing, invalid or not associated with the appropriate session.


# Reporting Cross-Site WebSocket Hijacking

> The WebSocket endpoint authenticates users through browser cookies but does not restrict connection establishment to trusted origins. A controlled external origin was able to establish an authenticated WebSocket connection using the test user's existing browser session and access protected functionality. The WebSocket handshake should validate the Origin header against an explicit trusted allowlist in addition to enforcing normal authentication and authorization.


# Reporting GET State Change

> The application performs a state-changing operation through an authenticated GET request. Because cross-site GET requests can be triggered through standard browser navigation and embedded resources, another origin can cause the victim browser to perform the operation. State changes should use an appropriate non-GET method and require effective CSRF protection.


# Avoid Overclaiming

Do not report:

```text
CORS enabled
```

as a vulnerability.


# Do Not Report

```text
Access-Control-Allow-Origin: *
```

on intentionally public non-sensitive data as a vulnerability without additional impact.


# Do Not Report

```text
No CSRF token
```

without understanding:

```text
Authentication

SameSite

Origin validation

Request requirements
```


# Do Not Report

```text
SameSite=Lax
```

as automatically insecure.


# Do Not Report

```text
OPTIONS allows DELETE
```

as proof that an unauthorized DELETE operation is possible.


# Do Not Report

```text
Origin reflected
```

without establishing whether:

```text
Browser can send credentials

Sensitive response is readable

Origin is truly untrusted
```


# Severity - CORS

Consider:

```text
Data sensitivity

Credentialed access

Read vs write capability

Trusted origin scope

Account privilege

Cross-tenant exposure

Token exposure

Browser exploitability
```


# Severity - CSRF

Consider:

```text
Action performed

Victim privilege

Reversibility

User interaction

Reauthentication

Financial impact

Account takeover potential

Administrative impact
```


# High-Impact CORS

Examples:

```text
Arbitrary origin reads authenticated personal data

Arbitrary origin retrieves API tokens

Trusted attacker-controlled subdomain reads administrative API

Cross-origin access exposes high-value tenant data
```


# High-Impact CSRF

Examples:

```text
Change account recovery details

Add privileged user

Change security settings

Link attacker-controlled identity

Create privileged API credential

Modify payment destination
```


# Lower-Impact CSRF

Examples may include:

```text
Logout

Preference change

Low-impact profile field
```

depending on context.


# Root Causes - CORS

Common causes:

```text
Reflecting Origin blindly

Wildcard trust

Substring origin validation

Suffix validation errors

Overly broad subdomain trust

Trusting null origin

Credentials enabled unnecessarily

Multiple conflicting configuration layers
```


# Root Causes - CSRF

Common causes:

```text
No CSRF protection

Token generated but not validated

Token not session-bound

Unsafe GET state changes

Weak Origin validation

Overly permissive CORS

Inappropriate SameSite configuration

Framework CSRF disabled

Sensitive endpoint excluded from middleware
```


# Remediation - CORS

Maintain an explicit allowlist.

Example conceptual policy:

```text
https://app.example.com

https://admin.example.com
```


# Parse Origins Properly

Compare:

```text
Scheme

Host

Port
```

rather than strings containing trusted text.


# Avoid Arbitrary Reflection

Do not:

```text
Read Origin
    |
    v
Return Same Value
```

without validating it against the trust policy.


# Credentials

Enable:

```http
Access-Control-Allow-Credentials: true
```

only where credentialed cross-origin access is actually required.


# Minimize Trusted Origins

Every trusted origin expands the browser trust boundary.


# Review Subdomains

Remove obsolete or unnecessary origins from the allowlist.


# Preflight Policy

Allow only methods and headers required by legitimate clients.


# Remediation - CSRF

Use framework-provided CSRF protection where possible.


# Synchronizer Token

Conceptually:

```text
Session
   |
   v
Random CSRF Token
   |
   v
Form / Request
   |
   v
Server Validation
```


# Token Validation

Reject:

```text
Missing token

Invalid token

Token belonging to wrong session
```


# Origin Validation

Validate trusted origins for sensitive state-changing requests where appropriate.


# SameSite

Use an appropriate SameSite policy for session cookies as defense-in-depth.


# Avoid State Changes Through GET

Use methods appropriate to the operation.


# Reauthentication

Require recent authentication for high-risk security changes where appropriate.


# Content-Type

For APIs, strictly requiring intended content types can make simple cross-site request construction harder, but it should complement rather than replace the broader CSRF design.


# Custom Headers

Requiring a custom anti-CSRF header can be effective for AJAX APIs when combined with a restrictive CORS policy.


# Protect XSS Boundary

Because XSS can often bypass CSRF controls from within the trusted origin, XSS prevention remains essential.


# Retesting CORS

Repeat the exact origin used in the finding.


# Expected

```text
Untrusted Origin
      |
      v
No ACAO Permission
      |
      v
Browser Cannot Read Response
```


# Trusted Origin

Verify legitimate frontend functionality still works.


# Credential Retest

If credentials are not required cross-origin, verify:

```text
Access-Control-Allow-Credentials
```

has been removed or restricted appropriately.


# Origin Matching Retest

Test:

```text
Trusted exact origin

Lookalike domain

Sibling subdomain

Different scheme

Different port

null
```


# Browser Retest

Use the original browser proof rather than relying only on Repeater.


# Retesting CSRF

Repeat the original proof.


# Expected

```text
Cross-Site Request
       |
       v
Missing / Invalid Protection
       |
       v
Rejected
```


# Verify State

Confirm the protected value did not change.


# Valid Request

Then verify the legitimate application still works with:

```text
Valid token

Expected Origin

Normal browser flow
```


# Token Retest

Test:

```text
Missing token

Empty token

Invalid token

Other-session token
```


# Origin Retest

Test:

```text
Expected origin

Untrusted origin

Missing origin
```

according to the intended application policy.


# SameSite Retest

Inspect the final cookie attributes and verify browser behaviour where SameSite was part of the remediation.


# Equivalent Endpoints

After one CSRF issue is found, search for similar state-changing routes.

Examples:

```text
/account/*

/settings/*

/admin/*

/api/*

/profile/*

/users/*

/billing/*
```


# Equivalent CORS Endpoints

Review whether CORS is configured:

```text
Globally

Per controller

Per route

At gateway

At reverse proxy
```


# CORS Checklist

## Architecture

- [ ] Frontend origins identified
- [ ] API origins identified
- [ ] Authentication mechanism identified
- [ ] Credentialed CORS requirement understood
- [ ] Reverse proxy/CDN/gateway layers identified

## Headers

- [ ] `Access-Control-Allow-Origin` reviewed
- [ ] `Access-Control-Allow-Credentials` reviewed
- [ ] `Access-Control-Allow-Methods` reviewed
- [ ] `Access-Control-Allow-Headers` reviewed
- [ ] `Access-Control-Expose-Headers` reviewed
- [ ] `Access-Control-Max-Age` reviewed
- [ ] `Vary: Origin` reviewed where relevant

## Origin Validation

- [ ] Trusted origin tested
- [ ] Arbitrary origin tested
- [ ] Prefix lookalike tested
- [ ] Suffix lookalike tested
- [ ] Sibling subdomain tested
- [ ] Scheme variation tested
- [ ] Port variation tested
- [ ] `null` origin tested where relevant
- [ ] Wildcard behaviour understood

## Credentials

- [ ] Cookie behaviour understood
- [ ] Credentialed request tested
- [ ] Sensitive response identified
- [ ] Browser-readable response confirmed
- [ ] Token exposure reviewed

## Preflight

- [ ] OPTIONS request reviewed
- [ ] Allowed methods reviewed
- [ ] Allowed headers reviewed
- [ ] Authorization-header behaviour reviewed
- [ ] Actual request tested
- [ ] Preflight result not mistaken for authorization

## Trust Boundary

- [ ] All allowed origins inventoried
- [ ] Trusted subdomains reviewed
- [ ] User-controlled origins excluded
- [ ] Abandoned origins reviewed
- [ ] Development origins reviewed
- [ ] Origin takeover risk reviewed

## Evidence

- [ ] Baseline request captured
- [ ] Modified Origin captured
- [ ] CORS response headers captured
- [ ] Browser proof captured
- [ ] Sensitive data exposure confirmed
- [ ] Test account used
- [ ] Credentials/tokens redacted

## Retest

- [ ] Original untrusted origin rejected
- [ ] Lookalike origins rejected
- [ ] Null origin handled correctly
- [ ] Trusted origin still works
- [ ] Credential behaviour correct
- [ ] Browser proof no longer works


# CSRF Checklist

## Authentication

- [ ] Authentication mechanism identified
- [ ] Cookie authentication reviewed
- [ ] HTTP authentication reviewed where relevant
- [ ] Bearer-token architecture understood
- [ ] Automatically attached credentials identified

## State-Changing Actions

- [ ] Profile changes tested
- [ ] Email changes tested
- [ ] Password/security changes reviewed
- [ ] MFA changes reviewed
- [ ] Account linking reviewed
- [ ] Administrative actions reviewed
- [ ] API-key operations reviewed
- [ ] File uploads reviewed
- [ ] GET state changes identified

## CSRF Token

- [ ] Token presence reviewed
- [ ] Missing token tested
- [ ] Empty token tested
- [ ] Invalid token tested
- [ ] Other-session token tested
- [ ] Session binding reviewed
- [ ] Token predictability considered
- [ ] Server-side validation confirmed

## Origin Validation

- [ ] Origin header reviewed
- [ ] Trusted origin accepted
- [ ] Untrusted origin rejected
- [ ] Missing Origin behaviour understood
- [ ] Referer fallback reviewed
- [ ] URL parsing reviewed

## Cookies

- [ ] `SameSite` reviewed
- [ ] `Secure` reviewed
- [ ] `HttpOnly` reviewed
- [ ] `Domain` reviewed
- [ ] `Path` reviewed
- [ ] Sibling-subdomain implications reviewed

## Request Construction

- [ ] HTML form feasibility tested
- [ ] Simple POST tested
- [ ] GET behaviour reviewed
- [ ] `text/plain` acceptance reviewed
- [ ] Form-encoded acceptance reviewed
- [ ] Multipart acceptance reviewed
- [ ] Method override reviewed
- [ ] Custom headers reviewed

## APIs

- [ ] JSON content type enforced
- [ ] Alternative content types tested
- [ ] CORS interaction reviewed
- [ ] Custom anti-CSRF headers reviewed
- [ ] Object authorization separately tested

## WebSockets

- [ ] Cookie authentication identified
- [ ] Origin validation reviewed
- [ ] Cross-site handshake tested where relevant
- [ ] Sensitive message access reviewed
- [ ] Per-message authorization reviewed

## Evidence

- [ ] Legitimate baseline captured
- [ ] Cross-site request captured
- [ ] CSRF control removed/modified
- [ ] Browser credentials confirmed
- [ ] State change verified
- [ ] Controlled account used
- [ ] Reversible action used where possible

## Retest

- [ ] Original proof rejected
- [ ] Missing token rejected
- [ ] Invalid token rejected
- [ ] Other-session token rejected where applicable
- [ ] Untrusted origin rejected
- [ ] Legitimate application request succeeds
- [ ] Equivalent endpoints reviewed


# CORS Header Matrix

| Header | Security Question |
|---|---|
| `Access-Control-Allow-Origin` | Which origins can read the response? |
| `Access-Control-Allow-Credentials` | Can credentialed requests be exposed cross-origin? |
| `Access-Control-Allow-Methods` | Which methods are permitted by preflight? |
| `Access-Control-Allow-Headers` | Which request headers are permitted? |
| `Access-Control-Expose-Headers` | Which response headers can JavaScript read? |
| `Access-Control-Max-Age` | How long may preflight policy be cached? |
| `Vary: Origin` | Do caches distinguish origin-dependent responses? |


# Origin Test Matrix

| Origin | Purpose |
|---|---|
| Legitimate frontend | Baseline |
| Arbitrary external origin | Reflection test |
| Trusted-prefix lookalike | Prefix-validation test |
| Trusted-suffix lookalike | Suffix-validation test |
| Sibling subdomain | Subdomain trust |
| HTTP version of HTTPS origin | Scheme validation |
| Alternate port | Port validation |
| `null` | Null-origin policy |


# CSRF Defense Matrix

| Control | Purpose |
|---|---|
| CSRF token | Request authorization/correlation |
| Origin validation | Verify request source |
| Referer validation | Fallback source validation |
| SameSite | Restrict cross-site cookie sending |
| Custom header | Make simple cross-site request harder |
| Reauthentication | Protect sensitive operations |
| Correct HTTP methods | Avoid unsafe GET state changes |


# SameSite Matrix

| Value | General Intent |
|---|---|
| `Strict` | Strong cross-site cookie restriction |
| `Lax` | Allows some top-level navigation scenarios |
| `None` | Allows cross-site use; requires Secure in modern browsers |


# Request Matrix

| Request Type | Cross-Site Construction |
|---|---|
| GET | Easy |
| Form POST | Easy |
| `application/x-www-form-urlencoded` | HTML form |
| `multipart/form-data` | HTML form |
| `text/plain` | Possible through browser mechanisms |
| `application/json` | Normally requires JavaScript + preflight |
| Custom header | Normally requires preflight |
| PUT/PATCH/DELETE | Normally requires JavaScript + preflight |


# Authentication Matrix

| Authentication | Typical CSRF Relevance |
|---|---|
| Session cookie | High relevance |
| HTTP authentication | Review carefully |
| Client certificate | Review browser behaviour |
| JS-added Bearer header | Different threat model |
| API key in custom header | Usually not automatically attached |


# Finding Matrix

| Observation | Conclusion |
|---|---|
| Arbitrary ACAO on public data | Usually informational/expected |
| Arbitrary ACAO + credentials + sensitive readable data | Potential CORS vulnerability |
| Missing CSRF token but Origin strictly validated | Additional analysis required |
| No token + no origin defense + cookie auth + state change | Strong CSRF indication |
| SameSite=Lax only | Not automatically vulnerable |
| OPTIONS allows DELETE | Not proof of authorization bypass |
| GET performs sensitive state change | Strong CSRF concern |


# Evidence Matrix

| Finding | Evidence |
|---|---|
| CORS origin reflection | Request Origin + response ACAO |
| Credentialed CORS | ACAO + ACAC + browser credentials |
| CORS data exposure | Browser-readable sensitive response |
| CSRF | Cross-site request + authenticated state change |
| Missing token validation | Removed token + successful action |
| Weak Origin validation | Untrusted Origin + successful action |
| WebSocket hijacking | External Origin + authenticated socket |


# Remediation Matrix

| Weakness | Primary Control |
|---|---|
| Arbitrary CORS reflection | Explicit origin allowlist |
| Weak domain matching | Parse and exactly compare origin |
| Excessive trusted origins | Reduce trust boundary |
| Unnecessary credentials | Disable credentialed CORS |
| Missing CSRF protection | Framework CSRF protection/token |
| Weak token validation | Session-bound validation |
| Unsafe GET state change | Appropriate HTTP method + CSRF |
| Weak source validation | Strict Origin validation |
| Cross-site cookies unnecessary | Appropriate SameSite policy |
| Cross-site WebSocket access | Origin validation |


# CORS Decision Model

```text
               REQUEST ORIGIN
                      |
                      v
               PARSE ORIGIN
                      |
                      v
            TRUSTED EXACT ORIGIN?
                 +----+----+
                 |         |
                YES        NO
                 |         |
                 v         v
            CORS POLICY   NO CORS
                 |
                 v
        CREDENTIALS REQUIRED?
             +---+---+
             |       |
            YES      NO
             |       |
             v       v
       ALLOW CREDENTIALS
         IF INTENDED
```


# Credentialed CORS Model

```text
          ATTACKER ORIGIN
                |
                v
          fetch(credentials)
                |
                v
             BROWSER
                |
                v
         TARGET API REQUEST
                |
                v
          SESSION COOKIE?
                |
                v
         CORS RESPONSE
                |
        +-------+-------+
        |               |
    UNTRUSTED         TRUSTED
        |               |
        v               v
 BROWSER BLOCKS    JS READS DATA
   RESPONSE
```


# CSRF Decision Model

```text
             STATE-CHANGING REQUEST
                      |
                      v
          AUTOMATIC CREDENTIALS?
                 +----+----+
                 |         |
                NO        YES
                 |         |
                 v         v
          LOWER CSRF     CAN ATTACKER
           EXPOSURE      BUILD REQUEST?
                              |
                         +----+----+
                         |         |
                        NO        YES
                         |         |
                         v         v
                     RESTRICTED   CSRF DEFENSE?
                                      |
                                 +----+----+
                                 |         |
                               VALID      MISSING/
                                 |        BYPASSABLE
                                 v         |
                               ALLOW       v
                                         RISK
```


# CSRF Token Model

```text
                USER SESSION
                     |
                     v
               CSRF TOKEN
                     |
                     v
              LEGITIMATE FORM
                     |
                     v
                SUBMISSION
                     |
                     v
            SERVER VALIDATION
                     |
              +------+------+
              |             |
            VALID         INVALID
              |             |
              v             v
            ACTION         REJECT
```


# CORS and CSRF Interaction Model

```text
                  ATTACKER SITE
                       |
                       v
                 CROSS-ORIGIN JS
                       |
                       v
                 CORS PREFLIGHT
                       |
                +------+------+
                |             |
              DENIED        ALLOWED
                |             |
                v             v
              STOP       CUSTOM HEADER
                              |
                              v
                       CREDENTIALS SENT
                              |
                              v
                       TARGET ENDPOINT
                              |
                              v
                         CSRF CONTROL
```


# SameSite Model

```text
                 BROWSER COOKIE
                       |
                       v
                   SameSite
                       |
          +------------+------------+
          |            |            |
       Strict         Lax          None
          |            |            |
          v            v            v
       Stronger      Some        Cross-Site
      Cross-Site   Navigation       Use
     Restriction   Exceptions
```


# Source Review Model

```text
              AUTHENTICATION
                    |
                    v
               COOKIE POLICY
                    |
                    v
                CORS CONFIG
                    |
                    v
              ORIGIN PARSING
                    |
                    v
             CSRF MIDDLEWARE
                    |
                    v
              ROUTE EXCEPTIONS
                    |
                    v
             STATE-CHANGING API
                    |
                    v
               AUTHORIZATION
```


# Practical Validation Model

```text
Identify Authentication
        |
        v
Capture Baseline Request
        |
        v
Identify Browser Trust Boundary
        |
        +------------------+
        |                  |
        v                  v
      CORS               CSRF
        |                  |
        v                  v
Test Origins       Test Request Controls
        |                  |
        v                  v
Test Credentials   Test Token / Origin
        |                  |
        v                  v
Browser Proof      Cross-Site Proof
        |                  |
        +---------+--------+
                  |
                  v
             Verify Impact
                  |
                  v
            Capture Evidence
                  |
                  v
             Remediation
                  |
                  v
                Retest
```


# Final Testing Principle

CORS testing is not:

```text
Add Origin header
      |
      v
See ACAO
      |
      v
Report vulnerability
```

It is:

```text
UNTRUSTED ORIGIN
       |
       v
BROWSER REQUEST
       |
       v
CREDENTIALS
       |
       v
SERVER CORS POLICY
       |
       v
BROWSER READ ACCESS
       |
       v
SENSITIVE IMPACT
```


# CSRF Testing Is Not

```text
No csrf_token parameter
       |
       v
Report CSRF
```


# It Is

```text
AUTHENTICATED USER
       |
       v
ATTACKER-CONTROLLED CROSS-SITE REQUEST
       |
       v
AUTOMATIC CREDENTIALS
       |
       v
MISSING OR BYPASSABLE REQUEST AUTHORIZATION
       |
       v
STATE CHANGE
       |
       v
VERIFIED IMPACT
```


# Final Questions

For every CORS implementation ask:

```text
Which origins are supposed to be trusted?

Is the origin parsed correctly?

Is exact scheme, host and port validation used?

Are arbitrary origins reflected?

Are lookalike domains accepted?

Are sibling subdomains trusted?

Are abandoned subdomains trusted?

Is null origin trusted?

Are credentials enabled?

Are credentials actually required?

Does the endpoint return sensitive data?

Can an attacker-controlled browser origin read the response?

Does the browser actually send the relevant cookie?

Are wildcard origins used only for public resources?

Are preflight methods unnecessarily broad?

Are custom headers unnecessarily allowed?

Are sensitive response headers exposed?

Is Vary: Origin correct where caching matters?

Is CORS configured at multiple layers?

Can duplicate headers create inconsistent behaviour?

Does the API still enforce authentication?

Does the API enforce authorization?

Does the API enforce object ownership?

Does the API enforce tenant boundaries?
```


# For Every CSRF Implementation Ask

```text
How is the user authenticated?

Does the browser attach credentials automatically?

Which requests change state?

Can those requests be created cross-site?

Are any state changes performed through GET?

Is a CSRF token present?

Is the token actually validated?

What happens when the token is removed?

What happens when the token is empty?

What happens when the token is invalid?

Is the token bound to the session?

Can another account's token be reused?

Is Origin validated?

Is Referer used as fallback?

Are origin URLs parsed safely?

What happens when Origin is missing?

What SameSite value does the session cookie use?

Are sibling subdomains part of the same-site trust boundary?

Does the endpoint accept simple content types?

Can application/json be changed to text/plain?

Can a form-encoded body reach the same handler?

Is multipart/form-data accepted?

Are method overrides supported?

Can a custom header defense be bypassed through CORS?

Does the application require reauthentication for high-risk actions?

Are account-linking operations protected?

Are MFA changes protected?

Are administrative operations protected?

Are file uploads protected?

Are WebSocket connections origin-validated?

Does GraphQL accept state-changing GET requests?

Does the application verify actual state change rather than only HTTP status?

Are framework CSRF exclusions justified?

Does XSS undermine the assumed CSRF protection?

Has the issue been demonstrated with controlled accounts?

Is the action reversible?

Has the exact impact been verified?

Have session cookies and tokens been redacted from evidence?
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Authentication and Session Testing Cheatsheet](authentication-session-testing.md)
- [Authorization, IDOR and BOLA Cheatsheet](authorization-access-control.md)
- [JWT Security Testing Cheatsheet](jwt.md)
- [OAuth 2.0 and OpenID Connect Security Testing Cheatsheet](oauth-oidc.md)
- [Cross-Site Scripting (XSS) Cheatsheet](xss.md)
- [curl Cheatsheet](curl.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

Useful deeper notes include:

```text
docs/web/cors.md
docs/web/csrf.md
docs/web/authentication.md
docs/web/authorisation.md
docs/web/api-security.md
docs/web/clickjacking.md
```


# References

- [MDN - Cross-Origin Resource Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS){ target="_blank" rel="noopener noreferrer" }
- [MDN - Same-Origin Policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy){ target="_blank" rel="noopener noreferrer" }
- [MDN - Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy - CORS](https://portswigger.net/web-security/cors){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy - CSRF](https://portswigger.net/web-security/csrf){ target="_blank" rel="noopener noreferrer" }
- [OWASP Cross-Origin Resource Sharing Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Origin_Resource_Sharing_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for Cross Site Request Forgery](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Start with the authentication model"

    Before testing CSRF, determine exactly how the browser authenticates to the target. Cookie-based sessions and JavaScript-added bearer tokens have different cross-site request properties.


!!! tip "CORS needs a browser proof"

    Burp Repeater can reveal server-side CORS policy, but the strongest validation demonstrates that JavaScript running on a controlled untrusted origin can actually read the sensitive authenticated response in a browser.


!!! tip "Verify the state change"

    For CSRF testing, do not treat an HTTP 200 or redirect as proof. Confirm that the intended account or application state actually changed.


!!! tip "Review CORS and CSRF together"

    A custom anti-CSRF header can be an effective control because cross-origin JavaScript normally requires preflight to send it. If CORS also trusts an attacker-controlled origin, that security assumption may fail.


!!! warning "CORS is not authorization"

    CORS controls browser response access. It does not prevent curl, Burp, mobile applications or other non-browser clients from calling an API. Authentication and authorization must still be enforced independently.


!!! warning "SameSite is not the whole CSRF model"

    SameSite cookies provide important browser-level protection, but the effective security depends on request type, site relationships, cookie configuration and application architecture. Sensitive applications should use a layered CSRF defense appropriate to their threat model.
