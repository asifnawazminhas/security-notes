# JSON Web Token Security

JSON Web Tokens, commonly abbreviated as JWTs, are widely used for authentication, authorisation, identity federation and API access.

They commonly appear in:

```text
Web applications
REST APIs
Mobile applications
Single Sign-On
OAuth 2.0
OpenID Connect
Microservices
Service-to-service authentication
Password reset workflows
Email verification
API gateways
WebSocket authentication
```

A JWT typically looks like:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.
eyJzdWIiOiIxMjM0NTYiLCJyb2xlIjoidXNlciJ9
.
SIGNATURE
```

The three components are:

```text
HEADER
  .
PAYLOAD
  .
SIGNATURE
```

Conceptually:

```text
Header
   ↓
Algorithm / Key Information

Payload
   ↓
Claims / Identity / Metadata

Signature
   ↓
Integrity Protection
```

A JWT is not automatically secure simply because it contains a signature.

Security depends on:

```text
How the signature is validated
Which algorithms are accepted
How signing keys are selected
How keys are managed
Which claims are trusted
Whether issuer is validated
Whether audience is validated
Whether expiration is enforced
How authorisation is implemented
How tokens are stored
How tokens are revoked
```

!!! warning "Authorised Security Testing"
    JWT testing should only be performed against systems included in the authorised assessment scope. Use controlled accounts and test tokens wherever possible. Do not attempt to impersonate unrelated production users merely to demonstrate that a token validation weakness exists.

---

# JWT Structure

A standard signed JWT is normally composed of three Base64URL-encoded sections:

```text
HEADER.PAYLOAD.SIGNATURE
```

Example:

```text
xxxxx.yyyyy.zzzzz
```

Each section has a different purpose.

---

# Header

The header commonly contains:

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

Potential fields include:

```text
alg
typ
kid
jku
jwk
x5u
x5c
crit
```

Security-sensitive fields include:

```text
alg
kid
jku
jwk
```

because they may influence how the server verifies the token.

---

# Payload

The payload contains claims.

Example:

```json
{
  "iss": "https://identity.example",
  "sub": "248289761001",
  "aud": "target-api",
  "exp": 1780000000,
  "iat": 1779999000,
  "role": "user",
  "email": "user@example.com"
}
```

Claims may describe:

```text
Identity
Issuer
Audience
Expiration
Authentication time
Role
Groups
Organisation
Tenant
Permissions
Scopes
Application state
```

---

# Signature

The signature protects the integrity of the token.

Conceptually:

```text
Base64URL(Header)
        +
"."
        +
Base64URL(Payload)
        ↓
Cryptographic Signing Operation
        ↓
Signature
```

The server should verify the signature before trusting security-sensitive claims.

---

# Encoding Is Not Encryption

JWT headers and payloads are normally encoded rather than encrypted.

For example:

```text
Base64URL
```

does not provide confidentiality.

Therefore:

```text
JWT Payload
     ↓
Usually Readable
```

Anyone possessing the token may normally decode the header and payload.

Do not place unnecessary secrets in JWT claims.

---

# JWT vs JWS vs JWE

JWT is a token format.

Related standards include:

```text
JWS
JSON Web Signature

JWE
JSON Web Encryption
```

A commonly encountered:

```text
header.payload.signature
```

token is typically a signed JWT using JWS.

JWE can provide encrypted token content.

Do not assume all JWTs are encrypted.

---

# JWT Discovery

JWTs can appear in many locations.

Common examples:

```http
Authorization: Bearer eyJ...
```

Cookies:

```http
Cookie: access_token=eyJ...
```

JSON responses:

```json
{
  "access_token": "eyJ..."
}
```

WebSocket messages:

```json
{
  "token": "eyJ..."
}
```

URLs may occasionally contain them as well, although placing sensitive bearer tokens in URLs should generally be avoided.

---

# Recognising JWTs

A JWT often begins with:

```text
eyJ
```

because Base64URL-encoded JSON frequently starts that way.

Typical pattern:

```text
xxxxx.yyyyy.zzzzz
```

You can search Burp history for:

```text
eyJ
```

but do not assume every `eyJ` value is a JWT.

---

# JWT Discovery Workflow

A practical workflow:

```text
Browse Application
      ↓
Burp Proxy
      ↓
HTTP History
      ↓
Search for:
Authorization
Bearer
eyJ
access_token
id_token
jwt
token
      ↓
Identify JWT
      ↓
Decode
      ↓
Map Claims
      ↓
Determine Where Token Is Accepted
```

---

# Burp Suite

Burp Suite is extremely useful for JWT testing.

Useful components include:

```text
Proxy
HTTP History
Repeater
Decoder
Comparer
Extensions
```

A typical workflow:

```text
Browser
   ↓
Burp Proxy
   ↓
Capture JWT
   ↓
Send Request to Repeater
   ↓
Establish Baseline
   ↓
Inspect Token
   ↓
Modify One Security Property
   ↓
Send
   ↓
Observe Server Behaviour
```

---

# Burp JWT Editor

JWT Editor is a commonly used Burp Suite extension for working with JSON Web Tokens.

It can assist with:

```text
Decoding JWTs
Editing claims
Editing headers
Working with signing keys
Generating test keys
Re-signing controlled tokens
Testing algorithm handling
Testing key-selection behaviour
Working with JWKS
```

Install extensions only from trusted sources and understand what the extension changes before sending requests.

The extension assists testing.

It does not replace understanding JWT validation.

---

# Decode a JWT

The first step is normally to decode the token.

Example:

```text
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9
.
eyJzdWIiOiIxMjM0NTYiLCJyb2xlIjoidXNlciJ9
.
SIGNATURE
```

Decoded header:

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

Decoded payload:

```json
{
  "sub": "123456",
  "role": "user"
}
```

At this stage you have learned:

```text
Algorithm
Subject
Role
Potential token purpose
```

but you have not proven a vulnerability.

---

# JWT Claim Inventory

Document important claims.

Example:

| Claim | Example | Purpose |
|---|---|---|
| `iss` | `https://identity.example` | Issuer |
| `sub` | `123456` | Subject |
| `aud` | `target-api` | Audience |
| `exp` | `1780000000` | Expiration |
| `nbf` | `1779999000` | Not before |
| `iat` | `1779999000` | Issued at |
| `jti` | `abc123` | Token identifier |
| `role` | `user` | Application role |
| `scope` | `profile.read` | Permission scope |
| `tenant` | `company-a` | Tenant |

Then determine:

```text
Which claims affect security decisions?
```

---

# Registered Claims

Common registered claims include:

```text
iss
sub
aud
exp
nbf
iat
jti
```

These claims have standard meanings but are not automatically validated merely because they are present.

The application must enforce the relevant validation rules.

---

# iss

The:

```text
iss
```

claim identifies the issuer.

Example:

```json
{
  "iss": "https://identity.example"
}
```

The application should verify that the token came from an expected trusted issuer.

Conceptually:

```text
JWT
 ↓
Verify Signature
 ↓
Read iss
 ↓
Expected Issuer?
 ↓
Accept / Reject
```

---

# Testing Issuer Validation

With controlled tokens and infrastructure, determine whether the application verifies the expected issuer.

The security question is:

```text
Can a correctly structured token from an unintended issuer be accepted?
```

This can be particularly important in:

```text
OAuth
OIDC
Multi-tenant identity systems
Multiple identity-provider deployments
```

---

# sub

The:

```text
sub
```

claim identifies the subject.

Example:

```json
{
  "sub": "user-123"
}
```

The application may use this value to identify the authenticated account.

Questions include:

```text
Is sub immutable?

Is it unique within the issuer?

Is issuer considered together with sub?

Does changing sub change the account?

Does the application instead trust email?
```

---

# aud

The:

```text
aud
```

claim identifies the intended audience.

Example:

```json
{
  "aud": "payments-api"
}
```

A token intended for:

```text
service-a
```

should not automatically be accepted by:

```text
service-b
```

simply because both trust the same signing key.

---

# Audience Validation

Conceptually:

```text
Token
  ↓
Valid Signature
  ↓
aud = API-A
  ↓
Presented to API-B
  ↓
Reject
```

Without audience validation:

```text
Valid token for one service
          ↓
Potentially reusable elsewhere
```

This is especially important in microservice environments.

---

# exp

The:

```text
exp
```

claim defines when the token expires.

Example:

```json
{
  "exp": 1780000000
}
```

After expiration:

```text
Token
 ↓
Expired
 ↓
Rejected
```

---

# Testing Expiration

A useful test is:

```text
Obtain short-lived test token
        ↓
Establish baseline
        ↓
Wait until expiration
        ↓
Replay same request
```

Expected:

```text
Rejected
```

Do not change only the visible `exp` value and assume that proves expiration handling because changing the payload should invalidate the signature.

---

# nbf

The:

```text
nbf
```

claim means:

```text
Not Before
```

Example:

```json
{
  "nbf": 1779999000
}
```

The token should not be accepted before the specified time.

---

# iat

The:

```text
iat
```

claim identifies when the token was issued.

Example:

```json
{
  "iat": 1779999000
}
```

Its security significance depends on how the application uses it.

---

# jti

The:

```text
jti
```

claim provides a token identifier.

Example:

```json
{
  "jti": "1cda8d31-1234-5678"
}
```

It may be used for:

```text
Replay detection
Revocation
Audit correlation
Token tracking
```

Its presence alone does not mean replay protection exists.

---

# Custom Claims

Applications frequently add custom claims.

Examples:

```json
{
  "role": "user",
  "isAdmin": false,
  "tenant": "company-a",
  "permissions": [
    "profile.read"
  ]
}
```

Security testing should identify which custom claims influence authorisation.

---

# Role Claims

Suppose the token contains:

```json
{
  "role": "user"
}
```

The key question is:

```text
Does the application trust this claim?
```

A properly signed role claim can be a legitimate authorisation mechanism.

The vulnerability occurs if the application accepts unauthorised modifications or incorrectly maps the claim.

---

# Authorisation Claims

Potentially interesting claims include:

```text
role
roles
admin
isAdmin
permissions
scope
scopes
groups
tenant
organisation
accountType
subscription
verified
```

Do not blindly modify every claim.

First determine:

```text
Which claims are actually used?
```

---

# Two-Account JWT Testing

Use two controlled accounts:

```text
Account A
Account B
```

Capture tokens for both.

Compare:

```text
Header
Issuer
Subject
Audience
Roles
Scopes
Groups
Tenant
Expiration
Key ID
```

This helps determine which values represent identity and privilege.

---

# Example Comparison

Account A:

```json
{
  "sub": "1001",
  "role": "user",
  "tenant": "company-a"
}
```

Account B:

```json
{
  "sub": "1002",
  "role": "manager",
  "tenant": "company-b"
}
```

Potentially important differences:

```text
sub
role
tenant
```

These become candidates for authorisation threat modelling.

---

# JWT Signature Validation

The most fundamental security requirement is:

```text
Never trust token claims until the token has been cryptographically validated.
```

Conceptually:

```text
JWT Received
    ↓
Parse Header
    ↓
Determine Expected Verification Policy
    ↓
Verify Signature
    ↓
Validate Claims
    ↓
Authorisation
```

The expected verification policy should come from server-side configuration, not from untrusted token input.

---

# alg

The JWT header commonly contains:

```json
{
  "alg": "RS256"
}
```

The:

```text
alg
```

field specifies the algorithm associated with the token.

Common examples include:

```text
HS256
HS384
HS512

RS256
RS384
RS512

PS256
PS384
PS512

ES256
ES384
ES512
```

---

# Algorithm Allowlisting

The server should know which algorithm it expects.

Conceptually:

```text
Server Configuration
       ↓
Expected Algorithm = RS256
       ↓
JWT alg
       ↓
RS256?
       ↓
Continue
```

Avoid:

```text
JWT tells server which arbitrary verification strategy to trust
```

without enforcing an appropriate allowlist.

---

# alg none

Historically, insecure JWT implementations sometimes accepted:

```json
{
  "alg": "none"
}
```

which represents an unsigned token.

A secure application requiring signed JWTs should reject unsigned tokens.

---

# Testing alg none

During an authorised assessment, a controlled test can determine whether the server accepts an unsigned version of your own token.

Conceptually:

```text
Original Signed Test Token
          ↓
Change Header:
alg = none
          ↓
Remove Signature
          ↓
Send Controlled Request
```

Expected:

```text
Rejected
```

Do not use this to impersonate unrelated users.

A failure to reject an unsigned token is already sufficient evidence of broken JWT verification.

---

# Symmetric Algorithms

HMAC algorithms include:

```text
HS256
HS384
HS512
```

These use a shared secret.

Conceptually:

```text
Secret
  ↓
Sign
  ↓
JWT
  ↓
Same Secret
  ↓
Verify
```

Both signing and verification rely on the same secret.

---

# Asymmetric Algorithms

Algorithms such as:

```text
RS256
PS256
ES256
```

use asymmetric cryptography.

Conceptually:

```text
Private Key
    ↓
Sign
    ↓
JWT
    ↓
Public Key
    ↓
Verify
```

The private key should remain protected.

The public verification key can be distributed.

---

# Algorithm Confusion

JWT algorithm confusion vulnerabilities can occur when an implementation incorrectly handles the relationship between:

```text
Symmetric algorithms
```

and:

```text
Asymmetric algorithms
```

Conceptually, a vulnerable implementation may be configured with an RSA public key but incorrectly allow that key material to be treated as an HMAC secret.

A secure implementation should:

```text
Explicitly configure expected algorithms
Use appropriate key types
Reject unexpected algorithm families
Avoid deriving verification policy from attacker-controlled headers
```

---

# Testing Algorithm Confusion

For authorised testing, first establish:

```text
Expected algorithm
Verification key type
Supported algorithms
```

Then determine whether the server accepts tokens using an unintended algorithm family.

Use only your own controlled test identity and claims.

Expected:

```text
Unexpected algorithm
        ↓
Rejected
```

The objective is to demonstrate verification failure without escalating into unrelated accounts.

---

# kid

The:

```text
kid
```

header identifies a signing key.

Example:

```json
{
  "alg": "RS256",
  "kid": "key-2026-01"
}
```

A server may use it like:

```text
JWT kid
   ↓
Key Store
   ↓
Select Public Key
   ↓
Verify Signature
```

---

# Why kid Matters

If key selection is implemented insecurely, attacker-controlled:

```text
kid
```

may influence backend operations.

Potential implementation risks include:

```text
Unsafe file lookup
Unsafe database lookup
Unexpected key selection
Fallback behaviour
Injection into key lookup logic
```

The exact test depends on how the application processes the value.

---

# kid Testing

Start with normal values.

Example:

```json
{
  "kid": "key-1"
}
```

Determine:

```text
What happens when kid is missing?

What happens when kid is unknown?

Does the server fail closed?

Does another known key identifier work?

Are detailed errors returned?
```

Expected:

```text
Unknown key
   ↓
Reject token
```

---

# kid and Path Handling

A poorly implemented application might conceptually perform:

```text
keys/<kid>
```

If so, unsafe path handling could become relevant.

Do not begin by sending destructive filesystem payloads.

First use harmless controlled values to determine whether:

```text
kid
```

appears to influence filesystem-backed key selection.

---

# kid and Database Queries

Another possible implementation:

```text
SELECT key
FROM signing_keys
WHERE kid = ?
```

If parameterisation is used, this is safe.

If the value is concatenated unsafely, injection may theoretically become relevant.

Treat this as an implementation-specific sink rather than assuming every `kid` is an SQL injection target.

---

# jku

The:

```text
jku
```

header may specify a URL containing a JSON Web Key Set.

Example:

```json
{
  "alg": "RS256",
  "jku": "https://identity.example/.well-known/jwks.json"
}
```

If the server follows an attacker-controlled `jku`, this creates an important trust boundary.

---

# Secure jku Handling

A secure implementation should not trust arbitrary key URLs supplied by the token.

Conceptually:

```text
JWT jku
   ↓
Is URL Explicitly Trusted?
   ↓
Yes
   ↓
Retrieve / Use Key
```

Rather than:

```text
JWT jku
   ↓
Fetch Anything
```

---

# jku Testing

During authorised testing determine:

```text
Is jku accepted?

Is it required?

Is the host allowlisted?

Are redirects followed?

Can arbitrary external hosts be supplied?

Is HTTPS required?

Is the resulting key trusted?
```

Use infrastructure you control where callback testing is authorised.

---

# jku and SSRF

If the server retrieves an attacker-controlled:

```text
jku
```

URL, the behaviour may overlap with SSRF.

Conceptually:

```text
JWT
 ↓
jku
 ↓
Server-Side HTTP Request
 ↓
Remote Location
```

If arbitrary destinations are accepted, apply the SSRF methodology.

Refer to:

[Server Side Request Forgery](ssrf.md)

---

# jwk

A JWT header may contain an embedded public key using:

```text
jwk
```

Example conceptually:

```json
{
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "kid": "example"
  }
}
```

A secure server should not automatically trust an arbitrary public key supplied inside an untrusted token.

---

# Embedded JWK Injection

The dangerous trust model is:

```text
Attacker Generates Key Pair
        ↓
Attacker Signs JWT
        ↓
JWT Contains Attacker Public Key
        ↓
Server Trusts Embedded Key
        ↓
Signature Appears Valid
```

A secure implementation should establish trust in signing keys independently of attacker-controlled token contents.

---

# Testing Embedded JWK Handling

Using a controlled account:

```text
Generate test key pair
        ↓
Create token containing own public JWK
        ↓
Sign using corresponding private key
        ↓
Send token
```

Expected:

```text
Rejected
```

unless the application explicitly implements a secure mechanism where embedded keys are trusted through some separate validation process.

---

# JWKS

JSON Web Key Sets are commonly used to publish public verification keys.

Example structure:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "key-1",
      "use": "sig",
      "alg": "RS256",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

OIDC discovery may provide:

```text
jwks_uri
```

---

# Discover JWKS

OIDC:

```bash
curl -s \
  https://identity.example/.well-known/openid-configuration
```

Look for:

```json
{
  "jwks_uri": "https://identity.example/.well-known/jwks.json"
}
```

Then:

```bash
curl -s \
  https://identity.example/.well-known/jwks.json
```

Public signing keys are intended to be public.

Their disclosure is not a vulnerability.

---

# Key Trust

The security question is not:

```text
Can I download the public key?
```

The important question is:

```text
How does the application decide which public key to trust?
```

Potential trust sources include:

```text
Static application configuration
Trusted JWKS endpoint
OIDC discovery
Certificate store
Database
Local filesystem
```

---

# Key Rotation

Signing keys should be rotatable.

A provider may expose:

```text
kid = old-key
kid = current-key
kid = next-key
```

During rotation:

```text
Old tokens may remain valid temporarily
New tokens use new key
```

Testing questions:

```text
How long are retired keys trusted?

What happens to old tokens?

Does an unknown kid fail closed?

Are revoked keys removed?

Does JWKS caching behave safely?
```

---

# JWKS Caching

Applications may cache JWKS responses.

Conceptually:

```text
Identity Provider
      ↓
JWKS
      ↓
Application Cache
      ↓
JWT Verification
```

Caching is normal.

Security considerations include:

```text
Refresh behaviour
Unknown kid handling
Key rotation
Cache lifetime
Failure behaviour
```

---

# x5u

The:

```text
x5u
```

header can reference a URL containing an X.509 certificate or certificate chain.

As with `jku`, the key security question is:

```text
Does the server trust an attacker-controlled URL?
```

Unexpected external key retrieval may create:

```text
Trust issues
SSRF behaviour
Key substitution risks
```

---

# x5c

The:

```text
x5c
```

header may contain an X.509 certificate chain.

The application should validate certificate trust appropriately rather than assuming that the presence of a certificate makes the signing key trustworthy.

---

# Header Injection Threat Model

Security-sensitive JWT header parameters include:

```text
alg
kid
jku
jwk
x5u
x5c
```

Think of the header as:

```text
Untrusted Input
      ↓
Cryptographic Verification Logic
```

This makes strict validation especially important.

---

# Signature Verification vs Claim Validation

A token can have a completely valid signature and still be unacceptable.

Example:

```text
Signature Valid
      ↓
Issuer Wrong
      ↓
Reject
```

or:

```text
Signature Valid
      ↓
Audience Wrong
      ↓
Reject
```

or:

```text
Signature Valid
      ↓
Expired
      ↓
Reject
```

Therefore:

```text
Valid Signature ≠ Valid Token
```

---

# Complete Validation Pipeline

A robust conceptual pipeline is:

```text
Receive JWT
   ↓
Parse Safely
   ↓
Expected Token Type?
   ↓
Expected Algorithm?
   ↓
Trusted Key?
   ↓
Valid Signature?
   ↓
Expected Issuer?
   ↓
Expected Audience?
   ↓
Not Expired?
   ↓
Not Before Satisfied?
   ↓
Required Claims Present?
   ↓
Application Context Valid?
   ↓
Authorisation
```

---

# Token Type Confusion

Applications may process multiple JWT types.

For example:

```text
Access Token
ID Token
Refresh-related token
Email Verification Token
Password Reset Token
Invitation Token
```

If these tokens use similar structures or keys, the application must distinguish their intended purpose.

---

# Access Token vs ID Token

An:

```text
Access Token
```

is generally intended for:

```text
Resource Server / API
```

An:

```text
ID Token
```

is intended to communicate authentication information to an OIDC client.

They should not automatically be interchangeable.

---

# Token Confusion Threat Model

Conceptually:

```text
ID Token
   ↓
Presented to API
   ↓
Does API Accept It?
```

or:

```text
Access Token
   ↓
Presented as Login Identity
   ↓
Does Client Accept It?
```

A secure implementation validates:

```text
Issuer
Audience
Token purpose
Relevant claims
```

---

# Password Reset JWTs

Some applications use JWTs for password reset.

Example:

```text
/reset-password?token=eyJ...
```

Important questions:

```text
Is the token short lived?

Is it single use?

Is it bound to the correct account?

Is its purpose explicitly identified?

Does changing the password invalidate it?

Can it be replayed?
```

---

# Email Verification JWTs

Email verification may use:

```text
/verify-email?token=eyJ...
```

Test:

```text
Expiration
Single-use behaviour
Account binding
Purpose binding
Replay
```

A verification token should not accidentally function as an authentication token.

---

# Invitation JWTs

Organisation invitations may use JWTs.

Example claims:

```json
{
  "email": "user@example.com",
  "organisation": "company-a",
  "role": "member",
  "purpose": "invite"
}
```

Threat model:

```text
Can role be changed?

Can organisation be changed?

Can another user redeem it?

Does it expire?

Can it be reused?

Is identity verified at redemption?
```

---

# Purpose Binding

Tokens should be bound to their intended purpose.

Conceptually:

```text
Token:
purpose = email_verification
```

should not work at:

```text
Password Reset Endpoint
```

or:

```text
Authentication Endpoint
```

even if the same signing infrastructure is used.

---

# Token Replay

JWTs are frequently bearer tokens.

Unless the application maintains state or additional proof mechanisms:

```text
Same Valid Token
       ↓
Can Often Be Reused
```

Whether this is a vulnerability depends on the token's intended semantics.

For an API access token, reuse during its valid lifetime may be normal.

For:

```text
Password reset
Invitation acceptance
Email verification
One-time transaction
```

replay may be dangerous.

---

# Replay Testing

For one-time workflows:

```text
Use Token
   ↓
Action Succeeds
   ↓
Use Same Token Again
```

Expected:

```text
Rejected
```

where the token is explicitly intended to be single use.

Use your own controlled account.

---

# Token Revocation

Stateless JWT validation creates a challenge:

```text
Token Signed
   ↓
Valid Until exp
```

Even after the user logs out, the token may remain cryptographically valid unless the architecture provides revocation or short lifetimes.

---

# Revocation Strategies

Possible approaches include:

```text
Short token lifetime
Token denylist
Session version
User security stamp
Key rotation
Refresh-token revocation
Central introspection
```

The appropriate design depends on the system.

---

# Logout Testing

A practical test:

```text
Login
  ↓
Capture JWT
  ↓
Confirm JWT Works
  ↓
Logout
  ↓
Replay JWT
```

Then determine the application's intended behaviour.

For some systems:

```text
Access token remains valid until expiration
```

may be an intentional architecture.

For others, immediate revocation may be required.

Report the behaviour in the context of the application's security requirements.

---

# Password Change

Test whether:

```text
Password Changed
       ↓
Previously Issued Tokens
       ↓
Still Valid?
```

Again, the expected result depends on design.

High-risk applications may invalidate existing sessions and tokens after credential changes.

---

# Account Disablement

A particularly important scenario:

```text
User Receives JWT
      ↓
Account Disabled
      ↓
JWT Presented Again
```

Expected behaviour for many applications:

```text
Sensitive access denied
```

If authorisation relies solely on stale JWT claims, disabled accounts may retain access until token expiration.

---

# Role Changes

Suppose a token contains:

```json
{
  "role": "admin"
}
```

Then:

```text
Administrator Role Removed
       ↓
Old JWT Still Contains admin
```

Ask:

```text
Does the application re-check current permissions?

How long can stale privilege claims remain valid?
```

This is especially relevant with long-lived tokens.

---

# Tenant Changes

Similarly:

```json
{
  "tenant": "company-a"
}
```

If the user is removed from the organisation:

```text
Old JWT
   ↓
Still Grants Company-A Access?
```

The answer depends on whether the resource server relies entirely on token claims or performs current authorisation checks.

---

# Token Lifetime

Record:

```text
iat
exp
```

Calculate:

```text
Lifetime = exp - iat
```

For example:

```text
iat = 1779999000
exp = 1780002600
```

means:

```text
3600 seconds
=
1 hour
```

Long-lived bearer tokens increase the impact of token theft.

---

# Refresh Tokens

JWT access tokens may be paired with refresh tokens.

Conceptually:

```text
Short-Lived Access Token
          +
Longer-Lived Refresh Token
```

The refresh token can obtain new access tokens.

Security testing should consider both.

---

# Refresh Token Rotation

A common model:

```text
Refresh Token A
      ↓
Redeem
      ↓
Access Token
+
Refresh Token B
```

Then:

```text
Refresh Token A
      ↓
Reuse
      ↓
Rejected
```

This can reduce the impact of refresh-token theft.

---

# Scope Claims

OAuth access tokens may contain:

```json
{
  "scope": "profile.read files.read"
}
```

or:

```json
{
  "scp": [
    "profile.read",
    "files.read"
  ]
}
```

The resource server should enforce the scope.

---

# Scope Enforcement

Conceptually:

```text
JWT
 ↓
scope = profile.read
 ↓
Request:
DELETE /profile
 ↓
Requires profile.write
 ↓
Reject
```

A valid signature does not grant every API permission.

---

# Role vs Scope

These concepts may overlap but are not identical.

Example:

```text
Role:
Administrator

Scope:
users.read
```

The server may require:

```text
Correct Role
+
Correct Scope
+
Correct Object Permission
```

for a sensitive operation.

---

# Object-Level Authorisation

JWTs identify the caller but do not automatically solve object-level authorisation.

Suppose:

```json
{
  "sub": "user-a"
}
```

and the request is:

```http
GET /api/accounts/user-b
```

The server must still determine:

```text
Is user-a authorised to access user-b?
```

Refer to:

[Authorisation Testing](authorisation.md)

---

# JWT and IDOR / BOLA

A common misconception is:

```text
JWT Valid
   ↓
Request Authorised
```

The correct model is:

```text
JWT Valid
   ↓
Caller Identified
   ↓
Requested Object Identified
   ↓
Permission Checked
   ↓
Allow / Deny
```

JWT authentication and object authorisation are separate controls.

---

# JWT and Business Logic

JWT claims may participate in business rules.

Examples:

```text
subscription
accountType
organisation
region
verified
plan
tier
featureFlags
```

Ask:

```text
Is the claim authoritative?

Who creates it?

How often is it refreshed?

Can it become stale?

Does another server-side check exist?
```

---

# JWT Storage

Common storage locations include:

```text
HttpOnly cookie
JavaScript memory
localStorage
sessionStorage
Native secure storage
```

Each approach has different security characteristics.

---

# JWT in Cookies

Example:

```http
Set-Cookie: access_token=eyJ...; Secure; HttpOnly; SameSite=Lax
```

Review:

```text
Secure
HttpOnly
SameSite
Path
Domain
Expiration
```

If the JWT cookie is automatically included by the browser, CSRF considerations may also apply.

---

# JWT in localStorage

Example:

```javascript
localStorage.setItem("token", token);
```

The token becomes accessible to JavaScript executing within that origin.

Therefore:

```text
XSS
 ↓
Potential Token Access
```

This does not mean `localStorage` alone constitutes a vulnerability, but it affects the threat model.

---

# JWT in sessionStorage

`sessionStorage` is also accessible to JavaScript within the relevant origin and browser context.

XSS therefore remains relevant.

---

# JWT in URLs

Avoid transmitting bearer JWTs in URLs where possible.

URLs may appear in:

```text
Browser history
Proxy logs
Web server logs
Analytics
Referer headers
Monitoring systems
Screenshots
```

Prefer appropriate headers or secure cookie mechanisms.

---

# JWT Leakage

Search for token exposure in:

```text
URLs
HTML
JavaScript
Logs
Error messages
Referer
Browser storage
Source maps
Debug interfaces
Analytics
Third-party requests
```

The impact depends on:

```text
Token privileges
Token lifetime
Audience
Replayability
Revocation
```

---

# JWT and XSS

If JavaScript can access the JWT:

```text
XSS
 ↓
JavaScript Execution
 ↓
Token Access
 ↓
Potential Session Impact
```

Therefore token storage and XSS threat modelling should be considered together.

Refer to:

[Cross-Site Scripting](xss.md)

---

# JWT and CSRF

If authentication is stored in automatically included cookies:

```text
Browser
 ↓
Cross-Site Request
 ↓
Cookie Automatically Included
```

CSRF protections may be required depending on:

```text
SameSite
Request method
Application design
Additional CSRF controls
```

Refer to:

[Cross-Site Request Forgery](csrf.md)

---

# JWT and CORS

Bearer tokens are frequently used with APIs.

Review:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
```

but assess actual impact.

Permissive CORS is not automatically exploitable if the browser cannot obtain or send the relevant credential.

---

# JWT and OAuth

OAuth access tokens may be JWTs.

But:

```text
OAuth Access Token
```

does not have to be a JWT.

Some access tokens are opaque.

When the token is a JWT, apply both:

```text
OAuth threat model
+
JWT validation threat model
```

Refer to:

[OAuth 2.0 and OpenID Connect Security](oauth-oidc.md)

---

# JWT and OpenID Connect

OIDC ID Tokens are JWTs.

Therefore validate:

```text
Signature
iss
aud
exp
nonce
Token purpose
```

Do not simply decode the ID Token and trust the resulting identity.

---

# Multi-Tenant JWT Security

Multi-tenant applications may include:

```json
{
  "tenant": "company-a"
}
```

or:

```json
{
  "tid": "123456"
}
```

Questions include:

```text
Is tenant validated?

Is tenant part of authorisation?

Can the user belong to multiple tenants?

Can stale tokens retain old tenant access?

Does issuer differ between tenants?

Can tokens cross tenant boundaries?
```

---

# Tenant Isolation Test

Using two controlled tenants:

```text
Tenant A
Tenant B
```

and controlled users:

```text
User A
User B
```

test:

```text
Token A → Resource A
Token B → Resource B
```

then controlled cross-boundary cases:

```text
Token A → Resource B
Token B → Resource A
```

Expected:

```text
Denied
```

This is fundamentally an authorisation test.

---

# Microservices

JWTs are frequently used between microservices.

Architecture:

```text
User
 ↓
API Gateway
 ↓
JWT
 ↓
Service A
 ↓
Service B
 ↓
Service C
```

Security questions include:

```text
Does every service validate the signature?

Does every service validate audience?

Do services trust gateway-added headers?

Are internal services directly reachable?

Can a token intended for Service A reach Service B?
```

---

# Gateway Trust

Some architectures validate the JWT only at the gateway:

```text
Internet
 ↓
API Gateway
 ↓
JWT Validation
 ↓
X-User-ID Header
 ↓
Backend
```

The backend may then trust:

```http
X-User-ID: 123
```

Ask:

```text
Can clients reach the backend directly?

Can clients inject trusted identity headers?

Does the gateway remove client-supplied versions?

Is the trust boundary enforced?
```

This may become a broader architecture or authorisation finding rather than a JWT issue.

---

# Error Handling

JWT validation errors can reveal useful implementation details.

Examples:

```text
Invalid signature
Unknown kid
Token expired
Unsupported algorithm
Invalid issuer
Invalid audience
Malformed JWT
```

Some differentiation is useful operationally, but production responses should avoid unnecessary sensitive implementation details.

---

# Error Behaviour Matrix

Document:

| Test | Result |
|---|---|
| Valid token | 200 |
| Missing token | 401 |
| Malformed token | 401 |
| Invalid signature | 401 |
| Expired token | 401 |
| Wrong audience | 401 |
| Unknown `kid` | 401 |

Unexpected differences may help identify validation gaps.

---

# Malformed JWT Testing

Safe malformed-token tests can include:

```text
Missing token
Empty token
One segment
Two segments
Four segments
Invalid Base64URL
Invalid JSON
Missing header
Missing payload
Missing signature
```

Expected:

```text
Controlled rejection
```

The application should not return:

```text
Stack traces
Internal paths
Framework debug information
```

---

# Missing Claims

Where claims are required, test controlled tokens missing:

```text
iss
sub
aud
exp
```

where you have the ability to create appropriately signed test tokens.

Expected behaviour depends on token policy.

Required claims should be explicitly enforced.

---

# Duplicate JSON Claims

JSON parsers can behave differently when duplicate properties exist.

Conceptually:

```json
{
  "role": "user",
  "role": "admin"
}
```

Different parsers may interpret:

```text
First value
Last value
Error
```

JWT libraries should reject ambiguous token structures or process them consistently.

This becomes especially interesting when:

```text
Gateway parser
      ↓
Backend parser
```

behave differently.

---

# Case Sensitivity

Test assumptions around:

```text
Issuer
Audience
Role
Scope
Tenant
```

where application logic may apply inconsistent normalisation.

For example:

```text
Admin
admin
ADMIN
```

should not unexpectedly cross role boundaries because different components normalise values differently.

---

# JWT Key Management

Secure JWT architecture depends heavily on key management.

Signing keys should be:

```text
Strong
Protected
Rotatable
Access controlled
Auditable
Separated by environment
```

Avoid:

```text
Hard-coded production secrets
Shared secrets across unrelated applications
Keys committed to source repositories
Extremely weak HMAC secrets
```

---

# Weak HMAC Secrets

If an application uses:

```text
HS256
```

the signing secret must have sufficient entropy.

A weak human-readable secret can undermine the entire signing mechanism.

Examples of poor secret choices conceptually include:

```text
password
secret
companyname
jwtsecret
```

Do not perform uncontrolled password cracking against production systems.

For an authorised assessment, agree on appropriate password-auditing constraints and rate/resource limits.

---

# HMAC Secret Testing

If explicitly authorised:

```text
Identify HS algorithm
      ↓
Use captured token from own account
      ↓
Perform controlled offline secret audit
      ↓
Determine whether weak secret is recoverable
```

Because JWT verification is offline, this can be resource intensive without generating requests to the application.

The scope should still explicitly permit credential or secret-strength testing.

---

# Environment Separation

Development and production environments should not unnecessarily share signing keys.

Otherwise:

```text
Compromise Development Key
        ↓
Potential Production Impact
```

Test environments should use separate key material.

---

# Key Rotation Threat Model

Ask:

```text
How are new keys introduced?

How are old keys removed?

How long are old keys trusted?

What happens when a key is compromised?

Can tokens be invalidated quickly?

How does JWKS caching respond?
```

---

# JWT Testing Workflow

A structured JWT assessment:

```text
Identify JWT
    ↓
Determine Token Purpose
    ↓
Decode Header
    ↓
Decode Payload
    ↓
Identify Algorithm
    ↓
Identify kid / jku / jwk
    ↓
Identify Claims
    ↓
Determine Verification Architecture
    ↓
Test Signature Enforcement
    ↓
Test Algorithm Policy
    ↓
Test Key Selection
    ↓
Test Issuer
    ↓
Test Audience
    ↓
Test Lifetime
    ↓
Test Token Purpose
    ↓
Test Roles / Scopes
    ↓
Test Object Authorisation
    ↓
Test Replay
    ↓
Test Logout / Revocation
    ↓
Review Storage
    ↓
Review Leakage
    ↓
Collect Evidence
    ↓
Report
```

---

# Burp JWT Testing Workflow

```text
Proxy
  ↓
Capture Authenticated Request
  ↓
Send to Repeater
  ↓
Confirm Baseline
  ↓
Inspect JWT
  ↓
Decode Header / Payload
  ↓
Identify Security-Relevant Claims
  ↓
Modify One Element
  ↓
Send
  ↓
Compare Response
```

Do not modify five different JWT properties at once.

Change one variable so you know what caused the observed behaviour.

---

# Test Order

A useful order is:

```text
1. Baseline valid token

2. Missing token

3. Malformed token

4. Modified payload without valid signature

5. Expired token

6. Wrong issuer

7. Wrong audience

8. Unexpected algorithm

9. Unknown kid

10. Token purpose confusion

11. Role / scope behaviour

12. Logout / revocation

13. Storage and leakage
```

Not every test applies to every application.

---

# Baseline First

Before testing anything, confirm:

```text
Known Valid Token
      ↓
Known Request
      ↓
Known Response
```

For example:

```http
GET /api/profile HTTP/1.1
Host: target.example
Authorization: Bearer VALID_TEST_TOKEN
```

Response:

```http
HTTP/1.1 200 OK
```

Now modifications can be compared against a stable baseline.

---

# Modified Payload Without Re-Signing

One of the simplest validation checks:

```text
Valid JWT
   ↓
Modify payload
   ↓
Leave original signature
   ↓
Send
```

Expected:

```text
Rejected
```

If accepted, signature verification may be missing or broken.

Use only your own identity and a harmless claim change.

---

# Example Controlled Claim Change

Original:

```json
{
  "sub": "test-user",
  "displayName": "Test User"
}
```

Modified:

```json
{
  "sub": "test-user",
  "displayName": "JWT-TEST"
}
```

If the server accepts the modified token despite an invalid signature, the verification problem has been demonstrated without attempting privilege escalation.

---

# Authorisation Testing

After cryptographic validation has been assessed, move to application authorisation.

Ask:

```text
Does role affect endpoints?

Does scope affect actions?

Does tenant affect object access?

Does sub affect resource ownership?

Are permissions checked server-side?
```

Use controlled accounts.

---

# JWT Authorisation Matrix

Example:

| Token | Endpoint | Expected |
|---|---|---|
| User | `/api/profile` | Allow |
| User | `/api/admin` | Deny |
| Admin | `/api/admin` | Allow |
| Tenant A | Tenant A object | Allow |
| Tenant A | Tenant B object | Deny |
| Read scope | GET | Allow |
| Read scope | DELETE | Deny |

This provides much clearer evidence than random claim mutation.

---

# JWT and Horizontal Privilege Escalation

Example:

```text
User A JWT
    ↓
GET /api/users/A
    ↓
Allowed
```

Then:

```text
User A JWT
    ↓
GET /api/users/B
```

Expected:

```text
Denied
```

This test does not require modifying the JWT.

The JWT authenticates User A while the object identifier tests authorisation.

---

# JWT and Vertical Privilege Escalation

Example:

```text
Normal User JWT
       ↓
POST /api/admin/action
```

Expected:

```text
Denied
```

Again, do not assume you need to forge an administrator JWT.

First test whether the endpoint itself enforces authorisation.

---

# Claim Trust vs Server-Side State

Some applications use JWT claims as the complete authorisation state.

Others use the JWT only for identity:

```text
JWT
 ↓
sub
 ↓
Database
 ↓
Current Role
 ↓
Authorisation
```

Both architectures can work.

The security implications differ.

---

# Stale Claims

JWT claims can become stale.

Example:

```text
Token issued:
role = admin
       ↓
Role removed in database
       ↓
Token still says:
role = admin
```

Ask:

```text
How quickly should the privilege change take effect?
```

This is an architectural security decision.

---

# Clock Skew

JWT validation may allow small clock differences.

For example:

```text
30 seconds
60 seconds
```

This can be legitimate.

Do not report a small expiration tolerance as a vulnerability without meaningful impact.

---

# JWT Size

JWTs can become large when they contain:

```text
Many groups
Many roles
Large permission sets
User metadata
Certificates
```

Large tokens can affect:

```text
HTTP header limits
Proxy behaviour
Cookie limits
Performance
```

Avoid intentionally generating extremely large production requests without explicit approval.

---

# Sensitive Data in JWTs

Because JWT payloads are often readable, avoid placing unnecessary:

```text
Passwords
Secrets
API keys
Private personal data
Internal credentials
```

inside them.

A token should contain only the claims required for its purpose.

---

# Logging

Applications and infrastructure may log:

```http
Authorization: Bearer eyJ...
```

This can expose active bearer tokens.

Review:

```text
Reverse proxy logs
Application logs
Debug logs
Monitoring
APM
Error reports
Support exports
```

Sensitive token values should normally be redacted.

---

# Browser Developer Tools

Useful areas include:

```text
Network
Application
Cookies
Local Storage
Session Storage
```

Determine:

```text
Where token is stored
How it is transmitted
When it is refreshed
Whether JavaScript can access it
```

---

# curl

A JWT-authenticated API request might look like:

```bash
curl -i \
  -H "Authorization: Bearer TEST_TOKEN" \
  https://target.example/api/profile
```

Use only authorised test tokens.

Avoid placing real production tokens in:

```text
Shell history
Shared scripts
Screenshots
Reports
Git repositories
```

---

# JWT Decoding With Python

For local inspection, the JWT components can be decoded without sending the token to an external website.

Example:

```python
import base64
import json

token = "HEADER.PAYLOAD.SIGNATURE"

header_b64, payload_b64, signature_b64 = token.split(".")

def decode_part(value):
    value += "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value)

header = json.loads(decode_part(header_b64))
payload = json.loads(decode_part(payload_b64))

print(json.dumps(header, indent=2))
print(json.dumps(payload, indent=2))
```

This only decodes the token.

It does not verify the signature.

---

# Avoid Public JWT Decoder Sites for Sensitive Tokens

Public JWT inspection websites may be convenient, but active tokens should be treated as credentials.

Prefer:

```text
Burp Decoder
Local scripts
Local JWT tools
Browser Developer Tools
```

for sensitive assessment tokens.

---

# Tools

Useful JWT testing tools include:

```text
Burp Suite
JWT Editor
Burp Decoder
Burp Repeater
Browser Developer Tools
curl
Python
jwt_tool
JOSE / JWT libraries
OIDC discovery
JWKS endpoints
```

---

# jwt_tool

`jwt_tool` is a security testing utility for analysing JWT implementations.

It can assist with areas such as:

```text
Token decoding
Claim inspection
Signature testing
Algorithm analysis
Key handling
JWT security checks
```

Use it only against authorised targets.

Always understand the individual test being performed rather than treating automated output as proof of a vulnerability.

---

# Automation

Automated JWT tools can help identify:

```text
Algorithms
Headers
Claims
Potential configuration weaknesses
```

but automation cannot reliably determine:

```text
Business impact
Account mapping
Tenant boundaries
Role semantics
Object-level authorisation
Expected token lifetime
Whether token reuse is intentional
```

Manual analysis remains essential.

---

# JWT Testing Checklist

## Discovery

```text
[ ] Search Authorization headers
[ ] Search cookies
[ ] Search JSON responses
[ ] Search browser storage
[ ] Search WebSocket messages
[ ] Identify access tokens
[ ] Identify ID tokens
[ ] Identify other JWT workflows
```

## Structure

```text
[ ] Decode header
[ ] Decode payload
[ ] Identify algorithm
[ ] Identify kid
[ ] Identify jku
[ ] Identify jwk
[ ] Identify issuer
[ ] Identify audience
[ ] Identify subject
[ ] Identify expiration
[ ] Identify roles
[ ] Identify scopes
[ ] Identify tenant
```

## Signature

```text
[ ] Confirm modified payload is rejected
[ ] Confirm unsigned token is rejected
[ ] Review allowed algorithms
[ ] Review algorithm family
[ ] Review key type
```

## Key Selection

```text
[ ] Review kid
[ ] Test unknown kid
[ ] Review jku
[ ] Review jwk
[ ] Review x5u where present
[ ] Review JWKS
[ ] Review key rotation
```

## Claims

```text
[ ] Validate issuer
[ ] Validate audience
[ ] Validate expiration
[ ] Validate not-before
[ ] Review subject
[ ] Review required claims
[ ] Review custom claims
```

## Token Purpose

```text
[ ] Distinguish access token
[ ] Distinguish ID token
[ ] Review password reset token
[ ] Review verification token
[ ] Review invitation token
[ ] Test purpose binding where relevant
```

## Authorisation

```text
[ ] Test role enforcement
[ ] Test scope enforcement
[ ] Test object-level authorisation
[ ] Test tenant isolation
[ ] Test controlled horizontal access
[ ] Test controlled vertical access
```

## Lifecycle

```text
[ ] Record token lifetime
[ ] Test expiration
[ ] Review refresh behaviour
[ ] Review refresh rotation
[ ] Test logout behaviour
[ ] Test password-change behaviour
[ ] Test account disablement
[ ] Test role changes
```

## Storage

```text
[ ] Review cookies
[ ] Review localStorage
[ ] Review sessionStorage
[ ] Review JavaScript exposure
[ ] Review URL exposure
[ ] Review logs
```

## Errors

```text
[ ] Test missing token
[ ] Test malformed token
[ ] Test invalid signature
[ ] Test expired token
[ ] Test unknown kid
[ ] Review error detail
```

---

# JWT Quick Reference

```text
STRUCTURE

HEADER.PAYLOAD.SIGNATURE
```

```text
HEADER

alg
typ
kid
jku
jwk
x5u
x5c
```

```text
REGISTERED CLAIMS

iss
sub
aud
exp
nbf
iat
jti
```

```text
APPLICATION CLAIMS

role
roles
scope
permissions
groups
tenant
organisation
isAdmin
```

```text
COMMON ALGORITHMS

HS256
RS256
PS256
ES256
```

```text
SECURITY QUESTIONS

Is the signature verified?
Is the expected algorithm enforced?
Is the signing key trusted?
Is issuer validated?
Is audience validated?
Is expiration enforced?
Is token purpose validated?
Are roles enforced?
Are scopes enforced?
Are objects authorised?
```

---

# JWT Decision Tree

```text
JWT Found
   ↓
What Is Its Purpose?
   ↓
Access / ID / Reset / Invite / Other
   ↓
Decode Header
   ↓
Which Algorithm?
   ↓
Expected Algorithm?
   ↓
Which Key?
   ↓
kid / JWKS / Static / Other
   ↓
Signature Verified?
   ↓
Issuer Valid?
   ↓
Audience Valid?
   ↓
Lifetime Valid?
   ↓
Purpose Valid?
   ↓
Which Claims Affect Access?
   ↓
Role?
Scope?
Tenant?
Subject?
   ↓
Authorisation Enforced?
   ↓
Object-Level Checks?
   ↓
Replay Relevant?
   ↓
Revocation Required?
   ↓
Secure Storage?
```

---

# Five Questions for Every JWT

For every JWT ask:

```text
1. Who signed this token?

2. How does the application know that signing key is trusted?

3. What system is this token intended for?

4. Which claims affect authentication or authorisation?

5. When does the token stop being valid?
```

Then ask:

```text
6. Can the token be replayed?

7. What happens after logout?

8. What happens after a role or tenant change?

9. Where is the token stored?

10. Can another token type be used in its place?
```

---

# JWT Threat Model Template

```text
TOKEN:
Access Token

LOCATION:
Authorization: Bearer

ALGORITHM:
RS256

ISSUER:
https://identity.example

AUDIENCE:
target-api

KEY SOURCE:
Trusted JWKS

KEY ID:
key-2026-01

SUBJECT:
Application user ID

LIFETIME:
60 minutes

ROLES:
user

SCOPES:
profile.read

TENANT:
company-a

STORAGE:
Browser memory

REFRESH:
Refresh token rotation

LOGOUT:
Application session invalidated

AUTHORISATION:
API checks role + object ownership
```

Then derive tests:

```text
Signature enforcement
Algorithm enforcement
Unknown kid
Issuer
Audience
Expiration
Scope
Role
Tenant isolation
Object ownership
Logout
Refresh rotation
```

---

# Evidence Collection

For a JWT-related finding record:

```text
Affected endpoint
Token purpose
Algorithm
Relevant header
Relevant claims
Account / role
Original request
Modified request
Expected behaviour
Observed behaviour
Security impact
```

Redact the active token.

For example:

```text
eyJhbGciOiJSUzI1Ni...REDACTED...abc123
```

---

# Example Signature Validation Finding

```text
Finding:
JWT Signature Is Not Validated

Affected Endpoint:
GET /api/profile

Baseline:
A valid JWT for the controlled test account was accepted.

Test:
A non-security-sensitive claim in the JWT payload was modified without generating a new signature.

Expected:
The token should be rejected because the signature no longer matches the token contents.

Observed:
The modified token remained accepted.

Impact:
An attacker possessing a token may be able to modify claims without cryptographic verification, undermining the integrity guarantees of the authentication mechanism.
```

---

# Example Algorithm Finding

```text
Finding:
JWT Verification Accepts Unsigned Tokens

Expected:
The application requires cryptographically signed JWTs.

Observed:
An unsigned JWT using an unsupported unsigned mode was accepted for the controlled test account.

Impact:
JWT integrity verification can be bypassed, allowing token claims to be modified without possession of the legitimate signing key.
```

---

# Example Audience Finding

```text
Finding:
JWT Audience Is Not Validated

Expected:
The API should accept only tokens issued for its configured audience.

Observed:
A valid test token intended for a different controlled application audience was accepted.

Impact:
Tokens issued for another service may be reusable against the affected API, weakening service isolation.
```

---

# Example Expiration Finding

```text
Finding:
Expired JWTs Remain Valid

Expected:
Tokens should be rejected after their expiration time.

Observed:
The same controlled test token continued to provide authenticated access after its exp timestamp had passed.

Impact:
Compromised tokens may remain usable beyond their intended lifetime.
```

---

# Example Stale Role Finding

```text
Finding:
Removed Privileges Remain Active Through Existing JWTs

Expected:
Removal of the administrative role should prevent further administrative actions within the required security window.

Observed:
A JWT issued before the role was removed continued to authorise administrative operations until token expiration.

Impact:
Revoked privileges remain usable for the lifetime of previously issued tokens.
```

Whether this constitutes a vulnerability depends on the application's intended revocation requirements.

---

# Example Tenant Finding

```text
Finding:
JWT-Authenticated Users Can Access Resources Across Tenant Boundaries

Token:
Controlled User A
Tenant:
Tenant A

Requested Resource:
Controlled object belonging to Tenant B

Expected:
Access denied.

Observed:
The resource was returned successfully.

Impact:
Tenant isolation is not correctly enforced for authenticated API requests.
```

The root cause may be object-level authorisation rather than JWT validation itself.

Report the underlying security failure accurately.

---

# Reporting Titles

Prefer precise titles such as:

```text
JWT Signature Is Not Validated

JWT Verification Accepts Unsigned Tokens

JWT Verification Accepts Unexpected Algorithms

JWT Audience Is Not Validated

JWT Issuer Is Not Validated

Expired JWTs Remain Valid

JWT Key Selection Trusts Unvalidated Key Sources

JWT Access Tokens Remain Valid After Account Disablement

JWT Scope Is Not Enforced by the API

JWT-Authenticated Users Can Access Cross-Tenant Resources

Password Reset JWT Can Be Reused

ID Token Is Accepted as an API Access Token

JWT Bearer Token Is Exposed in Application Logs
```

Avoid:

```text
JWT Vulnerability
```

because it does not describe the actual security failure.

---

# Remediation

JWT security should use established JWT, JOSE and OIDC libraries rather than custom cryptographic code.

The validation policy should be defined server-side.

---

# Secure Validation Model

```text
JWT Received
   ↓
Expected Token Type?
   ↓
Expected Algorithm?
   ↓
Trusted Key?
   ↓
Valid Signature?
   ↓
Expected Issuer?
   ↓
Expected Audience?
   ↓
Valid Lifetime?
   ↓
Required Claims?
   ↓
Correct Purpose?
   ↓
Current Authorisation?
   ↓
Allow
```

Failure at any required stage should result in rejection.

---

# Algorithm Protection

Configure an explicit allowlist.

For example conceptually:

```text
Expected:
RS256
```

Reject:

```text
none
HS256
ES256
Unexpected algorithm
```

unless explicitly required by the application architecture.

---

# Key Protection

Signing keys should be:

```text
Strong
Protected
Rotated
Environment-specific
Access controlled
Monitored
```

Private keys and HMAC secrets must remain confidential.

---

# kid Protection

Treat:

```text
kid
```

as untrusted input.

Use it only to select from an explicitly trusted key store.

Avoid constructing unsafe:

```text
File paths
SQL statements
URLs
Commands
```

from the value.

---

# jku and jwk Protection

Do not trust arbitrary key sources supplied by an untrusted JWT.

Signing-key trust should be established through server-side configuration and trusted identity metadata.

---

# Claim Validation

Explicitly validate required claims.

Examples:

```text
iss
aud
exp
nbf
```

Do not assume the JWT library validates every claim automatically.

Library defaults differ.

---

# Purpose Separation

Where multiple JWT types exist:

```text
Access
Identity
Password reset
Email verification
Invitation
```

bind them to explicit purposes and audiences.

Where appropriate, use:

```text
Different audiences
Different claims
Different keys
Different validation policies
```

to reduce token confusion.

---

# Authorisation

JWT validation should identify a trusted caller.

It should not replace authorisation.

For every sensitive request:

```text
Trusted Identity
      ↓
Requested Action
      ↓
Requested Object
      ↓
Current Permissions
      ↓
Allow / Deny
```

---

# Token Lifetime

Use token lifetimes appropriate to:

```text
Risk
Application type
Revocation capability
Refresh architecture
User experience
```

Avoid unnecessarily long-lived bearer access tokens.

---

# Refresh Token Protection

Refresh tokens should receive stronger protection because they can generate new access tokens.

Consider:

```text
Rotation
Reuse detection
Revocation
Secure storage
Expiration
Device/session binding where appropriate
```

---

# Secure Storage

Select storage based on the application threat model.

Consider:

```text
XSS
CSRF
Browser behaviour
Mobile platform protections
Token lifetime
Refresh architecture
```

There is no universal storage mechanism that removes every threat.

---

# Logging Protection

Do not log complete bearer tokens unnecessarily.

Redact:

```text
Authorization headers
JWT cookies
Refresh tokens
Authorization codes
```

in:

```text
Application logs
Proxy logs
APM
Error reports
Support tooling
```

---

# Recommended JWT Testing Workflow

```text
                    APPLICATION
                         ↓
                    JWT FOUND
                         ↓
                 DETERMINE PURPOSE
                         ↓
              ┌──────────┼──────────┐
              ↓          ↓          ↓
           Access       ID       Workflow
            Token      Token       Token
              ↓          ↓          ↓
              └──────────┼──────────┘
                         ↓
                    DECODE JWT
                         ↓
              ┌──────────┼──────────┐
              ↓          ↓          ↓
            Header     Claims    Signature
              ↓          ↓          ↓
              └──────────┼──────────┘
                         ↓
                 VALIDATION POLICY
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
   Algorithm            Key              Claims
       ↓                 ↓                 ↓
 alg allowlist      kid / JWKS      iss / aud / exp
       ↓                 ↓                 ↓
       └─────────────────┼─────────────────┘
                         ↓
                  TOKEN PURPOSE
                         ↓
                   AUTHORISATION
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
      Role              Scope            Tenant
       ↓                 ↓                 ↓
       └─────────────────┼─────────────────┘
                         ↓
                 OBJECT OWNERSHIP
                         ↓
                   TOKEN LIFETIME
                         ↓
              LOGOUT / REVOCATION
                         ↓
                  TOKEN STORAGE
                         ↓
                     LEAKAGE
                         ↓
                COLLECT EVIDENCE
                         ↓
                      REPORT
```

---

# References

## PortSwigger Web Security Academy: JWT Attacks

https://portswigger.net/web-security/jwt

Excellent practical material covering JWT security testing.

---

## PortSwigger: JWT Algorithm Confusion

https://portswigger.net/web-security/jwt/algorithm-confusion

Useful for understanding algorithm confusion between symmetric and asymmetric JWT verification.

---

## PortSwigger: JWT Header Parameter Injection

https://portswigger.net/web-security/jwt#injecting-self-signed-jwts-via-the-jwk-parameter

Useful for understanding security-sensitive JWT header parameters such as:

```text
jwk
jku
kid
```

---

## PortSwigger JWT Editor

https://portswigger.net/bappstore/26aaa5a046f341debeea7ebc74d7f27d

Burp Suite extension for working with JWTs and signing keys during authorised testing.

---

## OWASP JSON Web Token Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

Useful defensive guidance covering JWT implementation considerations.

---

## OWASP REST Security Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html

Relevant for JWT bearer authentication and API authorisation.

---

## RFC 7519: JSON Web Token

https://datatracker.ietf.org/doc/html/rfc7519

The JSON Web Token specification.

---

## RFC 7515: JSON Web Signature

https://datatracker.ietf.org/doc/html/rfc7515

Defines JSON Web Signature.

---

## RFC 7517: JSON Web Key

https://datatracker.ietf.org/doc/html/rfc7517

Defines JSON Web Keys and JSON Web Key Sets.

---

## RFC 8725: JWT Best Current Practices

https://datatracker.ietf.org/doc/html/rfc8725

Important security guidance for JWT implementations.

---

## OpenID Connect Core

https://openid.net/specs/openid-connect-core-1_0.html

Relevant for JWT-based ID Tokens and OIDC claim validation.

---

## jwt_tool

https://github.com/ticarpi/jwt_tool

Useful JWT testing utility for authorised security assessments.

---

# Final JWT Testing Model

```text
JWT
 ↓
What is it?
 ↓
Who issued it?
 ↓
Who should accept it?
 ↓
Which algorithm should be used?
 ↓
Which key should verify it?
 ↓
Is the signature valid?
 ↓
Is the issuer trusted?
 ↓
Is the audience correct?
 ↓
Is the token currently valid?
 ↓
Is this the correct token type?
 ↓
Who is the subject?
 ↓
Which roles/scopes apply?
 ↓
Which tenant applies?
 ↓
What action is requested?
 ↓
Which object is requested?
 ↓
Is this subject authorised?
 ↓
Has access been revoked?
 ↓
Allow / Deny
```

The key principle is:

> A JWT should be treated as an untrusted assertion until its signature, signing key, algorithm, issuer, audience, lifetime and intended purpose have been validated. Even after successful JWT validation, the application must still enforce current server-side authorisation for the requested action and object.
