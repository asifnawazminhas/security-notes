# Information Disclosure

Information disclosure occurs when an application unintentionally reveals information that should not be available to the current user or to an unauthenticated attacker.

The disclosed information may appear harmless when viewed in isolation, but it can provide valuable intelligence for further attacks.

Examples include:

```text
Software versions
Internal hostnames
Internal IP addresses
Directory paths
Source code
Configuration files
Credentials
API keys
Tokens
Database information
Stack traces
Debug information
User information
Administrative functionality
Cloud metadata
Backup files
Source maps
Git repositories
Environment variables
Internal URLs
Infrastructure details
```

Information disclosure is sometimes referred to as:

```text
Information leakage
Sensitive information exposure
Information exposure
Verbose error disclosure
Metadata leakage
```

A useful way to think about it is:

```text
Application
     ↓
Unexpected Information
     ↓
Attacker Learns Something
     ↓
Information Enables Further Testing
     ↓
Potential Attack Chain
```

!!! warning "Authorised Security Testing"
    Information disclosure testing should only be performed against systems included in the authorised assessment scope. Avoid accessing unnecessary personal or sensitive information. Stop once sufficient evidence has been collected.

---

# Why Information Disclosure Matters

Information disclosure is often underestimated because the disclosed information may not immediately provide direct compromise.

For example:

```text
Internal hostname
```

may initially appear low risk.

However:

```text
Internal Hostname
       ↓
Technology Identification
       ↓
Infrastructure Mapping
       ↓
Internal Endpoint Discovery
       ↓
Potential SSRF Target
```

Similarly:

```text
Framework Version
       ↓
Known Vulnerability Research
       ↓
Relevant CVE Identified
       ↓
Targeted Validation
```

Information disclosure therefore often supports other vulnerability classes.

---

# Information Disclosure Attack Surface

Information can leak through many locations:

```text
HTTP response headers
HTTP response bodies
Error messages
API responses
HTML comments
JavaScript files
Source maps
Configuration files
Backup files
Temporary files
Debug endpoints
Health endpoints
Monitoring endpoints
Log files
Git repositories
Directory listings
Robots.txt
Sitemap files
Authentication responses
GraphQL
Cloud metadata
File downloads
Uploaded files
Redirects
Cookies
TLS certificates
DNS
```

Do not limit testing to visible application pages.

---

# Information Disclosure Testing Workflow

A structured workflow can look like:

```text
Map Application
      ↓
Inspect Responses
      ↓
Inspect Headers
      ↓
Trigger Controlled Errors
      ↓
Review JavaScript
      ↓
Review Source Maps
      ↓
Search for Backup Files
      ↓
Check Debug Endpoints
      ↓
Check Metadata
      ↓
Review API Responses
      ↓
Search for Internal References
      ↓
Assess Sensitivity
      ↓
Determine Attack Value
      ↓
Report
```

The objective is not simply:

```text
Find information
```

but:

```text
Find information
      ↓
Understand why it should not be exposed
      ↓
Determine how it affects the attack surface
```

---

# Start With HTTP Responses

Every response may contain useful information.

Inspect:

```text
Status line
Response headers
Cookies
Response body
HTML comments
JavaScript references
Redirect locations
Error messages
```

For example:

```http
HTTP/1.1 200 OK
Server: nginx/1.18.0
X-Powered-By: Express
X-Backend-Server: app-prod-03.internal
```

This reveals several pieces of information.

---

# Server Headers

Common headers include:

```http
Server: Apache/2.4.49
```

```http
Server: nginx/1.18.0
```

```http
Server: Microsoft-IIS/10.0
```

These may disclose:

```text
Web server
Product
Version
Platform
```

A version number can assist with technology-specific vulnerability research.

However:

> A version disclosure alone does not prove that the disclosed software is vulnerable.

The actual deployed software, patches and configuration still need to be considered.

---

# X-Powered-By

Applications may return:

```http
X-Powered-By: PHP/8.1.2
```

or:

```http
X-Powered-By: Express
```

or framework-specific information.

This can assist technology identification.

Where there is no operational requirement to expose this information, unnecessary technology headers should generally be removed.

---

# Custom Headers

Do not inspect only standard headers.

Custom headers can reveal much more interesting information.

Examples:

```http
X-Backend: app-prod-02
X-Environment: production
X-Debug: true
X-Internal-IP: 10.20.30.40
X-Node: web03.internal
X-Request-ID: 123456
X-Cluster: prod-eu-west
```

Potential information includes:

```text
Environment names
Internal hosts
Infrastructure topology
Cluster names
Cloud regions
Backend identifiers
```

---

# Internal URL Disclosure

A particularly useful information disclosure occurs when the application exposes internal URLs.

Example:

```http
Location: http://internal-app:8080/login
```

or:

```json
{
    "service": "http://users-api.internal:9000"
}
```

or:

```text
http://10.20.30.40:8080/admin
```

This may reveal:

```text
Internal hostnames
Internal ports
Service names
Network architecture
Administrative interfaces
```

---

# Internal URL Attack Chain

An internal URL may become useful during SSRF testing.

For example:

```text
Information Disclosure
        ↓
http://admin.internal:8080
        ↓
SSRF Endpoint Found
        ↓
Internal URL Tested
        ↓
Internal Service Reached
```

Refer to:

[Server Side Request Forgery](ssrf.md)

---

# Internal IP Addresses

Look for private address ranges such as:

```text
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

Examples:

```text
10.10.20.15
172.16.50.12
192.168.1.25
```

Internal IP disclosure may help map backend infrastructure.

Do not automatically classify every private IP disclosure as high severity.

Assess how it contributes to realistic attack paths.

---

# Stack Traces

Verbose exceptions are a common source of information disclosure.

Example:

```text
java.lang.NullPointerException
    at com.example.account.UserService.getUser(UserService.java:142)
    at com.example.account.AccountController.profile(AccountController.java:87)
```

This may reveal:

```text
Programming language
Framework
Package structure
Class names
Methods
Source file names
Line numbers
Application architecture
```

---

# Stack Trace Example

A Python application might reveal:

```text
Traceback (most recent call last):
  File "/opt/app/api/users.py", line 83, in get_user
  File "/opt/app/database.py", line 42, in query
```

This exposes:

```text
/opt/app/
api/users.py
database.py
```

These paths can become useful during:

```text
Path traversal
File inclusion
Source code review
Configuration discovery
```

---

# Triggering Controlled Errors

Error handling can be tested by supplying controlled invalid input.

Examples include:

```text
Invalid identifier
Incorrect data type
Missing parameter
Malformed JSON
Unexpected HTTP method
Invalid encoding
Invalid date
Oversized numeric value
Unexpected enum value
```

The objective is to observe how the application handles errors.

Do not intentionally cause service instability.

---

# Example Type Error

Normal request:

```http
GET /api/user?id=123 HTTP/1.1
Host: target.example
```

Controlled malformed request:

```http
GET /api/user?id=test HTTP/1.1
Host: target.example
```

Possible verbose response:

```text
SQL conversion error:
Cannot convert varchar value 'test' to integer
```

This may reveal database behaviour.

---

# Database Errors

Database errors can disclose:

```text
Database technology
Table names
Column names
Queries
Schema information
Database users
Connection details
File paths
```

Examples of technology indicators include:

```text
MySQL
PostgreSQL
Microsoft SQL Server
Oracle
SQLite
MongoDB
```

Such information can significantly improve subsequent injection testing.

Refer to:

[SQL Injection](sql-injection.md)

and:

[NoSQL Injection](nosql-injection.md)

once the NoSQL page is added.

---

# SQL Query Disclosure

A verbose error might expose:

```sql
SELECT id, username, email
FROM users
WHERE id = ?
```

This reveals:

```text
Table name
Column names
Query structure
```

Even if injection is not possible, the application is exposing unnecessary implementation details.

---

# Filesystem Paths

Errors may disclose paths such as:

```text
/var/www/html/
/opt/application/
/srv/api/
/home/app/
/usr/local/tomcat/
C:\inetpub\wwwroot\
C:\Program Files\Application\
```

These can help with:

```text
Path traversal
File inclusion
File upload
Configuration discovery
Exploit development
```

---

# HTML Comments

Inspect page source for comments.

Example:

```html
<!-- TODO remove debug endpoint before production -->
```

or:

```html
<!-- admin panel moved to /management-console -->
```

or:

```html
<!-- API v2 available at /api/v2 -->
```

Comments can reveal functionality that is not linked through the visible interface.

---

# Developer Comments

Search for:

```text
TODO
FIXME
DEBUG
TEMP
REMOVE
PASSWORD
SECRET
TOKEN
ADMIN
INTERNAL
DEV
TEST
STAGING
```

These terms can help identify interesting developer artefacts.

---

# JavaScript Files

JavaScript is a major source of application intelligence.

Review JavaScript for:

```text
API endpoints
Internal routes
Feature flags
Environment names
Authentication flows
GraphQL endpoints
WebSocket endpoints
Hidden parameters
Administrative routes
Cloud resources
Third-party services
Source map references
```

Refer to:

[JavaScript Analysis](reconnaissance/javascript-analysis.md)

---

# Secrets in JavaScript

Search for patterns relating to:

```text
api_key
apikey
secret
token
authorization
bearer
password
client_secret
access_token
private_key
```

However:

> Not every value called `apiKey` is a secret.

Some browser-side API identifiers are intentionally public.

Determine whether the discovered value provides privileged access.

---

# Source Maps

Production JavaScript may reference source maps.

Example:

```javascript
//# sourceMappingURL=app.js.map
```

A source map may expose:

```text
Original source code
Directory structure
Source file names
Comments
Framework components
API logic
Routes
Developer information
```

---

# Source Map Discovery

If the application loads:

```text
/static/js/app.js
```

check whether:

```text
/static/js/app.js.map
```

exists.

Also inspect the end of JavaScript files for:

```text
sourceMappingURL
```

---

# Source Map Example

```text
app.min.js
    ↓
app.min.js.map
    ↓
Original Sources
    ↓
Authentication Logic
API Routes
Internal Components
```

Source maps can greatly improve application understanding.

---

# Source Maps and Secrets

Do not assume a source map is sensitive simply because it exists.

Assess whether it reveals:

```text
Private source code
Internal endpoints
Credentials
Secrets
Security logic
Unpublished functionality
```

The impact depends on the contents.

---

# Backup Files

Backup files are a common source of information disclosure.

Potential naming patterns include:

```text
index.php.bak
index.php.old
index.php~
config.php.bak
config.old
web.config.bak
application.yml.old
database.sql
backup.zip
site-backup.zip
www.zip
source.zip
```

---

# Common Backup Extensions

Potential extensions include:

```text
.bak
.old
.orig
.save
.tmp
.temp
.copy
.backup
~
.zip
.tar
.tar.gz
.gz
.7z
.rar
```

Testing should be targeted rather than blindly requesting huge filename lists.

---

# Backup Configuration Files

Interesting examples include:

```text
.env.bak
web.config.old
application.properties.bak
application.yml.old
config.php~
settings.py.bak
```

These files may contain:

```text
Database credentials
API credentials
Secret keys
Internal hosts
Cloud configuration
Application secrets
```

---

# Temporary Editor Files

Editors sometimes create files such as:

```text
file~
.file.swp
.file.swo
```

These can accidentally expose source or configuration data.

---

# .env Files

Environment files are particularly sensitive.

Potential path:

```text
/.env
```

Possible contents:

```text
DB_HOST=
DB_USERNAME=
DB_PASSWORD=
APP_SECRET=
API_KEY=
JWT_SECRET=
```

If exposed, collect only enough information to demonstrate the issue.

Avoid unnecessary use of discovered credentials unless explicitly authorised.

---

# Configuration Files

Potential configuration files include:

```text
.env
config.php
web.config
appsettings.json
application.properties
application.yml
settings.py
config.json
database.yml
composer.json
package.json
pom.xml
```

Some are intentionally public or non-sensitive.

Others can contain highly sensitive configuration.

---

# web.config

For ASP.NET applications:

```text
web.config
```

may contain:

```text
Connection strings
Authentication settings
Application configuration
Custom errors configuration
Secrets
```

Direct access should normally be prevented.

---

# appsettings.json

.NET applications commonly use:

```text
appsettings.json
```

Potential contents include:

```text
ConnectionStrings
Logging
Authentication
JWT configuration
API endpoints
Application settings
```

Production deployments should ensure sensitive configuration is not publicly accessible.

---

# application.properties

Java applications may use:

```text
application.properties
```

or:

```text
application.yml
```

Potential values include:

```text
Database configuration
Spring settings
Management endpoints
Credentials
Cloud configuration
Internal services
```

---

# Debug Endpoints

Applications and frameworks may expose debugging functionality.

Potential examples include:

```text
/debug
/debug/
_debug
/dev
/test
/status
/health
/metrics
/info
/config
/env
```

The exact endpoints depend on the technology.

---

# Spring Boot Actuator

Spring Boot applications may expose management endpoints under:

```text
/actuator
```

Potential endpoints include:

```text
/actuator/health
/actuator/info
/actuator/env
/actuator/configprops
/actuator/mappings
/actuator/beans
/actuator/metrics
/actuator/loggers
/actuator/threaddump
/actuator/heapdump
```

Exposure depends on:

```text
Spring Boot version
Configuration
Authentication
Network controls
Management endpoint configuration
```

---

# Actuator Testing

Start with:

```text
/actuator
```

and:

```text
/actuator/health
```

Determine which endpoints are intentionally exposed.

Do not automatically request sensitive endpoints such as heap dumps unless this is permitted by the assessment scope.

---

# Actuator Information Value

Potential information includes:

```text
Application configuration
Environment variables
Internal hostnames
Routes
Beans
Dependencies
Memory information
Thread information
Service names
```

Some endpoints can expose significantly more sensitive information than others.

---

# Heap Dumps

Heap dumps can contain:

```text
Session information
Credentials
Tokens
Secrets
Application data
Database information
User data
```

Downloading or analysing a production heap dump can expose large quantities of sensitive data.

Therefore:

> Do not retrieve heap dumps unless this level of testing is explicitly authorised and necessary.

A safer proof may be demonstrating that the sensitive endpoint is accessible.

---

# Thread Dumps

Thread dumps may reveal:

```text
Application paths
Class names
Package names
Internal service calls
Thread names
Technology stack
```

Their sensitivity is usually different from heap dumps but should still be assessed carefully.

---

# Debug Mode

Framework debug modes can expose extensive information.

Examples include:

```text
Stack traces
Source snippets
Environment configuration
Routes
Variables
Framework versions
Interactive debugging
```

Debug mode should generally not be enabled on production systems.

---

# PHP Information

Exposed:

```text
phpinfo()
```

output can reveal:

```text
PHP version
Loaded modules
Filesystem paths
Environment variables
Server configuration
Operating system
HTTP headers
Extension versions
```

Potential filenames include:

```text
phpinfo.php
info.php
test.php
```

Do not assume these names exist. Use technology and application context to guide testing.

---

# Directory Listing

A web server may expose directory contents.

Example:

```text
Index of /uploads/

document1.pdf
backup.zip
test.txt
old/
```

This can reveal files that are not linked through the application.

---

# Directory Listing Risks

Directory listing can expose:

```text
Uploaded files
Backup files
Temporary files
Source files
Logs
Configuration files
Old application versions
```

The severity depends on what is accessible.

---

# robots.txt

Review:

```text
/robots.txt
```

Example:

```text
User-agent: *
Disallow: /admin/
Disallow: /internal/
Disallow: /backup/
```

`robots.txt` is public by design.

Therefore:

> The existence of sensitive-looking paths in robots.txt is not itself a vulnerability.

Use the paths as reconnaissance leads and assess their actual accessibility.

---

# sitemap.xml

Review:

```text
/sitemap.xml
```

and sitemap indexes.

These may reveal:

```text
Unlinked pages
Legacy pages
Language variants
Administrative-looking routes
Application structure
```

Again, a sitemap is generally public by design.

The interesting question is what the discovered endpoints expose.

---

# Security.txt

Review:

```text
/.well-known/security.txt
```

This normally contains security contact information and disclosure policy details.

It is not an information disclosure vulnerability.

It can be useful for understanding the organisation's responsible disclosure process.

---

# Git Repository Exposure

Check whether development artefacts have accidentally been deployed.

A particularly important example is:

```text
/.git/
```

Potential files include:

```text
/.git/HEAD
/.git/config
/.git/index
```

---

# Git HEAD Test

A controlled request to:

```text
/.git/HEAD
```

may return:

```text
ref: refs/heads/main
```

This indicates that Git metadata may be publicly accessible.

---

# Why Exposed Git Is Dangerous

An exposed repository may reveal:

```text
Application source code
Commit history
Deleted secrets
Configuration
Credentials
Internal endpoints
Developer names
Historical vulnerabilities
```

The repository history can sometimes be more sensitive than the current application source.

---

# SVN and Other VCS Metadata

Other development artefacts may include:

```text
/.svn/
/.hg/
/.bzr/
```

Modern applications are most commonly affected by accidental Git exposure, but other version control metadata may still appear.

---

# API Responses

APIs frequently disclose more information than the frontend displays.

Example:

```json
{
    "id": 42,
    "username": "test",
    "email": "test@example.com",
    "role": "user",
    "internalUserId": "USR-48392",
    "isAdmin": false,
    "lastLoginIp": "10.20.30.40"
}
```

The frontend may only display:

```text
username
email
```

while the API returns additional fields.

---

# Excessive Data Exposure

Ask:

```text
Does the client actually require every field returned?
```

Potential unnecessary fields include:

```text
Internal identifiers
User roles
Email addresses
Phone numbers
IP addresses
Administrative flags
Backend references
Debug values
Internal timestamps
```

This overlaps with API security testing.

Refer to:

[API Security](api-security.md)

---

# API Error Messages

Malformed API requests may reveal:

```text
Object names
Class names
Validation framework
Database schema
Internal paths
Backend services
```

Example:

```json
{
    "error": "Cannot deserialize instance of com.example.UserRequest"
}
```

This reveals a Java class name and package structure.

---

# GraphQL

GraphQL can expose substantial schema information.

Potential endpoint:

```text
/graphql
```

GraphQL introspection may reveal:

```text
Types
Queries
Mutations
Fields
Arguments
Application structure
```

Whether introspection is considered a vulnerability depends on the application's threat model and what it exposes.

A dedicated GraphQL page will be added at:

[GraphQL API Security](graphql.md)

---

# Authentication Responses

Authentication functionality can leak information through different responses.

Example:

```text
Username does not exist
```

versus:

```text
Incorrect password
```

This may allow username enumeration.

---

# Username Enumeration

Compare:

```text
Status code
Response body
Response length
Response time
Headers
Redirect behaviour
```

For example:

```text
Existing user:
Incorrect password

Non-existing user:
Account does not exist
```

This reveals account validity.

Refer to:

[Authentication Testing](authentication.md)

---

# Password Reset

Password reset functionality may disclose:

```text
Whether account exists
Email address fragments
Phone number fragments
Identity provider
Account type
Organisation
```

Example:

```text
Password reset email sent to a***@example.com
```

Assess whether this information meaningfully assists account enumeration.

---

# Authorisation Errors

Access control failures can also disclose information.

For example:

```http
HTTP/1.1 403 Forbidden
```

with:

```json
{
    "error": "User 1023 does not have permission to access invoice 8821 owned by user 402"
}
```

This reveals object and user identifiers even though access is denied.

Refer to:

[Authorisation Testing](authorisation.md)

---

# Cookies

Review cookies for unnecessary information.

Example:

```http
Set-Cookie: role=administrator
```

or:

```http
Set-Cookie: username=john.smith
```

or encoded values containing application state.

Cookies should not expose unnecessary sensitive information.

Do not assume an encoded value is encrypted.

---

# Base64

Values such as:

```text
dXNlcj10ZXN0JnJvbGU9YWRtaW4=
```

may simply be Base64 encoded.

Base64 is not encryption.

Decode suspicious values during authorised testing to understand their contents.

---

# JWTs

JSON Web Tokens often intentionally contain readable claims.

A JWT payload may contain:

```json
{
    "sub": "12345",
    "role": "user",
    "email": "test@example.com"
}
```

JWT payloads are generally encoded, not encrypted.

Do not place unnecessary sensitive information in readable token claims.

Refer to:

```text
docs/web/jwt.md
```

---

# File Downloads

Downloaded documents can contain metadata.

Examples:

```text
PDF author
Document creator
Organisation
Username
Software version
Creation path
Revision history
Comments
```

This can reveal internal information.

---

# PDF Metadata

A PDF may contain metadata such as:

```text
Author: John Smith
Creator: Microsoft Word
Producer: Adobe PDF Library
Company: Example Corporation
```

Whether this is sensitive depends on context.

---

# Office Documents

Office documents can contain:

```text
Author names
Company names
Template paths
Revision information
Comments
Hidden sheets
Hidden content
Document properties
```

Documents intended for public distribution should be reviewed before publication.

---

# Image Metadata

Images may contain metadata such as:

```text
Camera model
Creation software
Timestamp
GPS information
Author
Comments
```

Publicly uploaded images should be assessed for unnecessary metadata exposure.

---

# File Names

File names themselves may disclose information.

Examples:

```text
internal-audit-2026.pdf
customer-export.csv
production-backup.zip
password-reset-test.xlsx
```

File naming should not reveal sensitive operational information where unnecessary.

---

# Cloud Storage

Applications may reveal storage locations such as:

```text
Amazon S3 bucket names
Azure Blob Storage containers
Google Cloud Storage buckets
CDN origins
```

Example:

```text
https://company-production-backups.s3.amazonaws.com/
```

The bucket name alone may not be a vulnerability.

Determine whether:

```text
Listing is enabled
Files are public
Sensitive objects are accessible
Write access exists
```

---

# Cloud Metadata

SSRF vulnerabilities may expose cloud instance metadata.

Conceptually:

```text
SSRF
  ↓
Cloud Metadata Service
  ↓
Instance Information
  ↓
Potential Credentials
```

This should be treated as an SSRF attack chain rather than generic information disclosure alone.

Refer to:

[Server Side Request Forgery](ssrf.md)

---

# DNS Information

DNS can reveal:

```text
Subdomains
Mail infrastructure
Cloud providers
Development environments
Internal naming conventions
Third-party services
```

Examples:

```text
dev.example.com
staging.example.com
vpn.example.com
api.example.com
admin.example.com
```

DNS information is often public by design.

The security value comes from how it expands the attack surface.

---

# TLS Certificates

Certificates may reveal:

```text
Hostnames
Subdomains
Organisation names
Service names
```

Certificate Transparency data can be useful during reconnaissance.

Refer to:

[Subdomain Enumeration](reconnaissance/subdomain-enumeration.md)

---

# Technology Version Disclosure

Technology versions may appear in:

```text
Headers
HTML
JavaScript
Error messages
Comments
Package files
Static assets
Debug pages
```

Examples:

```text
Angular 17.3.12
jQuery 3.4.1
Apache 2.4.x
nginx 1.18.x
Spring Boot
Next.js
```

Version identification should lead to:

```text
Technology
     ↓
Version
     ↓
Security Advisories
     ↓
Relevant CVEs
     ↓
Configuration Requirements
     ↓
Controlled Validation
```

Do not assume that version identification proves vulnerability.

---

# Dependency Disclosure

Files such as:

```text
package.json
package-lock.json
composer.json
composer.lock
pom.xml
requirements.txt
Gemfile.lock
```

can expose dependency versions.

This may make vulnerability research significantly easier.

---

# Package Lock Files

A lock file can provide exact versions.

For example:

```text
package-lock.json
```

may reveal the complete JavaScript dependency tree.

If accidentally exposed, assess whether this creates meaningful security impact.

---

# Swagger and OpenAPI

Applications may expose API documentation through endpoints such as:

```text
/swagger
/swagger-ui
/swagger-ui.html
/api-docs
/v3/api-docs
/openapi.json
swagger.json
```

These can reveal:

```text
API endpoints
Parameters
Schemas
Authentication requirements
Administrative operations
Hidden functionality
```

---

# Is Swagger a Vulnerability?

Not necessarily.

Some APIs intentionally provide public documentation.

The important questions are:

```text
Was it intended to be public?
Does it expose internal-only endpoints?
Does it expose sensitive schemas?
Does it reveal administrative functionality?
Does it materially expand the attack surface?
```

---

# Health Endpoints

Potential paths include:

```text
/health
/healthz
/status
/ready
/readiness
/liveness
```

A secure health endpoint may simply return:

```json
{
    "status": "UP"
}
```

A verbose endpoint might reveal:

```json
{
    "database": "db-prod-03.internal",
    "redis": "10.20.30.12:6379",
    "queue": "rabbitmq.internal",
    "status": "UP"
}
```

The second response exposes infrastructure information.

---

# Metrics Endpoints

Potential endpoints include:

```text
/metrics
/prometheus
/actuator/metrics
/actuator/prometheus
```

Metrics can expose:

```text
Service names
Routes
Hostnames
Performance data
Application internals
Library information
Environment labels
```

Access should reflect the sensitivity of the information.

---

# Prometheus Metrics

Prometheus-style metrics may contain labels such as:

```text
instance=
job=
service=
namespace=
pod=
host=
```

These can reveal infrastructure topology.

---

# Kubernetes Information

Application responses may leak Kubernetes-related information such as:

```text
Pod names
Namespaces
Service names
Cluster domains
Node names
Container names
```

Examples:

```text
users-api-7f8d9c6d5b-x2abc
production
users-api.default.svc.cluster.local
```

These can help map containerised infrastructure.

---

# Container Information

Error messages may reveal paths such as:

```text
/app/
/usr/src/app/
/workspace/
```

or container identifiers.

Again, determine whether the information meaningfully assists an attack.

---

# Hostname Disclosure

A response may expose:

```text
web-prod-01
api-node-04
app-eu-west-2
```

This can reveal:

```text
Environment
Role
Region
Architecture
Naming convention
```

A single hostname may be low impact, but multiple disclosures can provide an infrastructure map.

---

# Environment Names

Look for:

```text
dev
development
test
testing
qa
uat
stage
staging
preprod
prod
production
```

These may appear in:

```text
URLs
Headers
JavaScript
Configuration
Cookies
API responses
```

---

# Internal Email Addresses

Applications may disclose internal addresses such as:

```text
developer@example.com
admin@example.com
security@example.com
support@example.com
```

Public support addresses are normally intentional.

Developer or employee addresses exposed through debug output may not be.

Assess context.

---

# Source Code Disclosure

Source code disclosure is significantly more serious than simple technology disclosure.

Potential causes include:

```text
Backup files
Misconfigured web server
Exposed Git repository
Source maps
Path traversal
File inclusion
Debug functionality
Download endpoints
```

Source code can reveal:

```text
Authentication logic
Authorisation logic
Credentials
Secrets
Database queries
Internal APIs
Cryptographic implementation
Hidden functionality
Vulnerable code paths
```

---

# Source Code Review After Disclosure

Where authorised, disclosed source can be reviewed for:

```text
Routes
Authentication
Authorisation
User-controlled input
Sources
Sinks
File operations
Command execution
Template rendering
Deserialization
Database queries
SSRF sinks
Secrets
```

This can transition from black-box testing toward source-assisted vulnerability research.

---

# Secrets

Potential secrets include:

```text
Passwords
API keys
Client secrets
Private keys
Database credentials
JWT signing secrets
Cloud credentials
Access tokens
Refresh tokens
Webhook secrets
Encryption keys
```

If a secret is discovered:

```text
Record minimum evidence
      ↓
Determine likely purpose
      ↓
Avoid unnecessary use
      ↓
Confirm scope before validation
      ↓
Report securely
```

---

# Private Keys

A private key may appear as:

```text
-----BEGIN PRIVATE KEY-----
```

or:

```text
-----BEGIN RSA PRIVATE KEY-----
```

Do not reproduce full private keys in reports, screenshots or notes unless absolutely necessary.

Redact sensitive portions.

---

# API Keys

An API key should be assessed based on:

```text
Provider
Permissions
Environment
Restrictions
Expiration
Accessible functionality
```

Do not automatically use discovered credentials against third-party services.

Third-party infrastructure may fall outside the assessment scope.

---

# Error Handling Testing

Test how the application responds to:

```text
Invalid path
Invalid parameter
Missing parameter
Wrong method
Malformed JSON
Malformed XML
Incorrect Content-Type
Invalid object ID
Invalid encoding
Unexpected characters
```

Look for differences in:

```text
Status
Headers
Body
Length
Timing
Redirects
```

---

# 404 Responses

Custom 404 pages may leak:

```text
Framework
Server
Internal path
Routing logic
Backend host
Stack trace
```

Compare:

```text
Known path
Unknown path
Malformed path
```

---

# 403 Responses

403 responses can sometimes reveal:

```text
Resource existence
Authorisation model
Object identifiers
Administrative routes
Backend product
```

For example:

```text
You do not have permission to access /internal/admin-console
```

confirms that the resource exists.

---

# 500 Responses

500 responses are particularly interesting because exception handlers may expose verbose debugging information.

Do not intentionally create resource-intensive errors.

Use small controlled malformed requests.

---

# Different Content Types

Test error handling across:

```text
application/json
application/xml
application/x-www-form-urlencoded
multipart/form-data
text/plain
```

Different parsers may expose different error information.

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
Review Responses
  ↓
Search Interesting Keywords
  ↓
Send Interesting Requests to Repeater
  ↓
Trigger Controlled Errors
  ↓
Compare Responses
  ↓
Inspect JavaScript
  ↓
Inspect APIs
  ↓
Document Disclosures
```

---

# Burp Search

Useful search terms include:

```text
password
passwd
secret
token
api_key
apikey
authorization
bearer
internal
localhost
127.0.0.1
10.
172.16
192.168
debug
stack
exception
error
trace
database
jdbc
mongodb
redis
admin
staging
production
```

Treat matches as leads requiring context.

---

# Burp Logger

Burp's HTTP history and logging functionality can help identify information that appears only occasionally.

For example:

```text
Error responses
Redirects
API calls
Background requests
JavaScript requests
WebSocket handshakes
```

Review traffic rather than focusing only on pages visible in the browser.

---

# Burp Comparer

Comparer can help identify subtle differences between responses.

Useful for:

```text
Username enumeration
Resource enumeration
Error handling
Role-based differences
Authenticated vs unauthenticated responses
```

---

# Burp Repeater

Repeater is useful for controlled error testing.

Example workflow:

```text
Normal Request
      ↓
Send to Repeater
      ↓
Change One Input
      ↓
Send
      ↓
Compare Response
```

Change one variable at a time where possible.

---

# Content Discovery

Information disclosure often depends on discovering forgotten files or endpoints.

Useful categories include:

```text
Backup files
Configuration files
Documentation
Debug endpoints
Health endpoints
Source maps
Old versions
API documentation
Version control metadata
```

Refer to:

[Content Discovery](reconnaissance/content-discovery.md)

---

# Information Disclosure and Business Logic

Information can be sensitive because of the application's business context.

For example:

```text
E-commerce
```

might expose:

```text
Internal wholesale prices
Discount rules
Supplier identifiers
Inventory thresholds
```

A banking application might expose:

```text
Internal transaction references
Risk scores
Fraud flags
Approval states
```

A recruitment system might expose:

```text
Internal candidate scores
Reviewer comments
Hidden workflow states
```

Therefore:

> Information disclosure testing should follow the application's business logic, not only technical metadata.

---

# Role-Based Information Disclosure

Compare application behaviour between roles.

Example:

```text
Anonymous
   ↓
User
   ↓
Manager
   ↓
Administrator
```

Look for information exposed to lower-privileged users that is only required by higher-privileged roles.

---

# Horizontal Information Disclosure

A user may be able to access another user's information.

Example:

```text
/api/users/1001
```

versus:

```text
/api/users/1002
```

This is primarily an access control vulnerability rather than generic information disclosure.

Report according to the root cause.

Refer to:

[Authorisation Testing](authorisation.md)

---

# Vertical Information Disclosure

A normal user may receive information intended only for administrators.

Example:

```json
{
    "username": "test",
    "internalRiskScore": 92,
    "adminNotes": "Review manually"
}
```

Again, this may represent an authorisation problem if access restrictions are missing.

---

# Information Disclosure Chains

Information disclosure becomes particularly valuable when chained.

Example:

```text
Verbose Error
    ↓
Internal Path
    ↓
Path Traversal
    ↓
Configuration File
    ↓
Database Credentials
```

Another:

```text
JavaScript
    ↓
Internal API Endpoint
    ↓
SSRF
    ↓
Internal API Reached
```

Another:

```text
Server Version
    ↓
Known CVE
    ↓
Controlled Validation
    ↓
Confirmed Vulnerability
```

Another:

```text
Source Map
    ↓
Hidden API Route
    ↓
Authorisation Testing
    ↓
IDOR
```

---

# Information Disclosure Severity

Severity depends on what is disclosed.

A useful conceptual scale is:

```text
Low
 ↓
Technology name

Low / Medium
 ↓
Exact versions
Internal paths
Internal hostnames

Medium
 ↓
Source code
Internal architecture
User information

High
 ↓
Credentials
Tokens
Private keys
Sensitive personal information

Critical Potential
 ↓
Highly privileged reusable credentials
or secrets enabling major compromise
```

This is only a general guide.

Context determines actual severity.

---

# Do Not Overstate Version Disclosure

Example:

```http
Server: nginx/1.18.0
```

does not mean:

```text
Server is vulnerable to every nginx 1.18.0 CVE
```

Backported security patches and vendor packages can retain older-looking version strings.

Report what is actually demonstrated.

---

# Do Not Overstate Internal IP Disclosure

Example:

```text
10.20.30.40
```

may provide reconnaissance value but does not automatically create direct compromise.

A stronger finding demonstrates how the information contributes to an attack path.

---

# Do Not Overstate Public Information

Information already intentionally public should not be reported as sensitive disclosure.

Examples may include:

```text
Public support email
Public API documentation
Public product information
Public security.txt
Public certificate information
```

Always establish the intended confidentiality of the information.

---

# Information Disclosure Testing Matrix

| Source | Example | Sensitive? | Attack Value | Finding? |
|---|---|---:|---:|---:|
| Header | nginx version | Low | Recon | Depends |
| Header | Internal hostname | Medium | Internal mapping | Possibly |
| Error | Stack trace | Medium | Architecture | Yes |
| API | Other user's data | High | Direct exposure | Yes |
| File | `.env` | High | Credentials | Yes |
| File | Source map | Depends | Source review | Depends |
| Git | Repository | High | Source/history | Yes |
| Debug | Environment variables | High | Secrets/config | Yes |
| Health | `{"status":"UP"}` | Low | Minimal | Usually no |

---

# Information Disclosure Checklist

## HTTP

```text
[ ] Inspect Server header
[ ] Inspect X-Powered-By
[ ] Inspect custom headers
[ ] Inspect redirects
[ ] Inspect cookies
[ ] Inspect error responses
[ ] Inspect authentication responses
```

## Application

```text
[ ] Review HTML comments
[ ] Review JavaScript
[ ] Review source maps
[ ] Review API responses
[ ] Review hidden fields
[ ] Review client-side configuration
```

## Files

```text
[ ] Check backup files
[ ] Check temporary files
[ ] Check configuration files
[ ] Check environment files
[ ] Check version control metadata
[ ] Check source archives
```

## Debugging

```text
[ ] Check debug endpoints
[ ] Check health endpoints
[ ] Check metrics
[ ] Check framework management endpoints
[ ] Check verbose exceptions
[ ] Check stack traces
```

## API

```text
[ ] Check excessive response fields
[ ] Check unauthenticated responses
[ ] Check role differences
[ ] Check error messages
[ ] Check API documentation
[ ] Check GraphQL exposure
```

## Infrastructure

```text
[ ] Check internal hostnames
[ ] Check internal IPs
[ ] Check cloud references
[ ] Check container names
[ ] Check Kubernetes names
[ ] Check environment names
```

## Documents

```text
[ ] Review PDF metadata
[ ] Review Office metadata
[ ] Review image metadata
[ ] Review file names
[ ] Review downloadable archives
```

## Impact

```text
[ ] Determine confidentiality requirement
[ ] Determine affected user
[ ] Determine affected role
[ ] Determine attack value
[ ] Identify possible chains
[ ] Avoid unnecessary sensitive data collection
```

---

# Information Disclosure Decision Tree

```text
Information Found
       ↓
Was It Intended to Be Public?
       ↓
      YES
       ↓
Usually Not a Finding

       OR

      NO
       ↓
Is It Sensitive?
       ↓
      NO
       ↓
Does It Materially Assist an Attack?
       ↓
      NO
       ↓
Low / Informational

       OR

      YES
       ↓
What Does It Reveal?
       ↓
┌──────────────┬───────────────┬──────────────┐
↓              ↓               ↓              ↓
Technology   Internal       User Data       Secrets
Details      Infrastructure
↓              ↓               ↓              ↓
Assess       Assess          Assess          High
Recon Value  Attack Chain    Confidentiality Potential
       ↓
Can It Be Chained?
       ↓
Document
       ↓
Report According to Actual Impact
```

---

# Quick Reference

```text
HEADERS

Server
X-Powered-By
X-Backend
X-Environment
Location
Set-Cookie
```

```text
FILES

.env
.git/
*.bak
*.old
*.zip
*.map
web.config
appsettings.json
application.properties
application.yml
```

```text
DEBUG

/debug
/health
/status
/metrics
/actuator
/swagger
/api-docs
```

```text
SEARCH TERMS

password
secret
token
apikey
internal
localhost
debug
exception
trace
database
admin
staging
production
```

```text
HIGH-VALUE DISCLOSURE

Credentials
Tokens
Private keys
Source code
Configuration
User information
Internal architecture
```

---

# Evidence Collection

For a confirmed information disclosure finding, record:

```text
Affected URL
HTTP method
Authentication state
Affected user role
Request
Response
Information disclosed
Why information is sensitive
Potential attack value
Screenshots
Relevant attack chain
```

Redact:

```text
Passwords
Tokens
Private keys
Personal information
Session identifiers
```

where appropriate.

---

# Example Finding: Internal URL Disclosure

```text
Finding:
Internal Backend URL Disclosed in HTTP Response

Affected Endpoint:
/api/config

Observed:
The application response disclosed an internal backend service URL:

http://users-api.internal:8080

Impact:
The disclosure provides information about internal service naming and network architecture. This information could assist an attacker when testing vulnerabilities capable of accessing internal services, such as Server-Side Request Forgery.

Recommendation:
Avoid returning internal infrastructure references to untrusted clients. Where internal URLs are required for backend processing, translate them to appropriate external references before constructing client-facing responses.
```

---

# Example Finding: Verbose Error

```text
Finding:
Verbose Application Errors Disclose Internal Implementation Details

Affected Endpoint:
/api/users

Observed:
Supplying an invalid identifier caused the application to return a detailed exception containing internal package names, source file paths and database-related information.

Impact:
The disclosed information provides unnecessary insight into the application's internal implementation and can assist targeted vulnerability research.

Recommendation:
Return generic error responses to clients while recording detailed diagnostic information only in appropriately protected server-side logging systems.
```

---

# Example Finding: Source Map

```text
Finding:
Production JavaScript Source Map Publicly Accessible

Affected Resource:
/static/js/app.js.map

Observed:
The production source map was publicly accessible and contained original application source files and internal API route information.

Impact:
The source map significantly reduces the effort required to understand the application's internal client-side architecture and reveals functionality that is not apparent from the production bundle.

Recommendation:
If production source maps are not required by clients, prevent public access to them. Where source maps are required for monitoring, use a deployment process that uploads them directly to the authorised monitoring platform rather than serving them publicly.
```

---

# Example Finding: Exposed Environment File

```text
Finding:
Environment Configuration File Publicly Accessible

Affected Resource:
/.env

Observed:
The web server returned the application's environment configuration file without authentication.

The file contained application configuration and sensitive credentials.

Impact:
Exposure of environment configuration can reveal credentials, secrets and internal service information that may enable further compromise.

Recommendation:
Prevent web access to environment and configuration files. Store secrets outside the publicly served web root and rotate any credentials that have been exposed.
```

---

# Example Finding: Excessive API Data

```text
Finding:
API Response Exposes Unnecessary Internal Account Information

Affected Endpoint:
/api/profile

Observed:
The profile API returned internal account attributes that were not used or displayed by the client application.

The response included internal workflow and account-management fields.

Impact:
The unnecessary information reveals implementation details and internal account state to users who do not require it.

Recommendation:
Return only the minimum fields required by the client and apply response schemas appropriate to the requesting user's role.
```

---

# Example Informational Observation

```text
Observation:
Web Server Version Disclosed

Observed:
HTTP responses disclose the web server product and version through the Server response header.

Impact:
The information can assist technology fingerprinting but no vulnerability associated with the disclosed version was demonstrated.

Recommendation:
Where operationally feasible, minimise unnecessary version information returned to unauthenticated clients.
```

This is preferable to exaggerating a version banner as a direct compromise.

---

# Reporting Titles

Useful titles include:

```text
Internal Backend URL Disclosed in API Response

Verbose Error Messages Reveal Internal Application Details

Production Source Maps Expose Application Source Code

Environment Configuration File Publicly Accessible

Exposed Git Repository Allows Source Code Disclosure

API Response Exposes Unnecessary Internal User Information

Debug Endpoint Exposes Application Configuration

Internal Hostnames Disclosed Through Response Headers

Application Stack Trace Exposes Filesystem Paths

Sensitive Metadata Exposed in Public Documents
```

Prefer describing the actual disclosure rather than simply:

```text
Information Disclosure
```

---

# Remediation

Information disclosure should be addressed according to the source of the leak.

General principles include:

```text
Minimise client-facing information
Disable production debugging
Use generic error messages
Protect management endpoints
Remove unnecessary headers
Prevent access to configuration files
Prevent access to version control metadata
Remove backup files from web roots
Disable unnecessary directory listings
Limit API response fields
Remove secrets from client-side code
Protect source maps
Sanitise document metadata
Restrict health and metrics endpoints
```

---

# Secure Error Handling

Clients should receive messages such as:

```json
{
    "error": "Unable to process request"
}
```

Detailed diagnostics should be written to protected server-side logging systems.

Do not expose:

```text
Stack traces
Database queries
Filesystem paths
Credentials
Internal hostnames
```

to ordinary clients.

---

# Production Debugging

Ensure production environments do not expose:

```text
Debug mode
Interactive debugger
Verbose exception pages
Development middleware
Diagnostic consoles
```

Debug information should be accessible only through authorised operational tooling.

---

# Configuration Protection

Sensitive configuration should:

```text
Remain outside public web roots
Use appropriate filesystem permissions
Use secrets management where appropriate
Never be committed unnecessarily
Never be included in public artefacts
```

---

# API Response Minimisation

Instead of:

```json
{
    "id": 42,
    "username": "test",
    "email": "test@example.com",
    "internalRiskScore": 87,
    "databaseId": 8391,
    "supportFlag": true,
    "adminNotes": null
}
```

return only what the client requires:

```json
{
    "username": "test",
    "email": "test@example.com"
}
```

---

# Source Map Protection

If source maps are required for error monitoring:

```text
Build Application
      ↓
Generate Source Maps
      ↓
Upload to Monitoring Platform
      ↓
Do Not Publish Publicly
```

where technically appropriate.

---

# Secret Rotation

If a credential or secret has been exposed, simply removing the file may not be sufficient.

Consider:

```text
Remove exposure
      ↓
Rotate Secret
      ↓
Invalidate Old Secret
      ↓
Review Logs
      ↓
Determine Exposure Window
      ↓
Review Related Systems
```

---

# Information Disclosure and Reconnaissance

Information disclosure should feed back into reconnaissance.

```text
Disclosure
   ↓
New Hostname
   ↓
Scope Check
   ↓
Technology Identification
   ↓
New Endpoint
   ↓
Further Authorised Testing
```

Always verify that newly discovered assets remain within the authorised scope before testing them.

---

# References

## PortSwigger Web Security Academy: Information Disclosure

https://portswigger.net/web-security/information-disclosure

PortSwigger covers information disclosure through error messages, debugging information, backup files, version control history and application behaviour.

---

## PortSwigger Information Disclosure Labs

https://portswigger.net/web-security/all-labs#information-disclosure

Useful practical labs for recognising information leakage in web applications.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

The OWASP WSTG provides testing guidance for configuration, error handling, information gathering and application security assessment.

---

## OWASP Error Handling Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html

Useful defensive guidance for preventing verbose errors and exception information from reaching clients.

---

## OWASP REST Security Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html

Useful guidance for minimising information exposure through API responses and error handling.

---

## OWASP Secrets Management Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

Guidance for securely managing application secrets and responding to secret exposure.

---

## OWASP Logging Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

Useful for understanding how detailed diagnostic information can remain available to defenders without exposing it to clients.

---

# Final Information Disclosure Testing Model

```text
                       APPLICATION
                            ↓
                    MAP ATTACK SURFACE
                            ↓
         ┌──────────────────┼──────────────────┐
         ↓                  ↓                  ↓
      RESPONSES           FILES             CLIENT
         ↓                  ↓                  ↓
      Headers            Backups          JavaScript
      Errors             Config           Source Maps
      APIs               Git              Metadata
         ↓                  ↓                  ↓
         └──────────────────┼──────────────────┘
                            ↓
                    INFORMATION FOUND
                            ↓
                 SHOULD IT BE PUBLIC?
                            ↓
                  ┌─────────┴─────────┐
                  ↓                   ↓
                 YES                  NO
                  ↓                   ↓
             Usually Fine        IS IT SENSITIVE?
                                      ↓
                           ┌──────────┴──────────┐
                           ↓                     ↓
                          NO                    YES
                           ↓                     ↓
                    RECON VALUE?          DIRECT IMPACT?
                           ↓                     ↓
                           └──────────┬──────────┘
                                      ↓
                              CAN IT BE CHAINED?
                                      ↓
                  ┌───────────────────┼───────────────────┐
                  ↓                   ↓                   ↓
                SSRF             PATH TRAVERSAL       AUTH / ACCESS
                  ↓                   ↓                   ↓
             Internal Host        File Paths          User / Object
                  ↓                   ↓                   ↓
                  └───────────────────┼───────────────────┘
                                      ↓
                              ASSESS REAL IMPACT
                                      ↓
                              MINIMISE COLLECTION
                                      ↓
                                  DOCUMENT
                                      ↓
                                   REPORT
```

The key principle is:

> Information disclosure testing is not a hunt for banners alone. Determine what the application reveals, whether that information was intended to be public, how sensitive it is, and whether it materially reduces the effort required to compromise another part of the application or infrastructure.
