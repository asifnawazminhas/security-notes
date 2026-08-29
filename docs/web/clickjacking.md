# Clickjacking

Clickjacking is a client-side attack in which a user is tricked into interacting with an application element that is hidden, transparent or visually disguised beneath attacker-controlled content.

The victim believes they are clicking one element:

```text
Visible Attacker-Controlled Page
             ↓
        "Click Here"
```

but their click is actually delivered to another application:

```text
Visible Attacker-Controlled Page
             ↓
Transparent / Hidden iframe
             ↓
Target Application
             ↓
Sensitive Action
```

Clickjacking is sometimes referred to as:

```text
UI redressing
User interface redressing
Frame-based UI manipulation
```

The vulnerability normally exists when a sensitive application can be embedded inside another website without sufficient framing protections.

!!! warning "Authorised Security Testing"
    Perform Clickjacking testing only against applications included in the authorised assessment scope. Use controlled accounts and harmless actions for proof-of-concept testing. Do not cause actions on behalf of real users.

---

# How Clickjacking Works

Consider an application containing:

```html
<button>Delete Account</button>
```

The application may require the user to be authenticated before this button is available.

An attacker cannot necessarily submit the action directly because protections such as:

```text
Authentication
Session cookies
CSRF tokens
```

may prevent direct request forgery.

However, if the application can be loaded inside an iframe, an attacker may attempt to place the legitimate interface underneath another element.

Conceptually:

```text
Attacker Page
      ↓
Loads Target in iframe
      ↓
iframe Positioned Over Decoy Content
      ↓
Victim Clicks Decoy
      ↓
Click Reaches Target Application
      ↓
Authenticated Action Occurs
```

The browser performs the action using the victim's existing authenticated session where cookie and browser policies permit it.

---

# Basic Clickjacking Architecture

```text
┌──────────────────────────────────────┐
│ Attacker-Controlled Page             │
│                                      │
│       Click to continue              │
│              ↓                       │
│ ┌──────────────────────────────────┐ │
│ │ Transparent iframe              │ │
│ │                                  │ │
│ │ Target Application               │ │
│ │                                  │ │
│ │       Sensitive Button           │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

The iframe may be:

```text
Transparent
Nearly transparent
Positioned absolutely
Resized
Layered using z-index
Aligned with another element
```

The attacker attempts to make the user interact with the underlying application without understanding what they are actually clicking.

---

# Clickjacking Preconditions

Several conditions usually need to be present.

```text
Target can be framed
        ↓
Victim can authenticate to target
        ↓
Sensitive UI exists
        ↓
UI can be positioned predictably
        ↓
Victim interaction performs action
```

Important questions include:

```text
Can the target page be loaded in an iframe?

Does authentication remain available inside the iframe?

Does the browser send the required cookies?

Can a meaningful action be triggered with a click?

Does the application require additional confirmation?

Are framing protections present?
```

---

# Initial Testing

The first test is simple:

> Can the page be framed?

Create a minimal local HTML page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking Test</title>
</head>
<body>

<h1>Clickjacking Test</h1>

<iframe
    src="https://target.example/"
    width="1200"
    height="800">
</iframe>

</body>
</html>
```

Open the page in a browser.

Possible results:

```text
Target loads normally
Target refuses to load
Browser displays framing error
Target redirects elsewhere
Authentication disappears
Target loads but session is unavailable
```

---

# Minimal Proof of Concept

For an authorised assessment, begin with a visible iframe.

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking PoC</title>
</head>
<body>

<h1>Authorised Clickjacking Test</h1>

<iframe
    src="https://target.example/account"
    width="1200"
    height="800"
    style="border: 3px solid;">
</iframe>

</body>
</html>
```

Do not immediately make the iframe transparent.

First establish:

```text
Can it be framed?
Does authentication work?
Does the target render correctly?
```

---

# Transparent iframe Test

Once framing has been confirmed, transparency can demonstrate the underlying Clickjacking condition.

Example:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clickjacking PoC</title>

    <style>
        iframe {
            position: absolute;
            width: 1000px;
            height: 700px;
            opacity: 0.2;
            z-index: 2;
        }

        .decoy {
            position: absolute;
            top: 200px;
            left: 300px;
            z-index: 1;
        }
    </style>
</head>

<body>

<div class="decoy">
    <button>Click Here</button>
</div>

<iframe src="https://target.example/account"></iframe>

</body>
</html>
```

During development, keep the iframe partially visible:

```css
opacity: 0.2;
```

This makes alignment easier to verify.

For a controlled proof of concept, the purpose is to demonstrate that an authenticated interface can be overlaid and interacted with.

---

# CSS Positioning

Typical Clickjacking demonstrations rely on CSS properties such as:

```text
position
top
left
width
height
opacity
z-index
```

Example:

```css
iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 1000px;
    height: 700px;
    opacity: 0.1;
    z-index: 2;
}
```

The important security issue is not the CSS itself.

The issue is:

```text
Can an untrusted origin embed the sensitive application?
```

---

# Frameability Test

A useful workflow is:

```text
Interesting Page
      ↓
Inspect Response Headers
      ↓
Check X-Frame-Options
      ↓
Check CSP frame-ancestors
      ↓
Attempt iframe
      ↓
Observe Browser Behaviour
      ↓
Test Authenticated State
      ↓
Identify Sensitive UI
```

---

# X-Frame-Options

`X-Frame-Options` is a response header designed to restrict framing.

Common values are:

```http
X-Frame-Options: DENY
```

and:

```http
X-Frame-Options: SAMEORIGIN
```

---

## DENY

```http
X-Frame-Options: DENY
```

means the page should not be displayed in a frame.

Conceptually:

```text
Any Parent Origin
       ↓
Attempt to Frame
       ↓
Browser Blocks
```

---

## SAMEORIGIN

```http
X-Frame-Options: SAMEORIGIN
```

allows framing only when the relevant origin requirements are satisfied.

Conceptually:

```text
Same Origin
    ↓
Allowed

Different Origin
    ↓
Blocked
```

---

# Content Security Policy

Modern applications can control framing using CSP:

```http
Content-Security-Policy: frame-ancestors 'none';
```

or:

```http
Content-Security-Policy: frame-ancestors 'self';
```

---

## frame-ancestors 'none'

```http
Content-Security-Policy: frame-ancestors 'none';
```

prevents the resource from being embedded in framing contexts.

This is conceptually similar to:

```http
X-Frame-Options: DENY
```

---

## frame-ancestors 'self'

```http
Content-Security-Policy: frame-ancestors 'self';
```

restricts framing to the same origin.

---

## Allowing Specific Origins

Applications that legitimately require framing can define explicit trusted origins.

Conceptually:

```http
Content-Security-Policy: frame-ancestors 'self' https://trusted.example;
```

The policy should be as restrictive as the application's business requirements allow.

---

# CSP frame-src vs frame-ancestors

Do not confuse:

```text
frame-src
```

with:

```text
frame-ancestors
```

They solve different problems.

`frame-src` controls:

```text
What this page may load inside frames
```

while `frame-ancestors` controls:

```text
Which pages may embed this page
```

For Clickjacking protection, the relevant directive is:

```text
frame-ancestors
```

---

# Checking Headers with Burp Suite

Browse to the target page through Burp Proxy.

Inspect the response.

Look for:

```http
X-Frame-Options:
```

and:

```http
Content-Security-Policy:
```

For CSP, specifically inspect:

```text
frame-ancestors
```

Example:

```http
HTTP/1.1 200 OK
Content-Type: text/html
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: frame-ancestors 'self';
```

This indicates explicit framing protection.

---

# Missing Framing Headers

A response such as:

```http
HTTP/1.1 200 OK
Content-Type: text/html
```

with neither:

```text
X-Frame-Options
```

nor:

```text
CSP frame-ancestors
```

is worth investigating.

However:

> Missing headers alone do not automatically demonstrate an exploitable Clickjacking vulnerability.

You should verify actual browser behaviour.

---

# curl Header Check

You can inspect headers using:

```bash
curl -I https://target.example/
```

or:

```bash
curl -s -D - -o /dev/null https://target.example/
```

Look for:

```text
X-Frame-Options
Content-Security-Policy
```

---

# Testing Multiple Pages

Do not test only:

```text
/
```

Framing policies may differ between endpoints.

Test security-sensitive pages such as:

```text
/account
/profile
/settings
/preferences
/security
/admin
/dashboard
/payment
/checkout
/delete
/oauth
```

For example:

```text
/                  → Protected
/account           → Protected
/profile/edit      → Missing protection
/settings/security → Missing protection
```

A single sensitive endpoint without framing protection may still be important.

---

# Authentication and Clickjacking

A Clickjacking vulnerability becomes more interesting when the target remains authenticated inside the iframe.

Test with a controlled account:

```text
Login Normally
      ↓
Open Clickjacking PoC
      ↓
Target Loads in iframe
      ↓
Check Authentication State
```

Possible outcomes:

```text
Authenticated
Unauthenticated
Redirected to login
Blocked by browser
Cookies unavailable
```

---

# SameSite Cookies

Modern cookie behaviour can influence Clickjacking.

A session cookie may use:

```http
SameSite=Strict
```

```http
SameSite=Lax
```

or:

```http
SameSite=None; Secure
```

Whether the cookie is available in a cross-site iframe depends on browser cookie policies and the deployment context.

Therefore:

> Do not determine Clickjacking exploitability solely from framing headers.

Test the real browser behaviour.

---

# Third-Party Cookie Restrictions

Modern browsers increasingly restrict third-party cookies.

This can affect traditional Clickjacking scenarios because the framed target may not receive the victim's authenticated session.

However:

```text
Browser behaviour
Cookie attributes
Same-site relationships
Deployment architecture
Storage partitioning
```

can all influence the result.

Always test with the browsers relevant to the assessment.

---

# Clickjacking and CSRF

Clickjacking and Cross-Site Request Forgery are different vulnerabilities.

CSRF:

```text
Attacker Causes Request
        ↓
Victim Browser Sends Request
        ↓
Application Processes Action
```

Clickjacking:

```text
Attacker Frames Application
        ↓
Victim Physically Clicks
        ↓
Click Reaches Legitimate Interface
        ↓
Application Processes Action
```

A CSRF token may prevent traditional CSRF while Clickjacking remains possible.

Why?

Because the user is interacting with the legitimate application itself.

The legitimate page already contains the required token.

Refer to:

[Cross-Site Request Forgery](csrf.md)

---

# Clickjacking With CSRF Protection

Consider:

```html
<form action="/account/delete" method="POST">

<input
    type="hidden"
    name="csrf"
    value="RANDOM-TOKEN">

<button>Delete Account</button>

</form>
```

An attacker may not know:

```text
RANDOM-TOKEN
```

Therefore direct CSRF could fail.

But if the legitimate page can be framed:

```text
Target Page
    ↓
Contains Valid CSRF Token
    ↓
Victim Clicks Legitimate Button
    ↓
Valid Request Submitted
```

This demonstrates why CSRF protection does not replace anti-framing controls.

---

# Sensitive Actions

Prioritise pages containing actions such as:

```text
Change email
Change profile information
Modify privacy settings
Enable features
Disable features
Delete content
Create resources
Submit forms
Approve requests
Confirm operations
Modify subscriptions
Change notification settings
```

For proof-of-concept testing, use the least destructive action available.

---

# Clickjacking Testing by Business Logic

Do not test Clickjacking as simply:

```text
Does iframe work?
```

Instead ask:

```text
What business actions become possible if framing works?
```

Examples follow.

---

# Account Settings

Suppose the application allows:

```text
Change display name
Change email
Modify profile visibility
```

If the settings page can be framed:

```text
Attacker Page
      ↓
Victim Click
      ↓
Settings Button
      ↓
Account State Changes
```

Use a harmless profile modification with a controlled account to demonstrate the condition.

---

# Administrative Interfaces

If an administrative interface can be framed, the impact may be greater.

Possible actions include:

```text
Approve user
Disable user
Change configuration
Modify permissions
Publish content
Approve request
```

Do not perform destructive administrative actions.

Use a safe test action or stop once sufficient evidence exists.

---

# Financial Applications

Potential actions include:

```text
Add beneficiary
Modify payment preference
Select subscription
Confirm purchase
Change billing setting
```

Financial actions can have real consequences.

Testing should use:

```text
Test environments
Controlled accounts
Sandbox transactions
Explicitly authorised actions
```

---

# SaaS Applications

Interesting actions include:

```text
Invite user
Create project
Change workspace settings
Enable integration
Generate API configuration
Modify notifications
```

Again, the objective is to demonstrate UI redressing, not to cause operational impact.

---

# Multi-Step Clickjacking

Some actions require multiple clicks.

Example:

```text
Open Settings
      ↓
Click Security
      ↓
Click Disable
      ↓
Click Confirm
```

An attacker may theoretically attempt to guide a victim through multiple interactions.

This is known as:

```text
Multi-step Clickjacking
```

For assessment purposes, demonstrate only as much interaction as is required to prove impact.

---

# Clickjacking With Form Input

Some actions require text input before submission.

A basic Clickjacking attack becomes more difficult when the victim must provide unpredictable data.

However, browser UI manipulation may sometimes combine:

```text
Typing
Focus changes
Clicks
Keyboard navigation
```

Do not assume every form is exploitable simply because it can be framed.

Evaluate the complete interaction.

---

# Prepopulated Forms

Applications may prepopulate sensitive forms.

Example:

```text
Email: user@example.com
Privacy: Public
```

If only a single click is required to submit a state change, Clickjacking may be more practical.

---

# Clickjacking and Confirmation Dialogues

A confirmation step can reduce exploitability.

Example:

```text
Delete Account
      ↓
Are you sure?
      ↓
Confirm
```

But it does not necessarily eliminate Clickjacking if both interactions can be manipulated.

Evaluate:

```text
Number of interactions
Predictability of UI
Placement
Timing
Additional authentication
```

---

# Reauthentication

Sensitive operations may require:

```text
Password
MFA
Passkey
Security key
One-time code
```

Reauthentication significantly changes the practical impact of Clickjacking.

Document this clearly.

For example:

```text
Page can be framed
but
sensitive action requires password re-entry
```

This should influence severity.

---

# Frame Busting

Some applications use JavaScript to attempt to prevent framing.

Historical examples include logic conceptually similar to:

```javascript
if (top !== self) {
    top.location = self.location;
}
```

This is often called:

```text
Frame busting
```

JavaScript-based frame busting should not be considered a strong replacement for browser-enforced policies such as:

```text
CSP frame-ancestors
X-Frame-Options
```

---

# Why Frame-Busting JavaScript Is Weaker

Client-side scripts depend on:

```text
JavaScript execution
Browser behaviour
Page loading order
Framing conditions
Implementation correctness
```

Browser-enforced response headers are more appropriate security controls.

---

# Nested Frames

Applications may use legitimate framing internally.

Example:

```text
Parent Application
      ↓
Trusted iframe
      ↓
Embedded Component
```

Before recommending:

```http
frame-ancestors 'none'
```

understand whether framing is part of the application's architecture.

The correct policy may instead allow explicitly trusted origins.

---

# Cross-Origin Framing

The central Clickjacking trust boundary is often:

```text
Trusted Application
        ↓
Embedded by
        ↓
Untrusted Origin
```

For example:

```text
target.example
```

should generally not be frameable by:

```text
attacker.example
```

unless this is intentionally supported.

---

# Same-Origin Framing

Some applications intentionally frame their own content.

A policy such as:

```http
X-Frame-Options: SAMEORIGIN
```

or:

```http
Content-Security-Policy: frame-ancestors 'self';
```

can permit this design while preventing arbitrary third-party framing.

---

# Subdomain Considerations

Suppose an organisation uses:

```text
app.example.com
portal.example.com
support.example.com
```

Do not automatically assume all subdomains should be allowed to frame each other.

Different subdomains may have different trust levels.

Consider:

```text
User-generated content
Third-party hosted subdomains
Legacy applications
Marketing systems
Support platforms
```

The framing policy should reflect actual trust boundaries.

---

# CSP Policy Review

When reviewing:

```http
Content-Security-Policy:
```

identify:

```text
frame-ancestors
```

Example:

```http
Content-Security-Policy:
    default-src 'self';
    frame-ancestors 'self';
```

For Clickjacking, the important portion is:

```text
frame-ancestors 'self'
```

---

# Multiple CSP Policies

Applications may return multiple CSP headers.

Do not inspect only one line and assume the effective policy.

Use browser Developer Tools and actual framing tests to confirm behaviour.

---

# Report-Only CSP

Be careful with:

```http
Content-Security-Policy-Report-Only:
```

A report-only policy does not enforce the restriction.

For example:

```http
Content-Security-Policy-Report-Only: frame-ancestors 'none';
```

should not be treated as equivalent to:

```http
Content-Security-Policy: frame-ancestors 'none';
```

Verify the enforcing policy.

---

# X-Frame-Options and CSP Together

Applications may return both:

```http
X-Frame-Options: SAMEORIGIN
```

and:

```http
Content-Security-Policy: frame-ancestors 'self';
```

This can provide compatibility across different browser environments.

Modern browsers support CSP `frame-ancestors`, while `X-Frame-Options` remains common as an additional defence.

---

# Burp Suite Workflow

A practical workflow is:

```text
Burp Proxy
     ↓
Browse Application
     ↓
HTTP History
     ↓
Identify Sensitive Pages
     ↓
Inspect Response Headers
     ↓
Check X-Frame-Options
     ↓
Check CSP frame-ancestors
     ↓
Build Visible iframe Test
     ↓
Open in Browser
     ↓
Test Authenticated Session
     ↓
Identify Safe Action
     ↓
Build Controlled PoC
     ↓
Document Result
```

---

# Burp Response Analysis

Suppose Burp shows:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Set-Cookie: session=...
```

but no:

```http
X-Frame-Options:
```

and no:

```text
frame-ancestors
```

This should trigger a framing test.

Do not report based solely on the headers.

---

# Browser Developer Tools

Developer Tools can help identify why a frame does not load.

Inspect:

```text
Console
Network
Application
Elements
```

The Console may show browser messages relating to:

```text
X-Frame-Options
CSP
frame-ancestors
Cookie restrictions
Cross-origin behaviour
```

---

# Console Example

When framing is blocked, the browser may report that the page refused to display because of:

```text
X-Frame-Options
```

or:

```text
Content Security Policy
```

The exact message varies by browser.

---

# Clickjacking PoC Development

A good development process is:

```text
1. Start with visible iframe

2. Confirm target loads

3. Confirm authenticated state

4. Resize iframe

5. Identify target element coordinates

6. Position decoy content

7. Reduce opacity gradually

8. Verify alignment

9. Use harmless action

10. Capture evidence
```

This is much more reliable than immediately creating an invisible frame.

---

# Example Controlled PoC

```html
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<title>Authorised Clickjacking Test</title>

<style>

body {
    font-family: sans-serif;
}

.target-frame {
    position: absolute;
    top: 100px;
    left: 100px;
    width: 1000px;
    height: 700px;
    opacity: 0.25;
    z-index: 2;
}

.decoy {
    position: absolute;
    top: 250px;
    left: 300px;
    z-index: 1;
}

</style>

</head>

<body>

<h1>Authorised Clickjacking Test</h1>

<div class="decoy">
    <button>Test Button</button>
</div>

<iframe
    class="target-frame"
    src="https://target.example/account">
</iframe>

</body>

</html>
```

During an authorised test, adjust:

```text
top
left
width
height
```

to match the controlled target page.

---

# Serving the PoC Locally

You can save the proof of concept as:

```text
clickjacking-poc.html
```

and open it directly in the browser.

If browser behaviour requires an HTTP origin, you can serve the directory locally:

```bash
python3 -m http.server 8000
```

Then browse to:

```text
http://127.0.0.1:8000/clickjacking-poc.html
```

This is useful for controlled local testing.

---

# Testing Different Viewports

Clickjacking alignment can depend on:

```text
Screen resolution
Browser window size
Zoom level
Responsive layout
Mobile layout
Application state
```

This affects practical exploitability.

A PoC that works only at one exact resolution may be less reliable than one targeting a stable interface element.

---

# Responsive Applications

Modern applications may reposition buttons based on:

```text
Viewport width
Viewport height
Device type
Navigation state
```

Test whether the sensitive control has a predictable position.

---

# Scroll Position

The target element may not initially be visible.

Clickjacking scenarios can be affected by:

```text
iframe scroll position
Page scrolling
Sticky navigation
Responsive components
Dynamic content
```

Document any interaction required before the sensitive control becomes reachable.

---

# Dynamic Interfaces

Single-page applications may load elements asynchronously.

Example:

```text
iframe loads
    ↓
API request
    ↓
UI renders
    ↓
Button appears
```

Timing can affect alignment.

Do not assume a static HTML proof of concept accurately represents every interaction.

---

# Clickjacking and SPA Applications

Applications built using:

```text
React
Angular
Vue
Next.js
Single-page application frameworks
```

are still subject to framing protections.

The framework itself does not prevent Clickjacking.

Check the HTTP response headers delivered by:

```text
Application
Reverse proxy
CDN
Web server
```

---

# Clickjacking and APIs

Pure JSON APIs generally do not provide clickable user interfaces.

Therefore traditional Clickjacking is primarily relevant to browser-rendered pages.

However, an API-backed web interface may still be vulnerable through its frontend.

---

# Clickjacking and CORS

CORS and Clickjacking address different browser security mechanisms.

CORS controls whether scripts from another origin can read certain cross-origin responses.

Clickjacking concerns whether an application can be visually embedded and interacted with.

Therefore:

```text
Strict CORS
```

does not automatically prevent:

```text
Clickjacking
```

Refer to:

[Cross-Origin Resource Sharing (CORS)](cors.md)

once that page is added.

---

# Clickjacking and SOP

The Same-Origin Policy can prevent an attacker from reading the contents of a cross-origin iframe.

However, Clickjacking does not necessarily require reading the frame.

Conceptually:

```text
Cannot Read iframe
        ≠
Cannot Overlay iframe
```

This distinction is fundamental to understanding Clickjacking.

---

# Testing Administrative Actions Safely

If the application contains administrative functionality, avoid destructive tests.

Prefer actions such as:

```text
Open tab
Change harmless preference
Toggle test setting
Select non-destructive option
Modify controlled test object
```

If simply demonstrating that the sensitive page is frameable is sufficient under the assessment methodology, stop there.

---

# Business Impact Analysis

The severity should be based on what an attacker can realistically cause.

Consider:

```text
Is authentication required?

Does the session work inside the frame?

What action can be triggered?

How many clicks are required?

Is reauthentication required?

Is MFA required?

Does the action have material impact?

Is the UI predictable?

Does browser cookie policy interfere?

Can a realistic victim reach the vulnerable state?
```

---

# Weak Clickjacking Finding

Example:

```text
Public informational page can be framed
```

with no sensitive actions.

This may have little or no security impact.

---

# Stronger Clickjacking Finding

Example:

```text
Authenticated account settings page can be framed
        ↓
Session remains authenticated
        ↓
Sensitive state-changing control is predictable
        ↓
No reauthentication required
        ↓
Controlled action succeeds
```

This provides much stronger evidence.

---

# Do Not Report Headers Alone

Avoid findings such as:

```text
Missing X-Frame-Options
```

without analysing impact.

A better approach is:

```text
1. Identify missing anti-framing controls

2. Verify target can actually be framed

3. Determine whether authentication survives

4. Identify sensitive interaction

5. Demonstrate controlled impact

6. Report the resulting Clickjacking condition
```

---

# Testing Matrix

Create a matrix:

| Endpoint | X-Frame-Options | frame-ancestors | Frames? | Authenticated? | Sensitive Action |
|---|---|---|---:|---:|---|
| `/` | Missing | Missing | Yes | N/A | No |
| `/login` | Missing | Missing | Yes | N/A | No |
| `/account` | Missing | Missing | Yes | Yes | Yes |
| `/security` | SAMEORIGIN | `'self'` | No | N/A | Yes |
| `/admin` | DENY | `'none'` | No | N/A | Yes |

This provides much better assessment coverage than checking only the home page.

---

# Clickjacking Checklist

## Discovery

```text
[ ] Identify sensitive pages
[ ] Identify sensitive buttons
[ ] Identify state-changing actions
[ ] Check authentication requirements
[ ] Check confirmation requirements
[ ] Check reauthentication requirements
```

## Headers

```text
[ ] Check X-Frame-Options
[ ] Check CSP
[ ] Check frame-ancestors
[ ] Check Report-Only CSP
[ ] Check policies on individual endpoints
```

## Browser Testing

```text
[ ] Create visible iframe
[ ] Verify page loads
[ ] Verify authenticated state
[ ] Check browser Console
[ ] Check cookie behaviour
[ ] Check multiple relevant browsers where required
```

## Proof of Concept

```text
[ ] Use controlled account
[ ] Use harmless action
[ ] Keep iframe visible during development
[ ] Align target control
[ ] Reduce opacity
[ ] Verify click reaches target
[ ] Stop after sufficient evidence
```

## Impact

```text
[ ] Identify affected user role
[ ] Determine required interaction
[ ] Determine number of clicks
[ ] Check additional confirmation
[ ] Check MFA or reauthentication
[ ] Assess business impact
```

---

# Clickjacking Decision Tree

```text
Sensitive Page
      ↓
Can It Be Framed?
      ↓
     NO
      ↓
Not Clickjacking Through This Path

      OR

     YES
      ↓
Does Authentication Work in Frame?
      ↓
     NO
      ↓
Impact Likely Reduced

      OR

     YES
      ↓
Sensitive UI Available?
      ↓
     NO
      ↓
Limited Impact

      OR

     YES
      ↓
Can Controlled User Interaction Trigger Action?
      ↓
     YES
      ↓
Additional Confirmation?
      ↓
Reauthentication?
      ↓
Assess Practical Exploitability
      ↓
Document
      ↓
Report
```

---

# Clickjacking Quick Reference

```text
CHECK HEADERS

X-Frame-Options
Content-Security-Policy
```

```text
X-FRAME-OPTIONS

DENY
SAMEORIGIN
```

```text
CSP

frame-ancestors 'none'
frame-ancestors 'self'
```

```text
BASIC TEST

<iframe src="https://target.example/"></iframe>
```

```text
CSS

position: absolute;
opacity: 0.2;
z-index: 2;
```

```text
TEST FLOW

Frame
 ↓
Authentication
 ↓
Sensitive UI
 ↓
Controlled Click
 ↓
State Change
```

---

# Evidence Collection

For a confirmed finding, record:

```text
Affected endpoint
Affected functionality
Required authentication
Affected user role
X-Frame-Options value
CSP frame-ancestors value
Browser tested
Cookie behaviour
Sensitive action
Number of interactions
Reauthentication requirements
Proof-of-concept HTML
Screenshots
Before state
After state
```

---

# Screenshot Evidence

Useful screenshots include:

```text
Target application loaded inside iframe
PoC showing target and decoy alignment
Browser Developer Tools showing relevant headers
State before controlled interaction
State after controlled interaction
```

Avoid capturing unnecessary personal or sensitive information.

---

# Example Finding

```text
Finding:
Clickjacking on Authenticated Account Settings

Affected Endpoint:
/account/settings

Expected:
Sensitive authenticated pages should prevent framing by untrusted origins.

Observed:
The account settings page could be embedded in a cross-origin iframe. The controlled user's authenticated session remained available within the frame, and a harmless account preference could be changed through an overlaid interface.

Anti-Framing Controls:
X-Frame-Options: Missing
CSP frame-ancestors: Missing

Impact:
An attacker could potentially construct a page that visually disguises the framed account settings interface and induces an authenticated user to perform unintended actions.
```

---

# Example Lower-Impact Finding

```text
Finding:
Application Pages Can Be Framed by Arbitrary Origins

Observed:
Several application pages could be embedded within a third-party iframe because no effective X-Frame-Options or CSP frame-ancestors policy was present.

Impact:
The tested public pages did not expose sensitive state-changing functionality. The issue therefore presents limited direct security impact in the tested workflow.

Recommendation:
Implement an appropriate anti-framing policy to prevent future functionality from becoming exposed to UI-redressing attacks.
```

This is more accurate than exaggerating the finding.

---

# Reporting Titles

Prefer specific titles:

```text
Clickjacking on Authenticated Account Settings

Clickjacking Allows UI Redressing of Profile Controls

Sensitive Administrative Page Can Be Framed by Arbitrary Origins

Missing Anti-Framing Protection Allows Clickjacking

Clickjacking on Account Preference Functionality
```

Avoid vague titles such as:

```text
X-Frame-Options Missing
```

when actual Clickjacking has been demonstrated.

---

# Remediation

Modern applications should control which origins may frame sensitive pages.

The preferred control is:

```http
Content-Security-Policy: frame-ancestors 'none';
```

when framing is never required.

---

# Same-Origin Framing

If the application legitimately frames itself:

```http
Content-Security-Policy: frame-ancestors 'self';
```

may be appropriate.

---

# Explicit Trusted Origins

Where specific external applications must frame the page:

```http
Content-Security-Policy: frame-ancestors 'self' https://trusted.example;
```

Use the smallest possible allowlist.

---

# X-Frame-Options

For additional compatibility, applications may also return:

```http
X-Frame-Options: DENY
```

or:

```http
X-Frame-Options: SAMEORIGIN
```

depending on the required architecture.

---

# Sensitive Actions

Anti-framing controls should be combined with security measures appropriate to the action, such as:

```text
CSRF protection
Reauthentication
MFA
Confirmation steps
Secure session management
Authorisation checks
```

Defence in depth is important.

---

# Reverse Proxy Configuration

Anti-framing headers may be added at:

```text
Application
Web server
Reverse proxy
Load balancer
CDN
API gateway
```

Ensure the policy applies consistently to all sensitive HTML responses.

---

# Nginx Example

Conceptually:

```nginx
add_header Content-Security-Policy "frame-ancestors 'self'" always;
add_header X-Frame-Options "SAMEORIGIN" always;
```

The exact configuration should be tested against the application's legitimate framing requirements.

---

# Apache Example

Conceptually:

```apache
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Content-Security-Policy "frame-ancestors 'self'"
```

Again, validate against the actual deployment architecture.

---

# Application-Level Example

Frameworks may also set security headers directly.

The important outcome is that the final HTTP response contains the intended policy consistently.

Test the response after:

```text
Application
Proxy
CDN
Load balancer
```

have all processed it.

---

# Common Mistakes

Avoid relying solely on:

```text
JavaScript frame busting
Hidden form fields
CSRF tokens
CORS
Same-Origin Policy
Referer checks
```

None of these is a direct replacement for a proper anti-framing policy.

---

# Clickjacking vs Related Vulnerabilities

```text
Clickjacking
    ↓
UI interaction is disguised
```

```text
CSRF
    ↓
Cross-site request is induced
```

```text
XSS
    ↓
Attacker-controlled script executes
```

```text
HTML Injection
    ↓
Attacker-controlled markup is rendered
```

```text
Open Redirect
    ↓
Trusted application redirects to external destination
```

These vulnerabilities can sometimes interact, but they should be tested and reported based on the behaviour actually demonstrated.

---

# References

## PortSwigger Web Security Academy: Clickjacking

https://portswigger.net/web-security/clickjacking

PortSwigger provides detailed material covering Clickjacking fundamentals, frame-based attacks and practical testing techniques.

---

## PortSwigger Clickjacking Labs

https://portswigger.net/web-security/all-labs#clickjacking

Useful practical labs for understanding Clickjacking behaviour.

---

## OWASP Clickjacking Defense Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html

Useful defensive guidance covering CSP `frame-ancestors`, `X-Frame-Options`, SameSite cookies and related protections.

---

## MDN: X-Frame-Options

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options

Reference documentation for the `X-Frame-Options` response header.

---

## MDN: CSP frame-ancestors

https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors

Reference documentation for the CSP `frame-ancestors` directive.

---

# Final Clickjacking Testing Model

```text
                    APPLICATION
                         ↓
                 IDENTIFY SENSITIVE UI
                         ↓
                  INSPECT RESPONSE
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                 ↓
 X-Frame-Options                   CSP frame-ancestors
        ↓                                 ↓
        └────────────────┬────────────────┘
                         ↓
                 ATTEMPT FRAMING
                         ↓
                  DOES PAGE LOAD?
                         ↓
                        YES
                         ↓
                AUTHENTICATED STATE?
                         ↓
                        YES
                         ↓
                 SENSITIVE ACTION?
                         ↓
                        YES
                         ↓
                 CONTROLLED ACCOUNT
                         ↓
                  VISIBLE iframe
                         ↓
                  ALIGN INTERFACE
                         ↓
                HARMLESS INTERACTION
                         ↓
                DOES ACTION SUCCEED?
                         ↓
                        YES
                         ↓
              PRACTICAL CLICKJACKING
                         ↓
                ASSESS BUSINESS IMPACT
                         ↓
                      REPORT
```

The key principle is:

> Do not report Clickjacking simply because an anti-framing header is missing. Determine whether an untrusted origin can actually frame the application, whether the victim's authenticated state remains usable, and whether a meaningful action can be triggered through disguised user interaction.
