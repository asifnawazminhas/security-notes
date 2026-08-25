# Content Discovery

Content discovery is the process of identifying directories, files, endpoints and functionality that are not immediately visible through normal application navigation.

During a web application penetration test, content discovery can reveal administrative interfaces, APIs, backup files, configuration files, development functionality, debug endpoints, documentation, source maps and legacy application components.

The objective is not simply to run a large wordlist against a target. Effective content discovery combines **manual investigation, technology identification, crawling, targeted wordlists, recursive discovery and careful analysis of HTTP responses**.

!!! warning "Authorised Security Testing"

    Perform content discovery only against applications and systems that are within the authorised scope of the security assessment.

---

## Content Discovery Workflow

A practical workflow can be organised as:

```text
Live Web Target
      |
      v
Manual Discovery
      |
      +---- robots.txt
      +---- sitemap.xml
      +---- .well-known/
      +---- HTML
      +---- JavaScript
      |
      v
Technology Identification
      |
      v
Select Wordlists
      |
      v
Directory Discovery
      |
      +---- ffuf
      +---- feroxbuster
      +---- dirsearch
      |
      v
File Discovery
      |
      v
Extension Discovery
      |
      v
Recursive Discovery
      |
      v
Interesting Endpoints
      |
      +---- Admin
      +---- API
      +---- Authentication
      +---- Backups
      +---- Configuration
      +---- Debug
      +---- Documentation
      +---- Uploads
      +---- Source Maps
      |
      v
Manual Validation
      |
      v
Expanded Attack Surface
```

Content discovery should be iterative.

A newly discovered directory can contain additional directories, files and functionality that require another round of discovery.

---

# 1. Start Manually

Before using automated tools, inspect the application manually.

Browse the application and identify:

* Navigation links
* Forms
* Authentication pages
* API requests
* JavaScript files
* Static resources
* Upload functionality
* Download functionality
* Administrative links
* Error pages
* Redirects

Use the browser developer tools and an intercepting proxy to understand how the application is structured.

A surprising amount of content can be discovered without fuzzing.

---

# 2. robots.txt

One of the first resources to check is:

```text
/robots.txt
```

Request it:

```bash
curl -sk https://example.com/robots.txt
```

Example:

```text
User-agent: *
Disallow: /admin/
Disallow: /internal/
Disallow: /backup/
```

These entries are not access controls.

They simply instruct search engine crawlers which locations should not normally be indexed.

From a reconnaissance perspective, they may reveal interesting application paths.

For example:

```text
robots.txt
    |
    +---- /admin/
    |
    +---- /internal/
    |
    +---- /backup/
```

Each discovered path should be manually validated.

---

# 3. sitemap.xml

Check:

```text
/sitemap.xml
```

Request it:

```bash
curl -sk https://example.com/sitemap.xml
```

Sitemaps may reveal:

* Application routes
* Product pages
* Legacy pages
* Language-specific paths
* Hidden functionality
* Additional subdomains

A sitemap may also reference additional sitemap files.

For example:

```xml
<sitemap>
    <loc>https://example.com/sitemap-products.xml</loc>
</sitemap>
```

These should also be reviewed.

---

# 4. .well-known

The `.well-known` directory contains standardised resources used by various protocols and services.

Examples include:

```text
/.well-known/security.txt
/.well-known/openid-configuration
/.well-known/assetlinks.json
/.well-known/apple-app-site-association
/.well-known/change-password
```

Check:

```bash
curl -sk https://example.com/.well-known/security.txt
```

and where relevant:

```bash
curl -sk https://example.com/.well-known/openid-configuration
```

These resources can reveal information about:

* Security contacts
* Authentication infrastructure
* OAuth
* OpenID Connect
* Mobile applications
* Related domains
* API endpoints

---

# 5. security.txt

A security policy may be available at:

```text
/.well-known/security.txt
```

or occasionally:

```text
/security.txt
```

Request:

```bash
curl -sk https://example.com/.well-known/security.txt
```

This may provide useful information about:

* Security contact details
* Responsible disclosure policies
* Scope information
* Security acknowledgements
* Policy URLs

For authorised assessments, the formal engagement scope remains authoritative.

---

# 6. Inspect HTML

HTML can contain links and resources that are not immediately visible in the rendered application.

Download the page:

```bash
curl -sk https://example.com/ -o index.html
```

Search URLs:

```bash
grep -Eo 'href="[^"]+"' index.html
```

Search form actions:

```bash
grep -Eo 'action="[^"]+"' index.html
```

Search interesting strings:

```bash
grep -Ei \
'admin|api|debug|internal|upload|download|backup|swagger|graphql' \
index.html
```

HTML comments can also contain useful information.

Search:

```bash
grep -n '<!--' index.html
```

---

# 7. JavaScript

Modern web applications frequently expose large portions of their attack surface through JavaScript.

JavaScript can reveal:

* API endpoints
* Hidden routes
* Administrative endpoints
* Parameter names
* Internal URLs
* WebSocket endpoints
* Feature flags
* Development functionality
* Source maps

Extract JavaScript references:

```bash
curl -sk https://example.com/ \
  | grep -Eo '<script[^>]+src="[^"]+"'
```

JavaScript analysis will be covered in more detail in the dedicated reconnaissance note.

---

# 8. Choose the Right Wordlist

Wordlist selection has a significant effect on content discovery.

Using the largest available wordlist is not automatically better.

Consider:

* Application technology
* Application purpose
* Available testing time
* Request limits
* Server performance
* Scope
* Known application structure

A small targeted wordlist may outperform a huge generic list.

---

# 9. SecLists

SecLists contains many useful discovery wordlists.

On Kali Linux it is commonly available under:

```text
/usr/share/seclists/
```

Web content lists are commonly located under:

```text
/usr/share/seclists/Discovery/Web-Content/
```

List them:

```bash
ls /usr/share/seclists/Discovery/Web-Content/
```

Useful examples include:

```text
common.txt
directory-list-2.3-medium.txt
raft-small-directories.txt
raft-medium-directories.txt
raft-large-directories.txt
raft-small-files.txt
raft-medium-files.txt
raft-large-files.txt
raft-small-words.txt
raft-medium-words.txt
```

Different wordlists serve different purposes.

---

# 10. Directory Wordlists

For directory discovery, a useful starting point is:

```text
raft-medium-directories.txt
```

For example:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

For faster initial discovery:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-small-directories.txt
```

A useful strategy is:

```text
Small Wordlist
      |
      v
Initial Results
      |
      v
Interesting Target?
      |
   +--+--+
   |     |
  No    Yes
         |
         v
   Larger / Targeted
      Wordlists
```

---

# 11. ffuf

ffuf is a fast web fuzzer commonly used for content discovery.

Basic directory discovery:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

A shorter form is:

```bash
ffuf -u https://example.com/FUZZ -w wordlist.txt
```

The `FUZZ` keyword identifies where each wordlist entry should be inserted.

---

# 12. Understanding ffuf Results

Example output may contain:

```text
admin        [Status: 302, Size: 0]
api          [Status: 200, Size: 128]
backup       [Status: 403, Size: 153]
login        [Status: 200, Size: 4821]
uploads      [Status: 301, Size: 178]
```

Do not look only at status `200`.

Interesting status codes include:

| Status | Meaning |
| --- | --- |
| 200 | Resource returned successfully |
| 204 | Successful response without body |
| 301 | Permanent redirect |
| 302 | Temporary redirect |
| 307 | Temporary redirect preserving method |
| 308 | Permanent redirect preserving method |
| 401 | Authentication required |
| 403 | Access forbidden |
| 405 | Method not allowed |
| 500 | Server-side error |

A `401` or `403` may be more interesting than a public `200` page.

---

# 13. Match Status Codes

ffuf can match specific HTTP status codes.

For example:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -mc 200,204,301,302,307,401,403,405
```

Alternatively, match all responses:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -mc all
```

Then filter unwanted responses.

---

# 14. Filter Status Codes

For example, exclude standard `404` responses:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -mc all \
  -fc 404
```

However, filtering only by status code is often insufficient because many applications return `200` for nonexistent pages.

This is known as a soft `404`.

---

# 15. Soft 404 Responses

Some applications return:

```text
HTTP/1.1 200 OK
```

even when the requested resource does not exist.

For example:

```text
/random-does-not-exist
```

may return:

```text
200 OK
```

with:

```text
Page not found
```

Test a random path before starting discovery:

```bash
curl -ski https://example.com/random-does-not-exist-12345
```

Record:

* Status code
* Response length
* Word count
* Line count
* Response body
* Redirect behaviour

This creates a baseline for nonexistent resources.

---

# 16. Response Size Filtering

Suppose nonexistent pages consistently return:

```text
Status: 200
Size: 4242
```

Filter that size:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -fs 4242
```

This can dramatically improve discovery results.

---

# 17. Word Count Filtering

Responses can also be filtered by word count.

For example:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -fw 37
```

This can be useful when dynamic values make the byte size change slightly while the overall response structure remains similar.

---

# 18. Line Count Filtering

Filter by number of lines:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -fl 12
```

Filtering can therefore use:

```text
Status
Size
Words
Lines
```

A good content discovery workflow establishes the baseline first and then selects the appropriate filter.

---

# 19. ffuf Auto Calibration

ffuf can attempt to automatically identify common false-positive responses.

Use:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -ac
```

Auto calibration can be useful when applications return similar responses for nonexistent content.

Always manually inspect the results because automated calibration can occasionally hide interesting responses.

---

# 20. Follow Redirects

Redirects can be useful during discovery.

Follow them with:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -r
```

However, sometimes the redirect itself is the interesting behaviour.

For example:

```text
/admin
   |
   v
302
   |
   v
/login
```

The redirect reveals that `/admin` likely exists.

For this reason, retaining redirect information is often useful during initial discovery.

---

# 21. File Discovery

Directory discovery should be complemented by file discovery.

Use a file-oriented wordlist:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
```

Potential discoveries include:

```text
config
backup
database
debug
test
old
settings
admin
login
```

File extensions can then be tested separately.

---

# 22. Extension Discovery

Technology identification should influence which extensions are tested.

Common extensions include:

```text
.php
.aspx
.asp
.jsp
.json
.xml
.txt
.html
.js
.map
.bak
.old
.zip
.tar
.gz
```

For example:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -e .php,.txt,.bak,.old,.zip
```

This tests entries such as:

```text
admin
admin.php
admin.txt
admin.bak
admin.old
admin.zip
```

---

# 23. Technology-Specific Extensions

Technology identification should guide content discovery.

For example:

```text
Technology
    |
    +---- PHP
    |      |
    |      +---- .php
    |
    +---- ASP.NET
    |      |
    |      +---- .aspx
    |
    +---- Java
    |      |
    |      +---- .jsp
    |
    +---- Static / API
           |
           +---- .json
           +---- .xml
           +---- .txt
```

Do not blindly test every possible extension.

Use evidence from the application stack.

---

# 24. Backup Files

Backup files can unintentionally expose application content or configuration.

Common patterns include:

```text
config.php.bak
config.php.old
config.php~
index.php.bak
web.config.old
application.properties.bak
backup.zip
site.zip
www.zip
```

Potential backup extensions include:

```text
.bak
.old
.orig
.save
.tmp
~
.zip
.tar
.gz
```

These can be incorporated into targeted discovery.

---

# 25. Configuration Files

Potentially interesting configuration files include:

```text
.env
web.config
.htaccess
.htpasswd
application.properties
application.yml
application.yaml
config.php
settings.php
package.json
composer.json
```

The presence of these files does not mean they are publicly accessible.

The objective is to identify accidental exposure.

---

# 26. Environment Files

A commonly investigated file is:

```text
.env
```

Request:

```bash
curl -ski https://example.com/.env
```

If the server correctly denies access or returns a normal `404`, record that behaviour and continue.

Do not assume that a file exists simply because an application uses a framework that commonly supports it.

---

# 27. Git Metadata

Accidentally exposed version-control metadata can reveal application structure.

A useful check is:

```text
/.git/
```

For example:

```bash
curl -ski https://example.com/.git/HEAD
```

A normal secure deployment should not expose repository metadata publicly.

Other version-control artefacts may include:

```text
/.svn/
/.hg/
```

Any exposed repository information should be handled carefully because it may contain sensitive source code or configuration.

---

# 28. Source Maps

JavaScript source maps may be exposed as:

```text
app.js.map
main.js.map
bundle.js.map
```

If a JavaScript file contains:

```text
//# sourceMappingURL=app.js.map
```

test whether the referenced source map is accessible.

Source maps may reveal:

* Original filenames
* Source directories
* Frontend source code
* API endpoints
* Comments
* Application structure

---

# 29. API Discovery

Common API paths include:

```text
/api/
/api/v1/
/api/v2/
/rest/
/services/
/graphql
```

Technology-specific reconnaissance may reveal additional API conventions.

For example:

```bash
ffuf \
  -u https://example.com/api/FUZZ \
  -w wordlist.txt
```

Once an API base path is identified, perform discovery specifically within that path.

---

# 30. Swagger and OpenAPI

API documentation may expose a significant portion of the application's attack surface.

Potential paths include:

```text
/swagger
/swagger/
/swagger-ui
/swagger-ui/
/swagger-ui.html
/api-docs
/v2/api-docs
/v3/api-docs
/openapi.json
/swagger.json
```

Check manually:

```bash
curl -ski https://example.com/swagger
```

and:

```bash
curl -ski https://example.com/openapi.json
```

API documentation can reveal:

* Endpoints
* HTTP methods
* Parameters
* Request bodies
* Authentication schemes
* Object models

---

# 31. GraphQL

Potential GraphQL endpoints include:

```text
/graphql
/api/graphql
/graphql/v1
```

A discovered GraphQL endpoint should be recorded for the API testing phase.

The purpose of content discovery at this stage is primarily to identify its existence and location.

---

# 32. Administrative Interfaces

Interesting paths may include:

```text
/admin
/administrator
/manage
/management
/console
/dashboard
/backend
/control
/panel
```

Search with a targeted list:

```bash
printf '%s\n' \
admin \
administrator \
manage \
management \
console \
dashboard \
backend \
control \
panel \
> admin-paths.txt
```

Then:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w admin-paths.txt
```

A `401`, `403` or redirect to authentication can still confirm that functionality exists.

---

# 33. Debug and Development Endpoints

Potentially interesting paths include:

```text
/debug
/dev
/test
/testing
/status
/health
/metrics
/info
/console
```

Framework-specific endpoints should be selected based on technology identification rather than tested blindly against every target.

Development functionality can reveal:

* Debug information
* Internal paths
* Environment information
* Application state
* Software versions

---

# 34. Spring Boot Content Discovery

If Spring Boot has been identified, relevant paths may include:

```text
/actuator
/actuator/health
/actuator/info
```

Depending on configuration, additional management endpoints may exist.

The presence of Spring Boot alone does not mean these resources are publicly exposed.

Check only what is appropriate within the authorised scope.

---

# 35. WordPress Content Discovery

If WordPress is identified, useful paths include:

```text
/wp-admin/
/wp-login.php
/wp-content/
/wp-includes/
/wp-json/
```

Additional content discovery may focus on:

```text
/wp-content/plugins/
/wp-content/themes/
/wp-content/uploads/
```

Technology-specific enumeration is generally more effective than using only generic wordlists.

---

# 36. Recursive Discovery

A discovered directory can contain additional hidden content.

For example:

```text
/admin/
   |
   +---- login
   |
   +---- users
   |
   +---- settings
```

If `/admin/` is discovered, run another discovery pass:

```bash
ffuf \
  -u https://example.com/admin/FUZZ \
  -w wordlist.txt
```

The process becomes:

```text
/
|
+---- admin/
|       |
|       +---- users/
|       |
|       +---- settings/
|
+---- api/
        |
        +---- v1/
                |
                +---- users
                +---- accounts
```

Recursive discovery is particularly useful for large applications.

---

# 37. feroxbuster

feroxbuster is designed for recursive content discovery.

Basic usage:

```bash
feroxbuster \
  -u https://example.com
```

Specify a wordlist:

```bash
feroxbuster \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
```

Specify extensions:

```bash
feroxbuster \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -x php,txt,json,bak
```

feroxbuster can automatically recurse into discovered directories, which makes it useful when mapping larger applications.

---

# 38. Limit feroxbuster Depth

Recursive discovery can generate large numbers of requests.

Control recursion depth:

```bash
feroxbuster \
  -u https://example.com \
  -d 2
```

Use an appropriate depth for the application and assessment scope.

More recursion is not automatically better.

---

# 39. dirsearch

dirsearch is another commonly used content discovery tool.

Basic usage:

```bash
dirsearch -u https://example.com
```

Specify extensions:

```bash
dirsearch \
  -u https://example.com \
  -e php,html,js,json,txt,bak
```

Specify a wordlist:

```bash
dirsearch \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
```

Different tools may produce slightly different results because they handle recursion, redirects, extensions and filtering differently.

---

# 40. Compare Tools Rather Than Trusting One

A useful workflow may be:

```text
                Target
                   |
        +----------+----------+
        |          |          |
       ffuf    feroxbuster  dirsearch
        |          |          |
        +----------+----------+
                   |
                   v
             Compare Results
                   |
                   v
            Manual Validation
```

You do not necessarily need to run all three against every application.

Choose the tool that best fits the task.

---

# 41. Virtual Host Discovery

Some web servers host multiple applications on the same IP address.

For example:

```text
10.10.10.10
    |
    +---- www.example.com
    |
    +---- admin.example.com
    |
    +---- dev.example.com
```

If the server routes requests based on the `Host` header, virtual host discovery may reveal additional applications.

A basic ffuf pattern is:

```bash
ffuf \
  -u https://example.com/ \
  -H "Host: FUZZ.example.com" \
  -w wordlist.txt
```

This should only be performed where the wildcard domain or relevant hostnames are within the authorised scope.

---

# 42. Baseline Virtual Host Behaviour

Before fuzzing the `Host` header, send a random hostname:

```bash
curl -ski \
  -H "Host: random-does-not-exist.example.com" \
  https://example.com/
```

Record the response:

```text
Status
Size
Words
Lines
Redirect
```

Then filter that baseline during discovery.

This prevents default virtual-host responses from appearing as false positives.

---

# 43. Authentication Boundaries

Content discovery should be performed both before and after authentication where the scope and available accounts allow it.

For example:

```text
Unauthenticated
      |
      +---- /
      +---- /login
      +---- /public
      |
      v
Authenticated
      |
      +---- /account
      +---- /dashboard
      +---- /api
      +---- /settings
```

Authenticated application areas frequently expose significantly more functionality.

Use the appropriate authenticated session through your testing proxy or tool configuration.

---

# 44. Different User Roles

If multiple test accounts are available, repeat discovery from different privilege levels.

For example:

```text
Anonymous
    |
    v
User
    |
    v
Manager
    |
    v
Administrator
```

Different roles may expose different routes.

This can later support authorisation testing.

---

# 45. Crawling and Content Discovery

Crawling and content discovery complement each other.

```text
Crawling
   |
   +---- Follow existing links
   |
   +---- Parse JavaScript
   |
   +---- Discover referenced endpoints
```

while:

```text
Content Discovery
   |
   +---- Guess unlinked resources
   |
   +---- Discover hidden directories
   |
   +---- Discover backup files
```

Combining both approaches provides better coverage.

---

# 46. Historical URLs

Historical sources may reveal resources that are no longer linked.

Useful tools include:

```text
waybackurls
gau
```

For example:

```bash
waybackurls example.com > historical-urls.txt
```

or:

```bash
gau example.com > historical-urls.txt
```

Review paths:

```bash
cat historical-urls.txt \
  | sed 's/[?#].*$//' \
  | sort -u
```

Historical content should be validated before assuming it still exists.

---

# 47. Extract Paths from Historical URLs

You can extract path information from historical URLs.

For example:

```bash
cat historical-urls.txt \
  | awk -F/ '{for(i=4;i<=NF;i++) printf "/"$i; print ""}' \
  | sort -u
```

This can reveal naming patterns that improve subsequent wordlist selection.

For example:

```text
/api/v1/
/legacy/
/old-admin/
/reports/
/downloads/
```

These patterns can then guide targeted discovery.

---

# 48. Build Target-Specific Wordlists

One of the most effective techniques is creating a wordlist from the application itself.

Sources include:

* Existing URLs
* JavaScript
* HTML
* Historical URLs
* API documentation
* File names
* Product terminology
* Business terminology

Suppose the application contains terms such as:

```text
customer
invoice
report
document
account
payment
```

These can become a custom discovery list:

```text
customer
customers
invoice
invoices
report
reports
document
documents
account
accounts
payment
payments
```

Target-specific wordlists often discover resources that generic lists miss.

---

# 49. Case Sensitivity

Some servers and frameworks treat paths as case-sensitive.

For example:

```text
/admin
/Admin
/ADMIN
```

may behave differently.

This is particularly relevant on Linux-hosted applications and certain frameworks.

Do not assume path case is normalised.

---

# 50. Trailing Slashes

Compare:

```text
/admin
```

with:

```text
/admin/
```

They may produce:

```text
200
301
302
403
404
```

depending on server and framework behaviour.

Redirect behaviour can itself confirm that a directory exists.

---

# 51. HTTP Methods

A resource returning:

```text
405 Method Not Allowed
```

may still be interesting.

For example:

```bash
curl -ski https://example.com/api/users
```

may return:

```text
405 Method Not Allowed
```

This can indicate that the endpoint exists but does not accept `GET`.

Record such endpoints for later API testing.

---

# 52. OPTIONS

Where appropriate, inspect allowed methods:

```bash
curl -ski \
  -X OPTIONS \
  https://example.com/api/example
```

Responses may contain:

```text
Allow: GET, POST, OPTIONS
```

Do not assume the `Allow` header is complete or authoritative, but it can provide useful information.

---

# 53. Custom Headers and Authentication

Some endpoints may behave differently depending on headers or authentication.

For example:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -H "Authorization: Bearer TOKEN"
```

or:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -H "Cookie: session=VALUE"
```

Use only test credentials and tokens provided or generated within the authorised assessment.

Avoid storing sensitive tokens directly in notes or repositories.

---

# 54. Rate Control

Content discovery can generate significant traffic.

Use rate controls where appropriate.

For example with ffuf:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -rate 50
```

The correct rate depends on:

* Assessment rules
* Application capacity
* Network conditions
* Scope
* Testing window

The objective is discovery, not service disruption.

---

# 55. Threads

Concurrency can also affect application load.

For example:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -t 20
```

Higher thread counts are not automatically better.

Use conservative values when application stability is uncertain.

---

# 56. Save ffuf Results

Do not rely solely on terminal output.

Save results:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -o ffuf-results.json \
  -of json
```

Other output formats may also be available depending on the tool version.

Keeping raw results makes later analysis and reporting easier.

---

# 57. Interesting Response Sizes

When reviewing results, group responses by size.

Suppose you see:

```text
admin      403    153 bytes
internal   403    153 bytes
backup     403    153 bytes
random     403    153 bytes
portal     403   4281 bytes
```

The different size for `/portal` may indicate different handling.

Response differences are often more useful than the status code alone.

---

# 58. Compare Responses

For interesting endpoints, manually compare:

```bash
curl -ski https://example.com/admin
```

and:

```bash
curl -ski https://example.com/random-does-not-exist
```

Compare:

```text
Status
Headers
Content-Type
Content-Length
Body
Redirect
Cookies
```

This helps distinguish genuine discoveries from generic application behaviour.

---

# 59. Wildcard Responses

Some applications return the same response for almost every path.

For example:

```text
/abc123     -> 200
/random999  -> 200
/admin      -> 200
/api        -> 200
```

This often occurs with Single Page Applications.

The frontend may return the same HTML shell for every route.

In this situation:

```text
Status Code
```

alone is not useful.

Compare:

* Response length
* Body hash
* Page title
* JavaScript behaviour
* Browser rendering
* API responses

---

# 60. Single Page Applications

Applications built with frameworks such as React, Angular or Vue may use client-side routing.

The web server may return:

```text
index.html
```

for almost every path.

For example:

```text
/admin
/random
/does-not-exist
```

could all return the same frontend application.

This is why technology identification should occur before interpreting content discovery results.

---

# 61. Interesting Content Categories

Useful discoveries can be grouped into categories.

## Administrative

```text
/admin
/manage
/console
/dashboard
```

## API

```text
/api
/api/v1
/graphql
/swagger
```

## Authentication

```text
/login
/logout
/register
/reset
/oauth
/sso
```

## Development

```text
/dev
/test
/debug
/staging
```

## Files

```text
/upload
/uploads
/download
/files
/documents
```

## Monitoring

```text
/status
/health
/metrics
```

## Legacy

```text
/old
/legacy
/v1
/backup
```

Categorising results helps determine what to investigate next.

---

# 62. Prioritise Discoveries

Not every discovered resource deserves equal attention.

A simple prioritisation model is:

```text
Discovered Endpoint
        |
        v
Authentication Required?
        |
        v
Sensitive Functionality?
        |
        v
User Input?
        |
        v
File / URL / Command Processing?
        |
        v
Administrative?
        |
        v
API?
        |
        v
Testing Priority
```

Examples of higher-priority functionality may include:

* Authentication
* Administration
* File uploads
* File downloads
* URL imports
* API endpoints
* Debug functionality
* Reporting
* Data exports
* Search
* Integrations

---

# 63. Content Discovery Does Not Equal Vulnerability

A discovered endpoint is not automatically a security finding.

For example:

```text
/admin
```

returning:

```text
403 Forbidden
```

may simply indicate correctly protected functionality.

The workflow should be:

```text
Endpoint Discovered
        |
        v
Manually Validate
        |
        v
Understand Function
        |
        v
Determine Access Control
        |
        v
Security Testing
        |
        v
Finding / No Finding
```

Do not report the existence of a path as a vulnerability without security impact.

---

# 64. Practical ffuf Workflow

Start by understanding the baseline:

```bash
curl -ski \
  https://example.com/random-does-not-exist-12345
```

Then run directory discovery:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -mc all \
  -fc 404
```

If the application uses soft `404`s, use auto calibration:

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -ac
```

Then investigate interesting directories recursively.

For example:

```bash
ffuf \
  -u https://example.com/api/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -ac
```

---

# 65. Practical feroxbuster Workflow

A practical starting command is:

```bash
feroxbuster \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
```

With selected extensions:

```bash
feroxbuster \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -x php,json,txt,bak
```

Limit recursion when necessary:

```bash
feroxbuster \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -d 2
```

---

# 66. Practical dirsearch Workflow

Basic discovery:

```bash
dirsearch \
  -u https://example.com
```

With extensions:

```bash
dirsearch \
  -u https://example.com \
  -e php,html,js,json,txt,bak
```

With a SecLists wordlist:

```bash
dirsearch \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
```

---

# 67. Practical Reconnaissance Pipeline

Content discovery should consume information from earlier reconnaissance stages.

For example:

```text
Subdomain Enumeration
        |
        v
alive-hosts.txt
        |
        v
Technology Identification
        |
        v
Select Relevant Wordlists
        |
        v
Content Discovery
        |
        +---- ffuf
        |
        +---- feroxbuster
        |
        +---- dirsearch
        |
        v
Interesting Endpoints
        |
        v
Manual Validation
        |
        v
Crawling
        |
        v
Parameter Discovery
        |
        v
JavaScript Analysis
```

Each reconnaissance stage should improve the next one.

---

# 68. Recommended Output Structure

Keep discovery results organised.

For example:

```text
recon/
├── subdomains/
│   ├── subdomains.txt
│   ├── resolved-subdomains.txt
│   └── alive-hosts.txt
│
├── technology/
│   ├── httpx.txt
│   └── whatweb.txt
│
└── content/
    ├── ffuf/
    ├── feroxbuster/
    ├── dirsearch/
    ├── historical-urls.txt
    ├── interesting-endpoints.txt
    └── validated-endpoints.txt
```

For larger assessments, create separate directories for each hostname.

For example:

```text
content/
├── www.example.com/
├── api.example.com/
├── portal.example.com/
└── admin.example.com/
```

---

# 69. Record Interesting Endpoints

Maintain a simple list such as:

```text
/admin
/api
/api/v1
/login
/upload
/download
/swagger
/graphql
/debug
```

Or include additional context:

```text
/admin       302   -> /login
/api         200   application/json
/swagger     200   Swagger UI
/debug       403
/upload      200   Authenticated
```

This becomes useful input for subsequent testing.

---

# 70. Quick Reference

## robots.txt

```bash
curl -sk https://example.com/robots.txt
```

## sitemap.xml

```bash
curl -sk https://example.com/sitemap.xml
```

## security.txt

```bash
curl -sk https://example.com/.well-known/security.txt
```

## Random 404 Baseline

```bash
curl -ski \
  https://example.com/random-does-not-exist-12345
```

## ffuf Directory Discovery

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## ffuf with Auto Calibration

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -ac
```

## ffuf File Discovery

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
```

## ffuf Extensions

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -e .php,.json,.txt,.bak
```

## Filter 404

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -mc all \
  -fc 404
```

## Filter Response Size

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -fs 4242
```

## Save JSON Results

```bash
ffuf \
  -u https://example.com/FUZZ \
  -w wordlist.txt \
  -o ffuf-results.json \
  -of json
```

## feroxbuster

```bash
feroxbuster \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
```

## dirsearch

```bash
dirsearch \
  -u https://example.com \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
```

## Historical URLs

```bash
waybackurls example.com > historical-urls.txt
```

## gau

```bash
gau example.com > historical-urls.txt
```

## Virtual Host Discovery

```bash
ffuf \
  -u https://example.com/ \
  -H "Host: FUZZ.example.com" \
  -w wordlist.txt
```

---

# 71. Testing Checklist

During content discovery, ask:

```text
[ ] Did I check robots.txt?
[ ] Did I check sitemap.xml?
[ ] Did I check .well-known resources?
[ ] Did I inspect HTML?
[ ] Did I inspect JavaScript?
[ ] Did I establish the application's 404 baseline?
[ ] Did I identify soft 404 behaviour?
[ ] Did I choose a suitable wordlist?
[ ] Did I perform directory discovery?
[ ] Did I perform file discovery?
[ ] Did I use technology-specific extensions?
[ ] Did I investigate redirects?
[ ] Did I retain 401 and 403 results?
[ ] Did I investigate unusual response sizes?
[ ] Did I recurse into interesting directories?
[ ] Did I check API documentation?
[ ] Did I look for source maps?
[ ] Did I review historical URLs?
[ ] Did I build target-specific wordlists?
[ ] Did I repeat discovery after authentication?
[ ] Did I compare different user roles where available?
[ ] Did I manually validate interesting results?
```

---

# 72. Final Workflow

The complete process can be summarised as:

```text
                         Live Web Target
                                |
                                v
                      Manual Investigation
                                |
               +----------------+----------------+
               |                |                |
          robots.txt       sitemap.xml      JavaScript
               |                |                |
               +----------------+----------------+
                                |
                                v
                    Technology Identification
                                |
                                v
                       Wordlist Selection
                                |
             +------------------+------------------+
             |                  |                  |
            ffuf           feroxbuster         dirsearch
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                         Raw Discoveries
                                |
                +---------------+---------------+
                |               |               |
             Status           Size           Redirect
                |               |               |
                +---------------+---------------+
                                |
                                v
                         Remove Noise
                                |
                                v
                        Manual Validation
                                |
             +------------------+------------------+
             |                  |                  |
           Admin               API              Files
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                     Recursive Discovery
                                |
                                v
                      Expanded Attack Surface
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
         Parameter Discovery            JavaScript Analysis
```

The most important principle is:

```text
Do Not Fuzz Blindly
        |
        v
Understand the Target
        |
        v
Establish a Baseline
        |
        v
Choose Relevant Wordlists
        |
        v
Discover Content
        |
        v
Analyse Differences
        |
        v
Manually Validate
```

Content discovery is most effective when it is driven by information collected during the rest of reconnaissance.

---

## Related Notes

* [Reconnaissance Overview](index.md)
* [Subdomain Enumeration](subdomain-enumeration.md)
* [Technology Identification](technology-identification.md)
* [Parameter Discovery](parameter-discovery.md)
* [JavaScript Analysis](javascript-analysis.md)
* [Web Application Testing Methodology](../methodology.md)
* [Web Application Pentesting Checklist](../checklist.md)
