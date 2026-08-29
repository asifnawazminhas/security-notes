# Authentication and Authorisation Source Code Review

Authentication and authorisation are two of the most important security boundaries to analyse during source code review.

Authentication determines:

```text
Who is making the request?
```

Authorisation determines:

```text
Is that identity permitted to perform this action
on this specific resource?
```

These controls are related but fundamentally different.

```text
Authentication
      |
      v
Identity Established
      |
      v
Authorisation
      |
      v
Permission to Perform Action
```

A common security mistake is assuming:

```text
Authenticated
    =
Authorised
```

That is incorrect.

An authenticated user may still be able to:

```text
Access another user's object
Modify another tenant's data
Call administrator functionality
Change roles or permissions
Delete protected resources
Perform actions outside their assigned privileges
```

During source code review, the objective is to understand the complete security decision path:

```text
Request
   |
   v
Authentication
   |
   v
Identity
   |
   v
Route / Handler
   |
   v
Authorisation
   |
   v
Object-Level Authorisation
   |
   v
Business Rules
   |
   v
Sensitive Operation
```

---

# Authorised Testing

Use these techniques only when reviewing applications, repositories, and environments that you are authorised to assess.

Authentication and authorisation code may expose sensitive information including:

```text
Session architecture
JWT signing configuration
OAuth client configuration
SAML configuration
Password hashing
Role mappings
Permission models
Administrative functionality
Tenant boundaries
Recovery mechanisms
API keys
Secrets
```

Handle source code and findings according to the rules of engagement.

---

# Core Security Model

A useful model is:

```text
REQUEST
   |
   v
AUTHENTICATION
   |
   v
IDENTITY
   |
   v
ROUTE
   |
   v
AUTHORISATION
   |
   v
OBJECT AUTHORISATION
   |
   v
BUSINESS AUTHORISATION
   |
   v
SENSITIVE OPERATION
```

Each layer answers a different question.

---

# Authentication

Authentication establishes identity.

Examples:

```text
Username + password
Session cookie
JWT
API key
OAuth/OIDC
SAML
Client certificate
Service token
```

The result is normally some representation of identity:

```text
user
principal
subject
claims
session
security context
request.user
current_user
```

---

# Authorisation

Authorisation decides whether the identity may perform an operation.

Examples:

```text
Administrator role required
Permission required
Ownership required
Tenant membership required
Resource relationship required
Feature entitlement required
```

---

# Object-Level Authorisation

Object-level authorisation answers:

```text
Can this user access THIS object?
```

Example:

```text
GET /api/documents/123
```

Authentication may establish:

```text
User = Alice
```

but the application must still determine:

```text
Does document 123 belong to Alice?

Can Alice access document 123?

Does Alice's tenant own document 123?
```

---

# Function-Level Authorisation

Function-level authorisation answers:

```text
Can this user perform THIS operation?
```

Example:

```text
POST /admin/users/123/disable
```

The user may be authenticated but should perhaps require:

```text
Administrator
```

or:

```text
user:disable permission
```

---

# Property-Level Authorisation

Applications may correctly protect an object while failing to protect sensitive properties.

Example:

```json
{
  "displayName": "Alice",
  "role": "admin",
  "isVerified": true
}
```

The user may be allowed to modify:

```text
displayName
```

but not:

```text
role
isVerified
```

This overlaps with:

```text
Mass Assignment
Broken Object Property Level Authorisation
```

---

# Tenant-Level Authorisation

Multi-tenant applications introduce another security boundary.

```text
User
  |
  v
Tenant
  |
  v
Object
```

A secure lookup often needs to constrain both:

```text
User / Permission
        +
Tenant
        +
Object
```

rather than retrieving an object globally by identifier.

---

# Business-Level Authorisation

Some restrictions are business rules rather than simple roles.

Examples:

```text
Only the account owner can close an account

Only the invoice approver can approve payment

A user cannot approve their own request

A refund requires a completed transaction

An invitation can only be accepted by the intended recipient
```

These controls may not appear in framework security configuration.

Manual review is essential.

---

# Start With the Security Architecture

Before searching individual checks, identify the application's security architecture.

Look for:

```text
Authentication middleware
Authorisation middleware
Security filters
Guards
Interceptors
Decorators
Annotations
Policies
Permission classes
Base controllers
Security services
Identity providers
```

Build:

```text
Request
   |
   v
Security Middleware
   |
   v
Authentication
   |
   v
Identity Context
   |
   v
Controller
   |
   v
Authorisation
   |
   v
Service
```

---

# Authentication Inventory

Identify all authentication mechanisms.

Example:

| Mechanism | Used For | Identity |
|---|---|---|
| Session cookie | Browser | User |
| JWT | API | User |
| API key | Integration | Service |
| OAuth | Browser login | User |
| mTLS | Internal API | Service |

Multiple mechanisms frequently coexist.

---

# Authentication Entry Points

Search for:

```text
login
signin
authenticate
session
token
refresh
logout
password
reset
forgot
mfa
2fa
otp
oauth
oidc
saml
```

Using ripgrep:

```bash
rg -n -i \
'login|signin|authenticate|session|token|refresh|logout|password|reset|mfa|2fa|otp|oauth|oidc|saml' \
.
```

This is discovery only.

Matches require manual triage.

---

# Visual Studio Code Workflow

Open the repository:

```bash
code .
```

Use:

```text
Ctrl + Shift + F
```

for global search.

Useful searches:

```text
Authorize
AllowAnonymous
permitAll
hasRole
hasAuthority
permission_classes
login_required
current_user
req.user
isAuthenticated
UseGuards
roles
permissions
owner
tenant
```

Then use:

```text
F12
```

for Go to Definition and:

```text
Shift + F12
```

for Find All References.

---

# Follow the Identity

After authentication, identify how identity moves through the application.

Examples:

```text
HttpContext.User
SecurityContext
Principal
Authentication
request.user
current_user
req.user
session.user
JWT claims
```

Trace:

```text
Authentication
      |
      v
Identity Object
      |
      v
Controller
      |
      v
Service
      |
      v
Authorisation Decision
```

---

# Authentication Source-to-Sink Analysis

Authentication can itself be analysed as a source-to-sink flow.

```text
Credentials / Token
        |
        v
Parser
        |
        v
Verification
        |
        v
Identity Mapping
        |
        v
Session / Security Context
```

Ask:

```text
What proves identity?

What values are trusted?

What verification occurs?

How is identity mapped?

What security context is created?
```

---

# Password Authentication

Typical flow:

```text
Username
   +
Password
   |
   v
Account Lookup
   |
   v
Password Verification
   |
   v
Account State Check
   |
   v
MFA
   |
   v
Session Creation
```

Review each stage.

---

# Password Storage

Search for:

```text
bcrypt
argon2
scrypt
PBKDF2
PasswordHasher
BCryptPasswordEncoder
hashpw
checkpw
```

Also search potentially dangerous primitives:

```bash
rg -n -i \
'md5|sha1|sha256|sha512|MessageDigest|CreateHash|hashlib' \
.
```

The presence of a general hash function does not prove insecure password storage.

Determine what the hash is used for.

---

# Password Verification

Identify:

```text
Password lookup
Hash verification
Account lock status
Disabled account status
Password expiration
MFA requirement
```

Example:

```text
Password Correct
      |
      v
Account Disabled?
      |
      v
MFA Required?
      |
      v
Session
```

Do not inspect password comparison in isolation.

---

# Login Failure Behaviour

Review:

```text
Error messages
Timing differences
Account lockout
Rate limiting
Audit logging
Failed attempt tracking
```

Potential issues may include:

```text
Username enumeration
Missing rate limiting
Lockout weaknesses
Information disclosure
```

These require runtime validation where appropriate.

---

# Session Authentication

Typical flow:

```text
Session Cookie
      |
      v
Session Lookup
      |
      v
Session Validation
      |
      v
User Identity
```

Review:

```text
Session generation
Session rotation
Expiration
Logout invalidation
Concurrent sessions
Privilege-change handling
Cookie configuration
```

---

# Session Fixation

Trace session creation around authentication.

Potentially safer model:

```text
Anonymous Session
       |
       v
Login
       |
       v
Rotate Session Identifier
       |
       v
Authenticated Session
```

Look for whether session identifiers are regenerated after authentication or major privilege changes.

---

# Logout

Trace:

```text
Logout Request
      |
      v
Server Session Invalidated?
      |
      v
Cookie Removed?
      |
      v
Tokens Revoked?
```

Deleting a browser cookie alone may not invalidate a server-side session.

---

# JWT Authentication

Typical flow:

```text
JWT
 |
 v
Parse
 |
 v
Signature Verification
 |
 v
Claims Validation
 |
 v
Identity Mapping
 |
 v
Authorisation
```

Search:

```bash
rg -n -i \
'jwt|jsonwebtoken|JwtSecurityToken|JwtDecoder|JwtEncoder|decode\(|verify\(' \
.
```

---

# JWT Verification

Review:

```text
Signature verification
Allowed algorithms
Signing key
Issuer
Audience
Expiration
Not-before
Subject
Key selection
Claims mapping
```

Do not assume:

```text
Token parsed
```

means:

```text
Token securely verified
```

---

# JWT Claims

Sensitive claims may include:

```text
sub
role
roles
permissions
tenant
scope
groups
admin
```

Trace how claims influence authorisation.

```text
JWT Claim
    |
    v
Identity
    |
    v
Role / Permission
    |
    v
Sensitive Operation
```

---

# JWT Authorisation Mistakes

Review for patterns such as:

```text
Role accepted directly from untrusted data
Missing issuer validation
Missing audience validation
Incorrect key selection
Claims trusted before verification
Sensitive custom claims mapped incorrectly
```

A suspicious configuration is a candidate for further analysis, not automatic proof of exploitability.

---

# API Keys

Search:

```bash
rg -n -i \
'api.?key|x-api-key|apikey' \
.
```

Trace:

```text
Header
  |
  v
API Key Lookup
  |
  v
Identity / Service
  |
  v
Permissions
```

Review:

```text
Storage
Comparison
Rotation
Scopes
Logging
Revocation
```

---

# OAuth 2.0 / OpenID Connect

Typical authentication flow:

```text
User
 |
 v
Authorization Request
 |
 v
Identity Provider
 |
 v
Callback
 |
 v
Authorization Code
 |
 v
Token Exchange
 |
 v
Token Validation
 |
 v
Identity Mapping
 |
 v
Session
```

Search:

```bash
rg -n -i \
'oauth|openid|oidc|authorization.?code|redirect_uri|state|nonce|pkce|code_verifier|code_challenge' \
.
```

---

# OAuth / OIDC Review

Review:

```text
state validation
nonce validation
PKCE
redirect URI handling
token validation
issuer
audience
identity mapping
account linking
session creation
```

---

# Account Linking

Pay special attention to:

```text
External identity
      |
      v
Email / Subject
      |
      v
Existing Local Account
```

Ask:

```text
What uniquely identifies the external user?

Is email trusted?

Is email verified?

Can identities from different providers collide?

Can an attacker link themselves to another account?
```

---

# SAML

Typical flow:

```text
SAMLResponse
     |
     v
XML Parsing
     |
     v
Signature Validation
     |
     v
Assertion Validation
     |
     v
Identity Mapping
     |
     v
Session
```

Search:

```bash
rg -n -i \
'saml|SAMLResponse|assertion|acs|metadata|single.?sign.?on|single.?logout' \
.
```

Review:

```text
Signature validation
Assertion conditions
Audience
Recipient
Destination
Issuer
Time conditions
Identity mapping
Session creation
```

---

# MFA

Typical flow:

```text
Primary Authentication
        |
        v
MFA Required?
        |
        v
Challenge
        |
        v
Verification
        |
        v
Authenticated Session
```

Search:

```bash
rg -n -i \
'mfa|2fa|totp|otp|authenticator|recovery.?code|backup.?code' \
.
```

---

# MFA State

Identify how the application remembers:

```text
MFA pending
MFA completed
MFA enrolled
Trusted device
Recovery authentication
```

The state may exist in:

```text
Session
JWT claim
Database
Cookie
Temporary token
```

---

# MFA Bypass Review

Map every route capable of creating a fully authenticated session.

```text
Password Login
OAuth Login
SAML Login
Password Reset
Recovery Code
Magic Link
Administrative Impersonation
Remember Device
```

Then determine whether MFA is consistently enforced.

---

# Password Reset

Typical flow:

```text
Reset Request
     |
     v
Account Lookup
     |
     v
Token Generation
     |
     v
Token Delivery
     |
     v
Token Verification
     |
     v
Password Change
     |
     v
Token Invalidation
```

Search:

```bash
rg -n -i \
'forgot.?password|reset.?password|password.?reset|reset.?token' \
.
```

---

# Password Reset Review

Review:

```text
Token entropy
Token expiration
Single use
Account binding
Invalidation
Host/header handling
Rate limiting
Session invalidation
MFA interaction
```

---

# Magic Links

Search:

```bash
rg -n -i \
'magic.?link|passwordless|login.?link' \
.
```

Trace:

```text
Email
  |
  v
Token
  |
  v
Callback
  |
  v
Identity
  |
  v
Session
```

Review the token similarly to password-reset tokens.

---

# Authorisation Architecture

After authentication is understood, identify the authorisation model.

Common models include:

```text
RBAC
ABAC
ACL
Ownership
Tenant isolation
Scopes
Claims
Policies
Permissions
Relationship-based access
```

Applications frequently combine several.

---

# RBAC

Role-Based Access Control:

```text
User
 |
 v
Role
 |
 v
Permissions
```

Example:

```text
Alice
 |
 v
Administrator
 |
 v
user:delete
```

Review:

```text
Role assignment
Role hierarchy
Role checks
Default roles
Role modification
```

---

# ABAC

Attribute-Based Access Control may consider:

```text
User department
Resource classification
Tenant
Location
Time
Account status
Ownership
```

Conceptually:

```text
Subject Attributes
       +
Resource Attributes
       +
Environment
       |
       v
Policy Decision
```

---

# ACL

Access Control Lists may associate permissions directly with resources.

```text
Document
 |
 +-- Alice -> Read
 +-- Bob   -> Read/Write
 +-- Admin -> Full Control
```

Review both:

```text
ACL creation
ACL enforcement
```

---

# Ownership

A common pattern:

```text
Resource.ownerId == currentUser.id
```

Search:

```bash
rg -n -i \
'owner|ownerId|userId|createdBy|belongsTo|tenantId|organisationId|organizationId' \
.
```

These are discovery indicators only.

---

# ASP.NET Core Authentication

Common security components include:

```text
AddAuthentication
AddAuthorization
UseAuthentication
UseAuthorization
[Authorize]
[AllowAnonymous]
RequireAuthorization
Policies
Claims
Roles
```

Search:

```bash
rg -n \
'AddAuthentication|AddAuthorization|UseAuthentication|UseAuthorization|\[Authorize|\[AllowAnonymous|RequireAuthorization|RequireClaim|RequireRole' \
-g '*.cs' \
.
```

---

# ASP.NET Identity

Search:

```bash
rg -n \
'UserManager|SignInManager|RoleManager|PasswordHasher|IdentityUser|IdentityRole' \
-g '*.cs' \
.
```

Trace:

```text
Login
 |
 v
SignInManager
 |
 v
Identity
 |
 v
ClaimsPrincipal
 |
 v
HttpContext.User
```

---

# ASP.NET Authorisation

Example:

```csharp
[Authorize(Roles = "Admin")]
[HttpDelete("{id}")]
public IActionResult DeleteUser(
    int id
)
{
    ...
}
```

This provides function-level authorisation.

Still review object-level or business-level checks where relevant.

---

# ASP.NET Policies

Example:

```csharp
[Authorize(
    Policy = "CanManageUsers"
)]
```

Follow:

```text
CanManageUsers
```

to its policy definition.

Search:

```bash
rg -n \
'AddPolicy|RequireClaim|RequireRole|IAuthorizationRequirement|AuthorizationHandler' \
-g '*.cs' \
.
```

---

# ASP.NET Object Authorisation

Example:

```csharp
var document =
    repository.Get(id);

if (
    document.OwnerId !=
    currentUserId
)
{
    return Forbid();
}
```

Trace where:

```text
currentUserId
```

originates and whether the comparison applies to every sensitive action.

---

# ASP.NET Resource-Based Authorisation

Look for:

```text
IAuthorizationService
AuthorizeAsync
AuthorizationHandler
```

Example:

```csharp
await authorizationService.AuthorizeAsync(
    User,
    document,
    "CanEditDocument"
);
```

Review the corresponding handler.

---

# Java / Spring Security

Search:

```bash
rg -n \
'SecurityFilterChain|HttpSecurity|authorizeHttpRequests|requestMatchers|permitAll|authenticated|hasRole|hasAuthority|@PreAuthorize|@PostAuthorize|@Secured|@RolesAllowed' \
-g '*.java' \
-g '*.kt' \
.
```

---

# Spring Route Security

Example:

```java
http
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/admin/**")
        .hasRole("ADMIN")
        .requestMatchers("/api/**")
        .authenticated()
    );
```

Create a security map:

```text
/admin/** -> ADMIN
/api/**   -> Authenticated
```

Compare it with the route inventory.

---

# Spring Method Security

Example:

```java
@PreAuthorize(
    "hasRole('ADMIN')"
)
public void deleteUser(
    Long id
) {
    ...
}
```

Search:

```bash
rg -n \
'@PreAuthorize|@PostAuthorize|@PreFilter|@PostFilter|@Secured|@RolesAllowed' \
-g '*.java' \
.
```

---

# Spring Expression Authorisation

Example:

```java
@PreAuthorize(
    "#userId == authentication.principal.id"
)
```

Review:

```text
Expression
Principal
Object ID
Service behaviour
```

Complex expressions deserve manual inspection.

---

# Spring Security Context

Search:

```bash
rg -n \
'SecurityContextHolder|getAuthentication\(|Principal|Authentication' \
-g '*.java' \
.
```

Trace how identity is obtained.

---

# PHP / Laravel Authentication

Search:

```bash
rg -n \
'Auth::|auth\(\)|middleware\(["'\'']auth|->middleware\(["'\'']auth|Gate::|authorize\(|can\(' \
-g '*.php' \
.
```

---

# Laravel Middleware

Example:

```php
Route::middleware(
    'auth'
)->group(function () {
    ...
});
```

Map which routes inherit the middleware.

---

# Laravel Gates

Example:

```php
Gate::authorize(
    'update-post',
    $post
);
```

Follow the gate definition.

Search:

```bash
rg -n \
'Gate::define|Gate::authorize|Gate::allows|Gate::denies' \
-g '*.php' \
.
```

---

# Laravel Policies

Search:

```bash
rg -n \
'Policy|authorize\(|can\(|cannot\(' \
-g '*.php' \
.
```

Review methods such as:

```text
view
create
update
delete
restore
forceDelete
```

---

# PHP Direct Authorisation

Legacy PHP may implement checks manually.

Example:

```php
if ($_SESSION['role'] !== 'admin') {
    http_response_code(403);
    exit;
}
```

Search:

```bash
rg -n -i \
'\$_SESSION|role|permission|admin|user_id|owner' \
-g '*.php' \
.
```

---

# Django Authentication

Django commonly exposes:

```text
request.user
login_required
permission_required
LoginRequiredMixin
PermissionRequiredMixin
```

Search:

```bash
rg -n \
'request\.user|login_required|permission_required|LoginRequiredMixin|PermissionRequiredMixin|authenticate\(|login\(|logout\(' \
-g '*.py' \
.
```

---

# Django Authorisation

Example:

```python
@login_required
def document(request, id):

    document =
        Document.objects.get(
            id=id,
            owner=request.user
        )

    return ...
```

The query itself constrains ownership.

---

# Django Dangerous Lookup Pattern

Candidate:

```python
document =
    Document.objects.get(
        id=id
    )
```

Then:

```text
Where is ownership checked?
```

Do not report IDOR solely from the lookup.

Search the surrounding execution path.

---

# Django Permissions

Search:

```bash
rg -n \
'has_perm|has_perms|permission_required|user_passes_test|is_staff|is_superuser' \
-g '*.py' \
.
```

---

# Django REST Framework

Authentication and authorisation frequently use:

```text
authentication_classes
permission_classes
get_permissions
has_permission
has_object_permission
```

Search:

```bash
rg -n \
'authentication_classes|permission_classes|get_permissions|has_permission|has_object_permission|IsAuthenticated|AllowAny|IsAdminUser' \
-g '*.py' \
.
```

---

# DRF Object-Level Permissions

Pay particular attention to:

```python
def has_object_permission(
    self,
    request,
    view,
    obj
):
    ...
```

But also verify that the framework path actually invokes object permission checks for the relevant operation.

---

# DRF Queryset Filtering

Object isolation may occur through:

```python
def get_queryset(self):

    return Document.objects.filter(
        owner=self.request.user
    )
```

This may be a meaningful object-level security control.

Review all alternate access paths.

---

# Flask Authentication

Flask security is frequently implemented through extensions or custom decorators.

Search:

```bash
rg -n \
'login_required|current_user|before_request|jwt_required|roles_required|permission|session\[' \
-g '*.py' \
.
```

---

# Flask-Login

Common identity:

```text
current_user
```

Example:

```python
@login_required
def profile():
    return ...
```

This proves authentication enforcement at the decorator level, not necessarily object-level authorisation.

---

# Flask Object Authorisation

Example:

```python
document =
    Document.query.get(id)

if (
    document.user_id !=
    current_user.id
):
    abort(403)
```

Trace all routes using the same document service.

---

# Node.js / Express Authentication

Common patterns:

```text
req.user
req.session
authenticate middleware
JWT middleware
Passport
Custom middleware
```

Search:

```bash
rg -n \
'req\.user|req\.session|passport|authenticate|isAuthenticated|requireAuth|verifyToken|jwt\.verify' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Express Middleware Chain

Example:

```javascript
router.delete(
    "/users/:id",
    authenticate,
    requireAdmin,
    deleteUser
);
```

Map:

```text
Route
  |
  v
authenticate
  |
  v
requireAdmin
  |
  v
deleteUser
```

---

# Express Middleware Ordering

Compare:

```javascript
app.use(
    authenticate
);

app.use(
    "/api",
    router
);
```

with:

```javascript
app.use(
    "/api",
    router
);

app.use(
    authenticate
);
```

Ordering may affect security behaviour.

Confirm framework/runtime semantics before reporting.

---

# Express Object Authorisation

Candidate:

```javascript
const document =
    await Document.findById(
        req.params.id
    );

return res.json(document);
```

Ask:

```text
Where is ownership or tenant access checked?
```

---

# NestJS Authentication

Search:

```bash
rg -n \
'@UseGuards|AuthGuard|RolesGuard|@Roles|CanActivate|ExecutionContext' \
-g '*.ts' \
.
```

---

# NestJS Guards

Example:

```typescript
@UseGuards(
    JwtAuthGuard,
    RolesGuard
)
@Roles("admin")
@Delete(":id")
deleteUser() {
    ...
}
```

Trace guard implementation.

---

# Client-Side Authorisation

Client-side checks are not server-side security boundaries.

Example:

```javascript
if (
    currentUser.role === "admin"
) {
    showDeleteButton();
}
```

This controls UI behaviour.

It does not prove:

```text
DELETE /api/users/{id}
```

is protected.

Always find the server-side check.

---

# Hidden Buttons

A hidden administrator button is not authorisation.

```text
Frontend
   |
   v
Hide Button
```

must be backed by:

```text
Server
  |
  v
Permission Check
```

---

# GraphQL Authentication

GraphQL may authenticate:

```text
At HTTP middleware
In GraphQL context
At resolver level
Through directives
```

Search:

```bash
rg -n -i \
'context|currentUser|user|auth|permission|guard|directive' \
-g '*.js' \
-g '*.ts' \
-g '*.py' \
-g '*.java' \
-g '*.cs' \
.
```

Manual triage is required.

---

# GraphQL Authorisation

Map each sensitive resolver:

```text
Mutation
   |
   v
Resolver
   |
   v
Identity
   |
   v
Permission
   |
   v
Object
```

Example:

```text
deleteDocument(id)
       |
       v
documentResolver
       |
       v
findById(id)
       |
       v
ownership?
       |
       v
delete()
```

---

# GraphQL Field-Level Authorisation

Sensitive fields may include:

```text
email
phone
salary
internalNotes
permissions
tokens
billing
personal data
```

An object may be accessible while specific fields should not be.

---

# GraphQL Mutations

Prioritise:

```text
create
update
delete
invite
approve
transfer
reset
changeRole
changePassword
disableMFA
```

These are only review priorities.

---

# gRPC Authentication

Authentication may be implemented through:

```text
Metadata
Interceptors
mTLS
JWT
API keys
Service identity
```

Typical model:

```text
gRPC Request
     |
     v
Interceptor
     |
     v
Identity
     |
     v
RPC Handler
```

---

# gRPC Authorisation

Do not stop at the interceptor.

Review:

```text
Service-level authorisation
RPC-level authorisation
Object-level authorisation
Tenant isolation
```

Example:

```text
DeleteDocumentRequest.id
          |
          v
DeleteDocument()
          |
          v
Document Lookup
          |
          v
Ownership?
          |
          v
Delete
```

---

# WebSocket Authentication

Authentication may occur:

```text
During HTTP upgrade
Through cookie
Through query token
Through first message
Through protocol-specific authentication
```

Trace how the authenticated identity is stored for later messages.

---

# WebSocket Authorisation

Every sensitive message handler should be reviewed.

Example:

```javascript
socket.on(
    "delete-document",
    async id => {
        await documents.delete(id);
    }
);
```

Ask:

```text
Who owns the socket?

Where is the user identity?

Where is document ownership checked?
```

---

# Webhook Authentication

Webhooks usually authenticate the sender rather than a human user.

Typical controls:

```text
HMAC signature
Asymmetric signature
Shared secret
mTLS
Source authentication
```

Model:

```text
Webhook Request
      |
      v
Signature Verification
      |
      v
Event Processing
```

Review whether verification occurs before sensitive processing.

---

# Background Jobs

Authorisation may occur earlier than the worker.

Example:

```text
HTTP Request
     |
     v
Authorisation
     |
     v
Queue Job
     |
     v
Worker
```

But ask:

```text
Can another producer create jobs?

Does the job contain trusted user IDs?

Does the worker independently validate tenant boundaries?

Can stored data change between authorisation and execution?
```

---

# IDOR / BOLA

The core pattern is:

```text
Attacker-Controlled Identifier
            |
            v
Object Lookup
            |
            v
Authorisation?
            |
            v
Sensitive Operation
```

---

# IDOR Review Strategy

Search for identifiers:

```bash
rg -n -i \
'user.?id|account.?id|document.?id|order.?id|invoice.?id|tenant.?id|organisation.?id|organization.?id|owner.?id' \
.
```

Then identify lookups.

---

# Database Lookup Patterns

Potential examples:

```text
findById
getById
FindAsync
Single
First
get()
filter()
findOne
findByPk
```

Do not report these methods themselves.

Trace what happens after the lookup.

---

# Secure Ownership Query Pattern

Example:

```sql
SELECT *
FROM documents
WHERE id = ?
AND owner_id = ?
```

Conceptually:

```text
Attacker Object ID
       +
Authenticated User ID
       |
       v
Constrained Lookup
```

This can provide strong object-level isolation.

---

# Post-Lookup Authorisation

Another valid model:

```text
Object Lookup
     |
     v
Ownership Check
     |
     v
Return Object
```

Both models may be secure if correctly implemented.

---

# Missing Ownership Check

Candidate:

```text
Route ID
   |
   v
Repository.findById(id)
   |
   v
Return
```

Compare against the application's normal pattern:

```text
Route ID
   |
   v
Repository.findById(id)
   |
   v
checkOwnership()
   |
   v
Return
```

This comparison is powerful during variant analysis.

---

# Horizontal Privilege Escalation

```text
User A
  |
  v
Object ID belonging to User B
  |
  v
Sensitive Operation
```

Examples:

```text
Read another user's profile
Download another user's document
Modify another user's order
Delete another user's resource
```

---

# Vertical Privilege Escalation

```text
Normal User
    |
    v
Administrator Function
```

Examples:

```text
Change role
Disable user
View audit logs
Modify system settings
Generate API keys
```

---

# Tenant Escape

```text
Tenant A User
      |
      v
Tenant B Object ID
      |
      v
Object Lookup
      |
      v
Sensitive Operation
```

Search for whether database queries include:

```text
tenantId
organisationId
organizationId
customerId
accountId
```

where required.

---

# Role Assignment

Role-management code deserves high priority.

Search:

```bash
rg -n -i \
'role|roles|permission|permissions|isAdmin|admin|grant|revoke' \
.
```

Review:

```text
Who can assign roles?

Can users assign their own role?

Can mass assignment modify role fields?

Can tenant administrators assign global roles?
```

---

# Mass Assignment and Authorisation

Example:

```javascript
await User.update(
    req.body,
    {
        where: {
            id: req.user.id
        }
    }
);
```

Potential sensitive fields:

```text
role
isAdmin
permissions
tenantId
verified
```

Review DTOs, allowlists, serializers, and ORM behaviour before concluding exploitability.

---

# Administrative Impersonation

Search:

```bash
rg -n -i \
'impersonat|login.?as|switch.?user|assume.?user' \
.
```

Review:

```text
Who can impersonate?

Is the action audited?

Can privileged identities be impersonated?

How is impersonation ended?

Can the impersonation state be forged?
```

---

# Security Context Switching

Applications may support:

```text
Switch tenant
Switch organisation
Assume role
Act on behalf of
Delegation
```

These are important authorisation boundaries.

---

# Sensitive Operations

Prioritise operations such as:

```text
Create administrator
Change role
Change email
Change password
Disable MFA
Generate recovery codes
Create API key
Delete user
Delete tenant
Transfer funds
Issue refund
Approve request
Change ownership
Export sensitive data
```

Use Find All References to identify every path to these operations.

---

# Reverse Authorisation Analysis

Instead of starting from routes, begin at sensitive operations.

```text
Sensitive Operation
        |
        v
Who calls it?
        |
        v
Find All References
        |
        v
Controllers / Resolvers / Workers
        |
        v
Where is authorisation?
```

This is one of the strongest techniques for finding alternate-entry-point vulnerabilities.

---

# Example

Suppose:

```java
userService.deleteUser(id);
```

is security-sensitive.

Find every caller:

```text
REST AdminController
GraphQL UserMutation
gRPC UserService
Background CleanupJob
```

Then compare controls.

```text
REST
 |
 +--> @PreAuthorize ADMIN
 |
 v
deleteUser()


GraphQL
 |
 +--> authenticated
 |
 v
deleteUser()


gRPC
 |
 +--> AdminInterceptor
 |
 v
deleteUser()
```

The GraphQL path deserves further investigation.

---

# Alternate Entry Points

The same operation may be reachable through:

```text
REST
GraphQL
gRPC
WebSocket
Admin panel
Internal API
Background worker
CLI
```

Compare security controls across all paths.

---

# Security Control Consistency Matrix

| Operation | REST | GraphQL | gRPC | WebSocket |
|---|---|---|---|---|
| Read document | Auth + owner | Auth + ? | Auth + owner | N/A |
| Delete document | Auth + owner | Auth + ? | Admin | Auth + owner |
| Change role | Admin | Admin | Admin | N/A |

Question marks become review targets.

---

# Missing Authorisation Search

Once a common security control is identified:

```text
checkPermission()
```

search for its usage:

```bash
rg -n \
'checkPermission\(' \
.
```

Then search sensitive operations that do not call it.

---

# Custom Security Helpers

Common names:

```text
authorize
authorise
checkPermission
checkAccess
canAccess
canEdit
canDelete
requireRole
requirePermission
verifyOwnership
validateTenant
```

Search:

```bash
rg -n -i \
'authori[sz]e|check.?permission|check.?access|can.?access|can.?edit|can.?delete|require.?role|require.?permission|verify.?owner|validate.?tenant' \
.
```

---

# Negative Security Pattern Analysis

Sometimes the safest code has a consistent structure.

Example:

```text
getDocument()
checkOwnership()
updateDocument()
```

Search for:

```text
getDocument()
updateDocument()
```

without:

```text
checkOwnership()
```

This is a powerful candidate-discovery technique.

---

# Security Control Bypass Through Direct Service Calls

Controllers may be protected while services are callable from alternate entry points.

Example:

```text
AdminController
      |
      v
Role Check
      |
      v
UserService.changeRole()
```

but:

```text
GraphQL Resolver
      |
      v
UserService.changeRole()
```

with no equivalent role check.

---

# Security in Controllers vs Services

If security exists only in controllers:

```text
Controller
   |
   v
Authorisation
   |
   v
Service
```

then every alternate caller must reproduce the same security check.

Security enforced closer to the sensitive operation may reduce this risk, depending on architecture.

---

# Default-Allow vs Default-Deny

Determine the application's security model.

Default deny:

```text
Everything protected
       |
       v
Explicit anonymous exceptions
```

Default allow:

```text
Everything accessible
       |
       v
Explicit protected routes
```

Default-deny models are generally easier to reason about securely.

Verify actual framework behaviour.

---

# Anonymous Exceptions

Search:

```text
AllowAnonymous
permitAll
AllowAny
public
anonymous
skipAuth
```

Examples:

```bash
rg -n -i \
'AllowAnonymous|permitAll|AllowAny|anonymous|skip.?auth|publicRoute' \
.
```

Review every exception.

But:

```text
Anonymous route
    !=
Vulnerability
```

Many routes legitimately require public access.

---

# Authentication Bypass Through Route Matching

Review security configuration against route definitions.

Example:

```text
Security:
/api/admin/** -> ADMIN
```

Actual route:

```text
/admin/api/users
```

The rule may not apply.

Do not infer bypass from visual similarity alone.

Confirm framework route matching semantics.

---

# HTTP Method Differences

Security may differ by method.

Example:

```text
GET /api/users/{id}
POST /api/users/{id}
DELETE /api/users/{id}
```

Review each separately.

A GET route may be public while DELETE should require stronger privileges.

---

# Method-Level Security

Map:

```text
Path
+
HTTP Method
```

rather than path alone.

---

# Case and Normalisation

Security components and routers may interpret paths differently.

Potential areas for careful review:

```text
Trailing slashes
Case sensitivity
URL decoding
Encoded separators
Path normalisation
Proxy rewrites
```

Do not claim bypassability without confirming actual routing behaviour.

---

# Reverse Proxy Authorisation

Some applications rely partly on:

```text
NGINX
API gateway
Ingress
Service mesh
Identity-aware proxy
```

Map:

```text
Internet
   |
   v
Gateway Authentication
   |
   v
Application
```

Then determine whether the application is reachable through another path that bypasses the gateway.

---

# Trusting Identity Headers

Search:

```bash
rg -n -i \
'x-user|x-username|x-role|x-groups|x-auth|remote-user|remote_user' \
.
```

Applications behind trusted proxies sometimes consume identity headers.

Review:

```text
Who sets the header?

Can clients supply it directly?

Does the proxy overwrite it?

Can the application be reached without the proxy?
```

---

# Tenant Headers

Similarly search:

```text
X-Tenant-ID
X-Organisation-ID
X-Account-ID
```

Trace whether tenant context is securely bound to the authenticated identity.

---

# Client-Controlled Role Headers

A pattern such as:

```text
X-Role: admin
```

deserves investigation if the application trusts it.

But determine whether trusted infrastructure injects or overwrites the value before reporting.

---

# CSRF and Authorisation

CSRF does not replace authorisation.

A request can be:

```text
Properly authorised
```

but vulnerable to:

```text
Cross-Site Request Forgery
```

Similarly, CSRF protection does not prove the user is authorised for the underlying action.

Treat the controls separately.

---

# CORS and Authorisation

CORS is not an authorisation mechanism.

```text
CORS
```

controls browser cross-origin response access.

It does not replace:

```text
Authentication
Authorisation
```

Server endpoints must enforce access independently.

---

# Rate Limiting

Authentication-related endpoints often require rate limiting.

Prioritise:

```text
Login
Password reset
MFA verification
OTP verification
Account recovery
Magic links
API key validation
```

Search:

```bash
rg -n -i \
'rate.?limit|throttle|attempt|lockout|failed.?login' \
.
```

---

# Authentication State Machines

Complex authentication should be modelled as states.

Example:

```text
Unauthenticated
      |
      v
Password Verified
      |
      v
MFA Pending
      |
      v
MFA Verified
      |
      v
Authenticated
```

Then identify routes allowed in each state.

---

# MFA State Machine Example

```text
LOGIN
  |
  v
Password Correct
  |
  +--> MFA Disabled -> Full Session
  |
  +--> MFA Enabled
            |
            v
       MFA Pending
            |
            v
       OTP Verified
            |
            v
       Full Session
```

Search for any path:

```text
MFA Pending
     |
     v
Sensitive Application
```

without completion of MFA.

---

# Password Reset State Machine

```text
Reset Requested
      |
      v
Token Issued
      |
      v
Token Presented
      |
      v
Token Validated
      |
      v
Password Changed
      |
      v
Token Invalidated
```

Look for transitions that skip expected checks.

---

# Business Authorisation State Machines

Example:

```text
Draft
  |
  v
Submitted
  |
  v
Approved
  |
  v
Paid
```

Review whether users can call later-stage operations directly.

---

# TOCTOU and Authorisation

A potential pattern:

```text
Check Permission
      |
      v
Delay / Async Boundary
      |
      v
Resource Changes
      |
      v
Sensitive Operation
```

This can matter where ownership or state can change between check and use.

---

# Cached Authorisation

Search:

```bash
rg -n -i \
'permission.*cache|role.*cache|authorization.*cache|authorisation.*cache' \
.
```

Review whether permission changes invalidate cached decisions appropriately.

---

# Revocation

Ask:

```text
What happens when:

User is disabled?
Role is removed?
Password changes?
MFA is reset?
API key is revoked?
Session is terminated?
```

Determine whether existing credentials remain valid.

---

# Privilege Changes

A session created as:

```text
Normal User
```

may later become:

```text
Administrator
```

or vice versa.

Review whether:

```text
Sessions
JWTs
Cached permissions
Refresh tokens
```

reflect changes appropriately.

---

# Implicit Trust

Watch for assumptions such as:

```text
Internal user = trusted

Authenticated user = trusted

Administrator = unrestricted

Database value = trusted

Service request = trusted
```

Each assumption should be justified by the architecture.

---

# Error Handling

Authorisation failures should not accidentally expose protected data.

Example:

```text
Load object
     |
     v
Render object
     |
     v
Check permission
```

is dangerous if rendering or logging already exposes sensitive information.

Prefer conceptual ordering:

```text
Load minimal object
     |
     v
Authorise
     |
     v
Return sensitive data
```

---

# Logging

Authentication logs may contain:

```text
Usernames
Session IDs
JWTs
Reset tokens
OTP values
Passwords
API keys
```

Search:

```bash
rg -n -i \
'log.*password|log.*token|log.*session|logger.*password|logger.*token|console\.log.*token' \
.
```

Manual inspection is required.

---

# Secrets in Authentication Code

Search for:

```text
JWT secrets
OAuth client secrets
SAML keys
API keys
Cookie secrets
Session secrets
```

Use dedicated secrets scanning as well.

Do not treat every string matching `secret` as a credential.

---

# Static Analysis

Static analysis can help discover:

```text
Anonymous endpoints
Missing authorisation
Direct object lookups
Security annotations
Role checks
Permission helpers
Authentication configuration
```

But:

```text
Static Analysis Finding
        !=
Confirmed Access Control Vulnerability
```

---

# ripgrep Workflow

Start broad:

```bash
rg -n -i \
'auth|authori[sz]|permission|role|owner|tenant|session|jwt|oauth|saml|mfa' \
.
```

Then narrow to framework-specific controls.

---

# Semgrep / OpenGrep

Structural rules can identify patterns such as:

```text
Sensitive route without expected decorator

Object lookup without common ownership helper

AllowAnonymous on sensitive controller

Direct role assignment from request body
```

These should produce review candidates.

---

# Conceptual Missing Authorisation Rule

Suppose the application normally uses:

```python
check_permission(
    current_user,
    document
)
```

A project-specific rule can search document update handlers where this expected pattern is absent.

Project-specific rules are often more valuable than generic rules for business authorisation.

---

# CodeQL

CodeQL can help trace:

```text
Request ID
    |
    v
Controller
    |
    v
Service
    |
    v
Repository Lookup
```

and identify whether common security helpers appear along related paths.

It can also help perform variant analysis across complex codebases.

---

# Static Analysis Workflow

```text
ripgrep
   |
   v
Discover Security Architecture
   |
   v
Semgrep / OpenGrep
   |
   v
Find Structural Candidates
   |
   v
CodeQL
   |
   v
Trace Complex Data Flow
   |
   v
VS Code
   |
   v
Manual Authorisation Analysis
   |
   v
Burp Suite
   |
   v
Runtime Validation
```

---

# Dynamic Validation

Once source review identifies a candidate:

```text
Source
  |
  v
Potential Missing Control
  |
  v
Burp Suite
  |
  v
Controlled Runtime Test
```

For access control, compare requests using authorised test identities with different privileges.

---

# Burp Suite Workflow

Conceptually:

```text
1. Capture a legitimate request.

2. Identify the source-code handler.

3. Determine the expected authentication.

4. Determine the expected authorisation.

5. Identify the object or sensitive operation.

6. Reproduce the request with an authorised test account.

7. Compare behaviour across permitted test roles/users.

8. Change only the relevant object or operation where allowed.

9. Confirm whether the source-code control behaves as expected.

10. Record evidence.
```

---

# IDOR Runtime Validation Model

```text
Test User A
   |
   v
Access Object A
   |
   v
Expected Success

Test User A
   |
   v
Access Object B
   |
   v
Expected Denial
```

If the second operation succeeds contrary to the intended policy, investigate the source path and impact.

---

# Role Validation Model

```text
Administrator
   |
   v
Sensitive Function
   |
   v
Expected Success

Normal User
   |
   v
Same Function
   |
   v
Expected Denial
```

---

# Do Not Test Destructive Actions Blindly

Sensitive operations may include:

```text
Delete account
Transfer money
Change production configuration
Revoke credentials
Disable MFA
Delete tenant
```

Understand the code path and use safe test data appropriate to the engagement.

---

# Variant Analysis

After confirming one access-control flaw:

```text
Confirmed Finding
       |
       v
Identify Missing Control
       |
       v
Find Normal Secure Pattern
       |
       v
Search Similar Routes
       |
       v
Search Same Service
       |
       v
Search Same Object Type
       |
       v
Search Alternate Protocols
```

---

# IDOR Variant Analysis

Known finding:

```text
GET /documents/{id}
        |
        v
findById(id)
        |
        v
No Ownership Check
```

Search for:

```text
updateDocument
deleteDocument
downloadDocument
shareDocument
exportDocument
```

and other calls to the same repository.

---

# Function-Level Variant Analysis

Known finding:

```text
GraphQL changeRole()
```

missing administrator authorisation.

Search:

```text
REST changeRole
gRPC ChangeRole
Admin controller
Internal API
UserService.changeRole()
```

---

# Find All References

If the sensitive sink is:

```text
changeRole()
```

use Visual Studio Code:

```text
Shift + F12
```

to identify all callers.

This can quickly reveal inconsistent security controls.

---

# Git History

Security regressions can be investigated through Git history.

Useful commands:

```bash
git log --all --oneline
```

Search changes:

```bash
git log -S 'Authorize' --all
```

or:

```bash
git log -S 'checkPermission' --all
```

Review why security controls were added or removed.

Do not assume an old vulnerable implementation is still reachable.

---

# Security Tests

Search for tests such as:

```text
shouldReturnForbidden
shouldRejectUnauthorised
shouldRejectUnauthorized
requiresAdmin
cannotAccessOtherUser
cannotAccessOtherTenant
```

Using:

```bash
rg -n -i \
'forbidden|unauthori[sz]ed|requires.?admin|permission|other.?user|other.?tenant' \
.
```

Tests can document expected policy.

---

# Missing Security Tests

Compare sensitive functionality against test coverage.

For example:

```text
deleteDocument
```

may have:

```text
success test
not-found test
```

but no:

```text
unauthorised-user test
```

This is useful review context, but missing tests alone are not a vulnerability.

---

# Authorisation Matrix

For complex applications, build a matrix.

| Operation | Anonymous | User | Manager | Admin |
|---|---:|---:|---:|---:|
| View own profile | No | Yes | Yes | Yes |
| View other profile | No | No | Limited | Yes |
| Update role | No | No | No | Yes |
| Delete user | No | No | No | Yes |
| Export tenant | No | No | Yes | Yes |

Then compare source code against intended policy.

---

# Object Matrix

Example:

| Actor | Own Object | Same Tenant | Other Tenant |
|---|---:|---:|---:|
| User | Read/Write | No | No |
| Manager | Read | Read | No |
| Admin | Read/Write | Read/Write | Depends |

This makes BOLA and tenant-isolation review more systematic.

---

# Authentication Review Worksheet

```text
AUTH-001

Mechanism:
Session / JWT / OAuth / SAML / API Key

Entry Point:
/login

Credential Source:
...

Verification:
...

Identity Mapping:
...

Session / Token Creation:
...

MFA:
...

Rate Limiting:
...

Account State:
...

Potential Concerns:
...

Runtime Validation:
...

Status:
Reviewed / Candidate / Confirmed
```

---

# Authorisation Review Worksheet

```text
AUTHZ-001

Entry Point:
GET /api/documents/{id}

Handler:
DocumentController.get()

Identity:
current_user

Object Identifier:
id

Object Lookup:
Document.findById(id)

Required Policy:
User must own document

Authorisation Check:
...

Tenant Check:
...

Sensitive Operation:
Return document

Alternate Entry Points:
GraphQL document(id)
gRPC GetDocument

Runtime Validation:
...

Status:
Reviewed / Candidate / Confirmed
```

---

# Access-Control Finding Evidence

Strong evidence includes:

```text
Entry point
Required privilege
Actual privilege
Identity source
Object identifier
Authorisation path
Missing or ineffective control
Sensitive operation
Runtime behaviour
Impact
```

---

# Weak Finding Description

Avoid:

```text
The endpoint may be vulnerable to IDOR because it accepts an ID.
```

An identifier alone does not prove broken access control.

---

# Stronger Finding Description

Prefer:

```text
The document identifier supplied through GET /api/documents/{id}
is passed to DocumentRepository.findById() and the returned document
is sent to the authenticated user without an ownership or tenant
authorisation check along this execution path.

Runtime testing with authorised test accounts confirmed that a user
could retrieve a document belonging to another user by supplying the
other document identifier.
```

This connects:

```text
Source
+
Missing Control
+
Sink
+
Runtime Evidence
+
Impact
```

---

# Remediation

Authorisation remediation should enforce the intended security policy at a reliable security boundary.

Potential patterns include:

```text
Centralised policies
Resource-based authorisation
Object-level permissions
Tenant-constrained queries
Explicit field allowlists
Service-layer permission checks
Default-deny routing
```

The appropriate design depends on the application architecture.

---

# Object-Level Remediation

Instead of:

```text
findById(objectId)
```

consider an architecture that enforces:

```text
findByIdAndOwner(
    objectId,
    currentUser
)
```

or:

```text
findByIdAndTenant(
    objectId,
    authorisedTenant
)
```

where appropriate.

This reduces the chance that a retrieved object escapes the intended security boundary.

---

# Centralise Repeated Security Logic

If every controller manually implements:

```text
if object.owner != current_user:
    deny
```

security inconsistencies become easier to introduce.

Where appropriate, centralise through:

```text
Policies
Permission services
Repository constraints
Framework authorisation
Resource-based authorisation
```

---

# Defence in Depth

Strong access control may include:

```text
Authentication
       +
Function-Level Authorisation
       +
Object-Level Authorisation
       +
Tenant Isolation
       +
Business Rules
       +
Audit Logging
```

No single layer should be assumed to replace all others.

---

# Retesting

After remediation:

```text
Review Code Change
      |
      v
Verify Security Control
      |
      v
Test Expected Allowed Action
      |
      v
Test Expected Denied Action
      |
      v
Test Alternate Entry Points
      |
      v
Variant Search
```

---

# Authentication Checklist

```text
[ ] All authentication mechanisms identified
[ ] Login flow traced
[ ] Identity creation traced
[ ] Password verification reviewed
[ ] Password storage reviewed
[ ] Account state checks reviewed
[ ] Session creation reviewed
[ ] Session rotation reviewed
[ ] Session expiration reviewed
[ ] Logout reviewed
[ ] JWT validation reviewed
[ ] API key authentication reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
[ ] MFA reviewed
[ ] Password reset reviewed
[ ] Recovery flows reviewed
[ ] Magic links reviewed
[ ] Rate limiting reviewed
[ ] Authentication logging reviewed
```

---

# Authorisation Checklist

```text
[ ] Authorisation architecture identified
[ ] Roles identified
[ ] Permissions identified
[ ] Policies identified
[ ] Claims identified
[ ] Ownership model identified
[ ] Tenant model identified
[ ] Route-level controls reviewed
[ ] Method-level controls reviewed
[ ] Object-level controls reviewed
[ ] Property-level controls reviewed
[ ] Business rules reviewed
[ ] Administrative operations reviewed
[ ] Role assignment reviewed
[ ] Tenant switching reviewed
[ ] Impersonation reviewed
```

---

# IDOR / BOLA Checklist

```text
[ ] User-controlled identifiers identified
[ ] Object lookups traced
[ ] Ownership checks identified
[ ] Tenant checks identified
[ ] Read operations reviewed
[ ] Update operations reviewed
[ ] Delete operations reviewed
[ ] Download operations reviewed
[ ] Export operations reviewed
[ ] Share operations reviewed
[ ] Alternate entry points reviewed
```

---

# Framework Checklist

```text
[ ] ASP.NET Authorize/AllowAnonymous reviewed where applicable
[ ] ASP.NET policies reviewed
[ ] Spring SecurityFilterChain reviewed
[ ] Spring method security reviewed
[ ] Laravel middleware/policies reviewed
[ ] Django permissions reviewed
[ ] DRF object permissions reviewed
[ ] Flask decorators/middleware reviewed
[ ] Express middleware reviewed
[ ] NestJS guards reviewed
[ ] GraphQL resolver authorisation reviewed
[ ] gRPC interceptors and handlers reviewed
[ ] WebSocket message authorisation reviewed
```

---

# Security Architecture Checklist

```text
[ ] Default allow/default deny understood
[ ] Global middleware understood
[ ] Security filters understood
[ ] Proxy/gateway security understood
[ ] Identity headers reviewed
[ ] Multiple authentication mechanisms compared
[ ] Alternate protocols compared
[ ] Background workers reviewed
[ ] Internal APIs reviewed
[ ] Administrative APIs reviewed
```

---

# Runtime Checklist

```text
[ ] Route reachable
[ ] Expected authentication confirmed
[ ] Expected authorisation confirmed
[ ] Allowed action tested
[ ] Denied action tested
[ ] Object ownership tested where authorised
[ ] Tenant isolation tested where authorised
[ ] Role boundaries tested where authorised
[ ] Alternate entry points considered
[ ] Destructive testing avoided unless explicitly appropriate
```

---

# Common Mistakes

## Authentication Equals Authorisation

Incorrect:

```text
User is logged in
    =
User may access everything
```

---

## Role Check Equals Object Check

Incorrect:

```text
Role = User
```

does not answer:

```text
Does this user own document 123?
```

---

## UI Restriction Equals Security

Incorrect:

```text
Button hidden
    =
Operation protected
```

Server-side enforcement is required.

---

## Middleware Exists Therefore Route Is Protected

Incorrect.

Determine:

```text
Middleware ordering
Route mounting
Exceptions
Configuration
```

---

## Annotation Missing Therefore Route Is Vulnerable

Incorrect.

Security may exist globally or elsewhere in the call path.

---

## Identifier Means IDOR

Incorrect.

```text
GET /users/{id}
```

is not automatically vulnerable.

The authorisation behaviour determines the finding.

---

## Internal Route Means Safe

Incorrect.

Verify actual exposure and trust boundaries.

---

## Admin User Means No Authorisation Needed

Administrative functionality may still require:

```text
Tenant restrictions
Role separation
Business approval
Auditability
```

---

## Database Data Is Trusted

Incorrect.

Stored attacker-controlled values remain attacker-controlled.

---

## Scanner Finding Equals Vulnerability

Incorrect.

Static analysis identifies candidates.

Manual and runtime analysis establish exploitability.

---

# Authentication Decision Tree

```text
Authentication mechanism found
          |
          v
What proves identity?
          |
          v
Is verification performed?
      +---+---+
      |       |
     No      Yes
      |       |
      v       v
 Investigate Claims / Session
              |
              v
       Identity Mapping
              |
              v
       Account State Checked?
              |
              v
          MFA Required?
              |
              v
        Session / Token
              |
              v
        Privilege Context
```

---

# Authorisation Decision Tree

```text
Sensitive operation
       |
       v
Authentication required?
    +--+--+
    |     |
   No    Yes
    |     |
    v     v
 Review  Identity
 Exposure   |
            v
      Function Authorised?
          +--+--+
          |     |
         No    Yes
          |     |
          v     v
       Candidate Object involved?
                    |
                 +--+--+
                 |     |
                No    Yes
                 |     |
                 v     v
             Business  Object
              Rules    Authorised?
                         |
                      +--+--+
                      |     |
                     No    Yes
                      |     |
                      v     v
                  Candidate Tenant
                            Boundary?
                               |
                            +--+--+
                            |     |
                           No    Yes
                            |     |
                            v     v
                       Candidate Sensitive
                                 Operation
```

---

# Reverse Access-Control Model

One of the most effective workflows is:

```text
SENSITIVE OPERATION
        |
        v
FIND ALL REFERENCES
        |
        v
ENTRY POINTS
        |
  +-----+-----+-----+
  |           |     |
  v           v     v
REST       GraphQL gRPC
  |           |     |
  +-----------+-----+
              |
              v
       Compare Controls
              |
       +------+------+
       |             |
       v             v
Authentication   Authorisation
       |             |
       +------+------+
              |
              v
        Object Check
              |
              v
        Tenant Check
              |
              v
        Business Rule
```

This frequently reveals security inconsistencies between entry points.

---

# Final Authentication Model

```text
Credentials / Token
        |
        v
     Parsing
        |
        v
   Verification
        |
        v
Account Validation
        |
        v
       MFA
        |
        v
Identity Mapping
        |
        v
Session / Security Context
        |
        v
Authenticated Identity
```

---

# Final Authorisation Model

```text
Authenticated Identity
          |
          v
      Entry Point
          |
          v
 Function Permission
          |
          v
     Object Lookup
          |
          v
 Object Permission
          |
          v
    Tenant Boundary
          |
          v
    Business Rules
          |
          v
 Sensitive Operation
```

---

# Complete Security Model

```text
                         REQUEST
                            |
                            v
                     AUTHENTICATION
                            |
                            v
                         IDENTITY
                            |
                            v
                       ENTRY POINT
                            |
                            v
                 FUNCTION AUTHORISATION
                            |
                            v
                   ATTACKER-CONTROLLED
                      OBJECT IDENTIFIER
                            |
                            v
                       OBJECT LOOKUP
                            |
                            v
                  OBJECT AUTHORISATION
                            |
                            v
                     TENANT BOUNDARY
                            |
                            v
                     BUSINESS RULES
                            |
                            v
                  SENSITIVE OPERATION
                            |
                            v
                         IMPACT
```

The core review question is:

```text
Can this identity perform this operation
on this specific object
within this security context?
```

Not merely:

```text
Is the user logged in?
```

---

# Practical Testing Model

For every sensitive operation answer:

```text
1. What is the entry point?

2. What authentication mechanism applies?

3. How is identity established?

4. What function-level permission is required?

5. Where is that permission enforced?

6. Does the operation reference an object?

7. Who controls the object identifier?

8. Where is the object retrieved?

9. Where is ownership checked?

10. Where is tenant membership checked?

11. Are sensitive properties separately protected?

12. Are business rules enforced?

13. Are there alternate entry points?

14. Do those entry points use equivalent controls?

15. Can the operation be reached asynchronously?

16. Can the control be bypassed through another service?

17. Does runtime behaviour match the source?

18. Are similar variants present elsewhere?
```

If these questions can be answered, the authentication and authorisation path is understood.

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/methodology.md
docs/source-code-review/source-to-sink-analysis.md
docs/source-code-review/routes-and-entry-points.md

docs/source-code-review/dotnet.md
docs/source-code-review/java.md
docs/source-code-review/php.md
docs/source-code-review/python.md
docs/source-code-review/django.md
docs/source-code-review/flask.md
docs/source-code-review/nodejs.md
docs/source-code-review/javascript.md
```

---

# Related Static Analysis Notes

```text
docs/source-code-review/static-analysis/index.md
docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/semgrep.md
docs/source-code-review/static-analysis/opengrep.md
docs/source-code-review/static-analysis/codeql.md
```

---

# Related Web Security Notes

```text
docs/web/authentication.md
docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/mfa.md
docs/web/jwt.md
docs/web/oauth-oidc.md
docs/web/saml.md
docs/web/mass-assignment.md
docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/rate-limiting.md
docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md
```

---

# References

## OWASP Authentication Cheat Sheet

[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

## OWASP Authorization Cheat Sheet

[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

## OWASP Session Management Cheat Sheet

[OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## OWASP Password Storage Cheat Sheet

[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

## OWASP Forgot Password Cheat Sheet

[OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)

## OWASP Multifactor Authentication Cheat Sheet

[OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)

## OWASP JSON Web Token Cheat Sheet

[OWASP JSON Web Token Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

## OWASP OAuth 2.0 Protocol Cheat Sheet

[OWASP OAuth 2.0 Protocol Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)

## OWASP REST Security Cheat Sheet

[OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)

## OWASP GraphQL Cheat Sheet

[OWASP GraphQL Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)

## OWASP Secure Code Review Cheat Sheet

[OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html)

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## OWASP API Security Project

[OWASP API Security Project](https://owasp.org/www-project-api-security/)

## PortSwigger Web Security Academy - Authentication

[PortSwigger Web Security Academy - Authentication](https://portswigger.net/web-security/authentication)

## PortSwigger Web Security Academy - Access Control

[PortSwigger Web Security Academy - Access Control](https://portswigger.net/web-security/access-control)

## PortSwigger Web Security Academy - JWT

[PortSwigger Web Security Academy - JWT](https://portswigger.net/web-security/jwt)

## PortSwigger Web Security Academy - OAuth

[PortSwigger Web Security Academy - OAuth](https://portswigger.net/web-security/oauth)

## Microsoft ASP.NET Core Security

[Microsoft ASP.NET Core Security](https://learn.microsoft.com/en-us/aspnet/core/security/)

## Microsoft ASP.NET Core Authorization

[Microsoft ASP.NET Core Authorization](https://learn.microsoft.com/en-us/aspnet/core/security/authorization/introduction)

## Spring Security

[Spring Security](https://docs.spring.io/spring-security/reference/)

## Django Authentication

[Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)

## Django REST Framework Permissions

[Django REST Framework Permissions](https://www.django-rest-framework.org/api-guide/permissions/)

## Flask-Login

[Flask-Login](https://flask-login.readthedocs.io/)

## Laravel Authorization

[Laravel Authorization](https://laravel.com/docs/authorization)

## Passport

[Passport](https://www.passportjs.org/)

## CodeQL

[CodeQL](https://codeql.github.com/docs/)

## Semgrep

[Semgrep](https://semgrep.dev/docs/)

## OpenGrep

[OpenGrep](https://opengrep.dev/)

---

# Summary

Authentication establishes identity.

Authorisation determines what that identity may do.

The source-review workflow is:

```text
Map Authentication
       |
       v
Trace Identity
       |
       v
Map Routes
       |
       v
Find Sensitive Operations
       |
       v
Map Function-Level Controls
       |
       v
Map Object-Level Controls
       |
       v
Map Tenant Boundaries
       |
       v
Map Business Rules
       |
       v
Find Alternate Entry Points
       |
       v
Compare Security Controls
       |
       v
Runtime Validation
       |
       v
Variant Analysis
```

The final rule is:

```text
Authenticated
    !=
Authorised
```

and:

```text
Role Check
    !=
Object-Level Authorisation
```

and:

```text
One Protected Entry Point
    !=
Every Entry Point Protected
```

A complete review therefore determines:

```text
WHO
can perform
WHAT ACTION
on
WHICH OBJECT
inside
WHICH TENANT / SECURITY CONTEXT
through
WHICH ENTRY POINTS
under
WHICH BUSINESS RULES
```

That model should be applied to every security-sensitive operation in the application.
