# Rate Limiting and Anti-Automation

Rate limiting and anti-automation controls protect applications from excessive, repeated, or automated use of functionality.

These controls are especially important for security-sensitive workflows such as:

```text
Login
Password reset
MFA / OTP verification
Account registration
Email verification
Username recovery
Invitation workflows
Coupon redemption
Promo codes
Gift cards
Search
Data exports
API requests
File generation
SMS / email sending
Expensive calculations
AI / LLM endpoints
```

A basic rate limit answers:

```text
How frequently may this action occur?
```

Anti-automation is broader:

```text
Should this sequence of actions be allowed
to occur automatically at this scale,
for this identity,
against these objects,
from this source,
within this period?
```

Conceptually:

```text
Client
  |
  v
Request
  |
  v
Authentication
  |
  v
Rate / Abuse Controls
  |
  +-- Request frequency
  +-- Account
  +-- IP / network
  +-- Session
  +-- Device
  +-- Target object
  +-- Operation
  +-- Cost
  +-- Behaviour
  |
  v
Authorisation
  |
  v
Business Logic
  |
  v
Response
```

!!! warning "Authorised Security Testing"
    Rate-limit and anti-automation testing can unintentionally create denial-of-service conditions, lock accounts, send large numbers of emails or SMS messages, consume paid API resources, exhaust quotas, or affect other users. Use controlled accounts and objects, begin with very low request volumes, increase gradually only when necessary, and perform high-volume or resource-exhaustion testing only when explicitly authorised.

---

# Rate Limiting vs Anti-Automation

These concepts overlap but are not identical.

## Rate Limiting

Rate limiting controls the number of operations allowed during a period.

For example:

```text
5 login attempts
per account
per 10 minutes
```

or:

```text
100 API requests
per API key
per minute
```

---

## Anti-Automation

Anti-automation attempts to detect or prevent abusive automated behaviour.

This can include:

```text
Rate limits
Progressive delays
Account lockouts
CAPTCHA
Proof-of-work or challenges
OTP attempt limits
Replay prevention
Device signals
Behavioural analysis
Risk-based authentication
Per-object limits
Workflow state
Fraud controls
Cost controls
Monitoring
```

Therefore:

```text
Rate Limiting
      |
      v
One component of
      |
      v
Anti-Automation
```

---

# Why Rate Limiting Matters

Without appropriate controls, attackers may automate actions such as:

```text
Password guessing
Credential stuffing
Username enumeration
OTP guessing
Reset-token guessing
Email flooding
SMS flooding
Account creation
Coupon guessing
Gift-card enumeration
API scraping
Object enumeration
Data harvesting
Resource exhaustion
Expensive operations
```

The vulnerability is often not:

```text
Automation is possible
```

because many legitimate APIs are intentionally automatable.

The security question is:

```text
Can automation be used to cross a security
or business boundary at an unacceptable scale?
```

---

# A Simple Example

Suppose a login endpoint accepts:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
    "username": "test@example.com",
    "password": "Password123"
}
```

An attacker may attempt:

```text
password1
password2
password3
password4
...
```

A rate limiter might enforce:

```text
5 failed attempts
        |
        v
Temporary restriction
        |
        v
Further attempts rejected or delayed
```

Without this control:

```text
Unlimited attempts
        |
        v
Password guessing becomes more practical
```

---

# Rate Limiting Is Context Dependent

There is no universal rule such as:

```text
Every endpoint must allow exactly
5 requests per minute
```

Appropriate limits depend on:

```text
Endpoint purpose
User expectations
Risk
Cost
Authentication state
Business model
Traffic patterns
Infrastructure
Recovery requirements
```

For example:

```text
GET /public/news
```

has a different risk profile from:

```text
POST /api/mfa/verify
```

and:

```text
POST /api/password-reset
```

has a different risk profile from:

```text
GET /api/profile
```

---

# Security-Sensitive Endpoints

Prioritise:

```text
Authentication
Password reset
MFA
OTP verification
Email verification
Registration
Invitation acceptance
Account recovery
API keys
Promo codes
Gift cards
Payments
Search
Exports
Resource creation
Notification sending
AI / LLM requests
```

---

# Build an Endpoint Inventory

Create a table:

| Endpoint | Action | Authentication | Sensitive? | Expected Limit |
|---|---|---|---|---|
| `/login` | Login | No | High | Yes |
| `/reset` | Password reset | No | High | Yes |
| `/otp/verify` | OTP verification | Partial | High | Yes |
| `/search` | Search | Yes | Medium | Depends |
| `/export` | Export data | Yes | High cost | Yes |
| `/profile` | Read profile | Yes | Low | Depends |

This prevents testing only the obvious login endpoint.

---

# Rate-Limit Dimensions

A rate limiter needs a key.

Common keys include:

```text
IP address
Account
Username
Email address
Session
API key
Access token
Device
Tenant
Target object
Endpoint
Operation
Global application state
```

A secure design often uses multiple dimensions.

---

# IP-Based Rate Limiting

Example:

```text
Source IP
   |
   v
Request counter
   |
   +-- <= 20/min -> Allow
   |
   +-- > 20/min -> Restrict
```

This is useful but usually insufficient by itself.

Why?

Because attackers may have:

```text
Multiple IP addresses
Cloud infrastructure
Proxy networks
IPv6 addresses
Distributed clients
```

At the same time, legitimate users may share one IP through:

```text
Corporate NAT
University networks
Mobile carriers
VPN gateways
```

Therefore IP limits need careful design.

---

# Account-Based Rate Limiting

Instead of counting only the source IP:

```text
Account
   |
   v
Failed attempts
```

For example:

```text
alice@example.com

Attempt 1
Attempt 2
Attempt 3
Attempt 4
Attempt 5
```

Further attempts may trigger:

```text
Delay
Challenge
Temporary restriction
Risk review
```

This makes distributed guessing against one account harder.

---

# Account Lockout

A simple implementation may use:

```text
5 failed passwords
       |
       v
Lock account
```

This can reduce password guessing but creates another risk:

```text
Attacker intentionally sends
5 bad passwords for victim
       |
       v
Victim locked out
```

This creates:

```text
Account denial of service
```

For this reason, permanent or easily triggered hard lockouts can be problematic.

Alternatives include:

```text
Progressive delays
Temporary restrictions
Risk-based challenges
Additional verification
User notifications
Combined IP/account limits
```

---

# Progressive Delays

Instead of immediately locking an account:

```text
Failure 1 -> normal
Failure 2 -> normal
Failure 3 -> short delay
Failure 4 -> longer delay
Failure 5 -> stronger restriction
```

Conceptually:

```text
Repeated failures
       |
       v
Increasing friction
       |
       v
Automation becomes expensive
```

while legitimate users retain a recovery path.

---

# Per-Session Rate Limiting

Some applications limit requests by:

```text
Session cookie
```

For example:

```text
session A -> 10 requests/minute
```

Potential issue:

```text
Create new session
       |
       v
Counter resets
```

Therefore test whether obtaining a new session resets the protection unexpectedly.

---

# API-Key Rate Limiting

APIs commonly use:

```text
API key
```

as a quota key.

Example:

```text
API_KEY_A
    |
    +-- 100 requests/minute
```

Questions include:

```text
Can new keys be generated easily?

Does deleting and recreating a key reset the limit?

Are multiple keys allowed per account?

Is there also an account-level quota?

Can one tenant create unlimited keys?
```

---

# Token-Based Limits

Applications may rate-limit by:

```text
Access token
```

Potential weakness:

```text
Refresh token
     |
     v
New access token
     |
     v
New rate-limit bucket
```

Test whether limits are enforced at the appropriate:

```text
User
Account
Tenant
```

level rather than only the temporary token.

---

# Target-Based Rate Limiting

Sometimes the important dimension is not the attacker.

It is the target.

Example:

```text
POST /password-reset

email=victim@example.com
```

Even if requests originate from different IP addresses, the application should consider:

```text
How many reset requests
are being sent to this account?
```

Otherwise distributed abuse may still flood the victim.

---

# Per-Object Limits

Consider:

```text
POST /api/send-invite
```

A user might be allowed:

```text
100 requests/day
```

but if all 100 can target:

```text
victim@example.com
```

the target may still receive abusive volumes.

Useful dimensions include:

```text
Sender
Target
Sender + Target
Tenant
Global
```

---

# Combined Rate Limits

A stronger design may combine:

```text
Per IP
+
Per account
+
Per target
+
Per session
+
Global threshold
```

For example:

```text
Login
 |
 +-- Per IP threshold
 |
 +-- Per username threshold
 |
 +-- IP + username threshold
 |
 +-- Global anomaly detection
```

This makes simple bypasses more difficult.

---

# Fixed Window Rate Limiting

A fixed-window implementation might allow:

```text
100 requests
between 12:00 and 12:01
```

then reset:

```text
12:01
```

Potential boundary behaviour:

```text
99 requests at 12:00:59

+

99 requests at 12:01:01
```

This can result in a short burst larger than the nominal rate.

---

# Sliding Window

A sliding-window approach evaluates requests over a moving time interval.

Conceptually:

```text
Current time
     |
     v
Look backward 60 seconds
     |
     v
Count requests
```

This can smooth fixed-window boundary effects.

---

# Token Bucket

A token bucket conceptually contains:

```text
Tokens
```

Each operation consumes one or more tokens.

Tokens regenerate over time.

```text
Bucket
 |
 +-- Request -> consume token
 |
 +-- Time -> replenish tokens
```

This permits controlled bursts while enforcing a long-term rate.

---

# Leaky Bucket

A leaky-bucket model processes work at a controlled rate.

Conceptually:

```text
Incoming Requests
       |
       v
      Queue
       |
       v
Constant processing rate
```

Excess traffic may:

```text
Queue
or
Be rejected
```

depending on implementation.

---

# Cost-Based Rate Limiting

Not all requests have equal cost.

Compare:

```text
GET /health
```

with:

```text
POST /generate-large-report
```

or:

```text
POST /ai/generate
```

A cost-aware limiter may assign:

```text
Health check -> 1 unit
Search -> 5 units
Report -> 20 units
AI generation -> 50 units
```

This can better protect expensive operations.

---

# HTTP 429

The standard HTTP status commonly associated with rate limiting is:

```http
429 Too Many Requests
```

Example:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
Content-Type: application/json

{
    "error": "Too many requests"
}
```

---

# Retry-After

Servers may return:

```http
Retry-After: 60
```

meaning retry after approximately:

```text
60 seconds
```

It may also use an HTTP date.

Applications should not rely on clients voluntarily respecting `Retry-After`.

Enforcement must remain server-side.

---

# Not Every Rate Limit Uses 429

Applications may instead return:

```text
403
401
400
200 with error JSON
Connection rejection
Delayed response
CAPTCHA challenge
```

Therefore do not test only for:

```text
status == 429
```

Look at:

```text
Status
Body
Headers
Response length
Timing
Application state
```

---

# Rate-Limit Headers

APIs may expose rate-limit information through headers.

Examples seen in different implementations include:

```text
RateLimit-Limit
RateLimit-Remaining
RateLimit-Reset

X-RateLimit-Limit
X-RateLimit-Remaining
X-RateLimit-Reset
```

Header conventions vary.

Do not assume every application implements the same format.

---

# Baseline First

Before testing limits, establish normal behaviour.

Example:

```text
Request 1 -> 200
Request 2 -> 200
Request 3 -> 200
```

Record:

```text
Status
Body
Length
Headers
Timing
State changes
```

Then gradually test repeated requests.

---

# Safe Incremental Testing

Start small.

For example:

```text
1 request
3 requests
5 requests
10 requests
```

rather than immediately sending:

```text
10,000 requests
```

Stop as soon as the control can be characterised.

The goal is:

```text
Understand enforcement
```

not:

```text
Overload the application
```

---

# Burp Suite Repeater

Repeater is useful for manual baseline testing.

Send the same request several times and compare:

```text
Response
Headers
Timing
Cookies
Application state
```

For example:

```text
Attempt 1 -> normal
Attempt 2 -> normal
Attempt 3 -> normal
Attempt 4 -> delay
Attempt 5 -> 429
```

This can reveal progressive controls.

---

# Burp Repeater Groups

Repeater groups can help compare:

```text
Different users
Different sessions
Different endpoints
```

For example:

```text
Request A -> Account A
Request B -> Account B
```

This helps determine whether the limit is:

```text
Global
Per account
Per session
```

---

# Burp Intruder

Burp Intruder can perform controlled repeated-request testing.

For example, use a small payload list:

```text
test01
test02
test03
test04
test05
```

Observe:

```text
Status
Length
Words
Time
Headers
```

!!! warning
    Configure conservative request rates. Intruder can generate significant traffic and may trigger lockouts, monitoring alerts, messaging costs, or service degradation.

---

# Intruder Resource Pools

Use Burp resource pools to control:

```text
Concurrent requests
Delay between requests
Request rate
```

For rate-limit testing, deliberate low-rate configuration is often more useful than maximum speed.

---

# Burp Comparer

Comparer is useful when the rate-limit response is subtle.

Compare:

```text
Normal response
```

against:

```text
Restricted response
```

Differences may include:

```text
JSON field
Error message
Header
Cookie
Hidden state
```

---

# Burp Logger

Burp's logging functionality can help inspect:

```text
Request sequence
Response codes
Timing
Extensions
Background traffic
```

This is useful when the application performs additional requests automatically.

---

# Turbo Intruder

Turbo Intruder is a Burp extension designed for sending large numbers of HTTP requests and for advanced request timing and race-condition testing.

Official BApp Store:

```text
https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988
```

GitHub:

```text
https://github.com/PortSwigger/turbo-intruder
```

For rate-limit testing it can help with:

```text
Precise timing
Concurrency
Burst behaviour
Race conditions
Window-boundary testing
```

!!! danger "High Traffic Potential"
    Turbo Intruder can generate substantial traffic. Do not use high concurrency or large request counts against production systems unless that level of testing is explicitly authorised.

---

# Turbo Intruder Is Not Always Necessary

For many assessments:

```text
Repeater
+
Small Intruder test
```

is enough.

Use Turbo Intruder when you specifically need to understand:

```text
Concurrency
Timing
Burst handling
Race behaviour
```

Do not use it merely because it is faster.

---

# Testing Login Rate Limits

Use a controlled test account.

Baseline:

```text
Correct password
```

Then test a small number of intentionally incorrect passwords.

Record:

| Attempt | Result | Status | Delay |
|---:|---|---:|---:|
| 1 | Invalid password | 401 | 100 ms |
| 2 | Invalid password | 401 | 110 ms |
| 3 | Invalid password | 401 | 300 ms |
| 4 | Restricted | 429 | 50 ms |

Then determine:

```text
What key triggered the restriction?
```

---

# Test IP vs Account Scope

With controlled accounts:

```text
Account A
Account B
```

Test:

```text
Several failures against A
```

then:

```text
Login attempt against B
```

Possible interpretation:

```text
B also blocked
-> possibly IP-based

B unaffected
-> possibly account-based
```

Do not conclude based on one observation.

Applications may use multiple controls simultaneously.

---

# Test Account Scope

Using the same controlled account from authorised testing sources:

```text
Source A
Source B
```

determine whether the account-level restriction persists.

If changing source completely resets all protection:

```text
Protection may rely only on source address
```

This is especially relevant to:

```text
Password guessing
OTP guessing
Reset-token guessing
```

---

# Password Spraying

Password spraying differs from brute-forcing one account.

```text
Brute force:

User A -> password1
User A -> password2
User A -> password3
```

Password spraying:

```text
User A -> Password1
User B -> Password1
User C -> Password1
```

A limiter protecting only:

```text
Attempts per account
```

may not detect:

```text
One attempt across many accounts
```

Defensive controls should therefore consider both:

```text
Per-account behaviour
+
Cross-account behaviour
```

Testing password spraying against real users can create significant risk and should only be performed when explicitly authorised.

---

# Credential Stuffing

Credential stuffing uses previously compromised username/password pairs against another service.

For testing:

```text
Do not use real stolen credentials.
```

Use controlled accounts and controlled credentials to validate whether anti-automation controls would limit repeated distributed authentication attempts.

---

# Username Enumeration and Rate Limits

An application may prevent brute force but still allow unlimited username enumeration.

For example:

```text
Known user:
"Incorrect password"

Unknown user:
"Account does not exist"
```

or differences in:

```text
Status
Length
Timing
Headers
```

Rate limiting should not be considered a replacement for consistent authentication responses.

Refer to:

```text
docs/web/authentication.md
```

---

# Password Reset Rate Limiting

Password reset has several abuse cases.

```text
POST /password-reset

{
    "email": "victim@example.com"
}
```

Potential abuse:

```text
Email flooding
SMS flooding
Account enumeration
Reset-token guessing
Resource consumption
```

Test with controlled accounts.

Refer to:

```text
docs/web/password-reset.md
```

---

# Reset Email Flooding

Using a controlled mailbox:

```text
Request 1 -> email
Request 2 -> email
Request 3 -> email
Request 4 -> email
```

Questions:

```text
Is there a per-account limit?

Per-IP limit?

Cooldown?

Daily limit?

Does each request invalidate previous tokens?

Does the endpoint continue sending messages indefinitely?
```

Stop after enough requests to characterise behaviour.

---

# Target vs Source Protection

For messaging endpoints, consider:

```text
Source control
```

and:

```text
Target control
```

Example:

```text
IP A -> victim
IP B -> victim
IP C -> victim
```

If only source-based controls exist, the victim may still be flooded through distributed sources.

---

# MFA / OTP Rate Limiting

OTP verification is one of the most important places for attempt limits.

Suppose an OTP contains:

```text
6 decimal digits
```

The theoretical code space is:

```text
000000 - 999999
```

or:

```text
1,000,000 possibilities
```

Security therefore depends partly on:

```text
Short validity
Attempt limits
Account/challenge binding
Replay prevention
Secure generation
```

Refer to:

```text
docs/web/mfa.md
```

---

# Safe OTP Testing

Use a controlled account.

Request a valid OTP.

Then submit only a small number of intentionally incorrect values:

```text
111111
222222
333333
```

Observe:

```text
Does the challenge remain active?

Does a restriction occur?

Is the valid OTP still accepted?

Does requesting a new OTP reset the attempt counter?
```

Do not attempt exhaustive OTP enumeration against production.

---

# OTP Counter Reset

A common design question:

```text
Challenge A
   |
   +-- 5 attempts
```

Then:

```text
Request new OTP
```

Does this create:

```text
Challenge B
+
fresh 5 attempts
```

while allowing unlimited challenge creation?

If so, the effective protection may be weaker than expected.

A robust design should consider:

```text
Per challenge
Per account
Per session
Per source
Overall time window
```

---

# OTP Binding

An OTP should normally be bound to the appropriate:

```text
Account
Challenge
Purpose
Transaction
```

depending on its use.

For example:

```text
OTP for Account A
```

should not validate:

```text
Account B
```

Rate limiting cannot compensate for missing challenge binding.

---

# Email Verification

Verification-code endpoints should also have:

```text
Attempt limits
Expiry
Single-use behaviour
Account binding
Challenge binding
```

Test using controlled addresses.

---

# Registration Abuse

Account registration may be abused for:

```text
Mass account creation
Referral abuse
Free-trial abuse
Promo abuse
Spam
Resource consumption
```

Rate limiting can be useful but is often insufficient alone.

Other controls may include:

```text
Email verification
Phone verification
Risk scoring
Device signals
Fraud controls
Quota enforcement
```

---

# CAPTCHA

CAPTCHA is one possible anti-automation mechanism.

Conceptually:

```text
Suspicious activity
       |
       v
Challenge
       |
       v
Human interaction
```

CAPTCHA should generally be considered:

```text
One layer
```

rather than the entire anti-automation strategy.

---

# CAPTCHA Bypass Testing

Questions include:

```text
Is CAPTCHA validated server-side?

Is it required for the sensitive action?

Is the challenge bound to the session?

Can the same solution be replayed?

Does changing endpoint bypass it?

Does API access bypass the browser challenge?

Is CAPTCHA required only by frontend JavaScript?
```

Do not attempt to defeat third-party CAPTCHA services at scale.

Focus on application integration.

---

# Frontend-Only CAPTCHA

A weak implementation may look like:

```text
Browser JavaScript
       |
       +-- CAPTCHA passed?
       |
       v
Send request
```

but the backend simply accepts:

```http
POST /login
```

without verifying the CAPTCHA token.

Then:

```text
Direct HTTP request
       |
       v
CAPTCHA bypassed
```

The backend must validate the challenge where the security decision occurs.

---

# CAPTCHA Replay

A CAPTCHA token may be intended to be:

```text
Single use
Short lived
Bound to context
```

Test whether a controlled valid token can be replayed.

If unlimited reuse is possible, automation protection may be weakened.

---

# Alternative Endpoint Bypass

Applications frequently expose several routes to the same functionality.

Example:

```text
/login
/api/login
/api/v1/login
/api/v2/login
/mobile/login
/graphql
```

One route may have:

```text
Rate limiting
```

while another does not.

Build an endpoint map.

---

# API Version Bypass

Example:

```text
POST /api/v2/login
```

is protected.

But:

```text
POST /api/v1/login
```

remains reachable without the same controls.

This is an example of inconsistent security enforcement across versions.

---

# HTTP Method Differences

Check whether the same operation is available through:

```text
POST
PUT
PATCH
GET
```

where appropriate.

Security middleware may be attached to:

```text
Route + method
```

rather than the underlying business operation.

---

# Content-Type Differences

Applications may support:

```text
application/json
application/x-www-form-urlencoded
multipart/form-data
```

A protection layer might inspect only one parser or route.

Test supported content types only when the application legitimately accepts them.

---

# GraphQL Rate Limiting

GraphQL complicates rate limiting because:

```text
One HTTP request
```

can contain:

```text
Multiple operations
Complex queries
Deep nesting
Aliases
Expensive resolvers
```

Therefore:

```text
Requests per minute
```

may be insufficient.

Consider:

```text
Query complexity
Depth
Resolver cost
Object count
Operation
User
```

Refer to:

```text
docs/web/graphql.md
```

---

# GraphQL Aliases

A query may contain multiple aliases:

```graphql
query {
    a: user(id: 1) {
        id
    }

    b: user(id: 2) {
        id
    }

    c: user(id: 3) {
        id
    }
}
```

A naive limiter counting:

```text
HTTP requests
```

sees:

```text
1
```

while the backend performs multiple logical operations.

GraphQL protections should account for operation cost.

---

# GraphQL Batching

Some GraphQL implementations support batching.

Conceptually:

```text
One HTTP request
       |
       +-- Operation 1
       +-- Operation 2
       +-- Operation 3
```

Rate limits should consider:

```text
Logical operations
```

not merely transport requests.

---

# gRPC Rate Limiting

gRPC has similar concerns.

One HTTP/2 connection can contain:

```text
Multiple concurrent streams
```

and a stream can contain:

```text
Multiple messages
```

Therefore:

```text
Connections per minute
```

is not sufficient as the only control.

Refer to:

```text
docs/web/grpc-security.md
```

---

# gRPC Streaming

For streaming methods consider:

```text
Messages per stream
Streams per user
Concurrent streams
Message cost
Stream duration
Idle timeout
```

A single long-lived stream can perform many logical operations.

---

# WebSocket Rate Limiting

WebSockets also use long-lived connections.

A weak design may rate-limit:

```text
Connections
```

but not:

```text
Messages
```

For example:

```text
1 connection
+
100,000 messages
```

may bypass a connection-based control.

Refer to:

```text
docs/web/websockets.md
```

---

# Per-Message Limits

For WebSocket and streaming protocols:

```text
Connection-level control
+
Message-level control
+
Operation-level control
```

may all be necessary.

---

# Business Logic Rate Limits

Some limits are business controls rather than purely infrastructure controls.

Examples:

```text
3 promo redemptions/account
1 free trial/person
5 invitations/day
10 exports/day
1 refund/request
```

Bypassing them may create:

```text
Financial loss
Fraud
Abuse
Resource consumption
```

---

# Coupon and Promo Codes

Potential tests include:

```text
Repeated guessing
Reuse
Cross-account reuse
Case variations
Whitespace
Concurrent redemption
Multiple endpoints
```

Rate limiting should complement strong code entropy and server-side business rules.

Do not use real customer coupons without permission.

---

# Gift Cards

Gift-card functionality can be especially sensitive because it may represent monetary value.

Controls may include:

```text
High-entropy identifiers
Attempt limits
Account limits
Monitoring
Fraud detection
```

Testing should use designated test cards or controlled balances.

---

# Invitation Abuse

Example:

```text
POST /invite

email=victim@example.com
```

Potential abuse:

```text
Spam
Email flooding
Reputation damage
Cost
```

Test:

```text
Per sender
Per recipient
Per tenant
Global
```

limits.

---

# Search and Enumeration

Search endpoints can enable bulk data harvesting.

Example:

```text
GET /api/users?query=a
```

Automation might enumerate:

```text
Users
Emails
Phone numbers
Customer records
Orders
Products
```

Controls may include:

```text
Authorisation
Pagination
Result limits
Rate limits
Monitoring
Data minimisation
```

Rate limiting should not be used to hide data that users should not be authorised to access.

---

# Export Endpoints

Export functionality may be expensive.

Examples:

```text
CSV export
PDF generation
Report generation
Archive creation
Backup generation
```

Potential risks:

```text
CPU exhaustion
Memory exhaustion
Storage consumption
Queue exhaustion
Cloud cost
```

Use cost-aware limits.

---

# AI and LLM Endpoints

AI endpoints may have substantial cost.

Example:

```text
POST /api/chat
POST /api/generate
POST /api/summarise
```

Controls may include:

```text
Requests per user
Tokens per minute
Tokens per day
Concurrent generations
Model-specific quotas
Financial quotas
Input size
Output size
```

A simple:

```text
100 HTTP requests/minute
```

may be meaningless if one request can consume extremely large model resources.

---

# File Upload

Upload controls should consider:

```text
Files per period
File size
Total storage
Processing cost
Scanning cost
Conversion cost
```

Rate limits complement:

```text
File validation
Size limits
Storage quotas
```

Refer to:

```text
docs/web/file-upload.md
```

---

# HTTP Header Bypass Claims

Rate-limit testing sometimes involves changing headers such as:

```text
X-Forwarded-For
X-Real-IP
Forwarded
```

Do not assume these headers influence the rate limiter.

Test carefully.

Example:

```http
X-Forwarded-For: 192.0.2.10
```

then:

```http
X-Forwarded-For: 192.0.2.11
```

If changing an untrusted client-controlled header resets a security-sensitive rate limit, investigate further.

---

# Trusted Proxy Architecture

Headers such as:

```text
X-Forwarded-For
```

can be legitimate when set by trusted reverse proxies.

Correct architecture:

```text
Internet
   |
   v
Trusted Proxy
   |
   | Sanitises / sets client IP
   v
Application
```

Dangerous architecture:

```text
Internet Client
   |
   | X-Forwarded-For: arbitrary
   v
Application trusts value
```

The issue is not the existence of the header.

The issue is:

```text
Trusting attacker-controlled forwarding data
```

---

# Header Variations

When investigating a suspected proxy-trust issue, relevant headers may include:

```text
X-Forwarded-For
X-Real-IP
Forwarded
```

but only test headers relevant to the application's infrastructure.

Blindly spraying large lists of spoofing headers is usually less useful than understanding the proxy chain.

---

# IPv6

Rate limiting based on source addresses needs to account for IPv6.

IPv6 provides very large address spaces, so naive per-address limits can behave differently from IPv4 environments.

Designs may need to consider:

```text
Address
Prefix
Account
Device
Other signals
```

according to the environment.

---

# User-Agent Based Limits

A rate limiter based only on:

```text
User-Agent
```

is weak because the value is client controlled.

User-Agent may be useful as:

```text
One behavioural signal
```

but should not normally be treated as a strong identity.

---

# Cookie-Based Limits

If a counter is keyed only to a cookie:

```text
Cookie deleted
      |
      v
New rate-limit identity
```

may be possible.

Test whether the protection also considers:

```text
Account
Source
Target
```

where appropriate.

---

# Session Rotation

Test:

```text
Reach limit
      |
      v
Logout
      |
      v
Login
      |
      v
New session
```

Does the limit disappear?

Whether this is a problem depends on the intended scope.

For security-sensitive limits, session-only tracking may be insufficient.

---

# Logout / Login Reset

Similarly:

```text
5 OTP failures
      |
      v
Logout
      |
      v
Login again
```

should not necessarily provide unlimited new OTP guesses.

The limit should follow the security object being protected.

---

# New Challenge Reset

For challenge-based workflows:

```text
Challenge A
   |
   +-- attempt limit
```

test:

```text
Request Challenge B
```

Questions:

```text
Does the global account counter persist?

Can unlimited challenges be created?

Are old challenges invalidated?

Are attempts tracked per challenge only?
```

---

# Distributed Limits

Applications deployed across several backend instances need shared or coordinated rate-limit state.

Potential architecture:

```text
Load Balancer
     |
 +---+---+
 |       |
 v       v
App 1   App 2
```

If each instance independently allows:

```text
10 attempts
```

the effective total may become:

```text
20 attempts
```

or more.

---

# Load Balancer Testing

Do not attempt to manipulate backend routing aggressively.

But if ordinary requests naturally reveal inconsistent counters:

```text
Request 1 -> Node A
Request 2 -> Node B
```

investigate whether rate-limit state is shared correctly.

---

# Race Conditions

Rate-limit counters can themselves be vulnerable to races.

Conceptually:

```text
Request A -> check counter = 4
Request B -> check counter = 4

Both allowed

Counter becomes 6
```

instead of:

```text
Only one allowed
```

Refer to:

```text
docs/web/race-conditions.md
```

---

# Safe Concurrency Testing

Use only enough simultaneous requests to determine whether the limit is atomic.

For example:

```text
2
3
5
```

concurrent requests may be sufficient.

Do not start with hundreds of simultaneous requests.

---

# Window Boundary Testing

Suppose the limit is:

```text
10 requests/minute
```

and resets on a fixed boundary.

A controlled test can compare:

```text
Requests just before reset
+
Requests just after reset
```

to determine burst behaviour.

This is generally an implementation observation unless it creates meaningful security impact.

---

# Response Timing

Some anti-automation controls use delays.

Measure:

```text
Attempt 1 -> 100 ms
Attempt 2 -> 110 ms
Attempt 3 -> 500 ms
Attempt 4 -> 2 s
Attempt 5 -> 5 s
```

This may indicate:

```text
Progressive throttling
```

rather than a hard limit.

---

# Timing Measurement With curl

For a controlled endpoint:

```bash
curl \
  -s \
  -o /dev/null \
  -w '%{http_code} %{time_total}\n' \
  https://target.example/api/test
```

This prints:

```text
HTTP status
Total request time
```

Repeat only at an authorised, conservative rate.

---

# Simple Controlled Python Tester

For low-volume controlled testing:

```python
#!/usr/bin/env python3

import time
import requests

URL = "https://target.example/api/test"

TOTAL_REQUESTS = 10
DELAY = 1.0

session = requests.Session()

for number in range(1, TOTAL_REQUESTS + 1):

    started = time.perf_counter()

    response = session.get(
        URL,
        timeout=10,
    )

    elapsed = time.perf_counter() - started

    print(
        f"{number:02d} "
        f"status={response.status_code} "
        f"length={len(response.content)} "
        f"time={elapsed:.3f}s "
        f"retry-after={response.headers.get('Retry-After')}"
    )

    time.sleep(DELAY)
```

This intentionally includes:

```text
Delay
Low request count
No concurrency
```

so it can be used as a starting point rather than a load-testing tool.

---

# Authenticated Python Tester

```python
#!/usr/bin/env python3

import time
import requests

URL = "https://target.example/api/profile"

TOKEN = "REDACTED"

TOTAL_REQUESTS = 10
DELAY = 1.0

headers = {
    "Authorization": f"Bearer {TOKEN}",
}

session = requests.Session()

for number in range(1, TOTAL_REQUESTS + 1):

    started = time.perf_counter()

    response = session.get(
        URL,
        headers=headers,
        timeout=10,
    )

    elapsed = time.perf_counter() - started

    print(
        f"{number:02d} "
        f"status={response.status_code} "
        f"length={len(response.content)} "
        f"time={elapsed:.3f}s"
    )

    time.sleep(DELAY)
```

Do not hard-code real production credentials into scripts committed to source control.

---

# Comparing Two Accounts

A useful controlled test is:

```text
Account A reaches rate limit
```

then test:

```text
Account B
```

If B is also restricted:

```text
Potential shared IP/global limit
```

If B remains unaffected:

```text
Potential account-specific limit
```

Use this as evidence gathering, not as proof from one test alone.

---

# Response Fingerprinting

Rate limits may not produce obvious status changes.

Record:

```text
Status
Length
Hash
Response time
Headers
Error field
```

Example:

```text
200 length=1534
200 length=1534
200 length=1534
200 length=72
```

The fourth response may contain:

```json
{
    "error": "Too many attempts"
}
```

despite still returning:

```text
HTTP 200
```

---

# JSON Error Fields

Look for:

```text
error
message
code
retry_after
remaining
limit
blocked
challenge
```

Example:

```json
{
    "code": "RATE_LIMITED",
    "retry_after": 60
}
```

---

# Rate Limit Persistence

After triggering a controlled limit, test:

```text
Same request after short wait
Same account in new session
Same account after login
Same target from second controlled account
```

This helps determine the scope.

---

# Reset Time

Determine whether the limit resets:

```text
Immediately
After fixed period
Gradually
After successful authentication
After password reset
After new challenge
After session rotation
```

Understanding reset conditions is as important as discovering the limit.

---

# Successful Request Behaviour

Some counters reset after a successful operation.

Example:

```text
4 failed passwords
+
1 successful login
```

Does the failure counter reset?

This may be legitimate.

But understand whether it affects:

```text
Attack feasibility
Account protection
Detection
```

---

# Enumeration Through Limits

Rate-limit responses themselves can create enumeration.

Example:

Known account:

```text
429 Too Many Attempts
```

Unknown account:

```text
404 Account Not Found
```

This difference may reveal account validity.

Protection responses should avoid introducing new information leaks.

---

# Rate Limits and Caching

Be careful when:

```text
CDN
Reverse proxy
Application cache
```

sits in front of the application.

A response may come from:

```text
Edge
```

rather than:

```text
Application
```

Inspect headers such as:

```text
Age
Via
Cache-Control
CDN-specific headers
```

when relevant.

---

# WAF vs Application Rate Limiting

A WAF may enforce:

```text
Requests per IP
```

while the application separately enforces:

```text
OTP attempts per account
```

These are different layers.

Conceptually:

```text
Client
  |
  v
CDN / WAF
  |
  | Network-level rate limit
  v
Application
  |
  | Business-level rate limit
  v
OTP verification
```

Testing should distinguish them.

---

# Infrastructure Limit vs Security Limit

Example:

```text
WAF:
1000 requests/minute
```

does not necessarily protect:

```text
6-digit OTP
```

because:

```text
1000 guesses/minute
```

may still be unacceptable.

Sensitive operations need operation-specific controls.

---

# Anti-Automation Layers

A mature anti-automation design may combine:

```text
Rate Limiting
      |
      +-- IP
      +-- Account
      +-- Target
      +-- Device
      +-- Session
      |
      v
Progressive Friction
      |
      +-- Delays
      +-- CAPTCHA
      +-- Step-up authentication
      |
      v
Business Rules
      |
      +-- Daily limits
      +-- Quotas
      +-- Replay prevention
      |
      v
Risk Detection
      |
      +-- Behaviour
      +-- Reputation
      +-- Velocity
      |
      v
Monitoring
```

---

# Replay Prevention

Some operations should not simply be rate limited.

They should be:

```text
Single use
```

Examples:

```text
Password reset tokens
OTP codes
Email verification tokens
Recovery codes
Payment authorisations
Invitation tokens
```

A replayed token should be rejected even if:

```text
rate limit has not been reached
```

---

# Idempotency

APIs performing sensitive state changes may support idempotency keys.

Example:

```http
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

This can help prevent accidental duplicate processing.

But the server must:

```text
Bind the key appropriately
Store results safely
Prevent cross-user reuse
Expire keys appropriately
```

Rate limiting and idempotency solve different problems.

---

# Anti-Automation and Business Logic

Consider:

```text
POST /coupon/redeem
```

Even with:

```text
10 requests/minute
```

an attacker may run:

```text
10/minute
24 hours/day
```

The long-term number of attempts remains large.

Controls should consider:

```text
Total attempts
Account history
Target object
Code entropy
Monitoring
```

not just short-term request rate.

---

# Long-Term Limits

Some actions need:

```text
Per minute
Per hour
Per day
Per month
```

limits simultaneously.

Example:

```text
5 password reset emails / hour
10 / day
```

Short windows alone may allow sustained abuse.

---

# Quotas

A quota is often longer-term than a rate limit.

Example:

```text
Rate:
10 requests / second

Quota:
10,000 requests / day
```

Both can be useful.

---

# Rate Limit Bypass Methodology

Do not start by randomly changing headers.

Use a structured process.

```text
1. Identify protected operation

2. Establish baseline

3. Determine apparent threshold

4. Determine reset behaviour

5. Determine enforcement scope

6. Test session scope

7. Test account scope

8. Test target scope

9. Test supported alternate endpoints

10. Test relevant API versions

11. Test transport-specific behaviour

12. Test low-level concurrency if authorised

13. Confirm security impact

14. Collect evidence
```

---

# Step 1: Establish Threshold

Controlled sequence:

```text
Request 1
Request 2
Request 3
...
```

Stop when:

```text
Restriction observed
```

or when you reach the safe test limit agreed for the assessment.

---

# Step 2: Identify Key

Ask:

```text
What caused the restriction?
```

Potential candidates:

```text
IP
Account
Session
Token
Target
Endpoint
Global
```

Change only one variable at a time.

---

# Step 3: Test Session Scope

```text
Session A -> limit reached
```

Then:

```text
Session B -> same account
```

Observe.

---

# Step 4: Test Account Scope

```text
Account A -> limit reached
```

Then:

```text
Account B -> same test source
```

Observe.

---

# Step 5: Test Target Scope

For controlled target objects:

```text
Target A -> repeated action
```

Then:

```text
Target B
```

Observe whether the counter is:

```text
Per target
or
Per caller
```

---

# Step 6: Test Alternate Route

If the application itself exposes:

```text
/api/v1/action
/api/v2/action
```

compare them.

Do not invent unsupported endpoints merely to generate traffic.

---

# Step 7: Test Concurrency

Only when relevant and authorised:

```text
Two simultaneous requests
```

may be enough to identify non-atomic counters.

Increase minimally if needed.

---

# Step 8: Confirm Impact

A rate-limit weakness becomes meaningful when it enables something such as:

```text
Practical password guessing
Practical OTP guessing
Email/SMS flooding
Mass account creation
Bulk data harvesting
Financial abuse
Quota bypass
Resource exhaustion
```

Without meaningful impact, the observation may be:

```text
Hardening
Informational
Expected behaviour
```

rather than a vulnerability.

---

# Common False Positives

Do not report:

```text
No 429 header
```

as:

```text
No rate limiting
```

The application may use:

```text
Delays
403
CAPTCHA
Account restriction
Silent throttling
```

---

Do not report:

```text
10 requests succeeded
```

automatically as:

```text
Rate limiting missing
```

The expected threshold may legitimately be much higher.

---

Do not report:

```text
Rate limit can be bypassed with another account
```

if the intended limit is explicitly:

```text
Per account
```

and no protected security boundary is crossed.

---

Do not report:

```text
X-Forwarded-For changes response
```

without proving:

```text
The attacker controls the trusted identity used by the limiter
```

and that this meaningfully weakens a security control.

---

# Evidence Collection

Record:

```text
Endpoint
Method
Account
Target
Session
Source
Authentication state
Request number
Timestamp
Status
Response length
Response body
Rate-limit headers
Retry-After
Response time
Observed application state
```

---

# Evidence Table

| Attempt | Account | Target | Status | Time | Result |
|---:|---|---|---:|---:|---|
| 1 | A | A | 401 | 120 ms | Invalid |
| 2 | A | A | 401 | 130 ms | Invalid |
| 3 | A | A | 401 | 400 ms | Invalid |
| 4 | A | A | 429 | 80 ms | Restricted |

This is much clearer than:

```text
There seems to be rate limiting.
```

---

# Example Finding: Missing Login Rate Limiting

```text
Finding:
Insufficient Rate Limiting on Authentication Endpoint

Affected endpoint:
POST /api/login

Observed:
The authentication endpoint accepted repeated failed login attempts against a controlled account without applying an observable account-level restriction, progressive delay, challenge, or temporary lockout within the tested range.

Testing was performed at a conservative rate using a controlled account.

Impact:
An attacker may be able to perform automated password guessing or credential-stuffing attempts at a higher rate than intended.

Recommendation:
Implement layered authentication abuse controls that consider account, source, and behavioural signals. Apply appropriate throttling or progressive delays and monitor repeated authentication failures.
```

Do not claim:

```text
Unlimited brute force
```

unless you actually established that fact within the authorised test scope.

---

# Example Finding: OTP Attempt Limit Reset

```text
Finding:
Requesting a New OTP Resets Verification Attempt Counter

Observed:
A controlled MFA challenge allowed five invalid OTP attempts before further attempts were restricted.

Requesting a new OTP created a new challenge and reset the attempt counter.

This process could be repeated without an observed account-level limit.

Impact:
An attacker who has already reached the OTP stage may obtain additional OTP guesses by repeatedly requesting new challenges, weakening the effective protection against OTP guessing.

Recommendation:
Track OTP verification failures across both individual challenges and the protected account/session. Apply an overall attempt limit and time window in addition to per-challenge limits.
```

---

# Example Finding: Password Reset Email Flooding

```text
Finding:
Password Reset Endpoint Allows Repeated Email Delivery

Observed:
Repeated password reset requests for a controlled account caused a new reset email to be sent for each request.

No effective recipient-level cooldown or restriction was observed within the tested range.

Impact:
An attacker may repeatedly trigger password reset emails to users, causing nuisance, inbox flooding, and potentially increased messaging costs.

Recommendation:
Apply recipient-level and source-level throttling to password reset requests. Consider progressive cooldowns and monitoring for repeated reset requests.
```

---

# Example Finding: Client-Controlled IP Header Bypasses Limit

```text
Finding:
Authentication Rate Limit Trusts Client-Controlled X-Forwarded-For Header

Observed:
After the authentication rate limit was reached, further requests were rejected.

Changing the client-supplied X-Forwarded-For value caused the application to treat the request as originating from a new source and restored authentication attempts.

The application endpoint was directly reachable by the testing client and accepted the forwarding header without an enforced trusted proxy boundary.

Impact:
An attacker can repeatedly change the client-controlled forwarding value to circumvent the source-based authentication rate limit.

Recommendation:
Accept client address information only from trusted reverse proxies. Remove or overwrite untrusted forwarding headers at the network boundary and combine source-based controls with account-level authentication protections.
```

---

# Example Finding: Rate Limit Only Applies to Web Endpoint

```text
Finding:
Authentication Rate Limit Can Be Bypassed Through Legacy API

Observed:
The primary login endpoint applied a temporary restriction after repeated failed authentication attempts.

The legacy API endpoint exposed equivalent authentication functionality but did not share the same restriction.

Impact:
An attacker may use the legacy endpoint to circumvent protections applied to the current authentication interface.

Recommendation:
Apply authentication abuse controls consistently at the underlying authentication service or shared security layer rather than relying solely on individual routes.
```

---

# Example Finding: Missing Per-Target Limit

```text
Finding:
Invitation Endpoint Lacks Recipient-Level Anti-Abuse Controls

Observed:
A controlled user was able to send repeated invitation emails to the same controlled recipient.

The application enforced a broad sender quota but did not apply an effective recipient-level cooldown within the tested range.

Impact:
A legitimate account could be used to repeatedly send unwanted invitation messages to a specific recipient.

Recommendation:
Apply recipient-level throttling in addition to sender quotas and monitor repeated delivery attempts to the same destination.
```

---

# Finding Titles

Useful titles include:

```text
Insufficient Rate Limiting on Authentication Endpoint

MFA Verification Endpoint Lacks Effective Attempt Limiting

Requesting a New OTP Resets Verification Attempt Counter

Password Reset Endpoint Allows Repeated Email Delivery

Authentication Rate Limit Trusts Client-Controlled Forwarding Header

Legacy Authentication Endpoint Bypasses Current Rate Limit

Invitation Endpoint Lacks Recipient-Level Anti-Abuse Controls

Account Registration Lacks Effective Anti-Automation Controls

API Rate Limit Can Be Reset by Session Rotation

Sensitive Operation Lacks Account-Level Rate Limiting

GraphQL Batching Circumvents Operation-Level Rate Limit

WebSocket Messages Are Not Subject to Operation-Level Rate Limits

gRPC Streaming Method Lacks Message-Level Rate Limiting

Concurrent Requests Bypass Non-Atomic Operation Limit
```

---

# Severity

Severity depends on impact.

Examples:

```text
Missing limit on public static page
-> likely not a security issue

Missing login limit with strong passwords and other controls
-> context dependent

Missing OTP attempt limit
-> potentially significant

Unlimited password-reset email delivery
-> abuse / availability impact

Unlimited expensive AI operation
-> financial/resource impact

Rate-limit bypass enabling account takeover
-> potentially high severity
```

Do not assign severity based only on:

```text
number of requests
```

Evaluate:

```text
Likelihood
Attack complexity
Security boundary
Business impact
Scale
Existing controls
```

---

# Remediation Principles

A strong design uses layered controls.

```text
                     USER ACTION
                          |
                          v
                    EDGE CONTROLS
                          |
                +---------+---------+
                |                   |
                v                   v
             IP Rate             Global
              Limit              Protection
                |                   |
                +---------+---------+
                          |
                          v
                  IDENTITY CONTROLS
                          |
             +------------+------------+
             |            |            |
             v            v            v
          Account       Session      Device
             |            |            |
             +------------+------------+
                          |
                          v
                   TARGET CONTROLS
                          |
                 +--------+--------+
                 |                 |
                 v                 v
              Object           Recipient
                 |                 |
                 +--------+--------+
                          |
                          v
                  BUSINESS CONTROLS
                          |
             +------------+------------+
             |            |            |
             v            v            v
           Quota        Replay       Workflow
                        Control
             |            |            |
             +------------+------------+
                          |
                          v
                    RISK CONTROLS
                          |
                 +--------+--------+
                 |                 |
                 v                 v
             Challenge         Monitoring
                 |
                 v
             OPERATION
```

---

# Combine Multiple Dimensions

For sensitive authentication:

```text
Per account
+
Per source
+
Account/source combination
+
Behaviour
```

For password reset:

```text
Per source
+
Per recipient
+
Per account
+
Daily quota
```

For APIs:

```text
Per API key
+
Per user
+
Per tenant
+
Operation cost
```

---

# Apply Limits Server-Side

Do not rely on:

```text
Disabled buttons
JavaScript timers
Frontend counters
```

The security decision must be enforced by:

```text
Server
API gateway
Trusted edge infrastructure
```

---

# Use Shared State Where Required

Distributed applications may need:

```text
Central rate-limit store
```

or another coordinated mechanism.

Conceptually:

```text
App 1 ----+
          |
App 2 ----+---- Shared Counter
          |
App 3 ----+
```

This prevents independent backend counters from unintentionally multiplying the effective limit.

---

# Atomic Counters

Security-sensitive counters should be updated atomically.

Avoid logic equivalent to:

```text
Read count
Check count
Increment count
```

when concurrent requests can race between those operations.

Prefer atomic mechanisms supported by the chosen datastore or rate-limiting infrastructure.

---

# Protect Against Lockout Abuse

Do not make it trivial for attackers to permanently deny access to victims.

Consider:

```text
Temporary restrictions
Progressive delays
Risk-based challenges
Recovery mechanisms
Notifications
Multiple signals
```

---

# Use CAPTCHA Selectively

CAPTCHA can be useful when:

```text
Risk increases
Repeated abuse occurs
Anonymous automation is detected
```

but should not replace:

```text
Server-side limits
Authentication security
Business rules
Monitoring
```

---

# Monitor Abuse

Log relevant events:

```text
Authentication failures
OTP failures
Reset requests
Rate-limit triggers
CAPTCHA challenges
Registration velocity
Targeted recipients
API quota use
Repeated object enumeration
```

Avoid logging:

```text
Passwords
OTP values
Tokens
Secrets
```

---

# Alerting

Useful alerts may include:

```text
Many accounts attacked from one source

One account attacked from many sources

Large numbers of OTP failures

Repeated reset requests against one account

High registration velocity

Large export volume

Unusual API cost

Many rate-limit triggers
```

---

# Rate Limiting Is Not Authorisation

This is critical.

Suppose:

```text
GET /api/users/123
```

allows Account A to access Account B.

Adding:

```text
10 requests/minute
```

does not fix the vulnerability.

The application still has:

```text
Broken Object Level Authorisation
```

Rate limiting only reduces exploitation speed.

Refer to:

```text
docs/web/idor-bola.md
```

---

# Rate Limiting Is Not Input Validation

Likewise:

```text
SQL injection
```

does not become safe because:

```text
5 requests/minute
```

are allowed.

Fix the underlying injection vulnerability.

---

# Rate Limiting Is Not Strong Authentication

A login endpoint with:

```text
1 attempt/hour
```

is still insecure if:

```text
authentication can be bypassed entirely
```

Controls must address the actual security boundary.

---

# Rate Limiting Is Defence in Depth

The correct model is:

```text
Authentication
+
Authorisation
+
Input Validation
+
Business Rules
+
Rate Limiting
+
Anti-Automation
+
Monitoring
```

not:

```text
Rate Limiting
=
all abuse solved
```

---

# Pentesting Checklist

## Discovery

```text
[ ] Authentication endpoints
[ ] Registration endpoints
[ ] Password reset endpoints
[ ] OTP endpoints
[ ] MFA endpoints
[ ] Verification endpoints
[ ] Invitation endpoints
[ ] Search endpoints
[ ] Export endpoints
[ ] Messaging endpoints
[ ] Expensive operations
[ ] API endpoints
[ ] GraphQL operations
[ ] gRPC methods
[ ] WebSocket operations
```

---

## Baseline

```text
[ ] Normal response captured
[ ] Normal timing recorded
[ ] Normal headers recorded
[ ] Normal application state verified
[ ] Controlled account used
[ ] Safe request count established
```

---

## Rate-Limit Behaviour

```text
[ ] Threshold investigated
[ ] 429 checked
[ ] Alternative error responses checked
[ ] Retry-After checked
[ ] Rate-limit headers checked
[ ] Progressive delay checked
[ ] CAPTCHA checked
[ ] Temporary restriction checked
[ ] Lockout behaviour checked
[ ] Reset time checked
```

---

## Scope

```text
[ ] Per IP
[ ] Per account
[ ] Per session
[ ] Per token
[ ] Per API key
[ ] Per tenant
[ ] Per target
[ ] Per object
[ ] Per endpoint
[ ] Global
```

---

## Reset Behaviour

```text
[ ] New session
[ ] Logout/login
[ ] New token
[ ] Token refresh
[ ] New challenge
[ ] New OTP
[ ] New API key
[ ] Time-window reset
```

---

## Alternate Paths

```text
[ ] API versions
[ ] Legacy routes
[ ] Mobile API
[ ] Browser API
[ ] GraphQL
[ ] gRPC
[ ] WebSockets
[ ] Supported content types
```

---

## Anti-Automation

```text
[ ] CAPTCHA server-side validation
[ ] CAPTCHA replay
[ ] Challenge binding
[ ] OTP attempt limits
[ ] OTP replay
[ ] Token single use
[ ] Target-level controls
[ ] Long-term quotas
[ ] Business limits
[ ] Behaviour monitoring
```

---

## Resource Protection

```text
[ ] Request size
[ ] Upload limits
[ ] Export limits
[ ] Search limits
[ ] Pagination
[ ] Expensive queries
[ ] AI token limits
[ ] Concurrent operations
[ ] Streaming limits
```

---

## Evidence

```text
[ ] Request sequence recorded
[ ] Response sequence recorded
[ ] Timing recorded
[ ] Account recorded
[ ] Target recorded
[ ] Threshold documented
[ ] Reset behaviour documented
[ ] Security impact confirmed
[ ] Sensitive data redacted
```

---

# Quick Reference

```text
LOGIN
 |
 +-- Per account?
 +-- Per IP?
 +-- Progressive delay?
 +-- Lockout abuse?
 +-- Password spray detection?
```

```text
PASSWORD RESET
 |
 +-- Per sender?
 +-- Per recipient?
 +-- Cooldown?
 +-- Daily quota?
 +-- Enumeration?
```

```text
OTP
 |
 +-- Attempts per challenge?
 +-- Attempts per account?
 +-- New challenge reset?
 +-- Expiry?
 +-- Replay?
 +-- Account binding?
```

```text
API
 |
 +-- Per user?
 +-- Per key?
 +-- Per tenant?
 +-- Per operation?
 +-- Cost aware?
```

```text
STREAMING
 |
 +-- Connections?
 +-- Streams?
 +-- Messages?
 +-- Operations?
 +-- Duration?
```

---

# Testing Decision Tree

```text
                SENSITIVE ACTION
                       |
                       v
               Establish Baseline
                       |
                       v
              Repeat Conservatively
                       |
                       v
             Restriction Observed?
                  /          \
                YES           NO
                 |             |
                 v             v
          Determine Type    Stop at Safe
                 |          Test Boundary
                 |             |
       +---------+------+      v
       |         |      |   Assess Impact
       v         v      v
      429      Delay  Challenge
       |         |      |
       +---------+------+
                 |
                 v
           Determine Scope
                 |
      +----------+-----------+
      |          |           |
      v          v           v
     IP       Account      Session
      |          |           |
      +----------+-----------+
                 |
                 v
            Target Scope?
                 |
                 v
            Reset Behaviour
                 |
        +--------+--------+
        |        |        |
        v        v        v
      Time    Session   Challenge
        |        |        |
        +--------+--------+
                 |
                 v
          Alternate Routes
                 |
                 v
        Concurrency Relevant?
                 |
            +----+----+
            |         |
           YES        NO
            |         |
            v         |
       Minimal Safe    |
       Concurrency     |
            |         |
            +----+----+
                 |
                 v
           Confirm Impact
                 |
                 v
         Collect Evidence
                 |
                 v
              Report
```

---

# What Makes a Good Finding?

A useful finding does not simply say:

```text
Rate limiting missing
```

It explains:

```text
WHAT
Sensitive operation is affected

WHERE
Endpoint / API method

HOW
Protection was tested

SCOPE
Account / source / target behaviour

OBSERVED LIMIT
What happened during testing

BYPASS
How the protection failed, if applicable

IMPACT
What meaningful abuse becomes possible

RECOMMENDATION
Which layer should enforce the control
```

---

# What Not to Do

Do not:

```text
Send millions of requests to prove no limit exists

Lock real customer accounts

Flood real users with reset emails

Send large numbers of SMS messages

Consume expensive cloud resources

Exhaust production API quotas

Perform distributed brute force

Use stolen credentials

Attempt exhaustive OTP brute force

Create denial-of-service conditions
```

unless the exact activity has been explicitly authorised and coordinated.

For ordinary application pentesting, minimal proof is preferable.

---

# Reporting Model

```text
Observation
     |
     v
Is there a sensitive operation?
     |
  +--+--+
  |     |
 NO    YES
  |     |
  v     v
Likely  Can automation meaningfully
Not     abuse the operation?
Issue          |
           +---+---+
           |       |
          NO      YES
           |       |
           v       v
       Hardening   Is an existing
       / Info      control bypassed?
                       |
                  +----+----+
                  |         |
                 NO        YES
                  |         |
                  v         v
              Missing     Rate-Limit /
              Control     Anti-Automation
                            Bypass
                              |
                              v
                         Assess Impact
```

---

# Remediation Checklist

```text
[ ] Identify sensitive operations
[ ] Define expected legitimate usage
[ ] Define abuse scenarios
[ ] Apply server-side limits
[ ] Use multiple dimensions where appropriate
[ ] Add account-level controls
[ ] Add target-level controls
[ ] Add long-term quotas
[ ] Protect challenge workflows
[ ] Prevent replay
[ ] Use progressive friction where appropriate
[ ] Protect against account-lockout abuse
[ ] Coordinate distributed counters
[ ] Use atomic updates
[ ] Protect expensive operations
[ ] Monitor abuse
[ ] Alert on suspicious velocity
[ ] Test alternate API paths
[ ] Test legacy endpoints
[ ] Review limits after architecture changes
```

---

# References

## OWASP Automated Threats to Web Applications

```text
https://owasp.org/www-project-automated-threats-to-web-applications/
```

Useful for understanding automation-driven abuse scenarios.

---

## OWASP Credential Stuffing Prevention Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html
```

Relevant to:

```text
Credential stuffing
Layered defences
Rate limiting
Risk-based controls
CAPTCHA
Monitoring
```

---

## OWASP Authentication Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
```

Relevant to:

```text
Authentication throttling
Account lockout
Password attacks
MFA
```

---

## OWASP Forgot Password Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
```

Relevant to:

```text
Password reset
Consistent responses
Rate limiting
Reset flooding
Token security
```

---

## OWASP Denial of Service Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
```

Useful when evaluating:

```text
Resource consumption
Availability
Expensive operations
```

---

## OWASP API Security

```text
https://owasp.org/API-Security/
```

Pay particular attention to:

```text
Unrestricted Resource Consumption
Unrestricted Access to Sensitive Business Flows
```

when analysing API anti-automation controls.

---

## PortSwigger Web Security Academy - Authentication

```text
https://portswigger.net/web-security/authentication
```

Relevant to:

```text
Brute-force protection
Authentication logic
Account locking
Rate-limit bypass concepts
```

---

## PortSwigger Web Security Academy - Business Logic Vulnerabilities

```text
https://portswigger.net/web-security/logic-flaws
```

Relevant because anti-automation weaknesses frequently become meaningful through business workflows.

---

## PortSwigger Web Security Academy - Race Conditions

```text
https://portswigger.net/web-security/race-conditions
```

Relevant when:

```text
Concurrent requests
```

can bypass counters or business limits.

---

## Turbo Intruder

Official BApp Store:

```text
https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988
```

GitHub:

```text
https://github.com/PortSwigger/turbo-intruder
```

Use only when the assessment requires controlled:

```text
Concurrency
Timing
Burst testing
Race-condition testing
```

---

## HTTP 429 - Too Many Requests

MDN:

```text
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429
```

---

# Final Testing Model

```text
                        AUTOMATION
                            |
                            v
                     SENSITIVE ACTION
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
   Authentication       Verification        Business
        |                   |                Operation
        v                   v                   v
      Login               OTP              Coupon
      Reset              MFA               Export
      Register           Email             Invite
        |                   |                   |
        +-------------------+-------------------+
                            |
                            v
                       RATE CONTROL
                            |
      +----------+----------+----------+----------+
      |          |          |          |          |
      v          v          v          v          v
     IP       Account    Session     Target     Tenant
      |          |          |          |          |
      +----------+----------+----------+----------+
                            |
                            v
                    TIME / COST MODEL
                            |
            +---------------+---------------+
            |               |               |
            v               v               v
          Burst          Sustained         Cost
            |               |               |
            v               v               v
       Per second       Per day        CPU / Money
       Per minute       Quota          Messages
            |               |               |
            +---------------+---------------+
                            |
                            v
                     ANTI-AUTOMATION
                            |
       +------------+-------+-------+------------+
       |            |               |            |
       v            v               v            v
     Delay       Challenge        Replay       Risk
                / CAPTCHA        Prevention    Detection
       |            |               |            |
       +------------+-------+-------+------------+
                            |
                            v
                      BYPASS TESTING
                            |
       +------------+-------+-------+------------+
       |            |               |            |
       v            v               v            v
    Session       Account         Route        Timing
    Rotation      Scope          Version       / Race
       |            |               |            |
       +------------+-------+-------+------------+
                            |
                            v
                         IMPACT
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
       Account            Abuse            Resource
       Compromise         / Fraud          Exhaustion
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                         EVIDENCE
                            |
                            v
                          REPORT
                            |
                            v
                          RETEST
```

The key question during a pentest is not simply:

> **"Can I send many requests?"**

Instead ask:

> **"Can an attacker automate this security-sensitive or business-sensitive operation at a scale that defeats its intended security controls or causes meaningful abuse?"**

For each sensitive action, determine:

```text
What is being protected?

Who is performing the action?

Who or what is being targeted?

Which identifier does the limiter use?

How many attempts are allowed?

Over what period?

What happens when the threshold is reached?

What resets the counter?

Does changing session reset it?

Does changing token reset it?

Does changing endpoint reset it?

Does requesting a new challenge reset it?

Are distributed attempts considered?

Are concurrent attempts handled atomically?

Are long-term quotas present?

Is abuse detected and logged?

What actual security impact does bypassing the control create?
```

That produces a much stronger rate-limiting assessment than simply sending requests until a `429` appears.
