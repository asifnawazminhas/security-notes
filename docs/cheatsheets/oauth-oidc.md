---
title: OAuth 2.0 and OpenID Connect Security Testing Cheatsheet
description: Practical OAuth 2.0 and OpenID Connect security testing cheatsheet covering authorization flows, PKCE, state, nonce, redirect URIs, tokens, scopes, OIDC discovery, client security, account linking, Burp Suite workflows, source review, evidence, remediation and retesting.
---

# OAuth 2.0 and OpenID Connect Security Testing Cheatsheet

OAuth 2.0 and OpenID Connect are widely used for delegated authorization, API access and federated authentication.

They solve related but different problems.

```text
OAuth 2.0
    |
    v
Delegated Authorization

OpenID Connect
    |
    v
Authentication Layer Built on OAuth 2.0
```

A simplified OAuth question is:

```text
Can this client access this resource
with this authorization?
```

A simplified OpenID Connect question is:

```text
Who authenticated at the identity provider?
```

!!! warning "Authorised Security Testing"

    Test OAuth and OpenID Connect only against applications, clients, accounts and identity providers included in the assessment scope. Use dedicated test accounts and controlled authorization grants wherever possible. Avoid connecting unrelated third-party accounts, accessing real user data or changing production identity-provider configuration solely to demonstrate a weakness.


# Core Mental Model

OAuth security becomes easier to reason about when the participants are clearly identified.

```text
Resource Owner
     |
     v
Client
     |
     v
Authorization Server
     |
     v
Access Token
     |
     v
Resource Server
```


# OpenID Connect Adds Identity

```text
User
 |
 v
OpenID Provider
 |
 +--> ID Token
 |
 +--> Access Token
 |
 v
Relying Party
```


# OAuth Roles

The main OAuth roles are:

```text
Resource Owner

Client

Authorization Server

Resource Server
```


# Resource Owner

Usually:

```text
The user
```

who owns or controls access to protected resources.


# Client

The application requesting delegated access.

Examples:

```text
Web application

Single-page application

Mobile application

Desktop application

CLI
```


# Authorization Server

The system that:

```text
Authenticates the user

Obtains authorization

Issues tokens
```


# Resource Server

The API that accepts access tokens and provides protected resources.


# OpenID Connect Roles

OIDC commonly uses:

```text
End User

OpenID Provider

Relying Party
```


# OpenID Provider

The OpenID Provider performs authentication and issues identity information.


# Relying Party

The application relying on the OpenID Provider for authentication.


# OAuth Is Not Authentication by Itself

OAuth 2.0 defines an authorization framework.

Do not assume:

```text
OAuth access token
```

automatically provides a complete secure authentication protocol.


# OpenID Connect

OIDC adds standardized identity functionality including:

```text
ID tokens

UserInfo endpoint

Discovery metadata

Authentication claims

Nonce handling
```


# Common Components

During testing identify:

```text
Authorization endpoint

Token endpoint

Redirect URI

Client ID

Client type

Scopes

Response type

Grant type

PKCE

State

Nonce

Access token

Refresh token

ID token

UserInfo endpoint

JWKS endpoint

Discovery endpoint
```


# Typical Authorization Endpoint

```text
https://auth.example.com/authorize
```


# Typical Token Endpoint

```text
https://auth.example.com/token
```


# OIDC Discovery

Common location:

```text
/.well-known/openid-configuration
```


# JWKS

Commonly referenced through discovery metadata:

```text
jwks_uri
```


# Start With Discovery

If OIDC is in use, retrieve the discovery document when it is intentionally exposed.

Example:

```bash
curl -s https://auth.example.com/.well-known/openid-configuration | jq .
```


# Representative Metadata

```json
{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "userinfo_endpoint": "https://auth.example.com/userinfo",
  "jwks_uri": "https://auth.example.com/.well-known/jwks.json"
}
```


# Public Discovery Is Usually Expected

Do not report:

```text
OIDC discovery endpoint is publicly accessible
```

as a vulnerability by itself.

Discovery metadata is intentionally designed to describe the provider.


# Record the Architecture

Before testing, document:

```text
Authorization Server:
Client:
Resource Server:
Client ID:
Redirect URI:
Flow:
PKCE:
Scopes:
Token types:
Issuer:
Audience:
```


# OAuth Flow Inventory

Common OAuth grant types and flows include:

```text
Authorization Code

Authorization Code + PKCE

Client Credentials

Refresh Token

Device Authorization
```


# Legacy or Discouraged Patterns

You may encounter:

```text
Implicit Grant

Resource Owner Password Credentials
```

in older systems.

Their presence should be evaluated in context rather than automatically treated as a standalone exploitable vulnerability.


# Authorization Code Flow

A simplified flow:

```text
User
 |
 v
Client
 |
 v
Authorization Endpoint
 |
 v
User Authenticates
 |
 v
Authorization Code
 |
 v
Client
 |
 v
Token Endpoint
 |
 v
Access Token
```


# Detailed Flow

```text
Browser
  |
  | GET /authorize
  v
Authorization Server
  |
  | Authenticate + Consent
  v
Redirect URI
  |
  | code=...
  v
Client Backend
  |
  | POST /token
  v
Authorization Server
  |
  | access_token
  v
Client
```


# Example Authorization Request

```http
GET /authorize?response_type=code&client_id=client123&redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback&scope=openid%20profile&state=STATE_VALUE&code_challenge=CHALLENGE&code_challenge_method=S256 HTTP/1.1
Host: auth.example.com
```


# Parameters

| Parameter | Purpose |
|---|---|
| `response_type` | Requested response |
| `client_id` | Identifies client |
| `redirect_uri` | Callback destination |
| `scope` | Requested permissions |
| `state` | Correlates authorization request |
| `code_challenge` | PKCE challenge |
| `code_challenge_method` | PKCE method |


# Authorization Response

Example:

```http
HTTP/1.1 302 Found
Location: https://app.example.com/callback?code=AUTH_CODE&state=STATE_VALUE
```


# Token Exchange

Example:

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=AUTH_CODE&
redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback&
client_id=client123&
code_verifier=VERIFIER
```


# Token Response

```json
{
  "access_token": "ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "REFRESH_TOKEN",
  "id_token": "ID_TOKEN"
}
```


# Testing Model

For every OAuth flow ask:

```text
Who initiated the flow?

Which client requested authorization?

Which redirect URI was used?

Was the request correlated to the browser session?

Was PKCE used?

Was the code bound to the correct client?

Was the code bound to the redirect URI?

Can the code be reused?

Which scopes were granted?

Which tokens were returned?

Where were tokens delivered?

How are tokens validated?

How is the external identity linked to the local account?
```


# `state`

`state` is commonly used to maintain request correlation and protect authorization flows against CSRF-like attacks.

Conceptually:

```text
Client Generates State
       |
       v
Authorization Request
       |
       v
Authorization Server
       |
       v
Callback With State
       |
       v
Client Compares State
```


# Secure Behaviour

```text
Sent state
    =
Returned state
```

and the value should be bound to the initiating user-agent session or transaction.


# Baseline State Test

Capture a legitimate authorization request:

```text
state=abc123
```


# Callback

```text
/callback?code=CODE&state=abc123
```


# Controlled Modification

Change:

```text
state=abc123
```

to:

```text
state=invalid-test-value
```


# Expected

The client should reject the callback or otherwise fail the authorization transaction safely.


# Missing State

If an application does not use `state`, determine whether another mechanism provides equivalent request correlation.

Do not report:

```text
No state parameter
```

without understanding the actual flow and protections.


# State Quality

A state value should generally be:

```text
Unpredictable

Bound to the browser session

Single-use or transaction-specific

Validated on callback
```


# Static State

Example:

```text
state=12345
```

on every login may indicate ineffective request correlation.


# State Must Be Validated

Simply sending a state parameter is not enough.

```text
Generate
   |
   v
Send
   |
   v
Receive
   |
   v
Compare
```


# PKCE

PKCE stands for:

```text
Proof Key for Code Exchange
```

PKCE binds an authorization code to the client instance that initiated the authorization request.


# PKCE Model

```text
Client Generates
code_verifier
     |
     v
Derives
code_challenge
     |
     v
Authorization Request
     |
     v
Authorization Code
     |
     v
Token Request + code_verifier
     |
     v
Server Verifies
```


# S256

The recommended challenge transformation is:

```text
S256
```


# Concept

```text
BASE64URL(SHA256(code_verifier))
```

produces the:

```text
code_challenge
```


# Generate a Test Verifier

For a controlled lab or assessment client:

```bash
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```


# Generate S256 Challenge

```bash
python3 - <<'PY'
import base64
import hashlib

verifier = "PASTE_CONTROLLED_VERIFIER"
digest = hashlib.sha256(verifier.encode()).digest()
challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
print(challenge)
PY
```


# PKCE Validation Test

Use a code generated through your own controlled account.

Attempt the token exchange with an incorrect:

```text
code_verifier
```


# Expected

```text
Token exchange rejected
```


# Missing Verifier

If the original authorization request included a PKCE challenge, test whether the token endpoint incorrectly accepts the code without the corresponding verifier.


# Expected

```text
Rejected
```


# PKCE Downgrade

If the client normally uses:

```text
S256
```

determine whether the authorization server unexpectedly permits the security property to be removed or downgraded for the same client where policy requires PKCE.


# Do Not Assume PKCE Replaces State

PKCE and state address overlapping but not identical concerns.

Think of:

```text
state
  |
  v
Authorization request correlation

PKCE
  |
  v
Authorization code binding
```


# Authorization Code Security

Authorization codes should be:

```text
Short-lived

Single-use

Bound to the client

Bound to the redirect URI where applicable

Bound to PKCE verifier when PKCE is used
```


# Code Reuse

Use a controlled authorization code.

Exchange it once successfully.

Then attempt the same exchange again.


# Expected

```text
Second exchange rejected
```


# Code Lifetime

Authorization codes should have a limited lifetime.

Do not assume a specific number of seconds is universally required.

Evaluate:

```text
Provider design

Standards guidance

Application sensitivity
```


# Code Binding

A code issued to:

```text
Client A
```

should not be redeemable by:

```text
Client B
```


# Redirect URI Security

Redirect URI handling is one of the most important OAuth security boundaries.

After authorization, sensitive values may be delivered to the redirect URI.

Depending on the flow, this can include:

```text
Authorization code

Error information

State

Legacy front-channel tokens
```


# Secure Principle

Redirect URIs should be compared using strict matching according to the protocol and client registration model.


# Registered Redirect URI

Example:

```text
https://app.example.com/oauth/callback
```


# Test Variations Carefully

Potentially relevant controlled variations include:

```text
Different path

Different subdomain

Different scheme

Different port

Added query parameters

Path traversal normalization

Open redirect chaining
```


# Example

Registered:

```text
https://app.example.com/oauth/callback
```

Test:

```text
https://evil.example/oauth/callback
```

should obviously be rejected.


# Subdomain Variation

```text
https://attacker.app.example.com/oauth/callback
```

should not be accepted merely because it shares a parent domain unless explicitly registered and intended.


# Prefix Matching

Dangerous logic conceptually resembles:

```text
redirect_uri startsWith "https://app.example.com"
```


# Why Prefix Matching Is Dangerous

A value such as:

```text
https://app.example.com.attacker.example/callback
```

is not hosted on:

```text
app.example.com
```


# Exact URI Comparison

For ordinary registered redirect URIs, prefer strict comparison rather than custom substring or suffix logic.


# Redirect URI and Open Redirects

An authorization server may correctly redirect to:

```text
https://app.example.com/callback
```

but the callback endpoint itself may contain an open redirect.


# Example Flow

```text
Authorization Server
       |
       v
Trusted Callback
       |
       v
Open Redirect
       |
       v
External Site
```


# Security Impact Depends on Data Flow

Determine whether sensitive authorization material can actually reach the external destination.


# Do Not Report Chaining Theoretically

Demonstrate:

```text
Which value leaks?

How does it reach the external site?

Can it be used?
```


# Redirect URI Parameters

Some clients register redirect URIs containing query parameters.

Verify that comparison and token exchange behaviour remain consistent.


# Client Types

OAuth distinguishes conceptually between clients capable of protecting credentials and clients that cannot reliably do so.


# Confidential Client

Examples:

```text
Server-side web application

Backend service
```


# Public Client

Examples:

```text
Browser SPA

Native mobile application

Desktop application
```


# Public Client Secrets

A secret embedded in:

```text
JavaScript

Mobile binary

Desktop client
```

cannot be treated as a durable confidential credential.


# Do Not Report a Public Client ID

`client_id` is an identifier, not a secret.


# Client Secret

A confidential client may authenticate to the token endpoint using a client credential.


# Example

```http
Authorization: Basic BASE64_CLIENT_CREDENTIALS
```


# Secret Exposure

Search:

```bash
rg -ni 'client.?secret|client_secret|oauth.*secret|oidc.*secret' .
```


# Configuration Files

```bash
rg -ni 'CLIENT_SECRET|OAUTH|OIDC|CLIENT_ID' -g '.env*' -g '*.yaml' -g '*.yml' -g '*.json' -g '*.toml' .
```


# Browser Source

A confidential client secret should not be exposed in browser-delivered JavaScript.


# Scope

Scopes represent authorization requested by the client.

Examples:

```text
openid

profile

email

read

write

orders:read

orders:write
```


# Scope Testing

Determine:

```text
Which scopes are requested?

Which scopes are granted?

Which scopes are actually enforced?
```


# Reduced Scope

If a token has:

```text
orders:read
```

attempting a write operation should fail if:

```text
orders:write
```

is required.


# Scope Expansion

Do not assume that adding:

```text
scope=admin
```

to an authorization request should succeed.

The authorization server should grant only scopes permitted for:

```text
Client

User

Policy
```


# Requested vs Granted

Record both:

```text
Requested scopes

Granted scopes
```


# Consent

Where consent is part of the system, review whether the user is clearly shown:

```text
Client identity

Requested permissions

Relevant resource access
```


# Consent Is Contextual

Enterprise systems may use:

```text
Administrative consent

Pre-authorized clients

First-party clients
```

where interactive user consent is intentionally absent.


# Do Not Report Missing Consent Automatically

Determine the intended authorization model first.


# OpenID Connect

OIDC commonly adds:

```text
scope=openid
```

to the OAuth authorization request.


# ID Token

An ID token is typically a JWT containing authentication claims.

Example:

```json
{
  "iss": "https://auth.example.com",
  "sub": "248289761001",
  "aud": "client123",
  "exp": 1780000000,
  "iat": 1779996400,
  "nonce": "abc123"
}
```


# ID Token Validation

A relying party should validate relevant properties including:

```text
Signature

Issuer

Audience

Expiration

Nonce when applicable

Protocol-specific requirements
```


# JWT Validation

For detailed JWT testing, use:

[JWT Security Testing Cheatsheet](jwt.md)


# Access Token vs ID Token

```text
ID Token
   |
   v
Information about authentication
for the client

Access Token
   |
   v
Authorization credential
for resource server
```


# Token Confusion

Test whether an API incorrectly accepts an:

```text
ID token
```

where it should require:

```text
Access token
```


# Secure Behaviour

Each component should validate the token according to its intended purpose.


# `nonce`

OIDC can use `nonce` to associate a client session with an ID token and mitigate token replay/substitution risks in applicable flows.


# Model

```text
Client Generates Nonce
        |
        v
Authorization Request
        |
        v
OpenID Provider
        |
        v
ID Token Contains Nonce
        |
        v
Client Validates Nonce
```


# Nonce Test

Record the nonce from a controlled authentication flow.

Verify that an ID token containing an unexpected nonce is not accepted for that transaction where nonce validation is required.


# State vs Nonce

```text
state
 |
 v
Correlates authorization response

nonce
 |
 v
Correlates ID token/authentication transaction
```


# Both May Be Present

Example authorization request:

```text
/authorize?
client_id=client123&
response_type=code&
scope=openid%20profile&
state=STATE&
nonce=NONCE
```


# UserInfo Endpoint

OIDC providers may expose:

```text
/userinfo
```


# Example

```bash
curl -s \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  https://auth.example.com/userinfo
```


# Representative Response

```json
{
  "sub": "123",
  "name": "Test User",
  "email": "test@example.com"
}
```


# Authorization

The UserInfo endpoint should accept only appropriate access tokens.


# UserInfo Claims

Review whether the returned claims match:

```text
Granted scopes

Provider policy

Application requirements
```


# Excessive Claims

Do not assume every returned claim is vulnerable.

Determine whether sensitive information is exposed beyond the authorization granted.


# Account Linking

Account linking is a critical OIDC testing area.

Example:

```text
Local Account
     |
     v
"Sign in with Provider"
     |
     v
External Identity
     |
     v
Linked Account
```


# Dangerous Assumption

Do not automatically trust:

```text
Email address
```

as sufficient proof that two identities represent the same person.


# Stable Identity

OIDC identity should generally rely on the provider's stable identity relationship, particularly:

```text
iss + sub
```


# Why

The same:

```text
sub
```

from different issuers may represent different identities.


# Identity Key

Conceptually:

```text
Issuer
  +
Subject
  =
Federated Identity
```


# Email Linking

Review whether the application:

```text
Automatically links by email

Requires authentication to existing account

Requires verification

Handles email changes

Handles provider differences
```


# Account Linking Test

Using only controlled accounts:

```text
1. Create local test account.

2. Create controlled identity-provider account.

3. Observe linking workflow.

4. Determine what proves ownership of both identities.

5. Verify that attacker-controlled claims cannot force linking.
```


# Never Use Real Third-Party Accounts Without Scope

Identity-provider testing can affect systems outside the target organization's control.


# Login CSRF

A login flow may be vulnerable when an attacker can cause a victim browser to become authenticated to the attacker's account.

Conceptually:

```text
Attacker Starts Login
       |
       v
Attacker Authorization Response
       |
       v
Victim Browser Processes Response
       |
       v
Victim Logged Into Attacker Account
```


# Why It Matters

The victim may unknowingly enter:

```text
Personal data

Payment information

Documents
```

into an attacker-controlled account.


# State and Transaction Binding

Correct request correlation is important for preventing this class of issue.


# Authorization Response Injection

A client should ensure the callback corresponds to an authorization transaction it initiated.


# Callback Validation

Ask:

```text
Was this callback expected?

Which browser session initiated it?

Which authorization request does it belong to?

Is the code associated with the expected client?
```


# Token Endpoint

The token endpoint is security-critical.

Review:

```text
Grant type validation

Client authentication

Authorization code validation

PKCE validation

Redirect URI validation

Refresh-token handling

Error handling
```


# Client Authentication

Confidential clients may authenticate using methods such as:

```text
client_secret_basic

client_secret_post

private_key_jwt
```

depending on provider support.


# Avoid Client Secrets in URLs

Do not transmit client secrets in query strings.


# Token Endpoint Errors

Errors should not expose:

```text
Client secrets

Private keys

Stack traces

Internal database details
```


# Refresh Tokens

Refresh tokens allow a client to obtain new access tokens without repeating the full authorization flow.


# Review

```text
Lifetime

Storage

Rotation

Replay

Revocation

Scope

Client binding
```


# Refresh Scope

A refresh operation should not silently expand privileges beyond the original authorized grant.


# Example

Original:

```text
scope=profile:read
```

Refresh should not result in:

```text
profile:read admin:write
```


# Refresh Token Rotation

Conceptually:

```text
Refresh A
   |
   v
Token Endpoint
   |
   +--> Access B
   |
   +--> Refresh B

Refresh A
   |
   v
No Longer Valid
```


# Replay

If a rotated refresh token is reused, the provider should follow its configured replay-handling policy.


# Revocation

OAuth deployments may provide token revocation mechanisms.

Test whether logout or account disconnect behaves according to the application's intended lifecycle.


# Do Not Assume Immediate Access Token Revocation

Short-lived stateless access tokens may remain valid until expiration.

Determine the actual design before reporting.


# Client Credentials Grant

Machine-to-machine flow:

```text
Client
  |
  | Client Authentication
  v
Token Endpoint
  |
  v
Access Token
  |
  v
API
```


# No User

Client Credentials normally represents:

```text
Client / workload identity
```

rather than an end user.


# Review

```text
Secret/key storage

Allowed scopes

Audience

Token lifetime

Service authorization

Credential rotation
```


# Client Credential Exposure

High-impact locations include:

```text
Source repositories

CI logs

Container images

Environment dumps

Browser JavaScript

Public configuration
```


# Device Authorization

Device flows are used by devices that cannot easily perform browser authentication themselves.


# Concept

```text
Device
  |
  v
Device Code
  |
  v
User Verification URI
  |
  v
User Authenticates Elsewhere
  |
  v
Device Receives Token
```


# Review

```text
Device-code lifetime

User-code entropy

Polling behaviour

Binding

User confirmation

Phishing resistance
```


# Implicit Flow

Older applications may receive tokens through the front channel.

Example historical pattern:

```text
/callback#access_token=...
```


# Modern Guidance

New implementations should generally prefer authorization code flow with PKCE rather than implicit flow.


# Existing Applications

Do not classify implicit flow alone as proof of account compromise.

Assess:

```text
Actual token exposure

Client type

Migration feasibility

Provider configuration

Application risk
```


# Resource Owner Password Credentials

Older OAuth deployments may directly collect:

```text
Username

Password
```

and exchange them for tokens.


# Modern Guidance

This grant is not part of OAuth 2.1 direction and is generally unsuitable for new designs.


# Again

Architecture age alone is not proof of exploitability.

Document:

```text
Actual risk

Credential handling

Available migration path
```


# Authorization Server Mix-Up

Complex deployments may interact with multiple authorization servers.

The client must know:

```text
Which authorization server produced this response?
```


# Issuer Validation

OIDC issuer information and authorization-server metadata help bind responses and tokens to the intended provider.


# Multiple Identity Providers

Example:

```text
Login with Provider A

Login with Provider B

Corporate SSO
```


# Review

```text
Issuer binding

State binding

Callback handling

Account linking

Identity collisions
```


# Open Redirect Interaction

OAuth parameters may include application-controlled return locations in addition to the registered OAuth redirect URI.

Examples:

```text
return_url

next

continue

redirect

redirectTo
```


# Distinguish Them

```text
OAuth redirect_uri
```

and:

```text
Application post-login redirect
```

may be different controls.


# Post-Login Redirect

Example:

```text
/oauth/callback?next=/dashboard
```


# Test

Determine whether:

```text
next
```

can redirect externally after authentication.


# Impact

An open redirect may support:

```text
Phishing

Token leakage in specific architectures

Authorization flow manipulation
```

but the exact impact must be demonstrated.


# Referer Leakage

Sensitive values placed in URLs may leak through:

```http
Referer:
```


# Review Callback Pages

Callback pages should avoid unnecessarily loading third-party resources before sensitive URL parameters are removed or exchanged.


# Browser History

Front-channel values may remain in browser history if not handled carefully.


# Authorization Codes

Codes are intended to be short-lived and single-use, reducing but not eliminating the need to handle them carefully.


# Access Tokens in URLs

Bearer access tokens should not ordinarily be placed in URLs.


# Why

URLs may appear in:

```text
Browser history

Server logs

Proxy logs

Analytics

Referer headers
```


# Fragment

Historically, implicit-flow tokens were delivered in URL fragments.

Fragments are not sent in ordinary HTTP requests to the server, but browser-side scripts and history still make front-channel token handling security-sensitive.


# Token Storage

Browser applications may store tokens in:

```text
Memory

Cookies

localStorage

sessionStorage
```


# No Universal Storage Answer

Evaluate:

```text
XSS exposure

CSRF exposure

Architecture

Token lifetime

Refresh design

Browser constraints
```


# Cookies

If OAuth-derived application sessions use cookies, review:

```text
Secure

HttpOnly

SameSite

Domain

Path
```


# JavaScript Storage

Tokens accessible to JavaScript may be exposed by XSS.


# XSS Interaction

OAuth does not protect tokens from malicious script running in the trusted application origin.


# CORS Interaction

CORS does not replace:

```text
OAuth authorization

Token validation

Resource authorization
```


# API Token Validation

Resource servers should validate access tokens according to the token type and deployment architecture.


# JWT Access Token

If the access token is a JWT, review:

```text
Signature

Issuer

Audience

Expiration

Scope
```


# Opaque Access Token

An access token may instead be:

```text
Opaque
```


# Opaque Token

The API may validate it using:

```text
Authorization-server introspection

Shared session/token store
```


# Do Not Assume Access Tokens Are JWTs

Inspect actual token format and architecture.


# Token Introspection

OAuth deployments may expose an introspection endpoint to authorized clients/resource servers.


# Security Question

Is introspection itself properly authenticated and restricted?


# Token Revocation

Revocation endpoints should similarly enforce appropriate client authentication and token handling.


# Scope Enforcement

A valid access token is not enough.

Example:

```text
Token scope:
orders:read
```

Request:

```http
DELETE /api/orders/123
```


# Expected

```text
Denied
```

if deletion requires a stronger permission.


# Object Authorization

Even a token with:

```text
orders:read
```

should not necessarily read every user's order.


# Model

```text
Valid Access Token
        |
        v
Correct Audience
        |
        v
Correct Scope
        |
        v
Object Authorization
        |
        v
Resource
```


# Tenant Authorization

OAuth scopes do not automatically enforce tenant boundaries.


# Example

```json
{
  "scope": "projects:read",
  "tenant": "10"
}
```


# Test

Can the token read:

```text
Tenant 11 project
```

by modifying an object identifier?


# Burp Suite Workflow

Burp is especially useful because OAuth flows span multiple requests and redirects.


# Proxy

Capture the complete login sequence:

```text
Application

Authorization redirect

Identity provider

Callback

Token-related backend calls

Application session
```


# HTTP History

Filter by:

```text
authorize

oauth

oidc

callback

token

userinfo

login

sso
```


# Repeater

Use Repeater for controlled testing of:

```text
Authorization requests

Callback requests

Token endpoint requests

UserInfo requests

Protected APIs
```


# Preserve Baseline

Save a complete successful flow before modifying anything.


# One-Variable Method

Modify one parameter at a time:

```text
state

redirect_uri

code_verifier

scope

client_id

nonce
```


# Why

OAuth requests contain many interdependent values.

Changing several at once makes interpretation difficult.


# Burp Comparer

Useful for comparing:

```text
Valid callback

Invalid state callback

Correct verifier

Incorrect verifier

Allowed redirect URI

Rejected redirect URI
```


# Logger

A logging extension can help correlate:

```text
Authorization request

Callback

Token exchange

API request
```


# Session Handling

Be careful when Burp or the browser automatically updates:

```text
Cookies

Authorization headers

Tokens
```

during testing.


# Multiple Browsers

Two isolated browser profiles can help distinguish:

```text
Victim test session

Attacker test session
```


# Keep Accounts Controlled

OAuth CSRF and account-linking tests are much easier to defend when both identities belong to the assessment team.


# Browser Developer Tools

Useful areas:

```text
Network

Application

Cookies

localStorage

sessionStorage
```


# Inspect Redirect Chain

Record:

```text
302

Location header

Query parameters

Fragments

Cookies
```


# curl

Authorization endpoints are browser-oriented, but metadata and APIs can often be inspected with curl.


# Discovery

```bash
curl -s https://auth.example.com/.well-known/openid-configuration | jq .
```


# JWKS

After obtaining the configured `jwks_uri`:

```bash
curl -s https://auth.example.com/.well-known/jwks.json | jq .
```


# UserInfo

```bash
curl -s \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  https://auth.example.com/userinfo | jq .
```


# Protected API

```bash
curl -i \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  https://api.example.com/me
```


# Avoid Shell History Leakage

Bearer tokens and client secrets entered directly on the command line may be retained in shell history depending on configuration.


# Prefer Temporary Environment Variables Carefully

For a controlled local environment:

```bash
read -rsp 'Access token: ' ACCESS_TOKEN
echo
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" https://api.example.com/me
unset ACCESS_TOKEN
```


# Source Code Review

Trace the full trust chain:

```text
Login Start
    |
    v
Authorization Request
    |
    v
Callback
    |
    v
Code Exchange
    |
    v
Token Validation
    |
    v
Identity Mapping
    |
    v
Session Creation
    |
    v
Authorization
```


# Generic Search

```bash
rg -ni 'oauth|openid|oidc|authorize|authorization_endpoint|token_endpoint|userinfo|jwks' .
```


# Redirect Search

```bash
rg -ni 'redirect_uri|redirectUri|callback|return_url|returnUrl|redirectTo|continue|next' .
```


# State Search

```bash
rg -ni '\bstate\b|csrf.*oauth|oauth.*csrf' .
```


# PKCE Search

```bash
rg -ni 'code_verifier|codeVerifier|code_challenge|codeChallenge|S256|pkce' .
```


# Nonce Search

```bash
rg -ni '\bnonce\b|id.?token|openid' .
```


# Client Credentials Search

```bash
rg -ni 'client_id|clientId|client_secret|clientSecret|CLIENT_SECRET|CLIENT_ID' .
```


# Scope Search

```bash
rg -ni '\bscope\b|scopes|permissions|claims' .
```


# Issuer Search

```bash
rg -ni 'issuer|authority|discovery|metadata|well-known' .
```


# Node.js

Common libraries/frameworks may include:

```text
openid-client

passport

Passport OAuth strategies

Auth.js
```


# Search

```bash
rg -ni 'openid-client|passport|oauth|oidc|authorizationUrl|tokenUrl|clientSecret' -g '*.js' -g '*.ts' .
```


# Python

Common libraries may include:

```text
Authlib

oauthlib

requests-oauthlib

social-auth
```


# Search

```bash
rg -ni 'Authlib|oauthlib|requests_oauthlib|social.*auth|openid|oauth' -g '*.py' .
```


# Java

Common components include:

```text
Spring Security OAuth2 Client

Spring Security Resource Server
```


# Search

```bash
rg -ni 'oauth2Login|oauth2Client|ClientRegistration|OidcUser|OAuth2User|issuer-uri|jwk-set-uri' -g '*.java' -g '*.yaml' -g '*.yml' .
```


# .NET

Common components include:

```text
OpenIdConnect

OAuth

JwtBearer

Microsoft.Identity
```


# Search

```bash
rg -ni 'AddOpenIdConnect|OpenIdConnectOptions|AddOAuth|ClientId|ClientSecret|Authority|CallbackPath' -g '*.cs' .
```


# PHP

Search:

```bash
rg -ni 'oauth|openid|oidc|client_id|client_secret|redirect_uri' -g '*.php' .
```


# Go

Search:

```bash
rg -ni 'oauth2|oidc|ClientID|ClientSecret|RedirectURL|Endpoint|Verifier' -g '*.go' .
```


# Ruby

Search:

```bash
rg -ni 'omniauth|oauth2|openid_connect|client_id|client_secret|callback' -g '*.rb' .
```


# Configuration

OAuth configuration often exists outside source code.

Search:

```bash
rg -ni 'OAUTH|OIDC|OPENID|CLIENT_ID|CLIENT_SECRET|ISSUER|AUTHORITY|REDIRECT_URI' -g '.env*' -g '*.yaml' -g '*.yml' -g '*.json' -g '*.toml' .
```


# Front-End Review

Search JavaScript bundles for:

```text
client_id

authorization endpoint

redirect URI

scope

issuer

OIDC metadata
```


# Public Configuration

Values such as:

```text
client_id

authorization endpoint

issuer
```

are often intentionally public.

Do not classify them as secrets.


# Secrets

Values such as confidential-client:

```text
client_secret
```

require protection.


# Callback Source Review

The callback is one of the most important code paths.


# Review

```text
State validation

Code handling

Error handling

Token exchange

Issuer validation

Nonce validation

Identity mapping

Session creation

Post-login redirect
```


# Vulnerable Concept

```text
Receive code
    |
    v
Exchange code
    |
    v
Read email claim
    |
    v
Login matching local email
```

without sufficient identity-provider and account-linking validation.


# Better Model

```text
Trusted Issuer
      +
Stable Subject
      |
      v
Known Federated Identity
      |
      v
Local Account
```


# Session Creation

After successful OAuth/OIDC authentication, many applications create their own session cookie.


# Test Both Layers

```text
OAuth/OIDC Layer
       |
       v
Application Session
```


# Application Session

Review:

```text
Session fixation

Cookie attributes

Logout

Timeout

Privilege changes

Account linking
```


# Do Not Stop at the Identity Provider

A correctly configured provider cannot compensate for insecure local session or authorization logic.


# Error Handling

Test controlled malformed values such as:

```text
Invalid state

Unknown code

Expired code

Wrong verifier

Invalid redirect URI

Unsupported scope
```


# Expected

```text
Safe rejection
```

without unnecessary:

```text
Stack traces

Client secrets

Token values

Internal endpoints

Database errors
```


# Logging

OAuth logs can accidentally contain:

```text
Authorization codes

Access tokens

Refresh tokens

ID tokens

Client secrets
```


# Redaction

Prefer logging:

```text
Flow ID

Client ID

User ID

Issuer

Outcome

Error category
```

without full credential values.


# Reverse Proxy Considerations

Applications behind reverse proxies may construct callback URLs from:

```text
Host

X-Forwarded-Host

X-Forwarded-Proto
```


# Security Question

Can untrusted forwarded headers influence:

```text
OAuth redirect URI

Password-reset URL

OIDC callback URL
```


# Trust Proxy Configuration

Only trusted proxies should be allowed to establish forwarded host/scheme information.


# Dynamic Redirect URI Generation

Safer designs often use:

```text
Configured canonical external URL
```

rather than constructing security-sensitive callback addresses from arbitrary request headers.


# Multiple Environments

OAuth registrations may include:

```text
Production

Staging

Development

Localhost
```


# Review

Ensure production clients do not unnecessarily allow:

```text
Development callback domains

Abandoned hosts

Untrusted subdomains
```


# Subdomain Takeover Interaction

A registered redirect URI pointing to an abandoned subdomain can become security-sensitive.

Confirm:

```text
Domain ownership

DNS state

Provider registration

Actual authorization data flow
```

before reporting.


# Native Applications

Native applications commonly use:

```text
Custom URI schemes

Loopback redirects

Claimed HTTPS URLs
```


# Review

Determine whether another application could intercept the authorization response and whether PKCE mitigates code interception.


# Custom URI Scheme

Example:

```text
myapp://oauth/callback
```


# Risk

Multiple applications may be able to register the same custom scheme on some platforms.


# PKCE

PKCE is particularly important for public native clients because they cannot securely hold a client secret.


# SPA

Single-page applications are public clients.


# Do Not Rely on Embedded Client Secret

Any secret shipped to the browser should be assumed obtainable by the user.


# SPA Review

Focus on:

```text
Authorization code + PKCE

Redirect URI

State

Token storage

XSS exposure

Refresh design

CORS

API authorization
```


# Backend-for-Frontend

Some architectures keep OAuth tokens server-side and expose only an application session to the browser.


# Model

```text
Browser
   |
   v
BFF Session Cookie
   |
   v
Backend-for-Frontend
   |
   v
OAuth Tokens
   |
   v
API
```


# Benefit

This can reduce direct exposure of OAuth tokens to browser JavaScript.

It still requires:

```text
CSRF protection

Session security

Authorization
```


# Microservices

OAuth access tokens may cross:

```text
Gateway

Service A

Service B

Service C
```


# Review Every Resource Server

Each service should enforce:

```text
Issuer

Audience

Token lifetime

Scopes

Resource authorization
```


# Gateway

If only the gateway validates tokens, determine whether backend services can be reached directly.


# Identity Headers

A gateway may translate tokens into:

```http
X-User-ID: 123
X-Scope: profile:read
```


# Backend Trust

Backends must ensure these headers originate only from the trusted gateway.


# User-Controlled Header

An external client should not be able to supply:

```http
X-User-ID: administrator
```

and bypass the gateway-derived identity.


# API Audience

A token intended for:

```text
API A
```

should not automatically be accepted by:

```text
API B
```


# Scope Is Not Object Authorization

```text
scope=orders:read
```

does not mean:

```text
read every order
```


# Combine

```text
Token Valid
    |
    v
Audience Valid
    |
    v
Scope Valid
    |
    v
User/Tenant Authorized
    |
    v
Object Returned
```


# Common Testing Mistakes

Avoid these conclusions:

```text
Client ID visible = vulnerability

OIDC discovery visible = vulnerability

JWKS public = vulnerability

OAuth uses redirects = open redirect

No consent screen = vulnerability

No client secret in SPA = vulnerability

JWT readable = vulnerability
```


# Instead

Ask:

```text
What security property failed?

What was the expected policy?

What actual behaviour proves failure?

What impact follows from that behaviour?
```


# Evidence - State Failure

Capture:

```text
Authorization request

Original state

Callback

Modified/mismatched state

Successful login or linking result
```


# Evidence - Redirect URI Failure

Capture:

```text
Registered/expected redirect URI

Modified redirect URI

Authorization-server response

Destination reached

Sensitive value delivered
```


# Evidence - PKCE Failure

Capture:

```text
Authorization request with challenge

Authorization code

Incorrect or missing verifier

Successful token response
```


# Evidence - Code Reuse

Capture:

```text
First token exchange

Successful response

Second exchange using same code

Second successful response
```

if that is the observed failure.


# Evidence - Scope Failure

Capture:

```text
Token scope

Protected endpoint

Required permission

Successful unauthorized action
```


# Evidence - Account Linking

Capture only controlled identities:

```text
Local Account A

Federated Account B

Linking condition

Resulting local identity
```


# Evidence - Token Confusion

Capture:

```text
Token type

Token issuer

Token audience

Target service

Successful acceptance
```


# Reporting Missing State Validation

> The OAuth callback does not adequately validate the authorization transaction against the browser session that initiated it. A callback containing a mismatched controlled `state` value was accepted and completed the authentication flow. The client should generate an unpredictable transaction-specific state value, bind it to the initiating session and verify it before processing the authorization response.


# Reporting PKCE Validation Failure

> The authorization server issues an authorization code with a PKCE challenge but the token endpoint does not enforce possession of the corresponding verifier. A code generated through a controlled test account was successfully exchanged using an incorrect verifier. The token endpoint must cryptographically bind the authorization code to the original PKCE verifier.


# Reporting Redirect URI Weakness

> The authorization server accepts a redirect URI outside the client's intended registered callback set. A modified authorization request caused the authorization response to be delivered to a controlled alternate destination. Redirect URIs should be registered explicitly and validated using strict matching appropriate to the client type.


# Reporting Code Reuse

> Authorization codes are not invalidated after successful redemption. The same controlled authorization code was exchanged more than once and each exchange returned valid token material. Authorization codes should be short-lived, single-use credentials and must be invalidated after successful redemption.


# Reporting Scope Enforcement Failure

> The resource server does not enforce the permissions represented by the access token scope. A token containing only the `orders:read` scope successfully performed an operation requiring write access. The API should validate the required scope or authorization policy for every protected operation.


# Reporting ID Token Confusion

> The API accepts an OpenID Connect ID token as an API authorization credential even though the token is intended for the client application rather than the resource server. Resource servers should accept only access tokens intended for that API and validate token audience, purpose and required authorization claims.


# Reporting Account Linking Weakness

> The application links a federated identity to an existing local account based solely on an email claim without adequately proving that the external identity is authorized to control the existing account. Federated account mapping should use a trusted issuer and stable subject identifier, with explicit proof of account ownership where identities are linked.


# Reporting Client Secret Exposure

> A confidential OAuth client secret is included in browser-delivered application code. Because browser clients cannot protect embedded secrets from users, the credential should be rotated and removed from client-side code. If the application is a public client, it should use an OAuth flow designed for public clients rather than relying on a client secret for confidentiality.


# Reporting Token Leakage

> OAuth bearer tokens are exposed through URL parameters during the application flow. URLs may be retained by browser history, reverse proxies, application logs and analytics systems. Sensitive bearer credentials should be transmitted using protocol-appropriate mechanisms that minimize unintended disclosure.


# Avoid Overclaiming

Do not write:

```text
OAuth authentication can be completely bypassed
```

if the demonstrated issue is only:

```text
State value is predictable
```

without demonstrating a meaningful security consequence.


# Severity

Consider:

```text
Account takeover

Account linking

Token theft

Authorization-code theft

Cross-user login

Cross-tenant access

Privilege level

Scopes

Token lifetime

Refresh capability

User interaction

Affected clients

Affected APIs
```


# High-Impact Conditions

Potentially severe OAuth/OIDC issues include:

```text
Authorization response redirected to attacker-controlled origin

Account linking to attacker identity

Authentication transaction injection

Access token accepted by unintended high-value API

Client credential compromise

Refresh-token compromise

Issuer/token confusion resulting in account compromise
```


# Context-Dependent Conditions

Examples requiring careful interpretation:

```text
Missing state

Long token lifetime

Implicit flow

Public client without secret

Public JWKS

Broad scope request

No consent screen
```


# Root Causes

Common root causes include:

```text
Weak redirect URI validation

Missing transaction binding

Missing PKCE enforcement

Authorization code reuse

Incorrect client binding

Incorrect issuer validation

Incorrect audience validation

Token purpose confusion

Weak account linking

Scope not enforced

Secrets embedded in public clients

Unsafe post-login redirects

Insecure token storage
```


# Remediation - Authorization Code Flow

For modern interactive clients, prefer authorization code flow with appropriate PKCE support according to current OAuth security guidance.


# Redirect URI Registration

Maintain explicit registered redirect URIs.

Avoid:

```text
Wildcards

Substring matching

Unnecessary subdomain patterns

Untrusted development domains
```

unless the platform has a carefully designed reason and equivalent security controls.


# State

Where state is used for transaction correlation:

```text
Generate securely

Bind to session

Validate on callback

Expire after use
```


# PKCE

Use:

```text
S256
```

and enforce verifier validation for clients requiring PKCE.


# Authorization Codes

Ensure codes are:

```text
Short-lived

Single-use

Client-bound

Redirect-bound where required

PKCE-bound where used
```


# Client Credentials

Store confidential-client credentials in:

```text
Server-side secret stores

Protected environment configuration

Managed secret services
```

rather than browser or mobile code.


# Rotate Exposed Credentials

If a client secret has been exposed:

```text
Remove from code
```

and:

```text
Rotate the credential
```


# Token Validation

Resource servers should validate relevant:

```text
Issuer

Audience

Lifetime

Token type

Scope
```


# OIDC Validation

Relying parties should correctly validate:

```text
Issuer

Audience

Signature

Expiration

Nonce where applicable
```


# Identity Mapping

Prefer stable federated identity mapping based on:

```text
Trusted issuer

Stable subject
```


# Account Linking

Require sufficient proof before connecting:

```text
External identity
```

to:

```text
Existing local account
```


# Token Storage

Minimize exposure according to the application's architecture.

Consider:

```text
XSS

CSRF

Token lifetime

Refresh-token sensitivity
```


# Scope

Follow least privilege:

```text
Request only needed scopes

Grant only permitted scopes

Enforce scopes at APIs
```


# Object Authorization

After scope validation, still enforce:

```text
User ownership

Tenant boundary

Role

Business policy
```


# Logging

Redact:

```text
Authorization codes

Access tokens

Refresh tokens

ID tokens

Client secrets
```


# Retesting State

Repeat the original authorization flow.

Expected:

```text
Correct state
   |
   v
Accepted

Wrong state
   |
   v
Rejected
```


# Retesting PKCE

```text
Correct verifier
    |
    v
Accepted

Incorrect verifier
    |
    v
Rejected

Missing verifier
    |
    v
Rejected
```


# Retesting Redirect URI

Try the exact URI used in the original finding.

Expected:

```text
Rejected
```

while the registered callback remains functional.


# Retesting Code Reuse

```text
First redemption
      |
      v
Success

Second redemption
      |
      v
Rejected
```


# Retesting Scope

Use a low-scope token against the original privileged endpoint.

Expected:

```text
Denied
```


# Retesting Token Purpose

Present the previously misused token type.

Expected:

```text
Rejected
```


# Retesting Account Linking

Repeat with two controlled identities.

Verify the application requires the intended proof before linking.


# Retesting Client Secret

Verify:

```text
Old secret invalid

New secret protected

Secret absent from client-side code
```


# Equivalent Clients

If one OAuth weakness is found, review:

```text
Web client

SPA

Mobile client

Admin client

Legacy client

Staging client
```


# Equivalent Providers

Where multiple identity providers exist, compare:

```text
Redirect validation

State

Nonce

Account linking

Issuer validation
```


# OAuth / OIDC Checklist

## Architecture

- [ ] Authorization server identified
- [ ] Resource server identified
- [ ] Client identified
- [ ] Client type identified
- [ ] Client ID recorded
- [ ] Redirect URIs identified
- [ ] OAuth flow identified
- [ ] OIDC usage identified
- [ ] Token types identified
- [ ] Issuer identified
- [ ] API audiences identified

## Authorization Request

- [ ] `response_type` reviewed
- [ ] `client_id` reviewed
- [ ] `redirect_uri` reviewed
- [ ] `scope` reviewed
- [ ] `state` reviewed
- [ ] PKCE reviewed
- [ ] `nonce` reviewed where applicable
- [ ] Additional application redirect parameters reviewed

## State

- [ ] State present or equivalent protection understood
- [ ] State unpredictable
- [ ] State session-bound
- [ ] State validated
- [ ] Mismatched state rejected
- [ ] Reused state reviewed
- [ ] Missing state behaviour reviewed

## PKCE

- [ ] PKCE enabled where appropriate
- [ ] S256 used
- [ ] Verifier required
- [ ] Incorrect verifier rejected
- [ ] Missing verifier rejected
- [ ] Downgrade behaviour reviewed

## Authorization Code

- [ ] Code lifetime reviewed
- [ ] Code single-use
- [ ] Code client-bound
- [ ] Code redirect-bound where applicable
- [ ] Code PKCE-bound
- [ ] Code reuse tested

## Redirect URI

- [ ] Registered URIs identified
- [ ] Exact matching behaviour reviewed
- [ ] Scheme changes tested where relevant
- [ ] Host changes tested
- [ ] Subdomain changes tested
- [ ] Path changes tested
- [ ] Port changes tested
- [ ] Open redirect chaining reviewed
- [ ] Abandoned callback domains reviewed

## Client Security

- [ ] Client type understood
- [ ] Public vs confidential model correct
- [ ] Client secrets searched
- [ ] Browser code reviewed
- [ ] Mobile/public client secrets not relied upon
- [ ] Confidential secrets protected
- [ ] Secret rotation capability reviewed

## Tokens

- [ ] Access token identified
- [ ] Refresh token identified
- [ ] ID token identified
- [ ] Token lifetime reviewed
- [ ] Token storage reviewed
- [ ] URL leakage reviewed
- [ ] Logging leakage reviewed
- [ ] Token purpose validated
- [ ] Cross-service reuse reviewed

## OIDC

- [ ] Discovery metadata reviewed
- [ ] Issuer validation reviewed
- [ ] ID token signature validation reviewed
- [ ] Audience validation reviewed
- [ ] Expiration validation reviewed
- [ ] Nonce validation reviewed
- [ ] UserInfo reviewed
- [ ] Identity mapping reviewed

## Account Linking

- [ ] Federated identity key identified
- [ ] Issuer considered
- [ ] Subject considered
- [ ] Email linking reviewed
- [ ] Existing-account linking reviewed
- [ ] Linking requires appropriate proof
- [ ] Multiple providers reviewed

## Scope and Authorization

- [ ] Requested scopes recorded
- [ ] Granted scopes recorded
- [ ] API scope enforcement tested
- [ ] Read/write separation tested
- [ ] Object authorization tested
- [ ] Tenant authorization tested
- [ ] Role authorization tested

## Refresh Tokens

- [ ] Storage reviewed
- [ ] Lifetime reviewed
- [ ] Rotation reviewed
- [ ] Replay handling reviewed
- [ ] Revocation reviewed
- [ ] Scope expansion tested
- [ ] Client binding reviewed

## Session

- [ ] Application session identified
- [ ] Session fixation reviewed
- [ ] Cookie attributes reviewed
- [ ] Logout reviewed
- [ ] Password change reviewed
- [ ] Account disable reviewed

## Source Review

- [ ] OAuth libraries identified
- [ ] OIDC libraries identified
- [ ] Callback handler identified
- [ ] State generation identified
- [ ] State validation identified
- [ ] PKCE implementation identified
- [ ] Redirect validation identified
- [ ] Token exchange identified
- [ ] Token validation identified
- [ ] Identity mapping identified
- [ ] Account linking identified
- [ ] Secrets searched

## Evidence

- [ ] Full baseline flow captured
- [ ] Accounts controlled
- [ ] Exact modified parameter recorded
- [ ] Modified request saved
- [ ] Response saved
- [ ] Redirect chain saved
- [ ] Token values redacted
- [ ] Side effect verified
- [ ] Timestamp recorded

## Retest

- [ ] Original state issue fixed
- [ ] Original PKCE issue fixed
- [ ] Redirect URI restricted
- [ ] Code reuse rejected
- [ ] Scope enforced
- [ ] Token purpose enforced
- [ ] Account linking fixed
- [ ] Exposed credentials rotated
- [ ] Legitimate login still works
- [ ] Equivalent clients reviewed


# Parameter Matrix

| Parameter | Security Question |
|---|---|
| `client_id` | Which client initiated the request? |
| `redirect_uri` | Where will the response be delivered? |
| `state` | Is the response bound to the initiating transaction? |
| `scope` | Which permissions are requested? |
| `code_challenge` | Is the code bound through PKCE? |
| `nonce` | Is the OIDC authentication transaction bound? |
| `response_type` | Which response is requested? |


# Token Matrix

| Token | Intended Consumer | Purpose |
|---|---|---|
| Authorization code | Token endpoint | Exchange for tokens |
| Access token | Resource server | API authorization |
| ID token | OIDC client | Authentication information |
| Refresh token | Authorization server | Obtain new tokens |


# Client Matrix

| Client | Can Reliably Keep Secret? | Typical Protection |
|---|---:|---|
| Server web app | Yes | Client authentication + PKCE where appropriate |
| SPA | No | Authorization code + PKCE |
| Native mobile app | No | Authorization code + PKCE |
| Backend service | Yes | Protected client credential |


# State / PKCE / Nonce Matrix

| Control | Primary Role |
|---|---|
| `state` | Authorization transaction correlation |
| PKCE | Authorization-code binding |
| `nonce` | OIDC ID-token transaction binding |


# Redirect Matrix

| Test | Expected |
|---|---|
| Registered URI | Allow |
| Unregistered host | Deny |
| Unregistered subdomain | Deny |
| Unregistered scheme | Deny |
| Unexpected port | Deny unless registered |
| Prefix lookalike | Deny |
| External attacker URI | Deny |


# Code Matrix

| Test | Expected |
|---|---|
| Valid unused code | Accept once |
| Reused code | Reject |
| Expired code | Reject |
| Wrong client | Reject |
| Wrong PKCE verifier | Reject |
| Missing required verifier | Reject |


# OIDC Matrix

| Control | Question |
|---|---|
| Signature | Was ID token issued by trusted signer? |
| `iss` | Is this the expected provider? |
| `aud` | Is this token intended for this client? |
| `exp` | Is the token still valid? |
| `nonce` | Does it belong to this transaction? |
| `sub` | Which provider identity authenticated? |


# Scope Matrix

| Token Scope | Endpoint | Expected |
|---|---|---|
| `orders:read` | Read order | Allow if object authorized |
| `orders:read` | Modify order | Deny |
| `orders:write` | Modify own authorized order | Policy dependent |
| No admin scope | Admin function | Deny |


# False Positive Matrix

| Observation | Interpretation |
|---|---|
| Client ID visible | Usually expected |
| Discovery endpoint public | Usually expected |
| JWKS public | Usually expected |
| SPA has no client secret | Expected for public client |
| OAuth uses redirects | Normal protocol behaviour |
| No consent screen | May be intentional |
| ID token is JWT | Normal |
| Access token is opaque | Normal |
| `state` absent | Requires flow analysis |
| Implicit flow present | Legacy design, not proof of exploitability |


# Evidence Matrix

| Observation | Supported Conclusion |
|---|---|
| Mismatched state accepted with security impact | Transaction binding weakness |
| Wrong PKCE verifier accepted | PKCE enforcement failure |
| Unregistered attacker URI receives response | Redirect URI validation failure |
| Same code redeemed twice | Code replay weakness |
| Read-only token performs write | Scope enforcement failure |
| ID token accepted by API | Token-purpose validation failure |
| External identity linked without sufficient proof | Account-linking weakness |


# Remediation Matrix

| Weakness | Primary Control |
|---|---|
| Missing transaction binding | State/session correlation |
| Code interception risk | PKCE S256 |
| Weak redirect validation | Strict registered URI matching |
| Code replay | Single-use authorization codes |
| Scope bypass | Resource-server scope enforcement |
| Token confusion | Audience/type/purpose validation |
| Weak account linking | Trusted issuer + subject + proof |
| Client secret exposure | Rotate and server-side storage |
| Token leakage | Safer transport/storage |
| Broad permissions | Least-privilege scopes |


# Authorization Code Flow Model

```text
                USER
                  |
                  v
               CLIENT
                  |
                  v
       AUTHORIZATION REQUEST
                  |
                  v
        AUTHORIZATION SERVER
                  |
                  v
          USER AUTHENTICATES
                  |
                  v
         AUTHORIZATION CODE
                  |
                  v
               CLIENT
                  |
                  v
            TOKEN ENDPOINT
                  |
                  v
            ACCESS TOKEN
                  |
                  v
          RESOURCE SERVER
```


# PKCE Model

```text
              CLIENT
                |
                v
         CODE VERIFIER
                |
                v
       SHA256 + BASE64URL
                |
                v
        CODE CHALLENGE
                |
                v
      AUTHORIZATION REQUEST
                |
                v
      AUTHORIZATION CODE
                |
                v
     TOKEN REQUEST + VERIFIER
                |
                v
          SERVER COMPARES
                |
         +------+------+
         |             |
       MATCH        NO MATCH
         |             |
         v             v
       TOKEN         REJECT
```


# State Model

```text
             CLIENT SESSION
                   |
                   v
            GENERATE STATE
                   |
                   v
       AUTHORIZATION REQUEST
                   |
                   v
       AUTHORIZATION SERVER
                   |
                   v
       CALLBACK + RETURNED STATE
                   |
                   v
              COMPARE
                   |
           +-------+-------+
           |               |
         MATCH          MISMATCH
           |               |
           v               v
        CONTINUE         REJECT
```


# OIDC Identity Model

```text
             OPENID PROVIDER
                    |
                    v
                 ID TOKEN
                    |
                    v
            VERIFY SIGNATURE
                    |
                    v
             VERIFY ISSUER
                    |
                    v
            VERIFY AUDIENCE
                    |
                    v
             VERIFY LIFETIME
                    |
                    v
              VERIFY NONCE
                    |
                    v
              ISSUER + SUB
                    |
                    v
             LOCAL IDENTITY
```


# Resource Authorization Model

```text
              ACCESS TOKEN
                    |
                    v
             TOKEN VALIDATION
                    |
                    v
             CORRECT AUDIENCE
                    |
                    v
              REQUIRED SCOPE
                    |
                    v
              USER / TENANT
                    |
                    v
          OBJECT AUTHORIZATION
                    |
                    v
                 RESOURCE
```


# Account Linking Model

```text
           EXTERNAL PROVIDER
                   |
                   v
             TRUSTED ISSUER
                   |
                   v
             STABLE SUBJECT
                   |
                   v
           FEDERATED IDENTITY
                   |
                   v
          LINKING AUTHORIZATION
                   |
                   v
             LOCAL ACCOUNT
```


# Source Review Model

```text
                LOGIN START
                    |
                    v
          AUTHORIZATION REQUEST
                    |
                    v
              STATE / PKCE
                    |
                    v
          AUTHORIZATION SERVER
                    |
                    v
                 CALLBACK
                    |
                    v
             STATE VALIDATION
                    |
                    v
              CODE EXCHANGE
                    |
                    v
             TOKEN VALIDATION
                    |
                    v
             IDENTITY MAPPING
                    |
                    v
              SESSION CREATE
                    |
                    v
               AUTHORIZATION
```


# Practical Validation Model

```text
Map OAuth Architecture
        |
        v
Capture Successful Flow
        |
        v
Identify Trust Boundaries
        |
        v
Review Redirect URI
        |
        v
Review State
        |
        v
Review PKCE
        |
        v
Review Authorization Code
        |
        v
Review Token Validation
        |
        v
Review OIDC Identity Mapping
        |
        v
Review Scope / Authorization
        |
        v
Review Token Lifecycle
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

OAuth testing is not:

```text
Find /authorize
      |
      v
Change random parameters
      |
      v
Report OAuth issue
```

It is:

```text
UNDERSTAND ACTORS
       |
       v
UNDERSTAND FLOW
       |
       v
IDENTIFY TRUST BOUNDARIES
       |
       v
CONTROL ONE VARIABLE
       |
       v
OBSERVE SECURITY DECISION
       |
       v
VERIFY IMPACT
```

For every OAuth or OIDC implementation ask:

```text
Which authorization server is trusted?

Which client is involved?

Is the client public or confidential?

Which flow is being used?

Which redirect URIs are registered?

How strictly are redirect URIs validated?

Can an untrusted origin receive authorization material?

Is the authorization request bound to the browser session?

Is state used and actually validated?

Is PKCE used?

Is S256 used?

Is the verifier required?

Can PKCE be removed or downgraded?

Are authorization codes short-lived?

Are authorization codes single-use?

Are codes bound to the correct client?

Are codes bound to the redirect URI where required?

Which scopes are requested?

Which scopes are granted?

Are scopes actually enforced by APIs?

Does object-level authorization still occur?

Are tenant boundaries enforced?

Which token types are issued?

Can an ID token be used as an access token?

Can a token for one API be used against another?

Is issuer validation correct?

Is audience validation correct?

Are token lifetimes enforced?

Are refresh tokens protected?

Are refresh tokens rotated where appropriate?

Can refresh-token replay be detected?

Are tokens exposed in URLs?

Are tokens exposed in logs?

Are client secrets exposed?

Is a public client incorrectly expected to keep a secret?

Does OIDC use a stable issuer and subject for identity?

Is nonce validated where required?

How are external identities linked to local accounts?

Can an attacker influence account linking?

What happens after logout?

What happens after account disablement?

What happens after unlinking an identity provider?

Are callback errors handled safely?

Can forwarded headers influence callback URLs?

Are old development redirect URIs still registered?

Are abandoned callback domains registered?

Do mobile and SPA clients use appropriate public-client protections?

Do all resource servers validate the same token consistently?

Have findings been demonstrated using controlled accounts?

Has actual impact been verified rather than inferred?

Have access tokens, refresh tokens, codes and secrets been redacted from evidence?
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Authentication and Session Testing Cheatsheet](authentication-session-testing.md)
- [Authorization, IDOR and BOLA Cheatsheet](authorization-access-control.md)
- [JWT Security Testing Cheatsheet](jwt.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

Useful deeper notes include:

[OAuth 2.0 and OpenID Connect Security](../web/oauth-oidc.md)

[JSON Web Token Security](../web/jwt.md)

[Authentication Testing](../web/authentication.md)

[Authorisation Testing](../web/authorisation.md)

[API Security](../web/api-security.md)


# References

- [RFC 6749 - The OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749){ target="_blank" rel="noopener noreferrer" }
- [RFC 9700 - Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700){ target="_blank" rel="noopener noreferrer" }
- [RFC 7636 - Proof Key for Code Exchange by OAuth Public Clients](https://www.rfc-editor.org/rfc/rfc7636){ target="_blank" rel="noopener noreferrer" }
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html){ target="_blank" rel="noopener noreferrer" }
- [OpenID Connect Discovery 1.0](https://openid.net/specs/openid-connect-discovery-1_0.html){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy - OAuth Authentication](https://portswigger.net/web-security/oauth){ target="_blank" rel="noopener noreferrer" }
- [OWASP OAuth2 Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Map the flow before attacking it"

    OAuth and OIDC requests contain many interdependent values. Capture one complete successful authentication flow first and identify the client, authorization server, redirect URI, state, PKCE values, scopes and token types before changing anything.


!!! tip "Change one parameter at a time"

    Testing `state`, `redirect_uri`, PKCE, scopes and token handling independently makes it much easier to identify which security control failed and to produce defensible evidence.


!!! tip "Separate protocol layers"

    A secure OAuth authorization flow does not guarantee secure application authorization. After validating the token, the resource server must still enforce scopes, roles, object ownership and tenant boundaries.


!!! tip "Use controlled identities"

    Two dedicated test accounts are especially useful for login CSRF, federated account linking and identity-mapping tests because they allow the complete security consequence to be demonstrated without involving unrelated users.


!!! warning "Public metadata is not a vulnerability"

    Client IDs, OIDC discovery metadata and public JWKS documents are normally designed to be visible. Focus on whether the application establishes and enforces the correct trust relationships rather than treating public protocol metadata as sensitive information.


!!! warning "Protect OAuth credentials in evidence"

    Authorization codes, access tokens, refresh tokens, ID tokens and confidential-client secrets may all provide security-sensitive access. Redact them from reports, screenshots and shared logs.
