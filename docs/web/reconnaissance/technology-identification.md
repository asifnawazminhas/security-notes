# Technology Identification

Technology identification is the process of determining the technologies, frameworks, libraries and infrastructure components used by a web application.

Accurate technology identification helps guide the rest of a web application security assessment. Knowing that an application uses technologies such as Next.js, Spring Boot, ASP.NET, WordPress or nginx can significantly influence which endpoints, configuration weaknesses and vulnerability classes should be investigated.

The objective is not simply to produce a list of technology names. The objective is to understand the application's **technology stack and architecture** well enough to make informed testing decisions.

!!! warning "Authorised Security Testing"

    Perform technology identification and subsequent security testing only against systems that are within the authorised scope of the assessment.

---

## Technology Identification Workflow

A practical workflow can be organised as:

```text
Live Web Target
      |
      v
HTTP Response
      |
      +---- Headers
      |
      +---- Cookies
      |
      +---- HTML
      |
      +---- Error Pages
      |
      +---- JavaScript
      |
      +---- Static Assets
      |
      v
Automated Fingerprinting
      |
      +---- WhatWeb
      |
      +---- Wappalyzer
      |
      +---- httpx
      |
      +---- Nuclei
      |
      v
Manual Validation
      |
      v
Version Identification
      |
      v
Technology Inventory
      |
      v
Security Research
      |
      v
Controlled Validation
```

Multiple identification techniques should be combined because no single fingerprinting tool is completely reliable.

A useful principle is:

```text
Technology Detected
        !=
Vulnerability Confirmed
```

Technology identification tells us **what to investigate next**. It does not prove that a vulnerability exists.

---

# 1. Start with the HTTP Response

Before running specialised tools, inspect the application's HTTP response.

A simple request can already reveal useful information:

```bash
curl -I https://example.com
```

Alternatively:

```bash
curl -skI https://example.com
```

Example:

```text
HTTP/2 200
server: nginx/1.24.0
content-type: text/html
x-powered-by: Express
strict-transport-security: max-age=31536000
```

Potential technology indicators include:

```text
Server
X-Powered-By
Via
X-AspNet-Version
X-AspNetMvc-Version
X-Generator
X-Drupal-Cache
X-Varnish
X-Cache
CF-Ray
```

Headers can reveal:

* Web servers
* Frameworks
* Reverse proxies
* CDNs
* Caching infrastructure
* Programming languages
* Application platforms

However, headers can be removed, modified or deliberately misleading.

Treat them as evidence rather than proof.

---

# 2. Inspect the Full Response

Retrieve the complete response:

```bash
curl -ski https://example.com/
```

Save it if required:

```bash
curl -ski https://example.com/ > response.txt
```

Search interesting headers:

```bash
grep -Ei \
'server:|x-powered-by:|via:|x-aspnet|x-generator:|x-cache:|cf-ray:' \
response.txt
```

This provides a useful first-pass technology profile.

---

# 3. Cookies

Cookies frequently reveal application technologies.

Examples include:

```text
PHPSESSID
JSESSIONID
ASP.NET_SessionId
connect.sid
laravel_session
csrftoken
wordpress_*
```

Some common associations are:

| Cookie | Possible Technology |
| --- | --- |
| `PHPSESSID` | PHP |
| `JSESSIONID` | Java |
| `ASP.NET_SessionId` | ASP.NET |
| `connect.sid` | Express / Node.js |
| `laravel_session` | Laravel |
| `csrftoken` | Commonly Django |
| `wordpress_*` | WordPress |

Inspect cookies:

```bash
curl -skI https://example.com/ | grep -i set-cookie
```

Cookie names can be customised, so combine this information with other fingerprints.

---

# 4. HTML Source

HTML source can reveal significant information about the technology stack.

Download the page:

```bash
curl -sk https://example.com/ -o index.html
```

Inspect it:

```bash
less index.html
```

Search common indicators:

```bash
grep -Ei \
'generator|wordpress|drupal|joomla|next|react|angular|vue|webpack|vite' \
index.html
```

Interesting elements include:

* Generator metadata
* Framework-specific HTML attributes
* JavaScript bundle names
* CSS paths
* Static asset paths
* Comments
* API URLs
* Build identifiers
* Framework-generated elements

---

# 5. Generator Metadata

Some applications expose technology information through HTML metadata.

For example:

```html
<meta name="generator" content="WordPress">
```

or:

```html
<meta name="generator" content="Drupal">
```

Search for it:

```bash
curl -sk https://example.com/ \
  | grep -i 'name="generator"'
```

Administrators may remove generator information, so its absence proves nothing.

---

# 6. Static Asset Paths

Static asset paths can reveal frameworks and content management systems.

Examples:

```text
/wp-content/
/wp-includes/
/sites/default/files/
/_next/static/
/static/js/
/media/system/js/
```

Possible relationships include:

```text
/wp-content/
      |
      v
   WordPress
```

```text
/_next/static/
      |
      v
    Next.js
```

```text
/sites/default/
      |
      v
     Drupal
```

Asset paths can sometimes be stronger indicators than response headers because they are required by the application's frontend.

---

# 7. JavaScript Analysis

JavaScript is one of the most valuable technology identification sources in modern applications.

Extract script references:

```bash
curl -sk https://example.com/ \
  | grep -Eo '<script[^>]+src="[^"]+"'
```

JavaScript can reveal:

* Framework names
* Build systems
* API endpoints
* Package names
* Application versions
* Internal URLs
* Third-party integrations
* Source maps
* Environment information

Typical bundle names include:

```text
main.js
app.js
runtime.js
vendor.js
webpack.js
chunk.js
```

Modern frameworks may generate hashed bundles such as:

```text
main.8a2f1d.js
vendor.a991fe.js
```

JavaScript analysis gets its own dedicated reconnaissance note later because it can reveal much more than technology information alone.

---

# 8. Source Maps

Source maps can sometimes reveal original application source structures.

Look for:

```text
.js.map
```

or references such as:

```text
//# sourceMappingURL=app.js.map
```

Search downloaded JavaScript:

```bash
grep -R "sourceMappingURL" .
```

Source maps may expose:

* Original filenames
* Source directories
* Framework structure
* Internal comments
* API calls
* Application logic

Their presence does not automatically constitute a vulnerability, but they can significantly improve understanding of the application.

---

# 9. WhatWeb

WhatWeb is a useful command-line technology fingerprinting tool.

Basic usage:

```bash
whatweb https://example.com
```

More verbose output:

```bash
whatweb -v https://example.com
```

Multiple targets:

```bash
whatweb -i alive-hosts.txt
```

WhatWeb uses information such as:

* HTTP headers
* HTML patterns
* Cookies
* Scripts
* Metadata
* Known application signatures

Example output may resemble:

```text
https://example.com
HTTPServer[nginx]
HTML5
Script
Title[Example]
X-Powered-By[Next.js]
```

---

# 10. Wappalyzer

Wappalyzer identifies technologies based on known fingerprints.

It can identify categories such as:

* CMS
* JavaScript frameworks
* Web servers
* Programming languages
* Analytics
* CDNs
* Tag managers
* E-commerce platforms
* UI frameworks
* Reverse proxies

Wappalyzer is particularly useful as a second opinion after manual inspection.

A useful workflow is:

```text
Manual Inspection
      |
      v
WhatWeb
      |
      v
Wappalyzer
      |
      v
Compare Results
      |
      v
Manual Validation
```

Do not assume every detected technology is correct.

---

# 11. WappalyzerGo

WappalyzerGo provides technology detection functionality for Go applications and custom security tooling.

This can be useful when building reconnaissance pipelines where technology detection needs to be performed programmatically.

Conceptually:

```text
HTTP Response
      |
      v
Headers + HTML
      |
      v
WappalyzerGo
      |
      v
Technology Fingerprints
      |
      v
Reconnaissance Pipeline
```

This is particularly useful when fingerprinting is integrated into custom asset discovery tooling.

---

# 12. httpx Technology Detection

ProjectDiscovery httpx can perform technology detection while probing live applications.

Single target:

```bash
httpx -u https://example.com -tech-detect
```

Multiple targets:

```bash
httpx -l alive-hosts.txt \
  -silent \
  -tech-detect
```

Collect more information:

```bash
httpx -l alive-hosts.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect \
  -server \
  -ip \
  -cname
```

Example:

```text
https://portal.example.com [200] [Portal] [nginx,React]
https://api.example.com [403] [nginx]
https://shop.example.com [200] [Shop] [Cloudflare,WordPress]
```

This is particularly useful when hundreds of discovered web assets require initial classification.

---

# 13. Nuclei Technology Detection

Nuclei can complement other fingerprinting tools through technology detection templates.

For example:

```bash
nuclei -u https://example.com -tags tech
```

Against multiple targets:

```bash
nuclei -l alive-hosts.txt -tags tech
```

The results can help determine which technologies deserve further investigation.

!!! important "Detection is not confirmation"

    A technology fingerprint is not evidence that a vulnerability exists. Any security issue must be validated independently.

---

# 14. Web Server Identification

Common web servers include:

```text
nginx
Apache HTTP Server
Microsoft IIS
Caddy
LiteSpeed
Tomcat
Jetty
```

Potential indicators include:

```text
Server: nginx
Server: Apache
Server: Microsoft-IIS/10.0
```

Check:

```bash
curl -skI https://example.com/ | grep -i '^server:'
```

Or:

```bash
httpx -u https://example.com -server
```

Be aware that:

```text
Server: nginx
```

may identify only a reverse proxy.

The architecture could actually be:

```text
Internet
   |
   v
nginx
   |
   +---- Node.js
   |
   +---- Java
   |
   +---- ASP.NET
```

Understanding the layers is important.

---

# 15. Reverse Proxy Identification

Many applications sit behind reverse proxies.

Common technologies include:

* nginx
* HAProxy
* Envoy
* Traefik
* Apache
* IIS
* Cloudflare

Indicators can appear in:

```text
Server
Via
X-Forwarded-*
X-Cache
CF-*
```

Architecture may resemble:

```text
Internet
   |
   v
Cloudflare
   |
   v
nginx
   |
   v
Application
```

Fingerprinting only the outermost layer may therefore provide an incomplete picture.

---

# 16. CDN Identification

Content Delivery Networks can influence application behaviour and obscure underlying infrastructure.

Common providers include:

* Cloudflare
* Akamai
* Fastly
* Amazon CloudFront
* Azure Front Door

Indicators may include:

```text
CF-Ray
CF-Cache-Status
X-Amz-Cf-Id
X-Cache
Via
Server
```

DNS can also provide useful evidence:

```bash
dig example.com
```

or:

```bash
dnsx -d example.com -cname
```

---

# 17. WAF Identification

A Web Application Firewall may affect testing behaviour.

Possible indicators include:

* Block pages
* Specific response headers
* Response code changes
* Request-specific filtering
* CDN infrastructure
* JavaScript challenges

WAF detection can help explain why certain requests behave differently from normal application traffic.

However:

```text
Request Blocked
      !=
Application Secure
```

A WAF is an additional security control and does not replace secure application design.

---

# 18. Error Page Fingerprinting

Error pages are an often overlooked technology fingerprint.

Request a resource that is unlikely to exist:

```bash
curl -ski https://example.com/this-page-should-not-exist-12345
```

Then inspect:

* HTTP status code
* Response headers
* Response body
* HTML structure
* Error message wording
* Content type
* Response length
* Server signatures
* Framework-specific formatting

Conceptually:

```text
https://example.com/does-not-exist
                 |
                 v
               404
                 |
        +--------+--------+
        |                 |
     Headers           Response
        |                 |
        v                 v
   Web Server       Error Template
                          |
                          v
                    Framework Clues
```

Default error pages can sometimes distinguish between technologies that otherwise expose very little information.

---

## Why 404 Pages Are Useful

Applications frequently customise their normal pages while leaving default error handling unchanged.

A request to:

```text
/random-page-that-does-not-exist
```

may therefore reveal information that is not visible on:

```text
/
```

Potential fingerprints include:

```text
nginx
Apache
IIS
Flask
Django
FastAPI
aiohttp
Fiber
Gin
PHP-FPM
Laravel
Symfony
Express
Next.js
Tomcat
Spring Boot
Jetty
Ruby on Rails
Sinatra
```

0xdf maintains a particularly useful visual reference showing default 404 responses for these technologies:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

It can be useful when comparing an unknown application's error response against known default pages.

---

## Test Multiple Random Paths

Do not rely on a single nonexistent URL.

Try several harmless random paths:

```bash
curl -ski https://example.com/does-not-exist-12345

curl -ski https://example.com/random-test-page-98765

curl -ski https://example.com/nonexistent/test/path
```

Different routing layers may handle errors differently.

For example:

```text
/random
   |
   v
Reverse Proxy 404
```

while:

```text
/api/random
   |
   v
Application Framework 404
```

This can reveal multiple layers of the application architecture.

---

## Compare Application Areas

Compare error handling across different application areas:

```bash
curl -ski https://example.com/random-404

curl -ski https://example.com/api/random-404

curl -ski https://example.com/admin/random-404

curl -ski https://example.com/static/random-404
```

You might discover:

```text
Main Site
   |
   +---- nginx 404

API
   |
   +---- JSON framework error

Admin
   |
   +---- Application-specific error
```

That is useful evidence that different paths are handled by different components.

---

## Compare File Extensions

Extensions can sometimes cause requests to be processed by different backend components.

For example:

```bash
curl -ski https://example.com/does-not-exist

curl -ski https://example.com/does-not-exist.php

curl -ski https://example.com/does-not-exist.aspx
```

Compare:

```text
Status Code
Headers
Response Length
Content-Type
Error Message
HTML Structure
```

For example, a web server may process a normal nonexistent path itself but forward a `.php` request to PHP-FPM.

This difference can provide additional architectural information.

---

## JSON Error Responses

APIs frequently return JSON instead of HTML.

For example:

```json
{
  "detail": "Not Found"
}
```

or:

```json
{
  "error": "Not Found",
  "status": 404
}
```

Inspect an API error:

```bash
curl -ski https://example.com/api/does-not-exist
```

Look at:

```text
Content-Type
Response Structure
Header Behaviour
Error Wording
```

These characteristics may provide clues about the API framework.

---

## 404 Fingerprinting Workflow

A practical workflow is:

```text
Request Random Path
        |
        v
Receive 404
        |
        +---- Response Headers
        |
        +---- HTML / JSON
        |
        +---- Error Text
        |
        +---- Response Length
        |
        v
Compare Known Fingerprints
        |
        v
Candidate Technology
        |
        v
Validate Using Other Evidence
```

Never identify a framework solely from the appearance of an error page.

Combine it with:

```text
Headers
Cookies
HTML
JavaScript
Static Assets
WhatWeb
Wappalyzer
httpx
DNS
Framework Behaviour
```

---

## Architecture Matters

A default-looking 404 does not prove that the entire application uses that technology.

For example:

```text
Internet
   |
   v
Cloudflare
   |
   v
nginx
   |
   +------------------+
   |                  |
   v                  v
Next.js             API
Frontend          Spring Boot
```

Different paths can therefore produce completely different error fingerprints.

Error-page fingerprinting should be treated as one component of a broader technology identification methodology.

---

# 19. WordPress Identification

Common WordPress indicators include:

```text
/wp-admin/
/wp-login.php
/wp-content/
/wp-includes/
/wp-json/
xmlrpc.php
```

HTML may contain:

```text
/wp-content/themes/
/wp-content/plugins/
```

Check:

```bash
curl -sk https://example.com/ \
  | grep -Ei 'wp-content|wp-includes|wordpress'
```

Technology identification can then be followed by version, theme and plugin analysis where this is relevant to the assessment.

---

# 20. Drupal Identification

Potential Drupal indicators include:

```text
/sites/default/
/sites/all/
Drupal.settings
X-Drupal-Cache
```

Search:

```bash
curl -sk https://example.com/ \
  | grep -Ei 'drupal|sites/default|sites/all'
```

Headers may provide additional Drupal-specific information depending on the configuration.

---

# 21. Joomla Identification

Potential Joomla indicators include:

```text
/administrator/
/media/system/js/
/components/
/modules/
```

Generator metadata may also identify Joomla.

Use multiple indicators before concluding that a technology is present.

---

# 22. PHP Identification

Potential PHP indicators include:

```text
PHPSESSID
.php
X-Powered-By: PHP
```

For example:

```text
X-Powered-By: PHP/8.x
```

Check:

```bash
curl -skI https://example.com/ \
  | grep -Ei 'php|phpsessid'
```

The absence of `.php` extensions does not mean PHP is not being used.

Modern routing frequently hides implementation details.

---

# 23. Laravel Identification

Potential Laravel indicators include:

```text
laravel_session
XSRF-TOKEN
```

Other clues may appear in:

* Error pages
* HTML
* JavaScript
* Framework-specific paths
* Response behaviour

Check cookies:

```bash
curl -skI https://example.com/ \
  | grep -Ei 'laravel|xsrf'
```

The default Laravel error page may also provide a useful fingerprint when it has not been customised.

---

# 24. ASP.NET Identification

Potential indicators include:

```text
ASP.NET_SessionId
__VIEWSTATE
__EVENTVALIDATION
X-AspNet-Version
X-AspNetMvc-Version
```

Search:

```bash
curl -sk https://example.com/ \
  | grep -Ei '__VIEWSTATE|__EVENTVALIDATION|ASP.NET'
```

Headers may expose:

```text
X-Powered-By: ASP.NET
```

Classic ASP.NET applications can often be distinguished from newer ASP.NET Core applications through framework artefacts and application behaviour.

---

# 25. Java Application Identification

Potential Java indicators include:

```text
JSESSIONID
```

Common Java application technologies include:

```text
Tomcat
Jetty
Spring
Spring Boot
JBoss
WildFly
WebLogic
WebSphere
```

Check cookies:

```bash
curl -skI https://example.com/ \
  | grep -i jsessionid
```

Server headers, error pages and application behaviour may provide additional evidence.

---

# 26. Spring Boot Identification

Spring Boot applications may expose distinctive behaviour.

Potential indicators include:

```text
Spring
Spring Boot
Whitelabel Error Page
JSESSIONID
```

Some deployments expose management functionality under paths such as:

```text
/actuator
/actuator/health
/actuator/info
```

Whether those endpoints exist or are accessible depends on the application's configuration.

Technology detection should therefore lead to investigation rather than assumptions.

---

# 27. Node.js Identification

Potential indicators include:

```text
X-Powered-By: Express
connect.sid
```

Check:

```bash
curl -skI https://example.com/ \
  | grep -Ei 'express|connect.sid'
```

Node.js itself may not be directly exposed through headers.

Application behaviour, JavaScript and framework fingerprints can provide additional evidence.

---

# 28. Express Identification

Express applications may expose:

```text
X-Powered-By: Express
```

Check:

```bash
curl -skI https://example.com/ \
  | grep -i 'x-powered-by'
```

A default Express 404 can also provide a useful fingerprint.

For example, an uncustomised Express application commonly includes a short error response indicating that the requested method and path were not found.

Compare suspected error responses against the 0xdf 404 reference when useful.

---

# 29. Next.js Identification

Next.js applications have several useful fingerprints.

Potential indicators include:

```text
/_next/static/
/_next/image
__NEXT_DATA__
Next.js
x-nextjs-cache
x-powered-by: Next.js
```

Search the HTML:

```bash
curl -sk https://example.com/ \
  | grep -Ei '_next|__NEXT_DATA__|nextjs'
```

Check headers:

```bash
curl -skI https://example.com/ \
  | grep -Ei 'next|powered'
```

Static resources may contain paths such as:

```text
/_next/static/chunks/
/_next/static/css/
/_next/static/media/
```

A Next.js deployment may conceptually look like:

```text
Browser
   |
   v
CDN / Reverse Proxy
   |
   v
Next.js
   |
   +---- React Frontend
   |
   +---- Server Components
   |
   +---- API Routes
   |
   +---- Middleware
```

Identifying Next.js should lead to further questions:

```text
Next.js Detected
       |
       v
Can the Version Be Identified?
       |
       v
Which Features Are Used?
       |
       v
Middleware?
API Routes?
Server Components?
Image Optimisation?
       |
       v
Relevant Security Research
```

---

# 30. React Identification

Potential React indicators include:

* React-specific JavaScript bundles
* React Developer Tools artefacts
* Build metadata
* Framework-specific DOM behaviour
* Next.js or other React-based frameworks

Static files may include:

```text
static/js/main.*
static/js/runtime.*
```

React identification alone says little about the backend technology.

Architecture may be:

```text
React
  |
  v
REST API
  |
  v
Java / .NET / Node.js / PHP
```

The frontend and backend should therefore be fingerprinted independently.

---

# 31. Angular Identification

Potential Angular indicators include:

```text
ng-version
_nghost
_ngcontent
main.js
polyfills.js
runtime.js
```

Search:

```bash
curl -sk https://example.com/ \
  | grep -Ei 'ng-version|_nghost|_ngcontent'
```

JavaScript bundle structures can provide additional clues.

Where an Angular version is exposed, record it for later dependency and security research.

---

# 32. Vue Identification

Potential Vue indicators may appear in:

* JavaScript bundles
* Framework-specific DOM behaviour
* Build artefacts
* Vue development metadata

Automated tools such as Wappalyzer and WhatWeb can provide an initial indication, but manual validation is still useful.

---

# 33. API Technology Identification

APIs should be fingerprinted separately from the primary frontend.

Inspect:

```bash
curl -ski https://example.com/api/
```

Look at:

* Content-Type
* Error structure
* Authentication headers
* Server headers
* CORS headers
* JSON field names
* Framework-specific errors

For example:

```text
Frontend
   |
   +---- Next.js

API
   |
   +---- Spring Boot
```

or:

```text
Frontend
   |
   +---- Angular

API
   |
   +---- ASP.NET Core
```

This distinction can significantly affect subsequent testing.

---

# 34. REST Identification

REST APIs commonly expose:

```text
application/json
```

and resource-oriented paths such as:

```text
/api/users
/api/orders
/api/v1/accounts
```

Look for:

* API versioning
* Authentication mechanisms
* Documentation
* Error structures
* Framework-specific headers

---

# 35. GraphQL Identification

Potential GraphQL endpoints include:

```text
/graphql
/api/graphql
/graphql/v1
```

GraphQL responses and error structures can provide additional framework information.

Technology identification may lead to investigation of:

* GraphQL server implementation
* Introspection configuration
* Schema exposure
* Authentication
* Authorisation

Detailed testing belongs in the API Security notes.

---

# 36. SOAP Identification

SOAP services commonly expose XML and may provide WSDL documents.

Potential paths include:

```text
/service
/services
?wsdl
/service?wsdl
```

Indicators include:

```text
Content-Type: text/xml
SOAPAction
Envelope
WSDL
```

The underlying platform may be Java, .NET or another enterprise application stack.

---

# 37. TLS and Certificate Information

Certificates can also reveal infrastructure information.

Inspect:

```bash
openssl s_client \
  -connect example.com:443 \
  -servername example.com
```

Certificate information may reveal:

* Subject Alternative Names
* Related hostnames
* Certificate authority
* Organisation information
* Infrastructure relationships

Certificate Transparency data can further expand this information during reconnaissance.

---

# 38. DNS as a Technology Source

DNS can reveal hosting and infrastructure technologies.

Check:

```bash
dig example.com
```

and:

```bash
dig CNAME example.com
```

Interesting CNAME values may reveal services such as:

```text
CloudFront
Azure
Cloudflare
GitHub Pages
Netlify
Vercel
Heroku
```

For example:

```text
app.example.com
      |
      v
project.vercel.app
```

This provides useful deployment context even if the application itself does not expose obvious technology information.

---

# 39. Version Identification

Technology names become significantly more useful when a reliable version can also be identified.

Potential version sources include:

```text
HTTP headers
HTML
JavaScript
Static assets
Generator metadata
Error pages
Package files
API responses
Documentation
Public repositories
```

For example:

```text
Technology: nginx
Version: 1.x
```

is more useful than:

```text
Technology: nginx
```

However, version information must be validated carefully because banners can be stale or intentionally modified.

---

# 40. Avoid False Positives

Automated technology detection produces false positives.

For example:

```text
Wappalyzer
    |
    +---- React
    +---- Next.js
    +---- nginx
```

should lead to:

```text
Automated Detection
        |
        v
Manual Validation
        |
        +---- Headers
        +---- HTML
        +---- JavaScript
        +---- Cookies
        +---- Error Pages
        +---- Static Assets
        |
        v
Confirmed Technology Inventory
```

The stronger the conclusion, the more independent evidence should support it.

---

# 41. Technology Does Not Equal Vulnerability

One of the most important principles is:

```text
Technology Detected
        !=
Vulnerability Confirmed
```

For example:

```text
Next.js Detected
       |
       v
Determine Version
       |
       v
Research Security Advisories
       |
       v
Understand Preconditions
       |
       v
Check Application Configuration
       |
       v
Controlled Validation
       |
       v
Confirmed / Not Confirmed
```

Do not report a vulnerability simply because a technology appears in a vulnerability database.

---

# 42. Map Technologies to Security Research

Once a technology has been identified, research can begin.

Useful sources include:

* Vendor security advisories
* NVD
* CVE records
* GitHub Security Advisories
* Release notes
* Framework documentation
* Security research publications
* Exploit databases
* Source code repositories

The objective is to answer:

```text
What technology is this?
        |
        v
What version is it?
        |
        v
Is the version affected?
        |
        v
Are the vulnerable features enabled?
        |
        v
Are the attack prerequisites present?
        |
        v
Can the behaviour be safely validated?
```

---

# 43. Prioritise Technologies

Not every detected technology deserves the same level of investigation.

Prioritise components based on factors such as:

* Internet exposure
* Version
* Authentication requirements
* Known vulnerability history
* Application role
* Privilege level
* Input processing
* File processing
* Network access
* Administrative functionality

For example:

```text
Technology Inventory
        |
        +---- Static CSS framework
        |
        +---- Analytics library
        |
        +---- Internet-facing CMS
        |
        +---- Authentication platform
        |
        +---- Server-side framework
```

The server-side framework and authentication platform may deserve more attention than a purely visual library.

---

# 44. Technology Inventory

Maintain an organised inventory.

For example:

| Host | Layer | Technology | Version | Evidence |
| --- | --- | --- | --- | --- |
| `www.example.com` | CDN | Cloudflare | Unknown | Headers |
| `www.example.com` | Proxy | nginx | Unknown | Server header |
| `www.example.com` | Frontend | Next.js | Unknown | `/_next/` |
| `api.example.com` | Backend | Spring Boot | Unknown | Error response |
| `shop.example.com` | CMS | WordPress | Unknown | `/wp-content/` |

An additional column can track investigation status:

| Technology | Version | Research | Validation |
| --- | --- | --- | --- |
| Next.js | Unknown | Pending | Pending |
| nginx | Unknown | Reviewed | N/A |
| WordPress | Identified | Pending | Pending |

This prevents useful fingerprinting information from being lost during a large assessment.

---

# 45. Practical Fingerprinting Pipeline

A practical workflow for multiple live hosts could start with:

```bash
httpx -l alive-hosts.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect \
  -server \
  -ip \
  -cname \
  > technology-scan.txt
```

Run WhatWeb:

```bash
whatweb -i alive-hosts.txt > whatweb.txt
```

Then manually investigate interesting targets.

The process becomes:

```text
alive-hosts.txt
      |
      +---- httpx
      |
      +---- WhatWeb
      |
      +---- Wappalyzer
      |
      v
Candidate Technologies
      |
      v
Manual Inspection
      |
      +---- Headers
      +---- Cookies
      +---- HTML
      +---- JavaScript
      +---- Error Pages
      +---- DNS
      |
      v
Technology Inventory
```

---

# 46. Quick Reference

## Headers

```bash
curl -skI https://example.com/
```

## Full Response

```bash
curl -ski https://example.com/
```

## Cookies

```bash
curl -skI https://example.com/ \
  | grep -i set-cookie
```

## HTML

```bash
curl -sk https://example.com/ -o index.html
```

## Search HTML

```bash
grep -Ei \
'wordpress|drupal|joomla|next|react|angular|vue|generator' \
index.html
```

## WhatWeb

```bash
whatweb https://example.com
```

## WhatWeb Verbose

```bash
whatweb -v https://example.com
```

## httpx

```bash
httpx -u https://example.com \
  -status-code \
  -title \
  -tech-detect \
  -server
```

## Multiple Hosts

```bash
httpx -l alive-hosts.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect \
  -server \
  -ip \
  -cname
```

## Nuclei Technology Detection

```bash
nuclei -u https://example.com -tags tech
```

## Random 404

```bash
curl -ski \
  https://example.com/this-page-should-not-exist-12345
```

## API 404

```bash
curl -ski \
  https://example.com/api/this-page-should-not-exist-12345
```

## DNS

```bash
dig example.com
```

## CNAME

```bash
dig CNAME example.com
```

---

# 47. Final Workflow

The complete technology identification process can be summarised as:

```text
                       Live Web Target
                              |
              +---------------+---------------+
              |               |               |
           Headers          HTML           Cookies
              |               |               |
              +---------------+---------------+
                              |
                 +------------+------------+
                 |                         |
             JavaScript                Error Pages
                 |                         |
                 +------------+------------+
                              |
                              v
                    Automated Detection
                              |
              +---------------+---------------+
              |               |               |
           WhatWeb        Wappalyzer        httpx
              |               |               |
              +---------------+---------------+
                              |
                            Nuclei
                              |
                              v
                     Manual Validation
                              |
              +---------------+---------------+
              |               |               |
          Frontend          Backend       Infrastructure
              |               |               |
              +---------------+---------------+
                              |
                              v
                     Version Identification
                              |
                              v
                      Security Research
                              |
                              v
                   Preconditions Present?
                              |
                     +--------+--------+
                     |                 |
                    No                Yes
                     |                 |
                     v                 v
                   Stop        Controlled Validation
                                       |
                                       v
                                Confirmed Finding?
```

Technology identification should ultimately answer more than:

> What software is this application using?

The more useful questions are:

```text
What is it?
What version is it?
Where in the architecture is it used?
How confident am I in the fingerprint?
Which functionality does it expose?
Does that technology change my testing methodology?
Are relevant security advisories applicable?
Can any suspected issue be independently validated?
```

That transforms technology fingerprinting from simple reconnaissance into actionable security assessment information.

---

## Useful References

### Default 404 Fingerprints

The following reference is particularly useful when manually comparing error responses:

[0xdf - Default 404 Pages](https://0xdf.gitlab.io/cheatsheets/404){ target="_blank" rel="noopener noreferrer" }

It contains examples for technologies including nginx, Apache, IIS, Flask, Django, FastAPI, aiohttp, Fiber, Gin, PHP-FPM, Laravel, Symfony, Express, Next.js, Tomcat, Spring Boot, Jetty, Ruby on Rails and Sinatra.

### General Technology Research

Useful sources when researching identified technologies include:

* Official vendor documentation
* Vendor security advisories
* NVD
* CVE records
* GitHub Security Advisories
* Release notes
* Project source repositories

Prefer primary vendor information when determining whether a particular version is affected by a security issue.

---

## Related Notes

* [Reconnaissance Overview](index.md)
* [Subdomain Enumeration](subdomain-enumeration.md)
* [Content Discovery](content-discovery.md)
* [Parameter Discovery](parameter-discovery.md)
* [JavaScript Analysis](javascript-analysis.md)
* [Web Application Testing Methodology](../methodology.md)
* [Web Application Pentesting Checklist](../checklist.md)
