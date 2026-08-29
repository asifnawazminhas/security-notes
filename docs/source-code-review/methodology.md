# Source Code Review Methodology

Source code review is the systematic examination of an application's source code to identify security weaknesses that may not be visible through black-box testing alone.

Unlike traditional penetration testing, where the application is primarily analysed from the outside, source code review allows the reviewer to examine how the application actually processes data internally.

This makes it possible to answer questions such as:

```text
Where are the application entry points?

Where does user-controlled input enter the application?

Where is authentication implemented?

Where is authorisation enforced?

Where is input validated?

Where are database queries constructed?

Where are operating system commands executed?

Where are files accessed?

Where are outbound HTTP requests made?

Where are templates rendered?

Where are objects deserialised?

Where are secrets stored?

Where are security-sensitive operations performed?

Can attacker-controlled data reach those operations?
```

The fundamental methodology is:

```text
SOURCE
  |
  v
USER-CONTROLLED INPUT
  |
  v
TRANSFORMATIONS
  |
  +-- validation
  +-- parsing
  +-- decoding
  +-- normalisation
  +-- sanitisation
  +-- business logic
  +-- authorisation
  |
  v
SINK
  |
  v
SECURITY-SENSITIVE OPERATION
```

Examples:

```text
HTTP Parameter
     |
     v
Controller
     |
     v
Service
     |
     v
Repository
     |
     v
SQL Query
```

or:

```text
JSON Body
    |
    v
API Controller
    |
    v
URL Builder
    |
    v
HTTP Client
    |
    v
External Request
```

or:

```text
Path Parameter
     |
     v
Controller
     |
     v
Database Lookup
     |
     v
Object Returned
```

The final example may represent an IDOR / BOLA vulnerability if ownership or authorisation is not verified.

The core principle is:

```text
grep match
    !=
vulnerability
```

Similarly:

```text
Sink found
    !=
Vulnerability found
```

A candidate normally becomes a confirmed vulnerability only when the reviewer establishes:

```text
Attacker-controlled source
        +
Reachable data flow
        +
Security-sensitive sink
        +
Missing or ineffective security control
        +
Meaningful security impact
```

!!! warning "Authorised Security Testing"
    Perform source code review only against applications, repositories and environments for which you have explicit authorisation. Dynamic validation should be performed only within the agreed scope and rules of engagement.

---

# Objectives

A security-focused source code review should attempt to understand:

```text
Application architecture
Attack surface
Entry points
Trust boundaries
Authentication
Authorisation
Session management
Input validation
Data flows
Dangerous sinks
Business logic
External integrations
Secrets
Dependencies
Security configuration
Logging
Error handling
Cryptography
Concurrency
Background processing
```

The objective is not simply to search for dangerous functions.

The objective is to understand:

```text
How does attacker-controlled data move through the application?
```

---

# Source Code Review Workflow

A practical review can follow this process:

```text
1. Prepare the review environment

2. Identify the technology stack

3. Understand the project structure

4. Build the application where possible

5. Identify configuration

6. Identify routes and entry points

7. Identify authentication

8. Identify authorisation

9. Identify user-controlled input

10. Identify validation and sanitisation

11. Identify dangerous sinks

12. Trace sources to sinks

13. Trace sinks back to sources

14. Identify trust boundaries

15. Review business logic

16. Review security controls

17. Review secrets and configuration

18. Review dependencies

19. Review background processing

20. Review external integrations

21. Run static-analysis tools

22. Perform variant analysis

23. Dynamically validate candidates

24. Document evidence

25. Report confirmed findings
```

This can be visualised as:

```text
Repository
    |
    v
Technology Identification
    |
    v
Architecture Mapping
    |
    v
Attack Surface Mapping
    |
    v
Entry Point Discovery
    |
    v
Source Discovery
    |
    v
Sink Discovery
    |
    v
Data Flow Analysis
    |
    v
Security Control Analysis
    |
    v
Exploitability Validation
    |
    v
Variant Analysis
    |
    v
Reporting
```

---

# Review Types

Source code review can generally be performed in two ways.

## Baseline Review

A baseline review examines the application broadly.

Useful when:

```text
Reviewing a new application
Performing a full security assessment
Reviewing a legacy application
Reviewing an unfamiliar codebase
Establishing an initial security baseline
```

The reviewer attempts to understand the entire application architecture and attack surface.

---

# Diff-Based Review

A diff-based review focuses on changes.

Examples:

```text
Pull request
Commit
Feature branch
Release
Security patch
Hotfix
```

Useful commands:

```bash
git diff
```

Compare branches:

```bash
git diff main..feature
```

Changed files:

```bash
git diff --name-only main..feature
```

Security review then concentrates on:

```text
New entry points
Changed authentication
Changed authorisation
New sinks
Changed validation
New dependencies
New external integrations
Changed configuration
```

---

# Hybrid Review

A hybrid approach combines:

```text
Baseline understanding
        +
Diff-focused investigation
```

This is often useful during continuous security review.

---

# Visual Studio Code as the Review IDE

Visual Studio Code is a useful IDE for source code review because it provides:

```text
Repository-wide search
Regex search
Go to Definition
Go to References
Call hierarchy
Symbol navigation
Integrated terminal
Git integration
Debugging
Extensions
Multi-language support
```

The IDE does not replace manual analysis.

It makes navigation and data-flow tracing significantly easier.

---

# Open the Repository in Visual Studio Code

From a terminal:

```bash
code .
```

Or:

```bash
code /path/to/project
```

Before reviewing individual files, inspect the repository structure.

---

# Initial Repository View

The first objective is not finding vulnerabilities.

The first objective is answering:

```text
What am I looking at?
```

Look for:

```text
src/
app/
server/
client/
backend/
frontend/
controllers/
routes/
services/
repositories/
models/
entities/
templates/
static/
config/
middleware/
filters/
security/
tests/
```

Also identify build and dependency files.

---

# Technology Identification

Common files include:

## .NET

```text
*.sln
*.csproj
Program.cs
Startup.cs
appsettings.json
```

## Java

```text
pom.xml
build.gradle
build.gradle.kts
settings.gradle
application.properties
application.yml
```

## PHP

```text
composer.json
composer.lock
artisan
index.php
```

## Python

```text
requirements.txt
pyproject.toml
setup.py
Pipfile
```

## Django

```text
manage.py
settings.py
urls.py
wsgi.py
asgi.py
```

## Flask

```text
app.py
wsgi.py
requirements.txt
```

## Node.js

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
server.js
app.js
```

---

# VS Code Explorer

Use the Explorer panel to understand application organisation.

Do not immediately open random files.

Build a mental model:

```text
Application
│
├── Controllers
│
├── Services
│
├── Repositories
│
├── Models
│
├── Security
│
├── Configuration
│
├── Templates
│
└── Static Content
```

For example:

```text
src/
└── main/
    ├── java/
    │   └── com/example/app/
    │       ├── controller/
    │       ├── service/
    │       ├── repository/
    │       ├── security/
    │       └── model/
    │
    └── resources/
        ├── application.yml
        ├── templates/
        └── static/
```

This immediately tells the reviewer where different security controls are likely to exist.

---

# VS Code Global Search

One of the most useful source review features is repository-wide search.

Use:

```text
Ctrl + Shift + F
```

on Windows/Linux.

This searches across the repository.

Examples:

```text
Authorize
login
password
executeQuery
Process.Start
Runtime.exec
innerHTML
HttpClient
eval(
```

---

# Enable Regex Search

VS Code search supports regular expressions.

Enable the:

```text
.*
```

button in the Search panel.

Example:

```regex
exec\(|system\(|shell_exec\(
```

Another example:

```regex
innerHTML|outerHTML|document\.write
```

Another:

```regex
SELECT|INSERT|UPDATE|DELETE
```

Regex searching is extremely useful for sink discovery.

---

# Search File Types

VS Code allows searches to be limited to particular files.

Example:

```text
*.java
```

or:

```text
*.cs
```

or:

```text
*.php
```

or:

```text
*.py
```

or:

```text
*.js
```

---

# Include Patterns

Example:

```text
src/**/*.java
```

This limits the search scope.

---

# Exclude Patterns

Exclude directories such as:

```text
node_modules
vendor
dist
build
target
bin
obj
```

Example VS Code exclude pattern:

```text
**/node_modules/**,**/vendor/**,**/dist/**,**/build/**,**/target/**
```

This reduces noise.

---

# VS Code Go to Definition

When a function is called:

```java
userService.getUser(id);
```

use:

```text
F12
```

or:

```text
Right-click
    ->
Go to Definition
```

This allows the reviewer to follow the implementation.

Example:

```text
Controller
    |
    v
userService.getUser()
    |
    v
UserService.getUser()
```

---

# Peek Definition

Use:

```text
Alt + F12
```

to inspect a function without leaving the current file.

This is useful during data-flow analysis.

---

# Go to References

Place the cursor on a function or variable and use:

```text
Shift + F12
```

This identifies where the symbol is used.

Example:

```text
findUser()
    |
    +-- UserController
    |
    +-- AdminController
    |
    +-- PasswordResetService
    |
    +-- ExportService
```

This is extremely useful for variant analysis.

---

# Find All References

Suppose a security-sensitive method exists:

```java
executeCommand()
```

Finding all references may reveal:

```text
Admin endpoint
Background job
API endpoint
Debug endpoint
Internal service
```

One vulnerable call site may indicate additional variants.

---

# Call Hierarchy

For supported languages and language servers, VS Code can display call relationships.

Use:

```text
Right-click
    ->
Show Call Hierarchy
```

Then inspect:

```text
Incoming Calls
Outgoing Calls
```

Conceptually:

```text
HTTP Controller
      |
      v
processRequest()
      |
      v
generateReport()
      |
      v
runConverter()
      |
      v
ProcessBuilder
```

Call hierarchy can make source-to-sink tracing significantly faster.

---

# Outline and Symbols

VS Code can display symbols such as:

```text
Classes
Methods
Functions
Properties
Interfaces
```

Use:

```text
Ctrl + Shift + O
```

to navigate symbols within the current file.

Use:

```text
Ctrl + T
```

to search workspace symbols.

This can quickly locate:

```text
LoginController
SecurityConfig
AuthService
UserRepository
FileService
HttpClientService
```

---

# Integrated Terminal

Open the VS Code terminal:

```text
Ctrl + `
```

This allows commands such as:

```bash
rg
git
semgrep
codeql
mvn
gradle
dotnet
npm
python
```

to be run without leaving the review environment.

---

# Recommended Review Layout

A useful VS Code layout is:

```text
+-------------------+-----------------------------+
|                   |                             |
| Explorer          | Source Code                 |
|                   |                             |
| Search            | Controller / Service        |
|                   |                             |
+-------------------+-----------------------------+
|                                                 |
| Integrated Terminal                             |
|                                                 |
+-------------------------------------------------+
```

During tracing:

```text
Left editor:
Controller

Right editor:
Service / Repository

Bottom:
ripgrep / Git / static analysis
```

Split editors can make multi-file data flow easier to understand.

---

# Stage 1 - Understand the Architecture

Before searching for vulnerabilities, identify:

```text
Application components
Framework
Database
Authentication mechanism
Session mechanism
External services
Message queues
Caches
File storage
Background jobs
APIs
```

Create a simple architecture model.

Example:

```text
Browser
   |
   v
Reverse Proxy
   |
   v
Web Application
   |
   +-----------> Database
   |
   +-----------> Redis
   |
   +-----------> File Storage
   |
   +-----------> External API
   |
   +-----------> Message Queue
```

---

# Identify Trust Boundaries

A trust boundary exists whenever data moves between components with different trust levels.

Example:

```text
Internet
   |
   | Trust Boundary
   v
Web Application
   |
   | Trust Boundary
   v
Database
```

Another:

```text
Web Application
      |
      | Trust Boundary
      v
Third-Party API
```

Another:

```text
User
  |
  v
Uploaded File
  |
  v
Background Processor
```

Trust boundaries are important because validation assumptions frequently fail at these transitions.

---

# Stage 2 - Build the Attack Surface

Create an inventory of externally reachable functionality.

Look for:

```text
HTTP routes
API endpoints
GraphQL
gRPC
WebSockets
File uploads
Webhooks
OAuth callbacks
SAML endpoints
Password reset
Authentication
Admin interfaces
Debug endpoints
Background job triggers
Message consumers
```

---

# Route Mapping

The exact patterns depend on the language.

Examples:

## ASP.NET Core

```text
[HttpGet]
[HttpPost]
[HttpPut]
[HttpPatch]
[HttpDelete]
[Route]
MapGet
MapPost
MapPut
MapDelete
```

## Spring

```text
@RequestMapping
@GetMapping
@PostMapping
@PutMapping
@PatchMapping
@DeleteMapping
```

## Django

```text
path(
re_path(
```

## Flask

```text
@app.route
@blueprint.route
```

## Express

```text
app.get(
app.post(
app.put(
app.patch(
app.delete(

router.get(
router.post(
```

---

# Route Inventory

Create a table during the review:

| Method | Route | Handler | Authentication | Authorisation | Input |
|---|---|---|---|---|---|
| GET | `/api/users/{id}` | `getUser()` | Yes | Review | Path |
| POST | `/api/users` | `createUser()` | Yes | Admin | JSON |
| POST | `/upload` | `upload()` | Yes | User | File |
| GET | `/redirect` | `redirect()` | No | N/A | Query |

This immediately exposes suspicious areas.

---

# Stage 3 - Identify Sources

A source is where potentially attacker-controlled data enters the program.

Common sources include:

```text
HTTP query parameters
Path parameters
POST bodies
JSON
XML
Headers
Cookies
File uploads
WebSocket messages
GraphQL arguments
gRPC messages
Message queues
Webhooks
Database data
Environment variables
Configuration
```

Not every source is directly attacker-controlled.

The reviewer must determine the trust boundary.

---

# HTTP Sources

Conceptually:

```text
GET /users?id=123
             |
             v
            id
```

The parameter:

```text
id
```

becomes a source.

---

# Headers as Sources

Examples:

```text
Host
X-Forwarded-Host
X-Forwarded-For
User-Agent
Referer
Origin
Custom headers
```

Headers should not automatically be considered trusted.

---

# Cookies as Sources

Cookies are also client-controlled from the server's perspective unless integrity protection or another security mechanism changes the trust model.

---

# File Upload Sources

Uploaded files contain multiple attacker-controlled properties:

```text
Filename
Content
MIME type
Size
Extension
Metadata
Archive contents
```

---

# Database Data as a Source

A common mistake is assuming:

```text
Database data = trusted
```

This is not always true.

Example:

```text
Attacker Input
     |
     v
Database
     |
     v
Background Job
     |
     v
Command Execution
```

This is a second-order data flow.

---

# Stage 4 - Identify Sinks

A sink is a security-sensitive operation.

High-value categories include:

```text
Database queries
Operating system commands
HTML output
Template rendering
File operations
Network requests
Deserialisation
XML parsing
Dynamic code execution
Redirects
Logging
Cryptographic operations
Authentication decisions
Authorisation decisions
```

---

# SQL Sinks

Examples:

```text
executeQuery
executeUpdate
SqlCommand
FromSqlRaw
createNativeQuery
mysqli_query
PDO::query
cursor.execute
```

The existence of one of these functions does not prove SQL injection.

The query construction must be examined.

---

# Command Execution Sinks

Examples:

```text
Runtime.exec
ProcessBuilder
Process.Start
system
exec
shell_exec
subprocess
os.system
child_process.exec
```

---

# File Sinks

Examples:

```text
File.Open
File.ReadAllText
Files.readString
open()
fopen()
fs.readFile
```

Potential vulnerabilities include:

```text
Path traversal
Arbitrary file read
Arbitrary file write
Unsafe archive extraction
File inclusion
```

---

# Network Sinks

Examples:

```text
HttpClient
WebClient
RestClient
WebClient
requests
urllib
curl
axios
fetch
```

Potential issue:

```text
SSRF
```

---

# HTML Sinks

Examples:

```text
innerHTML
outerHTML
document.write
th:utext
Raw
Html.Raw
```

Potential issue:

```text
XSS
HTML Injection
```

---

# Deserialisation Sinks

Examples:

```text
ObjectInputStream
BinaryFormatter
pickle.loads
unserialize
```

The exact risk depends on:

```text
Format
Library
Configuration
Trust boundary
Available types
Application version
```

---

# Stage 5 - Source-to-Sink Analysis

Source-to-sink analysis follows attacker-controlled data forward through the application.

Example:

```text
HTTP Request
     |
     v
request.getParameter("name")
     |
     v
name
     |
     v
buildQuery(name)
     |
     v
executeQuery()
```

The reviewer should ask at every step:

```text
Is the value still attacker-controlled?

Was it validated?

Was it normalised?

Was it encoded?

Was it parameterised?

Was authorisation performed?

Did the data change context?
```

---

# Example - SQL Injection Analysis

Candidate:

```java
String id =
    request.getParameter("id");

String sql =
    "SELECT * FROM users WHERE id = "
    + id;

statement.executeQuery(sql);
```

Trace:

```text
request.getParameter("id")
          |
          v
         id
          |
          v
String Concatenation
          |
          v
         sql
          |
          v
executeQuery()
```

Candidate vulnerability:

```text
SQL Injection
```

---

# Safe SQL Comparison

Example:

```java
PreparedStatement statement =
    connection.prepareStatement(
        "SELECT * FROM users WHERE id = ?"
    );

statement.setString(
    1,
    id
);
```

The same source exists:

```text
id
```

and the same database operation exists.

But the security control changes the analysis:

```text
Attacker Input
      |
      v
Prepared Statement Parameter
      |
      v
SQL Engine
```

---

# Stage 6 - Reverse Sink Analysis

For large applications, starting from every source may be inefficient.

Instead:

```text
Find dangerous sink
        |
        v
Trace backwards
        |
        v
Determine data origin
```

Example:

```text
ProcessBuilder
      ^
      |
executeCommand()
      ^
      |
generateReport()
      ^
      |
ReportController
      ^
      |
HTTP Parameter
```

This is called reverse sink analysis.

---

# Why Reverse Sink Analysis Works

Applications may contain:

```text
Thousands of inputs
```

but only:

```text
A small number of command execution functions
A small number of raw SQL functions
A small number of deserialisation functions
A small number of outbound HTTP clients
```

Searching sinks first can therefore be very efficient.

---

# Recommended Combination

Use both:

```text
SOURCE -> SINK
```

and:

```text
SINK -> SOURCE
```

The combination provides better coverage.

---

# Stage 7 - Follow Transformations

Data rarely moves directly from source to sink.

Example:

```text
Request
  |
  v
Controller
  |
  v
DTO
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

Each transformation must be reviewed.

---

# Example

```java
@GetMapping("/search")
public ResponseEntity<?> search(
    @RequestParam String q
) {
    return service.search(q);
}
```

Then:

```java
public List<User> search(
    String q
) {
    String filter =
        prepareFilter(q);

    return repository.search(
        filter
    );
}
```

Then:

```java
private String prepareFilter(
    String input
) {
    return input.trim();
}
```

Then:

```java
entityManager
    .createNativeQuery(
        "SELECT * FROM users WHERE name = '"
        + filter
        + "'"
    );
```

`trim()` does not remove attacker control.

Flow:

```text
q
 |
 v
trim()
 |
 v
filter
 |
 v
SQL concatenation
```

---

# Sanitisation Must Match the Sink

A critical principle:

```text
Sanitisation is context-specific.
```

Examples:

```text
HTML escaping
    !=
SQL parameterisation

URL validation
    !=
Command argument safety

SQL escaping
    !=
LDAP escaping
```

A transformation that is safe for one sink may be irrelevant for another.

---

# Stage 8 - Authentication Review

Locate:

```text
Login
Logout
Session creation
Token creation
Password validation
Identity providers
JWT validation
OAuth
OIDC
SAML
MFA
```

Search:

```bash
rg -n -i \
'login|logout|authenticate|authentication|password|jwt|oauth|oidc|saml|mfa|totp' \
.
```

---

# Authentication Flow

Map:

```text
Credentials
    |
    v
Login Endpoint
    |
    v
Credential Validation
    |
    v
Session / Token Creation
    |
    v
Authenticated Request
```

Questions:

```text
How are credentials validated?

How are passwords stored?

How are sessions created?

How are tokens signed?

How are tokens validated?

How does logout work?

Is MFA enforced?

Are alternate login flows protected?
```

---

# Stage 9 - Authorisation Review

Authentication asks:

```text
Who are you?
```

Authorisation asks:

```text
Are you allowed to perform this action?
```

These must be reviewed separately.

---

# Authorisation Mapping

For every sensitive route, identify:

```text
Authentication required?
Role required?
Permission required?
Object ownership checked?
Tenant checked?
```

Example:

```text
GET /api/users/123
       |
       v
Authenticated User
       |
       v
findById(123)
       |
       v
Return User
```

Missing step:

```text
Does authenticated user have permission
to access user 123?
```

---

# IDOR / BOLA Review

Search object lookups:

```text
findById
getById
findOne
getUser
getAccount
getOrder
getDocument
```

Then inspect whether the application checks:

```text
Ownership
Tenant
Organisation
Role
Permission
Relationship
```

---

# Secure Pattern

Conceptually:

```text
Object Requested
      |
      v
Object Loaded
      |
      v
Ownership / Permission Check
      |
      +-- Denied
      |
      +-- Allowed
             |
             v
          Response
```

---

# Stage 10 - Input Validation

Locate:

```text
Validators
Schemas
DTO constraints
Regex checks
Type validation
Length limits
Allowlist validation
```

Remember:

```text
Validation
    !=
Authorisation
```

and:

```text
Validation
    !=
Output Encoding
```

and:

```text
Validation
    !=
SQL Parameterisation
```

Each solves a different problem.

---

# Validation Location

Review whether validation occurs:

```text
Client side
Server side
Controller
Service
Domain layer
Database
```

Client-side validation must not be treated as a server-side security boundary.

---

# Stage 11 - Business Logic

Automated tools are particularly weak at identifying business logic vulnerabilities.

Examples:

```text
Negative quantities
Repeated refunds
Coupon reuse
Workflow bypass
Order state manipulation
Privilege transitions
Account linking
Approval bypass
Payment race conditions
Invitation abuse
Tenant switching
```

---

# Model the State Machine

Example:

```text
Created
   |
   v
Approved
   |
   v
Paid
   |
   v
Shipped
```

Ask:

```text
Can Created become Shipped directly?

Can Paid become Created?

Can Approved be skipped?

Can an action be repeated?
```

---

# Business Invariants

Identify rules such as:

```text
Balance cannot become negative

A refund cannot exceed payment

Only an owner can delete a resource

An invitation can only be used once

An MFA challenge must precede sensitive action

An order can only be shipped after payment
```

Then find where these rules are enforced.

---

# Stage 12 - Mass Assignment

Look for:

```text
Request Body
      |
      v
Automatic Object Binding
      |
      v
Database Entity
```

Example attacker-controlled fields:

```text
role
isAdmin
balance
ownerId
tenantId
verified
status
```

Prefer explicit DTOs and explicit mapping for security-sensitive models.

---

# Stage 13 - SSRF

Find outbound network clients.

Search examples:

```bash
rg -n \
'HttpClient|WebClient|RestTemplate|RestClient|requests\.|urllib|axios|fetch\(' \
.
```

Then trace:

```text
User Input
    |
    v
URL Construction
    |
    v
HTTP Client
```

Review:

```text
Scheme
Hostname
Port
Redirects
DNS resolution
Internal addresses
Cloud metadata
Egress controls
```

---

# Stage 14 - Command Injection

Search:

```bash
rg -n \
'Process\.Start|ProcessBuilder|Runtime\.getRuntime|os\.system|subprocess|child_process|shell_exec|system\(' \
.
```

Then determine whether attacker-controlled input reaches:

```text
Command
Executable
Arguments
Shell
Working directory
Environment
```

---

# Shell Boundary

A useful distinction is:

```text
Program + argument array
```

versus:

```text
Shell command string
```

Example:

```text
/bin/sh -c
cmd.exe /c
powershell -Command
bash -c
```

Shell invocation substantially changes parsing behaviour and should receive additional scrutiny.

---

# Stage 15 - File Operations

Search for:

```text
File reads
File writes
Path construction
Archive extraction
Uploads
Downloads
Temporary files
```

Data flow:

```text
User Filename
     |
     v
Path Construction
     |
     v
File Read
```

Potential:

```text
Path Traversal
```

---

# Path Normalisation

Do not assume:

```text
Path.Combine
Path.resolve
Paths.get
```

automatically prevents traversal.

Review whether the final canonical or normalised path is constrained to the intended base directory.

Conceptually:

```text
Requested Path
      |
      v
Resolve
      |
      v
Normalise
      |
      v
Check Base Boundary
      |
      +-- Outside -> Reject
      |
      +-- Inside -> Continue
```

---

# Stage 16 - File Upload Review

Trace:

```text
Multipart Request
      |
      v
Uploaded File
      |
      +-- Filename
      +-- Content
      +-- MIME Type
      +-- Size
      |
      v
Validation
      |
      v
Storage
```

Review:

```text
Extension
Content
MIME type
Filename
Storage location
Generated filenames
Permissions
Web accessibility
Archive extraction
Downstream processing
```

---

# Stage 17 - Deserialisation

Search for deserialisation APIs.

Then determine:

```text
What data format is used?

Who controls the data?

Which types can be created?

Is polymorphism enabled?

Are dangerous classes available?

Are integrity controls present?
```

Do not report:

```text
ObjectMapper.readValue()
```

or similar generic parsing APIs as inherently insecure.

Configuration and trust boundaries matter.

---

# Stage 18 - XML Parsing

Search for:

```text
XML parsers
Document builders
SAX
DOM
XMLReader
XMLInputFactory
lxml
XMLDecoder
```

Review:

```text
External entities
DTD processing
Network access
Parser configuration
Library version
```

Do not assume parser defaults without verifying the exact runtime and configuration.

---

# Stage 19 - Template Rendering

Find:

```text
Template engines
Dynamic template names
Template strings
Expression engines
```

Distinguish:

```text
Attacker-controlled template data
```

from:

```text
Attacker-controlled template source
```

The latter is much more likely to create SSTI.

---

# Stage 20 - XSS and Output Handling

Trace:

```text
User Input
    |
    v
Stored / Processed
    |
    v
Output
    |
    v
HTML Context
```

Review context:

```text
HTML
Attribute
JavaScript
CSS
URL
```

Encoding must match the output context.

---

# Stage 21 - Redirects

Search:

```text
redirect
RedirectView
sendRedirect
Response.Redirect
location.href
```

Trace whether attacker-controlled data determines the destination.

Prefer:

```text
Internal identifiers
Relative paths
Explicit allowlists
Parsed origin checks
```

rather than fragile string matching.

---

# Stage 22 - Host Header and Proxy Trust

Search:

```text
Host
X-Forwarded-Host
X-Forwarded-Proto
X-Forwarded-For
Forwarded
```

Determine whether these values influence:

```text
Password reset URLs
OAuth URLs
Absolute links
Security decisions
Redirects
```

Also review proxy trust configuration.

---

# Stage 23 - Secrets

Search:

```bash
rg -n -i \
'password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key|client[_-]?secret' \
.
```

Also inspect:

```text
.env
appsettings.json
application.yml
application.properties
config files
Docker files
CI/CD files
Kubernetes manifests
Terraform
Source maps
Tests
Example configuration
```

A string called:

```text
password
```

does not prove credential exposure.

Determine whether the value is real, sensitive and usable.

---

# Git History

Deleted secrets may remain in Git history.

Useful commands:

```bash
git log --all --oneline
```

Search historical changes:

```bash
git log -p
```

Search commits affecting a file:

```bash
git log -p -- path/to/file
```

Search commits that added or removed a string:

```bash
git log -S 'password' -p
```

Use Git history review only where repository history is within scope.

---

# Stage 24 - Dependencies

Identify manifests:

```text
pom.xml
build.gradle
*.csproj
packages.lock.json
composer.json
composer.lock
requirements.txt
pyproject.toml
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
```

Review:

```text
Direct dependencies
Transitive dependencies
Versions
Unsupported packages
Known vulnerabilities
Dependency sources
Build scripts
Install hooks
```

---

# Dependency Finding Validation

Do not report:

```text
Library X appears in manifest
```

as a vulnerability without considering:

```text
Installed version
Reachability
Affected component
Vulnerable functionality
Mitigations
Deployment context
```

---

# Stage 25 - Logging

Search:

```bash
rg -n \
'log\.|logger\.|Console\.Write|console\.log|print\(' \
.
```

Review whether logs contain:

```text
Passwords
Tokens
Session IDs
API keys
Personal data
Sensitive business data
```

Also consider log forging when attacker-controlled data is written to structured or security-sensitive logs.

---

# Stage 26 - Error Handling

Search:

```text
catch
except
Exception
stack trace
error
debug
```

Review whether errors expose:

```text
Stack traces
Filesystem paths
SQL
Secrets
Internal hosts
Source code
Configuration
```

---

# Stage 27 - Cryptography

Search for:

```text
Cipher
MessageDigest
Hash
AES
DES
RSA
Random
SecureRandom
PBKDF
bcrypt
scrypt
Argon
```

Review:

```text
Algorithm
Mode
Key length
Key generation
Key storage
Nonce / IV
Authentication
Password hashing
Randomness
```

Avoid simple pattern-based conclusions.

For example:

```text
MD5 found
```

does not automatically mean a vulnerability.

Determine what it is used for.

---

# Stage 28 - Race Conditions

Identify operations involving:

```text
Balances
Inventory
Coupons
Tokens
Invitations
Password resets
MFA
Payments
Reservations
Counters
State transitions
```

Look for:

```text
Read
 |
 v
Check
 |
 v
Modify
 |
 v
Write
```

without atomic enforcement.

---

# TOCTOU Pattern

```text
Check
  |
  | Time Gap
  v
Use
```

Another request may change the state between the two operations.

Review:

```text
Transactions
Locks
Atomic operations
Unique constraints
Optimistic locking
Pessimistic locking
Idempotency
```

Absence of an obvious lock does not automatically prove a race condition.

---

# Stage 29 - Background Processing

Security review should not stop at HTTP controllers.

Search:

```text
Scheduled jobs
Workers
Queues
Consumers
Event handlers
Cron jobs
Async jobs
```

Potential data flow:

```text
HTTP Request
     |
     v
Database
     |
     v
Queue
     |
     v
Worker
     |
     v
Dangerous Sink
```

This is a common second-order flow.

---

# Stage 30 - Message Queues

Identify:

```text
Kafka
RabbitMQ
JMS
SQS
Azure Service Bus
Redis queues
Celery
Bull
```

Questions:

```text
Who can produce messages?

Are messages trusted?

Are fields validated?

Can messages trigger privileged actions?

Can messages reach dangerous sinks?
```

---

# Stage 31 - Webhooks

Search:

```text
webhook
callback
signature
HMAC
event
```

Review:

```text
Authentication
Signature verification
Replay protection
Event type validation
Authorisation
Destination URLs
```

---

# Stage 32 - Caching

Search:

```text
Cache
Redis
MemoryCache
@Cacheable
cache.get
cache.set
```

Review cache keys.

Example:

```text
cache["profile:" + userId]
```

Ask whether the key includes all required security context:

```text
User
Tenant
Organisation
Permission
Locale
```

Missing identity dimensions can cause cross-user or cross-tenant data exposure.

---

# Stage 33 - API Review

For APIs identify:

```text
Routes
Methods
Authentication
Authorisation
Object identifiers
Schemas
Rate limiting
Mass assignment
Error handling
Versioning
```

Create:

| Endpoint | Auth | Authz | Object | Input | Sink |
|---|---|---|---|---|---|
| `/api/users/{id}` | Yes | Review | User | ID | DB |
| `/api/import` | Yes | Admin | File | Upload | Parser |
| `/api/fetch` | Yes | User | URL | JSON | HTTP Client |

---

# Stage 34 - GraphQL

Search:

```text
Query
Mutation
Subscription
Resolver
DataFetcher
@QueryMapping
@MutationMapping
```

Map:

```text
GraphQL Operation
       |
       v
Resolver
       |
       v
Service
       |
       v
Repository
```

Review authorisation at resolver and service boundaries.

---

# Stage 35 - gRPC

Search:

```text
.proto
service
rpc
BindableService
```

Map:

```text
RPC
 |
 v
Handler
 |
 v
Service
 |
 v
Sink
```

Do not assume an RPC is internal merely because it uses gRPC.

---

# Stage 36 - WebSockets

Identify:

```text
Connection authentication
Message handlers
Channel subscriptions
Object identifiers
Server-side authorisation
```

Map:

```text
WebSocket Message
       |
       v
Message Handler
       |
       v
Business Logic
       |
       v
Sensitive Operation
```

---

# Stage 37 - Rate Limiting

Look for controls around:

```text
Login
Password reset
MFA
OTP
Registration
Invitation
Search
Expensive APIs
Messaging
Payments
```

Rate limiting may exist outside application source code.

For example:

```text
Reverse proxy
API gateway
WAF
Cloud service
Load balancer
```

Therefore:

```text
No rate-limit code found
```

does not prove:

```text
No rate limiting exists
```

---

# Stage 38 - Static Analysis

Manual review should be complemented with automated analysis.

Useful tools include:

```text
ripgrep
Semgrep
CodeQL
Language-specific SAST
Dependency scanners
Secret scanners
```

Automated results are candidate generators.

They are not automatically confirmed vulnerabilities.

---

# ripgrep

`ripgrep` is extremely useful during manual review.

Basic search:

```bash
rg -n 'pattern' .
```

Case-insensitive:

```bash
rg -ni 'password' .
```

File type:

```bash
rg -n 'executeQuery' -g '*.java' .
```

Multiple patterns:

```bash
rg -n \
'executeQuery|executeUpdate|ProcessBuilder|Runtime\.getRuntime' \
.
```

---

# Excluding Noise

Example:

```bash
rg -n \
'password|secret|token' \
. \
-g '!node_modules/**' \
-g '!vendor/**' \
-g '!dist/**' \
-g '!build/**'
```

---

# Search Routes

```bash
rg -n \
'HttpGet|HttpPost|HttpPut|HttpDelete|RequestMapping|GetMapping|PostMapping|app\.get|app\.post|router\.get|router\.post|@app\.route|path\(' \
.
```

---

# Search Authentication

```bash
rg -ni \
'authorize|authorise|authenticate|authentication|login|required|permission|role|jwt|oauth|oidc|saml' \
.
```

---

# Search SQL

```bash
rg -n \
'executeQuery|executeUpdate|SqlCommand|FromSqlRaw|ExecuteSqlRaw|createNativeQuery|mysqli_query|PDO|cursor\.execute|\.query\(' \
.
```

---

# Search Commands

```bash
rg -n \
'Runtime\.getRuntime|ProcessBuilder|Process\.Start|os\.system|subprocess|child_process|shell_exec|system\(' \
.
```

---

# Search Files

```bash
rg -n \
'File\.Read|File\.Open|Files\.read|FileInputStream|FileOutputStream|fopen|file_get_contents|open\(|fs\.readFile|fs\.writeFile' \
.
```

---

# Search SSRF Candidates

```bash
rg -n \
'HttpClient|WebClient|RestTemplate|RestClient|requests\.|urllib|urlopen|axios|fetch\(' \
.
```

---

# Search Deserialisation

```bash
rg -n \
'ObjectInputStream|readObject|BinaryFormatter|pickle\.loads|unserialize|XMLDecoder|yaml\.load' \
.
```

---

# Search XSS Sinks

```bash
rg -n \
'innerHTML|outerHTML|document\.write|Html\.Raw|th:utext|dangerouslySetInnerHTML|v-html' \
.
```

---

# Search Redirects

```bash
rg -n \
'redirect|RedirectView|sendRedirect|Response\.Redirect|location\.href' \
.
```

---

# Search Secrets

```bash
rg -ni \
'password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key|client[_-]?secret' \
.
```

---

# Semgrep

Semgrep can quickly identify security-relevant code patterns.

Basic scan:

```bash
semgrep --config=auto .
```

Depending on the installed Semgrep version, the equivalent command may also be exposed through the newer `semgrep scan` interface.

Always verify the current CLI syntax before incorporating it into automation.

Semgrep is useful for:

```text
Dangerous APIs
Injection candidates
Hard-coded secrets
Framework-specific patterns
Security anti-patterns
```

---

# Semgrep Review Workflow

```text
Semgrep Result
      |
      v
Open File in VS Code
      |
      v
Identify Source
      |
      v
Trace Data Flow
      |
      v
Inspect Security Controls
      |
      v
Determine Exploitability
```

---

# CodeQL

CodeQL is particularly useful for deeper:

```text
Data-flow analysis
Taint tracking
Variant analysis
Cross-function analysis
Security query development
```

Conceptually:

```text
SOURCE
   |
   v
Data Flow Graph
   |
   v
SINK
```

A CodeQL result should still be manually validated.

---

# CodeQL and VS Code

The CodeQL extension for Visual Studio Code can be useful for:

```text
Writing queries
Running queries
Viewing results
Exploring data-flow paths
Variant analysis
```

This is especially valuable after a vulnerability pattern has already been identified.

---

# Example Variant Analysis

Suppose manual review discovers:

```text
request parameter
      |
      v
buildCommand()
      |
      v
ProcessBuilder
```

Instead of stopping after one finding, search for:

```text
Every ProcessBuilder call
```

and:

```text
Every buildCommand() reference
```

Then identify similar flows.

---

# Variant Analysis Model

```text
Confirmed Vulnerability
        |
        v
Identify Root Pattern
        |
        v
Search Similar Sinks
        |
        v
Search Similar Sources
        |
        v
Search Similar Data Flows
        |
        v
Validate Variants
```

---

# VS Code Variant Analysis

Useful features:

```text
Find All References
Call Hierarchy
Global Search
Regex Search
Workspace Symbols
Git History
```

Example:

```text
Confirmed:
UserController -> UserService -> unsafeQuery()

Find All References:
unsafeQuery()
    |
    +-- UserController
    +-- AdminController
    +-- SearchController
    +-- ExportService
```

Each call site becomes a candidate.

---

# Stage 39 - Dynamic Validation

Static analysis should be combined with runtime validation where appropriate and authorised.

Example:

```text
Source Review
     |
     v
Potential SQL Injection
     |
     v
Identify Endpoint
     |
     v
Burp Repeater
     |
     v
Controlled Validation
```

Dynamic testing confirms assumptions that static review may not reveal.

---

# Static + Dynamic Testing

A strong workflow is:

```text
Source Code
    |
    v
Find Candidate
    |
    v
Understand Data Flow
    |
    v
Identify Endpoint
    |
    v
Burp Suite
    |
    v
Validate Behaviour
    |
    v
Return to Source
    |
    v
Identify Root Cause
```

---

# Burp Suite and VS Code Together

A practical setup:

```text
Browser
   |
   v
Burp Suite
   |
   v
Running Application

        +

Visual Studio Code
   |
   v
Source Repository
```

Use Burp to observe:

```text
Requests
Responses
Cookies
Headers
Parameters
Tokens
WebSockets
```

Use VS Code to determine:

```text
Where is this parameter handled?

Where is this token validated?

Where is this object loaded?

Where is this header trusted?

Where does this value reach?
```

---

# Example Workflow

Burp request:

```http
GET /api/users/123 HTTP/1.1
Host: application.example
Authorization: Bearer ...
```

VS Code search:

```text
/api/users
```

Find:

```java
@GetMapping("/api/users/{id}")
```

Follow:

```text
Controller
   |
   v
UserService
   |
   v
UserRepository.findById(id)
```

Then ask:

```text
Where is ownership checked?
```

If nowhere:

```text
Potential IDOR / BOLA
```

Then validate dynamically with authorised test accounts.

---

# Stage 40 - Debugging

When source and an authorised test environment are available, debugging can provide excellent visibility into data flows.

Useful breakpoint locations:

```text
Controller entry
Validation function
Authorisation function
Dangerous sink
Database query
HTTP client
File operation
```

---

# VS Code Breakpoints

Set a breakpoint by clicking next to the line number.

Then inspect:

```text
Variables
Call stack
Arguments
Return values
Object state
```

Example:

```text
HTTP Parameter
      |
      v
Breakpoint: Controller
      |
      v
Breakpoint: Service
      |
      v
Breakpoint: SQL Sink
```

This can confirm the exact runtime flow.

---

# Do Not Modify Evidence Accidentally

During a review, avoid unnecessary source modifications.

If testing requires modifications:

```text
Create a separate branch
```

or:

```text
Create a copy
```

Use:

```bash
git status
```

frequently.

This helps distinguish reviewer changes from original application code.

---

# Git Review

Useful commands:

```bash
git status
```

```bash
git log --oneline --all --decorate
```

```bash
git branch -a
```

```bash
git diff
```

```bash
git blame path/to/file
```

Git history can provide context for:

```text
Why a security control exists
When vulnerable code was introduced
Previous implementation
Removed secrets
Security patches
```

---

# Review Tests

Do not ignore:

```text
tests/
test/
spec/
integration-tests/
```

Tests can reveal:

```text
Expected security behaviour
Hidden routes
Test credentials
Role models
Object relationships
Business rules
Authentication assumptions
```

---

# Search TODO Comments

```bash
rg -ni \
'TODO|FIXME|HACK|XXX|temporary|remove before production|bypass' \
.
```

These are not vulnerabilities.

They can identify interesting review areas.

---

# Search Security Comments

```bash
rg -ni \
'security|auth|permission|role|admin|validate|sanitize|escape|trusted' \
.
```

Developer comments can reveal intended security assumptions.

Always verify the implementation rather than trusting the comment.

---

# Identify Security Boundaries

During review, mark important boundaries.

Example:

```text
[UNTRUSTED]
HTTP Request
     |
     v
Controller
     |
     v
[VALIDATION]
DTO Validator
     |
     v
Service
     |
     v
[AUTHORISATION]
Permission Check
     |
     v
Repository
     |
     v
[TRUSTED DATA STORE]
Database
```

This makes missing controls easier to identify.

---

# Review Data Context Changes

A value may be safe in one context and dangerous in another.

Example:

```text
Username
   |
   v
Database
   |
   v
HTML
```

Another:

```text
Filename
   |
   v
Database
   |
   v
Shell Command
```

Another:

```text
URL
 |
 v
Database
 |
 v
HTTP Client
```

Always ask:

```text
What security context is this value entering now?
```

---

# Second-Order Vulnerabilities

Second-order vulnerabilities occur when attacker-controlled data is stored and used later.

Example:

```text
Attacker
   |
   v
Profile Name
   |
   v
Database
   |
   v
Admin Dashboard
   |
   v
HTML Sink
```

Potential:

```text
Stored XSS
```

Another:

```text
Attacker Filename
      |
      v
Database
      |
      v
Nightly Job
      |
      v
Shell Command
```

Potential:

```text
Second-order command injection
```

---

# Security Control Inventory

Create a list of controls:

```text
Authentication middleware
Authorisation middleware
Input validators
Output encoding
CSRF protection
CORS configuration
Rate limiting
Security headers
Session configuration
Cryptographic helpers
Logging filters
File validators
URL validators
```

Then identify whether the controls are consistently applied.

---

# Inconsistent Security Controls

Example:

```text
Controller A
    |
    v
@Authorize
    |
    v
Sensitive Action

Controller B
    |
    v
No Authorisation
    |
    v
Same Sensitive Action
```

This is a common source of vulnerabilities.

---

# Security Control Bypass Paths

Look for alternate entry points.

Example:

```text
                   +--> Web Controller
                   |
Sensitive Service -+--> GraphQL Resolver
                   |
                   +--> Background Job
                   |
                   +--> WebSocket Handler
```

One path may have stronger controls than another.

---

# Entry Point Comparison

Example:

```text
REST API
    |
    +-- Authentication
    +-- Authorisation
    +-- Validation

GraphQL
    |
    +-- Authentication
    +-- ???
    +-- Validation
```

The missing control becomes a high-value review target.

---

# Review by Vulnerability Class

After architecture mapping, perform dedicated passes.

Recommended order:

```text
1. Authentication

2. Authorisation

3. IDOR / BOLA

4. Session Management

5. Input Validation

6. SQL Injection

7. NoSQL Injection

8. LDAP Injection

9. Command Injection

10. SSTI

11. SSRF

12. Path Traversal

13. File Upload

14. XXE

15. Deserialisation

16. XSS

17. HTML Injection

18. CSRF

19. CORS

20. Open Redirect

21. Host Header

22. Mass Assignment

23. Business Logic

24. Race Conditions

25. Rate Limiting

26. Secrets

27. Dependencies

28. Logging

29. Cryptography

30. APIs
```

---

# Prioritisation

Not every file deserves equal review time.

Prioritise code containing:

```text
Authentication
Authorisation
Admin functionality
Payments
File handling
Database queries
Command execution
Network requests
Deserialisation
Template rendering
Password reset
MFA
OAuth
SAML
JWT
Cryptography
Secrets
Background processing
```

---

# High-Risk File Names

Search:

```bash
find . -type f | grep -Ei \
'auth|security|admin|login|password|reset|upload|file|command|exec|payment|token|jwt|oauth|saml|webhook|crypto'
```

This is prioritisation only.

Do not assume file names determine vulnerability.

---

# Create a Review Notebook

Maintain notes during review.

Example:

```text
Application:
ExampleApp

Framework:
Spring Boot

Authentication:
JWT

Database:
PostgreSQL

External Services:
Payment API
Email API

High-Risk Areas:
File upload
Report generation
Admin API
Password reset

Potential Findings:
SRC-001
SRC-002
SRC-003
```

---

# Candidate Tracking

Use a table:

| ID | Candidate | Source | Sink | Status |
|---|---|---|---|---|
| C-001 | SQLi | `q` | `createNativeQuery` | Investigating |
| C-002 | SSRF | `url` | `HttpClient` | Protected |
| C-003 | IDOR | `userId` | `findById` | Confirmed |
| C-004 | Command Injection | `filename` | `ProcessBuilder` | False Positive |

This prevents duplicate work.

---

# Candidate States

Useful states:

```text
Candidate
Investigating
Protected
Not Reachable
False Positive
Confirmed
Needs Dynamic Validation
```

---

# Evidence Collection

For confirmed findings record:

```text
File
Line
Function
Route
Source
Transformations
Sink
Security control
Why control fails
Impact
Dynamic evidence
Remediation
```

---

# Source Code Evidence

Example:

```text
File:
src/main/java/com/example/UserController.java

Method:
search()

Source:
@RequestParam String q

Sink:
EntityManager.createNativeQuery()

Flow:
q -> UserService.search() -> Repository.search() -> createNativeQuery()

Security Control:
No parameterisation identified.

Impact:
Potential SQL injection.
```

---

# Evidence Should Explain the Flow

Weak evidence:

```text
createNativeQuery found.
```

Better:

```text
The q HTTP parameter is passed from SearchController.search()
to SearchService.search(), concatenated into a native SQL query in
SearchRepository.search(), and executed through createNativeQuery().
No parameter binding is applied to q before execution.
```

The second explanation demonstrates exploitability much more clearly.

---

# Finding Template

```text
Title:

Affected Component:

Affected Route:

Source:

Transformations:

Sink:

Security Control:

Security Control Weakness:

Data Flow:

Exploitability:

Impact:

Evidence:

Recommendation:
```

---

# Data Flow Template

```text
SOURCE
  |
  v
Controller
  |
  v
Service
  |
  v
Transformation
  |
  v
Security Control
  |
  v
Sink
```

---

# Example Finding Model

```text
Title:
Server-Side Request Forgery in URL Import Functionality

Source:
POST /api/import
JSON field: url

Data Flow:

request.url
    |
    v
ImportController
    |
    v
ImportService
    |
    v
HttpClient
    |
    v
Outbound Request

Security Control:
The application verifies that the URL begins with HTTP or HTTPS.

Weakness:
The validation does not restrict destination hosts or resolved IP addresses.

Impact:
An authenticated user may be able to cause the server to send requests to unintended network destinations.
```

---

# Avoid Overclaiming

Source review frequently produces suspicious code that is not exploitable.

Examples:

```text
Raw SQL function
```

does not automatically mean:

```text
SQL Injection
```

```text
HttpClient
```

does not automatically mean:

```text
SSRF
```

```text
ProcessBuilder
```

does not automatically mean:

```text
Command Injection
```

```text
innerHTML
```

does not automatically mean:

```text
XSS
```

```text
ObjectInputStream
```

does not automatically mean:

```text
Exploitable Deserialisation
```

Context determines security impact.

---

# False Positive Reduction

For every candidate ask:

```text
1. Can an attacker control the source?

2. Can the attacker reach the code?

3. Does the data actually reach the sink?

4. Is there validation?

5. Is there sanitisation?

6. Is there parameterisation?

7. Is there encoding?

8. Is there authorisation?

9. Does framework behaviour provide protection?

10. Is the sink used in a dangerous context?

11. Is exploitation realistic?

12. What is the actual impact?
```

---

# Security Review Decision Tree

```text
Interesting Code Pattern
        |
        v
Security-Sensitive Sink?
        |
   +----+----+
   |         |
  No        Yes
   |         |
   v         v
Lower     Trace Input
Priority      |
              v
      Attacker Controlled?
              |
         +----+----+
         |         |
        No        Yes
         |         |
         v         v
      Lower     Security
      Priority   Control?
                   |
              +----+----+
              |         |
             Yes        No
              |         |
              v         v
          Effective?   Candidate
              |
         +----+----+
         |         |
        Yes        No
         |         |
         v         v
     Protected   Candidate
                   |
                   v
             Dynamically
              Validate
                   |
                   v
                 Impact
```

---

# Manual Review and SAST

The strongest methodology combines:

```text
Manual Review
     +
Pattern Searching
     +
SAST
     +
Dependency Analysis
     +
Dynamic Testing
```

No single technique provides complete coverage.

---

# What Automated Tools Are Good At

Automated tools are useful for:

```text
Pattern detection
Known dangerous APIs
Known vulnerability classes
Repeated patterns
Dependency vulnerabilities
Secret patterns
Data-flow candidates
```

---

# What Humans Are Better At

Manual review is particularly important for:

```text
Business logic
Authorisation
Tenant isolation
Workflow vulnerabilities
Security assumptions
Context-specific validation
Race conditions
Trust boundaries
Chained vulnerabilities
Architecture
```

---

# Review Checklist

## Preparation

```text
[ ] Scope confirmed
[ ] Repository obtained
[ ] Correct branch identified
[ ] Build instructions reviewed
[ ] Application architecture understood
[ ] Technology stack identified
[ ] Dependencies identified
```

## Visual Studio Code

```text
[ ] Repository opened in VS Code
[ ] Explorer structure reviewed
[ ] Search exclusions configured
[ ] Language extensions available
[ ] Go to Definition working
[ ] Find References working
[ ] Integrated terminal available
[ ] Git repository detected
```

## Attack Surface

```text
[ ] Routes identified
[ ] APIs identified
[ ] GraphQL identified
[ ] gRPC identified
[ ] WebSockets identified
[ ] File uploads identified
[ ] Webhooks identified
[ ] Background jobs identified
[ ] Message consumers identified
[ ] Admin functionality identified
```

## Sources

```text
[ ] Query parameters reviewed
[ ] Path parameters reviewed
[ ] Request bodies reviewed
[ ] Headers reviewed
[ ] Cookies reviewed
[ ] File uploads reviewed
[ ] WebSocket messages reviewed
[ ] GraphQL arguments reviewed
[ ] gRPC inputs reviewed
[ ] Database-originated untrusted data considered
[ ] Queue messages reviewed
```

## Authentication

```text
[ ] Login reviewed
[ ] Logout reviewed
[ ] Password handling reviewed
[ ] Session creation reviewed
[ ] Token creation reviewed
[ ] Token validation reviewed
[ ] MFA reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
```

## Authorisation

```text
[ ] Route-level authorisation reviewed
[ ] Method-level authorisation reviewed
[ ] Object ownership reviewed
[ ] Tenant isolation reviewed
[ ] Administrative operations reviewed
[ ] Alternate entry points reviewed
```

## Input Validation

```text
[ ] Validation framework identified
[ ] Server-side validation reviewed
[ ] Type validation reviewed
[ ] Length limits reviewed
[ ] Allowlist validation reviewed
[ ] Normalisation reviewed
```

## Injection

```text
[ ] SQL sinks reviewed
[ ] NoSQL sinks reviewed
[ ] LDAP sinks reviewed
[ ] Command sinks reviewed
[ ] Template sinks reviewed
[ ] Expression engines reviewed
```

## Server-Side

```text
[ ] SSRF sinks reviewed
[ ] File operations reviewed
[ ] Path handling reviewed
[ ] File uploads reviewed
[ ] XML parsing reviewed
[ ] Deserialisation reviewed
```

## Client-Side

```text
[ ] HTML output reviewed
[ ] XSS sinks reviewed
[ ] Redirects reviewed
[ ] CORS configuration reviewed
[ ] CSRF protection reviewed
[ ] Security headers reviewed
```

## Identity

```text
[ ] JWT reviewed
[ ] OAuth reviewed
[ ] OIDC reviewed
[ ] SAML reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
```

## Business Logic

```text
[ ] State transitions mapped
[ ] Critical invariants identified
[ ] Repeated actions reviewed
[ ] Negative values reviewed
[ ] Workflow bypass reviewed
[ ] Race conditions reviewed
```

## Data Protection

```text
[ ] Secrets reviewed
[ ] Cryptography reviewed
[ ] Sensitive logging reviewed
[ ] Error handling reviewed
[ ] Data exposure reviewed
```

## Supply Chain

```text
[ ] Dependencies inventoried
[ ] Versions identified
[ ] Dependency scanning performed
[ ] Build scripts reviewed
[ ] Third-party sources reviewed
```

## Static Analysis

```text
[ ] ripgrep searches performed
[ ] Semgrep considered
[ ] CodeQL considered
[ ] Language-specific SAST considered
[ ] Dependency scanner considered
[ ] Secret scanner considered
[ ] Results manually validated
```

## Variant Analysis

```text
[ ] Similar sinks searched
[ ] Similar sources searched
[ ] Find References used
[ ] Call hierarchy reviewed
[ ] Similar controllers reviewed
[ ] Similar services reviewed
[ ] Alternate entry points reviewed
```

## Validation

```text
[ ] Candidate exploitability assessed
[ ] Framework protections considered
[ ] Runtime configuration considered
[ ] Dynamic validation performed where appropriate
[ ] False positives removed
[ ] Impact established
```

## Reporting

```text
[ ] Source documented
[ ] Data flow documented
[ ] Sink documented
[ ] Missing control documented
[ ] Evidence captured
[ ] Impact explained
[ ] Recommendation provided
[ ] Variant analysis completed
```

---

# Common Review Mistakes

## Searching Only for Dangerous Functions

Finding:

```text
exec()
```

is only the beginning.

The real question is:

```text
Can attacker-controlled input reach exec()?
```

---

# Reviewing Only Controllers

Vulnerabilities frequently exist deeper in:

```text
Services
Repositories
Utilities
Workers
Background jobs
Message handlers
```

Follow the complete call chain.

---

# Trusting Database Data

Stored data may originally have come from an attacker.

Always consider second-order flows.

---

# Ignoring Alternate Entry Points

The same service may be reachable through:

```text
REST
GraphQL
WebSocket
gRPC
Background job
Admin interface
```

Security controls may differ.

---

# Treating Validation as Authorisation

Example:

```text
userId must be numeric
```

does not answer:

```text
Is the current user allowed to access userId?
```

---

# Treating Authentication as Authorisation

Being logged in does not mean a user may access every object.

---

# Ignoring Framework Security

Frameworks may provide:

```text
Output encoding
CSRF protection
Parameterisation
Security headers
Authentication middleware
```

Understand the framework before reporting.

---

# Assuming Framework Defaults

The opposite mistake is also dangerous.

Do not assume protections are enabled simply because the framework supports them.

Review:

```text
Version
Configuration
Overrides
Custom code
Deployment
```

---

# Trusting Function Names

A function named:

```text
sanitize()
```

is not automatically secure.

Open the implementation.

---

# Trusting Comments

A comment such as:

```text
// validate URL
```

does not prove that URL validation is correct.

Review the implementation.

---

# Ignoring Configuration

Security behaviour may depend heavily on:

```text
Environment variables
Production profiles
Reverse proxies
Feature flags
Cloud configuration
Deployment settings
```

Source code alone may not provide the complete answer.

---

# Ignoring Build Output

Generated or bundled code may differ from source.

Where relevant compare:

```text
Source
Build configuration
Production artifact
```

---

# Stopping After the First Finding

A confirmed vulnerability often indicates a reusable vulnerable pattern.

Always perform:

```text
Variant Analysis
```

---

# Final Source Code Review Model

```text
                           REPOSITORY
                               |
                               v
                     TECHNOLOGY IDENTIFICATION
                               |
                               v
                       ARCHITECTURE MAPPING
                               |
                               v
                     ATTACK SURFACE MAPPING
                               |
                               v
                          ENTRY POINTS
                               |
                               v
                            SOURCES
                               |
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
         HTTP Input         Stored Data       Messages
            |                  |                  |
            +------------------+------------------+
                               |
                               v
                        TRANSFORMATIONS
                               |
       +-----------+-----------+-----------+-----------+
       |           |           |           |           |
       v           v           v           v           v
   Validation   Parsing    Normalisation  AuthZ    Business Logic
       |           |           |           |           |
       +-----------+-----------+-----------+-----------+
                               |
                               v
                             SINK
                               |
       +-----------+-----------+-----------+-----------+
       |           |           |           |           |
       v           v           v           v           v
      SQL       Command       File        HTTP       Output
       |           |           |           |           |
       +-----------+-----------+-----------+-----------+
                               |
                               v
                       SECURITY CONTROL
                               |
                         +-----+-----+
                         |           |
                         v           v
                     Effective   Ineffective
                         |           |
                         v           v
                     Protected    Candidate
                                     |
                                     v
                              Dynamic Validation
                                     |
                                     v
                                   Impact
                                     |
                                     v
                             Confirmed Finding
                                     |
                                     v
                              Variant Analysis
```

The review can therefore be reduced to five fundamental questions:

```text
1. Where does data enter?

2. Where does the data go?

3. What security-sensitive operation does it reach?

4. What security controls exist between source and sink?

5. Can those controls be bypassed or are they ineffective?
```

Or even more simply:

```text
SOURCE
   |
   v
DATA FLOW
   |
   v
SECURITY CONTROL
   |
   v
SINK
   |
   v
IMPACT
```

The tools help locate these components.

Visual Studio Code helps navigate them.

Static analysis helps identify candidates.

Dynamic testing helps validate behaviour.

The security reviewer determines whether the complete flow represents a real vulnerability.

---

# Visual Studio Code Quick Reference

```text
Open repository:
code .

Global Search:
Ctrl + Shift + F

Go to Definition:
F12

Peek Definition:
Alt + F12

Find All References:
Shift + F12

File Symbols:
Ctrl + Shift + O

Workspace Symbols:
Ctrl + T

Integrated Terminal:
Ctrl + `

Command Palette:
Ctrl + Shift + P
```

Useful review workflow:

```text
Ctrl + Shift + F
        |
        v
Search Sink
        |
        v
Open Match
        |
        v
F12
        |
        v
Follow Definition
        |
        v
Shift + F12
        |
        v
Find Callers
        |
        v
Trace Source
        |
        v
Ctrl + `
        |
        v
Run rg / Semgrep / Git
```

---

# Recommended Source Code Review Structure

The complete Source Code Review section can now follow:

```text
Source Code Review
│
├── Overview
├── Methodology
│
├── Languages and Frameworks
│   ├── .NET / ASP.NET Core
│   ├── Java / Spring
│   ├── PHP
│   ├── Python
│   ├── Django
│   ├── Flask
│   ├── Node.js / Express
│   └── Client-Side JavaScript
│
└── Static Analysis
    ├── Semgrep
    ├── CodeQL
    └── Grep / ripgrep
```

The language-specific pages answer:

```text
What are the sources and sinks
for this technology?
```

This methodology page answers:

```text
How do I systematically review
an unfamiliar application?
```

Together they provide a repeatable white-box application security methodology.

---

# References

## OWASP Secure Code Review Cheat Sheet

[OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html)

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## OWASP Application Security Verification Standard

[OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

## OWASP Attack Surface Analysis Cheat Sheet

[OWASP Attack Surface Analysis Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Attack_Surface_Analysis_Cheat_Sheet.html)

## Visual Studio Code Documentation

[docs](https://code.visualstudio.com/docs)

## Visual Studio Code Editing

[Visual Studio Code Editing](https://code.visualstudio.com/docs/editing/codebasics)

## Visual Studio Code Search

[Visual Studio Code Search](https://code.visualstudio.com/docs/editing/codebasics#_search-across-files)

## Visual Studio Code Debugging

[Visual Studio Code Debugging](https://code.visualstudio.com/docs/debugtest/debugging)

## Visual Studio Code Source Control

[Visual Studio Code Source Control](https://code.visualstudio.com/docs/sourcecontrol/overview)

## Semgrep Documentation

[docs](https://semgrep.dev/docs/)

## CodeQL Documentation

[docs](https://codeql.github.com/docs/)

## CodeQL Data Flow Analysis

[CodeQL Data Flow Analysis](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/)

## Git Documentation

[doc](https://git-scm.com/doc)

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
docs/source-code-review/javascript.md
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
docs/web/sql-injection.md
docs/web/nosql-injection.md
docs/web/ldap-injection.md
docs/web/command-injection.md
docs/web/ssti.md
docs/web/ssrf.md
docs/web/path-traversal.md
docs/web/file-upload.md
docs/web/xxe.md
docs/web/deserialization.md
docs/web/xss.md
docs/web/html-injection.md
docs/web/csrf.md
docs/web/cors.md
docs/web/open-redirect.md
docs/web/host-header-attacks.md
docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/rate-limiting.md
docs/web/mass-assignment.md
docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md
```
