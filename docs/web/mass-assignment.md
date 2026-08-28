# Mass Assignment

Mass assignment vulnerabilities occur when an application automatically binds attacker-controlled request parameters to internal application objects without restricting which properties may be modified.

Depending on the framework or programming language, the same problem may also be called:

```text
Mass Assignment
Auto-Binding
Object Binding
Object Injection
Over-Posting
```

A typical application may intentionally expose:

```json
{
    "firstName": "Alice",
    "lastName": "Example",
    "email": "alice@example.com"
}
```

but internally the user object may contain additional properties:

```json
{
    "id": 1001,
    "firstName": "Alice",
    "lastName": "Example",
    "email": "alice@example.com",
    "role": "user",
    "isAdmin": false,
    "accountStatus": "active",
    "credit": 0,
    "emailVerified": false
}
```

If the application blindly maps incoming JSON onto the complete user object, an attacker may be able to submit properties that were never intended to be user-controlled.

Conceptually:

```text
Attacker-Controlled Request
          ↓
      JSON / Form Data
          ↓
 Automatic Object Binding
          ↓
    Internal User Object
          ↓
Sensitive Property Modified
          ↓
      Security Impact
```

For example:

```json
{
    "firstName": "Alice",
    "isAdmin": true
}
```

The fundamental security question is:

> Can the client supply additional object properties that the application accepts even though those properties were not intended to be user-controlled?

!!! warning "Authorised Security Testing"
    Perform mass assignment testing only against applications included in the authorised assessment scope. Use controlled test accounts and harmless properties where possible. Avoid changing administrative roles, financial values, account ownership, or security settings unless the assessment explicitly requires it and the impact can be safely demonstrated.

---

# Core Concept

Consider an application containing a user object:

```text
User
├── id
├── username
├── email
├── firstName
├── lastName
├── role
├── isAdmin
├── accountStatus
├── emailVerified
└── credit
```

The profile form exposes only:

```text
firstName
lastName
email
```

The intended security boundary is therefore:

```text
CLIENT-CONTROLLABLE

firstName
lastName
email

-----------------------

SERVER-CONTROLLED

id
role
isAdmin
accountStatus
emailVerified
credit
```

A mass assignment vulnerability breaks this boundary.

---

# Vulnerable Data Flow

A vulnerable application may effectively perform:

```text
HTTP Request
     ↓
Parse JSON
     ↓
Convert Entire Request Body
     ↓
User Object
     ↓
Database Save
```

For example:

```javascript
app.patch("/profile", async (req, res) => {

    await User.updateOne(
        { _id: req.user.id },
        req.body
    );

    res.sendStatus(200);
});
```

The problem is:

```javascript
req.body
```

is passed directly into the database update.

If the model contains:

```text
role
isAdmin
emailVerified
```

the attacker may be able to modify those fields.

---

# Safer Data Flow

A safer approach explicitly selects permitted properties:

```text
HTTP Request
     ↓
Parse JSON
     ↓
Select Allowed Properties
     ↓
Validate Values
     ↓
Update Object
```

Conceptually:

```javascript
const allowed = {
    firstName: req.body.firstName,
    lastName: req.body.lastName,
    email: req.body.email
};
```

Then:

```javascript
await User.updateOne(
    { _id: req.user.id },
    allowed
);
```

---

# Why Mass Assignment Happens

Modern frameworks frequently provide automatic mapping between:

```text
HTTP Request
```

and:

```text
Application Object
```

because it makes development easier.

For example:

```text
JSON
   ↓
User Object

Form Parameters
   ↓
Model Object

GraphQL Input
   ↓
Domain Object
```

This becomes dangerous when:

```text
Client-Controlled Fields
```

and:

```text
Server-Controlled Fields
```

share the same object.

---

# Common Sensitive Properties

Interesting properties may include:

```text
role
roles
admin
isAdmin
administrator
isStaff
isSuperuser
permissions
privileges
accessLevel
accountType
userType
status
accountStatus
verified
emailVerified
phoneVerified
approved
active
enabled
disabled
locked
blocked
owner
ownerId
userId
accountId
organisationId
organizationId
tenantId
groupId
teamId
projectId
balance
credit
credits
price
discount
isPaid
paid
subscription
plan
tier
quota
limit
mfaEnabled
twoFactorEnabled
passwordResetRequired
```

These are discovery hints.

Do not blindly send every property to every endpoint.

---

# Mass Assignment vs IDOR / BOLA

These vulnerabilities are related but different.

## IDOR / BOLA

The attacker changes:

```text
Which object is accessed
```

Example:

```text
PATCH /api/users/1002
```

instead of:

```text
PATCH /api/users/1001
```

---

## Mass Assignment

The attacker changes:

```text
Which property is updated
```

Example:

```json
{
    "role": "admin"
}
```

instead of only:

```json
{
    "displayName": "Alice"
}
```

---

# Combined Attack

The two vulnerabilities can sometimes combine:

```text
Attacker
   ↓
Selects Another User
   ↓
IDOR / BOLA
   ↓
Adds Sensitive Property
   ↓
Mass Assignment
   ↓
Modifies Other User's Security State
```

Refer to:

```text
docs/web/idor-bola.md
```

---

# Mass Assignment vs Parameter Pollution

Mass assignment concerns:

```text
Unexpected object properties
```

Parameter pollution concerns:

```text
Multiple or manipulated representations
of parameters
```

For example:

```text
role=user&role=admin
```

is parameter pollution behaviour.

While:

```json
{
    "role": "admin"
}
```

being accepted when `role` was never intended to be user-controlled is mass assignment.

The two can sometimes interact.

---

# Mass Assignment vs Prototype Pollution

Mass assignment:

```text
Request Property
      ↓
Application Object
      ↓
Sensitive Application Property
```

Prototype pollution:

```text
Request Property
      ↓
Prototype Chain
      ↓
Inherited Property
      ↓
Application Gadget
```

They are different vulnerability classes.

Refer to:

```text
docs/web/prototype-pollution.md
```

---

# Mass Assignment vs Business Logic

Suppose the application intentionally allows:

```json
{
    "plan": "enterprise"
}
```

but fails to charge for the upgrade.

That may be:

```text
Business Logic Vulnerability
```

rather than mass assignment.

Mass assignment normally means:

```text
The field should not have been client-controllable
in the first place.
```

Refer to:

```text
docs/web/business-logic.md
```

---

# Mass Assignment vs Hidden Form Fields

A hidden field such as:

```html
<input
    type="hidden"
    name="role"
    value="user">
```

is still client-controlled.

If changing it modifies security-sensitive state:

```text
Access Control / Business Logic Issue
```

may exist.

Mass assignment becomes particularly relevant when the field is not even present in the intended client request but is accepted when manually added.

---

# Primary Testing Model

A useful methodology is:

```text
Observe Legitimate Request
          ↓
Identify Existing Properties
          ↓
Discover Additional Object Properties
          ↓
Choose Harmless Candidate
          ↓
Add Candidate Property
          ↓
Send Request
          ↓
Application Accepts It?
     ↓                 ↓
    NO                YES
     ↓                 ↓
 Continue         Verify State Change
                       ↓
             Security-Sensitive?
                  ↓         ↓
                 NO        YES
                  ↓         ↓
              Document    Finding
```

---

# Step 1: Identify Object Update Endpoints

Mass assignment is especially relevant to endpoints that:

```text
Create objects
Update objects
Modify profiles
Modify accounts
Change preferences
Create users
Update users
Create organisations
Modify projects
Manage subscriptions
Create API resources
```

Common methods:

```text
POST
PUT
PATCH
```

---

# High-Value Endpoint Patterns

Look for:

```text
/api/users
/api/profile
/api/account
/api/accounts
/api/settings
/api/preferences
/api/register
/api/signup
/api/projects
/api/organisations
/api/organizations
/api/teams
/api/admin/users
/api/subscriptions
/api/orders
/api/payments
/graphql
```

---

# Step 2: Capture the Legitimate Request

Example:

```http
PATCH /api/profile HTTP/1.1
Host: target.example
Authorization: Bearer USER_TOKEN
Content-Type: application/json

{
    "displayName": "Alice"
}
```

Send the request to:

```text
Burp Repeater
```

Establish a baseline.

---

# Step 3: Understand the Object

Determine what server-side object is likely being modified.

Potential sources include:

```text
API responses
GET endpoints
JavaScript
GraphQL schema
Documentation
Mobile application traffic
Error messages
Source maps
Swagger / OpenAPI
Previous application responses
Admin interfaces
Registration requests
Other roles
```

---

# Response Property Discovery

One of the strongest techniques is comparing:

```text
GET Object
```

with:

```text
PATCH Object
```

Example response:

```json
{
    "id": 1001,
    "displayName": "Alice",
    "email": "alice@example.com",
    "role": "user",
    "emailVerified": true,
    "createdAt": "2026-08-28T10:00:00Z"
}
```

Update request:

```json
{
    "displayName": "Alice"
}
```

Interesting difference:

```text
Response exposes:

role
emailVerified
createdAt

Request exposes:

displayName
```

This does not prove vulnerability.

But it gives candidate property names for controlled testing.

---

# Read / Write Asymmetry

A common mass assignment clue is:

```text
Object Returned by API
          ↓
Contains Many Properties
          ↓
Update Endpoint Accepts Same Object Type
          ↓
Client Normally Sends Only Some Properties
```

Example:

```text
GET /api/users/me
```

returns:

```json
{
    "id": 101,
    "name": "Alice",
    "email": "alice@example.com",
    "role": "user",
    "verified": true,
    "credits": 100
}
```

while:

```text
PATCH /api/users/me
```

normally sends:

```json
{
    "name": "Alice"
}
```

Candidates include:

```text
role
verified
credits
```

Testing must still be controlled.

---

# Step 4: Add One Property

Do not immediately send:

```json
{
    "role": "admin",
    "isAdmin": true,
    "balance": 999999,
    "verified": true,
    "ownerId": 1
}
```

This creates unnecessary impact and makes debugging difficult.

Instead:

```text
Add One Property at a Time
```

For example, where a harmless writable candidate exists:

```json
{
    "displayName": "Alice",
    "theme": "dark"
}
```

Then determine whether the additional property was accepted.

For security-sensitive fields, use the least impactful proof permitted by the engagement.

---

# Step 5: Verify Persistence

A:

```text
200 OK
```

does not prove mass assignment.

The application may silently ignore unknown properties.

Verify using:

```text
GET endpoint
UI
Second API request
Controlled account state
Database-visible application behaviour
```

---

# Example

Baseline:

```http
PATCH /api/profile HTTP/1.1
Content-Type: application/json

{
    "displayName": "Alice"
}
```

Candidate test:

```http
PATCH /api/profile HTTP/1.1
Content-Type: application/json

{
    "displayName": "Alice",
    "nickname": "AM-MASS-001"
}
```

Then retrieve:

```http
GET /api/profile HTTP/1.1
```

If:

```json
{
    "nickname": "AM-MASS-001"
}
```

appears unexpectedly, the property is writable.

Whether this is security-sensitive depends on what the property represents.

---

# Security-Sensitive Testing

After establishing that unexpected properties can be bound, determine whether a security-sensitive property is exposed.

Possible categories:

```text
Authorisation
Identity
Verification
Ownership
Financial
Subscription
Workflow
Security Controls
```

---

# Authorisation Properties

Examples:

```text
role
roles
isAdmin
admin
permissions
accessLevel
userType
isStaff
isSuperuser
```

These are high-risk properties.

A secure application should not permit ordinary users to assign their own privileges.

---

# Identity Properties

Examples:

```text
userId
accountId
ownerId
customerId
organisationId
tenantId
```

Changing these may alter:

```text
Ownership
Object relationships
Tenant context
```

and can potentially lead to authorisation failures.

---

# Verification Properties

Examples:

```text
verified
emailVerified
phoneVerified
approved
identityVerified
kycVerified
```

These may bypass verification workflows if improperly client-controllable.

---

# Account State Properties

Examples:

```text
active
enabled
disabled
locked
blocked
status
accountStatus
```

These may affect:

```text
Account lifecycle
Security controls
Administrative workflows
```

---

# Financial Properties

Examples:

```text
balance
credit
credits
price
discount
amount
paid
isPaid
```

These are particularly sensitive.

Do not modify real financial values during testing.

Use controlled test environments or explicitly approved test accounts.

---

# Subscription Properties

Examples:

```text
plan
tier
subscription
premium
pro
enterprise
quota
limit
```

If user-controlled, these may allow:

```text
Feature entitlement bypass
Quota manipulation
Subscription bypass
```

---

# Security-Control Properties

Examples:

```text
mfaEnabled
twoFactorEnabled
passwordResetRequired
forcePasswordChange
securityLevel
```

Changing security settings can create significant impact.

Use extreme caution.

---

# Nested Mass Assignment

Mass assignment may occur inside nested objects.

Example legitimate request:

```json
{
    "profile": {
        "displayName": "Alice"
    }
}
```

Potential candidate:

```json
{
    "profile": {
        "displayName": "Alice",
        "verified": true
    }
}
```

---

# Deeply Nested Objects

Example:

```json
{
    "user": {
        "profile": {
            "settings": {
                "theme": "dark"
            }
        }
    }
}
```

The vulnerable binding may occur at:

```text
Top level
Nested level
Multiple levels
```

Test the actual application structure.

---

# Nested Relationship Manipulation

Example:

```json
{
    "project": {
        "name": "Test",
        "owner": {
            "id": 102
        }
    }
}
```

Potential impact:

```text
Ownership manipulation
```

if nested relationships are automatically bound.

---

# Arrays

Mass assignment can also affect arrays.

Example:

```json
{
    "roles": [
        "user"
    ]
}
```

If the client can submit:

```json
{
    "roles": [
        "user",
        "administrator"
    ]
}
```

and the server accepts it:

```text
Privilege Escalation
```

may occur.

---

# Object Collections

Example:

```json
{
    "permissions": [
        {
            "name": "read"
        }
    ]
}
```

Test whether unexpected permission objects can be added only where safe and explicitly authorised.

---

# Null Values

Object binders may behave differently when a property is:

```json
null
```

For example:

```json
{
    "ownerId": null
}
```

This may:

```text
Remove ownership
Trigger defaults
Bypass validation
Create orphaned objects
```

Use controlled objects.

---

# Boolean Values

Security properties are often Boolean:

```text
true
false
```

Examples:

```text
isAdmin
verified
enabled
premium
```

Check whether the application accepts the field at all before assessing impact.

---

# Type Confusion

An application may expect:

```json
{
    "role": "user"
}
```

but receive:

```json
{
    "role": [
        "user",
        "admin"
    ]
}
```

or:

```json
{
    "role": {
        "name": "admin"
    }
}
```

This is not necessarily mass assignment by itself, but unsafe object binding and type coercion can interact.

---

# JSON Requests

JSON APIs are particularly relevant because object structure maps naturally onto application models.

Example:

```http
PATCH /api/account HTTP/1.1
Content-Type: application/json

{
    "name": "Alice"
}
```

Candidate:

```json
{
    "name": "Alice",
    "accountStatus": "active"
}
```

---

# Form-Encoded Requests

Mass assignment can also occur with:

```text
application/x-www-form-urlencoded
```

Example:

```text
name=Alice&email=alice@example.com
```

Candidate:

```text
name=Alice&email=alice@example.com&role=admin
```

Use a harmless equivalent when first establishing behaviour.

---

# Multipart Requests

Example:

```http
Content-Disposition: form-data; name="displayName"

Alice
```

Additional form fields may also be automatically bound.

Mass assignment is not limited to JSON.

---

# Query Parameters

Some frameworks bind query parameters to objects.

Example:

```text
/profile/update?displayName=Alice
```

Candidate additional properties may also be accepted through the query string.

---

# Property Naming Variations

Applications may use naming conventions such as:

```text
isAdmin
is_admin
admin
administrator
Admin
role
Role
user_role
userRole
```

Do not assume one naming convention.

Technology identification can help predict likely names.

---

# JavaScript Property Discovery

Frontend JavaScript frequently reveals internal field names.

Search for:

```text
role
permissions
verified
isAdmin
accountStatus
subscription
ownerId
```

Example:

```bash
grep -RniE \
'role|roles|permission|isAdmin|admin|verified|accountStatus|ownerId|userId|accountId|tenantId|subscription|plan|credits|balance' \
.
```

Refer to:

```text
docs/web/reconnaissance/javascript-analysis.md
```

---

# JavaScript Models

Frontend applications may define TypeScript interfaces.

Example:

```typescript
interface User {
    id: number;
    name: string;
    email: string;
    role: string;
    verified: boolean;
}
```

Even if the UI only permits editing:

```text
name
email
```

the interface reveals:

```text
role
verified
```

as candidate server-side properties.

---

# Source Maps

Source maps can reveal:

```text
Interfaces
Models
DTOs
API clients
Validation schemas
Administrative fields
```

Search:

```text
.js.map
```

and inspect them where exposed.

Refer to:

```text
docs/web/information-disclosure.md
```

---

# API Documentation

Look for:

```text
Swagger
OpenAPI
GraphQL schema
Postman collections
API documentation
```

These may reveal fields that the normal user interface never sends.

---

# OpenAPI

Example schema:

```yaml
User:
  type: object
  properties:
    id:
      type: integer
    name:
      type: string
    role:
      type: string
    verified:
      type: boolean
```

Compare schemas used for:

```text
Response
```

and:

```text
Update Request
```

A secure API often uses separate schemas.

---

# DTOs

A common defensive architecture uses:

```text
Domain Object
```

and separate:

```text
Data Transfer Objects
```

For example:

```text
User
```

contains:

```text
id
name
email
role
verified
```

while:

```text
UpdateProfileRequest
```

contains only:

```text
name
email
```

This significantly reduces mass assignment risk.

---

# GraphQL

GraphQL often makes accepted input fields explicit.

Example:

```graphql
mutation {
    updateProfile(
        input: {
            displayName: "Alice"
        }
    ) {
        id
        displayName
    }
}
```

If introspection reveals:

```graphql
input UpdateUserInput {
    displayName: String
    role: String
    verified: Boolean
}
```

then:

```text
role
verified
```

deserve careful review.

Refer to:

```text
docs/web/graphql.md
```

---

# GraphQL Input Types

GraphQL input types are valuable because they explicitly enumerate accepted properties.

Example:

```graphql
input UpdateAccountInput {
    name: String
    email: String
    accountType: String
}
```

Ask:

```text
Should the current role be allowed to control accountType?
```

---

# GraphQL Is Not Automatically Safe

A strict GraphQL schema prevents arbitrary unknown fields from being submitted.

However, if the schema itself exposes a sensitive field:

```graphql
role: String
```

to an inappropriate mutation:

```text
Authorisation / Mass Assignment Style Issue
```

may still exist.

---

# REST APIs

REST APIs frequently expose mass assignment because update endpoints commonly accept JSON objects.

Prioritise:

```text
POST /resource
PUT /resource/{id}
PATCH /resource/{id}
```

---

# PUT vs PATCH

Test both where supported.

The application may implement:

```text
PUT
```

using complete model binding while:

```text
PATCH
```

uses explicit field handling.

Or the reverse.

Do not assume they share implementation.

---

# PATCH Documents

Some APIs use:

```text
JSON Patch
```

Example:

```json
[
    {
        "op": "replace",
        "path": "/displayName",
        "value": "Alice"
    }
]
```

If arbitrary paths are permitted:

```json
[
    {
        "op": "replace",
        "path": "/role",
        "value": "admin"
    }
]
```

could expose a similar security issue.

Use harmless candidate paths first.

---

# Merge Patch

An API using:

```text
application/merge-patch+json
```

may accept partial object updates.

Example:

```json
{
    "displayName": "Alice"
}
```

The same mass assignment questions apply.

---

# Registration Endpoints

Registration is a classic target.

Normal request:

```json
{
    "username": "alice",
    "email": "alice@example.com",
    "password": "ExamplePassword"
}
```

Potential hidden server properties:

```text
role
verified
accountType
credits
subscription
```

Registration endpoints are interesting because:

```text
No existing account privileges
```

may be required to reach them.

---

# User Creation

Administrative user creation endpoints may accept:

```json
{
    "username": "alice",
    "role": "user"
}
```

Determine whether lower-privileged administrative roles can assign:

```text
Higher roles
```

This may be both:

```text
Mass Assignment
```

and:

```text
Broken Function-Level Authorisation
```

depending on the design.

---

# Profile Update Endpoints

Profile endpoints are common mass assignment candidates because developers may bind:

```text
User object
```

directly.

Normal fields:

```text
name
email
phone
address
```

Sensitive internal fields:

```text
role
status
verified
permissions
```

---

# Organisation Objects

Example:

```json
{
    "name": "Example Organisation"
}
```

Internal properties might include:

```text
ownerId
billingPlan
approved
tenantId
quota
```

---

# Project Objects

Example:

```json
{
    "name": "Research"
}
```

Potential internal properties:

```text
ownerId
visibility
organisationId
adminOnly
status
```

---

# Order Objects

Normal client properties might include:

```text
product
quantity
shippingAddress
```

Sensitive server properties may include:

```text
price
discount
paid
status
ownerId
```

Price and payment state should generally be derived or validated server-side.

---

# Payment Objects

Be extremely cautious.

Potential properties:

```text
amount
currency
paid
paymentStatus
discount
refund
```

Never modify real payment state during testing.

Use:

```text
Sandbox
Test payment provider
Controlled transaction
```

where explicitly authorised.

---

# File Metadata

Mass assignment can also affect uploaded-file metadata.

Example:

```json
{
    "filename": "report.pdf",
    "private": true,
    "ownerId": 101
}
```

If a client can change:

```text
ownerId
private
accessLevel
```

unexpected access-control consequences may occur.

---

# Ownership Fields

Ownership fields deserve particular attention:

```text
owner
ownerId
createdBy
userId
accountId
customerId
```

If writable, they may create:

```text
Cross-user object reassignment
```

or interact with:

```text
IDOR / BOLA
```

---

# Tenant Fields

Examples:

```text
tenant
tenantId
organisationId
organizationId
```

These can become extremely security-sensitive in SaaS systems.

Detailed tenant-isolation testing belongs under:

```text
Cloud Security
```

but web/API mass assignment testing should still recognise tenant identifiers as sensitive fields.

---

# Frameworks

Mass assignment behaviour varies by framework.

Common environments include:

```text
Ruby on Rails
Spring MVC
ASP.NET
Node.js
Mongoose
Django
Laravel
Grails
Java object mappers
```

Framework identification can therefore help guide testing.

---

# Ruby on Rails

Mass assignment is historically associated strongly with Rails.

Modern Rails uses:

```text
Strong Parameters
```

to restrict permitted fields.

Conceptually:

```ruby
params.require(:user).permit(
  :name,
  :email
)
```

Sensitive properties should not be included unless explicitly required.

---

# Spring MVC

Spring may bind HTTP parameters to Java objects.

A dangerous architecture may bind directly to a domain object containing:

```text
role
admin
permissions
```

OWASP recommends controlling which fields can be bound.

Safer designs often use dedicated request DTOs.

---

# ASP.NET

ASP.NET model binding can map request properties onto model objects.

Potentially sensitive properties should not become client-controlled simply because they exist in the model.

Use:

```text
Dedicated view models
DTOs
Explicit binding controls
```

where appropriate.

---

# Node.js

A dangerous pattern is:

```javascript
Object.assign(user, req.body);
```

or:

```javascript
await User.updateOne(
    { _id: id },
    req.body
);
```

The issue is:

```text
Entire attacker-controlled object
```

is passed to a sensitive update operation.

---

# Mongoose

Dangerous conceptual pattern:

```javascript
User.findByIdAndUpdate(
    req.user.id,
    req.body
);
```

Safer:

```javascript
User.findByIdAndUpdate(
    req.user.id,
    {
        name: req.body.name,
        email: req.body.email
    }
);
```

Schema validation remains important, but:

```text
Field existence in a schema
```

does not mean:

```text
User should be allowed to control it.
```

---

# Django

Django ModelForms and serializers should expose only intended fields.

Avoid patterns that automatically expose:

```text
All model fields
```

to untrusted clients without reviewing which fields are security-sensitive.

---

# Django REST Framework

Serializer fields should be explicitly reviewed.

Properties may need to be:

```text
read_only
```

or excluded entirely from user-controlled serializers.

---

# Laravel

Laravel provides model mechanisms for controlling mass assignment.

Common concepts include:

```text
$fillable
$guarded
```

The security objective is:

```text
Explicitly control which properties can be assigned.
```

---

# Object Mappers

Java object-mapping libraries such as:

```text
Jackson
GSON
```

can map JSON onto application objects.

The security concern remains:

```text
Does the input model contain properties
that the client should not control?
```

---

# Burp Suite Workflow

Burp is particularly useful because mass assignment testing requires:

```text
Request modification
Property discovery
Response comparison
State verification
```

Recommended workflow:

```text
Proxy
  ↓
Capture Object Update
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Discover Candidate Properties
  ↓
Add One Property
  ↓
Send
  ↓
Compare Response
  ↓
Retrieve Object
  ↓
Verify Persistence
```

---

# Burp Proxy

Use Proxy to identify:

```text
POST
PUT
PATCH
```

requests containing:

```text
JSON
Form data
GraphQL mutations
```

Pay particular attention to requests that modify:

```text
Users
Accounts
Projects
Orders
Settings
```

---

# Burp Repeater

Repeater is the primary manual tool.

Baseline:

```http
PATCH /api/profile HTTP/1.1
Host: target.example
Content-Type: application/json

{
    "displayName": "Alice"
}
```

Candidate:

```http
PATCH /api/profile HTTP/1.1
Host: target.example
Content-Type: application/json

{
    "displayName": "Alice",
    "nickname": "AM-MASS-001"
}
```

Compare:

```text
Status
Response body
Error
Object representation
Application state
```

---

# Burp Comparer

Comparer is useful when the response differences are subtle.

Compare:

```text
Baseline response
```

against:

```text
Response with additional property
```

Look for:

```text
New fields
Changed values
Different object state
Different response length
Different errors
```

---

# Burp Intruder

Intruder can help test a small candidate list of property names.

For example, a request body might conceptually contain:

```json
{
    "displayName": "Alice",
    "§PROPERTY§": "AM-MASS-001"
}
```

Candidate property list:

```text
nickname
description
timezone
language
```

Start with low-impact properties.

Do not blindly fuzz dangerous properties across production objects.

---

# Param Miner

Param Miner is useful for discovering hidden inputs that affect application behaviour.

It can identify:

```text
Parameters
Headers
Cookies
```

that are not normally visible during standard interaction.

For mass assignment, this can help identify:

```text
Unexpected accepted parameters
```

although Param Miner was not created specifically for mass assignment.

Install through:

```text
Burp Suite
  ↓
Extensions
  ↓
BApp Store
  ↓
Param Miner
```

Official BApp Store:

https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943

---

# Param Miner Workflow

Select an interesting request.

Then:

```text
Right Click
   ↓
Extensions / Param Miner
   ↓
Guess Parameters
```

Exact context-menu wording may vary between Burp versions.

Param Miner performs differential testing to identify inputs that influence responses.

Potential workflow:

```text
Profile Update Request
       ↓
Param Miner
       ↓
Hidden Parameter Candidate
       ↓
Manual Repeater Verification
       ↓
Retrieve Object
       ↓
Determine Security Impact
```

---

# Important Param Miner Limitation

Finding that:

```text
Parameter X affects response
```

does not prove:

```text
Mass Assignment
```

You must verify:

```text
Property was accepted
Property changed object state
Property should not be client-controlled
Security impact exists
```

---

# OWASP API Security Top 10 Scanner

The Burp BApp Store includes:

```text
OWASP API Security Top 10 Scanner
```

which performs API-focused active and passive testing.

Its active checks include:

```text
Mass assignment
Broken object authorisation
Broken function authorisation
Injection
SSRF
Parameter pollution
```

This makes it directly relevant to this page.

Official BApp Store:

https://portswigger.net/bappstore/4894a4ba29ec4303990196a6bbc5d67b

---

# API Scanner Workflow

Conceptually:

```text
Proxy API Traffic
      ↓
Identify API Endpoint
      ↓
Run API Security Audit
      ↓
Mass Assignment Candidates
      ↓
Review Suggested Fields
      ↓
Manual Repeater Verification
      ↓
Confirm State Change
      ↓
Determine Security Impact
```

Automated results should always be manually validated.

---

# API Scanner AI-Assisted Suggestions

Where supported and enabled, the API scanner can suggest context-specific mass-assignment fields based on observed request bodies.

For example, an account object might produce candidates conceptually related to:

```text
role
status
verified
plan
```

Treat these as:

```text
Testing Leads
```

not confirmed vulnerabilities.

---

# Burp Scanner

Burp Scanner can also help identify unexpected input behaviour and API vulnerabilities.

However, mass assignment often requires:

```text
Business Context
Object Knowledge
State Verification
```

which makes manual testing especially important.

---

# PyBurp

For complex APIs, the BApp Store also contains:

```text
PyBurp
```

which allows Python-based request and response processing within Burp.

It supports:

```text
HTTP modification
WebSocket modification
Nested JSON transformations
Parameter fuzzing
Custom scanning
```

Official BApp Store:

https://portswigger.net/bappstore/d8969aceb89d4dc38e996f3c3579880d

This can be useful when testing APIs with:

```text
Deeply nested JSON
Custom encodings
Repeated transformations
Complex request structures
```

---

# When PyBurp Is Useful

Suppose requests contain:

```json
{
    "account": {
        "profile": {
            "settings": {
                "displayName": "Alice"
            }
        }
    }
}
```

A small Python transformation can systematically insert candidate properties into:

```text
settings
profile
account
```

without manually rebuilding every request.

For ordinary JSON APIs:

```text
Repeater
```

is usually simpler.

---

# Burp Logger

Use Logger to understand:

```text
Requests generated by extensions
Scanner activity
Unexpected automated traffic
```

This is particularly useful when active extensions are installed.

---

# Burp Extension Safety

Burp extensions can:

```text
Read assessment traffic
Modify requests
Send requests
Access sensitive application data
```

Review extensions before using them on sensitive engagements.

Do not install unnecessary extensions simply because they appear useful.

---

# Custom Mass Assignment Helper

A small Python helper can compare candidate properties against a controlled endpoint.

The script below intentionally uses:

```text
One candidate at a time
```

and prints response metadata.

```python
#!/usr/bin/env python3

import copy
import json
import requests


URL = "https://target.example/api/profile"

TOKEN = "REPLACE_WITH_TEST_TOKEN"

BASELINE = {
    "displayName": "Alice"
}

CANDIDATES = {
    "nickname": "AM-MASS-001",
    "timezone": "UTC",
    "language": "en"
}

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def send(payload):

    response = requests.patch(
        URL,
        headers=HEADERS,
        json=payload,
        timeout=10,
        allow_redirects=False
    )

    return response


baseline_response = send(BASELINE)

print(
    "[BASELINE]",
    baseline_response.status_code,
    len(baseline_response.content)
)


for property_name, value in CANDIDATES.items():

    payload = copy.deepcopy(BASELINE)

    payload[property_name] = value

    response = send(payload)

    print(
        f"[TEST] {property_name:20} "
        f"status={response.status_code} "
        f"length={len(response.content)}"
    )
```

Use only:

```text
Low-impact candidate fields
Controlled accounts
Authorised endpoints
```

until behaviour is understood.

---

# State Verification Helper

A stronger workflow retrieves the object after each test.

```python
#!/usr/bin/env python3

import copy
import requests


UPDATE_URL = "https://target.example/api/profile"
READ_URL = "https://target.example/api/profile"

TOKEN = "REPLACE_WITH_TEST_TOKEN"

BASELINE = {
    "displayName": "Alice"
}

CANDIDATES = {
    "nickname": "AM-MASS-001",
    "timezone": "UTC"
}

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def update(payload):

    return requests.patch(
        UPDATE_URL,
        headers=HEADERS,
        json=payload,
        timeout=10,
        allow_redirects=False
    )


def read():

    return requests.get(
        READ_URL,
        headers=HEADERS,
        timeout=10,
        allow_redirects=False
    )


for property_name, value in CANDIDATES.items():

    payload = copy.deepcopy(BASELINE)

    payload[property_name] = value

    update_response = update(payload)

    read_response = read()

    print()
    print(f"Property: {property_name}")
    print(
        f"Update: {update_response.status_code}"
    )
    print(
        f"Read:   {read_response.status_code}"
    )

    try:

        body = read_response.json()

        print(
            f"Returned value: "
            f"{body.get(property_name)!r}"
        )

    except ValueError:

        print("Read response was not JSON.")
```

This is stronger because:

```text
HTTP 200
```

is not treated as proof.

The script verifies whether the property appears in the retrieved object.

---

# Candidate Wordlist

A general discovery wordlist might contain:

```text
role
roles
admin
isAdmin
administrator
isStaff
isSuperuser
permission
permissions
accessLevel
userType
verified
emailVerified
phoneVerified
approved
active
enabled
locked
blocked
status
accountStatus
owner
ownerId
userId
accountId
customerId
organisationId
organizationId
tenantId
teamId
groupId
projectId
plan
tier
subscription
premium
quota
limit
```

Do not use this as a blind production fuzzing list.

First derive candidates from:

```text
Application responses
JavaScript
API documentation
Schemas
Technology stack
```

---

# Candidate Generation Strategy

Prioritise candidates in this order:

```text
1. Fields observed in API responses
2. Fields observed in JavaScript
3. Fields from GraphQL / OpenAPI schemas
4. Fields observed under another role
5. Framework-specific model names
6. Generic candidate wordlist
```

This produces much less noise than blind fuzzing.

---

# Compare User and Admin Traffic

If controlled accounts with different roles are available:

```text
Normal User
Administrator
```

compare requests for similar functionality.

For example:

Normal user:

```json
{
    "name": "Alice"
}
```

Administrator:

```json
{
    "name": "Alice",
    "role": "manager",
    "enabled": true
}
```

This reveals high-confidence candidate properties:

```text
role
enabled
```

Now determine whether the normal-user endpoint improperly accepts them.

---

# Role-Differential Testing

Architecture:

```text
Admin UI
   ↓
Captures Sensitive Property Names
   ↓
Normal User Endpoint
   ↓
Add Same Property
   ↓
Accepted?
```

This is one of the strongest mass assignment discovery techniques.

---

# Registration vs Administration

Compare:

```text
POST /register
```

with:

```text
POST /admin/users
```

Admin request may reveal fields such as:

```text
role
status
verified
```

Test whether the public registration endpoint accepts the same fields only with safe, authorised values and controlled accounts.

---

# Create vs Update

Properties rejected during:

```text
Create
```

may be accepted during:

```text
Update
```

and vice versa.

Test both:

```text
POST
PATCH
PUT
```

where available.

---

# API Version Comparison

Compare:

```text
/api/v1/profile
/api/v2/profile
```

Different versions may use different serializers or DTOs.

An older endpoint may expose broader object binding.

---

# Content-Type Variation

Where legitimately supported, compare:

```text
application/json
application/x-www-form-urlencoded
multipart/form-data
```

Different parsers may produce different binding behaviour.

---

# Case Sensitivity

Some frameworks treat property names differently.

For example:

```text
isAdmin
IsAdmin
isadmin
```

Only test variations when justified by the identified technology.

---

# Unknown Property Behaviour

Observe what happens when you send:

```json
{
    "AM_UNKNOWN_PROPERTY": "AM-MASS-001"
}
```

Possible outcomes:

```text
400 Unknown Property
Ignored
Accepted
Stored
Reflected
```

This can reveal the binding strategy.

---

# Strict vs Permissive Deserialisation

Strict:

```text
Unknown Property
      ↓
Reject Request
```

Permissive:

```text
Unknown Property
      ↓
Ignore / Bind
```

Permissive behaviour does not automatically mean mass assignment, but it helps understand the attack surface.

---

# Error Messages

Errors may reveal internal property names.

Example:

```text
Property 'accountRole' is read-only
```

or:

```text
Cannot bind field 'isVerified'
```

This can reveal:

```text
Internal object structure
```

without proving exploitability.

---

# Validation Errors

Suppose:

```json
{
    "role": "AM-MASS-001"
}
```

returns:

```text
role must be one of USER, MANAGER, ADMIN
```

This strongly suggests:

```text
role is recognised
```

but does not prove the current user can successfully modify it.

Continue with the minimum safe validation needed.

---

# Differential Errors

Compare:

Unknown field:

```text
foobar
→ ignored
```

Candidate:

```text
role
→ validation error
```

This suggests:

```text
role
```

is a real property.

Burp Comparer is useful here.

---

# Read-Only Properties

A secure API may return:

```json
{
    "role": "user"
}
```

but reject attempts to modify it:

```json
{
    "role": "manager"
}
```

Expected response:

```text
400
403
Validation error
Field ignored
```

depending on API design.

---

# Server-Derived Values

Properties such as:

```text
price
ownerId
createdAt
role
verified
```

should often be derived server-side.

Example:

```text
ownerId
```

should usually come from:

```text
Authenticated user identity
```

rather than:

```text
Client request
```

---

# Mass Assignment in Microservices

An API gateway may validate:

```text
Public Request DTO
```

but internal services may accept broader objects.

Architecture:

```text
Client
  ↓
API Gateway
  ↓
Service A
  ↓
Internal JSON
  ↓
Service B
```

Security issues may arise when:

```text
Unexpected client properties survive
```

through multiple layers.

---

# Internal APIs

Do not assume internal endpoints are safe because they are not exposed directly.

If a public service forwards user-controlled objects into:

```text
Internal APIs
```

mass assignment can propagate downstream.

---

# Mass Assignment and Trust Boundaries

Map:

```text
Browser
  ↓
API
  ↓
Controller
  ↓
DTO
  ↓
Service
  ↓
ORM
  ↓
Database
```

At each boundary ask:

```text
Which fields remain attacker-controlled?
```

---

# Source Code Review

Look for patterns where entire request objects are passed directly into persistence functions.

Examples:

```text
req.body
request.json
request.data
params
```

combined with:

```text
update
save
create
merge
assign
bind
```

---

# JavaScript / Node.js Search

Example:

```bash
grep -RniE \
'Object\.assign|req\.body|findByIdAndUpdate|updateOne|findOneAndUpdate|\.create\(' \
.
```

Review manually.

---

# Java Search

Look for:

```text
@RequestBody
BeanUtils
ModelAttribute
ObjectMapper
```

and model objects containing security-sensitive fields.

---

# PHP Search

Look for:

```text
fill(
create(
update(
request->all
```

depending on framework.

---

# Python Search

Look for patterns involving:

```text
serializer
ModelForm
request.data
objects.create
update
```

and determine whether field allowlisting exists.

---

# Code Review Question

For every update handler ask:

```text
Does this code explicitly specify
which properties are allowed?
```

If not:

```text
Investigate Further
```

---

# Secure DTO Pattern

Example conceptual model:

```text
User Domain Object

id
name
email
role
verified
credits
```

Separate request DTO:

```text
UpdateProfileRequest

name
email
```

Then:

```text
UpdateProfileRequest
       ↓
Validation
       ↓
Explicit Mapping
       ↓
User
```

This significantly reduces exposure.

---

# Allowlisting

Prefer:

```text
Allowed:
name
email
phone
```

rather than:

```text
Blocked:
role
admin
verified
```

Why?

Because future developers may add:

```text
accountType
premium
securityLevel
```

and forget to add them to the blocklist.

---

# Blocklisting Problem

Initial object:

```text
name
email
role
```

Blocklist:

```text
role
```

Later developer adds:

```text
isAdmin
```

If the blocklist is not updated:

```text
isAdmin
```

may become client-controllable.

Allowlisting avoids this class of regression.

---

# Business Impact

Mass assignment can potentially lead to:

```text
Privilege escalation
Account takeover
Verification bypass
Workflow bypass
Unauthorised ownership changes
Subscription bypass
Financial manipulation
Security-control modification
Cross-tenant access
Data integrity compromise
```

The actual impact depends entirely on which property can be modified.

---

# False Positives

An API accepting:

```json
{
    "unknown": "test"
}
```

does not automatically mean mass assignment.

It may simply ignore unknown properties.

Verify persistence.

---

# False Positive: Reflection

The application may return:

```json
{
    "unknown": "test"
}
```

in the immediate response but never persist it.

This could be simple response echoing.

Retrieve the object independently.

---

# False Positive: Intended Property

If users are intentionally allowed to modify:

```text
nickname
timezone
language
```

then accepting these fields is not a vulnerability.

Mass assignment requires:

```text
Unintended property control
```

with meaningful security consequences.

---

# False Positive: Admin Functionality

An administrator being able to submit:

```json
{
    "role": "manager"
}
```

may be expected.

The security question is:

```text
Can an unauthorised role control the field?
```

---

# False Positive: UI Difference

The fact that:

```text
UI does not expose a field
```

does not automatically mean:

```text
API must reject it.
```

Some APIs intentionally expose functionality not present in a particular frontend.

Confirm intended access policy.

---

# Evidence Collection

Strong evidence should include:

```text
Controlled account
Affected endpoint
HTTP method
Baseline request
Modified request
Unexpected property
Baseline state
Modified state
Independent verification
Security impact
Relevant role
Screenshot where useful
```

---

# Strong Evidence Pattern

```text
1. Controlled User A is created.

2. User A has role "user".

3. Normal profile update request contains:
   displayName only.

4. The request is replayed with an additional
   security-sensitive property.

5. Server accepts the property.

6. A separate GET request confirms that
   the property changed.

7. Application behaviour confirms the
   security consequence.

8. No administrative permission was granted
   to User A.
```

---

# Example Finding: Privilege Property

```text
Finding:
Mass Assignment Allows Modification of Security-Sensitive User Properties

Observed:
The profile update endpoint accepts arbitrary properties from the JSON request body and binds them to the authenticated user's server-side object.

The normal application request contains only user-editable profile properties.

During testing with a controlled account, an additional security-sensitive property was accepted by the endpoint and the resulting state change was independently verified.

Impact:
An authenticated attacker may modify properties that should be controlled exclusively by the server.

Depending on the affected property, this could result in privilege escalation or bypass of application security controls.

Recommendation:
Do not bind the complete request body directly to the user domain object. Define a dedicated update DTO containing only explicitly permitted user-editable properties and map those properties to the domain object server-side.
```

---

# Example Finding: Verification Bypass

```text
Finding:
Mass Assignment Allows Modification of Account Verification State

Observed:
The account update API accepts the verification property even though this field is not exposed through the normal user interface.

A controlled account was used to demonstrate that the property could be modified directly through the API.

Impact:
An attacker may bypass the intended account verification workflow.

Recommendation:
Treat verification state as server-controlled data. Remove the property from user-controlled request models and modify it only through the trusted verification workflow.
```

---

# Example Finding: Ownership Manipulation

```text
Finding:
Mass Assignment Allows Modification of Object Ownership

Observed:
The project update endpoint accepts the ownerId property from the client.

A controlled project was used to demonstrate that the ownership field could be changed independently of the normal application workflow.

Impact:
An attacker may be able to alter object ownership and potentially interfere with access-control decisions.

Recommendation:
Derive ownership from authenticated server-side context and authorised workflows. Do not permit arbitrary owner identifiers through general object update requests.
```

---

# Example Finding: Subscription Manipulation

```text
Finding:
Mass Assignment Allows Modification of Subscription Properties

Observed:
The account API accepts subscription-related properties that are not exposed through the normal account settings interface.

The behaviour was demonstrated using a controlled test account.

Impact:
An attacker may be able to alter feature entitlements or subscription state without completing the intended business workflow.

Recommendation:
Maintain subscription state server-side and modify it only through authorised billing or administrative workflows.
```

---

# Reporting Titles

Useful titles include:

```text
Mass Assignment Allows Modification of Security-Sensitive User Properties

Mass Assignment Allows Privilege Escalation Through Role Property

Mass Assignment Allows Account Verification Bypass

Mass Assignment Allows Modification of Object Ownership

Mass Assignment Allows Subscription State Manipulation

Mass Assignment Exposes Server-Controlled Account Properties

GraphQL Mutation Exposes Security-Sensitive Input Fields

Unsafe Model Binding Allows Modification of Administrative Properties
```

Avoid vague titles such as:

```text
Extra JSON Parameters Accepted

Hidden Parameter Found

API Accepts Unknown Field
```

unless that is genuinely the entire impact.

---

# Severity

Severity depends on the property.

Examples:

```text
Unexpected nickname field
→ Informational / No finding

Preference manipulation
→ Low

Verification state
→ Medium / High

Ownership manipulation
→ Medium / High

Subscription entitlement
→ Medium / High

Role modification
→ High

Administrative privilege
→ High / Critical depending on impact

Financial state
→ High / Critical depending on impact
```

Rate:

```text
Demonstrated Security Impact
```

not simply:

```text
Mass Assignment Exists
```

---

# Remediation

The primary defence is:

```text
Explicit Property Allowlisting
```

---

# Use Dedicated Request DTOs

Avoid:

```text
HTTP Request
      ↓
Domain Object
```

Prefer:

```text
HTTP Request
      ↓
Request DTO
      ↓
Validation
      ↓
Explicit Mapping
      ↓
Domain Object
```

---

# Separate Read and Write Models

A useful architecture is:

```text
UserResponse
```

containing:

```text
id
name
email
role
verified
createdAt
```

while:

```text
UpdateProfileRequest
```

contains only:

```text
name
email
```

The API can therefore return fields without automatically making them writable.

---

# Explicitly Allow Fields

Example:

```text
Allowed:

name
email
phone
timezone
```

Everything else:

```text
Rejected or Ignored
```

according to application design.

---

# Prefer Rejection for Sensitive APIs

For security-sensitive APIs, rejecting unexpected fields can make implementation mistakes easier to identify.

For example:

```text
Unknown property: role
```

may be preferable to silently accepting arbitrary request structure.

---

# Server-Controlled Fields

Fields such as:

```text
role
verified
ownerId
createdAt
updatedAt
balance
paymentStatus
```

should normally be controlled by trusted server-side logic.

---

# Derive Ownership from Authentication

Instead of accepting:

```json
{
    "ownerId": 101
}
```

derive:

```text
ownerId
```

from:

```text
Authenticated User
```

where appropriate.

---

# Authorise Relationship Changes

Where ownership or relationship changes are legitimate:

```text
Transfer Project
Change Team
Move Resource
```

implement dedicated endpoints with explicit authorisation.

For example:

```text
POST /projects/100/transfer
```

may be safer than allowing:

```text
ownerId
```

through a generic PATCH endpoint.

---

# Validate Nested Objects

Allowlisting must apply recursively.

Do not allow:

```text
profile
```

as a whole if:

```text
profile
```

contains sensitive nested fields.

---

# Protect Arrays

Collections such as:

```text
roles
permissions
groups
```

must also be explicitly authorised.

---

# Framework Controls

Use the framework's supported mass assignment protections.

Examples include:

```text
Strong Parameters
DTOs
View Models
Serializer field restrictions
Fillable property controls
Binding restrictions
Read-only fields
```

---

# Do Not Depend on UI Restrictions

The browser is attacker-controlled.

Security must not depend on:

```text
Field not displayed
Hidden field
Disabled input
JavaScript restriction
Frontend validation
```

---

# Logging

Consider logging attempts to modify:

```text
role
permissions
verified
ownerId
accountStatus
```

where such properties should never appear in ordinary user requests.

This can provide useful detection telemetry.

---

# Regression Tests

Add security tests such as:

```text
Normal user cannot modify role

Normal user cannot modify verification state

Normal user cannot modify ownerId

Normal user cannot modify account status

Normal user cannot modify subscription state
```

These tests should run after:

```text
Model changes
Serializer changes
Framework upgrades
API changes
```

---

# Mass Assignment Checklist

## Discovery

```text
[ ] POST endpoints identified
[ ] PUT endpoints identified
[ ] PATCH endpoints identified
[ ] Registration tested
[ ] Profile updates tested
[ ] Account updates tested
[ ] Object creation tested
[ ] Administrative equivalents compared
```

## Property Sources

```text
[ ] API responses reviewed
[ ] JavaScript reviewed
[ ] Source maps reviewed
[ ] OpenAPI reviewed
[ ] Swagger reviewed
[ ] GraphQL schema reviewed
[ ] Error messages reviewed
[ ] Admin requests reviewed
[ ] Other-role requests reviewed
```

## Sensitive Properties

```text
[ ] Roles
[ ] Permissions
[ ] Admin flags
[ ] Verification flags
[ ] Account state
[ ] Ownership
[ ] User IDs
[ ] Account IDs
[ ] Organisation IDs
[ ] Tenant IDs
[ ] Subscription
[ ] Quotas
[ ] Financial state
[ ] Security controls
```

## Structures

```text
[ ] Top-level properties
[ ] Nested properties
[ ] Arrays
[ ] Nested arrays
[ ] Relationship objects
[ ] Null values where relevant
[ ] Boolean properties
```

## Interfaces

```text
[ ] JSON
[ ] Form encoded
[ ] Multipart
[ ] REST
[ ] GraphQL
[ ] API versions
[ ] Mobile APIs where in scope
```

## Methods

```text
[ ] POST
[ ] PUT
[ ] PATCH
[ ] JSON Patch where supported
[ ] Merge Patch where supported
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Comparer
[ ] Intruder
[ ] Param Miner
[ ] OWASP API Security Top 10 Scanner
[ ] PyBurp where useful
[ ] Logger
```

## Verification

```text
[ ] Baseline established
[ ] One property changed at a time
[ ] Controlled account used
[ ] Low-impact property tested first
[ ] Persistence independently verified
[ ] Security impact confirmed
[ ] Real financial data avoided
[ ] Real user data avoided
```

---

# Quick Reference

```text
NORMAL REQUEST

{
    "name": "Alice"
}

        ↓

DISCOVER INTERNAL PROPERTY

role

        ↓

CONTROLLED TEST

{
    "name": "Alice",
    "role": "<controlled-value>"
}

        ↓

SERVER RESPONSE

        ↓

RETRIEVE OBJECT

        ↓

PROPERTY CHANGED?
    ↓          ↓
   NO         YES
    ↓          ↓
SAFE /      SHOULD USER
REJECTED    CONTROL IT?
                ↓
           NO       YES
            ↓         ↓
      MASS ASSIGNMENT  EXPECTED
```

---

# Recommended Burp Workflow

```text
Browse Application
        ↓
Burp Proxy
        ↓
Find POST / PUT / PATCH
        ↓
Send to Repeater
        ↓
Establish Baseline
        ↓
Inspect API Responses
        ↓
Inspect JavaScript
        ↓
Inspect GraphQL / OpenAPI
        ↓
Compare Other Roles
        ↓
Build Candidate Property List
        ↓
Add One Harmless Property
        ↓
Send Request
        ↓
Retrieve Object
        ↓
Property Persisted?
        ↓
Determine Whether Property
Should Be Client-Controlled
        ↓
Test Security-Sensitive Candidate
Only Where Authorised
        ↓
Verify Impact
        ↓
Run Param Miner / API Scanner
for Additional Coverage
        ↓
Manually Verify Results
        ↓
Collect Minimal Evidence
        ↓
Report
```

---

# References

## OWASP Mass Assignment Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html

OWASP guidance covering mass assignment, auto-binding, object injection, common framework behaviour, and defensive controls.

---

## OWASP API Security

https://owasp.org/API-Security/

OWASP API security guidance covering common API security weaknesses and authorisation problems.

---

## OWASP Input Validation Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html

Guidance for validating untrusted application input.

---

## OWASP Authorization Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

Guidance for secure authorisation design.

---

## PortSwigger Param Miner

https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943

Burp extension for discovering hidden parameters, headers, and cookies through differential response analysis.

---

## PortSwigger Hidden Input Discovery

https://portswigger.net/burp/documentation/desktop/testing-workflow/analyzing/hidden-inputs

Burp documentation describing hidden-input discovery using Param Miner.

---

## OWASP API Security Top 10 Scanner

https://portswigger.net/bappstore/4894a4ba29ec4303990196a6bbc5d67b

Burp extension providing API-focused active and passive checks, including mass assignment testing.

---

## PyBurp

https://portswigger.net/bappstore/d8969aceb89d4dc38e996f3c3579880d

Burp extension that enables Python-based request and response manipulation, nested JSON processing, parameter fuzzing, and custom testing workflows.

---

## PortSwigger BApp Store

https://portswigger.net/bappstore

Official Burp Suite extension repository.

---

# Final Mass Assignment Testing Model

```text
                       APPLICATION
                            ↓
                   IDENTIFY ENDPOINTS
                            ↓
                  POST / PUT / PATCH
                            ↓
                    CAPTURE REQUEST
                            ↓
                    BURP REPEATER
                            ↓
                  ESTABLISH BASELINE
                            ↓
                 DISCOVER OBJECT MODEL
                            ↓
       ┌────────────────────┼────────────────────┐
       ↓                    ↓                    ↓
 API RESPONSES          JAVASCRIPT          API SCHEMA
       ↓                    ↓                    ↓
 READ-ONLY FIELDS       MODEL NAMES        GRAPHQL /
                                            OPENAPI
       └────────────────────┼────────────────────┘
                            ↓
                  CANDIDATE PROPERTIES
                            ↓
                     PRIORITISE SAFELY
                            ↓
                 ADD ONE PROPERTY ONLY
                            ↓
                     SEND REQUEST
                            ↓
                  PROPERTY RECOGNISED?
                     ↓             ↓
                    NO            YES
                     ↓             ↓
                 CONTINUE      RETRIEVE OBJECT
                                    ↓
                              VALUE PERSISTED?
                               ↓          ↓
                              NO         YES
                               ↓          ↓
                           CONTINUE    SHOULD CLIENT
                                      CONTROL FIELD?
                                       ↓         ↓
                                      YES        NO
                                       ↓          ↓
                                   EXPECTED    SECURITY
                                              BOUNDARY
                                              BROKEN
                                                 ↓
                                    SECURITY-SENSITIVE?
                                       ↓         ↓
                                      NO        YES
                                       ↓         ↓
                                  LOW / NONE   VERIFY WITH
                                              MINIMAL IMPACT
                                                 ↓
                                    ┌────────────┼────────────┐
                                    ↓            ↓            ↓
                                  ROLE       OWNERSHIP    VERIFICATION
                                    ↓            ↓            ↓
                               PRIVILEGE      IDOR /       WORKFLOW
                               ESCALATION      BOLA         BYPASS
                                    └────────────┼────────────┘
                                                 ↓
                                         COLLECT EVIDENCE
                                                 ↓
                                              REPORT
```

The central principle is:

> A client should only be able to modify properties that the application explicitly intends that client to control. Do not treat a field as safe simply because it is hidden from the user interface, difficult to discover, or undocumented. Map the server-side object model, identify the intended write boundary, and verify that unexpected properties cannot cross it.
