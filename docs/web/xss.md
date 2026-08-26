# Cross-Site Scripting

Cross-Site Scripting (XSS) occurs when attacker-controlled input reaches a browser context where it is interpreted as executable client-side content.

XSS testing should not simply consist of sending large numbers of payloads. A more reliable approach is to determine where input enters the application, where it is reflected or stored, how the application transforms it, and in which browser context it eventually appears.

!!! warning "Authorised Security Testing"
    Perform XSS testing only against applications for which you have explicit authorisation. These notes are intended for authorised penetration testing, lab environments, security research and responsible vulnerability disclosure.

---

## Objectives

The primary objectives of XSS testing are to determine:

- whether user-controlled input reaches a browser response or DOM sink
- where the input appears
- which characters are accepted
- which characters are encoded or removed
- whether sanitisation is performed
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

First understand what the application does with the input.

---

# Types of XSS

The main categories are:

```text
Reflected XSS
Stored XSS
DOM-Based XSS
Blind XSS
```

These categories can overlap.

For example, stored data may later reach a client-side DOM sink and result in execution.

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

The first question should be:

> Where did `test123` appear?

---

## Reflected XSS Workflow

```text
Identify Input
      ↓
Submit Unique Marker
      ↓
Locate Reflection
      ↓
Determine Context
      ↓
Determine Encoding
      ↓
Test Relevant Characters
      ↓
Perform Context-Specific Testing
      ↓
Validate in Browser
```

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
```

The vulnerable rendering may occur somewhere other than where the data was originally submitted.

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

Therefore, stored XSS testing should include secondary application interfaces.

---

## Stored XSS Workflow

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
Check Secondary Interfaces
      ↓
Check Privileged Interfaces
      ↓
Validate Behaviour
```

One stored field may be rendered in multiple contexts.

Test each rendering location independently.

---

# DOM-Based XSS

DOM-based XSS occurs when client-side JavaScript takes attacker-controlled data and passes it into an unsafe sink.

The malicious value may never appear in the original server response.

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

This makes JavaScript and DOM analysis important during XSS testing.

---

# Start With a Unique Marker

Before testing executable syntax, submit a unique harmless marker.

For example:

```text
AMXSS987654
```

Then search the response for the marker.

Example:

```bash
curl -s "https://target.example/search?q=AMXSS987654" | grep "AMXSS987654"
```

Determine:

```text
Was the value reflected?

Where?

How many times?

Was it transformed?

Was it encoded?
```

---

# Reflection Analysis

Suppose:

```text
AMXSS987654
```

appears as:

```html
<h2>Results for AMXSS987654</h2>
```

The value is in HTML text context.

If it appears as:

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

These are different contexts and require different testing strategies.

---

# Understand the Injection Context

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

A test that works in one context may be completely irrelevant in another.

The correct question is:

> How will the browser parse this value?

---

# HTML Context

Example:

```html
<div>
USER_INPUT
</div>
```

Start by determining whether HTML metacharacters are encoded.

Example test:

```text
<test>
```

Possible response:

```html
&lt;test&gt;
```

This indicates that angle brackets are being HTML encoded.

If the response instead contains:

```html
<test>
```

the browser may interpret the value as markup.

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

Test interesting characters individually:

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
Can surrounding JavaScript syntax be influenced?
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

Review:

```text
Allowed protocols
URL encoding
Scheme restrictions
Redirect validation
DOM manipulation
```

URL contexts can interact with:

```text
Open redirects
DOM XSS
Unsafe URL handling
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

JSON reflection alone does not automatically constitute XSS.

The important question is what consumes the value.

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

Before attempting complex tests, determine which characters survive the application.

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

A marker can help identify transformations:

```text
AMXSS<>"'`{}()[]=/\;
```

Compare the request and response carefully.

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

Encoding must be appropriate for the output context.

HTML encoding does not necessarily protect a JavaScript context.

Similarly, JavaScript escaping may not be appropriate for an HTML attribute.

---

# Double Encoding

Check whether input passes through multiple decoding layers.

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

Applications containing several decoding and encoding layers can produce unexpected behaviour.

Analyse each transformation step.

---

# Burp Suite Workflow

Burp Suite is particularly useful because requests can be repeatedly modified while observing the exact response.

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

Start with:

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

For example:

```text
GET /search?q=§PAYLOAD§ HTTP/1.1
```

Test characters such as:

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

View Source shows the original HTML returned by the server.

The Elements panel shows the current DOM after JavaScript has executed.

For DOM XSS testing, the current DOM is often more important.

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

When JavaScript files have been collected during reconnaissance:

```bash
grep -RniE \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|document\.writeln|eval\(|setTimeout\(|setInterval\(|new Function' \
.
```

For larger applications, combine this with the JavaScript Analysis methodology from the reconnaissance section.

---

# File Names and Metadata

Applications sometimes render uploaded file names or metadata.

For example:

```text
report.pdf
```

may later appear as:

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

Some applications reflect or store HTTP headers in:

```text
Debug pages
Administrative interfaces
Analytics dashboards
Logging systems
Error pages
Monitoring interfaces
```

Headers worth reviewing include:

```text
User-Agent
Referer
X-Forwarded-For
X-Forwarded-Host
X-Original-URL
X-Requested-With
```

Start with a harmless marker:

```http
User-Agent: AMXSS987654
```

Then determine whether the value appears elsewhere.

---

# Blind XSS

Blind Cross-Site Scripting occurs when attacker-controlled input is stored or processed by an application but execution occurs in another interface that the tester cannot directly observe.

This commonly happens when submitted information is later viewed by:

```text
Administrators
Support personnel
Moderators
SOC analysts
Helpdesk personnel
Back-office users
Application operators
```

A typical flow is:

```text
Attacker-Controlled Input
          ↓
Application
          ↓
Database / Logs / Queue
          ↓
Internal Application
          ↓
Administrator Views Data
          ↓
Browser Processes Input
          ↓
Blind XSS Trigger
```

Unlike normal reflected XSS, execution may occur minutes, hours or days after the original request.

---

## Where to Test for Blind XSS

Blind XSS is particularly interesting anywhere user-controlled information may eventually be displayed in an internal interface.

Potential locations include:

```text
Contact forms
Support tickets
Feedback forms
User profiles
Account registration
Usernames
Display names
Email addresses
Company names
Address fields
Order information
Customer notes
File names
Uploaded file metadata
Audit logs
Application logs
Search logs
Error logs
User-Agent
Referer
X-Forwarded-For
X-Forwarded-Host
Administrative dashboards
CRM systems
Moderation interfaces
Analytics platforms
Monitoring systems
```

The important question is:

> Where might this data eventually be displayed?

---

## Blind XSS Through HTTP Headers

HTTP headers are interesting because they are frequently stored in logging or monitoring systems.

Examples include:

```text
User-Agent
Referer
X-Forwarded-For
X-Forwarded-Host
X-Real-IP
X-Original-URL
X-Requested-With
Forwarded
```

Start with a unique harmless marker.

Example:

```http
User-Agent: AM-BXSS-987654
```

---

## Blind XSS Testing Workflow

```text
Identify Stored Input
        ↓
Insert Unique Marker
        ↓
Determine Likely Internal Consumer
        ↓
Identify Interesting Input Locations
        ↓
Configure Authorised Callback
        ↓
Submit Controlled Test
        ↓
Wait for Interaction
        ↓
Record Callback Context
        ↓
Identify Trigger Location
        ↓
Manually Reproduce Where Possible
        ↓
Report
```

Keep track of exactly where each test value was submitted.

For example:

```text
BXSS-001 → User-Agent
BXSS-002 → Contact form name
BXSS-003 → Contact form message
BXSS-004 → Profile display name
BXSS-005 → Uploaded file name
BXSS-006 → Referer
```

This makes it significantly easier to determine which input triggered a callback.

---

## XSS Hunter

XSS Hunter can be used during authorised Blind XSS testing to detect execution occurring in interfaces that are not directly visible to the tester.

XSS Hunter by Truffle Security:

https://xsshunter.trufflesecurity.com/app/#/

General workflow:

```text
Application Input
       ↓
Blind XSS Test
       ↓
Input Stored
       ↓
Internal User Views Input
       ↓
Browser Executes Test
       ↓
XSS Hunter
       ↓
Callback Received
```

---

## Example XSS Hunter Workflow

```text
1. Identify fields likely to be viewed internally

2. Assign each test location a unique identifier

3. Configure the authorised XSS Hunter callback

4. Submit the controlled Blind XSS test

5. Continue normal testing

6. Monitor for callbacks

7. Correlate any callback with the original input location

8. Determine which application or administrative interface rendered it

9. Validate the underlying output handling

10. Document the complete source-to-sink path
```

The important evidence is not simply that a callback occurred.

Establish:

```text
SOURCE
  ↓
STORAGE
  ↓
INTERNAL INTERFACE
  ↓
RENDERING CONTEXT
  ↓
EXECUTION
  ↓
CALLBACK
```

---

## Burp Suite and Blind XSS

A practical workflow is:

```text
Burp Proxy
     ↓
HTTP History
     ↓
Interesting Request
     ↓
Repeater
     ↓
Identify Input Locations
     ↓
Insert Controlled Blind XSS Test
     ↓
Send Request
     ↓
Monitor Callback Service
```

Interesting locations include:

```text
Request parameters
JSON properties
HTTP headers
Cookies
Registration fields
Support forms
Profile fields
File metadata
```

Prioritise values likely to be:

```text
Stored
Logged
Reviewed
Moderated
Displayed
Investigated
```

---

## Blind XSS in Administrative Interfaces

Administrative interfaces frequently aggregate data from multiple untrusted sources.

For example:

```text
Public Contact Form
        ↓
Support Database
        ↓
Internal Support Dashboard
        ↓
Support Agent Opens Ticket
```

Another example:

```text
HTTP Request
     ↓
Application Logs
     ↓
Log Management Interface
     ↓
Administrator Reviews Event
```

The vulnerable component may therefore be an internal application rather than the public-facing endpoint itself.

---

## Blind XSS in Logging Systems

Consider:

```http
GET / HTTP/1.1
Host: target.example
User-Agent: AM-BXSS-987654
```

The public application may process the request normally.

However:

```text
User-Agent
    ↓
Web Server
    ↓
Application Log
    ↓
Log Management Platform
    ↓
Analyst Browser
```

If the log viewer renders untrusted data incorrectly, the vulnerability may appear there.

---

## Blind XSS in File Upload Workflows

File upload functionality may create secondary rendering locations.

Potentially interesting metadata includes:

```text
File name
Document title
Image metadata
Description
Upload comments
Display name
```

Example:

```text
Upload
   ↓
Metadata Stored
   ↓
Administrative File Manager
   ↓
Metadata Rendered
   ↓
Potential Blind XSS
```

Start with harmless markers to understand where metadata appears.

---

## Blind XSS Evidence

When a callback occurs, record:

```text
Original request
Affected endpoint
Affected parameter or header
Unique identifier
Timestamp submitted
Timestamp triggered
Callback domain
Triggering application if identifiable
Rendering context
Affected user role
Required interaction
Browser information where available
Relevant screenshot
```

---

## Blind XSS Testing Considerations

Blind XSS testing can affect users who are not directly participating in the assessment.

Therefore:

```text
Confirm scope
Use controlled callbacks
Avoid destructive behaviour
Minimise collected information
Do not attempt session theft
Do not collect unnecessary sensitive data
Use unique identifiers
Document every injection location
Stop once sufficient evidence exists
```

The objective is to demonstrate unsafe rendering, not to collect data from affected users.

---

## Blind XSS Quick Reference

```text
Interesting Input
      ↓
Will it be stored?
      ↓
Will someone else view it?
      ↓
Where will it be rendered?
      ↓
Is output encoding applied?
      ↓
Can browser execution occur?
      ↓
Can a controlled callback confirm it?
```

High-value locations:

```text
Support forms
Contact forms
Feedback
Profiles
Registration
File names
Metadata
User-Agent
Referer
Forwarding headers
Audit logs
Error logs
CRM systems
Admin panels
Monitoring systems
Analytics dashboards
```

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

Use it to prioritise parameters for manual analysis.

---

## Example kxss Workflow

Suppose reconnaissance produces:

```text
https://target.example/search?q=test
https://target.example/products?id=1
https://target.example/profile?name=test
```

Store them in:

```text
urls.txt
```

Then:

```bash
cat urls.txt | kxss
```

Review parameters where special characters are reflected.

Then:

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

# Parameter Discovery and XSS Workflow

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

Do not conclude that XSS is impossible simply because a common tag is blocked.

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

Context is more important than any individual payload.

---

# Test Characters Individually

Rather than immediately submitting complicated input, test:

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

This makes application behaviour considerably easier to understand.

---

# Browser Parsing

Remember that the browser is the final parser.

```text
HTTP Response
      ↓
HTML Parser
      ↓
DOM Construction
      ↓
JavaScript Execution
```

The browser may repair malformed HTML or create a DOM structure that is not immediately obvious from the raw response.

Always inspect the rendered DOM.

---

# Content Security Policy

Content Security Policy can reduce the impact of XSS but should be treated as defence in depth.

Review:

```http
Content-Security-Policy:
```

Important directives include:

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

Pay particular attention to configurations involving:

```text
'unsafe-inline'
'unsafe-eval'
*
data:
blob:
```

and overly broad trusted domains.

---

## CSP Example

A policy such as:

```http
Content-Security-Policy:
    default-src 'self';
    script-src 'self';
    object-src 'none';
    base-uri 'self';
```

is significantly stronger than:

```http
Content-Security-Policy:
    script-src * 'unsafe-inline' 'unsafe-eval';
```

However:

```text
CSP ≠ replacement for secure output handling
```

---

## Check CSP in Burp

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

A report-only policy does not enforce the restrictions.

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
Sanitisation bypass APIs
Unsafe trust APIs
Legacy AngularJS expressions
Third-party directives
```

The exact behaviour depends heavily on the Angular or AngularJS version.

Technology identification therefore matters.

---

# React

React normally escapes values inserted into JSX.

For example:

```jsx
<div>{username}</div>
```

However, review:

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

Review locations where raw HTML is deliberately rendered.

For example:

```text
v-html
```

Trace attacker-controlled input reaching these locations.

---

# jQuery

Legacy applications frequently use jQuery DOM manipulation.

Search for:

```javascript
.html()
.append()
.prepend()
.after()
.before()
```

Determine whether attacker-controlled data reaches these operations.

---

# Client-Side Template Injection

Client-side template systems can introduce injection paths that do not resemble traditional HTML injection.

When a framework is detected:

```text
Identify Framework
      ↓
Determine Version
      ↓
Identify Template Syntax
      ↓
Locate User-Controlled Input
      ↓
Understand Framework Sanitisation
      ↓
Perform Relevant Context Testing
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

Then determine whether known security issues apply to the identified version.

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

In these situations, evaluate the sanitisation policy rather than merely determining whether HTML is accepted.

---

# Markdown Rendering

Markdown input may eventually become HTML.

```text
Markdown
   ↓
Markdown Parser
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

A WAF blocking a test does not demonstrate that the underlying application safely handles the input.

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
GET Parameter
     ↓
Search Endpoint
     ↓
Insufficient Output Encoding
     ↓
HTML Attribute
     ↓
Browser Interprets Attacker-Controlled Content
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

Keep evidence minimal and reproducible.

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

Avoid simply stating:

```text
The application is vulnerable to XSS.
```

Explain the complete input-to-execution path.

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

prefer an API that treats the value as text when HTML is not required:

```javascript
element.textContent = userInput;
```

The appropriate solution depends on the application's intended behaviour.

---

# Output Encoding

Apply encoding based on output context.

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

## Stored and Blind XSS

- [ ] Test profile fields
- [ ] Test contact forms
- [ ] Test support tickets
- [ ] Test feedback fields
- [ ] Test file names
- [ ] Test metadata
- [ ] Review User-Agent handling
- [ ] Review Referer handling
- [ ] Review forwarding headers
- [ ] Consider administrative interfaces
- [ ] Consider logging systems
- [ ] Use unique Blind XSS identifiers
- [ ] Monitor authorised callback service

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

# XSS Payload and Research Resources

Large payload collections are useful, but they should complement context analysis rather than replace it.

A useful approach is:

```text
Understand Context
      ↓
Determine Restrictions
      ↓
Select Relevant Reference
      ↓
Choose Appropriate Test
      ↓
Manual Validation
```

---

## PortSwigger XSS Cheat Sheet

PortSwigger maintains an extensive interactive XSS cheat sheet containing vectors organised by tags, events, browser behaviour and context.

https://portswigger.net/web-security/cross-site-scripting/cheat-sheet

Particularly useful when researching:

```text
HTML contexts
Event handlers
Restricted tags
Restricted characters
Encoding
CSP
Framework-specific behaviour
Browser parsing
```

---

## Tiny XSS Payloads

Tiny XSS Payloads by terjanq provides a collection of compact XSS payloads and techniques.

https://tinyxss.terjanq.me/

This can be particularly useful when researching situations involving:

```text
Length restrictions
Character limits
Restricted input fields
Compact browser syntax
Payload optimisation
```

Use the resource after determining the injection context and application restrictions.

---

## XSSNow

XSSNow provides additional XSS payload and research material.

https://xssnow.in/

Use payload collections as references after understanding the injection context rather than blindly sending every available payload.

---

## OWASP XSS Filter Evasion Cheat Sheet

OWASP provides additional reference material covering browser parsing and XSS filter-evasion concepts.

https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html

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
| XSS Hunter | Blind XSS callback detection |
| Katana | Crawling and endpoint discovery |
| ParamSpider | Parameter discovery |
| waybackurls | Historical URL discovery |
| urlfinder | URL collection |
| grep / ripgrep | JavaScript source and sink searching |

---

# Quick Reference

```text
Reflection does not automatically mean XSS.

HTML acceptance does not automatically mean XSS.

A blocked common payload does not mean XSS is impossible.

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

# References

## OWASP Cross-Site Scripting Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

Guidance covering context-aware output encoding, HTML sanitisation, safe sinks and defensive controls.

---

## OWASP DOM Based XSS Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html

Guidance specifically covering DOM-based XSS and safe client-side development.

---

## OWASP XSS Filter Evasion Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html

---

## PortSwigger Cross-Site Scripting

https://portswigger.net/web-security/cross-site-scripting

PortSwigger Web Security Academy material covering reflected, stored and DOM-based XSS.

---

## PortSwigger XSS Cheat Sheet

https://portswigger.net/web-security/cross-site-scripting/cheat-sheet

Interactive reference for context-specific XSS research.

---

## Tiny XSS Payloads

https://tinyxss.terjanq.me/

Compact XSS payload and technique reference maintained by terjanq.

---

## XSSNow

https://xssnow.in/

XSS payload and research reference.

---

## XSS Hunter

https://xsshunter.trufflesecurity.com/app/#/

Useful during authorised Blind XSS testing where execution may occur in an internal or otherwise inaccessible browser context.

---

## kxss

https://github.com/Emoe/kxss

Useful for identifying reflected parameters and characters.

Example:

```bash
cat urls.txt | kxss
```

---

## Dalfox

https://github.com/hahwul/dalfox

Automated XSS parameter analysis and scanning.

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

# Related Notes

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

The reconnaissance, parameter discovery, JavaScript analysis and Burp Suite notes are particularly useful before performing XSS testing.
