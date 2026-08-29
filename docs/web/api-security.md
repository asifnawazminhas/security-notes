# API Security

Application Programming Interfaces are a major part of modern web applications.

A traditional application may render most functionality server-side:

```text
Browser
   ↓
Web Application
   ↓
Database
```

Modern applications frequently separate the user interface from application functionality:

```text
Browser / Mobile App
        ↓
       API
        ↓
Application Services
        ↓
Database / Internal Services
```

This means that a large part of the application's attack surface may exist within its APIs rather than within visible web pages.

API security testing should therefore focus on understanding:

```text
What endpoints exist?

What objects can be accessed?

What actions can be performed?

Who can perform those actions?

Which properties can users control?

Which business rules are enforced?

Which API versions exist?

What information is exposed?

What limits exist?

Which internal services does the API communicate with?
```

!!! warning "Authorised Security Testing"
    Perform API security testing only against APIs explicitly included within the authorised assessment scope. Be particularly careful with destructive methods such as DELETE, PUT and PATCH, bulk operations, administrative endpoints and APIs connected to production data.

---

# API Security Mindset

API testing should not simply consist of sending injection payloads into JSON parameters.

A better approach is:

```text
Discover API
    ↓
Understand API
    ↓
Map Endpoints
    ↓
Identify Objects
    ↓
Identify Actors
    ↓
Understand Authentication
    ↓
Understand Authorisation
    ↓
Identify Business Rules
    ↓
Map Trust Boundaries
    ↓
Create API Threat Model
    ↓
Test
```

The objective is to understand what the API allows users and systems to do.

---

# API Attack Surface

APIs may be exposed through:

```text
REST
GraphQL
SOAP
WebSockets
RPC
gRPC
Mobile APIs
Internal APIs
Partner APIs
Administrative APIs
Legacy APIs
Microservices
```

An application may use several simultaneously.

Example:

```text
Web Application
      ↓
REST API
      ↓
Microservices
      ↓
Internal APIs
```

Another application might use:

```text
Browser
   ↓
GraphQL
   ↓
Application
   ↓
REST Services
```

---

# Start With API Discovery

Before testing vulnerabilities, determine what API surface exists.

Look for paths such as:

```text
/api/
/api/v1/
/api/v2/
/api/v3/
/rest/
/graphql
/graphql/
/gql
/swagger
/swagger-ui
/swagger-ui.html
/api-docs
/v2/api-docs
/v3/api-docs
/openapi.json
/swagger.json
/openapi.yaml
/swagger.yaml
```

Also inspect:

```text
JavaScript files
Network traffic
Mobile application traffic
HTML source
robots.txt
sitemap.xml
Error messages
Documentation
GitHub repositories
Archived URLs
API clients
```

---

# Burp Suite API Discovery

A practical starting workflow is:

```text
Browser
   ↓
Burp Proxy
   ↓
Use Application Normally
   ↓
HTTP History
   ↓
Filter API Requests
   ↓
Map Endpoints
```

Look for:

```text
/api/
/graphql
JSON responses
XML responses
Bearer tokens
API keys
Version numbers
Object identifiers
```

Do not immediately modify requests.

First understand how the application communicates with the API.

---

# Browser Developer Tools

Browser Developer Tools are also useful.

Open:

```text
Developer Tools
    ↓
Network
    ↓
Fetch / XHR
```

Interact with the application.

Observe requests such as:

```text
GET /api/v1/users/123
POST /api/v1/orders
PATCH /api/v1/profile
DELETE /api/v1/items/500
```

The front end can effectively act as API documentation.

---

# JavaScript Analysis

JavaScript files often reveal API endpoints that are not immediately visible.

Search downloaded JavaScript:

```bash
grep -RniE '/api/|graphql|swagger|openapi' .
```

Useful tools may include:

```text
Burp Suite
LinkFinder
Katana
gau
waybackurls
urlfinder
grep
ripgrep
```

Example:

```bash
rg -i '/api/|graphql|swagger|openapi' .
```

Look for:

```text
API routes
Hidden parameters
Administrative routes
Old API versions
Feature flags
Object names
Authentication headers
```

---

# API Documentation

API documentation can dramatically increase coverage.

Look for:

```text
OpenAPI
Swagger
Postman collections
GraphQL schema
WSDL
Developer documentation
SDK documentation
```

For example:

```text
/openapi.json
```

may reveal:

```text
Endpoints
Methods
Parameters
Request bodies
Schemas
Authentication
Response structures
```

---

# Swagger and OpenAPI

Common paths include:

```text
/swagger
/swagger-ui
/swagger-ui.html
/swagger.json
/openapi.json
/api-docs
/v2/api-docs
/v3/api-docs
```

If documentation is intentionally public, its existence is not necessarily a vulnerability.

However, it can provide valuable information during an authorised assessment.

Example:

```text
OpenAPI
   ↓
GET /users/{id}
POST /users
PATCH /users/{id}
DELETE /users/{id}
```

This immediately gives a testing map.

---

# API Inventory

Create an endpoint inventory.

For example:

| Method | Endpoint | Authentication | Object | Notes |
|---|---|---|---|---|
| GET | `/api/v1/users/me` | User | User | Current profile |
| GET | `/api/v1/users/{id}` | User | User | Test object access |
| PATCH | `/api/v1/users/{id}` | User | User | Test writable fields |
| GET | `/api/v1/orders/{id}` | User | Order | Test ownership |
| POST | `/api/v1/orders` | User | Order | Business logic |
| DELETE | `/api/v1/orders/{id}` | User | Order | State dependent |
| GET | `/api/v1/admin/users` | Admin | User | Function-level access |

This makes testing systematic.

---

# API Threat Modelling

For each API area, identify:

```text
ACTORS

Anonymous user
Authenticated user
Administrator
Service account
Partner
Internal service
```

Then:

```text
OBJECTS

User
Account
Order
Invoice
Document
Organisation
Subscription
Payment
Message
File
```

Then:

```text
ACTIONS

Read
Create
Modify
Delete
Approve
Export
Import
Share
Transfer
```

The combination becomes:

```text
Actor
  ↓
Action
  ↓
Object
```

For example:

```text
User A
  ↓
Read
  ↓
Order belonging to User B
```

This immediately suggests an authorisation test.

---

# OWASP API Security Top 10

The OWASP API Security Top 10 provides an excellent framework for API assessments.

The 2023 categories are:

```text
API1:2023
Broken Object Level Authorization

API2:2023
Broken Authentication

API3:2023
Broken Object Property Level Authorization

API4:2023
Unrestricted Resource Consumption

API5:2023
Broken Function Level Authorization

API6:2023
Unrestricted Access to Sensitive Business Flows

API7:2023
Server Side Request Forgery

API8:2023
Security Misconfiguration

API9:2023
Improper Inventory Management

API10:2023
Unsafe Consumption of APIs
```

These categories are useful for structuring testing.

---

# API1: Broken Object Level Authorization

Broken Object Level Authorization, commonly referred to as BOLA, occurs when an API allows a user to access an object they should not be authorised to access.

This is closely related to IDOR.

Example:

```http
GET /api/v1/orders/1001 HTTP/1.1
Host: target.example
Authorization: Bearer USER_A_TOKEN
```

Response:

```json
{
    "orderId": 1001,
    "customer": "Alice"
}
```

Now suppose another order exists:

```text
1002
```

The security question is:

```text
Does order 1002 belong to User A?
```

not:

```text
Does order 1002 exist?
```

---

# BOLA Testing

Conceptually:

```text
User A
  ↓
GET /orders/1001
  ↓
Allowed
```

Then:

```text
User A
  ↓
GET /orders/1002
  ↓
Order belongs to User B
```

Expected:

```text
403 Forbidden
```

or another appropriate denial.

Potential vulnerability:

```text
200 OK
+
User B's order
```

---

# Test With Two Accounts

The safest and clearest BOLA testing method is using two accounts you control.

```text
Account A
    ↓
Create Object A

Account B
    ↓
Create Object B
```

Then:

```text
Account A
    ↓
Request Object B
```

This avoids guessing identifiers belonging to unrelated users.

---

# Object Identifiers

Do not only look for numeric IDs.

Objects may be identified by:

```text
Integer
UUID
GUID
Email
Username
Filename
Slug
Account number
Order number
Document ID
Hash
Reference code
```

Examples:

```text
/users/123
/users/550e8400-e29b-41d4-a716-446655440000
/users/alice
/orders/ORD-2026-000123
```

Using UUIDs does not replace authorisation.

---

# Nested Object References

Identifiers may also appear inside JSON.

Example:

```json
{
    "accountId": 5001,
    "documentId": 9876
}
```

Test every object reference independently.

The endpoint itself may not contain the vulnerable identifier.

---

# BOLA Across HTTP Methods

Do not test only:

```text
GET
```

An API might correctly protect reading but fail to protect modification.

Test according to scope:

```text
GET
POST
PUT
PATCH
DELETE
```

For example:

```text
GET /documents/123
```

may be protected while:

```text
DELETE /documents/123
```

is not.

---

# API2: Broken Authentication

API authentication may use:

```text
Session cookies
Bearer tokens
JWT
API keys
OAuth
Client certificates
Custom tokens
```

Testing should determine:

```text
How are tokens issued?

How are tokens validated?

When do tokens expire?

Can tokens be reused?

Are tokens bound to the correct user?

Does logout invalidate tokens?

Are sensitive endpoints consistently protected?
```

---

# Missing Authentication

Start simple.

Take an authenticated request:

```http
GET /api/v1/profile HTTP/1.1
Host: target.example
Authorization: Bearer eyJ...
```

Remove:

```http
Authorization: Bearer eyJ...
```

Expected:

```text
401 Unauthorized
```

Check whether the endpoint still returns protected information.

---

# Authentication Consistency

Applications sometimes expose multiple routes to the same functionality.

Example:

```text
/api/v1/profile
/api/v2/profile
/internal/profile
/mobile/profile
```

One endpoint may enforce authentication while another does not.

This is why API inventory matters.

---

# API Keys

Look for API keys in:

```text
HTTP headers
Query parameters
JavaScript
Mobile applications
Configuration files
Git repositories
Documentation
```

Examples:

```http
X-API-Key: ...
```

or:

```text
/api/data?api_key=...
```

Determine:

```text
What does the key identify?

What permissions does it provide?

Can it be revoked?

Does it expire?

Is it exposed client-side intentionally?

Is it restricted to expected operations?
```

---

# JWT

APIs commonly use JSON Web Tokens.

Example:

```http
Authorization: Bearer eyJhbGciOi...
```

JWT testing deserves its own detailed methodology, but during API testing inspect:

```text
Header
Payload
Signature
Expiration
Issuer
Audience
Subject
Roles
Scopes
```

Conceptually:

```text
JWT
 ↓
Identity
 ↓
Claims
 ↓
API Authorisation
```

The server must not trust modified claims without valid cryptographic verification.

---

# OAuth Scopes

OAuth-protected APIs may use scopes.

For example:

```text
profile:read
profile:write
orders:read
orders:write
admin
```

Ask:

```text
Does the API actually enforce scopes?

Can a read-only token perform writes?

Can a user token access administrator operations?

Are scopes checked on every relevant endpoint?
```

---

# API3: Broken Object Property Level Authorization

Modern APIs frequently map request data directly into application objects.

Example:

```json
{
    "displayName": "Alice",
    "email": "alice@example.com"
}
```

But the internal object may contain additional properties:

```text
displayName
email
role
isAdmin
accountStatus
subscription
credit
organisationId
```

If the API accepts properties that the user should not control, a property-level authorisation vulnerability may exist.

---

# Mass Assignment

Suppose the normal request is:

```http
PATCH /api/v1/profile HTTP/1.1
Content-Type: application/json

{
    "displayName": "Alice"
}
```

An interesting test is whether unexpected properties are accepted.

For example:

```json
{
    "displayName": "Alice",
    "role": "admin"
}
```

The correct behaviour should be:

```text
Ignore or reject unauthorised property
```

The server should use an allowlist of writable properties.

---

# Discovering Hidden Properties

Properties may be discovered through:

```text
GET responses
JavaScript
OpenAPI schemas
GraphQL schemas
Error messages
Mobile applications
Old API versions
Documentation
Source code
```

For example, a GET response might reveal:

```json
{
    "id": 123,
    "username": "alice",
    "role": "user",
    "isVerified": true,
    "subscription": "standard"
}
```

Not every returned property should necessarily be writable.

---

# Excessive Data Exposure

Property-level authorisation also applies to responses.

Example:

```http
GET /api/v1/profile
```

Expected:

```json
{
    "username": "alice",
    "displayName": "Alice"
}
```

Potentially excessive:

```json
{
    "username": "alice",
    "displayName": "Alice",
    "passwordHash": "...",
    "internalNotes": "...",
    "mfaSecret": "...",
    "resetToken": "..."
}
```

The API should return only information required by the client.

---

# API4: Unrestricted Resource Consumption

APIs consume resources such as:

```text
CPU
Memory
Disk
Bandwidth
Database queries
Email
SMS
Third-party API calls
Cloud resources
```

An API may expose functionality that is individually legitimate but expensive when repeatedly invoked.

Examples:

```text
Password reset emails
SMS verification
PDF generation
Report generation
Image processing
Search
Data export
AI inference
File conversion
```

---

# Resource Consumption Threat Model

For each expensive function ask:

```text
Who can invoke it?

How often?

How much data can be requested?

How expensive is one operation?

Does it call a paid third-party service?

Are limits per IP?

Per account?

Per API key?

Per organisation?
```

---

# Pagination

Consider:

```http
GET /api/v1/users?limit=50
```

Test reasonable boundaries:

```text
limit=1
limit=50
limit=100
limit=1000
```

The server should impose a maximum.

Avoid requesting extremely large values against production systems merely to demonstrate the issue.

---

# GraphQL Resource Consumption

GraphQL can create expensive nested queries.

Conceptually:

```text
Query
 ↓
Users
 ↓
Orders
 ↓
Products
 ↓
Reviews
 ↓
Authors
```

A relatively small request may cause significant server-side work.

Controls may include:

```text
Query depth limits
Query complexity limits
Timeouts
Rate limits
Pagination
```

---

# API5: Broken Function Level Authorization

Broken Function Level Authorization occurs when a user can invoke a function intended for another role.

Example:

```text
Normal User
    ↓
GET /api/v1/profile
```

Administrator:

```text
Admin
  ↓
GET /api/v1/admin/users
```

Test whether:

```text
Normal User
    ↓
GET /api/v1/admin/users
```

is properly denied.

---

# Function-Level Testing

Look for endpoints containing:

```text
/admin/
/management/
/internal/
/staff/
/support/
/moderator/
/operator/
```

But do not rely solely on naming.

Sensitive actions may also appear as:

```text
POST /users/123/disable
POST /orders/123/refund
POST /documents/123/approve
POST /accounts/123/unlock
```

The function itself determines the required privilege.

---

# Role Matrix

Create a role matrix.

| Function | Anonymous | User | Manager | Admin |
|---|---:|---:|---:|---:|
| View own profile | No | Yes | Yes | Yes |
| View another user | No | No | Maybe | Yes |
| Create order | No | Yes | Yes | Yes |
| Approve order | No | No | Yes | Yes |
| Delete user | No | No | No | Yes |

Then test the boundaries.

---

# API6: Unrestricted Access to Sensitive Business Flows

Some API functionality is intentionally available but can be abused at scale.

Examples:

```text
Buying limited products
Creating accounts
Making reservations
Submitting applications
Posting comments
Sending invitations
Claiming rewards
Using promotional codes
Purchasing tickets
```

The vulnerability may not involve bypassing authentication.

The issue may be that automation allows the business process to be abused.

---

# Business Flow Threat Modelling

Suppose an API provides:

```http
POST /api/v1/reservations
```

The endpoint is intentionally public to authenticated users.

Ask:

```text
Can one account reserve all available slots?

Can reservations be automated?

Are there sensible limits?

Can abandoned reservations exhaust inventory?

Can a single user monopolise a scarce resource?
```

This directly connects API security with business logic threat modelling.

---

# API7: Server-Side Request Forgery

APIs frequently accept URLs.

Examples:

```json
{
    "avatarUrl": "https://example.com/image.jpg"
}
```

or:

```json
{
    "webhook": "https://example.com/callback"
}
```

Potential features include:

```text
Webhooks
URL previews
Image imports
PDF generators
File imports
Remote integrations
Feed readers
Callbacks
```

These should be assessed for SSRF.

Refer to:

[Server Side Request Forgery](ssrf.md)

for the dedicated SSRF methodology.

---

# API8: Security Misconfiguration

API security misconfigurations may include:

```text
Verbose errors
Debug endpoints
Default credentials
Unnecessary HTTP methods
Exposed management interfaces
Incorrect CORS
Missing TLS
Sensitive headers
Stack traces
Exposed documentation
Unsafe content types
Misconfigured caching
```

---

# Verbose Errors

Malformed requests may reveal:

```text
Framework
Source paths
Database names
SQL queries
Class names
Internal hostnames
Stack traces
Dependency versions
```

Example:

```json
{
    "error": "NullReferenceException",
    "file": "/app/services/UserService.cs",
    "line": 187
}
```

Production APIs should return controlled error responses.

---

# HTTP Methods

Determine which methods are supported.

Common methods:

```text
GET
POST
PUT
PATCH
DELETE
OPTIONS
HEAD
```

Potentially less common:

```text
TRACE
CONNECT
```

Use:

```bash
curl -i -X OPTIONS https://target.example/api/
```

Do not assume the `Allow` header provides a complete or accurate picture.

---

# Method Switching

Sometimes authorisation is applied inconsistently across methods.

For example:

```text
GET /api/users/123
```

may be protected while:

```text
PATCH /api/users/123
```

is not.

Or:

```text
POST /api/admin/action
```

is blocked while another supported method reaches equivalent functionality.

Test only methods that make sense for the endpoint and avoid destructive operations without approval.

---

# CORS

APIs often rely on Cross-Origin Resource Sharing.

Inspect:

```http
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Access-Control-Allow-Methods
Access-Control-Allow-Headers
```

The security impact depends on:

```text
Authentication method
Allowed origin
Credential handling
Sensitive response data
```

Do not report:

```http
Access-Control-Allow-Origin: *
```

as automatically vulnerable.

Context matters.

---

# API9: Improper Inventory Management

Modern applications frequently contain multiple API versions.

For example:

```text
/api/v1/
/api/v2/
/api/v3/
```

Developers may secure the latest API while older versions remain accessible.

Example:

```text
/api/v3/users
```

may enforce current controls while:

```text
/api/v1/users
```

still exposes deprecated behaviour.

---

# API Version Discovery

Look for:

```text
/v1/
/v2/
/v3/
/beta/
/alpha/
/legacy/
/old/
/internal/
/test/
/dev/
```

Search:

```text
JavaScript
OpenAPI
GitHub
Wayback Machine
Historical URLs
Mobile application code
Documentation
```

---

# Compare API Versions

If:

```text
/api/v2/account
```

exists, test whether:

```text
/api/v1/account
```

also exists.

Compare:

```text
Authentication
Authorisation
Response fields
Input validation
Rate limits
Business rules
```

Older APIs can expose security controls that were fixed only in newer versions.

---

# Shadow APIs

A shadow API is an API that exists but is not properly inventoried or managed.

Examples:

```text
Developer API
Temporary API
Legacy endpoint
Internal API exposed externally
Old mobile API
Forgotten beta API
```

API discovery should therefore extend beyond documented routes.

---

# API10: Unsafe Consumption of APIs

Applications increasingly consume external APIs.

Architecture:

```text
User
 ↓
Application
 ↓
Third-Party API
 ↓
Application
 ↓
User
```

Developers may trust third-party API responses more than ordinary user input.

That trust can be dangerous.

---

# Third-Party Trust

Consider:

```text
Application
     ↓
External API
     ↓
JSON Response
```

Ask:

```text
Is returned data validated?

Can the third-party response contain unexpected values?

Can redirects occur?

Can returned URLs cause SSRF?

Can returned HTML cause XSS?

Are numeric values trusted?

Are object properties trusted?
```

External data should still be treated as untrusted.

---

# REST APIs

REST APIs commonly expose resources through paths.

Example:

```text
GET    /api/users/123
POST   /api/users
PATCH  /api/users/123
DELETE /api/users/123
```

Think:

```text
RESOURCE
   ↓
IDENTIFIER
   ↓
ACTION
   ↓
AUTHORISATION
```

For each resource ask:

```text
Can I read another user's object?

Can I modify another user's object?

Can I delete another user's object?

Can I create properties I should not control?

Can I call privileged actions?
```

---

# REST API Testing Workflow

```text
Discover Resource
      ↓
Identify CRUD Operations
      ↓
Identify Object ID
      ↓
Identify Owner
      ↓
Test Authentication
      ↓
Test Object Authorisation
      ↓
Test Property Authorisation
      ↓
Test Function Authorisation
      ↓
Test Business Logic
```

---

# GraphQL

GraphQL commonly uses a single endpoint:

```text
/graphql
```

or:

```text
/api/graphql
```

Example query:

```graphql
query {
  user {
    id
    username
  }
}
```

Unlike REST, the client specifies which fields it wants returned.

---

# GraphQL Discovery

Common endpoints include:

```text
/graphql
/graphql/
/api/graphql
/gql
```

Inspect:

```text
JavaScript
Network traffic
Documentation
Error responses
```

---

# GraphQL Introspection

GraphQL may support introspection.

Introspection allows clients to understand the schema.

Conceptually:

```text
GraphQL Endpoint
      ↓
Schema
      ↓
Types
Queries
Mutations
Fields
```

If intentionally enabled, introspection is not automatically a vulnerability.

However, it can significantly improve attack-surface discovery.

---

# GraphQL Security Testing

Focus on:

```text
Object-level authorisation
Field-level authorisation
Mutation authorisation
Excessive data exposure
Resource consumption
Business logic
Batching
Aliases
Introspection
Error messages
```

---

# GraphQL Object Authorisation

Suppose:

```graphql
query {
  order(id: "1001") {
    id
    total
  }
}
```

The same BOLA question applies:

```text
Does the authenticated user own order 1001?
```

GraphQL does not remove the need for server-side object authorisation.

---

# GraphQL Field-Level Authorization

Consider:

```graphql
query {
  user(id: "123") {
    username
    email
    internalNotes
  }
}
```

A user might legitimately access:

```text
username
```

but not:

```text
internalNotes
```

Authorisation should therefore sometimes occur at field level as well as object level.

---

# GraphQL Mutations

Mutations perform actions.

Example:

```graphql
mutation {
  updateProfile(name: "Alice") {
    id
  }
}
```

Test mutations for:

```text
Authentication
Object ownership
Writable properties
Role requirements
Business rules
```

---

# SOAP APIs

SOAP APIs typically use XML.

Example:

```http
POST /service HTTP/1.1
Content-Type: text/xml
```

with:

```xml
<soap:Envelope>
    ...
</soap:Envelope>
```

Look for:

```text
WSDL
SOAPAction
XML parsing
Authentication
Object identifiers
Business operations
```

SOAP testing can overlap with:

```text
XXE
XPath injection
Business logic
Authentication
Authorisation
```

---

# WSDL

A WSDL file can reveal:

```text
Operations
Parameters
Data types
Endpoints
Services
```

Common patterns include:

```text
?wsdl
/service?wsdl
```

If WSDL documentation is intentionally exposed, its presence alone is not necessarily a vulnerability.

---

# Content-Type Testing

APIs may support multiple representations.

Examples:

```text
application/json
application/xml
text/xml
application/x-www-form-urlencoded
multipart/form-data
```

If an endpoint normally accepts JSON, determine whether it also processes XML where appropriate.

This may expose a different parser and therefore a different attack surface.

---

# Hidden API Parameters

An endpoint may accept more properties than the UI sends.

Normal:

```json
{
    "name": "Alice"
}
```

Potential internal model:

```json
{
    "name": "Alice",
    "role": "user",
    "status": "active",
    "credit": 0
}
```

Sources for discovering properties include:

```text
GET responses
JavaScript
OpenAPI
GraphQL
Mobile applications
Error messages
Old API versions
```

---

# Parameter Pollution

APIs may handle duplicate parameters inconsistently.

Example:

```text
?userId=100&userId=200
```

Different components may choose:

```text
First value
Last value
Both values
Combined value
```

This can matter when:

```text
WAF
Proxy
Framework
Application
```

interpret duplicate parameters differently.

Test carefully and observe behaviour.

---

# JSON Duplicate Keys

The same issue can occur in JSON.

Conceptually:

```json
{
    "role": "user",
    "role": "admin"
}
```

Different parsers or components may interpret duplicate keys differently.

This is especially interesting when multiple systems process the request.

---

# API Parameter Boundaries

For numeric values test logical boundaries.

Example:

```json
{
    "quantity": 5
}
```

Consider:

```text
0
1
Maximum allowed
Maximum + 1
Negative values
Decimal values where integers are expected
```

Do not send extremely large values merely to exhaust resources.

The objective is validation testing, not disruption.

---

# API Business Logic

API testing and business logic testing are closely connected.

If the API handles:

```text
Pricing
```

threat model:

```text
Price
Quantity
Discount
Currency
Payment amount
```

If it handles:

```text
Account recovery
```

threat model:

```text
Token
Account binding
Step sequence
Expiration
Reuse
```

If it handles:

```text
Approval
```

threat model:

```text
Role
State
Approval level
Self-approval
Post-approval modification
```

The API is often where the real business rules are enforced.

---

# Burp Repeater

Burp Repeater is one of the most useful tools for API testing.

Use it for:

```text
Object ID changes
Token changes
Role comparison
Property manipulation
Method changes
Content-Type changes
API version testing
Workflow testing
Request replay
```

A useful naming scheme:

```text
API-BOLA-001
API-BFLA-001
API-PROP-001
API-AUTH-001
API-LOGIC-001
```

---

# Burp Comparer

Comparer can help compare:

```text
User A Response
       vs
User B Response
```

or:

```text
Normal Request
       vs
Modified Request
```

Compare:

```text
Response status
JSON fields
Object IDs
Headers
Response length
Error messages
```

---

# Autorize

The Burp extension:

```text
Autorize
```

can assist with authorisation testing.

A common workflow is:

```text
Privileged Session
       ↓
Capture Requests
       ↓
Autorize Replays Requests
       ↓
Lower-Privilege Credentials
       ↓
Compare Responses
```

This is particularly useful for:

```text
BOLA
BFLA
Role-based access testing
```

Automated results still require manual validation.

---

# AuthMatrix

Another useful Burp extension is:

```text
AuthMatrix
```

It can help create an authorisation matrix across:

```text
Users
Roles
Requests
```

Conceptually:

```text
Request
        User A   User B   Admin
        ↓        ↓        ↓
GET A   Allow    Deny     Allow
GET B   Deny     Allow    Allow
ADMIN   Deny     Deny     Allow
```

This is useful when an API contains many roles and endpoints.

---

# Postman

If the development team provides a Postman collection, it can be extremely useful.

A collection may contain:

```text
Endpoints
Parameters
Example requests
Authentication
Variables
Workflows
```

Importing the collection can quickly provide an API inventory.

Remember that documentation may not include:

```text
Deprecated APIs
Internal endpoints
Hidden parameters
Legacy versions
```

so discovery should continue beyond the collection.

---

# curl

Basic GET:

```bash
curl -i https://target.example/api/v1/profile
```

Bearer token:

```bash
curl -i \
  -H "Authorization: Bearer TOKEN" \
  https://target.example/api/v1/profile
```

POST JSON:

```bash
curl -i \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"name":"Alice"}' \
  https://target.example/api/v1/profile
```

Use test credentials and authorised targets only.

---

# ffuf API Discovery

For authorised endpoint discovery:

```bash
ffuf \
  -u https://target.example/api/FUZZ \
  -w wordlist.txt
```

Possible API-oriented words:

```text
users
accounts
orders
admin
profile
documents
files
payments
subscriptions
internal
health
status
```

Keep request rates appropriate for the environment.

---

# API Response Codes

Common responses include:

```text
200 OK
201 Created
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
405 Method Not Allowed
409 Conflict
422 Unprocessable Content
429 Too Many Requests
500 Internal Server Error
```

Do not rely solely on the status code.

Always inspect the body.

For example:

```text
403
```

might still contain sensitive information.

---

# 401 vs 403

Generally:

```text
401
```

means authentication is required or invalid.

```text
403
```

means the server understands the request but refuses the operation.

Applications do not always follow these conventions consistently.

Focus on actual behaviour.

---

# Rate Limiting

Look for:

```http
HTTP/1.1 429 Too Many Requests
```

and headers such as:

```text
Retry-After
RateLimit-Limit
RateLimit-Remaining
RateLimit-Reset
X-RateLimit-Limit
X-RateLimit-Remaining
```

Assess rate limiting in the context of the protected business function.

---

# Sensitive Rate-Limit Candidates

Particularly important operations include:

```text
Login
Password reset
MFA verification
OTP generation
Email verification
Account registration
Invitation creation
Voucher redemption
Search
Export
SMS sending
```

Testing should remain controlled and should not generate excessive emails, SMS messages or expensive external operations.

---

# File Upload APIs

APIs may expose upload endpoints such as:

```text
/api/files
/api/upload
/api/documents
```

Test according to the dedicated file-upload methodology.

Important areas include:

```text
File type
Extension
Content type
Magic bytes
File size
Filename
Metadata
Storage location
Retrieval
Processing
```

Refer to:

[File Upload Security](file-upload.md)

---

# API SSRF

Look for parameters such as:

```text
url
uri
endpoint
callback
webhook
image
avatar
feed
redirect
resource
```

Example:

```json
{
    "callback": "https://example.com"
}
```

This should trigger SSRF threat modelling.

Refer to:

```text
docs/web/ssrf.md
```

---

# API Injection

API inputs can still reach traditional injection sinks.

Test according to the relevant context for:

```text
SQL injection
Command injection
SSTI
XXE
XSS
Path traversal
```

Do not send every payload to every parameter.

First understand what the parameter does.

---

# API Testing Decision Tree

```text
Endpoint Found
     ↓
Does It Require Authentication?
     ↓
What Actor Is Authenticated?
     ↓
What Object Is Accessed?
     ↓
Who Owns the Object?
     ↓
What Function Is Performed?
     ↓
Which Role Should Perform It?
     ↓
Which Properties Are Read?
     ↓
Which Properties Are Writable?
     ↓
What Business Rule Applies?
     ↓
What Resources Are Consumed?
     ↓
Does It Call Another Service?
```

---

# API Testing Checklist

## Discovery

```text
[ ] Proxy application traffic
[ ] Inspect JavaScript
[ ] Look for /api/
[ ] Look for GraphQL
[ ] Look for Swagger/OpenAPI
[ ] Look for WSDL
[ ] Identify API versions
[ ] Identify legacy endpoints
[ ] Review documentation
[ ] Build endpoint inventory
```

## Authentication

```text
[ ] Remove credentials
[ ] Test expired credentials
[ ] Test logout behaviour
[ ] Compare authentication across versions
[ ] Review API keys
[ ] Review bearer tokens
[ ] Review JWT where applicable
[ ] Review OAuth scopes
```

## Object Authorisation

```text
[ ] Identify object IDs
[ ] Use two controlled accounts
[ ] Read another controlled account's object
[ ] Modify another controlled account's object
[ ] Delete another controlled account's object where safe
[ ] Test nested object IDs
[ ] Test UUID/GUID objects
```

## Property Authorisation

```text
[ ] Compare request and response schemas
[ ] Identify hidden properties
[ ] Test writable properties
[ ] Test sensitive properties
[ ] Look for excessive data exposure
[ ] Test mass assignment
```

## Function Authorisation

```text
[ ] Identify privileged endpoints
[ ] Create role matrix
[ ] Test user vs admin
[ ] Test user vs manager
[ ] Test privileged actions
[ ] Test alternate methods
```

## Business Logic

```text
[ ] Identify business function
[ ] Identify business rules
[ ] Map workflow
[ ] Test step skipping
[ ] Test replay
[ ] Test boundaries
[ ] Test state transitions
[ ] Consider concurrency
```

## Resource Consumption

```text
[ ] Review pagination
[ ] Review query limits
[ ] Review export limits
[ ] Review expensive operations
[ ] Review email/SMS operations
[ ] Review third-party API usage
```

## Inventory

```text
[ ] Identify API versions
[ ] Identify beta endpoints
[ ] Identify legacy endpoints
[ ] Identify undocumented endpoints
[ ] Identify development endpoints
[ ] Compare controls across versions
```

---

# Evidence Collection

For every API finding record:

```text
Endpoint
HTTP method
API version
Authentication context
User / role
Object
Object owner
Original request
Modified request
Original response
Modified response
Expected behaviour
Observed behaviour
Business impact
```

---

# Example BOLA Evidence

```text
Finding:
Broken Object Level Authorization

Account A Object:
Order 1001

Account B Object:
Order 1002

Test:
Account A requested /api/v1/orders/1002

Expected:
Access denied

Observed:
200 OK containing Account B's order

Impact:
Authenticated users can access orders belonging to other users.
```

---

# Example Property-Level Finding

```text
Finding:
Broken Object Property Level Authorization

Endpoint:
PATCH /api/v1/profile

Normal Request:

{
    "displayName": "Alice"
}

Modified Request:

{
    "displayName": "Alice",
    "role": "admin"
}

Expected:
The role property should be rejected or ignored.

Observed:
The API accepted the property.

Impact:
User-controlled properties can modify security-sensitive account state.
```

---

# Reporting

Avoid vague titles such as:

```text
API Security Issue
```

Use precise titles.

Examples:

```text
Broken Object Level Authorization Exposes Other Users' Orders

Standard Users Can Access Administrative API Function

API Allows Modification of Restricted Account Properties

Deprecated API Version Bypasses Current Authorisation Controls

Password Reset API Lacks Effective Rate Limiting

API Exposes Sensitive Internal Account Properties
```

---

# Remediation

API security controls should be enforced server-side.

The API should never assume:

```text
The UI prevented the action
```

or:

```text
The client would not send that property
```

The API is the security boundary.

---

# Object-Level Authorisation

For every object request:

```text
Authenticated User
       ↓
Requested Object
       ↓
Check Ownership / Permission
       ↓
Allow or Deny
```

Do not rely on unpredictable identifiers.

---

# Property Allowlisting

For updates:

```text
Incoming JSON
      ↓
Allowlisted Properties
      ↓
Validated Values
      ↓
Update Object
```

Do not automatically bind every supplied property to an internal model.

---

# Function-Level Authorisation

Every sensitive function should independently verify:

```text
Identity
Role
Permission
Resource
Business state
```

Do not rely solely on hidden UI functionality.

---

# API Inventory Management

Maintain an inventory containing:

```text
API
Version
Environment
Owner
Exposure
Authentication
Documentation
Lifecycle status
```

Deprecated APIs should be removed when no longer required.

---

# Secure Third-Party API Consumption

Treat external API responses as untrusted.

Apply:

```text
Schema validation
Type validation
Length validation
URL validation
Output encoding
Error handling
Timeouts
Resource limits
```

---

# API Security Quick Reference

```text
DISCOVERY

/api/
/v1/
/v2/
/graphql
/swagger
/openapi.json
/api-docs
?wsdl
```

```text
AUTHENTICATION

Cookies
Bearer
JWT
API keys
OAuth
```

```text
AUTHORISATION

Object
Property
Function
Role
Scope
```

```text
BUSINESS LOGIC

State
Sequence
Limits
Replay
Concurrency
```

```text
INVENTORY

Versions
Legacy
Beta
Internal
Shadow APIs
```

---

# Five Questions for Every API Request

For every interesting API request ask:

```text
1. Who am I?

2. What object am I accessing?

3. Am I allowed to access this object?

4. Am I allowed to perform this action?

5. Am I allowed to control these properties?
```

Then add:

```text
6. What business rule applies?

7. What happens if I repeat this request?

8. What happens if I change the workflow?

9. What resource does this consume?

10. What other systems does this request reach?
```

---

# API Threat Model Template

```text
API AREA:
Orders

ACTORS:
Customer
Support
Administrator

OBJECTS:
Order
Product
Payment

FUNCTIONS:
Create
Read
Cancel
Refund

AUTHENTICATION:
Bearer token

OBJECT AUTHORISATION:
Customer may access own orders only

PROPERTY AUTHORISATION:
Customer may modify delivery instructions before shipment

BUSINESS RULES:
Paid orders cannot change product
Refund cannot exceed payment
Shipped orders cannot be cancelled

RESOURCE RISKS:
Order creation
PDF invoice generation

EXTERNAL DEPENDENCIES:
Payment provider

TESTS:
BOLA
BFLA
Property manipulation
State manipulation
Refund logic
Resource limits
```

---

# Recommended Testing Workflow

```text
Application
     ↓
Burp Proxy
     ↓
Map API Traffic
     ↓
Discover Documentation
     ↓
Inspect JavaScript
     ↓
Identify API Versions
     ↓
Build Endpoint Inventory
     ↓
Identify Actors
     ↓
Identify Objects
     ↓
Identify Functions
     ↓
Identify Properties
     ↓
Identify Business Rules
     ↓
Create Role Matrix
     ↓
Create API Threat Model
     ↓
Test Authentication
     ↓
Test BOLA
     ↓
Test Property Authorization
     ↓
Test Function Authorization
     ↓
Test Business Logic
     ↓
Test Resource Controls
     ↓
Test API Inventory
     ↓
Review External API Trust
     ↓
Investigate Context-Specific Injection
     ↓
Collect Evidence
     ↓
Report
```

---

# Tools

Useful API security tools include:

```text
Burp Suite
Burp Repeater
Burp Comparer
Autorize
AuthMatrix
Postman
curl
ffuf
httpx
Katana
Browser Developer Tools
GraphQL clients
Swagger / OpenAPI tooling
```

Automation should supplement rather than replace manual analysis.

API vulnerabilities frequently depend on understanding:

```text
Objects
Roles
Properties
Workflows
Business rules
```

which generic vulnerability scanners may not understand.

---

# References

## OWASP API Security Project

https://owasp.org/www-project-api-security/

The OWASP API Security Project provides guidance specifically focused on API security risks.

---

## OWASP API Security Top 10

https://owasp.org/API-Security/

The OWASP API Security Top 10 is an excellent framework for structuring an API assessment.

---

## OWASP API1:2023 Broken Object Level Authorization

https://owasp.org/API-Security/editions/2023/en/0x11-t10/

Useful when assessing object-level access control.

---

## PortSwigger Web Security Academy

API Testing:

https://portswigger.net/web-security/api-testing

PortSwigger provides practical API testing guidance and deliberately vulnerable labs.

---

## PortSwigger GraphQL API Vulnerabilities

https://portswigger.net/web-security/graphql

Useful for GraphQL discovery, schema analysis, access-control testing and GraphQL-specific attack surface.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

Useful as a broader methodology reference alongside the API Security Top 10.

---

# Final API Security Workflow

```text
                     API
                      ↓
              DISCOVER EVERYTHING
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
 Documentation    JavaScript      Traffic
       ↓              ↓              ↓
       └──────────────┼──────────────┘
                      ↓
               Endpoint Inventory
                      ↓
                 Threat Model
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    Actors          Objects        Actions
       ↓              ↓              ↓
       └──────────────┼──────────────┘
                      ↓
                 Test Controls
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
 Authentication  Authorisation   Business Logic
                      ↓
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
     BOLA          Properties      Functions
       ↓              ↓              ↓
       └──────────────┼──────────────┘
                      ↓
               Resource Controls
                      ↓
                API Inventory
                      ↓
              External API Trust
                      ↓
              Contextual Testing
                      ↓
                 Evidence
                      ↓
                  Report
```

The key principle is:

> Do not treat an API as a collection of parameters to fuzz. Treat it as a collection of objects, actions, actors and business rules. Discover the API surface, understand who should be able to perform each action against each object, identify which properties the client should control, and then systematically test whether the server enforces those rules.
