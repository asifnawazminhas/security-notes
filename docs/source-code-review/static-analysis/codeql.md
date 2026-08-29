# CodeQL for Security Source Code Review

CodeQL is a semantic static analysis engine that allows source code to be queried as data.

Instead of searching only for text or syntax patterns, CodeQL creates a database representing the source code and allows security researchers to query:

```text
Functions
Methods
Classes
Calls
Expressions
Types
Inheritance
Control flow
Data flow
Taint flow
Sources
Sinks
Security controls
Relationships between program elements
```

For security source code review, CodeQL is particularly useful when:

```text
Simple grep searches are no longer sufficient
Source-to-sink flows cross functions
Framework abstractions hide important behaviour
You need semantic rather than textual matching
You need global data-flow analysis
You want path explanations
You want repository-wide variant analysis
You want reusable custom security queries
```

A practical workflow is:

```text
Repository
    |
    v
ripgrep
    |
    v
Fast Reconnaissance
    |
    v
OpenGrep / Semgrep
    |
    v
Pattern and Taint Analysis
    |
    v
CodeQL
    |
    +--> Semantic Analysis
    +--> Data Flow
    +--> Taint Tracking
    +--> Path Queries
    +--> Variant Analysis
    |
    v
Visual Studio Code
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
    Use CodeQL only against source code and repositories that you are authorised to assess. A CodeQL result is a security-review candidate. It does not automatically prove that a vulnerability is reachable or exploitable.

---

# Core Principle

The most important rule is:

```text
CodeQL result
      !=
Confirmed vulnerability
```

CodeQL can identify:

```text
Interesting code structures
Potentially dangerous APIs
Security-sensitive calls
Possible data flows
Possible taint flows
Missing expected patterns
Source-to-sink paths
Variants of known vulnerable patterns
```

The security reviewer still needs to determine:

```text
Is the code reachable?

Can an attacker influence the source?

Can the source reach the sink?

What transformations occur?

Is validation present?

Is sanitisation appropriate?

Does authentication apply?

Does authorisation apply?

Does the framework provide protection?

Does infrastructure provide protection?

Is the path feasible at runtime?

What security impact exists?
```

Use:

```text
CodeQL Result
      |
      v
Candidate
      |
      v
Manual Data-Flow Review
      |
      v
Security-Control Review
      |
      v
Runtime Validation
      |
      v
Confirmed / Rejected
```

---

# Why CodeQL Is Different

Consider:

```java
String host =
    request.getParameter("host");

String command =
    buildCommand(host);

executeDiagnostic(command);
```

The dangerous operation may exist somewhere else:

```java
void executeDiagnostic(
    String command
) throws IOException {

    Runtime
        .getRuntime()
        .exec(command);
}
```

A text search can find:

```text
Runtime.getRuntime().exec
```

but does not inherently understand:

```text
request.getParameter()
        |
        v
host
        |
        v
buildCommand()
        |
        v
command
        |
        v
executeDiagnostic()
        |
        v
Runtime.exec()
```

CodeQL is designed to reason about relationships in the program.

---

# CodeQL Mental Model

CodeQL transforms source code into a queryable database.

```text
SOURCE CODE
     |
     v
CodeQL Extractor
     |
     v
CodeQL Database
     |
     +--> AST
     +--> Types
     +--> Calls
     +--> Control Flow
     +--> Data Flow
     +--> Program Relationships
     |
     v
QL Queries
     |
     v
Results
```

You query the database using the QL query language.

---

# CodeQL vs ripgrep vs OpenGrep vs Semgrep

These tools should complement each other.

| Tool | Best Use |
|---|---|
| ripgrep | Extremely fast text and regex reconnaissance |
| OpenGrep | Structural matching, custom rules and taint analysis |
| Semgrep | Structural matching, custom rules and taint analysis |
| CodeQL | Semantic queries, global data flow and deeper variant analysis |
| VS Code | Manual reasoning and navigation |
| Burp Suite | Runtime validation |

A practical model:

```text
Repository
    |
    +--------------------+
    |                    |
    v                    v
ripgrep             OpenGrep/Semgrep
    |                    |
    +---------+----------+
              |
              v
       Candidate Areas
              |
              v
            CodeQL
              |
              v
      Semantic Analysis
              |
              v
         VS Code
              |
              v
       Manual Review
              |
              v
       Burp Validation
```

Do not think:

```text
CodeQL replaces ripgrep
```

or:

```text
CodeQL replaces manual review
```

Instead:

```text
ripgrep
    =
fast discovery

OpenGrep / Semgrep
    =
syntax-aware rules

CodeQL
    =
semantic and data-flow reasoning

VS Code
    =
human understanding

Burp
    =
runtime validation
```

---

# Supported Languages

Current CodeQL language identifiers include:

| Language | CodeQL Identifier |
|---|---|
| C / C++ | `c-cpp` |
| C# | `csharp` |
| Go | `go` |
| Java / Kotlin | `java-kotlin` |
| JavaScript / TypeScript | `javascript-typescript` |
| Python | `python` |
| Ruby | `ruby` |
| Rust | `rust` |
| Swift | `swift` |

Alternative identifiers may also be accepted for some languages.

Examples:

```text
c
cpp
java
kotlin
javascript
typescript
```

---

# Important PHP Limitation

PHP is not currently one of the CodeQL languages listed by GitHub for database creation.

Therefore, for PHP source code review use tools such as:

```text
ripgrep
OpenGrep
Semgrep
PHP-specific static analysis
Manual review
```

Do not write:

```bash
codeql database create php-db \
  --language=php
```

and expect official PHP CodeQL support.

For this notes repository:

```text
.NET
    -> CodeQL supported

Java
    -> CodeQL supported

Python
    -> CodeQL supported

Django
    -> Python CodeQL

Flask
    -> Python CodeQL

Node.js
    -> JavaScript/TypeScript CodeQL

Client JavaScript
    -> JavaScript/TypeScript CodeQL

PHP
    -> use ripgrep/OpenGrep/Semgrep instead
```

---

# CodeQL Components

A practical CodeQL environment consists of:

```text
CodeQL CLI
    |
    +--> Database creation
    +--> Database analysis
    +--> Query execution
    +--> Pack management
    +--> SARIF output

CodeQL Queries
    |
    +--> Built-in queries
    +--> Custom queries
    +--> Query suites

CodeQL for VS Code
    |
    +--> Query development
    +--> Database selection
    +--> Query execution
    +--> Result inspection
    +--> Path visualization
    +--> Model editing
    +--> Variant analysis
```

---

# CodeQL CLI

The CodeQL CLI is used to:

```text
Create databases
Analyze databases
Run queries
Compile queries
Manage query packs
Generate SARIF
Inspect available languages
```

Verify installation:

```bash
codeql version
```

Display help:

```bash
codeql --help
```

---

# Check Available Languages

Use:

```bash
codeql resolve languages
```

This shows the language extractors available to your CodeQL installation.

This is useful because the exact available extractors depend on the installed CodeQL bundle.

---

# Check Available Packs

Use:

```bash
codeql resolve packs
```

This helps verify that CodeQL can locate:

```text
Language libraries
Query packs
Standard queries
Custom packs
```

---

# CodeQL Database

CodeQL does not normally run directly against arbitrary source files.

First create a database.

```text
Repository
    |
    v
Extractor
    |
    v
CodeQL Database
    |
    v
Queries
```

A database contains a representation of one programming language.

---

# Create a Python Database

From the repository root:

```bash
codeql database create codeql-db-python \
  --language=python
```

---

# Create a JavaScript / TypeScript Database

```bash
codeql database create codeql-db-js \
  --language=javascript-typescript
```

This covers both JavaScript and TypeScript.

---

# Create a C# Database

A basic example:

```bash
codeql database create codeql-db-csharp \
  --language=csharp
```

For compiled languages, database creation may involve:

```text
No-build extraction
Autobuild
Manual build
```

depending on the language and chosen build mode.

---

# Create a Java Database

```bash
codeql database create codeql-db-java \
  --language=java-kotlin
```

For Java-only projects, no-build analysis may be available.

For Kotlin, build requirements differ.

---

# Build Modes

CodeQL supports different database build approaches depending on language.

Conceptually:

```text
none
    |
    +--> analyze without normal application build

autobuild
    |
    +--> CodeQL attempts to determine build process

manual
    |
    +--> you provide the build command
```

---

# No-Build Mode

For supported languages:

```bash
codeql database create codeql-db \
  --language=csharp \
  --build-mode=none
```

No-build mode can simplify analysis where CodeQL supports it.

However, database quality can depend on:

```text
Dependencies
Generated source
Framework information
Build configuration
Language
Project structure
```

Do not automatically assume:

```text
No-build database
      =
identical semantic information to successful real build
```

---

# Autobuild

Example:

```bash
codeql database create codeql-db \
  --language=csharp \
  --build-mode=autobuild
```

CodeQL attempts to determine the appropriate build process.

This works well for many conventional projects.

---

# Manual Build

For a custom build:

```bash
codeql database create codeql-db \
  --language=csharp \
  --command="dotnet build"
```

For Java Maven:

```bash
codeql database create codeql-db \
  --language=java-kotlin \
  --command="mvn clean package -DskipTests"
```

For Gradle:

```bash
codeql database create codeql-db \
  --language=java-kotlin \
  --command="./gradlew build -x test"
```

Use the application's real build process where practical.

---

# Interpreted Languages

Python and JavaScript/TypeScript do not normally require you to supply an application build command to CodeQL database creation.

For Python:

```bash
codeql database create codeql-db \
  --language=python
```

For JavaScript/TypeScript:

```bash
codeql database create codeql-db \
  --language=javascript-typescript
```

Do not add a build command merely because the project itself has one unless CodeQL's extraction workflow specifically requires it.

---

# Multi-Language Repositories

A repository may contain:

```text
C#
JavaScript
Python
```

CodeQL databases are language-specific.

You can create a database cluster:

```bash
codeql database create codeql-dbs \
  --db-cluster \
  --language=csharp,javascript-typescript,python
```

Conceptually:

```text
Repository
    |
    +--> C# Database
    |
    +--> JavaScript Database
    |
    +--> Python Database
```

---

# Source Root

If running outside the repository root:

```bash
codeql database create codeql-db \
  --language=python \
  --source-root=/path/to/project
```

---

# Verify Database

Once created:

```bash
codeql database info codeql-db
```

Use this to inspect database information.

---

# Database Creation Problems

Common causes include:

```text
Dependencies unavailable
Build failure
Wrong language
Wrong source root
Unsupported language
Generated code missing
Private dependency feeds unavailable
Wrong JDK
Wrong .NET SDK
Wrong Node.js version
Custom build tooling
Monorepo layout
```

A badly extracted database can produce misleadingly low coverage.

---

# Query Suites

CodeQL ships with built-in query suites.

The two main current suites are:

```text
default
security-extended
```

---

# Default Suite

The default suite prioritises high-precision results.

Conceptually:

```text
default
    |
    +--> higher precision
    +--> fewer findings
    +--> lower expected false-positive rate
```

This is a good initial scan.

---

# Security-Extended Suite

The `security-extended` suite includes:

```text
default queries
        +
additional security queries
```

Conceptually:

```text
security-extended
        |
        +--> broader security coverage
        +--> more findings
        +--> potentially more false positives
```

For manual penetration-testing source review, this broader coverage can be useful because the reviewer will manually triage candidates.

---

# Important Suite Note

Older examples may mention other suite names.

Always verify current suite availability.

For current GitHub CodeQL code scanning, the primary built-in suites documented by GitHub are:

```text
default
security-extended
```

---

# Analyze a Database

General form:

```bash
codeql database analyze \
  <database> \
  <queries-or-suite> \
  --format=sarif-latest \
  --output=results.sarif
```

---

# Example - JavaScript

```bash
codeql database analyze \
  codeql-db-js \
  codeql/javascript-queries \
  --format=sarif-latest \
  --output=javascript-results.sarif
```

---

# Example - Python

```bash
codeql database analyze \
  codeql-db-python \
  codeql/python-queries \
  --format=sarif-latest \
  --output=python-results.sarif
```

---

# Example - Java

```bash
codeql database analyze \
  codeql-db-java \
  codeql/java-queries \
  --format=sarif-latest \
  --output=java-results.sarif
```

---

# Example - C#

```bash
codeql database analyze \
  codeql-db-csharp \
  codeql/csharp-queries \
  --format=sarif-latest \
  --output=csharp-results.sarif
```

---

# SARIF

SARIF is a standard format for static-analysis results.

```text
CodeQL
   |
   v
SARIF
   |
   +--> CI
   +--> GitHub Code Scanning
   +--> Analysis tooling
   +--> Result processing
```

Example:

```bash
--format=sarif-latest
```

and:

```bash
--output=results.sarif
```

---

# Visual Studio Code

Visual Studio Code is particularly useful for CodeQL development.

Install the official:

```text
CodeQL
```

extension.

The extension supports:

```text
Writing QL queries
Running queries
Selecting databases
Viewing query results
Viewing path explanations
Managing query packs
Testing queries
Working with model packs
Variant analysis
```

---

# Recommended VS Code Layout

A useful layout:

```text
+----------------------------------------------+
| Explorer                                     |
|                                              |
| src/                                         |
| queries/                                     |
| codeql-pack.yml                              |
+----------------------+-----------------------+
| Application Source   | CodeQL Query          |
|                      |                       |
| Controller.java      | command.ql            |
| Service.java         |                       |
|                      |                       |
+----------------------+-----------------------+
| CodeQL Results / Terminal                    |
+----------------------------------------------+
```

---

# VS Code Workflow

```text
1. Open repository

2. Add CodeQL database

3. Open custom query

4. Run query

5. Inspect result

6. Open source location

7. View data-flow path

8. Use Go to Definition

9. Use Find All References

10. Use Call Hierarchy

11. Trace security controls

12. Validate candidate dynamically
```

---

# CodeQL Query Language

CodeQL queries use QL.

A simple query generally has:

```text
import
from
where
select
```

Conceptually:

```ql
import <language>

from <variables>
where <conditions>
select <results>
```

---

# Simple JavaScript Query

Example:

```ql
import javascript

from CallExpr call
where
  call.getCalleeName() = "eval"
select call, "Review dynamic JavaScript execution."
```

This demonstrates the general idea:

```text
Find call expressions
        |
        v
Filter to eval()
        |
        v
Return matching locations
```

A real security query may need additional semantic checks.

---

# Simple Python Query

```ql
import python

from Call call
where
  call.getFunc().toString() = "eval"
select call, "Review dynamic Python evaluation."
```

Treat simple examples as learning queries.

Production security queries normally require stronger modelling.

---

# QL Classes

CodeQL exposes classes representing program elements.

Examples conceptually include:

```text
Function
Method
Class
Call
Expression
Parameter
Variable
Type
Statement
File
```

The exact classes depend on the language library.

---

# Predicates

Predicates express relationships.

Conceptually:

```ql
predicate isInteresting(Call call) {
    ...
}
```

Then:

```ql
from Call call
where isInteresting(call)
select call
```

Predicates allow complex analysis to be decomposed into reusable logic.

---

# AST Analysis

CodeQL can query the abstract syntax representation.

This is useful for questions such as:

```text
Where is this function called?

What argument is passed?

What type is this expression?

What method does this invocation resolve to?

What class contains this method?

What annotation is attached?
```

---

# Control Flow

Control-flow analysis reasons about execution paths.

Example:

```text
Input
  |
  v
if authenticated
  |
  +--> true --> sensitive operation
  |
  +--> false --> reject
```

Security review may use control flow to understand whether:

```text
Validation executes before sink
Authorisation executes before action
Error path bypasses checks
Dangerous code is reachable
```

---

# Data Flow

Data-flow analysis determines how values propagate.

Example:

```java
String value =
    request.getParameter("name");

String copy =
    value;

process(copy);
```

Data flow:

```text
request parameter
      |
      v
value
      |
      v
copy
      |
      v
process()
```

---

# Data-Flow Graph

CodeQL data flow is based on a data-flow graph.

Conceptually:

```text
AST
    =
program syntax

Data-Flow Graph
    =
how values move through the program
```

Not every AST element is a data-flow node.

---

# Local Data Flow

Local data flow operates within a single function or callable.

Example:

```python
def example(request):
    value = request.args.get("cmd")
    copy = value
    os.system(copy)
```

Flow:

```text
request.args
     |
     v
value
     |
     v
copy
     |
     v
os.system
```

Local data flow is generally:

```text
Faster
More precise
Less computationally expensive
```

than global data flow.

---

# Global Data Flow

Global data flow can track relationships across functions and broader program structure.

Example:

```python
def get_input(request):
    return request.args.get("cmd")

def execute(value):
    os.system(value)

def handler(request):
    value = get_input(request)
    execute(value)
```

Conceptually:

```text
request.args
     |
     v
get_input()
     |
     v
handler()
     |
     v
execute()
     |
     v
os.system()
```

---

# Important Global Data-Flow Limitation

Global analysis is more powerful than local analysis.

However:

```text
More powerful
     !=
Perfect
```

Global data flow is generally:

```text
More computationally expensive
Less precise
Potentially capable of producing spurious flows
Dependent on library/framework models
```

Therefore:

```text
CodeQL global flow
       !=
guaranteed runtime flow
```

Manual validation remains necessary.

---

# Data Flow vs Taint Tracking

CodeQL distinguishes normal data flow from taint tracking.

Normal data flow focuses on value-preserving flow.

Taint tracking also models transformations where the exact value changes but attacker influence remains.

Example:

```javascript
let input =
    req.query.name;

let value =
    "hello-" + input;

sink(value);
```

The value changed.

But:

```text
input
   |
   v
String Concatenation
   |
   v
value
```

is still attacker-influenced.

That is where taint tracking is useful.

---

# Security Source-to-Sink Model

Most security data-flow queries can be understood as:

```text
SOURCE
   |
   v
PROPAGATION
   |
   v
TRANSFORMATION
   |
   v
SINK
```

Examples:

```text
HTTP parameter
      |
      v
String operations
      |
      v
Runtime.exec()
```

or:

```text
HTTP parameter
      |
      v
URL builder
      |
      v
HTTP client
```

or:

```text
HTTP parameter
      |
      v
Path construction
      |
      v
File read
```

---

# Sources

Typical sources include:

```text
HTTP query parameters
Route parameters
Request body
Headers
Cookies
Uploaded files
WebSocket messages
GraphQL arguments
gRPC request fields
Queue messages
Environment-dependent external input
Stored attacker-controlled database values
```

---

# Sinks

Typical sinks include:

```text
SQL execution
OS command execution
HTTP requests
Filesystem operations
Template evaluation
HTML rendering
Dynamic code execution
LDAP queries
XML parsing
Deserialisation
Redirects
Sensitive logging
```

---

# Sanitizers

A sanitizer prevents a dangerous flow for a particular context.

Examples:

```text
SQL parameterisation
Path containment
URL allowlisting
HTML encoding
Shell-safe argument construction
Strict type validation
```

But:

```text
sanitizer
    !=
universal security
```

For example:

```text
HTML encoding
    !=
SQL injection protection
```

and:

```text
SQL parameterisation
    !=
command injection protection
```

---

# Path Queries

Path queries are especially useful for security research.

Instead of returning only:

```text
Potential sink here
```

they can return:

```text
Source
  |
  v
Step
  |
  v
Step
  |
  v
Step
  |
  v
Sink
```

This makes source-to-sink analysis significantly easier.

---

# Path Query Metadata

A path query uses:

```text
@kind path-problem
```

Conceptually:

```ql
/**
 * @kind path-problem
 */
```

The query then defines:

```text
Source
Sink
Flow configuration
Path graph
```

---

# Modern Data-Flow API

Current CodeQL uses the modular data-flow API.

A conceptual path-query structure is:

```ql
/**
 * @kind path-problem
 */

import <language>

module MyConfig implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node source) {
    ...
  }

  predicate isSink(DataFlow::Node sink) {
    ...
  }
}

module MyFlow =
  TaintTracking::Global<MyConfig>;

import MyFlow::PathGraph

from
  MyFlow::PathNode source,
  MyFlow::PathNode sink

where
  MyFlow::flowPath(source, sink)

select
  sink.getNode(),
  source,
  sink,
  "Potential attacker-controlled flow."
```

The exact imports and classes differ between language libraries.

Always use the current language-specific documentation when building real queries.

---

# DataFlow::Global

For value-preserving global data flow:

```text
DataFlow::Global<...>
```

is used.

Conceptually:

```ql
module MyFlow =
    DataFlow::Global<MyConfig>;
```

---

# TaintTracking::Global

For taint propagation:

```text
TaintTracking::Global<...>
```

can be used.

Conceptually:

```ql
module MyFlow =
    TaintTracking::Global<MyConfig>;
```

This includes additional propagation steps appropriate for taint analysis.

---

# isSource

A data-flow configuration defines where interesting flow begins.

Conceptually:

```ql
predicate isSource(
    DataFlow::Node source
) {
    ...
}
```

Examples:

```text
HTTP request parameter
Request body
Header
Cookie
GraphQL argument
```

---

# isSink

The configuration also defines security-sensitive destinations.

Conceptually:

```ql
predicate isSink(
    DataFlow::Node sink
) {
    ...
}
```

Examples:

```text
Runtime.exec()
Process.Start()
os.system()
child_process.exec()
requests.get()
File.ReadAllText()
```

---

# Additional Flow Steps

Applications often use wrappers.

Example:

```text
Input
  |
  v
Custom Sanitizer
  |
  v
DTO
  |
  v
Helper
  |
  v
Sink
```

If CodeQL does not understand a project-specific propagation step, a custom model or additional flow step may be required.

Conceptually:

```ql
predicate isAdditionalFlowStep(
    DataFlow::Node pred,
    DataFlow::Node succ
) {
    ...
}
```

Use additional flow steps carefully.

Overly broad modelling can create many false positives.

---

# Framework Models

CodeQL libraries include modelling for many common frameworks and libraries.

This is important because source code for framework internals may not exist in the repository.

Examples include modelling of:

```text
HTTP frameworks
Standard libraries
String transformations
Filesystem APIs
HTTP clients
Promises
Collections
Framework request objects
```

However:

```text
Framework model exists
      !=
Every application abstraction is modeled
```

Custom frameworks and wrappers may need additional modelling.

---

# Model Packs

CodeQL model packs can extend analysis without directly modifying standard query libraries.

They can help model:

```text
Custom sources
Custom sinks
Custom sanitizers
Custom summaries
Application frameworks
Third-party libraries
```

This is useful for large applications with internal security abstractions.

---

# Model Editor

The CodeQL VS Code extension provides tooling for model packs.

A useful workflow:

```text
Unknown Application API
        |
        v
Understand Behaviour
        |
        v
Model API
        |
        v
Re-run Data Flow
        |
        v
Find Additional Paths
```

---

# Command Injection Analysis

Consider:

```java
@GetMapping("/ping")
public String ping(
    @RequestParam String host
) throws Exception {

    Runtime
        .getRuntime()
        .exec(
            "ping " + host
        );

    return "done";
}
```

Desired analysis:

```text
@RequestParam
      |
      v
host
      |
      v
String concatenation
      |
      v
Runtime.exec()
```

A CodeQL query can model:

```text
HTTP input
      =
source

Runtime.exec argument
      =
sink
```

Then use taint tracking to search for flows.

---

# Command Injection Variant Analysis

Suppose one vulnerability is found:

```text
Request
   |
   v
executeDiagnostic()
   |
   v
Runtime.exec()
```

Instead of searching only for `Runtime.exec`, identify the application's wrapper:

```text
executeDiagnostic()
```

Then query:

```text
Where is executeDiagnostic called?

What reaches its argument?

Which calls originate from HTTP input?
```

This can reveal variants missed by generic rules.

---

# SQL Injection Analysis

A useful SQL injection model is:

```text
HTTP Input
    |
    v
Query Construction
    |
    v
Raw SQL Execution
```

The key distinction is between:

```text
SQL code
```

and:

```text
SQL parameters
```

A sink alone is not enough.

Example:

```java
PreparedStatement statement =
    connection.prepareStatement(
        "SELECT * FROM users WHERE id = ?"
    );

statement.setString(
    1,
    userId
);
```

This is fundamentally different from:

```java
Statement statement =
    connection.createStatement();

statement.executeQuery(
    "SELECT * FROM users WHERE id = '" +
    userId +
    "'"
);
```

CodeQL data-flow analysis can help distinguish where attacker-influenced values reach SQL query construction.

---

# NoSQL Injection

For Node.js applications, model:

```text
req.query
req.params
req.body
      |
      v
Mongo Query Object
      |
      v
find()
findOne()
aggregate()
```

The dangerous behaviour may involve:

```text
Operator injection
Object injection
$where
Regex abuse
Query structure manipulation
```

CodeQL queries can be useful where the database library is semantically modeled.

---

# LDAP Injection

Model:

```text
HTTP Input
    |
    v
LDAP Filter Construction
    |
    v
LDAP Search
```

Potential sinks include framework-specific LDAP query APIs.

Custom enterprise LDAP wrappers may require project-specific modelling.

---

# SSRF Analysis

SSRF is a strong CodeQL use case.

Model:

```text
HTTP Input
    |
    v
URL Construction
    |
    v
HTTP Client
```

Potential sinks include:

```text
Java HttpClient
RestTemplate
WebClient
.NET HttpClient
Python requests
Python httpx
Node fetch
axios
```

Then manually review:

```text
Scheme restrictions
Host allowlisting
Port restrictions
Redirect handling
DNS resolution
Private network blocking
Loopback blocking
Link-local blocking
Cloud metadata protection
```

---

# Path Traversal Analysis

Model:

```text
HTTP Input
    |
    v
Path Construction
    |
    v
Filesystem Sink
```

Potential sinks include:

```text
File reads
File writes
File deletion
Directory access
Archive extraction
File streaming
```

Review transformations such as:

```text
Path.Combine
Paths.get
Path.resolve
resolve()
normalize()
realpath()
canonical paths
```

A normalisation function does not automatically guarantee containment.

---

# File Upload Analysis

Trace:

```text
Uploaded File
     |
     +--> Filename
     +--> MIME Type
     +--> Extension
     +--> Content
     |
     v
Validation
     |
     v
Storage Path
     |
     v
Later Processing
```

CodeQL can help find flows from uploaded filenames or content into:

```text
Filesystem paths
Archive extraction
Image processors
Document processors
Template engines
Command execution
```

---

# Deserialisation

Model:

```text
Untrusted Data
     |
     v
Deserializer
```

Potential APIs depend on language.

Examples:

```text
Java ObjectInputStream
Python pickle
.NET serializers
YAML loaders
```

A deserializer call is not automatically vulnerable.

Determine whether attacker-controlled serialized content can reach it.

---

# XXE

Model:

```text
Attacker XML
     |
     v
XML Parser
     |
     v
External Entity Resolution?
```

The important questions are:

```text
Which parser?
Which configuration?
DTD enabled?
External entities enabled?
External resources accessible?
```

Static analysis is particularly useful for finding parser configuration.

---

# SSTI

Model:

```text
Attacker Input
     |
     v
Template Source
     |
     v
Template Evaluation
```

Do not confuse:

```text
attacker-controlled template data
```

with:

```text
attacker-controlled template source
```

The latter is normally the more dangerous condition.

---

# XSS

Server-side XSS:

```text
HTTP Input
     |
     v
Application
     |
     v
HTML Output
```

Client-side DOM XSS:

```text
location.search
     |
     v
JavaScript
     |
     v
innerHTML
```

CodeQL includes security queries for JavaScript and TypeScript and can model many client-side flows.

---

# DOM XSS

Potential sources:

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
```

Potential sinks:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
eval
Function
script.src
iframe.srcdoc
```

The important question is:

```text
Can attacker-controlled browser data reach the sink without effective context-specific protection?
```

---

# Open Redirect

Model:

```text
Attacker URL
     |
     v
Navigation Sink
```

Potential sinks:

```text
redirect()
location.href
location.assign()
location.replace()
window.open()
```

Review validation carefully.

Substring checks are often insufficient.

---

# Authentication Review

CodeQL can help locate:

```text
Login endpoints
Authentication middleware
Authentication annotations
Password verification
Session creation
JWT verification
OAuth callbacks
SAML processing
MFA logic
```

But authentication correctness often requires architecture-level reasoning.

---

# Authorisation Review

Authorisation is especially important because it is often application-specific.

Model:

```text
Request
   |
   v
Authentication
   |
   v
Object Identifier
   |
   v
Object Lookup
   |
   v
Authorisation
   |
   v
Sensitive Action
```

CodeQL can help answer:

```text
Where is this object retrieved?

Which functions call this repository method?

Which callers perform permission checks?

Which sensitive operations lack the expected security wrapper?
```

---

# IDOR / BOLA

Model:

```text
Attacker-Controlled ID
        |
        v
Object Retrieval
        |
        v
Ownership / Permission Check?
        |
        v
Sensitive Object
```

A powerful strategy is to identify the application's standard authorisation helper.

Example:

```text
checkOwnership()
```

Then query sensitive object access paths and compare whether the helper is used consistently.

---

# Variant Analysis for Authorisation

Suppose:

```text
UserController.delete()
```

correctly calls:

```text
authorizationService.canDeleteUser()
```

but another endpoint:

```text
AdminApi.deleteUser()
```

does not.

Variant analysis can search for:

```text
All calls to userRepository.delete()
```

and inspect whether each path contains the expected authorisation control.

---

# Mass Assignment

Model:

```text
Request Body
     |
     v
Object Binder
     |
     v
Sensitive Domain Object
```

Review fields such as:

```text
role
isAdmin
permissions
ownerId
tenantId
status
balance
verified
```

CodeQL can help locate direct request-to-model flows where the framework is modeled.

---

# JWT

Review:

```text
JWT decode
JWT verify
Algorithm handling
Key selection
Issuer
Audience
Expiration
Not-before
Claims
Authorisation
```

Important:

```text
Valid JWT
    !=
Authorised operation
```

Authentication and authorisation must be reviewed separately.

---

# OAuth / OIDC

Trace:

```text
Authorization Request
       |
       v
Callback
       |
       v
State Validation
       |
       v
Code Exchange
       |
       v
Token Validation
       |
       v
Identity Mapping
       |
       v
Session
```

Review:

```text
state
nonce
PKCE
redirect URI
issuer
audience
token validation
identity mapping
account linking
```

---

# SAML

Trace:

```text
SAMLResponse
      |
      v
XML Parsing
      |
      v
Signature Validation
      |
      v
Assertion Validation
      |
      v
Identity Mapping
      |
      v
Session
```

Review:

```text
Signature
Audience
Recipient
Destination
InResponseTo
Replay
Identity mapping
Authorisation
```

---

# Password Reset

Search for:

```text
reset token creation
reset token validation
password update
email generation
absolute URL generation
session invalidation
```

CodeQL can be especially useful when tracing:

```text
Host Header
     |
     v
Reset URL Generation
     |
     v
Email
```

---

# MFA

Review:

```text
OTP verification
TOTP verification
Recovery codes
MFA state
Session state
Step-up authentication
```

Trace whether sensitive endpoints require the correct authentication state.

---

# CORS

CodeQL can help identify:

```text
CORS configuration
Origin reflection
Wildcard configuration
Credentials configuration
Framework middleware
```

But runtime behaviour must be validated.

---

# CSRF

Look for:

```text
CSRF middleware
CSRF exemptions
State-changing routes
Cookie authentication
SameSite configuration
```

A missing source-code control does not prove missing infrastructure or framework protection.

---

# Host Header Attacks

Trace:

```text
Host
X-Forwarded-Host
Forwarded
      |
      v
URL Generation
      |
      v
Security-Sensitive Output
```

Examples:

```text
Password reset links
OAuth redirect URLs
Invitation links
Email links
Canonical URLs
```

---

# Prototype Pollution

For JavaScript/TypeScript review, inspect flows involving:

```text
Object.assign
Deep merge functions
Recursive setters
Dynamic property writes
__proto__
constructor
prototype
```

CodeQL can be useful because dangerous behaviour often involves relationships rather than one exact text pattern.

---

# GraphQL

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

Review:

```text
Object-level authorisation
Field-level authorisation
Mutations
Batching
Subscriptions
Input validation
Resource limits
```

---

# gRPC

Model:

```text
gRPC Request
     |
     v
RPC Handler
     |
     v
Interceptor
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

Review:

```text
Authentication interceptors
Authorisation interceptors
Message fields
Object IDs
Service methods
Streaming RPCs
```

---

# WebSockets

Model:

```text
Handshake
   |
   v
Connection
   |
   v
Message
   |
   v
Message Handler
   |
   v
Authorisation
   |
   v
Sensitive Action
```

Handshake authentication does not automatically authorise every WebSocket message.

---

# Background Jobs

Do not restrict analysis to HTTP routes.

Look for:

```text
Schedulers
Workers
Queue consumers
Message listeners
Cron jobs
Background services
Event handlers
```

Potential flow:

```text
HTTP Input
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
Command Execution
```

---

# Second-Order Vulnerabilities

Second-order flows may cross persistence boundaries.

```text
Attacker Input
      |
      v
Database
      |
      v
Later Query
      |
      v
Background Worker
      |
      v
Dangerous Sink
```

Not every persistence boundary will be automatically represented as a complete CodeQL flow.

Manual architecture understanding remains essential.

---

# Secrets

CodeQL can detect some security-sensitive patterns involving secrets.

But use dedicated tools too:

```text
TruffleHog
Git history review
Secret scanners
Repository search
```

A hardcoded-looking string is not automatically a valid secret.

---

# Cryptography

Use CodeQL to identify:

```text
Weak algorithms
Insecure random generation
Hardcoded cryptographic keys
TLS verification problems
Certificate validation problems
Weak password hashing
Unsafe cipher modes
```

Context matters.

For example:

```text
MD5 for non-security cache deduplication
```

is not equivalent to:

```text
MD5 for password storage
```

---

# Logging

Review flows from sensitive information to logging sinks.

Examples:

```text
Passwords
Tokens
Session IDs
API keys
Personal data
Authentication headers
Reset tokens
```

Model:

```text
Sensitive Source
      |
      v
Logger
```

---

# Information Disclosure

CodeQL can help identify:

```text
Stack traces
Debug responses
Verbose exceptions
Secrets in responses
Sensitive logging
Debug endpoints
Development configuration
```

But actual exposure often requires runtime validation.

---

# Race Conditions

Static analysis can identify candidate patterns involving:

```text
Check-then-act
Read-modify-write
Missing transaction
Missing locking
Shared mutable state
```

But exploitability generally depends on runtime concurrency and persistence behaviour.

---

# Rate Limiting

Source review can locate:

```text
Throttle middleware
Rate-limit decorators
Attempt counters
Quota checks
```

But:

```text
No application rate limiter
      !=
No production rate limiting
```

Controls may exist at:

```text
CDN
WAF
API gateway
Reverse proxy
Service mesh
```

---

# Query Metadata

Security queries should include metadata.

Example:

```ql
/**
 * @name Potential command injection
 * @description Finds potentially untrusted input reaching command execution.
 * @kind path-problem
 * @problem.severity error
 * @security-severity 8.8
 * @precision high
 * @id custom/java/command-injection
 * @tags security
 *       external/cwe/cwe-078
 */
```

Metadata controls how results are interpreted and presented.

---

# Alert Queries

An alert query identifies a suspicious location.

Conceptually:

```text
Dangerous API Call
       |
       v
Alert
```

Example use:

```text
Find all Runtime.exec calls
```

---

# Path Queries

A path query identifies:

```text
Source
   |
   v
Flow
   |
   v
Sink
```

For security research, path queries are often much more informative.

---

# Query Development Strategy

Do not begin by writing an extremely complicated global taint query.

Use:

```text
Step 1
Find the sink

Step 2
Understand its AST representation

Step 3
Find the source

Step 4
Understand its AST representation

Step 5
Test local data flow

Step 6
Add global flow

Step 7
Add taint tracking

Step 8
Add path visualization

Step 9
Add framework models

Step 10
Reduce false positives
```

---

# Start with Sink Discovery

Suppose you want command injection.

First query:

```text
Where are command execution APIs?
```

Then manually inspect them.

Only after understanding the application should you build:

```text
HTTP Input
      |
      v
Command Execution
```

This makes query development easier.

---

# Source-First Analysis

Sometimes start from the source.

```text
HTTP Request
      |
      v
Where does this data go?
```

Useful for:

```text
File upload
Password reset
GraphQL resolver
Webhook
WebSocket message
gRPC request
```

---

# Sink-First Analysis

Often more efficient:

```text
Dangerous Sink
      |
      v
Who calls it?
      |
      v
What reaches it?
      |
      v
Can attacker input reach it?
```

Useful for:

```text
Command execution
SQL
Filesystem
HTTP client
Deserialisation
Template evaluation
Dynamic execution
```

---

# Partial Flow

When a data-flow query unexpectedly produces no results, do not immediately conclude:

```text
No vulnerability exists
```

The model may be incomplete.

Use partial-flow debugging techniques to determine:

```text
How far did taint propagate?

Where did the model stop?

Is a library model missing?

Is a wrapper missing?

Is an additional flow step needed?
```

---

# Missing Models

Example:

```text
Request
   |
   v
Custom Framework Wrapper
   |
   X
   |
   v
Sink
```

CodeQL may not know that:

```text
Custom Framework Wrapper
```

propagates attacker-controlled data.

You may need to model it.

---

# Reflection

Reflection can complicate static analysis.

Examples:

```text
Java reflection
.NET reflection
Dynamic JavaScript property access
Python getattr()
Dependency injection
Runtime plugin loading
```

Do not assume static analysis sees every dynamically resolved relationship.

---

# Dynamic Dispatch

Object-oriented applications may call:

```text
Interface
   |
   v
Implementation A
Implementation B
Implementation C
```

Static analysis must determine possible call targets.

This can increase:

```text
Complexity
Analysis time
False-positive possibilities
```

---

# Generated Code

Generated code may:

```text
Increase noise
Contain important security behaviour
Represent framework bindings
Contain protocol code
```

Do not blindly exclude it.

Understand what it represents first.

---

# Framework Magic

Frameworks often use:

```text
Annotations
Decorators
Dependency injection
Reflection
Convention
Generated proxies
Configuration
```

This can make source-to-sink reasoning more difficult.

CodeQL's framework models help, but manual review remains necessary.

---

# Variant Analysis

Variant analysis is one of the strongest CodeQL use cases.

```text
Confirmed Vulnerability
        |
        v
Understand Root Cause
        |
        v
Create Query
        |
        v
Run Against Repository
        |
        v
Find Similar Patterns
        |
        v
Triage Variants
```

---

# Example Variant Analysis

Suppose you confirm:

```java
String command =
    request.getParameter("cmd");

commandService.execute(command);
```

and:

```java
void execute(
    String command
) {

    Runtime
        .getRuntime()
        .exec(command);
}
```

Instead of searching only:

```text
Runtime.exec
```

build a query around:

```text
commandService.execute()
```

Then ask:

```text
Which HTTP sources can reach this helper?
```

This may reveal additional vulnerable routes.

---

# Variant Analysis Across Repositories

The CodeQL VS Code extension includes variant-analysis functionality for running suitable queries at scale against repositories available through the supported GitHub workflow.

This can be useful when:

```text
The same vulnerable library is used across repositories
The same internal framework is reused
The same dangerous helper is copied
The same coding pattern appears across projects
```

Always ensure assessment authorisation covers every repository being analyzed.

---

# Project-Specific Queries

Generic query:

```text
Find Runtime.exec()
```

Project-specific query:

```text
Find attacker-controlled values reaching DiagnosticService.execute()
```

Generic query:

```text
Find HttpClient.SendAsync()
```

Project-specific query:

```text
Find user-controlled URLs reaching ExternalPreviewService.fetch()
```

Generic query:

```text
Find SQL execution
```

Project-specific query:

```text
Find HTTP values reaching ReportingRepository.runRawQuery()
```

Project-specific queries can dramatically improve signal.

---

# Query Packs

CodeQL queries can be organised into packs.

A useful structure:

```text
codeql/
├── qlpack.yml
├── java/
│   ├── command-injection.ql
│   ├── ssrf.ql
│   └── authorization.ql
├── csharp/
├── javascript/
└── python/
```

However, CodeQL packs are language/library-aware, so in practice you may maintain separate packs where dependencies differ.

---

# Example Pack Purpose

```text
security-review-java
security-review-csharp
security-review-javascript
security-review-python
```

Then:

```text
Confirmed Finding
       |
       v
Custom Query
       |
       v
Security Review Pack
       |
       v
Future Assessments
```

---

# Query Tests

Custom security queries should be tested.

Test cases should contain:

```text
Expected positive examples
Expected negative examples
Edge cases
Wrapper functions
Sanitised flows
Unsafe flows
Framework variants
```

The purpose is to prevent:

```text
Query regression
False-positive growth
False-negative regressions
```

---

# Query Precision

A security query may have precision metadata such as:

```text
very-high
high
medium
low
```

Do not confuse query precision with vulnerability severity.

A query can be:

```text
High precision
```

while identifying:

```text
Medium severity vulnerability
```

or vice versa.

---

# False Positives

Common causes include:

```text
Spurious global flows
Trusted sources
Unreachable code
Effective validation
Effective sanitisation
Framework protections
Security checks not modeled
Test code
Generated code
Impossible call target
Infrastructure controls
```

---

# False Negatives

Common causes include:

```text
Missing framework model
Custom wrapper
Reflection
Dynamic dispatch
Generated behaviour
Cross-service flow
Database persistence
Message queue
Background job
Unsupported library
Custom sanitizer
Dynamic language behaviour
```

Therefore:

```text
No CodeQL result
      !=
No vulnerability
```

---

# Triage Workflow

For each result:

```text
CodeQL Result
      |
      v
Open File in VS Code
      |
      v
Review Source
      |
      v
Review Path
      |
      v
Review Sink
      |
      v
Review Validation
      |
      v
Review Sanitisation
      |
      v
Review Authentication
      |
      v
Review Authorisation
      |
      v
Review Runtime Feasibility
      |
      v
Validate Dynamically
```

---

# Triage Template

```text
ID:
CQL-001

Query:
custom/java/request-to-command

File:
src/main/java/controllers/ToolsController.java

Source:
@RequestParam("host")

Sink:
Runtime.exec()

Path:
ToolsController
    -> DiagnosticService
    -> CommandBuilder
    -> Runtime.exec

Reachable:
Yes / No / Unknown

Attacker Controlled:
Yes / No / Unknown

Validation:
None / Present / Unknown

Sanitisation:
None / Present / Unknown

Authentication:
...

Authorisation:
...

Framework Controls:
...

Runtime Validation:
...

Impact:
...

Status:
Investigating / Confirmed / Rejected
```

---

# Dynamic Validation

Static analysis should guide dynamic testing.

Example:

```text
CodeQL

@RequestParam
      |
      v
DiagnosticService
      |
      v
Runtime.exec
```

Map it to:

```text
POST /api/tools/ping
```

Then use Burp:

```text
Proxy
   |
   v
Repeater
   |
   v
Controlled Input
   |
   v
Observe Behaviour
```

Do not dynamically test systems outside the authorised scope.

---

# Burp + CodeQL Workflow

```text
CodeQL
   |
   v
Potential Source-to-Sink Path
   |
   v
Find Controller / Route
   |
   v
Burp HTTP History
   |
   v
Identify Request
   |
   v
Repeater
   |
   v
Controlled Validation
   |
   v
Confirmed / Rejected
```

This combination is especially effective for:

```text
SQL Injection
Command Injection
SSRF
Path Traversal
XSS
Open Redirect
IDOR
Mass Assignment
Authentication flaws
Authorisation flaws
```

---

# Baseline Review

For an initial assessment:

```text
Full Repository
      |
      v
CodeQL Database
      |
      v
Built-In Security Queries
      |
      v
Custom Queries
      |
      v
Manual Triage
```

This establishes a security baseline.

---

# Diff-Based Review

For later reviews:

```text
Previous Version
      |
      v
New Commit / Pull Request
      |
      v
Changed Code
      |
      v
Security-Sensitive Changes
      |
      v
Targeted CodeQL Queries
```

Focus on changes involving:

```text
Routes
Authentication
Authorisation
SQL
Command execution
HTTP clients
Filesystem
Uploads
Deserialisation
Templates
Security configuration
Dependencies
```

But remember that a small code change can alter a flow through unchanged code.

---

# Security Review Strategy

A strong workflow is:

```text
PASS 1
Architecture

PASS 2
Routes

PASS 3
Authentication

PASS 4
Authorisation

PASS 5
Sources

PASS 6
Sinks

PASS 7
Built-in CodeQL security queries

PASS 8
Source-to-sink queries

PASS 9
Custom project models

PASS 10
Variant analysis

PASS 11
Dynamic validation
```

---

# Recommended Vulnerability Passes

```text
Pass 01 - Authentication

Pass 02 - Authorisation

Pass 03 - IDOR / BOLA

Pass 04 - SQL Injection

Pass 05 - NoSQL Injection

Pass 06 - LDAP Injection

Pass 07 - Command Injection

Pass 08 - SSRF

Pass 09 - Path Traversal

Pass 10 - File Upload

Pass 11 - Deserialisation

Pass 12 - XML / XXE

Pass 13 - SSTI

Pass 14 - XSS

Pass 15 - DOM XSS

Pass 16 - Open Redirect

Pass 17 - Prototype Pollution

Pass 18 - Mass Assignment

Pass 19 - JWT

Pass 20 - OAuth / OIDC

Pass 21 - SAML

Pass 22 - Password Reset

Pass 23 - MFA

Pass 24 - GraphQL

Pass 25 - gRPC

Pass 26 - WebSockets

Pass 27 - Secrets

Pass 28 - Cryptography

Pass 29 - Logging

Pass 30 - Background Jobs

Pass 31 - Business Logic Variants

Pass 32 - Confirmed Vulnerability Variants
```

---

# Java / Spring Strategy

Start with:

```text
Controllers
@RequestMapping
@GetMapping
@PostMapping
@PutMapping
@PatchMapping
@DeleteMapping
```

Then:

```text
@RequestParam
@PathVariable
@RequestBody
@RequestHeader
@CookieValue
```

Then security:

```text
SecurityFilterChain
@PreAuthorize
@PostAuthorize
@Secured
hasRole
hasAuthority
permitAll
```

Then sinks:

```text
Runtime.exec
ProcessBuilder
SQL
HTTP clients
Filesystem
XML
Deserialisation
Templates
Redirects
```

Then CodeQL data flow.

---

# .NET Strategy

Start with:

```text
Controllers
Minimal APIs
MapGet
MapPost
MapPut
MapDelete
```

Sources:

```text
Request.Query
Request.Form
Request.Headers
Request.Cookies
Route values
Model binding
```

Security:

```text
[Authorize]
[AllowAnonymous]
Policies
Roles
Claims
```

Sinks:

```text
Process.Start
Raw SQL
HttpClient
Filesystem
XML
Deserialisation
Razor
Redirects
```

Then CodeQL data flow.

---

# Python Strategy

Sources:

```text
Flask request
Django request
FastAPI parameters
Headers
Cookies
Uploads
```

Sinks:

```text
os.system
subprocess
eval
exec
SQL
requests
httpx
open
pickle
YAML
XML
Templates
Redirects
```

Then:

```text
Local data flow
      |
      v
Global data flow
      |
      v
Taint tracking
```

---

# Django Strategy

Review:

```text
urls.py
Views
ViewSets
Serializers
Authentication classes
Permission classes
get_queryset
get_object
Raw SQL
CSRF exemptions
Uploads
Redirects
Templates
Settings
Celery tasks
```

Use CodeQL Python analysis for deeper source-to-sink relationships.

---

# Flask Strategy

Review:

```text
@app.route
Blueprints
request.args
request.form
request.values
request.json
request.files
session
```

Then:

```text
SQL
os.system
subprocess
requests
httpx
open
pickle
render_template_string
redirect
```

---

# Node.js Strategy

Sources:

```text
req.query
req.params
req.body
req.headers
req.cookies
WebSocket messages
GraphQL arguments
```

Sinks:

```text
child_process
SQL
MongoDB
fetch
axios
fs
eval
Function
templates
redirects
```

Then review:

```text
Authentication middleware
Authorisation middleware
Middleware order
Prototype pollution
Mass assignment
JWT
GraphQL
WebSockets
```

---

# Client-Side JavaScript Strategy

Sources:

```text
location
document.URL
document.referrer
window.name
postMessage
localStorage
sessionStorage
API responses
```

Sinks:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
eval
Function
location
window.open
script.src
iframe.srcdoc
```

CodeQL JavaScript analysis can be particularly useful for DOM source-to-sink analysis.

---

# PHP Strategy

CodeQL currently does not provide official PHP database support.

Use:

```text
ripgrep
     |
     v
OpenGrep / Semgrep
     |
     v
Manual Source-to-Sink Review
     |
     v
Burp Validation
```

Do not omit PHP from source review simply because CodeQL does not support it.

---

# Query Performance

Global data-flow queries can be expensive.

Avoid:

```text
Every expression
      ->
Every expression
```

Instead define specific:

```text
Sources
Sinks
Frameworks
Types
APIs
```

Conceptually:

```text
Broad Global Flow
       |
       v
Huge Search Space
```

versus:

```text
HTTP Sources
      |
      v
Command Sinks
      |
      v
Focused Search
```

---

# Performance Strategy

```text
1. Start with AST query

2. Narrow sink

3. Narrow source

4. Test local flow

5. Add global flow

6. Add taint

7. Add framework constraints

8. Add path output

9. Profile slow query if necessary
```

---

# Do Not Overmodel

Suppose you add:

```text
Every function return
      ->
Every caller
```

as an additional taint step.

You may generate huge numbers of impossible flows.

Models should reflect actual program semantics.

---

# Security Controls Must Be Modeled Carefully

Do not automatically treat a function named:

```text
sanitize()
validate()
clean()
secure()
check()
```

as a sanitizer.

Inspect what it actually does.

Example:

```python
def sanitize(value):
    return value.replace("<", "")
```

This may not provide meaningful protection for:

```text
SQL
Shell
URL
Filesystem
HTML attributes
JavaScript contexts
```

---

# CodeQL Does Not Understand Business Intent Automatically

Suppose:

```text
Manager
    can
approve invoice
```

and:

```text
Employee
    cannot
approve invoice
```

CodeQL can help identify:

```text
approveInvoice()
callers
role checks
permission checks
```

But it does not inherently know the organisation's intended business policy.

Manual review remains essential.

---

# Variant Analysis Model

```text
One Confirmed Finding
        |
        v
Identify Primitive
        |
        +--> Source
        +--> Sink
        +--> Wrapper
        +--> Missing Control
        |
        v
Write CodeQL Query
        |
        v
Run Against Database
        |
        v
Find Variants
        |
        v
Manual Triage
```

---

# Example Missing Authorisation Variant

Known safe pattern:

```text
Controller
    |
    v
checkPermission()
    |
    v
deleteDocument()
```

Potential variant:

```text
Controller
    |
    v
deleteDocument()
```

A custom query can search:

```text
All callers of deleteDocument()
```

Then investigate whether each path has the expected security control.

Do not assume absence of one exact helper proves missing authorisation.

---

# Source Review Evidence

Store:

```text
review/
├── codeql/
│   ├── version.txt
│   ├── database-info.txt
│   ├── default.sarif
│   ├── security-extended.sarif
│   ├── custom.sarif
│   ├── queries/
│   └── notes.md
│
├── opengrep/
├── semgrep/
├── ripgrep/
└── findings/
```

---

# Record Version

```bash
codeql version
```

Store:

```text
CodeQL Version:
<version>

Repository:
<repository>

Branch:
<branch>

Commit:
<commit>

Database Language:
<language>

Database Build Mode:
<mode>

Queries:
<query pack / suite>

Assessment Date:
<date>
```

---

# Reproducibility

A CodeQL result should ideally be reproducible from:

```text
Repository commit
        +
CodeQL version
        +
Database creation command
        +
Build environment
        +
Query pack version
        +
Custom query version
```

---

# Finding Validation Checklist

Before reporting:

```text
[ ] Query result manually reviewed
[ ] Code reachable
[ ] Source identified
[ ] Attacker control established
[ ] Source-to-sink path understood
[ ] Transformations reviewed
[ ] Validation reviewed
[ ] Sanitisation reviewed
[ ] Authentication reviewed
[ ] Authorisation reviewed
[ ] Framework protection reviewed
[ ] Infrastructure controls considered
[ ] Runtime feasibility established
[ ] Security impact established
[ ] Dynamic validation performed where appropriate
```

---

# CodeQL Query Checklist

```text
[ ] Query purpose documented
[ ] Correct language library used
[ ] Sink modeled correctly
[ ] Source modeled correctly
[ ] Local flow tested
[ ] Global flow justified
[ ] Taint tracking justified
[ ] Sanitizers justified
[ ] Additional flow steps justified
[ ] Framework models considered
[ ] Positive tests created
[ ] Negative tests created
[ ] False positives reviewed
[ ] False negatives considered
[ ] Query performance acceptable
[ ] Query metadata correct
[ ] Query version controlled
```

---

# Database Checklist

```text
[ ] Correct repository
[ ] Correct commit
[ ] Correct language
[ ] Correct source root
[ ] Dependencies available
[ ] Build mode appropriate
[ ] Build completed where required
[ ] Database contains expected source
[ ] Generated source considered
[ ] Exclusions reviewed
[ ] CodeQL version recorded
```

---

# VS Code Checklist

```text
[ ] CodeQL extension installed
[ ] Database selected
[ ] Query pack detected
[ ] Query runs successfully
[ ] Results inspected
[ ] Path explanations reviewed
[ ] Go to Definition used
[ ] Find All References used
[ ] Call Hierarchy used
[ ] Relevant source and sink files reviewed
```

---

# Common Mistakes

## Mistake 1

```text
CodeQL found it
    =
vulnerability confirmed
```

Incorrect.

---

## Mistake 2

```text
No CodeQL finding
    =
secure
```

Incorrect.

---

## Mistake 3

Only running built-in queries.

Built-in queries are valuable, but application-specific vulnerabilities may require custom queries.

---

## Mistake 4

Only searching sinks.

A sink is not automatically vulnerable.

---

## Mistake 5

Ignoring authorisation.

Many serious application vulnerabilities are caused by business and access-control logic rather than classic injection sinks.

---

## Mistake 6

Using global data flow for everything.

Start with narrower queries.

---

## Mistake 7

Ignoring framework models.

Incorrect modelling can produce both false positives and false negatives.

---

## Mistake 8

Treating every apparent sanitizer as effective.

Review the implementation.

---

## Mistake 9

Ignoring second-order flows.

Data may pass through:

```text
Database
Queue
Cache
File
Background worker
```

before reaching a sink.

---

## Mistake 10

Forcing CodeQL onto unsupported languages.

For PHP, use other static-analysis tools.

---

# Complete CodeQL Workflow

```text
1. Obtain authorised repository

2. Record commit

3. Open repository in VS Code

4. Identify languages

5. Identify frameworks

6. Map application architecture

7. Map trust boundaries

8. Map routes

9. Map authentication

10. Map authorisation

11. Identify sources

12. Identify sinks

13. Install / verify CodeQL CLI

14. Verify language extractor

15. Create CodeQL database

16. Verify database

17. Run built-in queries

18. Review default-suite findings

19. Run broader security queries where appropriate

20. Triage findings

21. Identify interesting sinks

22. Identify interesting sources

23. Write custom AST queries

24. Test local data flow

25. Add global data flow

26. Add taint tracking

27. Convert useful queries to path queries

28. Review path explanations

29. Add project-specific models

30. Perform variant analysis

31. Validate candidates dynamically

32. Confirm vulnerabilities

33. Search for related variants

34. Save queries and evidence

35. Document remediation

36. Retest
```

---

# Recommended Combined Workflow

```text
                    REPOSITORY
                        |
                        v
                 VISUAL STUDIO CODE
                        |
                        v
                 UNDERSTAND CODE
                        |
           +------------+------------+
           |                         |
           v                         v
       ripgrep                 OpenGrep/Semgrep
           |                         |
           v                         v
      Fast Search               SAST Rules
           |                         |
           +------------+------------+
                        |
                        v
                 Candidate Areas
                        |
                        v
                      CodeQL
                        |
             +----------+----------+
             |          |          |
             v          v          v
            AST     Data Flow   Taint Flow
             |          |          |
             +----------+----------+
                        |
                        v
                  Path Queries
                        |
                        v
                   VS Code
                        |
                        v
                  Manual Trace
                        |
                        v
                Security Controls
                        |
                        v
                    Burp Suite
                        |
                        v
               Runtime Validation
                        |
                        v
                Confirmed Finding
                        |
                        v
                 Variant Analysis
```

---

# Final CodeQL Testing Model

```text
SOURCE
  |
  v
Can an attacker control it?
  |
  v
DATA FLOW
  |
  +--> local flow
  +--> function calls
  +--> method calls
  +--> object properties
  +--> framework models
  +--> additional flow steps
  |
  v
TAINT PROPAGATION
  |
  +--> concatenation
  +--> transformations
  +--> collections
  +--> wrappers
  |
  v
SECURITY CONTROLS
  |
  +--> validation
  +--> sanitisation
  +--> authentication
  +--> authorisation
  |
  v
SINK
  |
  v
Is the sink security-sensitive?
  |
  v
PATH QUERY
  |
  v
Manual Path Review
  |
  v
Runtime Validation
  |
  v
Impact
```

A meaningful vulnerability requires:

```text
Reachable source
       +
Attacker control
       +
Feasible propagation
       +
Security-sensitive sink
       +
Absent / ineffective controls
       +
Security impact
```

Not merely:

```text
CodeQL produced a result
```

---

# Quick Reference

## Version

```bash
codeql version
```

## Help

```bash
codeql --help
```

## Available Languages

```bash
codeql resolve languages
```

## Available Packs

```bash
codeql resolve packs
```

## Python Database

```bash
codeql database create codeql-db-python \
  --language=python
```

## JavaScript / TypeScript Database

```bash
codeql database create codeql-db-js \
  --language=javascript-typescript
```

## C# Database

```bash
codeql database create codeql-db-csharp \
  --language=csharp
```

## Java / Kotlin Database

```bash
codeql database create codeql-db-java \
  --language=java-kotlin
```

## C# No-Build Database

```bash
codeql database create codeql-db-csharp \
  --language=csharp \
  --build-mode=none
```

## C# Autobuild

```bash
codeql database create codeql-db-csharp \
  --language=csharp \
  --build-mode=autobuild
```

## C# Manual Build

```bash
codeql database create codeql-db-csharp \
  --language=csharp \
  --command="dotnet build"
```

## Java Maven Build

```bash
codeql database create codeql-db-java \
  --language=java-kotlin \
  --command="mvn clean package -DskipTests"
```

## Java Gradle Build

```bash
codeql database create codeql-db-java \
  --language=java-kotlin \
  --command="./gradlew build -x test"
```

## Database Information

```bash
codeql database info codeql-db
```

## JavaScript Analysis

```bash
codeql database analyze \
  codeql-db-js \
  codeql/javascript-queries \
  --format=sarif-latest \
  --output=javascript-results.sarif
```

## Python Analysis

```bash
codeql database analyze \
  codeql-db-python \
  codeql/python-queries \
  --format=sarif-latest \
  --output=python-results.sarif
```

## Java Analysis

```bash
codeql database analyze \
  codeql-db-java \
  codeql/java-queries \
  --format=sarif-latest \
  --output=java-results.sarif
```

## C# Analysis

```bash
codeql database analyze \
  codeql-db-csharp \
  codeql/csharp-queries \
  --format=sarif-latest \
  --output=csharp-results.sarif
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
 OpenGrep / Semgrep
        |
        v
      CodeQL
        |
        +--> AST
        +--> Control Flow
        +--> Local Data Flow
        +--> Global Data Flow
        +--> Taint Tracking
        +--> Path Queries
        |
        v
   Manual Review
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
Variant Analysis
        |
        v
Custom CodeQL Query
```

---

# References

## CodeQL Documentation

[docs](https://codeql.github.com/docs/)

## GitHub CodeQL Documentation

[codeql cli](https://docs.github.com/en/code-security/codeql-cli)

## CodeQL CLI

[CodeQL CLI](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-the-command-line/set-up-codeql-cli)

## Preparing Code for CodeQL Analysis

[Preparing Code for CodeQL Analysis](https://docs.github.com/en/code-security/tutorials/customize-code-scanning/prepare-code-for-analysis)

## CodeQL Query Suites

[CodeQL Query Suites](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-query-suites)

## CodeQL Queries

[CodeQL Queries](https://codeql.github.com/docs/writing-codeql-queries/)

## About CodeQL Queries

[About CodeQL Queries](https://codeql.github.com/docs/writing-codeql-queries/about-codeql-queries/)

## Data Flow Analysis

[Data Flow Analysis](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/)

## Creating Path Queries

[Creating Path Queries](https://codeql.github.com/docs/writing-codeql-queries/creating-path-queries/)

## CodeQL for Visual Studio Code

[CodeQL for Visual Studio Code](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-for-vs-code)

## Scan from Visual Studio Code

[Scan from Visual Studio Code](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-vs-code)

## JavaScript / TypeScript Data Flow

[JavaScript / TypeScript Data Flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/)

## JavaScript Data Flow Cheat Sheet

[JavaScript Data Flow Cheat Sheet](https://codeql.github.com/docs/codeql-language-guides/data-flow-cheat-sheet-for-javascript/)

## Python Data Flow

[Python Data Flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-python/)

## Java / Kotlin Data Flow

[Java / Kotlin Data Flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-java/)

## C# Data Flow

[C# Data Flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-csharp/)

## CodeQL GitHub Repository

[CodeQL GitHub Repository](https://github.com/github/codeql)

## OWASP Secure Code Review Cheat Sheet

[OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html)

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

## OWASP Static Code Analysis

[OWASP Static Code Analysis](https://owasp.org/www-community/controls/Static_Code_Analysis)

---

# Related Static Analysis Notes

```text
docs/source-code-review/static-analysis/index.md
docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/semgrep.md
docs/source-code-review/static-analysis/opengrep.md
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
docs/web/input-validation.md

docs/web/authentication.md
docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/mfa.md
docs/web/saml.md

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
