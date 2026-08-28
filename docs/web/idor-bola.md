# IDOR and BOLA

Insecure Direct Object Reference (IDOR) and Broken Object Level Authorization (BOLA) vulnerabilities occur when an application exposes references to objects and fails to correctly verify whether the authenticated user is authorised to access or manipulate those objects.

A typical vulnerable flow is:

```text
Authenticated User
        ↓
GET /api/orders/1001
        ↓
Application Reads Object ID
        ↓
Database Lookup
        ↓
Order 1001 Returned
```

The security question is:

```text
Does the application verify that
the current user is authorised
to access Order 1001?
```

A vulnerable implementation may effectively perform:

```text
Object Exists?
     ↓
    YES
     ↓
Return Object
```

A secure implementation requires:

```text
Object Exists?
     ↓
    YES
     ↓
Does Current User Have Access?
     ↓
 YES          NO
  ↓            ↓
Return        Deny
```

!!! warning "Authorised Security Testing"
    Perform IDOR and BOLA testing only against applications included in the authorised assessment scope. Where possible, use two or more controlled test accounts and objects created specifically for the assessment. Avoid accessing, modifying, or deleting real user data.

---

# IDOR vs BOLA

The terms are closely related but come from slightly different security terminology.

## IDOR

IDOR traditionally describes an application exposing a direct reference to an internal object and failing to enforce appropriate access control.

Example:

```http
GET /account/document?id=12345 HTTP/1.1
Host: target.example
Cookie: session=USER_A
```

Changing:

```text
12345
```

to:

```text
12346
```

might return another user's document.

---

# BOLA

BOLA is commonly used in API security.

The core problem is still:

```text
Attacker Controls Object Identifier
            ↓
Application Retrieves Object
            ↓
Object-Level Authorisation Missing
```

For example:

```http
GET /api/v1/users/73/orders/992 HTTP/1.1
Authorization: Bearer USER_A_TOKEN
```

If order:

```text
992
```

belongs to User B but is returned to User A, object-level authorisation is broken.

---

# Core Security Model

The correct model should be:

```text
Request
   ↓
Authentication
   ↓
Current User Identity
   ↓
Requested Object
   ↓
Object Ownership / Permission Check
   ↓
Authorised?
   ↓
YES ───────→ Return Object
NO  ───────→ Deny Request
```

The vulnerable model is often:

```text
Request
   ↓
Authentication
   ↓
Object ID
   ↓
Database Lookup
   ↓
Return Object
```

Authentication alone does not provide authorisation.

---

# Horizontal vs Vertical Access Control

IDOR and BOLA commonly produce horizontal privilege escalation.

## Horizontal

```text
User A
  ↓
Object belonging to User B
```

Both users may have the same role.

Example:

```text
Alice → Alice's invoices
Bob   → Bob's invoices
```

A vulnerability allows:

```text
Alice → Bob's invoices
```

---

# Vertical

Vertical privilege escalation involves crossing privilege levels.

```text
Normal User
     ↓
Administrator Object / Function
```

For example:

```http
GET /api/admin/users/100 HTTP/1.1
Authorization: Bearer NORMAL_USER
```

Vertical authorisation issues are covered more broadly in:

```text
docs/web/authorisation.md
```

---

# IDOR Is Not Just Numeric IDs

A common mistake is testing only:

```text
?id=100
?id=101
?id=102
```

Object references can appear almost anywhere.

Examples:

```text
Numeric IDs
UUIDs
GUIDs
Usernames
Email addresses
File names
File paths
Order numbers
Invoice numbers
Account numbers
Transaction IDs
Project IDs
Tenant IDs
Document IDs
Message IDs
API keys
Database identifiers
Hashes
Encoded identifiers
Slug values
Composite identifiers
GraphQL IDs
WebSocket channel IDs
```

---

# UUIDs Do Not Fix IDOR

Consider:

```text
/api/documents/9dd2a913-23f7-4a52-a59d-7862f27145e8
```

The identifier may be difficult to guess.

However:

```text
Unpredictable Identifier
        ≠
Authorisation
```

If User A obtains User B's UUID through:

```text
API response
JavaScript
Shared link
Search result
WebSocket
Email
Referrer
Logs
Another endpoint
GraphQL
Information disclosure
```

the application must still enforce authorisation.

---

# Object Reference Discovery

Look for references in:

```text
URL paths
Query parameters
POST bodies
JSON
XML
GraphQL variables
HTTP headers
Cookies
WebSocket messages
Hidden form fields
JavaScript
HTML attributes
API responses
Redirect URLs
Download links
Mobile API traffic
```

---

# URL Path Objects

Example:

```http
GET /api/orders/8127 HTTP/1.1
```

Candidate object:

```text
8127
```

Test with controlled objects belonging to another assessment account.

---

# Query Parameter Objects

Example:

```http
GET /download?document=12883 HTTP/1.1
```

Candidate:

```text
document=12883
```

---

# JSON Objects

Example:

```http
POST /api/profile HTTP/1.1
Content-Type: application/json

{
    "userId": 1001
}
```

Candidate:

```text
userId
```

---

# Nested JSON Objects

Example:

```json
{
    "order": {
        "id": 5012
    },
    "customer": {
        "id": 901
    }
}
```

Both identifiers may require testing.

Do not assume only the top-level identifier matters.

---

# Hidden Form Fields

Example:

```html
<input type="hidden" name="accountId" value="8842">
```

Hidden fields are:

```text
Client-Controlled Input
```

They do not provide a security boundary.

---

# Cookies

Applications sometimes store object references in cookies.

Example:

```http
Cookie: account=1042
```

Test whether the server trusts the value to determine which object should be returned.

---

# HTTP Headers

Custom headers may contain object or identity references.

Examples:

```http
X-User-ID: 1002
X-Account-ID: 5501
X-Customer-ID: 991
X-Organisation-ID: 17
X-Project-ID: 901
```

Treat these values as attacker-controlled unless protected by a trusted intermediary that strips and regenerates them.

---

# Object References in Responses

Object IDs are frequently discovered from other API responses.

Example:

```json
{
    "users": [
        {
            "id": 781,
            "username": "testuser"
        }
    ]
}
```

The ID:

```text
781
```

may be usable against another endpoint.

This produces a common attack chain:

```text
Information Disclosure
        ↓
Object Identifier
        ↓
Different Endpoint
        ↓
Missing Authorisation
        ↓
IDOR / BOLA
```

---

# Object Reference Mapping

During testing, create an object map.

Example:

| Object | User A | User B |
|---|---:|---:|
| User ID | 101 | 102 |
| Account ID | 501 | 502 |
| Order ID | 9001 | 9002 |
| Document ID | 7001 | 7002 |
| Project ID | 3001 | 3002 |

This makes systematic testing much easier.

---

# Two-Account Testing

The strongest IDOR methodology uses at least two controlled accounts.

```text
Account A
Account B
```

Each account creates its own objects.

For example:

```text
Account A
   ↓
Creates Document A
   ↓
ID = 1001

Account B
   ↓
Creates Document B
   ↓
ID = 1002
```

Now test:

```text
Account A + Document B
```

and:

```text
Account B + Document A
```

---

# Two-Account Matrix

| Request | Object | Expected |
|---|---|---|
| User A | Object A | Allow |
| User A | Object B | Deny |
| User B | Object B | Allow |
| User B | Object A | Deny |
| Anonymous | Object A | Deny |
| Anonymous | Object B | Deny |

This simple matrix detects a large number of authorisation flaws.

---

# Three-Account Testing

Where practical, add:

```text
Administrator
User A
User B
```

Then test:

| Actor | User A Object | User B Object | Admin Object |
|---|---|---|---|
| Anonymous | Deny | Deny | Deny |
| User A | Allow | Deny | Deny |
| User B | Deny | Allow | Deny |
| Administrator | Depends | Depends | Allow |

This helps distinguish:

```text
Authentication
Horizontal Authorisation
Vertical Authorisation
```

---

# CRUD Testing

Do not stop after testing:

```text
GET
```

Test the complete object lifecycle.

```text
Create
Read
Update
Delete
```

Common HTTP methods:

```text
POST
GET
PUT
PATCH
DELETE
```

---

# Read IDOR

Example:

```http
GET /api/invoices/5002 HTTP/1.1
Authorization: Bearer USER_A
```

If invoice:

```text
5002
```

belongs to User B and is returned:

```text
Broken Object-Level Authorisation
```

---

# Update IDOR

Example:

```http
PATCH /api/users/102 HTTP/1.1
Authorization: Bearer USER_A
Content-Type: application/json

{
    "displayName": "AM-IDOR-TEST"
}
```

If User A can modify User B:

```text
Horizontal Privilege Escalation
```

Use only controlled accounts.

---

# Delete IDOR

Example:

```http
DELETE /api/documents/1002 HTTP/1.1
Authorization: Bearer USER_A
```

Deletion testing is destructive.

Prefer:

```text
Dedicated test objects
```

created specifically for the assessment.

---

# Create Operations

Create operations can also contain object-level authorisation problems.

Example:

```json
{
    "projectId": 2002,
    "message": "test"
}
```

If:

```text
projectId=2002
```

belongs to another user, determine whether User A can create objects inside User B's project.

---

# Parent and Child Objects

Modern APIs frequently use nested routes.

Example:

```text
/projects/100/documents/500
```

Test both:

```text
project=100
document=500
```

A vulnerable application may validate only one.

---

# Parent-Child Mismatch

Suppose:

```text
User A Project = 100
User B Document = 900
```

Test:

```text
/projects/100/documents/900
```

and:

```text
/projects/200/documents/500
```

The application should verify the complete relationship:

```text
User
 ↓
Project
 ↓
Document
```

---

# Relationship-Based Authorisation

Ownership is not always:

```text
object.user_id == current_user.id
```

Applications may use:

```text
Teams
Groups
Organisations
Projects
Departments
Shared folders
Delegated permissions
ACLs
Roles
```

The correct question is:

```text
Should this user have access to this object
under the application's intended policy?
```

---

# IDOR in File Downloads

High-value targets include:

```text
Invoices
PDFs
Reports
Statements
Exports
Images
Attachments
Contracts
Backups
Support documents
```

Example:

```http
GET /download/83482.pdf HTTP/1.1
```

Test with another controlled account's file identifier.

---

# Static File IDOR

Sometimes authentication protects the application page but not the underlying file.

Example:

```text
Application:

/documents/view?id=100

Actual file:

/uploads/documents/100.pdf
```

Test whether direct access to the underlying file bypasses application authorisation.

---

# Filename-Based IDOR

Example:

```text
/download?file=invoice-88213.pdf
```

The filename itself may be the object reference.

---

# Encoded Object References

Applications may encode identifiers.

Examples:

```text
MTAwMQ==
```

could simply be:

```text
1001
```

encoded with Base64.

Do not treat:

```text
Encoding
```

as:

```text
Authorisation
```

---

# Hash-Like References

Example:

```text
/download/6f1ed002ab5595859014ebf0951522d9
```

Determine whether the value is:

```text
Random
Derived
Predictable
Leaked elsewhere
```

Even if unpredictable, server-side authorisation is still required.

---

# Sequential IDs

Sequential identifiers make enumeration easier.

Example:

```text
1001
1002
1003
1004
```

But predictability affects:

```text
Exploitability
```

not the fundamental authorisation flaw.

---

# Negative IDs

When appropriate and safe, test unusual object values:

```text
0
-1
```

Some applications use special records or fallback logic.

Do not blindly fuzz destructive endpoints.

---

# Duplicate Parameters

Example:

```text
?id=1001&id=1002
```

Different components may interpret duplicate parameters differently.

This can occasionally affect authorisation.

Refer to parameter parsing behaviour in:

```text
docs/web/api-security.md
```

---

# Alternative Parameter Locations

If the application accepts:

```text
?id=1001
```

also determine whether it accepts the object identifier through:

```text
Path
JSON
Form body
Header
Cookie
```

Different code paths may enforce different controls.

---

# Method-Based Authorisation

An endpoint may protect:

```text
GET
```

but not:

```text
PUT
PATCH
DELETE
```

Example:

```text
GET /api/users/102
→ 403
```

but:

```text
PATCH /api/users/102
→ 200
```

Test each supported method.

---

# Method Override

Some frameworks support:

```text
X-HTTP-Method-Override
_method
```

For example:

```http
POST /api/users/102 HTTP/1.1
X-HTTP-Method-Override: DELETE
```

Only test this where relevant to the application's technology stack.

---

# Content-Type Differences

Authorisation may be implemented differently across handlers.

Test supported formats such as:

```text
application/json
application/x-www-form-urlencoded
multipart/form-data
```

when the endpoint legitimately accepts them.

---

# API Version Differences

Applications may expose:

```text
/api/v1/
/api/v2/
/api/internal/
```

Older API versions sometimes contain weaker authorisation controls.

Example:

```text
/api/v2/users/100
```

securely checks ownership while:

```text
/api/v1/users/100
```

does not.

---

# Mobile APIs

Mobile applications often use the same backend APIs.

Potential object references can be found through:

```text
Mobile proxy traffic
API responses
Application code
Deep links
```

Do not assume the web interface exposes the complete attack surface.

---

# REST APIs

REST-style APIs frequently expose object references directly:

```text
GET /users/100
GET /orders/500
GET /documents/800
```

For every endpoint ask:

```text
Who owns this object?
Who should access it?
Where is that enforced?
```

---

# GraphQL BOLA

GraphQL commonly exposes objects through arguments.

Example:

```graphql
query {
    order(id: "5002") {
        id
        total
        customerEmail
    }
}
```

Test using:

```text
User A session
+
User B controlled order ID
```

GraphQL resolvers must enforce object-level authorisation.

Refer to:

```text
docs/web/graphql.md
```

---

# GraphQL Nested Objects

Example:

```graphql
query {
    user(id: "102") {
        orders {
            id
            total
        }
    }
}
```

The application may protect:

```text
user()
```

but fail to protect:

```text
orders
```

or individual nested objects.

Test authorisation at every resolver boundary.

---

# GraphQL Node IDs

Some GraphQL implementations use global IDs.

Example:

```text
VXNlcjoxMDA=
```

These may encode:

```text
User:100
```

The encoded value still requires server-side authorisation.

---

# WebSockets

Object-level authorisation also applies to WebSocket messages.

Example:

```json
{
    "action": "subscribe",
    "conversationId": 9002
}
```

Test whether User A can subscribe to User B's controlled conversation.

Refer to:

```text
docs/web/websockets.md
```

---

# WebSocket Channel IDs

Potential references include:

```text
roomId
channelId
conversationId
userId
projectId
documentId
```

Authentication during the WebSocket handshake does not automatically guarantee authorisation for every subsequent message.

---

# Export Functions

High-value endpoints include:

```text
/export
/download
/report
/archive
/backup
```

Example:

```http
POST /api/export HTTP/1.1

{
    "accountId": 102
}
```

Test whether the export is restricted to the current user's authorised objects.

---

# Search Functions

Search endpoints may leak other users' objects.

Example:

```text
/api/search?userId=102
```

Even if direct object retrieval is protected, search functionality may expose:

```text
Names
IDs
Metadata
Documents
Email addresses
```

that can enable further BOLA testing.

---

# Batch Endpoints

Example:

```json
{
    "ids": [
        1001,
        1002,
        1003
    ]
}
```

Applications may correctly authorise single-object endpoints but fail to validate each item in a batch request.

Test mixed ownership:

```text
User A Object
User B Object
User A Object
```

using controlled objects.

---

# Bulk Operations

High-value examples:

```text
Bulk delete
Bulk update
Bulk export
Bulk download
Bulk assignment
```

Every object in the collection must be independently authorised.

---

# IDOR in Notifications

Potential endpoints:

```text
/notifications/100
/messages/100
/inbox/100
```

These often contain sensitive information.

---

# IDOR in Support Systems

Potential objects:

```text
Tickets
Attachments
Comments
Internal notes
Cases
```

Pay particular attention to:

```text
Internal support notes
```

and attachments.

---

# IDOR in Administrative Workflows

Potential objects:

```text
Users
Roles
Invitations
Audit logs
Reports
Approvals
```

Even if an endpoint is normally reachable only through an administrator UI, direct requests must enforce authorisation.

---

# IDOR in Password Reset Workflows

Object references may appear in:

```text
Reset request IDs
Account IDs
Recovery IDs
Email change IDs
```

Refer to the dedicated password reset page when added.

---

# IDOR in OAuth and OIDC Applications

Potential objects include:

```text
Connected accounts
Authorisations
Clients
Consents
Sessions
```

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# IDOR and JWT

Do not assume a JWT automatically prevents BOLA.

Example JWT:

```json
{
    "sub": "101",
    "role": "user"
}
```

Request:

```text
GET /api/users/102
```

The backend must compare:

```text
Authenticated identity
```

with:

```text
Requested object
```

according to the authorisation policy.

Refer to:

```text
docs/web/jwt.md
```

---

# IDOR and Mass Assignment

IDOR and mass assignment can combine.

Example:

```http
PATCH /api/profile/101 HTTP/1.1

{
    "accountId": 102,
    "displayName": "test"
}
```

Potential chain:

```text
Mass Assignment
      ↓
Object Relationship Modified
      ↓
Broken Authorisation
```

Mass assignment should be tested separately because the vulnerability mechanics differ.

---

# IDOR and Information Disclosure

Information disclosure frequently reveals object IDs.

Example:

```json
{
    "owner": {
        "id": 102
    }
}
```

That identifier may then be tested against:

```text
/users/102
/files?owner=102
/orders?user=102
```

Refer to:

```text
docs/web/information-disclosure.md
```

---

# IDOR and Business Logic

Some authorisation relationships depend on workflow state.

Example:

```text
Draft Invoice
Submitted Invoice
Approved Invoice
Paid Invoice
```

Different users may have access at different stages.

Map:

```text
Role
+
Object
+
State
+
Action
```

Refer to:

```text
docs/web/business-logic.md
```

---

# IDOR and Race Conditions

Authorisation checks may interact with concurrent operations.

Example:

```text
Check Ownership
      ↓
Ownership Changes
      ↓
Action Executes
```

This can create a TOCTOU-style problem.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Burp Suite Testing

Burp Suite is particularly useful for IDOR and BOLA testing because it allows requests from different users to be compared and replayed systematically.

A useful workflow is:

```text
Account A
   ↓
Browse Application
   ↓
Proxy History
   ↓
Identify Object References
   ↓
Send to Repeater
   ↓
Capture Account B Object ID
   ↓
Replace Object Reference
   ↓
Replay as Account A
   ↓
Compare Response
```

---

# Burp Repeater

Repeater is the primary manual tool for IDOR testing.

Example:

```http
GET /api/orders/1001 HTTP/1.1
Host: target.example
Authorization: Bearer USER_A_TOKEN
```

Baseline:

```text
User A → Object A
```

Then change only:

```text
1001
```

to the controlled User B object:

```text
1002
```

The important principle is:

```text
Change One Security-Relevant Variable
```

where possible.

---

# Response Comparison

Do not look only at:

```text
HTTP status
```

Compare:

```text
Status
Response length
JSON fields
Object owner
Object ID
Error message
Redirect
Side effects
Database state
```

A response may return:

```text
200 OK
```

but contain:

```text
{"error":"unauthorised"}
```

or return:

```text
403
```

after already performing a state-changing action.

---

# Burp Comparer

Burp Comparer can help compare:

```text
User A response
User B response
Unauthorised response
```

Useful differences include:

```text
Object data
Error text
Metadata
Response length
Headers
```

---

# Burp Intruder

Intruder can help identify exposed object references.

For example:

```http
GET /api/orders/§1001§ HTTP/1.1
```

Use only a small, controlled identifier set during authorised testing.

Example payloads:

```text
1000
1001
1002
1003
```

Prefer known controlled IDs over broad enumeration whenever possible.

PortSwigger's current IDOR testing workflow specifically demonstrates using Intruder against exposed object references. :contentReference[oaicite:2]{index=2}

---

# Burp Site Map Comparison

When two controlled users exist:

```text
User A
User B
```

browse the application as both users.

Then compare their accessible application surfaces.

PortSwigger recommends comparing site maps when testing horizontal access controls, alongside targeted Repeater testing. :contentReference[oaicite:3]{index=3}

This can reveal:

```text
Endpoints available to both users
Different object references
Role-specific functionality
Unexpected cross-user access
```

---

# Autorize

**Autorize** is one of the most useful Burp extensions for authorisation testing.

Its purpose is to automatically detect authorisation enforcement issues by replaying requests with alternative authentication context.

The current PortSwigger BApp Store lists Autorize as an authorisation-enforcement extension and shows it was updated in February 2026. :contentReference[oaicite:4]{index=4}

Typical workflow:

```text
Login as Low-Privilege User
        ↓
Capture Session / Token
        ↓
Configure Autorize
        ↓
Browse as Higher-Privilege / Different User
        ↓
Autorize Replays Requests
        ↓
Compare Authorised vs Unauthorised Response
        ↓
Review Potential Findings
```

Install it through:

```text
Burp Suite
  ↓
Extensions
  ↓
BApp Store
  ↓
Search: Autorize
```

Always manually verify results.

---

# AuthMatrix

**AuthMatrix** provides a matrix-based approach to authorisation testing.

The current BApp Store describes it as providing a simple way to test authorisation in web applications and web services. :contentReference[oaicite:5]{index=5}

Conceptually:

```text
                User A   User B   Admin   Anonymous

GET /profile/A    ✓        ✗       ✓         ✗

GET /profile/B    ✗        ✓       ✓         ✗

DELETE /user/B    ✗        ✗       ✓         ✗
```

This is particularly useful for applications with:

```text
Multiple roles
Many endpoints
Complex access rules
```

---

# Auth Analyzer

**Auth Analyzer** can repeat proxy requests using user-defined authentication headers or tokens.

The current BApp Store describes it as an extension for finding authorisation bugs by repeating Proxy requests with alternative headers and tokens. :contentReference[oaicite:6]{index=6}

This can be useful where authentication uses:

```text
Bearer tokens
API keys
Custom headers
Session tokens
```

---

# Agartha

The current BApp Store also lists **Agartha**, which includes an access matrix for authentication and authorisation auditing in addition to its injection and bypass functionality. :contentReference[oaicite:7]{index=7}

It can therefore be useful as a broader testing assistant.

For dedicated authorisation testing, however, tools such as:

```text
Autorize
AuthMatrix
Auth Analyzer
```

are easier to reason about because their purpose is narrower.

---

# AutoRepeater

AutoRepeater can automatically repeat requests while applying replacement rules and comparing responses.

This can be useful when testing:

```text
User A token
      ↓
Replace with User B token
      ↓
Replay
      ↓
Compare
```

The current BApp Store lists AutoRepeater as supporting automatic request repetition, replacement rules, and response diffing. :contentReference[oaicite:8]{index=8}

---

# Extension Safety

Burp extensions can:

```text
Read HTTP traffic
Modify HTTP traffic
Send requests
Access sensitive assessment data
```

PortSwigger notes that BApp extensions are third-party code and recommends reviewing them before installation. :contentReference[oaicite:9]{index=9}

For sensitive engagements:

```text
Review source
Use trusted extensions
Understand what traffic they generate
Disable unnecessary extensions
```

---

# Manual Testing Still Matters

Do not rely entirely on:

```text
Autorize says enforced
```

or:

```text
AuthMatrix says denied
```

Complex authorisation can depend on:

```text
Object state
User relationship
Role
Tenant
HTTP method
Request body
Workflow
Parent object
Child object
```

Automated tools do not understand the complete business policy.

---

# Simple IDOR Helper Script

For a controlled assessment, a small script can compare a known set of object IDs.

Example:

```python
#!/usr/bin/env python3

import requests

BASE_URL = "https://target.example/api/orders/{}"

OBJECT_IDS = [
    "1001",
    "1002",
    "1003",
]

HEADERS = {
    "Authorization": "Bearer REPLACE_WITH_TEST_TOKEN"
}

for object_id in OBJECT_IDS:

    url = BASE_URL.format(object_id)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10,
        allow_redirects=False
    )

    print(
        object_id,
        response.status_code,
        len(response.content)
    )
```

Use only:

```text
Known controlled identifiers
```

unless broader enumeration is explicitly authorised.

---

# Better Two-Account Comparison Script

For repeatable controlled testing:

```python
#!/usr/bin/env python3

import requests

BASE_URL = "https://target.example/api/orders/{}"

USER_A_TOKEN = "USER_A_TEST_TOKEN"
USER_B_TOKEN = "USER_B_TEST_TOKEN"

OBJECTS = {
    "user_a_order": "1001",
    "user_b_order": "1002",
}

SESSIONS = {
    "user_a": {
        "Authorization": f"Bearer {USER_A_TOKEN}"
    },
    "user_b": {
        "Authorization": f"Bearer {USER_B_TOKEN}"
    }
}

for user, headers in SESSIONS.items():

    print(f"\n=== {user} ===")

    for name, object_id in OBJECTS.items():

        response = requests.get(
            BASE_URL.format(object_id),
            headers=headers,
            timeout=10,
            allow_redirects=False
        )

        print(
            f"{name:20} "
            f"status={response.status_code} "
            f"length={len(response.content)}"
        )
```

Expected pattern:

```text
User A → User A Object = ALLOW
User A → User B Object = DENY

User B → User B Object = ALLOW
User B → User A Object = DENY
```

This is deliberately simple.

The goal is:

```text
Comparison
```

not uncontrolled enumeration.

---

# Response Fingerprinting

When automating comparisons, record:

```text
Status code
Response length
Content type
Redirect location
Selected JSON fields
Response hash
```

Do not rely on response length alone.

---

# JSON Response Comparison

For APIs, extract important fields such as:

```text
id
owner
userId
accountId
email
status
```

Example conceptual output:

```text
USER_A → OBJECT_A
status=200 owner=101

USER_A → OBJECT_B
status=200 owner=102
```

That is much stronger evidence than:

```text
Both responses have similar length.
```

---

# Object Discovery from JavaScript

Search JavaScript for:

```text
userId
accountId
customerId
orderId
documentId
projectId
invoiceId
messageId
conversationId
organisationId
organizationId
tenantId
```

Example:

```bash
grep -RniE \
'userId|accountId|customerId|orderId|documentId|projectId|invoiceId|messageId|conversationId|organisationId|organizationId|tenantId' \
.
```

---

# Endpoint Discovery

Search JavaScript for API routes:

```bash
grep -RniE \
'/api/|fetch\(|axios\.|XMLHttpRequest|graphql|WebSocket' \
.
```

Then inspect routes that contain object references.

---

# Interesting Parameter Names

Useful candidate names include:

```text
id
uid
user
userId
account
accountId
customer
customerId
order
orderId
invoice
invoiceId
document
documentId
file
fileId
project
projectId
team
teamId
group
groupId
organisation
organisationId
organization
organizationId
tenant
tenantId
message
messageId
conversation
conversationId
ticket
ticketId
```

These are discovery hints, not vulnerabilities.

---

# Burp Search

Search Proxy history for:

```text
"id":
userId
accountId
orderId
documentId
projectId
```

Also search for known controlled object IDs.

For example:

```text
1001
```

may reveal every endpoint where the same object is referenced.

---

# Identifier Reuse

An object identifier obtained from:

```text
GET /api/orders
```

may be usable in:

```text
GET /api/orders/{id}
PUT /api/orders/{id}
DELETE /api/orders/{id}
/api/export?order={id}
/api/invoice?order={id}
```

Always search for identifier reuse across endpoints.

---

# Differential Testing

The strongest pattern is:

```text
Same Request
Same User
Different Object
```

Example:

```text
User A + Object A → 200
User A + Object B → 403
```

Secure.

Potentially vulnerable:

```text
User A + Object A → 200
User A + Object B → 200
```

But verify the returned object actually belongs to User B.

---

# Do Not Infer Ownership from IDs Alone

Do not assume:

```text
Object 1002 belongs to User B
```

because the number looks different.

Prove ownership using controlled accounts.

For example:

```text
Login as User B
Create Object
Record ID
```

Then test that exact object as User A.

---

# Anonymous Testing

Remove authentication completely.

Example:

```http
GET /api/orders/1001 HTTP/1.1
Host: target.example
```

This tests:

```text
Unauthenticated Object Access
```

which may be more severe than horizontal BOLA.

---

# Session Swapping

Capture:

```text
User A request
```

Then replace:

```text
User A session
```

with:

```text
User B session
```

while leaving the object identifier unchanged.

This tests the inverse relationship:

```text
User B
   ↓
User A Object
```

---

# Token Swapping

For bearer tokens:

```http
Authorization: Bearer USER_A
```

replace only:

```text
USER_A
```

with:

```text
USER_B
```

Keep the requested object constant.

This produces clean evidence.

---

# Role Testing

Where roles exist:

```text
User
Manager
Administrator
Support
Auditor
```

create a role matrix.

Example:

| Endpoint | User | Manager | Admin |
|---|---|---|---|
| Own profile | Allow | Allow | Allow |
| Other profile | Deny | Maybe | Allow |
| Delete account | Deny | Deny | Allow |
| Audit logs | Deny | Maybe | Allow |

Test the intended policy rather than assuming every cross-role difference is a vulnerability.

---

# State Testing

Authorisation may depend on object state.

Example:

```text
Draft
Submitted
Approved
Archived
```

Create a matrix:

| State | Owner | Other User | Manager |
|---|---|---|---|
| Draft | Allow | Deny | Maybe |
| Submitted | Allow | Deny | Allow |
| Approved | Read | Deny | Allow |
| Archived | Read | Deny | Read |

---

# IDOR Testing Methodology

Use the following workflow.

## Step 1: Map Users and Roles

Identify:

```text
Anonymous
User A
User B
Manager
Administrator
Other relevant roles
```

---

## Step 2: Map Objects

Identify:

```text
Users
Accounts
Orders
Documents
Files
Projects
Messages
Tickets
Invoices
Reports
API resources
```

---

## Step 3: Record Controlled IDs

Create objects under each controlled account.

Example:

```text
User A Order = 1001
User B Order = 1002
```

---

## Step 4: Capture Baseline Requests

For each object:

```text
Owner accesses own object
```

Record:

```text
Request
Response
Status
Important fields
```

---

## Step 5: Swap Object References

Keep:

```text
User A session
```

and replace:

```text
Object A
```

with:

```text
Object B
```

---

## Step 6: Test CRUD

Test:

```text
Read
Create within parent
Update
Delete
Download
Export
Share
```

as applicable.

---

## Step 7: Test Alternative Interfaces

Check:

```text
REST
GraphQL
WebSockets
Mobile APIs
Legacy API versions
Exports
Background endpoints
```

---

## Step 8: Test Parent-Child Relationships

Check nested objects independently.

---

## Step 9: Verify Side Effects

For state-changing requests:

```text
Login as Object Owner
```

and confirm whether the change actually occurred.

---

## Step 10: Minimise Impact

Use:

```text
Controlled objects
Harmless markers
Reversible changes
```

where possible.

---

# High-Value IDOR Targets

Prioritise:

```text
Personal information
Financial information
Invoices
Orders
Documents
Messages
Support tickets
Attachments
Exports
Reports
Account settings
Email addresses
Phone numbers
Addresses
Payment information
API credentials
Security settings
MFA configuration
Password reset data
Administrative objects
```

---

# IDOR Testing Matrix

| Feature | Read | Create | Update | Delete | Export |
|---|---:|---:|---:|---:|---:|
| Profile | ✓ | N/A | ✓ | Maybe | Maybe |
| Orders | ✓ | ✓ | ✓ | ✓ | ✓ |
| Documents | ✓ | ✓ | ✓ | ✓ | ✓ |
| Messages | ✓ | ✓ | Maybe | ✓ | Maybe |
| Projects | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tickets | ✓ | ✓ | ✓ | ✓ | ✓ |

For every supported operation test:

```text
Owner
Other User
Anonymous
Higher Role
Lower Role
```

as appropriate.

---

# False Positives

A different object ID returning:

```text
200 OK
```

does not automatically prove IDOR.

The object may be:

```text
Public
Shared
Accessible by design
```

Verify intended access rules.

---

# False Positive: Generic Response

Example:

```json
{
    "status": "success"
}
```

may be identical for all IDs.

Check whether:

```text
Data changed
Object returned
Action occurred
```

before reporting.

---

# False Positive: Different Object Does Not Exist

Example:

```text
User A object = 1001
Test object = 1002
```

If object 1002 does not exist, a:

```text
404
```

does not prove authorisation is secure.

Use a known controlled object belonging to User B.

---

# False Positive: Shared Object

Objects may legitimately be shared through:

```text
Team membership
Project membership
Delegation
Public links
Organisation policy
```

Understand the application's authorisation model.

---

# Evidence Collection

For a strong IDOR finding collect:

```text
Account A identity
Account B identity
Object ownership
Baseline request
Baseline response
Cross-account request
Cross-account response
Affected endpoint
Affected method
Object identifier
Security impact
Screenshot
Side-effect verification
```

Avoid collecting unnecessary sensitive information.

---

# Strong Evidence Pattern

```text
1. User B creates controlled object.

2. Object ID is recorded as 1002.

3. User B successfully accesses /api/orders/1002.

4. User A requests /api/orders/1002.

5. User A receives HTTP 200.

6. Response contains User B's controlled object data.

7. No sharing relationship exists between the accounts.
```

This provides clear evidence of:

```text
Broken Object-Level Authorisation
```

---

# Example Finding: Read IDOR

```text
Finding:
Insecure Direct Object Reference Allows Access to Other Users' Invoices

Observed:
Two controlled user accounts were used during testing.

User B created an invoice with identifier 5002.

While authenticated as User A, the following request was submitted:

GET /api/invoices/5002

The application returned HTTP 200 and disclosed the invoice belonging to User B.

No sharing relationship existed between the two accounts.

Impact:
An authenticated attacker may access invoices belonging to other application users by modifying the invoice identifier.

Depending on the information contained within invoices, this may result in disclosure of personal, financial, or commercially sensitive information.

Recommendation:
Enforce object-level authorisation server-side for every invoice request. The application should verify that the authenticated user is authorised to access the requested invoice before returning any invoice data.
```

---

# Example Finding: Update IDOR

```text
Finding:
Broken Object-Level Authorisation Allows Modification of Other Users' Profiles

Observed:
User B's controlled profile had identifier 102.

While authenticated as User A, the profile identifier was changed from User A's identifier to 102 in the profile update request.

The application accepted the request and User B's profile was modified.

Impact:
An authenticated attacker may modify profile information belonging to other application users.

Recommendation:
Derive the target user from the authenticated session where possible. Where an object identifier must be supplied, explicitly verify that the authenticated user is authorised to modify that object.
```

---

# Example Finding: Delete IDOR

```text
Finding:
Broken Object-Level Authorisation Allows Deletion of Other Users' Documents

Observed:
User B created a controlled test document.

While authenticated as User A, the document identifier was supplied to the DELETE endpoint.

The application returned a successful response.

Logging back in as User B confirmed that the controlled document had been deleted.

Impact:
An authenticated attacker may delete documents belonging to other users, resulting in unauthorised modification and potential loss of data.

Recommendation:
Apply object-level authorisation before performing deletion and ensure that every destructive operation validates ownership or an equivalent permission relationship.
```

---

# Example Finding: GraphQL BOLA

```text
Finding:
GraphQL Resolver Does Not Enforce Object-Level Authorisation

Observed:
User B created a controlled order.

While authenticated as User A, the User B order identifier was supplied to the GraphQL order query.

The resolver returned the complete User B order object.

Impact:
An authenticated attacker may retrieve orders belonging to other users through the GraphQL API.

Recommendation:
Enforce object-level authorisation inside or before the affected resolver. Do not rely on knowledge of GraphQL object identifiers as an access-control mechanism.
```

---

# Reporting Titles

Useful titles include:

```text
Insecure Direct Object Reference Allows Access to Other Users' Documents

Broken Object-Level Authorisation Allows Modification of Other Users' Accounts

IDOR Allows Unauthorised Download of Invoices

GraphQL BOLA Exposes Other Users' Orders

WebSocket BOLA Allows Subscription to Other Users' Conversations

IDOR Allows Deletion of Other Users' Files

Missing Object-Level Authorisation on Export Endpoint

Broken Parent-Child Authorisation Allows Cross-Project Access
```

---

# Severity

Severity depends on:

```text
Data sensitivity
Action available
Number of affected objects
Authentication requirement
Predictability
Identifier leakage
Privilege boundary
Business impact
```

Examples:

```text
Public profile metadata
→ Low / Informational depending on design

Private user information
→ Medium / High

Financial records
→ High

Account modification
→ High

Security setting modification
→ High

Administrative object manipulation
→ High / Critical depending on impact
```

Do not rate severity based only on:

```text
ID is sequential
```

The important factor is:

```text
What unauthorised action becomes possible?
```

---

# Remediation

The fundamental fix is:

```text
Server-Side Object-Level Authorisation
```

for every object access.

---

# Derive Identity from the Session

Avoid accepting:

```text
userId
```

when the application already knows the authenticated user.

Instead of:

```http
GET /api/profile?userId=101
```

consider:

```http
GET /api/profile/me
```

where appropriate.

The server derives:

```text
Current User
```

from the authenticated session.

---

# Scope Database Queries

A vulnerable pattern may conceptually be:

```text
SELECT *
FROM orders
WHERE id = requested_id
```

A safer model is:

```text
SELECT *
FROM orders
WHERE id = requested_id
AND owner_id = current_user_id
```

The exact implementation depends on the application's authorisation model.

---

# Centralise Authorisation

Avoid duplicating inconsistent access-control checks across controllers.

Use:

```text
Central authorisation policies
Middleware
Service-layer checks
Framework policy mechanisms
```

where appropriate.

---

# Deny by Default

Authorisation logic should follow:

```text
No Explicit Permission
        ↓
       DENY
```

rather than:

```text
No Matching Restriction
        ↓
       ALLOW
```

---

# Check Every Operation

Protect:

```text
Read
Create
Update
Delete
Download
Export
Share
Archive
Approve
Restore
```

Do not assume protecting:

```text
GET
```

protects:

```text
PATCH
DELETE
```

---

# Validate Nested Relationships

For:

```text
/projects/{project}/documents/{document}
```

verify:

```text
Current User
     ↓
Can Access Project?
     ↓
Does Document Belong to Project?
     ↓
Can Access Document?
```

---

# Do Not Rely on Unpredictable IDs

UUIDs can reduce enumeration but should be considered:

```text
Defence in Depth
```

not:

```text
Authorisation
```

---

# Protect Bulk Operations

Authorise every individual object.

Do not perform:

```text
DELETE WHERE id IN (...)
```

without validating the complete authorised object set.

---

# Log Authorisation Failures

Monitor repeated access attempts involving:

```text
Different object IDs
Cross-user resources
Administrative objects
```

This may help identify active exploitation.

---

# Regression Testing

Authorisation vulnerabilities frequently return after application changes.

Create automated tests such as:

```text
User A cannot read User B object
User A cannot update User B object
User A cannot delete User B object
Anonymous cannot access User A object
```

These should become part of application security regression testing.

---

# IDOR / BOLA Checklist

## Accounts

```text
[ ] Anonymous context tested
[ ] User A available
[ ] User B available
[ ] Different roles available where relevant
[ ] Controlled objects created
```

## Object Discovery

```text
[ ] URL path IDs
[ ] Query parameters
[ ] JSON properties
[ ] XML properties
[ ] Hidden form fields
[ ] Cookies
[ ] Headers
[ ] GraphQL variables
[ ] WebSocket messages
[ ] JavaScript
[ ] API responses
```

## Identifier Types

```text
[ ] Numeric IDs
[ ] UUIDs
[ ] Usernames
[ ] Emails
[ ] File names
[ ] Order numbers
[ ] Account IDs
[ ] Project IDs
[ ] Encoded IDs
[ ] Composite IDs
```

## Operations

```text
[ ] Read
[ ] Create
[ ] Update
[ ] Delete
[ ] Download
[ ] Export
[ ] Share
[ ] Archive
[ ] Restore
[ ] Approve
```

## Interfaces

```text
[ ] Web application
[ ] REST API
[ ] GraphQL
[ ] WebSockets
[ ] Legacy APIs
[ ] Mobile APIs where in scope
```

## Relationships

```text
[ ] User ownership
[ ] Parent-child objects
[ ] Teams
[ ] Groups
[ ] Organisations
[ ] Projects
[ ] Shared resources
[ ] Delegated permissions
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Comparer
[ ] Intruder
[ ] Site map comparison
[ ] Autorize
[ ] AuthMatrix
[ ] Auth Analyzer
[ ] AutoRepeater where useful
```

## Verification

```text
[ ] Known User B object used
[ ] Ownership proven
[ ] Access policy understood
[ ] Response compared
[ ] Side effect verified
[ ] Real user data avoided
[ ] Minimum-impact proof used
```

---

# Quick Reference

```text
ACCOUNT A
    ↓
OBJECT A
    ↓
Baseline = ALLOW

ACCOUNT B
    ↓
OBJECT B
    ↓
Baseline = ALLOW

Now test:

ACCOUNT A
    ↓
OBJECT B
    ↓
Should = DENY

ACCOUNT B
    ↓
OBJECT A
    ↓
Should = DENY
```

If either cross-account request succeeds:

```text
Investigate Object-Level Authorisation
```

---

# Recommended Burp Workflow

```text
Create User A
      ↓
Create User B
      ↓
Create Object A
      ↓
Create Object B
      ↓
Browse Through Burp
      ↓
Map Object References
      ↓
Send Requests to Repeater
      ↓
Establish Baselines
      ↓
Swap Object IDs
      ↓
Swap Authentication Context
      ↓
Compare Responses
      ↓
Test CRUD
      ↓
Test Nested Objects
      ↓
Test REST / GraphQL / WebSockets
      ↓
Run Autorize / AuthMatrix
      ↓
Manually Verify Results
      ↓
Collect Minimal Evidence
      ↓
Report
```

---

# References

## PortSwigger Access Control

https://portswigger.net/web-security/access-control

PortSwigger Web Security Academy material covering access-control vulnerabilities, including horizontal and vertical privilege escalation and IDOR.

---

## PortSwigger Testing for IDORs

https://portswigger.net/burp/documentation/desktop/testing-workflow/vulnerabilities/access-controls/testing-for-idors

Burp Suite workflow for identifying and testing exposed object references.

---

## PortSwigger Testing Horizontal Access Controls

https://portswigger.net/burp/documentation/desktop/testing-workflow/vulnerabilities/access-controls/horizontal-access-controls

Guidance for testing cross-user access using controlled accounts, Repeater, and site-map comparison.

---

## OWASP Insecure Direct Object Reference Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html

OWASP defensive guidance for preventing IDOR vulnerabilities.

---

## OWASP Authorization Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

General guidance for implementing secure authorisation.

---

## OWASP Authorization Testing Automation Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Testing_Automation_Cheat_Sheet.html

Guidance for automated authorisation testing.

---

## OWASP Authorization Regression Testing Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Regression_Testing_Cheat_Sheet.html

Guidance for building repeatable authorisation regression tests.

---

## OWASP API Security

https://owasp.org/API-Security/

The OWASP API Security project includes Broken Object Level Authorization as a major API security risk.

---

## PortSwigger BApp Store

https://portswigger.net/bappstore

Burp Suite extension repository containing authorisation testing extensions including:

```text
Autorize
AuthMatrix
Auth Analyzer
AutoRepeater
Agartha
```

---

# Final IDOR / BOLA Testing Model

```text
                         APPLICATION
                              ↓
                     IDENTIFY OBJECTS
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
            USER            ORDER          DOCUMENT
              ↓               ↓               ↓
          OBJECT ID        OBJECT ID       OBJECT ID
              └───────────────┼───────────────┘
                              ↓
                     CREATE TWO ACCOUNTS
                              ↓
                   ┌──────────┴──────────┐
                   ↓                     ↓
                USER A                USER B
                   ↓                     ↓
               OBJECT A              OBJECT B
                   ↓                     ↓
                   └──────────┬──────────┘
                              ↓
                     BASELINE TESTING
                              ↓
                 A → A = SHOULD ALLOW
                 B → B = SHOULD ALLOW
                              ↓
                     CROSS-USER TESTING
                              ↓
                 A → B = SHOULD DENY
                 B → A = SHOULD DENY
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
                  DENIED              ALLOWED
                    ↓                   ↓
             CONTROL WORKS        VERIFY OWNERSHIP
                                        ↓
                               TEST OTHER OPERATIONS
                                        ↓
                         ┌──────────────┼─────────────┐
                         ↓              ↓             ↓
                        READ          UPDATE        DELETE
                         ↓              ↓             ↓
                         └──────────────┼─────────────┘
                                        ↓
                                TEST OTHER INTERFACES
                                        ↓
                         REST / GRAPHQL / WEBSOCKETS
                                        ↓
                               MANUAL + BURP TOOLS
                                        ↓
                    REPEATER / AUTORIZE / AUTHMATRIX
                                        ↓
                                 VERIFY IMPACT
                                        ↓
                               MINIMUM SAFE PROOF
                                        ↓
                                     REPORT
```

The central principle is:

> An object identifier is a reference, not an authorisation mechanism. Every request that reads, modifies, deletes, exports, or otherwise interacts with an object must independently verify that the authenticated user is authorised to perform that action on that specific object.
