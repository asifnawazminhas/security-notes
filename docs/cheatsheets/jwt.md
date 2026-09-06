---
title: JWT Security Testing Cheatsheet
description: Practical JSON Web Token security testing cheatsheet covering token structure, claims, signatures, algorithms, key handling, JWKS, validation, session lifecycle, authorization, Burp Suite, source review, evidence, remediation and retesting.
---

# JWT Security Testing Cheatsheet

JSON Web Tokens are commonly used to carry authenticated identity and authorization information between systems.

A typical JWT looks like:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.
eyJzdWIiOiIxMjMiLCJyb2xlIjoidXNlciJ9
.
SIGNATURE
```

The three components are:

```text
HEADER
  |
  v
PAYLOAD
  |
  v
SIGNATURE
```

More precisely:

```text
Base64URL(Header)
      .
Base64URL(Payload)
      .
Signature
```

!!! warning "Authorised Security Testing"

    Test JWT implementations only against applications and accounts included in the assessment scope. Use dedicated test accounts and controlled tokens where possible. Do not attempt to forge privileged production tokens or access unrelated user data simply to demonstrate a validation weakness.


# JWT Mental Model

JWT security depends on more than:

```text
Is the token signed?
```

A stronger model is:

```text
Token Received
     |
     v
Parse Token
     |
     v
Validate Algorithm
     |
     v
Select Trusted Key
     |
     v
Verify Signature
     |
     v
Validate Issuer
     |
     v
Validate Audience
     |
     v
Validate Time Claims
     |
     v
Interpret Claims
     |
     v
Authorization Decision
```


# JWT vs JWS vs JWE

JWT is a token format.

JWTs may be represented using:

```text
JWS
```

for signed or MAC-protected content, or:

```text
JWE
```

for encrypted content.


# JWS

A common signed JWT contains three segments:

```text
HEADER.PAYLOAD.SIGNATURE
```


# JWE

A compact JWE contains five segments.

Conceptually:

```text
HEADER
.
ENCRYPTED KEY
.
IV
.
CIPHERTEXT
.
AUTHENTICATION TAG
```


# Important

Most JWTs encountered during ordinary web application testing are signed JWS tokens.

Do not assume:

```text
JWT = encrypted
```


# Base64URL Is Not Encryption

The header and payload of an ordinary signed JWT can usually be decoded without knowing the signing key.


# Example Payload

```json
{
  "sub": "123",
  "name": "Test User",
  "role": "user"
}
```


# Security Property

The signature protects integrity and authenticity when implemented correctly.

It does not inherently provide confidentiality.


# Identify JWTs

JWTs commonly appear in:

```text
Authorization headers

Cookies

API responses

localStorage

sessionStorage

OAuth/OIDC flows

WebSocket authentication

Mobile application traffic
```


# Authorization Header

```http
Authorization: Bearer eyJhbGciOi...
```


# Cookie

```http
Cookie: access_token=eyJhbGciOi...
```


# JSON Response

```json
{
  "access_token": "eyJhbGciOi..."
}
```


# Browser Storage

Applications may store tokens in:

```text
localStorage

sessionStorage
```


# Storage Is Security-Relevant

JavaScript-accessible storage can increase token exposure if the application has an XSS vulnerability.


# Token Inventory

Record:

| Token | Location | Purpose | Lifetime |
|---|---|---|---|
| Access token | Authorization header | API access | Short |
| ID token | OIDC client | Identity assertion | Short |
| Refresh token | Cookie/storage | Token renewal | Longer |


# Do Not Treat All Tokens the Same

An:

```text
Access Token
```

is not necessarily interchangeable with:

```text
ID Token
```

or:

```text
Refresh Token
```


# Decode JWT Locally

JWT segments use Base64URL rather than ordinary Base64.

Python:

```bash
python3 - <<'PY'
import base64
import json

token = "PASTE_TOKEN_HERE"
parts = token.split(".")

for i, part in enumerate(parts[:2]):
    part += "=" * (-len(part) % 4)
    decoded = base64.urlsafe_b64decode(part)
    try:
        print(json.dumps(json.loads(decoded), indent=2))
    except Exception:
        print(decoded)
PY
```


# Do Not Paste Sensitive Tokens Into Public Websites

Production JWTs may grant direct access to:

```text
Accounts

APIs

Personal data

Administrative functions
```

Prefer local tooling for sensitive tokens.


# JWT Header

Example:

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-2026-01"
}
```


# Common Header Parameters

| Parameter | Meaning |
|---|---|
| `alg` | Cryptographic algorithm |
| `typ` | Token type |
| `kid` | Key identifier |
| `jku` | JWK Set URL |
| `jwk` | Embedded JSON Web Key |
| `x5u` | X.509 certificate URL |
| `x5c` | X.509 certificate chain |
| `crit` | Critical header parameters |


# JWT Payload

Example:

```json
{
  "iss": "https://auth.example.com",
  "sub": "123",
  "aud": "api.example.com",
  "exp": 1780000000,
  "iat": 1779996400,
  "role": "user"
}
```


# Registered Claims

Important registered claims include:

```text
iss

sub

aud

exp

nbf

iat

jti
```


# Claim Reference

| Claim | Meaning |
|---|---|
| `iss` | Issuer |
| `sub` | Subject |
| `aud` | Audience |
| `exp` | Expiration time |
| `nbf` | Not before |
| `iat` | Issued at |
| `jti` | JWT identifier |


# Custom Claims

Applications may add:

```text
role

roles

permissions

scope

tenant

tenant_id

email

username

is_admin

groups
```


# Claims Are Security-Sensitive

A token may contain:

```json
{
  "role": "admin"
}
```

but the security question is:

```text
Who created and signed this claim?

Was the signature validated?

Is the issuer trusted?

Is this claim appropriate for this application?

Does the server independently enforce authorization?
```


# JWT Testing Workflow

```text
Capture Token
     |
     v
Identify Purpose
     |
     v
Decode Header
     |
     v
Decode Payload
     |
     v
Record Algorithm
     |
     v
Record Key Identifier
     |
     v
Review Claims
     |
     v
Test Signature Validation
     |
     v
Test Claim Validation
     |
     v
Test Authorization
     |
     v
Test Lifecycle
     |
     v
Capture Evidence
```


# Establish a Baseline

Capture a legitimate authenticated request.

```http
GET /api/me HTTP/1.1
Host: target.example
Authorization: Bearer VALID_TOKEN
```


# Record Baseline

Capture:

```text
HTTP status

Response body

Token header

Token payload

Issuer

Audience

Subject

Expiration

Role

Scope

Key identifier
```


# Invalid Token Baseline

Modify one character in the signature.

Example concept:

```text
VALID_SIGNATURE
```

becomes:

```text
VALID_SIGNATURX
```


# Expected

```text
Token rejected
```


# Why This Matters

Before testing complex JWT behaviour, establish that signature verification is actually being performed.


# Signature Validation

The most fundamental JWT security property is:

```text
Modified signed content
        |
        v
Signature no longer valid
        |
        v
Token rejected
```


# Modify Payload Without Re-Signing

Original:

```json
{
  "sub": "123",
  "role": "user"
}
```


# Controlled Modification

```json
{
  "sub": "123",
  "role": "admin"
}
```


# Expected

If the signature has not been recreated using a trusted signing key:

```text
Rejected
```


# Important

A server returning:

```text
401
```

or:

```text
403
```

after payload modification supports the conclusion that the modified token was not accepted.

Do not infer the exact validation logic from the status code alone.


# The `alg` Header

The JWT header identifies the cryptographic algorithm.

Examples:

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

EdDSA
```


# Algorithm Families

Conceptually:

```text
HS*
 |
 v
Shared secret MAC

RS* / PS*
 |
 v
RSA signatures

ES*
 |
 v
Elliptic curve signatures
```


# HMAC

With HMAC:

```text
Signing Key = Verification Key
```

The same secret is shared by token issuer and verifier.


# RSA / ECDSA

With asymmetric signing:

```text
Private Key
    |
    v
Sign Token

Public Key
    |
    v
Verify Token
```


# Security Benefit

API services can verify tokens using a public key without possessing the private signing key.


# Algorithm Allowlisting

Applications should explicitly define which algorithms are acceptable.

Conceptually:

```text
Expected:
RS256

Received:
HS256

Result:
Reject
```


# Do Not Trust Token-Selected Algorithms Blindly

The token is attacker-controlled input.

The application should know:

```text
Which algorithm should be used
```

rather than trusting arbitrary algorithm choices from the token.


# Unsecured JWTs

JOSE defines an unsecured JWS representation using:

```json
{
  "alg": "none"
}
```


# Security Expectation

Applications requiring signed tokens must reject unsecured JWTs.


# Safe Validation

You can determine whether an application improperly accepts unsigned tokens using a dedicated low-privilege test account and controlled claims.

Do not use the issue to create or exercise unauthorized privileged production access.


# Algorithm Confusion

Algorithm confusion can occur when a verifier incorrectly allows a token to influence whether a key is interpreted as:

```text
Asymmetric verification key
```

or:

```text
HMAC secret
```


# Conceptual Risk

```text
Application expects RS256
        |
        v
Public RSA Key
        |
        v
Attacker changes token algorithm
        |
        v
Verifier incorrectly treats public key
as HMAC material
```


# Secure Behaviour

The server should bind:

```text
Algorithm

Key type

Issuer

Token purpose
```

to trusted server-side configuration.


# Do Not Test by Guessing Production Secrets

Algorithm-confusion testing should focus on validation behaviour and known public verification material where applicable.

Do not attempt unrelated key theft or secret harvesting.


# Weak HMAC Secrets

HMAC JWT security depends on the strength of the shared secret.


# Weak Example

Conceptually weak values include:

```text
secret

password

jwtsecret

companyname
```


# Source Review

Search configuration for JWT secrets:

```bash
rg -ni 'jwt.*secret|secret.*jwt|signing.*key|token.*secret|JWT_SECRET' .
```


# Environment Files

```bash
rg -ni 'JWT|TOKEN|SIGNING|SECRET' -g '.env*' -g '*.yaml' -g '*.yml' -g '*.json' -g '*.toml' .
```


# Important

Do not expose secrets discovered during source review in screenshots or public reports.


# Secret Rotation

If a signing secret is exposed:

```text
Changing application code
```

is not enough.

The secret itself must be rotated.


# `kid` - Key Identifier

Example:

```json
{
  "alg": "RS256",
  "kid": "key-2026-01"
}
```


# Purpose

`kid` helps the verifier select the correct key from a key set.


# Security Question

How does the server resolve:

```text
kid
```

to:

```text
verification key
```


# Dangerous Design

Avoid treating `kid` as an unrestricted:

```text
File path

Database query fragment

Command argument

URL
```


# Safe Model

```text
kid
 |
 v
Lookup in trusted key set
 |
 v
Known key
```


# Unknown `kid`

Test a controlled unknown identifier:

```json
{
  "alg": "RS256",
  "kid": "does-not-exist"
}
```


# Expected

```text
Token rejected safely
```

without:

```text
Stack trace

File path disclosure

Database error

Internal key material
```


# `jku` - JWK Set URL

Example:

```json
{
  "alg": "RS256",
  "jku": "https://auth.example.com/.well-known/jwks.json",
  "kid": "key1"
}
```


# Risk

If the application blindly trusts a token-controlled `jku`, the token may influence where verification keys are obtained.


# Secure Design

Trust:

```text
Configured issuer

Configured JWKS endpoint

Approved key set
```

not arbitrary token-provided locations.


# SSRF Consideration

Remote key retrieval can also create SSRF risk if arbitrary URLs are accepted.

JWT key handling and SSRF should therefore be reviewed together where remote key retrieval exists.


# `jwk` - Embedded Key

A JWT header may contain an embedded JSON Web Key.

Example concept:

```json
{
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "kid": "key1"
  }
}
```


# Security Expectation

The application should not automatically trust an attacker-supplied embedded verification key unless the protocol and trust model explicitly require and validate it.


# `x5u`

`x5u` can reference an X.509 certificate or certificate chain location depending on the JOSE design.


# Security Question

Can an untrusted token control where the application retrieves certificate material?


# `x5c`

`x5c` carries certificate chain information directly in the JOSE header.

Certificate presence does not itself establish trust.

The verifier must validate the chain and expected trust relationship appropriately.


# JWKS

A JSON Web Key Set contains public verification keys.

Common endpoint:

```text
/.well-known/jwks.json
```


# Example

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


# Public Keys Are Usually Not Secrets

Public verification keys are intended to be distributable.

Do not report:

```text
Public JWKS accessible
```

as a vulnerability by itself.


# JWKS Review

Check:

```text
Trusted origin

HTTPS

Key identifiers

Algorithm consistency

Key rotation

Caching

Unknown-key behaviour
```


# Key Rotation

Systems should support moving from:

```text
Old Key
```

to:

```text
New Key
```

without unsafe trust expansion.


# Rotation Model

```text
Key A signs existing tokens

Key B introduced

New tokens signed with Key B

Key A retained during overlap

Key A eventually retired
```


# Retired Keys

Determine whether tokens signed with a retired key remain accepted beyond the intended transition period.


# Issuer Validation

`iss` identifies the token issuer.

Example:

```json
{
  "iss": "https://auth.example.com"
}
```


# Security Expectation

The verifier should compare the issuer against a trusted expected value.


# Why Issuer Matters

Without correct issuer validation, an application may accept tokens from another identity system that uses compatible keys or token structure.


# Audience Validation

`aud` identifies the intended recipient.

Example:

```json
{
  "aud": "payments-api"
}
```


# Security Expectation

A service should reject a token intended only for:

```text
different-api
```


# Cross-Service Token Confusion

Architecture:

```text
Service A

Service B
```

If both trust the same issuer but fail to validate audience:

```text
Token for Service A
        |
        v
Presented to Service B
        |
        v
Incorrectly accepted
```


# Subject

`sub` normally identifies the principal.

Example:

```json
{
  "sub": "user-123"
}
```


# Review

Determine whether the application uses:

```text
sub

email

username

custom user ID
```

as its identity key.


# Avoid Mutable Identity Keys

Using mutable claims such as email addresses as permanent internal identity keys can create lifecycle complexity.

Prefer stable subject identifiers where appropriate.


# Expiration

Example:

```json
{
  "exp": 1780000000
}
```


# Expected

After expiration:

```text
Token rejected
```


# Test Expiration

Use a token from your own test account and verify behaviour after the configured expiration period.


# Clock Skew

Small clock-skew allowances may be legitimate.

Do not report a token being accepted a few seconds beyond the nominal timestamp without understanding configured tolerance.


# `nbf`

`nbf` means:

```text
Not valid before this time
```


# Expected

A token presented significantly before its valid time should be rejected.


# `iat`

`iat` records issuance time.

It can support:

```text
Auditing

Token-age rules

Session policy
```

but simply including `iat` does not enforce token lifetime.


# `jti`

`jti` provides a token identifier.

It may support:

```text
Replay tracking

Revocation

Audit correlation
```


# Important

A `jti` claim does not automatically prevent replay.

The server must actually use it in a relevant control.


# Token Lifetime

Record:

```text
iat

exp
```


# Calculate Lifetime

```python
lifetime = exp - iat
```


# Python Example

```bash
python3 - <<'PY'
iat = 1779996400
exp = 1780000000

seconds = exp - iat
print("seconds:", seconds)
print("minutes:", seconds / 60)
print("hours:", seconds / 3600)
PY
```


# Interpret Lifetime Contextually

A suitable lifetime depends on:

```text
Token purpose

Application sensitivity

Revocation capability

Refresh-token design

User experience

Risk model
```


# Long-Lived Access Tokens

Long-lived bearer access tokens increase the window in which a stolen token can be reused.


# Refresh Tokens

A common model is:

```text
Short-Lived Access Token
          |
          v
API Requests

Longer-Lived Refresh Token
          |
          v
Token Endpoint
          |
          v
New Access Token
```


# Refresh Token Security

Review:

```text
Storage

Lifetime

Rotation

Revocation

Replay detection

Client binding

Session termination
```


# Refresh Token Rotation

Conceptually:

```text
Refresh Token A
      |
      v
Used
      |
      +--> Access Token
      |
      +--> Refresh Token B

Refresh Token A
      |
      v
Invalidated
```


# Replay Detection

If an already-rotated refresh token is reused, the authorization server may treat this as evidence of token theft and revoke the token family depending on the architecture.


# Logout

JWTs create special logout considerations.


# Stateless Access Token

If the API validates only:

```text
Signature

Claims

Expiration
```

then deleting the token from the browser does not necessarily invalidate a previously copied token.


# Test Model

```text
Login
  |
  v
Capture Token
  |
  v
Logout
  |
  v
Replay Token
```


# Interpret Carefully

A token remaining valid after logout is not automatically a vulnerability.

Determine the intended architecture:

```text
Short-lived stateless token?

Server-side revocation?

Refresh token revoked?

High-risk application requiring immediate logout?
```


# Revocation Strategies

Possible designs include:

```text
Short access-token lifetime

Refresh-token revocation

Token denylist

Session version

Key rotation

Central introspection
```


# Password Change

Test whether existing JWT-based sessions behave according to the application's intended policy after:

```text
Password change

Password reset

Account disablement

MFA reset
```


# Account Disablement

High-risk systems may need disabled accounts to lose access before existing access tokens naturally expire.


# Session Version

Some systems include or verify server-side session state such as:

```text
session_version

token_version
```

to invalidate previously issued tokens.


# Authorization Claims

Example:

```json
{
  "sub": "123",
  "role": "user"
}
```


# Critical Question

Does the server correctly validate:

```text
Token integrity
```

and then correctly enforce:

```text
Authorization
```


# Valid JWT Does Not Mean Authorized

A perfectly valid token can still be used incorrectly by the application.


# Example

```text
Valid User A Token
       |
       v
/api/users/200
       |
       v
User B Object
```

This is an authorization problem even though the JWT is valid.


# Role Claims

Applications may use:

```text
role

roles

groups

permissions

scope
```


# Review

Determine:

```text
Who issues the claim?

Can the user influence it?

Which service trusts it?

Is it refreshed after role changes?

Is server-side authorization still applied?
```


# Stale Role Claims

Example:

```text
User receives admin token

Administrator role later removed

Old token remains valid
```

Whether this is acceptable depends on:

```text
Token lifetime

Risk

Revocation design
```


# Tenant Claims

Example:

```json
{
  "sub": "123",
  "tenant_id": "10"
}
```


# Security Question

Can this token access:

```text
Tenant 11
```

through an object identifier or request parameter?


# JWT Does Not Replace Tenant Authorization

Even when:

```text
tenant_id = 10
```

is cryptographically protected, resource authorization must still verify tenant boundaries.


# Scope Claims

OAuth access tokens commonly contain:

```text
scope
```

or equivalent permissions.


# Example

```json
{
  "scope": "profile:read orders:read"
}
```


# Test

An endpoint requiring:

```text
orders:write
```

should not accept a token containing only:

```text
orders:read
```


# Audience vs Scope

These solve different problems.

```text
aud
 |
 v
Which service is this token intended for?

scope
 |
 v
What operations may this token perform?
```


# Token Type Confusion

Systems may issue:

```text
Access token

ID token

Refresh token
```


# Security Question

Does an API incorrectly accept an:

```text
ID token
```

as an:

```text
Access token
```


# Token Purpose

Tokens should be distinguishable through trusted validation rules such as:

```text
Issuer

Audience

Token type

Claims

Protocol context
```


# OIDC ID Tokens

An ID token tells an OIDC client about an authenticated user.

It is not automatically an API authorization credential.


# Cross-Application Token Reuse

Where multiple applications use the same identity provider:

```text
Application A

Application B
```

test whether each application validates:

```text
Audience

Issuer

Token purpose
```


# Burp Suite

Burp Suite is useful for JWT testing through:

```text
Proxy

Repeater

Comparer

Decoder

Logger

JWT-focused extensions
```


# Repeater Workflow

```text
Capture Authenticated Request
        |
        v
Send to Repeater
        |
        v
Baseline Valid Token
        |
        v
Modify One JWT Property
        |
        v
Replay
        |
        v
Compare
```


# Change One Variable

For defensible results, modify one dimension at a time.

Examples:

```text
Signature

exp

aud

iss

role

kid
```


# Burp Decoder

Decoder can help inspect:

```text
Base64

Base64URL

URL encoding
```

but JWT-specific tooling is usually more convenient for structured tokens.


# JWT Editor

The Burp Suite JWT Editor extension can assist with:

```text
JWT inspection

Key management

Signing controlled test tokens

JOSE header testing
```


# Important

Tool output is not the finding.

The finding is the application's demonstrated validation failure.


# Capture Both Tokens

Save:

```text
Original token structure

Modified token structure
```

but redact sensitive values from reports.


# JWT Testing Matrix

Create a table:

| Test | Expected |
|---|---|
| Valid token | Accepted |
| Corrupted signature | Rejected |
| Modified payload | Rejected |
| Unsupported algorithm | Rejected |
| Expired token | Rejected |
| Wrong issuer | Rejected |
| Wrong audience | Rejected |
| Unknown key | Rejected |


# Claim Validation Matrix

| Claim | Test |
|---|---|
| `iss` | Wrong trusted issuer |
| `aud` | Token for another service |
| `exp` | Expired token |
| `nbf` | Token before valid time |
| `sub` | Identity mapping |
| `scope` | Missing required scope |
| `tenant` | Cross-tenant access |
| `role` | Role enforcement |


# Error Handling

Invalid JWTs should fail safely.


# Avoid Detailed Errors

Production APIs generally should not expose unnecessary details such as:

```text
Expected signing key path

Internal key ID

Library stack trace

Certificate filesystem path

Database query

Private key location
```


# Useful Client Response

Example:

```json
{
  "error": "invalid_token"
}
```


# Logging

Detailed JWT validation errors may be useful in trusted server logs.

Avoid logging full bearer tokens.


# Log Redaction

Instead of:

```text
Authorization: Bearer eyJ...FULL_TOKEN
```

prefer:

```text
Authorization: Bearer <redacted>
```


# JWT in URL

Avoid placing bearer JWTs in:

```text
Query strings
```

such as:

```text
/api/data?token=JWT
```


# Why

URLs can leak through:

```text
Browser history

Server logs

Proxy logs

Analytics

Referer headers
```


# JWT in Cookies

If JWTs are stored in cookies, review:

```text
Secure

HttpOnly

SameSite

Domain

Path

Lifetime
```


# JWT Cookie Example

```http
Set-Cookie: access_token=JWT; Secure; HttpOnly; SameSite=Lax
```


# CSRF

Cookie-based JWT authentication may still require CSRF protection depending on:

```text
SameSite behaviour

Request method

Application architecture

Cross-site flows
```


# Bearer Header Model

Tokens explicitly added to:

```http
Authorization: Bearer ...
```

by application JavaScript have different CSRF characteristics from automatically attached cookies.


# XSS

XSS may expose JavaScript-accessible tokens stored in:

```text
localStorage

sessionStorage

JavaScript variables
```


# HttpOnly Cookies

`HttpOnly` can prevent ordinary JavaScript from directly reading the cookie value.

It does not prevent XSS from performing actions in the victim's browser.


# JWT Size

JWTs may become large when carrying:

```text
Many roles

Groups

Permissions

Profile data
```


# Avoid Sensitive Data

Remember:

```text
Signed != Encrypted
```


# Do Not Store

Avoid placing unnecessary sensitive data in readable JWT payloads.


# PII

If personal information is included, consider:

```text
Privacy

Logging

Browser storage

Telemetry

Token exposure

Retention
```


# Source Code Review

JWT source review should trace:

```text
Token Issuance
     |
     v
Signing Configuration
     |
     v
Token Transport
     |
     v
Verification
     |
     v
Claim Validation
     |
     v
Authorization
```


# Generic Searches

```bash
rg -ni 'jwt|jsonwebtoken|jose|jwks|bearer|access.?token|refresh.?token|id.?token' .
```


# Signing Search

```bash
rg -ni 'sign\(|signing|private.?key|JWT_SECRET|jwt.?secret|algorithm' .
```


# Verification Search

```bash
rg -ni 'verify\(|decode\(|validate\(|issuer|audience|jwks|algorithms' .
```


# Claim Search

```bash
rg -ni '\biss\b|\baud\b|\bexp\b|\bnbf\b|\biat\b|\bjti\b|\bsub\b|scope|roles?|permissions?' .
```


# Key Search

```bash
rg -ni 'kid|jku|jwk|jwks|x5u|x5c|public.?key|private.?key' .
```


# Node.js

Common libraries include:

```text
jsonwebtoken

jose
```


# Search

```bash
rg -ni 'jsonwebtoken|from .jose.|jwt\.sign|jwt\.verify|SignJWT|jwtVerify' -g '*.js' -g '*.ts' .
```


# Node.js Review

Look for explicit configuration of:

```text
Algorithms

Issuer

Audience

Key source
```


# Python

Common libraries include:

```text
PyJWT

python-jose

Authlib
```


# Search

```bash
rg -ni 'jwt\.encode|jwt\.decode|PyJWT|python-jose|Authlib|JWT' -g '*.py' .
```


# Python Review

Check whether decode/verification explicitly validates:

```text
Signature

Allowed algorithm

Issuer

Audience

Expiration
```


# Java

Common ecosystems include:

```text
Nimbus JOSE + JWT

JJWT

Spring Security
```


# Search

```bash
rg -ni 'Nimbus|JJWT|JwtDecoder|JwtEncoder|SignedJWT|JWTClaimsSet|oauth2ResourceServer' -g '*.java' .
```


# .NET

Search:

```bash
rg -ni 'JwtBearer|JwtSecurityToken|TokenValidationParameters|ValidateIssuer|ValidateAudience|ValidateLifetime|IssuerSigningKey' -g '*.cs' .
```


# Important .NET Settings

Review configuration around:

```text
ValidateIssuer

ValidateAudience

ValidateLifetime

ValidateIssuerSigningKey
```


# PHP

Common libraries include:

```text
firebase/php-jwt
```

Search:

```bash
rg -ni 'JWT::encode|JWT::decode|firebase.*jwt|Key\(' -g '*.php' .
```


# Go

Search:

```bash
rg -ni 'jwt|ParseWithClaims|Parse|SigningMethod|ValidMethods|RegisteredClaims' -g '*.go' .
```


# Ruby

Search:

```bash
rg -ni 'JWT\.encode|JWT\.decode|ruby-jwt|jwt' -g '*.rb' .
```


# Configuration Files

JWT trust may be configured outside application code.

Search:

```bash
rg -ni 'issuer|audience|jwks|jwt|signing|token' -g '*.yaml' -g '*.yml' -g '*.json' -g '*.toml' -g '*.conf' .
```


# Environment Variables

Common names:

```text
JWT_SECRET

JWT_ISSUER

JWT_AUDIENCE

JWT_PUBLIC_KEY

JWT_PRIVATE_KEY

JWKS_URL
```


# Search Carefully

```bash
rg -ni 'JWT_|JWKS|SIGNING_KEY|TOKEN_SECRET' .
```


# Secret Handling

Do not commit:

```text
Private signing keys

HMAC secrets

Refresh tokens
```

to source repositories.


# Public Key Handling

Public verification keys can usually be distributed.

The important control is:

```text
Which public keys are trusted?
```


# Key Trust Boundary

Secure model:

```text
Configured Trusted Issuer
        |
        v
Configured Trusted JWKS
        |
        v
Known Key ID
        |
        v
Verification
```


# Dangerous Model

```text
Token
  |
  v
Attacker-Controlled Key Location
  |
  v
Fetch Key
  |
  v
Trust Key
```


# Library Defaults

Do not assume a JWT library is insecure because a dangerous historical configuration existed in an old version.

Review:

```text
Current library

Current version

Current configuration

Actual application behaviour
```


# Dependency Review

Examples:

```bash
rg -ni 'jsonwebtoken|pyjwt|python-jose|nimbus|jjwt|firebase/php-jwt|jwt-go|golang-jwt' .
```


# Lockfiles

Review:

```text
package-lock.json

yarn.lock

pnpm-lock.yaml

requirements.txt

poetry.lock

pom.xml

build.gradle

packages.lock.json

composer.lock

go.mod

Gemfile.lock
```


# Avoid Version-Only Findings

An old dependency version is not automatically evidence that the application is exploitable.

Determine:

```text
Affected version?

Vulnerable code path?

Relevant configuration?

Reachable behaviour?
```


# Microservices

JWTs are often used across multiple services.

Architecture:

```text
Identity Provider
       |
       v
     JWT
       |
       +--> API A
       |
       +--> API B
       |
       +--> API C
```


# Review Each Service

Each verifier should correctly validate:

```text
Signature

Issuer

Audience

Lifetime

Token purpose

Required scope
```


# Shared Trust

Broad trust relationships increase the importance of:

```text
Audience

Scope

Issuer

Key separation
```


# Internal Services

Do not assume internal APIs can skip JWT validation simply because they are:

```text
Internal
```


# Gateway Validation

Architecture:

```text
Client
  |
  v
API Gateway
  |
  v
Backend Service
```


# Question

Does the backend:

```text
Trust gateway-injected identity
```

and if so:

```text
Can clients reach the backend directly?

Can identity headers be spoofed?

Is the network trust boundary enforced?
```


# JWT to Header Translation

A gateway may validate a JWT and forward:

```http
X-User-ID: 123
X-Role: user
```


# Security Requirement

Backends must distinguish:

```text
Trusted gateway headers
```

from:

```text
Client-supplied headers
```


# Remove Client-Supplied Identity Headers

Gateways should overwrite or remove security-sensitive identity headers from untrusted incoming requests.


# WebSockets

JWTs may authenticate WebSocket connections.


# Review

```text
How token is supplied

Whether token expires during connection

Reconnect behaviour

Per-message authorization

Tenant authorization
```


# Long-Lived Connections

A token may expire while a WebSocket remains open.

The appropriate behaviour depends on the application's session model.


# Mobile Applications

Mobile clients often use:

```text
Access tokens

Refresh tokens
```


# Review

```text
Secure device storage

Token lifetime

Refresh rotation

Logout

Certificate validation

API authorization
```


# Do Not Put Signing Secrets in Mobile Apps

A shared HMAC signing secret embedded in an untrusted client cannot remain secret.


# Browser Applications

Public browser clients cannot securely store application-wide signing secrets either.


# Signing Should Occur Server-Side

Typical secure model:

```text
Browser
   |
   v
Authentication Server
   |
   v
Signed Token
```


# Error Analysis

Useful invalid-token cases:

```text
Malformed token

Wrong number of segments

Invalid Base64URL

Invalid JSON

Unknown algorithm

Invalid signature

Expired token

Wrong audience

Wrong issuer

Unknown kid
```


# Expected

All should:

```text
Fail safely
```

without exposing internal details.


# Malformed Token

Example:

```text
not-a-jwt
```


# Expected

```text
Rejected
```


# Missing Signature Segment

A malformed token should not trigger:

```text
500 Internal Server Error
```

with a stack trace.


# Denial-of-Service Considerations

Malformed token testing should remain low-volume.

Do not send enormous headers, deeply nested structures or expensive cryptographic inputs unless explicitly scoped for resilience testing.


# Evidence - Signature Validation Failure

Capture:

```text
Valid token accepted

Payload modified

Signature unchanged/invalid

Modified token still accepted
```


# Evidence - Audience Failure

Capture:

```text
Token issued for Service A

Token presented to Service B

Service B accepts token

Audience values documented
```


# Evidence - Expiration Failure

Capture:

```text
Token exp value

Current time

Expired token request

Successful authenticated response
```


# Evidence - Key Trust Failure

Capture:

```text
Original trusted key behaviour

Controlled untrusted key reference

Modified token

Server acceptance
```

without exposing sensitive private keys in the report.


# Evidence - Authorization Claim Failure

Capture:

```text
Account identity

Original claim

Modified/alternate valid claim context

Protected endpoint

Observed authorization decision
```


# Reporting Missing Signature Validation

> The API accepts JWTs whose signed payload has been modified without a valid corresponding signature. A token issued to a dedicated test account was modified and replayed without possession of the trusted signing key, and the API continued to treat the request as authenticated. The application must cryptographically verify the token before processing any identity or authorization claims.


# Reporting Algorithm Validation Weakness

> The application does not restrict JWT verification to the algorithm expected by the authentication architecture. The verifier accepts an alternative token algorithm rather than binding the algorithm and key type to trusted server-side configuration. JWT verification should use an explicit algorithm allowlist and trusted key configuration.


# Reporting Missing Audience Validation

> The API accepts a valid JWT issued for a different service because the token audience is not validated against the current API. This allows tokens intended for one relying service to be reused against another service sharing the same trust environment.


# Reporting Missing Issuer Validation

> The application verifies the token signature but does not enforce the expected issuer. Tokens should be accepted only from the identity provider explicitly trusted by the application.


# Reporting Expired Token Acceptance

> The API continues to accept access tokens after their `exp` claim has passed. A token issued to a dedicated test account remained usable after expiration and successfully accessed an authenticated endpoint. Token lifetime validation should be enforced during every authenticated request.


# Reporting Untrusted JWKS Source

> JWT verification accepts key material from a location controlled through an untrusted token header rather than restricting verification to the application's configured trusted key set. The verification key source must be derived from trusted issuer configuration and must not be selected from arbitrary token-controlled URLs.


# Reporting Token Exposure

> The application transmits bearer JWTs in URL query parameters. Because URLs may be retained in browser history, server logs, proxy logs and analytics systems, this increases the likelihood of token disclosure. Bearer tokens should be transmitted using an appropriate authorization header or protected cookie according to the application's authentication architecture.


# Reporting Stale Privilege Claims

> Authorization privileges are embedded in long-lived JWTs and remain effective after the corresponding server-side role is removed. The application should reduce the lifetime of privilege-bearing tokens or introduce an appropriate revocation or authorization-state mechanism for security-sensitive privilege changes.


# Avoid Overclaiming

Do not report:

```text
JWT payload can be decoded
```

as a vulnerability.

That is expected for ordinary signed JWTs.


# Do Not Report

```text
Public key is publicly accessible
```

when the key is intentionally published for verification.


# Do Not Report

```text
Token uses Base64
```

as weak encryption.

Base64URL is encoding, not encryption.


# Do Not Report

```text
JWT uses RS256
```

as inherently insecure.

Security depends on implementation, key management and validation.


# Severity Considerations

Consider:

```text
Authentication bypass

Ability to forge arbitrary identity

Ability to forge administrative role

Cross-tenant access

Token lifetime

Scope

Audience

Key exposure

User interaction

Revocation

Affected services

Data sensitivity
```


# High-Impact Conditions

Potentially severe issues include:

```text
Unsigned tokens accepted

Signature not verified

Attacker-controlled keys trusted

Signing secret exposed

Cross-service privileged token reuse

Arbitrary identity claims accepted
```


# Lower-Impact Conditions

Examples that may have lower impact depending on context:

```text
Minor token information disclosure

Overly verbose validation errors

Longer-than-desired token lifetime

Non-sensitive claims exposed
```


# Root Causes

Common root causes include:

```text
Signature verification disabled

Decode used instead of verify

Algorithm not allowlisted

Issuer not validated

Audience not validated

Expiration not validated

Untrusted key source

Weak HMAC secret

Private key exposure

Token purpose confusion

Authorization based solely on inappropriate claims

Excessive token lifetime
```


# Remediation - Use Mature Libraries

Use actively maintained JOSE/JWT libraries rather than implementing token cryptography manually.


# Explicit Validation

Configure:

```text
Expected algorithm

Trusted issuer

Expected audience

Trusted key source

Lifetime validation
```


# Reject Unexpected Algorithms

Example policy:

```text
Application expects RS256
        |
        v
Anything Else
        |
        v
Reject
```


# Trusted Key Selection

Resolve keys from:

```text
Configured trusted JWKS
```

or:

```text
Locally configured trusted keys
```

rather than arbitrary token-controlled locations.


# Strong HMAC Secrets

If HMAC is appropriate:

```text
Use cryptographically random secrets

Store them securely

Rotate them when exposed
```


# Asymmetric Keys

Protect private signing keys using appropriate:

```text
Secret management

File permissions

HSM/KMS where justified

Rotation procedures
```


# Claim Validation

Validate relevant:

```text
iss

aud

exp

nbf

Token purpose

Required scope
```


# Authorization

Do not assume:

```text
Valid JWT
```

means:

```text
Allowed operation
```


# Apply Resource Authorization

```text
Valid Token
    |
    v
Identity
    |
    v
Role / Scope
    |
    v
Object Authorization
    |
    v
Action
```


# Token Lifetime

Prefer shorter access-token lifetimes where practical, especially when tokens cannot be immediately revoked.


# Refresh Tokens

Protect refresh tokens more strongly because they can create new access tokens.


# Rotation

Implement refresh-token rotation or another suitable replay-resistant design where appropriate to the threat model.


# Secrets in Claims

Do not place unnecessary:

```text
Secrets

Passwords

Private keys

Sensitive internal data
```

inside ordinary JWT payloads.


# Transport

Use:

```text
HTTPS
```

for bearer tokens.


# Logging

Redact tokens from:

```text
Application logs

Reverse proxy logs

APM systems

Analytics

Error reports
```


# Retesting JWT Validation

Start with the original finding.


# Signature Retest

```text
Valid Token
    |
    v
Accepted

Modified Payload
    |
    v
Invalid Signature
    |
    v
Rejected
```


# Algorithm Retest

Present an unexpected algorithm.

Expected:

```text
Rejected
```


# Issuer Retest

Present a token from an untrusted issuer.

Expected:

```text
Rejected
```


# Audience Retest

Present a token intended for another service.

Expected:

```text
Rejected
```


# Expiration Retest

Present an expired test token.

Expected:

```text
Rejected
```


# Unknown Key Retest

Use an unknown `kid`.

Expected:

```text
Rejected safely
```


# JWKS Retest

Verify key retrieval is restricted to the configured trusted source.


# Authorization Retest

Verify a valid low-privilege token cannot access:

```text
Administrative endpoint

Other user's object

Other tenant

Missing-scope function
```


# Lifecycle Retest

Review:

```text
Logout

Password change

Password reset

Account disablement

Role change

MFA reset
```


# Equivalent Verifiers

If one JWT validation issue is found, identify every component that verifies the same token.


# Search Architecture

```text
API Gateway

Backend APIs

Microservices

WebSocket service

Admin API

Legacy API

Mobile API
```


# JWT Checklist

## Discovery

- [ ] JWT locations identified
- [ ] Access tokens identified
- [ ] ID tokens identified
- [ ] Refresh tokens identified
- [ ] Cookie-based tokens identified
- [ ] Authorization-header tokens identified
- [ ] WebSocket tokens identified

## Structure

- [ ] Header decoded
- [ ] Payload decoded
- [ ] Algorithm recorded
- [ ] `kid` recorded
- [ ] Issuer recorded
- [ ] Audience recorded
- [ ] Subject recorded
- [ ] Expiration recorded
- [ ] Scope/roles recorded
- [ ] Tenant claims recorded

## Signature

- [ ] Corrupted signature tested
- [ ] Modified payload tested
- [ ] Unsupported algorithm handling reviewed
- [ ] Unsecured token handling reviewed where relevant
- [ ] Algorithm allowlist reviewed
- [ ] Key type binding reviewed

## Keys

- [ ] Key source identified
- [ ] JWKS reviewed
- [ ] `kid` handling reviewed
- [ ] Unknown `kid` tested
- [ ] `jku` reviewed where present
- [ ] `jwk` reviewed where present
- [ ] `x5u` reviewed where present
- [ ] `x5c` trust reviewed where present
- [ ] Key rotation reviewed
- [ ] HMAC secret storage reviewed where applicable
- [ ] Private key storage reviewed where applicable

## Claims

- [ ] `iss` validation reviewed
- [ ] `aud` validation reviewed
- [ ] `exp` validation reviewed
- [ ] `nbf` validation reviewed
- [ ] `sub` identity mapping reviewed
- [ ] `scope` enforcement reviewed
- [ ] Role claims reviewed
- [ ] Tenant claims reviewed
- [ ] Token purpose reviewed

## Authorization

- [ ] Valid low-privilege token tested
- [ ] Horizontal authorization reviewed
- [ ] Vertical authorization reviewed
- [ ] Tenant isolation reviewed
- [ ] Scope enforcement reviewed
- [ ] Stale role behaviour reviewed

## Lifecycle

- [ ] Token lifetime measured
- [ ] Logout behaviour reviewed
- [ ] Password-change behaviour reviewed
- [ ] Password-reset behaviour reviewed
- [ ] Account-disable behaviour reviewed
- [ ] Role-change behaviour reviewed
- [ ] Revocation capability reviewed
- [ ] Refresh-token rotation reviewed

## Storage

- [ ] Cookies reviewed
- [ ] localStorage reviewed
- [ ] sessionStorage reviewed
- [ ] URL exposure reviewed
- [ ] Logging exposure reviewed
- [ ] Third-party leakage reviewed

## Source Review

- [ ] JWT libraries identified
- [ ] Signing code identified
- [ ] Verification code identified
- [ ] Allowed algorithms reviewed
- [ ] Issuer validation reviewed
- [ ] Audience validation reviewed
- [ ] Lifetime validation reviewed
- [ ] Key loading reviewed
- [ ] Secrets searched
- [ ] Authorization claims traced

## Evidence

- [ ] Valid baseline captured
- [ ] Modified token captured
- [ ] Exact changed field recorded
- [ ] Response captured
- [ ] Authentication state confirmed
- [ ] Authorization state confirmed
- [ ] Token values redacted
- [ ] Timestamp recorded

## Retest

- [ ] Original validation issue fixed
- [ ] Modified tokens rejected
- [ ] Wrong issuer rejected
- [ ] Wrong audience rejected
- [ ] Expired tokens rejected
- [ ] Unexpected algorithms rejected
- [ ] Untrusted keys rejected
- [ ] Legitimate tokens still work
- [ ] Equivalent verifiers reviewed


# Algorithm Matrix

| Family | Key Model | Example |
|---|---|---|
| HMAC | Shared secret | HS256 |
| RSA PKCS#1 v1.5 | Private/public key | RS256 |
| RSA-PSS | Private/public key | PS256 |
| ECDSA | Private/public key | ES256 |
| EdDSA | Private/public key | EdDSA |


# Claim Matrix

| Claim | Security Question |
|---|---|
| `iss` | Did a trusted issuer create this token? |
| `sub` | Which identity does this token represent? |
| `aud` | Is this token intended for this service? |
| `exp` | Is the token still valid? |
| `nbf` | Is the token valid yet? |
| `iat` | When was it issued? |
| `jti` | Is there a unique token identifier? |
| `scope` | Which operations are permitted? |


# Header Matrix

| Header | Review |
|---|---|
| `alg` | Explicitly allowed algorithm |
| `kid` | Trusted key lookup |
| `jku` | Trusted URL only |
| `jwk` | Do not blindly trust embedded key |
| `x5u` | Trusted certificate location |
| `x5c` | Validate certificate trust |
| `crit` | Correct critical-header processing |


# Token Type Matrix

| Token | Primary Purpose |
|---|---|
| Access token | API authorization |
| ID token | OIDC authentication information for client |
| Refresh token | Obtain new tokens |
| Session token | Maintain application session |


# Validation Matrix

| Test | Secure Result |
|---|---|
| Valid token | Accept |
| Corrupted signature | Reject |
| Modified payload | Reject |
| Unexpected algorithm | Reject |
| Wrong issuer | Reject |
| Wrong audience | Reject |
| Expired token | Reject |
| Too-early token | Reject |
| Unknown trusted key | Reject |


# Key Trust Matrix

| Source | Trust Decision |
|---|---|
| Configured local public key | Trusted if correctly provisioned |
| Configured issuer JWKS | Trusted according to issuer policy |
| Arbitrary token `jku` | Do not trust automatically |
| Arbitrary embedded `jwk` | Do not trust automatically |
| Client-supplied key | Untrusted |


# Authorization Matrix

| Token | Resource | Expected |
|---|---|---|
| User A | User A object | Allow |
| User A | User B object | Deny |
| Normal user | Admin function | Deny |
| Tenant A | Tenant B object | Deny |
| Read scope | Write endpoint | Deny |


# Lifecycle Matrix

| Event | Question |
|---|---|
| Login | How are tokens issued? |
| Refresh | Is rotation/replay handled? |
| Logout | What becomes invalid? |
| Password change | Are sessions affected? |
| Password reset | Are sessions affected? |
| Role change | How quickly do claims update? |
| Account disable | How quickly is access removed? |
| Key rotation | How are old tokens handled? |


# False Positive Matrix

| Observation | Meaning |
|---|---|
| JWT payload readable | Normal for signed JWT |
| Public key accessible | Usually expected |
| `kid` present | Normal key-selection mechanism |
| `jku` present | Requires trust validation, not automatically vulnerable |
| Long token | Not automatically insecure |
| RS256 used | Not automatically secure or insecure |
| Token valid after logout | Depends on lifecycle design |
| Role in JWT | Not automatically vulnerable |


# Evidence Matrix

| Observation | Supported Conclusion |
|---|---|
| Modified payload accepted without valid signature | Signature validation failure |
| Unexpected algorithm accepted | Algorithm validation weakness |
| Wrong-audience token accepted | Audience validation failure |
| Untrusted issuer token accepted | Issuer validation failure |
| Expired token accepted | Lifetime validation failure |
| Arbitrary attacker key trusted | Key trust failure |
| Read-only token performs write | Scope/authorization failure |


# Remediation Matrix

| Weakness | Primary Control |
|---|---|
| Signature not verified | Mandatory cryptographic verification |
| Algorithm confusion | Explicit algorithm/key binding |
| Weak HMAC secret | Strong random secret and rotation |
| Wrong issuer accepted | Strict issuer validation |
| Wrong audience accepted | Strict audience validation |
| Expired tokens accepted | Lifetime validation |
| Untrusted JWKS | Configured trusted key source |
| Stale privilege token | Shorter lifetime/revocation strategy |
| Token in URL | Safer token transport |
| Excessive claims | Minimize token contents |


# JWT Validation Model

```text
                   JWT
                    |
                    v
              PARSE STRUCTURE
                    |
                    v
            EXPECTED ALGORITHM?
                    |
             +------+------+
             |             |
            NO            YES
             |             |
             v             v
           REJECT      TRUSTED KEY?
                           |
                    +------+------+
                    |             |
                   NO            YES
                    |             |
                    v             v
                  REJECT      VERIFY SIGNATURE
                                  |
                           +------+------+
                           |             |
                          FAIL          PASS
                           |             |
                           v             v
                         REJECT      VALIDATE CLAIMS
                                         |
                                  +------+------+
                                  |             |
                                 FAIL          PASS
                                  |             |
                                  v             v
                                REJECT      AUTHORIZATION
```


# Key Selection Model

```text
                  TOKEN
                    |
                    v
                   kid
                    |
                    v
             TRUSTED KEY SET
                    |
           +--------+--------+
           |                 |
        NOT FOUND           FOUND
           |                 |
           v                 v
         REJECT          VERIFY TOKEN
```


# Unsafe Key Trust Model

```text
                UNTRUSTED TOKEN
                      |
                      v
                  jku / jwk
                      |
                      v
               ATTACKER KEY
                      |
                      v
               SERVER TRUSTS KEY
                      |
                      v
                TOKEN ACCEPTED
```

The key security requirement is:

```text
Token may identify a key.

Token must not establish trust in that key.
```


# Access Token Lifecycle

```text
                 AUTHENTICATION
                       |
                       v
                  ACCESS TOKEN
                       |
                       v
                 API REQUESTS
                       |
                       v
                    EXPIRES
                       |
                       v
                  REFRESH FLOW
                       |
                       v
               NEW ACCESS TOKEN
```


# Refresh Rotation Model

```text
              REFRESH TOKEN A
                     |
                     v
                   USED
                     |
          +----------+----------+
          |                     |
          v                     v
   ACCESS TOKEN B        REFRESH TOKEN B
                                |
                                v
                        TOKEN A INVALID
```


# Authorization Model

```text
                 VALID JWT
                    |
                    v
                 IDENTITY
                    |
                    v
              ROLE / SCOPE
                    |
                    v
             TENANT CONTEXT
                    |
                    v
              OBJECT ACCESS
                    |
                    v
                DECISION
```


# Source Review Model

```text
              TOKEN ISSUANCE
                    |
                    v
              SIGNING KEY
                    |
                    v
             TOKEN TRANSPORT
                    |
                    v
                VERIFIER
                    |
                    v
          ALGORITHM VALIDATION
                    |
                    v
              KEY SELECTION
                    |
                    v
          SIGNATURE VALIDATION
                    |
                    v
            CLAIM VALIDATION
                    |
                    v
              AUTHORIZATION
```


# Practical Validation Model

```text
Capture Valid Token
       |
       v
Understand Token Purpose
       |
       v
Decode Header and Payload
       |
       v
Identify Trust Model
       |
       v
Validate Signature Enforcement
       |
       v
Validate Algorithm Handling
       |
       v
Validate Key Selection
       |
       v
Validate Issuer / Audience
       |
       v
Validate Lifetime
       |
       v
Validate Authorization
       |
       v
Validate Lifecycle
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

JWT testing is not:

```text
Decode Token
    |
    v
Change role=user to role=admin
    |
    v
Done
```

It is:

```text
TOKEN PURPOSE
     |
     v
CRYPTOGRAPHIC TRUST
     |
     v
KEY TRUST
     |
     v
CLAIM VALIDATION
     |
     v
TOKEN LIFECYCLE
     |
     v
AUTHORIZATION
```

For every JWT implementation ask:

```text
What type of token is this?

Who issued it?

Which service should accept it?

Which algorithm is expected?

Is the algorithm fixed by trusted configuration?

Which key verifies the token?

How is that key selected?

Can the token influence the key source?

Is the signature always verified?

Are unsecured tokens rejected?

Are unexpected algorithms rejected?

Is the issuer validated?

Is the audience validated?

Is expiration enforced?

Is not-before enforced where relevant?

What clock skew is allowed?

How long does the token live?

What does the subject identify?

Which roles or permissions are present?

Are scopes enforced?

Are tenant boundaries independently enforced?

Can an ID token be misused as an access token?

Can a token for one API be reused against another?

How are refresh tokens protected?

Are refresh tokens rotated?

Can refresh-token replay be detected?

What happens after logout?

What happens after password change?

What happens after password reset?

What happens after account disablement?

What happens after a role change?

Can tokens be revoked when required?

Are tokens stored in URLs?

Are tokens logged?

Are browser tokens exposed to JavaScript?

Are unnecessary sensitive claims present?

Are public keys being confused with secrets?

Are private signing keys properly protected?

Are equivalent JWT verifiers configured consistently?

Does a valid JWT still receive proper object-level authorization?

Has every finding been demonstrated through actual server behaviour?

Have token values been redacted from evidence?
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Authentication and Session Testing Cheatsheet](authentication-session-testing.md)
- [Authorization, IDOR and BOLA Cheatsheet](authorization-access-control.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)
- [Cross-Site Scripting (XSS) Cheatsheet](xss.md)


# Related Notes

Useful deeper notes include:

```text
docs/web/jwt.md
docs/web/oauth-oidc.md
docs/web/authentication.md
docs/web/authorisation.md
docs/web/api-security.md
```


# References

- [RFC 7519 - JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519){ target="_blank" rel="noopener noreferrer" }
- [RFC 8725 - JSON Web Token Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725){ target="_blank" rel="noopener noreferrer" }
- [RFC 7515 - JSON Web Signature](https://www.rfc-editor.org/rfc/rfc7515){ target="_blank" rel="noopener noreferrer" }
- [RFC 7517 - JSON Web Key](https://www.rfc-editor.org/rfc/rfc7517){ target="_blank" rel="noopener noreferrer" }
- [OWASP JSON Web Token Cheat Sheet for Java](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy - JWT Attacks](https://portswigger.net/web-security/jwt){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Start with trust"

    Before modifying claims, determine which issuer, algorithm and verification keys the application is supposed to trust. Most meaningful JWT weaknesses occur when that trust model is implemented incorrectly.


!!! tip "A valid JWT is not authorization"

    Successful signature verification establishes token integrity according to the configured trust model. The application must still enforce roles, scopes, ownership and tenant boundaries for every protected resource.


!!! tip "Change one property at a time"

    Modify one JWT property per test whenever possible. This makes it clear whether acceptance resulted from missing signature validation, issuer handling, audience handling, key selection, lifetime validation or authorization.


!!! tip "Review every verifier"

    In microservice environments, the same token may be validated by an API gateway, multiple backend services, WebSocket infrastructure and legacy APIs. One correctly configured verifier does not prove that the others are equally secure.


!!! warning "JWT payloads are usually readable"

    Ordinary signed JWT payloads are encoded rather than encrypted. Being able to decode a payload is expected and is not itself a vulnerability.


!!! warning "Never expose live bearer tokens"

    JWTs frequently function as bearer credentials. Redact them from screenshots, reports, logs and public tooling, and avoid submitting production tokens to third-party token-decoding websites.
