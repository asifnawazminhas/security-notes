# Web Cache Poisoning

Web cache poisoning occurs when an attacker causes a web cache to store a malicious or unintended response that is subsequently served to other users.

Modern web applications frequently use caching infrastructure to improve:

```text
Performance
Scalability
Latency
Availability
Bandwidth usage
```

Caching may occur at several layers:

```text
Browser
CDN
Reverse proxy
Load balancer
Application cache
API gateway
Web server
```

A simplified architecture is:

```text
User
  ↓
CDN / Cache
  ↓
Reverse Proxy
  ↓
Application
```

Normally:

```text
Request
   ↓
Cache Lookup
   ↓
Cached Response Exists?
   ↓
YES → Return Cached Response
```

If no cached response exists:

```text
Request
   ↓
Cache MISS
   ↓
Application Processes Request
   ↓
Response Generated
   ↓
Response Stored
   ↓
Returned to User
```

Web cache poisoning becomes possible when attacker-controlled input affects the generated response but is not correctly represented in the cache key.

Conceptually:

```text
Attacker-Controlled Input
          ↓
Application Response
          ↓
Cache Stores Response
          ↓
Victim Requests Normal Page
          ↓
Victim Receives Poisoned Response
```

Potential impact includes:

```text
Cross-Site Scripting
Malicious redirects
Content manipulation
JavaScript injection
Sensitive information exposure
Denial of service
Authentication workflow manipulation
Cache-based persistence
```

!!! warning "Authorised Security Testing"
    Web cache poisoning can affect users other than the tester. During authorised assessments, use unique cache busters and controlled resources wherever possible. Do not deliberately poison shared production cache entries unless this has been explicitly authorised.

---

# Why Web Cache Poisoning Happens

A cache needs to determine whether two requests should receive the same cached response.

It does this using a:

```text
Cache Key
```

A simplified cache key might consist of:

```text
Scheme
Host
Path
Query string
```

For example:

```text
https://target.example/products?id=123
```

may produce a cache key based on:

```text
target.example
/products
id=123
```

However, the application may also use other request data when generating the response.

Examples include:

```text
X-Forwarded-Host
X-Forwarded-Proto
X-Original-URL
X-Rewrite-URL
User-Agent
Accept-Language
Origin
Cookies
Custom headers
```

If the application uses a value that the cache ignores, a discrepancy can occur.

---

# Cache Key vs Application Input

This is the central concept behind web cache poisoning.

Consider:

```text
CACHE KEY

Host
Path
Query
```

while the application also processes:

```text
X-Forwarded-Host
```

If `X-Forwarded-Host` changes the response but is not part of the cache key:

```text
Attacker Request
       ↓
X-Forwarded-Host: controlled.example
       ↓
Application Generates:
https://controlled.example/script.js
       ↓
Cache Stores Response Under:
target.example/
       ↓
Victim Requests:
target.example/
       ↓
Victim Receives Cached Response
Containing controlled.example
```

The unkeyed input has poisoned the cached response.

---

# Cache Keys

A cache key determines which requests are considered equivalent.

Potential components include:

```text
Host
Path
Query parameters
HTTP method
Selected headers
Cookies
Protocol
```

The exact implementation depends on:

```text
CDN
Reverse proxy
Application
Cache configuration
Framework
```

---

# Keyed Inputs

A keyed input contributes to the cache key.

Suppose:

```text
Accept-Language
```

is part of the cache key.

Then:

```http
Accept-Language: en
```

and:

```http
Accept-Language: nl
```

may produce separate cache entries.

This prevents one language variant from being incorrectly served to another.

---

# Unkeyed Inputs

An unkeyed input affects the application response but does not contribute to the cache key.

This is particularly interesting during testing.

Conceptually:

```text
Unkeyed Input
     ↓
Changes Response
     ↓
Cache Does Not Distinguish Request
     ↓
Modified Response Stored
     ↓
Normal Users Receive It
```

---

# Cache Poisoning Testing Methodology

A structured workflow is:

```text
Identify Cache
      ↓
Find Cacheable Endpoint
      ↓
Understand Cache Key
      ↓
Add Unique Cache Buster
      ↓
Identify Unkeyed Inputs
      ↓
Determine Whether Input Changes Response
      ↓
Determine Whether Response Is Cached
      ↓
Request Same Cache Key Without Input
      ↓
Check Whether Modification Persists
      ↓
Assess Security Impact
      ↓
Report
```

The most important rule during testing is:

> Avoid contaminating cache entries used by real users.

---

# Identifying a Cache

Look for response headers such as:

```text
Age
X-Cache
X-Cache-Hits
CF-Cache-Status
Via
X-Served-By
X-Proxy-Cache
X-Varnish
Cache-Control
Expires
ETag
Last-Modified
```

Examples:

```http
X-Cache: HIT
```

```http
X-Cache: MISS
```

```http
CF-Cache-Status: HIT
```

```http
Age: 120
```

These can indicate caching behaviour.

---

# Cache HIT

A response may contain:

```http
X-Cache: HIT
```

This generally indicates that the response was served from cache.

Another common indicator is:

```http
Age: 42
```

If the value increases between requests, this may indicate that the same cached object is being reused.

---

# Cache MISS

A response may contain:

```http
X-Cache: MISS
```

This generally indicates that the cache did not contain a suitable response and forwarded the request to the backend.

A common sequence is:

```text
First Request
    ↓
MISS

Second Request
    ↓
HIT
```

---

# Dynamic Cache Headers

Different providers use different terminology.

Examples include:

```text
HIT
MISS
BYPASS
DYNAMIC
STALE
REVALIDATED
EXPIRED
```

Do not rely on header names alone.

Confirm behaviour through repeated requests.

---

# Establishing a Baseline

Start with a normal request.

```http
GET / HTTP/1.1
Host: target.example
```

Record:

```text
Status code
Response length
Cache headers
Age
ETag
Response body
Response time
```

Send the same request again.

Compare the responses.

---

# Cache Busters

A cache buster creates a unique cache entry for testing.

For example:

```text
/?cb=AM123456
```

Request:

```http
GET /?cb=AM123456 HTTP/1.1
Host: target.example
```

This reduces the chance that testing affects ordinary visitors.

---

# Why Cache Busters Matter

Without a cache buster:

```text
Tester
  ↓
Poisons /
  ↓
Cache
  ↓
Real Users Request /
  ↓
Poisoned Response
```

With a unique cache buster:

```text
Tester
  ↓
Poisons /?cb=AM123456
  ↓
Unique Cache Entry
  ↓
Normal Users Request /
  ↓
Different Cache Entry
```

This is much safer during authorised testing.

---

# Verify That the Cache Buster Is Keyed

Do not assume every query parameter is part of the cache key.

Some caches ignore selected parameters.

Test:

```text
/?cb=AM111
```

and:

```text
/?cb=AM222
```

Compare:

```text
Cache status
Age
Response
```

Ensure the values create separate cache entries before relying on them for safe testing.

---

# Query Parameter Handling

Caches may:

```text
Include all query parameters
Ignore all query parameters
Ignore selected parameters
Normalise parameter order
Remove tracking parameters
Sort parameters
```

For example:

```text
utm_source
utm_campaign
fbclid
gclid
```

may sometimes be excluded from cache keys.

Do not use a parameter as a safety cache buster until you know it is keyed.

---

# Unkeyed Header Discovery

Headers are common candidates for unkeyed inputs.

Interesting examples include:

```text
X-Forwarded-Host
X-Forwarded-Proto
X-Forwarded-Port
X-Original-URL
X-Rewrite-URL
X-Host
X-Forwarded-Server
X-HTTP-Host-Override
X-Original-Host
Forwarded
Origin
Referer
Accept-Language
User-Agent
```

Not every application processes these headers.

Test systematically.

---

# Harmless Canary Testing

Start with a unique harmless marker.

Example:

```http
X-Forwarded-Host: am-cache-001.example
```

Then search the response for:

```text
am-cache-001.example
```

Possible reflection points include:

```text
Absolute URLs
Canonical links
Script sources
Stylesheets
Redirects
Forms
API responses
Meta tags
```

---

# Example Reflection

Request:

```http
GET /?cb=AM001 HTTP/1.1
Host: target.example
X-Forwarded-Host: am-cache-001.example
```

Response:

```html
<script src="https://am-cache-001.example/resources/app.js"></script>
```

This establishes that:

```text
X-Forwarded-Host
```

influences the response.

The next question is:

> Is this response cached without `X-Forwarded-Host` being part of the cache key?

---

# Confirming Unkeyed Behaviour

Send:

```http
GET /?cb=AM001 HTTP/1.1
Host: target.example
X-Forwarded-Host: am-cache-001.example
```

Then request:

```http
GET /?cb=AM001 HTTP/1.1
Host: target.example
```

If the second response still contains:

```text
am-cache-001.example
```

and is served from cache, this suggests that the header affected the cached response while not being represented in the cache key.

---

# Safe Proof Model

The safest useful proof is often:

```text
Unique Cache Buster
       ↓
Harmless Canary
       ↓
Response Modified
       ↓
Response Cached
       ↓
Same Cache-Busted URL Requested Normally
       ↓
Canary Still Present
```

This demonstrates cache poisoning without injecting executable content.

---

# X-Forwarded-Host

One of the most important headers to test is:

```http
X-Forwarded-Host:
```

Example:

```http
GET /?cb=AM002 HTTP/1.1
Host: target.example
X-Forwarded-Host: controlled.example
```

Look for:

```text
https://controlled.example/
```

in the response.

---

# Why X-Forwarded-Host Is Interesting

Applications behind proxies may use:

```text
X-Forwarded-Host
```

to reconstruct the original hostname.

Architecture:

```text
Browser
   ↓
CDN
   ↓
Reverse Proxy
   ↓
Application
```

The application may assume:

```text
X-Forwarded-Host
```

was generated by trusted infrastructure.

If external clients can supply it directly, this assumption may fail.

---

# X-Forwarded-Proto

Another interesting header is:

```http
X-Forwarded-Proto:
```

For example:

```http
X-Forwarded-Proto: http
```

or:

```http
X-Forwarded-Proto: https
```

It may affect:

```text
Absolute URLs
Redirects
Canonical links
Cookie behaviour
Generated resources
```

---

# Forwarded

The standard `Forwarded` header may contain:

```http
Forwarded: host=controlled.example;proto=https
```

Test whether it affects the response.

Support varies significantly between applications and proxies.

---

# X-Original-URL and X-Rewrite-URL

Some infrastructure supports headers such as:

```http
X-Original-URL:
```

and:

```http
X-Rewrite-URL:
```

These may affect request routing.

For example:

```http
X-Original-URL: /admin
```

If such a header changes the generated response and the cache does not account for it, interesting discrepancies may arise.

---

# Web Cache Poisoning via Host Headers

Host-related headers are a classic cache poisoning source.

Refer to:

```text
docs/web/host-header-attacks.md
```

A common pattern is:

```text
Unkeyed Host Override
        ↓
Application Generates Absolute URL
        ↓
Modified URL Enters Response
        ↓
Response Cached
        ↓
Victims Receive Modified URL
```

---

# Cache Poisoning to Cross-Site Scripting

Cache poisoning can sometimes amplify another weakness into stored-like XSS behaviour.

Conceptually:

```text
Unkeyed Input
      ↓
Unsafe Reflection
      ↓
Executable Browser Context
      ↓
Response Cached
      ↓
Victims Receive Cached Response
      ↓
JavaScript Executes
```

The important chain is:

```text
Input controllable
+
Unsafe rendering
+
Cache persistence
+
Victim delivery
```

Refer to:

```text
docs/web/xss.md
```

---

# Harmless Validation Before XSS

During authorised testing, first establish:

```text
Reflection
Cache persistence
Cache key behaviour
```

using a harmless canary.

You usually do not need executable JavaScript to prove the cache poisoning primitive.

Only escalate testing when necessary and authorised.

---

# Cache Poisoning via Cookies

Cookies may influence application responses.

Example:

```http
Cookie: language=en
```

If:

```text
Cookie affects response
```

but:

```text
Cookie is not part of cache key
```

one user's response variant may potentially be served to another.

This can create:

```text
Content poisoning
Information disclosure
User-specific cache leakage
```

---

# User-Specific Data and Caching

A particularly serious configuration error occurs when authenticated or personalised responses are cached incorrectly.

Conceptually:

```text
User A
  ↓
Authenticated Request
  ↓
Personalised Response
  ↓
Shared Cache
  ↓
User B
  ↓
Receives User A Response
```

This may be better classified as:

```text
Sensitive data exposure through shared caching
```

rather than classic attacker-controlled cache poisoning.

Report the root cause accurately.

---

# Cache-Control

Review:

```http
Cache-Control:
```

Common directives include:

```text
public
private
no-cache
no-store
max-age
s-maxage
must-revalidate
```

---

# public

Example:

```http
Cache-Control: public
```

indicates that a response may be stored by shared caches.

This can be dangerous for personalised responses.

---

# private

Example:

```http
Cache-Control: private
```

indicates that the response is intended for private caches rather than shared caches.

This is commonly appropriate for personalised content.

---

# no-store

Example:

```http
Cache-Control: no-store
```

instructs caches not to store the response.

This is useful for highly sensitive responses.

---

# s-maxage

Example:

```http
Cache-Control: public, s-maxage=300
```

`s-maxage` applies to shared caches.

It may override other caching lifetimes for CDN or proxy caching.

---

# Vary

The `Vary` response header tells caches that selected request headers influence the response.

Example:

```http
Vary: Accept-Encoding
```

or:

```http
Vary: Origin
```

Conceptually:

```text
Response Changes Based On Origin
        ↓
Vary: Origin
        ↓
Cache Stores Separate Variants
```

---

# Missing Vary

Suppose an application changes its response based on:

```http
Origin:
```

but does not return:

```http
Vary: Origin
```

Depending on the caching architecture, responses intended for one origin may potentially be reused for another.

This can interact with:

```text
CORS
Cache poisoning
Cross-origin data exposure
```

Refer to:

```text
docs/web/cors.md
```

---

# Cache Poisoning and CORS

Consider:

```text
Request Origin
       ↓
Application Reflects Origin
       ↓
CORS Response
       ↓
Shared Cache
```

If:

```text
Origin
```

is not correctly represented in caching behaviour, an incorrect CORS policy may be cached.

Always inspect:

```http
Vary: Origin
```

when CORS responses are dynamically generated.

---

# Cache Poisoning and Redirects

A cacheable redirect influenced by unkeyed input can potentially poison navigation.

Example:

```http
HTTP/1.1 302 Found
Location: https://controlled.example/login
```

If cached:

```text
Victim
 ↓
Requests Normal URL
 ↓
Receives Cached Redirect
 ↓
Sent Elsewhere
```

This can overlap with:

```text
Open Redirect
Host Header Attacks
Cache Poisoning
```

Refer to:

```text
docs/web/open-redirect.md
```

---

# Cache Poisoning and Error Responses

Some caches store error responses.

Potential status codes include:

```text
301
302
404
403
500
```

depending on configuration.

This can sometimes produce:

```text
Cache poisoning
Denial of service
Unexpected content persistence
```

---

# Cacheable 404 Responses

Suppose attacker-controlled input changes how a route is resolved and causes:

```http
HTTP/1.1 404 Not Found
```

If the response is cached under a legitimate cache key, users may receive the cached error instead of valid content.

This can create a denial-of-service style cache poisoning condition.

---

# Cache Poisoning Denial of Service

Conceptually:

```text
Attacker Request
       ↓
Application Generates Error
       ↓
Error Cached
       ↓
Victims Request Resource
       ↓
Cached Error Returned
```

The impact depends on:

```text
Cache duration
Affected endpoint
Number of users
Ease of reproduction
Recovery behaviour
```

---

# Web Cache Poisoning vs Web Cache Deception

These are different vulnerability classes.

Web cache poisoning:

```text
Attacker influences cached response
        ↓
Victims receive attacker-influenced response
```

Web cache deception:

```text
Victim requests sensitive content
        ↓
Cache incorrectly stores it
        ↓
Attacker retrieves victim's cached response
```

Simplified:

```text
POISONING
Attacker → Cache → Victim

DECEPTION
Victim → Cache → Attacker
```

A separate page should cover:

```text
docs/web/web-cache-deception.md
```

---

# Cache Poisoning vs Stored XSS

Stored XSS:

```text
Payload
 ↓
Application Storage
 ↓
Victim
```

Cache poisoning:

```text
Payload
 ↓
Cache
 ↓
Victim
```

The persistence layer is different.

A cache-poisoning vulnerability can nevertheless deliver an XSS payload.

---

# Cache Poisoning vs HTTP Request Smuggling

HTTP request smuggling exploits disagreement about HTTP message boundaries.

Web cache poisoning exploits disagreement about:

```text
Which request inputs define a cached response?
```

The two can sometimes interact, but they are separate vulnerability classes.

Refer to:

```text
docs/web/http-request-smuggling.md
```

---

# Cache Key Normalisation

Caches may normalise request components before constructing a key.

Examples include:

```text
Lowercasing hostnames
Normalising paths
Removing default ports
Sorting query parameters
Ignoring selected parameters
Decoding characters
Normalising duplicate slashes
```

The backend may perform different normalisation.

This can create discrepancies.

---

# Path Normalisation

Consider:

```text
/products
/products/
/products//
```

Different components may treat these as:

```text
Same resource
```

or:

```text
Different resources
```

Differences between cache and origin behaviour can create unusual cache conditions.

---

# Query Parameter Normalisation

Consider:

```text
?a=1&b=2
```

and:

```text
?b=2&a=1
```

The application may consider these equivalent.

The cache may or may not.

Understanding parameter handling can help map the cache key.

---

# Parameter Exclusion

Some caching systems deliberately ignore selected query parameters.

Examples may include analytics parameters:

```text
utm_source
utm_medium
utm_campaign
```

If an ignored parameter affects the application response, it may become an unkeyed input.

---

# Parameter Cloaking

Applications, proxies and caches may parse query strings differently.

For example, different components may disagree about:

```text
Parameter delimiters
Duplicate parameters
Encoded delimiters
Parameter ordering
```

Conceptually:

```text
Cache Parser
    ↓
Interpretation A

Application Parser
    ↓
Interpretation B
```

Parser discrepancies can sometimes allow attacker-controlled values to affect the backend response without changing the cache key as expected.

---

# Duplicate Parameters

Example:

```text
?lang=en&lang=nl
```

Possible interpretations:

```text
First value
Last value
Array
Combined value
```

If the cache and application disagree, cache behaviour may become interesting.

This overlaps with HTTP parameter pollution.

---

# Cache Key Injection

Some advanced cache vulnerabilities involve manipulating data used to construct the cache key itself.

The general question is:

> Can attacker-controlled input cause the cache to confuse one request with another?

This can occur through:

```text
Header parsing differences
Delimiter handling
URL normalisation
Port handling
Host parsing
Query parsing
```

Such issues require careful manual analysis.

---

# Fat GET Requests

Some applications accept request bodies with GET requests.

Example:

```http
GET /search HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 9

q=example
```

A cache may key the response based on:

```text
GET + path
```

while ignoring the body.

If the application uses the body, this can create a cache discrepancy.

---

# GET Body Model

Conceptually:

```text
Cache
 ↓
GET /search
 ↓
Ignores Body

Application
 ↓
GET /search
 ↓
Processes Body
```

If the body changes the response:

```text
Unkeyed Request Body
```

may exist.

Support for GET bodies varies significantly.

---

# HTTP Method Handling

Check whether:

```text
GET
HEAD
POST
```

share unexpected cache behaviour.

For example, some caches may derive `HEAD` responses from cached `GET` responses.

Method handling should be understood before drawing conclusions.

---

# HEAD Requests

A `HEAD` request normally returns the same headers as `GET` without the body.

Test whether:

```text
HEAD
```

and:

```text
GET
```

interact unexpectedly with cache state.

---

# Static vs Dynamic Resources

Caching is common for:

```text
JavaScript
CSS
Images
Fonts
Static HTML
Public API responses
```

Dynamic resources may also be cached.

Prioritise endpoints where:

```text
Response is cacheable
+
Input influences response
```

---

# JavaScript Resources

Cached JavaScript is particularly sensitive.

Conceptually:

```text
Attacker Influences JavaScript Response
          ↓
Response Cached
          ↓
Victims Load Script
          ↓
Attacker-Controlled JavaScript Executes
```

This can have widespread impact.

Use harmless markers during initial testing.

---

# CSS Resources

CSS may also be cached for long periods.

While CSS injection usually has different impact from JavaScript injection, poisoning shared static resources can still affect many users.

---

# API Caching

APIs may be cached by:

```text
CDNs
API gateways
Reverse proxies
Application caches
```

Check whether responses vary by:

```text
Authentication
Tenant
Role
Language
Origin
Device
Region
```

and whether those dimensions are represented correctly in the cache key.

---

# Authentication and Caching

Authenticated responses deserve special attention.

Ask:

```text
Is this response cacheable?

Is the session cookie part of the cache key?

Is Authorization part of the cache key?

Does the CDN bypass authenticated requests?

Can a private response enter a shared cache?
```

---

# Authorization Header

Requests may contain:

```http
Authorization: Bearer TOKEN
```

Shared caches should handle authenticated responses carefully.

A serious issue can occur if:

```text
Response varies by Authorization
```

but:

```text
Shared cache does not distinguish users
```

---

# Cookie Handling

Caches often bypass requests containing session cookies.

But this is configuration-dependent.

Check rather than assume.

Example:

```http
Cookie: session=CONTROLLED_SESSION
```

Observe whether:

```text
X-Cache: HIT
```

still appears.

---

# Tenant Caching

Multi-tenant applications may vary responses by:

```text
Host
Tenant header
Cookie
JWT claim
Query parameter
```

If tenant identity is not properly represented in caching:

```text
Tenant A
   ↓
Cached Response
   ↓
Tenant B
```

cross-tenant data exposure may occur.

---

# Language Caching

Applications may vary by:

```http
Accept-Language:
```

or:

```text
?lang=
```

If the cache ignores the relevant value, users may receive another language variant.

This is usually low impact unless the variation also contains security-sensitive or user-specific data.

---

# Device-Specific Caching

Applications may vary responses based on:

```text
User-Agent
Device headers
Mobile detection
```

If the cache does not account for this, different clients may receive incorrect variants.

Again, impact depends on the content difference.

---

# Geographical Caching

CDNs may vary responses based on:

```text
Country
Region
Edge location
IP-derived information
```

Custom geographic headers should generally be trusted only when generated by known infrastructure.

---

# Cache Poisoning via X-Forwarded-Scheme

Some frameworks recognise headers that influence URL scheme.

Examples may include:

```text
X-Forwarded-Proto
X-Forwarded-Scheme
X-Forwarded-SSL
```

If these change response content and are unkeyed, investigate further.

---

# Cache Poisoning via Port

Generated URLs may use:

```text
X-Forwarded-Port
```

or the port included in:

```http
Host:
```

Example:

```text
https://target.example:8443/
```

Check whether port values influence cached responses.

---

# Multiple Cache Layers

Applications may have several caches.

Example:

```text
Browser
   ↓
Cloud CDN
   ↓
Reverse Proxy Cache
   ↓
Application Cache
   ↓
Origin
```

A response may therefore show confusing behaviour.

For example:

```text
CDN MISS
```

does not necessarily mean:

```text
Origin application generated response
```

because another downstream cache may have served it.

---

# Cache Layer Mapping

Useful headers may reveal cache layers:

```text
Via
X-Cache
Age
Server
CF-Ray
X-Served-By
X-Varnish
```

Build a mental model:

```text
Client
 ↓
CDN
 ↓
Proxy
 ↓
Origin
```

before attempting advanced cache analysis.

---

# Cache TTL

TTL means:

```text
Time To Live
```

It controls how long an object remains fresh in cache.

Example:

```http
Cache-Control: max-age=300
```

means:

```text
300 seconds
```

for relevant caching behaviour.

Long TTLs can increase the persistence of a poisoning issue.

---

# Age Header

Example:

```http
Age: 120
```

This can indicate how long the object has been stored by a cache.

Repeated requests may show:

```text
Age: 120
Age: 121
Age: 122
```

providing useful evidence that the same cached object is being served.

---

# Cache Revalidation

Caches may revalidate content using:

```text
ETag
If-None-Match
Last-Modified
If-Modified-Since
```

Example:

```http
ETag: "abc123"
```

Client:

```http
If-None-Match: "abc123"
```

Response:

```http
HTTP/1.1 304 Not Modified
```

Revalidation behaviour can complicate cache testing.

---

# Cache Poisoning and CDN Behaviour

CDNs often have provider-specific caching rules.

Potential considerations include:

```text
Query parameter handling
Cookie bypass rules
Cacheable status codes
Host handling
Forwarded headers
Origin configuration
Custom cache keys
Edge functions
```

Do not assume all CDNs behave identically.

---

# Burp Suite Workflow

A practical Burp workflow is:

```text
Proxy
  ↓
Browse Application
  ↓
HTTP History
  ↓
Identify Cached Responses
  ↓
Send to Repeater
  ↓
Add Cache Buster
  ↓
Establish MISS → HIT
  ↓
Test Candidate Unkeyed Input
  ↓
Insert Canary
  ↓
Request Same Cache Key Normally
  ↓
Check Persistence
  ↓
Assess Impact
```

---

# Burp Repeater

Repeater is particularly useful because cache testing requires precise control over:

```text
Headers
Query parameters
Cookies
Request order
```

Example baseline:

```http
GET /?cb=AM100 HTTP/1.1
Host: target.example
```

Then:

```http
GET /?cb=AM100 HTTP/1.1
Host: target.example
X-Forwarded-Host: am-cache.example
```

Then again:

```http
GET /?cb=AM100 HTTP/1.1
Host: target.example
```

Compare all three responses.

---

# Burp Comparer

Comparer can help identify subtle differences between:

```text
Baseline response
Modified response
Cached response
```

Compare:

```text
Headers
Body
URLs
Script sources
Redirects
Length
```

---

# Burp Decoder

Decoder can assist when cache-related values appear:

```text
URL encoded
Base64 encoded
HTML encoded
```

Understand how the application transforms the input before it reaches the response.

---

# Param Miner

A particularly useful Burp extension for web cache poisoning research is:

```text
Param Miner
```

Param Miner can help identify:

```text
Hidden parameters
Unkeyed headers
Unkeyed cookies
Cache behaviour
```

It is widely used when testing web cache poisoning.

---

# Installing Param Miner

In Burp Suite:

```text
Extensions
   ↓
BApp Store
   ↓
Search:
Param Miner
   ↓
Install
```

After installation, relevant functionality becomes available through Burp's extension interfaces and context menus.

---

# Param Miner Workflow

A practical workflow is:

```text
Interesting Request
      ↓
Send to Repeater
      ↓
Establish Cache Behaviour
      ↓
Param Miner
      ↓
Guess Headers
      ↓
Interesting Header Found
      ↓
Manual Repeater Validation
      ↓
Canary Reflection
      ↓
Cache Persistence
      ↓
Impact Assessment
```

---

# Guess Headers

Param Miner can assist with identifying headers that affect application behaviour.

Conceptually:

```text
Candidate Headers
      ↓
Application
      ↓
Response Difference
      ↓
Interesting Candidate
```

A detected header should always be manually verified.

---

# Param Miner Findings

Treat extension findings as:

```text
Leads
```

rather than:

```text
Confirmed vulnerabilities
```

You still need to establish:

```text
Input affects response
Input is unkeyed
Response is cached
Normal request receives poisoned response
Security impact exists
```

---

# Web Cache Poisoning Testing With curl

curl can help inspect basic cache behaviour.

Example:

```bash
curl -k -i \
  "https://target.example/?cb=AM200"
```

Repeat:

```bash
curl -k -i \
  "https://target.example/?cb=AM200"
```

Compare:

```text
Age
X-Cache
CF-Cache-Status
```

---

# Header Canary With curl

```bash
curl -k -i \
  -H "X-Forwarded-Host: am-cache.example" \
  "https://target.example/?cb=AM201"
```

Then:

```bash
curl -k -i \
  "https://target.example/?cb=AM201"
```

Search for the harmless canary.

---

# Response Comparison

Useful shell tools include:

```text
diff
grep
sha256sum
```

Example:

```bash
curl -sk \
  "https://target.example/?cb=AM300" \
  -o baseline.html
```

Then compare against a modified response.

---

# Automated Testing Considerations

Automation can help identify:

```text
Headers affecting responses
Cacheable endpoints
Cache status changes
Response differences
```

However, aggressive automated cache testing can accidentally affect shared cache entries.

Therefore:

```text
Use unique cache busters
Limit request volume
Prefer controlled endpoints
Verify manually
```

---

# Safe Testing Strategy

A strong authorised workflow is:

```text
1. Identify cache

2. Select low-risk endpoint

3. Create unique cache buster

4. Verify cache buster is keyed

5. Establish cache MISS/HIT behaviour

6. Introduce harmless canary

7. Determine whether canary changes response

8. Remove candidate input

9. Request identical cache-busted URL

10. Determine whether canary persists

11. Stop once cache poisoning primitive is demonstrated

12. Assess potential impact without affecting normal users
```

---

# Web Cache Poisoning Checklist

## Cache Discovery

```text
[ ] Check Age
[ ] Check X-Cache
[ ] Check CF-Cache-Status
[ ] Check Via
[ ] Check Cache-Control
[ ] Check ETag
[ ] Repeat request
[ ] Establish HIT/MISS behaviour
```

## Cache Safety

```text
[ ] Create unique cache buster
[ ] Verify cache buster is keyed
[ ] Avoid normal production cache keys
[ ] Use harmless markers
[ ] Limit testing volume
[ ] Stop after sufficient evidence
```

## Cache Key

```text
[ ] Host
[ ] Path
[ ] Query string
[ ] Query parameter order
[ ] Selected headers
[ ] Cookies
[ ] HTTP method
[ ] Scheme
[ ] Port
```

## Candidate Unkeyed Inputs

```text
[ ] X-Forwarded-Host
[ ] X-Forwarded-Proto
[ ] X-Forwarded-Port
[ ] Forwarded
[ ] X-Original-URL
[ ] X-Rewrite-URL
[ ] Origin
[ ] Accept-Language
[ ] User-Agent
[ ] Cookies
[ ] Custom headers
```

## Response Effects

```text
[ ] Absolute URLs
[ ] Script sources
[ ] Stylesheets
[ ] Canonical URLs
[ ] Redirects
[ ] HTML
[ ] API responses
[ ] Error messages
```

## Persistence

```text
[ ] Modified request sent
[ ] Response modified
[ ] Response cached
[ ] Candidate input removed
[ ] Same cache key requested
[ ] Modification remains
```

## Authentication

```text
[ ] Check authenticated responses
[ ] Check session cookies
[ ] Check Authorization
[ ] Check user-specific content
[ ] Check role-specific content
[ ] Check tenant-specific content
```

## Tools

```text
[ ] Burp Proxy
[ ] Burp Repeater
[ ] Burp Comparer
[ ] Param Miner
[ ] curl
```

## Impact

```text
[ ] XSS
[ ] Redirect manipulation
[ ] JavaScript modification
[ ] Content poisoning
[ ] Information disclosure
[ ] Denial of service
[ ] Authentication workflow impact
[ ] Cross-user exposure
```

---

# Cache Poisoning Decision Tree

```text
Is Response Cached?
       ↓
      YES
       ↓
Create Unique Cache Buster
       ↓
Is Cache Buster Keyed?
       ↓
      YES
       ↓
Identify Candidate Input
       ↓
Does Input Change Response?
       ↓
      YES
       ↓
Is Input Part of Cache Key?
       ↓
      NO
       ↓
Can Modified Response Be Cached?
       ↓
      YES
       ↓
Remove Candidate Input
       ↓
Request Same Cache Key
       ↓
Modification Still Present?
       ↓
      YES
       ↓
Cache Poisoning Confirmed
       ↓
Assess Security Impact
       ↓
Document
       ↓
Report
```

---

# High-Value Cache Poisoning Model

```text
UNKEYED INPUT
      +
RESPONSE INFLUENCE
      +
CACHEABLE RESPONSE
      +
SHARED CACHE
      =
WEB CACHE POISONING PRIMITIVE
```

Impact then depends on what the attacker controls.

For example:

```text
Cache Poisoning Primitive
        +
JavaScript URL Control
        =
Potential Script Delivery
```

or:

```text
Cache Poisoning Primitive
        +
Redirect Control
        =
Potential Redirect Poisoning
```

or:

```text
Cache Poisoning Primitive
        +
Error Generation
        =
Potential Cache-Based DoS
```

---

# Evidence Collection

For a confirmed finding, record:

```text
Affected URL
HTTP method
Cache provider where identifiable
Cache headers
Cache key observations
Cache buster used
Candidate unkeyed input
Canary value
Baseline request
Poisoning request
Verification request
Baseline response
Poisoned response
Cache HIT evidence
Age values
Persistence duration
Potential victim impact
```

Use a unique harmless marker in screenshots whenever possible.

---

# Example Finding: X-Forwarded-Host

```text
Finding:
Web Cache Poisoning via Unkeyed X-Forwarded-Host Header

Affected Endpoint:
/

Observed:
The application used the X-Forwarded-Host request header when generating an absolute resource URL.

The header was not represented in the cache key.

Using a unique cache-busting parameter and harmless controlled hostname, the modified response was cached. A subsequent request for the same cache-busted URL without the X-Forwarded-Host header received the cached response containing the controlled hostname.

Impact:
An attacker may be able to influence content stored in the shared cache and subsequently served to other users. The final impact depends on the context in which the attacker-controlled hostname is used.

Recommendation:
Do not use externally supplied forwarding headers unless they are generated by trusted proxy infrastructure. Include all request inputs that legitimately alter cached responses in the cache key, or prevent affected responses from being cached.
```

---

# Example Finding: Cache-Based Redirect

```text
Finding:
Unkeyed Host Information Allows Cached Redirect Manipulation

Observed:
Attacker-controlled host information influenced the Location response header of a cacheable redirect.

The modified redirect was subsequently returned for a request that did not contain the manipulated host information.

Impact:
Users requesting the affected cache entry may be redirected to an unintended destination.

Recommendation:
Generate redirects using trusted server-side configuration and ensure attacker-controlled request values cannot influence cached redirect destinations.
```

---

# Example Finding: User Data

```text
Finding:
Shared Cache Exposes Authenticated User Information

Observed:
An authenticated endpoint returned user-specific information that was stored by a shared cache.

A subsequent controlled request from a separate test session received information belonging to the first test account.

Impact:
Users may receive information associated with another authenticated user, resulting in a confidentiality breach.

Recommendation:
Do not store user-specific authenticated responses in shared caches unless the cache key safely distinguishes the relevant security context. Sensitive personalised responses should generally use appropriate private or no-store cache directives.
```

---

# Example Finding: Cache-Based Denial of Service

```text
Finding:
Attacker-Controlled Input Allows Error Response to Poison Shared Cache

Observed:
A controlled request variation caused the application to generate an error response that was stored under the same cache key used by normal requests.

Subsequent requests for the controlled cache-busted URL received the cached error response.

Impact:
If reproduced against shared production cache keys, an attacker may be able to temporarily make affected resources unavailable to users.

Recommendation:
Prevent attacker-controlled request metadata from influencing cacheable error responses and review which status codes are eligible for shared caching.
```

---

# Reporting Titles

Useful titles include:

```text
Web Cache Poisoning via Unkeyed X-Forwarded-Host Header

Cached Redirect Manipulation via Unkeyed Host Input

Unkeyed Request Header Allows Shared Cache Poisoning

Shared Cache Exposes Authenticated User Information

Web Cache Poisoning Enables Persistent Content Manipulation

Cache Key Misconfiguration Allows Cross-User Response Leakage

Cacheable Error Response Enables Cache-Based Denial of Service

Missing Cache Variation Causes Cross-Origin Response Confusion
```

Avoid vague titles such as:

```text
Caching Issue
```

Describe the actual primitive and impact.

---

# Severity

Severity depends on:

```text
What can be controlled?
How long is it cached?
How many users are affected?
Does poisoning require authentication?
Can executable content be introduced?
Can redirects be controlled?
Can sensitive information cross users?
Can important resources be made unavailable?
```

For example:

```text
Harmless text reflection
+
Cache persistence
```

may have limited impact.

While:

```text
Attacker-controlled script URL
+
Shared cache
+
High-traffic page
```

can have much greater impact.

---

# Remediation

The core principle is:

> Every request input that legitimately changes a cached response must either be represented correctly in the cache key or prevented from influencing the response.

---

# Remove Unnecessary Input Dependencies

If the application does not need:

```text
X-Forwarded-Host
```

do not use it to generate client-facing URLs.

Prefer trusted server-side configuration.

For example:

```text
APPLICATION_URL=https://target.example
```

rather than reconstructing the application origin from arbitrary request headers.

---

# Strip Untrusted Forwarding Headers

At the external proxy boundary:

```text
Internet
   ↓
Reverse Proxy
   ↓
Remove Client-Supplied Forwarding Headers
   ↓
Generate Trusted Headers
   ↓
Application
```

Headers such as:

```text
X-Forwarded-Host
X-Forwarded-Proto
Forwarded
```

should only be trusted when generated by authorised infrastructure.

---

# Correct Cache Keys

If a response legitimately varies based on:

```text
Language
Origin
Tenant
Device
```

ensure the cache distinguishes those variants appropriately.

Examples may involve:

```text
Cache key configuration
Vary
CDN cache policies
Application cache configuration
```

---

# Avoid Caching Sensitive Responses

Sensitive personalised responses may require:

```http
Cache-Control: private
```

or:

```http
Cache-Control: no-store
```

depending on application requirements.

---

# Separate Public and Private Caching

A useful architecture is:

```text
Public Static Content
       ↓
Shared CDN Cache

Authenticated Content
       ↓
Private / Non-Shared Handling
```

Avoid mixing both under ambiguous cache policies.

---

# Normalise Requests Consistently

Ensure:

```text
CDN
Proxy
Web server
Framework
Application
```

agree on how requests are parsed and normalised.

Differences in:

```text
Paths
Query parameters
Headers
Hosts
Ports
Encoding
```

can create cache discrepancies.

---

# Review Error Caching

Ensure that sensitive or attacker-influenced errors are not cached under legitimate cache keys.

Review caching of:

```text
400
403
404
500
Redirects
```

where appropriate.

---

# Test Cache Configuration

Caching behaviour should be included in security testing whenever changes are made to:

```text
CDN rules
Reverse proxy configuration
Cache keys
Routing
Header handling
Authentication
Tenant selection
CORS
```

---

# References

## PortSwigger Web Security Academy: Web Cache Poisoning

https://portswigger.net/web-security/web-cache-poisoning

PortSwigger provides detailed research and methodology covering cache keys, unkeyed inputs, header-based poisoning, cache implementation flaws and practical exploitation.

---

## PortSwigger Web Cache Poisoning Labs

https://portswigger.net/web-security/all-labs#web-cache-poisoning

Practical labs covering common and advanced web cache poisoning scenarios.

---

## PortSwigger: Practical Web Cache Poisoning

https://portswigger.net/research/practical-web-cache-poisoning

Research into practical cache poisoning techniques and the relationship between unkeyed inputs and cached responses.

---

## PortSwigger: Web Cache Entanglement

https://portswigger.net/research/web-cache-entanglement

Advanced research into cache key behaviour, parameter handling and cache implementation vulnerabilities.

---

## PortSwigger BApp Store: Param Miner

https://portswigger.net/bappstore/17d2949a985c4cc1a490683513d6d0b9

Param Miner can assist with discovering hidden parameters, unkeyed headers and other inputs relevant to web cache poisoning.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

Provides broader methodology for web application security testing and HTTP infrastructure analysis.

---

## MDN: Cache-Control

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control

Reference for HTTP cache directives.

---

## MDN: Vary

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Vary

Reference for controlling how request headers influence cached response variants.

---

# Final Web Cache Poisoning Testing Model

```text
                         REQUEST
                            ↓
                     CACHE LOOKUP
                            ↓
                       CACHE KEY
                            ↓
       ┌────────────────────┼────────────────────┐
       ↓                    ↓                    ↓
      HOST                 PATH                QUERY
       ↓                    ↓                    ↓
       └────────────────────┼────────────────────┘
                            ↓
                  WHAT IS NOT KEYED?
                            ↓
       ┌────────────────────┼────────────────────┐
       ↓                    ↓                    ↓
    HEADERS              COOKIES              BODY
       ↓                    ↓                    ↓
       └────────────────────┼────────────────────┘
                            ↓
              DOES INPUT CHANGE RESPONSE?
                            ↓
                           YES
                            ↓
                 IS RESPONSE CACHEABLE?
                            ↓
                           YES
                            ↓
                    UNIQUE CACHE BUSTER
                            ↓
                    POISON TEST ENTRY
                            ↓
                 REMOVE ATTACKER INPUT
                            ↓
                 REQUEST SAME CACHE KEY
                            ↓
               MODIFICATION STILL PRESENT?
                            ↓
                           YES
                            ↓
               CACHE POISONING CONFIRMED
                            ↓
       ┌────────────────────┼────────────────────┐
       ↓                    ↓                    ↓
      XSS                REDIRECT              DoS
       ↓                    ↓                    ↓
       └────────────────────┼────────────────────┘
                            ↓
                INFORMATION DISCLOSURE?
                            ↓
                       ASSESS IMPACT
                            ↓
                    DOCUMENT SAFELY
                            ↓
                          REPORT
```

The key principle is:

> Do not begin web cache poisoning testing by trying to inject a dangerous payload. First understand the cache key, establish a safe keyed cache buster, identify inputs that affect the response without affecting the cache key, and prove persistence using a harmless unique canary. Once the cache poisoning primitive is established, assess what security impact that primitive could realistically produce.
