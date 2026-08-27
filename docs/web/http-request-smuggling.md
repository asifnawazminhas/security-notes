# HTTP Request Smuggling

HTTP Request Smuggling, also known as HTTP desynchronisation or HTTP desync, occurs when multiple HTTP components disagree about where one request ends and the next request begins.

Modern web applications frequently sit behind multiple infrastructure components.

A request may travel through:

```text
Client
  ↓
CDN
  ↓
Reverse Proxy
  ↓
Load Balancer
  ↓
WAF
  ↓
Web Server
  ↓
Application
```

If two components interpret the boundaries of an HTTP request differently, an attacker may be able to cause part of one request to be interpreted as the beginning of another.

Conceptually:

```text
Attacker Request
      ↓
Front-End Server
      ↓
Interprets Request Boundary A
      ↓
Back-End Server
      ↓
Interprets Request Boundary B
      ↓
Connection Becomes Desynchronised
```

This can potentially affect subsequent requests using the same back-end connection.

Possible consequences include:

```text
Access-control bypass
Front-end security bypass
Web cache poisoning
Web cache deception
Request routing manipulation
Session confusion
Response queue poisoning
Credential exposure
Cross-site scripting
Request interception
Access to internal endpoints
Other users receiving incorrect responses
```

HTTP request smuggling is highly architecture dependent.

!!! warning "Authorised Security Testing"
    HTTP request smuggling testing can affect other users because requests may share persistent back-end connections. Perform testing only against systems for which you have explicit authorisation. Prefer isolated test environments, PortSwigger Web Security Academy labs, staging systems and low-impact detection techniques. Stop testing once sufficient evidence has been collected.

---

# Understanding HTTP Request Boundaries

HTTP servers need to determine where the body of a request ends.

In HTTP/1.1, two important mechanisms are:

```text
Content-Length
Transfer-Encoding
```

For example:

```http
POST / HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

hello=world
```

The server uses:

```http
Content-Length: 11
```

to determine the size of the body.

Another mechanism is chunked transfer encoding:

```http
Transfer-Encoding: chunked
```

Conceptually:

```text
HTTP Request
     ↓
Determine Body Length
     ↓
Read Body
     ↓
Next Request Begins
```

Problems occur when different servers disagree about this process.

---

# Typical Architecture

Consider:

```text
Internet
   ↓
Front-End Server
   ↓
Persistent Back-End Connection
   ↓
Application Server
```

The front end may process requests from multiple clients and forward them over persistent connections.

For example:

```text
Client A ─┐
Client B ─┼── Front End ─── Back End
Client C ─┘
```

Normally:

```text
Request A
Request B
Request C
```

remain correctly separated.

With desynchronisation:

```text
Attacker Request
       ↓
Front End sees:

[ Request A ]

Back End sees:

[ Request A ][ Partial Request B ]
```

The leftover data can affect a subsequent request.

---

# Core Request Smuggling Concept

The basic issue is:

```text
Front End
   ↓
Request Length = X

Back End
   ↓
Request Length = Y
```

where:

```text
X ≠ Y
```

This causes the two systems to disagree about request boundaries.

---

# Classic HTTP Request Smuggling

Classic request smuggling generally involves disagreement between:

```text
Content-Length
```

and:

```text
Transfer-Encoding
```

The traditional categories are:

```text
CL.TE
TE.CL
TE.TE
```

The notation indicates which mechanism each server uses.

---

# CL.TE

CL.TE means:

```text
Front End
   ↓
Content-Length

Back End
   ↓
Transfer-Encoding
```

Conceptually:

```text
             Front End
                 ↓
          Content-Length
                 ↓
          Entire Request
                 ↓
             Back End
                 ↓
        Transfer-Encoding
                 ↓
Different Request Boundary
```

A deliberately simplified structure looks like:

```http
POST / HTTP/1.1
Host: target.example
Content-Length: ...
Transfer-Encoding: chunked

...
```

The exact body structure depends on the target and should be calculated carefully rather than copied blindly.

---

# TE.CL

TE.CL is the reverse.

```text
Front End
   ↓
Transfer-Encoding

Back End
   ↓
Content-Length
```

Conceptually:

```text
             Front End
                 ↓
        Transfer-Encoding
                 ↓
             Back End
                 ↓
          Content-Length
                 ↓
Different Request Boundary
```

Again, the important concept is not a specific payload.

It is the disagreement:

```text
Front End Boundary
        ≠
Back End Boundary
```

---

# TE.TE

TE.TE occurs when both servers support `Transfer-Encoding`, but one server can be induced to ignore or interpret the header differently.

Conceptually:

```text
Front End
   ↓
Recognises Transfer-Encoding

Back End
   ↓
Does Not Recognise Equivalent Header
```

or the reverse.

Historically, research has explored ambiguous variations of the header.

Modern infrastructure is generally stricter about malformed HTTP, so these techniques are increasingly dependent on implementation-specific parsing differences.

---

# Content-Length

Example:

```http
Content-Length: 20
```

means the server expects 20 bytes of request body.

Conceptually:

```text
Headers
   ↓
Content-Length = N
   ↓
Read N Bytes
   ↓
Next Request
```

---

# Transfer-Encoding

HTTP/1.1 may use:

```http
Transfer-Encoding: chunked
```

A chunked body consists conceptually of:

```text
Chunk Size
Chunk Data

Chunk Size
Chunk Data

0
```

The terminating zero-sized chunk indicates the end of the body.

Request smuggling becomes possible when another component uses a different method for determining that boundary.

---

# Detecting HTTP Request Smuggling

A useful methodology is:

```text
Identify Architecture
        ↓
Determine HTTP Version
        ↓
Inspect Proxy Behaviour
        ↓
Identify Front-End / Back-End Differences
        ↓
Test Request Framing
        ↓
Use Timing-Based Detection
        ↓
Use Differential Responses
        ↓
Confirm Carefully
        ↓
Determine Impact
```

Do not begin by attempting to interfere with another user's request.

Start with detection.

---

# Burp Suite Workflow

Burp Suite is particularly useful for HTTP request smuggling testing.

A practical workflow is:

```text
Burp Proxy
     ↓
HTTP History
     ↓
Interesting Request
     ↓
Send to Repeater
     ↓
Inspect HTTP Version
     ↓
Modify Request Framing
     ↓
Send Controlled Test
     ↓
Observe Timing / Response
```

Burp Repeater allows requests to be manually modified and resent while comparing application behaviour.

---

# Burp Repeater

Send an interesting request to Repeater:

```text
Proxy
  ↓
HTTP History
  ↓
Right Click
  ↓
Send to Repeater
```

Then inspect:

```text
HTTP version
Content-Length
Transfer-Encoding
Connection behaviour
Response timing
Response status
Connection reuse
```

Repeater is useful because request smuggling testing often requires precise control over HTTP messages.

---

# Disable Automatic Content-Length Updating

When manually testing HTTP/1 request framing, be aware that Burp may automatically update `Content-Length`.

Depending on the test, you may need precise control over this value.

Check the Repeater settings and Inspector when constructing controlled requests.

The important point is:

```text
Automatic Request Normalisation
             ↓
May Change Test Request
```

Always verify the exact request being sent.

---

# HTTP Request Smuggler

One of the most useful Burp extensions for request smuggling research is:

```text
HTTP Request Smuggler
```

It was developed by PortSwigger researcher James Kettle and automates testing for numerous HTTP desynchronisation techniques.

The extension can assist with identifying:

```text
CL.TE
TE.CL
TE.TE
HTTP/2 desync
H2.CL
H2.TE
CL.0
Other parser discrepancies
```

depending on the version and target architecture.

---

# Installing HTTP Request Smuggler

In Burp Suite:

```text
Burp Suite
    ↓
Extensions
    ↓
BApp Store
    ↓
Search
    ↓
HTTP Request Smuggler
    ↓
Install
```

After installation, the extension becomes available within Burp.

The exact menus can change between Burp releases, but the extension can normally be accessed from relevant request context menus.

---

# HTTP Request Smuggler Workflow

A typical authorised workflow is:

```text
Browse Target
     ↓
Burp Proxy
     ↓
HTTP History
     ↓
Select Interesting Request
     ↓
Send / Launch Request Smuggling Test
     ↓
HTTP Request Smuggler
     ↓
Automated Desync Probes
     ↓
Review Findings
     ↓
Manually Confirm
```

The extension should be treated as:

```text
Detection Assistant
```

rather than:

```text
Automatic Proof of Vulnerability
```

Always manually investigate interesting results.

---

# Example HTTP Request Smuggler Usage

Suppose Burp contains:

```http
POST /search HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 9

q=testing
```

A workflow might be:

```text
1. Capture the request in Burp.

2. Confirm the host is explicitly authorised.

3. Send the request to Repeater.

4. Establish the normal baseline behaviour.

5. Right-click the request.

6. Launch the HTTP Request Smuggler extension.

7. Run the appropriate detection checks.

8. Review reported anomalies.

9. Send suspected cases to Repeater.

10. Manually verify the behaviour.

11. Stop once sufficient evidence exists.
```

Do not automatically assume every timeout means request smuggling.

Possible causes include:

```text
Rate limiting
Network latency
WAF behaviour
Connection timeout
Application slowness
Proxy timeout
Server instability
```

Manual confirmation is important.

---

# HTTP Request Smuggler Results

Interesting findings may indicate:

```text
Possible CL.TE
Possible TE.CL
Possible CL.0
Possible HTTP/2 desync
Timeout anomaly
Differential response
Connection anomaly
Parser discrepancy
```

The next step should be:

```text
Automated Detection
       ↓
Manual Reproduction
       ↓
Controlled Confirmation
       ↓
Impact Assessment
```

---

# Timing-Based Detection

Timing behaviour can help identify parser disagreements.

Conceptually:

```text
Send Ambiguous Request
        ↓
One Server Waits for More Data
        ↓
Connection Delays
        ↓
Potential Desynchronisation Indicator
```

A suspicious delay may suggest that one server believes the request is incomplete while another believes it is complete.

However:

```text
Timeout ≠ Vulnerability
```

Always repeat the test and compare against baseline behaviour.

---

# Differential Response Testing

Another useful technique is observing whether a carefully controlled request affects the interpretation of a subsequent request.

Conceptually:

```text
Probe Request
     ↓
Potential Desync
     ↓
Follow-Up Request
     ↓
Unexpected Response
```

Examples of unexpected behaviour may include:

```text
404 instead of 200
Different redirect
Different response body
Unexpected headers
Connection reset
Unexpected application route
```

Use endpoints you control where possible.

---

# Self-Contained Confirmation

The safest confirmation attempts to affect only your own subsequent request.

Conceptually:

```text
Your Request A
      ↓
Potential Smuggled Prefix
      ↓
Your Request B
      ↓
Observable Difference
```

This is preferable to attempting to interfere with unrelated users.

---

# CL.0 Request Smuggling

CL.0 vulnerabilities represent another form of desynchronisation.

The general idea is:

```text
Front End
   ↓
Uses Content-Length

Back End
   ↓
Effectively Treats Body Length as Zero
```

Conceptually:

```text
POST Request
Content-Length: N

BODY
```

Front end:

```text
BODY belongs to current request
```

Back end:

```text
Current request has no body

BODY becomes next request data
```

This creates:

```text
CL.0
```

desynchronisation.

---

# Why CL.0 Is Interesting

Traditional request smuggling testing focused heavily on:

```text
CL.TE
TE.CL
```

CL.0 demonstrates that request smuggling does not necessarily require both:

```text
Content-Length
```

and:

```text
Transfer-Encoding
```

The vulnerability can arise simply because a back-end endpoint does not consume the body in the way expected by the front end.

---

# CL.0 Candidate Endpoints

Interesting endpoints may include those that:

```text
Expect no request body
Return early
Redirect immediately
Serve static content
Produce server-level errors
Reject unsupported methods
```

Conceptually:

```text
Front End
   ↓
Forwards Body

Back End
   ↓
Responds Before Consuming Body

Remaining Bytes
   ↓
Next Request
```

This is why early-response behaviour is important during modern desync testing.

---

# Client-Side Desync

Client-side desynchronisation extends desync concepts to the browser.

Conceptually:

```text
Browser
   ↓
Front-End Server
   ↓
Connection Becomes Desynchronised
   ↓
Subsequent Browser Request
   ↓
Unexpected Interpretation
```

This differs from traditional request smuggling because the browser itself can participate in triggering the desynchronisation.

---

# Browser-Powered Request Smuggling

Modern request smuggling research has demonstrated that some desync vulnerabilities can be triggered using browser-compatible requests.

This creates potential attack flows such as:

```text
Victim Browser
      ↓
Attacker-Controlled Page
      ↓
Request to Vulnerable Site
      ↓
Connection Desynchronised
      ↓
Subsequent Request Affected
```

These techniques are considerably more advanced than traditional CL.TE testing.

Use PortSwigger's dedicated Web Security Academy labs when learning them.

---

# HTTP/2

HTTP/2 handles message framing differently from HTTP/1.1.

HTTP/2 uses binary frames:

```text
HTTP/2 Connection
       ↓
HEADERS Frame
       ↓
DATA Frame
       ↓
Built-In Frame Length
```

This largely removes the classic ambiguity around:

```text
Content-Length
Transfer-Encoding
```

when HTTP/2 is used end to end.

However, problems can appear when HTTP/2 is downgraded.

---

# HTTP/2 Downgrading

A common architecture is:

```text
Client
  ↓
HTTP/2
  ↓
Front End
  ↓
HTTP/1.1
  ↓
Back End
```

The front end must translate:

```text
HTTP/2
```

into:

```text
HTTP/1.1
```

This conversion may introduce request framing inconsistencies.

---

# H2.CL

H2.CL means:

```text
Front End
   ↓
HTTP/2 Framing

Back End
   ↓
Content-Length
```

Conceptually:

```text
HTTP/2 Request
      ↓
Front End
      ↓
Downgrade
      ↓
HTTP/1.1 + Content-Length
      ↓
Back End
```

If the generated `Content-Length` and actual request body are interpreted differently, desynchronisation may occur.

---

# H2.TE

H2.TE involves:

```text
HTTP/2
   ↓
Front End
   ↓
Downgrade
   ↓
Transfer-Encoding
   ↓
Back End
```

Again, the security issue exists because:

```text
Front-End Interpretation
          ≠
Back-End Interpretation
```

---

# Testing HTTP/2 in Burp

Burp Repeater allows requests to be sent using HTTP/1 or HTTP/2 where supported.

When testing a target, compare:

```text
HTTP/1 Behaviour
        vs
HTTP/2 Behaviour
```

Interesting differences include:

```text
Different status codes
Different headers
Different redirects
Different WAF behaviour
Different routing
Different request normalization
```

---

# Burp Inspector and HTTP/2

Burp's Inspector is useful for manipulating HTTP/2-specific request components.

HTTP/2 includes pseudo-headers such as:

```text
:method
:path
:authority
:scheme
```

These are conceptually equivalent to important pieces of the HTTP/1 request.

Understanding them is important when investigating HTTP/2 request smuggling.

---

# HTTP/2 Pseudo-Headers

A simplified HTTP/2 request may contain:

```text
:method = GET
:path = /
:authority = example.com
:scheme = https
```

Instead of:

```http
GET / HTTP/1.1
Host: example.com
```

HTTP/2 uses structured pseudo-header fields.

---

# Response Queue Poisoning

A particularly serious consequence of desynchronisation is response queue poisoning.

Normally:

```text
Request A → Response A
Request B → Response B
Request C → Response C
```

After desynchronisation:

```text
Request A → Response A
Request B → Response C
Request C → Response D
```

Responses become associated with the wrong requests.

This can potentially expose responses intended for other users.

Because of the potential impact on unrelated users, this should not be tested aggressively against production environments.

---

# Front-End Security Bypass

A front-end server may enforce security controls such as:

```text
Authentication
IP restrictions
WAF rules
Path restrictions
Rate limiting
Access control
```

But the back end may trust requests received from the front end.

Conceptually:

```text
Internet
   ↓
Security Controls
   ↓
Front End
   ↓
Back End
```

If a request can be smuggled through an already accepted front-end request, the back end may process something the front end never independently validated.

---

# Internal Header Discovery

Front-end servers frequently add internal headers.

For example:

```text
X-Forwarded-For
X-Forwarded-Host
X-Real-IP
X-Original-URL
Internal routing headers
Authentication headers
```

Request smuggling research sometimes involves determining how the front end rewrites requests before forwarding them.

This can reveal important information about the internal architecture.

---

# Web Cache Poisoning

Request smuggling may sometimes be chained with caching behaviour.

Conceptually:

```text
Request Smuggling
      ↓
Back-End Response Manipulation
      ↓
Cache Stores Response
      ↓
Other Users Receive Response
```

This can increase the persistence and impact of a desync vulnerability.

Related notes:

```text
Web Cache Poisoning
Web Cache Deception
HTTP Host Header Attacks
```

should eventually have their own dedicated pages.

---

# Request Smuggling and XSS

A desynchronisation issue can sometimes be combined with reflected XSS.

Conceptually:

```text
Smuggled Request
      ↓
Reflected Input
      ↓
Response
      ↓
Response Associated With Another Request
```

This demonstrates why the impact of request smuggling can extend beyond request routing.

---

# Request Smuggling and Authentication

Consider:

```text
Front End
    ↓
Authentication Check
    ↓
Back End
```

If a smuggled request reaches the back end without passing through the expected front-end processing path, authentication assumptions may break.

Potentially interesting areas include:

```text
/admin
/internal
/api/admin
/debug
/management
```

Only test endpoints explicitly included in the assessment scope.

---

# Request Smuggling and WAFs

Architecture:

```text
Internet
   ↓
WAF
   ↓
Reverse Proxy
   ↓
Application
```

If:

```text
WAF Parser
     ≠
Application Parser
```

the WAF may inspect a different request than the application ultimately processes.

This general class of problem is often called:

```text
Parser Differential
```

Request smuggling is fundamentally a parser differential vulnerability.

---

# Identifying Infrastructure

Before testing, fingerprint the architecture.

Useful indicators include:

```text
Server headers
Via
X-Cache
X-Served-By
X-Forwarded headers
CDN headers
Load-balancer cookies
TLS certificates
DNS records
HTTP/2 support
HTTP/3 support
Response behaviour
```

Tools include:

```text
Burp Suite
curl
httpx
Nmap
testssl.sh
Browser DevTools
```

---

# curl

Check protocol support:

```bash
curl -I https://target.example/
```

Verbose output:

```bash
curl -vk https://target.example/
```

Test HTTP/1.1:

```bash
curl --http1.1 -vk https://target.example/
```

Test HTTP/2:

```bash
curl --http2 -vk https://target.example/
```

Compare behaviour.

---

# httpx

For authorised infrastructure discovery:

```bash
httpx -u https://target.example -title -status-code -tech-detect
```

This can help identify:

```text
Status
Title
Technology
Server behaviour
```

It is not a request-smuggling detector by itself.

---

# Connection Reuse

Persistent connections are central to many request smuggling vulnerabilities.

Conceptually:

```text
Front End
    ↓
Connection 1
    ↓
Request A
Request B
Request C
```

If the back end believes part of Request A belongs to Request B:

```text
Request Boundary Corruption
```

occurs.

This is why simply replaying requests over separate TCP connections may fail to demonstrate certain desync behaviours.

---

# Burp Repeater Request Groups

Burp Repeater supports grouped requests.

This can be useful for carefully controlled sequences such as:

```text
Probe Request
      ↓
Follow-Up Request
```

Testing on the same connection can be relevant for desynchronisation research.

Always verify whether the requests are actually using:

```text
Same Connection
```

or:

```text
Separate Connections
```

because the result can differ significantly.

---

# Establish a Baseline

Before testing:

```text
Send Normal Request
       ↓
Record Response
       ↓
Repeat Several Times
       ↓
Establish Stable Behaviour
```

Record:

```text
Status code
Response length
Response time
Headers
Redirects
Cookies
Connection behaviour
```

Only then introduce request-framing changes.

---

# Testing Methodology

A structured approach is:

```text
1. Confirm scope

2. Identify HTTP architecture

3. Determine HTTP versions

4. Establish normal baseline

5. Check for front-end infrastructure

6. Send request to Burp Repeater

7. Test low-impact framing discrepancies

8. Use HTTP Request Smuggler

9. Review timing anomalies

10. Review differential responses

11. Investigate CL.TE / TE.CL where appropriate

12. Investigate HTTP/2 downgrade behaviour

13. Investigate CL.0 behaviour

14. Confirm using your own requests

15. Determine security impact

16. Stop once sufficient evidence exists

17. Document the complete architecture and behaviour
```

---

# Request Smuggling Decision Tree

```text
Target
  ↓
HTTP/1.1 or HTTP/2?
  ↓
Is There a Front End?
  ↓
Are Connections Reused?
  ↓
Do Components Parse Requests Differently?
  ↓
CL.TE?
TE.CL?
TE.TE?
H2.CL?
H2.TE?
CL.0?
  ↓
Can Behaviour Be Reproduced?
  ↓
Can Own Follow-Up Request Be Affected?
  ↓
What Security Boundary Is Bypassed?
```

---

# False Positives

Request smuggling testing can produce misleading behaviour.

Possible causes include:

```text
Slow application
WAF rate limiting
CDN retries
Load balancer behaviour
Network latency
Connection pool exhaustion
Server errors
Application crashes
Request normalization
Proxy buffering
```

Therefore:

```text
One Timeout
    ≠
Confirmed Request Smuggling
```

Look for reproducible behaviour.

---

# Evidence Collection

For each candidate, record:

```text
Target
Endpoint
HTTP version
Front-end technology
Back-end technology if known
Request type
Desync classification
Original request
Modified request
Timing behaviour
Response behaviour
Connection behaviour
HTTP Request Smuggler output
Manual confirmation
Security impact
Timestamp
```

---

# Example Evidence Record

```text
HRS-001

Endpoint:
POST /search

HTTP Version:
HTTP/1.1

Candidate:
CL.TE

Detection:
HTTP Request Smuggler

Observation:
Consistent timing anomaly

Manual Confirmation:
Controlled follow-up request affected

Affected User:
Tester only

Status:
Confirmed for further impact assessment
```

---

# Reporting

A request smuggling report should explain the infrastructure clearly.

For example:

```text
Client
  ↓
Reverse Proxy
  ↓
Application Server
```

Then describe the parsing difference:

```text
Reverse Proxy
     ↓
Uses Content-Length

Application Server
     ↓
Uses Transfer-Encoding
```

This causes:

```text
Request Boundary Disagreement
```

---

# Example Finding Title

```text
HTTP Request Smuggling Due to Front-End and Back-End Request Parsing Discrepancy
```

More specific:

```text
CL.TE HTTP Request Smuggling
```

or:

```text
HTTP/2 Downgrade Enables H2.CL Request Smuggling
```

or:

```text
CL.0 HTTP Desynchronisation
```

Use the most accurate classification established during testing.

---

# Impact

Potential impacts include:

```text
Authentication bypass
Authorisation bypass
WAF bypass
Internal endpoint access
Cache poisoning
Cache deception
Cross-site scripting
Request interception
Response queue poisoning
Credential exposure
Session compromise
User-to-user response confusion
```

The actual report should describe only the impact demonstrated or strongly established.

Do not automatically report every request smuggling vulnerability as critical.

---

# Remediation

The fundamental remediation is:

> Ensure every component in the HTTP request chain agrees unambiguously on request boundaries.

---

# Prefer HTTP/2 End to End

Where possible:

```text
Client
  ↓
HTTP/2
  ↓
Front End
  ↓
HTTP/2
  ↓
Back End
```

is preferable to:

```text
Client
  ↓
HTTP/2
  ↓
Front End
  ↓
Downgrade
  ↓
HTTP/1.1
  ↓
Back End
```

Protocol translation introduces additional parsing complexity.

---

# Reject Ambiguous Requests

Infrastructure should reject requests containing ambiguous framing.

For example, requests containing conflicting framing information should not be forwarded.

Conceptually:

```text
Ambiguous Request
      ↓
Front End
      ↓
Reject
```

rather than:

```text
Ambiguous Request
      ↓
Normalize
      ↓
Forward
```

unless normalization is guaranteed to produce identical interpretation across every component.

---

# Avoid Front-End / Back-End Parser Differences

Ensure:

```text
CDN
Reverse Proxy
Load Balancer
WAF
Web Server
Application Server
```

follow compatible request parsing rules.

Keep all infrastructure updated.

Request parsing vulnerabilities have historically appeared in many different HTTP implementations.

---

# Close Connections on Errors

Connection handling should prevent malformed or ambiguous requests from contaminating subsequent requests.

Conceptually:

```text
Malformed Request
       ↓
Reject
       ↓
Close Connection
```

This can help prevent residual bytes from affecting another request.

---

# Do Not Rely Solely on a WAF

A WAF cannot reliably compensate for inconsistent request parsing between infrastructure components.

If:

```text
WAF sees Request A
```

while:

```text
Application sees Request B
```

security controls may be bypassed.

Fix the parser discrepancy itself.

---

# HTTP Request Smuggling Quick Reference

```text
CL.TE

Front End  → Content-Length
Back End   → Transfer-Encoding
```

```text
TE.CL

Front End  → Transfer-Encoding
Back End   → Content-Length
```

```text
TE.TE

Both process Transfer-Encoding differently
```

```text
H2.CL

Front End  → HTTP/2 framing
Back End   → Content-Length after downgrade
```

```text
H2.TE

Front End  → HTTP/2 framing
Back End   → Transfer-Encoding after downgrade
```

```text
CL.0

Front End  → Content-Length
Back End   → Effectively ignores body
```

---

# Tools

Useful tools include:

```text
Burp Suite
Burp Repeater
Burp Inspector
HTTP Request Smuggler
Turbo Intruder
curl
httpx
Browser Developer Tools
```

---

# HTTP Request Smuggler

Primary Burp extension:

```text
HTTP Request Smuggler
```

Use it for:

```text
Automated desync detection
HTTP/1 request smuggling research
HTTP/2 desync research
CL.0 detection
Request framing analysis
```

Recommended workflow:

```text
HTTP Request Smuggler
        ↓
Candidate Finding
        ↓
Burp Repeater
        ↓
Manual Confirmation
        ↓
Impact Assessment
```

---

# PortSwigger Web Security Academy

PortSwigger provides extensive material and deliberately vulnerable labs covering HTTP request smuggling.

Topics include:

```text
CL.TE
TE.CL
TE.TE
Detection techniques
Security control bypass
Front-end request rewriting
HTTP/2 request smuggling
H2.CL
H2.TE
CL.0
Client-side desync
Browser-powered desync
Response queue poisoning
HTTP request tunnelling
```

These labs are highly recommended before testing complex desynchronisation behaviour against real infrastructure.

---

# References

## PortSwigger Web Security Academy

HTTP Request Smuggling:

https://portswigger.net/web-security/request-smuggling

This should be the primary learning reference for these notes.

---

## PortSwigger HTTP Request Smuggling Research

https://portswigger.net/research/request-smuggling

James Kettle's PortSwigger research provides extensive coverage of modern HTTP desynchronisation techniques.

---

## HTTP Desync Attacks: Request Smuggling Reborn

PortSwigger Research.

This research helped reintroduce HTTP request smuggling as a major modern web security topic and explored practical parser discrepancies in contemporary infrastructure.

---

## HTTP/2: The Sequel Is Always Worse

PortSwigger Research.

Important research covering:

```text
HTTP/2 downgrading
H2.CL
H2.TE
HTTP/2-exclusive vectors
```

---

## Browser-Powered Desync Attacks

PortSwigger Research.

Important for understanding:

```text
CL.0
Client-side desync
Browser-powered request smuggling
Pause-based desync
```

---

## HTTP Request Smuggler

Burp Suite extension developed for HTTP desynchronisation research.

Install through:

```text
Burp Suite
  ↓
Extensions
  ↓
BApp Store
  ↓
HTTP Request Smuggler
```

---

## OWASP

OWASP resources should also be consulted when reviewing HTTP request processing, proxy architecture and secure deployment practices.

https://owasp.org/

---

# Final Testing Workflow

```text
Target Application
       ↓
Identify Architecture
       ↓
CDN / WAF / Proxy / Load Balancer?
       ↓
Determine HTTP Versions
       ↓
Establish Baseline
       ↓
Burp Proxy
       ↓
Burp Repeater
       ↓
Inspect Request Framing
       ↓
HTTP Request Smuggler
       ↓
Automated Detection
       ↓
Candidate Found?
       ↓
Manual Reproduction
       ↓
CL.TE / TE.CL / TE.TE?
       ↓
HTTP/2 Downgrade?
       ↓
H2.CL / H2.TE?
       ↓
CL.0?
       ↓
Controlled Self-Contained Confirmation
       ↓
Determine Security Boundary Affected
       ↓
Collect Minimum Necessary Evidence
       ↓
Stop Testing
       ↓
Report
```

The key principle is:

> HTTP request smuggling is fundamentally a disagreement between HTTP parsers. Understand how each component determines request boundaries, use automation such as HTTP Request Smuggler to identify candidates, and then manually confirm the behaviour using controlled requests before determining the real security impact.
