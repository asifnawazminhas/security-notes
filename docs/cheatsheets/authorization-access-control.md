---
title: Authorization, IDOR and BOLA Cheatsheet
description: Practical authorization and access control testing cheatsheet covering IDOR, BOLA, horizontal and vertical privilege escalation, function-level authorization, multi-tenant isolation, APIs, GraphQL, source review, Burp Suite workflows, evidence, remediation and retesting.
---

# Authorization, IDOR and BOLA Cheatsheet

Authorization determines:

```text
What is this authenticated identity allowed to do?
```

Authentication establishes identity:

```text
Who are you?
```

Authorization decides access:

```text
What can you access?

What can you modify?

What actions can you perform?
```

A simplified model is:

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
Authorization Decision
  |
  +--> Allowed
  |
  +--> Denied
```

Authorization vulnerabilities occur when an application fails to enforce the intended relationship between:

```text
Identity

Role

Resource

Action

Tenant

Ownership

Business state
```

!!! warning "Authorised Security Testing"

    Perform authorization testing only against accounts, objects and tenants included in the assessment scope. Use dedicated test accounts and test data wherever possible. Avoid accessing, modifying or deleting real user information simply to demonstrate an authorization weakness.


# Core Testing Principle

Never assume:

```text
Hidden from UI
```

means:

```text
Protected by server
```

Authorization must be enforced on every relevant server-side request.


# Authorization Model

Think about every request as:

```text
SUBJECT
   |
   v
ACTION
   |
   v
OBJECT
   |
   v
CONTEXT
   |
   v
AUTHORIZATION DECISION
```


# Subject

The subject may be:

```text
Anonymous user

Normal user

Privileged user

Administrator

API client

Service account

Tenant administrator

Support user
```


# Action

Examples:

```text
Read

Create

Update

Delete

Approve

Export

Download

Upload

Invite

Reset

Impersonate

Execute
```


# Object

Examples:

```text
User

Order

Invoice

Document

Message

Project

API key

Tenant

File

Ticket

Report
```


# Context

Authorization may depend on:

```text
Ownership

Tenant

Role

Relationship

Resource state

Time

Workflow stage

Subscription

Organisation
```


# Access Control Categories

The main areas to test are:

```text
Horizontal Authorization

Vertical Authorization

Object-Level Authorization

Function-Level Authorization

Property-Level Authorization

Tenant Isolation

Contextual Authorization
```


# Horizontal Authorization

Horizontal authorization separates users with equivalent privilege.

Example:

```text
User A -> User A's invoice

User B -> User B's invoice
```


# Vulnerable Behaviour

```text
User A
  |
  v
/invoices/1001
  |
  v
Change 1001 -> 1002
  |
  v
User B's Invoice
```


# Vertical Authorization

Vertical authorization separates privilege levels.

Example:

```text
Normal User

Administrator
```


# Vulnerable Behaviour

```text
Normal User
    |
    v
/admin/users
    |
    v
Administrative Function
```


# Object-Level Authorization

The application must verify whether the current identity is permitted to access the requested object.

This is particularly important in APIs.


# BOLA

BOLA stands for:

```text
Broken Object Level Authorization
```

Typical API request:

```http
GET /api/orders/1001 HTTP/1.1
Host: target.example
Authorization: Bearer TOKEN_A
```


# Test

Change:

```text
1001
```

to an object known to belong to another test account:

```http
GET /api/orders/1002 HTTP/1.1
Host: target.example
Authorization: Bearer TOKEN_A
```


# Expected

```text
Access denied
```

or an equivalent response that does not disclose the other user's object.


# IDOR

IDOR stands for:

```text
Insecure Direct Object Reference
```

An IDOR occurs when an application exposes a direct reference to an object and fails to perform appropriate authorization before using that reference.


# Example

```text
/profile?id=1001
```

Changing:

```text
1001
```

to:

```text
1002
```

must not expose another user's profile unless intended.


# IDOR vs BOLA

The terms overlap heavily.

A useful practical distinction is:

```text
IDOR
    |
    v
Common web application terminology

BOLA
    |
    v
API-focused object authorization terminology
```


# Important

The vulnerability is not:

```text
Predictable ID
```

The vulnerability is:

```text
Missing or ineffective authorization check
```


# UUIDs Do Not Fix Authorization

Replacing:

```text
1001
```

with:

```text
550e8400-e29b-41d4-a716-446655440000
```

does not remove the need for authorization.


# UUID Example

```http
GET /api/documents/550e8400-e29b-41d4-a716-446655440000
```


# Security Question

```text
Does the server verify that the current user
is permitted to access this document?
```


# Two-Account Methodology

One of the strongest authorization testing techniques is:

```text
Account A

Account B
```


# Setup

Create an object using Account A.

Example:

```text
Account A creates:

Invoice A
ID: 1001
```


# Create Comparable Object

Account B creates:

```text
Invoice B
ID: 1002
```


# Capture Request

As Account A:

```http
GET /api/invoices/1001 HTTP/1.1
Host: target.example
Cookie: session=SESSION_A
```


# Change Only Object Identifier

```http
GET /api/invoices/1002 HTTP/1.1
Host: target.example
Cookie: session=SESSION_A
```


# Expected

```text
403 Forbidden
```

or another secure non-disclosing response.


# Strong Evidence

If Account A receives Account B's object:

```text
Authentication:
Account A

Requested object:
Account B

Result:
Object returned
```

this provides clear horizontal authorization evidence.


# Why Two Accounts Matter

Without controlled ownership, you may not know whether:

```text
Object is public

Object belongs to current user

Object is intentionally shared

Object is global

Object belongs to another tenant
```


# Authorization Test Matrix

For each resource, consider:

| Subject | Object | Action |
|---|---|---|
| User A | User A object | Read |
| User A | User B object | Read |
| User A | User B object | Update |
| User A | User B object | Delete |
| Normal user | Admin object | Read |
| Normal user | Admin function | Execute |


# Start With Read-Only Tests

Prefer testing:

```text
GET

HEAD

Read-only GraphQL queries
```

before state-changing actions.


# State-Changing Tests

For:

```text
POST

PUT

PATCH

DELETE
```

use dedicated test objects.


# Avoid

Deleting or modifying real user objects solely to prove an issue.


# Object Identifier Discovery

Identifiers may appear in:

```text
URL paths

Query parameters

POST bodies

JSON

XML

GraphQL variables

Cookies

Headers

Hidden fields

WebSocket messages
```


# URL Path

```text
/api/users/123
```


# Query Parameter

```text
/download?fileId=123
```


# JSON Body

```json
{
  "document_id": 123
}
```


# Nested JSON

```json
{
  "project": {
    "id": 123
  }
}
```


# Header

```http
X-Account-ID: 123
```


# Cookie

```http
Cookie: tenant=123
```


# Hidden Field

```html
<input type="hidden" name="account_id" value="123">
```


# GraphQL Variable

```json
{
  "id": "123"
}
```


# Identifier Types

Look for:

```text
Integer IDs

UUIDs

GUIDs

Slugs

Usernames

Email addresses

Filenames

Order numbers

Invoice numbers

Project IDs

Tenant IDs

Hashes

Encoded identifiers

Composite keys
```


# Encoded Identifiers

An identifier may be encoded.

Example:

```text
MTAwMQ==
```


# Decode

```bash
printf '%s' 'MTAwMQ==' | base64 -d
```


# Result

```text
1001
```


# Important

Encoding does not provide authorization.


# Burp Suite Workflow

```text
Account A
   |
   v
Capture Request
   |
   v
Send to Repeater
   |
   v
Record Baseline
   |
   v
Replace Object A ID
   |
   v
Object B ID
   |
   v
Replay With Session A
   |
   v
Compare Response
```


# Burp Repeater

Repeater is ideal for controlled authorization testing.

Original:

```http
GET /api/orders/1001 HTTP/1.1
Host: target.example
Cookie: session=SESSION_A
```


# Modified

```http
GET /api/orders/1002 HTTP/1.1
Host: target.example
Cookie: session=SESSION_A
```


# Change One Variable

For strong evidence, change only:

```text
Object identifier
```

while keeping:

```text
Same account

Same session

Same endpoint

Same method

Same headers
```


# Burp Comparer

Compare:

```text
Account A -> Object A

Account A -> Object B
```

Look for:

```text
Object content

Owner

Email

User ID

Tenant ID

Response length

Metadata
```


# Autorize

The Burp extension Autorize can help compare requests using different authorization contexts.

Typical workflow:

```text
High-Privilege Request
        |
        v
Replay With Low-Privilege Credentials
        |
        v
Compare Response
```


# Important

Treat automated authorization results as candidates.

Manually verify important findings.


# AuthMatrix

AuthMatrix can help model:

```text
Users

Roles

Requests

Expected permissions
```

This is useful for complex applications with many role combinations.


# Authorization Testing Strategy

Create a matrix:

```text
Endpoint

Method

Role

Object Owner

Expected Result

Actual Result
```


# Example

| Endpoint | User | Object | Expected | Actual |
|---|---|---|---|---|
| `/api/profile/101` | A | A | Allow | Allow |
| `/api/profile/102` | A | B | Deny | Allow |
| `/api/admin/users` | A | Admin | Deny | Deny |


# Horizontal Read

Example:

```http
GET /api/messages/5001 HTTP/1.1
Cookie: session=SESSION_A
```


# Test

```http
GET /api/messages/5002 HTTP/1.1
Cookie: session=SESSION_A
```


# Horizontal Update

Original:

```http
PATCH /api/profile/1001 HTTP/1.1
Content-Type: application/json
Cookie: session=SESSION_A

{
  "display_name": "Account A"
}
```


# Test Object

Using a dedicated Account B:

```http
PATCH /api/profile/1002 HTTP/1.1
Content-Type: application/json
Cookie: session=SESSION_A

{
  "display_name": "Authorization Test"
}
```


# Validate

Log in as Account B and confirm whether the controlled field changed.


# Horizontal Delete

Only test deletion against objects specifically created for the assessment.


# Workflow

```text
Account B Creates Test Object
        |
        v
Account A Attempts Delete
        |
        v
Account B Verifies Object
```


# Function-Level Authorization

Object access is only one part of authorization.

Test whether users can invoke functions they should not have.


# Examples

```text
Create user

Delete user

Approve payment

Generate API key

Export data

Change role

Disable MFA

Impersonate user

View audit logs
```


# UI Restriction Is Not Authorization

Example:

```text
Normal user UI:
No "Delete User" button
```

But request:

```http
DELETE /api/users/123 HTTP/1.1
Cookie: session=NORMAL_USER
```


# Expected

```text
Denied server-side
```


# Vertical Authorization Workflow

```text
Admin Account
    |
    v
Perform Admin Action
    |
    v
Capture Request
    |
    v
Replace Admin Session
    |
    v
Normal User Session
    |
    v
Replay
```


# Keep Request Identical

Change only:

```text
Authentication context
```

when testing vertical access.


# Example

Admin request:

```http
POST /api/users/1002/disable HTTP/1.1
Cookie: session=ADMIN_SESSION
```


# Replay

```http
POST /api/users/1002/disable HTTP/1.1
Cookie: session=USER_SESSION
```


# Expected

```text
403 Forbidden
```

or equivalent.


# URL-Based Authorization

Applications sometimes protect only expected routes.

Example:

```text
/admin
```

may be protected while:

```text
/admin/

/ADMIN

/api/admin

/v1/admin

/internal/admin
```

behave differently.


# Test Only Plausible Variants

Do not blindly generate enormous path permutations.

Use:

```text
Application routes

JavaScript

API documentation

Source code

Observed redirects
```


# HTTP Method Authorization

Authorization should apply consistently across methods.

Example:

```text
GET /api/users/123
```

may be protected while:

```text
PATCH /api/users/123
```

is not.


# Review

```text
GET

POST

PUT

PATCH

DELETE
```

where each method is legitimately supported or suggested by application behaviour.


# Method Override

Some frameworks support:

```http
X-HTTP-Method-Override:
```

or request parameters that override methods.


# Test Only When Relevant

Do not assume method override support exists.


# Property-Level Authorization

An API may correctly restrict access to an object but fail to restrict individual properties.


# Example Response

```json
{
  "id": 1001,
  "name": "Alice",
  "email": "alice@example.com",
  "internal_role": "administrator",
  "mfa_secret": "..."
}
```


# Question

Should the current user receive every returned property?


# Excessive Data Exposure

Authorization review should consider:

```text
Sensitive fields

Internal fields

Administrative metadata

Secrets

Tenant information
```


# Property-Level Update

Example:

```json
{
  "display_name": "Alice",
  "role": "admin"
}
```


# Security Question

Can a normal user modify:

```text
role
```

even though they are allowed to modify:

```text
display_name
```


# Mass Assignment

Mass assignment can become an authorization issue when user-controlled properties map directly to privileged object fields.


# Example

```http
PATCH /api/users/me HTTP/1.1
Content-Type: application/json

{
  "display_name": "Alice",
  "is_admin": true
}
```


# Expected

The server should:

```text
Ignore

Reject

or independently authorize
```

security-sensitive fields.


# Allowlist Fields

Prefer:

```text
display_name

language

timezone
```

rather than automatically binding every supplied property.


# Hidden Fields

A field missing from the UI may still be accepted by the backend.

Inspect:

```text
JavaScript

API schemas

Responses

Source code
```

for additional properties.


# Tenant Isolation

Multi-tenant applications require authorization at both:

```text
User level

Tenant level
```


# Model

```text
Tenant A
  |
  +--> User A1
  +--> User A2

Tenant B
  |
  +--> User B1
  +--> User B2
```


# Cross-Tenant Test

```text
User A1
  |
  v
Tenant B Object
```


# Expected

```text
Denied
```


# Tenant Identifier Locations

Look for:

```text
tenant_id

organisation_id

organization_id

account_id

workspace_id

company_id

team_id
```


# Example

```http
GET /api/tenants/10/projects/500 HTTP/1.1
```


# Test

Change:

```text
tenant 10
```

to the ID of a dedicated test tenant:

```http
GET /api/tenants/11/projects/500 HTTP/1.1
```


# Tenant ID in Header

Example:

```http
X-Tenant-ID: 10
```


# Critical Question

Does the server trust the supplied tenant header or derive tenant membership from the authenticated identity?


# Tenant ID in JWT

A token may contain:

```json
{
  "sub": "123",
  "tenant": "10"
}
```

Even when the token is valid, the application must correctly enforce tenant authorization.


# Nested Resource Authorization

Example:

```text
/projects/10/documents/500
```


# Potential Bug

The application verifies:

```text
User can access project 10
```

but retrieves:

```text
document 500
```

without checking whether the document actually belongs to project 10.


# Parent-Child Authorization

Verify:

```text
Requested Child
      |
      v
Belongs to Requested Parent?
      |
      v
User Can Access Parent?
```


# Example Secure Query

Conceptually:

```text
SELECT document
WHERE document_id = ?
AND project_id = ?
AND project_id IN user's_allowed_projects
```


# Do Not Trust Parent IDs Alone

If the backend performs:

```text
load(document_id)
```

after separately checking only the supplied project ID, authorization may be bypassed.


# Indirect Object References

Some applications map public references to internal IDs.

Example:

```text
Public Reference
      |
      v
Server Mapping
      |
      v
Internal Object
```

This can reduce identifier exposure but does not replace authorization.


# API Authorization

APIs are especially susceptible to object-level authorization failures because identifiers frequently appear directly in requests.


# API Inventory

Review:

```text
REST

GraphQL

WebSockets

Mobile APIs

Legacy APIs

Internal APIs exposed externally
```


# REST

Typical resources:

```text
/api/users/{id}

/api/orders/{id}

/api/files/{id}

/api/projects/{id}
```


# Test Every CRUD Operation

For each object:

```text
Create

Read

Update

Delete
```


# CRUD Matrix

| Operation | Example |
|---|---|
| Create | `POST /api/projects` |
| Read | `GET /api/projects/123` |
| Update | `PATCH /api/projects/123` |
| Delete | `DELETE /api/projects/123` |


# Create Authorization

Check whether users can create resources under another:

```text
Tenant

User

Project

Account
```


# Example

```json
{
  "tenant_id": 11,
  "name": "Test Project"
}
```


# Server Should Derive Context

Where appropriate:

```text
Authenticated User
       |
       v
Tenant Membership
       |
       v
Allowed Tenant
```

rather than trusting arbitrary client-selected tenant identifiers.


# List Endpoints

Authorization bugs are not limited to direct object endpoints.

Example:

```http
GET /api/orders
```


# Review

Does the list contain:

```text
Only current user's orders
```

or:

```text
All users' orders
```


# Search Endpoints

Example:

```http
GET /api/orders/search?q=test
```


# Search Authorization

Search results must apply the same authorization filters as direct object retrieval.


# Export Endpoints

High-value candidates:

```text
/export

/download

/report

/csv

/pdf
```


# Example

```http
GET /api/reports/123/export
```


# Verify

Export authorization may differ from:

```text
GET /api/reports/123
```


# File Downloads

Example:

```http
GET /download?file_id=500
```


# Test

Use a file created by Account B and request it as Account A.


# Signed URLs

Signed URLs may intentionally permit possession-based access.

Review:

```text
Expiry

Scope

Object binding

Method binding

Leakage

Revocation requirements
```


# Do Not Report Intended Sharing

Determine whether the application intentionally provides shareable links before classifying access as unauthorized.


# GraphQL Authorization

GraphQL often exposes object identifiers through:

```text
Arguments

Variables

Nested queries

Mutations
```


# Query Example

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}
```


# Variables

```json
{
  "id": "1001"
}
```


# Test

Change to Account B's controlled object:

```json
{
  "id": "1002"
}
```


# Authorization Must Be Resolver-Side

The GraphQL schema alone does not provide authorization.


# Nested GraphQL Authorization

Example:

```graphql
query {
  project(id: "10") {
    documents {
      id
      name
    }
  }
}
```


# Review

Authorization may be correct on:

```text
project
```

but missing on:

```text
documents
```


# GraphQL Mutations

Example:

```graphql
mutation UpdateUser($id: ID!, $name: String!) {
  updateUser(id: $id, name: $name) {
    id
    name
  }
}
```


# Test

Use controlled Account B data and change:

```text
id
```


# GraphQL Aliases

Aliases can send multiple object requests in one GraphQL operation.

For authorization testing, use them cautiously and keep request volume controlled.


# WebSocket Authorization

Authentication during WebSocket connection establishment does not guarantee authorization for every message.


# Model

```text
Authenticated WebSocket
        |
        v
Message
        |
        v
Object ID
        |
        v
Authorization Check
```


# Example

```json
{
  "action": "subscribe",
  "channel_id": "123"
}
```


# Test

Can Account A subscribe to a channel belonging only to Account B?


# Subscription Authorization

Review:

```text
Chat rooms

Notifications

Projects

Tenant events

Administrative streams
```


# Background Jobs

Authorization should occur before scheduling privileged work.

Example:

```http
POST /api/reports/export HTTP/1.1

{
  "account_id": 1002
}
```


# Potential Problem

The API may accept the job and a worker later exports Account B's data without revalidating authorization.


# Second-Order Authorization

Flow:

```text
User Request
    |
    v
Queue
    |
    v
Worker
    |
    v
Object Access
```


# Review

Authorization context must survive safely across asynchronous boundaries.


# Business Workflow Authorization

Authorization may depend on workflow state.

Example:

```text
Draft
  |
  v
Submitted
  |
  v
Approved
```


# Test

Can a user directly call:

```text
/approve
```

without being an approver?


# State Transition Authorization

Review:

```text
Who can transition?

From which state?

To which state?
```


# Example

```json
{
  "status": "approved"
}
```


# Security Question

Can the client directly set privileged workflow state?


# Role Manipulation

Review requests containing:

```text
role

permissions

groups

is_admin

admin

privilege

access_level
```


# Example

```json
{
  "name": "Test User",
  "role": "admin"
}
```


# Test Safely

Use dedicated accounts and verify whether the server independently authorizes role changes.


# Invitation Authorization

Invitation workflows may permit role selection.

Review:

```text
Who can invite?

Which roles can they assign?

Which tenant receives the invite?

Can invitation parameters be changed?
```


# Example

```json
{
  "email": "test@example.com",
  "role": "administrator"
}
```


# Support and Impersonation

Administrative applications may contain:

```text
Login as user

Impersonate

View as customer
```


# High-Impact Controls

Review:

```text
Who can impersonate?

Which users can be impersonated?

Is re-authentication required?

Is the action logged?

Can impersonation cross tenants?
```


# Administrative APIs

Do not test only administrative web pages.

Look for:

```text
/api/admin

/admin/api

/internal

/management

/support
```


# JavaScript Route Discovery

Search front-end files for:

```text
/admin

/api/

role

permission

tenant

userId
```


# ripgrep

```bash
rg -ni 'admin|permission|role|tenant|account_id|user_id|owner_id|is_admin' .
```


# JavaScript Files

```bash
rg -ni '/api/|admin|role|permission|tenant' -g '*.js' -g '*.ts' -g '*.tsx' -g '*.jsx' .
```


# Source Code Review

Authorization source review should trace:

```text
Request
  |
  v
Authenticated Identity
  |
  v
Requested Object
  |
  v
Authorization Check
  |
  v
Database Query
  |
  v
Response / Action
```


# Strong Pattern

Authorization should be applied close to the object query or business operation.


# Vulnerable Concept

```python
document = Document.get(request.args["id"])
return document
```


# Better Concept

```python
document = Document.query.filter_by(
    id=request.args["id"],
    owner_id=current_user.id
).first_or_404()
```


# Important

Actual framework syntax varies.

The security principle is:

```text
Object ID
    +
Authorized Scope
```


# Query Scoping

Prefer:

```text
Current User
    |
    v
Authorized Objects
    |
    v
Requested Object
```


# Instead Of

```text
Requested Object
    |
    v
Return Object
```


# Python Search

```bash
rg -ni 'current_user|user_id|owner_id|tenant_id|permission|authorize|login_required' -g '*.py' .
```


# Django

Look for:

```text
request.user

permission_required

user_passes_test

get_object_or_404

queryset filtering
```


# Search

```bash
rg -ni 'request\.user|permission_required|user_passes_test|get_object_or_404|queryset' -g '*.py' .
```


# Django Object Query

Review whether objects are scoped to:

```text
request.user

organization

tenant
```


# Flask

Search:

```bash
rg -ni 'current_user|login_required|roles_required|permission|owner_id|user_id' -g '*.py' .
```


# FastAPI

Search:

```bash
rg -ni 'Depends|current_user|permission|role|owner_id|tenant_id' -g '*.py' .
```


# Node.js

```bash
rg -ni 'req\.user|userId|ownerId|tenantId|authorize|permission|role|isAdmin' -g '*.js' -g '*.ts' .
```


# Express Middleware

Review:

```text
Authentication middleware

Authorization middleware

Route-level controls
```


# Potential Pattern

```javascript
app.get('/api/users/:id', auth, async (req, res) => {
    const user = await User.findById(req.params.id);
    res.json(user);
});
```


# Question

Where is the authorization check?


# Java

```bash
rg -ni '@PreAuthorize|@Secured|hasRole|hasAuthority|Principal|SecurityContext|permission|ownerId|tenantId' -g '*.java' .
```


# Spring Security

Review:

```text
@PreAuthorize

@Secured

Method security

URL security

Repository query scope
```


# Important

Endpoint-level role checks may not be enough for object ownership.


# .NET

```bash
rg -ni '\[Authorize|ClaimsPrincipal|User\.Identity|IsInRole|AuthorizationService|userId|ownerId|tenantId' -g '*.cs' .
```


# ASP.NET

Review:

```text
[Authorize]

Policies

Claims

Resource-based authorization

Database query scoping
```


# PHP

```bash
rg -ni 'user_id|owner_id|tenant_id|role|permission|authorize|auth' -g '*.php' .
```


# Laravel

Review:

```text
Policies

Gates

Middleware

Route authorization

Model queries
```


# Ruby

```bash
rg -ni 'current_user|authorize|policy|role|permission|user_id|owner_id|tenant_id' -g '*.rb' .
```


# Rails

Review:

```text
before_action

Pundit policies

CanCanCan abilities

Controller object queries
```


# Go

```bash
rg -ni 'userID|ownerID|tenantID|permission|authorize|role|claims' -g '*.go' .
```


# SQL Review

Authorization failures frequently originate in database queries.


# Dangerous Concept

```sql
SELECT *
FROM documents
WHERE id = ?;
```


# Safer Concept

```sql
SELECT *
FROM documents
WHERE id = ?
AND owner_id = ?;
```


# Multi-Tenant Concept

```sql
SELECT *
FROM documents
WHERE id = ?
AND tenant_id = ?;
```


# Stronger Context

The tenant ID should come from trusted authenticated context, not merely another client-controlled parameter.


# Repository Pattern

Centralized data-access layers should provide functions such as:

```text
getDocumentForUser()

getProjectForTenant()

getOrderForCustomer()
```

rather than unrestricted generic object retrieval where possible.


# Middleware Limitations

Middleware may establish:

```text
User is authenticated
```

but cannot always determine:

```text
User owns object 123
```

Object authorization often belongs closer to business logic.


# Client-Side Authorization

Examples:

```javascript
if (user.role === "admin") {
    showDeleteButton();
}
```


# This Is UI Logic

Server must still enforce:

```text
DELETE /api/users/123
```


# Disabled Buttons

```html
<button disabled>Delete</button>
```

does not enforce authorization.


# Hidden Inputs

```html
<input type="hidden" name="role" value="user">
```

are attacker-controlled.


# HTTP Status Codes

Common secure responses include:

```text
401 Unauthorized

403 Forbidden

404 Not Found
```


# 404 for Unauthorized Objects

Applications sometimes return:

```text
404
```

for objects the user is not allowed to know exist.

This can reduce object enumeration.


# Status Alone Is Not Enough

A response can return:

```text
200
```

but still hide sensitive fields.

Or:

```text
403
```

after already performing a state-changing action.


# Validate Side Effects

For write operations, verify actual state.


# Example

Response:

```text
403 Forbidden
```

but Account B's object was modified.

This is still vulnerable.


# Response vs State

Always distinguish:

```text
HTTP Response
```

from:

```text
Backend Effect
```


# Blind Authorization Issues

Some unauthorized actions may not return sensitive data.

Example:

```text
Delete another user's notification

Trigger another user's workflow

Change another user's setting
```


# Verify Through Controlled Side Effects

Use Account B to confirm the result.


# Race Conditions

Authorization decisions may be vulnerable to state changes or timing issues.

These are separate from ordinary IDOR/BOLA testing and should be tested only when the application workflow suggests relevance.


# Caching

Authorization-sensitive responses must not leak between users through caches.


# Potential Flow

```text
User A Requests Object
        |
        v
Shared Cache
        |
        v
User B Receives Cached Response
```


# Review

```text
Cache-Control

Vary

CDN behaviour

Cache keys

Authorization headers
```


# Authorization and CORS

CORS does not provide authorization.

Even if browsers cannot read a cross-origin response:

```text
Server-side authorization must still be correct.
```


# Authorization and CSRF

CSRF and authorization are different.

```text
CSRF:
Can another site cause the victim to send an authorized request?

Authorization:
Should the victim be permitted to perform that action?
```


# Authorization and Authentication

Do not report:

```text
Unauthenticated endpoint
```

as an authorization vulnerability if the endpoint is intentionally public.


# Establish Intended Policy

Before concluding, determine:

```text
Who should have access?

What should they access?

Which actions should they perform?
```


# Sources of Intended Policy

Use:

```text
Application behaviour

Role descriptions

Requirements

Documentation

API specifications

Stakeholder confirmation

Source code

Comparable endpoints
```


# Public Resources

Some objects are intentionally public.

Example:

```text
Public profile

Published article

Shared document
```


# Do Not Assume Private

Confirm intended access.


# Shared Resources

Objects may be intentionally shared between users.

Review:

```text
Owner

Member

Viewer

Editor

Public

Guest
```


# Relationship-Based Access

Authorization may depend on relationships.

Example:

```text
Project Owner

Project Member

External Guest
```


# Build Role Matrix

| Role | Read | Create | Update | Delete | Admin |
|---|---:|---:|---:|---:|---:|
| Viewer | Yes | No | No | No | No |
| Editor | Yes | Yes | Yes | No | No |
| Owner | Yes | Yes | Yes | Yes | Limited |
| Admin | Yes | Yes | Yes | Yes | Yes |


# Compare Expected vs Actual

This provides much stronger reporting than testing random endpoints.


# Enumeration Through Authorization

Even when unauthorized access is denied, different responses may reveal object existence.

Example:

```text
Existing unauthorized object:
403

Non-existing object:
404
```


# Impact

This may permit:

```text
Object enumeration
```

but does not automatically provide object access.


# Treat Separately

Do not label existence disclosure as full IDOR unless data/action access is actually demonstrated.


# Sequential IDs

Sequential IDs make enumeration easier.

Example:

```text
1001

1002

1003
```

But sequential IDs are not themselves an authorization vulnerability.


# UUIDs

UUIDs may make guessing harder.

They should be considered:

```text
Defence in depth
```

not:

```text
Authorization
```


# API Documentation

Review:

```text
OpenAPI

Swagger

GraphQL schema

Postman collections
```


# OpenAPI

Look for object parameters:

```yaml
/api/users/{userId}
/api/orders/{orderId}
/api/tenants/{tenantId}
```


# Extract Endpoints

If an OpenAPI document is available:

```bash
jq -r '.paths | keys[]' openapi.json
```


# Search ID Parameters

```bash
jq '.. | objects | select(has("name")) | .name' openapi.json | grep -Ei 'id|user|account|tenant|owner|project'
```


# JavaScript Discovery

Search downloaded source:

```bash
rg -ni 'userId|accountId|tenantId|ownerId|projectId|documentId|orderId' .
```


# Content Discovery

Authorization-sensitive routes often include:

```text
/admin

/manage

/internal

/account

/users

/roles

/permissions

/export

/audit

/reports
```


# Authorization Automation

Automation can help identify candidates but cannot fully understand business authorization policy.


# Good Automation Use

```text
Replay known requests

Swap sessions

Swap controlled object IDs

Compare responses
```


# Poor Automation Use

```text
Enumerate every possible object identifier
without knowing ownership or expected policy
```


# Rate and Scope

Object enumeration can generate substantial traffic.

Use:

```text
Known test objects

Small controlled sets

Agreed request rates
```


# Avoid Harvesting Real Data

Once unauthorized access is established:

```text
One or two controlled objects
```

are generally enough to prove the issue.


# Evidence Chain - Horizontal IDOR

Strong evidence:

```text
1. Account A owns object A.

2. Account B owns object B.

3. Account A requests object A successfully.

4. Only the object identifier is changed.

5. Account A requests object B.

6. Object B data is returned.

7. Ownership is confirmed using Account B.
```


# Evidence Chain - Vertical Authorization

```text
1. Admin performs privileged action.

2. Request is captured.

3. Authentication context is replaced with normal-user credentials.

4. Request is replayed.

5. Privileged action succeeds.

6. Side effect is verified.
```


# Evidence Chain - Property Authorization

```text
1. Normal user can edit profile.

2. Legitimate request contains allowed fields.

3. Privileged field is added.

4. Server accepts the field.

5. Resulting privilege/state change is confirmed.
```


# Evidence Chain - Tenant Isolation

```text
1. Tenant A and Tenant B are controlled test tenants.

2. Object B belongs to Tenant B.

3. User A belongs only to Tenant A.

4. User A requests Object B.

5. Tenant B data is returned or modified.

6. Cross-tenant ownership is confirmed.
```


# Evidence to Capture

For every authorization finding record:

```text
Finding ID

Endpoint

HTTP method

Account

Role

Tenant

Object ID

Object owner

Expected access

Actual access

Baseline request

Modified request

Response

Side effect

Timestamp
```


# Redact Sensitive Data

Avoid including unnecessary:

```text
Personal information

Session tokens

Bearer tokens

Real customer records
```


# Screenshot Strategy

Useful screenshots show:

```text
Account A identity

Object B ownership

Modified request

Unauthorized response/data
```


# Burp Evidence

Save:

```text
Original request

Modified request

Original response

Modified response
```


# Reporting IDOR

> The application does not enforce object-level authorization when retrieving user documents. A user authenticated as Account A can modify the document identifier in the request and retrieve a document belonging to Account B. Testing was performed using two dedicated assessment accounts, confirming that the returned object was owned by a different user.


# Reporting BOLA

> The API accepts an object identifier from the request and retrieves the corresponding resource without verifying that the authenticated user is authorized to access that object. Changing the identifier from an object owned by Account A to an object owned by Account B returned Account B's data.


# Reporting Vertical Privilege Escalation

> A function intended for administrative users is accessible to a normal authenticated user. An administrative request was captured and replayed using a normal-user session without otherwise modifying the request. The server performed the privileged action despite the lower-privileged authentication context.


# Reporting Cross-Tenant Access

> Tenant isolation is not enforced when retrieving project resources. A user belonging exclusively to Tenant A was able to request a project owned by Tenant B by modifying the tenant and project identifiers. The application returned Tenant B data without verifying tenant membership.


# Reporting Mass Assignment Authorization

> The profile update endpoint accepts security-sensitive properties that are not exposed through the normal user interface. Adding the privileged `role` property to a legitimate profile update request caused the server to persist the supplied value. The endpoint should explicitly allow only user-editable properties and independently authorize security-sensitive changes.


# Reporting Object Existence Disclosure

> The endpoint returns distinguishable responses for existing but unauthorized objects and non-existent objects. This allows authenticated users to determine whether specific object identifiers exist. Testing did not demonstrate unauthorized access to the object contents.


# Reporting Function-Level Authorization

> The application hides the user-management function from normal users in the interface, but the underlying endpoint does not enforce the same role restriction. A normal-user session successfully invoked the administrative endpoint directly.


# Avoid Overclaiming

Do not write:

```text
Full account takeover is possible.
```

if the demonstrated behaviour is only:

```text
Another user's display name can be read.
```


# State Demonstrated Impact

Example:

```text
Account A can retrieve Account B's invoice metadata.
```

Then separately discuss credible consequences.


# Severity Considerations

Consider:

```text
Data sensitivity

Read vs write

Delete capability

Privilege level

Cross-tenant access

Number of affected objects

Discoverability of identifiers

Authentication required

Business impact

Regulatory impact

Ability to automate

Administrative functionality

Persistence
```


# Read vs Write

Generally:

```text
Unauthorized Read
```

and:

```text
Unauthorized Write
```

have different impact.


# High-Impact Examples

Potentially severe authorization failures include:

```text
Cross-tenant data access

Administrative action execution

Role modification

Payment modification

Account takeover workflows

API key access

Sensitive document access

User impersonation
```


# Root Cause

Common root causes include:

```text
Missing authorization check

Authorization only in UI

Authentication mistaken for authorization

Object query not scoped to user

Object query not scoped to tenant

Role check missing

Property allowlist missing

Authorization implemented inconsistently

Client-controlled tenant context trusted
```


# Remediation - Deny by Default

Use:

```text
No explicit permission
        |
        v
       DENY
```


# Centralize Policy

Where practical, define authorization policy centrally.

Examples:

```text
Role policies

Resource policies

Framework authorization middleware

Service-level authorization functions
```


# But Enforce Near Resources

Central policy should still be applied at the point where:

```text
Object is loaded

Action is performed
```


# Object Query Scoping

Prefer:

```text
get object where:
    object_id = requested_id
    AND owner_id = current_user
```

rather than:

```text
get object by requested_id
```


# Tenant Query Scoping

Prefer:

```text
object_id
AND
trusted_current_tenant
```


# Trusted Tenant Context

Derive tenant membership from:

```text
Authenticated identity

Server-side session

Validated token claims + server-side policy
```

rather than blindly trusting:

```text
X-Tenant-ID

tenant_id parameter

hidden field
```


# Property Allowlisting

Explicitly define writable fields.

Example:

```text
Allowed:
display_name
timezone
language

Not user-writable:
role
tenant_id
is_admin
account_status
```


# Function Authorization

Every privileged endpoint should independently verify:

```text
Authenticated?

Correct role?

Correct permission?

Correct object relationship?
```


# Avoid Role Checks Only in Front-End

Security controls belong server-side.


# Indirect IDs

Random identifiers can reduce enumeration but should only be defence in depth.


# Logging

Log important authorization failures.

Useful fields include:

```text
User ID

Tenant

Requested object

Action

Endpoint

Timestamp

Decision
```


# Avoid Sensitive Logs

Do not log unnecessary:

```text
Session tokens

Bearer tokens

Full confidential object contents
```


# Detection

Potential signals include:

```text
Many sequential object requests

Repeated 403/404 responses

Cross-tenant identifier attempts

Normal users calling admin endpoints

Repeated access to unrelated objects
```


# Retesting IDOR

Use the original two accounts.


# Workflow

```text
Account A -> Object A
        |
        v
        Allow

Account A -> Object B
        |
        v
        Deny
```


# Verify Response

Ensure unauthorized requests do not expose:

```text
Object content

Sensitive metadata

Side effects
```


# Retest Write Operations

Verify Account B's test object remains unchanged after Account A attempts the original unauthorized modification.


# Retest Delete

Verify the controlled object still exists.


# Retest Vertical Authorization

Replay the original privileged request using the normal-user session.

Expected:

```text
Denied
```


# Retest Tenant Isolation

Verify cross-tenant requests fail regardless of:

```text
Object ID

Tenant ID

Endpoint variant

HTTP method
```


# Retest Property Authorization

Add the previously accepted privileged property.

Expected:

```text
Rejected or ignored
```

and verify the underlying account state remains unchanged.


# Retest Equivalent Endpoints

Do not stop at the single fixed endpoint.

Review equivalent:

```text
API versions

Mobile endpoints

Export endpoints

GraphQL resolvers

WebSocket messages

Background jobs
```


# Root Cause Review

After one authorization issue, search the entire application for the same pattern.


# Generic Search

```bash
rg -ni 'user_id|userId|owner_id|ownerId|tenant_id|tenantId|account_id|accountId|role|permission|authorize|isAdmin|is_admin' .
```


# Route Search

```bash
rg -ni 'GET|POST|PUT|PATCH|DELETE|router|route|controller|endpoint' src/
```


# Object Lookup Search

```bash
rg -ni 'findById|getById|findOne|get_object_or_404|FirstOrDefault|FindAsync|where.*id' .
```


# Authorization Search

```bash
rg -ni 'authorize|permission|policy|role|ownership|owner|tenant|access.*control' .
```


# Review Every Direct Object Lookup

For each:

```text
getById(id)
```

ask:

```text
Where is ownership checked?

Where is tenant membership checked?

Where is role checked?
```


# Authorization Checklist

## Preparation

- [ ] Dedicated Account A available
- [ ] Dedicated Account B available
- [ ] Privileged account available where required
- [ ] Test objects created
- [ ] Ownership recorded
- [ ] Tenant relationships understood
- [ ] Intended role model understood

## Object Discovery

- [ ] URL path IDs reviewed
- [ ] Query IDs reviewed
- [ ] JSON IDs reviewed
- [ ] XML IDs reviewed
- [ ] Headers reviewed
- [ ] Cookies reviewed
- [ ] Hidden fields reviewed
- [ ] GraphQL variables reviewed
- [ ] WebSocket messages reviewed
- [ ] Encoded IDs reviewed

## Horizontal Authorization

- [ ] Read tested
- [ ] Update tested where safe
- [ ] Delete tested on dedicated objects where safe
- [ ] Account A -> Account B objects tested
- [ ] Ownership independently confirmed

## Vertical Authorization

- [ ] Admin endpoints identified
- [ ] Admin requests captured
- [ ] Normal-user replay tested
- [ ] UI-only restrictions identified
- [ ] Administrative APIs reviewed
- [ ] Role-changing functions reviewed
- [ ] Impersonation reviewed where present

## Function-Level Authorization

- [ ] Create operations reviewed
- [ ] Approve operations reviewed
- [ ] Export operations reviewed
- [ ] Delete operations reviewed
- [ ] Invitation functions reviewed
- [ ] API key management reviewed
- [ ] Account management reviewed

## Property Authorization

- [ ] Writable fields identified
- [ ] Hidden fields reviewed
- [ ] Role properties reviewed
- [ ] Tenant properties reviewed
- [ ] Ownership properties reviewed
- [ ] Status fields reviewed
- [ ] Mass assignment considered
- [ ] Sensitive response fields reviewed

## Multi-Tenant

- [ ] Tenant IDs identified
- [ ] Cross-tenant read tested
- [ ] Cross-tenant write tested where safe
- [ ] Cross-tenant delete tested only on dedicated data
- [ ] Tenant headers reviewed
- [ ] Tenant claims reviewed
- [ ] Nested resources reviewed
- [ ] Exports reviewed
- [ ] Background jobs reviewed

## APIs

- [ ] REST reviewed
- [ ] List endpoints reviewed
- [ ] Search endpoints reviewed
- [ ] CRUD operations reviewed
- [ ] API versions reviewed
- [ ] Mobile APIs reviewed
- [ ] Legacy APIs reviewed
- [ ] OpenAPI/Swagger reviewed

## GraphQL

- [ ] Object queries reviewed
- [ ] Nested resolvers reviewed
- [ ] Mutations reviewed
- [ ] Variables reviewed
- [ ] Property exposure reviewed
- [ ] Role-sensitive fields reviewed

## WebSockets

- [ ] Connection authentication reviewed
- [ ] Message authorization reviewed
- [ ] Subscription authorization reviewed
- [ ] Object IDs reviewed
- [ ] Tenant boundaries reviewed

## Source Review

- [ ] Object lookups identified
- [ ] Ownership checks identified
- [ ] Tenant checks identified
- [ ] Role checks identified
- [ ] Authorization middleware reviewed
- [ ] Database query scoping reviewed
- [ ] Client-controlled security fields reviewed
- [ ] Equivalent sinks reviewed

## Evidence

- [ ] Account A recorded
- [ ] Account B recorded
- [ ] Roles recorded
- [ ] Tenants recorded
- [ ] Object ownership recorded
- [ ] Baseline request saved
- [ ] Modified request saved
- [ ] Response saved
- [ ] Side effect verified
- [ ] Sensitive data redacted
- [ ] Timestamp recorded

## Retest

- [ ] Original object access denied
- [ ] Original write denied
- [ ] Original delete denied
- [ ] Privileged function denied
- [ ] Cross-tenant access denied
- [ ] Privileged properties rejected
- [ ] Equivalent endpoints reviewed
- [ ] Legitimate access still works


# Authorization Matrix

| Test | Subject | Object | Expected |
|---|---|---|---|
| Own object | User A | A | Allow |
| Other user's object | User A | B | Deny |
| Admin object | Normal user | Admin | Deny |
| Own tenant | Tenant A user | Tenant A | Allow |
| Other tenant | Tenant A user | Tenant B | Deny |


# CRUD Authorization Matrix

| Operation | Own Object | Other User | Other Tenant |
|---|---|---|---|
| Create | Policy dependent | Policy dependent | Deny |
| Read | Allow | Deny | Deny |
| Update | Allow if permitted | Deny | Deny |
| Delete | Allow if permitted | Deny | Deny |


# Object Identifier Matrix

| Location | Example |
|---|---|
| URL path | `/users/123` |
| Query | `?user_id=123` |
| JSON | `"user_id": 123` |
| Header | `X-User-ID: 123` |
| Cookie | `tenant=123` |
| GraphQL | `"id": "123"` |
| WebSocket | `"channel_id": "123"` |


# Access Control Matrix

| Type | Question |
|---|---|
| Horizontal | Can User A access User B? |
| Vertical | Can normal user perform admin actions? |
| Object-level | Can subject access this object? |
| Function-level | Can subject invoke this function? |
| Property-level | Can subject read/write this field? |
| Tenant-level | Can Tenant A access Tenant B? |


# Evidence Matrix

| Observation | Supports |
|---|---|
| A reads B object | Horizontal authorization failure |
| User executes admin action | Vertical authorization failure |
| Tenant A reads Tenant B | Tenant isolation failure |
| User sets `role=admin` | Property-level authorization failure |
| Unauthorized object returns different existence signal | Object enumeration |
| Sequential IDs only | Not authorization failure by itself |


# False Positive Matrix

| Observation | Alternative Explanation |
|---|---|
| Object accessible | Object may intentionally be public |
| Object shared between users | Sharing may be intended |
| Predictable ID | Does not prove missing authorization |
| UUID used | Does not prove secure authorization |
| 403 response | Action may already have occurred |
| 404 response | Could intentionally conceal existence |
| Hidden admin button | Server may still enforce authorization |


# Remediation Matrix

| Weakness | Primary Control |
|---|---|
| IDOR/BOLA | Object-level authorization |
| Vertical escalation | Function-level authorization |
| Cross-tenant access | Tenant-scoped authorization |
| Mass assignment | Writable-property allowlist |
| Client-controlled role | Server-side role derivation |
| Unscoped object lookup | User/tenant-scoped query |
| UI-only restriction | Server-side enforcement |
| Inconsistent policy | Central authorization policy |


# Two-Account Testing Model

```text
                ACCOUNT A
                    |
                    v
              CREATE OBJECT A
                    |
                    v
              CAPTURE REQUEST
                    |
                    v
            REPLACE OBJECT ID
                    |
                    v
                OBJECT B
                    |
                    v
           KEEP SESSION A
                    |
                    v
                 REPLAY
                    |
          +---------+---------+
          |                   |
          v                   v
        DENIED              ALLOWED
          |                   |
          v                   v
        SECURE          VERIFY OWNERSHIP
                              |
                              v
                         AUTHZ FINDING
```


# Vertical Testing Model

```text
                 ADMIN USER
                     |
                     v
              PRIVILEGED ACTION
                     |
                     v
               CAPTURE REQUEST
                     |
                     v
             REPLACE AUTH CONTEXT
                     |
                     v
                NORMAL USER
                     |
                     v
                   REPLAY
                     |
          +----------+----------+
          |                     |
          v                     v
        DENIED                ALLOWED
          |                     |
          v                     v
        SECURE             VERIFY EFFECT
                                |
                                v
                         AUTHZ FINDING
```


# Tenant Testing Model

```text
                 TENANT A USER
                       |
                       v
                 TENANT A OBJECT
                       |
                       v
                  BASELINE
                       |
                       v
              TENANT B TEST OBJECT
                       |
                       v
                   REQUEST
                       |
              +--------+--------+
              |                 |
              v                 v
            DENIED            ALLOWED
              |                 |
              v                 v
            SECURE       CROSS-TENANT ISSUE
```


# Source Review Model

```text
                  REQUEST
                     |
                     v
              AUTHENTICATION
                     |
                     v
              CURRENT IDENTITY
                     |
                     v
               REQUESTED ID
                     |
                     v
             AUTHORIZED SCOPE
                     |
                     v
                OBJECT QUERY
                     |
                     v
             BUSINESS ACTION
                     |
                     v
                  RESPONSE
```


# Secure Object Access Model

```text
               AUTHENTICATED USER
                       |
                       v
                AUTHORIZED SCOPE
                       |
                       v
                 OBJECT ID
                       |
                       v
               SCOPED DATABASE QUERY
                       |
             +---------+---------+
             |                   |
             v                   v
           FOUND              NOT FOUND
             |                   |
             v                   v
           ALLOW                DENY
```


# Practical Validation Model

```text
Understand Roles
      |
      v
Create Controlled Accounts
      |
      v
Create Controlled Objects
      |
      v
Capture Baseline
      |
      v
Change One Authorization Dimension
      |
      v
Replay
      |
      v
Verify Response and Side Effect
      |
      v
Confirm Ownership / Role / Tenant
      |
      v
Determine Actual Impact
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

Authorization testing is not:

```text
Change ID
   |
   v
Got 200
   |
   v
Report IDOR
```

It is:

```text
KNOWN SUBJECT
     |
     v
KNOWN PERMISSION
     |
     v
KNOWN OBJECT OWNER
     |
     v
CONTROLLED CHANGE
     |
     v
SERVER AUTHORIZATION DECISION
     |
     v
VERIFIED RESULT
```

For every authorization-sensitive request ask:

```text
Who is making the request?

What role do they have?

Which tenant do they belong to?

What object are they requesting?

Who owns that object?

Is the object intentionally shared?

What action is being performed?

Should this role perform that action?

Where does the object identifier originate?

Can the identifier be modified?

Does the server scope the query to the current user?

Does the server scope the query to the current tenant?

Are nested objects independently authorized?

Are write operations protected as strongly as reads?

Are delete operations protected?

Are export/download endpoints protected?

Are search/list endpoints filtered?

Can hidden properties be modified?

Can role or tenant properties be supplied by the client?

Are administrative endpoints protected server-side?

Does GraphQL enforce authorization in resolvers?

Do WebSocket messages enforce object authorization?

Do background workers preserve authorization context?

Does a 403 actually prevent the side effect?

Are predictable identifiers being confused with the actual vulnerability?

Have two controlled accounts been used?

Have controlled objects been used?

Has ownership been verified?

Has the exact demonstrated impact been documented?

Have equivalent endpoints been reviewed?

Has the fix been retested using the original authorization boundary?
```

The strongest evidence is:

```text
CONTROLLED ACCOUNT A
        |
        v
KNOWN OBJECT B
        |
        v
OBJECT B BELONGS TO CONTROLLED ACCOUNT B
        |
        v
REQUEST MADE AS ACCOUNT A
        |
        v
ONLY AUTHORIZATION-RELEVANT VALUE CHANGED
        |
        v
SERVER ALLOWS UNAUTHORIZED ACCESS
        |
        v
RESULT VERIFIED
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Authentication and Session Testing Cheatsheet](authentication-session-testing.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)
- [Content Discovery Cheatsheet](content-discovery.md)
- [SQL Injection Cheatsheet](sql-injection.md)


# Related Notes

Known deeper notes that are useful alongside this cheatsheet include:

```text
docs/web/authorisation.md
docs/web/api-security.md
docs/web/graphql.md
docs/web/business-logic.md
```


# References

- [PortSwigger Web Security Academy - Access Control](https://portswigger.net/web-security/access-control){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy - API Testing](https://portswigger.net/web-security/api-testing){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Insecure Direct Object Reference Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP API Security Top 10](https://owasp.org/API-Security/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Authorization Testing](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [CWE-639 - Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html){ target="_blank" rel="noopener noreferrer" }
- [CWE-862 - Missing Authorization](https://cwe.mitre.org/data/definitions/862.html){ target="_blank" rel="noopener noreferrer" }
- [CWE-863 - Incorrect Authorization](https://cwe.mitre.org/data/definitions/863.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Use two accounts"

    Account A and Account B with known object ownership provide much stronger authorization evidence than changing random identifiers and guessing who owns the returned resource.


!!! tip "Change one dimension at a time"

    For horizontal testing, keep Account A's session and change only the object identifier. For vertical testing, keep the request identical and change only the authentication context. This makes the authorization failure much easier to demonstrate and defend.


!!! tip "Verify state, not only responses"

    A `403 Forbidden` response does not prove that a write operation was prevented. Verify the underlying object using the second controlled account whenever testing updates, deletes or workflow actions.


!!! tip "Scope database queries"

    One of the strongest authorization patterns is to retrieve objects from the authenticated user's or tenant's authorized scope rather than loading arbitrary objects first and attempting to authorize them afterwards.


!!! warning "Predictable IDs are not IDOR"

    Sequential integers, UUIDs, encoded identifiers and hidden parameters are object references. The vulnerability exists when the server fails to enforce the required authorization when those references are used.


!!! warning "Stop after proving the boundary"

    Once unauthorized access to a controlled object has been demonstrated, there is usually no need to enumerate additional users, tenants or production records. Capture the evidence and move on to root-cause and equivalent-endpoint review.
