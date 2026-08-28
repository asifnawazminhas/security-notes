# Multi-Factor Authentication Security

Multi-factor authentication (MFA) strengthens authentication by requiring users to prove their identity using more than one independent authentication factor.

A typical authentication flow is:

```text
Username
   ↓
Password
   ↓
First Factor Valid
   ↓
MFA Challenge
   ↓
Second Factor Valid
   ↓
Fully Authenticated Session
```

MFA becomes ineffective when an attacker can bypass the second factor through weaknesses in:

```text
Workflow state
Session management
OTP validation
Rate limiting
Recovery mechanisms
Remember-device functionality
API endpoints
Direct URL access
Response handling
Account recovery
SSO integration
Trusted-device tokens
MFA reset
Backup codes
Race conditions
```

The central testing question is:

```text
Does the server independently enforce MFA
before granting access to protected functionality?
```

!!! warning "Authorised Security Testing"
    Perform MFA testing only against accounts and authentication factors that are explicitly authorised for the assessment. Use controlled test accounts, controlled phone numbers, controlled authenticator applications, and controlled email addresses wherever possible. Avoid locking real users out, consuming genuine recovery codes, generating excessive SMS messages, or performing high-volume OTP guessing unless specifically authorised.

---

# Authentication Factors

Authentication factors are generally divided into:

```text
Something You Know
Something You Have
Something You Are
```

Examples:

| Factor | Examples |
|---|---|
| Knowledge | Password, PIN |
| Possession | Authenticator app, hardware token, phone |
| Inherence | Fingerprint, facial recognition |

MFA should combine independent factors.

For example:

```text
Password
+
TOTP
```

is MFA because it combines:

```text
Knowledge
+
Possession
```

Using:

```text
Password
+
Security Question
```

does not provide the same assurance because both are knowledge factors.

---

# MFA Architecture

A common MFA workflow looks like:

```text
User
  ↓
POST /login
  ↓
Password Verified
  ↓
Temporary Authentication State
  ↓
MFA Challenge
  ↓
POST /mfa/verify
  ↓
OTP Verified
  ↓
Authentication State Upgraded
  ↓
Fully Authenticated Session
```

The critical transition is:

```text
Partially Authenticated
        ↓
Fully Authenticated
```

This transition must occur only after successful MFA verification.

---

# Authentication State Machine

Think of MFA as a state machine:

```text
STATE 0
Unauthenticated
    ↓
Correct Password
    ↓
STATE 1
Password Verified
MFA Pending
    ↓
Correct MFA
    ↓
STATE 2
Fully Authenticated
```

The application must enforce:

```text
STATE 0
Cannot access authenticated resources

STATE 1
Cannot access fully authenticated resources

STATE 2
Can access authorised resources
```

A common MFA vulnerability occurs when:

```text
STATE 1
```

is mistakenly treated as:

```text
STATE 2
```

---

# MFA Testing Methodology

Use a structured workflow:

```text
Create Controlled Account
        ↓
Enable MFA
        ↓
Record Normal Login
        ↓
Map Every MFA Request
        ↓
Identify Authentication State
        ↓
Inspect Cookies / Tokens
        ↓
Test Direct Resource Access
        ↓
Test Workflow Manipulation
        ↓
Test OTP Validation
        ↓
Test Account Binding
        ↓
Test Rate Limiting
        ↓
Test Remember-Device
        ↓
Test Recovery Codes
        ↓
Test MFA Reset
        ↓
Test Password Reset Interaction
        ↓
Test Session Behaviour
        ↓
Test API Enforcement
        ↓
Verify Minimal Impact
        ↓
Report
```

---

# Establish a Baseline

First perform a completely normal login.

Record:

```text
Login request
Login response
Cookies before MFA
MFA challenge request
MFA verification request
Cookies after MFA
Redirects
Access tokens
Refresh tokens
Protected resources
```

This baseline becomes essential when comparing bypass attempts.

---

# Burp Proxy Workflow

Use Burp Proxy to capture:

```text
POST /login
        ↓
302 /mfa
        ↓
GET /mfa
        ↓
POST /mfa/verify
        ↓
302 /dashboard
        ↓
GET /dashboard
```

Pay particular attention to:

```text
Set-Cookie
Location
Authorization
JWTs
Hidden parameters
CSRF tokens
MFA identifiers
Challenge IDs
```

---

# Before and After MFA Comparison

Record the authentication material before MFA.

Example:

```http
Set-Cookie: session=PRE_MFA_SESSION
```

After successful MFA:

```http
Set-Cookie: session=POST_MFA_SESSION
```

Questions:

```text
Does the session rotate?

Does the server track MFA completion?

Is MFA status embedded in a token?

Does the same pre-MFA session become privileged?

Can the pre-MFA session access protected endpoints?
```

---

# Direct Endpoint Access

One of the highest-value MFA tests is extremely simple:

```text
Authenticate with password
        ↓
Stop at MFA
        ↓
Request /dashboard directly
```

Example:

```http
GET /dashboard HTTP/1.1
Host: target.example
Cookie: session=PRE_MFA_SESSION
```

Expected:

```text
Redirect to MFA
```

or:

```text
403 Forbidden
```

Potential vulnerability:

```text
200 OK
Protected content returned
```

---

# Do Not Trust Redirects Alone

Suppose:

```http
GET /account HTTP/1.1
Cookie: session=PRE_MFA_SESSION
```

returns:

```http
HTTP/1.1 302 Found
Location: /mfa
```

Check the response body.

Occasionally applications return:

```text
302 Redirect
+
Sensitive HTML
```

The browser follows the redirect, but the protected data was still disclosed.

Inspect the raw response.

---

# Test Multiple Protected Resources

Do not test only:

```text
/dashboard
```

Also consider:

```text
/account
/profile
/settings
/admin
/api/me
/api/account
/api/orders
/api/messages
/api/documents
/api/admin
```

The UI may enforce MFA while APIs do not.

---

# API MFA Enforcement

A common architecture is:

```text
Web Frontend
    ↓
MFA Check
    ↓
API
```

But the API may trust the session without checking MFA state.

Test:

```text
Password Valid
MFA Pending
      ↓
Direct API Request
```

Example:

```http
GET /api/account HTTP/1.1
Authorization: Bearer PRE_MFA_TOKEN
```

Expected:

```text
Denied
```

---

# Partial Authentication Tokens

Applications sometimes issue a token after password verification.

Example JWT:

```json
{
    "sub": "1001",
    "authenticated": true,
    "mfa": false
}
```

After MFA:

```json
{
    "sub": "1001",
    "authenticated": true,
    "mfa": true
}
```

Every sensitive backend endpoint must understand the distinction.

---

# JWT MFA State

Look for claims such as:

```text
mfa
mfa_verified
amr
acr
auth_level
authentication_level
loa
otp_verified
```

Example:

```json
{
    "sub": "1001",
    "amr": [
        "pwd"
    ]
}
```

After MFA:

```json
{
    "sub": "1001",
    "amr": [
        "pwd",
        "otp"
    ]
}
```

Refer to:

```text
docs/web/jwt.md
```

for JWT-specific testing.

---

# Authentication Method Reference

OpenID Connect commonly uses:

```text
amr
```

to describe authentication methods.

Conceptually:

```text
pwd
```

may indicate password authentication.

```text
otp
```

may indicate an OTP mechanism.

Do not assume every application implements these claims correctly.

---

# MFA Workflow Bypass

A typical vulnerable workflow:

```text
POST /login
    ↓
Password Correct
    ↓
GET /mfa
    ↓
POST /mfa/verify
    ↓
GET /dashboard
```

Try:

```text
POST /login
    ↓
Password Correct
    ↓
GET /dashboard
```

If successful:

```text
MFA is only enforced by application navigation
```

rather than by the server-side authorisation layer.

---

# Skipping MFA Verification

Another workflow may be:

```text
/login
   ↓
/mfa/send
   ↓
/mfa/verify
   ↓
/mfa/complete
   ↓
/dashboard
```

Test whether:

```text
/mfa/complete
```

can be accessed before:

```text
/mfa/verify
```

Security-relevant workflow transitions must be validated server-side.

---

# Client-Side MFA Enforcement

Look for JavaScript such as:

```javascript
if (response.mfaVerified) {
    window.location = "/dashboard";
}
```

Changing the response locally may reveal the dashboard route.

That alone is not a vulnerability.

The real question is:

```text
Does the server allow protected actions?
```

---

# Response Manipulation

Suppose the server returns:

```json
{
    "success": false,
    "mfaVerified": false
}
```

Changing it in the browser to:

```json
{
    "success": true,
    "mfaVerified": true
}
```

may cause the frontend to navigate to:

```text
/dashboard
```

This only becomes a security vulnerability if:

```text
/dashboard
```

or the underlying APIs accept the partially authenticated session.

Important:

```text
Frontend Bypass
      ≠
Authentication Bypass
```

---

# Burp Match and Replace

Burp Match and Replace can help investigate client-side response handling.

For example, in a controlled environment you might temporarily modify:

```text
"mfaVerified": false
```

to:

```text
"mfaVerified": true
```

This can reveal:

```text
Client-side workflow assumptions
Hidden routes
Additional API calls
```

Always verify server-side access separately.

---

# Hidden MFA Parameters

Look for parameters such as:

```text
mfa=true
mfa=false
verified=true
otpVerified=true
step=2
stage=complete
authLevel=2
challengeComplete=true
```

Example:

```http
POST /login HTTP/1.1
Content-Type: application/json

{
    "username": "controlled-user",
    "password": "CONTROLLED_PASSWORD",
    "mfa": true
}
```

Security state must not be derived from attacker-controlled values.

---

# Hidden Form Fields

Example:

```html
<input
    type="hidden"
    name="mfaVerified"
    value="true">
```

Never trust:

```text
Hidden form fields
```

for authentication decisions.

---

# MFA State in Cookies

Inspect cookies for values such as:

```text
mfa=true
verified=true
auth_level=2
```

Example:

```http
Cookie: session=ABC; mfa_verified=true
```

Test whether the server trusts an unsigned client-controlled cookie.

Expected:

```text
Server-side verification
```

not:

```text
Trust arbitrary cookie value
```

---

# MFA State in LocalStorage

Search:

```text
localStorage
sessionStorage
```

for:

```text
mfa
verified
authenticated
authLevel
```

Example:

```javascript
localStorage.setItem(
    "mfaVerified",
    "true"
);
```

This may control the UI but must not control server-side access.

---

# OTP-Based MFA

One-time passwords are commonly delivered through:

```text
Authenticator application
SMS
Email
Hardware token
```

Common formats:

```text
6-digit numeric
8-digit numeric
Alphanumeric
```

---

# TOTP

Time-based One-Time Passwords are commonly generated using:

```text
Shared Secret
+
Current Time
+
Cryptographic Function
```

Conceptually:

```text
Shared Secret
      ↓
Time Window
      ↓
TOTP Algorithm
      ↓
One-Time Code
```

The server independently calculates acceptable codes.

---

# HOTP

HMAC-based One-Time Passwords use:

```text
Shared Secret
+
Counter
```

rather than time.

The counter must remain synchronised.

---

# OTP Validation

Test:

```text
Correct OTP
Incorrect OTP
Expired OTP
Previously used OTP
OTP from another controlled account
```

---

# Two-Account OTP Binding

Create:

```text
User A
User B
```

Both with MFA enabled.

Generate:

```text
OTP_A
OTP_B
```

Test:

| OTP | Session | Expected |
|---|---|---|
| OTP A | User A | Allow |
| OTP A | User B | Deny |
| OTP B | User B | Allow |
| OTP B | User A | Deny |
| Invalid OTP | User A | Deny |

This verifies:

```text
OTP
    ↓
Correct Account / Challenge
```

binding.

---

# MFA Challenge IDs

Some applications use:

```text
challengeId
transactionId
mfaId
verificationId
```

Example:

```json
{
    "challengeId": "829192",
    "code": "123456"
}
```

Test whether:

```text
Challenge A
```

can be used with:

```text
Session B
```

using two controlled accounts.

---

# Challenge Binding

Secure design:

```text
Challenge
   ↓
Account
   ↓
Session
   ↓
Authentication Attempt
```

should be securely associated.

---

# OTP Replay

After successful OTP verification:

```text
OTP
 ↓
Accepted
```

test whether the same OTP can be submitted again.

For TOTP, a small acceptance window may exist because of clock skew.

Whether replay is prevented within the same TOTP time step depends on the application's risk model.

For high-security applications, preventing reuse can provide additional protection.

---

# OTP Expiration

Test whether old codes remain accepted beyond the intended window.

Do not assume:

```text
Six digits
```

means:

```text
30-second TOTP
```

The implementation may be custom.

---

# Time Window

TOTP implementations commonly tolerate neighbouring time windows for clock drift.

Conceptually:

```text
Previous Window
Current Window
Next Window
```

An excessively large acceptance window weakens security.

---

# OTP Brute Force

A six-digit numeric code has:

```text
1,000,000
```

possible combinations.

MFA security therefore depends heavily on online protections.

Look for:

```text
Attempt limits
Rate limiting
Challenge invalidation
Account lockout
Progressive delays
Risk-based controls
```

---

# Safe OTP Rate-Limit Testing

Start with a very small number of incorrect codes:

```text
000001
000002
000003
```

using a controlled account.

Observe:

```text
HTTP status
Response
Delay
Headers
Challenge state
Account state
```

Do not attempt exhaustive brute force unless explicitly authorised.

---

# Rate-Limit Scope

Determine whether rate limiting applies to:

```text
IP address
Account
Session
Challenge
Device
OTP
Combination
```

A control based only on:

```text
IP address
```

may not adequately protect the account.

---

# Rate-Limit Reset

Check carefully whether obtaining a new challenge resets:

```text
Failed attempt counter
```

Example:

```text
Challenge A
3 failures
      ↓
Request Challenge B
      ↓
Attempt counter = 0?
```

Use only a few attempts.

---

# Header-Based Rate-Limit Bypass

Do not automatically assume headers such as:

```text
X-Forwarded-For
X-Real-IP
Forwarded
```

can bypass a rate limit.

Whether they matter depends on trusted proxy configuration.

For authorised testing, a small controlled comparison may identify whether attacker-controlled forwarding headers improperly influence rate-limit identity.

---

# Burp Intruder for OTP Testing

Burp Intruder can be useful for:

```text
Small controlled OTP sets
Response comparison
Rate-limit verification
Challenge-binding testing
```

Example payload position:

```http
POST /mfa/verify HTTP/1.1
Content-Type: application/json

{
    "code": "§000001§"
}
```

Use a small payload list:

```text
000001
000002
000003
VALID_CONTROLLED_CODE
```

This is usually sufficient to understand basic behaviour.

---

# Intruder Grep Match

Useful response indicators:

```text
invalid
incorrect
expired
locked
too many
success
verified
```

Also compare:

```text
Status
Length
Redirect
Set-Cookie
```

---

# Burp Comparer

Comparer is useful for:

```text
Valid vs invalid OTP
Expired vs invalid OTP
User A vs User B
Pre-MFA vs post-MFA responses
```

---

# Burp Repeater

Repeater should be the primary tool for MFA testing.

Use it for:

```text
Workflow bypass
Direct endpoint access
OTP replay
Challenge manipulation
Session comparison
Account binding
MFA reset
Remember-device testing
```

---

# Burp Sequencer

Sequencer can analyse the statistical quality of:

```text
Recovery tokens
Trusted-device tokens
Challenge identifiers
```

when enough samples can be safely collected.

It is generally less useful for standard TOTP codes because those are intentionally generated from a deterministic cryptographic algorithm.

---

# MFA Code Leakage

OTP values may leak through:

```text
API responses
Logs
Analytics
Debug endpoints
HTML
JavaScript
Push notification metadata
```

Example vulnerability:

```json
{
    "message": "OTP sent",
    "debugOtp": "381922"
}
```

Always inspect raw responses.

---

# OTP Returned by API

Development or test functionality sometimes returns:

```text
verificationCode
otp
debugCode
```

in the response.

Search JSON for:

```text
otp
code
verification
challenge
token
```

---

# Information Disclosure

Error responses may reveal:

```text
Correct account
MFA method
Phone number
Email address
Challenge state
MFA enabled status
```

Example:

```text
SMS sent to +31******42
```

Partially masked information may still aid user enumeration.

Refer to:

```text
docs/web/information-disclosure.md
```

---

# MFA Method Enumeration

The application may reveal:

```text
This user uses SMS MFA
```

versus:

```text
This user uses authenticator MFA
```

This may help attackers profile authentication controls.

Assess actual impact before reporting.

---

# SMS MFA

SMS-based MFA introduces additional risks beyond the web application itself:

```text
SIM swapping
Telecom account compromise
Message interception
Phone number reassignment
```

During web application testing, focus primarily on:

```text
Application workflow
Rate limiting
OTP binding
Recovery
Phone-number change
Session handling
```

Do not attempt attacks against telecommunications infrastructure.

---

# Email MFA

Email OTP security depends partly on:

```text
Security of the email account
```

Application testing should focus on:

```text
OTP entropy
Expiration
Binding
Replay
Rate limiting
Workflow
```

---

# Push MFA

Push authentication may use:

```text
Approve
Deny
```

notifications.

Potential concerns include:

```text
MFA fatigue
Repeated push generation
Weak number matching
Unclear transaction context
```

Testing should avoid generating excessive push notifications.

---

# MFA Fatigue

An attacker may repeatedly trigger:

```text
Push Notifications
```

hoping the user eventually approves one.

Applications can reduce this risk with:

```text
Number matching
Rate limiting
Transaction context
User reporting
Temporary lockout
Risk detection
```

During testing:

```text
Do not spam real users.
```

Use only controlled devices.

---

# Number Matching

A stronger push flow may display:

```text
42
```

in the login browser and require:

```text
42
```

to be selected or entered on the trusted device.

This helps reduce accidental approval.

---

# MFA Enrollment

MFA setup itself is a sensitive workflow.

Typical flow:

```text
Authenticated User
      ↓
Enable MFA
      ↓
Generate Secret
      ↓
Display QR Code
      ↓
Verify OTP
      ↓
MFA Enabled
```

Test:

```text
Reauthentication
CSRF protection
Secret exposure
Activation state
Account binding
Recovery code handling
```

---

# TOTP Secret

The TOTP secret is effectively a long-term authentication credential.

Example representation:

```text
otpauth://totp/Example:user@example.test?secret=...
```

Anyone possessing the secret may generate valid future OTPs.

Treat it like a password.

---

# QR Code Exposure

The QR code usually contains:

```text
TOTP secret
Issuer
Account name
Algorithm
Digits
Period
```

Do not include real TOTP secrets in reports.

Redact them.

---

# MFA Enrollment Without Reauthentication

If an attacker steals an authenticated session, they may attempt to enroll their own MFA device.

Sensitive operations such as:

```text
Enable MFA
Replace MFA
Add authenticator
```

may require recent authentication depending on the application's threat model.

---

# MFA Enrollment CSRF

If MFA setup can be triggered through CSRF, an attacker may potentially bind their own authenticator to the victim's account.

The exact exploitability depends on:

```text
Enrollment flow
Secret generation
Verification step
Session state
```

Refer to:

```text
docs/web/csrf.md
```

---

# MFA Secret Regeneration

Requesting the MFA setup page repeatedly may:

```text
Reuse same secret
Generate new secret
Invalidate previous secret
```

Understand the lifecycle.

Secrets should not remain exposed longer than necessary.

---

# Activation Verification

MFA should not normally become active until the user demonstrates possession of the authenticator by providing a valid code.

Conceptually:

```text
Generate Secret
      ↓
User Configures Device
      ↓
User Enters Valid OTP
      ↓
MFA Activated
```

---

# MFA Disable

Disabling MFA is security-sensitive.

Potential controls:

```text
Current password
Existing MFA
Recent authentication
Recovery code
Security notification
```

Test whether a partially authenticated session can call:

```text
POST /mfa/disable
```

---

# Direct MFA Disable Endpoint

Example:

```http
POST /api/account/mfa/disable HTTP/1.1
Cookie: session=PRE_MFA_SESSION
```

Expected:

```text
Denied
```

---

# MFA Disable CSRF

If disabling MFA requires only an authenticated session and lacks CSRF protection:

```text
Victim Browser
     ↓
Attacker-Controlled Request
     ↓
MFA Disabled
```

may be possible.

Refer to:

```text
docs/web/csrf.md
```

---

# MFA Reset

Applications often provide:

```text
Lost your authenticator?
```

or:

```text
Reset MFA
```

This recovery path must provide equivalent security.

Conceptually:

```text
Strong MFA
   ↓
Weak MFA Reset
   ↓
Effective MFA Security = Weak
```

---

# MFA Reset Channels

Common recovery methods:

```text
Email link
SMS
Recovery code
Support desk
Identity verification
Password
Alternative authenticator
```

Test each available route.

---

# Password-Only MFA Reset

A dangerous workflow may be:

```text
Password
   ↓
Reset MFA
   ↓
Enroll New Device
```

If an attacker already has the password:

```text
MFA provides little additional protection.
```

Whether this is a vulnerability depends on the intended security model.

---

# Password Reset Interaction

Password reset can unintentionally bypass MFA.

Test:

```text
MFA-enabled controlled account
        ↓
Password Reset
        ↓
New Password
        ↓
What Happens Next?
```

Possible outcomes:

```text
MFA still required
Fully authenticated automatically
MFA disabled
Trusted device created
Recovery state persists
```

Refer to:

```text
docs/web/password-reset.md
```

---

# Automatic Login After Password Reset

A particularly important test:

```text
Reset Password
      ↓
Application Automatically Logs User In
      ↓
MFA Required?
```

If not:

```text
Password Recovery
```

may become an MFA bypass.

---

# Recovery Codes

Recovery codes provide an alternative authentication path.

Example:

```text
ABCD-EFGH
JKLM-NPQR
STUV-WXYZ
```

They should normally be:

```text
Random
Single use
Account bound
Stored securely
Revocable
Protected from disclosure
```

---

# Recovery Code Replay

Use a controlled recovery code:

```text
Code A
  ↓
Authenticate
  ↓
Try Code A Again
```

Expected:

```text
Rejected
```

---

# Recovery Code Binding

With two controlled accounts:

```text
Recovery Code A
+
Account B Session
```

must fail.

---

# Recovery Code Storage

Recovery codes should ideally be stored similarly to passwords:

```text
Hash(Code)
```

rather than plaintext where practical.

---

# Recovery Code Disclosure

Check whether codes appear in:

```text
API responses
Page source
JavaScript
Logs
Browser storage
Analytics
```

after initial generation.

---

# Regenerating Recovery Codes

When new recovery codes are generated:

```text
Old Recovery Codes
```

should normally become invalid.

---

# Downloadable Recovery Codes

Applications may allow:

```text
Download Recovery Codes
```

Check:

```text
Cache-Control
Content-Disposition
Authentication
Reauthentication
```

and whether the file contains unnecessary sensitive information.

---

# Remember Device

Many MFA implementations support:

```text
Remember this device
```

or:

```text
Trust this browser for 30 days
```

This usually creates a long-lived token.

Architecture:

```text
Successful MFA
      ↓
Remember Device Selected
      ↓
Trusted Device Token
      ↓
Future Login
      ↓
MFA Skipped
```

That token effectively becomes:

```text
An MFA bypass credential
```

and must be protected accordingly.

---

# Trusted Device Cookie

Example:

```http
Set-Cookie: trusted_device=TOKEN
```

Inspect:

```text
Entropy
Expiration
Secure
HttpOnly
SameSite
Domain
Path
Account binding
Device binding
Revocation
```

---

# Predictable Trusted Device Tokens

Do not assume a long cookie is secure.

Check whether it contains:

```text
User ID
Timestamp
Username
Static hash
```

Burp Decoder can help inspect its structure.

---

# Trusted Device Account Binding

With controlled accounts:

```text
Trusted Token A
+
Login as User B
```

must not suppress User B's MFA.

---

# Trusted Device Token Replay

Copy the trusted-device cookie to:

```text
Another browser profile
```

using your own controlled account.

Determine whether the token is simply a bearer credential.

This may be expected.

The important questions are:

```text
Is it sufficiently unpredictable?

Is it securely stored?

Can it be revoked?

Is it account bound?

Does it expire?

Does password reset invalidate it?
```

---

# Trusted Device Lifetime

Check whether:

```text
Trust this device for 30 days
```

is actually enforced server-side.

Do not rely only on cookie expiration.

---

# Trusted Device Revocation

Test whether trusted-device tokens become invalid after:

```text
Password change
Password reset
MFA reset
MFA disable
Account security reset
Manual device revocation
```

depending on intended policy.

---

# Trusted Device and XSS

If a trusted-device token is accessible to JavaScript because:

```text
HttpOnly
```

is missing, an XSS vulnerability may potentially steal it.

However:

```text
HttpOnly
```

cannot protect against every consequence of XSS.

Refer to:

```text
docs/web/xss.md
```

---

# Session Management

MFA is tightly connected to session security.

Compare:

```text
Pre-MFA Session
Post-MFA Session
```

Look for:

```text
Session rotation
Authentication level
Expiration
Privilege state
```

Refer to:

```text
docs/web/session-management.md
```

---

# Session Fixation

A strong design often rotates authentication state when the user's authentication level increases.

Conceptually:

```text
Anonymous Session
       ↓
Password Authentication
       ↓
New / Upgraded Session
       ↓
MFA
       ↓
New / Upgraded Fully Authenticated Session
```

Exact implementation varies.

---

# Pre-MFA Session Reuse

Capture:

```text
PRE_MFA_SESSION
```

Then complete MFA.

Afterwards test whether the old pre-MFA session unexpectedly gained:

```text
Full authentication
```

without being properly upgraded or rotated.

---

# Multiple Browser Test

Useful workflow:

```text
Browser A
Password Login
Stop at MFA
Save Session A

Browser B
Use Same Account
Complete MFA

Return to Session A
```

Question:

```text
Did Session A become fully authenticated merely because MFA was completed elsewhere?
```

The expected behaviour depends on how authentication challenges are bound.

This can reveal weak:

```text
Account-level MFA state
```

instead of:

```text
Session-level authentication state
```

---

# Challenge vs Account State

Dangerous implementation:

```text
User.mfa_verified = true
```

globally after one successful challenge.

Safer model:

```text
Authentication Session A
    ↓
MFA verified for Session A
```

Other login attempts should not automatically inherit that state.

---

# Parallel MFA Attempts

Create two controlled login attempts:

```text
Session A
Session B
```

Both stop at MFA.

Complete MFA in:

```text
Session A
```

Then test:

```text
Session B
```

Session B should not become authenticated unless the application intentionally and securely binds both attempts.

---

# Race Conditions

MFA workflows may contain race conditions.

Example:

```text
Recovery Code
     ↓
Request A validates
Request B validates
     ↓
Both execute before code marked used
```

Potential result:

```text
Single-use code used twice
```

Refer to:

```text
docs/web/race-conditions.md
```

---

# Safe Race Testing

Use:

```text
Controlled account
Controlled recovery code
Two or a very small number of requests
```

Burp Repeater request groups are useful.

---

# Burp Repeater Parallel Requests

For appropriate endpoints:

```text
Create request group
      ↓
Add two controlled requests
      ↓
Send in parallel
```

This can test:

```text
Recovery code reuse
Single-use challenge
MFA reset race
```

without high request volume.

---

# Turbo Intruder

For specialised timing-sensitive MFA testing, Turbo Intruder can assist.

Useful cases may include:

```text
Single-use token races
Recovery-code races
Challenge state races
```

Official BApp Store:

https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988

GitHub:

https://github.com/PortSwigger/turbo-intruder

Use it conservatively.

Standard MFA testing rarely requires high request rates.

---

# Authentication Endpoint Discovery

Search JavaScript and source files for:

```text
mfa
2fa
otp
totp
hotp
authenticator
verification
challenge
recovery
backup
trusted
remember
device
factor
```

Example:

```bash
grep -RniE \
'mfa|2fa|otp|totp|hotp|authenticator|verification|challenge|recovery|backup.?code|trusted.?device|remember.?device' \
.
```

---

# Common MFA Endpoints

Look for:

```text
/mfa
/2fa
/otp
/mfa/verify
/2fa/verify
/otp/verify
/mfa/setup
/mfa/enable
/mfa/disable
/mfa/reset
/mfa/recovery
/mfa/backup-codes
/api/mfa
/api/auth/mfa
/api/auth/verify-otp
```

---

# JavaScript Analysis

Search frontend JavaScript for:

```text
mfaRequired
mfaVerified
otpRequired
otpVerified
authLevel
challengeId
trustedDevice
rememberDevice
```

These may reveal:

```text
Hidden API endpoints
Workflow states
Parameter names
Alternative MFA methods
```

Refer to:

```text
docs/web/reconnaissance/javascript-analysis.md
```

---

# API Documentation

Inspect:

```text
Swagger
OpenAPI
GraphQL
Mobile API endpoints
```

for MFA functionality not exposed by the normal UI.

Examples:

```text
POST /api/mfa/disable
POST /api/mfa/reset
POST /api/mfa/verify
POST /api/mfa/recovery
```

---

# GraphQL MFA

GraphQL applications may expose mutations such as:

```graphql
mutation {
    verifyMfa(
        code: "CONTROLLED_CODE"
    ) {
        success
    }
}
```

or:

```graphql
mutation {
    disableMfa {
        success
    }
}
```

Test the same:

```text
Authentication
Authorisation
Workflow
Binding
Rate limiting
```

principles.

Refer to:

```text
docs/web/graphql.md
```

---

# WebSocket Authentication

If an application uses WebSockets after login, determine whether:

```text
Pre-MFA session
```

can establish an authenticated WebSocket connection.

Refer to:

```text
docs/web/websockets.md
```

---

# Mobile APIs

Mobile applications may use a different authentication flow.

Potential issue:

```text
Web Login
Requires MFA

Legacy Mobile API
Does Not Require MFA
```

All authentication channels should enforce the intended security policy.

---

# Legacy APIs

Look for:

```text
/v1/login
/v2/login
/mobile/login
/api/legacy/auth
```

A legacy endpoint may accept:

```text
Username
Password
```

and return a fully authenticated token without MFA.

---

# Alternative Login Methods

Test available authentication mechanisms:

```text
Password
SSO
OAuth
Magic link
API login
Mobile login
Recovery
```

MFA may be enforced on one path but missing from another.

---

# OAuth and MFA

Applications using OAuth or OpenID Connect may delegate MFA to an identity provider.

Architecture:

```text
Application
    ↓
Identity Provider
    ↓
Password
    ↓
MFA
    ↓
OIDC Token
    ↓
Application
```

The application may rely on claims such as:

```text
amr
acr
```

to determine authentication strength.

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# SAML and MFA

Enterprise applications may use SAML assertions to communicate authentication context.

The application should not simply assume:

```text
SSO Login
=
MFA Completed
```

unless that assurance is provided and validated according to the intended architecture.

---

# MFA Downgrade

Look for ways to change:

```text
TOTP
```

to a weaker mechanism such as:

```text
Email OTP
SMS
Security question
```

without adequate verification.

A downgrade may undermine the stronger factor.

---

# Alternative Factor Selection

Example:

```text
Use another method
```

may expose:

```text
SMS
Email
Recovery code
Push
```

Test each independently.

The overall security is often determined by:

```text
Weakest Available Recovery Factor
```

---

# MFA Factor Replacement

Changing the registered:

```text
Phone number
Email
Authenticator
Hardware key
```

is security-sensitive.

Test whether replacement requires:

```text
Current factor
Password
Recent authentication
```

according to application policy.

---

# Phone Number Change

A chain may be:

```text
Session Compromise
      ↓
Change Phone Number
      ↓
Receive MFA OTP
      ↓
Permanent Account Access
```

Phone number changes deserve strong verification.

---

# Email Change

If email is an MFA factor:

```text
Change Email
```

can become:

```text
Change MFA Destination
```

Refer to:

```text
docs/web/business-logic.md
```

and:

```text
docs/web/password-reset.md
```

---

# Factor Deletion

Applications supporting multiple factors may allow:

```text
Delete Authenticator
Delete Hardware Key
Delete Phone
```

Test whether the last strong factor can be removed without appropriate verification.

---

# WebAuthn and Passkeys

WebAuthn provides phishing-resistant public-key authentication.

Conceptually:

```text
Server Challenge
      ↓
Authenticator
      ↓
Private Key Signature
      ↓
Server Verifies Public Key
```

Unlike OTPs:

```text
Private key
```

does not leave the authenticator.

---

# WebAuthn Testing Areas

Relevant areas include:

```text
Registration
Authentication
Challenge randomness
Challenge expiration
Challenge binding
Origin validation
RP ID validation
Credential binding
User verification
Credential deletion
Recovery
```

---

# WebAuthn Challenge

The server sends a random challenge.

Example conceptual structure:

```json
{
    "challenge": "RANDOM_VALUE",
    "rpId": "target.example"
}
```

The challenge should be:

```text
Unpredictable
Short-lived
Single-use
Bound to authentication ceremony
```

---

# WebAuthn Origin

The server validates the origin associated with the authentication ceremony.

This helps make WebAuthn resistant to traditional phishing.

---

# WebAuthn RP ID

The relying party identifier defines the domain scope of the credential.

Incorrect RP ID validation can undermine the security model.

---

# Passkeys

Passkeys use WebAuthn credentials and may be:

```text
Device-bound
Synced across trusted devices
```

depending on provider and platform.

Application testing should focus on:

```text
Registration
Authentication
Credential management
Recovery
Account binding
```

rather than attempting to attack the authenticator platform itself.

---

# Hardware Security Keys

Hardware security keys commonly use:

```text
FIDO2
WebAuthn
```

They provide strong phishing resistance.

However, the application's:

```text
Recovery path
Factor removal
Alternative factor
```

may still weaken overall security.

---

# Step-Up Authentication

Some applications require additional authentication only for sensitive actions.

Example:

```text
Normal Session
     ↓
View Dashboard
     ↓
Transfer Money
     ↓
Require MFA
```

This is:

```text
Step-Up Authentication
```

---

# Step-Up Bypass

Test whether the protected action can be called directly.

Example:

```http
POST /api/payment HTTP/1.1
Cookie: session=VALID_SESSION
```

without completing the step-up challenge.

Expected:

```text
Denied
```

---

# Step-Up State

Do not trust:

```text
UI navigation
```

to enforce step-up authentication.

The backend should verify:

```text
Recent MFA
Authentication strength
Transaction context
```

---

# Step-Up Lifetime

Determine how long:

```text
Recently MFA Verified
```

remains valid.

Potential issue:

```text
MFA completed months ago
```

still satisfies a sensitive transaction requiring recent authentication.

---

# Transaction Binding

For high-risk operations, MFA may need to be bound to:

```text
Specific transaction
Amount
Destination
Action
```

rather than simply:

```text
User authenticated with MFA at some point
```

---

# Transaction Authorisation

Conceptually:

```text
Transfer €100
to Account B
      ↓
MFA Challenge
      ↓
Authorise
      ↓
Transfer €100
to Account B
```

A vulnerability may exist if the attacker can change:

```text
€100
```

to:

```text
€10,000
```

or change the destination after MFA approval.

This is broader than login MFA and relates to transaction authorisation.

---

# MFA and IDOR / BOLA

MFA endpoints may contain:

```text
userId
factorId
challengeId
deviceId
```

Test whether these objects are correctly authorised.

Example:

```http
DELETE /api/mfa/factors/812
```

A user must not be able to delete another user's factor.

Refer to:

```text
docs/web/idor-bola.md
```

---

# MFA and Mass Assignment

Example:

```json
{
    "code": "123456",
    "verified": true,
    "authLevel": 2
}
```

Unexpected fields should not alter authentication state.

Refer to:

```text
docs/web/mass-assignment.md
```

---

# MFA and Race Conditions

Relevant targets include:

```text
Recovery codes
One-time challenges
MFA disable
MFA enrollment
Factor replacement
```

Refer to:

```text
docs/web/race-conditions.md
```

---

# MFA and CSRF

High-value MFA-related CSRF targets include:

```text
Enable MFA
Disable MFA
Replace MFA factor
Change MFA phone number
Generate recovery codes
Trust device
```

Refer to:

```text
docs/web/csrf.md
```

---

# MFA and XSS

XSS may potentially:

```text
Perform actions in authenticated session
Manipulate MFA enrollment
Access non-HttpOnly tokens
Alter transaction context
```

MFA does not eliminate XSS risk.

Refer to:

```text
docs/web/xss.md
```

---

# MFA and Business Logic

MFA is fundamentally a stateful business workflow.

Ask:

```text
Can steps be skipped?

Can another session inherit MFA state?

Can factors be downgraded?

Can recovery bypass the factor?

Can the target account change?

Can MFA be disabled directly?

Can trusted-device state be forged?

Can the transaction change after approval?
```

Refer to:

```text
docs/web/business-logic.md
```

---

# Burp Suite Testing Workflow

Recommended workflow:

```text
Controlled MFA Account
        ↓
Burp Proxy
        ↓
Perform Normal Login
        ↓
Save Pre-MFA Session
        ↓
Complete MFA
        ↓
Save Post-MFA Session
        ↓
Burp Comparer
        ↓
Identify State Differences
        ↓
Return to Pre-MFA Session
        ↓
Request Protected Resources
        ↓
Test API Endpoints
        ↓
Test Workflow Skipping
        ↓
Test OTP Binding
        ↓
Test Challenge Binding
        ↓
Test Rate Limiting
        ↓
Test Recovery Codes
        ↓
Test Remember Device
        ↓
Test MFA Reset / Disable
        ↓
Test Password Reset
        ↓
Test Alternative Login Paths
        ↓
Test Step-Up Actions
        ↓
Test Parallel Sessions
        ↓
Verify Minimal Impact
        ↓
Report
```

---

# Autorize

Autorize is useful when MFA interacts with protected application endpoints.

It can help identify requests that remain accessible using:

```text
Lower-privileged
Unauthenticated
Partially authenticated
```

contexts.

For MFA testing, manual verification is still essential because the important distinction may be:

```text
Password-authenticated session
```

versus:

```text
Fully MFA-authenticated session
```

rather than simply authenticated versus unauthenticated.

---

# AuthMatrix

AuthMatrix can be useful for building a matrix such as:

| Request | Unauthenticated | Pre-MFA | Post-MFA |
|---|---:|---:|---:|
| Dashboard | Deny | Deny | Allow |
| Account API | Deny | Deny | Allow |
| MFA Verify | Deny | Allow | N/A |
| MFA Disable | Deny | Deny | Allow |
| Admin API | Deny | Deny | Role dependent |

This is a particularly useful conceptual model for MFA testing.

---

# Session Token Analysis

Useful tools:

```text
Burp Decoder
Burp Comparer
Burp Sequencer
JWT tooling
Browser DevTools
```

Compare:

```text
Pre-MFA
Post-MFA
Remembered Device
Recovery Login
Password Reset Login
```

---

# Burp Logger

Logger can help review all authentication-related traffic.

Filter for:

```text
mfa
2fa
otp
verify
challenge
factor
recovery
trusted
device
```

This is useful when the workflow makes many background API calls.

---

# Browser DevTools

Useful tabs:

```text
Network
Application
Sources
Console
```

Inspect:

```text
Cookies
LocalStorage
SessionStorage
IndexedDB
JavaScript
API calls
WebAuthn requests
```

---

# Testing Matrix

| Test | Pre-MFA | Post-MFA | Expected |
|---|---|---|---|
| Dashboard | Attempt | Access | Deny / Allow |
| Account API | Attempt | Access | Deny / Allow |
| Profile | Attempt | Access | Deny / Allow |
| MFA Disable | Attempt | Access | Deny / Controlled |
| Sensitive action | Attempt | Access | Deny / Allow |
| WebSocket | Attempt | Access | Deny / Allow |

---

# Factor Matrix

| Authentication Path | Password | MFA | Expected Assurance |
|---|---:|---:|---|
| Normal login | Yes | Yes | Full |
| Password reset | Recovery | Yes | Full |
| Remember device | Yes | Trusted token | Full |
| Recovery code | Yes / policy | Recovery code | Full |
| SSO | IdP | IdP policy | Full |
| Legacy API | Yes | Required | Full |
| Mobile API | Yes | Required | Full |

The objective is to identify paths where:

```text
MFA unexpectedly disappears.
```

---

# MFA Attack Surface Checklist

## Authentication State

```text
[ ] Pre-MFA session captured
[ ] Post-MFA session captured
[ ] Session differences compared
[ ] Protected resources tested before MFA
[ ] API endpoints tested before MFA
[ ] WebSocket access tested where relevant
[ ] Authentication level verified server-side
```

## Workflow

```text
[ ] MFA page cannot be skipped
[ ] Verification endpoint required
[ ] Completion endpoint cannot be called directly
[ ] Client-side state not trusted
[ ] Hidden fields not trusted
[ ] Response manipulation verified server-side
```

## OTP

```text
[ ] Correct OTP
[ ] Invalid OTP
[ ] Expired OTP
[ ] Replay
[ ] Account binding
[ ] Session binding
[ ] Challenge binding
[ ] Rate limiting
[ ] Attempt limits
[ ] Challenge expiration
```

## MFA Enrollment

```text
[ ] Reauthentication considered
[ ] CSRF protection
[ ] TOTP secret protected
[ ] QR code protected
[ ] Activation requires verification
[ ] Secret lifecycle understood
```

## MFA Disable

```text
[ ] Authentication required
[ ] Recent authentication considered
[ ] Existing MFA verification considered
[ ] CSRF protection
[ ] Direct API access tested
[ ] User notification
```

## MFA Recovery

```text
[ ] Recovery mechanism identified
[ ] Password-only reset assessed
[ ] Email recovery assessed
[ ] SMS recovery assessed
[ ] Recovery code assessed
[ ] Support recovery assessed
[ ] Recovery preserves intended MFA assurance
```

## Recovery Codes

```text
[ ] Randomness
[ ] Single use
[ ] Account binding
[ ] Replay
[ ] Regeneration invalidates old codes
[ ] Secure storage
[ ] Disclosure
```

## Remember Device

```text
[ ] Trusted-device token identified
[ ] Entropy
[ ] Account binding
[ ] Expiration
[ ] Secure
[ ] HttpOnly
[ ] SameSite
[ ] Revocation
[ ] Password reset interaction
[ ] MFA reset interaction
```

## Sessions

```text
[ ] Pre-MFA session remains restricted
[ ] Session rotation
[ ] Parallel login attempts
[ ] MFA state is session-bound
[ ] Existing sessions after MFA reset
```

## Alternative Authentication

```text
[ ] Password reset
[ ] OAuth
[ ] OIDC
[ ] SAML
[ ] Mobile API
[ ] Legacy API
[ ] Magic link
[ ] Recovery login
```

## Step-Up Authentication

```text
[ ] Sensitive actions identified
[ ] Direct endpoint access tested
[ ] Step-up state server-side
[ ] Step-up expiration
[ ] Transaction binding
```

## WebAuthn / Passkeys

```text
[ ] Registration
[ ] Authentication
[ ] Challenge binding
[ ] Challenge expiration
[ ] Origin validation
[ ] RP ID validation
[ ] Credential management
[ ] Recovery
```

## Related Vulnerabilities

```text
[ ] IDOR / BOLA
[ ] Mass Assignment
[ ] CSRF
[ ] Race Conditions
[ ] Business Logic
[ ] Session Management
[ ] JWT
[ ] OAuth / OIDC
[ ] Password Reset
[ ] Information Disclosure
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Comparer
[ ] Decoder
[ ] Logger
[ ] Intruder where appropriate
[ ] Sequencer where appropriate
[ ] Turbo Intruder where justified
[ ] Autorize where useful
[ ] AuthMatrix where useful
```

## Safety

```text
[ ] Controlled account
[ ] Controlled authenticator
[ ] Controlled email
[ ] Controlled phone where applicable
[ ] No real-user OTP attempts
[ ] No SMS flooding
[ ] No push flooding
[ ] No uncontrolled brute force
[ ] Recovery codes restored/regenerated if needed
```

---

# High-Value Tests

Prioritise:

```text
Direct protected-resource access before MFA

API access before MFA

MFA verification step skipping

Pre-MFA session becoming fully authenticated

OTP not bound to account

OTP not bound to challenge

No OTP rate limiting

Recovery code reuse

MFA reset using password only

MFA disable without reauthentication

Password reset bypassing MFA

Legacy API bypassing MFA

Trusted-device token weaknesses

Step-up authentication bypass

Cross-session MFA state inheritance
```

---

# False Positive: UI Access

Seeing:

```text
/dashboard
```

after modifying frontend behaviour does not prove MFA bypass.

You need:

```text
Protected server-side data
```

or:

```text
Protected server-side action
```

to demonstrate impact.

---

# False Positive: Different Session Cookie

A new cookie after MFA is not automatically secure.

Verify what each cookie can actually access.

---

# False Positive: Same Session Cookie

Using the same session identifier before and after MFA is not automatically vulnerable either.

The server may securely store:

```text
Authentication Level
```

server-side.

Test behaviour rather than assuming.

---

# False Positive: OTP Reuse During Same Time Window

TOTP implementations may intentionally accept the same code more than once during a short validity window.

Assess:

```text
Threat model
Transaction type
Application design
```

before reporting.

---

# False Positive: SMS MFA

SMS is generally considered less phishing-resistant than stronger mechanisms such as WebAuthn.

Its use alone is not necessarily an application vulnerability.

Report concrete implementation weaknesses.

---

# Evidence Collection

Strong MFA evidence includes:

```text
Controlled account
Normal login flow
Pre-MFA session
Protected request
Protected response
MFA verification request
Post-MFA session
API request
State comparison
Screenshots
Burp history
Timeline
```

For OTP findings:

```text
Challenge identifier
Small controlled attempt set
Rate-limit behaviour
Account state
```

Redact:

```text
Passwords
TOTP secrets
Recovery codes
Session tokens
Personal information
```

where not required.

---

# Example Finding: MFA Workflow Bypass

```text
Finding:
Multi-Factor Authentication Can Be Bypassed Through Direct Endpoint Access

Observed:
A controlled account with MFA enabled was used during testing.

After submitting the correct username and password, the application redirected the browser to the MFA verification page.

Before supplying the second authentication factor, the partially authenticated session was used to request the authenticated account endpoint directly.

The server returned the protected account data without requiring successful MFA verification.

Impact:
An attacker who obtains a user's password can bypass the configured second authentication factor and gain access to the user's account.

This defeats the primary security objective of MFA.

Recommendation:
Track MFA completion as part of server-side authentication state and enforce the required authentication level on every protected endpoint. Partially authenticated sessions must not be authorised to access normal authenticated functionality.
```

---

# Example Finding: MFA Missing from API

```text
Finding:
Application API Does Not Enforce Multi-Factor Authentication

Observed:
The web interface correctly required MFA after password authentication.

However, the access token issued before MFA completion could be used directly against authenticated API endpoints.

The API returned protected user information while the account remained in the MFA-pending state.

Impact:
An attacker possessing valid account credentials can bypass MFA by interacting directly with the backend API.

Recommendation:
Enforce authentication assurance consistently at the backend API layer. Tokens issued before MFA completion should either have limited scope or be rejected by endpoints requiring fully authenticated users.
```

---

# Example Finding: Cross-Account OTP

```text
Finding:
MFA Verification Codes Are Not Bound to the Target Account

Observed:
Two controlled MFA-enabled accounts were used.

A valid OTP generated for User A was submitted using the MFA authentication session belonging to User B.

The application accepted the OTP and completed authentication for User B.

Impact:
An attacker able to obtain a valid MFA code for their own account may be able to use that code to satisfy another user's MFA challenge.

This may allow bypass of multi-factor authentication and account takeover.

Recommendation:
Bind each MFA challenge and verification code to the correct account, authentication session, and authentication attempt. The server should derive the target identity from trusted authentication state rather than client-controlled parameters.
```

---

# Example Finding: MFA OTP Lacks Rate Limiting

```text
Finding:
MFA Verification Endpoint Lacks Effective Rate Limiting

Observed:
Multiple incorrect OTP values were submitted against a controlled account.

The application continued accepting verification attempts without meaningful delay, challenge invalidation, temporary lockout, or other effective attempt restrictions.

Impact:
An attacker who obtains a user's password may be able to systematically guess the second authentication factor.

For short numeric OTPs, insufficient online guessing protections can significantly reduce the effective security provided by MFA.

Recommendation:
Apply strict server-side attempt limits to MFA challenges. Bind limits to the account and authentication challenge, use short challenge lifetimes, invalidate challenges after excessive failures, and implement additional abuse detection where appropriate.
```

---

# Example Finding: Password Reset Bypasses MFA

```text
Finding:
Password Reset Workflow Bypasses Multi-Factor Authentication

Observed:
A controlled account with MFA enabled was used.

After completing the password reset process, the application automatically established a fully authenticated session without requiring the configured second authentication factor.

Impact:
An attacker who gains access to the password recovery channel can bypass MFA entirely.

Recommendation:
Ensure password recovery does not automatically satisfy independent MFA requirements unless the recovery process itself provides equivalent assurance. Require the configured second factor before establishing a fully authenticated session.
```

---

# Example Finding: MFA Reset Requires Only Password

```text
Finding:
Multi-Factor Authentication Can Be Reset Using Only the Account Password

Observed:
A controlled account with MFA enabled was used.

After authenticating with the account password, the MFA recovery functionality allowed the existing authenticator to be removed and a new authenticator to be registered without requiring the existing factor or an equivalently strong recovery mechanism.

Impact:
An attacker who obtains the user's password can remove the protection provided by MFA and register an attacker-controlled authentication factor.

Recommendation:
Protect MFA reset and replacement using a recovery mechanism that provides assurance appropriate to the account risk. Consider requiring an existing factor, recovery code, verified recovery channel, recent strong authentication, or additional identity verification.
```

---

# Example Finding: Recovery Code Reuse

```text
Finding:
MFA Recovery Codes Can Be Reused

Observed:
A recovery code generated for a controlled account was successfully used to satisfy MFA.

The same recovery code remained valid and could be used again.

Impact:
An attacker who obtains a previously used recovery code may retain persistent access to the account.

Recommendation:
Treat recovery codes as single-use authentication credentials. Invalidate each code atomically after successful use and provide users with functionality to regenerate and revoke recovery codes.
```

---

# Example Finding: MFA State Shared Across Sessions

```text
Finding:
MFA Verification State Is Incorrectly Shared Across Authentication Sessions

Observed:
Two independent login sessions were created for the same controlled account.

Both sessions successfully completed password authentication and stopped at the MFA challenge.

MFA was then completed only in Session A.

Without submitting an MFA code in Session B, Session B subsequently gained access to protected application functionality.

Impact:
An attacker who knows a user's password may be able to maintain a partially authenticated session and have it automatically upgraded when the legitimate user completes MFA in another session.

Recommendation:
Bind MFA completion to the specific authentication session and challenge that successfully completed verification. Do not maintain MFA verification as a global account-level flag for independent login attempts.
```

---

# Example Finding: Trusted Device Token Not Account Bound

```text
Finding:
Trusted Device Token Can Suppress MFA for Other Accounts

Observed:
A trusted-device token was generated after successfully completing MFA for controlled User A.

The same trusted-device token was subsequently supplied while authenticating as controlled User B.

The application suppressed User B's MFA challenge.

Impact:
An attacker who obtains or creates a trusted-device token may be able to bypass MFA for other accounts.

Recommendation:
Cryptographically bind trusted-device tokens to the intended account and security context. Tokens should be unpredictable, revocable, time-limited, and validated server-side.
```

---

# Reporting Titles

Useful titles include:

```text
Multi-Factor Authentication Can Be Bypassed Through Direct Endpoint Access

Application API Does Not Enforce Multi-Factor Authentication

MFA Verification Codes Are Not Bound to the Target Account

MFA Verification Endpoint Lacks Effective Rate Limiting

MFA Verification State Is Shared Across Authentication Sessions

Password Reset Workflow Bypasses Multi-Factor Authentication

Multi-Factor Authentication Can Be Reset Using Only the Account Password

MFA Recovery Codes Can Be Reused

Trusted Device Token Is Not Bound to the User Account

MFA Can Be Disabled Without Reauthentication

MFA Enrollment Does Not Require Reauthentication

Legacy Authentication Endpoint Bypasses MFA

Step-Up Authentication Can Be Bypassed

MFA Recovery Mechanism Provides Weaker Authentication Assurance
```

---

# Severity

Severity depends on actual impact.

Examples:

```text
Minor MFA information disclosure
→ Low

Weak security notification
→ Low

Long trusted-device lifetime
→ Low / Medium

Missing reauthentication for MFA settings
→ Medium / High

Recovery code reuse
→ Medium / High

Weak MFA recovery
→ High

OTP brute force
→ High

Direct MFA bypass
→ High / Critical

API MFA bypass
→ High / Critical

Cross-account OTP acceptance
→ Critical / High

Legacy login bypass
→ High / Critical
```

The most important question is:

```text
Can an attacker with only the first factor
obtain access that should require MFA?
```

---

# Remediation

A secure MFA implementation should enforce:

```text
Server-side authentication state
Session-specific MFA state
Challenge binding
Account binding
Short challenge lifetimes
Attempt limits
Strong recovery
Secure trusted-device tokens
Secure enrollment
Secure factor replacement
Secure factor removal
Consistent API enforcement
Consistent alternative-login enforcement
```

---

# Enforce MFA Server-Side

Every protected backend endpoint should verify the required authentication assurance.

Do not rely on:

```text
Frontend routing
JavaScript
Hidden fields
Client-controlled cookies
LocalStorage
```

---

# Separate Partial and Full Authentication

Model authentication explicitly:

```text
Unauthenticated

Password Authenticated

MFA Authenticated
```

Each state should have clearly defined privileges.

---

# Restrict Pre-MFA Sessions

A pre-MFA session should normally be able to access only functionality required to:

```text
Complete MFA
Cancel login
Recover MFA
Logout
```

It should not have general account access.

---

# Bind Challenges

Bind MFA challenges to:

```text
Account
Authentication session
Authentication attempt
Purpose
Expiration
```

---

# Apply Attempt Limits

Protect OTP verification with:

```text
Server-side rate limiting
Attempt counters
Challenge invalidation
Monitoring
```

---

# Protect Recovery

Recovery should not be significantly weaker than MFA itself.

---

# Secure Trusted Devices

Trusted-device tokens should be:

```text
Cryptographically random
Account bound
Time limited
Revocable
Securely stored
```

and protected using appropriate cookie attributes.

---

# Secure Enrollment

Protect MFA enrollment with:

```text
Authenticated session
Recent authentication where appropriate
CSRF protection
Verification of new factor
Security notification
```

---

# Secure MFA Disable

Protect MFA removal using:

```text
Strong authentication
Existing factor where appropriate
Recent authentication
CSRF protection
Security notification
```

---

# Protect Recovery Codes

Recovery codes should be:

```text
Random
Single use
Securely stored
Revocable
Regeneratable
```

---

# Preserve MFA During Password Reset

Password reset should not automatically:

```text
Disable MFA
Create fully authenticated session
Create trusted device
```

unless the recovery process intentionally provides equivalent assurance.

---

# Enforce MFA Across APIs

Apply the same policy to:

```text
Web
REST APIs
GraphQL
WebSockets
Mobile APIs
Legacy APIs
```

---

# Protect Step-Up Authentication

Sensitive operations should verify:

```text
Recent authentication
Required authentication strength
Transaction context
```

server-side.

---

# Monitor MFA Events

Log:

```text
MFA success
MFA failure
MFA reset
MFA disable
New factor
Removed factor
Recovery code use
Trusted device creation
Repeated failures
```

without logging:

```text
TOTP secrets
Recovery codes
OTP values
```

---

# Notify Users

Notify users about important events such as:

```text
MFA enabled
MFA disabled
Authenticator changed
Recovery codes regenerated
Trusted device added
MFA recovery completed
```

---

# References

## OWASP Multifactor Authentication Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html

Primary OWASP guidance for implementing and recovering multi-factor authentication.

---

## OWASP Authentication Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

General authentication guidance.

---

## OWASP Forgot Password Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html

Important for understanding interactions between account recovery and MFA.

---

## OWASP Session Management Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

Relevant to pre-MFA and post-MFA session handling.

---

## OWASP Transaction Authorization Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html

Relevant to step-up authentication and transaction-specific authorisation.

---

## PortSwigger Authentication Vulnerabilities

https://portswigger.net/web-security/authentication

PortSwigger Web Security Academy material covering authentication weaknesses.

---

## PortSwigger 2FA Bypass

https://portswigger.net/web-security/authentication/multi-factor

PortSwigger material covering multi-factor authentication vulnerabilities and testing concepts.

---

## PortSwigger Race Conditions

https://portswigger.net/web-security/race-conditions

Relevant for single-use recovery tokens and MFA workflow races.

---

## PortSwigger Turbo Intruder

https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988

Useful for specialised race-condition and timing-sensitive testing.

GitHub:

https://github.com/PortSwigger/turbo-intruder

---

## WebAuthn

https://www.w3.org/TR/webauthn-3/

Web Authentication specification.

---

## FIDO Alliance

https://fidoalliance.org/

Background information about FIDO authentication standards.

---

# Final MFA Testing Model

```text
                              MFA
                               ↓
                      NORMAL LOGIN BASELINE
                               ↓
                  PASSWORD FACTOR COMPLETED
                               ↓
                    PRE-MFA AUTHENTICATION
                               ↓
             ┌─────────────────┼──────────────────┐
             ↓                 ↓                  ↓
         SESSION             TOKEN               API
             ↓                 ↓                  ↓
       RESTRICTED?       MFA STATE?          RESTRICTED?
             └─────────────────┼──────────────────┘
                               ↓
                         MFA CHALLENGE
                               ↓
              ┌────────────────┼─────────────────┐
              ↓                ↓                 ↓
             OTP          CHALLENGE ID       RECOVERY
              ↓                ↓                 ↓
           ENTROPY           BINDING          SECURITY
              ↓                ↓                 ↓
        RATE LIMITING      EXPIRATION        SINGLE USE
              └────────────────┼─────────────────┘
                               ↓
                        MFA VERIFICATION
                               ↓
                     SERVER-SIDE ENFORCED?
                          ↓            ↓
                         YES           NO
                          ↓            ↓
                     CONTINUE       BYPASS
                          ↓
                   POST-MFA SESSION
                          ↓
                AUTHENTICATION UPGRADE
                          ↓
              ┌───────────┼────────────┐
              ↓           ↓            ↓
           SESSION       API        WEBSOCKET
              ↓           ↓            ↓
             FULL        FULL         FULL
             MFA?        MFA?         MFA?
              └───────────┼────────────┘
                          ↓
                    MFA MANAGEMENT
                          ↓
       ┌──────────────────┼────────────────────┐
       ↓                  ↓                    ↓
    ENROLLMENT          DISABLE              RESET
       ↓                  ↓                    ↓
   PROTECTED?          PROTECTED?          PROTECTED?
       └──────────────────┼────────────────────┘
                          ↓
                     RECOVERY PATH
                          ↓
          IS RECOVERY WEAKER THAN MFA?
                    ↓             ↓
                   NO             YES
                    ↓             ↓
                 CONTINUE     INVESTIGATE
                    ↓
                  TRUSTED DEVICE
                    ↓
              TOKEN SECURELY BOUND?
                    ↓             ↓
                   YES            NO
                    ↓             ↓
                 CONTINUE      BYPASS RISK
                    ↓
                 ALTERNATIVE PATHS
                    ↓
       ┌────────────┼─────────────┬─────────────┐
       ↓            ↓             ↓             ↓
     RESET         SSO         MOBILE        LEGACY
       └────────────┼─────────────┴─────────────┘
                    ↓
             MFA CONSISTENTLY ENFORCED?
                    ↓             ↓
                   YES            NO
                    ↓             ↓
                 CONTINUE       BYPASS
                    ↓
               STEP-UP ACTIONS
                    ↓
          TRANSACTION AUTHORIZATION
                    ↓
                VERIFY IMPACT
                    ↓
           MINIMUM SAFE EVIDENCE
                    ↓
                  REPORT
```

The key principle is:

> MFA must be a server-enforced authentication state, not a page in the login workflow. A user who has supplied only the first factor must remain partially authenticated until the second factor has been independently validated. This distinction must be enforced consistently across web pages, APIs, WebSockets, mobile clients, recovery mechanisms, trusted devices, account management and sensitive step-up operations.
