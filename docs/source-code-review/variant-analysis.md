# Variant Analysis

Variant analysis is the process of using a known vulnerability, security weakness, or suspicious code pattern to systematically search for similar instances elsewhere in a codebase.

Instead of treating a confirmed vulnerability as an isolated finding:

```text
Confirmed Vulnerability
        |
        v
Fix This Location
```

variant analysis asks:

```text
Confirmed Vulnerability
        |
        v
What caused it?
        |
        v
What code pattern created it?
        |
        v
Where else does this pattern exist?
        |
        v
Find Related Variants
```

This is one of the most powerful techniques in source code security review.

A single vulnerability can reveal:

```text
A repeated coding pattern
A missing security control
A dangerous helper
A vulnerable abstraction
A framework misuse
A repeated sink
A missing ownership check
A missing validation function
A dangerous API wrapper
A vulnerable architectural pattern
```

The objective is therefore not merely:

```text
Find another copy of the vulnerable line
```

but:

```text
Find every semantically similar path that may produce
the same security weakness.
```

---

# Authorised Testing

Use variant analysis only against source code, applications, and environments that you are authorised to assess.

Variant analysis can reveal large numbers of security-sensitive locations, including:

```text
Administrative functionality
Internal APIs
Authentication logic
Authorisation controls
Database queries
File operations
Network requests
Command execution
Secrets
Debug functionality
```

Handle discovered information according to the rules of engagement.

---

# Why Variant Analysis Matters

Applications rarely contain security bugs in complete isolation.

Developers frequently reuse:

```text
Functions
Libraries
Patterns
Frameworks
Helpers
Services
Controllers
Repository methods
Security controls
```

Therefore:

```text
One Vulnerability
      |
      v
Underlying Pattern
      |
      v
Potentially Many Variants
```

For example, if this endpoint contains an IDOR:

```text
GET /documents/{id}
```

the same object access pattern may exist in:

```text
PUT /documents/{id}
DELETE /documents/{id}
GET /documents/{id}/download
POST /documents/{id}/share

GraphQL:
document(id)
updateDocument(id)
deleteDocument(id)

gRPC:
GetDocument
UpdateDocument
DeleteDocument

WebSocket:
delete-document
share-document
```

The original finding becomes the starting point for broader analysis.

---

# Core Principle

Variant analysis should begin with understanding the root cause.

Do not search only for the vulnerable string.

Instead determine:

```text
SOURCE
  |
  v
DATA FLOW
  |
  v
MISSING / WEAK CONTROL
  |
  v
SINK
  |
  v
IMPACT
```

Then search for variations of that pattern.

---

# Variant Analysis Model

```text
CONFIRMED FINDING
       |
       v
UNDERSTAND ROOT CAUSE
       |
       v
IDENTIFY SOURCE
       |
       v
IDENTIFY SINK
       |
       v
IDENTIFY MISSING CONTROL
       |
       v
IDENTIFY CODE PATTERN
       |
       v
SEARCH EXACT VARIANTS
       |
       v
SEARCH STRUCTURAL VARIANTS
       |
       v
SEARCH SEMANTIC VARIANTS
       |
       v
TRACE CANDIDATES
       |
       v
VALIDATE
       |
       v
REPEAT
```

---

# A Variant Is Not Necessarily a Duplicate

A duplicate may be almost identical:

```java
repository.findById(id);
```

appearing in several controllers.

A variant may be structurally different while creating the same security weakness.

Example:

```java
repository.findById(id);
```

versus:

```java
repository.findOne(
    specification
);
```

versus:

```java
entityManager.find(
    Document.class,
    id
);
```

All may ultimately represent:

```text
Attacker-Controlled ID
        |
        v
Object Lookup
        |
        v
Missing Ownership Check
```

---

# Three Levels of Variant Analysis

A practical model is:

```text
Level 1 - Textual Variants

Level 2 - Structural Variants

Level 3 - Semantic Variants
```

---

# Level 1 - Textual Variants

Search for the same:

```text
Function
Method
Class
String
Route
Helper
API
Sink
```

Tools:

```text
ripgrep
VS Code Search
grep
```

Example:

```bash
rg -n \
'findById\(' \
.
```

This is fast but can miss semantically equivalent code.

---

# Level 2 - Structural Variants

Search for code with the same syntactic structure.

Tools:

```text
Semgrep
OpenGrep
AST-based analysis
```

Example concept:

```text
Request Parameter
      |
      v
Database Lookup
```

regardless of exact variable names.

---

# Level 3 - Semantic Variants

Search for equivalent data-flow or security behaviour.

Tools:

```text
CodeQL
Taint analysis
Manual source-to-sink tracing
Call graph analysis
```

Example:

```text
HTTP Request
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
Sensitive Sink
```

even if multiple functions separate source and sink.

---

# Start With a Confirmed Finding

Variant analysis is strongest when based on a confirmed vulnerability.

Record:

```text
Finding
Entry point
Source
Transformations
Security controls
Missing security control
Sink
Impact
```

Example:

```text
Finding:
IDOR

Route:
GET /api/documents/{id}

Source:
id

Lookup:
DocumentRepository.findById(id)

Expected Control:
Ownership validation

Actual Control:
None

Sink:
Document returned to user

Impact:
Another user's document can be retrieved
```

Now the variant search has a precise target.

---

# Root Cause Analysis

Before searching, answer:

```text
Why is this vulnerable?
```

For example:

```text
Because attacker-controlled object identifiers are used
to retrieve documents without constraining the lookup
to the authenticated user's authorised objects.
```

This is more useful than:

```text
findById() is vulnerable.
```

`findById()` itself is not inherently vulnerable.

---

# Extract the Security Pattern

Convert the vulnerability into a reusable model.

```text
ATTACKER-CONTROLLED OBJECT ID
            |
            v
       OBJECT LOOKUP
            |
            v
   NO OWNERSHIP / TENANT CHECK
            |
            v
     SENSITIVE OPERATION
```

Then search for every implementation of this model.

---

# Build a Variant Hypothesis

Before searching, define what variants might look like.

For IDOR:

```text
Same object
Different HTTP method

Same object
Different controller

Same repository
Different route

Same service
Different API

Same object
GraphQL

Same object
gRPC

Same object
WebSocket

Different object
Same vulnerable lookup pattern
```

---

# Visual Studio Code Workflow

Visual Studio Code is particularly useful for variant analysis.

Useful features:

```text
Global Search
Go to Definition
Find All References
Call Hierarchy
Peek Definition
Workspace Symbols
Git integration
Integrated terminal
```

---

# Find All References

If a vulnerable helper is:

```text
getDocumentById()
```

place the cursor on the function and use:

```text
Shift + F12
```

This can reveal:

```text
REST controller
GraphQL resolver
gRPC service
Background worker
Admin controller
```

---

# Call Hierarchy

Use Call Hierarchy to understand:

```text
Who calls this function?
```

and:

```text
What does this function call?
```

This is especially useful for shared services.

Example:

```text
DocumentService.delete()
          ^
          |
    +-----+-----+
    |           |
REST API     GraphQL
    |
Admin API
```

---

# Go to Definition

Use:

```text
F12
```

to follow:

```text
Controller
    |
    v
Service
    |
    v
Repository
    |
    v
Sink
```

---

# Global Search

Use:

```text
Ctrl + Shift + F
```

to search for:

```text
Vulnerable helper
Repository method
Security helper
Object type
Route
Sink
Validation function
```

---

# ripgrep

ripgrep is usually the fastest first step.

If the vulnerability uses:

```java
documentRepository.findById(
```

search:

```bash
rg -n \
'documentRepository\.findById\(' \
.
```

Then broaden:

```bash
rg -n \
'\.findById\(' \
.
```

Then search related methods:

```bash
rg -n \
'\.(findById|findOne|getById|getReferenceById)\(' \
.
```

---

# Search the Object Name

For a vulnerable `Document` object:

```bash
rg -n -i \
'document' \
.
```

Then narrow:

```bash
rg -n \
'DocumentRepository|DocumentService|DocumentController' \
.
```

---

# Search the Sensitive Operation

If the confirmed finding involves:

```text
deleteDocument()
```

search:

```bash
rg -n \
'deleteDocument\(' \
.
```

and related sinks:

```bash
rg -n \
'\.(delete|deleteById|remove|destroy)\(' \
.
```

Manual triage is required.

---

# Search the Missing Security Control

Suppose secure routes normally use:

```text
checkDocumentAccess()
```

Search:

```bash
rg -n \
'checkDocumentAccess\(' \
.
```

Now compare:

```text
Where is the helper used?

Where is the same sensitive service called without it?
```

---

# Negative Pattern Analysis

This is particularly powerful.

Secure pattern:

```text
loadDocument()
checkDocumentAccess()
returnDocument()
```

Potential vulnerable pattern:

```text
loadDocument()
returnDocument()
```

Variant analysis asks:

```text
Where is loadDocument() used without checkDocumentAccess()?
```

---

# Security Helper Inventory

Search for common security helpers:

```bash
rg -n -i \
'authori[sz]e|check.?access|check.?permission|verify.?owner|validate.?tenant|can.?access|can.?edit|can.?delete' \
.
```

Build a list.

Example:

```text
authorizeDocument()
authorizeProject()
checkOwnership()
validateTenant()
requirePermission()
```

These become useful anchors for variant searches.

---

# Search the Sink, Not Only the Source

If a vulnerability ends in:

```text
Runtime.exec()
```

search every use:

```bash
rg -n \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder' \
-g '*.java' \
.
```

Then trace each sink backwards.

```text
SINK
  ^
  |
INPUT
```

This is reverse source-to-sink analysis.

---

# Forward and Reverse Variant Analysis

Use both directions.

Forward:

```text
Source
  |
  v
Find every path to dangerous sinks
```

Reverse:

```text
Sink
  |
  v
Find every attacker-controlled path reaching it
```

Combined:

```text
SOURCE ---> SINK
   \         ^
    \       /
     VARIANTS
```

---

# Variant Analysis by Vulnerability Type

Different vulnerability classes require different variant strategies.

---

# IDOR / BOLA Variants

Confirmed pattern:

```text
Request ID
   |
   v
Object Lookup
   |
   v
Missing Ownership Check
```

Search for:

```text
Object IDs
Repository lookups
Service lookups
Object serializers
Download handlers
Update handlers
Delete handlers
```

---

# IDOR ripgrep Searches

```bash
rg -n -i \
'user.?id|account.?id|document.?id|order.?id|invoice.?id|tenant.?id|organisation.?id|organization.?id' \
.
```

Repository operations:

```bash
rg -n \
'findById|getById|findOne|findByPk|FindAsync|SingleAsync|FirstAsync' \
.
```

Then manually determine whether object-level authorisation exists.

---

# IDOR Operation Variants

For:

```text
Document
```

search operations:

```bash
rg -n -i \
'get.*document|read.*document|update.*document|delete.*document|download.*document|share.*document|export.*document' \
.
```

---

# SQL Injection Variants

Confirmed pattern:

```text
Request Input
    |
    v
String Concatenation
    |
    v
SQL Execution
```

Extract:

```text
Database API
Query construction method
Source type
```

Search sinks.

---

# Java SQL Sinks

```bash
rg -n \
'executeQuery|executeUpdate|createNativeQuery|createQuery|Statement' \
-g '*.java' \
.
```

---

# .NET SQL Sinks

```bash
rg -n \
'SqlCommand|ExecuteReader|ExecuteScalar|ExecuteNonQuery|FromSqlRaw|ExecuteSqlRaw' \
-g '*.cs' \
.
```

---

# Python SQL Sinks

```bash
rg -n \
'\.execute\(|\.executemany\(|\.raw\(' \
-g '*.py' \
.
```

---

# PHP SQL Sinks

```bash
rg -n \
'->query\(|mysqli_query|PDO|DB::raw|whereRaw|selectRaw' \
-g '*.php' \
.
```

---

# Node.js SQL Sinks

```bash
rg -n \
'\.query\(|\.execute\(|sequelize\.query|\$queryRaw|\$executeRaw' \
-g '*.js' \
-g '*.ts' \
.
```

Then determine whether attacker-controlled input reaches dynamically constructed queries.

---

# Command Injection Variants

Confirmed model:

```text
User Input
   |
   v
Command Construction
   |
   v
Process Execution
```

Search execution APIs.

---

# Java

```bash
rg -n \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'Process\.Start|ProcessStartInfo' \
-g '*.cs' \
.
```

---

# Python

```bash
rg -n \
'os\.system|os\.popen|subprocess\.(run|Popen|call|check_output|check_call)' \
-g '*.py' \
.
```

---

# PHP

```bash
rg -n \
'\b(system|exec|shell_exec|passthru|popen|proc_open)\s*\(' \
-g '*.php' \
.
```

---

# Node.js

```bash
rg -n \
'child_process|exec\(|execSync\(|spawn\(|spawnSync\(' \
-g '*.js' \
-g '*.ts' \
.
```

---

# SSRF Variants

Confirmed model:

```text
Attacker URL
    |
    v
HTTP Client
    |
    v
Server-Side Request
```

Search HTTP clients.

---

# Python SSRF Sinks

```bash
rg -n \
'requests\.(get|post|put|delete|request)|httpx\.|urllib\.request|aiohttp' \
-g '*.py' \
.
```

---

# Java SSRF Sinks

```bash
rg -n \
'HttpClient|RestTemplate|WebClient|URLConnection|openConnection' \
-g '*.java' \
.
```

---

# .NET SSRF Sinks

```bash
rg -n \
'HttpClient|WebClient|HttpWebRequest|WebRequest' \
-g '*.cs' \
.
```

---

# Node.js SSRF Sinks

```bash
rg -n \
'axios\.|fetch\(|got\(|request\(|http\.request|https\.request' \
-g '*.js' \
-g '*.ts' \
.
```

---

# PHP SSRF Sinks

```bash
rg -n \
'curl_exec|curl_init|file_get_contents|fopen|Guzzle' \
-g '*.php' \
.
```

Then determine which URLs can be attacker-controlled.

---

# Path Traversal Variants

Model:

```text
User-Controlled Path
       |
       v
Path Construction
       |
       v
Filesystem Operation
```

Search:

```text
read
write
delete
move
copy
download
extract
```

---

# Python File Sinks

```bash
rg -n \
'open\(|Path\(|send_file|send_from_directory|os\.remove|shutil\.' \
-g '*.py' \
.
```

---

# Java File Sinks

```bash
rg -n \
'Files\.(read|write|copy|move|delete)|FileInputStream|FileOutputStream|new File\(' \
-g '*.java' \
.
```

---

# .NET File Sinks

```bash
rg -n \
'File\.(Read|Write|Open|Delete|Copy|Move)|FileStream|Path\.Combine' \
-g '*.cs' \
.
```

---

# Node.js File Sinks

```bash
rg -n \
'fs\.(readFile|writeFile|createReadStream|createWriteStream|unlink|rename)|path\.join|path\.resolve' \
-g '*.js' \
-g '*.ts' \
.
```

---

# PHP File Sinks

```bash
rg -n \
'file_get_contents|file_put_contents|fopen|readfile|unlink|move_uploaded_file' \
-g '*.php' \
.
```

---

# File Upload Variants

If one vulnerable upload exists, search for every upload implementation.

```bash
rg -n -i \
'upload|multipart|IFormFile|MultipartFile|request\.files|req\.files|multer|move_uploaded_file' \
.
```

Compare:

```text
Filename validation
Extension validation
MIME handling
Storage location
Randomised naming
Parser behaviour
Archive extraction
Authorisation
```

Different upload routes may use different controls.

---

# Deserialization Variants

Search deserialization APIs and wrappers.

Java:

```bash
rg -n \
'ObjectInputStream|readObject\(' \
-g '*.java' \
.
```

.NET:

```bash
rg -n \
'BinaryFormatter|LosFormatter|NetDataContractSerializer|ObjectStateFormatter' \
-g '*.cs' \
.
```

Python:

```bash
rg -n \
'pickle\.loads?|yaml\.load|marshal\.loads?' \
-g '*.py' \
.
```

PHP:

```bash
rg -n \
'unserialize\(' \
-g '*.php' \
.
```

Node.js:

```bash
rg -n -i \
'deserialize|node-serialize|serialize-javascript' \
-g '*.js' \
-g '*.ts' \
.
```

A deserialization API match is not automatically exploitable.

Trace attacker control and configuration.

---

# SSTI Variants

Search dynamic template creation and rendering.

Python:

```bash
rg -n \
'render_template_string|Template\(' \
-g '*.py' \
.
```

Java:

```bash
rg -n -i \
'freemarker|velocity|thymeleaf|template\.process|evaluate' \
-g '*.java' \
.
```

PHP:

```bash
rg -n -i \
'twig|blade|render\(' \
-g '*.php' \
.
```

Node.js:

```bash
rg -n \
'res\.render|ejs\.render|Handlebars\.compile|pug\.render' \
-g '*.js' \
-g '*.ts' \
.
```

Determine whether attacker input controls template source rather than ordinary template data.

---

# XSS Variants

Confirmed model:

```text
Attacker Input
     |
     v
HTML / DOM Sink
     |
     v
Browser Interpretation
```

Search both server-side output and browser sinks.

---

# Browser JavaScript Sinks

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|document\.writeln|srcdoc|createContextualFragment' \
-g '*.js' \
-g '*.jsx' \
-g '*.ts' \
-g '*.tsx' \
.
```

---

# Dynamic Execution

```bash
rg -n \
'eval\(|new Function|setTimeout\([^,]*["'\'']|setInterval\([^,]*["'\'']' \
-g '*.js' \
-g '*.ts' \
.
```

Manual review is required.

---

# React

```bash
rg -n \
'dangerouslySetInnerHTML' \
-g '*.jsx' \
-g '*.tsx' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Angular

Search:

```bash
rg -n \
'bypassSecurityTrustHtml|bypassSecurityTrustScript|bypassSecurityTrustUrl|bypassSecurityTrustResourceUrl' \
-g '*.ts' \
.
```

---

# Vue

```bash
rg -n \
'v-html' \
-g '*.vue' \
.
```

---

# Open Redirect Variants

Model:

```text
User-Controlled URL
       |
       v
Redirect / Navigation Sink
```

Search server-side redirects.

```bash
rg -n \
'redirect\(|Redirect\(|RedirectToAction|sendRedirect|header\(["'\'']Location' \
.
```

Client-side:

```bash
rg -n \
'location\.(href|assign|replace)|window\.open' \
-g '*.js' \
-g '*.ts' \
.
```

Then determine whether destinations are appropriately constrained.

---

# XXE Variants

Search XML parsers.

Java:

```bash
rg -n \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory|SchemaFactory' \
-g '*.java' \
.
```

.NET:

```bash
rg -n \
'XmlDocument|XmlReader|XmlTextReader|XDocument' \
-g '*.cs' \
.
```

Python:

```bash
rg -n \
'xml\.etree|lxml|ElementTree|minidom|sax' \
-g '*.py' \
.
```

PHP:

```bash
rg -n \
'DOMDocument|SimpleXML|simplexml_load|XMLReader' \
-g '*.php' \
.
```

Review parser configuration rather than reporting parser presence alone.

---

# LDAP Injection Variants

Search LDAP operations.

Java:

```bash
rg -n \
'LdapTemplate|DirContext|InitialDirContext|search\(' \
-g '*.java' \
.
```

.NET:

```bash
rg -n \
'DirectorySearcher|DirectoryEntry|SearchRequest' \
-g '*.cs' \
.
```

Python:

```bash
rg -n -i \
'ldap|ldap3' \
-g '*.py' \
.
```

PHP:

```bash
rg -n \
'ldap_search|ldap_bind|ldap_list|ldap_read' \
-g '*.php' \
.
```

Trace whether LDAP filters are dynamically constructed from attacker input.

---

# NoSQL Injection Variants

Search database operations involving:

```text
MongoDB
Mongoose
DynamoDB
CouchDB
Elasticsearch
```

Node.js:

```bash
rg -n \
'findOne\(|find\(|findById\(|updateOne\(|deleteOne\(|\$where|\$regex' \
-g '*.js' \
-g '*.ts' \
.
```

Python:

```bash
rg -n \
'find_one\(|find\(|update_one\(|delete_one\(' \
-g '*.py' \
.
```

The database method itself is not a vulnerability.

Review attacker-controlled query structure.

---

# Mass Assignment Variants

Search for patterns where entire request objects are passed to models.

Node.js:

```bash
rg -n \
'create\(req\.body|update\(req\.body|Object\.assign\([^,]+,\s*req\.body' \
-g '*.js' \
-g '*.ts' \
.
```

Python:

```bash
rg -n \
'\*\*request\.(json|data)|\*\*serializer\.validated_data' \
-g '*.py' \
.
```

PHP:

```bash
rg -n \
'->create\(\$request->all|->update\(\$request->all|fill\(\$request->all' \
-g '*.php' \
.
```

Review allowlists, DTOs, serializers, model fillable fields, and framework protections.

---

# Prototype Pollution Variants

Search:

```bash
rg -n \
'Object\.assign|lodash\.merge|_.merge|_.set|deepmerge|merge\(' \
-g '*.js' \
-g '*.ts' \
.
```

Then trace:

```text
Attacker-Controlled Key
        |
        v
Recursive Merge / Property Assignment
        |
        v
Prototype Modification
        |
        v
Security-Relevant Impact
```

Prototype pollution requires meaningful impact.

---

# Authentication Variants

If one authentication bypass is discovered, search all paths capable of creating authentication state.

```text
Password Login
OAuth
OIDC
SAML
Magic Link
Password Reset
MFA Recovery
Remember Device
API Login
Mobile Login
Legacy Login
```

Search:

```bash
rg -n -i \
'login|signin|authenticate|session|token|oauth|oidc|saml|magic.?link|password.?reset|mfa|2fa' \
.
```

---

# MFA Variant Analysis

If MFA is bypassed through one flow, map every path to:

```text
Full Session
```

Example:

```text
Password
    |
    v
MFA
    |
    v
Session


OAuth
    |
    v
Session
```

The second path deserves investigation if policy requires MFA.

---

# Authorisation Variants

Confirmed issue:

```text
REST endpoint missing ownership check
```

Search:

```text
Same object
Same service
Same repository
Same controller
GraphQL resolver
gRPC method
WebSocket handler
Admin API
```

---

# Business Logic Variants

Business logic vulnerabilities often require conceptual rather than textual searches.

Known flaw:

```text
Discount can be applied repeatedly
```

Search for all:

```text
Coupon application
Discount calculation
Promotion processing
Order recalculation
Refund calculation
```

The implementation may use entirely different function names.

---

# Race Condition Variants

If a race exists around:

```text
Balance check
      |
      v
Update balance
```

search similar:

```text
Check then update
Check then insert
Check then delete
Inventory check then purchase
Token check then consume
Coupon check then redeem
```

---

# Security Header Variants

If one response path lacks expected security headers, determine whether:

```text
Headers are global
Headers are middleware-based
Specific routes override them
Static content bypasses middleware
Error responses differ
```

Do not simply search for header strings.

Understand where headers are applied.

---

# Secret Exposure Variants

A discovered credential should trigger broader secret analysis.

Search:

```bash
rg -n -i \
'password|passwd|secret|api.?key|access.?key|private.?key|token|client.?secret' \
.
```

Use dedicated secret-scanning tools as well.

Do not assume every match is an active secret.

---

# Error Handling Variants

If one endpoint leaks stack traces:

```text
Exception
   |
   v
Detailed Error Response
```

search:

```text
Global exception handlers
Debug middleware
Error serializers
Development settings
Custom exception responses
```

---

# Logging Variants

If one sensitive token is logged:

```text
Token
 |
 v
Logger
```

search similar logging.

```bash
rg -n -i \
'log.*token|logger.*token|log.*password|logger.*password|log.*secret|console\.log' \
.
```

---

# Dependency Variants

If one vulnerable dependency is identified, check:

```text
Other manifests
Other lockfiles
Monorepo packages
Containers
Build files
Frontend dependencies
Backend dependencies
Development tooling
```

Repositories may contain multiple dependency trees.

---

# API Variants

One vulnerable REST operation may have equivalent:

```text
GraphQL
gRPC
WebSocket
Mobile API
Legacy API
Internal API
```

Search by business operation rather than protocol.

---

# Route Variant Analysis

Suppose:

```text
POST /api/users/{id}/role
```

is vulnerable.

Search:

```bash
rg -n -i \
'role|changeRole|updateRole|assignRole|grantRole|permission' \
.
```

Then identify every entry point.

---

# Alternate API Versions

Search:

```bash
rg -n \
'/v[0-9]+/|api/v[0-9]+' \
.
```

Compare:

```text
v1
v2
v3
```

A vulnerability fixed in a newer API may remain in an older route.

Verify runtime exposure.

---

# Legacy Code

Search:

```bash
rg -n -i \
'legacy|deprecated|old|v1|compat|backward' \
.
```

These are indicators only.

Legacy code may still be secure or may not be reachable.

---

# Copy-Paste Vulnerabilities

Git history can help identify copied vulnerable code.

Search the vulnerable line:

```bash
git grep \
'vulnerableFunction'
```

Then:

```bash
git log -S 'vulnerableFunction' --all
```

This may reveal when the pattern was introduced and where it was copied.

---

# Git Blame

Use:

```bash
git blame path/to/file
```

This can identify the commit introducing a security-sensitive pattern.

Then inspect:

```bash
git show <commit>
```

Look for related changes elsewhere in the same commit.

---

# Git Diff Variant Analysis

If a vulnerability has been patched:

```bash
git diff <old> <new>
```

Study the fix.

The patch often reveals the precise missing security control.

Example:

```diff
 document =
     repository.findById(id);

+authorizeDocument(
+    currentUser,
+    document
+);
```

Now search for other calls to:

```text
repository.findById()
```

without:

```text
authorizeDocument()
```

---

# Patch-Diff Analysis

A patch provides:

```text
Vulnerable Pattern
        +
Security Fix
```

This is excellent input for variant analysis.

Model:

```text
Before
   |
   v
Vulnerability

After
   |
   v
Security Control
```

Search for other code resembling the "before" state.

---

# Semgrep Variant Analysis

Once a vulnerable structure is understood, encode it as a Semgrep rule.

Example vulnerable code:

```python
@app.get("/documents/<id>")
def document(id):

    document =
        Document.query.get(id)

    return jsonify(
        document.to_dict()
    )
```

Conceptual rule:

```yaml
rules:
  - id: document-lookup-review
    languages:
      - python
    message: Review document lookup for object-level authorisation
    severity: WARNING
    patterns:
      - pattern: |
          $OBJ = Document.query.get($ID)
```

This identifies candidates.

It does not prove missing authorisation.

---

# Improve the Rule

Add contextual structure where appropriate.

```yaml
rules:
  - id: flask-document-lookup
    languages:
      - python
    message: Review Flask document lookup for object-level authorisation
    severity: WARNING
    patterns:
      - pattern-inside: |
          def $FUNC(...):
            ...
      - pattern: |
          $OBJ = Document.query.get($ID)
```

Project-specific rules can become increasingly precise.

---

# Negative Patterns

If secure code always uses:

```python
authorize_document(...)
```

a rule can attempt to exclude functions containing that control.

Conceptually:

```yaml
patterns:
  - pattern: |
      $OBJ = Document.query.get($ID)

  - pattern-not-inside: |
      def $FUNC(...):
        ...
        authorize_document(...)
        ...
```

Negative-pattern logic must be used carefully.

The presence of a helper somewhere in a function does not necessarily prove it protects the relevant object or path.

---

# OpenGrep Variant Analysis

OpenGrep can be used similarly for structural rules.

Workflow:

```text
Confirmed Finding
       |
       v
Extract Pattern
       |
       v
Create OpenGrep Rule
       |
       v
Scan Repository
       |
       v
Review Matches
       |
       v
Improve Rule
```

---

# Taint-Based Variant Analysis

Some vulnerability classes are better represented as:

```text
SOURCE
   |
   v
SINK
```

than simple structural patterns.

Example:

```text
request.args
    |
    v
subprocess.run
```

Taint analysis can search for multiple data-flow variants.

---

# Conceptual Taint Rule

```yaml
rules:
  - id: flask-command-execution-review
    languages:
      - python
    message: User-controlled input may reach command execution
    severity: WARNING
    mode: taint

    pattern-sources:
      - pattern: request.args.get(...)

    pattern-sinks:
      - pattern: subprocess.run(...)
```

Add sanitizers only when they genuinely prevent the relevant vulnerability.

---

# Sanitizer Modelling

Be careful with:

```text
Validation
Escaping
Encoding
Normalisation
```

A sanitizer that prevents:

```text
SQL injection
```

does not necessarily prevent:

```text
Command injection
```

Sanitizer modelling must be vulnerability-specific.

---

# CodeQL Variant Analysis

CodeQL is particularly useful for deeper semantic variants.

A CodeQL query can model:

```text
Source
Sink
Data flow
Taint flow
Additional flow steps
Framework behaviour
```

This is useful when:

```text
Controller
   |
   v
Service A
   |
   v
Helper
   |
   v
Service B
   |
   v
Sink
```

cannot be represented reliably through simple textual patterns.

---

# CodeQL Data-Flow Model

Conceptually:

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
Helper
      |
      v
Dangerous API
```

A CodeQL query can search all paths matching the relevant source and sink definitions.

---

# CodeQL Path Queries

Path queries are especially useful during variant analysis because they show:

```text
Source
  |
  v
Intermediate Steps
  |
  v
Sink
```

This makes manual validation significantly easier.

---

# CodeQL Variant Workflow

```text
Confirmed Finding
       |
       v
Identify Source
       |
       v
Identify Sink
       |
       v
Write / Adapt Query
       |
       v
Run Against Database
       |
       v
Inspect Paths
       |
       v
Classify Candidates
       |
       v
Improve Models
       |
       v
Run Again
```

---

# Framework Models

Variant analysis becomes more accurate when framework-specific sources and sinks are modelled.

Examples:

```text
ASP.NET request parameters
Spring request annotations
Django request objects
Flask request objects
Express req objects
GraphQL arguments
gRPC request fields
```

---

# Custom Wrappers

Real applications frequently wrap dangerous APIs.

Example:

```python
def fetch_url(url):
    return requests.get(url)
```

If searching only:

```text
requests.get
```

you may find the wrapper but miss every caller.

Treat:

```text
fetch_url()
```

as an application-specific SSRF sink during variant analysis.

---

# Wrapper Expansion

Model:

```text
Known Sink
   |
   v
Wrapper
   |
   v
Find All References
   |
   v
Application Callers
```

This is extremely useful.

---

# Security Wrapper Analysis

The same applies to security controls.

Example:

```text
authorize()
    |
    v
canAccess()
    |
    v
PolicyEngine
```

Understand wrappers before deciding whether a route lacks authorisation.

---

# Helper Functions

If one vulnerable helper exists:

```text
buildQuery()
fetchUrl()
runCommand()
renderTemplate()
openFile()
deserialize()
```

search every caller.

A single unsafe helper can create many vulnerabilities.

---

# Shared Utility Analysis

Prioritise directories such as:

```text
utils
helpers
common
shared
core
services
lib
libraries
```

A security-sensitive bug in shared code may have wide impact.

---

# Base Classes

Security logic may exist in:

```text
BaseController
BaseService
BaseRepository
AbstractHandler
Middleware superclass
```

A variant may occur where a class bypasses or overrides the secure base behaviour.

---

# Overrides

Search:

```text
override
extends
implements
super
```

depending on language.

Review security-sensitive overrides.

---

# Inheritance Variants

Example:

```text
SecureBaseController
        |
        +--> UserController
        |
        +--> AdminController
        |
        +--> LegacyController
```

If:

```text
LegacyController
```

overrides authentication behaviour, it deserves attention.

---

# Configuration Variants

A vulnerability may result from configuration rather than code.

Examples:

```text
CORS
Authentication
Security headers
Debug mode
JWT validation
XML parser settings
Proxy trust
```

Search every environment configuration:

```text
application.yml
application-prod.yml
appsettings.json
appsettings.Production.json
.env
settings.py
config.js
config.production.js
```

---

# Environment Variants

Compare:

```text
Development
Testing
Staging
Production
```

A secure default may be overridden in one environment.

---

# Infrastructure Variants

Security may differ across:

```text
NGINX
API gateway
Kubernetes ingress
Cloud load balancer
Reverse proxy
Service mesh
```

A source-level fix may not address alternate infrastructure routes.

---

# Microservice Variant Analysis

In microservices:

```text
Service A
Service B
Service C
```

may implement the same business operation independently.

Example:

```text
User lookup
Tenant validation
Role checking
Document access
```

Search across the entire repository or organisation-controlled codebase where authorised.

---

# Monorepos

Do not restrict searches to the first application directory.

Use:

```bash
rg -n \
'pattern' \
.
```

from the repository root where appropriate.

Identify:

```text
apps/
services/
packages/
libs/
frontend/
backend/
workers/
```

---

# Cross-Language Variants

A monorepo may contain:

```text
Java backend
Node.js gateway
Python worker
JavaScript frontend
```

The same vulnerability concept may appear in several languages.

Search conceptually, not only syntactically.

---

# Cross-Protocol Variants

Always consider:

```text
REST
GraphQL
gRPC
WebSocket
Webhooks
Queues
CLI
```

The same business operation may be reachable through several protocols.

---

# Second-Order Variants

Some vulnerabilities occur when attacker input is stored first.

```text
Attacker Input
     |
     v
Database
     |
     v
Background Worker
     |
     v
Dangerous Sink
```

If one second-order issue is found, search:

```text
Who writes this field?

Who reads this field?

Where else is it consumed?
```

---

# Stored Data Is Still a Source

During variant analysis:

```text
Database Value
    !=
Trusted Value
```

if the value originally came from an attacker-controlled source.

---

# Background Worker Variants

Search:

```bash
rg -n -i \
'worker|job|queue|consumer|listener|task|scheduled' \
.
```

Then trace whether stored attacker data reaches:

```text
Commands
Templates
File paths
URLs
Parsers
Logs
```

---

# Webhook Variants

If one webhook lacks correct verification, search all webhook handlers.

```bash
rg -n -i \
'webhook|callback|event.?handler|notification' \
.
```

Compare:

```text
Signature verification
Timestamp validation
Replay protection
Event validation
```

---

# Validation Variants

Suppose one endpoint lacks:

```text
validateFilename()
```

Search every file operation.

Then determine:

```text
Which routes use the validator?

Which routes implement their own validation?

Which routes perform no equivalent validation?
```

---

# Validation Helper Search

```bash
rg -n -i \
'validate|sanitize|sanitise|escape|normalize|normalise|allowlist|whitelist' \
.
```

A validation-looking function must be inspected to determine what it actually guarantees.

---

# Partial Validation

One common variant is inconsistent validation.

```text
Route A
 |
 v
validateUrl()
 |
 v
fetch()


Route B
 |
 v
fetch()
```

The second path deserves investigation.

---

# Validation Context

A validator safe for one context may not be safe for another.

Examples:

```text
HTML escaping
SQL parameterisation
Shell argument handling
URL validation
Filesystem path validation
```

Do not treat generic `sanitize()` functions as universally protective.

---

# Variant Candidate Classification

Classify results:

```text
Confirmed Variant
Likely Variant
Needs Runtime Validation
Protected
False Positive
Not Reachable
Dead Code
Unknown
```

This prevents a large scan result set from becoming unmanageable.

---

# Candidate Tracking Table

| ID | Location | Pattern | Entry Point | Control | Status |
|---|---|---|---|---|---|
| VA-001 | `DocumentController.java` | IDOR | REST | Missing | Confirmed |
| VA-002 | `DocumentResolver.java` | IDOR | GraphQL | Unknown | Review |
| VA-003 | `DocumentGrpc.java` | IDOR | gRPC | Present | Protected |
| VA-004 | `LegacyDocument.java` | IDOR | REST | Missing | Reachability? |

---

# Variant Families

Group related findings.

Example:

```text
VA-DOCUMENT-IDOR
    |
    +-- REST read
    +-- REST delete
    +-- GraphQL read
    +-- GraphQL delete
```

This helps explain the systemic root cause.

---

# Root Cause vs Individual Findings

Sometimes variants should be reported separately.

Sometimes they are better represented as one systemic finding.

Consider:

```text
Different affected endpoints
Different privileges
Different data
Different impact
Different remediation
```

Avoid artificially splitting or merging findings.

---

# Variant Severity

Do not automatically assign the same severity to every variant.

Example:

```text
IDOR read public profile
```

may have different impact from:

```text
IDOR download confidential document
```

Severity should reflect actual impact and exploitability.

---

# Runtime Validation

Static variant discovery produces candidates.

Where appropriate and authorised:

```text
Candidate
   |
   v
Understand Route
   |
   v
Understand Expected Control
   |
   v
Safe Runtime Test
   |
   v
Confirmed / Rejected
```

---

# Burp Suite

Burp Suite is useful for validating web-accessible variants.

Use:

```text
Proxy
HTTP history
Site map
Repeater
Comparer
Logger
```

---

# Access-Control Variant Validation

For IDOR:

```text
User A -> Object A -> Allowed

User A -> Object B -> Should be denied
```

Compare source behaviour with runtime behaviour.

---

# Injection Variant Validation

For an injection candidate:

```text
Source
  |
  v
Candidate Flow
  |
  v
Sink
```

first understand:

```text
Validation
Encoding
Parameterisation
Framework behaviour
```

before dynamic testing.

---

# Do Not Blindly Validate Every Candidate

Variant analysis can produce many candidates.

Prioritise:

```text
Externally reachable
Unauthenticated
Low privilege
Sensitive operation
High-value data
Dangerous sink
Missing common control
```

---

# Prioritisation Model

```text
Candidate
   |
   v
Reachable?
   |
   v
Attacker-Controlled?
   |
   v
Sensitive Sink?
   |
   v
Security Control?
   |
   v
Potential Impact?
```

---

# High-Value Variant Targets

Prioritise variants involving:

```text
Authentication
Authorisation
Role changes
Password reset
MFA
Administrative operations
Command execution
SQL
SSRF
File access
File uploads
Deserialization
Template rendering
Sensitive exports
Secrets
Tenant boundaries
```

---

# False Positive Reduction

For every candidate ask:

```text
Is the code reachable?

Is the source attacker-controlled?

Is the sink security-sensitive?

Is there validation?

Is there sanitisation?

Is there authorisation?

Is there framework protection?

Is there infrastructure protection?

Is the data transformed?

Does the vulnerable path actually execute?
```

---

# False Negatives

Variant searches can miss issues because of:

```text
Custom wrappers
Reflection
Dynamic dispatch
Dependency injection
Generated code
Runtime configuration
Framework magic
Metaprogramming
Dynamic routes
ORM abstractions
```

Combine tools.

---

# Tool Combination

No single tool should be expected to find every variant.

Recommended model:

```text
                 CONFIRMED FINDING
                        |
                        v
                     ripgrep
                        |
                        v
                 Textual Variants
                        |
                        v
                Semgrep/OpenGrep
                        |
                        v
                Structural Variants
                        |
                        v
                     CodeQL
                        |
                        v
                 Semantic Variants
                        |
                        v
                     VS Code
                        |
                        v
                  Manual Review
                        |
                        v
                    Burp Suite
                        |
                        v
               Runtime Validation
```

---

# Recommended Practical Workflow

## Step 1 - Document the Finding

Record:

```text
Source
Sink
Missing control
Entry point
Impact
```

---

## Step 2 - Identify the Root Cause

Ask:

```text
What exactly made this exploitable?
```

---

## Step 3 - Search Exact Strings

Use:

```text
ripgrep
VS Code
```

Search:

```text
Function
Class
Sink
Object
Route
Helper
```

---

## Step 4 - Find All References

Use:

```text
Shift + F12
```

on:

```text
Vulnerable helper
Sensitive service
Repository
Security function
```

---

## Step 5 - Search Related Operations

If the finding affects:

```text
read
```

also search:

```text
create
update
delete
download
export
share
approve
```

---

## Step 6 - Search Alternate Entry Points

Check:

```text
REST
GraphQL
gRPC
WebSocket
Webhooks
Workers
Admin APIs
```

---

## Step 7 - Search Missing Controls

Identify the application's normal secure pattern.

Compare vulnerable paths against it.

---

## Step 8 - Create Structural Rules

Use:

```text
Semgrep
OpenGrep
```

to automate the pattern.

---

## Step 9 - Create Semantic Queries

Use:

```text
CodeQL
```

when cross-function data flow is required.

---

## Step 10 - Manually Review Candidates

Use Visual Studio Code to trace:

```text
Entry Point
    |
    v
Source
    |
    v
Transformations
    |
    v
Security Controls
    |
    v
Sink
```

---

## Step 11 - Validate Safely

Use runtime testing only where appropriate and authorised.

---

## Step 12 - Repeat

Every confirmed variant may reveal a broader pattern.

```text
Finding
   |
   v
Variant
   |
   v
Better Pattern
   |
   v
More Variants
```

---

# Variant Analysis Worksheet

```text
Variant Family:
VA-001

Original Finding:
...

Vulnerability Class:
...

Original Entry Point:
...

Original Source:
...

Original Sink:
...

Missing Control:
...

Root Cause:
...

Exact Search Terms:
...

Related Functions:
...

Related Objects:
...

Related Routes:
...

Related Protocols:
...

ripgrep Results:
...

Semgrep/OpenGrep Results:
...

CodeQL Results:
...

Manual Review:
...

Runtime Validation:
...

Confirmed Variants:
...

Protected Variants:
...

False Positives:
...

Remediation Pattern:
...
```

---

# Variant Review Checklist

## Root Cause

```text
[ ] Original vulnerability confirmed
[ ] Entry point identified
[ ] Source identified
[ ] Sink identified
[ ] Missing control identified
[ ] Root cause documented
```

## Text Search

```text
[ ] Vulnerable function searched
[ ] Sensitive sink searched
[ ] Object type searched
[ ] Security helper searched
[ ] Related methods searched
[ ] Related routes searched
```

## IDE Analysis

```text
[ ] Find All References used
[ ] Go to Definition used
[ ] Call hierarchy reviewed
[ ] Shared services reviewed
[ ] Shared helpers reviewed
[ ] Base classes reviewed
```

## Entry Points

```text
[ ] REST reviewed
[ ] GraphQL reviewed
[ ] gRPC reviewed
[ ] WebSockets reviewed
[ ] Webhooks reviewed
[ ] Background workers reviewed
[ ] Scheduled jobs reviewed
[ ] Administrative APIs reviewed
[ ] Internal APIs reviewed
```

## Static Analysis

```text
[ ] ripgrep used
[ ] Semgrep considered
[ ] OpenGrep considered
[ ] CodeQL considered
[ ] Project-specific rules considered
[ ] Taint analysis considered
```

## Variants

```text
[ ] Exact duplicates reviewed
[ ] Structural variants reviewed
[ ] Semantic variants reviewed
[ ] Alternate object operations reviewed
[ ] Alternate API versions reviewed
[ ] Legacy functionality reviewed
[ ] Environment variants reviewed
```

## Validation

```text
[ ] Reachability established
[ ] Attacker control established
[ ] Security controls reviewed
[ ] Runtime validation performed where appropriate
[ ] False positives documented
[ ] Impact assessed independently
```

## Remediation

```text
[ ] Common root cause identified
[ ] Systemic remediation considered
[ ] All variants included in retest
[ ] Static-analysis rule retained where useful
```

---

# Common Mistakes

## Searching Only the Vulnerable Line

Incorrect:

```text
Find exact string
     |
     v
No other matches
     |
     v
No variants
```

Semantic variants may use completely different code.

---

## Searching Only the Sink

A sink search finds candidates, not vulnerabilities.

```text
Sink
 !=
Vulnerability
```

---

## Searching Only the Source

Likewise:

```text
Request parameter
 !=
Vulnerability
```

Trace the complete path.

---

## Ignoring Secure Patterns

Understanding how the application normally implements security can be as valuable as studying the vulnerability.

```text
Secure Pattern
     |
     v
Find Deviations
```

---

## Ignoring Alternate Protocols

A REST fix may leave:

```text
GraphQL
gRPC
WebSocket
```

vulnerable.

---

## Ignoring Workers

Second-order vulnerabilities may exist in asynchronous processing.

---

## Assuming Similar Code Has Similar Impact

Each variant must be assessed independently.

---

## Reporting Every Static Match

Static matches are candidates.

```text
Static Match
    |
    v
Manual Review
    |
    v
Exploitability
```

---

## Assuming a Security Helper Is Effective

A function named:

```text
sanitize()
authorize()
validate()
```

must be inspected.

Names do not prove security properties.

---

## Ignoring Reachability

Dead or disabled code may not be exploitable.

Record it appropriately.

---

# Variant Analysis Decision Tree

```text
Confirmed vulnerability?
        |
        v
Understand root cause
        |
        v
Identify source and sink
        |
        v
Identify missing control
        |
        v
Search exact pattern
        |
        v
Other matches?
    +---+---+
    |       |
   Yes      No
    |       |
    v       v
 Review   Broaden Search
            |
            v
       Structural Search
            |
            v
       More Candidates?
         +--+--+
         |     |
        Yes    No
         |     |
         v     v
       Review Semantic Search
                 |
                 v
              CodeQL /
             Manual Flow
                 |
                 v
             Candidates
                 |
                 v
              Reachable?
              +--+--+
              |     |
             No    Yes
              |     |
              v     v
           Record  Security
                   Control?
                   +--+--+
                   |     |
                  Yes    No
                   |     |
                   v     v
                Review Candidate
                         |
                         v
                    Validate
                         |
                         v
                   Confirmed?
                    +----+----+
                    |         |
                   No        Yes
                    |         |
                    v         v
                 Reject    New Variant
                               |
                               v
                         Repeat Analysis
```

---

# Variant Analysis After Remediation

Variant analysis should also be performed after a fix.

```text
Patch
 |
 v
Understand New Security Control
 |
 v
Search Other Locations
 |
 v
Apply Equivalent Fixes
 |
 v
Retest
```

This reduces the chance of fixing only one manifestation of a systemic weakness.

---

# Turn Findings Into Detection

One of the best outcomes of variant analysis is reusable detection.

```text
Confirmed Vulnerability
        |
        v
Understand Pattern
        |
        v
Create Rule
        |
        v
Scan Repository
        |
        v
Fix Variants
        |
        v
Keep Rule
        |
        v
Prevent Regression
```

---

# Security Regression Detection

A project-specific Semgrep/OpenGrep/CodeQL rule can be added to:

```text
Developer workflow
CI/CD
Pull request scanning
Security review
```

where appropriate.

This turns a pentesting finding into a long-term security improvement.

---

# Variant Analysis and Secure Code Review

Variant analysis connects several parts of source code review:

```text
Routes
   |
   v
Sources
   |
   v
Sinks
   |
   v
Security Controls
   |
   v
Confirmed Vulnerability
   |
   v
Variant Analysis
   |
   v
Systemic Understanding
```

---

# Final Variant Analysis Model

```text
                         CONFIRMED
                        VULNERABILITY
                             |
                             v
                         ROOT CAUSE
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
            SOURCE       MISSING CONTROL    SINK
              |              |              |
              +--------------+--------------+
                             |
                             v
                       CODE PATTERN
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
       TEXTUAL           STRUCTURAL          SEMANTIC
       VARIANTS          VARIANTS            VARIANTS
          |                  |                  |
          v                  v                  v
       ripgrep          Semgrep/OpenGrep       CodeQL
          |                  |                  |
          +------------------+------------------+
                             |
                             v
                          VS CODE
                             |
                             v
                       MANUAL REVIEW
                             |
                             v
                    RUNTIME VALIDATION
                             |
                    +--------+--------+
                    |                 |
                    v                 v
                 REJECTED          CONFIRMED
                                      |
                                      v
                                  NEW VARIANT
                                      |
                                      v
                              REPEAT ANALYSIS
```

---

# Practical Mental Model

When a vulnerability is found, do not ask only:

```text
Where else is this exact code?
```

Ask:

```text
Where else can the same attacker-controlled data enter?

Where else is the same sink used?

Where else is this security control missing?

Where else is the same object accessed?

Where else is the same business operation exposed?

Where else is the same helper called?

Where else does another protocol expose this operation?

Where else was this vulnerable pattern copied?

Where else does an equivalent semantic data flow exist?
```

That is variant analysis.

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/methodology.md
docs/source-code-review/routes-and-entry-points.md
docs/source-code-review/authentication-authorisation.md
docs/source-code-review/source-to-sink-analysis.md

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

# Related Static Analysis Notes

```text
docs/source-code-review/static-analysis/index.md
docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/semgrep.md
docs/source-code-review/static-analysis/opengrep.md
docs/source-code-review/static-analysis/codeql.md
```

---

# Related Web Security Notes

```text
docs/web/attack-surface-analysis.md
docs/web/authentication.md
docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/sql-injection.md
docs/web/nosql-injection.md
docs/web/ldap-injection.md
docs/web/command-injection.md
docs/web/ssrf.md
docs/web/path-traversal.md
docs/web/file-upload.md
docs/web/deserialization.md
docs/web/ssti.md
docs/web/xss.md
docs/web/xxe.md
docs/web/mass-assignment.md
docs/web/prototype-pollution.md
docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md
```

---

# References

## CodeQL - Variant Analysis

```text
https://codeql.github.com/docs/codeql-overview/codeql-glossary/#variant-analysis
```

## CodeQL Documentation

```text
https://codeql.github.com/docs/
```

## CodeQL - Data Flow Analysis

```text
https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/
```

## CodeQL - Creating Path Queries

```text
https://codeql.github.com/docs/writing-codeql-queries/creating-path-queries/
```

## GitHub CodeQL

```text
https://github.com/github/codeql
```

## Semgrep Documentation

```text
https://semgrep.dev/docs/
```

## Semgrep - Rule Syntax

```text
https://semgrep.dev/docs/writing-rules/rule-syntax
```

## Semgrep - Taint Mode

```text
https://semgrep.dev/docs/writing-rules/data-flow/taint-mode/
```

## OpenGrep

```text
https://opengrep.dev/
```

## OpenGrep GitHub

```text
https://github.com/opengrep/opengrep
```

## ripgrep

```text
https://github.com/BurntSushi/ripgrep
```

## Visual Studio Code

```text
https://code.visualstudio.com/docs
```

## OWASP Secure Code Review Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html
```

## OWASP Code Review Guide

```text
https://owasp.org/www-project-code-review-guide/
```

## OWASP Web Security Testing Guide

```text
https://owasp.org/www-project-web-security-testing-guide/
```

## OWASP Authorization Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
```

## OWASP Input Validation Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
```

## PortSwigger Web Security Academy

```text
https://portswigger.net/web-security
```

---

# Summary

Variant analysis transforms an individual vulnerability into a systematic search strategy.

The workflow is:

```text
Confirmed Vulnerability
        |
        v
Understand Root Cause
        |
        v
Identify Source
        |
        v
Identify Sink
        |
        v
Identify Missing Control
        |
        v
Search Exact Pattern
        |
        v
Search Structural Pattern
        |
        v
Search Semantic Pattern
        |
        v
Review Alternate Entry Points
        |
        v
Manual Source-to-Sink Analysis
        |
        v
Runtime Validation
        |
        v
Confirmed Variants
        |
        v
Systemic Remediation
        |
        v
Regression Detection
```

The most important principle is:

```text
Do not stop when you find a vulnerability.

Use the vulnerability to teach you
how the application fails securely,
then search the entire attack surface
for every other place where it fails
in the same way.
```

A strong source code review therefore follows:

```text
Find
  |
  v
Understand
  |
  v
Generalise
  |
  v
Search
  |
  v
Validate
  |
  v
Repeat
```

That is the foundation of effective variant analysis.
