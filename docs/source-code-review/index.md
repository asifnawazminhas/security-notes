# Source Code Review

Source code review is the process of analysing application source code to identify security weaknesses, understand application behaviour, trace attacker-controlled data, and determine whether security-sensitive operations can be reached in an unsafe way.

Unlike black-box web application testing, source code review provides visibility into the application's internal implementation.

A reviewer can examine:

```text
Routes
Controllers
Endpoints
Middleware
Authentication
Authorisation
Input handling
Validation
Business logic
Database access
File operations
HTTP requests
Template rendering
Deserialisation
Cryptography
Secrets
Configuration
Dependencies
Security controls
Dangerous sinks
```

The primary objective is not simply to search for dangerous functions.

The objective is to understand:

```text
SOURCE
   |
   v
ATTACKER-CONTROLLED DATA
   |
   v
TRANSFORMATIONS
   |
   +--> Parsing
   +--> Decoding
   +--> Validation
   +--> Sanitisation
   +--> Normalisation
   +--> Business Logic
   +--> Authorisation
   |
   v
SINK
   |
   v
SECURITY-SENSITIVE OPERATION
```

A dangerous function found in source code is therefore only a **review candidate**.

```text
Dangerous function found
          !=
Vulnerability confirmed
```

The complete data flow and security controls must be analysed.

!!! warning "Authorised Security Testing"
    Perform source code review only against applications, repositories, source packages, or systems for which you have explicit authorisation. Source code may contain credentials, personal data, internal infrastructure information, cryptographic material, API keys, proprietary business logic, and other sensitive information. Handle reviewed material according to the engagement rules and applicable data-handling requirements.

---

# Source Code Review vs Black-Box Testing

Black-box testing primarily observes the application externally.

```text
Tester
  |
  v
HTTP Request
  |
  v
Application
  |
  v
HTTP Response
```

The tester attempts to infer what happens internally.

Source code review provides another perspective:

```text
HTTP Request
     |
     v
Route
     |
     v
Middleware
     |
     v
Controller
     |
     v
Validation
     |
     v
Authorisation
     |
     v
Business Logic
     |
     v
Sensitive Operation
```

This can reveal attack paths that are difficult to identify through black-box testing alone.

---

# White-Box, Grey-Box and Black-Box Testing

## Black-Box

The tester has no source code.

```text
External Behaviour
        |
        v
Infer Internal Behaviour
```

Examples:

```text
Burp Suite
HTTP testing
Content discovery
Parameter discovery
Fuzzing
Application interaction
```

---

## Grey-Box

The tester has partial knowledge.

Examples:

```text
API documentation
Limited source code
Architecture diagrams
Test credentials
Configuration files
Selected repositories
```

---

## White-Box

The tester has extensive internal visibility.

Examples:

```text
Full source code
Configuration
Dependency manifests
Infrastructure information
Database schemas
Build files
Deployment configuration
Architecture documentation
```

Source code review is primarily associated with white-box and grey-box testing.

---

# Why Source Code Review Matters

Many security weaknesses are easier to identify when implementation details are visible.

Examples include:

```text
Missing authorisation checks
Unsafe SQL construction
Command execution
Dangerous deserialisation
Weak cryptography
Hard-coded credentials
Hidden API endpoints
Debug functionality
Unused legacy routes
Internal administrative endpoints
Unsafe file handling
SSRF sinks
Mass assignment
Business logic flaws
Race conditions
Inconsistent validation
Framework misconfiguration
```

Source review also helps answer:

```text
Where does user input enter?

Where does it go?

What security controls are applied?

Can those controls be bypassed?

Where are sensitive operations performed?

Which endpoints expose those operations?
```

---

# The Core Source Code Review Model

A useful model is:

```text
ATTACK SURFACE
      |
      v
ENTRY POINT
      |
      v
SOURCE
      |
      v
DATA FLOW
      |
      v
SECURITY CONTROLS
      |
      v
SINK
      |
      v
IMPACT
```

Each stage should be understood.

---

# Attack Surface

Before searching for vulnerabilities, understand the application's attack surface.

Identify:

```text
Web routes
API routes
GraphQL endpoints
gRPC services
WebSocket handlers
Authentication endpoints
Administrative functionality
File upload endpoints
Import/export functionality
Webhooks
Callbacks
Background jobs
Scheduled tasks
Message consumers
Third-party integrations
Internal APIs
Debug endpoints
Health endpoints
Management interfaces
```

Source review should complement:

[Attack Surface Analysis](../web/attack-surface-analysis.md)

---

# Entry Points

An entry point is somewhere external data enters application logic.

Examples:

```text
HTTP request
API request
WebSocket message
gRPC message
GraphQL query
File upload
Webhook
Message queue
Database record
Configuration
Environment variable
Command-line argument
Scheduled job
Third-party API
```

Not every entry point is directly attacker-controlled.

The trust boundary must be determined.

---

# Sources

A **source** is a location where potentially untrusted data enters the application's data flow.

Examples:

```text
Query parameters
Path parameters
Form fields
JSON properties
XML elements
HTTP headers
Cookies
Uploaded files
Filename metadata
WebSocket messages
GraphQL arguments
gRPC fields
Webhook payloads
```

Language-specific examples differ.

For example:

```text
PHP

$_GET
$_POST
$_REQUEST
$_COOKIE
$_FILES
```

Python Flask:

```text
request.args
request.form
request.json
request.files
request.headers
request.cookies
```

Django:

```text
request.GET
request.POST
request.FILES
request.COOKIES
request.headers
```

Express:

```text
req.query
req.params
req.body
req.headers
req.cookies
```

ASP.NET:

```text
Request.Query
Request.Form
Request.Headers
Request.Cookies
RouteData
```

Java/Spring:

```text
@RequestParam
@PathVariable
@RequestBody
@RequestHeader
@CookieValue
```

These are starting points for tracing.

---

# Sinks

A **sink** is a security-sensitive operation where attacker-controlled data may become dangerous.

Examples include:

```text
SQL execution
Operating-system command execution
Template evaluation
LDAP queries
File access
URL fetching
Deserialisation
HTML generation
Redirects
Dynamic code execution
XML parsing
Header construction
Logging
Email generation
Expression evaluation
```

Conceptually:

```text
Source
   |
   v
User Input
   |
   v
Sink
```

is interesting.

But:

```text
Source
   |
   v
Validation
   |
   v
Safe API
   |
   v
Sink
```

may be secure.

Therefore sinks identify **review locations**, not automatically vulnerabilities.

---

# Sources and Sinks

The central question during source review is:

```text
Can attacker-controlled input reach a dangerous sink?
```

Then:

```text
What happens between the source and the sink?
```

Example:

```text
request parameter
       |
       v
controller
       |
       v
validation
       |
       v
service
       |
       v
database query
```

The reviewer must inspect the complete chain.

---

# Source-to-Sink Analysis

Consider:

```text
SOURCE
  |
  v
request.getParameter("id")
  |
  v
TRANSFORMATION
  |
  v
Integer.parseInt()
  |
  v
DATABASE QUERY
```

If the application converts the value to an integer before safely binding it to a parameterised query, SQL injection may not be possible.

Compare:

```text
SOURCE
  |
  v
request.getParameter("name")
  |
  v
String concatenation
  |
  v
SQL query
```

This requires closer inspection.

---

# Taint Analysis

Taint analysis tracks potentially untrusted data through an application.

Conceptually:

```text
TAINTED SOURCE
      |
      v
Variable A
      |
      v
Function B
      |
      v
Object C
      |
      v
Function D
      |
      v
SENSITIVE SINK
```

Example:

```text
HTTP Parameter
      |
      v
username
      |
      v
buildQuery(username)
      |
      v
executeQuery()
```

The objective is to determine whether the data remains attacker-controlled when it reaches the sink.

---

# Taint Propagation

Input may move through multiple variables.

Example:

```text
request.body.url
      |
      v
target
      |
      v
validatedTarget
      |
      v
fetchUrl()
```

Do not stop at variable names.

Inspect what actually happens.

For example:

```text
validatedTarget
```

does not prove that validation exists.

Read the implementation.

---

# Interprocedural Data Flow

Data often crosses multiple functions.

Example:

```text
Controller
   |
   v
Service
   |
   v
Utility
   |
   v
Repository
   |
   v
Database
```

The vulnerable operation may be several functions away from the original request.

---

# Reverse Source-to-Sink Analysis

Sometimes it is faster to start at dangerous sinks.

Example:

```text
exec()
```

Then work backwards:

```text
exec()
  ^
  |
command
  ^
  |
buildCommand()
  ^
  |
request parameter
```

This is particularly useful when reviewing large applications.

---

# Forward Analysis

Forward analysis starts at attacker-controlled input.

```text
HTTP Input
    |
    v
Where does it go?
```

This is useful when reviewing security-sensitive endpoints.

---

# Backward Analysis

Backward analysis starts at a dangerous operation.

```text
Dangerous Sink
      |
      v
Where did its arguments originate?
```

Both techniques should be used.

---

# Sources Are Not Always HTTP Inputs

An important source-review principle is:

```text
Untrusted data
    !=
Only HTTP parameters
```

Potentially untrusted sources may include:

```text
Database values
Message queues
Uploaded documents
CSV imports
Email
Third-party APIs
Webhooks
Cache values
Environment-specific integrations
User-generated content stored earlier
```

This matters for second-order vulnerabilities.

---

# Second-Order Vulnerabilities

A value may be stored safely initially but become dangerous later.

Example:

```text
User Input
    |
    v
Database
    |
    v
Later Retrieved
    |
    v
Dangerous Sink
```

Examples include:

```text
Stored XSS
Second-order SQL injection
Stored command injection
Stored template injection
Stored path manipulation
```

Do not assume database data is trusted merely because it came from the database.

---

# Trust Boundaries

Identify where data crosses trust boundaries.

Example:

```text
Internet
   |
   | Trust Boundary
   v
Web Application
```

But modern applications often have many more:

```text
Browser
   |
   v
API Gateway
   |
   v
Application
   |
   v
Internal API
   |
   v
Database
```

or:

```text
External SaaS
     |
     v
Webhook
     |
     v
Application
```

Trust must be based on architecture, not assumptions.

---

# Start With Application Structure

Before looking for individual vulnerabilities, understand the repository.

Useful questions:

```text
What language is used?

Which framework?

Where are routes defined?

Where are controllers?

Where is authentication implemented?

Where is authorisation implemented?

Where is configuration stored?

Where are templates?

Where are database queries?

Where are API clients?

Where are file operations?

Where are dependencies defined?

Where are tests?

Where are deployment files?
```

---

# Initial Repository Enumeration

Start with:

```bash
pwd
```

Then:

```bash
find . -maxdepth 2 -type f | sort
```

For larger repositories:

```bash
find . -maxdepth 3 -type f | sort | less
```

Directories:

```bash
find . -maxdepth 3 -type d | sort
```

---

# Tree

If available:

```bash
tree
```

Limit depth:

```bash
tree -L 3
```

Ignore common noise:

```bash
tree -L 3 -I 'node_modules|vendor|venv|.venv|dist|build|target|bin|obj'
```

This provides a quick architecture overview.

---

# Identify Languages

Useful command:

```bash
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -nr
```

This provides a rough extension count.

For example:

```text
450 java
220 js
90 html
50 xml
20 properties
```

This can immediately indicate the application's technology stack.

---

# Identify Frameworks

Look for dependency and build files.

Common examples:

```text
.NET

*.csproj
*.sln
Directory.Build.props
packages.lock.json
```

Java:

```text
pom.xml
build.gradle
build.gradle.kts
settings.gradle
```

PHP:

```text
composer.json
composer.lock
```

Python:

```text
requirements.txt
pyproject.toml
Pipfile
Pipfile.lock
poetry.lock
setup.py
```

JavaScript:

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
```

---

# Dependency Files

Dependency manifests reveal:

```text
Framework
Libraries
Database drivers
Template engines
Authentication libraries
Cloud SDKs
Serialization libraries
HTTP clients
Security libraries
```

They are also important for dependency security.

Refer to:

[Dependency Security](../web/dependency-security.md)

---

# Identify Configuration

Search for:

```text
.env
.env.example
application.properties
application.yml
appsettings.json
web.config
settings.py
config.py
config.php
php.ini
package.json
docker-compose.yml
Dockerfile
```

Also inspect:

```text
CI/CD files
Kubernetes manifests
Terraform
Helm charts
Cloud configuration
```

Configuration often reveals security-relevant behaviour.

---

# Secrets Exposure

Search repositories for potential:

```text
Passwords
API keys
Tokens
Private keys
Database credentials
Cloud credentials
Signing secrets
JWT secrets
OAuth secrets
Encryption keys
```

Refer to:

[Secrets Exposure](../web/secrets-exposure.md)

Do not assume every high-entropy string is a valid credential.

Validate carefully and safely.

---

# Route Discovery

One of the first major source-review tasks is finding all routes.

The objective is to build:

```text
HTTP Method
    |
    v
Route
    |
    v
Handler
    |
    v
Authentication
    |
    v
Authorisation
```

Example inventory:

| Method | Route | Handler | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/profile` | `profile()` | Required | Current user |
| POST | `/admin/user` | `createUser()` | Required | Admin |
| GET | `/api/orders/{id}` | `getOrder()` | Required | Object check |
| POST | `/upload` | `upload()` | Required | User |

---

# Why Route Mapping Matters

Route mapping reveals:

```text
Hidden endpoints
Legacy endpoints
Administrative functionality
Debug endpoints
Internal APIs
Alternate versions
Unauthenticated functionality
Different HTTP methods
```

It also provides the foundation for systematic review.

---

# Authentication Mapping

Find:

```text
Login handlers
Session creation
Token generation
JWT validation
OAuth callbacks
SAML handlers
Password reset
MFA
Remember-me functionality
API key validation
```

Then determine:

```text
Which endpoints require authentication?

Which do not?

How is authentication enforced?

Is it middleware-based?

Annotation-based?

Decorator-based?

Manually implemented?
```

Refer to:

[Authentication Testing](../web/authentication.md)

---

# Authorisation Mapping

Authentication answers:

```text
Who are you?
```

Authorisation answers:

```text
Are you allowed to perform this action?
```

Search for:

```text
Role checks
Permission checks
Ownership checks
Tenant checks
Policy checks
Authorisation middleware
Security annotations
Decorators
Access-control helpers
```

The key question is:

```text
Can a user reach a sensitive operation without the required authorisation check?
```

Refer to:

[Authorisation Testing](../web/authorisation.md)

[IDOR and BOLA](../web/idor-bola.md)

---

# Object-Level Authorisation

For endpoints such as:

```text
GET /api/orders/123
```

trace:

```text
123
 |
 v
Object Lookup
 |
 v
Ownership / Permission Check
 |
 v
Return Object
```

A secure lookup may conceptually be:

```text
Find order
WHERE
order.id = requested_id
AND
order.user_id = current_user
```

rather than:

```text
Find order
WHERE
order.id = requested_id
```

followed by no ownership check.

---

# Input Validation Mapping

Find where the application validates:

```text
Types
Length
Range
Format
Enumerations
Business rules
Schemas
Files
URLs
Identifiers
```

Then determine whether validation occurs:

```text
Client-side only
Server-side
Controller
Schema
Service
Domain layer
Database
```

Refer to:

[Input Validation](../web/input-validation.md)

---

# Security Control Mapping

During review, build an inventory of reusable security controls.

Examples:

```text
Authentication middleware
Authorisation middleware
CSRF middleware
Input validators
Output encoders
HTML sanitisers
URL validators
File validators
SQL abstraction layers
Logging helpers
Cryptographic utilities
Rate limiters
```

Then determine:

```text
Where are they used?

Where are they missing?

Can they be bypassed?

Are there alternate implementations?
```

---

# Identify Security Control Inconsistency

One of the most productive review techniques is comparing similar endpoints.

Example:

```text
/api/v1/users/{id}
        |
        +--> authorisation check

/api/v2/users/{id}
        |
        +--> no authorisation check
```

or:

```text
POST /profile
    |
    +--> validation

PATCH /profile
    |
    +--> no validation
```

Security inconsistencies frequently reveal vulnerabilities.

---

# Dangerous Sink Categories

A useful source-review strategy is to classify sinks.

```text
Database Sinks
Command Sinks
File Sinks
Network Sinks
Template Sinks
Deserialisation Sinks
HTML / DOM Sinks
Redirect Sinks
XML Sinks
Dynamic Code Sinks
Cryptographic Sinks
Logging Sinks
```

---

# Database Sinks

Potential security issues:

```text
SQL Injection
NoSQL Injection
LDAP Injection
Mass Assignment
Data exposure
```

Review:

```text
Raw queries
String concatenation
Dynamic query fragments
Native queries
ORM escape hatches
User-controlled filters
Sort expressions
Column names
Table names
```

---

# Command Sinks

Look for APIs capable of launching:

```text
Commands
Processes
Shells
Scripts
External programs
```

Then trace:

```text
Can attacker-controlled data influence:

Executable?
Arguments?
Environment?
Working directory?
Shell syntax?
```

Refer to:

[OS Command Injection](../web/command-injection.md)

---

# File Sinks

Review:

```text
File reads
File writes
File deletion
Directory creation
Archive extraction
Upload storage
File downloads
Template loading
Configuration loading
```

Trace attacker-controlled:

```text
Filename
Path
Extension
Directory
Archive entry
```

Refer to:

[Path Traversal](../web/path-traversal.md)

[File Inclusion](../web/file-inclusion.md)

[File Upload Security](../web/file-upload.md)

---

# Network Sinks

Look for:

```text
HTTP clients
URL fetchers
Webhook clients
Image downloaders
Document importers
Cloud SDKs
FTP clients
Socket connections
```

Trace:

```text
URL
Hostname
Port
Scheme
Redirect destination
```

Refer to:

[Server Side Request Forgery](../web/ssrf.md)

---

# Template Sinks

Review:

```text
Dynamic template creation
Template strings
Template compilation
Template evaluation
```

The key distinction is:

```text
User input as data
```

versus:

```text
User input as template source
```

Refer to:

[Server-Side Template Injection](../web/ssti.md)

---

# Deserialisation Sinks

Look for APIs that convert serialized data into objects.

Formats may include:

```text
Native object serialization
JSON
XML
YAML
Pickle
Binary formats
Custom serialization
```

Not all deserialisation is unsafe.

Review:

```text
Data source
Type restrictions
Allowed classes
Parser configuration
Integrity protection
```

Refer to:

[Insecure Deserialization](../web/deserialization.md)

---

# XML Sinks

Identify XML parsers.

Review:

```text
External entity support
DTD handling
Schema handling
Network access
Parser configuration
```

Refer to:

[XML External Entity Injection](../web/xxe.md)

---

# HTML and DOM Sinks

Review places where attacker-controlled data reaches:

```text
HTML
JavaScript
DOM APIs
Attributes
URLs
CSS
```

Context matters.

Refer to:

[Cross-Site Scripting](../web/xss.md)

[DOM-Based Vulnerabilities](../web/dom-based-vulnerabilities.md)

[HTML Injection](../web/html-injection.md)

---

# Redirect Sinks

Look for:

```text
Redirect functions
Location headers
Callback URLs
Return URLs
Next parameters
Continue parameters
```

Trace whether the destination is attacker-controlled.

Refer to:

[Open Redirect](../web/open-redirect.md)

---

# Dynamic Code Execution

High-value review candidates include APIs capable of:

```text
Evaluating code
Executing expressions
Compiling code
Loading dynamic modules
Interpreting scripts
```

Examples differ by language.

These require careful source tracing.

---

# Business Logic

Many important vulnerabilities do not have an obvious dangerous function.

Examples:

```text
Negative quantities
Invalid state transitions
Discount manipulation
Workflow bypass
Approval bypass
Double spending
Tenant confusion
Race conditions
Privilege transitions
```

These require understanding the application.

Source code review should therefore not be reduced to sink searching.

Refer to:

[Business Logic Vulnerabilities](../web/business-logic.md)

[Race Conditions](../web/race-conditions.md)

---

# Security-Relevant Variables

Search for names such as:

```text
admin
role
permission
privilege
owner
user_id
account_id
tenant_id
price
amount
quantity
discount
balance
status
state
approved
verified
mfa
password
token
secret
key
redirect
callback
url
filename
path
command
query
```

These searches can identify important logic quickly.

But:

```text
Interesting variable name
        !=
Vulnerability
```

---

# Search Tools

Useful tools include:

```text
grep
ripgrep
find
git
Semgrep
CodeQL
Language-specific static analysers
IDE references
Call hierarchy
```

---

# ripgrep

`ripgrep`, commonly invoked as `rg`, is extremely useful for source review.

Basic search:

```bash
rg 'pattern' .
```

Case-insensitive:

```bash
rg -i 'password|secret|token' .
```

Line numbers are displayed by default.

Restrict by file type:

```bash
rg -t py 'subprocess|os\.system' .
```

List matching files:

```bash
rg -l 'pattern' .
```

---

# Search Multiple Security Concepts

Example:

```bash
rg -n -i \
'password|passwd|secret|token|api[_-]?key|private[_-]?key' \
.
```

Treat results as candidates requiring manual validation.

---

# Exclude Dependencies

Large repositories may contain third-party code.

Example:

```bash
rg \
-g '!node_modules/**' \
-g '!vendor/**' \
-g '!venv/**' \
-g '!.venv/**' \
-g '!dist/**' \
-g '!build/**' \
'pattern' \
.
```

This can significantly reduce noise.

---

# Search Configuration Files

```bash
find . \
-type f \
\( \
-name '*.env' \
-o -name '*.yml' \
-o -name '*.yaml' \
-o -name '*.json' \
-o -name '*.xml' \
-o -name '*.properties' \
-o -name '*.config' \
\) \
-print
```

Review relevant results manually.

---

# Search TODO and Debug Code

```bash
rg -n -i \
'todo|fixme|hack|debug|temporary|bypass|disable|disabled' \
.
```

These comments may reveal unfinished security controls or development functionality.

Do not assume comments accurately describe current behaviour.

---

# Search Authentication Terms

```bash
rg -n -i \
'login|logout|authenticate|authentication|authorize|authorization|permission|role|admin|session|jwt|oauth|saml|mfa' \
.
```

---

# Search Potential Secrets

```bash
rg -n -i \
'password|passwd|secret|token|api[_-]?key|client[_-]?secret|private[_-]?key|access[_-]?key' \
.
```

Then determine:

```text
Example value?
Test credential?
Production credential?
Placeholder?
Environment variable reference?
Actually usable secret?
```

---

# Git History

Current source code is only one point in time.

Security-relevant data may exist in Git history.

Useful commands:

```bash
git log --oneline --all
```

Search commit changes:

```bash
git log -p --all
```

Search for a string:

```bash
git log -S 'password' --all -p
```

Search commits whose patches match a regex:

```bash
git log -G 'secret|token|api[_-]?key' --all -p
```

Handle historical secrets carefully.

A removed credential may still be active.

---

# Review Security Fixes

Git history can reveal previous vulnerabilities.

Search commit messages:

```bash
git log --all --oneline --grep='security'
```

```bash
git log --all --oneline --grep='auth'
```

```bash
git log --all --oneline --grep='sanitize'
```

```bash
git log --all --oneline --grep='validation'
```

A previous fix can reveal similar unfixed code elsewhere.

---

# Variant Analysis

Variant analysis means:

```text
Find one security weakness
        |
        v
Understand its root cause
        |
        v
Search for the same pattern elsewhere
```

Example:

```text
Missing ownership check
        |
        v
Search all object lookup endpoints
```

or:

```text
Unsafe raw SQL construction
        |
        v
Search all raw query usage
```

This is one of the most effective source-review techniques.

---

# Code Duplication

Similar vulnerable logic may have been copied.

Search:

```text
Same helper
Same query pattern
Same validation function
Same controller logic
Same authorisation pattern
```

Do not stop after finding the first instance.

---

# IDE-Assisted Review

An IDE can significantly improve manual analysis.

Useful features include:

```text
Go to definition
Find references
Call hierarchy
Type hierarchy
Search symbols
Find implementations
Rename preview
Data-flow features
```

For example:

```text
Dangerous Sink
      |
      v
Find References
      |
      v
Identify Callers
      |
      v
Trace Back to Routes
```

---

# Visual Studio Code

Useful source-review functionality includes:

```text
Global search
Go to Definition
Peek Definition
Find All References
Call Hierarchy
Symbol Search
Git integration
```

Extensions should be reviewed before installation in sensitive environments.

---

# Semgrep

Semgrep can identify source patterns using static-analysis rules.

Typical workflow:

```text
Repository
    |
    v
Semgrep
    |
    v
Candidate Findings
    |
    v
Manual Review
```

Semgrep results should not automatically be treated as confirmed vulnerabilities.

Official project:

```text
https://semgrep.dev/
```

---

# CodeQL

CodeQL supports semantic code analysis and can model data flow.

Conceptually:

```text
Source
   |
   v
Data Flow
   |
   v
Sink
```

This makes it particularly useful for vulnerability classes such as:

```text
Injection
Path traversal
XSS
Unsafe deserialisation
```

depending on the supported language and query.

Official documentation:

```text
https://codeql.github.com/docs/
```

---

# Static Analysis vs Manual Review

Static analysis is useful for:

```text
Pattern detection
Data flow
Known dangerous APIs
Large codebases
Variant analysis
```

Manual review remains important for:

```text
Business logic
Authorisation
Workflow
Context
Architecture
False-positive elimination
Exploitability
```

The strongest approach combines both.

```text
Static Analysis
       +
Manual Review
       +
Dynamic Testing
```

---

# SAST Findings Are Leads

A scanner may report:

```text
Potential SQL Injection
```

This means:

```text
Investigate
```

not automatically:

```text
Confirmed SQL Injection
```

Verify:

```text
Source controllability
Data flow
Sanitisation
Parameterisation
Reachability
Authentication
Authorisation
Impact
```

---

# Reachability

A dangerous function may not be reachable.

Example:

```text
Legacy function
    |
    v
No callers
```

or:

```text
Debug endpoint
    |
    v
Only compiled in development
```

Determine whether the code is actually reachable in the target deployment.

---

# Deployment Context

Source code alone may not reveal which functionality is enabled.

Consider:

```text
Environment variables
Build flags
Feature flags
Configuration
Reverse proxy
API gateway
Cloud environment
Container configuration
Runtime version
```

A vulnerability in unused code may have different significance from one exposed in production.

---

# Feature Flags

Search for:

```text
feature
flag
enabled
disabled
experimental
beta
preview
```

Security controls sometimes differ between feature variants.

---

# Environment-Specific Logic

Look for:

```text
development
staging
production
test
local
debug
```

Example conceptual pattern:

```text
if development:
    disable_authentication()
```

Determine whether configuration mistakes could expose development behaviour elsewhere.

---

# Debug Functionality

Search for:

```text
debug
test
diagnostic
health
metrics
admin
internal
dev
```

Then determine:

```text
Is it routable?

Is it authenticated?

What information does it expose?

Can it perform actions?
```

---

# Information Disclosure

Source review can identify:

```text
Stack trace configuration
Debug pages
Verbose errors
Internal hostnames
Database details
File paths
Secrets
API keys
Source maps
Internal endpoints
```

Refer to:

[Information Disclosure](../web/information-disclosure.md)

---

# Error Handling

Search:

```text
Exception
catch
throw
traceback
stack trace
error handler
```

Determine whether:

```text
Sensitive information reaches users
Errors are swallowed
Security checks fail open
```

---

# Fail Open vs Fail Closed

Security controls should generally fail safely.

Example:

```text
Authorisation Service Error
          |
      +---+---+
      |       |
      v       v
    Deny     Allow
```

For security-sensitive decisions, unexpected errors should generally not result in automatic access.

---

# Authentication Review

Review:

```text
Credential validation
Password hashing
Session creation
Token generation
Token validation
Logout
Password reset
MFA
Account recovery
Remember-me
Brute-force protection
```

Refer to:

[Authentication Testing](../web/authentication.md)

[Password Reset Security](../web/password-reset.md)

[Multi-Factor Authentication Security](../web/mfa.md)

[Session Management](../web/session-management.md)

---

# Password Storage

Identify password hashing functions and configuration.

Review:

```text
Algorithm
Work factor
Salt handling
Migration from legacy hashes
Password comparison
```

Do not confuse encryption with password hashing.

---

# Session Review

Trace:

```text
Login
  |
  v
Session Creation
  |
  v
Cookie
  |
  v
Request Authentication
  |
  v
Logout / Expiry
```

Review:

```text
Session rotation
Expiration
Invalidation
Cookie attributes
Concurrent sessions
```

---

# JWT Review

Find:

```text
Token generation
Signing
Verification
Claims
Expiration
Issuer
Audience
Key selection
```

Trace where claims influence:

```text
Identity
Roles
Tenant
Permissions
```

Refer to:

[JSON Web Token Security](../web/jwt.md)

---

# OAuth and OIDC Review

Map:

```text
Authorization request
       |
       v
Callback
       |
       v
Code exchange
       |
       v
Token validation
       |
       v
Session creation
```

Review:

```text
state
nonce
redirect URI
issuer
audience
PKCE
token validation
account linking
```

Refer to:

[OAuth 2.0 and OpenID Connect Security](../web/oauth-oidc.md)

---

# SAML Review

Map:

```text
SAML Request
     |
     v
Identity Provider
     |
     v
SAML Response
     |
     v
Validation
     |
     v
Application Session
```

Review:

```text
Signature validation
Issuer
Audience
Destination
Recipient
Replay
XML parsing
Attribute mapping
```

Refer to:

[SAML Security](../web/saml.md)

---

# Authorisation Review

Look beyond obvious:

```text
if role == admin
```

Authorisation may be implemented through:

```text
Middleware
Annotations
Decorators
Policies
Filters
Framework configuration
Database queries
Service methods
```

Build an authorisation matrix.

---

# Authorisation Matrix

Example:

| Action | Anonymous | User | Manager | Admin |
|---|---:|---:|---:|---:|
| View profile | No | Own | Team | Any |
| Edit profile | No | Own | No | Any |
| View invoice | No | Own | Team | Any |
| Delete user | No | No | No | Yes |

Compare this expected model with actual code.

---

# IDOR / BOLA Review

Look for patterns:

```text
Object ID from request
       |
       v
Database lookup
       |
       v
Return / modify object
```

Then ask:

```text
Where is ownership checked?
```

Refer to:

[IDOR and BOLA](../web/idor-bola.md)

---

# Mass Assignment Review

Look for:

```text
Request object
      |
      v
Automatic binding
      |
      v
Domain / database object
```

Determine whether security-sensitive properties can be set.

Examples:

```text
role
admin
owner
tenant
balance
status
verified
```

Refer to:

[Mass Assignment](../web/mass-assignment.md)

---

# SQL Injection Review

Trace:

```text
Request Input
      |
      v
Query Construction
      |
      v
Database Execution
```

Look for:

```text
String concatenation
String interpolation
Raw SQL
Dynamic query fragments
Native queries
```

Then determine whether parameterisation is used correctly.

Refer to:

[SQL Injection](../web/sql-injection.md)

---

# NoSQL Injection Review

Review:

```text
Dynamic query objects
User-controlled operators
JSON-to-query conversion
Filter construction
```

Refer to:

[NoSQL Injection](../web/nosql-injection.md)

---

# LDAP Injection Review

Review:

```text
LDAP filters
Distinguished names
Search filters
Dynamic filter construction
```

Refer to:

[LDAP Injection](../web/ldap-injection.md)

---

# Command Injection Review

Trace:

```text
Input
  |
  v
Command Construction
  |
  v
Process API
```

Determine whether:

```text
Shell invoked?
Executable controlled?
Arguments controlled?
Input allowlisted?
```

Refer to:

[OS Command Injection](../web/command-injection.md)

---

# SSTI Review

Find template APIs.

Determine:

```text
Is user input passed as template data?
```

or:

```text
Is user input compiled/evaluated as template source?
```

Refer to:

[Server-Side Template Injection](../web/ssti.md)

---

# XSS Review

Trace:

```text
User Input
    |
    v
Storage / Processing
    |
    v
HTML Output
```

Review the actual output context.

Examples:

```text
HTML text
HTML attribute
JavaScript
URL
CSS
DOM
```

Refer to:

[Cross-Site Scripting](../web/xss.md)

[DOM-Based Vulnerabilities](../web/dom-based-vulnerabilities.md)

---

# CSRF Review

Identify state-changing endpoints.

Review:

```text
Cookie-based authentication
CSRF tokens
SameSite cookies
Origin checks
Referer checks
Framework CSRF middleware
```

Refer to:

[Cross-Site Request Forgery](../web/csrf.md)

---

# CORS Review

Search for:

```text
CORS configuration
Allowed origins
Credential support
Wildcard origins
Dynamic origin reflection
```

Refer to:

[Cross-Origin Resource Sharing (CORS)](../web/cors.md)

---

# SSRF Review

Search HTTP-client usage.

Trace:

```text
Request Parameter
       |
       v
URL Construction
       |
       v
HTTP Client
```

Review:

```text
Scheme restrictions
Host restrictions
DNS resolution
Redirect handling
Network egress
```

Refer to:

[Server Side Request Forgery](../web/ssrf.md)

---

# Path Traversal Review

Trace:

```text
User Input
    |
    v
Path Construction
    |
    v
File Operation
```

Review:

```text
Canonicalisation
Path joining
Base directory enforcement
Filename mapping
```

Refer to:

[Path Traversal](../web/path-traversal.md)

---

# File Upload Review

Trace:

```text
Uploaded File
     |
     v
Validation
     |
     v
Storage
     |
     v
Processing
     |
     v
Retrieval
```

Review:

```text
Filename
Extension
MIME type
Content
File signature
Size
Storage location
Execution possibility
Image/document processing
Archive extraction
```

Refer to:

[File Upload Security](../web/file-upload.md)

---

# Deserialisation Review

Search for deserialisation APIs and trace their input.

Determine:

```text
Can an attacker influence serialized data?

Are arbitrary types allowed?

Is integrity protection used?

Does deserialisation trigger dangerous behaviour?
```

Refer to:

[Insecure Deserialization](../web/deserialization.md)

---

# Open Redirect Review

Trace:

```text
Request Input
      |
      v
Redirect Destination
```

Review whether destinations are:

```text
Allowlisted
Mapped server-side
Restricted to local paths
```

Refer to:

[Open Redirect](../web/open-redirect.md)

---

# HTTP Host Header Review

Search for use of:

```text
Host
X-Forwarded-Host
Forwarded
```

in:

```text
Password reset links
Absolute URLs
Redirects
Emails
Cache keys
Security decisions
```

Refer to:

[HTTP Host Header Attacks](../web/host-header-attacks.md)

---

# HTTP Security Headers

Review configuration for:

```text
Content-Security-Policy
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
Frame protection
```

Do not automatically report every missing header as a vulnerability.

Consider application context and actual impact.

Refer to:

[HTTP Security Headers](../web/http-security-headers.md)

---

# Rate Limiting

Identify:

```text
Login
Password reset
MFA
Registration
OTP verification
API keys
Expensive operations
Search
AI endpoints
```

Then locate rate-limiting controls.

Review:

```text
Key used for limiting
IP address handling
User/account identifiers
Distributed storage
Proxy trust
Failure behaviour
```

Refer to:

[Rate Limiting and Anti-Automation](../web/rate-limiting.md)

---

# Race Conditions

Look for:

```text
Check
 |
 v
State Read
 |
 v
Operation
 |
 v
State Write
```

where concurrent requests may violate assumptions.

Security-sensitive examples:

```text
Balance
Coupon
Inventory
Password reset
Invitation
MFA
Account creation
```

Refer to:

[Race Conditions](../web/race-conditions.md)

---

# Dependency Security

Identify dependency manifests and lockfiles.

Review:

```text
Versions
Known vulnerabilities
Unsupported packages
Unmaintained dependencies
Direct dependencies
Transitive dependencies
```

Use software composition analysis where appropriate.

Refer to:

[Dependency Security](../web/dependency-security.md)

---

# Third-Party JavaScript

Review:

```text
External scripts
CDNs
Tag managers
Analytics
Payment scripts
Support widgets
Chat widgets
```

Determine:

```text
What executes in the page?

What data can it access?

Is SRI appropriate?

What CSP restrictions exist?

How is vendor change managed?
```

Refer to:

[Third-Party JavaScript Security](../web/third-party-javascript.md)

---

# API Security

For APIs, map:

```text
Routes
Methods
Authentication
Authorisation
Object IDs
Schemas
Rate limits
Error handling
Versioning
```

Refer to:

[API Security](../web/api-security.md)

---

# GraphQL

Identify:

```text
Schema
Resolvers
Mutations
Authentication
Authorisation
Data loaders
Custom scalars
```

Authorisation should be reviewed at the actual data-access level, not merely at the GraphQL endpoint.

Refer to:

[GraphQL API Security](../web/graphql.md)

---

# gRPC

Identify:

```text
.proto files
Services
RPC methods
Interceptors
Authentication
Authorisation
Message validation
```

Refer to:

[gRPC Security](../web/grpc-security.md)

---

# WebSockets

Map:

```text
Connection establishment
Authentication
Message handlers
Message types
Object access
Authorisation
State changes
```

Refer to:

[WebSocket Security](../web/websockets.md)

---

# Secrets and Sensitive Configuration

Review:

```text
Source files
Configuration
Environment examples
Tests
CI/CD
Docker files
Git history
Documentation
Scripts
```

Potential secrets require validation.

Refer to:

[Secrets Exposure](../web/secrets-exposure.md)

---

# Cryptography

Search for:

```text
Encryption
Decryption
Hashing
Random generation
Key generation
Signatures
Password hashing
Token generation
```

Review:

```text
Algorithm choice
Key management
Nonce/IV generation
Randomness
Integrity protection
Hard-coded keys
Custom cryptography
```

Avoid reporting algorithm names without understanding their usage.

---

# Randomness

Security-sensitive values include:

```text
Session IDs
Password-reset tokens
MFA recovery codes
API keys
Invitation tokens
CSRF tokens
```

Determine whether they use a cryptographically secure random source.

---

# Logging

Review whether logs contain:

```text
Passwords
Tokens
Authorization headers
Session IDs
API keys
Personal data
Sensitive request bodies
```

Also consider attacker-controlled data entering logs.

---

# Source Code Review Workflow

A practical workflow is:

```text
1. Understand the Repository

2. Identify Languages and Frameworks

3. Identify Build and Dependency Files

4. Identify Configuration

5. Map Routes and Entry Points

6. Map Authentication

7. Map Authorisation

8. Map User-Controlled Sources

9. Map Security Controls

10. Identify Dangerous Sinks

11. Trace Source-to-Sink Data Flow

12. Review Business Logic

13. Review Secrets and Configuration

14. Review Dependencies

15. Review Git History

16. Run Static Analysis

17. Perform Variant Analysis

18. Validate Findings Dynamically Where Permitted

19. Determine Security Impact

20. Document Evidence
```

---

# Phase 1 - Repository Understanding

```text
[ ] Languages identified
[ ] Frameworks identified
[ ] Build system identified
[ ] Dependency files identified
[ ] Application entry point identified
[ ] Configuration identified
[ ] Deployment files identified
[ ] Test directories identified
[ ] Generated code identified
[ ] Third-party code identified
```

---

# Phase 2 - Attack Surface

```text
[ ] Routes identified
[ ] API endpoints identified
[ ] GraphQL identified
[ ] gRPC identified
[ ] WebSockets identified
[ ] File uploads identified
[ ] Webhooks identified
[ ] Admin endpoints identified
[ ] Debug endpoints identified
[ ] Background jobs identified
[ ] Third-party integrations identified
```

---

# Phase 3 - Authentication

```text
[ ] Login flow mapped
[ ] Logout flow mapped
[ ] Session creation mapped
[ ] Password reset mapped
[ ] MFA mapped
[ ] OAuth/OIDC mapped
[ ] SAML mapped
[ ] API authentication mapped
[ ] JWT generation mapped
[ ] JWT validation mapped
```

---

# Phase 4 - Authorisation

```text
[ ] Roles identified
[ ] Permissions identified
[ ] Authorisation middleware identified
[ ] Object ownership checks identified
[ ] Tenant checks identified
[ ] Administrative actions identified
[ ] Sensitive endpoints mapped to permissions
```

---

# Phase 5 - Sources

```text
[ ] Query parameters identified
[ ] Path parameters identified
[ ] Request bodies identified
[ ] JSON fields identified
[ ] XML fields identified
[ ] Headers identified
[ ] Cookies identified
[ ] Uploaded files identified
[ ] WebSocket messages identified
[ ] GraphQL arguments identified
[ ] gRPC fields identified
[ ] Webhook data identified
```

---

# Phase 6 - Sinks

```text
[ ] SQL sinks identified
[ ] NoSQL sinks identified
[ ] LDAP sinks identified
[ ] Command sinks identified
[ ] File sinks identified
[ ] Network sinks identified
[ ] Template sinks identified
[ ] Deserialisation sinks identified
[ ] XML parsers identified
[ ] Redirect sinks identified
[ ] HTML/DOM sinks identified
[ ] Dynamic execution sinks identified
```

---

# Phase 7 - Data Flow

For every important source-to-sink path:

```text
[ ] Source is attacker-controllable
[ ] Data transformations identified
[ ] Validation identified
[ ] Sanitisation identified
[ ] Encoding identified
[ ] Authorisation identified
[ ] Sink identified
[ ] Reachability confirmed
[ ] Exploitability assessed
```

---

# Phase 8 - Business Logic

```text
[ ] State transitions reviewed
[ ] Financial calculations reviewed
[ ] Quantity handling reviewed
[ ] Discounts reviewed
[ ] Approval workflows reviewed
[ ] Tenant boundaries reviewed
[ ] Role transitions reviewed
[ ] Race conditions considered
```

---

# Phase 9 - Configuration and Secrets

```text
[ ] Hard-coded credentials searched
[ ] API keys searched
[ ] Tokens searched
[ ] Private keys searched
[ ] Debug settings reviewed
[ ] Production settings reviewed
[ ] CORS reviewed
[ ] Security headers reviewed
[ ] Secret management reviewed
```

---

# Phase 10 - Dependencies

```text
[ ] Dependency manifests reviewed
[ ] Lockfiles reviewed
[ ] Vulnerability scanning considered
[ ] Unsupported dependencies identified
[ ] High-risk libraries reviewed
[ ] Transitive dependencies considered
```

---

# Phase 11 - Git History

```text
[ ] Security-related commits reviewed
[ ] Removed secrets considered
[ ] Previous vulnerability fixes reviewed
[ ] Deleted endpoints considered
[ ] Historical configuration considered
```

---

# Phase 12 - Static Analysis

```text
[ ] ripgrep searches performed
[ ] Semgrep considered
[ ] CodeQL considered
[ ] Language-specific analyser considered
[ ] Scanner results manually reviewed
[ ] False positives removed
```

---

# Phase 13 - Variant Analysis

```text
[ ] Root cause understood
[ ] Similar functions searched
[ ] Similar routes searched
[ ] Similar sinks searched
[ ] Similar validation patterns searched
[ ] Similar authorisation patterns searched
```

---

# Phase 14 - Dynamic Validation

Where authorised and appropriate:

```text
Source Finding
      |
      v
Identify Endpoint
      |
      v
Create Controlled Request
      |
      v
Verify Behaviour
      |
      v
Determine Impact
```

Source review and dynamic testing reinforce each other.

---

# Evidence Collection

For each candidate finding record:

```text
File
Line
Function
Class
Route
Source
Data flow
Security control
Sink
Reachability
Authentication requirement
Authorisation requirement
Observed impact
```

Example:

```text
Route:
POST /api/report

Source:
request JSON field "url"

Handler:
ReportController.create()

Data flow:
url -> ReportService.generate() -> fetchRemoteDocument()

Sink:
HTTP client

Validation:
Scheme validation only

Authorisation:
Authenticated users

Security concern:
Potential SSRF

Dynamic validation:
Controlled callback received

Impact:
Server-side request to attacker-controlled destination
```

---

# Finding Classification

A useful classification is:

```text
Candidate
   |
   v
Reachable?
   |
   +-- No --> Informational / discard
   |
   v
Attacker Controlled?
   |
   +-- No --> Review context
   |
   v
Security Control?
   |
   +-- Effective --> Not vulnerable
   |
   v
Exploitable?
   |
   +-- No --> Defence-in-depth / discard
   |
   v
Security Impact?
   |
   +-- No --> Low significance
   |
   v
Confirmed Finding
```

---

# Avoid Scanner-Driven Reporting

Do not report:

```text
Semgrep found exec()
```

Report:

```text
Attacker-controlled filename reaches a shell command without safe argument handling, allowing command injection.
```

The finding should describe:

```text
Cause
Reachability
Exploitability
Impact
```

---

# Finding Template

```text
Title:
[Specific vulnerability]

Affected Component:
[Route / class / function]

Source:
[Attacker-controlled input]

Sink:
[Security-sensitive operation]

Data Flow:
[Source -> transformations -> sink]

Security Control:
[Missing / ineffective / bypassable control]

Impact:
[What an attacker can achieve]

Evidence:
[Relevant source locations and controlled runtime evidence]

Recommendation:
[Root-cause remediation]
```

---

# Example Source Review Finding

```text
Title:
Server-Side Request Forgery Through User-Controlled Report URL

Affected Component:
Report generation functionality

Source:
POST /api/report
JSON property: url

Data Flow:

request.body.url
      |
      v
ReportController
      |
      v
ReportService
      |
      v
HTTP client
      |
      v
Remote request

Observed Control:
Only the URL scheme is checked.

Impact:
An authenticated attacker can cause the application server to make requests to attacker-controlled destinations.

Recommendation:
Restrict server-side requests to explicitly permitted destinations where possible. Validate the resolved destination, account for redirects and DNS behaviour, and apply network-level egress restrictions appropriate to the application's requirements.
```

---

# Quick Review Questions

For every endpoint ask:

```text
Where is the route defined?

What HTTP methods are allowed?

Is authentication required?

How is authentication enforced?

What role is required?

How is authorisation enforced?

Which objects can the user reference?

Are ownership checks performed?

Which parameters are attacker-controlled?

How are they validated?

Where do they flow?

Do they reach SQL?

Do they reach a shell?

Do they reach LDAP?

Do they reach a template?

Do they reach the filesystem?

Do they reach an HTTP client?

Do they reach HTML?

Do they reach a redirect?

Do they reach a deserialiser?

Can the user control object properties?

Can the user influence state transitions?

Are operations rate-limited?

Are secrets involved?

Are sensitive values logged?

Can requests race?

Does another route implement the same operation differently?
```

---

# Quick Sink Reference

```text
SQL
  -> SQL Injection

NoSQL Query
  -> NoSQL Injection

LDAP Query
  -> LDAP Injection

Shell / Process
  -> Command Injection

Template Evaluation
  -> SSTI

HTML / DOM
  -> XSS / HTML Injection

File Read
  -> Path Traversal / File Inclusion

File Write
  -> Arbitrary File Write / Upload Issues

HTTP Client
  -> SSRF

Redirect
  -> Open Redirect

Deserialiser
  -> Insecure Deserialisation

XML Parser
  -> XXE

Object Binding
  -> Mass Assignment

Object Lookup
  -> IDOR / BOLA

Dynamic Code Evaluation
  -> Code Injection
```

This is a triage map, not a vulnerability guarantee.

---

# Quick Source Reference

```text
HTTP Query
HTTP Path
HTTP Body
JSON
XML
Headers
Cookies
Files
WebSocket Messages
GraphQL Arguments
gRPC Messages
Webhooks
Message Queues
Third-Party APIs
Stored User Data
```

Any of these may become attacker-controlled depending on the architecture.

---

# Vulnerability Review Matrix

| Vulnerability | Primary Source Review Question |
|---|---|
| SQL Injection | Can untrusted data alter SQL syntax? |
| NoSQL Injection | Can untrusted data alter NoSQL query semantics? |
| LDAP Injection | Can untrusted data alter LDAP filters? |
| Command Injection | Can untrusted data influence shell/command execution? |
| SSTI | Can untrusted data become template source? |
| XSS | Can untrusted data reach an unsafe output context? |
| SSRF | Can untrusted data control a server-side destination? |
| Path Traversal | Can untrusted data influence filesystem paths? |
| File Upload | Can attacker-controlled files be stored or processed unsafely? |
| XXE | Can attacker-controlled XML reach an unsafe parser? |
| Deserialisation | Can attacker-controlled serialized data reach dangerous object construction? |
| IDOR / BOLA | Is object access restricted to authorised users? |
| Mass Assignment | Can users bind security-sensitive object properties? |
| Open Redirect | Can users control redirect destinations? |
| CSRF | Can authenticated state-changing actions be triggered cross-site? |
| CORS | Can untrusted origins read sensitive responses? |
| Authentication | Can identity verification be bypassed or abused? |
| Authorisation | Can users perform unauthorised actions? |
| Session Management | Can sessions be stolen, fixed, reused or remain valid incorrectly? |
| JWT | Are tokens generated and validated securely? |
| OAuth/OIDC | Are authorization flows and tokens validated correctly? |
| SAML | Are assertions and protocol fields validated correctly? |
| Business Logic | Can valid functions be combined or manipulated unexpectedly? |
| Race Conditions | Can concurrent operations violate security assumptions? |
| Rate Limiting | Can sensitive operations be automated excessively? |
| Secrets Exposure | Are usable secrets exposed in code/config/history? |
| Dependency Security | Are vulnerable or unsupported components reachable? |

---

# Technology-Specific Notes

The following pages provide language and framework-specific review guidance.

---

## .NET / ASP.NET Core

[.NET / ASP.NET Core Source Code Review](dotnet.md)

Topics include:

```text
ASP.NET Core routes
Controllers
Minimal APIs
Authentication
Authorisation
Entity Framework
ADO.NET
Dapper
Process execution
HttpClient
File APIs
Serialization
Razor
Configuration
Secrets
```

---

## Java / Spring

```text
docs/source-code-review/java.md
```

Topics include:

```text
Spring MVC
Spring Boot
Servlets
Controllers
Spring Security
JDBC
JPA
Hibernate
ProcessBuilder
Runtime.exec
HTTP clients
XML parsers
Serialization
Templates
```

---

## PHP

```text
docs/source-code-review/php.md
```

Topics include:

```text
Superglobals
Routing
PDO
MySQLi
Command execution
File inclusion
File operations
unserialize()
Sessions
Headers
Templates
Framework patterns
```

---

## Python

```text
docs/source-code-review/python.md
```

Topics include:

```text
Python security primitives
subprocess
os.system
pickle
YAML
File operations
HTTP clients
eval
exec
Cryptography
Dependencies
```

---

## Django

```text
docs/source-code-review/django.md
```

Topics include:

```text
URLs
Views
Middleware
Authentication
Permissions
ORM
RawSQL
Templates
CSRF
File uploads
Redirects
Settings
```

---

## Flask

```text
docs/source-code-review/flask.md
```

Topics include:

```text
Routes
Blueprints
request
Sessions
Jinja
render_template_string
SQLAlchemy
Redirects
File handling
Configuration
Extensions
```

---

## Node.js / Express

```text
docs/source-code-review/nodejs.md
```

Topics include:

```text
Express routes
Middleware
req.query
req.params
req.body
Authentication
Authorisation
Database access
child_process
Filesystem APIs
HTTP clients
Templates
Prototype pollution
Dependencies
```

---

## Client-Side JavaScript

```text
docs/source-code-review/javascript.md
```

Topics include:

```text
DOM sources
DOM sinks
postMessage
location
Web Storage
innerHTML
document.write
eval
Dynamic script loading
Prototype pollution
Third-party JavaScript
Client-side routing
```

---

# Recommended Review Order

For an unfamiliar application:

```text
Repository Structure
        |
        v
Technology Stack
        |
        v
Routes
        |
        v
Authentication
        |
        v
Authorisation
        |
        v
Sources
        |
        v
Sensitive Business Logic
        |
        v
Dangerous Sinks
        |
        v
Source-to-Sink Tracing
        |
        v
Configuration
        |
        v
Secrets
        |
        v
Dependencies
        |
        v
Static Analysis
        |
        v
Variant Analysis
        |
        v
Dynamic Validation
```

---

# Final Source Code Review Model

The complete methodology can be reduced to five questions:

```text
1. WHERE CAN AN ATTACKER ENTER DATA?

                  SOURCE

                     |
                     v

2. WHERE DOES THAT DATA GO?

                 DATA FLOW

                     |
                     v

3. WHAT SECURITY CONTROLS DOES IT CROSS?

        VALIDATION
        SANITISATION
        ENCODING
        AUTHENTICATION
        AUTHORISATION

                     |
                     v

4. WHAT SECURITY-SENSITIVE OPERATION DOES IT REACH?

                   SINK

                     |
                     v

5. WHAT CAN AN ATTACKER ACTUALLY ACHIEVE?

                  IMPACT
```

Or:

```text
SOURCE
   |
   v
DATA FLOW
   |
   v
SECURITY CONTROLS
   |
   v
SINK
   |
   v
EXPLOITABILITY
   |
   v
IMPACT
```

The most important rule is:

```text
Search results identify code.

Data-flow analysis identifies candidates.

Security-control analysis determines whether the path is protected.

Dynamic validation demonstrates behaviour.

Impact determines whether there is a vulnerability worth reporting.
```

---

# Source Code Review Checklist

```text
[ ] Repository structure understood
[ ] Languages identified
[ ] Frameworks identified
[ ] Routes mapped
[ ] Entry points mapped
[ ] Authentication mapped
[ ] Authorisation mapped
[ ] Roles mapped
[ ] Tenant boundaries mapped
[ ] User-controlled sources mapped
[ ] Input validation reviewed
[ ] SQL sinks reviewed
[ ] NoSQL sinks reviewed
[ ] LDAP sinks reviewed
[ ] Command sinks reviewed
[ ] Template sinks reviewed
[ ] File sinks reviewed
[ ] HTTP/network sinks reviewed
[ ] XML parsers reviewed
[ ] Deserialisation reviewed
[ ] HTML/DOM sinks reviewed
[ ] Redirects reviewed
[ ] Mass assignment reviewed
[ ] IDOR/BOLA reviewed
[ ] Business logic reviewed
[ ] Race conditions considered
[ ] Rate limiting reviewed
[ ] Session management reviewed
[ ] JWT reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
[ ] File uploads reviewed
[ ] GraphQL reviewed where present
[ ] gRPC reviewed where present
[ ] WebSockets reviewed where present
[ ] CORS reviewed
[ ] CSRF reviewed
[ ] Security headers reviewed
[ ] Error handling reviewed
[ ] Logging reviewed
[ ] Cryptography reviewed
[ ] Randomness reviewed
[ ] Secrets searched
[ ] Dependencies reviewed
[ ] Configuration reviewed
[ ] Git history reviewed
[ ] Static analysis performed where useful
[ ] Variant analysis performed
[ ] Candidate findings manually validated
[ ] Dynamic validation performed where authorised
[ ] Findings based on demonstrated security impact
```

---

# References

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Application Security Verification Standard

[OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP Top 10

[OWASP Top 10](https://owasp.org/www-project-top-ten/){ target="_blank" rel="noopener noreferrer" }

---

## OWASP API Security Project

[OWASP API Security Project](https://owasp.org/www-project-api-security/){ target="_blank" rel="noopener noreferrer" }

---

## CWE

[CWE](https://cwe.mitre.org/){ target="_blank" rel="noopener noreferrer" }

---

## Semgrep

[Semgrep](https://semgrep.dev/){ target="_blank" rel="noopener noreferrer" }

---

## Semgrep Documentation

[docs](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

---

## CodeQL

[CodeQL](https://codeql.github.com/){ target="_blank" rel="noopener noreferrer" }

---

## CodeQL Documentation

[docs](https://codeql.github.com/docs/){ target="_blank" rel="noopener noreferrer" }

---

## GitHub CodeQL

[GitHub CodeQL](https://github.com/github/codeql){ target="_blank" rel="noopener noreferrer" }

---

## ripgrep

[ripgrep](https://github.com/BurntSushi/ripgrep){ target="_blank" rel="noopener noreferrer" }

---

# Related Notes

```text
docs/web/index.md
docs/web/methodology.md
docs/web/checklist.md
docs/web/attack-surface-analysis.md
docs/web/input-validation.md

docs/web/authentication.md
docs/web/authorisation.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/mfa.md
docs/web/idor-bola.md

docs/web/sql-injection.md
docs/web/nosql-injection.md
docs/web/ldap-injection.md
docs/web/command-injection.md
docs/web/ssti.md
docs/web/xxe.md

docs/web/xss.md
docs/web/dom-based-vulnerabilities.md
docs/web/html-injection.md
docs/web/csrf.md
docs/web/cors.md
docs/web/open-redirect.md

docs/web/ssrf.md
docs/web/path-traversal.md
docs/web/file-inclusion.md
docs/web/file-upload.md
docs/web/deserialization.md

docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/rate-limiting.md

docs/web/jwt.md
docs/web/oauth-oidc.md
docs/web/saml.md

docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md
docs/web/mass-assignment.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md
docs/web/information-disclosure.md
docs/web/http-security-headers.md
```
