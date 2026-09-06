---
title: Authentication and Session Testing Cheatsheet
description: Practical authentication and session security cheatsheet for authorised web application testing covering login, enumeration, password policy, MFA, password reset, session management, cookies, fixation, logout, concurrent sessions, remember-me functionality, source review, evidence, remediation and retesting.
---

# Authentication and Session Testing Cheatsheet

Authentication answers:

```text
Who are you?
```

Session management answers:

```text
How does the application maintain that authenticated identity
across multiple requests?
```

A simplified authentication flow is:

```text
Credentials
    |
    v
Authentication Endpoint
    |
    v
Identity Verification
    |
    v
Session Created
    |
    v
Session Identifier
    |
    v
Authenticated Requests
```

Security testing should evaluate the complete lifecycle rather than testing only the login form.

```text
Registration
     |
     v
Login
     |
     v
MFA
     |
     v
Session Creation
     |
     v
Session Use
     |
     v
Privilege Change
     |
     v
Password Change
     |
     v
Logout
     |
     v
Session Invalidation
     |
     v
Account Recovery
```

!!! warning "Authorised Security Testing"

    Perform authentication and session testing only against systems and accounts explicitly included in the assessment scope. Password spraying, brute-force testing, MFA testing and account lockout testing can affect real users and availability. Use dedicated test accounts and agreed request rates whenever possible.


# Testing Model

Do not reduce authentication testing to:

```text
Can I guess the password?
```

Use:

```text
Identity Claim
     |
     v
Authentication
     |
     v
MFA
     |
     v
Session Creation
     |
     v
Session Integrity
     |
     v
Authorization
     |
     v
Session Termination
     |
     v
Recovery
```


# Authentication Attack Surface

Identify every authentication-related endpoint.

Typical functionality includes:

```text
Login

Registration

Logout

Password reset

Forgot password

Password change

Email change

Username change

MFA enrolment

MFA verification

MFA recovery

Backup codes

Remember me

Account activation

Email verification

Magic links

SSO

OAuth/OIDC login

SAML login

API authentication

Mobile authentication

Device registration

Session management

Account deletion
```


# Endpoint Inventory

Create a table during testing.

| Function | Endpoint | Method | Authentication |
|---|---|---|---|
| Login | `/login` | POST | None |
| Logout | `/logout` | POST | Required |
| Forgot password | `/forgot-password` | POST | None |
| Reset password | `/reset-password` | POST | Token |
| Change password | `/account/password` | POST | Required |
| MFA verify | `/mfa/verify` | POST | Partial |
| Sessions | `/account/sessions` | GET | Required |


# Establish Test Accounts

Where possible, use at least:

```text
Account A

Account B
```

If role testing is required:

```text
Normal User A

Normal User B

Privileged User
```

This becomes especially useful when authentication testing transitions into authorization testing.


# Authentication Baseline

Capture a legitimate login.

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=testuser&password=CorrectPassword123!
```


# Record

Capture:

```text
Request

Response

Status code

Response length

Redirect

Cookies

Session token

CSRF token

Authentication headers

MFA transition

Timing
```


# Invalid Password Baseline

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=testuser&password=IncorrectPassword123!
```


# Invalid Username Baseline

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=does-not-exist-7f3a9&password=IncorrectPassword123!
```


# Compare Responses

Compare:

```text
Status code

Response body

Response length

Headers

Redirect

Cookies

Timing
```


# Burp Suite Workflow

```text
Proxy
  |
  v
Capture Login
  |
  v
Send to Repeater
  |
  v
Valid Baseline
  |
  v
Invalid Password
  |
  v
Invalid Username
  |
  v
Compare
  |
  v
Test Controls
  |
  v
Session Lifecycle
  |
  v
Capture Evidence
```


# Burp Repeater

Use Repeater for:

```text
Username enumeration

Password validation

MFA workflow testing

Password reset

Session reuse

Cookie testing

Logout validation

Remember-me testing
```


# Burp Comparer

Comparer is useful when responses appear visually identical.

Compare:

```text
Existing user + wrong password

Non-existing user + wrong password
```


# Burp Intruder

Use Intruder carefully for:

```text
Small controlled username sets

Rate-limit validation

Lockout validation

Response clustering
```

Do not use large credential lists unless explicitly authorised.


# Authentication Response Analysis

A login endpoint may signal success through:

```text
200 response

302 redirect

New cookie

JSON field

JWT

Location header

Different body length

Different application state
```


# JSON Login Example

```http
POST /api/login HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "username": "testuser",
  "password": "CorrectPassword123!"
}
```


# Possible Response

```json
{
  "authenticated": true
}
```


# Authentication Failure

```json
{
  "authenticated": false,
  "message": "Invalid credentials"
}
```


# Username Enumeration

Username enumeration occurs when the application reveals whether an account exists.


# Direct Enumeration

Existing account:

```text
Incorrect password.
```

Non-existing account:

```text
User does not exist.
```


# Better Behaviour

```text
Invalid username or password.
```


# Enumeration Through Status Codes

Example:

```text
Existing user:
401 Unauthorized

Unknown user:
404 Not Found
```


# Enumeration Through Response Length

Example:

```text
Existing user:
Content-Length: 1248

Unknown user:
Content-Length: 1193
```


# Enumeration Through Timing

Potential flow:

```text
Known User
   |
   v
Password Hash Verification
   |
   v
Response
```

versus:

```text
Unknown User
   |
   v
Immediate Reject
```


# Timing Test

Timing differences require careful statistical interpretation.

Do not conclude:

```text
Username enumeration
```

from one slow request.


# Timing Noise

Consider:

```text
Network latency

Load balancing

Caching

Database load

Rate limiting

WAF processing

Application load
```


# Registration Enumeration

Registration may reveal existing users.

Example:

```text
An account already exists for this email.
```


# Password Reset Enumeration

Forgot-password functionality may reveal account existence.

Example:

```text
Reset email sent.
```

versus:

```text
No account exists.
```


# Preferred Response

```text
If an account exists for that address,
password reset instructions will be sent.
```


# Enumeration Through Side Effects

Even when the response is generic, test whether observable side effects differ.

Examples:

```text
Email received

SMS received

Different response timing

Different rate-limit behaviour
```


# Password Policy

Review:

```text
Minimum length

Maximum length

Character requirements

Password reuse

Common password blocking

Breached password checks

Password history

Unicode handling

Whitespace handling
```


# Long Password Support

Applications should permit reasonably long passwords.

Test using a dedicated account.

Examples:

```text
64 characters

100 characters
```

Do not submit extremely large passwords solely to consume resources.


# Password Truncation

Check whether:

```text
Password123456789ABC
```

and:

```text
Password123456789XYZ
```

behave unexpectedly as equivalent due to truncation.


# Important

Only perform truncation tests on dedicated test accounts where changing passwords is safe.


# Password Normalisation

Potential differences include:

```text
Leading spaces

Trailing spaces

Unicode normalisation

Case handling
```


# Password Change

Review the password-change workflow.

Ask:

```text
Is current password required?

Is MFA required?

Is the new password validated?

Are existing sessions invalidated?

Are remembered devices invalidated?

Is the user notified?
```


# Password Change Request

Example:

```http
POST /account/password HTTP/1.1
Host: target.example
Cookie: session=...
Content-Type: application/json

{
  "current_password": "CurrentPassword123!",
  "new_password": "NewPassword456!"
}
```


# Test Current Password Requirement

Do not assume that being authenticated is sufficient for sensitive account changes.


# Sensitive Actions

Consider re-authentication for:

```text
Password change

Email change

MFA disablement

Recovery configuration

Payment details

API key generation

Account deletion
```


# Password Reset Workflow

Typical flow:

```text
Email Address
     |
     v
Reset Request
     |
     v
Random Token
     |
     v
Email
     |
     v
Reset Endpoint
     |
     v
New Password
```


# Password Reset Testing

Review:

```text
Account enumeration

Token randomness

Token length

Token lifetime

Single use

User binding

Session invalidation

Host header handling

Rate limiting

Token leakage

Referer leakage

Password policy
```


# Reset Token Properties

A reset token should be:

```text
Cryptographically random

Sufficiently long

Single-use

Time-limited

Bound to the correct account
```


# Reset Token Replay

After successfully using a reset token:

```text
Use Token
   |
   v
Password Changed
   |
   v
Replay Same Token
```

Expected:

```text
Rejected
```


# Reset Token Expiry

Verify expired tokens cannot be reused.


# Reset Token Account Binding

A token generated for:

```text
Account A
```

must not reset:

```text
Account B
```


# Do Not Brute Force Reset Tokens

Token quality can often be assessed through:

```text
Length

Format

Source review

Multiple generated samples

Randomness design
```

without brute-force attempts.


# Password Reset Host Handling

Applications sometimes construct reset links using request-derived host information.

Conceptually:

```text
Host Header
    |
    v
Reset URL Generator
    |
    v
Email
```


# Review

Determine whether reset links use:

```text
Trusted configured origin
```

rather than blindly trusting request headers.


# Password Reset Token Leakage

Review whether reset tokens appear in:

```text
Referer headers

Analytics requests

Third-party scripts

Logs

Browser history

Error messages
```


# Reset Page Resources

A reset page loading third-party content may unintentionally expose sensitive URL data through browser behaviour depending on how the token is transported.


# Prefer

Sensitive tokens should not remain unnecessarily in URLs after use.


# Email Change

Email addresses often participate in account recovery.

Review:

```text
Current password required?

MFA required?

Old address notified?

New address verified?

Existing sessions affected?
```


# Email Change Risk

If an attacker with a stolen session can change:

```text
Email
```

and then:

```text
Reset password
```

the session compromise may become persistent account takeover.


# MFA Testing

MFA should strengthen authentication rather than merely add another UI page.


# MFA Flow

```text
Username + Password
        |
        v
Primary Authentication
        |
        v
Partial Session
        |
        v
MFA Verification
        |
        v
Fully Authenticated Session
```


# Critical Question

Can the partially authenticated session access endpoints intended only for fully authenticated users?


# MFA Bypass Through Direct Navigation

After password validation but before MFA completion, request:

```text
/account

/dashboard

/api/me

/admin
```

as appropriate to the account's expected authorization.


# Expected

```text
MFA required
```

until verification completes.


# MFA State

Avoid relying only on:

```text
Browser page flow
```

Enforcement must occur server-side.


# MFA Code Reuse

After successful verification:

```text
Code Used
   |
   v
Replay Code
```

Expected behaviour depends on the MFA mechanism, but one-time codes should not remain valid outside their intended window/use model.


# TOTP

Review:

```text
Time window

Replay handling

Rate limiting

Recovery process

Secret storage
```


# Do Not Exhaustively Guess OTPs

Use a dedicated account and a very small number of agreed requests to evaluate controls.


# MFA Rate Limiting

Test whether repeated incorrect codes trigger:

```text
Delay

Temporary block

Challenge reset

Additional verification
```


# MFA Reset

Often more important than MFA itself.

Review:

```text
Who can reset MFA?

What proof is required?

Can support bypass MFA?

Can email alone disable MFA?

Are users notified?
```


# Backup Codes

Review:

```text
Randomness

One-time use

Storage

Regeneration

Invalidation

Display behaviour
```


# Backup Code Replay

After using a backup code:

```text
Replay Same Code
```

Expected:

```text
Rejected
```


# MFA Enrolment

Ask:

```text
Does enrolment require current authentication?

Does it require re-authentication?

Can an attacker with a stolen session register their own MFA device?

Is the existing MFA factor required?
```


# MFA Disablement

Sensitive operation:

```text
Disable MFA
```

should normally require strong verification.


# Remember Me

Remember-me functionality often creates long-lived authentication tokens.


# Test

Capture:

```text
Normal session cookie

Remember-me cookie

Expiry

Cookie attributes

Logout behaviour

Password-change behaviour
```


# Expected

A remember-me token should not simply contain:

```text
Username

User ID

Role
```

without strong protection.


# Remember-Me Lifecycle

```text
Login
  |
  v
Long-Lived Token
  |
  v
Browser
  |
  v
Future Authentication
```


# Review

Ask:

```text
Is token random?

Is it revocable?

Does logout revoke it?

Does password change revoke it?

Can users view remembered devices?

Can users revoke all devices?
```


# Session Management

After authentication, the application typically issues a session identifier.

Example:

```http
Set-Cookie: session=RANDOM_VALUE; Secure; HttpOnly; SameSite=Lax
```


# Session Identifier Properties

A good session identifier should be:

```text
Unpredictable

Unique

Sufficiently random

Meaningless to the client

Server-side validated
```


# Session Token Analysis

Do not judge randomness from one token.

Collect several tokens from your own test accounts and compare:

```text
Length

Character set

Structure

Static components

Timestamp patterns

User identifiers
```


# Example

Tokens:

```text
abc001-user42-1700000000

abc002-user42-1700000010

abc003-user42-1700000020
```

would deserve investigation because they appear structured and potentially predictable.


# Opaque Tokens

Prefer tokens that appear as random opaque identifiers.

However:

```text
Looks random
```

does not prove:

```text
Cryptographically secure
```


# Source Review Can Confirm Generation

Search for session generation logic where source is available.


# Cookie Attributes

Review:

```text
Secure

HttpOnly

SameSite

Path

Domain

Expires

Max-Age
```


# Secure

Example:

```http
Set-Cookie: session=...; Secure
```

Meaning:

```text
Browser should send cookie only over secure transport.
```


# HttpOnly

Example:

```http
Set-Cookie: session=...; HttpOnly
```

Meaning:

```text
Client-side JavaScript cannot normally access the cookie.
```


# Important

`HttpOnly` helps reduce some XSS consequences but does not prevent XSS from making authenticated requests in the victim's browser.


# SameSite

Common values:

```text
Strict

Lax

None
```


# SameSite=None

Modern browsers require:

```text
Secure
```

with:

```text
SameSite=None
```


# SameSite Is Contextual

The correct value depends on application requirements such as:

```text
SSO

Cross-site integrations

Embedded applications
```


# Cookie Domain

Review:

```http
Domain=.example.com
```

Broad cookie scope can expose a session cookie to additional subdomains.


# Prefer Narrow Scope

Use the narrowest appropriate:

```text
Domain

Path
```


# Cookie Path

Example:

```http
Path=/
```

may be necessary, but unnecessary broad scope should be avoided.


# Cookie Expiration

Session cookies may be:

```text
Browser-session cookies

Persistent cookies
```


# Review

Compare:

```text
Application sensitivity

Session lifetime

Idle timeout

Absolute timeout

Remember-me functionality
```


# Session Fixation

Session fixation occurs when an attacker can establish or predict a session identifier that remains valid after the victim authenticates.


# Test Model

```text
Pre-Login Session ID
        |
        v
User Logs In
        |
        v
Post-Login Session ID
```


# Expected

The session identifier should normally rotate after successful authentication.


# Capture Before Login

```http
Cookie: session=PRE_AUTH_VALUE
```


# Capture After Login

```http
Cookie: session=POST_AUTH_VALUE
```


# Compare

Expected:

```text
PRE_AUTH_VALUE != POST_AUTH_VALUE
```


# Session Rotation

Also consider rotation after:

```text
MFA completion

Privilege elevation

Sensitive authentication events
```


# Important

A cookie value remaining the same does not automatically prove exploitable fixation.

Determine:

```text
Can an attacker choose or obtain the pre-authentication value?

Does the server bind authentication to that same value?
```


# Session Upgrade

Some applications use:

```text
Anonymous session
```

before authentication.

That is normal.

The security question is whether authentication creates a new secure session context.


# Session Invalidation

Test:

```text
Logout

Password change

Password reset

MFA reset

Account disablement

Administrative session revocation
```


# Logout Testing

Workflow:

```text
Login
  |
  v
Capture Authenticated Request
  |
  v
Logout
  |
  v
Replay Old Authenticated Request
```


# Expected

```text
Unauthorized / Redirect to Login
```


# Important

Deleting the cookie only in the browser is not sufficient.

Server-side session state should be invalidated where server-side sessions are used.


# Replay After Logout

In Burp Repeater, resend a request captured before logout with the old session identifier.

Expected:

```text
Session rejected
```


# Browser vs Server Logout

Weak implementation:

```text
Logout
  |
  v
Browser Deletes Cookie
```

but:

```text
Server Session Remains Valid
```


# Stronger Model

```text
Logout
  |
  +--> Browser Removes Token
  |
  +--> Server Revokes Session
```


# Password Change Session Behaviour

After password change, determine whether existing sessions remain active.


# Security Decision

Applications may choose different policies based on risk.

High-risk applications often invalidate:

```text
Other sessions

Remember-me tokens

Recovery sessions
```


# Password Reset Session Behaviour

Password reset should generally trigger consideration of active-session invalidation because the reset may have occurred after suspected credential compromise.


# Session Timeout

Test:

```text
Idle timeout

Absolute timeout
```


# Idle Timeout

```text
Last Activity
     |
     v
Idle Period
     |
     v
Session Invalidated
```


# Absolute Timeout

```text
Session Created
     |
     v
Maximum Lifetime
     |
     v
Session Invalidated
```

even if the user remains active.


# Do Not Wait Manually During Every Test

Where source/configuration is available, verify configured timeout values and perform representative dynamic validation.


# Concurrent Sessions

Test whether multiple sessions can exist.

Example:

```text
Browser A -> Session A

Browser B -> Session B
```


# Review

Ask:

```text
Are concurrent sessions intended?

Can users see active sessions?

Can users revoke individual sessions?

Can users revoke all sessions?

Are new-login notifications provided where appropriate?
```


# Session Management Page

Useful functionality may display:

```text
Device

Browser

Approximate location

Created time

Last activity

Revoke button
```


# Session Revocation Test

```text
Session A revokes Session B
        |
        v
Replay Session B
```

Expected:

```text
Rejected
```


# CSRF and Authentication

Authentication endpoints can interact with CSRF.

Potential areas:

```text
Login CSRF

Logout CSRF

Password change

Email change

MFA settings
```


# Login CSRF

Conceptually:

```text
Victim
  |
  v
Forced Login
  |
  v
Attacker's Account
```

This can cause the victim to unknowingly interact with an attacker-controlled account.


# Login CSRF Impact

Potential examples:

```text
Victim enters personal data into attacker's account

Search history saved to attacker's account

Payment information associated with wrong account
```


# Authentication and Caching

Authenticated responses should not unintentionally leak through shared caches.


# Review Headers

```http
Cache-Control:
Pragma:
Vary:
```


# Sensitive Pages

Consider whether pages containing:

```text
Account data

Tokens

Personal information

Recovery information
```

can be cached inappropriately.


# Authentication Headers

APIs may use:

```http
Authorization: Bearer TOKEN
```

or:

```http
Authorization: Basic ...
```


# Basic Authentication

Basic authentication credentials are merely Base64 encoded.

They require HTTPS.


# Bearer Tokens

Anyone possessing a valid bearer token can generally use it within its scope.

Protect bearer tokens from:

```text
Logs

URLs

Referer headers

Client-side storage exposure

Third-party scripts
```


# Tokens in URLs

Avoid:

```text
https://target.example/account?token=SECRET
```

because URLs may appear in:

```text
Browser history

Logs

Analytics

Referer headers
```


# Session Tokens in Local Storage

Applications sometimes store tokens in:

```text
localStorage

sessionStorage
```


# Review Trade-Offs

JavaScript-accessible token storage increases exposure to:

```text
XSS
```


# Cookie-Based Sessions

Properly configured `HttpOnly` cookies reduce direct JavaScript access to session tokens.

But cookie-based authentication requires appropriate consideration of:

```text
CSRF

SameSite

Origin checks
```


# Authentication State in Front-End Code

Do not trust:

```javascript
if (user.isAdmin) {
    showAdminPanel();
}
```

as an authorization control.

Client-side state can improve UX but security decisions must be enforced server-side.


# API Authentication

Test API endpoints independently from the GUI.


# Example

GUI:

```text
/account
```

API:

```text
/api/account
```


# Remove Authentication

Send:

```http
GET /api/account HTTP/1.1
Host: target.example
```

without the session or bearer token.


# Expected

```text
401 Unauthorized
```

or equivalent.


# Invalid Token

Test:

```http
Authorization: Bearer INVALID_TOKEN_7f3a9
```


# Expired Token

Where safely available, verify expired tokens are rejected.


# API Status Codes

Common semantics:

```text
401 -> authentication missing/invalid

403 -> authenticated but not permitted
```

Applications may vary, so interpret behaviour rather than relying solely on status codes.


# Rate Limiting

Authentication endpoints often require abuse controls.


# Candidate Endpoints

```text
Login

Password reset

Registration

MFA verification

Magic links

Verification codes

Recovery codes
```


# Safe Rate-Limit Validation

Use:

```text
Dedicated account

Small request count

Agreed test rate

Controlled window
```


# Observe

```text
429 response

Retry-After

Increasing delay

Temporary account protection

IP throttling

Account throttling
```


# Rate Limit Scope

Determine whether controls apply by:

```text
IP address

Account

Username

Session

Device

Combination
```


# Weak IP-Only Controls

Pure IP-based controls may be insufficient in distributed attack scenarios.

However, bypass testing should remain within the agreed assessment scope.


# Account Lockout

Lockout can reduce guessing but can also create denial-of-service risk.


# Review

```text
Threshold

Duration

Unlock mechanism

Notification

Scope

Administrative recovery
```


# Do Not Lock Real Users

Use dedicated test accounts.


# Lockout Enumeration

Different behaviour for:

```text
Existing account

Unknown account
```

may itself expose usernames.


# Credential Stuffing

Credential stuffing tests should use only credentials specifically authorised for the assessment.

Do not use leaked third-party credentials against real users.


# Password Spraying

Password spraying sends a small number of common passwords across multiple accounts.

This can trigger:

```text
Lockouts

Alerts

Incident response
```

and must be explicitly authorised.


# Magic Links

Passwordless authentication may use emailed links.


# Review

```text
Randomness

Lifetime

Single use

Account binding

Session binding

Redirect handling

Token leakage
```


# Magic Link Replay

After successful authentication:

```text
Replay Same Link
```

Expected:

```text
Rejected
```

if designed as a one-time authentication token.


# Email Verification

Review:

```text
Token randomness

Token lifetime

Account binding

Replay

Whether unverified users gain restricted functionality
```


# Registration Workflow

Review:

```text
Duplicate accounts

Email verification

Username enumeration

Mass assignment

Default roles

Invitation controls

Tenant assignment
```


# Default Role

New users should receive the intended least-privileged role.


# Invitation Systems

Test:

```text
Invitation token randomness

Expiry

Single use

Recipient binding

Tenant binding

Role binding
```


# Account Activation

Activation tokens should not permit:

```text
Activating another account

Changing identity

Escalating role
```


# SSO Authentication

SSO may use:

```text
SAML

OAuth 2.0

OpenID Connect
```

These require protocol-specific testing beyond ordinary session testing.


# SSO Session Lifecycle

Still verify:

```text
Local session creation

Session rotation

Logout

Local session invalidation

Role mapping
```


# Authentication Bypass Through Alternate Endpoints

An application may protect:

```text
/login
```

correctly but expose alternate functionality.


# Search For

```text
/api/login

/mobile/login

/v1/auth

/legacy/login

/admin/login

/sso/callback

/internal/auth
```


# Versioned APIs

Check:

```text
/api/v1/

/api/v2/
```

because older authentication paths may remain reachable.


# HTTP Method Variations

If appropriate, compare:

```text
GET

POST

PUT

PATCH
```

only where the endpoint or framework suggests alternate method handling.


# Do Not Interpret Every 405 as Security-Relevant

Method testing should be driven by application behaviour.


# Authentication Bypass Through Parameters

Review parameters such as:

```text
authenticated

isAdmin

role

userId

verified

mfaComplete
```

if they are supplied by the client.


# Example

```json
{
  "username": "testuser",
  "password": "password",
  "authenticated": true
}
```

The server must ignore client-supplied authentication state.


# Hidden Fields

HTML:

```html
<input type="hidden" name="role" value="user">
```

Hidden does not mean trusted.


# Source Code Review

Authentication source review should trace:

```text
Credential Input
      |
      v
Identity Lookup
      |
      v
Password Verification
      |
      v
MFA
      |
      v
Session Creation
      |
      v
Authorization Context
```


# Generic Authentication Searches

```bash
rg -ni 'login|signin|authenticate|authentication|password|session|cookie|logout|mfa|totp|reset.*password' src/
```


# Password Verification

Search:

```bash
rg -ni 'bcrypt|argon2|scrypt|pbkdf2|password.*verify|verify.*password|check_password' .
```


# Password Hashing

Preferred password storage should use dedicated password hashing algorithms such as:

```text
Argon2id

bcrypt

scrypt

PBKDF2
```

with appropriate parameters.


# Avoid Fast General-Purpose Hashes

Do not store passwords using only:

```text
MD5

SHA-1

SHA-256

SHA-512
```

without an appropriate password hashing construction.


# Plaintext Password Search

```bash
rg -ni 'password\s*[:=]\s*["'\''][^"'\'']+["'\'']' .
```


# Be Careful With Search Results

This may find:

```text
Tests

Examples

Documentation

Dummy credentials
```

Validate context before reporting.


# Session Source Search

```bash
rg -ni 'session|Set-Cookie|cookie|HttpOnly|SameSite|Secure|Max-Age|Expires' src/
```


# Session Rotation Search

Framework-specific APIs vary.

Search conceptually for:

```text
regenerate

rotate

invalidate

destroy session
```


# Generic

```bash
rg -ni 'regenerate|rotate.*session|invalidate.*session|destroy.*session|session.*invalidate' src/
```


# Password Reset Search

```bash
rg -ni 'forgot.*password|reset.*password|reset.*token|password.*token|recovery' src/
```


# Token Generation Search

```bash
rg -ni 'random|SecureRandom|secrets\.|randomBytes|random_bytes|token_urlsafe|UUID' src/
```


# Important

A random-looking API name does not automatically mean the token is cryptographically secure.

Trace the actual generator.


# MFA Search

```bash
rg -ni 'mfa|2fa|totp|otp|backup.*code|recovery.*code|authenticator' src/
```


# Authentication Middleware

Search:

```bash
rg -ni 'middleware|auth_required|login_required|RequireAuthorization|Authorize|authenticated' src/
```


# Source Review Questions

Ask:

```text
How are users identified?

How are passwords verified?

What password hashing algorithm is used?

Are authentication errors generic?

When is the session created?

Does the session ID rotate after login?

Does it rotate after MFA?

What state represents partial authentication?

Can partial sessions reach protected endpoints?

How are sessions invalidated?

How are reset tokens generated?

How are reset tokens stored?

Are reset tokens hashed at rest?

Are tokens single-use?

How is MFA reset?

How are backup codes generated?

How are remembered devices implemented?

How are authorization roles loaded?

Does any security decision trust client-controlled state?
```


# Framework Session Controls

Use framework-provided session mechanisms where possible rather than designing custom session tokens.


# Custom Authentication

Custom authentication code deserves additional scrutiny.

Look for:

```text
Custom crypto

Predictable tokens

Manual cookie construction

Client-side roles

Unsigned state

Home-grown password hashing
```


# Session Token Entropy

Do not estimate entropy solely by:

```text
Token length
```

A 64-character token can still be predictable if generated from deterministic data.


# Better Evidence

Use:

```text
Source review

Documented framework behaviour

Token generation implementation
```


# Session Binding

Some applications bind sessions to:

```text
IP address

User-Agent

Device identifier
```

These controls can provide additional signals but can also cause usability issues and should not replace unpredictable session identifiers.


# IP Binding

Be cautious with strict IP binding because legitimate users may change networks.


# Session Replay

Bearer-style sessions are inherently replayable while valid.

The security objective is usually:

```text
Prevent token theft

Limit lifetime

Support revocation

Detect suspicious use
```


# Session Exposure

Search for session identifiers in:

```text
URLs

HTML

JavaScript

Logs

Error messages

Analytics

Third-party requests
```


# Session ID in URL

Example:

```text
/account?session=SECRET
```

is generally undesirable.


# URL Risks

URLs can appear in:

```text
Browser history

Proxy logs

Server logs

Referer headers

Screenshots
```


# HTTPS

Authentication and session traffic should use HTTPS.


# HTTP Redirect

Check whether:

```text
http://target.example
```

redirects to:

```text
https://target.example
```


# HSTS

Review:

```http
Strict-Transport-Security:
```

for HTTPS applications where HSTS is appropriate.


# Do Not Test TLS Only From Browser Icons

Inspect actual protocol and headers.


# Error Messages

Authentication errors should avoid exposing:

```text
Database errors

Stack traces

Internal usernames

LDAP details

Directory paths

Authentication backend details
```


# Logging

Applications should log security-relevant events such as:

```text
Successful login

Failed login

Password reset

Password change

MFA change

Session revocation

Account lockout
```


# Avoid Logging Secrets

Do not log:

```text
Passwords

Reset tokens

Session identifiers

MFA secrets

Backup codes
```


# Detection Opportunities

Potential security signals include:

```text
Repeated failed logins

Distributed failures against one account

MFA failures

Password reset bursts

Session reuse from unusual contexts

Multiple session revocations

Recovery changes
```


# Authentication False Positives

## Different Error Messages

Different wording may be intentional but still constitute enumeration if it reveals account existence.

The question is whether an attacker gains reliable information.


## Different Response Length

Small length differences may result from:

```text
CSRF tokens

Dynamic timestamps

Random IDs

Advertisements
```

Compare the actual content.


## Session Cookie Before Login

A pre-authentication session cookie is normal.

The issue is whether authentication securely upgrades or replaces the session.


## Long-Lived Cookie

A long-lived cookie may be:

```text
Preference cookie

Analytics cookie

Remember-me token
```

Identify its purpose before reporting.


## Missing HttpOnly

Not every cookie requires `HttpOnly`.

It is most important for sensitive authentication/session cookies.


## Missing SameSite

Assess actual authentication and cross-site request behaviour rather than treating every absent attribute as automatically exploitable CSRF.


# Authentication Evidence

Capture:

```text
Finding ID

Endpoint

Method

Account used

Role

Baseline request

Modified request

Response

Status

Relevant headers

Cookies

Session lifecycle

Timestamp
```


# Sensitive Evidence

Redact:

```text
Passwords

Session tokens

Reset tokens

MFA secrets

Backup codes

Personal information
```


# Example

Instead of:

```text
session=eyJhbGciOi...FULL_TOKEN
```

use:

```text
session=eyJhbGciOi...<redacted>
```


# Reporting Username Enumeration

> The authentication endpoint responds differently depending on whether a supplied username exists. Requests containing a valid username and an incorrect password return a different response from requests containing a non-existent username. This allows unauthenticated users to determine valid account identifiers and may facilitate password spraying, credential stuffing or targeted social engineering.


# Reporting Session Fixation

> The application retains the same session identifier before and after successful authentication. Testing confirmed that a pre-authentication session identifier can become associated with an authenticated account rather than being replaced during authentication. The application should regenerate the session identifier when the authentication state changes.


# Reporting Logout Failure

> Logging out removes the session cookie from the browser but does not invalidate the corresponding server-side session. Replaying an authenticated request using the pre-logout session identifier after logout continued to return authenticated content. Logout should invalidate the server-side session in addition to removing the browser cookie.


# Reporting MFA Bypass

> After valid username and password authentication, the application creates a partially authenticated session and presents an MFA challenge. However, the same partial session can directly access an endpoint intended for fully authenticated users without completing MFA. MFA state must be enforced server-side for every protected request.


# Reporting Password Reset Replay

> Password reset tokens remain valid after successful use. A reset token that had already been used to change the account password could be replayed to perform another password change. Reset tokens should be invalidated atomically after their first successful use.


# Reporting Cookie Configuration

> The application's primary authentication cookie is transmitted without the `HttpOnly` attribute. Because the cookie represents the authenticated session, client-side scripts can access its value. The session cookie should be configured with `HttpOnly` unless the application has a documented requirement for JavaScript access.


# Reporting Client-Controlled Authentication State

> The application accepts security-relevant account state from a client-controlled request parameter and uses that value when constructing the authenticated session. Authentication and authorization state must be derived from trusted server-side identity information rather than values supplied by the client.


# Reporting Weak Session Revocation

> Changing the account password does not invalidate existing authenticated sessions. A session established before the password change remained fully usable afterwards. For this application's threat model, password changes should revoke other active sessions and long-lived authentication tokens.


# Avoid Overclaiming

Do not write:

```text
Authentication is completely broken.
```

when you demonstrated only:

```text
Username enumeration.
```


# State Exact Behaviour

Prefer:

```text
The login endpoint reveals whether an account exists
through distinguishable responses.
```


# Severity Considerations

Consider:

```text
Unauthenticated exploitability

Account sensitivity

MFA presence

Rate limiting

Password policy

Enumeration reliability

Session lifetime

Reset-token lifetime

Recovery controls

Privilege of affected accounts

Required user interaction

Existing compensating controls
```


# Authentication Remediation Principles

## Generic Errors

Return a consistent response for authentication failures.

Example:

```text
Invalid username or password.
```


# Consistent Processing

Where practical, authentication logic should avoid large measurable processing differences between:

```text
Existing user

Unknown user
```


# Password Storage

Use a modern password hashing algorithm with appropriate parameters.


# Password Reset

Use:

```text
Cryptographically random tokens

Short lifetime

Single use

Account binding

Secure delivery

Server-side validation
```


# Session Rotation

Regenerate session identifiers after:

```text
Successful login

MFA completion

Privilege elevation
```


# Session Invalidation

Support reliable invalidation after:

```text
Logout

Password reset

Security-sensitive account recovery

Administrative revocation
```


# Cookie Hardening

Authentication cookies should generally consider:

```text
Secure

HttpOnly

Appropriate SameSite

Narrow Domain

Appropriate Path

Appropriate lifetime
```


# Server-Side Authorization

Never use client-controlled values as authoritative proof of:

```text
Identity

Role

Tenant

MFA status

Privilege
```


# MFA

Enforce MFA server-side as part of authentication state.


# Rate Limiting

Apply abuse controls to:

```text
Login

MFA

Recovery

Reset

Registration
```

using a design appropriate to the application's risk profile.


# Account Recovery

Recovery should not be materially weaker than normal authentication.


# Re-Authentication

Require appropriate verification before highly sensitive account changes.


# Retesting Authentication

Retest the original issue and surrounding lifecycle.


# Username Enumeration Retest

Compare:

```text
Existing user + invalid password

Unknown user + invalid password
```

Expected:

```text
Equivalent external behaviour
```

within reasonable implementation constraints.


# Session Fixation Retest

Capture:

```text
Pre-auth session

Post-auth session
```

Expected:

```text
Different identifiers
```


# Logout Retest

```text
Login
  |
  v
Capture Request
  |
  v
Logout
  |
  v
Replay Old Request
```

Expected:

```text
Rejected
```


# Password Reset Retest

Verify:

```text
Token expires

Token is single-use

Token is account-bound

Old token fails after successful reset
```


# MFA Retest

Verify a partially authenticated session cannot access protected endpoints.


# Session Revocation Retest

Verify revoked sessions cannot be replayed.


# Password Change Retest

Verify the intended session-invalidation policy is enforced.


# Cookie Retest

Inspect:

```http
Set-Cookie:
```

and verify required attributes.


# Root Cause Review

After identifying one authentication issue, search for equivalent flows.

Review:

```text
Web login

API login

Mobile API

Legacy API

Admin login

SSO

Password reset

MFA recovery

Invitation acceptance
```


# Authentication Checklist

## Attack Surface

- [ ] Login identified
- [ ] Registration identified
- [ ] Logout identified
- [ ] Forgot-password identified
- [ ] Password-reset identified
- [ ] Password-change identified
- [ ] Email-change identified
- [ ] MFA enrolment identified
- [ ] MFA verification identified
- [ ] MFA recovery identified
- [ ] Remember-me functionality identified
- [ ] SSO identified
- [ ] API authentication identified
- [ ] Session-management functionality identified

## Login

- [ ] Valid login baseline captured
- [ ] Invalid password tested
- [ ] Invalid username tested
- [ ] Response status compared
- [ ] Response body compared
- [ ] Response length compared
- [ ] Redirects compared
- [ ] Cookies compared
- [ ] Timing considered
- [ ] Generic error handling reviewed

## Enumeration

- [ ] Login enumeration tested
- [ ] Registration enumeration tested
- [ ] Password-reset enumeration tested
- [ ] MFA/recovery enumeration considered
- [ ] Timing differences validated carefully
- [ ] Side effects considered

## Passwords

- [ ] Minimum length reviewed
- [ ] Maximum length reviewed
- [ ] Long password support reviewed
- [ ] Truncation considered
- [ ] Common-password controls reviewed
- [ ] Password reuse reviewed
- [ ] Password storage reviewed where source available
- [ ] Current-password requirement reviewed for password changes

## Rate Limiting

- [ ] Login throttling reviewed
- [ ] Account-based throttling reviewed
- [ ] IP-based throttling reviewed
- [ ] MFA throttling reviewed
- [ ] Password-reset throttling reviewed
- [ ] Registration throttling reviewed
- [ ] Lockout behaviour reviewed
- [ ] Real-user lockouts avoided

## Password Reset

- [ ] Enumeration reviewed
- [ ] Token randomness reviewed
- [ ] Token lifetime reviewed
- [ ] Single use tested
- [ ] Account binding tested
- [ ] Token leakage reviewed
- [ ] Reset-link host handling reviewed
- [ ] Password policy reviewed
- [ ] Session invalidation reviewed

## MFA

- [ ] Partial authentication state identified
- [ ] Direct navigation tested
- [ ] API access before MFA tested
- [ ] OTP rate limiting reviewed
- [ ] OTP replay reviewed
- [ ] Backup codes reviewed
- [ ] Backup-code replay reviewed
- [ ] MFA enrolment reviewed
- [ ] MFA disablement reviewed
- [ ] MFA recovery reviewed
- [ ] User notification reviewed

## Sessions

- [ ] Pre-login session captured
- [ ] Post-login session captured
- [ ] Session rotation reviewed
- [ ] Session randomness reviewed
- [ ] Session lifetime reviewed
- [ ] Idle timeout reviewed
- [ ] Absolute timeout reviewed
- [ ] Concurrent sessions reviewed
- [ ] Session-management page reviewed
- [ ] Session revocation tested

## Cookies

- [ ] `Secure` reviewed
- [ ] `HttpOnly` reviewed
- [ ] `SameSite` reviewed
- [ ] `Domain` reviewed
- [ ] `Path` reviewed
- [ ] `Expires` reviewed
- [ ] `Max-Age` reviewed
- [ ] Sensitive cookie purpose confirmed

## Logout

- [ ] Browser cookie removal reviewed
- [ ] Server-side invalidation reviewed
- [ ] Old session replay tested
- [ ] Remember-me token invalidation reviewed

## Sensitive Account Changes

- [ ] Password change reviewed
- [ ] Email change reviewed
- [ ] MFA disablement reviewed
- [ ] Recovery changes reviewed
- [ ] Re-authentication requirements reviewed
- [ ] User notifications reviewed

## Source Review

- [ ] Login handlers identified
- [ ] Password verification identified
- [ ] Password hashing reviewed
- [ ] Session generation reviewed
- [ ] Session rotation reviewed
- [ ] Session invalidation reviewed
- [ ] Reset-token generation reviewed
- [ ] MFA implementation reviewed
- [ ] Authorization state source reviewed
- [ ] Client-controlled security state reviewed

## Evidence

- [ ] Endpoint
- [ ] Method
- [ ] Test account
- [ ] Role
- [ ] Baseline request
- [ ] Modified request
- [ ] Response
- [ ] Relevant headers
- [ ] Cookie state
- [ ] Authentication state
- [ ] Timestamp
- [ ] Secrets redacted

## Retest

- [ ] Original issue retested
- [ ] Equivalent authentication endpoints reviewed
- [ ] Legitimate authentication still works
- [ ] Session lifecycle retested
- [ ] Recovery lifecycle retested
- [ ] MFA lifecycle retested


# Authentication Response Matrix

| Test | Expected Secure Behaviour |
|---|---|
| Unknown username | Generic authentication failure |
| Wrong password | Generic authentication failure |
| Repeated failures | Appropriate throttling |
| Successful login | New authenticated session |
| MFA pending | Protected resources unavailable |
| MFA success | Authentication state upgraded securely |
| Logout | Session invalidated |
| Reset token replay | Rejected |
| Expired reset token | Rejected |
| Password change | Intended session policy enforced |


# Cookie Matrix

| Attribute | Purpose |
|---|---|
| `Secure` | Restricts cookie transmission to HTTPS |
| `HttpOnly` | Restricts normal JavaScript access |
| `SameSite` | Controls some cross-site cookie sending |
| `Domain` | Defines host scope |
| `Path` | Defines URL path scope |
| `Expires` | Absolute persistence expiry |
| `Max-Age` | Relative persistence lifetime |


# Authentication State Matrix

| State | Expected Access |
|---|---|
| Unauthenticated | Public resources only |
| Primary credentials accepted, MFA pending | MFA completion resources only |
| Fully authenticated | User-authorized resources |
| Logged out | Public resources only |
| Revoked session | Public resources only |
| Expired session | Public resources only |


# Password Reset Matrix

| Control | Expected |
|---|---|
| Token randomness | Cryptographically strong |
| Lifetime | Limited |
| Single use | Yes |
| Account binding | Yes |
| Token leakage | Minimized |
| Password policy | Enforced |
| Session invalidation | Defined by threat model |
| User notification | Appropriate |


# MFA Matrix

| Test | Expected |
|---|---|
| Direct dashboard access before MFA | Rejected |
| API access before MFA | Rejected |
| Incorrect OTP | Rejected |
| Repeated incorrect OTPs | Throttled |
| Used backup code replay | Rejected |
| MFA disablement | Strong verification |
| MFA recovery | Strong identity verification |


# Session Lifecycle Matrix

| Event | Session Consideration |
|---|---|
| Anonymous visit | Pre-auth session may exist |
| Login | Rotate session |
| MFA completion | Rotate or securely upgrade session |
| Privilege elevation | Rotate session |
| Password change | Review/revoke sessions per policy |
| Password reset | Review/revoke sessions per policy |
| Logout | Revoke active session |
| Admin revocation | Session becomes unusable |


# Evidence Matrix

| Observation | Supported Conclusion |
|---|---|
| Different error for valid username | Username enumeration |
| Same session before/after auth plus attacker-settable pre-auth ID | Session fixation |
| Old session works after logout | Failed session invalidation |
| Partial MFA session accesses protected endpoint | MFA bypass |
| Reset token works twice | Reset-token replay |
| Client controls trusted role value | Broken trust boundary |
| Sensitive cookie lacks HttpOnly | Cookie hardening weakness |
| Session token appears in URL | Session exposure risk |


# False Positive Matrix

| Observation | Alternative Explanation |
|---|---|
| Different response length | Dynamic content |
| Slow login | Network/application load |
| Cookie before login | Anonymous session |
| Long-lived cookie | Non-authentication preference |
| Missing HttpOnly | Cookie may not be sensitive |
| 302 after login | Normal application routing |
| Session value unchanged | May require fixation reachability analysis |


# Source Review Priority Matrix

| Pattern | Priority |
|---|---:|
| Framework authentication + server-side sessions | Normal review |
| Custom session generation | High |
| Client-controlled role or identity | Very High |
| Weak/custom password hashing | Very High |
| Password reset token from predictable data | Very High |
| MFA enforced only in front-end | Very High |
| Session not invalidated server-side | High |
| Authentication token in URL | High |


# Remediation Matrix

| Issue | Primary Remediation |
|---|---|
| Username enumeration | Consistent external responses |
| Weak passwords | Strong password policy and secure hashing |
| Login abuse | Rate limiting and monitoring |
| Session fixation | Rotate session on authentication |
| Weak cookie configuration | Appropriate cookie attributes |
| Logout replay | Server-side session invalidation |
| Reset token replay | Single-use tokens |
| Weak reset token | Cryptographically random token |
| MFA bypass | Server-side MFA state enforcement |
| Client-controlled role | Server-side identity/authorization state |


# Burp Quick Workflow

```text
                   LOGIN
                     |
                     v
              CAPTURE BASELINE
                     |
          +----------+----------+
          |                     |
          v                     v
     WRONG PASSWORD        UNKNOWN USER
          |                     |
          +----------+----------+
                     |
                     v
                  COMPARE
                     |
                     v
               RATE LIMITING
                     |
                     v
                     MFA
                     |
                     v
              SESSION CREATION
                     |
                     v
               COOKIE REVIEW
                     |
                     v
             SESSION ROTATION
                     |
                     v
              LOGOUT / REPLAY
                     |
                     v
              PASSWORD RESET
                     |
                     v
              CAPTURE EVIDENCE
```


# Session Testing Model

```text
                PRE-AUTH SESSION
                       |
                       v
                     LOGIN
                       |
                       v
                SESSION ROTATION
                       |
                       v
                 MFA COMPLETION
                       |
                       v
              AUTHENTICATED SESSION
                       |
              +--------+--------+
              |                 |
              v                 v
          ACTIVITY          PRIVILEGE CHANGE
              |                 |
              +--------+--------+
                       |
                       v
                    LOGOUT
                       |
                       v
                  INVALIDATED
```


# Password Reset Model

```text
                RESET REQUEST
                      |
                      v
              GENERATE RANDOM TOKEN
                      |
                      v
                 DELIVER TOKEN
                      |
                      v
                 VERIFY TOKEN
                      |
                      v
               CHANGE PASSWORD
                      |
                      v
                INVALIDATE TOKEN
                      |
                      v
             SESSION POLICY APPLIED
```


# MFA Enforcement Model

```text
              USERNAME + PASSWORD
                       |
                       v
                 PRIMARY AUTH
                       |
                       v
                 PARTIAL STATE
                       |
              +--------+--------+
              |                 |
              v                 v
        PROTECTED API        MFA VERIFY
              |                 |
              v                 v
           REJECT          FULL SESSION
                                |
                                v
                         PROTECTED API
                                |
                                v
                              ALLOW
```


# Secure Authentication Model

```text
                 USER CREDENTIALS
                        |
                        v
               IDENTITY VERIFICATION
                        |
                        v
                 MFA IF REQUIRED
                        |
                        v
                SESSION ROTATION
                        |
                        v
              SERVER-SIDE IDENTITY
                        |
                        v
              SERVER AUTHORIZATION
                        |
                        v
                  APPLICATION
```


# Practical Validation Model

```text
Prerequisites
     |
     v
Map Authentication Surface
     |
     v
Capture Valid Baseline
     |
     v
Test Failure Behaviour
     |
     v
Review Abuse Controls
     |
     v
Review MFA
     |
     v
Review Session Creation
     |
     v
Review Cookie Security
     |
     v
Test Session Lifecycle
     |
     v
Review Recovery
     |
     v
Interpret Evidence
     |
     v
Remediation
     |
     v
Retest
```


# Final Testing Principle

Authentication testing is not only:

```text
LOGIN FORM
```

It is:

```text
IDENTITY
   |
   v
AUTHENTICATION
   |
   v
MFA
   |
   v
SESSION
   |
   v
RECOVERY
   |
   v
REVOCATION
```

For every authentication implementation ask:

```text
Can users be enumerated?

How are passwords stored?

Are long passwords supported?

Can login attempts be abused at scale?

How is MFA enforced?

Can MFA be skipped through direct requests?

Can recovery bypass MFA?

How are reset tokens generated?

Are reset tokens single-use?

Are reset tokens account-bound?

Does password reset invalidate appropriate sessions?

When is the session created?

Does the session rotate after login?

Does the session rotate after MFA?

Are session identifiers unpredictable?

Are authentication cookies properly scoped?

Are sensitive cookies Secure?

Are sensitive cookies HttpOnly?

Is SameSite appropriate?

Can old sessions be replayed after logout?

Can users revoke sessions?

What happens after a password change?

What happens after an MFA reset?

Can client-controlled fields define identity or role?

Are API authentication controls equivalent to the GUI?

Are old or alternate authentication endpoints still exposed?

Are secrets present in URLs or logs?

Are security events monitored?

Does account recovery provide weaker authentication than login?

Have the findings been demonstrated with dedicated test accounts?

Have secrets been redacted from evidence?
```

The strongest authentication assessment does not end at:

```text
Login successful.
```

It follows the identity through the entire lifecycle:

```text
IDENTITY CLAIM
      |
      v
CREDENTIAL VERIFICATION
      |
      v
SECOND FACTOR
      |
      v
SESSION CREATION
      |
      v
SESSION USE
      |
      v
SENSITIVE ACCOUNT CHANGES
      |
      v
RECOVERY
      |
      v
LOGOUT
      |
      v
REVOCATION
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)
- [Cross-Site Scripting (XSS) Cheatsheet](xss.md)
- [Insecure Deserialization Cheatsheet](deserialization.md)
- [SQL Injection Cheatsheet](sql-injection.md)


# Related Notes

- [Authentication](../web/authentication.md)
- [Session Management](../web/session-management.md)
- [Password Reset](../web/password-reset.md)
- [Multi-Factor Authentication](../web/mfa.md)
- [Web Application Methodology](../web/methodology.md)


# References

- [PortSwigger Web Security Academy - Authentication](https://portswigger.net/web-security/authentication){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-63B - Authentication and Authenticator Management](https://pages.nist.gov/800-63-4/sp800-63b.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Test the lifecycle"

    A strong authentication assessment follows the account from login through MFA, session creation, password changes, recovery, logout and revocation rather than treating each screen as an isolated feature.


!!! tip "Use two dedicated accounts"

    Separate test accounts make it much easier to distinguish authentication problems from authorization problems and reduce the risk of affecting real users.


!!! tip "Replay sessions after security events"

    Replaying an existing authenticated request after logout, password reset, password change or explicit session revocation is one of the simplest ways to validate whether server-side invalidation actually occurs.


!!! warning "Do not lock out real users"

    Brute-force, password-spraying, OTP and lockout testing can affect availability and trigger incident response. Use dedicated accounts, controlled request counts and the agreed assessment scope.


!!! warning "A cookie attribute is not the whole finding"

    Cookie attributes should be assessed according to the cookie's purpose, authentication model and actual attack path. Avoid reporting every cookie with a missing attribute as an exploitable session vulnerability without establishing relevance.
