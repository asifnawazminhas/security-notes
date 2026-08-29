# Third-Party JavaScript Security

Third-party JavaScript is JavaScript loaded or executed by a web application but developed, hosted, managed, or supplied by another party.

Common examples include:

```text
Analytics
Tag managers
Advertising
Customer-support widgets
Chat widgets
Payment integrations
A/B testing
Consent-management platforms
Social-media widgets
CDN-hosted libraries
Monitoring agents
Error tracking
Marketing tools
Authentication widgets
Maps
CAPTCHA services
Video players
Embedded forms
Personalisation services
```

A typical application might load:

```html
<script src="https://analytics.example.net/analytics.js"></script>
```

The important security property is:

```text
Third-party JavaScript
        |
        v
Runs inside the user's browser
        |
        v
Usually executes with the privileges
of the page that included it
```

This creates a significant trust relationship.

If a third-party script executing in the application origin becomes malicious or compromised, it may be able to interact with sensitive application data available to JavaScript.

!!! warning "Authorised Security Testing"
    Only test third-party integrations, domains, scripts, tag managers, APIs, and associated infrastructure that fall within the authorised assessment scope. Do not attempt to compromise a third-party vendor to demonstrate risk. Testing should focus on how the assessed application integrates, constrains, monitors, and trusts third-party code.

---

# Why Third-Party JavaScript Matters

Modern web applications commonly depend on external JavaScript.

For example:

```text
Application
    |
    +-- Application JavaScript
    |
    +-- Analytics
    |
    +-- Tag Manager
    |
    +-- Payment Widget
    |
    +-- Support Chat
    |
    +-- Advertising
```

Each external script introduces another trust relationship.

Conceptually:

```text
Application Security
        |
        v
Depends partly on
        |
        v
Third-Party Security
```

The application owner may securely develop their own code but still load JavaScript controlled by another organisation.

---

# Core Security Problem

Consider:

```html
<script src="https://cdn.vendor.example/widget.js"></script>
```

The browser performs:

```text
Application HTML
      |
      v
Request widget.js
      |
      v
Vendor Server
      |
      v
JavaScript Returned
      |
      v
Browser Executes It
```

If the vendor's infrastructure is compromised:

```text
Vendor Infrastructure
      |
      v
Script Modified
      |
      v
Application Visitors Download It
      |
      v
Modified JavaScript Executes
```

The application does not need to be directly compromised.

---

# Major Risks

OWASP highlights three major risks associated with third-party JavaScript:

```text
Loss of control over changes
        |
        v
Third party can change code

Arbitrary code execution
        |
        v
Third-party JavaScript executes
inside the browser

Sensitive information leakage
        |
        v
Third-party code may access
data available in the page
```

These risks should be considered independently.

---

# Risk 1: Loss of Control

When JavaScript is loaded directly from a third-party server:

```html
<script src="https://vendor.example/script.js"></script>
```

the application owner may not control when that script changes.

For example:

```text
Monday

script.js
Version A
```

then:

```text
Tuesday

script.js
Version B
```

without any change to the application's own source repository.

This can introduce:

```text
Security vulnerabilities
Breaking changes
Unexpected network requests
New data collection
New dependencies
New tracking behaviour
Malicious functionality after compromise
```

---

# Risk 2: Arbitrary JavaScript Execution

JavaScript loaded through a normal `<script>` element is not automatically isolated from the host page.

Conceptually:

```text
Host Page
    |
    +-- First-party JavaScript
    |
    +-- Third-party JavaScript
```

Both may execute within the same page context.

Depending on browser security boundaries and application design, third-party JavaScript may potentially interact with:

```text
DOM content
Forms
Page text
JavaScript variables
Web Storage
Application state
User actions
Network-accessible application APIs
Non-HttpOnly cookies
```

This makes third-party JavaScript similar to deliberately allowing another party to execute code within the client-side application.

---

# Risk 3: Sensitive Data Leakage

Third-party JavaScript may intentionally or unintentionally receive sensitive data.

Examples include:

```text
Page URLs
Query parameters
User identifiers
Email addresses
Form values
Search queries
Product information
Transaction metadata
DOM content
Application state
Analytics events
```

The important question is:

```text
What data can the third party observe?
```

not merely:

```text
What data do we intentionally send?
```

---

# Trust Model

A useful model is:

```text
User
 |
 v
Application
 |
 +------------------+
 |                  |
 v                  v
First-Party JS   Third-Party JS
                    |
                    v
               Vendor Systems
```

Trust therefore extends beyond:

```text
Application server
```

to include:

```text
Vendor
Vendor infrastructure
Vendor CDN
Vendor deployment process
Vendor dependencies
Tag manager
Vendor administrators
```

---

# Third Party vs Third-Party Hosted

These are related but different concepts.

A third-party library might be:

```text
Downloaded
Reviewed
Self-hosted
```

For example:

```html
<script src="/assets/vendor/library.min.js"></script>
```

The code originated from another project but is served by the application.

Alternatively:

```html
<script src="https://cdn.vendor.example/library.min.js"></script>
```

loads the resource directly from another origin.

The second architecture introduces an ongoing runtime dependency on that external host.

---

# Deployment Models

Common third-party JavaScript deployment models include:

```text
Third-party code copied into application

Direct request to vendor

CDN-hosted library

Tag manager

Iframe integration

Server-side integration
```

Each has a different security model.

---

# Direct Vendor Script

Example:

```html
<script src="https://analytics.vendor.example/script.js"></script>
```

Flow:

```text
Browser
   |
   v
Application
   |
   v
Vendor JavaScript
   |
   v
Executed in Page
```

Advantages may include:

```text
Simple integration
Automatic vendor updates
```

Security disadvantages include:

```text
Vendor controls future script content
Runtime dependency on vendor
Vendor compromise affects visitors
Difficult change control
```

---

# Self-Hosted Vendor Script

Another model is:

```text
Vendor
  |
  v
Download Script
  |
  v
Security Review
  |
  v
Host Locally
  |
  v
Application
```

Example:

```html
<script src="/assets/vendor/widget-1.4.2.js"></script>
```

This gives the application owner greater control over when the script changes.

However:

```text
Self-hosting
```

does not automatically mean:

```text
Secure
```

The code itself can still contain vulnerabilities or malicious functionality.

The organisation must also maintain updates.

---

# Tag Managers

Tag managers create a particularly important trust boundary.

Conceptually:

```text
Application
     |
     v
Tag Manager Container
     |
     +-- Analytics
     +-- Advertising
     +-- Marketing
     +-- Tracking
     +-- A/B Testing
     +-- Other Scripts
```

The application may load only:

```text
one tag manager script
```

but that script may dynamically load many additional resources.

---

# Why Tag Managers Increase Complexity

Without a tag manager:

```text
Application Repository
      |
      v
Deployment
      |
      v
Script Change
```

With some tag-manager architectures:

```text
Marketing / Analytics User
      |
      v
Tag Manager Interface
      |
      v
Configuration Published
      |
      v
Browser Immediately Receives
New JavaScript Behaviour
```

This can bypass normal:

```text
Code review
Pull requests
Application testing
Deployment approval
```

unless governance controls exist.

---

# Tag Manager Questions

During an assessment ask:

```text
Who can modify tags?

Who can publish changes?

Is MFA required?

Are changes reviewed?

Are environments separated?

Is there an audit log?

Are production changes approved?

Can arbitrary JavaScript be inserted?

Can tags access the complete DOM?

Can tags read sensitive fields?

Which external domains can tags contact?

Are old accounts removed?
```

---

# Third-Party JavaScript Discovery

The first testing step is inventory.

Conceptually:

```text
Application
    |
    v
Collect JavaScript
    |
    +-- First party
    +-- Third party
    |
    v
Identify External Origins
    |
    v
Classify Purpose
    |
    v
Analyse Trust
```

---

# Browser DevTools

Open:

```text
Developer Tools
    |
    v
Network
    |
    v
Filter:
JS
```

Review:

```text
Request URL
Domain
Initiator
Response
Cookies
Timing
Redirects
```

Pay particular attention to resources loaded from origins different from the application.

---

# Burp Suite Discovery

Burp Proxy is extremely useful for identifying third-party requests.

Workflow:

```text
Browser
    |
    v
Burp Proxy
    |
    v
Application
    |
    +-- First-party requests
    |
    +-- Third-party requests
```

Browse the application normally and review:

```text
Proxy
    |
    v
HTTP history
```

Sort or filter by:

```text
Host
URL
MIME type
Extension
```

---

# Third-Party Inventory

Build an inventory such as:

```text
Host:
analytics.vendor.example

Purpose:
Analytics

Resource:
https://analytics.vendor.example/v3/client.js

Loaded by:
Main application page

SRI:
No

CSP allowed:
Yes

Data transmitted:
Page URL
User identifier
Analytics events
```

Repeat this for each integration.

---

# Useful Inventory Fields

Record:

```text
Domain
Vendor
Script URL
Purpose
Page
Load mechanism
Direct / tag manager
SRI present?
CSP allowed?
Data received
Data transmitted
Cookies involved?
Storage used?
postMessage used?
Sensitive page access?
```

---

# HTML Script Discovery

Search HTML for:

```html
<script
```

Example:

```bash
curl -s https://target.example/ \
| grep -i '<script'
```

This can identify directly declared scripts.

However, it will not necessarily find scripts dynamically loaded by other JavaScript.

---

# Extract External Script Sources

A simple Python helper can inventory external `<script src>` resources from a saved HTML page.

```python
#!/usr/bin/env python3

from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import sys


class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return

        attributes = dict(attrs)

        if "src" in attributes:
            self.scripts.append(attributes["src"])


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <base-url> <html-file>")
    sys.exit(1)

base_url = sys.argv[1]
html_file = sys.argv[2]

with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

parser = ScriptParser()
parser.feed(html)

base_host = urlparse(base_url).hostname

for src in parser.scripts:
    absolute = urljoin(base_url, src)
    host = urlparse(absolute).hostname

    classification = (
        "THIRD-PARTY"
        if host and base_host and host != base_host
        else "FIRST-PARTY"
    )

    print(f"[{classification}] {absolute}")
```

Save as:

```text
script_inventory.py
```

Usage:

```bash
python3 script_inventory.py \
  https://target.example/ \
  index.html
```

!!! note
    Different subdomains may belong to the same organisation. Hostname differences are useful for discovery but do not automatically prove that a resource is controlled by a third party.

---

# Dynamic Script Loading

JavaScript can dynamically create scripts.

Example:

```javascript
const script = document.createElement("script");
script.src = "https://vendor.example/widget.js";
document.head.appendChild(script);
```

Therefore static HTML analysis alone is insufficient.

Use:

```text
Browser Network panel
Burp Proxy
JavaScript source review
```

together.

---

# Search JavaScript for External URLs

For downloaded JavaScript:

```bash
rg -n \
'https?://[A-Za-z0-9._~:/?#\[\]@!$&()*+,;=%-]+' \
.
```

This can reveal:

```text
Analytics endpoints
CDNs
APIs
Telemetry
WebSockets
Additional scripts
Tracking endpoints
```

Treat results as leads.

---

# JS Link Finder

Burp's BApp Store contains:

```text
JS Link Finder
```

It passively scans JavaScript files for endpoint links.

This can help discover:

```text
Additional endpoints
External domains
API paths
Resources referenced by JavaScript
```

It is not specifically a third-party JavaScript security scanner, but it can assist with dependency and external-origin discovery.

Check the current BApp Store entry from:

```text
https://portswigger.net/bappstore
```

---

# JS Miner

The BApp Store also contains:

```text
JS Miner
```

It analyses static files, particularly JavaScript and JSON, for potentially interesting information.

It can complement manual review when looking for:

```text
URLs
Secrets
Endpoints
Interesting strings
Configuration
```

Again:

```text
Finding a URL
```

does not automatically mean:

```text
Third-party security issue
```

---

# Burp Extensions Are Optional

There is no requirement to install a specialised Burp extension to test third-party JavaScript correctly.

A strong baseline is:

```text
Burp Proxy
+
HTTP history
+
Logger
+
Repeater
+
Browser DevTools
+
Manual JavaScript review
```

Dedicated JavaScript extensions can accelerate discovery.

---

# Burp Extension Safety

BApp Store extensions are third-party software.

They may be able to access:

```text
HTTP requests
HTTP responses
Cookies
Tokens
Application data
```

Before installing:

```text
Review source code where possible
Review publisher
Understand external communication
Avoid unnecessary extensions
```

This is especially relevant when testing applications containing sensitive data.

---

# Determine What a Script Can Access

After identifying a third-party script, determine the execution context.

Questions include:

```text
Does it execute directly in the main document?

Is it isolated in an iframe?

What iframe sandbox attributes exist?

Can it access the parent page?

Does it use postMessage?

Can it access Web Storage?

Can it access forms?

Can it read DOM content?

What network destinations does it contact?
```

---

# Main-Document Execution

Consider:

```html
<script src="https://vendor.example/script.js"></script>
```

The script executes as part of the host document.

This means the application should treat the script as highly trusted code.

Conceptually:

```text
Third-Party Script
       |
       v
Host Document
       |
       +-- DOM
       +-- JavaScript state
       +-- Web Storage
       +-- Application functionality
```

Browser security mechanisms still apply, but simply being downloaded from another origin does not sandbox normal script execution away from the embedding document.

---

# Same-Origin Misconception

A common misunderstanding is:

```text
Script comes from vendor.example
therefore it runs under vendor.example
```

For a normal external script included in the page:

```html
<script src="https://vendor.example/script.js"></script>
```

that is not the correct security model.

The downloaded script executes as part of the embedding document's JavaScript environment.

Therefore:

```text
Cross-origin script hosting
```

does not itself provide isolation.

---

# HttpOnly Cookies

Third-party JavaScript running in the page cannot read cookies marked:

```text
HttpOnly
```

through `document.cookie`.

This is an important protection.

However, third-party JavaScript may still be able to:

```text
Trigger application requests
Read DOM data
Read non-HttpOnly cookies
Read accessible Web Storage
Observe application state
Modify page behaviour
```

depending on the application.

Therefore HttpOnly helps protect cookie confidentiality but does not make arbitrary third-party JavaScript harmless.

---

# Web Storage

Review whether sensitive data is stored in:

```text
localStorage
sessionStorage
```

Example:

```javascript
localStorage.getItem("access_token")
```

JavaScript executing in the page's origin can potentially access origin-scoped Web Storage.

Therefore sensitive tokens in Web Storage increase the consequences of malicious script execution.

Refer to:

```text
docs/web/session-management.md
```

---

# DOM Access

Third-party JavaScript may potentially inspect:

```text
Page text
Hidden fields
Forms
Account information
Transaction information
User identifiers
Search terms
Application-generated data
```

depending on how the application is built.

This makes data minimisation important.

---

# Sensitive Form Fields

Pay particular attention to pages containing:

```text
Passwords
Payment details
Personal information
Health information
Authentication codes
Recovery codes
Security answers
```

Ask:

```text
Does third-party JavaScript need to execute here?
```

Often the strongest control is:

```text
Do not load unnecessary third-party scripts
on sensitive pages.
```

---

# Payment Pages

Payment pages deserve special attention.

Conceptually:

```text
Payment Form
    |
    +-- Cardholder Data
    |
    +-- Application JS
    |
    +-- Third-Party JS
```

Any script capable of reading payment fields increases the security impact of a third-party compromise.

Where possible, sensitive payment data should be isolated using architectures provided by trusted payment providers, such as appropriately isolated hosted fields or frames.

---

# Magecart-Style Threat

A common third-party JavaScript threat model is client-side skimming.

Conceptually:

```text
Trusted Script Source
        |
        v
Source Compromised
        |
        v
Malicious JavaScript Added
        |
        v
Customer Opens Checkout
        |
        v
Script Reads Sensitive Form Data
        |
        v
Data Sent Elsewhere
```

This class of attack demonstrates why third-party JavaScript should be treated as part of the application's attack surface.

---

# Data Exfiltration Review

Use Burp and browser DevTools to observe what third-party scripts transmit.

Look for requests such as:

```text
POST /collect
POST /events
POST /analytics
POST /track
GET /pixel
POST /telemetry
```

Review:

```text
Query parameters
Request body
Headers
Cookies
Referrer
```

---

# Example Analytics Request

```http
POST /collect HTTP/1.1
Host: analytics.vendor.example
Content-Type: application/json

{
  "event": "checkout",
  "user": "12345",
  "page": "/checkout"
}
```

Determine whether additional sensitive information is transmitted.

---

# Do Not Assume Analytics Is Harmless

Analytics systems may receive:

```text
Full URLs
Query strings
DOM values
User IDs
Search terms
Page titles
Custom event properties
```

A seemingly harmless configuration can accidentally send:

```text
Reset tokens
Email addresses
Account numbers
Internal identifiers
Sensitive search queries
```

---

# Secrets in URLs

Consider:

```text
https://target.example/reset?token=SECRET
```

If analytics collects the complete page URL:

```text
Browser
   |
   v
Analytics Script
   |
   v
Page URL
   |
   v
Third Party
```

the reset token may be disclosed.

This is why secrets should generally not be placed unnecessarily in URLs.

Refer to:

```text
docs/web/secrets-exposure.md
```

---

# Referrer Leakage

Cross-origin requests may include a:

```text
Referer
```

header according to the applicable Referrer Policy and browser behaviour.

Sensitive information in URLs can therefore create additional disclosure risk.

Review:

```text
Referrer-Policy
```

and avoid placing secrets in URLs in the first place.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# Subresource Integrity

Subresource Integrity, commonly abbreviated:

```text
SRI
```

allows a page to specify an expected cryptographic hash for certain externally loaded resources.

Example:

```html
<script
  src="https://cdn.example.net/library.min.js"
  integrity="sha384-EXPECTED_HASH"
  crossorigin="anonymous">
</script>
```

Conceptually:

```text
Browser
   |
   v
Download Script
   |
   v
Calculate Hash
   |
   v
Compare With Expected Hash
   |
   +-----------+
   |           |
 Match      Mismatch
   |           |
   v           v
Execute       Reject
```

---

# What SRI Protects Against

Without SRI:

```text
Trusted CDN
    |
    v
File Changed
    |
    v
Browser Executes New File
```

With correctly configured SRI:

```text
Trusted CDN
    |
    v
File Changed
    |
    v
Hash Different
    |
    v
Browser Rejects Resource
```

This can reduce the risk that unexpected modifications to an externally hosted static resource are silently executed.

---

# SRI Hash Algorithms

SRI supports cryptographic hashes such as:

```text
sha256
sha384
sha512
```

Example:

```html
integrity="sha384-..."
```

Do not manually invent the value.

It must match the exact resource bytes.

---

# Generate an SRI Hash

For a local copy of an authorised static script:

```bash
openssl dgst -sha384 -binary library.js \
| openssl base64 -A
```

Then prepend:

```text
sha384-
```

Example structure:

```text
sha384-BASE64_HASH
```

---

# Simple SRI Helper

A small Python helper:

```python
#!/usr/bin/env python3

import base64
import hashlib
import sys


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <file>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename, "rb") as f:
    data = f.read()

digest = hashlib.sha384(data).digest()
encoded = base64.b64encode(digest).decode()

print(f"sha384-{encoded}")
```

Save as:

```text
generate_sri.py
```

Usage:

```bash
python3 generate_sri.py library.js
```

---

# SRI Requires Stable Content

SRI works best when a resource has stable content.

Consider:

```html
<script src="https://vendor.example/latest.js"></script>
```

If:

```text
latest.js
```

changes frequently, the expected SRI hash will no longer match.

Therefore versioned immutable resources are easier to protect:

```text
/vendor-3.4.2.min.js
```

rather than:

```text
/latest.js
```

---

# SRI and CORS

For cross-origin resources, SRI interacts with CORS requirements.

A common external-script pattern is:

```html
<script
  src="https://cdn.example.net/library.js"
  integrity="sha384-..."
  crossorigin="anonymous">
</script>
```

The external server must also permit the relevant cross-origin resource request.

Always test the actual browser behaviour after introducing SRI.

---

# Missing SRI

Consider:

```html
<script src="https://cdn.example.net/library.js"></script>
```

versus:

```html
<script
  src="https://cdn.example.net/library.js"
  integrity="sha384-..."
  crossorigin="anonymous">
</script>
```

The second provides browser-enforced integrity checking.

However:

```text
Missing SRI
```

should not automatically be reported as:

```text
Exploitable vulnerability
```

Risk depends on:

```text
Resource type
Hosting architecture
Vendor control
Update model
Sensitivity of page
Other controls
Threat model
```

---

# SRI Does Not Make a Script Safe

Important:

```text
SRI says:

"This is the script I expected."
```

It does not say:

```text
"This script is secure."
```

If the expected script itself contains malicious or vulnerable code:

```text
Hash matches
     |
     v
Browser executes it
```

SRI protects integrity, not trustworthiness.

---

# SRI Does Not Solve Every Third-Party Integration

Some third-party scripts intentionally change frequently.

Examples include:

```text
Tag managers
Analytics bootstraps
Advertising
Dynamic widgets
```

Static SRI hashes may be operationally difficult for such resources.

Alternative architecture may be necessary.

---

# Content Security Policy

Content Security Policy can restrict where scripts are allowed to load from.

Example:

```http
Content-Security-Policy:
  script-src 'self' https://trusted.vendor.example
```

Conceptually:

```text
Browser
   |
   v
Script Requested
   |
   v
Is Source Allowed?
   |
 +--+--+
 |     |
YES    NO
 |     |
 v     v
Load  Block
```

---

# CSP Is an Allowlist Boundary

If the policy contains:

```text
https://trusted.vendor.example
```

then scripts from that allowed source may be trusted by the policy.

Therefore:

```text
Adding a vendor to CSP
```

is a security decision.

Avoid unnecessarily broad source expressions.

---

# Weak CSP Example

```http
Content-Security-Policy:
  script-src 'self' https:
```

This permits scripts from any HTTPS origin under that source expression.

That is much broader than:

```http
Content-Security-Policy:
  script-src 'self' https://analytics.example.net
```

The exact CSP security properties depend on the complete policy.

Refer to:

```text
docs/web/http-security-headers.md
docs/web/xss.md
```

---

# Wildcard CSP

Be cautious with:

```http
script-src *.example.net
```

A wildcard may trust:

```text
Many subdomains
Legacy applications
User-controlled services
Forgotten systems
```

The security of the CSP then depends partly on all matching hosts.

---

# CSP Nonces

A strict CSP can use nonces for scripts authorised by the application.

Conceptually:

```text
Server generates random nonce
       |
       +----------------+
       |                |
       v                v
CSP Header         Script Element
       |                |
       +-------+--------+
               |
               v
          Values Match?
               |
            +--+--+
            |     |
           YES    NO
            |     |
            v     v
         Execute Block
```

Example structure:

```http
Content-Security-Policy:
  script-src 'nonce-RANDOM_VALUE'
```

with:

```html
<script nonce="RANDOM_VALUE">
  // authorised script
</script>
```

The nonce must be unpredictable and generated appropriately for each response.

---

# CSP Hashes

CSP can also trust scripts using cryptographic hashes.

Conceptually:

```text
Expected Script Hash
        |
        v
CSP
        |
        v
Browser Calculates Script Hash
        |
        v
Match?
```

Hash-based policies are useful for static script content.

---

# strict-dynamic

Modern strict CSP designs may use:

```text
'strict-dynamic'
```

with nonces or hashes.

This changes how trust can propagate from an authorised script to scripts it dynamically loads.

Do not add:

```text
'strict-dynamic'
```

without understanding the resulting policy.

CSP should be designed and tested as a complete policy.

---

# CSP Does Not Replace SRI

CSP and SRI answer different questions.

CSP:

```text
Where may scripts load from?
```

SRI:

```text
Is this the exact resource expected?
```

Therefore:

```text
CSP
+
SRI
```

can provide complementary controls for suitable static third-party resources.

---

# Example

```html
<script
  src="https://cdn.example.net/library-3.4.2.js"
  integrity="sha384-EXPECTED_HASH"
  crossorigin="anonymous">
</script>
```

with CSP:

```http
Content-Security-Policy:
  script-src 'self' https://cdn.example.net
```

Conceptually:

```text
Source Allowed by CSP?
        |
        v
       YES
        |
        v
SRI Hash Correct?
        |
        v
       YES
        |
        v
     Execute
```

---

# Iframe Isolation

Another architecture is to place third-party functionality inside an iframe.

Example:

```html
<iframe
  src="https://widget.vendor.example/"
  sandbox>
</iframe>
```

Conceptually:

```text
Main Application
      |
      v
Iframe Boundary
      |
      v
Third-Party Application
```

This can provide stronger isolation than loading arbitrary vendor JavaScript directly into the main document.

---

# iframe sandbox

The:

```text
sandbox
```

attribute restricts iframe capabilities.

Example:

```html
<iframe
  src="https://widget.vendor.example/"
  sandbox="allow-scripts">
</iframe>
```

Permissions should be granted only when required.

Possible sandbox tokens include capabilities related to:

```text
Scripts
Forms
Downloads
Popups
Same-origin treatment
Top-level navigation
```

The exact set should be reviewed against current browser documentation.

---

# Be Careful With allow-same-origin

The combination of:

```text
allow-scripts
```

and:

```text
allow-same-origin
```

can significantly reduce sandbox isolation in some same-origin scenarios.

Do not copy sandbox configurations without understanding:

```text
iframe origin
required functionality
granted capabilities
```

---

# Cross-Origin iframe

Where possible:

```text
Main application:
https://app.example.com

Third-party frame:
https://widget.vendor.example
```

provides a normal cross-origin boundary.

The browser's same-origin policy restricts direct DOM access between these origins.

Communication can then be deliberately implemented using:

```text
postMessage
```

---

# postMessage

Cross-origin frames often communicate using:

```javascript
window.postMessage()
```

Conceptually:

```text
Parent
  |
  | postMessage
  v
Iframe
```

or:

```text
Iframe
  |
  | postMessage
  v
Parent
```

This communication must itself be secured.

---

# postMessage Receiver

Avoid accepting messages from arbitrary origins.

Weak pattern:

```javascript
window.addEventListener("message", function(event) {
    processMessage(event.data);
});
```

Better concept:

```javascript
window.addEventListener("message", function(event) {
    if (event.origin !== "https://trusted.vendor.example") {
        return;
    }

    processMessage(event.data);
});
```

Also validate:

```text
Message structure
Expected type
Expected fields
Allowed actions
```

---

# Dangerous postMessage Target

Avoid unnecessarily using:

```javascript
targetWindow.postMessage(data, "*");
```

for sensitive information.

Prefer an explicit expected target origin where possible.

Refer to:

```text
docs/web/dom-based-vulnerabilities.md
```

---

# Server-Side Integration

Some third-party services do not require vendor JavaScript to execute in the browser.

Instead:

```text
Browser
   |
   v
Application Server
   |
   v
Vendor API
```

This can reduce the amount of third-party code running inside the client application.

Example:

```text
Application receives event
        |
        v
Server sanitises/minimises data
        |
        v
Server calls analytics API
```

This architecture can provide stronger control over:

```text
Data shared
Authentication
Validation
Logging
Network destinations
```

where the vendor supports it.

---

# Data Layer

OWASP describes a data-layer approach for reducing direct third-party access to arbitrary DOM data.

Conceptually:

```text
Sensitive Application DOM
        |
        X
        |
Third-Party Code
```

Instead:

```text
Application
    |
    v
Controlled Data Layer
    |
    +-- event
    +-- page category
    +-- approved identifier
    |
    v
Analytics / Marketing
```

This implements:

```text
Data minimisation
```

and reduces the need for third parties to inspect arbitrary page content.

---

# Data Layer Example

Instead of allowing analytics code to scrape:

```text
document.body
forms
URL
DOM elements
```

the application explicitly exposes:

```javascript
window.analyticsData = {
    pageType: "product",
    productCategory: "books"
};
```

Only non-sensitive approved fields should be exposed.

---

# Sensitive Data Classification

Before integrating a third party, classify data such as:

```text
Public
Internal
Confidential
Authentication data
Financial data
Personal data
Security-sensitive data
```

Then define:

```text
What can the vendor receive?
```

---

# Data Minimisation

Prefer:

```json
{
  "event": "purchase_completed",
  "product_category": "books"
}
```

over sending:

```json
{
  "email": "user@example.com",
  "full_name": "Example User",
  "address": "...",
  "session_token": "...",
  "purchase": "...",
  "page_html": "..."
}
```

unless each field is genuinely required and appropriately governed.

---

# Third-Party Cookies

Third-party services may set or receive cookies depending on:

```text
Browser rules
Cookie attributes
Request context
Storage policies
Vendor architecture
```

Review:

```text
Set-Cookie
Cookie
SameSite
Secure
HttpOnly
Domain
Path
```

Do not assume all vendor requests automatically receive application cookies.

Cookie behaviour is origin/domain and browser-policy dependent.

---

# Credentialed Requests

Review whether vendor scripts call application APIs.

Example:

```javascript
fetch("/api/profile", {
    credentials: "include"
});
```

If the third-party script executes in the application page, it may be able to initiate same-origin application requests.

Authorization must therefore always be enforced server-side.

Never rely on:

```text
Only our JavaScript knows how to call this API.
```

---

# Third-Party Script and CSRF

A malicious script executing directly in the application's page context is generally a stronger capability than traditional cross-site request forgery.

The script may potentially:

```text
Initiate application requests
Read same-origin responses accessible to page JavaScript
Interact with application state
Manipulate the DOM
```

depending on the application's controls.

This reinforces the importance of treating directly executed third-party JavaScript as trusted code.

---

# DOM XSS in Third-Party Scripts

Third-party JavaScript may itself contain client-side vulnerabilities.

Example concept:

```text
location.search
     |
     v
Third-Party Script
     |
     v
innerHTML
```

The vulnerability may exist inside:

```text
Vendor code
```

but affect:

```text
Application users
```

because the script executes on the application's page.

Refer to:

```text
docs/web/dom-based-vulnerabilities.md
docs/web/xss.md
```

---

# Prototype Pollution

Third-party libraries can introduce:

```text
Prototype pollution
```

through unsafe object-merging or property-handling functionality.

Refer to:

```text
docs/web/prototype-pollution.md
```

Dependency scanning can help identify known vulnerable library versions.

---

# Dependency Security

Third-party JavaScript should also be assessed as a dependency.

Questions include:

```text
What library is it?

What version?

Is the version supported?

Are vulnerabilities known?

Who maintains it?

How is it updated?

Is it pinned?

Is integrity checked?
```

Refer to:

```text
docs/web/dependency-security.md
```

---

# Retire.js

For client-side dependency identification, Retire.js can detect known vulnerable JavaScript libraries.

The Burp BApp Store contains a Retire.js extension.

Use results as:

```text
Potential vulnerable dependency
```

and manually confirm:

```text
Library
Version
Advisory
Affected range
Application applicability
```

Refer to:

```text
docs/web/dependency-security.md
```

---

# JavaScript Source Review

Download a script:

```bash
curl -s \
  https://vendor.example/script.js \
  -o vendor-script.js
```

Then inspect:

```bash
less vendor-script.js
```

or search:

```bash
rg -n \
'fetch|XMLHttpRequest|sendBeacon|postMessage|localStorage|sessionStorage|document\.cookie|innerHTML|eval' \
vendor-script.js
```

These are investigation leads.

Their presence alone does not indicate a vulnerability.

---

# Network APIs to Review

Interesting JavaScript APIs include:

```text
fetch
XMLHttpRequest
navigator.sendBeacon
WebSocket
EventSource
```

These may reveal where third-party scripts send information.

---

# Browser Storage APIs

Search for:

```text
localStorage
sessionStorage
document.cookie
indexedDB
```

Determine:

```text
What data is read?

Why?

Where is it sent?
```

---

# DOM APIs

Interesting sinks include:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
eval
Function
setTimeout with string input
```

Context matters.

Do not report based solely on string matching.

---

# JavaScript Beautification

Minified JavaScript can be difficult to review.

Common approaches include:

```text
Browser DevTools pretty-print
IDE formatting
JavaScript beautifiers
```

Always retain the original file for comparison.

---

# Source Maps

Check for:

```text
//# sourceMappingURL=
```

Example:

```javascript
//# sourceMappingURL=widget.js.map
```

Source maps may expose:

```text
Original source
Readable function names
Internal modules
Comments
Endpoints
Configuration
```

Refer to:

```text
docs/web/reconnaissance/javascript-analysis.md
```

---

# Monitor Script Changes

Because third-party resources can change independently of the application, organisations may monitor their content.

A simple defensive concept:

```text
Fetch Approved Script
      |
      v
Calculate Hash
      |
      v
Store Baseline
      |
      v
Fetch Later
      |
      v
Calculate Hash
      |
      v
Compare
```

Unexpected changes can then trigger review.

---

# Simple Script Hashing

For a downloaded script:

```bash
sha256sum vendor-script.js
```

Example output:

```text
HASH  vendor-script.js
```

Later:

```bash
sha256sum vendor-script-new.js
```

Compare the values.

Different hashes mean:

```text
File changed
```

not necessarily:

```text
Malicious change
```

---

# Safe Monitoring Script

A simple helper for an authorised static resource:

```python
#!/usr/bin/env python3

import hashlib
import sys
import urllib.request


if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <url>")
    sys.exit(1)

url = sys.argv[1]

request = urllib.request.Request(
    url,
    headers={
        "User-Agent": "ThirdPartyScriptMonitor/1.0"
    }
)

with urllib.request.urlopen(request, timeout=10) as response:
    data = response.read()

digest = hashlib.sha256(data).hexdigest()

print(f"URL:    {url}")
print(f"Bytes:  {len(data)}")
print(f"SHA256: {digest}")
```

Save as:

```text
hash_remote_script.py
```

Usage:

```bash
python3 hash_remote_script.py \
  https://vendor.example/script.js
```

!!! warning
    Use monitoring only for resources you are authorised to retrieve. Respect application and vendor operational constraints.

---

# Script Version Pinning

Prefer stable versioned resources where supported.

Example:

```text
https://cdn.example.net/library/4.2.1/library.min.js
```

instead of:

```text
https://cdn.example.net/library/latest/library.min.js
```

Version pinning provides:

```text
Predictability
Reviewability
Reproducibility
```

but requires an update process.

---

# Pinning Does Not Replace Updates

A permanently pinned dependency can become vulnerable.

Therefore:

```text
Pin
  |
  v
Monitor
  |
  v
Security Update
  |
  v
Review
  |
  v
Update Hash
  |
  v
Deploy
```

---

# CDN Security

Using a CDN can improve:

```text
Performance
Availability
Caching
```

but introduces trust.

Review:

```text
Who controls the CDN account?

Is MFA enabled?

Who can upload files?

Are objects immutable?

Are logs available?

Can old versions be replaced?

Are deployment credentials protected?
```

---

# CDN Account Compromise

Threat model:

```text
Attacker
   |
   v
CDN Credentials
   |
   v
Replace JavaScript
   |
   v
Application Visitors
   |
   v
Malicious Script Executes
```

SRI can reduce this risk for suitable static resources because unexpected content will not match the configured hash.

---

# Domain Takeover Risk

Third-party resources sometimes reference:

```text
Old vendors
Deprecated SaaS
Expired domains
Abandoned cloud resources
```

Example:

```html
<script src="https://old-widget.example/script.js"></script>
```

If ownership of the referenced resource changes, the trust relationship may change.

Therefore periodically inventory:

```text
External domains
Vendor ownership
DNS records
Active contracts
Resource ownership
```

---

# Remove Unused Integrations

Old integrations are common.

Examples:

```text
Old analytics
Unused chat widget
Previous A/B testing platform
Legacy marketing tags
Deprecated CDN
```

If no longer needed:

```text
Remove it.
```

Every external script creates additional attack surface.

---

# Third-Party JavaScript on Authentication Pages

Review:

```text
Login
Registration
Password reset
MFA
Account recovery
```

Ask:

```text
Which third-party scripts execute here?

Why are they required?

What form data can they observe?

What URLs or tokens can they observe?

Can they access authentication state?
```

Minimise unnecessary integrations on security-sensitive pages.

---

# Password Pages

A third-party script executing directly on a page containing:

```html
<input type="password">
```

may potentially interact with the DOM containing that field.

Browser password-field protections do not make arbitrary JavaScript in the page automatically untrusted or isolated.

Therefore:

```text
Do we need this third-party script here?
```

is an important architectural question.

---

# Password Managers

Do not disable password-manager functionality simply to compensate for third-party JavaScript.

The better control is:

```text
Reduce unnecessary third-party execution
+
Isolate integrations
+
Use strong vendor governance
```

rather than weakening password usability or security.

---

# MFA Pages

Review third-party JavaScript on pages containing:

```text
OTP
Recovery codes
Push approval information
MFA setup secrets
```

Again:

```text
Need-to-execute
```

should be the default decision criterion.

---

# Password Reset Pages

Password-reset URLs may contain security-sensitive values.

Example:

```text
/reset?token=...
```

A third-party analytics system collecting full URLs could receive the token.

Therefore test:

```text
Analytics
Referrer behaviour
Logging
Third-party requests
```

Refer to:

```text
docs/web/password-reset.md
```

---

# Consent Management

Consent-management systems themselves often execute third-party JavaScript.

Review whether:

```text
Non-essential scripts execute before consent

Consent choice is respected

Tags are correctly categorised

Rejected scripts remain blocked
```

Privacy compliance and security are related but not identical.

A security assessment should focus on technical exposure while noting relevant data flows.

---

# Shadow Third Parties

A directly approved vendor may itself load another vendor.

Conceptually:

```text
Application
    |
    v
Vendor A
    |
    v
Vendor B
    |
    v
Vendor C
```

The application owner may only know about:

```text
Vendor A
```

while users execute code from all three.

This is sometimes called a:

```text
third-party chain
```

or further-party dependency.

---

# Discover Script Chains

Use browser DevTools:

```text
Network
    |
    v
Initiator
```

to determine which resource caused another resource to load.

Conceptually:

```text
index.html
   |
   v
tag-manager.js
   |
   +-- analytics.js
   |
   +-- ads.js
   |
   +-- survey.js
```

This is particularly important for tag-manager environments.

---

# Burp Logger

Burp Logger can help investigate:

```text
Requests initiated by extensions
Application requests
Third-party traffic
```

For application testing, Proxy HTTP history remains the primary view for normal browser traffic.

Use filters to isolate vendor domains.

---

# Burp Repeater

Repeater can help inspect third-party endpoints where interaction is within scope.

Example:

```text
Analytics collection endpoint
```

Questions include:

```text
What data is sent?

Is authentication used?

Is sensitive information included?

Does the endpoint require the data?
```

Do not fuzz or attack the vendor's infrastructure unless it is explicitly in scope.

---

# Burp Comparer

Comparer can help compare:

```text
Script Version A
vs
Script Version B
```

or:

```text
Response before login
vs
Response after login
```

This can help identify changing third-party behaviour.

For large JavaScript files, dedicated diff tools may be more convenient.

---

# CSP Testing in Burp

Inspect:

```http
Content-Security-Policy:
```

Identify:

```text
script-src
script-src-elem
default-src
```

depending on the policy.

Record which third-party origins are trusted.

Example:

```http
Content-Security-Policy:
  script-src 'self'
             https://analytics.example.net
             https://support.example.org
```

Build a trust list:

```text
analytics.example.net
support.example.org
```

Then investigate why each is required.

---

# CSP Report-Only

An application may use:

```http
Content-Security-Policy-Report-Only:
```

This allows policy violations to be observed without enforcing the policy.

Useful deployment model:

```text
Design Policy
     |
     v
Report-Only
     |
     v
Observe Violations
     |
     v
Fix Compatibility
     |
     v
Enforce CSP
```

Do not confuse:

```text
Report-Only
```

with:

```text
Enforced protection
```

---

# SRI Testing

Search HTML for:

```text
integrity=
```

Example:

```bash
curl -s https://target.example/ \
| grep -i 'integrity='
```

Then identify external scripts without integrity attributes.

Again:

```text
No SRI
```

is an architectural observation.

Whether it becomes a reportable security finding depends on risk and context.

---

# Verify SRI

Download the exact resource:

```bash
curl -s \
  https://cdn.example.net/library.js \
  -o library.js
```

Generate SHA-384:

```bash
openssl dgst \
  -sha384 \
  -binary library.js \
| openssl base64 -A
```

Compare:

```text
sha384-GENERATED_HASH
```

with:

```html
integrity="sha384-CONFIGURED_HASH"
```

The browser is the authoritative enforcement point, but this is useful for manual validation.

---

# Test SRI Safely

Do not modify a production CDN resource to prove SRI enforcement.

Instead use:

```text
Local test page
Controlled test resource
Staging environment
```

where permitted.

Example concept:

```text
Known script
    |
    v
Correct SRI
    |
    v
Loads
```

then:

```text
Controlled script changed
    |
    v
Hash mismatch
    |
    v
Browser blocks
```

---

# Check Browser Console

SRI and CSP violations are often visible in browser developer tools.

Review:

```text
Console
Network
Security
```

for messages related to:

```text
CSP
Integrity
CORS
Blocked resources
```

---

# CSP and Third-Party Compromise

Suppose CSP allows:

```text
https://analytics.vendor.example
```

If that exact trusted source is compromised:

```text
CSP
```

may still allow scripts from it.

This illustrates why:

```text
CSP source allowlisting
```

and:

```text
SRI
```

solve different problems.

---

# First-Party Proxying

Some organisations proxy third-party resources through their own infrastructure.

Example:

```text
Browser
   |
   v
app.example.com/vendor/script.js
   |
   v
Controlled Retrieval Process
   |
   v
Vendor
```

This can provide:

```text
Change control
Caching
Review
Monitoring
```

but simply proxying live vendor content without integrity or review does not remove the trust problem.

---

# Service Workers

Review whether third-party code can influence:

```text
Service worker registration
Caching
Offline content
```

Service workers are powerful and persist beyond a single page load.

Only trusted application-controlled code should generally manage application service workers.

---

# Web Workers

Some integrations may use:

```text
Worker
SharedWorker
```

Workers provide a different execution environment from the page DOM.

However:

```text
Worker isolation
```

does not automatically make untrusted third-party logic safe.

Review:

```text
Data passed to worker
Network access
Origin
Messages
Imported scripts
```

---

# importScripts

Classic workers can load additional scripts using:

```javascript
importScripts(...)
```

This can introduce additional third-party dependencies.

Inventory worker resources as well as normal page scripts.

---

# ES Modules

Modern applications may use:

```html
<script type="module">
```

or:

```javascript
import something from "https://example.net/module.js";
```

Module dependency graphs can introduce external resources that are less obvious from the initial HTML.

Use:

```text
Network inspection
Source review
Build manifests
```

to discover them.

---

# Dynamic Imports

JavaScript may use:

```javascript
import("https://example.net/module.js");
```

or dynamically generated application paths.

Therefore dependency discovery should include runtime behaviour.

---

# Supply Chain Relationship

Third-party JavaScript is a software supply chain issue.

Conceptually:

```text
Vendor Developer
      |
      v
Vendor Repository
      |
      v
Vendor Build
      |
      v
Vendor CDN
      |
      v
Application User
```

The assessed organisation may have little visibility into the first several stages.

Controls should therefore reduce the consequences of upstream compromise.

---

# Vendor Security Review

Before adopting a high-impact third-party integration consider:

```text
Vendor security maturity
Incident response
Security contact
MFA
Change management
Secure development
Vulnerability disclosure
Dependency management
Infrastructure security
Data handling
Subprocessor relationships
```

Technical controls should complement vendor governance.

---

# Change Management

Third-party changes should be observable.

A useful model:

```text
Vendor Update
     |
     v
Detected
     |
     v
Reviewed
     |
     v
Tested
     |
     v
Approved
     |
     v
Production
```

Direct live loading often reduces this control unless additional mechanisms exist.

---

# Inventory Ownership

Every third-party integration should have an owner.

Record:

```text
Vendor
Business owner
Technical owner
Purpose
Data accessed
Pages loaded
Contract status
Review date
Removal process
```

Without ownership, integrations frequently become forgotten attack surface.

---

# Periodic Review

Periodically ask:

```text
Is the integration still used?

Is the vendor still approved?

Has functionality changed?

Has data collection changed?

Are new domains loaded?

Is SRI still valid?

Is CSP still appropriate?

Are permissions still required?

Has the vendor suffered an incident?
```

---

# Testing Workflow

A practical third-party JavaScript assessment can follow:

```text
1. Browse application through Burp
        |
        v
2. Inventory all JavaScript
        |
        v
3. Identify external origins
        |
        v
4. Identify tag managers
        |
        v
5. Build script dependency chains
        |
        v
6. Classify each vendor
        |
        v
7. Determine execution context
        |
        v
8. Review data accessible to scripts
        |
        v
9. Review outbound data
        |
        v
10. Check sensitive pages
        |
        v
11. Review CSP
        |
        v
12. Review SRI
        |
        v
13. Review iframe isolation
        |
        v
14. Review postMessage
        |
        v
15. Review vulnerable dependencies
        |
        v
16. Review change control
        |
        v
17. Validate findings
        |
        v
18. Report
```

---

# Black-Box Workflow

With no source-code access:

```text
Browser
   |
   v
Burp Proxy
   |
   v
Collect Domains
   |
   v
Collect Scripts
   |
   v
Identify Third Parties
   |
   v
Inspect CSP / SRI
   |
   v
Observe Network Traffic
   |
   v
Review Sensitive Pages
   |
   v
Inspect iframe / postMessage
   |
   v
Analyse Client Dependencies
```

---

# White-Box Workflow

With source access:

```text
Repository
    |
    +-- HTML templates
    +-- JavaScript
    +-- Tag-manager configuration
    +-- Package manifests
    +-- CSP configuration
    +-- Vendor integration code
    |
    v
Third-Party Inventory
    |
    v
Compare With Runtime Traffic
    |
    v
Identify Undocumented Integrations
```

Runtime analysis remains important because tag managers and dynamic scripts may not be obvious from application source alone.

---

# Sensitive Page Matrix

Build a matrix such as:

```text
Page                Third Party        Required?
------------------------------------------------
Login               Analytics          No?
Password Reset      Analytics          No?
Checkout            Payment Provider   Yes
Checkout            Advertising        No?
Account Settings    Support Widget      Maybe
Public Home Page    Analytics          Yes
```

The goal is not:

```text
Remove every third party
```

but:

```text
Minimise unnecessary execution
```

especially on sensitive pages.

---

# Data Flow Matrix

Example:

```text
Vendor          Data             Destination
-------------------------------------------------
Analytics       Page path        analytics.example
Analytics       User ID          analytics.example
Support         Email            support.example
Payment         Payment token    payment.example
```

Then classify:

```text
Necessary?
Sensitive?
Minimised?
Expected?
Documented?
```

---

# Finding: Sensitive Data Sent to Analytics Provider

Example:

```text
Finding:
Sensitive Application Data Disclosed to Third-Party Analytics Provider

Observed:
The application loads a third-party analytics script on an authenticated account page.

During normal application use, the analytics integration transmitted sensitive user information to the external analytics service.

Affected data:
User identifier
Email address
Account metadata

Impact:
Sensitive application data is disclosed to an external third party beyond what is required for the observed analytics functionality. Compromise or misuse of the third-party service could increase the exposure of this information.

Recommendation:
Review the data required by the analytics integration and implement data minimisation. Remove unnecessary sensitive fields, restrict analytics on sensitive pages where possible, and use an explicitly controlled analytics data layer.
```

---

# Finding: Reset Token Disclosed to Third Party

```text
Finding:
Password Reset Token Disclosed to Third-Party Analytics Service

Observed:
The password-reset page included a security token in the page URL.

A third-party analytics integration collected the complete page URL and transmitted it to an external analytics endpoint.

Impact:
Possession of an active password-reset token may allow an unauthorised party to complete the password-reset process for the affected account, depending on token validity and additional application controls.

Recommendation:
Do not expose reset credentials to third-party analytics. Avoid placing long-lived secrets in URLs where possible, prevent analytics from collecting sensitive query parameters, minimise third-party scripts on password-recovery pages, and invalidate any affected tokens.
```

---

# Finding: Unnecessary Third-Party JavaScript on Login Page

```text
Finding:
Unnecessary Third-Party JavaScript Executes on Authentication Page

Observed:
Multiple marketing and analytics scripts execute directly within the application's login page.

The scripts are not required for authentication functionality and execute in the same document as the authentication interface.

Impact:
Compromise of one of the trusted third-party script sources could increase the impact on users visiting the authentication page, including potential access to DOM data and manipulation of authentication-related page behaviour.

Recommendation:
Remove non-essential third-party JavaScript from authentication pages. Where third-party functionality is required, evaluate isolation mechanisms and minimise the data and privileges available to the integration.
```

---

# Finding: Missing SRI on Static External Script

Use this finding carefully.

```text
Finding:
External Static JavaScript Loaded Without Subresource Integrity

Observed:
The application loads a versioned static JavaScript resource directly from an external CDN without an integrity attribute.

The script executes in the application's page context.

Impact:
If the externally hosted resource is unexpectedly modified, browsers have no configured SRI hash with which to detect that content change before execution.

This observation does not by itself demonstrate compromise of the external provider.

Recommendation:
Where operationally suitable, use Subresource Integrity for stable externally hosted scripts and styles. Pin resources to controlled versions and maintain a secure update process. Consider self-hosting where stronger change control is required.
```

---

# Finding: Overly Broad CSP Script Source

```text
Finding:
Overly Broad Content Security Policy Permits Unnecessary Script Origins

Observed:
The application's Content Security Policy permits scripts from a broad source expression that is not limited to the specific external services required by the application.

Impact:
A broad script policy increases the number of locations from which browser-executed JavaScript may be trusted, reducing the effectiveness of CSP as a defence-in-depth control.

Recommendation:
Restrict script sources to the minimum required set and consider a strict nonce-based or hash-based CSP where compatible with the application architecture.
```

---

# Finding: Insecure postMessage Trust

```text
Finding:
Third-Party iframe Message Handler Does Not Validate Sender Origin

Observed:
The application receives postMessage events from an embedded integration but processes message data without verifying event.origin against an explicit trusted origin.

Impact:
An untrusted page capable of obtaining a reference to the receiving window may be able to send crafted messages that are processed as if they originated from the trusted integration.

Recommendation:
Validate event.origin against an explicit allowlist, validate the message schema and permitted actions, and use explicit target origins when sending sensitive postMessage data.
```

---

# Finding Titles

Useful report titles include:

```text
Sensitive Data Disclosed to Third-Party JavaScript Provider

Password Reset Token Disclosed to Analytics Service

Unnecessary Third-Party JavaScript on Authentication Pages

External JavaScript Loaded Without Subresource Integrity

Overly Broad CSP Allows Unnecessary Script Origins

Insecure Third-Party iframe Integration

Third-Party postMessage Handler Does Not Validate Origin

Deprecated Third-Party JavaScript Integration

Vulnerable Third-Party JavaScript Dependency

Uncontrolled Third-Party JavaScript Changes

Sensitive Form Data Accessible to Unnecessary Third-Party Scripts

Tag Manager Allows Unreviewed Production JavaScript Changes

Unused Third-Party Script Increases Client-Side Attack Surface

Sensitive Data Included in Third-Party Analytics Events
```

---

# Severity

Severity depends heavily on context.

Consider:

```text
Data sensitivity
Script privileges
Pages affected
Authentication context
Vendor trust
Ability to change script
SRI
CSP
Isolation
Actual data disclosure
Exploitability
Number of users
Business impact
```

Examples:

```text
Unused analytics script on public page
-> Informational / Low depending on context
```

```text
Sensitive personal data unnecessarily sent to third party
-> Context dependent
```

```text
Password reset token disclosed to external analytics
-> Potentially High depending on token controls
```

```text
Demonstrated malicious script execution through compromised
in-scope integration
-> Potentially High / Critical depending on impact
```

Do not assign severity simply because:

```text
Third-party JavaScript exists.
```

---

# False Positives

## External Domain Does Not Automatically Mean Third Party

Example:

```text
static.example-cdn.com
```

may be owned and controlled by the same organisation.

Confirm ownership before classification.

---

# Missing SRI Is Not Automatic Exploitability

SRI may be:

```text
Not applicable
Operationally incompatible
Compensated by self-hosting
Compensated by immutable controlled delivery
```

Assess the architecture.

---

# CSP Allowlist Does Not Mean Compromise

A CSP entry:

```text
https://vendor.example
```

shows that the application trusts that source.

It does not prove:

```text
vendor.example is vulnerable.
```

---

# Third-Party Request Does Not Mean Data Leak

A request to:

```text
analytics.example
```

is not automatically sensitive.

Inspect:

```text
Actual transmitted data
```

before reporting.

---

# Encoded Data

Analytics payloads may use:

```text
Base64
Compression
Custom encoding
Binary protocols
```

Encoding alone is not encryption.

Decode only where authorised and necessary to understand the data flow.

---

# Evidence Collection

For each relevant integration collect:

```text
Page
Script URL
Vendor
Domain
Purpose
Execution context
SRI status
CSP status
iframe status
Sandbox attributes
Data accessed
Data transmitted
Request evidence
Response evidence
Sensitive fields
Screenshots where useful
```

---

# Evidence Example

```text
Page:
https://target.example/account

Vendor:
Example Analytics

Script:
https://analytics.example/client.js

Execution:
Main document

SRI:
Not present

CSP:
analytics.example allowed

Observed data:
User ID
Account type
Page URL

Sensitive data:
None observed during tested workflow
```

This may be useful documentation without necessarily becoming a vulnerability finding.

---

# Remediation Strategy

Third-party JavaScript security should use layers.

```text
Need Assessment
      |
      v
Minimise Scripts
      |
      v
Choose Trusted Vendor
      |
      v
Control Data
      |
      v
Control Script Source
      |
      v
Integrity / Isolation
      |
      v
Monitor Changes
      |
      v
Review Continuously
```

---

# Remove Unnecessary Third Parties

The strongest control for an unnecessary script is:

```text
Do not load it.
```

This eliminates its:

```text
Execution privilege
Data access
Supply-chain dependency
Network dependency
Maintenance burden
```

---

# Minimise Sensitive Page Exposure

Consider disabling unnecessary third-party scripts on:

```text
Login
MFA
Password reset
Account recovery
Payment
Sensitive profile pages
Administrative interfaces
```

---

# Use SRI Where Appropriate

For stable external static resources:

```text
Version pinning
+
SRI
```

provides stronger control over unexpected changes.

Example:

```html
<script
  src="https://cdn.example.net/library-4.2.1.min.js"
  integrity="sha384-EXPECTED_HASH"
  crossorigin="anonymous">
</script>
```

---

# Use CSP

Use a restrictive CSP to control permitted script execution.

Prefer:

```text
Explicit trust
```

over broad:

```text
https:
*
```

source expressions.

Where feasible, evaluate:

```text
Nonce-based strict CSP
Hash-based strict CSP
```

---

# Isolate Third-Party Functionality

Where the integration permits:

```text
Cross-origin iframe
+
sandbox
+
restricted postMessage
```

can provide a stronger boundary than direct script execution.

---

# Minimise iframe Permissions

Start from:

```html
<iframe sandbox>
```

and add only capabilities required by the integration.

Avoid granting broad sandbox exceptions simply to make an integration work without understanding their effect.

---

# Secure postMessage

Use:

```text
Explicit origin validation
Explicit target origin
Schema validation
Action allowlisting
Minimal data
```

---

# Use Controlled Data Layers

Instead of allowing arbitrary DOM scraping:

```text
Application
     |
     v
Approved Data Object
     |
     v
Vendor
```

Only expose fields that are required.

---

# Protect Vendor Accounts

Third-party administrative accounts should use:

```text
MFA
Least privilege
SSO where appropriate
Strong lifecycle management
Audit logging
Change approval
```

A compromised tag-manager administrator can sometimes have an impact comparable to a compromised application deployment account.

---

# Monitor Third-Party Changes

For high-risk static integrations:

```text
Content hashes
Change alerts
Vendor release monitoring
Dependency scanning
CSP reporting
```

can help detect unexpected behaviour.

---

# Maintain an Inventory

Maintain:

```text
Vendor
Script
Owner
Purpose
Pages
Data
Privileges
Approval
Review date
```

This turns unmanaged external code into an explicit security dependency.

---

# Incident Response

Prepare for:

```text
Vendor compromise
Malicious script
Credential compromise
Unexpected script change
Data disclosure
```

Response may require:

```text
Disable integration
Block domain through CSP
Remove tag
Invalidate exposed tokens
Notify vendor
Review affected sessions
Investigate data exposure
Deploy clean version
Monitor users
```

---

# Emergency Kill Switch

For critical third-party integrations, consider whether the organisation can quickly:

```text
Disable the tag
Remove the script
Change CSP
Disable vendor account
Block outbound data
```

without waiting for a full application release cycle.

This can significantly improve incident response.

---

# Pentesting Checklist

## Inventory

```text
[ ] All JavaScript resources inventoried
[ ] External origins identified
[ ] Vendor ownership confirmed
[ ] Script purpose identified
[ ] Tag managers identified
[ ] Dynamic script loaders identified
[ ] Script dependency chains identified
[ ] Unused integrations identified
```

---

## Execution Context

```text
[ ] Main-document scripts identified
[ ] iframe integrations identified
[ ] Cross-origin boundaries identified
[ ] sandbox attributes reviewed
[ ] Worker scripts reviewed
[ ] Dynamic imports considered
[ ] ES modules considered
```

---

## Sensitive Data

```text
[ ] DOM access considered
[ ] Forms reviewed
[ ] localStorage reviewed
[ ] sessionStorage reviewed
[ ] Cookies reviewed
[ ] URLs reviewed
[ ] Query parameters reviewed
[ ] Analytics events reviewed
[ ] Outbound requests reviewed
```

---

## Sensitive Pages

```text
[ ] Login
[ ] Registration
[ ] MFA
[ ] Password reset
[ ] Account recovery
[ ] Checkout
[ ] Payment
[ ] Profile
[ ] Administration
```

For each ask:

```text
Which third-party scripts execute here?

Are they required?
```

---

## Subresource Integrity

```text
[ ] External static scripts identified
[ ] integrity attributes checked
[ ] Hash algorithm reviewed
[ ] Resource version pinned
[ ] crossorigin behaviour considered
[ ] SRI suitability assessed
```

---

## CSP

```text
[ ] Content-Security-Policy present
[ ] script-src reviewed
[ ] script-src-elem reviewed where applicable
[ ] Broad wildcards identified
[ ] https: source expressions identified
[ ] Third-party origins inventoried
[ ] Nonces reviewed
[ ] Hashes reviewed
[ ] strict-dynamic understood where used
[ ] Report-Only distinguished from enforcement
```

---

## iframe

```text
[ ] Third-party iframe identified
[ ] Origin reviewed
[ ] sandbox present
[ ] Sandbox permissions minimised
[ ] allow-scripts justified
[ ] allow-same-origin justified
[ ] postMessage reviewed
```

---

## postMessage

```text
[ ] event.origin validated
[ ] Message schema validated
[ ] Allowed actions restricted
[ ] targetOrigin explicit
[ ] Sensitive data minimised
```

---

## Dependency Security

```text
[ ] Third-party library identified
[ ] Version identified
[ ] Support status checked
[ ] Known vulnerabilities checked
[ ] Retire.js considered
[ ] Dependency scanner results validated
```

---

## Vendor Governance

```text
[ ] Technical owner identified
[ ] Business owner identified
[ ] Vendor account security reviewed
[ ] MFA enabled where available
[ ] Least privilege applied
[ ] Production publishing controlled
[ ] Audit logging available
[ ] Change approval exists
```

---

## Burp Suite

```text
[ ] Proxy traffic reviewed
[ ] External hosts filtered
[ ] JavaScript responses reviewed
[ ] Initiated requests identified
[ ] Analytics payloads inspected
[ ] Repeater used where appropriate
[ ] Comparer used for script changes where useful
[ ] JS Link Finder considered
[ ] JS Miner considered
[ ] Retire.js considered
```

---

# Quick Reference

```text
APPLICATION
     |
     v
THIRD-PARTY JAVASCRIPT
     |
     +----------------------+
     |                      |
     v                      v
EXECUTION                DATA ACCESS
     |                      |
     +-- DOM                +-- Page data
     +-- Storage            +-- URLs
     +-- Requests           +-- Forms
     +-- Application APIs   +-- Identifiers
     |                      |
     +----------+-----------+
                |
                v
             VENDOR
                |
                v
        SUPPLY CHAIN TRUST
                |
     +----------+-----------+
     |                      |
     v                      v
SCRIPT CHANGES          VENDOR COMPROMISE
     |                      |
     +----------+-----------+
                |
                v
             CONTROLS
                |
     +----------+----------+
     |          |          |
     v          v          v
    SRI        CSP      ISOLATION
     |          |          |
     +----------+----------+
                |
                v
         DATA MINIMISATION
                |
                v
            MONITORING
```

---

# Testing Decision Tree

```text
External JavaScript Found
          |
          v
Who controls it?
          |
      +---+---+
      |       |
    Same     Third
    Org      Party
      |       |
      |       v
      |   Is it required?
      |       |
      |   +---+---+
      |   |       |
      |  NO      YES
      |   |       |
      |   v       v
      | Remove   Where does
      |          it execute?
      |              |
      |       +------+------+
      |       |             |
      |      Main         iframe
      |      Page            |
      |       |              v
      |       |         Sandbox?
      |       |              |
      |       v              v
      |   What data      postMessage
      |   can it access?  secure?
      |       |
      |       v
      |   Sensitive?
      |       |
      |   +---+---+
      |   |       |
      |  YES      NO
      |   |       |
      |   v       v
      | Minimise Continue
      |   |
      |   v
      | Is resource static?
      |   |
      | +-+--+
      | |    |
      |YES   NO
      | |    |
      | v    v
      |SRI? Alternative
      |      controls
      |
      v
Review CSP
      |
      v
Review Vendor Trust
      |
      v
Review Change Control
      |
      v
Monitor
```

---

# Final Testing Model

```text
                    THIRD-PARTY JAVASCRIPT
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
         DISCOVERY         EXECUTION          DATA
             |                |                |
      +------+------+     +---+----+      +----+----+
      |      |      |     |        |      |         |
      v      v      v     v        v      v         v
    HTML   Burp   Runtime Main    iframe   DOM    Network
      |      |      |     Page      |      |         |
      +------+------+     |         |      +----+----+
             |            |         |           |
             v            |         v           v
         INVENTORY        |      sandbox      DATA FLOW
             |            |         |           |
             v            |         v           v
          VENDORS         |    postMessage   SENSITIVE?
             |            |                     |
             +------------+----------+----------+
                                     |
                                     v
                                TRUST MODEL
                                     |
                      +--------------+--------------+
                      |              |              |
                      v              v              v
                    CHANGE         VENDOR         SUPPLY
                    CONTROL       SECURITY        CHAIN
                      |              |              |
                      +--------------+--------------+
                                     |
                                     v
                                  CONTROLS
                                     |
               +---------------------+---------------------+
               |                     |                     |
               v                     v                     v
              SRI                   CSP                 ISOLATION
               |                     |                     |
               +----------+----------+----------+----------+
                          |                     |
                          v                     v
                   DATA MINIMISATION       MONITORING
                          |                     |
                          +----------+----------+
                                     |
                                     v
                                  EVIDENCE
                                     |
                                     v
                                   REPORT
                                     |
                                     v
                                REMEDIATION
                                     |
                                     v
                                   RETEST
```

The key principle is:

> **Loading third-party JavaScript directly into a page is a security trust decision, not merely a frontend implementation detail.**

For every third-party script ask:

```text
Who controls it?

Why is it required?

Where does it execute?

Can it access sensitive DOM data?

Can it access browser storage?

Which application APIs can it invoke?

What data does it transmit?

Where is that data sent?

Does it execute on login, MFA, reset, or payment pages?

Can the vendor change the script without our deployment process?

Is the resource static enough for SRI?

Is the source restricted by CSP?

Could the functionality be isolated in an iframe?

Is postMessage implemented securely?

Can the integration be implemented server-side?

Who can modify the vendor configuration?

Who can publish tag-manager changes?

How would we disable it during an incident?

Do we still need it?
```

A strong baseline workflow is:

```text
Burp Proxy
     +
Browser DevTools
     +
JavaScript inventory
     +
External-origin mapping
     +
Script-chain analysis
     +
Data-flow analysis
     +
Sensitive-page review
     +
SRI review
     +
CSP review
     +
iframe / postMessage review
     +
Dependency analysis
     +
Vendor/change-control review
```

---

# References

## OWASP Third Party JavaScript Management Cheat Sheet

[OWASP Third Party JavaScript Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html)

Covers:

```text
Third-party JavaScript risks
Tag-management architectures
Data layers
Subresource Integrity
iframe containment
CSP
```

---

## OWASP Content Security Policy Cheat Sheet

[OWASP Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

---

## MDN Subresource Integrity

[MDN Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity)

---

## MDN Content Security Policy

[MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)

---

## MDN script-src

[MDN script-src](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src)

---

## MDN iframe sandbox

[MDN iframe sandbox](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/iframe)

---

## MDN postMessage

[MDN postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)

---

## PortSwigger BApp Store

[PortSwigger BApp Store](https://portswigger.net/bappstore)

Useful extensions to investigate for this workflow include:

```text
JS Link Finder
JS Miner
Retire.js
```

Review current extension behaviour and source code before using BApps on sensitive assessments.

---

## PortSwigger Burp Extensions Documentation

[PortSwigger - extensions](https://portswigger.net/burp/documentation/desktop/extend-burp/extensions)

---

# Related Notes

```text
docs/web/dependency-security.md
docs/web/secrets-exposure.md
docs/web/http-security-headers.md
docs/web/reconnaissance/javascript-analysis.md
docs/web/dom-based-vulnerabilities.md
docs/web/xss.md
docs/web/prototype-pollution.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/csp.md
docs/web/cors.md
```
