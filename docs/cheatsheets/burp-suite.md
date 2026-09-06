---
title: Burp Suite Cheatsheet
description: Detailed practical Burp Suite reference for authorised web application and API security assessments covering Proxy, Repeater, Intruder, Decoder, Comparer, Sequencer, Collaborator, extensions, authentication, authorisation, APIs, evidence collection and testing workflows.
---

# Burp Suite Cheatsheet

Burp Suite is an integrated platform for web application and API security testing.

Rather than treating Burp as a collection of individual tools, use it as an assessment workflow:

```text
Browser / Client
       |
       v
     Proxy
       |
       v
  HTTP History
       |
       v
Identify Interesting Request
       |
       v
    Repeater
       |
       v
Controlled Modification
       |
       +--> Authentication
       +--> Authorisation
       +--> Input Validation
       +--> Business Logic
       +--> API Behaviour
       |
       v
Compare Responses
       |
       v
Further Validation
       |
       v
Evidence
       |
       v
Finding
```

!!! warning "Authorised Security Testing"

    Only use Burp Suite against applications, APIs and infrastructure that you are explicitly authorised to assess. Intruder, extensions, active scanning and automated testing can generate substantial traffic or change application state. Understand the assessment scope before using automated functionality.


# Quick Reference

| Task | Burp Tool |
|---|---|
| Capture browser traffic | Proxy |
| Review requests | HTTP history |
| Modify and resend requests | Repeater |
| Automate controlled input variations | Intruder |
| Encode/decode data | Decoder |
| Compare responses | Comparer |
| Analyse session token randomness | Sequencer |
| Out-of-band interaction testing | Collaborator |
| Organise interesting requests | Organizer |
| Inspect WebSockets | WebSockets history |
| Extend Burp | Extensions / BApp Store |
| Automated vulnerability testing | Scanner - Professional |
| Browser testing | Burp's browser |


# Practical Testing Model

A strong Burp workflow is:

```text
BASELINE
   |
   v
Understand Normal Request
   |
   v
Identify Security Boundary
   |
   v
Change One Variable
   |
   v
Observe Response
   |
   v
Compare With Baseline
   |
   v
Determine Alternative Explanations
   |
   v
Validate Again
   |
   v
Document Security Consequence
```

Avoid:

```text
Intercept Request
      |
      v
Change Everything
      |
      v
Unexpected Response
      |
      v
Report Vulnerability
```

Controlled testing produces much stronger evidence.


# Starting Burp Suite

On Kali Linux:

```bash
burpsuite
```

Check the installed package:

```bash
apt policy burpsuite
```

For the latest supported release and installation options, use the official PortSwigger distribution appropriate to your environment.


# Burp's Browser

A convenient testing method is:

```text
Proxy
    |
    v
Open Browser
```

Burp's embedded browser is already configured to proxy traffic through Burp.

This avoids manually configuring a separate browser for many assessment workflows.


# External Browser

Typical Burp proxy listener:

```text
127.0.0.1:8080
```

Configure the assessment browser to use:

```text
HTTP Proxy: 127.0.0.1
Port:       8080
```

HTTPS traffic also needs Burp's CA certificate trusted in the dedicated assessment browser if you want Burp to inspect TLS-protected application traffic.


# Dedicated Assessment Browser

Prefer a browser/profile used specifically for security testing.

This helps separate:

```text
Personal sessions

Production credentials

Assessment accounts

Burp certificates

Proxy configuration

Testing extensions
```


# Proxy

The Proxy is the central point through which browser HTTP/S traffic passes.

```text
Browser
   |
   v
Burp Proxy
   |
   v
Application
```


# Intercept

When interception is enabled:

```text
Browser
   |
   v
Burp Holds Request
   |
   v
Tester Reviews / Modifies
   |
   v
Forward
   |
   v
Server
```

Use interception when you specifically need to modify a request before it reaches the server.


# Intercept Off Is Normal

You do not need to leave interception enabled constantly.

A common workflow is:

```text
Intercept Off
     |
     v
Browse Application Normally
     |
     v
HTTP History
     |
     v
Find Interesting Request
     |
     v
Send to Repeater
```

This is often more efficient than manually forwarding every request.


# HTTP History

Proxy HTTP history records requests passing through Burp.

Review fields such as:

```text
Host

Method

URL

Status

Length

MIME type

Extension

TLS

Notes
```


# What to Look For

During normal application browsing, identify:

```text
Authentication endpoints

Password reset

Account settings

Administrative endpoints

API requests

Object identifiers

File downloads

File uploads

Search parameters

Redirect parameters

Role-related functionality

Hidden application features

GraphQL endpoints

WebSocket connections
```


# Scope

Define the assessment target before spending significant time in HTTP history.

Conceptually:

```text
Everything Browser Contacts
          |
          v
       Burp
          |
    +-----+-----+
    |           |
    v           v
In Scope     Out of Scope
    |
    v
Assessment
```

Scope helps reduce noise from:

```text
Analytics

CDNs

Advertising

Browser services

Third-party APIs

External identity providers
```

Do not assume a third-party service becomes authorised merely because the application communicates with it.


# Target Scope

Add only authorised hosts and URLs.

Example:

```text
https://app.example.com/
https://api.example.com/
```

Avoid accidentally including unrelated domains.


# Site Map

The Target site map helps visualise discovered application content.

Look for:

```text
Directories

Endpoints

Parameters

API routes

Static resources

Different response codes

Unexpected functionality
```


# Repeater

Repeater is one of the most important Burp tools.

Use it to:

```text
Replay requests

Modify parameters

Change headers

Change cookies

Change methods

Test object identifiers

Test authentication boundaries

Test API requests

Compare responses

Validate findings
```


# Send to Repeater

From HTTP history:

```text
Right-click request
      |
      v
Send to Repeater
```

Common shortcut:

```text
Ctrl+R
```

Then open Repeater and send the request.


# Repeater Testing Model

```text
Original Request
      |
      v
Send
      |
      v
Baseline Response
      |
      v
Change One Input
      |
      v
Send Again
      |
      v
Modified Response
      |
      v
Compare
```


# Baseline First

Before modifying a request, send the original.

Record:

```text
Status

Response length

Response body

Headers

Timing

Application state
```

This becomes the baseline.


# Example Baseline

```http
GET /api/profile HTTP/1.1
Host: app.example.com
Cookie: session=<account-a-session>
Accept: application/json
```

Representative response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1001,
  "username": "account-a"
}
```

Now modifications can be compared against known behaviour.


# Change One Variable

For example:

```text
Baseline:
GET /api/orders/1001

Modified:
GET /api/orders/2001
```

Keep:

```text
Method

Session

Headers

Body
```

constant.

This makes the effect of the object identifier easier to interpret.


# Repeater Tabs

Use descriptive names where possible:

```text
Login Baseline

Account A Own Object

Account A -> Account B

Admin Endpoint

Upload Baseline

CORS Test
```

This reduces confusion during large assessments.


# Authentication Testing

Start by understanding:

```text
Login

Logout

Session creation

Session invalidation

Password reset

MFA

Remember-me

Account recovery

Session expiration
```


# Login Baseline

Capture a valid login request.

Example:

```http
POST /login HTTP/1.1
Host: app.example.com
Content-Type: application/x-www-form-urlencoded

username=testuser&password=<password>
```

Determine:

```text
Success response

Failure response

Redirect behaviour

Session cookie changes

Authentication tokens
```


# Login Response

Possible:

```http
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=<value>; Secure; HttpOnly; SameSite=Lax
```

This provides several observations:

```text
Authentication appears successful.

A session cookie is issued.

The application redirects to /dashboard.
```

It does not prove the overall authentication implementation is secure.


# Session Testing

Review:

```text
Session creation

Cookie attributes

Session rotation

Logout invalidation

Concurrent sessions

Idle timeout

Absolute timeout

Privilege changes
```


# Cookie Attributes

Inspect:

```text
Secure

HttpOnly

SameSite

Domain

Path

Expires

Max-Age
```

Example:

```http
Set-Cookie: session=<value>; Secure; HttpOnly; SameSite=Lax
```


# Session Rotation

A useful controlled test:

```text
Before Login
    |
    v
Session A
    |
    v
Authenticate
    |
    v
Session B?
```

If the application uses session identifiers before and after authentication, determine whether they are appropriately rotated according to the application's design.


# Logout Testing

```text
Authenticated Session
       |
       v
Logout
       |
       v
Reuse Old Session
       |
      / \
 Accepted Rejected
```

A rejected old session supports successful server-side invalidation.

Do not rely only on the browser deleting the cookie.


# Authorisation Testing

Authorisation is one of the strongest uses of Repeater.

A controlled approach uses at least two test identities:

```text
Account A

Account B
```

Prefer accounts created specifically for the assessment.


# Two-Account Matrix

| Request | Expected |
|---|---|
| A -> A object | Allowed |
| A -> B object | Denied |
| B -> B object | Allowed |
| B -> A object | Denied |
| Unauthenticated -> protected object | Denied |


# IDOR / BOLA Example

Controlled environment:

```text
Account A owns order 1001.

Account B owns order 2001.
```

Account A baseline:

```http
GET /api/orders/1001 HTTP/1.1
Host: app.example.com
Authorization: Bearer <account-a-token>
```

Response:

```http
HTTP/1.1 200 OK

{
  "orderId": 1001,
  "owner": "account-a"
}
```


# Cross-Account Test

Change only:

```text
1001
```

to:

```text
2001
```

Request:

```http
GET /api/orders/2001 HTTP/1.1
Host: app.example.com
Authorization: Bearer <account-a-token>
```

Secure behaviour may be:

```http
HTTP/1.1 403 Forbidden
```

or:

```http
HTTP/1.1 404 Not Found
```

depending on application design.


# Positive Authorisation Result

If Account A receives:

```http
HTTP/1.1 200 OK

{
  "orderId": 2001,
  "owner": "account-b",
  "deliveryAddress": "..."
}
```

validate:

```text
Is 2001 definitely owned by Account B?

Is Account A definitely authenticated?

Should Account A be denied?

Is protected information returned?

Can the behaviour be reproduced?
```


# Defensible Conclusion

Do not report:

> Changing the ID returned 200.

Prefer:

> The API did not enforce object-level authorisation for order resources. A session authenticated as controlled Account A could request the identifier of an order belonging to controlled Account B and receive the protected order information.


# Horizontal Authorisation

```text
User A
  |
  X
  |
User B Resource
```

Test whether one user can access another user's equivalent resources.


# Vertical Authorisation

```text
Standard User
     |
     X
     |
Administrative Function
```

Test whether lower-privileged accounts can access functions reserved for privileged roles.


# Function-Level Authorisation

Do not test only links visible in the UI.

Capture the actual administrative request with an authorised admin test account, then determine how the application responds when the same controlled function is requested under a lower-privileged test account.


# Unauthenticated Testing

Remove:

```text
Cookie

Authorization header

Session token
```

and resend the protected request.

Determine whether the endpoint still exposes protected functionality or data.


# Method Testing

Suppose:

```http
GET /api/profile/1001
```

is authorised correctly.

Where relevant and safe, determine whether other supported methods apply equivalent controls:

```text
POST

PUT

PATCH

DELETE
```

Do not use destructive methods against real data without explicit authorisation.


# API Testing

Burp works especially well with:

```text
REST

JSON

GraphQL

SOAP

Custom HTTP APIs
```


# JSON Request

```http
POST /api/profile HTTP/1.1
Host: app.example.com
Content-Type: application/json
Authorization: Bearer <token>

{
  "displayName": "Test User"
}
```

Review:

```text
Input validation

Authorisation

Unexpected fields

Server-side validation

Error handling

Object ownership
```


# Hidden JSON Fields

Suppose the normal client sends:

```json
{
  "displayName": "Test User"
}
```

Server response contains:

```json
{
  "displayName": "Test User",
  "role": "user"
}
```

Do not automatically assume sending:

```json
{
  "role": "admin"
}
```

will be accepted.

If testing mass assignment in an authorised environment, use controlled accounts and safe properties, and validate server-side behaviour rather than relying on the presence of a field name.


# GraphQL

Common endpoint patterns:

```text
/graphql

/api/graphql
```

A GraphQL request may resemble:

```http
POST /graphql HTTP/1.1
Host: app.example.com
Content-Type: application/json

{
  "query": "{ currentUser { id username } }"
}
```

Review:

```text
Authentication

Object authorisation

Field-level authorisation

Error handling

Introspection policy

Query complexity controls
```

See the detailed [GraphQL Notes](../web/graphql.md).


# HTTP Headers

Useful headers to review:

```text
Host

Origin

Referer

Authorization

Cookie

Content-Type

Accept

X-Forwarded-For

X-Forwarded-Host

Forwarded

X-Original-URL

X-Rewrite-URL
```

The presence of proxy-related headers does not itself imply a bypass.


# Host Header Testing

Baseline:

```http
GET / HTTP/1.1
Host: app.example.com
```

Controlled modification:

```http
GET / HTTP/1.1
Host: test.example.invalid
```

Observe:

```text
Status

Redirects

Absolute URLs

Password-reset links

Cache behaviour

Backend routing
```

A changed response alone does not prove a Host header vulnerability.


# CORS Testing

Baseline request:

```http
GET /api/profile HTTP/1.1
Host: app.example.com
Origin: https://app.example.com
Cookie: session=<value>
```

Controlled origin:

```http
Origin: https://example.invalid
```

Review:

```text
Access-Control-Allow-Origin

Access-Control-Allow-Credentials

Vary
```


# CORS Interpretation

A reflected origin is not automatically exploitable.

Determine:

```text
Can credentials be included?

Does the browser permit the response to be read?

Does the endpoint return sensitive information?

Is the origin actually trusted?

Does the behaviour apply to authenticated requests?
```


# Preflight

Example:

```http
OPTIONS /api/profile HTTP/1.1
Host: app.example.com
Origin: https://example.invalid
Access-Control-Request-Method: GET
Access-Control-Request-Headers: Authorization
```

Review the server response.


# CSRF

When testing state-changing requests, determine:

```text
Does the request depend on cookies?

Is there a CSRF token?

Is the token validated?

Is SameSite relevant?

Does Origin/Referer validation exist?

Can a cross-site request produce the state change?
```

Do not conclude CSRF solely because a token is absent.


# Open Redirect

Example:

```http
GET /redirect?next=/dashboard HTTP/1.1
Host: app.example.com
```

Controlled modification:

```text
next=https://example.invalid/
```

Review:

```text
Location header

Validation

Allowed destinations

URL parsing behaviour
```

See [Open Redirect](../web/open-redirect.md).


# File Upload

Capture a normal authorised upload.

Example:

```http
POST /upload HTTP/1.1
Host: app.example.com
Content-Type: multipart/form-data; boundary=...

...
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

Authorised assessment test file
...
```

Review:

```text
Filename handling

Content-Type validation

Extension validation

Storage location

Download behaviour

Authorisation

Metadata handling
```


# Safe Upload Baseline

Start with a harmless file:

```text
test.txt
```

Establish:

```text
Upload succeeds?

Where is it stored?

Can it be downloaded?

Who can access it?

Is filename changed?

Is Content-Type changed?
```


# Path Traversal

Example application request:

```http
GET /download?file=report.pdf HTTP/1.1
Host: app.example.com
```

First determine how the application normally identifies files.

Testing should focus on controlled files and the authorised environment.

See [Path Traversal](../web/path-traversal.md).


# SSRF

Server-side request functionality may appear in:

```text
URL previews

Webhook configuration

Import-by-URL

Image fetchers

PDF generators

Integrations

Callback configuration
```

A controlled test should answer:

```text
Did the application server make the request?

Was only DNS resolution performed?

Was an HTTP request received?

Which source IP connected?

Which protocol was used?
```


# Collaborator

Burp Collaborator can support detection of out-of-band interactions in authorised assessments.

Typical workflow:

```text
Collaborator Payload
       |
       v
Controlled Input
       |
       v
Application Processes Input
       |
       v
DNS / HTTP Interaction?
       |
       v
Collaborator
```


# Collaborator Interpretation

Suppose you observe:

```text
DNS interaction only
```

This supports:

```text
Some component attempted to resolve the supplied hostname.
```

It does not necessarily prove:

```text
The application performed an HTTP request.

Internal resources are reachable.

Sensitive data can be retrieved.
```


# HTTP Interaction

If Collaborator records:

```text
DNS
+
HTTP request
```

this is stronger evidence that an HTTP-capable component attempted a server-side request.

Still determine:

```text
Which component made it?

What source IP was used?

What input triggered it?

Can the behaviour be reproduced?

What destinations/protocols are permitted?

What security consequence follows?
```


# Collaborator Evidence

Capture:

```text
Payload

Request containing payload

Interaction timestamp

Interaction type

Source IP

DNS details

HTTP request where present

Correlation ID
```


# Intruder

Intruder automates repeated requests with controlled variations.

Useful legitimate assessment cases include:

```text
Parameter enumeration

Identifier variation

Header comparison

Input boundary testing

Response comparison

Content discovery
```

Be cautious with:

```text
Authentication attempts

Account recovery

MFA

Expensive API operations

State-changing endpoints
```


# Intruder Workflow

```text
Baseline Request
      |
      v
Send to Intruder
      |
      v
Choose Positions
      |
      v
Define Payloads
      |
      v
Control Request Rate
      |
      v
Run
      |
      v
Sort Responses
      |
      v
Investigate Outliers
```


# Payload Positions

Intruder marks positions using:

```text
§value§
```

Example:

```http
GET /api/items/§1001§ HTTP/1.1
Host: app.example.com
```

Only mark the value that should vary.


# Response Analysis

Useful Intruder columns include:

```text
Status

Length

Words

Lines

Time

Error

Custom grep results
```

Outliers can indicate interesting behaviour but require manual validation.


# Response Length

Example:

```text
1001 -> 200 -> 842 bytes
1002 -> 403 -> 120 bytes
1003 -> 403 -> 120 bytes
1004 -> 200 -> 915 bytes
```

The `1004` response deserves investigation.

It does not automatically mean:

```text
Authorisation bypass confirmed.
```


# Intruder Rate

Before automated testing consider:

```text
Application capacity

Production impact

Rate limiting

Account lockout

Monitoring

Rules of engagement
```

Use the minimum request volume needed to answer the assessment question.


# Authentication and Intruder

Do not start credential attacks simply because Intruder supports repeated requests.

Before any authentication automation establish:

```text
Explicit authorisation

Test accounts

Lockout policy

Allowed request rate

Monitoring expectations

Stop conditions
```


# Decoder

Decoder helps transform data between common encodings.

Common uses:

```text
URL encoding

Base64

Hex

HTML encoding
```


# Example Base64

Input:

```text
dGVzdA==
```

Decode:

```text
test
```

Encoding is not encryption.


# URL Encoding

Example:

```text
Test Value
```

may become:

```text
Test%20Value
```

Understand where decoding occurs:

```text
Browser

Proxy

Web server

Framework

Application
```


# Multiple Decoding Layers

A value may pass through several parsers:

```text
Client
  |
  v
Proxy
  |
  v
Web Server
  |
  v
Framework
  |
  v
Application
```

Unexpected behaviour can result from different decoding stages.


# Comparer

Comparer helps identify differences between:

```text
Responses

Requests

Tokens

Application output
```

Useful for:

```text
Authorisation comparisons

Authentication responses

Error messages

Different user roles

Different backend responses
```


# Two-Account Comparer Workflow

```text
Account A Response
       |
       v
Comparer
       ^
       |
Account B Response
```

This can highlight differences that are difficult to spot manually.


# Compare Baseline vs Modified

```text
Baseline
   |
   v
Comparer
   ^
   |
Modified
```

Then determine whether the difference is security relevant.


# Sequencer

Sequencer analyses the quality of tokens whose unpredictability matters.

Potential candidates:

```text
Session identifiers

CSRF tokens

Password reset tokens

Other security-sensitive values
```

Only test tokens generated for authorised assessment accounts.


# Sequencer Workflow

```text
Identify Token
     |
     v
Determine Security Purpose
     |
     v
Collect Sufficient Samples
     |
     v
Sequencer Analysis
     |
     v
Interpret Carefully
```

Statistical output should not be translated directly into a vulnerability without considering how the token is generated and used.


# Organizer

Organizer can help preserve important requests during a large assessment.

Useful categories:

```text
Potential Finding

Needs Validation

Interesting Endpoint

Authentication

Authorisation

API

Upload

Business Logic
```


# Notes

Add notes to important requests such as:

```text
Account A baseline

Account B object

Admin-only endpoint

Potential IDOR - needs ownership confirmation

Interesting 500 response
```

This reduces rework later.


# WebSockets

Modern applications may use WebSockets for:

```text
Chat

Notifications

Live dashboards

Trading interfaces

Administrative consoles

Real-time APIs
```


# WebSocket History

Burp can display WebSocket messages passing through the proxy.

Review:

```text
Connection establishment

Authentication

Message structure

Object identifiers

Authorisation

Server responses
```


# WebSocket Security Model

Do not assume:

```text
Authenticated WebSocket
        |
        v
Every Message Authorised
```

Individual messages may still require server-side authorisation.


# WebSocket Testing

Controlled approach:

```text
Account A Connection
       |
       v
Normal Message
       |
       v
Baseline Response
       |
       v
Modify Object Identifier
       |
       v
Observe Server Behaviour
```


# Scanner

Burp Scanner is available in Burp Suite Professional.

It can assist with detecting classes of web vulnerabilities.

Automated scanner output should be treated as:

```text
Scanner Observation
       |
       v
Review Request
       |
       v
Review Response
       |
       v
Understand Detection Logic
       |
       v
Manual Validation
       |
       v
Security Conclusion
```


# Do Not Report Scanner Output Blindly

Automated findings may be:

```text
True positive

False positive

Informational

Context-dependent

Duplicate

Not exploitable
```

Manual validation remains important.


# Passive vs Active Scanning

Conceptually:

```text
Passive
   |
   v
Observe Existing Traffic

Active
   |
   v
Send Additional Test Requests
```

Active scanning may:

```text
Generate substantial traffic

Modify application state

Trigger monitoring

Reach sensitive endpoints
```

Use it according to scope and rules of engagement.


# Extensions

Burp can be extended through the BApp Store.

Useful categories include:

```text
Authorisation testing

Request manipulation

API testing

HTTP request smuggling

JWT analysis

GraphQL

Logging

Response comparison
```


# Extension Safety

Extensions can:

```text
Read traffic

Modify traffic

Generate requests

Store sensitive data

Connect to external services
```

Before installing an extension, understand:

```text
What data it accesses

Whether it sends data externally

Whether it generates requests

Whether it is actively maintained

Whether the engagement permits it
```


# Useful Extension - Autorize

Autorize can assist with authorisation testing by comparing requests under different authentication contexts.

Conceptually:

```text
Privileged Request
       |
       v
Repeat With Lower-Privilege Context
       |
       v
Compare
```

Manual confirmation is still required.


# Useful Extension - AuthMatrix

AuthMatrix can help model:

```text
Users

Roles

Requests

Expected permissions
```

This is useful for complex role-based applications.


# Useful Extension - Logger++

Logger++ can provide enhanced HTTP logging and filtering.

Useful for:

```text
Large assessments

Traffic review

Search

Filtering

Request history
```


# Useful Extension - JWT Editor

JWT Editor can assist with JWT inspection and controlled testing.

Review JWTs for:

```text
Header

Claims

Signature

Key selection

Expiration

Issuer

Audience

Authorisation use
```

See [JWT Notes](../web/jwt.md).


# Useful Extension - HTTP Request Smuggler

PortSwigger's HTTP Request Smuggler extension can support authorised HTTP desynchronisation testing.

This is specialised testing that should only be performed when:

```text
In scope

Operational impact understood

Testing method understood

Request volume controlled
```

See [HTTP Request Smuggling](../web/http-request-smuggling.md).


# Useful Extension - Param Miner

Param Miner can help identify:

```text
Hidden parameters

Headers

Cookies

Cache-related input
```

Automated discovery results still require validation.


# Useful Extension - Turbo Intruder

Turbo Intruder supports specialised high-performance request workflows.

It can generate substantial traffic.

Use it only when:

```text
Necessary

Explicitly authorised

Rate understood

Impact understood

Stop conditions defined
```


# Extension Workflow

```text
Install Extension
      |
      v
Understand Behaviour
      |
      v
Configure Scope
      |
      v
Use Against Controlled Target
      |
      v
Review Generated Requests
      |
      v
Manually Validate Results
```


# Content Discovery

Burp can assist with identifying application endpoints through:

```text
Normal browsing

Site map

JavaScript requests

API traffic

Scanner observations

Extensions
```

Combine this with the [Web Application Security Cheatsheet](web.md).


# JavaScript Analysis

Review JavaScript responses for:

```text
API paths

Route names

Parameter names

Feature flags

Internal references

Source maps

Client-side validation
```

Do not automatically report every internal-looking string as sensitive information.


# Search HTTP History

Search for terms such as:

```text
/admin

/api/

/graphql

token

Authorization

password

redirect

upload

download

debug
```

Use this as a discovery technique, not as proof of a vulnerability.


# Error Handling

Interesting responses include:

```text
400

401

403

404

405

409

415

429

500

502

503
```

Pay particular attention to differences between baseline and modified requests.


# 500 Responses

A server error may indicate:

```text
Unhandled input

Application exception

Backend failure

Parsing error

Unexpected state
```

It does not automatically prove exploitable behaviour.


# Sensitive Error Information

Review error responses for unnecessary disclosure such as:

```text
Stack traces

Filesystem paths

Internal hostnames

Database details

Framework information

Source code fragments
```

Determine whether the disclosed information creates meaningful security impact.


# Response Length

Length differences are useful signals.

Example:

```text
Baseline: 403 / 120 bytes
Modified: 200 / 842 bytes
```

This is worth investigation.

But:

```text
Different length
```

does not equal:

```text
Vulnerability.
```


# Status Codes

| Code | General Meaning | Assessment Question |
|---:|---|---|
| 200 | Success | Was the requester authorised? |
| 201 | Created | Was creation permitted? |
| 204 | Success, no body | Did an authorised state change occur? |
| 301 | Permanent redirect | Where is the client redirected? |
| 302 | Redirect | Is the destination expected? |
| 307 | Redirect preserving method | Is method/body preserved appropriately? |
| 308 | Permanent redirect preserving method | Is destination expected? |
| 400 | Bad request | Does the error disclose internals? |
| 401 | Authentication required/failed | Is authentication consistently enforced? |
| 403 | Forbidden | Is authorisation consistently enforced? |
| 404 | Not found | Is existence intentionally hidden? |
| 405 | Method not allowed | Are other methods handled differently? |
| 415 | Unsupported media type | Which content types are accepted? |
| 429 | Rate limited | How is the control scoped? |
| 500 | Server error | Is sensitive diagnostic information exposed? |


# Response Comparison

When testing security controls, compare:

```text
Status

Length

Headers

Body

Timing

Cookies

Redirects

Application state
```

Do not rely on only one indicator.


# Business Logic Testing

Burp is particularly valuable for business-logic testing because requests can be replayed outside the normal UI sequence.

Map:

```text
Step 1
  |
  v
Step 2
  |
  v
Step 3
  |
  v
Final Action
```

Then ask:

```text
Can a step be skipped?

Can a step be repeated?

Can requests be reordered?

Is server-side state validated?

Does one user control another user's workflow?

Are important values trusted from the client?
```


# Business Logic Baseline

Document the legitimate workflow before modifying it.

Example:

```text
Add Item
   |
   v
Review Cart
   |
   v
Confirm Address
   |
   v
Confirm Order
```

Then test only safe, controlled deviations.


# Client-Side Controls

A browser may prevent:

```text
Negative values

Unexpected characters

Disabled options

Hidden fields

Role selections
```

Burp allows the raw request to be examined.

The security question is:

```text
Does the server enforce the same security rule?
```


# Rate Limiting

Controlled testing can compare repeated requests.

Possible response:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

This demonstrates some rate-limiting behaviour.

It does not prove the control is sufficient across:

```text
Accounts

IPs

Sessions

Endpoints

Distributed sources
```


# Cache Behaviour

Review headers such as:

```text
Cache-Control

Age

Vary

ETag

Via

X-Cache
```

Names vary across infrastructure.

Cache testing should use controlled requests because shared caches can affect other users.


# Request Smuggling

HTTP request smuggling/desynchronisation testing is specialised.

Before testing establish:

```text
Reverse proxy architecture

Scope

Production impact

Request volume

Safe endpoint

Stop conditions
```

Do not blindly send copied desynchronisation payloads to production applications.


# Burp and curl

Burp and curl complement each other:

```text
Browser
   |
   v
Burp
   |
   v
Interesting Request
   |
   v
Reproduce With curl
   |
   v
Automation / Evidence
```

Or:

```text
curl
 |
 v
Burp Proxy
 |
 v
Repeater
```

Example:

```bash
curl -k -x http://127.0.0.1:8080 https://example.com/
```

See the [curl Cheatsheet](curl.md).


# Burp and Nmap

```text
Nmap
 |
 v
Web Service Identified
 |
 v
curl
 |
 v
Initial HTTP Triage
 |
 v
Burp Suite
 |
 v
Application Testing
```

See the [Nmap Cheatsheet](nmap.md).


# Burp and Wireshark

```text
Burp
 |
 v
HTTP/Application Behaviour

Wireshark
 |
 v
Packet/Protocol Behaviour
```

Use Burp when the question is:

```text
What HTTP request did the application make?
```

Use Wireshark when the question is:

```text
What happened at the network/protocol layer?
```

See the [Wireshark and tshark Cheatsheet](wireshark-tshark.md).


# Evidence Collection

For a significant Burp test capture:

```text
Test ID

Timestamp

Target

URL

HTTP method

Account

Role

Authentication context

Baseline request

Baseline response

Modified request

Modified response

Security consequence

Burp version

Relevant notes
```


# Request Evidence

Preserve the minimum request required to reproduce the behaviour.

Example:

```http
GET /api/orders/2001 HTTP/1.1
Host: app.example.com
Authorization: Bearer <redacted>
Accept: application/json
```


# Response Evidence

Preserve relevant portions:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "orderId": 2001,
  "owner": "account-b",
  "deliveryAddress": "<redacted>"
}
```

Redact unnecessary personal or sensitive data.


# Screenshots

A useful screenshot should show enough context to understand:

```text
Request

Modified parameter

Response

Relevant protected data

Burp tab/tool
```

Avoid screenshots containing unrelated sensitive data.


# Evidence Naming

Example:

```text
WEB-004-account-a-own-object.txt
WEB-004-account-a-cross-account.txt
WEB-004-response-cross-account.txt
WEB-004-evidence.png
```


# Finding Workflow

```text
Observation
    |
    v
Baseline
    |
    v
Controlled Modification
    |
    v
Unexpected Behaviour
    |
    v
Reproduce
    |
    v
Alternative Explanation?
    |
    v
Security Boundary Confirmed
    |
    v
Evidence
    |
    v
Finding
```


# Reporting Example - IDOR/BOLA

Weak:

> Changing `id=1001` to `id=2001` worked.

Better:

> The order API did not enforce object-level authorisation. A session authenticated as controlled Account A could request order `2001`, which belonged to controlled Account B, and the API returned Account B's protected order information. The issue was reproduced using both controlled accounts.


# Reporting Example - Missing Cookie Attribute

Weak:

> HttpOnly is missing.

Better:

> The application's session cookie was issued without the `HttpOnly` attribute. This allows browser-side JavaScript to access the session identifier. The practical risk depends on whether script execution can occur in the application's origin and should therefore be considered together with the application's XSS exposure and session design.


# Reporting Example - CORS

Weak:

> Origin is reflected.

Better:

> The API reflected an untrusted Origin value and permitted credentialed cross-origin access to an authenticated endpoint returning protected account information. Browser-based validation confirmed that a page hosted on the controlled external origin could read the authenticated response.


# Retesting

Retest the underlying security control rather than only checking whether the exact original request changed.


# IDOR Retest

Before:

```text
Account A -> Account B Object -> Allowed
```

After:

```text
Account A -> Account B Object -> Denied
```


# Retest Matrix

| Test | Expected |
|---|---|
| A -> A object | Allowed |
| A -> B object | Denied |
| B -> B object | Allowed |
| B -> A object | Denied |
| Unauthenticated -> protected object | Denied |


# Retest Equivalent Endpoints

If the original issue affected:

```text
GET /api/orders/{id}
```

also consider whether the same authorisation control protects related operations such as:

```text
Update

Download

Export

Delete

Comments

Attachments
```

where these operations are in scope and can be tested safely.


# Common Mistake - No Baseline

Without a baseline:

```text
Unexpected Response
```

is difficult to interpret.

Always understand normal behaviour first.


# Common Mistake - Changing Too Much

Changing:

```text
Method

Token

Cookie

Object ID

Header

Body
```

simultaneously makes the result difficult to attribute.

Change one meaningful variable at a time.


# Common Mistake - Reporting Status Code Only

```text
200
```

does not prove:

```text
Authorisation bypass.
```

You need:

```text
Identity

Ownership

Expected access

Returned protected resource
```


# Common Mistake - Blind Automation

Do not:

```text
Run Scanner
    |
    v
Export Findings
    |
    v
Report Everything
```

Use:

```text
Automation
    |
    v
Candidate
    |
    v
Manual Validation
    |
    v
Finding
```


# Common Mistake - Leaving Intercept On

This often creates:

```text
Browser appears frozen

Requests queue up

Application stops loading
```

Check Proxy interception when troubleshooting.


# Common Mistake - Testing Third Parties

Applications frequently contact:

```text
Analytics

CDNs

Payment providers

Identity providers

External APIs
```

These are not automatically part of the authorised scope.


# Common Mistake - Production Account Damage

Avoid unsafe modifications to:

```text
Real user accounts

Production orders

Financial records

Administrative configuration

Shared resources
```

Prefer dedicated assessment accounts and test data.


# Common Mistake - Not Recording Account Context

A request is much less useful as evidence if you cannot later determine:

```text
Which account sent it?

Which role did it have?

Who owned the object?
```


# Troubleshooting - Browser Has No Internet

Check:

```text
Proxy listener

Proxy address

Proxy port

Intercept status

VPN

DNS
```


# Troubleshooting - HTTPS Certificate Warning

When using a separate assessment browser, ensure the Burp CA certificate is correctly installed for that dedicated browser/profile.

Do not weaken certificate validation outside the assessment environment unnecessarily.


# Troubleshooting - Request Never Reaches Server

Check:

```text
Intercept enabled?

Request waiting in Proxy?

Target reachable?

DNS working?

VPN connected?

Burp upstream proxy configured?
```


# Troubleshooting - Application Behaves Differently Through Burp

Possible causes:

```text
HTTP version

TLS behaviour

Proxy detection

Certificate pinning

WebSocket handling

Timing

Browser profile differences
```


# Troubleshooting - Too Much HTTP History

Use:

```text
Target scope

Display filters

Search

MIME filters

Status filters
```

and remove unrelated traffic from the working view.


# Troubleshooting - Session Keeps Expiring

Check:

```text
Cookie changed?

CSRF token changed?

Access token expired?

Refresh token required?

Application requires workflow state?

Account logged out elsewhere?
```


# Troubleshooting - Repeater Request Fails

Compare against the original Proxy request.

Look for missing:

```text
Cookies

Authorization

CSRF tokens

Content-Type

Origin

Referer

Custom headers

Body fields
```


# Practical Web Assessment Workflow

```text
                         APPLICATION
                              |
                              v
                       NORMAL BROWSING
                              |
                              v
                         HTTP HISTORY
                              |
               +--------------+--------------+
               |                             |
               v                             v
         AUTHENTICATION                  ENDPOINTS
               |                             |
               v                             v
            SESSIONS                      INPUTS
               |                             |
               +--------------+--------------+
                              |
                              v
                           REPEATER
                              |
               +--------------+--------------+
               |              |              |
               v              v              v
          AUTHORIZATION     INPUT          BUSINESS
                           HANDLING         LOGIC
               |              |              |
               +--------------+--------------+
                              |
                              v
                      CONTROLLED TEST
                              |
                              v
                     RESPONSE COMPARISON
                              |
                              v
                         VALIDATION
                              |
                              v
                          EVIDENCE
                              |
                              v
                          REPORTING
```


# Burp Tool Selection

| Question | Tool |
|---|---|
| What requests does the browser make? | Proxy |
| Which endpoints have I visited? | HTTP history / Site map |
| Can I manually change this parameter? | Repeater |
| How does the response change across values? | Intruder |
| How do two responses differ? | Comparer |
| What does this encoded value contain? | Decoder |
| Is this security token sufficiently unpredictable? | Sequencer |
| Did the server make an out-of-band request? | Collaborator |
| What WebSocket messages are exchanged? | WebSockets history |
| Can Burp automate candidate detection? | Scanner |
| Can functionality be extended? | Extensions |


# Assessment Checklist

## Setup

- [ ] Target authorised
- [ ] Scope configured
- [ ] Dedicated assessment browser used
- [ ] Proxy listener confirmed
- [ ] Burp CA configured where needed
- [ ] Test accounts identified
- [ ] Roles documented

## Mapping

- [ ] Application browsed normally
- [ ] Authentication workflow mapped
- [ ] Account settings mapped
- [ ] API endpoints identified
- [ ] Administrative functionality identified
- [ ] Upload/download functionality identified
- [ ] WebSockets identified
- [ ] Third-party services excluded

## Authentication

- [ ] Login baseline captured
- [ ] Failure behaviour reviewed
- [ ] Session creation reviewed
- [ ] Session rotation reviewed
- [ ] Logout invalidation reviewed
- [ ] Password reset reviewed
- [ ] MFA reviewed where applicable
- [ ] Cookie attributes reviewed

## Authorisation

- [ ] Controlled accounts available
- [ ] Ownership documented
- [ ] Own-object baseline established
- [ ] Cross-account access tested
- [ ] Vertical access tested
- [ ] Unauthenticated access tested
- [ ] Related methods considered
- [ ] Related endpoints considered

## Input

- [ ] Parameters identified
- [ ] Headers reviewed
- [ ] JSON fields reviewed
- [ ] File inputs reviewed
- [ ] Redirect parameters reviewed
- [ ] URL-fetching functionality reviewed
- [ ] Client-side restrictions compared with server behaviour

## APIs

- [ ] Authentication reviewed
- [ ] Object authorisation reviewed
- [ ] Function authorisation reviewed
- [ ] Error handling reviewed
- [ ] Content types reviewed
- [ ] Rate limiting reviewed where appropriate
- [ ] GraphQL reviewed where present

## Automation

- [ ] Intruder rate controlled
- [ ] Scanner scope controlled
- [ ] Extension behaviour understood
- [ ] Production impact considered
- [ ] Automated results manually validated

## Evidence

- [ ] Test ID recorded
- [ ] Timestamp recorded
- [ ] Account recorded
- [ ] Role recorded
- [ ] Object ownership recorded
- [ ] Baseline request saved
- [ ] Baseline response saved
- [ ] Modified request saved
- [ ] Modified response saved
- [ ] Sensitive values redacted
- [ ] Security consequence documented

## Retest

- [ ] Original condition retested
- [ ] Legitimate workflow still works
- [ ] Unauthorised workflow denied
- [ ] Related endpoints considered
- [ ] Related methods considered
- [ ] Evidence captured


# Quick Repeater Workflow

```text
Proxy History
     |
     v
Interesting Request
     |
     v
Ctrl+R
     |
     v
Repeater
     |
     v
Send Baseline
     |
     v
Modify One Value
     |
     v
Send
     |
     v
Compare
```


# Quick Authorisation Workflow

```text
Create / Identify Account A
            |
            v
Create / Identify Account B
            |
            v
Document Resource Ownership
            |
            v
A -> A
            |
            v
A -> B
            |
            v
B -> B
            |
            v
B -> A
            |
            v
Unauthenticated Test
            |
            v
Interpret
```


# Quick API Workflow

```text
Capture API Request
       |
       v
Send to Repeater
       |
       v
Establish Baseline
       |
       v
Identify Authentication
       |
       v
Identify Object IDs
       |
       v
Identify Roles
       |
       v
Controlled Modification
       |
       v
Compare Response
       |
       v
Validate Security Boundary
```


# Quick Collaborator Workflow

```text
Generate Collaborator Payload
          |
          v
Place in Controlled Input
          |
          v
Trigger Application Processing
          |
          v
Poll Collaborator
          |
          v
DNS?
HTTP?
Other?
          |
          v
Interpret Interaction
          |
          v
Further Validation
```


# Quick Intruder Workflow

```text
Request
  |
  v
Send to Intruder
  |
  v
Select One Position
  |
  v
Configure Payloads
  |
  v
Control Rate
  |
  v
Run
  |
  v
Sort Status / Length
  |
  v
Investigate Outliers in Repeater
```


# Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| `200 OK` | Request succeeded | Correct authorisation |
| `403` | Request refused | Resource absent |
| `404` | Not-found response | Resource definitely does not exist |
| Different length | Response changed | Vulnerability |
| Different timing | Processing differed | Time-based vulnerability |
| Reflected input | Input appears in response | XSS |
| Origin reflected | CORS reacts to Origin | Exploitable CORS |
| Object ID accepted | Object exists/was processed | IDOR/BOLA |
| DNS Collaborator hit | Hostname resolution occurred | Full SSRF |
| HTTP Collaborator hit | HTTP request occurred | Access to sensitive internal resources |
| 500 response | Server-side error occurred | Exploitability |
| Scanner finding | Automated detection triggered | Confirmed vulnerability |
| Hidden parameter found | Server accepts/recognises input | Security impact |
| Session cookie issued | Session mechanism exists | Secure session management |


# Evidence Quality Model

```text
WEAK EVIDENCE

"Burp returned 200."

        |
        v

STRONG EVIDENCE

Controlled Account
        |
        v
Known Resource Ownership
        |
        v
Baseline Request
        |
        v
Single Controlled Change
        |
        v
Unexpected Protected Response
        |
        v
Reproduction
        |
        v
Security Consequence
```


# Final Testing Principle

Burp Suite is most valuable when it helps turn browser behaviour into a **controlled, reproducible security test**.

Do not stop at:

```text
Interesting Request
       |
       v
Modify Parameter
       |
       v
Interesting Response
```

Continue:

```text
Interesting Request
       |
       v
Understand Normal Behaviour
       |
       v
Identify Security Boundary
       |
       v
Establish Baseline
       |
       v
Modify One Variable
       |
       v
Compare
       |
       v
Reproduce
       |
       v
Rule Out Alternative Explanation
       |
       v
Establish Security Consequence
       |
       v
Capture Evidence
       |
       v
Report
       |
       v
Retest
```

For every important Burp result ask:

```text
Which identity made this request?

What role did the identity have?

Who owns the requested object?

What should the requester be allowed to do?

What did the original request do?

What exactly did I change?

What changed in the response?

Could another explanation produce this result?

Can I reproduce the behaviour?

What security boundary was crossed?

What protected data or action became available?

What evidence proves the conclusion?

What should remediation enforce?

How will I prove the fix during retesting?
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [curl Cheatsheet](curl.md)
- [Nmap Cheatsheet](nmap.md)
- [Wireshark and tshark Cheatsheet](wireshark-tshark.md)
- [Networking Cheatsheet](networking.md)


# Detailed Web Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [Authentication](../web/authentication.md)
- [Authorisation](../web/authorisation.md)
- [Business Logic](../web/business-logic.md)
- [API Security](../web/api-security.md)
- [JWT](../web/jwt.md)
- [OAuth and OIDC](../web/oauth-oidc.md)
- [CORS](../web/cors.md)
- [CSRF](../web/csrf.md)
- [Clickjacking](../web/clickjacking.md)
- [HTML Injection](../web/html-injection.md)
- [Open Redirect](../web/open-redirect.md)
- [Deserialization](../web/deserialization.md)
- [Command Injection](../web/command-injection.md)
- [File Inclusion](../web/file-inclusion.md)
- [Path Traversal](../web/path-traversal.md)
- [File Upload](../web/file-upload.md)
- [SSRF](../web/ssrf.md)
- [SSTI](../web/ssti.md)
- [HTTP Request Smuggling](../web/http-request-smuggling.md)
- [Prototype Pollution](../web/prototype-pollution.md)
- [Host Header Attacks](../web/host-header-attacks.md)
- [GraphQL](../web/graphql.md)


# Recommended Burp Extensions

| Extension | Primary Use |
|---|---|
| Autorize | Authorisation comparison |
| AuthMatrix | Role/access-control matrix testing |
| Logger++ | Enhanced traffic logging |
| JWT Editor | JWT analysis |
| Param Miner | Hidden input discovery |
| HTTP Request Smuggler | HTTP desynchronisation testing |
| Turbo Intruder | Specialised high-performance request workflows |

Always review the extension's current behaviour and permissions before using it during an engagement.


# References

- [PortSwigger Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }
- [Burp Suite Getting Started](https://portswigger.net/burp/documentation/desktop/getting-started){ target="_blank" rel="noopener noreferrer" }
- [Burp Proxy](https://portswigger.net/burp/documentation/desktop/tools/proxy){ target="_blank" rel="noopener noreferrer" }
- [Burp Repeater](https://portswigger.net/burp/documentation/desktop/tools/repeater){ target="_blank" rel="noopener noreferrer" }
- [Burp Intruder](https://portswigger.net/burp/documentation/desktop/tools/intruder){ target="_blank" rel="noopener noreferrer" }
- [Burp Collaborator](https://portswigger.net/burp/documentation/collaborator){ target="_blank" rel="noopener noreferrer" }
- [Burp Sequencer](https://portswigger.net/burp/documentation/desktop/tools/sequencer){ target="_blank" rel="noopener noreferrer" }
- [Burp Decoder](https://portswigger.net/burp/documentation/desktop/tools/decoder){ target="_blank" rel="noopener noreferrer" }
- [Burp Comparer](https://portswigger.net/burp/documentation/desktop/tools/comparer){ target="_blank" rel="noopener noreferrer" }
- [BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }
- [Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [OWASP API Security Project](https://owasp.org/www-project-api-security/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Repeater is your validation workspace"

    HTTP history helps you discover interesting requests. Repeater is where those requests should become controlled experiments with a baseline, one deliberate modification, a comparison and a defensible interpretation.


!!! tip "Use two controlled accounts for authorisation testing"

    A two-account model gives you known resource ownership and expected access boundaries. This produces much stronger IDOR/BOLA evidence than guessing whether an identifier belongs to another real user.


!!! tip "Use automation to find candidates"

    Scanner, Intruder and extensions can help locate interesting behaviour. Move important candidates into Repeater and manually establish the security consequence before reporting them.


!!! warning "Do not treat Collaborator DNS interactions as full SSRF"

    A DNS interaction demonstrates that hostname resolution occurred somewhere in the processing chain. An HTTP interaction provides stronger evidence of server-side HTTP behaviour, but the actual security impact still requires further validation.


!!! warning "Keep third-party systems out of scope"

    Burp will often display requests to analytics providers, identity platforms, payment services, CDNs and other external systems. Their presence in HTTP history does not make those systems part of the authorised assessment scope.
