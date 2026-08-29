# Client-Side JavaScript Source Code Review

Client-side JavaScript is one of the most important areas of web application source-code review because security-sensitive behaviour increasingly occurs inside the browser.

Modern applications may use JavaScript for:

- DOM manipulation
- Routing
- Authentication state
- API communication
- OAuth and OIDC flows
- WebSockets
- Cross-window communication
- Browser storage
- File processing
- URL handling
- Dynamic HTML generation
- Third-party integrations
- Feature flags
- Client-side validation
- Single-page applications
- Service workers
- Web workers
- WebAssembly integration

Client-side JavaScript review differs from server-side review because the browser itself becomes part of the trust boundary.

The fundamental rule is:

```text
Anything controlled by the browser
must ultimately be considered attacker-controlled
by the server.
```

Client-side controls can improve usability and provide defence in depth, but they cannot replace server-side:

```text
Authentication
Authorisation
Validation
Business rules
Tenant isolation
Access control
```

The primary review methodology remains:

```text
SOURCE
  |
  v
Attacker-Controlled Data
  |
  v
TRANSFORMATIONS
  |
  +-- parsing
  +-- decoding
  +-- sanitisation
  +-- filtering
  +-- validation
  +-- object merging
  |
  v
SINK
  |
  v
Security-Sensitive Browser Operation
```

Examples:

```text
location.search
      |
      v
URLSearchParams
      |
      v
innerHTML
```

or:

```text
postMessage
    |
    v
message event
    |
    v
eval()
```

or:

```text
location.hash
     |
     v
redirect logic
     |
     v
location.href
```

The key question is:

```text
Can attacker-controlled data reach a dangerous browser sink
without an effective security control?
```

Remember:

```text
Source found
    !=
Vulnerability
```

and:

```text
Sink found
    !=
Vulnerability
```

A vulnerability normally requires:

```text
Attacker-controlled source
        +
Reachable data flow
        +
Dangerous sink
        +
Missing or ineffective protection
        +
Security impact
```

!!! warning "Authorised Security Testing"
    Perform source-code review and dynamic validation only against applications, repositories and environments for which you have explicit authorisation.

---

# Review Strategy

A practical client-side JavaScript review can follow:

```text
1. Identify JavaScript files

2. Identify JavaScript frameworks

3. Identify application bundles

4. Identify source maps

5. Identify third-party scripts

6. Identify URL-derived sources

7. Identify DOM-derived sources

8. Identify postMessage handlers

9. Identify browser storage usage

10. Identify API requests

11. Identify WebSocket connections

12. Identify dangerous DOM sinks

13. Identify dynamic JavaScript execution

14. Identify redirect sinks

15. Identify dynamic script loading

16. Review HTML sanitisation

17. Review prototype pollution

18. Review DOM clobbering

19. Review client-side authentication logic

20. Review client-side authorisation assumptions

21. Review OAuth/OIDC handling

22. Review secrets and configuration

23. Review CSP and Trusted Types

24. Review third-party JavaScript

25. Review service workers

26. Review Web Workers

27. Review WebAssembly integration

28. Perform source-to-sink tracing

29. Run static analysis

30. Perform variant analysis

31. Validate candidates dynamically where authorised
```

---

# Identify JavaScript Files

Search:

```bash
find . -type f \( \
-name '*.js' \
-o -name '*.mjs' \
-o -name '*.cjs' \
-o -name '*.jsx' \
-o -name '*.ts' \
-o -name '*.tsx' \
\) -print
```

For a downloaded website:

```bash
find . -type f -name '*.js' -print
```

Count:

```bash
find . -type f -name '*.js' | wc -l
```

---

# Identify Source Maps

Search:

```bash
find . -type f -name '*.map' -print
```

Search JavaScript references:

```bash
rg -n \
'sourceMappingURL' \
--glob '*.js' \
.
```

Example:

```javascript
//# sourceMappingURL=app.js.map
```

Source maps may expose:

```text
Original source files
Framework structure
Comments
Internal endpoints
Function names
API calls
Configuration
Development code
Potential secrets
```

Source maps are not automatically vulnerabilities.

Determine whether exposed information has meaningful security impact.

---

# Identify Frameworks

Search package manifests:

```bash
cat package.json
```

Common frameworks and libraries include:

```text
React
Angular
Vue
Svelte
Next.js
Nuxt
jQuery
Alpine.js
Backbone
Ember
Lit
Axios
Lodash
DOMPurify
```

Search:

```bash
rg -n -i \
'react|angular|vue|svelte|next|nuxt|jquery|lodash|dompurify|axios' \
package.json package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
```

---

# Bundled Applications

Production JavaScript may be bundled using:

```text
Webpack
Vite
Rollup
Parcel
esbuild
Turbopack
```

Search:

```bash
find . -maxdepth 3 -type f \( \
-name 'webpack.config.*' \
-o -name 'vite.config.*' \
-o -name 'rollup.config.*' \
-o -name 'next.config.*' \
-o -name 'nuxt.config.*' \
\) -print
```

Bundling can obscure source relationships.

Source maps can greatly improve review quality.

---

# Beautifying JavaScript

Minified JavaScript is difficult to review.

Common tools include:

```bash
npx prettier app.js > app.pretty.js
```

or:

```bash
js-beautify app.js > app.pretty.js
```

Do not modify the original evidence file.

---

# Client-Side Sources

High-value attacker-controlled sources include:

```javascript
location
location.href
location.search
location.hash
location.pathname
document.URL
document.documentURI
document.referrer
window.name
```

Other sources include:

```text
postMessage
localStorage
sessionStorage
IndexedDB
Cookies
WebSocket messages
API responses
DOM attributes
Form values
URL parameters
```

---

# URL Sources

Search:

```bash
rg -n \
'location\.(href|search|hash|pathname|host|hostname)|document\.(URL|documentURI|referrer)|window\.name' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# location.search

Example:

```javascript
const params =
    new URLSearchParams(
        location.search
    );

const name =
    params.get("name");
```

This creates an attacker-controlled source when the URL can be influenced.

---

# location.hash

Example:

```javascript
const section =
    location.hash.substring(1);
```

Fragments are not normally sent to the server.

They are nevertheless attacker-controlled browser input.

---

# document.referrer

Example:

```javascript
const previousPage =
    document.referrer;
```

Do not treat the referrer as trusted security data.

---

# window.name

Search:

```bash
rg -n \
'window\.name' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

`window.name` can persist across navigations and should be treated as untrusted input.

---

# DOM Sources

Form elements:

```javascript
element.value
```

Search:

```bash
rg -n \
'\.value\b|FormData\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Dataset

Example:

```javascript
const id =
    element.dataset.id;
```

Search:

```bash
rg -n \
'\.dataset\b|getAttribute\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

DOM attributes may originate from attacker-controlled HTML or server responses.

---

# Cookies

Search:

```bash
rg -n \
'document\.cookie' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Client-side JavaScript cannot read cookies marked:

```text
HttpOnly
```

Do not assume every cookie is available to JavaScript.

---

# Web Storage

Search:

```bash
rg -n \
'localStorage|sessionStorage' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Common operations:

```javascript
localStorage.getItem()
localStorage.setItem()

sessionStorage.getItem()
sessionStorage.setItem()
```

Data in browser storage should generally be considered attacker-controllable from the application's trust perspective.

---

# IndexedDB

Search:

```bash
rg -n \
'indexedDB|IDBDatabase|IDBObjectStore' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review whether data retrieved from IndexedDB reaches dangerous sinks.

---

# API Responses as Sources

Example:

```javascript
const response =
    await fetch("/api/profile");

const data =
    await response.json();

element.innerHTML =
    data.biography;
```

Flow:

```text
Server-Stored Data
      |
      v
API Response
      |
      v
response.json()
      |
      v
data.biography
      |
      v
innerHTML
```

This can create stored DOM XSS.

---

# Fetch

Search:

```bash
rg -n \
'\bfetch\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Axios

Search:

```bash
rg -n \
'axios\.(get|post|put|patch|delete|request)\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# XMLHttpRequest

Search:

```bash
rg -n \
'XMLHttpRequest|\.open\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Dangerous DOM Sinks

High-value sinks include:

```javascript
innerHTML
outerHTML
insertAdjacentHTML()
document.write()
document.writeln()
```

Search:

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write\(|document\.writeln\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# innerHTML

Candidate:

```javascript
const name =
    new URLSearchParams(
        location.search
    ).get("name");

document.querySelector(
    "#welcome"
).innerHTML =
    name;
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

This is a high-value DOM XSS candidate.

---

# outerHTML

Candidate:

```javascript
element.outerHTML =
    userInput;
```

Search:

```bash
rg -n \
'outerHTML\s*=' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# insertAdjacentHTML

Candidate:

```javascript
element.insertAdjacentHTML(
    "beforeend",
    content
);
```

Search:

```bash
rg -n \
'insertAdjacentHTML\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# document.write

Search:

```bash
rg -n \
'document\.write\(|document\.writeln\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Trace attacker-controlled values carefully.

---

# Safer Text Output

When HTML interpretation is unnecessary:

```javascript
element.textContent =
    value;
```

or:

```javascript
element.innerText =
    value;
```

Search:

```bash
rg -n \
'textContent|innerText' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

These are generally preferable to HTML-parsing sinks when only text output is required.

---

# DOM XSS

The core DOM XSS pattern is:

```text
ATTACKER SOURCE
      |
      v
JavaScript Processing
      |
      v
HTML / JS SINK
```

Example:

```text
location.hash
     |
     v
decodeURIComponent()
     |
     v
innerHTML
```

---

# DOM XSS Sources

Common sources:

```text
location.href
location.search
location.hash
document.URL
document.referrer
window.name
postMessage
localStorage
sessionStorage
API responses
```

---

# DOM XSS Sinks

Common sinks:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
document.writeln
eval
Function
setTimeout with string
setInterval with string
script.src
iframe.src
location
```

The security context differs between sinks.

Do not treat every sink identically.

Refer to:

```text
docs/web/dom-based-vulnerabilities.md
docs/web/xss.md
```

---

# Dynamic JavaScript Execution

High-value sinks:

```javascript
eval()
Function()
new Function()
setTimeout()
setInterval()
```

Search:

```bash
rg -n \
'\beval\(|new Function\(|\bFunction\(|setTimeout\(|setInterval\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# eval()

Candidate:

```javascript
const expression =
    new URLSearchParams(
        location.search
    ).get("expr");

eval(expression);
```

Flow:

```text
location.search
      |
      v
expr
      |
      v
eval()
```

---

# Function Constructor

Candidate:

```javascript
const fn =
    new Function(
        userInput
    );
```

Search:

```bash
rg -n \
'new Function\(|Function\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# setTimeout

This is not inherently dangerous:

```javascript
setTimeout(
    updateUI,
    1000
);
```

A string-based call deserves additional attention:

```javascript
setTimeout(
    userInput,
    1000
);
```

Trace whether strings are evaluated as code.

---

# setInterval

The same distinction applies:

```javascript
setInterval(
    callback,
    1000
);
```

versus attacker-controlled string input.

---

# URL-Based Sinks

High-value URL sinks include:

```javascript
location
location.href
location.assign()
location.replace()
window.open()
```

Search:

```bash
rg -n \
'location\s*=|location\.href\s*=|location\.assign\(|location\.replace\(|window\.open\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Client-Side Open Redirect

Candidate:

```javascript
const next =
    new URLSearchParams(
        location.search
    ).get("next");

location.href =
    next;
```

Flow:

```text
location.search
      |
      v
next
      |
      v
location.href
```

Determine whether arbitrary external destinations are accepted.

Refer to:

```text
docs/web/open-redirect.md
```

---

# URL Validation

A stronger pattern may use the URL parser:

```javascript
const target =
    new URL(
        userInput,
        location.origin
    );

if (
    target.origin ===
    location.origin
) {
    location.assign(
        target.href
    );
}
```

The correct policy depends on the application.

Avoid fragile checks such as:

```javascript
url.startsWith(
    "https://trusted.example"
);
```

without understanding URL parsing and origin boundaries.

---

# javascript: URLs

Review URL assignment where attacker-controlled values can reach navigation or executable URL contexts.

Search:

```bash
rg -n \
'\.href\s*=|setAttribute\(["'\'']href|window\.open\(|location\.' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

The browser context and applicable platform protections must be validated dynamically.

---

# Dynamic Script Loading

Search:

```bash
rg -n \
'createElement\(["'\'']script["'\'']\)|script\.src|appendChild\(.*script|import\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Candidate:

```javascript
const script =
    document.createElement(
        "script"
    );

script.src =
    userInput;

document.head.appendChild(
    script
);
```

Review whether attackers can influence script origins.

---

# Dynamic import()

Search:

```bash
rg -n \
'import\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Dynamic imports are not automatically vulnerable.

Determine whether untrusted input influences module selection or URL resolution.

---

# iframe Sources

Search:

```bash
rg -n \
'iframe|\.src\s*=|srcdoc' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,html}' \
.
```

High-value sinks include:

```javascript
iframe.src
iframe.srcdoc
```

---

# srcdoc

Candidate:

```javascript
iframe.srcdoc =
    userInput;
```

This creates an HTML parsing context.

Review attacker control and sandboxing.

---

# postMessage

Cross-window messaging is a major source of client-side vulnerabilities.

Search:

```bash
rg -n \
'postMessage\(|addEventListener\(["'\'']message|onmessage\s*=' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Sending Messages

Example:

```javascript
targetWindow.postMessage(
    data,
    targetOrigin
);
```

Review the target origin.

---

# Wildcard Target Origin

Candidate:

```javascript
targetWindow.postMessage(
    sensitiveData,
    "*"
);
```

This may expose information to unintended origins depending on window relationships and application flow.

Do not report every wildcard message without establishing impact.

---

# Receiving Messages

Example:

```javascript
window.addEventListener(
    "message",
    event => {
        ...
    }
);
```

The primary questions are:

```text
Is event.origin validated?
Is event.source validated where necessary?
What data is trusted?
Which sinks receive event.data?
```

---

# Missing Origin Validation

Candidate:

```javascript
window.addEventListener(
    "message",
    event => {
        document.querySelector(
            "#result"
        ).innerHTML =
            event.data;
    }
);
```

Flow:

```text
postMessage
    |
    v
event.data
    |
    v
innerHTML
```

---

# Origin Validation

A strict comparison is usually preferable:

```javascript
if (
    event.origin !==
    "https://trusted.example"
) {
    return;
}
```

Avoid fragile patterns such as:

```javascript
event.origin.includes(
    "trusted.example"
);
```

or:

```javascript
event.origin.endsWith(
    "trusted.example"
);
```

unless the exact domain policy has been carefully implemented.

---

# Regex Origin Checks

Candidate:

```javascript
if (
    /trusted\.example/.test(
        event.origin
    )
) {
    ...
}
```

Review regex boundaries carefully.

---

# event.source

For some communication flows, validating only the origin may not be sufficient.

Review whether the application expects a particular:

```text
Window
iframe
popup
parent
opener
```

and whether `event.source` should also be checked.

---

# postMessage Source-to-Sink

```text
Untrusted Window
      |
      v
postMessage()
      |
      v
message event
      |
      v
event.data
      |
      v
innerHTML
```

or:

```text
event.data
    |
    v
location.href
```

or:

```text
event.data
    |
    v
eval()
```

Prioritise these flows.

---

# DOM Clobbering

DOM clobbering occurs when HTML elements alter how JavaScript resolves expected properties or global variables.

This is particularly relevant when JavaScript relies on named DOM elements.

Example HTML:

```html
<form id="config">
</form>
```

JavaScript may reference:

```javascript
window.config
```

because named elements can interact with browser property resolution.

---

# DOM Clobbering Search

Look for implicit globals:

```bash
rg -n \
'window\[[^]]+\]|window\.[A-Za-z_$][A-Za-z0-9_$]*|document\.[A-Za-z_$][A-Za-z0-9_$]*' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Manual review is required because most matches are normal.

---

# Named Elements

Search HTML:

```bash
rg -n \
'(id|name)=["'\''][^"'\'']+' \
--glob '*.{html,htm}' \
.
```

Review JavaScript that assumes global variables correspond to application objects.

---

# Defensive Pattern

Prefer explicit lookups:

```javascript
const config =
    document.getElementById(
        "config"
    );
```

over relying on named properties appearing on `window`.

---

# DOM Clobbering Impact

Clobbering becomes security-relevant when the modified value reaches sinks such as:

```text
script.src
location
iframe.src
innerHTML
dynamic imports
URL construction
security decisions
```

Do not report DOM clobbering without establishing an attacker-controlled HTML primitive and meaningful impact.

---

# Prototype Pollution

Prototype pollution is important in both server-side and client-side JavaScript.

Potential sources:

```text
URL parameters
JSON
postMessage
API responses
localStorage
```

Potential operations:

```javascript
Object.assign()
deep merge
recursive setters
dynamic properties
```

Search:

```bash
rg -n \
'Object\.assign\(|merge\(|mergeWith\(|defaultsDeep\(|set\(|setWith\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Dynamic Property Assignment

Candidate:

```javascript
object[
    key
] =
    value;
```

Search:

```bash
rg -n \
'\[[A-Za-z0-9_.$]+\]\s*=' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review whether attacker-controlled keys can include:

```text
__proto__
constructor
prototype
```

---

# Recursive Property Assignment

Candidate:

```javascript
function setValue(
    object,
    path,
    value
) {
    ...
}
```

Search for utility functions that recursively create object properties.

---

# Prototype Pollution Impact

Pollution itself is only part of the analysis.

Trace polluted properties into gadgets such as:

```text
innerHTML
script.src
iframe.src
fetch options
jQuery configuration
authorisation-like client logic
sanitiser configuration
```

Refer to:

```text
docs/web/prototype-pollution.md
```

---

# Object Spread

Search:

```bash
rg -n \
'\.\.\.[A-Za-z_$][A-Za-z0-9_.$]*' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Object spread is not automatically prototype pollution.

Understand the exact language semantics and data flow before reporting.

---

# jQuery

Legacy and modern applications may use jQuery.

Search:

```bash
rg -n \
'\$\(|jQuery\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# jQuery HTML Sinks

High-value operations include:

```javascript
.html()
.append()
.prepend()
.before()
.after()
.replaceWith()
```

Search:

```bash
rg -n \
'\.(html|append|prepend|before|after|replaceWith)\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Context and jQuery version matter.

---

# jQuery Selector Inputs

Review attacker-controlled input entering `$()`.

The behaviour depends on:

```text
Input format
jQuery version
Browser behaviour
Context
```

Do not classify every dynamic selector as XSS.

---

# React

React applications generally escape values inserted through JSX expressions.

Example:

```jsx
<div>
    {username}
</div>
```

This is different from inserting raw HTML.

---

# dangerouslySetInnerHTML

Search:

```bash
rg -n \
'dangerouslySetInnerHTML' \
--glob '*.{js,jsx,ts,tsx}' \
.
```

Example:

```jsx
<div
    dangerouslySetInnerHTML={{
        __html:
            userContent
    }}
/>
```

Trace the source of `userContent`.

---

# React URL Handling

Review attacker-controlled values used in:

```text
href
src
formAction
redirects
window.location
```

Do not assume React's text escaping makes every URL context safe.

---

# React Client-Side Authorisation

Candidate:

```jsx
{
    user.role === "admin" &&
        <AdminPanel />
}
```

This may correctly control the UI.

It must not be the only control protecting server-side administrative functionality.

---

# Angular

Angular templates provide contextual output encoding and sanitisation mechanisms.

Review explicit bypasses.

Search:

```bash
rg -n \
'bypassSecurityTrust|DomSanitizer|innerHTML' \
--glob '*.{js,ts,html}' \
.
```

---

# Angular DomSanitizer

High-value methods include:

```text
bypassSecurityTrustHtml
bypassSecurityTrustScript
bypassSecurityTrustUrl
bypassSecurityTrustResourceUrl
bypassSecurityTrustStyle
```

Search:

```bash
rg -n \
'bypassSecurityTrust(Html|Script|Url|ResourceUrl|Style)' \
--glob '*.{js,ts}' \
.
```

These APIs do not automatically create vulnerabilities.

Determine whether attacker-controlled values are being explicitly marked trusted.

---

# Angular innerHTML

Example:

```html
<div
    [innerHTML]="content">
</div>
```

Angular may sanitise HTML depending on the context.

Review:

```text
Framework version
Sanitisation
DomSanitizer bypasses
Data source
```

---

# Vue

Vue normally escapes interpolation:

```html
<div>
    {{ username }}
</div>
```

Review:

```text
v-html
dynamic URLs
runtime templates
```

Search:

```bash
rg -n \
'v-html|innerHTML' \
--glob '*.{vue,js,ts}' \
.
```

---

# Vue v-html

Candidate:

```html
<div
    v-html="userContent">
</div>
```

Trace the source of `userContent`.

---

# Svelte

Review Svelte raw HTML:

```text
{@html ...}
```

Search:

```bash
rg -n \
'\{@html' \
--glob '*.{svelte,js,ts}' \
.
```

Example:

```svelte
{@html content}
```

Trace whether `content` is attacker-controlled and appropriately sanitised.

---

# Sanitisation

One of the most common HTML sanitisation libraries is DOMPurify.

Search:

```bash
rg -n \
'DOMPurify|sanitize\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# DOMPurify

Example:

```javascript
const clean =
    DOMPurify.sanitize(
        dirty
    );

element.innerHTML =
    clean;
```

This can be an appropriate pattern for applications that intentionally permit limited HTML.

Review:

```text
DOMPurify version
Configuration
Allowed tags
Allowed attributes
Hooks
Subsequent transformations
```

---

# Sanitisation Mutation

A dangerous design may be:

```text
Untrusted HTML
     |
     v
DOMPurify
     |
     v
Further String Manipulation
     |
     v
innerHTML
```

Post-sanitisation transformations can potentially invalidate assumptions made by the sanitiser.

Review the complete flow.

---

# Custom HTML Sanitisation

Search:

```bash
rg -n -i \
'sanitize|escapeHtml|stripTags|allowedTags|allowedAttributes' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Custom sanitisation implementations deserve careful review.

Regex-based HTML sanitisation should receive additional scrutiny.

---

# Trusted Types

Trusted Types can reduce DOM XSS exposure by restricting assignments to certain injection sinks.

Search:

```bash
rg -n \
'trustedTypes|TrustedHTML|TrustedScript|TrustedScriptURL|require-trusted-types-for|trusted-types' \
.
```

---

# Trusted Types Policy

Example:

```javascript
const policy =
    trustedTypes.createPolicy(
        "default",
        {
            createHTML:
                input =>
                    DOMPurify.sanitize(
                        input
                    )
        }
    );
```

Review policy implementations carefully.

A permissive policy can undermine the protection.

---

# Permissive Trusted Types

Candidate:

```javascript
trustedTypes.createPolicy(
    "default",
    {
        createHTML:
            input =>
                input
    }
);
```

This may effectively convert untrusted strings into trusted HTML without meaningful validation.

---

# CSP

Search HTML and configuration:

```bash
rg -n -i \
'content-security-policy|script-src|default-src|nonce-|unsafe-inline|unsafe-eval|strict-dynamic|require-trusted-types-for' \
.
```

CSP is defence in depth.

It should not replace safe source-to-sink handling.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# Nonces

Search:

```bash
rg -n \
'nonce=' \
--glob '*.{html,htm,js,jsx,ts,tsx}' \
.
```

Review whether nonces are:

```text
Random
Per response
Correctly applied
Not attacker-controlled
```

---

# unsafe-eval

If CSP allows:

```text
'unsafe-eval'
```

then some CSP restrictions on string-to-code APIs are weakened.

Do not automatically report this as a standalone exploitable vulnerability.

Determine whether dangerous code paths exist.

---

# Third-Party JavaScript

Search:

```bash
rg -n \
'<script[^>]+src=' \
--glob '*.{html,htm}' \
.
```

Identify:

```text
CDNs
Analytics
Tag managers
Chat widgets
Payment scripts
Advertising
Monitoring
Support widgets
A/B testing
```

---

# External Script Trust

A third-party script executes with the privileges of the page.

It may access:

```text
DOM
Non-HttpOnly cookies
localStorage
sessionStorage
Page content
JavaScript variables
```

This makes third-party JavaScript part of the application's browser-side trust boundary.

---

# Subresource Integrity

Search:

```bash
rg -n \
'integrity=' \
--glob '*.{html,htm}' \
.
```

Example:

```html
<script
    src="https://cdn.example/library.js"
    integrity="sha384-..."
    crossorigin="anonymous">
</script>
```

SRI can protect eligible externally hosted static resources against unexpected modification.

It is not appropriate for every dynamically changing third-party script.

Refer to:

```text
docs/web/third-party-javascript.md
```

---

# Dynamic Third-Party Scripts

Tag managers may dynamically load additional scripts.

Search:

```bash
rg -n -i \
'googletagmanager|gtm|analytics|segment|hotjar|intercom|zendesk|script\.src' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,html}' \
.
```

Map the actual script dependency chain.

---

# Client-Side Secrets

Search:

```bash
rg -n -i \
'api[_-]?key|secret|client[_-]?secret|access[_-]?token|private[_-]?key|password|bearer' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,json,map}' \
.
```

---

# Public API Keys

Not every API key found in JavaScript is a secret.

Some services intentionally use public browser-side identifiers.

Determine:

```text
What service uses the key?
What permissions does it grant?
Is it intended to be public?
Is it restricted by origin?
Can it perform privileged operations?
Can it incur cost?
```

---

# Build-Time Environment Variables

Frameworks may intentionally expose selected environment variables to browser bundles.

Examples include framework-specific public variable prefixes.

Search:

```bash
rg -n \
'process\.env|import\.meta\.env' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review what values actually reach the browser bundle.

---

# Client-Side Authentication

Search:

```bash
rg -n -i \
'login|logout|authenticated|isAuthenticated|currentUser|accessToken|refreshToken|jwt|bearer|session' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Client-Side Authentication State

Example:

```javascript
if (
    localStorage.getItem(
        "isAdmin"
    ) === "true"
) {
    showAdminPanel();
}
```

This may be acceptable for UI rendering.

It must not be relied upon by the server as proof of authorisation.

---

# Hidden UI Is Not Access Control

Example:

```javascript
if (
    !user.isAdmin
) {
    adminButton.remove();
}
```

This hides the interface.

It does not protect:

```text
/admin
/api/admin
GraphQL mutations
WebSocket events
```

The server must enforce access control.

---

# Discover Hidden Endpoints

Client-side JavaScript frequently reveals endpoints that are not visible through normal navigation.

Search:

```bash
rg -n \
'["'\'']/api/|["'\'']/admin|["'\'']/internal|["'\'']/debug|["'\'']/graphql|["'\'']/auth' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# URL Extraction

Simple candidate search:

```bash
rg -o \
'https?://[^"'\'') ]+' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Also search relative API paths:

```bash
rg -o \
'["'\'']/[A-Za-z0-9_./?&=%:{}-]+' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Expect false positives.

Manual review is required.

---

# API Method Discovery

Search:

```bash
rg -n \
'fetch\(|axios\.(get|post|put|patch|delete)|method\s*:\s*["'\''](GET|POST|PUT|PATCH|DELETE)' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Build an endpoint inventory.

---

# Client-Side Route Discovery

Single-page applications often define routes.

Search React Router:

```bash
rg -n \
'<Route|createBrowserRouter|createHashRouter|useRoutes|path\s*:' \
--glob '*.{js,jsx,ts,tsx}' \
.
```

Angular:

```bash
rg -n \
'Routes\s*=|RouterModule\.forRoot|RouterModule\.forChild|path\s*:' \
--glob '*.{ts,js}' \
.
```

Vue:

```bash
rg -n \
'createRouter|routes\s*:|path\s*:' \
--glob '*.{js,ts,vue}' \
.
```

Client-side routes can reveal hidden functionality but do not prove server-side endpoints are accessible.

---

# Client-Side Authorisation

Search:

```bash
rg -n -i \
'isAdmin|role|roles|permission|permissions|canAccess|hasPermission|authoriz|authoris|featureFlag' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Use these findings to identify security-sensitive functionality for server-side testing.

---

# JWT Handling

Search:

```bash
rg -n -i \
'jwt|decodeJwt|jwtDecode|accessToken|refreshToken|Authorization|Bearer' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# JWT Decode

Client applications often decode JWTs to display user information.

Example:

```javascript
const claims =
    jwtDecode(token);
```

This is not necessarily a vulnerability.

The problem occurs when decoded but unverified claims are treated as authoritative by a security boundary that trusts the browser.

---

# Token Storage

Search:

```bash
rg -n \
'localStorage.*token|sessionStorage.*token|setItem\([^)]*token|getItem\([^)]*token' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review token storage in the application's overall threat model.

Consider:

```text
XSS exposure
Token lifetime
Refresh tokens
Session design
Cookie alternatives
Application architecture
```

Do not automatically classify localStorage token usage as a vulnerability without context.

---

# OAuth and OIDC

Search:

```bash
rg -n -i \
'oauth|oidc|openid|authorization_endpoint|token_endpoint|client_id|redirect_uri|code_verifier|code_challenge|state|nonce' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# OAuth Callback Handling

Review:

```text
Authorization code
State
Nonce
PKCE
Redirect URI
Token storage
Error handling
Account linking
```

---

# State

Search:

```bash
rg -n \
'\bstate\b' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Do not assume any variable named `state` is OAuth state.

Trace the OAuth flow.

---

# PKCE

Search:

```bash
rg -n \
'code_verifier|code_challenge|S256' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# CORS Misconceptions

Client-side JavaScript cannot make an insecure server-side CORS policy safe.

Review JavaScript to understand:

```text
Origins
Credentials
API locations
Authentication mechanisms
```

but validate CORS primarily through server response behaviour.

Search:

```bash
rg -n \
'credentials\s*:|withCredentials|mode\s*:\s*["'\'']cors' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Refer to:

```text
docs/web/cors.md
```

---

# fetch Credentials

Example:

```javascript
fetch(
    "/api/profile",
    {
        credentials:
            "include"
    }
);
```

This indicates cookie credentials may be sent.

Review:

```text
CSRF
CORS
SameSite
Authentication
```

---

# CSRF Tokens

Search:

```bash
rg -n -i \
'csrf|xsrf|x-csrf-token|x-xsrf-token' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Client-side code can reveal how anti-CSRF tokens are obtained and transmitted.

Do not conclude CSRF is absent merely because no token is visible in JavaScript.

Refer to:

```text
docs/web/csrf.md
```

---

# WebSockets

Search:

```bash
rg -n \
'new WebSocket\(|socket\.io|io\(|socket\.emit\(|socket\.on\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# WebSocket URL

Example:

```javascript
const socket =
    new WebSocket(
        "wss://example.com/socket"
    );
```

Map:

```text
Endpoint
Authentication
Messages
Event types
Identifiers
```

---

# WebSocket Messages

Search:

```bash
rg -n \
'\.send\(|\.emit\(|\.on\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Expect many false positives.

Focus on WebSocket objects and Socket.IO instances.

---

# Client-Side Message Inventory

Example:

```text
connect
authenticate
join-room
send-message
delete-message
update-profile
admin-action
```

These can reveal server-side attack surface.

Refer to:

```text
docs/web/websockets.md
```

---

# GraphQL

Search:

```bash
rg -n -i \
'graphql|gql`|query\s+[A-Za-z]|mutation\s+[A-Za-z]|subscription\s+[A-Za-z]' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,graphql,gql}' \
.
```

Client bundles frequently contain:

```text
Queries
Mutations
Fragments
Field names
Object types
Endpoints
```

---

# GraphQL Endpoint

Search:

```bash
rg -n \
'/graphql|graphqlEndpoint|uri\s*:' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# GraphQL Mutations

Search:

```bash
rg -n \
'\bmutation\b' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,graphql,gql}' \
.
```

Mutations reveal high-value operations.

Refer to:

```text
docs/web/graphql.md
```

---

# gRPC-Web

Search:

```bash
rg -n -i \
'grpc-web|protobuf|proto3|grpc' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Client code may expose:

```text
Service names
RPC methods
Message structures
Endpoints
```

Refer to:

```text
docs/web/grpc-security.md
```

---

# Server-Sent Events

Search:

```bash
rg -n \
'EventSource\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Example:

```javascript
const stream =
    new EventSource(
        "/api/events"
    );
```

Review:

```text
Endpoint
Authentication
Sensitive data
Cross-origin behaviour
DOM sinks receiving event data
```

---

# Service Workers

Find:

```bash
find . -type f \( \
-name '*service-worker*.js' \
-o -name 'sw.js' \
-o -name 'serviceWorker.js' \
\) -print
```

Search:

```bash
rg -n \
'serviceWorker\.register|self\.addEventListener\(["'\'']fetch|caches\.open|CacheStorage' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Service Worker Scope

Example:

```javascript
navigator.serviceWorker.register(
    "/sw.js"
);
```

Review:

```text
Worker location
Scope
Caching
Fetch interception
Sensitive responses
Update behaviour
```

---

# Service Worker Cache

Search:

```bash
rg -n \
'caches\.open|cache\.put|cache\.add|cache\.addAll|caches\.match' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review whether sensitive authenticated responses are cached inappropriately.

---

# Service Worker Fetch Handler

Example:

```javascript
self.addEventListener(
    "fetch",
    event => {
        ...
    }
);
```

Trace:

```text
Request
  |
  v
Service Worker
  |
  +-- Network
  |
  +-- Cache
```

Review cache key and user-context assumptions.

---

# Web Workers

Search:

```bash
rg -n \
'new Worker\(|new SharedWorker\(|importScripts\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review worker message handling similarly to `postMessage`.

---

# Worker postMessage

Search:

```bash
rg -n \
'onmessage|postMessage\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Trace worker-controlled or attacker-influenced messages into sensitive operations.

---

# WebAssembly

Search:

```bash
rg -n \
'WebAssembly\.|\.wasm' \
.
```

Client applications may load WebAssembly modules for:

```text
Cryptography
Media processing
Parsing
Games
Security functions
Business logic
```

Do not assume code moved into WebAssembly becomes a security boundary.

---

# Client-Side Cryptography

Search:

```bash
rg -n \
'crypto\.subtle|window\.crypto|getRandomValues|randomUUID' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Web Crypto

Example:

```javascript
crypto.getRandomValues(
    buffer
);
```

This provides cryptographically strong random values through the browser's cryptographic API.

---

# Math.random

Search:

```bash
rg -n \
'Math\.random\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Do not report every use.

Prioritise uses involving:

```text
Security tokens
Password reset values
MFA values
Session identifiers
Cryptographic nonces
```

Client-generated security tokens also require broader architectural review because the client itself is attacker-controlled.

---

# Client-Side Encryption

Search:

```bash
rg -n -i \
'encrypt|decrypt|crypto\.subtle|AES|RSA|PBKDF2|deriveKey|importKey' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review:

```text
Key source
Key storage
Threat model
Nonce / IV
Algorithm
Authentication
Server trust
```

Do not assume client-side encryption protects data from a server that controls the JavaScript delivered to the browser.

---

# File Handling

Search:

```bash
rg -n \
'FileReader|Blob\(|URL\.createObjectURL|showOpenFilePicker|showSaveFilePicker' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review:

```text
File content
Filename
MIME type
Preview rendering
Uploads
Downloads
DOM insertion
```

---

# FileReader

Example:

```javascript
const reader =
    new FileReader();

reader.onload =
    () => {
        preview.innerHTML =
            reader.result;
    };
```

The security significance depends on file type and rendering context.

---

# Blob URLs

Search:

```bash
rg -n \
'URL\.createObjectURL|URL\.revokeObjectURL' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Blob URLs are not automatically dangerous.

Review how their content is generated and where they are used.

---

# Dynamic Downloads

Search:

```bash
rg -n \
'createElement\(["'\'']a["'\'']\)|\.download\s*=|URL\.createObjectURL' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review whether attacker-controlled content or filenames create security or social-engineering risks.

---

# HTML Parsing APIs

Additional APIs deserve review:

```javascript
DOMParser()
Range.createContextualFragment()
```

Search:

```bash
rg -n \
'DOMParser\(|createContextualFragment\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# DOMParser

Candidate:

```javascript
const parser =
    new DOMParser();

const doc =
    parser.parseFromString(
        userInput,
        "text/html"
    );
```

Parsing attacker-controlled HTML is not automatically XSS.

Review what happens to the resulting DOM.

---

# createContextualFragment

Candidate:

```javascript
const fragment =
    range.createContextualFragment(
        userInput
    );

element.appendChild(
    fragment
);
```

Trace attacker control and browser execution behaviour.

---

# setAttribute

Search:

```bash
rg -n \
'setAttribute\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

High-value attributes include:

```text
href
src
srcdoc
action
formaction
style
```

Context matters.

---

# Event Handler Attributes

Search:

```bash
rg -n \
'setAttribute\(["'\'']on[a-z]+' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Dynamic event-handler creation deserves careful review.

---

# Dynamic Event Handlers

Search:

```bash
rg -n \
'\.onclick\s*=|\.onload\s*=|\.onerror\s*=|addEventListener\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Normal callback registration is not dangerous by itself.

Trace dynamic code or attacker-controlled behaviour.

---

# Client-Side Template Systems

Search:

```bash
rg -n -i \
'template|compile|render|handlebars|mustache|nunjucks|lodash\.template' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review whether attacker-controlled input becomes:

```text
Template data
```

or:

```text
Template source
```

These have very different security implications.

---

# Lodash Templates

Search:

```bash
rg -n \
'_\.template\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Trace whether attackers control the template string.

---

# Client-Side HTML Injection

Not every unsafe HTML insertion produces JavaScript execution.

A flow may still permit HTML injection:

```text
location.search
      |
      v
innerHTML
```

with execution constrained by context or browser behaviour.

Determine the actual impact.

Refer to:

```text
docs/web/html-injection.md
```

---

# CSS Injection

Search:

```bash
rg -n \
'\.style\.|style\.cssText|setAttribute\(["'\'']style' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Modern browser behaviour limits many historical CSS attack techniques, but attacker-controlled CSS can still have security or UI impact depending on context.

Avoid overclaiming.

---

# Client-Side Host Handling

Search:

```bash
rg -n \
'location\.(host|hostname|origin)|document\.domain' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review whether host-derived values influence:

```text
API URLs
OAuth redirects
WebSocket endpoints
Security decisions
```

---

# document.domain

Search:

```bash
rg -n \
'document\.domain' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Legacy applications may use `document.domain` to relax same-origin restrictions between related subdomains.

Modern application designs should generally prefer explicit cross-origin communication mechanisms rather than relying on this legacy behaviour.

---

# Origin Checks

Search:

```bash
rg -n \
'location\.origin|event\.origin|new URL\(.*\)\.origin|\.origin\s*===' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review exact comparisons and parsing.

---

# XS-Leaks

Client-side source review can identify features relevant to XS-Leaks, such as:

```text
Cross-origin windows
iframes
window.open
postMessage
resource loading
navigation
timing
```

Search:

```bash
rg -n \
'window\.open\(|iframe|postMessage|performance\.now|PerformanceObserver|onload|onerror' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,html}' \
.
```

Source review alone usually does not prove an XS-Leak.

Browser behaviour and cross-origin response differences must be tested.

Refer to:

```text
docs/web/xs-leaks.md
```

---

# Client-Side Cache

Search:

```bash
rg -n \
'localStorage|sessionStorage|caches\.|CacheStorage|indexedDB' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review whether sensitive data remains after:

```text
Logout
Account switching
Tenant switching
Shared-device use
```

---

# Logout Cleanup

Search:

```bash
rg -n \
'localStorage\.clear|sessionStorage\.clear|removeItem\(|logout' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Do not assume all storage must be cleared.

Identify sensitive state specifically.

---

# Feature Flags

Search:

```bash
rg -n -i \
'featureFlag|feature_flag|features|isEnabled|enabledFeatures' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Client-side feature flags can reveal hidden functionality.

They should not be treated as access-control mechanisms.

---

# Debug Functionality

Search:

```bash
rg -n -i \
'debug|development|devMode|localhost|staging|testMode|console\.log' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review for:

```text
Hidden endpoints
Debug panels
Verbose errors
Test credentials
Internal URLs
Feature switches
```

---

# Environment Detection

Search:

```bash
rg -n \
'NODE_ENV|import\.meta\.env|process\.env|location\.hostname' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Client-side environment checks can expose production/development assumptions.

---

# Hard-Coded Endpoints

Search:

```bash
rg -n \
'https?://|wss?://' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,json}' \
.
```

Look for:

```text
Internal APIs
Staging systems
Development systems
Cloud storage
GraphQL
WebSockets
Admin APIs
Monitoring
```

---

# Internal IP Addresses

Search:

```bash
rg -n \
'\b(10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3})\b' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,json,map}' \
.
```

Internal addresses may constitute information disclosure depending on context and impact.

---

# Cloud Storage URLs

Search:

```bash
rg -n -i \
's3\.amazonaws|blob\.core\.windows|storage\.googleapis|cloudfront|firebaseio|supabase' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,json,map}' \
.
```

Review access controls separately.

---

# Source-to-Sink Analysis

The most valuable part of JavaScript review is connecting sources to sinks.

---

# Example - DOM XSS

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

Code:

```javascript
const params =
    new URLSearchParams(
        location.search
    );

const name =
    params.get("name");

output.innerHTML =
    name;
```

---

# Example - postMessage DOM XSS

```text
Attacker Window
      |
      v
postMessage()
      |
      v
event.data
      |
      v
innerHTML
```

Code:

```javascript
window.addEventListener(
    "message",
    event => {
        output.innerHTML =
            event.data;
    }
);
```

Review origin validation.

---

# Example - Client-Side Open Redirect

```text
location.search
      |
      v
next
      |
      v
location.href
```

Code:

```javascript
const next =
    new URLSearchParams(
        location.search
    ).get("next");

location.href =
    next;
```

---

# Example - Dynamic Script Loading

```text
location.search
      |
      v
scriptUrl
      |
      v
script.src
      |
      v
Browser Script Execution
```

---

# Example - Stored DOM XSS

```text
Attacker Input
      |
      v
Server Database
      |
      v
API Response
      |
      v
response.json()
      |
      v
innerHTML
```

---

# Example - localStorage DOM XSS

```text
localStorage
      |
      v
getItem()
      |
      v
innerHTML
```

The key question becomes:

```text
Can an attacker influence the stored value?
```

---

# Example - Prototype Pollution

```text
location.search
      |
      v
Query Parser
      |
      v
Deep Merge
      |
      v
Object.prototype
      |
      v
Security-Relevant Gadget
```

---

# Example - postMessage Redirect

```text
Attacker Window
      |
      v
postMessage()
      |
      v
event.data.url
      |
      v
location.href
```

---

# Example - Client-Side Authorisation Discovery

```text
JavaScript Bundle
      |
      v
isAdmin Check
      |
      v
Hidden Admin Function
      |
      v
/api/admin/users
```

The client-side check is not necessarily the vulnerability.

The discovered server endpoint should be tested for server-side authorisation.

---

# Reverse Sink Analysis

For large JavaScript bundles, start with high-value sinks.

Example:

```text
innerHTML
    ^
    |
renderMessage()
    ^
    |
handleMessage()
    ^
    |
event.data
```

Search sinks first and trace backwards.

---

# Forward Source Analysis

Start from attacker-controlled sources:

```text
location.search
location.hash
postMessage
localStorage
API response
```

Then trace forward.

Example:

```text
location.hash
     |
     v
parseRoute()
     |
     v
renderContent()
     |
     v
innerHTML
```

---

# High-Value Sink Search

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write\(|document\.writeln\(|\beval\(|new Function\(|\bFunction\(|setTimeout\(|setInterval\(|location\.href\s*=|location\.assign\(|location\.replace\(|window\.open\(|script\.src|srcdoc|dangerouslySetInnerHTML|v-html|\{@html' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,vue,svelte}' \
.
```

---

# High-Value Source Search

```bash
rg -n \
'location\.(href|search|hash|pathname)|document\.(URL|documentURI|referrer|cookie)|window\.name|event\.data|localStorage|sessionStorage|postMessage|URLSearchParams' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# DOM XSS Search

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|document\.writeln|dangerouslySetInnerHTML|v-html|\{@html' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,vue,svelte}' \
.
```

---

# JavaScript Execution Search

```bash
rg -n \
'\beval\(|new Function\(|\bFunction\(|setTimeout\(|setInterval\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Redirect Search

```bash
rg -n \
'location\s*=|location\.href\s*=|location\.assign\(|location\.replace\(|window\.open\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# postMessage Search

```bash
rg -n \
'postMessage\(|addEventListener\(["'\'']message|onmessage\s*=|event\.origin|event\.source|event\.data' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Storage Search

```bash
rg -n \
'localStorage|sessionStorage|indexedDB' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# API Search

```bash
rg -n \
'\bfetch\(|axios\.(get|post|put|patch|delete|request)\(|XMLHttpRequest|/api/' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# WebSocket Search

```bash
rg -n \
'new WebSocket\(|socket\.emit\(|socket\.on\(|io\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# GraphQL Search

```bash
rg -n -i \
'/graphql|\bquery\b|\bmutation\b|\bsubscription\b|gql`' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,graphql,gql}' \
.
```

---

# Prototype Pollution Search

```bash
rg -n \
'Object\.assign\(|merge\(|mergeWith\(|defaultsDeep\(|set\(|setWith\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Sanitisation Search

```bash
rg -n -i \
'DOMPurify|sanitize|escapeHtml|trustedTypes|TrustedHTML|bypassSecurityTrust' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Secret Search

```bash
rg -n -i \
'api[_-]?key|secret|client[_-]?secret|access[_-]?token|refresh[_-]?token|private[_-]?key|password|bearer' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,json,map}' \
.
```

---

# Endpoint Search

```bash
rg -n \
'https?://|wss?://|/api/|/graphql|/admin|/internal|/debug' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,json,map}' \
.
```

---

# Broad JavaScript Review Search

```bash
rg -n \
'location\.(href|search|hash|pathname)|document\.(URL|documentURI|referrer|cookie)|window\.name|event\.data|localStorage|sessionStorage|innerHTML|outerHTML|insertAdjacentHTML|document\.write\(|document\.writeln\(|\beval\(|new Function\(|setTimeout\(|setInterval\(|location\.href\s*=|location\.assign\(|location\.replace\(|window\.open\(|postMessage\(|addEventListener\(["'\'']message|script\.src|srcdoc|dangerouslySetInnerHTML|Object\.assign\(|merge\(|DOMPurify|trustedTypes|\bfetch\(|axios\.|new WebSocket\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Treat this as candidate discovery.

Not vulnerability confirmation.

---

# Static Analysis

Useful tools include:

```text
Semgrep
CodeQL
ESLint
Retire.js
Dependency scanners
Custom grep/ripgrep
```

---

# Semgrep

Run:

```bash
semgrep scan \
--config auto \
.
```

Semgrep can help identify:

```text
DOM XSS
Dynamic code execution
Unsafe framework APIs
Potential prototype pollution
Hard-coded secrets
Dangerous URL handling
```

Manual validation remains necessary.

---

# CodeQL

CodeQL supports JavaScript and TypeScript analysis including:

```text
Data flow
Taint tracking
Control flow
Call graphs
Security queries
```

A useful conceptual query is:

```text
SOURCE
location.search
      |
      v
TAINT FLOW
      |
      v
SINK
innerHTML
```

or:

```text
SOURCE
event.data
      |
      v
TAINT FLOW
      |
      v
SINK
eval()
```

CodeQL is especially useful when source and sink are separated across multiple functions or modules.

---

# ESLint

Run where appropriate:

```bash
npx eslint .
```

Security-relevant lint rules may identify dangerous patterns, but lint results are not vulnerability proof.

---

# Retire.js

Retire.js can identify known vulnerable client-side JavaScript libraries.

Example:

```bash
retire
```

or:

```bash
retire --path .
```

Verify current tool syntax before integrating it into automation.

Dependency findings still require contextual validation.

---

# Burp Suite Workflow

Client-side source review works well alongside Burp Suite.

A practical workflow is:

```text
Browser
   |
   v
Burp Proxy
   |
   v
Application
   |
   v
JavaScript Files
   |
   v
Source Review
   |
   v
Candidate Source-to-Sink Flow
   |
   v
Burp Repeater / Browser Validation
```

---

# Burp Target

Use:

```text
Target
  -> Site map
```

Identify:

```text
.js
.map
.json
GraphQL
WebSocket
API
```

---

# Burp Search

Useful search terms include:

```text
innerHTML
outerHTML
postMessage
location.href
location.hash
document.write
eval(
localStorage
sessionStorage
/api/
graphql
wss://
token
secret
```

---

# Burp DOM Invader

Burp's DOM Invader can assist with browser-side testing of DOM-based vulnerabilities.

It is especially useful for investigating:

```text
DOM XSS
postMessage
DOM clobbering
Prototype pollution
Client-side sources and sinks
```

Use DOM Invader as a testing aid rather than treating every reported source/sink as a confirmed vulnerability.

---

# Burp JavaScript Analysis

Burp's JavaScript analysis and site map can help identify:

```text
Endpoints
Parameters
Secrets
WebSockets
API calls
Client-side routes
```

Correlate dynamic observations with source review.

---

# Browser DevTools Workflow

DevTools is extremely useful for client-side source review.

Use:

```text
Sources
Network
Application
Console
Debugger
DOM Inspector
```

---

# Sources Panel

Use the Sources panel to:

```text
Pretty-print JavaScript
Set breakpoints
Inspect call stacks
Trace variables
Inspect event handlers
Review loaded scripts
```

---

# Breakpoint at Sink

For a candidate:

```javascript
element.innerHTML =
    value;
```

set a breakpoint and inspect:

```text
value
Call stack
Originating event
URL
Storage
API response
```

This can help confirm source-to-sink relationships.

---

# Event Listener Breakpoints

Browser DevTools can pause on:

```text
Mouse events
Keyboard events
Message events
DOM mutations
XHR/fetch
```

This can be valuable when tracing complex applications.

---

# Network Panel

Use the Network panel to map:

```text
REST APIs
GraphQL
WebSockets
JavaScript
Source maps
Third-party scripts
OAuth redirects
```

---

# Application Panel

Review:

```text
Cookies
localStorage
sessionStorage
IndexedDB
Service Workers
Cache Storage
```

Correlate stored values with source-code usage.

---

# Variant Analysis

Once a vulnerability is confirmed, search for other occurrences of the same pattern.

---

# DOM XSS Variants

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|dangerouslySetInnerHTML|v-html|\{@html' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx,vue,svelte}' \
.
```

---

# postMessage Variants

```bash
rg -n \
'addEventListener\(["'\'']message|onmessage\s*=' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

Review every receiver.

---

# Redirect Variants

```bash
rg -n \
'location\.href\s*=|location\.assign\(|location\.replace\(|window\.open\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Prototype Pollution Variants

```bash
rg -n \
'Object\.assign\(|merge\(|mergeWith\(|defaultsDeep\(|set\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Dynamic Code Variants

```bash
rg -n \
'\beval\(|new Function\(|setTimeout\(|setInterval\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Dynamic Script Variants

```bash
rg -n \
'createElement\(["'\'']script["'\'']\)|script\.src|import\(' \
--glob '*.{js,mjs,cjs,jsx,ts,tsx}' \
.
```

---

# Compare Similar Components

Example:

```text
SearchResults
    -> textContent

ProfileBiography
    -> DOMPurify + innerHTML

AdminAnnouncement
    -> innerHTML directly
```

The inconsistent output handling is a strong review signal.

---

# Compare Input Channels

The same dangerous sink may receive data from:

```text
URL
postMessage
API
localStorage
WebSocket
```

Example:

```text
             +-- location.search
             |
             +-- API response
             |
innerHTML <--+-- postMessage
             |
             +-- localStorage
```

Search every route into the sink.

---

# Client-Side Review Matrix

| Vulnerability | High-Value Sources / Sinks |
|---|---|
| DOM XSS | URL sources -> HTML sinks |
| Stored DOM XSS | API response -> HTML sinks |
| HTML Injection | attacker input -> HTML parser |
| Open Redirect | URL input -> location |
| postMessage | `event.data`, `event.origin` |
| Prototype Pollution | object merge/set operations |
| DOM Clobbering | named elements -> JS properties |
| Dynamic Code | `eval`, `Function` |
| Dynamic Script Loading | attacker input -> `script.src` |
| OAuth/OIDC | callbacks, state, nonce, PKCE |
| Client Auth | tokens, UI restrictions |
| Secrets | bundles, source maps |
| WebSockets | messages, endpoints |
| GraphQL | operations, endpoints |
| Third-Party JS | external script trust |
| CSP | script policy, Trusted Types |
| Storage | localStorage, sessionStorage |
| Service Workers | fetch/cache logic |
| XS-Leaks | cross-origin browser behaviour |

---

# Review Checklist

## Discovery

```text
[ ] JavaScript files identified
[ ] TypeScript files identified
[ ] Framework identified
[ ] Bundler identified
[ ] Source maps identified
[ ] Third-party scripts identified
[ ] Client-side routes mapped
[ ] API endpoints mapped
[ ] WebSocket endpoints mapped
[ ] GraphQL operations mapped
```

## Sources

```text
[ ] location.href reviewed
[ ] location.search reviewed
[ ] location.hash reviewed
[ ] location.pathname reviewed
[ ] document.URL reviewed
[ ] document.referrer reviewed
[ ] window.name reviewed
[ ] postMessage reviewed
[ ] localStorage reviewed
[ ] sessionStorage reviewed
[ ] IndexedDB reviewed
[ ] API responses reviewed
[ ] WebSocket messages reviewed
```

## DOM Sinks

```text
[ ] innerHTML reviewed
[ ] outerHTML reviewed
[ ] insertAdjacentHTML reviewed
[ ] document.write reviewed
[ ] document.writeln reviewed
[ ] srcdoc reviewed
[ ] DOMParser reviewed
[ ] createContextualFragment reviewed
```

## JavaScript Execution

```text
[ ] eval reviewed
[ ] Function reviewed
[ ] new Function reviewed
[ ] string setTimeout reviewed
[ ] string setInterval reviewed
[ ] dynamic imports reviewed
```

## URL Handling

```text
[ ] location.href reviewed
[ ] location.assign reviewed
[ ] location.replace reviewed
[ ] window.open reviewed
[ ] script.src reviewed
[ ] iframe.src reviewed
[ ] href assignments reviewed
[ ] URL validation reviewed
```

## postMessage

```text
[ ] Message senders identified
[ ] Message receivers identified
[ ] event.origin checks reviewed
[ ] event.source checks reviewed
[ ] event.data sinks reviewed
[ ] Wildcard target origins reviewed
```

## Frameworks

```text
[ ] React dangerouslySetInnerHTML reviewed
[ ] Angular DomSanitizer bypasses reviewed
[ ] Vue v-html reviewed
[ ] Svelte {@html} reviewed
[ ] jQuery HTML sinks reviewed
```

## Sanitisation

```text
[ ] DOMPurify reviewed
[ ] Custom sanitisation reviewed
[ ] Sanitiser configuration reviewed
[ ] Post-sanitisation transformations reviewed
[ ] Trusted Types reviewed
```

## Prototype Pollution

```text
[ ] Object.assign reviewed
[ ] Deep merge functions reviewed
[ ] Dynamic property assignment reviewed
[ ] Recursive setters reviewed
[ ] Prototype pollution gadgets reviewed
```

## DOM Clobbering

```text
[ ] Implicit globals reviewed
[ ] Named DOM elements reviewed
[ ] Window property assumptions reviewed
[ ] Clobbering gadgets reviewed
```

## Authentication and Authorisation

```text
[ ] Client authentication state reviewed
[ ] Client authorisation logic reviewed
[ ] Hidden functionality identified
[ ] Admin endpoints identified
[ ] JWT handling reviewed
[ ] Token storage reviewed
[ ] OAuth/OIDC reviewed
```

## Browser Storage

```text
[ ] localStorage reviewed
[ ] sessionStorage reviewed
[ ] IndexedDB reviewed
[ ] Sensitive data identified
[ ] Logout cleanup reviewed
[ ] Tenant/account switching reviewed
```

## APIs

```text
[ ] fetch calls reviewed
[ ] Axios calls reviewed
[ ] XMLHttpRequest reviewed
[ ] GraphQL reviewed
[ ] WebSockets reviewed
[ ] gRPC-Web reviewed
[ ] Server-Sent Events reviewed
```

## Browser Features

```text
[ ] Service Workers reviewed
[ ] Cache Storage reviewed
[ ] Web Workers reviewed
[ ] WebAssembly reviewed
[ ] File APIs reviewed
```

## Secrets

```text
[ ] Hard-coded credentials searched
[ ] API keys reviewed
[ ] Tokens reviewed
[ ] Source maps reviewed
[ ] Environment variables reviewed
[ ] Internal endpoints reviewed
```

## Security Controls

```text
[ ] CSP reviewed
[ ] Trusted Types reviewed
[ ] SRI reviewed
[ ] Third-party JavaScript reviewed
[ ] CORS assumptions reviewed
[ ] CSRF token handling reviewed
```

## Static Analysis

```text
[ ] ripgrep searches performed
[ ] Semgrep considered
[ ] CodeQL considered
[ ] ESLint considered
[ ] Retire.js considered
[ ] Findings manually validated
[ ] Variant analysis performed
```

---

# Finding Validation Model

Before reporting:

```text
STATIC MATCH
     |
     v
ATTACKER-CONTROLLED SOURCE?
     |
     +-- No --> Usually informational
     |
     v
REACHABLE DATA FLOW?
     |
     +-- No --> Discard / investigate
     |
     v
DANGEROUS SINK?
     |
     +-- No --> Contextual review
     |
     v
SANITISATION / VALIDATION?
     |
     +-- Effective --> Protected
     |
     v
BROWSER / FRAMEWORK PROTECTION?
     |
     +-- Effective --> Protected
     |
     v
EXPLOITABLE?
     |
     +-- No --> Defence-in-depth / contextual
     |
     v
SECURITY IMPACT?
     |
     v
CONFIRMED FINDING
```

---

# Example Finding - DOM XSS

```text
Title:
DOM-Based Cross-Site Scripting Through URL Parameter

Source:
location.search

Parameter:
name

Data Flow:

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

Security Control:
No effective HTML sanitisation or safe text sink was identified.

Impact:
An attacker able to influence the URL may be able to cause attacker-controlled content to be interpreted as HTML in the victim's browser.

Recommendation:
Use textContent when HTML rendering is unnecessary. If limited HTML is required, apply a well-maintained allowlist-based HTML sanitiser before insertion into an HTML parsing sink.
```

---

# Example Finding - postMessage Origin Validation

```text
Title:
Cross-Origin Message Handler Does Not Validate Message Origin

Source:
window message event

Data Flow:

External Window
      |
      v
postMessage()
      |
      v
event.data
      |
      v
Sensitive Browser Action

Security Control:
The message handler does not verify event.origin before trusting the message.

Recommendation:
Validate event.origin using an exact allowlist of expected origins and validate event.source where the communication flow expects a specific window.
```

---

# Example Finding - Client-Side Open Redirect

```text
Title:
Client-Side Open Redirect Through next Parameter

Source:
location.search

Data Flow:

location.search
      |
      v
next
      |
      v
location.href

Security Control:
No effective destination restriction was identified.

Impact:
An attacker may be able to construct a trusted application URL that redirects victims to an external destination.

Recommendation:
Use server-controlled redirect identifiers or validate the parsed destination against an explicit allowlist of permitted origins or paths.
```

---

# Example Finding - Dynamic Script Loading

```text
Title:
Attacker-Controlled URL Used for Dynamic Script Loading

Source:
location.search

Data Flow:

location.search
      |
      v
scriptUrl
      |
      v
script.src
      |
      v
document.head.appendChild()
      |
      v
Browser Script Execution

Security Control:
No effective restriction was identified on the script origin.

Impact:
If an attacker can control the script URL, arbitrary JavaScript may execute in the application's origin.

Recommendation:
Do not construct script locations from attacker-controlled input. Use server-controlled script identifiers mapped to explicitly trusted resources.
```

---

# Example Finding - Stored DOM XSS

```text
Title:
Stored DOM-Based Cross-Site Scripting in Profile Biography

Source:
API response containing stored biography

Data Flow:

Stored Biography
      |
      v
GET /api/profile
      |
      v
response.json()
      |
      v
data.biography
      |
      v
innerHTML

Security Control:
The stored value is inserted into an HTML parsing sink without effective sanitisation.

Recommendation:
Use textContent for plain-text biographies. If HTML is a required feature, sanitise the content using a well-maintained allowlist-based HTML sanitiser.
```

---

# Example Finding - Client-Side Authorisation Is Not Server Enforcement

```text
Title:
Administrative Functionality Identified Through Client-Side Role Check

Observation:

if (user.role === "admin") {
    showAdminPanel();
}

The JavaScript bundle references:

POST /api/admin/users/create

Security Assessment:
The client-side role check controls interface visibility but does not establish whether the API itself enforces authorisation.

Required Validation:
Test the server-side endpoint using an authenticated non-administrative account within the authorised test environment.

Reporting:
Do not report broken access control unless the server-side operation can actually be performed without the required permission.
```

---

# Example Finding - Prototype Pollution Candidate

```text
Title:
Potential Prototype Pollution Through Recursive Object Merge

Source:
URL query parameters

Data Flow:

location.search
      |
      v
Query Parser
      |
      v
Recursive Merge
      |
      v
Application Configuration

Review:
Determine whether special property names can modify object prototypes.

Impact Validation:
Identify whether polluted properties influence a security-sensitive gadget.

Reporting:
Do not report a confirmed prototype pollution vulnerability solely from the presence of a recursive merge function.
```

---

# Common Review Mistakes

## Every innerHTML Is XSS

Incorrect.

Determine:

```text
Data source
Attacker control
Sanitisation
Framework behaviour
HTML context
Reachability
```

---

# Every location.href Assignment Is Open Redirect

Incorrect.

Determine whether the attacker controls the destination and whether external navigation is permitted.

---

# Every postMessage Handler Is Vulnerable

Incorrect.

Review:

```text
event.origin
event.source
event.data
Sink
Impact
```

---

# Every postMessage("*") Is a Vulnerability

Incorrect.

Determine whether sensitive information can reach an unintended recipient.

---

# Every localStorage Value Is a Vulnerability

Incorrect.

Determine:

```text
What is stored?
Who can influence it?
Where is it used?
What is the threat model?
```

---

# JWT in localStorage Automatically Means Vulnerability

Incorrect.

It can increase exposure to successful XSS, but the overall security assessment depends on architecture, token lifetime, refresh-token handling and other controls.

---

# Every API Key in JavaScript Is a Secret

Incorrect.

Some browser-side API identifiers are intentionally public.

Determine privileges and intended exposure.

---

# Every Source Map Is a Vulnerability

Incorrect.

Assess whether the map exposes security-sensitive information that materially changes the attack surface.

---

# Every Object.assign Is Prototype Pollution

Incorrect.

Trace attacker-controlled keys and actual prototype mutation behaviour.

---

# Every React JSX Value Is XSS

Incorrect.

React normally escapes values rendered through JSX expressions.

Review explicit raw HTML mechanisms such as:

```text
dangerouslySetInnerHTML
```

---

# Every Angular innerHTML Is XSS

Incorrect.

Angular applies framework sanitisation in relevant contexts.

Review bypass APIs and actual data flow.

---

# Every Vue Interpolation Is XSS

Incorrect.

Normal Vue interpolation is escaped.

Review:

```text
v-html
```

and other raw HTML paths.

---

# Every Svelte Variable Is XSS

Incorrect.

Review explicit raw HTML:

```text
{@html ...}
```

---

# CSP Means XSS Is Impossible

Incorrect.

CSP is defence in depth.

Safe source-to-sink handling remains necessary.

---

# DOMPurify Means XSS Is Impossible

Incorrect.

Review:

```text
Version
Configuration
Hooks
Post-sanitisation mutation
Destination context
```

---

# Client-Side Validation Means Input Is Safe

Incorrect.

The browser is controlled by the user.

Server-side validation remains necessary.

---

# Hidden Button Means Protected Function

Incorrect.

UI visibility is not server-side authorisation.

---

# Final Client-Side JavaScript Review Model

```text
                     CLIENT-SIDE JAVASCRIPT
                              |
                              v
                            SOURCE
                              |
        +---------------------+----------------------+
        |                     |                      |
        v                     v                      v
      URL                postMessage              Storage
        |                     |                      |
        |                     |                      |
        +----------+----------+----------+-----------+
                   |                     |
                   v                     v
               API Data             DOM Data
                   |                     |
                   +----------+----------+
                              |
                              v
                       TRANSFORMATIONS
                              |
            +-----------------+------------------+
            |                 |                  |
            v                 v                  v
         Parsing          Validation         Sanitisation
            |                 |                  |
            +-----------------+------------------+
                              |
                              v
                             SINK
                              |
      +-------------+---------+---------+--------------+
      |             |                   |              |
      v             v                   v              v
     HTML         JavaScript          Navigation      Script
      |             |                   |              |
      v             v                   v              v
 innerHTML        eval()          location.href     script.src
      |             |                   |              |
      +-------------+---------+---------+--------------+
                              |
                              v
                        SECURITY IMPACT
```

A second useful model is:

```text
URL / Storage / Message / API
             |
             v
        JavaScript
             |
     +-------+-------+
     |               |
     v               v
Sanitisation     No Sanitisation
     |               |
     v               v
   Sink            Sink
     |               |
     v               v
Browser Behaviour / Framework Protection
             |
             v
       Exploitability
             |
             v
           Impact
```

The core question remains:

```text
Can attacker-controlled browser data reach a security-sensitive
sink without an effective protection?
```

Evaluate:

```text
Source
+
Transformations
+
Framework behaviour
+
Sanitisation
+
Sink
+
Browser behaviour
+
Reachability
+
Exploitability
+
Impact
```

Only then classify the candidate as a confirmed vulnerability.

---

# References

## MDN Web Security

[MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security){ target="_blank" rel="noopener noreferrer" }

## MDN Cross-Site Scripting

[MDN Cross-Site Scripting](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS){ target="_blank" rel="noopener noreferrer" }

## MDN innerHTML

[MDN innerHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML){ target="_blank" rel="noopener noreferrer" }

## MDN insertAdjacentHTML

[MDN insertAdjacentHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML){ target="_blank" rel="noopener noreferrer" }

## MDN postMessage

[MDN postMessage](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage){ target="_blank" rel="noopener noreferrer" }

## MDN Web Storage

[MDN Web Storage](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API){ target="_blank" rel="noopener noreferrer" }

## MDN Content Security Policy

[MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP){ target="_blank" rel="noopener noreferrer" }

## MDN Subresource Integrity

[MDN Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Subresource_Integrity){ target="_blank" rel="noopener noreferrer" }

## MDN Trusted Types

[MDN Trusted Types](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API){ target="_blank" rel="noopener noreferrer" }

## MDN Service Worker API

[MDN Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API){ target="_blank" rel="noopener noreferrer" }

## MDN Web Workers

[MDN Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API){ target="_blank" rel="noopener noreferrer" }

## MDN Web Crypto API

[MDN Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API){ target="_blank" rel="noopener noreferrer" }

## OWASP DOM Based XSS Prevention Cheat Sheet

[OWASP DOM Based XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Cross Site Scripting Prevention Cheat Sheet

[OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Third Party JavaScript Management Cheat Sheet

[OWASP Third Party JavaScript Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP HTML5 Security Cheat Sheet

[OWASP HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Content Security Policy Cheat Sheet

[OWASP Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP ASVS

[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/){ target="_blank" rel="noopener noreferrer" }

## PortSwigger DOM-Based Vulnerabilities

[PortSwigger DOM-Based Vulnerabilities](https://portswigger.net/web-security/dom-based){ target="_blank" rel="noopener noreferrer" }

## PortSwigger DOM XSS

[PortSwigger DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based){ target="_blank" rel="noopener noreferrer" }

## PortSwigger DOM Invader

[PortSwigger DOM Invader](https://portswigger.net/burp/documentation/desktop/tools/dom-invader){ target="_blank" rel="noopener noreferrer" }

## DOMPurify

[DOMPurify](https://github.com/cure53/DOMPurify){ target="_blank" rel="noopener noreferrer" }

## React dangerouslySetInnerHTML

[React dangerouslySetInnerHTML](https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html){ target="_blank" rel="noopener noreferrer" }

## Angular Security

[Angular Security](https://angular.dev/best-practices/security){ target="_blank" rel="noopener noreferrer" }

## Vue Security

[Vue Security](https://vuejs.org/guide/best-practices/security.html){ target="_blank" rel="noopener noreferrer" }

## Svelte HTML

[Svelte HTML](https://svelte.dev/docs/svelte/@html){ target="_blank" rel="noopener noreferrer" }

## Semgrep

[Semgrep](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

## CodeQL for JavaScript and TypeScript

[CodeQL for JavaScript and TypeScript](https://codeql.github.com/docs/codeql-language-guides/codeql-for-javascript/){ target="_blank" rel="noopener noreferrer" }

## CodeQL JavaScript Data Flow

[CodeQL JavaScript Data Flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/){ target="_blank" rel="noopener noreferrer" }

## Retire.js

[Retire.js](https://github.com/RetireJS/retire.js){ target="_blank" rel="noopener noreferrer" }

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/dotnet.md
docs/source-code-review/java.md
docs/source-code-review/php.md
docs/source-code-review/python.md
docs/source-code-review/django.md
docs/source-code-review/flask.md
docs/source-code-review/nodejs.md
```

---

# Related Web Security Notes

```text
docs/web/attack-surface-analysis.md
docs/web/input-validation.md

docs/web/authentication.md
docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/mfa.md

docs/web/xss.md
docs/web/dom-based-vulnerabilities.md
docs/web/html-injection.md
docs/web/csrf.md
docs/web/cors.md
docs/web/clickjacking.md
docs/web/open-redirect.md
docs/web/xs-leaks.md

docs/web/prototype-pollution.md

docs/web/jwt.md
docs/web/oauth-oidc.md

docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md

docs/web/http-security-headers.md
docs/web/information-disclosure.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md
```
