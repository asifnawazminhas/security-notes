# HTML Injection

HTML Injection occurs when attacker-controlled input is inserted into an HTML document without appropriate output encoding or sanitisation.

Unlike Cross-Site Scripting, HTML Injection does not necessarily require JavaScript execution.

A vulnerable application may allow an attacker to inject arbitrary HTML elements that alter:

```text
Page content
Page structure
Links
Forms
Images
Headings
User interface elements
Displayed information
```

A simplified flow is:

```text
User-Controlled Input
        ↓
Application
        ↓
Input Returned or Stored
        ↓
HTML Response
        ↓
Browser Parses Injected Markup
        ↓
Page Content Modified
```

HTML Injection can therefore be useful both as a vulnerability in its own right and as an indication that output handling should be investigated further for Cross-Site Scripting.

!!! warning "Authorised Security Testing"
    Perform HTML Injection testing only against applications included in the authorised assessment scope. Start with harmless visual markers and avoid deceptive forms, external content or actions that could affect real users.

---

# HTML Injection vs XSS

HTML Injection and Cross-Site Scripting are closely related, but they are not identical.

HTML Injection:

```text
Attacker Input
      ↓
HTML Parsing
      ↓
Page Structure Changes
```

Cross-Site Scripting:

```text
Attacker Input
      ↓
Browser Execution Context
      ↓
JavaScript Execution
```

For example:

```html
<h1>HTML-INJECTION-TEST</h1>
```

may demonstrate HTML Injection.

It does not by itself demonstrate JavaScript execution.

The distinction is important when reporting findings.

Do not report:

```text
Cross-Site Scripting
```

when the demonstrated behaviour is only:

```text
HTML Injection
```

---

# Why HTML Injection Matters

Even without JavaScript execution, injected HTML may affect the security and integrity of an application.

Potential consequences include:

```text
Page content manipulation
UI manipulation
Misleading information
Link injection
Form injection
Content spoofing
Brand impersonation
Phishing opportunities
User confusion
Security warning suppression
Modification of application presentation
```

The actual impact depends heavily on where the injection occurs and who can cause other users to view it.

---

# Types of HTML Injection

Useful categories include:

```text
Reflected HTML Injection
Stored HTML Injection
DOM-Based HTML Injection
Attribute Injection
```

---

# Reflected HTML Injection

Reflected HTML Injection occurs when input from the request is immediately included in the response.

Example:

```http
GET /search?q=AM-HTML-TEST HTTP/1.1
Host: target.example
```

The response may contain:

```html
<p>Search results for AM-HTML-TEST</p>
```

Start with a harmless marker:

```text
AM-HTML-987654
```

Then determine whether HTML syntax is interpreted.

---

# Stored HTML Injection

Stored HTML Injection occurs when attacker-controlled HTML is saved and rendered later.

Possible storage locations include:

```text
Profiles
Comments
Support tickets
Product reviews
User descriptions
Messages
Forum posts
Administrative notes
Company names
Address fields
Uploaded file metadata
```

Conceptually:

```text
Input
 ↓
Database
 ↓
Another Page
 ↓
Browser
 ↓
HTML Parsed
```

Stored HTML Injection can have greater impact because multiple users may encounter the injected content.

---

# DOM-Based HTML Injection

DOM-based HTML Injection occurs when client-side JavaScript places attacker-controlled data into an HTML parsing sink.

Conceptually:

```text
URL / Input
     ↓
JavaScript
     ↓
DOM Sink
     ↓
Browser Parses HTML
```

Potential sources include:

```text
location.search
location.hash
location.href
document.URL
document.referrer
postMessage
localStorage
sessionStorage
```

Potential sinks include:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
document.writeln
```

Example pattern:

```javascript
element.innerHTML = userInput;
```

The security question is:

```text
Can attacker-controlled data reach the HTML sink without safe handling?
```

---

# Attribute Injection

User input may appear inside an existing HTML attribute.

Example:

```html
<input value="USER_INPUT">
```

or:

```html
<a href="USER_INPUT">Continue</a>
```

or:

```html
<div title="USER_INPUT">
```

The relevant context is different from normal HTML body content.

Always determine exactly where the input appears.

---

# Context Matters

Before testing, identify the rendering context.

Possible contexts include:

```text
HTML body
HTML attribute
URL attribute
HTML comment
Script block
Style block
DOM property
Template
```

Example body context:

```html
<div>
USER_INPUT
</div>
```

Attribute context:

```html
<input value="USER_INPUT">
```

URL context:

```html
<a href="USER_INPUT">
```

Comment context:

```html
<!-- USER_INPUT -->
```

Different contexts require different security controls.

---

# Start With a Marker

Always begin with a unique harmless marker.

Example:

```text
AM-HTML-987654
```

Submit it to the application.

Then determine:

```text
Is it reflected?

Is it stored?

Where is it rendered?

Is it encoded?

Is it inside an attribute?

Is it inserted through JavaScript?

Does another user see it?
```

---

# HTML Encoding

A secure application may transform:

```html
<h1>TEST</h1>
```

into:

```html
&lt;h1&gt;TEST&lt;/h1&gt;
```

The browser displays:

```text
<h1>TEST</h1>
```

rather than interpreting it as markup.

This is expected output encoding behaviour.

---

# Basic Harmless HTML Tests

Once reflection has been confirmed, simple formatting elements can establish whether HTML is interpreted.

Examples:

```html
<b>AM-HTML-TEST</b>
```

```html
<i>AM-HTML-TEST</i>
```

```html
<h1>AM-HTML-TEST</h1>
```

```html
<mark>AM-HTML-TEST</mark>
```

```html
<small>AM-HTML-TEST</small>
```

These are preferable as initial tests because they visibly demonstrate HTML interpretation without JavaScript.

---

# Structural HTML Tests

You may also use simple structural elements:

```html
<div>AM-HTML-DIV</div>
```

```html
<p>AM-HTML-PARAGRAPH</p>
```

```html
<ul>
<li>AM-HTML-ITEM</li>
</ul>
```

The objective is simply to establish:

```text
Input
 ↓
HTML Parser
 ↓
Rendered Markup
```

---

# Link Injection

A useful controlled test is whether an anchor element can be inserted.

For example:

```html
<a href="https://example.com">AM-HTML-LINK</a>
```

Using a harmless destination such as `example.com` avoids directing users to malicious infrastructure.

If rendered, determine:

```text
Is the link clickable?

Can arbitrary destinations be supplied?

Is the link stored?

Can another user see it?

Does the application visually distinguish user content?
```

---

# Image Injection

A controlled image element may help determine whether markup is interpreted.

For example, when external requests are explicitly allowed within scope:

```html
<img src="https://example.com/example.png" alt="AM-HTML-TEST">
```

However, external resources can generate outbound browser requests.

For many assessments, a simple formatting element is sufficient to demonstrate HTML Injection without introducing external network interaction.

---

# Form Injection

HTML Injection may permit forms to be inserted into trusted application pages.

Conceptually:

```html
<form>
  <label>AM HTML Injection Test</label>
  <input type="text">
</form>
```

This can demonstrate that an attacker may create misleading interface elements.

Avoid creating deceptive login forms or collecting credentials.

The objective is to demonstrate UI manipulation, not to obtain user information.

---

# UI Manipulation

HTML Injection can sometimes alter the appearance of trusted content.

For example:

```html
<h2>AM HTML Injection Test</h2>
<p>This text was inserted through user-controlled input.</p>
```

This demonstrates content injection without pretending to be an application security warning or requesting user action.

---

# HTML Injection in Search

Search functionality frequently reflects query values.

Example:

```http
GET /search?q=AM-HTML-987654 HTTP/1.1
Host: target.example
```

Response:

```html
<h2>Search results for AM-HTML-987654</h2>
```

Workflow:

```text
Search Parameter
      ↓
Response
      ↓
Locate Reflection
      ↓
Determine Context
      ↓
Test Encoding
      ↓
Test Harmless HTML
```

---

# HTML Injection in Error Messages

Applications may reflect values in errors.

Example:

```text
Unknown account: USER_INPUT
```

or:

```text
No results found for USER_INPUT
```

Error pages therefore deserve the same context analysis as normal application pages.

---

# HTML Injection in Profiles

Profile fields may include:

```text
First name
Last name
Display name
Biography
Company
Job title
Address
Website
```

A useful workflow:

```text
Account A
   ↓
Set Unique Marker
   ↓
View Own Profile
   ↓
View from Account B
   ↓
Determine Whether Stored
   ↓
Test Harmless HTML
```

Two controlled accounts help determine whether the injection affects other users.

---

# HTML Injection in Support Systems

Support functionality is particularly interesting because data may cross application boundaries.

Example:

```text
Public Application
       ↓
Support Ticket
       ↓
Database
       ↓
Support Dashboard
       ↓
Support Agent Browser
```

Fields may include:

```text
Subject
Name
Email
Company
Message
Ticket title
Attachment name
```

Start with markers rather than markup if an internal user may process the data.

---

# HTML Injection in File Names

Uploaded file names may later appear in:

```text
Upload confirmation pages
File managers
Administrative interfaces
Download pages
Audit logs
Document management systems
```

Example workflow:

```text
File Name
   ↓
Upload
   ↓
Metadata Stored
   ↓
Application Renders File Name
```

Begin with:

```text
AM-HTML-FILENAME-987654.pdf
```

Then determine whether special characters are encoded correctly.

---

# HTML Injection in Email Templates

User-controlled content may be inserted into HTML email.

Conceptually:

```text
User Input
    ↓
Application
    ↓
HTML Email Template
    ↓
Recipient Mail Client
```

Examples include:

```text
Display name
Invitation message
Support message
Order information
Notification content
```

Testing email rendering can affect external recipients, so use only controlled mailboxes and authorised workflows.

---

# HTML Injection in PDFs and Generated Documents

Applications may convert user-controlled content into:

```text
PDF
HTML report
Invoice
Receipt
Export
Printable page
```

The rendering engine may interpret HTML differently from the browser.

Test these workflows separately when they are in scope.

---

# HTML Injection in Administrative Interfaces

A public input may later appear in an administrative interface.

Conceptually:

```text
Public Input
    ↓
Stored
    ↓
Admin Interface
    ↓
Rendered
```

This overlaps with Blind XSS methodology.

Start with unique markers and determine where the value appears before attempting any callback-based testing.

---

# Burp Suite Workflow

A practical Burp workflow:

```text
Proxy
  ↓
Browse Application
  ↓
HTTP History
  ↓
Identify Input
  ↓
Send Request to Repeater
  ↓
Insert Unique Marker
  ↓
Locate Marker in Response
  ↓
Determine HTML Context
  ↓
Test Encoding
  ↓
Insert Harmless HTML
  ↓
Compare Response
```

---

# Burp Repeater

Suppose the baseline request is:

```http
GET /search?q=hello HTTP/1.1
Host: target.example
```

Send it to Repeater.

Change:

```text
hello
```

to:

```text
AM-HTML-987654
```

Locate the marker in the response.

Then try:

```html
<b>AM-HTML-TEST</b>
```

If the response contains:

```html
<b>AM-HTML-TEST</b>
```

and the browser renders it as bold text, HTML interpretation has been demonstrated.

---

# Raw Response vs Browser Rendering

Do not rely solely on Burp's raw response.

For example:

```html
&lt;b&gt;AM-HTML-TEST&lt;/b&gt;
```

and:

```html
<b>AM-HTML-TEST</b>
```

look similar when reading quickly but have completely different browser behaviour.

Always verify:

```text
Raw response
+
Browser rendering
```

---

# Browser Developer Tools

Developer Tools can help determine whether injected markup appears in the DOM.

Inspect:

```text
Elements
Network
Sources
Console
```

For DOM-based cases, identify whether JavaScript transforms:

```text
Text
```

into:

```text
HTML
```

after the original response loads.

---

# View Source vs DOM

There is an important distinction between:

```text
View Source
```

and:

```text
DOM shown in Developer Tools
```

DOM-based injection may not appear in the original HTTP response.

Conceptually:

```text
Server Response
      ↓
JavaScript Executes
      ↓
DOM Modified
```

Therefore inspect both.

---

# JavaScript Source Review

Search JavaScript for HTML sinks such as:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
document.writeln
```

Example:

```javascript
result.innerHTML = searchTerm;
```

Then trace where:

```text
searchTerm
```

originates.

---

# Source-to-Sink Analysis

A useful model:

```text
SOURCE
  ↓
User-Controlled Data
  ↓
TRANSFORMATIONS
  ↓
HTML SINK
  ↓
BROWSER PARSING
```

Example:

```text
location.search
      ↓
URLSearchParams
      ↓
searchTerm
      ↓
innerHTML
```

This is more useful than simply collecting isolated payloads.

---

# Filters

Applications may filter:

```text
<
>
"
'
/
=
```

or particular element names.

Do not immediately conclude that the application is secure.

Determine:

```text
What context is used?

Is output encoding present?

Is sanitisation used?

Is the filter applied consistently?

Does another rendering path exist?
```

---

# Sanitisation

Some applications intentionally allow limited HTML.

For example:

```text
Blog comments
Rich-text editors
CMS content
Knowledge bases
Forums
```

The correct security control may therefore be:

```text
HTML Sanitisation
```

rather than encoding all markup.

A sanitiser may allow:

```html
<b>
<i>
<p>
<ul>
<li>
```

while removing dangerous constructs.

Allowed HTML is not automatically a vulnerability.

The security question is whether the sanitisation policy prevents unsafe content.

---

# Rich Text Editors

Rich-text functionality may intentionally support HTML.

Test:

```text
Which elements are allowed?

Which attributes are allowed?

Are URL schemes restricted?

Is sanitisation performed server-side?

Does another renderer process the content differently?

Does the API enforce the same policy as the GUI?
```

Do not report expected formatting support as HTML Injection.

---

# Markdown Rendering

Applications may convert Markdown to HTML.

Example:

```markdown
**hello**
```

becomes:

```html
<strong>hello</strong>
```

The relevant question is:

```text
Can raw or generated HTML escape the intended Markdown security policy?
```

The Markdown parser and HTML sanitiser may be separate components.

---

# Content Security Policy

Content Security Policy can reduce the impact of certain browser-based attacks.

However:

```text
CSP
```

does not fix unsafe HTML rendering.

HTML Injection may still allow:

```text
Content manipulation
Links
Forms
Page structure changes
```

even when script execution is prevented.

---

# HTML Injection to XSS

When HTML Injection is confirmed, evaluate whether it can become Cross-Site Scripting.

Conceptually:

```text
HTML Injection
      ↓
Can Browser Execution Be Reached?
      ↓
Yes
      ↓
XSS
```

If JavaScript execution is demonstrated, classify and report the more significant XSS condition appropriately.

Refer to:

[Cross-Site Scripting](xss.md)

---

# HTML Injection and Open Redirect

Injected HTML may create links pointing to arbitrary destinations.

For example:

```html
<a href="https://example.com">Continue</a>
```

This is different from an Open Redirect.

HTML Injection:

```text
Attacker inserts a new link
```

Open Redirect:

```text
Existing trusted application endpoint redirects browser to attacker-controlled destination
```

Keep the vulnerabilities conceptually separate.

---

# HTML Injection and Phishing

One possible impact of HTML Injection is UI spoofing.

For example, an attacker may be able to alter trusted application content.

However, testing should not involve collecting real credentials.

A safe proof of concept can demonstrate:

```text
Injected heading
Injected explanatory text
Injected non-functional input
Injected harmless link
```

This is normally sufficient to demonstrate UI manipulation.

---

# Reflection Mapping

Create a simple table:

| Input | Reflected | Context | Encoded |
|---|---:|---|---:|
| `q` | Yes | HTML body | No |
| `name` | Yes | Attribute | Yes |
| `message` | No | N/A | N/A |
| `company` | Yes | HTML body | No |

This helps prioritise testing.

---

# Stored Input Mapping

For stored values:

| Input | Storage | Viewer | HTML Parsed |
|---|---|---|---:|
| Display name | Profile | User | No |
| Biography | Profile | Other users | Yes |
| Ticket subject | Support DB | Support agent | Unknown |
| File name | Upload DB | Admin | Unknown |

This is particularly useful when testing applications with many workflows.

---

# Testing Checklist

## Discovery

```text
[ ] Identify reflected parameters
[ ] Identify stored user-controlled fields
[ ] Identify DOM-controlled input
[ ] Identify administrative rendering paths
[ ] Identify file metadata
[ ] Identify generated documents
[ ] Identify email rendering
```

## Context

```text
[ ] HTML body
[ ] HTML attribute
[ ] URL attribute
[ ] HTML comment
[ ] DOM sink
[ ] Rich-text context
[ ] Markdown context
```

## Encoding

```text
[ ] Test <
[ ] Test >
[ ] Test "
[ ] Test '
[ ] Inspect entity encoding
[ ] Compare raw response and DOM
```

## HTML Interpretation

```text
[ ] Test unique marker
[ ] Test harmless formatting
[ ] Test simple structural HTML
[ ] Test harmless link where appropriate
[ ] Determine whether injection is reflected or stored
```

## Stored Behaviour

```text
[ ] View from same account
[ ] View from second controlled account
[ ] Check administrative workflow where authorised
[ ] Check persistence
[ ] Check editing
[ ] Check deletion
```

## DOM

```text
[ ] Review JavaScript
[ ] Search innerHTML
[ ] Search outerHTML
[ ] Search insertAdjacentHTML
[ ] Search document.write
[ ] Trace source to sink
```

## Impact

```text
[ ] Can content be changed?
[ ] Can links be inserted?
[ ] Can forms be inserted?
[ ] Can trusted UI be imitated?
[ ] Does another user see the content?
[ ] Can it escalate to XSS?
```

---

# HTML Injection Decision Tree

```text
User Input
    ↓
Reflected / Stored / DOM?
    ↓
Where Is It Rendered?
    ↓
HTML Body?
Attribute?
DOM?
    ↓
Is It Encoded?
    ↓
Yes → Likely Safe for That Context
    ↓
No
    ↓
Does Browser Parse Markup?
    ↓
No → Continue Context Analysis
    ↓
Yes
    ↓
HTML Injection Confirmed
    ↓
Stored?
    ↓
Other Users Affected?
    ↓
Can Script Execution Occur?
    ↓
Yes → Evaluate as XSS
    ↓
No
    ↓
Assess HTML Injection Impact
```

---

# HTML Injection Quick Reference

```text
START

AM-HTML-987654
```

```text
FORMATTING

<b>AM-HTML-TEST</b>
<i>AM-HTML-TEST</i>
<h1>AM-HTML-TEST</h1>
<mark>AM-HTML-TEST</mark>
```

```text
STRUCTURE

<div>AM-HTML-DIV</div>
<p>AM-HTML-PARAGRAPH</p>
```

```text
HARMLESS LINK

<a href="https://example.com">AM-HTML-LINK</a>
```

```text
DOM SINKS

innerHTML
outerHTML
insertAdjacentHTML
document.write
document.writeln
```

---

# Evidence Collection

For a confirmed issue record:

```text
Affected endpoint
Affected parameter
Injection type
Rendering context
Original request
Modified request
Raw response
Rendered result
Whether stored
Affected users
Required interaction
Security impact
```

Screenshots should clearly demonstrate the injected content without including unnecessary sensitive information.

---

# Example Finding

```text
Finding:
Stored HTML Injection in User Biography

Affected Functionality:
User Profile

Affected Parameter:
biography

Expected:
User-controlled profile content should be safely encoded or sanitised before rendering.

Observed:
HTML supplied through the biography field was stored and subsequently interpreted as markup when another controlled user viewed the profile.

Proof of Concept:
<b>AM-HTML-TEST</b>

Impact:
An attacker can modify the appearance and structure of profile pages viewed by other users. Depending on the permitted HTML and browser context, this may facilitate misleading content or potentially form part of a broader browser-side attack.
```

---

# Reporting Titles

Prefer precise titles:

```text
Reflected HTML Injection in Search Results

Stored HTML Injection in User Biography

HTML Injection Through Uploaded File Name

HTML Injection in Support Ticket Subject

DOM-Based HTML Injection Through URL Parameter

HTML Injection in Generated Email Content
```

Avoid reporting:

```text
Cross-Site Scripting
```

unless browser script execution has actually been demonstrated.

---

# Remediation

The correct remediation depends on whether HTML is intended.

If HTML is not required:

```text
Context-aware output encoding
```

should normally be applied.

If HTML is intentionally supported:

```text
Strict HTML sanitisation
```

should be used.

---

# Output Encoding

For HTML body content, characters such as:

```text
&
<
>
"
'
```

should be handled according to the relevant output context.

Do not rely only on input filtering.

Security should be applied when data is rendered.

---

# Context-Aware Encoding

Different contexts require different encoding.

```text
HTML body
HTML attribute
JavaScript
URL
CSS
```

A generic replace operation is not sufficient for every context.

Use framework-supported encoding functions.

---

# Sanitisation

If users are allowed to provide HTML:

```text
Untrusted HTML
      ↓
Well-Maintained Sanitiser
      ↓
Allowed Elements / Attributes
      ↓
Safe HTML
```

Use established libraries rather than custom regular-expression filters.

---

# Server-Side Enforcement

Do not rely solely on client-side validation.

An attacker can bypass the browser UI and submit requests directly.

Controls should therefore be enforced where the data is processed and rendered.

---

# References

## OWASP Cross Site Scripting Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

Useful guidance for context-aware output encoding and safe rendering.

---

## OWASP HTML5 Security Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html

Useful security guidance for modern HTML and browser functionality.

---

## PortSwigger Cross-Site Scripting

https://portswigger.net/web-security/cross-site-scripting

Useful for understanding the boundary between unsafe HTML handling and script execution.

---

# Final HTML Injection Testing Model

```text
                    USER INPUT
                        ↓
                 UNIQUE MARKER
                        ↓
              WHERE DOES IT APPEAR?
                        ↓
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
   Reflected          Stored            DOM
       ↓                ↓                ↓
       └────────────────┼────────────────┘
                        ↓
                RENDERING CONTEXT
                        ↓
       ┌────────────────┼────────────────┐
       ↓                ↓                ↓
   HTML Body        Attribute        HTML Sink
       ↓                ↓                ↓
       └────────────────┼────────────────┘
                        ↓
                 OUTPUT ENCODING?
                        ↓
                 HTML INTERPRETED?
                        ↓
                       YES
                        ↓
                 HTML INJECTION
                        ↓
             WHO CAN VIEW THE DATA?
                        ↓
              WHAT CAN BE MODIFIED?
                        ↓
               CAN IT BECOME XSS?
                        ↓
                 ASSESS IMPACT
                        ↓
                      REPORT
```

The key principle is:

> First determine where attacker-controlled data is rendered and whether the browser interprets it as HTML. Demonstrate HTML Injection with harmless markup before investigating whether the condition can escalate into Cross-Site Scripting or another browser-side vulnerability.
