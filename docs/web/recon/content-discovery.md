# Content Discovery

Content discovery is the process of identifying hidden or unlinked resources within a web application.

Applications frequently expose endpoints that are not accessible through normal navigation. These may include administrative interfaces, API endpoints, backup files, configuration files, development resources, old application versions and forgotten functionality.

!!! warning "Authorised Security Testing"
    Perform content discovery only against systems for which you have explicit authorisation.

---

## Objectives

Content discovery attempts to identify resources such as:

```text
Directories
Files
API endpoints
Administrative interfaces
Backup files
Configuration files
Development environments
Documentation
Debug endpoints
Legacy applications
Source files
Temporary files
Exposed repositories
```

A typical workflow is:

```text
Application
    ↓
Manual Exploration
    ↓
robots.txt / sitemap.xml
    ↓
Historical URL Collection
    ↓
Directory Discovery
    ↓
File Discovery
    ↓
Extension Discovery
    ↓
Response Analysis
    ↓
Manual Verification
```

The objective is not simply to generate thousands of requests.

The objective is to identify **interesting application functionality that expands the attack surface**.

---

# Start Manually

Before running automated discovery tools, browse the application manually.

Review:

```text
Navigation
Links
Forms
JavaScript
API requests
Redirects
Static resources
Authentication flows
Error messages
```

Burp Suite's HTTP history and site map are particularly useful here.

A manually observed application might initially appear as:

```text
/
├── /login
├── /register
├── /account
└── /contact
```

Content discovery might later reveal:

```text
/
├── /login
├── /register
├── /account
├── /contact
├── /admin
├── /api
├── /swagger
├── /backup
├── /debug
└── /internal
```

The second view provides a much more complete picture of the application's attack surface.

---

# robots.txt

Always check:

```text
/robots.txt
```

Example:

```bash
curl https://target.example/robots.txt
```

A response might contain:

```text
User-agent: *
Disallow: /admin/
Disallow: /internal/
Disallow: /backup/
```

Although `robots.txt` is intended for web crawlers, it can provide useful reconnaissance information.

!!! note
    A `Disallow` entry is not an access control mechanism.

---

# sitemap.xml

Check:

```text
/sitemap.xml
```

Example:

```bash
curl https://target.example/sitemap.xml
```

Sitemaps may reveal:

```text
Application pages
Legacy endpoints
Product pages
Documentation
API routes
Unlinked content
```

Also consider:

```text
/sitemap_index.xml
/sitemap-index.xml
/sitemap1.xml
```

---

# security.txt

Check for:

```text
/.well-known/security.txt
/security.txt
```

Example:

```bash
curl https://target.example/.well-known/security.txt
```

This file may provide:

```text
Security contact
Responsible disclosure policy
Scope information
Acknowledgement pages
Security policy links
```

It is particularly useful during legitimate vulnerability research.

---

# Common Files

Some files are worth checking early because they may provide additional information about the application.

Examples:

```text
/robots.txt
/sitemap.xml
/.well-known/security.txt
/favicon.ico
/manifest.json
/asset-manifest.json
/README.md
```

Framework-specific resources can also be valuable.

For example:

```text
/_next/
/static/
/assets/
/swagger/
/api/
```

---

# Directory Discovery

Directory discovery attempts to identify resources that are not directly linked from the application.

Common tools include:

```text
ffuf
feroxbuster
dirsearch
gobuster
Burp Suite
```

Do not immediately use extremely large wordlists.

Start with a sensible list and expand only when necessary.

---

# FFUF

FFUF is a fast and flexible web fuzzer.

Basic directory discovery:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

The keyword:

```text
FUZZ
```

is replaced with entries from the wordlist.

Potential output:

```text
admin                   [Status: 302]
api                     [Status: 200]
backup                  [Status: 403]
internal                [Status: 403]
uploads                 [Status: 301]
```

These responses should then be manually investigated.

---

# FFUF Status Filtering

You can restrict interesting status codes:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -mc 200,204,301,302,307,401,403
```

Do not automatically discard:

```text
401
403
```

A `403 Forbidden` response can be extremely useful.

It confirms that something may exist at that location.

---

# Response Size Filtering

Applications frequently return custom error pages with HTTP 200 responses.

For example:

```text
/nonexistent123
```

might return:

```text
HTTP/1.1 200 OK
Content-Length: 4242
```

If every nonexistent resource returns the same size, filter it:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w wordlist.txt \
  -fs 4242
```

Useful FFUF filters include:

```text
-fs    Filter response size
-fw    Filter number of words
-fl    Filter number of lines
-fc    Filter status codes
```

This is often more reliable than filtering only by HTTP status.

---

# FFUF Auto Calibration

FFUF can automatically attempt to identify baseline responses:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w wordlist.txt \
  -ac
```

Auto calibration can help reduce false positives caused by wildcard responses.

However, always verify important results manually.

---

# Feroxbuster

Feroxbuster is particularly useful for recursive content discovery.

Basic usage:

```bash
feroxbuster \
  -u https://target.example
```

Specify a wordlist:

```bash
feroxbuster \
  -u https://target.example \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Feroxbuster can recursively discover directories.

For example:

```text
/admin
/admin/users
/admin/config
/admin/logs
```

This can reveal application structure that a single directory scan might miss.

---

# Feroxbuster Extensions

Search for specific file extensions:

```bash
feroxbuster \
  -u https://target.example \
  -x php,txt,json,xml,bak
```

Possible findings:

```text
config.php
users.json
backup.bak
settings.xml
debug.txt
```

---

# Dirsearch

Dirsearch is another useful content discovery tool.

Basic usage:

```bash
dirsearch \
  -u https://target.example
```

Specify extensions:

```bash
dirsearch \
  -u https://target.example \
  -e php,asp,aspx,jsp,json,txt,bak
```

Useful options include:

```text
-r    Recursive discovery
-x    Exclude status codes
-i    Include status codes
```

---

# Gobuster

Gobuster can also perform directory discovery:

```bash
gobuster dir \
  -u https://target.example \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

With extensions:

```bash
gobuster dir \
  -u https://target.example \
  -w wordlist.txt \
  -x php,txt,bak,json
```

---

# Wordlists

SecLists provides a large collection of useful discovery wordlists.

Common location on Kali Linux:

```text
/usr/share/seclists/
```

Useful directories include:

```text
Discovery/Web-Content/
Discovery/DNS/
Fuzzing/
Passwords/
Usernames/
```

For content discovery:

```text
/usr/share/seclists/Discovery/Web-Content/
```

Useful starting lists include:

```text
common.txt
raft-small-directories.txt
raft-medium-directories.txt
raft-small-files.txt
raft-medium-files.txt
directory-list-2.3-small.txt
directory-list-2.3-medium.txt
```

A practical approach is:

```text
Small list
   ↓
Review Results
   ↓
Medium list
   ↓
Technology-Specific Lists
   ↓
Target-Specific Discovery
```

Avoid blindly starting with the largest available wordlist.

---

# Technology-Specific Discovery

Technology identification should influence content discovery.

For example, if the application uses PHP:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w wordlist.txt \
  -e .php
```

For ASP.NET:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w wordlist.txt \
  -e .aspx,.ashx,.asmx
```

For Java:

```text
.jsp
.action
.do
```

For configuration-heavy applications:

```text
.json
.xml
.yml
.yaml
.conf
.config
```

Technology-aware discovery produces more relevant results.

---

# File Extension Discovery

Do not assume that all resources are extensionless.

Useful extensions include:

```text
.php
.asp
.aspx
.jsp
.do
.action
.json
.xml
.txt
.conf
.config
.yml
.yaml
.log
.bak
.old
.zip
.tar
.gz
```

Example:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w wordlist.txt \
  -e .php,.txt,.json,.xml,.bak,.old
```

---

# Backup Files

Backup files are particularly interesting because developers and administrators may accidentally leave them accessible.

Common patterns include:

```text
index.php.bak
index.php.old
index.php~
config.php.bak
web.config.old
application.zip
backup.zip
site.tar.gz
www.zip
```

Potentially interesting extensions:

```text
.bak
.backup
.old
.orig
.save
.tmp
~
.zip
.tar
.gz
```

If a legitimate application file is known:

```text
config.php
```

consider whether authorised testing permits checking common backup variants:

```text
config.php.bak
config.php.old
config.php~
```

---

# Configuration Files

Potential configuration resources include:

```text
.env
web.config
application.properties
application.yml
application.yaml
config.json
config.xml
settings.json
```

Configuration files can potentially expose:

```text
Application settings
Internal hostnames
API endpoints
Database configuration
Debug settings
Environment information
```

Any discovered sensitive information should be handled according to the assessment's rules of engagement.

---

# Git Repository Exposure

Check whether repository metadata has accidentally been published:

```text
/.git/
```

A simple request:

```bash
curl -I https://target.example/.git/HEAD
```

An exposed `.git` directory can potentially reveal application source code and repository history.

Also consider other version control artefacts:

```text
/.svn/
/.hg/
```

Do not download or reconstruct repositories unless this is permitted by the assessment scope.

---

# API Discovery

Look for common API paths:

```text
/api
/api/v1
/api/v2
/rest
/graphql
/swagger
/swagger-ui
/openapi.json
/api-docs
/v1
/v2
```

Example:

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w api-wordlist.txt
```

API documentation can significantly expand the visible attack surface.

---

# Swagger and OpenAPI

Common locations include:

```text
/swagger
/swagger-ui
/swagger-ui.html
/swagger.json
/openapi.json
/api-docs
/v2/api-docs
/v3/api-docs
```

If documentation is exposed, review:

```text
Endpoints
HTTP methods
Parameters
Request schemas
Authentication requirements
Administrative functionality
```

Documentation should be treated as an attack surface map.

---

# GraphQL

Common GraphQL locations include:

```text
/graphql
/graphiql
/api/graphql
```

Content discovery may identify GraphQL even when it is not linked from the main application.

Look for requests containing:

```text
query
mutation
__typename
```

JavaScript files may also disclose GraphQL endpoints.

---

# Administrative Interfaces

Look for administrative and management functionality.

Common patterns include:

```text
/admin
/administrator
/management
/manage
/console
/dashboard
/backend
/control
/panel
/internal
```

A `401`, `403` or redirect can still be a meaningful result.

For example:

```text
/admin       → 403
/management  → 401
/dashboard   → 302 /login
```

All three indicate potentially valid application functionality.

---

# Development and Debug Resources

Look for:

```text
/debug
/dev
/test
/testing
/staging
/internal
/console
/actuator
/metrics
/health
/status
```

Development functionality can expose significantly more information than production interfaces.

---

# Spring Boot Actuator

If Spring Boot is identified, common Actuator endpoints may include:

```text
/actuator
/actuator/health
/actuator/info
/actuator/env
/actuator/configprops
/actuator/mappings
/actuator/metrics
```

The exact exposed endpoints depend on application configuration and Spring Boot version.

Do not assume an endpoint is sensitive solely because it exists. Review the actual information exposed.

---

# Historical URLs

Current application navigation does not necessarily show everything that has existed historically.

Historical URL sources can reveal:

```text
Old endpoints
Deprecated APIs
Backup resources
Legacy applications
Old parameters
JavaScript files
Previous directories
```

Tools commonly used for this include:

```text
waybackurls
gau
urlfinder
```

---

# Waybackurls

Example:

```bash
echo target.example | waybackurls
```

Save results:

```bash
echo target.example | waybackurls > wayback.txt
```

Remove duplicates:

```bash
sort -u wayback.txt -o wayback.txt
```

Historical URLs can then be checked to determine whether they still exist.

---

# GAU

GetAllUrls can gather URLs from multiple public sources.

Example:

```bash
gau target.example
```

Save the results:

```bash
gau target.example > gau.txt
```

Then deduplicate:

```bash
sort -u gau.txt -o gau.txt
```

---

# URLFinder

URLFinder can also help discover URLs associated with a target.

Example:

```bash
urlfinder -d target.example
```

Save output:

```bash
urlfinder -d target.example -o urls.txt
```

Historical URL collection is particularly useful before parameter discovery.

---

# Combine URL Sources

Results from multiple sources can be combined:

```bash
cat wayback.txt gau.txt urlfinder.txt \
  | sort -u \
  > all-urls.txt
```

You can then inspect the discovered paths:

```bash
cat all-urls.txt
```

A large URL collection can reveal application functionality that normal crawling missed.

---

# Extract Unique Paths

If many URLs have been collected, extracting unique paths can make analysis easier.

For example:

```text
https://target.example/admin/users
https://target.example/api/v1/users
https://target.example/account/settings
```

can be reduced conceptually to:

```text
/admin/users
/api/v1/users
/account/settings
```

These paths can then inform further targeted discovery.

---

# JavaScript-Based Discovery

JavaScript often contains endpoints that directory brute forcing will never discover.

Look for:

```text
/api/users
/api/admin
/internal/status
/auth/refresh
/graphql
/upload
/download
```

Search downloaded JavaScript:

```bash
grep -RniE \
  '(/api/|/admin|/internal|/graphql|/upload|/download)' \
  javascript/
```

JavaScript analysis should therefore complement traditional directory discovery.

---

# Crawling

Crawlers discover linked content rather than guessing filenames.

Useful tools include:

```text
Katana
Burp Suite
Hakrawler
gospider
```

For example:

```bash
katana -u https://target.example
```

With greater depth:

```bash
katana \
  -u https://target.example \
  -d 3
```

Save results:

```bash
katana \
  -u https://target.example \
  -o katana.txt
```

Crawling and brute force discovery solve different problems:

```text
Crawler
   ↓
Discover linked resources

Wordlist Discovery
   ↓
Discover unlinked resources
```

Use both.

---

# Response Code Interpretation

HTTP status codes provide useful clues.

| Status | Interpretation |
|---|---|
| `200` | Resource likely accessible |
| `204` | Resource exists with no body |
| `301` | Permanent redirect |
| `302` | Temporary redirect |
| `307` | Redirect preserving method |
| `401` | Authentication required |
| `403` | Resource may exist but access denied |
| `404` | Resource likely unavailable |
| `405` | Endpoint may exist but method is incorrect |
| `500` | Application processed something unexpectedly |

Do not judge results solely by status code.

Compare:

```text
Status
Response size
Word count
Headers
Redirect destination
Response body
Timing
```

---

# 403 Responses

Do not automatically ignore `403 Forbidden`.

For example:

```text
/admin        403
/internal     403
/backup       403
```

These responses indicate potentially valid resources.

A useful workflow is:

```text
403 discovered
      ↓
Record endpoint
      ↓
Compare response fingerprint
      ↓
Determine expected access control
      ↓
Review application behaviour
      ↓
Continue testing within scope
```

The important finding may simply be that previously unknown functionality exists.

---

# 404 Fingerprinting

Not all `404` responses are identical.

Different application components may produce different error pages.

For example:

```text
/does-not-exist
```

might return an nginx 404 while:

```text
/api/does-not-exist
```

returns a JSON framework error.

This can indicate different backend components.

The 0xdf 404 cheatsheet is useful for recognising technology-specific error pages:

```text
https://0xdf.gitlab.io/cheatsheets/404
```

This can complement technology identification during content discovery.

---

# Baseline Responses

Before running large discovery scans, establish a baseline.

Request random nonexistent paths:

```bash
curl -i https://target.example/randomdoesnotexist12345
```

Then another:

```bash
curl -i https://target.example/randomdoesnotexist67890
```

Compare:

```text
Status
Content-Length
Body
Headers
Redirect
```

If both responses are identical, that response fingerprint can be filtered during discovery.

---

# Virtual Hosts

Sometimes content is separated by virtual host rather than path.

For example:

```text
www.target.example
admin.target.example
api.target.example
dev.target.example
```

Subdomain enumeration therefore complements directory discovery.

The complete attack surface is usually:

```text
Domains
   +
Subdomains
   +
Virtual Hosts
   +
Directories
   +
Files
   +
Parameters
   +
JavaScript Endpoints
   +
APIs
```

---

# Burp Suite Workflow

Burp Suite provides an excellent central location for reviewing discovered content.

Use:

```text
Proxy
→ HTTP history
```

and:

```text
Target
→ Site map
```

After automated discovery, send interesting endpoints through Burp for manual analysis.

Example:

```text
/admin
/api/v1/users
/swagger
/internal
/upload
```

Then investigate:

```text
Authentication
Authorisation
Parameters
Methods
Headers
Cookies
Input handling
Response behaviour
```

---

# Organising Discovery Results

Raw tool output quickly becomes difficult to manage.

Organise findings into categories:

```text
Application
├── Authentication
├── Administration
├── API
├── Upload
├── Download
├── Internal
├── Debug
├── Documentation
└── Static Resources
```

For example:

```text
Authentication
/login
/logout
/password-reset

Administration
/admin
/admin/users

API
/api/v1
/api/v1/users

Documentation
/swagger
/openapi.json
```

This turns content discovery into an actual application map.

---

# Prioritising Results

Not every discovered path deserves equal attention.

A useful priority order is:

```text
Administrative functionality
        ↓
Authentication endpoints
        ↓
API endpoints
        ↓
File upload/download
        ↓
Debug functionality
        ↓
Internal functionality
        ↓
Backup/configuration files
        ↓
Legacy functionality
        ↓
Static resources
```

Prioritisation should also consider the application's purpose and assessment scope.

---

# Practical Workflow

A practical content discovery workflow could be:

### 1. Manual browsing

Use:

```text
Browser
Burp Suite
Developer Tools
```

### 2. Check standard resources

```text
robots.txt
sitemap.xml
security.txt
```

### 3. Crawl

```bash
katana \
  -u https://target.example \
  -d 3 \
  -o katana.txt
```

### 4. Historical URLs

```bash
echo target.example | waybackurls > wayback.txt
```

```bash
gau target.example > gau.txt
```

### 5. Combine

```bash
cat katana.txt wayback.txt gau.txt \
  | sort -u \
  > discovered-urls.txt
```

### 6. Directory discovery

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt \
  -ac
```

### 7. File discovery

```bash
ffuf \
  -u https://target.example/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt \
  -e .php,.json,.xml,.txt,.bak,.old \
  -ac
```

### 8. Review JavaScript

Look for additional endpoints and API routes.

### 9. Manual verification

Send interesting findings through Burp Suite.

---

# Recording Results

Keep a structured record of discovered resources.

For example:

| Endpoint | Status | Type | Priority | Notes |
|---|---:|---|---|---|
| `/admin` | 302 | Administration | High | Redirects to login |
| `/api/v1` | 200 | API | High | API root |
| `/swagger` | 200 | Documentation | High | API documentation |
| `/internal` | 403 | Internal | High | Resource exists |
| `/assets` | 301 | Static | Low | Static files |
| `/health` | 200 | Monitoring | Medium | Health endpoint |

This provides a useful attack surface inventory for later testing.

---

# Checklist

```text
[ ] Browse application manually
[ ] Review Burp site map
[ ] Check robots.txt
[ ] Check sitemap.xml
[ ] Check security.txt
[ ] Establish baseline 404 response
[ ] Crawl application
[ ] Perform directory discovery
[ ] Perform file discovery
[ ] Test relevant extensions
[ ] Review 401 responses
[ ] Review 403 responses
[ ] Review unusual redirects
[ ] Search historical URLs
[ ] Review JavaScript endpoints
[ ] Look for APIs
[ ] Look for Swagger/OpenAPI
[ ] Look for GraphQL
[ ] Look for admin interfaces
[ ] Look for debug interfaces
[ ] Look for backup files
[ ] Look for configuration files
[ ] Check repository metadata
[ ] Record interesting endpoints
[ ] Manually verify findings
```

---

## Key Principle

Content discovery should not be treated as:

```text
Run directory scanner
        ↓
Save output
        ↓
Done
```

A better methodology is:

```text
Discover
   ↓
Classify
   ↓
Correlate
   ↓
Prioritise
   ↓
Verify
   ↓
Expand
```

Every interesting endpoint should answer a question:

> What does this resource tell me about the application, and what should I test next?

The end result of content discovery should therefore be an increasingly accurate **map of the application's attack surface**, not simply a large collection of URLs.
