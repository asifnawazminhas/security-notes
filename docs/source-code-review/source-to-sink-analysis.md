# Source-to-Sink Analysis

Source-to-sink analysis is one of the most important techniques in security source code review.

The objective is to determine whether attacker-controlled data can travel from an application entry point to a security-sensitive operation without sufficient validation, sanitisation, encoding, authorisation, or other security controls.

The fundamental model is:

```text
SOURCE
  |
  v
ATTACKER-CONTROLLED DATA
  |
  v
TRANSFORMATIONS
  |
  +-- parsing
  +-- decoding
  +-- validation
  +-- normalisation
  +-- sanitisation
  +-- encoding
  +-- business logic
  +-- persistence
  |
  v
SINK
  |
  v
SECURITY-SENSITIVE OPERATION
```

Examples include:

```text
HTTP Parameter
      |
      v
String Concatenation
      |
      v
SQL Execution
```

```text
HTTP Parameter
      |
      v
Command Builder
      |
      v
Process Execution
```

```text
User-Supplied URL
      |
      v
URL Parser
      |
      v
HTTP Client
```

```text
Uploaded Filename
      |
      v
Path Construction
      |
      v
Filesystem Write
```

The presence of a source and sink alone does not prove a vulnerability.

```text
Source
  +
Sink
  !=
Vulnerability
```

The complete question is:

```text
Can attacker-controlled data
reach a security-sensitive sink
through a feasible execution path
without an effective security control?
```

---

# Authorised Testing

Use these techniques only when reviewing applications, repositories, and environments that you are authorised to assess.

Source code analysis can reveal sensitive information including:

```text
Credentials
API keys
Internal endpoints
Database structure
Authentication logic
Authorisation logic
Cryptographic material
Infrastructure information
Business logic
```

Handle source code and findings according to the assessment rules of engagement.

---

# Why Source-to-Sink Analysis Matters

Searching for dangerous functions is useful.

For example:

```bash
rg -n 'Runtime\.getRuntime\(\)\.exec|ProcessBuilder' .
```

may reveal command-execution functionality.

But:

```text
Dangerous Sink Found
        |
        v
Vulnerability?
```

cannot be answered yet.

The sink may receive:

```text
Hardcoded data
Trusted configuration
Administrator-controlled data
Validated input
Allowlisted values
Attacker-controlled data
```

Only the last case, or another attacker-influenced path, may create a vulnerability.

Therefore:

```text
Sink Discovery
      |
      v
Data-Flow Analysis
      |
      v
Control Analysis
      |
      v
Reachability Analysis
      |
      v
Exploitability Analysis
```

---

# The Core Security Model

A useful model is:

```text
ENTRY POINT
     |
     v
SOURCE
     |
     v
PROPAGATION
     |
     v
TRANSFORMATION
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

Each stage should be investigated separately.

---

# Entry Point

An entry point is where execution enters application-controlled code.

Examples:

```text
HTTP route
REST endpoint
GraphQL resolver
gRPC method
WebSocket handler
Message queue consumer
Webhook handler
Background job
Scheduled task
CLI interface
File import
Event handler
Serverless function
```

An entry point is not necessarily a source.

For example:

```java
@GetMapping("/health")
public String health() {
    return "OK";
}
```

This is an entry point but does not contain attacker-controlled input.

---

# Source

A source is where potentially attacker-controlled data enters the data flow.

Typical sources include:

```text
Query parameters
Route parameters
Request bodies
HTTP headers
Cookies
Uploaded files
Uploaded filenames
GraphQL arguments
gRPC request fields
WebSocket messages
Webhook payloads
Queue messages
Environment-dependent external data
Database values originally supplied by users
```

---

# Sink

A sink is a security-sensitive operation.

Typical sink categories include:

```text
Database execution
OS command execution
Dynamic code execution
Template evaluation
HTML rendering
HTTP requests
Filesystem operations
XML parsing
Deserialisation
LDAP queries
Redirects
Authentication decisions
Authorisation decisions
Cryptographic operations
Sensitive logging
```

A sink can be dangerous without being vulnerable.

---

# Transformations

Between source and sink, data may be transformed.

Example:

```text
Request Parameter
       |
       v
URL Decode
       |
       v
Trim
       |
       v
Lowercase
       |
       v
Regex Validation
       |
       v
Database Lookup
       |
       v
Command Builder
       |
       v
Process Execution
```

Every transformation matters.

---

# Security Controls

Potential controls include:

```text
Allowlisting
Type validation
Range validation
Canonicalisation
Path containment
Parameterised queries
Context-aware output encoding
URL validation
Authentication
Authorisation
CSRF validation
Cryptographic verification
Safe API usage
Sandboxing
```

The reviewer must determine whether the control is effective for the specific sink.

---

# Impact

A technically interesting flow is not necessarily a meaningful security vulnerability.

Determine what the sink allows.

Examples:

```text
Database Read
Database Write
Command Execution
Internal HTTP Request
Arbitrary File Read
Arbitrary File Write
Cross-User Data Access
Privilege Change
Session Creation
HTML/JavaScript Execution
Sensitive Information Disclosure
```

---

# Forward Analysis

Forward analysis begins at a source.

```text
SOURCE
  |
  v
Where does the data go?
```

Example:

```java
@GetMapping("/search")
public String search(
    @RequestParam String q
) {
    return searchService.search(q);
}
```

Start with:

```text
q
```

Then trace:

```text
q
 |
 v
searchService.search()
 |
 v
repository.search()
 |
 v
SQL query
```

---

# Forward Analysis Workflow

```text
Source
  |
  v
Find References
  |
  v
Assignments
  |
  v
Function Arguments
  |
  v
Return Values
  |
  v
Object Properties
  |
  v
Transformations
  |
  v
Sink
```

Forward analysis is useful when:

```text
A suspicious parameter exists
A new endpoint is being reviewed
An uploaded file is processed
A webhook payload is consumed
A GraphQL argument is interesting
A security-sensitive request field exists
```

---

# Reverse Analysis

Reverse analysis begins at a sink.

```text
SINK
  |
  v
Where does its data come from?
```

Example:

```java
Runtime
    .getRuntime()
    .exec(command);
```

Start with:

```text
command
```

Then trace backwards:

```text
Runtime.exec()
      ^
      |
command
      ^
      |
buildCommand()
      ^
      |
host
      ^
      |
@RequestParam
```

---

# Reverse Analysis Workflow

```text
Dangerous Sink
      |
      v
Inspect Arguments
      |
      v
Find Assignments
      |
      v
Trace Return Values
      |
      v
Trace Callers
      |
      v
Trace Controllers
      |
      v
Identify Source
```

Reverse analysis is often highly efficient because dangerous sinks are usually less numerous than application inputs.

---

# Bidirectional Analysis

The strongest approach combines both directions.

```text
SOURCE
  |
  v
Forward Trace
  |
  v
Potential Sink

AND

SINK
  |
  v
Reverse Trace
  |
  v
Potential Source
```

If both analyses meet:

```text
SOURCE
  |
  v
FLOW
  |
  v
SINK
```

the candidate deserves closer review.

---

# Recommended Review Strategy

Use:

```text
1. Map entry points

2. Identify sources

3. Identify dangerous sinks

4. Trace important sources forward

5. Trace dangerous sinks backwards

6. Identify where the traces meet

7. Review transformations

8. Review security controls

9. Establish reachability

10. Establish attacker control

11. Establish impact

12. Validate dynamically where appropriate

13. Search for variants
```

---

# Visual Studio Code Workflow

Visual Studio Code is particularly useful for manual source-to-sink tracing.

Open the repository:

```bash
code .
```

Useful features include:

```text
Global Search
Go to Definition
Peek Definition
Find All References
Call Hierarchy
Workspace Symbols
Integrated Terminal
Git History
Breakpoints
Debugger
```

---

# Global Search

Use:

```text
Ctrl + Shift + F
```

to search across the repository.

Useful searches include:

```text
exec(
Process.Start
Runtime.getRuntime
HttpClient
requests.get
fetch(
innerHTML
executeQuery
FromSqlRaw
pickle.loads
ObjectInputStream
redirect(
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
```

---

# Find All References

Use:

```text
Shift + F12
```

This is extremely useful for reverse sink analysis.

Example:

```text
Dangerous Helper

executeCommand()
      |
      +--> Controller A
      +--> Controller B
      +--> Worker
      +--> Admin API
```

One helper may expose several attack paths.

---

# Call Hierarchy

Call Hierarchy can help understand:

```text
Who calls this method?
```

and:

```text
What does this method call?
```

This is especially useful in:

```text
Java
C#
TypeScript
JavaScript
Python
```

when language-server support is available.

---

# Workspace Symbols

Use:

```text
Ctrl + T
```

to search symbols across the project.

Useful when searching for:

```text
Controllers
Services
Repositories
Security classes
Validators
Upload handlers
HTTP clients
Command wrappers
```

---

# Split Editor Workflow

A useful layout is:

```text
+---------------------------------------------+
| Controller              | Sink              |
|                         |                   |
| UserController          | CommandService    |
|                         |                   |
+-------------------------+-------------------+
| Service                 | Notes             |
|                         |                   |
| UserService             | Source -> Sink    |
+-------------------------+-------------------+
```

Keep:

```text
Source
Intermediate Function
Sink
```

visible simultaneously where possible.

---

# Trace Variables, Not Just Function Names

Consider:

```java
String host =
    request.getParameter("host");

String target =
    host.trim();

String command =
    "ping " + target;

execute(command);
```

Trace:

```text
request.getParameter("host")
          |
          v
        host
          |
          v
      host.trim()
          |
          v
        target
          |
          v
   "ping " + target
          |
          v
       command
          |
          v
      execute()
```

Do not lose track of attacker influence merely because the variable name changes.

---

# Assignment Propagation

Simple propagation:

```python
user_input = request.args.get("url")
target = user_input
value = target
requests.get(value)
```

Flow:

```text
request.args
     |
     v
user_input
     |
     v
target
     |
     v
value
     |
     v
requests.get
```

---

# Function Argument Propagation

Example:

```python
def handler():
    value = request.args.get("url")
    fetch(value)

def fetch(target):
    requests.get(target)
```

Flow:

```text
request.args
     |
     v
value
     |
     v
fetch(value)
     |
     v
target
     |
     v
requests.get(target)
```

---

# Return Value Propagation

Example:

```python
def get_target():
    return request.args.get("url")

def handler():
    target = get_target()
    requests.get(target)
```

Flow:

```text
request.args
     |
     v
get_target()
     |
     v
return value
     |
     v
target
     |
     v
requests.get()
```

---

# Object Property Propagation

Example:

```javascript
const requestData = {
    target: req.query.url
};

service.fetch(requestData);
```

Later:

```javascript
function fetch(data) {
    return axios.get(data.target);
}
```

Flow:

```text
req.query.url
     |
     v
requestData.target
     |
     v
data.target
     |
     v
axios.get()
```

---

# DTO Propagation

Enterprise applications frequently move data through DTOs.

```text
HTTP Request
     |
     v
Request DTO
     |
     v
Service DTO
     |
     v
Domain Object
     |
     v
Repository
```

Do not stop tracing because input has been converted into an object.

---

# Collection Propagation

Attacker-controlled data may pass through:

```text
Lists
Arrays
Maps
Dictionaries
Sets
Queues
```

Example:

```python
targets = []

targets.append(
    request.args.get("url")
)

for target in targets:
    requests.get(target)
```

The source remains attacker-controlled.

---

# String Transformation

Common transformations include:

```text
Concatenation
Interpolation
Formatting
Replacement
Trimming
Case conversion
Substring
Encoding
Decoding
Escaping
```

Example:

```python
host = request.args.get("host")

command = f"ping -c 1 {host}"

os.system(command)
```

The string transformation does not remove attacker control.

---

# Encoding Is Not Automatically Sanitisation

Example:

```text
Base64 Encode
URL Encode
JSON Encode
HTML Encode
```

Encoding changes representation.

It does not necessarily make input safe for another context.

```text
URL Encoding
    !=
Command Injection Protection
```

```text
Base64
    !=
SQL Injection Protection
```

---

# Decoding Can Reintroduce Dangerous Input

Example:

```text
Request
   |
   v
Validation
   |
   v
URL Decode
   |
   v
Sink
```

Ask:

```text
Was validation performed before or after decoding?
```

Canonicalisation order matters.

---

# Validation

Validation attempts to determine whether input is acceptable.

Examples:

```text
Type checks
Length checks
Regex
Allowlist
Range checks
Enum validation
Schema validation
```

Example:

```python
if host not in allowed_hosts:
    abort(400)

requests.get(host)
```

This may provide meaningful protection depending on how `allowed_hosts` is defined and how the HTTP request is constructed.

---

# Allowlisting

Allowlisting is often stronger than denylisting.

Example:

```python
allowed = {
    "api.example.com",
    "images.example.com"
}

if hostname not in allowed:
    raise ValueError()

fetch(url)
```

But review:

```text
URL parsing
DNS resolution
Redirects
Port handling
Scheme handling
Userinfo
Case normalisation
Trailing dots
Internationalised domain names
```

A conceptually correct allowlist can still be implemented incorrectly.

---

# Denylisting

Example:

```python
if "127.0.0.1" in url:
    reject()
```

This may be insufficient because alternative representations or other internal destinations may exist.

Do not automatically report bypassability.

Determine whether the complete validation logic can actually be bypassed.

---

# Sanitisation

Sanitisation modifies data to make it safe for a particular sink.

Example:

```text
Attacker HTML
     |
     v
HTML Sanitizer
     |
     v
innerHTML
```

The security question becomes:

```text
Is the sanitizer appropriate?

Is it configured correctly?

Is sanitisation applied after the final transformation?

Can later operations undo the protection?

Is the output used in the expected context?
```

---

# Context Matters

Protection effective for one sink may be irrelevant for another.

```text
HTML Encoding
    protects
HTML Text Context

but does not necessarily protect
    |
    +--> JavaScript
    +--> SQL
    +--> Shell
    +--> LDAP
    +--> Filesystem
```

Similarly:

```text
SQL parameterisation
```

does not protect:

```text
OS command execution
```

---

# Safe API Usage

Sometimes the strongest protection is using a safer API.

For SQL:

```text
String Concatenation
      |
      v
Raw Query
```

versus:

```text
Parameterized Query
```

For process execution:

```text
Shell Command String
```

versus:

```text
Executable + Argument Array
```

Even safer APIs still require review for context-specific risks.

---

# Reachability

A source-to-sink flow matters only if the code can execute.

Ask:

```text
Is the route registered?

Is the feature enabled?

Is the code dead?

Is the function called?

Is the configuration active?

Is the endpoint exposed?

Is the branch reachable?

Is the environment relevant?
```

---

# Dead Code

Example:

```python
if False:
    os.system(request.args.get("cmd"))
```

A scanner may find:

```text
os.system
```

but the path is not normally reachable.

Do not report solely from textual evidence.

---

# Feature Flags

Example:

```text
if FEATURE_DIAGNOSTICS:
    execute_command()
```

Determine:

```text
Is the feature enabled in production?

Can users influence the feature flag?

Does another environment expose it?
```

---

# Authentication

A vulnerable sink may require authentication.

That affects:

```text
Attack prerequisites
Severity
Exploitability
```

but does not automatically eliminate the vulnerability.

Document:

```text
Unauthenticated
Authenticated user
Privileged user
Administrator
Service account
```

---

# Authorisation

Authentication answers:

```text
Who are you?
```

Authorisation answers:

```text
Are you allowed to do this?
```

Source-to-sink analysis must include both where relevant.

Example:

```text
User-Controlled Document ID
          |
          v
Database Lookup
          |
          v
Document Returned
```

The missing security control may not be input validation.

It may be:

```text
Ownership Check
```

---

# Security Controls Are Part of the Flow

For access control:

```text
Request
   |
   v
Authentication
   |
   v
Object ID
   |
   v
Object Lookup
   |
   v
Authorisation
   |
   v
Sensitive Operation
```

The reviewer should verify:

```text
Authorisation occurs
at the correct point
for the correct object
using the correct identity
```

---

# Source-to-Sink for SQL Injection

Model:

```text
HTTP Input
    |
    v
SQL Construction
    |
    v
SQL Execution
```

Potential sources:

```text
Query parameter
Route parameter
JSON field
Header
Cookie
Stored user data
```

Potential sinks:

```text
execute()
executeQuery()
raw()
query()
FromSqlRaw()
createNativeQuery()
```

---

# Vulnerable SQL Pattern

```python
username = request.args.get("username")

query = (
    "SELECT * FROM users "
    "WHERE username = '" +
    username +
    "'"
)

cursor.execute(query)
```

Flow:

```text
request.args
     |
     v
username
     |
     v
SQL concatenation
     |
     v
cursor.execute()
```

---

# Safer SQL Pattern

```python
username = request.args.get("username")

cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)
)
```

Here:

```text
User Input
    |
    v
SQL Parameter
```

rather than:

```text
User Input
    |
    v
SQL Syntax
```

---

# Stored / Second-Order SQL Injection

Do not only trace direct request flows.

```text
HTTP Input
    |
    v
Database
    |
    v
Later Retrieval
    |
    v
SQL Construction
    |
    v
SQL Execution
```

The source may be temporally separated from the sink.

---

# Command Injection

Model:

```text
HTTP Input
    |
    v
Command Construction
    |
    v
Process Execution
```

Potential sinks:

```text
Runtime.exec
ProcessBuilder
Process.Start
os.system
subprocess
child_process.exec
shell_exec
system
exec
```

---

# Java Example

```java
String host =
    request.getParameter("host");

Runtime
    .getRuntime()
    .exec(
        "ping " + host
    );
```

Flow:

```text
request.getParameter
        |
        v
      host
        |
        v
concatenation
        |
        v
Runtime.exec
```

---

# .NET Example

```csharp
var host =
    Request.Query["host"];

Process.Start(
    "cmd.exe",
    "/c ping " + host
);
```

Trace:

```text
Request.Query
     |
     v
host
     |
     v
Process.Start
```

---

# Node.js Example

```javascript
const host =
    req.query.host;

exec(
    `ping ${host}`
);
```

Trace:

```text
req.query.host
     |
     v
template literal
     |
     v
exec()
```

---

# SSRF

Model:

```text
Attacker-Controlled URL
          |
          v
URL Processing
          |
          v
HTTP Client
```

Potential sinks include:

```text
HttpClient
requests
httpx
urllib
fetch
axios
RestTemplate
WebClient
```

---

# Python SSRF Example

```python
url =
    request.args.get("url")

response =
    requests.get(url)
```

Flow:

```text
request.args
     |
     v
url
     |
     v
requests.get()
```

Then review controls:

```text
Scheme validation
Hostname validation
IP validation
DNS behaviour
Redirect handling
Port restrictions
Private address restrictions
Cloud metadata restrictions
```

---

# SSRF Through Helper

```python
def preview(url):
    return requests.get(url)

def endpoint():
    target =
        request.args.get("url")

    return preview(target)
```

Trace:

```text
request.args
     |
     v
target
     |
     v
preview()
     |
     v
url
     |
     v
requests.get()
```

---

# Path Traversal

Model:

```text
Attacker-Controlled Path
          |
          v
Path Construction
          |
          v
Filesystem Operation
```

Potential sinks:

```text
open()
File.ReadAllText
File.WriteAllText
Files.readString
send_file
fs.readFile
fs.writeFile
```

---

# Python Example

```python
filename =
    request.args.get("file")

path =
    "/var/data/" + filename

return open(path).read()
```

Trace:

```text
request.args
     |
     v
filename
     |
     v
path
     |
     v
open()
```

---

# Path Normalisation

A common pattern:

```text
Input
  |
  v
Normalize
  |
  v
Filesystem
```

Normalisation alone may not ensure that the final path remains inside the intended directory.

Review:

```text
Canonical path
Base directory
Containment check
Symlinks
Absolute paths
Platform path semantics
```

---

# File Upload

File upload contains several independent sources:

```text
Uploaded File
     |
     +--> Filename
     +--> Extension
     +--> MIME type
     +--> Content
     +--> Size
     +--> Metadata
```

Each can flow to different sinks.

---

# Filename Flow

```text
Original Filename
       |
       v
Path Construction
       |
       v
File Write
```

Potential issue:

```text
Path Traversal
```

---

# File Content Flow

```text
Uploaded Content
       |
       v
Parser
       |
       v
Image / PDF / XML / Archive Processor
```

Potential issues:

```text
Parser vulnerabilities
XXE
Archive extraction issues
Unsafe deserialisation
Command execution
Resource exhaustion
```

---

# Archive Extraction

Trace:

```text
Archive Entry Name
       |
       v
Destination Path
       |
       v
Filesystem Write
```

Review path containment after extraction path resolution.

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
External Entity Resolution
```

The sink is not merely:

```text
XML parser exists
```

The important configuration includes:

```text
DTD handling
External entities
External resources
Resolver configuration
Parser defaults
```

---

# Deserialisation

Model:

```text
Attacker-Controlled Serialized Data
               |
               v
           Deserializer
```

Potential sinks include:

```text
ObjectInputStream
pickle.loads
BinaryFormatter
YAML unsafe loaders
Language-specific object serializers
```

A deserializer is not automatically vulnerable.

Establish attacker control.

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
Template Engine
```

Important distinction:

```text
Template Data
```

versus:

```text
Template Source
```

Example:

```python
render_template(
    "profile.html",
    username=user_input
)
```

is different from:

```python
render_template_string(
    user_input
)
```

---

# Server-Side XSS Analysis

Model:

```text
HTTP Input
    |
    v
Application
    |
    v
HTML Generation
    |
    v
Browser
```

Review:

```text
Template autoescaping
Manual raw output
Context
Encoding
Sanitisation
```

---

# DOM XSS

Model:

```text
Browser Source
      |
      v
JavaScript
      |
      v
DOM Sink
```

Sources include:

```text
location.search
location.hash
location.href
document.URL
document.referrer
window.name
postMessage
localStorage
sessionStorage
```

Sinks include:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
eval
Function
srcdoc
```

---

# DOM XSS Example

```javascript
const value =
    new URLSearchParams(
        location.search
    ).get("message");

output.innerHTML =
    value;
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

---

# HTML Injection

Not every HTML sink results in JavaScript execution.

Trace:

```text
Attacker Input
     |
     v
HTML Interpretation
```

Then determine actual impact:

```text
Markup injection
UI manipulation
Phishing
Form injection
Potential XSS
```

Do not automatically classify HTML injection as XSS.

---

# Open Redirect

Model:

```text
Attacker-Controlled URL
          |
          v
Redirect Sink
```

Potential sinks:

```text
redirect()
Response.Redirect()
sendRedirect()
location.href
location.assign()
location.replace()
```

Review validation of:

```text
Scheme
Host
Path
Relative URLs
Protocol-relative URLs
Parsing
Normalisation
```

---

# LDAP Injection

Model:

```text
Attacker Input
     |
     v
LDAP Filter Construction
     |
     v
LDAP Search
```

Review:

```text
LDAP filter escaping
DN escaping
Filter construction
Framework API
```

LDAP DN and LDAP filter contexts require different handling.

---

# NoSQL Injection

Model:

```text
Attacker Input
     |
     v
Query Object
     |
     v
NoSQL Database
```

Especially review cases where structured input is passed directly into query objects.

Example:

```javascript
const filter =
    req.body.filter;

const result =
    await users.find(filter);
```

Trace whether attackers can control:

```text
Operators
Nested objects
Query structure
Regular expressions
```

---

# Mass Assignment

Model:

```text
Request Body
     |
     v
Automatic Object Binding
     |
     v
Domain Object
     |
     v
Database
```

Sensitive properties may include:

```text
isAdmin
role
permissions
ownerId
tenantId
balance
status
verified
```

---

# IDOR / BOLA

IDOR/BOLA is a source-to-security-decision problem.

```text
Attacker-Controlled Object ID
           |
           v
Object Retrieval
           |
           v
Authorisation?
           |
           v
Sensitive Operation
```

The sink may be:

```text
Read object
Modify object
Delete object
Download object
Execute action
```

---

# IDOR Example

```python
@app.get("/documents/<id>")
def document(id):

    return Document.query.get(id)
```

Trace:

```text
Route Parameter
      |
      v
id
      |
      v
Database Lookup
      |
      v
Document
```

Then ask:

```text
Where is ownership checked?
```

---

# Business Logic

Not all source-to-sink flows end in classic dangerous APIs.

Example:

```text
User-Controlled Quantity
        |
        v
Price Calculation
        |
        v
Payment
```

or:

```text
User-Controlled Role
        |
        v
Account Update
```

or:

```text
Coupon
   |
   v
Discount
   |
   v
Order Total
```

The sink may be a security-sensitive business action.

---

# Security-Sensitive Business Sinks

Examples:

```text
Transfer money
Approve payment
Change email
Change password
Assign role
Reset MFA
Delete account
Invite administrator
Change ownership
Generate refund
Redeem voucher
Create API key
```

---

# Authentication Flow Analysis

Model:

```text
Credentials
    |
    v
Authentication Logic
    |
    v
Identity
    |
    v
Session / Token
```

Trace:

```text
Password verification
MFA verification
Session creation
JWT creation
OAuth callback
SAML assertion
Recovery flow
```

---

# JWT Flow

```text
Token
  |
  v
Parse
  |
  v
Signature Verification
  |
  v
Claims Validation
  |
  v
Identity
  |
  v
Authorisation
```

Do not stop at:

```text
JWT successfully verifies
```

Review:

```text
Issuer
Audience
Expiration
Algorithm
Key selection
Claims
Role mapping
Authorisation
```

---

# OAuth / OIDC Flow

```text
Authorization Response
         |
         v
Callback
         |
         v
state / nonce / PKCE
         |
         v
Token Exchange
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

---

# SAML Flow

```text
SAMLResponse
     |
     v
XML Parser
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

---

# Password Reset Flow

```text
Reset Request
     |
     v
Token Generation
     |
     v
URL Generation
     |
     v
Delivery
     |
     v
Token Validation
     |
     v
Password Change
```

Trace all attacker-influenced values including:

```text
Host headers
Email address
Reset token
User identifier
Redirect URL
```

---

# WebSocket Flow

```text
WebSocket Message
       |
       v
Message Parser
       |
       v
Message Handler
       |
       v
Authorisation
       |
       v
Sensitive Operation
```

Authentication at connection time does not necessarily provide per-message authorisation.

---

# GraphQL Flow

```text
GraphQL Argument
      |
      v
Resolver
      |
      v
Service
      |
      v
Authorisation
      |
      v
Database / Sink
```

Review:

```text
Resolver-level authorisation
Object-level authorisation
Field-level authorisation
Mutations
Subscriptions
Nested resolvers
```

---

# gRPC Flow

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
Service
     |
     v
Security-Sensitive Operation
```

Trace:

```text
Request fields
Metadata
Identity
Object IDs
Authorisation
Streaming messages
```

---

# Webhook Flow

```text
External Request
      |
      v
Webhook Endpoint
      |
      v
Signature Verification
      |
      v
Payload Processing
      |
      v
Sensitive Operation
```

The critical security control may be cryptographic authenticity rather than ordinary authentication.

---

# Queue Consumer Flow

```text
Queue Message
     |
     v
Consumer
     |
     v
Parser
     |
     v
Business Logic
     |
     v
Sink
```

Do not automatically trust internal queue messages.

Ask:

```text
Who can publish messages?

Can external input reach the queue?

Is message authenticity enforced?

Can another compromised service influence it?
```

---

# Background Job Flow

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
Dangerous Sink
```

This is a common second-order flow.

---

# Persistence Boundaries

A source-to-sink path may cross:

```text
Database
Cache
File
Queue
Object storage
Session
Message broker
```

Example:

```text
Attacker Input
      |
      v
Database
      |
      v
Later Worker
      |
      v
Template Engine
```

Do not assume the database makes input trusted.

---

# Trust Boundaries

Mark transitions such as:

```text
Internet
   |
   v
Reverse Proxy
   |
   v
Web Application
   |
   v
Internal API
   |
   v
Database
```

and:

```text
Browser
   |
   v
API
   |
   v
Queue
   |
   v
Worker
```

Data crossing an internal boundary may still be attacker-controlled.

---

# Trust Is Not Sanitisation

A common mistake:

```text
Data came from our database
        =
Trusted
```

Incorrect.

The database may contain attacker-controlled values.

Likewise:

```text
Internal API
Queue
Cache
Configuration service
```

can propagate attacker-controlled data.

---

# Multi-Stage Data Flow

Example:

```text
POST /profile
      |
      v
display_name
      |
      v
Database
      |
      v
GET /admin/users
      |
      v
Admin Template
      |
      v
Raw HTML Output
```

This may create:

```text
Stored XSS
```

The source and sink occur in different requests.

---

# Cross-Service Data Flow

Modern applications may involve:

```text
Service A
    |
    v
API
    |
    v
Service B
    |
    v
Queue
    |
    v
Service C
```

A single repository may show only part of the flow.

Document:

```text
Known Flow
Unknown Boundary
Expected Downstream Processing
```

Do not invent behaviour not supported by the available source.

---

# Source Classification

Classify sources.

| Source | Typical Trust |
|---|---|
| Query parameter | Untrusted |
| Request body | Untrusted |
| Route parameter | Untrusted |
| Header | Untrusted |
| Cookie | Untrusted |
| Uploaded file | Untrusted |
| Database field | Depends on origin |
| Environment variable | Configuration-dependent |
| Internal API | Depends on trust boundary |
| Queue message | Depends on producer |
| Hardcoded constant | Usually trusted |

---

# Sink Classification

Classify sinks by security impact.

| Sink | Potential Impact |
|---|---|
| SQL execution | SQL injection |
| Process execution | Command injection |
| HTTP client | SSRF |
| Filesystem read | Path traversal / file disclosure |
| Filesystem write | Arbitrary file write |
| Template evaluation | SSTI |
| HTML sink | XSS / HTML injection |
| Deserializer | Unsafe deserialisation |
| XML parser | XXE |
| LDAP query | LDAP injection |
| Redirect | Open redirect |
| Object lookup | IDOR / BOLA |
| Role update | Privilege escalation |

---

# Prioritising Sinks

A useful priority model:

```text
Critical Review Priority
    |
    +--> OS command execution
    +--> Dynamic code execution
    +--> Unsafe deserialisation
    +--> Raw SQL
    +--> Arbitrary file write
    +--> Template evaluation
```

Then:

```text
High Review Priority
    |
    +--> HTTP clients
    +--> Filesystem reads
    +--> XML parsers
    +--> LDAP queries
    +--> Sensitive object access
    +--> Role / permission changes
```

Priority is for review efficiency, not automatic severity.

---

# ripgrep Workflow

Use ripgrep for fast discovery.

General pattern:

```bash
rg -n -i 'pattern' .
```

---

# Find Command Execution Sinks

```bash
rg -n -i \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder|Process\.Start|os\.system|subprocess|child_process|exec\(|shell_exec|system\(' \
.
```

---

# Find HTTP Client Sinks

```bash
rg -n -i \
'HttpClient|RestTemplate|WebClient|requests\.(get|post|put|delete)|httpx\.|urllib|axios\.|fetch\(' \
.
```

---

# Find File Sinks

```bash
rg -n -i \
'File\.Read|File\.Write|Files\.read|Files\.write|open\(|readFile|writeFile|send_file|sendFile' \
.
```

---

# Find SQL Sinks

```bash
rg -n -i \
'executeQuery|executeUpdate|cursor\.execute|FromSqlRaw|ExecuteSqlRaw|createNativeQuery|raw\(|query\(' \
.
```

---

# Find Dynamic Execution

```bash
rg -n -i \
'eval\(|exec\(|Function\(|compile\(' \
.
```

---

# Find Deserialisation

```bash
rg -n -i \
'ObjectInputStream|pickle\.loads|pickle\.load|BinaryFormatter|yaml\.load|deserialize|unserialize' \
.
```

---

# Find Sources

```bash
rg -n -i \
'request\.args|request\.form|request\.json|request\.files|req\.query|req\.params|req\.body|Request\.Query|Request\.Form|Request\.Headers|@RequestParam|@PathVariable|@RequestBody' \
.
```

---

# ripgrep Is Discovery, Not Proof

```text
rg match
   |
   v
Candidate
   |
   v
Manual Trace
```

Never:

```text
rg match
   =
Vulnerability
```

---

# Semgrep / OpenGrep

Semgrep and OpenGrep can identify structural patterns.

Instead of:

```text
Find text containing exec
```

they can reason about code patterns.

Example conceptual rule:

```yaml
rules:
  - id: python-command-execution
    languages:
      - python
    message: Review process execution
    severity: WARNING
    patterns:
      - pattern-either:
          - pattern: os.system(...)
          - pattern: subprocess.$FUNC(...)
```

This still identifies a candidate sink rather than proving command injection.

---

# Taint Analysis

A stronger static-analysis rule can model:

```text
Source
   |
   v
Propagation
   |
   v
Sink
```

Conceptually:

```yaml
mode: taint

pattern-sources:
  - ...

pattern-sinks:
  - ...
```

This is closer to manual source-to-sink reasoning.

---

# CodeQL

CodeQL is useful when flows become more complex.

```text
Source
   |
   v
Function
   |
   v
Object
   |
   v
Service
   |
   v
Sink
```

CodeQL can perform:

```text
Local data flow
Global data flow
Taint tracking
Path queries
Semantic queries
Variant analysis
```

Use CodeQL when simple structural matching does not provide enough context.

---

# Static Analysis Tool Model

```text
ripgrep
   |
   v
Fast Pattern Discovery
   |
   v
Semgrep / OpenGrep
   |
   v
Structural / Taint Analysis
   |
   v
CodeQL
   |
   v
Deeper Semantic/Data-Flow Analysis
   |
   v
VS Code
   |
   v
Manual Validation
```

---

# Scanner Result Triage

For every static-analysis result ask:

```text
1. What is the source?

2. Is it attacker-controlled?

3. What is the sink?

4. Is the sink security-sensitive?

5. What transformations occur?

6. What validation occurs?

7. What sanitisation occurs?

8. What authentication is required?

9. What authorisation is required?

10. Is the path reachable?

11. Is the flow feasible?

12. What is the impact?
```

---

# Source-to-Sink Worksheet

Use a repeatable worksheet.

```text
Candidate:
STS-001

Entry Point:
POST /api/diagnostics

Source:
JSON field "host"

Source Location:
DiagnosticsController.java:42

Attacker Controlled:
Yes / No / Unknown

Transformations:
1.
2.
3.

Validation:
...

Sanitisation:
...

Authentication:
...

Authorisation:
...

Sink:
Runtime.exec()

Sink Location:
DiagnosticService.java:81

Flow:
DiagnosticsController
    -> DiagnosticService
    -> CommandBuilder
    -> Runtime.exec

Reachable:
Yes / No / Unknown

Runtime Preconditions:
...

Potential Impact:
...

Dynamic Validation:
...

Status:
Investigating / Confirmed / Rejected
```

---

# Draw the Flow

For complex findings, draw the complete flow.

Example:

```text
POST /api/diagnostics
          |
          v
DiagnosticsRequest.host
          |
          v
DiagnosticsController.run()
          |
          v
DiagnosticsService.ping()
          |
          v
CommandBuilder.build()
          |
          v
"ping " + host
          |
          v
Runtime.exec()
```

Then add controls:

```text
POST /api/diagnostics
          |
          v
Authentication
          |
          v
DiagnosticsRequest.host
          |
          v
Regex Validation
          |
          v
CommandBuilder
          |
          v
Runtime.exec()
```

This makes it easier to determine whether the validation actually breaks the dangerous flow.

---

# Security Control Inventory

During review, identify reusable controls.

Examples:

```text
InputValidator
UrlValidator
PathValidator
HtmlSanitizer
AuthorizationService
PermissionChecker
SafeCommandRunner
RepositoryBase
SecurityMiddleware
```

Then search for:

```text
Where is the control used?

Where is it not used?
```

---

# Missing-Control Analysis

Suppose the safe pattern is:

```text
Controller
    |
    v
checkOwnership()
    |
    v
repository.get()
```

Search for variants:

```text
Controller
    |
    v
repository.get()
```

without the expected ownership check.

This is especially powerful for:

```text
IDOR
BOLA
Privilege escalation
Tenant isolation
Administrative actions
```

---

# Variant Analysis

Once one vulnerability is confirmed:

```text
Confirmed Finding
      |
      v
Identify Root Cause
      |
      +--> Source
      +--> Sink
      +--> Missing Control
      +--> Unsafe Helper
      |
      v
Search Entire Repository
```

---

# Variant Analysis Example

Known vulnerable path:

```text
req.query.url
     |
     v
previewService.fetch()
     |
     v
axios.get()
```

Search for:

```text
previewService.fetch(
```

Then inspect every caller.

Also search for:

```text
axios.get
axios.post
fetch
HTTP wrappers
```

to find equivalent sinks.

---

# Wrapper Functions

Dangerous APIs are often wrapped.

Example:

```python
def run_process(command):
    return subprocess.run(
        command,
        shell=True
    )
```

Searching only:

```text
subprocess
```

finds the wrapper.

After that, the important sink becomes:

```text
run_process()
```

Search:

```bash
rg -n 'run_process\(' .
```

This can be more valuable than repeatedly searching the low-level API.

---

# HTTP Client Wrappers

Example:

```javascript
async function fetchRemote(url) {
    return axios.get(url);
}
```

After identifying this:

```text
axios.get
```

becomes:

```text
fetchRemote
```

for application-specific SSRF analysis.

---

# Database Wrappers

Example:

```java
public Result runQuery(
    String query
) {
    return jdbcTemplate.queryForList(query);
}
```

Now search:

```text
runQuery()
```

and trace its callers.

---

# File Wrappers

Example:

```csharp
public string ReadDocument(
    string path
) {
    return File.ReadAllText(path);
}
```

The application-specific sink becomes:

```text
ReadDocument()
```

---

# Source Wrappers

Sources can also be wrapped.

Example:

```python
def get_parameter(name):
    return request.args.get(name)
```

Searching only:

```text
request.args
```

finds the wrapper but may miss most real sources.

After discovering it, search:

```text
get_parameter(
```

---

# Framework Abstractions

Sources may be hidden behind:

```text
DTO binding
Dependency injection
Framework decorators
Annotations
Resolvers
Middleware
Base controllers
Request contexts
```

Example:

```java
public void update(
    @Valid UpdateUserRequest request
)
```

The request object itself contains attacker-controlled fields.

Trace individual properties:

```text
request.email
request.role
request.ownerId
```

---

# Validation Annotations

Annotations such as:

```text
@NotNull
@Size
@Pattern
[Required]
[StringLength]
RegularExpression
Pydantic constraints
Django validators
```

may provide useful validation.

But verify whether the validation addresses the sink.

Example:

```text
@Size(max=200)
```

does not automatically prevent:

```text
SQL injection
SSRF
Command injection
```

---

# Validation Placement

Correct validation should occur before dangerous interpretation.

Good conceptual flow:

```text
Source
  |
  v
Decode
  |
  v
Canonicalise
  |
  v
Validate
  |
  v
Sink
```

Potentially problematic:

```text
Source
  |
  v
Validate
  |
  v
Decode
  |
  v
Sink
```

because decoding may change the value after validation.

---

# Multiple Decoding

Review applications that perform:

```text
URL Decode
HTML Decode
Base64 Decode
Unicode Normalisation
JSON Decode
```

multiple times.

Flow:

```text
Encoded Input
     |
     v
Validation
     |
     v
Decode
     |
     v
Decode Again
     |
     v
Sink
```

This can invalidate earlier assumptions.

---

# Type Conversion

Type conversion can provide meaningful constraints.

Example:

```python
user_id =
    int(request.args["id"])
```

This strongly limits the input to an integer if conversion succeeds.

For SQL injection through that value, this may break the relevant dangerous flow.

But it does not automatically solve:

```text
IDOR
BOLA
Business logic
```

because an attacker can still choose another valid integer.

---

# Security Is Sink-Specific

The same validation can have different security meaning.

```text
Integer Conversion
```

may be strong protection against:

```text
SQL syntax injection
```

but irrelevant to:

```text
IDOR
```

This is why source-to-sink analysis must consider the intended sink and security property.

---

# Data-Flow Labels

When taking notes, label data.

Example:

```text
[A] attacker-controlled
[T] trusted
[V] validated
[S] sanitised
[E] encoded
[U] unknown
```

Then:

```text
[A] request.url
        |
        v
[A] target
        |
        v
[V] validateUrl(target)
        |
        v
[?] normalizedTarget
        |
        v
[?] httpClient.get()
```

This makes uncertain assumptions visible.

---

# Do Not Upgrade Unknown to Trusted

If you cannot determine the origin of a value:

```text
UNKNOWN
```

is the correct classification.

Do not silently assume:

```text
Trusted
```

or:

```text
Attacker-Controlled
```

without evidence.

---

# Dynamic Validation

Static analysis should guide controlled runtime testing.

```text
Source Code
    |
    v
Candidate Flow
    |
    v
Route Mapping
    |
    v
Burp Suite
    |
    v
Controlled Input
    |
    v
Observe Runtime Behaviour
```

---

# Burp Suite Workflow

```text
1. Identify route from source

2. Capture legitimate request

3. Send to Repeater

4. Identify mapped source parameter

5. Modify only the relevant input

6. Observe application behaviour

7. Compare with source expectations

8. Confirm or reject candidate
```

---

# Runtime Validation Questions

Ask:

```text
Does the request reach this route?

Does this code path execute?

Does the validation run?

Does the sink execute?

Is the source transformed differently at runtime?

Does middleware modify the input?

Does infrastructure block the request?

Does the framework provide hidden protection?
```

---

# Debugger-Assisted Validation

Where authorised and practical:

```text
Breakpoint at Source
       |
       v
Inspect Input
       |
       v
Step Through Transformations
       |
       v
Breakpoint at Sink
       |
       v
Inspect Final Value
```

This can provide extremely strong evidence.

---

# Example Debug Flow

```text
Request
  |
  v
Breakpoint:
Controller
  |
  v
host = "example"
  |
  v
Step Into:
CommandBuilder
  |
  v
command = "ping example"
  |
  v
Breakpoint:
Runtime.exec
```

This confirms actual runtime propagation.

---

# Unit Tests

Security-focused unit tests can validate assumptions.

Example:

```text
Given:
Untrusted URL

When:
validateUrl()

Then:
Internal destinations rejected
```

Tests are useful for understanding expected security behaviour.

But:

```text
Passing test
    !=
Complete security
```

The test may not cover bypass cases.

---

# Reporting Source-to-Sink Findings

A strong finding should describe the complete flow.

Avoid:

```text
The application uses Runtime.exec().
```

Prefer:

```text
The host parameter supplied to POST /api/diagnostics
is passed through DiagnosticsService and concatenated into
a command string that is subsequently supplied to Runtime.exec().
No effective validation preventing command interpretation was
identified along this execution path.
```

---

# Evidence

Include:

```text
Entry point
Source
Intermediate functions
Sink
Security controls
Relevant code locations
Runtime evidence
Impact
```

---

# Source Evidence

Example:

```text
File:
src/controllers/DiagnosticsController.java

Line:
42

Source:
@RequestParam String host
```

---

# Sink Evidence

```text
File:
src/services/DiagnosticService.java

Line:
81

Sink:
Runtime.getRuntime().exec(command)
```

---

# Flow Evidence

```text
DiagnosticsController.run()
        |
        v
DiagnosticsService.ping()
        |
        v
CommandBuilder.build()
        |
        v
Runtime.exec()
```

---

# Remediation Should Break the Dangerous Flow

A remediation should address the root cause.

For example:

```text
Attacker Input
     |
     v
Shell Command
```

could be redesigned to:

```text
Validated Host/IP
     |
     v
Non-Shell Network API
```

rather than attempting to blacklist shell metacharacters.

---

# Defence in Depth

Strong remediation may include:

```text
Safer API
        +
Strict Validation
        +
Least Privilege
        +
Authorisation
        +
Monitoring
```

Do not rely on one weak control where a safer design exists.

---

# Retesting

After remediation:

```text
Original Flow
     |
     v
Review Code Change
     |
     v
Verify Control
     |
     v
Runtime Retest
     |
     v
Variant Search
```

Also determine whether similar vulnerable paths remain elsewhere.

---

# Source-to-Sink Review Checklist

## Architecture

```text
[ ] Application architecture understood
[ ] Trust boundaries identified
[ ] External integrations identified
[ ] Background processing identified
[ ] Persistence boundaries identified
```

## Entry Points

```text
[ ] HTTP routes mapped
[ ] API endpoints mapped
[ ] GraphQL resolvers mapped
[ ] gRPC methods mapped
[ ] WebSocket handlers mapped
[ ] Webhooks mapped
[ ] Queue consumers mapped
[ ] Background jobs mapped
[ ] File imports mapped
```

## Sources

```text
[ ] Query parameters reviewed
[ ] Route parameters reviewed
[ ] Request bodies reviewed
[ ] Headers reviewed
[ ] Cookies reviewed
[ ] Uploaded files reviewed
[ ] Uploaded filenames reviewed
[ ] GraphQL arguments reviewed
[ ] gRPC fields reviewed
[ ] WebSocket messages reviewed
[ ] Stored user data considered
```

## Sinks

```text
[ ] SQL execution reviewed
[ ] NoSQL queries reviewed
[ ] LDAP queries reviewed
[ ] Command execution reviewed
[ ] Dynamic code execution reviewed
[ ] HTTP clients reviewed
[ ] Filesystem operations reviewed
[ ] Template evaluation reviewed
[ ] HTML sinks reviewed
[ ] XML parsers reviewed
[ ] Deserialisers reviewed
[ ] Redirects reviewed
[ ] Sensitive business actions reviewed
```

## Data Flow

```text
[ ] Assignments traced
[ ] Function arguments traced
[ ] Return values traced
[ ] Object properties traced
[ ] DTOs traced
[ ] Collections traced
[ ] Wrapper functions traced
[ ] Persistence boundaries considered
[ ] Cross-service boundaries considered
```

## Transformations

```text
[ ] Decoding reviewed
[ ] Encoding reviewed
[ ] Normalisation reviewed
[ ] Canonicalisation reviewed
[ ] Parsing reviewed
[ ] String manipulation reviewed
[ ] Type conversion reviewed
```

## Security Controls

```text
[ ] Input validation reviewed
[ ] Allowlisting reviewed
[ ] Sanitisation reviewed
[ ] Output encoding reviewed
[ ] Safe API usage reviewed
[ ] Authentication reviewed
[ ] Authorisation reviewed
[ ] Framework protections reviewed
[ ] Infrastructure controls considered
```

## Exploitability

```text
[ ] Code path reachable
[ ] Attacker control established
[ ] Security control effectiveness established
[ ] Runtime preconditions identified
[ ] Required privileges identified
[ ] Impact identified
[ ] Dynamic validation performed where appropriate
```

## Variant Analysis

```text
[ ] Dangerous wrapper identified
[ ] All wrapper callers reviewed
[ ] Equivalent sinks searched
[ ] Equivalent sources searched
[ ] Missing-control variants searched
[ ] Static-analysis rule considered
[ ] CodeQL query considered
```

---

# Quick Decision Tree

```text
Found a dangerous sink?
        |
        v
Can you identify its input?
        |
       Yes
        |
        v
Trace backwards
        |
        v
Does it reach attacker-controlled data?
        |
      +---+---+
      |       |
     No      Yes
      |       |
      v       v
 Lower      Review
Priority   Controls
              |
              v
      Effective Control?
          +---+---+
          |       |
         Yes      No
          |       |
          v       v
       Likely   Check
       Safe     Reachability
                  |
                  v
             Reachable?
              +---+---+
              |       |
             No      Yes
              |       |
              v       v
           Reject   Validate
                    Runtime
                       |
                       v
                    Impact
```

---

# Source-First Decision Tree

```text
Found attacker-controlled input?
        |
        v
Where does it go?
        |
        v
Is it transformed?
        |
        v
Is it validated?
        |
        v
Does it reach a sensitive operation?
        |
      +---+---+
      |       |
     No      Yes
      |       |
      v       v
 Continue   Review
 Tracing    Context
              |
              v
      Is protection effective?
              |
          +---+---+
          |       |
         Yes      No
          |       |
          v       v
        Safe    Candidate
                   |
                   v
             Runtime Validation
```

---

# Final Source-to-Sink Model

The complete security model is:

```text
                     ENTRY POINT
                          |
                          v
                        SOURCE
                          |
                          v
                ATTACKER CONTROL?
                          |
                     +----+----+
                     |         |
                    No        Yes
                     |         |
                     v         v
               Lower Priority  PROPAGATION
                               |
                 +-------------+-------------+
                 |             |             |
                 v             v             v
             Variables      Functions      Objects
                 |             |             |
                 +-------------+-------------+
                               |
                               v
                        TRANSFORMATIONS
                               |
                +--------------+--------------+
                |              |              |
                v              v              v
             Decode        Normalize       Parse
                |              |              |
                +--------------+--------------+
                               |
                               v
                        SECURITY CONTROL
                               |
                +--------------+--------------+
                |              |              |
                v              v              v
           Validation     Sanitisation   Authorisation
                |              |              |
                +--------------+--------------+
                               |
                               v
                             SINK
                               |
                               v
                     SECURITY-SENSITIVE?
                               |
                          +----+----+
                          |         |
                         No        Yes
                          |         |
                          v         v
                    Lower Priority REACHABLE?
                                     |
                                +----+----+
                                |         |
                               No        Yes
                                |         |
                                v         v
                             Reject   RUNTIME
                                      VALIDATION
                                          |
                                          v
                                        IMPACT
                                          |
                                          v
                                  CONFIRMED FINDING
                                          |
                                          v
                                   VARIANT ANALYSIS
```

The core rule is:

```text
SOURCE
   +
FLOW
   +
SINK
```

is still not enough.

A meaningful vulnerability normally requires:

```text
Attacker-Controlled Source
          +
Feasible Data Flow
          +
Reachable Security-Sensitive Sink
          +
Absent or Ineffective Security Control
          +
Security Impact
```

---

# Practical Testing Model

When reviewing any potential source-to-sink vulnerability, answer these questions:

```text
1. Where does the data enter?

2. Who controls it?

3. What transformations occur?

4. Where is it validated?

5. Where is it sanitised?

6. Where is it encoded?

7. Which functions receive it?

8. Which objects store it?

9. Does it cross a persistence boundary?

10. Does it cross a trust boundary?

11. Which security-sensitive sink receives it?

12. Is the sink reachable?

13. What authentication is required?

14. What authorisation is required?

15. Are the controls appropriate for this sink?

16. Can runtime behaviour confirm the flow?

17. What security impact results?

18. Are there similar variants elsewhere?
```

If those questions can be answered, the source-to-sink path is understood.

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
```

---

# References

## OWASP Secure Code Review Cheat Sheet

[OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP Static Code Analysis

[OWASP Static Code Analysis](https://owasp.org/www-community/controls/Static_Code_Analysis){ target="_blank" rel="noopener noreferrer" }

## OWASP Input Validation Cheat Sheet

[OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Authorization Cheat Sheet

[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Injection Prevention Cheat Sheet

[OWASP Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP SQL Injection Prevention Cheat Sheet

[OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP OS Command Injection Defense Cheat Sheet

[OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP SSRF Prevention Cheat Sheet

[OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP File Upload Cheat Sheet

[OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Deserialization Cheat Sheet

[OWASP Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP XSS Prevention Cheat Sheet

[OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## PortSwigger Web Security Academy

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

## Semgrep Documentation

[docs](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

## OpenGrep

[OpenGrep](https://opengrep.dev/){ target="_blank" rel="noopener noreferrer" }

## CodeQL Documentation

[docs](https://codeql.github.com/docs/){ target="_blank" rel="noopener noreferrer" }

## CodeQL Data Flow Analysis

[CodeQL Data Flow Analysis](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/){ target="_blank" rel="noopener noreferrer" }

## Visual Studio Code

[Visual Studio Code](https://code.visualstudio.com/docs){ target="_blank" rel="noopener noreferrer" }

## ripgrep

[ripgrep](https://github.com/BurntSushi/ripgrep){ target="_blank" rel="noopener noreferrer" }

---

# Summary

Source-to-sink analysis can be reduced to one question:

```text
Can attacker-controlled data reach a security-sensitive operation
through a feasible path without an effective security control?
```

The practical workflow is:

```text
Map Entry Points
      |
      v
Identify Sources
      |
      v
Identify Sinks
      |
      v
Trace Forward
      |
      v
Trace Backwards
      |
      v
Map Transformations
      |
      v
Review Security Controls
      |
      v
Establish Reachability
      |
      v
Establish Attacker Control
      |
      v
Validate Runtime Behaviour
      |
      v
Determine Impact
      |
      v
Confirm Finding
      |
      v
Search for Variants
```

The final rule remains:

```text
Sink found
    !=
Vulnerability found

Source reaches sink
    !=
Vulnerability automatically confirmed

Attacker-controlled source
    +
feasible flow
    +
security-sensitive sink
    +
ineffective controls
    +
security impact
    =
meaningful security finding
```
