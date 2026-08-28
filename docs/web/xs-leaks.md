# XS-Leaks

Cross-Site Leaks, commonly called **XS-Leaks**, are a family of browser side-channel techniques that allow one website to infer information about a user or another website without directly reading the protected cross-origin response.

The key idea is:

```text
Same-Origin Policy
        ↓
Attacker cannot directly read
cross-origin response
        ↓
But browser behaviour may differ
depending on the response
        ↓
Attacker observes that difference
        ↓
Information is inferred
```

XS-Leaks are therefore different from vulnerabilities such as:

```text
Cross-Site Scripting
CORS misconfiguration
CSRF
```

because the attacker may never obtain direct access to the protected response body.

Instead, the attacker observes a **side effect**.

Examples include:

```text
Resource loaded successfully?
Resource generated an error?
Window contains a certain number of frames?
Navigation behaved differently?
Resource was cached?
Window reference survived?
postMessage was received?
Request took noticeably longer?
```

These differences can sometimes reveal sensitive state.

For example:

```text
Is the victim logged in?

Does this account exist?

Is the victim an administrator?

Does the victim have access to this document?

Does the victim have a particular contact?

Does a search return results?

Does a private resource exist?
```

!!! warning "Authorised Security Testing"
    Perform XS-Leak testing only against applications that you are explicitly authorised to assess. Use controlled accounts and controlled data whenever possible. XS-Leaks frequently require a victim browser to interact with an attacker-controlled page, so use your own browser session and test accounts rather than attempting to influence real users.

---

# Why XS-Leaks Exist

Modern browsers allow websites to interact with resources from other origins in many ways.

For example:

```html
<img src="https://example.com/image.png">
```

or:

```html
<script src="https://example.com/script.js"></script>
```

or:

```html
<iframe src="https://example.com/page"></iframe>
```

or:

```javascript
window.open(
    "https://example.com/"
);
```

The browser may allow the request.

However, the **Same-Origin Policy** normally prevents the attacker's JavaScript from directly reading the cross-origin response.

Conceptually:

```text
attacker.example
        ↓
GET https://target.example/account
        ↓
Browser sends request
        ↓
Target responds
        ↓
Same-Origin Policy
        ↓
Attacker cannot simply read:
response.body
```

This is an essential browser security boundary.

However:

```text
Cannot read response
```

does not necessarily mean:

```text
Cannot observe anything about response
```

That distinction is the foundation of XS-Leaks.

---

# Core XS-Leak Concept

Suppose a target behaves differently depending on whether the victim is an administrator.

Conceptually:

```text
/admin/avatar
```

For an administrator:

```text
HTTP 200
Image returned
```

For a normal user:

```text
HTTP 403
HTML error returned
```

An attacker may not be able to read either response.

However, if the URL is loaded as an image:

```javascript
const image = new Image();

image.onload = () => {
    console.log("Loaded");
};

image.onerror = () => {
    console.log("Failed");
};

image.src =
    "https://target.example/admin/avatar";
```

the browser behaviour may reveal:

```text
onload
vs
onerror
```

The attacker has learned something without reading the response.

Conceptually:

```text
Secret state
    ↓
Different server response
    ↓
Different browser behaviour
    ↓
Observable side channel
    ↓
Information leak
```

---

# XS-Leaks Are Side-Channel Attacks

A side channel reveals information indirectly.

Instead of:

```text
Give me the secret
```

the attacker asks:

```text
Did something happen?
```

For example:

```text
Did this resource load?

Did this page contain frames?

Was this resource already cached?

Did this window remain accessible?

Did the server respond quickly?

Did a message arrive?

Did navigation occur?
```

These observations can encode:

```text
Yes / No
```

information.

Repeated observations can sometimes reveal considerably more information.

---

# Typical XS-Leak Model

A common attack model is:

```text
Victim
  ↓
Logged in to:
target.example

Victim
  ↓
Visits:
attacker.example

attacker.example
  ↓
Causes browser to request:
target.example/private-resource

Victim's browser
  ↓
May include target credentials

target.example
  ↓
Response depends on victim state

Browser
  ↓
Produces observable behaviour

attacker.example
  ↓
Infers secret state
```

---

# Important Requirement: Victim Authentication

Many XS-Leaks become interesting because the victim browser already has:

```text
Session cookies
Authentication state
Browser state
Cached resources
```

for the target.

The attacker's page leverages the victim's browser as an oracle.

---

# Same-Origin Policy

Understanding XS-Leaks requires understanding the Same-Origin Policy.

Two URLs are generally same-origin when they have the same:

```text
Scheme
Host
Port
```

For example:

```text
https://example.com/app
https://example.com/profile
```

are same-origin.

But:

```text
https://example.com
https://api.example.com
```

are not.

The hosts differ.

Likewise:

```text
http://example.com
https://example.com
```

are not same-origin because the scheme differs.

---

# Origin vs Site

This distinction is extremely important when studying:

```text
XS-Leaks
SameSite cookies
CSRF
Fetch Metadata
CORS
```

An **origin** is based on:

```text
scheme + host + port
```

A **site** is a different concept and is based around the registrable domain together with scheme in modern schemeful same-site calculations.

For example:

```text
https://app.example.com
https://api.example.com
```

are:

```text
Cross-Origin
```

but can still be:

```text
Same-Site
```

This matters because:

```text
SameSite cookies
```

operate using the **site** concept rather than the stricter **origin** concept.

---

# Same-Origin Example

```text
https://example.com:443/a
https://example.com/b
```

These are same-origin because:

```text
Scheme = HTTPS
Host   = example.com
Port   = 443
```

---

# Cross-Origin Example

```text
https://example.com
https://sub.example.com
```

These are cross-origin because:

```text
Host differs
```

even though they may be considered same-site.

---

# Same-Origin Policy Does Not Prevent Requests

A common misunderstanding is:

```text
SOP prevents cross-origin requests
```

This is incorrect.

Browsers routinely make cross-origin requests for:

```text
Images
Scripts
Stylesheets
Frames
Navigation
Fonts
Media
```

The Same-Origin Policy mainly restricts what one origin can **read or manipulate** from another origin.

Conceptually:

```text
Cross-Origin Request
       ↓
Often Allowed

Cross-Origin Response Reading
       ↓
Usually Restricted
```

XS-Leaks exploit observable information that remains available despite those restrictions.

---

# XS-Leaks vs CORS

CORS determines when JavaScript is permitted to read certain cross-origin responses.

A CORS vulnerability may result in:

```text
Attacker JavaScript
        ↓
Reads sensitive response directly
```

XS-Leaks are different:

```text
Attacker JavaScript
        ↓
Cannot directly read response
        ↓
Observes side effect
        ↓
Infers information
```

Refer to:

```text
docs/web/cors.md
```

---

# XS-Leaks vs CSRF

CSRF typically attempts to make the victim's browser perform an unwanted action.

Example:

```text
Victim browser
    ↓
POST /change-email
    ↓
State changed
```

XS-Leaks generally attempt to **learn information**.

Example:

```text
Victim browser
    ↓
Request /admin/resource
    ↓
Attacker observes browser behaviour
    ↓
Infers whether victim is admin
```

Conceptually:

```text
CSRF
→ Cause state change

XS-Leak
→ Infer state
```

There can be overlap between the defenses used against both.

Refer to:

```text
docs/web/csrf.md
```

---

# XS-Leaks vs XSS

XSS normally gives attacker-controlled JavaScript execution in the target application's security context.

That can potentially provide direct access to:

```text
DOM
Application data
Same-origin responses
Storage
User actions
```

XS-Leaks normally operate from a separate attacker origin.

Conceptually:

```text
XSS

attacker code
    ↓
runs inside target origin
```

versus:

```text
XS-Leak

attacker.example
    ↓
observes cross-origin side channel
    ↓
infers target state
```

Refer to:

```text
docs/web/xss.md
```

---

# What Can XS-Leaks Reveal?

The answer depends heavily on the application.

Potential questions include:

```text
Is the victim logged in?

Does the victim have an account?

Is the victim an administrator?

Does the victim have access to a resource?

Does a document exist?

Does a private search return results?

Does the victim know a specific user?

Does the victim belong to a group?

Has the victim visited a specific application state?

Was a particular resource cached?

Did a sensitive action occur?
```

---

# Binary Oracles

Many XS-Leaks produce a binary answer:

```text
YES
or
NO
```

For example:

```text
Does /admin/avatar return an image?

YES
→ possibly administrator

NO
→ possibly not administrator
```

One bit of information may sound insignificant.

However, if the attacker can ask many carefully chosen questions:

```text
Question 1
Question 2
Question 3
Question 4
...
```

the combined result can potentially reveal meaningful information.

---

# XS-Leak Components

A useful model is:

```text
Secret
  ↓
State-dependent behaviour
  ↓
Cross-site trigger
  ↓
Browser observable
  ↓
Oracle
  ↓
Inference
```

During testing, identify each component.

---

# Step 1: Identify the Secret

Ask:

```text
What information could be inferred?
```

Examples:

```text
Authentication state
Privilege level
Resource existence
Search result
User relationship
Account existence
Document access
```

---

# Step 2: Identify State-Dependent Behaviour

Look for endpoints where:

```text
State A
```

and:

```text
State B
```

produce different behaviour.

Examples:

```text
200 vs 404
200 vs 403
Image vs HTML
Redirect vs no redirect
Fast vs slow
Frame vs no frame
Cache hit vs cache miss
Message vs no message
```

---

# Step 3: Find a Cross-Site Trigger

Determine whether another origin can cause the browser to interact with the target using:

```text
iframe
img
script
link
window.open()
navigation
form
media
object
embed
```

The exact primitives available depend on browser security rules and target headers.

---

# Step 4: Find an Observable

Potential observables include:

```text
load event
error event
window reference
frame count
navigation behaviour
cache timing
resource timing
postMessage
focus behaviour
history behaviour
```

Browser mitigations have reduced or removed many historical XS-Leak techniques, so every technique must be verified against current browsers.

---

# Step 5: Build an Oracle

An oracle converts browser behaviour into a conclusion.

Conceptually:

```javascript
if (observable === stateA) {
    console.log("Secret likely true");
} else {
    console.log("Secret likely false");
}
```

The important word is:

```text
likely
```

because side channels can produce:

```text
Noise
Caching effects
Network variance
Browser differences
Extensions
Proxy differences
```

Always establish reproducibility.

---

# Testing Methodology

A practical XS-Leaks workflow:

```text
Map Sensitive States
        ↓
Capture Baseline Responses
        ↓
Compare State A / State B
        ↓
Identify Observable Differences
        ↓
Determine Cross-Site Reachability
        ↓
Create Controlled Attacker Page
        ↓
Test in Browser
        ↓
Confirm Authentication Context
        ↓
Repeat Tests
        ↓
Eliminate Noise
        ↓
Determine Information Revealed
        ↓
Assess Practical Impact
```

---

# Start With Two Controlled States

A useful testing model is:

```text
Browser State A
→ Controlled account logged in

Browser State B
→ Logged out
```

Or:

```text
Account A
→ Standard user

Account B
→ Controlled privileged test account
```

Or:

```text
Account A
→ Has access to test document

Account B
→ Does not have access
```

Then compare target behaviour.

---

# Burp Baseline Analysis

Burp is useful for identifying endpoints that behave differently.

Use:

```text
Proxy
Repeater
Comparer
Logger
```

Start by capturing the same endpoint under different controlled states.

Example:

```http
GET /private/resource HTTP/1.1
Host: target.example
Cookie: session=ACCOUNT_A
```

versus:

```http
GET /private/resource HTTP/1.1
Host: target.example
Cookie: session=ACCOUNT_B
```

Compare:

```text
Status code
Content-Type
Content-Length
Redirects
Headers
Body structure
Caching
Response time
```

---

# Burp Comparer

Comparer is particularly useful.

Send:

```text
Account A response
```

and:

```text
Account B response
```

to Comparer.

Look for differences in:

```text
Status
Length
Content-Type
Location
Cache-Control
CSP
X-Frame-Options
Cross-Origin-Resource-Policy
Cross-Origin-Opener-Policy
```

A difference does not automatically mean XS-Leak.

The next question is:

```text
Can attacker-controlled cross-site JavaScript observe it?
```

---

# Browser Testing Is Essential

XS-Leaks are browser side-channel attacks.

Therefore:

```text
Burp alone cannot prove many XS-Leaks.
```

Burp can reveal candidate differences.

The browser must then demonstrate whether those differences are observable cross-site.

Use:

```text
Firefox DevTools
Chrome DevTools
Burp's browser
```

where appropriate.

---

# Controlled Attacker Origin

Create a separate origin for testing.

For example:

```text
http://127.0.0.1:8000
```

while the target is:

```text
https://target.example
```

These are cross-origin.

Create:

```text
xsleak-test.html
```

and serve it:

```bash
python3 -m http.server 8000
```

Then browse to:

```text
http://127.0.0.1:8000/xsleak-test.html
```

This provides a simple controlled attacker origin.

---

# Important Cookie Consideration

A cross-site request is only useful for authentication-state testing if the browser sends the relevant authentication credentials.

Cookie behaviour depends on:

```text
SameSite
Secure
Request context
Navigation type
Browser behaviour
```

Always confirm what the browser actually sends.

Do not assume:

```text
Victim logged in
```

means:

```text
Every cross-site request includes session cookie
```

---

# SameSite Cookies

The `SameSite` cookie attribute controls when cookies are sent in cross-site contexts.

Common values:

```text
Strict
Lax
None
```

---

# SameSite=Strict

Conceptually:

```http
Set-Cookie:
session=...;
Secure;
HttpOnly;
SameSite=Strict
```

This provides strong restrictions on sending the cookie in cross-site contexts.

However, compatibility with legitimate workflows must be considered.

---

# SameSite=Lax

Example:

```http
Set-Cookie:
session=...;
Secure;
HttpOnly;
SameSite=Lax
```

`Lax` generally prevents cookies from being sent with many cross-site subresource requests while allowing them for certain top-level navigations using safe methods.

This blocks several common XS-Leak primitives.

However:

```text
SameSite=Lax
```

is not a universal XS-Leak defense.

---

# SameSite=None

Example:

```http
Set-Cookie:
session=...;
Secure;
HttpOnly;
SameSite=None
```

This allows cookies in cross-site contexts when the applicable browser requirements are satisfied.

Applications requiring legitimate cross-site embedding may need this configuration.

It also means additional cross-site attack surface must be considered carefully.

---

# SameSite Is Defense in Depth

Do not write:

```text
SameSite prevents XS-Leaks
```

as a universal statement.

Correct model:

```text
SameSite
    ↓
Restricts authenticated cross-site requests
    ↓
Blocks some XS-Leak techniques
```

But other XS-Leaks may still work through mechanisms such as:

```text
Top-level navigation
Window relationships
Non-cookie state
Cache state
```

depending on the technique.

---

# Error Event Leaks

One important XS-Leak family uses differences between:

```text
load
```

and:

```text
error
```

events.

Suppose:

```text
/private/avatar
```

returns:

```text
Valid image
```

when authorised and:

```text
HTML error
```

when unauthorised.

A controlled test might use:

```html
<!doctype html>

<html>

<head>
    <meta charset="utf-8">
    <title>XS-Leak Test</title>
</head>

<body>

<h1>Controlled XS-Leak Test</h1>

<script>

const image = new Image();

image.onload = () => {
    console.log(
        "Resource loaded as image"
    );
};

image.onerror = () => {
    console.log(
        "Resource generated image error"
    );
};

image.src =
    "https://target.example/private/avatar";

document.body.appendChild(
    image
);

</script>

</body>

</html>
```

This test does not read the response.

It observes:

```text
Browser resource loading behaviour
```

---

# Error Event Oracle

Conceptually:

```text
Account has access
      ↓
Image returned
      ↓
onload
```

versus:

```text
Account lacks access
      ↓
HTML error returned
      ↓
onerror
```

This creates:

```text
Access oracle
```

---

# Error Events Are Context Dependent

Do not assume:

```text
200 = onload
404 = onerror
```

for every element.

Browser event behaviour depends on:

```text
Element type
MIME type
Response
Redirects
CORP
CSP
Browser
```

Always test the actual target and actual browser.

---

# Script Error Oracle

Historically, script elements have also been used as cross-origin loading primitives.

Conceptually:

```html
<script
    src="https://target.example/resource">
</script>
```

Whether this provides a useful observable depends on:

```text
Response type
Browser behaviour
Headers
Content
```

Do not assume arbitrary HTML endpoints can safely or usefully be loaded as scripts.

---

# Frame Counting

Another XS-Leak family involves counting frames.

Cross-origin restrictions normally prevent:

```javascript
frame.contentDocument
```

or:

```javascript
frame.document
```

from being read.

However, some window properties have historically exposed limited information.

A classic example is:

```text
window.length
```

which represents the number of child browsing contexts.

---

# Frame Counting Concept

Suppose:

```text
/account
```

for one user state contains:

```text
0 frames
```

while another state contains:

```text
2 frames
```

If an attacker can obtain an appropriate window reference and observe the frame count, this difference may become an oracle.

Conceptually:

```text
Secret state
    ↓
Different number of frames
    ↓
Observable frame count
    ↓
Secret inferred
```

---

# Framing Restrictions

Applications should generally prevent untrusted origins from framing sensitive pages unless framing is required.

Preferred modern control:

```http
Content-Security-Policy:
frame-ancestors 'none'
```

or an appropriate allow-list.

Legacy compatibility control:

```http
X-Frame-Options: DENY
```

Refer to:

```text
docs/web/clickjacking.md
```

---

# Important CSP Direction

Do not confuse:

```text
frame-src
```

with:

```text
frame-ancestors
```

`frame-src` controls:

```text
What this page may frame
```

while `frame-ancestors` controls:

```text
Who may frame this page
```

For anti-framing protection, the relevant directive is:

```text
frame-ancestors
```

---

# Window-Based XS-Leaks

Another important family uses:

```javascript
window.open()
```

Example:

```javascript
const target = window.open(
    "https://target.example/"
);
```

Historically, the attacker might retain limited relationships with the newly opened cross-origin window.

These relationships can create side channels.

---

# Cross-Origin-Opener-Policy

The `Cross-Origin-Opener-Policy` response header, abbreviated:

```text
COOP
```

controls whether documents share a browsing context group with cross-origin opener documents.

A strong configuration may use:

```http
Cross-Origin-Opener-Policy: same-origin
```

where compatible with application requirements.

This can sever cross-origin opener relationships and mitigate window-reference-based XS-Leaks.

---

# COOP Concept

Without sufficient isolation:

```text
attacker.example
       ↓
window.open()
       ↓
target.example
       ↓
Window relationship may remain
```

With suitable COOP:

```text
attacker.example
       ↓
window.open()
       ↓
target.example
       ↓
Different browsing context group
       ↓
Opener relationship severed
```

This removes an important class of observables.

---

# COOP Values

Important COOP values include:

```text
unsafe-none
same-origin
same-origin-allow-popups
```

The correct value depends on application behaviour.

Do not recommend:

```text
same-origin
```

blindly without considering:

```text
OAuth popups
Payment popups
SSO
Third-party authentication
Legitimate opener communication
```

---

# postMessage

Web applications can intentionally communicate across origins using:

```javascript
window.postMessage()
```

This is legitimate and widely used.

However, insecure message handling can create cross-origin information leaks.

---

# Sending Messages

Example:

```javascript
window.parent.postMessage(
    {
        status: "logged-in"
    },
    "https://trusted.example"
);
```

The second argument is:

```text
targetOrigin
```

---

# Dangerous targetOrigin

A dangerous pattern is:

```javascript
window.parent.postMessage(
    sensitiveData,
    "*"
);
```

because:

```text
*
```

allows the message to be delivered regardless of the receiver's origin.

For sensitive information, specify the intended origin exactly.

---

# Receiving Messages

A receiver should validate:

```javascript
event.origin
```

Example:

```javascript
window.addEventListener(
    "message",
    event => {

        if (
            event.origin !==
            "https://trusted.example"
        ) {
            return;
        }

        // Process trusted message.
    }
);
```

---

# postMessage Testing

Search JavaScript for:

```text
postMessage(
addEventListener("message"
onmessage
event.origin
```

Refer to:

```text
docs/web/dom-based-vulnerabilities.md
```

---

# postMessage XS-Leak

Suppose an application sends:

```text
logged-in
```

only when the user has an active session.

If an attacker can open or embed the target and receive that message:

```text
Message received
→ logged in

No message
→ logged out
```

This creates an authentication-state oracle.

---

# Cache-Based XS-Leaks

Browser caching can sometimes expose whether a user previously loaded a resource.

Conceptually:

```text
Victim accesses private page
        ↓
Resource cached
        ↓
Attacker later causes resource load
        ↓
Timing / cache behaviour differs
        ↓
Attacker infers prior state
```

---

# Cache State

Potentially sensitive cached resources might indicate:

```text
User visited page
User accessed feature
User belongs to group
Specific private content was displayed
```

The practical feasibility depends strongly on:

```text
Browser cache partitioning
Cache-Control
Resource URL
Browser version
Timing precision
```

Modern browsers increasingly partition state to reduce cross-site tracking and XS-Leaks.

Therefore historical cache attacks must not automatically be assumed to work today.

---

# Cache-Control

Sensitive responses can use:

```http
Cache-Control: no-store
```

when they should not be stored.

However, do not blindly apply:

```text
no-store
```

to every resource.

Caching is important for performance.

Use it appropriately for:

```text
Sensitive personalised resources
Authentication responses
Highly private data
```

---

# Unpredictable Resource URLs

For some personalised resources, unpredictable user-specific tokens can make cache probing more difficult.

Conceptually:

```text
/avatar.svg?token=UNPREDICTABLE_VALUE
```

If the attacker cannot determine the URL, probing the resource becomes harder.

Tokens must be:

```text
Unpredictable
User-specific where appropriate
Not exposed elsewhere
```

---

# Timing-Based XS-Leaks

Timing differences can sometimes reveal server-side state.

Suppose:

```text
/search?q=value
```

takes:

```text
50 ms
```

when no records exist and:

```text
500 ms
```

when expensive processing occurs.

If an attacker can measure this difference cross-site with sufficient reliability, it may become an oracle.

---

# Timing Model

```text
Secret condition
      ↓
Different server work
      ↓
Different response timing
      ↓
Browser observes timing
      ↓
Secret inferred
```

---

# Timing Noise

Timing attacks are particularly vulnerable to noise from:

```text
Network latency
CPU load
CDN
Caching
Connection reuse
HTTP/2
HTTP/3
Browser scheduling
Proxy latency
Background tabs
```

Never conclude:

```text
XS-Leak confirmed
```

from one timing measurement.

---

# Timing Testing

Use repeated controlled measurements:

```text
State A
State A
State A
State A
State A

State B
State B
State B
State B
State B
```

Compare distributions rather than individual requests.

---

# Resource Timing

The browser provides APIs such as:

```text
Performance API
Resource Timing API
```

but cross-origin timing information is intentionally restricted in various ways.

Do not assume the attacker can access all timing information for cross-origin resources.

The exact browser behaviour must be tested.

---

# Cross-Origin Resource Policy

`Cross-Origin-Resource-Policy`, abbreviated:

```text
CORP
```

is a response header that allows a server to restrict which origins or sites may load a resource.

Examples:

```http
Cross-Origin-Resource-Policy: same-origin
```

or:

```http
Cross-Origin-Resource-Policy: same-site
```

or:

```http
Cross-Origin-Resource-Policy: cross-origin
```

---

# CORP Concept

Without CORP:

```text
attacker.example
       ↓
<img src="target.example/private-image">
```

may cause the browser to attempt to load the resource.

With:

```http
Cross-Origin-Resource-Policy: same-origin
```

the browser can block inappropriate cross-origin use.

---

# CORP Is Resource Specific

Do not blindly set:

```text
CORP: same-origin
```

on every response.

Some resources are intentionally cross-origin:

```text
CDN assets
Public images
Fonts
Embeddable resources
APIs
Widgets
```

The correct policy depends on the resource.

---

# Fetch Metadata

Modern browsers send Fetch Metadata request headers describing how a request was initiated.

Important headers include:

```text
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-Dest
Sec-Fetch-User
```

These are **request headers**.

They are not response security headers.

---

# Sec-Fetch-Site

Example:

```http
Sec-Fetch-Site: same-origin
```

Possible values include:

```text
same-origin
same-site
cross-site
none
```

---

# Cross-Site Example

A request from:

```text
https://attacker.example
```

to:

```text
https://target.example
```

may contain:

```http
Sec-Fetch-Site: cross-site
```

The server can use this information when deciding whether the request should be permitted.

---

# Sec-Fetch-Dest

`Sec-Fetch-Dest` describes the intended destination.

Examples include:

```text
document
iframe
image
script
style
empty
```

For example:

```http
Sec-Fetch-Dest: image
```

may indicate that a request is being made through an image element.

---

# Sec-Fetch-Mode

Possible modes include values such as:

```text
navigate
cors
no-cors
same-origin
websocket
```

depending on the request.

---

# Sec-Fetch-User

`Sec-Fetch-User` can indicate a user-activated navigation.

This can help distinguish:

```text
User navigation
```

from:

```text
Programmatic resource request
```

in suitable isolation policies.

---

# Fetch Metadata Is Not Automatically Protection

This distinction is critical.

The browser sending:

```http
Sec-Fetch-Site: cross-site
```

does not itself block the request.

The application must enforce a policy.

Conceptually:

```text
Browser
  ↓
Sec-Fetch-Site: cross-site
  ↓
Server
  ↓
Policy Decision
  ↓
Allow / Reject
```

Without the policy:

```text
Header exists
```

but:

```text
No protection is gained
```

---

# Resource Isolation Policy

A conceptual server-side policy could be:

```text
If request is cross-site
AND
request is trying to load sensitive resource
AND
cross-site access is not required
    ↓
Reject
```

Do not implement overly broad blocking without understanding legitimate integrations.

---

# Example Fetch Metadata Logic

Conceptual Express example:

```javascript
function allowRequest(req) {

    const site =
        req.get("Sec-Fetch-Site");

    if (
        site === "same-origin" ||
        site === "same-site" ||
        site === "none"
    ) {
        return true;
    }

    return false;
}
```

Real applications generally require more nuanced logic.

For example:

```text
Public resources
OAuth callbacks
Webhooks
CORS APIs
Payment integrations
Cross-site forms
CDN resources
```

may require exceptions.

---

# Fetch Metadata Testing With Burp

Capture a normal browser request.

Look for:

```http
Sec-Fetch-Site:
Sec-Fetch-Mode:
Sec-Fetch-Dest:
Sec-Fetch-User:
```

Then compare:

```text
Same-origin request
vs
Cross-site request
```

The important test is not simply:

```text
Are headers present?
```

but:

```text
Does the server enforce meaningful restrictions?
```

---

# Fetch Metadata Example

Same-origin:

```http
GET /account HTTP/1.1
Host: target.example
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-Dest: document
```

Cross-site resource request:

```http
GET /account HTTP/1.1
Host: target.example
Sec-Fetch-Site: cross-site
Sec-Fetch-Mode: no-cors
Sec-Fetch-Dest: image
```

If `/account` should never be loaded cross-site as an image, the application could reject the latter request.

---

# Do Not Trust User-Supplied Copies Blindly

Fetch Metadata headers are browser-controlled request metadata in normal browser contexts.

Security policies should be designed around actual browser semantics.

Do not create authentication logic such as:

```text
Sec-Fetch-Site == same-origin
→ User is authenticated
```

Fetch Metadata is:

```text
Request context information
```

not:

```text
Authentication
```

---

# Framing Protection

Many XS-Leak techniques become harder when sensitive pages cannot be embedded cross-origin.

Preferred control:

```http
Content-Security-Policy:
frame-ancestors 'none'
```

or:

```http
Content-Security-Policy:
frame-ancestors 'self'
```

depending on requirements.

Legacy defense-in-depth:

```http
X-Frame-Options: DENY
```

or:

```http
X-Frame-Options: SAMEORIGIN
```

---

# Why Framing Protection Helps

Without framing protection:

```text
attacker.example
       ↓
iframe
       ↓
target.example
```

The attacker cannot normally read the target DOM.

However, the frame may still expose:

```text
Navigation behaviour
Window relationships
Frame count
Other side channels
```

Preventing unnecessary framing removes that attack surface.

---

# CSP and XS-Leaks

Content Security Policy can help reduce certain cross-origin interactions.

Relevant directives can include:

```text
frame-ancestors
script-src
connect-src
img-src
object-src
```

However:

```text
CSP is not a universal XS-Leak defense.
```

Some historical and specialised XS-Leak techniques have even used CSP-related browser behaviour as an oracle.

Use CSP as part of layered browser isolation rather than assuming it solves the entire class.

---

# Cross-Origin Isolation

Modern browser security includes several related mechanisms:

```text
COOP
COEP
CORP
```

where:

```text
COOP
→ Cross-Origin-Opener-Policy

COEP
→ Cross-Origin-Embedder-Policy

CORP
→ Cross-Origin-Resource-Policy
```

Together they can provide stronger isolation between origins.

---

# COEP

Example:

```http
Cross-Origin-Embedder-Policy:
require-corp
```

This controls which cross-origin resources can be embedded by the document.

COEP is particularly relevant to:

```text
Cross-origin isolation
SharedArrayBuffer
High-resolution capabilities
Resource embedding
```

It should not be enabled blindly because it can break legitimate third-party resources.

---

# COOP vs COEP vs CORP

A useful mental model:

```text
COOP
→ Who shares my top-level browsing context group?

COEP
→ Which cross-origin resources may my document embed?

CORP
→ Who may load this resource?
```

---

# Header Testing

During an XS-Leak assessment inspect:

```text
Content-Security-Policy
X-Frame-Options
Cross-Origin-Opener-Policy
Cross-Origin-Embedder-Policy
Cross-Origin-Resource-Policy
Cache-Control
Set-Cookie
```

Also inspect request-side:

```text
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-Dest
Sec-Fetch-User
```

Refer to:

```text
docs/web/http-security-headers.md
```

---

# Element ID / Fragment-Based Leaks

Some XS-Leak techniques involve browser behaviour around:

```text
URL fragments
```

and:

```text
HTML element IDs
```

Conceptually:

```text
https://target.example/page#secret-element
```

If browser behaviour differs depending on whether:

```text
id="secret-element"
```

exists, this can sometimes create an observable.

Historically, techniques have used behaviours such as:

```text
Scrolling
Focus
Navigation
Rendering
```

as side channels.

Modern browser behaviour and mitigations vary, so this class should be tested rather than assumed.

---

# Fragment Identifier

The fragment:

```text
#section
```

is generally handled by the browser and is not normally sent to the HTTP server.

Example:

```text
https://example.com/page#admin
```

The server receives:

```text
/page
```

not:

```text
/page#admin
```

This distinction matters when analysing fragment-based XS-Leaks.

---

# Search-Based XS-Leaks

Search functionality can create useful state differences.

Suppose:

```text
/search?q=secret
```

behaves differently depending on whether results exist.

Potential differences:

```text
Redirect
Response size
Frames
Images
Timing
Cache behaviour
Error behaviour
```

An attacker might try to transform:

```text
Does search term X exist?
```

into a browser-observable oracle.

---

# Search Oracle Concept

```text
/search?q=project-alpha

Results exist
    ↓
Browser state A

No results
    ↓
Browser state B
```

If:

```text
State A
```

and:

```text
State B
```

can be distinguished cross-origin, private search data may leak.

---

# Search Leakage Impact

Potentially sensitive information includes:

```text
Email addresses
Usernames
Project names
Private messages
Contacts
Documents
Medical terms
Internal identifiers
```

The severity depends on:

```text
What can actually be inferred
```

and:

```text
How reliably
```

---

# Redirect-Based Behaviour

State-dependent redirects can create XS-Leak candidates.

Example:

```text
/admin
```

for admin:

```text
200 OK
```

for normal user:

```text
302 /login
```

or:

```text
302 /forbidden
```

The Same-Origin Policy may prevent reading the response, but some browser behaviours can still differ.

Investigate whether the redirect creates an observable through:

```text
Resource type
Window navigation
postMessage
Timing
Error events
```

---

# Status Codes Alone Are Not an XS-Leak

Burp showing:

```text
200
vs
403
```

does not prove a cross-site leak.

You still need:

```text
Cross-site observable
```

Conceptually:

```text
Different responses
        ↓
Potential oracle

Different responses
+
Observable browser difference
        ↓
Actual XS-Leak candidate
```

---

# Content-Length Alone Is Not Enough

Likewise:

```text
Content-Length: 500
```

versus:

```text
Content-Length: 1000
```

does not automatically mean attacker JavaScript can determine the cross-origin response length.

SOP may prevent direct access.

A browser side channel must expose the difference.

---

# Authentication-State Detection

A common XS-Leak goal is:

```text
Is the victim logged in?
```

Suppose:

```text
/profile/avatar
```

returns:

```text
Image
```

when logged in and:

```text
Login HTML
```

when logged out.

If cross-site image loading includes authentication cookies and produces different events:

```text
onload
vs
onerror
```

the attacker may infer authentication state.

---

# Why Login-State Leaks Matter

Knowing that a user is logged into:

```text
Sensitive service
Healthcare service
Internal organisation
Political organisation
Financial platform
```

can itself be privacy-sensitive.

Impact depends heavily on application context.

---

# Account Existence Leaks

An endpoint might behave differently for:

```text
Existing user
```

and:

```text
Non-existing user
```

If this difference is observable cross-site, it may provide:

```text
Account enumeration
```

without directly reading the response.

Refer to:

```text
docs/web/authentication.md
```

---

# Permission-State Leaks

Suppose:

```text
/document/123
```

returns:

```text
Image preview
```

for authorised users and:

```text
HTML 403
```

for unauthorised users.

A resource-loading oracle could reveal:

```text
Does this victim have access to document 123?
```

This may expose:

```text
Organisation membership
Project membership
Document relationships
Privilege state
```

---

# XS-Leaks and IDOR

IDOR/BOLA asks:

```text
Can I directly access another object's data?
```

XS-Leaks may instead ask:

```text
Can I infer whether another object exists
or whether the victim can access it?
```

Refer to:

```text
docs/web/idor-bola.md
```

---

# XS-Leaks and Clickjacking

Both may involve:

```text
iframes
```

but the objectives differ.

Clickjacking:

```text
Trick user into clicking hidden UI
```

XS-Leak:

```text
Observe browser behaviour to infer information
```

Anti-framing controls can mitigate both.

Refer to:

```text
docs/web/clickjacking.md
```

---

# XS-Leaks and Open Redirects

Open redirects can interact with:

```text
Navigation-based oracles
Window behaviour
Authentication flows
```

An open redirect is not automatically an XS-Leak.

It becomes relevant when it contributes to an observable cross-site state difference.

Refer to:

```text
docs/web/open-redirect.md
```

---

# XS-Leaks and Web Cache

Caching can amplify side channels.

Review:

```text
Cache-Control
Vary
CDN behaviour
Private vs public caching
Browser cache
```

Also distinguish XS-Leaks from:

```text
Web Cache Poisoning
Web Cache Deception
```

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# XS-Leaks and Session Management

The victim's session state is often central to the attack.

Review:

```text
SameSite
Secure
HttpOnly
Session lifetime
Authentication state
```

Note:

```text
HttpOnly
```

does not stop the browser from sending the cookie.

It prevents JavaScript from reading the cookie directly.

Therefore:

```text
HttpOnly
```

does not by itself prevent XS-Leaks.

Refer to:

```text
docs/web/session-management.md
```

---

# Cookie Attributes

Useful session cookie baseline:

```http
Set-Cookie:
session=...;
Secure;
HttpOnly;
SameSite=Lax
```

or:

```text
SameSite=Strict
```

where application requirements allow.

The exact SameSite policy should match the application's legitimate cross-site workflows.

---

# Secure Does Not Prevent XS-Leaks

`Secure` ensures the cookie is only sent over secure transport.

It does not determine whether a cross-site request may include the cookie.

That is primarily related to:

```text
SameSite
```

and request context.

---

# HttpOnly Does Not Prevent XS-Leaks

`HttpOnly` prevents JavaScript from reading the cookie through:

```javascript
document.cookie
```

It does not prevent the browser from automatically attaching the cookie to qualifying requests.

---

# SameSite Is the Relevant Cookie Attribute

For cross-site request behaviour:

```text
SameSite
```

is particularly important.

But again:

```text
SameSite
≠
Complete XS-Leak defense
```

---

# Testing With Burp's Browser

A useful setup:

```text
Burp
  ↓
Proxy
  ↓
Burp Browser
  ↓
Target
```

Log in with:

```text
Controlled Account A
```

Then open your attacker page from:

```text
http://127.0.0.1:8000
```

Observe:

```text
Browser console
Burp HTTP history
DevTools Network
```

---

# Confirm Cookie Transmission

When your attacker page triggers:

```text
https://target.example/resource
```

inspect the resulting request in Burp.

Check whether:

```http
Cookie: session=...
```

was actually sent.

If not:

```text
Your test may not represent authenticated victim state
```

and the oracle may be meaningless.

---

# Confirm Sec-Fetch Headers

Observe:

```http
Sec-Fetch-Site: cross-site
Sec-Fetch-Dest: image
```

or other values appropriate to your test.

This confirms the browser sees the request as:

```text
Cross-site
```

and identifies the request context.

---

# Compare Same-Origin and Cross-Site Requests

Capture:

```text
Normal target request
```

and:

```text
Attacker-triggered request
```

Compare:

```text
Cookies
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-Dest
Origin
Referer
Response
```

This often explains why a candidate leak does or does not work.

---

# Controlled Test Page

A reusable basic test page:

```html
<!doctype html>

<html lang="en">

<head>

    <meta charset="utf-8">

    <title>
        XS-Leak Controlled Test
    </title>

</head>

<body>

<h1>
    XS-Leak Controlled Test
</h1>

<p id="result">
    Waiting...
</p>

<script>

const TARGET =
    "https://target.example/private/image";

const result =
    document.getElementById(
        "result"
    );

const image =
    new Image();

image.onload = () => {

    result.textContent =
        "LOAD event observed";

    console.log(
        "[+] LOAD event"
    );

};

image.onerror = () => {

    result.textContent =
        "ERROR event observed";

    console.log(
        "[-] ERROR event"
    );

};

image.src =
    TARGET;

document.body.appendChild(
    image
);

</script>

</body>

</html>
```

Use only against an authorised target and replace:

```text
target.example
```

with the in-scope application.

---

# Two-State Test

Test the same page under:

```text
State A
→ Logged in

State B
→ Logged out
```

Record:

```text
State A:
LOAD

State B:
ERROR
```

Then repeat several times.

If stable:

```text
Potential authentication-state oracle
```

---

# Controlled Access Test

A stronger application-specific test:

```text
Account A
→ Has access to controlled resource

Account B
→ Does not have access
```

Run the same cross-site test.

If:

```text
A → LOAD
B → ERROR
```

and the difference is reproducible:

```text
Access-state XS-Leak
```

may exist.

---

# Avoid Real User Enumeration

Do not immediately test:

```text
CEO
Administrator
Other customer
Real employee
```

Use:

```text
Controlled accounts
Controlled documents
Controlled groups
```

to demonstrate the security property.

---

# Browser Differences

XS-Leak behaviour can vary between:

```text
Chrome
Chromium
Firefox
Safari
```

because browsers implement different:

```text
Isolation
Caching
Timing
Partitioning
Security mitigations
```

Record the browser and version used for testing.

---

# Browser Version Matters

An XS-Leak technique described in older research may no longer work because browsers continually introduce:

```text
Site isolation
Cache partitioning
Storage partitioning
Timing reductions
COOP
CORP
SameSite defaults
Fetch Metadata
```

Never report a historical technique without confirming it works against the current target and supported browser.

---

# Extension Testing

There is no requirement to use a dedicated Burp XS-Leaks extension.

The most important tools are:

```text
Burp Proxy
Burp Repeater
Burp Comparer
Burp Logger
Browser DevTools
Controlled HTML/JavaScript test pages
```

Check the current BApp Store if additional tooling is desired:

```text
https://portswigger.net/bappstore
```

Do not depend on an abandoned historical extension merely because it mentions XS-Leaks.

---

# Useful Browser DevTools

Use the Network panel to inspect:

```text
Request URL
Request type
Initiator
Cookies
Redirects
Timing
Response headers
```

Use Console for:

```text
load events
error events
postMessage
window behaviour
timing measurements
```

---

# Testing Response Headers

For each candidate sensitive endpoint inspect:

```bash
curl -sS \
  -D - \
  -o /dev/null \
  https://target.example/private/resource
```

Look for:

```text
Content-Security-Policy
X-Frame-Options
Cross-Origin-Opener-Policy
Cross-Origin-Embedder-Policy
Cross-Origin-Resource-Policy
Cache-Control
Set-Cookie
```

---

# HEAD Caveat

Do not rely exclusively on:

```bash
curl -I
```

because:

```text
HEAD
```

responses can differ from:

```text
GET
```

responses.

For accurate header testing, using:

```bash
curl -D - -o /dev/null
```

with a normal GET is often preferable.

---

# Basic Header Audit Script

A controlled Python helper:

```python
#!/usr/bin/env python3

import argparse
import requests


HEADERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Embedder-Policy",
    "Cross-Origin-Resource-Policy",
    "Cache-Control",
    "Referrer-Policy",
]


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Inspect headers relevant to "
            "XS-Leak defenses."
        )
    )

    parser.add_argument(
        "url",
        help="Authorised target URL"
    )

    args = parser.parse_args()

    response = requests.get(
        args.url,
        timeout=10,
        allow_redirects=False
    )

    print(
        f"Status: {response.status_code}"
    )

    print()

    for header in HEADERS:

        value = response.headers.get(
            header
        )

        if value is None:

            print(
                f"[-] {header}: not present"
            )

        else:

            print(
                f"[+] {header}: {value}"
            )


if __name__ == "__main__":
    main()
```

Usage:

```bash
python3 xsleak_headers.py \
  https://target.example/account
```

Important:

```text
Missing header
≠
Confirmed XS-Leak
```

The script identifies:

```text
Potential missing isolation controls
```

not exploitable vulnerabilities.

---

# Fetch Metadata Testing

Because Fetch Metadata headers are browser-generated, test them using a real browser.

Example normal request:

```http
Sec-Fetch-Site: same-origin
```

Attacker-origin request:

```http
Sec-Fetch-Site: cross-site
```

Then determine whether the application responds differently.

---

# Potential Secure Behaviour

For a sensitive endpoint that should never be loaded cross-site:

```http
GET /account/private-data HTTP/1.1
Sec-Fetch-Site: cross-site
Sec-Fetch-Dest: image
```

could be rejected:

```http
HTTP/1.1 403 Forbidden
```

while legitimate:

```http
Sec-Fetch-Site: same-origin
```

requests continue normally.

The exact policy must match application requirements.

---

# Fetch Metadata Cannot Replace Authentication

Do not implement:

```text
Sec-Fetch-Site: same-origin
        ↓
Allow sensitive data
```

without authentication.

Fetch Metadata is a supplemental isolation mechanism.

The server must still enforce:

```text
Authentication
Authorisation
CSRF protection
Input validation
```

as applicable.

---

# Information Disclosure Testing

XS-Leaks often depend on a state difference.

Therefore existing information-disclosure issues can contribute to useful oracles.

Examples:

```text
Different status codes
Different resource types
Different redirects
Different error pages
Different cache behaviour
```

Refer to:

```text
docs/web/information-disclosure.md
```

---

# Cross-Origin Resource Testing Matrix

For each candidate endpoint test:

| State | Expected Response | Cross-Site Primitive | Observable |
|---|---|---|---|
| Logged in | Image | img | load |
| Logged out | HTML login | img | error |
| Has access | Resource | iframe | behaviour A |
| No access | Error | iframe | behaviour B |
| Result exists | Response A | window | behaviour A |
| No result | Response B | window | behaviour B |

Only record an XS-Leak when the observable is reproducible.

---

# Candidate Endpoint Checklist

Prioritise:

```text
/account
/profile
/avatar
/admin
/search
/messages
/notifications
/documents
/files
/projects
/groups
/contacts
/invoices
/orders
/reports
```

Focus on endpoints where:

```text
Response depends on private user state
```

---

# Search Endpoint Checklist

```text
[ ] Search requires authentication
[ ] Results depend on private data
[ ] Result/no-result responses differ
[ ] Difference visible cross-site
[ ] Authentication cookie included
[ ] Oracle reproducible
[ ] Query can be controlled
[ ] Sensitive information can be inferred
```

---

# Authentication-State Checklist

```text
[ ] Logged-in response captured
[ ] Logged-out response captured
[ ] Differences identified
[ ] Cross-site request possible
[ ] Authentication state preserved
[ ] Browser observable identified
[ ] Test repeated
[ ] Browser/version recorded
[ ] Information inferred documented
```

---

# Error Event Checklist

```text
[ ] Resource can be requested cross-site
[ ] State A produces load
[ ] State B produces error
[ ] Cookies confirmed
[ ] Redirects understood
[ ] MIME type understood
[ ] CORP checked
[ ] CSP checked
[ ] SameSite checked
[ ] Results reproducible
```

---

# Window-Based Checklist

```text
[ ] Target can be opened cross-origin
[ ] Window reference obtained
[ ] Observable identified
[ ] COOP checked
[ ] Browser behaviour verified
[ ] Popup restrictions considered
[ ] Results reproducible
```

---

# Frame Checklist

```text
[ ] Target can be framed
[ ] frame-ancestors checked
[ ] X-Frame-Options checked
[ ] State-dependent frame behaviour identified
[ ] Observable confirmed
[ ] Browser behaviour verified
```

---

# Cache Checklist

```text
[ ] Sensitive resource cacheable
[ ] Cache state differs
[ ] Resource URL predictable
[ ] Cross-site probing possible
[ ] Browser cache partitioning considered
[ ] Timing noise measured
[ ] Results reproducible
```

---

# postMessage Checklist

```text
[ ] postMessage usage identified
[ ] Message sender identified
[ ] Message receiver identified
[ ] targetOrigin reviewed
[ ] event.origin validation reviewed
[ ] Sensitive data identified
[ ] Cross-origin message receipt tested
```

---

# Defensive Header Checklist

```text
[ ] Content-Security-Policy
[ ] frame-ancestors
[ ] X-Frame-Options
[ ] Cross-Origin-Opener-Policy
[ ] Cross-Origin-Embedder-Policy
[ ] Cross-Origin-Resource-Policy
[ ] Cache-Control
[ ] SameSite cookie attributes
```

---

# Fetch Metadata Checklist

```text
[ ] Sec-Fetch-Site observed
[ ] Sec-Fetch-Mode observed
[ ] Sec-Fetch-Dest observed
[ ] Sec-Fetch-User considered
[ ] Cross-site requests identified
[ ] Server policy identified
[ ] Sensitive resources protected
[ ] Legitimate integrations preserved
```

---

# False Positives

XS-Leaks are especially prone to false positives.

---

# Different Responses Are Not Enough

This:

```text
Logged in
→ 200

Logged out
→ 302
```

does not by itself prove XS-Leak.

You need:

```text
Attacker-observable cross-site difference
```

---

# Missing COOP Is Not Automatically a Vulnerability

Do not report:

```text
Cross-Origin-Opener-Policy missing
```

as a vulnerability without context.

COOP is an important isolation mechanism, but:

```text
Missing header
```

does not prove:

```text
Sensitive information can be leaked
```

---

# Missing CORP Is Not Automatically a Vulnerability

Likewise:

```text
Cross-Origin-Resource-Policy missing
```

does not automatically create a finding.

Determine whether:

```text
Sensitive resource
+
Cross-origin loading
+
Observable difference
```

exists.

---

# Missing Fetch Metadata Enforcement Is Not Automatically a Vulnerability

An application does not necessarily need to reject every:

```text
Sec-Fetch-Site: cross-site
```

request.

Many applications legitimately support cross-site interaction.

A finding requires meaningful security impact.

---

# SameSite=None Is Not Automatically Vulnerable

Some applications require:

```text
SameSite=None
```

for:

```text
Embedded applications
SSO
Cross-site integrations
```

The security question is whether that cross-site capability creates an exploitable state-changing or state-leaking condition.

---

# Timing Difference Is Not Enough

A single:

```text
100 ms
vs
200 ms
```

measurement is not proof.

Repeat testing and determine whether the distributions are sufficiently distinguishable.

---

# Browser Console Errors Are Not Proof

Console messages may indicate:

```text
CORS
CORP
CSP
Mixed content
MIME blocking
```

but these are not themselves evidence of an XS-Leak.

Understand why the browser behaves differently.

---

# Impact Assessment

Ask:

```text
What can the attacker learn?
```

Then:

```text
How sensitive is it?
```

Then:

```text
How reliably?
```

Then:

```text
Under what victim conditions?
```

Then:

```text
How many interactions are required?
```

---

# Example Low-Impact Leak

```text
Attacker can determine whether
a public page was previously loaded.
```

May be:

```text
Informational / Low
```

depending on context.

---

# Example Privacy Leak

```text
Attacker can determine whether victim
is logged into a sensitive service.
```

Impact may be higher depending on the nature of the service.

---

# Example Sensitive State Leak

```text
Attacker can determine whether victim
has access to a confidential project.
```

This could reveal:

```text
Employment
Membership
Investigation
Project involvement
```

and may have meaningful privacy impact.

---

# Example Data Extraction Oracle

If repeated queries allow the attacker to infer secret data character by character:

```text
Secret
 ↓
Question 1
 ↓
Yes / No
 ↓
Question 2
 ↓
Yes / No
 ↓
...
 ↓
Secret reconstructed
```

the severity can become substantially higher.

---

# Evidence Collection

Capture:

```text
Target endpoint
Sensitive state
State A response
State B response
Attacker page
Browser/version
Cross-site request
Cookies sent
Fetch Metadata headers
Observable result
Repeated test results
Relevant defensive headers
```

---

# Minimal Proof

Prefer proving:

```text
Controlled state A
vs
Controlled state B
```

rather than extracting real sensitive information.

For example:

```text
Controlled Account A
has access to:
XSLEAK-TEST-DOCUMENT

Controlled Account B
does not
```

Then demonstrate:

```text
Attacker page can distinguish A from B
```

This is normally sufficient to prove the security boundary.

---

# Example Finding: Authentication State XS-Leak

```text
Finding:
Cross-Site Resource Loading Reveals User Authentication State

Observed:
A cross-origin page can determine whether a user is authenticated to the application by loading an authenticated resource as an image.

When the controlled test account is authenticated, the endpoint returns an image and the browser fires the load event.

When the user is unauthenticated, the endpoint returns an HTML login response and the browser fires the error event.

The attacker-controlled page cannot read either response body, but the difference in browser behaviour provides a reliable authentication-state oracle.

Impact:
A malicious website visited by an authenticated user can determine whether the victim is currently logged into the affected application.

Depending on the sensitivity of the service, this may expose private information about the victim's use of the application and may support further cross-site attacks.

Recommendation:
Prevent unnecessary authenticated cross-site resource loading. Configure an appropriate SameSite policy for session cookies, implement a Fetch Metadata resource isolation policy where compatible, and consider CORP for sensitive resources. Ensure authenticated and unauthenticated states do not unnecessarily create externally observable resource-type differences.
```

---

# Example Finding: Permission State XS-Leak

```text
Finding:
Cross-Site Side Channel Reveals Access to Private Documents

Observed:
The application returns a valid image preview when the authenticated user has access to a document and an HTML error response when access is denied.

An attacker-controlled origin can load the preview endpoint using an image element and distinguish the two states through load and error events.

Testing was performed using two controlled accounts and a controlled test document.

Impact:
A malicious website visited by an authenticated user can determine whether that user has access to a specific document.

If document identifiers or names are predictable, this could reveal sensitive project, organisation or document membership information.

Recommendation:
Prevent sensitive personalised resources from being usable as cross-site oracles. Apply appropriate SameSite cookies, Fetch Metadata resource isolation, CORP and access-response design according to application requirements.
```

---

# Example Finding: postMessage Information Leak

```text
Finding:
Sensitive Authentication State Is Disclosed Through Cross-Origin postMessage

Observed:
The application sends authentication-state information to the parent or opener window using postMessage without restricting the target origin.

An attacker-controlled page can embed or open the application and receive the message.

Impact:
A malicious website can determine whether the victim is authenticated and may receive additional information contained in the message.

Recommendation:
Specify an exact trusted targetOrigin when sending sensitive postMessage data and validate event.origin when receiving messages. Do not use "*" as the target origin for security-sensitive information.
```

---

# Example Finding: Search XS-Leak

```text
Finding:
Cross-Site Side Channel Reveals Private Search Results

Observed:
The authenticated search endpoint produces browser-observable behaviour that differs depending on whether the supplied search term matches private data.

A controlled attacker page can query the endpoint cross-site and distinguish result and no-result states without reading the response body.

Testing was performed using controlled test data.

Impact:
A malicious website visited by an authenticated user may be able to query the victim's private search state and infer whether specific values exist.

Depending on the searchable data and query flexibility, this could expose sensitive information.

Recommendation:
Prevent authenticated cross-site requests to sensitive search endpoints where they are not required. Implement appropriate SameSite cookie policy and Fetch Metadata resource isolation. Remove unnecessary cross-site observables and ensure sensitive search responses cannot be used as reliable browser side channels.
```

---

# Example Finding Titles

Useful titles include:

```text
Cross-Site Resource Loading Reveals Authentication State

XS-Leak Reveals Access to Private Resources

Cross-Site Side Channel Reveals Private Search Results

Cross-Origin Frame Behaviour Reveals User State

Cross-Origin Window Side Channel Reveals Authentication State

Sensitive State Disclosed Through postMessage

Cross-Site Cache Side Channel Reveals Private Resource Access

Missing Cross-Origin Isolation Enables User-State Inference
```

Avoid vague titles such as:

```text
XS-Leak Exists
```

State what information is actually exposed.

---

# Remediation Strategy

There is no universal:

```text
XS-Leak fix
```

because XS-Leaks exploit many different browser mechanisms.

Use layered defenses.

Conceptually:

```text
                  XS-Leak Defenses
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Request Isolation  Document Isolation Resource Isolation
        ↓                ↓                ↓
 Fetch Metadata         COOP             CORP
 SameSite              Framing           COEP
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                   Safe Application
                      Behaviour
                         ↓
                 Reduce Side Channels
```

---

# Defense 1: SameSite Cookies

Use an appropriate:

```text
SameSite
```

policy for authentication cookies.

Prefer:

```text
Strict
```

where compatible.

Otherwise:

```text
Lax
```

may provide useful defense in depth.

Use:

```text
None
```

only where legitimate cross-site functionality requires it.

---

# Defense 2: Fetch Metadata

Use:

```text
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-Dest
Sec-Fetch-User
```

to identify suspicious cross-site contexts.

Implement a server-side resource isolation policy.

Do not merely check whether the headers exist.

---

# Defense 3: Framing Protection

If pages do not need cross-origin framing:

```http
Content-Security-Policy:
frame-ancestors 'none'
```

or:

```http
Content-Security-Policy:
frame-ancestors 'self'
```

as appropriate.

For legacy defense-in-depth:

```http
X-Frame-Options: DENY
```

or:

```http
X-Frame-Options: SAMEORIGIN
```

---

# Defense 4: COOP

Where compatible:

```http
Cross-Origin-Opener-Policy:
same-origin
```

can isolate the document from cross-origin opener relationships.

Test application compatibility before deployment.

---

# Defense 5: CORP

Sensitive resources that should not be loaded cross-origin may use:

```http
Cross-Origin-Resource-Policy:
same-origin
```

or:

```text
same-site
```

depending on architecture.

Do not apply it indiscriminately to intentionally public cross-origin resources.

---

# Defense 6: COEP

Applications requiring stronger cross-origin isolation may use:

```http
Cross-Origin-Embedder-Policy:
require-corp
```

when compatible.

COEP can break third-party resource loading, so deployment requires testing.

---

# Defense 7: Cache Control

For sensitive resources that should not be stored:

```http
Cache-Control: no-store
```

may reduce cache-based side channels.

Do not disable caching globally without considering performance and resource sensitivity.

---

# Defense 8: Safe postMessage

Send:

```javascript
window.postMessage(
    data,
    "https://trusted.example"
);
```

instead of:

```javascript
window.postMessage(
    data,
    "*"
);
```

for sensitive data.

On receipt:

```javascript
if (
    event.origin !==
    "https://trusted.example"
) {
    return;
}
```

---

# Defense 9: Reduce State-Dependent Browser Differences

Where practical, avoid creating unnecessary differences such as:

```text
Image
vs
HTML

Frame
vs
No frame

Cacheable
vs
Non-cacheable

Message
vs
No message
```

for sensitive state when those differences are externally observable.

This does not mean all responses must be identical.

The goal is to avoid creating useful cross-site oracles.

---

# Defense 10: Minimise Sensitive Cross-Site Functionality

Ask:

```text
Does this endpoint need to work cross-site?
```

If not:

```text
Restrict it
```

using appropriate browser and server controls.

---

# Recommended Layered Model

For a sensitive authenticated application:

```text
Session Cookie
    ↓
Appropriate SameSite

Sensitive Pages
    ↓
frame-ancestors

Top-Level Documents
    ↓
COOP where compatible

Sensitive Resources
    ↓
CORP where appropriate

Cross-Site Requests
    ↓
Fetch Metadata policy

Sensitive Cache
    ↓
Cache-Control

Cross-Window Messaging
    ↓
Strict postMessage origins
```

---

# Important Remediation Principle

Do not recommend every header to every application.

For example:

```text
COOP: same-origin
```

can interfere with legitimate popup workflows.

```text
CORP: same-origin
```

can break public CDN resources.

```text
SameSite=Strict
```

can interfere with legitimate external navigation workflows.

Security controls must match:

```text
Application architecture
```

and:

```text
Required cross-origin behaviour
```

---

# Full Pentesting Checklist

## Architecture

```text
[ ] Target origins mapped
[ ] Authentication domains mapped
[ ] Cross-origin integrations mapped
[ ] Embedded applications identified
[ ] Popup workflows identified
[ ] SSO workflows identified
```

## Sensitive State

```text
[ ] Login state
[ ] Privilege state
[ ] Resource access
[ ] Search results
[ ] User relationships
[ ] Document existence
[ ] Group membership
[ ] Account existence
```

## Response Differences

```text
[ ] Status codes
[ ] Content-Type
[ ] Redirects
[ ] Resource type
[ ] Frame structure
[ ] Cache behaviour
[ ] Timing
[ ] postMessage
```

## Browser Primitives

```text
[ ] img
[ ] script
[ ] iframe
[ ] window.open
[ ] navigation
[ ] form
[ ] media
[ ] link
```

## Observables

```text
[ ] load
[ ] error
[ ] frame count
[ ] window behaviour
[ ] navigation
[ ] cache
[ ] timing
[ ] postMessage
```

## Cookies

```text
[ ] Secure
[ ] HttpOnly
[ ] SameSite
[ ] Cross-site cookie behaviour confirmed
```

## Fetch Metadata

```text
[ ] Sec-Fetch-Site
[ ] Sec-Fetch-Mode
[ ] Sec-Fetch-Dest
[ ] Sec-Fetch-User
[ ] Server enforcement tested
```

## Isolation

```text
[ ] CSP frame-ancestors
[ ] X-Frame-Options
[ ] COOP
[ ] COEP
[ ] CORP
```

## Cache

```text
[ ] Sensitive resources identified
[ ] Cache-Control reviewed
[ ] Browser cache behaviour tested
[ ] Cache partitioning considered
```

## Messaging

```text
[ ] postMessage senders
[ ] postMessage receivers
[ ] targetOrigin
[ ] event.origin
[ ] Sensitive messages
```

## Validation

```text
[ ] Controlled accounts used
[ ] Controlled data used
[ ] Multiple repetitions
[ ] Browser recorded
[ ] Browser version recorded
[ ] Network noise considered
[ ] False positives eliminated
```

## Evidence

```text
[ ] Attacker page saved
[ ] Requests saved
[ ] Responses saved
[ ] Browser console captured
[ ] Burp history retained
[ ] Observable documented
[ ] Secret state documented
```

---

# Quick Reference

```text
XS-Leak

Attacker Origin
      ↓
Victim Browser
      ↓
Cross-Origin Interaction
      ↓
Target Application
      ↓
Response Depends on Secret
      ↓
Browser Behaviour Differs
      ↓
Attacker Observes Difference
      ↓
Secret Inferred
```

Common secrets:

```text
Logged in?
Admin?
Resource exists?
Has access?
Search result exists?
Member of group?
```

Common observables:

```text
load/error
frames
window references
navigation
cache
timing
postMessage
```

Important defenses:

```text
SameSite
Fetch Metadata
frame-ancestors
X-Frame-Options
COOP
CORP
COEP
Cache-Control
Strict postMessage origins
```

---

# Pentester Quick Workflow

```text
1. Identify private state

2. Capture state A

3. Capture state B

4. Compare responses

5. Find browser-visible difference

6. Create separate attacker origin

7. Trigger target cross-site

8. Confirm cookies/state

9. Confirm Fetch Metadata

10. Observe browser side channel

11. Repeat test

12. Eliminate noise

13. Determine exactly what is inferred

14. Test relevant defenses

15. Demonstrate with controlled data

16. Report practical impact
```

---

# XS-Leak Decision Tree

```text
Does target behaviour depend
on sensitive user state?
          │
      ┌───┴───┐
      │       │
     NO      YES
      │       │
    STOP      ↓
        Can attacker trigger
        interaction cross-site?
              │
          ┌───┴───┐
          │       │
         NO      YES
          │       │
        STOP      ↓
           Does browser expose
           observable difference?
                  │
              ┌───┴───┐
              │       │
             NO      YES
              │       │
            STOP      ↓
             Is difference reliable?
                      │
                  ┌───┴───┐
                  │       │
                 NO      YES
                  │       │
             Investigate   ↓
                    What information
                    can be inferred?
                          │
                          ↓
                    Assess impact
                          │
                          ↓
                    Minimal proof
                          │
                          ↓
                       Report
```

---

# Key Principle

The most important concept to remember is:

```text
XS-Leak does not usually mean:

Attacker reads cross-origin response.

XS-Leak means:

Attacker learns something
from cross-origin browser behaviour.
```

Or conceptually:

```text
              SAME-ORIGIN POLICY
                      ↓
             Response cannot be
                directly read
                      ↓
                BUT BROWSER
                      ↓
          May expose side effects
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
      Events        Windows        Cache
        ↓             ↓             ↓
   load/error      frame count     timing
        │             │             │
        └─────────────┼─────────────┘
                      ↓
                  OBSERVABLE
                      ↓
                SECRET STATE
                   INFERRED
```

---

# References

## OWASP Cross-Site Leaks Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/XS_Leaks_Cheat_Sheet.html
```

This should be one of the primary references for this note.

It covers:

```text
Same-Origin Policy
SameSite cookies
Element ID attacks
Error events
postMessage
Frame counting
Browser cache
Fetch Metadata
CORP
COOP
Framing protection
```

---

## XS-Leaks Wiki

```text
https://xsleaks.dev/
```

A dedicated reference for XS-Leak techniques and browser side channels.

Use this when researching individual XS-Leak classes.

---

## MDN Cross-Site Leaks

```text
https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XS-Leaks
```

Current browser-focused explanation of XS-Leaks and mitigations.

---

## MDN Same-Origin Policy

```text
https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy
```

Essential background for understanding why XS-Leaks are possible.

---

## MDN Fetch Metadata

```text
https://developer.mozilla.org/en-US/docs/Glossary/Fetch_metadata_request_header
```

Useful background for:

```text
Sec-Fetch-Site
Sec-Fetch-Mode
Sec-Fetch-Dest
Sec-Fetch-User
```

---

## MDN Sec-Fetch-Site

```text
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Sec-Fetch-Site
```

Reference for the request initiator relationship header.

---

## MDN Cross-Origin-Opener-Policy

```text
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy
```

Important reference for window and browsing-context isolation.

---

## MDN Cross-Origin-Resource-Policy

```text
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy
```

Reference for restricting cross-origin resource loading.

---

## MDN Cross-Origin-Embedder-Policy

```text
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy
```

Reference for cross-origin embedding restrictions and cross-origin isolation.

---

## MDN Window.postMessage

```text
https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage
```

Reference for secure cross-origin window messaging.

---

## OWASP HTTP Headers Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
```

Useful when reviewing:

```text
COOP
CORP
CSP
Other isolation headers
```

---

## OWASP Content Security Policy Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
```

Useful for:

```text
frame-ancestors
```

and related CSP controls.

---

## PortSwigger BApp Store

```text
https://portswigger.net/bappstore
```

Check current Burp extensions before relying on third-party tooling.

For XS-Leaks, browser behaviour and controlled proof pages are generally more important than a dedicated extension.

---

# Final Testing Model

```text
                         XS-LEAKS
                            │
                            ↓
                  IDENTIFY SECRET STATE
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
          LOGIN           ACCESS         SEARCH
          STATE           STATE          STATE
             │              │              │
             └──────────────┼──────────────┘
                            ↓
                    COMPARE RESPONSES
                            │
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
       RESOURCE          WINDOW             CACHE
       DIFFERENCE        DIFFERENCE         DIFFERENCE
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ↓
                   CROSS-SITE TRIGGER
                            │
      ┌────────────┬────────┼────────┬────────────┐
      ↓            ↓        ↓        ↓            ↓
     IMG         IFRAME   WINDOW   SCRIPT      NAVIGATION
      │            │        │        │            │
      └────────────┴────────┼────────┴────────────┘
                            ↓
                     BROWSER OBSERVABLE
                            │
      ┌────────────┬────────┼────────┬────────────┐
      ↓            ↓        ↓        ↓            ↓
    LOAD         ERROR    FRAMES   TIMING      MESSAGE
      │            │        │        │            │
      └────────────┴────────┼────────┴────────────┘
                            ↓
                         ORACLE
                            │
                      ┌─────┴─────┐
                      ↓           ↓
                  UNRELIABLE   RELIABLE
                      │           │
                      ↓           ↓
                    STOP      WHAT LEAKS?
                                  │
                ┌─────────────────┼─────────────────┐
                ↓                 ↓                 ↓
             LOGIN             ACCESS            DATA
              STATE             STATE          INFERENCE
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  ↓
                            ASSESS IMPACT
                                  ↓
                          CONTROLLED PROOF
                                  ↓
                            CHECK DEFENSES
                                  │
             ┌────────────────────┼────────────────────┐
             ↓                    ↓                    ↓
          REQUEST              WINDOW              RESOURCE
         ISOLATION            ISOLATION            ISOLATION
             ↓                    ↓                    ↓
       Fetch Metadata            COOP                  CORP
       SameSite                  CSP                   COEP
             │              frame-ancestors             │
             └────────────────────┼────────────────────┘
                                  ↓
                            CACHE / MESSAGING
                                  ↓
                          Cache-Control
                          Safe postMessage
                                  ↓
                               REPORT
                                  ↓
                                RETEST
```

The central testing question is:

> **Can an attacker-controlled origin cause the victim's browser to interact with a target whose behaviour depends on private user state, and then distinguish those states through browser-observable behaviour despite being unable to read the cross-origin response directly?**

If the answer is yes, determine **exactly what can be inferred, how reliably it can be inferred, what victim state is required, which browsers are affected, and which isolation boundary is missing or ineffective** before reporting an XS-Leak.
