# Python Source Code Review

Python is widely used for web applications, APIs, automation services, background workers, data-processing systems, administrative tools and security-sensitive backend services.

From a source-code review perspective, Python is particularly interesting because attacker-controlled data can reach powerful functionality such as:

```text
Operating system commands
Dynamic code execution
File-system operations
Network requests
Database queries
Template engines
Object deserialization
YAML parsing
XML parsing
Archive extraction
Dynamic imports
Cryptographic operations
```

This note focuses on general Python source-code review.

Framework-specific security behaviour is covered separately:

```text
docs/source-code-review/django.md
docs/source-code-review/flask.md
```

The objective is to answer:

```text
Where does attacker-controlled data enter the application?

What transformations are applied?

What validation occurs?

What security boundaries are crossed?

Which dangerous operations consume the data?

Can the attacker influence those operations in a meaningful way?
```

The fundamental review model is:

```text
SOURCE
  |
  v
ATTACKER-CONTROLLED DATA
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
SECURITY CONTROLS
  |
  v
SINK
  |
  v
SECURITY-SENSITIVE OPERATION
```

Remember:

```text
grep match
    !=
vulnerability
```

and:

```text
Sink found
    !=
Vulnerability found
```

A static match identifies code that deserves investigation.

Exploitability requires understanding the complete data flow.

!!! warning "Authorised Security Testing"
    Perform source-code review and dynamic validation only against applications, repositories and environments for which you have explicit authorisation. Source repositories can contain credentials, tokens, private keys, personal information and internal infrastructure details.

---

# Review Strategy

A practical Python review can follow this order:

```text
1. Identify Python version

2. Identify frameworks and libraries

3. Identify application entry points

4. Identify routes / API endpoints

5. Identify attacker-controlled input

6. Identify authentication

7. Identify authorisation

8. Identify validation

9. Search dangerous sinks

10. Trace source-to-sink paths

11. Review business logic

12. Review configuration

13. Search secrets

14. Review dependencies

15. Review background workers

16. Review file-processing functionality

17. Run static analysis

18. Perform variant analysis

19. Validate findings dynamically where authorised
```

---

# Identify the Application

Start by understanding the repository.

```bash
find . -maxdepth 3 -type f \( \
-name 'pyproject.toml' \
-o -name 'requirements.txt' \
-o -name 'requirements-*.txt' \
-o -name 'Pipfile' \
-o -name 'Pipfile.lock' \
-o -name 'poetry.lock' \
-o -name 'uv.lock' \
-o -name 'setup.py' \
-o -name 'setup.cfg' \
-o -name 'manage.py' \
-o -name 'wsgi.py' \
-o -name 'asgi.py' \
-o -name '.env' \
-o -name '.env.example' \
-o -name 'Dockerfile' \
\) -print
```

Common indicators:

| File | Possible Meaning |
|---|---|
| `pyproject.toml` | Modern Python project configuration |
| `requirements.txt` | pip dependencies |
| `Pipfile` | Pipenv |
| `poetry.lock` | Poetry |
| `uv.lock` | uv-managed dependencies |
| `manage.py` | Often Django |
| `wsgi.py` | WSGI application |
| `asgi.py` | ASGI application |
| `.env` | Environment configuration |
| `Dockerfile` | Runtime environment |

---

# Identify Python Version

Search:

```bash
rg -n \
'requires-python|python_requires|python_version|python-version|FROM python:' \
.
```

Check:

```text
pyproject.toml
setup.py
setup.cfg
Pipfile
Dockerfile
.github/workflows/
.gitlab-ci.yml
```

Examples:

```toml
requires-python = ">=3.12"
```

or:

```dockerfile
FROM python:3.13-slim
```

Knowing the runtime version matters when assessing:

```text
Deprecated functionality
Library compatibility
Security behaviour
Parser behaviour
Language features
Unsupported Python releases
```

---

# Identify Frameworks

Search dependency files:

```bash
rg -n -i \
'django|flask|fastapi|starlette|tornado|aiohttp|sanic|falcon|pyramid|bottle|quart' \
pyproject.toml requirements*.txt Pipfile setup.py setup.cfg 2>/dev/null
```

Common frameworks:

```text
Django
Flask
FastAPI
Starlette
aiohttp
Tornado
Sanic
Falcon
Pyramid
Bottle
Quart
```

Framework identification is important because:

```text
Input sources
Routing
Authentication
Authorisation
CSRF
Sessions
Templates
Validation
File uploads
Proxy handling
```

may be implemented by the framework rather than directly in application code.

---

# Application Structure

Common Python project structures include:

```text
project/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── views.py
│   ├── models.py
│   ├── services.py
│   └── utils.py
├── tests/
├── pyproject.toml
└── requirements.txt
```

Django may resemble:

```text
project/
├── manage.py
├── project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── app/
    ├── views.py
    ├── models.py
    └── urls.py
```

Flask may resemble:

```text
project/
├── app.py
├── routes.py
├── templates/
├── static/
└── requirements.txt
```

FastAPI may resemble:

```text
project/
├── main.py
├── routers/
├── schemas/
├── models/
├── services/
└── dependencies/
```

---

# Find Python Files

```bash
find . -type f -name '*.py' \
-not -path './.venv/*' \
-not -path './venv/*' \
-not -path './site-packages/*'
```

Count them:

```bash
find . -type f -name '*.py' \
-not -path './.venv/*' \
-not -path './venv/*' \
| wc -l
```

---

# High-Value Files

Prioritise files named:

```text
app.py
main.py
server.py
application.py

routes.py
urls.py
views.py
controllers.py
handlers.py

auth.py
authentication.py
permissions.py
authorization.py

models.py
schemas.py
serializers.py

services.py
utils.py
helpers.py

config.py
settings.py

tasks.py
jobs.py
workers.py

upload.py
download.py
import.py
export.py

admin.py
```

Search:

```bash
find . -type f \( \
-name 'routes.py' \
-o -name 'urls.py' \
-o -name 'views.py' \
-o -name 'auth.py' \
-o -name 'models.py' \
-o -name 'services.py' \
-o -name 'settings.py' \
-o -name 'config.py' \
-o -name 'tasks.py' \
\) -print
```

---

# Route Discovery

Routing is framework-specific.

Useful first-pass search:

```bash
rg -n \
'@.*\.(get|post|put|patch|delete|route)\(|add_url_rule|urlpatterns|path\(|re_path\(|APIRouter|add_route|add_api_route' \
--glob '*.py' \
.
```

Expect false positives.

---

# Flask Routes

Common patterns:

```python
@app.route("/users")
def users():
    ...
```

```python
@app.get("/users")
def users():
    ...
```

```python
@blueprint.route("/users")
def users():
    ...
```

Search:

```bash
rg -n \
'@(app|bp|blueprint|[A-Za-z_][A-Za-z0-9_]*)\.(route|get|post|put|patch|delete)\(' \
--glob '*.py' \
.
```

---

# FastAPI Routes

Examples:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    ...
```

```python
@router.post("/users")
async def create_user(...):
    ...
```

Search:

```bash
rg -n \
'@(app|router)\.(get|post|put|patch|delete|options|head)\(' \
--glob '*.py' \
.
```

Also search:

```bash
rg -n \
'APIRouter\(|include_router\(' \
--glob '*.py' \
.
```

---

# Django Routes

Search:

```bash
rg -n \
'urlpatterns|path\(|re_path\(|include\(' \
--glob '*.py' \
.
```

Django is covered in more detail in:

```text
docs/source-code-review/django.md
```

---

# Route Inventory

Create a route table:

| Method | Route | Handler | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/users/{id}` | `get_user()` | Required | Ownership |
| POST | `/login` | `login()` | Public | N/A |
| POST | `/upload` | `upload()` | Required | User |
| DELETE | `/admin/users/{id}` | `delete_user()` | Required | Admin |

This provides a map for subsequent analysis.

---

# Identify Input Sources

The exact input API depends on the framework.

Common sources include:

```text
Query parameters
Route parameters
Form values
JSON bodies
Headers
Cookies
Uploaded files
WebSocket messages
Environment variables
Database records
Message queues
Command-line arguments
Files
External APIs
```

Remember:

```text
Database data
    !=
Trusted data
```

Stored attacker input can create second-order vulnerabilities.

---

# Generic Source Search

Search for common request APIs:

```bash
rg -n \
'request\.(args|form|json|files|headers|cookies|values|data)|request\.get_json|request\.GET|request\.POST|request\.FILES|Query\(|Path\(|Body\(|Header\(|Cookie\(' \
--glob '*.py' \
.
```

---

# Flask Sources

Common Flask sources:

```python
request.args
request.form
request.values
request.json
request.get_json()
request.files
request.headers
request.cookies
request.data
```

Search:

```bash
rg -n \
'request\.(args|form|values|json|files|headers|cookies|data)|request\.get_json\(' \
--glob '*.py' \
.
```

---

# FastAPI Sources

FastAPI may express input through function parameters:

```python
@app.get("/users/{user_id}")
async def user(
    user_id: int,
    search: str | None = None
):
    ...
```

and explicitly:

```python
Query()
Path()
Body()
Header()
Cookie()
Form()
File()
UploadFile
```

Search:

```bash
rg -n \
'\b(Query|Path|Body|Header|Cookie|Form|File|UploadFile)\(' \
--glob '*.py' \
.
```

Function parameters themselves may represent attacker-controlled input even when no `request` object appears.

---

# Command-Line Input

Python applications may expose CLI functionality.

Search:

```bash
rg -n \
'argparse|sys\.argv|click\.command|click\.option|typer\.' \
--glob '*.py' \
.
```

CLI input can still become dangerous if an attacker can influence job arguments, automation inputs or administrative workflows.

---

# Environment Variables

Search:

```bash
rg -n \
'os\.environ|os\.getenv|environ\.get|dotenv' \
--glob '*.py' \
.
```

Environment variables are normally configuration inputs, but their trust depends on deployment architecture.

---

# Input Validation

Validation mechanisms may include:

```text
Type conversion
Regex
Allowlisting
Pydantic
Marshmallow
Django Forms
Django REST Framework serializers
Custom validators
```

Search:

```bash
rg -n \
'validate|validator|field_validator|model_validator|BaseModel|Schema|Serializer|Form|re\.(match|fullmatch|search)' \
--glob '*.py' \
.
```

Validation must match the downstream security requirement.

For example:

```text
Integer validation
    !=
Object authorisation

URL syntax validation
    !=
SSRF protection

HTML sanitisation
    !=
SQL injection protection
```

---

# Authentication

Search:

```bash
rg -n -i \
'authenticate|authentication|login|logout|current_user|session|jwt|bearer|oauth|openid|saml|api.?key' \
--glob '*.py' \
.
```

Identify:

```text
Login handlers
Authentication middleware
Decorators
Dependencies
Token validation
Session handling
API keys
OAuth/OIDC
SAML
```

---

# Decorators

Security controls are often implemented using decorators.

Search:

```bash
rg -n \
'@(login_required|permission_required|requires_auth|authenticated|authorized|admin_required|jwt_required)' \
--glob '*.py' \
.
```

Also search custom decorators:

```bash
rg -n \
'^def .*required|^def .*permission|^def .*auth|functools\.wraps' \
--glob '*.py' \
.
```

Review what custom decorators actually enforce.

Do not trust the decorator name.

---

# Authorisation

Authentication establishes identity.

Authorisation determines access.

Review:

```text
Roles
Permissions
Ownership
Tenant membership
Object access
Administrative actions
```

Search:

```bash
rg -n -i \
'permission|authorize|authorization|role|is_admin|is_superuser|owner|tenant|organization|organisation' \
--glob '*.py' \
.
```

---

# IDOR / BOLA

Object-level authorisation should be reviewed whenever user-controlled identifiers select records.

Candidate:

```python
user_id = request.args["id"]

user = User.query.get(user_id)

return serialize(user)
```

Critical question:

```text
Where is object-level authorisation?
```

---

# Object Lookup Search

Search ORM lookups:

```bash
rg -n \
'\.get\(|\.filter\(|\.filter_by\(|\.first\(|\.one\(|\.query\.' \
--glob '*.py' \
.
```

This generates many false positives.

Prioritise lookups containing:

```text
id
user_id
account_id
document_id
invoice_id
tenant_id
organization_id
```

---

# Tenant Isolation

Search:

```bash
rg -n -i \
'tenant|tenant_id|organization_id|organisation_id|account_id|company_id|workspace_id' \
--glob '*.py' \
.
```

Expected conceptual flow:

```text
Attacker-Controlled Object ID
          +
Authenticated Tenant
          |
          v
Scoped Database Query
```

---

# SQL Injection

Python database access may use:

```text
sqlite3
psycopg
psycopg2
PyMySQL
mysql.connector
SQLAlchemy
Django ORM
asyncpg
```

Search:

```bash
rg -n \
'\.execute\(|\.executemany\(|\.executescript\(|text\(|raw\(|cursor\(' \
--glob '*.py' \
.
```

---

# Unsafe sqlite3 Example

```python
user = request.args["user"]

query = (
    "SELECT * FROM users WHERE username = '"
    + user
    + "'"
)

cursor.execute(query)
```

Data flow:

```text
request.args["user"]
        |
        v
user
        |
        v
SQL concatenation
        |
        v
cursor.execute()
```

---

# Parameterised Query

Preferred pattern:

```python
cursor.execute(
    "SELECT * FROM users WHERE username = ?",
    (user,),
)
```

For PostgreSQL adapters, the placeholder syntax may differ.

Example:

```python
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (user,),
)
```

Do not manually add quotes around placeholders.

---

# f-Strings in SQL

High-value search:

```bash
rg -n \
'execute\(f["'\'']|executemany\(f["'\'']|text\(f["'\'']' \
--glob '*.py' \
.
```

Candidate:

```python
cursor.execute(
    f"SELECT * FROM users WHERE id = {user_id}"
)
```

---

# format() SQL

Search:

```bash
rg -n \
'execute\(.*\.format\(|executemany\(.*\.format\(' \
--glob '*.py' \
.
```

---

# Percent Formatting

Search:

```bash
rg -n \
'execute\(.*%.*\)' \
--glob '*.py' \
.
```

Inspect manually because `%s` may also be the legitimate placeholder syntax used by a database driver.

The distinction is:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,),
)
```

versus:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = %s" % user_id
)
```

---

# SQLAlchemy

Search:

```bash
rg -n \
'text\(|execute\(|exec_driver_sql\(|from_statement\(' \
--glob '*.py' \
.
```

Candidate:

```python
query = text(
    f"SELECT * FROM users WHERE name = '{name}'"
)

session.execute(query)
```

Raw SQL deserves manual review.

---

# Dynamic Identifiers

Parameterisation generally protects data values, not arbitrary SQL syntax such as:

```text
Table names
Column names
ORDER BY expressions
Sort direction
```

Unsafe candidate:

```python
sort = request.args["sort"]

query = (
    "SELECT * FROM users ORDER BY "
    + sort
)
```

Use server-controlled mappings:

```python
allowed = {
    "name": "name",
    "date": "created_at",
}

column = allowed.get(sort, "name")
```

---

# SQL Search

```bash
rg -n \
'execute\(|executemany\(|executescript\(|exec_driver_sql\(|text\(|raw\(' \
--glob '*.py' \
.
```

Refer to:

```text
docs/web/sql-injection.md
```

---

# NoSQL Injection

Python applications may use:

```text
PyMongo
Motor
Redis
Elasticsearch
OpenSearch
CouchDB
```

Search:

```bash
rg -n -i \
'pymongo|motor|mongodb|redis|elasticsearch|opensearch|find_one|find\(|aggregate\(' \
--glob '*.py' \
.
```

---

# MongoDB Candidate

```python
query = request.get_json()

result = collection.find(query)
```

Trace whether attacker-controlled JSON can introduce query operators or alter the intended query structure.

---

# MongoDB Operators

Search:

```bash
rg -n \
'\$where|\$regex|\$ne|\$gt|\$lt|\$in|\$nin|\$expr' \
--glob '*.py' \
.
```

Static operator presence alone does not prove injection.

Determine whether the attacker controls the query structure.

Refer to:

```text
docs/web/nosql-injection.md
```

---

# LDAP Injection

Python LDAP libraries include:

```text
ldap3
python-ldap
```

Search:

```bash
rg -n -i \
'ldap3|import ldap|ldap\.search|search_s|search_ext|search_filter' \
--glob '*.py' \
.
```

Candidate:

```python
username = request.args["username"]

ldap_filter = f"(uid={username})"

connection.search(
    search_base,
    ldap_filter
)
```

Trace attacker-controlled values into:

```text
LDAP filters
Distinguished names
Search bases
```

Refer to:

```text
docs/web/ldap-injection.md
```

---

# OS Command Injection

Python provides several mechanisms for executing external processes.

High-value APIs include:

```text
os.system()
os.popen()

subprocess.run()
subprocess.Popen()
subprocess.call()
subprocess.check_call()
subprocess.check_output()

asyncio.create_subprocess_shell()
asyncio.create_subprocess_exec()
```

Search:

```bash
rg -n \
'os\.(system|popen)\(|subprocess\.(run|Popen|call|check_call|check_output)\(|create_subprocess_(shell|exec)\(' \
--glob '*.py' \
.
```

---

# os.system

Candidate:

```python
host = request.args["host"]

os.system(
    "ping -c 1 " + host
)
```

Data flow:

```text
request.args["host"]
        |
        v
host
        |
        v
Shell command
        |
        v
os.system()
```

---

# subprocess with shell=True

Search:

```bash
rg -n \
'shell\s*=\s*True' \
--glob '*.py' \
.
```

Candidate:

```python
subprocess.run(
    f"ping -c 1 {host}",
    shell=True
)
```

This deserves high-priority review when attacker-controlled values enter the command string.

---

# subprocess Argument List

Compare:

```python
subprocess.run(
    ["ping", "-c", "1", host],
    check=True
)
```

with:

```python
subprocess.run(
    f"ping -c 1 {host}",
    shell=True
)
```

Passing arguments as a sequence without invoking a shell avoids shell interpretation of metacharacters.

However:

```text
No shell
    !=
Automatically safe
```

The called program may itself interpret attacker-controlled arguments or options in dangerous ways.

Review:

```text
Option injection
Executable selection
Path control
Environment variables
Downstream program behaviour
```

---

# shlex

Search:

```bash
rg -n \
'shlex\.(quote|split)\(' \
--glob '*.py' \
.
```

`shlex.quote()` may help with individual shell arguments when a shell is unavoidable, but avoiding shell execution is generally preferable.

---

# Executable Path Control

Candidate:

```python
binary = request.args["tool"]

subprocess.run(
    [binary, "--version"]
)
```

Even without `shell=True`, attacker control over the executable may be dangerous.

---

# Environment Variables

Search process calls with custom environments:

```bash
rg -n \
'env\s*=|os\.environ|PATH' \
--glob '*.py' \
.
```

Review whether attacker-controlled environment values affect executable resolution or process behaviour.

---

# Command Injection Search

```bash
rg -n \
'os\.system\(|os\.popen\(|subprocess\.(run|Popen|call|check_call|check_output)\(|shell\s*=\s*True|create_subprocess_shell\(' \
--glob '*.py' \
.
```

Refer to:

```text
docs/web/command-injection.md
```

---

# Dynamic Code Execution

Python contains powerful dynamic execution primitives.

High-value sinks include:

```text
eval()
exec()
compile()
```

Search:

```bash
rg -n \
'\beval\(|\bexec\(|\bcompile\(' \
--glob '*.py' \
.
```

---

# eval

Candidate:

```python
expression = request.args["expression"]

result = eval(expression)
```

Data flow:

```text
Request
  |
  v
expression
  |
  v
eval()
```

Attacker-controlled input reaching `eval()` is a high-priority finding candidate.

---

# Restricted eval Is Difficult

Code such as:

```python
eval(
    expression,
    {"__builtins__": {}},
    {}
)
```

deserves careful review.

Do not assume that removing built-ins automatically creates a secure sandbox.

Prefer parsing a deliberately constrained data or expression format.

---

# exec

Candidate:

```python
code = request.get_json()["code"]

exec(code)
```

Trace all paths reaching the operation.

---

# compile

`compile()` does not necessarily execute code itself, but commonly feeds:

```text
eval()
exec()
```

Search surrounding usage.

---

# ast.literal_eval

Search:

```bash
rg -n \
'ast\.literal_eval\(' \
--glob '*.py' \
.
```

`ast.literal_eval()` is intended for Python literal structures rather than arbitrary code execution.

However, do not use this fact to ignore:

```text
Resource exhaustion
Input-size concerns
Application-specific logic
```

---

# Server-Side Template Injection

Python commonly uses:

```text
Jinja2
Django Templates
Mako
Tornado templates
Chameleon
```

Search:

```bash
rg -n -i \
'jinja|mako|template|render_template|render_template_string|Template\(' \
--glob '*.py' \
.
```

---

# Jinja2

Search:

```bash
rg -n \
'Environment\(|Template\(|from_string\(|render_template_string\(' \
--glob '*.py' \
.
```

Critical distinction:

```text
Attacker input as template DATA
```

versus:

```text
Attacker input as template SOURCE
```

---

# Candidate SSTI

```python
template = request.args["template"]

return render_template_string(template)
```

Conceptually:

```text
Request
   |
   v
Template Source
   |
   v
Template Engine
```

This deserves investigation.

---

# Safer Design

Prefer fixed templates:

```python
return render_template(
    "profile.html",
    username=username,
)
```

Here the user-controlled value is data supplied to a server-controlled template.

Output safety still depends on:

```text
Template engine
Autoescaping
Output context
Explicit safe/markup operations
```

Refer to:

```text
docs/web/ssti.md
```

---

# Cross-Site Scripting

Python frameworks frequently provide template escaping, but application code can bypass it.

Search for:

```text
Markup
mark_safe
safe
autoescape
render_template_string
HTMLResponse
```

```bash
rg -n \
'Markup\(|mark_safe\(|\|safe|autoescape|HTMLResponse|render_template_string' \
--glob '*.py' \
--glob '*.html' \
.
```

---

# MarkupSafe

Candidate:

```python
return Markup(user_input)
```

Review whether attacker-controlled content is being explicitly marked as trusted HTML.

---

# Django mark_safe

Search:

```bash
rg -n \
'mark_safe\(' \
--glob '*.py' \
.
```

Django-specific behaviour is covered in:

```text
docs/source-code-review/django.md
```

---

# Jinja safe Filter

Search templates:

```bash
rg -n \
'\|\s*safe\b' \
--glob '*.html' \
--glob '*.jinja' \
--glob '*.jinja2' \
.
```

Trace the corresponding variable.

---

# HTMLResponse

FastAPI / Starlette applications may use:

```python
HTMLResponse(...)
```

Search:

```bash
rg -n \
'HTMLResponse\(' \
--glob '*.py' \
.
```

Determine whether attacker-controlled data is inserted into HTML without appropriate encoding.

---

# XSS Review Model

```text
Attacker Input
      |
      v
Application
      |
      v
Template / HTML Construction
      |
      v
Encoding?
      |
      v
Browser Context
```

Contexts include:

```text
HTML body
Attribute
JavaScript
CSS
URL
DOM
```

Refer to:

```text
docs/web/xss.md
docs/web/html-injection.md
```

---

# SSRF

Python contains many HTTP clients.

Common libraries:

```text
requests
httpx
urllib
urllib3
aiohttp
http.client
socket
```

Search:

```bash
rg -n \
'requests\.(get|post|put|patch|delete|request)\(|httpx\.(get|post|put|patch|delete|request)\(|urlopen\(|aiohttp\.ClientSession|urllib3|HTTPConnection|HTTPSConnection' \
--glob '*.py' \
.
```

---

# requests

Candidate:

```python
url = request.args["url"]

response = requests.get(url)
```

Data flow:

```text
Request Parameter
      |
      v
URL
      |
      v
requests.get()
      |
      v
Outbound Request
```

---

# Redirects

HTTP clients may automatically follow redirects depending on the client and configuration.

Search:

```bash
rg -n \
'allow_redirects|follow_redirects' \
--glob '*.py' \
.
```

SSRF controls should consider whether a permitted destination can redirect to a forbidden destination.

---

# URL Parsing

Search:

```bash
rg -n \
'urlparse\(|urlsplit\(|urljoin\(' \
--glob '*.py' \
.
```

Parsing a URL is not the same as authorising its destination.

---

# urljoin

Review carefully:

```python
target = urljoin(
    "https://example.com/",
    user_input
)
```

Depending on the supplied value, URL joining may produce a different host than expected.

Use destination validation after constructing the final URL.

---

# SSRF Review Checklist

Review:

```text
Scheme
Hostname
Port
DNS resolution
Redirects
Proxy behaviour
IP address
IPv6
Internal networks
Loopback
Link-local
Cloud metadata
Alternative IP representations
DNS rebinding considerations
Network egress controls
```

Refer to:

```text
docs/web/ssrf.md
```

---

# Path Traversal

Common file operations:

```text
open()
pathlib.Path
os.path
shutil
send_file-style framework helpers
```

Search:

```bash
rg -n \
'\bopen\(|Path\(|read_text\(|read_bytes\(|write_text\(|write_bytes\(|shutil\.(copy|copyfile|move|rmtree)\(' \
--glob '*.py' \
.
```

---

# Candidate

```python
filename = request.args["file"]

with open(
    "/srv/files/" + filename,
    "rb"
) as file:
    return file.read()
```

Data flow:

```text
Request
   |
   v
filename
   |
   v
Path Construction
   |
   v
open()
```

---

# os.path.join

Search:

```bash
rg -n \
'os\.path\.join\(' \
--glob '*.py' \
.
```

Do not assume:

```python
os.path.join(base, user_input)
```

guarantees that the final path remains inside `base`.

Path joining is not a security boundary.

---

# pathlib

Search:

```bash
rg -n \
'Path\(|\.resolve\(|\.relative_to\(' \
--glob '*.py' \
.
```

A common defensive model is:

```text
Trusted Base
    |
    v
Join Candidate
    |
    v
Canonicalise
    |
    v
Verify Candidate Is Within Base
    |
    v
File Operation
```

The implementation must also consider:

```text
Symbolic links
Non-existent files
Race conditions
Platform path semantics
```

---

# Path Containment

Conceptually:

```python
base = Path("/srv/files").resolve()

candidate = (
    base / user_input
).resolve()

candidate.relative_to(base)
```

This can be useful as part of containment checking.

However, file-system security may still require consideration of:

```text
Symlink changes
TOCTOU
File creation
Permissions
Mount points
```

---

# File Operations Search

```bash
rg -n \
'\bopen\(|Path\(|os\.path\.join\(|shutil\.|tempfile\.|send_file|send_from_directory' \
--glob '*.py' \
.
```

Refer to:

```text
docs/web/path-traversal.md
```

---

# File Upload

Common upload functionality depends on the framework.

Search:

```bash
rg -n -i \
'upload|uploadedfile|uploadfile|request\.files|\.save\(|filename|secure_filename' \
--glob '*.py' \
.
```

Review:

```text
Filename
Extension
MIME type
File signature
Size
Storage location
Generated filename
Overwrite behaviour
Web accessibility
Execution possibility
Downstream processing
Archive extraction
```

---

# Filename Handling

Never assume:

```text
filename
=
Trusted
```

Uploaded filenames are typically attacker-controlled metadata.

---

# Werkzeug secure_filename

Flask applications may use:

```python
secure_filename(filename)
```

Search:

```bash
rg -n \
'secure_filename\(' \
--glob '*.py' \
.
```

This helps normalise unsafe filename components but does not provide complete upload security.

You must still review:

```text
Extension policy
Storage location
Generated names
Content validation
Permissions
Execution
Authorisation
```

---

# Temporary Files

Search:

```bash
rg -n \
'tempfile\.|NamedTemporaryFile|TemporaryDirectory|mkstemp|mkdtemp' \
--glob '*.py' \
.
```

Prefer secure temporary-file APIs rather than predictable filenames.

---

# Archive Extraction

High-value libraries:

```text
zipfile
tarfile
shutil.unpack_archive
```

Search:

```bash
rg -n \
'zipfile|ZipFile|tarfile|TarFile|extractall\(|extract\(|unpack_archive\(' \
--glob '*.py' \
.
```

---

# Archive Entry Traversal

Conceptual vulnerability:

```text
Archive
   |
   v
Entry Name
   |
   v
Destination Path
   |
   v
Write Outside Intended Directory
```

Review extraction behaviour against the actual Python version and API being used.

Do not rely on historical assumptions about standard-library archive extraction without checking the deployed runtime.

---

# Custom Extraction

Candidate:

```python
for member in archive.namelist():
    destination = os.path.join(
        upload_directory,
        member,
    )

    with open(destination, "wb") as output:
        output.write(
            archive.read(member)
        )
```

Trace whether archive-controlled names can escape the destination.

Refer to:

```text
docs/web/file-upload.md
docs/web/path-traversal.md
```

---

# Pickle Deserialization

Python `pickle` is a critical source-review target.

Search:

```bash
rg -n \
'pickle\.(load|loads)\(|cPickle|_pickle' \
--glob '*.py' \
.
```

---

# Dangerous Candidate

```python
data = request.get_data()

obj = pickle.loads(data)
```

Data flow:

```text
HTTP Body
    |
    v
pickle.loads()
    |
    v
Python Object Construction
```

Never deserialize untrusted pickle data.

---

# Pickle Trust Boundary

Important question:

```text
Can an attacker create or modify the pickle?
```

Potential sources include:

```text
HTTP requests
Cookies
Uploaded files
Message queues
Cache entries
Database values
Shared storage
Signed but attacker-obtainable objects
```

---

# Pickle Integrity

Even if a pickle is protected by an integrity mechanism, review:

```text
Who can obtain a valid signature?
Who controls the signing key?
Can the signed data originate from user input?
Can another service generate signed objects?
```

Prefer data-only formats for untrusted boundaries.

---

# shelve

Python `shelve` commonly uses pickle internally.

Search:

```bash
rg -n \
'\bshelve\b' \
--glob '*.py' \
.
```

Review whether untrusted parties can modify the underlying shelf files.

---

# joblib

Search:

```bash
rg -n \
'joblib\.(load|dump)\(' \
--glob '*.py' \
.
```

Joblib persistence may involve pickle-based object loading.

Review the trust boundary.

---

# ML Model Loading

Search:

```bash
rg -n \
'torch\.load\(|joblib\.load\(|pickle\.load|pickle\.loads|cloudpickle|dill\.loads|dill\.load' \
--glob '*.py' \
.
```

Model files and serialized Python objects should be treated as potentially executable content depending on the serialization mechanism and library.

This becomes especially important for:

```text
Uploaded models
Downloaded models
Shared model repositories
CI/CD model artifacts
Third-party ML files
```

---

# dill and cloudpickle

Search:

```bash
rg -n \
'dill\.(load|loads)\(|cloudpickle\.(load|loads)\(' \
--glob '*.py' \
.
```

Treat these as high-value deserialization review targets.

Refer to:

```text
docs/web/deserialization.md
```

---

# YAML Deserialization

PyYAML is another important target.

Search:

```bash
rg -n \
'yaml\.(load|unsafe_load|full_load|safe_load)\(' \
--glob '*.py' \
.
```

---

# yaml.safe_load

Preferred for ordinary untrusted YAML data:

```python
data = yaml.safe_load(content)
```

This restricts construction to standard YAML types rather than arbitrary Python objects.

---

# yaml.load

Review the configured loader:

```python
yaml.load(
    content,
    Loader=...
)
```

The security properties depend on the loader.

High-value loaders include:

```text
UnsafeLoader
Loader
FullLoader
SafeLoader
```

Do not classify all `yaml.load()` calls identically.

Determine:

```text
PyYAML version
Loader
Input trust
Required object types
```

---

# unsafe_load

Search:

```bash
rg -n \
'yaml\.unsafe_load\(' \
--glob '*.py' \
.
```

Attacker-controlled input reaching unsafe object construction is a high-priority candidate.

---

# YAML Search

```bash
rg -n \
'import yaml|from yaml|yaml\.(load|safe_load|full_load|unsafe_load)\(' \
--glob '*.py' \
.
```

---

# XML External Entity Injection

Python provides multiple XML parsers.

Search:

```bash
rg -n \
'xml\.etree|ElementTree|lxml|etree|xml\.dom|minidom|pulldom|sax|xmlrpc|BeautifulSoup' \
--glob '*.py' \
.
```

Do not classify parser use alone as XXE.

Review:

```text
Parser library
Python version
Library version
Parser options
DTD handling
Entity handling
Network access
Attacker control
```

---

# lxml

Search:

```bash
rg -n \
'XMLParser\(|fromstring\(|parse\(' \
--glob '*.py' \
.
```

Important options may include:

```text
resolve_entities
load_dtd
no_network
huge_tree
```

Inspect explicitly configured parsers.

---

# defusedxml

Search:

```bash
rg -n \
'defusedxml' \
--glob '*.py' \
.
```

`defusedxml` provides hardened alternatives for several XML parsing scenarios.

Review actual usage rather than simply noting the dependency.

Refer to:

```text
docs/web/xxe.md
```

---

# Open Redirect

Python frameworks commonly provide redirect helpers.

Search:

```bash
rg -n \
'\bredirect\(|RedirectResponse\(' \
--glob '*.py' \
.
```

Candidate:

```python
next_url = request.args["next"]

return redirect(next_url)
```

Trace whether users can select arbitrary external destinations.

---

# URL Validation

Search:

```bash
rg -n \
'urlparse\(|urlsplit\(|urljoin\(' \
--glob '*.py' \
.
```

Review:

```text
Scheme
Hostname
Port
Relative URLs
Scheme-relative URLs
Backslashes
Encoding
Final destination after joining
```

Refer to:

```text
docs/web/open-redirect.md
```

---

# HTTP Header Injection

Search response construction:

```bash
rg -n \
'headers\[|set_header|Response\(|make_response|Content-Disposition|Location' \
--glob '*.py' \
.
```

Review attacker-controlled data entering:

```text
Location
Content-Disposition
Set-Cookie
Custom headers
```

Frameworks may reject newline characters, but application-specific header logic still deserves review.

---

# Host Header Attacks

Search:

```bash
rg -n \
'request\.host|request\.headers.*Host|HTTP_HOST|get_host\(|X-Forwarded-Host|X_FORWARDED_HOST' \
--glob '*.py' \
.
```

Review host-derived values used for:

```text
Password reset links
Email verification links
Absolute URLs
OAuth callbacks
Tenant selection
Security decisions
```

Conceptually unsafe:

```python
reset_url = (
    "https://"
    + request.host
    + "/reset?token="
    + token
)
```

Prefer trusted application configuration when generating security-sensitive absolute URLs.

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# Proxy Trust

Search:

```bash
rg -n -i \
'proxyfix|forwarded|x-forwarded-for|x-forwarded-host|x-forwarded-proto|trusted.?proxy' \
--glob '*.py' \
.
```

Review:

```text
Trusted proxy count
Deployment topology
Client IP derivation
Host derivation
Scheme derivation
```

Incorrect proxy trust can affect:

```text
Rate limiting
Audit logging
Host validation
HTTPS detection
Security redirects
IP allowlists
```

---

# CORS

Search:

```bash
rg -n -i \
'cors|allow_origins|allow_credentials|access-control-allow-origin|CORS\(' \
--glob '*.py' \
.
```

Frameworks may use:

```text
Flask-CORS
django-cors-headers
Starlette CORSMiddleware
FastAPI CORSMiddleware
```

Review:

```text
Allowed origins
Credentials
Methods
Headers
Sensitive endpoints
```

Do not report broad CORS as exploitable without establishing meaningful cross-origin access.

Refer to:

```text
docs/web/cors.md
```

---

# CSRF

Search:

```bash
rg -n -i \
'csrf|xsrf|csrf_exempt|csrf_protect|CSRFProtect' \
--glob '*.py' \
.
```

Review:

```text
State-changing routes
Cookie-based authentication
Framework middleware
Exemptions
Custom tokens
```

Do not assume APIs require CSRF protection without first understanding how credentials are transported.

Refer to:

```text
docs/web/csrf.md
```

---

# Session Management

Search:

```bash
rg -n \
'\bsession\b|session\[|set_cookie\(|delete_cookie\(' \
--glob '*.py' \
.
```

Review:

```text
Session storage
Cookie integrity
Cookie confidentiality
Secure
HttpOnly
SameSite
Expiration
Session rotation
Logout
Privilege changes
```

---

# Cookie Security

Search:

```bash
rg -n \
'set_cookie\(|SESSION_COOKIE|secure\s*=|httponly\s*=|samesite\s*=' \
--glob '*.py' \
.
```

Do not report missing flags solely from application source if they may be configured elsewhere.

Check deployment and framework configuration.

Refer to:

```text
docs/web/session-management.md
```

---

# JWT

Common libraries include:

```text
PyJWT
python-jose
Authlib
jwcrypto
```

Search:

```bash
rg -n -i \
'jwt|pyjwt|jose|jwcrypto|authlib' \
pyproject.toml requirements*.txt Pipfile --glob '*.py' 2>/dev/null
```

---

# JWT Decode

Search:

```bash
rg -n \
'jwt\.decode\(|JWT\(|decode_token|verify_token' \
--glob '*.py' \
.
```

Review:

```text
Signature verification
Allowed algorithms
Issuer
Audience
Expiration
Not-before
Key selection
JWKS
Claims
```

---

# Dangerous Verification Configuration

Search:

```bash
rg -n \
'verify_signature|verify_exp|verify_aud|algorithms\s*=' \
--glob '*.py' \
.
```

Do not report based on option names alone.

Trace actual configuration and code paths.

Refer to:

```text
docs/web/jwt.md
```

---

# OAuth / OIDC

Search:

```bash
rg -n -i \
'oauth|openid|oidc|client_id|client_secret|redirect_uri|code_verifier|code_challenge|nonce|state' \
--glob '*.py' \
.
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
account linking
callback handling
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
'saml|pysaml|python3-saml|xmlsec|onelogin' \
--glob '*.py' \
pyproject.toml requirements*.txt 2>/dev/null
```

Review:

```text
Signature validation
Assertion validation
Issuer
Audience
Destination
Recipient
Replay
Certificate trust
Attribute mapping
```

Refer to:

```text
docs/web/saml.md
```

---

# Password Hashing

Common secure libraries and APIs include:

```text
argon2-cffi
bcrypt
passlib
PBKDF2
Framework password hashers
```

Search:

```bash
rg -n -i \
'argon2|bcrypt|passlib|pbkdf2|password_hash|check_password|make_password' \
--glob '*.py' \
.
```

---

# Weak Password Hashing Candidates

Search:

```bash
rg -n \
'hashlib\.(md5|sha1)\(' \
--glob '*.py' \
.
```

Do not report every MD5 or SHA-1 use as password weakness.

Determine what is being hashed.

```text
Password?
Token?
Cache key?
Checksum?
Protocol value?
```

---

# Password Reset

Search:

```bash
rg -n -i \
'forgot.?password|reset.?password|password.?reset|reset.?token' \
--glob '*.py' \
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
Rate limiting
Host handling
Session invalidation
```

---

# Randomness

Search:

```bash
rg -n \
'\brandom\.|random\.random\(|random\.randint\(|random\.choice\(|secrets\.|os\.urandom\(|uuid\.uuid4\(' \
--glob '*.py' \
.
```

---

# secrets Module

For security-sensitive tokens, Python provides the `secrets` module.

Examples:

```python
secrets.token_bytes()
secrets.token_hex()
secrets.token_urlsafe()
secrets.choice()
```

---

# random Module

The general-purpose `random` module is not intended for cryptographic security.

Prioritise cases where it generates:

```text
Password-reset tokens
API keys
Session identifiers
MFA codes
Invitation tokens
Verification tokens
```

---

# UUID

Do not automatically classify:

```python
uuid.uuid4()
```

as insecure.

Review the security requirement.

Random UUIDs may be appropriate for identifiers but should not automatically be assumed to provide all properties required of authentication secrets.

---

# MFA

Search:

```bash
rg -n -i \
'totp|hotp|otp|mfa|2fa|two.?factor|authenticator|recovery.?code|backup.?code' \
--glob '*.py' \
.
```

Review:

```text
Enrollment
Verification
Rate limiting
Recovery
Reset
Remember-device
Bypass paths
```

Refer to:

```text
docs/web/mfa.md
```

---

# Cryptography

Search:

```bash
rg -n -i \
'cryptography|Crypto\.|AES|DES|RSA|Fernet|Cipher|hashlib|hmac|PBKDF2|scrypt|argon2' \
--glob '*.py' \
.
```

Review:

```text
Algorithm
Mode
Key size
Key source
Nonce / IV
Authentication
Randomness
Key reuse
Hard-coded secrets
Error handling
```

---

# PyCryptodome

Search:

```bash
rg -n \
'Crypto\.Cipher|AES\.new|DES\.new|DES3\.new' \
--glob '*.py' \
.
```

Do not classify cryptographic use from algorithm names alone.

Review the complete construction.

---

# Secrets Exposure

Search:

```bash
rg -n -i \
'password|passwd|secret|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|token|database_url|dsn' \
.
```

---

# High-Value Secret Files

```text
.env
.env.*
settings.py
config.py
secrets.py
credentials.py

pyproject.toml
Dockerfile
docker-compose.yml

CI/CD configuration
Tests
Fixtures
Example configurations
```

---

# Private Keys

Search:

```bash
rg -n \
'BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY' \
.
```

---

# AWS-Style Access Keys

Generic secret scanners are preferable, but initial searching may include:

```bash
rg -n \
'AKIA[0-9A-Z]{16}' \
.
```

Do not assume every regex match is a valid active credential.

---

# Secret-Scanning Tools

Useful tools include:

```text
TruffleHog
Gitleaks
GitHub secret scanning
Semgrep
```

Always validate:

```text
Is it real?
Is it sensitive?
Is it active?
Is it reachable?
Is it already revoked?
```

Refer to:

```text
docs/web/secrets-exposure.md
```

---

# Information Disclosure

Search:

```bash
rg -n \
'print\(|pprint\(|traceback|debug\s*=\s*True|DEBUG\s*=\s*True|logger\.(debug|info|warning|error|exception)' \
--glob '*.py' \
.
```

---

# Debug Mode

High-value search:

```bash
rg -n -i \
'debug\s*=\s*true|DEBUG\s*=\s*True' \
.
```

Do not report a development default unless it is actually deployed in production.

---

# Exception Handling

Search:

```bash
rg -n \
'except Exception|traceback\.|format_exc|print_exc|logger\.exception' \
--glob '*.py' \
.
```

Review whether internal exceptions reach users.

---

# Sensitive Logging

Search:

```bash
rg -n \
'logger\.(debug|info|warning|error|critical|exception)\(|logging\.(debug|info|warning|error|critical|exception)\(' \
--glob '*.py' \
.
```

Review logging of:

```text
Passwords
Session IDs
JWTs
Authorization headers
API keys
Personal information
Request bodies
MFA codes
Reset tokens
```

---

# Business Logic

Search for domain-sensitive operations:

```bash
rg -n -i \
'price|amount|balance|quantity|discount|coupon|credit|refund|approved|verified|status|role|permission|tenant|owner' \
--glob '*.py' \
.
```

Business logic vulnerabilities often have no obvious dangerous API.

Review:

```text
Price calculation
Discounts
Refunds
Account credits
Inventory
Approval workflows
Role changes
Tenant changes
Verification
State transitions
```

---

# Client-Supplied Price

Candidate:

```python
price = request.json["price"]

order.total = price
```

Ask:

```text
Should the client control the authoritative price?
```

Prefer:

```text
Product ID
    |
    v
Server-Side Product Lookup
    |
    v
Server-Side Price
```

---

# State Machines

Search:

```bash
rg -n -i \
'status|state|pending|approved|completed|cancelled|refunded|verified' \
--glob '*.py' \
.
```

Map:

```text
PENDING
   |
   v
APPROVED
   |
   v
COMPLETED
```

Determine whether required transitions can be skipped.

Refer to:

```text
docs/web/business-logic.md
```

---

# Race Conditions

Python applications frequently perform:

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

This can create race conditions when operations are concurrent.

High-value functionality:

```text
Balance changes
Coupons
Inventory
Password reset
Invitation acceptance
One-time tokens
File operations
Job processing
```

---

# Transactions

Search:

```bash
rg -n -i \
'transaction|atomic|begin\(|commit\(|rollback\(|with_for_update|select_for_update|FOR UPDATE' \
--glob '*.py' \
.
```

---

# Locks

Search:

```bash
rg -n \
'Lock\(|RLock\(|Semaphore\(|asyncio\.Lock|filelock|redis.*lock' \
--glob '*.py' \
.
```

The presence or absence of a lock does not prove security.

Understand the concurrency model and shared state.

---

# Async Code

Search:

```bash
rg -n \
'async def|await |asyncio\.' \
--glob '*.py' \
.
```

Review state shared between asynchronous requests/tasks.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Rate Limiting

Search:

```bash
rg -n -i \
'rate.?limit|ratelimit|throttle|limiter|slowapi|flask-limiter' \
--glob '*.py' \
.
```

Prioritise:

```text
Login
Password reset
OTP
MFA
Registration
Email verification
Search
Exports
Expensive APIs
```

---

# Client IP

Search:

```bash
rg -n \
'remote_addr|client\.host|REMOTE_ADDR|X-Forwarded-For|x-forwarded-for' \
--glob '*.py' \
.
```

If rate limiting depends on IP addresses, review trusted-proxy handling.

Refer to:

```text
docs/web/rate-limiting.md
```

---

# Mass Assignment

Python frameworks and ORMs can expose mass-assignment-style problems.

Candidate:

```python
data = request.get_json()

for key, value in data.items():
    setattr(user, key, value)
```

Search:

```bash
rg -n \
'setattr\(|__dict__\.update|\.update\(\*\*|\*\*request|\*\*data|model_validate|from_orm' \
--glob '*.py' \
.
```

---

# setattr

Candidate:

```python
for key, value in request.json.items():
    setattr(account, key, value)
```

Review whether security-sensitive fields can be modified:

```text
is_admin
role
permissions
owner_id
tenant_id
verified
balance
status
```

---

# **kwargs

Candidate:

```python
user = User(
    **request.get_json()
)
```

Whether this is dangerous depends on:

```text
Model constructor
Schema validation
Allowed fields
ORM behaviour
Business rules
```

Do not report based on `**data` alone.

Refer to:

```text
docs/web/mass-assignment.md
```

---

# Prototype Pollution

Prototype pollution is primarily a JavaScript concern.

However, Python services may process attacker-controlled JSON that is later consumed by JavaScript systems.

Review cross-language trust boundaries such as:

```text
Python API
   |
   v
JSON
   |
   v
Node.js Service
```

Do not classify Python dictionary manipulation itself as JavaScript prototype pollution.

Refer to:

```text
docs/web/prototype-pollution.md
```

---

# Dependency Security

Python projects may use:

```text
requirements.txt
requirements-dev.txt
pyproject.toml
Pipfile.lock
poetry.lock
uv.lock
```

Find:

```bash
find . -maxdepth 3 -type f \( \
-name 'requirements*.txt' \
-o -name 'pyproject.toml' \
-o -name 'Pipfile*' \
-o -name 'poetry.lock' \
-o -name 'uv.lock' \
\) -print
```

---

# requirements.txt

Inspect:

```bash
cat requirements.txt
```

Look for:

```text
Unpinned dependencies
Old versions
Direct Git dependencies
Custom indexes
Local packages
```

---

# pyproject.toml

Search:

```bash
rg -n \
'dependencies|optional-dependencies|requires-python|index|source' \
pyproject.toml
```

---

# pip-audit

A useful dependency-auditing tool is:

```bash
pip-audit
```

Against requirements:

```bash
pip-audit -r requirements.txt
```

JSON output:

```bash
pip-audit -r requirements.txt -f json
```

---

# OSV-Scanner

For repository-level dependency analysis:

```bash
osv-scanner scan source -r .
```

Review the scanner output manually.

A vulnerable dependency version does not automatically prove that the vulnerable functionality is reachable.

---

# Dependency Review Model

```text
Dependency
    |
    v
Known Vulnerability
    |
    v
Affected Version?
    |
    v
Affected Feature Used?
    |
    v
Reachable?
    |
    v
Attacker Controlled?
    |
    v
Exploitability
```

Refer to:

```text
docs/web/dependency-security.md
```

---

# Dynamic Imports

Python can import modules dynamically.

Search:

```bash
rg -n \
'importlib\.import_module|__import__\(' \
--glob '*.py' \
.
```

Candidate:

```python
module_name = request.args["module"]

module = importlib.import_module(
    module_name
)
```

Review attacker influence over:

```text
Module names
Python path
Plugin directories
File-system locations
```

---

# sys.path Manipulation

Search:

```bash
rg -n \
'sys\.path\.(append|insert)|PYTHONPATH' \
--glob '*.py' \
.
```

Review whether writable directories are introduced into module search paths.

---

# Plugin Systems

Search:

```bash
rg -n -i \
'plugin|extension|import_module|entry_points|load_module' \
--glob '*.py' \
.
```

Plugin loading can create dangerous trust boundaries when users control:

```text
Plugin path
Plugin package
Module name
Configuration
Archive
```

---

# getattr

Search:

```bash
rg -n \
'getattr\(' \
--glob '*.py' \
.
```

Candidate:

```python
method = request.args["method"]

handler = getattr(
    service,
    method
)

handler()
```

`getattr()` is not inherently dangerous.

Review attacker influence over method selection.

---

# setattr

Search:

```bash
rg -n \
'setattr\(' \
--glob '*.py' \
.
```

Review:

```text
Mass assignment
Security configuration
Object state
Role changes
```

---

# Globals and Locals

Search:

```bash
rg -n \
'globals\(\)|locals\(\)' \
--glob '*.py' \
.
```

Candidate:

```python
function_name = request.args["action"]

globals()[function_name]()
```

This deserves manual investigation.

---

# Reflection and Introspection

Search:

```bash
rg -n \
'getattr\(|setattr\(|hasattr\(|globals\(\)|locals\(\)|inspect\.' \
--glob '*.py' \
.
```

Dynamic behaviour can obscure data flow.

---

# Unsafe Temporary Paths

Search:

```bash
rg -n \
'/tmp/|tempfile\.mktemp|mktemp\(' \
--glob '*.py' \
.
```

`tempfile.mktemp()` is unsafe for creating temporary files because it introduces a race between name generation and file creation.

Prefer secure APIs such as:

```text
NamedTemporaryFile
TemporaryFile
mkstemp
TemporaryDirectory
```

as appropriate.

---

# File Permissions

Search:

```bash
rg -n \
'os\.chmod\(|chmod\(|umask\(' \
--glob '*.py' \
.
```

Review overly broad permissions around:

```text
Secrets
Uploads
Temporary files
Configuration
Private keys
Generated reports
```

---

# Symlinks

Search:

```bash
rg -n \
'os\.symlink|Path.*symlink|readlink|is_symlink' \
--glob '*.py' \
.
```

Consider symlink attacks when applications perform privileged file operations in attacker-writable directories.

---

# TOCTOU

Look for patterns such as:

```python
if os.path.exists(path):
    ...
    open(path)
```

or:

```python
if allowed(path):
    ...
    write(path)
```

A security decision based on file state followed by a separate file operation may be vulnerable to race conditions in attacker-influenced directories.

---

# HTTP Request Smuggling

Application source review alone usually cannot confirm HTTP request smuggling because the vulnerability often arises from disagreement between:

```text
Front-end proxy
Reverse proxy
Load balancer
Application server
Framework
```

However, source/configuration review can identify relevant architecture:

```text
Gunicorn
uWSGI
Hypercorn
Uvicorn
Daphne
nginx
Apache
HAProxy
Traefik
Cloud proxies
```

Search:

```bash
rg -n -i \
'gunicorn|uwsgi|uvicorn|hypercorn|daphne|nginx|haproxy|traefik' \
.
```

Do not report request smuggling solely from application code.

Refer to:

```text
docs/web/http-request-smuggling.md
```

---

# Web Cache Security

Search:

```bash
rg -n -i \
'cache|cached|redis|memcache|lru_cache|Cache-Control|Vary' \
--glob '*.py' \
.
```

Review cache keys for security-relevant dimensions:

```text
User
Tenant
Authentication state
Role
Language
Host
Headers
Query parameters
```

Incorrect cache key construction may cause cross-user data leakage.

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# HTTP Security Headers

Search:

```bash
rg -n -i \
'content-security-policy|x-frame-options|x-content-type-options|strict-transport-security|referrer-policy|permissions-policy' \
.
```

Do not report a vulnerability solely because a header is absent from Python source.

Headers may be added by:

```text
Reverse proxy
CDN
Ingress controller
Web server
WAF
Platform
```

Validate the actual HTTP response.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# GraphQL

Common Python GraphQL libraries include:

```text
Graphene
Strawberry
Ariadne
graphql-core
```

Search:

```bash
rg -n -i \
'graphene|strawberry|ariadne|graphql|resolver|mutation' \
--glob '*.py' \
pyproject.toml requirements*.txt 2>/dev/null
```

Review:

```text
Resolvers
Mutations
Object-level authorisation
Field-level authorisation
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

Python WebSocket libraries may include:

```text
websockets
Starlette WebSocket
FastAPI WebSocket
Django Channels
aiohttp
Socket.IO
```

Search:

```bash
rg -n -i \
'websocket|websockets|channels|socketio|WebSocket' \
--glob '*.py' \
.
```

Review:

```text
Connection authentication
Message authorisation
Channel access
Object access
Origin validation
State-changing operations
```

Refer to:

```text
docs/web/websockets.md
```

---

# gRPC

Python gRPC commonly uses:

```text
grpcio
grpcio-tools
```

Search:

```bash
rg -n -i \
'grpc|Servicer|add_.*Servicer_to_server|grpc\.server|grpc\.aio' \
--glob '*.py' \
pyproject.toml requirements*.txt 2>/dev/null
```

Review:

```text
Service methods
Authentication interceptors
Authorisation
Metadata
Object-level access
Input validation
TLS
Reflection
Error handling
```

Refer to:

```text
docs/web/grpc-security.md
```

---

# Webhooks

Search:

```bash
rg -n -i \
'webhook|callback|signature|hmac' \
--glob '*.py' \
.
```

Review:

```text
Signature verification
Secret management
Timestamp validation
Replay protection
Payload validation
State changes
```

---

# HMAC

Search:

```bash
rg -n \
'hmac\.new|hmac\.compare_digest' \
--glob '*.py' \
.
```

When verifying signatures, compare values using an appropriate constant-time comparison mechanism such as:

```python
hmac.compare_digest()
```

where applicable.

---

# Background Jobs

Python applications commonly use:

```text
Celery
RQ
Dramatiq
Huey
APScheduler
```

Search:

```bash
rg -n -i \
'celery|shared_task|@task|rq\.|dramatiq|huey|apscheduler' \
--glob '*.py' \
.
```

Background processing can create second-order vulnerabilities.

Example:

```text
HTTP Request
    |
    v
Database
    |
    v
Celery Job
    |
    v
subprocess.run()
```

The dangerous sink may be far removed from the original request.

---

# Celery

Search:

```bash
rg -n \
'@shared_task|@.*\.task|\.delay\(|apply_async\(' \
--glob '*.py' \
.
```

Review:

```text
Task arguments
Queue trust
Serialization format
Worker privileges
Command execution
File processing
Network access
```

---

# Message Serialization

Search:

```bash
rg -n -i \
'serializer|pickle|json|msgpack|yaml' \
--glob '*.py' \
.
```

Avoid unsafe serialization across untrusted queue boundaries.

---

# Second-Order Vulnerabilities

Do not stop tracing when input is stored.

Example:

```text
POST /profile
      |
      v
Biography
      |
      v
Database
      |
      v
Background Report Generator
      |
      v
HTML Template
      |
      v
Stored XSS
```

Another example:

```text
POST /import
      |
      v
URL stored
      |
      v
Background Worker
      |
      v
requests.get()
      |
      v
SSRF
```

---

# API Security

Map each API endpoint:

```text
Route
   |
   v
Authentication
   |
   v
Authorisation
   |
   v
Validation
   |
   v
Business Logic
   |
   v
Data Access
```

Search:

```bash
rg -n \
'@.*\.(get|post|put|patch|delete)\(|APIRouter|APIView|ViewSet' \
--glob '*.py' \
.
```

Refer to:

```text
docs/web/api-security.md
```

---

# Administrative Functionality

Search:

```bash
rg -n -i \
'admin|administrator|superuser|staff|management|privileged' \
--glob '*.py' \
.
```

Map:

```text
Administrative Route
        |
        v
Authentication
        |
        v
Role / Permission
        |
        v
Sensitive Operation
```

---

# Registration

Search:

```bash
rg -n -i \
'register|registration|signup|sign.?up|create.?user' \
--glob '*.py' \
.
```

Review:

```text
Default role
Tenant assignment
Mass assignment
Email verification
Invitation logic
Duplicate accounts
Privilege selection
```

---

# Account Modification

Search:

```bash
rg -n -i \
'change.?email|update.?email|change.?password|update.?password|profile|account.?settings' \
--glob '*.py' \
.
```

Review whether sensitive changes require:

```text
Current password
MFA
Re-authentication
Confirmation
Ownership
```

depending on application requirements.

---

# Static Analysis

Static analysis should assist manual review.

Useful tools include:

```text
Semgrep
CodeQL
Bandit
Ruff
pip-audit
OSV-Scanner
TruffleHog
Gitleaks
```

---

# Semgrep

Semgrep supports Python security analysis and custom rules.

Example:

```bash
semgrep scan --config auto .
```

For security-focused rulesets, choose an appropriate maintained configuration and review what rules are actually being executed.

Semgrep findings are candidates:

```text
Semgrep Finding
      |
      v
Reachable?
      |
      v
Attacker Controlled?
      |
      v
Security Control?
      |
      v
Exploitable?
```

Official documentation:

```text
https://semgrep.dev/docs/
```

---

# CodeQL

CodeQL supports Python analysis.

It is useful for:

```text
Data flow
Taint tracking
Call graphs
Variant analysis
Security queries
```

Official documentation:

```text
https://codeql.github.com/docs/codeql-language-guides/codeql-for-python/
```

---

# Bandit

Bandit is designed to identify common security issues in Python code.

Install:

```bash
python3 -m pip install bandit
```

Run:

```bash
bandit -r .
```

Exclude tests:

```bash
bandit -r . -x ./tests
```

JSON:

```bash
bandit -r . -f json -o bandit.json
```

Typical areas include:

```text
subprocess
shell execution
hard-coded passwords
unsafe deserialization
weak cryptography
temporary files
TLS configuration
```

Bandit findings still require manual validation.

Official project:

```text
https://github.com/PyCQA/bandit
```

---

# Ruff

Ruff is primarily a Python linter rather than a dedicated vulnerability scanner.

It can still help identify:

```text
Bad coding patterns
Suspicious constructs
Error-prone code
Quality issues relevant to review
```

Use security-focused tooling alongside it.

---

# Reverse Sink Analysis

For large Python applications, start with dangerous sinks and trace backwards.

Example:

```text
subprocess.run()
       ^
       |
ReportGenerator
       ^
       |
ExportService
       ^
       |
POST /export
```

High-value starting points:

```text
eval
exec

os.system
os.popen

subprocess.run
subprocess.Popen
subprocess.call
subprocess.check_output

pickle.load
pickle.loads
dill.loads
cloudpickle.loads
joblib.load

yaml.load
yaml.unsafe_load

requests.get
requests.post
httpx
urlopen

open
Path
shutil

cursor.execute
session.execute
text

render_template_string
Template
from_string

redirect
RedirectResponse

getattr
setattr
importlib.import_module
```

---

# Forward Source Analysis

Start with attacker-controlled sources and trace forward.

Example:

```text
request.args
request.form
request.json
request.files
request.headers
request.cookies
route parameters
WebSocket messages
```

Then:

```text
SOURCE
  |
  v
Variable
  |
  v
Function
  |
  v
Service
  |
  v
Database / File / Network / Process
```

---

# Source-to-Sink Example - SQL Injection

```text
GET /search?q=test
       |
       v
request.args["q"]
       |
       v
query
       |
       v
f-string SQL
       |
       v
cursor.execute()
```

Review:

```text
Is q attacker-controlled?

Is the query parameterised?

Can q modify SQL syntax?

Is the route reachable?

What authentication is required?

What database permissions exist?
```

---

# Source-to-Sink Example - Command Injection

```text
POST /diagnostics
       |
       v
request.json["host"]
       |
       v
host
       |
       v
f"ping -c 1 {host}"
       |
       v
subprocess.run(..., shell=True)
```

---

# Source-to-Sink Example - SSRF

```text
POST /preview
       |
       v
request.json["url"]
       |
       v
url
       |
       v
requests.get(url)
```

Review:

```text
Destination policy
Redirects
DNS
Network controls
```

---

# Source-to-Sink Example - Path Traversal

```text
GET /download?file=report.pdf
       |
       v
request.args["file"]
       |
       v
filename
       |
       v
base + filename
       |
       v
open()
```

---

# Source-to-Sink Example - Deserialization

```text
POST /restore
       |
       v
HTTP Body
       |
       v
pickle.loads()
       |
       v
Object Construction
```

---

# Source-to-Sink Example - YAML

```text
POST /config/import
       |
       v
Uploaded YAML
       |
       v
yaml.load()
       |
       v
Configured Loader
```

The loader and trust boundary determine the security implications.

---

# Source-to-Sink Example - SSTI

```text
GET /preview?template=...
       |
       v
request.args["template"]
       |
       v
render_template_string()
       |
       v
Template Evaluation
```

---

# Source-to-Sink Example - IDOR

```text
GET /invoice/100
       |
       v
invoice_id
       |
       v
Invoice.query.get(invoice_id)
       |
       v
Invoice returned
```

Critical question:

```text
Where is object-level authorisation?
```

---

# Source-to-Sink Example - Mass Assignment

```text
PATCH /account
       |
       v
request.json
       |
       v
for key, value in data.items()
       |
       v
setattr(user, key, value)
```

Review whether the attacker can set:

```text
role
is_admin
tenant_id
verified
balance
```

---

# Source-to-Sink Example - Second-Order SSRF

```text
POST /integration
       |
       v
Webhook URL
       |
       v
Database
       |
       v
Background Job
       |
       v
requests.post()
```

---

# Broad Python Security Search

```bash
rg -n \
'eval\(|exec\(|compile\(|os\.system\(|os\.popen\(|subprocess\.(run|Popen|call|check_call|check_output)\(|shell\s*=\s*True|pickle\.(load|loads)\(|dill\.(load|loads)\(|cloudpickle|joblib\.load|yaml\.(load|unsafe_load|full_load|safe_load)\(|requests\.(get|post|put|patch|delete|request)\(|httpx\.|urlopen\(|\bopen\(|Path\(|cursor\.execute\(|session\.execute\(|render_template_string\(|Template\(|from_string\(|redirect\(|RedirectResponse\(|getattr\(|setattr\(|importlib\.import_module|__import__\(' \
--glob '*.py' \
.
```

This identifies candidates.

It does not confirm vulnerabilities.

---

# Command Execution Search

```bash
rg -n \
'os\.(system|popen)\(|subprocess\.(run|Popen|call|check_call|check_output)\(|shell\s*=\s*True|create_subprocess_(shell|exec)\(' \
--glob '*.py' \
.
```

---

# Dynamic Execution Search

```bash
rg -n \
'\beval\(|\bexec\(|\bcompile\(' \
--glob '*.py' \
.
```

---

# Deserialization Search

```bash
rg -n \
'pickle\.(load|loads)\(|dill\.(load|loads)\(|cloudpickle|joblib\.load|shelve\.' \
--glob '*.py' \
.
```

---

# YAML Search

```bash
rg -n \
'yaml\.(load|safe_load|full_load|unsafe_load)\(' \
--glob '*.py' \
.
```

---

# SQL Search

```bash
rg -n \
'\.execute\(|\.executemany\(|\.executescript\(|exec_driver_sql\(|text\(|raw\(' \
--glob '*.py' \
.
```

---

# SSRF Search

```bash
rg -n \
'requests\.(get|post|put|patch|delete|request)\(|httpx\.|urlopen\(|aiohttp\.ClientSession|urllib3|HTTPConnection|HTTPSConnection' \
--glob '*.py' \
.
```

---

# File Operation Search

```bash
rg -n \
'\bopen\(|Path\(|os\.path\.join\(|shutil\.|zipfile|tarfile|extractall\(|unpack_archive\(' \
--glob '*.py' \
.
```

---

# Template Search

```bash
rg -n \
'render_template_string\(|Template\(|from_string\(|Markup\(|mark_safe\(|\|safe' \
--glob '*.py' \
--glob '*.html' \
.
```

---

# Authentication Search

```bash
rg -n -i \
'authenticate|authentication|login|required|permission|authorize|role|current_user|jwt|oauth|oidc|saml|session' \
--glob '*.py' \
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

# Exclude Virtual Environments

For most manual searches:

```bash
rg \
-g '!venv/**' \
-g '!.venv/**' \
-g '!site-packages/**' \
-g '!node_modules/**' \
'pattern' \
.
```

Review third-party dependencies separately.

---

# Variant Analysis

After confirming a vulnerability, identify its root cause.

Example:

```text
Confirmed SQL Injection
        |
        v
Root Cause:
f-string passed to execute()
        |
        v
Search:
execute(f"...")
        |
        v
Review Similar Locations
```

Search:

```bash
rg -n \
'execute\(f["'\'']' \
--glob '*.py' \
.
```

---

# Command Injection Variant Analysis

If one vulnerable pattern uses:

```python
subprocess.run(
    command,
    shell=True
)
```

search:

```bash
rg -n \
'shell\s*=\s*True' \
--glob '*.py' \
.
```

Then trace each command source.

---

# Deserialization Variant Analysis

After finding one unsafe pickle boundary:

```bash
rg -n \
'pickle\.(load|loads)\(|joblib\.load|dill\.(load|loads)\(|cloudpickle' \
--glob '*.py' \
.
```

---

# SSRF Variant Analysis

Search all outbound request functionality:

```bash
rg -n \
'requests\.|httpx\.|urlopen\(|aiohttp\.ClientSession' \
--glob '*.py' \
.
```

Determine whether the same URL validation logic is reused.

---

# Compare Security Controls

Look for inconsistencies.

Example:

```text
GET /documents/{id}
    -> ownership check

PUT /documents/{id}
    -> ownership check

DELETE /documents/{id}
    -> no ownership check
```

This is often more valuable than searching only for dangerous APIs.

---

# Compare API Versions

Search:

```bash
rg -n \
'/v1/|/v2/|api/v1|api/v2' \
--glob '*.py' \
.
```

Older API versions may have weaker controls.

---

# Compare Sync and Async Paths

Applications may implement:

```text
Synchronous endpoint
Asynchronous worker
Administrative endpoint
Internal API
```

for the same functionality.

Compare their security controls.

---

# Git History

Secrets and removed vulnerable functionality may remain in history.

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

```bash
git log -S 'api_key' --all
```

Inspect:

```bash
git show <commit>
```

Use dedicated secret scanners for larger repositories.

---

# Backup Files

Search:

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

---

# Test Code

Tests can reveal:

```text
Hidden endpoints
Expected roles
Internal API calls
Hard-coded credentials
Authentication bypasses
Business rules
Example payload structures
```

Search:

```bash
find . -type f \( \
-path '*/test/*' \
-o -path '*/tests/*' \
-o -name 'test_*.py' \
-o -name '*_test.py' \
\) -print
```

Do not automatically report test credentials as production credentials.

---

# Configuration Review

Search:

```bash
find . -type f \( \
-name '*.ini' \
-o -name '*.toml' \
-o -name '*.yaml' \
-o -name '*.yml' \
-o -name '*.json' \
-o -name '.env*' \
\) -print
```

Review:

```text
Debug mode
Secrets
Database connections
Trusted hosts
CORS
CSRF
Session configuration
Proxy trust
TLS
Storage paths
External services
Logging
```

---

# Docker Review

Search:

```bash
rg -n \
'^FROM|^USER|^ENV|^EXPOSE|pip install|requirements' \
Dockerfile*
```

Review:

```text
Runtime user
Secrets in ENV
Dependency installation
Base image
Exposed services
File permissions
Development server use
```

---

# Running as Root

Containerised Python services may run as root.

Check:

```bash
rg -n \
'^USER ' \
Dockerfile*
```

No `USER` directive does not automatically prove the deployed container runs as root because orchestration can override it.

Verify deployment configuration.

---

# CI/CD

Search:

```bash
find . -type f \( \
-path './.github/workflows/*' \
-o -name '.gitlab-ci.yml' \
-o -name 'Jenkinsfile' \
-o -name 'azure-pipelines.yml' \
\) -print
```

Review:

```text
Secrets
Untrusted pull-request input
Dependency installation
Artifact handling
Publishing
Deployment
Shell execution
```

---

# Source Code Review Matrix

| Vulnerability | High-Value Python Targets |
|---|---|
| SQL Injection | `execute`, raw SQL, SQLAlchemy `text` |
| NoSQL Injection | MongoDB filters, attacker-controlled dictionaries |
| LDAP Injection | LDAP search filters |
| Command Injection | `os.system`, `subprocess`, shell execution |
| Code Injection | `eval`, `exec` |
| SSTI | Jinja `from_string`, dynamic templates |
| XSS | `Markup`, `mark_safe`, raw HTML responses |
| SSRF | `requests`, `httpx`, `urlopen`, `aiohttp` |
| Path Traversal | `open`, `Path`, `os.path`, `shutil` |
| File Upload | Upload APIs, filenames, storage, extraction |
| XXE | XML parsers and options |
| Deserialization | pickle, dill, cloudpickle, joblib, YAML |
| IDOR / BOLA | ORM lookups using request IDs |
| Mass Assignment | `setattr`, `**data`, generic model updates |
| Open Redirect | `redirect`, `RedirectResponse` |
| Host Header | Request host / forwarded-host use |
| CSRF | Framework CSRF configuration |
| CORS | CORS middleware/configuration |
| Sessions | Session and cookie configuration |
| JWT | JWT decode/validation |
| OAuth/OIDC | Callback and token validation |
| SAML | Assertion/signature validation |
| Password Reset | Token generation and validation |
| MFA | OTP and recovery workflows |
| Secrets | Environment, source, configuration, Git |
| Race Conditions | Check-then-update flows |
| Rate Limiting | Login, OTP, reset, expensive APIs |
| Business Logic | Domain workflows and state changes |
| Dependencies | pip/Poetry/Pipenv/uv dependencies |
| Information Disclosure | Debug, exceptions, logging |
| GraphQL | Resolvers and mutations |
| WebSockets | Message authorisation |
| gRPC | Service methods and interceptors |

---

# Source Code Review Checklist

## Application Discovery

```text
[ ] Python version identified
[ ] Framework identified
[ ] Dependency manager identified
[ ] Application entry point identified
[ ] Routes mapped
[ ] Controllers / handlers identified
[ ] Models identified
[ ] Services identified
[ ] Background workers identified
[ ] Configuration identified
```

## Input Sources

```text
[ ] Query parameters reviewed
[ ] Route parameters reviewed
[ ] Form values reviewed
[ ] JSON bodies reviewed
[ ] Headers reviewed
[ ] Cookies reviewed
[ ] Uploaded files reviewed
[ ] WebSocket input reviewed
[ ] CLI input considered
[ ] Stored attacker input considered
[ ] Message queue input considered
```

## Authentication

```text
[ ] Login flow reviewed
[ ] Authentication middleware reviewed
[ ] Custom decorators reviewed
[ ] Session handling reviewed
[ ] Password hashing reviewed
[ ] JWT reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
```

## Authorisation

```text
[ ] Roles reviewed
[ ] Permissions reviewed
[ ] Ownership reviewed
[ ] Object-level authorisation reviewed
[ ] Tenant isolation reviewed
[ ] Administrative routes reviewed
[ ] API methods compared
[ ] Background tasks reviewed
```

## Injection

```text
[ ] Raw SQL reviewed
[ ] SQL string construction reviewed
[ ] NoSQL queries reviewed
[ ] LDAP filters reviewed
[ ] os.system reviewed
[ ] subprocess reviewed
[ ] shell=True reviewed
[ ] eval reviewed
[ ] exec reviewed
[ ] Dynamic templates reviewed
```

## Server-Side

```text
[ ] requests/httpx reviewed
[ ] URL handling reviewed
[ ] File reads reviewed
[ ] File writes reviewed
[ ] Path construction reviewed
[ ] Uploads reviewed
[ ] Archive extraction reviewed
[ ] XML parsing reviewed
[ ] Pickle reviewed
[ ] YAML reviewed
[ ] Dynamic imports reviewed
```

## Client-Side / HTTP

```text
[ ] Template escaping reviewed
[ ] Markup / mark_safe reviewed
[ ] Redirects reviewed
[ ] Header construction reviewed
[ ] Host handling reviewed
[ ] Proxy trust reviewed
[ ] CORS reviewed
[ ] CSRF reviewed
[ ] Session cookies reviewed
```

## Business Logic

```text
[ ] Prices reviewed
[ ] Balances reviewed
[ ] Discounts reviewed
[ ] Refunds reviewed
[ ] State transitions reviewed
[ ] Role changes reviewed
[ ] Tenant changes reviewed
[ ] Race conditions considered
[ ] Rate limiting reviewed
```

## Secrets / Configuration

```text
[ ] .env files reviewed
[ ] settings/config reviewed
[ ] Hard-coded secrets searched
[ ] Private keys searched
[ ] Debug configuration reviewed
[ ] Logging reviewed
[ ] Error handling reviewed
[ ] Git history reviewed
```

## Dependencies

```text
[ ] requirements files reviewed
[ ] pyproject.toml reviewed
[ ] Lock files reviewed
[ ] pip-audit considered
[ ] OSV-Scanner considered
[ ] Unsupported packages considered
[ ] Direct Git dependencies reviewed
```

## Static Analysis

```text
[ ] ripgrep searches performed
[ ] Semgrep considered
[ ] CodeQL considered
[ ] Bandit considered
[ ] Secret scanner considered
[ ] Findings manually validated
[ ] Variant analysis performed
```

---

# Recommended Review Order

For an unfamiliar Python repository:

```text
pyproject.toml / requirements.txt
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
     Input Validation
            |
            v
 Controllers / Handlers
            |
            v
     Models / Services
            |
            v
     Dangerous Sinks
            |
            v
    Background Workers
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

# High-Value Search Terms

```text
request
args
form
json
files
headers
cookies

execute
executemany
text

os.system
os.popen
subprocess
shell=True

eval
exec
compile

pickle
dill
cloudpickle
joblib
shelve

yaml.load
unsafe_load

requests
httpx
urlopen
aiohttp

open
Path
os.path
shutil
zipfile
tarfile

Template
from_string
render_template_string
Markup
mark_safe

redirect
RedirectResponse

getattr
setattr
globals
locals
import_module

session
jwt
oauth
saml

password
secret
token
api_key

role
permission
owner
tenant

price
amount
balance
refund
status
```

---

# Finding Validation

Before reporting a vulnerability:

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

For each finding document:

```text
Title:

Route / Entry Point:

HTTP Method:

Source File:

Source Line:

Input Source:

Data Flow:

Transformations:

Validation:

Authentication:

Authorisation:

Sink:

Reachability:

Exploitability:

Dynamic Validation:

Impact:

Recommendation:
```

---

# Example Finding - Command Injection

```text
Title:
OS Command Injection in Diagnostic Function

Route:
POST /api/diagnostics

Source:
JSON field "host"

Data Flow:

request.json["host"]
        |
        v
host
        |
        v
f"ping -c 1 {host}"
        |
        v
subprocess.run(..., shell=True)

Security Control:
No effective allowlist or shell-safe argument separation was identified.

Impact:
An authenticated user able to access the functionality may be able to influence the shell command executed by the server.

Recommendation:
Avoid invoking a shell. Pass the executable and arguments separately and validate the host value against the application's expected input format.
```

---

# Example Finding - SSRF

```text
Title:
Server-Side Request Forgery in URL Preview Function

Route:
POST /api/preview

Source:
JSON field "url"

Data Flow:

request.json["url"]
        |
        v
url
        |
        v
requests.get(url)

Security Control:
No effective destination policy was identified.

Impact:
The application may make server-side requests to destinations selected by the user, potentially including internal services depending on network access.

Recommendation:
Prefer server-controlled destinations. Where arbitrary external URLs are required, enforce a strict destination policy and network-level egress controls.
```

---

# Example Finding - Unsafe Pickle Deserialization

```text
Title:
Untrusted Serialized Python Object Deserialization

Route:
POST /api/restore

Source:
HTTP request body

Data Flow:

HTTP Body
    |
    v
pickle.loads()
    |
    v
Python Object Reconstruction

Impact:
Python pickle data can invoke object reconstruction behaviour during deserialization. Processing attacker-controlled pickle data can therefore result in arbitrary behaviour within the application's process.

Recommendation:
Do not use pickle across untrusted boundaries. Use a data-only format such as JSON and validate the resulting structure.
```

---

# Example Finding - IDOR / BOLA

```text
Title:
Missing Object-Level Authorisation on Invoice Endpoint

Route:
GET /api/invoices/{invoice_id}

Source:
Route parameter invoice_id

Data Flow:

invoice_id
    |
    v
Invoice Query
    |
    v
Invoice returned

Authentication:
Required.

Authorisation:
No ownership, tenant or equivalent object-level permission check was identified.

Impact:
An authenticated user may be able to access invoices belonging to another user by modifying the identifier.

Recommendation:
Scope database queries to objects the authenticated principal is authorised to access or perform an equivalent object-level authorisation check.
```

---

# Common Review Mistakes

## Every subprocess Call Is Command Injection

Incorrect:

```text
subprocess
    =
Command Injection
```

Determine:

```text
Attacker control
Shell usage
Argument construction
Executable control
Option handling
```

---

# Every shell=True Is Exploitable

`shell=True` substantially increases review priority, but exploitability still requires attacker influence over the command.

```text
shell=True
+
Fixed constant command
    !=
Automatically command injection
```

---

# Every execute() Is SQL Injection

Incorrect:

```text
execute()
    =
SQL Injection
```

Determine:

```text
How SQL is constructed
Whether parameters are bound
Whether attacker input changes syntax
```

---

# Every requests.get() Is SSRF

Determine:

```text
Who controls the URL?
What destinations are allowed?
Are redirects followed?
What network access exists?
```

---

# Every open() Is Path Traversal

Determine:

```text
Who controls the path?
How is the path constructed?
Is containment enforced?
What operation occurs?
```

---

# Every pickle.load() Is Remotely Exploitable

Determine the trust boundary.

```text
Local application-owned file
    !=
Attacker-controlled upload
```

Nevertheless, pickle should not be used to deserialize untrusted data.

---

# Every yaml.load() Is Unsafe

Review the loader.

```text
yaml.load(..., Loader=SafeLoader)
```

is materially different from unsafe object construction.

---

# Every Template Render Is SSTI

Incorrect:

```text
Template Engine
    =
SSTI
```

The important distinction is:

```text
User Input as Template DATA
```

versus:

```text
User Input as Template SOURCE
```

---

# Every Missing Header Is a Python Vulnerability

Security headers may be configured by infrastructure outside the application.

Verify the actual response.

---

# Every Hard-Coded String Is a Secret

Determine whether the value is:

```text
Real
Sensitive
Active
Production relevant
```

---

# Every Static-Analysis Finding Is Real

Always perform manual validation.

```text
Static Analysis
      |
      v
Candidate
      |
      v
Data Flow
      |
      v
Reachability
      |
      v
Exploitability
      |
      v
Finding
```

---

# Final Python Source Review Model

```text
                      PYTHON APPLICATION
                             |
                             v
                      ROUTE / ENTRY POINT
                             |
                             v
                    ATTACKER-CONTROLLED DATA
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
      HTTP Input          Files            Messages
          |                  |                  |
          +------------------+------------------+
                             |
                             v
                        DATA FLOW
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
      Validation        Authorisation      Business Logic
          |                  |                  |
          +------------------+------------------+
                             |
                             v
                   SECURITY-SENSITIVE SINK
                             |
      +----------------------+----------------------+
      |                      |                      |
      v                      v                      v
 subprocess               Database               Network
      |                      |                      |
      v                      v                      v
 Command Injection          SQLi                   SSRF

    File System           Template              Deserializer
        |                    |                      |
        v                    v                      v
 Path Traversal          XSS / SSTI          Pickle / YAML

                      Dynamic Execution
                             |
                             v
                         eval / exec
```

The fundamental question is:

```text
Can attacker-controlled data reach a security-sensitive Python operation
without an effective security boundary?
```

Determine:

```text
Source
+
Transformations
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

## Python Documentation

```text
https://docs.python.org/3/
```

## Python Security Considerations

```text
https://docs.python.org/3/library/security_warnings.html
```

## subprocess

```text
https://docs.python.org/3/library/subprocess.html
```

## pickle

```text
https://docs.python.org/3/library/pickle.html
```

## secrets

```text
https://docs.python.org/3/library/secrets.html
```

## tempfile

```text
https://docs.python.org/3/library/tempfile.html
```

## pathlib

```text
https://docs.python.org/3/library/pathlib.html
```

## urllib.parse

```text
https://docs.python.org/3/library/urllib.parse.html
```

## XML Security

```text
https://docs.python.org/3/library/xml.html
```

## PyYAML

```text
https://pyyaml.org/wiki/PyYAMLDocumentation
```

## Requests

```text
https://requests.readthedocs.io/
```

## SQLAlchemy

```text
https://docs.sqlalchemy.org/
```

## OWASP Code Review Guide

```text
https://owasp.org/www-project-code-review-guide/
```

## OWASP Cheat Sheet Series

```text
https://cheatsheetseries.owasp.org/
```

## OWASP Web Security Testing Guide

```text
https://owasp.org/www-project-web-security-testing-guide/
```

## OWASP ASVS

```text
https://owasp.org/www-project-application-security-verification-standard/
```

## CWE

```text
https://cwe.mitre.org/
```

## Semgrep

```text
https://semgrep.dev/docs/
```

## CodeQL for Python

```text
https://codeql.github.com/docs/codeql-language-guides/codeql-for-python/
```

## Bandit

```text
https://bandit.readthedocs.io/
```

## pip-audit

```text
https://github.com/pypa/pip-audit
```

## OSV-Scanner

```text
https://github.com/google/osv-scanner
```

## ripgrep

```text
https://github.com/BurntSushi/ripgrep
```

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/dotnet.md
docs/source-code-review/java.md
docs/source-code-review/php.md
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
docs/web/grpc-security.md
docs/web/websockets.md
docs/web/mass-assignment.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
```
