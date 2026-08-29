# Input Validation

Input validation is the process of verifying that data received by an application conforms to the format, type, length, range, structure, and business rules expected by the application before the data is processed.

A simplified model is:

```text
Untrusted Input
      |
      v
Validation
      |
      +---- Invalid ----> Reject
      |
      v
Valid Input
      |
      v
Application Logic
      |
      v
Sensitive Operation
```

Input validation should be performed as early as possible in the application's data flow.

The fundamental security principle is:

```text
Never assume input is trustworthy
because it came from the expected client.
```

!!! warning "Authorised Security Testing"
    Input validation testing can involve modifying parameters, HTTP headers, cookies, JSON, XML, multipart data, file metadata, HTTP methods, and other application inputs. Perform these tests only against systems for which you have explicit authorisation. Start with controlled canary values and avoid destructive payloads unless they are specifically required and permitted by the rules of engagement.

---

# Why Input Validation Matters

Applications process data from many different sources.

Examples include:

```text
URL parameters
Form fields
JSON
XML
HTTP headers
Cookies
File uploads
WebSockets
GraphQL
gRPC
APIs
Webhooks
Third-party integrations
Message queues
Imported files
Backend systems
```

If an application accepts unexpected or malformed input, the result may range from a harmless validation error to a serious security vulnerability.

Conceptually:

```text
Attacker-Controlled Input
          |
          v
Weak / Missing Validation
          |
          v
Unexpected Application Behaviour
          |
          +-- Injection
          +-- Business logic abuse
          +-- Data corruption
          +-- Parser confusion
          +-- Access-control problems
          +-- Application errors
          +-- Resource exhaustion
```

Input validation is therefore one layer of a broader secure-design strategy.

---

# Input Validation Is Not a Complete Injection Defence

A critical distinction is:

```text
Input Validation
       !=
Complete Injection Prevention
```

For example, SQL injection should primarily be prevented through:

```text
Parameterized queries
Prepared statements
Safe ORM usage
```

not by attempting to remove characters such as:

```text
'
"
;
--
```

Similarly, XSS should primarily be addressed through:

```text
Context-aware output encoding
Safe DOM APIs
Appropriate sanitisation where HTML is intentionally allowed
Content Security Policy as defence in depth
```

Input validation can significantly reduce attack surface, but it should not replace the security control appropriate to the destination or sink.

---

# Validation vs Sanitisation

These concepts are frequently confused.

## Validation

Validation asks:

```text
Is this input acceptable?
```

Example:

```text
Expected:
Integer from 1 to 100

Received:
42

Result:
Accept
```

Another example:

```text
Expected:
Integer from 1 to 100

Received:
hello

Result:
Reject
```

---

## Sanitisation

Sanitisation asks:

```text
Can this data be transformed into a safer form?
```

Example:

```text
User-supplied HTML
        |
        v
HTML Sanitiser
        |
        v
Allowed HTML subset
```

Sanitisation is particularly relevant when potentially dangerous content is intentionally allowed.

For example:

```text
Rich-text editor
Markdown renderer
HTML comments
CMS content
```

Do not attempt to create complex HTML sanitisation using custom regular expressions.

Use mature libraries designed for that purpose.

---

# Validation vs Encoding

Encoding is another different concept.

Example:

```text
User Input
    |
    v
Output Encoding
    |
    v
HTML Context
```

Input validation determines whether input is acceptable.

Output encoding ensures data is safely represented in a particular output context.

For example:

```text
HTML body
HTML attribute
JavaScript
URL
CSS
```

may require different encoding strategies.

---

# Validation vs Escaping

Escaping changes the interpretation of characters in a specific context.

Example conceptually:

```text
'
```

may need special handling in one context but not another.

Escaping should not be treated as universal validation.

---

# Validation vs Normalisation

Normalisation converts equivalent representations into a consistent form.

Example:

```text
Input
  |
  v
Canonical / Normal Form
  |
  v
Validation
```

This is important because attackers may attempt to represent the same logical input in multiple ways.

Examples include:

```text
URL encoding
Double encoding
Unicode
Case differences
Path representations
Whitespace variations
```

---

# Validation vs Business Rules

A value can be technically valid but still invalid in the application's business context.

Example:

```text
quantity=999999
```

may be:

```text
Valid integer
```

but:

```text
Invalid order quantity
```

Therefore validation should occur at multiple levels.

---

# Syntactic Validation

Syntactic validation verifies whether input has the correct structure.

Examples:

```text
Is this an integer?

Is this a valid date format?

Is this a UUID?

Does this value contain the expected number of characters?

Does this JSON match the expected schema?
```

Example:

```text
Expected:

YYYY-MM-DD
```

Valid:

```text
2026-08-28
```

Invalid:

```text
hello
```

---

# Semantic Validation

Semantic validation determines whether a syntactically valid value makes sense in the application's context.

Example:

```text
startDate=2026-09-20
endDate=2026-09-10
```

Both values may be valid dates.

But:

```text
startDate > endDate
```

may violate the application's business rules.

Another example:

```text
quantity=-10
```

may be syntactically valid as an integer but semantically invalid for a normal purchase.

---

# Validation Model

A useful model is:

```text
Input
  |
  v
Type Validation
  |
  v
Format Validation
  |
  v
Length Validation
  |
  v
Range Validation
  |
  v
Structural Validation
  |
  v
Semantic Validation
  |
  v
Business Rule Validation
  |
  v
Accepted
```

Not every field requires every layer.

Validation should reflect the field's actual purpose.

---

# Trust Boundaries

Validation should occur when data crosses a trust boundary.

Example:

```text
Browser
   |
   | Trust Boundary
   v
Web Application
```

But this is not the only boundary.

Consider:

```text
Third Party
    |
    | Trust Boundary
    v
Webhook
    |
    v
Application
```

or:

```text
Application A
      |
      | Trust Boundary
      v
Application B
```

Do not assume backend data is inherently trusted.

A compromised upstream service may send malformed or malicious input.

---

# Sources of Untrusted Input

Potentially untrusted input includes:

```text
Query parameters
POST parameters
JSON
XML
Cookies
Headers
Path parameters
Uploaded files
Filenames
Multipart metadata
WebSocket messages
GraphQL variables
gRPC messages
Webhook bodies
Email
CSV files
Excel files
Imported documents
Third-party APIs
Partner feeds
Backend integrations
Database content originally supplied by users
```

A useful rule is:

```text
If the application did not generate and fully control
the value itself, consider whether it crosses a trust boundary.
```

---

# Client-Side Validation

Applications frequently perform validation in JavaScript.

Example:

```javascript
if (age < 18) {
    alert("You must be at least 18");
    return;
}
```

This may improve user experience.

It is not a security boundary.

An attacker can bypass client-side validation using:

```text
Burp Suite
curl
Custom scripts
Browser DevTools
Direct API requests
Modified JavaScript
```

Conceptually:

```text
Browser Validation
      |
      X
      |
      v
Direct HTTP Request
      |
      v
Server
```

Therefore:

```text
Client-side validation
        +
Server-side validation
```

is appropriate.

For security:

```text
Server-side validation is mandatory.
```

---

# Hidden Fields Are Still User-Controlled

Example:

```html
<input type="hidden" name="price" value="100">
```

An attacker can modify:

```text
price=100
```

to:

```text
price=1
```

using Burp Repeater.

Hidden HTML fields must therefore be treated as attacker-controlled.

---

# Disabled Fields Are Still User-Controlled

Example:

```html
<input name="role" value="user" disabled>
```

The browser may prevent normal editing.

An attacker can still submit:

```text
role=admin
```

directly.

The server must independently enforce allowed values and authorisation.

---

# Dropdown Lists Are User-Controlled

Example:

```html
<select name="country">
    <option value="NL">Netherlands</option>
    <option value="GB">United Kingdom</option>
</select>
```

An attacker can submit:

```text
country=XYZ
```

even though the browser never offered that option.

The server should verify that the submitted value belongs to the allowed set.

---

# Radio Buttons and Checkboxes

The same rule applies to:

```text
Radio buttons
Checkboxes
Select elements
Hidden fields
Read-only fields
Disabled fields
```

The client interface does not define the server's security boundary.

---

# Allowlisting

OWASP recommends defining what input is permitted rather than attempting to identify every possible malicious value.

Conceptually:

```text
Expected Input
      |
      v
Matches Allowed Rules?
      |
   +--+--+
   |     |
  Yes    No
   |     |
   v     v
Accept Reject
```

Example:

```text
accountType
```

Allowed values:

```text
personal
business
```

Anything else:

```text
Reject
```

---

# Denylisting

Denylisting attempts to identify forbidden input.

Example:

```text
Reject:
<script>
'
"
../
;
```

The problem is that attackers can often represent malicious input differently.

Conceptually:

```text
Known Bad Patterns
      |
      v
Block
```

but:

```text
Unknown Variant
      |
      v
Potential Bypass
```

Denylisting may be useful as an additional layer or detection mechanism.

It should generally not be the primary validation strategy.

---

# Example: Weak Denylist

Suppose an application blocks:

```text
<script>
```

That does not mean the application is protected against XSS.

There are many other HTML and JavaScript execution contexts.

The correct control depends on where the data is ultimately used.

---

# Example: Apostrophe Filtering

Blocking:

```text
'
```

may appear to reduce SQL injection attempts.

However, legitimate names may contain apostrophes.

Example:

```text
O'Brien
```

More importantly:

```text
Blocking apostrophes
```

is not a replacement for:

```text
Parameterized SQL queries
```

---

# Type Validation

Type validation verifies that data has the expected type.

Example:

```text
Expected:
Integer

Input:
123
```

Accept.

Input:

```text
abc
```

Reject.

---

# Type Confusion Testing

Applications sometimes accept unexpected data types.

Expected:

```json
{
  "id": 123
}
```

Test controlled alternatives such as:

```json
{
  "id": "123"
}
```

```json
{
  "id": null
}
```

```json
{
  "id": true
}
```

```json
{
  "id": []
}
```

```json
{
  "id": {}
}
```

Observe whether:

```text
Validation rejects the request

Parser coerces the value

Application throws an error

Business logic changes

Unexpected code path executes
```

---

# Integer Validation

Example expected value:

```text
quantity=5
```

Useful boundary tests:

```text
0
1
-1
999999999
2147483647
2147483648
```

The exact values should reflect the application's expected data type and business rules.

---

# Floating-Point Values

Where decimal values are accepted, test:

```text
0
0.0
-0.1
1.5
999999999.99
```

Also consider whether the application handles:

```text
Rounding
Precision
Currency
Scientific notation
```

appropriately.

Avoid assuming floating-point behaviour is a vulnerability without demonstrating security or business impact.

---

# Boolean Values

An application may expect:

```json
{
  "enabled": true
}
```

Test whether it unexpectedly accepts:

```json
{
  "enabled": "true"
}
```

or:

```json
{
  "enabled": 1
}
```

or:

```json
{
  "enabled": "yes"
}
```

Unexpected coercion may matter if the field controls a sensitive operation.

---

# Null Values

Test whether:

```json
{
  "email": null
}
```

is handled differently from:

```json
{
  "email": ""
}
```

and from the field being completely absent.

These three states may have different meanings:

```text
Missing
Empty
Null
```

---

# Missing Parameters

Given:

```json
{
  "username": "alice",
  "email": "alice@example.com"
}
```

remove:

```text
email
```

and observe the result.

Possible outcomes:

```text
Rejected correctly
Default value applied
Old value retained
Null stored
Unexpected error
Security check skipped
```

---

# Empty Values

Test:

```text
parameter=
```

and:

```json
{
  "parameter": ""
}
```

An application should define whether empty input is valid.

---

# Whitespace

Whitespace can reveal inconsistent validation.

Controlled tests include:

```text
"alice"
" alice"
"alice "
" alice "
" "
```

Also consider:

```text
Tabs
Newlines
Carriage returns
```

when relevant to the field and parser.

---

# Length Validation

Every field should have reasonable size limits based on its purpose.

Example:

```text
Username:

Minimum: 3
Maximum: 50
```

Testing:

```text
2 characters
3 characters
50 characters
51 characters
```

This is boundary-value testing.

---

# Why Length Limits Matter

Length restrictions can help reduce:

```text
Unexpected parser behaviour
Database truncation
Resource consumption
UI problems
Log abuse
Downstream processing issues
```

Do not submit extremely large values to production systems without explicit authorisation.

---

# Boundary Value Testing

If the accepted range is:

```text
1 - 100
```

test:

```text
0
1
2
99
100
101
```

This pattern is useful because validation errors often occur at boundaries.

---

# Range Validation

Example:

```text
discountPercentage
```

Expected:

```text
0 - 100
```

Test:

```text
-1
0
1
99
100
101
```

If:

```text
discountPercentage=100000
```

is accepted, determine whether it produces actual business impact before reporting it as a vulnerability.

---

# Enumeration Validation

For small fixed sets, require an exact allowed value.

Example:

```text
status
```

Allowed:

```text
pending
approved
rejected
```

Reject:

```text
admin
unknown
test
123
```

---

# Regular Expressions

Regular expressions can be useful for structured fields.

Example:

```regex
^[a-z0-9]{3,20}$
```

This defines:

```text
Lowercase letters
Digits
Length 3 - 20
Entire input must match
```

---

# Anchor the Entire Input

A common mistake is validating only part of a value.

Prefer patterns that validate the complete expected value.

Conceptually:

```text
^
expected structure
$
```

rather than searching for a valid substring inside arbitrary input.

---

# Regex Is Not Always the Right Tool

Do not use complex regex when a dedicated parser or framework validator exists.

Examples:

```text
URLs
Email addresses
IP addresses
Dates
JSON
XML
UUIDs
```

Dedicated parsers are often safer and easier to maintain.

---

# ReDoS

Poorly designed regular expressions can create Regular Expression Denial of Service.

Conceptually:

```text
Attacker Input
     |
     v
Pathological Regex
     |
     v
Excessive Backtracking
     |
     v
CPU Consumption
```

Be cautious with:

```text
Nested quantifiers
Ambiguous repetition
Unbounded patterns
```

especially on attacker-controlled strings.

---

# Unicode

Input validation must account for Unicode when international input is supported.

Consider:

```text
Different scripts
Equivalent characters
Combining characters
Normalisation
Case conversion
Look-alike characters
```

Do not unnecessarily restrict legitimate international names to:

```text
A-Z
a-z
```

unless the application's actual requirements justify it.

---

# Unicode Normalisation

Equivalent text may have multiple Unicode representations.

A robust design may use:

```text
Input
  |
  v
Unicode Normalisation
  |
  v
Validation
```

The exact normalisation strategy depends on the field.

Do not blindly normalise security-sensitive identifiers without understanding the consequences.

---

# Canonicalisation

Canonicalisation converts multiple representations into a consistent representation.

This is particularly important for:

```text
Paths
URLs
Hostnames
Unicode
Encoded input
```

Example:

```text
%2e%2e%2f
```

may decode to:

```text
../
```

Validation must occur at the correct stage of decoding and canonicalisation.

---

# Double Encoding

Input may be encoded more than once.

Example conceptually:

```text
Original Character
      |
      v
Encoded
      |
      v
Encoded Again
```

If different components decode different numbers of times, validation may be bypassed.

Testing should compare:

```text
Raw value
Single encoded value
Double encoded value
```

only with safe canaries unless exploit-specific testing is authorised.

---

# URL Encoding

Example safe canary:

```text
TEST VALUE
```

URL encoded:

```text
TEST%20VALUE
```

Observe whether:

```text
Proxy
Web server
Framework
Application
```

interpret the value consistently.

---

# Path Validation

File and path inputs deserve special care.

Example:

```text
filename=report.pdf
```

Applications should avoid trusting arbitrary user-controlled filesystem paths.

Where a filename is expected, validation should generally reflect:

```text
Expected file name
Expected extension
Expected location
```

rather than allowing arbitrary path syntax.

Refer to:

```text
docs/web/path-traversal.md
docs/web/file-inclusion.md
docs/web/file-upload.md
```

---

# Filename Validation

A filename may contain:

```text
Path separators
Unicode
Control characters
Multiple extensions
Very long values
Reserved names
```

Applications should:

```text
Generate server-side storage names where possible
Restrict allowed extensions
Validate actual content
Avoid using raw filenames as filesystem paths
Store outside executable web roots where appropriate
```

---

# Email Address Validation

Email addresses are more complex than they appear.

Avoid attempting to implement the entire email specification using a simplistic custom regular expression.

A practical design often includes:

```text
Basic syntax validation
Reasonable length limits
Mail-library parsing
Verification email
Business-specific restrictions where necessary
```

Semantic validation may involve confirming control of the address.

Example:

```text
User enters email
      |
      v
Syntax validation
      |
      v
Verification token sent
      |
      v
User proves mailbox control
```

---

# URL Validation

URL validation is security-sensitive because URLs may later be used for:

```text
Redirects
Webhooks
Image fetching
Document fetching
OAuth callbacks
Server-side requests
```

Validation should account for:

```text
Scheme
Hostname
Port
Path
Userinfo
Redirect behaviour
DNS resolution where relevant
```

If the server makes requests to user-supplied URLs, refer to:

[Server Side Request Forgery](ssrf.md)

If the browser is redirected to user-controlled URLs, refer to:

[Open Redirect](open-redirect.md)

---

# UUID Validation

Expected:

```text
550e8400-e29b-41d4-a716-446655440000
```

Use a UUID parser where possible rather than relying solely on custom string matching.

Also remember:

```text
Valid UUID
```

does not mean:

```text
Authorised object
```

A valid identifier still requires object-level authorisation.

---

# Date Validation

Date validation should consider:

```text
Format
Calendar validity
Range
Timezone
Business rules
Ordering
```

Example:

```text
2026-02-30
```

may match:

```text
YYYY-MM-DD
```

syntactically but is not a valid calendar date.

Use a date parser.

---

# Date Semantic Validation

Example:

```text
startDate=2026-10-10
endDate=2026-10-01
```

Both dates are individually valid.

Together they may violate:

```text
startDate <= endDate
```

---

# JSON Validation

APIs commonly receive JSON.

Example:

```json
{
  "username": "alice",
  "age": 30
}
```

Validation should consider:

```text
Required properties
Allowed properties
Data types
String lengths
Number ranges
Nested structures
Array lengths
Enumerations
Nullability
```

---

# JSON Schema

JSON Schema can define expected request structure.

Conceptually:

```text
JSON Request
     |
     v
Schema Validation
     |
   +--+--+
   |     |
Valid  Invalid
```

However:

```text
Schema validation
```

does not replace:

```text
Authorisation
Business logic validation
Injection-safe APIs
Output encoding
```

---

# Unexpected JSON Properties

Expected:

```json
{
  "displayName": "Alice"
}
```

Test a harmless unexpected property:

```json
{
  "displayName": "Alice",
  "security_test": "canary"
}
```

Observe whether it is:

```text
Rejected
Ignored
Stored
Returned
Passed downstream
```

This can help identify:

```text
Over-posting
Mass assignment
Loose schema validation
```

---

# Duplicate JSON Keys

Parsers may disagree about duplicate keys.

Example:

```json
{
  "role": "user",
  "role": "admin"
}
```

Different components may interpret:

```text
First value
Last value
Error
Both values
```

This can become security-relevant when different layers parse the same request differently.

Use benign duplicate values first when testing parser behaviour.

---

# Arrays

Expected:

```json
{
  "items": [1, 2, 3]
}
```

Test:

```text
Empty array
One item
Maximum expected items
One above maximum
Unexpected data types
Nested arrays
```

Avoid very large arrays on production systems without explicit permission.

---

# Nested Objects

Example:

```json
{
  "user": {
    "name": "Alice"
  }
}
```

Test whether unexpected nested properties are accepted:

```json
{
  "user": {
    "name": "Alice",
    "security_test": "canary"
  }
}
```

This may expose differences between:

```text
API schema
Object mapper
Business object
Database model
```

---

# XML Validation

XML inputs may be validated using an XML Schema where appropriate.

Validation may cover:

```text
Allowed elements
Required elements
Data types
Element order
Attributes
Namespaces
Cardinality
```

XML security also requires secure parser configuration.

Schema validation alone does not prevent:

```text
XXE
```

Refer to:

[XML External Entity Injection](xxe.md)

---

# Content-Type Validation

Applications should define which content types each endpoint accepts.

Example:

```http
Content-Type: application/json
```

Test whether the endpoint unexpectedly accepts:

```text
application/xml
application/x-www-form-urlencoded
multipart/form-data
text/plain
```

Unexpected parser support may expose additional attack surface.

---

# Burp Content Type Converter

A useful Burp extension for this type of testing is:

```text
Content Type Converter
```

It can convert request bodies between formats such as:

```text
JSON -> XML
XML -> JSON
Form parameters -> JSON
Form parameters -> XML
```

This can help determine whether an endpoint unexpectedly accepts another parser format.

BApp Store:

```text
https://portswigger.net/bappstore/db57ecbe2cb7446292a94aa6181c9278
```

The extension is old, so review its source and compatibility before using it on an engagement.

---

# HTTP Parameter Pollution

Applications may interpret duplicate parameters differently.

Example:

```http
GET /search?id=1&id=2 HTTP/1.1
```

Possible interpretations include:

```text
First value
Last value
Both values
Array
Concatenated value
```

Differences between:

```text
CDN
WAF
Reverse proxy
Web server
Framework
Application
```

can create security-relevant inconsistencies.

---

# Safe HPP Testing

Start with harmless values:

```text
test=one&test=two
```

Compare the response with:

```text
test=one
```

and:

```text
test=two
```

Determine which value the application uses.

---

# HTTP Headers as Input

Headers should also be considered untrusted.

Examples:

```text
Host
Origin
Referer
User-Agent
X-Forwarded-For
X-Forwarded-Host
X-Original-URL
Accept-Language
Content-Type
Authorization
```

The exact headers that matter depend on the application's architecture.

---

# Host Header

The `Host` header is attacker-controlled in many deployment scenarios.

Do not assume:

```text
Host
```

is inherently trustworthy.

Refer to:

[HTTP Host Header Attacks](host-header-attacks.md)

---

# Proxy Headers

Applications behind proxies may process:

```text
X-Forwarded-For
X-Forwarded-Host
X-Forwarded-Proto
Forwarded
```

These headers should only be trusted when they come from appropriately trusted infrastructure and are handled according to the deployment architecture.

---

# Cookies as Input

Cookies are also attacker-controlled.

Example:

```http
Cookie: language=en; theme=dark
```

Test whether unexpected values affect:

```text
Application state
Roles
Tenant selection
Pricing
Feature flags
Authentication
```

Never trust a cookie merely because the application originally issued it.

---

# File Upload Validation

File upload validation requires multiple controls.

A simplified model:

```text
Uploaded File
     |
     v
Size Check
     |
     v
Extension Check
     |
     v
Content-Type Check
     |
     v
Content / Signature Validation
     |
     v
Safe Storage
     |
     v
Safe Processing
```

No single check is sufficient.

Refer to:

[File Upload Security](file-upload.md)

---

# MIME Type

Example:

```http
Content-Type: image/jpeg
```

is supplied by the client and should not be trusted as proof that the content is actually JPEG data.

Server-side content validation may be required.

---

# File Extension

Checking:

```text
.jpg
```

alone does not prove that the file contains an image.

Likewise:

```text
Content-Type: image/jpeg
```

alone does not prove the content matches the claimed format.

Validation should consider the application's actual security requirements.

---

# File Signature

Many file types have characteristic binary signatures.

Where appropriate, applications may verify:

```text
Extension
MIME type
File signature
Actual parser behaviour
```

These checks should be combined rather than relied upon individually.

---

# File Size

Enforce reasonable upload limits.

Test boundaries such as:

```text
Maximum - 1 byte
Maximum
Maximum + 1 byte
```

Do not intentionally upload very large files to production environments unless explicitly authorised.

---

# CSV Input

CSV imports can contain:

```text
Unexpected columns
Missing columns
Very long fields
Formula-like values
Different delimiters
Quoted values
Newlines
Encoding differences
```

Validation should reflect the expected schema.

If exported CSV is opened by spreadsheet software, also consider spreadsheet formula injection.

---

# XML Input

XML can contain:

```text
Unexpected elements
Unexpected attributes
Deep nesting
Namespaces
External entity declarations
```

Validation and parser hardening are separate controls.

---

# GraphQL Input

GraphQL provides strong typing at the schema level, but application-level semantic validation remains necessary.

Example:

```graphql
mutation {
  updateProfile(age: -100)
}
```

The value may satisfy:

```text
Int
```

while violating the business rule.

Refer to:

[GraphQL API Security](graphql.md)

---

# gRPC Input

Protocol Buffers provide structured types, but they do not automatically enforce all application rules.

Example:

```text
quantity: -100
```

may still be a valid integer field.

Applications must enforce:

```text
Ranges
Business rules
Authorisation
State transitions
```

Refer to:

[gRPC Security](grpc-security.md)

---

# WebSocket Input

WebSocket messages must be validated just like normal HTTP requests.

Example:

```json
{
  "action": "sendMessage",
  "recipient": "123",
  "message": "hello"
}
```

Validate:

```text
Action
Object identifier
Message length
Message type
Authorisation
Business rules
```

Refer to:

[WebSocket Security](websockets.md)

---

# Webhook Validation

Webhooks originate outside the application trust boundary.

Validate:

```text
Authentication / signature
Message structure
Required fields
Data types
Allowed values
Replay controls
Business rules
```

Do not assume a request is trusted merely because it reaches a dedicated webhook endpoint.

---

# Business Logic Validation

Some of the most important validation cannot be expressed using a regular expression.

Example:

```text
Account balance:
100

Requested transfer:
500
```

The value:

```text
500
```

is a perfectly valid integer.

But the operation may be invalid.

---

# Price Validation

Avoid trusting client-supplied authoritative pricing.

Example:

```http
price=100
```

An attacker may submit:

```http
price=1
```

A safer design is:

```text
Product ID
    |
    v
Server retrieves authoritative price
    |
    v
Calculation
```

rather than:

```text
Client tells server the authoritative price
```

---

# Quantity Validation

Potential tests include:

```text
0
1
-1
Maximum expected
Maximum + 1
Very large positive value
```

Observe:

```text
Cart total
Stock
Discount logic
Shipping
Refund behaviour
```

---

# Currency Validation

Where currency is supplied:

```text
EUR
USD
GBP
```

the server should verify that:

```text
Currency is supported
Currency is valid for the transaction
Price is calculated consistently
```

Do not trust a client-controlled currency field to determine authoritative pricing.

---

# State Validation

Applications should enforce valid state transitions.

Example:

```text
CREATED
   |
   v
PAID
   |
   v
SHIPPED
```

Test whether requests can move directly:

```text
CREATED
   |
   v
SHIPPED
```

if that transition should be impossible.

---

# Cross-Field Validation

Fields may be valid individually but invalid together.

Example:

```text
country=NL
postalCode=90210
```

Each string may be syntactically valid.

The combination may not be semantically valid.

---

# Role-Dependent Validation

Allowed values may depend on the user's role.

Example:

```text
Normal User:

status=
draft
```

Administrator:

```text
status=
draft
approved
rejected
```

The server must enforce role-specific rules.

---

# Tenant-Dependent Validation

In multi-tenant systems:

```text
tenant_id
project_id
account_id
```

must be validated not only for format but also for ownership and authorisation.

Example:

```text
Valid UUID
      |
      v
Does object exist?
      |
      v
Does it belong to this tenant?
      |
      v
Is this user authorised?
```

---

# Validation and Authorisation

These are different controls.

Example:

```text
user_id=123
```

may be:

```text
Valid integer
```

but the current user may not be authorised to access user 123.

Therefore:

```text
Input Validation
      +
Object-Level Authorisation
```

are both required.

Refer to:

```text
docs/web/idor-bola.md
docs/web/authorisation.md
```

---

# Validation and Mass Assignment

An API may accept unexpected properties.

Expected:

```json
{
  "name": "Alice"
}
```

Attacker sends:

```json
{
  "name": "Alice",
  "role": "admin"
}
```

The problem may not simply be weak input validation.

It may involve:

```text
Automatic object binding
Missing property allowlist
Missing authorisation
```

Refer to:

[Mass Assignment](mass-assignment.md)

---

# Validation and SQL Injection

Input validation may reduce attack opportunities, but SQL injection should primarily be prevented through parameterisation.

Correct conceptual model:

```text
Untrusted Input
      |
      v
Validation
      |
      v
Parameterized Query
      |
      v
Database
```

not:

```text
Input
  |
  v
Remove apostrophes
  |
  v
String concatenation
```

Refer to:

[SQL Injection](sql-injection.md)

---

# Validation and NoSQL Injection

The same principle applies to NoSQL.

Do not rely solely on blocking characters.

Enforce:

```text
Expected types
Expected object structure
Allowed operators
Safe query APIs
```

Refer to:

[NoSQL Injection](nosql-injection.md)

---

# Validation and LDAP Injection

LDAP input should be safely handled for the relevant LDAP context.

Validation can reduce unexpected input but should not replace correct LDAP escaping and safe query construction.

Refer to:

[LDAP Injection](ldap-injection.md)

---

# Validation and Command Injection

Where user-controlled input reaches operating-system commands, avoid shell execution where possible.

Prefer:

```text
Safe library API
```

over:

```text
Shell command
```

Where commands are unavoidable:

```text
Separate command from arguments
Use appropriate APIs
Strictly allowlist expected arguments
```

Refer to:

[OS Command Injection](command-injection.md)

---

# Validation and SSTI

Input validation is not a reliable primary defence if untrusted input is inserted into template source.

Use the template engine correctly so that:

```text
User input = data
```

rather than:

```text
User input = template code
```

Refer to:

[Server-Side Template Injection](ssti.md)

---

# Validation and XSS

Do not treat input validation as the primary XSS control.

Example:

```text
Comment field
```

may legitimately need:

```text
Unicode
Punctuation
URLs
```

Trying to block every "dangerous" character often fails.

Use:

```text
Context-aware output encoding
Safe DOM APIs
Sanitisation when HTML is intentionally allowed
```

Refer to:

[Cross-Site Scripting](xss.md)

---

# Validation and SSRF

If an application accepts URLs:

```text
url=
callback=
webhook=
image=
```

strict URL validation can reduce risk.

But SSRF protection may additionally require:

```text
Destination allowlists
DNS/IP validation
Network egress controls
Redirect handling
Protocol restrictions
```

Refer to:

[Server Side Request Forgery](ssrf.md)

---

# Validation and Path Traversal

If a user selects a file:

```text
file=report.pdf
```

prefer mapping an identifier to a server-side file rather than accepting arbitrary paths.

Example:

```text
document_id=123
```

Server:

```text
123 -> /safe/storage/report.pdf
```

Refer to:

[Path Traversal](path-traversal.md)

---

# Validation and Open Redirects

For redirect destinations, prefer:

```text
Server-side destination identifiers
```

Example:

```text
next=dashboard
```

mapped internally to:

```text
/dashboard
```

rather than accepting arbitrary URLs.

Refer to:

[Open Redirect](open-redirect.md)

---

# Validation and HTTP Headers

If an application generates:

```text
Location
Content-Disposition
Set-Cookie
Custom headers
```

from user input, validate the input and use safe framework APIs.

Avoid constructing raw HTTP headers from untrusted strings.

---

# Validation Errors

Validation failures should produce controlled responses.

Example:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Invalid request"
}
```

Avoid exposing:

```text
Stack traces
Filesystem paths
Database errors
Framework internals
Source code
```

---

# Error Consistency

Different validation responses may reveal useful application information.

Example:

```text
User does not exist
```

versus:

```text
Incorrect password
```

may enable account enumeration.

Validation error design should consider information disclosure.

---

# Fail Closed

Where validation cannot confidently determine that input is acceptable:

```text
Reject
```

rather than:

```text
Process anyway
```

Conceptually:

```text
Unknown / Invalid
       |
       v
Reject
```

---

# Server-Side Validation Workflow

A robust pattern is:

```text
Receive Request
      |
      v
Parse According to Expected Content Type
      |
      v
Validate Structure
      |
      v
Validate Types
      |
      v
Validate Length / Range
      |
      v
Validate Allowed Values
      |
      v
Validate Business Rules
      |
      v
Authorisation
      |
      v
Perform Operation Using Safe APIs
```

The exact order may vary depending on application architecture.

---

# Burp Suite Workflow

Burp Suite is particularly useful for identifying validation that exists only in the client.

A practical workflow is:

```text
1. Use the application normally

2. Capture the request in Proxy

3. Send the request to Repeater

4. Establish the normal response

5. Modify one input at a time

6. Test type

7. Test length

8. Test range

9. Test allowed values

10. Test missing / empty / null

11. Test encoding

12. Test duplicate parameters

13. Test alternate content types

14. Test business rules

15. Compare responses

16. Verify security impact
```

---

# Establish a Baseline

Always start with a known-valid request.

Example:

```http
POST /api/profile HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "displayName": "Alice",
  "age": 30
}
```

Record:

```text
Status code
Response length
Response body
Headers
Timing
State change
```

Then modify one field.

---

# One Variable at a Time

Prefer:

```text
Baseline
    |
    v
Change one field
    |
    v
Compare
```

instead of changing ten fields simultaneously.

This makes it easier to understand which input caused the behaviour.

---

# Burp Repeater

Repeater is the primary manual tool for validation testing.

Useful tests include:

```text
Change value
Remove value
Duplicate value
Change type
Change content type
Change encoding
Change length
Change range
Add unexpected property
```

---

# Burp Comparer

Comparer can help identify subtle differences between:

```text
Valid response
Invalid response
Boundary response
```

This is useful when the visible UI does not clearly show the difference.

---

# Burp Intruder

Intruder can assist with controlled boundary testing.

For example:

```text
quantity=§VALUE§
```

Payloads:

```text
-1
0
1
99
100
101
```

Use conservative payload sets and appropriate rate limits.

---

# Intruder for Enumerations

For:

```text
accountType=§VALUE§
```

test a small controlled set:

```text
personal
business
admin
test
null
```

The goal is to identify accepted values and unexpected behaviour, not to flood the endpoint.

---

# Burp Match and Replace

Match and Replace can be useful when repeatedly modifying:

```text
Headers
Cookies
Parameters
```

during manual browsing.

Be careful not to unintentionally modify unrelated requests.

---

# Burp Decoder

Decoder can help analyse:

```text
URL encoding
Base64
Hex
HTML entities
```

This is useful when determining whether validation occurs:

```text
Before decoding
```

or:

```text
After decoding
```

---

# Burp Logger

Logger can help inspect traffic generated by Burp and extensions and can be useful when understanding request transformations.

---

# Content Type Converter

Relevant BApp:

```text
Content Type Converter
```

Official BApp Store page:

```text
https://portswigger.net/bappstore/db57ecbe2cb7446292a94aa6181c9278
```

Useful for testing whether an endpoint that normally expects:

```text
JSON
```

also accepts:

```text
XML
Form data
```

This can reveal additional parser attack surface.

Review third-party extension code and compatibility before installation.

---

# Param Miner

Another useful extension in broader input-surface discovery is:

```text
Param Miner
```

It can help identify hidden:

```text
Parameters
Headers
Cookies
```

that may influence application behaviour.

Official BApp Store page:

```text
https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943
```

Discovered parameters should then be manually tested for validation and security impact.

---

# BApp Security

Burp extensions are third-party software.

Before installing an extension:

```text
Review source
Check maintenance status
Understand network behaviour
Understand data handling
Confirm compatibility
```

This is particularly important when testing sensitive client environments.

---

# curl Testing

Simple validation tests can also be performed using `curl`.

Baseline:

```bash
curl -i \
  -X POST \
  -H 'Content-Type: application/json' \
  --data '{"age":30}' \
  https://target.example/api/profile
```

Boundary:

```bash
curl -i \
  -X POST \
  -H 'Content-Type: application/json' \
  --data '{"age":-1}' \
  https://target.example/api/profile
```

Use only against authorised targets.

---

# Simple Validation Test Script

For controlled numeric boundary testing:

```python
#!/usr/bin/env python3

import requests

url = "https://target.example/api/profile"

values = [
    -1,
    0,
    1,
    17,
    18,
    19,
    100,
    101
]

for value in values:
    response = requests.post(
        url,
        json={"age": value},
        timeout=10
    )

    print(
        f"value={value!r} "
        f"status={response.status_code} "
        f"length={len(response.content)}"
    )
```

Do not blindly run automation against production systems.

Configure:

```text
Authentication
Rate
Target
Payloads
```

for the authorised engagement.

---

# Generic String Boundary Generator

A small local helper:

```python
#!/usr/bin/env python3

lengths = [
    0,
    1,
    2,
    10,
    49,
    50,
    51,
    100,
    255,
    256
]

for length in lengths:
    value = "A" * length

    print(
        f"length={length} "
        f"value={value}"
    )
```

Save as:

```text
string_boundaries.py
```

Run:

```bash
python3 string_boundaries.py
```

This generates controlled test values without automatically sending requests.

---

# Generic Numeric Boundary Generator

```python
#!/usr/bin/env python3

minimum = 1
maximum = 100

values = sorted({
    minimum - 1,
    minimum,
    minimum + 1,
    maximum - 1,
    maximum,
    maximum + 1
})

for value in values:
    print(value)
```

Output:

```text
0
1
2
99
100
101
```

---

# Validation Test Matrix

For each parameter consider:

| Test | Example |
|---|---|
| Valid | `10` |
| Missing | parameter removed |
| Empty | `""` |
| Null | `null` |
| Wrong type | `"ten"` |
| Minimum - 1 | `0` |
| Minimum | `1` |
| Maximum | `100` |
| Maximum + 1 | `101` |
| Unexpected enum | `admin` |
| Leading whitespace | `" test"` |
| Trailing whitespace | `"test "` |
| Duplicate | `id=1&id=2` |
| Encoded | `%74%65%73%74` |
| Unexpected property | `security_test=canary` |

Not every test applies to every parameter.

---

# Input Classification

Before testing, classify each input.

Example:

```text
Parameter:
quantity

Type:
Integer

Expected range:
1 - 100

Required:
Yes

Source:
JSON body

Business meaning:
Number of items ordered

Security relevance:
Price / inventory calculation
```

This produces much better testing than random fuzzing.

---

# Input Inventory

A useful table:

| Input | Location | Type | Required | Rules | Security Relevance |
|---|---|---|---|---|---|
| `username` | JSON | String | Yes | 3-50 chars | Authentication |
| `quantity` | JSON | Integer | Yes | 1-100 | Pricing |
| `role` | JSON | Enum | No | user/admin | Authorisation |
| `redirect` | Query | URL/path | No | Internal path | Redirect |
| `file` | Multipart | File | Yes | PDF only | File processing |

---

# Prioritise Security-Sensitive Inputs

High-value fields include:

```text
role
admin
isAdmin
price
amount
quantity
discount
status
state
user_id
account_id
tenant_id
owner
filename
path
url
redirect
callback
webhook
template
command
query
filter
sort
```

The field name alone does not prove vulnerability.

It helps prioritise manual review.

---

# Validation Decision Tree

```text
                 INPUT RECEIVED
                       |
                       v
                Is it required?
                  /         \
                No           Yes
                |             |
                v             v
        Missing allowed?   Is it present?
                              |
                              v
                      Correct data type?
                         /         \
                       No           Yes
                       |             |
                       v             v
                    Reject      Correct format?
                                   /      \
                                 No        Yes
                                 |          |
                                 v          v
                              Reject    Length valid?
                                           |
                                           v
                                      Range valid?
                                           |
                                           v
                                    Allowed value?
                                           |
                                           v
                                   Semantic rules?
                                           |
                                           v
                                    Business rules?
                                           |
                                           v
                                     Authorised?
                                           |
                                           v
                                         Accept
```

---

# Black-Box Testing Methodology

A structured black-box process is:

```text
Map Inputs
    |
    v
Understand Expected Values
    |
    v
Capture Valid Baseline
    |
    v
Test Missing / Empty / Null
    |
    v
Test Type
    |
    v
Test Length
    |
    v
Test Range
    |
    v
Test Enumeration
    |
    v
Test Encoding
    |
    v
Test Duplicate Inputs
    |
    v
Test Alternate Content Types
    |
    v
Test Semantic Rules
    |
    v
Test Business Rules
    |
    v
Assess Security Impact
```

---

# White-Box Testing

With source access, identify validation at:

```text
Routes
Controllers
Request models
DTOs
Schemas
Serialisers
Service layer
Domain layer
Database layer
```

Search for:

```text
Validators
Regular expressions
Schema definitions
Type conversions
Range checks
Length checks
Enum checks
Business rules
```

---

# Validation Placement

A common architecture:

```text
HTTP Request
     |
     v
Controller
     |
     v
Request Schema
     |
     v
Service
     |
     v
Domain Logic
     |
     v
Repository
```

Different validation belongs at different layers.

For example:

```text
Request schema:
Is age an integer?

Domain logic:
Is this age allowed for this operation?
```

---

# Avoid Validation Duplication

Duplicated validation logic can drift.

Example:

```text
Web UI:
Maximum 100

API:
Maximum 1000

Mobile API:
No maximum
```

Centralising business rules where appropriate reduces inconsistency.

---

# Framework Validation

Use framework-supported validation where appropriate.

Examples include:

```text
Typed request models
Schema validators
DTO validation
Form validators
JSON Schema
XML Schema
```

Avoid reinventing common validation mechanisms unnecessarily.

---

# Database Constraints

Database constraints can provide an additional layer.

Examples:

```text
NOT NULL
UNIQUE
CHECK
FOREIGN KEY
Data type constraints
```

However:

```text
Database constraint
```

does not replace:

```text
Application validation
```

The application should reject invalid requests cleanly before they become database errors.

---

# Validation at Multiple Layers

A defence-in-depth model:

```text
Client Validation
       |
       v
API Schema Validation
       |
       v
Business Validation
       |
       v
Authorisation
       |
       v
Database Constraints
```

Each layer serves a different purpose.

---

# API Gateway Validation

API gateways may enforce:

```text
Request size
Schema
Content type
Rate limits
Authentication
```

But backend services should not blindly assume that all requests always passed through the gateway.

Architecture matters.

---

# Parser Differential Testing

Security issues can occur when components interpret the same input differently.

Example:

```text
Request
   |
   v
WAF
   |
   v
Reverse Proxy
   |
   v
Framework
   |
   v
Application
```

Potential differences include:

```text
Duplicate parameters
Encoding
Content length
Transfer encoding
JSON duplicate keys
URL paths
Unicode
```

This concept also appears in vulnerabilities such as HTTP request smuggling.

---

# Validation Bypass Through Alternate Endpoints

An application may validate:

```text
POST /profile
```

but not:

```text
PATCH /api/profile
```

Always identify all interfaces that modify the same object.

Example:

```text
Web UI
REST API
GraphQL
Mobile API
Legacy API
```

---

# Validation Bypass Through Alternate Methods

Example:

```text
POST /user
```

may validate input differently from:

```text
PUT /user
PATCH /user
```

Do not assume validation is consistent across methods.

---

# Validation Bypass Through API Versions

Example:

```text
/api/v1/profile
/api/v2/profile
```

A security control may exist only in the newer version.

Legacy APIs deserve explicit testing.

---

# Validation Bypass Through Case Differences

Where values are case-insensitive, test:

```text
user
USER
User
uSeR
```

The application should handle case according to a clearly defined rule.

---

# Validation Bypass Through Whitespace

Test controlled variants:

```text
admin
 admin
admin 
 admin 
```

particularly when different layers may trim input differently.

---

# Validation Bypass Through Encoding

Conceptually test:

```text
Raw
URL encoded
Unicode representation
Double encoded
```

when relevant.

Do not assume a successful bypass is exploitable until downstream security impact is demonstrated.

---

# Validation Bypass Through Nested Data

Expected:

```json
{
  "name": "Alice"
}
```

Alternative structures:

```json
{
  "name": {
    "value": "Alice"
  }
}
```

or:

```json
{
  "name": ["Alice"]
}
```

should normally be rejected if the schema expects a string.

---

# Validation Bypass Through Parameter Location

A value may be accepted from:

```text
Query
Body
Cookie
Header
```

Example:

```text
role=user
```

might exist in both:

```text
Cookie
```

and:

```text
POST body
```

Determine which source takes precedence.

---

# Validation Bypass Through Duplicate Inputs

Example:

```http
role=user&role=admin
```

Different components may use different values.

Start with benign values when determining precedence.

---

# Validation and Rate Limiting

Input validation does not replace anti-automation controls.

An endpoint may correctly validate every request but still permit unlimited attempts.

Refer to:

```text
docs/web/rate-limiting.md
```

---

# Validation and Error Handling

Invalid input should not trigger:

```text
500 Internal Server Error
Stack trace
Database exception
Framework debug page
```

A `500` response is not automatically a vulnerability.

Investigate whether the error reveals information or creates meaningful availability impact.

---

# Validation and Logging

Avoid logging raw sensitive or attacker-controlled values unnecessarily.

Potential risks include:

```text
Secret exposure
Log injection
Very large log entries
Control characters
Sensitive personal data
```

Logging should preserve useful security evidence without creating new exposure.

---

# Common Validation Weaknesses

## Client-Side Only Validation

```text
Browser blocks invalid input
Server accepts it
```

---

## Denylist-Only Validation

```text
Known malicious patterns blocked
Unexpected variants accepted
```

---

## Missing Type Validation

```text
Expected integer
Object accepted
```

---

## Missing Length Validation

```text
Expected short string
Extremely long input accepted
```

---

## Missing Range Validation

```text
Expected 1-100
-100 accepted
```

---

## Missing Enumeration Validation

```text
Expected user/business
admin accepted
```

---

## Inconsistent Validation

```text
Web UI validates
API does not
```

---

## Validation Before Decoding

```text
Encoded value passes validation
      |
      v
Decoded later
      |
      v
Dangerous interpretation
```

---

## Validation After Dangerous Processing

Incorrect order:

```text
Input
  |
  v
Dangerous Operation
  |
  v
Validation
```

Validation should occur before dangerous processing.

---

## Trusting Hidden Fields

```text
Hidden in browser
```

does not mean:

```text
Trusted by server
```

---

## Trusting HTTP Headers

Headers are attacker-controlled unless the architecture provides a specific trustworthy source and handling model.

---

## Trusting File Extensions

```text
document.pdf
```

does not prove:

```text
PDF content
```

---

## Ignoring Semantic Validation

```text
Valid integer
```

does not mean:

```text
Valid business value
```

---

# False Positives

Weak validation is not automatically exploitable.

Example:

```text
age=-1
```

is accepted.

But if the value:

```text
Has no security consequence
Does not affect business logic
Is never stored
Is corrected server-side
```

the security impact may be negligible.

A finding should demonstrate:

```text
Unexpected Input
       |
       v
Security-Relevant Behaviour
       |
       v
Impact
```

---

# Evidence Collection

Record:

```text
Endpoint
Method
Parameter
Normal value
Modified value
Expected behaviour
Actual behaviour
Response status
Response body
State change
Security impact
```

Example:

```text
Endpoint:
POST /api/order

Parameter:
quantity

Expected:
1 - 100

Test:
quantity=-10

Observed:
Request accepted

Result:
Order total became negative

Impact:
Business logic manipulation
```

This is much stronger evidence than:

```text
Application accepts negative numbers
```

---

# Example Finding: Missing Server-Side Range Validation

```text
Finding:
Insufficient Server-Side Validation of Order Quantity

Observed:
The order API accepts negative values for the quantity parameter.

The graphical interface restricts the quantity to positive values, but this restriction can be bypassed by modifying the request directly.

Example:

quantity=-10

The server accepted the request and used the negative quantity during order calculation.

Impact:
An authenticated user may manipulate order calculations by submitting values outside the intended business range.

Recommendation:
Enforce the permitted quantity range on the server before performing price or order calculations. Client-side restrictions may remain for usability but should not be relied upon as a security control.
```

---

# Example Finding: Client-Side Validation Only

```text
Finding:
Security-Relevant Input Validation Enforced Only Client-Side

Observed:
The application interface restricts the account type to predefined options.

However, the server accepts arbitrary account-type values when the request is modified directly.

Impact:
An attacker can bypass the browser restriction and submit values that were not intended to be available through the application.

The actual severity depends on how these values affect server-side functionality.

Recommendation:
Validate all security-relevant values on the server against the expected set of allowed values. Treat client-side validation only as a usability control.
```

---

# Example Finding: Unexpected JSON Properties Accepted

```text
Finding:
API Accepts Unexpected Request Properties

Observed:
The profile API accepts properties that are not part of the documented request schema.

Unexpected properties are passed to the underlying application object rather than being rejected or ignored.

Impact:
Depending on the available object properties, this behaviour may expose the application to over-posting or mass-assignment vulnerabilities.

Recommendation:
Define an explicit allowlist of properties accepted by each API operation. Bind request objects only to fields required for the specific operation and enforce authorisation separately for security-sensitive properties.
```

---

# Example Finding: Missing Maximum Length

```text
Finding:
Missing Server-Side Length Restriction on User-Controlled Field

Observed:
The application accepts values substantially larger than the length expected for the field.

Impact:
Unrestricted input lengths can increase resource consumption and may cause unexpected behaviour in downstream components.

No denial-of-service condition was demonstrated during testing.

Recommendation:
Define and enforce reasonable server-side minimum and maximum lengths based on the field's functional requirements.
```

Note the wording:

```text
No denial-of-service condition was demonstrated.
```

Do not claim DoS without demonstrating it safely and within scope.

---

# Example Finding: Invalid State Transition

```text
Finding:
Insufficient Validation of Order State Transitions

Observed:
The application permits an order to move directly from the CREATED state to the SHIPPED state without passing through the required payment state.

Impact:
An authenticated user may bypass the intended business workflow and cause the application to process an order in an invalid state.

Recommendation:
Define permitted state transitions server-side and reject requests that attempt to move objects between invalid states. Do not rely on the client interface to enforce workflow order.
```

---

# Finding Titles

Useful titles include:

```text
Insufficient Server-Side Input Validation

Security-Relevant Validation Enforced Only Client-Side

Missing Server-Side Range Validation

Missing Maximum Input Length

Unexpected API Properties Accepted

Insufficient Enumeration Validation

Inconsistent Validation Across API Versions

Inconsistent Validation Across HTTP Methods

Insufficient Validation of Business Rules

Invalid State Transitions Permitted

Unexpected Content Type Accepted

Insufficient File Type Validation

Duplicate Parameters Processed Inconsistently

Malformed Input Causes Sensitive Error Disclosure
```

Choose the title that describes the actual demonstrated weakness.

---

# Remediation Principles

A strong validation strategy follows:

```text
Define
  |
  v
Parse
  |
  v
Normalise Where Appropriate
  |
  v
Validate
  |
  v
Authorise
  |
  v
Process Using Safe APIs
  |
  v
Encode Output Appropriately
```

---

# Define Expected Input

For every field define:

```text
Type
Required / Optional
Minimum length
Maximum length
Minimum value
Maximum value
Format
Allowed values
Business rules
Null behaviour
```

---

# Reject Unexpected Input

Where possible:

```text
Expected:
name
email
```

Reject or deliberately ignore unexpected properties rather than automatically binding everything to internal objects.

Security-sensitive APIs should favour explicit request models.

---

# Use Strong Types

Prefer:

```text
Integer
Boolean
Date
Enum
UUID
```

over treating everything as:

```text
String
```

when the application's framework supports strong typing.

---

# Use Dedicated Parsers

Prefer mature parsers for:

```text
Dates
URLs
IP addresses
JSON
XML
UUIDs
```

rather than custom parsing logic.

---

# Validate Length

Set reasonable:

```text
Minimum
Maximum
```

based on business requirements.

---

# Validate Range

For numeric values define:

```text
Minimum
Maximum
```

and test boundaries.

---

# Validate Enumerations

For finite choices:

```text
Allow:
A
B
C
```

Reject:

```text
Everything else
```

---

# Validate Business Rules

Examples:

```text
startDate <= endDate

quantity > 0

withdrawal <= available balance

object belongs to current tenant

requested transition is permitted
```

---

# Validate on the Server

Client-side validation is useful for user experience.

Security validation must also occur server-side.

---

# Parameterise Queries

For database operations:

```text
Validation
      +
Parameterized Query
```

not:

```text
Validation alone
```

---

# Encode Output

When displaying user-controlled data:

```text
Validate Input
      +
Context-Aware Output Encoding
```

These controls solve different problems.

---

# Use Safe APIs

Prefer APIs that keep:

```text
Data
```

separate from:

```text
Code
Commands
Queries
Templates
```

---

# Pentesting Checklist

## Discovery

```text
[ ] Query parameters identified
[ ] Body parameters identified
[ ] JSON properties identified
[ ] XML elements identified
[ ] Path parameters identified
[ ] Headers identified
[ ] Cookies identified
[ ] File inputs identified
[ ] WebSocket inputs identified
[ ] GraphQL inputs identified
[ ] gRPC inputs identified
[ ] Webhook inputs identified
```

---

## Client-Side Controls

```text
[ ] HTML maxlength reviewed
[ ] HTML min/max reviewed
[ ] HTML pattern reviewed
[ ] Hidden fields identified
[ ] Disabled fields identified
[ ] Read-only fields identified
[ ] Dropdown values identified
[ ] JavaScript validation identified
[ ] Server-side enforcement verified
```

---

## Type Validation

```text
[ ] Expected type tested
[ ] String instead of number tested
[ ] Number instead of string tested
[ ] Boolean tested where relevant
[ ] Null tested
[ ] Array tested where relevant
[ ] Object tested where relevant
```

---

## Required Fields

```text
[ ] Missing parameter tested
[ ] Empty parameter tested
[ ] Null parameter tested
[ ] Whitespace-only value tested
```

---

## Length

```text
[ ] Minimum - 1 tested
[ ] Minimum tested
[ ] Minimum + 1 tested
[ ] Maximum - 1 tested
[ ] Maximum tested
[ ] Maximum + 1 tested
```

---

## Numeric Range

```text
[ ] Negative value tested
[ ] Zero tested
[ ] Minimum boundary tested
[ ] Maximum boundary tested
[ ] Above maximum tested
[ ] Large value considered
[ ] Decimal value considered
```

---

## Enumerations

```text
[ ] Expected values identified
[ ] Unknown value tested
[ ] Case variation tested
[ ] Whitespace variation tested
[ ] Empty value tested
```

---

## Encoding

```text
[ ] URL encoding considered
[ ] Double encoding considered
[ ] Unicode considered
[ ] Normalisation considered
[ ] Whitespace considered
```

---

## Duplicate Input

```text
[ ] Duplicate query parameters tested
[ ] Duplicate body parameters considered
[ ] Duplicate JSON keys considered
[ ] Parameter precedence understood
```

---

## Content Types

```text
[ ] Expected content type identified
[ ] Alternate content types considered
[ ] JSON tested where applicable
[ ] Form data tested where applicable
[ ] XML tested where applicable
[ ] Multipart tested where applicable
```

---

## JSON

```text
[ ] Required properties tested
[ ] Unexpected properties tested
[ ] Nested objects tested
[ ] Arrays tested
[ ] Type coercion tested
[ ] Duplicate keys considered
[ ] Schema enforcement assessed
```

---

## Files

```text
[ ] Filename validated
[ ] Extension validated
[ ] MIME type validated
[ ] Content validated
[ ] File signature considered
[ ] Size limits tested safely
[ ] Storage behaviour reviewed
```

---

## Business Logic

```text
[ ] Negative values tested
[ ] Zero values tested
[ ] Boundary values tested
[ ] Cross-field relationships tested
[ ] Invalid state transitions tested
[ ] Role-specific values tested
[ ] Tenant relationships tested
[ ] Authoritative server-side values identified
```

---

## Error Handling

```text
[ ] Invalid input returns controlled response
[ ] Stack traces absent
[ ] Database errors absent
[ ] Framework errors absent
[ ] Validation errors do not expose sensitive data
[ ] Error messages do not enable harmful enumeration
```

---

## Security Impact

```text
[ ] Validation weakness reproduced
[ ] Downstream behaviour understood
[ ] Security impact demonstrated
[ ] Finding not based solely on malformed input
[ ] Severity reflects actual impact
```

---

# Quick Reference

```text
Input Validation

DO:

Allowlist expected values
Validate server-side
Validate type
Validate length
Validate range
Validate structure
Validate semantics
Validate business rules
Use strong types
Use dedicated parsers
Use schemas where appropriate
Use safe APIs
Use parameterised queries
Encode output appropriately

DO NOT:

Trust browser validation
Trust hidden fields
Trust disabled fields
Trust dropdown values
Trust cookies
Trust headers
Trust MIME types
Trust file extensions
Rely only on denylists
Use validation as the sole SQLi defence
Use validation as the sole XSS defence
Assume syntactically valid means semantically valid
Assume a valid object ID is authorised
```

---

# Input Validation Testing Workflow

```text
                     ATTACK SURFACE
                           |
                           v
                     INPUT INVENTORY
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       HTTP             Structured         Files
       Input              Data
          |                |                |
    +-----+-----+      +---+---+        +---+---+
    |     |     |      |       |        |       |
    v     v     v      v       v        v       v
 Query  Body Headers  JSON    XML    Upload   Import
    |     |     |      |       |        |       |
    +-----+-----+------+-------+--------+-------+
                           |
                           v
                     CLASSIFY INPUT
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
         Type            Format          Business
          |                |                |
          v                v                v
       Integer          UUID             Quantity
       String           Date             Price
       Boolean          URL              State
       Array            Email            Role
          |                |                |
          +----------------+----------------+
                           |
                           v
                      TEST BASELINE
                           |
                           v
                  CONTROLLED MUTATION
                           |
       +----------+--------+--------+----------+
       |          |        |        |          |
       v          v        v        v          v
     Type       Length    Range   Encoding   Structure
       |          |        |        |          |
       +----------+--------+--------+----------+
                           |
                           v
                   SEMANTIC VALIDATION
                           |
                           v
                    BUSINESS RULES
                           |
                           v
                     AUTHORISATION
                           |
                           v
                    DOWNSTREAM SINK
                           |
              +------------+------------+
              |                         |
              v                         v
         Safe Behaviour          Unexpected Behaviour
                                        |
                                        v
                                 VERIFY IMPACT
                                        |
                                        v
                                     REPORT
```

---

# Final Testing Model

For every input ask:

```text
Where does it come from?

Who controls it?

What type should it be?

Is it required?

Can it be empty?

Can it be null?

What is the minimum length?

What is the maximum length?

What is the minimum value?

What is the maximum value?

What values are explicitly allowed?

Is the complete value validated?

Is Unicode relevant?

Is normalisation relevant?

Is the value decoded before validation?

Can the parameter occur more than once?

Can its type be changed?

Can unexpected properties be added?

Can another content type be used?

Is validation performed client-side?

Is validation also performed server-side?

Does another endpoint validate it differently?

Does another API version validate it differently?

Does another HTTP method validate it differently?

Is it syntactically valid?

Is it semantically valid?

Does it satisfy the business rules?

Is the current user authorised to use the value?

Where does the value go next?

Does it reach SQL?

Does it reach LDAP?

Does it reach a shell?

Does it reach a template?

Does it become a file path?

Does it become a URL?

Does it become HTML?

Does it control a redirect?

Does it control an object identifier?

Does it control price, quantity, state, role, or tenant?

What happens when validation fails?

Does the failure expose information?

Can validation be bypassed through encoding?

Can validation be bypassed through type confusion?

Can validation be bypassed through duplicate parameters?

Can validation be bypassed through another interface?

What is the actual security impact?
```

The central model is:

```text
Untrusted Data
      |
      v
Parse Safely
      |
      v
Syntactic Validation
      |
      v
Semantic Validation
      |
      v
Business Rule Validation
      |
      v
Authorisation
      |
      v
Safe Processing
      |
      v
Context-Specific Output Handling
```

Input validation should therefore be viewed as:

```text
One important security control
```

rather than:

```text
A universal vulnerability prevention mechanism
```

Strong applications combine:

```text
Input Validation
       +
Authentication
       +
Authorisation
       +
Parameterized Queries
       +
Safe APIs
       +
Output Encoding
       +
Secure Parser Configuration
       +
Business Rule Enforcement
       +
Rate Limiting
       +
Secure Error Handling
```

---

# References

## OWASP Input Validation Cheat Sheet

[OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP WSTG - Input Validation Testing

[OWASP WSTG - Input Validation Testing](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Injection Prevention Cheat Sheet

[OWASP Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## OWASP SQL Injection Prevention Cheat Sheet

[OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Cross Site Scripting Prevention Cheat Sheet

[OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## OWASP File Upload Cheat Sheet

[OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## OWASP SSRF Prevention Cheat Sheet

[OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## OWASP OS Command Injection Defense Cheat Sheet

[OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger Web Security Academy

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger BApp Store

[PortSwigger BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger Content Type Converter

[PortSwigger Content Type Converter](https://portswigger.net/bappstore/db57ecbe2cb7446292a94aa6181c9278){ target="_blank" rel="noopener noreferrer" }

---

## PortSwigger Param Miner

[PortSwigger Param Miner](https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943){ target="_blank" rel="noopener noreferrer" }

---

# Related Notes

```text
docs/web/attack-surface-analysis.md
docs/web/methodology.md
docs/web/checklist.md

docs/web/sql-injection.md
docs/web/nosql-injection.md
docs/web/ldap-injection.md
docs/web/command-injection.md
docs/web/ssti.md
docs/web/xss.md
docs/web/xxe.md

docs/web/ssrf.md
docs/web/path-traversal.md
docs/web/file-inclusion.md
docs/web/file-upload.md
docs/web/open-redirect.md

docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md

docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/mass-assignment.md

docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/rate-limiting.md
```
