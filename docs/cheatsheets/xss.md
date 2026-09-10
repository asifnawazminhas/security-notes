---
title: Cross-Site Scripting (XSS) Cheatsheet
description: Detailed practical XSS cheatsheet for authorised web application security testing covering reflected, stored and DOM-based XSS, HTML and JavaScript contexts, source and sink analysis, encoding, CSP, Burp Suite, validation, evidence, remediation and retesting.
---

# Cross-Site Scripting (XSS) Cheatsheet

Cross-site scripting (XSS) occurs when attacker-controlled data reaches a browser execution context without appropriate handling, allowing unintended client-side script execution.

A simplified model is:

```text
Attacker-Controlled Input
          |
          v
      Application
          |
          v
      HTML / DOM
          |
          v
 Browser Interprets Input
          |
          v
 JavaScript Execution
```

The important question is not simply:

```text
Is my input reflected?
```

It is:

```text
Where does my input appear?

How is it encoded?

How does the browser parse it?

Can it reach an executable context?
```

!!! warning "Authorised Security Testing"

    Perform XSS testing only against applications that are explicitly within scope. Prefer harmless proof-of-concept execution and controlled test accounts. Avoid payloads that access real user sessions, sensitive information, browser storage or external systems unless that activity is specifically authorised.


# Quick Reference

## Basic HTML Context Probe

```html
<script>alert(1)</script>
```


## Image Event Handler

```html
<img src=x onerror=alert(1)>
```


## SVG Event Handler

```html
<svg onload=alert(1)>
```


## Attribute Context Probe

```html
" autofocus onfocus=alert(1) x="
```


## JavaScript String Context Probe

```javascript
';alert(1);//
```


## Harmless Marker

```text
XSS_TEST_7f3a9
```


## HTML-Sensitive Characters

```text
<
>
"
'
&
```


## URL-Encoding Examples

```text
<  -> %3C
>  -> %3E
"  -> %22
'  -> %27
```


# XSS Testing Model

Do not use:

```text
Input Reflected
      |
      v
     XSS
```

Use:

```text
Input
  |
  v
Reflection / Storage / DOM Flow
  |
  v
Identify Context
  |
  v
Determine Encoding
  |
  v
Determine Browser Parsing
  |
  v
Controlled Execution?
  |
  +--> No  -> Reflection / Candidate
  |
  +--> Yes -> XSS Confirmed
```


# Main XSS Types

The three major categories are:

```text
Reflected XSS

Stored XSS

DOM-Based XSS
```


# Reflected XSS

Reflected XSS occurs when request data is included in the immediate HTTP response and reaches an executable browser context.

```text
Request
   |
   v
Server
   |
   v
Response Contains Input
   |
   v
Browser Parses Response
   |
   v
Execution
```


# Reflected Example

Request:

```http
GET /search?q=test HTTP/1.1
Host: example.com
```

Response:

```html
<h2>Search results for test</h2>
```

The value:

```text
test
```

is reflected.

This alone is not XSS.


# Safe Reflection

If:

```text
?q=<test>
```

becomes:

```html
<h2>Search results for &lt;test&gt;</h2>
```

the application is applying HTML encoding for that context.

The browser displays:

```text
<test>
```

as text instead of interpreting it as markup.


# Potentially Unsafe Reflection

If:

```text
?q=<b>test</b>
```

becomes:

```html
<h2>Search results for <b>test</b></h2>
```

the browser interprets the supplied HTML.

This demonstrates HTML injection.

It does not yet necessarily demonstrate JavaScript execution.


# Reflected XSS Validation

If a harmless execution marker such as:

```html
<img src=x onerror=alert(1)>
```

is inserted into an executable HTML context and the event handler runs, reflected XSS is established.


# Stored XSS

Stored XSS occurs when attacker-controlled data is persisted and later rendered to one or more users.

```text
Attacker Input
      |
      v
   Database
      |
      v
Stored Value
      |
      v
Victim Loads Page
      |
      v
Browser Executes
```


# Common Stored XSS Locations

```text
Profile names

Comments

Support tickets

Forum posts

Product reviews

File names

Organisation names

Chat messages

Administrative notes

Imported records

CMS content

Audit/log viewers
```


# Stored XSS Workflow

```text
Submit Marker
      |
      v
Confirm Stored
      |
      v
Locate Every Render Location
      |
      v
Identify Context
      |
      v
Controlled XSS Test
      |
      v
Test Relevant Roles
```


# Stored XSS Can Cross Roles

Example:

```text
Standard User
     |
     v
Creates Support Ticket
     |
     v
Stored in Database
     |
     v
Administrator Opens Ticket
     |
     v
Payload Executes
```

This can materially increase impact because execution occurs in a more privileged user's browser context.


# Stored Input May Appear in Multiple Places

A profile name might appear in:

```text
Profile page

Navigation

Search results

Administrative panel

Audit history

Emails

PDF exports
```

Each output context must be considered separately.


# DOM-Based XSS

DOM-based XSS occurs when client-side JavaScript reads attacker-controlled data and writes it into a dangerous DOM or JavaScript sink.

```text
Source
  |
  v
JavaScript
  |
  v
Transformation
  |
  v
Sink
  |
  v
Browser Execution
```


# DOM Source Examples

Potential sources include:

```javascript
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


# DOM Sink Examples

Security-sensitive sinks can include:

```javascript
innerHTML
outerHTML
document.write()
document.writeln()
eval()
Function()
setTimeout()
setInterval()
insertAdjacentHTML()
```


# Sink Does Not Automatically Mean Vulnerability

This:

```javascript
element.innerHTML = "<strong>Hello</strong>";
```

contains no attacker-controlled input.

The relevant question is:

```text
Can untrusted data reach the sink?
```


# Source-to-Sink Analysis

```text
Source
  |
  v
Variable
  |
  v
Transformation
  |
  v
Validation / Sanitisation?
  |
  v
Sink
```


# DOM Example

Potentially unsafe:

```javascript
const message = location.hash.substring(1);
document.getElementById("output").innerHTML = message;
```

Flow:

```text
location.hash
     |
     v
message
     |
     v
innerHTML
```


# Safer Alternative

If the value should be text:

```javascript
const message = location.hash.substring(1);
document.getElementById("output").textContent = message;
```

`textContent` treats the value as text rather than HTML.


# Start With a Marker

Before trying execution, use a unique marker:

```text
XSS_TEST_7f3a9
```

Submit:

```text
?q=XSS_TEST_7f3a9
```

Then search for it in:

```text
HTTP response

Rendered DOM

JavaScript

HTML attributes

JSON

Stored pages
```


# Why Unique Markers Help

A unique marker makes it easier to distinguish your input from:

```text
Existing application text

Other test traffic

Cached values

Unrelated reflections
```


# Identify the Output Context

This is one of the most important XSS testing steps.

Possible contexts:

```text
HTML text

HTML attribute

JavaScript string

JavaScript expression

URL

CSS

JSON

DOM
```


# HTML Text Context

Example:

```html
<div>
USER_INPUT
</div>
```

If the application outputs raw markup here, HTML tags may be interpreted.


# HTML Attribute Context

Example:

```html
<input value="USER_INPUT">
```

The important surrounding syntax is:

```text
value="
       ^
```

A test must account for the quote delimiting the attribute.


# Unquoted Attribute

Example:

```html
<input value=USER_INPUT>
```

This has different parsing behaviour from a quoted attribute.


# Single-Quoted Attribute

Example:

```html
<input value='USER_INPUT'>
```

The relevant delimiter is:

```text
'
```


# JavaScript String Context

Example:

```html
<script>
const search = 'USER_INPUT';
</script>
```

The value is inside:

```text
JavaScript
    +
single-quoted string
```

HTML payloads designed for normal page markup may not work in this context.


# Double-Quoted JavaScript String

```html
<script>
const search = "USER_INPUT";
</script>
```

The delimiter is:

```text
"
```


# JavaScript Expression Context

Example:

```html
<script>
const userId = USER_INPUT;
</script>
```

The input is not inside a quoted string.

This creates a different injection context.


# URL Context

Example:

```html
<a href="USER_INPUT">Open</a>
```

The security question becomes:

```text
Can attacker-controlled input create an unsafe navigation or executable URL?
```


# JSON Context

Example response:

```json
{
  "query": "USER_INPUT"
}
```

JSON reflection by itself is generally not XSS.

Determine:

```text
How is this JSON consumed?

Is it later inserted into HTML?

Is it embedded directly into a script block?
```


# HTML Encoding

Important characters include:

| Character | HTML Entity |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | context dependent |
| `&` | `&amp;` |


# Encoding Must Match Context

There is no single universal:

```text
XSS encoding
```

Different contexts require different handling.

```text
HTML text
    -> HTML encoding

HTML attribute
    -> Attribute-safe encoding

JavaScript
    -> JavaScript-safe serialization/encoding

URL
    -> URL validation + appropriate encoding
```


# HTML Encoding vs URL Encoding

These are different.

HTML:

```text
< -> &lt;
```

URL:

```text
< -> %3C
```

Do not treat URL encoding as a universal XSS defence.


# Browser Decoding Layers

Input can pass through multiple transformations:

```text
URL Encoding
     |
     v
Server Decoding
     |
     v
Application Processing
     |
     v
HTML Encoding
     |
     v
Browser Parsing
```


# Test What the Browser Receives

Do not rely only on what appears in the address bar.

Inspect:

```text
Raw HTTP response

Browser DOM

JavaScript execution context
```


# View Source vs DOM

The original response source and the live DOM may differ.

```text
HTTP Response
     |
     v
Browser Parses
     |
     v
JavaScript Modifies Page
     |
     v
Final DOM
```

DOM-based XSS may exist even when the dangerous markup does not appear in the original server response.


# Browser Developer Tools

Useful tabs:

```text
Elements

Console

Network

Sources
```


# Elements

Use Elements to inspect the live DOM and determine:

```text
Where input appears

Whether attributes were created

Whether tags were created

Whether JavaScript modified the DOM
```


# Console

The console can help identify:

```text
JavaScript errors

DOM behaviour

CSP violations

Source/sink behaviour
```


# Network

Use Network to determine:

```text
Which request produced the page

Redirects

JavaScript files loaded

CSP headers

API calls
```


# Burp Suite Workflow

```text
Browser
  |
  v
Burp Proxy
  |
  v
HTTP History
  |
  v
Identify Input
  |
  v
Repeater
  |
  v
Marker
  |
  v
Context Analysis
  |
  v
Controlled XSS Test
```


# Burp Repeater

Use Repeater to modify one input at a time.

Baseline:

```http
GET /search?q=hello HTTP/1.1
Host: example.com
```

Marker:

```http
GET /search?q=XSS_TEST_7f3a9 HTTP/1.1
Host: example.com
```


# Inspect Raw Response

Search for:

```text
XSS_TEST_7f3a9
```

Determine whether it appears as:

```html
XSS_TEST_7f3a9
```

or:

```html
XSS_TEST_7f3a9
```

inside an attribute, script, JSON object or other context.


# Burp Search

Search HTTP history for the marker.

This is particularly useful for stored input because the value may appear on a different endpoint.


# Burp Comparer

Comparer can help when encoding transformations are subtle.

Compare:

```text
Original Response

Modified Response
```


# Burp Decoder

Decoder can help inspect:

```text
URL encoding

HTML encoding

Base64

Hex
```

Encoding and decoding are not automatically security bypasses; use them to understand how data is transformed.


# Burp DOM Invader

DOM Invader can assist with client-side security testing and source/sink analysis.

It can be useful for:

```text
DOM XSS

postMessage testing

DOM clobbering analysis

Client-side sources and sinks
```


# DOM Invader Workflow

```text
Open Target in Burp Browser
        |
        v
Enable DOM Invader
        |
        v
Inject Canary
        |
        v
Interact With Application
        |
        v
Review Sources / Sinks
        |
        v
Validate Manually
```


# Do Not Report Tool Output Alone

A scanner or DOM analysis tool finding:

```text
source -> sink
```

should be manually validated.

Determine whether:

```text
Input is attacker controlled

Sanitisation occurs

Execution is possible

The flow is reachable
```


# Reflected XSS Workflow

```text
Parameter
   |
   v
Unique Marker
   |
   v
Marker Reflected?
   |
   +--> No -> Other Inputs
   |
   +--> Yes
          |
          v
      Find Context
          |
          v
      Check Encoding
          |
          v
    Harmless HTML Test
          |
          v
 Controlled Execution
```


# Stored XSS Workflow

```text
Input Field
   |
   v
Unique Marker
   |
   v
Save
   |
   v
Locate Render Locations
   |
   v
Determine Context
   |
   v
Controlled Payload
   |
   v
View With Relevant Role
   |
   v
Execution?
```


# DOM XSS Workflow

```text
Source
  |
  v
Can Attacker Control It?
  |
  v
Trace JavaScript
  |
  v
Sink
  |
  v
Sanitisation?
  |
  v
Browser Interpretation
  |
  v
Execution?
```


# Common HTML Proofs

A basic script element:

```html
<script>alert(1)</script>
```

An event-handler example:

```html
<img src=x onerror=alert(1)>
```

SVG:

```html
<svg onload=alert(1)>
```

Use the smallest proof appropriate for the identified context.


# Prefer Unique Proof Markers

Instead of:

```javascript
alert(1)
```

you can use:

```javascript
alert('XSS-7f3a9')
```

This makes screenshots and evidence easier to associate with the assessment.


# Do Not Use Sensitive Proofs

Avoid proof-of-concept code that:

```text
Reads real cookies

Reads localStorage tokens

Changes passwords

Performs transactions

Creates privileged users

Sends data externally
```

unless specifically authorised and required.


# Attribute Context

Suppose:

```html
<input value="USER_INPUT">
```

A test input must first determine whether the application safely handles:

```text
"
```

If quotes are encoded:

```html
<input value="&quot;">
```

breaking out of the attribute may not be possible through that value.


# Attribute Validation

Check characters individually:

```text
"

'

<

>
```

Observe exactly how each is represented in the response and DOM.


# Event Handler Context

Suppose input controls:

```html
<button onclick="USER_INPUT">
```

This is already a JavaScript-capable context.

The key questions are:

```text
Can an attacker control the attribute?

Is the value safely encoded?

Can JavaScript syntax be influenced?
```


# URL Attribute Context

Examples:

```html
<a href="USER_INPUT">

<iframe src="USER_INPUT">

<form action="USER_INPUT">
```

Review:

```text
Allowed schemes

URL parsing

Navigation restrictions

CSP

Browser behaviour
```


# Do Not Assume Every `href` Reflection Is XSS

A value such as:

```html
<a href="/profile?next=USER_INPUT">
```

may be safely URL encoded.

Context determines exploitability.


# Script Block Context

Example:

```html
<script>
var username = 'USER_INPUT';
</script>
```

Inspect:

```text
Quote handling

Backslash handling

Newline handling

HTML script termination

JavaScript encoding
```


# Safe JavaScript Data Embedding

Prefer framework-supported serialization.

For example, safely serialize structured data rather than concatenating untrusted strings into executable JavaScript.


# JavaScript Template Literals

Example:

```javascript
const message = `USER_INPUT`;
```

Template literals have their own syntax and should not be treated as equivalent to single-quoted strings.


# Client-Side Templates

Review frameworks that render data client-side.

The relevant flow may be:

```text
API Response
    |
    v
JavaScript Object
    |
    v
Template
    |
    v
DOM
```


# Framework Auto-Escaping

Modern frameworks commonly provide escaping by default.

Examples include:

```text
React

Angular

Vue

Django templates

Jinja2

Twig

Razor
```

Risk often appears when developers bypass normal escaping.


# React

Normal JSX:

```jsx
<div>{userInput}</div>
```

is generally rendered as text.

A high-risk API is:

```jsx
dangerouslySetInnerHTML
```


# React Source Search

```bash
rg -n 'dangerouslySetInnerHTML' -g '*.js' -g '*.jsx' -g '*.ts' -g '*.tsx' .
```


# Angular

Review APIs and patterns that intentionally bypass sanitisation.

Search:

```bash
rg -ni 'bypassSecurityTrust|innerHTML' -g '*.ts' -g '*.html' .
```


# Vue

Normal interpolation:

```html
{{ userInput }}
```

is generally escaped.

Review:

```html
v-html
```

because it intentionally renders HTML.


# Vue Source Search

```bash
rg -n 'v-html' -g '*.vue' .
```


# Server-Side Templates

Search for explicit safe/raw rendering functionality.

Examples depend on the template engine.

The important pattern is:

```text
Untrusted Data
      |
      v
Escaping Disabled
      |
      v
HTML Output
```


# `innerHTML`

Potentially dangerous:

```javascript
element.innerHTML = userInput;
```

Safer for text:

```javascript
element.textContent = userInput;
```


# `outerHTML`

Review:

```javascript
element.outerHTML = userInput;
```

because supplied markup may replace the element.


# `insertAdjacentHTML`

Review:

```javascript
element.insertAdjacentHTML("beforeend", userInput);
```

because it parses the supplied value as HTML.


# `document.write`

Review:

```javascript
document.write(userInput);
```

because it writes markup into the document parser.


# `eval`

Review:

```javascript
eval(userInput);
```

This is a JavaScript execution sink and should generally not receive untrusted data.


# `Function`

Review:

```javascript
new Function(userInput)();
```

This similarly interprets strings as JavaScript.


# `setTimeout`

Potentially unsafe:

```javascript
setTimeout(userInput, 1000);
```

Safer:

```javascript
setTimeout(function () {
    doSomething();
}, 1000);
```


# `setInterval`

Potentially unsafe:

```javascript
setInterval(userInput, 1000);
```

Avoid string-based execution.


# jQuery

Legacy applications may contain sinks such as:

```javascript
.html()
.append()
.after()
.before()
```

Security depends on what data reaches them and how the API processes the value.


# Search JavaScript for Sinks

```bash
rg -ni 'innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function|setTimeout\(|setInterval\(' -g '*.js' -g '*.ts' .
```


# Search JavaScript for Sources

```bash
rg -ni 'location\.href|location\.search|location\.hash|document\.referrer|window\.name|localStorage|sessionStorage|postMessage' -g '*.js' -g '*.ts' .
```


# Search Source and Sink Together

First find sources:

```bash
rg -n 'location\.(search|hash|href)|document\.referrer' src/
```

Then find sinks:

```bash
rg -n 'innerHTML|outerHTML|insertAdjacentHTML|document\.write' src/
```

Trace candidate flows manually.


# Example Source Review

```javascript
const params = new URLSearchParams(location.search);
const name = params.get("name");

document.querySelector("#welcome").innerHTML =
    "Welcome " + name;
```

Flow:

```text
location.search
      |
      v
URLSearchParams
      |
      v
name
      |
      v
innerHTML
```


# Safer Version

```javascript
const params = new URLSearchParams(location.search);
const name = params.get("name");

document.querySelector("#welcome").textContent =
    "Welcome " + name;
```


# Sanitisation

If HTML must intentionally be supported, use a well-maintained sanitisation library appropriate to the application.

Do not attempt to create a home-grown sanitizer using a few string replacements.


# Sanitisation Is Different From Encoding

```text
Encoding
   |
   v
Treat Input as Text
```

versus:

```text
Sanitisation
   |
   v
Allow Some Markup
   |
   v
Remove Unsafe Constructs
```


# Rich Text

Applications may intentionally permit:

```html
<b>

<i>

<p>

<ul>

<li>
```

but need to reject dangerous markup and attributes.

This is a sanitisation problem rather than simple text encoding.


# DOMPurify

DOMPurify is a commonly used HTML sanitisation library for browser environments.

Use it according to the project's documented configuration and threat model.

Do not weaken sanitisation by subsequently modifying sanitized markup in unsafe ways.


# Sanitisation Foot-Guns

Conceptually:

```text
Untrusted HTML
      |
      v
Sanitise
      |
      v
Safe HTML
      |
      v
Unsafe String Manipulation
      |
      v
Danger Reintroduced
```


# Content Security Policy

Content Security Policy (CSP) can reduce the impact of XSS, but should normally be treated as defence in depth rather than a replacement for safe output handling.


# Check CSP Header

```bash
curl -I https://example.com/
```

Look for:

```http
Content-Security-Policy:
```


# Example CSP

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```


# CSP Report-Only

This header:

```http
Content-Security-Policy-Report-Only:
```

does not enforce the policy.

It reports violations for monitoring/testing purposes.


# CSP Questions

Review:

```text
Is CSP enforced?

What is script-src?

Are nonces used?

Are hashes used?

Is unsafe-inline allowed?

Is unsafe-eval allowed?

Are broad external script origins trusted?

Are wildcard sources used?

Are dangerous schemes allowed?
```


# `unsafe-inline`

A policy containing:

```text
'unsafe-inline'
```

may permit inline JavaScript depending on the rest of the policy.

Its significance must be evaluated in the complete CSP.


# `unsafe-eval`

A policy containing:

```text
'unsafe-eval'
```

permits certain string-to-code JavaScript operations.

It weakens CSP but is not, by itself, proof of XSS.


# Nonces

Example:

```html
<script nonce="RANDOM_VALUE">
```

with:

```http
Content-Security-Policy: script-src 'nonce-RANDOM_VALUE'
```

A nonce should be unpredictable and generated per response.


# Do Not Report CSP Alone as XSS

This:

```text
CSP contains unsafe-inline
```

does not demonstrate:

```text
XSS vulnerability
```

It is a hardening observation unless a meaningful security consequence is established.


# XSS With CSP

If XSS exists but CSP blocks a simple inline proof:

```text
Input Injection Exists
       |
       v
Browser Creates Markup
       |
       v
CSP Blocks Script Execution
```

Document both facts accurately.

Do not claim successful JavaScript execution if CSP prevented it.


# CSP Console Errors

Browser console may show:

```text
Refused to execute inline script...
```

This is useful evidence that CSP affected the test.


# Trusted Types

Trusted Types can reduce DOM XSS risk in supported applications by restricting assignment to dangerous DOM sinks.

Review:

```http
Content-Security-Policy: require-trusted-types-for 'script'
```

where applicable.


# HTTPOnly Cookies

`HttpOnly` prevents JavaScript from directly reading a cookie.

Example:

```http
Set-Cookie: session=...; HttpOnly; Secure
```

This reduces one common XSS impact but does not fix XSS.


# XSS Impact Is Not Only Cookie Theft

XSS can potentially perform actions available to the victim's browser context.

Depending on the application:

```text
Read page data

Modify page content

Send same-origin requests

Interact with APIs

Access non-HttpOnly browser storage

Perform actions as the user
```

Therefore:

```text
Session cookie is HttpOnly
```

does not mean:

```text
XSS has no impact.
```


# SameSite Cookies

SameSite is primarily a cross-site request control and does not prevent JavaScript already executing within the application's origin from interacting with same-origin application functionality.


# Secure Cookies

The `Secure` attribute ensures a cookie is sent only over secure transport.

It does not remediate XSS.


# Stored XSS in File Names

Applications may display uploaded file names.

Example:

```text
report.pdf
```

Test whether filename values are:

```text
Stored

Reflected

HTML encoded

Displayed to other users
```


# File Name Testing

Use a harmless marker first.

For example:

```text
XSS_TEST_7f3a9.pdf
```

Upload normally and determine where the filename is rendered.


# File Name Context

Possible render locations:

```text
Upload confirmation

File list

Administrative portal

Download page

Audit history
```


# Do Not Confuse File Content With Filename XSS

These are separate surfaces:

```text
Filename handling

File content handling

Content-Type handling

Inline rendering
```


# Stored XSS in Logs

Some applications display request data in web-based administrative log viewers.

Potential stored values include:

```text
User-Agent

Referer

URL

Search term

Username
```

Use harmless markers first and only test administrator-facing execution where authorised.


# Blind XSS Concept

Blind XSS occurs when supplied input executes in a location the tester cannot directly view, often in a different workflow or privileged interface.

Conceptually:

```text
Input Submitted
      |
      v
Stored / Logged
      |
      v
Different User Opens Record
      |
      v
Execution
```


# Blind XSS Testing

Blind XSS often relies on an external callback service.

Because this causes an out-of-band interaction, use only infrastructure and domains approved for the assessment.

Do not send real application data in callbacks.


# Safe Blind XSS Design

A controlled callback should prove only what is necessary, such as:

```text
Unique test ID

Target identifier

Execution timestamp
```

Avoid collecting:

```text
Cookies

Tokens

Page contents

Personal data
```


# postMessage

`postMessage` is another important client-side input source.

Listener example:

```javascript
window.addEventListener("message", function (event) {
    output.innerHTML = event.data;
});
```

Questions:

```text
Is event.origin validated?

Is event.source validated where needed?

How is event.data used?

Does it reach a dangerous sink?
```


# postMessage Origin Validation

Weak:

```javascript
if (event.origin.includes("example.com")) {
```

Prefer exact expected origins where appropriate.

The exact implementation depends on the application's architecture.


# URL Fragment

Example:

```text
https://example.com/#hello
```

The fragment:

```text
#hello
```

is normally not sent to the server.

Client-side JavaScript can still read:

```javascript
location.hash
```

making it relevant for DOM XSS.


# Query String

```text
https://example.com/?q=hello
```

JavaScript can read:

```javascript
location.search
```


# Referrer

JavaScript may read:

```javascript
document.referrer
```

Whether an attacker can meaningfully control it depends on navigation and browser behaviour.


# localStorage

Example:

```javascript
const name = localStorage.getItem("name");
output.innerHTML = name;
```

The relevant question is:

```text
Can an attacker cause malicious data to enter localStorage?
```


# sessionStorage

Same principle:

```javascript
sessionStorage.getItem(...)
```

Storage is a source only if untrusted values can reach it.


# Mutation XSS

Browser parsing and HTML sanitisation can interact in complex ways.

Do not assume:

```text
Sanitised string looked safe before DOM insertion
```

always means:

```text
Resulting DOM is safe.
```

For rich HTML functionality, rely on mature sanitisation libraries and browser-aware testing.


# Multi-Context Reflection

The same input can appear multiple times:

```html
<h1>USER_INPUT</h1>

<input value="USER_INPUT">

<script>
const q = "USER_INPUT";
</script>
```

Each reflection has a different security context.


# Test Every Reflection

Do not stop after determining that one reflection is safely encoded.

Another occurrence may be unsafe.


# Reflection in HTML Comment

Example:

```html
<!-- USER_INPUT -->
```

This is a distinct parser context.

Determine whether input can alter comment structure before making any security conclusion.


# Reflection in CSS

Example:

```html
<style>
.profile {
    background: USER_INPUT;
}
</style>
```

CSS injection and modern browser security behaviour differ from standard JavaScript XSS.

Analyse the actual impact rather than labeling every CSS-context injection as XSS.


# Meta Tags

Example:

```html
<meta content="USER_INPUT">
```

Again, context and browser interpretation determine impact.


# Template Injection vs XSS

Do not confuse:

```text
Server-Side Template Injection
```

with:

```text
Cross-Site Scripting
```

An input such as:

```text
{{7*7}}
```

may be relevant to template processing, while XSS concerns browser-side execution.

See:

[SSTI Notes](../web/ssti.md)


# HTML Injection vs XSS

HTML injection:

```html
<b>Injected</b>
```

demonstrates attacker-controlled markup.

XSS requires an executable browser context.

Relationship:

```text
HTML Injection
      |
      +--> Markup Only
      |
      +--> Executable Context
              |
              v
             XSS
```


# Open Redirect vs XSS

If attacker input controls:

```text
Location:
```

or a navigation URL, the issue may be open redirect rather than XSS.

See:

[Open Redirect Notes](../web/open-redirect.md)


# XSS vs JavaScript URL

A controllable URL may require separate analysis of:

```text
Allowed schemes

Browser behaviour

CSP

User interaction
```

Do not classify solely from the string value.


# XSS vs CRLF Injection

If input affects HTTP headers rather than HTML/DOM output, investigate response splitting or header injection separately.


# XSS vs SQL Injection

A quote producing an error does not tell you which interpreter is involved.

Always determine the processing context:

```text
Browser?

SQL?

Shell?

Template?

LDAP?

XML?
```


# Scanner Findings

Automated scanners may report:

```text
Possible reflected XSS

Input reflected

Potential DOM sink

CSP weakness
```

These are candidates requiring validation.


# Scanner False Positives

Common reasons:

```text
Input HTML encoded

Reflection occurs inside JSON

Reflection occurs in non-executable text

CSP blocks execution

Sanitiser removes dangerous attributes

Input never reaches browser DOM
```


# Scanner False Negatives

Automated scanning can miss:

```text
Stored XSS

Multi-step workflows

Role-dependent rendering

DOM XSS

JavaScript-generated contexts

Blind XSS

Second-order rendering
```


# Application Workflow Matters

Example:

```text
Create User
   |
   v
Set Display Name
   |
   v
No Execution on Profile
   |
   v
Admin Opens User Management
   |
   v
Execution
```

Testing only the submission response would miss the vulnerability.


# Multi-Role Testing

For stored input, consider:

```text
Attacker role

Same user

Different standard user

Administrator

Support user
```

Only where these roles are available and authorised.


# XSS and Access Control

Impact depends on who can create the payload and who can trigger it.

Example:

```text
Admin -> Admin
```

may have lower practical impact than:

```text
Unauthenticated -> Administrator
```


# Impact Questions

Ask:

```text
Who can supply the input?

Who receives the output?

Does execution require interaction?

Which origin executes the script?

What functionality is available to the victim?

Does CSP restrict execution?

Are sensitive APIs accessible from the browser?

Does the application contain privileged administrative actions?
```


# Do Not Overstate Impact

Do not automatically claim:

```text
Account takeover

Credential theft

Server compromise
```

from every XSS.

Explain the impact supported by the tested application.


# Source-Code Review

Search for output-related functions.

JavaScript:

```bash
rg -ni 'innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function' -g '*.js' -g '*.ts' .
```

React:

```bash
rg -n 'dangerouslySetInnerHTML' -g '*.jsx' -g '*.tsx' -g '*.js' -g '*.ts' .
```

Vue:

```bash
rg -n 'v-html' -g '*.vue' .
```

Angular:

```bash
rg -ni 'bypassSecurityTrust|innerHTML' -g '*.ts' -g '*.html' .
```


# Search for Template Raw Output

Framework syntax differs.

Look for mechanisms that mean:

```text
Do not escape this value.
```

Then determine whether attacker-controlled input can reach them.


# Search for Sanitisation

```bash
rg -ni 'DOMPurify|sanitize|sanitise|escapeHtml|encodeForHTML' .
```

A sanitisation function name does not prove correct use.

Review configuration and data flow.


# Search Sources

```bash
rg -ni 'location\.search|location\.hash|location\.href|document\.referrer|window\.name|localStorage|sessionStorage' .
```


# Trace Candidate

Suppose:

```text
app.js:18: const value = location.hash.substring(1);
app.js:47: output.innerHTML = value;
```

Inspect context:

```bash
rg -n -C 6 'location\.hash|innerHTML' app.js
```


# Representative Source Review

```javascript
const value = location.hash.substring(1);

if (value.length < 100) {
    output.innerHTML = value;
}
```

The length check:

```text
value.length < 100
```

does not provide HTML sanitisation.

The important flow remains:

```text
Attacker-Controlled Fragment
        |
        v
       value
        |
        v
     innerHTML
```


# Source Review Interpretation

Do not conclude only:

```text
innerHTML found.
```

Document:

```text
Source

Transformation

Validation

Sink

Reachability

Browser behaviour
```


# Example Candidate Classification

```text
location.hash -> textContent
```

Generally lower risk for XSS.

```text
location.hash -> innerHTML
```

Security-relevant candidate.

```text
constant string -> innerHTML
```

Not attacker-controlled.

```text
sanitised rich text -> innerHTML
```

Requires sanitizer/configuration review.


# False Positive - Encoded Reflection

Input:

```html
<script>alert(1)</script>
```

Response:

```html
&lt;script&gt;alert(1)&lt;/script&gt;
```

Browser renders it as text.

No execution is demonstrated.


# False Positive - JSON Response

Response:

```json
{
  "query": "<script>alert(1)</script>"
}
```

This alone is not XSS.

Determine how the JSON is consumed.


# False Positive - Dead JavaScript

A dangerous sink may exist in:

```text
Unused file

Old bundle

Feature disabled

Unreachable function
```

Confirm reachability.


# False Positive - Sanitised Flow

A source may reach:

```text
DOMPurify.sanitize()
```

before:

```text
innerHTML
```

Review whether sanitisation is correctly configured before concluding vulnerability.


# False Positive - CSP

Input may create an inline script element but CSP may prevent execution.

Report only the behaviour actually demonstrated.


# Common Testing Mistake - Payload Lists First

Bad:

```text
Copy 500 XSS payloads
      |
      v
Send Them Everywhere
```

Better:

```text
Marker
  |
  v
Context
  |
  v
Encoding
  |
  v
Small Context-Specific Test
```


# Common Testing Mistake - Ignoring the DOM

Server response may look safe while JavaScript later creates unsafe markup.


# Common Testing Mistake - Testing Only Search

XSS can occur in:

```text
Profiles

Comments

File names

Admin panels

Headers

Logs

Imports

APIs

Client-side routing
```


# Common Testing Mistake - Testing Only `<script>`

A blocked script element does not prove the context is safe.

Understand browser parsing and the exact output context.


# Common Testing Mistake - Treating Filtering as Encoding

Removing:

```text
<script>
```

does not safely encode arbitrary HTML.


# Common Testing Mistake - Ignoring Stored Locations

A value may be safe on one page and unsafe elsewhere.


# Common Testing Mistake - Reporting Reflection

Reflection alone is not XSS.


# Common Testing Mistake - Cookie Theft as PoC

Do not use sensitive session theft as routine proof.

A harmless unique execution marker is normally enough.


# Evidence Collection

Record:

```text
Finding ID

Endpoint

Method

Parameter / field

Authentication context

XSS type

Input value

Storage location if applicable

Render location

Output context

Relevant response

Relevant DOM

Browser

CSP

Victim role

Execution evidence

Timestamp
```


# Reflected XSS Evidence

A strong evidence chain:

```text
1. Baseline request.

2. Marker reflection.

3. Output context.

4. Controlled payload.

5. Browser execution.

6. Relevant CSP behaviour.

7. Screenshot / response evidence.
```


# Stored XSS Evidence

Capture:

```text
Submission request

Stored value

Page where value is rendered

Role viewing the value

Execution proof

Relevant response/DOM
```


# DOM XSS Evidence

Capture:

```text
Source

Attacker-controlled value

JavaScript data flow

Sink

DOM result

Execution
```


# Screenshot Quality

A useful screenshot should show enough context to identify:

```text
Application

Affected feature

Unique PoC marker

Execution
```

Do not expose unnecessary sensitive data.


# Reporting Example - Reflected XSS

Weak:

> The `q` parameter is vulnerable to XSS.

Better:

> The `q` parameter on the search endpoint is reflected into the HTML response without context-appropriate output encoding. A controlled event-handler payload supplied through the parameter was inserted into the resulting DOM and executed in the application's origin when the response was rendered in the browser.


# Reporting Example - Stored XSS

> The profile display name is stored by the application and later rendered without context-appropriate encoding in the administrative user-management interface. A value submitted by a standard user executed JavaScript when the corresponding record was viewed using the authorised administrator test account.


# Reporting Example - DOM XSS

> Client-side code reads attacker-controlled data from `location.hash` and assigns the resulting value to `innerHTML` without sanitisation. A controlled fragment value therefore produced executable markup in the live DOM without requiring the value to be reflected by the server.


# Reporting Example - HTML Injection Only

> The tested parameter is rendered as raw HTML and allows attacker-controlled markup to alter page presentation. JavaScript execution was not demonstrated during testing, so the issue was classified as HTML injection rather than cross-site scripting.


# Reporting Example - CSP Prevented Execution

> The application reflects attacker-controlled markup into the response without HTML encoding. The supplied markup was created in the DOM; however, the tested inline JavaScript execution was blocked by the application's enforced Content Security Policy. No successful JavaScript execution was demonstrated using the tested technique.


# Remediation

Primary principle:

```text
Apply context-appropriate output encoding.
```


# HTML Text

For values intended to be text:

```text
Encode HTML-sensitive characters.
```

Prefer framework APIs that escape by default.


# DOM Text

Prefer:

```javascript
textContent
```

instead of:

```javascript
innerHTML
```

when HTML rendering is unnecessary.


# Rich HTML

If users are intentionally allowed to submit HTML:

```text
Use a mature HTML sanitiser.

Define allowed elements.

Define allowed attributes.

Keep the sanitiser updated.

Test configuration.
```


# JavaScript Context

Avoid dynamically constructing executable JavaScript with untrusted data.

Prefer:

```text
Structured data

DOM APIs

Safe serialization

Event listeners
```


# URL Context

Validate:

```text
Allowed schemes

Allowed destinations

Expected URL structure
```

and apply appropriate URL handling.


# Framework Defaults

Do not disable framework escaping unless there is a clear requirement and the data has been appropriately sanitised.


# CSP

Deploy a strong CSP as defence in depth.

Prefer policies based on:

```text
Nonces

Hashes

Explicit script origins
```

rather than relying on broad inline-script allowances.


# Cookies

Use:

```text
HttpOnly

Secure

Appropriate SameSite
```

for session cookies.

These reduce some impact but do not remediate XSS.


# Trusted Types

Where appropriate for the application, consider Trusted Types to reduce dangerous DOM sink usage.


# Root Cause Review

After finding one XSS issue, search for the underlying pattern.

Examples:

```text
innerHTML with untrusted input

dangerouslySetInnerHTML

v-html

raw template output

unsafe rich-text rendering
```


# Retesting

Retest the exact original input location first.

```text
Original Input
     |
     v
Original Render Location
     |
     v
Original XSS Context
     |
     v
No Execution
```


# Verify Why It No Longer Executes

Good remediation should produce a clear safe behaviour.

For example:

Input:

```html
<img src=x onerror=alert(1)>
```

Rendered as text:

```text
<img src=x onerror=alert(1)>
```

rather than creating an image element.


# Inspect the DOM During Retest

Do not rely only on:

```text
No alert appeared.
```

Inspect whether the application:

```text
Encoded the value

Sanitised the value

Removed dangerous attributes

Changed to a safe DOM API
```


# Retest Alternative Context Characters

If the fix was encoding-related, verify handling of:

```text
<

>

"

'

&
```


# Retest Stored Copies

For stored XSS:

```text
Old malicious record

Newly created record

Every known render location
```

may need review.

Historical stored values can remain dangerous after code changes depending on how they are rendered.


# Retest Multiple Roles

If the original issue affected:

```text
Administrator
```

retest the administrative rendering path, not only the attacker's own page.


# Retest Root Cause

If one instance of:

```javascript
innerHTML = userInput
```

was fixed, search for equivalent patterns elsewhere.


# Regression Tests

Useful application tests:

```text
HTML-sensitive input renders as text.

Stored values remain safely encoded.

Client-side routing does not create unsafe DOM.

Rich HTML is sanitised.

Unsafe attributes are removed.

Normal Unicode input still works.
```


# Practical XSS Checklist

## Input Discovery

- [ ] Query parameters reviewed
- [ ] POST fields reviewed
- [ ] JSON properties reviewed
- [ ] Path parameters reviewed
- [ ] Profile fields reviewed
- [ ] Comments/messages reviewed
- [ ] File names reviewed
- [ ] Search fields reviewed
- [ ] Administrative workflows reviewed
- [ ] Headers/logging workflows considered
- [ ] Client-side URL sources reviewed

## Reflection

- [ ] Unique marker used
- [ ] Raw response searched
- [ ] Live DOM inspected
- [ ] Every reflection identified
- [ ] Stored render locations identified

## Context

- [ ] HTML text
- [ ] Double-quoted attribute
- [ ] Single-quoted attribute
- [ ] Unquoted attribute
- [ ] JavaScript string
- [ ] JavaScript expression
- [ ] URL
- [ ] JSON
- [ ] DOM sink

## Character Handling

- [ ] `<` tested
- [ ] `>` tested
- [ ] `"` tested
- [ ] `'` tested
- [ ] `&` tested
- [ ] Encoding observed
- [ ] Browser parsing confirmed

## Reflected XSS

- [ ] Baseline captured
- [ ] Marker reflected
- [ ] Context identified
- [ ] Encoding understood
- [ ] Harmless execution tested
- [ ] Execution reproduced

## Stored XSS

- [ ] Input stored
- [ ] Render location identified
- [ ] Same-user view tested where relevant
- [ ] Cross-user view tested where authorised
- [ ] Administrative view tested where authorised
- [ ] Every output context considered

## DOM XSS

- [ ] Source identified
- [ ] Attacker control confirmed
- [ ] Data flow traced
- [ ] Transformations reviewed
- [ ] Sink identified
- [ ] Sanitisation reviewed
- [ ] Reachability confirmed
- [ ] Browser execution tested

## CSP

- [ ] CSP header checked
- [ ] Enforced vs report-only identified
- [ ] `script-src` reviewed
- [ ] Nonces reviewed
- [ ] Hashes reviewed
- [ ] `unsafe-inline` noted where relevant
- [ ] `unsafe-eval` noted where relevant
- [ ] Console CSP violations reviewed
- [ ] CSP not treated as root-cause remediation

## Source Review

- [ ] `innerHTML` searched
- [ ] `outerHTML` searched
- [ ] `insertAdjacentHTML` searched
- [ ] `document.write` searched
- [ ] `eval` searched
- [ ] `Function` searched
- [ ] Framework unsafe rendering APIs searched
- [ ] Sources searched
- [ ] Source-to-sink flow traced
- [ ] Sanitisation reviewed

## Evidence

- [ ] Endpoint recorded
- [ ] Parameter/field recorded
- [ ] Authentication context recorded
- [ ] XSS type recorded
- [ ] Payload recorded
- [ ] Response captured
- [ ] DOM captured
- [ ] Execution captured
- [ ] Victim role recorded
- [ ] CSP behaviour recorded
- [ ] Sensitive values redacted

## Retest

- [ ] Original input retested
- [ ] Original render location retested
- [ ] Browser DOM inspected
- [ ] Stored copies considered
- [ ] Multiple roles considered
- [ ] Equivalent sinks reviewed
- [ ] Normal functionality verified


# XSS Type Comparison

| Type | Input Location | Execution Location | Typical Testing Approach |
|---|---|---|---|
| Reflected | Current request | Immediate response | Marker -> context -> execution |
| Stored | Persisted application data | Later page/view | Store -> locate render -> execution |
| DOM-based | Browser-controlled source | Client-side DOM | Source -> data flow -> sink |


# Context Matrix

| Context | Example | Main Question |
|---|---|---|
| HTML text | `<div>INPUT</div>` | Is markup encoded? |
| Attribute | `<input value="INPUT">` | Can the attribute boundary be altered? |
| Script string | `var x='INPUT'` | Is JavaScript string encoding correct? |
| Script expression | `var x=INPUT` | Can JavaScript syntax be controlled? |
| URL | `<a href="INPUT">` | Are unsafe schemes/destinations possible? |
| JSON | `{"x":"INPUT"}` | How is the JSON later consumed? |
| DOM | `innerHTML = input` | Can attacker data reach an HTML sink? |


# Source and Sink Matrix

| Source | Sink | Review Priority |
|---|---|---:|
| `location.hash` | `innerHTML` | High |
| `location.search` | `insertAdjacentHTML` | High |
| `document.referrer` | `document.write` | High |
| `postMessage` | `innerHTML` | High |
| `localStorage` | `innerHTML` | Depends on storage control |
| Constant | `innerHTML` | Low |
| User input | `textContent` | Usually lower for XSS |


# Result Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| Marker reflected | Input reaches response | XSS |
| `<b>` renders bold | HTML injection | JavaScript execution |
| Quote changes DOM | Context may be controllable | XSS without execution |
| Event handler executes | Executable markup | Broader impact beyond tested context |
| Value stored | Persistence | Stored XSS |
| Source reaches sink | DOM XSS candidate | Exploitability without attacker control |
| CSP blocks script | Defence is active | Underlying output handling is safe |
| `innerHTML` found | Dangerous sink exists | Vulnerability |
| `dangerouslySetInnerHTML` found | Unsafe-rendering API used | Attacker-controlled input |
| Scanner reports XSS | Candidate | Confirmed vulnerability |


# Remediation Matrix

| Problem | Preferred Approach |
|---|---|
| Text inserted into HTML | Context-aware output encoding |
| Text inserted into DOM | `textContent` |
| User HTML required | Mature HTML sanitisation |
| Dynamic JavaScript construction | Avoid string-to-code patterns |
| Dynamic URL | Scheme/destination validation |
| Raw framework rendering | Restore safe auto-escaping |
| DOM sinks | Replace with safer APIs |
| Weak CSP | Strengthen as defence in depth |
| Sensitive session cookies | `HttpOnly`, `Secure`, appropriate `SameSite` |


# Burp Suite Quick Workflow

```text
Proxy
  |
  v
HTTP History
  |
  v
Repeater
  |
  v
Unique Marker
  |
  v
Search Response
  |
  v
Identify Context
  |
  v
Check Character Encoding
  |
  v
Controlled PoC
  |
  v
Browser Validation
```


# DOM XSS Quick Workflow

```text
URL / postMessage / Storage
          |
          v
        Source
          |
          v
    JavaScript Variable
          |
          v
     Transformations
          |
          v
      Sanitisation?
          |
          v
         Sink
          |
          v
       Live DOM
          |
          v
      Execution?
```


# Stored XSS Quick Workflow

```text
Controlled Test Account
        |
        v
Submit Unique Marker
        |
        v
Value Stored
        |
        v
Find Render Locations
        |
        v
Determine Each Context
        |
        v
Submit Minimal PoC
        |
        v
View With Relevant Role
        |
        v
Capture Evidence
```


# Secure Rendering Model

```text
                    UNTRUSTED DATA
                          |
                          v
                  DETERMINE PURPOSE
                    /            \
                   /              \
                  v                v
              TEXT ONLY         RICH HTML
                  |                |
                  v                v
           SAFE TEXT API       SANITISER
                  |                |
                  v                v
            ENCODED TEXT      ALLOWED HTML
                   \              /
                    \            /
                     +----------+
                          |
                          v
                        DOM
```


# Final Testing Principle

The key XSS question is:

```text
Can attacker-controlled data reach an executable browser context?
```

A strong testing workflow is:

```text
Input
  |
  v
Unique Marker
  |
  v
Find Reflection / Storage / Source
  |
  v
Identify Context
  |
  v
Understand Encoding
  |
  v
Understand Browser Parsing
  |
  v
Minimal Context-Specific PoC
  |
  v
Execution?
  |
  +--> No
  |     |
  |     v
  |  Document Candidate / HTML Injection / Safe Handling
  |
  +--> Yes
        |
        v
   Determine Victim
        |
        v
   Determine Impact
        |
        v
      Evidence
        |
        v
    Remediation
        |
        v
      Retest
```

For every candidate ask:

```text
Where does the input originate?

Is the attacker able to control it?

Is it reflected immediately or stored?

Where does it appear?

What parser context is involved?

Which characters are encoded?

Is HTML actually created?

Is JavaScript execution possible?

Does the browser DOM differ from the server response?

Does JavaScript move the value into another sink?

Does CSP affect execution?

Who can submit the value?

Who views the value?

Does the issue cross privilege boundaries?

Could the observation only be HTML injection?

Could framework auto-escaping already make it safe?

Is sanitisation being used?

Can the behaviour be reproduced?

What is the minimum safe proof?

Has the root cause been fixed?
```

Do not stop at:

```text
Payload reflected.
```

Move through:

```text
REFLECTION
    |
    v
CONTEXT
    |
    v
PARSING
    |
    v
EXECUTION
    |
    v
IMPACT
```

That distinction turns a payload collection into a defensible XSS testing methodology.


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [SQL Injection Cheatsheet](sql-injection.md)
- [Content Discovery Cheatsheet](content-discovery.md)
- [curl Cheatsheet](curl.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [HTML Injection](../web/html-injection.md)
- [Authentication](../web/authentication.md)
- [Authorisation](../web/authorisation.md)
- [CSP](../web/http-security-headers.md)
- [Open Redirect](../web/open-redirect.md)
- [SSTI](../web/ssti.md)
- [File Upload](../web/file-upload.md)
- [API Security](../web/api-security.md)
- [JavaScript Analysis](../web/reconnaissance/javascript-analysis.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - Cross-Site Scripting](https://portswigger.net/web-security/cross-site-scripting){ target="_blank" rel="noopener noreferrer" }
- [PortSwigger Web Security Academy - DOM-Based Vulnerabilities](https://portswigger.net/web-security/dom-based){ target="_blank" rel="noopener noreferrer" }
- [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP DOM Based XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for Reflected Cross Site Scripting](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/01-Testing_for_Reflected_Cross_Site_Scripting){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for Stored Cross Site Scripting](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting){ target="_blank" rel="noopener noreferrer" }
- [MDN - Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP){ target="_blank" rel="noopener noreferrer" }
- [DOMPurify](https://github.com/cure53/DOMPurify){ target="_blank" rel="noopener noreferrer" }


!!! tip "Start with context, not payload lists"

    A unique marker and five minutes of context analysis are usually more valuable than blindly sending hundreds of XSS strings. Determine where the value appears and how the browser parses it before selecting a proof.


!!! tip "Inspect both response and DOM"

    The server response shows what the application returned. The live DOM shows what the browser ultimately constructed after parsing and JavaScript execution. DOM-based vulnerabilities may only become apparent in the latter.


!!! tip "Separate HTML injection from XSS"

    If attacker-controlled markup changes the page but JavaScript execution cannot be demonstrated, describe the observed behaviour accurately as HTML injection rather than automatically calling it XSS.


!!! tip "Trace source to sink"

    During client-side review, a dangerous sink such as `innerHTML` is only part of the story. Identify whether attacker-controlled data can actually reach that sink, what transformations occur and whether sanitisation is applied.


!!! warning "Keep the proof harmless"

    An alert or similarly harmless unique execution marker is normally sufficient to establish XSS. Avoid accessing real cookies, tokens, page data or privileged functionality simply to make the proof more dramatic.


!!! warning "CSP is defence in depth"

    A Content Security Policy can substantially reduce XSS impact, but it should not replace context-appropriate encoding, safe DOM APIs and sanitisation. Document separately whether unsafe injection exists and whether CSP prevents the tested execution path.
