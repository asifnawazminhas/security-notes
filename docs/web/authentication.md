# Authentication Testing

Authentication is the process used by an application to verify the identity of a user.

Authentication weaknesses can allow attackers to impersonate other users, bypass security controls, compromise accounts or gain access to functionality that should require authentication.

Authentication testing should therefore examine the **entire authentication lifecycle**, not only the login form.

!!! warning "Authorised Security Testing"
    Perform authentication testing only against applications and accounts for which you have explicit authorisation. Activities such as password spraying, credential testing and account lockout testing should be specifically permitted by the rules of engagement.

---

## Objectives

Authentication testing should determine whether an attacker can:

- Identify valid usernames or accounts
- Guess or brute-force credentials
- Bypass authentication
- Abuse password reset functionality
- Circumvent MFA or 2FA
- Reuse authentication tokens
- Manipulate remember-me functionality
- Exploit alternative authentication endpoints
- Abuse registration workflows
- Exploit OAuth or OpenID Connect flows
- Exploit inconsistent authentication between web and API endpoints
- Access authenticated functionality without completing authentication
- Abuse account recovery mechanisms

A practical workflow is:

```text
Identify Authentication Surface
        ↓
Map Authentication Flows
        ↓
Test User Enumeration
        ↓
Test Password Controls
        ↓
Test Rate Limiting / Lockout
        ↓
Test Password Reset
        ↓
Test MFA / 2FA
        ↓
Test Remember-Me
        ↓
Test Alternative Endpoints
        ↓
Test Authentication State
        ↓
Test OAuth / OIDC
        ↓
Test API Authentication
        ↓
Attempt Authentication Bypass
        ↓
Document Findings
```

---

# 1. Map the Authentication Surface

Do not start by attacking `/login`.

First identify every authentication-related endpoint.

Look for:

```text
/login
/signin
/sign-in
/auth
/authenticate
/register
/signup
/logout
/password-reset
/reset-password
/forgot-password
/change-password
/mfa
/2fa
/otp
/verify
/token
/refresh
/oauth
/callback
/sso
```

Also inspect API routes:

```text
/api/login
/api/auth
/api/auth/login
/api/token
/api/token/refresh
/api/password/reset
/api/v1/auth
/api/v2/auth
```

JavaScript analysis can reveal authentication endpoints that are not directly linked from the user interface.

---

# 2. Build an Authentication Map

Record the complete authentication process.

For example:

```text
Unauthenticated User
        ↓
POST /login
        ↓
Username + Password
        ↓
MFA Challenge
        ↓
POST /verify-otp
        ↓
Session Created
        ↓
/dashboard
```

Password reset might use:

```text
User
 ↓
Forgot Password
 ↓
Email Address
 ↓
Reset Token
 ↓
Password Reset
 ↓
Login
```

SSO might use:

```text
Application
    ↓
Identity Provider
    ↓
Authentication
    ↓
Authorization Code
    ↓
Callback
    ↓
Session
```

Understanding these state transitions is essential when testing authentication bypasses.

---

# 3. Capture a Normal Login

Use Burp Suite to capture a successful login.

Example:

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=testuser&password=Password123!
```

Record:

```text
Request method
Endpoint
Parameters
Cookies
CSRF tokens
Response status
Redirect destination
Session cookie
Authentication headers
```

Then capture a failed login.

Example:

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=testuser&password=WrongPassword
```

Compare both responses.

---

# 4. User Enumeration

Applications may reveal whether an account exists.

Enumeration can occur through:

```text
Login
Registration
Password reset
Account recovery
MFA
API responses
Error messages
Response timing
HTTP status codes
Response sizes
```

---

## Login Enumeration

Compare:

```text
Valid username + invalid password
```

against:

```text
Invalid username + invalid password
```

Example:

```text
Incorrect password
```

versus:

```text
User does not exist
```

This directly reveals whether the username exists.

A safer response would be something generic such as:

```text
Invalid username or password
```

---

# 5. Response Difference Analysis

Enumeration may exist even when the visible message is identical.

Compare:

```text
HTTP status
Content-Length
Word count
Response body
Headers
Cookies
Redirects
Response timing
```

For example:

```text
Existing account:

HTTP/1.1 200 OK
Content-Length: 4210
```

versus:

```text
Non-existing account:

HTTP/1.1 200 OK
Content-Length: 4178
```

The difference may be enough to distinguish valid users.

Burp Intruder can help compare large numbers of responses.

---

# 6. Timing-Based Enumeration

Sometimes the response body is identical, but processing time differs.

Conceptually:

```text
Valid user
    ↓
Password hash comparison
    ↓
Slower response
```

while:

```text
Invalid user
    ↓
Immediate rejection
    ↓
Faster response
```

Timing differences should be tested repeatedly because normal network latency can produce misleading results.

---

# 7. Registration Enumeration

Registration functionality may reveal existing users.

Example:

```text
This email address is already registered.
```

If login attempts use generic errors but registration reveals account existence, enumeration remains possible.

Test:

```text
Username
Email address
Telephone number
Organisation identifier
```

where applicable.

---

# 8. Password Reset Enumeration

Password reset functionality frequently exposes account existence.

Compare:

```text
Password reset requested for valid account
```

with:

```text
Password reset requested for invalid account
```

Look for differences in:

```text
Message
Status
Response length
Redirect
Timing
```

A generic response could be:

```text
If an account exists for this address, reset instructions will be sent.
```

---

# 9. Password Policy

Determine the application's password requirements.

Test:

```text
Minimum length
Maximum length
Uppercase requirement
Lowercase requirement
Number requirement
Special character requirement
Password history
Common password restrictions
Username inclusion
Email inclusion
```

Do not assume a complex-looking password policy is automatically secure.

Password length and resistance to commonly used or compromised passwords are particularly important.

---

# 10. Maximum Password Length

Maximum password length can expose unusual application behaviour.

Test progressively larger passwords:

```text
20 characters
50 characters
100 characters
500 characters
```

Observe whether the application:

```text
Accepts the password
Rejects it cleanly
Truncates it
Returns an error
Behaves differently during login
```

Silent password truncation is particularly worth documenting.

---

# 11. Password Change

Authenticated password-change functionality should also be tested.

Determine whether it requires:

```text
Current password
New password
Confirmation
Recent authentication
MFA
```

Example:

```http
POST /account/change-password HTTP/1.1
Cookie: session=...

currentPassword=OldPassword&newPassword=NewPassword
```

Questions to investigate:

```text
Is the current password required?
Can another user's password be targeted?
Are existing sessions invalidated?
Are remembered devices invalidated?
Is MFA required for sensitive changes?
```

---

# 12. Brute-Force Protection

Authentication endpoints should resist repeated password guessing.

Possible controls include:

```text
Rate limiting
Progressive delays
Account lockout
IP-based restrictions
CAPTCHA
Risk-based authentication
MFA
Monitoring
```

Testing should be performed conservatively and according to the rules of engagement.

---

# 13. Rate Limiting

Send a small, authorised sequence of failed login attempts.

Observe whether:

```text
Responses slow down
429 is returned
CAPTCHA appears
Account becomes temporarily locked
Requests are blocked
Additional verification is required
```

A typical rate-limited response might be:

```http
HTTP/1.1 429 Too Many Requests
```

Potential header:

```text
Retry-After: 60
```

---

# 14. Rate-Limit Scope

Determine what the rate limit applies to.

Possible implementations include:

```text
Per IP
Per account
Per session
Per device
Per endpoint
Global
```

For example:

```text
/login
```

may be protected while:

```text
/api/login
```

is not.

Authentication controls should be consistent across equivalent endpoints.

---

# 15. Account Lockout

If account lockout testing is explicitly permitted, determine:

```text
Number of failed attempts
Lockout duration
Unlock mechanism
Whether lockout applies globally
Whether successful login resets the counter
Whether an attacker can intentionally lock users out
```

Be careful with production accounts.

Account lockout testing can cause denial of service.

---

# 16. Alternative Login Endpoints

Applications may expose multiple authentication mechanisms.

Examples:

```text
/login
/mobile/login
/api/login
/api/v1/login
/api/v2/login
/admin/login
/sso/login
```

Security controls may differ between them.

For example:

```text
/login
→ rate limited

/api/login
→ no rate limiting
```

This creates an alternative path around the intended control.

---

# 17. HTTP Method Differences

Check whether authentication endpoints behave differently with different methods.

For example:

```text
GET /login
POST /login
PUT /login
```

Do not send arbitrary state-changing methods without understanding the endpoint.

The purpose is to identify inconsistent routing or authentication handling.

---

# 18. Authentication State

Authentication often involves several stages.

For example:

```text
Password verified
      ↓
MFA pending
      ↓
Fully authenticated
```

The application must distinguish these states correctly.

A user who has passed the password stage but not MFA should not automatically receive access to authenticated functionality.

---

# 19. MFA / 2FA Testing

Multi-factor authentication introduces additional state transitions.

Typical flow:

```text
Username + Password
        ↓
Primary Authentication Successful
        ↓
MFA Challenge
        ↓
MFA Verification
        ↓
Authenticated Session
```

Test whether MFA is enforced consistently throughout the application.

---

# 20. MFA Direct Navigation

After entering valid username and password credentials but **before completing MFA**, attempt to access an authenticated page directly.

For example:

```text
/dashboard
/account
/profile
/admin
```

If the application grants access, MFA may only be enforced by the frontend workflow rather than the backend.

This is a high-value authentication test.

---

# 21. MFA API Access

The browser interface may enforce MFA while backend APIs do not.

After reaching the MFA stage, test authorised requests to endpoints such as:

```text
/api/profile
/api/account
/api/dashboard
```

The backend should recognise that authentication is incomplete.

---

# 22. MFA Session State

Observe cookies before and after MFA.

For example:

```text
Before MFA:

session=abc123
```

and:

```text
After MFA:

session=xyz789
```

or the same session may be upgraded internally.

Determine whether the pre-MFA session can access protected resources.

---

# 23. MFA Code Properties

Within the agreed scope, determine:

```text
Code length
Expiry time
Single-use behaviour
Attempt limits
Replay resistance
Association with the correct account
Association with the correct session
```

Do not perform high-volume OTP guessing unless specifically authorised.

---

# 24. MFA Replay

After successfully using an MFA code, determine whether the same code can be reused.

Expected behaviour is generally:

```text
OTP
 ↓
Successful verification
 ↓
OTP invalidated
```

A reusable OTP weakens the authentication process.

---

# 25. MFA Account Binding

An MFA challenge should be bound to the intended authentication transaction.

Conceptually:

```text
User A credentials
        ↓
MFA challenge for User A
```

The application should prevent MFA tokens associated with another account or authentication attempt from satisfying that challenge.

---

# 26. Remember-Me Functionality

Applications may provide:

```text
Remember me
Keep me signed in
Trust this device
Remember this device
```

These features often create long-lived tokens.

Inspect:

```text
Cookies
Local storage
Session storage
Token lifetime
Token rotation
```

---

# 27. Remember-Me Cookie

Example:

```http
Set-Cookie: remember_me=abc123; Max-Age=2592000
```

Investigate:

```text
Is the value predictable?
Is it signed?
Is it bound to the user?
Does logout invalidate it?
Does password change invalidate it?
Does account compromise recovery invalidate it?
```

Do not assume that a long random-looking value is secure without understanding how it is validated.

---

# 28. Logout

Logout is part of authentication security.

After logout:

```text
Replay old session cookie
      ↓
Request authenticated endpoint
```

Expected result:

```text
Session rejected
```

Test:

```text
Browser session
API tokens
Remember-me tokens
Refresh tokens
```

Logout behaviour may differ between these mechanisms.

---

# 29. Password Reset Workflow

Password reset functionality is effectively an alternative authentication mechanism.

A typical workflow is:

```text
User submits email
        ↓
Application generates token
        ↓
Token delivered to user
        ↓
User opens reset link
        ↓
New password submitted
        ↓
Token invalidated
```

Every stage should be reviewed.

---

# 30. Password Reset Token Properties

A reset token should generally be:

```text
Unpredictable
Sufficiently random
Short-lived
Single-use
Bound to the correct user
Invalidated after use
Protected during transmission
```

Also determine what happens when:

```text
A second reset token is requested
Password is changed
Email address is changed
Account is disabled
Token expires
```

---

# 31. Reset Token in URL

Reset links commonly contain:

```text
https://target.example/reset?token=...
```

Tokens appearing in URLs may potentially leak through:

```text
Browser history
Application logs
Proxy logs
Referer headers
Analytics
Third-party resources
```

Review whether sensitive reset pages load external content that could receive the reset URL through the `Referer` header.

---

# 32. Password Reset Host Handling

Some applications construct reset URLs using request-derived host information.

Example request:

```http
POST /forgot-password HTTP/1.1
Host: target.example

email=user@example.com
```

The application should use a trusted configured origin when constructing reset links.

Do not assume the `Host` header is trustworthy.

---

# 33. Reset Token Reuse

After successfully resetting a password:

```text
Reuse same reset link
```

Expected:

```text
Token rejected
```

If the token remains valid, it may allow repeated password changes.

---

# 34. Reset Token Expiry

Determine whether reset tokens expire within a reasonable period.

Test:

```text
Immediate use
Later use
Use after password change
Use after requesting another reset
```

Record observed behaviour.

---

# 35. Password Reset Session Handling

After a password reset, consider whether existing authenticated sessions remain valid.

Depending on the application's security requirements, sensitive applications may invalidate existing sessions following a password reset.

This is especially important when password reset is used for account recovery after suspected compromise.

---

# 36. Account Recovery

Account recovery may use:

```text
Email
SMS
Recovery codes
Security questions
Support processes
Backup email addresses
Trusted devices
```

The recovery mechanism should not be weaker than the authentication mechanism it replaces.

For example:

```text
Strong password + MFA
        ↓
Weak security question
        ↓
Account recovered
```

would undermine the stronger authentication controls.

---

# 37. Security Questions

If security questions are used, consider:

```text
Are answers easily guessable?
Can answers be discovered publicly?
Are multiple attempts permitted?
Are answers compared case-sensitively?
Can users choose weak questions?
```

Security questions are generally weaker than modern recovery mechanisms.

---

# 38. Registration Testing

Registration is part of the authentication lifecycle.

Review:

```text
Account enumeration
Email verification
Duplicate accounts
Password policy
Role assignment
Invite codes
Organisation membership
Default permissions
```

---

# 39. Email Verification

A typical registration flow:

```text
Register
   ↓
Verification email
   ↓
Verification token
   ↓
Account activated
```

Determine whether the application allows protected functionality before verification.

Also inspect whether verification tokens are:

```text
Single-use
Time-limited
Bound to the correct account
```

---

# 40. Registration Role Assignment

Inspect registration requests for fields such as:

```text
role
admin
isAdmin
permissions
group
accountType
organisation
```

Example:

```json
{
  "username": "test",
  "email": "test@example.com",
  "role": "user"
}
```

The server should not trust client-controlled privilege fields.

This should later be combined with authorisation and mass-assignment testing.

---

# 41. Authentication Cookies

After successful authentication, inspect session cookies.

Example:

```http
Set-Cookie: session=abc123;
    Secure;
    HttpOnly;
    SameSite=Lax
```

Important attributes include:

```text
Secure
HttpOnly
SameSite
Path
Domain
Max-Age
Expires
```

---

# 42. Secure Cookie Attribute

Sensitive authentication cookies should generally use:

```text
Secure
```

This prevents browsers from transmitting them over unencrypted HTTP connections.

---

# 43. HttpOnly

Authentication cookies should normally use:

```text
HttpOnly
```

This prevents ordinary client-side JavaScript from reading the cookie.

It does not prevent all consequences of XSS, but it can reduce direct session token theft.

---

# 44. SameSite

Review:

```text
SameSite=Strict
SameSite=Lax
SameSite=None
```

If:

```text
SameSite=None
```

is used, browsers require:

```text
Secure
```

The appropriate setting depends on legitimate cross-site application requirements.

---

# 45. Session Fixation

Determine whether the session identifier changes after authentication.

Conceptually:

```text
Before login:
session=AAA

After login:
session=AAA
```

may warrant investigation.

A stronger pattern is:

```text
Before login:
session=AAA

After login:
session=BBB
```

Session regeneration after authentication reduces session fixation risk.

---

# 46. Session Token Entropy

Authentication tokens should not be predictable.

Avoid conclusions based solely on visual appearance.

A token such as:

```text
8f14e45fceea167a5a36dedd4bea2543
```

may look random without actually being unpredictable.

Where relevant, collect a safe number of tokens and examine:

```text
Length
Character set
Repeated structure
Static portions
Timestamp-like portions
User-related information
```

---

# 47. JWT Authentication

Applications may use JSON Web Tokens.

Typical header:

```http
Authorization: Bearer eyJ...
```

JWT structure:

```text
HEADER.PAYLOAD.SIGNATURE
```

Decode the token to understand claims.

For example:

```json
{
  "sub": "123",
  "role": "user",
  "iat": 1710000000,
  "exp": 1710003600
}
```

Review:

```text
Algorithm
Expiration
Issuer
Audience
Subject
Roles
Permissions
Token type
```

---

# 48. JWT Security Questions

Determine:

```text
Is the signature verified?
Are accepted algorithms restricted?
Is expiration enforced?
Is issuer validated?
Is audience validated?
Are access and refresh tokens distinguished?
Are privileges derived safely?
```

Never assume that modifying the decoded payload changes server-side privileges.

The server should reject modified tokens when signature validation is working correctly.

---

# 49. Access and Refresh Tokens

Modern applications often use:

```text
Access token
+
Refresh token
```

Typical lifecycle:

```text
Login
 ↓
Access Token
 ↓
API Requests
 ↓
Access Token Expires
 ↓
Refresh Token
 ↓
New Access Token
```

Review:

```text
Token lifetime
Storage
Rotation
Revocation
Logout behaviour
Password-change behaviour
Reuse detection
```

Refresh tokens deserve particular attention because they are often longer-lived.

---

# 50. API Authentication

Web and API authentication should be tested independently.

Possible API authentication mechanisms include:

```text
Session cookies
Bearer tokens
JWT
API keys
OAuth
Mutual TLS
Custom headers
```

An application may protect:

```text
/dashboard
```

while accidentally exposing:

```text
/api/dashboard
```

without equivalent authentication.

---

# 51. Unauthenticated API Access

After mapping API endpoints, request them without authentication.

For example:

```http
GET /api/profile HTTP/1.1
Host: target.example
```

Expected behaviour might be:

```http
HTTP/1.1 401 Unauthorized
```

Test relevant endpoints systematically rather than assuming frontend protection represents backend protection.

---

# 52. Authentication Header Removal

Take an authenticated API request:

```http
GET /api/profile HTTP/1.1
Authorization: Bearer TOKEN
```

Remove:

```text
Authorization
```

and resend.

The endpoint should reject the request if authentication is required.

Also test the behaviour of:

```text
Empty token
Malformed token
Expired token
Invalid token
```

---

# 53. Cookie Removal

For cookie-based applications, remove the session cookie.

Example:

```http
GET /account HTTP/1.1
Host: target.example
```

instead of:

```http
Cookie: session=abc123
```

Confirm the application does not rely solely on frontend routing to protect the page.

---

# 54. Direct Endpoint Access

Applications sometimes enforce authentication only through navigation.

If:

```text
/login
   ↓
/dashboard
```

try requesting authenticated endpoints directly while unauthenticated.

Examples:

```text
/dashboard
/account
/profile
/settings
/admin
/api/profile
```

The server should independently enforce authentication.

---

# 55. Authentication Bypass Through Workflow

Authentication systems often contain multiple states.

Example:

```text
POST /login
      ↓
POST /mfa
      ↓
GET /dashboard
```

Test whether stages can be skipped:

```text
POST /login
      ↓
GET /dashboard
```

or whether protected API functionality becomes accessible before the workflow is complete.

This is particularly important for:

```text
MFA
Email verification
Password-change requirements
Terms acceptance
Account activation
```

---

# 56. Forced Password Change

Some applications require a user to change a temporary password.

Example:

```text
Login with temporary password
        ↓
/change-password
        ↓
Dashboard
```

Determine whether the user can directly access:

```text
/dashboard
/api/
```

without completing the mandatory password change.

---

# 57. Authentication Across Roles

Where multiple authorised test accounts are available, compare:

```text
Normal user
Administrator
Support user
Read-only user
Service account
```

Authentication behaviour may differ between roles.

For example:

```text
Normal user → MFA required
Administrator → MFA required
Legacy admin API → MFA not required
```

Such inconsistencies can expose alternative authentication paths.

---

# 58. Default Credentials

Where the technology or product legitimately supports default credentials, determine whether defaults have been changed.

This is especially relevant for:

```text
Administrative interfaces
Monitoring systems
Development tools
Network appliances
Self-hosted products
```

Testing default credentials should be explicitly permitted and limited to known relevant combinations rather than broad password guessing.

---

# 59. SSO

Applications may delegate authentication to an identity provider.

Examples:

```text
Microsoft Entra ID
Google
Okta
Auth0
Keycloak
AD FS
```

Map:

```text
Application
    ↓
Identity Provider
    ↓
Authentication
    ↓
Application Callback
    ↓
Session
```

Determine which component is responsible for each security decision.

---

# 60. OAuth 2.0

OAuth is primarily an authorisation framework, but it is frequently involved in authentication architectures.

Common endpoints include:

```text
/authorize
/token
/callback
/oauth
/oauth2
```

Common parameters include:

```text
client_id
redirect_uri
response_type
scope
state
code
code_challenge
code_challenge_method
```

---

# 61. OpenID Connect

OpenID Connect adds an identity layer to OAuth 2.0.

Look for:

```text
openid
id_token
userinfo
nonce
```

Discovery metadata may be available at:

```text
/.well-known/openid-configuration
```

This can describe:

```text
authorization_endpoint
token_endpoint
userinfo_endpoint
jwks_uri
issuer
supported algorithms
```

---

# 62. OAuth / OIDC Mapping

Record:

```text
Identity provider
Client ID
Redirect URI
Response type
Scopes
State parameter
Nonce
PKCE
Callback endpoint
Token endpoint
```

Example flow:

```text
Application
    ↓
/authorize
    ↓
Identity Provider
    ↓
Authorization Code
    ↓
/callback
    ↓
/token
    ↓
Application Session
```

---

# 63. OAuth State

The `state` parameter is commonly used to bind the OAuth response to the initiating browser session and help protect against request-forgery attacks.

Example:

```text
state=random-value
```

Review whether:

```text
State exists
State is unpredictable
State is validated
State is associated with the correct session
```

---

# 64. OIDC Nonce

OpenID Connect may use:

```text
nonce
```

to bind an ID token to an authentication request and reduce token replay risks.

Review whether it is generated and validated appropriately when the flow requires it.

---

# 65. PKCE

Modern OAuth flows often use Proof Key for Code Exchange.

Look for:

```text
code_challenge
code_challenge_method
code_verifier
```

Common secure configuration:

```text
code_challenge_method=S256
```

PKCE is particularly important for public clients.

---

# 66. OAuth Redirect URI

The identity provider should restrict where authorisation responses can be sent.

Review:

```text
redirect_uri
```

The value should be validated against registered application redirect URIs according to the provider's security model.

Loose redirect URI validation can undermine the authentication flow.

---

# 67. SAML

Enterprise applications may use SAML-based SSO.

Typical flow:

```text
Service Provider
      ↓
Identity Provider
      ↓
SAML Response
      ↓
Service Provider
      ↓
Authenticated Session
```

Important areas include:

```text
Signature validation
Audience validation
Recipient validation
Destination validation
Assertion expiry
Replay prevention
Identity mapping
```

Detailed SAML testing can be maintained as a dedicated note if needed.

---

# 68. Authentication in JavaScript

JavaScript analysis can reveal:

```text
Authentication endpoints
Token storage
Token refresh logic
Role checks
MFA endpoints
OAuth configuration
Client IDs
Redirect URIs
```

Search:

```bash
grep -RniE \
'login|logout|signin|password|token|jwt|bearer|oauth|oidc|mfa|2fa|otp|session' \
javascript/
```

---

# 69. Client-Side Token Storage

Search:

```bash
grep -RniE \
'localStorage|sessionStorage|document\.cookie' \
javascript/
```

Example:

```javascript
localStorage.setItem("access_token", token);
```

Document where authentication tokens are stored because this influences the impact of client-side vulnerabilities.

---

# 70. Authentication Responses

Do not only inspect whether authentication succeeded.

Compare:

```text
Status
Headers
Cookies
Body
Redirect
Timing
```

Example:

```text
Successful login:

302 → /dashboard
Set-Cookie: session=...
```

versus:

```text
Failed login:

200
Invalid username or password
```

These differences are useful when understanding authentication behaviour.

---

# 71. Burp Repeater Workflow

For each authentication request:

```text
Capture
   ↓
Send to Repeater
   ↓
Establish Baseline
   ↓
Modify One Element
   ↓
Send
   ↓
Compare
   ↓
Record Behaviour
```

Modify one thing at a time whenever possible.

For example:

```text
Username
Password
Cookie
Token
MFA code
Reset token
HTTP method
Content type
```

This makes behavioural differences easier to understand.

---

# 72. Burp Intruder

Burp Intruder can help with controlled testing of:

```text
User enumeration
Small password-policy tests
Rate-limit behaviour
OTP handling
Parameter behaviour
Response differences
```

Configure appropriate:

```text
Payload positions
Request rate
Resource pools
Response matching
Response length analysis
```

Avoid uncontrolled high-volume testing against production systems.

---

# 73. Burp Comparer

When authentication responses look almost identical, use:

```text
Burp Suite
→ Comparer
```

Compare:

```text
Valid username response
Invalid username response
```

or:

```text
Successful authentication state
Incomplete authentication state
```

Small differences may reveal application logic.

---

# 74. Burp Decoder

Burp Decoder can help inspect:

```text
JWT components
Base64 values
URL-encoded parameters
Hex values
Encoded state parameters
```

Remember that encoding is not encryption.

---

# 75. Content-Type Differences

Authentication endpoints may accept multiple request formats.

For example:

```text
application/x-www-form-urlencoded
```

versus:

```text
application/json
```

Example:

```http
POST /api/login
Content-Type: application/json

{
  "username": "test",
  "password": "Password123!"
}
```

Compare security controls across supported interfaces.

---

# 76. Case Sensitivity

Determine whether usernames are case-sensitive.

For example:

```text
asif
Asif
ASIF
```

Applications should handle identity normalisation consistently.

Inconsistent case handling can create unusual account or authorisation behaviour.

---

# 77. Email Canonicalisation

Where email addresses are usernames, examine how addresses are normalised.

Potential differences include:

```text
Uppercase / lowercase
Whitespace
Unicode
Provider-specific behaviour
```

The application should use consistent canonicalisation during:

```text
Registration
Login
Password reset
Account lookup
```

---

# 78. Authentication Error Handling

Authentication endpoints should not expose unnecessary internal information.

Look for:

```text
Stack traces
Database errors
Framework errors
LDAP errors
Internal usernames
Directory paths
Identity provider errors
```

Example:

```text
LDAP user CN=testuser not found
```

may reveal unnecessary implementation details.

---

# 79. Authentication Logging

Where assessment access permits reviewing logs or detection controls, determine whether security-relevant events are recorded.

Examples:

```text
Repeated failed login
Account lockout
Password reset
MFA failure
MFA reset
Successful login
New device
Password change
Suspicious authentication
```

This is particularly useful during purple-team assessments.

---

# 80. Authentication Testing Matrix

Maintain a testing matrix.

| Area | Test | Result |
|---|---|---|
| Login | User enumeration | |
| Login | Rate limiting | |
| Login | Account lockout | |
| Login | Alternative endpoints | |
| Password | Password policy | |
| Password | Password change | |
| Recovery | User enumeration | |
| Recovery | Token expiry | |
| Recovery | Token reuse | |
| MFA | Direct navigation bypass | |
| MFA | API bypass | |
| MFA | Replay | |
| Session | Session regeneration | |
| Session | Logout invalidation | |
| JWT | Expiry validation | |
| API | Missing authentication | |
| OAuth | State validation | |
| OAuth | Redirect URI validation | |
| OIDC | Nonce handling | |
| Registration | Verification enforcement | |

---

# 81. Prioritisation

Authentication findings can be prioritised conceptually as:

```text
Authentication Bypass
        ↓
MFA Bypass
        ↓
Account Takeover
        ↓
Password Reset Weakness
        ↓
Token Weakness
        ↓
Brute-Force Weakness
        ↓
User Enumeration
        ↓
Information Disclosure
```

Actual severity depends on:

```text
Exploitability
Required privileges
Account type
MFA presence
Available mitigations
Business impact
```

---

# 82. Example Authentication Assessment Workflow

A practical assessment might proceed as follows.

## Step 1: Discover

Identify:

```text
/login
/register
/forgot-password
/reset-password
/mfa
/api/auth
/oauth
```

## Step 2: Baseline

Capture:

```text
Successful login
Failed login
Logout
Password reset
MFA verification
```

## Step 3: Enumeration

Compare:

```text
Valid user
Invalid user
```

across:

```text
Login
Registration
Password reset
```

## Step 4: Password Controls

Review:

```text
Password policy
Rate limiting
Lockout
Password change
```

## Step 5: Recovery

Review:

```text
Reset token
Expiry
Reuse
Session invalidation
```

## Step 6: MFA

Review:

```text
Workflow enforcement
Direct navigation
API access
OTP lifetime
OTP reuse
```

## Step 7: Sessions

Review:

```text
Session regeneration
Cookie attributes
Logout
Remember-me
```

## Step 8: Tokens

Review:

```text
JWT
Access token
Refresh token
Revocation
```

## Step 9: SSO

Review:

```text
OAuth
OIDC
SAML
```

## Step 10: Alternative Interfaces

Compare:

```text
Web
Mobile API
REST API
Legacy API
Admin interface
```

---

# 83. Authentication Attack Surface Map

The complete authentication surface can be visualised as:

```text
                       Authentication
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
        Login           Registration         Recovery
          │                  │                  │
          ├─ Password        ├─ Verification    ├─ Reset Token
          ├─ Rate Limit      ├─ Roles           ├─ Recovery Codes
          ├─ Lockout         └─ Activation      └─ Support Flow
          │
          ├──────────── MFA
          │               │
          │               ├─ OTP
          │               ├─ Push
          │               ├─ Recovery
          │               └─ Trusted Device
          │
          └──────────── Session
                          │
                          ├─ Cookie
                          ├─ JWT
                          ├─ Access Token
                          ├─ Refresh Token
                          └─ Remember-Me

                       Federation
                           │
                    ┌──────┼──────┐
                    │      │      │
                  OAuth   OIDC   SAML
```

Testing should consider the relationships between these components rather than treating each one in isolation.

---

# 84. Authentication Checklist

## Authentication Surface

- [ ] Identify login endpoints
- [ ] Identify registration endpoints
- [ ] Identify password-reset endpoints
- [ ] Identify MFA endpoints
- [ ] Identify API authentication
- [ ] Identify SSO
- [ ] Identify alternative login endpoints
- [ ] Identify legacy authentication endpoints

## User Enumeration

- [ ] Login responses
- [ ] Registration responses
- [ ] Password reset responses
- [ ] MFA responses
- [ ] API responses
- [ ] Status differences
- [ ] Response-length differences
- [ ] Timing differences

## Password Security

- [ ] Minimum password length
- [ ] Maximum password length
- [ ] Common password controls
- [ ] Password change
- [ ] Current-password requirement
- [ ] Password history
- [ ] Password reset
- [ ] Session invalidation after reset

## Brute-Force Protection

- [ ] Rate limiting
- [ ] Progressive delays
- [ ] Account lockout
- [ ] CAPTCHA
- [ ] Alternative endpoints
- [ ] API rate limiting
- [ ] Lockout denial-of-service considerations

## MFA

- [ ] MFA enforced server-side
- [ ] Direct navigation tested
- [ ] API access tested
- [ ] OTP expiry
- [ ] OTP replay
- [ ] Attempt limits
- [ ] Session state before MFA
- [ ] Recovery mechanism
- [ ] Trusted-device behaviour

## Password Reset

- [ ] User enumeration
- [ ] Token randomness
- [ ] Token expiry
- [ ] Token reuse
- [ ] Account binding
- [ ] Host handling
- [ ] Existing-session behaviour
- [ ] Reset token leakage considerations

## Registration

- [ ] Email verification
- [ ] Duplicate accounts
- [ ] Role parameters
- [ ] Organisation assignment
- [ ] Account activation
- [ ] Default permissions

## Sessions

- [ ] Session ID changes after login
- [ ] Secure cookie attribute
- [ ] HttpOnly
- [ ] SameSite
- [ ] Logout invalidation
- [ ] Remember-me invalidation
- [ ] Password-change invalidation

## JWT / Tokens

- [ ] Signature validation
- [ ] Algorithm restrictions
- [ ] Expiry
- [ ] Issuer
- [ ] Audience
- [ ] Token type
- [ ] Access-token lifetime
- [ ] Refresh-token handling
- [ ] Revocation
- [ ] Rotation

## OAuth / OIDC

- [ ] Identify provider
- [ ] Map flow
- [ ] State validation
- [ ] Nonce validation
- [ ] Redirect URI validation
- [ ] PKCE
- [ ] Scope handling
- [ ] Callback endpoint
- [ ] Token handling

## API Authentication

- [ ] Unauthenticated endpoint access
- [ ] Remove authentication header
- [ ] Remove session cookie
- [ ] Invalid token
- [ ] Expired token
- [ ] Alternative API versions
- [ ] Authentication consistency

---

# 85. Quick Reference

## Authentication Endpoints

```text
/login
/signin
/auth
/register
/signup
/logout
/forgot-password
/reset-password
/change-password
/mfa
/2fa
/otp
/verify
/token
/refresh
/oauth
/callback
/sso
```

## Authentication Keywords

```text
login
logout
password
token
jwt
bearer
session
auth
oauth
oidc
saml
mfa
2fa
otp
reset
refresh
remember
```

## JavaScript Search

```bash
grep -RniE \
'login|logout|password|token|jwt|bearer|session|oauth|oidc|mfa|2fa|otp' \
javascript/
```

## Token Storage Search

```bash
grep -RniE \
'localStorage|sessionStorage|document\.cookie' \
javascript/
```

## OIDC Discovery

```text
/.well-known/openid-configuration
```

---

# 86. Key Principle

Authentication testing should not be approached as:

```text
Find /login
     ↓
Try passwords
     ↓
Done
```

A better methodology is:

```text
Discover
   ↓
Map
   ↓
Understand State
   ↓
Compare Behaviour
   ↓
Test Controls
   ↓
Test Alternative Paths
   ↓
Test Recovery
   ↓
Test MFA
   ↓
Test Tokens
   ↓
Test Federation
   ↓
Validate Server-Side Enforcement
```

The central question is:

> Can the application reliably prove that the user is who they claim to be at every stage of the authentication lifecycle?

Authentication is a **system of interconnected workflows**, not simply a login form.

---

# 87. Relationship With Other Testing

Authentication testing connects directly to several other areas:

```text
Authentication
      │
      ├── Session Cookies
      │       ↓
      │   Session Management
      │
      ├── User / Account IDs
      │       ↓
      │   Authorisation
      │
      ├── JWT / OAuth
      │       ↓
      │   API Security
      │
      ├── Password Reset
      │       ↓
      │   Account Takeover
      │
      ├── Redirect Parameters
      │       ↓
      │   Open Redirect
      │
      ├── Client-Side Tokens
      │       ↓
      │   XSS Impact
      │
      └── SSO
              ↓
          OAuth / OIDC / SAML
```

A weakness in one authentication component can undermine otherwise strong controls elsewhere.

---

# References

Useful references for further study:

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy: Authentication](https://portswigger.net/web-security/authentication){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy: OAuth](https://portswigger.net/web-security/oauth){ target="_blank" rel="noopener noreferrer" }
- [OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700){ target="_blank" rel="noopener noreferrer" }
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html){ target="_blank" rel="noopener noreferrer" }

---

## Related Notes

Continue with:

- [Web Application Security Overview](index.md)
- [Web Application Testing Methodology](methodology.md)
- [Pentesting Checklist](checklist.md)
- [Authorisation](authorisation.md)
- [Session Management](session-management.md)
- [API Security](api-security.md)
- [Cross-Site Scripting](xss.md)
