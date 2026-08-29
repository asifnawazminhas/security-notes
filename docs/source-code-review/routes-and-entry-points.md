# Routes and Entry Points

Finding every application entry point is one of the first and most important tasks during source code review.

Before analysing vulnerabilities, the reviewer needs to understand how attacker-controlled data can enter the application.

An entry point is any location where data, events, requests, or messages originating outside the current trust boundary cause application code to execute.

The obvious examples are HTTP routes:

```text
GET /api/users
POST /login
PUT /api/profile
DELETE /api/documents/{id}
```

However, modern applications frequently expose many other entry points:

```text
REST endpoints
GraphQL queries
GraphQL mutations
GraphQL subscriptions
gRPC methods
WebSocket messages
Webhooks
File uploads
File imports
Message queues
Background workers
Scheduled jobs
Serverless functions
CLI interfaces
Authentication callbacks
OAuth callbacks
SAML endpoints
Administrative interfaces
Internal APIs
Health and management endpoints
```

The objective is to create an attack-surface map that answers:

```text
What can cause this application to execute code?

What data can enter through that path?

Who can reach it?

What security controls protect it?

Where does the data go?
```

---

# Authorised Testing

Use these techniques only against source code, applications, systems, and environments that you are authorised to assess.

Source code may expose sensitive information including:

```text
Internal routes
Administrative functionality
Credentials
API keys
Infrastructure
Authentication logic
Authorisation logic
Debug functionality
Internal services
Undocumented APIs
```

Handle this information according to the rules of engagement.

---

# Why Route Discovery Matters

Dynamic testing only reveals functionality that can be discovered from the running application.

Source code review can reveal functionality that is:

```text
Undocumented
Hidden from navigation
Accessible only through APIs
Role-restricted
Feature-flagged
Environment-specific
Internal
Legacy
Partially deprecated
Called asynchronously
Triggered through another service
```

A source-assisted review therefore begins with:

```text
Repository
    |
    v
Application Structure
    |
    v
Entry Points
    |
    v
Routes
    |
    v
Inputs
    |
    v
Security Controls
    |
    v
Sensitive Operations
```

---

# Route Discovery Is Attack-Surface Discovery

Do not think of route discovery as merely finding URL strings.

The actual goal is:

```text
ENTRY POINT
     |
     +--> METHOD / PROTOCOL
     |
     +--> PATH / MESSAGE TYPE
     |
     +--> HANDLER
     |
     +--> INPUT
     |
     +--> AUTHENTICATION
     |
     +--> AUTHORISATION
     |
     +--> VALIDATION
     |
     +--> SENSITIVE OPERATION
```

For every discovered entry point, determine as much of this model as possible.

---

# Entry Point Categories

A useful classification is:

```text
Application Entry Points
|
+-- HTTP
|   |
|   +-- REST
|   +-- MVC
|   +-- Form handlers
|   +-- File upload
|   +-- Authentication
|   +-- Administrative
|
+-- API Protocols
|   |
|   +-- GraphQL
|   +-- gRPC
|   +-- WebSockets
|   +-- Server-Sent Events
|
+-- External Integrations
|   |
|   +-- Webhooks
|   +-- OAuth callbacks
|   +-- SAML endpoints
|   +-- Payment callbacks
|
+-- Asynchronous
|   |
|   +-- Message queues
|   +-- Event consumers
|   +-- Background workers
|   +-- Scheduled jobs
|
+-- Data Processing
|   |
|   +-- File uploads
|   +-- File imports
|   +-- Archive processing
|   +-- Document processing
|
+-- Operational
    |
    +-- Health endpoints
    +-- Metrics
    +-- Debug
    +-- Management
    +-- Internal APIs
```

---

# The Route Inventory

Create an inventory while reviewing.

Example:

| Method | Route | Handler | Authentication | Authorisation | Inputs | Notes |
|---|---|---|---|---|---|---|
| GET | `/api/users/{id}` | `getUser()` | Required | Ownership? | `id` | Review IDOR |
| POST | `/login` | `login()` | No | N/A | username/password | Authentication |
| POST | `/api/import` | `importFile()` | Required | Admin? | file | Upload/import |
| GET | `/preview` | `preview()` | Required | Unknown | `url` | SSRF candidate |
| POST | `/webhook/payment` | `paymentWebhook()` | Signature | N/A | JSON | Verify signature |

The inventory should evolve during the review.

---

# Entry Point Confidence

It can be useful to classify discovered routes:

```text
Confirmed
Potential
Disabled
Environment-specific
Unknown
```

For example:

```text
/admin/debug
```

may exist in source but only be enabled when:

```text
DEBUG=true
```

Do not automatically treat every route found in source as externally reachable.

---

# Route Reachability

For each route ask:

```text
Is it registered?

Is the controller instantiated?

Is the router mounted?

Is the feature enabled?

Is the module included?

Is it behind a reverse proxy?

Is it restricted by environment?

Is it restricted by network location?

Is authentication required?

Is authorisation required?
```

---

# Start With Repository Structure

Before searching individual routes, inspect the repository.

```bash
ls
```

and:

```bash
find . -maxdepth 2 -type d | sort
```

Look for directories such as:

```text
controllers
routes
api
handlers
views
services
resolvers
graphql
grpc
proto
websocket
webhooks
workers
jobs
tasks
consumers
middleware
security
auth
admin
internal
```

---

# Visual Studio Code

Open the repository:

```bash
code .
```

Use Visual Studio Code as the primary manual review environment.

Useful features:

```text
Explorer
Global Search
Regex Search
Go to Definition
Find All References
Call Hierarchy
Workspace Symbols
Integrated Terminal
Git Integration
Debugger
```

---

# Global Search

Use:

```text
Ctrl + Shift + F
```

to search across the repository.

Search for framework-specific route declarations and generic terms:

```text
route
router
controller
endpoint
handler
mapping
resolver
webhook
socket
consumer
listener
job
task
```

---

# ripgrep

ripgrep is extremely useful for initial route discovery.

General syntax:

```bash
rg -n 'pattern' .
```

Case-insensitive:

```bash
rg -n -i 'pattern' .
```

Search selected source files:

```bash
rg -n 'pattern' \
-g '*.java' \
-g '*.cs' \
-g '*.py' \
-g '*.php' \
-g '*.js' \
-g '*.ts' \
.
```

---

# ASP.NET Core

ASP.NET Core applications commonly expose endpoints through:

```text
Controllers
Minimal APIs
Razor Pages
SignalR hubs
gRPC services
Middleware
```

---

# ASP.NET Controller Discovery

Typical controller:

```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    [HttpGet("{id}")]
    public IActionResult GetUser(int id)
    {
        ...
    }
}
```

Result:

```text
GET /api/users/{id}
```

Search:

```bash
rg -n \
'\[(Route|HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch|HttpHead|HttpOptions)' \
-g '*.cs' \
.
```

---

# ASP.NET Route Attributes

Look for:

```text
[Route(...)]
[HttpGet(...)]
[HttpPost(...)]
[HttpPut(...)]
[HttpDelete(...)]
[HttpPatch(...)]
```

Example:

```csharp
[Route("api/admin")]
public class AdminController
{
    [HttpPost("users/{id}/disable")]
    ...
}
```

Combine controller and method routes:

```text
/api/admin
+
users/{id}/disable
=
POST /api/admin/users/{id}/disable
```

---

# ASP.NET Minimal APIs

Modern ASP.NET Core applications may use Minimal APIs.

Example:

```csharp
app.MapGet(
    "/api/users/{id}",
    GetUser
);

app.MapPost(
    "/api/users",
    CreateUser
);
```

Search:

```bash
rg -n \
'Map(Get|Post|Put|Delete|Patch|Methods|Group|Fallback)\(' \
-g '*.cs' \
.
```

Also search:

```bash
rg -n \
'MapControllers|MapRazorPages|MapHub|MapGrpcService' \
-g '*.cs' \
.
```

---

# ASP.NET Route Groups

Example:

```csharp
var api =
    app.MapGroup("/api");

var users =
    api.MapGroup("/users");

users.MapGet(
    "/{id}",
    GetUser
);
```

The final route is:

```text
GET /api/users/{id}
```

Do not inspect individual `MapGet()` calls without considering parent route groups.

---

# ASP.NET Authentication and Authorisation

Search:

```bash
rg -n \
'Authorize|AllowAnonymous|RequireAuthorization|AddAuthorization|AddAuthentication' \
-g '*.cs' \
.
```

Look for:

```text
[Authorize]
[AllowAnonymous]
RequireAuthorization()
Policies
Roles
Claims
```

Example:

```csharp
[Authorize]
[HttpGet("{id}")]
public IActionResult GetUser(int id)
```

Authentication is visible.

Object-level authorisation still needs separate review.

---

# ASP.NET Inputs

Sources include:

```text
Route values
Query strings
Headers
Cookies
Form values
JSON bodies
Uploaded files
```

Search:

```bash
rg -n \
'Request\.(Query|Form|Headers|Cookies)|IFormFile|FromBody|FromQuery|FromRoute|FromHeader|FromForm' \
-g '*.cs' \
.
```

---

# ASP.NET SignalR

SignalR exposes message-style entry points.

Search:

```bash
rg -n \
'Hub\b|MapHub|HubConnection|Clients\.' \
-g '*.cs' \
.
```

A public Hub method may effectively be an externally callable operation.

Review:

```text
Hub authentication
Method authorisation
Connection identity
Object-level authorisation
Input validation
```

---

# ASP.NET gRPC

Search:

```bash
rg -n \
'MapGrpcService|BindableService|ServerCallContext|override.*Task' \
-g '*.cs' \
.
```

Also inspect:

```text
.proto
```

files.

```bash
rg -n \
'^\s*(service|rpc)\s+' \
-g '*.proto' \
.
```

---

# Java / Spring

Spring applications commonly expose endpoints through:

```text
@RestController
@Controller
@RequestMapping
@GetMapping
@PostMapping
@PutMapping
@DeleteMapping
@PatchMapping
```

---

# Spring Controller Discovery

Example:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public User getUser(
        @PathVariable Long id
    ) {
        ...
    }
}
```

Final route:

```text
GET /api/users/{id}
```

Search:

```bash
rg -n \
'@(RestController|Controller|RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)' \
-g '*.java' \
-g '*.kt' \
.
```

---

# Spring Parent Mappings

Always combine:

```text
Class-level @RequestMapping
```

with:

```text
Method-level mapping
```

Example:

```java
@RequestMapping("/admin")
```

plus:

```java
@PostMapping("/users/{id}")
```

becomes:

```text
POST /admin/users/{id}
```

---

# Spring Request Inputs

Search:

```bash
rg -n \
'@(RequestParam|PathVariable|RequestBody|RequestHeader|CookieValue|RequestPart|ModelAttribute)' \
-g '*.java' \
.
```

Potential sources include:

```text
@RequestParam
@PathVariable
@RequestBody
@RequestHeader
@CookieValue
@RequestPart
@ModelAttribute
MultipartFile
HttpServletRequest
```

---

# Spring Security

Search:

```bash
rg -n \
'@(PreAuthorize|PostAuthorize|Secured|RolesAllowed)|authorizeHttpRequests|requestMatchers|permitAll|authenticated|hasRole|hasAuthority' \
-g '*.java' \
.
```

Review:

```text
Global route rules
Method security
Role checks
Permission checks
Object-level checks
```

---

# Spring Functional Routing

Not all Spring applications use controllers.

Spring WebFlux can use functional routes.

Search:

```bash
rg -n \
'RouterFunctions|route\(|GET\(|POST\(|PUT\(|DELETE\(' \
-g '*.java' \
-g '*.kt' \
.
```

---

# Spring Actuator

Search configuration for:

```text
management.endpoints
management.endpoint
management.server
```

Example:

```bash
rg -n \
'management\.(endpoints|endpoint|server)' \
.
```

Review exposure of management functionality.

Do not treat the presence of Actuator dependencies or configuration alone as proof that sensitive endpoints are externally accessible.

---

# Java Servlets

Legacy Java applications may use servlets.

Search:

```bash
rg -n \
'@WebServlet|extends HttpServlet|doGet\(|doPost\(|doPut\(|doDelete\(' \
-g '*.java' \
.
```

Also inspect:

```text
web.xml
```

for servlet mappings.

---

# PHP

PHP applications may use:

```text
Framework routers
Controller annotations
Route configuration files
Direct script endpoints
```

Direct `.php` files themselves may be entry points.

---

# PHP File Discovery

```bash
find . -type f -name '*.php' | sort
```

Look especially for:

```text
index.php
api.php
upload.php
login.php
admin.php
callback.php
webhook.php
download.php
```

Do not assume filenames alone determine exposure.

---

# Laravel

Laravel routes commonly appear in:

```text
routes/web.php
routes/api.php
routes/console.php
routes/channels.php
```

Search:

```bash
rg -n \
'Route::(get|post|put|patch|delete|options|any|match|resource|apiResource|group|prefix)' \
-g '*.php' \
.
```

Example:

```php
Route::get(
    '/users/{id}',
    [UserController::class, 'show']
);
```

---

# Laravel Route Groups

Example:

```php
Route::prefix('admin')
    ->middleware('auth')
    ->group(function () {

        Route::get(
            '/users',
            [AdminController::class, 'users']
        );
    });
```

Final route:

```text
GET /admin/users
```

with:

```text
auth middleware
```

Route groups must be included when mapping effective security controls.

---

# Laravel Middleware

Search:

```bash
rg -n \
'->middleware\(|middleware\(|Route::middleware|auth:|can:|Gate::|authorize\(' \
-g '*.php' \
.
```

Review:

```text
Authentication middleware
Authorisation middleware
Policies
Gates
Controller checks
Model ownership
```

---

# Symfony

Search:

```bash
rg -n \
'#\[Route|@Route|Routing\\Annotation\\Route' \
-g '*.php' \
.
```

Example:

```php
#[Route(
    '/users/{id}',
    methods: ['GET']
)]
```

Also inspect routing configuration files such as:

```text
config/routes.yaml
config/routes/
```

---

# Generic PHP Inputs

Search:

```bash
rg -n \
'\$_(GET|POST|REQUEST|FILES|COOKIE|SERVER)' \
-g '*.php' \
.
```

Sources include:

```text
$_GET
$_POST
$_REQUEST
$_FILES
$_COOKIE
$_SERVER
```

---

# Python

Python applications may expose routes through:

```text
Django
Flask
FastAPI
Starlette
aiohttp
Custom frameworks
```

---

# Django

Django commonly defines routes in:

```text
urls.py
```

Search:

```bash
rg -n \
'path\(|re_path\(|url\(|include\(' \
-g '*.py' \
.
```

Example:

```python
urlpatterns = [
    path(
        "users/<int:id>/",
        views.user_detail
    )
]
```

---

# Django Nested URL Configuration

Example:

```python
path(
    "api/",
    include("users.urls")
)
```

and inside:

```python
path(
    "users/<int:id>/",
    user_detail
)
```

Final route:

```text
/api/users/<id>/
```

Always follow `include()` chains.

---

# Django Views

Search:

```bash
rg -n \
'def (get|post|put|delete|patch)\(|class .*View|APIView|ViewSet|ModelViewSet|GenericAPIView' \
-g '*.py' \
.
```

Django REST Framework requires additional attention.

---

# Django REST Framework

Search:

```bash
rg -n \
'APIView|ViewSet|ModelViewSet|GenericViewSet|router\.register|DefaultRouter|SimpleRouter|@api_view|@action' \
-g '*.py' \
.
```

A router may automatically generate multiple routes.

Example:

```python
router.register(
    r"users",
    UserViewSet
)
```

may expose actions for:

```text
list
retrieve
create
update
partial_update
destroy
```

depending on the ViewSet.

---

# Django Authentication and Permissions

Search:

```bash
rg -n \
'permission_classes|authentication_classes|IsAuthenticated|AllowAny|IsAdminUser|has_permission|has_object_permission|login_required|permission_required' \
-g '*.py' \
.
```

Pay particular attention to:

```text
has_object_permission()
```

when reviewing IDOR/BOLA.

---

# Django Inputs

Typical sources:

```text
request.GET
request.POST
request.body
request.data
request.FILES
request.COOKIES
request.headers
```

Search:

```bash
rg -n \
'request\.(GET|POST|body|data|FILES|COOKIES|headers)' \
-g '*.py' \
.
```

---

# Flask

Flask routes commonly use:

```python
@app.route(...)
```

or:

```python
@blueprint.route(...)
```

Search:

```bash
rg -n \
'@(app|bp|blueprint|[A-Za-z_][A-Za-z0-9_]*)\.(route|get|post|put|delete|patch)\(' \
-g '*.py' \
.
```

---

# Flask Example

```python
@app.route(
    "/users/<int:id>",
    methods=["GET"]
)
def get_user(id):
    ...
```

Final route:

```text
GET /users/<id>
```

---

# Flask Blueprints

Example:

```python
api =
    Blueprint(
        "api",
        __name__,
        url_prefix="/api"
    )
```

Then:

```python
@api.route("/users")
def users():
    ...
```

Final route:

```text
/api/users
```

Review:

```text
Blueprint prefix
Application registration
Nested prefixes
```

---

# Flask Inputs

Search:

```bash
rg -n \
'request\.(args|form|json|files|cookies|headers|values|get_json)' \
-g '*.py' \
.
```

---

# Flask Authentication

Authentication may be implemented through:

```text
Decorators
before_request
Middleware
Flask-Login
JWT libraries
Custom wrappers
```

Search:

```bash
rg -n \
'login_required|current_user|before_request|jwt_required|roles_required|permission' \
-g '*.py' \
.
```

---

# FastAPI

FastAPI routes commonly use:

```python
@app.get(...)
@app.post(...)
@router.get(...)
@router.post(...)
```

Search:

```bash
rg -n \
'@(app|router)\.(get|post|put|delete|patch|options|head)\(' \
-g '*.py' \
.
```

---

# FastAPI Routers

Example:

```python
router =
    APIRouter(
        prefix="/users"
    )
```

and:

```python
@router.get("/{id}")
```

mounted with:

```python
app.include_router(
    router,
    prefix="/api"
)
```

Final route:

```text
GET /api/users/{id}
```

Multiple prefixes may need to be combined.

---

# Node.js / Express

Express applications commonly define routes through:

```text
app.get()
app.post()
router.get()
router.post()
```

Search:

```bash
rg -n \
'\.(get|post|put|delete|patch|options|head|all|use)\(' \
-g '*.js' \
-g '*.ts' \
.
```

This is intentionally broad and requires manual triage.

---

# Express Example

```javascript
router.get(
    "/users/:id",
    auth,
    getUser
);
```

Route:

```text
GET /users/:id
```

Middleware:

```text
auth
```

Handler:

```text
getUser
```

---

# Express Router Mounting

Example:

```javascript
app.use(
    "/api",
    userRouter
);
```

Inside:

```javascript
router.get(
    "/users/:id",
    getUser
);
```

Final route:

```text
GET /api/users/:id
```

Always follow router mounting.

---

# Express Inputs

Search:

```bash
rg -n \
'req\.(query|params|body|headers|cookies|file|files)' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Express Middleware

Routes may be protected through middleware.

Example:

```javascript
router.delete(
    "/users/:id",
    authenticate,
    requireAdmin,
    deleteUser
);
```

Map:

```text
DELETE /users/:id
        |
        +--> authenticate
        |
        +--> requireAdmin
        |
        +--> deleteUser
```

Do not only record the handler.

Record the middleware chain.

---

# NestJS

NestJS uses decorators similar to Spring.

Search:

```bash
rg -n \
'@(Controller|Get|Post|Put|Delete|Patch|Options|Head|UseGuards|UseInterceptors)' \
-g '*.ts' \
.
```

Example:

```typescript
@Controller("users")
export class UserController {

    @Get(":id")
    getUser() {
        ...
    }
}
```

Final route:

```text
GET /users/:id
```

---

# Next.js

Modern Next.js applications can expose server-side endpoints.

Review both:

```text
Pages Router
App Router
```

---

# Next.js Pages Router

Look under:

```text
pages/api/
```

Example:

```text
pages/api/users/[id].js
```

may map to:

```text
/api/users/{id}
```

Search:

```bash
find . \
-path '*/pages/api/*' \
-type f \
| sort
```

---

# Next.js App Router

Look for:

```text
app/**/route.js
app/**/route.ts
```

Search:

```bash
find . \
\( -name 'route.js' -o -name 'route.ts' \) \
-type f \
| sort
```

Inside route handlers:

```typescript
export async function GET(request) {
    ...
}

export async function POST(request) {
    ...
}
```

Search:

```bash
rg -n \
'export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Next.js Server Actions

Server Actions may also expose security-sensitive functionality indirectly from client interactions.

Search:

```bash
rg -n \
'["'\'']use server["'\'']' \
-g '*.js' \
-g '*.jsx' \
-g '*.ts' \
-g '*.tsx' \
.
```

Review:

```text
Authentication
Authorisation
Input validation
Object ownership
Sensitive operations
```

Do not assume a Server Action is safe merely because it is not a conventional REST endpoint.

---

# GraphQL

GraphQL attack surfaces are different from traditional REST.

The primary entry point may simply be:

```text
POST /graphql
```

but the real attack surface is:

```text
Queries
Mutations
Subscriptions
Resolvers
Fields
Arguments
```

---

# GraphQL Schema Discovery

Search:

```bash
rg -n \
'type Query|type Mutation|type Subscription|extend type Query|extend type Mutation' \
.
```

Also search:

```bash
find . \
\( -name '*.graphql' -o -name '*.gql' \) \
-type f \
| sort
```

---

# GraphQL Resolver Discovery

JavaScript/TypeScript:

```bash
rg -n \
'Query\s*:|Mutation\s*:|Subscription\s*:|Resolver|resolve\s*\(' \
-g '*.js' \
-g '*.ts' \
.
```

Python:

```bash
rg -n \
'resolve_|mutation|graphene|strawberry|ariadne' \
-g '*.py' \
.
```

Java:

```bash
rg -n \
'@QueryMapping|@MutationMapping|@SubscriptionMapping|@SchemaMapping|DataFetcher' \
-g '*.java' \
.
```

.NET:

```bash
rg -n \
'QueryType|MutationType|ObjectType|Resolver|GraphQL' \
-g '*.cs' \
.
```

---

# GraphQL Route Inventory

Do not record only:

```text
POST /graphql
```

Record operations:

| Type | Operation | Resolver | Authentication | Authorisation |
|---|---|---|---|---|
| Query | `user(id)` | `userResolver` | Required | Ownership? |
| Query | `documents` | `documentResolver` | Required | Tenant filter? |
| Mutation | `deleteUser(id)` | `deleteUserResolver` | Required | Admin? |
| Mutation | `updateRole(...)` | `roleResolver` | Required | Admin? |

---

# GraphQL Object-Level Authorisation

Trace:

```text
GraphQL Argument
      |
      v
Resolver
      |
      v
Object Lookup
      |
      v
Authorisation?
      |
      v
Return / Mutation
```

GraphQL frequently exposes BOLA-style issues when object-level checks are missing.

---

# gRPC

gRPC exposes services and RPC methods rather than conventional URL routes.

Start with `.proto` files.

```bash
find . -type f -name '*.proto' | sort
```

Search:

```bash
rg -n \
'^\s*(service|rpc)\s+' \
-g '*.proto' \
.
```

---

# gRPC Example

```protobuf
service UserService {

    rpc GetUser(
        GetUserRequest
    ) returns (
        UserResponse
    );

    rpc DeleteUser(
        DeleteUserRequest
    ) returns (
        DeleteUserResponse
    );
}
```

Inventory:

```text
UserService.GetUser
UserService.DeleteUser
```

---

# gRPC Security Review

For every RPC method determine:

```text
Request fields
Metadata
Authentication
Interceptors
Authorisation
Object-level checks
Input validation
Sensitive sinks
```

---

# gRPC Interceptors

Security may be implemented centrally.

Search for:

```text
Interceptor
ServerInterceptor
UnaryServerInterceptor
StreamServerInterceptor
```

Do not assume an interceptor provides object-level authorisation.

---

# WebSockets

WebSocket applications often expose only one connection endpoint:

```text
/ws
/socket
/socket.io
```

but many message handlers.

The actual attack surface is:

```text
Connection
    |
    +--> message type A
    +--> message type B
    +--> message type C
```

---

# WebSocket Search

JavaScript:

```bash
rg -n \
'WebSocket|socket\.on|io\.on|on\(["'\'']connection|on\(["'\'']message' \
-g '*.js' \
-g '*.ts' \
.
```

Python:

```bash
rg -n \
'websocket|WebSocket|receive_text|receive_json|send_text|send_json' \
-g '*.py' \
.
```

Java:

```bash
rg -n \
'@ServerEndpoint|WebSocketHandler|TextWebSocketHandler|WebSocketConfigurer' \
-g '*.java' \
.
```

.NET:

```bash
rg -n \
'WebSocket|MapHub|Hub\b' \
-g '*.cs' \
.
```

---

# WebSocket Message Inventory

Example:

```javascript
socket.on(
    "delete-document",
    async (id) => {
        ...
    }
);
```

Inventory:

```text
Protocol:
WebSocket

Event:
delete-document

Input:
id

Authentication:
Connection-level?

Authorisation:
Object ownership?
```

---

# WebSocket Authentication

Do not assume:

```text
Authenticated WebSocket
```

means:

```text
Every message is authorised
```

Review:

```text
Connection authentication
Session expiry
Token refresh
Per-message authorisation
Object-level authorisation
Tenant isolation
```

---

# Webhooks

Webhooks are externally triggered entry points.

Search:

```bash
rg -n -i \
'webhook|callback|hook|notification|event' \
.
```

Potential examples:

```text
/payment/webhook
/github/webhook
/stripe/webhook
/callback
/events
```

---

# Webhook Security Model

```text
External Service
      |
      v
Webhook Endpoint
      |
      v
Authenticity Verification
      |
      v
Payload Validation
      |
      v
Business Operation
```

Review:

```text
Signature verification
Shared secret
Timestamp validation
Replay protection
Content validation
Event type validation
Idempotency
```

---

# Webhook Verification Ordering

Important:

```text
Webhook Request
      |
      v
Signature Verification
      |
      v
Processing
```

Potentially dangerous:

```text
Webhook Request
      |
      v
Sensitive Processing
      |
      v
Signature Verification
```

---

# OAuth Callbacks

Search:

```bash
rg -n -i \
'oauth|oidc|callback|redirect_uri|authorization_code|code_verifier|state|nonce' \
.
```

Identify routes such as:

```text
/oauth/callback
/auth/callback
/login/oauth2/code/*
```

Review:

```text
state
nonce
PKCE
redirect handling
token validation
identity mapping
session creation
```

---

# SAML Endpoints

Search:

```bash
rg -n -i \
'saml|acs|assertionconsumer|metadata|singlelogout|sso' \
.
```

Potential entry points:

```text
ACS endpoint
SSO endpoint
SLO endpoint
Metadata endpoint
```

---

# File Upload Entry Points

Search:

```bash
rg -n -i \
'upload|multipart|IFormFile|MultipartFile|request\.files|req\.files|multer|UploadedFile' \
.
```

Record:

```text
Route
Accepted file type
Filename handling
Storage destination
Parser
Post-processing
Authentication
Authorisation
```

---

# File Import Entry Points

Uploads and imports should be distinguished.

An import may trigger:

```text
CSV parsing
XML parsing
Spreadsheet parsing
Archive extraction
PDF processing
Image processing
Object deserialisation
```

Search:

```bash
rg -n -i \
'import|parse|csv|xlsx|xml|zip|archive|pdf' \
.
```

Manual triage is required because these terms are broad.

---

# Message Queues

Applications may receive attacker-influenced data asynchronously.

Technologies include:

```text
RabbitMQ
Kafka
AWS SQS
Azure Service Bus
Google Pub/Sub
Redis queues
Celery
BullMQ
MassTransit
Spring Kafka
```

---

# Queue Consumer Discovery

Search broadly:

```bash
rg -n -i \
'consumer|listener|subscriber|subscribe|queue|kafka|rabbit|sqs|servicebus|pubsub|celery|bullmq|masstransit' \
.
```

---

# Spring Queue Consumers

Search:

```bash
rg -n \
'@(KafkaListener|RabbitListener|JmsListener|SqsListener)' \
-g '*.java' \
.
```

Example:

```java
@KafkaListener(
    topics = "documents"
)
public void process(
    String message
) {
    ...
}
```

The queue message is an entry point.

---

# Celery

Search:

```bash
rg -n \
'@.*task|@shared_task|Celery\(' \
-g '*.py' \
.
```

Example:

```python
@shared_task
def process_document(path):
    ...
```

Then determine who can cause the task to be queued and whether task arguments can contain attacker-controlled data.

---

# Bull / BullMQ

Search:

```bash
rg -n \
'new Worker|new Queue|process\(|bullmq|bull' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Background Jobs

Background jobs may process previously stored attacker-controlled data.

Example:

```text
HTTP Request
     |
     v
Database
     |
     v
Background Worker
     |
     v
Dangerous Sink
```

This is an important second-order path.

---

# Scheduled Jobs

Search:

```bash
rg -n -i \
'cron|schedule|scheduled|scheduler|timer|periodic' \
.
```

Framework-specific examples follow.

---

# Spring Scheduled Jobs

```bash
rg -n \
'@Scheduled' \
-g '*.java' \
.
```

---

# .NET Background Services

Search:

```bash
rg -n \
'BackgroundService|IHostedService|ExecuteAsync|AddHostedService' \
-g '*.cs' \
.
```

---

# Python Scheduled Jobs

Search:

```bash
rg -n -i \
'celerybeat|apscheduler|schedule\.|crontab|periodic_task' \
-g '*.py' \
.
```

---

# Node Scheduled Jobs

Search:

```bash
rg -n -i \
'node-cron|cron\.schedule|setInterval|agenda|bullmq' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Serverless Functions

Applications may expose:

```text
AWS Lambda
Azure Functions
Google Cloud Functions
Cloudflare Workers
Vercel Functions
```

Search for platform configuration.

---

# AWS Lambda

Look for:

```text
serverless.yml
serverless.yaml
template.yaml
samconfig.toml
```

Search:

```bash
rg -n -i \
'handler:|events:|httpApi:|http:|schedule:|sqs:|sns:|s3:' \
-g '*.yml' \
-g '*.yaml' \
.
```

---

# Azure Functions

Search:

```bash
find . -name 'function.json' -o -name 'host.json'
```

Also search:

```bash
rg -n \
'HttpTrigger|QueueTrigger|TimerTrigger|BlobTrigger|ServiceBusTrigger' \
.
```

---

# Serverless Trigger Types

A function may be triggered by:

```text
HTTP
Queue
Object upload
Database event
Timer
Message topic
Authentication event
```

All relevant triggers belong in the entry-point map.

---

# CLI Entry Points

Some web application repositories include administrative CLI tools.

Search:

```bash
rg -n \
'argparse|click\.command|commander|yargs|CommandLineRunner|ICommand|Main\(' \
.
```

CLI interfaces may be relevant when:

```text
User-controlled data is passed into them indirectly
Web functionality invokes them
Background jobs invoke them
Operators process untrusted files
```

---

# Internal APIs

Routes named:

```text
/internal
/private
/service
/admin
/management
/debug
```

should receive additional attention.

But naming does not prove exposure.

Determine:

```text
Network restriction
Authentication
Authorisation
Reverse proxy routing
Environment configuration
```

---

# Administrative Routes

Search:

```bash
rg -n -i \
'admin|administrator|management|manage|internal|debug' \
.
```

Review actions such as:

```text
Create user
Delete user
Change role
Impersonate user
Reset MFA
Generate token
Change configuration
Run diagnostics
Import data
Export data
```

---

# Debug Endpoints

Search:

```bash
rg -n -i \
'debug|diagnostic|trace|testendpoint|devonly|development' \
.
```

Also inspect conditional configuration:

```text
DEBUG
ENVIRONMENT
NODE_ENV
ASPNETCORE_ENVIRONMENT
SPRING_PROFILES_ACTIVE
FLASK_ENV
DJANGO_DEBUG
```

---

# Health and Metrics

Search:

```bash
rg -n -i \
'health|metrics|prometheus|actuator|status|ready|readiness|live|liveness' \
.
```

These endpoints are not automatically vulnerabilities.

Review whether they expose sensitive operational information or privileged functionality.

---

# Feature Flags

Feature flags may expose hidden routes.

Search:

```bash
rg -n -i \
'feature.?flag|featureflag|isEnabled|enabledFeatures|toggle' \
.
```

Map:

```text
Route
   |
   v
Feature Flag
   |
   v
Handler
```

Determine whether the feature is active in the target environment.

---

# Environment-Specific Routes

Example:

```javascript
if (
    process.env.NODE_ENV !== "production"
) {
    app.use(
        "/debug",
        debugRouter
    );
}
```

Record:

```text
/debug
```

as:

```text
Environment-specific
```

rather than automatically exposed.

---

# Middleware Mapping

Route discovery without middleware mapping is incomplete.

Example:

```text
POST /admin/users
        |
        +--> authenticate
        |
        +--> csrfProtection
        |
        +--> requireAdmin
        |
        +--> validateBody
        |
        +--> createUser
```

This is much more useful than:

```text
POST /admin/users -> createUser
```

---

# Global Middleware

Security controls may apply before routes.

Examples:

```text
Authentication
CSRF
CORS
Rate limiting
Security headers
Tenant resolution
Request validation
Logging
```

Identify global middleware.

---

# Express Global Middleware

Example:

```javascript
app.use(authenticate);
app.use(apiRouter);
```

Every route mounted after the authentication middleware may inherit it.

Ordering matters.

---

# ASP.NET Middleware Ordering

Review:

```text
UseRouting
UseAuthentication
UseAuthorization
MapControllers
```

Security middleware ordering can affect behaviour.

Do not infer a vulnerability solely from unusual ordering without confirming framework semantics and runtime behaviour.

---

# Spring Security Filter Chain

Look for:

```text
SecurityFilterChain
HttpSecurity
requestMatchers
authorizeHttpRequests
```

Map route rules such as:

```text
/admin/** -> ADMIN
/api/**   -> authenticated
/public/** -> permitAll
```

Then compare those rules against discovered routes.

---

# Route-Level vs Object-Level Authorisation

A route may correctly require:

```text
Authenticated user
```

but still fail object-level authorisation.

Example:

```text
GET /api/documents/{id}
       |
       v
Authenticated
       |
       v
DocumentRepository.findById(id)
       |
       v
Return Document
```

Missing:

```text
Does this document belong to the user?
```

---

# Route Parameters

Examples:

```text
/users/{id}
/documents/:id
/accounts/<account_id>
/tenant/{tenantId}/users/{userId}
```

These should immediately trigger review for:

```text
IDOR
BOLA
Tenant isolation
Authorisation
```

---

# Sensitive Parameter Names

Search route and request definitions for:

```text
id
userId
accountId
documentId
tenantId
organisationId
role
permission
admin
owner
url
path
file
filename
redirect
callback
command
query
template
```

These names are only review indicators.

They are not findings.

---

# Route-to-Sink Mapping

After discovering a route:

```text
ROUTE
  |
  v
HANDLER
  |
  v
SERVICE
  |
  v
REPOSITORY / HELPER
  |
  v
SINK
```

Example:

```text
GET /preview
     |
     v
PreviewController
     |
     v
PreviewService
     |
     v
HttpClient.get()
```

Potential review category:

```text
SSRF
```

---

# Route-to-Sink Example

```python
@app.get("/preview")
def preview():

    url =
        request.args.get("url")

    return preview_service.fetch(url)
```

Service:

```python
def fetch(url):
    return requests.get(url).text
```

Map:

```text
GET /preview
      |
      v
request.args["url"]
      |
      v
preview_service.fetch()
      |
      v
requests.get()
```

---

# Route-to-Authorisation Mapping

Example:

```text
DELETE /api/users/{id}
        |
        v
authenticate()
        |
        v
deleteUser(id)
        |
        v
UserRepository.delete(id)
```

Ask:

```text
Where is administrative permission checked?

Where is object-level authorisation checked?
```

---

# Route-to-Validation Mapping

Example:

```text
POST /api/import
      |
      v
Multipart Upload
      |
      v
validateFile()
      |
      v
parseDocument()
```

Record both:

```text
Source
Security control
Sink
```

---

# Build an Attack Surface Table

A useful working table:

| Entry Point | Type | Input | AuthN | AuthZ | Sensitive Sink | Review |
|---|---|---|---|---|---|---|
| `/login` | HTTP | credentials | No | N/A | Session creation | Auth |
| `/users/{id}` | REST | `id` | Yes | Unknown | DB read | IDOR |
| `/preview` | REST | `url` | Yes | N/A | HTTP client | SSRF |
| `deleteUser` | GraphQL mutation | `id` | Yes | Unknown | DB delete | BOLA |
| `DeleteUser` | gRPC | request ID | Yes | Unknown | DB delete | AuthZ |
| `delete-document` | WebSocket | ID | Yes | Unknown | DB delete | AuthZ |
| `/payment/webhook` | Webhook | JSON | Signature | N/A | Payment update | Webhook |

---

# Hidden Entry Points

Pay additional attention to:

```text
Legacy controllers
Unused-looking routes
Test endpoints
Debug handlers
Administrative endpoints
Internal APIs
Alternative API versions
Old GraphQL mutations
Deprecated RPC methods
Unused WebSocket events
Migration endpoints
Import/export functions
```

---

# API Versioning

Search:

```bash
rg -n \
'/v[0-9]+/|api/v[0-9]+|version' \
.
```

Applications may simultaneously expose:

```text
/api/v1/
/api/v2/
/api/v3/
```

Older versions may have weaker security controls.

Do not assume deprecated routes remain externally accessible.

Verify reachability.

---

# Duplicate Functionality

Look for the same operation through multiple entry points.

Example:

```text
REST:
DELETE /api/users/{id}

GraphQL:
deleteUser(id)

gRPC:
UserService.DeleteUser()

Admin:
POST /admin/delete-user
```

Security controls should be consistent across all paths.

---

# Alternate Entry Point Analysis

This is extremely important.

A secure operation may exist through one path:

```text
REST
 |
 v
Authentication
 |
 v
Authorisation
 |
 v
Sensitive Operation
```

while another path may expose:

```text
GraphQL
 |
 v
Authentication
 |
 v
Sensitive Operation
```

with missing authorisation.

---

# Security Control Consistency

For every sensitive operation ask:

```text
How many ways can this operation be reached?
```

Then compare:

```text
Authentication
Authorisation
Validation
Rate limiting
Audit logging
CSRF
Business rules
```

---

# Authentication Endpoint Inventory

Search for:

```text
login
signin
authenticate
token
session
logout
refresh
password
reset
forgot
mfa
2fa
otp
verify
```

Example:

```bash
rg -n -i \
'login|signin|authenticate|logout|refresh|forgot.?password|reset.?password|mfa|2fa|otp' \
.
```

Map all identity-related entry points separately.

---

# Account Creation

Search:

```bash
rg -n -i \
'register|signup|sign.?up|create.?account|invite' \
.
```

Review:

```text
Role assignment
Email verification
Tenant assignment
Invitation handling
Duplicate accounts
Mass assignment
```

---

# Password Reset

Search:

```bash
rg -n -i \
'forgot.?password|reset.?password|password.?reset|reset.?token' \
.
```

Map:

```text
Request reset
Generate token
Deliver token
Validate token
Change password
Invalidate token
```

---

# MFA

Search:

```bash
rg -n -i \
'mfa|2fa|totp|otp|authenticator|recovery.?code|backup.?code' \
.
```

Entry points may include:

```text
Enable MFA
Disable MFA
Verify MFA
Generate recovery codes
Use recovery code
Reset MFA
```

---

# OAuth / OIDC

Search:

```bash
rg -n -i \
'oauth|openid|oidc|callback|redirect_uri|state|nonce|pkce|code_verifier' \
.
```

Map:

```text
Login initiation
Callback
Token exchange
Account linking
Logout
Refresh
```

---

# SAML

Search:

```bash
rg -n -i \
'saml|assertion|acs|single.?sign.?on|single.?logout|metadata' \
.
```

---

# API Key Entry Points

Search:

```bash
rg -n -i \
'api.?key|x-api-key|apikey' \
.
```

Determine which routes support:

```text
Session authentication
JWT
API keys
mTLS
Internal service tokens
```

Different authentication mechanisms may produce different authorisation paths.

---

# Host and Proxy-Dependent Routes

Review routing logic that depends on:

```text
Host
X-Forwarded-Host
X-Forwarded-Proto
X-Forwarded-Prefix
Tenant hostname
Subdomain
```

Search:

```bash
rg -n -i \
'host|hostname|x-forwarded-host|x-forwarded-proto|subdomain|tenant' \
.
```

Manual triage is essential because these terms are broad.

---

# Multi-Tenant Routing

Applications may derive tenant context from:

```text
Hostname
Route
Header
JWT claim
Session
Database lookup
```

Example:

```text
/{tenantId}/documents/{id}
```

Map:

```text
Attacker tenant identifier
        |
        v
Tenant resolution
        |
        v
Object lookup
        |
        v
Tenant authorisation
```

---

# Route Discovery Through Tests

Tests often reveal hidden routes.

Search:

```bash
find . \
\( -path '*test*' -o -path '*spec*' \) \
-type f \
| sort
```

Look for:

```text
GET
POST
PUT
DELETE
PATCH
/graphql
/api/
admin
login
```

Tests may document expected security behaviour.

---

# Route Discovery Through OpenAPI

Search:

```bash
find . \
\( \
-name 'openapi*.json' -o \
-name 'openapi*.yaml' -o \
-name 'openapi*.yml' -o \
-name 'swagger*.json' -o \
-name 'swagger*.yaml' -o \
-name 'swagger*.yml' \
\) \
-type f
```

OpenAPI specifications can reveal:

```text
Routes
Methods
Parameters
Schemas
Authentication schemes
Deprecated endpoints
```

---

# Swagger Configuration

Search:

```bash
rg -n -i \
'swagger|openapi|springdoc|swashbuckle' \
.
```

Do not assume Swagger UI is externally exposed simply because the dependency exists.

---

# GraphQL Schema Files

```bash
find . \
\( -name '*.graphql' -o -name '*.gql' \) \
-type f \
| sort
```

These can provide an extremely accurate map of the GraphQL attack surface.

---

# Proto Files

```bash
find . \
-name '*.proto' \
-type f \
| sort
```

These provide the primary gRPC service map.

---

# Infrastructure Configuration

Routes may also appear in:

```text
nginx.conf
Apache configuration
Ingress resources
API gateways
Terraform
Kubernetes manifests
Reverse proxy configuration
Cloud routing configuration
```

Search:

```bash
rg -n -i \
'location |proxy_pass|ingress|path:|route|gateway|rewrite|upstream' \
.
```

---

# Reverse Proxy Paths

Example:

```text
External:
/service/users

Reverse Proxy:
rewrite -> /users

Application:
/users
```

The source-code route may differ from the externally visible route.

Record both where known.

---

# Kubernetes Ingress

Search:

```bash
rg -n \
'kind:\s*Ingress|path:|pathType:|backend:' \
-g '*.yaml' \
-g '*.yml' \
.
```

This can reveal externally routed application paths.

---

# API Gateways

Search for configuration relating to:

```text
AWS API Gateway
Kong
Traefik
NGINX
Azure API Management
Apigee
Envoy
```

These may provide:

```text
Authentication
Rate limiting
Path rewriting
Header modification
Network restrictions
```

Do not assume application-level exposure without considering these controls.

---

# Frontend Route Discovery

Client-side code can reveal server endpoints.

Search:

```bash
rg -n \
'fetch\(|axios\.|XMLHttpRequest|\.ajax\(|/api/' \
-g '*.js' \
-g '*.jsx' \
-g '*.ts' \
-g '*.tsx' \
.
```

This is useful for identifying:

```text
Undocumented APIs
Parameter names
HTTP methods
GraphQL operations
WebSocket endpoints
```

---

# JavaScript API Calls

Example:

```javascript
axios.delete(
    `/api/users/${userId}`
);
```

This reveals:

```text
DELETE /api/users/{userId}
```

even before the server implementation is found.

---

# Source Maps

Where source maps are available during an authorised assessment, they may help map frontend functionality to original source.

Review:

```text
API clients
Route definitions
Feature flags
Administrative functionality
GraphQL queries
WebSocket events
```

Source map availability alone is not automatically a vulnerability.

---

# Dynamic Route Validation

After building the source map, compare it with the running application.

Use Burp Suite:

```text
Proxy
HTTP history
Site map
Repeater
Logger
```

Compare:

```text
Source Routes
     |
     v
Runtime Routes
```

---

# Source vs Runtime

Classify:

```text
Source + Runtime
    = Confirmed exposed route

Source only
    = Investigate reachability

Runtime only
    = Find implementation / proxy mapping
```

---

# Burp Suite Workflow

For each interesting route:

```text
1. Find route in source.

2. Determine expected HTTP method.

3. Determine parameters.

4. Determine expected authentication.

5. Capture a legitimate request where possible.

6. Send to Repeater.

7. Compare runtime behaviour with source.

8. Test security controls within scope.

9. Map the route to relevant source-to-sink flows.
```

---

# Do Not Blindly Request Every Route

Source review may reveal:

```text
Destructive administrative actions
Account deletion
Payment actions
Production integrations
Bulk operations
```

Understand the route before testing it dynamically.

Use safe testing procedures appropriate to the engagement.

---

# Semgrep / OpenGrep

Static analysis can automate framework-specific route discovery.

Conceptual example:

```yaml
rules:
  - id: flask-route
    languages:
      - python
    message: Flask route
    severity: INFO
    pattern: |
      @$APP.route($PATH, ...)
      def $FUNC(...):
        ...
```

This can produce an initial route candidate list.

---

# Route Rules as Reconnaissance Rules

Static-analysis rules can identify:

```text
Controllers
Route decorators
Anonymous routes
Admin routes
Upload handlers
Webhooks
GraphQL resolvers
Dangerous route/sink combinations
```

Example conceptual target:

```text
HTTP Route
   +
Command Execution
```

---

# CodeQL

CodeQL becomes useful when route-to-sink analysis requires deeper semantic tracing.

Conceptually:

```text
HTTP Source
     |
     v
Controller
     |
     v
Service
     |
     v
Repository / Helper
     |
     v
Sensitive Sink
```

Queries can model:

```text
Request sources
Framework routes
Data flow
Taint tracking
Sensitive sinks
```

---

# Route Discovery Is Not Vulnerability Discovery

Remember:

```text
Interesting Route
      !=
Vulnerability
```

Likewise:

```text
/admin route
      !=
Broken Access Control
```

and:

```text
/debug route
      !=
Information Disclosure
```

and:

```text
/upload route
      !=
File Upload Vulnerability
```

The route identifies where deeper analysis should occur.

---

# Prioritising Routes

After mapping routes, prioritise security-sensitive functionality.

A useful review order is:

```text
1. Authentication

2. Password reset

3. MFA

4. Administrative functionality

5. Role / permission changes

6. User and tenant management

7. File upload / import

8. URL fetching / previews

9. Command / diagnostics functionality

10. Financial / transactional actions

11. Object access by identifier

12. GraphQL mutations

13. gRPC write operations

14. WebSocket state-changing messages

15. Webhooks

16. Internal / debug endpoints
```

This is a review-priority model, not a severity ranking.

---

# High-Value Route Names

Search for terms such as:

```text
admin
internal
debug
diagnostic
execute
command
shell
upload
import
export
download
preview
fetch
proxy
callback
webhook
reset
password
mfa
role
permission
invite
token
secret
key
config
backup
restore
delete
update
transfer
payment
refund
```

---

# Route Security Matrix

A useful matrix:

| Route | AuthN | AuthZ | Validation | Rate Limit | CSRF | Audit |
|---|---:|---:|---:|---:|---:|---:|
| `/login` | N/A | N/A | Yes | ? | N/A | ? |
| `/password/reset` | N/A | N/A | Yes | ? | N/A | ? |
| `/api/users/{id}` | Yes | ? | Yes | ? | N/A | ? |
| `/admin/users` | Yes | Admin | Yes | ? | ? | Yes |
| `/upload` | Yes | Yes | ? | ? | ? | ? |

The `?` values become review tasks.

---

# Route Mapping Worksheet

Use a repeatable format.

```text
Route ID:
RT-001

Protocol:
HTTP

Method:
GET

External Path:
/api/users/{id}

Internal Path:
/users/{id}

Handler:
UserController.getUser()

Source File:
src/controllers/UserController.java

Inputs:
id

Authentication:
Required

Authorisation:
Unknown

Validation:
Integer conversion

Rate Limiting:
Unknown

CSRF:
N/A

Sensitive Operation:
UserRepository.findById()

Potential Review:
IDOR / BOLA

Reachability:
Confirmed

Notes:
...
```

---

# Non-HTTP Worksheet

```text
Entry Point ID:
EP-017

Protocol:
WebSocket

Connection:
/ws

Message:
delete-document

Handler:
deleteDocument()

Input:
documentId

Authentication:
Connection requires session

Authorisation:
Unknown

Sensitive Operation:
DocumentService.delete()

Potential Review:
Object-level authorisation

Reachability:
Confirmed / Unknown

Notes:
...
```

---

# gRPC Worksheet

```text
Entry Point ID:
GRPC-003

Service:
UserService

Method:
DeleteUser

Input:
DeleteUserRequest.id

Handler:
UserServiceImpl.deleteUser()

Authentication:
Interceptor

Authorisation:
Unknown

Sink:
UserRepository.delete()

Potential Review:
BOLA / privilege enforcement

Reachability:
Unknown
```

---

# Webhook Worksheet

```text
Entry Point ID:
WH-002

Path:
/webhooks/payment

Method:
POST

Authentication:
Webhook signature

Replay Protection:
Unknown

Input:
JSON event

Handler:
PaymentWebhook.handle()

Sensitive Operation:
Payment status update

Potential Review:
Signature verification
Replay protection
Business logic
Idempotency
```

---

# Entry Point Coverage

At the end of route discovery, ask whether each category has been considered.

```text
HTTP
REST
GraphQL
gRPC
WebSockets
Webhooks
Queues
Workers
Scheduled jobs
File processing
Serverless functions
Authentication callbacks
Administrative interfaces
Internal interfaces
Operational endpoints
```

---

# Route Discovery Checklist

## Repository

```text
[ ] Repository structure reviewed
[ ] Application framework identified
[ ] Multiple applications identified
[ ] Frontend and backend separated
[ ] Microservices identified
[ ] Infrastructure configuration reviewed
```

## HTTP

```text
[ ] Controllers mapped
[ ] Route decorators mapped
[ ] Minimal APIs mapped
[ ] Router files mapped
[ ] Route groups mapped
[ ] Parent prefixes mapped
[ ] HTTP methods recorded
[ ] Parameters recorded
```

## Authentication

```text
[ ] Login endpoints mapped
[ ] Logout endpoints mapped
[ ] Session endpoints mapped
[ ] Token endpoints mapped
[ ] Refresh endpoints mapped
[ ] Password reset mapped
[ ] MFA endpoints mapped
[ ] OAuth callbacks mapped
[ ] SAML endpoints mapped
```

## Authorisation

```text
[ ] Route-level authorisation mapped
[ ] Role checks mapped
[ ] Permission checks mapped
[ ] Object-level checks identified
[ ] Tenant checks identified
[ ] Anonymous routes identified
```

## APIs

```text
[ ] REST endpoints mapped
[ ] GraphQL queries mapped
[ ] GraphQL mutations mapped
[ ] GraphQL subscriptions mapped
[ ] gRPC services mapped
[ ] gRPC methods mapped
[ ] WebSocket handlers mapped
```

## Asynchronous Entry Points

```text
[ ] Queue consumers mapped
[ ] Event listeners mapped
[ ] Background workers mapped
[ ] Scheduled jobs mapped
[ ] Serverless triggers mapped
```

## External Integrations

```text
[ ] Webhooks mapped
[ ] Payment callbacks mapped
[ ] OAuth callbacks mapped
[ ] SAML callbacks mapped
[ ] Third-party event handlers mapped
```

## Files

```text
[ ] Upload endpoints mapped
[ ] Import endpoints mapped
[ ] Download endpoints mapped
[ ] Archive processing mapped
[ ] Document processing mapped
```

## Operational

```text
[ ] Admin routes mapped
[ ] Internal routes mapped
[ ] Debug routes mapped
[ ] Health routes mapped
[ ] Metrics routes mapped
[ ] Management routes mapped
```

## Reachability

```text
[ ] Router registration confirmed
[ ] Parent prefixes resolved
[ ] Feature flags reviewed
[ ] Environment conditions reviewed
[ ] Reverse proxy mapping reviewed
[ ] Network restrictions considered
[ ] Runtime exposure checked where appropriate
```

## Security Controls

```text
[ ] Authentication mapped
[ ] Authorisation mapped
[ ] Validation mapped
[ ] CSRF controls mapped
[ ] Rate limiting mapped
[ ] Middleware mapped
[ ] Audit logging mapped
```

---

# Route Review Decision Tree

```text
Found route or entry point?
          |
          v
Is it registered?
      +---+---+
      |       |
     No      Yes
      |       |
      v       v
 Record     Determine
 Context     Inputs
                |
                v
        Attacker-Controlled?
            +---+---+
            |       |
           No      Yes
            |       |
            v       v
         Review   Authentication?
         Logic       |
                 +---+---+
                 |       |
                No      Yes
                 |       |
                 v       v
              Review   Authorisation?
              Exposure     |
                       +---+---+
                       |       |
                      No      Yes
                       |       |
                       v       v
                    Review   Trace
                    Access   Source
                              |
                              v
                             Sink
```

---

# Alternate Entry Point Decision Tree

```text
Sensitive operation found
          |
          v
Who calls it?
          |
          v
Find All References
          |
    +-----+-----+-----+
    |           |     |
    v           v     v
  REST       GraphQL gRPC
    |           |     |
    +-----------+-----+
                |
                v
          WebSocket?
                |
                v
           Worker?
                |
                v
           Admin API?
                |
                v
      Compare Security Controls
```

This reverse approach can expose alternate paths that route-first analysis misses.

---

# Recommended Complete Workflow

```text
Repository
    |
    v
Identify Frameworks
    |
    v
Inspect Project Structure
    |
    v
Find HTTP Routes
    |
    v
Find API Entry Points
    |
    +--> GraphQL
    +--> gRPC
    +--> WebSockets
    |
    v
Find External Entry Points
    |
    +--> Webhooks
    +--> OAuth
    +--> SAML
    |
    v
Find Async Entry Points
    |
    +--> Queues
    +--> Workers
    +--> Scheduled Jobs
    |
    v
Find Operational Entry Points
    |
    +--> Admin
    +--> Internal
    +--> Debug
    +--> Management
    |
    v
Resolve Parent Routes
    |
    v
Map Middleware
    |
    v
Map Authentication
    |
    v
Map Authorisation
    |
    v
Map Inputs
    |
    v
Trace to Sensitive Operations
    |
    v
Prioritise Attack Surface
    |
    v
Validate Runtime Exposure
```

---

# Combining With Source-to-Sink Analysis

Route mapping answers:

```text
Where does execution begin?
```

Source-to-sink analysis answers:

```text
Where can attacker-controlled data go?
```

Together:

```text
ENTRY POINT
     |
     v
ROUTE
     |
     v
SOURCE
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

This should become the central model for source-assisted application security testing.

---

# Combining With Static Analysis

Use the tools together:

```text
ripgrep
   |
   v
Find route declarations quickly
   |
   v
Semgrep / OpenGrep
   |
   v
Find structural route patterns
   |
   v
CodeQL
   |
   v
Trace complex route-to-sink flows
   |
   v
VS Code
   |
   v
Manual analysis
   |
   v
Burp Suite
   |
   v
Runtime validation
```

---

# Common Mistakes

## Only Searching Controllers

Modern applications may expose:

```text
Minimal APIs
GraphQL
gRPC
WebSockets
Webhooks
Queues
Serverless functions
```

Controllers alone are insufficient.

---

## Ignoring Parent Routes

Example:

```text
/api
  +
/users
  +
/{id}
```

must be reconstructed as:

```text
/api/users/{id}
```

---

## Ignoring Middleware

A route definition without its middleware does not show the complete security model.

---

## Treating Authentication as Authorisation

```text
Authenticated
    !=
Authorised for every object
```

---

## Ignoring Alternate Protocols

The same sensitive operation may be exposed through:

```text
REST
GraphQL
gRPC
WebSocket
Admin API
```

---

## Assuming Internal Means Trusted

```text
/internal
```

is only a name.

Verify actual network and authentication controls.

---

## Assuming Source Means Reachable

A route found in source may be:

```text
Disabled
Unregistered
Feature-flagged
Development-only
Legacy
Dead code
```

---

## Assuming Missing Annotation Means Missing Security

Security may be implemented:

```text
Globally
Through middleware
Through filters
Through interceptors
Through base classes
Through infrastructure
```

Trace the complete execution path.

---

## Treating Route Discovery as a Finding

A route is attack-surface information.

A vulnerability requires additional evidence.

---

# What Proves a Vulnerability?

Route discovery itself proves only that code defines or references an entry point.

For a security finding, establish:

```text
Entry point
    +
Reachability
    +
Attacker-controlled input or action
    +
Missing / ineffective security property
    +
Security impact
```

For example:

```text
DELETE /api/users/{id}
```

does not prove broken access control.

A stronger finding would establish:

```text
Authenticated low-privileged user
        |
        v
DELETE /api/users/{id}
        |
        v
Attacker chooses another user's ID
        |
        v
No object/role authorisation
        |
        v
Another user's account is deleted
```

---

# Final Testing Model

The final route and entry-point model is:

```text
                        REPOSITORY
                            |
                            v
                     APPLICATIONS
                            |
                            v
                       ENTRY POINTS
                            |
       +----------+---------+---------+----------+
       |          |         |         |          |
       v          v         v         v          v
      HTTP     GraphQL     gRPC   WebSockets   Async
       |          |         |         |          |
       +----------+---------+---------+----------+
                            |
                            v
                         HANDLER
                            |
                            v
                         INPUT
                            |
                            v
                    ATTACKER CONTROL?
                            |
                       +----+----+
                       |         |
                      No        Yes
                       |         |
                       v         v
                  Review Logic  AUTHENTICATION
                                      |
                                      v
                                AUTHORISATION
                                      |
                                      v
                                  VALIDATION
                                      |
                                      v
                               SOURCE-TO-SINK
                                      |
                                      v
                              SENSITIVE ACTION
                                      |
                                      v
                              RUNTIME EXPOSURE
                                      |
                                      v
                                  SECURITY
                                   IMPACT
```

The key principle is:

```text
Do not begin by asking:

"What vulnerabilities are in this repository?"

Begin by asking:

"What can cause this application to execute code,
what can an attacker control through those entry points,
what security controls apply,
and where does that data or action ultimately go?"
```

Once the complete entry-point map exists, vulnerability discovery becomes significantly more systematic.

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/methodology.md
docs/source-code-review/source-to-sink-analysis.md

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
docs/web/authentication.md
docs/web/authorisation.md
docs/web/idor-bola.md
docs/web/input-validation.md
docs/web/api-security.md
docs/web/graphql.md
docs/web/grpc-security.md
docs/web/websockets.md
docs/web/file-upload.md
docs/web/business-logic.md
docs/web/rate-limiting.md
```

---

# References

## OWASP Secure Code Review Cheat Sheet

[OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP Web Security Testing Guide - Attack Surface Identification

[OWASP Web Security Testing Guide - Attack Surface Identification](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP REST Security Cheat Sheet

[OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP GraphQL Cheat Sheet

[OWASP GraphQL Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Authorization Cheat Sheet

[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP Authentication Cheat Sheet

[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## PortSwigger Web Security Academy

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

## ASP.NET Core Routing

[ASP.NET Core Routing](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing){ target="_blank" rel="noopener noreferrer" }

## Spring Web MVC

[Spring Web MVC](https://docs.spring.io/spring-framework/reference/web/webmvc.html){ target="_blank" rel="noopener noreferrer" }

## Django URL Dispatcher

[Django URL Dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/){ target="_blank" rel="noopener noreferrer" }

## Django REST Framework Routers

[Django REST Framework Routers](https://www.django-rest-framework.org/api-guide/routers/){ target="_blank" rel="noopener noreferrer" }

## Flask Routing

[Flask Routing](https://flask.palletsprojects.com/){ target="_blank" rel="noopener noreferrer" }

## Express Routing

[Express Routing](https://expressjs.com/en/guide/routing.html){ target="_blank" rel="noopener noreferrer" }

## FastAPI

[FastAPI](https://fastapi.tiangolo.com/){ target="_blank" rel="noopener noreferrer" }

## GraphQL

[GraphQL](https://graphql.org/){ target="_blank" rel="noopener noreferrer" }

## gRPC

[gRPC](https://grpc.io/docs/){ target="_blank" rel="noopener noreferrer" }

## OpenAPI

[OpenAPI](https://www.openapis.org/){ target="_blank" rel="noopener noreferrer" }

## CodeQL

[CodeQL](https://codeql.github.com/docs/){ target="_blank" rel="noopener noreferrer" }

## Semgrep

[Semgrep](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

## OpenGrep

[OpenGrep](https://opengrep.dev/){ target="_blank" rel="noopener noreferrer" }

## ripgrep

[ripgrep](https://github.com/BurntSushi/ripgrep){ target="_blank" rel="noopener noreferrer" }

## Visual Studio Code

[Visual Studio Code](https://code.visualstudio.com/docs){ target="_blank" rel="noopener noreferrer" }

---

# Summary

Route and entry-point analysis establishes the application's true attack surface.

The workflow is:

```text
Repository
    |
    v
Framework Identification
    |
    v
Route Discovery
    |
    v
Non-HTTP Entry Point Discovery
    |
    v
Resolve Route Prefixes
    |
    v
Map Middleware
    |
    v
Map Authentication
    |
    v
Map Authorisation
    |
    v
Map Inputs
    |
    v
Map Sensitive Operations
    |
    v
Source-to-Sink Analysis
    |
    v
Runtime Validation
    |
    v
Security Finding
```

A complete review should therefore map more than URLs.

It should map:

```text
Entry Point
+
Handler
+
Input
+
Authentication
+
Authorisation
+
Validation
+
Sensitive Operation
+
Reachability
```

That map becomes the foundation for the rest of the source code security review.
