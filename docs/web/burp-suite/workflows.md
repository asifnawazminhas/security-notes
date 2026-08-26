# Burp Suite Testing Workflows

Burp Suite is most effective when used as part of a structured testing methodology rather than simply intercepting requests and trying random payloads.

This page provides practical Burp Suite workflows for common web application security testing activities.

The objective is to move systematically from:

```text
Application Mapping
        ↓
Request Identification
        ↓
Manual Analysis
        ↓
Controlled Manipulation
        ↓
Response Comparison
        ↓
Vulnerability Validation
        ↓
Evidence Collection
```

!!! warning "Authorised Security Testing"
    Perform these techniques only against applications and systems for which you have explicit authorisation. Use dedicated test accounts and test data where possible.

---

# 1. General Burp Suite Workflow

A useful general workflow for a web application assessment is:

```text
Configure Target Scope
        ↓
Browse Application
        ↓
Proxy / HTTP History
        ↓
Build Application Map
        ↓
Identify Interesting Requests
        ↓
Send to Repeater
        ↓
Establish Baseline
        ↓
Modify One Element
        ↓
Compare Response
        ↓
Investigate Interesting Behaviour
        ↓
Use Specialised Tools / Extensions
        ↓
Manually Verify
        ↓
Capture Evidence
        ↓
Report
```

The most important principle is:

> Understand the normal request before modifying it.

Without a baseline, it becomes difficult to determine whether a modification actually changed application behaviour.

---

# 2. Initial Burp Setup

Before testing, configure the target scope.

Navigate to:

```text
Target
    ↓
Scope
```

Add the authorised target.

For example:

```text
https://app.example.test
```

Where appropriate, include authorised subdomains:

```text
*.example.test
```

Do not automatically assume every related domain is within scope.

---

# 3. Use Scope Aggressively

Once the target has been configured, use:

```text
Show only in-scope items
```

where appropriate.

This makes large assessments considerably easier to manage.

Instead of seeing:

```text
Google Analytics
CDNs
Fonts
Advertising
Third-party APIs
Target Application
```

you primarily see:

```text
Target Application
```

---

# 4. Browser Mapping Workflow

Start by using the application normally.

Visit:

```text
Home
Login
Registration
Profile
Account
Search
Upload
Download
Settings
API functionality
Administrative functionality
```

Use every feature available to your authorised account.

While doing this, Burp builds an HTTP history.

```text
Browser
   ↓
Burp Proxy
   ↓
HTTP History
   ↓
Application Map
```

Do not immediately start injecting payloads.

First understand the application.

---

# 5. HTTP History Review

After browsing the application, review:

```text
Proxy
    ↓
HTTP history
```

Look for interesting requests containing:

```text
id
user
account
role
admin
file
filename
path
url
uri
redirect
return
callback
search
query
token
session
password
email
upload
download
export
import
template
debug
api
```

Also pay attention to:

```text
POST
PUT
PATCH
DELETE
```

These often represent state-changing functionality.

---

# 6. Request Triage

A useful approach is to classify interesting requests.

```text
Authentication
Authorisation
Session
Input
File
URL
API
Administrative
Business Logic
```

Example:

```http
GET /api/users/123 HTTP/1.1
```

Classification:

```text
API
Object Identifier
Authorisation
Potential IDOR / BOLA
```

Another example:

```http
POST /api/fetch HTTP/1.1

url=https://example.test
```

Classification:

```text
URL Input
Server-Side Processing
Potential SSRF
```

This helps determine the appropriate testing workflow.

---

# 7. Repeater First

For manual testing, Repeater should normally be the first destination for an interesting request.

```text
HTTP History
      ↓
Right Click
      ↓
Send to Repeater
```

Shortcut:

```text
Ctrl + R
```

Then:

```text
Repeater
   ↓
Send Original Request
   ↓
Record Baseline
   ↓
Modify One Variable
   ↓
Send Again
   ↓
Compare
```

---

# 8. Establish a Baseline

Before changing anything, send the original request.

Record:

```text
Status code
Response length
Response body
Headers
Redirects
Response time
Application state
```

Example:

```text
200 OK
Length: 4281
```

Then modify one element.

This makes response differences easier to understand.

---

# 9. Modify One Thing at a Time

Avoid changing:

```text
Cookie
Parameter
HTTP method
Header
Object ID
Payload
```

all at once.

Instead:

```text
Baseline
   ↓
Change Parameter
   ↓
Observe
   ↓
Restore
   ↓
Change Header
   ↓
Observe
```

This makes it much easier to determine which modification caused the behaviour.

---

# 10. Authentication Testing Workflow

Start by capturing the login request.

```text
Browser
   ↓
Login
   ↓
Proxy
   ↓
Capture Request
   ↓
Send to Repeater
```

Example:

```http
POST /login HTTP/1.1
Host: example.test
Content-Type: application/x-www-form-urlencoded

username=testuser&password=Password123!
```

---

## Authentication Workflow

```text
Capture Login
     ↓
Identify Credentials
     ↓
Identify Additional Parameters
     ↓
Send to Repeater
     ↓
Establish Valid Login Baseline
     ↓
Test Invalid Credentials
     ↓
Observe Error Behaviour
     ↓
Test Authentication Logic
     ↓
Inspect Session Creation
     ↓
Test MFA if Present
     ↓
Test Password Reset
     ↓
Test Account Recovery
```

---

# 11. Authentication Response Comparison

Compare:

```text
Valid Username + Valid Password
Invalid Username + Valid Password
Valid Username + Invalid Password
Invalid Username + Invalid Password
```

Look for differences in:

```text
Response message
Status
Response length
Redirect
Response time
Headers
Cookies
```

Potential username enumeration may appear as:

```text
Unknown username
```

versus:

```text
Incorrect password
```

or through more subtle response differences.

---

# 12. Authentication Cookies

After successful authentication, inspect:

```http
Set-Cookie:
```

Record:

```text
Session cookie
Secure
HttpOnly
SameSite
Domain
Path
Expiration
```

Then compare the session before and after authentication.

```text
Unauthenticated Session
        ↓
Login
        ↓
Authenticated Session
```

Determine whether the relevant session identifier changes.

---

# 13. MFA Workflow

If MFA exists:

```text
Username + Password
        ↓
MFA Challenge
        ↓
Authenticated Session
```

Capture requests around the transition.

Look for:

```text
Session changes
MFA state parameters
Verification endpoints
Recovery functionality
Remember-device functionality
Alternative authentication paths
```

The key question is:

> Does the server independently verify that MFA was completed before granting access to protected functionality?

---

# 14. Password Reset Workflow

Map the complete password reset process:

```text
Request Reset
     ↓
Reset Token Generated
     ↓
Token Delivered
     ↓
Token Validated
     ↓
New Password
     ↓
Existing Session Behaviour
```

Capture each request.

Review:

```text
Token location
Token lifetime
Token reuse
Session invalidation
Account identification
Host handling
Redirect behaviour
```

---

# 15. Authorisation Testing Workflow

Authorisation testing works particularly well with two test accounts.

Use:

```text
User A
User B
```

Preferably also:

```text
Administrator
```

---

## Horizontal Authorisation

Create or identify an object belonging to User A.

Example:

```text
User A document ID:

1001
```

Capture:

```http
GET /api/documents/1001 HTTP/1.1
Cookie: session=USER_A
```

Send to Repeater.

Now replace only:

```text
USER_A
```

with:

```text
USER_B
```

Keep:

```text
/document/1001
```

unchanged.

---

## Horizontal Workflow

```text
User A
   ↓
Access User A Object
   ↓
Capture Request
   ↓
Repeater
   ↓
Replace Session with User B
   ↓
Keep User A Object ID
   ↓
Send
   ↓
Compare
```

Expected:

```text
Access denied
```

If User B receives User A's object, investigate for IDOR / BOLA.

---

# 16. Autorize Workflow

Autorize can automate much of this comparison.

```text
Low-Privilege User
       ↓
Capture Session
       ↓
Configure Autorize
       ↓
Browse as Privileged User
       ↓
Autorize Replays Requests
       ↓
Compare Responses
       ↓
Potential Findings
       ↓
Repeater
       ↓
Manual Verification
```

A practical example:

```text
Administrator
     ↓
GET /admin/users
     ↓
Autorize
     ↓
Replay with USER session
```

If the normal user's response appears equivalent, investigate manually.

!!! tip
    Never report an Autorize result solely because it is highlighted. Send the request to Repeater and verify the actual access and resulting application state.

---

# 17. Vertical Privilege Escalation Workflow

Use an administrator account to perform an administrative operation.

Example:

```http
DELETE /api/admin/users/123 HTTP/1.1
Cookie: session=ADMIN
```

Capture the request.

Replace:

```text
ADMIN
```

with:

```text
NORMAL_USER
```

Then replay.

```text
Administrator
      ↓
Perform Admin Function
      ↓
Capture Request
      ↓
Repeater
      ↓
Replace Admin Session
      ↓
Normal User Session
      ↓
Replay
      ↓
Verify Result
```

This is generally more reliable than simply guessing `/admin` endpoints.

---

# 18. AuthMatrix Workflow

For applications with multiple roles:

```text
Admin
Manager
Employee
Customer
Anonymous
```

build an access matrix.

Example:

| Function | Admin | Manager | User | Anonymous |
|---|---:|---:|---:|---:|
| Profile | ✓ | ✓ | ✓ | ✗ |
| Reports | ✓ | ✓ | ✗ | ✗ |
| User Management | ✓ | ✗ | ✗ | ✗ |
| Configuration | ✓ | ✗ | ✗ | ✗ |

Then test requests across the different identities.

```text
Capture Requests
       ↓
Define Roles
       ↓
Define Expected Permissions
       ↓
Run Matrix
       ↓
Review Differences
       ↓
Manual Verification
```

---

# 19. IDOR / BOLA Workflow

Look for identifiers in:

```text
URL paths
Query parameters
JSON
POST bodies
GraphQL variables
Headers
Cookies
WebSocket messages
```

Example:

```http
GET /api/orders/7312 HTTP/1.1
```

Ask:

```text
Who owns order 7312?
```

Then test with another authorised test identity.

---

## Practical IDOR Flow

```text
Find Object ID
      ↓
Determine Owner
      ↓
Capture Valid Request
      ↓
Repeater
      ↓
Switch Identity
      ↓
Keep Object ID
      ↓
Replay
      ↓
Test READ
      ↓
Test UPDATE
      ↓
Test DELETE
      ↓
Verify
```

Do not stop after testing `GET`.

An application might prevent:

```text
GET
```

while incorrectly allowing:

```text
PATCH
DELETE
```

---

# 20. Session Management Workflow

Capture an authenticated request.

Example:

```http
GET /account HTTP/1.1
Cookie: session=ABC123
```

Send it to Repeater.

---

## Session Workflow

```text
Login
  ↓
Capture Session
  ↓
Inspect Cookie
  ↓
Record Session Value
  ↓
Test Rotation
  ↓
Test Logout
  ↓
Replay Old Session
  ↓
Test Password Change
  ↓
Replay Old Session
  ↓
Test Expiration
  ↓
Test Revocation
```

---

# 21. Logout Testing

Procedure:

```text
1. Login
2. Capture authenticated request
3. Send to Repeater
4. Confirm request works
5. Logout normally
6. Return to Repeater
7. Replay original request
```

Expected:

```text
Session rejected
```

Potential issue:

```text
Old session remains authenticated
```

Do not rely only on the browser cookie disappearing.

Verify server-side invalidation.

---

# 22. Session Fixation Workflow

Record the session before login:

```text
session=AAA
```

Authenticate.

Record it again:

```text
session=BBB
```

Compare:

```text
AAA
vs
BBB
```

Workflow:

```text
Unauthenticated Session
        ↓
Record Token
        ↓
Authenticate
        ↓
Record Token
        ↓
Compare
```

A relevant session identifier should normally rotate when authentication state changes.

---

# 23. Sequencer Workflow

For tokens that should be unpredictable:

```text
Identify Token
     ↓
Send Response to Sequencer
     ↓
Configure Token Location
     ↓
Capture Multiple Tokens
     ↓
Analyse Randomness
     ↓
Investigate Patterns
```

Useful targets include:

```text
Session identifiers
CSRF tokens
Password reset tokens
Other security-sensitive random values
```

---

# 24. Parameter Testing Workflow

When you identify a parameter:

```text
?id=123
```

do not immediately throw every payload at it.

First determine its purpose.

```text
Parameter
    ↓
Change Value
    ↓
Observe Response
    ↓
Determine Data Type
    ↓
Determine Processing Context
    ↓
Choose Relevant Tests
```

---

# 25. Parameter Classification

A useful mental model:

```text
id=
   ↓
Object Reference
   ↓
IDOR / BOLA

url=
   ↓
URL Processing
   ↓
SSRF / Redirect

file=
   ↓
Filesystem
   ↓
Path Traversal / File Handling

search=
   ↓
Application Input
   ↓
XSS / Injection

template=
   ↓
Template Processing
   ↓
SSTI

redirect=
   ↓
Navigation
   ↓
Open Redirect
```

Context should determine the test.

---

# 26. Hidden Parameter Discovery

Param Miner can assist with discovering hidden inputs.

Workflow:

```text
Interesting Request
       ↓
Param Miner
       ↓
Guess Parameters
       ↓
Guess Headers
       ↓
Observe Response Changes
       ↓
Interesting Candidate
       ↓
Repeater
       ↓
Manual Investigation
```

Useful areas include:

```text
Hidden parameters
Debug functionality
Cache behaviour
Proxy headers
Routing headers
Undocumented features
```

---

# 27. XSS Testing Workflow

For XSS testing, first identify where input appears in the response.

```text
Input
  ↓
Submit Unique Marker
  ↓
Find Marker in Response
  ↓
Determine Context
  ↓
Test Context Escape
  ↓
Determine Encoding
  ↓
Validate Execution Safely
```

Use a unique marker first:

```text
XSSMARKER123
```

Then search the response.

---

## XSS Context Identification

Determine whether the marker appears in:

```html
<div>XSSMARKER123</div>
```

or:

```html
<input value="XSSMARKER123">
```

or:

```html
<script>
var search = "XSSMARKER123";
</script>
```

or:

```javascript
const data = {
    value: "XSSMARKER123"
};
```

The context determines the appropriate testing strategy.

---

# 28. XSS Burp Workflow

```text
Proxy
  ↓
Identify User Input
  ↓
Repeater
  ↓
Submit Unique Marker
  ↓
Locate Reflection
  ↓
Determine Context
  ↓
Test Encoding
  ↓
Test Context-Specific Input
  ↓
Browser Validation
  ↓
Capture Evidence
```

Useful Burp components include:

```text
Proxy
Repeater
Intruder
DOM Invader
Scanner
```

The dedicated XSS notes should contain the detailed testing methodology.

---

# 29. SQL Injection Workflow

Start with an input that appears to influence server-side data processing.

```text
Parameter
   ↓
Baseline Request
   ↓
Controlled Input Changes
   ↓
Observe Errors / Behaviour
   ↓
Compare Responses
   ↓
Investigate Database Interaction
```

Useful indicators can include:

```text
Database errors
Boolean response differences
Unexpected query behaviour
Timing differences
```

---

## SQL Injection Burp Flow

```text
Proxy
  ↓
Interesting Parameter
  ↓
Repeater
  ↓
Baseline
  ↓
Controlled Test Input
  ↓
Compare Response
  ↓
Investigate Behaviour
  ↓
Scanner where authorised
  ↓
Manual Verification
```

Detailed SQL injection techniques belong in the dedicated SQL Injection page.

---

# 30. Command Injection Workflow

Identify parameters that may be passed to operating-system commands.

Common candidates include functionality involving:

```text
Ping
DNS lookup
Network diagnostics
File conversion
Image processing
Backup
Archive handling
System utilities
```

Workflow:

```text
Identify Function
      ↓
Understand Expected Input
      ↓
Repeater
      ↓
Establish Baseline
      ↓
Controlled Input Modification
      ↓
Observe Behaviour
      ↓
Investigate Server-Side Processing
      ↓
Validate Safely
```

Use non-destructive validation methods during authorised testing.

---

# 31. SSRF Workflow

Look for parameters that accept URLs or network locations.

Examples:

```text
url
uri
endpoint
callback
webhook
image
avatar
feed
proxy
destination
redirect
```

Example:

```http
POST /api/fetch HTTP/1.1
Content-Type: application/json

{
  "url": "https://example.test"
}
```

---

## SSRF Flow

```text
Identify URL Input
      ↓
Repeater
      ↓
Baseline External URL
      ↓
Determine Server-Side Fetching
      ↓
Test Controlled Destination
      ↓
Observe Response
      ↓
Use Collaborator if Appropriate
      ↓
Investigate Restrictions
      ↓
Manual Verification
```

---

# 32. Burp Collaborator Workflow

For functionality that may perform server-side network interactions:

```text
Generate Collaborator Address
        ↓
Insert into Controlled Input
        ↓
Send Request
        ↓
Poll Collaborator
        ↓
DNS Interaction?
        ↓
HTTP Interaction?
        ↓
Investigate
```

Possible applications include:

```text
SSRF
Blind XXE
Blind injection
Webhook processing
Backend URL validation
Asynchronous processing
```

An interaction proves that some component reached the Collaborator infrastructure, but you should still determine which input and application component caused it.

---

# 33. Collaborator Everywhere Workflow

```text
Enable Extension
       ↓
Browse Application
       ↓
Extension Injects Collaborator References
       ↓
Application Processes Traffic
       ↓
Monitor Collaborator
       ↓
Identify Interactions
       ↓
Trace Back to Request
       ↓
Repeater
       ↓
Manual Verification
```

This can help discover server-side behaviour that was not obvious from application responses.

---

# 34. File Upload Workflow

File upload functionality requires multiple layers of testing.

First determine:

```text
Allowed extensions
MIME validation
Content validation
Filename handling
Storage location
File retrieval
Processing behaviour
Access control
```

---

## Burp File Upload Flow

```text
Upload Normal File
       ↓
Capture Request
       ↓
Repeater
       ↓
Understand Multipart Structure
       ↓
Modify Filename
       ↓
Modify Content-Type
       ↓
Modify File Content
       ↓
Observe Validation
       ↓
Determine Storage / Processing
       ↓
Retrieve File
       ↓
Test Access Control
```

Example multipart structure:

```http
Content-Disposition: form-data; name="file"; filename="test.pdf"
Content-Type: application/pdf
```

Do not assume validation is based solely on:

```text
filename
```

or:

```text
Content-Type
```

Determine what the server actually validates.

---

# 35. File Download Workflow

Download endpoints frequently expose:

```text
IDOR
Path traversal
Information disclosure
Missing authorisation
```

Example:

```http
GET /download?id=123 HTTP/1.1
```

Workflow:

```text
Capture Download
      ↓
Identify File Reference
      ↓
Repeater
      ↓
Test Ownership
      ↓
Test Identifier Changes
      ↓
Test Path Handling if Relevant
      ↓
Verify Access Controls
```

---

# 36. Path Traversal Workflow

Look for parameters that appear to reference files or paths.

Examples:

```text
file
filename
path
document
template
page
download
```

Workflow:

```text
Identify File Parameter
       ↓
Baseline Valid File
       ↓
Repeater
       ↓
Modify Path
       ↓
Observe Normalisation
       ↓
Observe Errors
       ↓
Determine Filesystem Interaction
       ↓
Validate Safely
```

Detailed traversal techniques belong in the dedicated Path Traversal page.

---

# 37. XXE Workflow

Identify functionality processing XML.

Look for:

```http
Content-Type: application/xml
```

or:

```http
Content-Type: text/xml
```

or XML-based file formats and integrations.

Workflow:

```text
Identify XML Processing
      ↓
Capture Valid XML
      ↓
Repeater
      ↓
Understand Parser Behaviour
      ↓
Controlled XML Modification
      ↓
Observe Response
      ↓
Collaborator if Appropriate
      ↓
Manual Verification
```

---

# 38. SSTI Workflow

Template injection testing begins by identifying input rendered by a server-side template engine.

```text
Input
  ↓
Rendered Output
  ↓
Determine Transformation
  ↓
Identify Possible Template Context
  ↓
Controlled Expression Testing
  ↓
Fingerprint Engine
  ↓
Assess Impact
```

Burp workflow:

```text
Proxy
  ↓
Find Reflected Input
  ↓
Repeater
  ↓
Baseline
  ↓
Controlled Template Expression
  ↓
Compare Output
  ↓
Investigate
```

---

# 39. Open Redirect Workflow

Look for parameters such as:

```text
redirect
redirect_uri
return
returnUrl
next
continue
url
destination
callback
```

Example:

```text
/login?returnUrl=/dashboard
```

Workflow:

```text
Identify Redirect Parameter
       ↓
Baseline Internal Redirect
       ↓
Repeater
       ↓
Controlled External Destination
       ↓
Observe Location Header
       ↓
Browser Validation
       ↓
Determine Security Impact
```

---

# 40. API Testing Workflow

Modern applications frequently expose significant functionality through APIs.

Start by mapping:

```text
Endpoints
Methods
Authentication
Object identifiers
Content types
Roles
Versions
```

---

## API Flow

```text
Browse Application
      ↓
HTTP History
      ↓
Filter API Requests
      ↓
Map Endpoints
      ↓
Identify Objects
      ↓
Identify Methods
      ↓
Repeater
      ↓
Test Authentication
      ↓
Test Authorisation
      ↓
Test Input Validation
      ↓
Test Business Logic
```

---

# 41. API Endpoint Classification

Classify endpoints:

```text
/api/users
    ↓
User Management

/api/orders
    ↓
Business Objects

/api/admin
    ↓
Administrative

/api/files
    ↓
File Handling

/api/search
    ↓
Input Processing

/api/export
    ↓
Data Export
```

This makes testing more systematic.

---

# 42. API Method Testing

For relevant endpoints, determine supported methods:

```text
GET
POST
PUT
PATCH
DELETE
```

Do not assume security controls are identical across methods.

Example:

```text
GET /api/user/123
```

may be protected while:

```text
PATCH /api/user/123
```

uses different authorisation logic.

---

# 43. API Version Testing

Look for:

```text
/api/v1/
/api/v2/
/api/v3/
```

Compare equivalent functionality across versions.

```text
Current API
    ↓
Strong Controls

Legacy API
    ↓
Different Controls?
```

JavaScript and historical endpoints may reveal older versions.

---

# 44. GraphQL Workflow

Identify the GraphQL endpoint.

Common examples:

```text
/graphql
/api/graphql
/graphql/api
```

Map:

```text
Queries
Mutations
Objects
Arguments
Authentication
Authorisation
```

---

## GraphQL Flow

```text
Identify GraphQL Endpoint
       ↓
Capture Valid Query
       ↓
Repeater
       ↓
Understand Query Structure
       ↓
Identify Object IDs
       ↓
Test Authorisation
       ↓
Test Mutations
       ↓
Test Nested Objects
       ↓
Validate Results
```

---

# 45. WebSocket Workflow

Burp can capture WebSocket traffic.

Review:

```text
Proxy
    ↓
WebSockets history
```

Look for messages containing:

```text
userId
messageId
channel
room
organisation
role
action
```

---

## WebSocket Flow

```text
Establish Connection
       ↓
Capture Messages
       ↓
Understand Message Format
       ↓
Identify Object IDs
       ↓
Identify Actions
       ↓
Modify Controlled Fields
       ↓
Test Authorisation
       ↓
Observe Responses
```

---

# 46. Business Logic Workflow

Business logic vulnerabilities often require understanding the application's intended workflow.

Start with:

```text
What is supposed to happen?
```

Then:

```text
Can the workflow be performed differently?
```

---

## Example

Normal:

```text
Create Order
    ↓
Payment
    ↓
Confirmation
    ↓
Delivery
```

Testing questions:

```text
Can steps be skipped?
Can steps be repeated?
Can steps be performed out of order?
Can values change between steps?
Can another user perform a step?
Can an expired step still be used?
```

---

# 47. Business Logic Burp Flow

```text
Perform Normal Workflow
       ↓
Capture Every Request
       ↓
Send Important Requests to Repeater
       ↓
Understand State Transitions
       ↓
Replay Requests
       ↓
Change Order
       ↓
Change Values
       ↓
Skip Steps
       ↓
Repeat Steps
       ↓
Observe Server-Side Enforcement
```

This is an area where manual testing is particularly important.

---

# 48. Race Condition Workflow

Identify functionality where multiple requests occurring close together could create inconsistent state.

Examples include:

```text
Coupon redemption
Invitation acceptance
Balance operations
One-time actions
Limit enforcement
Account creation
Resource allocation
```

Start with Burp Repeater's parallel request functionality where appropriate.

Conceptually:

```text
Single Request
      ↓
Expected State Change
      ↓
Send Multiple Controlled Requests
      ↓
Observe Whether Constraint Holds
```

Turbo Intruder can be useful for more specialised testing.

!!! warning
    Race-condition testing can create multiple transactions or state changes. Use dedicated test data and stay within agreed rate and impact limits.

---

# 49. HTTP Request Smuggling Workflow

Request smuggling testing should begin by understanding the architecture.

```text
Client
  ↓
CDN
  ↓
Reverse Proxy
  ↓
Load Balancer
  ↓
Application
```

Potential parsing differences between systems can create request desynchronisation.

Workflow:

```text
Identify Suitable Endpoint
       ↓
HTTP Request Smuggler
       ↓
Run Controlled Checks
       ↓
Observe Timing / Response Behaviour
       ↓
Investigate Anomalies
       ↓
Manual Verification
```

!!! warning
    Request smuggling testing can interfere with shared backend connections. Use conservative testing and follow the agreed rules of engagement.

---

# 50. Cache Testing Workflow

Start by identifying cacheable responses.

Inspect:

```text
Cache-Control
Age
Vary
ETag
CDN headers
X-Cache
```

Workflow:

```text
Baseline Request
      ↓
Determine Cache Behaviour
      ↓
Identify Unkeyed Input Candidates
      ↓
Param Miner
      ↓
Controlled Modification
      ↓
Repeat Request
      ↓
Observe Cache Behaviour
      ↓
Verify Carefully
```

Avoid poisoning shared production caches with harmful or persistent content.

---

# 51. JavaScript Analysis Workflow

Burp HTTP history can help identify JavaScript files.

Filter for:

```text
JS
```

Then search downloaded JavaScript for:

```text
/api/
/admin/
/internal/
token
secret
apikey
password
debug
upload
download
graphql
websocket
```

Workflow:

```text
Browse Application
      ↓
Capture JavaScript
      ↓
Identify Interesting Files
      ↓
Search for Routes
      ↓
Search for Parameters
      ↓
Search for Secrets / Config
      ↓
Add Endpoints to Testing Map
      ↓
Test Through Repeater
```

---

# 52. Response Comparison Workflow

Many vulnerabilities become visible only through subtle response differences.

Compare:

```text
Valid vs Invalid
User A vs User B
Admin vs User
Authenticated vs Anonymous
Normal Input vs Modified Input
Existing Object vs Missing Object
```

Use:

```text
Comparer
```

or manually compare:

```text
Status
Length
Headers
Body
Timing
Side effects
```

---

# 53. Intruder Workflow

Intruder is useful when one controlled request needs to be repeated with multiple input values.

```text
Repeater
   ↓
Request Understood
   ↓
Send to Intruder
   ↓
Select Payload Position
   ↓
Configure Payloads
   ↓
Run Controlled Test
   ↓
Sort Responses
   ↓
Identify Outliers
   ↓
Repeater
   ↓
Manual Verification
```

The important step is:

```text
Intruder result
      ↓
Repeater
      ↓
Manual verification
```

---

# 54. Intruder Response Analysis

Useful columns include:

```text
Status
Length
Words
Lines
Time
```

Look for outliers.

Example:

| Payload | Status | Length |
|---|---:|---:|
| test1 | 403 | 421 |
| test2 | 403 | 421 |
| test3 | 200 | 4832 |
| test4 | 403 | 421 |

The interesting result is:

```text
test3
```

Send it to Repeater and determine why it differs.

---

# 55. Decoder Workflow

Use Decoder when values appear encoded.

Examples:

```text
Base64
URL encoding
Hex
HTML entities
```

Workflow:

```text
Interesting Value
      ↓
Decoder
      ↓
Decode
      ↓
Understand Structure
      ↓
Modify if Relevant
      ↓
Encode
      ↓
Repeater
      ↓
Test
```

Encoding is not encryption.

---

# 56. Logger++ Workflow

For large assessments:

```text
Proxy Traffic
      ↓
Logger++
      ↓
Filter
      ↓
Search
      ↓
Interesting Request
      ↓
Repeater
```

Useful search terms:

```text
admin
token
password
secret
debug
internal
upload
download
redirect
callback
api
graphql
role
permission
```

---

# 57. Scanner Workflow

Where Burp Scanner is available and authorised:

```text
Map Application
      ↓
Understand Functionality
      ↓
Select Appropriate Targets
      ↓
Run Scanner
      ↓
Review Findings
      ↓
Send Request to Repeater
      ↓
Manual Verification
      ↓
Determine Impact
```

Do not treat scanner output as automatically confirmed.

---

# 58. Evidence Collection Workflow

Once a vulnerability has been confirmed:

```text
Clean Reproduction
       ↓
Baseline Request
       ↓
Modified Request
       ↓
Relevant Response
       ↓
Verify Impact
       ↓
Capture Evidence
       ↓
Record Steps
```

Keep evidence minimal and clear.

---

# 59. Repeater Tabs

Use descriptive Repeater tab names.

Instead of:

```text
Tab 1
Tab 2
Tab 3
Tab 4
```

use:

```text
AUTH Login
AUTH Reset
IDOR Documents
ADMIN Users
UPLOAD PDF
SSRF Webhook
API Orders
```

This becomes extremely useful during larger assessments.

---

# 60. Request Naming Strategy

A practical naming convention:

```text
[CATEGORY] Function
```

Examples:

```text
[AUTH] Login
[AUTH] Password Reset
[AUTHZ] User Profile
[IDOR] Download Invoice
[API] Update Account
[UPLOAD] Document
[SSRF] Webhook
[XSS] Search
[SQLI] Product ID
```

---

# 61. Burp Notes Strategy

For each interesting request, record:

```text
What does this request do?
Which account was used?
Which object does it affect?
Which parameters are interesting?
What tests have already been performed?
What remains to be tested?
```

This prevents duplicated work.

---

# 62. Practical Testing Decision Tree

When you encounter an input:

```text
                    INPUT
                      │
          ┌───────────┼───────────┐
          │           │           │
       Object        URL        File/Path
          │           │           │
      IDOR/BOLA     SSRF       Traversal
          │        Redirect      Upload
          │
          ├───────────────┐
          │               │
        Text            Template
          │               │
     XSS / SQLi          SSTI
          │
          └───────────────┐
                          │
                         XML
                          │
                         XXE
```

The parameter name alone is not proof of the backend processing context.

Use application behaviour to determine the appropriate test.

---

# 63. Practical Endpoint Decision Tree

When you discover an endpoint:

```text
Endpoint
   ↓
Does it require authentication?
   ↓
Should this user access it?
   ↓
Does it reference an object?
   ↓
Who owns the object?
   ↓
Does it accept input?
   ↓
Where does the input go?
   ↓
Does it change application state?
   ↓
Can the workflow be manipulated?
```

This single process identifies a large amount of potential attack surface.

---

# 64. Recommended Workflow by Vulnerability

| Testing Area | Burp Components |
|---|---|
| Authentication | Proxy, Repeater, Intruder, Comparer |
| Authorisation | Repeater, Comparer, Autorize, AuthMatrix |
| Session Management | Repeater, Sequencer, Decoder |
| IDOR / BOLA | Repeater, Autorize, Comparer |
| XSS | Repeater, DOM Invader, Intruder |
| SQL Injection | Repeater, Scanner, Intruder |
| SSRF | Repeater, Collaborator |
| File Upload | Proxy, Repeater |
| Path Traversal | Repeater, Intruder |
| XXE | Repeater, Collaborator |
| SSTI | Repeater |
| Open Redirect | Repeater |
| API Security | Proxy, Repeater, Autorize |
| GraphQL | Proxy, Repeater |
| WebSockets | WebSockets History |
| Race Conditions | Repeater, Turbo Intruder |
| Request Smuggling | HTTP Request Smuggler |
| Cache Testing | Repeater, Param Miner |
| JWT | Repeater, JWT Editor |
| Hidden Parameters | Param Miner |
| Response Analysis | Comparer, Logger++ |

---

# 65. Recommended Assessment Workflow

A complete practical assessment might look like:

```text
                    TARGET
                      ↓
                 Configure Scope
                      ↓
               Browse Application
                      ↓
                  Proxy History
                      ↓
                Application Map
                      ↓
        ┌─────────────┼─────────────┐
        │             │             │
 Authentication  Authorisation    Inputs
        │             │             │
        ↓             ↓             ↓
   Sessions       IDOR/BOLA      Injection
        │             │             │
        └─────────────┼─────────────┘
                      ↓
                     API
                      ↓
                Business Logic
                      ↓
                Special Cases
                      ↓
       ┌──────────────┼──────────────┐
       │              │              │
   WebSockets      Caching        HTTP
       │              │              │
       └──────────────┼──────────────┘
                      ↓
               Manual Verification
                      ↓
                    Evidence
                      ↓
                    Report
```

---

# 66. Daily Burp Workflow

For a practical assessment, a simple repeatable process is:

```text
1. Browse
2. Capture
3. Understand
4. Classify
5. Repeater
6. Establish baseline
7. Modify
8. Compare
9. Automate where useful
10. Verify manually
11. Record evidence
12. Continue mapping
```

Do not separate reconnaissance and vulnerability testing too rigidly.

During testing you will continuously discover:

```text
New endpoints
New parameters
New roles
New APIs
New objects
New workflows
```

Add them back into the application map.

---

# 67. Testing Loop

A useful mental model is:

```text
DISCOVER
   ↓
UNDERSTAND
   ↓
TEST
   ↓
COMPARE
   ↓
VERIFY
   ↓
DOCUMENT
   ↓
DISCOVER MORE
   ↺
```

Web application penetration testing is iterative.

A new API endpoint discovered during authorisation testing may expose another parameter, which may lead to another vulnerability class.

---

# 68. What Not to Do

Avoid approaching Burp as:

```text
Intercept Request
      ↓
Insert Random Payload
      ↓
Nothing Happens
      ↓
Move On
```

Instead:

```text
Understand Request
      ↓
Understand Input
      ↓
Understand Trust Boundary
      ↓
Choose Relevant Test
      ↓
Modify Carefully
      ↓
Compare Behaviour
      ↓
Verify
```

---

# 69. Automation vs Manual Testing

Automation is useful for:

```text
Repetition
Discovery
Large input sets
Response comparison
Known vulnerability patterns
```

Manual testing is particularly important for:

```text
Business logic
Authorisation
Authentication
Workflow manipulation
Complex application state
Chained vulnerabilities
Impact validation
```

The strongest methodology combines both.

```text
Manual Understanding
        +
Targeted Automation
        +
Manual Verification
        =
Effective Testing
```

---

# 70. Final Burp Methodology

A mature Burp Suite workflow should therefore resemble:

```text
Scope
  ↓
Proxy
  ↓
Map
  ↓
Understand
  ↓
Classify
  ↓
Repeater
  ↓
Baseline
  ↓
Controlled Modification
  ↓
Compare
  ↓
Extension / Intruder / Scanner
  ↓
Manual Verification
  ↓
Impact Analysis
  ↓
Evidence
  ↓
Reporting
```

The objective is not to use every Burp feature or extension.

The objective is to understand the application well enough to select the correct tool and test for each trust boundary.

---

# Quick Reference

## Interesting Request

```text
HTTP History
    ↓
Send to Repeater
    ↓
Baseline
    ↓
Modify One Element
    ↓
Compare
```

## Access Control

```text
Account A
    ↓
Capture Request
    ↓
Account B Session
    ↓
Replay
    ↓
Compare
```

## Session

```text
Capture Session
    ↓
Logout
    ↓
Replay
    ↓
Password Change
    ↓
Replay
```

## Input

```text
Unique Marker
    ↓
Find Reflection / Processing
    ↓
Determine Context
    ↓
Select Relevant Test
```

## API

```text
Endpoint
    ↓
Method
    ↓
Authentication
    ↓
Authorisation
    ↓
Objects
    ↓
Input
    ↓
Business Logic
```

## Finding

```text
Potential Issue
    ↓
Repeater
    ↓
Reproduce
    ↓
Verify Impact
    ↓
Evidence
    ↓
Report
```

---

## Related Notes

- [Web Application Security](../index.md)
- [Web Application Testing Methodology](../methodology.md)
- [Pentesting Checklist](../checklist.md)
- [Authentication](../authentication.md)
- [Authorisation](../authorisation.md)
- [Session Management](../session-management.md)
- [Burp Suite Extensions](extensions.md)
