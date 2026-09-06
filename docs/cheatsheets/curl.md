---
title: curl Cheatsheet
description: Detailed practical curl reference for authorised web application and API security assessments covering HTTP requests, methods, headers, authentication, cookies, redirects, proxies, TLS, APIs, uploads, downloads, debugging, evidence collection and result interpretation.
---

# curl Cheatsheet

`curl` is one of the most useful command-line tools for interacting with HTTP and HTTPS services during security assessments.

It is particularly useful when you need to quickly answer:

```text
Does this endpoint respond?

Which HTTP status code is returned?

Which headers are present?

Where does this redirect?

Does the endpoint require authentication?

How does the server handle different HTTP methods?

What happens when I send JSON?

Which cookies are issued?

Does the behaviour change through a proxy?

Which TLS certificate is presented?

Can I reproduce the request outside the browser?
```

A practical workflow is:

```text
Endpoint
   |
   v
Basic Request
   |
   v
Inspect Status and Headers
   |
   v
Understand Authentication
   |
   v
Reproduce Required Request
   |
   v
Modify One Input
   |
   v
Compare Response
   |
   v
Interpret Behaviour
   |
   v
Validate
   |
   v
Capture Evidence
```

!!! warning "Authorised Security Testing"

    Only send requests to applications, APIs and infrastructure that you are authorised to assess. Avoid destructive methods, excessive request rates, large uploads and state-changing operations unless they are explicitly permitted by the assessment scope.


# Quick Start

Basic request:

```bash
curl https://example.com/
```

Headers only:

```bash
curl -I https://example.com/
```

Verbose request:

```bash
curl -v https://example.com/
```

Follow redirects:

```bash
curl -L https://example.com/
```

Save response:

```bash
curl https://example.com/ -o response.html
```

Ignore certificate validation for an authorised test environment:

```bash
curl -k https://example.com/
```

JSON request:

```bash
curl -X POST https://example.com/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"test","password":"test"}'
```

Proxy through Burp Suite:

```bash
curl -k -x http://127.0.0.1:8080 https://example.com/
```


# Installation

Kali/Debian:

```bash
sudo apt update
sudo apt install curl
```

Check:

```bash
curl --version
```

Locate:

```bash
which curl
```

Help:

```bash
curl --help
```

Full help:

```bash
curl --help all
```

Manual:

```bash
man curl
```


# curl Version

```bash
curl --version
```

Representative output:

```text
curl 8.x.x ...
Protocols: ...
Features: ...
```

Record the locally installed version when behaviour depends on supported protocols or features.


# Basic GET Request

```bash
curl https://example.com/
```

The response body is written to standard output.


# Explicit GET

```bash
curl -X GET https://example.com/
```

Usually this is unnecessary because GET is already the default.

Prefer:

```bash
curl https://example.com/
```

unless explicitly setting the method improves clarity.


# Include Response Headers

```bash
curl -i https://example.com/
```

Representative output:

```text
HTTP/2 200
content-type: text/html
server: nginx
content-length: 1234

<html>
...
```

`-i` includes response headers with the response body.


# Headers Only

```bash
curl -I https://example.com/
```

This sends a HEAD request.

Do not assume HEAD behaves identically to GET.

Some applications:

```text
Disable HEAD

Handle HEAD differently

Return different headers

Route HEAD differently
```


# Better Header Validation

When you specifically need headers from a normal GET request:

```bash
curl -sS -D - -o /dev/null https://example.com/
```

This performs a GET while displaying the response headers.


# Status Code Only

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://example.com/
```

Representative output:

```text
200
```


# Status and Final URL

```bash
curl -s -o /dev/null -w 'Status: %{http_code}\nURL: %{url_effective}\n' -L https://example.com/
```


# Useful Write-Out Fields

```bash
curl -s -o /dev/null \
  -w 'HTTP: %{http_code}\nRemote IP: %{remote_ip}\nContent Type: %{content_type}\nTotal: %{time_total}s\n' \
  https://example.com/
```

Useful variables include:

```text
http_code

url_effective

remote_ip

remote_port

local_ip

content_type

size_download

time_connect

time_starttransfer

time_total
```


# Silent Mode

```bash
curl -s https://example.com/
```

This suppresses progress output.


# Silent but Show Errors

```bash
curl -sS https://example.com/
```

This is usually better for scripts because errors remain visible.


# Fail on HTTP Errors

```bash
curl -f https://example.com/
```

Useful in automation.

Remember that HTTP responses such as:

```text
401

403

404

500
```

may themselves be valuable security-assessment evidence, so do not hide them when investigating application behaviour.


# Verbose Mode

```bash
curl -v https://example.com/
```

Verbose output shows information about:

```text
DNS resolution

TCP connection

TLS negotiation

Request headers

Response headers

Redirect behaviour
```


# Verbose Output Symbols

Typical verbose output uses:

```text
> request data

< response data

* curl diagnostic information
```


# Example

```text
> GET / HTTP/1.1
> Host: example.com
> User-Agent: curl/...
> Accept: */*

< HTTP/1.1 200 OK
< Content-Type: text/html
```

This is useful for understanding exactly what curl sent and received.


# Trace

For deeper troubleshooting:

```bash
curl --trace-ascii trace.txt https://example.com/
```

Be careful:

```text
Trace files may contain credentials.

Trace files may contain cookies.

Trace files may contain tokens.

Trace files may contain sensitive response data.
```

Handle them as assessment evidence.


# Save Response Body

```bash
curl https://example.com/ -o response.html
```


# Preserve Remote Filename

```bash
curl -O https://example.com/file.txt
```

Only use this when you trust the intended output location and filename.


# Headers to File

```bash
curl -D headers.txt https://example.com/ -o response.html
```

This creates separate:

```text
headers.txt

response.html
```


# Complete Evidence Capture

```bash
curl -sS -D headers.txt https://example.com/ -o response.html
```

Then record the exact command separately.


# HTTP Methods

Common methods:

```text
GET

POST

PUT

PATCH

DELETE

HEAD

OPTIONS
```


# OPTIONS

```bash
curl -i -X OPTIONS https://example.com/api/users
```

Possible response:

```text
Allow: GET, POST, OPTIONS
```

Do not assume the `Allow` header completely describes application authorisation.


# POST Form Data

```bash
curl -X POST https://example.com/login \
  -d 'username=test&password=test'
```

`curl` automatically uses:

```text
application/x-www-form-urlencoded
```

for standard `-d` form data unless overridden.


# POST JSON

```bash
curl https://example.com/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"test","password":"test"}'
```

Using `-d` causes curl to use POST unless another method is explicitly specified.


# JSON with Accept Header

```bash
curl https://example.com/api/users \
  -H 'Accept: application/json'
```


# PUT

For a non-destructive authorised endpoint:

```bash
curl -X PUT https://example.com/api/profile \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"Test User"}'
```

Only use state-changing methods where explicitly authorised.


# PATCH

```bash
curl -X PATCH https://example.com/api/profile \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"Test User"}'
```


# DELETE

Syntax:

```bash
curl -X DELETE https://example.com/api/resource/123
```

!!! warning "State-Changing Request"
    Do not send DELETE requests to real application objects unless the assessment explicitly permits destructive testing and the target object is safe to remove.


# Custom Header

```bash
curl https://example.com/ \
  -H 'X-Test: authorised-assessment'
```


# Multiple Headers

```bash
curl https://example.com/api/users \
  -H 'Accept: application/json' \
  -H 'X-Test: authorised-assessment'
```


# User-Agent

```bash
curl https://example.com/ \
  -A 'Authorised-Security-Assessment'
```

Equivalent:

```bash
curl https://example.com/ \
  -H 'User-Agent: Authorised-Security-Assessment'
```


# Referer

```bash
curl https://example.com/ \
  -e 'https://example.com/'
```


# Host Header

```bash
curl http://192.0.2.10/ \
  -H 'Host: app.example.com'
```

This is useful when testing:

```text
Virtual hosting

Reverse proxies

Load balancers

Applications behind shared IP addresses
```

Do not automatically interpret a changed response as a Host-header vulnerability.


# Virtual Host Validation

Suppose:

```bash
curl http://192.0.2.10/
```

returns:

```text
Default server
```

while:

```bash
curl http://192.0.2.10/ -H 'Host: portal.example.com'
```

returns:

```text
Application login page
```

Interpretation:

```text
The web server uses Host-based virtual hosting.
```

This is expected behaviour in many environments.


# Resolve Hostname to Specific IP

A better option for HTTPS virtual-host testing is often:

```bash
curl --resolve app.example.com:443:192.0.2.10 https://app.example.com/
```

This preserves:

```text
URL hostname

Host header

TLS SNI hostname
```

while connecting to the specified IP.


# Why `--resolve` Is Useful

Compare:

```bash
curl https://192.0.2.10/ -H 'Host: app.example.com'
```

with:

```bash
curl --resolve app.example.com:443:192.0.2.10 https://app.example.com/
```

The second approach better represents a normal HTTPS request to:

```text
app.example.com
```

because TLS SNI also uses the hostname.


# Redirects

Without `-L`:

```bash
curl -i http://example.com/
```

Possible:

```text
HTTP/1.1 301 Moved Permanently
Location: https://example.com/
```

Follow:

```bash
curl -L http://example.com/
```


# Show Redirect Chain

```bash
curl -sS -D - -o /dev/null -L http://example.com/
```

This helps identify:

```text
HTTP -> HTTPS

Login redirects

Canonical-host redirects

Application routing
```


# Do Not Hide Redirects Too Early

If investigating redirect behaviour, first inspect without:

```text
-L
```

Otherwise the original:

```text
301

302

303

307

308
```

may be less obvious.


# Cookies

Send cookie:

```bash
curl https://example.com/ \
  -b 'session=examplevalue'
```


# Multiple Cookies

```bash
curl https://example.com/ \
  -b 'session=examplevalue; preference=dark'
```


# Save Cookies

```bash
curl -c cookies.txt https://example.com/login
```


# Load Cookies

```bash
curl -b cookies.txt https://example.com/profile
```


# Save and Reuse Cookies

```bash
curl -c cookies.txt -b cookies.txt https://example.com/
```


# Cookie Workflow

```text
Login
  |
  v
Receive Set-Cookie
  |
  v
Store Cookie Jar
  |
  v
Authenticated Request
  |
  v
Observe Authorisation
```


# Cookie Security Attributes

Look for:

```text
Secure

HttpOnly

SameSite

Path

Domain

Expires

Max-Age
```

Example:

```text
Set-Cookie: session=...; Secure; HttpOnly; SameSite=Lax
```


# Authentication

curl supports several authentication mechanisms.


# Basic Authentication

```bash
curl -u 'testuser:testpassword' https://example.com/
```

Be careful:

```text
Credentials may appear in shell history.

Credentials may appear in process information.

Credentials may be captured in evidence.
```


# Prompt for Password

Safer than embedding the password:

```bash
curl -u testuser https://example.com/
```

curl can prompt for the password.


# Bearer Token

```bash
curl https://example.com/api/profile \
  -H 'Authorization: Bearer <token>'
```


# API Key Header

Example:

```bash
curl https://example.com/api/data \
  -H 'X-API-Key: <api-key>'
```

The exact header depends on the application.


# Avoid Publishing Real Tokens

Documentation and screenshots should use:

```text
<token>

<api-key>

<session-cookie>
```

rather than real credentials.


# Proxy Through Burp Suite

HTTP:

```bash
curl -x http://127.0.0.1:8080 http://example.com/
```

HTTPS:

```bash
curl -k -x http://127.0.0.1:8080 https://example.com/
```


# Burp Workflow

```text
curl
 |
 v
Burp Proxy
 |
 v
Target
 |
 v
Burp HTTP History
```

This is useful when:

```text
Reproducing CLI requests

Comparing curl with browser behaviour

Modifying requests in Repeater

Capturing evidence
```


# Environment Proxy

```bash
export HTTP_PROXY=http://127.0.0.1:8080
export HTTPS_PROXY=http://127.0.0.1:8080
```

Remove:

```bash
unset HTTP_PROXY
unset HTTPS_PROXY
```


# Check Proxy Variables

```bash
env | grep -i proxy
```


# Ignore Proxy for Target

```bash
curl --noproxy '*' https://example.com/
```

Useful when environment proxy variables unexpectedly affect testing.


# TLS

HTTPS request:

```bash
curl https://example.com/
```


# Certificate Validation Failure

You may see:

```text
SSL certificate problem
```

Possible reasons:

```text
Self-signed certificate

Expired certificate

Hostname mismatch

Untrusted CA

Incomplete certificate chain
```


# Ignore TLS Validation

For an authorised test environment:

```bash
curl -k https://example.com/
```

or:

```bash
curl --insecure https://example.com/
```

!!! warning "Do Not Normalise `-k`"
    `-k` is useful in labs and assessment environments, but it disables certificate verification. A request succeeding with `-k` does not mean the certificate configuration is valid.


# Inspect TLS Verbosely

```bash
curl -v https://example.com/
```

This can expose useful TLS and certificate information.


# TLS Version

Where supported by the target and local curl build:

```bash
curl --tlsv1.2 https://example.com/
```

Minimum TLS 1.3:

```bash
curl --tlsv1.3 https://example.com/
```

Use dedicated TLS tooling for comprehensive cipher/protocol analysis.


# Client Certificate

Where the assessment provides an authorised client certificate:

```bash
curl --cert client.pem --key client.key https://example.com/
```

Protect private-key material carefully.


# Custom CA

```bash
curl --cacert assessment-ca.pem https://example.com/
```

This is preferable to `-k` when you have the appropriate CA certificate.


# HTTP Protocol Version

Force HTTP/1.1:

```bash
curl --http1.1 https://example.com/
```

Request HTTP/2:

```bash
curl --http2 https://example.com/
```

Availability depends on the local curl build and server capabilities.


# HTTP Version Comparison

Useful workflow:

```text
HTTP/1.1
   |
   v
Observe Behaviour

HTTP/2
   |
   v
Observe Behaviour

Compare
```

Differences may result from:

```text
Reverse proxy

CDN

Load balancer

Protocol-specific routing

Application gateway
```

Do not automatically interpret differences as vulnerabilities.


# DNS

Show resolution and connection details:

```bash
curl -v https://example.com/
```

Resolve manually:

```bash
getent hosts example.com
```

or:

```bash
dig example.com
```


# Force IPv4

```bash
curl -4 https://example.com/
```


# Force IPv6

```bash
curl -6 https://example.com/
```


# Test Different Backend IPs

Suppose:

```text
app.example.com

192.0.2.10

192.0.2.11
```

Test first backend:

```bash
curl --resolve app.example.com:443:192.0.2.10 https://app.example.com/
```

Second:

```bash
curl --resolve app.example.com:443:192.0.2.11 https://app.example.com/
```

This can help identify backend inconsistencies where those IPs are within scope.


# API Testing

curl is particularly useful for APIs because requests can be precisely reproduced.


# GET JSON

```bash
curl -sS https://example.com/api/users \
  -H 'Accept: application/json'
```


# Pretty Print JSON with jq

```bash
curl -sS https://example.com/api/users | jq
```


# POST JSON

```bash
curl -sS https://example.com/api/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test User"}'
```


# JSON from File

```bash
curl https://example.com/api/users \
  -H 'Content-Type: application/json' \
  --data-binary @request.json
```


# Why File-Based Requests Help

For larger bodies:

```text
request.json
```

is easier to:

```text
Version

Review

Repeat

Modify

Preserve as evidence
```

than a large inline shell string.


# Form Submission

```bash
curl https://example.com/login \
  -d 'username=test&password=test'
```


# Multipart Form

```bash
curl https://example.com/profile \
  -F 'displayName=Test User'
```


# File Upload

For an authorised upload test:

```bash
curl https://example.com/upload \
  -F 'file=@test.txt'
```

Add another field:

```bash
curl https://example.com/upload \
  -F 'description=Assessment test file' \
  -F 'file=@test.txt'
```

Use harmless assessment files unless the scope specifically requires another controlled test case.


# Specify Multipart Content Type

```bash
curl https://example.com/upload \
  -F 'file=@test.txt;type=text/plain'
```


# Download File

```bash
curl https://example.com/files/test.pdf -o test.pdf
```

Check:

```bash
file test.pdf
```

Hash:

```bash
sha256sum test.pdf
```


# Resume Download

```bash
curl -C - https://example.com/large-file.zip -o large-file.zip
```


# API Authorisation Testing

curl is useful for controlled two-account authorisation testing.

Example:

```text
Account A owns object 1001

Account B owns object 2001
```


# Baseline - Account A Own Object

```bash
curl -i https://example.com/api/orders/1001 \
  -H 'Authorization: Bearer <account-a-token>'
```

Expected:

```text
200 OK
```


# Cross-Account Test

```bash
curl -i https://example.com/api/orders/2001 \
  -H 'Authorization: Bearer <account-a-token>'
```

Secure behaviour might be:

```text
403 Forbidden
```

or:

```text
404 Not Found
```

depending on application design.


# Authorisation Interpretation

If Account A receives Account B's protected object:

```text
Controlled Account A
        |
        v
Request Object B
        |
        v
Protected Data Returned
        |
        v
Confirm Object Ownership
        |
        v
Reproduce
        |
        v
Authorisation Failure
```

The important evidence is not simply:

```text
HTTP 200
```

but:

```text
User A was not authorised to access object B, yet the application returned B's protected data.
```


# Compare Responses

Save baseline:

```bash
curl -sS https://example.com/api/orders/1001 \
  -H 'Authorization: Bearer <account-a-token>' \
  -o account-a-own.json
```

Cross-account:

```bash
curl -sS https://example.com/api/orders/2001 \
  -H 'Authorization: Bearer <account-a-token>' \
  -o account-a-other.json
```

Compare:

```bash
diff -u account-a-own.json account-a-other.json
```


# Response Size

```bash
curl -s -o /dev/null -w '%{size_download}\n' https://example.com/
```

Response-size differences can help identify behavioural changes, but size alone is not proof of a security issue.


# Timing

```bash
curl -s -o /dev/null -w '%{time_total}\n' https://example.com/
```

More detailed:

```bash
curl -s -o /dev/null \
  -w 'DNS: %{time_namelookup}\nConnect: %{time_connect}\nTTFB: %{time_starttransfer}\nTotal: %{time_total}\n' \
  https://example.com/
```


# Timing Interpretation

Response timing can be affected by:

```text
Network latency

Application load

Caching

Database load

CDN

Rate limiting

Backend selection

TLS negotiation
```

Do not infer a vulnerability from a single slow request.


# Repeat Timing Tests

Where timing matters, collect multiple controlled observations rather than comparing only one request against another.


# Security Headers

Quick check:

```bash
curl -sS -D - -o /dev/null https://example.com/
```

Review headers such as:

```text
Content-Security-Policy

Strict-Transport-Security

X-Content-Type-Options

Referrer-Policy

Permissions-Policy

Set-Cookie

Cache-Control
```


# Header Absence Is Contextual

Do not automatically report every missing security header.

Consider:

```text
Application type

Response content

Browser exposure

Existing equivalent controls

Threat model
```


# HSTS

Check:

```bash
curl -sS -D - -o /dev/null https://example.com/ | grep -i strict-transport-security
```

A missing HSTS header may be relevant for browser-facing HTTPS applications but must be assessed in context.


# CSP

```bash
curl -sS -D - -o /dev/null https://example.com/ | grep -i content-security-policy
```

Presence of CSP does not mean the policy is strong.

The policy itself requires review.


# CORS

Send an Origin header:

```bash
curl -i https://example.com/api/profile \
  -H 'Origin: https://example.invalid'
```

Review:

```text
Access-Control-Allow-Origin

Access-Control-Allow-Credentials

Vary
```


# CORS Preflight

```bash
curl -i -X OPTIONS https://example.com/api/profile \
  -H 'Origin: https://example.invalid' \
  -H 'Access-Control-Request-Method: GET'
```

Do not conclude CORS exploitation solely from a reflected origin.

Consider:

```text
Credentials

Browser behaviour

Sensitive response

Allowed methods

Allowed headers
```


# Cache Behaviour

Headers:

```bash
curl -sS -D - -o /dev/null https://example.com/
```

Review:

```text
Cache-Control

Age

ETag

Expires

Vary

Via

X-Cache
```

Header names vary by infrastructure.


# Conditional Request

If an ETag is returned:

```bash
curl -i https://example.com/resource \
  -H 'If-None-Match: "<etag>"'
```

Possible:

```text
304 Not Modified
```


# Content Types

Check:

```bash
curl -sS -D - -o /dev/null https://example.com/
```

Look for:

```text
Content-Type
```

Do not rely only on file extensions to determine response type.


# Compression

Request compressed content:

```bash
curl --compressed https://example.com/
```

This tells curl to request supported compression and decompress the response.


# Range Requests

Request first 100 bytes:

```bash
curl -H 'Range: bytes=0-99' https://example.com/file.bin
```

Possible response:

```text
206 Partial Content
```

Useful when validating download behaviour.


# Basic Reconnaissance

A quick web-service triage:

```bash
curl -k -sS -D - -o /dev/null https://example.com/
```

Then:

```bash
curl -k -v https://example.com/
```

Then inspect the body:

```bash
curl -k -sS https://example.com/
```


# Nmap to curl Workflow

```text
Nmap
 |
 v
443/tcp open
 |
 v
curl
 |
 +--> Status
 +--> Headers
 +--> Redirect
 +--> TLS
 +--> Application Response
 |
 v
Browser / Burp
```

Example:

```bash
nmap -sV -p 443 192.0.2.10
```

Then:

```bash
curl -k -v https://192.0.2.10/
```


# Virtual Host Workflow

```text
IP Address
    |
    v
Default Response
    |
    v
Known Hostname
    |
    v
--resolve
    |
    v
Application Response
```

Example:

```bash
curl --resolve portal.example.com:443:192.0.2.10 \
  https://portal.example.com/
```


# Burp to curl Workflow

A request identified in Burp can often be reproduced with curl.

Conceptually:

```text
Burp Request
     |
     v
Method
     |
     v
URL
     |
     v
Headers
     |
     v
Cookies / Token
     |
     v
Body
     |
     v
curl
```

This is useful for:

```text
Reproduction

Automation

Evidence

Response comparison
```


# curl to Burp Workflow

```bash
curl -k -x http://127.0.0.1:8080 \
  https://example.com/api/profile \
  -H 'Authorization: Bearer <token>'
```

The request can then be examined and sent to Repeater.


# Request from File

Body:

```bash
curl https://example.com/api/test \
  -H 'Content-Type: application/json' \
  --data-binary @request.json
```

Headers can also be managed carefully in scripts when repeated testing is required.


# Preserve Exact Body

`--data-binary` is useful when the exact body should be sent without `-d` style transformations:

```bash
curl https://example.com/api/test \
  --data-binary @request.bin
```


# URL Encoding

Encode form value:

```bash
curl https://example.com/search \
  --data-urlencode 'q=test value'
```

For GET query construction:

```bash
curl -G https://example.com/search \
  --data-urlencode 'q=test value'
```

This produces an encoded query parameter.


# Multiple Query Parameters

```bash
curl -G https://example.com/search \
  --data-urlencode 'q=test value' \
  --data-urlencode 'page=1'
```


# Why `-G` Is Useful

Without `-G`, `-d` normally creates a request body.

With:

```text
-G
```

the data is appended to the URL query string.


# Request Timeout

Maximum total time:

```bash
curl --max-time 10 https://example.com/
```

Connection timeout:

```bash
curl --connect-timeout 5 https://example.com/
```


# Retry

```bash
curl --retry 3 https://example.com/
```

Use retries carefully during testing because repeated requests can alter:

```text
Rate limiting

Lockout behaviour

Application state

Monitoring
```


# Rate Limiting Observation

Suppose repeated authorised requests produce:

```text
200

200

200

429
```

This supports the observation that the application is applying some form of request-rate control.

It does not automatically prove:

```text
The rate limit is secure.

The rate limit cannot be bypassed.

The limit applies across accounts/IPs/endpoints.
```


# HTTP 401

```text
401 Unauthorized
```

typically indicates authentication is required or authentication failed.

Inspect:

```text
WWW-Authenticate
```

where present.


# HTTP 403

```text
403 Forbidden
```

typically means the server understood the request but refused it.

Do not assume:

```text
Resource does not exist.
```


# HTTP 404

```text
404 Not Found
```

may mean:

```text
Resource absent

Routing rejected

Authorisation intentionally hidden

Application custom behaviour
```

Compare controlled requests before drawing conclusions.


# HTTP 405

```text
405 Method Not Allowed
```

suggests the requested method is not supported for the resource.

Check:

```text
Allow
```

where provided.


# HTTP 429

```text
429 Too Many Requests
```

indicates rate limiting or request throttling.

Review:

```text
Retry-After
```

where present.


# HTTP 500

```text
500 Internal Server Error
```

does not automatically indicate exploitable behaviour.

It may reveal:

```text
Unhandled exception

Application bug

Backend failure

Invalid input handling
```

Review the response carefully for unnecessary internal information.


# Response Comparison Model

When testing an input:

```text
Baseline Request
      |
      v
Baseline Response
      |
      v
Change One Variable
      |
      v
Modified Response
      |
      v
Compare
      |
      v
Explain Difference
```

Avoid changing several parameters simultaneously because this makes causality harder to establish.


# Good Controlled Comparison

Baseline:

```bash
curl -i 'https://example.com/api/items/1001' \
  -H 'Authorization: Bearer <token>'
```

Modified:

```bash
curl -i 'https://example.com/api/items/1002' \
  -H 'Authorization: Bearer <token>'
```

Only the object identifier changes.


# Poor Comparison

Changing:

```text
Object ID

Token

User-Agent

Method

Content-Type

Body
```

all at once makes the result difficult to interpret.


# Common Mistake - Always Using `-k`

Problem:

```text
Certificate problems become invisible.
```

Better:

```text
Try normal certificate validation first.

Use -k only when the assessment requires bypassing trust validation.
```


# Common Mistake - Always Using `-L`

Problem:

```text
Important redirect behaviour may be hidden.
```

Better:

```text
Inspect the original response first.
```


# Common Mistake - Using `-I` as GET Evidence

Problem:

```text
-I performs HEAD.
```

Better for GET response headers:

```bash
curl -sS -D - -o /dev/null https://example.com/
```


# Common Mistake - Explicit `-X POST` with `-d`

This works:

```bash
curl -X POST https://example.com/api \
  -d 'a=b'
```

but `-d` already selects POST in ordinary usage.

Simpler:

```bash
curl https://example.com/api \
  -d 'a=b'
```


# Common Mistake - Reporting Server Header as Confirmed Version

Response:

```text
Server: nginx
```

or a version-bearing banner may be:

```text
Modified

Hidden

Proxied

Generated by an intermediary
```

Use it as supporting evidence rather than unquestionable product identification.


# Common Mistake - Exposing Secrets in Shell History

Avoid:

```bash
curl -H 'Authorization: Bearer REAL_SECRET_TOKEN' ...
```

when working with sensitive production credentials if safer alternatives are available.

Be conscious of:

```text
Shell history

Terminal recordings

Screenshots

Process lists

Shared logs
```


# Environment Variables for Test Tokens

For temporary authorised testing:

```bash
export TEST_TOKEN='<token>'
```

Then:

```bash
curl https://example.com/api/profile \
  -H "Authorization: Bearer $TEST_TOKEN"
```

Remove:

```bash
unset TEST_TOKEN
```

This reduces repeated token exposure in copied commands, although environment variables themselves are not a universal secret-storage solution.


# Common Mistake - Confusing Network and Application Errors

Example:

```text
Connection refused
```

is different from:

```text
HTTP/1.1 403 Forbidden
```

The first is primarily a connection/service observation.

The second is an application/protocol response.


# Troubleshooting - Could Not Resolve Host

Example:

```text
curl: (6) Could not resolve host
```

Check:

```bash
getent hosts example.com
```

```bash
dig example.com
```

If testing a known in-scope backend:

```bash
curl --resolve example.com:443:192.0.2.10 https://example.com/
```


# Troubleshooting - Connection Refused

Check:

```bash
nmap -p 443 example.com
```

or:

```bash
nc -vz example.com 443
```

Possible causes:

```text
Service not listening

Wrong port

Firewall rejection

Wrong IP

Service stopped
```


# Troubleshooting - Timeout

```bash
curl --connect-timeout 5 --max-time 10 https://example.com/
```

Then investigate:

```text
DNS

Routing

Firewall

Proxy

VPN

Service health
```


# Troubleshooting - Certificate Error

Use verbose mode:

```bash
curl -v https://example.com/
```

Inspect:

```text
Hostname

Issuer

Trust

Validity

Certificate chain
```

Use `-k` only when bypassing certificate validation is appropriate for the test.


# Troubleshooting - Wrong Application

If the IP hosts multiple sites:

```bash
curl --resolve app.example.com:443:192.0.2.10 https://app.example.com/
```

This often resolves virtual-host/SNI issues.


# Troubleshooting - Proxy Unexpectedly Used

Check:

```bash
env | grep -i proxy
```

Bypass:

```bash
curl --noproxy '*' https://example.com/
```


# Troubleshooting - HTTP vs HTTPS

Test HTTP:

```bash
curl -v http://example.com/
```

HTTPS:

```bash
curl -v https://example.com/
```

The HTTP endpoint may simply redirect to HTTPS.


# Evidence Collection

For an important HTTP test record:

```text
Test ID

Timestamp

Source IP

Target hostname

Target IP where relevant

URL

Method

Authentication context

Request headers

Request body where relevant

Response status

Response headers

Relevant response body

curl version

Exact command

Interpretation
```


# Example Evidence Record

```text
Test ID:
WEB-CURL-007

Timestamp:
2026-09-06 18:45 UTC

Tool:
curl

Target:
https://portal.example.com/api/orders/2001

Method:
GET

Authentication:
Controlled Account A

Objective:
Determine whether Account A can access an object belonging
to controlled Account B.

Baseline:
Account A successfully accessed its own object 1001.

Test:
Account A requested Account B object 2001.

Result:
HTTP 200 returned with Account B order details.

Interpretation:
The application did not enforce the expected object-level
authorisation boundary between the two controlled accounts.
```


# Reporting

Do not report:

> curl returned HTTP 200.

Report the underlying security condition.

Example:

> The API did not enforce object-level authorisation when accessing order resources. A session authenticated as controlled Account A could request the identifier of an order belonging to controlled Account B and receive the protected order details.


# Evidence Quality

Weak:

```text
Screenshot of terminal showing 200.
```

Better:

```text
Controlled account ownership documented.

Baseline request preserved.

Modified request preserved.

Response preserved.

Only object identifier changed.

Protected data identified.

Behaviour reproduced.
```


# Retesting

Use the same controlled test after remediation.

Before:

```text
Account A -> Object B -> 200 + protected data
```

After:

```text
Account A -> Object B -> 403
```

or another intentionally secure response.


# Retest Example

```bash
curl -i https://example.com/api/orders/2001 \
  -H 'Authorization: Bearer <account-a-token>'
```

Expected after remediation:

```text
HTTP/1.1 403 Forbidden
```

or an application-designed equivalent.


# Retest More Than Status

Do not validate only:

```text
Status changed from 200 to 403.
```

Also confirm:

```text
Protected data absent

Alternative methods denied

Equivalent endpoints protected

Account A still accesses own object

Account B still accesses own object
```


# API Retest Matrix

| Test | Expected |
|---|---|
| A -> A object | Allowed |
| A -> B object | Denied |
| B -> B object | Allowed |
| B -> A object | Denied |
| Unauthenticated -> A | Denied |


# curl and jq

Pretty print:

```bash
curl -sS https://example.com/api/data | jq
```

Specific field:

```bash
curl -sS https://example.com/api/data | jq '.id'
```

Array:

```bash
curl -sS https://example.com/api/users | jq '.[].username'
```

Use only when the response is valid JSON.


# curl and grep

Headers:

```bash
curl -sS -D - -o /dev/null https://example.com/ | grep -i server
```

Cookies:

```bash
curl -sS -D - -o /dev/null https://example.com/ | grep -i set-cookie
```

Security headers:

```bash
curl -sS -D - -o /dev/null https://example.com/ | grep -Ei 'content-security-policy|strict-transport-security|x-content-type-options'
```


# curl and diff

Baseline:

```bash
curl -sS https://example.com/api/item/1001 -o baseline.txt
```

Modified:

```bash
curl -sS https://example.com/api/item/1002 -o modified.txt
```

Compare:

```bash
diff -u baseline.txt modified.txt
```


# curl and sha256sum

Download:

```bash
curl -sS https://example.com/file.bin -o file.bin
```

Hash:

```bash
sha256sum file.bin
```

Useful for evidence integrity and file comparison.


# curl and Nmap

```text
Nmap
  |
  v
Find Web Port
  |
  v
curl
  |
  v
Protocol Triage
  |
  v
Burp Suite
  |
  v
Application Testing
```

See [Nmap Cheatsheet](nmap.md).


# curl and Burp Suite

```text
curl
 |
 v
Burp Proxy
 |
 v
Repeater
 |
 v
Controlled Modification
 |
 v
Response Comparison
```

This is particularly useful for APIs and requests originally identified outside the browser.


# curl and Web Notes

After initial curl triage, continue with the detailed [Web Application Security Notes](../web/index.md) for application-specific testing.


# Quick Reference

## GET

```bash
curl https://example.com/
```

## Headers and Body

```bash
curl -i https://example.com/
```

## GET Headers Only

```bash
curl -sS -D - -o /dev/null https://example.com/
```

## HEAD

```bash
curl -I https://example.com/
```

## Verbose

```bash
curl -v https://example.com/
```

## Follow Redirects

```bash
curl -L https://example.com/
```

## Ignore Certificate Validation

```bash
curl -k https://example.com/
```

## Status Only

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://example.com/
```

## Save Body

```bash
curl https://example.com/ -o response.html
```

## Save Headers

```bash
curl -D headers.txt https://example.com/ -o response.html
```

## Custom Header

```bash
curl https://example.com/ -H 'X-Test: authorised-assessment'
```

## Basic Authentication

```bash
curl -u testuser https://example.com/
```

## Bearer Token

```bash
curl https://example.com/api/profile \
  -H 'Authorization: Bearer <token>'
```

## Cookie

```bash
curl https://example.com/ -b 'session=<value>'
```

## Cookie Jar

```bash
curl -c cookies.txt -b cookies.txt https://example.com/
```

## POST Form

```bash
curl https://example.com/login \
  -d 'username=test&password=test'
```

## POST JSON

```bash
curl https://example.com/api/test \
  -H 'Content-Type: application/json' \
  -d '{"test":"value"}'
```

## JSON File

```bash
curl https://example.com/api/test \
  -H 'Content-Type: application/json' \
  --data-binary @request.json
```

## Multipart

```bash
curl https://example.com/upload \
  -F 'file=@test.txt'
```

## Burp Proxy

```bash
curl -k -x http://127.0.0.1:8080 https://example.com/
```

## Resolve Host to IP

```bash
curl --resolve app.example.com:443:192.0.2.10 https://app.example.com/
```

## IPv4

```bash
curl -4 https://example.com/
```

## IPv6

```bash
curl -6 https://example.com/
```

## HTTP/1.1

```bash
curl --http1.1 https://example.com/
```

## HTTP/2

```bash
curl --http2 https://example.com/
```

## Timeout

```bash
curl --connect-timeout 5 --max-time 10 https://example.com/
```


# HTTP Status Quick Reference

| Status | General Meaning | Assessment Question |
|---:|---|---|
| `200` | Request succeeded | Was the requester authorised? |
| `201` | Resource created | Was creation permitted? |
| `204` | Success, no body | Did state change as expected? |
| `301` | Permanent redirect | Where does it redirect? |
| `302` | Redirect | Is destination controlled/expected? |
| `307` | Temporary redirect preserving method | Is method/body preserved safely? |
| `308` | Permanent redirect preserving method | Is destination expected? |
| `400` | Bad request | Does response expose internals? |
| `401` | Authentication required/failed | Which authentication scheme? |
| `403` | Request refused | Is authorisation enforced consistently? |
| `404` | Resource not found/hidden | Does behaviour differ by authorisation? |
| `405` | Method not allowed | Which methods are actually accepted? |
| `409` | Conflict | What state caused conflict? |
| `415` | Unsupported media type | Which content types are accepted? |
| `429` | Too many requests | How is throttling scoped? |
| `500` | Server error | Is sensitive diagnostic information exposed? |
| `502` | Bad gateway | Which intermediary failed? |
| `503` | Service unavailable | Temporary failure or backend issue? |


# Header Quick Reference

| Header | Why Review It |
|---|---|
| `Location` | Redirect destination |
| `Set-Cookie` | Session and cookie controls |
| `WWW-Authenticate` | Authentication mechanism |
| `Content-Type` | Response interpretation |
| `Content-Length` | Response comparison |
| `Content-Security-Policy` | Browser content restrictions |
| `Strict-Transport-Security` | HTTPS enforcement |
| `Access-Control-Allow-Origin` | CORS behaviour |
| `Access-Control-Allow-Credentials` | Credentialed CORS |
| `Cache-Control` | Caching behaviour |
| `Vary` | Cache/proxy behaviour |
| `Server` | Possible technology clue |
| `Allow` | Advertised HTTP methods |


# curl Option Quick Reference

| Option | Purpose |
|---|---|
| `-s` | Silent |
| `-S` | Show errors with silent mode |
| `-i` | Include response headers |
| `-I` | HEAD request |
| `-v` | Verbose |
| `-L` | Follow redirects |
| `-k` | Disable TLS certificate verification |
| `-H` | Add header |
| `-d` | Send request data |
| `--data-binary` | Send data without normal form-style processing |
| `-F` | Multipart form |
| `-b` | Send/read cookies |
| `-c` | Save cookies |
| `-u` | Authentication credentials |
| `-x` | Proxy |
| `-o` | Output file |
| `-O` | Remote filename |
| `-D` | Save response headers |
| `-w` | Write selected metadata |
| `-G` | Put data in URL query |
| `--resolve` | Override hostname resolution |
| `--connect-timeout` | Connection timeout |
| `--max-time` | Maximum total request time |
| `-4` | IPv4 |
| `-6` | IPv6 |


# Result Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| `200 OK` | Request succeeded | Request was authorised correctly |
| `301/302` | Redirect occurred | Redirect is vulnerable |
| `401` | Authentication challenge/failure | Endpoint is securely protected |
| `403` | Request refused | Resource does not exist |
| `404` | Not-found style response | Object definitely absent |
| `500` | Server-side failure | Exploitable vulnerability |
| `Set-Cookie` present | Server issued cookie | Cookie security is sufficient |
| CSP present | CSP configured | CSP is effective |
| CORS origin reflected | CORS behaviour depends on Origin | Sensitive cross-origin access is exploitable |
| `Server` header | Technology clue | Exact software/patch level |
| Request works with `-k` | TLS connection succeeds without verification | Certificate is valid |
| Different response size | Behaviour changed | Security boundary bypassed |


# Practical Web Assessment Workflow

```text
                         TARGET URL
                             |
                             v
                        BASIC GET
                             |
                             v
                    STATUS + HEADERS
                             |
              +--------------+--------------+
              |                             |
              v                             v
          REDIRECT                      RESPONSE
              |                             |
              v                             v
       FOLLOW DELIBERATELY            IDENTIFY TYPE
              |                             |
              +--------------+--------------+
                             |
                             v
                       AUTHENTICATION
                             |
                             v
                     CONTROLLED SESSION
                             |
                             v
                         BASELINE
                             |
                             v
                    MODIFY ONE INPUT
                             |
                             v
                    COMPARE RESPONSE
                             |
                             v
                       INTERPRET
                             |
                             v
                        VALIDATE
                             |
                             v
                         EVIDENCE
```


# curl Assessment Checklist

## Preparation

- [ ] Target authorised
- [ ] Endpoint authorised
- [ ] Test account identified
- [ ] State-changing operations understood
- [ ] Proxy configuration understood
- [ ] TLS requirements understood

## Initial Request

- [ ] HTTP status recorded
- [ ] Response headers reviewed
- [ ] Response body reviewed
- [ ] Redirect behaviour reviewed
- [ ] Content type reviewed
- [ ] Server clues recorded carefully

## Authentication

- [ ] Authentication mechanism identified
- [ ] Controlled credentials used
- [ ] Cookies handled safely
- [ ] Tokens handled safely
- [ ] Unauthenticated behaviour compared
- [ ] Authentication failures interpreted correctly

## Authorisation

- [ ] Own-object baseline established
- [ ] Controlled second account used where possible
- [ ] One identifier changed at a time
- [ ] Protected response data identified
- [ ] Cross-account behaviour reproduced
- [ ] Alternative methods considered where appropriate

## Headers

- [ ] Cookie attributes reviewed
- [ ] CSP reviewed where relevant
- [ ] HSTS reviewed where relevant
- [ ] CORS reviewed where relevant
- [ ] Cache controls reviewed
- [ ] Redirect destination reviewed

## API

- [ ] Correct Content-Type used
- [ ] GET reviewed
- [ ] POST reviewed where authorised
- [ ] PUT/PATCH reviewed where authorised
- [ ] DELETE avoided unless explicitly safe
- [ ] JSON responses preserved
- [ ] Error handling reviewed

## TLS

- [ ] Normal validation attempted
- [ ] Certificate errors recorded
- [ ] `-k` used only when necessary
- [ ] SNI/hostname behaviour considered
- [ ] `--resolve` used where appropriate

## Evidence

- [ ] Timestamp recorded
- [ ] Target recorded
- [ ] Account context recorded
- [ ] Method recorded
- [ ] Exact request preserved
- [ ] Relevant response preserved
- [ ] Secrets redacted
- [ ] Interpretation documented

## Retest

- [ ] Original request repeated
- [ ] Baseline still functions
- [ ] Unauthorised case denied
- [ ] Protected data absent
- [ ] Equivalent endpoint considered
- [ ] Evidence captured


# Final Testing Principle

curl is most useful when it helps turn an observation into a reproducible HTTP test.

Do not stop at:

```text
curl
 |
 v
200 OK
```

Continue:

```text
Request
   |
   v
Authentication Context
   |
   v
Application Behaviour
   |
   v
Response
   |
   v
Authorisation Context
   |
   v
Controlled Comparison
   |
   v
Interpretation
   |
   v
Security Consequence
```

For every important request ask:

```text
What exactly did I send?

Which identity sent it?

What should that identity be allowed to do?

What response did the application return?

What protected information or action was available?

What changed from the baseline?

Could another explanation produce the same result?

Can I reproduce it?

What evidence proves the security boundary was crossed?

What should remediation change?

How will I retest it?
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Networking Cheatsheet](networking.md)
- [Nmap Cheatsheet](nmap.md)
- [PowerShell Cheatsheet](powershell.md)
- [Linux Cheatsheet](linux.md)


# Detailed Notes

- [Web Application Security](../web/index.md)
- [Web Methodology](../web/methodology.md)
- [Authentication](../web/authentication.md)
- [Authorisation](../web/authorisation.md)
- [API Security](../web/api-security.md)
- [CORS](../web/cors.md)
- [Open Redirect](../web/open-redirect.md)
- [File Upload](../web/file-upload.md)
- [SSRF](../web/ssrf.md)
- [HTTP Request Smuggling](../web/http-request-smuggling.md)


# References

- [curl Official Website](https://curl.se/){ target="_blank" rel="noopener noreferrer" }
- [curl Documentation](https://curl.se/docs/){ target="_blank" rel="noopener noreferrer" }
- [curl Manual](https://curl.se/docs/manpage.html){ target="_blank" rel="noopener noreferrer" }
- [Everything curl](https://everything.curl.dev/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [OWASP API Security Project](https://owasp.org/www-project-api-security/){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }


!!! tip "Use curl for reproducibility"
    Browser testing is essential, but a concise curl command can make an HTTP observation much easier to reproduce, compare and preserve as assessment evidence.


!!! tip "Use --resolve for HTTPS virtual hosts"
    When an application hostname must be tested against a specific in-scope IP address, `--resolve` usually provides a cleaner test than connecting directly to the IP and changing only the Host header because it also preserves the hostname used for TLS SNI.


!!! tip "Change one variable at a time"
    Controlled comparisons are much easier to defend. Keep the method, identity, headers and body constant while changing only the parameter or object identifier being investigated.


!!! warning "HEAD is not GET"
    `curl -I` sends a HEAD request. If you need the headers produced by a normal GET request, use `curl -sS -D - -o /dev/null <URL>` instead.


!!! warning "HTTP success does not prove correct authorisation"
    A `200 OK` response only establishes that the request succeeded at the HTTP/application level. For access-control testing, establish who owns the resource, which identity made the request and whether that identity was permitted to receive the returned data or perform the action.
