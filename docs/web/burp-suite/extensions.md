# Burp Suite Extensions

Burp Suite extensions can significantly improve the efficiency of web application security testing by automating repetitive tasks, highlighting suspicious behaviour and providing specialised testing capabilities.

This page contains a practical collection of Burp Suite extensions that are useful during authorised web application penetration testing and vulnerability research.

!!! warning "Authorised Security Testing"
    Use these extensions only against systems for which you have explicit permission to perform security testing.

---

## Extension Overview

| Extension | Primary Use |
|---|---|
| Autorize | Authorisation and access control testing |
| AuthMatrix | Role and permission testing |
| JWT Editor | JSON Web Token testing |
| Param Miner | Hidden parameter and header discovery |
| Logger++ | Advanced HTTP logging |
| HTTP Request Smuggler | HTTP request smuggling testing |
| Backslash Powered Scanner | Unusual server-side behaviour discovery |
| Turbo Intruder | High-performance request automation |
| Collaborator Everywhere | Out-of-band interaction discovery |
| Active Scan++ | Additional active scanning checks |
| Error Message Checks | Information disclosure detection |

Extensions should complement manual testing rather than replace it.

---

# Autorize

## Purpose

Autorize assists with identifying access-control vulnerabilities by automatically replaying requests using the credentials of another user.

It is particularly useful when testing applications containing multiple users, roles or privilege levels.

Typical examples include:

- administrator and normal user
- manager and employee
- customer A and customer B
- authenticated and unauthenticated users
- privileged and low-privileged accounts

---

## Useful For

Autorize can assist with identifying:

- Insecure Direct Object References (IDOR)
- horizontal privilege escalation
- vertical privilege escalation
- missing authorisation controls
- broken role-based access control
- administrative functionality exposed to normal users
- authenticated functionality accessible without authentication

---

## Typical Workflow

```text
Create Low-Privilege Account
        ↓
Authenticate as Low-Privilege User
        ↓
Capture Session Cookie
        ↓
Configure Autorize
        ↓
Authenticate as Higher-Privilege User
        ↓
Browse Application
        ↓
Autorize Replays Requests
        ↓
Compare Responses
        ↓
Investigate Potential Access-Control Issues
```

---

## Example Scenario

Assume the application contains two accounts:

```text
administrator
normal-user
```

The administrator accesses:

```text
GET /admin/users
```

with:

```http
Cookie: session=ADMIN_SESSION
```

Autorize can replay the request using:

```http
Cookie: session=NORMAL_USER_SESSION
```

If the application returns the administrative functionality to the normal user, this may indicate a vertical privilege escalation vulnerability.

---

## Horizontal Authorisation Testing

Autorize is also useful when testing users with the same privilege level.

Example:

```text
User A
User B
```

User A accesses:

```http
GET /api/account/1001
```

Autorize can help determine whether the request remains accessible when replayed using User B's session.

This may reveal horizontal access-control weaknesses.

---

## Manual Verification

Autorize findings should always be manually verified.

Send the interesting request to **Repeater** and compare:

```text
Original User
      ↓
Original Request
      ↓
Baseline Response
```

against:

```text
Different User
      ↓
Same Request
      ↓
Modified Session
      ↓
Response
```

Check more than the HTTP status code.

Compare:

- response body
- response length
- returned objects
- sensitive information
- application behaviour
- side effects
- redirects
- error messages

!!! tip
    A `200 OK` response does not automatically prove an authorisation vulnerability. The response may contain an access-denied message while still returning HTTP 200.

---

# AuthMatrix

## Purpose

AuthMatrix provides a structured method for testing access controls across multiple users and roles.

It is especially useful when an application has a complex permission model.

Example:

```text
Administrator
Manager
Employee
Customer
Unauthenticated
```

Instead of manually testing every endpoint with every account, AuthMatrix allows requests and roles to be organised into an access-control matrix.

---

## Example Matrix

| Function | Admin | Manager | User | Anonymous |
|---|---:|---:|---:|---:|
| View profile | ✓ | ✓ | ✓ | ✗ |
| Edit own profile | ✓ | ✓ | ✓ | ✗ |
| View another user | ✓ | ✓ | ✗ | ✗ |
| Delete user | ✓ | ✗ | ✗ | ✗ |
| Admin panel | ✓ | ✗ | ✗ | ✗ |

The expected access model can then be compared against the application's actual behaviour.

---

## Useful For

AuthMatrix is particularly useful for:

- role-based access control
- multi-role applications
- horizontal privilege escalation
- vertical privilege escalation
- administrative interfaces
- API permission testing
- complex authorisation models

---

## Testing Strategy

A useful approach is:

```text
Identify Roles
      ↓
Create Test Accounts
      ↓
Map Sensitive Functions
      ↓
Define Expected Access
      ↓
Capture Requests
      ↓
Test Requests Across Roles
      ↓
Identify Differences
      ↓
Verify Manually
```

---

# JWT Editor

## Purpose

JWT Editor assists with analysing and testing JSON Web Tokens.

JWTs are commonly used for:

- authentication
- API access
- session management
- identity information
- role information
- authorisation claims

---

## JWT Structure

A typical JWT consists of:

```text
HEADER.PAYLOAD.SIGNATURE
```

For example:

```text
eyJhbGciOiJSUzI1NiJ9
.
eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InVzZXIifQ
.
SIGNATURE
```

Decoded conceptually:

```json
{
  "alg": "RS256"
}
```

```json
{
  "sub": "1234567890",
  "role": "user"
}
```

---

## Useful Testing Areas

JWT Editor can assist when investigating:

- token signatures
- JWT claims
- signing algorithms
- key handling
- token validation
- expiration
- issuer validation
- audience validation
- role claims
- key confusion issues

---

## Claims to Review

Common claims include:

```text
sub
iss
aud
exp
nbf
iat
jti
```

Applications may also introduce custom claims:

```text
role
admin
permissions
user_id
tenant
scope
```

Pay particular attention to claims that appear to influence authorisation.

---

## Workflow

```text
Capture JWT
    ↓
Decode Token
    ↓
Inspect Header
    ↓
Inspect Claims
    ↓
Identify Security-Relevant Fields
    ↓
Understand Signature Configuration
    ↓
Test Validation Behaviour
    ↓
Verify Server-Side Enforcement
```

---

# Param Miner

## Purpose

Param Miner helps discover parameters, headers and other inputs that may not be visible during normal application usage.

These hidden inputs can expose additional attack surface.

---

## Useful For

Param Miner can assist with discovering:

- hidden GET parameters
- hidden POST parameters
- HTTP headers
- cookies
- undocumented application behaviour
- cache-related behaviour
- proxy behaviour

---

## Example

A request may initially contain:

```http
GET /account HTTP/1.1
Host: example.test
```

The application might also recognise an undocumented parameter:

```text
?debug=true
```

or header:

```http
X-Original-URL: /admin
```

Discovering hidden inputs can expose application functionality that was not visible through the normal interface.

---

## Workflow

```text
Interesting Request
       ↓
Param Miner
       ↓
Guess Parameters / Headers
       ↓
Observe Response Differences
       ↓
Investigate Interesting Inputs
       ↓
Send to Repeater
       ↓
Manual Verification
```

---

## Particularly Useful During

Param Miner is valuable when investigating:

- cache poisoning
- routing behaviour
- reverse proxies
- hidden functionality
- undocumented APIs
- unusual authentication behaviour
- header-based application logic

---

# Logger++

## Purpose

Logger++ provides enhanced logging and filtering capabilities for HTTP traffic passing through Burp Suite.

Large applications can generate thousands of requests, making HTTP history difficult to analyse efficiently.

Logger++ can help organise this traffic.

---

## Useful For

Logger++ is useful for:

- recording requests and responses
- searching historical traffic
- filtering requests
- analysing large applications
- identifying unusual responses
- finding interesting parameters
- reviewing previous test activity

---

## Useful Search Targets

During an assessment, search captured traffic for terms such as:

```text
admin
debug
token
password
secret
apikey
api_key
authorization
bearer
session
internal
redirect
callback
upload
download
file
```

These searches can quickly identify interesting application functionality.

---

# HTTP Request Smuggler

## Purpose

HTTP Request Smuggler assists with testing applications for HTTP request smuggling vulnerabilities.

These vulnerabilities can occur when front-end and back-end systems interpret HTTP request boundaries differently.

---

## Architecture

A common architecture might look like:

```text
Client
  ↓
CDN / Reverse Proxy
  ↓
Load Balancer
  ↓
Web Server
  ↓
Application
```

Different components may parse requests differently.

That difference can introduce request desynchronisation behaviour.

---

## Useful For

The extension assists with investigating:

- request parsing inconsistencies
- proxy behaviour
- front-end/back-end disagreement
- request desynchronisation
- HTTP request smuggling conditions

---

## Testing Approach

```text
Identify Proxy Architecture
        ↓
Capture Request
        ↓
Analyse Request Handling
        ↓
Run Appropriate Checks
        ↓
Observe Timing / Response Behaviour
        ↓
Investigate Anomalies
        ↓
Manually Verify
```

!!! warning
    Request smuggling testing can affect shared connections and other application users. Testing should be performed carefully within the agreed scope and rules of engagement.

---

# Turbo Intruder

## Purpose

Turbo Intruder provides a high-performance HTTP request engine for situations where a large number of requests or precise request timing is required.

It should generally be used when standard Burp Intruder is not suitable for the testing scenario.

---

## Useful For

Turbo Intruder can assist with:

- race-condition testing
- high-volume request testing
- timing-sensitive application behaviour
- large input sets
- custom request workflows

---

## Typical Workflow

```text
Interesting Request
       ↓
Send to Turbo Intruder
       ↓
Define Request Strategy
       ↓
Execute Controlled Requests
       ↓
Analyse Responses
       ↓
Identify Anomalies
       ↓
Verify Manually
```

!!! warning
    High-volume testing can affect application availability. Configure request volume according to the agreed testing scope and rate limits.

---

# Collaborator Everywhere

## Purpose

Collaborator Everywhere helps identify functionality that may cause the target application to interact with external systems.

It works with Burp Collaborator to identify out-of-band interactions.

---

## Useful For

It can help discover potential:

- server-side request behaviour
- backend HTTP requests
- DNS interactions
- email interactions
- asynchronous processing
- blind vulnerabilities
- external service integrations

---

## Concept

Some vulnerabilities do not immediately appear in the HTTP response.

Instead:

```text
Request
   ↓
Application
   ↓
Backend Processing
   ↓
External Interaction
   ↓
Burp Collaborator
```

The external interaction may provide evidence that user-controlled data reached a backend component.

---

## Workflow

```text
Enable Collaborator Everywhere
          ↓
Browse Application
          ↓
Extension Adds Collaborator Payloads
          ↓
Application Processes Requests
          ↓
Monitor Collaborator
          ↓
Investigate Interactions
          ↓
Manual Verification
```

---

# Active Scan++

## Purpose

Active Scan++ extends Burp Scanner with additional checks for web application vulnerabilities and unusual application behaviour.

It can complement Burp's built-in scanner during authorised assessments.

---

## Useful For

The extension may assist with identifying:

- input validation weaknesses
- unusual response behaviour
- additional server-side issues
- application-specific weaknesses

Automated findings should always be manually verified.

---

# Backslash Powered Scanner

## Purpose

Backslash Powered Scanner uses unusual input transformations and response differences to identify potentially interesting server-side behaviour.

It can help identify inputs that warrant deeper manual investigation.

---

## Testing Philosophy

The extension is particularly useful for identifying behaviour such as:

```text
Input
  ↓
Unexpected Server Processing
  ↓
Response Difference
  ↓
Potential Injection Point
  ↓
Manual Investigation
```

The extension should be considered a discovery tool rather than proof of vulnerability.

---

# Error Message Checks

## Purpose

Error Message Checks assists with identifying verbose application error messages.

Verbose errors can disclose useful technical information about the application.

---

## Information That May Be Exposed

Examples include:

- stack traces
- framework versions
- database errors
- filesystem paths
- SQL queries
- internal hostnames
- package names
- source code references
- debugging information

---

## Example

Instead of:

```text
Invalid request.
```

an application might return:

```text
SQLException
Database connection failed
/var/www/application/controllers/UserController.php
```

This information can assist with technology identification and further vulnerability research.

---

# Built-In Burp Features

Extensions are useful, but many important tests can be performed using Burp's built-in functionality.

---

## Proxy

Use Proxy for:

- intercepting requests
- modifying requests
- viewing application traffic
- understanding application behaviour
- identifying interesting endpoints

A common workflow is:

```text
Browser
   ↓
Burp Proxy
   ↓
Application
```

---

# HTTP History

HTTP history is one of the most valuable sources of information during an assessment.

Review it for:

- API endpoints
- authentication requests
- administrative functions
- object identifiers
- file operations
- redirects
- interesting parameters
- hidden functionality

Useful filters include:

```text
MIME type
HTTP method
Status code
Search term
In-scope only
```

---

# Repeater

Repeater is one of the most important tools for manual web application testing.

Use it to repeatedly modify and resend requests.

Typical workflow:

```text
Proxy
  ↓
Interesting Request
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Modify One Element
  ↓
Send
  ↓
Compare Response
  ↓
Repeat
```

Repeater is particularly useful for:

- authentication testing
- authorisation testing
- input validation
- API testing
- injection testing
- session testing
- business logic testing

---

# Intruder

Intruder automates repeated requests using configurable payload positions.

It is useful when the same test must be performed against multiple values.

Examples include:

- parameter enumeration
- identifier testing
- input fuzzing
- endpoint testing
- header testing
- controlled wordlist-based testing

---

# Comparer

Comparer allows two pieces of data to be compared.

This is particularly useful for authorisation testing.

Example:

```text
Administrator Response
          ↓
       Comparer
          ↑
Normal User Response
```

Differences may reveal whether sensitive information or functionality remains accessible.

---

# Decoder

Decoder can transform encoded data.

Common formats encountered during testing include:

```text
URL encoding
Base64
Hex
HTML encoding
```

Decoder is useful when analysing:

- cookies
- parameters
- tokens
- API data
- application-generated identifiers

---

# Sequencer

Sequencer analyses the randomness of tokens.

It can be useful when investigating:

- session identifiers
- CSRF tokens
- password-reset tokens
- application-generated security tokens

A typical workflow is:

```text
Identify Token
     ↓
Capture Multiple Samples
     ↓
Sequencer
     ↓
Analyse Randomness
     ↓
Investigate Predictability
```

---

# Recommended Extension Workflow

Do not install extensions simply because they are available.

Select extensions according to the functionality being tested.

```text
Application Mapping
        ↓
Identify Testing Area
        ↓
Select Relevant Extension
        ↓
Automated Assistance
        ↓
Review Interesting Results
        ↓
Repeater
        ↓
Manual Verification
        ↓
Evidence Collection
        ↓
Reporting
```

---

# Extension Selection by Testing Area

## Authentication

Useful tools:

```text
Proxy
Repeater
Intruder
Sequencer
Logger++
```

---

## Authorisation

Useful tools:

```text
Autorize
AuthMatrix
Repeater
Comparer
Logger++
```

---

## Session Management

Useful tools:

```text
Proxy
Repeater
Sequencer
Decoder
Logger++
```

---

## JWT

Useful tools:

```text
JWT Editor
Repeater
Decoder
Logger++
```

---

## Reconnaissance

Useful tools:

```text
Param Miner
Logger++
HTTP History
Target Sitemap
```

---

## HTTP Behaviour

Useful tools:

```text
Param Miner
HTTP Request Smuggler
Repeater
Comparer
```

---

## Out-of-Band Testing

Useful tools:

```text
Burp Collaborator
Collaborator Everywhere
Repeater
```

---

## Race Conditions

Useful tools:

```text
Repeater
Turbo Intruder
```

---

# Suggested Core Extension Set

For a general web application penetration test, a useful starting collection is:

```text
Autorize
AuthMatrix
JWT Editor
Param Miner
Logger++
HTTP Request Smuggler
Collaborator Everywhere
Turbo Intruder
Active Scan++
Backslash Powered Scanner
Error Message Checks
```

You do not necessarily need every extension for every assessment.

Choose extensions based on the application and attack surface.

---

# Manual Verification

Burp extensions should primarily be treated as assistants.

A useful principle is:

```text
Extension Finding
       ↓
Understand Why It Was Flagged
       ↓
Send Request to Repeater
       ↓
Establish Baseline
       ↓
Reproduce Behaviour
       ↓
Determine Security Impact
       ↓
Capture Evidence
       ↓
Report
```

!!! tip
    Do not report a vulnerability solely because a Burp extension marked a request as interesting or vulnerable. Reproduce the behaviour manually and determine the actual security impact.

---

# Practical Burp Toolkit

A useful way to think about Burp Suite during an assessment is:

```text
                    BURP SUITE
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    DISCOVERY        TESTING         ANALYSIS
        │               │               │
     Proxy           Repeater         Logger++
 HTTP History        Intruder         Comparer
 Param Miner      Turbo Intruder      Decoder
        │               │             Sequencer
        └───────────────┼───────────────┘
                        │
                   SPECIALISED
                        │
             Autorize / AuthMatrix
                   JWT Editor
             HTTP Request Smuggler
            Collaborator Everywhere
```

The objective is not to automate the entire assessment.

The objective is to combine:

```text
Application Understanding
          +
Manual Testing
          +
Burp Automation
          +
Specialised Extensions
          =
Effective Web Application Testing
```

---

## Related Notes

- [Web Application Testing Methodology](../methodology.md)
- [Web Application Pentesting Checklist](../checklist.md)
- [Authentication Testing](../authentication.md)
- [Authorisation Testing](../authorisation.md)
- [Session Management Testing](../session-management.md)
- [Burp Suite Testing Workflows](workflows.md)
