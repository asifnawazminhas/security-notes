---
title: Server-Side Request Forgery (SSRF) Cheatsheet
description: Detailed practical SSRF cheatsheet for authorised web application security testing covering discovery, validation, blind SSRF, URL parsing, redirects, internal services, cloud metadata, Burp Suite, out-of-band testing, source review, evidence, remediation and retesting.
---

# Server-Side Request Forgery (SSRF) Cheatsheet

Server-Side Request Forgery (SSRF) occurs when an application makes a server-side network request using attacker-controlled or insufficiently restricted input.

A simplified flow is:

```text
User Input
    |
    v
Application
    |
    v
Server-Side HTTP Client
    |
    v
Destination
```

The important distinction is that the request originates from the application environment rather than directly from the tester's browser.

This can expose network locations or services that are reachable by the application but not directly reachable by an external user.

!!! warning "Authorised Security Testing"

    Perform SSRF testing only against systems explicitly included in the assessment scope. Internal service access, cloud metadata testing, redirect chaining, alternative protocols and out-of-band callbacks can interact with systems outside the original web application. Use controlled infrastructure and the minimum validation required to demonstrate the issue.


# Quick Reference

## Common SSRF Parameters

```text
url

uri

link

src

source

target

dest

destination

redirect

return

returnUrl

callback

webhook

feed

image

imageUrl

avatar

avatarUrl

file

document

endpoint

proxy

host

domain
```


## Loopback

```text
http://127.0.0.1/

http://localhost/
```


## IPv6 Loopback

```text
http://[::1]/
```


## Controlled External URL

```text
https://ssrf-test.example/
```


## Burp Collaborator

Where authorised, generate a unique Burp Collaborator domain and submit it through the suspected parameter.

Conceptually:

```text
https://UNIQUE-ID.oastify.com/
```


## Basic curl Request

```bash
curl -i 'https://target.example/fetch?url=https://ssrf-test.example/'
```


# SSRF Testing Model

Do not use:

```text
URL Parameter
     |
     v
    SSRF
```

Use:

```text
Candidate Input
      |
      v
Controlled Destination
      |
      v
Server-Side Interaction?
      |
      v
Determine Request Origin
      |
      v
Understand Restrictions
      |
      v
Minimal Impact Validation
      |
      v
Evidence
```


# What SSRF Can Affect

Depending on the application architecture, SSRF can potentially provide access to:

```text
Loopback services

Internal web applications

Internal APIs

Management interfaces

Container services

Cloud metadata services

Service discovery endpoints

Monitoring systems

Internal-only authentication services
```

The actual impact depends on network reachability, application privileges and destination behaviour.


# SSRF Types

Useful categories include:

```text
Basic SSRF

Blind SSRF

Semi-blind SSRF

Stored SSRF

Second-order SSRF
```


# Basic SSRF

Basic SSRF returns information from the server-side request to the user.

```text
Attacker
   |
   v
Application
   |
   v
Internal Resource
   |
   v
Application Returns Response
   |
   v
Attacker
```


# Blind SSRF

Blind SSRF occurs when the application performs the request but does not return the destination response.

```text
Attacker
   |
   v
Application
   |
   v
External Callback
   |
   v
DNS / HTTP Interaction
```

The tester confirms behaviour through an out-of-band service.


# Semi-Blind SSRF

The application may not return destination content but may reveal differences such as:

```text
Status

Error message

Response time

Content length

Application behaviour
```


# Stored SSRF

A URL may be stored and requested later.

Example:

```text
User Configures Webhook
        |
        v
URL Stored
        |
        v
Background Worker
        |
        v
Request Sent Later
```


# Second-Order SSRF

An input may appear harmless during submission but later reach a server-side request function.

```text
Input
  |
  v
Database
  |
  v
Background Process
  |
  v
HTTP Client
  |
  v
Destination
```


# Common SSRF Features

Look for functionality that naturally causes the server to retrieve remote content.

Examples:

```text
URL preview

Image import

Avatar import

Webhook

Callback URL

PDF generation

Document conversion

Remote file import

RSS/Atom feed

Website screenshot

URL scanner

Link checker

API proxy

SSO metadata import

OpenGraph preview

External integration

Repository import

XML processing

Media transcoding
```


# URL Preview Example

Request:

```http
POST /api/preview HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "url": "https://example.org/"
}
```

Possible server behaviour:

```text
Application
    |
    v
GET https://example.org/
    |
    v
Parse Title / Description
    |
    v
Return Preview
```


# Image Import Example

```http
POST /api/avatar/import HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "imageUrl": "https://images.example.org/avatar.png"
}
```


# Webhook Example

```http
POST /api/webhooks HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "callback": "https://hooks.example.org/test"
}
```

The request may occur:

```text
Immediately

After an event

From a background worker

From another infrastructure segment
```


# Step 1 - Establish Baseline

Start with a legitimate destination.

Example:

```http
POST /api/fetch HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "url": "https://example.org/"
}
```

Record:

```text
Status

Response body

Response length

Response time

Redirect behaviour

Displayed destination content
```


# Step 2 - Use a Controlled Destination

Use infrastructure you control or an approved callback service.

Example:

```http
POST /api/fetch HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "url": "https://ssrf-test.example/test-7f3a9"
}
```


# Why a Unique Path Helps

Use:

```text
/test-7f3a9
```

rather than:

```text
/
```

This helps correlate the interaction with the exact test request.


# Strong Initial Evidence

If your controlled server records:

```text
GET /test-7f3a9 HTTP/1.1
```

shortly after submitting the application request, this strongly supports server-side URL retrieval.


# Confirm Request Origin

Do not automatically assume every callback came from the target application.

Check:

```text
Timestamp

Unique token

Source IP where useful

HTTP headers

Request path

Request method

DNS lookup timing
```


# DNS Interaction vs HTTP Interaction

This distinction is important.

Suppose the callback service records only:

```text
DNS lookup
```

This demonstrates that some application-side component resolved the supplied hostname.

It does not necessarily prove that an HTTP request completed.


# DNS-Only Interpretation

Possible causes include:

```text
URL validation

DNS-based security filtering

HTTP client resolution

Proxy resolution

Background scanner

Application request that failed before connection
```


# HTTP Interaction

If you observe:

```http
GET /test-7f3a9 HTTP/1.1
Host: UNIQUE-ID.oastify.com
```

this provides stronger evidence that an HTTP request was actually initiated.


# DNS + HTTP

```text
DNS Query
   |
   v
TCP Connection
   |
   v
HTTP Request
```

Observing both gives a clearer picture than DNS alone.


# Burp Collaborator Workflow

```text
Candidate URL Parameter
        |
        v
Generate Collaborator Payload
        |
        v
Insert Unique URL
        |
        v
Send Request
        |
        v
Poll Collaborator
        |
        v
DNS?
        |
        +--> Yes -> Resolution confirmed
        |
        v
HTTP?
        |
        +--> Yes -> HTTP interaction confirmed
```


# Burp Collaborator Example

Parameter:

```text
url=https://UNIQUE-ID.oastify.com/ssrf-7f3a9
```

Then review interactions.


# Record Collaborator Evidence

Capture:

```text
Interaction type

Timestamp

Unique identifier

DNS query

HTTP request if present

Request headers

Request path
```


# Do Not Expose Sensitive Data

A callback should normally contain only:

```text
Unique test identifier
```

Avoid deliberately sending:

```text
Tokens

Cookies

Internal response data

Credentials

Personal data
```

to external infrastructure.


# Basic SSRF Validation

After proving server-side retrieval to a controlled host, determine whether destination restrictions exist.

Questions:

```text
Can only HTTPS be used?

Can only specific domains be used?

Are redirects followed?

Is DNS resolved before validation?

Are private addresses blocked?

Is loopback blocked?

Are non-standard ports allowed?
```


# Loopback Testing

A common next test is:

```text
http://127.0.0.1/
```

or:

```text
http://localhost/
```

Only perform this where internal service testing is within scope.


# Possible Responses

```text
Connection refused

Timeout

403

200

Application-specific response

Blocked destination

Invalid URL
```


# Connection Refused

Example:

```text
connect ECONNREFUSED 127.0.0.1:80
```

This can reveal that:

```text
The application attempted to connect to loopback.
```

However, confirm that the message genuinely comes from server-side request handling.


# Timeout

A timeout can indicate:

```text
Network filtering

Unresponsive service

Blackholed address

Application timeout

Proxy behaviour
```

A timeout alone does not prove that a particular internal service exists.


# Different Internal Responses

Suppose:

```text
http://127.0.0.1:80/
    -> connection refused

http://127.0.0.1:8080/
    -> different application error
```

This may indicate different service behaviour.

Treat this as a candidate and validate carefully.


# Do Not Turn SSRF Into Blind Port Scanning by Default

Testing large internal address or port ranges can:

```text
Generate significant traffic

Interact with sensitive systems

Trigger monitoring

Affect fragile services
```

Use targeted validation based on known architecture and assessment scope.


# Internal Hostnames

Where explicitly authorised, applications may be tested against known internal hostnames supplied by the organisation.

Example:

```text
http://internal-api.example.local/
```

Prefer known test systems over indiscriminate internal discovery.


# Internal DNS Names

Potential environments may use names such as:

```text
api.internal

monitoring.internal

service.namespace.svc.cluster.local
```

Do not guess or enumerate internal namespaces unnecessarily.


# URL Parsing

SSRF controls often fail because different components parse URLs differently.

Conceptually:

```text
User URL
   |
   v
Validator
   |
   v
URL Parser A
   |
   v
HTTP Client
   |
   v
URL Parser B
```

If Parser A and Parser B interpret the URL differently, validation may not protect the actual request.


# Correct Defensive Principle

Applications should:

```text
Parse

Canonicalise

Validate

Resolve

Verify

Connect
```

using consistent, well-defined logic.


# Scheme Validation

Review which URL schemes are accepted.

Normal web retrieval should usually be limited to:

```text
http

https
```

if those are the only protocols required.


# Reject Unnecessary Schemes

Applications should not accept arbitrary schemes simply because the underlying library supports them.


# Redirects

Redirect handling is particularly important.

Example:

```text
Allowed URL
    |
    v
https://safe.example/
    |
    v
302 Redirect
    |
    v
Internal Destination
```


# Redirect Testing

A controlled redirect service can test whether:

```text
Initial URL is validated

Redirect destination is revalidated
```


# Safe Redirect Test

Conceptually:

```text
https://controlled.example/redirect
```

returns:

```http
HTTP/1.1 302 Found
Location: https://another-controlled.example/final
```

First establish redirect behaviour using controlled external hosts.


# Redirect Security Principle

Every redirect destination should be subject to the same destination validation as the initial URL.


# Redirect Chain

```text
User Input
   |
   v
URL A
   |
   v
Validation
   |
   v
Request A
   |
   v
302 -> URL B
   |
   v
Validate Again
   |
   v
Request B
```


# DNS Resolution

Destination filtering based only on the supplied hostname can be insufficient.

Conceptually:

```text
Hostname
   |
   v
DNS Resolution
   |
   v
IP Address
   |
   v
Network Request
```


# Defensive DNS Validation

Applications should consider whether the resolved destination belongs to:

```text
Loopback

Private networks

Link-local ranges

Reserved ranges

Other prohibited destinations
```


# DNS Rebinding

DNS responses can change over time.

Conceptually:

```text
Validation Resolution
       |
       v
Public Address
       |
       v
Later Connection Resolution
       |
       v
Private Address
```

Defences should avoid insecure time-of-check/time-of-use assumptions.


# IP Address Representation

Network libraries may accept addresses in forms other than the familiar dotted-decimal representation.

Defensive validation should canonicalise IP addresses before checking them.

Do not rely on string matching such as:

```text
URL does not contain "127.0.0.1"
```

as an SSRF defence.


# IPv4 Private Ranges

Important private IPv4 networks include:

```text
10.0.0.0/8

172.16.0.0/12

192.168.0.0/16
```


# IPv4 Loopback

```text
127.0.0.0/8
```


# Link-Local IPv4

```text
169.254.0.0/16
```


# IPv6 Loopback

```text
::1
```


# IPv6 Local Addressing

Defensive validation must also account for relevant IPv6 address classes rather than validating only IPv4.


# Cloud Metadata

Cloud environments may expose metadata services to workloads.

Because metadata can contain security-sensitive information, testing these services should only be performed when explicitly authorised.


# AWS Metadata

The well-known IPv4 link-local metadata address is:

```text
169.254.169.254
```

Modern AWS environments can use IMDSv2, which requires a session token for metadata requests.


# AWS IMDSv2

A simple server-side GET through an SSRF primitive may therefore not be enough to access protected metadata when IMDSv2 is required.

Do not conclude:

```text
AWS metadata inaccessible
```

means:

```text
SSRF does not exist.
```

These are separate questions.


# Azure Metadata

Azure environments also provide instance metadata services.

Metadata access normally includes platform-specific request requirements.

Do not perform metadata enumeration unless cloud metadata testing is explicitly authorised.


# Google Cloud Metadata

Google Cloud exposes instance metadata through its metadata service and requires specific request headers for normal metadata access.

Again:

```text
SSRF existence
```

and:

```text
metadata exploitability
```

are separate findings.


# Cloud Metadata Testing Principle

Prefer:

```text
Prove SSRF to controlled destination
        |
        v
Establish internal reachability if authorised
        |
        v
Assess metadata exposure only if required
```

rather than immediately targeting metadata services.


# Containers and Kubernetes

SSRF from containerised applications may expose services reachable from the workload network.

Potential architecture:

```text
Internet
   |
   v
Web Application Pod
   |
   +--> Internal Service
   |
   +--> Cluster DNS
   |
   +--> Other Permitted Network Services
```

Do not assume all cluster services are reachable.


# Service Meshes

Requests may pass through:

```text
Sidecar proxy

Service mesh

Egress proxy

Network policy
```

This can change observed SSRF behaviour.


# Proxy Behaviour

The application may use an outbound proxy.

Flow:

```text
Application
   |
   v
HTTP Proxy
   |
   v
Destination
```

The callback source IP may therefore belong to:

```text
Proxy

NAT gateway

Cloud egress
```

rather than the application host itself.


# Source IP Is Supporting Evidence

Do not require the callback source IP to equal the web server's public IP.

Modern architectures commonly separate:

```text
Frontend

Workers

Proxy

NAT

Egress gateway
```


# Background Workers

A URL may be fetched asynchronously.

Example:

```text
Submit URL
   |
   v
Queue
   |
   v
Worker
   |
   v
Fetch
```

Allow enough time for controlled callbacks before concluding that no request occurred.


# Stored Webhooks

Webhook testing may require triggering the relevant event.

Example:

```text
Create Webhook
      |
      v
Create Test Event
      |
      v
Webhook Worker
      |
      v
Callback
```


# PDF Generation

Server-side HTML-to-PDF tools may retrieve:

```text
Images

Stylesheets

Fonts

Links

iframes
```

depending on the renderer and configuration.

A user-controlled HTML or URL input may therefore create an SSRF surface.


# Screenshot Services

Applications that generate screenshots from URLs are natural SSRF candidates.

```text
User URL
   |
   v
Headless Browser
   |
   v
Destination
```

A headless browser introduces different behaviour from a simple HTTP client.


# Headless Browser SSRF

A browser may automatically request:

```text
HTML

JavaScript

CSS

Images

Fonts

Favicons
```

One submitted URL can therefore create multiple callback interactions.


# Distinguish Primary and Secondary Requests

If a page contains:

```html
<img src="https://callback.example/image">
```

the callback might be generated by the rendering engine loading a secondary resource.

Document the exact interaction path.


# XML and SSRF

XML external entity processing can sometimes produce server-side network interactions.

That is primarily an XXE issue even though the observable effect can resemble SSRF.

See:

[XXE Notes](../web/xxe.md)


# Open Redirect vs SSRF

A parameter such as:

```text
?next=https://example.org/
```

may cause the browser to navigate.

That is not SSRF if the server does not retrieve the destination.

Determine:

```text
Who makes the request?
```


# Client-Side Request

```text
Browser
   |
   v
Destination
```

Not SSRF.


# Server-Side Request

```text
Browser
   |
   v
Application
   |
   v
Destination
```

Potential SSRF.


# Browser Developer Tools

If the destination request appears directly in the browser's Network tab, determine whether it is simply client-side functionality.

A server-side callback service can help distinguish the source.


# URL Validation

Weak validation:

```python
if "example.com" in url:
    fetch(url)
```

This is not a robust allowlist.


# Safer Allowlist Model

```text
Parse URL
   |
   v
Require HTTPS
   |
   v
Extract Hostname
   |
   v
Exact Allowlist Match
   |
   v
Resolve Host
   |
   v
Validate Resolved Address
   |
   v
Connect
```


# Hostname Allowlist

Prefer explicit trusted destinations where business requirements permit.

Example conceptual allowlist:

```text
images.example.com

cdn.example.com
```

Do not rely on substring matching.


# Exact Host Comparison

Conceptually:

```python
allowed_hosts = {
    "images.example.com",
    "cdn.example.com"
}
```

Then compare the parsed hostname to an exact allowed value.


# Suffix Checks

A naive suffix check can introduce mistakes.

For example, developers must carefully distinguish:

```text
example.com

sub.example.com

notexample.com
```

Use a proper URL/domain parsing strategy.


# Credentials in URLs

URLs can contain user-information syntax:

```text
scheme://user:password@host/
```

Security filters must use the parsed destination hostname rather than visually inspecting the entire URL string.


# Fragments

A URL fragment:

```text
#section
```

is generally not sent in the HTTP request to the remote server.

Validation logic should still use a proper URL parser rather than string splitting.


# Ports

Review whether users can control destination ports.

Example:

```text
https://example.org:8443/
```

Applications may need an explicit port policy.


# Port Allowlisting

Where only normal web access is required, the application may restrict requests to approved ports.

This reduces access to unrelated internal services.


# HTTP Methods

Determine which method the server-side client uses.

Possible:

```text
GET

HEAD

POST
```

Do not assume user control of the destination URL also provides control over HTTP method or body.


# Headers

Some SSRF features allow users to configure request headers.

This can materially increase risk.

Examples:

```text
Webhook testing

API integrations

HTTP proxy functionality
```


# Header Control

If a feature allows:

```json
{
  "url": "https://api.example.org/",
  "headers": {
    "Authorization": "..."
  }
}
```

review both:

```text
Destination restrictions

Header restrictions
```


# Credential Leakage

A server-side request mechanism may automatically attach credentials or internal headers.

Examples can include:

```text
Proxy credentials

Internal API keys

Service authentication headers

Client certificates
```

Do not assume this occurs. Validate only where authorised.


# Redirect Header Leakage

If a client follows redirects, sensitive headers should not automatically be forwarded to untrusted destinations.

This is an important secure implementation consideration.


# URL Fetching Libraries

Source review may identify libraries such as:

```text
requests

urllib

httpx

axios

fetch

curl

HttpClient

RestTemplate

WebClient

OkHttp
```


# Python Source Search

```bash
rg -ni 'requests\.(get|post|request)|urllib\.request|httpx\.(get|post)|urlopen' -g '*.py' .
```


# JavaScript / TypeScript Source Search

```bash
rg -ni 'axios\.|fetch\(|http\.get|https\.get' -g '*.js' -g '*.ts' .
```


# Java Source Search

```bash
rg -ni 'HttpClient|RestTemplate|WebClient|OkHttp|openConnection' -g '*.java' .
```


# C# Source Search

```bash
rg -ni 'HttpClient|WebClient|WebRequest|HttpWebRequest' -g '*.cs' .
```


# PHP Source Search

```bash
rg -ni 'curl_exec|curl_init|file_get_contents|fopen\(' -g '*.php' .
```


# Search URL Parameters

```bash
rg -ni 'url|uri|callback|webhook|redirect|imageUrl|avatarUrl|endpoint' src/
```


# Source-to-Sink Model

```text
HTTP Parameter
      |
      v
Application Variable
      |
      v
URL Validation
      |
      v
HTTP Client
      |
      v
Network Destination
```


# Vulnerable Source Example

```python
url = request.args.get("url")

response = requests.get(url)

return response.text
```

The destination is directly controlled by request input.


# Safer Design

Conceptually:

```python
url = parse_user_url()

validate_scheme(url)
validate_hostname(url)
resolve_and_validate_destination(url)

response = fetch_with_redirect_validation(url)
```

Actual implementation should use well-tested URL and IP parsing libraries.


# Source Review Questions

For each URL-fetching candidate ask:

```text
Can a user control the URL?

Can a user control the hostname?

Can a user control the port?

Can a user control the scheme?

Is there an allowlist?

How is the URL parsed?

Is DNS resolution validated?

Are private ranges blocked?

Are redirects followed?

Are redirect destinations revalidated?

Does the client use a proxy?

Are credentials attached?

Is the response returned to the user?
```


# Candidate Classification

## Low Concern

```text
Constant URL
    |
    v
HTTP Client
```

Example:

```python
requests.get("https://status.example.com/api")
```

No user-controlled destination.


# Review Candidate

```text
User Path
   |
   v
Fixed Trusted Host
```

Example:

```python
requests.get(
    "https://api.example.com/" + user_path
)
```

This may create other issues, but destination host control is more constrained.


# High-Priority Candidate

```text
User URL
   |
   v
requests.get(user_url)
```

This should receive detailed SSRF review.


# Blind SSRF Validation

If the response is always:

```text
Request queued successfully
```

use a controlled out-of-band domain.


# Blind SSRF Example

Request:

```http
POST /api/webhook/test HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "url": "https://UNIQUE-ID.oastify.com/ssrf-test"
}
```


# Possible Result

Application:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "queued"
}
```

Collaborator later records:

```text
DNS
HTTP
```

This supports blind SSRF.


# Timing Analysis

Timing can sometimes help distinguish destination behaviour.

Example:

```text
Controlled external URL:
0.4 seconds

Loopback closed port:
0.1 seconds

Unroutable destination:
5.0 seconds
```

However, timing is noisy.


# Do Not Use Timing Alone

Possible causes include:

```text
Network latency

Connection timeout

DNS timeout

Proxy behaviour

Application queueing

Server load
```


# Repeat Timing Tests

If timing is relevant, use multiple requests and compare stable patterns.


# Response Fingerprinting

Basic SSRF may return destination content.

Look for:

```text
Different Server header

Different page title

Different HTML structure

Internal hostname

API JSON

Unexpected authentication page
```


# Do Not Overstate Internal Content

A returned:

```text
401 Unauthorized
```

from an internal endpoint still demonstrates reachability, but not authentication bypass.


# Internal Authentication

SSRF may reach a service that still requires:

```text
Authentication

Client certificate

API key

Kerberos

OAuth token
```

Reachability and authorisation are separate security controls.


# Network Segmentation

SSRF impact is often increased when the vulnerable workload has broad internal network access.

Architecture:

```text
Internet User
     |
     v
Web Application
     |
     +--> Database Network
     |
     +--> Management Network
     |
     +--> Internal APIs
```

Strong segmentation can limit the blast radius.


# Egress Filtering

Outbound filtering can reduce SSRF impact.

Example:

```text
Application
    |
    v
Egress Firewall
    |
    +--> Approved API
    |
    X--> Internal Management
    |
    X--> Internet
```


# Egress Proxy

A controlled outbound proxy can enforce:

```text
Destination policy

Logging

Protocol restrictions

Authentication

Network segmentation
```


# SSRF Allowlist vs Blocklist

Prefer:

```text
Allow only destinations required by business functionality
```

over:

```text
Allow everything except known bad destinations
```


# Blocklist Challenges

A complete denylist must correctly handle:

```text
IPv4

IPv6

DNS

Redirects

Alternative address representations

Reserved ranges

URL parser differences
```

This is difficult to implement reliably.


# When Arbitrary Internet URLs Are Required

Some products genuinely need to retrieve arbitrary public URLs.

Defences should then include layers such as:

```text
Scheme restriction

URL canonicalisation

DNS/IP validation

Private-range rejection

Redirect validation

Egress proxy

Network isolation

Timeouts

Response size limits
```


# Response Size Limits

Remote servers may return extremely large responses.

Set limits to reduce:

```text
Memory exhaustion

Disk exhaustion

Bandwidth consumption
```


# Timeouts

Use strict:

```text
Connection timeout

Read timeout

Overall request timeout
```

to reduce resource exhaustion.


# Redirect Limits

Set a maximum redirect count.

This helps prevent:

```text
Redirect loops

Excessive resource use
```


# Content-Type Validation

If the feature expects an image, validate actual content rather than trusting only:

```http
Content-Type: image/png
```

However, content validation alone does not prevent SSRF because the request has already occurred.


# SSRF and Authentication

Record whether the SSRF feature requires:

```text
Unauthenticated access

Standard user

Privileged user

Administrator
```

This materially affects risk.


# SSRF and Multi-Tenancy

In multi-tenant environments, SSRF may allow one tenant's workload to reach:

```text
Shared internal services

Tenant management systems

Cross-tenant infrastructure
```

Do not assume cross-tenant impact without evidence.


# SSRF and WebSockets

A URL-fetching function that supports only normal HTTP requests differs from a generic network proxy.

Determine the actual protocols and capabilities before describing impact.


# SSRF and File Access

Some libraries support URL schemes beyond HTTP.

If a non-HTTP scheme leads to local file access, that may materially change the issue.

Do not test alternative protocols unless explicitly within scope.


# SSRF and Command Injection

A URL passed to a shell command can create a separate command-injection vulnerability.

Example pattern:

```text
User URL
   |
   v
Shell Command
   |
   v
curl <user-url>
```

This should be reviewed as both:

```text
Server-side request functionality

Potential shell injection
```


# SSRF and XXE

If XML processing causes a network request:

```text
XML Parser
   |
   v
External Entity
   |
   v
Network Request
```

the root cause is usually XXE.

Classify findings according to the actual vulnerable component.


# SSRF and Open Redirect

An open redirect can sometimes become relevant to SSRF if the SSRF implementation validates only the initial destination and blindly follows redirects.

The issues may combine:

```text
SSRF Destination Validation
        |
        v
Allowed Redirector
        |
        v
Prohibited Destination
```


# SSRF and Host Header Attacks

Host header attacks concern trust in HTTP request host information.

SSRF concerns server-side outbound requests.

They can overlap in complex architectures but are distinct vulnerability classes.


# Error Interpretation

## Invalid URL

```text
Invalid URL
```

May mean:

```text
Parser rejected input

Application validation rejected input
```


## Host Not Allowed

```text
Destination is not permitted
```

Supports the existence of destination filtering.


## DNS Failure

```text
getaddrinfo failed
```

May indicate that the application attempted hostname resolution.


## Connection Refused

```text
Connection refused
```

May indicate a connection attempt reached a host with no listening service.


## Timeout

```text
Request timed out
```

May indicate an attempted connection, but does not establish service existence.


## TLS Error

```text
certificate verify failed
```

Can indicate the application connected far enough to perform TLS validation.


# Result Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| URL parameter exists | Possible fetch functionality | SSRF |
| DNS callback received | Server-side resolution | Completed HTTP request |
| HTTP callback received | Server-side HTTP interaction | Internal network access |
| Loopback gives different error | Different network behaviour | Valuable internal service |
| Internal endpoint returns 401 | Internal reachability | Authentication bypass |
| Timeout differs | Possible network distinction | Open port |
| Redirect followed | Redirect support | Redirect validation bypass |
| Metadata address blocked | Specific destination control | SSRF is fixed |
| Scanner reports SSRF | Candidate | Confirmed SSRF |
| `requests.get(user_url)` found | Strong source candidate | Runtime reachability |


# Burp Suite Workflow

```text
Proxy
  |
  v
Identify URL-Like Parameter
  |
  v
Repeater
  |
  v
Legitimate External URL
  |
  v
Controlled Collaborator URL
  |
  v
Poll Collaborator
  |
  v
DNS / HTTP?
  |
  v
Determine Restrictions
```


# Burp Repeater Example

Original:

```http
POST /api/preview HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "url": "https://example.org/"
}
```

Controlled:

```http
POST /api/preview HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "url": "https://UNIQUE-ID.oastify.com/ssrf-7f3a9"
}
```


# Burp Intruder

Intruder can help test a small, controlled set of approved destinations or URL parsing cases.

Do not use it for indiscriminate internal network scanning.


# Burp Collaborator

Useful for:

```text
Blind SSRF

Stored SSRF

Asynchronous SSRF

DNS interaction detection

HTTP interaction detection
```


# Interactsh

ProjectDiscovery Interactsh can also provide out-of-band interaction infrastructure.

Typical authorised workflow:

```text
Start controlled Interactsh client
        |
        v
Generate unique interaction domain
        |
        v
Submit through suspected SSRF input
        |
        v
Observe DNS / HTTP interaction
```


# Use Assessment-Controlled Infrastructure

Where sensitive environments are involved, use an approved self-hosted or organisation-approved interaction service if required by the engagement rules.


# curl for Controlled Callback Server

If you operate a simple approved HTTP test server, application callbacks can be inspected through the server logs.

The exact setup depends on the assessment infrastructure.


# Python Test Server

For a simple controlled lab:

```bash
python3 -m http.server 8000
```

This is useful only when the application can reach the test host and the engagement permits it.


# Netcat Listener

For basic lab inspection:

```bash
nc -lvnp 8000
```

A real HTTP server is generally easier for repeated request analysis.


# Request Headers

A callback can reveal headers such as:

```text
User-Agent

Accept

Host

Connection

Via
```

These can help identify the server-side client.


# User-Agent Example

```http
User-Agent: python-requests/...
```

This may suggest a Python HTTP client.

Do not rely on User-Agent alone for architecture conclusions.


# Source-Code Review Workflow

```text
Find HTTP Client Calls
        |
        v
Identify URL Argument
        |
        v
Trace Backwards
        |
        v
User Controlled?
        |
        v
Review Validation
        |
        v
Review Redirects
        |
        v
Review DNS/IP Controls
        |
        v
Runtime Validation
```


# ripgrep - Python

```bash
rg -n -C 4 'requests\.(get|post|request)|httpx\.(get|post)|urlopen' -g '*.py' .
```


# ripgrep - JavaScript

```bash
rg -n -C 4 'axios\.|fetch\(|https?\.get' -g '*.js' -g '*.ts' .
```


# ripgrep - Java

```bash
rg -n -C 4 'HttpClient|RestTemplate|WebClient|OkHttp|openConnection' -g '*.java' .
```


# ripgrep - .NET

```bash
rg -n -C 4 'HttpClient|WebClient|WebRequest|HttpWebRequest' -g '*.cs' .
```


# Example Source Candidate

```python
@app.post("/preview")
def preview():
    target = request.json["url"]

    response = requests.get(target, timeout=5)

    return response.text
```

Interpretation:

```text
HTTP request body
       |
       v
target
       |
       v
requests.get()
```

The destination appears directly attacker controlled.


# Example With Host Allowlist

```python
parsed = urlparse(target)

if parsed.hostname not in ALLOWED_HOSTS:
    abort(400)

response = requests.get(target)
```

This is better, but review:

```text
Exact allowlist contents

Redirect handling

DNS resolution

IP validation

Parser behaviour
```


# Do Not Stop at the First `if`

A function named:

```text
validate_url()
```

does not prove secure SSRF protection.

Inspect what it actually validates.


# Example Weak Validation

```python
if not target.startswith("https://"):
    abort(400)
```

This only restricts the scheme.

It does not restrict destination.


# Another Weak Pattern

```python
if "trusted.example" not in target:
    abort(400)
```

This uses substring matching rather than parsed-host validation.


# Secure Architecture Pattern

```text
User
 |
 v
Application
 |
 v
URL Parser
 |
 v
Destination Policy
 |
 v
DNS Resolver
 |
 v
Resolved IP Policy
 |
 v
Egress Proxy
 |
 v
Approved Destination
```


# Evidence Collection

For an SSRF finding record:

```text
Finding ID

Endpoint

Method

Parameter

Authentication context

Feature

Submitted URL

Unique callback identifier

Interaction timestamp

DNS interaction

HTTP interaction

Source IP where relevant

HTTP request details

Internal destination test if authorised

Response differences

Redirect behaviour

Network restrictions observed
```


# Minimal Blind SSRF Evidence

A strong minimal proof:

```text
1. Submit unique callback URL.

2. Application accepts the request.

3. Callback service records DNS resolution.

4. Callback service records HTTP request.

5. Timestamp and unique token correlate with submission.

6. Repeat with a second unique token.
```


# Repeatability

Use another identifier:

```text
ssrf-test-a1b2

ssrf-test-c3d4
```

This helps establish deterministic behaviour.


# Evidence for Basic SSRF

Capture:

```text
Original request

Controlled destination request

Returned destination content

Relevant response headers

Timestamp
```


# Evidence for Internal Reachability

If authorised:

```text
Controlled internal test service

Known port

Known expected response

Application-retrieved response
```

is preferable to scanning arbitrary internal systems.


# Reporting Example - Basic SSRF

> The `url` property of the preview functionality is used by the application to perform server-side HTTP requests without restricting the destination to approved hosts. A URL pointing to assessment-controlled infrastructure caused the application to retrieve the supplied resource and return its contents in the application response. This demonstrates that an authenticated user can control the destination of server-side requests.


# Reporting Example - Blind SSRF

> The webhook test functionality performs server-side requests to user-supplied destinations. Submitting a unique assessment-controlled URL resulted in correlated DNS and HTTP interactions from the application environment. The destination response is not returned to the user, so the issue was validated as blind SSRF.


# Reporting Example - Internal Reachability

> After server-side request control was established using assessment-controlled infrastructure, the same functionality was tested against an approved internal test service. The application successfully retrieved the known response from the internal endpoint, demonstrating that the SSRF primitive can cross the external application boundary and access resources reachable from the application network.


# Reporting Example - DNS Only

> Submitting a unique assessment-controlled hostname resulted in a correlated DNS lookup from the application environment. No HTTP interaction was observed during repeated testing. The result demonstrates server-side hostname resolution but does not establish that the application completed an outbound HTTP request to the supplied destination.


# Reporting Example - Redirect Weakness

> The application validates the initial URL against its destination policy but follows HTTP redirects without applying the same validation to the redirect target. An assessment-controlled allowed destination was able to redirect the server-side client to a second destination that would otherwise be rejected when supplied directly.


# Avoid Overclaiming

Do not write:

```text
SSRF allows full internal network compromise.
```

unless that impact was actually demonstrated.

Prefer:

```text
The application can initiate server-side HTTP requests to attacker-controlled destinations.
```

Then separately document demonstrated reachability.


# Severity Considerations

Consider:

```text
Authentication required

Destination restrictions

Internal network access

Response visibility

HTTP method

Header control

Redirect behaviour

Cloud environment

Application network position

Database/management reachability

Egress controls
```


# Remediation

The strongest remediation is often architectural:

```text
Do not allow users to control arbitrary request destinations.
```


# Allowlist Destinations

Where possible:

```text
Feature
  |
  v
Approved Service IDs
  |
  v
Server Maps ID to URL
```

instead of accepting arbitrary URLs.


# Server-Side Mapping

Prefer:

```json
{
  "provider": "profile-image-service"
}
```

with server-side mapping:

```text
profile-image-service
        |
        v
https://images.example.com/
```

over:

```json
{
  "url": "https://anything.example/"
}
```


# Parse URLs Properly

Use a mature URL parser.

Validate the parsed:

```text
Scheme

Hostname

Port
```


# Resolve and Validate

After hostname parsing:

```text
Resolve hostname

Canonicalise returned addresses

Reject prohibited networks

Connect only to validated addresses
```


# Revalidate Redirects

Every redirect target should pass the same destination policy.


# Restrict Schemes

Allow only protocols required by the feature.

Usually:

```text
https
```

or:

```text
http + https
```

depending on business requirements.


# Restrict Ports

If the feature only requires:

```text
443
```

there may be no reason to allow arbitrary destination ports.


# Egress Filtering

Network-level egress controls should prevent application workloads from reaching unnecessary:

```text
Management networks

Metadata services

Database networks

Administrative interfaces
```


# Isolate Fetchers

For features that must retrieve arbitrary Internet URLs, consider a dedicated isolated fetch service.

```text
Application
    |
    v
Isolated Fetch Service
    |
    v
Public Internet
```

The fetch service should have no access to sensitive internal networks.


# Cloud Metadata Controls

Cloud-specific controls should be enabled where available.

For example, AWS environments should use appropriate IMDS protections and network architecture rather than relying solely on application URL validation.


# Request Limits

Implement:

```text
Connection timeout

Read timeout

Maximum response size

Redirect limit

Content restrictions where appropriate
```


# Logging

Record security-relevant outbound fetch information such as:

```text
Requesting user

Feature

Destination hostname

Resolved address where appropriate

Timestamp

Result
```

Avoid logging sensitive URL credentials or tokens.


# Monitoring

Potential SSRF indicators include:

```text
Requests to loopback

Requests to private networks

Requests to link-local addresses

Unexpected ports

Unusual external callback domains

Repeated failed destination requests
```


# Retesting

Retest the exact original feature.

```text
Original SSRF Input
        |
        v
Destination Rejected?
        |
        v
Approved URL Still Works?
```


# Retest Controlled External Host

If arbitrary external URLs should no longer be accepted:

```text
https://ssrf-test.example/
```

should be rejected unless explicitly approved.


# Retest Loopback

Where appropriate:

```text
http://127.0.0.1/
```

should be rejected before a network request is made.


# Retest Private Networks

Verify prohibited private destinations are rejected consistently.


# Retest IPv6

Do not validate only IPv4.

Include the relevant IPv6 prohibited destinations.


# Retest Redirects

Test:

```text
Approved URL
    |
    v
Redirect
    |
    v
Prohibited Destination
```

The redirect should be blocked.


# Retest DNS Resolution

Confirm that hostnames resolving to prohibited address ranges are rejected.


# Retest Normal Functionality

Valid business functionality must still work.

Example:

```text
Approved image host
       |
       v
Image import succeeds
```


# Retest Source Code

Where source is available, confirm that the fix addresses:

```text
Destination validation

Resolved IP validation

Redirect validation

Network restrictions
```

rather than simply blocking one string.


# Weak Fix Example

```python
if "127.0.0.1" in url:
    abort(400)
```

This is not a complete SSRF defence.


# Better Fix Model

```text
Parse URL
   |
   v
Validate Scheme
   |
   v
Validate Exact Host Policy
   |
   v
Resolve Host
   |
   v
Validate All Resolved Addresses
   |
   v
Connect
   |
   v
Revalidate Redirects
```


# Common False Positives

## Browser Makes Request

If the request originates directly from the user's browser:

```text
Not SSRF
```


## DNS Only

A DNS lookup proves resolution behaviour, not necessarily a completed HTTP request.


## Security Scanner

A scanner finding:

```text
Potential SSRF parameter
```

is only a candidate.


## Application Error

```text
Unable to fetch URL
```

does not prove that the supplied destination was contacted.


## Generic Timeout

A timeout alone does not identify the destination state.


## URL Reflection

If the application merely displays:

```text
https://example.org/
```

without fetching it, there is no SSRF.


# Common Testing Mistakes

## Immediately Targeting Metadata

First prove the server-side request primitive using controlled infrastructure.


## Scanning Internal Networks

Avoid broad internal enumeration unless explicitly authorised.


## Treating DNS as HTTP

Record interaction type accurately.


## Ignoring Redirects

Destination controls often behave differently after redirects.


## Ignoring IPv6

IPv4-only filtering is incomplete.


## Ignoring Background Workers

The request may occur asynchronously.


## Ignoring Authentication

An administrator-only SSRF has a different threat model from an unauthenticated SSRF.


## Ignoring Egress Architecture

Callbacks may originate from proxies, workers or NAT gateways.


## Ignoring Source Code

White-box review can reveal the exact destination-validation logic.


## Reporting Hypothetical Impact as Demonstrated

Separate:

```text
Confirmed behaviour
```

from:

```text
Potential consequence.
```


# Practical SSRF Checklist

## Discovery

- [ ] URL parameters identified
- [ ] Webhook functionality reviewed
- [ ] Callback functionality reviewed
- [ ] Remote image import reviewed
- [ ] URL preview reviewed
- [ ] PDF generation reviewed
- [ ] Screenshot functionality reviewed
- [ ] Feed import reviewed
- [ ] API proxy functionality reviewed
- [ ] Background workers considered

## Baseline

- [ ] Legitimate URL tested
- [ ] Baseline response captured
- [ ] Response time recorded
- [ ] Redirect behaviour observed
- [ ] Authentication context recorded

## Controlled Validation

- [ ] Unique callback hostname generated
- [ ] Unique path/token used
- [ ] DNS interaction checked
- [ ] HTTP interaction checked
- [ ] Timestamp correlated
- [ ] Test repeated
- [ ] Callback data minimised

## Destination Controls

- [ ] Scheme restrictions reviewed
- [ ] Hostname restrictions reviewed
- [ ] Port restrictions reviewed
- [ ] Loopback handling reviewed
- [ ] Private-address handling reviewed
- [ ] Link-local handling reviewed
- [ ] IPv6 handling reviewed
- [ ] DNS resolution reviewed

## Redirects

- [ ] Redirect following identified
- [ ] Redirect destination validation reviewed
- [ ] Multiple redirects considered
- [ ] Sensitive header forwarding considered

## Internal Validation

- [ ] Internal testing explicitly authorised
- [ ] Known test service preferred
- [ ] Broad port scanning avoided
- [ ] Response interpreted carefully
- [ ] Reachability separated from authentication

## Cloud

- [ ] Cloud environment identified
- [ ] Metadata testing authorised before use
- [ ] Metadata protections considered
- [ ] SSRF existence separated from metadata exploitability

## Source Review

- [ ] HTTP client calls searched
- [ ] User-controlled URL traced
- [ ] URL parser identified
- [ ] Scheme validation reviewed
- [ ] Host validation reviewed
- [ ] DNS/IP validation reviewed
- [ ] Redirect handling reviewed
- [ ] Proxy configuration reviewed
- [ ] Header behaviour reviewed

## Evidence

- [ ] Endpoint
- [ ] Method
- [ ] Parameter
- [ ] Authentication context
- [ ] Submitted URL
- [ ] Unique callback ID
- [ ] DNS interaction
- [ ] HTTP interaction
- [ ] Timestamp
- [ ] Internal response if authorised
- [ ] Redirect behaviour
- [ ] Sensitive values redacted

## Remediation

- [ ] Arbitrary URL requirement challenged
- [ ] Destination allowlist considered
- [ ] URL parsing implemented
- [ ] Resolved IP validation implemented
- [ ] Redirect revalidation implemented
- [ ] Scheme restrictions implemented
- [ ] Port restrictions considered
- [ ] Egress filtering considered
- [ ] Fetcher isolation considered
- [ ] Timeouts configured
- [ ] Response size limited

## Retest

- [ ] Original payload retested
- [ ] Controlled external URL retested
- [ ] Loopback retested
- [ ] Private ranges retested
- [ ] IPv6 retested
- [ ] Redirect chain retested
- [ ] DNS resolution behaviour retested
- [ ] Normal business functionality verified


# SSRF Type Comparison

| Type | Response Visible? | Typical Evidence |
|---|---:|---|
| Basic SSRF | Yes | Destination content returned |
| Blind SSRF | No | DNS/HTTP callback |
| Semi-blind SSRF | Partial | Error/timing/status difference |
| Stored SSRF | Later | Delayed callback |
| Second-order SSRF | Later workflow | Callback from downstream process |


# Interaction Interpretation

| Observation | Meaning |
|---|---|
| No interaction | No proof of server-side retrieval |
| DNS only | Server-side hostname resolution occurred |
| DNS + HTTP | Server-side HTTP interaction strongly supported |
| HTTP with unique path | Strong correlation to test |
| Internal 401 | Internal service reachable, authentication still enforced |
| Connection refused | Connection attempt may have reached closed port |
| Timeout | Ambiguous network behaviour |
| TLS certificate error | TLS connection processing likely occurred |


# Destination Review Matrix

| Destination | Typical Security Treatment |
|---|---|
| Approved external service | Allow if business required |
| Arbitrary Internet host | Restrict where possible |
| Loopback | Block |
| Private network | Block unless specifically required |
| Link-local | Block |
| Cloud metadata | Block from generic fetchers |
| Management network | Block |
| Arbitrary port | Restrict where possible |


# SSRF Impact Matrix

| Capability | Potential Significance |
|---|---|
| External callback only | Confirms server-side request control |
| Internal HTTP reachability | Increased network exposure |
| Internal response returned | Information disclosure potential |
| Redirect policy bypass | Destination controls weakened |
| Header control | Increased request capability |
| Arbitrary methods/body | Increased interaction capability |
| Metadata access | Cloud credential/configuration exposure risk |
| Broad network reachability | Larger internal attack surface |


# Source Review Matrix

| Pattern | Priority |
|---|---:|
| Constant URL -> HTTP client | Low |
| Allowlisted service ID -> fixed URL | Low |
| User path -> fixed host | Medium |
| User hostname -> HTTP client | High |
| User URL -> HTTP client | High |
| User URL -> client with redirects | High |
| User URL -> shell command | Critical review candidate |


# Burp Quick Workflow

```text
             TARGET FEATURE
                    |
                    v
              URL PARAMETER
                    |
                    v
                REPEATER
                    |
                    v
            LEGITIMATE URL
                    |
                    v
         COLLABORATOR DOMAIN
                    |
                    v
              SEND REQUEST
                    |
                    v
          POLL COLLABORATOR
             /          \
            /            \
           v              v
         DNS             HTTP
           |              |
           v              v
     RESOLUTION       REQUEST
      CONFIRMED       CONFIRMED
            \            /
             \          /
              +--------+
                  |
                  v
          TEST RESTRICTIONS
                  |
                  v
              EVIDENCE
```


# Source-to-Sink Model

```text
                    USER INPUT
                        |
                        v
                       URL
                        |
                        v
                  URL PARSER
                        |
                        v
                   VALIDATION
                        |
                        v
                  DNS RESOLUTION
                        |
                        v
                    IP CHECK
                        |
                        v
                  HTTP CLIENT
                        |
                        v
                   REDIRECT?
                    /      \
                   No      Yes
                   |        |
                   |        v
                   |   VALIDATE AGAIN
                   |        |
                   +----+---+
                        |
                        v
                   DESTINATION
```


# Secure Architecture Model

```text
                   USER
                     |
                     v
                APPLICATION
                     |
                     v
             APPROVED RESOURCE ID
                     |
                     v
              SERVER-SIDE MAPPING
                     |
                     v
                 URL POLICY
                     |
                     v
               DNS/IP POLICY
                     |
                     v
                EGRESS PROXY
                     |
                     v
           APPROVED DESTINATION
```

For arbitrary public URL fetchers:

```text
Application
    |
    v
Isolated Fetch Service
    |
    +----X----> Internal Networks
    |
    +---------> Approved Public Internet
```


# Final Testing Principle

The core SSRF question is:

```text
CAN USER-CONTROLLED INPUT
          |
          v
CAUSE THE APPLICATION
          |
          v
TO INITIATE A SERVER-SIDE REQUEST
          |
          v
TO A DESTINATION THE USER CONTROLS?
```

A strong workflow is:

```text
Find URL-Like Input
        |
        v
Establish Baseline
        |
        v
Use Controlled Destination
        |
        v
Observe DNS / HTTP
        |
        v
Repeat With Unique Token
        |
        v
Understand Destination Controls
        |
        v
Test Redirect Behaviour
        |
        v
Internal Validation if Authorised
        |
        v
Determine Real Impact
        |
        v
Capture Evidence
        |
        v
Remediate Root Cause
        |
        v
Retest Controls
```

For every SSRF candidate ask:

```text
Does the application actually make a request?

Or does the browser make it?

Can I prove server-side interaction?

Did I observe DNS only?

Did I observe HTTP?

Can I correlate the callback using a unique identifier?

Does the application return destination content?

What schemes are accepted?

Can the destination hostname be controlled?

Can the destination port be controlled?

Are private addresses blocked?

Is loopback blocked?

Is IPv6 handled?

Are redirects followed?

Are redirect targets revalidated?

Does DNS resolution occur before or after validation?

Does the application use a proxy?

Does a background worker make the request?

Are credentials automatically attached?

Is internal network testing authorised?

Is cloud metadata testing authorised?

What impact was actually demonstrated?

What impact is only theoretical?

Has the root cause been fixed rather than one URL string blocked?
```

The strongest SSRF finding is not:

```text
The parameter looks like a URL.
```

It is:

```text
CONTROLLED INPUT
      |
      v
SERVER-SIDE INTERACTION
      |
      v
REPEATABLE EVIDENCE
      |
      v
DEMONSTRATED REACHABILITY
      |
      v
SECURITY IMPACT
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [curl Cheatsheet](curl.md)
- [SQL Injection Cheatsheet](sql-injection.md)
- [XSS Cheatsheet](xss.md)
- [Content Discovery Cheatsheet](content-discovery.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [SSRF](../web/ssrf.md)
- [XXE](../web/xxe.md)
- [Open Redirect](../web/open-redirect.md)
- [Host Header Attacks](../web/host-header-attacks.md)
- [API Security](../web/api-security.md)
- [File Upload](../web/file-upload.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - Server-Side Request Forgery](https://portswigger.net/web-security/ssrf){ target="_blank" rel="noopener noreferrer" }
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for SSRF](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery){ target="_blank" rel="noopener noreferrer" }
- [Burp Suite Documentation - Collaborator](https://portswigger.net/burp/documentation/collaborator){ target="_blank" rel="noopener noreferrer" }
- [ProjectDiscovery Interactsh](https://github.com/projectdiscovery/interactsh){ target="_blank" rel="noopener noreferrer" }
- [AWS EC2 Instance Metadata Service](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Azure Instance Metadata Service](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service){ target="_blank" rel="noopener noreferrer" }
- [Google Cloud Compute Engine - VM Metadata](https://cloud.google.com/compute/docs/metadata/overview){ target="_blank" rel="noopener noreferrer" }


!!! tip "Prove the server-side request first"

    Before testing internal addresses or cloud metadata, submit a unique URL pointing to assessment-controlled infrastructure. A correlated HTTP interaction gives you a clean foundation for the rest of the SSRF assessment.


!!! tip "DNS and HTTP are different evidence"

    A DNS interaction demonstrates that the supplied hostname was resolved by an application-side component. An HTTP interaction provides stronger evidence that an outbound HTTP request was actually initiated. Record the distinction in your notes and report.


!!! tip "Use known internal test services"

    When internal SSRF validation is authorised, a known organisation-provided test service produces stronger and safer evidence than scanning large internal address or port ranges.


!!! tip "Review redirects separately"

    A destination allowlist may protect the first request but fail when the HTTP client follows a redirect. The redirect destination should be subjected to the same security policy as the original URL.


!!! warning "Do not jump directly to cloud metadata"

    Cloud metadata can contain sensitive workload information and credentials. Establish the SSRF primitive first and test metadata services only when that level of validation is explicitly authorised.


!!! warning "Blocklists are difficult to get right"

    Blocking strings such as `127.0.0.1` is not a complete SSRF defence. Secure implementations need consistent URL parsing, destination policy enforcement, resolved-address validation, redirect validation and network-level egress restrictions.
