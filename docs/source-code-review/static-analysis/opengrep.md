# OpenGrep for Security Source Code Review

OpenGrep is an open-source static analysis engine designed for syntax-aware code searching, security analysis, custom rules and taint tracking.

It is a fork of Semgrep and maintains compatibility with Semgrep-style rules while continuing to develop additional open-source static analysis capabilities.

For security source code review, OpenGrep is particularly useful for:

```text
Finding dangerous APIs
Finding security-sensitive coding patterns
Searching for vulnerability variants
Building custom security rules
Source-to-sink taint analysis
Cross-function taint analysis within files
Reviewing framework-specific security patterns
Automating repeatable source code review
Producing JSON and SARIF results
Reusing many Semgrep-compatible rules
```

A practical source review workflow is:

```text
Repository
    |
    v
Visual Studio Code
    |
    +--> Understand application
    |
    +--> Map routes
    |
    +--> Map authentication
    |
    +--> Map authorisation
    |
    v
ripgrep
    |
    v
Fast Reconnaissance
    |
    v
OpenGrep
    |
    +--> Structural Search
    +--> Security Rules
    +--> Taint Analysis
    +--> Variant Analysis
    |
    v
Candidate Vulnerabilities
    |
    v
Manual Source-to-Sink Review
    |
    v
Dynamic Validation
    |
    v
Confirmed Finding
```

!!! warning "Authorised Security Testing"
    Use OpenGrep only against source code and applications that you are authorised to assess. An OpenGrep result is a security-review candidate, not automatic proof that a vulnerability is exploitable.

---

# Core Principle

The most important rule is:

```text
OpenGrep finding
      !=
Confirmed vulnerability
```

OpenGrep can tell you that code:

```text
Matches a security pattern
Calls a dangerous API
Contains a potential source
Contains a potential sink
Contains a possible taint flow
Uses suspicious configuration
```

It cannot automatically establish the complete security context.

The reviewer must determine:

```text
Is the code reachable?

Can an attacker influence the source?

Does the source actually reach the sink?

What transformations occur?

Is validation performed?

Is sanitisation appropriate for the sink?

Does the framework provide protection?

Does authorisation exist elsewhere?

Does infrastructure enforce the control?

Can the behaviour be triggered?

What impact is possible?
```

Use:

```text
OpenGrep Result
      |
      v
Candidate
      |
      v
Manual Data-Flow Analysis
      |
      v
Security-Control Review
      |
      v
Exploitability Analysis
      |
      v
Dynamic Validation
      |
      v
Confirmed / Rejected
```

---

# OpenGrep, Semgrep, ripgrep and CodeQL

These tools overlap, but they are not identical.

A useful mental model is:

| Tool | Main Role |
|---|---|
| ripgrep | Extremely fast text and regex search |
| OpenGrep | Open-source syntax-aware rules and taint analysis |
| Semgrep | Syntax-aware static analysis and security rules |
| CodeQL | Semantic queries and deeper program/data-flow analysis |
| VS Code | Manual code navigation and reasoning |
| Burp Suite | Dynamic web application validation |

Do not choose only one.

Use them together.

```text
ripgrep
   |
   v
Find Interesting Code
   |
   v
OpenGrep
   |
   v
Structural / Taint Analysis
   |
   v
VS Code
   |
   v
Manual Review
   |
   +--> Simple enough?
   |       |
   |       v
   |     Validate
   |
   +--> Complex flow?
           |
           v
         CodeQL
           |
           v
       Validate
```

---

# Why OpenGrep?

OpenGrep is useful when you want an open-source static analysis engine that supports Semgrep-style rules.

Important capabilities include:

```text
Semgrep-compatible rules
Custom pattern rules
Taint-mode rules
Intrafile cross-function taint analysis
Higher-order-function taint tracking
JSON output
SARIF output
Multiple languages
Self-contained binaries
Open-source development
```

OpenGrep was forked from Semgrep 1.100.0.

Since the fork, the projects have developed independently.

Therefore:

```text
Semgrep rule compatibility
        !=
Permanent feature parity
```

Always test important rules against the engine you intend to use.

---

# Language Support

OpenGrep supports many programming and configuration languages.

Security-relevant examples include:

```text
C
C++
C#
Java
Kotlin
JavaScript
TypeScript
JSX
TSX
PHP
Python
Go
Ruby
Rust
Scala
Bash
HTML
XML
YAML
JSON
Dockerfile
Terraform
Solidity
Visual Basic
Apex
Elixir
```

Language support continues to evolve.

Always check current OpenGrep documentation when relying on specific parser or taint-analysis capabilities.

---

# Installation

## Linux and macOS

The current OpenGrep project provides an installation script.

```bash
curl -fsSL \
https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh \
| bash
```

Verify:

```bash
opengrep --version
```

Help:

```bash
opengrep --help
```

Scan help:

```bash
opengrep scan --help
```

---

# Windows

The project also provides a PowerShell installation method.

```powershell
irm https://raw.githubusercontent.com/opengrep/opengrep/main/install.ps1 | iex
```

Verify:

```powershell
opengrep --version
```

---

# Manual Installation

Prebuilt binaries are available from the OpenGrep GitHub releases.

After installation:

```bash
which opengrep
```

Then:

```bash
opengrep --version
```

---

# Basic Structural Search

OpenGrep can perform quick syntax-aware searches without creating a YAML rule.

Example:

```bash
opengrep scan \
  -e 'os.system(...)' \
  -l python \
  .
```

Search Python execution calls:

```bash
opengrep scan \
  -e 'subprocess.run(...)' \
  -l python \
  .
```

Search function definitions:

```bash
opengrep scan \
  -e 'def $FUNC(...): ...' \
  -l python \
  .
```

Search method calls:

```bash
opengrep scan \
  -e '$OBJ.execute(...)' \
  -l python \
  .
```

This is useful during reconnaissance.

---

# Structural Search vs ripgrep

Suppose the code contains:

```python
subprocess.run(
    command,
    shell=True
)
```

A text search:

```bash
rg 'subprocess\.run'
```

finds text.

OpenGrep:

```bash
opengrep scan \
  -e 'subprocess.run(...)' \
  -l python \
  .
```

parses source syntax and searches structurally.

Conceptually:

```text
ripgrep

Source File
    |
    v
Characters
    |
    v
Regex
    |
    v
Text Match
```

OpenGrep:

```text
Source File
    |
    v
Parser
    |
    v
Syntax Tree
    |
    v
Structural Pattern
    |
    v
Code Match
```

Use ripgrep when speed and broad recall matter.

Use OpenGrep when code structure matters.

---

# First Security Scan

From the repository root, a ruleset can be run using:

```bash
opengrep scan \
  --config p/security-audit \
  .
```

Depending on the rule source and environment, other compatible rule configurations may also be available.

Do not assume a generic ruleset provides complete application coverage.

The purpose of the first scan is:

```text
Reconnaissance
    |
    v
Interesting Areas
    |
    v
Manual Review
    |
    v
Custom Rules
```

---

# Scan a Local Rule

Suppose:

```text
rules/command-injection.yml
```

contains a custom rule.

Run:

```bash
opengrep scan \
  -f rules/command-injection.yml \
  .
```

Or:

```bash
opengrep scan \
  --config rules/command-injection.yml \
  .
```

---

# Scan a Rule Directory

A useful structure is:

```text
rules/
├── java/
├── dotnet/
├── php/
├── python/
├── django/
├── flask/
├── nodejs/
└── javascript/
```

Run the desired rules against the target project.

---

# Recommended Source Review Structure

For repeatable assessments:

```text
security-review/
│
├── rules/
│   ├── java/
│   ├── dotnet/
│   ├── php/
│   ├── python/
│   ├── django/
│   ├── flask/
│   └── javascript/
│
├── tests/
│
├── output/
│   ├── initial.json
│   ├── taint.json
│   ├── variants.json
│   └── results.sarif
│
└── notes/
    ├── attack-surface.md
    ├── candidates.md
    └── confirmed-findings.md
```

---

# Visual Studio Code Workflow

Open the repository:

```bash
code .
```

Then:

```text
VS Code
   |
   +--> Explorer
   |
   +--> Global Search
   |
   +--> Go to Definition
   |
   +--> Find All References
   |
   +--> Call Hierarchy
   |
   +--> Integrated Terminal
   |
   v
OpenGrep
```

Recommended workflow:

```text
1. Understand project structure

2. Identify languages

3. Identify frameworks

4. Map routes

5. Map authentication

6. Map authorisation

7. Find user-input sources

8. Find dangerous sinks

9. Run OpenGrep

10. Open results in VS Code

11. Trace data manually

12. Validate findings dynamically
```

---

# Anatomy of an OpenGrep Rule

A basic rule:

```yaml
rules:
  - id: python-os-system
    languages:
      - python
    message: Review operating system command execution
    severity: WARNING
    pattern: os.system(...)
```

Important components:

```text
id
languages
message
severity
pattern
```

---

# Pattern Matching

Example:

```yaml
pattern: os.system(...)
```

Matches calls structurally resembling:

```python
os.system(command)
```

or:

```python
os.system(
    build_command()
)
```

---

# Metavariables

Metavariables capture parts of code.

Example:

```yaml
pattern: os.system($COMMAND)
```

Given:

```python
os.system(user_input)
```

then:

```text
$COMMAND
```

represents:

```text
user_input
```

Given:

```python
os.system(build_command(host))
```

it represents the expression:

```text
build_command(host)
```

---

# Ellipsis

The ellipsis:

```text
...
```

matches arbitrary syntax in many contexts.

Example:

```yaml
pattern: subprocess.run(...)
```

This allows argument differences.

---

# pattern-either

Use `pattern-either` when multiple APIs represent the same security concept.

Example:

```yaml
rules:
  - id: python-command-execution
    languages:
      - python
    message: Review command execution
    severity: WARNING

    pattern-either:
      - pattern: os.system(...)
      - pattern: os.popen(...)
      - pattern: subprocess.run(...)
      - pattern: subprocess.Popen(...)
      - pattern: subprocess.call(...)
      - pattern: subprocess.check_output(...)
```

This is useful for sink discovery.

It does not prove command injection.

---

# patterns

Multiple conditions can be combined.

Conceptually:

```yaml
patterns:
  - pattern: ...
  - pattern-inside: |
      def $FUNCTION(...):
          ...
```

This allows a rule to require context.

---

# Negative Patterns

OpenGrep-compatible rule syntax can use negative patterns to exclude known cases.

Conceptually:

```yaml
patterns:
  - pattern: dangerous(...)
  - pattern-not: known_safe(...)
```

Be careful.

An overly broad exclusion can create false negatives.

---

# Rule Severity

Common severities include:

```text
INFO
WARNING
ERROR
```

Use severity for triage.

Do not interpret:

```text
ERROR
```

as:

```text
Confirmed critical vulnerability
```

Rule severity and vulnerability severity are different concepts.

---

# Sink-First Analysis

A strong source review technique is to start from dangerous sinks.

```text
Dangerous Sink
      |
      v
Find Callers
      |
      v
Trace Arguments Backwards
      |
      v
Find Source
      |
      v
Review Validation
      |
      v
Determine Exploitability
```

OpenGrep is excellent for sink discovery.

---

# Python Command Execution

```yaml
rules:
  - id: python-command-execution
    languages:
      - python
    message: Review operating system command execution
    severity: WARNING

    pattern-either:
      - pattern: os.system(...)
      - pattern: os.popen(...)
      - pattern: subprocess.run(...)
      - pattern: subprocess.Popen(...)
      - pattern: subprocess.call(...)
      - pattern: subprocess.check_call(...)
      - pattern: subprocess.check_output(...)
```

---

# Python shell=True

A higher-interest pattern:

```yaml
rules:
  - id: python-shell-true
    languages:
      - python
    message: Review subprocess execution using shell=True
    severity: WARNING

    pattern-either:
      - pattern: subprocess.run(..., shell=True, ...)
      - pattern: subprocess.Popen(..., shell=True, ...)
      - pattern: subprocess.call(..., shell=True, ...)
      - pattern: subprocess.check_output(..., shell=True, ...)
```

Review:

```text
Can the attacker control the command?

Can the attacker control part of the command?

Is concatenation used?

Is shell expansion possible?

Are fixed arguments used?
```

---

# Java Command Execution

```yaml
rules:
  - id: java-command-execution
    languages:
      - java
    message: Review operating system command execution
    severity: WARNING

    pattern-either:
      - pattern: Runtime.getRuntime().exec(...)
      - pattern: new ProcessBuilder(...)
```

Trace:

```text
@RequestParam
      |
      v
Controller
      |
      v
Service
      |
      v
ProcessBuilder
```

---

# .NET Command Execution

```yaml
rules:
  - id: dotnet-process-execution
    languages:
      - csharp
    message: Review process execution
    severity: WARNING

    pattern-either:
      - pattern: Process.Start(...)
      - pattern: new ProcessStartInfo(...)
```

Manual review is required because safe fixed command execution is common.

---

# PHP Command Execution

```yaml
rules:
  - id: php-command-execution
    languages:
      - php
    message: Review command execution
    severity: WARNING

    pattern-either:
      - pattern: system(...)
      - pattern: exec(...)
      - pattern: shell_exec(...)
      - pattern: passthru(...)
      - pattern: popen(...)
      - pattern: proc_open(...)
```

---

# Node.js Command Execution

```yaml
rules:
  - id: node-command-execution
    languages:
      - javascript
      - typescript
    message: Review child process execution
    severity: WARNING

    pattern-either:
      - pattern: child_process.exec(...)
      - pattern: child_process.execSync(...)
      - pattern: child_process.spawn(...)
      - pattern: child_process.spawnSync(...)
      - pattern: child_process.execFile(...)
      - pattern: child_process.execFileSync(...)
```

Import aliases and destructuring must also be considered.

Example:

```javascript
const {
    exec
} = require("child_process");

exec(command);
```

A rule matching only:

```text
child_process.exec(...)
```

may miss this variant.

---

# Dynamic Code Execution

## Python

```yaml
rules:
  - id: python-dynamic-code
    languages:
      - python
    message: Review dynamic code execution
    severity: WARNING

    pattern-either:
      - pattern: eval(...)
      - pattern: exec(...)
```

---

# JavaScript

```yaml
rules:
  - id: javascript-dynamic-code
    languages:
      - javascript
      - typescript
    message: Review dynamic JavaScript execution
    severity: WARNING

    pattern-either:
      - pattern: eval(...)
      - pattern: new Function(...)
```

---

# SQL Injection Review

Do not simply search for:

```text
execute()
```

and report SQL injection.

The security question is:

```text
How was the query constructed?
```

Review:

```text
Parameterisation
Prepared statements
Raw SQL
String concatenation
Template literals
ORM escape hatches
Dynamic identifiers
Stored procedures
```

---

# Python SQL Sink Discovery

```yaml
rules:
  - id: python-sql-execution
    languages:
      - python
    message: Review SQL construction and parameterisation
    severity: INFO

    pattern-either:
      - pattern: $CURSOR.execute(...)
      - pattern: $CURSOR.executemany(...)
```

This intentionally finds safe and unsafe calls.

---

# Django Raw SQL

```yaml
rules:
  - id: django-raw-sql
    languages:
      - python
    message: Review raw SQL usage
    severity: WARNING

    pattern-either:
      - pattern: $MODEL.objects.raw(...)
      - pattern: RawSQL(...)
      - pattern: $CURSOR.execute(...)
      - pattern: $QUERYSET.extra(...)
```

---

# Java SQL Review

```yaml
rules:
  - id: java-sql-review
    languages:
      - java
    message: Review SQL construction
    severity: INFO

    pattern-either:
      - pattern: $CONNECTION.createStatement(...)
      - pattern: $STATEMENT.executeQuery(...)
      - pattern: $STATEMENT.executeUpdate(...)
      - pattern: $ENTITY.createNativeQuery(...)
      - pattern: $ENTITY.createQuery(...)
```

---

# .NET SQL Review

```yaml
rules:
  - id: dotnet-sql-review
    languages:
      - csharp
    message: Review SQL construction and parameterisation
    severity: INFO

    pattern-either:
      - pattern: $DB.Database.ExecuteSqlRaw(...)
      - pattern: $DB.Database.FromSqlRaw(...)
      - pattern: new SqlCommand(...)
```

---

# PHP SQL Review

```yaml
rules:
  - id: php-sql-review
    languages:
      - php
    message: Review SQL construction and parameterisation
    severity: INFO

    pattern-either:
      - pattern: mysqli_query(...)
      - pattern: $DB->query(...)
      - pattern: $DB->exec(...)
      - pattern: $DB->prepare(...)
```

`prepare()` may indicate safer parameterisation.

Do not report it as SQL injection merely because it matched.

---

# NoSQL Injection Review

Useful Node.js areas include:

```text
find()
findOne()
findById()
updateOne()
updateMany()
deleteOne()
aggregate()
$where
$regex
```

The important question is whether attacker-controlled objects or operators can alter query semantics.

Conceptually:

```text
req.body
   |
   v
Mongo Query
   |
   v
Database
```

Search:

```bash
rg -n \
'findOne|findById|updateOne|aggregate|\$where|\$regex' \
-g '*.js' \
-g '*.ts' \
.
```

Use OpenGrep to model application-specific unsafe query construction after identifying the database library.

---

# LDAP Injection Review

Search Java:

```text
DirContext
InitialDirContext
search()
SearchControls
```

Search .NET:

```text
DirectorySearcher
DirectoryEntry
```

Search PHP:

```text
ldap_search
ldap_bind
ldap_list
```

The important flow is:

```text
Attacker Input
      |
      v
LDAP Filter Construction
      |
      v
LDAP Search
```

---

# SSRF Review

## Python

```yaml
rules:
  - id: python-http-client
    languages:
      - python
    message: Review outbound HTTP destination
    severity: WARNING

    pattern-either:
      - pattern: requests.get(...)
      - pattern: requests.post(...)
      - pattern: requests.request(...)
      - pattern: httpx.get(...)
      - pattern: httpx.post(...)
      - pattern: httpx.request(...)
      - pattern: urllib.request.urlopen(...)
```

---

# Java

```yaml
rules:
  - id: java-http-client
    languages:
      - java
    message: Review outbound request destination
    severity: WARNING

    pattern-either:
      - pattern: new URL(...)
      - pattern: URI.create(...)
      - pattern: $REST.getForObject(...)
      - pattern: $REST.getForEntity(...)
      - pattern: $CLIENT.send(...)
```

---

# .NET

```yaml
rules:
  - id: dotnet-http-client
    languages:
      - csharp
    message: Review outbound HTTP request destination
    severity: WARNING

    pattern-either:
      - pattern: $CLIENT.GetAsync(...)
      - pattern: $CLIENT.GetStringAsync(...)
      - pattern: $CLIENT.SendAsync(...)
```

---

# PHP

```yaml
rules:
  - id: php-outbound-request
    languages:
      - php
    message: Review outbound request destination
    severity: WARNING

    pattern-either:
      - pattern: curl_init(...)
      - pattern: file_get_contents(...)
      - pattern: fopen(...)
```

Some APIs also perform filesystem operations.

Context matters.

---

# Node.js

```yaml
rules:
  - id: node-http-client
    languages:
      - javascript
      - typescript
    message: Review outbound request destination
    severity: WARNING

    pattern-either:
      - pattern: fetch(...)
      - pattern: axios.get(...)
      - pattern: axios.post(...)
      - pattern: axios.request(...)
```

---

# SSRF Validation Model

Finding:

```text
requests.get(url)
```

is only the beginning.

Trace:

```text
HTTP Parameter
     |
     v
URL Parser
     |
     v
Validation
     |
     v
DNS Resolution
     |
     v
HTTP Client
```

Review:

```text
Allowed schemes
Allowed hosts
Allowed ports
Redirect handling
DNS rebinding assumptions
IPv4
IPv6
Loopback
Private networks
Link-local ranges
Cloud metadata
URL parser inconsistencies
```

---

# Path Traversal Review

## Python

```yaml
rules:
  - id: python-file-access
    languages:
      - python
    message: Review filesystem path construction
    severity: INFO

    pattern-either:
      - pattern: open(...)
      - pattern: pathlib.Path(...)
```

---

# Java

```yaml
rules:
  - id: java-file-access
    languages:
      - java
    message: Review filesystem path construction
    severity: INFO

    pattern-either:
      - pattern: new File(...)
      - pattern: Paths.get(...)
      - pattern: Path.of(...)
      - pattern: new FileInputStream(...)
      - pattern: new FileOutputStream(...)
```

---

# .NET

```yaml
rules:
  - id: dotnet-file-access
    languages:
      - csharp
    message: Review filesystem path construction
    severity: INFO

    pattern-either:
      - pattern: File.Open(...)
      - pattern: File.ReadAllText(...)
      - pattern: File.ReadAllBytes(...)
      - pattern: File.WriteAllText(...)
      - pattern: File.WriteAllBytes(...)
      - pattern: Path.Combine(...)
```

`Path.Combine()` is not inherently vulnerable.

---

# Node.js

```yaml
rules:
  - id: node-file-access
    languages:
      - javascript
      - typescript
    message: Review filesystem path construction
    severity: INFO

    pattern-either:
      - pattern: fs.readFile(...)
      - pattern: fs.readFileSync(...)
      - pattern: fs.writeFile(...)
      - pattern: fs.writeFileSync(...)
      - pattern: fs.createReadStream(...)
      - pattern: fs.createWriteStream(...)
```

---

# File Upload Review

## Flask

```yaml
rules:
  - id: flask-file-upload
    languages:
      - python
    message: Review uploaded file validation and storage
    severity: INFO

    pattern: request.files[...]
```

---

# Django

```yaml
rules:
  - id: django-file-upload
    languages:
      - python
    message: Review uploaded file validation and storage
    severity: INFO

    pattern: request.FILES[...]
```

---

# Java

```yaml
rules:
  - id: java-file-upload
    languages:
      - java
    message: Review uploaded filename and storage
    severity: INFO

    pattern-either:
      - pattern: $FILE.getOriginalFilename()
      - pattern: $FILE.transferTo(...)
```

---

# Node.js

```yaml
rules:
  - id: node-file-upload
    languages:
      - javascript
      - typescript
    message: Review uploaded file handling
    severity: INFO

    pattern-either:
      - pattern: req.file
      - pattern: req.files
```

Review:

```text
Filename
Extension
MIME type
Magic bytes
Destination
Generated name
Overwrite behaviour
Path traversal
Archive extraction
Image/document processing
Public accessibility
Execution possibility
```

---

# Deserialisation Review

## Python

```yaml
rules:
  - id: python-deserialization
    languages:
      - python
    message: Review deserialisation of potentially untrusted data
    severity: WARNING

    pattern-either:
      - pattern: pickle.load(...)
      - pattern: pickle.loads(...)
      - pattern: yaml.load(...)
      - pattern: marshal.loads(...)
```

YAML behaviour depends on the library and loader configuration.

---

# Java

```yaml
rules:
  - id: java-deserialization
    languages:
      - java
    message: Review deserialisation trust boundary
    severity: WARNING

    pattern-either:
      - pattern: new ObjectInputStream(...)
      - pattern: $STREAM.readObject(...)
      - pattern: new XMLDecoder(...)
```

---

# PHP

```yaml
rules:
  - id: php-unserialize
    languages:
      - php
    message: Review unserialize input trust boundary
    severity: WARNING

    pattern: unserialize(...)
```

---

# .NET

```yaml
rules:
  - id: dotnet-deserialization
    languages:
      - csharp
    message: Review serializer and input trust boundary
    severity: WARNING

    pattern-either:
      - pattern: new BinaryFormatter(...)
      - pattern: new NetDataContractSerializer(...)
```

---

# XML and XXE Review

Search for:

```text
XML parsers
DocumentBuilderFactory
SAXParserFactory
XMLInputFactory
XmlReader
XmlDocument
SimpleXML
DOMDocument
lxml
ElementTree
```

The security question is not:

```text
Does XML parsing exist?
```

It is:

```text
Can attacker-controlled XML reach a parser configured to resolve dangerous external resources?
```

---

# SSTI Review

Search template engines such as:

```text
Jinja2
Twig
Freemarker
Velocity
Thymeleaf
Razor
EJS
Pug
Handlebars
```

The important distinction:

```text
Attacker-controlled template data
```

versus:

```text
Attacker-controlled template source
```

SSTI generally requires influence over template syntax or evaluation, not merely data passed into a safely defined template.

---

# DOM XSS Sink Discovery

```yaml
rules:
  - id: javascript-html-sink
    languages:
      - javascript
      - typescript
    message: Review HTML sink for attacker-controlled data
    severity: WARNING

    pattern-either:
      - pattern: $ELEMENT.innerHTML = $VALUE
      - pattern: $ELEMENT.outerHTML = $VALUE
      - pattern: $ELEMENT.insertAdjacentHTML(...)
      - pattern: document.write(...)
      - pattern: document.writeln(...)
```

A sink match is not automatic XSS.

Trace the source.

---

# DOM XSS Sources

Common sources include:

```text
location.href
location.search
location.hash
document.URL
document.documentURI
document.referrer
window.name
event.data
localStorage
sessionStorage
API responses
```

A complete model:

```text
location.search
      |
      v
URLSearchParams
      |
      v
User Value
      |
      v
Transformation
      |
      v
innerHTML
```

---

# React

Search:

```text
dangerouslySetInnerHTML
```

A structural rule can help identify use of raw HTML rendering.

The presence of the API is not automatic XSS.

Review:

```text
Source
Sanitisation
DOMPurify configuration
Trusted Types
CSP
```

---

# Angular

Search:

```text
[innerHTML]
DomSanitizer
bypassSecurityTrustHtml
bypassSecurityTrustScript
bypassSecurityTrustUrl
bypassSecurityTrustResourceUrl
```

Example:

```bash
rg -n \
'bypassSecurityTrust(Html|Script|Url|ResourceUrl)|\[innerHTML\]' \
-g '*.ts' \
-g '*.html' \
.
```

Bypass APIs deserve review because they intentionally bypass Angular security handling.

---

# Vue

Search:

```bash
rg -n \
'v-html' \
-g '*.vue' \
.
```

Review whether the value can contain attacker-controlled HTML.

---

# Open Redirect

```yaml
rules:
  - id: javascript-navigation
    languages:
      - javascript
      - typescript
    message: Review attacker influence over navigation
    severity: WARNING

    pattern-either:
      - pattern: location.href = $URL
      - pattern: window.location = $URL
      - pattern: location.assign($URL)
      - pattern: location.replace($URL)
      - pattern: window.open($URL, ...)
```

---

# Authentication Review

OpenGrep can help locate authentication controls.

Look for:

```text
Authentication middleware
Login handlers
Password verification
Session creation
JWT verification
OAuth callbacks
SAML handlers
MFA verification
Password reset flows
```

Do not expect generic static analysis to understand every custom authentication design automatically.

---

# Authorisation Review

Authorisation is one of the most important areas for manual review.

Model:

```text
Route
  |
  v
Authentication
  |
  v
Object Identifier
  |
  v
Object Retrieval
  |
  v
Authorisation Check
  |
  v
Sensitive Operation
```

Static analysis can identify:

```text
Object lookups
Permission functions
Authorisation annotations
Role checks
Tenant checks
Ownership checks
```

But the reviewer must understand the intended policy.

---

# Spring Security

Search:

```text
SecurityFilterChain
authorizeHttpRequests
requestMatchers
permitAll
authenticated
hasRole
hasAuthority
@PreAuthorize
@PostAuthorize
@Secured
```

Example:

```yaml
rules:
  - id: spring-permit-all
    languages:
      - java
    message: Review routes covered by permitAll
    severity: INFO

    pattern: $X.permitAll()
```

Do not report `permitAll()` itself as a vulnerability.

Determine which routes it affects.

---

# ASP.NET Core

Search:

```text
[Authorize]
[AllowAnonymous]
RequireAuthorization
AddAuthorization
UseAuthentication
UseAuthorization
Policies
Roles
Claims
```

Candidate:

```yaml
rules:
  - id: dotnet-allow-anonymous
    languages:
      - csharp
    message: Review anonymous endpoint exposure
    severity: INFO

    pattern: |
      [AllowAnonymous]
      $DECL
```

Rules may need adjustment for different declaration forms.

---

# Django

Review:

```text
@login_required
permission_required
user_passes_test
IsAuthenticated
permission_classes
authentication_classes
get_object()
get_queryset()
```

Potentially interesting:

```text
@csrf_exempt
```

Example:

```yaml
rules:
  - id: django-csrf-exempt
    languages:
      - python
    message: Review why CSRF protection is disabled
    severity: WARNING

    pattern: |
      @csrf_exempt
      def $FUNCTION(...):
          ...
```

CSRF exemption is not automatically exploitable.

---

# Flask

Because Flask applications often implement security controls manually, inspect:

```text
before_request
Decorators
Session checks
JWT middleware
Blueprint middleware
Role checks
Ownership checks
```

Search:

```bash
rg -n \
'@.*route|before_request|login_required|authorize|permission|role|session|jwt' \
-g '*.py' \
.
```

---

# Express

Review:

```text
router.use()
app.use()
authenticate()
authorize()
isAdmin()
requireRole()
requirePermission()
```

Important:

```text
Middleware order matters.
```

An authorisation middleware may exist but not cover every route.

---

# IDOR / BOLA

The important flow is:

```text
Attacker-Controlled Object ID
          |
          v
Object Lookup
          |
          v
Authorisation?
          |
          v
Sensitive Object
```

Search:

```bash
rg -n \
'findById|findOne|findUnique|findFirst|objects\.get|FindAsync|SingleOrDefault' \
.
```

OpenGrep becomes particularly valuable after identifying the application's normal authorisation helper.

Example:

```text
checkOwnership()
```

Then perform variant analysis around code paths that access sensitive objects.

---

# Mass Assignment

Example Node.js:

```javascript
Object.assign(
    user,
    req.body
);
```

Rule:

```yaml
rules:
  - id: node-request-body-object-assign
    languages:
      - javascript
      - typescript
    message: Review request-body mass assignment
    severity: WARNING

    pattern: Object.assign($OBJECT, req.body)
```

Review sensitive fields such as:

```text
role
isAdmin
permissions
tenantId
status
verified
balance
ownerId
```

---

# JWT Review

## Python

```yaml
rules:
  - id: python-jwt-review
    languages:
      - python
    message: Review JWT handling
    severity: INFO

    pattern-either:
      - pattern: jwt.decode(...)
      - pattern: jwt.encode(...)
```

---

# Node.js

```yaml
rules:
  - id: node-jwt-review
    languages:
      - javascript
      - typescript
    message: Review JWT handling
    severity: INFO

    pattern-either:
      - pattern: jwt.verify(...)
      - pattern: jwt.decode(...)
      - pattern: jwt.sign(...)
```

Review:

```text
Signature verification
Algorithm restrictions
Issuer
Audience
Expiration
Not-before
Key selection
Key retrieval
Claims
Authorisation
```

---

# OAuth and OIDC

Search:

```text
authorize
callback
redirect_uri
state
nonce
code_verifier
code_challenge
issuer
audience
openid
userinfo
```

Static analysis can identify handlers and configuration.

Protocol correctness still requires understanding the entire flow.

---

# SAML

Search:

```text
SAMLResponse
RelayState
Assertion
Signature
Audience
Recipient
Destination
InResponseTo
```

Review:

```text
Signature validation
Assertion validation
Audience
Recipient
Destination
Replay
Identity mapping
Authorisation after authentication
```

---

# Password Reset

Use ripgrep first:

```bash
rg -ni \
'forgot.?password|reset.?password|password.?reset|reset.?token|recovery' \
.
```

Then inspect:

```text
Token generation
Token entropy
Token storage
Expiration
Single use
User enumeration
Session invalidation
Password policy
Host-derived links
```

---

# MFA

Search:

```text
totp
otp
mfa
2fa
verifyCode
backupCode
recoveryCode
```

Review whether MFA is enforced at:

```text
Initial login
Sensitive actions
Session upgrade
Password reset
Account recovery
API authentication
```

---

# Taint Analysis

Pattern rules answer:

```text
Does this code contain something interesting?
```

Taint analysis asks:

```text
Can untrusted data reach a dangerous operation?
```

This is one of the most important differences.

```text
SOURCE
   |
   v
Untrusted Data
   |
   v
Transformation
   |
   v
Function
   |
   v
SINK
```

---

# Basic Taint Rule

Conceptually:

```yaml
rules:
  - id: example-taint
    languages:
      - python

    message: Untrusted data may reach a sensitive sink

    severity: WARNING

    mode: taint

    pattern-sources:
      - pattern: source(...)

    pattern-sinks:
      - pattern: sink(...)
```

---

# Sources

A source represents potentially untrusted data.

Examples:

```text
HTTP parameters
Request bodies
Headers
Cookies
Uploaded files
GraphQL arguments
WebSocket messages
gRPC fields
Queue messages
Database-stored attacker data
```

---

# Sinks

A sink represents a security-sensitive operation.

Examples:

```text
SQL execution
OS command execution
Filesystem access
HTTP requests
Template evaluation
Dynamic code execution
HTML rendering
Redirects
Deserialisation
LDAP filters
XML parsing
```

---

# Sanitizers

Taint rules can model sanitizers.

Conceptually:

```yaml
pattern-sanitizers:
  - pattern: validate(...)
```

But only model a function as a sanitizer if you understand its guarantees.

A function named:

```text
sanitize()
```

does not automatically make data safe.

---

# Context-Specific Sanitisation

Remember:

```text
HTML encoding
    !=
SQL protection

SQL parameterisation
    !=
Shell escaping

Shell escaping
    !=
URL validation

URL validation
    !=
Path containment
```

Security controls are context-specific.

---

# Flask Command Injection Taint Rule

```yaml
rules:
  - id: flask-request-to-os-system

    languages:
      - python

    message: Flask request data may reach os.system()

    severity: ERROR

    mode: taint

    pattern-sources:
      - pattern: request.args.get(...)
      - pattern: request.form.get(...)
      - pattern: request.values.get(...)

    pattern-sinks:
      - pattern: os.system(...)
```

Example:

```python
@app.route("/ping")
def ping():
    host = request.args.get("host")
    os.system("ping -c 1 " + host)
    return "done"
```

Flow:

```text
request.args.get()
       |
       v
      host
       |
       v
String Construction
       |
       v
os.system()
```

---

# Flask SSRF Taint Rule

```yaml
rules:
  - id: flask-request-to-http-client

    languages:
      - python

    message: Flask request data may reach an outbound HTTP request

    severity: WARNING

    mode: taint

    pattern-sources:
      - pattern: request.args.get(...)
      - pattern: request.form.get(...)
      - pattern: request.values.get(...)

    pattern-sinks:
      - pattern: requests.get(...)
      - pattern: requests.post(...)
      - pattern: requests.request(...)
```

This identifies possible flows.

It does not determine whether URL validation prevents SSRF.

---

# Cross-Function Taint Analysis

One particularly important OpenGrep capability is:

```text
--taint-intrafile
```

This enables taint tracking across function boundaries within the same file.

Without it, a taint flow may be limited by function boundaries.

Conceptually:

```python
def get_input():
    return source()

def helper(value):
    return value

def main():
    data = get_input()
    result = helper(data)
    sink(result)
```

Flow:

```text
source()
   |
   v
get_input()
   |
   v
main()
   |
   v
helper()
   |
   v
sink()
```

Run:

```bash
opengrep scan \
  -f taint-rule.yml \
  example.py \
  --taint-intrafile
```

This capability is extremely useful for security review because real applications frequently use helper functions.

---

# Intrafile Does Not Mean Whole Program

Important distinction:

```text
--taint-intrafile
```

means cross-function analysis within a file.

Do not automatically interpret it as:

```text
Complete whole-program interprocedural analysis across the repository
```

Complex cross-file flows may still require:

```text
Manual tracing
Custom rules
CodeQL
Other static analysis
Dynamic validation
```

---

# Cross-Function Example

Suppose:

```python
def get_target():
    return request.args.get("url")

def fetch(url):
    return requests.get(url)

@app.route("/preview")
def preview():
    target = get_target()
    return fetch(target).text
```

A basic local flow may be difficult for simple taint analysis.

With intrafile cross-function analysis:

```text
request.args
     |
     v
get_target()
     |
     v
preview()
     |
     v
fetch()
     |
     v
requests.get()
```

becomes analysable within the same file.

---

# Higher-Order Functions

OpenGrep's intrafile taint work also includes support for higher-order-function patterns.

This matters especially for JavaScript and TypeScript.

Example:

```javascript
const input = source();

const values = [input];

values.forEach((value) => {
    sink(value);
});
```

Conceptually:

```text
source()
   |
   v
Array
   |
   v
forEach()
   |
   v
Callback Parameter
   |
   v
sink()
```

Modern JavaScript frequently uses:

```text
map()
filter()
reduce()
forEach()
callbacks
custom higher-order functions
```

Taint analysis that understands these patterns can provide better coverage.

---

# Collections

Taint can also move through collections.

Example:

```text
User Input
   |
   v
List / Map
   |
   v
Collection Operation
   |
   v
Retrieved Value
   |
   v
Sink
```

This matters for:

```text
Java collections
JavaScript arrays
Maps
Lists
Dictionaries
```

Still validate findings manually.

---

# Dataflow Traces

OpenGrep can display data-flow traces for taint findings.

Example:

```bash
opengrep scan \
  --dataflow-traces \
  -f rule.yml \
  .
```

This can make triage significantly easier.

Conceptually:

```text
Source
  |
  v
Assignment
  |
  v
Function
  |
  v
Transformation
  |
  v
Sink
```

Use the trace as a guide.

Then inspect the actual source code in VS Code.

---

# Testing Rules

Security rules should be tested.

Example test:

```python
def vulnerable():
    value = source()

    # ruleid: example-taint
    sink(value)


def safe():
    value = "fixed"

    # ok: example-taint
    sink(value)
```

Run:

```bash
opengrep test \
  --config rule.yml \
  test_rule.py
```

OpenGrep supports multiple target files for rule testing.

Example:

```bash
opengrep test \
  --config rule.yml \
  test_python.py \
  test_python_variants.py
```

---

# Validate Rule Syntax

Validate a rule:

```bash
opengrep validate rule.yml
```

Use this before relying on a new rule.

---

# Rule Development Workflow

```text
Write Rule
   |
   v
Validate
   |
   v
Test Positive Cases
   |
   v
Test Negative Cases
   |
   v
Run Against Repository
   |
   v
Review False Positives
   |
   v
Review False Negatives
   |
   v
Refine
   |
   v
Production Rule
```

---

# Positive Tests

Positive tests should cover:

```text
Direct call
Multiline call
Alias
Wrapper
Different argument order
Nested expression
Cross-function flow
Collection flow
Framework-specific variant
```

---

# Negative Tests

Negative tests should cover:

```text
Constant input
Correct parameterisation
Validated input
Correct sanitisation
Safe API
Test-only false positive
Different unrelated API
```

---

# Rule Naming

Use descriptive rule IDs.

Good:

```text
flask-request-to-os-system
django-request-to-raw-sql
spring-request-to-processbuilder
dotnet-request-to-httpclient
node-request-to-child-process
javascript-location-to-innerhtml
```

Avoid:

```text
rule1
test
bad
vulnerability
```

---

# Variant Analysis

One of the strongest uses of OpenGrep is variant analysis.

```text
Confirmed Vulnerability
        |
        v
Understand Root Cause
        |
        v
Identify Code Pattern
        |
        v
Create OpenGrep Rule
        |
        v
Scan Repository
        |
        v
Find Similar Instances
```

This often provides more value than generic security rules.

---

# Example Variant Analysis

Suppose manual review finds:

```java
public void executeReport(
    String command
) throws Exception {

    Runtime.getRuntime().exec(command);
}
```

The application repeatedly uses:

```text
executeReport(...)
```

Create:

```yaml
rules:
  - id: application-execute-report
    languages:
      - java
    message: Review custom command execution helper
    severity: ERROR

    pattern: executeReport(...)
```

Scan:

```bash
opengrep scan \
  -f rules/application-execute-report.yml \
  .
```

Now inspect every caller.

---

# Variant Analysis Workflow

```text
1. Confirm one vulnerability manually

2. Determine the vulnerable primitive

3. Identify helper functions

4. Identify wrappers

5. Write structural rule

6. Write taint rule if useful

7. Create positive tests

8. Create negative tests

9. Run OpenGrep

10. Triage results

11. Refine rule

12. Scan related authorised repositories

13. Use CodeQL if the flow is too complex
```

---

# Project-Specific Rules

Generic rule:

```text
Find os.system()
```

Project-specific rule:

```text
Find every call to executeDiagnosticCommand()
```

Generic:

```text
Find requests.get()
```

Project-specific:

```text
Find every call to fetchExternalResource()
```

Generic:

```text
Find cursor.execute()
```

Project-specific:

```text
Find every call to runReportQuery()
```

Once the architecture is understood, project-specific rules usually become much more valuable.

---

# Authentication Variant Analysis

Suppose the normal pattern is:

```java
@PreAuthorize("hasAuthority('ADMIN')")
public void deleteUser(...) {
```

During review, you may want to identify related sensitive operations and compare their authorisation.

Do not automatically write a rule that assumes every function without the annotation is vulnerable.

Authorisation may exist:

```text
At controller level
At class level
In middleware
In filters
In service logic
At API gateway level
```

Missing-control analysis requires careful architecture knowledge.

---

# Tenant Isolation

For multi-tenant applications, look for:

```text
tenantId
organisationId
organizationId
accountId
customerId
workspaceId
```

Model:

```text
Authenticated User
      |
      v
Tenant Context
      |
      v
Object ID
      |
      v
Database Query
      |
      v
Tenant Constraint?
```

A useful review question is:

```text
Does every sensitive object query enforce the tenant boundary?
```

OpenGrep can help search for repository methods that omit the expected tenant parameter.

---

# Business Logic

Static analysis is weaker at generic business logic.

Examples:

```text
Coupon reuse
Price manipulation
Approval bypass
Account-state bypass
Workflow skipping
Duplicate redemption
Negative quantity
Tenant workflow errors
```

But once a broken pattern is known:

```text
Manual Discovery
      |
      v
Broken Function
      |
      v
Structural Pattern
      |
      v
OpenGrep Rule
      |
      v
Variant Search
```

becomes powerful.

---

# Race Conditions

OpenGrep can help locate:

```text
Read-modify-write patterns
Transaction handling
Locking
Atomic operations
Concurrency checks
```

But race-condition exploitability usually depends on runtime behaviour.

Review:

```text
Transactions
Isolation levels
Database constraints
Optimistic locking
Distributed locks
External services
```

---

# Rate Limiting

OpenGrep can identify:

```text
Rate-limit middleware
Throttle decorators
Quota functions
Login attempt counters
Password reset limits
OTP attempt limits
```

But:

```text
No rate limiter in source
      !=
No rate limiting in production
```

Controls may exist in:

```text
CDN
WAF
API gateway
Reverse proxy
Service mesh
```

---

# HTTP Security Headers

Search:

```text
Content-Security-Policy
Strict-Transport-Security
X-Frame-Options
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
```

Remember:

```text
Missing in application source
        !=
Missing in HTTP response
```

Infrastructure may inject headers.

---

# Host Header and Proxy Trust

Review:

```text
Host
X-Forwarded-Host
X-Forwarded-Proto
Forwarded
trust proxy
absolute URL generation
password reset URLs
OAuth callback URLs
```

Potential flow:

```text
Host Header
    |
    v
Framework
    |
    v
Absolute URL
    |
    v
Password Reset Email
```

---

# HTTP Request Smuggling

OpenGrep cannot prove HTTP request smuggling merely by inspecting application code.

It can help locate:

```text
Custom HTTP parsers
Content-Length processing
Transfer-Encoding processing
Proxy code
Header rewriting
```

Actual exploitability depends on the entire HTTP processing chain.

---

# Web Cache Security

Search:

```text
Cache-Control
Vary
cache keys
custom caching
reverse proxy configuration
CDN configuration
```

Cache poisoning and deception often require runtime testing.

---

# GraphQL

Search:

```text
Resolver
Mutation
Query
Subscription
GraphQL
DataFetcher
```

Model:

```text
GraphQL Argument
      |
      v
Resolver
      |
      v
Authorisation
      |
      v
Service
      |
      v
Database
```

Object-level authorisation is particularly important.

---

# gRPC

Review:

```text
.proto files
service definitions
RPC methods
interceptors
authentication
authorisation
message fields
```

Model:

```text
gRPC Message
     |
     v
RPC Handler
     |
     v
Authorisation
     |
     v
Service
     |
     v
Sensitive Sink
```

---

# WebSockets

Review:

```text
Connection authentication
Message handlers
Message-level authorisation
Room access
Channel access
Subscriptions
Object IDs
Input validation
```

Authentication during the initial handshake does not automatically authorise every subsequent operation.

---

# Background Jobs

Static analysis should not stop at HTTP controllers.

Search:

```text
cron
scheduler
worker
queue
consumer
listener
job
task
background
```

Potential second-order flow:

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

---

# Second-Order Vulnerabilities

Example:

```text
Attacker Input
      |
      v
Stored in Database
      |
      v
Later Retrieved
      |
      v
Background Worker
      |
      v
Process Execution
```

Simple direct taint analysis may not model every persistence boundary.

Always ask:

```text
Who originally controlled this data?
```

---

# Trust Boundaries

Do not automatically trust data because it comes from:

```text
Database
Cache
Message queue
Internal API
File
Environment
Microservice
Webhook
```

The important question is:

```text
What was the original source?
```

---

# Secrets

OpenGrep can search for suspicious hardcoded credentials.

But dedicated tools should also be used.

Examples:

```text
TruffleHog
Git history analysis
Repository search
Secret scanners
```

Do not report every:

```text
password =
token =
secret =
```

as a vulnerability.

Determine whether the value is an actual credential and what it can access.

---

# Cryptography

Search:

```text
MD5
SHA1
DES
ECB
static IV
hardcoded key
random
PRNG
TLS verification disabled
certificate validation bypass
```

Context matters.

For example:

```text
SHA-1 used for a non-security cache key
```

is different from:

```text
SHA-1 used for password storage
```

---

# Dependency Security

OpenGrep is primarily source-code static analysis.

Use dedicated dependency tools as well:

```text
OSV-Scanner
npm audit
pip-audit
Trivy
Composer audit
Maven tooling
Gradle tooling
NuGet tooling
```

Use OpenGrep to identify:

```text
Unsafe library usage
Deprecated security APIs
Application-specific misuse
```

---

# Ignore Files

OpenGrep supports `.semgrepignore` compatibility.

Example:

```text
node_modules/
vendor/
dist/
build/
coverage/
generated/
```

Be careful when excluding:

```text
vendor/
generated/
third_party/
```

because security-sensitive code can exist there.

Review exclusions before scanning.

---

# Custom Ignore Filename

OpenGrep supports specifying a custom ignore file.

Conceptually:

```bash
opengrep scan \
  --semgrepignore-filename=<file> \
  ...
```

This can be useful when maintaining separate:

```text
Development exclusions
Security-review exclusions
```

---

# Include and Exclude Paths

Example:

```bash
opengrep scan \
  --config rules/ \
  --include='src/**' \
  --exclude='**/test/**' \
  .
```

Review what you exclude.

Tests can sometimes reveal:

```text
Hidden endpoints
Default credentials
Security assumptions
Internal APIs
Feature flags
Debug functionality
```

---

# force-exclude

OpenGrep also provides:

```text
--force-exclude
```

for applying include/exclude behaviour to explicitly passed targets where appropriate.

Example concept:

```bash
opengrep scan \
  --force-exclude \
  --exclude='**/vendor/**' \
  -f rule.yml \
  .
```

Check current CLI help for exact behaviour in your installed version.

---

# JSON Output

For automation:

```bash
opengrep scan \
  -f rules/ \
  --json \
  -o opengrep.json \
  .
```

JSON is useful for:

```text
Scripts
Dashboards
Triage tooling
Result comparison
CI/CD
```

---

# SARIF Output

SARIF integrates well with security tooling and code-scanning systems.

```bash
opengrep scan \
  -f rules/ \
  --sarif \
  -o opengrep.sarif \
  .
```

---

# Data-Flow Output

For taint analysis:

```bash
opengrep scan \
  --dataflow-traces \
  -f taint-rule.yml \
  .
```

This helps show:

```text
Source
  |
  v
Propagation
  |
  v
Sink
```

---

# Save Assessment Evidence

Recommended:

```text
review/
├── opengrep/
│   ├── initial.json
│   ├── sinks.json
│   ├── taint.json
│   ├── intrafile.json
│   ├── variants.json
│   ├── results.sarif
│   └── triage.md
│
├── ripgrep/
│   ├── routes.txt
│   ├── sources.txt
│   └── sinks.txt
│
└── findings/
```

---

# Record Tool Version

Always record:

```bash
opengrep --version
```

Example evidence:

```text
Tool:
OpenGrep

Version:
<version>

Repository:
<repository>

Branch:
<branch>

Commit:
<commit hash>

Rules:
rules/

Date:
<assessment date>
```

This improves reproducibility.

---

# Triage Template

```text
ID:
OG-001

Rule:
flask-request-to-os-system

File:
src/routes/tools.py

Line:
84

Potential Vulnerability:
Command Injection

Source:
request.args.get("host")

Sink:
os.system()

Reachable:
Yes / No / Unknown

Attacker Controlled:
Yes / No / Unknown

Validation:
None / Present / Unknown

Sanitisation:
None / Present / Unknown

Security Controls:
...

Data Flow:
...

Dynamic Validation:
...

Status:
Investigating / Confirmed / False Positive

Notes:
...
```

---

# Finding Validation Model

```text
OpenGrep Match
      |
      v
Reachable?
      |
      +--> No
      |     |
      |     v
      |   Reject
      |
      v
Attacker-Controlled Source?
      |
      +--> No
      |     |
      |     v
      |   Review Trust Boundary
      |
      v
Source Reaches Sink?
      |
      +--> No
      |     |
      |     v
      |   Reject
      |
      v
Validation?
      |
      +--> Effective
      |     |
      |     v
      |   Protected
      |
      v
Sanitisation?
      |
      +--> Effective for Sink
      |     |
      |     v
      |   Protected
      |
      v
Framework Protection?
      |
      +--> Effective
      |     |
      |     v
      |   Protected
      |
      v
Security Impact?
      |
      v
Dynamic Validation
      |
      v
Confirmed Finding
```

---

# Dynamic Validation with Burp Suite

For web applications:

```text
OpenGrep
   |
   v
Candidate Vulnerability
   |
   v
Trace to Route
   |
   v
Identify Request
   |
   v
Burp Proxy
   |
   v
Burp Repeater
   |
   v
Controlled Validation
```

Example:

```text
OpenGrep:

request.args.get("url")
        |
        v
requests.get(url)

Route:

GET /preview?url=

Burp:

GET /preview?url=<controlled-destination>
```

The static analysis identifies where to test.

Burp validates runtime behaviour.

---

# OpenGrep and ripgrep

Use ripgrep for reconnaissance:

```bash
rg -n \
'Runtime\.getRuntime|ProcessBuilder' \
-g '*.java' \
.
```

Then OpenGrep:

```yaml
rules:
  - id: java-command-execution
    languages:
      - java
    message: Review command execution
    severity: WARNING

    pattern-either:
      - pattern: Runtime.getRuntime().exec(...)
      - pattern: new ProcessBuilder(...)
```

This progression works well:

```text
ripgrep
   |
   v
Find Pattern
   |
   v
Understand Pattern
   |
   v
OpenGrep
   |
   v
Structural Variant Search
```

---

# OpenGrep and Semgrep

OpenGrep was forked from Semgrep and aims to maintain compatibility with Semgrep rules.

This makes it possible to reuse many existing rule files.

Conceptually:

```text
rules/
   |
   +--> Semgrep
   |
   +--> OpenGrep
```

But test important rules in both engines if both are part of your workflow.

Reasons include:

```text
Parser differences
Engine evolution
Taint behaviour
CLI differences
Feature divergence
Bug fixes
Language support differences
```

Do not assume permanent one-to-one equivalence.

---

# OpenGrep and CodeQL

Use OpenGrep for:

```text
Fast structural searches
Custom patterns
Taint rules
Intrafile cross-function taint
Variant analysis
Framework-specific patterns
```

Use CodeQL when you need deeper semantic reasoning.

Examples:

```text
Complex cross-file flows
Large call graphs
Type relationships
Repository-wide semantic analysis
Complex interprocedural data flow
```

Workflow:

```text
OpenGrep
   |
   v
Interesting Candidate
   |
   v
Can Flow Be Understood?
   |
   +--> Yes
   |     |
   |     v
   |   Manual Review
   |
   +--> No
         |
         v
       CodeQL
```

---

# OpenGrep and VS Code

Example workflow:

```text
OpenGrep Result

src/controllers/ReportController.java:84

        |
        v

VS Code

        |
        +--> Go to Definition
        |
        +--> Find References
        |
        +--> Call Hierarchy
        |
        v

Trace Backwards

        |
        v

@RequestParam
```

This combination is often more effective than treating SAST output as a standalone report.

---

# Recommended Security Passes

Run focused passes.

```text
Pass 01 - Routes and attack surface
Pass 02 - Authentication
Pass 03 - Authorisation
Pass 04 - Session management
Pass 05 - SQL injection
Pass 06 - NoSQL injection
Pass 07 - LDAP injection
Pass 08 - Command execution
Pass 09 - Dynamic code execution
Pass 10 - SSRF
Pass 11 - Filesystem
Pass 12 - Uploads
Pass 13 - XML
Pass 14 - Deserialisation
Pass 15 - Templates
Pass 16 - XSS
Pass 17 - Redirects
Pass 18 - Prototype pollution
Pass 19 - Mass assignment
Pass 20 - JWT
Pass 21 - OAuth/OIDC
Pass 22 - SAML
Pass 23 - GraphQL
Pass 24 - gRPC
Pass 25 - WebSockets
Pass 26 - Secrets
Pass 27 - Cryptography
Pass 28 - Background jobs
Pass 29 - Business logic variants
Pass 30 - Confirmed-finding variant analysis
```

---

# Java Review Strategy

Prioritise:

```text
Spring routes
Servlets
Request parameters
Spring Security
Method security
SQL/JPA
Process execution
HTTP clients
Filesystem
Uploads
XML
Deserialisation
SpEL
Templates
Redirects
JWT
OAuth/OIDC
SAML
GraphQL
gRPC
WebSockets
Schedulers
Queue consumers
```

Workflow:

```text
Routes
  |
  v
Sources
  |
  v
OpenGrep Sinks
  |
  v
Security Controls
  |
  v
Taint Analysis
```

---

# .NET Review Strategy

Prioritise:

```text
Controllers
Minimal APIs
Model binding
Authentication
Authorisation
Entity Framework
Raw SQL
Process.Start
HttpClient
Filesystem
Uploads
XML
Deserialisation
Razor
JWT
OAuth/OIDC
SignalR
gRPC
BackgroundService
HostedService
```

---

# PHP Review Strategy

Prioritise:

```text
Routes
$_GET
$_POST
$_REQUEST
$_COOKIE
$_FILES
SQL
Command execution
File inclusion
Filesystem
Uploads
unserialize()
Templates
Redirects
SSRF
Sessions
Authentication
Authorisation
```

---

# Python Review Strategy

Prioritise:

```text
Request input
SQL
subprocess
os.system
HTTP clients
Filesystem
pickle
YAML
XML
Templates
eval
exec
Secrets
```

---

# Django Review Strategy

Prioritise:

```text
urls.py
Views
ViewSets
Serializers
Authentication classes
Permission classes
get_queryset()
get_object()
Raw SQL
Mass assignment
Uploads
Redirects
CSRF exemptions
Templates
Settings
Background jobs
```

---

# Flask Review Strategy

Prioritise:

```text
@app.route
Blueprints
request.args
request.form
request.values
request.json
request.files
SQL
subprocess
requests
httpx
render_template_string
send_file
redirect
session
SECRET_KEY
debug
CSRF
Authentication decorators
Authorisation decorators
```

---

# Node.js Review Strategy

Prioritise:

```text
Express routes
req.query
req.params
req.body
req.headers
Authentication middleware
Authorisation middleware
SQL
NoSQL
child_process
HTTP clients
Filesystem
Templates
Prototype pollution
Mass assignment
JWT
CORS
Sessions
GraphQL
WebSockets
Background jobs
```

---

# Client-Side JavaScript Review Strategy

Prioritise:

```text
location
URL parameters
Fragments
postMessage
window.name
Storage
API responses
innerHTML
outerHTML
insertAdjacentHTML
document.write
eval
Function
Navigation
Dynamic scripts
Prototype pollution
Client-side auth assumptions
Tokens
Source maps
Third-party JavaScript
```

---

# Common False Positives

Examples:

```text
Safe parameterisation
Trusted constant
Unreachable code
Test code
Correct sanitisation
Correct validation
Framework protection
Internal-only fixed data
False source
False sink
Correct security configuration
```

---

# Common False Negatives

Examples:

```text
Custom wrappers
Aliased imports
Reflection
Dynamic dispatch
Generated code
Framework magic
Cross-file flows
Second-order flows
Database persistence
Message queues
Background jobs
Custom sanitizers
Unsupported syntax
```

No SAST engine gives complete coverage.

---

# Rule Review Checklist

```text
[ ] Rule ID is descriptive
[ ] Language is correct
[ ] Framework assumptions documented
[ ] Sources are correct
[ ] Sinks are correct
[ ] Sanitizers are justified
[ ] Positive tests exist
[ ] Negative tests exist
[ ] Alternate syntax tested
[ ] Aliased imports considered
[ ] Wrapper functions considered
[ ] False positives reviewed
[ ] False negatives reviewed
[ ] Rule validated
[ ] Rule version controlled
```

---

# Finding Checklist

Before reporting:

```text
[ ] Code is reachable
[ ] Source is attacker-controlled
[ ] Source trust boundary understood
[ ] Data reaches sink
[ ] Transformations reviewed
[ ] Validation reviewed
[ ] Sanitisation reviewed
[ ] Framework protection reviewed
[ ] Authorisation reviewed
[ ] Infrastructure controls considered
[ ] Impact established
[ ] Dynamic validation performed where appropriate
```

---

# Cross-Function Taint Checklist

When using:

```text
--taint-intrafile
```

check:

```text
[ ] Source function identified
[ ] Return flow understood
[ ] Helper functions identified
[ ] Method calls reviewed
[ ] Constructors reviewed
[ ] Collection operations reviewed
[ ] Higher-order functions considered
[ ] Cross-file boundaries identified
[ ] Persistence boundaries identified
[ ] Manual trace performed
```

---

# False-Positive Reduction

Do not reduce false positives by blindly excluding large areas.

Instead:

```text
Broad Rule
   |
   v
Review Matches
   |
   v
Understand False Positive
   |
   v
Refine Structural Context
   |
   v
Add Justified Exclusion
   |
   v
Add Regression Test
```

---

# False-Negative Reduction

After finding one vulnerability:

```text
Confirmed Finding
      |
      v
Search Same Sink
      |
      v
Search Same Source
      |
      v
Search Same Helper
      |
      v
Search Same Framework Pattern
      |
      v
Create OpenGrep Variant Rule
      |
      v
Run --taint-intrafile
      |
      v
Consider CodeQL
```

---

# CI/CD Integration

OpenGrep can be incorporated into CI/CD.

Conceptually:

```text
Commit
   |
   v
CI Pipeline
   |
   v
OpenGrep
   |
   v
Security Rules
   |
   v
JSON / SARIF
   |
   v
Triage
```

Before enforcing build failures:

```text
Rules should be stable
False positives should be controlled
Rule ownership should be clear
Suppression should be reviewed
Baseline strategy should exist
Rules should be versioned
Developers should understand remediation
```

Experimental security rules should normally begin in reporting mode.

---

# Rule Lifecycle

```text
Experimental
     |
     v
Tested
     |
     v
Validated
     |
     v
Pilot
     |
     v
Production
     |
     v
Maintained
     |
     v
Deprecated
```

---

# Rule Documentation

Document:

```text
Rule ID
Purpose
Language
Framework
Vulnerability class
Sources
Sinks
Sanitizers
Known false positives
Known false negatives
Positive tests
Negative tests
Last reviewed
```

Example:

```text
Rule:
flask-request-to-os-system

Purpose:
Identify Flask request values reaching os.system().

Sources:
request.args.get()
request.form.get()
request.values.get()

Sink:
os.system()

Limitations:
Does not model every custom request wrapper.
Cross-file persistence is not automatically modelled.
Shell semantics require manual review.
```

---

# Complete Security Review Workflow

```text
1. Open repository in VS Code

2. Record branch and commit

3. Identify languages

4. Identify frameworks

5. Map application architecture

6. Map trust boundaries

7. Map routes

8. Map authentication

9. Map authorisation

10. Identify sources

11. Identify sinks with ripgrep

12. Run OpenGrep structural rules

13. Run OpenGrep taint rules

14. Run relevant rules with --taint-intrafile

15. Review data-flow traces

16. Trace findings manually in VS Code

17. Review validation

18. Review sanitisation

19. Review framework controls

20. Review infrastructure assumptions

21. Dynamically validate candidates

22. Confirm vulnerabilities

23. Build custom OpenGrep rules

24. Perform variant analysis

25. Test custom rules

26. Consider Semgrep comparison

27. Use CodeQL for complex flows

28. Document evidence

29. Document remediation

30. Retest
```

---

# OpenGrep Security Testing Model

```text
                         REPOSITORY
                             |
                             v
                      VISUAL STUDIO CODE
                             |
                             v
                    UNDERSTAND APPLICATION
                             |
          +------------------+------------------+
          |                                     |
          v                                     v
       ripgrep                               OpenGrep
          |                                     |
          v                                     v
   Text Reconnaissance                 Structural Analysis
          |                                     |
          +------------------+------------------+
                             |
                             v
                       ATTACK SURFACE
                             |
               +-------------+-------------+
               |                           |
               v                           v
            SOURCES                       SINKS
               |                           |
               +-------------+-------------+
                             |
                             v
                       TAINT ANALYSIS
                             |
                             v
                     --taint-intrafile
                             |
                             v
                    CROSS-FUNCTION FLOW
                             |
                             v
                      TRANSFORMATIONS
                             |
              +--------------+--------------+
              |                             |
              v                             v
          VALIDATION                    SANITISATION
              |                             |
              +--------------+--------------+
                             |
                             v
                    SECURITY CONTROLS
                             |
                             v
                     MANUAL VALIDATION
                             |
                  +----------+----------+
                  |                     |
                  v                     v
            False Positive          Candidate
                                         |
                                         v
                                Dynamic Validation
                                         |
                                         v
                                 Confirmed Finding
                                         |
                                         v
                                   Root Pattern
                                         |
                                         v
                                 Variant Analysis
                                         |
                       +-----------------+-----------------+
                       |                 |                 |
                       v                 v                 v
                    OpenGrep          Semgrep            CodeQL
```

---

# Final Source-to-Sink Model

For every OpenGrep result:

```text
SOURCE
  |
  v
Can an attacker control it?
  |
  v
PROPAGATION
  |
  +--> assignments
  +--> functions
  +--> methods
  +--> constructors
  +--> collections
  +--> callbacks
  |
  v
TRANSFORMATIONS
  |
  +--> parsing
  +--> decoding
  +--> normalisation
  +--> validation
  +--> sanitisation
  +--> business logic
  |
  v
SINK
  |
  v
Is the operation security-sensitive?
  |
  v
SECURITY CONTROLS
  |
  v
Are the controls effective?
  |
  v
IMPACT
```

A meaningful finding requires:

```text
Source identified
      +
Attacker control established
      +
Reachable flow established
      +
Sink identified
      +
Security controls absent or ineffective
      +
Security impact established
```

Not:

```text
OpenGrep matched something
```

---

# Quick Reference

## Version

```bash
opengrep --version
```

## Help

```bash
opengrep --help
```

## Structural Search

```bash
opengrep scan \
  -e 'os.system(...)' \
  -l python \
  .
```

## Scan Rule

```bash
opengrep scan \
  -f rule.yml \
  .
```

## Taint Scan

```bash
opengrep scan \
  -f taint-rule.yml \
  .
```

## Intrafile Cross-Function Taint

```bash
opengrep scan \
  -f taint-rule.yml \
  . \
  --taint-intrafile
```

## Data-Flow Traces

```bash
opengrep scan \
  --dataflow-traces \
  -f taint-rule.yml \
  .
```

## Validate Rule

```bash
opengrep validate rule.yml
```

## Test Rule

```bash
opengrep test \
  --config rule.yml \
  test_rule.py
```

## JSON Output

```bash
opengrep scan \
  -f rules/ \
  --json \
  -o opengrep.json \
  .
```

## SARIF Output

```bash
opengrep scan \
  -f rules/ \
  --sarif \
  -o opengrep.sarif \
  .
```

---

# Recommended Tool Chain

```text
Visual Studio Code
        |
        v
     ripgrep
        |
        v
     OpenGrep
        |
        +--> Structural Rules
        |
        +--> Taint Rules
        |
        +--> --taint-intrafile
        |
        v
   Manual Review
        |
        v
      CodeQL
   when required
        |
        v
   Burp Suite
        |
        v
Dynamic Validation
        |
        v
Confirmed Finding
        |
        v
OpenGrep Variant Rule
        |
        v
Repository-Wide Search
```

---

# References

## OpenGrep

[OpenGrep](https://opengrep.dev/)

## OpenGrep GitHub Repository

[OpenGrep GitHub Repository](https://github.com/opengrep/opengrep)

## OpenGrep README

[OpenGrep README](https://github.com/opengrep/opengrep/blob/main/README.md)

## OpenGrep Changes Since the Fork

[OpenGrep Changes Since the Fork](https://github.com/opengrep/opengrep/blob/main/OPENGREP.md)

## OpenGrep Wiki

[OpenGrep Wiki](https://github.com/opengrep/opengrep/wiki)

## OpenGrep Intrafile Taint Analysis

[OpenGrep Intrafile Taint Analysis](https://github.com/opengrep/opengrep/wiki/Intrafile-tainting-tutorial)

## OpenGrep Higher-Order Function Taint Analysis

[OpenGrep Higher-Order Function Taint Analysis](https://github.com/opengrep/opengrep/wiki/Higher-order-functions-tutorial)

## Semgrep

[Semgrep](https://semgrep.dev/)

## Semgrep Rule Syntax

[Semgrep Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax)

## CodeQL

[CodeQL](https://codeql.github.com/docs/)

## OWASP Secure Code Review Cheat Sheet

[OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html)

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

## OWASP Static Code Analysis

[OWASP Static Code Analysis](https://owasp.org/www-community/controls/Static_Code_Analysis)

## Visual Studio Code

[Visual Studio Code](https://code.visualstudio.com/docs)

---

# Related Static Analysis Notes

```text
docs/source-code-review/static-analysis/index.md
docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/semgrep.md
docs/source-code-review/static-analysis/codeql.md
```

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/methodology.md

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

docs/web/authentication.md
docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/mfa.md
docs/web/saml.md

docs/web/input-validation.md

docs/web/sql-injection.md
docs/web/nosql-injection.md
docs/web/ldap-injection.md
docs/web/command-injection.md
docs/web/ssti.md

docs/web/ssrf.md
docs/web/path-traversal.md
docs/web/file-inclusion.md
docs/web/file-upload.md
docs/web/xxe.md
docs/web/deserialization.md

docs/web/xss.md
docs/web/dom-based-vulnerabilities.md
docs/web/html-injection.md
docs/web/csrf.md
docs/web/cors.md
docs/web/open-redirect.md
docs/web/xs-leaks.md

docs/web/host-header-attacks.md
docs/web/http-security-headers.md
docs/web/http-request-smuggling.md
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
docs/web/information-disclosure.md

docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/rate-limiting.md
docs/web/mass-assignment.md

docs/web/jwt.md
docs/web/oauth-oidc.md

docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md
docs/web/prototype-pollution.md
```
