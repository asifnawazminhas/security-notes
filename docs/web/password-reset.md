# Password Reset Security

Password reset functionality is a critical authentication mechanism because it provides an alternative path for gaining access to an account when the user no longer knows their password.

From an attacker's perspective, the password reset process can become an alternative authentication mechanism:

```text
Normal Authentication

Username
   ↓
Password
   ↓
Authentication
   ↓
Account


Password Reset

Account Identifier
   ↓
Reset Request
   ↓
Reset Token / OTP / Link
   ↓
New Password
   ↓
Account
```

If the password reset workflow is weaker than the normal authentication process, an attacker may be able to bypass the protections applied to login.

Common password reset vulnerabilities include:

```text
User enumeration
Predictable reset tokens
Weak reset tokens
Token leakage
Token reuse
Missing token expiration
Host header poisoning
Reset link manipulation
Reset poisoning
Broken object-level authorisation
OTP brute force
Missing rate limiting
Account identifier manipulation
Email address manipulation
Password reset CSRF
Session handling weaknesses
MFA bypass
Race conditions
Response manipulation
Workflow bypass
Token exposure through URLs
Unsafe redirects
```

!!! warning "Authorised Security Testing"
    Perform password reset testing only against accounts and email addresses that are explicitly authorised for the assessment. Use controlled test accounts whenever possible. Do not trigger password resets for real users, attempt to access third-party mailboxes, or change another user's password unless this is specifically authorised and can be performed safely.

---

# Core Security Principle

Password reset should provide security equivalent to normal authentication.

Conceptually:

```text
Login Security
      ≈
Password Reset Security
```

A secure login process combined with a weak reset process still results in weak account security.

For example:

```text
Login
├── Strong password
├── Rate limiting
├── MFA
└── Monitoring

Password Reset
├── Predictable token
├── No rate limiting
└── MFA bypass
```

The effective security of the account may therefore be:

```text
Password Reset Security
```

rather than:

```text
Login Security
```

---

# Password Reset Architecture

A typical password reset workflow looks like:

```text
User
  ↓
Forgot Password
  ↓
Enter Email / Username
  ↓
Server Generates Token
  ↓
Token Stored Server-Side
  ↓
Reset Link Sent by Email
  ↓
User Opens Link
  ↓
Token Validated
  ↓
New Password Submitted
  ↓
Password Updated
  ↓
Token Invalidated
```

Example reset link:

```text
https://target.example/reset-password?token=abc123
```

---

# Security Boundaries

Several trust boundaries exist:

```text
User
  ↓
Reset Request Endpoint
  ↓
Application
  ↓
Token Generator
  ↓
Database / Token Store
  ↓
Email Provider
  ↓
User Mailbox
  ↓
Browser
  ↓
Reset Endpoint
```

A weakness anywhere in this chain may compromise the reset process.

---

# Password Reset Testing Methodology

Use a structured workflow:

```text
Map Reset Workflow
        ↓
Create Controlled Accounts
        ↓
Request Reset
        ↓
Capture All Requests
        ↓
Inspect Responses
        ↓
Inspect Reset Link
        ↓
Analyse Token
        ↓
Test Token Lifecycle
        ↓
Test Account Binding
        ↓
Test Rate Limiting
        ↓
Test Host Handling
        ↓
Test Workflow State
        ↓
Test Session Behaviour
        ↓
Test MFA Interaction
        ↓
Verify Minimum Safe Impact
```

---

# Controlled Test Accounts

Ideally create:

```text
User A
User B
```

with email accounts you control.

Example:

```text
User A
alice-test@example.test

User B
bob-test@example.test
```

This allows controlled testing of:

```text
Token binding
Account binding
Reset workflow
Email delivery
Token reuse
Session invalidation
Cross-account manipulation
```

without involving real users.

---

# Map the Complete Workflow

Record every request involved.

Example:

```text
GET /forgot-password

POST /forgot-password

GET /reset-password?token=...

POST /reset-password

POST /login
```

Also look for API endpoints:

```text
/api/password/reset/request
/api/password/reset
/api/auth/forgot-password
/api/auth/reset-password
/api/v1/password-reset
```

---

# Burp Proxy Workflow

Use Burp Proxy to capture the complete password reset sequence.

```text
Browser
  ↓
Burp Proxy
  ↓
Forgot Password
  ↓
Reset Request
  ↓
Email Link
  ↓
Reset Page
  ↓
New Password Submission
```

Record:

```text
Endpoint
HTTP method
Parameters
Cookies
Headers
Tokens
Redirects
Responses
```

---

# User Enumeration

Password reset endpoints frequently reveal whether an account exists.

Example:

```http
POST /forgot-password HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

email=alice@example.test
```

Response:

```text
A password reset email has been sent.
```

Unknown account:

```text
No account exists with this email address.
```

This reveals valid users.

---

# Enumeration Through Status Codes

Example:

```text
Known account
→ 200

Unknown account
→ 404
```

Even if response bodies are generic, the status code may reveal account existence.

---

# Enumeration Through Response Length

Example:

```text
Known user
HTTP 200
Length: 1842

Unknown user
HTTP 200
Length: 1761
```

Burp Comparer can help identify subtle differences.

---

# Enumeration Through Timing

The application may respond differently because:

```text
Known account
   ↓
Database lookup
   ↓
Token generation
   ↓
Email processing
```

while:

```text
Unknown account
   ↓
Immediate response
```

This can create a timing difference.

Timing tests require:

```text
Multiple samples
Consistent network conditions
Statistical comparison
```

Do not report a single timing difference as user enumeration.

---

# Enumeration Through Headers

Compare:

```text
Location
Set-Cookie
Content-Length
Cache-Control
```

between:

```text
Known account
Unknown account
```

---

# Enumeration Through API Responses

Example:

```json
{
    "success": false,
    "error": "USER_NOT_FOUND"
}
```

Even when the UI displays:

```text
If the account exists, an email has been sent.
```

the underlying API may disclose the actual result.

Always inspect raw responses.

---

# Secure Enumeration Behaviour

A safer response is:

```text
If an account exists for the supplied information,
password reset instructions will be sent.
```

The external response should remain consistent for:

```text
Existing account
Non-existing account
Disabled account
Locked account
```

where practical.

---

# Reset Token Analysis

The reset token is usually the most important component.

Example:

```text
https://target.example/reset-password?token=7f91e9...
```

Determine:

```text
Length
Character set
Encoding
Structure
Entropy
Expiration
Account binding
Single-use behaviour
```

---

# Token Formats

Tokens may appear as:

```text
Random hexadecimal
Base64
Base64URL
UUID
JWT
Numeric OTP
Signed token
Opaque random token
```

Examples:

```text
4d5c9a92e21d...

550e8400-e29b-41d4-a716-446655440000

eyJhbGciOi...

482193
```

The format itself does not prove security or insecurity.

---

# Random Tokens

Secure reset tokens should normally be generated using:

```text
Cryptographically Secure Random Number Generator
```

with sufficient entropy.

Conceptually:

```text
CSPRNG
  ↓
High-Entropy Token
  ↓
Bound to Account
  ↓
Short Expiration
  ↓
Single Use
```

---

# Predictable Tokens

Weak implementations may derive tokens from:

```text
Username
Email address
Timestamp
User ID
Sequential counter
Weak random generator
Known secret
```

Example conceptual pattern:

```text
MD5(username + timestamp)
```

This is unsafe if an attacker can reproduce or significantly reduce the token search space.

---

# Encoded Is Not Random

A token such as:

```text
MTAwMToxNzU2Mzk1MDAw
```

may simply be Base64.

Decode it before assuming it is random.

For example:

```bash
echo 'MTAwMToxNzU2Mzk1MDAw' | base64 -d
```

could reveal:

```text
1001:1756395000
```

Encoding provides:

```text
Representation
```

not:

```text
Security
```

---

# Burp Decoder

Use Burp Decoder to inspect tokens for:

```text
Base64
Base64URL
Hex
URL encoding
```

Look for embedded:

```text
User IDs
Email addresses
Timestamps
Account IDs
```

---

# JWT Reset Tokens

Some applications use JWTs as password reset tokens.

Example:

```text
eyJhbGciOiJIUzI1NiIs...
```

Decode the token and inspect claims.

Potential claims:

```json
{
    "sub": "101",
    "purpose": "password-reset",
    "exp": 1756396000
}
```

Important checks include:

```text
Signature validation
Expiration
Purpose binding
Account binding
Single-use behaviour
```

JWT-specific security testing is covered in:

```text
docs/web/jwt.md
```

---

# Purpose Binding

A token issued for:

```text
Email Verification
```

should not work for:

```text
Password Reset
```

Likewise:

```text
Password Reset Token
```

should not work for:

```text
Email Change
MFA Reset
Account Activation
```

Tokens should be bound to their intended purpose.

---

# Account Binding

A reset token should be securely associated with exactly one account.

Suppose User A receives:

```text
TOKEN_A
```

and User B receives:

```text
TOKEN_B
```

Test whether:

```text
TOKEN_A + USER_B
```

can affect User B.

---

# Token and User Parameters

Example:

```http
POST /reset-password HTTP/1.1
Content-Type: application/x-www-form-urlencoded

token=TOKEN_A&
userId=101&
password=NewPassword
```

Potential security issue:

```text
Token identifies User A
```

but:

```text
userId controls target account
```

If the application validates only the token but trusts `userId`, account takeover may be possible.

---

# Two-Account Binding Test

Controlled matrix:

| Token | Target Account | Expected |
|---|---|---|
| Token A | User A | Allow |
| Token A | User B | Deny |
| Token B | User B | Allow |
| Token B | User A | Deny |
| Invalid token | User A | Deny |

This is one of the most useful password reset tests.

---

# IDOR / BOLA in Password Reset

Password reset workflows may expose object identifiers such as:

```text
userId
accountId
resetId
requestId
```

Example:

```http
POST /api/password/reset HTTP/1.1
Content-Type: application/json

{
    "resetId": "991",
    "password": "NewPassword"
}
```

Determine whether the server securely binds:

```text
Reset Request
```

to:

```text
Correct Account
```

Refer to:

```text
docs/web/idor-bola.md
```

---

# Token Expiration

Reset tokens should expire after a short period.

Test:

```text
Request Token
   ↓
Record Time
   ↓
Wait Beyond Expected Lifetime
   ↓
Attempt Reset
```

The expected expiration period depends on application policy.

---

# Expiration Verification

Do not infer expiration solely from:

```text
Email says link expires in 15 minutes.
```

Verify whether the server actually enforces it.

---

# Missing Expiration

A reset token that remains valid indefinitely increases the impact of:

```text
Email compromise
Browser history exposure
Log exposure
Token leakage
Old database records
```

---

# Single-Use Tokens

A reset token should normally become invalid after successful use.

Test:

```text
TOKEN_A
  ↓
Reset Password
  ↓
Success
  ↓
Reuse TOKEN_A
```

Expected:

```text
Rejected
```

---

# Token Reuse

If:

```text
TOKEN_A
```

can be used repeatedly, an attacker who later obtains the token may continue resetting the account.

---

# Token Invalidation After New Request

Consider:

```text
Request TOKEN_A
      ↓
Request TOKEN_B
      ↓
Try TOKEN_A
```

Depending on the application design, older reset tokens may need to be invalidated when a newer token is issued.

A common secure model is:

```text
Only Most Recent Reset Token Valid
```

although implementations can securely support multiple outstanding tokens if properly designed.

---

# Token Invalidation After Password Change

After:

```text
Password Changed
```

all outstanding reset tokens should normally be invalidated.

Test with controlled accounts:

```text
Request TOKEN_A
Request TOKEN_B
Use TOKEN_A
Try TOKEN_B
```

Expected:

```text
TOKEN_B rejected
```

for implementations using single outstanding reset state.

---

# Reset Token Storage

Server-side reset tokens should be protected.

A strong design may store:

```text
Hash(Token)
```

rather than:

```text
Raw Token
```

similar to password storage principles.

If the database is compromised, raw reset tokens should ideally not provide immediate account access.

---

# OTP-Based Password Reset

Some applications use numeric codes.

Example:

```text
Enter the six-digit code sent to your email.

482193
```

Security depends heavily on:

```text
Entropy
Expiration
Rate limiting
Account binding
Attempt limits
Replay protection
```

---

# OTP Search Space

A six-digit numeric OTP has:

```text
1,000,000
```

possible values:

```text
000000
through
999999
```

This is only safe when strong online protections exist.

---

# OTP Rate Limiting

Test whether repeated invalid OTP attempts trigger:

```text
Temporary lock
Rate limit
Increasing delay
Token invalidation
CAPTCHA
Additional verification
```

Use a very small number of controlled attempts unless higher-volume testing is explicitly authorised.

---

# OTP Account Binding

Example:

```http
POST /verify-reset-code HTTP/1.1
Content-Type: application/json

{
    "email": "alice@example.test",
    "code": "482193"
}
```

Test whether:

```text
User A Code
```

can be submitted with:

```text
User B Email
```

using two controlled accounts.

Expected:

```text
Denied
```

---

# OTP Reuse

After successful verification:

```text
OTP
```

should normally become invalid.

---

# OTP Expiration

A code should not remain valid indefinitely.

---

# OTP Attempt Counter Reset

Look for workflows where the attempt counter can be reset by:

```text
Requesting another code
Changing session
Changing endpoint
Changing account identifier format
Starting a new browser session
```

Only perform minimal testing.

---

# Rate Limiting

Password reset endpoints should protect:

```text
Reset request generation
OTP verification
Token verification
Account lookup
Email delivery
```

Potential abuse includes:

```text
User enumeration
OTP brute force
Email flooding
Resource exhaustion
Account harassment
```

---

# Reset Email Flooding

Repeated reset requests may generate many emails.

Test minimally.

Example:

```text
Request 1
Request 2
Request 3
```

Determine whether reasonable throttling exists.

Do not intentionally flood mail infrastructure.

---

# Rate-Limit Scope

Rate limiting may operate by:

```text
IP
Account
Email
Session
Device
Token
Combination
```

A strong implementation generally avoids relying solely on attacker-controlled identifiers.

---

# Burp Intruder

Burp Intruder can assist with controlled testing of:

```text
Enumeration
OTP validation
Token formats
Account binding
```

However, password reset endpoints are sensitive.

Use:

```text
Small payload sets
Low request rate
Controlled accounts
```

unless higher-volume testing is explicitly approved.

---

# Enumeration with Intruder

Example request:

```http
POST /forgot-password HTTP/1.1
Content-Type: application/x-www-form-urlencoded

email=§alice@example.test§
```

Payload set:

```text
known-test-account@example.test
nonexistent-test-account@example.test
```

Compare:

```text
Status
Length
Words
Response body
Timing
Headers
```

This can be sufficient to demonstrate enumeration without testing real users.

---

# Burp Comparer

Comparer is particularly useful for comparing:

```text
Known user response
Unknown user response
```

Look for subtle differences.

---

# Burp Repeater

Repeater should be the main tool for:

```text
Token binding
Account binding
Token reuse
Expiration
Host manipulation
Workflow manipulation
Session behaviour
```

---

# Password Reset Poisoning

Password reset poisoning occurs when an attacker influences the URL placed inside a password reset email.

Example intended link:

```text
https://target.example/reset?token=TOKEN
```

Vulnerable application:

```text
Host header
    ↓
Used to Construct Reset URL
    ↓
Reset Email
```

Attacker sends:

```http
POST /forgot-password HTTP/1.1
Host: attacker-controlled.example

email=victim@example.test
```

Application constructs:

```text
https://attacker-controlled.example/reset?token=TOKEN
```

If the recipient follows the link, the token may be sent to the attacker-controlled host.

---

# Safe Reset Poisoning Testing

Do not target real users.

Use:

```text
Your controlled test account
Your controlled mailbox
Your controlled callback domain
```

Workflow:

```text
Controlled Account
      ↓
Request Password Reset
      ↓
Modify Host-Related Input
      ↓
Receive Email Yourself
      ↓
Inspect Generated Link
```

There is no need to compromise another account to demonstrate the issue.

---

# Host Header Testing

Candidate headers include:

```text
Host
X-Forwarded-Host
X-Forwarded-Proto
Forwarded
X-Original-Host
X-Host
```

Which headers matter depends on:

```text
Reverse proxy
Load balancer
Framework
Application
```

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# X-Forwarded-Host

Example:

```http
POST /forgot-password HTTP/1.1
Host: target.example
X-Forwarded-Host: controlled.example
Content-Type: application/x-www-form-urlencoded

email=controlled-account@example.test
```

Inspect the email received by the controlled account.

If it contains:

```text
https://controlled.example/reset?token=...
```

the application may be vulnerable to reset poisoning.

---

# Forwarded Header

Some environments use:

```http
Forwarded: host=controlled.example;proto=https
```

Again:

```text
Use only your own reset email
```

during testing.

---

# X-Forwarded-Proto

The application may trust:

```http
X-Forwarded-Proto: http
```

when constructing reset links.

This may cause:

```text
HTTPS Downgrade
```

or otherwise incorrect URL generation.

---

# Absolute URL Generation

Search password reset emails for:

```text
Scheme
Hostname
Port
Path
Token
```

Determine where each value originates.

Secure architecture:

```text
Trusted Application Configuration
          ↓
Reset Base URL
```

rather than:

```text
Untrusted Request Headers
          ↓
Reset Base URL
```

---

# Host Header Inchecktion

For broader Host header testing, Burp's BApp Store provides:

```text
Host Header Inchecktion
```

This extension can assist with testing Host header injection issues.

It is especially relevant where password reset URLs are constructed from incoming request metadata.

Use it for:

```text
Host manipulation
Forwarded host testing
Reflection detection
Collaborator-based checks
```

Password reset poisoning should still be verified manually using a controlled mailbox.

---

# Burp Collaborator

Collaborator can help determine whether:

```text
Reset link
Redirect
Server-side request
```

interacts with a controlled domain.

For password reset poisoning, a controlled domain or Collaborator-style endpoint may provide evidence that a generated URL points outside the trusted application domain.

Do not expose genuine user reset tokens unnecessarily.

---

# Host Header Poisoning Evidence

Strong evidence:

```text
1. Controlled account requests password reset.

2. X-Forwarded-Host is changed to controlled.example.

3. Application returns normal reset response.

4. Controlled mailbox receives password reset email.

5. Reset link points to controlled.example.

6. Link contains a valid reset token.
```

This proves the issue without affecting another user.

---

# Reset Link Leakage

Reset tokens may leak through:

```text
Referer headers
Browser history
Proxy logs
Analytics
Third-party scripts
Server logs
URL monitoring
Screenshots
Support systems
```

---

# Token in URL

Example:

```text
/reset-password?token=SECRET
```

Tokens in URLs can appear in:

```text
Browser history
Access logs
Analytics
Referer
```

This is common, but the surrounding page must be designed to minimise leakage.

---

# Referer Leakage

Suppose the reset page loads:

```text
https://analytics.example/script.js
```

or contains links to external sites.

The browser may send a Referer containing the reset URL depending on the referrer policy and navigation context.

A secure application should reduce the possibility of sensitive token leakage.

---

# Referrer-Policy

Useful policy:

```http
Referrer-Policy: no-referrer
```

may be appropriate for highly sensitive reset pages.

Other policies can also limit leakage depending on application requirements.

---

# Third-Party Content

Password reset pages should minimise:

```text
Analytics
Advertising
Third-party JavaScript
External images
External fonts
Third-party widgets
```

because these create additional opportunities for token exposure.

---

# Token Exposure in HTML

Inspect page source and responses for:

```text
Reset token
Email address
User ID
```

Avoid unnecessarily exposing secrets to client-side JavaScript.

---

# Token Exposure in JavaScript

Example:

```javascript
window.resetToken = "SECRET";
```

If third-party scripts execute in the page:

```text
Reset token
```

may become accessible to them.

---

# Token Exposure Through Errors

Error pages may include:

```text
Full reset URL
Token
User ID
Stack trace
```

Refer to:

```text
docs/web/information-disclosure.md
```

---

# Open Redirect Interaction

Suppose:

```text
/reset?token=TOKEN&next=https://external.example
```

If the application redirects while retaining the token:

```text
Reset Token
   ↓
External Site
```

may become exposed.

Refer to:

```text
docs/web/open-redirect.md
```

---

# Password Reset CSRF

Some password reset workflows allow a password to be changed using:

```text
Authenticated session
```

without requiring:

```text
Current password
CSRF protection
Reset token
```

This may create a password-change CSRF issue.

Example:

```http
POST /account/change-password HTTP/1.1
Cookie: session=VICTIM

newPassword=AttackerChosenPassword
```

If an attacker can cause the victim's browser to submit this request:

```text
Victim's password may be changed
```

depending on session and CSRF protections.

Refer to:

```text
docs/web/csrf.md
```

---

# Reset Token CSRF

Reset-token flows can behave differently.

If the token itself provides sufficient unpredictable authorisation:

```text
CSRF may not always be independently exploitable.
```

Analyse the exact workflow rather than reporting missing CSRF tokens mechanically.

---

# Password Change vs Password Reset

These are different workflows.

## Password Change

Authenticated user:

```text
Current Session
      ↓
Current Password
      ↓
New Password
```

## Password Reset

Unauthenticated or recovery flow:

```text
Reset Token
     ↓
New Password
```

They should be tested separately.

---

# Current Password Verification

For authenticated password changes, test whether:

```text
Current password
```

is required where appropriate.

This becomes particularly important when:

```text
Session compromise
CSRF
Unattended browser
```

are relevant threats.

---

# Account Identifier Manipulation

Example:

```http
POST /reset-password HTTP/1.1
Content-Type: application/json

{
    "token": "TOKEN_A",
    "email": "alice@example.test",
    "password": "NewPassword"
}
```

Test with controlled accounts whether:

```text
email
```

or another identifier can redirect the reset to a different account.

---

# Email Parameter Manipulation

Some reset requests contain:

```json
{
    "email": "alice@example.test"
}
```

Look for parsing inconsistencies such as:

```text
Multiple email fields
Array values
Duplicate parameters
Case variations
Whitespace
```

Only test these against controlled accounts.

---

# Duplicate Parameters

Example:

```text
email=alice@example.test&email=bob@example.test
```

Different components may choose:

```text
First value
Last value
Both values
```

This can occasionally create workflow inconsistencies.

---

# JSON Arrays

Example:

```json
{
    "email": [
        "alice@example.test",
        "bob@example.test"
    ]
}
```

Some frameworks may unexpectedly coerce or process arrays.

Use only controlled addresses.

---

# Email Case Normalisation

Test controlled variations:

```text
Alice@example.test
alice@example.test
ALICE@example.test
```

depending on application behaviour.

The purpose is to identify:

```text
Identity normalisation inconsistencies
```

not to brute-force users.

---

# Unicode and Canonicalisation

Identity systems may normalise:

```text
Unicode
Whitespace
Case
```

differently across:

```text
Registration
Login
Password Reset
```

Inconsistent canonicalisation can occasionally cause account confusion.

This requires careful controlled testing.

---

# Password Reset Workflow Bypass

A multi-step reset process may look like:

```text
Step 1
Request Reset

Step 2
Verify OTP

Step 3
Choose New Password
```

Do not assume each step is enforced server-side.

---

# Direct Step Access

Test whether:

```text
Step 3
```

can be accessed without completing:

```text
Step 2
```

Example:

```text
POST /reset/complete
```

with a controlled account.

The server must enforce workflow state.

---

# Client-Side Workflow State

A vulnerable application may rely on:

```text
JavaScript variable
Hidden field
LocalStorage
SessionStorage
```

to indicate:

```text
OTP verified
```

Security-relevant workflow state must be validated server-side.

---

# Response Manipulation

Suppose OTP verification returns:

```json
{
    "verified": false
}
```

and the frontend decides whether to show the reset form.

Changing the response locally to:

```json
{
    "verified": true
}
```

may reveal the form, but this is not a vulnerability unless the server also accepts the subsequent reset without valid verification.

Important principle:

```text
Client-Side UI Bypass
        ≠
Server-Side Security Bypass
```

Always verify the server-side action.

---

# Hidden Fields

Example:

```html
<input
    type="hidden"
    name="verified"
    value="true">
```

This must not be trusted as evidence that recovery verification occurred.

---

# Reset Workflow State Tokens

Applications may use:

```text
resetSession
recoverySession
flowId
challengeId
```

These values should be:

```text
Unpredictable
Bound to account
Bound to workflow
Short-lived
Protected from reuse
```

---

# Race Conditions

Password reset workflows can contain race conditions.

Example:

```text
TOKEN
  ↓
Request A validates token
Request B validates token
  ↓
Both succeed before invalidation
```

This may allow:

```text
Single-use token
```

to be used more than once concurrently.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Safe Race Testing

Use:

```text
Controlled account
Controlled reset token
Small number of concurrent requests
```

Avoid large request bursts.

Burp Repeater request groups can assist with controlled parallel testing.

---

# Session Handling After Reset

After a password reset, determine what happens to existing sessions.

Potential behaviour:

```text
All sessions remain active
Current session remains active
Other sessions revoked
All sessions revoked
```

The expected policy depends on the application.

For high-risk applications, password reset often should invalidate existing authenticated sessions.

---

# Existing Session Test

Controlled workflow:

```text
Browser A
Login as User A
      ↓
Browser B
Reset User A Password
      ↓
Return to Browser A
      ↓
Test Existing Session
```

Record whether:

```text
Session remains valid
```

and compare with expected application policy.

---

# Remember-Me Tokens

Password reset should also consider:

```text
Remember-me cookies
Long-lived refresh tokens
Mobile sessions
API tokens
```

Changing the password while leaving long-lived authentication tokens active may undermine the user's ability to recover from account compromise.

---

# Refresh Tokens

If the application uses:

```text
Access Token
Refresh Token
```

test whether password reset invalidates:

```text
Existing refresh tokens
```

where this is expected by the application's security model.

---

# API Keys

Password reset does not necessarily need to revoke API keys automatically.

However, for some application models:

```text
Password reset due to suspected compromise
```

may warrant:

```text
Credential review
Session revocation
API key revocation
```

This is a policy decision.

---

# MFA and Password Reset

Password reset may accidentally bypass MFA.

Example:

```text
Normal Login
   ↓
Password
   ↓
MFA
   ↓
Account
```

but:

```text
Password Reset
   ↓
Email Link
   ↓
New Password
   ↓
Authenticated Session
   ↓
No MFA
```

This may undermine MFA.

---

# Automatic Login After Reset

Some applications automatically authenticate the user after resetting the password.

Test whether the resulting session has completed all required authentication factors.

If MFA is enabled:

```text
Password Reset
```

should not necessarily create:

```text
Fully MFA-Authenticated Session
```

unless the recovery process itself provides equivalent assurance.

---

# MFA Reset

Some account recovery workflows allow:

```text
Reset Password
Disable MFA
```

through the same recovery process.

This deserves particularly careful testing.

The dedicated MFA page will cover this in more detail.

---

# Recovery Codes

If recovery codes exist, test:

```text
Single use
Account binding
Storage
Rate limiting
Invalidation
```

using controlled accounts.

---

# Security Questions

Some password reset workflows still use:

```text
Security Questions
```

Examples:

```text
Mother's maiden name
First school
Favourite city
```

These are generally weak recovery mechanisms because answers may be:

```text
Guessable
Publicly available
Reused
Socially discoverable
```

Do not attempt to research real users' personal answers during testing.

---

# Password Policy During Reset

Ensure password reset enforces the same password policy as:

```text
Registration
Password Change
```

Potential inconsistencies:

```text
Minimum length
Maximum length
Breached-password checks
Character requirements
Password history
```

---

# Password Storage

Password reset should feed into the same secure password storage mechanism as normal password changes.

The reset workflow must not result in:

```text
Plaintext password storage
Reversible password storage
Weak password hashing
```

---

# Password Confirmation

The reset form commonly asks:

```text
New Password
Confirm Password
```

This is primarily a usability mechanism.

Security should not depend on client-side confirmation alone.

---

# Information Disclosure

Reset workflows may reveal:

```text
Internal user ID
Account status
Email address
Phone number
MFA state
Organisation
Authentication provider
```

Example:

```text
Password reset unavailable because this account uses SAML.
```

This may disclose account configuration.

Assess whether the information materially increases attackability.

---

# SSO Accounts

Applications using:

```text
SAML
OAuth
OIDC
Enterprise SSO
```

may not have local passwords.

Test whether password reset unexpectedly allows:

```text
Local password creation
```

for an SSO-only account.

This can create an authentication bypass.

---

# SSO Downgrade

Potential vulnerable architecture:

```text
Corporate Account
      ↓
SSO Only
      ↓
Forgot Password
      ↓
Local Password Created
      ↓
Login Without SSO
```

This can bypass:

```text
Corporate MFA
Conditional Access
Identity Provider Controls
```

and may be severe.

---

# Password Reset and OAuth

Accounts created through social login may behave differently.

Test controlled accounts for:

```text
Google login
Microsoft login
GitHub login
Local password
```

where available.

Determine whether reset unexpectedly creates alternative authentication paths.

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# Email Change Interaction

A dangerous chain can occur:

```text
Change Account Email
       ↓
No Reauthentication
       ↓
Request Password Reset
       ↓
Reset Sent to New Email
       ↓
Account Takeover
```

Email-change workflows therefore deserve the same security attention as password reset.

---

# Email Change Verification

Secure designs may require:

```text
Current password
MFA
Verification of old email
Verification of new email
```

depending on application risk.

---

# Password Reset and Host Header Attacks

Password reset is one of the highest-value places to test:

```text
Host
X-Forwarded-Host
Forwarded
```

because applications frequently need to generate absolute URLs.

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# Password Reset and Cache Behaviour

Sensitive reset pages should not be stored in shared caches.

Inspect:

```http
Cache-Control
Pragma
Expires
```

Sensitive pages commonly require restrictive caching behaviour.

---

# Reset Token in Cache

A dangerous architecture could cache:

```text
/reset-password?token=SECRET
```

or user-specific reset content in a shared cache.

This may expose recovery information.

Refer to:

```text
docs/web/web-cache-deception.md
docs/web/web-cache-poisoning.md
```

where relevant.

---

# HTTPS

Password reset links should use:

```text
HTTPS
```

because reset tokens are authentication credentials.

HTTP links may expose tokens to network attackers.

---

# HSTS

HSTS can reduce downgrade risks for users who have already established an HTTPS trust relationship with the site.

Refer to the HTTP Security Headers page when added.

---

# Open Redirect After Reset

Example:

```text
/reset?token=TOKEN&returnUrl=https://controlled.example
```

Test whether:

```text
returnUrl
next
redirect
continue
```

can send the user to an external domain after reset.

Even when the reset token itself is not leaked, this can facilitate phishing.

---

# Password Reset and XSS

An XSS vulnerability on a password reset page may be particularly sensitive because:

```text
Reset Token
```

may be accessible through:

```text
URL
DOM
Page state
JavaScript
```

Refer to:

```text
docs/web/xss.md
docs/web/dom-based-vulnerabilities.md
```

---

# Password Reset and CSRF

Relevant scenarios include:

```text
Password change CSRF
Email change CSRF
Recovery setting modification
```

Refer to:

```text
docs/web/csrf.md
```

---

# Password Reset and Business Logic

Password recovery is fundamentally a business workflow.

Questions include:

```text
Can steps be skipped?

Can tokens be reused?

Can one account's token affect another?

Can the target account change during the flow?

Can an SSO account obtain a local password?

Can MFA be bypassed?

Can verification state be manipulated?
```

Refer to:

```text
docs/web/business-logic.md
```

---

# Password Reset and Mass Assignment

Reset APIs may accept unexpected fields.

Example:

```json
{
    "token": "TOKEN",
    "password": "NewPassword",
    "verified": true
}
```

Unexpected object properties should not influence recovery state.

Refer to:

```text
docs/web/mass-assignment.md
```

---

# Password Reset and IDOR / BOLA

Reset workflows frequently contain identifiers:

```text
userId
accountId
requestId
challengeId
```

Each must be securely bound to the recovery token or authenticated recovery state.

Refer to:

```text
docs/web/idor-bola.md
```

---

# Browser DevTools

Browser DevTools can help inspect:

```text
Reset page JavaScript
LocalStorage
SessionStorage
Cookies
Network requests
Client-side workflow state
Third-party resources
Referrer behaviour
```

Useful tabs:

```text
Network
Application
Sources
Console
```

---

# LocalStorage

Security-sensitive reset state should not depend solely on:

```javascript
localStorage.setItem(
    "otpVerified",
    "true"
);
```

An attacker controls browser storage.

---

# SessionStorage

The same principle applies to:

```text
sessionStorage
```

It may be useful for UI state but not as the sole server-side authorisation mechanism.

---

# Cookies

Inspect reset-related cookies for:

```text
Secure
HttpOnly
SameSite
Path
Domain
Expiration
```

Determine whether reset sessions are:

```text
Bound correctly
Short-lived
Invalidated after use
```

---

# Reset Session Fixation

If the application creates a reset-session cookie before verification:

```text
reset_session=ABC
```

determine whether:

```text
ABC
```

is rotated or securely bound after successful verification.

Recovery state should not be transferable between accounts or users.

---

# Burp Sequencer

Burp Sequencer can help analyse the randomness of tokens generated by an application when enough samples can be safely collected.

Potential use:

```text
Password Reset Tokens
Session Tokens
Recovery Tokens
```

However:

```text
Sequencer analysis requires many samples
```

and repeatedly generating reset emails may create operational impact.

Use it only when:

```text
High-volume token generation is explicitly authorised
```

and preferably in a test environment.

---

# Sequencer Workflow

Conceptually:

```text
Generate Many Controlled Tokens
          ↓
Collect Tokens
          ↓
Burp Sequencer
          ↓
Statistical Analysis
          ↓
Investigate Randomness
```

Do not use Sequencer merely because a token looks unusual.

---

# Burp Collaborator

Useful for:

```text
Password reset poisoning
Host header injection
External callback verification
```

A controlled external interaction can provide strong evidence.

---

# Param Miner

Param Miner can help identify hidden:

```text
Headers
Parameters
Cookies
```

that influence password reset behaviour.

Particularly interesting:

```text
Forwarding headers
URL-generation parameters
Hidden workflow parameters
```

Official BApp Store:

https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943

Always manually verify discovered inputs.

---

# Host Header Inchecktion

A useful Burp extension for this topic is:

```text
Host Header Inchecktion
```

It assists with Host header injection testing and can help identify places where:

```text
Host
Forwarded headers
```

influence application behaviour.

Official BApp Store:

https://portswigger.net/bappstore/3908768b9ae945d8adf583052ad2e3b3

Password reset poisoning remains a manual workflow because the important evidence is often:

```text
What URL actually arrived in the controlled mailbox?
```

---

# Turbo Intruder

Turbo Intruder may be useful for specialised testing involving:

```text
Race conditions
Small controlled OTP tests
Timing-sensitive workflows
```

Official BApp Store:

https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988

GitHub:

https://github.com/PortSwigger/turbo-intruder

Do not use high-speed brute forcing against password recovery mechanisms unless this is explicitly authorised.

For most password reset testing:

```text
Repeater
```

and:

```text
Intruder with very small payload sets
```

are safer.

---

# AuthMatrix and Autorize

Password reset endpoints are usually unauthenticated, so authorisation extensions may not always be the primary tools.

However, they become useful for:

```text
Authenticated password changes
Recovery settings
MFA reset
Email changes
Administrative password reset
```

where multiple roles are involved.

---

# Administrative Password Reset

Administrators or support staff may have functionality such as:

```text
Reset User Password
Send Reset Email
Generate Temporary Password
Unlock Account
Disable MFA
```

Test role boundaries carefully.

Potential issue:

```text
Low-Privilege Support User
       ↓
Administrative Reset Endpoint
       ↓
Higher-Privilege Account
```

This may result in vertical privilege escalation.

---

# Temporary Passwords

Some systems send:

```text
Temporary Password
```

instead of a reset link.

Test whether temporary passwords are:

```text
Random
Short-lived
Single-use
Forced to change
Protected against brute force
```

Sending plaintext temporary credentials by email has additional security implications.

---

# Support-Assisted Recovery

Some applications allow support staff to reset accounts manually.

Security controls may include:

```text
Identity verification
Audit logging
Role restrictions
Approval
Reauthentication
```

This is primarily a business process and access-control concern.

---

# Custom Reset Token Inspector

A simple local helper can inspect the format of tokens you obtain from your own controlled reset emails.

```python
#!/usr/bin/env python3

import base64
import re
import sys
from urllib.parse import unquote


def try_hex(value):

    try:

        raw = bytes.fromhex(value)

        if raw:
            print(
                "[+] Hex decoded:",
                raw
            )

    except ValueError:
        pass


def try_base64(value):

    candidates = [
        value,
        value.replace("-", "+").replace("_", "/")
    ]

    for candidate in candidates:

        try:

            padding = "=" * (
                (4 - len(candidate) % 4) % 4
            )

            raw = base64.b64decode(
                candidate + padding,
                validate=False
            )

            if raw:

                printable = sum(
                    32 <= byte <= 126
                    for byte in raw
                )

                if printable / len(raw) > 0.7:

                    print(
                        "[+] Base64-like decoded:",
                        raw.decode(
                            "utf-8",
                            errors="replace"
                        )
                    )

        except Exception:
            pass


if len(sys.argv) != 2:

    print(
        f"Usage: {sys.argv[0]} TOKEN"
    )

    sys.exit(1)


token = unquote(sys.argv[1])

print(
    f"[+] Token length: {len(token)}"
)

print(
    f"[+] Token: {token}"
)

if re.fullmatch(
    r"[0-9a-fA-F]+",
    token
):

    print(
        "[+] Token looks hexadecimal."
    )

    try_hex(token)


if token.count(".") == 2:

    print(
        "[+] Token resembles a JWT."
    )


try_base64(token)
```

Usage:

```bash
python3 reset_token_inspector.py 'TOKEN_FROM_CONTROLLED_ACCOUNT'
```

This script performs:

```text
Local format analysis only
```

and sends no requests.

---

# Controlled Token Comparison Script

When several reset tokens have been generated for your own controlled account, compare them locally.

```python
#!/usr/bin/env python3

TOKENS = [
    "CONTROLLED_TOKEN_1",
    "CONTROLLED_TOKEN_2",
    "CONTROLLED_TOKEN_3"
]


print(
    f"{'TOKEN':<50} LENGTH"
)

print(
    "-" * 70
)


for token in TOKENS:

    print(
        f"{token:<50} {len(token)}"
    )


if len(set(TOKENS)) != len(TOKENS):

    print(
        "\n[!] Duplicate token detected."
    )

else:

    print(
        "\n[+] All supplied tokens are unique."
    )
```

Uniqueness alone does not prove sufficient entropy.

---

# Controlled Account-Binding Script

For an API-based reset flow, a small script can automate a two-account matrix.

Use only controlled accounts and tokens.

```python
#!/usr/bin/env python3

import requests


URL = "https://target.example/api/password/reset"

TEST_PASSWORD = "Controlled-Test-Password-2026!"

TOKENS = {
    "user_a": "TOKEN_A",
    "user_b": "TOKEN_B"
}

USERS = {
    "user_a": "USER_A_IDENTIFIER",
    "user_b": "USER_B_IDENTIFIER"
}


for token_owner, token in TOKENS.items():

    for target_user, user_id in USERS.items():

        payload = {
            "token": token,
            "userId": user_id,
            "password": TEST_PASSWORD
        }

        response = requests.post(
            URL,
            json=payload,
            timeout=10,
            allow_redirects=False
        )

        print(
            f"token={token_owner:<6} "
            f"target={target_user:<6} "
            f"status={response.status_code:<3} "
            f"length={len(response.content)}"
        )
```

Expected:

```text
TOKEN A + USER A
→ Allow

TOKEN A + USER B
→ Deny

TOKEN B + USER B
→ Allow

TOKEN B + USER A
→ Deny
```

Be aware that successful tests change passwords.

Use:

```text
Dedicated disposable test accounts
```

and restore them afterwards.

---

# Password Reset Endpoint Discovery

Search JavaScript:

```bash
grep -RniE \
'forgot.?password|reset.?password|password.?reset|recover|recovery|resetToken|reset_token|otp|verificationCode' \
.
```

---

# API Route Discovery

Useful search terms:

```text
forgot
reset
recover
recovery
password
otp
verification
challenge
```

---

# JavaScript Analysis

Look for:

```text
API endpoint
Parameter names
Reset token handling
Redirect parameters
Client-side verification state
Hidden workflow steps
```

Refer to:

```text
docs/web/reconnaissance/javascript-analysis.md
```

---

# Source Code Review

Search for functions involving:

```text
resetPassword
forgotPassword
generateResetToken
validateResetToken
passwordReset
sendResetEmail
recovery
OTP
```

---

# Token Generation Review

Verify that tokens use:

```text
Cryptographically secure randomness
```

rather than:

```text
Math.random()
rand()
Timestamp
Sequential counter
Predictable hash
```

---

# Example Secure Token Generation

Conceptually:

```text
CSPRNG
  ↓
256-bit Random Value
  ↓
Encode
  ↓
Store Hash
  ↓
Send Token
```

The exact implementation depends on language and framework.

---

# Reset Token Database Model

A secure model might contain:

```text
User ID
Token Hash
Created At
Expires At
Used At
Purpose
```

Security decisions remain server-side.

---

# Logging

Password reset events should be logged.

Useful events:

```text
Reset requested
Reset token generated
Reset completed
Reset failed
OTP failures
Rate limit triggered
Password changed
Sessions revoked
```

Do not log:

```text
Raw reset tokens
New passwords
OTPs
```

---

# Notifications

Users may be notified when:

```text
Password reset requested
Password successfully changed
Recovery email changed
MFA changed
```

Notifications can help detect account takeover.

---

# Password Reset Checklist

## Workflow Mapping

```text
[ ] Forgot-password page identified
[ ] Reset request endpoint identified
[ ] Reset verification endpoint identified
[ ] Password update endpoint identified
[ ] API endpoints identified
[ ] Redirects recorded
[ ] Cookies recorded
[ ] Tokens recorded
```

## Enumeration

```text
[ ] Known vs unknown account response
[ ] Status codes
[ ] Response lengths
[ ] Response bodies
[ ] Headers
[ ] Timing where justified
[ ] API errors
```

## Reset Token

```text
[ ] Token format analysed
[ ] Token length recorded
[ ] Encoding checked
[ ] Embedded data checked
[ ] Account binding tested
[ ] Purpose binding tested
[ ] Expiration tested
[ ] Single-use behaviour tested
[ ] Reuse after password change tested
[ ] Old-token invalidation tested
```

## OTP

```text
[ ] OTP length
[ ] Character set
[ ] Expiration
[ ] Account binding
[ ] Attempt limits
[ ] Rate limiting
[ ] Reuse
[ ] New-code behaviour
```

## Password Reset Poisoning

```text
[ ] Host tested
[ ] X-Forwarded-Host tested where relevant
[ ] Forwarded tested where relevant
[ ] X-Forwarded-Proto tested where relevant
[ ] Generated email URL inspected
[ ] Controlled mailbox used
[ ] External host not accepted
```

## Token Leakage

```text
[ ] URL exposure
[ ] Referer behaviour
[ ] Third-party resources
[ ] Browser history considerations
[ ] Logging
[ ] Analytics
[ ] JavaScript exposure
[ ] Error exposure
```

## Workflow

```text
[ ] Steps cannot be skipped
[ ] Verification enforced server-side
[ ] Client state not trusted
[ ] Hidden fields not trusted
[ ] Reset session securely bound
[ ] Account cannot change mid-flow
```

## Session Security

```text
[ ] Existing sessions tested
[ ] Refresh tokens considered
[ ] Remember-me tokens considered
[ ] Session policy verified
```

## MFA

```text
[ ] MFA remains enforced
[ ] Automatic login checked
[ ] Recovery does not silently disable MFA
[ ] MFA reset separately protected
```

## SSO

```text
[ ] SSO-only account behaviour checked
[ ] Local password cannot be created unexpectedly
[ ] Corporate authentication controls preserved
```

## Related Vulnerabilities

```text
[ ] IDOR / BOLA
[ ] Mass Assignment
[ ] Host Header Attacks
[ ] Open Redirect
[ ] CSRF
[ ] XSS
[ ] Information Disclosure
[ ] Race Conditions
[ ] Business Logic
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Comparer
[ ] Decoder
[ ] Intruder where appropriate
[ ] Sequencer where explicitly authorised
[ ] Collaborator
[ ] Param Miner
[ ] Host Header Inchecktion
[ ] Turbo Intruder where justified
```

## Safety

```text
[ ] Controlled accounts used
[ ] Controlled mailbox used
[ ] Controlled callback domain used
[ ] No real users targeted
[ ] No email flooding
[ ] No uncontrolled OTP brute forcing
[ ] Minimal proof obtained
```

---

# Password Reset Testing Matrix

| Test | User A | User B | Expected |
|---|---|---|---|
| Token A resets User A | Token A | User A | Allow |
| Token A resets User B | Token A | User B | Deny |
| Token B resets User B | Token B | User B | Allow |
| Token B resets User A | Token B | User A | Deny |
| Invalid token | Invalid | User A | Deny |
| Expired token | Expired | User A | Deny |
| Used token | Used | User A | Deny |
| Token A reused | Used A | User A | Deny |

---

# High-Value Findings

Prioritise issues such as:

```text
Password reset poisoning
Predictable reset tokens
OTP brute force without rate limiting
Cross-account token use
Token reuse
Missing token expiration
Workflow bypass
SSO downgrade
MFA bypass
Account identifier manipulation
Reset-token leakage
```

---

# False Positives

## Generic Reset Message

A generic response is:

```text
Good Practice
```

but does not prove enumeration is impossible.

Inspect:

```text
Status
Length
Timing
API response
Headers
```

---

# False Positive: Token Looks Structured

A token such as:

```text
UUID
JWT
Base64
```

is not automatically weak.

Assess:

```text
Cryptographic security
Validation
Expiration
Binding
Replay
```

---

# False Positive: Long Token

A long token is not automatically secure.

It may contain:

```text
Predictable encoded data
```

---

# False Positive: Missing CSRF Token

A reset endpoint without a conventional CSRF token is not automatically vulnerable.

If:

```text
High-entropy reset token
```

already provides request authorisation, traditional CSRF may not create additional impact.

Analyse the complete flow.

---

# False Positive: Existing Sessions Remain Active

Not every application must automatically invalidate all sessions after a password change.

This depends on:

```text
Threat model
Application risk
Documented policy
```

However, for security-sensitive applications, session invalidation is generally desirable.

---

# Evidence Collection

Strong evidence may include:

```text
Controlled account details
Reset request
Reset email
Reset link
Token structure
Modified request
Server response
State verification
Session behaviour
Timeline
Screenshots
Burp requests
Burp responses
```

Redact:

```text
Passwords
Tokens not needed for evidence
Personal data
```

from reports where appropriate.

---

# Example Finding: Password Reset Poisoning

```text
Finding:
Password Reset Poisoning Through X-Forwarded-Host

Observed:
The password reset functionality constructs the absolute reset URL using the X-Forwarded-Host request header.

A password reset was requested for a controlled test account while supplying a controlled external hostname through X-Forwarded-Host.

The password reset email received by the controlled account contained a valid reset link pointing to the supplied external hostname.

Impact:
An attacker who can trigger a password reset for another user may be able to cause the application to send that user a password reset link containing an attacker-controlled hostname.

If the user follows the link, the reset token may be disclosed to the attacker-controlled server, potentially allowing account takeover.

Recommendation:
Generate password reset URLs from a trusted server-side configuration value rather than incoming Host or forwarding headers. Reject unexpected Host values and configure reverse proxies to overwrite untrusted forwarding headers.
```

---

# Example Finding: Reset Token Reuse

```text
Finding:
Password Reset Tokens Remain Valid After Successful Use

Observed:
A password reset token generated for a controlled account was successfully used to change the account password.

The same token was subsequently submitted again and remained valid.

Impact:
An attacker who obtains an old reset token may retain the ability to reset the user's password even after the legitimate user has already completed the recovery process.

Recommendation:
Invalidate password reset tokens immediately after successful use. Reset tokens should be single-use, short-lived, and securely bound to the intended account and recovery purpose.
```

---

# Example Finding: Cross-Account Reset

```text
Finding:
Password Reset Token Is Not Bound to the Target Account

Observed:
Two controlled accounts were used during testing.

A valid reset token was generated for User A.

The token was then submitted to the reset endpoint while changing the account identifier to User B.

The application accepted the request and changed User B's password.

Impact:
An attacker who obtains a valid reset token for their own account may be able to use it to reset the password of another application user.

This could result in arbitrary account takeover.

Recommendation:
Bind each password reset token cryptographically or server-side to exactly one account. The target account must be derived from the validated reset token rather than from a separate client-controlled identifier.
```

---

# Example Finding: OTP Rate Limiting

```text
Finding:
Password Reset OTP Verification Lacks Effective Rate Limiting

Observed:
The password reset workflow uses a numeric one-time code.

Multiple invalid codes could be submitted for a controlled test account without meaningful throttling, lockout, or invalidation of the recovery challenge.

Impact:
An attacker may be able to systematically guess password reset codes and take over user accounts.

Recommendation:
Apply strict server-side attempt limits to password reset OTPs. Bind limits to the account and recovery challenge, use short expiration periods, invalidate challenges after excessive failures, and implement additional abuse controls where appropriate.
```

---

# Example Finding: MFA Bypass

```text
Finding:
Password Reset Workflow Bypasses Multi-Factor Authentication

Observed:
A controlled account with MFA enabled was used during testing.

After completing the password reset process, the application automatically created a fully authenticated session without requiring the configured second authentication factor.

Impact:
An attacker who compromises the password recovery channel may bypass MFA and gain complete access to the account.

Recommendation:
Ensure that password recovery does not automatically satisfy independent MFA requirements unless the recovery process itself provides equivalent assurance. Require the configured second factor before establishing a fully authenticated session.
```

---

# Example Finding: SSO Downgrade

```text
Finding:
Password Reset Allows Local Authentication for SSO-Only Accounts

Observed:
A controlled account configured to authenticate exclusively through the organisation's identity provider was submitted to the password reset workflow.

The application allowed a local password to be created and subsequently accepted direct username and password authentication.

Impact:
An attacker who compromises the recovery channel may bypass controls enforced by the organisation's identity provider, potentially including MFA and conditional access policies.

Recommendation:
Disable local password recovery for accounts configured exclusively for federated authentication unless a specifically designed and equivalently secure recovery mechanism exists.
```

---

# Reporting Titles

Useful titles include:

```text
Password Reset Poisoning Through X-Forwarded-Host

Password Reset Token Is Not Bound to the Target Account

Password Reset Tokens Remain Valid After Successful Use

Password Reset Tokens Do Not Expire

Predictable Password Reset Tokens Allow Account Takeover

Password Reset OTP Lacks Effective Rate Limiting

Password Reset Workflow Allows User Enumeration

Password Reset Workflow Bypasses Multi-Factor Authentication

Password Reset Allows Local Authentication for SSO-Only Accounts

Password Reset Token Leaks Through External Requests

Password Reset Workflow Trusts Client-Side Verification State

Password Reset Workflow Allows Verification Step Bypass

Password Reset Does Not Invalidate Existing Sessions
```

---

# Severity

Severity depends on demonstrated impact.

Examples:

```text
Minor user enumeration
→ Low / Medium depending on context

Reset email flooding
→ Low / Medium

Long-lived reset token
→ Medium depending on exposure

Reusable reset token
→ Medium / High

Reset token leakage
→ High

OTP brute force
→ High

Password reset poisoning
→ High

Cross-account token use
→ Critical / High

Predictable reset token
→ Critical / High

SSO bypass
→ High / Critical

MFA bypass
→ High
```

The important question is:

```text
Can the weakness result in
unauthorised account access?
```

---

# Remediation

A secure password reset implementation should use:

```text
Generic responses
Cryptographically random tokens
Short token lifetime
Single-use tokens
Account binding
Purpose binding
Rate limiting
Trusted URL generation
Secure email delivery
Server-side workflow state
Strong password policy
Session management
MFA-aware recovery
Audit logging
User notification
```

---

# Generate Tokens Securely

Use:

```text
Cryptographically Secure Random Number Generator
```

with sufficient entropy.

Do not derive tokens from:

```text
Username
Timestamp
User ID
Predictable random values
```

---

# Store Tokens Securely

Where practical:

```text
Store Hash(Token)
```

instead of:

```text
Store Raw Token
```

---

# Bind Token to Account

The server should know:

```text
Token
  ↓
Account
```

without relying on a separate client-controlled account identifier.

---

# Bind Token to Purpose

A password reset token should only perform:

```text
Password Reset
```

---

# Expire Tokens

Use a limited lifetime appropriate to application risk.

---

# Make Tokens Single Use

After successful reset:

```text
Token
  ↓
Immediately Invalid
```

---

# Invalidate Outstanding Tokens

After successful password reset, invalidate other outstanding recovery tokens where appropriate.

---

# Rate Limit Recovery

Protect:

```text
Reset generation
OTP validation
Token validation
Email delivery
```

against abuse.

---

# Use Generic Responses

Avoid exposing whether an account exists.

---

# Generate URLs from Trusted Configuration

Use:

```text
Configured Public Application URL
```

not:

```text
Host
X-Forwarded-Host
Forwarded
```

from untrusted requests.

---

# Restrict Forwarded Headers

Reverse proxies should:

```text
Remove untrusted forwarding headers
```

and regenerate trusted values.

---

# Protect Reset Pages

Reset pages should:

```text
Use HTTPS
Avoid unnecessary third-party resources
Restrict referrer leakage
Avoid caching sensitive responses
Avoid exposing tokens unnecessarily
```

---

# Enforce Workflow Server-Side

Do not trust:

```text
JavaScript
Hidden fields
LocalStorage
SessionStorage
Client-controlled flags
```

for recovery authorisation.

---

# Consider Session Revocation

After password reset, consider invalidating:

```text
Existing sessions
Refresh tokens
Remember-me tokens
```

according to application risk.

---

# Preserve MFA

Password reset should not silently disable or bypass:

```text
MFA
```

unless the recovery mechanism intentionally provides equivalent assurance.

---

# Protect SSO Accounts

SSO-only accounts should not unexpectedly gain:

```text
Local Password Authentication
```

through password recovery.

---

# Log Security Events

Record:

```text
Reset requested
Reset completed
Failed recovery attempts
Rate limiting
MFA recovery
Session revocation
```

without logging secrets.

---

# Notify Users

Notify users when:

```text
Password changed
Recovery completed
Security settings changed
```

This provides an additional detection mechanism.

---

# Recommended Burp Workflow

```text
Create Controlled User A
          ↓
Create Controlled User B
          ↓
Burp Proxy
          ↓
Map Complete Reset Flow
          ↓
Test Enumeration
          ↓
Request Token A
          ↓
Request Token B
          ↓
Burp Decoder
          ↓
Analyse Token Structure
          ↓
Test Account Binding
          ↓
Test Expiration
          ↓
Test Reuse
          ↓
Test Old-Token Invalidation
          ↓
Test OTP Controls
          ↓
Test Host / Forwarded Headers
          ↓
Inspect Controlled Reset Email
          ↓
Test Workflow Steps
          ↓
Test Session Behaviour
          ↓
Test MFA Behaviour
          ↓
Test SSO Behaviour
          ↓
Review Related IDOR / Logic Issues
          ↓
Use Extensions for Additional Coverage
          ↓
Manually Verify Everything
          ↓
Collect Minimal Evidence
          ↓
Restore Test Accounts
          ↓
Report
```

---

# Recommended Burp Tools

```text
Burp Proxy
    ↓
Capture entire workflow

Burp Repeater
    ↓
Manual token and workflow testing

Burp Comparer
    ↓
Enumeration and response differences

Burp Decoder
    ↓
Token structure analysis

Burp Intruder
    ↓
Small controlled input sets

Burp Sequencer
    ↓
Token randomness analysis when authorised

Burp Collaborator
    ↓
Reset poisoning / external interactions

Param Miner
    ↓
Hidden inputs and forwarding headers

Host Header Inchecktion
    ↓
Host header attack coverage

Turbo Intruder
    ↓
Controlled race/timing testing
```

---

# References

## OWASP Forgot Password Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html

Primary OWASP guidance for secure password recovery design.

---

## OWASP Authentication Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

Guidance covering secure authentication and account recovery considerations.

---

## OWASP Multifactor Authentication Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html

Guidance for MFA implementation and recovery.

---

## OWASP Password Storage Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

Guidance for secure password storage.

---

## OWASP Choosing and Using Security Questions Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Choosing_and_Using_Security_Questions_Cheat_Sheet.html

Guidance regarding security questions and account recovery.

---

## PortSwigger Password Reset Poisoning

https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning

PortSwigger Web Security Academy material covering password reset poisoning through Host header manipulation.

---

## PortSwigger Authentication Vulnerabilities

https://portswigger.net/web-security/authentication

PortSwigger Web Security Academy material covering authentication vulnerabilities, including password reset mechanisms.

---

## PortSwigger Host Header Attacks

https://portswigger.net/web-security/host-header

Background material for Host header vulnerabilities and password reset poisoning.

---

## PortSwigger Burp Sequencer

https://portswigger.net/burp/documentation/desktop/tools/sequencer

Burp Suite tool for statistical analysis of token randomness.

---

## PortSwigger Burp Collaborator

https://portswigger.net/burp/documentation/collaborator

Burp Collaborator documentation.

---

## Param Miner

https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943

Burp extension for identifying hidden parameters, headers, and cookies.

---

## Host Header Inchecktion

https://portswigger.net/bappstore/3908768b9ae945d8adf583052ad2e3b3

Burp extension for Host header injection testing.

---

## Turbo Intruder

https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988

Burp extension for specialised high-performance and timing-sensitive request testing.

GitHub:

https://github.com/PortSwigger/turbo-intruder

---

# Final Password Reset Testing Model

```text
                         PASSWORD RESET
                               ↓
                       MAP COMPLETE FLOW
                               ↓
               ┌───────────────┼────────────────┐
               ↓               ↓                ↓
            REQUEST           TOKEN           ACCOUNT
               ↓               ↓                ↓
         ENUMERATION       RANDOMNESS        BINDING
               ↓               ↓                ↓
         RATE LIMITING     EXPIRATION       USER A / B
               │               │                │
               └───────────────┼────────────────┘
                               ↓
                         TOKEN LIFECYCLE
                               ↓
                    ┌──────────┼──────────┐
                    ↓          ↓          ↓
                 SINGLE      REUSE      PURPOSE
                   USE                    BINDING
                    └──────────┼──────────┘
                               ↓
                         URL GENERATION
                               ↓
              ┌────────────────┼─────────────────┐
              ↓                ↓                 ↓
             HOST       X-FORWARDED-HOST     FORWARDED
              └────────────────┼─────────────────┘
                               ↓
                     CONTROLLED RESET EMAIL
                               ↓
                      CORRECT TRUSTED HOST?
                         ↓             ↓
                        YES            NO
                         ↓             ↓
                      CONTINUE    RESET POISONING
                         ↓
                     TOKEN LEAKAGE
                         ↓
              ┌──────────┼──────────────┐
              ↓          ↓              ↓
           REFERER     LOGGING      THIRD PARTY
              └──────────┼──────────────┘
                         ↓
                    WORKFLOW STATE
                         ↓
             ┌───────────┼────────────┐
             ↓           ↓            ↓
          OTP STEP    RESET STEP    CLIENT STATE
             ↓           ↓            ↓
         ENFORCED?    ENFORCED?    TRUSTED?
             └───────────┼────────────┘
                         ↓
                    SESSION STATE
                         ↓
             EXISTING SESSIONS / TOKENS
                         ↓
                    MFA INTERACTION
                         ↓
                  MFA STILL REQUIRED?
                    ↓             ↓
                   YES            NO
                    ↓             ↓
                 CONTINUE      INVESTIGATE
                    ↓
                    SSO
                    ↓
           SSO-ONLY ACCOUNT CAN
           CREATE LOCAL PASSWORD?
               ↓             ↓
              NO             YES
               ↓             ↓
            SECURE       INVESTIGATE
               ↓
             VERIFY
               ↓
       MINIMUM SAFE EVIDENCE
               ↓
             REPORT
```

The central principle is:

> Password reset is an authentication mechanism, not merely a convenience feature. Reset tokens and recovery challenges must be unpredictable, short-lived, single-use, securely bound to the intended account and purpose, protected against brute force and leakage, and processed entirely through trusted server-side workflow state. A user should never receive weaker authentication guarantees simply because they entered the application through account recovery rather than normal login.
