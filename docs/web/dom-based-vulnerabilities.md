# DOM-Based Vulnerabilities

DOM-based vulnerabilities occur when client-side JavaScript processes attacker-controlled data and passes it into a security-sensitive operation.

Unlike many traditional server-side vulnerabilities, the vulnerable behaviour may occur entirely inside the user's browser.

A useful model is:

```text
Attacker-Controlled Input
        ↓
      Source
        ↓
Client-Side JavaScript
        ↓
   Propagation
        ↓
      Sink
        ↓
Security Impact
```

Examples of possible impact include:

```text
DOM-Based XSS
DOM-Based Open Redirect
DOM-Based Cookie Manipulation
DOM-Based JavaScript Injection
DOM-Based WebSocket Manipulation
DOM-Based Link Manipulation
DOM-Based Document-Domain Manipulation
Web Message Manipulation
Client-Side Data Leakage
```

The fundamental question during testing is:

> Can attacker-controlled data reach a security-sensitive DOM sink without appropriate validation, sanitisation, or encoding?

!!! warning "Authorised Security Testing"
    Perform DOM-based vulnerability testing only against applications included in the authorised assessment scope. Use harmless canary values first and demonstrate the minimum impact necessary to prove the vulnerability.

---

# The Document Object Model

The Document Object Model, or DOM, represents a web page as objects that JavaScript can interact with.

Consider:

```html
<html>
  <body>
    <h1>Hello</h1>
  </body>
</html>
```

The browser represents this approximately as:

```text
Document
   ↓
 HTML
   ↓
 BODY
   ↓
  H1
   ↓
"Hello"
```

JavaScript can:

```text
Read DOM elements
Modify DOM elements
Create elements
Delete elements
Read URL information
Read cookies
Access browser storage
Process messages
Handle navigation
```

This makes the DOM a major client-side attack surface.

---

# DOM-Based Vulnerability Model

The most important concepts are:

```text
SOURCE
  ↓
PROPAGATION
  ↓
SINK
```

For example:

```text
location.search
      ↓
JavaScript
      ↓
innerHTML
      ↓
DOM XSS
```

Another example:

```text
location.hash
      ↓
JavaScript
      ↓
location.href
      ↓
Open Redirect
```

Another:

```text
postMessage
      ↓
Message Handler
      ↓
eval()
      ↓
JavaScript Execution
```

Understanding:

```text
Source → Sink
```

is therefore fundamental to DOM security testing.

---

# Sources

A source is a location where attacker-controlled data enters client-side JavaScript.

Common sources include:

```text
location
location.href
location.search
location.hash
location.pathname
document.URL
document.documentURI
document.referrer
document.cookie
window.name
postMessage
localStorage
sessionStorage
IndexedDB
WebSocket messages
URLSearchParams
```

Not every source is automatically attacker-controlled.

The security question is:

```text
Can an attacker influence this value?
```

---

# Sinks

A sink is a JavaScript function, property, or API that can cause a security-sensitive action when supplied with attacker-controlled data.

Examples include:

```text
innerHTML
outerHTML
document.write()
document.writeln()
eval()
Function()
setTimeout()
setInterval()
location
location.href
location.assign()
location.replace()
window.open()
script.src
iframe.src
WebSocket()
document.cookie
```

Different sinks create different vulnerability classes.

---

# Source to Sink Analysis

Suppose the application contains:

```javascript
const message = location.hash.substring(1);

document.getElementById("message").innerHTML = message;
```

The source is:

```javascript
location.hash
```

The sink is:

```javascript
innerHTML
```

The flow is:

```text
URL Fragment
     ↓
location.hash
     ↓
message
     ↓
innerHTML
     ↓
HTML Interpretation
```

This is a potential DOM-based XSS path.

---

# Sources vs Sinks

A source alone is not normally a vulnerability.

For example:

```javascript
const value = location.search;
```

does not automatically create a security problem.

Likewise:

```javascript
element.innerHTML = "<b>Hello</b>";
```

is not attacker-controlled.

The interesting condition is:

```text
Attacker-Controlled Source
          ↓
Dangerous Sink
```

---

# Propagation

Data does not always move directly from source to sink.

Example:

```javascript
const params = new URLSearchParams(location.search);

const value = params.get("name");

const decoded = decodeURIComponent(value);

const message = "Hello " + decoded;

document.getElementById("welcome").innerHTML = message;
```

Flow:

```text
location.search
      ↓
URLSearchParams
      ↓
params.get("name")
      ↓
decodeURIComponent()
      ↓
String concatenation
      ↓
innerHTML
```

This entire path must be analysed.

---

# DOM-Based XSS

DOM-based XSS occurs when attacker-controlled data reaches a JavaScript sink capable of creating executable browser content.

Common sinks include:

```text
innerHTML
outerHTML
document.write()
document.writeln()
eval()
Function()
setTimeout()
setInterval()
script.src
```

Example:

```javascript
const search = new URLSearchParams(location.search);

document.getElementById("result").innerHTML =
    search.get("q");
```

Conceptual request:

```text
https://target.example/?q=AM-DOM-TEST
```

If:

```text
AM-DOM-TEST
```

appears in the DOM through `innerHTML`, investigate the rendering context.

Refer to:

```text
docs/web/xss.md
```

---

# DOM XSS vs Reflected XSS

Traditional reflected XSS:

```text
Request
  ↓
Server
  ↓
Attacker Input Reflected in HTML
  ↓
Browser Executes
```

DOM-based XSS:

```text
Request
  ↓
Browser
  ↓
JavaScript Reads Input
  ↓
JavaScript Modifies DOM
  ↓
Browser Executes
```

The server response may not contain the injected value at all.

---

# Why Proxy-Only Testing Can Miss DOM XSS

Consider:

```text
https://target.example/#AM-DOM-TEST
```

The URL fragment:

```text
#AM-DOM-TEST
```

is normally not sent to the server.

Therefore Burp may see:

```http
GET / HTTP/1.1
Host: target.example
```

while browser JavaScript sees:

```javascript
location.hash
```

containing:

```text
#AM-DOM-TEST
```

This is why browser-side analysis is important.

---

# `innerHTML`

One of the most important DOM sinks is:

```javascript
innerHTML
```

Example:

```javascript
element.innerHTML = userInput;
```

The browser interprets the value as:

```text
HTML
```

rather than plain text.

Safer alternatives may include:

```javascript
textContent
```

when HTML interpretation is unnecessary.

---

# `outerHTML`

Similarly:

```javascript
element.outerHTML = userInput;
```

causes the browser to interpret the supplied value as HTML.

Treat attacker-controlled values reaching:

```text
outerHTML
```

as high-priority review targets.

---

# `document.write()`

Example:

```javascript
document.write(location.search);
```

`document.write()` interprets supplied content as part of the document.

It is therefore a security-sensitive sink.

Search for:

```text
document.write(
document.writeln(
```

during JavaScript analysis.

---

# `eval()`

Example:

```javascript
eval(userInput);
```

`eval()` interprets a string as JavaScript.

Attacker-controlled input reaching:

```text
eval()
```

is particularly dangerous.

Search for:

```text
eval(
```

during source review.

---

# `Function()`

The JavaScript `Function` constructor can also evaluate dynamically constructed code.

Example:

```javascript
const fn = new Function(userInput);
fn();
```

Treat this similarly to:

```javascript
eval()
```

for security analysis.

---

# `setTimeout()` and `setInterval()`

These functions can accept strings:

```javascript
setTimeout(userInput, 1000);
```

or:

```javascript
setInterval(userInput, 1000);
```

When strings are used, they may be interpreted as JavaScript.

Safer patterns use:

```javascript
setTimeout(functionReference, 1000);
```

rather than dynamically generated code.

---

# DOM-Based Open Redirect

DOM-based open redirect occurs when attacker-controlled data determines a navigation destination.

Example:

```javascript
const params = new URLSearchParams(location.search);

location.href = params.get("return");
```

Flow:

```text
?return=
    ↓
location.search
    ↓
URLSearchParams
    ↓
location.href
    ↓
Navigation
```

A harmless controlled test could use:

```text
https://example.com/
```

Refer to:

```text
docs/web/open-redirect.md
```

---

# Navigation Sinks

Important navigation sinks include:

```text
location
location.href
location.assign()
location.replace()
window.open()
```

Examples:

```javascript
location = destination;
```

```javascript
location.href = destination;
```

```javascript
location.assign(destination);
```

```javascript
location.replace(destination);
```

```javascript
window.open(destination);
```

---

# DOM Open Redirect Testing

Suppose:

```javascript
const next = new URLSearchParams(location.search).get("next");

location.href = next;
```

Test with a harmless destination:

```text
https://example.com/
```

Determine whether the application:

```text
Allows arbitrary external origins
```

or restricts navigation to:

```text
Trusted application URLs
```

---

# JavaScript URL Validation

Weak validation may look like:

```javascript
if (url.includes("target.example")) {
    location.href = url;
}
```

This is fragile because string matching does not reliably validate:

```text
Scheme
Hostname
Port
Origin
```

Prefer structured URL parsing.

For example:

```javascript
const parsed = new URL(value, location.origin);

if (parsed.origin === location.origin) {
    location.href = parsed.href;
}
```

The exact validation depends on application requirements.

---

# DOM-Based Cookie Manipulation

JavaScript may write attacker-controlled data into cookies.

Example:

```javascript
document.cookie =
    "language=" + location.hash.substring(1);
```

Flow:

```text
location.hash
      ↓
JavaScript
      ↓
document.cookie
```

The impact depends on how the cookie is later used.

---

# Cookie Manipulation Impact

Potential consequences include:

```text
Application state manipulation
Security control manipulation
Stored client-side injection
Unexpected server-side behaviour
Session-related issues
```

However:

```text
Attacker can modify a non-sensitive preference cookie
```

is not automatically a meaningful vulnerability.

Determine how the cookie is consumed.

---

# Cookie Source and Sink

`document.cookie` can act as both:

```text
Source
```

and:

```text
Sink
```

Source:

```javascript
const cookies = document.cookie;
```

Sink:

```javascript
document.cookie = userInput;
```

Context matters.

---

# DOM-Based JavaScript Injection

Attacker-controlled values may reach JavaScript execution sinks.

Examples:

```text
eval()
Function()
setTimeout(string)
setInterval(string)
script.src
```

Architecture:

```text
Attacker Input
     ↓
JavaScript Source
     ↓
Execution Sink
     ↓
JavaScript Execution
```

---

# Script Source Manipulation

Example:

```javascript
const script = document.createElement("script");

script.src = location.hash.substring(1);

document.body.appendChild(script);
```

If an attacker controls:

```text
script.src
```

the application may load attacker-controlled JavaScript.

This can lead to:

```text
Arbitrary JavaScript Execution
```

depending on browser and CSP restrictions.

---

# iframe Source Manipulation

Example:

```javascript
frame.src = userInput;
```

Potential consequences depend on:

```text
Destination restrictions
Sandbox attributes
Browser security model
Application context
```

Not every controllable iframe source is automatically a vulnerability.

---

# Link Manipulation

Example:

```javascript
document.getElementById("continue").href =
    new URLSearchParams(location.search).get("next");
```

This may allow an attacker to modify where a trusted application link sends users.

Possible impacts include:

```text
Phishing
Open Redirect
Workflow Manipulation
```

---

# Form Action Manipulation

Another interesting sink is:

```javascript
form.action
```

Example:

```javascript
document.forms[0].action = userInput;
```

If attacker-controlled input can modify where sensitive form data is submitted:

```text
User enters data
      ↓
Modified form.action
      ↓
Unexpected destination
```

this may have significant impact.

---

# postMessage

Modern web applications frequently use:

```javascript
window.postMessage()
```

for communication between:

```text
Windows
Frames
iframes
Popups
Embedded applications
```

Architecture:

```text
Window A
   ↓
postMessage()
   ↓
Window B
   ↓
message Event
```

---

# Receiving Messages

Example:

```javascript
window.addEventListener("message", function(event) {
    console.log(event.data);
});
```

The important security questions are:

```text
Is event.origin validated?
Is event.source validated?
How is event.data used?
Does event.data reach a dangerous sink?
```

---

# Unsafe postMessage Handler

Example:

```javascript
window.addEventListener("message", function(event) {
    document.getElementById("message").innerHTML = event.data;
});
```

Flow:

```text
External Window
      ↓
postMessage
      ↓
event.data
      ↓
innerHTML
```

If origin validation is absent, this may create a cross-origin attack path.

---

# `event.origin`

The browser provides:

```javascript
event.origin
```

to identify the origin that sent the message.

Example:

```javascript
window.addEventListener("message", function(event) {

    if (event.origin !== "https://trusted.example") {
        return;
    }

    processMessage(event.data);
});
```

This is substantially safer than processing messages from arbitrary origins.

---

# Weak Origin Validation

Dangerous examples include:

```javascript
if (event.origin.includes("trusted.example")) {
```

or:

```javascript
if (event.origin.endsWith("trusted.example")) {
```

depending on the exact logic.

Origin validation should normally compare the expected:

```text
Scheme
Hostname
Port
```

as an origin.

---

# `postMessage` Target Origin

Sending:

```javascript
window.postMessage(data, "*");
```

allows any receiving origin to receive the message if the relevant window reference is available.

Where possible, specify an exact trusted target origin:

```javascript
window.postMessage(
    data,
    "https://trusted.example"
);
```

---

# postMessage Testing Workflow

Search JavaScript for:

```text
postMessage(
addEventListener("message"
addEventListener('message'
onmessage
event.data
event.origin
```

Then map:

```text
Message Sender
      ↓
Message Receiver
      ↓
Origin Validation
      ↓
event.data
      ↓
Sink
```

---

# Safe postMessage Testing

A controlled test page may conceptually:

```javascript
targetWindow.postMessage(
    "AM-POSTMESSAGE-001",
    "https://target.example"
);
```

Observe whether the target processes the marker.

Only progress to security-sensitive testing if the message reaches an interesting sink.

---

# Web Storage

Client-side applications commonly use:

```text
localStorage
sessionStorage
```

Example:

```javascript
localStorage.setItem("theme", "dark");
```

Data can later become a source:

```javascript
const value = localStorage.getItem("message");
```

---

# localStorage

`localStorage` persists across browser sessions for the same origin until removed.

Example:

```javascript
const value = localStorage.getItem("name");

element.innerHTML = value;
```

Flow:

```text
localStorage
     ↓
JavaScript
     ↓
innerHTML
```

The key question becomes:

```text
Can an attacker control the stored value?
```

---

# sessionStorage

`sessionStorage` is scoped differently but can still provide attacker-influenced data to client-side code.

Example:

```javascript
const redirect =
    sessionStorage.getItem("redirect");

location.href = redirect;
```

Potential result:

```text
DOM-Based Open Redirect
```

if an attacker can control the stored value.

---

# Storage-Based DOM XSS

Conceptually:

```text
Attacker-Controlled Input
       ↓
Stored in localStorage
       ↓
Later Page Load
       ↓
localStorage.getItem()
       ↓
innerHTML
       ↓
DOM XSS
```

This resembles:

```text
Stored XSS
```

but the persistence may exist entirely in the browser.

---

# IndexedDB

Modern applications may store substantial client-side data in:

```text
IndexedDB
```

Potential security questions include:

```text
Can attacker-controlled data enter the database?
How is stored data later rendered?
Does it reach HTML or JavaScript sinks?
Does sensitive information persist unnecessarily?
```

Use browser DevTools to inspect IndexedDB.

---

# window.name

`window.name` is an often-overlooked source.

Example:

```javascript
const value = window.name;
```

The value can persist across certain navigations.

If used in:

```text
innerHTML
eval()
location
```

it may become security relevant.

---

# document.referrer

Example:

```javascript
const source = document.referrer;
```

Applications may use the referrer for:

```text
Navigation
Analytics
UI content
Redirect logic
```

If the value reaches a sensitive sink, investigate whether an attacker can control the referring URL sufficiently to exploit the flow.

---

# location

The `location` object contains multiple attacker-influenced components.

Important properties include:

```text
location.href
location.search
location.hash
location.pathname
location.hostname
location.origin
```

---

# location.search

For:

```text
https://target.example/search?q=test
```

JavaScript sees:

```javascript
location.search
```

as approximately:

```text
?q=test
```

This is one of the most common DOM sources.

---

# URLSearchParams

Modern applications often use:

```javascript
new URLSearchParams(location.search)
```

Example:

```javascript
const params =
    new URLSearchParams(location.search);

const search = params.get("q");
```

This makes parameter identification easier during source review.

Search for:

```text
URLSearchParams
```

in JavaScript bundles.

---

# location.hash

For:

```text
https://target.example/page#section
```

JavaScript sees:

```javascript
location.hash
```

as:

```text
#section
```

Because the fragment is processed client-side, it is particularly important for DOM testing.

---

# location.pathname

For:

```text
https://target.example/users/alice
```

JavaScript may read:

```javascript
location.pathname
```

as:

```text
/users/alice
```

Client-side routers frequently depend on this value.

---

# document.URL

Example:

```javascript
const current = document.URL;
```

This can contain attacker-controlled URL components.

Search for:

```text
document.URL
document.documentURI
```

during JavaScript review.

---

# DOM-Based WebSocket Manipulation

WebSocket applications may process attacker-influenced DOM data before sending messages.

Example:

```javascript
socket.send(location.hash.substring(1));
```

Flow:

```text
location.hash
      ↓
JavaScript
      ↓
WebSocket.send()
      ↓
Server
```

The security impact depends on how the server processes the message.

Refer to:

```text
docs/web/websockets.md
```

---

# WebSocket Messages as Sources

Incoming WebSocket data can also act as a source:

```javascript
socket.onmessage = function(event) {
    output.innerHTML = event.data;
};
```

Flow:

```text
WebSocket Server
      ↓
event.data
      ↓
innerHTML
```

If an attacker can influence server-sent data, this may create a DOM injection path.

---

# DOM-Based AJAX Manipulation

Client-side code may construct AJAX requests using attacker-controlled input.

Example:

```javascript
const endpoint =
    new URLSearchParams(location.search).get("api");

fetch(endpoint);
```

Potential impacts include:

```text
Unexpected external requests
Information disclosure
Client-side request manipulation
CORS-related behaviour
```

The browser security model still applies.

---

# fetch()

Search for:

```text
fetch(
```

Then determine whether the URL or request body is attacker-controlled.

Example:

```javascript
fetch(userControlledUrl);
```

Potential security implications depend on:

```text
Destination
Credentials
CORS
Response handling
```

---

# XMLHttpRequest

Legacy and modern applications may use:

```javascript
XMLHttpRequest
```

Search for:

```text
XMLHttpRequest
.open(
.send(
```

Map attacker-controlled values into:

```text
URL
Method
Headers
Body
```

---

# DOM-Based Header Manipulation

JavaScript may use attacker-controlled data in request headers.

Example:

```javascript
fetch("/api", {
    headers: {
        "X-Value": userInput
    }
});
```

Whether this is exploitable depends on:

```text
Server behaviour
Header restrictions
Application logic
```

---

# DOM Clobbering

DOM clobbering occurs when HTML elements interfere with JavaScript variables or properties through browser DOM behaviour.

It can sometimes transform:

```text
HTML Injection
```

into:

```text
JavaScript Behaviour Manipulation
```

even when direct script execution is blocked.

---

# DOM Clobbering Concept

Suppose application JavaScript expects:

```javascript
window.config
```

to contain a trusted JavaScript object.

HTML elements with specific:

```text
id
name
```

attributes may create properties on:

```text
window
document
```

in certain circumstances.

Conceptually:

```text
Injected HTML
     ↓
Named DOM Element
     ↓
Global Property
     ↓
Application JavaScript
     ↓
Unexpected Behaviour
```

---

# DOM Clobbering Example Concept

Application:

```javascript
let config = window.config || {};

const script = document.createElement("script");

script.src = config.url;

document.body.appendChild(script);
```

If attacker-controlled HTML can create a DOM structure that influences:

```text
window.config
```

the application's assumptions may fail.

The exact browser behaviour and DOM structure must be verified.

---

# Why DOM Clobbering Matters

Modern applications may have:

```text
HTML injection
```

while:

```text
<script>
```

is blocked.

DOM clobbering can sometimes provide another route from:

```text
HTML Injection
```

to:

```text
Dangerous JavaScript Behaviour
```

depending on available gadgets.

---

# DOM Clobbering Sources

Look for attacker-controlled HTML entering:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
```

Then inspect application code for assumptions involving:

```text
window.someProperty
document.someProperty
global named properties
```

---

# DOM Clobbering Gadgets

A gadget is existing application code that can be influenced through DOM clobbering.

Conceptually:

```text
Attacker HTML
      ↓
DOM Property
      ↓
Existing JavaScript Gadget
      ↓
Sensitive Sink
```

This is similar to gadget discovery in:

```text
Prototype Pollution
```

but the mechanism differs.

Refer to:

```text
docs/web/prototype-pollution.md
```

---

# DOM Clobbering vs Prototype Pollution

DOM clobbering:

```text
HTML / Named Elements
       ↓
DOM Properties
       ↓
JavaScript Behaviour
```

Prototype pollution:

```text
Attacker-Controlled Object Property
       ↓
Prototype Chain
       ↓
Inherited Property
       ↓
JavaScript Behaviour
```

Both often require:

```text
Existing Gadget
```

but use different mechanisms.

---

# DOM-Based Document-Domain Manipulation

Legacy applications may use:

```javascript
document.domain
```

to relax same-origin restrictions between related subdomains.

Example:

```javascript
document.domain = "example.com";
```

This mechanism is deprecated and should generally be avoided in modern applications.

Review applications that rely on it carefully because it changes origin assumptions.

---

# DOM-Based Client-Side Logic Manipulation

Not every DOM vulnerability results in XSS.

JavaScript may make security-sensitive decisions such as:

```javascript
if (localStorage.getItem("role") === "admin") {
    showAdminPanel();
}
```

If this controls only:

```text
UI visibility
```

while the server still enforces authorisation, impact may be minimal.

If the backend trusts the resulting client behaviour:

```text
Security issue
```

may exist.

---

# Client-Side Security Is Not Authorisation

Never rely on:

```text
Hidden button
Disabled form
JavaScript role check
localStorage flag
```

to enforce server-side authorisation.

Correct model:

```text
Browser
 ↓
Request
 ↓
Server
 ↓
Authorisation Check
 ↓
Sensitive Action
```

Refer to:

```text
docs/web/authorisation.md
```

---

# Client-Side Validation

JavaScript validation may check:

```text
Input length
Character sets
File types
Numeric values
Business rules
```

Example:

```javascript
if (amount > 1000) {
    return;
}
```

The server must independently validate the value.

Client-side validation is useful for:

```text
User experience
```

but is not a security boundary.

---

# DOM-Based URL Manipulation

Applications frequently construct URLs:

```javascript
const url =
    "/search?q=" + userInput;
```

Potential consequences depend on where the URL is used:

```text
Navigation
fetch()
iframe
script
image
form
WebSocket
```

Always trace the final sink.

---

# Dangerous URL Schemes

When URLs are attacker-controlled, review whether the application restricts schemes appropriately.

Possible schemes include:

```text
http:
https:
javascript:
data:
blob:
```

The security impact depends heavily on:

```text
Sink
Browser behaviour
CSP
Application context
```

Do not assume all schemes work in all sinks.

---

# DOM-Based Link Manipulation

Example:

```javascript
link.href = userInput;
```

Potential impact:

```text
Phishing
Navigation manipulation
Open redirect
```

Test with:

```text
https://example.com/
```

before considering anything more intrusive.

---

# DOM-Based Image Manipulation

Example:

```javascript
image.src = userInput;
```

Potential impacts may include:

```text
External requests
Tracking
Information leakage
```

depending on browser and application context.

This is not automatically XSS.

---

# DOM-Based iframe Manipulation

Example:

```javascript
iframe.src = userInput;
```

Review:

```text
Destination restrictions
Sandbox
Permissions
Same-origin behaviour
Sensitive embedding
```

---

# DOM-Based Form Manipulation

Interesting properties include:

```text
form.action
form.method
input.value
```

If attacker-controlled data modifies:

```text
Submission destination
```

or:

```text
Security-sensitive form state
```

investigate the impact.

---

# DOM-Based File Handling

Modern applications may process files entirely client-side using:

```text
FileReader
Blob
Object URLs
Canvas
PDF libraries
Spreadsheet libraries
```

Potential sources include:

```text
Filename
File content
Metadata
MIME type
```

If these values reach HTML sinks, DOM injection may occur.

---

# File Names as DOM Sources

Suppose:

```javascript
filenameElement.innerHTML = file.name;
```

A specially crafted filename may be interpreted as HTML.

Safer:

```javascript
filenameElement.textContent = file.name;
```

Refer to:

```text
docs/web/file-upload.md
docs/web/html-injection.md
docs/web/xss.md
```

---

# Third-Party JavaScript

DOM vulnerabilities frequently occur inside:

```text
Application JavaScript
Third-party libraries
Analytics
Widgets
Chat components
Tag managers
Legacy dependencies
```

Review:

```text
First-party code
```

and:

```text
Third-party code
```

where relevant.

---

# Minified JavaScript

Production JavaScript is frequently minified:

```javascript
function a(b){document.getElementById("x").innerHTML=b}
```

Use:

```text
Browser Pretty Print
Source maps
Burp
Local formatting tools
```

to make analysis easier.

---

# Source Maps

Source maps may expose original source code.

Look for:

```text
//# sourceMappingURL=
```

or files ending:

```text
.js.map
```

Source maps can make source-to-sink analysis substantially easier.

Refer to:

```text
docs/web/information-disclosure.md
docs/web/reconnaissance/javascript-analysis.md
```

---

# Static JavaScript Analysis

Useful search terms include:

```text
location
location.href
location.search
location.hash
location.pathname
document.URL
document.referrer
document.cookie
window.name
postMessage
event.data
localStorage
sessionStorage
innerHTML
outerHTML
document.write
eval
Function
setTimeout
setInterval
location.assign
location.replace
window.open
insertAdjacentHTML
```

---

# grep

For downloaded JavaScript:

```bash
grep -RniE \
'location\.|document\.URL|document\.referrer|document\.cookie|window\.name|postMessage|event\.data|localStorage|sessionStorage|innerHTML|outerHTML|document\.write|eval\(|new Function|setTimeout|setInterval|location\.assign|location\.replace|window\.open|insertAdjacentHTML' \
.
```

This is a discovery mechanism.

Every result requires manual analysis.

---

# Source Search

Potential sources:

```bash
grep -RniE \
'location\.href|location\.search|location\.hash|location\.pathname|document\.URL|document\.documentURI|document\.referrer|document\.cookie|window\.name|event\.data|localStorage|getItem|sessionStorage|getItem' \
.
```

---

# Sink Search

Potential sinks:

```bash
grep -RniE \
'innerHTML|outerHTML|document\.write|document\.writeln|eval\(|new Function|setTimeout|setInterval|location\.href|location\.assign|location\.replace|window\.open|insertAdjacentHTML' \
.
```

---

# Manual Data-Flow Analysis

Suppose search finds:

```javascript
const redirect = getRedirect();

location.href = redirect;
```

Find:

```javascript
getRedirect()
```

Then continue backwards until you determine the original source.

Example:

```javascript
function getRedirect() {
    return new URLSearchParams(location.search).get("next");
}
```

Now the complete flow is:

```text
location.search
      ↓
URLSearchParams
      ↓
getRedirect()
      ↓
redirect
      ↓
location.href
```

---

# Source-to-Sink Graph

For complex applications, document flows:

```text
Source:
location.search
     ↓
parseQuery()
     ↓
getParameter("next")
     ↓
validateRedirect()
     ↓
redirectUser()
     ↓
Sink:
location.href
```

Then inspect:

```text
validateRedirect()
```

to determine whether the flow is safe.

---

# Sanitisation

A source-to-sink path may contain a sanitizer.

Example:

```javascript
element.innerHTML =
    DOMPurify.sanitize(userInput);
```

Do not immediately report the sink.

Determine:

```text
Sanitizer
Configuration
Version
Context
Transformations after sanitisation
```

---

# Sanitisation Must Match the Sink

Different contexts require different controls.

For example:

```text
HTML
JavaScript
URL
CSS
```

have different security requirements.

A sanitizer designed for:

```text
HTML
```

does not automatically make data safe for:

```text
JavaScript execution
```

or:

```text
URL navigation
```

---

# Encoding

Encoding may transform:

```text
<
```

into:

```text
&lt;
```

for HTML contexts.

But security depends on:

```text
Where the value is inserted
```

Always determine the final browser interpretation.

---

# Transformation Chains

Data may be transformed through:

```text
decodeURIComponent()
atob()
JSON.parse()
String replacement
Regular expressions
URL parsing
HTML decoding
Base64 decoding
```

Example:

```text
location.hash
      ↓
atob()
      ↓
JSON.parse()
      ↓
object.message
      ↓
innerHTML
```

The source remains attacker-controlled even after transformation.

---

# Base64 Is Not Sanitisation

Example:

```javascript
const value = atob(location.hash.substring(1));
```

Base64:

```text
Encoding / Representation
```

is not:

```text
Security Sanitisation
```

The decoded value must still be treated as untrusted.

---

# JSON Is Not Sanitisation

Similarly:

```javascript
JSON.parse(userInput)
```

does not make the resulting values safe.

If:

```javascript
data.message
```

later reaches:

```javascript
innerHTML
```

the vulnerability may still exist.

---

# DOM Invader

Burp Suite includes:

```text
DOM Invader
```

which is specifically designed to assist with client-side DOM vulnerability testing.

It is integrated into Burp's browser.

DOM Invader can help identify:

```text
Sources
Sinks
DOM XSS
Web messages
Prototype pollution
Client-side data flows
```

---

# Enabling DOM Invader

In Burp Suite:

```text
Proxy
 ↓
Open Browser
 ↓
DOM Invader
```

Enable DOM Invader for the target.

The exact UI may vary between Burp versions.

---

# DOM Invader Canary

DOM Invader uses a unique:

```text
Canary
```

to help trace attacker-controlled data.

Conceptually:

```text
Unique Canary
     ↓
Source
     ↓
Application JavaScript
     ↓
Sink
```

If the canary reaches an interesting sink:

```text
Potential DOM vulnerability
```

---

# DOM Invader Workflow

```text
Open Target in Burp Browser
        ↓
Enable DOM Invader
        ↓
Insert Canary into URL / Parameter
        ↓
Load Application
        ↓
DOM Invader Tracks Canary
        ↓
Canary Reaches Sink?
        ↓
YES
        ↓
Inspect Data Flow
        ↓
Determine Context
        ↓
Safe Proof
```

---

# DOM Invader and DOM XSS

DOM Invader can help identify values reaching sinks such as:

```text
innerHTML
document.write
eval
```

A sink hit does not automatically prove exploitability.

Inspect:

```text
Encoding
Sanitisation
Context
Browser behaviour
```

---

# DOM Invader and Web Messages

DOM Invader can also assist with:

```text
postMessage
```

analysis.

This is especially useful for identifying:

```text
Message listeners
Origin validation
Data flows
Potential sinks
```

---

# DOM Invader and Prototype Pollution

DOM Invader includes functionality for identifying:

```text
Prototype pollution sources
Gadgets
```

Prototype pollution has its own dedicated methodology.

Refer to:

```text
docs/web/prototype-pollution.md
```

---

# Burp Proxy

Burp Proxy remains useful for:

```text
JavaScript files
API calls
HTML responses
Source maps
WebSocket traffic
```

However, remember:

```text
Not all DOM data reaches the server.
```

---

# Burp Repeater

Repeater is useful when the source originates from:

```text
Query parameters
Server-returned JSON
API responses
Cookies
Headers
```

But purely client-side sources such as:

```text
location.hash
```

are often easier to test directly in the browser.

---

# Burp Scanner

Burp Scanner can identify many client-side vulnerabilities, including certain DOM-based issues.

Automated results should still be manually verified.

A strong report should demonstrate:

```text
Source
Data Flow
Sink
Security Impact
```

---

# Burp Collaborator

Collaborator can help when a DOM sink causes:

```text
External requests
```

For example:

```text
Image source
Script source
Fetch request
WebSocket connection
```

Use only controlled callback infrastructure.

---

# Browser DevTools

Browser DevTools is one of the most important tools for DOM testing.

Useful panels include:

```text
Elements
Console
Sources
Network
Application
```

---

# Elements

Use:

```text
Elements
```

to inspect the live DOM.

This is different from:

```text
View Source
```

because JavaScript may modify the page after it loads.

---

# View Source vs DOM

Original response:

```text
Server HTML
```

Browser DOM:

```text
Server HTML
     +
JavaScript Modifications
```

DOM vulnerabilities may exist only in:

```text
Live DOM
```

---

# Console

Use the Console to inspect sources.

Examples:

```javascript
location.href
```

```javascript
location.search
```

```javascript
location.hash
```

```javascript
document.referrer
```

```javascript
document.cookie
```

```javascript
localStorage
```

```javascript
sessionStorage
```

---

# Sources Panel

Use:

```text
Sources
```

to:

```text
Inspect JavaScript
Pretty-print bundles
Set breakpoints
Search code
Trace functions
Inspect variables
```

---

# Breakpoints

Set breakpoints on suspicious code.

For example:

```javascript
element.innerHTML = value;
```

Pause execution and inspect:

```text
value
Call stack
Source
Transformations
```

---

# DOM Breakpoints

Browser DevTools can also break when DOM elements are:

```text
Modified
Removed
Updated
```

This can help locate JavaScript responsible for dynamic content.

---

# Event Listener Breakpoints

Useful categories may include:

```text
Message
Mouse
Keyboard
Timer
XHR/fetch
WebSocket
```

This can help analyse event-driven applications.

---

# JavaScript Breakpoint Workflow

```text
Identify Sink
    ↓
Set Breakpoint
    ↓
Trigger Feature
    ↓
Execution Pauses
    ↓
Inspect Variable
    ↓
Inspect Call Stack
    ↓
Trace Backward
    ↓
Identify Source
```

---

# Pretty Printing

Minified JavaScript:

```javascript
function a(b){c.innerHTML=b}
```

can be transformed in DevTools into a more readable structure.

Use:

```text
{}
```

or the browser's pretty-print functionality.

---

# Source Maps

If available, DevTools may automatically map minified JavaScript back to original source files.

This can expose:

```text
Function names
Components
TypeScript
React source
Vue source
Angular source
Comments
```

---

# Frameworks

DOM vulnerabilities can exist in:

```text
Vanilla JavaScript
React
Angular
Vue
jQuery
Svelte
Next.js
Nuxt
Legacy frameworks
```

Frameworks may reduce some risks by default, but unsafe escape hatches still exist.

---

# React

React normally escapes values inserted through JSX:

```jsx
<div>{userInput}</div>
```

But:

```jsx
dangerouslySetInnerHTML
```

is security-sensitive.

Search for:

```text
dangerouslySetInnerHTML
```

---

# Angular

Angular generally performs contextual escaping.

However, review use of:

```text
innerHTML
bypassSecurityTrustHtml
bypassSecurityTrustScript
bypassSecurityTrustUrl
bypassSecurityTrustResourceUrl
```

Security bypass APIs deserve particular attention.

---

# Vue

Vue normally escapes interpolated values.

Review:

```text
v-html
```

because it renders HTML.

Example:

```html
<div v-html="userInput"></div>
```

---

# jQuery

Important jQuery sinks include:

```text
.html()
.append()
.prepend()
.after()
.before()
```

depending on how values are supplied.

Example:

```javascript
$("#result").html(userInput);
```

---

# insertAdjacentHTML

Example:

```javascript
element.insertAdjacentHTML(
    "beforeend",
    userInput
);
```

This parses the supplied string as HTML.

Treat attacker-controlled input reaching this function as security-sensitive.

---

# Safe DOM APIs

Where text is intended, prefer:

```text
textContent
innerText
createTextNode()
```

over:

```text
innerHTML
document.write()
```

Example:

```javascript
element.textContent = userInput;
```

This treats the value as text rather than HTML.

---

# createElement

Safer DOM construction often uses:

```javascript
const link =
    document.createElement("a");

link.textContent =
    userControlledLabel;
```

rather than constructing large HTML strings.

URL properties still require appropriate validation.

---

# Client-Side Template Rendering

Some applications construct HTML:

```javascript
const html =
    `<div>${userInput}</div>`;

container.innerHTML = html;
```

Even though template literals are used:

```text
Attacker input still reaches innerHTML.
```

Template literals do not provide security encoding.

---

# DOM XSS Testing Methodology

Start with a unique harmless marker:

```text
AM-DOM-XSS-001
```

For example:

```text
https://target.example/?q=AM-DOM-XSS-001
```

Then determine:

```text
Does JavaScript read it?
Where does it go?
Does it enter the DOM?
Which sink is used?
Is it encoded?
```

Only after understanding the context should exploitability be assessed.

---

# HTML Marker Testing

If a value reaches an HTML sink, a harmless formatting marker can help identify whether HTML is interpreted.

For example:

```html
<b>AM-DOM-HTML-001</b>
```

If rendered as:

```text
Bold text
```

rather than literal markup, HTML interpretation is occurring.

This does not automatically prove JavaScript execution.

Refer to:

```text
docs/web/html-injection.md
```

---

# DOM Open Redirect Testing Methodology

Start with:

```text
https://example.com/
```

as the controlled destination.

Determine:

```text
Does the browser navigate?
Does validation occur?
Is only same-origin navigation allowed?
Are schemes restricted?
```

Avoid using malicious or deceptive domains.

---

# postMessage Testing Methodology

```text
Identify Listener
      ↓
Inspect event.origin
      ↓
Inspect event.source
      ↓
Trace event.data
      ↓
Identify Sink
      ↓
Use Harmless Canary
      ↓
Verify Cross-Origin Influence
      ↓
Determine Impact
```

---

# Web Storage Testing Methodology

```text
Identify Storage Key
      ↓
Determine Who Can Write It
      ↓
Set Controlled Canary
      ↓
Reload / Trigger Feature
      ↓
Trace Storage Value
      ↓
Identify Sink
      ↓
Determine Impact
```

---

# DOM Clobbering Testing Methodology

```text
Identify HTML Injection
      ↓
Identify Named DOM Properties
      ↓
Review JavaScript Global Lookups
      ↓
Identify Gadget
      ↓
Use Harmless DOM Structure
      ↓
Observe Behaviour Change
      ↓
Determine Security Impact
```

---

# Common DOM Sources

| Source | Example |
|---|---|
| URL | `location.href` |
| Query | `location.search` |
| Fragment | `location.hash` |
| Path | `location.pathname` |
| Document URL | `document.URL` |
| Referrer | `document.referrer` |
| Cookies | `document.cookie` |
| Window name | `window.name` |
| Web message | `event.data` |
| Local storage | `localStorage.getItem()` |
| Session storage | `sessionStorage.getItem()` |
| WebSocket | `event.data` |

---

# Common DOM Sinks

| Sink | Potential Impact |
|---|---|
| `innerHTML` | HTML injection / DOM XSS |
| `outerHTML` | HTML injection / DOM XSS |
| `document.write()` | HTML injection / DOM XSS |
| `insertAdjacentHTML()` | HTML injection / DOM XSS |
| `eval()` | JavaScript execution |
| `Function()` | JavaScript execution |
| `setTimeout(string)` | JavaScript execution |
| `setInterval(string)` | JavaScript execution |
| `location.href` | Open redirect |
| `location.assign()` | Open redirect |
| `location.replace()` | Open redirect |
| `window.open()` | Navigation manipulation |
| `document.cookie` | Cookie manipulation |
| `script.src` | Script loading |
| `iframe.src` | Frame manipulation |
| `form.action` | Form destination manipulation |

---

# High-Value Search Terms

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
document.writeln
eval
new Function
setTimeout
setInterval
location.href
location.assign
location.replace
window.open
postMessage
event.data
event.origin
location.search
location.hash
document.referrer
window.name
localStorage
sessionStorage
document.cookie
dangerouslySetInnerHTML
v-html
bypassSecurityTrust
```

---

# DOM Testing Checklist

## Sources

```text
[ ] location.href
[ ] location.search
[ ] location.hash
[ ] location.pathname
[ ] document.URL
[ ] document.documentURI
[ ] document.referrer
[ ] document.cookie
[ ] window.name
[ ] postMessage / event.data
[ ] localStorage
[ ] sessionStorage
[ ] IndexedDB
[ ] WebSocket messages
```

## HTML Sinks

```text
[ ] innerHTML
[ ] outerHTML
[ ] document.write()
[ ] document.writeln()
[ ] insertAdjacentHTML()
[ ] jQuery .html()
[ ] jQuery .append()
[ ] React dangerouslySetInnerHTML
[ ] Vue v-html
[ ] Angular HTML bypass APIs
```

## JavaScript Sinks

```text
[ ] eval()
[ ] Function()
[ ] setTimeout(string)
[ ] setInterval(string)
[ ] script.src
```

## Navigation

```text
[ ] location
[ ] location.href
[ ] location.assign()
[ ] location.replace()
[ ] window.open()
[ ] link.href
[ ] form.action
```

## Web Messages

```text
[ ] Message listeners identified
[ ] event.origin validated
[ ] event.source considered
[ ] event.data traced
[ ] Dangerous sinks identified
[ ] targetOrigin reviewed
```

## Storage

```text
[ ] localStorage
[ ] sessionStorage
[ ] IndexedDB
[ ] Stored values attacker-controllable
[ ] Stored values reach sinks
```

## DOM Clobbering

```text
[ ] HTML injection exists
[ ] Named elements possible
[ ] Global properties used
[ ] Gadget identified
[ ] Security impact demonstrated
```

## JavaScript

```text
[ ] First-party bundles reviewed
[ ] Third-party scripts reviewed where relevant
[ ] Source maps checked
[ ] Minified files pretty-printed
[ ] Sources searched
[ ] Sinks searched
[ ] Data flow manually verified
```

## Burp

```text
[ ] Proxy
[ ] Burp Browser
[ ] DOM Invader
[ ] Repeater
[ ] Scanner
[ ] Collaborator where appropriate
```

## Browser

```text
[ ] Elements
[ ] Console
[ ] Sources
[ ] Network
[ ] Application
[ ] Breakpoints
[ ] Event listeners
```

---

# Decision Tree

```text
ATTACKER-CONTROLLED INPUT?
          ↓
     YES / MAYBE
          ↓
   IDENTIFY SOURCE
          ↓
 TRACE JAVASCRIPT FLOW
          ↓
 REACHES A SINK?
    ↓          ↓
   NO         YES
    ↓          ↓
OTHER FLOW   WHAT SINK?
              ↓
     ┌────────┼─────────┬──────────┐
     ↓        ↓         ↓          ↓
    HTML   JAVASCRIPT  URL       COOKIE
     ↓        ↓         ↓          ↓
 HTML/XSS   XSS      REDIRECT   MANIPULATION
     ↓        ↓         ↓          ↓
  VERIFY CONTEXT AND SECURITY IMPACT
                   ↓
             CONTROLLED PROOF
                   ↓
                 REPORT
```

---

# Source-to-Sink Decision Model

```text
SOURCE
  ↓
Can attacker control it?
  ↓
 YES
  ↓
TRANSFORMATIONS
  ↓
Is data safely validated / sanitised?
  ↓
 NO / INSUFFICIENT
  ↓
SINK
  ↓
What does sink do?
  ↓
┌────────────┬─────────────┬─────────────┐
↓            ↓             ↓             ↓
HTML       SCRIPT       NAVIGATION     STATE
↓            ↓             ↓             ↓
XSS       CODE EXEC      REDIRECT      COOKIE /
                                        LOGIC
```

---

# False Positives

A source and sink existing on the same page does not prove a vulnerability.

For example:

```javascript
const value = location.search;

element.innerHTML = trustedConstant;
```

There is:

```text
Source
```

and:

```text
Sink
```

but no:

```text
Source → Sink
```

data flow.

---

# False Positive: Safe Text Sink

Example:

```javascript
element.textContent =
    new URLSearchParams(location.search).get("q");
```

The attacker controls the value, but:

```text
textContent
```

normally treats it as text.

This is significantly safer than:

```text
innerHTML
```

---

# False Positive: Proper Validation

Example:

```javascript
const value =
    new URLSearchParams(location.search)
        .get("next");

const url =
    new URL(value, location.origin);

if (url.origin !== location.origin) {
    return;
}

location.href = url.href;
```

An attacker-controlled source reaches:

```text
location.href
```

but validation may prevent arbitrary external navigation.

Verify implementation carefully.

---

# False Positive: Unreachable Code

Static analysis may identify:

```text
Dangerous sink
```

inside code that is:

```text
Unused
Dead
Feature-flagged
Development-only
```

Confirm runtime reachability.

---

# False Positive: Sanitised HTML

Example:

```javascript
element.innerHTML =
    DOMPurify.sanitize(userInput);
```

This requires further analysis rather than immediate reporting.

Review:

```text
DOMPurify version
Configuration
Allowed tags
Allowed attributes
Subsequent DOM transformations
```

---

# Mutation XSS

Even sanitised HTML can sometimes become dangerous if:

```text
Browser parsing
```

or:

```text
Subsequent DOM manipulation
```

changes its interpretation.

This class of issue is commonly referred to as:

```text
Mutation XSS
```

or:

```text
mXSS
```

Modern sanitisation libraries specifically defend against many known mutation behaviours.

Do not attempt to invent bypasses without first understanding:

```text
Sanitizer
Version
Configuration
Browser
Context
```

---

# Client-Side Template Injection

Some client-side frameworks interpret special template syntax.

Conceptually:

```text
Attacker Input
     ↓
Client Template Engine
     ↓
Template Evaluation
```

This is different from:

```text
Server-Side Template Injection
```

which occurs on the server.

Framework and version matter significantly.

---

# DOM-Based Vulnerability Chains

DOM vulnerabilities frequently become more significant when chained.

Example:

```text
HTML Injection
      ↓
DOM Clobbering
      ↓
JavaScript Gadget
      ↓
Dangerous Sink
      ↓
DOM XSS
```

Another:

```text
postMessage
      ↓
Missing Origin Validation
      ↓
event.data
      ↓
innerHTML
      ↓
DOM XSS
```

Another:

```text
URL Parameter
      ↓
localStorage
      ↓
Later Page
      ↓
innerHTML
      ↓
Persistent DOM XSS
```

---

# DOM XSS and CSP

Content Security Policy may limit the impact of certain DOM XSS paths.

However:

```text
CSP
```

should be treated as:

```text
Defence in Depth
```

rather than the primary fix.

The vulnerable source-to-sink flow should still be corrected.

---

# Trusted Types

Trusted Types is a browser security mechanism designed to reduce DOM XSS by restricting dangerous DOM sinks.

Conceptually:

```text
Untrusted String
      ↓
Dangerous DOM Sink
      ↓
Blocked
```

unless the value has been created through an approved:

```text
Trusted Types Policy
```

---

# Trusted Types Header

A CSP may contain:

```http
Content-Security-Policy: require-trusted-types-for 'script'
```

Applications may also define:

```text
trusted-types
```

policies.

Trusted Types can significantly reduce DOM XSS risk in supported applications.

---

# Trusted Types Is Defence in Depth

Trusted Types should complement:

```text
Safe DOM APIs
Validation
Sanitisation
Secure coding
```

rather than replace them.

---

# Remediation

The correct remediation depends on:

```text
Source
Sink
Context
```

The general objective is:

```text
Untrusted Data
      ↓
Appropriate Validation / Sanitisation
      ↓
Safe API
```

---

# Avoid Dangerous HTML Sinks

Instead of:

```javascript
element.innerHTML = userInput;
```

prefer:

```javascript
element.textContent = userInput;
```

when only text is required.

---

# Avoid Dynamic Code Execution

Avoid:

```text
eval()
Function()
setTimeout(string)
setInterval(string)
```

with attacker-influenced values.

Use explicit functions and structured data.

---

# Validate Navigation Destinations

Instead of string matching:

```javascript
if (url.includes("example.com"))
```

parse the URL and validate:

```text
Scheme
Origin
Hostname
Port
```

according to application requirements.

---

# Validate postMessage Origins

Use exact trusted origins.

Example:

```javascript
if (
    event.origin !==
    "https://trusted.example"
) {
    return;
}
```

Also validate:

```text
Message structure
Expected data type
Expected action
```

---

# Restrict postMessage Destinations

Avoid:

```javascript
postMessage(data, "*");
```

when the receiving origin is known.

Use:

```javascript
postMessage(
    data,
    "https://trusted.example"
);
```

---

# Validate Message Schemas

Do not process arbitrary message objects.

Conceptually:

```javascript
if (
    typeof event.data !== "object" ||
    event.data === null ||
    event.data.type !== "expected-action"
) {
    return;
}
```

Then validate each field.

---

# Treat Storage as Untrusted

Values retrieved from:

```text
localStorage
sessionStorage
IndexedDB
```

should not automatically be trusted.

They can often be manipulated by:

```text
Existing XSS
Browser extensions
Application functionality
Previous attacker-controlled flows
```

---

# Avoid Client-Side Security Decisions

Do not use:

```text
DOM state
localStorage
Hidden fields
JavaScript variables
```

as authoritative security controls.

Enforce:

```text
Authentication
Authorisation
Business rules
```

server-side.

---

# Use Robust HTML Sanitisation

If user-controlled HTML is intentionally supported, use a mature sanitisation library.

For example:

```text
DOMPurify
```

with an appropriate configuration.

Do not create ad-hoc sanitizers using simple:

```text
Regex
String replacement
Blacklists
```

---

# Content Security Policy

Use a strong CSP as defence in depth.

Avoid unnecessary:

```text
unsafe-inline
unsafe-eval
```

where practical.

CSP can reduce the impact of some client-side injection vulnerabilities.

---

# Trusted Types

For suitable modern applications, consider:

```text
Trusted Types
```

to restrict dangerous DOM sinks.

This is particularly valuable for large JavaScript applications.

---

# Framework Safety Features

Avoid bypassing framework protections unnecessarily.

Examples:

```text
React:
dangerouslySetInnerHTML

Angular:
bypassSecurityTrust*

Vue:
v-html
```

These features are sometimes necessary, but every use should be reviewed carefully.

---

# Third-Party Dependencies

Keep client-side libraries current.

Old JavaScript libraries may contain:

```text
Known DOM XSS gadgets
Unsafe parsing behaviour
Sanitizer bypasses
Prototype pollution
```

Dependency updates should be part of remediation.

---

# Evidence Collection

For a confirmed DOM vulnerability record:

```text
Affected URL
Affected parameter / source
Source
Propagation path
Sink
JavaScript file
Function
Line where available
Browser behaviour
Controlled marker
Security impact
Screenshot
Burp request where applicable
Relevant DOM state
```

---

# Strong DOM XSS Evidence

Example:

```text
Source:
location.search

Parameter:
q

Propagation:
URLSearchParams → searchTerm

Sink:
innerHTML

Result:
Controlled HTML interpreted by browser
```

For executable XSS, document the minimum authorised proof separately.

---

# Strong postMessage Evidence

Example:

```text
Source:
Cross-origin postMessage

Origin validation:
Missing

Data:
AM-POSTMESSAGE-001

Sink:
innerHTML

Result:
Cross-origin page controls DOM content
```

---

# Strong DOM Open Redirect Evidence

Example:

```text
Source:
?next=

Propagation:
URLSearchParams

Sink:
location.href

Controlled destination:
https://example.com/

Result:
Browser navigates to external origin
```

---

# Example Finding: DOM-Based XSS

```text
Finding:
DOM-Based Cross-Site Scripting Through the q Parameter

Observed:
The application reads the q parameter from location.search using URLSearchParams.

The resulting value is passed directly to the innerHTML property of the search results element without appropriate sanitisation.

Flow:

location.search
      ↓
URLSearchParams
      ↓
q
      ↓
innerHTML

Impact:
An attacker may be able to cause arbitrary JavaScript to execute within the security context of the application when a victim visits a crafted URL.

Recommendation:
Avoid inserting attacker-controlled strings through innerHTML. Use textContent where HTML rendering is unnecessary, or apply robust context-appropriate sanitisation when user-controlled HTML is intentionally supported.
```

---

# Example Finding: DOM-Based Open Redirect

```text
Finding:
DOM-Based Open Redirect Through the next Parameter

Observed:
Client-side JavaScript reads the next parameter from the current URL and assigns the value directly to location.href.

No restriction is applied to the destination origin.

A controlled test using https://example.com/ caused the browser to navigate away from the trusted application.

Impact:
An attacker may construct trusted-domain URLs that redirect users to arbitrary external websites, increasing the effectiveness of phishing or social-engineering attacks.

Recommendation:
Allow only expected relative paths or validate the parsed destination against an explicit allowlist of trusted origins.
```

---

# Example Finding: postMessage Origin Validation

```text
Finding:
Cross-Origin postMessage Handler Processes Messages Without Origin Validation

Observed:
The application registers a message event listener and processes event.data without verifying event.origin.

A controlled external origin was able to send the marker AM-POSTMESSAGE-001 to the application and influence the target functionality.

Impact:
An attacker-controlled website may be able to interact with client-side application functionality that was intended only for trusted origins.

The final severity depends on the actions exposed by the message handler.

Recommendation:
Validate event.origin against an exact allowlist of trusted origins, validate the message structure, and ensure security-sensitive actions require appropriate server-side authorisation.
```

---

# Example Finding: DOM-Based Cookie Manipulation

```text
Finding:
DOM-Based Cookie Manipulation Through URL Fragment

Observed:
The application reads data from location.hash and writes the value directly into a cookie using document.cookie.

No appropriate validation is applied before the value is stored.

Impact:
An attacker may influence client-side application state through a crafted URL.

The security impact depends on how the affected cookie is subsequently used by the application.

Recommendation:
Do not derive security-sensitive cookie values from attacker-controlled URL components. Apply strict validation and enforce all security-sensitive decisions server-side.
```

---

# Example Finding: DOM Clobbering

```text
Finding:
HTML Injection Can Influence Application JavaScript Through DOM Clobbering

Observed:
The application permits controlled HTML to be inserted into the page.

Application JavaScript subsequently reads a named global DOM property without verifying its expected type.

A controlled DOM structure was able to modify the value consumed by the JavaScript gadget.

Impact:
An attacker may influence client-side application behaviour despite direct script elements being blocked.

The final impact depends on the affected gadget and sink.

Recommendation:
Avoid relying on named global DOM properties for security-sensitive configuration. Explicitly define application variables, validate expected object types, and sanitise attacker-controlled HTML.
```

---

# Reporting Titles

Useful titles include:

```text
DOM-Based Cross-Site Scripting Through URL Parameter

DOM-Based Open Redirect Through Client-Side Navigation

Cross-Origin postMessage Handler Lacks Origin Validation

DOM-Based Cookie Manipulation Through URL Fragment

Stored Client-Side Data Reaches Unsafe HTML Sink

HTML Injection Enables DOM Clobbering of Application Configuration

Attacker-Controlled URL Reaches Dangerous JavaScript Sink

Client-Side WebSocket Data Is Rendered Without Sanitisation
```

Avoid vague titles such as:

```text
DOM Issue

JavaScript Problem

Unsafe Client-Side Code
```

Describe:

```text
Source
Sink
Impact
```

where practical.

---

# Severity

Severity depends on the resulting vulnerability.

Examples:

```text
DOM XSS
→ commonly Medium / High depending on context

Open Redirect
→ commonly Low / Medium

Cookie Manipulation
→ depends entirely on cookie purpose

postMessage Issue
→ depends on exposed functionality

DOM Clobbering
→ depends on available gadget

Client-Side UI Manipulation
→ potentially Informational if no security boundary is crossed
```

Do not rate based solely on:

```text
Dangerous function exists
```

Rate the demonstrated:

```text
Security impact
```

---

# Quick Reference

```text
DOM VULNERABILITY
       ↓
ATTACKER INPUT
       ↓
SOURCE
       ↓
PROPAGATION
       ↓
SINK
       ↓
┌──────────────┬───────────────┬──────────────┬──────────────┐
↓              ↓               ↓              ↓
HTML        JAVASCRIPT      NAVIGATION      STATE
↓              ↓               ↓              ↓
HTML/XSS     EXECUTION       REDIRECT       COOKIE /
                                             LOGIC
```

High-value sources:

```text
location.search
location.hash
document.referrer
window.name
postMessage
localStorage
sessionStorage
WebSocket event.data
```

High-value sinks:

```text
innerHTML
outerHTML
document.write
insertAdjacentHTML
eval
Function
setTimeout(string)
setInterval(string)
location.href
location.assign
location.replace
window.open
document.cookie
```

---

# Recommended Workflow

```text
Burp Browser
     ↓
Enable DOM Invader
     ↓
Browse Application
     ↓
Identify Input
     ↓
Insert Unique Canary
     ↓
Canary Enters Source
     ↓
Trace Propagation
     ↓
Canary Reaches Sink?
     ↓
YES
     ↓
Inspect Sink Context
     ↓
Check Sanitisation
     ↓
Use Harmless Proof
     ↓
Determine Security Impact
     ↓
Document Source → Sink
     ↓
Report
```

---

# References

## PortSwigger Web Security Academy: DOM-Based Vulnerabilities

https://portswigger.net/web-security/dom-based

PortSwigger's Web Security Academy material covering DOM-based vulnerabilities, sources, sinks, and client-side data flow.

---

## PortSwigger DOM-Based Vulnerability Labs

https://portswigger.net/web-security/all-labs#dom-based-vulnerabilities

Practical labs covering DOM-based vulnerability classes.

---

## PortSwigger DOM XSS

https://portswigger.net/web-security/cross-site-scripting/dom-based

Detailed guidance on DOM-based cross-site scripting.

---

## PortSwigger DOM Invader

https://portswigger.net/burp/documentation/desktop/tools/dom-invader

Burp Suite's browser-based tool for identifying client-side sources, sinks, web-message issues, and other DOM vulnerabilities.

---

## PortSwigger Web Message Vulnerabilities

https://portswigger.net/web-security/dom-based/controlling-the-web-message-source

Useful material for analysing:

```text
postMessage
event.data
event.origin
```

---

## PortSwigger DOM Clobbering

https://portswigger.net/web-security/dom-based/dom-clobbering

PortSwigger material covering DOM clobbering techniques and client-side gadgets.

---

## OWASP DOM Based XSS Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html

Defensive guidance for preventing DOM-based XSS.

---

## OWASP Cross Site Scripting Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

General XSS prevention guidance.

---

## MDN Document Object Model

https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model

Reference for the browser DOM.

---

## MDN Window.postMessage

https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage

Reference for cross-window messaging and origin validation.

---

## MDN Web Storage API

https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API

Reference for:

```text
localStorage
sessionStorage
```

---

## MDN Location

https://developer.mozilla.org/en-US/docs/Web/API/Location

Reference for:

```text
location.href
location.search
location.hash
location.pathname
```

---

## DOMPurify

https://github.com/cure53/DOMPurify

Widely used HTML sanitisation library for client-side applications.

---

## Trusted Types

https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API

Browser security mechanism designed to reduce DOM XSS risks from dangerous DOM sinks.

---

# Final DOM-Based Vulnerability Testing Model

```text
                         ATTACKER
                            ↓
                     CONTROLLED INPUT
                            ↓
             ┌──────────────┼───────────────┐
             ↓              ↓               ↓
            URL          WEB MESSAGE       STORAGE
             ↓              ↓               ↓
      location.search    event.data      localStorage
      location.hash                      sessionStorage
             ↓              ↓               ↓
             └──────────────┼───────────────┘
                            ↓
                         SOURCE
                            ↓
                  CLIENT-SIDE JAVASCRIPT
                            ↓
                    DATA TRANSFORMATION
                            ↓
                  VALIDATION / SANITISATION?
                       ↓              ↓
                      YES            NO
                       ↓              ↓
                 VERIFY SAFE       SINK
                                      ↓
                  ┌───────────────────┼──────────────────┐
                  ↓                   ↓                  ↓
                HTML              JAVASCRIPT         NAVIGATION
                  ↓                   ↓                  ↓
             innerHTML             eval()          location.href
             outerHTML           Function()        window.open()
          document.write()           ↓                  ↓
                  ↓             CODE EXECUTION       REDIRECT
             DOM XSS
                  │
                  └───────────────────┬──────────────────┘
                                      ↓
                              SECURITY IMPACT
                                      ↓
                               CONTROLLED PROOF
                                      ↓
                                   REPORT
```

The central principle is:

> DOM-based security testing is source-to-sink analysis. Finding an attacker-controlled source is not enough, and finding a dangerous JavaScript function is not enough. Trace whether attacker-controlled data actually travels through the application's client-side logic into a security-sensitive sink, determine what transformations and protections occur along the way, and demonstrate the resulting security boundary failure with the minimum controlled proof necessary.
