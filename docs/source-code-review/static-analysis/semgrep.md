# Semgrep for Security Source Code Review

Semgrep is a static analysis tool that searches source code using syntax-aware patterns rather than relying only on text or regular expressions.

For security source code review, Semgrep is useful for:

```text
Finding dangerous APIs
Finding insecure coding patterns
Finding missing security controls
Tracing selected source-to-sink flows
Finding vulnerability variants
Creating organisation-specific security rules
Scanning multiple languages
Automating repeatable source review
Reducing noise compared with simple grep searches
```

Semgrep fits naturally between manual searching and deeper program analysis:

```text
ripgrep
   |
   v
Fast Text Search
   |
   v
Manual Review
   |
   v
Semgrep
   |
   v
Syntax-Aware Pattern Matching
   |
   v
Taint Analysis
   |
   v
Candidate Vulnerabilities
   |
   v
Manual Validation
```

A useful security workflow is:

```text
Repository
    |
    v
Visual Studio Code
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
Candidate Security-Relevant Code
    |
    v
Manual Source-to-Sink Analysis
    |
    v
Dynamic Validation
    |
    v
Confirmed Finding
```

!!! warning "Authorised Security Testing"
    Use Semgrep only on source code and systems that you are authorised to assess. Static analysis results are candidates for investigation and should not automatically be treated as confirmed vulnerabilities.

---

# Core Principle

The most important rule is:

```text
Semgrep finding
      !=
Confirmed vulnerability
```

Semgrep may identify:

```text
Dangerous function
Potential source
Potential sink
Potential taint flow
Missing pattern
Suspicious configuration
```

The reviewer must still determine:

```text
Is the code reachable?

Can an attacker control the source?

Does the data actually reach the sink?

What transformations occur?

Is validation present?

Is sanitisation appropriate?

Does the framework provide protection?

Does deployment configuration provide protection?

Can the security control be bypassed?

What security impact is possible?
```

The correct model is:

```text
Semgrep Result
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
Exploitability Analysis
      |
      v
Dynamic Validation
      |
      v
Confirmed / Rejected
```

---

# Semgrep vs ripgrep

`ripgrep` searches text.

Semgrep searches source-code structure.

Example Java code:

```java
Runtime
    .getRuntime()
    .exec(command);
```

A simple textual search may need to account for formatting.

Semgrep understands the syntax tree.

Conceptually:

```text
ripgrep

Text
 |
 v
Regex
 |
 v
Match
```

Semgrep:

```text
Source Code
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
Match
```

Both are useful.

---

# Recommended Tool Roles

Use the tools for different purposes:

| Tool | Primary Purpose |
|---|---|
| ripgrep | Extremely fast reconnaissance and text searching |
| Semgrep | Syntax-aware security patterns and taint analysis |
| OpenGrep | Open-source Semgrep-compatible static analysis workflow |
| CodeQL | Deeper semantic and data-flow analysis |
| VS Code | Manual source navigation and validation |
| Burp Suite | Dynamic validation of reachable web vulnerabilities |

A practical workflow is:

```text
ripgrep
   |
   v
Find Interesting Areas
   |
   v
VS Code
   |
   v
Understand Application
   |
   v
Semgrep / OpenGrep
   |
   v
Search Variants
   |
   v
CodeQL
   |
   v
Complex Data Flow
   |
   v
Burp Suite
   |
   v
Dynamic Validation
```

---

# Installation

Always check the current Semgrep documentation for the recommended installation method for your operating system.

A common Python-based installation approach is:

```bash
python3 -m pip install semgrep
```

Verify:

```bash
semgrep --version
```

Help:

```bash
semgrep --help
```

Scan help:

```bash
semgrep scan --help
```

If your environment uses isolated Python tooling, a virtual environment can keep the installation separate from the system Python environment.

Example:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install semgrep
```

Verify:

```bash
semgrep --version
```

---

# Basic Scan

From the repository root:

```bash
semgrep scan --config auto .
```

This can provide a useful initial view, but it should not replace targeted manual review.

For security work, targeted rules are often more valuable than blindly accepting every result from a broad scan.

---

# Scan a Directory

```bash
semgrep scan --config auto ./src
```

---

# Scan a File

```bash
semgrep scan --config auto ./src/app.py
```

---

# Scan with a Local Rule

```bash
semgrep scan \
  --config rules/command-injection.yml \
  .
```

Multiple rule files can be placed in a directory:

```text
rules/
├── command-injection.yml
├── sql-injection.yml
├── ssrf.yml
├── xss.yml
└── secrets.yml
```

Then:

```bash
semgrep scan \
  --config rules/ \
  .
```

---

# Visual Studio Code Workflow

For manual review, Visual Studio Code works well alongside Semgrep.

Open the repository:

```bash
code .
```

Recommended workflow:

```text
Repository
    |
    v
VS Code
    |
    +--> Understand project structure
    |
    +--> Identify framework
    |
    +--> Find routes
    |
    +--> Find authentication
    |
    +--> Find authorisation
    |
    +--> Find input sources
    |
    v
ripgrep
    |
    v
Semgrep
    |
    v
Candidate
    |
    v
VS Code
    |
    +--> Go to Definition
    +--> Find References
    +--> Call Hierarchy
    +--> Type Hierarchy
    |
    v
Trace Source -> Sink
```

Semgrep should support manual review rather than replace it.

---

# Suggested Repository Layout

For repeatable security assessments:

```text
security-review/
├── rules/
│   ├── java/
│   ├── dotnet/
│   ├── php/
│   ├── python/
│   └── javascript/
│
├── output/
│   ├── semgrep.json
│   └── findings.md
│
└── notes/
```

Or keep project-specific rules inside:

```text
.semgrep/
├── command-injection.yml
├── ssrf.yml
├── sql-injection.yml
└── custom-security.yml
```

---

# Anatomy of a Semgrep Rule

A basic rule looks like:

```yaml
rules:
  - id: example-rule
    languages:
      - python
    message: Review this security-sensitive operation
    severity: WARNING
    pattern: dangerous_function(...)
```

Important fields include:

```text
id
languages
message
severity
pattern
```

Depending on the rule, additional constructs can include:

```text
patterns
pattern-either
pattern-inside
pattern-not
pattern-not-inside
pattern-regex
metavariable-regex
metavariable-pattern
focus-metavariable
```

For data-flow rules, Semgrep also supports taint-mode concepts such as:

```text
pattern-sources
pattern-sinks
pattern-sanitizers
pattern-propagators
```

Exact syntax and supported capabilities can evolve, so check the current Semgrep rule documentation when building production rules.

---

# Metavariables

Semgrep metavariables allow parts of code to be captured.

Example:

```yaml
pattern: os.system($CMD)
```

`$CMD` matches the argument passed to `os.system()`.

For:

```python
os.system(user_input)
```

`$CMD` represents:

```text
user_input
```

For:

```python
os.system(command)
```

it represents:

```text
command
```

---

# Ellipsis

Semgrep uses:

```text
...
```

to represent arbitrary code in many structural patterns.

Example:

```yaml
pattern: subprocess.run(...)
```

This can match different argument lists.

---

# Multiple Patterns

Rules can require multiple conditions.

Example structure:

```yaml
patterns:
  - pattern: ...
  - pattern-inside: |
      def $FUNC(...):
          ...
```

This allows rules to focus on a particular context.

---

# Pattern Either

Use `pattern-either` when multiple APIs represent the same security concept.

Example:

```yaml
rules:
  - id: python-command-execution
    languages:
      - python
    message: Review command execution with potentially untrusted input
    severity: WARNING
    pattern-either:
      - pattern: os.system(...)
      - pattern: os.popen(...)
      - pattern: subprocess.Popen(...)
      - pattern: subprocess.run(...)
```

This is a sink-discovery rule.

It does not prove command injection.

---

# Pattern Not

Exclusions can reduce false positives.

Conceptually:

```yaml
patterns:
  - pattern: dangerous(...)
  - pattern-not: known_safe(...)
```

Use exclusions carefully.

An overly broad exclusion can hide real vulnerabilities.

---

# Start with Sink Discovery

One of the easiest ways to use Semgrep during source review is to find dangerous sinks.

Workflow:

```text
Sink Rule
   |
   v
Semgrep Results
   |
   v
Open Candidate
   |
   v
Trace Arguments Backwards
   |
   v
Find Source
   |
   v
Review Validation
```

---

# Python Command Execution Rule

```yaml
rules:
  - id: python-command-execution
    languages:
      - python
    message: Review command execution for attacker-controlled input
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

Run:

```bash
semgrep scan \
  --config rules/python-command-execution.yml \
  .
```

---

# Python shell=True

A higher-interest pattern is:

```yaml
rules:
  - id: python-subprocess-shell-true
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

`shell=True` increases review priority, but still does not prove exploitability.

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

Questions:

```text
Can an attacker control the executable?

Can an attacker control arguments?

Is a shell involved?

Can arguments alter the behaviour of the invoked program?

Is the invoked program itself security-sensitive?
```

---

# PHP Command Execution

```yaml
rules:
  - id: php-command-execution
    languages:
      - php
    message: Review command execution with potentially untrusted input
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

Depending on import style, additional rules may be needed.

Example:

```javascript
const { exec } = require("child_process");

exec(command);
```

A rule matching only:

```text
child_process.exec(...)
```

may not represent every code style.

This is why repository-specific variant analysis matters.

---

# SQL Injection Review

Semgrep can find query execution and unsafe query construction patterns.

However, SQL injection analysis requires understanding:

```text
Query construction
Parameter binding
ORM behaviour
Dynamic identifiers
Raw SQL
Stored procedures
Database driver behaviour
```

---

# Python SQL Candidate

```yaml
rules:
  - id: python-sql-execution
    languages:
      - python
    message: Review SQL execution and parameter handling
    severity: WARNING
    pattern-either:
      - pattern: $CURSOR.execute(...)
      - pattern: $CURSOR.executemany(...)
```

This intentionally has high recall.

Manual review determines whether parameterisation is used.

---

# Django Raw SQL

```yaml
rules:
  - id: django-raw-sql
    languages:
      - python
    message: Review raw SQL construction and parameterisation
    severity: WARNING
    pattern-either:
      - pattern: $MODEL.objects.raw(...)
      - pattern: RawSQL(...)
      - pattern: $CURSOR.execute(...)
      - pattern: $QUERYSET.extra(...)
```

Not every use is vulnerable.

---

# Java SQL Review

```yaml
rules:
  - id: java-sql-sensitive-api
    languages:
      - java
    message: Review SQL construction and parameter binding
    severity: WARNING
    pattern-either:
      - pattern: $CONN.createStatement(...)
      - pattern: $STMT.executeQuery(...)
      - pattern: $STMT.executeUpdate(...)
      - pattern: $EM.createNativeQuery(...)
      - pattern: $EM.createQuery(...)
```

This rule is intentionally broad.

---

# .NET SQL Review

Example:

```yaml
rules:
  - id: dotnet-raw-sql-review
    languages:
      - csharp
    message: Review raw SQL construction and parameterisation
    severity: WARNING
    pattern-either:
      - pattern: $DB.Database.ExecuteSqlRaw(...)
      - pattern: $DB.Database.FromSqlRaw(...)
      - pattern: new SqlCommand(...)
```

Framework versions and API usage matter.

---

# PHP SQL Review

```yaml
rules:
  - id: php-sql-review
    languages:
      - php
    message: Review SQL query construction and parameterisation
    severity: WARNING
    pattern-either:
      - pattern: mysqli_query(...)
      - pattern: $DB->query(...)
      - pattern: $DB->exec(...)
      - pattern: $DB->prepare(...)
```

`prepare()` is normally an indicator that parameterisation may be used.

Do not flag it as SQL injection merely because it appears.

---

# SSRF Sink Discovery

---

# Python

```yaml
rules:
  - id: python-http-request
    languages:
      - python
    message: Review outbound HTTP request for attacker-controlled destination
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
  - id: java-http-client-review
    languages:
      - java
    message: Review outbound request destination for SSRF
    severity: WARNING
    pattern-either:
      - pattern: new URL(...)
      - pattern: URI.create(...)
      - pattern: $REST.getForObject(...)
      - pattern: $REST.getForEntity(...)
      - pattern: $CLIENT.send(...)
```

This is reconnaissance, not proof of SSRF.

---

# .NET

```yaml
rules:
  - id: dotnet-http-client-review
    languages:
      - csharp
    message: Review outbound request destination for SSRF
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
  - id: php-outbound-request-review
    languages:
      - php
    message: Review outbound request destination for SSRF
    severity: WARNING
    pattern-either:
      - pattern: curl_init(...)
      - pattern: file_get_contents(...)
      - pattern: fopen(...)
```

Some of these APIs also perform local file operations.

Context determines relevance.

---

# Node.js

```yaml
rules:
  - id: node-http-request-review
    languages:
      - javascript
      - typescript
    message: Review outbound request destination for SSRF
    severity: WARNING
    pattern-either:
      - pattern: fetch(...)
      - pattern: axios.get(...)
      - pattern: axios.post(...)
      - pattern: axios.request(...)
```

---

# Path Traversal Sink Discovery

---

# Python

```yaml
rules:
  - id: python-file-access
    languages:
      - python
    message: Review filesystem path for attacker-controlled components
    severity: WARNING
    pattern-either:
      - pattern: open(...)
      - pattern: pathlib.Path(...)
```

This is intentionally broad and likely noisy.

---

# Java

```yaml
rules:
  - id: java-file-access
    languages:
      - java
    message: Review filesystem path construction
    severity: WARNING
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
    message: Review filesystem path construction and containment
    severity: WARNING
    pattern-either:
      - pattern: File.Open(...)
      - pattern: File.ReadAllText(...)
      - pattern: File.ReadAllBytes(...)
      - pattern: File.WriteAllText(...)
      - pattern: File.WriteAllBytes(...)
      - pattern: Path.Combine(...)
```

`Path.Combine()` is not inherently dangerous.

The rule identifies paths that deserve tracing.

---

# Node.js

```yaml
rules:
  - id: node-file-access
    languages:
      - javascript
      - typescript
    message: Review filesystem path construction
    severity: WARNING
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

Semgrep can locate upload handlers.

Python:

```yaml
rules:
  - id: python-file-upload-review
    languages:
      - python
    message: Review uploaded filename, content, destination and downstream processing
    severity: WARNING
    pattern-either:
      - pattern: request.files[...]
      - pattern: request.FILES[...]
```

Java:

```yaml
rules:
  - id: java-file-upload-review
    languages:
      - java
    message: Review uploaded filename and storage controls
    severity: WARNING
    pattern-either:
      - pattern: $FILE.getOriginalFilename()
      - pattern: $FILE.transferTo(...)
```

Node.js:

```yaml
rules:
  - id: node-file-upload-review
    languages:
      - javascript
      - typescript
    message: Review uploaded file validation and storage
    severity: WARNING
    pattern-either:
      - pattern: req.file
      - pattern: req.files
```

---

# Deserialisation Review

---

# Java

```yaml
rules:
  - id: java-deserialization-review
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

# Python

```yaml
rules:
  - id: python-deserialization-review
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

Be careful with YAML analysis.

The security behaviour depends on the YAML library and loader configuration.

---

# PHP

```yaml
rules:
  - id: php-unserialize-review
    languages:
      - php
    message: Review unserialize() input trust boundary
    severity: WARNING
    pattern: unserialize(...)
```

---

# .NET

```yaml
rules:
  - id: dotnet-deserialization-review
    languages:
      - csharp
    message: Review deserialisation trust boundary and serializer configuration
    severity: WARNING
    pattern-either:
      - pattern: $F.Deserialize(...)
      - pattern: new BinaryFormatter(...)
      - pattern: new NetDataContractSerializer(...)
```

This will require manual triage because `Deserialize()` is a broad method name.

---

# XSS Sink Discovery

---

# Browser JavaScript

```yaml
rules:
  - id: javascript-html-sink
    languages:
      - javascript
      - typescript
    message: Review HTML sink for attacker-controlled data
    severity: WARNING
    pattern-either:
      - pattern: $EL.innerHTML = $VALUE
      - pattern: $EL.outerHTML = $VALUE
      - pattern: $EL.insertAdjacentHTML(...)
      - pattern: document.write(...)
      - pattern: document.writeln(...)
```

---

# React

```yaml
rules:
  - id: react-dangerously-set-inner-html
    languages:
      - javascript
      - typescript
    message: Review raw HTML rendering
    severity: WARNING
    pattern: |
      <$ELEMENT dangerouslySetInnerHTML={...} />
```

React normally escapes text rendered through JSX expressions.

`dangerouslySetInnerHTML` intentionally bypasses normal text escaping and deserves review.

It is not automatically exploitable if the value is trusted or correctly sanitised.

---

# Vue

A review should search for:

```text
v-html
```

Because `.vue` single-file components may require different parser support or search strategies depending on tooling and Semgrep version, verify current language support before relying exclusively on a Semgrep rule.

`ripgrep` remains useful:

```bash
rg -n 'v-html' \
  -g '*.vue' \
  .
```

---

# Angular

Interesting Angular patterns include:

```text
[innerHTML]
DomSanitizer
bypassSecurityTrustHtml
bypassSecurityTrustScript
bypassSecurityTrustUrl
bypassSecurityTrustResourceUrl
```

Use `ripgrep` alongside Semgrep:

```bash
rg -n \
'bypassSecurityTrust(Html|Script|Url|ResourceUrl)|\[innerHTML\]' \
-g '*.ts' \
-g '*.html' \
.
```

Bypass APIs intentionally bypass Angular security handling and therefore deserve careful review.

Their presence alone does not prove XSS.

---

# Open Redirect Review

JavaScript:

```yaml
rules:
  - id: javascript-navigation-sink
    languages:
      - javascript
      - typescript
    message: Review attacker influence over navigation destination
    severity: WARNING
    pattern-either:
      - pattern: location.href = $URL
      - pattern: window.location = $URL
      - pattern: location.assign($URL)
      - pattern: location.replace($URL)
      - pattern: window.open($URL, ...)
```

---

# Dynamic Code Execution

JavaScript:

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

Python:

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

# Authentication Review

Static analysis can identify authentication-sensitive APIs and configuration.

Java / Spring:

```yaml
rules:
  - id: spring-security-config-review
    languages:
      - java
    message: Review Spring Security configuration
    severity: INFO
    pattern-either:
      - pattern: $HTTP.authorizeHttpRequests(...)
      - pattern: $HTTP.csrf(...)
      - pattern: $HTTP.oauth2Login(...)
      - pattern: $HTTP.oauth2ResourceServer(...)
      - pattern: $HTTP.saml2Login(...)
```

This is primarily navigation assistance.

---

# Spring permitAll

A simple candidate rule:

```yaml
rules:
  - id: spring-permit-all-review
    languages:
      - java
    message: Review which routes are intentionally publicly accessible
    severity: INFO
    pattern: $X.permitAll()
```

Never report:

```text
permitAll() found
```

as an access-control vulnerability without determining which request matchers it affects.

---

# .NET AllowAnonymous

```yaml
rules:
  - id: dotnet-allow-anonymous-review
    languages:
      - csharp
    message: Review anonymous endpoint exposure
    severity: INFO
    pattern: |
      [AllowAnonymous]
      $DECL
```

Depending on syntax and declaration type, additional rule variants may be needed.

---

# Django csrf_exempt

```yaml
rules:
  - id: django-csrf-exempt-review
    languages:
      - python
    message: Review why CSRF protection is disabled for this view
    severity: WARNING
    pattern: |
      @csrf_exempt
      def $FUNC(...):
          ...
```

`csrf_exempt` does not automatically mean CSRF is exploitable.

Review:

```text
Authentication mechanism
HTTP methods
Endpoint behaviour
Custom token validation
API design
```

---

# Flask Debug Mode

```yaml
rules:
  - id: flask-debug-mode
    languages:
      - python
    message: Review Flask debug mode configuration
    severity: WARNING
    pattern: $APP.run(..., debug=True, ...)
```

Deployment configuration still matters.

---

# Express Proxy Trust

```yaml
rules:
  - id: express-trust-proxy-review
    languages:
      - javascript
      - typescript
    message: Review Express proxy trust configuration
    severity: INFO
    pattern: $APP.set("trust proxy", ...)
```

Proxy trust can affect:

```text
Client IP
Protocol
Host
Secure cookies
Rate limiting
Absolute URLs
```

---

# CORS Review

Node.js:

```yaml
rules:
  - id: express-cors-review
    languages:
      - javascript
      - typescript
    message: Review CORS configuration
    severity: INFO
    pattern: $APP.use(cors(...))
```

CORS vulnerabilities generally require understanding the actual server response configuration and credential model.

A source-code match alone is insufficient.

---

# CSRF Review

Search framework-specific CSRF disable or exemption patterns.

The correct question is:

```text
Does the application use browser-managed credentials for a state-changing request?

If so, what server-side CSRF protection exists?
```

Do not assume:

```text
No CSRF library
    =
CSRF vulnerability
```

---

# JWT Review

Static analysis can locate JWT handling.

Python:

```yaml
rules:
  - id: python-jwt-review
    languages:
      - python
    message: Review JWT validation configuration
    severity: INFO
    pattern-either:
      - pattern: jwt.decode(...)
      - pattern: jwt.encode(...)
```

Node.js:

```yaml
rules:
  - id: node-jwt-review
    languages:
      - javascript
      - typescript
    message: Review JWT verification and claim validation
    severity: INFO
    pattern-either:
      - pattern: jwt.verify(...)
      - pattern: jwt.decode(...)
      - pattern: jwt.sign(...)
```

Important distinction:

```text
Decode
   !=
Verify
```

But library behaviour and application logic must be reviewed before reaching a conclusion.

---

# Password Reset Discovery

Semgrep can be used to locate functions named around reset functionality, but text search is often more efficient:

```bash
rg -ni \
'forgot.?password|reset.?password|password.?reset|reset.?token|recovery' \
.
```

Then use Semgrep for specific security-sensitive APIs discovered inside the flow.

---

# Secrets

Semgrep can identify hardcoded credential patterns, but dedicated secret-scanning tools are usually more appropriate for broad secret detection.

Use:

```text
Semgrep
TruffleHog
Git history analysis
Repository search
```

as complementary techniques.

Do not report every variable named:

```text
password
token
secret
```

as a hardcoded secret.

---

# Taint Analysis

Pattern matching answers:

```text
Does this code contain a dangerous construct?
```

Taint analysis asks:

```text
Can data from a source reach a sink?
```

Conceptually:

```text
SOURCE
  |
  v
User Input
  |
  v
Transformation
  |
  v
Function Call
  |
  v
SINK
```

This is much closer to how security vulnerabilities are actually discovered.

---

# Taint Rule Structure

A conceptual Semgrep taint rule looks like:

```yaml
rules:
  - id: example-taint-rule
    languages:
      - python
    message: Potential source-to-sink flow
    severity: WARNING
    mode: taint

    pattern-sources:
      - pattern: source(...)

    pattern-sinks:
      - pattern: sink(...)
```

Optionally:

```yaml
pattern-sanitizers:
  - pattern: sanitize(...)
```

The exact semantics of taint propagation, sanitizers and advanced taint options should be checked against the current Semgrep documentation.

---

# Flask Command Injection Taint Example

A useful educational example:

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

Example vulnerable code:

```python
from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/ping")
def ping():
    host = request.args.get("host")
    os.system("ping -c 1 " + host)
    return "done"
```

Flow:

```text
request.args.get("host")
          |
          v
         host
          |
          v
String Concatenation
          |
          v
os.system()
```

This is significantly more useful than merely finding every `os.system()` call.

---

# Flask SSRF Taint Example

```yaml
rules:
  - id: flask-request-to-requests
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

This identifies possible SSRF flows.

It does not determine whether the application has effective URL validation.

---

# Django SQL Injection Taint Concept

Conceptually:

```text
request.GET
    |
    v
User Input
    |
    v
String Construction
    |
    v
cursor.execute()
```

A project-specific taint rule can model:

```text
Django request sources
        ->
Raw SQL sinks
```

But be careful to distinguish:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    [user_id]
)
```

from unsafe string construction.

---

# Java Spring Taint Model

Useful Spring sources include:

```text
@RequestParam
@PathVariable
@RequestBody
@RequestHeader
@CookieValue
HttpServletRequest.getParameter()
HttpServletRequest.getHeader()
```

Useful sinks include:

```text
Runtime.exec()
ProcessBuilder
createNativeQuery()
HTTP clients
File operations
Expression parsers
```

Conceptually:

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
Helper
     |
     v
Sink
```

Complex interprocedural flows may require more advanced static analysis or CodeQL.

---

# JavaScript DOM XSS Taint Model

Source:

```javascript
const value =
    new URLSearchParams(location.search)
        .get("name");
```

Sink:

```javascript
output.innerHTML = value;
```

Flow:

```text
location.search
      |
      v
URLSearchParams
      |
      v
value
      |
      v
innerHTML
```

A Semgrep taint rule can model browser sources and DOM sinks.

However, exploitability can depend on:

```text
Sanitisation
Trusted Types
CSP
Framework handling
Browser parsing
Output context
```

---

# Sanitizers

A taint rule can model sanitization.

Conceptually:

```yaml
pattern-sanitizers:
  - pattern: DOMPurify.sanitize(...)
```

But do not casually mark any function called:

```text
sanitize()
```

as a sanitizer.

You must understand what the function actually guarantees.

For example:

```text
HTML sanitisation
    !=
SQL parameterisation

URL validation
    !=
Shell escaping

HTML encoding
    !=
JavaScript string encoding
```

Sanitization is context-specific.

---

# Custom Security Helpers

One of the strongest uses of Semgrep is modelling application-specific functions.

Suppose the application contains:

```java
public void runSystemTask(
    String command
) {
    Runtime.getRuntime().exec(command);
}
```

After confirming the helper is dangerous, create a rule:

```yaml
rules:
  - id: application-run-system-task
    languages:
      - java
    message: Review use of custom command execution helper
    severity: ERROR
    pattern: runSystemTask(...)
```

Now scan the repository:

```bash
semgrep scan \
  --config rules/application-run-system-task.yml \
  .
```

This performs variant analysis.

---

# Variant Analysis

Variant analysis means:

```text
Confirmed Vulnerability
        |
        v
Identify Root Pattern
        |
        v
Search Similar Code
        |
        v
Find Additional Instances
```

Example:

```text
Confirmed SQL Injection
        |
        v
Unsafe Repository Helper
        |
        v
Semgrep Rule
        |
        v
Find Every Similar Query
```

This is often much more valuable than running generic rules.

---

# Variant Analysis Workflow

```text
1. Find one real vulnerability manually

2. Understand why it is vulnerable

3. Identify the structural pattern

4. Write a Semgrep rule

5. Test the rule against the confirmed instance

6. Scan the entire repository

7. Triage matches

8. Refine the rule

9. Search sibling repositories if authorised

10. Convert complex cases to CodeQL if necessary
```

---

# Example Variant Rule

Suppose this pattern is confirmed unsafe:

```python
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
```

A first-pass structural search could target string concatenation passed to SQL execution.

The exact rule should be tested against the application's coding style.

Do not immediately generalise one code example into a production rule without testing false positives and false negatives.

---

# Pattern Testing

Create a test file:

```text
tests/command-injection.py
```

Example:

```python
import os
import subprocess

def unsafe(value):
    os.system(value)

def candidate(value):
    subprocess.run(value, shell=True)

def safer_fixed():
    subprocess.run(
        ["/usr/bin/id"],
        shell=False
    )
```

Run:

```bash
semgrep scan \
  --config rules/python-command-execution.yml \
  tests/
```

Check:

```text
Did the expected vulnerable patterns match?

Did safe patterns unexpectedly match?

Did alternate syntax evade the rule?
```

---

# Rule Development Loop

```text
Write Rule
   |
   v
Run Against Test Code
   |
   v
Expected Match?
   |
   +--> No -> Fix Rule
   |
   v
Run Against Repository
   |
   v
Too Much Noise?
   |
   +--> Yes -> Refine Rule
   |
   v
Missing Variants?
   |
   +--> Yes -> Expand Rule
   |
   v
Stable Rule
```

---

# Rule Naming

Use descriptive IDs.

Good:

```text
java-user-input-to-processbuilder
django-request-to-raw-sql
flask-request-to-requests
node-user-input-to-child-process
javascript-location-to-innerhtml
```

Poor:

```text
rule1
bad-code
security-test
```

---

# Severity

Semgrep supports severity levels in rule definitions.

Use severity to communicate triage priority, not to claim confirmed business impact.

For example:

```yaml
severity: INFO
```

for:

```text
Security configuration discovery
Sensitive API inventory
```

Use:

```yaml
severity: WARNING
```

for:

```text
Security-sensitive candidate requiring review
```

Use:

```yaml
severity: ERROR
```

for stronger patterns where the rule is designed to identify likely vulnerabilities.

Even then:

```text
ERROR
   !=
Confirmed exploitable vulnerability
```

---

# Metadata

Rules can contain metadata useful for larger rule repositories.

Conceptually:

```yaml
metadata:
  category: security
  technology:
    - flask
  vulnerability:
    - command-injection
```

You can also maintain internal mappings such as:

```text
OWASP category
CWE
Technology
Review owner
Rule confidence
```

Use metadata consistently.

---

# Rule Repository Structure

Recommended:

```text
rules/
│
├── common/
│   ├── secrets.yml
│   └── crypto.yml
│
├── java/
│   ├── command-injection.yml
│   ├── sql-injection.yml
│   ├── ssrf.yml
│   ├── deserialization.yml
│   └── spring-security.yml
│
├── dotnet/
│   ├── command-injection.yml
│   ├── sql-injection.yml
│   ├── ssrf.yml
│   └── deserialization.yml
│
├── php/
│   ├── command-injection.yml
│   ├── sql-injection.yml
│   ├── file-inclusion.yml
│   └── deserialization.yml
│
├── python/
│   ├── command-injection.yml
│   ├── sql-injection.yml
│   ├── ssrf.yml
│   └── deserialization.yml
│
├── django/
│   ├── raw-sql.yml
│   ├── csrf.yml
│   └── redirects.yml
│
├── flask/
│   ├── command-injection.yml
│   ├── ssrf.yml
│   └── debug.yml
│
└── javascript/
    ├── dom-xss.yml
    ├── open-redirect.yml
    ├── dynamic-code.yml
    ├── prototype-pollution.yml
    └── node-command-injection.yml
```

---

# Security Rule Categories

A useful rule taxonomy is:

```text
rules/
│
├── attack-surface/
├── authentication/
├── authorisation/
├── injection/
├── server-side/
├── client-side/
├── identity/
├── api/
├── secrets/
├── cryptography/
├── configuration/
├── business-logic/
└── supply-chain/
```

---

# Java Review Strategy

For Java / Spring applications, prioritise:

```text
Routes
Request sources
Spring Security
Method security
SQL/JPA
Command execution
SSRF
Filesystem access
Uploads
XML parsing
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
Background jobs
```

Recommended workflow:

```text
ripgrep route inventory
        |
        v
Semgrep sensitive APIs
        |
        v
Spring Security review
        |
        v
Source-to-sink analysis
        |
        v
Variant rules
```

---

# .NET Review Strategy

Prioritise:

```text
Controllers
Minimal APIs
Authentication middleware
Authorisation attributes
Entity Framework
Raw SQL
Process.Start
HttpClient
File operations
XML
Deserialisation
Razor raw output
JWT
OAuth/OIDC
SignalR
gRPC
Background services
```

---

# PHP Review Strategy

Prioritise:

```text
Routes
Superglobals
SQL
Command execution
File inclusion
File access
Uploads
unserialize()
Template rendering
Redirects
SSRF
Session handling
Authentication
Authorisation
```

PHP benefits from combining:

```text
ripgrep
+
Semgrep
+
Manual review
```

because many security-sensitive operations are concise and easy to search.

---

# Python Review Strategy

Prioritise:

```text
Request input
SQL execution
subprocess
os.system
HTTP clients
File operations
pickle
YAML
XML
Template construction
Dynamic execution
Secrets
```

---

# Django Review Strategy

Prioritise:

```text
urls.py
Views
DRF ViewSets
Serializers
Authentication classes
Permission classes
Raw SQL
Mass assignment
File uploads
Redirects
CSRF exemptions
Template safety
Settings
```

Django's ORM and template system provide important protections, but these can be bypassed by raw APIs or unsafe output handling.

---

# Flask Review Strategy

Prioritise:

```text
@app.route
Blueprint routes
request.args
request.form
request.json
request.files
SQL
subprocess
requests/httpx
render_template_string
send_file
redirect
session
SECRET_KEY
debug mode
CSRF
Custom authentication
Custom authorisation
```

---

# Node.js Review Strategy

Prioritise:

```text
Express routes
req.query
req.params
req.body
Authentication middleware
Authorisation middleware
SQL/NoSQL
child_process
HTTP clients
Filesystem
Template engines
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

# Browser JavaScript Review Strategy

Prioritise:

```text
location
URL parameters
Fragments
postMessage
Storage
API responses
DOM sinks
Dynamic execution
Navigation
Dynamic script loading
Prototype pollution
Client-side authentication assumptions
Client-side authorisation assumptions
Tokens
Source maps
Third-party JavaScript
```

---

# DOM XSS Sources

Useful sources include:

```text
location
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
```

Useful sinks include:

```text
innerHTML
outerHTML
insertAdjacentHTML()
document.write()
document.writeln()
eval()
Function()
location
window.open()
script.src
iframe.srcdoc
```

Semgrep can model selected flows.

Manual browser validation is still important.

---

# postMessage Review

Interesting source:

```javascript
window.addEventListener(
    "message",
    function(event) {
        // event.data
    }
);
```

Review:

```text
event.origin
event.source
Message structure
Data validation
DOM sinks
Navigation sinks
Code execution
API calls
```

Bad origin checks can include logic such as:

```text
substring checks
suffix checks
weak regexes
missing scheme/port assumptions
```

Prefer exact expected origins where the architecture permits.

---

# Prototype Pollution

Semgrep can identify:

```text
Recursive merges
Dynamic property assignment
Deep setters
__proto__
constructor
prototype
```

But:

```text
Prototype pollution primitive
          !=
Security impact
```

The complete chain is:

```text
Attacker-Controlled Key
        |
        v
Unsafe Object Write
        |
        v
Prototype Modified
        |
        v
Application Gadget
        |
        v
Security Impact
```

Use Semgrep to find both:

```text
Pollution primitives
Potential gadgets
```

Then connect them manually or through deeper data-flow analysis.

---

# Mass Assignment

Potential patterns include:

```text
Request body
    |
    v
Object merge
    |
    v
ORM model
    |
    v
Database
```

Node.js example:

```javascript
Object.assign(
    user,
    req.body
);
```

Candidate rule:

```yaml
rules:
  - id: node-request-body-object-assign
    languages:
      - javascript
      - typescript
    message: Review mass assignment of request data
    severity: WARNING
    pattern: Object.assign($OBJ, req.body)
```

This may identify interesting code but still requires determining:

```text
Which fields exist?

Which fields are sensitive?

Does schema validation restrict properties?

Does the ORM enforce field selection?
```

---

# Business Logic

Generic SAST tools are weaker at business logic.

Examples:

```text
Coupon reuse
Price manipulation
Approval workflow bypass
Account-state transitions
Duplicate redemption
Multi-step process bypass
Tenant-specific rules
```

Semgrep becomes useful once you identify a specific implementation pattern.

Example:

```text
Manual Review
      |
      v
Find Broken Discount Check
      |
      v
Identify Function
      |
      v
Create Semgrep Rule
      |
      v
Search Every Use
```

---

# Race Conditions

Semgrep can identify:

```text
Read-modify-write sequences
Transactions
Locks
Optimistic concurrency
Atomic operations
```

But proving a race condition generally requires understanding:

```text
Database isolation
Transactions
Concurrency
Application architecture
External systems
```

Static matching alone is rarely enough.

---

# Rate Limiting

Semgrep can identify application-level rate-limiting middleware and configuration.

However:

```text
No rate limiter in source
      !=
No rate limiting
```

Rate limiting may exist in:

```text
CDN
WAF
API gateway
Reverse proxy
Load balancer
Service mesh
```

---

# HTTP Security Headers

Source review may identify application configuration for:

```text
Content-Security-Policy
X-Frame-Options
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
```

But absence from application source does not prove absence in production.

Headers may be added externally.

---

# HTTP Request Smuggling

Semgrep is not sufficient to confirm HTTP request smuggling.

It can help identify:

```text
Custom HTTP parsers
Content-Length handling
Transfer-Encoding handling
Header rewriting
Proxy assumptions
```

Actual exploitability depends on the complete HTTP processing chain.

---

# Web Cache Issues

Semgrep can help locate:

```text
Cache-Control generation
Vary headers
Cache keys
Framework caching
Custom cache middleware
```

But cache poisoning and cache deception often depend on:

```text
CDN behaviour
Reverse proxy behaviour
Cache configuration
URL normalization
Header handling
```

Dynamic validation remains necessary.

---

# GraphQL

Use Semgrep to locate:

```text
Resolvers
Mutations
Subscriptions
Authentication checks
Authorisation checks
Database operations
```

A useful model is:

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
Database / Sink
```

Do not assume authentication at the GraphQL endpoint protects every object operation.

---

# WebSockets

Review:

```text
Connection authentication
Message handlers
Message-level authorisation
Object IDs
Subscriptions
Room/channel access
Input validation
Output encoding
```

A secure connection does not automatically mean every message operation is authorised.

---

# gRPC

Review:

```text
.proto files
Services
RPC methods
Interceptors
Authentication
Authorisation
Message fields
Database operations
Outbound requests
```

Static analysis can locate implementation methods and security-sensitive APIs.

---

# Secrets and Client Code

Remember:

```text
Browser JavaScript cannot keep a secret from the user.
```

Values intentionally shipped to a browser are visible to the browser user.

But not every exposed API key is a vulnerability.

Determine:

```text
What can the credential do?

Is it intentionally public?

Is it restricted?

Can it access privileged data?

Can it perform privileged operations?

Can it incur significant cost?
```

---

# Dependency Security

Semgrep is primarily source-code analysis.

Dependency vulnerabilities should also be assessed using software composition analysis tools such as:

```text
OSV-Scanner
npm audit
pip-audit
Trivy
Maven/Gradle tooling
NuGet tooling
Composer tooling
```

Semgrep can still identify:

```text
Dependency declarations
Unsafe API usage
Legacy APIs
Application-specific risky use of a library
```

---

# Semgrep Registry

Semgrep provides reusable rule configurations.

A broad scan can be useful during reconnaissance:

```bash
semgrep scan --config auto .
```

For serious assessments:

```text
Do not blindly trust rule packs.

Review which rules ran.

Understand their assumptions.

Validate findings manually.

Add application-specific rules.
```

---

# Generic Rules vs Project-Specific Rules

Generic:

```text
Find Runtime.exec
Find eval
Find innerHTML
Find pickle.loads
```

Project-specific:

```text
Find every use of internalCommandRunner()
Find every endpoint missing tenantCheck()
Find every unsafe reportQuery()
Find every call to fetchInternalUrl()
```

Project-specific rules often provide significantly more value after the application has been understood.

---

# Security Control Rules

Semgrep can search not only for dangerous operations but also for expected controls.

Example:

```text
Controller
    |
    v
Expected Authorisation Annotation
```

However, "absence" rules are difficult because controls may exist:

```text
Globally
In middleware
In parent classes
In filters
In interceptors
At infrastructure level
```

Missing-control rules require particularly careful design.

---

# Negative Patterns

Negative patterns can reduce noise.

Suppose:

```python
subprocess.run(
    command,
    shell=True
)
```

is interesting, while a fixed safe helper is known.

A rule can exclude the known-safe helper.

But always ask:

```text
Is the helper actually safe?

Can its implementation change?

Can attackers influence its inputs?

Will the exclusion hide future vulnerabilities?
```

---

# False Positives

Common causes:

```text
Safe parameterisation
Trusted constants
Unreachable code
Test code
Framework sanitisation
Effective validation
Internal-only data
Dead code
False source modelling
False sink modelling
Correctly configured security APIs
```

---

# False Negatives

Common causes:

```text
Custom wrappers
Aliased imports
Reflection
Dynamic dispatch
Framework magic
Interprocedural flows
Generated code
Unsupported syntax
Custom sanitizers
Second-order data
Database-stored attacker input
Message queues
Background jobs
```

No static analysis tool provides complete coverage.

---

# Second-Order Vulnerabilities

Example:

```text
HTTP Request
    |
    v
Database
    |
    v
Background Job
    |
    v
ProcessBuilder
```

A simple request-to-sink taint rule may miss the database boundary.

Manual review remains essential.

---

# Trust Boundaries

Do not treat data as trusted merely because it comes from:

```text
Database
Message queue
Internal API
Cache
File
Environment
Another microservice
```

Ask:

```text
Who originally controlled the data?
```

---

# Semgrep Output

Human-readable output is useful during manual review.

For automation, structured output is preferable.

Example:

```bash
semgrep scan \
  --config rules/ \
  --json \
  . \
  > semgrep.json
```

Then retain:

```text
Rule ID
File
Line
Message
Severity
Matched code
```

---

# Save Assessment Results

Recommended:

```text
review/
├── semgrep/
│   ├── initial.json
│   ├── custom.json
│   ├── variants.json
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

# Triage Template

```text
ID:
SG-001

Semgrep Rule:
flask-request-to-os-system

File:
app/routes/tools.py

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

Validation:
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

Use:

```text
Semgrep Match
     |
     v
Reachable?
     |
     +--> No -> Reject / Lower Priority
     |
     v
Attacker-Controlled Source?
     |
     +--> No -> Reject / Review Trust Boundary
     |
     v
Source Reaches Sink?
     |
     +--> No -> Reject
     |
     v
Validation / Sanitisation?
     |
     +--> Effective -> Protected
     |
     v
Framework Protection?
     |
     +--> Effective -> Protected
     |
     v
Deployment Protection?
     |
     +--> Effective -> Assess Residual Risk
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

# Dynamic Validation

Where authorised and appropriate, validate static candidates against the running application.

For web applications:

```text
Semgrep
   |
   v
Candidate Route
   |
   v
Burp Suite
   |
   v
Controlled Request
   |
   v
Observe Behaviour
   |
   v
Confirm / Reject
```

Do not begin dynamic testing without understanding:

```text
Scope
Environment
Potential side effects
Authentication
Data sensitivity
```

---

# Semgrep and Burp Suite

A powerful workflow is:

```text
Source Code
    |
    v
Semgrep
    |
    v
Potential Sink
    |
    v
Trace Back to Route
    |
    v
Identify HTTP Request
    |
    v
Burp Proxy / Repeater
    |
    v
Controlled Validation
```

Example:

```text
Semgrep finds:

request.args.get("url")
        ->
requests.get(url)

Trace to:

GET /preview?url=

Burp:

GET /preview?url=<controlled-test-destination>
```

The source code explains where to test.

Burp validates runtime behaviour.

---

# Semgrep and ripgrep

Use `ripgrep` first when you do not yet understand the application.

Example:

```bash
rg -n \
'ProcessBuilder|Runtime\.getRuntime' \
-g '*.java' \
.
```

Once a recurring pattern is identified:

```text
ripgrep
   |
   v
Interesting Pattern
   |
   v
Semgrep Rule
   |
   v
Syntax-Aware Variant Search
```

---

# Semgrep and OpenGrep

Semgrep and OpenGrep occupy similar static-analysis territory and can be useful in comparable rule-driven workflows.

A practical lab can maintain rules in a form that is tested against whichever engine is part of the assessment workflow.

Do not assume every feature, CLI option or rule behaviour is identical between engines.

Test compatibility.

Conceptually:

```text
Security Rule
    |
    +--> Semgrep
    |
    +--> OpenGrep
```

This makes rule portability worth considering.

The dedicated OpenGrep page should document differences and compatibility in more detail.

---

# Semgrep and CodeQL

Semgrep excels at:

```text
Fast pattern matching
Custom security rules
Local variant analysis
Readable rules
Developer-friendly scans
Targeted taint analysis
```

CodeQL is particularly useful for:

```text
Complex data flow
Interprocedural analysis
Call graphs
Type relationships
Semantic queries
Large-scale variant analysis
```

Recommended progression:

```text
ripgrep
   |
   v
Semgrep / OpenGrep
   |
   v
Manual Review
   |
   v
Complex Flow?
   |
   +--> No -> Continue Review
   |
   +--> Yes
          |
          v
        CodeQL
```

---

# Semgrep and VS Code

A productive workflow:

```text
Terminal:
semgrep scan ...

        |
        v

Finding:
src/controllers/UserController.java:84

        |
        v

VS Code:
code -g src/controllers/UserController.java:84

        |
        v

Go to Definition

        |
        v

Find References

        |
        v

Call Hierarchy

        |
        v

Trace Source -> Sink
```

---

# CI/CD Integration

Static analysis can also run during development.

Conceptually:

```text
Developer Push
      |
      v
CI Pipeline
      |
      v
Semgrep
      |
      v
Security Rules
      |
      v
Results
```

However, CI enforcement requires:

```text
Stable rules
Low false-positive rate
Clear ownership
Suppression process
Baseline strategy
Versioned rules
Developer guidance
```

Do not immediately fail builds on noisy experimental rules.

---

# Rule Lifecycle

```text
Experimental
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

Keep rules under version control.

---

# Rule Documentation

Each custom rule should document:

```text
Purpose
Vulnerability class
Supported language
Framework
Source
Sink
Sanitizers
Known false positives
Known false negatives
Test cases
Author
Last reviewed
```

Example:

```text
Rule:
flask-request-to-os-system

Purpose:
Detect Flask request parameters reaching os.system()

Source:
request.args.get()
request.form.get()

Sink:
os.system()

Known Limitations:
Does not model database-stored input.
Does not model every custom request wrapper.
Does not determine shell semantics.
```

---

# Rule Tests

Maintain:

```text
rules/
└── python/
    ├── command-injection.yml
    └── tests/
        └── command-injection.py
```

Test code should include:

```text
Expected matches
Expected non-matches
Edge cases
Alternate syntax
Wrapper functions
```

---

# Security Review Workflow

A complete source review can use:

```text
1. Open repository in VS Code

2. Identify languages and frameworks

3. Inventory routes

4. Inventory authentication

5. Inventory authorisation

6. Identify input sources

7. Search dangerous sinks with ripgrep

8. Run Semgrep rules

9. Review findings manually

10. Trace source -> sink

11. Identify validation and sanitisation

12. Review framework protections

13. Review infrastructure assumptions

14. Dynamically validate where appropriate

15. Confirm findings

16. Create variant rules

17. Run Semgrep again

18. Use OpenGrep for compatible/open-source workflows

19. Use CodeQL for complex flows

20. Document evidence and remediation
```

---

# Recommended Security Passes

Do not run only one generic scan.

Perform focused passes.

```text
Pass 1  - Attack surface
Pass 2  - Authentication
Pass 3  - Authorisation
Pass 4  - SQL
Pass 5  - NoSQL
Pass 6  - LDAP
Pass 7  - Command execution
Pass 8  - Dynamic code execution
Pass 9  - SSRF
Pass 10 - Files
Pass 11 - Uploads
Pass 12 - XML
Pass 13 - Deserialisation
Pass 14 - Templates
Pass 15 - XSS
Pass 16 - Redirects
Pass 17 - Prototype pollution
Pass 18 - Mass assignment
Pass 19 - Secrets
Pass 20 - Crypto
Pass 21 - API security
Pass 22 - Background processing
Pass 23 - Business logic variants
```

---

# Example Combined Workflow - Command Injection

Start with ripgrep:

```bash
rg -n \
'Runtime\.getRuntime|ProcessBuilder' \
-g '*.java' \
.
```

Then Semgrep:

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

Then:

```text
VS Code
   |
   v
Find References
   |
   v
Trace Arguments
   |
   v
Controller
   |
   v
@RequestParam
```

If a vulnerable helper is identified:

```text
executeReportCommand()
```

create a variant rule:

```yaml
rules:
  - id: application-report-command
    languages:
      - java
    message: Review use of vulnerable report command helper
    severity: ERROR
    pattern: executeReportCommand(...)
```

Then scan again.

---

# Example Combined Workflow - SSRF

ripgrep:

```bash
rg -n \
'requests\.|httpx\.|urlopen' \
-g '*.py' \
.
```

Semgrep:

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
      - pattern: httpx.get(...)
      - pattern: urllib.request.urlopen(...)
```

Then manually trace:

```text
request.args
     |
     v
url
     |
     v
validate_url()
     |
     v
requests.get()
```

Open:

```text
validate_url()
```

Review:

```text
Scheme
Hostname
Port
DNS resolution
Private IP ranges
Loopback
Link-local
Redirect handling
IPv6
Alternative IP formats
```

Only then determine exploitability.

---

# Example Combined Workflow - DOM XSS

ripgrep:

```bash
rg -n \
'location\.(search|hash)|innerHTML|outerHTML|insertAdjacentHTML|document\.write' \
-g '*.js' \
-g '*.ts' \
.
```

Semgrep sink rule:

```yaml
rules:
  - id: javascript-html-sink
    languages:
      - javascript
      - typescript
    message: Review attacker-controlled data reaching HTML sink
    severity: WARNING
    pattern-either:
      - pattern: $EL.innerHTML = $VALUE
      - pattern: $EL.outerHTML = $VALUE
      - pattern: $EL.insertAdjacentHTML(...)
      - pattern: document.write(...)
```

Then:

```text
location.search
      |
      v
URLSearchParams
      |
      v
value
      |
      v
DOMPurify.sanitize?
      |
      v
innerHTML
```

Review whether sanitisation exists and is correctly applied.

---

# Example Combined Workflow - IDOR / BOLA

Use ripgrep to inventory object retrieval:

```bash
rg -n \
'findById|findOne|objects\.get|objects\.filter|FindAsync|findUnique|findFirst' \
.
```

Semgrep can then target project-specific repository access patterns.

Example:

```text
repository.findById(id)
```

The important question is not:

```text
Does findById exist?
```

It is:

```text
Where is ownership or tenant authorisation enforced?
```

Semgrep is most useful after you identify the expected security helper.

For example:

```text
checkDocumentAccess(user, document)
```

Then search for sensitive document retrieval that does not follow the expected pattern.

This type of absence analysis is more complex and should be validated carefully.

---

# Example Combined Workflow - Mass Assignment

Candidate:

```javascript
router.patch(
    "/users/:id",
    async (req, res) => {
        const user =
            await User.findById(req.params.id);

        Object.assign(
            user,
            req.body
        );

        await user.save();

        res.json(user);
    }
);
```

Semgrep:

```yaml
rules:
  - id: node-object-assign-request-body
    languages:
      - javascript
      - typescript
    message: Review request-body mass assignment
    severity: WARNING
    pattern: Object.assign($OBJECT, req.body)
```

Then determine whether request validation restricts:

```text
role
permissions
isAdmin
tenantId
verified
status
balance
```

---

# Example Combined Workflow - Deserialisation

Python:

```python
data =
    request.get_data()

obj =
    pickle.loads(data)
```

Semgrep:

```yaml
rules:
  - id: python-pickle-loads
    languages:
      - python
    message: Review untrusted pickle deserialisation
    severity: WARNING
    pattern: pickle.loads(...)
```

Manual flow:

```text
HTTP Body
    |
    v
request.get_data()
    |
    v
pickle.loads()
```

This is much stronger evidence than:

```text
pickle.loads found somewhere in repository
```

---

# Finding Evidence

A source-review finding should contain:

```text
Affected route
Source
Transformations
Validation
Sink
Security controls
Data flow
Exploitability
Impact
Dynamic validation
Recommendation
```

Example:

```text
Route:
GET /preview

Source:
request.args.get("url")

Transformation:
None

Validation:
None

Sink:
requests.get(url)

Security Control:
No destination allowlist identified.

Data Flow:
HTTP query parameter -> Flask route -> requests.get()

Dynamic Validation:
Controlled destination requested successfully.

Impact:
Application can be induced to make server-side HTTP requests to attacker-selected destinations.
```

---

# Semgrep Finding Template

```text
Title:

Rule ID:

Language:

Framework:

File:

Line:

Affected Route:

Source:

Transformations:

Sanitizers:

Sink:

Security Controls:

Data Flow:

Reachability:

Exploitability:

Dynamic Validation:

Impact:

False-Positive Considerations:

Recommendation:
```

---

# False-Positive Checklist

Before reporting:

```text
[ ] Is the code reachable?
[ ] Is the source attacker-controlled?
[ ] Is the source correctly modelled?
[ ] Does the data reach the sink?
[ ] Is the sink security-sensitive in this context?
[ ] Is validation present?
[ ] Is sanitisation present?
[ ] Is encoding context-correct?
[ ] Is parameterisation used?
[ ] Does the framework provide protection?
[ ] Is the value constant or trusted?
[ ] Is authorisation enforced elsewhere?
[ ] Is infrastructure enforcing the control?
[ ] Can the behaviour be dynamically validated?
```

---

# False-Negative Checklist

After finishing the scan:

```text
[ ] Custom wrappers searched
[ ] Aliased imports considered
[ ] Helper functions searched
[ ] Background jobs reviewed
[ ] Queue consumers reviewed
[ ] Stored second-order data considered
[ ] GraphQL reviewed
[ ] gRPC reviewed
[ ] WebSockets reviewed
[ ] Alternate controllers reviewed
[ ] Custom middleware reviewed
[ ] Reflection/dynamic dispatch considered
[ ] Generated routes considered
[ ] Variant rules created
```

---

# Semgrep Review Checklist

## Setup

```text
[ ] Repository confirmed
[ ] Branch confirmed
[ ] Commit recorded
[ ] Semgrep version recorded
[ ] Languages identified
[ ] Frameworks identified
[ ] Exclusions reviewed
```

## Reconnaissance

```text
[ ] Routes mapped
[ ] Controllers mapped
[ ] API endpoints mapped
[ ] Authentication identified
[ ] Authorisation identified
[ ] Middleware identified
[ ] Background jobs identified
[ ] Message consumers identified
```

## Sources

```text
[ ] Query parameters
[ ] Route parameters
[ ] Request bodies
[ ] Headers
[ ] Cookies
[ ] Files
[ ] GraphQL inputs
[ ] WebSocket messages
[ ] gRPC messages
[ ] Queue messages
[ ] Stored attacker-controlled data
```

## Injection

```text
[ ] SQL injection
[ ] NoSQL injection
[ ] LDAP injection
[ ] Command injection
[ ] Dynamic code execution
[ ] SSTI
[ ] Expression injection
```

## Server-Side

```text
[ ] SSRF
[ ] Path traversal
[ ] File inclusion
[ ] File upload
[ ] Archive extraction
[ ] XXE
[ ] Deserialisation
```

## Client-Side

```text
[ ] DOM XSS
[ ] HTML injection
[ ] Open redirect
[ ] postMessage
[ ] Dynamic JavaScript
[ ] Prototype pollution
[ ] Third-party JavaScript
```

## Access Control

```text
[ ] Authentication
[ ] Authorisation
[ ] IDOR / BOLA
[ ] Mass assignment
[ ] Session management
[ ] Tenant isolation
```

## Identity

```text
[ ] JWT
[ ] OAuth/OIDC
[ ] SAML
[ ] Password reset
[ ] MFA
```

## APIs

```text
[ ] REST
[ ] GraphQL
[ ] gRPC
[ ] WebSockets
[ ] Webhooks
```

## Application Logic

```text
[ ] Business logic
[ ] Race conditions
[ ] Rate limiting
[ ] Workflow enforcement
```

## Data Protection

```text
[ ] Secrets
[ ] Cryptography
[ ] Logging
[ ] Error handling
[ ] Debug configuration
```

## Variant Analysis

```text
[ ] Confirmed findings converted into patterns
[ ] Custom helpers modelled
[ ] Similar sinks searched
[ ] Similar sources searched
[ ] Alternate syntax tested
[ ] Rules tested against positive examples
[ ] Rules tested against negative examples
[ ] OpenGrep compatibility considered
[ ] CodeQL considered for complex flows
```

## Validation

```text
[ ] Findings manually reviewed
[ ] Reachability confirmed
[ ] Attacker control confirmed
[ ] Source-to-sink flow confirmed
[ ] Security controls reviewed
[ ] Framework protections reviewed
[ ] Deployment controls considered
[ ] Dynamic validation performed where appropriate
[ ] False positives removed
```

---

# Common Mistakes

## Reporting Every Semgrep Finding

Wrong:

```text
Semgrep reported 120 security vulnerabilities.
```

Better:

```text
Semgrep identified 120 candidates requiring triage.
```

After review:

```text
120 candidates
     |
     v
Manual Triage
     |
     +--> False Positive
     +--> Informational
     +--> Security Hardening
     +--> Vulnerability
```

---

# Treating Sink Discovery as Taint Analysis

A rule:

```yaml
pattern: os.system(...)
```

finds a sink.

It does not establish:

```text
Attacker input -> os.system()
```

---

# Overtrusting Sanitizers

A function called:

```text
sanitizeInput()
```

may:

```text
Remove HTML
```

while the actual sink is:

```text
SQL
```

or:

```text
Shell
```

Sanitization must match the sink context.

---

# Ignoring Framework Behaviour

Examples:

```text
React JSX text escaping
Django template autoescaping
Parameterized ORM queries
Spring Security filters
ASP.NET Core model binding
```

Framework behaviour can materially affect exploitability.

---

# Assuming Framework Defaults Are Active

Applications can:

```text
Disable protections
Override defaults
Use raw APIs
Use unsafe bypass APIs
Implement custom rendering
Implement custom authentication
```

Review actual code and configuration.

---

# Ignoring Infrastructure

Security controls may exist outside source code:

```text
CDN
WAF
API gateway
Reverse proxy
Load balancer
Service mesh
Identity-aware proxy
```

Static review cannot see everything.

---

# Ignoring Business Context

A technically suspicious operation may have no attacker-controlled path.

Conversely, code that looks ordinary may contain a serious business logic flaw.

Semgrep is strongest when combined with understanding of the application.

---

# Relying Only on Generic Rules

Generic rules are useful at the beginning.

The highest-value rules are often created after discovering how the application works.

```text
Generic Rules
     |
     v
Learn Application
     |
     v
Find Vulnerability
     |
     v
Create Custom Rule
     |
     v
Variant Analysis
```

---

# Semgrep Security Testing Model

```text
                          REPOSITORY
                              |
                              v
                       VISUAL STUDIO CODE
                              |
                              v
                     UNDERSTAND APPLICATION
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
          ripgrep                           Semgrep
             |                                 |
             v                                 v
      Text Reconnaissance              Structural Search
             |                                 |
             +----------------+----------------+
                              |
                              v
                        ATTACK SURFACE
                              |
              +---------------+---------------+
              |                               |
              v                               v
           SOURCES                           SINKS
              |                               |
              +---------------+---------------+
                              |
                              v
                         TAINT FLOW
                              |
                              v
                       TRANSFORMATIONS
                              |
              +---------------+---------------+
              |                               |
              v                               v
          VALIDATION                      SANITISATION
              |                               |
              +---------------+---------------+
                              |
                              v
                     SECURITY CONTROLS
                              |
                              v
                     MANUAL VALIDATION
                              |
                    +---------+---------+
                    |                   |
                    v                   v
              False Positive        Candidate
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
                    +-------------------+-------------------+
                    |                   |                   |
                    v                   v                   v
                 ripgrep             Semgrep            OpenGrep
                                                            |
                                        +-------------------+
                                        |
                                        v
                                      CodeQL
```

---

# Final Source-to-Sink Model

For every Semgrep security result, ask:

```text
SOURCE
  |
  v
Can an attacker control it?
  |
  v
TRANSFORMATIONS
  |
  +--> parsing
  +--> decoding
  +--> validation
  +--> sanitisation
  +--> normalisation
  +--> business logic
  |
  v
SINK
  |
  v
Is the sink security-sensitive?
  |
  v
SECURITY CONTROLS
  |
  v
Can they be bypassed?
  |
  v
IMPACT
```

A finding becomes meaningful when you can demonstrate:

```text
Source found
    +
Attacker control established
    +
Reachable flow established
    +
Sink found
    +
Security control absent or ineffective
    +
Security impact established
```

Not simply:

```text
Semgrep matched code
```

---

# Quick Reference

## Initial Scan

```bash
semgrep scan \
  --config auto \
  .
```

## Local Rules

```bash
semgrep scan \
  --config rules/ \
  .
```

## JSON Output

```bash
semgrep scan \
  --config rules/ \
  --json \
  . \
  > semgrep.json
```

## Python Command Rule

```yaml
rules:
  - id: python-command-execution
    languages:
      - python
    message: Review command execution
    severity: WARNING
    pattern-either:
      - pattern: os.system(...)
      - pattern: subprocess.run(...)
      - pattern: subprocess.Popen(...)
```

## Java Command Rule

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

## PHP Command Rule

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
```

## Browser JavaScript HTML Sink

```yaml
rules:
  - id: javascript-html-sink
    languages:
      - javascript
      - typescript
    message: Review HTML sink
    severity: WARNING
    pattern-either:
      - pattern: $EL.innerHTML = $VALUE
      - pattern: $EL.outerHTML = $VALUE
      - pattern: $EL.insertAdjacentHTML(...)
      - pattern: document.write(...)
```

## Flask Taint Rule

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

    pattern-sinks:
      - pattern: os.system(...)
```

---

# Recommended Workflow

```text
VS Code
   |
   v
Understand Repository
   |
   v
ripgrep
   |
   v
Map Routes / Sources / Sinks
   |
   v
Semgrep
   |
   v
Structural Security Search
   |
   v
Taint Analysis
   |
   v
Manual Source-to-Sink Review
   |
   v
Dynamic Validation
   |
   v
Confirmed Vulnerability
   |
   v
Create Custom Semgrep Rule
   |
   v
Variant Analysis
   |
   +--> Semgrep
   |
   +--> OpenGrep
   |
   +--> CodeQL
```

---

# References

## Semgrep

```text
https://semgrep.dev/
```

## Semgrep Documentation

```text
https://semgrep.dev/docs/
```

## Semgrep CLI Reference

```text
https://semgrep.dev/docs/cli-reference
```

## Semgrep Rule Syntax

```text
https://semgrep.dev/docs/writing-rules/rule-syntax
```

## Semgrep Pattern Syntax

```text
https://semgrep.dev/docs/writing-rules/pattern-syntax
```

## Semgrep Taint Mode

```text
https://semgrep.dev/docs/writing-rules/data-flow/taint-mode
```

## Semgrep Rule Writing

```text
https://semgrep.dev/docs/writing-rules/overview
```

## Semgrep GitHub Repository

```text
https://github.com/semgrep/semgrep
```

## OWASP Secure Code Review Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html
```

## OWASP Code Review Guide

```text
https://owasp.org/www-project-code-review-guide/
```

## OWASP Cheat Sheet Series

```text
https://cheatsheetseries.owasp.org/
```

## Visual Studio Code

```text
https://code.visualstudio.com/docs
```

## OpenGrep

```text
https://opengrep.dev/
```

## OpenGrep GitHub

```text
https://github.com/opengrep/opengrep
```

## CodeQL Documentation

```text
https://codeql.github.com/docs/
```

---

# Related Static Analysis Notes

```text
docs/source-code-review/static-analysis/index.md
docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/opengrep.md
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
