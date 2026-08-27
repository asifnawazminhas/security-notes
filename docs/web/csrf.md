# Cross-Site Request Forgery

Cross-Site Request Forgery (CSRF) occurs when an attacker causes a victim's browser to perform an unwanted action against an application where the victim is already authenticated.

The vulnerability relies on the browser automatically including authentication information such as:

```text
Session cookies
Authentication cookies
Client certificates
HTTP authentication credentials
```

A basic CSRF flow looks like:

```text
Victim Authenticates
        ↓
Application Sets Session Cookie
        ↓
Victim Visits Attacker-Controlled Page
        ↓
Browser Sends Forged Request
        ↓
Session Cookie Automatically Included
        ↓
Application Accepts Request
        ↓
Victim's Account Performs Action
```

The attacker does not necessarily need to know the victim's session cookie.

The browser supplies it automatically when the request satisfies the relevant cookie rules.

!!! warning "Authorised Security Testing"
    Perform CSRF testing only against applications for which you have explicit authorisation. Use accounts and data you control. Avoid sending proof-of-concept requests to real users. For state-changing actions, use reversible changes wherever possible.

---

# Mental Model

Suppose an authenticated user changes their email address using:

```http
POST /account/email HTTP/1.1
Host: target.example
Cookie: session=REDACTED
Content-Type: application/x-www-form-urlencoded

email=user@example.com
```

If the application relies only on the session cookie to authorise the action, another website may be able to cause the victim's browser to submit the same request.

Conceptually:

```text
Attacker Website
      ↓
Victim Browser
      ↓
POST /account/email
      ↓
Browser Adds Session Cookie
      ↓
Target Application
      ↓
Email Address Changed
```

The core security question is:

> Can another origin cause the victim's browser to perform an authenticated state-changing action?

---

# CSRF Requirements

Traditional CSRF normally requires several conditions.

```text
1. A relevant state-changing action exists

2. Authentication is automatically attached by the browser

3. The attacker can reproduce the required request

4. The request lacks effective anti-CSRF protection
```

Potentially interesting actions include:

```text
Change email address
Change password
Change phone number
Update profile
Add payment details
Change shipping address
Create API key
Delete API key
Enable integration
Disable security control
Add user
Remove user
Change role
Create administrator
Delete account
Submit transaction
Change notification settings
Connect external account
Change MFA settings
```

---

# CSRF vs XSS

CSRF and XSS are different vulnerability classes.

CSRF:

```text
Attacker Site
     ↓
Victim Browser
     ↓
Authenticated Request
     ↓
Target Application
```

XSS:

```text
Attacker Input
     ↓
Target Application
     ↓
Victim Browser
     ↓
Attacker-Controlled Script Executes
```

The important distinction is:

```text
CSRF
Abuses authenticated browser requests

XSS
Executes attacker-controlled browser-side code
```

---

# XSS Can Defeat CSRF Protections

If an attacker has JavaScript execution within the target application's origin, many CSRF protections can potentially be bypassed because the malicious script operates from the trusted origin.

For example, same-origin JavaScript may be able to:

```text
Read CSRF tokens
Submit authenticated requests
Read application responses
Interact with protected APIs
```

Therefore:

> XSS can frequently undermine CSRF protections.

Fix XSS independently even when strong CSRF protection exists.

---

# CSRF vs CORS

CSRF and CORS are frequently confused.

They solve different problems.

CSRF asks:

```text
Can another site cause the browser to send
an authenticated request?
```

CORS asks:

```text
Can JavaScript from another origin read
or interact with a cross-origin response?
```

A browser may send a cross-origin request even when JavaScript cannot read the response.

Therefore:

```text
CORS blocking response access
≠
CSRF protection
```

---

# Same-Origin Policy

The Same-Origin Policy primarily restricts how one origin can interact with resources from another origin.

An origin consists of:

```text
Scheme
Host
Port
```

For example:

```text
https://example.com
```

and:

```text
https://example.com:8443
```

are different origins.

However, the Same-Origin Policy does not prevent every type of cross-origin request.

Browsers historically allow actions such as:

```text
Form submissions
Image loading
Navigation
Script loading
Stylesheet loading
```

under various circumstances.

This is why CSRF is possible.

---

# CSRF Testing Workflow

A structured workflow can look like:

```text
Identify State-Changing Functionality
              ↓
Capture Legitimate Request
              ↓
Identify Authentication Mechanism
              ↓
Identify CSRF Protection
              ↓
Remove CSRF Token
              ↓
Modify CSRF Token
              ↓
Test Token Binding
              ↓
Review SameSite Cookies
              ↓
Review Origin / Referer Validation
              ↓
Determine Cross-Origin Request Format
              ↓
Generate Controlled PoC
              ↓
Test With Controlled Victim Session
              ↓
Confirm State Change
              ↓
Assess Impact
              ↓
Report
```

---

# Start With State-Changing Requests

CSRF testing should focus primarily on requests that modify application state.

Examples:

```text
POST
PUT
PATCH
DELETE
```

However, HTTP method alone does not determine whether an action changes state.

Applications sometimes incorrectly perform state-changing actions using:

```text
GET
```

For example:

```http
GET /account/delete?id=123 HTTP/1.1
```

This can be particularly easy to exploit through CSRF.

---

# Build a State-Changing Request Inventory

While browsing the application, keep track of interesting actions.

For example:

| Action | Method | Endpoint |
|---|---|---|
| Change email | POST | `/account/email` |
| Change password | POST | `/account/password` |
| Add user | POST | `/admin/users` |
| Delete API key | DELETE | `/api/keys/123` |
| Update profile | PATCH | `/api/profile` |
| Logout | POST | `/logout` |

Then assess each request's CSRF protection.

---

# Burp Suite Workflow

Burp Suite is one of the best tools for manual CSRF testing.

A practical workflow:

```text
Browser
  ↓
Burp Proxy
  ↓
HTTP History
  ↓
Find State-Changing Request
  ↓
Send to Repeater
  ↓
Analyse Cookies
  ↓
Analyse CSRF Token
  ↓
Modify / Remove Protection
  ↓
Generate CSRF PoC
  ↓
Test in Controlled Browser
```

---

# Burp Proxy

Use Proxy to capture legitimate application requests.

Look for:

```text
POST
PUT
PATCH
DELETE
```

and state-changing GET requests.

Pay attention to:

```text
Cookie
Authorization
Origin
Referer
Content-Type
CSRF token
Custom headers
```

---

# Burp Repeater

Send interesting requests to Repeater.

For example:

```http
POST /account/email HTTP/1.1
Host: target.example
Cookie: session=REDACTED
Content-Type: application/x-www-form-urlencoded
Origin: https://target.example

email=test1@example.com
```

Confirm the request works normally.

Then systematically modify the request.

---

# First Test: Remove the CSRF Token

Suppose the legitimate request contains:

```http
POST /account/email HTTP/1.1
Host: target.example
Cookie: session=REDACTED
Content-Type: application/x-www-form-urlencoded

email=test@example.com&csrf=abc123
```

Remove:

```text
csrf=abc123
```

and resend.

If the request still succeeds:

```text
Token may not be required.
```

This is one of the first CSRF tests to perform.

---

# Second Test: Change the Token

Replace the token:

```text
csrf=abc123
```

with:

```text
csrf=invalid
```

or another clearly invalid controlled value.

If the request still succeeds:

```text
The token may not be validated correctly.
```

---

# Third Test: Empty Token

Try:

```text
csrf=
```

Some applications validate only whether the parameter exists rather than whether it contains a valid token.

Compare:

```text
Missing
Empty
Invalid
Valid
```

---

# Token Validation Matrix

A simple matrix is useful:

| Test | Result |
|---|---|
| Valid token | Accepted |
| Missing token | ? |
| Empty token | ? |
| Invalid token | ? |
| Token from another session | ? |
| Token from another user | ? |
| Reused token | ? |

This quickly shows how the protection behaves.

---

# CSRF Token Binding

A CSRF token should generally be associated with the user's authenticated session or otherwise cryptographically bound to the relevant security context.

Test:

```text
User A Token
    ↓
User B Request
```

If User A's token works in User B's session:

```text
Token may not be correctly bound.
```

Use only test accounts you control.

---

# Cross-Account Token Test

With two authorised accounts:

```text
Account A
Account B
```

capture a valid CSRF token from Account A.

Then use:

```text
Account B session cookie
+
Account A CSRF token
```

If the request succeeds, investigate whether the token is globally valid rather than session-bound.

---

# Static Tokens

A token may appear to be:

```text
Same across requests
Same across sessions
Same across users
```

A static token is suspicious.

However, do not assume vulnerability solely because the token remains unchanged.

Determine whether:

```text
Token is unpredictable
Token is secret
Token is session-bound
Token is validated
```

---

# Token Reuse

A CSRF token does not necessarily need to be single-use.

Reusable session-bound tokens are common.

Therefore:

```text
Token works twice
```

does not automatically mean:

```text
CSRF vulnerability
```

The important properties are usually:

```text
Unpredictability
Validation
Correct binding
```

---

# Synchronizer Token Pattern

A common CSRF defence uses a server-generated token associated with the user's session.

Conceptually:

```text
User Session
     ↓
Server Generates Token
     ↓
Token Embedded in Page
     ↓
Form Submission
     ↓
Server Compares Token
```

The attacker cannot normally know the token because another origin cannot read the protected page due to the Same-Origin Policy.

---

# Double-Submit Cookie Pattern

Another design uses a token in both:

```text
Cookie
+
Request Parameter / Header
```

Conceptually:

```text
CSRF Cookie
    +
CSRF Request Value
    ↓
Server Compares Values
```

A robust implementation should cryptographically bind the token to the authenticated session where appropriate.

Simply comparing attacker-influenceable values can be unsafe.

---

# Signed Double-Submit Cookie

A stronger double-submit design can bind the token to session-specific information using a keyed cryptographic construction.

Conceptually:

```text
Session Information
      +
Server Secret
      ↓
HMAC
      ↓
CSRF Token
```

This prevents an attacker from simply creating arbitrary matching token values.

---

# CSRF Tokens in Headers

Modern applications often send tokens through headers such as:

```text
X-CSRF-Token
X-CSRFToken
X-XSRF-TOKEN
XSRF-TOKEN
RequestVerificationToken
```

Example:

```http
X-CSRF-Token: abc123
```

Custom headers can provide useful protection because ordinary HTML forms cannot arbitrarily add them.

However, CORS configuration becomes relevant.

---

# Angular XSRF Pattern

Angular commonly supports an XSRF pattern using:

```text
XSRF-TOKEN
```

cookie and:

```text
X-XSRF-TOKEN
```

request header.

Conceptually:

```text
Cookie
 ↓
Angular Reads Token
 ↓
Adds Header
 ↓
Server Validates Header
```

The server still needs to validate the token correctly.

---

# Anti-Forgery Tokens in ASP.NET

ASP.NET applications may use anti-forgery functionality involving values such as:

```text
__RequestVerificationToken
```

These may appear in:

```text
Cookies
Form parameters
Headers
```

Do not remove only one component and conclude the protection is absent.

Determine the complete validation mechanism.

---

# Django CSRF

Django commonly uses:

```text
csrftoken
```

and may expect:

```text
csrfmiddlewaretoken
```

or:

```text
X-CSRFToken
```

Django also performs origin-related checks for relevant requests.

When testing Django applications, determine whether the application uses the framework's protection correctly or disables it for specific endpoints.

---

# Laravel CSRF

Laravel applications commonly use:

```text
_token
```

or headers such as:

```text
X-CSRF-TOKEN
X-XSRF-TOKEN
```

Endpoints excluded from CSRF middleware should receive particular attention.

---

# Rails CSRF

Ruby on Rails commonly embeds authenticity tokens in forms and metadata.

Look for:

```text
authenticity_token
```

The important question remains:

```text
Is the token required and correctly validated?
```

---

# CSRF Token in JSON

Some applications include a token within JSON:

```json
{
  "email": "test@example.com",
  "csrfToken": "abc123"
}
```

Test:

```text
Remove token
Invalid token
Empty token
Other-session token
```

just as with form parameters.

---

# SameSite Cookies

Modern browsers support the `SameSite` cookie attribute.

Possible values include:

```text
Strict
Lax
None
```

This attribute can significantly affect CSRF exploitability.

Example:

```http
Set-Cookie: session=abc123; Secure; HttpOnly; SameSite=Lax
```

---

# SameSite Strict

```text
SameSite=Strict
```

provides the strongest cross-site cookie restriction.

The browser generally does not include the cookie in cross-site requests.

Conceptually:

```text
Attacker Site
    ↓
Cross-Site Request
    ↓
Session Cookie Not Included
```

This can strongly reduce traditional CSRF risk.

However, application design and same-site relationships still matter.

---

# SameSite Lax

```text
SameSite=Lax
```

allows cookies in certain top-level cross-site navigations, particularly safe-method navigation scenarios.

This means state-changing GET requests remain particularly dangerous.

For example:

```html
<a href="https://target.example/account/delete">
```

could potentially trigger a state-changing GET action if the application incorrectly uses GET for sensitive operations.

---

# SameSite None

```text
SameSite=None
```

allows cookies to be sent in cross-site contexts.

Modern browsers require:

```text
Secure
```

alongside `SameSite=None`.

Example:

```http
Set-Cookie: session=abc123; Secure; SameSite=None
```

Applications using `SameSite=None` should not rely on SameSite as their primary CSRF defence.

---

# SameSite Default Behaviour

Modern browsers may apply default SameSite behaviour when the attribute is omitted.

Do not assume all browsers and application environments behave identically.

Explicitly configure the intended SameSite policy.

---

# Site vs Origin

`SameSite` and Same-Origin Policy do not use exactly the same security boundary.

This distinction is important.

Conceptually:

```text
Origin
=
Scheme + Host + Port
```

while site calculations are based around the registrable domain and scheme.

Therefore, two applications can be:

```text
Same-site
```

but:

```text
Cross-origin
```

This matters when assessing sibling subdomains.

---

# Sibling Subdomains

Consider:

```text
app.example.com
blog.example.com
```

These are different origins but may be considered same-site.

A vulnerable or attacker-controlled sibling subdomain can therefore change the threat model for SameSite-based protection.

Do not assume:

```text
SameSite=Strict
```

solves every trust issue involving sibling subdomains.

---

# Cookie Domain

Review:

```http
Domain=.example.com
```

versus a host-only cookie.

A broadly scoped cookie may be sent to multiple subdomains.

This can increase risk if another subdomain is:

```text
Compromised
Untrusted
User-controlled
Vulnerable to subdomain takeover
```

---

# Origin Header

Browsers may send:

```http
Origin: https://target.example
```

for relevant requests.

Applications can validate the Origin header to ensure the request originates from an approved origin.

For a cross-origin request:

```http
Origin: https://attacker.example
```

The server can reject it.

---

# Origin Validation Testing

Capture a legitimate request:

```http
Origin: https://target.example
```

Then test:

```text
Remove Origin
Change Origin
Use unrelated origin
Use malformed origin where appropriate
```

Observe whether the request is accepted.

---

# Weak Origin Validation

Weak validation might conceptually check:

```text
Origin contains "target.example"
```

rather than parsing and comparing the actual origin.

Secure validation should compare against explicit trusted origins.

Do not use substring matching.

---

# Referer Validation

Applications may also validate:

```http
Referer: https://target.example/account
```

A cross-site request may contain:

```http
Referer: https://attacker.example/
```

Referer checking can provide additional defence but should be implemented carefully.

---

# Missing Referer

Some clients or privacy controls may suppress Referer.

Applications therefore sometimes allow requests when:

```text
Referer is missing
```

This can weaken the defence.

Test:

```text
Valid Referer
Invalid Referer
Missing Referer
```

---

# Origin vs Referer

Prefer:

```text
Origin
```

when available because it contains less path information and is specifically useful for origin validation.

A robust application may use:

```text
Origin validation
```

with carefully designed fallback behaviour.

---

# Burp CSRF PoC Generator

Burp Suite can generate a CSRF proof of concept for suitable requests.

Typical workflow:

```text
Proxy / Repeater
      ↓
Right-Click Request
      ↓
Engagement Tools
      ↓
Generate CSRF PoC
```

Depending on the Burp version and interface, the exact menu placement may differ.

The generated HTML can then be reviewed and tested in a controlled environment.

---

# Basic HTML Form PoC

Suppose the vulnerable request is:

```http
POST /account/email HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

email=csrf-test@example.com
```

A basic controlled PoC may look like:

```html
<!doctype html>
<html>
  <body>
    <form action="https://target.example/account/email" method="POST">
      <input type="hidden" name="email" value="csrf-test@example.com">
      <input type="submit" value="Submit test">
    </form>
  </body>
</html>
```

Use only an account and state change you control.

---

# Automatic Form Submission

For controlled testing, the form can be automatically submitted:

```html
<!doctype html>
<html>
  <body>
    <form id="csrf-test"
          action="https://target.example/account/email"
          method="POST">

      <input type="hidden"
             name="email"
             value="csrf-test@example.com">

    </form>

    <script>
      document.getElementById("csrf-test").submit();
    </script>
  </body>
</html>
```

This models how a victim visiting another page could trigger the action.

---

# GET-Based CSRF

State-changing GET requests are particularly problematic.

Suppose:

```http
GET /account/email?email=csrf-test@example.com HTTP/1.1
```

A cross-site resource or navigation may be enough to trigger it.

For example:

```html
<img src="https://target.example/account/email?email=csrf-test@example.com">
```

or:

```html
<a href="https://target.example/account/email?email=csrf-test@example.com">
  Open
</a>
```

Sensitive state changes should not use GET.

---

# Why GET Should Be Safe

HTTP semantics expect GET to be:

```text
Safe
```

meaning it should retrieve information rather than perform significant state changes.

Sensitive actions should use appropriate methods such as:

```text
POST
PUT
PATCH
DELETE
```

together with CSRF protection where browser-managed authentication is used.

---

# Form Content Types

HTML forms normally support:

```text
application/x-www-form-urlencoded
multipart/form-data
text/plain
```

This is important when determining whether a request can be reproduced cross-origin without JavaScript access to the target origin.

---

# application/x-www-form-urlencoded

This is the standard form encoding.

Example:

```http
Content-Type: application/x-www-form-urlencoded

email=test@example.com&name=Asif
```

It is straightforward to reproduce using an HTML form.

---

# multipart/form-data

HTML forms can also send:

```text
multipart/form-data
```

This is commonly used for:

```text
File uploads
Complex forms
```

Do not assume multipart requests are automatically protected from CSRF.

---

# text/plain

HTML forms can submit:

```text
text/plain
```

This occasionally becomes relevant when APIs parse request bodies loosely.

Applications should validate expected content types strictly.

---

# JSON and CSRF

Developers sometimes assume:

```text
JSON API = No CSRF
```

This is not always safe.

The actual questions are:

```text
Can the browser create a request the endpoint accepts?

Are credentials automatically attached?

Does the server strictly require application/json?

Does CORS permit attacker-controlled JavaScript?

Does the server accept alternative content types?

Can method or format overrides be used?
```

---

# JSON Endpoint Example

Suppose:

```http
POST /api/profile HTTP/1.1
Host: target.example
Cookie: session=REDACTED
Content-Type: application/json

{
  "displayName": "Asif"
}
```

If the server strictly requires:

```text
Content-Type: application/json
```

then a normal cross-origin HTML form cannot directly reproduce the same request body and content type.

However, continue testing the surrounding behaviour.

---

# Content-Type Confusion

Some APIs accept the same data using multiple content types.

For example:

```text
application/json
application/x-www-form-urlencoded
text/plain
```

If an endpoint accepts a simple form-compatible content type, CSRF may become possible.

Test whether content-type validation is strict.

---

# JSON Parsing With text/plain

Some frameworks or custom middleware may attempt to parse a JSON-looking body even when:

```http
Content-Type: text/plain
```

This can weaken assumptions that JSON endpoints are inherently protected.

Test the server's actual behaviour rather than relying on the documented API format.

---

# CORS and JSON CSRF

A cross-origin JavaScript request using:

```text
application/json
```

typically triggers a CORS preflight.

Conceptually:

```text
Attacker JavaScript
      ↓
OPTIONS Preflight
      ↓
Server
      ↓
CORS Decision
      ↓
Actual Request
```

If CORS is securely configured, arbitrary attacker origins should not be allowed to send credentialed requests requiring non-simple characteristics.

---

# Credentialed CORS

A dangerous configuration may involve:

```http
Access-Control-Allow-Origin: https://attacker.example
Access-Control-Allow-Credentials: true
```

If an attacker-controlled origin is trusted, the impact may extend beyond traditional CSRF because attacker JavaScript may also be able to read responses.

Report the CORS weakness separately where appropriate.

---

# Custom Headers

Requiring a custom header can help protect APIs because ordinary cross-origin forms cannot add arbitrary headers.

For example:

```http
X-CSRF-Token: abc123
```

or even an application-specific header:

```http
X-Requested-By: WebApp
```

However:

```text
Custom Header
+
Overly Permissive CORS
```

can undermine the protection.

---

# Method Override

Some frameworks support method overrides such as:

```text
_method=DELETE
_method=PUT
```

or headers such as:

```text
X-HTTP-Method-Override
```

An endpoint that appears to require DELETE may still be reachable through a form-compatible POST.

Review method-override functionality.

---

# CSRF in REST APIs

For REST APIs, determine the authentication mechanism.

If authentication uses:

```text
Cookie-based session
```

CSRF may be relevant.

If authentication requires:

```http
Authorization: Bearer TOKEN
```

and the browser does not automatically attach the token cross-origin, traditional CSRF is usually much less applicable.

---

# Cookie Authentication vs Bearer Authentication

Cookie authentication:

```text
Browser
 ↓
Automatically Adds Cookie
 ↓
CSRF Relevant
```

Bearer token stored and explicitly attached by JavaScript:

```text
JavaScript
 ↓
Adds Authorization Header
 ↓
Attacker Site Does Not Know Token
```

Traditional CSRF generally relies on credentials being automatically attached.

However, token storage introduces separate risks such as XSS.

---

# HTTP Basic Authentication

Browsers can automatically reuse HTTP authentication credentials in some contexts.

Therefore applications relying on:

```text
Basic Authentication
Digest Authentication
```

may still require CSRF consideration depending on browser and application behaviour.

---

# Client Certificates

Applications using client certificates can also have CSRF concerns because authentication occurs at the transport/browser level rather than through an attacker-known secret.

Again, determine whether cross-site requests are accepted.

---

# Login CSRF

CSRF is not limited to actions performed after login.

Login CSRF occurs when an attacker causes a victim to log into an application using an account controlled by the attacker.

Conceptually:

```text
Attacker Creates Account
        ↓
Attacker Knows Credentials
        ↓
Victim Visits Malicious Page
        ↓
Login Request Submitted
        ↓
Victim Browser Logged Into Attacker Account
```

This can create confusing and potentially dangerous account interactions.

---

# Login CSRF Impact

Imagine an application where users later enter:

```text
Search history
Personal information
Payment information
Uploaded documents
Messages
```

If the victim unknowingly uses an attacker-controlled account, that information may become visible to the attacker through that account.

Therefore login endpoints may also require CSRF protection.

---

# Logout CSRF

An attacker may be able to force a user to log out.

For example:

```text
Attacker Site
    ↓
/logout
    ↓
Victim Session Destroyed
```

Logout CSRF is usually lower impact than account modification CSRF, but can still affect:

```text
Availability
Workflow
User experience
Security-sensitive processes
```

Logout should ideally use an appropriate state-changing request rather than an unprotected GET.

---

# Password Change CSRF

Password changes are high-value CSRF targets.

A secure password change flow may require:

```text
Current password
CSRF token
Reauthentication
```

If the application allows:

```text
New password only
```

and lacks CSRF protection, an attacker may potentially change the victim's password.

Use controlled test accounts only.

---

# Email Change CSRF

Changing an email address can be particularly serious because email may be used for:

```text
Password reset
Account recovery
Security notifications
MFA recovery
```

A vulnerable flow may enable account takeover.

Applications should consider:

```text
CSRF protection
Reauthentication
Email confirmation
Notification to old address
```

---

# MFA Configuration CSRF

Security-sensitive actions include:

```text
Enable MFA
Disable MFA
Change MFA device
Regenerate recovery codes
Change recovery phone
```

These should generally require stronger controls than ordinary profile updates.

Consider:

```text
CSRF token
Reauthentication
Current MFA confirmation
```

---

# API Key CSRF

Actions involving API credentials are high value.

Examples:

```text
Create API key
Delete API key
Rotate API key
Change API permissions
```

CSRF against an API-key creation endpoint could potentially cause credentials to be created under the victim's account.

Whether the attacker can obtain the resulting secret is a separate question.

---

# Administrative CSRF

Administrative interfaces can have particularly high-impact CSRF.

Interesting actions include:

```text
Create user
Create administrator
Change role
Reset password
Disable account
Change security policy
Configure integration
Change callback URL
Modify SSO
Upload configuration
Change access control
```

Test only with authorised administrative test accounts.

---

# CSRF in Multi-Step Actions

Some actions involve several steps.

For example:

```text
Step 1
Enter new email

Step 2
Review

Step 3
Confirm
```

Do not assume multi-step workflows prevent CSRF.

Determine whether:

```text
Every state-changing step is protected
```

and whether an attacker can directly invoke the final step.

---

# Step Skipping

Capture the final request.

Then determine whether it requires server-side state created during previous steps.

For example:

```text
Step 1
Generate transaction context

Step 2
Confirm transaction
```

If Step 2 accepts arbitrary values without validating the prior workflow, the intermediate step may provide little protection.

---

# Confirmation Pages

A confirmation page is not itself CSRF protection.

For example:

```text
POST /change-email
        ↓
Confirmation Page
        ↓
POST /confirm-email
```

If both requests can be forged, the additional page does not prevent CSRF.

---

# Reauthentication

For particularly sensitive actions, requiring the user's password or MFA again provides additional protection.

Examples:

```text
Change password
Disable MFA
Change recovery email
Delete account
Transfer funds
Create privileged administrator
```

Reauthentication complements CSRF protection.

It should not necessarily replace it.

---

# CSRF in File Uploads

File uploads can potentially be CSRF targets when:

```text
Victim's browser can submit the form cross-site
```

However, browsers intentionally restrict programmatic selection of arbitrary local files.

An attacker cannot normally cause a victim's browser to upload an arbitrary local file without user interaction.

Still, upload forms may contain other state-changing fields worth testing.

---

# CSRF in Profile Changes

Profile functionality commonly contains good CSRF test cases:

```text
Display name
Email
Phone
Address
Company
Website
Preferences
Notification settings
```

These are useful for controlled proof-of-concept testing because they are usually reversible.

---

# CSRF in Support Systems

Potential actions include:

```text
Create ticket
Close ticket
Change ticket email
Add note
Change notification settings
Upload attachment
```

Assess impact rather than reporting every state-changing request equally.

---

# CSRF in CMS Platforms

High-value CMS actions include:

```text
Create page
Publish page
Delete page
Change administrator
Install plugin
Change theme
Modify settings
Change integration
```

Administrative CSRF can have severe impact.

---

# CSRF in OAuth Flows

OAuth-related CSRF requires careful analysis.

A common security mechanism is:

```text
state
```

The OAuth client generates a value and verifies that the callback contains the expected value.

Conceptually:

```text
Client Starts OAuth
      ↓
Generate state
      ↓
Authorization Server
      ↓
Callback with state
      ↓
Client Verifies state
```

This helps protect the OAuth flow against CSRF and flow confusion.

---

# OAuth State Testing

When reviewing OAuth:

```text
Is state present?

Is state unpredictable?

Is state validated?

Is state bound to the initiating browser session?

Can state be omitted?

Can another session's state be reused?
```

OAuth deserves its own detailed testing methodology, but these checks are directly relevant to CSRF.

---

# CSRF and Open Redirect

Open redirects can sometimes interact with:

```text
OAuth
SSO
Origin trust
Referer-based logic
```

Do not automatically combine vulnerabilities.

Trace the actual request and trust decisions.

---

# CSRF in SSO

SSO flows may involve:

```text
SAML
OAuth
OpenID Connect
Custom federation
```

Potential CSRF-like issues can occur around:

```text
Login initiation
Account linking
Identity binding
Logout
Callback processing
```

Account-linking endpoints deserve particular attention because an attacker may attempt to bind their identity to the victim's authenticated account.

---

# Account Linking CSRF

Consider:

```text
Victim logged into target.example
        ↓
Attacker controls external identity
        ↓
Victim receives forged account-link request
        ↓
External identity becomes linked
```

If successful, the attacker may later authenticate using the linked identity.

This can have account takeover impact.

---

# CSRF and WebSockets

WebSocket handshakes begin as HTTP requests and browsers can initiate cross-origin WebSocket connections.

Applications should validate:

```text
Origin
Authentication
Authorisation
```

Cross-Site WebSocket Hijacking is related to CSRF concepts but is generally treated as a separate vulnerability class.

---

# CSRF and GraphQL

GraphQL does not inherently prevent CSRF.

Suppose the application uses:

```text
Cookie authentication
```

and accepts GraphQL mutations through form-compatible requests.

Then mutations may still be CSRF-relevant.

Interesting operations include:

```text
updateProfile
changeEmail
changePassword
createUser
deleteUser
updateSettings
```

---

# GraphQL GET Requests

Some GraphQL implementations allow queries through GET.

Mutations should generally not be accepted through GET.

If state-changing GraphQL operations can be triggered through a top-level navigation, SameSite protections may behave differently.

---

# CSRF and Content-Type

For GraphQL and JSON APIs, determine whether the endpoint accepts:

```text
application/json
application/graphql
application/x-www-form-urlencoded
text/plain
```

Strict content-type validation can reduce the set of browser-generated cross-origin requests that reach the application.

---

# CSRF and Fetch Metadata

Modern browsers can send Fetch Metadata headers such as:

```http
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-Dest
```

For example:

```http
Sec-Fetch-Site: cross-site
```

Applications can use these headers as an additional defence.

---

# Sec-Fetch-Site

Possible values include:

```text
same-origin
same-site
cross-site
none
```

A sensitive endpoint can potentially reject inappropriate:

```text
cross-site
```

requests.

This should be considered defence in depth rather than the only security mechanism.

---

# Fetch Metadata Policy

Conceptually:

```text
Request
   ↓
Sec-Fetch-Site
   ↓
Cross-Site?
   ↓
Sensitive Endpoint?
   ↓
Reject
```

This can significantly reduce cross-site request abuse when implemented carefully.

---

# Testing Fetch Metadata

Capture a legitimate browser request.

Look for:

```text
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-Dest
```

Then test the actual browser-based cross-site PoC.

Do not simply modify these headers manually and assume a browser attacker can do the same.

Browsers control Fetch Metadata headers.

---

# Browser-Accurate Testing

This is an important principle for CSRF.

Repeater tells you:

```text
What the server accepts
```

but the browser tells you:

```text
What an attacker can actually cause
```

Therefore final CSRF validation should use a browser-based proof of concept.

---

# Repeater vs Browser

Use Repeater for:

```text
Token validation
Origin validation
Referer validation
Parameter behaviour
Content-type behaviour
```

Use a browser for:

```text
SameSite behaviour
Automatic cookies
Form restrictions
Cross-origin behaviour
Redirect behaviour
Actual exploitability
```

Both are necessary.

---

# Testing With Two Browser Sessions

A useful setup is:

```text
Browser Profile A
Victim Test Account

Browser Profile B
Attacker / Secondary Test Account
```

This helps with:

```text
Token binding
Login CSRF
Account linking
Cross-account testing
```

Use isolated profiles to avoid session confusion.

---

# Incognito / Private Windows

Private browsing can help isolate sessions, but be aware that browsers may share some state differently depending on configuration.

Separate browser profiles provide clearer isolation when testing multiple identities.

---

# Hosting the PoC Locally

A CSRF proof of concept can be hosted from a local test server.

For example:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://127.0.0.1:8000/
```

with the victim test browser.

The target application should remain the authorised system being assessed.

---

# Burp's Built-In PoC

Burp's CSRF PoC generator can save time for form-compatible requests.

However, always review the generated HTML.

Check:

```text
Target URL
Method
Parameter names
Parameter values
Encoding
Automatic submission
```

Do not treat generated output as proof until it works in a real browser.

---

# CSRF Token Leakage

Even a correctly implemented CSRF token may fail if the token leaks to an attacker.

Potential leakage locations include:

```text
URLs
Referer headers
Logs
Third-party resources
Analytics
Error messages
Browser history
External links
```

Tokens should not normally be placed in URLs.

---

# Token in URL

Avoid:

```text
https://target.example/action?csrf=SECRET
```

URLs may appear in:

```text
Browser history
Server logs
Proxy logs
Referer headers
Monitoring
Analytics
```

Prefer request bodies or custom headers.

---

# CSRF Token Entropy

Tokens should be:

```text
Unpredictable
Generated using cryptographically secure randomness
Sufficiently long
```

Predictable values such as:

```text
Username
Timestamp
Sequential ID
User ID
MD5(user ID)
```

should not be used as standalone CSRF tokens.

---

# Token Comparison

Token validation should use appropriate secure comparison logic.

The primary issue in most CSRF testing is whether the token is:

```text
Required
Valid
Bound correctly
Unpredictable
```

Do not over-focus on theoretical comparison timing unless the application context makes it realistically relevant.

---

# CSRF Token Rotation

Tokens may be:

```text
Per session
Per request
Per form
```

All can potentially be valid designs.

Per-request rotation is not mandatory for effective CSRF protection.

Correct validation and binding matter more.

---

# Token Expiration

CSRF tokens should generally not remain valid indefinitely beyond the relevant session or security context.

When the session ends:

```text
Associated CSRF protection should no longer remain useful.
```

---

# Session Rotation

After:

```text
Login
Privilege elevation
Password change
Security-sensitive authentication event
```

the application may rotate the session.

Review whether CSRF tokens remain correctly associated with the new session.

---

# SameSite Is Defence in Depth

Do not rely exclusively on:

```text
SameSite
```

for high-value state-changing operations.

Browser behaviour evolves and application architecture may include:

```text
Sibling subdomains
SSO
Cross-site integrations
Legacy clients
Embedded content
```

A robust design combines:

```text
CSRF token
Origin validation
SameSite cookies
Correct HTTP methods
Reauthentication where appropriate
```

---

# CSRF Protection Matrix

Document protections clearly.

| Protection | Present | Effective |
|---|---|---|
| CSRF token | Yes / No | Yes / No |
| Token required | Yes / No | Yes / No |
| Token validated | Yes / No | Yes / No |
| Session-bound | Yes / No | Yes / No |
| SameSite cookie | Strict / Lax / None / Missing | |
| Origin validation | Yes / No | Yes / No |
| Referer validation | Yes / No | Yes / No |
| Custom header | Yes / No | Yes / No |
| Reauthentication | Yes / No | Yes / No |
| Fetch Metadata | Yes / No | Yes / No |

---

# Common CSRF Testing Mistakes

Do not assume:

```text
POST = protected
```

Do not assume:

```text
JSON = protected
```

Do not assume:

```text
CORS = CSRF protection
```

Do not assume:

```text
SameSite = impossible to exploit
```

Do not assume:

```text
Token present = token validated
```

Do not assume:

```text
Confirmation page = CSRF protection
```

Test the actual browser behaviour.

---

# False Positives

A request that succeeds in Repeater after removing the CSRF token does not automatically prove exploitable CSRF.

Why?

Because the browser may not send the required authentication cookie cross-site due to:

```text
SameSite
```

or the attacker may not be able to reproduce the required request format.

Therefore:

```text
Server accepts tokenless request
```

is evidence of weak token validation.

But final exploitability should account for:

```text
Browser behaviour
Cookie behaviour
Request format
Origin restrictions
```

---

# Browser Validation Checklist

Before reporting exploitable CSRF, determine:

```text
Can the PoC be loaded from another origin?

Does the browser submit the request?

Is the authentication cookie included?

Does the server accept the request?

Does the application state actually change?
```

This produces much stronger evidence.

---

# CSRF Through GET Example

Request:

```http
GET /profile/set-email?email=csrf-test@example.com HTTP/1.1
Host: target.example
Cookie: session=REDACTED
```

Controlled PoC:

```html
<!doctype html>
<html>
  <body>
    <img
      src="https://target.example/profile/set-email?email=csrf-test@example.com"
      alt="">
  </body>
</html>
```

If the victim's authenticated browser loads the image and the application changes the email address, the action is CSRF-vulnerable.

---

# CSRF Through POST Example

Request:

```http
POST /profile/set-email HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

email=csrf-test@example.com
```

Controlled PoC:

```html
<!doctype html>
<html>
  <body>

    <form id="csrf"
          action="https://target.example/profile/set-email"
          method="POST">

      <input type="hidden"
             name="email"
             value="csrf-test@example.com">

    </form>

    <script>
      document.getElementById("csrf").submit();
    </script>

  </body>
</html>
```

---

# Multi-Parameter Requests

Suppose:

```http
POST /profile HTTP/1.1
Content-Type: application/x-www-form-urlencoded

firstName=Asif&lastName=Minhas&email=csrf-test@example.com
```

The PoC must reproduce all parameters required by the server.

For example:

```html
<form action="https://target.example/profile" method="POST">
  <input type="hidden" name="firstName" value="Asif">
  <input type="hidden" name="lastName" value="Minhas">
  <input type="hidden" name="email" value="csrf-test@example.com">
</form>
```

Determine which parameters are actually required.

---

# Duplicate Parameters

Applications may behave unexpectedly with duplicate parameters:

```text
csrf=valid&csrf=invalid
```

Different layers may select:

```text
First value
Last value
All values
```

This can create validation inconsistencies.

Test duplicate parameters only when there is evidence that different components may parse the request differently.

---

# CSRF and Parameter Pollution

HTTP Parameter Pollution can interact with CSRF validation when:

```text
Security middleware
```

and:

```text
Application logic
```

interpret duplicate parameters differently.

Conceptually:

```text
Request
 ↓
CSRF Middleware reads first csrf
 ↓
Application reads second csrf
```

This is implementation-specific.

---

# Method Validation

Ensure the server correctly restricts HTTP methods.

If:

```text
POST /account/email
```

is expected, test whether:

```text
GET
```

unexpectedly performs the same action.

Likewise, test whether alternate form-compatible methods or method overrides reach the same functionality.

---

# CSRF in Mobile APIs

Native mobile applications often use bearer tokens rather than browser-managed cookies.

Traditional CSRF may therefore be less applicable.

However, if the same API is also consumed by a browser using cookies, assess the browser threat model separately.

---

# CSRF in SPAs

Single Page Applications often use:

```text
Cookie-based sessions
+
JSON APIs
```

Do not assume an SPA is immune to CSRF.

Review:

```text
SameSite
CSRF headers
CORS
Content-Type
Origin validation
Authentication model
```

---

# CSRF in Microservices

A browser may interact with several backend services through:

```text
API gateway
Reverse proxy
BFF
```

CSRF protection may exist at one layer but not another.

Trace:

```text
Browser
  ↓
Gateway
  ↓
Application
  ↓
Internal Service
```

Determine where validation occurs.

---

# Reverse Proxy Considerations

Applications behind reverse proxies may incorrectly reconstruct their origin using:

```text
Host
X-Forwarded-Host
Forwarded
X-Forwarded-Proto
```

This can affect Origin or Referer validation.

Origin validation should use trusted proxy configuration rather than blindly trusting attacker-controlled forwarding headers.

---

# Host Header and CSRF

If CSRF protection constructs an expected origin using an attacker-controlled:

```text
Host
```

or:

```text
X-Forwarded-Host
```

header, the protection may be weakened.

Conceptually:

```text
Expected Origin
=
"https://" + Host
```

If Host is not trustworthy, origin comparison may become unreliable.

---

# CSRF and Subdomain Takeover

Suppose session cookies are broadly scoped to:

```text
.example.com
```

and a sibling subdomain can be taken over.

The attacker may gain a same-site position that changes:

```text
SameSite behaviour
Cookie interactions
Origin assumptions
```

This demonstrates why subdomain security can affect CSRF threat models.

---

# CSRF and Cookie Injection

Some CSRF defence patterns can become weaker if an attacker can set cookies for the target application's domain.

Potential causes include:

```text
Vulnerable sibling subdomain
HTTP response splitting
Cookie injection
Subdomain compromise
```

This is especially relevant to naive double-submit cookie implementations.

---

# CSRF and Clickjacking

CSRF and clickjacking can both cause unintended user actions, but the mechanisms differ.

CSRF:

```text
Forged request
```

Clickjacking:

```text
Victim is tricked into clicking hidden or disguised UI
```

An action protected from CSRF may still be vulnerable to clickjacking if it relies only on user interaction.

---

# CSRF and User Interaction

Some actions require:

```text
Button click
Confirmation
Password
MFA code
CAPTCHA
```

This may make automated CSRF more difficult.

Determine whether the interaction genuinely requires information unavailable to the attacker.

A simple confirmation button alone may not be sufficient if the entire flow can still be forged.

---

# CAPTCHA

CAPTCHA can make some CSRF attacks more difficult, but it is not designed as a primary CSRF defence.

Use dedicated CSRF controls.

---

# Password Confirmation

Requiring:

```text
Current password
```

can effectively prevent many sensitive CSRF actions because the attacker does not know the victim's password.

This is particularly useful for:

```text
Password change
Email change
MFA changes
Account deletion
```

It should be combined with appropriate CSRF controls.

---

# Source Code Review

When source code is available, identify:

```text
State-changing routes
CSRF middleware
Middleware exclusions
Token generation
Token validation
Origin checks
SameSite configuration
Authentication mechanism
```

---

# Python / Django Source Review

Search for:

```text
csrf_exempt
CsrfViewMiddleware
csrf_protect
```

Example:

```bash
rg -n \
'csrf_exempt|CsrfViewMiddleware|csrf_protect|CSRF_TRUSTED_ORIGINS'
```

Pay particular attention to:

```python
@csrf_exempt
```

on state-changing endpoints.

---

# Flask Source Review

Flask applications may use extensions such as:

```text
Flask-WTF
CSRFProtect
```

Search:

```bash
rg -n \
'CSRFProtect|Flask-WTF|csrf|WTF_CSRF'
```

Review:

```text
Global protection
Blueprint exclusions
Route exclusions
Token validation
```

---

# Spring Security Source Review

Spring Security provides CSRF protection for browser applications.

Search:

```bash
rg -n \
'csrf\(|csrf\.disable|CsrfToken|CookieCsrfTokenRepository'
```

Pay particular attention to patterns conceptually equivalent to:

```text
csrf disabled
```

Determine why it was disabled and whether cookie-authenticated browser endpoints remain exposed.

---

# ASP.NET Source Review

Search for:

```text
ValidateAntiForgeryToken
AutoValidateAntiforgeryToken
Antiforgery
IgnoreAntiforgeryToken
```

Example:

```bash
rg -n \
'ValidateAntiForgeryToken|AutoValidateAntiforgeryToken|Antiforgery|IgnoreAntiforgeryToken'
```

Review exclusions carefully.

---

# Laravel Source Review

Search for:

```text
VerifyCsrfToken
csrf_token
@csrf
```

Example:

```bash
rg -n \
'VerifyCsrfToken|csrf_token|@csrf|X-CSRF-TOKEN'
```

Review the middleware's excluded routes.

---

# Rails Source Review

Search:

```bash
rg -n \
'protect_from_forgery|authenticity_token|skip_forgery_protection'
```

Interesting patterns include:

```text
skip_forgery_protection
```

or controller-specific exclusions.

---

# Express / Node.js Source Review

Node.js applications may use packages or custom middleware for CSRF protection.

Search:

```bash
rg -ni \
'csrf|xsrf|csurf|sameSite|origin|referer'
```

Also review session cookie configuration.

---

# Source-to-Sink Model

CSRF is different from injection vulnerabilities because the primary flow is not simply source-to-sink.

A useful model is:

```text
ATTACKER ORIGIN
      ↓
VICTIM BROWSER
      ↓
AUTOMATIC AUTHENTICATION
      ↓
STATE-CHANGING ENDPOINT
      ↓
MISSING / WEAK REQUEST AUTHENTICITY CHECK
      ↓
ACTION EXECUTED
```

---

# Source Review Questions

For every state-changing route, ask:

```text
How is the user authenticated?

Are credentials browser-managed?

Is a CSRF token required?

Where is the token generated?

How is it validated?

Is it session-bound?

Is Origin validated?

Is Referer used?

What SameSite policy applies?

Can the action use GET?

Which content types are accepted?

Are custom headers required?

Are any routes excluded from middleware?

Does CORS affect the protection?

Does the action require reauthentication?
```

---

# Automated Testing

Automated scanners can help identify missing CSRF protections, but CSRF is highly dependent on browser behaviour and application logic.

Tools may identify:

```text
State-changing form
No visible CSRF token
Missing SameSite
Token inconsistencies
```

However:

```text
No token
```

does not automatically equal exploitable CSRF.

Manual browser validation remains important.

---

# Burp Scanner

Burp Scanner may identify potential CSRF weaknesses.

Use scanner findings as:

```text
Candidate
```

then manually validate:

```text
Authentication
SameSite
Token behaviour
Origin checks
Browser exploitability
State change
```

---

# curl

`curl` is useful for reproducing requests and checking server-side validation.

For example:

```bash
curl -i \
  -X POST \
  -H 'Cookie: session=REDACTED' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'email=csrf-test@example.com' \
  https://target.example/account/email
```

However, `curl` does not reproduce browser SameSite behaviour.

Use it for server testing, not final browser exploitability.

---

# Browser DevTools

Browser DevTools can help inspect:

```text
Cookies
SameSite
Secure
Domain
Path
Requests
Origin
Referer
Redirects
Preflights
```

In Chromium-based browsers:

```text
Application
  ↓
Cookies
```

is particularly useful.

Firefox provides similar functionality through Storage and Network tooling.

---

# Cookie Review

For the session cookie, record:

```text
Name
Domain
Path
Secure
HttpOnly
SameSite
```

Example:

```http
Set-Cookie: session=REDACTED; Path=/; Secure; HttpOnly; SameSite=Lax
```

CSRF analysis should always include the authentication cookie configuration.

---

# Testing Matrix

A practical CSRF testing matrix:

| Test | Purpose |
|---|---|
| Remove token | Determine whether token required |
| Empty token | Identify presence-only validation |
| Invalid token | Test actual validation |
| Other-session token | Test binding |
| Other-user token | Test binding |
| Remove Origin | Test fallback behaviour |
| Change Origin | Test origin validation |
| Remove Referer | Test fallback behaviour |
| Cross-site form | Confirm browser exploitability |
| GET version | Detect unsafe method handling |
| Alternate content type | Test form compatibility |
| Method override | Test alternate request path |
| Real browser PoC | Confirm actual state change |

---

# Evidence Collection

Useful CSRF evidence includes:

```text
Affected action
Affected endpoint
HTTP method
Authentication mechanism
Session cookie SameSite value
Original request
CSRF token behaviour
Origin validation behaviour
Referer validation behaviour
PoC HTML
Victim test account
State before test
State after test
Screenshot
```

---

# Strong CSRF Evidence

Strong evidence demonstrates:

```text
1. Victim is authenticated

2. Victim loads attacker-controlled page

3. Browser automatically submits forged request

4. Browser includes required authentication

5. Application accepts request

6. Application state changes
```

That is much stronger than simply showing:

```text
CSRF token missing
```

---

# Minimal Proof

Use a reversible state change.

Good examples include:

```text
Change display name
Change test email
Change notification preference
Change profile field
```

Avoid using destructive actions when a harmless state change proves the vulnerability.

---

# Example CSRF Finding

```text
Title
Cross-Site Request Forgery in Email Address Change Functionality

Affected Endpoint
POST /account/email

Authentication Required
Yes

Description
The application allows authenticated users to change their account
email address through the /account/email endpoint.

The request relies on the user's session cookie for authentication
but does not require a valid anti-CSRF token or otherwise verify that
the request originated from the legitimate application.

A controlled HTML proof of concept hosted on a separate origin caused
the authenticated test browser to submit the email-change request.
The browser automatically included the victim test account's session
cookie and the application accepted the request.

The email address of the controlled test account was successfully
changed.

Impact
An attacker who can cause an authenticated user to visit an
attacker-controlled page could potentially perform the affected
action using the victim's authenticated session.

For email-change functionality, the impact may be particularly
significant when the email address is used for password recovery or
other account-security processes.

Recommendation
Implement robust anti-CSRF protection for all state-changing
browser-authenticated functionality.

Use framework-provided CSRF protection where available.

CSRF tokens should be unpredictable, validated server-side and
appropriately bound to the user's authenticated session.

Configure authentication cookies with an appropriate SameSite
attribute and validate request Origin information as defence in
depth.

Sensitive account-security changes should additionally require
reauthentication where appropriate.
```

---

# Example Weak Token Finding

```text
Title
Anti-CSRF Token Is Not Validated

Description
The affected state-changing request contains a parameter named csrf.

Testing demonstrated that the request succeeds when the token is:

Missing
Empty
Invalid

The application therefore appears to include an anti-CSRF token in
the request but does not enforce it server-side.

A browser-based proof of concept confirmed that the affected action
can be triggered from another origin using the authenticated test
user's session.

Recommendation
Validate the anti-CSRF token server-side for every protected
state-changing request.

Requests containing missing, malformed or incorrect tokens should be
rejected before the requested action is processed.
```

---

# Example Token Binding Finding

```text
Title
Anti-CSRF Tokens Are Not Bound to User Sessions

Description
The application requires a CSRF token for the affected request.

However, a valid token obtained from controlled test account A was
accepted when submitted together with the authenticated session of
controlled test account B.

This demonstrates that CSRF tokens are not correctly bound to the
user's security context.

Impact
Weak token binding may reduce the effectiveness of the application's
CSRF protection if an attacker can obtain a valid token through
another permitted context.

Recommendation
Cryptographically bind CSRF tokens to the authenticated session or
use the framework's established synchronizer-token implementation.
```

---

# Example GET-Based CSRF Finding

```text
Title
State-Changing Account Action Can Be Triggered Through GET Request

Description
The affected endpoint performs a state-changing account operation
using an HTTP GET request.

Because GET requests can be initiated through ordinary cross-site
navigation and resource loading, the action can be triggered from
another origin when the victim's authentication cookie is included.

A controlled proof of concept demonstrated the issue against a test
account.

Recommendation
Do not perform state-changing operations using GET requests.

Use an appropriate state-changing HTTP method and require robust
anti-CSRF protection.
```

---

# Example Login CSRF Finding

```text
Title
Login Endpoint Is Vulnerable to Cross-Site Request Forgery

Description
The application's login endpoint accepts authentication requests
without validating request authenticity.

A controlled proof of concept caused the victim test browser to log
into an account controlled by the tester.

Impact
A victim may unknowingly interact with the application while logged
into an account controlled by an attacker.

Depending on the application, information subsequently entered by the
victim may become associated with and accessible through the
attacker-controlled account.

Recommendation
Apply CSRF protection to the login flow.

Bind login attempts to a browser-initiated authentication flow and
validate appropriate request authenticity controls.
```

---

# Remediation

CSRF mitigation should use defence in depth.

A robust browser-authenticated application might use:

```text
State-Changing Request
        ↓
Correct HTTP Method
        ↓
CSRF Token
        ↓
Token Validation
        ↓
Session Binding
        ↓
Origin Validation
        ↓
SameSite Cookie
        ↓
Authorisation
        ↓
Sensitive Action?
        ↓
Reauthentication
        ↓
Execute
```

---

# Use Framework Protection

Prefer established framework mechanisms.

Examples include:

```text
Django CSRF middleware
Spring Security CSRF
ASP.NET Anti-Forgery
Laravel CSRF middleware
Rails request forgery protection
Flask-WTF CSRFProtect
```

Avoid creating custom CSRF systems unless necessary.

---

# Protect Every State-Changing Endpoint

Protection should apply consistently to:

```text
POST
PUT
PATCH
DELETE
```

and any legacy state-changing GET requests should be redesigned.

Do not protect only:

```text
HTML forms
```

while leaving:

```text
API endpoints
Administrative routes
Legacy endpoints
```

unprotected.

---

# Use Strong Tokens

Tokens should be:

```text
Cryptographically random
Unpredictable
Validated server-side
Bound to the relevant security context
```

Reject:

```text
Missing
Invalid
Malformed
Unexpected
```

tokens.

---

# Configure SameSite

Use an appropriate SameSite policy for authentication cookies.

Prefer:

```text
SameSite=Lax
```

or:

```text
SameSite=Strict
```

where application requirements permit.

Use:

```text
SameSite=None
```

only where cross-site cookie behaviour is genuinely required and pair it with strong CSRF controls.

---

# Use Secure Cookie Attributes

Authentication cookies should generally use:

```text
Secure
HttpOnly
SameSite
```

and should have the narrowest appropriate:

```text
Domain
Path
```

scope.

---

# Validate Origin

For sensitive state-changing requests, validate:

```text
Origin
```

against an explicit list of trusted origins.

Do not use:

```text
Substring matching
Suffix matching without domain boundaries
Attacker-controlled Host values
```

to make security decisions.

---

# Referer Fallback

Where Origin is unavailable, carefully designed Referer validation may provide additional defence.

Do not automatically trust:

```text
Missing Referer
```

without understanding the resulting security implications.

---

# Fetch Metadata

Consider using:

```text
Sec-Fetch-Site
```

and related Fetch Metadata headers as additional protection.

For example:

```text
Reject inappropriate cross-site requests
```

to sensitive endpoints.

Do not treat this as the sole CSRF control.

---

# Reauthentication

Require additional authentication for highly sensitive operations.

Examples:

```text
Change password
Change email
Disable MFA
Delete account
Change recovery settings
Create privileged credentials
```

---

# Avoid State Changes Through GET

GET should not perform actions such as:

```text
Delete
Update
Enable
Disable
Transfer
Change
Create
```

Use state-changing HTTP methods.

---

# Strict Content-Type Validation

API endpoints should accept only the content types they actually require.

For example, if the API requires:

```text
application/json
```

reject:

```text
text/plain
application/x-www-form-urlencoded
```

unless explicitly supported.

This can reduce cross-origin form compatibility.

---

# CORS Configuration

Do not use permissive CORS configuration with cookie-authenticated sensitive APIs.

Review:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Allowed methods
Allowed headers
```

CORS should complement rather than replace CSRF protection.

---

# CSRF Testing Checklist

## Discovery

- [ ] Change email
- [ ] Change password
- [ ] Change phone
- [ ] Update profile
- [ ] Change address
- [ ] Add user
- [ ] Delete user
- [ ] Change role
- [ ] Create API key
- [ ] Delete API key
- [ ] Change MFA
- [ ] Disable MFA
- [ ] Account deletion
- [ ] Administrative actions
- [ ] Webhook configuration
- [ ] Integration configuration
- [ ] SSO configuration
- [ ] Account linking
- [ ] Login
- [ ] Logout

## Request Analysis

- [ ] HTTP method
- [ ] Authentication mechanism
- [ ] Session cookie
- [ ] SameSite
- [ ] CSRF token
- [ ] Origin
- [ ] Referer
- [ ] Content-Type
- [ ] Custom headers
- [ ] Fetch Metadata

## Token Testing

- [ ] Remove token
- [ ] Empty token
- [ ] Invalid token
- [ ] Malformed token
- [ ] Other-session token
- [ ] Other-user token
- [ ] Token reuse
- [ ] Token predictability
- [ ] Token in URL
- [ ] Token leakage

## Cookie Testing

- [ ] Secure
- [ ] HttpOnly
- [ ] SameSite
- [ ] Domain
- [ ] Path
- [ ] Host-only vs domain cookie
- [ ] Sibling subdomain considerations

## Origin Validation

- [ ] Correct Origin
- [ ] Missing Origin
- [ ] Untrusted Origin
- [ ] Origin parsing
- [ ] Exact matching
- [ ] Trusted origin list
- [ ] Proxy header handling

## Referer Validation

- [ ] Correct Referer
- [ ] Missing Referer
- [ ] Untrusted Referer
- [ ] Parsing
- [ ] Fallback behaviour

## Request Format

- [ ] GET
- [ ] POST
- [ ] PUT
- [ ] PATCH
- [ ] DELETE
- [ ] Method override
- [ ] application/x-www-form-urlencoded
- [ ] multipart/form-data
- [ ] text/plain
- [ ] application/json
- [ ] Alternate content types

## API

- [ ] Cookie authentication
- [ ] Bearer authentication
- [ ] JSON endpoints
- [ ] CORS
- [ ] Credentialed CORS
- [ ] Custom headers
- [ ] GraphQL
- [ ] REST
- [ ] Method overrides

## Sensitive Workflows

- [ ] Password change
- [ ] Email change
- [ ] MFA changes
- [ ] Recovery settings
- [ ] API credentials
- [ ] Administrative users
- [ ] Account linking
- [ ] OAuth
- [ ] SSO
- [ ] Multi-step actions

## Burp

- [ ] Proxy
- [ ] HTTP History
- [ ] Repeater
- [ ] Generate CSRF PoC
- [ ] Review generated HTML
- [ ] Test in browser
- [ ] Confirm state change

## Browser

- [ ] Separate test session
- [ ] PoC hosted on separate origin
- [ ] Cookie included?
- [ ] SameSite behaviour
- [ ] Request sent?
- [ ] State changed?
- [ ] DevTools reviewed

## Source Review

- [ ] CSRF middleware
- [ ] Middleware exclusions
- [ ] State-changing routes
- [ ] Token generation
- [ ] Token validation
- [ ] Session binding
- [ ] Origin validation
- [ ] Referer validation
- [ ] SameSite configuration
- [ ] CORS configuration
- [ ] Reauthentication

## Validation

- [ ] Reproduce with controlled account
- [ ] Use reversible action
- [ ] Confirm real browser behaviour
- [ ] Confirm authentication automatically included
- [ ] Confirm state actually changes
- [ ] Determine required victim interaction
- [ ] Avoid affecting real users
- [ ] Stop after sufficient evidence

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | Primary manual CSRF testing |
| Burp Proxy | Capture state-changing requests |
| Burp Repeater | Token and header testing |
| Burp CSRF PoC Generator | Generate controlled PoCs |
| Browser DevTools | Cookie and browser behaviour analysis |
| curl | Server-side validation testing |
| ripgrep | Source-code review |
| Semgrep | Structured source analysis |

---

# Tool Selection

| Situation | Tool |
|---|---|
| Find actions | Burp Proxy |
| Test token | Burp Repeater |
| Test Origin | Burp Repeater |
| Generate PoC | Burp CSRF PoC Generator |
| Verify SameSite | Browser |
| Confirm exploitability | Browser |
| Inspect cookies | Browser DevTools |
| Reproduce server request | curl |
| Review source | ripgrep / Semgrep |

---

# Quick Reference

```text
High-Value Actions:

Change Email
Change Password
Change MFA
Change Recovery Settings
Add Administrator
Change Role
Create API Key
Account Linking
Delete Account
SSO Configuration
```

```text
First Token Tests:

Valid
  ↓
Missing
  ↓
Empty
  ↓
Invalid
  ↓
Other Session
  ↓
Other User
```

```text
Browser Controls:

SameSite
Origin
Referer
CORS
Fetch Metadata
```

```text
Request Formats:

GET
POST Form
Multipart Form
text/plain
JSON
Method Override
```

```text
Core Question:

Can another origin cause
the authenticated browser
to perform this action?
```

---

# Practical Workflow Summary

```text
              ┌────────────────────────────┐
              │ Find State-Changing Action │
              └──────────────┬─────────────┘
                             │
                             ▼
              ┌────────────────────────────┐
              │ Capture Legitimate Request │
              └──────────────┬─────────────┘
                             │
                             ▼
              ┌────────────────────────────┐
              │ Identify Authentication    │
              └──────────────┬─────────────┘
                             │
                             ▼
              ┌────────────────────────────┐
              │ CSRF Token Present?        │
              └──────────────┬─────────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
          ┌────────────────┐  ┌─────────────────┐
          │ Yes            │  │ No              │
          │ Test Token     │  │ Review Other    │
          │ Validation     │  │ Defences        │
          └───────┬────────┘  └────────┬────────┘
                  │                    │
                  └─────────┬──────────┘
                            │
                            ▼
              ┌────────────────────────────┐
              │ Review SameSite Cookie     │
              └──────────────┬─────────────┘
                             │
                             ▼
              ┌────────────────────────────┐
              │ Origin / Referer Checks    │
              └──────────────┬─────────────┘
                             │
                             ▼
              ┌────────────────────────────┐
              │ Can Browser Reproduce It?  │
              └──────────────┬─────────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
          ┌────────────────┐  ┌─────────────────┐
          │ No             │  │ Yes             │
          │ Document       │  │ Build PoC       │
          │ Defence        │  └────────┬────────┘
          └────────────────┘           │
                                       ▼
                             ┌─────────────────────┐
                             │ Controlled Browser  │
                             │ Test                │
                             └──────────┬──────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │ State Changed?      │
                             └──────────┬──────────┘
                                        │
                              ┌─────────┴─────────┐
                              │                   │
                              ▼                   ▼
                     ┌────────────────┐  ┌────────────────┐
                     │ No             │  │ Yes            │
                     │ Reassess       │  │ CSRF Confirmed │
                     └────────────────┘  └───────┬────────┘
                                                 │
                                                 ▼
                                        ┌────────────────┐
                                        │ Report         │
                                        └────────────────┘
```

---

# CSRF Security Model

```text
                         ATTACKER
                            │
                            ▼
                   ┌─────────────────┐
                   │ Attacker Origin │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Victim Browser  │
                   └────────┬────────┘
                            │
                Browser automatically
                attaches authentication
                            │
                            ▼
                   ┌─────────────────┐
                   │ Target App      │
                   └────────┬────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ Request Authenticity    │
              │ Validation              │
              └────────────┬────────────┘
                           │
               ┌───────────┴───────────┐
               │                       │
               ▼                       ▼
      ┌─────────────────┐     ┌─────────────────┐
      │ Valid           │     │ Invalid         │
      │ Process Request │     │ Reject Request  │
      └─────────────────┘     └─────────────────┘
```

---

# Defence-in-Depth Model

```text
STATE-CHANGING REQUEST
          ↓
CORRECT HTTP METHOD
          ↓
CSRF TOKEN
          ↓
TOKEN VALIDATION
          ↓
SESSION BINDING
          ↓
ORIGIN VALIDATION
          ↓
SAMESITE COOKIE
          ↓
FETCH METADATA
          ↓
AUTHORISATION
          ↓
REAUTHENTICATION
WHEN APPROPRIATE
          ↓
EXECUTE ACTION
```

---

# References

## PortSwigger Web Security Academy

### Cross-Site Request Forgery

https://portswigger.net/web-security/csrf

One of the primary practical references for CSRF testing.

PortSwigger covers:

```text
CSRF methodology
CSRF tokens
Token validation weaknesses
SameSite cookies
Referer-based defences
Browser behaviour
```

---

## PortSwigger

### Bypassing CSRF Token Validation

https://portswigger.net/web-security/csrf/bypassing-token-validation

Useful for understanding common implementation mistakes involving anti-CSRF tokens.

---

## PortSwigger

### Bypassing SameSite Cookie Restrictions

https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions

Useful for understanding:

```text
Site vs origin
SameSite Strict
SameSite Lax
Sibling domains
Browser behaviour
```

---

## PortSwigger

### Bypassing Referer-Based CSRF Defences

https://portswigger.net/web-security/csrf/bypassing-referer-based-defenses

Useful for understanding weaknesses in Referer-based request validation.

---

## OWASP Cross-Site Request Forgery Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

This should be the primary defensive reference for this page.

OWASP covers:

```text
Synchronizer tokens
Double-submit cookies
Signed tokens
SameSite
Origin verification
Custom headers
Fetch Metadata
User interaction
```

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

Useful for broader web application security testing methodology.

---

## OWASP SameSite Cookie Attribute

https://owasp.org/www-community/SameSite

Useful for understanding SameSite as part of browser cookie security.

---

## MDN SameSite

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie

Useful reference for browser cookie behaviour and the `SameSite` attribute.

---

## MDN Origin

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin

Useful for understanding the HTTP `Origin` request header.

---

## MDN Referer

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referer

Useful for understanding Referer behaviour.

---

## MDN Fetch Metadata

https://developer.mozilla.org/en-US/docs/Glossary/Fetch_metadata_request_header

Useful for:

```text
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-User
Sec-Fetch-Dest
```

---

## PayloadsAllTheThings

### CSRF Injection

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/CSRF%20Injection

Useful as a practical supplementary reference for CSRF testing.

---

## HackTricks

### CSRF

https://book.hacktricks.wiki/en/pentesting-web/csrf-cross-site-request-forgery.html

Useful as a practical supplementary CSRF reference.

---

# Related Notes

```text
Web Application Security
├── Methodology
├── Pentesting Checklist
├── Reconnaissance
│   ├── Subdomain Enumeration
│   ├── Technology Identification
│   ├── Content Discovery
│   ├── Parameter Discovery
│   └── JavaScript Analysis
├── Authentication
├── Authorisation
├── Session Management
├── Burp Suite
│   ├── Extensions
│   └── Testing Workflows
├── Cross-Site Scripting
├── SQL Injection
├── OS Command Injection
├── Server-Side Request Forgery
├── Server-Side Template Injection
├── Cross-Site Request Forgery
├── XML External Entity Injection
├── Path Traversal
├── File Inclusion
└── File Upload
```

CSRF connects particularly strongly with:

```text
Authentication
      ↓
Session Cookie
      ↓
CSRF
```

```text
Session Management
       ↓
SameSite
       ↓
Cross-Site Cookie Behaviour
```

```text
CSRF
 ↓
State-Changing Request
 ↓
Authorisation
```

```text
XSS
 ↓
Same-Origin JavaScript
 ↓
Potential CSRF Defence Bypass
```

```text
CORS
 ↓
Cross-Origin Request Rules
 ↓
API CSRF Analysis
```

```text
Subdomain Security
       ↓
Same-Site Trust
       ↓
CSRF Threat Model
```

---

# Final Testing Principle

Do not reduce CSRF testing to:

```text
There is no CSRF token.
```

A missing token is only one part of the analysis.

Instead ask:

```text
What action changes state?
        ↓
How is the victim authenticated?
        ↓
Does the browser attach those credentials automatically?
        ↓
Is a CSRF token present?
        ↓
Is the token actually required?
        ↓
Is it validated?
        ↓
Is it bound to the correct session?
        ↓
What SameSite policy applies?
        ↓
Is Origin validated?
        ↓
Is Referer validated?
        ↓
Can an ordinary cross-origin form reproduce the request?
        ↓
Does the endpoint accept alternative content types?
        ↓
Can GET or method overrides trigger the action?
        ↓
Does CORS change the threat model?
        ↓
Can a real browser PoC send the authenticated request?
        ↓
Does the application state actually change?
        ↓
What is the minimum reversible proof required?
```

The complete CSRF chain is:

```text
ATTACKER-CONTROLLED ORIGIN
          ↓
VICTIM VISITS PAGE
          ↓
BROWSER GENERATES REQUEST
          ↓
AUTHENTICATION AUTOMATICALLY ATTACHED
          ↓
TARGET APPLICATION
          ↓
MISSING / INEFFECTIVE REQUEST
AUTHENTICITY VALIDATION
          ↓
AUTHORISED USER ACTION EXECUTED
          ↓
SECURITY IMPACT
```

The secure model is:

```text
CROSS-SITE REQUEST
        ↓
SAMESITE / BROWSER CONTROLS
        ↓
CSRF TOKEN
        ↓
ORIGIN VALIDATION
        ↓
AUTHORISATION
        ↓
REAUTHENTICATION
WHEN REQUIRED
        ↓
STATE CHANGE
```

The key question throughout the assessment is:

> Can an attacker-controlled origin cause an authenticated victim's browser to perform a state-changing action that the victim did not intend?

That is the model to use when assessing Cross-Site Request Forgery.
