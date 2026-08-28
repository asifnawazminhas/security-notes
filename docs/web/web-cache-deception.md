# Web Cache Deception

Web cache deception is a vulnerability where an attacker tricks a shared web cache into storing a sensitive, dynamically generated response that should never have been cached.

The attacker then retrieves the cached response and gains access to information belonging to another user.

The core attack pattern is:

```text
Victim
  ↓
Attacker-Controlled URL
  ↓
Application Treats Request as Dynamic
  ↓
Sensitive User-Specific Response Generated
  ↓
Cache Treats Request as Static / Cacheable
  ↓
Response Stored
  ↓
Attacker Requests Same URL
  ↓
Cached Victim Response Returned
```

Potentially exposed information includes:

```text
Account details
Email addresses
Personal information
API responses
CSRF tokens
Session-related data
Order information
Billing information
Private messages
Authentication metadata
Internal identifiers
Application secrets exposed to the user
```

Web cache deception usually exists because:

```text
Origin Server
```

and:

```text
Cache / CDN
```

interpret the same request differently.

!!! warning "Authorised Security Testing"
    Web cache deception testing can cause sensitive authenticated responses to be stored in shared infrastructure. Use controlled test accounts and unique cache-busting paths. Never intentionally cache unrelated users' information. Avoid testing sensitive production endpoints without understanding the caching behaviour and assessment scope.

---

# What Is a Web Cache?

Web caches improve performance by storing responses so they can be reused.

Common caching layers include:

```text
Browser Cache
CDN
Reverse Proxy
Edge Cache
Application Cache
Load Balancer Cache
```

Architecture:

```text
Client
  ↓
CDN / Cache
  ↓
Reverse Proxy
  ↓
Application
```

Without caching:

```text
Request
  ↓
Application
  ↓
Generate Response
  ↓
Return Response
```

With caching:

```text
Request
  ↓
Cache
  ↓
Cached Object Exists?
  ↓
 YES ───────────────→ Return Cached Response
  ↓
 NO
  ↓
Application
  ↓
Generate Response
  ↓
Store Response
  ↓
Return Response
```

---

# Shared vs Private Caches

Understanding the distinction between:

```text
Private Cache
```

and:

```text
Shared Cache
```

is essential.

A browser cache is normally private to a user.

A CDN or reverse proxy cache may be shared between:

```text
Thousands
```

or:

```text
Millions
```

of users.

The dangerous situation is:

```text
Authenticated Response
        ↓
Shared Cache
```

---

# Dynamic vs Static Content

Dynamic content commonly includes:

```text
/account
/profile
/dashboard
/orders
/messages
/settings
/api/user
```

Static content commonly includes:

```text
/style.css
/app.js
/logo.png
/image.jpg
/fonts.woff2
```

Caches frequently treat requests ending in static-looking extensions differently.

Examples:

```text
.css
.js
.jpg
.jpeg
.png
.gif
.svg
.ico
.woff
.woff2
```

This becomes important when the cache and origin disagree about what resource is being requested.

---

# Web Cache Deception Core Concept

Suppose:

```text
https://target.example/account
```

returns:

```text
Alice's private account information
```

and is correctly not cached.

But the application also accepts:

```text
https://target.example/account/test.css
```

and internally interprets it as:

```text
/account
```

while the cache sees:

```text
/test.css
```

and assumes:

```text
Static CSS File
```

The result may be:

```text
Victim requests:

/account/test.css
        ↓
Origin sees:
/account
        ↓
Returns victim's account
        ↓
Cache sees:
.css
        ↓
Stores response
        ↓
Attacker requests:
/account/test.css
        ↓
Victim's cached account returned
```

This is web cache deception.

---

# The Fundamental Discrepancy

Web cache deception commonly requires a discrepancy between:

```text
Cache Interpretation
```

and:

```text
Origin Interpretation
```

For example:

```text
Request:
/account/test.css

Cache:
"Static .css resource"

Origin:
"/account endpoint with extra path information"
```

That disagreement creates the vulnerability.

---

# Cache Rules

Caches may decide whether to cache based on:

```text
File extension
Path
Directory
HTTP method
Status code
Response headers
Query parameters
Cookies
Authentication headers
Configured route
```

Examples of potentially cacheable patterns:

```text
*.css
*.js
*.jpg
*.png
/static/*
/assets/*
/images/*
```

Never assume a specific rule exists.

Determine actual behaviour.

---

# Origin Routing

Applications may interpret URLs using:

```text
Framework routing
Path parameters
Path info
Rewrites
Reverse proxy rules
URL normalization
```

For example:

```text
/account
/account/
/account/test
/account/test.css
```

may all route to the same application handler.

---

# Example Routing Behaviour

Suppose:

```text
GET /profile
```

returns:

```text
Current user's profile
```

Try a harmless unique path:

```text
GET /profile/am-test-001
```

If the same profile is returned, the application may tolerate additional path segments.

Then test:

```text
GET /profile/am-test-001.css
```

using only your controlled account.

If the same sensitive response appears, investigate caching behaviour.

---

# Web Cache Deception vs Web Cache Poisoning

These vulnerabilities are related but fundamentally different.

## Web Cache Poisoning

The attacker causes:

```text
Attacker-Controlled Response
```

to be cached and served to:

```text
Victims
```

Flow:

```text
Attacker
  ↓
Manipulates Response
  ↓
Cache Stores It
  ↓
Victim Receives Poisoned Response
```

---

## Web Cache Deception

The attacker causes:

```text
Victim's Sensitive Response
```

to be cached and later retrieved by:

```text
Attacker
```

Flow:

```text
Victim
  ↓
Sensitive Response
  ↓
Cache Stores It
  ↓
Attacker Retrieves It
```

---

# Quick Comparison

| Vulnerability | Cached Content | Main Victim |
|---|---|---|
| Web Cache Poisoning | Attacker-influenced response | Other users |
| Web Cache Deception | Victim-specific response | User whose response was cached |

Remember:

```text
Poisoning:
Attacker → Cache → Victim

Deception:
Victim → Cache → Attacker
```

Refer to:

```text
docs/web/web-cache-poisoning.md
```

---

# Testing Methodology

A structured methodology is:

```text
Identify Sensitive Dynamic Endpoint
        ↓
Confirm Authentication Dependency
        ↓
Understand Origin Path Handling
        ↓
Add Unique Path Segment
        ↓
Compare Response
        ↓
Add Static-Looking Extension
        ↓
Inspect Cache Behaviour
        ↓
Repeat Without Authentication
        ↓
Cached Response Returned?
        ↓
Confirm With Controlled Account
        ↓
Determine Impact
        ↓
Report
```

---

# Step 1: Identify Sensitive Endpoints

Prioritise authenticated endpoints containing:

```text
Personal information
Account information
Orders
Messages
Documents
Tokens
Billing information
Administrative data
```

Examples:

```text
/account
/profile
/dashboard
/settings
/orders
/messages
/api/me
/api/user
```

---

# Step 2: Establish the Baseline

Using a controlled authenticated account:

```http
GET /account HTTP/1.1
Host: target.example
Cookie: session=CONTROLLED_SESSION
```

Record:

```text
Status
Response body
Response length
Cache headers
Age
Cookies
Cache-Control
Vary
ETag
```

---

# Step 3: Test Additional Path Segments

Try:

```text
/account/am-wcd-001
```

If the response becomes:

```text
404 Not Found
```

the route may not tolerate extra path information.

If it still returns:

```text
Account Page
```

then investigate further.

---

# Step 4: Test Static Extensions

Using a unique controlled path:

```text
/account/am-wcd-001.css
```

Other extensions may include:

```text
.js
.jpg
.png
.svg
.ico
```

Start with one or two common extensions.

Do not blindly generate large extension lists against production infrastructure.

---

# Step 5: Compare the Response

Compare:

```text
/account
```

with:

```text
/account/am-wcd-001.css
```

Ask:

```text
Same status?
Same account information?
Same page?
Same user?
Same sensitive data?
```

If the origin returns the same authenticated content, a prerequisite may exist.

---

# Step 6: Determine Whether It Is Cached

Request the modified URL repeatedly.

For example:

```text
/account/am-wcd-001.css
```

Observe cache-related headers.

Common examples include:

```text
Age
X-Cache
X-Cache-Hits
CF-Cache-Status
Via
X-Served-By
Cache-Control
Vary
```

Possible responses:

```text
X-Cache: MISS
```

followed by:

```text
X-Cache: HIT
```

This strongly indicates shared caching.

---

# Cache Header Examples

Example:

```http
HTTP/1.1 200 OK
Cache-Control: public, max-age=300
Age: 27
X-Cache: HIT
```

Another CDN may return:

```http
CF-Cache-Status: HIT
```

Another might use:

```text
X-Cache: HIT
X-Cache-Hits: 1
```

Header names vary between providers.

---

# Age Header

The `Age` header indicates approximately how long a response has been stored in a cache.

Example:

```http
Age: 42
```

If repeated requests produce:

```text
Age: 1
Age: 5
Age: 9
```

this may indicate the same cached object is being served.

Do not rely on `Age` alone.

---

# Cache HIT / MISS

A useful sequence is:

```text
First request:
MISS

Second request:
HIT

Third request:
HIT
```

This provides much stronger evidence of caching than a single response.

---

# Step 7: Test Without Authentication

After caching a controlled account response, request the exact same unique URL without the session cookie.

For example:

```http
GET /account/am-wcd-001.css HTTP/1.1
Host: target.example
```

If the response contains:

```text
Controlled Account Data
```

then a shared-cache disclosure may exist.

This is strong evidence of web cache deception.

---

# Controlled Account Workflow

Always prefer:

```text
Your Test Account
```

rather than:

```text
Real Victim
```

Workflow:

```text
Authenticated Controlled Account
        ↓
Request Unique Cache URL
        ↓
Response Cached
        ↓
Remove Authentication
        ↓
Request Same URL
        ↓
Controlled Account Data Returned?
```

This demonstrates the issue without exposing unrelated users.

---

# Unique Cache Keys

Use a unique identifier:

```text
am-wcd-847291
```

Example:

```text
/account/am-wcd-847291.css
```

This reduces the chance of interacting with an existing cache object.

---

# Why Unique Paths Matter

Testing:

```text
/account/test.css
```

repeatedly may collide with:

```text
Previous tests
Other testers
Existing cache entries
```

Instead use:

```text
/account/am-wcd-20260828-847291.css
```

or another unique random value.

---

# Cache Keys

The cache must determine which requests correspond to the same cached object.

A simplified cache key might be:

```text
Host
 +
Path
 +
Query String
```

Conceptually:

```text
https://target.example/account/test.css
```

may become:

```text
target.example|/account/test.css
```

But real cache keys vary considerably.

---

# Cache Key Components

Potential components include:

```text
Scheme
Host
Path
Query parameters
HTTP method
Selected headers
Cookies
```

Potentially excluded inputs include:

```text
Some headers
Some cookies
Some query parameters
```

The exact configuration matters.

---

# Cookies and Caching

Authenticated pages normally use:

```text
Cookie: session=...
```

A safe cache should not accidentally serve one user's personalised response to another user.

However, a cache may:

```text
Ignore Cookie
```

for paths classified as static.

For example:

```text
/account/am-test.css
```

might be considered static despite the origin returning personalised content.

---

# `Vary`

The `Vary` header tells caches that a response varies based on specific request headers.

Example:

```http
Vary: Accept-Encoding
```

Another example:

```http
Vary: Origin
```

However:

```text
Vary
```

is not a universal solution for sensitive authenticated content.

Highly sensitive personalised responses often should not be stored in shared caches at all.

---

# Cache-Control

Important directives include:

```text
private
public
no-store
no-cache
max-age
s-maxage
```

---

# `private`

Example:

```http
Cache-Control: private
```

indicates that the response is intended for private caches rather than shared caches.

---

# `no-store`

Example:

```http
Cache-Control: no-store
```

instructs caches not to store the response.

This is commonly appropriate for highly sensitive responses.

---

# `public`

Example:

```http
Cache-Control: public
```

explicitly permits shared caching.

This is dangerous for user-specific responses unless the cache key safely separates every relevant user context, which is usually unnecessary complexity for sensitive pages.

---

# `s-maxage`

Example:

```http
Cache-Control: s-maxage=300
```

controls freshness specifically for shared caches.

A response may therefore behave differently in:

```text
Browser Cache
```

versus:

```text
CDN
```

---

# Browser Cache vs Shared Cache

Do not confuse:

```text
Browser caching
```

with:

```text
CDN caching
```

If your browser shows a cached response, this does not prove another user can retrieve it.

Strong evidence requires:

```text
Shared cache behaviour
```

and preferably:

```text
Unauthenticated or second controlled session retrieval
```

---

# Static Extension Rules

Caches frequently classify resources by extension.

Examples:

```text
.css
.js
.png
.jpg
.jpeg
.gif
.svg
.ico
.woff
.woff2
```

A rule might conceptually say:

```text
IF extension == .css
THEN cache
```

without considering that:

```text
/account/test.css
```

is actually handled dynamically by the application.

---

# Static Directory Rules

Caches may also cache specific directories.

Examples:

```text
/static/
/assets/
/images/
/scripts/
/css/
```

A discrepancy may occur if the origin normalises or rewrites the path differently.

Conceptually:

```text
Cache sees:
/static/../account

Origin sees:
/account
```

Whether this is possible depends heavily on:

```text
Normalization
Encoding
Reverse proxies
Framework routing
```

---

# Path Mapping Discrepancies

Important differences may involve:

```text
Path delimiters
Static extensions
Encoded characters
Path traversal normalization
Semicolon handling
Matrix parameters
URL decoding
Case normalization
```

The general model is:

```text
Cache Parses URL
       ↓
Interpretation A

Origin Parses URL
       ↓
Interpretation B
```

If:

```text
A != B
```

investigate whether the difference creates a security boundary.

---

# Path Delimiters

Different systems may interpret delimiters differently.

Characters of interest can include:

```text
;
?
#
/
.
```

as well as encoded forms.

For example:

```text
/account;test.css
```

might be interpreted differently by:

```text
CDN
Reverse Proxy
Application Framework
```

Do not assume this behaviour exists.

Test incrementally.

---

# Semicolon Handling

Some frameworks treat:

```text
;
```

as a path parameter delimiter.

Conceptually:

```text
/account;test.css
```

might be routed by the origin as:

```text
/account
```

while another component interprets:

```text
.css
```

as part of the path.

This parser discrepancy can become relevant to cache deception.

---

# Path Parameters

Some application servers support:

```text
Matrix Parameters
```

or similar syntax.

Example:

```text
/account;foo=bar
```

The application may ignore:

```text
;foo=bar
```

while the cache considers it part of the resource path.

---

# Encoded Delimiters

Different layers may decode URLs at different stages.

For example:

```text
%2F
%3B
%3F
%23
```

may be handled differently by:

```text
CDN
Reverse Proxy
Web Server
Framework
```

Testing should focus on identifying real parser differences rather than blindly trying encoding combinations.

---

# URL Decoding

Architecture:

```text
Raw Request
    ↓
CDN Decoding
    ↓
Proxy Decoding
    ↓
Framework Decoding
```

If one layer decodes once and another layer decodes again:

```text
Different interpretations
```

can occur.

This is relevant not only to cache deception but also:

```text
Path Traversal
Access Control
Routing Bypass
Request Smuggling
```

---

# Path Normalization

Normalization can include:

```text
Removing ../
Collapsing //
Decoding characters
Removing dot segments
Resolving semicolons
Canonicalising paths
```

If the cache and origin normalize differently:

```text
Cache Key
```

may refer to a different conceptual resource than the origin response.

---

# Normalization Example

Conceptually:

```text
Request:
/static/../account
```

Cache may treat:

```text
/static/../account
```

as a static route.

Origin may normalize:

```text
/static/../account
```

to:

```text
/account
```

and return sensitive content.

Whether this occurs depends entirely on the infrastructure.

---

# Cache Deception Using Static Directories

Suppose a CDN caches:

```text
/static/*
```

and the application accepts a path that normalizes to:

```text
/account
```

A discrepancy could result in:

```text
Cache:
Static resource

Origin:
Sensitive account endpoint
```

This is another form of web cache deception.

---

# Cache Deception Through Path Confusion

The central question is:

> Can I create a URL that the cache believes is cacheable while the application believes it references a sensitive dynamic resource?

That is the core of path-based cache deception testing.

---

# Origin Cache-Control Behaviour

Check whether the application returns:

```http
Cache-Control: no-store
```

for the original endpoint.

Then compare the modified path.

Example:

```text
/account
```

versus:

```text
/account/test.css
```

A reverse proxy or CDN may override origin caching rules depending on configuration.

---

# Authentication Responses

Sensitive authenticated endpoints should generally not become publicly retrievable from shared caches.

Test:

```text
Authenticated request
```

then:

```text
Unauthenticated request
```

using the exact same unique cache URL.

---

# Second Controlled Account

An even stronger test uses:

```text
Account A
Account B
```

Workflow:

```text
Account A
 ↓
Request unique URL
 ↓
Cache Account A response
 ↓
Account B
 ↓
Request same URL
 ↓
Account A data returned?
```

This demonstrates:

```text
Cross-user cache exposure
```

without involving real users.

---

# Session-Specific Data

Look for:

```text
Username
Email
Account ID
CSRF token
Orders
Messages
Address
Subscription
Billing data
```

Use a unique controlled marker in the account profile where possible.

For example:

```text
AM-WCD-CANARY-8472
```

If this appears in another controlled session:

```text
Cross-user disclosure confirmed
```

---

# CSRF Tokens

Some dynamic pages contain:

```text
CSRF tokens
```

If the page is cached, the token may also be exposed.

Whether this creates additional impact depends on:

```text
Token binding
Session binding
Token validation
Action being protected
```

Do not automatically claim CSRF bypass merely because a token is disclosed.

Refer to:

```text
docs/web/csrf.md
```

---

# API Endpoints

Web cache deception is not limited to HTML.

Sensitive JSON endpoints can also be affected.

Example:

```text
/api/me
```

Modified:

```text
/api/me/test.js
```

If the application still returns:

```json
{
  "email": "controlled@example.com",
  "accountId": "12345"
}
```

and a shared cache stores the response, sensitive API data may be exposed.

---

# API Testing Model

```text
/api/me
   ↓
Sensitive JSON
   ↓
/api/me/am-test.js
   ↓
Same JSON?
   ↓
Cached?
   ↓
Unauthenticated retrieval?
```

---

# Content-Type

Do not assume the response must actually be:

```text
text/css
```

for the cache to store it.

Some cache rules rely primarily on:

```text
URL
```

rather than:

```text
Content-Type
```

A response such as:

```http
Content-Type: text/html
```

may still be cached if the CDN configuration treats the path as static.

---

# Status Codes

Caches may cache:

```text
200
301
302
404
```

and other responses depending on configuration.

Do not assume only:

```text
200 OK
```

is cacheable.

---

# Redirects

Suppose an authenticated endpoint redirects:

```text
/account
 ↓
/users/alice
```

If a manipulated path causes the redirect itself to be cached, this may expose:

```text
Usernames
Internal identifiers
Sensitive paths
```

or create other cache-related behaviour.

---

# Cache Deception and Open Redirect

Open redirects can sometimes interact with caching.

For example:

```text
User-specific endpoint
       ↓
Redirect
       ↓
Cache
```

Investigate whether:

```text
Redirect target
```

or:

```text
redirect response
```

becomes incorrectly cached.

Refer to:

```text
docs/web/open-redirect.md
```

---

# Cache Deception and Authentication

A common assumption is:

```text
Authentication required
      ↓
Response is safe
```

But if:

```text
Authenticated Response
      ↓
Shared Cache
```

authentication may be bypassed indirectly because subsequent requests are served by the cache before reaching the application.

---

# Cache Before Authentication

Architecture:

```text
Request
 ↓
CDN
 ↓
Cache HIT?
 ↓
YES
 ↓
Return Response
```

The request may never reach:

```text
Authentication Middleware
```

on the origin.

This is why shared caching of private responses is dangerous.

---

# Cache Deception and Authorisation

Suppose:

```text
/admin/profile
```

requires administrative privileges.

If an administrator is tricked into requesting a cacheable variant:

```text
/admin/profile/am-test.css
```

and that response is stored publicly, the cache may effectively bypass:

```text
Origin Authorisation
```

for subsequent requests.

Refer to:

```text
docs/web/authorisation.md
```

---

# High-Privilege Victims

Impact increases substantially when the cached response belongs to:

```text
Administrator
Support staff
Finance staff
Privileged employee
Tenant administrator
```

However, during testing:

```text
Do not target real privileged users.
```

Use controlled privileged test accounts where available.

---

# Victim Interaction

Many web cache deception attacks require:

```text
Victim requests attacker-crafted URL
```

This may happen through:

```text
Link
Image
Redirect
Email
Embedded resource
Social engineering
```

The exact user interaction requirement should be reflected in severity.

---

# Safe Victim Simulation

During testing:

```text
Controlled Account
       ↓
Act as Victim
       ↓
Request Crafted URL
```

Then:

```text
Unauthenticated Session
       ↓
Act as Attacker
       ↓
Retrieve Cached Response
```

This provides complete proof without involving third parties.

---

# Cache Busters

Cache busters help isolate testing.

Example:

```text
/account/am-wcd-847291.css
```

or where appropriate:

```text
/account/test.css?cb=847291
```

However, query strings may be:

```text
Included in cache key
Ignored
Normalized
Removed
```

depending on cache configuration.

A unique path is often easier to reason about.

---

# Query String Behaviour

Determine whether:

```text
?a=1
```

and:

```text
?a=2
```

produce:

```text
Different cache objects
```

or:

```text
Same cache object
```

Do not assume.

---

# Cache Key Discovery

A useful process:

```text
Baseline URL
 ↓
Change One Component
 ↓
Observe HIT / MISS
 ↓
Repeat
 ↓
Infer Cache Key
```

Components to investigate include:

```text
Path
Query
Host
Cookies
Headers
```

---

# Detecting Shared Cache Behaviour

Useful indicators:

```text
Age increases
MISS → HIT
Stable cached response
Different session receives same content
Origin changes not immediately visible
CDN-specific headers
```

The strongest proof remains:

```text
Controlled Account A Response
          ↓
Returned to Account B / Unauthenticated Session
```

---

# Burp Suite

Burp Suite is particularly useful for cache deception testing.

Useful components:

```text
Proxy
Repeater
Comparer
Logger
Intruder
```

---

# Burp Repeater Workflow

Start with:

```text
Authenticated Request
```

Example:

```http
GET /account HTTP/1.1
Host: target.example
Cookie: session=CONTROLLED_SESSION
```

Send to Repeater.

Then test:

```text
/account/am-wcd-001
```

and:

```text
/account/am-wcd-001.css
```

Compare responses.

---

# Repeater Tabs

A useful layout is:

```text
Tab 1:
Original authenticated request

Tab 2:
Modified authenticated request

Tab 3:
Modified unauthenticated request

Tab 4:
Second controlled account
```

This makes comparison easier.

---

# Burp Comparer

Compare:

```text
/account
```

with:

```text
/account/am-test.css
```

Check whether:

```text
Sensitive content
```

is substantially identical.

Then compare:

```text
Authenticated modified response
```

with:

```text
Unauthenticated cached response
```

---

# Burp Logger

Logger can help identify:

```text
Repeated requests
Cache headers
Redirect chains
CDN behaviour
Unexpected background requests
```

---

# Burp Intruder

Intruder can help test a small set of path suffixes.

For example:

```text
.css
.js
.jpg
.png
.svg
.ico
```

Do not use large extension lists unnecessarily.

The objective is to understand:

```text
Cache rules
```

rather than brute-force every possible extension.

---

# Param Miner

Burp Suite's:

```text
Param Miner
```

is primarily known for discovering:

```text
Hidden parameters
Unkeyed headers
Cache-related behaviour
```

and is particularly useful for web cache poisoning research.

It can still be useful while analysing cache architecture, but web cache deception usually requires careful manual testing of:

```text
Path interpretation
Cache rules
Origin routing
```

rather than only hidden parameter discovery.

PortSwigger BApp Store:

```text
https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943
```

Always manually verify automated findings.

---

# Burp Cache Deception Scanner

When performing web cache research, check the current:

```text
BApp Store
```

for extensions related to:

```text
Web Cache Deception
Web Cache Poisoning
Cache Analysis
```

Extensions can help identify candidate behaviour, but manual confirmation is essential because cache rules are highly application-specific.

---

# curl Testing

A baseline request:

```bash
curl -i \
  -b "session=CONTROLLED_SESSION" \
  https://target.example/account
```

Modified path:

```bash
curl -i \
  -b "session=CONTROLLED_SESSION" \
  https://target.example/account/am-wcd-847291.css
```

Repeat:

```bash
curl -i \
  -b "session=CONTROLLED_SESSION" \
  https://target.example/account/am-wcd-847291.css
```

Then remove authentication:

```bash
curl -i \
  https://target.example/account/am-wcd-847291.css
```

Look for:

```text
Controlled account data
Age
X-Cache
CF-Cache-Status
Via
Cache-Control
```

---

# Header Inspection

Useful command:

```bash
curl -s -D - -o /dev/null \
  https://target.example/account/am-wcd-847291.css
```

This displays response headers without printing the response body.

---

# Browser Testing

Browser testing is useful when:

```text
Authentication state
Redirects
JavaScript
Cookies
Frontend routing
```

affect the request.

Use:

```text
Browser
 ↓
Burp
 ↓
Application
```

rather than relying only on curl.

---

# Browser DevTools

Inspect:

```text
Network
```

for:

```text
Status
Cache headers
Request URL
Redirects
Cookies
Response
```

Be careful with browser-local caching.

Disable browser cache during analysis where appropriate so that:

```text
Browser Cache
```

does not get confused with:

```text
Shared Cache
```

---

# CDN Identification

Response headers may reveal:

```text
Cloudflare
Fastly
Akamai
CloudFront
Varnish
Cloud CDN
Azure Front Door
```

This can help explain caching behaviour.

However:

```text
CDN detected
```

does not mean:

```text
Web Cache Deception exists
```

---

# Reverse Proxy Caches

Caching may also occur at:

```text
Nginx
Varnish
Apache
Application Gateway
Reverse Proxy
```

Therefore lack of an obvious CDN does not eliminate the vulnerability.

---

# Framework Routing

Different frameworks handle additional path information differently.

During testing determine whether:

```text
/profile/test
```

is:

```text
404
```

or:

```text
Same as /profile
```

This is more important than guessing the framework's behaviour.

---

# Static File Middleware

Applications may combine:

```text
Static File Handler
       +
Dynamic Router
```

Ordering can create unexpected behaviour.

For example:

```text
CDN
 ↓
Static Rule
 ↓
Reverse Proxy
 ↓
Dynamic Framework
```

Each component may interpret the path differently.

---

# Encoded Path Testing

Only after basic path testing, consider whether encoded delimiters produce different behaviour.

Examples:

```text
%2F
%3B
%2E
```

Use controlled paths and one mutation at a time.

Do not indiscriminately fuzz complex encoding combinations against production systems.

---

# Cache Deception and Path Traversal

Both may involve:

```text
Path normalization
```

but the vulnerabilities are different.

Path traversal:

```text
Attacker manipulates path
 ↓
Access unintended filesystem resource
```

Cache deception:

```text
Attacker manipulates path
 ↓
Cache and origin disagree
 ↓
Sensitive response cached
```

Refer to:

```text
docs/web/path-traversal.md
```

---

# Cache Deception and Request Smuggling

HTTP request smuggling can sometimes create cache-related effects.

However:

```text
Request Smuggling
```

and:

```text
Web Cache Deception
```

are separate vulnerability classes.

Request smuggling concerns disagreement about:

```text
HTTP request boundaries
```

whereas cache deception typically concerns disagreement about:

```text
URL interpretation / cacheability
```

Refer to:

```text
docs/web/http-request-smuggling.md
```

---

# Cache Deception and Information Disclosure

The ultimate impact of web cache deception is often:

```text
Information Disclosure
```

But the root cause is:

```text
Sensitive response stored in shared cache
```

A report should normally describe:

```text
Web Cache Deception
```

and explain the resulting data disclosure.

Refer to:

```text
docs/web/information-disclosure.md
```

---

# Cache Deception and Session Management

If a cached page contains:

```text
Session-related information
CSRF tokens
Account state
Authentication metadata
```

review whether those values can be reused.

Do not assume that disclosure automatically results in:

```text
Session Hijacking
```

Validate independently.

Refer to:

```text
docs/web/session-management.md
```

---

# Cache Deception and Business Logic

Some cached information may not appear technically sensitive but may have significant business value.

Examples:

```text
Private pricing
Unreleased products
Internal account status
Order history
Private reports
Subscription information
Customer-specific configuration
```

Assess impact based on:

```text
Application context
```

rather than data type alone.

---

# Path Testing Matrix

| Request | Purpose |
|---|---|
| `/account` | Baseline |
| `/account/AMTEST` | Extra path handling |
| `/account/AMTEST.css` | Static extension |
| `/account/AMTEST.js` | Static extension |
| `/account/AMTEST.jpg` | Static extension |
| `/account;AMTEST.css` | Delimiter behaviour |
| `/account/AMTEST.css?cb=123` | Query/cache behaviour |

Do not send every variation automatically.

Proceed based on observed behaviour.

---

# Cache Testing Matrix

| Request | Session | Expected Purpose |
|---|---|---|
| Original endpoint | Account A | Baseline |
| Unique static path | Account A | Populate candidate cache |
| Same static path | Account A | Detect HIT |
| Same static path | None | Test public exposure |
| Same static path | Account B | Test cross-user exposure |

---

# Cache Indicators Matrix

| Header | Possible Meaning |
|---|---|
| `Age` | Time stored in cache |
| `X-Cache: HIT` | Cache served response |
| `X-Cache: MISS` | Cache did not have object |
| `CF-Cache-Status` | Cloudflare cache status |
| `X-Cache-Hits` | Number of cache hits |
| `Via` | Intermediate proxy/cache |
| `Cache-Control` | Caching policy |
| `Vary` | Request headers affecting representation |

Headers are indicators.

Actual cross-session behaviour is stronger evidence.

---

# Vulnerability Confirmation

A strong confirmation sequence is:

```text
1. Account A requests unique modified URL

2. Sensitive Account A response is returned

3. Response indicates MISS

4. Repeat request indicates HIT

5. Remove Account A session

6. Request exact same URL

7. Account A data is still returned
```

This demonstrates:

```text
Sensitive Response
      ↓
Shared Cache
      ↓
Unauthorised Retrieval
```

---

# False Positive: Browser Cache

If:

```text
Same browser
```

returns cached content but:

```text
Separate client
```

does not, the behaviour may simply involve:

```text
Private browser caching
```

Do not report shared-cache deception without validating the shared aspect.

---

# False Positive: Public Data

If the cached response contains only:

```text
Public content
```

there may be no meaningful confidentiality impact.

---

# False Positive: Dynamic Reprocessing

Suppose:

```text
/account/test.css
```

returns Account A's data while logged in.

Then when unauthenticated it returns:

```text
Login page
```

This means the application may simply be dynamically processing both requests.

If there is no shared cached response:

```text
Web Cache Deception is not confirmed.
```

---

# False Positive: Cache Header Alone

A response containing:

```text
X-Cache: HIT
```

does not automatically prove a vulnerability.

Static resources are supposed to be cached.

The important condition is:

```text
Sensitive user-specific response
      ↓
Shared cache
      ↓
Unauthorised user
```

---

# Impact Analysis

Consider:

```text
What data is cached?
How long?
Who can retrieve it?
Is victim interaction required?
Does the attacker need to know the exact URL?
Can privileged users be affected?
Are tokens exposed?
Can cached data enable further attacks?
```

---

# Cache Lifetime

A cache TTL may be:

```text
30 seconds
5 minutes
1 hour
24 hours
```

Longer TTLs may increase:

```text
Exposure window
```

but even short TTLs can be exploitable.

---

# Predictable vs Unique URLs

If the attacker must know:

```text
Exact random path
```

that they themselves supplied to the victim, this is often practical.

For example:

```text
/account/ATTACKER-CONTROLLED.css
```

The attacker already knows the URL because they created it.

---

# Victim Interaction Requirements

Document whether exploitation requires:

```text
Victim clicking a link
Victim loading a page
Victim being authenticated
Specific user role
Specific timing
```

These conditions affect severity.

---

# High-Impact Data

Examples include:

```text
API tokens
Password reset tokens
Private messages
Financial information
Personal information
Authentication secrets
Administrative data
Confidential documents
```

---

# Evidence Collection

For a confirmed finding record:

```text
Original endpoint
Crafted endpoint
Cache-busting identifier
Account used
Authentication state
First response
Second response
Cache headers
Unauthenticated response
Cross-account response
Sensitive marker
Cache lifetime
CDN / cache indicators
Reproduction steps
```

---

# Recommended Evidence Sequence

Capture:

```text
1. Authenticated baseline

2. Authenticated crafted URL
   X-Cache: MISS

3. Authenticated repeat
   X-Cache: HIT

4. Unauthenticated crafted URL
   X-Cache: HIT
   Controlled account data visible
```

This creates a clear narrative for the report.

---

# Example Finding: Account Information Disclosure

```text
Finding:
Web Cache Deception Allows Unauthenticated Access to Authenticated Account Information

Affected Endpoint:
GET /account

Observed:
The authenticated account endpoint returned the same user-specific response when an additional static-looking path segment was appended to the URL.

A unique controlled URL ending in .css was requested while authenticated to a test account.

The response was stored by the shared caching layer.

When the exact same URL was subsequently requested without authentication, the cached response containing the controlled account's information was returned.

Impact:
An attacker may be able to cause authenticated users to cache sensitive account responses and subsequently retrieve those responses without authentication.

Recommendation:
Prevent shared caching of authenticated and user-specific responses, ensure the cache and origin interpret request paths consistently, and configure sensitive endpoints with appropriate Cache-Control directives.
```

---

# Example Finding: API Data Exposure

```text
Finding:
Web Cache Deception Exposes Authenticated API Responses

Affected Endpoint:
GET /api/me

Observed:
The application continued to process requests containing additional static-looking path segments as requests for the authenticated /api/me endpoint.

The caching layer classified the modified URL as cacheable.

After the controlled authenticated response had been cached, the same response could be retrieved without the session cookie.

Impact:
An attacker may obtain user-specific API data by causing a victim to request a specially crafted cacheable URL.

Recommendation:
Ensure authenticated API responses are never stored in shared caches and configure routing and caching rules using consistent canonical paths.
```

---

# Example Finding: Cross-User Disclosure

```text
Finding:
Web Cache Deception Causes Account Data to Be Shared Between Users

Observed:
A unique cacheable URL was requested using controlled Account A.

The response contained the marker:

AM-WCD-ACCOUNT-A-8472

When the same URL was subsequently requested using controlled Account B, the response still contained Account A's marker.

Impact:
Sensitive user-specific responses may be disclosed across account boundaries through the shared caching layer.

Recommendation:
Disable shared caching for personalised responses and ensure user-specific resources cannot be classified as static cacheable objects through manipulated request paths.
```

---

# Example Finding: Administrative Data

```text
Finding:
Web Cache Deception Allows Exposure of Privileged Administrative Responses

Observed:
Using a controlled administrative test account, an administrative endpoint accepted an additional static-looking path component.

The resulting user-specific administrative response was stored by the shared cache and could subsequently be retrieved from an unauthenticated session.

Impact:
An attacker capable of causing a privileged user to request a crafted URL may obtain sensitive administrative information.

Recommendation:
Prevent caching of authenticated administrative responses, strictly canonicalise application routes and ensure cache rules cannot classify dynamic administrative paths as static resources.
```

---

# Reporting Titles

Useful titles include:

```text
Web Cache Deception Allows Disclosure of Authenticated Account Data

Web Cache Deception Exposes User-Specific API Responses

Shared Cache Stores Sensitive Authenticated Responses

Web Cache Deception Allows Cross-User Information Disclosure

Web Cache Deception Exposes Administrative Information

Path Interpretation Discrepancy Causes Sensitive Responses to Be Cached
```

Avoid vague titles such as:

```text
Caching Issue

CDN Problem

Cache Vulnerability
```

Describe the demonstrated impact.

---

# Severity

Severity depends on:

```text
Data sensitivity
Victim interaction
Authentication requirements
Victim privileges
Cache lifetime
Exploit reliability
Additional attack chains
```

For example:

```text
Minor account preference disclosure
```

may be:

```text
Low / Medium
```

while:

```text
Private account data
```

may be:

```text
Medium / High
```

and:

```text
Administrative secrets
Authentication tokens
Highly sensitive personal data
```

may justify:

```text
High / Critical
```

depending on the actual impact.

---

# Remediation

The fundamental objective is:

```text
Sensitive Dynamic Response
        ↓
Never Enter Shared Cache
```

---

# Do Not Cache Authenticated Responses

Where appropriate:

```http
Cache-Control: private, no-store
```

can help ensure sensitive responses are not stored by shared caches.

The exact policy should be selected based on application requirements.

---

# Use `private`

For personalised responses:

```http
Cache-Control: private
```

indicates that shared caches should not store the response.

---

# Use `no-store`

For highly sensitive content:

```http
Cache-Control: no-store
```

prevents storage.

Examples may include:

```text
Account pages
Sensitive API responses
Authentication flows
Financial information
Private messages
```

depending on application requirements.

---

# Do Not Rely Only on File Extensions

Dangerous cache rule:

```text
IF URL ends in .css
THEN cache
```

without considering:

```text
Origin response
Authentication
Route
Cache-Control
```

Prefer cache policies based on explicitly defined static resources.

---

# Explicit Static Paths

Instead of broadly caching:

```text
*.css
```

consider caching known static locations:

```text
/assets/
/static/
/dist/
```

provided those paths cannot route to dynamic sensitive handlers.

---

# Consistent Path Interpretation

Ensure:

```text
CDN
Reverse Proxy
Web Server
Framework
```

agree on:

```text
Path
Normalization
Encoding
Delimiters
```

Avoid architectures where:

```text
Cache sees static file
```

while:

```text
Origin sees sensitive route
```

---

# Reject Unexpected Path Information

If the valid route is:

```text
/account
```

then:

```text
/account/random.css
```

should normally return:

```text
404
```

rather than silently resolving to:

```text
/account
```

unless the routing behaviour is intentionally required.

---

# Canonical Routing

Prefer deterministic routing:

```text
/account
```

rather than allowing arbitrary suffixes such as:

```text
/account/*
```

for endpoints that do not require them.

---

# Respect Origin Cache-Control

CDNs and reverse proxies should respect appropriate origin caching directives.

Avoid configurations that override:

```text
private
no-store
```

for dynamic authenticated responses.

---

# Separate Static and Dynamic Content

A cleaner architecture is:

```text
/static/*
    ↓
Static Content
    ↓
Cache

/account/*
    ↓
Dynamic Content
    ↓
No Shared Cache
```

rather than attempting to infer content type from arbitrary extensions across the entire application.

---

# Authentication-Aware Cache Configuration

If a request contains:

```text
Authorization
```

or:

```text
Session Cookie
```

carefully evaluate whether the response should be stored at all.

Do not assume cache keys based on authentication data are sufficient for every sensitive use case.

---

# Avoid Sensitive Data in Cacheable Responses

Where possible:

```text
Public Cacheable Shell
       +
Authenticated API Request
```

may be safer than caching a complete personalised HTML page.

For example:

```text
Public SPA HTML
      ↓
Browser
      ↓
Authenticated API
      ↓
Private Data
```

provided the authenticated API itself is securely configured.

---

# Purge Existing Cached Responses

After remediation, purge potentially affected objects from:

```text
CDN
Reverse proxy
Edge caches
Application caches
```

Fixing the origin alone may not remove previously cached sensitive responses.

---

# Test After Remediation

Repeat:

```text
/account
```

then:

```text
/account/unique.css
```

Expected behaviour should be one of:

```text
404
```

or:

```text
Dynamic response not stored in shared cache
```

Then verify:

```text
Unauthenticated request
```

cannot retrieve authenticated data.

---

# Remediation Validation

Checklist:

```text
[ ] Sensitive endpoint not shared-cacheable
[ ] Unexpected suffix rejected
[ ] Static extension does not change cacheability
[ ] Cache respects Cache-Control
[ ] Authenticated response not publicly retrievable
[ ] Account A response not returned to Account B
[ ] Encoded path variants behave consistently
[ ] CDN and origin normalize paths consistently
[ ] Previously cached objects purged
```

---

# Pentesting Checklist

## Discovery

```text
[ ] Identify CDN / cache
[ ] Identify cache headers
[ ] Identify sensitive authenticated endpoints
[ ] Identify static cache rules
[ ] Identify tolerated path suffixes
[ ] Identify framework routing behaviour
```

## Baseline

```text
[ ] Request original endpoint
[ ] Record response
[ ] Record Cache-Control
[ ] Record Age
[ ] Record X-Cache
[ ] Record Vary
[ ] Record cookies
```

## Path Testing

```text
[ ] Add unique path segment
[ ] Add static extension
[ ] Test delimiter behaviour
[ ] Test normalization where justified
[ ] Test encoded delimiter where justified
```

## Cache Confirmation

```text
[ ] First request MISS
[ ] Repeat request HIT
[ ] Age behaviour observed
[ ] Exact URL reused
[ ] Browser cache excluded
```

## Authentication

```text
[ ] Controlled Account A
[ ] Unauthenticated retrieval
[ ] Controlled Account B
[ ] Cross-user response comparison
```

## Data

```text
[ ] Username
[ ] Email
[ ] Account ID
[ ] Personal information
[ ] Orders
[ ] Messages
[ ] Tokens
[ ] Administrative data
```

## APIs

```text
[ ] HTML endpoints
[ ] JSON endpoints
[ ] Account APIs
[ ] User APIs
[ ] Administrative APIs
```

## Impact

```text
[ ] Sensitive data exposure
[ ] Cross-user exposure
[ ] Cross-tenant exposure
[ ] Privileged data
[ ] Token exposure
[ ] Additional attack chain
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Comparer
[ ] Logger
[ ] Intruder
```

---

# Decision Tree

```text
SENSITIVE AUTHENTICATED ENDPOINT
            ↓
       ADD UNIQUE PATH
            ↓
SAME SENSITIVE RESPONSE?
      ↓             ↓
     NO            YES
      ↓             ↓
  DIFFERENT      ADD STATIC
  TECHNIQUE      EXTENSION
                    ↓
            SAME RESPONSE?
              ↓          ↓
             NO         YES
              ↓          ↓
          REASSESS     REPEAT
                         ↓
                   CACHE HIT?
                    ↓      ↓
                   NO     YES
                    ↓      ↓
                REASSESS  REMOVE
                          SESSION
                            ↓
                    SAME RESPONSE?
                       ↓       ↓
                      NO      YES
                       ↓       ↓
                  NOT YET   CONTROLLED
                  CONFIRMED  ACCOUNT B
                               ↓
                       CROSS-USER?
                         ↓       ↓
                        NO      YES
                         ↓       ↓
                     ANALYSE   CONFIRMED
                               WCD
                                ↓
                         DETERMINE IMPACT
                                ↓
                              REPORT
```

---

# Quick Reference

```text
WEB CACHE DECEPTION
        ↓
Sensitive Dynamic Endpoint
        ↓
Add Unique Static-Looking Path
        ↓
Origin Still Returns Sensitive Content?
        ↓
YES
        ↓
Shared Cache Stores It?
        ↓
YES
        ↓
Remove Authentication
        ↓
Same Cached Sensitive Response?
        ↓
YES
        ↓
CONFIRMED
```

Remember:

```text
Cache Poisoning:

Attacker Response
      ↓
Cache
      ↓
Victim


Cache Deception:

Victim Response
      ↓
Cache
      ↓
Attacker
```

---

# Recommended Testing Workflow

```text
Burp Proxy
     ↓
Find Sensitive Endpoint
     ↓
Burp Repeater
     ↓
Baseline
     ↓
Unique Path
     ↓
Static Extension
     ↓
Check Cache Headers
     ↓
Repeat Request
     ↓
MISS → HIT?
     ↓
Remove Session
     ↓
Controlled Data Returned?
     ↓
Second Controlled Account
     ↓
Confirm Cross-User Exposure
     ↓
Document Minimal Proof
```

---

# References

## PortSwigger Web Security Academy: Web Cache Deception

https://portswigger.net/web-security/web-cache-deception

PortSwigger's Web Security Academy material covering:

```text
Web cache deception
Cache rules
Path mapping discrepancies
Delimiter discrepancies
Normalization discrepancies
Cache exploitation
```

---

## PortSwigger Web Cache Deception Labs

https://portswigger.net/web-security/all-labs#web-cache-deception

Practical labs covering web cache deception techniques.

---

## PortSwigger Research: Gotta Cache 'em All

https://portswigger.net/research/gotta-cache-em-all

PortSwigger research by James Kettle exploring modern web cache exploitation and discrepancies between caching layers and application servers.

---

## PortSwigger Web Cache Poisoning

https://portswigger.net/web-security/web-cache-poisoning

Useful for understanding the related but distinct web cache poisoning vulnerability class.

---

## RFC 9111: HTTP Caching

https://www.rfc-editor.org/rfc/rfc9111

The HTTP caching specification.

---

## MDN: HTTP Caching

https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching

Overview of HTTP caching concepts.

---

## MDN: Cache-Control

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control

Reference for directives including:

```text
private
public
no-store
no-cache
max-age
s-maxage
```

---

## Burp Suite Documentation

https://portswigger.net/burp/documentation

Useful for:

```text
Proxy
Repeater
Comparer
Intruder
Logger
```

during cache testing.

---

## Param Miner

https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943

Useful for identifying hidden inputs and cache-related behaviour.

---

# Final Web Cache Deception Testing Model

```text
                              CLIENT
                                ↓
                         AUTHENTICATED USER
                                ↓
                    SENSITIVE DYNAMIC ENDPOINT
                                ↓
                         /account
                                ↓
                       MODIFY REQUEST PATH
                                ↓
                /account/AM-WCD-8472.css
                                ↓
                 ┌──────────────┴──────────────┐
                 ↓                             ↓
               CACHE                         ORIGIN
                 ↓                             ↓
          SEES STATIC .CSS              SEES /account
                 ↓                             ↓
          CACHEABLE RESOURCE           AUTHENTICATED PAGE
                 ↓                             ↓
                 └──────────────┬──────────────┘
                                ↓
                       SENSITIVE RESPONSE
                                ↓
                          SHARED CACHE
                                ↓
                       ┌────────┴────────┐
                       ↓                 ↓
                 ORIGINAL USER       ATTACKER /
                                      OTHER USER
                                           ↓
                                  SAME CACHED RESPONSE
                                           ↓
                                   SENSITIVE DATA
                                      DISCLOSED
                                           ↓
                                  WEB CACHE DECEPTION
```

The key principle is:

> Web cache deception is fundamentally an interpretation discrepancy. The cache believes it is storing a safe, reusable resource while the origin believes it is serving sensitive dynamic content. During testing, first determine how the origin handles modified paths, then determine how the caching layer classifies those same paths, and finally prove the security impact using controlled accounts and unique cache keys. A cache header or unusual route alone is not enough: the strongest evidence is a sensitive response generated in one controlled authenticated context and subsequently returned from a shared cache to another context that was not authorised to receive it.
