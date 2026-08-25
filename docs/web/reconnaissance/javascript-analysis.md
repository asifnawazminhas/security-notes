# JavaScript Analysis

JavaScript analysis is an important part of modern web application reconnaissance.

Client-side JavaScript frequently contains information about application functionality that may not be immediately visible through normal browsing. Reviewing JavaScript files can reveal API endpoints, parameters, hidden routes, authentication flows, third-party services, application architecture and functionality that should be investigated further.

This page provides a practical methodology for analysing JavaScript during authorised web application security assessments.

!!! warning "Authorised Security Testing"
    Perform these techniques only against systems for which you have explicit authorisation. JavaScript analysis should remain within the agreed scope of the assessment.

---

## Objectives

JavaScript analysis can help identify:

- API endpoints
- Hidden application routes
- Administrative functionality
- Internal paths
- API versions
- Request parameters
- GraphQL endpoints
- WebSocket endpoints
- Authentication functionality
- Authorisation logic
- File upload functionality
- Debug functionality
- Development endpoints
- Feature flags
- Third-party integrations
- Cloud storage references
- Source maps
- Interesting comments
- Hardcoded configuration
- Accidentally exposed secrets
- Client-side security controls
- Potential vulnerability sinks

The objective is not simply to download JavaScript files.

The objective is to turn JavaScript into an **attack surface map**.

---

# JavaScript Analysis Workflow

A practical workflow can be represented as:

```text
Target
  ↓
Crawl Application
  ↓
Collect JavaScript Files
  ↓
Normalise and Deduplicate URLs
  ↓
Download JavaScript
  ↓
Search for Endpoints
  ↓
Search for Parameters
  ↓
Search for Interesting Keywords
  ↓
Search for Secrets
  ↓
Inspect Source Maps
  ↓
Identify Sources and Sinks
  ↓
Map Application Functionality
  ↓
Validate Findings
```

Each stage should feed information into the next stage.

---

# 1. Collect JavaScript Files

Start by collecting JavaScript files referenced by the application.

There are several useful sources.

## Browser Developer Tools

Open the application in a browser and use:

```text
Developer Tools
→ Network
→ JS
```

Reload the application.

This shows JavaScript resources loaded by the current page.

Also inspect:

```text
Developer Tools
→ Sources
```

This is particularly useful for modern single-page applications.

---

# 2. Inspect the HTML

JavaScript files may be referenced directly in HTML.

Example:

```html
<script src="/assets/app.js"></script>
<script src="/static/main.js"></script>
<script src="/js/application.js"></script>
```

Search downloaded HTML:

```bash
grep -Eo 'src="[^"]+\.js[^"]*"' index.html
```

Another simple approach:

```bash
grep -oE 'https?://[^"]+\.js' index.html
```

---

# 3. Crawl for JavaScript

Crawlers are usually more effective than inspecting pages manually.

Useful tools include:

- Katana
- gau
- waybackurls
- urlfinder
- hakrawler

---

## Katana

Basic crawl:

```bash
katana -u https://example.com
```

Save results:

```bash
katana -u https://example.com -o katana.txt
```

Extract JavaScript:

```bash
grep -Ei '\.js($|\?)' katana.txt > javascript.txt
```

Sort and deduplicate:

```bash
sort -u javascript.txt -o javascript.txt
```

---

## Katana JavaScript Crawling

Katana can perform deeper JavaScript analysis.

```bash
katana -u https://example.com -jc
```

Useful combination:

```bash
katana \
  -u https://example.com \
  -jc \
  -kf all \
  -d 5 \
  -o katana.txt
```

Then extract JavaScript:

```bash
grep -Ei '\.js($|\?)' katana.txt | sort -u > javascript.txt
```

---

# 4. Historical JavaScript Files

Historical URLs can reveal JavaScript files that are no longer directly linked.

This can be useful because older application versions sometimes expose functionality or endpoints that remain accessible.

---

## gau

```bash
gau example.com
```

Extract JavaScript:

```bash
gau example.com |
grep -Ei '\.js($|\?)' |
sort -u > gau-javascript.txt
```

---

## waybackurls

```bash
echo example.com | waybackurls
```

Extract JavaScript:

```bash
echo example.com |
waybackurls |
grep -Ei '\.js($|\?)' |
sort -u > wayback-javascript.txt
```

---

# 5. Combine JavaScript Sources

Combine results from multiple tools.

```bash
cat \
javascript.txt \
gau-javascript.txt \
wayback-javascript.txt \
2>/dev/null |
sort -u > all-javascript.txt
```

Count discovered JavaScript URLs:

```bash
wc -l all-javascript.txt
```

---

# 6. Verify JavaScript Files

Historical sources often contain dead URLs.

Verify which resources still respond.

Using `httpx`:

```bash
cat all-javascript.txt |
httpx -silent > live-javascript.txt
```

Include status codes:

```bash
cat all-javascript.txt |
httpx -silent -status-code
```

Filter successful responses:

```bash
cat all-javascript.txt |
httpx -silent -mc 200 > live-javascript.txt
```

---

# 7. Download JavaScript

JavaScript can then be downloaded for local analysis.

Create a directory:

```bash
mkdir -p javascript
```

Simple loop:

```bash
while read -r url; do
    wget -q "$url" -P javascript/
done < live-javascript.txt
```

Be aware that different URLs can contain identical filenames.

For larger assessments, preserve the URL-to-file mapping rather than relying only on the basename.

---

# 8. Beautify Minified JavaScript

Production JavaScript is frequently minified.

Example:

```javascript
function a(b){return fetch("/api/user?id="+b).then(c=>c.json())}
```

Beautification makes analysis significantly easier.

One option is `js-beautify`.

Install:

```bash
npm install -g js-beautify
```

Beautify:

```bash
js-beautify app.js > app-beautified.js
```

Process multiple files:

```bash
find javascript -type f -name "*.js" -exec js-beautify {} -o {}.beautified \;
```

---

# 9. Search for API Endpoints

One of the highest-value activities is identifying endpoints.

Search for common API strings:

```bash
grep -RniE '/api/|/v1/|/v2/|/v3/' javascript/
```

Examples might reveal:

```text
/api/users
/api/profile
/api/admin
/api/upload
/api/export
/api/download
/api/search
/api/auth/login
/api/auth/reset
/api/internal/status
```

Create an endpoint candidate file:

```bash
grep -RhoE '["'\''][/][A-Za-z0-9_?&=./:%-]+["'\'']' javascript/ |
tr -d "\"'" |
sort -u > endpoint-candidates.txt
```

Manual validation is still necessary because JavaScript contains many strings that are not endpoints.

---

# 10. Search for Interesting Paths

Search for functionality commonly worth investigating.

```bash
grep -RniE \
'admin|internal|debug|upload|download|export|import|backup|restore|config|settings|profile|account|user|reset|password|token' \
javascript/
```

Interesting examples include:

```text
/admin
/internal
/debug
/api/admin
/api/internal
/upload
/download
/export
/import
/backup
/config
/settings
```

---

# 11. Search for Parameters

JavaScript can reveal parameters that are difficult to discover through crawling alone.

Search for common parameter patterns:

```bash
grep -RniE \
'id|user|username|email|account|role|admin|file|filename|path|url|uri|redirect|callback|return|next|target|host|domain|query|search' \
javascript/
```

Examples:

```text
userId
accountId
documentId
redirectUrl
callbackUrl
downloadUrl
filePath
returnUrl
target
```

These can then be added to the parameter discovery workflow.

---

# 12. Search for HTTP Requests

JavaScript reveals how the frontend communicates with the backend.

Search for:

```bash
grep -RniE \
'fetch\(|axios|XMLHttpRequest|\.ajax\(|\$\.get|\$\.post' \
javascript/
```

Examples:

```javascript
fetch("/api/profile")
```

```javascript
axios.post("/api/login", data)
```

```javascript
$.ajax({
    url: "/api/admin/users"
})
```

These are particularly useful because they often reveal:

- endpoint
- HTTP method
- request body
- headers
- expected response
- authentication mechanism

---

# 13. Search for HTTP Methods

Search for explicit request methods:

```bash
grep -RniE \
'GET|POST|PUT|PATCH|DELETE|OPTIONS' \
javascript/
```

A JavaScript call such as:

```javascript
fetch("/api/users/" + id, {
    method: "DELETE"
})
```

reveals both an endpoint and an operation.

---

# 14. Authentication Analysis

Search for authentication-related functionality.

```bash
grep -RniE \
'login|logout|signin|signout|authenticate|authentication|authorization|password|reset|forgot|mfa|2fa|otp|token|jwt|bearer|session' \
javascript/
```

Look for:

```text
/login
/logout
/register
/reset-password
/forgot-password
/mfa
/verify
/token
/refresh
```

Also inspect how tokens are stored.

Search:

```bash
grep -RniE \
'localStorage|sessionStorage|document\.cookie|setItem|getItem' \
javascript/
```

Examples:

```javascript
localStorage.setItem("token", token)
```

or:

```javascript
sessionStorage.getItem("access_token")
```

These observations help map the application's authentication architecture.

---

# 15. JWT Usage

Search for JWT-related strings:

```bash
grep -RniE \
'jwt|access_token|refresh_token|bearer|authorization' \
javascript/
```

Look for code such as:

```javascript
Authorization: `Bearer ${token}`
```

or:

```javascript
localStorage.getItem("access_token")
```

Document:

```text
Token acquisition
      ↓
Token storage
      ↓
Token transmission
      ↓
Token refresh
      ↓
Token invalidation
```

---

# 16. Client-Side Authorisation

JavaScript sometimes contains client-side checks controlling which functionality is displayed.

Search for:

```bash
grep -RniE \
'role|permission|isAdmin|admin|authoriz|privilege|access' \
javascript/
```

Examples:

```javascript
if (user.role === "admin") {
    showAdminPanel();
}
```

or:

```javascript
if (permissions.includes("DELETE_USER")) {
    enableDeleteButton();
}
```

!!! note
    Client-side checks are not necessarily vulnerabilities. The important question is whether equivalent authorisation is enforced by the server.

Such findings identify functionality that should be tested directly against the backend.

---

# 17. Search for Administrative Functionality

```bash
grep -RniE \
'admin|administrator|superuser|manage|management|dashboard|console' \
javascript/
```

Potential discoveries:

```text
/admin
/admin/users
/admin/settings
/management
/internal/admin
/api/admin
```

Do not assume an endpoint is protected simply because the normal interface hides it.

---

# 18. File Upload Functionality

Search for:

```bash
grep -RniE \
'upload|multipart|FormData|filename|fileName|content-type' \
javascript/
```

Example:

```javascript
const data = new FormData();
data.append("file", selectedFile);

fetch("/api/upload", {
    method: "POST",
    body: data
});
```

This reveals:

```text
Endpoint
HTTP method
Parameter name
Request format
```

which can then be investigated through the file upload testing methodology.

---

# 19. File Download Functionality

Search:

```bash
grep -RniE \
'download|filename|filepath|filePath|attachment|blob' \
javascript/
```

Example:

```javascript
fetch("/api/download?file=" + filename)
```

This may identify functionality worth testing for:

- path traversal
- insecure direct object references
- access control issues
- arbitrary file retrieval

---

# 20. URL Processing

Search for functionality accepting URLs.

```bash
grep -RniE \
'url|uri|callback|webhook|redirect|returnUrl|next|target|endpoint|host' \
javascript/
```

Interesting examples:

```text
callbackUrl
redirectUrl
webhookUrl
imageUrl
avatarUrl
feedUrl
targetUrl
```

These can indicate functionality requiring further validation for issues such as:

- SSRF
- open redirects
- callback manipulation
- webhook abuse

---

# 21. GraphQL

Search for GraphQL references:

```bash
grep -RniE \
'graphql|query{|mutation{|apollo' \
javascript/
```

Possible endpoint:

```text
/graphql
```

or:

```text
/api/graphql
```

Look for operation names:

```javascript
query GetUser
mutation UpdateProfile
mutation DeleteAccount
```

These can reveal significant application functionality.

---

# 22. WebSockets

Search:

```bash
grep -RniE \
'WebSocket|wss://|ws://' \
javascript/
```

Example:

```javascript
new WebSocket("wss://example.com/socket")
```

WebSocket functionality may expose:

- chat
- notifications
- administrative events
- real-time application state
- internal APIs

---

# 23. Search for Source Maps

Source maps are particularly valuable during JavaScript analysis.

They commonly use:

```text
.js.map
```

Example:

```text
app.js
app.js.map
```

Test whether a corresponding source map exists:

```bash
curl -I https://example.com/assets/app.js.map
```

Search JavaScript files for:

```bash
grep -Rni 'sourceMappingURL' javascript/
```

Example:

```javascript
//# sourceMappingURL=app.js.map
```

---

## Why Source Maps Matter

A minified bundle might look like:

```javascript
function a(b){return fetch("/api/u/"+b)}
```

A source map may reconstruct original files such as:

```text
src/
├── api/
│   ├── auth.js
│   ├── users.js
│   └── admin.js
├── components/
├── config/
└── routes/
```

This can significantly improve understanding of the application.

---

# 24. Search for Development Artifacts

Look for references to:

```bash
grep -RniE \
'localhost|127\.0\.0\.1|dev\.|development|staging|test\.|internal|debug' \
javascript/
```

Potential discoveries:

```text
http://localhost:3000
https://dev.example.com
https://staging.example.com
https://api-internal.example.com
```

These may reveal additional architecture or environments.

They are not automatically in scope. Validate the authorised scope before interacting with newly discovered hosts.

---

# 25. Search for Hardcoded Secrets

JavaScript is publicly accessible to users, so secrets should generally not be embedded in frontend bundles.

Nevertheless, accidental exposures occur.

Search for common patterns:

```bash
grep -RniE \
'api[_-]?key|secret|password|passwd|token|access[_-]?key|private[_-]?key|client[_-]?secret' \
javascript/
```

Potential findings:

```text
API_KEY
SECRET_KEY
ACCESS_TOKEN
CLIENT_SECRET
AWS_ACCESS_KEY_ID
```

However, keyword searches produce many false positives.

Every result should be validated manually.

---

# 26. Automated Secret Discovery

Tools such as TruffleHog and Gitleaks can assist with identifying secret-like values.

For downloaded JavaScript:

```bash
gitleaks detect --source javascript/
```

Results should be treated as candidates until validated.

Avoid unnecessary use of discovered credentials.

The security issue can often be demonstrated by confirming exposure and understanding the associated service without performing intrusive actions.

---

# 27. Cloud References

Search for cloud-related infrastructure.

```bash
grep -RniE \
'amazonaws\.com|s3\.|blob\.core\.windows\.net|storage\.googleapis\.com|firebaseio\.com' \
javascript/
```

Potential findings include:

```text
S3 buckets
Azure Blob Storage
Google Cloud Storage
Firebase
CDN endpoints
```

Again, discovery does not automatically mean those resources are authorised targets.

---

# 28. Third-Party Services

Search for references to external services.

Examples include:

```text
analytics
payment providers
authentication providers
CDNs
monitoring platforms
support platforms
error reporting
```

Useful searches:

```bash
grep -RniE \
'stripe|paypal|sentry|segment|firebase|auth0|okta|cloudflare|googleapis' \
javascript/
```

This helps map application dependencies.

---

# 29. Comments and Developer Notes

Comments can contain surprisingly useful information.

Search:

```bash
grep -RniE \
'TODO|FIXME|HACK|DEBUG|TEMP|REMOVE|DEPRECATED' \
javascript/
```

Examples:

```javascript
// TODO remove old admin endpoint
```

```javascript
// FIXME authentication bypass for testing
```

```javascript
// deprecated API
```

Comments should be interpreted in context rather than assumed to represent exploitable behaviour.

---

# 30. Identify Client-Side Sources

For vulnerability research, it is useful to understand where attacker-controlled data enters JavaScript.

Common sources include:

```text
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

Search:

```bash
grep -RniE \
'location\.href|location\.search|location\.hash|document\.URL|document\.documentURI|document\.referrer|window\.name|postMessage|localStorage|sessionStorage' \
javascript/
```

---

# 31. Identify Potential Client-Side Sinks

Potentially interesting sinks include:

```text
innerHTML
outerHTML
document.write
document.writeln
insertAdjacentHTML
eval
Function
setTimeout
setInterval
location
location.href
```

Search:

```bash
grep -RniE \
'innerHTML|outerHTML|document\.write|document\.writeln|insertAdjacentHTML|eval\(|Function\(|setTimeout\(|setInterval\(' \
javascript/
```

A sink alone is **not a vulnerability**.

The important question is whether attacker-controlled input can reach the sink without appropriate validation or encoding.

Conceptually:

```text
Source
  ↓
Transformations
  ↓
Validation / Encoding
  ↓
Sink
```

---

# 32. DOM XSS Investigation

For DOM-based XSS, identify flows such as:

```text
location.search
      ↓
application processing
      ↓
innerHTML
```

Example:

```javascript
const value = new URLSearchParams(location.search).get("name");

document.getElementById("result").innerHTML = value;
```

The relevant task is tracing data flow from the source to the sink.

---

# 33. Redirect Logic

Search:

```bash
grep -RniE \
'location\.href|location\.assign|location\.replace|window\.open|redirect|returnUrl|next' \
javascript/
```

Example:

```javascript
window.location.href = params.get("next");
```

This identifies redirect behaviour that may require further validation.

---

# 34. postMessage

Search:

```bash
grep -RniE \
'postMessage|addEventListener.*message|onmessage' \
javascript/
```

Review:

- origin validation
- message data handling
- dangerous sinks
- sensitive actions triggered by messages

Example:

```javascript
window.addEventListener("message", function(event) {
    ...
});
```

Pay particular attention to whether `event.origin` is validated appropriately.

---

# 35. Framework Identification

JavaScript can reveal the frontend framework.

Common indicators include:

```text
React
Angular
Vue
Next.js
Nuxt
Svelte
jQuery
Webpack
Vite
```

Search:

```bash
grep -RniE \
'react|angular|vue|next|nuxt|svelte|jquery|webpack|vite' \
javascript/
```

Framework identification can guide further testing.

---

# 36. Next.js

Next.js applications frequently expose:

```text
/_next/static/
```

Look for:

```text
/_next/static/chunks/
/_next/static/build/
/_next/data/
```

JavaScript bundles can contain:

- routes
- API paths
- build information
- feature names
- internal application structure

Inspect:

```text
/_next/static/
```

and JavaScript chunk references discovered through the application.

---

# 37. Angular

Angular applications commonly contain files such as:

```text
main.js
runtime.js
polyfills.js
vendor.js
```

Search bundles for:

```bash
grep -RniE \
'api|endpoint|environment|production|baseUrl|apiUrl' \
javascript/
```

Pay particular attention to configuration embedded in environment objects.

---

# 38. React

React applications may expose:

```text
static/js/main.*.js
static/js/*.chunk.js
```

Search for:

```text
API URLs
routes
feature names
environment variables
authentication logic
```

Common environment variable prefix:

```text
REACT_APP_
```

Search:

```bash
grep -Rni 'REACT_APP_' javascript/
```

---

# 39. Vue

Vue applications may contain configuration such as:

```text
VUE_APP_API_URL
VUE_APP_BASE_URL
```

Search:

```bash
grep -Rni 'VUE_APP_' javascript/
```

---

# 40. JavaScript Endpoint Extraction Tools

Manual analysis should be complemented by automated extraction.

Useful tools include:

```text
LinkFinder
JSFinder
SecretFinder
xnLinkFinder
Katana
```

Different tools use different extraction logic, so combining results can improve coverage.

---

# 41. LinkFinder

LinkFinder extracts endpoints from JavaScript.

Repository:

```text
https://github.com/GerbenJavado/LinkFinder
```

Example:

```bash
python3 linkfinder.py \
-i https://example.com/assets/app.js \
-o cli
```

Recursive or downloaded JavaScript analysis can help identify endpoints that basic crawling misses.

---

# 42. SecretFinder

SecretFinder searches JavaScript for secret-like information.

Repository:

```text
https://github.com/m4ll0k/SecretFinder
```

Example:

```bash
python3 SecretFinder.py \
-i https://example.com/assets/app.js \
-o cli
```

Treat results as candidates requiring manual validation.

---

# 43. xnLinkFinder

`xnLinkFinder` can discover endpoints and parameters from various input sources.

Example concept:

```bash
python3 xnLinkFinder.py \
-i https://example.com \
-o endpoints.txt
```

It can complement crawler-based discovery.

---

# 44. Burp Suite

Burp Suite is particularly useful for JavaScript analysis because it combines passive collection with manual testing.

Useful locations include:

```text
Proxy
Target
Site map
HTTP history
Search
```

As the application is browsed, JavaScript files appear in the site map.

Search the site map for:

```text
.js
```

Then inspect responses for:

```text
/api/
admin
token
password
upload
download
redirect
debug
internal
```

---

# 45. Burp Search

Useful search strings include:

```text
/api/
Authorization
Bearer
token
admin
password
secret
upload
download
redirect
callback
localhost
internal
debug
```

This is often faster than opening every JavaScript file manually.

---

# 46. Browser Pretty Print

Browser Developer Tools can beautify minified JavaScript.

Open:

```text
Developer Tools
→ Sources
→ JavaScript file
```

Then select the pretty-print `{}` option.

This can make minified bundles significantly easier to inspect.

---

# 47. Application Route Discovery

Single-page applications frequently define routes client-side.

Search:

```bash
grep -RniE \
'route|router|path:' \
javascript/
```

Potential discoveries:

```text
/dashboard
/profile
/settings
/admin
/admin/users
/reports
/internal
/debug
```

Routes hidden from normal navigation may still reveal useful functionality.

---

# 48. Feature Flags

Search:

```bash
grep -RniE \
'featureFlag|feature_flag|featureEnabled|enableFeature|experimental|beta' \
javascript/
```

Feature flags can reveal:

```text
unfinished functionality
beta endpoints
administrative functionality
disabled application features
```

The backend should still enforce appropriate access controls regardless of whether a frontend feature is enabled.

---

# 49. Environment Configuration

Search:

```bash
grep -RniE \
'production|development|staging|environment|baseURL|baseUrl|apiURL|apiUrl' \
javascript/
```

Example:

```javascript
const config = {
    apiUrl: "https://api.example.com",
    environment: "production"
};
```

This is useful for understanding application architecture.

---

# 50. Build an Endpoint Inventory

Do not leave discoveries scattered across terminal output.

Create an inventory.

Example:

| Endpoint | Method | Source | Parameters | Authentication | Notes |
|---|---|---|---|---|---|
| `/api/login` | POST | `auth.js` | username, password | No | Authentication |
| `/api/profile` | GET | `user.js` | id | Bearer | User profile |
| `/api/upload` | POST | `files.js` | file | Bearer | File upload |
| `/api/admin/users` | GET | `admin.js` | page | Bearer | Admin functionality |
| `/api/export` | POST | `reports.js` | format | Bearer | Export functionality |

This becomes extremely valuable during later testing.

---

# 51. Build a Parameter Inventory

Similarly, record parameters.

Example:

| Parameter | Endpoint | Source | Potential Testing |
|---|---|---|---|
| `id` | `/api/user` | `user.js` | Access control |
| `file` | `/api/download` | `files.js` | Path handling |
| `url` | `/api/import` | `import.js` | Server-side URL processing |
| `redirect` | `/login` | `auth.js` | Redirect handling |
| `query` | `/api/search` | `search.js` | Input validation |

This connects JavaScript analysis directly to later vulnerability testing.

---

# 52. Prioritisation

Not every JavaScript discovery deserves equal attention.

A practical prioritisation model is:

```text
Authentication
      ↓
Authorisation
      ↓
Administrative Functionality
      ↓
File Operations
      ↓
Server-Side URL Processing
      ↓
User-Controlled Input
      ↓
Internal / Debug Functionality
      ↓
Client-Side Sources and Sinks
      ↓
General Application Routes
```

High-value keywords include:

```text
admin
internal
debug
token
password
upload
download
import
export
callback
redirect
webhook
file
path
role
permission
```

---

# 53. Practical Recon Pipeline

A simple JavaScript reconnaissance pipeline might be:

```bash
katana \
-u https://example.com \
-jc \
-kf all \
-d 5 \
-o katana.txt
```

Extract JavaScript:

```bash
grep -Ei '\.js($|\?)' katana.txt |
sort -u > javascript.txt
```

Add historical sources:

```bash
gau example.com |
grep -Ei '\.js($|\?)' >> javascript.txt
```

```bash
echo example.com |
waybackurls |
grep -Ei '\.js($|\?)' >> javascript.txt
```

Deduplicate:

```bash
sort -u javascript.txt -o javascript.txt
```

Check live resources:

```bash
cat javascript.txt |
httpx -silent -mc 200 > live-javascript.txt
```

The result becomes the input for deeper JavaScript analysis.

---

# 54. Practical Keyword Search

After downloading JavaScript:

```bash
grep -RniE \
'api|admin|internal|debug|upload|download|export|import|token|password|secret|redirect|callback|webhook|graphql|socket|role|permission' \
javascript/
```

Then search client-side sources and sinks:

```bash
grep -RniE \
'location\.href|location\.search|location\.hash|document\.URL|document\.referrer|postMessage|innerHTML|outerHTML|document\.write|insertAdjacentHTML|eval\(' \
javascript/
```

This gives a useful first-pass view of the client-side attack surface.

---

# 55. What to Record

During JavaScript analysis, record at minimum:

```text
JavaScript URL
Application route
API endpoint
HTTP method
Parameters
Authentication requirement
Interesting functionality
Potential source
Potential sink
Source map availability
Interesting configuration
Third-party dependency
Potential secret
Validation status
```

Good documentation prevents rediscovery later.

---

# 56. Common Mistakes

## Only inspecting main.js

Modern applications often split functionality across many chunks.

Analyse all relevant bundles.

---

## Ignoring historical JavaScript

Old JavaScript can reveal forgotten endpoints and functionality.

Include historical URL sources where appropriate.

---

## Treating Every Secret Pattern as a Secret

Strings containing words such as:

```text
token
key
secret
```

are often harmless variable names.

Validate findings manually.

---

## Treating Every Sink as XSS

Finding:

```javascript
innerHTML
```

does not prove XSS.

You must establish whether attacker-controlled data can reach the sink unsafely.

---

## Ignoring Source Maps

Source maps can transform a difficult minified bundle into understandable source code.

Always check for them.

---

## Ignoring API Calls

API requests made by JavaScript often provide more value than the visible frontend itself.

Map them carefully.

---

# 57. Recommended Output Structure

Store reconnaissance results consistently.

For example:

```text
recon/
├── javascript/
│   ├── javascript.txt
│   ├── live-javascript.txt
│   ├── endpoint-candidates.txt
│   ├── parameters.txt
│   ├── interesting-strings.txt
│   ├── source-maps.txt
│   ├── secret-candidates.txt
│   └── downloaded/
```

This makes later analysis significantly easier.

---

# 58. JavaScript Analysis Checklist

## Collection

- [ ] Crawl application
- [ ] Collect JavaScript URLs
- [ ] Check historical sources
- [ ] Deduplicate URLs
- [ ] Verify live JavaScript files
- [ ] Download relevant bundles

## Analysis

- [ ] Beautify minified JavaScript
- [ ] Extract endpoints
- [ ] Extract parameters
- [ ] Identify HTTP methods
- [ ] Identify authentication logic
- [ ] Identify authorisation logic
- [ ] Search administrative functionality
- [ ] Search file operations
- [ ] Search URL-processing functionality
- [ ] Search GraphQL references
- [ ] Search WebSocket references
- [ ] Search source maps
- [ ] Search development references
- [ ] Search secret candidates
- [ ] Search cloud references
- [ ] Search third-party integrations
- [ ] Search developer comments
- [ ] Identify sources
- [ ] Identify sinks
- [ ] Identify client-side routes
- [ ] Identify feature flags

## Validation

- [ ] Validate endpoints
- [ ] Validate parameters
- [ ] Validate authentication requirements
- [ ] Validate authorisation server-side
- [ ] Validate source-to-sink flows
- [ ] Validate potential secrets
- [ ] Confirm newly discovered hosts are in scope

## Documentation

- [ ] Create endpoint inventory
- [ ] Create parameter inventory
- [ ] Record source maps
- [ ] Record interesting JavaScript files
- [ ] Record testing opportunities
- [ ] Feed discoveries into later testing

---

# 59. JavaScript Analysis Mindset

The most useful way to approach JavaScript analysis is not:

```text
Find JavaScript
      ↓
grep for secrets
      ↓
Done
```

Instead:

```text
Collect JavaScript
      ↓
Understand Application Structure
      ↓
Extract Routes
      ↓
Extract APIs
      ↓
Extract Parameters
      ↓
Understand Authentication
      ↓
Understand Authorisation
      ↓
Identify Interesting Functionality
      ↓
Trace User-Controlled Data
      ↓
Identify Testing Opportunities
      ↓
Validate Manually
```

JavaScript should be treated as a source of information about how the application works.

---

# 60. Relationship With Other Testing

JavaScript analysis should feed directly into other sections of the assessment.

```text
JavaScript Analysis
        │
        ├── API endpoints
        │       ↓
        │   API Security
        │
        ├── Parameters
        │       ↓
        │   Input Validation
        │
        ├── Authentication
        │       ↓
        │   Authentication Testing
        │
        ├── Roles / Permissions
        │       ↓
        │   Authorisation Testing
        │
        ├── Upload / Download
        │       ↓
        │   File Testing
        │
        ├── URL Parameters
        │       ↓
        │   SSRF / Redirect Testing
        │
        ├── Sources / Sinks
        │       ↓
        │   DOM XSS
        │
        └── GraphQL / WebSockets
                ↓
            Protocol-Specific Testing
```

This is why JavaScript analysis belongs early in the reconnaissance process.

---

# 61. Quick Reference

### Crawl JavaScript

```bash
katana -u https://example.com -jc -kf all -d 5
```

### Historical JavaScript

```bash
gau example.com |
grep -Ei '\.js($|\?)'
```

```bash
echo example.com |
waybackurls |
grep -Ei '\.js($|\?)'
```

### Live JavaScript

```bash
cat javascript.txt |
httpx -silent -mc 200
```

### API Search

```bash
grep -RniE '/api/|/v1/|/v2/|/v3/' javascript/
```

### Interesting Functionality

```bash
grep -RniE \
'admin|internal|debug|upload|download|export|import|token|password|redirect|callback|webhook' \
javascript/
```

### Authentication

```bash
grep -RniE \
'login|logout|password|token|jwt|bearer|session|mfa|2fa' \
javascript/
```

### Client-Side Storage

```bash
grep -RniE \
'localStorage|sessionStorage|document\.cookie' \
javascript/
```

### Sources

```bash
grep -RniE \
'location\.href|location\.search|location\.hash|document\.URL|document\.referrer|window\.name|postMessage' \
javascript/
```

### Sinks

```bash
grep -RniE \
'innerHTML|outerHTML|document\.write|insertAdjacentHTML|eval\(|Function\(' \
javascript/
```

### Source Maps

```bash
grep -Rni 'sourceMappingURL' javascript/
```

### Development Infrastructure

```bash
grep -RniE \
'localhost|127\.0\.0\.1|development|staging|internal|debug' \
javascript/
```

---

# References

Useful references and projects for further study:

- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [MDN Web Docs: JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [Katana](https://github.com/projectdiscovery/katana)
- [gau](https://github.com/lc/gau)
- [waybackurls](https://github.com/tomnomnom/waybackurls)
- [LinkFinder](https://github.com/GerbenJavado/LinkFinder)
- [SecretFinder](https://github.com/m4ll0k/SecretFinder)
- [xnLinkFinder](https://github.com/xnl-h4ck3r/xnLinkFinder)
- [Gitleaks](https://github.com/gitleaks/gitleaks)

---

## Related Notes

Continue with:

- [Web Application Security Overview](../index.md)
- [Web Application Testing Methodology](../methodology.md)
- [Pentesting Checklist](../checklist.md)
- [Reconnaissance Overview](index.md)
- [Subdomain Enumeration](subdomain-enumeration.md)
- [Technology Identification](technology-identification.md)
- [Content Discovery](content-discovery.md)
- [Parameter Discovery](parameter-discovery.md)
