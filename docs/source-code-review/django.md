# Django Source Code Review

Django is a Python web framework that provides many security controls by default, including template escaping, CSRF protection, authentication, session management, ORM query parameterisation and host validation.

These protections significantly reduce common vulnerabilities when used correctly.

However, Django applications can still introduce vulnerabilities when developers:

```text
Bypass framework protections
Use raw SQL
Disable CSRF protection
Mark attacker-controlled HTML as safe
Perform missing object-level authorisation
Trust user-controlled object IDs
Use unsafe redirects
Construct paths from user input
Make outbound requests using attacker-controlled URLs
Perform unsafe deserialization
Expose sensitive settings
Use weak permission logic
Trust Host or proxy headers incorrectly
Mass assign model fields
Expose dangerous administrative functionality
```

The objective of Django source-code review is therefore not simply:

```text
Find dangerous functions
```

but:

```text
Understand how the application uses Django's security model
and identify where application code bypasses or weakens it.
```

The fundamental model remains:

```text
SOURCE
  |
  v
ATTACKER-CONTROLLED DATA
  |
  v
TRANSFORMATIONS
  |
  +-- forms
  +-- serializers
  +-- validation
  +-- parsing
  +-- business logic
  |
  v
SECURITY CONTROLS
  |
  +-- authentication
  +-- permissions
  +-- CSRF
  +-- ORM
  +-- template escaping
  |
  v
SINK
  |
  v
SECURITY-SENSITIVE OPERATION
```

Remember:

```text
Django application
    !=
Automatically secure
```

and:

```text
grep match
    !=
vulnerability
```

A source-code match identifies a location that requires investigation.

Exploitability requires understanding the complete data flow.

!!! warning "Authorised Security Testing"
    Perform source-code review and dynamic validation only against Django applications, repositories and environments for which you have explicit authorisation.

---

# Review Strategy

A practical Django review can follow:

```text
1. Identify Django version

2. Identify project structure

3. Review settings.py

4. Map URL configurations

5. Map views and API endpoints

6. Identify authentication controls

7. Identify authorisation controls

8. Review object-level access

9. Review forms and serializers

10. Review ORM usage

11. Search raw SQL

12. Review templates

13. Search escaping bypasses

14. Review CSRF protection

15. Review redirects

16. Review file uploads

17. Review file-system access

18. Review outbound requests

19. Review session configuration

20. Review host/proxy handling

21. Review Django REST Framework

22. Review business logic

23. Review background workers

24. Search secrets

25. Review dependencies

26. Run static analysis

27. Perform variant analysis

28. Validate findings dynamically where authorised
```

---

# Identify Django

Search dependency files:

```bash
rg -n -i \
'django|djangorestframework|django-rest-framework' \
requirements*.txt pyproject.toml Pipfile setup.py setup.cfg 2>/dev/null
```

Typical dependency:

```text
Django==5.x.x
```

or:

```toml
dependencies = [
    "Django>=5.2",
]
```

Determine the exact deployed version rather than relying only on development dependency files.

---

# Identify Django Version

Search:

```bash
rg -n \
'Django[=<>~!]|django[=<>~!]' \
requirements*.txt pyproject.toml Pipfile* poetry.lock uv.lock 2>/dev/null
```

If the environment is available:

```bash
python3 -m django --version
```

or:

```bash
python3 -c "import django; print(django.get_version())"
```

Version identification matters because:

```text
Security behaviour changes
Deprecated APIs change
Supported versions change
Security fixes are version-specific
Middleware behaviour evolves
```

Do not report an outdated Django version without confirming the actual runtime or deployed dependency.

---

# Django Project Structure

A common Django project resembles:

```text
project/
├── manage.py
├── requirements.txt
├── project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── api/
│   ├── serializers.py
│   ├── urls.py
│   ├── permissions.py
│   └── views.py
│
├── templates/
└── static/
```

High-value files include:

```text
settings.py
urls.py
views.py
models.py
forms.py
serializers.py
permissions.py
middleware.py
admin.py
tasks.py
signals.py
```

---

# Find Django Files

```bash
find . -type f \( \
-name 'settings.py' \
-o -name 'urls.py' \
-o -name 'views.py' \
-o -name 'models.py' \
-o -name 'forms.py' \
-o -name 'serializers.py' \
-o -name 'permissions.py' \
-o -name 'middleware.py' \
-o -name 'admin.py' \
-o -name 'tasks.py' \
-o -name 'signals.py' \
\) -print
```

---

# Identify Settings Modules

```bash
find . -type f -name 'settings*.py' -print
```

Projects may use:

```text
settings.py

settings/
├── base.py
├── development.py
├── staging.py
└── production.py
```

Review the configuration actually used in production.

---

# High-Value settings.py Search

```bash
rg -n \
'DEBUG|SECRET_KEY|ALLOWED_HOSTS|CSRF_|SESSION_|SECURE_|CORS_|DATABASES|MIDDLEWARE|INSTALLED_APPS|AUTHENTICATION_BACKENDS|AUTH_USER_MODEL|REST_FRAMEWORK' \
--glob '*.py' \
.
```

---

# DEBUG

Search:

```bash
rg -n \
'DEBUG\s*=' \
--glob '*.py' \
.
```

Potentially unsafe production configuration:

```python
DEBUG = True
```

Django debug output can expose substantial internal application information.

However:

```text
DEBUG = True in development settings
    !=
Production vulnerability
```

Determine which settings module is deployed.

---

# SECRET_KEY

Search:

```bash
rg -n \
'SECRET_KEY\s*=' \
--glob '*.py' \
.
```

Candidate:

```python
SECRET_KEY = "hard-coded-production-secret"
```

Prefer loading sensitive production values from appropriately protected configuration or secret-management systems.

Do not automatically report example or test keys as production secrets.

---

# Search Environment Loading

```bash
rg -n \
'os\.environ|os\.getenv|environ\.Env|decouple|dotenv|SECRET_KEY' \
--glob '*.py' \
.
```

---

# ALLOWED_HOSTS

Search:

```bash
rg -n \
'ALLOWED_HOSTS\s*=' \
--glob '*.py' \
.
```

Example:

```python
ALLOWED_HOSTS = [
    "app.example.com",
]
```

Review broad configurations such as:

```python
ALLOWED_HOSTS = ["*"]
```

but do not classify them as exploitable without understanding:

```text
Reverse proxy validation
Host usage
Absolute URL generation
Password-reset workflows
Deployment architecture
```

Django's host validation is an important control against malicious `Host` values.

---

# Middleware

Locate:

```bash
rg -n \
'MIDDLEWARE\s*=' \
--glob '*.py' \
.
```

Typical security-relevant middleware includes:

```text
SecurityMiddleware
SessionMiddleware
CommonMiddleware
CsrfViewMiddleware
AuthenticationMiddleware
```

Review whether expected middleware has been removed or replaced.

---

# Installed Applications

```bash
rg -n \
'INSTALLED_APPS\s*=' \
--glob '*.py' \
.
```

Look for:

```text
django.contrib.admin
django.contrib.auth
rest_framework
corsheaders
debug_toolbar
silk
django_extensions
third-party authentication packages
```

Development/debug packages deserve additional attention if enabled in production.

---

# Route Discovery

Django routes are normally defined using:

```python
path()
re_path()
include()
```

Search:

```bash
rg -n \
'urlpatterns|path\(|re_path\(|include\(' \
--glob 'urls.py' \
.
```

Broader search:

```bash
rg -n \
'\b(path|re_path|include)\(' \
--glob '*.py' \
.
```

---

# Basic Route

Example:

```python
urlpatterns = [
    path(
        "users/<int:user_id>/",
        views.user_detail,
        name="user-detail",
    ),
]
```

Map:

```text
/users/<user_id>/
        |
        v
views.user_detail
```

---

# Included Routes

Example:

```python
path(
    "api/",
    include("api.urls"),
)
```

Follow every `include()`.

Conceptually:

```text
project/urls.py
      |
      +-- accounts.urls
      |
      +-- api.urls
      |
      +-- admin.site.urls
```

---

# Route Inventory

Create:

| Method | Route | View | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/profile/` | `profile()` | Login | Self |
| GET | `/users/<id>/` | `user_detail()` | Login | ? |
| POST | `/upload/` | `upload()` | Login | User |
| DELETE | `/api/users/<id>/` | `UserViewSet` | Token | Admin |

This route map becomes the foundation of the review.

---

# Function-Based Views

Example:

```python
def profile(request):
    ...
```

Search:

```bash
rg -n \
'^def [A-Za-z_][A-Za-z0-9_]*\(request' \
--glob '*.py' \
.
```

Async views:

```bash
rg -n \
'^async def [A-Za-z_][A-Za-z0-9_]*\(request' \
--glob '*.py' \
.
```

---

# Class-Based Views

Search:

```bash
rg -n \
'class .*View\(|class .*APIView\(|class .*ViewSet\(|class .*GenericAPIView\(' \
--glob '*.py' \
.
```

Common Django classes include:

```text
View
TemplateView
DetailView
ListView
CreateView
UpdateView
DeleteView
FormView
```

DRF adds:

```text
APIView
GenericAPIView
ViewSet
ModelViewSet
ReadOnlyModelViewSet
```

---

# HTTP Method Handlers

Class-based views commonly use:

```python
def get(self, request):
    ...
```

```python
def post(self, request):
    ...
```

Search:

```bash
rg -n \
'def (get|post|put|patch|delete|head|options)\(' \
--glob '*.py' \
.
```

---

# User-Controlled Input

Common Django input sources include:

```python
request.GET
request.POST
request.FILES
request.COOKIES
request.headers
request.META
request.body
```

Route parameters are also attacker-controlled.

Example:

```python
def invoice(request, invoice_id):
    ...
```

`invoice_id` originates from the URL.

---

# Input Source Search

```bash
rg -n \
'request\.(GET|POST|FILES|COOKIES|headers|META|body)' \
--glob '*.py' \
.
```

---

# request.GET

Example:

```python
search = request.GET.get("search")
```

Search:

```bash
rg -n \
'request\.GET' \
--glob '*.py' \
.
```

---

# request.POST

```bash
rg -n \
'request\.POST' \
--glob '*.py' \
.
```

---

# Uploaded Files

```bash
rg -n \
'request\.FILES|UploadedFile|FileField|ImageField' \
--glob '*.py' \
.
```

---

# Headers

```bash
rg -n \
'request\.headers|request\.META' \
--glob '*.py' \
.
```

Potential attacker-controlled metadata includes:

```text
Host
Origin
Referer
User-Agent
X-Forwarded-For
X-Forwarded-Host
X-Forwarded-Proto
Custom headers
```

Trust depends on deployment architecture.

---

# JSON Input

Traditional Django views may parse:

```python
json.loads(request.body)
```

Search:

```bash
rg -n \
'json\.loads\(request\.body|request\.body' \
--glob '*.py' \
.
```

Django REST Framework normally provides:

```python
request.data
```

Search:

```bash
rg -n \
'request\.data' \
--glob '*.py' \
.
```

---

# Authentication

Django's authentication system commonly exposes:

```python
request.user
```

Search:

```bash
rg -n \
'request\.user|authenticate\(|login\(|logout\(' \
--glob '*.py' \
.
```

---

# login_required

Search:

```bash
rg -n \
'@login_required' \
--glob '*.py' \
.
```

Example:

```python
@login_required
def profile(request):
    ...
```

This verifies that the user is authenticated.

It does not automatically provide:

```text
Role authorisation
Object ownership
Tenant isolation
Business-level permission
```

---

# LoginRequiredMixin

Class-based views may use:

```python
class ProfileView(
    LoginRequiredMixin,
    TemplateView
):
    ...
```

Search:

```bash
rg -n \
'LoginRequiredMixin' \
--glob '*.py' \
.
```

---

# permission_required

Search:

```bash
rg -n \
'@permission_required|PermissionRequiredMixin' \
--glob '*.py' \
.
```

Example:

```python
@permission_required(
    "accounts.delete_user",
    raise_exception=True,
)
def delete_user(request, user_id):
    ...
```

Review:

```text
Correct permission?
Correct object?
Correct failure behaviour?
```

---

# user_passes_test

Search:

```bash
rg -n \
'user_passes_test' \
--glob '*.py' \
.
```

Example:

```python
@user_passes_test(
    lambda user: user.is_staff
)
def admin_report(request):
    ...
```

Review the test itself.

---

# is_staff and is_superuser

Search:

```bash
rg -n \
'is_staff|is_superuser' \
--glob '*.py' \
.
```

Do not assume these checks are incorrect.

Determine whether they match the application's intended privilege model.

---

# Authentication Bypass Review

Compare routes that perform similar actions.

Example:

```text
GET /account/
    -> @login_required

POST /account/update/
    -> @login_required

POST /account/delete/
    -> no authentication decorator
```

The missing control may be more important than a dangerous function.

---

# Authorisation

Authentication answers:

```text
Who are you?
```

Authorisation answers:

```text
Are you allowed to perform this action?
```

Search:

```bash
rg -n -i \
'permission|authorize|authorise|role|is_staff|is_superuser|owner|created_by|tenant|organization|organisation' \
--glob '*.py' \
.
```

---

# Object-Level Authorisation

A common Django vulnerability occurs when a view retrieves an object using an attacker-controlled ID without checking ownership.

Candidate:

```python
@login_required
def invoice(request, invoice_id):
    invoice = Invoice.objects.get(
        id=invoice_id
    )

    return render(
        request,
        "invoice.html",
        {"invoice": invoice},
    )
```

Data flow:

```text
/invoices/<invoice_id>/
          |
          v
invoice_id
          |
          v
Invoice.objects.get()
          |
          v
Invoice returned
```

Critical question:

```text
Where is object-level authorisation?
```

---

# Safer Query Scoping

A stronger design may scope the lookup:

```python
invoice = get_object_or_404(
    Invoice,
    id=invoice_id,
    owner=request.user,
)
```

Conceptually:

```text
Object ID
   +
Authenticated User
   |
   v
Scoped Query
```

For multi-tenant applications:

```python
invoice = get_object_or_404(
    Invoice,
    id=invoice_id,
    tenant=request.user.tenant,
)
```

The exact rule depends on the application's authorisation model.

---

# get_object_or_404

Search:

```bash
rg -n \
'get_object_or_404\(' \
--glob '*.py' \
.
```

Do not assume it provides authorisation.

Example:

```python
get_object_or_404(
    Invoice,
    id=invoice_id,
)
```

only proves that the object exists.

It does not prove the current user may access it.

---

# ORM Object Lookup Search

```bash
rg -n \
'\.objects\.(get|filter|exclude|all|first|last|create|update|get_or_create|update_or_create)\(' \
--glob '*.py' \
.
```

Prioritise lookups involving:

```text
id
pk
user_id
account_id
invoice_id
document_id
tenant_id
organisation_id
organization_id
```

---

# Tenant Isolation

Search:

```bash
rg -n -i \
'tenant|tenant_id|organisation|organization|workspace|account_id|company_id' \
--glob '*.py' \
.
```

Map:

```text
Authenticated User
       |
       v
Tenant Membership
       |
       v
Tenant-Scoped Queryset
       |
       v
Object
```

Look for code such as:

```python
Document.objects.get(
    id=document_id
)
```

where expected scoping should resemble:

```python
Document.objects.get(
    id=document_id,
    tenant=request.user.tenant,
)
```

---

# Django REST Framework

Django REST Framework is extremely common in Django applications.

Identify it:

```bash
rg -n \
'rest_framework|APIView|ViewSet|ModelViewSet|Serializer|ModelSerializer' \
--glob '*.py' \
.
```

Important review areas include:

```text
Authentication classes
Permission classes
Object permissions
Queryset filtering
Serializers
Mass assignment
Throttling
Parsers
Renderers
Custom actions
```

---

# DRF Authentication

Search:

```bash
rg -n \
'authentication_classes|DEFAULT_AUTHENTICATION_CLASSES' \
--glob '*.py' \
.
```

Authentication establishes identity.

It does not by itself determine whether an operation is authorised.

---

# DRF Permissions

Search:

```bash
rg -n \
'permission_classes|DEFAULT_PERMISSION_CLASSES|AllowAny|IsAuthenticated|IsAdminUser|IsAuthenticatedOrReadOnly' \
--glob '*.py' \
.
```

Example:

```python
class AccountView(
    APIView
):
    permission_classes = [
        IsAuthenticated
    ]
```

This ensures authentication.

It does not necessarily ensure object ownership.

---

# AllowAny

Search:

```bash
rg -n \
'AllowAny|permission_classes\s*=\s*\[\s*\]' \
--glob '*.py' \
.
```

`AllowAny` may be completely appropriate for:

```text
Login
Registration
Public content
Health endpoints
Webhook endpoints with independent authentication
```

Review the endpoint's intended security requirements.

---

# DRF Default Permissions

Review:

```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        ...
    ],
}
```

Search:

```bash
rg -n \
'REST_FRAMEWORK|DEFAULT_PERMISSION_CLASSES' \
--glob '*.py' \
.
```

DRF's default permission policy is unrestricted unless the application configures a different default. Therefore, explicit application policy is important when reviewing APIs. :contentReference[oaicite:0]{index=0}

---

# DRF Object-Level Permissions

Custom permission:

```python
class IsOwner(
    permissions.BasePermission
):
    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        return obj.owner == request.user
```

Search:

```bash
rg -n \
'has_object_permission|check_object_permissions' \
--glob '*.py' \
.
```

DRF generic views call object-level permission checks during normal object retrieval, but custom object retrieval logic may need to call `check_object_permissions()` explicitly. List endpoints also require queryset filtering because object-level permission checks are not automatically applied to every returned object. :contentReference[oaicite:1]{index=1}

---

# Dangerous Custom get_object()

Candidate:

```python
def get_object(self):
    return Invoice.objects.get(
        pk=self.kwargs["pk"]
    )
```

Review whether this bypasses expected object permission checks.

Safer custom implementations may need:

```python
obj = get_object_or_404(
    self.get_queryset(),
    pk=self.kwargs["pk"],
)

self.check_object_permissions(
    self.request,
    obj,
)

return obj
```

The exact implementation depends on the view architecture.

---

# DRF get_queryset()

Search:

```bash
rg -n \
'def get_queryset\(' \
--glob '*.py' \
.
```

Example:

```python
def get_queryset(self):
    return Invoice.objects.filter(
        owner=self.request.user
    )
```

This can enforce visibility at the queryset level.

Review every override.

---

# Dangerous Broad Queryset

Candidate:

```python
queryset = Invoice.objects.all()
```

This is not automatically vulnerable.

Ask:

```text
Are permission classes present?
Is get_queryset() overridden?
Are object permissions applied?
Should list responses be tenant-scoped?
```

---

# DRF Serializers

Search:

```bash
rg -n \
'class .*Serializer|ModelSerializer|Serializer\(' \
--glob '*.py' \
.
```

Serializers are security-relevant because they control:

```text
Accepted input
Validation
Writable fields
Read-only fields
Object creation
Object updates
Output
```

DRF serializers deserialize and validate incoming data before exposing it as `validated_data`. :contentReference[oaicite:2]{index=2}

---

# ModelSerializer

Example:

```python
class UserSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
        ]
```

Explicit field lists are easier to reason about during security review.

---

# Serializer fields

Search:

```bash
rg -n \
'fields\s*=|exclude\s*=|read_only_fields|write_only|read_only' \
--glob 'serializers.py' \
.
```

Security-sensitive fields include:

```text
is_staff
is_superuser
role
permissions
groups
owner
owner_id
tenant
tenant_id
balance
verified
status
approved
```

---

# read_only_fields

Example:

```python
class UserSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "is_staff",
        ]

        read_only_fields = [
            "is_staff",
        ]
```

DRF read-only fields appear in output but are not accepted as writable input. :contentReference[oaicite:3]{index=3}

---

# Serializer Validation

Search:

```bash
rg -n \
'def validate_|def validate\(' \
--glob '*.py' \
.
```

Example:

```python
def validate_role(self, value):
    ...
```

and:

```python
def validate(self, attrs):
    ...
```

Review whether validation implements:

```text
Security rules
Cross-field constraints
Tenant restrictions
State transitions
Ownership rules
```

Validation is not a substitute for authorisation.

---

# Serializer create() and update()

Search:

```bash
rg -n \
'def create\(self, validated_data|def update\(self, instance, validated_data' \
--glob '*.py' \
.
```

These are high-value locations for mass assignment and privilege changes.

---

# Mass Assignment

Candidate:

```python
def update(
    self,
    instance,
    validated_data,
):
    for key, value in validated_data.items():
        setattr(
            instance,
            key,
            value,
        )

    instance.save()

    return instance
```

Whether this is dangerous depends on which fields can enter `validated_data`.

Trace:

```text
Request Data
    |
    v
Serializer Fields
    |
    v
Validation
    |
    v
validated_data
    |
    v
Model Update
```

Refer to:

```text
docs/web/mass-assignment.md
```

---

# DRF Custom Actions

Search:

```bash
rg -n \
'@action\(' \
--glob '*.py' \
.
```

Example:

```python
@action(
    detail=True,
    methods=["post"],
)
def approve(
    self,
    request,
    pk=None,
):
    ...
```

Custom actions frequently implement security-sensitive business operations.

Review:

```text
Authentication
Permission classes
Object permissions
State transition
Ownership
Role requirements
```

---

# Forms

Django forms provide structured validation.

Search:

```bash
rg -n \
'class .*Form\(|class .*ModelForm\(' \
--glob '*.py' \
.
```

Example:

```python
class ProfileForm(
    forms.ModelForm
):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "bio",
        ]
```

---

# ModelForm Mass Assignment

Review:

```python
fields = "__all__"
```

Search:

```bash
rg -n \
'fields\s*=\s*["'\'']__all__["'\'']' \
--glob '*.py' \
.
```

This is not automatically vulnerable.

Determine whether the underlying model contains security-sensitive fields that users should not modify.

---

# Form Validation

Search:

```bash
rg -n \
'def clean\(|def clean_[A-Za-z_]' \
--glob '*.py' \
.
```

Example:

```python
def clean_email(self):
    ...
```

Review:

```text
Validation correctness
Canonicalisation
Cross-field rules
Business constraints
```

---

# SQL Injection

Django's ORM normally constructs parameterised database queries.

Typical ORM usage:

```python
User.objects.filter(
    username=username
)
```

does not involve manually concatenating SQL.

The highest-value areas are raw SQL interfaces.

---

# raw()

Search:

```bash
rg -n \
'\.raw\(' \
--glob '*.py' \
.
```

Candidate:

```python
query = (
    "SELECT * FROM accounts_user "
    "WHERE username = '"
    + username
    + "'"
)

User.objects.raw(query)
```

Trace attacker-controlled values into the SQL string.

---

# RawSQL

Search:

```bash
rg -n \
'RawSQL\(' \
--glob '*.py' \
.
```

Raw SQL constructs require manual review because the developer controls the SQL. Django's security documentation specifically notes that raw SQL mechanisms require safe handling of user input. :contentReference[oaicite:4]{index=4}

---

# connection.cursor()

Search:

```bash
rg -n \
'connection\.cursor\(|cursor\.execute\(|cursor\.executemany\(' \
--glob '*.py' \
.
```

Candidate:

```python
with connection.cursor() as cursor:
    cursor.execute(
        f"""
        SELECT *
        FROM accounts_user
        WHERE username = '{username}'
        """
    )
```

---

# Parameterised Raw Query

Preferred pattern:

```python
with connection.cursor() as cursor:
    cursor.execute(
        """
        SELECT *
        FROM accounts_user
        WHERE username = %s
        """,
        [username],
    )
```

Do not manually quote placeholders.

---

# extra()

Search:

```bash
rg -n \
'\.extra\(' \
--glob '*.py' \
.
```

`extra()` is an older raw-SQL-style queryset API and deserves review when encountered.

Do not report it solely because it exists.

Trace how SQL fragments and parameters are constructed.

---

# SQL Search

```bash
rg -n \
'\.raw\(|RawSQL\(|connection\.cursor\(|cursor\.execute\(|cursor\.executemany\(|\.extra\(' \
--glob '*.py' \
.
```

Refer to:

```text
docs/web/sql-injection.md
```

---

# Dynamic ORM Fields

ORM parameterisation does not make arbitrary attacker-controlled query structure safe.

Candidate:

```python
sort = request.GET.get("sort")

results = User.objects.order_by(
    sort
)
```

This may not be SQL injection in the classic sense, but dynamic field selection still deserves review.

Prefer server-controlled mappings where appropriate:

```python
allowed_sort = {
    "name": "username",
    "date": "date_joined",
}

sort_field = allowed_sort.get(
    sort,
    "username",
)
```

---

# Queryset Filters from Dictionaries

Search:

```bash
rg -n \
'\.filter\(\*\*|\.get\(\*\*|\.exclude\(\*\*' \
--glob '*.py' \
.
```

Candidate:

```python
filters = request.data

User.objects.filter(
    **filters
)
```

Review whether users can influence:

```text
Unexpected fields
Relationship traversal
Tenant scoping
Business logic
```

Do not automatically classify this as SQL injection.

---

# XSS

Django templates escape variables by default in normal HTML template contexts.

Example:

```html
<p>{{ username }}</p>
```

The major review targets are mechanisms that intentionally bypass escaping.

---

# mark_safe

Search:

```bash
rg -n \
'mark_safe\(' \
--glob '*.py' \
.
```

Candidate:

```python
return mark_safe(
    request.GET.get("message")
)
```

Trace whether attacker-controlled data is explicitly marked safe.

---

# safe Filter

Search:

```bash
rg -n \
'\|\s*safe\b' \
--glob '*.html' \
--glob '*.htm' \
--glob '*.txt' \
.
```

Candidate:

```html
{{ biography|safe }}
```

Trace where `biography` originates.

---

# autoescape off

Search:

```bash
rg -n \
'autoescape\s+off' \
--glob '*.html' \
.
```

Example:

```django
{% autoescape off %}
    {{ content }}
{% endautoescape %}
```

Review all variables inside the block.

---

# format_html

Search:

```bash
rg -n \
'format_html\(' \
--glob '*.py' \
.
```

`format_html()` is designed to build HTML while escaping interpolated arguments.

Do not classify its use as XSS solely because HTML is being generated.

Review any arguments already marked safe.

---

# format_html_join

```bash
rg -n \
'format_html_join\(' \
--glob '*.py' \
.
```

Again, investigate data flow rather than flagging the API itself.

---

# html_safe

Search:

```bash
rg -n \
'html_safe|SafeString|SafeData' \
--glob '*.py' \
.
```

These are high-value review locations because they interact with Django's escaping model.

---

# Template Search

```bash
rg -n \
'mark_safe\(|format_html\(|format_html_join\(|SafeString|\|\s*safe\b|autoescape\s+off' \
--glob '*.py' \
--glob '*.html' \
.
```

Refer to:

```text
docs/web/xss.md
docs/web/html-injection.md
```

---

# JavaScript Context

Even escaped template values can become dangerous when placed into inappropriate contexts.

Candidate:

```html
<script>
    const username = "{{ username }}";
</script>
```

HTML escaping and JavaScript-string escaping are different security contexts.

Review template data inserted into:

```text
JavaScript
CSS
URLs
HTML attributes
Inline event handlers
```

---

# json_script

For safely transferring structured data into JavaScript, Django provides mechanisms such as `json_script`.

Search:

```bash
rg -n \
'json_script' \
--glob '*.html' \
--glob '*.py' \
.
```

Review how the resulting data is subsequently consumed in JavaScript.

---

# Server-Side Template Injection

Traditional Django template rendering normally uses server-controlled template names:

```python
return render(
    request,
    "profile.html",
    context,
)
```

The review priority increases if attacker input controls template source or template selection.

Search:

```bash
rg -n \
'Template\(|Engine\(|from_string\(|get_template\(|select_template\(' \
--glob '*.py' \
.
```

Candidate:

```python
template_source = request.POST["template"]

template = Template(
    template_source
)

return HttpResponse(
    template.render(context)
)
```

Review the actual template engine and capabilities before determining impact.

Refer to:

```text
docs/web/ssti.md
```

---

# Template Path Control

Candidate:

```python
template_name = request.GET["template"]

return render(
    request,
    template_name,
)
```

Review whether attacker-controlled template names can expose unintended templates or interact with custom template loaders.

---

# CSRF

Django provides CSRF protection through middleware and template mechanisms.

Review middleware:

```bash
rg -n \
'CsrfViewMiddleware' \
--glob '*.py' \
.
```

---

# csrf_exempt

High-value search:

```bash
rg -n \
'@csrf_exempt|csrf_exempt\(' \
--glob '*.py' \
.
```

Example:

```python
@csrf_exempt
def update_profile(request):
    ...
```

Do not automatically report every exemption.

Determine:

```text
Does the endpoint change state?
Does it use cookie-based authentication?
Is there another request-authentication mechanism?
Is the endpoint intentionally called cross-site?
```

---

# csrf_protect

Search:

```bash
rg -n \
'@csrf_protect|csrf_protect\(' \
--glob '*.py' \
.
```

---

# Template CSRF Tokens

Search:

```bash
rg -n \
'csrf_token' \
--glob '*.html' \
.
```

Example:

```django
<form method="post">
    {% csrf_token %}
</form>
```

---

# CSRF Trusted Origins

Search:

```bash
rg -n \
'CSRF_TRUSTED_ORIGINS|CSRF_COOKIE_|CSRF_USE_SESSIONS' \
--glob '*.py' \
.
```

Review broad trusted-origin configurations.

Refer to:

```text
docs/web/csrf.md
```

---

# CORS

Django applications commonly use:

```text
django-cors-headers
```

Search:

```bash
rg -n -i \
'corsheaders|CORS_ALLOWED_ORIGINS|CORS_ALLOW_ALL_ORIGINS|CORS_ALLOW_CREDENTIALS|CORS_ALLOWED_ORIGIN_REGEXES' \
--glob '*.py' \
.
```

---

# Broad CORS

Candidate:

```python
CORS_ALLOW_ALL_ORIGINS = True
```

This is not automatically exploitable.

Determine:

```text
Are credentials permitted?
What endpoints return sensitive information?
What authentication mechanism is used?
Can an attacker-controlled origin read sensitive responses?
```

Refer to:

```text
docs/web/cors.md
```

---

# Open Redirect

Django redirect functionality includes:

```python
redirect()
HttpResponseRedirect()
HttpResponsePermanentRedirect()
```

Search:

```bash
rg -n \
'redirect\(|HttpResponseRedirect\(|HttpResponsePermanentRedirect\(' \
--glob '*.py' \
.
```

Candidate:

```python
next_url = request.GET.get("next")

return redirect(next_url)
```

Trace whether external destinations are allowed.

---

# Login Redirects

Search:

```bash
rg -n \
'next|redirect_to|LOGIN_REDIRECT_URL|LOGOUT_REDIRECT_URL' \
--glob '*.py' \
.
```

Login flows frequently accept a destination such as:

```text
?next=/dashboard/
```

Review whether external destinations are properly rejected.

---

# URL Safety Helpers

Search:

```bash
rg -n \
'url_has_allowed_host_and_scheme' \
--glob '*.py' \
.
```

This Django helper can be used when validating redirect targets against expected hosts and schemes.

Review the arguments and trusted-host set.

Refer to:

```text
docs/web/open-redirect.md
```

---

# SSRF

Django itself does not prevent application code from making unsafe outbound requests.

Search:

```bash
rg -n \
'requests\.(get|post|put|patch|delete|request)\(|httpx\.|urlopen\(|aiohttp\.ClientSession' \
--glob '*.py' \
.
```

Candidate:

```python
url = request.POST["url"]

response = requests.get(
    url
)
```

Data flow:

```text
request.POST["url"]
        |
        v
url
        |
        v
requests.get()
        |
        v
Outbound Request
```

Review:

```text
Destination allowlist
Scheme
Hostname
Port
DNS resolution
Redirects
IPv4/IPv6
Internal networks
Loopback
Link-local
Cloud metadata
Egress controls
```

Refer to:

```text
docs/web/ssrf.md
```

---

# Path Traversal

Search:

```bash
rg -n \
'\bopen\(|Path\(|os\.path\.join\(|FileResponse\(|StreamingHttpResponse\(' \
--glob '*.py' \
.
```

Candidate:

```python
filename = request.GET["file"]

path = os.path.join(
    settings.MEDIA_ROOT,
    filename,
)

return FileResponse(
    open(path, "rb")
)
```

Do not assume `os.path.join()` provides containment.

Trace the final canonical path.

---

# FileResponse

Search:

```bash
rg -n \
'FileResponse\(' \
--glob '*.py' \
.
```

Review where the opened file path originates.

---

# MEDIA_ROOT

Search:

```bash
rg -n \
'MEDIA_ROOT|MEDIA_URL|STATIC_ROOT|STATIC_URL' \
--glob '*.py' \
.
```

Review separation between:

```text
Uploaded content
Static content
Application source
Templates
Sensitive files
```

Refer to:

```text
docs/web/path-traversal.md
```

---

# File Upload

Django provides:

```python
request.FILES
```

and model fields such as:

```python
FileField
ImageField
```

Search:

```bash
rg -n \
'request\.FILES|FileField\(|ImageField\(|UploadedFile|FileSystemStorage' \
--glob '*.py' \
.
```

---

# Upload Review

For each upload flow determine:

```text
Who can upload?
What file types are expected?
How is filename handled?
Where is the file stored?
Can the file overwrite another file?
Is it publicly accessible?
Is content served with a safe Content-Type?
Is active content possible?
Is the file processed?
Is it passed to another parser?
Is it extracted?
Is it converted?
```

---

# File Extensions

Search:

```bash
rg -n -i \
'extension|content_type|mimetype|mime|filename' \
--glob '*.py' \
.
```

Do not assume extension validation alone proves content safety.

---

# File Validators

Search:

```bash
rg -n \
'FileExtensionValidator|validate_image_file_extension|validators=' \
--glob '*.py' \
.
```

Review whether validation matches the actual downstream risk.

---

# upload_to

Search:

```bash
rg -n \
'upload_to\s*=' \
--glob '*.py' \
.
```

Example:

```python
file = models.FileField(
    upload_to="documents/",
)
```

Custom upload path functions deserve additional review.

---

# Custom Upload Path

Example:

```python
def upload_path(
    instance,
    filename,
):
    return (
        f"{instance.user.username}/"
        f"{filename}"
    )
```

Review attacker control over:

```text
filename
username
directory components
```

---

# Archive Processing

Search:

```bash
rg -n \
'zipfile|ZipFile|tarfile|TarFile|extractall\(|unpack_archive\(' \
--glob '*.py' \
.
```

Uploaded archives can create:

```text
Path traversal
Resource exhaustion
Unexpected file overwrite
Unsafe downstream processing
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
obj = pickle.loads(
    request.body
)
```

Never deserialize untrusted pickle data.

Refer to:

```text
docs/web/deserialization.md
```

---

# Django Signed Data

Search:

```bash
rg -n \
'django\.core\.signing|signing\.(dumps|loads)|Signer\(|TimestampSigner\(' \
--glob '*.py' \
.
```

Signed data provides integrity when correctly implemented.

However, review:

```text
SECRET_KEY security
Salt separation
Expiration
Purpose
What data is trusted after verification
```

A valid signature does not automatically mean the underlying action is authorised.

---

# Session Management

Search:

```bash
rg -n \
'SESSION_ENGINE|SESSION_COOKIE_|SESSION_EXPIRE_AT_BROWSER_CLOSE|SESSION_COOKIE_AGE|request\.session' \
--glob '*.py' \
.
```

---

# Session Cookie Settings

High-value settings:

```text
SESSION_COOKIE_SECURE
SESSION_COOKIE_HTTPONLY
SESSION_COOKIE_SAMESITE
SESSION_COOKIE_DOMAIN
SESSION_COOKIE_PATH
```

Search:

```bash
rg -n \
'SESSION_COOKIE_(SECURE|HTTPONLY|SAMESITE|DOMAIN|PATH)' \
--glob '*.py' \
.
```

Remember that settings can be overridden by environment-specific configuration.

---

# CSRF Cookie Settings

Search:

```bash
rg -n \
'CSRF_COOKIE_(SECURE|HTTPONLY|SAMESITE|DOMAIN)' \
--glob '*.py' \
.
```

Do not blindly apply session-cookie assumptions to CSRF cookies. Understand Django's CSRF design and the application's JavaScript requirements.

---

# Secure Proxy SSL Header

Search:

```bash
rg -n \
'SECURE_PROXY_SSL_HEADER' \
--glob '*.py' \
.
```

Example:

```python
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)
```

This configuration is security-sensitive because it depends on the reverse proxy reliably controlling the corresponding header.

Review deployment architecture.

---

# USE_X_FORWARDED_HOST

Search:

```bash
rg -n \
'USE_X_FORWARDED_HOST|USE_X_FORWARDED_PORT' \
--glob '*.py' \
.
```

Incorrect trust in forwarded headers can contribute to:

```text
Host confusion
Incorrect absolute URLs
Security-sensitive redirects
Password-reset poisoning
Logging inaccuracies
```

---

# Host Header Usage

Search:

```bash
rg -n \
'request\.get_host\(|request\.build_absolute_uri\(|request\.META.*HTTP_HOST|request\.headers.*Host' \
--glob '*.py' \
.
```

---

# build_absolute_uri

Search:

```bash
rg -n \
'build_absolute_uri\(' \
--glob '*.py' \
.
```

High-value contexts:

```text
Password-reset emails
Account activation
Email verification
OAuth callbacks
Generated external links
```

Determine whether the resulting host is derived from trusted configuration or request metadata.

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# Password Reset

Django provides built-in password-reset functionality.

Search:

```bash
rg -n -i \
'PasswordReset|PasswordResetView|PasswordResetForm|PasswordResetTokenGenerator|password_reset|reset_password' \
--glob '*.py' \
.
```

Review custom implementations carefully.

---

# Custom Reset Tokens

Search:

```bash
rg -n -i \
'reset_token|password_reset_token|forgot_password|forgot.?password' \
--glob '*.py' \
.
```

Review:

```text
Randomness
Expiration
Single use
User binding
Enumeration
Rate limiting
Host generation
Session invalidation
```

Refer to:

```text
docs/web/password-reset.md
```

---

# Password Handling

Search:

```bash
rg -n \
'set_password\(|check_password\(|make_password\(|check_password\(' \
--glob '*.py' \
.
```

Django provides password hashing infrastructure.

Review custom password storage separately.

---

# Dangerous Direct Password Assignment

Search:

```bash
rg -n \
'\.password\s*=' \
--glob '*.py' \
.
```

Candidate:

```python
user.password = password
user.save()
```

This may store the value without Django's normal password hashing workflow.

Expected application code generally uses:

```python
user.set_password(password)
```

Validate surrounding code before reporting.

---

# Password Hashers

Search:

```bash
rg -n \
'PASSWORD_HASHERS' \
--glob '*.py' \
.
```

Review custom or legacy configurations.

---

# MFA

Django MFA may be implemented through third-party packages or custom code.

Search:

```bash
rg -n -i \
'totp|hotp|otp|mfa|2fa|two.?factor|recovery.?code|backup.?code' \
--glob '*.py' \
.
```

Review:

```text
Enrollment
Secret generation
Verification
Replay
Rate limiting
Recovery
Reset
Remember-device functionality
Bypass paths
```

Refer to:

```text
docs/web/mfa.md
```

---

# OAuth / OIDC

Common Django integrations include:

```text
django-allauth
social-auth-app-django
mozilla-django-oidc
Authlib integrations
```

Search:

```bash
rg -n -i \
'oauth|openid|oidc|allauth|social_auth|client_id|client_secret|redirect_uri|state|nonce|code_verifier' \
--glob '*.py' \
.
```

Review:

```text
State validation
Nonce
PKCE
Issuer
Audience
Redirect URI
Account linking
Callback handling
Token storage
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
'saml|python3-saml|pysaml|xmlsec|onelogin' \
--glob '*.py' \
.
```

Review:

```text
Signature validation
Assertion validation
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

# LDAP

Django applications may authenticate against LDAP.

Search:

```bash
rg -n -i \
'ldap|django_auth_ldap|AUTH_LDAP' \
--glob '*.py' \
.
```

Review custom LDAP filters and search construction.

Candidate:

```python
ldap_filter = (
    "(uid="
    + username
    + ")"
)
```

Refer to:

```text
docs/web/ldap-injection.md
```

---

# Command Injection

Django applications can invoke operating-system commands just like other Python applications.

Search:

```bash
rg -n \
'os\.(system|popen)\(|subprocess\.(run|Popen|call|check_call|check_output)\(|shell\s*=\s*True' \
--glob '*.py' \
.
```

Candidate:

```python
host = request.POST["host"]

subprocess.run(
    f"ping -c 1 {host}",
    shell=True,
)
```

Prefer avoiding shell invocation and passing arguments separately where possible.

Refer to:

```text
docs/web/command-injection.md
```

---

# Dynamic Code Execution

Search:

```bash
rg -n \
'\beval\(|\bexec\(|\bcompile\(' \
--glob '*.py' \
.
```

Candidate:

```python
expression = request.POST["expression"]

result = eval(expression)
```

Attacker-controlled input reaching `eval()` or `exec()` is a high-priority review target.

---

# XML / XXE

Search:

```bash
rg -n \
'xml\.etree|ElementTree|lxml|etree|xml\.dom|minidom|sax|XMLParser' \
--glob '*.py' \
.
```

Review:

```text
Parser
Version
DTD support
Entity resolution
Network access
Input trust
```

Do not classify XML parsing alone as XXE.

Refer to:

```text
docs/web/xxe.md
```

---

# Information Disclosure

Search:

```bash
rg -n \
'DEBUG\s*=|traceback|logger\.exception|print_exc|HttpResponse\(.*exception|str\(.*exception' \
--glob '*.py' \
.
```

Review whether exceptions expose:

```text
Stack traces
Source paths
Database errors
Secrets
Internal URLs
User information
Configuration
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

Look for:

```text
Passwords
JWTs
Session IDs
API keys
Reset tokens
MFA codes
Authorization headers
Sensitive request bodies
```

---

# SecurityMiddleware

Search:

```bash
rg -n \
'SecurityMiddleware|SECURE_' \
--glob '*.py' \
.
```

Security-related settings may include:

```text
SECURE_SSL_REDIRECT
SECURE_HSTS_SECONDS
SECURE_HSTS_INCLUDE_SUBDOMAINS
SECURE_HSTS_PRELOAD
SECURE_CONTENT_TYPE_NOSNIFF
SECURE_REFERRER_POLICY
```

Do not assume missing source configuration means the deployed application lacks the corresponding protection.

Reverse proxies and CDNs may provide some HTTP controls.

Validate actual responses.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# Clickjacking

Search:

```bash
rg -n \
'X_FRAME_OPTIONS|xframe_options_exempt|xframe_options_deny|xframe_options_sameorigin' \
--glob '*.py' \
.
```

High-value target:

```python
@xframe_options_exempt
```

Review why framing is allowed.

Refer to:

```text
docs/web/clickjacking.md
```

---

# Cache Security

Django provides several caching mechanisms.

Search:

```bash
rg -n \
'cache\.|cache_page|vary_on_headers|vary_on_cookie|CACHE_MIDDLEWARE|CACHES\s*=' \
--glob '*.py' \
.
```

Review cache keys and variation for:

```text
Authentication
User
Tenant
Role
Cookie
Host
Language
Headers
Query parameters
```

---

# cache_page

Example:

```python
@cache_page(60 * 15)
def dashboard(request):
    ...
```

If the response is user-specific, determine whether the cache is appropriately separated.

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# Business Logic

Search:

```bash
rg -n -i \
'price|amount|balance|discount|coupon|refund|credit|quantity|approved|verified|status|role|permission|tenant' \
--glob '*.py' \
.
```

Review:

```text
Pricing
Payments
Refunds
Credits
Discounts
Inventory
Approval workflows
Account state
Verification
Role changes
Tenant changes
```

---

# Model Methods

Security-sensitive business logic may reside in models.

Search:

```bash
rg -n \
'^class .*models\.Model|def save\(|def clean\(' \
--glob 'models.py' \
.
```

Do not review only views.

---

# Signals

Django signals can trigger hidden side effects.

Search:

```bash
rg -n \
'@receiver|post_save|pre_save|post_delete|pre_delete|m2m_changed' \
--glob '*.py' \
.
```

Example flow:

```text
HTTP Request
    |
    v
Model Save
    |
    v
post_save Signal
    |
    v
External Request
```

The dangerous sink may not appear in the view.

---

# Race Conditions

Search:

```bash
rg -n \
'transaction\.atomic|select_for_update|F\(|get_or_create|update_or_create' \
--glob '*.py' \
.
```

High-value workflows include:

```text
Balance changes
Coupon redemption
Inventory
One-time tokens
Password reset
Invitation acceptance
Approval
```

---

# select_for_update

Search:

```bash
rg -n \
'select_for_update\(' \
--glob '*.py' \
.
```

This may indicate explicit row locking.

Its presence does not automatically prove the workflow is race-safe.

Review the complete transaction.

---

# transaction.atomic

Search:

```bash
rg -n \
'transaction\.atomic' \
--glob '*.py' \
.
```

Map:

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
Commit
```

Determine whether concurrent requests can violate business invariants.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Rate Limiting

Traditional Django does not automatically provide comprehensive application-specific rate limiting for every sensitive workflow.

Applications may use:

```text
DRF throttling
django-ratelimit
Reverse proxy controls
WAF
Redis-based custom controls
```

Search:

```bash
rg -n -i \
'ratelimit|rate_limit|throttle|DEFAULT_THROTTLE|throttle_classes' \
--glob '*.py' \
.
```

---

# DRF Throttling

Search:

```bash
rg -n \
'DEFAULT_THROTTLE_CLASSES|DEFAULT_THROTTLE_RATES|throttle_classes' \
--glob '*.py' \
.
```

Prioritise:

```text
Login
Password reset
MFA
OTP
Registration
Verification
Expensive API calls
Exports
```

Do not conclude that rate limiting is absent from source alone because infrastructure may enforce it.

Refer to:

```text
docs/web/rate-limiting.md
```

---

# Django Admin

Search:

```bash
rg -n \
'admin\.site\.urls|admin\.site\.register|@admin\.register' \
--glob '*.py' \
.
```

Review:

```text
Admin exposure
Custom admin actions
Object permissions
Sensitive fields
Bulk actions
File operations
Custom HTML
```

---

# Admin Actions

Search:

```bash
rg -n \
'actions\s*=|@admin\.action' \
--glob '*.py' \
.
```

Administrative interfaces are trusted functionality, but security boundaries still matter.

---

# ModelAdmin HTML

Search:

```bash
rg -n \
'mark_safe\(|format_html\(' \
--glob 'admin.py' \
.
```

Admin interfaces can still contain stored XSS or unsafe HTML rendering.

---

# GraphQL

Django applications may use:

```text
Graphene-Django
Strawberry
Ariadne
```

Search:

```bash
rg -n -i \
'graphene|strawberry|ariadne|graphql|resolver|mutation' \
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
Query depth
Complexity
Batching
Introspection
```

Refer to:

```text
docs/web/graphql.md
```

---

# WebSockets / Django Channels

Search:

```bash
rg -n -i \
'channels|AsyncWebsocketConsumer|WebsocketConsumer|websocket|channel_layer' \
--glob '*.py' \
.
```

---

# Consumers

Example:

```python
class ChatConsumer(
    AsyncWebsocketConsumer
):
    async def receive(
        self,
        text_data,
    ):
        ...
```

Search:

```bash
rg -n \
'WebsocketConsumer|AsyncWebsocketConsumer|def receive|async def receive' \
--glob '*.py' \
.
```

Review:

```text
Connection authentication
Room/channel authorisation
Object access
Message authorisation
Origin validation
State-changing operations
```

Refer to:

```text
docs/web/websockets.md
```

---

# gRPC

Some Django systems communicate with gRPC services even when Django itself handles HTTP.

Search:

```bash
rg -n -i \
'grpc|Servicer|Stub\(' \
--glob '*.py' \
.
```

Review trust boundaries between:

```text
Django HTTP Application
        |
        v
gRPC Client
        |
        v
Internal Service
```

Do not assume internal RPC calls are inherently trusted.

Refer to:

```text
docs/web/grpc-security.md
```

---

# Background Jobs

Django commonly uses Celery.

Search:

```bash
rg -n -i \
'celery|shared_task|@.*\.task|\.delay\(|apply_async\(' \
--glob '*.py' \
.
```

---

# Second-Order Vulnerability Example

```text
POST /integrations/
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
        |
        v
SSRF
```

Do not stop tracing when attacker-controlled data is stored.

---

# Celery Task Arguments

Search:

```bash
rg -n \
'@shared_task|@.*\.task|\.delay\(|apply_async\(' \
--glob '*.py' \
.
```

Review whether task arguments originate from users.

---

# Secrets Exposure

Search:

```bash
rg -n -i \
'SECRET_KEY|password|passwd|secret|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|token|DATABASE_URL' \
.
```

---

# Database Credentials

Search:

```bash
rg -n \
'DATABASES\s*=|PASSWORD.*DATABASE|DATABASE_URL' \
--glob '*.py' \
.
```

Do not report placeholders or local development credentials as production secrets without evidence.

---

# Email Credentials

Search:

```bash
rg -n \
'EMAIL_HOST_USER|EMAIL_HOST_PASSWORD' \
--glob '*.py' \
.
```

---

# Cloud Credentials

Search:

```bash
rg -n -i \
'AWS_ACCESS_KEY|AWS_SECRET_ACCESS_KEY|AZURE_|GOOGLE_APPLICATION_CREDENTIALS' \
.
```

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
Django version
DRF version
Authentication packages
CORS packages
Image parsers
XML libraries
Serialization libraries
Database drivers
Cloud SDKs
```

---

# pip-audit

```bash
pip-audit
```

Against a requirements file:

```bash
pip-audit \
-r requirements.txt
```

---

# OSV-Scanner

```bash
osv-scanner scan source -r .
```

A vulnerable dependency version is a candidate finding.

Determine:

```text
Affected version?
Affected component used?
Vulnerable functionality reachable?
Attacker-controlled path?
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
TruffleHog
Gitleaks
```

---

# Semgrep

```bash
semgrep scan \
--config auto \
.
```

Use Semgrep to identify:

```text
Raw SQL
Command execution
Unsafe deserialization
Escaping bypasses
Hard-coded secrets
Dangerous request flows
```

Manual validation remains required.

---

# Bandit

```bash
bandit -r .
```

Exclude tests if appropriate:

```bash
bandit \
-r . \
-x ./tests
```

Bandit can help identify dangerous Python constructs, but Django-specific access-control and business-logic vulnerabilities still require manual review.

---

# CodeQL

CodeQL can assist with:

```text
Data flow
Taint tracking
Call graphs
Variant analysis
```

It is particularly useful for tracing:

```text
Request input
    |
    v
Multiple application layers
    |
    v
Dangerous sink
```

---

# Broad Django Security Search

```bash
rg -n \
'request\.(GET|POST|FILES|COOKIES|headers|META|body|data)|@login_required|LoginRequiredMixin|permission_required|PermissionRequiredMixin|AllowAny|permission_classes|has_object_permission|get_queryset|\.objects\.(get|filter|all)\(|\.raw\(|RawSQL\(|connection\.cursor\(|cursor\.execute\(|mark_safe\(|\|\s*safe\b|autoescape\s+off|@csrf_exempt|redirect\(|HttpResponseRedirect\(|requests\.(get|post|request)\(|httpx\.|\bopen\(|FileResponse\(|pickle\.(load|loads)\(|yaml\.(load|unsafe_load)\(|os\.system\(|subprocess\.|shell\s*=\s*True|eval\(|exec\(' \
--glob '*.py' \
--glob '*.html' \
.
```

This is a candidate-discovery search.

It is not a vulnerability scanner.

---

# Route Search

```bash
rg -n \
'urlpatterns|\bpath\(|\bre_path\(|include\(' \
--glob '*.py' \
.
```

---

# Authentication Search

```bash
rg -n \
'@login_required|LoginRequiredMixin|authenticate\(|request\.user|permission_required|PermissionRequiredMixin|is_staff|is_superuser' \
--glob '*.py' \
.
```

---

# Authorisation Search

```bash
rg -n -i \
'permission|owner|created_by|tenant|organization|organisation|role|is_staff|is_superuser' \
--glob '*.py' \
.
```

---

# DRF Security Search

```bash
rg -n \
'APIView|ViewSet|ModelViewSet|permission_classes|authentication_classes|AllowAny|IsAuthenticated|IsAdminUser|has_permission|has_object_permission|check_object_permissions|get_queryset|get_object|Serializer|ModelSerializer|read_only_fields' \
--glob '*.py' \
.
```

---

# SQL Search

```bash
rg -n \
'\.raw\(|RawSQL\(|connection\.cursor\(|cursor\.execute\(|cursor\.executemany\(|\.extra\(' \
--glob '*.py' \
.
```

---

# XSS Search

```bash
rg -n \
'mark_safe\(|SafeString|SafeData|format_html\(|\|\s*safe\b|autoescape\s+off' \
--glob '*.py' \
--glob '*.html' \
.
```

---

# CSRF Search

```bash
rg -n \
'csrf_exempt|csrf_protect|CsrfViewMiddleware|csrf_token|CSRF_TRUSTED_ORIGINS' \
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
'request\.FILES|FileField\(|ImageField\(|FileResponse\(|\bopen\(|Path\(|os\.path\.join\(|zipfile|tarfile|extractall\(' \
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

# Command Execution Search

```bash
rg -n \
'os\.(system|popen)\(|subprocess\.(run|Popen|call|check_call|check_output)\(|shell\s*=\s*True' \
--glob '*.py' \
.
```

---

# Configuration Search

```bash
rg -n \
'DEBUG|SECRET_KEY|ALLOWED_HOSTS|CSRF_|SESSION_|SECURE_|CORS_|USE_X_FORWARDED|SECURE_PROXY_SSL_HEADER|REST_FRAMEWORK' \
--glob '*.py' \
.
```

---

# Reverse Sink Analysis

For large Django applications, begin with dangerous sinks.

Example:

```text
requests.get()
      ^
      |
NotificationService
      ^
      |
Celery Task
      ^
      |
Integration Model
      ^
      |
POST /integrations/
```

High-value sinks:

```text
.raw()
RawSQL()
cursor.execute()

os.system()
subprocess.*

eval()
exec()

pickle.loads()
yaml.load()

requests.*
httpx.*

open()
FileResponse()

mark_safe()
Template()

redirect()
HttpResponseRedirect()
```

---

# Forward Source Analysis

Start from:

```text
request.GET
request.POST
request.FILES
request.COOKIES
request.headers
request.META
request.body

request.data

URL parameters
serializer.validated_data
form.cleaned_data
```

Trace forward:

```text
SOURCE
   |
   v
View
   |
   v
Form / Serializer
   |
   v
Service
   |
   v
Model
   |
   v
Task / Signal
   |
   v
SINK
```

---

# Source-to-Sink Example - IDOR

```text
GET /documents/123/
        |
        v
document_id
        |
        v
Document.objects.get(
    id=document_id
)
        |
        v
render()
```

Question:

```text
Where is ownership or tenant authorisation?
```

---

# Source-to-Sink Example - SQL Injection

```text
GET /search?q=admin
        |
        v
request.GET["q"]
        |
        v
f-string SQL
        |
        v
connection.cursor()
        |
        v
cursor.execute()
```

---

# Source-to-Sink Example - XSS

```text
POST /profile/
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

This is a second-order flow.

---

# Source-to-Sink Example - SSRF

```text
POST /preview/
        |
        v
request.POST["url"]
        |
        v
requests.get(url)
        |
        v
Outbound Network
```

---

# Source-to-Sink Example - Path Traversal

```text
GET /download/?file=...
        |
        v
request.GET["file"]
        |
        v
os.path.join(
    MEDIA_ROOT,
    filename
)
        |
        v
open()
        |
        v
FileResponse
```

---

# Source-to-Sink Example - Command Injection

```text
POST /diagnostics/
        |
        v
request.POST["host"]
        |
        v
f"ping -c 1 {host}"
        |
        v
subprocess.run(
    ...,
    shell=True
)
```

---

# Source-to-Sink Example - Mass Assignment

```text
PATCH /api/profile/
        |
        v
request.data
        |
        v
ModelSerializer
        |
        v
validated_data
        |
        v
Model fields
```

Review whether security-sensitive fields are writable.

---

# Source-to-Sink Example - Stored SSRF

```text
POST /webhooks/
        |
        v
Webhook URL
        |
        v
Model
        |
        v
Celery Task
        |
        v
requests.post()
```

---

# Variant Analysis

Once a confirmed vulnerability is identified, search for the root pattern throughout the project.

---

# IDOR Variant Analysis

If one view contains:

```python
Invoice.objects.get(
    id=invoice_id
)
```

search:

```bash
rg -n \
'\.objects\.get\(.*(id|pk)\s*=' \
--glob '*.py' \
.
```

Then manually review each object's authorisation model.

---

# Raw SQL Variant Analysis

```bash
rg -n \
'\.raw\(|RawSQL\(|cursor\.execute\(|\.extra\(' \
--glob '*.py' \
.
```

---

# XSS Variant Analysis

```bash
rg -n \
'mark_safe\(|\|\s*safe\b|autoescape\s+off' \
--glob '*.py' \
--glob '*.html' \
.
```

---

# CSRF Variant Analysis

```bash
rg -n \
'csrf_exempt' \
--glob '*.py' \
.
```

---

# SSRF Variant Analysis

```bash
rg -n \
'requests\.|httpx\.|urlopen\(' \
--glob '*.py' \
.
```

---

# Compare CRUD Controls

For every sensitive model compare:

```text
CREATE
READ
UPDATE
DELETE
```

Example:

```text
GET /documents/<id>/
    -> ownership check

PUT /documents/<id>/
    -> ownership check

DELETE /documents/<id>/
    -> only login_required
```

Inconsistent authorisation is a common source of vulnerabilities.

---

# Compare Web and API Controls

The same operation may exist in:

```text
Django HTML view
DRF API
Admin
Background task
GraphQL
WebSocket
```

Map them together:

```text
User Profile
    |
    +-- HTML View
    |
    +-- REST API
    |
    +-- Admin
    |
    +-- GraphQL
```

Compare security controls across every path.

---

# Source Code Review Matrix

| Vulnerability | High-Value Django Targets |
|---|---|
| Authentication | decorators, mixins, middleware, DRF authentication |
| Authorisation | permissions, queryset scoping, ownership |
| IDOR / BOLA | ORM lookups from URL/request IDs |
| SQL Injection | `raw`, `RawSQL`, cursor execution |
| LDAP Injection | custom LDAP filters |
| Command Injection | `subprocess`, `os.system` |
| SSTI | dynamic template source |
| XSS | `mark_safe`, `safe`, `autoescape off` |
| CSRF | `csrf_exempt`, middleware |
| CORS | django-cors-headers configuration |
| Open Redirect | `redirect`, `HttpResponseRedirect` |
| SSRF | `requests`, `httpx`, `urlopen` |
| Path Traversal | `open`, `FileResponse`, path construction |
| File Upload | `request.FILES`, `FileField`, storage |
| XXE | XML parser configuration |
| Deserialization | pickle, YAML, joblib |
| Mass Assignment | serializers, ModelForms, generic updates |
| Sessions | `SESSION_*`, `request.session` |
| Host Header | `get_host`, `build_absolute_uri` |
| Password Reset | reset views and custom tokens |
| MFA | OTP/recovery logic |
| OAuth/OIDC | callbacks and token validation |
| SAML | assertion validation |
| Information Disclosure | DEBUG, exceptions, logging |
| Race Conditions | transactions, locking |
| Rate Limiting | DRF throttling, django-ratelimit |
| Business Logic | model/service workflows |
| Cache Security | per-view caching, cache keys |
| GraphQL | resolvers and mutations |
| WebSockets | Channels consumers |
| Secrets | settings, `.env`, repository history |
| Dependencies | requirements/lock files |

---

# Django Review Checklist

## Project Discovery

```text
[ ] Django version identified
[ ] Production settings identified
[ ] Installed applications mapped
[ ] Middleware mapped
[ ] URL configurations mapped
[ ] Views mapped
[ ] Models mapped
[ ] Forms mapped
[ ] Serializers mapped
[ ] Background tasks mapped
[ ] Signals mapped
```

## Configuration

```text
[ ] DEBUG reviewed
[ ] SECRET_KEY reviewed
[ ] ALLOWED_HOSTS reviewed
[ ] MIDDLEWARE reviewed
[ ] SecurityMiddleware reviewed
[ ] Proxy trust reviewed
[ ] Session configuration reviewed
[ ] CSRF configuration reviewed
[ ] CORS configuration reviewed
[ ] Database configuration reviewed
```

## Authentication

```text
[ ] login_required reviewed
[ ] LoginRequiredMixin reviewed
[ ] permission_required reviewed
[ ] Custom decorators reviewed
[ ] DRF authentication reviewed
[ ] Password hashing reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
```

## Authorisation

```text
[ ] Object-level access reviewed
[ ] Ownership checks reviewed
[ ] Tenant isolation reviewed
[ ] Role checks reviewed
[ ] Admin checks reviewed
[ ] DRF permission classes reviewed
[ ] get_queryset() reviewed
[ ] get_object() reviewed
[ ] List endpoints reviewed
[ ] Create permissions reviewed
[ ] CRUD controls compared
```

## Input Validation

```text
[ ] Forms reviewed
[ ] ModelForms reviewed
[ ] Serializer fields reviewed
[ ] Serializer validation reviewed
[ ] Custom validators reviewed
[ ] Model validation reviewed
[ ] Security-sensitive fields identified
```

## Injection

```text
[ ] raw() reviewed
[ ] RawSQL reviewed
[ ] cursor.execute reviewed
[ ] extra() reviewed
[ ] LDAP filters reviewed
[ ] subprocess reviewed
[ ] shell=True reviewed
[ ] eval/exec reviewed
[ ] Dynamic templates reviewed
```

## Client-Side

```text
[ ] mark_safe reviewed
[ ] safe filters reviewed
[ ] autoescape off reviewed
[ ] JavaScript template contexts reviewed
[ ] Redirects reviewed
[ ] CORS reviewed
[ ] CSRF exemptions reviewed
[ ] Clickjacking exemptions reviewed
```

## Server-Side

```text
[ ] Outbound HTTP requests reviewed
[ ] File reads reviewed
[ ] File writes reviewed
[ ] FileResponse reviewed
[ ] Uploads reviewed
[ ] Archive extraction reviewed
[ ] XML parsing reviewed
[ ] Pickle/YAML reviewed
```

## APIs

```text
[ ] DRF authentication reviewed
[ ] DRF permissions reviewed
[ ] DRF object permissions reviewed
[ ] DRF serializers reviewed
[ ] DRF custom actions reviewed
[ ] DRF throttling reviewed
[ ] GraphQL reviewed
[ ] WebSockets reviewed
[ ] gRPC integrations reviewed
```

## Business Logic

```text
[ ] Prices reviewed
[ ] Balances reviewed
[ ] Discounts reviewed
[ ] Refunds reviewed
[ ] State transitions reviewed
[ ] Approval flows reviewed
[ ] Role changes reviewed
[ ] Tenant changes reviewed
[ ] Race conditions reviewed
```

## Secrets / Dependencies

```text
[ ] Hard-coded secrets searched
[ ] .env files reviewed
[ ] Git history considered
[ ] Requirements reviewed
[ ] Lock files reviewed
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

# Finding Validation

Before reporting:

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
FRAMEWORK PROTECTION?
    |
    +-- Effective --> Protected
    |
    v
AUTHORISATION?
    |
    +-- Effective --> Protected
    |
    v
EXPLOITABLE?
    |
    +-- No --> Contextual / defence-in-depth
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

# Example Finding - IDOR / BOLA

```text
Title:
Missing Object-Level Authorisation on Document Endpoint

Route:
GET /documents/<document_id>/

Source:
URL parameter document_id

Data Flow:

document_id
    |
    v
Document.objects.get(id=document_id)
    |
    v
Document
    |
    v
render()

Authentication:
@login_required

Authorisation:
No ownership or tenant restriction was identified.

Impact:
An authenticated user may be able to access documents belonging to another user by modifying the document identifier.

Recommendation:
Scope the object query to resources the authenticated principal is authorised to access or perform an equivalent object-level permission check.
```

---

# Example Finding - Stored XSS

```text
Title:
Stored Cross-Site Scripting Through Unsafe Template Rendering

Source:
Profile biography

Data Flow:

POST /profile/
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
Django's normal template escaping is explicitly bypassed by the safe filter.

Impact:
Attacker-controlled HTML may execute in the security context of users viewing the affected page, depending on the accepted content and browser context.

Recommendation:
Remove the safe filter for attacker-controlled content. If rich HTML is an application requirement, sanitise it using an appropriate allowlist-based HTML sanitisation strategy.
```

---

# Example Finding - SSRF

```text
Title:
Server-Side Request Forgery in URL Preview Endpoint

Route:
POST /preview/

Source:
request.POST["url"]

Data Flow:

request.POST["url"]
        |
        v
url
        |
        v
requests.get(url)

Security Control:
No effective destination restriction was identified.

Impact:
The server may make outbound requests to destinations selected by the user, potentially including internal services depending on network connectivity.

Recommendation:
Prefer server-controlled destinations. If user-selected external URLs are required, implement strict destination validation and network-level egress restrictions.
```

---

# Example Finding - Raw SQL Injection

```text
Title:
SQL Injection in User Search

Route:
GET /users/search/

Source:
request.GET["q"]

Data Flow:

request.GET["q"]
       |
       v
f-string SQL
       |
       v
connection.cursor()
       |
       v
cursor.execute()

Security Control:
No parameter binding was identified.

Recommendation:
Use the Django ORM where practical or pass attacker-controlled values as parameters to the database driver rather than constructing SQL syntax through string interpolation.
```

---

# Common Review Mistakes

## Django ORM Means the Entire Application Is Safe from SQL Injection

Incorrect.

The ORM substantially reduces SQL injection risk when used normally, but applications can still use:

```text
raw()
RawSQL()
cursor.execute()
extra()
```

and other custom query construction.

---

# login_required Means Authorisation Exists

Incorrect.

```text
@login_required
       |
       v
Authenticated
```

does not prove:

```text
Object ownership
Role permission
Tenant membership
Action permission
```

---

# get_object_or_404 Provides Authorisation

Incorrect.

```python
get_object_or_404(
    Invoice,
    id=invoice_id,
)
```

checks existence.

It does not inherently prove that the user may access the object.

---

# IsAuthenticated Prevents IDOR

Incorrect.

```python
permission_classes = [
    IsAuthenticated
]
```

means the user must be authenticated.

Object-level authorisation remains a separate concern.

---

# Serializer Validation Equals Authorisation

Incorrect.

A serializer may validate:

```text
Type
Length
Format
Allowed values
```

while still allowing a user to modify an object they do not own.

---

# Every AllowAny Is Vulnerable

Incorrect.

Public endpoints legitimately exist.

Determine the intended security policy.

---

# Every csrf_exempt Is Vulnerable

Incorrect.

Determine:

```text
Authentication mechanism
State change
Request context
Alternative verification
```

---

# Every mark_safe Is XSS

Incorrect.

Trace the value.

```text
Static trusted string
    !=
Attacker-controlled HTML
```

---

# Every requests.get Is SSRF

Incorrect.

Determine who controls the URL and what destination restrictions exist.

---

# Every FileField Is an Upload Vulnerability

Incorrect.

Review the complete upload lifecycle.

---

# Every DEBUG=True Match Is a Production Vulnerability

Incorrect.

Determine which configuration is deployed.

---

# Every Broad Queryset Is IDOR

Incorrect.

Review:

```text
Permissions
get_queryset()
Object permissions
Serializer behaviour
Endpoint type
```

---

# Final Django Review Model

```text
                         DJANGO APPLICATION
                                |
                                v
                              URLCONF
                                |
                                v
                              VIEW
                                |
          +---------------------+---------------------+
          |                     |                     |
          v                     v                     v
    request.GET           request.POST          request.data
          |                     |                     |
          +---------------------+---------------------+
                                |
                                v
                       FORM / SERIALIZER
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
          +---------------------+----------------------+
          |                     |                      |
          v                     v                      v
         ORM                 TEMPLATE               FILE
          |                     |                      |
          v                     v                      v
      Database              Browser               Filesystem

          +---------------------+----------------------+
          |                     |                      |
          v                     v                      v
     HTTP Client           subprocess             Celery
          |                     |                      |
          v                     v                      v
        SSRF             Command Injection       Second-Order
                                                   Flows
```

The core review question is:

```text
Can attacker-controlled data reach a security-sensitive Django or Python
operation without an effective framework, validation or authorisation boundary?
```

Evaluate:

```text
Source
+
Route
+
Authentication
+
Authorisation
+
Validation
+
Framework protection
+
Data flow
+
Sink
+
Exploitability
+
Impact
```

Only then classify the issue as a confirmed vulnerability.

---

# References

## Django Documentation

[docs.djangoproject.com](https://docs.djangoproject.com/){ target="_blank" rel="noopener noreferrer" }

## Django Security

[Django Security](https://docs.djangoproject.com/en/5.2/topics/security/){ target="_blank" rel="noopener noreferrer" }

## Django Security Policies

[Django Security Policies](https://docs.djangoproject.com/en/5.2/internals/security/){ target="_blank" rel="noopener noreferrer" }

## Django Settings

[Django Settings](https://docs.djangoproject.com/en/5.2/ref/settings/){ target="_blank" rel="noopener noreferrer" }

## Django Authentication

[Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/){ target="_blank" rel="noopener noreferrer" }

## Django CSRF Protection

[Django CSRF Protection](https://docs.djangoproject.com/en/5.2/ref/csrf/){ target="_blank" rel="noopener noreferrer" }

## Django Templates

[Django Templates](https://docs.djangoproject.com/en/5.2/topics/templates/){ target="_blank" rel="noopener noreferrer" }

## Django QuerySets

[Django QuerySets](https://docs.djangoproject.com/en/5.2/ref/models/querysets/){ target="_blank" rel="noopener noreferrer" }

## Performing Raw SQL Queries

[Performing Raw SQL Queries](https://docs.djangoproject.com/en/5.2/topics/db/sql/){ target="_blank" rel="noopener noreferrer" }

## Django File Uploads

[Django File Uploads](https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/){ target="_blank" rel="noopener noreferrer" }

## Django REST Framework

[Django REST Framework](https://www.django-rest-framework.org/){ target="_blank" rel="noopener noreferrer" }

## DRF Authentication

[DRF Authentication](https://www.django-rest-framework.org/api-guide/authentication/){ target="_blank" rel="noopener noreferrer" }

## DRF Permissions

[DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/){ target="_blank" rel="noopener noreferrer" }

## DRF Serializers

[DRF Serializers](https://www.django-rest-framework.org/api-guide/serializers/){ target="_blank" rel="noopener noreferrer" }

## DRF Throttling

[DRF Throttling](https://www.django-rest-framework.org/api-guide/throttling/){ target="_blank" rel="noopener noreferrer" }

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP ASVS

[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/){ target="_blank" rel="noopener noreferrer" }

## CWE

[CWE](https://cwe.mitre.org/){ target="_blank" rel="noopener noreferrer" }

## Semgrep

[Semgrep](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

## CodeQL for Python

[CodeQL for Python](https://codeql.github.com/docs/codeql-language-guides/codeql-for-python/){ target="_blank" rel="noopener noreferrer" }

## Bandit

[Bandit](https://bandit.readthedocs.io/){ target="_blank" rel="noopener noreferrer" }

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/dotnet.md
docs/source-code-review/java.md
docs/source-code-review/php.md
docs/source-code-review/python.md
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
