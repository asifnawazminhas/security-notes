# GraphQL API Security

GraphQL is a query language and API runtime that allows clients to request exactly the data they require.

Unlike traditional REST APIs, where functionality is commonly distributed across many endpoints, GraphQL applications frequently expose a single endpoint through which queries and mutations are performed.

Typical endpoints include:

```text
/graphql
/api/graphql
/api
/graphql/api
/graphql/graphql
/v1/graphql
/v2/graphql
/query
```

A simplified architecture is:

```text
Client
  ↓
GraphQL Endpoint
  ↓
GraphQL Parser
  ↓
Schema
  ↓
Resolvers
  ↓
Application Logic
  ↓
Database / Services
```

GraphQL itself is not inherently insecure.

Security issues generally arise from:

```text
Weak authorisation
Missing object-level access controls
Exposed introspection
Excessive data exposure
Unsafe resolver logic
Injection vulnerabilities
Weak rate limiting
Query batching
Alias abuse
Excessive query complexity
CSRF
Information disclosure
Business logic vulnerabilities
```

Potential impact includes:

```text
Sensitive data exposure
IDOR / BOLA
Privilege escalation
Authentication bypass
Authorisation bypass
Account compromise
Mass assignment
Brute-force amplification
Denial of service
Injection
Business logic abuse
```

!!! warning "Authorised Security Testing"
    GraphQL testing should only be performed against systems included in the authorised assessment scope. Query complexity, batching and alias testing can create significant server load, so begin with small controlled requests.

---

# GraphQL vs REST

A REST API may expose:

```text
GET /api/users/123
GET /api/users/123/orders
GET /api/products
POST /api/users
DELETE /api/users/123
```

GraphQL may expose:

```text
POST /graphql
```

and place the requested operation inside the request body.

For example:

```graphql
query {
    user(id: 123) {
        id
        username
        email
    }
}
```

The same endpoint may also perform updates:

```graphql
mutation {
    updateUser(
        id: 123
        name: "Alice"
    ) {
        id
        name
    }
}
```

Therefore:

```text
REST
 ↓
Endpoint-focused testing

GraphQL
 ↓
Schema + resolver + object-focused testing
```

---

# GraphQL Terminology

Important terms include:

```text
Schema
Type
Field
Argument
Query
Mutation
Subscription
Resolver
Variable
Fragment
Alias
Directive
Introspection
```

Understanding these concepts makes GraphQL security testing significantly easier.

---

# Schema

The GraphQL schema defines:

```text
Available objects
Available fields
Queries
Mutations
Subscriptions
Arguments
Relationships
Input types
Enums
```

Conceptually:

```text
Schema
 ├── Query
 │    ├── user
 │    ├── users
 │    └── products
 │
 ├── Mutation
 │    ├── createUser
 │    ├── updateUser
 │    └── deleteUser
 │
 └── Types
      ├── User
      ├── Product
      └── Order
```

From a penetration-testing perspective, the schema can become an extremely useful map of the application's attack surface.

---

# Queries

Queries normally retrieve information.

Example:

```graphql
query {
    user(id: 123) {
        id
        username
        email
    }
}
```

Possible response:

```json
{
  "data": {
    "user": {
      "id": "123",
      "username": "alice",
      "email": "alice@example.com"
    }
  }
}
```

---

# Mutations

Mutations modify application state.

Examples may include:

```text
createUser
updateUser
deleteUser
changePassword
createOrder
cancelOrder
updateRole
resetPassword
```

Example:

```graphql
mutation {
    updateProfile(name: "Alice") {
        id
        name
    }
}
```

Mutations deserve particular attention because they often expose:

```text
Authorisation flaws
Mass assignment
Business logic vulnerabilities
Privilege changes
Account modification
```

---

# Subscriptions

GraphQL subscriptions provide real-time updates.

They commonly use:

```text
WebSockets
```

Conceptually:

```text
Client
  ↓
GraphQL Subscription
  ↓
WebSocket
  ↓
Server Event
  ↓
Real-Time Response
```

If subscriptions are present, also review:

```text
docs/web/websockets.md
```

---

# Resolvers

Resolvers contain the server-side logic responsible for retrieving or modifying data.

Conceptually:

```text
GraphQL Query
      ↓
Field
      ↓
Resolver
      ↓
Database / Service
```

For example:

```text
user(id: 123)
      ↓
userResolver()
      ↓
Database
      ↓
User 123
```

Security controls often need to be enforced inside or before resolvers.

A schema may expose:

```graphql
user(id: ID!): User
```

but whether the current user is actually allowed to access that object depends on resolver and application logic.

---

# GraphQL Request Structure

A common request looks like:

```http
POST /graphql HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "query": "query { user(id: 123) { id username email } }"
}
```

GraphQL requests may also use variables.

Example:

```http
POST /graphql HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "query": "query GetUser($id: ID!) { user(id: $id) { id username email } }",
  "variables": {
    "id": "123"
  }
}
```

---

# Variables

Variables separate arguments from the GraphQL query.

Example:

```graphql
query GetUser($id: ID!) {
    user(id: $id) {
        id
        username
        email
    }
}
```

Variables:

```json
{
  "id": "123"
}
```

During testing, both should be reviewed:

```text
GraphQL query
+
Variables
```

---

# GraphQL Testing Methodology

A structured workflow is:

```text
Identify GraphQL Endpoint
          ↓
Confirm GraphQL
          ↓
Capture Legitimate Queries
          ↓
Identify Schema
          ↓
Test Introspection
          ↓
Enumerate Queries
          ↓
Enumerate Mutations
          ↓
Enumerate Types
          ↓
Map Arguments
          ↓
Test Authentication
          ↓
Test Object-Level Authorisation
          ↓
Test Field-Level Authorisation
          ↓
Test Mutations
          ↓
Test Input Validation
          ↓
Test Aliases / Batching
          ↓
Test Rate Limiting
          ↓
Test CSRF
          ↓
Test Query Complexity
          ↓
Test Business Logic
          ↓
Report
```

---

# Finding GraphQL Endpoints

The first step is identifying the GraphQL endpoint.

Common locations include:

```text
/graphql
/api
/api/graphql
/graphql/api
/graphql/graphql
/v1/graphql
/v2/graphql
/query
```

Also inspect:

```text
JavaScript
API documentation
Network traffic
Mobile API traffic
Source maps
Swagger/OpenAPI references
Error messages
```

---

# Universal GraphQL Query

A useful GraphQL probe is:

```graphql
query {
    __typename
}
```

Compact form:

```graphql
query{__typename}
```

Example request:

```http
POST /graphql HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "query": "query{__typename}"
}
```

A GraphQL service may respond with something similar to:

```json
{
  "data": {
    "__typename": "Query"
  }
}
```

This is useful because `__typename` is available on GraphQL object types.

---

# GET Requests

Some GraphQL endpoints accept queries through GET requests.

Example:

```text
/graphql?query=query{__typename}
```

During endpoint discovery, test both:

```text
POST
GET
```

where appropriate.

---

# Content Types

GraphQL APIs may accept:

```text
application/json
application/graphql
application/x-www-form-urlencoded
```

For security-sensitive operations, accepting alternative content types can become relevant to CSRF testing.

Record which combinations are accepted.

---

# Burp Suite GraphQL Detection

Burp Suite can recognise GraphQL traffic.

A practical workflow is:

```text
Burp Browser
     ↓
Proxy
     ↓
HTTP History
     ↓
GraphQL Request
     ↓
GraphQL Editor
     ↓
Repeater
```

When Burp recognises GraphQL traffic, GraphQL-specific editing support can make requests easier to analyse.

---

# Initial Burp Workflow

Browse the application normally first.

```text
Proxy
  ↓
HTTP History
  ↓
Filter Interesting Requests
  ↓
Locate GraphQL
  ↓
Send to Repeater
```

Do not begin by blindly generating large queries.

First understand what the normal application does.

---

# GraphQL Introspection

GraphQL introspection allows clients to query information about the schema itself.

This may reveal:

```text
Queries
Mutations
Types
Fields
Arguments
Enums
Input types
Subscriptions
```

Conceptually:

```text
Attacker
   ↓
Introspection
   ↓
Schema
   ↓
API Attack Surface
```

---

# Introspection Probe

A small introspection probe is:

```graphql
{
    __schema {
        queryType {
            name
        }
    }
}
```

JSON request:

```json
{
  "query": "{__schema{queryType{name}}}"
}
```

If introspection is enabled, the server may return schema information.

---

# Enumerating Query Types

Example:

```graphql
{
    __schema {
        queryType {
            fields {
                name
            }
        }
    }
}
```

This may reveal queries such as:

```text
user
users
product
products
order
orders
search
admin
```

---

# Enumerating Mutations

Mutations are often particularly valuable.

Example:

```graphql
{
    __schema {
        mutationType {
            fields {
                name
            }
        }
    }
}
```

Potential results:

```text
createUser
updateUser
deleteUser
changePassword
resetPassword
createOrder
cancelOrder
updateRole
```

---

# Full Introspection

A full introspection query can reveal the complete GraphQL schema.

Rather than manually maintaining a large introspection query, use tooling such as:

```text
Burp Suite
InQL
GraphiQL
GraphQL Voyager
GraphQL IDEs
```

where authorised.

The resulting schema can then be analysed systematically.

---

# Introspection Disabled

If introspection is disabled, do not assume the API cannot be mapped.

Other sources include:

```text
Application requests
JavaScript
Error messages
Field suggestions
Mobile applications
Documentation
Source maps
Historic endpoints
Known operation names
```

---

# GraphQL Suggestions

GraphQL implementations sometimes return suggestions when an invalid field name is supplied.

For example, requesting:

```graphql
query {
    usre {
        id
    }
}
```

may produce an error similar to:

```text
Cannot query field "usre".
Did you mean "user"?
```

These suggestions may assist schema reconstruction.

---

# Error-Based Schema Discovery

GraphQL error messages can reveal:

```text
Field names
Type names
Expected argument types
Required arguments
Enum values
Mutation names
Validation rules
```

For example:

```text
Field "user" argument "id" of type "ID!" is required
```

reveals:

```text
Field: user
Argument: id
Type: ID!
Required: yes
```

---

# GraphQL Schema Mapping

Create a map such as:

```text
Query
 ├── user(id)
 ├── users
 ├── product(id)
 ├── order(id)
 └── search(term)

Mutation
 ├── updateProfile
 ├── changePassword
 ├── createOrder
 ├── cancelOrder
 └── updateUser
```

Then prioritise:

```text
Authentication
Users
Roles
Permissions
Orders
Payments
Files
Administrative functions
Password operations
API keys
Tokens
```

---

# GraphQL and IDOR / BOLA

GraphQL APIs are highly relevant to object-level authorisation testing.

Consider:

```graphql
query {
    user(id: 1001) {
        id
        username
        email
    }
}
```

Change:

```text
1001
```

to:

```text
1002
```

Then ask:

> Is the authenticated user authorised to access user 1002?

This is fundamentally the same security question as REST API IDOR testing.

---

# Object-Level Authorisation Workflow

```text
Authenticated User A
       ↓
Query Own Object
       ↓
Capture Object ID
       ↓
Identify User B Object
       ↓
Change ID
       ↓
Send Request
       ↓
Authorisation Enforced?
```

Use controlled test accounts whenever possible.

---

# Nested Object Authorisation

GraphQL allows nested relationships.

Example:

```graphql
query {
    user(id: 123) {
        id
        username
        orders {
            id
            total
        }
    }
}
```

The API must enforce authorisation not only on:

```text
user
```

but potentially also:

```text
orders
```

A parent object being accessible does not automatically mean all nested objects should be accessible.

---

# Field-Level Authorisation

Different fields may require different privileges.

Example:

```graphql
query {
    user(id: 123) {
        id
        username
        email
        role
        passwordResetToken
        apiKey
    }
}
```

The user may legitimately access:

```text
username
email
```

but not:

```text
role
passwordResetToken
apiKey
```

Test fields individually.

---

# Excessive Data Exposure

GraphQL makes it easy for clients to request additional fields.

The UI may request:

```graphql
user {
    id
    username
}
```

while the schema may expose:

```graphql
user {
    id
    username
    email
    phone
    role
    internalId
    apiKey
}
```

Do not assume that fields absent from the normal frontend request are inaccessible.

---

# Hidden Fields

When schema information is available, compare:

```text
Fields used by frontend
```

against:

```text
Fields exposed by schema
```

The difference is particularly interesting.

For example:

```text
Frontend uses:
id
username
avatar

Schema also exposes:
email
phone
role
internalNotes
apiToken
```

Investigate authorisation for those fields.

---

# Mutation Authorisation

Mutations should receive the same scrutiny as sensitive REST methods.

Example:

```graphql
mutation {
    updateUser(
        id: 123
        name: "Alice"
    ) {
        id
        name
    }
}
```

Questions include:

```text
Can another user's ID be supplied?
Can privileged fields be changed?
Can role be modified?
Can ownership be changed?
Can account state be changed?
```

---

# Mass Assignment

Consider an input type:

```graphql
input UpdateUserInput {
    name: String
    email: String
    role: String
}
```

If a normal user should only modify:

```text
name
email
```

but the API also accepts:

```text
role
```

there may be a mass-assignment or authorisation issue.

Test schema-exposed input fields carefully.

---

# Input Object Enumeration

Introspection may reveal input types.

Conceptually:

```text
Mutation
   ↓
Argument
   ↓
Input Type
   ↓
Fields
```

For example:

```text
UpdateUserInput
 ├── username
 ├── email
 ├── role
 ├── verified
 └── status
```

Fields such as:

```text
role
verified
status
owner
permissions
```

deserve particular attention.

---

# GraphQL Aliases

GraphQL aliases allow multiple fields or operations to be requested under different names.

Example:

```graphql
query {
    first: user(id: 1) {
        username
    }

    second: user(id: 2) {
        username
    }
}
```

Response:

```json
{
  "data": {
    "first": {
      "username": "alice"
    },
    "second": {
      "username": "bob"
    }
  }
}
```

Aliases are a legitimate GraphQL feature.

However, they can interact with security controls.

---

# Alias Abuse

Suppose an application rate-limits:

```text
HTTP requests
```

rather than:

```text
GraphQL operations
```

One HTTP request may contain many aliases.

Conceptually:

```text
1 HTTP Request
      ↓
Alias 1
Alias 2
Alias 3
Alias 4
Alias 5
      ↓
5 Resolver Executions
```

This can potentially weaken naive request-based rate limiting.

---

# Safe Alias Testing

Begin with a very small number of operations.

For example:

```graphql
query {
    one: user(id: 1) {
        id
    }

    two: user(id: 2) {
        id
    }
}
```

Do not generate hundreds or thousands of aliases against production systems.

The objective is to determine whether controls operate per:

```text
HTTP request
```

or:

```text
GraphQL operation / resolver
```

---

# Aliases and Authentication Testing

Alias behaviour may also matter for operations such as:

```text
Login
OTP verification
Password reset
Username lookup
Coupon validation
```

The important question is:

> Does one HTTP request permit multiple security-sensitive attempts?

---

# GraphQL Batching

Some implementations allow multiple GraphQL operations in one HTTP request.

Conceptually:

```json
[
  {
    "query": "..."
  },
  {
    "query": "..."
  }
]
```

Batching can potentially interact with:

```text
Rate limiting
Brute-force protection
Monitoring
Logging
Resource consumption
```

Test only with small controlled batches.

---

# Rate Limiting

Rate limiting should consider:

```text
Requests
Operations
Aliases
Resolvers
User identity
Target object
Authentication action
```

A control that only counts HTTP requests may not adequately protect GraphQL operations.

---

# GraphQL CSRF

GraphQL endpoints may be vulnerable to CSRF when they accept requests that browsers can send cross-origin without requiring a CORS preflight.

Pay attention when mutations accept:

```text
GET
application/x-www-form-urlencoded
text/plain
```

or other browser-compatible request formats.

---

# CSRF Testing Workflow

```text
Identify State-Changing Mutation
        ↓
Determine Accepted HTTP Methods
        ↓
Determine Accepted Content Types
        ↓
Check Cookie Authentication
        ↓
Check CSRF Token
        ↓
Check SameSite
        ↓
Determine Whether Browser Can Submit Request
        ↓
Validate With Controlled Account
```

Refer to:

```text
docs/web/csrf.md
```

---

# JSON and CSRF

A GraphQL API that only accepts:

```text
POST
Content-Type: application/json
```

is more resistant to traditional form-based CSRF because browsers cannot normally submit arbitrary cross-origin JSON requests without triggering CORS preflight behaviour.

However, do not rely on content type alone.

Use:

```text
CSRF tokens
SameSite cookies
Origin validation
Appropriate CORS policy
```

where applicable.

---

# Content-Type Validation

Test whether:

```http
Content-Type: application/json
```

can be changed to:

```http
Content-Type: application/x-www-form-urlencoded
```

or:

```http
Content-Type: text/plain
```

while the mutation still executes.

If so, investigate CSRF implications.

---

# GET Mutations

State-changing operations should not normally be executable through GET requests.

Test whether the endpoint permits something equivalent to:

```text
GET /graphql?query=mutation{...}
```

If state-changing operations can be performed through GET, investigate:

```text
CSRF
Caching
Logging
URL leakage
```

---

# Injection Testing

GraphQL does not automatically eliminate injection vulnerabilities.

Resolver code may pass arguments into:

```text
SQL
NoSQL
Operating system commands
Templates
LDAP
Search engines
File paths
URLs
```

Example:

```graphql
query {
    search(term: "test") {
        id
        name
    }
}
```

The security question is:

> How does the resolver process `term`?

---

# SQL Injection

If a GraphQL resolver builds unsafe SQL queries:

```text
GraphQL Argument
      ↓
Resolver
      ↓
SQL Query
```

SQL injection may still occur.

Refer to:

```text
docs/web/sql-injection.md
```

---

# NoSQL Injection

GraphQL is frequently used with applications backed by:

```text
MongoDB
Document databases
NoSQL stores
```

GraphQL input should not be assumed safe merely because the schema specifies types.

Resolver and database logic still require review.

A dedicated page should cover:

```text
docs/web/nosql-injection.md
```

---

# Command Injection

If GraphQL input reaches system commands:

```text
GraphQL Argument
      ↓
Resolver
      ↓
Shell / Process
```

command injection may be possible.

Refer to:

```text
docs/web/command-injection.md
```

---

# SSRF

Resolvers may fetch remote resources.

Example conceptual query:

```graphql
query {
    preview(url: "https://example.com") {
        title
    }
}
```

Flow:

```text
GraphQL Argument
      ↓
Resolver
      ↓
Server-Side HTTP Request
```

This may create SSRF attack surface.

Refer to:

```text
docs/web/ssrf.md
```

---

# Path Traversal

GraphQL operations involving:

```text
Files
Exports
Downloads
Templates
Reports
Images
```

may expose path-related arguments.

Example:

```graphql
query {
    downloadFile(name: "report.pdf") {
        url
    }
}
```

Trace how the resolver handles the file identifier.

Refer to:

```text
docs/web/path-traversal.md
```

---

# File Uploads

GraphQL APIs can support file uploads through implementation-specific mechanisms such as multipart requests.

Review:

```text
File extension validation
MIME validation
Magic bytes
File size
Storage location
Authorisation
Metadata
Filename handling
Processing libraries
```

Refer to:

```text
docs/web/file-upload.md
```

---

# Business Logic

GraphQL exposes application functionality differently, but the underlying business rules remain critical.

For example:

```graphql
mutation {
    applyDiscount(code: "TEST") {
        total
    }
}
```

Questions include:

```text
Can the operation be repeated?
Can the same discount be reused?
Can negative quantities be supplied?
Can price fields be influenced?
Can workflow steps be skipped?
```

Refer to:

```text
docs/web/business-logic.md
```

---

# GraphQL Business Logic Mapping

Map important mutations to business actions.

For example:

```text
createOrder
      ↓
Creates Purchase

applyDiscount
      ↓
Changes Price

cancelOrder
      ↓
Changes Order State

approvePayment
      ↓
Changes Payment State

updateRole
      ↓
Changes Privilege
```

Then build security tests around the actual business rule.

---

# Query Depth

GraphQL allows nested queries.

Example:

```graphql
query {
    user {
        orders {
            items {
                product {
                    supplier {
                        products {
                            id
                        }
                    }
                }
            }
        }
    }
}
```

Deep nesting may require significant backend processing.

---

# Query Complexity

The actual cost of a GraphQL query may depend on:

```text
Depth
Number of fields
Number of objects
Resolver complexity
Database queries
Recursive relationships
Aliases
Fragments
```

Therefore:

```text
Small HTTP Request
```

can potentially trigger:

```text
Large Server Workload
```

---

# Denial-of-Service Considerations

GraphQL resource exhaustion may involve:

```text
Deep queries
Wide queries
Aliases
Recursive relationships
Large pagination values
Expensive resolvers
Batching
```

During authorised testing, avoid intentionally creating extreme resource consumption.

Start with small increases and observe:

```text
Response time
CPU impact where observable
Error behaviour
Complexity limits
Depth limits
```

---

# Pagination

Inspect pagination arguments such as:

```text
first
last
limit
offset
page
pageSize
```

Example:

```graphql
query {
    users(first: 20) {
        id
        username
    }
}
```

Questions include:

```text
Is there a maximum?
Can negative values be supplied?
Can extremely large values be supplied?
Does pagination bypass authorisation?
```

Use modest values when testing production systems.

---

# Fragments

Fragments allow reusable field selections.

Example:

```graphql
fragment UserFields on User {
    id
    username
    email
}

query {
    user(id: 123) {
        ...UserFields
    }
}
```

Fragments themselves are legitimate.

However, they can contribute to query complexity and should be included when understanding what the server actually executes.

---

# Directives

GraphQL supports directives such as:

```text
@include
@skip
```

Custom schemas may expose additional directives.

Introspection can reveal available directives.

Review custom directives because they may influence:

```text
Authentication
Authorisation
Caching
Data transformation
Resolver behaviour
```

---

# Error Handling

GraphQL errors may expose significant information.

Look for:

```text
Stack traces
Database errors
Internal paths
Framework names
Resolver names
Source files
SQL errors
NoSQL errors
Internal service URLs
Debug information
```

Example:

```json
{
  "errors": [
    {
      "message": "Database connection failed...",
      "extensions": {
        "stacktrace": []
      }
    }
  ]
}
```

Production responses should not expose unnecessary internal details.

---

# Partial Responses

GraphQL can return both:

```text
data
```

and:

```text
errors
```

in the same response.

Always inspect the entire response.

An error in one field does not necessarily mean the entire operation failed.

---

# Authentication

Test GraphQL authentication exactly as you would other application APIs.

Questions include:

```text
Can queries execute without a token?
Can mutations execute without a token?
Are expired tokens accepted?
Are different authentication mechanisms handled consistently?
Are subscriptions authenticated?
```

Refer to:

```text
docs/web/authentication.md
```

---

# Authorisation

GraphQL authorisation should be tested at several levels:

```text
Operation
Object
Field
Nested object
Mutation
Subscription
```

Conceptually:

```text
Can User Access Query?
        ↓
Can User Access Object?
        ↓
Can User Access Field?
        ↓
Can User Modify Object?
```

Refer to:

```text
docs/web/authorisation.md
```

---

# Multi-Tenant GraphQL

For multi-tenant applications, test whether tenant isolation is enforced inside resolvers.

Example:

```graphql
query {
    organisation(id: 123) {
        users {
            id
            email
        }
    }
}
```

Questions include:

```text
Can Tenant A query Tenant B?
Can nested objects cross tenants?
Can mutations modify another tenant?
Can IDs be enumerated?
```

---

# GraphQL and JWT

GraphQL APIs frequently use bearer tokens:

```http
Authorization: Bearer eyJ...
```

JWT security should be tested independently from GraphQL security.

Refer to:

```text
docs/web/jwt.md
```

---

# Burp Suite

Burp Suite is particularly useful for GraphQL because requests can be:

```text
Captured
Edited
Repeated
Compared
Fuzzed
Scanned
```

A practical GraphQL Burp workflow is:

```text
Proxy
  ↓
HTTP History
  ↓
GraphQL Request
  ↓
Repeater
  ↓
GraphQL Editor
  ↓
Modify Fields / Arguments
  ↓
Test Authorisation
  ↓
Test Mutations
  ↓
Test Inputs
  ↓
Intruder Where Appropriate
```

---

# Native GraphQL Support in Burp

Modern Burp Suite versions understand GraphQL requests and provide GraphQL-specific request editing functionality.

This makes it easier to separate and modify:

```text
Query
Variables
Operation name
```

rather than manually editing escaped JSON.

---

# Burp Scanner

Burp Scanner can assist with identifying GraphQL functionality and selected GraphQL security issues.

Useful automated checks can provide leads for:

```text
GraphQL endpoint discovery
Introspection
Schema-related information exposure
Content-type behaviour
```

Scanner findings should still be manually verified.

---

# Burp Repeater

Repeater should be one of the primary tools for manual GraphQL testing.

Use it for:

```text
Changing IDs
Changing fields
Adding fields
Changing arguments
Testing mutations
Changing variables
Testing aliases
Changing authentication
Testing content types
```

---

# Burp Intruder

Intruder can help with controlled testing of GraphQL variables.

Example:

```json
{
  "id": "§123§"
}
```

Potential uses include:

```text
Object ID testing
Input validation
Enumeration
Boundary testing
Controlled fuzzing
```

Be particularly careful with rate-sensitive operations.

---

# Burp Comparer

Comparer can help analyse differences between:

```text
User A response
User B response

Authenticated response
Unauthenticated response

Normal field set
Additional field set
```

This is useful when responses contain large JSON structures.

---

# Burp Logger

GraphQL applications can generate many similar requests.

Burp logging functionality can help identify:

```text
Operation names
Endpoints
Repeated mutations
Authentication changes
Interesting responses
```

---

# InQL

One of the most useful Burp extensions for GraphQL security testing is:

```text
InQL - GraphQL Scanner
```

InQL can assist with:

```text
GraphQL endpoint analysis
Schema analysis
Introspection
Query generation
Mutation generation
Subscription generation
Points-of-interest analysis
Burp integration
Sending generated operations to Repeater
Sending generated operations to Intruder
```

---

# Installing InQL

In Burp Suite:

```text
Extensions
   ↓
BApp Store
   ↓
Search:
InQL
   ↓
Install
```

After installation, InQL adds GraphQL-specific functionality to Burp.

---

# InQL Workflow

A practical workflow is:

```text
Identify GraphQL Endpoint
        ↓
InQL
        ↓
Retrieve / Import Schema
        ↓
Analyse Schema
        ↓
Generate Queries
        ↓
Generate Mutations
        ↓
Identify Interesting Operations
        ↓
Send to Repeater
        ↓
Manual Security Testing
```

---

# Why InQL Is Useful

A large schema may contain:

```text
Hundreds of types
Hundreds of fields
Dozens of mutations
Complex nested objects
```

Manually constructing every operation becomes inefficient.

InQL can help turn:

```text
Schema
```

into:

```text
Testable Requests
```

---

# InQL Schema Analysis

Once the schema is loaded, prioritise operations containing words such as:

```text
admin
user
account
role
permission
password
reset
token
secret
key
payment
order
delete
update
upload
export
internal
debug
```

Do not assume names alone indicate vulnerabilities.

Use them to prioritise manual testing.

---

# InQL to Repeater

One of the most useful workflows is:

```text
InQL
 ↓
Interesting Query
 ↓
Send to Repeater
 ↓
Modify Arguments
 ↓
Test Access Control
```

For example:

```text
user(id)
```

can be tested with controlled account identifiers.

---

# InQL to Intruder

For controlled enumeration:

```text
InQL
 ↓
Generated Query
 ↓
Intruder
 ↓
Mark Variable
 ↓
Controlled Payload Set
```

Always remain within assessment scope and rate limits.

---

# GraphQL Raider

Another Burp extension is:

```text
GraphQL Raider
```

GraphQL Raider is designed specifically for testing GraphQL endpoints.

It provides GraphQL-aware request handling inside Burp.

---

# GraphQL Raider Features

Useful functionality includes:

```text
GraphQL query editor
Variables editor
Readable GraphQL requests
Scanner insertion points
GraphQL-aware request manipulation
```

This can be useful when GraphQL requests are embedded inside JSON and are otherwise inconvenient to edit manually.

---

# Installing GraphQL Raider

In Burp:

```text
Extensions
   ↓
BApp Store
   ↓
Search:
GraphQL Raider
   ↓
Install
```

---

# GraphQL Raider Workflow

```text
Proxy
  ↓
Capture GraphQL Request
  ↓
GraphQL Raider
  ↓
Readable GraphQL Query
  ↓
Modify Query
  ↓
Modify Variables
  ↓
Send
  ↓
Analyse Response
```

---

# InQL vs GraphQL Raider

They overlap, but their strengths differ.

```text
InQL
 ↓
Schema analysis
Query generation
Mutation generation
Attack-surface mapping

GraphQL Raider
 ↓
Request editing
Variables editing
Scanner insertion points
GraphQL-aware Burp workflow
```

A useful setup is:

```text
Burp Native GraphQL Support
          +
InQL
          +
GraphQL Raider
```

You do not necessarily need all of them for every assessment.

---

# GraphQL Security Tester

The Burp BApp Store may also contain additional GraphQL-focused extensions.

One example is:

```text
GraphQL Security Tester
```

Such extensions can provide additional automation around GraphQL testing.

Treat extension-generated findings as leads and manually validate anything security-sensitive.

---

# Burp Extension Security

Burp extensions execute within your testing environment.

Before installing third-party extensions:

```text
Check maintainer
Check source
Check update history
Review permissions
Review network behaviour
Use trusted sources
```

Prefer installing through:

```text
Burp Suite
 ↓
Extensions
 ↓
BApp Store
```

where possible.

---

# Recommended GraphQL Burp Setup

For GraphQL-heavy assessments:

```text
Burp Proxy
Burp Repeater
Burp Intruder
Burp Comparer
Burp Scanner
Burp GraphQL Editor
DOM / Browser tooling where relevant

InQL
GraphQL Raider
```

Then use:

```text
Proxy
 ↓
Discover

InQL
 ↓
Map

Repeater
 ↓
Understand

Intruder
 ↓
Controlled Enumeration

Comparer
 ↓
Compare

Scanner
 ↓
Additional Leads

Manual Testing
 ↓
Confirm
```

---

# curl

GraphQL can also be tested using curl.

Example:

```bash
curl -k \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"query":"query{__typename}"}' \
  https://target.example/graphql
```

---

# Authenticated curl Request

```bash
curl -k \
  -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"query":"query{me{id username email}}"}' \
  https://target.example/graphql
```

---

# jq

`jq` is extremely useful for GraphQL responses.

Example:

```bash
curl -sk \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"query":"query{__typename}"}' \
  https://target.example/graphql | jq
```

This makes large JSON responses significantly easier to inspect.

---

# GraphQL Testing Checklist

## Discovery

```text
[ ] Check /graphql
[ ] Check /api
[ ] Check /api/graphql
[ ] Check /graphql/api
[ ] Check /graphql/graphql
[ ] Check /v1/graphql
[ ] Search JavaScript
[ ] Search source maps
[ ] Review HTTP history
[ ] Test universal query
[ ] Test GET
[ ] Test POST
```

## Schema

```text
[ ] Test introspection
[ ] Enumerate queries
[ ] Enumerate mutations
[ ] Enumerate subscriptions
[ ] Enumerate types
[ ] Enumerate input types
[ ] Enumerate enums
[ ] Enumerate directives
[ ] Review field suggestions
[ ] Review errors
```

## Authentication

```text
[ ] Query without authentication
[ ] Mutation without authentication
[ ] Invalid token
[ ] Expired token
[ ] Different user roles
[ ] Subscription authentication
```

## Authorisation

```text
[ ] Object-level access
[ ] Field-level access
[ ] Nested object access
[ ] Mutation authorisation
[ ] Cross-user access
[ ] Cross-tenant access
[ ] Administrative operations
```

## Data Exposure

```text
[ ] Hidden fields
[ ] Internal fields
[ ] Tokens
[ ] API keys
[ ] Email addresses
[ ] Phone numbers
[ ] Roles
[ ] Permissions
[ ] Internal IDs
[ ] Debug information
```

## Input Testing

```text
[ ] SQL injection
[ ] NoSQL injection
[ ] Command injection
[ ] SSRF
[ ] Path traversal
[ ] File handling
[ ] Template injection
[ ] Input validation
```

## Mutations

```text
[ ] Update another user
[ ] Delete another object
[ ] Modify role
[ ] Modify permissions
[ ] Change ownership
[ ] Change account state
[ ] Test hidden input fields
[ ] Test business rules
```

## Rate Limiting

```text
[ ] Aliases
[ ] Batching
[ ] Login operations
[ ] OTP operations
[ ] Password reset
[ ] Enumeration
[ ] Per-operation limits
```

## CSRF

```text
[ ] GET accepted
[ ] Form content type accepted
[ ] text/plain accepted
[ ] Cookie authentication
[ ] CSRF token
[ ] SameSite
[ ] Origin validation
```

## Complexity

```text
[ ] Query depth
[ ] Query width
[ ] Aliases
[ ] Fragments
[ ] Pagination
[ ] Recursive relationships
[ ] Complexity limits
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Intruder
[ ] Comparer
[ ] Scanner
[ ] Native GraphQL editor
[ ] InQL
[ ] GraphQL Raider
```

---

# GraphQL Quick Reference

```text
GRAPHQL ENDPOINT
       ↓
query{__typename}
       ↓
GRAPHQL CONFIRMED
       ↓
INTROSPECTION?
   ↓          ↓
 YES         NO
 ↓            ↓
SCHEMA      TRAFFIC
 ↓          ERRORS
 ↓          JS
 └──────┬─────┘
        ↓
MAP QUERIES
        ↓
MAP MUTATIONS
        ↓
MAP TYPES
        ↓
MAP INPUTS
        ↓
TEST AUTHENTICATION
        ↓
TEST OBJECT ACCESS
        ↓
TEST FIELD ACCESS
        ↓
TEST MUTATIONS
        ↓
TEST INPUTS
        ↓
TEST ALIASES
        ↓
TEST RATE LIMITS
        ↓
TEST CSRF
        ↓
TEST BUSINESS LOGIC
        ↓
REPORT
```

---

# High-Value GraphQL Targets

Prioritise schema objects containing:

```text
User
Account
Admin
Role
Permission
Organisation
Tenant
Payment
Order
Invoice
Token
APIKey
Secret
Password
Reset
File
Upload
Export
Report
```

And mutations containing:

```text
create
update
delete
change
reset
approve
cancel
invite
assign
grant
revoke
upload
export
```

---

# Evidence Collection

For confirmed GraphQL vulnerabilities, record:

```text
GraphQL endpoint
HTTP method
Authentication state
Operation name
Query / mutation
Variables
Affected object
Affected field
User role
Expected behaviour
Observed behaviour
Burp request
Burp response
Relevant schema information
Security impact
Reproduction steps
```

---

# Example Finding: GraphQL IDOR

```text
Finding:
GraphQL API Allows Unauthorised Access to Other Users' Data

Affected Endpoint:
/graphql

Affected Query:
user(id)

Observed:
A normal authenticated user was able to modify the user identifier supplied to the GraphQL user query and retrieve information associated with another controlled test account.

The API authenticated the request but did not enforce object-level authorisation for the requested user object.

Impact:
An authenticated user may access information belonging to other users.

Recommendation:
Implement object-level authorisation inside the relevant GraphQL resolver and verify that the authenticated user is authorised to access the requested object before returning data.
```

---

# Example Finding: Sensitive GraphQL Fields

```text
Finding:
GraphQL API Exposes Sensitive User Fields to Unprivileged Users

Observed:
The GraphQL User type exposed additional security-sensitive fields that were not used by the normal application interface.

An unprivileged authenticated account was able to request these fields directly.

Impact:
Sensitive user information may be disclosed to users who should not have access to it.

Recommendation:
Implement field-level authorisation and remove unnecessary sensitive fields from the externally accessible GraphQL schema.
```

---

# Example Finding: Introspection

```text
Finding:
GraphQL Introspection Enabled in Production

Observed:
The production GraphQL endpoint permitted schema introspection.

The schema disclosed available queries, mutations, types, arguments and input structures.

Impact:
An attacker can more easily map the GraphQL attack surface and identify sensitive or undocumented functionality.

Recommendation:
Where operationally appropriate, disable unrestricted introspection in production and ensure that security does not depend solely on hiding the schema. All operations must remain protected by appropriate authentication and authorisation controls.
```

---

# Example Finding: Alias Rate Limit Bypass

```text
Finding:
GraphQL Aliases Allow Multiple Security-Sensitive Operations Within a Single Rate-Limited Request

Observed:
The application applied rate limiting at the HTTP request level.

Multiple GraphQL aliases within a single request caused the security-sensitive resolver to execute multiple times while consuming only one HTTP request from the configured rate limit.

Impact:
An attacker may be able to increase the number of attempts against the affected operation beyond the intended rate limit.

Recommendation:
Apply rate limiting to the underlying security-sensitive operation rather than only to HTTP requests. Consider GraphQL operation counts, aliases and resolver execution when enforcing limits.
```

---

# Example Finding: GraphQL CSRF

```text
Finding:
GraphQL Mutation Vulnerable to Cross-Site Request Forgery

Observed:
The GraphQL endpoint authenticated users through cookies and accepted state-changing mutations using a browser-compatible request format without requiring a valid CSRF token.

Impact:
An attacker may be able to cause an authenticated user's browser to perform unintended state-changing operations.

Recommendation:
Require JSON POST requests, validate the Content-Type header, implement robust CSRF protection and configure authentication cookies with appropriate SameSite attributes.
```

---

# Example Finding: Excessive Data Exposure

```text
Finding:
GraphQL Schema Exposes Unnecessary Sensitive Account Data

Observed:
The GraphQL Account type exposed fields containing information not required by the normal client application.

These fields could be queried directly by a standard authenticated user.

Impact:
Users may obtain sensitive account information that should not be available to their role.

Recommendation:
Apply field-level authorisation and minimise the fields exposed through the GraphQL schema.
```

---

# Reporting Titles

Useful titles include:

```text
GraphQL API Allows Unauthorised Access to Other Users' Data

GraphQL Mutation Missing Object-Level Authorisation

GraphQL API Exposes Sensitive Fields to Unprivileged Users

GraphQL Introspection Enabled in Production

GraphQL Aliases Bypass Application Rate Limiting

GraphQL Mutation Vulnerable to CSRF

GraphQL API Exposes Administrative Mutation to Standard Users

GraphQL API Allows Cross-Tenant Data Access

GraphQL Error Responses Disclose Internal Application Information

GraphQL Query Complexity Allows Excessive Resource Consumption
```

Avoid vague titles such as:

```text
GraphQL Issue
```

Describe the actual security problem.

---

# Severity

Severity depends on demonstrated impact.

For example:

```text
Introspection Enabled
```

may primarily increase attack-surface visibility.

While:

```text
GraphQL IDOR
      ↓
Sensitive User Data
```

may have significant confidentiality impact.

And:

```text
Unauthorised Administrative Mutation
        ↓
Privilege Escalation
```

may be critical.

Report the actual impact rather than assigning severity simply because GraphQL is involved.

---

# Remediation

GraphQL security should be implemented in layers.

```text
Authentication
      ↓
Operation Authorisation
      ↓
Object Authorisation
      ↓
Field Authorisation
      ↓
Input Validation
      ↓
Rate Limiting
      ↓
Complexity Controls
      ↓
Secure Error Handling
```

---

# Enforce Object-Level Authorisation

Every resolver accessing an object should determine whether the authenticated user is authorised to access that object.

Do not rely solely on:

```text
Object IDs
Frontend restrictions
Hidden queries
Schema obscurity
```

---

# Enforce Field-Level Authorisation

Sensitive fields should be protected independently.

For example:

```text
User
 ├── username       Standard User
 ├── avatar         Standard User
 ├── email          Restricted
 ├── role           Restricted
 ├── apiKey         Highly Restricted
 └── internalNotes  Administrative
```

---

# Protect Mutations

Mutations should validate:

```text
Authentication
Object ownership
Role
Permission
Current state
Allowed transition
Allowed fields
```

before changing data.

---

# Restrict Introspection

Where appropriate for production deployments:

```text
Disable unrestricted introspection
```

or limit it to authorised administrative/development contexts.

However:

> Disabling introspection is not an authorisation control.

The API must remain secure even if the complete schema is known.

---

# Limit Query Depth

Configure a maximum acceptable query depth.

Conceptually:

```text
Query
 ↓
Depth Calculation
 ↓
Within Limit?
 ↓
YES → Execute
NO  → Reject
```

---

# Query Complexity Analysis

More advanced GraphQL implementations can calculate query cost.

For example:

```text
Simple scalar field = low cost

Large nested relationship = higher cost

Expensive resolver = high cost
```

Reject queries exceeding acceptable resource limits.

---

# Limit Aliases

Apply appropriate limits to:

```text
Aliases
Root fields
Operations
```

especially around security-sensitive resolvers.

---

# Rate Limit Resolvers

Do not rely exclusively on:

```text
Requests per IP
```

For sensitive functionality, rate limit based on:

```text
Account
Operation
Target object
Resolver
Authentication identity
```

---

# Pagination Limits

Set sensible maximum values for:

```text
first
last
limit
pageSize
```

Avoid allowing arbitrary result sizes.

---

# CSRF Protection

For state-changing GraphQL operations:

```text
Use POST
Require application/json
Validate Content-Type
Use CSRF protection
Configure SameSite cookies
Validate Origin where appropriate
```

---

# Input Validation

Validate GraphQL arguments according to their semantic purpose.

For example:

```text
ID
Email
URL
Filename
Quantity
Price
Role
Date
```

GraphQL type validation does not replace application-level validation.

---

# Secure Error Handling

Production GraphQL responses should avoid exposing:

```text
Stack traces
Source paths
Database queries
Internal service URLs
Secrets
Framework debugging data
```

Return useful but minimal error information.

---

# Logging

Security monitoring should capture:

```text
Operation name
Authenticated identity
Mutation
Target object
Failure
Rate-limit event
Complexity rejection
Authorisation rejection
```

Avoid unnecessarily logging:

```text
Passwords
Tokens
Secrets
Sensitive personal information
```

---

# Test After Remediation

After fixes, repeat:

```text
Original query
Changed object ID
Sensitive field query
Restricted mutation
Alias test
CSRF test
Introspection test
```

Confirm that controls operate at the correct GraphQL layer.

---

# Tools

Useful GraphQL security tools include:

```text
Burp Suite
Burp Repeater
Burp Intruder
Burp Scanner
Burp GraphQL Editor
InQL
GraphQL Raider
GraphiQL
GraphQL Voyager
curl
jq
Browser DevTools
```

For Burp-heavy assessments, a strong combination is:

```text
Burp Native GraphQL Support
          +
InQL
          +
GraphQL Raider
          +
Repeater
```

---

# References

## PortSwigger Web Security Academy: GraphQL API Vulnerabilities

https://portswigger.net/web-security/graphql

Covers:

```text
GraphQL endpoint discovery
Schema discovery
Introspection
Unsanitised arguments
Aliases
Rate limiting
GraphQL CSRF
Defences
```

---

## PortSwigger GraphQL Labs

https://portswigger.net/web-security/all-labs#graphql-api-vulnerabilities

Practical GraphQL security labs.

---

## PortSwigger: Working with GraphQL in Burp Suite

https://portswigger.net/burp/documentation/desktop/testing-workflow/working-with-graphql

Covers Burp Suite's native GraphQL workflow.

---

## InQL: GraphQL Scanner

https://portswigger.net/bappstore/296e9a0730384be4b2fffef7b4e19b1f

Burp Suite extension for GraphQL schema analysis, query generation and security testing.

---

## InQL GitHub

https://github.com/doyensec/inql

Open-source InQL project maintained by Doyensec.

---

## GraphQL Raider

https://portswigger.net/bappstore/4841f0d78a554ca381c65b26d48207e6

Burp Suite extension providing GraphQL-aware request editing and scanner insertion points.

---

## PortSwigger BApp Store

https://portswigger.net/bappstore

Search for additional GraphQL-focused Burp Suite extensions.

---

## GraphQL

https://graphql.org/

Official GraphQL documentation.

---

## OWASP GraphQL Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html

Security guidance covering:

```text
Input validation
Query limiting
Access control
Resource management
Server-side considerations
```

---

# Final GraphQL Testing Model

```text
                         APPLICATION
                              ↓
                     GRAPHQL ENDPOINT?
                              ↓
                             YES
                              ↓
                       query{__typename}
                              ↓
                      GRAPHQL CONFIRMED
                              ↓
               ┌──────────────┼──────────────┐
               ↓              ↓              ↓
             BURP            InQL       GRAPHQL RAIDER
               ↓              ↓              ↓
               └──────────────┼──────────────┘
                              ↓
                         MAP SCHEMA
                              ↓
               ┌──────────────┼──────────────┐
               ↓              ↓              ↓
            QUERIES        MUTATIONS        TYPES
               ↓              ↓              ↓
               └──────────────┼──────────────┘
                              ↓
                     IDENTIFY OBJECTS
                              ↓
                 TEST AUTHENTICATION
                              ↓
                  TEST AUTHORISATION
                              ↓
               ┌──────────────┼──────────────┐
               ↓              ↓              ↓
             OBJECT          FIELD         MUTATION
               ↓              ↓              ↓
               └──────────────┼──────────────┘
                              ↓
                       TEST INPUTS
                              ↓
               ┌──────────────┼──────────────┐
               ↓              ↓              ↓
             SQLi           NoSQLi          SSRF
               ↓              ↓              ↓
               └──────────────┼──────────────┘
                              ↓
                      TEST RATE LIMITS
                              ↓
                         ALIASES
                              ↓
                         BATCHING
                              ↓
                         TEST CSRF
                              ↓
                    TEST QUERY COMPLEXITY
                              ↓
                    TEST BUSINESS LOGIC
                              ↓
                     VALIDATE MANUALLY
                              ↓
                         DOCUMENT
                              ↓
                           REPORT
```

The key principle is:

> Do not treat GraphQL as a single endpoint that only needs conventional parameter fuzzing. Treat the schema as a map of the application's objects, relationships and operations. Enumerate the available attack surface, then test authentication, object-level authorisation, field-level authorisation, mutations, aliases, rate limiting, input handling and business rules systematically. Burp Suite, InQL and GraphQL Raider can make the schema and requests significantly easier to work with, but manual validation remains essential.
