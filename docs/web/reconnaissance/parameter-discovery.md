# Parameter Discovery

Parameter discovery is the process of identifying input parameters accepted by a web application or API.

Parameters are important because they represent locations where user-controlled input enters the application.

They may influence:

```text
Database queries
File operations
Redirects
Authentication
Authorisation
API requests
Templates
Operating system commands
Server-side HTTP requests
Application state
Business logic
```

A parameter that appears insignificant may expose important functionality when its value is modified.

!!! warning "Authorised Security Testing"
    Perform parameter discovery and subsequent testing only against systems for which you have explicit authorisation.

---

# Objectives

The objective is to identify as much of the application's input surface as possible.

Parameters may exist in:

```text
URL query strings
POST bodies
JSON requests
XML requests
HTTP headers
Cookies
Path parameters
Multipart forms
GraphQL requests
WebSocket messages
```

A practical workflow is:

```text
Endpoint Discovery
        ↓
Historical URL Collection
        ↓
Parameter Extraction
        ↓
Active Parameter Discovery
        ↓
JavaScript Analysis
        ↓
API Analysis
        ↓
Burp Suite Analysis
        ↓
Deduplication
        ↓
Classification
        ↓
Manual Verification
        ↓
Vulnerability Testing
```

The objective is not simply to collect thousands of URLs.

The objective is to understand:

> Where does user-controlled input enter the application?

---

# What Is a Parameter?

Consider:

```text
https://target.example/product?id=123
```

The parameter is:

```text
id
```

and the value is:

```text
123
```

Multiple parameters may exist:

```text
https://target.example/search?q=test&page=2&sort=date
```

Parameters:

```text
q
page
sort
```

Values:

```text
test
2
date
```

These parameters may behave very differently internally.

For example:

```text
q
 ↓
Search functionality
 ↓
Database query
```

while:

```text
sort
 ↓
Query construction
 ↓
Database ordering
```

Understanding the parameter's purpose is therefore just as important as discovering it.

---

# Parameter Locations

Parameters are not limited to URLs.

## Query Parameters

Example:

```http
GET /product?id=123&category=books HTTP/1.1
Host: target.example
```

Parameters:

```text
id
category
```

---

## Form Parameters

Example:

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=user&password=password
```

Parameters:

```text
username
password
```

---

## JSON Parameters

Modern APIs frequently use JSON.

Example:

```http
POST /api/profile HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "username": "test",
  "email": "test@example.com"
}
```

Parameters:

```text
username
email
```

---

## XML Parameters

Example:

```xml
<user>
    <username>test</username>
    <email>test@example.com</email>
</user>
```

Potential input points:

```text
username
email
```

---

## Path Parameters

Some frameworks encode parameters directly into paths.

Example:

```text
/users/123
```

The value:

```text
123
```

may represent:

```text
user_id
```

Another example:

```text
/api/orders/8472
```

Conceptually:

```text
/api/orders/{order_id}
```

Path parameters are particularly important when testing access controls.

---

## Headers

Applications may process user-controlled headers.

Examples:

```text
Host
Origin
Referer
User-Agent
X-Forwarded-For
X-Forwarded-Host
X-Original-URL
X-Rewrite-URL
Forwarded
```

Headers should therefore be considered part of the application's input surface.

---

## Cookies

Cookies can also contain application-controlled parameters.

Example:

```http
Cookie: session=abc123; language=en; role=user
```

Potential values:

```text
session
language
role
```

Never assume a cookie is safe simply because the browser normally manages it.

---

# Start With Burp Suite

Before using automated tools, inspect the application through Burp Suite.

Use:

```text
Proxy
→ HTTP history
```

and:

```text
Target
→ Site map
```

Look for requests containing:

```text
?
=
POST bodies
JSON
XML
Cookies
Custom headers
Path identifiers
```

For example:

```http
GET /account?id=1001 HTTP/1.1
```

or:

```http
POST /api/search HTTP/1.1
Content-Type: application/json

{
  "query": "administrator",
  "limit": 20
}
```

Burp often reveals parameters that automated URL collection tools cannot see.

---

# Browser Developer Tools

Browser Developer Tools are also useful.

Open:

```text
Developer Tools
→ Network
```

Interact with the application.

Look for:

```text
XHR
Fetch
API
GraphQL
WebSocket
Form submissions
Background requests
```

Modern applications may make numerous API requests that are not visible in the page URL.

---

# Historical Parameter Discovery

Historical URL sources are extremely valuable for parameter discovery.

An application might currently expose:

```text
/search
```

but historical data could reveal:

```text
/search?q=test
/search?query=test
/search?keyword=test
/search?category=1
```

Even if some URLs are old, the parameters may still be recognised by the current application.

Useful tools include:

```text
waybackurls
gau
urlfinder
```

---

# Waybackurls

Collect historical URLs:

```bash
echo target.example | waybackurls
```

Save the output:

```bash
echo target.example | waybackurls > wayback.txt
```

Remove duplicates:

```bash
sort -u wayback.txt -o wayback.txt
```

Find URLs containing parameters:

```bash
grep '=' wayback.txt
```

Or:

```bash
grep '?' wayback.txt
```

Save parameterised URLs:

```bash
grep '=' wayback.txt > wayback-params.txt
```

---

# GAU

GAU can collect URLs from multiple public sources.

Example:

```bash
gau target.example
```

Save output:

```bash
gau target.example > gau.txt
```

Find parameterised URLs:

```bash
grep '=' gau.txt
```

Save them:

```bash
grep '=' gau.txt > gau-params.txt
```

---

# URLFinder

URLFinder can also collect URLs associated with a domain.

Example:

```bash
urlfinder -d target.example
```

Save results:

```bash
urlfinder -d target.example -o urlfinder.txt
```

Extract parameterised URLs:

```bash
grep '=' urlfinder.txt > urlfinder-params.txt
```

---

# Combine Historical Sources

Combine the results:

```bash
cat wayback.txt gau.txt urlfinder.txt \
  | sort -u \
  > all-urls.txt
```

Then extract URLs containing parameters:

```bash
grep '=' all-urls.txt \
  | sort -u \
  > parameters.txt
```

Quick count:

```bash
wc -l parameters.txt
```

This produces an initial parameter attack surface.

---

# Extract Parameter Names

Suppose the collected URLs contain:

```text
https://target.example/search?q=test&page=1
https://target.example/product?id=100
https://target.example/redirect?url=https://example.com
```

The interesting parameter names are:

```text
q
page
id
url
```

A simple shell pipeline can help extract names:

```bash
cat parameters.txt \
  | grep -oE '[?&][^=]+' \
  | sed 's/^[?&]//' \
  | sort -u
```

Potential output:

```text
id
page
q
url
```

This can quickly reveal recurring parameter patterns.

---

# ParamSpider

ParamSpider is designed to discover parameters from web archives.

Basic usage:

```bash
python3 paramspider.py -d target.example
```

Depending on the installed version, output is typically written into an output directory.

For example:

```text
output/
└── target.example.txt
```

Inspect:

```bash
cat output/target.example.txt
```

Potential results:

```text
https://target.example/search?q=FUZZ
https://target.example/product?id=FUZZ
https://target.example/redirect?url=FUZZ
https://target.example/download?file=FUZZ
```

This format is useful because parameter values are replaced with:

```text
FUZZ
```

making the URLs ready for further testing.

---

# ParamSpider Workflow

A practical workflow might be:

```bash
python3 paramspider.py -d target.example
```

Then:

```bash
cd output
```

Review:

```bash
cat target.example.txt
```

Count:

```bash
wc -l target.example.txt
```

Deduplicate:

```bash
sort -u target.example.txt -o target.example.txt
```

The output can then be fed into specialised analysis tools.

---

# Active Parameter Discovery

Historical sources only reveal parameters that have previously appeared publicly.

Applications may also accept undocumented parameters.

Active parameter discovery attempts to identify them.

Useful tools include:

```text
Arjun
FFUF
Burp Intruder
Param Miner
```

---

# Arjun

Arjun is designed to discover hidden HTTP parameters.

Basic example:

```bash
arjun -u https://target.example/page
```

Potential result:

```text
parameter detected:

debug
```

The application might therefore accept:

```text
https://target.example/page?debug=true
```

even though the parameter never appeared in the application's normal interface.

---

# GET Parameter Discovery With Arjun

Example:

```bash
arjun \
  -u https://target.example/search \
  -m GET
```

Possible discovered parameters:

```text
q
query
search
page
limit
sort
```

Always manually verify interesting results.

---

# POST Parameter Discovery With Arjun

Arjun can also test POST parameters.

Example:

```bash
arjun \
  -u https://target.example/api/search \
  -m POST
```

This can help identify parameters accepted by endpoints where the request structure is not fully documented.

---

# Parameter Discovery With FFUF

FFUF can fuzz parameter names.

Suppose:

```text
https://target.example/page
```

You want to determine whether undocumented GET parameters are accepted.

Example:

```bash
ffuf \
  -u 'https://target.example/page?FUZZ=test' \
  -w parameters.txt
```

Possible wordlist entries:

```text
id
page
debug
admin
user
file
url
redirect
callback
lang
```

Look for changes in:

```text
Status
Response size
Word count
Line count
Redirect
Headers
```

---

# Establish a Baseline

Before fuzzing parameter names, understand the normal response.

Request:

```bash
curl -i https://target.example/page
```

Then:

```bash
curl -i 'https://target.example/page?randomparameter123=test'
```

Compare the responses.

If the application ignores unknown parameters, both responses may be identical.

A valid parameter may produce a different:

```text
Response size
Status code
Header
Redirect
Page content
Timing
```

This difference can be used during discovery.

---

# FFUF Response Filtering

If the baseline response size is:

```text
4242
```

filter it:

```bash
ffuf \
  -u 'https://target.example/page?FUZZ=test' \
  -w parameters.txt \
  -fs 4242
```

Other useful filters:

```text
-fs    Response size
-fw    Word count
-fl    Line count
-fc    Status code
```

This can significantly reduce false positives.

---

# Burp Param Miner

Burp Suite's Param Miner extension is useful for identifying hidden parameters.

It can test:

```text
Query parameters
Headers
Cookies
```

This is particularly useful for discovering behaviour associated with:

```text
Caching
Routing
Proxy behaviour
Hidden application functionality
```

Use the extension carefully because parameter guessing can generate a significant number of requests.

---

# JavaScript Parameter Discovery

JavaScript files frequently reveal parameter names.

For example:

```javascript
fetch("/api/users?id=" + userId)
```

reveals:

```text
/api/users
id
```

Another example:

```javascript
axios.get("/api/search", {
    params: {
        query: searchTerm,
        limit: 20
    }
})
```

reveals:

```text
query
limit
```

Search JavaScript files for patterns such as:

```text
?
&
=
params
query
search
id
url
redirect
callback
file
path
```

---

# Grep JavaScript

If JavaScript files have been downloaded:

```bash
grep -RniE \
  'id|user|url|uri|redirect|callback|file|path|query|search|page|limit' \
  javascript/
```

This is noisy but can reveal useful parameter names.

You can also search for API routes:

```bash
grep -RniE \
  '(/api/|/graphql|/admin|/internal|/upload|/download)' \
  javascript/
```

Combine endpoint discovery with parameter discovery.

---

# API Documentation

API documentation can provide the most accurate parameter inventory.

Look for:

```text
Swagger
OpenAPI
Postman collections
GraphQL documentation
Developer portals
API reference pages
```

Common endpoints include:

```text
/swagger
/swagger-ui
/swagger.json
/openapi.json
/api-docs
/v2/api-docs
/v3/api-docs
```

An OpenAPI specification might describe:

```yaml
parameters:
  - name: id
    in: query
    required: true
```

This immediately identifies:

```text
Parameter: id
Location: query
Required: yes
```

---

# Swagger and OpenAPI Analysis

When API documentation is available, record:

```text
Endpoint
Method
Parameter
Parameter location
Data type
Required/optional
Expected format
Authentication
```

For example:

| Endpoint | Method | Parameter | Location | Type |
|---|---|---|---|---|
| `/api/users` | GET | `id` | Query | Integer |
| `/api/search` | GET | `q` | Query | String |
| `/api/files` | POST | `file` | Multipart | File |
| `/api/orders/{id}` | GET | `id` | Path | Integer |

This provides an excellent starting point for later testing.

---

# GraphQL Parameters

GraphQL handles input differently from traditional REST APIs.

Example:

```graphql
query {
  user(id: 123) {
    username
    email
  }
}
```

Input:

```text
id
```

Another example:

```graphql
query Search($term: String!) {
  search(query: $term) {
    title
  }
}
```

Input:

```text
term
query
```

GraphQL variables may therefore represent important user-controlled input.

---

# JSON Parameter Mapping

Consider:

```json
{
  "user": {
    "name": "test",
    "email": "test@example.com"
  },
  "preferences": {
    "language": "en"
  }
}
```

The input surface includes:

```text
user.name
user.email
preferences.language
```

Do not only record top-level JSON keys.

Nested parameters can behave differently.

---

# Mass Assignment Awareness

JSON APIs sometimes accept more fields than the user interface sends.

For example, the UI may send:

```json
{
  "name": "Asif"
}
```

while the backend model contains:

```text
name
email
role
status
verified
```

Parameter discovery may therefore involve understanding which additional fields the API accepts.

This becomes particularly relevant during later business logic and authorisation testing.

Do not modify security-sensitive properties outside the authorised scope.

---

# Parameter Classification

Once parameters have been discovered, classify them.

A useful classification is:

```text
Identifiers
Search
Files
URLs
Redirects
Paths
Commands
Templates
Authentication
Authorisation
Pagination
Sorting
Filters
Callbacks
Language
Debug
API control
```

For example:

```text
id
user_id
account_id
order_id
```

could be classified as:

```text
Identifiers
```

while:

```text
url
uri
target
dest
destination
callback
```

could be classified as:

```text
URL-like input
```

Classification helps determine what type of testing should happen next.

---

# Interesting Parameter Names

Certain names deserve additional attention because they may indicate particular functionality.

## Identifiers

```text
id
uid
user
user_id
account
account_id
order
order_id
document
document_id
```

Potential testing areas:

```text
Authorisation
IDOR
Object-level access control
```

---

## URL Parameters

```text
url
uri
target
dest
destination
redirect
redirect_url
return
return_url
next
continue
callback
callback_url
```

Potential testing areas:

```text
Open redirect
Server-Side Request Forgery
Callback handling
```

---

## File Parameters

```text
file
filename
filepath
path
document
download
template
page
include
```

Potential testing areas:

```text
Path traversal
File inclusion
File handling
Download authorisation
```

---

## Search Parameters

```text
q
query
search
keyword
filter
term
```

Potential testing areas:

```text
SQL injection
Cross-Site Scripting
Search logic
Input validation
```

---

## Command-Like Parameters

```text
cmd
command
exec
execute
process
host
ip
```

Potential testing areas:

```text
Command injection
Argument injection
Server-side processing
```

---

## Template Parameters

```text
template
view
name
message
content
format
```

Potential testing areas:

```text
Template injection
HTML injection
Cross-Site Scripting
```

---

## Debug Parameters

```text
debug
test
dev
verbose
trace
preview
internal
```

Potentially interesting because they may expose:

```text
Debug information
Alternative application behaviour
Development functionality
Verbose errors
```

---

# Parameter Wordlists

SecLists contains parameter-related wordlists.

Search:

```bash
find /usr/share/seclists \
  -iname '*param*'
```

You can also create a target-specific parameter wordlist from discovered application terminology.

For example, if the application contains:

```text
customer
invoice
contract
document
organisation
```

create:

```text
customer
customer_id
invoice
invoice_id
contract
contract_id
document
document_id
organisation
organisation_id
```

Target-specific wordlists can be more effective than generic ones.

---

# Build a Custom Parameter Wordlist

Suppose reconnaissance identifies:

```text
/users
/accounts
/orders
/documents
```

A custom list could contain:

```text
user
userid
user_id
account
accountid
account_id
order
orderid
order_id
document
documentid
document_id
```

This can then be tested with:

```bash
ffuf \
  -u 'https://target.example/page?FUZZ=1' \
  -w custom-parameters.txt
```

---

# Deduplicating URLs

Historical sources often produce many duplicates.

For example:

```text
https://target.example/product?id=1
https://target.example/product?id=2
https://target.example/product?id=3
```

These represent the same basic attack surface:

```text
/product?id=
```

Testing every historical value is usually unnecessary.

Instead, normalise URLs based on:

```text
Host
Path
Parameter names
```

---

# uro

The `uro` tool can help reduce duplicate URLs.

Example:

```bash
cat all-urls.txt | uro
```

Save results:

```bash
cat all-urls.txt \
  | uro \
  > unique-urls.txt
```

This can significantly reduce noisy historical URL collections.

---

# qsreplace

`qsreplace` can replace query-string values.

For example:

```bash
echo 'https://target.example/search?q=test&page=1' \
  | qsreplace FUZZ
```

Result:

```text
https://target.example/search?q=FUZZ&page=FUZZ
```

This can make parameterised URLs easier to process with later testing tools.

---

# Parameter Discovery Pipeline

A useful passive pipeline is:

```bash
echo target.example | waybackurls > wayback.txt
```

```bash
gau target.example > gau.txt
```

```bash
urlfinder -d target.example -o urlfinder.txt
```

Combine:

```bash
cat wayback.txt gau.txt urlfinder.txt \
  | sort -u \
  > all-urls.txt
```

Reduce noise:

```bash
cat all-urls.txt \
  | uro \
  > unique-urls.txt
```

Extract parameterised URLs:

```bash
grep '=' unique-urls.txt \
  > parameterised-urls.txt
```

Count:

```bash
wc -l parameterised-urls.txt
```

---

# Parameter Discovery With ParamSpider

A second workflow can use ParamSpider directly:

```bash
python3 paramspider.py -d target.example
```

Then:

```bash
cd output
```

Review:

```bash
cat target.example.txt
```

Deduplicate:

```bash
sort -u target.example.txt \
  -o target.example.txt
```

The resulting URLs can then be manually reviewed or passed into specialised analysis tools.

---

# XSS Candidate Discovery With kxss

After collecting parameterised GET URLs, `kxss` can help identify parameters where supplied input is reflected in responses.

For example:

```bash
cat parameterised-urls.txt | kxss
```

Or with ParamSpider output:

```bash
cat output/target.example.txt | kxss
```

This does not automatically mean an endpoint is vulnerable to Cross-Site Scripting.

It identifies locations where input reflection may deserve further investigation.

A useful workflow is:

```text
Parameter Discovery
        ↓
Parameterised URLs
        ↓
kxss
        ↓
Reflection Candidates
        ↓
Manual Burp Testing
        ↓
Context Analysis
        ↓
XSS Testing
```

Always manually verify results.

---

# Live URL Verification

Historical URLs may no longer exist.

Before extensive testing, determine whether endpoints are still reachable.

For example, URL lists can be reviewed using HTTP probing tools such as:

```text
httpx
```

A conceptual workflow is:

```text
Historical URLs
      ↓
Deduplicate
      ↓
Probe
      ↓
Keep Relevant Live Endpoints
      ↓
Parameter Analysis
```

This can prevent spending time testing obsolete endpoints.

---

# GET Versus POST Parameters

GET parameters are easier to discover because they frequently appear in:

```text
Browser history
Search engine indexes
Web archives
JavaScript
Logs
Links
```

POST parameters are less visible.

They are more commonly discovered through:

```text
Burp Suite
Forms
JavaScript
API documentation
Source code
Mobile applications
Active parameter discovery
```

Do not assume a complete GET parameter inventory represents the complete input surface.

---

# Hidden Form Fields

HTML forms may contain hidden inputs.

Example:

```html
<input type="hidden" name="user_id" value="123">
<input type="hidden" name="action" value="update">
```

Parameters:

```text
user_id
action
```

Hidden does not mean trusted.

The browser can modify these values before submission.

Review all form fields through Burp Suite rather than relying only on visible page elements.

---

# Disabled Form Fields

Disabled fields can also reveal interesting application parameters.

Example:

```html
<input name="role" value="user" disabled>
```

Although the browser may not normally submit the field, the backend may still accept it if manually included.

Record these parameters for later validation.

---

# HTTP Method Analysis

The same endpoint may behave differently depending on the HTTP method.

For example:

```text
GET /api/user
POST /api/user
PUT /api/user
PATCH /api/user
DELETE /api/user
```

Each method may accept different parameters.

When documentation or application behaviour suggests multiple methods, map the parameter set independently.

---

# Content-Type Analysis

Parameter parsing may also depend on the content type.

For example:

```text
application/x-www-form-urlencoded
application/json
multipart/form-data
application/xml
text/xml
```

An endpoint may process:

```json
{"id":123}
```

differently from:

```text
id=123
```

Record the expected content type alongside each parameter.

---

# Parameter Behaviour Analysis

Discovery alone is not enough.

For each important parameter, determine:

```text
Is it required?
What data type does it expect?
Does it accept empty values?
Does it accept multiple values?
Does it affect the response?
Does it trigger a redirect?
Does it reference an object?
Does it reference a file?
Does it reference a URL?
Is it reflected?
Is it stored?
Does it change application state?
```

This creates context for later vulnerability testing.

---

# Duplicate Parameters

Applications may behave unexpectedly when the same parameter appears multiple times.

Example:

```text
?id=1&id=2
```

Different frameworks may:

```text
Use first value
Use last value
Create an array
Concatenate values
Reject request
```

This behaviour can become relevant during later validation and access-control testing.

Record it when observed.

---

# Case Sensitivity

Parameter names may be case-sensitive.

For example:

```text
id
ID
Id
userId
userid
userID
```

Do not automatically assume these are equivalent.

Application frameworks and custom parsing logic may treat them differently.

---

# Parameter Relationships

Parameters should not always be analysed independently.

Consider:

```text
/account?user_id=100&organisation_id=5
```

The relationship may be:

```text
organisation_id
      ↓
Defines organisation

user_id
      ↓
Defines user inside organisation
```

Testing the parameters together may reveal behaviour that testing each one independently misses.

This is particularly important for:

```text
Business logic
Authorisation
Multi-tenant applications
Object-level access control
```

---

# Parameter Inventory

Maintain a structured parameter inventory.

For example:

| Endpoint | Method | Parameter | Location | Type | Purpose |
|---|---|---|---|---|---|
| `/search` | GET | `q` | Query | String | Search |
| `/product` | GET | `id` | Query | Integer | Product identifier |
| `/redirect` | GET | `url` | Query | URL | Redirect destination |
| `/download` | GET | `file` | Query | String | File selection |
| `/api/user` | POST | `email` | JSON | String | User email |
| `/api/order/{id}` | GET | `id` | Path | Integer | Order identifier |

Add additional columns when useful:

```text
Authentication required
Role required
Reflected
Stored
Interesting behaviour
Testing status
Notes
```

---

# Prioritising Parameters

Not every parameter deserves equal attention.

A useful priority order is:

```text
Object identifiers
        ↓
URL parameters
        ↓
File/path parameters
        ↓
Authentication parameters
        ↓
Search/filter parameters
        ↓
Template/content parameters
        ↓
Debug parameters
        ↓
Pagination/display parameters
```

However, context matters.

For example:

```text
?page=2
```

might appear harmless.

But:

```text
?page=../../etc/passwd
```

would indicate that `page` is actually being used as a file path.

Parameter names are hints, not proof.

---

# Mapping Parameters to Testing Areas

Once parameters have been classified, map them to likely testing categories.

| Parameter Pattern | Testing Areas |
|---|---|
| `id`, `uid`, `account_id` | Authorisation, IDOR |
| `q`, `search`, `query` | XSS, SQLi, input validation |
| `url`, `uri`, `target` | SSRF, open redirect |
| `redirect`, `next`, `return` | Open redirect, authentication flows |
| `file`, `path`, `page` | Path traversal, file handling |
| `template`, `view` | SSTI, file inclusion |
| `cmd`, `command`, `exec` | Command injection |
| `callback` | Redirects, SSRF, JSONP |
| `role`, `admin`, `privilege` | Authorisation, mass assignment |
| `debug`, `test`, `dev` | Debug functionality |
| `sort`, `order`, `filter` | SQLi, business logic |
| `host`, `domain`, `ip` | SSRF, command injection, network functionality |

This mapping should guide testing, not replace manual analysis.

---

# Practical Workflow

A complete parameter discovery workflow could look like this.

## 1. Browse the application

Use:

```text
Browser
Burp Suite
Developer Tools
```

Record:

```text
GET parameters
POST parameters
JSON keys
Cookies
Headers
Path identifiers
```

---

## 2. Collect historical URLs

```bash
echo target.example | waybackurls > wayback.txt
```

```bash
gau target.example > gau.txt
```

```bash
urlfinder -d target.example -o urlfinder.txt
```

---

## 3. Combine results

```bash
cat wayback.txt gau.txt urlfinder.txt \
  | sort -u \
  > all-urls.txt
```

---

## 4. Reduce duplicates

```bash
cat all-urls.txt \
  | uro \
  > unique-urls.txt
```

---

## 5. Extract parameterised URLs

```bash
grep '=' unique-urls.txt \
  > parameterised-urls.txt
```

---

## 6. Run ParamSpider

```bash
python3 paramspider.py -d target.example
```

Review:

```bash
cat output/target.example.txt
```

---

## 7. Review JavaScript

Search for:

```text
API endpoints
Parameter names
Fetch requests
Axios requests
GraphQL queries
Hidden functionality
```

---

## 8. Active parameter discovery

For interesting endpoints:

```bash
arjun -u https://target.example/page
```

or:

```bash
ffuf \
  -u 'https://target.example/page?FUZZ=test' \
  -w parameters.txt
```

---

## 9. Identify reflection candidates

For authorised GET-based testing:

```bash
cat parameterised-urls.txt | kxss
```

---

## 10. Verify manually

Send interesting requests to Burp Repeater.

Determine:

```text
What does the parameter control?
What data type is expected?
How does the response change?
Where is the value processed?
What should be tested next?
```

---

# Example Attack Surface

Suppose reconnaissance produces:

```text
/search?q=test
/product?id=123
/download?file=document.pdf
/redirect?url=https://example.com
/api/user?user_id=100
```

The parameters can be mapped as:

```text
q
 ↓
Search
 ↓
XSS / SQLi investigation

id
 ↓
Object identifier
 ↓
Authorisation / IDOR investigation

file
 ↓
File reference
 ↓
File handling / path traversal investigation

url
 ↓
URL
 ↓
Redirect / SSRF investigation

user_id
 ↓
User object
 ↓
Authorisation investigation
```

This demonstrates why parameter discovery is a bridge between reconnaissance and vulnerability testing.

---

# Recommended Output Structure

Keep reconnaissance output organised.

For example:

```text
recon/
├── urls/
│   ├── wayback.txt
│   ├── gau.txt
│   ├── urlfinder.txt
│   ├── all-urls.txt
│   └── unique-urls.txt
│
├── parameters/
│   ├── parameterised-urls.txt
│   ├── parameter-names.txt
│   ├── paramspider.txt
│   ├── arjun.txt
│   └── reflection-candidates.txt
│
└── javascript/
    └── endpoints.txt
```

This makes later testing considerably easier.

---

# Parameter Discovery Checklist

```text
[ ] Review Burp HTTP history
[ ] Review Burp site map
[ ] Review browser Network requests
[ ] Record GET parameters
[ ] Record POST parameters
[ ] Record JSON parameters
[ ] Record XML parameters
[ ] Record path parameters
[ ] Review cookies
[ ] Review interesting headers
[ ] Collect Wayback URLs
[ ] Collect GAU URLs
[ ] Collect URLFinder URLs
[ ] Run ParamSpider
[ ] Deduplicate URLs
[ ] Extract parameter names
[ ] Review JavaScript
[ ] Review Swagger/OpenAPI
[ ] Review GraphQL requests
[ ] Check hidden form fields
[ ] Check disabled form fields
[ ] Perform active parameter discovery
[ ] Establish baseline responses
[ ] Review response differences
[ ] Identify reflection candidates
[ ] Classify parameters
[ ] Prioritise interesting parameters
[ ] Record parameters in an inventory
[ ] Manually verify important findings
```

---

# Quick Reference

## Passive Discovery

```bash
echo target.example | waybackurls > wayback.txt
```

```bash
gau target.example > gau.txt
```

```bash
urlfinder -d target.example -o urlfinder.txt
```

```bash
python3 paramspider.py -d target.example
```

---

## Combine URLs

```bash
cat wayback.txt gau.txt urlfinder.txt \
  | sort -u \
  > all-urls.txt
```

---

## Deduplicate

```bash
cat all-urls.txt \
  | uro \
  > unique-urls.txt
```

---

## Parameterised URLs

```bash
grep '=' unique-urls.txt \
  > parameterised-urls.txt
```

---

## Extract Parameter Names

```bash
cat parameterised-urls.txt \
  | grep -oE '[?&][^=]+' \
  | sed 's/^[?&]//' \
  | sort -u \
  > parameter-names.txt
```

---

## Active Discovery

```bash
arjun -u https://target.example/page
```

---

## FFUF Parameter Names

```bash
ffuf \
  -u 'https://target.example/page?FUZZ=test' \
  -w parameter-names.txt
```

---

## Reflection Candidates

```bash
cat parameterised-urls.txt | kxss
```

---

# Key Principle

Parameter discovery should not be treated as:

```text
Collect URLs
     ↓
Find ?
     ↓
Done
```

A better approach is:

```text
Discover Endpoint
        ↓
Identify Inputs
        ↓
Understand Input Location
        ↓
Determine Purpose
        ↓
Classify Parameter
        ↓
Observe Behaviour
        ↓
Prioritise
        ↓
Test
```

The important question is not:

> How many parameters did I find?

The important questions are:

> What does each parameter control?

and:

> Where does this input go?

A good parameter inventory transforms reconnaissance from a collection of URLs into a structured map of the application's **user-controlled input surface**.
