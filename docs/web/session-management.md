# Session Management

Session management controls how an application maintains a user's authenticated state across multiple HTTP requests.

Because HTTP is stateless, applications typically use session cookies, tokens, or other identifiers to associate requests with an authenticated user.

Weak session management can allow an attacker to hijack authenticated sessions, bypass authentication controls, maintain unauthorised access, or access another user's account.

!!! warning "Authorised Security Testing"
    Perform session management testing only against systems for which you have explicit authorisation. Use dedicated test accounts where possible and avoid accessing data belonging to real users.

---

## Objectives

Session management testing should determine whether:

- session identifiers are generated securely
- session identifiers contain sufficient entropy
- session cookies use appropriate security attributes
- sessions are invalidated correctly
- logout terminates the server-side session
- password changes invalidate existing sessions where appropriate
- authentication state is correctly enforced
- sessions expire after an appropriate period
- concurrent sessions are handled securely
- session identifiers are not exposed unnecessarily
- session fixation is prevented
- tokens cannot be replayed after invalidation
- sensitive operations require appropriate reauthentication

---

# Session Management Testing Methodology

A practical session management assessment can generally be approached as:

```text
Identify Session Mechanism
        ↓
Inspect Cookies and Tokens
        ↓
Analyse Session Identifier
        ↓
Test Session Rotation
        ↓
Test Session Fixation
        ↓
Test Logout
        ↓
Test Session Expiration
        ↓
Test Password Change Behaviour
        ↓
Test Concurrent Sessions
        ↓
Test Session Replay
        ↓
Test Cross-Account Behaviour
        ↓
Test Sensitive Operations
        ↓
Document Findings
```

---

# Identify the Session Mechanism

Start by determining how the application maintains authentication state.

Common mechanisms include:

```text
Cookies
JWTs
Bearer tokens
API tokens
Session IDs
OAuth tokens
Refresh tokens
Custom authentication headers
```

Use an intercepting proxy such as Burp Suite to compare requests before and after authentication.

Example:

```http
GET /account HTTP/1.1
Host: example.com
Cookie: session=abc123
```

The authentication state may depend entirely on:

```text
session=abc123
```

Alternatively:

```http
Authorization: Bearer eyJhbGciOi...
```

Determine which value actually controls the authenticated session.

---

# Identify Session Cookies

Review the `Set-Cookie` headers returned during authentication.

Example:

```http
HTTP/1.1 200 OK
Set-Cookie: session=abc123; Path=/; Secure; HttpOnly; SameSite=Lax
```

Record:

```text
Cookie name
Cookie value
Domain
Path
Secure
HttpOnly
SameSite
Expiration
```

Multiple cookies may be present.

For example:

```text
session
JSESSIONID
PHPSESSID
ASP.NET_SessionId
connect.sid
auth_token
remember_me
```

Do not assume every cookie is security sensitive. Determine which cookies affect authentication state.

---

# Cookie Security Attributes

Important cookie attributes should be reviewed.

## Secure

The `Secure` attribute prevents the browser from transmitting the cookie over plaintext HTTP connections.

Expected:

```http
Set-Cookie: session=abc123; Secure
```

A sensitive authentication cookie without `Secure` may potentially be exposed over an insecure connection.

---

## HttpOnly

The `HttpOnly` attribute prevents normal client-side JavaScript from directly reading the cookie.

Expected:

```http
Set-Cookie: session=abc123; HttpOnly
```

This provides additional protection against session theft through certain cross-site scripting scenarios.

It does not prevent XSS itself.

---

## SameSite

The `SameSite` attribute controls when browsers include cookies in cross-site requests.

Common values:

```text
Strict
Lax
None
```

Example:

```http
Set-Cookie: session=abc123; SameSite=Lax
```

If `SameSite=None` is used, modern browsers generally require:

```text
Secure
```

Example:

```http
Set-Cookie: session=abc123; SameSite=None; Secure
```

Do not treat `SameSite` as a complete replacement for CSRF protection.

---

## Domain

Review whether the cookie is unnecessarily available to subdomains.

Example:

```http
Domain=.example.com
```

This could expose the cookie to:

```text
app.example.com
api.example.com
legacy.example.com
dev.example.com
```

Where possible, sensitive cookies should have the narrowest appropriate scope.

---

## Path

Review the cookie path.

Example:

```http
Path=/
```

A broader path makes the cookie available to more application routes.

Determine whether this is necessary for the application's design.

---

# Inspect Cookies in Burp Suite

In Burp Suite:

```text
Proxy
    ↓
HTTP history
    ↓
Select authenticated request
    ↓
Inspect Cookie header
```

Example:

```http
Cookie: session=abc123; preferences=dark
```

Remove cookies individually and resend the request.

For example:

```http
Cookie: preferences=dark
```

If authentication disappears, the removed cookie is likely responsible for maintaining the authenticated session.

Burp Repeater is particularly useful for this.

---

# Session Identifier Analysis

Session identifiers should be unpredictable.

Potential warning signs include identifiers based on:

```text
Username
Email address
Timestamp
Sequential number
User ID
Incrementing database ID
Predictable random values
Encoded user information
```

Example of a suspicious pattern:

```text
10001
10002
10003
10004
```

Another example:

```text
user123:1693400000
```

A secure session identifier should generally be generated using a cryptographically secure random mechanism.

---

# Collect Multiple Session Identifiers

Authenticate repeatedly and collect multiple session values.

Example:

```text
Session 1: f62a76f6dfe349fdbe7d...
Session 2: 03f84ab71b7447d493f9...
Session 3: 9c739a8f6f5347a198e2...
Session 4: 38bc2c9e83f74cf29bb7...
```

Look for:

```text
Repeated sections
Sequential values
Timestamp patterns
Constant prefixes
Constant suffixes
Encoded usernames
Predictable changes
```

Burp Sequencer can assist with statistical analysis of session tokens.

---

# Burp Sequencer

Burp Suite includes Sequencer for analysing token randomness.

Typical workflow:

```text
Proxy
    ↓
Identify response containing session token
    ↓
Send to Sequencer
    ↓
Configure token location
    ↓
Start live capture
```

Sequencer can analyse characteristics such as:

```text
Character distribution
Entropy
Bit-level randomness
Token correlation
Predictability indicators
```

Automated statistical analysis should support manual investigation rather than replace it.

---

# Session Rotation

Applications should generally issue a new session identifier when authentication state changes.

Capture the session before authentication:

```text
session=AAA
```

Authenticate.

Then inspect the session again:

```text
session=BBB
```

Ideally:

```text
AAA != BBB
```

This is particularly important when transitioning from:

```text
Unauthenticated
        ↓
Authenticated
```

It may also be appropriate when:

```text
Privilege changes
MFA completes
Password changes
Account recovery completes
Security-sensitive authentication state changes
```

---

# Session Fixation

Session fixation occurs when an attacker can establish or predict a session identifier before authentication and the application continues using that same identifier after the victim authenticates.

Basic test:

```text
1. Visit application while unauthenticated
2. Record session identifier
3. Authenticate
4. Record session identifier again
5. Compare both values
```

Example:

Before login:

```text
session=ABC123
```

After login:

```text
session=ABC123
```

This deserves further investigation.

Expected behaviour will commonly resemble:

```text
Before login:

session=ABC123

After login:

session=F9D2A7E81...
```

The application should normally rotate the relevant session identifier when authentication occurs.

---

# Logout Testing

Logout should invalidate the authenticated session.

Basic procedure:

```text
1. Authenticate
2. Capture authenticated request
3. Send request to Burp Repeater
4. Log out normally
5. Replay the captured request
```

Example captured request:

```http
GET /account HTTP/1.1
Host: example.com
Cookie: session=abc123
```

After logout, replay it.

Expected result:

```text
Redirect to login
401 Unauthorized
403 Forbidden
Session invalid response
```

Potential vulnerability:

```text
Authenticated content is still returned
```

This can indicate that logout only removed the browser cookie without invalidating the server-side session.

---

# Browser Cookie Deletion vs Server-Side Invalidation

A logout response might contain:

```http
Set-Cookie: session=; Max-Age=0
```

This deletes the browser cookie.

However, this alone does not prove the session was invalidated on the server.

Always replay the original session identifier.

For example:

```http
Cookie: session=OLD_SESSION_VALUE
```

If it remains authenticated, logout may not properly invalidate the session.

---

# Session Expiration

Sessions should not remain valid indefinitely.

Test both:

```text
Idle timeout
Absolute timeout
```

---

## Idle Timeout

An idle timeout terminates a session after a period of inactivity.

Example:

```text
Login
↓
Wait without sending requests
↓
Replay authenticated request
```

The appropriate timeout depends on the application's risk profile and business requirements.

---

## Absolute Timeout

An absolute timeout limits the total lifetime of a session regardless of activity.

Example:

```text
Login
↓
Continue using application
↓
Session eventually expires
↓
Reauthentication required
```

Applications handling sensitive information may require stricter session lifetime controls.

---

# Password Change Testing

Determine what happens to existing sessions when the password changes.

Practical test:

```text
Browser A
Login to account

Browser B
Login to same account

Browser A
Change password

Browser B
Refresh authenticated page
```

Determine whether Browser B remains authenticated.

Possible behaviours include:

```text
All sessions invalidated
Only current session remains
Other sessions remain active
User chooses whether other sessions are terminated
```

The correct behaviour depends on the application's design and risk model.

However, applications should deliberately manage this behaviour rather than leaving stale sessions active unintentionally.

---

# Password Reset Testing

Password resets should also be tested against existing sessions.

Procedure:

```text
1. Login in Browser A
2. Initiate password reset separately
3. Complete password reset
4. Return to Browser A
5. Attempt authenticated actions
```

Determine whether the old session remains valid.

This is especially important where password reset is intended to recover an account after suspected compromise.

---

# Concurrent Sessions

Determine whether the application allows multiple active sessions for the same account.

Example:

```text
Chrome
Firefox
Mobile browser
API client
```

Authenticate using the same account.

Then determine:

```text
Are all sessions active?
Can the user view active sessions?
Can individual sessions be revoked?
Does logout affect only one session?
Does "logout everywhere" exist?
```

Multiple concurrent sessions are not automatically a vulnerability.

The important question is whether session behaviour matches the security requirements of the application.

---

# Session Revocation

Applications may provide functionality such as:

```text
Active Sessions
Connected Devices
Security Sessions
Login Activity
Sign Out Other Sessions
Sign Out Everywhere
```

Test whether revocation actually invalidates the selected session.

Procedure:

```text
Browser A
        ↓
Login

Browser B
        ↓
Login

Browser A
        ↓
Revoke Browser B

Browser B
        ↓
Replay authenticated request
```

Browser B should no longer have access if revocation succeeded.

---

# Session Replay

Capture an authenticated request:

```http
GET /profile HTTP/1.1
Host: example.com
Cookie: session=abc123
```

After an event expected to invalidate the session, replay the request.

Events worth testing include:

```text
Logout
Password change
Password reset
Account lock
Session revocation
Account disablement
MFA reset
Role change
```

Determine whether the old session remains usable.

---

# Cross-Account Session Testing

Use two test accounts:

```text
Account A
Account B
```

Capture the session for both.

Example:

```text
Account A → session=AAA
Account B → session=BBB
```

Test application behaviour carefully when switching between authenticated contexts.

Look for:

```text
Session confusion
Cached user data
Incorrect account association
Privilege leakage
Cross-user responses
```

Always use accounts specifically authorised for testing.

---

# Session Cookie Manipulation

Test whether modifying the session cookie affects identity or privileges.

Example:

```http
Cookie: role=user
```

Change:

```http
Cookie: role=admin
```

or:

```http
Cookie: user_id=1001
```

to:

```http
Cookie: user_id=1002
```

The application must not trust client-controlled values for security decisions without appropriate integrity protection and server-side authorisation.

---

# Encoded Session Values

Some session values may simply contain encoded data.

Example:

```text
dXNlcj1hc2lmJnJvbGU9dXNlcg==
```

Base64 decoding may reveal:

```text
user=asif&role=user
```

Linux:

```bash
echo 'dXNlcj1hc2lmJnJvbGU9dXNlcg==' | base64 -d
```

Encoding is not encryption.

Do not assume a value is securely protected merely because it is not immediately human readable.

---

# JWT-Based Sessions

Some applications use JSON Web Tokens for authentication.

Example:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

A JWT normally consists of:

```text
HEADER.PAYLOAD.SIGNATURE
```

Example structure:

```text
xxxxx.yyyyy.zzzzz
```

Decode the header and payload to understand the claims.

Typical payload:

```json
{
  "sub": "123",
  "username": "testuser",
  "role": "user",
  "iat": 1693400000,
  "exp": 1693403600
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
Token lifetime
Refresh behaviour
Revocation behaviour
```

JWT testing should be considered part of both authentication and session management.

---

# Access Tokens and Refresh Tokens

Modern applications may use:

```text
Access token
Refresh token
```

Typical model:

```text
Login
  ↓
Access Token
  ↓
Expires
  ↓
Refresh Token
  ↓
New Access Token
```

Review:

```text
Access token lifetime
Refresh token lifetime
Refresh token rotation
Token reuse
Logout invalidation
Password reset invalidation
Token storage
Revocation
```

Refresh tokens generally require stronger protection because they can be used to obtain new access tokens.

---

# Remember Me Functionality

Applications may provide:

```text
Remember me
Keep me signed in
Stay signed in
Trust this device
```

Determine whether enabling the option creates an additional persistent token.

Compare authentication responses with and without the option.

Look for additional cookies such as:

```text
remember_me
persistent_session
device_token
trusted_device
```

Test:

```text
Expiration
Randomness
Rotation
Logout invalidation
Password reset invalidation
Revocation
Device binding where applicable
```

---

# Sensitive Operations

Some operations should require additional verification even when the user already has an authenticated session.

Examples:

```text
Change password
Change email address
Disable MFA
Generate recovery codes
Add payment information
View highly sensitive information
Create API keys
Change security settings
Delete account
```

Test whether an old or unattended authenticated session can perform these operations without reauthentication.

Depending on the application's risk model, the application may require:

```text
Current password
MFA
Recent authentication
Security confirmation
```

---

# Session Handling Across HTTP and HTTPS

Check whether session cookies can ever be transmitted over HTTP.

Attempt:

```text
http://example.com
```

Determine whether the application:

```text
Redirects immediately to HTTPS
Uses HSTS
Sets Secure cookies
Avoids sensitive content over HTTP
```

Sensitive session cookies should not be exposed over plaintext connections.

---

# Session Identifiers in URLs

Session identifiers should generally not appear in URLs.

Example:

```text
https://example.com/account?session=abc123
```

or:

```text
https://example.com/session/abc123/profile
```

URLs may be stored in:

```text
Browser history
Proxy logs
Web server logs
Analytics systems
Monitoring systems
Screenshots
Referrer headers
Bookmarks
```

Prefer session identifiers in appropriately secured cookies or authentication headers.

---

# Session Identifiers in Responses

Search application responses for session identifiers or authentication tokens.

For example:

```text
HTML
JavaScript
JSON
Debug information
Error messages
Redirect URLs
```

A session token should not be unnecessarily exposed in application content.

---

# Browser Storage

Modern applications may store authentication information in:

```text
Cookies
localStorage
sessionStorage
IndexedDB
```

Use browser developer tools:

```text
Developer Tools
    ↓
Application
    ↓
Storage
```

Review:

```text
Cookies
Local Storage
Session Storage
IndexedDB
```

Sensitive tokens stored in JavaScript-accessible storage may have additional exposure if the application contains XSS.

---

# Cache Behaviour

Authenticated responses containing sensitive information should be reviewed for inappropriate caching.

Inspect headers such as:

```http
Cache-Control:
Pragma:
Expires:
```

Depending on the application's requirements, sensitive responses may use controls such as:

```http
Cache-Control: no-store
```

Test whether sensitive authenticated content remains accessible after logout through browser navigation or caching.

---

# Testing With Multiple Browsers

Using separate browsers or browser profiles is useful for session testing.

Example:

```text
Chrome → Account A
Firefox → Account B
Private window → Account A
Burp Repeater → Captured session
```

This makes it easier to test:

```text
Concurrent sessions
Session invalidation
Cross-account behaviour
Password changes
Logout behaviour
Role changes
```

---

# Burp Suite Workflow

A practical Burp workflow:

```text
Proxy
    ↓
Capture Login
    ↓
Identify Session Token
    ↓
Send Requests to Repeater
    ↓
Test Session Rotation
    ↓
Test Logout
    ↓
Test Expiration
    ↓
Test Password Change
    ↓
Test Replay
    ↓
Compare Responses
```

Useful Burp components include:

```text
Proxy
Repeater
Comparer
Sequencer
Logger
Decoder
```

---

# Comparing Sessions

Burp Comparer can help identify differences between:

```text
Unauthenticated request
Authenticated request
Logged-out request
Expired-session request
Account A request
Account B request
```

Pay attention to differences in:

```text
Cookies
Headers
Response codes
Redirects
Response bodies
User identifiers
Role information
CSRF tokens
```

---

# Session Testing Checklist

## Session Creation

- [ ] Identify session mechanism
- [ ] Identify authentication cookies
- [ ] Identify access tokens
- [ ] Identify refresh tokens
- [ ] Compare pre-authentication and post-authentication sessions
- [ ] Verify session rotation after login
- [ ] Check session identifier randomness
- [ ] Check for predictable session values

---

## Cookie Security

- [ ] Check `Secure`
- [ ] Check `HttpOnly`
- [ ] Check `SameSite`
- [ ] Review `Domain`
- [ ] Review `Path`
- [ ] Review cookie lifetime
- [ ] Check for unnecessary persistent cookies

---

## Session Lifecycle

- [ ] Test logout invalidation
- [ ] Replay session after logout
- [ ] Test idle timeout
- [ ] Test absolute timeout
- [ ] Test password change behaviour
- [ ] Test password reset behaviour
- [ ] Test account disablement behaviour where authorised
- [ ] Test session revocation
- [ ] Test logout-all-sessions functionality

---

## Concurrent Sessions

- [ ] Test multiple simultaneous sessions
- [ ] Determine whether active sessions are visible
- [ ] Test individual session revocation
- [ ] Test global session revocation
- [ ] Test device/session management controls

---

## Token Handling

- [ ] Check tokens in URLs
- [ ] Check tokens in responses
- [ ] Check browser storage
- [ ] Check token expiration
- [ ] Check refresh token rotation
- [ ] Check token reuse
- [ ] Check token revocation

---

## Sensitive Operations

- [ ] Test password changes
- [ ] Test email changes
- [ ] Test MFA changes
- [ ] Test API key generation
- [ ] Test security setting changes
- [ ] Check reauthentication requirements

---

# Common Findings

Common session management findings include:

| Finding | Description |
|---|---|
| Missing Secure flag | Authentication cookie may be transmitted over an insecure connection |
| Missing HttpOnly flag | Cookie is accessible to client-side JavaScript |
| Weak SameSite configuration | Cookie may be included in unintended cross-site requests |
| Session fixation | Session identifier is not rotated after authentication |
| Logout does not invalidate session | Old session remains usable after logout |
| Excessive session lifetime | Sessions remain active longer than necessary |
| Weak session identifier | Session value may be predictable |
| Session token in URL | Sensitive token may leak through logs or browser history |
| Password reset does not revoke sessions | Existing sessions remain active after account recovery |
| Ineffective session revocation | Revoked session continues to function |
| Sensitive action without reauthentication | Existing session is sufficient for high-risk account changes |

---

# Evidence Collection

For each potential finding, record:

```text
Endpoint
HTTP method
Session mechanism
Cookie/token name
Relevant request
Relevant response
Expected behaviour
Observed behaviour
Reproduction steps
Security impact
```

Avoid including active authentication tokens in reports unnecessarily.

Redact sensitive values.

Example:

```text
session=eyJhbGciOiJIUzI1NiIs...
```

can be documented as:

```text
session=[REDACTED]
```

---

# Reporting Example

## Title

```text
Authenticated Session Remains Valid After Logout
```

## Description

The application does not invalidate the authenticated session on the server when the user logs out. Although the browser removes the session cookie, the previously issued session identifier remains valid.

## Reproduction

```text
1. Authenticate using a test account.
2. Capture an authenticated request.
3. Send the request to Burp Repeater.
4. Log out through the application.
5. Replay the original authenticated request.
6. Observe that authenticated functionality remains accessible.
```

## Impact

An exposed or previously captured session token could remain usable after the legitimate user has logged out, increasing the window in which session hijacking could occur.

## Recommendation

Invalidate the corresponding server-side session when the user logs out. Previously issued session identifiers should no longer provide authenticated access after logout.

---

# Quick Reference

```text
Session established
        ↓
Was identifier rotated after login?
        ↓
Are cookie attributes secure?
        ↓
Is identifier unpredictable?
        ↓
Does logout invalidate it?
        ↓
Does it expire?
        ↓
Does password reset revoke it?
        ↓
Can sessions be individually revoked?
        ↓
Are sensitive operations protected?
```

---

# Useful Tools

Common tools for session management testing include:

```text
Burp Suite Proxy
Burp Repeater
Burp Sequencer
Burp Comparer
Burp Decoder
Browser Developer Tools
curl
JWT analysis tools
```

Example with curl:

```bash
curl -i https://example.com/login
```

Using a cookie:

```bash
curl -i \
  -H 'Cookie: session=SESSION_VALUE' \
  https://example.com/account
```

Store cookies:

```bash
curl -c cookies.txt \
  https://example.com/
```

Reuse cookies:

```bash
curl -b cookies.txt \
  https://example.com/account
```

---

# Key Principle

Session management testing is not simply checking whether a cookie contains `Secure` and `HttpOnly`.

The complete session lifecycle should be tested:

```text
Creation
   ↓
Authentication
   ↓
Rotation
   ↓
Use
   ↓
Expiration
   ↓
Revocation
   ↓
Logout
```

A secure application should ensure that session identifiers are unpredictable, appropriately protected, rotated when authentication state changes, expired according to policy, and reliably invalidated when they should no longer provide access.
