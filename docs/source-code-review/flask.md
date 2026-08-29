# Flask Source Code Review

Flask is a lightweight Python web framework commonly used for web applications, REST APIs, internal services, microservices and administrative interfaces.

Unlike frameworks that provide a large integrated security model, Flask intentionally provides a relatively small core. Security controls are therefore often implemented through:

- Flask itself
- Werkzeug
- Jinja
- Flask extensions
- Application-specific middleware and decorators
- Reverse proxies
- API gateways
- External identity providers

This makes source-code review especially important.

A Flask application may appear simple:

```python
@app.route("/profile")
def profile():
    ...
```

but the actual security model may involve:

```text
Browser
   |
   v
Reverse Proxy
   |
   v
Flask
   |
   +-- Authentication Extension
   |
   +-- CSRF Extension
   |
   +-- ORM
   |
   +-- Jinja
   |
   +-- Background Worker
   |
   +-- External APIs
   |
   v
Application Logic
```

The objective of Flask source-code review is to identify:

```text
Routes
User-controlled input
Authentication boundaries
Authorisation boundaries
Validation
Trust boundaries
Dangerous sinks
Security-sensitive configuration
```

and then trace attacker-controlled data through the application.

The core methodology is:

```text
SOURCE
  |
  v
USER-CONTROLLED INPUT
  |
  v
TRANSFORMATIONS
  |
  +-- parsing
  +-- validation
  +-- decoding
  +-- sanitisation
  +-- business logic
  |
  v
SECURITY CONTROLS
  |
  +-- authentication
  +-- authorisation
  +-- CSRF
  +-- tenant isolation
  |
  v
SINK
  |
  v
SECURITY-SENSITIVE OPERATION
```

Remember:

```text
Dangerous function found
        !=
Confirmed vulnerability
```

Instead:

```text
Candidate
   |
   v
Reachability
   |
   v
Attacker Control
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
    Perform source-code review and dynamic validation only against applications, repositories and environments for which you have explicit authorisation.

---

# Review Strategy

A practical Flask review can follow:

```text
1. Identify Flask and Python versions

2. Identify application entry points

3. Identify application factory

4. Identify configuration

5. Identify installed extensions

6. Map Blueprints

7. Map routes

8. Identify input sources

9. Map authentication

10. Map authorisation

11. Review object-level access

12. Review input validation

13. Review database access

14. Review template rendering

15. Review redirects

16. Review CSRF

17. Review CORS

18. Review file uploads

19. Review filesystem operations

20. Review outbound HTTP requests

21. Review command execution

22. Review serialization

23. Review session security

24. Review proxy trust

25. Review business logic

26. Review background workers

27. Search secrets

28. Review dependencies

29. Run static analysis

30. Perform variant analysis

31. Validate findings dynamically where authorised
```

---

# Identify Flask

Search dependency files:

```bash
rg -n -i \
'flask|werkzeug|jinja|flask-' \
requirements*.txt pyproject.toml Pipfile* poetry.lock uv.lock setup.py setup.cfg 2>/dev/null
```

Typical dependencies may include:

```text
Flask
Flask-SQLAlchemy
Flask-Login
Flask-WTF
Flask-CORS
Flask-Limiter
Flask-JWT-Extended
Flask-RESTful
Flask-SocketIO
```

Do not assume an extension is active merely because it appears in a dependency file.

Trace where it is configured and initialised.

---

# Determine Versions

If the environment is available:

```bash
python3 -c "import flask; print(flask.__version__)"
```

Depending on the installed Flask version, package metadata may be the more appropriate way to inspect the installed version:

```bash
python3 -c "from importlib.metadata import version; print(version('flask'))"
```

List relevant packages:

```bash
python3 -m pip list | grep -Ei \
'flask|werkzeug|jinja|sqlalchemy|wtf|cors|jwt|limiter|socketio'
```

Dependency files:

```bash
rg -n -i \
'flask|werkzeug|jinja|sqlalchemy' \
requirements*.txt pyproject.toml Pipfile* poetry.lock uv.lock 2>/dev/null
```

Version identification matters because security behaviour and supported APIs change.

---

# Application Structure

Common Flask layouts include:

```text
project/
├── app.py
├── config.py
├── requirements.txt
├── templates/
├── static/
└── models.py
```

Larger applications may resemble:

```text
project/
├── run.py
├── config.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── extensions.py
│   ├── auth/
│   │   ├── routes.py
│   │   └── forms.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── admin/
│   │   └── routes.py
│   ├── services/
│   ├── templates/
│   └── static/
└── migrations/
```

High-value files include:

```text
app.py
__init__.py
config.py
routes.py
views.py
models.py
forms.py
schemas.py
services.py
auth.py
permissions.py
decorators.py
extensions.py
tasks.py
```

---

# Find Flask Application Entry Points

Search:

```bash
rg -n \
'Flask\(__name__\)|Flask\(' \
--glob '*.py' \
.
```

Typical:

```python
app = Flask(__name__)
```

---

# Application Factory

Larger Flask projects frequently use:

```python
def create_app():
    app = Flask(__name__)
    ...
    return app
```

Search:

```bash
rg -n \
'def create_app\(' \
--glob '*.py' \
.
```

Follow everything initialised inside the factory:

```text
create_app()
   |
   +-- Configuration
   |
   +-- Database
   |
   +-- LoginManager
   |
   +-- CSRFProtect
   |
   +-- CORS
   |
   +-- Limiter
   |
   +-- Blueprints
```

---

# Configuration

Search:

```bash
rg -n \
'app\.config|from_object|from_envvar|Config|SECRET_KEY|SESSION_|DEBUG|TESTING|SERVER_NAME|TRUSTED_HOSTS|MAX_CONTENT_LENGTH|PREFERRED_URL_SCHEME' \
--glob '*.py' \
.
```

Potential sources include:

```python
app.config.from_object(...)
```

```python
app.config.from_pyfile(...)
```

```python
app.config.from_envvar(...)
```

```python
app.config["SECRET_KEY"] = ...
```

Trace which configuration is actually loaded in production.

---

# Configuration Files

Find:

```bash
find . -type f \( \
-name 'config.py' \
-o -name 'settings.py' \
-o -name '.env' \
-o -name '.flaskenv' \
-o -name '*.cfg' \
\) -print
```

Be careful when handling real secret files.

---

# DEBUG

Search:

```bash
rg -n \
'DEBUG\s*=|app\.debug|debug\s*=\s*True|FLASK_DEBUG' \
--glob '*.py' \
.
```

Candidate:

```python
app.run(debug=True)
```

Development debug functionality must not be assumed safe for hostile production exposure.

However:

```text
debug=True in local development code
    !=
Confirmed production vulnerability
```

Confirm deployment reachability and configuration.

---

# Development Server

Search:

```bash
rg -n \
'app\.run\(' \
--glob '*.py' \
.
```

Review whether the development server is accidentally used in production.

Production deployments commonly use a dedicated WSGI server or another supported deployment architecture.

---

# SECRET_KEY

Search:

```bash
rg -n \
'SECRET_KEY|secret_key' \
--glob '*.py' \
.
```

Candidate:

```python
app.config["SECRET_KEY"] = "development-secret"
```

Determine whether it is:

```text
Example value
Test value
Development value
Production value
```

Flask uses the secret key for security-sensitive signing functionality such as its default session mechanism.

A compromised production key may therefore have serious consequences depending on application design.

---

# Environment Variables

Search:

```bash
rg -n \
'os\.environ|os\.getenv|dotenv|load_dotenv' \
--glob '*.py' \
.
```

Example:

```python
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
```

Environment-variable use is not automatically secure.

Review:

```text
Secret lifecycle
Access permissions
Logging
Container configuration
Deployment manifests
Fallback values
```

---

# Flask Extensions

Search:

```bash
rg -n \
'LoginManager|SQLAlchemy|CSRFProtect|CORS\(|Limiter\(|JWTManager|SocketIO|Migrate|Marshmallow' \
--glob '*.py' \
.
```

Create an extension inventory:

| Extension | Purpose | Security Relevance |
|---|---|---|
| Flask-Login | Authentication/session helpers | High |
| Flask-WTF | Forms/CSRF | High |
| Flask-SQLAlchemy | Database | High |
| Flask-CORS | CORS | High |
| Flask-Limiter | Rate limiting | High |
| Flask-JWT-Extended | JWT | High |
| Flask-SocketIO | WebSockets | High |

---

# Route Discovery

Flask routes commonly use:

```python
@app.route()
```

or:

```python
@blueprint.route()
```

Search:

```bash
rg -n \
'@\w+\.route\(' \
--glob '*.py' \
.
```

Broader:

```bash
rg -n \
'\.route\(' \
--glob '*.py' \
.
```

---

# Route Example

```python
@app.route(
    "/users/<int:user_id>",
    methods=["GET"],
)
def user_detail(user_id):
    ...
```

Map:

```text
GET /users/<user_id>
          |
          v
user_detail(user_id)
```

---

# Route Methods

Search:

```bash
rg -n \
'methods\s*=\s*\[' \
--glob '*.py' \
.
```

Routes without an explicit methods argument normally need to be interpreted according to Flask's route behaviour rather than assumed to accept every method.

---

# Method-Specific Decorators

Modern Flask also supports shortcuts such as:

```python
@app.get("/users")
def users():
    ...
```

```python
@app.post("/users")
def create_user():
    ...
```

Search:

```bash
rg -n \
'@\w+\.(get|post|put|patch|delete)\(' \
--glob '*.py' \
.
```

---

# add_url_rule

Routes may also be registered programmatically.

Search:

```bash
rg -n \
'add_url_rule\(' \
--glob '*.py' \
.
```

Example:

```python
app.add_url_rule(
    "/health",
    view_func=health,
)
```

Do not rely only on decorator searches.

---

# Blueprints

Search:

```bash
rg -n \
'Blueprint\(|register_blueprint\(' \
--glob '*.py' \
.
```

Example:

```python
auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)
```

and:

```python
app.register_blueprint(auth)
```

Route construction:

```text
Blueprint prefix
      +
Route path
      =
Final endpoint
```

---

# Route Inventory

Create a table:

| Method | Route | Function | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/profile` | `profile()` | Login | Self |
| GET | `/users/<id>` | `user()` | Login | ? |
| POST | `/upload` | `upload()` | Login | User |
| POST | `/admin/user/<id>` | `update_user()` | Login | Admin? |

This exposes inconsistent controls quickly.

---

# Runtime Route Enumeration

If authorised source execution is available:

```bash
flask routes
```

This can help identify routes that are difficult to locate through static searches.

Do not assume every route is externally reachable.

---

# Input Sources

Common Flask input sources include:

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
request.get_data()
request.view_args
```

Route parameters are also attacker-controlled.

---

# Input Search

```bash
rg -n \
'request\.(args|form|values|json|files|headers|cookies|data|view_args)|request\.get_json\(|request\.get_data\(' \
--glob '*.py' \
.
```

---

# Query Parameters

```python
search = request.args.get("q")
```

Search:

```bash
rg -n \
'request\.args' \
--glob '*.py' \
.
```

---

# Form Data

```bash
rg -n \
'request\.form' \
--glob '*.py' \
.
```

---

# request.values

Search:

```bash
rg -n \
'request\.values' \
--glob '*.py' \
.
```

`request.values` can combine multiple input locations, which may make trust and parameter-precedence reasoning less obvious.

Review carefully where duplicate parameter names matter.

---

# JSON

Search:

```bash
rg -n \
'request\.json|request\.get_json\(' \
--glob '*.py' \
.
```

Example:

```python
data = request.get_json()
```

Trace fields from `data` individually.

---

# Raw Body

Search:

```bash
rg -n \
'request\.data|request\.get_data\(' \
--glob '*.py' \
.
```

Raw request bodies deserve particular attention when passed to:

```text
XML parsers
Deserializers
Template engines
Signature verification
Custom protocol parsers
```

---

# Headers

Search:

```bash
rg -n \
'request\.headers' \
--glob '*.py' \
.
```

Example:

```python
token = request.headers.get(
    "Authorization"
)
```

Potentially attacker-controlled headers include:

```text
Host
Origin
Referer
User-Agent
X-Forwarded-For
X-Forwarded-Host
X-Forwarded-Proto
Custom application headers
```

Whether forwarded headers are trustworthy depends on proxy configuration.

---

# Cookies

Search:

```bash
rg -n \
'request\.cookies' \
--glob '*.py' \
.
```

Do not treat a cookie as trusted merely because it came from a browser.

---

# Uploaded Files

Search:

```bash
rg -n \
'request\.files' \
--glob '*.py' \
.
```

Example:

```python
file = request.files["file"]
```

Trace:

```text
Filename
Content
MIME type
Storage location
Processing
Serving
```

---

# Route Parameters

Example:

```python
@app.get("/documents/<int:document_id>")
def document(document_id):
    ...
```

`document_id` is attacker-controlled.

Map route variables into downstream queries.

---

# Authentication

Flask itself does not prescribe one single authentication system.

Applications may use:

```text
Flask-Login
JWT
OAuth/OIDC
SAML
API keys
Custom sessions
Reverse-proxy authentication
```

Start with:

```bash
rg -n -i \
'login|logout|authenticate|authentication|current_user|login_required|jwt_required|Authorization|api.?key' \
--glob '*.py' \
.
```

---

# Flask-Login

Search:

```bash
rg -n \
'flask_login|LoginManager|login_user|logout_user|current_user|login_required|user_loader' \
--glob '*.py' \
.
```

---

# login_required

Example:

```python
@app.get("/profile")
@login_required
def profile():
    ...
```

This establishes an authentication requirement.

It does not automatically establish:

```text
Object ownership
Role authorisation
Tenant isolation
Action-level permission
```

---

# Authentication Coverage

Compare:

```python
@app.get("/account")
@login_required
def account():
    ...
```

with:

```python
@app.post("/account/delete")
def delete_account():
    ...
```

A missing decorator on a sensitive route deserves investigation.

---

# user_loader

Search:

```bash
rg -n \
'@.*user_loader|user_loader\(' \
--glob '*.py' \
.
```

Example:

```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

Review:

```text
Identifier handling
Account state
Disabled users
Deleted users
Tenant assumptions
```

---

# Custom Authentication Decorators

Search:

```bash
rg -n \
'def .*required|def .*permission|def .*auth|wraps\(' \
--glob '*.py' \
.
```

Example:

```python
def admin_required(func):
    ...
```

Read the implementation rather than trusting the decorator name.

---

# Authorisation

Search:

```bash
rg -n -i \
'role|permission|authorize|authorise|admin|owner|current_user|tenant|organization|organisation|workspace' \
--glob '*.py' \
.
```

---

# Object-Level Authorisation

Candidate:

```python
@app.get("/documents/<int:document_id>")
@login_required
def document(document_id):
    document = Document.query.get(
        document_id
    )

    return render_template(
        "document.html",
        document=document,
    )
```

Data flow:

```text
document_id
     |
     v
Document.query.get()
     |
     v
Document
     |
     v
Response
```

Question:

```text
Where is the ownership or tenant check?
```

---

# Scoped Object Lookup

A stronger pattern may resemble:

```python
document = Document.query.filter_by(
    id=document_id,
    owner_id=current_user.id,
).first_or_404()
```

For a tenant-based application:

```python
document = Document.query.filter_by(
    id=document_id,
    tenant_id=current_user.tenant_id,
).first_or_404()
```

The correct rule depends on application policy.

---

# Query Object Access

Search:

```bash
rg -n \
'\.query\.(get|filter|filter_by|all|first|one|one_or_none)|session\.(get|execute|query)' \
--glob '*.py' \
.
```

Prioritise attacker-controlled identifiers.

---

# IDOR / BOLA Search Strategy

Search likely object identifiers:

```bash
rg -n -i \
'user_id|account_id|document_id|invoice_id|order_id|tenant_id|organization_id|organisation_id|workspace_id' \
--glob '*.py' \
.
```

Then compare each lookup against:

```text
current_user
tenant
role
permission
ownership
```

Refer to:

```text
docs/web/idor-bola.md
docs/web/authorisation.md
```

---

# Multi-Tenant Applications

Map:

```text
User
 |
 v
Membership
 |
 v
Tenant
 |
 v
Tenant-Scoped Query
 |
 v
Object
```

A dangerous pattern may be:

```python
Invoice.query.get(invoice_id)
```

where the application requires:

```python
Invoice.query.filter_by(
    id=invoice_id,
    tenant_id=current_user.tenant_id,
).first()
```

Do not assume every global lookup is vulnerable.

Determine intended visibility.

---

# Input Validation

Flask applications may use:

```text
WTForms
Marshmallow
Pydantic
Custom validation
JSON Schema
Application-specific validators
```

Search:

```bash
rg -n -i \
'wtforms|marshmallow|pydantic|validate|validator|schema|Form\(' \
--glob '*.py' \
.
```

---

# Flask-WTF

Search:

```bash
rg -n \
'FlaskForm|validate_on_submit|DataRequired|Length|Regexp|Email|FileAllowed' \
--glob '*.py' \
.
```

Example:

```python
class ProfileForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(max=64),
        ],
    )
```

Validation helps establish input constraints.

It does not automatically provide:

```text
Authorisation
Safe SQL construction
Safe command construction
Safe HTML output
```

---

# Marshmallow

Search:

```bash
rg -n \
'Schema|fields\.|@validates|@validates_schema|load\(' \
--glob '*.py' \
.
```

Trace which fields can be supplied by clients.

Pay special attention to:

```text
role
admin
is_admin
owner_id
tenant_id
status
approved
verified
balance
permissions
```

---

# Pydantic

Search:

```bash
rg -n \
'BaseModel|field_validator|model_validator|model_validate' \
--glob '*.py' \
.
```

Again:

```text
Schema validation
    !=
Authorisation
```

---

# SQL Injection

Flask applications frequently use:

```text
SQLAlchemy
Flask-SQLAlchemy
Raw database drivers
```

Normal ORM query construction reduces SQL injection risk when values are bound correctly.

The highest-value review targets are raw SQL and dynamic query construction.

---

# SQLAlchemy Search

```bash
rg -n \
'SQLAlchemy|db\.session|session\.execute|text\(|execute\(|from_statement|\.query\.' \
--glob '*.py' \
.
```

---

# Raw SQL

Candidate:

```python
username = request.args.get("username")

query = (
    "SELECT * FROM users "
    "WHERE username = '"
    + username
    + "'"
)

result = db.session.execute(
    query
)
```

Trace user input into SQL syntax.

---

# f-string SQL

Search:

```bash
rg -n \
'f["'\''].*(SELECT|INSERT|UPDATE|DELETE)|format\(.*(SELECT|INSERT|UPDATE|DELETE)' \
--glob '*.py' \
.
```

Manual review is required because grep cannot determine whether the interpolated values are attacker-controlled.

---

# SQLAlchemy text()

Search:

```bash
rg -n \
'\btext\(' \
--glob '*.py' \
.
```

Candidate:

```python
query = text(
    f"SELECT * FROM users WHERE name = '{name}'"
)
```

Safer parameter binding resembles:

```python
query = text(
    "SELECT * FROM users WHERE name = :name"
)

result = db.session.execute(
    query,
    {"name": name},
)
```

---

# Database Driver Calls

Search:

```bash
rg -n \
'cursor\.execute\(|cursor\.executemany\(|execute\(' \
--glob '*.py' \
.
```

Review parameter handling for:

```text
sqlite3
psycopg
PyMySQL
mysqlclient
other DB-API drivers
```

---

# Dynamic Identifiers

Even parameterised value handling does not automatically make attacker-controlled SQL structure safe.

Example:

```python
sort = request.args.get("sort")
```

If `sort` influences:

```text
Column names
Table names
ORDER BY expressions
Operators
```

use server-controlled mappings or allowlists.

Refer to:

```text
docs/web/sql-injection.md
```

---

# NoSQL Injection

Flask applications may use MongoDB or other NoSQL databases.

Search:

```bash
rg -n -i \
'pymongo|mongoengine|mongodb|find_one|find\(|aggregate\(' \
--glob '*.py' \
.
```

Candidate:

```python
query = request.get_json()

user = users.find_one(query)
```

Potential issue:

```text
Attacker controls query structure
rather than only expected values
```

Review whether operators can be injected.

Refer to:

```text
docs/web/nosql-injection.md
```

---

# LDAP Injection

Search:

```bash
rg -n -i \
'ldap|ldap3|search_filter|filterstr|search\(' \
--glob '*.py' \
.
```

Candidate:

```python
username = request.form["username"]

search_filter = (
    "(uid="
    + username
    + ")"
)
```

Trace attacker-controlled values into LDAP filter syntax.

LDAP escaping must be appropriate for the specific LDAP context.

Refer to:

```text
docs/web/ldap-injection.md
```

---

# Command Injection

Search:

```bash
rg -n \
'os\.(system|popen)\(|subprocess\.(run|Popen|call|check_call|check_output)\(|shell\s*=\s*True' \
--glob '*.py' \
.
```

Candidate:

```python
host = request.form["host"]

subprocess.run(
    f"ping -c 1 {host}",
    shell=True,
)
```

Trace:

```text
request.form["host"]
        |
        v
Command String
        |
        v
Shell
```

---

# Safer Process Invocation

Prefer avoiding shell interpretation where possible.

Example:

```python
subprocess.run(
    [
        "ping",
        "-c",
        "1",
        host,
    ],
    check=True,
)
```

However:

```text
Argument list
    !=
Automatically safe
```

The called executable may interpret attacker-controlled arguments in security-sensitive ways.

Validation and allowlisting may still be required.

Refer to:

```text
docs/web/command-injection.md
```

---

# Dynamic Python Execution

Search:

```bash
rg -n \
'\beval\(|\bexec\(|\bcompile\(' \
--glob '*.py' \
.
```

Candidate:

```python
expression = request.form["expression"]

result = eval(expression)
```

Attacker-controlled input reaching dynamic Python execution is a high-priority review target.

---

# Server-Side Template Injection

Flask uses Jinja templates.

Normal usage:

```python
return render_template(
    "profile.html",
    username=username,
)
```

normally uses a server-controlled template file.

The highest-value SSTI target is runtime template source.

---

# render_template_string

Search:

```bash
rg -n \
'render_template_string\(' \
--glob '*.py' \
.
```

Candidate:

```python
template = request.args.get("template")

return render_template_string(
    template
)
```

Data flow:

```text
request.args
     |
     v
Template Source
     |
     v
Jinja Parser
     |
     v
Template Execution
```

This deserves immediate investigation.

---

# Jinja Environment

Search:

```bash
rg -n \
'Environment\(|from_string\(|Template\(' \
--glob '*.py' \
.
```

Candidate:

```python
template = env.from_string(
    user_input
)
```

Again, determine whether attacker-controlled data becomes template source.

Refer to:

```text
docs/web/ssti.md
```

---

# XSS

Jinja normally autoescapes HTML templates rendered through Flask's standard template integration.

Example:

```html
<p>{{ username }}</p>
```

High-value review targets intentionally bypass escaping.

---

# safe Filter

Search:

```bash
rg -n \
'\|\s*safe\b' \
--glob '*.html' \
--glob '*.jinja' \
--glob '*.jinja2' \
.
```

Candidate:

```html
{{ biography|safe }}
```

Trace where `biography` originates.

---

# Markup

Search:

```bash
rg -n \
'\bMarkup\(' \
--glob '*.py' \
.
```

Candidate:

```python
return Markup(
    request.args.get("html")
)
```

Treat attacker-controlled values marked as safe as high-priority review candidates.

---

# autoescape false

Search:

```bash
rg -n \
'autoescape\s+(false|False)|autoescape=False' \
--glob '*.html' \
--glob '*.jinja' \
--glob '*.jinja2' \
--glob '*.py' \
.
```

---

# HTML Response Construction

Search:

```bash
rg -n \
'Response\(|make_response\(' \
--glob '*.py' \
.
```

Candidate:

```python
name = request.args.get("name")

return Response(
    f"<h1>Hello {name}</h1>",
    mimetype="text/html",
)
```

Trace attacker-controlled content into HTML responses.

---

# JavaScript Context

Candidate:

```html
<script>
    const username = "{{ username }}";
</script>
```

HTML escaping and JavaScript-string safety are different contexts.

Review data inserted into:

```text
JavaScript
HTML attributes
CSS
URLs
Inline event handlers
```

Refer to:

```text
docs/web/xss.md
docs/web/html-injection.md
```

---

# CSRF

Flask core does not automatically add CSRF protection to arbitrary application routes.

Many applications use Flask-WTF:

```python
CSRFProtect(app)
```

Search:

```bash
rg -n \
'CSRFProtect|csrf\.init_app|csrf\.exempt|@csrf\.exempt|WTF_CSRF' \
--glob '*.py' \
.
```

---

# CSRF Exemptions

Search:

```bash
rg -n \
'csrf\.exempt|@.*csrf.*exempt' \
--glob '*.py' \
.
```

Do not report every exemption.

Determine:

```text
Does the endpoint change state?
Does it use cookie-based authentication?
Is another anti-CSRF mechanism present?
Is it a machine-to-machine API?
```

---

# Form CSRF

Flask-WTF forms commonly include CSRF integration.

Search:

```bash
rg -n \
'FlaskForm|hidden_tag\(|csrf_token' \
--glob '*.py' \
--glob '*.html' \
.
```

Refer to:

```text
docs/web/csrf.md
```

---

# CORS

Flask applications often use Flask-CORS.

Search:

```bash
rg -n \
'flask_cors|CORS\(|cross_origin\(' \
--glob '*.py' \
.
```

Candidate:

```python
CORS(
    app,
    origins="*",
)
```

Do not report broad CORS solely from this line.

Determine:

```text
Credentials
Sensitive responses
Authentication mechanism
Origin restrictions
Endpoint-specific configuration
```

---

# credentials

Search:

```bash
rg -n \
'supports_credentials|origins\s*=|allow_headers|expose_headers' \
--glob '*.py' \
.
```

Refer to:

```text
docs/web/cors.md
```

---

# Open Redirect

Flask commonly redirects using:

```python
redirect()
```

Search:

```bash
rg -n \
'\bredirect\(' \
--glob '*.py' \
.
```

Candidate:

```python
next_url = request.args.get("next")

return redirect(next_url)
```

Trace whether external URLs are permitted.

---

# Login next Parameter

Search:

```bash
rg -n \
'request\.(args|values).*next|next_url|redirect_url|return_url|return_to' \
--glob '*.py' \
.
```

A common flow:

```text
/login?next=/dashboard
```

Review destination validation.

---

# URL Parsing

Search:

```bash
rg -n \
'urlparse\(|urlsplit\(' \
--glob '*.py' \
.
```

Validation should correctly account for:

```text
Scheme
Host
Port
Protocol-relative URLs
Encoded values
Parser behaviour
```

Refer to:

```text
docs/web/open-redirect.md
```

---

# SSRF

Search:

```bash
rg -n \
'requests\.(get|post|put|patch|delete|request)\(|httpx\.|urllib\.request|urlopen\(|aiohttp\.ClientSession' \
--glob '*.py' \
.
```

Candidate:

```python
url = request.form["url"]

response = requests.get(
    url
)
```

Trace:

```text
User URL
   |
   v
Validation
   |
   v
HTTP Client
   |
   v
Destination
```

Review:

```text
Scheme
Hostname
Port
DNS resolution
Redirects
IPv4
IPv6
Loopback
Private ranges
Link-local addresses
Cloud metadata
Egress restrictions
```

---

# Stored SSRF

Example:

```text
POST /webhooks
      |
      v
Webhook URL
      |
      v
Database
      |
      v
Celery Task
      |
      v
requests.post()
```

This is why interprocedural and second-order tracing matters.

Refer to:

```text
docs/web/ssrf.md
```

---

# Path Traversal

Search:

```bash
rg -n \
'\bopen\(|Path\(|os\.path\.join\(|send_file\(|send_from_directory\(' \
--glob '*.py' \
.
```

Candidate:

```python
filename = request.args.get("file")

path = os.path.join(
    "/srv/files",
    filename,
)

return send_file(path)
```

Do not assume `os.path.join()` enforces containment.

Trace the final resolved path.

---

# send_file

Search:

```bash
rg -n \
'send_file\(' \
--glob '*.py' \
.
```

Review whether the path is:

```text
Server-controlled
Mapped from an object ID
Directly attacker-controlled
Canonicalised
Restricted to an expected directory
```

---

# send_from_directory

Search:

```bash
rg -n \
'send_from_directory\(' \
--glob '*.py' \
.
```

`send_from_directory()` is intended for serving files from a specified directory and uses Werkzeug's safe path handling, but application-level authorisation and correct directory selection still matter.

Do not automatically flag it as path traversal.

Refer to:

```text
docs/web/path-traversal.md
```

---

# File Upload

Search:

```bash
rg -n \
'request\.files|save\(|secure_filename\(|send_file\(|send_from_directory\(' \
--glob '*.py' \
.
```

Example:

```python
file = request.files["file"]

file.save(
    os.path.join(
        upload_dir,
        file.filename,
    )
)
```

Review whether the original filename is trusted.

---

# secure_filename

Search:

```bash
rg -n \
'secure_filename\(' \
--glob '*.py' \
.
```

Example:

```python
filename = secure_filename(
    file.filename
)
```

This is useful filename normalisation, but:

```text
secure_filename()
    !=
Complete upload security
```

Still review:

```text
File content
Extension
MIME type
Storage
Permissions
Overwrite behaviour
Serving
Downstream processing
Authorisation
```

---

# Upload Size

Search:

```bash
rg -n \
'MAX_CONTENT_LENGTH' \
--glob '*.py' \
.
```

Example:

```python
app.config[
    "MAX_CONTENT_LENGTH"
] = 16 * 1024 * 1024
```

Request-size restrictions can help reduce resource abuse.

Infrastructure limits may also exist.

---

# Archive Extraction

Search:

```bash
rg -n \
'zipfile|ZipFile|tarfile|TarFile|extractall\(|unpack_archive\(' \
--glob '*.py' \
.
```

Review uploaded archive extraction for:

```text
Traversal
Overwrite
Symlinks
Resource exhaustion
Unexpected file types
```

Refer to:

```text
docs/web/file-upload.md
```

---

# Insecure Deserialization

Search:

```bash
rg -n \
'pickle\.(load|loads)\(|dill\.(load|loads)\(|cloudpickle|joblib\.load|yaml\.(load|unsafe_load)\(' \
--glob '*.py' \
.
```

Candidate:

```python
data = pickle.loads(
    request.data
)
```

Untrusted pickle data must not be deserialized.

---

# YAML

Search:

```bash
rg -n \
'yaml\.(load|unsafe_load|safe_load)\(' \
--glob '*.py' \
.
```

Review which loader is used and whether the input is trusted.

Do not flag `safe_load()` merely because YAML is involved.

Refer to:

```text
docs/web/deserialization.md
```

---

# XML / XXE

Search:

```bash
rg -n \
'xml\.etree|ElementTree|lxml|etree|xml\.dom|minidom|sax|XMLParser' \
--glob '*.py' \
.
```

Determine:

```text
Parser implementation
Parser configuration
DTD handling
Entity resolution
Network access
Input trust
```

Do not report XML parsing itself as XXE.

Refer to:

```text
docs/web/xxe.md
```

---

# Session Management

Flask's default session mechanism stores session data in a signed cookie.

This means an important distinction is:

```text
Signed
    !=
Secret
```

Do not place sensitive plaintext data in client-visible session contents merely because integrity protection is present.

---

# Session Usage

Search:

```bash
rg -n \
'\bsession\[|session\.get\(|session\.pop\(|session\.clear\(' \
--glob '*.py' \
.
```

Example:

```python
session["user_id"] = user.id
```

Review:

```text
What is stored?
What security decisions rely on it?
How is it invalidated?
What happens after password changes?
What happens after privilege changes?
```

---

# Session Cookie Configuration

Search:

```bash
rg -n \
'SESSION_COOKIE_(SECURE|HTTPONLY|SAMESITE|DOMAIN|PATH|NAME)|PERMANENT_SESSION_LIFETIME' \
--glob '*.py' \
.
```

High-value settings include:

```text
SESSION_COOKIE_SECURE
SESSION_COOKIE_HTTPONLY
SESSION_COOKIE_SAMESITE
SESSION_COOKIE_DOMAIN
PERMANENT_SESSION_LIFETIME
```

Confirm effective deployment configuration.

---

# Session Fixation

Review login flows.

Search:

```bash
rg -n \
'login_user\(|session\.clear\(|session\[' \
--glob '*.py' \
.
```

Determine whether session state is appropriately replaced or cleared across authentication transitions.

---

# Remember-Me Functionality

Flask-Login can support persistent login functionality.

Search:

```bash
rg -n \
'remember\s*=|REMEMBER_COOKIE_|login_user\(' \
--glob '*.py' \
.
```

Review:

```text
Lifetime
Secure
HttpOnly
SameSite
Revocation expectations
```

---

# Host Header Security

Search:

```bash
rg -n \
'request\.host|request\.host_url|request\.url_root|request\.url|SERVER_NAME|TRUSTED_HOSTS' \
--glob '*.py' \
.
```

High-value contexts include:

```text
Password reset
Email verification
Account activation
OAuth callbacks
Absolute URL generation
Security-sensitive redirects
```

---

# url_for with _external

Search:

```bash
rg -n \
'url_for\(.*_external\s*=\s*True' \
--glob '*.py' \
.
```

Example:

```python
reset_url = url_for(
    "auth.reset",
    token=token,
    _external=True,
)
```

Determine which host and scheme influence the generated URL.

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# ProxyFix

Flask deployments behind reverse proxies may use Werkzeug's `ProxyFix`.

Search:

```bash
rg -n \
'ProxyFix|x_for|x_proto|x_host|x_port|x_prefix' \
--glob '*.py' \
.
```

Example:

```python
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
)
```

The security of this configuration depends on the real proxy topology.

The application must only trust the number of proxy hops that are actually controlled.

Incorrect proxy trust can cause attacker-supplied forwarded headers to be interpreted as trusted request metadata.

---

# Forwarded Header Usage

Search:

```bash
rg -n \
'X-Forwarded-For|X-Forwarded-Host|X-Forwarded-Proto|Forwarded' \
--glob '*.py' \
.
```

Map:

```text
Internet
   |
   v
Trusted Proxy
   |
   v
Forwarded Header
   |
   v
ProxyFix
   |
   v
Flask Request Metadata
```

---

# Password Reset

Search:

```bash
rg -n -i \
'forgot.?password|password.?reset|reset.?password|reset_token|generate.*token|verify.*token' \
--glob '*.py' \
.
```

Review:

```text
Token generation
Entropy
Expiration
Single use
User binding
Enumeration
Rate limiting
Host generation
Session invalidation
```

---

# Token Generation

Search:

```bash
rg -n \
'itsdangerous|URLSafeTimedSerializer|Serializer\(' \
--glob '*.py' \
.
```

Flask applications commonly use ItsDangerous for signed tokens.

Review:

```text
Secret key
Salt/purpose separation
Expiration
What claims are signed
How verified data is used
```

A correctly signed token does not automatically prove that the resulting action is authorised.

Refer to:

```text
docs/web/password-reset.md
```

---

# Password Hashing

Werkzeug provides password hashing helpers.

Search:

```bash
rg -n \
'generate_password_hash|check_password_hash|password_hash|bcrypt|argon2' \
--glob '*.py' \
.
```

Candidate safe-style flow:

```python
password_hash = generate_password_hash(
    password
)
```

Review custom cryptographic implementations carefully.

---

# Dangerous Password Storage

Search:

```bash
rg -n -i \
'password\s*=|user\.password|password_hash' \
--glob '*.py' \
.
```

Determine whether plaintext or reversible password storage occurs.

Do not infer this from a variable named `password`.

---

# MFA

Search:

```bash
rg -n -i \
'totp|hotp|otp|mfa|2fa|two.?factor|recovery.?code|backup.?code|pyotp' \
--glob '*.py' \
.
```

Review:

```text
Enrollment
Secret generation
Verification
Replay prevention
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

# JWT

Common Flask JWT packages include:

```text
Flask-JWT-Extended
PyJWT
Authlib
python-jose
```

Search:

```bash
rg -n -i \
'jwt|JWTManager|jwt_required|create_access_token|decode_token|encode\(|decode\(' \
--glob '*.py' \
.
```

---

# Flask-JWT-Extended

Search:

```bash
rg -n \
'JWTManager|@jwt_required|create_access_token|get_jwt|get_jwt_identity|JWT_' \
--glob '*.py' \
.
```

Review:

```text
Token location
Signing algorithm
Secret/key management
Issuer
Audience
Expiration
Revocation
Refresh tokens
CSRF when cookies are used
Privilege claims
```

---

# JWT Claims and Authorisation

Candidate:

```python
claims = get_jwt()

if claims["role"] == "admin":
    ...
```

Review:

```text
Where was role assigned?
Can stale tokens retain privileges?
Is server-side authorisation also performed?
How are tokens revoked?
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
'oauth|openid|oidc|authlib|client_id|client_secret|redirect_uri|state|nonce|code_verifier|token_endpoint' \
--glob '*.py' \
.
```

Review:

```text
State
Nonce
PKCE
Issuer
Audience
Redirect URI
Token validation
Account linking
Email trust
Session creation
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
'saml|python3-saml|xmlsec|onelogin|pysaml' \
--glob '*.py' \
.
```

Review:

```text
Signature validation
Issuer
Audience
Destination
Recipient
Replay protection
Attribute mapping
Account linking
```

Refer to:

```text
docs/web/saml.md
```

---

# API Keys

Search:

```bash
rg -n -i \
'api.?key|x-api-key|authorization|bearer' \
--glob '*.py' \
.
```

Review:

```text
Storage
Comparison
Rotation
Logging
Scope
Rate limiting
Revocation
```

---

# Rate Limiting

Flask applications may use Flask-Limiter or infrastructure-level controls.

Search:

```bash
rg -n \
'Limiter\(|@.*limit\(|RATELIMIT|rate.?limit' \
--glob '*.py' \
.
```

---

# Sensitive Rate-Limit Targets

Prioritise:

```text
Login
Password reset
MFA verification
Registration
Email verification
OTP
API authentication
Expensive searches
Exports
```

Do not conclude that rate limiting is absent merely because no Flask code implements it.

It may exist at:

```text
Nginx
Cloud proxy
WAF
API gateway
Load balancer
```

Refer to:

```text
docs/web/rate-limiting.md
```

---

# Business Logic

Search:

```bash
rg -n -i \
'price|amount|balance|discount|coupon|refund|credit|quantity|inventory|approved|verified|status|role|permission' \
--glob '*.py' \
.
```

Review:

```text
Payments
Refunds
Credits
Coupons
Inventory
Approval workflows
State transitions
Verification
Role changes
Tenant changes
```

---

# Trust Client-Supplied Prices

Candidate:

```python
price = request.form["price"]

order = Order(
    product_id=product_id,
    price=price,
)
```

Question:

```text
Should the server derive the price from trusted product data?
```

This is business-logic analysis rather than generic input validation.

---

# Mass Assignment

Flask applications frequently convert request dictionaries directly into model constructors or updates.

Search:

```bash
rg -n \
'\*\*request\.(json|form)|\*\*data|setattr\(|\.update\(' \
--glob '*.py' \
.
```

Candidate:

```python
data = request.get_json()

user = User(
    **data
)
```

Review whether the client can control:

```text
is_admin
role
permissions
owner_id
tenant_id
verified
status
balance
```

---

# Generic setattr

Candidate:

```python
for key, value in data.items():
    setattr(
        user,
        key,
        value,
    )
```

This deserves careful field-level analysis.

Refer to:

```text
docs/web/mass-assignment.md
```

---

# Race Conditions

Search:

```bash
rg -n \
'with_for_update|begin\(|commit\(|rollback\(|transaction|redis.*lock|Lock\(' \
--glob '*.py' \
.
```

High-value workflows:

```text
Balances
Credits
Coupons
Inventory
One-time tokens
Approvals
Password resets
Invitations
```

---

# Race Example

```text
Request A              Request B

Read balance=100       Read balance=100
      |                      |
Check >= 80            Check >= 80
      |                      |
Subtract 80            Subtract 80
      |                      |
Commit                 Commit
```

Review database transaction isolation and application-level locking.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Background Workers

Flask applications commonly use:

```text
Celery
RQ
Dramatiq
Custom queues
```

Search:

```bash
rg -n -i \
'celery|shared_task|@.*task|\.delay\(|apply_async\(|rq\.|enqueue\(|dramatiq' \
--glob '*.py' \
.
```

---

# Second-Order Flow

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
Dangerous Sink
```

Example:

```text
POST /integrations
       |
       v
Webhook URL
       |
       v
Database
       |
       v
Celery
       |
       v
requests.post()
```

---

# Signals / Hooks

Flask extensions and SQLAlchemy may introduce event-driven behaviour.

Search:

```bash
rg -n \
'@event\.listens_for|event\.listen|before_request|after_request|teardown_request|before_app_request' \
--glob '*.py' \
.
```

---

# before_request

Search:

```bash
rg -n \
'@.*before_request|before_request\(' \
--glob '*.py' \
.
```

Security controls may be applied globally here.

Do not assume a route lacks authentication merely because no decorator is visible.

---

# after_request

Search:

```bash
rg -n \
'@.*after_request|after_request\(' \
--glob '*.py' \
.
```

Security headers may be added here.

---

# Error Handlers

Search:

```bash
rg -n \
'@.*errorhandler|register_error_handler' \
--glob '*.py' \
.
```

Review whether exceptions expose:

```text
Stack traces
Internal paths
Database errors
Secrets
Tokens
User data
```

---

# Information Disclosure

Search:

```bash
rg -n \
'traceback|print_exc|logger\.exception|debug\s*=\s*True|DEBUG\s*=|str\(.*exception|repr\(.*exception' \
--glob '*.py' \
.
```

---

# Logging

Search:

```bash
rg -n \
'logger\.(debug|info|warning|error|critical|exception)\(|logging\.(debug|info|warning|error|critical|exception)\(' \
--glob '*.py' \
.
```

Review for:

```text
Passwords
Authorization headers
JWTs
Session cookies
API keys
Reset tokens
MFA codes
Sensitive request bodies
```

---

# HTTP Security Headers

Flask applications may configure headers using:

```text
after_request
Flask-Talisman
Reverse proxy
CDN
WAF
```

Search:

```bash
rg -n -i \
'Content-Security-Policy|X-Frame-Options|Strict-Transport-Security|X-Content-Type-Options|Referrer-Policy|Permissions-Policy|Talisman' \
--glob '*.py' \
.
```

Do not infer missing deployed headers from application source alone.

Validate actual responses.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# Clickjacking

Search:

```bash
rg -n -i \
'X-Frame-Options|frame-ancestors|Content-Security-Policy' \
--glob '*.py' \
.
```

Again, reverse proxies may supply these headers.

Refer to:

```text
docs/web/clickjacking.md
```

---

# Cache Security

Search:

```bash
rg -n -i \
'cache|Cache\(|cached\(|memoize\(|Cache-Control|Vary' \
--glob '*.py' \
.
```

Flask applications may use Flask-Caching.

Review cache separation for:

```text
User
Role
Tenant
Cookies
Authorization headers
Host
Query parameters
Language
```

---

# Cache Key Construction

Candidate:

```python
@cache.cached(
    timeout=300
)
@login_required
def account():
    ...
```

Determine whether the cache varies appropriately for authenticated users.

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# GraphQL

Common Python GraphQL frameworks include:

```text
Graphene
Ariadne
Strawberry
```

Search:

```bash
rg -n -i \
'graphene|ariadne|strawberry|graphql|resolver|mutation' \
--glob '*.py' \
.
```

Review:

```text
Resolvers
Mutations
Authentication
Object-level authorisation
Field-level access
Depth
Complexity
Batching
Introspection
```

Refer to:

```text
docs/web/graphql.md
```

---

# WebSockets

Flask applications may use Flask-SocketIO.

Search:

```bash
rg -n \
'SocketIO|socketio\.on|@.*\.on\(' \
--glob '*.py' \
.
```

Example:

```python
@socketio.on("join")
def join(data):
    ...
```

Review:

```text
Connection authentication
Event authorisation
Room access
Object access
Origin handling
State-changing events
```

Refer to:

```text
docs/web/websockets.md
```

---

# gRPC

A Flask application may act as a gRPC client or coexist with gRPC services.

Search:

```bash
rg -n -i \
'grpc|Stub\(|Servicer' \
--glob '*.py' \
.
```

Map trust boundaries:

```text
HTTP Request
     |
     v
Flask
     |
     v
gRPC Client
     |
     v
Internal Service
```

Do not automatically trust internal RPC traffic.

Refer to:

```text
docs/web/grpc-security.md
```

---

# Secrets Exposure

Search:

```bash
rg -n -i \
'secret|password|passwd|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|token|database_url|redis_url' \
.
```

---

# Common Flask Secret Locations

Review:

```text
.env
.flaskenv
config.py
settings.py
docker-compose.yml
Dockerfile
Kubernetes manifests
CI/CD configuration
Shell scripts
Deployment files
```

---

# Git History

Current source may no longer contain a secret while repository history does.

Useful commands:

```bash
git log --all --oneline
```

Search history:

```bash
git log -S 'SECRET_KEY' --all
```

Inspect a commit:

```bash
git show <commit>
```

Use secret-scanning tools where authorised.

Refer to:

```text
docs/web/secrets-exposure.md
```

---

# Dependency Security

Find dependency files:

```bash
find . -maxdepth 3 -type f \( \
-name 'requirements*.txt' \
-o -name 'pyproject.toml' \
-o -name 'Pipfile*' \
-o -name 'poetry.lock' \
-o -name 'uv.lock' \
\) -print
```

Review:

```text
Flask
Werkzeug
Jinja
SQLAlchemy
Authentication packages
JWT packages
CORS packages
XML libraries
Image libraries
Serialization libraries
Cloud SDKs
```

---

# pip-audit

```bash
pip-audit
```

Against requirements:

```bash
pip-audit \
-r requirements.txt
```

---

# OSV-Scanner

```bash
osv-scanner scan source -r .
```

A dependency match means:

```text
Potentially vulnerable version
```

not automatically:

```text
Exploitable application
```

Determine:

```text
Affected version
Affected functionality
Reachability
Attacker control
Deployment
```

Refer to:

```text
docs/web/dependency-security.md
```

---

# Static Analysis

Useful tools include:

```text
Semgrep
CodeQL
Bandit
pip-audit
OSV-Scanner
Gitleaks
TruffleHog
```

---

# Semgrep

Run:

```bash
semgrep scan \
--config auto \
.
```

Semgrep can help identify:

```text
Command execution
Raw SQL
Unsafe deserialization
SSTI candidates
XSS candidates
Hard-coded secrets
Unsafe HTTP requests
```

Manual validation remains required.

---

# Bandit

Run:

```bash
bandit -r .
```

Exclude tests where appropriate:

```bash
bandit \
-r . \
-x ./tests
```

Bandit is useful for Python security patterns but cannot reliably determine:

```text
Object authorisation
Tenant isolation
Business logic
Workflow vulnerabilities
```

---

# CodeQL

CodeQL can assist with:

```text
Data flow
Taint tracking
Interprocedural analysis
Variant analysis
```

Conceptually:

```text
request.args
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
requests.get()
```

---

# Broad Flask Search

```bash
rg -n \
'@\w+\.route\(|@\w+\.(get|post|put|patch|delete)\(|add_url_rule\(|request\.(args|form|values|json|files|headers|cookies|data|view_args)|request\.get_json\(|login_required|current_user|jwt_required|\.query\.(get|filter|filter_by)|session\.execute\(|cursor\.execute\(|render_template_string\(|\|\s*safe\b|Markup\(|csrf\.exempt|redirect\(|requests\.(get|post|put|patch|delete|request)\(|httpx\.|urlopen\(|send_file\(|send_from_directory\(|pickle\.(load|loads)\(|yaml\.(load|unsafe_load)\(|os\.(system|popen)\(|subprocess\.|shell\s*=\s*True|\beval\(|\bexec\(' \
--glob '*.py' \
--glob '*.html' \
--glob '*.jinja' \
.
```

This discovers candidates.

It does not prove vulnerabilities.

---

# Route Search

```bash
rg -n \
'@\w+\.route\(|@\w+\.(get|post|put|patch|delete)\(|add_url_rule\(' \
--glob '*.py' \
.
```

---

# Input Search

```bash
rg -n \
'request\.(args|form|values|json|files|headers|cookies|data|view_args)|request\.get_json\(|request\.get_data\(' \
--glob '*.py' \
.
```

---

# Authentication Search

```bash
rg -n \
'login_required|current_user|LoginManager|login_user|logout_user|jwt_required|Authorization' \
--glob '*.py' \
.
```

---

# Authorisation Search

```bash
rg -n -i \
'role|permission|owner|tenant|organization|organisation|workspace|is_admin|current_user' \
--glob '*.py' \
.
```

---

# SQL Search

```bash
rg -n \
'session\.execute\(|db\.session\.execute\(|cursor\.execute\(|\btext\(' \
--glob '*.py' \
.
```

---

# Command Search

```bash
rg -n \
'os\.(system|popen)\(|subprocess\.(run|Popen|call|check_call|check_output)\(|shell\s*=\s*True' \
--glob '*.py' \
.
```

---

# SSTI Search

```bash
rg -n \
'render_template_string\(|Environment\(|from_string\(|Template\(' \
--glob '*.py' \
.
```

---

# XSS Search

```bash
rg -n \
'\|\s*safe\b|\bMarkup\(|autoescape\s+(false|False)|Response\(|make_response\(' \
--glob '*.py' \
--glob '*.html' \
--glob '*.jinja' \
.
```

---

# CSRF Search

```bash
rg -n \
'CSRFProtect|csrf\.exempt|WTF_CSRF|FlaskForm|csrf_token' \
--glob '*.py' \
--glob '*.html' \
.
```

---

# SSRF Search

```bash
rg -n \
'requests\.(get|post|put|patch|delete|request)\(|httpx\.|urlopen\(|aiohttp\.ClientSession' \
--glob '*.py' \
.
```

---

# File Search

```bash
rg -n \
'request\.files|secure_filename\(|send_file\(|send_from_directory\(|\bopen\(|Path\(|os\.path\.join\(|extractall\(' \
--glob '*.py' \
.
```

---

# Deserialization Search

```bash
rg -n \
'pickle\.(load|loads)\(|dill\.(load|loads)\(|cloudpickle|joblib\.load|yaml\.(load|unsafe_load)\(' \
--glob '*.py' \
.
```

---

# Session Search

```bash
rg -n \
'SECRET_KEY|SESSION_COOKIE_|PERMANENT_SESSION_LIFETIME|\bsession\[|session\.get\(' \
--glob '*.py' \
.
```

---

# Proxy Search

```bash
rg -n \
'ProxyFix|X-Forwarded-For|X-Forwarded-Host|X-Forwarded-Proto|request\.host|request\.host_url|url_for\(.*_external' \
--glob '*.py' \
.
```

---

# Reverse Sink Analysis

For large Flask applications, begin from dangerous sinks.

Example:

```text
subprocess.run()
      ^
      |
Service Function
      ^
      |
Blueprint Route
      ^
      |
request.form
```

High-value sinks include:

```text
db.session.execute()
cursor.execute()

os.system()
subprocess.*

eval()
exec()

pickle.loads()
yaml.load()

render_template_string()
Jinja from_string()

requests.*
httpx.*

open()
send_file()

Markup()
safe

redirect()
```

---

# Forward Source Analysis

Begin from:

```text
request.args
request.form
request.values
request.json
request.get_json()
request.files
request.headers
request.cookies
request.data
route parameters
```

Trace forward:

```text
SOURCE
   |
   v
ROUTE
   |
   v
VALIDATION
   |
   v
SERVICE
   |
   v
MODEL
   |
   v
BACKGROUND JOB
   |
   v
SINK
```

---

# Source-to-Sink Example - IDOR

```text
GET /invoice/123
       |
       v
invoice_id
       |
       v
Invoice.query.get()
       |
       v
Invoice
       |
       v
render_template()
```

Question:

```text
Where is object-level authorisation?
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
f-string SQL
       |
       v
db.session.execute()
```

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
Jinja
```

---

# Source-to-Sink Example - Stored XSS

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
{{ biography|safe }}
       |
       v
Browser
```

---

# Source-to-Sink Example - SSRF

```text
POST /preview
       |
       v
request.form["url"]
       |
       v
requests.get()
       |
       v
Network
```

---

# Source-to-Sink Example - Path Traversal

```text
GET /download?file=...
       |
       v
request.args["file"]
       |
       v
os.path.join()
       |
       v
send_file()
```

---

# Source-to-Sink Example - Command Injection

```text
POST /diagnostics
       |
       v
request.form["host"]
       |
       v
Command String
       |
       v
subprocess.run(shell=True)
```

---

# Source-to-Sink Example - Mass Assignment

```text
PATCH /api/user
       |
       v
request.get_json()
       |
       v
**data
       |
       v
User(...)
```

Review writable fields.

---

# Source-to-Sink Example - Stored SSRF

```text
POST /webhooks
       |
       v
Webhook URL
       |
       v
Database
       |
       v
Celery
       |
       v
requests.post()
```

---

# Variant Analysis

Once one vulnerability is confirmed, search for the same root cause elsewhere.

---

# IDOR Variants

```bash
rg -n \
'\.query\.get\(|\.query\.filter_by\(|session\.get\(' \
--glob '*.py' \
.
```

Review each object lookup against:

```text
current_user
owner
tenant
role
permission
```

---

# SQL Injection Variants

```bash
rg -n \
'db\.session\.execute\(|session\.execute\(|cursor\.execute\(|\btext\(' \
--glob '*.py' \
.
```

---

# SSTI Variants

```bash
rg -n \
'render_template_string\(|from_string\(|Template\(' \
--glob '*.py' \
.
```

---

# XSS Variants

```bash
rg -n \
'\|\s*safe\b|\bMarkup\(|autoescape\s+(false|False)' \
--glob '*.py' \
--glob '*.html' \
--glob '*.jinja' \
.
```

---

# SSRF Variants

```bash
rg -n \
'requests\.|httpx\.|urlopen\(' \
--glob '*.py' \
.
```

---

# CSRF Variants

```bash
rg -n \
'csrf\.exempt|WTF_CSRF_ENABLED\s*=\s*False' \
--glob '*.py' \
.
```

---

# Compare Similar Routes

Suppose:

```text
GET /documents/<id>
    -> login_required
    -> ownership check

POST /documents/<id>/edit
    -> login_required
    -> ownership check

POST /documents/<id>/delete
    -> login_required
    -> no ownership check
```

The inconsistent route is immediately interesting.

---

# Compare Interfaces

The same functionality may exist through:

```text
HTML route
REST API
GraphQL
WebSocket
Admin route
Background task
```

Map them together:

```text
User Account
    |
    +-- /account
    |
    +-- /api/account
    |
    +-- GraphQL
    |
    +-- SocketIO
```

Security controls should be compared across all interfaces.

---

# Flask Security Review Matrix

| Vulnerability | High-Value Flask Targets |
|---|---|
| Authentication | Flask-Login, JWT, custom decorators |
| Authorisation | role checks, ownership, tenant filters |
| IDOR / BOLA | ORM lookups from route IDs |
| SQL Injection | raw SQL, `text()`, `execute()` |
| NoSQL Injection | Mongo query objects |
| LDAP Injection | dynamic LDAP filters |
| Command Injection | `subprocess`, `os.system` |
| SSTI | `render_template_string`, `from_string` |
| XSS | `safe`, `Markup`, direct HTML responses |
| CSRF | Flask-WTF, CSRF exemptions |
| CORS | Flask-CORS |
| Open Redirect | `redirect()` |
| SSRF | `requests`, `httpx`, `urlopen` |
| Path Traversal | `open`, `send_file`, path construction |
| File Upload | `request.files`, `.save()` |
| XXE | XML parser configuration |
| Deserialization | pickle, YAML, joblib |
| Mass Assignment | `**data`, `setattr()` |
| Sessions | secret key, cookie configuration |
| Host Header | request host, external URL generation |
| Proxy Trust | `ProxyFix` |
| Password Reset | custom token flows |
| MFA | OTP/recovery logic |
| JWT | Flask-JWT-Extended, PyJWT |
| OAuth/OIDC | callbacks and token validation |
| SAML | assertion processing |
| Information Disclosure | debug, errors, logs |
| Race Conditions | transactions and locks |
| Rate Limiting | Flask-Limiter/infrastructure |
| Business Logic | services/workflows |
| GraphQL | resolvers/mutations |
| WebSockets | Flask-SocketIO |
| Secrets | config/environment/history |
| Dependencies | Python dependency files |

---

# Flask Review Checklist

## Project Discovery

```text
[ ] Flask version identified
[ ] Python version identified
[ ] Entry point identified
[ ] Application factory identified
[ ] Configuration mapped
[ ] Extensions identified
[ ] Blueprints mapped
[ ] Routes mapped
[ ] Models mapped
[ ] Services mapped
[ ] Background jobs mapped
```

## Configuration

```text
[ ] DEBUG reviewed
[ ] SECRET_KEY reviewed
[ ] Production config identified
[ ] Environment loading reviewed
[ ] Session settings reviewed
[ ] Host handling reviewed
[ ] ProxyFix reviewed
[ ] Request-size limits reviewed
```

## Authentication

```text
[ ] Flask-Login reviewed
[ ] login_required coverage reviewed
[ ] Custom auth decorators reviewed
[ ] JWT authentication reviewed
[ ] API key authentication reviewed
[ ] Password hashing reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
```

## Authorisation

```text
[ ] Object ownership reviewed
[ ] Tenant isolation reviewed
[ ] Role checks reviewed
[ ] Admin checks reviewed
[ ] CRUD controls compared
[ ] API controls compared
[ ] Background operations reviewed
```

## Input Validation

```text
[ ] request.args reviewed
[ ] request.form reviewed
[ ] request.values reviewed
[ ] request.json reviewed
[ ] request.files reviewed
[ ] WTForms reviewed
[ ] Marshmallow reviewed
[ ] Pydantic reviewed
[ ] Custom validators reviewed
```

## Injection

```text
[ ] Raw SQL reviewed
[ ] SQLAlchemy text() reviewed
[ ] NoSQL query construction reviewed
[ ] LDAP filters reviewed
[ ] subprocess reviewed
[ ] shell=True reviewed
[ ] eval/exec reviewed
[ ] Dynamic templates reviewed
```

## Client-Side

```text
[ ] Jinja safe filter reviewed
[ ] Markup reviewed
[ ] Autoescape changes reviewed
[ ] JavaScript template contexts reviewed
[ ] Redirects reviewed
[ ] CSRF reviewed
[ ] CORS reviewed
[ ] Security headers reviewed
```

## Server-Side

```text
[ ] Outbound HTTP requests reviewed
[ ] File reads reviewed
[ ] File writes reviewed
[ ] send_file reviewed
[ ] send_from_directory reviewed
[ ] Uploads reviewed
[ ] Archive extraction reviewed
[ ] XML parsing reviewed
[ ] Pickle/YAML reviewed
```

## Sessions and Identity

```text
[ ] Session contents reviewed
[ ] Cookie flags reviewed
[ ] Persistent login reviewed
[ ] JWT claims reviewed
[ ] Token revocation reviewed
[ ] Password reset tokens reviewed
[ ] Host-dependent links reviewed
```

## APIs

```text
[ ] REST APIs reviewed
[ ] GraphQL reviewed
[ ] WebSockets reviewed
[ ] gRPC integrations reviewed
[ ] Mass assignment reviewed
[ ] Rate limiting reviewed
```

## Business Logic

```text
[ ] Prices reviewed
[ ] Balances reviewed
[ ] Discounts reviewed
[ ] Refunds reviewed
[ ] Inventory reviewed
[ ] Approval flows reviewed
[ ] State transitions reviewed
[ ] Role changes reviewed
[ ] Race conditions reviewed
```

## Secrets and Dependencies

```text
[ ] Hard-coded secrets searched
[ ] Environment files reviewed
[ ] Git history considered
[ ] Dependency files reviewed
[ ] pip-audit considered
[ ] OSV-Scanner considered
[ ] Secret scanning considered
```

## Static Analysis

```text
[ ] ripgrep searches performed
[ ] Semgrep considered
[ ] Bandit considered
[ ] CodeQL considered
[ ] Findings manually validated
[ ] Variant analysis performed
```

---

# Finding Validation Model

Before reporting:

```text
MATCH
  |
  v
REACHABLE?
  |
  +-- No --> Usually discard
  |
  v
ATTACKER CONTROL?
  |
  +-- No --> Contextual review
  |
  v
SECURITY BOUNDARY?
  |
  +-- Effective --> Protected
  |
  v
EXPLOITABLE?
  |
  +-- No --> Defence-in-depth / contextual
  |
  v
IMPACT?
  |
  v
CONFIRMED FINDING
```

---

# Example Finding - IDOR

```text
Title:
Missing Object-Level Authorisation on Invoice Endpoint

Route:
GET /invoices/<invoice_id>

Source:
invoice_id route parameter

Data Flow:

invoice_id
    |
    v
Invoice.query.get(invoice_id)
    |
    v
Invoice
    |
    v
render_template()

Authentication:
@login_required

Authorisation:
No ownership or tenant restriction was identified.

Impact:
An authenticated user may be able to access invoices belonging to another account by changing the invoice identifier.

Recommendation:
Scope the database lookup to objects the authenticated user is authorised to access or perform an equivalent object-level permission check.
```

---

# Example Finding - SSTI

```text
Title:
Server-Side Template Injection in Template Preview

Route:
POST /template/preview

Source:
request.form["template"]

Data Flow:

request.form["template"]
        |
        v
render_template_string()
        |
        v
Jinja Template Evaluation

Security Control:
No restriction prevents user-controlled input from becoming template source.

Impact:
The impact depends on the Jinja environment and application context and must be validated safely in the authorised environment.

Recommendation:
Do not interpret attacker-controlled input as template source. Keep template source server-controlled and pass untrusted values as template data.
```

---

# Example Finding - SSRF

```text
Title:
Server-Side Request Forgery in URL Preview Endpoint

Route:
POST /preview

Source:
request.form["url"]

Data Flow:

request.form["url"]
        |
        v
requests.get(url)

Security Control:
No effective destination restriction was identified.

Impact:
The server may perform outbound requests to destinations selected by the user, potentially including internal services depending on network access.

Recommendation:
Prefer server-controlled destinations. Where user-selected URLs are required, implement strict destination validation and network-level egress restrictions.
```

---

# Example Finding - SQL Injection

```text
Title:
SQL Injection Through Dynamically Constructed SQL Query

Route:
GET /search

Source:
request.args["q"]

Data Flow:

request.args["q"]
       |
       v
f-string SQL
       |
       v
db.session.execute()

Security Control:
No parameter binding was identified.

Recommendation:
Use ORM query construction or bind attacker-controlled values as parameters rather than concatenating them into SQL syntax.
```

---

# Example Finding - Stored XSS

```text
Title:
Stored Cross-Site Scripting Through Jinja Safe Filter

Source:
Profile biography

Data Flow:

POST /profile
      |
      v
Biography
      |
      v
Database
      |
      v
{{ biography|safe }}
      |
      v
Browser

Security Control:
Jinja's normal output escaping is explicitly bypassed.

Recommendation:
Do not mark attacker-controlled values as safe. If rich HTML is required, use an appropriate allowlist-based sanitisation strategy.
```

---

# Common Review Mistakes

## Flask Means No Security Controls

Incorrect.

Security controls may be implemented through:

```text
Extensions
Decorators
before_request hooks
Reverse proxies
API gateways
External identity providers
```

Map the actual architecture.

---

# login_required Means Authorisation Exists

Incorrect.

```text
login_required
      |
      v
Authenticated
```

does not automatically prove:

```text
Object ownership
Role permission
Tenant membership
Action permission
```

---

# SQLAlchemy Means SQL Injection Is Impossible

Incorrect.

Raw SQL and dynamic SQL construction can still occur.

Search:

```text
text()
execute()
cursor.execute()
```

---

# Every execute() Is SQL Injection

Incorrect.

Determine whether:

```text
SQL syntax is dynamic
Values are bound
Input is attacker-controlled
```

---

# Every render_template_string Is SSTI

Incorrect.

A static developer-controlled string may be safe.

The critical question is:

```text
Can attacker-controlled data become template source?
```

---

# Every safe Filter Is XSS

Incorrect.

Trace the value.

```text
Trusted static HTML
    !=
Attacker-controlled HTML
```

---

# Every requests.get Is SSRF

Incorrect.

Trace who controls the destination.

---

# Every redirect Is Open Redirect

Incorrect.

Determine whether attacker-controlled external destinations are accepted.

---

# Every send_file Is Path Traversal

Incorrect.

Determine who controls the final path.

---

# secure_filename Solves File Upload Security

Incorrect.

It addresses filename safety concerns, not the entire upload threat model.

---

# Every ProxyFix Is Vulnerable

Incorrect.

Its security depends on correct deployment topology and trusted proxy counts.

---

# Missing Flask-Limiter Means No Rate Limiting

Incorrect.

Rate limiting may be enforced outside the application.

---

# SECRET_KEY Found Means Secret Exposure

Incorrect.

Determine whether the value is:

```text
Real
Production
Sensitive
Committed
Reachable
```

---

# Final Flask Review Model

```text
                          FLASK APPLICATION
                                 |
                                 v
                               ROUTE
                                 |
          +----------------------+----------------------+
          |                      |                      |
          v                      v                      v
     request.args          request.form          request.json
          |                      |                      |
          +----------------------+----------------------+
                                 |
                                 v
                           VALIDATION
                                 |
                                 v
                         AUTHENTICATION
                                 |
                                 v
                          AUTHORISATION
                                 |
                                 v
                         BUSINESS LOGIC
                                 |
       +-------------------------+-------------------------+
       |                         |                         |
       v                         v                         v
    DATABASE                  TEMPLATE                  FILE
       |                         |                         |
       v                         v                         v
 SQL / NoSQL                   Jinja                  Filesystem

       +-------------------------+-------------------------+
       |                         |                         |
       v                         v                         v
   HTTP CLIENT               PROCESS                  QUEUE
       |                         |                         |
       v                         v                         v
      SSRF                Command Injection        Second-Order
                                                     Flows
```

The central question is:

```text
Can attacker-controlled data reach a security-sensitive operation
without an effective validation, authentication, authorisation or
framework security boundary?
```

Evaluate:

```text
Source
+
Route
+
Transformations
+
Validation
+
Authentication
+
Authorisation
+
Framework/extension protections
+
Sink
+
Reachability
+
Exploitability
+
Impact
```

Only then classify the candidate as a confirmed vulnerability.

---

# References

## Flask Documentation

[flask.palletsprojects.com](https://flask.palletsprojects.com/){ target="_blank" rel="noopener noreferrer" }

## Flask Security Considerations

[Flask Security Considerations](https://flask.palletsprojects.com/en/stable/web-security/){ target="_blank" rel="noopener noreferrer" }

## Flask Configuration

[Flask Configuration](https://flask.palletsprojects.com/en/stable/config/){ target="_blank" rel="noopener noreferrer" }

## Flask Request Object

[Flask Request Object](https://flask.palletsprojects.com/en/stable/api/#flask.Request){ target="_blank" rel="noopener noreferrer" }

## Flask File Uploads

[Flask File Uploads](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/){ target="_blank" rel="noopener noreferrer" }

## Flask Deployment

[Flask Deployment](https://flask.palletsprojects.com/en/stable/deploying/){ target="_blank" rel="noopener noreferrer" }

## Werkzeug

[Werkzeug](https://werkzeug.palletsprojects.com/){ target="_blank" rel="noopener noreferrer" }

## Werkzeug ProxyFix

[Werkzeug ProxyFix](https://werkzeug.palletsprojects.com/en/stable/middleware/proxy_fix/){ target="_blank" rel="noopener noreferrer" }

## Werkzeug Utilities

[Werkzeug Utilities](https://werkzeug.palletsprojects.com/en/stable/utils/){ target="_blank" rel="noopener noreferrer" }

## Jinja Documentation

[jinja.palletsprojects.com](https://jinja.palletsprojects.com/){ target="_blank" rel="noopener noreferrer" }

## Flask-Login

[Flask-Login](https://flask-login.readthedocs.io/){ target="_blank" rel="noopener noreferrer" }

## Flask-WTF

[Flask-WTF](https://flask-wtf.readthedocs.io/){ target="_blank" rel="noopener noreferrer" }

## Flask-CORS

[Flask-CORS](https://flask-cors.readthedocs.io/){ target="_blank" rel="noopener noreferrer" }

## Flask-Limiter

[Flask-Limiter](https://flask-limiter.readthedocs.io/){ target="_blank" rel="noopener noreferrer" }

## Flask-JWT-Extended

[Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/){ target="_blank" rel="noopener noreferrer" }

## Flask-SQLAlchemy

[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/){ target="_blank" rel="noopener noreferrer" }

## SQLAlchemy

[SQLAlchemy](https://docs.sqlalchemy.org/){ target="_blank" rel="noopener noreferrer" }

## Python subprocess

[Python subprocess](https://docs.python.org/3/library/subprocess.html){ target="_blank" rel="noopener noreferrer" }

## Python pickle

[Python pickle](https://docs.python.org/3/library/pickle.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

## OWASP ASVS

[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/){ target="_blank" rel="noopener noreferrer" }

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

## CWE

[CWE](https://cwe.mitre.org/){ target="_blank" rel="noopener noreferrer" }

## Semgrep

[Semgrep](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

## CodeQL for Python

[CodeQL for Python](https://codeql.github.com/docs/codeql-language-guides/codeql-for-python/){ target="_blank" rel="noopener noreferrer" }

## Bandit

[Bandit](https://bandit.readthedocs.io/){ target="_blank" rel="noopener noreferrer" }

## pip-audit

[pip-audit](https://github.com/pypa/pip-audit){ target="_blank" rel="noopener noreferrer" }

## OSV-Scanner

[OSV-Scanner](https://github.com/google/osv-scanner){ target="_blank" rel="noopener noreferrer" }

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/dotnet.md
docs/source-code-review/java.md
docs/source-code-review/php.md
docs/source-code-review/python.md
docs/source-code-review/django.md
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
docs/web/clickjacking.md
docs/web/open-redirect.md

docs/web/ssrf.md
docs/web/path-traversal.md
docs/web/file-upload.md
docs/web/deserialization.md

docs/web/host-header-attacks.md
docs/web/http-security-headers.md
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
