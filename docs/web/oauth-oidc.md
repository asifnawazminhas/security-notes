# OAuth 2.0 and OpenID Connect Security

OAuth 2.0 and OpenID Connect are widely used for delegated authorisation, authentication and Single Sign-On.

They commonly appear as:

```text
Sign in with Google
Sign in with Microsoft
Sign in with GitHub
Continue with SSO
Connect your account
Authorise application
```

OAuth and OpenID Connect involve several systems exchanging security-sensitive values.

A simplified OAuth flow looks like:

```text
User
 ↓
Client Application
 ↓
Authorization Server
 ↓
User Authenticates / Grants Access
 ↓
Authorization Code
 ↓
Client Application
 ↓
Token Endpoint
 ↓
Access Token
 ↓
Resource Server
```

OpenID Connect adds an identity layer:

```text
OAuth 2.0
   +
Identity Information
   ↓
OpenID Connect
```

During an authorised assessment, the objective is not simply to inspect tokens.

The important questions are:

```text
Which OAuth or OIDC flow is used?

Who is the Authorization Server?

Which application is the client?

How is redirect_uri validated?

Is state correctly implemented?

Is nonce correctly implemented?

Is PKCE used where appropriate?

Which scopes can be requested?

How are authorization codes protected?

How are access tokens handled?

How are refresh tokens handled?

How are ID tokens validated?

How are accounts linked?

Can authentication or authorisation boundaries be bypassed?
```

!!! warning "Authorised Security Testing"
    OAuth and OpenID Connect testing can involve multiple organisations and domains. The application's identity provider, third-party OAuth provider or external SSO platform may not automatically be included in the assessment scope. Confirm the authorised scope before actively testing external identity infrastructure.

---

# OAuth vs OpenID Connect

A useful distinction is:

```text
OAuth 2.0
    ↓
Authorisation
```

and:

```text
OpenID Connect
    ↓
Authentication / Identity
```

OAuth answers questions such as:

```text
Can Application A access Resource B on behalf of the user?
```

OIDC adds identity information allowing the client to establish:

```text
Who authenticated?
```

---

# OAuth Terminology

Understanding the roles is essential.

## Resource Owner

Usually:

```text
The User
```

The resource owner controls the protected resource.

---

## Client

The application requesting access.

Example:

```text
target.example
```

---

## Authorization Server

The server responsible for authenticating the user and issuing authorization codes or tokens.

Examples may include identity platforms or an organisation's own identity service.

---

## Resource Server

The server hosting the protected resource.

Example:

```text
API
```

---

# OAuth Architecture

A simplified architecture:

```text
Resource Owner
     ↓
   Client
     ↓
Authorization Server
     ↓
Access Token
     ↓
Resource Server
```

A real application may look like:

```text
Browser
   ↓
target.example
   ↓
Identity Provider
   ↓
Authorization Code
   ↓
target.example
   ↓
Token Exchange
   ↓
API
```

---

# OAuth Endpoint Discovery

Common endpoints may include:

```text
/authorize
/oauth/authorize
/oauth2/authorize
/token
/oauth/token
/oauth2/token
/revoke
/introspect
/userinfo
/logout
```

OIDC may expose:

```text
/.well-known/openid-configuration
```

This endpoint can reveal much of the identity architecture.

---

# OIDC Discovery

Look for:

```text
/.well-known/openid-configuration
```

Example:

```bash
curl -s https://identity.example/.well-known/openid-configuration
```

The response may contain:

```json
{
    "issuer": "https://identity.example",
    "authorization_endpoint": "https://identity.example/authorize",
    "token_endpoint": "https://identity.example/token",
    "userinfo_endpoint": "https://identity.example/userinfo",
    "jwks_uri": "https://identity.example/.well-known/jwks.json"
}
```

Potentially useful fields include:

```text
issuer
authorization_endpoint
token_endpoint
userinfo_endpoint
jwks_uri
registration_endpoint
scopes_supported
response_types_supported
response_modes_supported
grant_types_supported
token_endpoint_auth_methods_supported
code_challenge_methods_supported
```

Discovery documents are often intentionally public.

Their presence alone is not a vulnerability.

---

# OAuth Discovery Through Burp Suite

Start by using the application's normal login process.

```text
Browser
   ↓
Burp Proxy
   ↓
Login / SSO
   ↓
HTTP History
```

Search for:

```text
authorize
oauth
oauth2
openid
callback
code=
state=
client_id=
redirect_uri=
scope=
response_type=
nonce=
code_challenge=
```

Do not modify the flow immediately.

First capture a complete successful authentication.

---

# Map the Entire Flow

Record:

```text
1. Initial application request

2. Redirect to Authorization Server

3. Authorization request

4. Authentication

5. Consent if applicable

6. Redirect back to application

7. Authorization code

8. Token exchange

9. UserInfo request if used

10. Application session creation
```

The full chain matters.

---

# Example Authorization Request

A typical request might look like:

```http
GET /authorize?
client_id=CLIENT123&
redirect_uri=https%3A%2F%2Ftarget.example%2Fcallback&
response_type=code&
scope=openid%20profile%20email&
state=RANDOMVALUE&
nonce=RANDOMNONCE&
code_challenge=CHALLENGE&
code_challenge_method=S256 HTTP/1.1
Host: identity.example
```

Important parameters include:

```text
client_id
redirect_uri
response_type
scope
state
nonce
code_challenge
code_challenge_method
```

---

# Parameter Inventory

Create a table:

| Parameter | Purpose | Security Question |
|---|---|---|
| `client_id` | Identifies client | Can another client be substituted? |
| `redirect_uri` | Callback destination | Is it strictly validated? |
| `response_type` | Requested response | Are unsafe flows enabled? |
| `scope` | Requested permissions | Can excessive scopes be requested? |
| `state` | Request correlation / CSRF protection | Is it required and validated? |
| `nonce` | OIDC replay protection | Is it validated? |
| `code_challenge` | PKCE challenge | Is PKCE correctly enforced? |

---

# Authorization Code Flow

The Authorization Code Flow commonly works as:

```text
Browser
   ↓
Client
   ↓
Authorization Endpoint
   ↓
User Authenticates
   ↓
Authorization Code
   ↓
Client Callback
   ↓
Server-Side Token Exchange
   ↓
Access Token
```

Example callback:

```http
GET /callback?code=AUTHORIZATION_CODE&state=RANDOMVALUE HTTP/1.1
Host: target.example
```

The authorization code should normally be:

```text
Short lived
Single use
Bound to the client
Bound to the redirect URI
Protected by PKCE where appropriate
```

---

# OAuth Testing Mindset

Do not begin with random parameter mutation.

Think about the trust relationships:

```text
Browser
   ↓
Client
   ↓
Authorization Server
   ↓
Client Callback
   ↓
Token Endpoint
   ↓
Resource Server
```

At each boundary ask:

```text
What proves the identity of the participant?

What binds this response to the original request?

What prevents interception?

What prevents replay?

What controls the redirect destination?

What permissions are being granted?
```

---

# redirect_uri

`redirect_uri` is one of the most security-sensitive OAuth parameters.

Example:

```text
redirect_uri=https://target.example/oauth/callback
```

After successful authorisation, the Authorization Server may redirect:

```text
https://target.example/oauth/callback?code=...
```

If redirect URI validation is weak, sensitive OAuth responses may be sent somewhere unintended.

---

# Redirect URI Validation

A secure implementation should normally compare the requested callback against explicitly registered redirect URIs.

Conceptually:

```text
Requested redirect_uri
        ↓
Registered Redirect URIs
        ↓
Exact / Safe Comparison
        ↓
Allow or Reject
```

Avoid insecure validation based only on:

```text
Starts with trusted string
Contains trusted domain
Ends with expected text
Substring match
```

---

# Testing redirect_uri

Start with the legitimate value:

```text
https://target.example/oauth/callback
```

Then understand the provider's validation behaviour using controlled destinations where permitted.

Interesting areas may include:

```text
Host
Subdomain
Port
Path
Query string
Fragment handling
URL encoding
Duplicate parameters
```

The objective is to determine whether the Authorization Server can be made to send security-sensitive data to an unintended location.

---

# Redirect URI and Open Redirects

A registered callback may itself contain an open redirect.

Conceptually:

```text
Authorization Server
       ↓
Trusted Callback
       ↓
Open Redirect
       ↓
Unexpected Destination
```

For example, an application might register:

```text
https://target.example/callback
```

while another application path provides redirection functionality.

OAuth testing should therefore be connected to open redirect testing.

---

# state

The `state` parameter is commonly used to correlate an OAuth response with the browser session that initiated the flow and to protect against CSRF-style attacks.

Example:

```text
state=7hK29Pq...
```

The application should:

```text
Generate unpredictable state
        ↓
Associate it with initiating browser/session
        ↓
Send it to Authorization Server
        ↓
Receive it on callback
        ↓
Compare expected vs returned value
        ↓
Continue only if valid
```

---

# Testing state

Establish the baseline.

Then determine what happens when:

```text
state is removed
state is empty
state is modified
state is reused
state belongs to another controlled session
```

Expected behaviour:

```text
Authentication flow rejected
```

where `state` is required for the flow.

---

# OAuth Login CSRF

One OAuth-related risk occurs when the callback is not correctly tied to the browser that initiated authentication.

Conceptually:

```text
Attacker Initiates OAuth Login
          ↓
Authorization Response Generated
          ↓
Victim Browser Processes Response
          ↓
Victim Session Linked to Wrong Identity
```

The exact impact depends on how the application uses OAuth.

Correct request correlation is therefore important.

---

# nonce

OpenID Connect commonly uses:

```text
nonce
```

A nonce helps bind an ID token to the authentication request and mitigate replay.

Flow:

```text
Client Generates Nonce
        ↓
Authorization Request
        ↓
Identity Provider
        ↓
ID Token Contains Nonce
        ↓
Client Validates Nonce
```

---

# Testing nonce

Where OIDC uses nonce, determine whether:

```text
nonce is generated
nonce is unpredictable
nonce is included in the request
returned nonce is validated
old nonce values can be reused
incorrect nonce values are rejected
```

Do not assume `state` and `nonce` perform the same function.

---

# PKCE

Proof Key for Code Exchange is abbreviated:

```text
PKCE
```

PKCE strengthens the Authorization Code Flow by binding the token exchange to the client instance that initiated the authorization request.

The client generates:

```text
code_verifier
```

and derives:

```text
code_challenge
```

---

# PKCE Flow

```text
Client
  ↓
Generate code_verifier
  ↓
Generate code_challenge
  ↓
Authorization Request
  ↓
code_challenge
  ↓
Authorization Server
  ↓
Authorization Code
  ↓
Token Request
  ↓
code_verifier
  ↓
Authorization Server Validates
  ↓
Access Token
```

---

# PKCE Parameters

Authorization request:

```text
code_challenge=...
code_challenge_method=S256
```

Token request:

```text
code_verifier=...
```

Preferred challenge method:

```text
S256
```

---

# Why PKCE Matters

Without appropriate protections:

```text
Authorization Code
       ↓
Intercepted
       ↓
Potential Token Exchange
```

With PKCE:

```text
Authorization Code
       +
Correct code_verifier
       ↓
Token Exchange
```

The authorization code alone should not be sufficient where PKCE is enforced.

---

# Testing PKCE

During an authorised assessment determine:

```text
Is PKCE used?

Is code_challenge required?

Is S256 used?

Can code_challenge be omitted?

Can code_verifier be omitted?

Can an incorrect verifier be used?

Can a code be redeemed without the original verifier?
```

Expected:

```text
Invalid verifier
      ↓
Token exchange rejected
```

---

# Authorization Code Security

Authorization codes should generally be:

```text
Short lived
Single use
Bound to client
Bound to redirect URI
Protected against interception
```

A useful controlled test is determining whether the same code can be redeemed twice.

Expected:

```text
First redemption
      ↓
Success

Second redemption
      ↓
Rejected
```

Do not repeatedly test production login flows unnecessarily.

---

# Authorization Code Leakage

Authorization codes may accidentally leak through:

```text
Browser history
Application logs
Proxy logs
Referer headers
Analytics
Error pages
Third-party resources
```

Review what happens immediately after the callback.

A secure application should minimise the lifetime and exposure of authorization codes.

---

# Access Tokens

Access tokens authorise access to protected resources.

Example:

```http
Authorization: Bearer ACCESS_TOKEN
```

Questions include:

```text
What API accepts the token?

What scopes does it contain?

When does it expire?

Is it audience restricted?

Can it be replayed?

Where is it stored?

Is it exposed to JavaScript?

Does logout revoke it?

Can another application use it?
```

---

# Bearer Tokens

A bearer token generally means:

```text
Possession = Authority
```

Anyone possessing a valid bearer token may potentially use it within its intended scope.

Therefore bearer tokens should be protected from:

```text
Logging
URLs
Referer leakage
Browser storage exposure
XSS
Insecure transport
Unnecessary disclosure
```

---

# Refresh Tokens

Refresh tokens allow clients to obtain new access tokens.

Conceptually:

```text
Refresh Token
      ↓
Token Endpoint
      ↓
New Access Token
```

Refresh tokens are typically longer-lived and therefore particularly sensitive.

Assess:

```text
Storage
Rotation
Expiration
Revocation
Reuse detection
Client binding
Scope
```

---

# Refresh Token Rotation

A modern implementation may rotate refresh tokens:

```text
Refresh Token A
      ↓
Used
      ↓
Access Token
+
Refresh Token B
```

Then:

```text
Refresh Token A
      ↓
Reused
      ↓
Rejected
```

Depending on the implementation, reuse may trigger broader session invalidation.

---

# ID Tokens

OpenID Connect introduces the:

```text
ID Token
```

which is commonly a JWT containing identity claims.

Example claims:

```json
{
    "iss": "https://identity.example",
    "sub": "123456",
    "aud": "CLIENT123",
    "exp": 1780000000,
    "iat": 1779999000,
    "nonce": "RANDOMNONCE",
    "email": "user@example.com"
}
```

---

# ID Token Validation

The relying application should validate relevant properties such as:

```text
Signature
Issuer
Audience
Expiration
Nonce
Authorised algorithm
```

Conceptually:

```text
ID Token
   ↓
Verify Signature
   ↓
Verify iss
   ↓
Verify aud
   ↓
Verify exp
   ↓
Verify nonce
   ↓
Use Identity
```

---

# issuer

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

The application should ensure the token came from the expected issuer.

---

# audience

The:

```text
aud
```

claim identifies the intended audience.

Example:

```json
{
    "aud": "CLIENT123"
}
```

A token issued for another client should not automatically be accepted.

---

# subject

The:

```text
sub
```

claim identifies the authenticated subject.

Example:

```json
{
    "sub": "248289761001"
}
```

Applications should generally use stable provider identifiers appropriately rather than relying solely on mutable display information.

---

# Email Claims

Applications sometimes use:

```text
email
```

as the primary account-linking identifier.

Questions include:

```text
Is the email verified?

Who controls the email claim?

Can the value change?

Can two providers assert the same email?

How does account linking work?
```

Authentication security can fail even when token cryptography is correct if account linking is unsafe.

---

# JWKS

OIDC providers commonly publish signing keys using JSON Web Key Sets.

Discovery may reveal:

```text
jwks_uri
```

Example:

```text
https://identity.example/.well-known/jwks.json
```

The keys allow applications to verify signed tokens.

Publishing public verification keys is normal and not a vulnerability.

---

# JWT Security

Because ID tokens are frequently JWTs, OAuth/OIDC testing overlaps with JWT security.

Important areas include:

```text
Signature validation
Algorithm validation
Issuer validation
Audience validation
Expiration
Key selection
Claim validation
```

JWT testing should focus on actual implementation behaviour rather than merely decoding the token.

---

# Scope

OAuth scopes define requested permissions.

Example:

```text
scope=openid profile email
```

Other applications may use:

```text
read
write
files.read
files.write
calendar.read
admin
```

Ask:

```text
Which scopes are required?

Which scopes can be requested?

Does the resource server enforce them?

Can a token obtain more permissions than intended?
```

---

# Scope Escalation

Suppose the normal application requests:

```text
scope=openid profile
```

Determine whether requesting an additional authorised test scope changes behaviour.

For example:

```text
scope=openid profile email
```

The key questions are:

```text
Does the Authorization Server permit it?

Does consent reflect it?

Does the client need it?

Does the API enforce scope boundaries?
```

---

# Scope Enforcement

A token may contain:

```text
read:profile
```

but not:

```text
write:profile
```

The API must enforce this.

Conceptually:

```text
Access Token
      ↓
Scope
      ↓
Requested API Operation
      ↓
Allow / Deny
```

The UI is not a security boundary.

---

# Client ID

The:

```text
client_id
```

identifies the OAuth client.

Example:

```text
client_id=abc123
```

Client IDs are generally not secrets.

They frequently appear in browser-visible requests.

Do not report an exposed client ID as a secret simply because it is visible.

---

# Client Secret

A:

```text
client_secret
```

is different.

Confidential clients may use a client secret when authenticating to the token endpoint.

Client secrets should not be embedded in:

```text
Browser JavaScript
Mobile applications
Public repositories
Client-side configuration
```

because those environments cannot reliably keep a static secret confidential.

---

# Public vs Confidential Clients

Conceptually:

```text
Confidential Client
       ↓
Can securely maintain credentials
```

Examples may include:

```text
Server-side web application
Backend service
```

Public clients:

```text
Browser-based application
Native application
Mobile application
```

cannot safely rely on an embedded static client secret remaining confidential.

PKCE is especially important for public clients.

---

# OAuth Grant Types

OAuth deployments may support different grants.

Examples include:

```text
Authorization Code
Client Credentials
Device Authorization
Refresh Token
```

Older deployments may also expose legacy flows.

During testing, identify which flows are actually enabled.

---

# Authorization Code Flow

This is the primary flow to expect for many modern interactive applications.

```text
User
 ↓
Authorization Endpoint
 ↓
Authorization Code
 ↓
Token Endpoint
 ↓
Access Token
```

Combined with:

```text
PKCE
```

it provides strong protection for modern browser and native application scenarios when implemented correctly.

---

# Implicit Flow

Older applications may use:

```text
response_type=token
```

causing access tokens to be returned through the browser front channel.

Modern OAuth guidance generally favours Authorization Code Flow with PKCE instead.

If an older implicit flow is present, understand why it remains enabled and how tokens are exposed.

---

# Client Credentials

Machine-to-machine communication may use:

```text
grant_type=client_credentials
```

Conceptually:

```text
Service
   ↓
Client Authentication
   ↓
Token Endpoint
   ↓
Access Token
```

There is normally no interactive user.

Assess:

```text
Credential storage
Token scope
Token audience
Secret rotation
Permissions
```

---

# Device Authorization

Devices with limited input capabilities may use a device flow.

Conceptually:

```text
Device
  ↓
Device Code
  ↓
User Opens Verification Page
  ↓
User Authenticates
  ↓
Device Polls
  ↓
Access Token
```

Testing should consider:

```text
Code entropy
Expiration
User confirmation
Polling behaviour
Account binding
```

---

# Account Linking

Account linking is one of the most important OAuth/OIDC business logic areas.

Example:

```text
Existing Local Account
       +
Google Identity
       ↓
Linked Account
```

or:

```text
Existing Account
       +
Microsoft Identity
       ↓
Linked Account
```

Ask:

```text
How is ownership of both accounts proven?

Can an OAuth identity be linked without reauthentication?

Is email alone used?

Does the provider verify the email?

Can a user link an identity belonging to someone else?

Can an attacker pre-link an identity?
```

---

# Account Linking Threat Model

A secure process might require:

```text
Authenticated Existing User
        ↓
Reauthentication
        ↓
OAuth Login
        ↓
Validated Provider Identity
        ↓
Explicit Confirmation
        ↓
Link
```

Weak implementations may skip important ownership checks.

---

# Pre-Account Takeover Patterns

Some applications allow:

```text
Local Registration
```

and:

```text
OAuth Registration
```

to create or merge accounts based on email.

Threat model:

```text
How does the application decide these identities represent the same person?
```

Potential issues can occur when:

```text
Email ownership is not verified
Provider claims are trusted incorrectly
Accounts are merged automatically
Existing sessions are not reauthenticated
```

---

# Login vs Account Linking

These should be treated as separate workflows.

```text
Login with OAuth
```

means:

```text
Authenticate existing identity
```

while:

```text
Link OAuth Provider
```

means:

```text
Add another authentication method to an existing account
```

The second operation is security-sensitive and should normally require strong verification.

---

# Multiple Identity Providers

Applications may support:

```text
Google
Microsoft
GitHub
Corporate SSO
Local login
```

Create an identity matrix:

| Login Method | Identifier | Verified? | Account Mapping |
|---|---|---:|---|
| Local | Email | Yes | Local account |
| Provider A | `sub` | Yes | OAuth identity |
| Provider B | `sub` | Yes | OAuth identity |
| Corporate SSO | Subject | Yes | Organisation account |

Then understand how identities are merged.

---

# OAuth and CSRF

OAuth involves browser redirects and therefore requires protection against request confusion and login CSRF.

Important mechanisms may include:

```text
state
PKCE
nonce
SameSite cookies
Session binding
```

Do not assume one mechanism replaces all others.

---

# OAuth and Open Redirects

Search the application for redirection functionality.

Parameters may include:

```text
redirect
redirect_uri
return
returnUrl
return_to
next
continue
callback
url
```

A redirect weakness may become more significant when it participates in an authentication flow.

Refer to your open redirect testing methodology where applicable.

---

# OAuth and XSS

OAuth flows can become significantly more dangerous when combined with XSS.

For example:

```text
OAuth Callback
     ↓
Sensitive Values
     ↓
Browser
     ↓
XSS
```

XSS may expose:

```text
Tokens
Codes
Application session data
Account linking workflows
```

OAuth testing should therefore consider the application's broader browser security posture.

---

# OAuth and CORS

Token or user information endpoints may expose CORS policies.

Inspect:

```http
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
```

The security impact depends on:

```text
Endpoint
Authentication method
Allowed origin
Sensitive response data
```

Do not report permissive CORS without demonstrating meaningful exposure.

---

# OAuth and Browser Storage

Determine whether access tokens are stored in:

```text
Memory
Cookies
localStorage
sessionStorage
IndexedDB
```

Each design has different trade-offs.

For example:

```text
localStorage
     ↓
Accessible to JavaScript
     ↓
XSS becomes particularly relevant
```

while cookies require careful handling of:

```text
HttpOnly
Secure
SameSite
CSRF
```

---

# OAuth Callback Endpoint

The callback endpoint deserves careful review.

Example:

```text
/oauth/callback
```

Check:

```text
Required parameters
state validation
Error handling
Code handling
Redirect behaviour
Session creation
Account mapping
Logging
```

Malformed callbacks may also reveal useful implementation details.

---

# OAuth Error Responses

OAuth errors may appear as:

```text
error
error_description
error_uri
```

Example:

```text
?error=access_denied
```

Review whether errors reveal:

```text
Internal paths
Stack traces
Client secrets
Tokens
Provider configuration
Sensitive account details
```

---

# Duplicate Parameters

OAuth requests pass through multiple components:

```text
Browser
Proxy
Client
Authorization Server
Framework
```

Duplicate parameters may be interpreted differently.

Examples:

```text
redirect_uri=A&redirect_uri=B
```

or:

```text
state=A&state=B
```

Different components may select:

```text
First value
Last value
All values
```

Testing parameter parsing inconsistencies can be relevant where multiple systems validate and process the request differently.

---

# URL Encoding

OAuth parameters are frequently URL encoded.

Example:

```text
redirect_uri=https%3A%2F%2Ftarget.example%2Fcallback
```

When assessing validation, consider how many components perform decoding.

Conceptually:

```text
Input
 ↓
Proxy Decode
 ↓
Framework Decode
 ↓
Application Validation
 ↓
Redirect
```

Security controls should operate on a canonical and correctly parsed representation.

---

# OAuth Session Binding

A secure login flow should bind:

```text
Browser Session
      ↓
OAuth Request
      ↓
OAuth Response
      ↓
Resulting Application Session
```

The callback should not be accepted merely because it contains a valid authorization code.

The application must know that the response corresponds to the authentication attempt initiated by that browser session.

---

# Session Fixation Considerations

After successful authentication, inspect whether the application:

```text
Rotates session identifier
Creates a fresh authenticated session
Invalidates pre-authentication state where appropriate
```

OAuth does not replace normal session management requirements.

---

# Logout

OAuth/OIDC logout can involve several layers:

```text
Application Session
Identity Provider Session
Access Token
Refresh Token
Other Connected Applications
```

Logging out of:

```text
target.example
```

does not necessarily mean the user has logged out of the identity provider.

Determine the application's intended behaviour.

---

# Token Revocation

OAuth may provide a revocation endpoint.

Conceptually:

```text
Token
 ↓
Revocation Endpoint
 ↓
Token Invalidated
```

Assess whether sensitive long-lived credentials can be revoked when required.

---

# Token Introspection

Some architectures use token introspection.

Conceptually:

```text
Resource Server
      ↓
Token
      ↓
Authorization Server
      ↓
Active?
Scopes?
Subject?
Audience?
```

Introspection endpoints should themselves be appropriately protected.

---

# OAuth Business Logic

Do not restrict OAuth testing to protocol parameters.

Authentication is also a business workflow.

Ask:

```text
Can accounts be linked incorrectly?

Can an identity be changed after linking?

Can an unverified email create a trusted account?

Can deleted accounts be recreated through SSO?

Can disabled local accounts still authenticate through OAuth?

Can users switch organisations unexpectedly?

Can an OAuth identity inherit the wrong role?
```

---

# Organisation and Tenant Mapping

Enterprise SSO frequently involves tenants or organisations.

Conceptually:

```text
Identity Provider
      ↓
User Identity
      ↓
Organisation Mapping
      ↓
Application Role
```

Test:

```text
How is tenant determined?

Can tenant identifiers be manipulated?

Does email domain determine organisation?

Is domain ownership verified?

Can external identities enter internal tenants?

Are roles derived from trusted claims?
```

---

# Role Mapping

OIDC claims may influence application roles.

Example:

```json
{
    "groups": [
        "users"
    ]
}
```

or:

```json
{
    "role": "employee"
}
```

Ask:

```text
Which claim determines role?

Who controls the claim?

Is the issuer trusted?

Is the value validated?

What happens when the claim disappears?

Are old roles removed?
```

---

# Group Mapping

Enterprise applications may map identity-provider groups into application permissions.

Conceptually:

```text
OIDC Group
   ↓
Application Mapping
   ↓
Role
   ↓
Permissions
```

Review:

```text
Group names
Group IDs
Case sensitivity
Default role
Unknown groups
Removed groups
Nested groups
```

---

# Default Roles

A newly authenticated OAuth/OIDC user may receive a default role.

Ask:

```text
What is the default?

Can the user select it?

Can registration parameters influence it?

Does invitation state influence it?

Can the user join the wrong organisation?
```

---

# Invitation Flows

OAuth authentication is often combined with invitations.

Example:

```text
Admin Invites user@example.com
        ↓
User Opens Invitation
        ↓
Sign in with Provider
        ↓
Account Added to Organisation
```

Threat model:

```text
Is the authenticated identity the invited identity?

Is email verified?

Is invitation single use?

Does invitation expire?

Can invitation be transferred?

Can organisation ID be modified?
```

---

# OAuth Testing With Two Accounts

Two controlled accounts are extremely useful.

Create:

```text
Account A
Account B
```

Where permitted, use different identity-provider identities.

Then compare:

```text
state
nonce
authorization code
session cookie
sub
email
account mapping
organisation
role
```

This helps identify which values are actually bound to which account.

---

# Burp Repeater

Burp Repeater is useful for controlled OAuth testing.

Good candidates include:

```text
Authorization requests
Callback requests
Application endpoints
UserInfo requests
Token-related application requests
```

Be careful when manually replaying token endpoint requests because authorization codes are usually single use.

---

# Burp Sequencer

Burp Sequencer may help analyse application-generated security tokens where entropy analysis is relevant.

Examples might include:

```text
state
Application CSRF tokens
Session identifiers
```

Do not assume that every OAuth value needs statistical analysis.

First determine who generates the value and what security property it provides.

---

# Burp Decoder

Burp Decoder can help inspect:

```text
URL encoding
Base64
JWT components
Encoded OAuth parameters
```

Remember:

```text
Decode ≠ Decrypt
```

JWT headers and payloads are commonly Base64URL encoded and readable without the signing key.

---

# Burp Extensions

Useful Burp extensions may include tools for:

```text
JWT inspection
OAuth flow analysis
Authorization testing
Token handling
```

Extensions can assist with visibility, but OAuth testing still requires understanding the protocol flow and application-specific account logic.

---

# Browser Developer Tools

Developer Tools can reveal:

```text
Redirect chain
Cookies
localStorage
sessionStorage
Network requests
Callback behaviour
JavaScript token handling
```

Inspect:

```text
Network
Application / Storage
Console
```

where appropriate.

---

# curl

OIDC discovery:

```bash
curl -s \
  https://identity.example/.well-known/openid-configuration
```

JWKS:

```bash
curl -s \
  https://identity.example/.well-known/jwks.json
```

UserInfo where you have an authorised test token:

```bash
curl -i \
  -H "Authorization: Bearer TEST_ACCESS_TOKEN" \
  https://identity.example/userinfo
```

Do not send real production tokens to third-party token analysis websites.

---

# Token Handling Rule

Treat tokens like credentials.

Avoid:

```text
Posting them online
Sharing screenshots containing complete tokens
Committing them to Git
Including active tokens in reports
Copying them into third-party websites
```

Redact sensitive values.

For example:

```text
eyJhbGciOi...REDACTED...abc123
```

---

# OAuth Threat Model

For each OAuth implementation document:

```text
CLIENT:
target.example

AUTHORIZATION SERVER:
identity.example

RESOURCE SERVER:
api.target.example

FLOW:
Authorization Code + PKCE

CLIENT TYPE:
Public / Confidential

REDIRECT URI:
https://target.example/callback

SCOPES:
openid profile email

STATE:
Present

NONCE:
Present

PKCE:
S256

TOKEN STORAGE:
HTTP-only cookie / memory / etc.

ACCOUNT MAPPING:
OIDC sub

ROLE MAPPING:
Application database

LOGOUT:
Application logout

IDENTITY PROVIDERS:
Provider A
Provider B
```

Then derive tests from the architecture.

---

# OAuth Testing Checklist

## Discovery

```text
[ ] Identify OAuth/OIDC functionality
[ ] Identify Authorization Server
[ ] Identify Resource Server
[ ] Identify client
[ ] Identify flow
[ ] Identify client type
[ ] Find OIDC discovery document
[ ] Find authorization endpoint
[ ] Find token endpoint
[ ] Find UserInfo endpoint
[ ] Find JWKS
```

## Authorization Request

```text
[ ] Record client_id
[ ] Record redirect_uri
[ ] Record response_type
[ ] Record scope
[ ] Record state
[ ] Record nonce
[ ] Record PKCE parameters
```

## Redirect URI

```text
[ ] Establish legitimate redirect
[ ] Review registered callback behaviour
[ ] Test controlled path variations where permitted
[ ] Review subdomain handling
[ ] Review port handling
[ ] Review encoding
[ ] Review duplicate parameters
[ ] Check interaction with open redirects
```

## State

```text
[ ] Confirm state exists
[ ] Remove state
[ ] Modify state
[ ] Use empty state
[ ] Replay state
[ ] Compare between controlled sessions
```

## Nonce

```text
[ ] Confirm nonce exists
[ ] Determine where it is validated
[ ] Test incorrect nonce where possible
[ ] Test replay behaviour
```

## PKCE

```text
[ ] Confirm code_challenge exists
[ ] Confirm S256
[ ] Confirm code_verifier is required
[ ] Test invalid verifier
[ ] Test missing verifier
[ ] Confirm code is bound to verifier
```

## Authorization Code

```text
[ ] Confirm short lifetime
[ ] Confirm single use
[ ] Review leakage
[ ] Review logging
[ ] Review callback handling
```

## Tokens

```text
[ ] Review access token
[ ] Review token expiration
[ ] Review audience
[ ] Review scopes
[ ] Review storage
[ ] Review refresh tokens
[ ] Review revocation
```

## ID Token

```text
[ ] Validate expected issuer
[ ] Validate expected audience
[ ] Validate expiration
[ ] Review subject
[ ] Review nonce
[ ] Review identity claims
```

## Account Linking

```text
[ ] Test linking workflow
[ ] Confirm reauthentication
[ ] Confirm ownership verification
[ ] Review email-based linking
[ ] Review unlinking
[ ] Review multiple providers
```

## Organisation / Tenant

```text
[ ] Review tenant mapping
[ ] Review email domain mapping
[ ] Review role mapping
[ ] Review group mapping
[ ] Review invitation flow
[ ] Review default role
```

## Session

```text
[ ] Review session creation
[ ] Review session rotation
[ ] Review logout
[ ] Review session invalidation
[ ] Review OAuth token vs application session lifetime
```

---

# OAuth Testing Decision Tree

```text
OAuth / OIDC Found
        ↓
Which Flow?
        ↓
Authorization Code?
        ↓
Is PKCE Used?
        ↓
Who Is Authorization Server?
        ↓
What Is redirect_uri?
        ↓
Is It Strictly Validated?
        ↓
Is state Present?
        ↓
Is state Bound to Session?
        ↓
OIDC?
        ↓
Is nonce Used?
        ↓
How Is ID Token Validated?
        ↓
Which Identity Claim Maps Account?
        ↓
Which Scopes Are Granted?
        ↓
How Are Roles Mapped?
        ↓
How Are Accounts Linked?
        ↓
How Are Tokens Stored?
        ↓
What Happens at Logout?
```

---

# Five Questions for Every OAuth Flow

For every OAuth/OIDC implementation ask:

```text
1. Where can the Authorization Server send the response?

2. What binds the response to the browser that initiated the flow?

3. What prevents an intercepted authorization code from being redeemed?

4. How does the application determine which user authenticated?

5. How does the application determine what that user may access?
```

Then ask:

```text
6. How are accounts linked?

7. Which scopes are granted?

8. How are tokens stored?

9. What happens when authentication state changes?

10. Which external identity systems are trusted?
```

---

# Evidence Collection

For OAuth/OIDC findings record:

```text
Client
Authorization Server
Resource Server
OAuth flow
Affected endpoint
Authorization request
Callback request
Relevant parameters
Authenticated account
Expected behaviour
Observed behaviour
Security impact
```

Redact:

```text
Authorization codes
Access tokens
Refresh tokens
Session cookies
Client secrets
```

unless a specifically sanitised value is required as evidence.

---

# Example Redirect URI Finding

```text
Finding:
OAuth Redirect URI Validation Allows Unintended Callback Destination

Client:
target.example

Authorization Endpoint:
https://identity.example/authorize

Expected:
OAuth responses should only be sent to registered callback locations.

Observed:
A controlled unintended redirect destination was accepted.

Impact:
OAuth security-sensitive response data may be redirected outside the intended callback boundary.
```

The report should document the exact demonstrated behaviour without exposing active tokens.

---

# Example State Finding

```text
Finding:
OAuth Callback Does Not Validate State

Expected:
The callback should only accept responses corresponding to an authentication request initiated by the current browser session.

Observed:
The application accepted the OAuth callback when the state parameter was missing or invalid.

Impact:
The OAuth login flow is not correctly bound to the initiating browser session, potentially enabling login CSRF or account confusion depending on the application workflow.
```

---

# Example Account Linking Finding

```text
Finding:
OAuth Account Linking Does Not Require Reauthentication

Expected:
Adding a new authentication method should require strong verification of the existing account.

Observed:
An authenticated session could link an additional OAuth identity without reauthentication.

Impact:
An attacker with temporary access to an authenticated session may be able to establish a persistent alternative login method.
```

---

# Reporting

Prefer specific titles such as:

```text
OAuth Callback Does Not Validate State

OAuth Redirect URI Validation Allows Unintended Redirect Destinations

OAuth Authorization Code Can Be Reused

PKCE Is Not Enforced During Authorization Code Exchange

OIDC ID Token Audience Is Not Properly Validated

OAuth Account Linking Does Not Require Reauthentication

Unverified OAuth Email Claim Is Used for Account Linking

OAuth Identity Is Mapped to Incorrect Organisation

OAuth Access Token Exposed in Browser Storage
```

Avoid vague titles such as:

```text
OAuth Vulnerability
```

---

# Remediation

OAuth and OIDC security depends on correctly implementing the protocol as a complete system.

Do not attempt to secure individual parameters while ignoring the overall flow.

---

# Redirect URI Protection

Use explicitly registered redirect URIs.

Conceptually:

```text
Client Registration
      ↓
Known Redirect URIs
      ↓
Authorization Request
      ↓
Exact Safe Match
      ↓
Redirect
```

Avoid overly permissive wildcard behaviour unless specifically required and securely constrained.

---

# State Protection

Generate:

```text
Cryptographically unpredictable state
```

Bind it to:

```text
Initiating browser session
```

Validate it before accepting the callback.

Reject:

```text
Missing
Incorrect
Expired
Unexpected
```

values.

---

# PKCE Protection

For modern Authorization Code flows:

```text
PKCE
+
S256
```

should be used where appropriate.

The token endpoint should reject authorization code redemption without the correct verifier.

---

# ID Token Validation

Validate:

```text
Signature
Issuer
Audience
Expiration
Nonce
Relevant claims
```

using a well-maintained OIDC library rather than custom token parsing logic.

---

# Token Protection

Protect tokens using:

```text
TLS
Short lifetimes
Minimal scopes
Secure storage
Rotation
Revocation
Logging controls
```

Avoid placing sensitive bearer tokens in URLs.

---

# Account Linking Protection

Require:

```text
Authenticated session
        ↓
Reauthentication where appropriate
        ↓
Proof of new identity
        ↓
Explicit confirmation
        ↓
Link
```

Do not automatically merge accounts based only on an untrusted or unverified identifier.

---

# Role and Tenant Protection

Identity claims should not automatically become application permissions without validation.

Conceptually:

```text
Trusted Identity
      ↓
Validated Claims
      ↓
Server-Side Mapping
      ↓
Application Role
      ↓
Authorisation
```

---

# OAuth Quick Reference

```text
DISCOVERY

/.well-known/openid-configuration
/authorize
/token
/userinfo
/revoke
/introspect
JWKS
```

```text
AUTHORIZATION REQUEST

client_id
redirect_uri
response_type
scope
state
nonce
code_challenge
code_challenge_method
```

```text
CALLBACK

code
state
error
```

```text
PKCE

code_verifier
code_challenge
S256
```

```text
OIDC

ID Token
iss
sub
aud
exp
nonce
JWKS
```

```text
TOKENS

Access Token
Refresh Token
ID Token
```

```text
BUSINESS LOGIC

Account linking
Identity mapping
Tenant mapping
Role mapping
Invitations
Default roles
Logout
```

---

# Recommended OAuth/OIDC Workflow

```text
Use Application Normally
        ↓
Capture Complete Login
        ↓
Identify OAuth/OIDC
        ↓
Identify Authorization Server
        ↓
Identify Client
        ↓
Identify Resource Server
        ↓
Discover OIDC Metadata
        ↓
Identify Flow
        ↓
Map Authorization Request
        ↓
Review redirect_uri
        ↓
Review state
        ↓
Review nonce
        ↓
Review PKCE
        ↓
Review Authorization Code
        ↓
Review Token Exchange
        ↓
Review Access Token
        ↓
Review ID Token
        ↓
Review Scopes
        ↓
Review Account Mapping
        ↓
Review Account Linking
        ↓
Review Tenant / Role Mapping
        ↓
Review Session Creation
        ↓
Review Logout
        ↓
Create Threat Model
        ↓
Perform Controlled Tests
        ↓
Collect Evidence
        ↓
Report
```

---

# Tools

Useful tools include:

```text
Burp Suite
Burp Proxy
Burp Repeater
Burp Decoder
Burp Sequencer
Browser Developer Tools
curl
JWT inspection tools
OIDC discovery documents
Application documentation
```

The most important tool remains:

```text
Understanding the complete authentication flow
```

OAuth weaknesses are often caused by trust or business logic errors rather than cryptographic failure.

---

# References

## PortSwigger Web Security Academy: OAuth 2.0 Authentication Vulnerabilities

https://portswigger.net/web-security/oauth

Excellent practical material covering OAuth security testing and deliberately vulnerable labs.

---

## PortSwigger: OAuth Grant Types

https://portswigger.net/web-security/oauth/grant-types

Useful for understanding how different OAuth flows operate.

---

## PortSwigger: OAuth Authentication Vulnerabilities

https://portswigger.net/web-security/oauth

Useful for understanding vulnerabilities involving:

```text
redirect_uri
state
OAuth account linking
Token handling
```

---

## OAuth 2.0 Security Best Current Practice

https://datatracker.ietf.org/doc/html/rfc9700

Current security guidance for OAuth 2.0 deployments.

---

## OAuth 2.0 Authorization Framework

https://datatracker.ietf.org/doc/html/rfc6749

The core OAuth 2.0 specification.

---

## Proof Key for Code Exchange

https://datatracker.ietf.org/doc/html/rfc7636

Defines PKCE and the relationship between:

```text
code_verifier
code_challenge
```

---

## OpenID Connect Core

https://openid.net/specs/openid-connect-core-1_0.html

The core OpenID Connect specification.

---

## OpenID Connect Discovery

https://openid.net/specs/openid-connect-discovery-1_0.html

Defines OIDC discovery and:

```text
/.well-known/openid-configuration
```

---

## OWASP OAuth 2.0 Protocol Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html

Useful defensive guidance for implementing OAuth securely.

---

## OWASP Authentication Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

Useful broader guidance for authentication controls surrounding OAuth and OIDC.

---

## OWASP Session Management Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

Relevant because successful OAuth authentication normally results in an application session.

---

# Final OAuth/OIDC Testing Model

```text
                        USER
                          ↓
                       CLIENT
                          ↓
               AUTHORIZATION REQUEST
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
   redirect_uri         state             PKCE
        ↓                 ↓                 ↓
        └─────────────────┼─────────────────┘
                          ↓
                AUTHORIZATION SERVER
                          ↓
                     USER LOGIN
                          ↓
                  AUTHORIZATION CODE
                          ↓
                      CALLBACK
                          ↓
             Validate Request Binding
                          ↓
                    TOKEN EXCHANGE
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
  Access Token         ID Token       Refresh Token
        ↓                 ↓                 ↓
      Scope        Identity Claims       Rotation
        ↓                 ↓                 ↓
        └─────────────────┼─────────────────┘
                          ↓
                  APPLICATION SESSION
                          ↓
             ACCOUNT / IDENTITY MAPPING
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
 Account Linking     Tenant Mapping     Role Mapping
        ↓                 ↓                 ↓
        └─────────────────┼─────────────────┘
                          ↓
                    AUTHORISATION
                          ↓
                    PROTECTED DATA
```

The key principle is:

> OAuth and OpenID Connect should be tested as complete trust workflows rather than as collections of tokens. Map who issues the identity, where responses are allowed to travel, how the browser session is bound to the authentication attempt, how authorization codes are protected, how tokens are validated, and how the resulting identity is mapped to accounts, organisations and privileges.
