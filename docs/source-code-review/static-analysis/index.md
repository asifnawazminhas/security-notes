# Static Analysis for Source Code Review

Static analysis is the examination of source code without relying solely on executing the application.

During a security-focused source code review, static analysis helps identify:

```text
Application entry points
User-controlled input
Authentication controls
Authorisation controls
Dangerous functions
Security-sensitive APIs
Potential source-to-sink flows
Hard-coded secrets
Unsafe configuration
Vulnerable dependencies
Repeated vulnerable patterns
```

Static analysis should not be treated as:

```text
Scanner Result
     =
Confirmed Vulnerability
```

Instead:

```text
Static Analysis
      |
      v
Candidate Finding
      |
      v
Manual Source Review
      |
      v
Source-to-Sink Analysis
      |
      v
Security Control Analysis
      |
      v
Exploitability Assessment
      |
      v
Dynamic Validation
      |
      v
Confirmed Finding
```

This section focuses on four tools that complement each other:

```text
ripgrep
Semgrep
OpenGrep
CodeQL
```

They solve different problems.

---

# Tool Overview

A practical way to think about the tools is:

```text
ripgrep
   |
   +--> Fast text and regex searching
   |
   +--> Manual source/sink discovery
   |
   +--> Excellent for initial reconnaissance

Semgrep
   |
   +--> Syntax-aware static analysis
   |
   +--> Security rules
   |
   +--> Custom pattern matching
   |
   +--> Data-flow and taint-oriented analysis

OpenGrep
   |
   +--> Open-source static analysis
   |
   +--> Semgrep-style rules and workflows
   |
   +--> Custom security rule development
   |
   +--> Useful for local and CI scanning

CodeQL
   |
   +--> Semantic code analysis
   |
   +--> Data-flow analysis
   |
   +--> Taint tracking
   |
   +--> Cross-function investigation
   |
   +--> Advanced variant analysis
```

The tools should not necessarily compete with each other.

A strong review can use all four.

---

# Recommended Workflow

```text
                     SOURCE REPOSITORY
                            |
                            v
                    Understand Project
                            |
                            v
                    Identify Technology
                            |
                            v
                  Map Application Structure
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
         ripgrep        Semgrep        OpenGrep
             |              |              |
             |              |              |
             +--------------+--------------+
                            |
                            v
                    Candidate Findings
                            |
                            v
                    Manual VS Code Review
                            |
                            v
                    Source-to-Sink Trace
                            |
                            v
                    Security Controls
                            |
                            v
                       Exploitability
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
                          CodeQL
```

This is not a mandatory sequence.

For some applications, CodeQL may be used much earlier.

For others, a few well-designed `ripgrep` searches may reveal the most important attack surface quickly.

---

# Core Principle

The most important rule in this section is:

```text
Tool finding
    !=
Vulnerability
```

Similarly:

```text
Dangerous API
    !=
Exploitable vulnerability
```

For example:

```text
ProcessBuilder
```

does not automatically mean:

```text
Command Injection
```

Likewise:

```text
HttpClient
```

does not automatically mean:

```text
SSRF
```

and:

```text
createNativeQuery()
```

does not automatically mean:

```text
SQL Injection
```

The reviewer must establish the complete data flow.

---

# What Proves a Vulnerability?

A useful model is:

```text
Attacker-Controlled Source
           |
           v
      Reachable Flow
           |
           v
     Transformations
           |
           v
   Security Controls
           |
           v
Security-Sensitive Sink
           |
           v
        Impact
```

A candidate becomes much stronger when all of the following can be established:

```text
[+] Attacker controls the input

[+] The relevant code is reachable

[+] The input reaches the sink

[+] The input remains attacker-controlled

[+] Security controls are absent or ineffective

[+] The sink operates in a dangerous context

[+] Exploitation produces meaningful security impact
```

---

# Static Analysis and Visual Studio Code

Static-analysis tools become significantly more useful when combined with an IDE.

Visual Studio Code can be used to:

```text
Open scanner findings
Navigate definitions
Find references
Inspect callers
Inspect callees
Search the repository
Trace variables
Compare security controls
Review Git changes
Run tools from the terminal
```

A practical workflow is:

```text
Static Analysis Result
        |
        v
Open File in VS Code
        |
        v
Inspect Function
        |
        v
Go to Definition
        |
        v
Find References
        |
        v
Show Call Hierarchy
        |
        v
Trace Input
        |
        v
Inspect Security Controls
        |
        v
Determine Exploitability
```

---

# Source-to-Sink Analysis

Static analysis becomes much easier when code is viewed in terms of sources and sinks.

## Source

A source is a location where potentially attacker-controlled data enters the application.

Examples:

```text
HTTP query parameter
HTTP request body
HTTP header
Cookie
Path parameter
Uploaded file
GraphQL argument
WebSocket message
gRPC message
Webhook
Message queue
Database value originating from a user
```

## Sink

A sink is a security-sensitive operation.

Examples:

```text
SQL query
Operating system command
File read
File write
HTTP request
HTML output
Template rendering
Deserialisation
XML parsing
Dynamic code execution
Redirect
LDAP query
```

The basic model is:

```text
SOURCE
  |
  v
User-Controlled Data
  |
  v
TRANSFORMATIONS
  |
  +-- validation
  +-- parsing
  +-- normalisation
  +-- sanitisation
  +-- encoding
  +-- authorisation
  +-- business logic
  |
  v
SINK
```

---

# Forward Analysis

Forward analysis starts at a source.

Example:

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

Questions:

```text
Where does this input go?

Is it validated?

Is it normalised?

Is it encoded?

Is it parameterised?

Is authorisation performed?

Does it reach a dangerous sink?
```

---

# Reverse Sink Analysis

Reverse analysis starts with dangerous functionality.

Example:

```text
ProcessBuilder
      ^
      |
CommandService
      ^
      |
ReportService
      ^
      |
ReportController
      ^
      |
HTTP Parameter
```

This approach can be extremely efficient.

Large applications may have:

```text
Thousands of input parameters
```

but only:

```text
A few command execution sinks

A few deserialisation sinks

A few outbound HTTP clients

A few raw SQL construction locations
```

Therefore:

```text
Find Sink
   |
   v
Trace Backwards
   |
   v
Find Source
```

is often a useful review strategy.

---

# Use Both Directions

The strongest approach combines:

```text
SOURCE -> SINK
```

with:

```text
SINK -> SOURCE
```

For example:

```text
Route Mapping
     |
     v
Input Sources
     |
     v
Forward Analysis

        +

Dangerous API Search
     |
     v
Sink Discovery
     |
     v
Reverse Analysis
```

---

# Static Analysis Layers

A useful static-analysis model has several layers.

```text
Layer 1 - Text Search
        |
        v
Layer 2 - Syntax-Aware Matching
        |
        v
Layer 3 - Data Flow
        |
        v
Layer 4 - Taint Tracking
        |
        v
Layer 5 - Semantic / Program Analysis
        |
        v
Layer 6 - Manual Context Analysis
```

The four tools in this section fit approximately into these layers.

---

# Layer 1 - ripgrep

`ripgrep` performs extremely fast repository-wide text and regular-expression searching.

Example:

```bash
rg -n 'ProcessBuilder' .
```

Search multiple sinks:

```bash
rg -n \
'ProcessBuilder|Runtime\.getRuntime|Process\.Start|os\.system|child_process\.exec' \
.
```

This is excellent for:

```text
Reconnaissance
Route discovery
Source discovery
Sink discovery
Authentication discovery
Authorisation discovery
Configuration discovery
Secret hunting
Variant hunting
```

But `ripgrep` generally does not understand program semantics.

It sees text.

---

# Layer 2 - Semgrep

Semgrep understands source code structure.

Instead of simply searching for text such as:

```text
exec(
```

a rule can describe code patterns.

Conceptually:

```yaml
patterns:
  - pattern: dangerous_function(...)
```

Semgrep can therefore reduce some of the noise associated with raw regular expressions.

It is useful for:

```text
Dangerous API detection
Security anti-patterns
Framework-specific rules
Custom vulnerability patterns
Rule-based source review
Taint-oriented analysis
CI scanning
```

---

# Layer 3 - OpenGrep

OpenGrep provides an open-source static-analysis workflow with Semgrep-style rule concepts and is particularly useful when you want to maintain local security rules and scanning workflows.

A practical use case is:

```text
Manual Review
     |
     v
Discover Vulnerable Pattern
     |
     v
Create OpenGrep Rule
     |
     v
Scan Entire Repository
     |
     v
Discover Variants
```

For example, suppose manual review discovers a dangerous internal helper:

```text
executeSystemCommand()
```

Instead of manually searching every call site, a rule can be created to identify usage across the codebase.

OpenGrep is therefore particularly useful for:

```text
Custom rules
Security pattern libraries
Local SAST
CI scanning
Variant analysis
Organisation-specific dangerous APIs
```

Because OpenGrep is actively developed, verify the installed version's current CLI and supported rule features before building automation around a particular command or rule feature.

---

# Layer 4 - CodeQL

CodeQL models code semantically.

Instead of asking only:

```text
Does this function exist?
```

CodeQL can help answer questions such as:

```text
Can data from this source reach this sink?
```

Conceptually:

```text
HTTP Parameter
      |
      v
Controller
      |
      v
Helper
      |
      v
Service
      |
      v
Repository
      |
      v
SQL Sink
```

This makes CodeQL particularly useful for:

```text
Data-flow analysis
Taint tracking
Cross-function analysis
Variant analysis
Complex applications
Custom security research
```

---

# Tool Comparison

| Capability | ripgrep | Semgrep | OpenGrep | CodeQL |
|---|---|---|---|---|
| Fast text search | Excellent | Not primary purpose | Not primary purpose | No |
| Regex search | Excellent | Limited role | Limited role | No |
| Syntax-aware analysis | No | Yes | Yes | Yes |
| Custom rules | Regex-based | Yes | Yes | Yes |
| Data-flow analysis | Manual | Yes, depending on rule/engine | Depends on supported engine/features | Strong |
| Taint analysis | Manual | Supported workflows | Depends on supported engine/features | Strong |
| Cross-function analysis | Manual | Engine/rule dependent | Engine/rule dependent | Strong |
| Variant analysis | Good manually | Good | Good | Excellent |
| Initial reconnaissance | Excellent | Good | Good | Usually heavier |
| CI integration | Scriptable | Yes | Yes | Yes |
| Learning curve | Low | Medium | Medium | High |
| Manual review companion | Excellent | Excellent | Excellent | Excellent |

The exact capabilities of Semgrep and OpenGrep can evolve between versions.

Always verify tool-specific functionality against the installed release.

---

# Why ripgrep Still Matters

Advanced SAST does not replace simple searching.

A reviewer may want to answer:

```text
Where are all controllers?

Where is authentication configured?

Where is HttpClient used?

Where is ProcessBuilder used?

Where are files written?

Where is JWT parsed?

Where are redirects created?

Where are secrets referenced?
```

For these questions, `ripgrep` is often faster than creating a static-analysis query.

---

# Why Semgrep Matters

Semgrep becomes useful when:

```text
Text search creates too much noise

You need syntax-aware matching

You want reusable security rules

You want framework-specific detection

You want automated scanning

You want to turn manual findings into rules
```

Example:

```text
Manual Finding
      |
      v
Understand Code Pattern
      |
      v
Write Semgrep Rule
      |
      v
Scan Repository
      |
      v
Find Variants
```

---

# Why OpenGrep Matters

OpenGrep is useful when you want an open-source static-analysis workflow that can be incorporated into:

```text
Local pentesting environments
Source code review workstations
CI pipelines
Custom security tooling
Internal rule repositories
Security research
```

A useful model is:

```text
Security Researcher
       |
       v
Find Interesting Pattern
       |
       v
Write Rule
       |
       v
Run OpenGrep
       |
       v
Review Matches
       |
       v
Improve Rule
       |
       v
Build Rule Library
```

Over time this creates a personal security knowledge base encoded as executable rules.

---

# Why CodeQL Matters

CodeQL becomes particularly useful when:

```text
The repository is large

Data passes through many functions

Simple pattern matching is insufficient

You need semantic analysis

You are performing variant analysis

You are researching vulnerability classes

You need custom taint tracking
```

Example:

```text
Source
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
Sink
```

Manually tracing this is possible.

CodeQL can help automate portions of the analysis.

---

# Static Analysis Is Not Just Vulnerability Scanning

Static analysis should also be used for architecture discovery.

Examples:

```text
Routes
Controllers
Services
Repositories
Authentication
Authorisation
Middleware
Filters
Interceptors
Database clients
HTTP clients
File APIs
Template engines
Message queues
Background jobs
WebSockets
GraphQL
gRPC
```

This information helps build the application security model before individual vulnerabilities are investigated.

---

# Phase 1 - Repository Reconnaissance

Start by identifying the project.

```bash
ls -la
```

Useful discovery:

```bash
find . -maxdepth 2 -type f | sort
```

Look for:

```text
pom.xml
build.gradle
build.gradle.kts
*.sln
*.csproj
composer.json
requirements.txt
pyproject.toml
package.json
Dockerfile
docker-compose.yml
application.yml
application.properties
appsettings.json
.env
```

---

# Phase 2 - Identify Languages

Useful:

```bash
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -nr
```

This can provide a rough view of file extensions.

Do not rely on extensions alone to determine the application architecture.

---

# Phase 3 - Exclude Noise

Common generated or dependency directories include:

```text
node_modules
vendor
target
build
dist
bin
obj
coverage
.git
```

For `ripgrep`, exclusions can be added with:

```bash
rg \
-g '!node_modules/**' \
-g '!vendor/**' \
-g '!target/**' \
-g '!build/**' \
-g '!dist/**' \
PATTERN \
.
```

Static-analysis tools should similarly be configured to avoid spending excessive time analysing irrelevant generated or vendored code unless those files are intentionally part of the review.

---

# Phase 4 - Route Discovery

Before searching for vulnerabilities, map the attack surface.

## Java / Spring

```bash
rg -n \
'@RequestMapping|@GetMapping|@PostMapping|@PutMapping|@PatchMapping|@DeleteMapping|@RestController|@Controller' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'\[Route|\[HttpGet|\[HttpPost|\[HttpPut|\[HttpPatch|\[HttpDelete|MapGet\(|MapPost\(|MapPut\(|MapDelete\(' \
-g '*.cs' \
.
```

## Flask

```bash
rg -n \
'@.*\.route\(' \
-g '*.py' \
.
```

## Django

```bash
rg -n \
'path\(|re_path\(' \
-g '*.py' \
.
```

## Express

```bash
rg -n \
'app\.(get|post|put|patch|delete)|router\.(get|post|put|patch|delete)' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Phase 5 - Authentication Discovery

Search:

```bash
rg -ni \
'authenticate|authentication|login|logout|password|jwt|oauth|oidc|saml|mfa|totp|session' \
.
```

The objective is to map:

```text
Login
  |
  v
Credential Validation
  |
  v
Identity
  |
  v
Session / Token
  |
  v
Authenticated Request
```

---

# Phase 6 - Authorisation Discovery

Search:

```bash
rg -ni \
'authorize|authorise|permission|role|policy|access.?control|isAdmin|hasRole|hasAuthority|PreAuthorize' \
.
```

Then determine:

```text
Where is authorisation performed?

Route?

Middleware?

Service?

Repository?

Database query?
```

---

# Phase 7 - Source Discovery

Language-specific source patterns can identify potentially attacker-controlled input.

Examples:

## Java

```bash
rg -n \
'getParameter|getHeader|getCookies|getInputStream|getReader|@RequestParam|@PathVariable|@RequestBody|@RequestHeader|@CookieValue' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'Request\.Query|Request\.Form|Request\.Headers|Request\.Cookies|RouteData|FromQuery|FromRoute|FromBody|FromHeader' \
-g '*.cs' \
.
```

## PHP

```bash
rg -n \
'\$_GET|\$_POST|\$_REQUEST|\$_COOKIE|\$_FILES|\$_SERVER' \
-g '*.php' \
.
```

## Python

```bash
rg -n \
'request\.args|request\.form|request\.json|request\.files|request\.headers|request\.cookies|request\.GET|request\.POST|request\.FILES' \
-g '*.py' \
.
```

## Node.js

```bash
rg -n \
'req\.query|req\.params|req\.body|req\.headers|req\.cookies' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Phase 8 - Sink Discovery

Once the attack surface and sources are understood, search for dangerous operations.

---

# SQL Injection Candidates

## Java

```bash
rg -n \
'executeQuery|executeUpdate|createNativeQuery|createQuery|JdbcTemplate|PreparedStatement|Statement' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'SqlCommand|FromSqlRaw|ExecuteSqlRaw|SqlQueryRaw|QueryAsync|ExecuteAsync' \
-g '*.cs' \
.
```

## PHP

```bash
rg -n \
'mysqli_query|->query\(|->exec\(|->prepare\(' \
-g '*.php' \
.
```

## Python

```bash
rg -n \
'cursor\.execute|cursor\.executemany|\.raw\(|RawSQL|text\(' \
-g '*.py' \
.
```

## Node.js

```bash
rg -n \
'\.query\(|\.execute\(|\$queryRaw|\$executeRaw' \
-g '*.js' \
-g '*.ts' \
.
```

These are candidate locations.

Parameterized query APIs may be entirely safe.

---

# Command Injection Candidates

## Java

```bash
rg -n \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder|/bin/sh|bash -c|cmd\.exe|powershell' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'Process\.Start|ProcessStartInfo|cmd\.exe|powershell|/bin/sh|bash' \
-g '*.cs' \
.
```

## PHP

```bash
rg -n \
'system\(|exec\(|shell_exec\(|passthru\(|popen\(|proc_open\(' \
-g '*.php' \
.
```

## Python

```bash
rg -n \
'os\.system|subprocess\.(run|Popen|call|check_output|check_call)|shell\s*=\s*True' \
-g '*.py' \
.
```

## Node.js

```bash
rg -n \
'child_process|exec\(|execSync\(|spawn\(|spawnSync\(' \
-g '*.js' \
-g '*.ts' \
.
```

---

# SSRF Candidates

## Java

```bash
rg -n \
'HttpClient|RestTemplate|RestClient|WebClient|URLConnection|openConnection|new URL|URI\.create' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'HttpClient|WebClient|WebRequest|HttpWebRequest' \
-g '*.cs' \
.
```

## Python

```bash
rg -n \
'requests\.(get|post|put|delete|request)|urllib|urlopen|httpx\.' \
-g '*.py' \
.
```

## PHP

```bash
rg -n \
'curl_exec|curl_init|file_get_contents|fopen\(' \
-g '*.php' \
.
```

## Node.js

```bash
rg -n \
'axios|fetch\(|http\.request|https\.request|got\(' \
-g '*.js' \
-g '*.ts' \
.
```

---

# File Operation Candidates

## Java

```bash
rg -n \
'Files\.(read|write)|FileInputStream|FileOutputStream|new File|Paths\.get|Path\.of|\.resolve\(' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'File\.(Open|Read|Write|Delete|Move|Copy)|Path\.Combine|Directory\.' \
-g '*.cs' \
.
```

## PHP

```bash
rg -n \
'file_get_contents|file_put_contents|fopen|readfile|include\(|require\(' \
-g '*.php' \
.
```

## Python

```bash
rg -n \
'open\(|pathlib|send_file|send_from_directory' \
-g '*.py' \
.
```

## Node.js

```bash
rg -n \
'fs\.(readFile|writeFile|createReadStream|createWriteStream|unlink|rename)' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Deserialisation Candidates

## Java

```bash
rg -n \
'ObjectInputStream|readObject\(|readUnshared\(|XMLDecoder|XStream|activateDefaultTyping|enableDefaultTyping|Yaml\(' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'BinaryFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|Deserialize\(' \
-g '*.cs' \
.
```

## PHP

```bash
rg -n \
'unserialize\(' \
-g '*.php' \
.
```

## Python

```bash
rg -n \
'pickle\.loads|pickle\.load|yaml\.load|marshal\.loads' \
-g '*.py' \
.
```

## Node.js

Search application-specific serialisation libraries and unsafe dynamic object reconstruction rather than assuming ordinary `JSON.parse()` is equivalent to native object deserialisation.

---

# XSS Candidates

## Java

```bash
rg -n \
'th:utext|response\.getWriter|PrintWriter|\.write\(|\.print\(' \
-g '*.java' \
-g '*.html' \
-g '*.jsp' \
.
```

## .NET

```bash
rg -n \
'Html\.Raw|WriteLiteral|Response\.Write' \
-g '*.cs' \
-g '*.cshtml' \
.
```

## PHP

```bash
rg -n \
'echo|print|printf' \
-g '*.php' \
.
```

## Browser JavaScript

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|eval\(|new Function' \
-g '*.js' \
-g '*.ts' \
.
```

These searches can produce substantial false positives.

Context is essential.

---

# Open Redirect Candidates

```bash
rg -n \
'redirect\(|RedirectView|sendRedirect|Response\.Redirect|res\.redirect|location\.href|window\.location' \
.
```

Then trace the destination source.

---

# LDAP Injection Candidates

```bash
rg -n \
'LdapTemplate|DirContext|SearchControls|ldap_search|DirectorySearcher|DirectoryEntry' \
.
```

Then inspect how LDAP filters are constructed.

---

# Template Injection Candidates

Search template engines and dynamic expression evaluation.

```bash
rg -ni \
'render_template_string|Template\(|FreeMarker|Velocity|Thymeleaf|SpelExpressionParser|parseExpression|RazorEngine|eval\(' \
.
```

Do not confuse:

```text
Untrusted template data
```

with:

```text
Untrusted template source
```

---

# XXE Candidates

```bash
rg -n \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory|SchemaFactory|XmlDocument|XmlReader|lxml|etree' \
.
```

Parser security depends on:

```text
Parser
Version
Configuration
Runtime
Input trust
```

Do not report XXE from parser presence alone.

---

# Mass Assignment Candidates

Search for direct request-to-domain-object binding.

Examples:

```text
Request body -> Entity
Request body -> Model
Request body -> ORM object
```

Potential keywords:

```bash
rg -ni \
'BeanUtils\.copyProperties|ModelMapper|@ModelAttribute|UpdateModel|TryUpdateModel|Object\.assign|\.update\(req\.body|\.create\(req\.body' \
.
```

Manual analysis is particularly important here.

---

# Secrets Candidates

```bash
rg -ni \
'password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key|client[_-]?secret' \
.
```

Also search likely credential formats where appropriate.

Do not automatically report placeholders, test values or documentation examples.

---

# Security Configuration Discovery

Search:

```bash
rg -ni \
'cors|csrf|csp|content-security-policy|frame-options|sameSite|secureCookie|httponly|allowedOrigins|permitAll|allowAnonymous' \
.
```

This helps identify:

```text
CORS
CSRF
Security headers
Cookie configuration
Authentication exceptions
Authorisation exceptions
```

---

# Dependency Discovery

Search manifests:

```bash
find . -type f \( \
-name 'pom.xml' -o \
-name 'build.gradle' -o \
-name 'build.gradle.kts' -o \
-name '*.csproj' -o \
-name 'composer.json' -o \
-name 'composer.lock' -o \
-name 'requirements.txt' -o \
-name 'pyproject.toml' -o \
-name 'package.json' -o \
-name 'package-lock.json' -o \
-name 'yarn.lock' -o \
-name 'pnpm-lock.yaml' \
\)
```

Dependency analysis is a separate problem from code pattern analysis.

Combine SAST with software composition analysis where appropriate.

---

# Static Analysis by Vulnerability Class

A useful workflow is to perform dedicated passes.

```text
Pass 1
Attack Surface

Pass 2
Authentication

Pass 3
Authorisation

Pass 4
IDOR / BOLA

Pass 5
Input Validation

Pass 6
SQL / NoSQL / LDAP Injection

Pass 7
Command Injection

Pass 8
SSRF

Pass 9
Path Traversal / Files

Pass 10
File Upload

Pass 11
XXE

Pass 12
Deserialisation

Pass 13
SSTI

Pass 14
XSS / HTML Injection

Pass 15
CSRF / CORS

Pass 16
Redirects / Host Handling

Pass 17
Mass Assignment

Pass 18
Business Logic

Pass 19
Race Conditions

Pass 20
Secrets

Pass 21
Dependencies

Pass 22
Cryptography

Pass 23
Logging / Information Disclosure

Pass 24
API Security
```

This is often more systematic than running a scanner once and reviewing whatever it returns.

---

# Static Analysis by Technology

The exact source and sink patterns depend on the application stack.

The language-specific source code review notes contain deeper patterns for:

```text
.NET / ASP.NET Core
Java / Spring
PHP
Python
Django
Flask
Node.js / Express
Client-Side JavaScript
```

Static-analysis rules should be adapted to framework behaviour.

---

# Framework Awareness

Consider:

```text
Framework autoescaping

ORM parameterisation

Authentication middleware

Authorisation annotations

CSRF middleware

CORS middleware

Model binding

Request validation

Session handling

Proxy configuration
```

A generic rule may misunderstand framework protections.

---

# Example - SQL Injection Candidate

Suppose a scanner finds:

```java
String sql =
    "SELECT * FROM users WHERE name = '"
    + name
    + "'";

entityManager.createNativeQuery(sql);
```

The scanner should lead to:

```text
Where does name originate?
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
name
    |
    v
String Concatenation
    |
    v
createNativeQuery()
```

This creates a strong SQL injection candidate.

---

# Example - False Positive

Suppose the scanner finds:

```java
PreparedStatement stmt =
    connection.prepareStatement(
        "SELECT * FROM users WHERE id = ?"
    );

stmt.setLong(1, id);
```

A raw text search may flag:

```text
SELECT
```

and:

```text
prepareStatement
```

Manual review identifies parameter binding.

Result:

```text
Protected
```

---

# Example - SSRF Candidate

```python
url = request.args.get("url")

response = requests.get(url)
```

Flow:

```text
HTTP Parameter
     |
     v
url
     |
     v
requests.get()
```

Now inspect:

```text
URL validation
Host allowlisting
Scheme validation
Redirect behaviour
DNS resolution
Network egress
```

The sink alone does not prove SSRF.

---

# Example - IDOR

Static scanners may struggle with logic such as:

```java
@GetMapping("/documents/{id}")
public Document getDocument(
    @PathVariable Long id
) {
    return repository
        .findById(id)
        .orElseThrow();
}
```

The security question is not primarily:

```text
Is findById dangerous?
```

It is:

```text
Where is ownership or permission checked?
```

This demonstrates why manual review remains essential.

---

# Example - Business Logic

Consider:

```text
POST /coupon/apply

coupon.used = false
      |
      v
Apply Discount
      |
      v
coupon.used = true
```

The code may appear individually safe.

But concurrent requests could potentially interact with the workflow.

This requires reasoning about:

```text
Transactions
Concurrency
Atomicity
Database constraints
```

rather than searching for one dangerous API.

---

# Variant Analysis

One of the highest-value uses of static analysis is finding variants after discovering one real vulnerability.

Workflow:

```text
Confirmed Vulnerability
        |
        v
Identify Root Pattern
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
Search Repository
        |
        v
Find Similar Flows
```

---

# Example Variant Analysis

Suppose a vulnerable helper is discovered:

```java
public void executeReport(
    String command
) {
    Runtime.getRuntime().exec(command);
}
```

Search:

```bash
rg -n \
'executeReport\(' \
.
```

Then:

```text
Find All References
```

in VS Code.

Potential result:

```text
ReportController
AdminController
ExportController
ScheduledReportJob
```

Every caller becomes a candidate.

---

# Turn Findings Into Rules

A powerful long-term workflow is:

```text
Manual Finding
      |
      v
Understand Pattern
      |
      v
Create Search Pattern
      |
      +--> ripgrep
      |
      +--> Semgrep
      |
      +--> OpenGrep
      |
      +--> CodeQL
      |
      v
Scan for Variants
```

This transforms one vulnerability into reusable security knowledge.

---

# Personal Rule Library

A security reviewer can maintain a repository such as:

```text
security-rules/
│
├── java/
│   ├── command-execution.yml
│   ├── unsafe-sql.yml
│   └── ssrf.yml
│
├── dotnet/
│   ├── process-start.yml
│   ├── raw-sql.yml
│   └── unsafe-file-access.yml
│
├── python/
│   ├── shell-true.yml
│   ├── pickle.yml
│   └── unsafe-yaml.yml
│
├── php/
│   ├── command-execution.yml
│   └── unserialize.yml
│
└── javascript/
    ├── child-process.yml
    ├── dom-xss.yml
    └── unsafe-eval.yml
```

The exact rule syntax depends on the analysis engine.

---

# Finding Triage

Static-analysis output should be triaged.

Useful classifications:

```text
Confirmed
Likely
Needs Review
Protected
Not Reachable
False Positive
Informational
```

---

# Triage Priority

A simple prioritisation model:

```text
                 Attacker Control
                      High
                       |
                       v
High Impact Sink -> Highest Priority
                       |
                       v
Missing Control
```

High-priority sinks often include:

```text
Command execution
Raw SQL
Deserialisation
Dynamic code execution
File write
Sensitive file read
Outbound HTTP requests
Authentication decisions
Authorisation decisions
```

---

# Confidence Model

For each result consider:

```text
Source Confidence
Sink Confidence
Flow Confidence
Control Confidence
Impact Confidence
```

Example:

```text
Source Confidence: High
Sink Confidence: High
Flow Confidence: High
Control Confidence: Medium
Impact Confidence: High
```

The remaining work is obvious:

```text
Investigate security control.
```

---

# Dynamic Validation

Where authorised and appropriate:

```text
Static Candidate
      |
      v
Identify Endpoint
      |
      v
Run Application
      |
      v
Burp Suite
      |
      v
Controlled Test
      |
      v
Observe Behaviour
```

Dynamic validation can help confirm assumptions made during static analysis.

---

# Static Analysis + Burp Suite

Example:

```text
Semgrep / OpenGrep / CodeQL
          |
          v
Potential SSRF
          |
          v
VS Code
          |
          v
Find Controller
          |
          v
/api/import?url=
          |
          v
Burp Repeater
          |
          v
Controlled Validation
```

This creates a strong white-box testing workflow.

---

# Static Analysis + Debugger

When source and a test environment are available:

```text
Request
  |
  v
Breakpoint
  |
  v
Inspect Variable
  |
  v
Continue
  |
  v
Breakpoint at Sink
```

This can directly confirm the runtime data flow.

---

# Static Analysis + Git

Git is useful for understanding:

```text
When code was introduced

What changed

Whether security controls were removed

Whether a vulnerability has variants

Whether secrets existed historically
```

Useful commands:

```bash
git log --oneline --all
```

```bash
git diff
```

```bash
git blame path/to/file
```

```bash
git log -S 'dangerousFunction' -p
```

---

# Diff-Based Static Analysis

When reviewing a pull request or release:

```text
Changed Code
    |
    v
New Sources?
    |
    v
New Sinks?
    |
    v
Changed Security Controls?
    |
    v
Changed Dependencies?
```

Start with:

```bash
git diff --name-only main..feature
```

Then:

```bash
git diff main..feature
```

Prioritise:

```text
Authentication
Authorisation
Input handling
Database queries
Command execution
File handling
Network requests
Dependencies
Configuration
```

---

# Baseline vs Diff Review

```text
Baseline Review
      |
      +--> Entire application

Diff Review
      |
      +--> Changed code

Hybrid Review
      |
      +--> Understand baseline
      |
      +--> Deep review changes
```

---

# CI/CD Integration

Static analysis can also run automatically.

Conceptually:

```text
Developer Commit
      |
      v
Pull Request
      |
      v
CI Pipeline
      |
      +--> Semgrep
      |
      +--> OpenGrep
      |
      +--> CodeQL
      |
      +--> Dependency Scan
      |
      +--> Secret Scan
      |
      v
Security Results
```

Do not configure CI to blindly block every scanner match.

Poorly tuned rules can create:

```text
False positives
Alert fatigue
Developer bypass behaviour
Ignored security results
```

Rule quality matters.

---

# SARIF

Static Analysis Results Interchange Format, or SARIF, is commonly used to represent static-analysis findings.

Where a tool and workflow support SARIF, it can help integrate findings with:

```text
CI systems
Code scanning interfaces
Security dashboards
IDE workflows
```

Verify the exact output support and CLI options for the installed version of each tool.

---

# Scanner Output Preservation

During an assessment, preserve:

```text
Tool name
Tool version
Command
Rule set
Repository commit
Branch
Timestamp
Output
```

Example:

```text
Tool:
OpenGrep

Version:
<record installed version>

Repository:
example-app

Commit:
abc123...

Rules:
custom/java-security/

Command:
<record exact command>

Result:
scanner-output.json
```

This makes results reproducible.

---

# Reproducibility

A static-analysis result should ideally be reproducible against:

```text
Same repository commit
Same rules
Same tool version
Same configuration
```

Record:

```bash
git rev-parse HEAD
```

Also record tool versions.

---

# Do Not Scan the Wrong Revision

Before beginning:

```bash
git status
```

```bash
git branch --show-current
```

```bash
git rev-parse HEAD
```

The reviewed source must correspond to the intended assessment target.

---

# Generated Code

Generated code can create noise.

Examples:

```text
Generated API clients
ORM models
Bundled JavaScript
Build output
Protocol buffers
Vendor libraries
Minified files
```

Determine whether generated code should be:

```text
Excluded

Reviewed selectively

Reviewed through its source generator/configuration
```

Do not blindly exclude code merely because it is generated if it forms part of a meaningful security boundary.

---

# Vendored Dependencies

Vendored code may be relevant when:

```text
Application modifies the dependency

Dependency is directly deployed

Security behaviour depends on it

No package manager metadata exists
```

Otherwise dependency scanning may be more efficient than running every application rule against third-party code.

---

# Test Code

Do not automatically exclude tests.

Tests may reveal:

```text
Hidden endpoints
Test credentials
Authentication assumptions
Authorisation expectations
Security feature flags
Business logic
Example payloads
Internal API usage
```

But findings affecting only non-production test code should be classified appropriately.

---

# Configuration Files

Static review must include configuration.

Examples:

```text
application.yml
application.properties
appsettings.json
settings.py
.env
Dockerfile
docker-compose.yml
nginx.conf
Kubernetes manifests
Terraform
CI/CD workflows
```

Security behaviour can change dramatically based on configuration.

---

# Deployment Context

Static analysis alone may not reveal:

```text
Reverse proxy protections
API gateway policies
WAF controls
Cloud IAM
Network egress controls
Rate limiting
TLS termination
Secret injection
Runtime environment
```

Therefore avoid conclusions such as:

```text
No application rate-limit code exists,
therefore the endpoint has no rate limiting.
```

The control may exist elsewhere.

---

# HTTP Request Smuggling

Application source can reveal:

```text
Custom HTTP parsing
Header handling
Proxy assumptions
Content-Length logic
Transfer-Encoding handling
Framework/server versions
```

But HTTP request smuggling frequently depends on the complete chain:

```text
Client
  |
  v
CDN
  |
  v
Reverse Proxy
  |
  v
Load Balancer
  |
  v
Application Server
```

Do not report request smuggling based solely on an application code pattern without understanding the HTTP processing chain.

---

# Cache Security

Static analysis can identify:

```text
Cache key construction
@Cacheable
Redis usage
Memory caches
HTTP cache headers
```

Ask:

```text
Does the cache key include user identity?

Does it include tenant?

Does it include authorisation context?

Can private responses become shared?
```

---

# Security Headers

Static analysis can identify header configuration.

Search:

```bash
rg -ni \
'Content-Security-Policy|X-Frame-Options|Strict-Transport-Security|Referrer-Policy|Permissions-Policy|X-Content-Type-Options' \
.
```

Missing configuration in source code does not prove headers are absent in production.

Headers may be applied by:

```text
Reverse proxy
CDN
API gateway
Web server
Platform
```

---

# CORS

Search:

```bash
rg -ni \
'cors|allowedOrigins|allowedOriginPatterns|Access-Control-Allow-Origin|credentials' \
.
```

Then analyse:

```text
Allowed origins
Credentials
Methods
Headers
Dynamic origin reflection
Deployment context
```

Do not report CORS simply because:

```text
*
```

appears somewhere in source.

Determine the actual response behaviour and credential model.

---

# CSRF

Static analysis should identify:

```text
CSRF middleware
CSRF exclusions
Disabled CSRF
Ignored routes
Cookie authentication
Bearer-token authentication
```

CSRF risk depends heavily on how credentials are automatically attached to requests.

For example, a stateless API using an `Authorization: Bearer` token supplied explicitly by client-side code has a different CSRF threat model from a browser application authenticated by cookies.

---

# Authentication and Authorisation Rules

Custom rules are particularly useful for detecting:

```text
Anonymous endpoints
permitAll()
AllowAnonymous
Missing security decorators
Administrative handlers
Object lookup without obvious ownership checks
```

However, access control is highly contextual.

Automated rules should be treated as prioritisation mechanisms.

---

# Security-Sensitive Internal APIs

One of the best uses of custom rules is detecting application-specific dangerous functions.

Example:

```text
Internal helper:

CommandRunner.execute()
```

or:

```text
ReportService.renderUnsafeTemplate()
```

or:

```text
HttpHelper.fetchRemoteResource()
```

Once discovered:

```text
Create Rule
    |
    v
Find Every Caller
    |
    v
Review Input
```

This can outperform generic vulnerability rules during targeted source review.

---

# Custom Rule Development Workflow

```text
1. Find interesting security pattern manually

2. Identify the minimum vulnerable code pattern

3. Identify safe variants

4. Create test cases

5. Write rule

6. Run rule against test cases

7. Run against repository

8. Triage matches

9. Reduce false positives

10. Add rule to rule library
```

---

# Rule Test Cases

For every custom rule, ideally maintain:

```text
rule-name/
│
├── rule.yml
│
├── vulnerable-example.*
└── safe-example.*
```

This makes rule behaviour easier to maintain.

---

# Rule Quality

A useful rule should balance:

```text
Recall
```

and:

```text
Precision
```

High recall:

```text
Find as many real candidates as possible.
```

High precision:

```text
Avoid irrelevant matches.
```

During manual penetration testing, somewhat lower precision may be acceptable because a human is triaging the results.

In large CI environments, excessive false positives become much more expensive.

---

# Scanner Chaining

The tools can be used together.

Example:

```text
ripgrep
   |
   v
Find custom dangerous function
   |
   v
OpenGrep / Semgrep
   |
   v
Find structural variants
   |
   v
CodeQL
   |
   v
Investigate deeper data flows
```

Another workflow:

```text
CodeQL Finding
     |
     v
Understand Vulnerable Pattern
     |
     v
Create Lightweight OpenGrep Rule
     |
     v
Use During Future Assessments
```

---

# Tool Selection

A simple decision model:

```text
Need to find text quickly?
        |
       Yes
        |
        v
     ripgrep
```

```text
Need syntax-aware pattern matching?
        |
       Yes
        |
        v
Semgrep / OpenGrep
```

```text
Need custom reusable security rules?
        |
       Yes
        |
        v
Semgrep / OpenGrep
```

```text
Need deeper semantic data flow?
        |
       Yes
        |
        v
      CodeQL
```

```text
Need business logic understanding?
        |
       Yes
        |
        v
   Manual Review
```

---

# Practical Assessment Workflow

For an unfamiliar repository:

```text
1. Open repository in VS Code

2. Identify languages

3. Identify frameworks

4. Identify configuration

5. Map routes

6. Map authentication

7. Map authorisation

8. Search user-controlled sources

9. Search dangerous sinks with ripgrep

10. Run Semgrep and/or OpenGrep

11. Triage scanner findings

12. Trace candidates manually

13. Run CodeQL where deeper data-flow analysis is valuable

14. Perform variant analysis

15. Dynamically validate high-confidence candidates

16. Document confirmed findings
```

---

# Suggested Review Directory

Assessment artefacts can be organised as:

```text
review/
│
├── notes/
│
│   ├── architecture.md
│   ├── routes.md
│   ├── authentication.md
│   ├── authorisation.md
│   └── candidates.md
│
├── ripgrep/
│   ├── routes.txt
│   ├── sql-sinks.txt
│   ├── command-sinks.txt
│   ├── ssrf-sinks.txt
│   └── secrets.txt
│
├── semgrep/
│   └── results/
│
├── opengrep/
│   └── results/
│
├── codeql/
│   └── results/
│
└── findings/
```

Avoid storing sensitive assessment data insecurely.

---

# Candidate Record

Example:

```text
ID:
CAND-001

Type:
Potential SSRF

Source:
GET /api/fetch?url=

Source File:
FetchController.java

Source Variable:
url

Sink:
HttpClient.send()

Flow:
FetchController
    ->
FetchService
    ->
HttpClient.send()

Security Controls:
URLValidator.isAllowed()

Status:
Investigate URLValidator implementation.
```

---

# Scanner Finding Record

Example:

```text
Tool:
OpenGrep

Rule:
custom.java.ssrf-http-client

File:
src/main/java/example/FetchService.java

Line:
84

Candidate:
User-controlled URL may reach outbound HTTP client.

Manual Review:
Required.

Status:
Investigating.
```

---

# Confirmed Finding Record

```text
ID:
FIND-001

Type:
Server-Side Request Forgery

Route:
GET /api/fetch

Source:
url query parameter

Sink:
HttpClient.send()

Data Flow:

HTTP Parameter
      |
      v
FetchController
      |
      v
FetchService
      |
      v
URI.create()
      |
      v
HttpClient.send()

Security Control:
Scheme restricted to HTTP/HTTPS.

Weakness:
No destination host or resolved-address restriction.

Dynamic Validation:
Confirmed in authorised test environment.

Impact:
Application server can be induced to make requests to unintended destinations.
```

---

# Static Analysis Checklist

## Preparation

```text
[ ] Scope confirmed
[ ] Correct repository confirmed
[ ] Correct branch confirmed
[ ] Commit recorded
[ ] Languages identified
[ ] Frameworks identified
[ ] Build system identified
[ ] Generated code identified
[ ] Vendored code identified
```

## Attack Surface

```text
[ ] Routes mapped
[ ] APIs mapped
[ ] GraphQL mapped
[ ] gRPC mapped
[ ] WebSockets mapped
[ ] Webhooks mapped
[ ] File uploads mapped
[ ] Background jobs mapped
[ ] Message consumers mapped
```

## Security Controls

```text
[ ] Authentication located
[ ] Authorisation located
[ ] Validation located
[ ] Session configuration located
[ ] CSRF configuration located
[ ] CORS configuration located
[ ] Security headers located
[ ] Rate limiting considered
```

## Source Discovery

```text
[ ] Query parameters
[ ] Path parameters
[ ] Request bodies
[ ] Headers
[ ] Cookies
[ ] Files
[ ] GraphQL arguments
[ ] WebSocket messages
[ ] gRPC messages
[ ] Queue messages
[ ] Stored untrusted data
```

## Sink Discovery

```text
[ ] SQL
[ ] NoSQL
[ ] LDAP
[ ] Commands
[ ] Files
[ ] Network requests
[ ] Templates
[ ] HTML output
[ ] XML
[ ] Deserialisation
[ ] Dynamic code execution
[ ] Redirects
```

## Tooling

```text
[ ] ripgrep used
[ ] Semgrep considered
[ ] OpenGrep considered
[ ] CodeQL considered
[ ] Dependency scanning considered
[ ] Secret scanning considered
```

## Validation

```text
[ ] Findings manually reviewed
[ ] Sources established
[ ] Sinks established
[ ] Data flow established
[ ] Security controls reviewed
[ ] Framework protections reviewed
[ ] Deployment context considered
[ ] Dynamic validation performed where appropriate
[ ] False positives removed
```

## Variant Analysis

```text
[ ] Similar sinks searched
[ ] Similar sources searched
[ ] Custom helper functions searched
[ ] Find References used
[ ] Call hierarchy reviewed
[ ] Similar routes reviewed
[ ] Alternate entry points reviewed
[ ] Custom rules considered
```

---

# Common Mistakes

## Treating Scanner Output as Findings

Wrong:

```text
Semgrep reported SQL injection.

Therefore SQL injection exists.
```

Better:

```text
Semgrep identified a potential SQL injection data flow.

Manual review is required to determine whether attacker-controlled input reaches the query without effective parameterisation.
```

---

# Running Only One Tool

No single tool provides complete coverage.

```text
ripgrep
```

may find patterns that a rule set does not contain.

```text
Semgrep / OpenGrep
```

may identify structural patterns missed by regex.

```text
CodeQL
```

may identify deeper flows.

```text
Manual review
```

may identify business logic that none of them understand.

---

# Running Every Rule Available

More rules do not automatically mean better testing.

Large generic rule sets can produce:

```text
Noise
Irrelevant findings
Duplicate findings
Low-value warnings
```

Use broad scanning initially if useful, then move toward targeted rules based on:

```text
Technology
Framework
Attack surface
Assessment objectives
Observed patterns
```

---

# Ignoring Safe Variants

When creating custom rules, study both:

```text
Vulnerable code
```

and:

```text
Safe code
```

Otherwise the rule may match every usage of a security-sensitive API.

---

# Ignoring Framework Behaviour

Example:

```text
Output operation detected
```

may be safe because the framework performs context-aware encoding.

Conversely:

```text
Framework has autoescaping
```

does not mean every output path is safe.

Look for bypass mechanisms and alternate output APIs.

---

# Ignoring Custom Security Functions

Applications often contain helpers such as:

```text
validateUrl()
sanitizeInput()
checkPermission()
safeQuery()
verifyToken()
```

These functions are extremely important.

Open them.

Do not infer their behaviour from their names.

---

# Ignoring Second-Order Flows

Example:

```text
HTTP Input
    |
    v
Database
    |
    v
Scheduled Job
    |
    v
ProcessBuilder
```

A request-to-sink scanner may not always identify the complete lifecycle.

Manual review remains important.

---

# Ignoring Business Logic

Static analysis is weakest when the vulnerability depends on understanding:

```text
Money
Roles
Workflow
Ownership
State
Timing
Relationships
Organisation rules
```

These require human reasoning.

---

# Final Static Analysis Model

```text
                         SOURCE REPOSITORY
                                |
                                v
                         IDENTIFY STACK
                                |
                                v
                         MAP ARCHITECTURE
                                |
                                v
                       MAP ATTACK SURFACE
                                |
              +-----------------+-----------------+
              |                 |                 |
              v                 v                 v
          ripgrep           Semgrep           OpenGrep
              |                 |                 |
              +-----------------+-----------------+
                                |
                                v
                         CANDIDATE CODE
                                |
                                v
                        MANUAL VS CODE
                             REVIEW
                                |
                     +----------+----------+
                     |                     |
                     v                     v
               SOURCE -> SINK        SINK -> SOURCE
                     |                     |
                     +----------+----------+
                                |
                                v
                       SECURITY CONTROLS
                                |
                                v
                          EXPLOITABILITY
                                |
                       +--------+--------+
                       |                 |
                       v                 v
                   Protected         Candidate
                                         |
                                         v
                                DYNAMIC VALIDATION
                                         |
                                         v
                                CONFIRMED FINDING
                                         |
                                         v
                                 ROOT PATTERN
                                         |
                                         v
                                  VARIANT ANALYSIS
                                         |
                       +-----------------+----------------+
                       |                 |                |
                       v                 v                v
                    ripgrep        Semgrep/OpenGrep    CodeQL
                       |                 |                |
                       +-----------------+----------------+
                                         |
                                         v
                                  OTHER VARIANTS
```

The objective is therefore not:

```text
Run scanners.
```

It is:

```text
Understand the application.

Use tools to locate security-relevant code.

Trace attacker-controlled data.

Understand security controls.

Determine whether a dangerous operation is reachable.

Validate exploitability.

Find variants.

Report the root cause.
```

---

# Quick Tool Selection

```text
Question:
Where is this function used?

Use:
ripgrep / VS Code Find References
```

```text
Question:
Where does this code pattern appear?

Use:
ripgrep
Semgrep
OpenGrep
```

```text
Question:
Can this source reach this sink?

Use:
Manual tracing
Semgrep/OpenGrep where supported
CodeQL
```

```text
Question:
Are there variants of this vulnerability?

Use:
ripgrep
VS Code references
Semgrep
OpenGrep
CodeQL
```

```text
Question:
Is this business workflow vulnerable?

Use:
Manual review
Dynamic validation
```

---

# Next Notes

Continue with:

```text
docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/semgrep.md
docs/source-code-review/static-analysis/opengrep.md
docs/source-code-review/static-analysis/codeql.md
```

Each note focuses on using the individual tool during practical security source code review.

---

# References

## OWASP Secure Code Review Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html
```

## OWASP Code Review Guide

```text
https://owasp.org/www-project-code-review-guide/
```

## OWASP Application Security Verification Standard

```text
https://owasp.org/www-project-application-security-verification-standard/
```

## OWASP Cheat Sheet Series

```text
https://cheatsheetseries.owasp.org/
```

## Visual Studio Code

```text
https://code.visualstudio.com/docs
```

## ripgrep

```text
https://github.com/BurntSushi/ripgrep
```

## Semgrep Documentation

```text
https://semgrep.dev/docs/
```

## OpenGrep

```text
https://github.com/opengrep/opengrep
```

## OpenGrep Documentation

```text
https://opengrep.dev/
```

## CodeQL Documentation

```text
https://codeql.github.com/docs/
```

## CodeQL Data Flow Analysis

```text
https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/
```

## GitHub Code Scanning

```text
https://docs.github.com/en/code-security/code-scanning
```

## SARIF

```text
https://sarifweb.azurewebsites.net/
```

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/methodology.md

docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/semgrep.md
docs/source-code-review/static-analysis/opengrep.md
docs/source-code-review/static-analysis/codeql.md

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
docs/web/input-validation.md
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
docs/web/http-security-headers.md
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
