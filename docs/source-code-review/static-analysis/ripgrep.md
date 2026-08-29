# ripgrep for Security Source Code Review

`ripgrep` (`rg`) is one of the most useful tools for manual security source code review.

It provides extremely fast recursive searching across source repositories and supports:

```text
Literal searches
Regular expressions
File-type filtering
Directory exclusions
Context lines
Case-insensitive searches
Multiple patterns
Machine-readable output
```

For security review, `ripgrep` is particularly useful for locating:

```text
Routes and endpoints
User-controlled input
Authentication
Authorisation
Database queries
Operating system commands
File operations
Outbound HTTP requests
Template rendering
Deserialisation
XML parsing
Redirects
Secrets
Cryptographic operations
Security configuration
GraphQL
gRPC
WebSockets
Background jobs
Message queues
```

The fundamental workflow is:

```text
Repository
    |
    v
Identify Technology
    |
    v
Search Entry Points
    |
    v
Search Sources
    |
    v
Search Security Controls
    |
    v
Search Dangerous Sinks
    |
    v
Open Candidate in VS Code
    |
    v
Trace Source -> Sink
    |
    v
Determine Exploitability
```

!!! warning "Authorised Security Testing"
    Use these techniques only against source code, applications and environments for which you have explicit authorisation. A search result is a review candidate, not proof of a vulnerability.

---

# Core Principle

The most important rule when using `ripgrep` is:

```text
rg match
   !=
vulnerability
```

For example:

```bash
rg -n 'ProcessBuilder' .
```

may identify:

```java
new ProcessBuilder(
    "/usr/bin/convert",
    inputFile,
    outputFile
);
```

The presence of `ProcessBuilder` does not automatically prove command injection.

You must determine:

```text
Can an attacker control the executable?

Can an attacker control arguments?

Is a shell involved?

Can argument injection occur?

Is the path attacker-controlled?

What program is being invoked?

What does the invoked program do with its arguments?
```

Similarly:

```text
HttpClient
    !=
SSRF

createNativeQuery
    !=
SQL Injection

innerHTML
    !=
XSS

ObjectInputStream
    !=
Exploitable Deserialisation
```

`ripgrep` finds interesting code.

The reviewer determines whether it is vulnerable.

---

# Installation

## Debian / Ubuntu / Kali Linux

```bash
sudo apt update
sudo apt install ripgrep
```

Verify:

```bash
rg --version
```

---

# Basic Usage

Search recursively:

```bash
rg 'password' .
```

Show line numbers:

```bash
rg -n 'password' .
```

Case-insensitive:

```bash
rg -ni 'password' .
```

Show filenames only:

```bash
rg -l 'password' .
```

Count matches per file:

```bash
rg -c 'password' .
```

Fixed-string search:

```bash
rg -F 'Runtime.getRuntime().exec' .
```

---

# Search Multiple Patterns

Use regex alternation:

```bash
rg -n \
'password|secret|token|api_key' \
.
```

Or multiple `-e` expressions:

```bash
rg -n \
-e 'password' \
-e 'secret' \
-e 'token' \
.
```

---

# Context Lines

Show three lines before and after:

```bash
rg -n -C 3 'ProcessBuilder' .
```

Before:

```bash
rg -n -B 5 'ProcessBuilder' .
```

After:

```bash
rg -n -A 5 'ProcessBuilder' .
```

This is useful when reviewing:

```text
Sources
Validation
Function arguments
Security controls
```

---

# File Filtering

Search Java only:

```bash
rg -n 'ProcessBuilder' \
-g '*.java' \
.
```

C#:

```bash
rg -n 'Process.Start' \
-g '*.cs' \
.
```

PHP:

```bash
rg -n 'shell_exec' \
-g '*.php' \
.
```

Python:

```bash
rg -n 'subprocess' \
-g '*.py' \
.
```

JavaScript and TypeScript:

```bash
rg -n 'child_process' \
-g '*.js' \
-g '*.ts' \
-g '*.jsx' \
-g '*.tsx' \
.
```

---

# Excluding Noise

Large repositories often contain:

```text
node_modules
vendor
target
build
dist
bin
obj
coverage
generated files
```

Exclude them:

```bash
rg -n \
'password' \
. \
-g '!node_modules/**' \
-g '!vendor/**' \
-g '!target/**' \
-g '!build/**' \
-g '!dist/**' \
-g '!bin/**' \
-g '!obj/**'
```

---

# Recommended `.rgignore`

For repeated source review, create:

```text
.rgignore
```

Example:

```text
node_modules/
vendor/
target/
build/
dist/
bin/
obj/
coverage/
.next/
.nuxt/
```

Be careful with exclusions.

Do not hide security-relevant:

```text
Configuration
Templates
Deployment files
Generated API code
Custom vendored code
```

without first understanding the repository.

---

# Hidden Files

By default, hidden files are generally skipped.

Include them with:

```bash
rg --hidden 'secret' .
```

This can be important for:

```text
.env
.github/
.gitlab/
Docker configuration
CI/CD configuration
```

Avoid blindly searching `.git` internals unless Git history analysis is intentionally required.

Example:

```bash
rg --hidden \
-g '!.git/**' \
'secret' \
.
```

---

# List Files

List files `rg` considers searchable:

```bash
rg --files
```

Java files:

```bash
rg --files -g '*.java'
```

Configuration:

```bash
rg --files | grep -Ei \
'application|config|settings|security|docker|compose|nginx'
```

---

# Visual Studio Code Workflow

A practical workflow is:

```text
Terminal
   |
   v
rg search
   |
   v
Candidate File
   |
   v
Open in VS Code
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
Trace Data Flow
```

Open the current repository:

```bash
code .
```

Open a specific file:

```bash
code src/main/java/example/UserController.java
```

Open at a line where supported by the VS Code CLI:

```bash
code -g src/main/java/example/UserController.java:84
```

---

# Security Review Strategy

Do not begin with one enormous regex.

Perform separate passes:

```text
1. Repository reconnaissance
2. Route discovery
3. Source discovery
4. Authentication
5. Authorisation
6. Input validation
7. Database sinks
8. Command execution
9. SSRF
10. Files
11. Uploads
12. XML
13. Deserialisation
14. Templates
15. XSS
16. Redirects
17. Host/proxy handling
18. Secrets
19. Cryptography
20. Logging
21. Background processing
22. APIs
23. Dependencies
24. Variant analysis
```

---

# Repository Reconnaissance

Start with:

```bash
rg --files
```

Find common project manifests:

```bash
rg --files | grep -E \
'(^|/)(pom\.xml|build\.gradle|build\.gradle\.kts|package\.json|composer\.json|requirements\.txt|pyproject\.toml|.*\.csproj|.*\.sln)$'
```

Find configuration:

```bash
rg --files | grep -Ei \
'application\.(yml|yaml|properties)|appsettings.*\.json|settings\.py|\.env|docker|compose|nginx|apache|security|config'
```

---

# Identify Frameworks

Search dependency manifests:

```bash
rg -ni \
'spring-boot|spring-security|django|flask|express|aspnetcore|laravel|symfony|fastapi' \
.
```

This provides clues about which source and sink searches should be prioritised.

---

# Search TODO and Security Comments

```bash
rg -ni \
'TODO|FIXME|HACK|XXX|temporary|workaround|bypass|remove before production' \
.
```

These are not vulnerabilities.

They can identify high-value review areas.

Search security-related comments:

```bash
rg -ni \
'security|sanitize|sanitise|validate|trusted|permission|admin|authori[sz]e|authentication' \
.
```

Never trust a comment without inspecting the implementation.

---

# Route Discovery

Routes define much of the externally reachable attack surface.

---

# Java / Spring Routes

```bash
rg -n \
'@(RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RestController|Controller)\b' \
-g '*.java' \
.
```

Search functional WebFlux routes:

```bash
rg -n \
'RouterFunction|RouterFunctions\.route|\bGET\(|\bPOST\(|\bPUT\(|\bPATCH\(|\bDELETE\(' \
-g '*.java' \
.
```

Servlet/JAX-RS style:

```bash
rg -n \
'@WebServlet|@Path|@GET\b|@POST\b|@PUT\b|@PATCH\b|@DELETE\b' \
-g '*.java' \
.
```

Remember that Spring paths can be composed from:

```text
Class-level @RequestMapping
        +
Method-level @GetMapping
```

So a match may not contain the complete URL.

---

# .NET / ASP.NET Core Routes

```bash
rg -n \
'\[(Route|HttpGet|HttpPost|HttpPut|HttpPatch|HttpDelete|HttpHead|HttpOptions)' \
-g '*.cs' \
.
```

Minimal APIs:

```bash
rg -n \
'\.(MapGet|MapPost|MapPut|MapPatch|MapDelete|MapMethods|MapGroup)\(' \
-g '*.cs' \
.
```

Controllers:

```bash
rg -n \
'ControllerBase|Controller\b|\[ApiController\]' \
-g '*.cs' \
.
```

---

# PHP Routes

Framework-specific route definitions commonly include patterns such as:

```bash
rg -n \
'Route::(get|post|put|patch|delete|any|match)|->addRoute|->map\(' \
-g '*.php' \
.
```

Also inspect:

```text
routes/
controllers/
public/index.php
```

---

# Django Routes

```bash
rg -n \
'\bpath\(|\bre_path\(|\binclude\(' \
-g '*.py' \
.
```

Search views:

```bash
rg -n \
'def .*request|class .*View|APIView|ViewSet|ModelViewSet' \
-g '*.py' \
.
```

---

# Flask Routes

```bash
rg -n \
'@(app|[A-Za-z_][A-Za-z0-9_]*)\.route\(' \
-g '*.py' \
.
```

Also:

```bash
rg -n \
'add_url_rule\(' \
-g '*.py' \
.
```

---

# Node.js / Express Routes

```bash
rg -n \
'\b(app|router)\.(get|post|put|patch|delete|options|head|all)\(' \
-g '*.js' \
-g '*.ts' \
.
```

Search router mounting:

```bash
rg -n \
'\bapp\.use\(|\brouter\.use\(' \
-g '*.js' \
-g '*.ts' \
.
```

A complete route may be composed from:

```text
app.use("/api", router)
        +
router.get("/users/:id")
```

Result:

```text
/api/users/:id
```

---

# Route Inventory

Record results as:

| Method | Route | Handler | Auth | Authz | Input |
|---|---|---|---|---|---|
| GET | `/users/{id}` | `getUser` | Yes | Review | Path |
| POST | `/upload` | `upload` | Yes | User | File |
| POST | `/login` | `login` | No | N/A | Body |
| GET | `/fetch` | `fetch` | Yes | Review | URL |

This transforms search results into an attack-surface model.

---

# Source Discovery

A source is where potentially attacker-controlled data enters the application.

---

# Java / Spring Sources

```bash
rg -n \
'@RequestParam|@PathVariable|@RequestBody|@RequestHeader|@CookieValue|MultipartFile' \
-g '*.java' \
.
```

Servlet sources:

```bash
rg -n \
'getParameter\(|getParameterValues\(|getParameterMap\(|getHeader\(|getHeaders\(|getCookies\(|getInputStream\(|getReader\(|getRequestURI\(|getQueryString\(|getServerName\(' \
-g '*.java' \
.
```

---

# .NET Sources

```bash
rg -n \
'Request\.(Query|Form|Headers|Cookies|Body)|\[From(Query|Route|Body|Header|Form)\]|RouteData|HttpContext\.Request' \
-g '*.cs' \
.
```

File uploads:

```bash
rg -n \
'IFormFile|IFormFileCollection|Request\.Form\.Files' \
-g '*.cs' \
.
```

---

# PHP Sources

```bash
rg -n \
'\$_GET|\$_POST|\$_REQUEST|\$_COOKIE|\$_FILES|\$_SERVER' \
-g '*.php' \
.
```

Input stream:

```bash
rg -n \
'php://input|filter_input\(' \
-g '*.php' \
.
```

---

# Django Sources

```bash
rg -n \
'request\.(GET|POST|FILES|COOKIES|headers|body|META)' \
-g '*.py' \
.
```

Django REST Framework:

```bash
rg -n \
'request\.(data|query_params|FILES|auth|user)' \
-g '*.py' \
.
```

---

# Flask Sources

```bash
rg -n \
'request\.(args|form|json|files|headers|cookies|data|values)|request\.get_json\(' \
-g '*.py' \
.
```

---

# Node.js / Express Sources

```bash
rg -n \
'req\.(query|params|body|headers|cookies|signedCookies|file|files)' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Browser JavaScript Sources

```bash
rg -n \
'location\.(href|search|hash)|document\.(URL|documentURI|referrer)|window\.name|localStorage|sessionStorage|postMessage|message\.data|event\.data' \
-g '*.js' \
-g '*.ts' \
-g '*.jsx' \
-g '*.tsx' \
.
```

---

# Authentication Discovery

Search generally:

```bash
rg -ni \
'login|logout|authenticate|authentication|credential|password|session|jwt|bearer|oauth|oidc|saml|mfa|totp|otp' \
.
```

---

# Java / Spring Authentication

```bash
rg -n \
'SecurityFilterChain|HttpSecurity|AuthenticationManager|AuthenticationProvider|UserDetailsService|PasswordEncoder|UsernamePasswordAuthenticationFilter|OncePerRequestFilter|oauth2Login|oauth2ResourceServer|saml2Login' \
-g '*.java' \
.
```

---

# .NET Authentication

```bash
rg -n \
'AddAuthentication|UseAuthentication|AddJwtBearer|AddCookie|SignInAsync|SignOutAsync|ClaimsPrincipal|PasswordHasher|AddOpenIdConnect|AddOAuth' \
-g '*.cs' \
.
```

---

# Django Authentication

```bash
rg -n \
'authenticate\(|login\(|logout\(|login_required|AUTHENTICATION_BACKENDS|AuthenticationMiddleware' \
-g '*.py' \
.
```

---

# Flask Authentication

```bash
rg -n \
'login_user|logout_user|login_required|LoginManager|current_user|check_password_hash|generate_password_hash' \
-g '*.py' \
.
```

---

# Node.js Authentication

```bash
rg -n \
'passport|jsonwebtoken|jwt\.verify|jwt\.sign|bcrypt|argon2|express-session|cookie-session|req\.user|isAuthenticated' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Authorisation Discovery

Search:

```bash
rg -ni \
'authori[sz]e|permission|role|policy|access.?control|isAdmin|is_admin|ownership|tenant|hasRole|hasAuthority' \
.
```

---

# Java / Spring Authorisation

```bash
rg -n \
'authorizeHttpRequests|requestMatchers|permitAll|authenticated|hasRole|hasAuthority|@PreAuthorize|@PostAuthorize|@Secured|@RolesAllowed|@EnableMethodSecurity' \
-g '*.java' \
.
```

Pay special attention to:

```text
permitAll()
```

Search:

```bash
rg -n \
'permitAll\(' \
-g '*.java' \
.
```

A `permitAll()` match is not automatically a vulnerability.

Determine which routes it affects.

---

# .NET Authorisation

```bash
rg -n \
'\[Authorize|\[AllowAnonymous|AddAuthorization|RequireAuthorization|RequireRole|RequireClaim|AuthorizationPolicy|IAuthorizationHandler' \
-g '*.cs' \
.
```

---

# Django Authorisation

```bash
rg -n \
'permission_required|user_passes_test|has_perm|has_perms|PermissionRequiredMixin|UserPassesTestMixin|IsAdminUser|IsAuthenticated|permission_classes' \
-g '*.py' \
.
```

---

# Flask Authorisation

Flask applications often implement custom authorisation.

Search:

```bash
rg -ni \
'permission|role|admin|authori[sz]|current_user|owner|tenant' \
-g '*.py' \
.
```

---

# Node.js Authorisation

```bash
rg -ni \
'permission|role|isAdmin|authorize|authorise|owner|tenant|req\.user' \
-g '*.js' \
-g '*.ts' \
.
```

---

# IDOR / BOLA Candidates

Search object lookups.

## Java

```bash
rg -n \
'findById\(|getReferenceById\(|getById\(|findOne\(' \
-g '*.java' \
.
```

## .NET

```bash
rg -n \
'FindAsync\(|Find\(|FirstOrDefaultAsync|SingleOrDefaultAsync|FirstAsync|SingleAsync' \
-g '*.cs' \
.
```

## Django

```bash
rg -n \
'\.objects\.(get|filter)|get_object_or_404|get_queryset' \
-g '*.py' \
.
```

## Node.js

```bash
rg -n \
'findById|findOne|findUnique|findFirst|findByPk' \
-g '*.js' \
-g '*.ts' \
.
```

Then ask:

```text
Where is ownership checked?

Where is tenant isolation enforced?

Where is permission checked?
```

The lookup itself is not the vulnerability.

---

# Input Validation

Search:

```bash
rg -ni \
'validate|validator|sanitize|sanitise|schema|allowlist|whitelist|regex|pattern|constraint' \
.
```

---

# Java Validation

```bash
rg -n \
'@Valid|@Validated|@NotNull|@NotBlank|@NotEmpty|@Size|@Pattern|@Email|ConstraintValidator' \
-g '*.java' \
.
```

---

# .NET Validation

```bash
rg -n \
'\[Required|\[StringLength|\[MaxLength|\[MinLength|\[RegularExpression|ModelState\.IsValid|FluentValidation|AbstractValidator' \
-g '*.cs' \
.
```

---

# Django Validation

```bash
rg -n \
'clean\(|clean_[A-Za-z0-9_]+\(|validators|is_valid\(|Serializer|Form\b|ModelForm' \
-g '*.py' \
.
```

---

# Flask Validation

```bash
rg -ni \
'validate|validator|marshmallow|pydantic|wtforms|schema' \
-g '*.py' \
.
```

---

# Node.js Validation

```bash
rg -n \
'joi|zod|express-validator|ajv|yup|validator\.|validate\(' \
-g '*.js' \
-g '*.ts' \
.
```

Validation is not automatically equivalent to:

```text
SQL parameterisation
Output encoding
Authorisation
Command safety
```

---

# SQL Injection Candidates

---

# Java JDBC

```bash
rg -n \
'Statement|PreparedStatement|executeQuery\(|executeUpdate\(|execute\(' \
-g '*.java' \
.
```

Focus particularly on:

```text
Statement
String concatenation
Dynamic SQL fragments
```

---

# Java JPA / Hibernate

```bash
rg -n \
'createQuery\(|createNativeQuery\(|Session\.createQuery|@Query|nativeQuery\s*=\s*true' \
-g '*.java' \
.
```

Spring JDBC:

```bash
rg -n \
'JdbcTemplate|NamedParameterJdbcTemplate|queryForObject\(|queryForList\(|update\(' \
-g '*.java' \
.
```

These APIs can be used safely or unsafely.

Inspect how the query is built and how parameters are bound.

---

# .NET SQL

```bash
rg -n \
'SqlCommand|DbCommand|FromSqlRaw|ExecuteSqlRaw|SqlQueryRaw|FromSqlInterpolated|ExecuteSqlInterpolated|QueryAsync|ExecuteAsync' \
-g '*.cs' \
.
```

Look for string construction:

```bash
rg -n \
'\$".*(SELECT|INSERT|UPDATE|DELETE)|string\.Format\(.*(SELECT|INSERT|UPDATE|DELETE)|\+.*(SELECT|INSERT|UPDATE|DELETE)' \
-g '*.cs' \
.
```

Review manually because multiline construction can evade simple regexes.

---

# PHP SQL

```bash
rg -n \
'mysqli_query\(|mysqli_real_query\(|->query\(|->exec\(|->prepare\(' \
-g '*.php' \
.
```

Search SQL strings:

```bash
rg -ni \
'SELECT .*FROM|INSERT INTO|UPDATE .* SET|DELETE FROM' \
-g '*.php' \
.
```

---

# Django SQL

```bash
rg -n \
'\.raw\(|RawSQL\(|\.extra\(|cursor\.execute\(|cursor\.executemany\(' \
-g '*.py' \
.
```

Normal ORM queries are not automatically immune to every injection-style problem, but raw SQL and dynamic query construction deserve additional attention.

---

# Flask / Python SQL

```bash
rg -n \
'cursor\.execute\(|cursor\.executemany\(|text\(|execute\(|executemany\(' \
-g '*.py' \
.
```

Look for interpolation:

```bash
rg -n \
'f["'\''].*(SELECT|INSERT|UPDATE|DELETE)|\.format\(.*|%s.*%' \
-g '*.py' \
.
```

Expect false positives.

---

# Node.js SQL

```bash
rg -n \
'\.query\(|\.execute\(|\$queryRaw|\$executeRaw|sequelize\.query|knex\.raw' \
-g '*.js' \
-g '*.ts' \
.
```

Prisma raw APIs deserve review, particularly unsafe raw query construction.

---

# NoSQL Injection Candidates

---

# Java / MongoDB

```bash
rg -n \
'MongoTemplate|BasicQuery|Document\.parse|Criteria\.where|MongoCollection|Filters\.' \
-g '*.java' \
.
```

Look for attacker-controlled:

```text
Raw JSON
Mongo operators
Query documents
Field names
Operators
```

---

# Python / MongoDB

```bash
rg -n \
'find_one\(|find\(|update_one\(|update_many\(|delete_one\(|delete_many\(|aggregate\(' \
-g '*.py' \
.
```

---

# Node.js / MongoDB

```bash
rg -n \
'findOne\(|find\(|findById\(|updateOne\(|updateMany\(|deleteOne\(|aggregate\(' \
-g '*.js' \
-g '*.ts' \
.
```

Look for:

```text
req.body passed directly into query objects
Raw operators
$where
$regex
$ne
$gt
$where
```

Search:

```bash
rg -n \
'\$(where|ne|gt|gte|lt|lte|regex|in|nin|or|and)' \
-g '*.js' \
-g '*.ts' \
-g '*.json' \
.
```

---

# LDAP Injection Candidates

---

# Java

```bash
rg -n \
'LdapTemplate|DirContext|InitialDirContext|SearchControls|\.search\(' \
-g '*.java' \
.
```

Search LDAP filters:

```bash
rg -n \
'\(&|\(\||\(uid=|\(cn=|\(mail=|\(objectClass=' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'DirectorySearcher|DirectoryEntry|System\.DirectoryServices|SearchRoot|Filter\s*=' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'ldap_search\(|ldap_list\(|ldap_read\(|ldap_bind\(' \
-g '*.php' \
.
```

---

# Python

```bash
rg -n \
'ldap\.search|search_s\(|search_ext|ldap3|search_filter' \
-g '*.py' \
.
```

Always inspect filter construction and escaping.

---

# Command Injection Candidates

---

# Java

```bash
rg -n \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder|ProcessHandle' \
-g '*.java' \
.
```

Shell invocation:

```bash
rg -n \
'/bin/sh|/bin/bash|bash|sh -c|cmd\.exe|cmd /c|powershell|pwsh' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'Process\.Start|ProcessStartInfo|System\.Diagnostics\.Process' \
-g '*.cs' \
.
```

Shell invocation:

```bash
rg -ni \
'cmd\.exe|/c|powershell|pwsh|/bin/sh|bash' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'\b(system|exec|shell_exec|passthru|popen|proc_open|pcntl_exec)\s*\(' \
-g '*.php' \
.
```

Backticks can also execute commands in PHP and may require manual review.

---

# Python

```bash
rg -n \
'os\.system\(|os\.popen\(|subprocess\.(run|Popen|call|check_call|check_output|getoutput|getstatusoutput)\(' \
-g '*.py' \
.
```

High-interest shell use:

```bash
rg -n \
'shell\s*=\s*True' \
-g '*.py' \
.
```

---

# Node.js

```bash
rg -n \
'child_process|exec\(|execSync\(|execFile\(|execFileSync\(|spawn\(|spawnSync\(' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Dynamic Code Execution

Search:

```bash
rg -n \
'\beval\(|\bexec\(|new Function|Function\(|ScriptEngine|GroovyShell|CSharpScript|CodeDomProvider|compile\(' \
.
```

Interpret matches according to language.

For example:

```text
Python exec()
```

and:

```text
PHP exec()
```

are completely different security sinks.

Language-specific searches are preferable.

---

# Java Dynamic Execution

```bash
rg -n \
'ScriptEngine|ScriptEngineManager|GroovyShell|Class\.forName|Method\.invoke|SpelExpressionParser|parseExpression' \
-g '*.java' \
.
```

Reflection is not automatically unsafe.

Determine whether attacker-controlled data selects:

```text
Classes
Methods
Expressions
Scripts
```

---

# Python Dynamic Execution

```bash
rg -n \
'\beval\(|\bexec\(|compile\(' \
-g '*.py' \
.
```

---

# JavaScript Dynamic Execution

```bash
rg -n \
'\beval\(|new Function|Function\(|setTimeout\(|setInterval\(|vm\.runIn|vm\.runInNewContext|vm\.runInThisContext' \
-g '*.js' \
-g '*.ts' \
.
```

String-based timers deserve more attention than function callbacks.

---

# SSTI and Expression Injection

---

# Java / Spring

```bash
rg -n \
'SpelExpressionParser|parseExpression|Expression\.getValue|FreeMarker|Velocity|Thymeleaf|Pebble|TemplateEngine|process\(' \
-g '*.java' \
.
```

Search dynamic view names:

```bash
rg -n \
'return\s+["'\'']redirect:|return\s+.*view|ModelAndView|setViewName' \
-g '*.java' \
.
```

Manual context is essential.

---

# Flask / Jinja

```bash
rg -n \
'render_template_string\(|Environment\(|Template\(|from_string\(' \
-g '*.py' \
.
```

Normal:

```text
render_template("page.html", value=user_input)
```

does not mean SSTI merely because user input reaches template data.

Focus on attacker influence over:

```text
Template source
Template expression
Dynamic template construction
```

---

# PHP Templates

Search framework/template-specific functions:

```bash
rg -ni \
'twig|blade|smarty|template|render' \
-g '*.php' \
.
```

---

# SSRF Candidates

---

# Java

```bash
rg -n \
'java\.net\.URL|new URL\(|URI\.create|URLConnection|openConnection\(|HttpClient|HttpRequest|RestTemplate|RestClient|WebClient|OkHttpClient|CloseableHttpClient' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'HttpClient|WebClient|WebRequest|HttpWebRequest|RestClient|SendAsync|GetAsync|GetStringAsync' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'curl_init\(|curl_setopt\(|curl_exec\(|file_get_contents\(|fopen\(' \
-g '*.php' \
.
```

Remember that file APIs may support URLs depending on configuration and usage.

---

# Python

```bash
rg -n \
'requests\.(get|post|put|patch|delete|request)|httpx\.(get|post|put|patch|delete|request)|urlopen\(|urllib\.request|aiohttp|ClientSession' \
-g '*.py' \
.
```

---

# Node.js

```bash
rg -n \
'axios\.|fetch\(|http\.request|https\.request|http\.get|https\.get|got\(|request\(' \
-g '*.js' \
-g '*.ts' \
.
```

For every candidate examine:

```text
URL source
Scheme validation
Host validation
Port validation
DNS resolution
Redirects
Internal networks
Cloud metadata
Egress controls
```

---

# Path Traversal Candidates

---

# Java

```bash
rg -n \
'new File\(|Paths\.get\(|Path\.of\(|\.resolve\(|Files\.(read|write|copy|move|delete)|FileInputStream|FileOutputStream' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'Path\.(Combine|Join|GetFullPath)|File\.(Open|Read|Write|Delete|Move|Copy)|Directory\.' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'file_get_contents\(|file_put_contents\(|fopen\(|readfile\(|unlink\(|rename\(|copy\(' \
-g '*.php' \
.
```

---

# Python

```bash
rg -n \
'\bopen\(|Path\(|pathlib|os\.path\.(join|abspath|realpath)|send_file\(|send_from_directory\(' \
-g '*.py' \
.
```

---

# Node.js

```bash
rg -n \
'fs\.(readFile|readFileSync|writeFile|writeFileSync|createReadStream|createWriteStream|unlink|rename)|path\.(join|resolve|normalize)' \
-g '*.js' \
-g '*.ts' \
.
```

Do not assume:

```text
Path.resolve()
Path.Combine()
Path.join()
```

provides containment.

Review the final normalized/canonical path and base-directory boundary.

---

# File Inclusion Candidates

PHP is particularly relevant:

```bash
rg -n \
'\b(include|include_once|require|require_once)\s*\(' \
-g '*.php' \
.
```

Trace whether attacker-controlled data influences the included path.

---

# File Upload Candidates

---

# Java

```bash
rg -n \
'MultipartFile|getOriginalFilename\(|transferTo\(|getInputStream\(' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'IFormFile|CopyToAsync|CopyTo\(|FileName|OpenReadStream' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'\$_FILES|move_uploaded_file\(|is_uploaded_file\(' \
-g '*.php' \
.
```

---

# Django / Flask

```bash
rg -n \
'request\.FILES|request\.files|save\(|secure_filename|FileField|ImageField' \
-g '*.py' \
.
```

---

# Node.js

```bash
rg -n \
'multer|formidable|busboy|express-fileupload|req\.file|req\.files' \
-g '*.js' \
-g '*.ts' \
.
```

Review:

```text
Original filename
Generated filename
Extension
MIME type
Content
Size
Storage location
Web accessibility
Permissions
Downstream processing
Archive extraction
```

---

# Archive Extraction and Zip Slip

Search:

```bash
rg -ni \
'ZipInputStream|ZipEntry|ZipFile|extractall|extract\(|unzip|adm-zip|yauzl|archiver|ZipArchive' \
.
```

Trace archive entry names into filesystem paths.

---

# XXE Candidates

---

# Java

```bash
rg -n \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory|SchemaFactory|XMLReader|SAXParser|Unmarshaller|JAXBContext' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'XmlDocument|XmlReader|XmlTextReader|XDocument|XmlResolver|DtdProcessing' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'DOMDocument|SimpleXML|simplexml_load|XMLReader|xml_parse' \
-g '*.php' \
.
```

---

# Python

```bash
rg -n \
'xml\.etree|ElementTree|lxml|etree|xml\.dom|xml\.sax|BeautifulSoup' \
-g '*.py' \
.
```

Parser presence does not prove XXE.

Review:

```text
Parser
Version
DTD handling
External entity handling
Network access
Configuration
Input trust
```

---

# Deserialisation Candidates

---

# Java

```bash
rg -n \
'ObjectInputStream|readObject\(|readUnshared\(|XMLDecoder|XStream|activateDefaultTyping|enableDefaultTyping|ObjectMapper|Yaml\(' \
-g '*.java' \
.
```

Do not treat:

```text
ObjectMapper.readValue()
```

as inherently unsafe.

Investigate:

```text
Polymorphic typing
Allowed classes
Trust boundary
Library version
Custom type resolution
```

---

# .NET

```bash
rg -n \
'BinaryFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|JavaScriptSerializer|TypeNameHandling|Deserialize\(' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'\bunserialize\(' \
-g '*.php' \
.
```

---

# Python

```bash
rg -n \
'pickle\.(load|loads)|cPickle|yaml\.load\(|marshal\.loads|shelve\.' \
-g '*.py' \
.
```

---

# XSS and HTML Injection

---

# Java / JSP

```bash
rg -n \
'<%=|<c:out|response\.getWriter\(\)|PrintWriter|\.write\(|\.print\(' \
-g '*.jsp' \
-g '*.java' \
.
```

Thymeleaf:

```bash
rg -n \
'th:text|th:utext' \
-g '*.html' \
.
```

`th:text` and `th:utext` have different output behavior and should not be treated as equivalent.

---

# .NET / Razor

```bash
rg -n \
'Html\.Raw|WriteLiteral|Response\.Write|@Html\.|IHtmlContent' \
-g '*.cs' \
-g '*.cshtml' \
.
```

---

# PHP

```bash
rg -n \
'\becho\b|\bprint\b|\bprintf\s*\(' \
-g '*.php' \
.
```

These functions are extremely common.

Use them as output discovery, not vulnerability proof.

---

# Browser JavaScript

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|document\.writeln' \
-g '*.js' \
-g '*.ts' \
-g '*.jsx' \
-g '*.tsx' \
.
```

Framework-specific dangerous output:

```bash
rg -n \
'dangerouslySetInnerHTML|v-html|\[innerHTML\]' \
-g '*.js' \
-g '*.ts' \
-g '*.jsx' \
-g '*.tsx' \
-g '*.vue' \
-g '*.html' \
.
```

---

# DOM XSS Sources

```bash
rg -n \
'location\.(href|search|hash)|document\.(URL|documentURI|referrer)|window\.name|localStorage|sessionStorage|event\.data|message\.data' \
-g '*.js' \
-g '*.ts' \
.
```

Combine with sink searches and manually trace flows.

---

# postMessage Security

Search:

```bash
rg -n \
'addEventListener\(["'\'']message|onmessage|postMessage\(' \
-g '*.js' \
-g '*.ts' \
.
```

Then inspect origin validation:

```bash
rg -n \
'event\.origin|e\.origin|message\.origin' \
-g '*.js' \
-g '*.ts' \
.
```

Do not assume absence of a nearby `origin` string proves missing validation. Follow the complete handler.

---

# Prototype Pollution

Search object merge and assignment patterns:

```bash
rg -n \
'Object\.assign|merge\(|deepMerge|extend\(|set\(|__proto__|constructor\.prototype|prototype\[' \
-g '*.js' \
-g '*.ts' \
.
```

Prototype pollution requires careful data-flow and object-path analysis.

---

# Open Redirect Candidates

---

# Java / Spring

```bash
rg -n \
'redirect:|RedirectView|sendRedirect\(|Location' \
-g '*.java' \
.
```

---

# .NET

```bash
rg -n \
'Redirect\(|RedirectPermanent\(|RedirectPreserveMethod\(|LocalRedirect\(|Response\.Redirect|Location' \
-g '*.cs' \
.
```

---

# PHP

```bash
rg -n \
'header\s*\(\s*["'\'']Location:|header\s*\(' \
-g '*.php' \
.
```

---

# Django / Flask

```bash
rg -n \
'redirect\(|HttpResponseRedirect|HttpResponsePermanentRedirect' \
-g '*.py' \
.
```

---

# Node.js

```bash
rg -n \
'res\.redirect\(|Location' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Browser JavaScript Redirects

```bash
rg -n \
'window\.location|location\.href|location\.assign|location\.replace' \
-g '*.js' \
-g '*.ts' \
.
```

Trace whether attacker-controlled data determines the destination.

---

# CSRF Review

Search:

```bash
rg -ni \
'csrf|xsrf|anti.?forgery|antiforgery|SameSite' \
.
```

---

# Spring Security CSRF

```bash
rg -n \
'\.csrf\(|csrf\.disable|ignoringRequestMatchers|CsrfToken' \
-g '*.java' \
.
```

Do not automatically report:

```text
csrf.disable()
```

The application may be a stateless API using explicit bearer tokens.

Determine the authentication model.

---

# .NET CSRF

```bash
rg -n \
'ValidateAntiForgeryToken|AutoValidateAntiforgeryToken|IgnoreAntiforgeryToken|IAntiforgery|Antiforgery' \
-g '*.cs' \
.
```

---

# Django CSRF

```bash
rg -n \
'csrf_exempt|csrf_protect|CsrfViewMiddleware|CSRF_' \
-g '*.py' \
.
```

`csrf_exempt` deserves review, but is not automatically vulnerable.

---

# Flask CSRF

```bash
rg -ni \
'CSRFProtect|csrf\.exempt|WTF_CSRF|csrf' \
-g '*.py' \
.
```

---

# Node.js CSRF

```bash
rg -ni \
'csrf|csurf|SameSite' \
-g '*.js' \
-g '*.ts' \
.
```

---

# CORS Review

General:

```bash
rg -ni \
'cors|Access-Control-Allow-Origin|allowedOrigins|allowedOriginPatterns|allowCredentials|credentials' \
.
```

---

# Spring CORS

```bash
rg -n \
'@CrossOrigin|CorsConfiguration|allowedOrigins|allowedOriginPatterns|allowCredentials|CorsFilter|WebMvcConfigurer' \
-g '*.java' \
.
```

---

# .NET CORS

```bash
rg -n \
'AddCors|UseCors|WithOrigins|AllowAnyOrigin|AllowCredentials|AllowAnyHeader|AllowAnyMethod' \
-g '*.cs' \
.
```

---

# Django CORS

```bash
rg -n \
'CORS_ALLOWED_ORIGINS|CORS_ALLOW_ALL_ORIGINS|CORS_ALLOW_CREDENTIALS|corsheaders' \
-g '*.py' \
.
```

---

# Flask CORS

```bash
rg -n \
'CORS\(|cross_origin|supports_credentials|origins' \
-g '*.py' \
.
```

---

# Express CORS

```bash
rg -n \
'cors\(|Access-Control-Allow-Origin|credentials\s*:' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Clickjacking and Security Headers

Search:

```bash
rg -ni \
'X-Frame-Options|frame-ancestors|Content-Security-Policy|Strict-Transport-Security|X-Content-Type-Options|Referrer-Policy|Permissions-Policy' \
.
```

Missing header configuration in source code does not prove the header is missing in production.

It may be applied by:

```text
Reverse proxy
Web server
CDN
API gateway
Cloud platform
```

---

# Host Header Candidates

Search:

```bash
rg -ni \
'getServerName|getHeader\(["'\'']Host|Request\.Host|HTTP_HOST|request\.host|req\.hostname|req\.headers\.host|X-Forwarded-Host|Forwarded' \
.
```

High-value usage includes:

```text
Password reset URL generation
OAuth callbacks
Absolute URLs
Redirects
Email links
Security decisions
```

---

# Proxy Trust

Search:

```bash
rg -ni \
'trust proxy|ForwardedHeaderFilter|forward-headers|X-Forwarded-For|X-Forwarded-Proto|ProxyFix|ForwardedHeaders' \
.
```

Proxy trust can influence:

```text
Client IP
Scheme
Host
Secure cookies
Redirect URLs
Rate limiting
```

---

# Session Management

Search:

```bash
rg -ni \
'session|JSESSIONID|HttpSession|SESSION_COOKIE|express-session|cookie-session|AddSession|UseSession|SameSite|HttpOnly|Secure' \
.
```

---

# Java Sessions

```bash
rg -n \
'HttpSession|getSession\(|invalidate\(|changeSessionId|SessionCreationPolicy|sessionManagement' \
-g '*.java' \
.
```

---

# .NET Sessions and Cookies

```bash
rg -n \
'AddSession|UseSession|HttpContext\.Session|AddCookie|CookieSecurePolicy|HttpOnly|SameSite' \
-g '*.cs' \
.
```

---

# Django Sessions

```bash
rg -n \
'SESSION_COOKIE|SESSION_ENGINE|request\.session|cycle_key\(|flush\(' \
-g '*.py' \
.
```

---

# Flask Sessions

```bash
rg -n \
'SECRET_KEY|session\[|session\.|SESSION_COOKIE|Flask-Session' \
-g '*.py' \
.
```

---

# Express Sessions

```bash
rg -n \
'express-session|cookie-session|req\.session|session\.destroy|regenerate\(' \
-g '*.js' \
-g '*.ts' \
.
```

---

# JWT Review

Search:

```bash
rg -ni \
'jwt|jsonwebtoken|JwtDecoder|JwtEncoder|NimbusJwtDecoder|AddJwtBearer|decode\(|verify\(|sign\(' \
.
```

Review:

```text
Signature verification
Issuer
Audience
Expiration
Algorithm selection
Key handling
Custom claims
Authorisation
```

---

# Spring JWT

```bash
rg -n \
'JwtDecoder|JwtEncoder|NimbusJwtDecoder|oauth2ResourceServer|JwtAuthenticationConverter|JwtValidators|JwtClaimValidator' \
-g '*.java' \
.
```

---

# .NET JWT

```bash
rg -n \
'AddJwtBearer|TokenValidationParameters|ValidateIssuer|ValidateAudience|ValidateLifetime|IssuerSigningKey|JwtSecurityTokenHandler' \
-g '*.cs' \
.
```

---

# Python JWT

```bash
rg -n \
'jwt\.decode|jwt\.encode|PyJWT|python-jose|JWT' \
-g '*.py' \
.
```

---

# Node.js JWT

```bash
rg -n \
'jwt\.verify|jwt\.decode|jwt\.sign|jsonwebtoken' \
-g '*.js' \
-g '*.ts' \
.
```

`decode()` and `verify()` are not equivalent operations in many JWT libraries.

Inspect actual security decisions.

---

# OAuth / OIDC

Search:

```bash
rg -ni \
'oauth|oidc|openid|client_secret|client_id|redirect_uri|redirectUri|authorization_code|pkce|code_verifier|nonce|state' \
.
```

Review:

```text
Redirect URI handling
State
Nonce
PKCE
Token validation
Issuer
Audience
Account linking
Custom callbacks
```

---

# SAML

Search:

```bash
rg -ni \
'saml|SAMLResponse|SAMLRequest|RelyingParty|Assertion|Metadata|EntityDescriptor' \
.
```

Review framework configuration and any custom:

```text
Signature handling
Issuer validation
Audience validation
Recipient validation
Replay handling
Account mapping
```

---

# Password Reset

Search:

```bash
rg -ni \
'forgot.?password|password.?reset|reset.?token|resetPassword|PasswordReset|recovery' \
.
```

Then trace:

```text
Request
   |
   v
Token Generation
   |
   v
Storage
   |
   v
Email Link
   |
   v
Token Validation
   |
   v
Password Change
```

Review:

```text
Token entropy
Expiration
Single use
User enumeration
Host handling
Rate limiting
Session invalidation
```

---

# MFA / OTP

Search:

```bash
rg -ni \
'mfa|2fa|totp|otp|one.?time|authenticator|verification.?code|backup.?code' \
.
```

Review:

```text
Enrollment
Verification
Recovery
Bypass paths
Rate limiting
Replay
Backup codes
Sensitive-action enforcement
```

---

# Mass Assignment

Search:

```bash
rg -n \
'BeanUtils\.copyProperties|ModelMapper|@ModelAttribute|TryUpdateModel|UpdateModel|Object\.assign|req\.body|request\.data' \
.
```

Look for:

```text
Request Object
     |
     v
Domain / ORM Entity
     |
     v
Database
```

Sensitive fields include:

```text
role
isAdmin
permissions
ownerId
tenantId
balance
verified
status
```

---

# Race Conditions

Static search can identify concurrency-related controls.

Search:

```bash
rg -ni \
'transaction|@Transactional|synchronized|Lock|ReentrantLock|@Version|optimistic|pessimistic|SELECT .* FOR UPDATE|atomic|mutex|semaphore' \
.
```

Absence of these keywords does not prove a race condition.

The database may enforce atomicity or constraints elsewhere.

---

# Rate Limiting

Search:

```bash
rg -ni \
'rate.?limit|throttl|bucket4j|resilience4j|RequestRateLimiter|express-rate-limit|slowapi|limiter|TooManyRequests|429' \
.
```

Remember:

```text
No rate limiting in application code
    !=
No rate limiting
```

It may be implemented by:

```text
CDN
WAF
Reverse proxy
API gateway
Load balancer
```

---

# Cache Security

Search:

```bash
rg -ni \
'@Cacheable|CacheManager|MemoryCache|IMemoryCache|Redis|cache\.get|cache\.set|cached' \
.
```

Review cache keys for:

```text
User identity
Tenant
Organisation
Role
Permission
Resource
```

---

# Secrets Exposure

General search:

```bash
rg --hidden -ni \
-g '!.git/**' \
'password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key|client[_-]?secret' \
.
```

---

# Assignment-Like Secret Patterns

```bash
rg --hidden -ni \
-g '!.git/**' \
'(password|passwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]' \
.
```

Expect false positives.

---

# Private Keys

```bash
rg --hidden -n \
'BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY' \
-g '!.git/**' \
.
```

---

# Configuration Files

```bash
rg --files --hidden \
-g '!.git/**' \
| grep -Ei \
'(^|/)\.env|application.*\.(yml|yaml|properties)|appsettings.*\.json|settings\.py|config|secret|credential|docker|compose|k8s|kubernetes|terraform'
```

---

# GitHub Actions and CI/CD

```bash
rg --hidden -ni \
-g '.github/**' \
'secret|token|password|credential|curl|wget|npm|pip|mvn|gradle|docker' \
.
```

Also inspect:

```text
.gitlab-ci.yml
Jenkinsfile
azure-pipelines.yml
CircleCI
Buildkite
```

---

# Cryptography

Search:

```bash
rg -ni \
'Cipher|MessageDigest|SecureRandom|Random\(|AES|DES|3DES|RC4|RSA|MD5|SHA1|SHA-1|bcrypt|scrypt|argon|PBKDF|KeyGenerator|SecretKeySpec' \
.
```

Do not report:

```text
MD5 found
```

without determining its use.

For example:

```text
MD5 for a non-security cache identifier
```

has a different security implication from:

```text
MD5 for password storage
```

---

# Java Cryptography

```bash
rg -n \
'Cipher\.getInstance|MessageDigest\.getInstance|SecureRandom|new Random\(|SecretKeySpec|KeyGenerator|KeyPairGenerator' \
-g '*.java' \
.
```

---

# .NET Cryptography

```bash
rg -n \
'MD5|SHA1|SHA256|Aes|DES|TripleDES|RandomNumberGenerator|System\.Random|Rfc2898DeriveBytes|PasswordHasher' \
-g '*.cs' \
.
```

---

# Python Cryptography

```bash
rg -n \
'hashlib|random\.|secrets\.|Crypto\.|cryptography\.|bcrypt|argon2|pbkdf2' \
-g '*.py' \
.
```

---

# Node.js Cryptography

```bash
rg -n \
'crypto\.|Math\.random|bcrypt|argon2|pbkdf2|createHash|createCipher|createCipheriv' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Logging and Sensitive Data

Search:

```bash
rg -n \
'logger\.|log\.|Console\.Write|System\.out\.print|console\.log|print\(' \
.
```

Then search nearby sensitive values.

Examples:

```bash
rg -ni \
'log.*(password|token|secret|authorization|cookie)|logger.*(password|token|secret|authorization|cookie)' \
.
```

Expect false positives.

---

# Log Injection / Forging

Identify logging of attacker-controlled:

```text
Headers
Usernames
URLs
Request parameters
User-Agent
Referer
```

Search sources and logger calls, then trace manually.

---

# Error Handling and Information Disclosure

Search:

```bash
rg -ni \
'stacktrace|printStackTrace|traceback|debug\s*=\s*true|DEBUG\s*=\s*True|UseDeveloperExceptionPage|exception\.message|exception\.stack|console\.error' \
.
```

Also:

```bash
rg -ni \
'debug|development|verbose|stack.?trace|show.?errors' \
.
```

Configuration and environment matter.

---

# Spring Boot Actuator

Search:

```bash
rg -ni \
'actuator|management\.endpoints|management\.endpoint|management\.server|show-details|health|heapdump|env|configprops|loggers' \
-g '*.properties' \
-g '*.yml' \
-g '*.yaml' \
.
```

Actuator presence is not automatically information disclosure.

Review:

```text
Exposure
Network accessibility
Authentication
Authorisation
Environment
```

---

# Django Debug Configuration

```bash
rg -n \
'DEBUG\s*=|ALLOWED_HOSTS|SECRET_KEY|CSRF_TRUSTED_ORIGINS|SECURE_|SESSION_COOKIE|CSRF_COOKIE' \
-g '*.py' \
.
```

---

# Flask Debug

```bash
rg -n \
'debug\s*=\s*True|DEBUG\s*=|app\.run\(' \
-g '*.py' \
.
```

---

# Express Security Configuration

```bash
rg -n \
'helmet\(|trust proxy|express-session|cookie-session|cors\(|rateLimit|x-powered-by' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Dependency Security

Find manifests:

```bash
rg --files | grep -E \
'pom\.xml|build\.gradle|build\.gradle\.kts|package\.json|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|composer\.json|composer\.lock|requirements\.txt|poetry\.lock|Pipfile\.lock|pyproject\.toml|\.csproj$|packages\.lock\.json$'
```

`ripgrep` can locate dependencies, but vulnerability determination should use appropriate software composition analysis and version/context review.

---

# Java Dependencies

```bash
rg -n \
'<dependency>|<groupId>|<artifactId>|<version>' \
-g 'pom.xml' \
.
```

Gradle:

```bash
rg -n \
'implementation|api|compileOnly|runtimeOnly|testImplementation' \
-g 'build.gradle' \
-g 'build.gradle.kts' \
.
```

---

# .NET Dependencies

```bash
rg -n \
'PackageReference|PackageVersion|packages\.config' \
-g '*.csproj' \
-g '*.props' \
-g '*.targets' \
-g 'packages.config' \
.
```

---

# PHP Dependencies

```bash
rg -n \
'"require"|"require-dev"' \
-g 'composer.json' \
.
```

---

# Python Dependencies

```bash
rg -n \
'.+' \
-g 'requirements*.txt' \
-g 'pyproject.toml' \
-g 'Pipfile' \
.
```

---

# Node.js Dependencies

```bash
rg -n \
'"dependencies"|"devDependencies"|"peerDependencies"|"optionalDependencies"' \
-g 'package.json' \
.
```

---

# GraphQL Discovery

General:

```bash
rg -ni \
'graphql|resolver|mutation|subscription|DataFetcher|QueryMapping|MutationMapping|SubscriptionMapping' \
.
```

---

# Spring GraphQL

```bash
rg -n \
'@QueryMapping|@MutationMapping|@SubscriptionMapping|@SchemaMapping|DataFetcher|GraphQlSource' \
-g '*.java' \
.
```

---

# Python GraphQL

```bash
rg -ni \
'graphene|strawberry|ariadne|resolver|mutation|subscription' \
-g '*.py' \
.
```

---

# Node.js GraphQL

```bash
rg -ni \
'apollo|graphql|resolver|typeDefs|Mutation|Subscription' \
-g '*.js' \
-g '*.ts' \
.
```

Review resolver-level:

```text
Authentication
Authorisation
Object ownership
Input validation
Rate limiting
```

---

# gRPC Discovery

Find protocol files:

```bash
rg --files -g '*.proto'
```

Search:

```bash
rg -n \
'\bservice\b|\brpc\b' \
-g '*.proto' \
.
```

Java:

```bash
rg -n \
'BindableService|ImplBase|StreamObserver|@GrpcService' \
-g '*.java' \
.
```

.NET:

```bash
rg -n \
'Grpc\.Core|BindService|ServerCallContext|MapGrpcService' \
-g '*.cs' \
.
```

Python:

```bash
rg -n \
'grpc\.server|Servicer|add_.*Servicer_to_server' \
-g '*.py' \
.
```

Node.js:

```bash
rg -ni \
'@grpc/grpc-js|grpc\.loadPackageDefinition|addService' \
-g '*.js' \
-g '*.ts' \
.
```

---

# WebSocket Discovery

General:

```bash
rg -ni \
'websocket|sockjs|stomp|socket\.io|ws://' \
.
```

---

# Spring WebSocket

```bash
rg -n \
'@MessageMapping|WebSocketConfigurer|WebSocketMessageBrokerConfigurer|ChannelInterceptor|StompEndpointRegistry' \
-g '*.java' \
.
```

---

# .NET WebSockets / SignalR

```bash
rg -n \
'WebSocket|SignalR|Hub\b|MapHub|HubConnection' \
-g '*.cs' \
.
```

---

# Python WebSockets

```bash
rg -ni \
'websocket|websockets|SocketIO|channels|AsyncWebsocketConsumer' \
-g '*.py' \
.
```

---

# Node.js WebSockets

```bash
rg -ni \
'socket\.io|WebSocketServer|new WebSocket|ws\.Server|io\.on' \
-g '*.js' \
-g '*.ts' \
.
```

Review message-level authorisation, not only connection authentication.

---

# Background Jobs

Security review should not stop at HTTP routes.

Search:

```bash
rg -ni \
'scheduled|scheduler|cron|background|worker|job|queue|consumer|listener|async' \
.
```

---

# Spring Background Processing

```bash
rg -n \
'@Scheduled|@Async|@EventListener|ApplicationListener|CommandLineRunner|ApplicationRunner' \
-g '*.java' \
.
```

---

# .NET Background Processing

```bash
rg -n \
'BackgroundService|IHostedService|ExecuteAsync|Task\.Run|Timer' \
-g '*.cs' \
.
```

---

# Python Background Processing

```bash
rg -ni \
'celery|@task|@shared_task|rq\.|apscheduler|schedule\.' \
-g '*.py' \
.
```

---

# Node.js Background Processing

```bash
rg -ni \
'bullmq|bull|agenda|node-cron|setInterval|worker_threads' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Message Queues

Search:

```bash
rg -ni \
'kafka|rabbitmq|amqp|jms|sqs|servicebus|redis.*queue|consumer|producer|listener' \
.
```

---

# Java Messaging

```bash
rg -n \
'@KafkaListener|KafkaTemplate|@RabbitListener|RabbitTemplate|@JmsListener|JmsTemplate' \
-g '*.java' \
.
```

Messages should be treated according to their actual trust boundary.

An internal queue is not automatically trusted.

---

# Webhooks

Search:

```bash
rg -ni \
'webhook|callback|signature|hmac|event.?type' \
.
```

Look for:

```text
Signature verification
Replay protection
Timestamp checks
Event validation
Authorisation
```

---

# HTTP Request Smuggling Review

Source code can identify:

```text
Custom HTTP parsing
Transfer-Encoding handling
Content-Length handling
Header normalisation
Proxy assumptions
```

Search:

```bash
rg -ni \
'Content-Length|Transfer-Encoding|chunked|HTTP parser|raw headers' \
.
```

However:

```text
source code match
    !=
request smuggling vulnerability
```

The complete HTTP chain must be considered.

---

# HTTP Cache Security

Search:

```bash
rg -ni \
'Cache-Control|Vary|ETag|Expires|@Cacheable|ResponseCache|cache-control' \
.
```

Review whether responses containing:

```text
User-specific data
Tenant-specific data
Authenticated data
```

can become incorrectly shared.

---

# Third-Party JavaScript

Search external scripts:

```bash
rg -n \
'<script[^>]+src=|https://.*\.js' \
-g '*.html' \
-g '*.htm' \
-g '*.cshtml' \
-g '*.jsp' \
-g '*.php' \
.
```

Search integrity attributes:

```bash
rg -n \
'integrity=|crossorigin=' \
-g '*.html' \
-g '*.htm' \
-g '*.cshtml' \
-g '*.jsp' \
-g '*.php' \
.
```

Absence of SRI is not automatically a vulnerability.

Review the actual third-party trust model.

---

# Source Maps

Find source maps:

```bash
rg --files -g '*.map'
```

References:

```bash
rg -n \
'sourceMappingURL' \
-g '*.js' \
-g '*.css' \
.
```

Source maps may reveal:

```text
Original source
Internal paths
Comments
Endpoints
Secrets accidentally embedded in client code
```

Their presence alone does not automatically constitute a vulnerability.

---

# Client-Side Secrets

Search browser code:

```bash
rg -ni \
'api[_-]?key|secret|token|client[_-]?secret|authorization|bearer' \
-g '*.js' \
-g '*.ts' \
-g '*.jsx' \
-g '*.tsx' \
.
```

Remember that some public API identifiers are intentionally exposed.

Determine whether the credential grants sensitive capabilities.

---

# AI / LLM Integration Discovery

Where an application integrates AI or LLM services, identify the integration points:

```bash
rg -ni \
'openai|anthropic|gemini|ollama|langchain|llamaindex|prompt|system.?prompt|tool.?call|function.?call|embedding|vector.?store|rag' \
.
```

This is primarily attack-surface discovery.

Review:

```text
Prompt construction
Untrusted content
Tool permissions
Output handling
Secrets
RAG sources
External requests
Authorisation
```

---

# Mass Route Search Across Languages

For mixed repositories:

```bash
rg -n \
'@RequestMapping|@GetMapping|@PostMapping|\[HttpGet|\[HttpPost|MapGet\(|MapPost\(|@.*\.route\(|\bpath\(|\bre_path\(|\bapp\.(get|post|put|patch|delete)\(|\brouter\.(get|post|put|patch|delete)\(' \
.
```

Expect noise.

Technology-specific passes are normally better.

---

# Broad Source Search

```bash
rg -n \
'@RequestParam|@PathVariable|@RequestBody|Request\.Query|Request\.Form|\$_GET|\$_POST|request\.GET|request\.POST|request\.args|request\.form|req\.query|req\.params|req\.body' \
.
```

---

# Broad Command Sink Search

```bash
rg -n \
'Runtime\.getRuntime|ProcessBuilder|Process\.Start|ProcessStartInfo|system\(|shell_exec\(|passthru\(|proc_open\(|os\.system|subprocess\.|child_process|execSync\(' \
.
```

---

# Broad SSRF Sink Search

```bash
rg -n \
'HttpClient|WebClient|RestTemplate|RestClient|URLConnection|requests\.|httpx\.|urlopen|curl_exec|axios\.|fetch\(|http\.request|https\.request' \
.
```

---

# Broad Deserialisation Search

```bash
rg -n \
'ObjectInputStream|readObject\(|BinaryFormatter|LosFormatter|NetDataContractSerializer|unserialize\(|pickle\.load|yaml\.load|XMLDecoder|XStream|activateDefaultTyping' \
.
```

---

# Broad XSS Sink Search

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|Html\.Raw|th:utext|dangerouslySetInnerHTML|v-html|Response\.Write' \
.
```

---

# Broad Secret Search

```bash
rg --hidden -ni \
-g '!.git/**' \
'password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key|client[_-]?secret' \
.
```

---

# Search Output to Files

Store results:

```bash
mkdir -p review/ripgrep
```

Routes:

```bash
rg -n \
'@RequestMapping|@GetMapping|@PostMapping|app\.get|app\.post|\[HttpGet|\[HttpPost' \
. \
> review/ripgrep/routes.txt
```

Commands:

```bash
rg -n \
'ProcessBuilder|Runtime\.getRuntime|Process\.Start|os\.system|subprocess|child_process' \
. \
> review/ripgrep/command-sinks.txt
```

SSRF:

```bash
rg -n \
'HttpClient|WebClient|RestTemplate|requests\.|axios\.|fetch\(' \
. \
> review/ripgrep/ssrf-sinks.txt
```

---

# Useful Output Options

No headings:

```bash
rg --no-heading -n 'ProcessBuilder' .
```

Only matching text:

```bash
rg -o 'ProcessBuilder' .
```

Column numbers:

```bash
rg --column -n 'ProcessBuilder' .
```

JSON output:

```bash
rg --json 'ProcessBuilder' .
```

JSON output can be useful when integrating `rg` into custom analysis scripts.

---

# Search Files Containing a Sink

```bash
rg -l \
'ProcessBuilder|Runtime\.getRuntime' \
-g '*.java' \
.
```

This provides a quick list of high-interest files.

---

# Count Dangerous APIs

```bash
rg -c \
'ProcessBuilder|Runtime\.getRuntime' \
-g '*.java' \
.
```

Useful for prioritisation, not vulnerability counting.

---

# Search Files Without a Pattern

Sometimes the absence of a security annotation is interesting.

For example, list Java controllers:

```bash
rg -l \
'@(RestController|Controller)' \
-g '*.java' \
.
```

Then manually inspect their authorisation.

Trying to infer "missing authorisation" with regex alone is unreliable because security may be enforced globally.

---

# Piping to Other Tools

Example:

```bash
rg -l \
'ProcessBuilder|Runtime\.getRuntime' \
-g '*.java' \
. \
| sort -u
```

Count files:

```bash
rg -l \
'ProcessBuilder|Runtime\.getRuntime' \
-g '*.java' \
. \
| wc -l
```

---

# Finding Custom Security Helpers

Search names such as:

```bash
rg -ni \
'sanitize|validate|escape|safe|secure|permission|authorize|allowed|trusted' \
.
```

Interesting functions might include:

```text
validateUrl()
safeExecute()
sanitizeFilename()
checkAccess()
hasPermission()
```

Open them.

A function called:

```text
safeExecute()
```

may not actually be safe.

---

# Variant Analysis with ripgrep

Suppose manual review confirms a vulnerability in:

```java
CommandRunner.runCommand()
```

Find every call:

```bash
rg -n \
'runCommand\(' \
-g '*.java' \
.
```

Then search related helpers:

```bash
rg -n \
'CommandRunner|runCommand|executeCommand|shellCommand' \
-g '*.java' \
.
```

This is one of `ripgrep`'s strongest security use cases.

---

# Variant Analysis Workflow

```text
Confirmed Vulnerability
        |
        v
Identify Vulnerable Function
        |
        v
rg Function Name
        |
        v
Find Every Caller
        |
        v
Find Similar Functions
        |
        v
Review Each Flow
        |
        v
Identify Variants
```

---

# Turning ripgrep Patterns into SAST Rules

A useful workflow is:

```text
ripgrep
   |
   v
Find Pattern
   |
   v
Manual Validation
   |
   v
Understand Syntax
   |
   +----------------+
   |                |
   v                v
Semgrep          OpenGrep
   |                |
   +-------+--------+
           |
           v
    Reusable Rule
```

If deeper data-flow analysis is needed:

```text
Confirmed Pattern
       |
       v
CodeQL Query
```

---

# Example - SQL Injection Review

Search:

```bash
rg -n \
'createNativeQuery\(' \
-g '*.java' \
.
```

Candidate:

```java
String query =
    "SELECT * FROM users WHERE username = '"
    + username
    + "'";

entityManager.createNativeQuery(query);
```

Now find where `username` originates.

VS Code:

```text
Find References
Go to Definition
Call Hierarchy
```

Possible flow:

```text
@RequestParam username
        |
        v
UserController.search()
        |
        v
UserService.search()
        |
        v
UserRepository.search()
        |
        v
String Concatenation
        |
        v
createNativeQuery()
```

This is a strong SQL injection candidate.

---

# Example - Safe SQL Candidate

Search identifies:

```java
PreparedStatement statement =
    connection.prepareStatement(
        "SELECT * FROM users WHERE username = ?"
    );

statement.setString(
    1,
    username
);
```

Result:

```text
Source exists
Sink exists
Parameter binding exists
```

The search match alone should not be reported.

---

# Example - SSRF Review

Search:

```bash
rg -n \
'HttpClient' \
-g '*.java' \
.
```

Candidate:

```java
URI uri =
    URI.create(request.getParameter("url"));

HttpRequest request =
    HttpRequest.newBuilder(uri).build();

client.send(
    request,
    HttpResponse.BodyHandlers.ofString()
);
```

Flow:

```text
HTTP Parameter
      |
      v
URI.create()
      |
      v
HttpRequest
      |
      v
HttpClient.send()
```

Now search for validation:

```bash
rg -n \
'validateUrl|allowedHost|allowedDomain|allowlist|isAllowed|isPrivate|loopback' \
-g '*.java' \
.
```

Then inspect:

```text
Scheme
Host
Resolved address
Port
Redirects
Egress
```

---

# Example - Command Execution Review

Search:

```bash
rg -n \
'ProcessBuilder' \
-g '*.java' \
.
```

Candidate:

```java
new ProcessBuilder(
    "/usr/bin/convert",
    inputFile,
    outputFile
).start();
```

Questions:

```text
Can inputFile contain argument-like values?

Can outputFile alter program behaviour?

Are filenames generated by the server?

Can the executable path be changed?

Is a shell involved?

Does the target program itself interpret special syntax?
```

Do not simply report:

```text
ProcessBuilder = command injection
```

---

# Example - IDOR Review

Search:

```bash
rg -n \
'findById\(' \
-g '*.java' \
.
```

Candidate:

```java
@GetMapping("/documents/{id}")
public Document get(
    @PathVariable Long id
) {
    return repository
        .findById(id)
        .orElseThrow();
}
```

Now search the surrounding code for:

```text
Principal
Authentication
SecurityContext
owner
userId
tenant
permission
PreAuthorize
```

Potential flow:

```text
Attacker-Controlled ID
        |
        v
findById(id)
        |
        v
Document
        |
        v
Response
```

Missing ownership check may indicate IDOR/BOLA.

---

# Example - Stored XSS

Search output sinks:

```bash
rg -n \
'th:utext' \
-g '*.html' \
.
```

Candidate:

```html
<div th:utext="${profile.biography}"></div>
```

Trace backwards:

```text
profile.biography
       ^
       |
Database
       ^
       |
Profile Update
       ^
       |
HTTP Input
```

This is a second-order flow:

```text
HTTP Input
    |
    v
Database
    |
    v
HTML Sink
```

---

# Example - Second-Order Command Injection

Search command sinks:

```bash
rg -n \
'ProcessBuilder|Runtime\.getRuntime' \
.
```

Suppose:

```text
ScheduledJob
    |
    v
Database filename
    |
    v
Command execution
```

Now determine where the filename was originally stored:

```text
File Upload
    |
    v
Database
    |
    v
Scheduled Job
    |
    v
Command Sink
```

Do not limit source analysis to variables in the same function.

---

# Search by Security Boundary

A useful approach is searching components independently.

## Controllers

```bash
rg -l \
'Controller|RestController|ApiController|route\(|router\.' \
.
```

## Services

```bash
rg --files | grep -Ei \
'service'
```

## Repositories

```bash
rg --files | grep -Ei \
'repository|dao|database|store'
```

## Security

```bash
rg --files | grep -Ei \
'security|auth|permission|policy'
```

---

# Build a Source-Sink Inventory

Example:

```text
SOURCES

HTTP:
@RequestParam
@PathVariable
@RequestBody

Headers:
@RequestHeader
getHeader()

Files:
MultipartFile

Messages:
@KafkaListener
```

Then:

```text
SINKS

SQL:
createNativeQuery
Statement.executeQuery

Commands:
ProcessBuilder
Runtime.exec

HTTP:
HttpClient
WebClient

Files:
Files.readString
FileInputStream

Templates:
SpEL
FreeMarker
Thymeleaf
```

This creates a reusable map of the application.

---

# Save Technology-Specific Pattern Files

For repeated assessments, maintain:

```text
patterns/
│
├── java.txt
├── dotnet.txt
├── php.txt
├── python.txt
├── django.txt
├── flask.txt
├── nodejs.txt
└── javascript.txt
```

Or vulnerability-oriented files:

```text
patterns/
│
├── routes.txt
├── auth.txt
├── authz.txt
├── sql.txt
├── commands.txt
├── ssrf.txt
├── files.txt
├── deserialization.txt
└── secrets.txt
```

---

# Pattern Quality

A good `ripgrep` pattern should have a clear purpose.

Bad:

```bash
rg 'get' .
```

This produces excessive noise.

Better:

```bash
rg -n \
'@GetMapping|app\.get\(|router\.get\(' \
.
```

---

# Broad vs Narrow Searches

Start broad when learning the repository:

```text
High Recall
```

Then narrow:

```text
Higher Precision
```

Example:

```bash
rg -ni 'redirect' .
```

Then:

```bash
rg -n \
'RedirectView|sendRedirect|res\.redirect|Response\.Redirect' \
.
```

---

# Case Sensitivity

Security names may vary:

```text
password
Password
PASSWORD
```

Use:

```bash
rg -ni 'password' .
```

For API names where capitalization matters:

```bash
rg -n 'ProcessBuilder' .
```

---

# Multiline Limitations

Security-relevant code often spans multiple lines.

Example:

```java
entityManager
    .createNativeQuery(
        query
    );
```

Simple line-oriented searches can still find:

```text
createNativeQuery
```

but complex regexes attempting to understand an entire expression may fail.

This is where syntax-aware tools such as:

```text
Semgrep
OpenGrep
CodeQL
```

become more useful.

---

# Minified and Generated JavaScript

Searching minified bundles can generate huge output.

Prefer source files when available.

Possible exclusion:

```bash
rg \
-g '!*.min.js' \
PATTERN \
.
```

But review:

```text
Source maps
Bundled dependencies
Generated code
```

when they are relevant to the assessment.

---

# Search Only Tracked Git Files

For a Git repository, one option is:

```bash
git ls-files
```

You can combine this with additional workflows if you specifically want to constrain review to tracked files.

Be aware that untracked deployment/configuration files may also be security-relevant.

---

# Git History Complements ripgrep

Current repository search:

```bash
rg -ni 'password|secret|token' .
```

Historical search:

```bash
git log -S 'password' -p
```

Search history for a dangerous helper:

```bash
git log -S 'executeCommand' -p
```

This can reveal:

```text
Removed security controls
Deleted credentials
Previous vulnerable implementations
Security patches
```

---

# Reproducible Review

Record:

```bash
rg --version
```

Repository revision:

```bash
git rev-parse HEAD
```

Branch:

```bash
git branch --show-current
```

Status:

```bash
git status
```

Save important searches in assessment notes.

---

# Suggested Assessment Output

```text
review/
├── ripgrep/
│   ├── routes.txt
│   ├── sources.txt
│   ├── authentication.txt
│   ├── authorisation.txt
│   ├── sql.txt
│   ├── nosql.txt
│   ├── ldap.txt
│   ├── commands.txt
│   ├── ssrf.txt
│   ├── files.txt
│   ├── uploads.txt
│   ├── xxe.txt
│   ├── deserialization.txt
│   ├── xss.txt
│   ├── redirects.txt
│   ├── secrets.txt
│   └── dependencies.txt
│
├── candidates.md
└── findings/
```

---

# Candidate Template

```text
ID:
RG-001

Search:
ProcessBuilder

File:
src/main/java/example/ReportService.java

Line:
84

Potential Type:
Command Injection

Source:
Unknown

Sink:
ProcessBuilder

Next Action:
Trace arguments backwards to their source.

Status:
Investigating
```

---

# Confirmed Finding Template

```text
Title:

Affected Route:

Source:

Source File:

Transformations:

Sink:

Sink File:

Security Controls:

Why the Control Is Ineffective:

Data Flow:

Exploitability:

Impact:

Dynamic Validation:

Recommendation:
```

---

# Data Flow Diagram Template

```text
SOURCE
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
Validation
  |
  v
Repository / Helper
  |
  v
SINK
```

---

# ripgrep Review Checklist

## Repository

```text
[ ] Correct repository
[ ] Correct branch
[ ] Commit recorded
[ ] Languages identified
[ ] Frameworks identified
[ ] Build files identified
[ ] Configuration identified
[ ] Noise directories identified
```

## Attack Surface

```text
[ ] Routes searched
[ ] Controllers searched
[ ] APIs searched
[ ] GraphQL searched
[ ] gRPC searched
[ ] WebSockets searched
[ ] Webhooks searched
[ ] Background jobs searched
[ ] Message consumers searched
```

## Sources

```text
[ ] Query parameters
[ ] Path parameters
[ ] Request bodies
[ ] Headers
[ ] Cookies
[ ] Files
[ ] GraphQL arguments
[ ] gRPC messages
[ ] WebSocket messages
[ ] Queue messages
[ ] Stored attacker-controlled data
```

## Identity

```text
[ ] Authentication
[ ] Authorisation
[ ] Sessions
[ ] JWT
[ ] OAuth/OIDC
[ ] SAML
[ ] Password reset
[ ] MFA
```

## Injection

```text
[ ] SQL
[ ] NoSQL
[ ] LDAP
[ ] Command execution
[ ] Dynamic code execution
[ ] SSTI / expression injection
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
[ ] XSS
[ ] HTML injection
[ ] DOM XSS
[ ] postMessage
[ ] Prototype pollution
[ ] Open redirects
[ ] Third-party JavaScript
[ ] Source maps
```

## HTTP

```text
[ ] CORS
[ ] CSRF
[ ] Host handling
[ ] Proxy trust
[ ] Security headers
[ ] Cache behaviour
[ ] HTTP parsing assumptions
```

## Application Logic

```text
[ ] IDOR / BOLA
[ ] Mass assignment
[ ] Business logic
[ ] Race conditions
[ ] Rate limiting
```

## Data Protection

```text
[ ] Secrets
[ ] Cryptography
[ ] Logging
[ ] Error handling
[ ] Debug configuration
```

## Supply Chain

```text
[ ] Dependency manifests
[ ] Lock files
[ ] CI/CD
[ ] Build scripts
[ ] Third-party packages
```

## Validation

```text
[ ] Matches manually reviewed
[ ] Source established
[ ] Sink established
[ ] Data flow established
[ ] Security controls reviewed
[ ] Framework protections considered
[ ] Deployment controls considered
[ ] Dynamic validation performed where appropriate
[ ] False positives removed
```

## Variant Analysis

```text
[ ] Vulnerable function searched
[ ] All references reviewed
[ ] Similar sinks searched
[ ] Similar helpers searched
[ ] Alternate entry points searched
[ ] Second-order flows considered
[ ] Semgrep/OpenGrep rule considered
[ ] CodeQL query considered
```

---

# Common Mistakes

## Treating Matches as Vulnerabilities

Wrong:

```text
ProcessBuilder found.
Command injection confirmed.
```

Correct:

```text
ProcessBuilder found.
Trace its executable and arguments to determine whether attacker-controlled data reaches a dangerous execution context.
```

---

# Searching Only Sinks

Searching sinks is useful, but you should also understand:

```text
Routes
Sources
Authentication
Authorisation
Validation
Business logic
```

Otherwise the application context is missing.

---

# Searching Only Sources

The opposite is also inefficient.

A repository may contain thousands of request parameters.

Sink-first analysis can quickly identify high-impact areas.

Use both directions.

---

# Using One Giant Regex

A giant pattern may be difficult to:

```text
Understand
Maintain
Debug
Triage
Reuse
```

Prefer vulnerability-specific passes.

---

# Ignoring Framework Protection

Frameworks may provide:

```text
Autoescaping
CSRF protection
Parameterisation
Model validation
Authentication
Security headers
```

Do not report a finding without understanding the framework.

---

# Assuming Framework Protection

Framework protections can also be:

```text
Disabled
Bypassed
Misconfigured
Applied inconsistently
```

Review actual configuration and code.

---

# Ignoring Second-Order Data

Data can move:

```text
Request
   |
   v
Database
   |
   v
Background Job
   |
   v
Sink
```

Search the entire lifecycle.

---

# Ignoring Alternate Entry Points

A service may be reachable through:

```text
REST
GraphQL
gRPC
WebSocket
Admin interface
Background job
Message queue
```

Security controls may differ.

---

# Ignoring Custom Helpers

Applications frequently wrap dangerous APIs.

Example:

```java
public Response fetchUrl(
    String url
) {
    return internalHttpClient.fetch(url);
}
```

Searching only:

```text
HttpClient
```

may find the implementation but not every security-relevant caller.

Once the helper is identified:

```bash
rg -n \
'fetchUrl\(' \
.
```

---

# Ignoring Tests

Tests can reveal:

```text
Hidden routes
Roles
Permissions
Expected security controls
Example credentials
Business rules
Internal APIs
```

Do not automatically exclude them during reconnaissance.

---

# Final ripgrep Security Model

```text
                          REPOSITORY
                              |
                              v
                       TECHNOLOGY STACK
                              |
                              v
                         ROUTE SEARCH
                              |
                              v
                        ATTACK SURFACE
                              |
               +--------------+--------------+
               |                             |
               v                             v
          SOURCE SEARCH                 SINK SEARCH
               |                             |
               v                             v
       User-Controlled Data           Sensitive APIs
               |                             |
               +--------------+--------------+
                              |
                              v
                         VS CODE REVIEW
                              |
                    +---------+---------+
                    |                   |
                    v                   v
              SOURCE -> SINK      SINK -> SOURCE
                    |                   |
                    +---------+---------+
                              |
                              v
                       TRANSFORMATIONS
                              |
                              v
                     SECURITY CONTROLS
                              |
                      +-------+-------+
                      |               |
                      v               v
                  Effective       Ineffective
                      |               |
                      v               v
                  Protected        Candidate
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
                 ripgrep          Semgrep           OpenGrep
                                                        |
                                      +-----------------+
                                      |
                                      v
                                    CodeQL
```

The key questions remain:

```text
Where does attacker-controlled data enter?

Where does it travel?

Which security controls does it encounter?

Which security-sensitive operation does it reach?

Can the attacker meaningfully influence that operation?

What is the resulting security impact?
```

`ripgrep` helps answer the first part:

```text
Where is the interesting code?
```

Manual source review answers the important part:

```text
Is it actually vulnerable?
```

---

# Quick Reference

## Routes

```bash
rg -n \
'@RequestMapping|@GetMapping|@PostMapping|\[HttpGet|\[HttpPost|@.*\.route\(|\bpath\(|\bapp\.(get|post)|\brouter\.(get|post)' \
.
```

## Sources

```bash
rg -n \
'@RequestParam|@PathVariable|@RequestBody|Request\.Query|Request\.Form|\$_GET|\$_POST|request\.GET|request\.POST|request\.args|request\.form|req\.query|req\.params|req\.body' \
.
```

## Authentication

```bash
rg -ni \
'login|logout|authenticate|password|session|jwt|oauth|oidid|saml|mfa|totp' \
.
```

Note: if using this command directly, correct `oidid` to `oidc`:

```bash
rg -ni \
'login|logout|authenticate|password|session|jwt|oauth|oidc|saml|mfa|totp' \
.
```

## Authorisation

```bash
rg -ni \
'authori[sz]e|permission|role|policy|isAdmin|hasRole|hasAuthority|PreAuthorize|AllowAnonymous|permitAll' \
.
```

## SQL

```bash
rg -n \
'executeQuery|executeUpdate|createNativeQuery|SqlCommand|FromSqlRaw|mysqli_query|cursor\.execute|sequelize\.query|\$queryRaw' \
.
```

## Commands

```bash
rg -n \
'Runtime\.getRuntime|ProcessBuilder|Process\.Start|shell_exec|passthru|proc_open|os\.system|subprocess\.|child_process' \
.
```

## SSRF

```bash
rg -n \
'HttpClient|WebClient|RestTemplate|RestClient|URLConnection|requests\.|httpx\.|urlopen|curl_exec|axios\.|fetch\(' \
.
```

## Files

```bash
rg -n \
'FileInputStream|FileOutputStream|Files\.read|Files\.write|File\.Read|File\.Write|file_get_contents|file_put_contents|\bopen\(|fs\.readFile|fs\.writeFile' \
.
```

## Deserialisation

```bash
rg -n \
'ObjectInputStream|readObject\(|BinaryFormatter|unserialize\(|pickle\.load|yaml\.load|XMLDecoder|XStream|activateDefaultTyping' \
.
```

## XSS

```bash
rg -n \
'innerHTML|outerHTML|insertAdjacentHTML|document\.write|Html\.Raw|th:utext|dangerouslySetInnerHTML|v-html' \
.
```

## Redirects

```bash
rg -n \
'RedirectView|sendRedirect|Response\.Redirect|redirect\(|res\.redirect|location\.href|location\.assign|location\.replace' \
.
```

## Secrets

```bash
rg --hidden -ni \
-g '!.git/**' \
'password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|private[_-]?key|client[_-]?secret' \
.
```

## Security Configuration

```bash
rg -ni \
'cors|csrf|csp|Content-Security-Policy|SameSite|HttpOnly|Secure|allowedOrigins|permitAll|AllowAnonymous|trust proxy' \
.
```

## Background Processing

```bash
rg -ni \
'scheduled|scheduler|cron|background|worker|queue|consumer|listener|webhook' \
.
```

---

# Recommended Workflow

```text
rg --files
      |
      v
Identify Stack
      |
      v
Search Routes
      |
      v
Search Sources
      |
      v
Search Auth/Authz
      |
      v
Search Sinks
      |
      v
Open Candidates in VS Code
      |
      v
Trace Data Flow
      |
      v
Review Controls
      |
      v
Validate Candidate
      |
      v
Search Variants
      |
      +--> rg
      |
      +--> Semgrep
      |
      +--> OpenGrep
      |
      +--> CodeQL
```

---

# References

## ripgrep GitHub Repository

[ripgrep GitHub Repository](https://github.com/BurntSushi/ripgrep)

## ripgrep User Guide

[ripgrep User Guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md)

## ripgrep FAQ

[ripgrep FAQ](https://github.com/BurntSushi/ripgrep/blob/master/FAQ.md)

## Visual Studio Code Documentation

[docs](https://code.visualstudio.com/docs)

## OWASP Secure Code Review Cheat Sheet

[OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html)

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

## Semgrep Documentation

[docs](https://semgrep.dev/docs/)

## OpenGrep

[OpenGrep](https://opengrep.dev/)

## OpenGrep GitHub Repository

[OpenGrep GitHub Repository](https://github.com/opengrep/opengrep)

## CodeQL Documentation

[docs](https://codeql.github.com/docs/)

---

# Related Static Analysis Notes

```text
docs/source-code-review/static-analysis/index.md
docs/source-code-review/static-analysis/semgrep.md
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

docs/web/host-header-attacks.md
docs/web/http-security-headers.md
docs/web/http-request-smuggling.md
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md

docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/rate-limiting.md
docs/web/mass-assignment.md

docs/web/jwt.md
docs/web/oauth-oidc.md
docs/web/saml.md
docs/web/password-reset.md
docs/web/mfa.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md

docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md
```
