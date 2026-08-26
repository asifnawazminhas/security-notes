# Cross-Site Scripting

Cross-Site Scripting (XSS) occurs when attacker-controlled input is interpreted by a browser as executable client-side content.

XSS testing should not simply consist of sending large numbers of payloads. A more reliable approach is to determine **where input enters the application, where it is reflected or stored, how the application transforms it, and in which browser context it eventually appears**.

!!! warning "Authorised Security Testing"
    Perform XSS testing only against applications for which you have explicit authorisation. The techniques in these notes are intended for authorised security assessments, lab environments, security research and responsible vulnerability disclosure.

---

## Objectives

The primary objectives of XSS testing are to determine:

- whether user-controlled input reaches a browser response or DOM sink
- where the input appears
- which characters are accepted
- which characters are encoded or removed
- whether the application performs sanitisation
- whether input can influence HTML structure
- whether input reaches JavaScript execution contexts
- whether DOM manipulation introduces additional attack paths
- whether stored input is rendered to other users
- whether browser security controls limit exploitation
- whether framework-specific behaviour changes the attack surface

A useful mental model is:

```text
Input
  ↓
Application
  ↓
Transformation / Validation
  ↓
Output
  ↓
Browser Parser
  ↓
HTML / Attribute / JavaScript / URL / DOM Context
  ↓
Potential Execution
```

---

# XSS Testing Workflow

A structured XSS assessment can generally be approached as:

```text
Discover Input
      ↓
Identify Reflection
      ↓
Determine Output Context
      ↓
Send Harmless Marker
      ↓
Identify Encoding / Filtering
      ↓
Test Relevant Characters
      ↓
Select Context-Appropriate Test
      ↓
Inspect Browser Interpretation
      ↓
Confirm Exploitability
      ↓
Assess Security Controls
      ↓
Document Source → Transformation → Sink
      ↓
Report
```

Do not immediately start with complicated payloads.

First understand **what the application does with your input**.

---

# Types of XSS

The three primary categories are:

```text
Reflected XSS
Stored XSS
DOM-Based XSS
```

There are also situations where these concepts overlap.

For example, stored data may later reach a DOM sink and result in client-side execution.

---

# Reflected XSS

Reflected XSS occurs when input from a request is included in the application's immediate response.

Common input locations include:

```text
GET parameters
POST parameters
URL paths
Search fields
Error messages
HTTP headers
Redirect parameters
API parameters
JSON values
```

Example request:

```http
GET /search?q=test123 HTTP/1.1
Host: target.example
```

Potential response:

```html
<p>Search results for test123</p>
```

The first question is not whether JavaScript executes.

The first question is:

> Where did `test123` appear?

---

# Stored XSS

Stored XSS occurs when attacker-controlled input is stored by the application and subsequently displayed to users.

Potential storage locations include:

```text
User profiles
Comments
Support tickets
Forum posts
Messages
Product descriptions
File metadata
File names
Administrative notes
Audit interfaces
CMS content
Contact forms
Log viewers
```

The important difference is that the vulnerable rendering may occur somewhere other than where the data was originally submitted.

Example:

```text
User submits input
       ↓
Application stores input
       ↓
Administrator opens dashboard
       ↓
Stored value rendered
       ↓
Potential execution
```

Therefore, stored XSS testing should include **secondary application interfaces**.

---

# DOM-Based XSS

DOM-based XSS occurs when client-side JavaScript takes attacker-controlled data and passes it into an unsafe sink.

The server response may not contain the malicious value at all.

Example:

```javascript
const value = location.hash;
document.getElementById("output").innerHTML = value;
```

The flow is:

```text
location.hash
      ↓
JavaScript
      ↓
innerHTML
      ↓
DOM
```

This makes DOM analysis important during XSS testing.

---

# Start With a Unique Marker

Before testing executable syntax, submit a unique harmless marker.

For example:

```text
xsstest1337
```

or:

```text
AMXSS987654
```

Then search the response for that marker.

Example:

```bash
curl -s "https://target.example/search?q=AMXSS987654" | grep "AMXSS987654"
```

The objective is to determine:

```text
Was the value reflected?

Where?

How many times?

Was it transformed?

Was it encoded?
```

---

# Reflection Analysis

Suppose the input:

```text
AMXSS987654
```

appears as:

```html
<h2>Results for AMXSS987654</h2>
```

The value is in an HTML text context.

But if it appears as:

```html
<input value="AMXSS987654">
```

it is inside an HTML attribute.

If it appears as:

```html
<script>
var search = "AMXSS987654";
</script>
```

it is inside JavaScript.

These are different contexts and require different testing approaches.

---

# Understand the Injection Context

The injection context is one of the most important aspects of XSS testing.

Typical contexts include:

```text
HTML text
HTML attributes
JavaScript strings
JavaScript template literals
URLs
CSS
JSON
DOM sinks
Client-side templates
```

A payload that works in one context may be completely irrelevant in another.

---

# HTML Context

Example:

```html
<div>
USER_INPUT
</div>
```

Start by testing whether HTML metacharacters are encoded.

Example test:

```text
<test>
```

Possible response:

```html
&lt;test&gt;
```

This indicates that angle brackets are being encoded.

If the response instead contains:

```html
<test>
```

the browser may interpret the input as markup.

Further context-specific testing is then appropriate.

---

# HTML Attribute Context

Example:

```html
<input value="USER_INPUT">
```

Relevant questions include:

```text
Can the quote be terminated?
Are quotes encoded?
Are additional attributes possible?
Are event handlers filtered?
Is the attribute quoted?
```

Test characters individually.

For example:

```text
"
'
<
>
=
`
```

Observe exactly how each character is handled.

---

# JavaScript Context

Example:

```html
<script>
var username = "USER_INPUT";
</script>
```

Questions include:

```text
Which quote surrounds the input?
Are quotes escaped?
Are backslashes escaped?
Are newlines allowed?
Is the value JSON encoded?
Can the surrounding JavaScript syntax be influenced?
```

Do not treat JavaScript contexts like HTML contexts.

The JavaScript parser determines how the input is interpreted.

---

# URL Context

Input may appear inside:

```html
<a href="USER_INPUT">
```

or:

```javascript
window.location = userInput;
```

Test:

```text
Allowed protocols
URL encoding
Scheme restrictions
Redirect validation
DOM manipulation
```

URL contexts can interact with:

```text
Open redirect vulnerabilities
DOM XSS
Unsafe URL schemes
Client-side routing
```

---

# JSON Context

Modern applications frequently return user-controlled data through JSON APIs.

Example:

```json
{
  "username": "USER_INPUT"
}
```

JSON alone does not automatically imply XSS.

The important question is:

> What consumes the JSON value?

For example:

```text
API
 ↓
JSON
 ↓
JavaScript
 ↓
innerHTML
 ↓
Browser
```

The vulnerability may exist in the frontend rather than the API response itself.

---

# Character Testing

Before attempting complex payloads, determine which characters survive the application.

Useful characters include:

```text
<
>
"
'
`
(
)
{
}
[
]
=
/
\
;
:
&
#
```

A simple marker can help identify transformations:

```text
AMXSS<>"'`{}()[]=/\;
```

Compare the request and response.

---

# Encoding Analysis

Common transformations include:

```text
<    →    &lt;
>    →    &gt;
"    →    &quot;
'    →    &#39;
&    →    &amp;
```

But encoding must be appropriate for the output context.

HTML encoding does not necessarily protect a JavaScript context.

Similarly, JavaScript escaping may not be appropriate for an HTML attribute.

---

# Double Encoding

Check whether input is decoded multiple times.

For example:

```text
%3C
```

represents:

```text
<
```

Double encoding may appear as:

```text
%253C
```

Applications containing multiple decoding layers can sometimes produce unexpected results.

Analyse each transformation step.

---

# Burp Suite Workflow

Burp Suite is particularly useful for XSS testing because requests can be modified repeatedly while observing the exact response.

A useful workflow is:

```text
Proxy
  ↓
HTTP History
  ↓
Identify Input
  ↓
Send to Repeater
  ↓
Insert Unique Marker
  ↓
Search Response
  ↓
Determine Context
  ↓
Test Characters
  ↓
Test Encoding
  ↓
Confirm Browser Behaviour
```

---

# Burp Proxy

Browse the application normally with Burp Proxy enabled.

Look for parameters such as:

```text
q=
search=
query=
name=
message=
comment=
return=
redirect=
url=
callback=
next=
page=
filter=
sort=
```

Do not ignore:

```text
JSON requests
GraphQL
API endpoints
HTTP headers
Cookies
WebSocket messages
```

---

# Burp Repeater

Send interesting requests to Repeater.

Start with a marker:

```text
AMXSS987654
```

Then search the response.

Determine whether the value appears in:

```text
HTML
Attribute
JavaScript
JSON
URL
CSS
```

Repeater is ideal for controlled character-by-character analysis.

---

# Burp Intruder

Intruder can help determine how the application handles different characters.

For example, configure a payload position:

```text
GET /search?q=§PAYLOAD§ HTTP/1.1
```

Then test characters such as:

```text
<
>
"
'
`
{
}
(
)
;
```

Compare:

```text
Status code
Response length
Reflection
Encoding
Blocking
Application errors
```

This can quickly identify filtering behaviour.

---

# Browser DevTools

Do not rely only on the raw HTTP response.

The browser may transform the document after it loads.

Use browser DevTools to inspect:

```text
Elements
Sources
Network
Console
Event listeners
DOM mutations
```

This is especially important for DOM XSS.

---

# View Source vs DOM

There is an important distinction between:

```text
View Source
```

and:

```text
Elements
```

`View Source` shows the original HTML returned by the server.

The Elements panel shows the current DOM after JavaScript has executed.

For DOM XSS testing, the **current DOM** is often more important.

---

# DOM Sources

Sources are locations from which attacker-controlled data may enter client-side JavaScript.

Common examples include:

```javascript
location
location.href
location.search
location.hash
document.URL
document.documentURI
document.referrer
window.name
postMessage
localStorage
sessionStorage
```

Example:

```javascript
const input = location.hash;
```

---

# DOM Sinks

Sinks are functions or properties that may interpret attacker-controlled data unsafely.

Examples worth reviewing include:

```javascript
innerHTML
outerHTML
insertAdjacentHTML
document.write
document.writeln
eval
setTimeout
setInterval
Function
```

Also review framework-specific rendering functions and DOM manipulation libraries.

---

# Source-to-Sink Analysis

A useful way to analyse DOM XSS is:

```text
Source
  ↓
Transformation
  ↓
Validation
  ↓
Sink
```

Example:

```javascript
const query = location.search;
const value = new URLSearchParams(query).get("name");
document.getElementById("welcome").innerHTML = value;
```

The flow is:

```text
location.search
      ↓
URLSearchParams
      ↓
name
      ↓
innerHTML
```

This is significantly more useful than simply recording that a parameter was reflected.

---

# Search JavaScript for Potential Sinks

When JavaScript files have been collected during reconnaissance, search them for interesting DOM operations.

Example:

```bash
grep -RniE \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|document\.writeln|eval\(|setTimeout\(|setInterval\(|new Function' \
.
```

For larger JavaScript applications, combine this with the JavaScript analysis methodology documented under:

```text
Web Application Security
└── Reconnaissance
    └── JavaScript Analysis
```

---

# Stored XSS Workflow

Stored XSS requires a slightly different workflow.

```text
Identify Stored Input
      ↓
Submit Unique Marker
      ↓
Locate Every Rendering Location
      ↓
Determine Rendering Context
      ↓
Test Encoding
      ↓
Check Privileged Interfaces
      ↓
Confirm Execution
```

For example:

```text
Profile name
      ↓
Database
      ↓
User profile
      ↓
Admin dashboard
      ↓
Audit log
```

One stored field may be displayed in several different contexts.

Test each context independently.

---

# File Names and Metadata

Applications sometimes render uploaded file names or metadata.

For example:

```text
report.pdf
```

may later appear in:

```html
<a href="/files/123">report.pdf</a>
```

Test whether unusual but harmless characters are:

```text
Accepted
Stored
Encoded
Normalised
Rendered
```

This can identify potential stored injection issues.

---

# HTTP Headers

Some applications reflect HTTP headers into:

```text
Debug pages
Administrative interfaces
Analytics dashboards
Logging systems
Error pages
Monitoring interfaces
```

Headers worth reviewing can include:

```text
User-Agent
Referer
X-Forwarded-For
X-Forwarded-Host
X-Original-URL
X-Requested-With
```

Use harmless markers first.

Example:

```http
User-Agent: AMXSS987654
```

Then determine whether the marker appears elsewhere in the application.

---

# Blind XSS Considerations

Some stored input may only be viewed later by another application component or privileged user.

Potential locations include:

```text
Support dashboards
Administration panels
Logging systems
CRM systems
Moderation interfaces
Monitoring systems
Analytics platforms
```

For authorised assessments, document the expected interaction path before performing any callback-based testing.

---

# kxss

`kxss` is useful for identifying parameters that are reflected and determining which special characters survive reflection.

Typical pipeline:

```bash
cat urls.txt | kxss
```

A reconnaissance workflow may look like:

```text
URL Collection
     ↓
Parameter Discovery
     ↓
kxss
     ↓
Reflected Candidates
     ↓
Manual Verification
```

For example:

```bash
cat parameters.txt | kxss
```

Do not automatically treat every `kxss` result as a vulnerability.

Use it to **prioritise parameters for manual analysis**.

---

# Example kxss Workflow

Suppose reconnaissance produces:

```text
https://target.example/search?q=test
https://target.example/products?id=1
https://target.example/profile?name=test
```

Store them:

```bash
cat urls.txt
```

Then:

```bash
cat urls.txt | kxss
```

Review parameters where special characters are reflected.

Then manually inspect those endpoints with Burp Repeater.

```text
kxss
 ↓
Candidate
 ↓
Burp Repeater
 ↓
Context Analysis
 ↓
Manual Validation
```

---

# Dalfox

Dalfox is an XSS scanning and parameter analysis tool.

A single URL can be analysed using:

```bash
dalfox url "https://target.example/search?q=test"
```

A file containing URLs can be processed using:

```bash
dalfox file urls.txt
```

Dalfox can be useful after parameter discovery to prioritise potentially vulnerable input.

A workflow can look like:

```text
Subdomain Enumeration
        ↓
HTTP Probing
        ↓
Crawling
        ↓
Parameter Discovery
        ↓
kxss
        ↓
Dalfox
        ↓
Manual Verification
        ↓
Burp Suite
```

Automated results should always be manually verified.

---

# Parameter Discovery + XSS Workflow

A practical reconnaissance pipeline may look like:

```text
Subdomains
    ↓
Alive Hosts
    ↓
Crawler
    ↓
Historical URLs
    ↓
Parameter Discovery
    ↓
Deduplicate
    ↓
kxss
    ↓
Dalfox
    ↓
Burp Verification
```

Potential tooling includes:

```text
subfinder
httpx
katana
waybackurls
urlfinder
ParamSpider
kxss
Dalfox
Burp Suite
```

The exact tool is less important than understanding what each stage contributes.

---

# Testing Filters

Applications may block particular strings while still allowing dangerous browser behaviour.

Do not conclude that XSS is impossible simply because:

```text
<script>
```

is blocked.

Determine what is actually being filtered.

Questions include:

```text
Are angle brackets blocked?
Are quotes blocked?
Are event handler names blocked?
Are particular tags blocked?
Is filtering case-sensitive?
Is decoding performed before filtering?
Is sanitisation applied before or after rendering?
```

Context is more important than any individual string.

---

# Test Characters Individually

Rather than immediately submitting a complicated payload, test:

```text
<
```

then:

```text
>
```

then:

```text
"
```

then:

```text
'
```

then:

```text
`
```

This makes it much easier to understand application behaviour.

---

# Browser Parsing

Remember that the browser is the final parser.

The application may return malformed HTML that the browser repairs.

Therefore:

```text
HTTP response
      ↓
HTML parser
      ↓
DOM construction
      ↓
JavaScript execution
```

can produce behaviour that is not immediately obvious from the raw response.

Always inspect the rendered DOM.

---

# Content Security Policy

Content Security Policy (CSP) can reduce the impact of XSS but should be treated as defence in depth.

Review the CSP header:

```http
Content-Security-Policy:
```

Useful directives include:

```text
default-src
script-src
style-src
img-src
connect-src
frame-src
object-src
base-uri
form-action
frame-ancestors
```

Pay particular attention to:

```text
'unsafe-inline'
'unsafe-eval'
*
data:
blob:
```

and overly broad trusted domains.

---

# CSP Example

Example:

```http
Content-Security-Policy:
    default-src 'self';
    script-src 'self';
    object-src 'none';
    base-uri 'self';
```

This is significantly stronger than:

```http
Content-Security-Policy:
    script-src * 'unsafe-inline' 'unsafe-eval';
```

However, CSP should not replace proper output encoding and sanitisation.

---

# Check CSP in Burp

In Burp Suite:

```text
Proxy
 ↓
HTTP History
 ↓
Response
 ↓
Headers
 ↓
Content-Security-Policy
```

Also check:

```text
Content-Security-Policy-Report-Only
```

A report-only policy does not enforce restrictions.

---

# Framework-Specific Testing

Modern frontend frameworks change the way XSS vulnerabilities appear.

Frameworks worth considering include:

```text
Angular
AngularJS
React
Vue
Next.js
jQuery
Client-side template engines
```

Do not assume that using a framework automatically prevents XSS.

---

# Angular and AngularJS

Review:

```text
Template rendering
DOM manipulation
Dynamic HTML
Sanitisation bypasses
Unsafe trust APIs
Legacy AngularJS expressions
Third-party directives
```

Interesting areas may include APIs that explicitly trust HTML or bypass normal sanitisation.

The exact behaviour depends heavily on the Angular version.

Technology identification therefore matters.

---

# React

React normally escapes values inserted into JSX.

For example:

```jsx
<div>{username}</div>
```

is generally safer than inserting raw HTML.

However, review uses of:

```javascript
dangerouslySetInnerHTML
```

Example:

```jsx
<div dangerouslySetInnerHTML={{ __html: userContent }} />
```

Trace where `userContent` originates and whether it is sanitised.

---

# Vue

Review areas where raw HTML is deliberately rendered.

For example:

```text
v-html
```

Trace attacker-controlled input reaching these locations.

---

# jQuery

Legacy applications frequently use jQuery DOM manipulation.

Search for patterns such as:

```javascript
.html()
.append()
.prepend()
.after()
.before()
```

Then determine whether attacker-controlled data reaches these operations.

---

# Template Injection and XSS

Client-side template systems can sometimes introduce injection paths that do not resemble traditional HTML injection.

When a framework is detected:

```text
Identify framework
      ↓
Determine version
      ↓
Identify template syntax
      ↓
Locate user-controlled input
      ↓
Understand framework sanitisation
      ↓
Test relevant context
```

Avoid blindly applying payloads intended for a different framework or version.

---

# Third-Party Components

XSS may originate in:

```text
JavaScript libraries
WYSIWYG editors
Markdown renderers
UI components
Template engines
Analytics widgets
Chat components
File previewers
Legacy frontend frameworks
```

Record library versions during reconnaissance.

Then check whether known security issues apply to the identified version.

---

# Rich Text Editors

Applications intentionally allowing HTML require special attention.

Examples include:

```text
CMS editors
Forum editors
Email editors
Knowledge bases
Markdown editors
WYSIWYG components
```

The application may intentionally permit:

```html
<b>
<i>
<p>
<a>
```

while attempting to remove dangerous elements and attributes.

In these situations, evaluate the **sanitisation policy**, not merely whether HTML is accepted.

---

# Markdown Rendering

Markdown input may eventually become HTML.

Example:

```text
Markdown
   ↓
Markdown parser
   ↓
HTML
   ↓
Sanitiser
   ↓
Browser
```

Review whether raw HTML is permitted and whether sanitisation occurs after Markdown conversion.

---

# WAF Behaviour

A Web Application Firewall may block some test strings.

Indicators include:

```text
403 responses
Different response lengths
Connection resets
Generic security pages
Request blocking
Parameter-specific blocking
```

Record WAF behaviour separately from application-level encoding.

A WAF blocking a payload does not demonstrate that the underlying application safely handles the input.

---

# Validation

A valid XSS finding should demonstrate more than simple reflection.

Ideally establish:

```text
Source
 ↓
Input
 ↓
Transformation
 ↓
Output Context
 ↓
Browser Interpretation
 ↓
Security Impact
```

For example:

```text
GET parameter
     ↓
Search endpoint
     ↓
No output encoding
     ↓
HTML attribute
     ↓
Browser interprets attacker-controlled markup
```

---

# Evidence Collection

Useful evidence includes:

```text
Affected endpoint
HTTP method
Parameter
Original request
Original response
Reflection location
Output context
Encoding behaviour
Browser behaviour
Screenshots
DOM evidence
CSP configuration
Required user interaction
Affected user role
```

Keep the evidence minimal and reproducible.

---

# XSS Reporting

A report should clearly explain:

```text
Where input originates
Where it is rendered
Why existing encoding or sanitisation fails
What browser context is affected
Whether interaction is required
Who can be targeted
What security impact results
How the issue should be remediated
```

Avoid describing the finding merely as:

```text
"The application is vulnerable to XSS."
```

Instead explain the complete input-to-execution path.

---

# Example Finding Structure

```text
Title
Stored Cross-Site Scripting in Profile Display Name

Affected Endpoint
POST /api/profile

Affected Parameter
displayName

Rendering Location
/admin/users

Context
HTML

Authentication Required
Yes

Affected Users
Administrative users

Description
The application stores attacker-controlled profile data and later
renders the value within the administrative interface without
context-appropriate output encoding.

Impact
An attacker able to control the affected field may cause
attacker-controlled client-side content to execute when the
stored value is viewed by another user.

Recommendation
Apply context-appropriate output encoding and sanitisation before
rendering user-controlled content.
```

---

# Remediation

XSS remediation depends on context.

General defensive principles include:

```text
Context-aware output encoding
HTML sanitisation where HTML must be accepted
Safe DOM APIs
Framework-native escaping
Avoid dangerous JavaScript APIs
Validate URLs and protocols
Reduce unnecessary dynamic HTML
Use CSP as defence in depth
Keep frontend dependencies updated
```

---

# Prefer Safe DOM APIs

Instead of:

```javascript
element.innerHTML = userInput;
```

prefer APIs that treat the value as text when HTML is not required:

```javascript
element.textContent = userInput;
```

The appropriate solution depends on the application's intended behaviour.

---

# Output Encoding

Apply encoding based on the output context.

Different contexts require different handling:

```text
HTML body
HTML attribute
JavaScript
URL
CSS
```

There is no single universal encoding operation that is correct for every context.

---

# HTML Sanitisation

If the application intentionally accepts HTML, use a well-maintained HTML sanitisation library with an explicit allowlist.

The sanitiser should control:

```text
Allowed elements
Allowed attributes
Allowed protocols
Dangerous URL schemes
Event handlers
Embedded content
```

Avoid creating custom sanitisation using simple regular expressions.

---

# Security Headers

Security headers can provide additional protection.

Review:

```text
Content-Security-Policy
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
```

For XSS specifically, CSP can significantly reduce exploitability when correctly implemented.

However:

```text
CSP ≠ replacement for secure output handling
```

---

# XSS Testing Checklist

## Discovery

- [ ] Identify GET parameters
- [ ] Identify POST parameters
- [ ] Identify JSON parameters
- [ ] Identify URL path input
- [ ] Identify HTTP header input
- [ ] Identify stored user input
- [ ] Identify file names and metadata
- [ ] Identify WebSocket input
- [ ] Identify client-side sources

## Reflection

- [ ] Insert unique marker
- [ ] Search response
- [ ] Determine number of reflections
- [ ] Determine output context
- [ ] Compare raw response and DOM
- [ ] Check secondary interfaces

## Character Handling

- [ ] Test `<`
- [ ] Test `>`
- [ ] Test `"`
- [ ] Test `'`
- [ ] Test backticks
- [ ] Test parentheses
- [ ] Test braces
- [ ] Test URL encoding
- [ ] Test application transformations

## Context

- [ ] HTML context
- [ ] Attribute context
- [ ] JavaScript context
- [ ] URL context
- [ ] JSON context
- [ ] DOM context
- [ ] Template context

## DOM

- [ ] Review `location`
- [ ] Review `location.search`
- [ ] Review `location.hash`
- [ ] Review `document.referrer`
- [ ] Review `postMessage`
- [ ] Review local storage
- [ ] Review session storage
- [ ] Search for `innerHTML`
- [ ] Search for `outerHTML`
- [ ] Search for `document.write`
- [ ] Search for `insertAdjacentHTML`
- [ ] Search for dynamic execution APIs

## Frameworks

- [ ] Identify frontend framework
- [ ] Determine version
- [ ] Review raw HTML rendering
- [ ] Review sanitisation bypass APIs
- [ ] Review third-party components
- [ ] Review client-side templates

## Security Controls

- [ ] Review CSP
- [ ] Check report-only CSP
- [ ] Identify WAF behaviour
- [ ] Review sanitisation
- [ ] Review output encoding

## Validation

- [ ] Reproduce manually
- [ ] Confirm browser interpretation
- [ ] Determine affected users
- [ ] Determine required interaction
- [ ] Capture minimal evidence
- [ ] Document source-to-sink path

---

# Quick Reference

```text
Reflection does not automatically mean XSS.

HTML acceptance does not automatically mean XSS.

A blocked <script> tag does not mean XSS is impossible.

JSON reflection does not automatically mean XSS.

CSP does not fix unsafe output handling.

Automated scanner output is not sufficient evidence.

Always determine:

SOURCE → TRANSFORMATION → CONTEXT → SINK → BROWSER
```

---

# Practical Workflow Summary

```text
                    ┌─────────────────────┐
                    │   Discover Inputs   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Insert Marker     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Find Reflections    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Determine Context   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Test Characters     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Analyse Encoding    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Context-Specific    │
                    │ Testing             │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Browser / DOM       │
                    │ Validation          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Manual Verification │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evidence + Report   │
                    └─────────────────────┘
```

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | Manual HTTP testing and validation |
| Burp Repeater | Controlled request modification |
| Burp Intruder | Character and parameter testing |
| Browser DevTools | DOM and JavaScript analysis |
| kxss | Reflection and character discovery |
| Dalfox | XSS scanning and parameter analysis |
| Katana | Crawling and endpoint discovery |
| ParamSpider | Parameter discovery |
| waybackurls | Historical URL discovery |
| urlfinder | URL collection |
| grep / ripgrep | JavaScript source and sink searching |

---

# References

## OWASP

### Cross-Site Scripting Prevention Cheat Sheet

OWASP guidance covering context-aware output encoding, HTML sanitisation, safe sinks and defensive controls.

https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

### DOM Based XSS Prevention Cheat Sheet

OWASP guidance specifically covering DOM-based XSS and safe client-side development.

https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html

### XSS Filter Evasion Cheat Sheet

Reference material covering browser parsing behaviour and alternative XSS vectors.

https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html

---

## PortSwigger Web Security Academy

### Cross-Site Scripting

PortSwigger's XSS learning material and labs.

https://portswigger.net/web-security/cross-site-scripting

### Cross-Site Scripting Cheat Sheet

A large interactive reference containing XSS vectors organised by elements, events, browser behaviour and context.

https://portswigger.net/web-security/cross-site-scripting/cheat-sheet

This is particularly useful when testing unusual contexts or determining which browser events and HTML elements may be relevant.

---

## XSSNow

XSS payload and research reference.

https://xssnow.in/

Use large payload collections as references after understanding the injection context rather than blindly sending every payload.

---

## kxss

GitHub:

https://github.com/Emoe/kxss

Useful for identifying reflected parameters and characters during reconnaissance.

Example:

```bash
cat urls.txt | kxss
```

---

## Dalfox

GitHub:

https://github.com/hahwul/dalfox

Dalfox provides automated XSS parameter analysis and scanning.

Example:

```bash
dalfox url "https://target.example/search?q=test"
```

or:

```bash
dalfox file urls.txt
```

Automated findings should always be manually verified.

---

## Related Notes

Continue with:

```text
Web Application Security
├── Methodology
├── Pentesting Checklist
├── Reconnaissance
│   ├── Subdomain Enumeration
│   ├── Technology Identification
│   ├── Content Discovery
│   ├── Parameter Discovery
│   └── JavaScript Analysis
├── Authentication
├── Authorisation
├── Session Management
├── Burp Suite
│   ├── Extensions
│   └── Testing Workflows
└── Cross-Site Scripting
```

The reconnaissance, parameter discovery and JavaScript analysis notes are particularly useful before performing XSS testing.
