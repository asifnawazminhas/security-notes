# .NET / ASP.NET Core Source Code Review

This note provides a practical methodology for reviewing .NET and ASP.NET Core applications for security vulnerabilities.

The objective is not simply to search for dangerous .NET methods.

The objective is to trace attacker-controlled input through the application and determine whether it can reach security-sensitive operations without appropriate controls.

```text
HTTP Request
     |
     v
ASP.NET Route
     |
     v
Controller / Minimal API
     |
     v
Model Binding
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
Repository / Service
     |
     v
SECURITY-SENSITIVE SINK
```

Common technologies encountered during .NET source review include:

```text
ASP.NET Core
ASP.NET MVC
ASP.NET Web API
Minimal APIs
Razor Pages
Blazor
Entity Framework Core
Entity Framework 6
ADO.NET
Dapper
SignalR
gRPC
WCF
System.Text.Json
Newtonsoft.Json
```

!!! warning "Authorised Security Testing"
    Review and test only applications and source code for which you have explicit authorisation. Source repositories can contain credentials, personal information, cryptographic material, internal infrastructure information and other sensitive data.

---

# Review Strategy

A practical .NET review can be approached as:

```text
1. Identify solution and projects

2. Identify ASP.NET version and framework

3. Find application entry points

4. Enumerate routes

5. Map middleware

6. Map authentication

7. Map authorisation

8. Identify attacker-controlled sources

9. Identify validation

10. Identify dangerous sinks

11. Trace source-to-sink paths

12. Review business logic

13. Review configuration and secrets

14. Review dependencies

15. Review static-analysis findings

16. Perform variant analysis

17. Validate findings dynamically where authorised
```

---

# Identify the Application

Start by identifying .NET project files.

```bash
find . -type f \( \
-name '*.sln' \
-o -name '*.csproj' \
-o -name '*.fsproj' \
-o -name '*.vbproj' \
-o -name 'Directory.Build.props' \
-o -name 'Directory.Packages.props' \
-o -name 'packages.config' \
-o -name 'packages.lock.json' \
\) -print
```

Common files include:

```text
Application.sln
Application.csproj
Directory.Build.props
Directory.Packages.props
packages.config
packages.lock.json
```

---

# Inspect Project Files

Inspect `.csproj` files.

```bash
cat Application.csproj
```

Look for:

```xml
<TargetFramework>net8.0</TargetFramework>
```

or:

```xml
<TargetFrameworks>net8.0;net9.0</TargetFrameworks>
```

Legacy applications may contain:

```xml
<TargetFrameworkVersion>v4.8</TargetFrameworkVersion>
```

The framework version affects:

```text
Available APIs
Security defaults
Dependency support
Middleware architecture
Authentication configuration
Serialization behaviour
```

---

# Identify ASP.NET Core

Search:

```bash
rg -n \
'Microsoft\.AspNetCore|WebApplication\.CreateBuilder|CreateHostBuilder|ConfigureServices|Configure\(' \
.
```

Common modern entry point:

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

var app = builder.Build();

app.MapControllers();

app.Run();
```

Older ASP.NET Core applications commonly use:

```text
Program.cs
Startup.cs
```

with:

```csharp
public void ConfigureServices(IServiceCollection services)
```

and:

```csharp
public void Configure(IApplicationBuilder app)
```

---

# Identify Legacy ASP.NET

Search for:

```text
System.Web
Global.asax
Web.config
RouteConfig.cs
FilterConfig.cs
WebApiConfig.cs
App_Start
```

Command:

```bash
rg -n \
'System\.Web|HttpApplication|RouteConfig|WebApiConfig|RegisterRoutes|MapHttpRoute' \
.
```

Legacy ASP.NET applications require additional attention because their security configuration and APIs differ from ASP.NET Core.

---

# Repository Structure

Typical ASP.NET Core application:

```text
Application/
├── Controllers/
├── Models/
├── Services/
├── Repositories/
├── Middleware/
├── Filters/
├── Data/
├── Views/
├── Pages/
├── wwwroot/
├── Properties/
├── Program.cs
├── Startup.cs
├── appsettings.json
├── appsettings.Development.json
└── Application.csproj
```

Important directories include:

```text
Controllers
Services
Repositories
Middleware
Filters
Models
Views
Pages
wwwroot
Data
```

---

# Route Discovery

Route mapping should be one of the first tasks.

Search:

```bash
rg -n \
'\[Route\(|\[HttpGet|\[HttpPost|\[HttpPut|\[HttpPatch|\[HttpDelete|\[HttpHead|\[HttpOptions' \
.
```

Example:

```csharp
[Route("api/users")]
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

---

# Controller Discovery

Search:

```bash
rg -n \
'ControllerBase|: Controller|ApiController' \
--glob '*.cs' \
.
```

Typical controller:

```csharp
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
}
```

The `[controller]` token is replaced with the controller name.

For:

```text
OrdersController
```

the route becomes approximately:

```text
/api/orders
```

depending on route configuration.

---

# HTTP Method Attributes

Look for:

```text
[HttpGet]
[HttpPost]
[HttpPut]
[HttpPatch]
[HttpDelete]
[HttpHead]
[HttpOptions]
```

Search:

```bash
rg -n \
'\[Http(Get|Post|Put|Patch|Delete|Head|Options)' \
--glob '*.cs' \
.
```

---

# Minimal APIs

Modern ASP.NET Core applications may define endpoints without controllers.

Search:

```bash
rg -n \
'\.MapGet\(|\.MapPost\(|\.MapPut\(|\.MapPatch\(|\.MapDelete\(|\.MapMethods\(' \
--glob '*.cs' \
.
```

Example:

```csharp
app.MapGet("/api/users/{id}", async (int id, AppDbContext db) =>
{
    return await db.Users.FindAsync(id);
});
```

Minimal APIs must be included in route enumeration.

---

# Route Groups

Modern applications may use:

```csharp
var api = app.MapGroup("/api");

api.MapGet("/users", GetUsers);
api.MapPost("/users", CreateUser);
```

Search:

```bash
rg -n \
'MapGroup\(' \
--glob '*.cs' \
.
```

Remember to combine the group prefix with the individual endpoint path.

---

# Razor Pages

Search:

```bash
find . -type f -name '*.cshtml' -o -name '*.cshtml.cs'
```

Razor Pages commonly use handlers such as:

```text
OnGet()
OnPost()
OnPut()
OnDelete()
OnGetAsync()
OnPostAsync()
```

Search:

```bash
rg -n \
'On(Get|Post|Put|Delete|Patch).*Async|On(Get|Post|Put|Delete|Patch)\(' \
--glob '*.cs' \
.
```

---

# Build a Route Inventory

Create an inventory:

| Method | Route | Handler | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/api/users/{id}` | `UsersController.Get()` | Required | User |
| POST | `/api/users` | `UsersController.Create()` | Required | Admin |
| GET | `/admin` | `AdminController.Index()` | Required | Admin |
| POST | `/upload` | `UploadController.Upload()` | Required | User |

This becomes the foundation for systematic review.

---

# Middleware

ASP.NET Core middleware is extremely important.

Inspect:

```text
Program.cs
Startup.cs
Middleware/
```

Search:

```bash
rg -n \
'UseAuthentication|UseAuthorization|UseCors|UseStaticFiles|UseRouting|UseEndpoints|UseExceptionHandler|UseDeveloperExceptionPage|UseSession|UseHttpsRedirection|UseHsts' \
.
```

Typical pipeline:

```csharp
app.UseRouting();

app.UseAuthentication();

app.UseAuthorization();

app.MapControllers();
```

Middleware ordering can affect security behaviour.

Do not infer a vulnerability solely from order without understanding the framework version and application configuration.

---

# Custom Middleware

Search:

```bash
rg -n \
'IMiddleware|RequestDelegate|InvokeAsync|Invoke\(' \
--glob '*.cs' \
.
```

Custom middleware may implement:

```text
Authentication
Authorisation
Tenant selection
API key checks
Logging
Request validation
Header handling
IP restrictions
```

Review it carefully.

---

# Sources - Attacker-Controlled Input

Common ASP.NET Core sources include:

```text
Request.Query
Request.Form
Request.Headers
Request.Cookies
Request.Body
Request.RouteValues
Request.Path
Request.PathBase
Request.Host
Request.Scheme
```

Search:

```bash
rg -n \
'Request\.(Query|Form|Headers|Cookies|Body|RouteValues|Path|PathBase|Host|Scheme)' \
--glob '*.cs' \
.
```

---

# Model Binding

ASP.NET Core automatically binds request values to parameters and objects.

Example:

```csharp
[HttpPost]
public IActionResult Create(UserInput input)
{
    ...
}
```

The source is not visibly represented as:

```csharp
Request.Form
```

because model binding performs the conversion.

Therefore inspect:

```text
Controller parameters
DTOs
Request models
Records
Binding attributes
```

---

# Binding Attributes

Search:

```bash
rg -n \
'\[FromQuery|\[FromRoute|\[FromBody|\[FromForm|\[FromHeader|\[FromServices' \
--glob '*.cs' \
.
```

Examples:

```csharp
public IActionResult Search([FromQuery] string q)
```

```csharp
public IActionResult Get([FromRoute] int id)
```

```csharp
public IActionResult Create([FromBody] UserDto user)
```

```csharp
public IActionResult Upload([FromForm] IFormFile file)
```

```csharp
public IActionResult Test([FromHeader] string host)
```

---

# Query Parameters

Example:

```csharp
var value = Request.Query["search"];
```

or:

```csharp
public IActionResult Search(string query)
```

Trace query parameters into:

```text
SQL
Search queries
Files
URLs
Commands
Templates
Redirects
Logs
```

---

# Route Parameters

Example:

```csharp
[HttpGet("{id}")]
public IActionResult Get(int id)
```

or:

```csharp
var id = RouteData.Values["id"];
```

Route identifiers are especially important for:

```text
IDOR
BOLA
Authorisation
Path traversal
Business logic
```

---

# Headers

Examples:

```csharp
Request.Headers["X-Forwarded-Host"]
Request.Headers["User-Agent"]
Request.Headers["Referer"]
Request.Headers["Authorization"]
```

Search:

```bash
rg -n \
'Request\.Headers|\[FromHeader' \
--glob '*.cs' \
.
```

Headers can influence:

```text
Host handling
Redirects
Logging
Authentication
Proxy behaviour
URL generation
```

---

# Cookies

Search:

```bash
rg -n \
'Request\.Cookies|Response\.Cookies' \
--glob '*.cs' \
.
```

Review cookies used for:

```text
Authentication
Session state
Preferences
Tenant selection
Security decisions
```

---

# Authentication

Search:

```bash
rg -n \
'AddAuthentication|UseAuthentication|AuthenticateAsync|SignInAsync|SignOutAsync|\[Authorize|\[AllowAnonymous' \
--glob '*.cs' \
.
```

---

# Authorize Attribute

Example:

```csharp
[Authorize]
public class AccountController : Controller
{
}
```

or:

```csharp
[Authorize(Roles = "Admin")]
public IActionResult Admin()
{
}
```

Search:

```bash
rg -n \
'\[Authorize|\[AllowAnonymous' \
--glob '*.cs' \
.
```

---

# AllowAnonymous

`[AllowAnonymous]` deliberately bypasses authorization requirements for the affected endpoint.

Search:

```bash
rg -n \
'\[AllowAnonymous' \
--glob '*.cs' \
.
```

Review every occurrence.

Ask:

```text
Why is anonymous access required?

Does the endpoint expose sensitive data?

Does it perform state-changing actions?

Is the attribute overriding controller-level protection?
```

An `[AllowAnonymous]` attribute is not automatically a vulnerability.

---

# Authorization Policies

Search:

```bash
rg -n \
'AddAuthorization|AddPolicy|RequireRole|RequireClaim|RequireAssertion|IAuthorizationRequirement|AuthorizationHandler' \
--glob '*.cs' \
.
```

Example:

```csharp
options.AddPolicy("AdminOnly", policy =>
{
    policy.RequireRole("Admin");
});
```

Endpoint:

```csharp
[Authorize(Policy = "AdminOnly")]
```

Map policy names to their actual implementation.

---

# Resource-Based Authorization

ASP.NET Core may use:

```csharp
IAuthorizationService
```

Example:

```csharp
var result = await authorizationService.AuthorizeAsync(
    User,
    document,
    "EditDocument");
```

Search:

```bash
rg -n \
'IAuthorizationService|AuthorizeAsync\(' \
--glob '*.cs' \
.
```

This is particularly important for object-level authorisation.

---

# User Identity and Claims

Search:

```bash
rg -n \
'User\.Identity|User\.Claims|FindFirst|FindFirstValue|IsInRole|ClaimsPrincipal|ClaimsIdentity' \
--glob '*.cs' \
.
```

Review where claims influence:

```text
User ID
Role
Tenant
Permissions
Administrative status
Object ownership
```

---

# IDOR / BOLA

A common pattern:

```csharp
[HttpGet("{id}")]
public async Task<IActionResult> Get(int id)
{
    var invoice = await db.Invoices.FindAsync(id);

    return Ok(invoice);
}
```

The important question is:

```text
Where is the authorisation check?
```

A stronger pattern may scope the lookup:

```csharp
var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);

var invoice = await db.Invoices
    .SingleOrDefaultAsync(x =>
        x.Id == id &&
        x.UserId == userId);
```

The exact secure implementation depends on the application's authorisation model.

Refer to:

```text
docs/web/idor-bola.md
docs/web/authorisation.md
```

---

# Search Object Lookups

Useful review candidates:

```bash
rg -n \
'FindAsync\(|Find\(|FirstOrDefault|SingleOrDefault|Where\(' \
--glob '*.cs' \
.
```

Prioritise handlers where an object ID originates from:

```text
Route
Query
Request body
```

Then determine whether access is scoped to the authenticated user, role or tenant.

---

# Tenant Isolation

Search:

```bash
rg -n -i \
'tenant|tenantid|tenant_id|organization|organisation|companyid|accountid' \
--glob '*.cs' \
.
```

Trace:

```text
Request
   |
   v
Object ID
   |
   v
Database Query
   |
   v
Tenant Restriction?
```

Never assume an internal tenant ID is sufficient authorisation by itself.

---

# Input Validation

ASP.NET applications commonly use DataAnnotations.

Examples:

```csharp
[Required]
[StringLength(100)]
[Range(1, 100)]
[EmailAddress]
public string Email { get; set; }
```

Search:

```bash
rg -n \
'\[Required|\[StringLength|\[MaxLength|\[MinLength|\[Range|\[RegularExpression|\[EmailAddress|\[Url' \
--glob '*.cs' \
.
```

---

# ModelState

Legacy/controller-based applications may explicitly inspect:

```csharp
ModelState.IsValid
```

Search:

```bash
rg -n \
'ModelState\.IsValid|TryValidateModel|ValidateModel' \
--glob '*.cs' \
.
```

Do not assume the presence or absence of a manual `ModelState.IsValid` check proves whether validation is enforced. `[ApiController]` and framework behaviour can alter validation handling.

---

# FluentValidation

Applications may use FluentValidation.

Search:

```bash
rg -n \
'AbstractValidator<|RuleFor\(|FluentValidation' \
--glob '*.cs' \
.
```

Example:

```csharp
RuleFor(x => x.Username)
    .NotEmpty()
    .MaximumLength(100);
```

Trace which validators are registered and actually executed.

---

# Mass Assignment / Overposting

Example model:

```csharp
public class User
{
    public int Id { get; set; }

    public string Username { get; set; }

    public bool IsAdmin { get; set; }
}
```

Potentially risky:

```csharp
[HttpPost]
public async Task<IActionResult> Update(User user)
{
    db.Users.Update(user);

    await db.SaveChangesAsync();

    return Ok();
}
```

If clients can bind fields such as:

```text
IsAdmin
Role
TenantId
OwnerId
Balance
Verified
Status
```

the application may be vulnerable to overposting/mass assignment.

Prefer explicit request DTOs and explicit mapping of permitted fields.

Refer to:

```text
docs/web/mass-assignment.md
```

---

# Search Binding Candidates

```bash
rg -n \
'\[Bind\(|TryUpdateModelAsync|UpdateModelAsync|\.Update\(' \
--glob '*.cs' \
.
```

Also inspect controller parameters that directly accept persistence/domain models.

---

# SQL Injection

Common .NET database technologies include:

```text
ADO.NET
Entity Framework Core
Entity Framework
Dapper
NHibernate
Raw SQL
Stored procedures
```

---

# ADO.NET

Potentially dangerous pattern:

```csharp
var sql = "SELECT * FROM Users WHERE Username = '" + username + "'";

var command = new SqlCommand(sql, connection);
```

Search:

```bash
rg -n \
'SqlCommand|DbCommand|OleDbCommand|OdbcCommand' \
--glob '*.cs' \
.
```

Then inspect how the query string is constructed.

---

# Parameterised ADO.NET

Safer construction:

```csharp
var command = new SqlCommand(
    "SELECT * FROM Users WHERE Username = @username",
    connection);

command.Parameters.AddWithValue("@username", username);
```

Parameterisation protects data values from becoming SQL syntax when used correctly.

---

# Entity Framework Core

Normal LINQ queries such as:

```csharp
var user = await db.Users
    .FirstOrDefaultAsync(x => x.Username == username);
```

are generally translated using parameters for values.

The higher-value review targets are raw SQL APIs.

Search:

```bash
rg -n \
'FromSqlRaw|FromSqlInterpolated|ExecuteSqlRaw|ExecuteSqlInterpolated|SqlQueryRaw|SqlQuery<' \
--glob '*.cs' \
.
```

---

# FromSqlRaw

Potentially unsafe:

```csharp
var query =
    "SELECT * FROM Users WHERE Name = '" +
    name +
    "'";

var users = db.Users.FromSqlRaw(query);
```

Safer parameter use:

```csharp
var users = db.Users.FromSqlRaw(
    "SELECT * FROM Users WHERE Name = {0}",
    name);
```

Also review interpolated APIs carefully.

Do not assume all interpolation is unsafe: some EF Core interpolated APIs preserve values as parameters.

---

# ExecuteSqlRaw

Search:

```bash
rg -n \
'ExecuteSqlRaw|ExecuteSqlInterpolated' \
--glob '*.cs' \
.
```

Review whether attacker-controlled data modifies SQL syntax.

---

# Dapper

Search:

```bash
rg -n \
'QueryAsync|Query<|ExecuteAsync|Execute\(' \
--glob '*.cs' \
.
```

Potentially unsafe:

```csharp
connection.Query<User>(
    "SELECT * FROM Users WHERE Name = '" + name + "'");
```

Safer:

```csharp
connection.Query<User>(
    "SELECT * FROM Users WHERE Name = @Name",
    new { Name = name });
```

---

# Dynamic SQL Components

Parameterisation generally protects data values.

However, dynamic structural elements require separate attention:

```text
ORDER BY column
Table name
Column name
Sort direction
```

Example:

```csharp
var sql = $"SELECT * FROM Users ORDER BY {sort}";
```

These commonly require explicit allowlisting or server-side mapping.

---

# SQL Search Commands

```bash
rg -n \
'SqlCommand|FromSqlRaw|ExecuteSqlRaw|SqlQueryRaw|QueryAsync|ExecuteAsync|CreateCommand' \
--glob '*.cs' \
.
```

Then search for string construction near those locations:

```bash
rg -n \
'\$".*(SELECT|INSERT|UPDATE|DELETE)|".*(SELECT|INSERT|UPDATE|DELETE).*"\s*\+' \
--glob '*.cs' \
.
```

Treat regex results as triage only.

---

# NoSQL Injection

.NET applications may use:

```text
MongoDB
Elasticsearch
Redis
Cosmos DB
Other document databases
```

Search:

```bash
rg -n \
'MongoClient|Builders<|BsonDocument|FilterDefinition|ElasticsearchClient|ElasticClient|CosmosClient' \
--glob '*.cs' \
.
```

Review dynamic query construction and attacker-controlled query structures.

Refer to:

```text
docs/web/nosql-injection.md
```

---

# LDAP Injection

Common namespaces:

```text
System.DirectoryServices
System.DirectoryServices.Protocols
```

Search:

```bash
rg -n \
'DirectorySearcher|DirectoryEntry|SearchRequest|System\.DirectoryServices|Filter\s*=' \
--glob '*.cs' \
.
```

Potentially dangerous:

```csharp
searcher.Filter =
    "(&(objectClass=user)(sAMAccountName=" +
    username +
    "))";
```

If attacker-controlled data is inserted directly into an LDAP filter, review for LDAP injection.

Refer to:

```text
docs/web/ldap-injection.md
```

---

# OS Command Injection

Important .NET process APIs include:

```text
System.Diagnostics.Process
Process.Start()
ProcessStartInfo
```

Search:

```bash
rg -n \
'Process\.Start|ProcessStartInfo|System\.Diagnostics\.Process' \
--glob '*.cs' \
.
```

---

# Process.Start

Example review candidate:

```csharp
var filename = Request.Query["filename"];

Process.Start("tool.exe", filename);
```

Determine:

```text
Can the attacker control the executable?

Can the attacker control arguments?

Is a shell involved?

Are arguments passed structurally?

Are untrusted values validated?

Can shell metacharacters become meaningful?
```

---

# UseShellExecute

Search:

```bash
rg -n \
'UseShellExecute|cmd\.exe|powershell|pwsh|/bin/sh|/bin/bash' \
--glob '*.cs' \
.
```

Explicit shell invocation deserves particularly careful review.

Example:

```csharp
Process.Start(
    "cmd.exe",
    "/c some-command " + userInput);
```

User-controlled data reaching a shell command may create command injection risk.

---

# ArgumentList

Modern .NET provides structured process arguments:

```csharp
var startInfo = new ProcessStartInfo
{
    FileName = "tool.exe"
};

startInfo.ArgumentList.Add(userValue);
```

Passing arguments structurally can avoid some command-line construction problems, although the invoked program's own argument semantics must still be considered.

---

# Command Injection Data Flow

```text
Request.Query["host"]
        |
        v
Controller
        |
        v
String concatenation
        |
        v
cmd.exe /c ...
        |
        v
Command execution
```

Refer to:

```text
docs/web/command-injection.md
```

---

# Server-Side Request Forgery

Common .NET network APIs:

```text
HttpClient
HttpRequestMessage
WebClient
WebRequest
HttpWebRequest
SocketsHttpHandler
```

Search:

```bash
rg -n \
'HttpClient|HttpRequestMessage|WebClient|WebRequest|HttpWebRequest|GetAsync\(|PostAsync\(|SendAsync\(' \
--glob '*.cs' \
.
```

---

# SSRF Example

Review candidate:

```csharp
[HttpGet]
public async Task<string> Fetch(string url)
{
    return await httpClient.GetStringAsync(url);
}
```

Data flow:

```text
Query Parameter
     |
     v
url
     |
     v
HttpClient
     |
     v
Remote Request
```

Review:

```text
Allowed schemes
Allowed destinations
DNS resolution
Redirects
IP address restrictions
Network egress
Proxy behaviour
```

Refer to:

```text
docs/web/ssrf.md
```

---

# HttpClient BaseAddress

Do not only search direct URLs.

Example:

```csharp
httpClient.BaseAddress = new Uri(baseUrl);
```

Then:

```csharp
await httpClient.GetAsync(path);
```

Trace both:

```text
baseUrl
path
```

because the final destination may be constructed across multiple functions.

---

# Open Redirect

Common redirect APIs:

```text
Redirect()
RedirectPermanent()
LocalRedirect()
RedirectToAction()
RedirectToRoute()
Response.Redirect()
```

Search:

```bash
rg -n \
'Redirect\(|RedirectPermanent|LocalRedirect|RedirectToAction|RedirectToRoute|Response\.Redirect' \
--glob '*.cs' \
.
```

---

# Redirect Example

Review candidate:

```csharp
public IActionResult Login(string returnUrl)
{
    ...

    return Redirect(returnUrl);
}
```

Trace whether `returnUrl` can reference an external destination.

ASP.NET Core provides helpers such as:

```csharp
Url.IsLocalUrl(returnUrl)
```

and:

```csharp
LocalRedirect(returnUrl)
```

where appropriate.

Refer to:

```text
docs/web/open-redirect.md
```

---

# Path Traversal

Common filesystem APIs include:

```text
File.ReadAllText
File.ReadAllBytes
File.Open
File.OpenRead
File.OpenWrite
File.WriteAllText
FileStream
Directory.GetFiles
Directory.Delete
Path.Combine
```

Search:

```bash
rg -n \
'File\.(Read|Write|Open|Delete|Move|Copy)|FileStream|Directory\.(Get|Delete|Move|Create)|Path\.Combine|Path\.GetFullPath' \
--glob '*.cs' \
.
```

---

# Path.Combine Is Not a Security Boundary

Example:

```csharp
var path = Path.Combine(baseDirectory, userFilename);
```

`Path.Combine()` constructs paths.

It does not by itself guarantee that the final path remains inside the intended directory.

Review containment separately.

Conceptually:

```text
User Path
    |
    v
Combine With Base
    |
    v
Canonical / Full Path
    |
    v
Verify Containment
    |
    v
File Operation
```

Refer to:

```text
docs/web/path-traversal.md
```

---

# File Download

Look for:

```text
PhysicalFile()
File()
FileStreamResult
FileContentResult
VirtualFileResult
```

Search:

```bash
rg -n \
'PhysicalFile\(|FileStreamResult|FileContentResult|VirtualFileResult' \
--glob '*.cs' \
.
```

Trace attacker-controlled:

```text
filename
path
object ID
```

---

# File Upload

ASP.NET Core commonly represents uploaded files with:

```text
IFormFile
IFormFileCollection
```

Search:

```bash
rg -n \
'IFormFile|IFormFileCollection|CopyToAsync|CopyTo\(' \
--glob '*.cs' \
.
```

---

# File Upload Example

```csharp
public async Task<IActionResult> Upload(IFormFile file)
{
    var path = Path.Combine(
        uploadDirectory,
        file.FileName);

    using var stream = System.IO.File.Create(path);

    await file.CopyToAsync(stream);

    return Ok();
}
```

Review:

```text
Original filename
Path handling
Generated filename
Extension
MIME type
Content
File signature
File size
Storage directory
Execution possibility
Public accessibility
Downstream processing
```

Refer to:

```text
docs/web/file-upload.md
```

---

# FileName

Search:

```bash
rg -n \
'\.FileName|ContentType|ContentDisposition' \
--glob '*.cs' \
.
```

Do not trust:

```csharp
file.FileName
```

as a safe server-side path component.

---

# Archive Extraction

Search:

```bash
rg -n \
'ZipArchive|ZipFile|ExtractToDirectory|TarFile|GZipStream' \
--glob '*.cs' \
.
```

Review archive entry paths and extraction behaviour for traversal issues.

---

# XXE and XML Parsing

Common XML APIs include:

```text
XmlDocument
XmlReader
XmlTextReader
XDocument
XPathDocument
XmlSerializer
DataSet.ReadXml
```

Search:

```bash
rg -n \
'XmlDocument|XmlReader|XmlTextReader|XDocument|XPathDocument|XmlSerializer|ReadXml|DtdProcessing|XmlResolver' \
--glob '*.cs' \
.
```

---

# XML Security Configuration

Review:

```text
DtdProcessing
XmlResolver
External resource resolution
Framework/runtime version
```

Do not assume an XML parser is vulnerable solely because its class name appears.

Parser defaults and configuration vary by API and .NET version.

Refer to:

```text
docs/web/xxe.md
```

---

# Deserialization

High-value .NET deserialization APIs include legacy formatters and flexible serializers.

Search:

```bash
rg -n \
'BinaryFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|SoapFormatter|JavaScriptSerializer|JsonConvert|TypeNameHandling|DeserializeObject|Deserialize<' \
--glob '*.cs' \
.
```

---

# BinaryFormatter

Search:

```bash
rg -n \
'BinaryFormatter|\.Deserialize\(' \
--glob '*.cs' \
.
```

`BinaryFormatter` is a legacy dangerous serialization technology and should not be used for untrusted data.

Review whether attacker-controlled serialized data can reach it.

---

# LosFormatter and ObjectStateFormatter

Search:

```bash
rg -n \
'LosFormatter|ObjectStateFormatter' \
--glob '*.cs' \
.
```

These are especially relevant in legacy ASP.NET applications.

---

# Newtonsoft.Json TypeNameHandling

Search:

```bash
rg -n \
'TypeNameHandling|JsonSerializerSettings|JsonConvert\.DeserializeObject' \
--glob '*.cs' \
.
```

Configuration such as permissive polymorphic type handling can become security-sensitive when deserializing attacker-controlled data.

Do not report `JsonConvert.DeserializeObject()` by itself as insecure deserialization.

Review the serializer settings and permitted types.

---

# System.Text.Json

Search:

```bash
rg -n \
'JsonSerializer\.Deserialize|JsonSerializerOptions|JsonConverter' \
--glob '*.cs' \
.
```

Normal JSON deserialization is not automatically insecure.

Review:

```text
Target types
Custom converters
Polymorphism
Object binding
Business logic
Mass assignment
```

---

# YAML

Applications may use libraries such as YamlDotNet.

Search:

```bash
rg -n \
'YamlDotNet|DeserializerBuilder|\.Deserialize<' \
--glob '*.cs' \
.
```

Review type handling and data origin.

---

# SSTI and Razor

Common rendering mechanisms include:

```text
Razor
Razor Pages
MVC Views
RazorLight
Scriban
DotLiquid
Fluid
Handlebars.Net
```

Search:

```bash
rg -n \
'RazorLight|CompileRender|CompileRenderString|Scriban|DotLiquid|Fluid|Handlebars' \
--glob '*.cs' \
.
```

The important distinction is:

```text
Attacker data passed to a fixed template
```

versus:

```text
Attacker data treated as template source
```

The latter deserves closer SSTI review.

Refer to:

```text
docs/web/ssti.md
```

---

# XSS

ASP.NET Razor normally performs HTML encoding for standard Razor expressions.

Example:

```html
@Model.Username
```

should not automatically be treated as an XSS sink.

Look for explicit raw output or bypasses.

---

# Html.Raw

Search:

```bash
rg -n \
'Html\.Raw|HtmlString|IHtmlContent|HtmlContentBuilder' \
--glob '*.cs' \
--glob '*.cshtml' \
.
```

Example:

```html
@Html.Raw(Model.Content)
```

Trace whether:

```text
Model.Content
```

can contain attacker-controlled HTML.

---

# Razor HtmlString

Legacy applications may use:

```csharp
new HtmlString(value)
```

Search:

```bash
rg -n \
'HtmlString|MvcHtmlString|Html\.Raw' \
.
```

These APIs may deliberately mark content as already safe.

Trace their inputs carefully.

---

# JavaScript Injection From Razor

Search Razor files for server values embedded into script blocks.

```bash
rg -n \
'<script|Html\.Raw|Json\.Serialize|JsonSerializer' \
--glob '*.cshtml' \
.
```

Output context matters.

HTML encoding is not equivalent to JavaScript-context encoding.

Refer to:

```text
docs/web/xss.md
```

---

# Response.Write

Legacy ASP.NET:

```csharp
Response.Write(value);
```

Search:

```bash
rg -n \
'Response\.Write' \
.
```

Determine whether attacker-controlled content reaches HTML without appropriate context-specific encoding.

---

# HTML Injection

The same raw rendering primitives may result in HTML injection even when executable JavaScript cannot be demonstrated.

Refer to:

```text
docs/web/html-injection.md
```

---

# CSRF

ASP.NET Core MVC commonly provides anti-forgery protections.

Search:

```bash
rg -n \
'ValidateAntiForgeryToken|AutoValidateAntiforgeryToken|IgnoreAntiforgeryToken|IAntiforgery|AddAntiforgery|UseAntiforgery' \
--glob '*.cs' \
.
```

---

# ValidateAntiForgeryToken

Example:

```csharp
[HttpPost]
[ValidateAntiForgeryToken]
public IActionResult UpdateProfile(...)
```

Review state-changing cookie-authenticated endpoints.

---

# IgnoreAntiforgeryToken

Search:

```bash
rg -n \
'IgnoreAntiforgeryToken' \
--glob '*.cs' \
.
```

Review why protection is intentionally disabled.

It may be appropriate for APIs that do not rely on browser cookies.

---

# Global Anti-Forgery Filters

Applications may register:

```csharp
AutoValidateAntiforgeryTokenAttribute
```

globally.

Therefore absence of:

```text
[ValidateAntiForgeryToken]
```

on an individual action does not prove that CSRF protection is missing.

Trace the complete framework configuration.

Refer to:

```text
docs/web/csrf.md
```

---

# CORS

Search:

```bash
rg -n \
'AddCors|UseCors|WithOrigins|AllowAnyOrigin|AllowCredentials|AllowAnyHeader|AllowAnyMethod|SetIsOriginAllowed' \
--glob '*.cs' \
.
```

---

# CORS Review

Example:

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("Policy", policy =>
    {
        policy
            .WithOrigins("https://example.com")
            .AllowCredentials();
    });
});
```

Review:

```text
Allowed origins
Credentials
Dynamic origin logic
Environment differences
Endpoint-specific policies
```

Search especially for:

```csharp
AllowAnyOrigin()
```

and:

```csharp
SetIsOriginAllowed(...)
```

but do not automatically report them without assessing whether sensitive cross-origin access is possible.

Refer to:

```text
docs/web/cors.md
```

---

# Host Header Attacks

Search:

```bash
rg -n \
'Request\.Host|Request\.Headers\["Host"\]|X-Forwarded-Host|ForwardedHeaders|UseForwardedHeaders|HostString' \
--glob '*.cs' \
.
```

Review host-derived data used for:

```text
Password reset links
Email links
Absolute URL generation
Redirects
Security decisions
Cache keys
```

Refer to:

```text
docs/web/host-header-attacks.md
```

---

# Forwarded Headers

Search:

```bash
rg -n \
'ForwardedHeadersOptions|KnownProxies|KnownNetworks|ForwardedHeaders' \
--glob '*.cs' \
.
```

Reverse-proxy trust configuration can affect:

```text
Client IP
Scheme
Host
Security decisions
Rate limiting
Redirects
```

---

# HTTP Security Headers

Search:

```bash
rg -n \
'Content-Security-Policy|Strict-Transport-Security|X-Content-Type-Options|Referrer-Policy|Permissions-Policy|X-Frame-Options|UseHsts' \
.
```

Also inspect reverse-proxy and deployment configuration because headers may be added outside the application.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# Session Management

Search:

```bash
rg -n \
'AddSession|UseSession|HttpContext\.Session|SessionOptions|CookieAuthenticationOptions|AddCookie' \
--glob '*.cs' \
.
```

Review:

```text
Cookie name
Secure
HttpOnly
SameSite
Expiration
Sliding expiration
Session rotation
Logout
Invalidation
```

---

# Cookie Configuration

Search:

```bash
rg -n \
'Cookie\.SecurePolicy|Cookie\.HttpOnly|Cookie\.SameSite|SameSiteMode|CookieBuilder|CookieOptions' \
--glob '*.cs' \
.
```

Do not review cookie settings in isolation.

Determine which cookie is being configured and what security role it has.

---

# JWT

Search:

```bash
rg -n \
'AddJwtBearer|JwtBearerOptions|JwtSecurityTokenHandler|TokenValidationParameters|ValidateIssuer|ValidateAudience|ValidateLifetime|ValidateIssuerSigningKey|IssuerSigningKey' \
--glob '*.cs' \
.
```

---

# JWT Review

Inspect:

```text
Signing algorithm
Signing key
Issuer validation
Audience validation
Lifetime validation
Clock skew
Claims mapping
Key selection
Token source
```

Example:

```csharp
new TokenValidationParameters
{
    ValidateIssuer = true,
    ValidateAudience = true,
    ValidateLifetime = true,
    ValidateIssuerSigningKey = true
};
```

Do not assume booleans alone prove security.

Trace actual values and keys.

Refer to:

```text
docs/web/jwt.md
```

---

# JWT Claims

Search:

```bash
rg -n \
'ClaimTypes\.Role|ClaimTypes\.NameIdentifier|FindFirst|FindFirstValue|ClaimsPrincipal' \
--glob '*.cs' \
.
```

Determine whether attacker-influenced claims are used for:

```text
Roles
Tenant
User ID
Permissions
Administrative access
```

---

# OAuth / OpenID Connect

Search:

```bash
rg -n \
'AddOpenIdConnect|AddOAuth|OpenIdConnectOptions|OAuthOptions|CallbackPath|ClientId|ClientSecret|Authority|MetadataAddress' \
--glob '*.cs' \
.
```

Review:

```text
Authority
Issuer
Callback
Client ID
Client secret
State handling
Nonce
PKCE
Token validation
Claim mapping
Account linking
```

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# SAML

Common .NET SAML libraries may include:

```text
Sustainsys.Saml2
ITfoxtec.Identity.Saml2
ComponentSpace
```

Search:

```bash
rg -n -i \
'saml|sustainsys|itfoxtec|componentspace' \
--glob '*.cs' \
--glob '*.json' \
--glob '*.config' \
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
Certificate validation
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
'forgotpassword|resetpassword|passwordreset|generatepasswordresettoken|resetpasswordasync' \
--glob '*.cs' \
.
```

ASP.NET Identity commonly provides:

```text
GeneratePasswordResetTokenAsync()
ResetPasswordAsync()
```

Review:

```text
User enumeration
Token generation
Token lifetime
Token binding
Single use
Password-change invalidation
Reset URL construction
Host handling
Rate limiting
```

Refer to:

```text
docs/web/password-reset.md
```

---

# MFA

Search:

```bash
rg -n -i \
'twofactor|two-factor|2fa|mfa|authenticator|totp|otp|recoverycode' \
--glob '*.cs' \
.
```

ASP.NET Identity APIs may include:

```text
GetTwoFactorEnabledAsync()
GenerateTwoFactorTokenAsync()
VerifyTwoFactorTokenAsync()
GenerateNewTwoFactorRecoveryCodesAsync()
```

Review bypass paths as well as the main verification handler.

Refer to:

```text
docs/web/mfa.md
```

---

# Password Hashing

ASP.NET Identity commonly uses:

```text
IPasswordHasher<TUser>
PasswordHasher<TUser>
```

Search:

```bash
rg -n \
'PasswordHasher|IPasswordHasher|HashPassword|VerifyHashedPassword' \
--glob '*.cs' \
.
```

Custom password hashing implementations deserve careful review.

Search also for:

```bash
rg -n \
'MD5|SHA1|SHA256|SHA512|PBKDF2|Rfc2898DeriveBytes|BCrypt|Argon2' \
--glob '*.cs' \
.
```

Do not report a hash algorithm merely because its name appears.

Determine what it protects.

---

# Cryptography

Common .NET cryptographic APIs:

```text
Aes
RSA
ECDsa
RandomNumberGenerator
Rfc2898DeriveBytes
HMACSHA256
SHA256
```

Search:

```bash
rg -n \
'Aes\.Create|RSA\.Create|ECDsa\.Create|RandomNumberGenerator|Rfc2898DeriveBytes|HMACSHA|SHA256|SHA512|MD5|SHA1' \
--glob '*.cs' \
.
```

Review:

```text
Algorithm
Mode
Key source
Key size
Nonce/IV
Random generation
Integrity
Key storage
Hard-coded material
```

---

# Randomness

Search:

```bash
rg -n \
'new Random\(|Random\.Shared|RandomNumberGenerator|Guid\.NewGuid' \
--glob '*.cs' \
.
```

For security-sensitive unpredictable tokens, prefer cryptographically secure randomness.

Review use of ordinary:

```csharp
Random
```

for:

```text
Password reset tokens
Session tokens
API keys
MFA codes
Invitation tokens
```

---

# Hard-Coded Secrets

Search:

```bash
rg -n -i \
'password|passwd|secret|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|connectionstring|connectionstrings' \
.
```

Inspect:

```text
appsettings.json
appsettings.*.json
launchSettings.json
web.config
*.cs
*.config
*.xml
*.yml
*.yaml
Dockerfile
docker-compose.yml
CI/CD files
```

---

# appsettings.json

Typical configuration:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "..."
  },
  "Jwt": {
    "Key": "..."
  }
}
```

Determine whether values are:

```text
Placeholder
Development-only
Production credential
Environment override
Secret reference
Actually usable
```

Refer to:

```text
docs/web/secrets-exposure.md
```

---

# Environment Variables

Search:

```bash
rg -n \
'Environment\.GetEnvironmentVariable|GetConnectionString|Configuration\[|GetSection\(' \
--glob '*.cs' \
.
```

Environment-variable usage is generally preferable to hard-coded secrets, but environment values can still be exposed through:

```text
Logs
Debug pages
Configuration endpoints
Crash dumps
Container configuration
```

---

# User Secrets

Development applications may use:

```text
UserSecretsId
```

Search:

```bash
rg -n \
'UserSecretsId|AddUserSecrets' \
.
```

Do not assume development user secrets are deployed to production.

---

# Logging

Common APIs:

```text
ILogger
LogInformation
LogWarning
LogError
LogDebug
Console.WriteLine
Serilog
NLog
log4net
```

Search:

```bash
rg -n \
'LogInformation|LogWarning|LogError|LogDebug|Console\.WriteLine|Serilog|NLog|log4net' \
--glob '*.cs' \
.
```

Review whether logs contain:

```text
Passwords
Authorization headers
JWTs
Session IDs
API keys
Secrets
Personal data
Full request bodies
```

---

# Log Injection

Also inspect attacker-controlled values written directly to logs.

Structured logging is generally preferable to constructing log messages through string concatenation.

Example:

```csharp
logger.LogInformation(
    "Login attempt for {Username}",
    username);
```

The actual security implications depend on the logging backend and downstream processing.

---

# Information Disclosure

Search:

```bash
rg -n \
'UseDeveloperExceptionPage|DeveloperExceptionPage|IncludeExceptionDetails|EnableSensitiveDataLogging|EnableDetailedErrors' \
.
```

These settings can expose internal details when enabled in inappropriate environments.

---

# Entity Framework Sensitive Logging

Search:

```bash
rg -n \
'EnableSensitiveDataLogging|EnableDetailedErrors' \
--glob '*.cs' \
.
```

Sensitive-data logging may expose database values or query parameters.

Determine whether it is enabled in production.

---

# Error Handling

Search:

```bash
rg -n \
'UseExceptionHandler|UseDeveloperExceptionPage|catch\s*\(|throw\s' \
--glob '*.cs' \
.
```

Review:

```text
Fail-open behaviour
Stack traces
Sensitive exception messages
Authentication errors
Authorisation errors
Internal paths
Database information
```

---

# Business Logic

Search security-sensitive business terms:

```bash
rg -n -i \
'price|amount|balance|quantity|discount|coupon|credit|refund|approved|verified|status|state|role|permission|tenant' \
--glob '*.cs' \
.
```

Review:

```text
State transitions
Financial calculations
Approval flows
Ownership changes
Privilege changes
Tenant movement
```

These vulnerabilities often have no obvious dangerous sink.

Refer to:

```text
docs/web/business-logic.md
```

---

# Race Conditions

Look for read-modify-write patterns.

Example:

```text
Read Balance
     |
     v
Check Balance
     |
     v
Perform Action
     |
     v
Update Balance
```

Search for:

```text
Transactions
Locks
Concurrency tokens
RowVersion
Semaphore
lock
Interlocked
```

Commands:

```bash
rg -n \
'Transaction|BeginTransaction|RowVersion|ConcurrencyCheck|SemaphoreSlim|lock\s*\(|Interlocked' \
--glob '*.cs' \
.
```

Absence of a lock does not automatically indicate a race condition.

Understand the database transaction and concurrency model.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Rate Limiting

Modern ASP.NET Core provides rate-limiting middleware.

Search:

```bash
rg -n \
'AddRateLimiter|UseRateLimiter|RequireRateLimiting|DisableRateLimiting|RateLimitPartition|FixedWindowRateLimiter|SlidingWindowRateLimiter|TokenBucketRateLimiter|ConcurrencyLimiter' \
--glob '*.cs' \
.
```

Review protection around:

```text
Login
Password reset
MFA
Registration
Search
Expensive reports
API endpoints
```

Refer to:

```text
docs/web/rate-limiting.md
```

---

# Client IP Handling

Search:

```bash
rg -n \
'RemoteIpAddress|X-Forwarded-For|ForwardedHeaders|KnownProxies|KnownNetworks' \
--glob '*.cs' \
.
```

If rate limiting or security decisions rely on client IP addresses, verify proxy trust configuration.

---

# GraphQL

Common .NET GraphQL frameworks include:

```text
Hot Chocolate
GraphQL.NET
```

Search:

```bash
rg -n -i \
'hotchocolate|graphql|AddGraphQL|AddGraphQLServer|QueryType|MutationType|ObjectType<' \
--glob '*.cs' \
.
```

Review:

```text
Resolvers
Authentication
Authorisation
Object-level access
Mutations
Input types
Data loaders
Introspection configuration
Query complexity
Depth
```

Refer to:

```text
docs/web/graphql.md
```

---

# gRPC

Search:

```bash
find . -type f -name '*.proto' -print
```

Then:

```bash
rg -n \
'AddGrpc|MapGrpcService|Grpc\.Core|ServerCallContext' \
--glob '*.cs' \
.
```

Map:

```text
Service
   |
   v
RPC Method
   |
   v
Authentication
   |
   v
Authorisation
   |
   v
Request Message
   |
   v
Sensitive Operation
```

Refer to:

```text
docs/web/grpc-security.md
```

---

# SignalR / WebSockets

Search:

```bash
rg -n \
'Hub\b|Hub<|AddSignalR|MapHub|WebSocket|AcceptWebSocketAsync' \
--glob '*.cs' \
.
```

Review:

```text
Connection authentication
Hub authorisation
Method authorisation
Group membership
Object access
Message input
State-changing methods
```

Refer to:

```text
docs/web/websockets.md
```

---

# HTTP Request Smuggling

Application source alone may not reveal the complete request parsing chain.

Relevant components may include:

```text
Kestrel
IIS
HTTP.sys
Reverse proxy
Load balancer
CDN
API gateway
```

Review deployment configuration as well as application code.

Refer to:

```text
docs/web/http-request-smuggling.md
```

---

# Cache Security

Search:

```bash
rg -n \
'IMemoryCache|IDistributedCache|ResponseCache|OutputCache|AddOutputCache|UseOutputCache|Cache-Control|Vary' \
--glob '*.cs' \
.
```

Review:

```text
Cache keys
User identity
Tenant identity
Query parameters
Headers
Authentication state
Sensitive responses
```

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# Prototype Pollution

Prototype pollution is primarily associated with JavaScript ecosystems rather than normal .NET object semantics.

However, .NET applications may serve or build JavaScript front ends.

Review relevant JavaScript separately.

Refer to:

```text
docs/source-code-review/javascript.md
docs/source-code-review/nodejs.md
docs/web/prototype-pollution.md
```

---

# Dependency Security

Inspect:

```text
*.csproj
packages.config
packages.lock.json
Directory.Packages.props
```

List packages:

```bash
dotnet list package
```

Depending on the installed SDK, vulnerability-aware package listing commands are available.

Consult the current .NET CLI documentation for the SDK version used by the project before relying on a specific command syntax.

Also inspect:

```text
NuGet.config
```

for:

```text
Package sources
Internal feeds
Credentials
Dependency source configuration
```

Refer to:

```text
docs/web/dependency-security.md
```

---

# NuGet Package References

Search:

```bash
rg -n \
'<PackageReference|<PackageVersion|packages\.config' \
.
```

Review:

```text
Old packages
Unsupported packages
Known vulnerable packages
Untrusted package sources
Unexpected dependencies
```

---

# Third-Party JavaScript

ASP.NET applications may include JavaScript dependencies through:

```text
wwwroot/
libman.json
package.json
CDNs
Razor layouts
```

Search:

```bash
find . -type f \( \
-name 'package.json' \
-o -name 'package-lock.json' \
-o -name 'yarn.lock' \
-o -name 'pnpm-lock.yaml' \
-o -name 'libman.json' \
\) -print
```

Also search:

```bash
rg -n \
'<script[^>]+src=' \
--glob '*.cshtml' \
--glob '*.html' \
.
```

Refer to:

```text
docs/web/third-party-javascript.md
```

---

# Blazor

Identify:

```bash
rg -n \
'AddServerSideBlazor|AddRazorComponents|MapBlazorHub|InteractiveServer|InteractiveWebAssembly' \
.
```

Review whether security-sensitive assumptions are enforced only in client-side Blazor code.

Client-side UI restrictions are not server-side authorisation.

Sensitive operations must still be protected at the server/API boundary.

---

# SignalR Hub Authorisation

Example:

```csharp
[Authorize]
public class ChatHub : Hub
{
}
```

Individual hub methods may also require different authorisation.

Review:

```text
Hub-level authorization
Method-level authorization
Group membership
User identifiers
Tenant isolation
```

---

# Background Services

Not all attack paths begin with HTTP requests.

Search:

```bash
rg -n \
'BackgroundService|IHostedService|ExecuteAsync|AddHostedService' \
--glob '*.cs' \
.
```

Background services may process:

```text
Queued user input
Uploaded files
External messages
Webhooks
Database values
```

These can produce second-order vulnerabilities.

---

# Message Queues

Search for technologies such as:

```bash
rg -n -i \
'rabbitmq|kafka|azure\.messaging|servicebus|masstransit|nservicebus|sqs' \
--glob '*.cs' \
.
```

Treat externally influenced message data as potentially untrusted.

---

# Second-Order Vulnerabilities

Example:

```text
POST /profile
      |
      v
Store DisplayName
      |
      v
Database
      |
      v
Background Report Generator
      |
      v
Html.Raw()
```

The original endpoint may safely store the value.

The vulnerability occurs when the stored value later reaches a dangerous sink.

---

# Webhooks

Search:

```bash
rg -n -i \
'webhook|callback|signature|hmac' \
--glob '*.cs' \
.
```

Review:

```text
Signature verification
Replay protection
Timestamp validation
Secret handling
Payload validation
Authorisation
```

Do not trust webhook requests merely because they are intended to originate from a third-party service.

---

# HTTP Clients Created Dynamically

Search:

```bash
rg -n \
'new HttpClient|IHttpClientFactory|CreateClient\(' \
--glob '*.cs' \
.
```

Review configured named clients and handlers.

The destination may be configured elsewhere.

---

# Dependency Injection

ASP.NET Core relies heavily on dependency injection.

Example:

```csharp
builder.Services.AddScoped<IUserService, UserService>();
```

Search:

```bash
rg -n \
'AddSingleton|AddScoped|AddTransient|TryAddSingleton|TryAddScoped|TryAddTransient' \
--glob '*.cs' \
.
```

Understanding DI registrations helps trace:

```text
Controller
    |
    v
Interface
    |
    v
Concrete Service
    |
    v
Repository
    |
    v
Sink
```

---

# Trace Interfaces to Implementations

Suppose a controller uses:

```csharp
private readonly IUserService _userService;
```

Search:

```bash
rg -n \
'IUserService|UserService' \
--glob '*.cs' \
.
```

Determine which implementation is registered.

Do not stop tracing because a controller calls an interface.

---

# Example Source-to-Sink Trace - SQL Injection

```text
POST /api/search
      |
      v
SearchController.Search()
      |
      v
request.Query
      |
      v
SearchService.Search()
      |
      v
Repository.Search()
      |
      v
String concatenation
      |
      v
SqlCommand
```

Questions:

```text
Is the query parameter attacker-controlled?

Is it transformed?

Is it validated?

Is it used as SQL data or SQL syntax?

Is parameterisation used?

Can the route be reached?

What authentication is required?
```

---

# Example Source-to-Sink Trace - SSRF

```text
POST /api/import
      |
      v
ImportRequest.Url
      |
      v
ImportService
      |
      v
HttpClient.GetAsync()
```

Questions:

```text
Can the URL be controlled?

Are schemes restricted?

Are hosts restricted?

What happens after DNS resolution?

Are redirects followed?

Can internal destinations be reached?

What egress restrictions exist?
```

---

# Example Source-to-Sink Trace - Command Injection

```text
POST /api/convert
      |
      v
ConvertRequest.FileName
      |
      v
ConversionService
      |
      v
Command string
      |
      v
Process.Start()
```

Questions:

```text
Is a shell invoked?

Can filename influence command syntax?

Are arguments passed separately?

Can the executable be controlled?

What privileges does the process have?
```

---

# Example Source-to-Sink Trace - IDOR

```text
GET /api/invoices/{id}
      |
      v
id
      |
      v
InvoicesController
      |
      v
db.Invoices.FindAsync(id)
      |
      v
return invoice
```

Critical question:

```text
Where is ownership or permission checked?
```

---

# Example Source-to-Sink Trace - Stored XSS

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
Profile View
      |
      v
Html.Raw(Model.Biography)
```

The source and sink occur in different requests.

---

# ripgrep Quick Review

A broad first-pass command:

```bash
rg -n \
'Request\.(Query|Form|Headers|Cookies|Body|RouteValues|Host)|\[From(Query|Route|Body|Form|Header)|SqlCommand|FromSqlRaw|ExecuteSqlRaw|Process\.Start|ProcessStartInfo|HttpClient|WebClient|WebRequest|File\.(Read|Write|Open)|Path\.Combine|IFormFile|BinaryFormatter|TypeNameHandling|Html\.Raw|Response\.Redirect|Redirect\(' \
--glob '*.cs' \
.
```

This is deliberately broad.

Every match requires context.

---

# Route Search

```bash
rg -n \
'\[Route\(|\[Http(Get|Post|Put|Patch|Delete)|\.Map(Get|Post|Put|Patch|Delete)\(|MapGroup\(' \
--glob '*.cs' \
.
```

---

# Authentication Search

```bash
rg -n \
'AddAuthentication|UseAuthentication|\[Authorize|\[AllowAnonymous|SignInAsync|SignOutAsync|AddJwtBearer|AddCookie' \
--glob '*.cs' \
.
```

---

# Authorisation Search

```bash
rg -n \
'\[Authorize|RequireRole|RequireClaim|AddPolicy|IAuthorizationService|AuthorizeAsync|IsInRole|FindFirstValue' \
--glob '*.cs' \
.
```

---

# SQL Search

```bash
rg -n \
'SqlCommand|FromSqlRaw|ExecuteSqlRaw|SqlQueryRaw|QueryAsync|ExecuteAsync' \
--glob '*.cs' \
.
```

---

# Command Execution Search

```bash
rg -n \
'Process\.Start|ProcessStartInfo|cmd\.exe|powershell|pwsh|UseShellExecute' \
--glob '*.cs' \
.
```

---

# SSRF Search

```bash
rg -n \
'HttpClient|HttpRequestMessage|WebClient|WebRequest|HttpWebRequest|GetAsync|PostAsync|SendAsync|GetStringAsync' \
--glob '*.cs' \
.
```

---

# File Search

```bash
rg -n \
'File\.(Read|Write|Open|Delete|Move|Copy)|FileStream|Directory\.|Path\.Combine|Path\.GetFullPath|IFormFile|CopyToAsync' \
--glob '*.cs' \
.
```

---

# Deserialization Search

```bash
rg -n \
'BinaryFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|TypeNameHandling|DeserializeObject|JsonSerializer\.Deserialize|YamlDotNet' \
--glob '*.cs' \
.
```

---

# XSS Search

```bash
rg -n \
'Html\.Raw|HtmlString|MvcHtmlString|Response\.Write|IHtmlContent' \
--glob '*.cs' \
--glob '*.cshtml' \
.
```

---

# Redirect Search

```bash
rg -n \
'Redirect\(|RedirectPermanent|LocalRedirect|Response\.Redirect|RedirectToAction|RedirectToRoute' \
--glob '*.cs' \
.
```

---

# Secrets Search

```bash
rg -n -i \
'password|passwd|secret|token|api[_-]?key|client[_-]?secret|private[_-]?key|connectionstring' \
.
```

---

# Security Configuration Search

```bash
rg -n \
'UseAuthentication|UseAuthorization|UseCors|UseHsts|UseHttpsRedirection|UseExceptionHandler|UseDeveloperExceptionPage|UseSession|UseForwardedHeaders|UseRateLimiter' \
--glob '*.cs' \
.
```

---

# Find Suspicious Comments

```bash
rg -n -i \
'todo|fixme|hack|temporary|bypass|disable|disabled|security|auth' \
--glob '*.cs' \
.
```

These can reveal unfinished or deliberately bypassed security controls.

---

# Exclude Build Noise

For large repositories:

```bash
rg \
-g '!bin/**' \
-g '!obj/**' \
-g '!packages/**' \
-g '!node_modules/**' \
-g '!wwwroot/lib/**' \
'pattern' \
.
```

---

# Semgrep

Semgrep can complement manual .NET review.

Typical workflow:

```text
.NET Repository
      |
      v
Semgrep
      |
      v
Candidate Findings
      |
      v
Manual Source-to-Sink Review
```

Official documentation:

```text
https://semgrep.dev/docs/
```

Check current language and rule support before relying on a particular rule pack.

Scanner output is not proof of exploitability.

---

# CodeQL

CodeQL supports C# analysis and is particularly useful for semantic data-flow analysis.

Conceptually:

```text
ASP.NET Source
      |
      v
Tainted Data
      |
      v
Application Flow
      |
      v
Dangerous Sink
```

Official documentation:

```text
https://codeql.github.com/docs/
```

C# CodeQL documentation:

```text
https://codeql.github.com/docs/codeql-language-guides/codeql-for-csharp/
```

---

# CodeQL Data Flow

CodeQL can help identify paths such as:

```text
HTTP Input
   |
   v
Controller
   |
   v
Service
   |
   v
SQL Sink
```

or:

```text
HTTP Input
   |
   v
URL
   |
   v
HTTP Client
```

Manual review is still required to determine:

```text
Reachability
Framework behaviour
Validation
Authorisation
Business context
Actual impact
```

---

# Visual Studio / IDE Review

For .NET applications, IDE features are extremely valuable.

Use:

```text
Go to Definition
Find All References
Call Hierarchy
Find Implementations
Type Hierarchy
Search Symbols
```

Example:

```text
Process.Start()
      |
      v
Find All References
      |
      v
Identify Wrapper
      |
      v
Find Callers
      |
      v
Controller
      |
      v
HTTP Route
```

---

# Reverse Sink Analysis

For large .NET applications, starting from dangerous sinks can be efficient.

Example:

```text
Process.Start
      ^
      |
ConversionService
      ^
      |
DocumentController
      ^
      |
POST /convert
```

Other high-value starting points:

```text
SqlCommand
FromSqlRaw
ExecuteSqlRaw
HttpClient
File.Open
File.ReadAllText
Html.Raw
BinaryFormatter
TypeNameHandling
Response.Redirect
```

---

# Forward Source Analysis

Start from:

```text
[FromBody]
[FromQuery]
[FromRoute]
[FromForm]
Request.Query
Request.Form
Request.Headers
```

Then trace where the value goes.

This is useful for high-risk endpoints such as:

```text
Admin
Upload
Import
Export
Report generation
Password reset
Account management
Payment
Webhook
```

---

# Variant Analysis

Once one vulnerability is identified:

```text
Understand Root Cause
       |
       v
Identify Code Pattern
       |
       v
Search Entire Repository
```

Example:

```text
FromSqlRaw(
    "..." + userInput
)
```

Search all:

```bash
rg -n \
'FromSqlRaw|ExecuteSqlRaw|SqlCommand' \
--glob '*.cs' \
.
```

Then manually inspect every candidate.

---

# Compare Similar Controllers

Suppose:

```text
UsersController
OrdersController
InvoicesController
ReportsController
```

all perform object retrieval.

Compare how each performs authorisation.

Example:

```text
OrdersController
    |
    +--> ownership check

InvoicesController
    |
    +--> ownership check

ReportsController
    |
    +--> no ownership check
```

Inconsistency is often a strong lead.

---

# Compare API Versions

Search:

```bash
rg -n \
'api/v1|api/v2|ApiVersion|MapToApiVersion' \
--glob '*.cs' \
.
```

Security controls may differ between:

```text
/api/v1/
/api/v2/
```

Legacy versions deserve particular attention.

---

# Search Admin Functionality

```bash
rg -n -i \
'admin|administrator|superuser|privileged|manage|management' \
--glob '*.cs' \
.
```

Map administrative operations back to routes and authorisation requirements.

---

# Search Role Changes

```bash
rg -n \
'AddToRoleAsync|RemoveFromRoleAsync|RoleManager|UserManager|IsInRoleAsync|Claims' \
--glob '*.cs' \
.
```

Review who can:

```text
Assign roles
Remove roles
Create administrators
Change permissions
Modify claims
```

---

# ASP.NET Identity

Search:

```bash
rg -n \
'UserManager<|SignInManager<|RoleManager<|IdentityUser|AddIdentity|AddDefaultIdentity|AddIdentityCore' \
--glob '*.cs' \
.
```

Map:

```text
Registration
Login
Logout
Password change
Password reset
Email confirmation
MFA
Role management
Account lockout
```

---

# Account Lockout

Search:

```bash
rg -n \
'Lockout|AccessFailedAsync|ResetAccessFailedCountAsync|MaxFailedAccessAttempts|DefaultLockoutTimeSpan' \
--glob '*.cs' \
.
```

Review the complete authentication flow.

Refer to:

```text
docs/web/rate-limiting.md
docs/web/authentication.md
```

---

# Registration

Search:

```bash
rg -n -i \
'register|registration|createuser|createasync' \
--glob '*.cs' \
.
```

Review:

```text
Role assignment
Tenant assignment
Email verification
Mass assignment
Duplicate accounts
Invitation logic
Privilege fields
```

---

# Email Confirmation

Search:

```bash
rg -n \
'GenerateEmailConfirmationTokenAsync|ConfirmEmailAsync|EmailConfirmed' \
--glob '*.cs' \
.
```

Review whether confirmation state protects security-sensitive functionality where required.

---

# URL Generation

Search:

```bash
rg -n \
'Url\.Action|Url\.RouteUrl|LinkGenerator|GetUriByAction|GetUriByRouteValues' \
--glob '*.cs' \
.
```

Pay particular attention when generating:

```text
Password reset URLs
Email confirmation URLs
OAuth callbacks
External links
```

and determine how host/scheme are selected.

---

# Response Headers

Search:

```bash
rg -n \
'Response\.Headers|Headers\.Append|Headers\.Add' \
--glob '*.cs' \
.
```

Trace attacker-controlled values used in response headers.

Potential concerns include:

```text
Header injection
CORS
Caching
Content-Disposition
Redirects
Security headers
```

---

# Content-Disposition

Search:

```bash
rg -n \
'Content-Disposition|ContentDispositionHeaderValue|FileDownloadName' \
--glob '*.cs' \
.
```

Review attacker-controlled filenames and framework encoding behaviour.

---

# Header Injection

Modern frameworks commonly restrict invalid header characters, but do not rely on assumptions.

Trace:

```text
Request Input
      |
      v
Response Header Value
```

and understand the framework's validation behaviour.

---

# API Model Validation

For APIs, identify request DTOs.

Example:

```csharp
public record CreateUserRequest(
    string Username,
    string Email);
```

Then map:

```text
Request DTO
    |
    v
Validation
    |
    v
Domain Mapping
    |
    v
Database Object
```

DTOs help make accepted fields explicit but do not automatically enforce all security rules.

---

# Unknown JSON Properties

Review serializer configuration:

```bash
rg -n \
'JsonOptions|JsonSerializerOptions|AddJsonOptions|AddNewtonsoftJson|MissingMemberHandling|UnmappedMemberHandling' \
--glob '*.cs' \
.
```

Determine whether unexpected fields are:

```text
Ignored
Rejected
Mapped
Processed by custom converters
```

Security-sensitive APIs should have an intentional policy.

---

# Content-Type Handling

Review actions accepting:

```text
JSON
XML
Form data
Multipart
```

Search:

```bash
rg -n \
'\[Consumes\(|AddXmlSerializerFormatters|AddXmlDataContractSerializerFormatters' \
--glob '*.cs' \
.
```

Different parsers may create different validation or security behaviour.

---

# Request Size Limits

Search:

```bash
rg -n \
'RequestSizeLimit|DisableRequestSizeLimit|MaxRequestBodySize|MultipartBodyLengthLimit|FormOptions' \
--glob '*.cs' \
.
```

Review endpoints processing:

```text
Uploads
Large JSON
XML
Archives
Images
Documents
```

Large or complex inputs may create availability concerns.

Stress testing requires explicit authorisation.

---

# DisableRequestSizeLimit

Search:

```bash
rg -n \
'DisableRequestSizeLimit' \
--glob '*.cs' \
.
```

Review why limits are disabled and whether other controls exist.

Do not automatically classify this as a vulnerability.

---

# Regular Expressions

Search:

```bash
rg -n \
'Regex\.|new Regex\(' \
--glob '*.cs' \
.
```

Review regex used on attacker-controlled input for:

```text
Validation bypass
Anchoring mistakes
Unexpected newline behaviour
Excessive backtracking
Availability impact
```

Do not assume every complex regex is vulnerable to ReDoS.

---

# URL Validation

Search:

```bash
rg -n \
'Uri\.TryCreate|new Uri\(|UriBuilder|IsWellFormedUriString|IsLocalUrl' \
--glob '*.cs' \
.
```

For security-sensitive URL validation, understand:

```text
Scheme
Hostname
Port
Credentials
DNS
Redirects
Canonical representation
```

A syntactically valid URL is not necessarily an authorised destination.

---

# IP Address Handling

Search:

```bash
rg -n \
'IPAddress\.Parse|IPAddress\.TryParse|Dns\.GetHost|GetHostAddressesAsync|GetHostEntry' \
--glob '*.cs' \
.
```

Relevant for:

```text
SSRF
Allowlisting
Proxy trust
Rate limiting
Network restrictions
```

---

# Email Validation

Search:

```bash
rg -n \
'EmailAddressAttribute|MailAddress|EmailAddress' \
--glob '*.cs' \
.
```

Avoid assuming that a restrictive regex is necessarily better.

Validation should match the application's actual business requirements.

---

# Dynamic Assembly Loading

Search:

```bash
rg -n \
'Assembly\.Load|Assembly\.LoadFrom|Assembly\.LoadFile|Activator\.CreateInstance|Type\.GetType' \
--glob '*.cs' \
.
```

Review whether attacker-controlled input influences:

```text
Assembly path
Type name
Plugin selection
Dynamic loading
```

These can become high-risk sinks in plugin or extension systems.

---

# Reflection

Search:

```bash
rg -n \
'GetType\(|GetMethod\(|Invoke\(|Activator\.CreateInstance|MakeGenericType' \
--glob '*.cs' \
.
```

Reflection itself is not a vulnerability.

Review attacker influence over:

```text
Type selection
Method selection
Arguments
Assembly selection
```

---

# Dynamic C# Execution

Search:

```bash
rg -n -i \
'csharpcodeprovider|codedomprovider|compileassembly|roslyn|csharpscript|script\.evaluate|script\.run' \
--glob '*.cs' \
.
```

Applications intentionally compiling or executing dynamic code require careful trust-boundary analysis.

---

# Expression Evaluation

Search libraries and functionality involving:

```text
Dynamic LINQ
Expression parsers
Rule engines
Scripting engines
Template engines
```

Search:

```bash
rg -n -i \
'dynamiclinq|system\.linq\.dynamic|expressionparser|script|evaluate' \
--glob '*.cs' \
.
```

Trace attacker-controlled expressions.

---

# LINQ Dynamic Ordering

Example:

```csharp
query = query.OrderBy(sort);
```

with dynamic LINQ libraries may interpret strings as expressions.

Review:

```text
Library
Allowed syntax
Input control
Version
Configuration
```

Do not assume ordinary strongly typed LINQ is affected.

---

# Security Review by Vulnerability

A useful .NET review matrix:

| Vulnerability | High-Value .NET Review Targets |
|---|---|
| SQL Injection | `SqlCommand`, `FromSqlRaw`, `ExecuteSqlRaw`, Dapper raw SQL |
| NoSQL Injection | MongoDB filters, dynamic BSON/query construction |
| LDAP Injection | `DirectorySearcher.Filter`, LDAP filter construction |
| Command Injection | `Process.Start`, `ProcessStartInfo`, shell invocation |
| SSTI | Dynamic Razor/template compilation |
| XSS | `Html.Raw`, `HtmlString`, raw response output |
| SSRF | `HttpClient`, `WebClient`, `WebRequest` |
| Path Traversal | `File.*`, `Directory.*`, `Path.Combine` |
| File Upload | `IFormFile`, `CopyToAsync`, filename handling |
| XXE | XML parser configuration |
| Deserialization | `BinaryFormatter`, legacy formatters, polymorphic JSON |
| IDOR/BOLA | `FindAsync(id)`, object lookup without ownership scope |
| Mass Assignment | Domain entities accepted directly from requests |
| Open Redirect | `Redirect(userValue)` |
| CSRF | Anti-forgery configuration and state-changing cookie-auth endpoints |
| CORS | `AddCors`, `AllowAnyOrigin`, dynamic origin policy |
| JWT | `TokenValidationParameters`, claims and signing keys |
| OAuth/OIDC | `AddOpenIdConnect`, callback and token validation |
| SAML | SAML middleware/library configuration |
| Race Conditions | Read-check-write operations, transactions |
| Rate Limiting | `AddRateLimiter`, endpoint policies |
| Secrets | `appsettings`, source, CI/CD, Git history |
| Dependency Security | `.csproj`, NuGet packages |
| Information Disclosure | Developer exception pages, sensitive logging |

---

# Vulnerable vs Safe Patterns

Do not classify code based solely on API names.

Use:

```text
SOURCE
   |
   v
DATA FLOW
   |
   v
CONTROL
   |
   v
SINK
```

---

# SQL Example

Review candidate:

```csharp
var sql =
    "SELECT * FROM Users WHERE Username = '" +
    username +
    "'";

var cmd = new SqlCommand(sql, connection);
```

Prefer parameterisation:

```csharp
var cmd = new SqlCommand(
    "SELECT * FROM Users WHERE Username = @username",
    connection);

cmd.Parameters.AddWithValue("@username", username);
```

---

# Command Example

Higher-risk construction:

```csharp
var command = "/c tool.exe " + userValue;

Process.Start("cmd.exe", command);
```

Prefer avoiding shell construction and passing arguments structurally where the application genuinely needs to launch a process.

---

# SSRF Example

Review candidate:

```csharp
await client.GetAsync(request.Url);
```

A safer design depends on the business requirement but may involve:

```text
Server-side destination mapping
Explicit destination allowlists
Scheme restrictions
Resolved-address checks
Redirect controls
Network egress restrictions
```

Input validation alone does not fully solve SSRF.

---

# Path Example

Review candidate:

```csharp
var path =
    Path.Combine(
        uploadDirectory,
        request.FileName);

return System.IO.File.ReadAllBytes(path);
```

Review whether the resolved path can escape the intended directory.

---

# XSS Example

Review candidate:

```html
@Html.Raw(Model.UserContent)
```

Safer output depends on whether HTML is actually required.

For normal text:

```html
@Model.UserContent
```

allows Razor's normal encoding behaviour.

If rich HTML is intentionally supported, use an appropriate HTML sanitisation strategy before rendering trusted sanitised HTML.

---

# Mass Assignment Example

Higher-risk:

```csharp
public async Task<IActionResult> Update(User user)
{
    db.Users.Update(user);

    await db.SaveChangesAsync();

    return Ok();
}
```

Prefer an explicit DTO:

```csharp
public class UpdateProfileRequest
{
    public string DisplayName { get; set; }
}
```

and explicit mapping:

```csharp
user.DisplayName = request.DisplayName;
```

Security-sensitive fields are then not automatically exposed for binding.

---

# IDOR Example

Review candidate:

```csharp
var document =
    await db.Documents.FindAsync(id);
```

Ask:

```text
Who owns the document?

What permission is required?

Where is that permission enforced?
```

---

# Source Code Review Checklist

## Application

```text
[ ] Solution files identified
[ ] Projects identified
[ ] Target frameworks identified
[ ] ASP.NET version identified
[ ] Entry point identified
[ ] Middleware pipeline mapped
[ ] Dependency injection registrations reviewed
```

## Routes

```text
[ ] Controllers mapped
[ ] Attribute routes mapped
[ ] Minimal APIs mapped
[ ] Route groups mapped
[ ] Razor Pages mapped
[ ] API versions mapped
[ ] Admin routes identified
[ ] Debug routes identified
```

## Authentication

```text
[ ] Authentication scheme identified
[ ] [Authorize] usage reviewed
[ ] [AllowAnonymous] reviewed
[ ] Cookie authentication reviewed
[ ] JWT authentication reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
```

## Authorisation

```text
[ ] Roles identified
[ ] Policies identified
[ ] Resource-based authorisation reviewed
[ ] Object ownership checks reviewed
[ ] Tenant isolation reviewed
[ ] Administrative actions reviewed
[ ] Role-changing functionality reviewed
```

## Input

```text
[ ] Query input reviewed
[ ] Route values reviewed
[ ] Request body models reviewed
[ ] Form input reviewed
[ ] Headers reviewed
[ ] Cookies reviewed
[ ] File uploads reviewed
[ ] Model validation reviewed
[ ] Custom validators reviewed
```

## Injection

```text
[ ] ADO.NET queries reviewed
[ ] EF raw SQL reviewed
[ ] Dapper queries reviewed
[ ] NoSQL query construction reviewed
[ ] LDAP filters reviewed
[ ] Process execution reviewed
[ ] Dynamic template evaluation reviewed
[ ] Dynamic code/reflection reviewed
```

## Server-Side

```text
[ ] HttpClient usage reviewed
[ ] URL validation reviewed
[ ] File operations reviewed
[ ] Path handling reviewed
[ ] Upload handling reviewed
[ ] Archive extraction reviewed
[ ] XML parsers reviewed
[ ] Deserialisation reviewed
```

## Client-Side / HTTP

```text
[ ] Html.Raw reviewed
[ ] Raw HTML output reviewed
[ ] Redirects reviewed
[ ] CSRF protection reviewed
[ ] CORS reviewed
[ ] Host handling reviewed
[ ] Forwarded headers reviewed
[ ] Security headers reviewed
[ ] Cache behaviour reviewed
```

## Business Logic

```text
[ ] Financial calculations reviewed
[ ] State transitions reviewed
[ ] Approval workflows reviewed
[ ] Role transitions reviewed
[ ] Tenant transitions reviewed
[ ] Race conditions considered
[ ] Rate limiting reviewed
```

## Configuration

```text
[ ] appsettings reviewed
[ ] Environment-specific settings reviewed
[ ] Debug configuration reviewed
[ ] Secrets searched
[ ] Connection strings reviewed
[ ] Logging reviewed
[ ] Sensitive-data logging reviewed
[ ] Error handling reviewed
```

## Dependencies

```text
[ ] .csproj files reviewed
[ ] NuGet packages reviewed
[ ] Lockfiles reviewed
[ ] Unsupported dependencies identified
[ ] Third-party JavaScript reviewed
```

## Analysis

```text
[ ] ripgrep searches performed
[ ] IDE references reviewed
[ ] Semgrep considered
[ ] CodeQL considered
[ ] Git history reviewed
[ ] Variant analysis performed
[ ] Candidate findings manually validated
```

---

# Quick Review Command Set

## Routes

```bash
rg -n \
'\[Route\(|\[Http(Get|Post|Put|Patch|Delete)|\.Map(Get|Post|Put|Patch|Delete)\(|MapGroup\(' \
--glob '*.cs' \
.
```

## Sources

```bash
rg -n \
'Request\.(Query|Form|Headers|Cookies|Body|RouteValues|Host)|\[From(Query|Route|Body|Form|Header)' \
--glob '*.cs' \
.
```

## Authentication / Authorisation

```bash
rg -n \
'\[Authorize|\[AllowAnonymous|AddAuthentication|AddAuthorization|AddPolicy|IAuthorizationService|AuthorizeAsync|IsInRole' \
--glob '*.cs' \
.
```

## SQL

```bash
rg -n \
'SqlCommand|FromSqlRaw|ExecuteSqlRaw|SqlQueryRaw|QueryAsync|ExecuteAsync' \
--glob '*.cs' \
.
```

## Commands

```bash
rg -n \
'Process\.Start|ProcessStartInfo|cmd\.exe|powershell|pwsh|UseShellExecute' \
--glob '*.cs' \
.
```

## Network

```bash
rg -n \
'HttpClient|HttpRequestMessage|WebClient|WebRequest|HttpWebRequest|GetAsync|PostAsync|SendAsync' \
--glob '*.cs' \
.
```

## Files

```bash
rg -n \
'File\.(Read|Write|Open|Delete|Move|Copy)|FileStream|Directory\.|Path\.Combine|IFormFile|CopyToAsync' \
--glob '*.cs' \
.
```

## Deserialization

```bash
rg -n \
'BinaryFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|TypeNameHandling|DeserializeObject|JsonSerializer\.Deserialize' \
--glob '*.cs' \
.
```

## XSS

```bash
rg -n \
'Html\.Raw|HtmlString|MvcHtmlString|Response\.Write' \
--glob '*.cs' \
--glob '*.cshtml' \
.
```

## Redirects

```bash
rg -n \
'Redirect\(|LocalRedirect|Response\.Redirect|RedirectToAction|RedirectToRoute' \
--glob '*.cs' \
.
```

## Secrets

```bash
rg -n -i \
'password|passwd|secret|token|api[_-]?key|client[_-]?secret|private[_-]?key|connectionstring' \
.
```

## Security Configuration

```bash
rg -n \
'UseAuthentication|UseAuthorization|UseCors|UseHsts|UseHttpsRedirection|UseDeveloperExceptionPage|UseForwardedHeaders|UseRateLimiter' \
--glob '*.cs' \
.
```

---

# Recommended Manual Review Order

For an unfamiliar .NET application:

```text
.sln / .csproj
      |
      v
Program.cs / Startup.cs
      |
      v
Middleware
      |
      v
Controllers / Minimal APIs
      |
      v
Authentication
      |
      v
Authorisation
      |
      v
Request DTOs
      |
      v
Services
      |
      v
Repositories
      |
      v
Dangerous Sinks
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
Program.cs
Startup.cs

Controllers/*.cs
Pages/*.cshtml.cs

Middleware/*.cs
Filters/*.cs

Services/*.cs
Repositories/*.cs

Data/*.cs

Models/*.cs
DTOs/*.cs

appsettings.json
appsettings.*.json

web.config

*.csproj
Directory.Packages.props
packages.lock.json

Dockerfile
docker-compose.yml

CI/CD configuration
```

---

# High-Value Search Terms

```text
Authorize
AllowAnonymous

Admin
Role
Permission
Tenant
Owner

FromSqlRaw
ExecuteSqlRaw
SqlCommand

Process.Start
ProcessStartInfo

HttpClient
WebRequest

File.Read
File.Write
Path.Combine

IFormFile

BinaryFormatter
TypeNameHandling

Html.Raw

Redirect

Request.Host
X-Forwarded-Host

Jwt
OAuth
OpenIdConnect
Saml

PasswordReset
TwoFactor

Secret
Token
ApiKey
ConnectionString
```

---

# Finding Validation

A source-code match becomes increasingly significant as these questions become true:

```text
1. Is the code reachable?

             YES
              |
              v

2. Can an attacker influence the source?

             YES
              |
              v

3. Does the value reach the sink?

             YES
              |
              v

4. Are security controls missing or ineffective?

             YES
              |
              v

5. Can the behaviour be demonstrated safely?

             YES
              |
              v

6. Does it create meaningful security impact?

             YES
              |
              v

       CONFIRMED FINDING
```

---

# Evidence Template

For every .NET source finding record:

```text
Route:

HTTP Method:

Controller / Endpoint:

Source File:

Source Line:

Source:

Data Flow:

Security Controls:

Sink:

Authentication:

Authorisation:

Reachability:

Dynamic Validation:

Impact:
```

---

# Example Finding - SQL Injection

```text
Title:
SQL Injection in User Search

Route:
GET /api/users/search

Source:
Query parameter "name"

Controller:
UsersController.Search()

Data Flow:

Request.Query["name"]
        |
        v
UsersController
        |
        v
UserRepository.Search()
        |
        v
SQL string concatenation
        |
        v
SqlCommand

Security Control:
No parameterisation is used for the user-controlled value.

Impact:
An attacker able to access the endpoint may be able to alter the structure of the database query.

Recommendation:
Use parameterised database queries and avoid constructing SQL syntax through concatenation of untrusted data.
```

---

# Example Finding - IDOR

```text
Title:
Missing Object-Level Authorisation on Invoice Endpoint

Route:
GET /api/invoices/{id}

Source:
Route parameter "id"

Data Flow:

{id}
 |
 v
InvoicesController
 |
 v
db.Invoices.FindAsync(id)
 |
 v
Invoice returned

Authentication:
Required.

Authorisation:
No ownership or permission check was identified before the invoice was returned.

Impact:
An authenticated user may be able to access invoices belonging to other users by changing the object identifier.

Recommendation:
Enforce object-level authorisation for every invoice operation. Scope database queries to objects the authenticated principal is authorised to access or perform an equivalent policy-based authorisation check before returning the object.
```

---

# Example Finding - SSRF

```text
Title:
Server-Side Request Forgery Through Import URL

Route:
POST /api/import

Source:
ImportRequest.Url

Data Flow:

ImportRequest.Url
      |
      v
ImportController
      |
      v
ImportService
      |
      v
HttpClient.GetAsync()

Security Control:
No destination restriction was identified.

Impact:
An authenticated user may be able to cause the server to make requests to attacker-selected destinations.

Recommendation:
Where possible, map user choices to server-controlled destinations. Otherwise implement strict destination policy, validate resolved destinations, control redirects and apply network-level egress restrictions.
```

---

# Common Review Mistakes

## Treating Every Sink as Vulnerable

Incorrect:

```text
Process.Start found
    =
Command Injection
```

Correct:

```text
Process.Start found
      |
      v
Trace Arguments
      |
      v
Attacker Controlled?
      |
      v
Shell?
      |
      v
Security Controls?
      |
      v
Determine Exploitability
```

---

## Treating Every Raw SQL API as Vulnerable

`FromSqlRaw()` is a high-value review target.

It is not automatically SQL injection.

Determine how arguments are supplied.

---

## Assuming Entity Framework Prevents All SQL Injection

LINQ parameterisation reduces common injection risks.

But applications can still use:

```text
FromSqlRaw
ExecuteSqlRaw
Dynamic SQL fragments
Dapper
ADO.NET
Stored procedure construction
```

---

## Assuming Model Binding Means Validation

Model binding answers:

```text
How does request data become an object?
```

Validation answers:

```text
Is that value acceptable?
```

Authorisation answers:

```text
May this user perform this operation?
```

These are different controls.

---

## Assuming Authentication Implies Authorisation

```csharp
[Authorize]
```

may only require an authenticated user.

It does not necessarily mean:

```text
User owns requested object
```

or:

```text
User has permission for this action
```

---

## Ignoring Minimal APIs

Modern ASP.NET Core applications may contain substantial functionality in:

```text
Program.cs
Endpoint extension methods
MapGroup()
MapGet()
MapPost()
```

Do not search only controllers.

---

## Ignoring Middleware

Authentication and authorisation may be implemented outside controllers.

Likewise, a controller may appear protected while middleware behaviour creates an exception.

---

## Ignoring Dependency Injection

The interesting sink may be hidden behind:

```text
Interface
    |
    v
Service
    |
    v
Repository
```

Trace the actual implementation.

---

## Ignoring Configuration

Behaviour may change through:

```text
appsettings.json
appsettings.Production.json
Environment variables
Feature flags
Deployment configuration
```

---

## Ignoring Git History

A secret removed from the current source may still exist in repository history and may still be valid.

---

## Ignoring Business Logic

A clean SAST scan does not mean the application is secure.

Issues such as:

```text
IDOR
Role bypass
Workflow bypass
Race conditions
Tenant isolation
Price manipulation
Approval bypass
```

often require manual understanding.

---

# Final .NET Source Review Model

```text
                 ASP.NET APPLICATION
                         |
                         v
                  ROUTE DISCOVERY
                         |
                         v
                 HTTP ENTRY POINT
                         |
                         v
                 MODEL BINDING
                         |
                         v
                 USER-CONTROLLED
                      SOURCE
                         |
                         v
                 DATA-FLOW TRACE
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
      Validation     Authorisation   Business Rules
          |              |              |
          +--------------+--------------+
                         |
                         v
                 SECURITY-SENSITIVE
                       SINK
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
       SQL            Process           HTTP
        |                |                |
        v                v                v
      SQLi          Command Injection    SSRF

        File           Template       Deserialiser
          |               |               |
          v               v               v
    Traversal/Upload     XSS/SSTI     Deserialisation
```

The fundamental question remains:

```text
Can attacker-controlled data reach a security-sensitive operation
without an effective security boundary?
```

Then determine:

```text
Reachability
+
Attacker control
+
Security controls
+
Exploitability
+
Impact
```

Only after those have been established should a source-code pattern be treated as a confirmed security finding.

---

# References

## Microsoft ASP.NET Core Security

[Microsoft ASP.NET Core Security](https://learn.microsoft.com/en-us/aspnet/core/security/)

## ASP.NET Core Authentication

[ASP.NET Core Authentication](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/)

## ASP.NET Core Authorization

[ASP.NET Core Authorization](https://learn.microsoft.com/en-us/aspnet/core/security/authorization/introduction)

## ASP.NET Core Anti-Request-Forgery

[ASP.NET Core Anti-Request-Forgery](https://learn.microsoft.com/en-us/aspnet/core/security/anti-request-forgery)

## ASP.NET Core CORS

[ASP.NET Core CORS](https://learn.microsoft.com/en-us/aspnet/core/security/cors)

## ASP.NET Core Data Protection

[ASP.NET Core Data Protection](https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/)

## ASP.NET Core File Uploads

[ASP.NET Core File Uploads](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/file-uploads)

## ASP.NET Core Model Binding

[ASP.NET Core Model Binding](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/model-binding)

## ASP.NET Core Model Validation

[ASP.NET Core Model Validation](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation)

## ASP.NET Core Rate Limiting

[ASP.NET Core Rate Limiting](https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit)

## Entity Framework Core SQL Queries

[Entity Framework Core SQL Queries](https://learn.microsoft.com/en-us/ef/core/querying/sql-queries)

## .NET ProcessStartInfo

[.NET ProcessStartInfo](https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.processstartinfo)

## .NET HttpClient

[.NET HttpClient](https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient)

## .NET BinaryFormatter Security Guide

[.NET BinaryFormatter Security Guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide)

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)

## OWASP ASVS

[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)

## CWE

[CWE](https://cwe.mitre.org/)

## Semgrep

[Semgrep](https://semgrep.dev/)

## CodeQL for C#

[CodeQL for C](https://codeql.github.com/docs/codeql-language-guides/codeql-for-csharp/)

## ripgrep

[ripgrep](https://github.com/BurntSushi/ripgrep)

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
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

docs/web/sql-injection.md
docs/web/nosql-injection.md
docs/web/ldap-injection.md
docs/web/command-injection.md
docs/web/ssti.md

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
docs/web/xxe.md
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
docs/web/third-party-javascript.md
```
