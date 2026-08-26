# Authorisation Testing

Authorisation determines **what an authenticated user is permitted to access or perform**.

Authentication answers:

```text
Who are you?
```

Authorisation answers:

```text
What are you allowed to do?
```

An application can have strong authentication while still containing serious authorisation vulnerabilities.

Examples include:

- Accessing another user's data
- Modifying another user's resources
- Accessing administrative functionality
- Performing privileged API operations
- Accessing resources belonging to another organisation
- Changing roles or permissions
- Calling hidden endpoints directly
- Bypassing frontend access restrictions
- Manipulating object identifiers
- Exploiting inconsistent access controls between API versions

!!! warning "Authorised Security Testing"
    Perform these techniques only against applications and accounts for which you have explicit authorisation. Where possible, use dedicated test accounts representing different roles and organisations.

---

# Objectives

Authorisation testing should determine whether users can:

- Access objects belonging to other users
- Modify objects belonging to other users
- Delete objects belonging to other users
- Execute functionality outside their assigned role
- Access administrative functionality
- Manipulate roles or permissions
- Access another organisation or tenant
- Bypass access controls through alternative endpoints
- Bypass access controls using different HTTP methods
- Access APIs not exposed through the interface
- Access resources using predictable identifiers
- Exploit mass assignment
- Access archived, disabled or hidden functionality
- Circumvent workflow restrictions

A practical workflow is:

```text
Identify Roles
     ↓
Identify Objects
     ↓
Identify Privileged Functions
     ↓
Build Access Matrix
     ↓
Capture Legitimate Requests
     ↓
Replay Without Authentication
     ↓
Replay as Another User
     ↓
Replay as Another Role
     ↓
Manipulate Object Identifiers
     ↓
Manipulate Privilege Parameters
     ↓
Test Alternative Endpoints
     ↓
Test HTTP Methods
     ↓
Test Tenant Boundaries
     ↓
Validate Server-Side Enforcement
```

---

# 1. Understand the Access-Control Model

Before testing, determine how the application models access.

Common models include:

```text
Role-Based Access Control
Attribute-Based Access Control
Discretionary Access Control
Mandatory Access Control
Relationship-Based Access Control
Tenant-Based Access Control
Object Ownership
```

Web applications frequently combine several models.

For example:

```text
User
 │
 ├── belongs to Organisation A
 │
 ├── has role "Manager"
 │
 └── owns Project 123
```

Access might therefore depend on:

```text
Authentication
+
Role
+
Organisation
+
Object ownership
+
Object state
```

Understanding these relationships is essential.

---

# 2. Identify Application Roles

Determine which roles exist.

Examples:

```text
Unauthenticated
User
Premium User
Manager
Moderator
Support
Administrator
Super Administrator
```

Enterprise applications may contain:

```text
Employee
Manager
Department Administrator
Organisation Administrator
Global Administrator
Auditor
Read-Only User
Service Account
```

Record each role.

---

# 3. Identify Objects

Authorisation often protects objects rather than pages.

Examples:

```text
User
Account
Profile
Document
Invoice
Order
Ticket
Message
Project
Report
Organisation
File
API key
Device
```

Determine how objects are identified.

Examples:

```text
123
456
```

or:

```text
550e8400-e29b-41d4-a716-446655440000
```

or:

```text
document-84721
```

UUIDs do not eliminate authorisation requirements.

A difficult-to-guess identifier is not an access-control mechanism.

---

# 4. Identify Privileged Functions

Map functionality available to different users.

Examples:

```text
Create user
Delete user
Modify user
Change role
Reset password
Create API key
Export data
View reports
Manage billing
Upload files
Delete files
Configure application
Manage organisation
```

Administrative interfaces are particularly important.

---

# 5. Build an Access-Control Matrix

An access-control matrix makes testing systematic.

Example:

| Function | Anonymous | User | Manager | Admin |
|---|---:|---:|---:|---:|
| View own profile | No | Yes | Yes | Yes |
| View another profile | No | No | Limited | Yes |
| Edit own profile | No | Yes | Yes | Yes |
| Edit another profile | No | No | Limited | Yes |
| View reports | No | No | Yes | Yes |
| Create user | No | No | No | Yes |
| Delete user | No | No | No | Yes |
| Manage roles | No | No | No | Yes |

The matrix provides a clear set of tests.

For every:

```text
Role
×
Function
×
Object
```

ask:

```text
Should this access be permitted?
```

Then verify it.

---

# 6. Use Multiple Test Accounts

Authorisation testing is significantly easier with at least two accounts.

Use:

```text
User A
User B
```

Preferably also:

```text
Administrator
```

For multi-tenant applications:

```text
Organisation A
 ├── User A
 └── Admin A

Organisation B
 ├── User B
 └── Admin B
```

This allows realistic testing of ownership and tenant boundaries.

---

# 7. The Two-Account Method

The two-account method is one of the most useful authorisation-testing techniques.

Assume:

```text
User A
User B
```

User A owns:

```text
/api/documents/1001
```

User B owns:

```text
/api/documents/2002
```

Capture User A's request:

```http
GET /api/documents/1001 HTTP/1.1
Host: target.example
Cookie: session=USER_A
```

Now use User B's authenticated session:

```http
GET /api/documents/1001 HTTP/1.1
Host: target.example
Cookie: session=USER_B
```

Expected:

```text
Access denied
```

If User B receives User A's document, object-level authorisation may be broken.

---

# 8. IDOR

Insecure Direct Object Reference occurs when an application exposes an object identifier and fails to enforce appropriate access control when the identifier is changed.

Example:

```text
/account?id=1001
```

Changing:

```text
1001
```

to:

```text
1002
```

must not provide unauthorised access to another user's account.

---

# 9. IDOR Locations

Object identifiers may appear in:

```text
URL path
Query string
POST body
JSON
XML
Cookies
Headers
GraphQL variables
WebSocket messages
```

Examples:

```text
/profile?id=123
```

```text
/documents/123
```

```json
{
  "documentId": 123
}
```

```json
{
  "user": {
    "id": 123
  }
}
```

Do not restrict IDOR testing to URL parameters.

---

# 10. BOLA

In API security, object-level access-control weaknesses are commonly described as:

```text
Broken Object Level Authorization
```

or:

```text
BOLA
```

Example:

```http
GET /api/v1/orders/7312 HTTP/1.1
Authorization: Bearer USER_A_TOKEN
```

Change:

```text
7312
```

to an order belonging to User B.

The API must verify:

```text
Is this authenticated user permitted to access this specific object?
```

not merely:

```text
Is the user authenticated?
```

---

# 11. Read Versus Write Authorisation

Test more than `GET`.

An application may correctly prevent viewing another user's object while still allowing it to be modified.

Test relevant operations:

```text
GET
POST
PUT
PATCH
DELETE
```

Example:

```http
PATCH /api/profile/123 HTTP/1.1
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "displayName": "Updated"
}
```

Authorisation must apply to the modification itself.

---

# 12. Horizontal Privilege Escalation

Horizontal privilege escalation occurs when a user accesses resources belonging to another user with an equivalent privilege level.

Example:

```text
User A
  ↓
User B's invoice
```

Both users may have the same role.

The vulnerability exists because ownership is not enforced.

---

# 13. Horizontal Testing

For each object owned by User A:

```text
Profile
Document
Order
Invoice
Ticket
Message
API key
File
```

attempt the same request as User B.

Conceptually:

```text
User A request
      ↓
Replace session/token with User B
      ↓
Keep User A object identifier
      ↓
Send
```

Expected:

```text
403 Forbidden
```

or another secure denial response.

---

# 14. Vertical Privilege Escalation

Vertical privilege escalation occurs when a lower-privileged user accesses functionality intended for a higher-privileged role.

Example:

```text
Normal User
     ↓
Administrative Function
```

Possible targets include:

```text
/admin
/admin/users
/admin/settings
/api/admin/users
/api/admin/config
/management
/internal
```

---

# 15. Hidden Administrative URLs

Frontend navigation is not access control.

A normal user may not see:

```text
Admin
```

in the interface, but the underlying endpoint may still exist.

JavaScript might reveal:

```text
/admin/users
```

or:

```text
/api/admin/users
```

Request the endpoint directly with the lower-privileged test account.

The server must independently enforce the required role.

---

# 16. Client-Side Authorisation

JavaScript may contain checks such as:

```javascript
if (user.role === "admin") {
    showAdminPanel();
}
```

This only controls the interface.

The backend must separately verify access.

Search JavaScript for:

```bash
grep -RniE \
'role|permission|isAdmin|admin|authoriz|privilege|access' \
javascript/
```

Interesting code may reveal functionality worth testing directly.

---

# 17. Role Parameters

Requests may contain privilege-related parameters.

Examples:

```text
role
isAdmin
admin
permission
permissions
group
userType
accountType
accessLevel
```

Example:

```json
{
  "username": "testuser",
  "role": "user"
}
```

The server should not allow ordinary users to assign themselves unauthorised privileges.

---

# 18. Mass Assignment

Frameworks may automatically bind request parameters to application objects.

Suppose the intended request is:

```json
{
  "displayName": "Asif"
}
```

but the underlying user object also contains:

```text
role
isAdmin
verified
organisationId
permissions
```

If these fields can also be supplied by the client, mass assignment may create an authorisation weakness.

For example, during authorised testing, check whether unexpected privilege-related properties are accepted and whether they affect server-side state.

Do not assume acceptance from the response alone. Verify the resulting account state.

---

# 19. Registration and Privilege Assignment

Registration requests deserve particular attention.

Example:

```json
{
  "email": "user@example.com",
  "password": "Password123!",
  "role": "user"
}
```

Determine whether privilege-related fields are:

```text
Ignored
Rejected
Validated server-side
```

The client should not decide the account's security role.

---

# 20. Profile Update

Profile update endpoints frequently expose mass-assignment opportunities.

Example:

```http
PATCH /api/profile HTTP/1.1
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "displayName": "Test"
}
```

Look at responses and JavaScript to identify additional model properties.

Potentially sensitive properties include:

```text
role
permissions
organisation
tenant
verified
accountStatus
```

Only test properties relevant to the application's observed data model.

---

# 21. Function-Level Authorisation

Object-level authorisation asks:

```text
Can User A access Object B?
```

Function-level authorisation asks:

```text
Can User A perform this function at all?
```

Examples:

```text
Delete user
Create administrator
Generate report
Export all records
Change configuration
Reset another user's password
```

APIs must enforce both.

---

# 22. BFLA

In API security, insufficient function-level authorisation is commonly described as:

```text
Broken Function Level Authorization
```

or:

```text
BFLA
```

Example:

```http
DELETE /api/admin/users/123 HTTP/1.1
Authorization: Bearer NORMAL_USER_TOKEN
```

The API should verify whether the authenticated user has permission to perform the administrative action.

---

# 23. HTTP Method Testing

Access controls may differ between HTTP methods.

For example:

```text
GET /api/users/123
```

may be protected while:

```text
PATCH /api/users/123
```

is not.

For relevant endpoints, compare:

```text
GET
POST
PUT
PATCH
DELETE
```

Do not blindly send state-changing requests to production objects.

Use dedicated test objects.

---

# 24. Method Override

Some frameworks support method override mechanisms.

Examples include headers such as:

```text
X-HTTP-Method-Override
```

or parameters used by particular frameworks.

If the application legitimately supports method overrides, verify that authorisation is applied to the effective operation rather than only the original request method.

---

# 25. Alternative Endpoints

The same functionality may exist through several endpoints.

Example:

```text
/api/users/123
/api/v1/users/123
/api/v2/users/123
/mobile/users/123
/internal/users/123
```

Security controls may differ between versions.

Always compare equivalent functionality across exposed interfaces.

---

# 26. Legacy APIs

Older API versions can be particularly important.

Example:

```text
/api/v3/account
```

may have modern controls while:

```text
/api/v1/account
```

remains accessible.

JavaScript, historical URLs and API documentation can reveal legacy endpoints.

---

# 27. Multi-Tenant Applications

Multi-tenant applications require strong isolation between organisations.

Example:

```text
Organisation A
     ↓
Users
Projects
Invoices
Documents

Organisation B
     ↓
Users
Projects
Invoices
Documents
```

Users from Organisation A should not access Organisation B's resources unless explicitly authorised.

---

# 28. Tenant Identifiers

Tenant information may appear as:

```text
tenantId
organisationId
companyId
customerId
workspaceId
teamId
```

Example:

```json
{
  "organisationId": 100,
  "documentId": 500
}
```

Changing:

```text
organisationId
```

must not allow access to another tenant.

The server should derive trusted tenancy information from the authenticated identity wherever appropriate.

---

# 29. Nested Object Authorisation

Objects may be nested.

Example:

```text
Organisation
   ↓
Project
   ↓
Document
```

Endpoint:

```text
/api/organisations/10/projects/20/documents/30
```

The application should validate the complete relationship.

It is not enough to verify only:

```text
document 30 exists
```

The server should ensure that the document belongs to the expected project and organisation and that the user can access that hierarchy.

---

# 30. Parent-Child Relationships

Consider:

```text
/api/projects/100/documents/500
```

Try legitimate combinations using your authorised test objects.

For example:

```text
Project A + Document A
```

versus:

```text
Project A + Document B
```

The backend should verify that the requested child object belongs to the permitted parent.

---

# 31. UUIDs

Applications often use UUIDs:

```text
550e8400-e29b-41d4-a716-446655440000
```

This reduces simple enumeration but does not replace access control.

If User B obtains User A's UUID through:

```text
Logs
Links
Shared resources
API responses
JavaScript
Referer data
Search results
Notifications
```

the backend must still reject unauthorised access.

---

# 32. Encoded Identifiers

Identifiers may be encoded:

```text
MTIz
```

which may simply be Base64 for:

```text
123
```

Other representations may include:

```text
Hex
Base64
Hashids
Composite identifiers
Signed identifiers
```

Encoding does not itself provide authorisation.

---

# 33. Object IDs in Responses

API responses frequently expose identifiers useful for testing.

Example:

```json
{
  "id": 7312,
  "ownerId": 84,
  "organisationId": 12
}
```

Record relationships between:

```text
User
Object
Organisation
Parent object
```

This makes authorisation testing much more systematic.

---

# 34. Search Functionality

Search endpoints can expose objects that direct endpoints protect correctly.

Example:

```text
/api/search?q=invoice
```

Test whether search results respect:

```text
Object ownership
Role
Tenant
Visibility
```

Do not test only the object's primary endpoint.

---

# 35. Export Functionality

Export functionality can expose large amounts of data.

Examples:

```text
/export
/api/export
/reports/export
/download/csv
```

Test whether users can export:

```text
Another user's data
Another tenant's data
Administrative reports
Hidden fields
```

Exports often use different backend code paths than normal views.

---

# 36. File Access

File endpoints frequently contain object-level authorisation issues.

Examples:

```text
/files/123
/download?id=123
/api/documents/123/download
```

Test whether User B can access files belonging to User A.

Also test whether access control is enforced on:

```text
Preview
Download
Metadata
Delete
Rename
Share
```

---

# 37. Static File URLs

Applications sometimes protect a document page but expose the underlying file through a predictable static URL.

Example:

```text
/account/document/123
```

links to:

```text
/uploads/documents/123.pdf
```

Determine whether the underlying resource is itself appropriately protected.

---

# 38. Temporary Download URLs

Applications may generate signed or temporary download URLs.

Review:

```text
Expiration
Object binding
User binding where appropriate
Permissions
Reuse behaviour
```

A signed URL can intentionally function as a bearer capability, so assess behaviour against the application's intended security model.

---

# 39. Delete Operations

Deletion is often overlooked.

Example:

```http
DELETE /api/documents/123 HTTP/1.1
Authorization: Bearer TOKEN
```

Test with dedicated objects belonging to different authorised test accounts.

A user may be unable to view another user's object but still be able to delete it if authorisation is inconsistent.

---

# 40. Update Operations

Similarly test:

```text
PUT
PATCH
```

Example:

```http
PATCH /api/orders/123 HTTP/1.1
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "description": "Updated"
}
```

The backend must verify ownership and permissions before modification.

---

# 41. Creation Operations

Creation also requires authorisation.

Examples:

```text
Create user
Create organisation
Create API key
Create admin
Create project
Create invitation
```

A normal user should not be able to create objects requiring higher privileges simply by discovering the endpoint.

---

# 42. Administrative APIs

Search for:

```text
/admin
/api/admin
/management
/manage
/internal
/api/internal
```

JavaScript search:

```bash
grep -RniE \
'/admin|/api/admin|/management|/manage|/internal|/api/internal' \
javascript/
```

Administrative APIs are high-value targets for role-based authorisation testing.

---

# 43. Hidden Buttons

A UI may hide actions based on role.

For example:

```javascript
if (!user.isAdmin) {
    hideDeleteButton();
}
```

This does not prevent the underlying request from being sent manually.

Capture the administrative request using an authorised administrative test account, then replay it using the lower-privileged test account.

---

# 44. Burp Suite Workflow

A practical Burp workflow is:

```text
User A
  ↓
Perform Action
  ↓
Capture Request
  ↓
Send to Repeater
  ↓
Replace User A Session
  ↓
Use User B Session
  ↓
Keep User A Object
  ↓
Send
  ↓
Compare
```

This method works well for:

```text
IDOR
BOLA
Horizontal privilege escalation
Tenant isolation
```

---

# 45. Vertical Testing With Burp

For vertical access control:

```text
Administrator
     ↓
Perform Admin Action
     ↓
Capture Request
     ↓
Send to Repeater
     ↓
Replace Admin Session
     ↓
Use Normal User Session
     ↓
Send
```

Expected:

```text
Access denied
```

This is often more effective than guessing administrative endpoints.

---

# 46. Burp Repeater

Repeater should be central to manual authorisation testing.

For each request, modify one variable at a time:

```text
Session
Token
Object ID
Role-related parameter
Organisation ID
HTTP method
Endpoint version
```

This allows you to determine which control actually governs access.

---

# 47. Burp Comparer

Use Comparer when responses are similar.

Compare:

```text
Authorised request
Unauthorised request
```

Look for differences in:

```text
Body
Status
Headers
Response length
JSON properties
```

A `200 OK` does not necessarily mean the action succeeded.

Always verify the resulting state.

---

# 48. Match and Replace

During complex multi-account testing, Burp's Match and Replace functionality can help switch between controlled test identities.

Be careful to keep track of which account is active.

For sensitive tests, manual session replacement in Repeater is often easier to reason about.

---

# 49. Burp Autorize

The Autorize extension can assist with access-control testing by replaying requests using another user's session.

Typical concept:

```text
Browse as privileged user
        ↓
Autorize captures requests
        ↓
Requests replayed with lower-privileged credentials
        ↓
Responses compared
```

Automated results should always be manually verified.

---

# 50. AuthMatrix

AuthMatrix can help model multiple:

```text
Users
Roles
Requests
Permissions
```

This can be useful for applications with complex access-control matrices.

Manual verification remains important for high-impact findings.

---

# 51. Unauthenticated Access

For every sensitive endpoint, test whether authentication is required.

Take:

```http
GET /api/account HTTP/1.1
Cookie: session=...
```

Remove:

```text
Cookie
```

and resend.

For token-based APIs, remove:

```text
Authorization
```

Expected:

```text
401 Unauthorized
```

or equivalent denial.

---

# 52. Authentication Versus Authorisation

Understand the distinction between:

```text
401 Unauthorized
```

and:

```text
403 Forbidden
```

Conceptually:

```text
401
→ Authentication required or invalid
```

```text
403
→ Identity understood, but access denied
```

Applications do not always follow these semantics exactly, so focus on actual access rather than status code alone.

---

# 53. Response Status Is Not Enough

Suppose:

```http
HTTP/1.1 403 Forbidden
```

but the response still contains:

```json
{
  "name": "Sensitive Document",
  "owner": "user@example.com"
}
```

Access control is still leaking information.

Always inspect:

```text
Response body
Headers
Metadata
Side effects
```

---

# 54. Error-Based Information Leakage

Unauthorised requests may reveal whether an object exists.

Compare:

```text
Object exists but forbidden
```

against:

```text
Object does not exist
```

For example:

```text
403 Forbidden
```

versus:

```text
404 Not Found
```

Depending on the application's threat model, this may permit object enumeration.

---

# 55. GraphQL Authorisation

GraphQL requires authorisation at resolver and object level.

Example:

```graphql
query {
  user(id: 123) {
    email
    role
  }
}
```

Changing:

```text
123
```

to another user's identifier must trigger appropriate authorisation.

---

# 56. GraphQL Mutations

Test mutations as well as queries.

Example:

```graphql
mutation {
  updateUser(
    id: 123
    name: "Updated"
  ) {
    id
    name
  }
}
```

The server should verify:

```text
Who is making the request?
What object is being modified?
Is this operation permitted?
```

---

# 57. GraphQL Nested Objects

GraphQL can expose authorisation issues through nested relationships.

Example:

```graphql
query {
  organisation(id: 10) {
    users {
      id
      email
    }
  }
}
```

Access control must apply throughout the returned object graph.

---

# 58. WebSocket Authorisation

WebSocket connections also require authorisation.

The initial connection may be authenticated, but individual messages may perform actions against objects.

Example:

```json
{
  "action": "getMessage",
  "messageId": 123
}
```

Changing:

```text
messageId
```

should not expose another user's message.

---

# 59. WebSocket Subscriptions

Applications may subscribe users to channels such as:

```text
user-123
organisation-10
admin-events
project-500
```

The server must verify whether the user is permitted to subscribe to the requested channel.

Do not rely on obscure channel names.

---

# 60. Mobile APIs

Mobile applications often use the same backend as web applications but may expose additional endpoints.

Look for:

```text
/api/mobile
/mobile/api
/api/v1
/api/v2
```

If mobile API endpoints are within scope, compare their authorisation controls with the web application.

---

# 61. API Documentation

Documentation can reveal privileged functionality.

Look for authorised access to:

```text
/swagger
/swagger-ui
/api-docs
/openapi.json
/openapi.yaml
```

Documentation may expose:

```text
Administrative routes
Object IDs
Required roles
Hidden parameters
Legacy APIs
```

Discovery of documentation does not itself mean every documented operation is authorised for testing. Follow the assessment scope.

---

# 62. OpenAPI Analysis

OpenAPI specifications can make authorisation testing systematic.

For each operation, record:

```text
Method
Path
Authentication
Parameters
Object identifiers
Expected role
```

Then build an access-control matrix from the API definition.

---

# 63. JavaScript Route Analysis

Search JavaScript for application routes.

```bash
grep -RniE \
'admin|management|internal|settings|users|roles|permissions|organisation|tenant' \
javascript/
```

JavaScript may expose privileged endpoints even when the interface hides them.

---

# 64. Historical URLs

Historical URL sources may reveal old administrative or API endpoints.

Examples:

```bash
gau example.com
```

```bash
echo example.com | waybackurls
```

Search:

```bash
grep -Ei \
'admin|manage|internal|api|user|account|role|permission'
```

Only interact with discovered endpoints that remain within the authorised scope.

---

# 65. Content Discovery

Content discovery can reveal:

```text
/admin/
/management/
/internal/
/staff/
/moderator/
/api/admin/
```

These discoveries should feed into authorisation testing.

The question is not merely:

```text
Does the endpoint exist?
```

but:

```text
Which identities are permitted to access it?
```

---

# 66. Workflow Authorisation

Business workflows may contain state-based restrictions.

Example:

```text
Draft
  ↓
Submitted
  ↓
Approved
  ↓
Paid
```

A normal user may be permitted to edit a draft but not an approved object.

Test whether direct requests can bypass these state restrictions.

---

# 67. State Transition Testing

For an authorised test object:

```text
Object State A
      ↓
Allowed Action
      ↓
Object State B
```

Determine whether users can invoke operations that should only be available in another state.

Examples:

```text
Approve own request
Modify approved invoice
Cancel completed transaction
Edit closed ticket
```

These are often business-logic and authorisation issues simultaneously.

---

# 68. Ownership Changes

Applications may allow objects to be reassigned.

Example:

```json
{
  "ownerId": 123
}
```

Test whether ordinary users can:

```text
Change ownership
Assign objects to privileged users
Move objects between organisations
Claim another user's object
```

Ownership fields should be controlled according to server-side policy.

---

# 69. Organisation Invitations

Multi-user applications often support invitations.

Example:

```text
Invite User
   ↓
Invitation Token
   ↓
Join Organisation
```

Review:

```text
Which organisation issued the invitation?
What role is assigned?
Can the role be modified?
Can the invitation be reused?
Is the invitation bound to the intended recipient?
```

---

# 70. Role Changes

Role-management functionality is highly sensitive.

Example:

```http
PATCH /api/users/123/role HTTP/1.1
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "role": "admin"
}
```

Replay using a lower-privileged test account.

The server must reject unauthorised role modifications.

---

# 71. Permission Changes

Some applications use granular permissions rather than roles.

Example:

```json
{
  "permissions": [
    "read",
    "write",
    "delete"
  ]
}
```

Test whether users can alter their own permission set or another user's permissions without the appropriate privilege.

---

# 72. API Keys

API key management also requires authorisation.

Test:

```text
View key
Create key
Rotate key
Delete key
Rename key
Change key permissions
```

User A should not be able to manage User B's API keys unless explicitly authorised.

---

# 73. Billing Functionality

Billing endpoints can contain high-impact authorisation issues.

Examples:

```text
/api/billing
/api/invoices
/api/subscriptions
/api/payment-methods
```

Test:

```text
Object ownership
Tenant isolation
Administrative actions
Invoice downloads
Subscription changes
```

Use dedicated test data and avoid actions that create real charges unless explicitly authorised.

---

# 74. Support Functionality

Support and helpdesk roles sometimes have elevated access.

Examples:

```text
Impersonate user
Reset MFA
Reset password
View account
Unlock account
```

These functions should have strict server-side authorisation and auditing.

---

# 75. User Impersonation

Some administrative systems intentionally allow:

```text
Login as user
Impersonate
View as customer
```

Review:

```text
Who can initiate impersonation?
Which users can be impersonated?
Are privileged accounts excluded?
Is the action logged?
Can the impersonated session escalate further?
```

---

# 76. Soft-Deleted Objects

Applications may retain deleted records.

Test whether deleted objects remain accessible through direct identifiers.

Example:

```text
DELETE /api/documents/123
```

followed by:

```text
GET /api/documents/123
```

Expected behaviour depends on the application, but deleted data should not unexpectedly remain available to unauthorised users.

---

# 77. Archived Objects

Similarly test:

```text
Archived
Disabled
Expired
Closed
```

objects.

Frontend filtering should not be the only mechanism preventing access.

---

# 78. Caching

Authorised responses containing sensitive data should not accidentally become available to another user through shared caching.

Review relevant:

```text
Cache-Control
Vary
CDN behaviour
Proxy caching
```

This is especially important where responses depend on:

```text
Authorization
Cookie
Tenant
```

---

# 79. Object Enumeration

Predictable IDs may make testing easier:

```text
1001
1002
1003
```

But predictable identifiers are not necessarily vulnerabilities by themselves.

The security issue occurs when changing the identifier results in unauthorised access.

Keep the distinction clear:

```text
Predictable ID
≠
IDOR

Predictable ID
+
Missing object-level authorisation
=
IDOR / BOLA
```

---

# 80. Burp Intruder for Object IDs

For authorised test datasets, Intruder can help compare multiple known object identifiers.

Example position:

```text
GET /api/document/§1001§
```

Use controlled identifiers belonging to your test accounts.

Compare:

```text
Status
Length
Words
Response content
```

Avoid uncontrolled enumeration of production records.

---

# 81. Authorisation Testing Script Logic

For larger applications, the testing model can be automated conceptually:

```text
For each endpoint
    For each test identity
        Send request
        Record status
        Record length
        Record response hash
        Compare expected permission
```

The result can become an access matrix.

Automation should identify candidates.

Manual validation should confirm vulnerabilities.

---

# 82. Record Expected Versus Actual Behaviour

For every test, record:

| Identity | Object | Action | Expected | Actual |
|---|---|---|---|---|
| User A | User A document | Read | Allow | Allow |
| User B | User A document | Read | Deny | Deny |
| User B | User A document | Update | Deny | Allow |
| Admin | User A document | Read | Allow | Allow |

The third row immediately identifies an authorisation problem.

---

# 83. Evidence Collection

For confirmed findings, preserve:

```text
Original authorised request
Unauthorised request
Original response
Unauthorised response
Test identities
Object ownership
Expected behaviour
Actual behaviour
Impact
```

Avoid including unnecessary sensitive data in screenshots or reports.

---

# 84. Reporting IDOR / BOLA

A clear finding title could be:

```text
Broken Object-Level Authorisation Allows Access to Other Users' Documents
```

The description should explain:

```text
Who the attacker must be
Which object is affected
Which identifier is manipulated
Which authorisation check is missing
What data or action becomes available
```

---

# 85. Reporting Vertical Privilege Escalation

Example title:

```text
Insufficient Function-Level Authorisation Allows Access to Administrative Functionality
```

Explain:

```text
Normal user
      ↓
Administrative endpoint
      ↓
Server accepts request
      ↓
Privileged action performed
```

---

# 86. Remediation Principles

Access control should be:

```text
Server-side
Centralised where practical
Deny-by-default
Applied consistently
Validated on every request
Based on trusted identity information
Applied to both objects and functions
```

Do not rely on:

```text
Hidden buttons
Hidden URLs
JavaScript
Unpredictable IDs
Client-supplied roles
Client-supplied tenant IDs
Frontend routing
```

---

# 87. Object-Level Authorisation Pattern

Conceptually, the backend should perform:

```text
Request
   ↓
Authenticate User
   ↓
Load Requested Object
   ↓
Determine Ownership / Relationship
   ↓
Evaluate Policy
   ↓
Allow or Deny
```

Not:

```text
Request
   ↓
Object Exists?
   ↓
Return Object
```

---

# 88. Tenant Authorisation Pattern

A safer tenant-aware model is:

```text
Authenticated User
       ↓
Trusted Tenant Context
       ↓
Database Query Restricted to Tenant
       ↓
Object
```

rather than trusting:

```text
tenantId
```

supplied by the client without validation.

---

# 89. Authorisation Testing Checklist

## Mapping

- [ ] Identify application roles
- [ ] Identify user types
- [ ] Identify privileged functions
- [ ] Identify objects
- [ ] Identify object identifiers
- [ ] Identify ownership relationships
- [ ] Identify organisations / tenants
- [ ] Build access-control matrix

## Authentication Boundary

- [ ] Remove session cookie
- [ ] Remove bearer token
- [ ] Test protected pages unauthenticated
- [ ] Test protected APIs unauthenticated

## Horizontal Access Control

- [ ] User A object read as User B
- [ ] User A object update as User B
- [ ] User A object delete as User B
- [ ] User A file download as User B
- [ ] User A metadata as User B
- [ ] Search results
- [ ] Export functionality

## Vertical Access Control

- [ ] Normal user against admin pages
- [ ] Normal user against admin APIs
- [ ] Administrative actions
- [ ] Role management
- [ ] Permission management
- [ ] User management
- [ ] Configuration
- [ ] Reporting
- [ ] Support functionality

## Object-Level Authorisation

- [ ] URL path IDs
- [ ] Query parameters
- [ ] POST parameters
- [ ] JSON properties
- [ ] XML properties
- [ ] Headers
- [ ] Cookies
- [ ] GraphQL variables
- [ ] WebSocket messages

## Function-Level Authorisation

- [ ] GET
- [ ] POST
- [ ] PUT
- [ ] PATCH
- [ ] DELETE
- [ ] Alternative methods
- [ ] Alternative endpoints
- [ ] Legacy APIs
- [ ] Mobile APIs

## Mass Assignment

- [ ] Role
- [ ] Permissions
- [ ] isAdmin
- [ ] Verified state
- [ ] Account status
- [ ] Organisation ID
- [ ] Tenant ID
- [ ] Ownership

## Multi-Tenant

- [ ] Cross-tenant object access
- [ ] Cross-tenant modification
- [ ] Cross-tenant deletion
- [ ] Tenant identifier manipulation
- [ ] Organisation invitations
- [ ] Tenant administration
- [ ] Nested object relationships

## API

- [ ] BOLA
- [ ] BFLA
- [ ] API versions
- [ ] Hidden endpoints
- [ ] OpenAPI documentation
- [ ] Administrative APIs
- [ ] Search endpoints
- [ ] Export endpoints

## GraphQL

- [ ] Query object authorisation
- [ ] Mutation authorisation
- [ ] Nested object authorisation
- [ ] Role restrictions
- [ ] Tenant restrictions

## WebSockets

- [ ] Message-level authorisation
- [ ] Object identifiers
- [ ] Channel subscriptions
- [ ] Tenant boundaries
- [ ] Privileged actions

## Workflow

- [ ] State transitions
- [ ] Approval workflow
- [ ] Ownership changes
- [ ] Archived objects
- [ ] Deleted objects
- [ ] Disabled objects

## Validation

- [ ] Verify resulting server-side state
- [ ] Do not rely solely on status codes
- [ ] Compare response bodies
- [ ] Check for information leakage
- [ ] Reproduce confirmed issues
- [ ] Record expected versus actual behaviour

---

# 90. Quick Reference

## Interesting Parameters

```text
id
userId
accountId
profileId
documentId
fileId
orderId
invoiceId
projectId
ownerId
organisationId
organizationId
tenantId
teamId
role
permissions
isAdmin
accessLevel
```

## Interesting Paths

```text
/admin
/api/admin
/manage
/management
/internal
/api/internal
/users
/accounts
/roles
/permissions
/settings
/reports
/export
```

## JavaScript Search

```bash
grep -RniE \
'admin|role|permission|isAdmin|authoriz|privilege|tenant|organisation|organization|ownerId|userId' \
javascript/
```

## Historical Endpoint Search

```bash
gau example.com |
grep -Ei \
'admin|manage|internal|api|user|account|role|permission'
```

## Two-Account Test

```text
1. Create object as User A

2. Capture User A request

3. Send request to Burp Repeater

4. Replace User A session with User B session

5. Keep User A object identifier

6. Send request

7. Compare expected and actual access

8. Verify server-side state
```

---

# 91. Authorisation Testing Mindset

Do not approach authorisation testing as:

```text
Change id=1 to id=2
        ↓
Done
```

Instead:

```text
Understand Identities
       ↓
Understand Roles
       ↓
Understand Objects
       ↓
Understand Ownership
       ↓
Understand Tenancy
       ↓
Understand Functions
       ↓
Build Access Matrix
       ↓
Test Every Relevant Boundary
       ↓
Validate Server-Side Enforcement
```

The key question for every sensitive request is:

> Is this specific identity authorised to perform this specific action against this specific object?

---

# 92. The Three Core Authorisation Questions

For every request, ask:

```text
WHO?
 ↓
Which authenticated identity is making the request?

WHAT?
 ↓
Which action is being performed?

ON WHAT?
 ↓
Which object or resource is being accessed?
```

Then evaluate:

```text
Identity
   +
Action
   +
Object
   +
Context
   =
Authorisation Decision
```

Context may include:

```text
Role
Ownership
Tenant
Object state
Relationship
Time
Authentication strength
```

---

# 93. Relationship With Other Testing

Authorisation connects directly to:

```text
Authentication
      │
      ↓
Who is the user?
      │
      ↓
Authorisation
      │
      ├── Object IDs
      │       ↓
      │   IDOR / BOLA
      │
      ├── Roles
      │       ↓
      │   Vertical Privilege Escalation
      │
      ├── Ownership
      │       ↓
      │   Horizontal Privilege Escalation
      │
      ├── API Operations
      │       ↓
      │   BFLA
      │
      ├── Tenant IDs
      │       ↓
      │   Multi-Tenant Isolation
      │
      ├── Object Properties
      │       ↓
      │   Mass Assignment
      │
      └── Workflow State
              ↓
          Business Logic
```

This is why authorisation testing should be performed throughout the assessment rather than as a single isolated test.

---

# 94. Practical Testing Principle

One of the most productive authorisation-testing habits is:

```text
Every time you perform an action,
ask whether another identity could perform it.
```

For example:

```text
View document
      ↓
Can User B view it?

Edit document
      ↓
Can User B edit it?

Delete document
      ↓
Can User B delete it?

Share document
      ↓
Can User B change sharing?

Move document
      ↓
Can User B change ownership?
```

Repeat this thinking across the application's important objects.

---

# 95. Final Methodology

A mature authorisation assessment should therefore look like:

```text
Reconnaissance
      ↓
Identify Roles
      ↓
Identify Objects
      ↓
Identify Functions
      ↓
Identify Tenants
      ↓
Build Access Matrix
      ↓
Capture Legitimate Requests
      ↓
Test Unauthenticated Access
      ↓
Test Horizontal Access
      ↓
Test Vertical Access
      ↓
Test Object-Level Access
      ↓
Test Function-Level Access
      ↓
Test Mass Assignment
      ↓
Test Tenant Isolation
      ↓
Test Alternative APIs
      ↓
Test Workflows
      ↓
Validate Results
      ↓
Document Evidence
```

Good authorisation testing is ultimately about identifying **trust boundaries** and systematically attempting to cross them using identities that should not be permitted to do so.

---

# References

Useful references for further study:

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)
- [PortSwigger Web Security Academy: Access Control](https://portswigger.net/web-security/access-control)
- [PortSwigger Web Security Academy: API Testing](https://portswigger.net/web-security/api-testing)

---

## Related Notes

Continue with:

- [Web Application Security Overview](index.md)
- [Web Application Testing Methodology](methodology.md)
- [Pentesting Checklist](checklist.md)
- [Authentication](authentication.md)
- [Session Management](session-management.md)
- [Business Logic](business-logic.md)
- [API Security](api-security.md)
