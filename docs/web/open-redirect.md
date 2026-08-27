# Open Redirect

Open Redirect occurs when an application redirects a user to a destination influenced by attacker-controlled input without sufficiently restricting where the browser may be sent.

A typical flow looks like:

```text
User
 ↓
Trusted Application
 ↓
Redirect Parameter
 ↓
Application Generates Redirect
 ↓
Browser Follows Redirect
 ↓
External Destination
```

For example:

```text
https://target.example/redirect?url=https://example.com
```

may return:

```http
HTTP/1.1 302 Found
Location: https://example.com
```

The security issue is not simply that a redirect exists.

The important question is:

```text
Can an attacker control the redirect destination beyond the application's intended trust boundary?
```

!!! warning "Authorised Security Testing"
    Perform redirect testing only against applications included in the authorised assessment scope. Use harmless destinations such as `https://example.com` or controlled infrastructure where explicitly authorised. Avoid constructing deceptive links for real users.

---

# Why Open Redirect Matters

An Open Redirect may allow a trusted application URL to send users to an attacker-controlled destination.

Potential impact includes:

```text
Phishing
Trusted-domain abuse
Security control bypass
OAuth redirect chaining
Authentication workflow manipulation
Referer trust abuse
Token or code leakage in specific workflows
Chaining with other vulnerabilities
```

The severity depends heavily on context.

A simple redirect to an external website may be relatively low impact.

The same redirect inside:

```text
OAuth
SSO
Password reset
Authentication
Account linking
Payment workflow
```

may become significantly more important.

---

# Redirect Types

Redirects can occur:

```text
Server-side
Client-side
DOM-based
Meta refresh
JavaScript
Framework routing
```

---

# Server-Side Redirect

A server-side redirect commonly returns:

```http
HTTP/1.1 302 Found
Location: https://example.com
```

Other status codes include:

```text
301
302
303
307
308
```

The browser then follows the:

```http
Location:
```

header.

---

# Client-Side Redirect

JavaScript may perform the redirect.

Examples include:

```javascript
window.location = destination;
```

```javascript
location.href = destination;
```

```javascript
location.assign(destination);
```

```javascript
location.replace(destination);
```

These may not produce an HTTP 3xx response.

---

# Meta Refresh

HTML may redirect using:

```html
<meta http-equiv="refresh" content="0;url=https://example.com">
```

This is a browser-side redirect.

---

# Common Redirect Parameters

Look for parameters such as:

```text
url
uri
redirect
redirect_url
redirect_uri
return
returnUrl
return_url
returnTo
return_to
next
continue
destination
dest
target
callback
callbackUrl
goto
go
out
view
forward
ref
link
```

Do not assume a parameter is vulnerable based only on its name.

Observe its actual behaviour.

---

# Common Redirect Endpoints

Potentially interesting paths include:

```text
/redirect
/redirector
/out
/go
/forward
/login
/logout
/auth
/callback
/oauth/callback
/continue
/return
```

Redirect behaviour is also frequently embedded in normal application endpoints.

---

# Discovery Workflow

A practical workflow:

```text
Browse Application
      ↓
Burp Proxy
      ↓
HTTP History
      ↓
Search for 3xx Responses
      ↓
Inspect Location Header
      ↓
Identify Input Influencing Destination
      ↓
Send to Repeater
      ↓
Test Controlled Destination
```

---

# Search Burp History

Search for:

```text
Location:
```

and status codes:

```text
301
302
303
307
308
```

Also search request parameters for:

```text
redirect
url
return
next
continue
callback
destination
```

---

# Establish the Baseline

Suppose the application uses:

```http
GET /login?returnUrl=/dashboard HTTP/1.1
Host: target.example
```

Response:

```http
HTTP/1.1 302 Found
Location: /dashboard
```

This establishes the intended behaviour.

Do not immediately assume external destinations are accepted.

---

# Harmless External Destination

Where external redirect testing is authorised, use:

```text
https://example.com
```

For example:

```http
GET /redirect?url=https%3A%2F%2Fexample.com HTTP/1.1
Host: target.example
```

If the response becomes:

```http
HTTP/1.1 302 Found
Location: https://example.com
```

then an external redirect has potentially been demonstrated.

---

# Relative Redirects

Some applications intentionally allow only local paths.

Example:

```text
/dashboard
/profile
/settings
```

This is generally safer than allowing arbitrary absolute URLs.

However, validation should still ensure the value cannot be interpreted as an external destination.

---

# Absolute URLs

Example:

```text
https://example.com
```

If arbitrary absolute URLs are accepted, the application likely provides an externally controllable redirect.

The business purpose still matters.

Some redirect services intentionally support external destinations.

---

# Protocol-Relative URLs

A URL beginning with:

```text
//
```

may inherit the current scheme.

For example:

```text
//example.com
```

can be interpreted by browsers as an external host.

Therefore a filter that only blocks:

```text
http://
https://
```

may not adequately restrict external destinations.

---

# URL Parsing

Redirect validation should use a proper URL parser.

URLs contain multiple components:

```text
scheme://userinfo@host:port/path?query#fragment
```

Conceptually:

```text
https://user@example.com:443/path?x=1#section
```

Security decisions should be based on the parsed destination rather than substring matching.

---

# Hostname Validation

Suppose the application intends to allow:

```text
target.example
```

A weak check might ask:

```text
Does the URL contain "target.example"?
```

That is not sufficient.

The application should determine the actual parsed hostname.

---

# Subdomain Considerations

If redirects to subdomains are intentionally allowed, define the policy explicitly.

For example:

```text
*.target.example
```

requires careful hostname boundary validation.

A hostname that merely contains:

```text
target.example
```

is not necessarily a subdomain of it.

---

# Userinfo Component

URLs can contain user information before the host.

Conceptually:

```text
https://userinfo@host.example/
```

Validation logic should not confuse text in the userinfo component with the actual hostname.

This is another reason to use a proper URL parser.

---

# Ports

If the application allows trusted absolute URLs, consider whether ports matter.

For example:

```text
https://target.example:443/
```

and:

```text
https://target.example:8443/
```

may reach different services.

The expected policy depends on the application.

---

# Schemes

Redirect functionality should normally define which URL schemes are allowed.

Common web schemes:

```text
https
http
```

Other URI schemes may have different browser or operating-system behaviour.

Avoid testing unusual or potentially dangerous URI schemes unless specifically required and authorised.

For normal Open Redirect validation, demonstrating redirection to:

```text
https://example.com
```

is usually sufficient.

---

# URL Encoding

Redirect values are often URL encoded.

Example:

```text
https%3A%2F%2Fexample.com
```

The application may perform one or more decoding operations.

Conceptually:

```text
Request
  ↓
URL Decode
  ↓
Framework
  ↓
Validation
  ↓
Redirect
```

Understand which representation is validated and which representation is ultimately used.

---

# Double Encoding

Multiple application layers may decode values differently.

Conceptually:

```text
Encoded Input
    ↓
Proxy Decode
    ↓
Framework Decode
    ↓
Application
```

The security question is:

```text
Does validation occur on the same canonical value that is used for redirection?
```

Do not randomly generate encoding variants without understanding the processing chain.

---

# Backslashes

URL parsers and browsers may differ in how they treat:

```text
/
\
```

particularly when validation uses one parser and navigation uses another.

Modern applications should use consistent, standards-compliant URL parsing and validation.

---

# Duplicate Parameters

Example:

```text
?url=/dashboard&url=https://example.com
```

Different components may select:

```text
First value
Last value
All values
```

This can matter when:

```text
Security validation
```

and:

```text
Redirect execution
```

use different parsers.

---

# Parameter Pollution

Conceptually:

```text
Proxy
 ↓
Framework
 ↓
Validation
 ↓
Application
```

If components interpret duplicate parameters differently, validation may not apply to the value actually used.

This overlaps with HTTP Parameter Pollution testing.

---

# Fragments

URL fragments begin with:

```text
#
```

and are generally processed by the browser rather than sent to the server as part of the HTTP request.

However, fragments can matter in client-side redirect logic and historical OAuth flows.

---

# Query Parameters

Redirect destinations may themselves contain query parameters.

Example:

```text
https://target.example/redirect?url=https://example.com/?source=test
```

Ensure validation applies to the actual destination host rather than unrelated query-string text.

---

# Redirect Chaining

A redirect may initially point to another trusted endpoint:

```text
Application A
     ↓
Trusted Redirect Endpoint
     ↓
External Destination
```

This can become important when another security control allowlists the first application.

Conceptually:

```text
Security-Sensitive Workflow
        ↓
Trusted URL
        ↓
Open Redirect
        ↓
Unexpected Destination
```

---

# Open Redirect and OAuth

Open Redirects are particularly important around OAuth.

A simplified OAuth flow:

```text
Authorization Server
        ↓
redirect_uri
        ↓
Client Callback
```

Suppose the OAuth provider allows:

```text
https://target.example/callback
```

If the callback or related trusted path can redirect externally, the trust chain should be reviewed carefully.

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# OAuth Redirect Chaining

Conceptually:

```text
Authorization Server
        ↓
Trusted Client Domain
        ↓
Open Redirect
        ↓
External Destination
```

The impact depends on:

```text
OAuth flow
Redirect URI validation
Response mode
Code handling
Token handling
Browser behaviour
```

Do not assume every Open Redirect automatically compromises OAuth.

Demonstrate the actual chain.

---

# Open Redirect and Authentication

Authentication flows commonly use:

```text
returnUrl
next
continue
redirect
```

Example:

```text
/login?returnUrl=/dashboard
```

The intended flow:

```text
Unauthenticated User
       ↓
Login
       ↓
Successful Authentication
       ↓
Dashboard
```

If arbitrary destinations are accepted:

```text
Unauthenticated User
       ↓
Trusted Login Page
       ↓
Successful Authentication
       ↓
External Destination
```

This may make phishing or workflow manipulation more convincing.

---

# Post-Login Redirects

Always test redirect parameters:

```text
Before login
After login
After failed login
After logout
After password reset
After account creation
```

Different application branches may apply different validation.

---

# Logout Redirects

Example:

```text
/logout?returnUrl=/
```

or:

```text
/logout?post_logout_redirect_uri=...
```

Logout flows deserve separate testing, particularly in:

```text
OIDC
SSO
Federated authentication
```

---

# Password Reset

Password reset workflows may redirect users after completing a reset.

Example:

```text
/reset/complete?next=/login
```

Determine whether:

```text
next
```

can cross the intended origin boundary.

---

# Email Verification

Verification links may contain:

```text
continue
return
next
redirect
```

Example:

```text
/verify?token=...&continue=/dashboard
```

Because these links are often delivered by trusted email infrastructure, an external redirect can increase social-engineering credibility.

---

# Invitation Workflows

Organisation invitations may contain post-acceptance redirects.

Example:

```text
/invite/accept?token=...&next=/workspace
```

Test whether the redirect destination is independent of the security-sensitive invitation state.

---

# Payment Workflows

Applications may use parameters such as:

```text
success_url
cancel_url
return_url
```

Do not assume the application controls the third-party payment provider's redirect policy.

Test only the components included in scope.

Business logic is particularly important here.

---

# SSO

SSO systems frequently involve multiple redirects:

```text
Application
 ↓
Identity Provider
 ↓
Application Callback
 ↓
Application Destination
```

Map every redirect separately.

A redirect may be safe at one stage and weak at another.

---

# Open Redirect and Phishing

A trusted domain can make a malicious destination appear more credible.

Conceptually:

```text
https://trusted.example/redirect?url=EXTERNAL
```

The beginning of the URL belongs to the legitimate organisation.

The browser ultimately reaches another destination.

For reporting, a harmless destination such as:

```text
https://example.com
```

is normally enough to demonstrate the behaviour.

Do not create credential-harvesting pages.

---

# Open Redirect and Referer

Redirects can influence:

```http
Referer:
```

behaviour.

Whether sensitive information leaks depends on:

```text
Referrer-Policy
Browser behaviour
URL contents
Destination
```

Do not assume that query parameters automatically leak through Referer.

Verify actual browser behaviour.

---

# Open Redirect and Sensitive URL Data

Applications should avoid placing sensitive values in URLs in the first place.

Potentially sensitive values include:

```text
Tokens
Authorization codes
Password reset secrets
Session identifiers
```

If a redirect can cause such information to leave the intended trust boundary, the impact can become much greater.

---

# Open Redirect and SSRF

Open Redirect and SSRF are different vulnerabilities.

Open Redirect:

```text
Application
 ↓
Browser Redirect
 ↓
External Destination
```

SSRF:

```text
Application Server
 ↓
Server-Side Request
 ↓
Destination
```

However, an SSRF filter may allow a trusted URL that subsequently redirects elsewhere.

Conceptually:

```text
SSRF Function
    ↓
Trusted URL
    ↓
HTTP Redirect
    ↓
Restricted Destination
```

Therefore redirect following can be relevant during SSRF testing.

Refer to:

```text
docs/web/ssrf.md
```

---

# Open Redirect and HTML Injection

HTML Injection can create a new link:

```html
<a href="https://example.com">Continue</a>
```

This is not an Open Redirect.

An Open Redirect requires an existing application mechanism that performs the navigation.

Refer to:

```text
docs/web/html-injection.md
```

---

# Open Redirect and XSS

Redirect parameters may occasionally enter:

```text
HTML
JavaScript
DOM
```

rather than being used exclusively for navigation.

Therefore a parameter named:

```text
redirect
```

could potentially participate in:

```text
Open Redirect
HTML Injection
DOM XSS
Reflected XSS
```

depending on the sink.

Always identify the actual data flow.

---

# DOM-Based Open Redirect

Client-side JavaScript may read attacker-controlled input and assign it to a navigation sink.

Example conceptually:

```javascript
const destination = new URLSearchParams(location.search).get("next");
location.href = destination;
```

Flow:

```text
location.search
      ↓
next
      ↓
location.href
      ↓
Browser Navigation
```

If arbitrary external URLs are allowed, this may constitute a DOM-based Open Redirect.

---

# JavaScript Redirect Sinks

Search JavaScript for:

```text
location
location.href
window.location
location.assign
location.replace
window.open
```

Then trace attacker-controlled sources.

---

# Common Client-Side Sources

Potential sources include:

```text
location.search
location.hash
document.URL
document.referrer
postMessage
localStorage
sessionStorage
```

Again, source-to-sink analysis is more useful than blindly searching for payloads.

---

# Source-to-Sink Analysis

A useful model:

```text
SOURCE
  ↓
redirect parameter
  ↓
TRANSFORMATION
  ↓
URL parsing
  ↓
VALIDATION
  ↓
NAVIGATION SINK
```

The critical question is:

```text
What destination does the browser actually navigate to?
```

---

# Burp Suite Workflow

A structured workflow:

```text
Proxy
  ↓
Browse Application
  ↓
HTTP History
  ↓
Identify Redirect
  ↓
Identify Influencing Parameter
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Use Controlled Destination
  ↓
Inspect Location Header
  ↓
Verify Browser Behaviour
```

---

# Burp Repeater

Example baseline:

```http
GET /redirect?url=/dashboard HTTP/1.1
Host: target.example
```

Response:

```http
HTTP/1.1 302 Found
Location: /dashboard
```

Controlled test:

```http
GET /redirect?url=https%3A%2F%2Fexample.com HTTP/1.1
Host: target.example
```

Potential vulnerable response:

```http
HTTP/1.1 302 Found
Location: https://example.com
```

This provides clear evidence.

---

# Burp Proxy

Proxy is useful for finding redirects during normal browsing.

Look for:

```text
Login redirects
Logout redirects
SSO redirects
OAuth redirects
Return URLs
Navigation endpoints
Tracking links
External links
```

---

# Burp Comparer

Comparer can help when different redirect values cause subtly different responses.

Compare:

```text
Valid local path
Invalid local path
External destination
Malformed destination
```

---

# Browser Verification

Always verify actual browser behaviour where safe.

The response may contain:

```http
Location: ...
```

but client-side logic or browser parsing may alter the final navigation behaviour.

Record:

```text
Initial URL
Redirect response
Location value
Final browser destination
```

---

# curl

Server-side redirects can be inspected without automatically following them:

```bash
curl -i \
  "https://target.example/redirect?url=https%3A%2F%2Fexample.com"
```

To view the redirect chain:

```bash
curl -i -L \
  "https://target.example/redirect?url=https%3A%2F%2Fexample.com"
```

Be careful with `-L` when testing unknown redirect chains because curl will follow the destination.

---

# Redirect Mapping

Create a table:

| Endpoint | Parameter | Local Redirect | External Redirect |
|---|---|---:|---:|
| `/login` | `returnUrl` | Yes | No |
| `/logout` | `next` | Yes | Yes |
| `/redirect` | `url` | Yes | Yes |
| `/oauth/callback` | `continue` | Yes | Unknown |

This helps identify the most security-sensitive redirect points.

---

# Authentication Redirect Matrix

Test redirects around:

| Workflow | Parameter | Test |
|---|---|---|
| Login | `returnUrl` | External destination |
| Logout | `next` | External destination |
| Registration | `continue` | External destination |
| Password reset | `redirect` | External destination |
| Email verification | `next` | External destination |
| SSO | `returnTo` | External destination |
| OAuth | `redirect_uri` | Registered URI policy |

Do not treat OAuth `redirect_uri` exactly like an ordinary application redirect parameter. OAuth has additional protocol-specific requirements.

---

# Redirect Validation Approaches

Preferred designs include:

```text
Relative application paths
```

or:

```text
Server-side identifiers mapped to destinations
```

For example:

```text
?destination=dashboard
```

Server:

```text
dashboard → /dashboard
profile   → /profile
settings  → /settings
```

This avoids accepting arbitrary URLs.

---

# Allowlisting

If external redirects are genuinely required:

```text
Parse URL
   ↓
Validate Scheme
   ↓
Validate Host
   ↓
Validate Port if relevant
   ↓
Apply Explicit Policy
   ↓
Redirect
```

Do not use simple substring matching.

---

# Weak Validation Patterns

Conceptually weak checks include:

```text
URL contains trusted-domain
URL starts with trusted text
URL ends with trusted text without hostname parsing
Block only "http://"
Block only "https://"
```

The application should validate the parsed URL components.

---

# Relative Paths

Where possible, accept only:

```text
/dashboard
/profile
/account
```

and reject:

```text
Absolute external URLs
Protocol-relative URLs
Unexpected schemes
```

The exact policy depends on application requirements.

---

# Redirect Interstitial

For functionality that intentionally redirects users to arbitrary external sites, an interstitial warning can reduce phishing risk.

Example:

```text
You are leaving target.example.

Destination:
example.com

Continue?
```

This does not replace appropriate validation in security-sensitive workflows.

---

# Open Redirect Testing Checklist

## Discovery

```text
[ ] Search 3xx responses
[ ] Search Location headers
[ ] Search redirect parameters
[ ] Review login
[ ] Review logout
[ ] Review registration
[ ] Review password reset
[ ] Review email verification
[ ] Review OAuth/OIDC
[ ] Review SSO
[ ] Review payment workflows
```

## Parameters

```text
[ ] url
[ ] redirect
[ ] redirect_url
[ ] redirect_uri
[ ] return
[ ] returnUrl
[ ] return_to
[ ] next
[ ] continue
[ ] destination
[ ] callback
[ ] goto
```

## Destination Handling

```text
[ ] Relative path
[ ] Absolute URL
[ ] Protocol-relative URL
[ ] Hostname parsing
[ ] Subdomain handling
[ ] Port handling
[ ] URL encoding
[ ] Duplicate parameters
```

## Client Side

```text
[ ] Search window.location
[ ] Search location.href
[ ] Search location.assign
[ ] Search location.replace
[ ] Search window.open
[ ] Trace source to sink
```

## Impact

```text
[ ] Trusted-domain phishing potential
[ ] Authentication workflow
[ ] OAuth workflow
[ ] SSO workflow
[ ] Sensitive URL data
[ ] Security control chaining
[ ] SSRF redirect chaining
```

---

# Open Redirect Decision Tree

```text
Redirect Found
     ↓
What Controls Destination?
     ↓
Static / User Controlled?
     ↓
User Controlled
     ↓
Relative Paths Only?
     ↓
Yes → Review Parsing
     ↓
No / Absolute URLs Accepted
     ↓
Can External Host Be Used?
     ↓
No → Review Validation
     ↓
Yes
     ↓
Open Redirect Candidate
     ↓
Where Is It Used?
     ↓
┌────────────┬────────────┬────────────┐
↓            ↓            ↓            ↓
General     Login        OAuth        SSO
↓            ↓            ↓            ↓
└────────────┴──────┬─────┴────────────┘
                    ↓
              Assess Context
                    ↓
              Demonstrate Safely
                    ↓
                  Report
```

---

# Open Redirect Quick Reference

```text
COMMON PARAMETERS

url
redirect
redirect_url
return
returnUrl
return_to
next
continue
destination
callback
goto
```

```text
CONTROLLED DESTINATION

https://example.com
```

```text
SERVER-SIDE INDICATOR

HTTP/1.1 302 Found
Location: https://example.com
```

```text
CLIENT-SIDE SINKS

window.location
location.href
location.assign
location.replace
window.open
```

---

# Evidence Collection

For a confirmed Open Redirect record:

```text
Affected endpoint
Affected parameter
Original request
Modified request
HTTP response
Location header
Final destination
Authentication state
Required user interaction
Relevant workflow
Security impact
```

Use a harmless external destination for evidence whenever possible.

---

# Example Finding

```text
Finding:
Open Redirect Through returnUrl Parameter

Affected Endpoint:
GET /login

Affected Parameter:
returnUrl

Expected:
Post-authentication redirection should remain within the trusted application.

Observed:
The application accepted an absolute external URL and redirected the browser to that destination after the workflow completed.

Controlled Destination:
https://example.com

Impact:
An attacker may construct a URL on the trusted application domain that ultimately redirects users to an external destination. This may increase the credibility of phishing attacks and may have additional impact when combined with authentication or identity workflows.
```

---

# Example OAuth-Related Finding

```text
Finding:
Open Redirect on Trusted OAuth Client Domain

Affected Endpoint:
/redirect

Expected:
Redirect destinations used within authentication-related workflows should remain within explicitly trusted locations.

Observed:
The endpoint accepts an arbitrary external HTTPS destination.

Impact:
The redirect may weaken trust assumptions made by authentication or OAuth workflows that treat the application's domain as a trusted redirect location.

Further impact should be based on a demonstrated authentication or OAuth chain rather than assumed.
```

---

# Reporting Titles

Prefer:

```text
Open Redirect Through returnUrl Parameter

Post-Login Open Redirect to Arbitrary External Domains

Open Redirect in Logout Workflow

Open Redirect in Email Verification Workflow

DOM-Based Open Redirect Through next Parameter

Open Redirect on OAuth Client Domain
```

Avoid vague titles such as:

```text
URL Redirect Issue
```

---

# Severity

Open Redirect severity is context dependent.

A standalone redirect may often be:

```text
Low
```

or:

```text
Informational
```

depending on the programme's methodology.

Impact may increase when the redirect interacts with:

```text
OAuth
SSO
Sensitive tokens
Authentication
Password reset
Trusted security controls
```

Do not inflate severity based on hypothetical chaining.

Demonstrate the chain where possible.

---

# Remediation

The safest approach is to avoid accepting arbitrary redirect URLs.

Prefer:

```text
Server-side destination identifiers
```

or:

```text
Validated relative paths
```

---

# Destination Mapping

Instead of:

```text
?url=https://somewhere.example
```

use:

```text
?destination=dashboard
```

and map it server-side:

```text
dashboard → /dashboard
profile   → /profile
help      → /help
```

The client cannot directly control the resulting origin.

---

# URL Parsing

If absolute URLs are required:

```text
Parse URL
 ↓
Validate Scheme
 ↓
Validate Hostname
 ↓
Validate Port
 ↓
Apply Explicit Allowlist
 ↓
Redirect
```

Use established URL parsing libraries.

---

# Host Allowlist

Conceptually:

```text
Allowed:

target.example
accounts.target.example
support.target.example
```

Compare against the parsed hostname.

Do not use:

```text
contains()
```

for domain validation.

---

# Scheme Allowlist

For normal web redirects, explicitly allow required schemes such as:

```text
https
```

rather than attempting to blacklist every unwanted scheme.

---

# Canonicalisation

Validation and navigation should operate on the same canonical URL representation.

Avoid:

```text
Validate one representation
        ↓
Decode / Transform
        ↓
Redirect another representation
```

---

# Authentication Workflows

For:

```text
Login
Logout
Password reset
Registration
Email verification
```

prefer internal relative destinations or predefined identifiers.

Security-sensitive workflows rarely need unrestricted external redirects.

---

# OAuth

OAuth redirect URI validation should follow OAuth-specific security guidance.

Do not implement:

```text
substring matching
```

or broad wildcard redirect rules where avoidable.

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# References

## PortSwigger Web Security Academy: Open Redirection

https://portswigger.net/kb/issues/00500100_open-redirection-reflected

Useful background on reflected Open Redirect behaviour.

---

## PortSwigger DOM-Based Open Redirection

https://portswigger.net/web-security/dom-based/open-redirection

Useful for client-side redirect source-to-sink testing.

---

## OWASP Unvalidated Redirects and Forwards Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html

Useful defensive guidance for safe redirect implementation.

---

## OWASP WSTG: Testing for Client-Side URL Redirect

https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/04-Testing_for_Client-side_URL_Redirect

Useful methodology for client-side redirect testing.

---

## OAuth 2.0 Security Best Current Practice

https://datatracker.ietf.org/doc/html/rfc9700

Relevant when Open Redirect behaviour interacts with OAuth security.

---

# Final Open Redirect Testing Model

```text
                   APPLICATION
                        ↓
                 REDIRECT FOUND
                        ↓
             WHAT CONTROLS DESTINATION?
                        ↓
                  USER INPUT?
                        ↓
                       YES
                        ↓
                 PARSE DESTINATION
                        ↓
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
     Scheme            Host             Port
       ↓                ↓                ↓
       └────────────────┼────────────────┘
                        ↓
               TRUST BOUNDARY CHECK
                        ↓
             EXTERNAL DESTINATION?
                        ↓
                       YES
                        ↓
                  WHICH WORKFLOW?
                        ↓
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
    General           Login            OAuth
       ↓                ↓                ↓
       └────────────────┼────────────────┘
                        ↓
                  SSO / RESET / ETC.
                        ↓
                 ASSESS THE CHAIN
                        ↓
             USE HARMLESS DESTINATION
                        ↓
                 COLLECT EVIDENCE
                        ↓
                      REPORT
```

The key principle is:

> Do not test Open Redirect as a collection of URL tricks. Identify where the destination originates, how the application parses and validates it, what trust boundary the browser ultimately crosses, and whether the redirect participates in a more security-sensitive workflow such as authentication, SSO or OAuth.
