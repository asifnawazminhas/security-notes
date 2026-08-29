# PHP Source Code Review

PHP applications are particularly useful candidates for source code review because input sources, application logic, database operations, file-system operations, template rendering and dangerous execution functions are often visible directly in application code.

This note focuses on reviewing:

```text
PHP 8.x
Plain / Native PHP
Composer Applications
Laravel
Symfony
CodeIgniter
Slim
WordPress-style PHP applications
Custom PHP frameworks
Legacy PHP applications
```

The primary objective is to identify attacker-controlled input and determine whether it reaches a security-sensitive operation without an effective security control.

```text
HTTP Request
     |
     v
PHP Input Source
     |
     v
Routing / Controller
     |
     v
Validation
     |
     v
Authentication
     |
     v
Authorisation
     |
     v
Business Logic
     |
     v
SECURITY-SENSITIVE SINK
```

The basic review model is:

```text
SOURCE
   |
   v
USER-CONTROLLED DATA
   |
   v
TRANSFORMATIONS
   |
   +-- decoding
   +-- parsing
   +-- validation
   +-- normalisation
   +-- sanitisation
   +-- business logic
   |
   v
SECURITY CONTROL
   |
   v
SINK
   |
   v
EXPLOITABILITY
```

A source-code match is not automatically a vulnerability.

```text
grep match
    !=
vulnerability
```

Instead:

```text
Candidate Code
      |
      v
Data-Flow Analysis
      |
      v
Reachability
      |
      v
Security Controls
      |
      v
Exploitability
      |
      v
Impact
```

!!! warning "Authorised Security Testing"
    Perform source code review and dynamic validation only against applications and repositories for which you have explicit authorisation. Source repositories may contain credentials, API keys, cryptographic material, personal information and internal infrastructure details.

---

# Review Strategy

A practical PHP source review can be performed in the following order:

```text
1. Identify the PHP version

2. Identify the framework

3. Inspect Composer dependencies

4. Identify application entry points

5. Enumerate routes

6. Identify authentication

7. Identify authorisation

8. Identify attacker-controlled sources

9. Identify validation

10. Identify dangerous sinks

11. Trace source-to-sink paths

12. Review business logic

13. Review configuration

14. Search for secrets

15. Review dependencies

16. Review templates

17. Run static analysis

18. Perform variant analysis

19. Validate findings dynamically where authorised
```

---

# Identify the Application

Start by understanding the repository.

```bash
find . -maxdepth 3 -type f \( \
-name 'composer.json' \
-o -name 'composer.lock' \
-o -name 'artisan' \
-o -name 'symfony.lock' \
-o -name 'wp-config.php' \
-o -name 'index.php' \
-o -name '.env' \
-o -name '.env.example' \
\) -print
```

Common indicators:

| File | Possible Technology |
|---|---|
| `composer.json` | Composer-managed PHP |
| `artisan` | Laravel |
| `symfony.lock` | Symfony |
| `wp-config.php` | WordPress |
| `application/config/` | Older CodeIgniter |
| `app/Config/` | CodeIgniter 4 |
| `vendor/` | Composer dependencies |
| `.env` | Environment configuration |

---

# Identify PHP Version

Check Composer requirements:

```bash
rg -n \
'"php"\s*:' \
--glob 'composer.json' \
.
```

Example:

```json
"require": {
    "php": "^8.3"
}
```

Also inspect:

```text
Dockerfile
docker-compose.yml
.github/workflows/
.gitlab-ci.yml
composer.json
composer.lock
```

Search:

```bash
rg -n -i \
'php:[0-9]|php-version|FROM php|platform.*php' \
.
```

Knowing the PHP version matters when reviewing:

```text
Deprecated APIs
Removed APIs
Framework compatibility
Dependency vulnerabilities
Language behaviour
Security defaults
```

---

# Composer

Composer is the primary PHP dependency manager.

Important files:

```text
composer.json
composer.lock
```

Inspect:

```bash
cat composer.json
```

Search dependencies:

```bash
rg -n \
'"require"|"require-dev"|"repositories"|"autoload"|"scripts"' \
composer.json
```

---

# Identify Frameworks

Quick search:

```bash
rg -n -i \
'laravel|symfony|codeigniter|slim|cakephp|yii|wordpress|woocommerce' \
composer.json composer.lock 2>/dev/null
```

---

# Laravel

Indicators include:

```text
artisan
app/
bootstrap/
config/
database/
public/
resources/
routes/
storage/
```

Routes commonly exist in:

```text
routes/web.php
routes/api.php
routes/console.php
```

---

# Symfony

Common structure:

```text
bin/
config/
public/
src/
templates/
var/
vendor/
```

Routes may exist in:

```text
config/routes.yaml
config/routes/
Controller annotations / attributes
```

---

# Native PHP

Older or custom applications may use:

```text
index.php
login.php
admin.php
api.php
includes/
inc/
lib/
config/
```

Each PHP file may effectively represent an endpoint.

---

# Application Entry Points

Find PHP files:

```bash
find . -type f -name '*.php' \
-not -path './vendor/*' \
-not -path './node_modules/*'
```

Prioritise:

```text
public/index.php
index.php
api.php
login.php
admin.php
upload.php
download.php
callback.php
webhook.php
```

---

# Route Discovery

Route discovery depends heavily on the framework.

---

# Laravel Routes

Search:

```bash
rg -n \
'Route::(get|post|put|patch|delete|options|any|match|resource|apiResource)' \
--glob '*.php' \
.
```

Example:

```php
Route::get(
    '/users/{id}',
    [UserController::class, 'show']
);
```

Route:

```text
GET /users/{id}
```

---

# Laravel Route Groups

Review:

```php
Route::middleware(['auth'])->group(function () {
    ...
});
```

Search:

```bash
rg -n \
'Route::middleware|Route::prefix|Route::group|middleware\(' \
--glob '*.php' \
.
```

Route security may be inherited from groups.

Do not review individual routes in isolation.

---

# Symfony Routes

Modern Symfony commonly uses attributes:

```php
#[Route('/users/{id}', methods: ['GET'])]
public function show(int $id)
{
    ...
}
```

Search:

```bash
rg -n \
'#\[Route|@Route' \
--glob '*.php' \
.
```

Also inspect:

```text
config/routes.yaml
config/routes/
```

---

# Generic Route Search

```bash
rg -n \
'Route::|#\[Route|@Route|->get\(|->post\(|->put\(|->patch\(|->delete\(' \
--glob '*.php' \
.
```

Expect false positives.

---

# Build a Route Inventory

Create a table:

| Method | Route | Handler | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/users/{id}` | `UserController::show` | Required | Ownership |
| POST | `/users` | `UserController::store` | Required | Admin |
| POST | `/login` | `AuthController::login` | Public | N/A |
| POST | `/upload` | `FileController::upload` | Required | User |
| GET | `/admin` | `AdminController` | Required | Admin |

This route map becomes the basis for the rest of the review.

---

# PHP Input Sources

PHP provides several superglobal arrays containing attacker-controlled request data.

The most important are:

```text
$_GET
$_POST
$_REQUEST
$_COOKIE
$_FILES
$_SERVER
```

Other sources may include:

```text
php://input
HTTP headers
JSON bodies
Route parameters
Session values influenced by previous requests
Database values containing stored user input
Message queues
Uploaded files
```

---

# Search PHP Superglobals

```bash
rg -n \
'\$_GET|\$_POST|\$_REQUEST|\$_COOKIE|\$_FILES|\$_SERVER' \
--glob '*.php' \
.
```

This is one of the highest-value first searches in a PHP application.

---

# $_GET

Example:

```php
$id = $_GET['id'];
```

Source:

```text
GET parameter id
```

Trace:

```text
$_GET['id']
     |
     v
$id
     |
     v
Application Logic
     |
     v
Sink
```

---

# $_POST

Example:

```php
$username = $_POST['username'];
```

Trace where the value is used.

---

# $_REQUEST

Search:

```bash
rg -n \
'\$_REQUEST' \
--glob '*.php' \
.
```

`$_REQUEST` deserves additional attention because the exact sources included depend on PHP configuration.

Avoid assuming that it represents only one request location.

---

# Cookies

Search:

```bash
rg -n \
'\$_COOKIE' \
--glob '*.php' \
.
```

Cookies are attacker-controlled input.

Never assume:

```text
Cookie
=
Trusted
```

even if the application originally created the cookie.

---

# $_SERVER

High-value keys include:

```text
HTTP_HOST
HTTP_X_FORWARDED_FOR
HTTP_X_FORWARDED_HOST
HTTP_REFERER
HTTP_USER_AGENT
REQUEST_URI
REMOTE_ADDR
REQUEST_METHOD
```

Search:

```bash
rg -n \
'HTTP_HOST|HTTP_X_FORWARDED_FOR|HTTP_X_FORWARDED_HOST|HTTP_REFERER|HTTP_USER_AGENT|REQUEST_URI|REMOTE_ADDR' \
--glob '*.php' \
.
```

---

# Raw Request Bodies

Search:

```bash
rg -n \
'php://input|file_get_contents\s*\(\s*["'\'']php://input' \
--glob '*.php' \
.
```

Example:

```php
$body = file_get_contents('php://input');
```

This may contain:

```text
JSON
XML
Serialized data
Custom protocol data
```

---

# JSON Input

Search:

```bash
rg -n \
'json_decode\(' \
--glob '*.php' \
.
```

Example:

```php
$data = json_decode(
    file_get_contents('php://input'),
    true
);
```

The resulting values remain attacker-controlled.

---

# Laravel Input Sources

Common Laravel sources include:

```php
$request->input()
$request->query()
$request->post()
$request->header()
$request->cookie()
$request->file()
$request->all()
$request->only()
$request->except()
```

Search:

```bash
rg -n \
'\$request->(input|query|post|header|cookie|file|all|only|except)\(' \
--glob '*.php' \
.
```

---

# Symfony Input Sources

Common Symfony request APIs include:

```php
$request->query->get()
$request->request->get()
$request->headers->get()
$request->cookies->get()
$request->files->get()
$request->getContent()
```

Search:

```bash
rg -n \
'\$request->(query|request|headers|cookies|files)->get|\$request->getContent\(' \
--glob '*.php' \
.
```

---

# Validation

Validation is important, but validation alone does not make input safe for every sink.

For example:

```text
Length validation
    !=
SQL injection protection

Regex validation
    !=
Authorisation

HTML sanitisation
    !=
Command injection protection
```

---

# Native PHP Validation

Common functions include:

```text
filter_input()
filter_var()
ctype_digit()
is_numeric()
preg_match()
intval()
```

Search:

```bash
rg -n \
'filter_input\(|filter_var\(|ctype_|is_numeric\(|preg_match\(|intval\(' \
--glob '*.php' \
.
```

---

# filter_input

Example:

```php
$id = filter_input(
    INPUT_GET,
    'id',
    FILTER_VALIDATE_INT
);
```

This can enforce the expected type for an integer identifier.

It does not provide object-level authorisation.

---

# Laravel Validation

Search:

```bash
rg -n \
'->validate\(|Validator::make|FormRequest|rules\(\)' \
--glob '*.php' \
.
```

Example:

```php
$request->validate([
    'email' => 'required|email',
]);
```

Review whether validation rules match the security requirements of the downstream operation.

---

# Symfony Validation

Search:

```bash
rg -n \
'Assert\\\\|ValidatorInterface|->validate\(' \
--glob '*.php' \
.
```

---

# Authentication

Locate:

```text
Login handlers
Authentication middleware
Session creation
Token validation
JWT handling
OAuth
SAML
API keys
```

Search:

```bash
rg -n -i \
'login|authenticate|authentication|auth::|middleware.*auth|session|jwt|bearer|oauth|saml' \
--glob '*.php' \
.
```

---

# Laravel Authentication

Search:

```bash
rg -n \
'Auth::|auth\(\)|middleware\(["'\'']auth|->middleware\(["'\'']auth' \
--glob '*.php' \
.
```

Common patterns:

```php
Auth::user();

auth()->user();

$request->user();
```

---

# Symfony Security

Search:

```bash
rg -n \
'isGranted\(|denyAccessUnlessGranted|Security\b|UserInterface|AuthorizationCheckerInterface' \
--glob '*.php' \
.
```

Also inspect:

```text
config/packages/security.yaml
```

---

# Authorisation

Authentication answers:

```text
Who are you?
```

Authorisation answers:

```text
Are you allowed to perform this operation?
```

Search for:

```text
Roles
Permissions
Policies
Gates
Voters
Ownership
Tenant IDs
Administrative checks
```

---

# Laravel Gates and Policies

Search:

```bash
rg -n \
'Gate::|authorize\(|can\(|cannot\(|Policy|middleware.*can:' \
--glob '*.php' \
.
```

Example:

```php
$this->authorize(
    'view',
    $document
);
```

---

# Symfony Authorisation

Search:

```bash
rg -n \
'isGranted\(|denyAccessUnlessGranted|Voter|supports\(|voteOnAttribute\(' \
--glob '*.php' \
.
```

---

# IDOR / BOLA

Object-level authorisation is a major source-review target.

Example:

```php
$id = $_GET['id'];

$document = Document::find($id);

return $document;
```

Critical question:

```text
Where is permission checked?
```

---

# Laravel IDOR Candidates

Search:

```bash
rg -n \
'::find\(|::findOrFail\(|->find\(|where\(["'\'']id|whereKey\(' \
--glob '*.php' \
.
```

Example:

```php
$order = Order::findOrFail($id);
```

This confirms that an order exists.

It does not by itself confirm that the authenticated user is authorised to access it.

---

# Ownership Scoping

Compare:

```php
Order::findOrFail($id);
```

with a design such as:

```php
$user->orders()
    ->findOrFail($id);
```

The second approach may scope the lookup to objects associated with the authenticated user.

The exact secure implementation depends on the application's authorisation model.

---

# Tenant Isolation

Search:

```bash
rg -n -i \
'tenant|tenant_id|tenantid|organization_id|organisation_id|account_id|company_id' \
--glob '*.php' \
.
```

Review every security-sensitive object lookup.

Conceptually:

```text
Object ID
    +
Current Tenant
      |
      v
Database Lookup
```

---

# Mass Assignment

Mass assignment is particularly relevant to PHP frameworks with ORM models.

Laravel examples include:

```php
User::create($request->all());

$user->update($request->all());
```

Search:

```bash
rg -n \
'->all\(\)|::create\(|->create\(|->update\(|->fill\(' \
--glob '*.php' \
.
```

---

# Laravel fillable / guarded

Search:

```bash
rg -n \
'\$fillable|\$guarded' \
--glob '*.php' \
.
```

Review security-sensitive fields such as:

```text
role
is_admin
admin
verified
email_verified_at
tenant_id
owner_id
status
balance
credit
permissions
```

Do not conclude mass assignment exists merely because `create()` or `update()` is present.

Determine:

```text
Input
Model configuration
DTO / request mapping
Allowed attributes
Business logic
```

Refer to:

```text
docs/web/mass-assignment.md
```

---

# SQL Injection

PHP applications commonly access databases using:

```text
PDO
MySQLi
Framework query builders
ORMs
Raw SQL
```

The fundamental question is:

```text
Can attacker-controlled input alter SQL syntax?
```

---

# PDO

High-value functions:

```text
PDO::query()
PDO::exec()
PDO::prepare()
PDOStatement::execute()
PDO::quote()
```

Search:

```bash
rg -n \
'->query\(|->exec\(|->prepare\(|->execute\(|PDO::' \
--glob '*.php' \
.
```

---

# Unsafe PDO Example

```php
$id = $_GET['id'];

$sql =
    "SELECT * FROM users WHERE id = " .
    $id;

$result = $pdo->query($sql);
```

Data flow:

```text
$_GET['id']
     |
     v
$id
     |
     v
SQL concatenation
     |
     v
PDO::query()
```

---

# Prepared Statements

Preferred pattern:

```php
$stmt = $pdo->prepare(
    'SELECT * FROM users WHERE id = :id'
);

$stmt->execute([
    'id' => $id
]);
```

The value is passed separately from the SQL structure.

---

# Prepared Statements Are Not Magic

This can still be unsafe:

```php
$column = $_GET['sort'];

$sql =
    "SELECT * FROM users ORDER BY " .
    $column;

$stmt = $pdo->prepare($sql);
$stmt->execute();
```

Prepared statement parameters represent data values.

They generally cannot represent arbitrary SQL identifiers or syntax such as:

```text
Table names
Column names
SQL keywords
Sort direction
```

Use explicit server-side mappings.

Example:

```php
$allowed = [
    'name' => 'name',
    'date' => 'created_at'
];

$column =
    $allowed[$_GET['sort']] ?? 'name';
```

---

# MySQLi

Search:

```bash
rg -n \
'mysqli_query\(|mysqli_prepare\(|->query\(|->prepare\(' \
--glob '*.php' \
.
```

Unsafe candidate:

```php
$sql =
    "SELECT * FROM users WHERE name = '" .
    $_GET['name'] .
    "'";

mysqli_query($connection, $sql);
```

---

# MySQLi Prepared Statement

Example:

```php
$stmt = $mysqli->prepare(
    'SELECT * FROM users WHERE name = ?'
);

$stmt->bind_param(
    's',
    $name
);

$stmt->execute();
```

---

# Historical mysql_* API

Older source code may contain:

```text
mysql_query()
mysql_connect()
mysql_real_escape_string()
```

Search:

```bash
rg -n \
'mysql_query\(|mysql_connect\(|mysql_real_escape_string\(' \
--glob '*.php' \
.
```

These belong to the old `mysql` extension and should be treated as legacy code patterns rather than current PHP database APIs.

---

# Laravel Raw SQL

High-value searches:

```bash
rg -n \
'DB::raw|whereRaw|orWhereRaw|havingRaw|orderByRaw|selectRaw|groupByRaw|statement\(|unprepared\(' \
--glob '*.php' \
.
```

These deserve manual inspection.

---

# Query Builder

Normal query-builder usage such as:

```php
DB::table('users')
    ->where('email', $email)
    ->first();
```

is different from:

```php
DB::table('users')
    ->whereRaw(
        "email = '$email'"
    )
    ->first();
```

Trace how raw expressions are constructed.

---

# SQL Search

```bash
rg -n \
'PDO|mysqli|->query\(|->exec\(|->prepare\(|DB::raw|whereRaw|orWhereRaw|havingRaw|orderByRaw|selectRaw|unprepared\(' \
--glob '*.php' \
.
```

Refer to:

```text
docs/web/sql-injection.md
```

---

# NoSQL Injection

PHP applications may interact with:

```text
MongoDB
Redis
Elasticsearch
CouchDB
```

Search:

```bash
rg -n -i \
'mongodb|MongoDB\\\\|redis|elasticsearch|Elastic\\\\' \
--glob '*.php' \
.
```

Review dynamic query structures derived from:

```text
JSON
Request arrays
User-controlled operators
Filters
Aggregation pipelines
```

---

# MongoDB

Example review pattern:

```php
$filter = $_POST['filter'];

$collection->find($filter);
```

Determine whether attacker-controlled arrays can introduce query operators.

Refer to:

```text
docs/web/nosql-injection.md
```

---

# LDAP Injection

PHP provides LDAP APIs such as:

```text
ldap_search()
ldap_list()
ldap_read()
ldap_bind()
```

Search:

```bash
rg -n \
'ldap_(search|list|read|bind|compare)\(' \
--glob '*.php' \
.
```

---

# LDAP Filter Construction

Candidate:

```php
$username = $_GET['username'];

$filter =
    "(uid=" .
    $username .
    ")";

ldap_search(
    $ldap,
    $baseDn,
    $filter
);
```

Trace attacker input into:

```text
LDAP filters
Distinguished names
Search bases
```

---

# LDAP Escaping

Search:

```bash
rg -n \
'ldap_escape\(' \
--glob '*.php' \
.
```

Encoding requirements differ between:

```text
LDAP filter values
LDAP distinguished names
```

Review the correct context.

Refer to:

```text
docs/web/ldap-injection.md
```

---

# OS Command Injection

PHP exposes several process-execution functions.

High-value functions include:

```text
system()
exec()
shell_exec()
passthru()
popen()
proc_open()
backtick operator
```

Search:

```bash
rg -n \
'\bsystem\s*\(|\bexec\s*\(|shell_exec\s*\(|passthru\s*\(|popen\s*\(|proc_open\s*\(' \
--glob '*.php' \
.
```

---

# Unsafe Command Example

```php
$host = $_GET['host'];

system(
    'ping -c 1 ' . $host
);
```

Data flow:

```text
$_GET['host']
     |
     v
$host
     |
     v
Command concatenation
     |
     v
system()
```

---

# shell_exec

Candidate:

```php
$output =
    shell_exec(
        'convert ' .
        $filename .
        ' output.png'
    );
```

Trace:

```text
filename
```

back to its source.

---

# exec

Search:

```bash
rg -n \
'\bexec\s*\(' \
--glob '*.php' \
.
```

Remember that PHP also contains application methods named `exec`.

Inspect context.

---

# Backtick Operator

PHP can execute commands using backticks:

```php
$output = `whoami`;
```

Finding dynamic backticks with simple regex is less reliable.

Search manually around suspicious command construction and use static-analysis tools where possible.

---

# Escaping Functions

Functions include:

```text
escapeshellarg()
escapeshellcmd()
```

Search:

```bash
rg -n \
'escapeshellarg\(|escapeshellcmd\(' \
--glob '*.php' \
.
```

Their presence does not automatically make arbitrary process execution safe.

Review:

```text
Command construction
Argument boundaries
Shell usage
Executable selection
Option injection
Application-specific argument semantics
```

---

# Command Injection Review

```text
Attacker Input
      |
      v
Command / Argument Construction
      |
      v
Escaping / Validation
      |
      v
Shell?
      |
      v
system / exec / shell_exec / proc_open
```

Refer to:

```text
docs/web/command-injection.md
```

---

# Server-Side Request Forgery

PHP provides multiple network-capable APIs.

High-value functions include:

```text
file_get_contents()
fopen()
readfile()
curl_init()
curl_setopt()
curl_exec()
fsockopen()
stream_socket_client()
```

Search:

```bash
rg -n \
'file_get_contents\(|fopen\(|readfile\(|curl_init\(|curl_setopt\(|curl_exec\(|fsockopen\(|stream_socket_client\(' \
--glob '*.php' \
.
```

---

# file_get_contents SSRF Candidate

```php
$url = $_GET['url'];

$content =
    file_get_contents($url);
```

Data flow:

```text
$_GET['url']
      |
      v
$url
      |
      v
file_get_contents()
      |
      v
Network Request
```

`file_get_contents()` may access URLs when the relevant stream wrappers and configuration permit it.

Determine actual runtime configuration.

---

# cURL

Search:

```bash
rg -n \
'CURLOPT_URL|CURLOPT_FOLLOWLOCATION|curl_setopt|curl_setopt_array|curl_exec' \
--glob '*.php' \
.
```

Candidate:

```php
$ch = curl_init();

curl_setopt(
    $ch,
    CURLOPT_URL,
    $_POST['url']
);

$result = curl_exec($ch);
```

---

# SSRF Review

Review:

```text
Scheme
Hostname
Port
DNS resolution
Redirect handling
Proxy behaviour
Network egress
Internal destinations
Cloud metadata
Alternate IP representations
```

A URL parser is not an authorisation mechanism.

Refer to:

```text
docs/web/ssrf.md
```

---

# Path Traversal

High-value PHP file-system functions include:

```text
file_get_contents()
file_put_contents()
fopen()
readfile()
unlink()
copy()
rename()
mkdir()
rmdir()
scandir()
glob()
```

Search:

```bash
rg -n \
'file_get_contents\(|file_put_contents\(|fopen\(|readfile\(|unlink\(|copy\(|rename\(|scandir\(|glob\(' \
--glob '*.php' \
.
```

---

# Path Traversal Candidate

```php
$file = $_GET['file'];

$content =
    file_get_contents(
        '/var/www/files/' .
        $file
    );
```

Trace:

```text
file
 |
 v
Path Construction
 |
 v
File Operation
```

---

# basename

Search:

```bash
rg -n \
'basename\(|realpath\(' \
--glob '*.php' \
.
```

`basename()` may be useful for some filename-only designs, but it is not a universal path-security solution.

---

# realpath

Conceptually:

```text
User Input
    |
    v
Resolve Against Base
    |
    v
Canonicalise
    |
    v
Verify Containment
    |
    v
File Operation
```

Be careful because:

```php
realpath()
```

returns `false` when the target does not exist, which matters for file-creation workflows.

Refer to:

```text
docs/web/path-traversal.md
```

---

# File Inclusion

PHP file inclusion is an especially important review area.

Functions:

```text
include
include_once
require
require_once
```

Search:

```bash
rg -n \
'\b(include|include_once|require|require_once)\b' \
--glob '*.php' \
.
```

---

# Dynamic Include Candidate

```php
$page = $_GET['page'];

include(
    'pages/' .
    $page .
    '.php'
);
```

Data flow:

```text
$_GET['page']
     |
     v
$page
     |
     v
Dynamic path
     |
     v
include()
```

Review:

```text
Path traversal
Local file inclusion
Stream wrappers
Remote inclusion configuration
File execution semantics
Allowlisting
```

---

# PHP Stream Wrappers

PHP supports stream wrappers such as:

```text
file://
php://
data://
http://
https://
ftp://
phar://
zip://
```

Available wrappers depend on runtime configuration and installed extensions.

Inspect:

```php
stream_get_wrappers();
```

during authorised local testing if appropriate.

---

# Remote File Inclusion

Remote inclusion behaviour depends on configuration such as:

```text
allow_url_fopen
allow_url_include
```

Do not assume remote inclusion is possible solely because a dynamic `include()` exists.

---

# File Inclusion Search

```bash
rg -n \
'\b(include|include_once|require|require_once)\b|file_get_contents\(|readfile\(' \
--glob '*.php' \
.
```

Refer to:

```text
docs/web/file-inclusion.md
```

---

# File Upload

Primary PHP source:

```text
$_FILES
```

Search:

```bash
rg -n \
'\$_FILES|move_uploaded_file\(|is_uploaded_file\(' \
--glob '*.php' \
.
```

---

# Upload Example

```php
$file =
    $_FILES['upload'];

move_uploaded_file(
    $file['tmp_name'],
    '/var/www/uploads/' .
    $file['name']
);
```

Review:

```text
Original filename
Generated filename
Path handling
Extension
MIME type
File signature
Content
Size
Destination
Web accessibility
Execution possibility
Overwrite behaviour
Downstream processing
```

---

# Upload Metadata

Common fields:

```php
$_FILES['file']['name']
$_FILES['file']['type']
$_FILES['file']['tmp_name']
$_FILES['file']['error']
$_FILES['file']['size']
```

Treat:

```text
name
type
```

as attacker-controlled metadata.

Do not trust the client-supplied MIME type.

---

# MIME Detection

Search:

```bash
rg -n \
'finfo_file\(|finfo_buffer\(|mime_content_type\(|getimagesize\(' \
--glob '*.php' \
.
```

Content detection is one layer of an upload defence.

It does not replace:

```text
Safe storage
Generated names
Extension policy
Execution prevention
Authorisation
Size limits
Downstream parser security
```

---

# move_uploaded_file

Search:

```bash
rg -n \
'move_uploaded_file\(' \
--glob '*.php' \
.
```

Trace the destination path.

---

# Archive Extraction

Search:

```bash
rg -n \
'ZipArchive|->extractTo\(|PharData|RarArchive' \
--glob '*.php' \
.
```

Review archive extraction for entry-path traversal.

Conceptually:

```text
Archive Entry
      |
      v
Entry Name
      |
      v
Destination Path
      |
      v
Containment Check
      |
      v
Write
```

Refer to:

```text
docs/web/file-upload.md
```

---

# Insecure Deserialization

The primary native PHP sink is:

```text
unserialize()
```

Search:

```bash
rg -n \
'\bunserialize\s*\(' \
--glob '*.php' \
.
```

---

# Dangerous Candidate

```php
$data =
    unserialize(
        $_COOKIE['settings']
    );
```

Data flow:

```text
Cookie
  |
  v
unserialize()
  |
  v
Object Instantiation
```

Untrusted data should not be passed to `unserialize()`.

---

# PHP Magic Methods

Object injection impact often depends on available classes and magic methods.

Search:

```bash
rg -n \
'function\s+__(wakeup|destruct|toString|call|callStatic|get|set|invoke|unserialize|serialize)\s*\(' \
--glob '*.php' \
.
```

High-value methods include:

```text
__wakeup()
__unserialize()
__destruct()
__toString()
__call()
__invoke()
```

---

# Gadget Review

Conceptually:

```text
Untrusted Serialized Data
          |
          v
unserialize()
          |
          v
Object Graph
          |
          v
Magic Method
          |
          v
Security-Sensitive Operation
```

Potential operations include:

```text
File write
File delete
Command execution
Network request
Template rendering
Database operation
```

---

# allowed_classes

Search:

```bash
rg -n \
'allowed_classes' \
--glob '*.php' \
.
```

Do not treat:

```php
['allowed_classes' => false]
```

as justification for accepting attacker-controlled serialized data.

Prefer safer interchange formats such as JSON when the data crosses an untrusted boundary.

Refer to:

```text
docs/web/deserialization.md
```

---

# PHAR

Search:

```bash
rg -n -i \
'phar://|Phar\b|PharData' \
--glob '*.php' \
.
```

When reviewing older applications in particular, consider whether PHAR handling interacts with:

```text
File operations
Uploaded files
Legacy dependencies
Deserialization behaviour
```

Validate against the actual PHP version and application stack rather than assuming historical exploitation behaviour still applies.

---

# XML External Entity Injection

PHP XML parsing may involve:

```text
DOMDocument
SimpleXML
XMLReader
libxml
```

Search:

```bash
rg -n \
'DOMDocument|simplexml_load|XMLReader|libxml_' \
--glob '*.php' \
.
```

---

# DOMDocument

Example:

```php
$doc =
    new DOMDocument();

$doc->loadXML($xml);
```

Do not automatically classify this as XXE.

Review:

```text
PHP version
libxml version
Parser options
External entity behaviour
DTD processing
Network access
Input controllability
```

---

# SimpleXML

Search:

```bash
rg -n \
'simplexml_load_string|simplexml_load_file' \
--glob '*.php' \
.
```

Review parser options and runtime behaviour.

---

# LIBXML Options

Search:

```bash
rg -n \
'LIBXML_|libxml_' \
--glob '*.php' \
.
```

Options may materially alter parser behaviour.

Refer to:

```text
docs/web/xxe.md
```

---

# Server-Side Template Injection

PHP applications may use:

```text
Twig
Blade
Smarty
Latte
Mustache
Plates
```

Search:

```bash
rg -n -i \
'twig|blade|smarty|latte|mustache|plates|render\(|template' \
--glob '*.php' \
.
```

---

# Twig

Search:

```bash
rg -n \
'Twig\\\\|createTemplate\(|->render\(' \
--glob '*.php' \
.
```

The critical distinction is:

```text
User input used as template data
```

versus:

```text
User input used as template source
```

---

# Dynamic Twig Template

Candidate:

```php
$template =
    $twig->createTemplate(
        $userInput
    );

echo $template->render();
```

Trace whether the template source is attacker-controlled.

---

# Blade

Laravel Blade templates commonly reside in:

```text
resources/views/
```

Find:

```bash
find . -type f -name '*.blade.php'
```

---

# Blade Output

Common syntax:

```text
{{ $value }}
{!! $value !!}
```

Search unescaped output:

```bash
rg -n \
'\{!!' \
--glob '*.blade.php' \
.
```

Unescaped Blade output deserves review when the value may contain attacker-controlled HTML.

---

# Smarty

Search:

```bash
rg -n -i \
'smarty|->fetch\(|->display\(' \
--glob '*.php' \
.
```

Review dynamically constructed template source and configuration.

Refer to:

```text
docs/web/ssti.md
```

---

# Cross-Site Scripting

PHP output sinks include:

```text
echo
print
printf
sprintf when later rendered
templates
JSON embedded into HTML
```

Search:

```bash
rg -n \
'\becho\b|\bprint\b|printf\(' \
--glob '*.php' \
.
```

Expect many false positives.

---

# XSS Candidate

```php
$name = $_GET['name'];

echo $name;
```

Whether this is exploitable depends on the response context.

---

# htmlspecialchars

Search:

```bash
rg -n \
'htmlspecialchars\(|htmlentities\(' \
--glob '*.php' \
.
```

Example:

```php
echo htmlspecialchars(
    $name,
    ENT_QUOTES | ENT_SUBSTITUTE,
    'UTF-8'
);
```

Context matters.

HTML-text encoding is not automatically correct for:

```text
JavaScript
CSS
URL
HTML attributes
```

---

# XSS Contexts

Review output according to:

```text
HTML body
HTML attribute
JavaScript
CSS
URL
JSON inside HTML
DOM
```

Use context-appropriate encoding.

---

# Stored XSS

Trace:

```text
HTTP Input
    |
    v
Database
    |
    v
Later Request
    |
    v
Template / echo
```

Stored values are not automatically trusted merely because they came from the database.

---

# Laravel Blade

Review:

```text
{{ ... }}
```

versus:

```text
{!! ... !!}
```

Do not automatically classify ordinary Blade output as vulnerable.

Review framework escaping and the exact output context.

Refer to:

```text
docs/web/xss.md
docs/web/html-injection.md
```

---

# Open Redirect

PHP redirects commonly use:

```php
header('Location: ...');
```

Search:

```bash
rg -n -i \
'header\s*\(\s*["'\'']Location:|redirect\(' \
--glob '*.php' \
.
```

---

# Redirect Candidate

```php
$url = $_GET['next'];

header(
    'Location: ' . $url
);
```

Trace whether users can select arbitrary external destinations.

---

# Laravel Redirects

Search:

```bash
rg -n \
'redirect\(|Redirect::|->away\(|redirect\(\)->away' \
--glob '*.php' \
.
```

Pay particular attention to functionality intentionally allowing external URLs.

Refer to:

```text
docs/web/open-redirect.md
```

---

# HTTP Header Injection

Search:

```bash
rg -n \
'\bheader\s*\(' \
--glob '*.php' \
.
```

Trace attacker-controlled data into:

```text
Location
Content-Disposition
Set-Cookie
Custom headers
Content-Type
```

Modern PHP versions contain protections against some malformed headers, but application-specific header construction still deserves review.

---

# Host Header Attacks

PHP exposes the Host header through:

```php
$_SERVER['HTTP_HOST']
```

Search:

```bash
rg -n \
'HTTP_HOST|X_FORWARDED_HOST|SERVER_NAME' \
--glob '*.php' \
.
```

Review usage in:

```text
Password reset links
Email verification links
Absolute URLs
Redirects
Tenant selection
Security decisions
```

---

# Password Reset Example

Candidate:

```php
$link =
    'https://' .
    $_SERVER['HTTP_HOST'] .
    '/reset?token=' .
    $token;
```

Determine whether the host is validated or derived from trusted configuration.

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# CSRF

Look for state-changing endpoints:

```text
POST
PUT
PATCH
DELETE
```

Then determine whether anti-CSRF protection is applied where required.

---

# Native PHP CSRF

Search:

```bash
rg -n -i \
'csrf|xsrf|nonce' \
--glob '*.php' \
.
```

Review:

```text
Token generation
Token storage
Token comparison
Token binding
Token rotation
Protected operations
```

---

# Laravel CSRF

Laravel commonly handles CSRF through middleware for web routes.

Search:

```bash
rg -n \
'VerifyCsrfToken|validateCsrfTokens|except.*csrf|csrf_token|@csrf' \
--glob '*.php' \
--glob '*.blade.php' \
.
```

Review exclusions.

---

# Symfony CSRF

Search:

```bash
rg -n \
'CsrfToken|CsrfTokenManager|isCsrfTokenValid|csrf_token' \
--glob '*.php' \
--glob '*.twig' \
.
```

---

# CSRF Review

Do not report a missing token without understanding the authentication model.

A stateless API using manually attached bearer tokens has different CSRF properties from a browser application using session cookies.

Refer to:

```text
docs/web/csrf.md
```

---

# CORS

PHP applications may set CORS headers directly.

Search:

```bash
rg -n -i \
'access-control-allow-origin|access-control-allow-credentials|access-control-allow-methods|access-control-allow-headers' \
--glob '*.php' \
.
```

Candidate:

```php
header(
    'Access-Control-Allow-Origin: ' .
    $_SERVER['HTTP_ORIGIN']
);
```

Review:

```text
Origin validation
Credentials
Sensitive responses
Methods
Headers
Preflight handling
```

Do not classify permissive CORS as exploitable without demonstrating meaningful cross-origin access.

Refer to:

```text
docs/web/cors.md
```

---

# Session Management

PHP sessions commonly use:

```text
session_start()
$_SESSION
session_regenerate_id()
session_destroy()
```

Search:

```bash
rg -n \
'session_start\(|\$_SESSION|session_regenerate_id\(|session_destroy\(|session_set_cookie_params\(' \
--glob '*.php' \
.
```

---

# Session Fixation

Search:

```bash
rg -n \
'session_regenerate_id\(' \
--glob '*.php' \
.
```

Review session-ID rotation around:

```text
Login
Privilege elevation
MFA completion
Password changes
Account switching
```

Do not infer a vulnerability solely from the absence of a grep match because frameworks may manage sessions elsewhere.

---

# Session Cookie Configuration

Search:

```bash
rg -n -i \
'session\.cookie_secure|session\.cookie_httponly|session\.cookie_samesite|session_set_cookie_params' \
.
```

Also inspect:

```text
php.ini
Docker configuration
Web server configuration
Framework configuration
```

---

# JWT

Search:

```bash
rg -n -i \
'jwt|firebase/php-jwt|lcobucci/jwt|jsonwebtoken' \
composer.json composer.lock --glob '*.php' 2>/dev/null
```

Common PHP JWT libraries include:

```text
firebase/php-jwt
lcobucci/jwt
```

---

# JWT Review

Determine:

```text
Signature verification
Allowed algorithms
Signing key
Issuer
Audience
Expiration
Not-before
Key selection
Claims
```

Search:

```bash
rg -n \
'JWT::decode|JWT::encode|Configuration::for|parse\(|validate\(' \
--glob '*.php' \
.
```

Refer to:

```text
docs/web/jwt.md
```

---

# OAuth / OIDC

Search:

```bash
rg -n -i \
'oauth|openid|oidc|client_id|client_secret|redirect_uri|authorization_code|code_verifier|code_challenge' \
--glob '*.php' \
.
```

Review:

```text
State
Nonce
PKCE
Redirect URI
Token validation
Issuer
Audience
Account linking
```

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# SAML

Search:

```bash
rg -n -i \
'saml|onelogin|simplesaml|xmlseclibs' \
composer.json composer.lock --glob '*.php' 2>/dev/null
```

Review:

```text
Signature validation
Response validation
Assertion validation
Issuer
Audience
Destination
Recipient
Replay protection
Certificate trust
Attribute mapping
```

Refer to:

```text
docs/web/saml.md
```

---

# Password Reset

Search:

```bash
rg -n -i \
'forgot.?password|reset.?password|password.?reset|reset.?token' \
--glob '*.php' \
.
```

Review:

```text
Token generation
Entropy
Expiration
Single use
Account binding
User enumeration
Reset URL construction
Rate limiting
Session invalidation
```

---

# Token Generation

Search:

```bash
rg -n \
'random_bytes\(|random_int\(|openssl_random_pseudo_bytes\(|mt_rand\(|rand\(' \
--glob '*.php' \
.
```

Security-sensitive random values should use a cryptographically secure source.

---

# MFA

Search:

```bash
rg -n -i \
'totp|otp|mfa|2fa|two.?factor|authenticator|recovery.?code|backup.?code' \
--glob '*.php' \
.
```

Review:

```text
Enrollment
Verification
Recovery
Reset
Remember-device
Rate limiting
Bypass routes
```

Refer to:

```text
docs/web/mfa.md
```

---

# Password Hashing

PHP provides:

```text
password_hash()
password_verify()
password_needs_rehash()
```

Search:

```bash
rg -n \
'password_hash\(|password_verify\(|password_needs_rehash\(' \
--glob '*.php' \
.
```

---

# Weak Password Hashing

Search:

```bash
rg -n \
'md5\(|sha1\(|hash\(["'\''](?:md5|sha1)' \
--glob '*.php' \
.
```

Do not report these functions merely because they exist.

Determine whether they protect:

```text
Passwords
Tokens
Checksums
Cache keys
Protocol-specific values
```

---

# Cryptography

Search:

```bash
rg -n \
'openssl_encrypt\(|openssl_decrypt\(|openssl_sign\(|openssl_verify\(|sodium_|hash_hmac\(|random_bytes\(' \
--glob '*.php' \
.
```

Review:

```text
Algorithm
Mode
Key source
Nonce / IV
Authentication
Key reuse
Hard-coded keys
Error handling
```

---

# Randomness

Search:

```bash
rg -n \
'\brand\(|mt_rand\(|uniqid\(|random_bytes\(|random_int\(' \
--glob '*.php' \
.
```

Prioritise insecure randomness used for:

```text
Password reset
MFA
Session tokens
API keys
Invitation tokens
Verification tokens
```

---

# Secrets Exposure

Search:

```bash
rg -n -i \
'password|passwd|secret|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|token|database_url|dsn' \
.
```

High-value files:

```text
.env
.env.*
config.php
database.php
wp-config.php
composer.json
Dockerfile
docker-compose.yml
CI/CD configuration
Tests
Backups
```

---

# .env Files

Find:

```bash
find . -type f -name '.env*' -print
```

Inspect whether sensitive environment files were committed.

Do not assume:

```text
.env.example
```

contains real credentials.

Validate the values.

---

# Laravel Configuration

High-value files:

```text
.env
config/app.php
config/auth.php
config/database.php
config/filesystems.php
config/session.php
config/cors.php
config/services.php
```

---

# Laravel APP_DEBUG

Search:

```bash
rg -n \
'APP_DEBUG|APP_ENV|APP_KEY' \
.
```

Production debug exposure may reveal sensitive application details.

Verify deployed configuration before reporting a repository default.

---

# Symfony Configuration

Review:

```text
.env
.env.local
config/packages/
config/services.yaml
config/routes.yaml
config/packages/security.yaml
```

Search:

```bash
rg -n -i \
'app_secret|database_url|mailer_dsn|redis_url|messenger_transport_dsn' \
.
```

---

# WordPress Configuration

High-value file:

```text
wp-config.php
```

Review:

```text
Database credentials
Authentication keys
Salts
Debug configuration
Table prefix
Custom constants
Environment configuration
```

Search:

```bash
rg -n \
'DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|AUTH_KEY|SECURE_AUTH_KEY|LOGGED_IN_KEY|NONCE_KEY|WP_DEBUG' \
--glob 'wp-config.php' \
.
```

---

# Information Disclosure

Search:

```bash
rg -n \
'phpinfo\(|var_dump\(|print_r\(|dd\(|dump\(|display_errors|error_reporting\(' \
--glob '*.php' \
.
```

---

# phpinfo

Search:

```bash
rg -n \
'phpinfo\(' \
--glob '*.php' \
.
```

If reachable, `phpinfo()` can reveal extensive environment information.

Verify reachability before reporting it.

---

# var_dump / print_r

Search:

```bash
rg -n \
'var_dump\(|print_r\(' \
--glob '*.php' \
.
```

Determine whether output reaches the HTTP response or only development tooling/tests.

---

# Error Display

Search:

```bash
rg -n \
'display_errors|error_reporting\(' \
.
```

Review production configuration.

---

# Logging

Search:

```bash
rg -n \
'error_log\(|Log::|logger\(|->(debug|info|notice|warning|error|critical)\(' \
--glob '*.php' \
.
```

Review logging of:

```text
Passwords
JWTs
Session IDs
Authorization headers
API keys
Secrets
Personal information
Full request bodies
```

---

# Business Logic

Search security-sensitive business terms:

```bash
rg -n -i \
'price|amount|balance|quantity|discount|coupon|credit|refund|approved|verified|status|role|permission|tenant|owner' \
--glob '*.php' \
.
```

Review:

```text
Financial calculations
State transitions
Approval workflows
Role changes
Ownership transfers
Discounts
Refunds
Inventory
Account credits
```

Business logic vulnerabilities frequently do not contain a recognisable technical sink.

---

# Price Manipulation

Trace:

```text
Client Price
    |
    v
Request
    |
    v
Server
    |
    v
Used directly?
```

Prefer:

```text
Product ID
    |
    v
Server-side price lookup
```

rather than trusting a client-supplied price.

---

# State Transitions

Search:

```bash
rg -n -i \
'status|state|approved|pending|completed|cancelled|refunded|verified' \
--glob '*.php' \
.
```

Map transitions:

```text
PENDING
   |
   v
APPROVED
   |
   v
COMPLETED
```

Determine whether users can skip required states.

Refer to:

```text
docs/web/business-logic.md
```

---

# Race Conditions

Look for operations following:

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

Examples:

```text
Coupon redemption
Balance withdrawal
Stock decrement
Password reset
Invitation acceptance
One-time token use
```

---

# Database Transactions

Search:

```bash
rg -n \
'beginTransaction\(|commit\(|rollBack\(|DB::transaction|DB::beginTransaction|transactional\(' \
--glob '*.php' \
.
```

---

# Laravel Locks

Search:

```bash
rg -n \
'lockForUpdate\(|sharedLock\(' \
--glob '*.php' \
.
```

Their absence does not prove a race condition.

Trace the entire state transition.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Rate Limiting

Search:

```bash
rg -n -i \
'ratelimit|rate.?limit|throttle|throttling|limiter' \
--glob '*.php' \
.
```

---

# Laravel Rate Limiting

Search:

```bash
rg -n \
'RateLimiter|throttle:' \
--glob '*.php' \
.
```

Review protection around:

```text
Login
Password reset
MFA
OTP
Registration
Email verification
Expensive APIs
Exports
Search
```

---

# Client IP

Search:

```bash
rg -n \
'REMOTE_ADDR|X_FORWARDED_FOR|->ip\(|getClientIp\(' \
--glob '*.php' \
.
```

If rate limiting or authorisation depends on client IP, review trusted-proxy configuration.

Refer to:

```text
docs/web/rate-limiting.md
```

---

# GraphQL

PHP GraphQL implementations may use libraries such as:

```text
webonyx/graphql-php
Lighthouse
API Platform
OverblogGraphQLBundle
```

Search:

```bash
rg -n -i \
'graphql|lighthouse|webonyx|GraphQL\\\\|Mutation|Resolver' \
composer.json composer.lock --glob '*.php' 2>/dev/null
```

Review:

```text
Resolvers
Mutations
Object-level authorisation
Input validation
Query depth
Complexity
Introspection
Batching
```

Refer to:

```text
docs/web/graphql.md
```

---

# WebSockets

PHP applications may use:

```text
Ratchet
Swoole
OpenSwoole
Laravel Reverb
Workerman
```

Search:

```bash
rg -n -i \
'ratchet|swoole|openswoole|reverb|workerman|websocket' \
composer.json composer.lock --glob '*.php' 2>/dev/null
```

Review:

```text
Connection authentication
Message authorisation
Channel authorisation
Object access
State-changing messages
```

Refer to:

```text
docs/web/websockets.md
```

---

# API Security

Search API routes:

```bash
rg -n \
'Route::.*api|/api/|apiResource|JsonResponse|->json\(' \
--glob '*.php' \
.
```

Map:

```text
Endpoint
   |
   v
Authentication
   |
   v
Authorisation
   |
   v
Input Validation
   |
   v
Business Logic
   |
   v
Data Access
```

Refer to:

```text
docs/web/api-security.md
```

---

# HTTP Method Testing

Compare security controls across:

```text
GET
POST
PUT
PATCH
DELETE
```

For example:

```text
GET /users/{id}
    -> authorisation

DELETE /users/{id}
    -> no equivalent authorisation
```

Search Laravel routes:

```bash
rg -n \
'Route::(get|post|put|patch|delete|any|match)' \
--glob '*.php' \
.
```

---

# Administrative Functionality

Search:

```bash
rg -n -i \
'admin|administrator|superuser|management|manage|privileged' \
--glob '*.php' \
.
```

Map:

```text
Route
  |
  v
Authentication
  |
  v
Role Check
  |
  v
Sensitive Operation
```

---

# Role Management

Search:

```bash
rg -n -i \
'role|permission|is_admin|isadmin|admin|assignrole|syncroles|giverole|revoke' \
--glob '*.php' \
.
```

Review who can:

```text
Assign roles
Remove roles
Modify permissions
Create administrators
Change tenant membership
```

---

# Registration

Search:

```bash
rg -n -i \
'register|registration|signup|sign.?up|create.?user' \
--glob '*.php' \
.
```

Review:

```text
Role assignment
Mass assignment
Email verification
Tenant assignment
Default privileges
Invitation handling
Duplicate accounts
```

---

# Webhooks

Search:

```bash
rg -n -i \
'webhook|callback|signature|hmac' \
--glob '*.php' \
.
```

Review:

```text
Signature verification
Secret management
Timestamp verification
Replay protection
Payload validation
State changes
```

---

# hash_hmac

Search:

```bash
rg -n \
'hash_hmac\(|hash_equals\(' \
--glob '*.php' \
.
```

For signature verification, also review constant-time comparison where applicable.

---

# Background Jobs

Frameworks may process untrusted data asynchronously.

Laravel:

```text
Jobs
Queues
Listeners
Commands
Scheduled tasks
```

Search:

```bash
rg -n \
'ShouldQueue|dispatch\(|Queue::|Artisan::|Schedule::' \
--glob '*.php' \
.
```

Stored input may reach dangerous sinks later.

---

# Second-Order Vulnerabilities

Example:

```text
POST /profile
      |
      v
Store biography
      |
      v
Database
      |
      v
Admin Report
      |
      v
Blade {!! ... !!}
      |
      v
Stored XSS
```

Do not stop tracing merely because input is stored in a database.

---

# PHP Dynamic Code Execution

PHP contains several highly sensitive dynamic execution mechanisms.

---

# eval

Search:

```bash
rg -n \
'\beval\s*\(' \
--glob '*.php' \
.
```

Candidate:

```php
eval(
    $_POST['expression']
);
```

Attacker-controlled input reaching `eval()` is a high-value review target.

---

# assert

Search:

```bash
rg -n \
'\bassert\s*\(' \
--glob '*.php' \
.
```

Be careful with historical PHP behaviour.

Do not automatically apply exploitation assumptions from old PHP versions to modern PHP.

Determine:

```text
PHP version
Input
Expression type
Runtime configuration
```

---

# preg_replace Legacy /e Modifier

Old PHP applications may contain historical code such as:

```text
preg_replace('/.../e', ...)
```

Search:

```bash
rg -n \
'preg_replace\s*\(' \
--glob '*.php' \
.
```

The `/e` modifier is historical and removed from modern PHP.

If found, establish the actual runtime version rather than assuming the code is executable as-is.

---

# create_function

Search:

```bash
rg -n \
'create_function\(' \
--glob '*.php' \
.
```

This is another legacy pattern removed from modern PHP.

Its presence can indicate old application code or an outdated runtime assumption.

---

# Reflection

Search:

```bash
rg -n \
'ReflectionClass|ReflectionMethod|ReflectionFunction|call_user_func|call_user_func_array|is_callable' \
--glob '*.php' \
.
```

Reflection and dynamic callbacks are not vulnerabilities by themselves.

Review attacker influence over:

```text
Class names
Method names
Function names
Arguments
```

---

# Dynamic Function Calls

PHP supports:

```php
$function();
```

and:

```php
$object->$method();
```

Search for these patterns manually or with static-analysis tools.

High-value flow:

```text
Request Parameter
      |
      v
Function / Method Name
      |
      v
Dynamic Invocation
```

---

# call_user_func

Search:

```bash
rg -n \
'call_user_func\(|call_user_func_array\(' \
--glob '*.php' \
.
```

Trace the callback value.

---

# Dynamic Object Construction

Search:

```bash
rg -n \
'new \$[A-Za-z_]' \
--glob '*.php' \
.
```

Review attacker control over class names.

---

# Variable Variables

PHP supports:

```php
$$name
```

Search:

```bash
rg -n \
'\$\$[A-Za-z_]' \
--glob '*.php' \
.
```

Variable variables can complicate data-flow analysis and deserve manual inspection when influenced by request data.

---

# extract()

Search:

```bash
rg -n \
'\bextract\s*\(' \
--glob '*.php' \
.
```

Example:

```php
extract($_POST);
```

This can make attacker-controlled values difficult to trace and may overwrite existing variables depending on flags.

Review carefully.

---

# parse_str()

Search:

```bash
rg -n \
'parse_str\(' \
--glob '*.php' \
.
```

Determine where parsed variables are stored and whether they influence security-sensitive operations.

---

# Dynamic Properties / Array Assignment

Look for patterns such as:

```php
foreach ($request->all() as $key => $value) {
    $user->$key = $value;
}
```

This may create mass-assignment-style behaviour even without framework ORM features.

---

# Autoloading

Composer typically manages autoloading.

Inspect:

```json
"autoload": {
    "psr-4": {
        "App\\": "src/"
    }
}
```

Search:

```bash
rg -n \
'spl_autoload_register|__autoload|autoload' \
--glob '*.php' \
composer.json
```

Review custom autoloaders if class names can be influenced by attacker-controlled input.

---

# Dangerous File Writes

Search:

```bash
rg -n \
'file_put_contents\(|fwrite\(|fputs\(|copy\(|rename\(|move_uploaded_file\(' \
--glob '*.php' \
.
```

Trace:

```text
Path
Content
Extension
Destination
Permissions
Web accessibility
```

---

# File Delete Operations

Search:

```bash
rg -n \
'unlink\(|rmdir\(' \
--glob '*.php' \
.
```

Review object-level authorisation and path traversal.

---

# File Download

Search:

```bash
rg -n \
'readfile\(|file_get_contents\(|BinaryFileResponse|download\(' \
--glob '*.php' \
.
```

Review:

```text
Path traversal
Object authorisation
Tenant isolation
Content-Disposition
Content type
```

---

# Email

Search:

```bash
rg -n \
'\bmail\s*\(|Mailer|PHPMailer|SwiftMailer|MailerInterface|Mail::' \
--glob '*.php' \
.
```

Review attacker-controlled values used in:

```text
Recipients
Reply-To
Subject
Headers
Template content
Password reset URLs
```

---

# Header Trust

Search:

```bash
rg -n \
'HTTP_X_FORWARDED_FOR|HTTP_X_FORWARDED_HOST|HTTP_X_FORWARDED_PROTO|HTTP_FORWARDED' \
--glob '*.php' \
.
```

Review whether proxy headers are accepted from arbitrary clients.

---

# Client IP Security Decisions

Candidate:

```php
$ip =
    $_SERVER['HTTP_X_FORWARDED_FOR'];

if ($ip === '10.0.0.5') {
    ...
}
```

This is unsafe if the header can be supplied directly by untrusted clients and no trusted proxy normalises it.

---

# Cache Security

Search:

```bash
rg -n -i \
'cache|redis|memcached|remember\(|Cache::' \
--glob '*.php' \
.
```

Review cache keys for:

```text
User
Tenant
Object ID
Role
Authentication state
Language
Request headers
```

Incorrect cache isolation can disclose data across users or tenants.

---

# Dependency Security

Inspect:

```text
composer.json
composer.lock
```

Composer provides:

```bash
composer audit
```

for checking installed packages against known security advisories.

Run from the project directory where appropriate.

---

# Composer Lock

Do not review only:

```text
composer.json
```

because:

```text
composer.lock
```

usually identifies the resolved package versions actually selected for the project.

---

# Dependency Search

```bash
rg -n \
'"name"|"version"' \
composer.lock
```

For large files, use Composer tooling instead of manually reviewing every dependency.

---

# Composer Scripts

Inspect:

```bash
rg -n \
'"scripts"|"scripts-descriptions"|"scripts-aliases"' \
composer.json
```

Composer scripts can execute commands during package lifecycle operations.

---

# Composer Repositories

Search:

```bash
rg -n \
'"repositories"|"type".*"vcs"|"type".*"composer"|"url"' \
composer.json
```

Review unexpected package repositories.

Refer to:

```text
docs/web/dependency-security.md
```

---

# Third-Party JavaScript

PHP applications frequently contain frontend dependencies.

Find:

```bash
find . -type f \( \
-name 'package.json' \
-o -name 'package-lock.json' \
-o -name 'yarn.lock' \
-o -name 'pnpm-lock.yaml' \
\) -print
```

Refer to:

```text
docs/web/third-party-javascript.md
docs/source-code-review/javascript.md
```

---

# Git History

Sensitive data may have been removed from current source but remain in history.

Useful authorised review commands:

```bash
git log --oneline --all
```

Search history:

```bash
git log -S 'password' --all
```

```bash
git log -S 'secret' --all
```

Inspect a commit:

```bash
git show <commit>
```

Use dedicated secret-scanning tools for larger repositories.

---

# Backup Files

Find:

```bash
find . -type f \( \
-name '*.bak' \
-o -name '*.old' \
-o -name '*.backup' \
-o -name '*.orig' \
-o -name '*~' \
-o -name '*.swp' \
\) -print
```

These may expose:

```text
Old credentials
Source code
Configuration
Deprecated endpoints
Historical security controls
```

---

# Static Analysis

Static analysis should complement manual review rather than replace it.

Useful tools include:

```text
Semgrep
CodeQL
Psalm
PHPStan
Composer Audit
TruffleHog
Gitleaks
```

---

# Semgrep

Semgrep can identify PHP security patterns and assist with source-to-sink analysis.

Conceptually:

```text
PHP Repository
      |
      v
Semgrep
      |
      v
Candidate Findings
      |
      v
Manual Validation
```

Official documentation:

```text
https://semgrep.dev/docs/
```

---

# CodeQL

CodeQL supports analysis of PHP source code.

Use it to assist with:

```text
Data flow
Taint tracking
Call graphs
Security queries
Variant analysis
```

Official documentation:

```text
https://codeql.github.com/docs/codeql-language-guides/codeql-for-php/
```

---

# Psalm

Psalm is a PHP static-analysis tool.

```text
https://psalm.dev/
```

It is useful primarily for type and code analysis, with additional security-analysis capabilities depending on configuration and plugins.

---

# PHPStan

PHPStan:

```text
https://phpstan.org/
```

Useful for identifying:

```text
Type issues
Invalid assumptions
Dead code
Potential implementation mistakes
```

It is not a replacement for security-specific manual analysis.

---

# Reverse Sink Analysis

For large PHP applications, starting from dangerous sinks can be efficient.

Example:

```text
system()
   ^
   |
ConversionService
   ^
   |
UploadController
   ^
   |
POST /convert
```

High-value starting sinks:

```text
system
exec
shell_exec
passthru
proc_open

PDO::query
PDO::exec
mysqli_query
DB::raw

file_get_contents
file_put_contents
fopen
readfile
include
require

curl_exec
file_get_contents(URL)

unserialize

eval

header(Location)

move_uploaded_file
ZipArchive::extractTo
```

---

# Forward Source Analysis

Start with:

```text
$_GET
$_POST
$_REQUEST
$_COOKIE
$_FILES
$_SERVER

$request->input()
$request->query()
$request->all()

$request->query->get()
$request->request->get()
```

Then trace each value forward.

This is particularly useful around:

```text
Uploads
Downloads
Imports
Exports
Admin functions
Search
Password reset
Account management
Payments
Webhooks
Reports
```

---

# Source-to-Sink Example - SQL Injection

```text
GET /search?name=test
       |
       v
$_GET['name']
       |
       v
$name
       |
       v
SQL concatenation
       |
       v
PDO::query()
```

Questions:

```text
Is name attacker-controlled?

Is it transformed?

Is it bound as a parameter?

Can it alter SQL syntax?

Is the route reachable?

What authentication is required?
```

---

# Source-to-Sink Example - Command Injection

```text
POST /diagnostic
       |
       v
$_POST['host']
       |
       v
$host
       |
       v
'ping ' . $host
       |
       v
system()
```

---

# Source-to-Sink Example - SSRF

```text
POST /import
       |
       v
$_POST['url']
       |
       v
$url
       |
       v
curl_setopt(CURLOPT_URL)
       |
       v
curl_exec()
```

---

# Source-to-Sink Example - File Inclusion

```text
GET /page?page=help
       |
       v
$_GET['page']
       |
       v
$page
       |
       v
'pages/' . $page . '.php'
       |
       v
include()
```

---

# Source-to-Sink Example - Path Traversal

```text
GET /download?file=report.pdf
       |
       v
$_GET['file']
       |
       v
'/uploads/' . $file
       |
       v
readfile()
```

---

# Source-to-Sink Example - IDOR

```text
GET /invoice?id=100
       |
       v
$_GET['id']
       |
       v
Invoice::find($id)
       |
       v
Invoice returned
```

Critical question:

```text
Where is object-level authorisation?
```

---

# Source-to-Sink Example - Stored XSS

```text
POST /profile
       |
       v
$_POST['bio']
       |
       v
Database
       |
       v
Profile page
       |
       v
echo $bio
```

---

# Source-to-Sink Example - Deserialization

```text
Cookie
  |
  v
$_COOKIE['settings']
  |
  v
unserialize()
  |
  v
Object Graph
  |
  v
Magic Methods
```

---

# Source-to-Sink Example - Mass Assignment

```text
POST /profile
       |
       v
$request->all()
       |
       v
User::update()
       |
       v
Security-sensitive model fields
```

Determine whether the model and framework configuration restrict assignable attributes.

---

# Broad PHP Search

A useful first-pass search:

```bash
rg -n \
'\$_GET|\$_POST|\$_REQUEST|\$_COOKIE|\$_FILES|\$_SERVER|php://input|PDO|mysqli_|->query\(|->exec\(|DB::raw|whereRaw|\bsystem\s*\(|\bexec\s*\(|shell_exec\s*\(|passthru\s*\(|proc_open\s*\(|file_get_contents\(|file_put_contents\(|fopen\(|readfile\(|\binclude\b|\brequire\b|curl_exec\(|CURLOPT_URL|unserialize\(|eval\(|move_uploaded_file\(|ZipArchive|DOMDocument|simplexml_load|header\s*\(' \
--glob '*.php' \
.
```

This generates candidates.

It does not generate confirmed vulnerabilities.

---

# Input Search

```bash
rg -n \
'\$_GET|\$_POST|\$_REQUEST|\$_COOKIE|\$_FILES|\$_SERVER|php://input' \
--glob '*.php' \
.
```

---

# Laravel Input Search

```bash
rg -n \
'\$request->(input|query|post|header|cookie|file|all|only|except)\(' \
--glob '*.php' \
.
```

---

# SQL Search

```bash
rg -n \
'PDO|mysqli_|->query\(|->exec\(|->prepare\(|DB::raw|whereRaw|orWhereRaw|havingRaw|orderByRaw|selectRaw|unprepared\(' \
--glob '*.php' \
.
```

---

# Command Search

```bash
rg -n \
'\bsystem\s*\(|\bexec\s*\(|shell_exec\s*\(|passthru\s*\(|popen\s*\(|proc_open\s*\(|escapeshellarg\(|escapeshellcmd\(' \
--glob '*.php' \
.
```

---

# File Search

```bash
rg -n \
'file_get_contents\(|file_put_contents\(|fopen\(|fwrite\(|readfile\(|unlink\(|copy\(|rename\(|move_uploaded_file\(|ZipArchive' \
--glob '*.php' \
.
```

---

# Include Search

```bash
rg -n \
'\binclude\b|\binclude_once\b|\brequire\b|\brequire_once\b' \
--glob '*.php' \
.
```

---

# SSRF Search

```bash
rg -n \
'curl_init\(|curl_setopt\(|CURLOPT_URL|curl_exec\(|file_get_contents\(|fopen\(|fsockopen\(|stream_socket_client\(' \
--glob '*.php' \
.
```

---

# Deserialization Search

```bash
rg -n \
'unserialize\(|__wakeup|__unserialize|__destruct|__toString|phar://' \
--glob '*.php' \
.
```

---

# XML Search

```bash
rg -n \
'DOMDocument|simplexml_load_string|simplexml_load_file|XMLReader|LIBXML_|libxml_' \
--glob '*.php' \
.
```

---

# Template Search

```bash
rg -n -i \
'twig|blade|smarty|latte|mustache|createTemplate|render\(' \
--glob '*.php' \
.
```

---

# Redirect Search

```bash
rg -n -i \
'header\s*\(\s*["'\'']Location:|redirect\(|->away\(' \
--glob '*.php' \
.
```

---

# Authentication / Authorisation Search

```bash
rg -n -i \
'auth::|auth\(\)|authenticate|middleware.*auth|authorize\(|Gate::|Policy|isGranted\(|denyAccessUnlessGranted|Voter|role|permission' \
--glob '*.php' \
.
```

---

# Secret Search

```bash
rg -n -i \
'password|passwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|database_url|dsn' \
.
```

---

# Exclude Dependencies

For most manual searches, exclude third-party code initially:

```bash
rg \
-g '!vendor/**' \
-g '!node_modules/**' \
-g '!storage/**' \
-g '!cache/**' \
'pattern' \
.
```

Later review dependencies separately.

---

# Variant Analysis

After confirming one vulnerability:

```text
Finding
   |
   v
Determine Root Cause
   |
   v
Extract Pattern
   |
   v
Search Repository
   |
   v
Review Similar Paths
```

Example:

```text
Invoice::find($id)
without ownership check
```

Search:

```bash
rg -n \
'::find\(|::findOrFail\(' \
--glob '*.php' \
.
```

Review similar object lookups.

---

# Compare Controllers

Example:

```text
InvoiceController
      |
      +-- ownership check

OrderController
      |
      +-- ownership check

DocumentController
      |
      +-- no ownership check
```

Inconsistency often identifies security defects.

---

# Compare CRUD Operations

For the same object:

```text
GET    /documents/{id}
POST   /documents
PUT    /documents/{id}
DELETE /documents/{id}
```

Compare:

```text
Authentication
Authorisation
Tenant checks
Validation
```

across every operation.

---

# Compare API Versions

Search:

```bash
rg -n \
'/v1/|/v2/|api/v1|api/v2' \
--glob '*.php' \
.
```

Older endpoints may contain weaker security controls.

---

# Security Review Matrix

| Vulnerability | High-Value PHP Review Targets |
|---|---|
| SQL Injection | PDO, MySQLi, raw ORM/query-builder SQL |
| NoSQL Injection | MongoDB filters, dynamic arrays/JSON |
| LDAP Injection | `ldap_search()`, dynamic filters |
| Command Injection | `system`, `exec`, `shell_exec`, `passthru`, `proc_open` |
| SSTI | Twig, Blade, Smarty, dynamic templates |
| XSS | `echo`, `print`, raw template output |
| SSRF | cURL, URL-aware streams, sockets |
| Path Traversal | `file_get_contents`, `readfile`, `fopen`, writes |
| File Inclusion | `include`, `require` |
| File Upload | `$_FILES`, `move_uploaded_file`, archive extraction |
| XXE | DOMDocument, SimpleXML, XMLReader |
| Deserialization | `unserialize`, magic methods, legacy PHAR paths |
| IDOR/BOLA | Model/object lookup using request IDs |
| Mass Assignment | `$request->all()`, model `create/update/fill` |
| Open Redirect | `header('Location:')`, framework redirects |
| CSRF | Framework middleware, custom tokens |
| CORS | CORS response-header construction |
| Host Header | `HTTP_HOST`, forwarded host handling |
| Session | `session_start`, `$_SESSION`, cookie settings |
| JWT | JWT libraries and claims validation |
| OAuth/OIDC | Callback and token-validation logic |
| SAML | SAML libraries and assertion validation |
| Race Conditions | State transitions and transactions |
| Rate Limiting | Framework middleware and custom throttling |
| Secrets | `.env`, configuration, source, Git history |
| Dependency Security | Composer |
| Information Disclosure | `phpinfo`, debug output, error display |
| Business Logic | Services/controllers/domain workflows |

---

# Source Code Review Checklist

## Application

```text
[ ] PHP version identified
[ ] Framework identified
[ ] Composer configuration reviewed
[ ] Application entry points identified
[ ] Routes mapped
[ ] Controllers identified
[ ] Models identified
[ ] Services identified
[ ] Templates identified
[ ] Configuration identified
```

## Sources

```text
[ ] $_GET reviewed
[ ] $_POST reviewed
[ ] $_REQUEST reviewed
[ ] $_COOKIE reviewed
[ ] $_FILES reviewed
[ ] $_SERVER reviewed
[ ] php://input reviewed
[ ] Framework request APIs reviewed
[ ] Stored user input considered
```

## Authentication

```text
[ ] Login flow reviewed
[ ] Password hashing reviewed
[ ] Session creation reviewed
[ ] Session rotation reviewed
[ ] JWT reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
```

## Authorisation

```text
[ ] Route middleware reviewed
[ ] Roles reviewed
[ ] Permissions reviewed
[ ] Policies reviewed
[ ] Gates/Voters reviewed
[ ] Object-level authorisation reviewed
[ ] Tenant isolation reviewed
[ ] Administrative functions reviewed
```

## Input Validation

```text
[ ] Native PHP validation reviewed
[ ] Framework validation reviewed
[ ] Type validation reviewed
[ ] Length validation reviewed
[ ] Allowlisting reviewed
[ ] Business-rule validation reviewed
```

## Injection

```text
[ ] PDO reviewed
[ ] MySQLi reviewed
[ ] Raw SQL reviewed
[ ] NoSQL reviewed
[ ] LDAP reviewed
[ ] system() reviewed
[ ] exec() reviewed
[ ] shell_exec() reviewed
[ ] proc_open() reviewed
[ ] Template evaluation reviewed
[ ] eval() reviewed
```

## Server-Side

```text
[ ] cURL reviewed
[ ] URL stream operations reviewed
[ ] File reads reviewed
[ ] File writes reviewed
[ ] Includes reviewed
[ ] Uploads reviewed
[ ] Archive extraction reviewed
[ ] XML parsers reviewed
[ ] unserialize() reviewed
```

## Client-Side / HTTP

```text
[ ] echo/print output reviewed
[ ] Templates reviewed
[ ] Unescaped output reviewed
[ ] Redirects reviewed
[ ] Header construction reviewed
[ ] Host handling reviewed
[ ] CSRF reviewed
[ ] CORS reviewed
[ ] Session cookies reviewed
```

## Business Logic

```text
[ ] Prices reviewed
[ ] Balances reviewed
[ ] Discounts reviewed
[ ] Refunds reviewed
[ ] State transitions reviewed
[ ] Approval workflows reviewed
[ ] Role changes reviewed
[ ] Tenant changes reviewed
[ ] Race conditions considered
[ ] Rate limiting reviewed
```

## Configuration

```text
[ ] .env reviewed
[ ] Framework config reviewed
[ ] Database config reviewed
[ ] Debug configuration reviewed
[ ] Error display reviewed
[ ] Logging reviewed
[ ] Secrets searched
[ ] Production differences considered
```

## Dependencies

```text
[ ] composer.json reviewed
[ ] composer.lock reviewed
[ ] composer audit considered
[ ] Unsupported packages considered
[ ] Package repositories reviewed
[ ] Composer scripts reviewed
[ ] Frontend dependencies reviewed
```

## Analysis

```text
[ ] ripgrep searches performed
[ ] Semgrep considered
[ ] CodeQL considered
[ ] Git history reviewed
[ ] Variant analysis performed
[ ] Candidate findings manually validated
[ ] Dynamic verification performed where authorised
```

---

# Recommended Manual Review Order

For an unfamiliar PHP application:

```text
composer.json
      |
      v
composer.lock
      |
      v
Entry Point
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
Controllers
      |
      v
Input Validation
      |
      v
Models / Services
      |
      v
Database Queries
      |
      v
Dangerous Sinks
      |
      v
Templates
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
Git History
```

---

# High-Value Files

Prioritise:

```text
composer.json
composer.lock

.env
.env.*

index.php

routes/
routes/web.php
routes/api.php

app/Http/Controllers/
app/Http/Middleware/
app/Models/
app/Policies/
app/Providers/

src/Controller/
src/Security/

config/
config/packages/security.yaml

resources/views/
templates/

wp-config.php

Dockerfile
docker-compose.yml

CI/CD configuration
```

---

# High-Value Search Terms

```text
$_GET
$_POST
$_REQUEST
$_COOKIE
$_FILES
$_SERVER

request->input
request->all

Auth
authorize
Gate
Policy
Voter
role
permission
tenant

PDO
mysqli
query
DB::raw
whereRaw

system
exec
shell_exec
passthru
proc_open

curl
file_get_contents

include
require

fopen
readfile
file_put_contents

move_uploaded_file
ZipArchive

unserialize
__wakeup
__destruct

DOMDocument
SimpleXML

Twig
Blade
Smarty

echo
print

header
Location

session
JWT
OAuth
SAML

password
secret
token
api_key
```

---

# Finding Validation

Use the following model before classifying a PHP source-code match as a vulnerability:

```text
CODE MATCH
    |
    v
REACHABLE?
    |
    +-- No --> Usually discard / contextual note
    |
    v
ATTACKER CONTROLLED?
    |
    +-- No --> Continue contextual review
    |
    v
SOURCE-TO-SINK FLOW?
    |
    +-- No --> Not this vulnerability
    |
    v
SECURITY CONTROL?
    |
    +-- Effective --> Protected
    |
    v
EXPLOITABLE?
    |
    +-- No --> Defence-in-depth / contextual
    |
    v
MEANINGFUL IMPACT?
    |
    +-- No --> Low significance
    |
    v
CONFIRMED FINDING
```

---

# Evidence Template

For every finding record:

```text
Route:

HTTP Method:

Controller / File:

Source File:

Source Line:

Source:

Data Flow:

Validation:

Authentication:

Authorisation:

Sink:

Reachability:

Dynamic Validation:

Impact:

Recommendation:
```

---

# Example Finding - SQL Injection

```text
Title:
SQL Injection in Product Search

Route:
GET /products/search

Source:
$_GET['name']

Data Flow:

$_GET['name']
      |
      v
$name
      |
      v
SQL concatenation
      |
      v
PDO::query()

Security Control:
No parameter binding was identified for the attacker-controlled value.

Impact:
An attacker able to access the endpoint may be able to alter the structure of the database query.

Recommendation:
Use a parameterised query and bind the search value as data rather than concatenating it into SQL syntax.
```

---

# Example Finding - IDOR / BOLA

```text
Title:
Missing Object-Level Authorisation on Invoice Endpoint

Route:
GET /api/invoices/{id}

Source:
Route parameter id

Data Flow:

{id}
 |
 v
InvoiceController
 |
 v
Invoice::findOrFail($id)
 |
 v
Invoice returned

Authentication:
Required.

Authorisation:
No ownership, tenant or equivalent permission check was identified before returning the invoice.

Impact:
An authenticated user may be able to access invoices belonging to another user by modifying the object identifier.

Recommendation:
Scope invoice access to objects the authenticated principal is authorised to access or perform an equivalent object-level permission check.
```

---

# Example Finding - File Inclusion

```text
Title:
User-Controlled File Included by Page Handler

Route:
GET /page?page=<value>

Source:
$_GET['page']

Data Flow:

$_GET['page']
      |
      v
$page
      |
      v
Dynamic file path
      |
      v
include()

Impact:
Depending on the path restrictions, PHP configuration and available files, an attacker may be able to cause the application to include unintended local resources.

Recommendation:
Do not construct include paths from arbitrary request values. Map permitted page identifiers to server-controlled template or file paths.
```

---

# Example Finding - SSRF

```text
Title:
Server-Side Request Forgery Through URL Import

Route:
POST /api/import

Source:
Request parameter url

Data Flow:

url
 |
 v
ImportController
 |
 v
CURLOPT_URL
 |
 v
curl_exec()

Security Control:
No destination allowlist or equivalent outbound-request policy was identified.

Impact:
A user able to access the endpoint may be able to cause the application to make server-side requests to unintended destinations.

Recommendation:
Prefer server-controlled destinations. Where user-supplied URLs are required, enforce a strict destination policy and combine application validation with network-level egress restrictions.
```

---

# Example Finding - Unsafe Deserialization

```text
Title:
Untrusted Cookie Data Passed to unserialize()

Source:
$_COOKIE['preferences']

Data Flow:

Cookie
 |
 v
$_COOKIE['preferences']
 |
 v
unserialize()
 |
 v
PHP object graph

Impact:
Processing attacker-controlled serialized PHP objects may allow unintended object instantiation and trigger application or dependency behaviours through available classes and magic methods.

Recommendation:
Do not use PHP serialization across untrusted boundaries. Use a data-only format such as JSON and explicitly validate the resulting structure.
```

---

# Common Review Mistakes

## Every echo Is XSS

Incorrect:

```text
echo
 =
XSS
```

Correct:

```text
Attacker Input
     |
     v
Output
     |
     v
Context?
     |
     v
Encoding?
     |
     v
Browser Interpretation
```

---

# Every PDO Query Is SQL Injection

Incorrect:

```text
PDO
 =
SQL Injection
```

Determine:

```text
Query construction
Parameter binding
Attacker control
SQL context
```

---

# Every prepare() Is Safe

Incorrect:

```text
prepare()
 =
Safe
```

Example:

```php
$sql =
    'SELECT * FROM users ORDER BY ' .
    $_GET['sort'];

$stmt = $pdo->prepare($sql);
```

The dangerous SQL structure was constructed before preparation.

---

# Every include Is LFI

Incorrect:

```text
include()
 =
LFI
```

Determine:

```text
Is the path attacker-controlled?

Can traversal occur?

Is an allowlist used?

Which files are reachable?

What does PHP execute?
```

---

# Every file_get_contents Is SSRF

It may read:

```text
Local files
Trusted internal resources
Static application resources
Remote URLs
```

Trace the input and runtime configuration.

---

# Every unserialize Is Exploitable

The function is security-sensitive, but determine:

```text
Input trust boundary
Integrity protection
Reachability
Available classes
Application behaviour
```

For untrusted input, however, redesigning away from native PHP serialization is strongly preferred.

---

# Every md5 Is a Password Vulnerability

Determine what is being hashed.

```text
Password
    -> security concern

Cache key
    -> different context

Legacy protocol requirement
    -> different context
```

---

# Every Raw SQL Call Is SQL Injection

Raw SQL can be safely constructed.

The question is:

```text
Can untrusted input modify the SQL structure?
```

---

# Every Missing Validation Is a Vulnerability

Input validation is only one security layer.

The correct question is:

```text
What security property does this input require?
```

Examples:

```text
SQL value
    -> parameterisation

HTML output
    -> context-specific encoding

Object ID
    -> authorisation

URL
    -> destination policy

File path
    -> containment

Command argument
    -> avoid shell + strict argument handling
```

---

# Final PHP Source Review Model

```text
                    PHP APPLICATION
                          |
                          v
                    ROUTE / FILE
                          |
                          v
                  USER INPUT SOURCE
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       $_GET           $_POST          $_FILES
          |               |               |
          +---------------+---------------+
                          |
                          v
                    DATA FLOW
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
      Validation     Authorisation    Business Logic
          |               |               |
          +---------------+---------------+
                          |
                          v
                SECURITY-SENSITIVE SINK
                          |
       +------------------+------------------+
       |                  |                  |
       v                  v                  v
      PDO               system            cURL
       |                  |                  |
       v                  v                  v
     SQLi         Command Injection         SSRF

    include             File             Template
       |                  |                  |
       v                  v                  v
 File Inclusion      Traversal/Upload     XSS/SSTI

                      unserialize
                          |
                          v
                Unsafe Deserialization
```

The fundamental PHP source-review question is:

```text
Can attacker-controlled data reach a security-sensitive PHP operation
without an effective security boundary?
```

Determine:

```text
Source
+
Data Flow
+
Reachability
+
Validation
+
Authentication
+
Authorisation
+
Sink
+
Exploitability
+
Impact
```

Only then should a source-code pattern be classified as a confirmed vulnerability.

---

# References

## PHP Manual

[PHP Manual](https://www.php.net/manual/en/)

## PHP Security

[PHP Security](https://www.php.net/manual/en/security.php)

## PHP Database Security

[PHP Database Security](https://www.php.net/manual/en/security.database.php)

## PHP SQL Injection

[PHP SQL Injection](https://www.php.net/manual/en/security.database.sql-injection.php)

## PHP PDO

[PHP PDO](https://www.php.net/manual/en/book.pdo.php)

## PDO Prepared Statements

[PDO Prepared Statements](https://www.php.net/manual/en/pdo.prepared-statements.php)

## PDO::prepare

[PDO::prepare](https://www.php.net/manual/en/pdo.prepare.php)

## MySQLi Prepared Statements

[MySQLi Prepared Statements](https://www.php.net/manual/en/mysqli.quickstart.prepared-statements.php)

## PHP unserialize

[PHP unserialize](https://www.php.net/manual/en/function.unserialize.php)

## PHP File Uploads

[PHP File Uploads](https://www.php.net/manual/en/features.file-upload.php)

## PHP Sessions

[PHP Sessions](https://www.php.net/manual/en/book.session.php)

## PHP Password Hashing

[PHP Password Hashing](https://www.php.net/manual/en/book.password.php)

## Laravel Documentation

[docs](https://laravel.com/docs/)

## Laravel Authentication

[Laravel Authentication](https://laravel.com/docs/authentication)

## Laravel Authorisation

[Laravel Authorisation](https://laravel.com/docs/authorization)

## Laravel Validation

[Laravel Validation](https://laravel.com/docs/validation)

## Symfony Documentation

[index](https://symfony.com/doc/current/index.html)

## Symfony Security

[Symfony Security](https://symfony.com/doc/current/security.html)

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## OWASP ASVS

[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)

## CWE

[CWE](https://cwe.mitre.org/)

## Semgrep

[Semgrep](https://semgrep.dev/docs/)

## CodeQL for PHP

[CodeQL for PHP](https://codeql.github.com/docs/codeql-language-guides/codeql-for-php/)

## Psalm

[Psalm](https://psalm.dev/)

## PHPStan

[PHPStan](https://phpstan.org/)

## Composer

[Composer](https://getcomposer.org/)

## Composer Audit

[Composer Audit](https://getcomposer.org/doc/03-cli.md#audit)

## ripgrep

[ripgrep](https://github.com/BurntSushi/ripgrep)

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/dotnet.md
docs/source-code-review/java.md
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

docs/web/host-header-attacks.md
docs/web/http-security-headers.md
docs/web/http-request-smuggling.md
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
docs/web/information-disclosure.md

docs/web/business-logic.md
docs/web/race-conditions.md
docs/web/rate-limiting.md

docs/web/jwt.md
docs/web/oauth-oidc.md
docs/web/saml.md

docs/web/api-security.md
docs/web/graphql.md
docs/web/websockets.md
docs/web/mass-assignment.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md
```
