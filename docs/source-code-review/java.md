# Java / Spring Source Code Review

Java source code review involves identifying attacker-controlled input, tracing it through the application, identifying security controls, and determining whether that data can reach security-sensitive operations in an unsafe way.

This note focuses primarily on:

```text
Java
Spring Boot
Spring MVC
Spring WebFlux
Spring Security
Spring Data
JPA
Hibernate
JDBC
Jakarta Servlet
Jakarta REST / JAX-RS
Jackson
Thymeleaf
JSP
FreeMarker
XML processing
Java serialization
```

The primary review model is:

```text
HTTP Request
     |
     v
Route / Controller
     |
     v
Request Binding
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
Service Layer
     |
     v
Repository / Business Logic
     |
     v
SECURITY-SENSITIVE SINK
```

The objective is not:

```text
grep Runtime.exec()
        =
Command Injection
```

Instead:

```text
SOURCE
   |
   v
DATA FLOW
   |
   v
TRANSFORMATIONS
   |
   v
SECURITY CONTROLS
   |
   v
SINK
   |
   v
EXPLOITABILITY
   |
   v
IMPACT
```

!!! warning "Authorised Security Testing"
    Perform source code review and dynamic validation only against applications and source code for which you have explicit authorisation. Repositories can contain credentials, API keys, personal information, cryptographic material, internal infrastructure details and other sensitive information.

---

# Review Strategy

A practical Java review can be approached as:

```text
1. Identify projects and modules

2. Identify Java version

3. Identify frameworks

4. Identify application entry points

5. Enumerate routes

6. Map filters and interceptors

7. Map authentication

8. Map authorisation

9. Identify attacker-controlled sources

10. Identify validation

11. Identify dangerous sinks

12. Trace source-to-sink paths

13. Review business logic

14. Review configuration and secrets

15. Review dependencies

16. Run static analysis

17. Perform variant analysis

18. Validate findings dynamically where authorised
```

---

# Identify the Application

Start by locating build and project files.

```bash
find . -type f \( \
-name 'pom.xml' \
-o -name 'build.gradle' \
-o -name 'build.gradle.kts' \
-o -name 'settings.gradle' \
-o -name 'settings.gradle.kts' \
-o -name 'gradle.properties' \
-o -name 'mvnw' \
-o -name 'gradlew' \
\) -print
```

Common Java build systems include:

```text
Maven
Gradle
```

---

# Maven

The primary Maven project file is:

```text
pom.xml
```

Inspect:

```bash
cat pom.xml
```

Look for dependencies such as:

```text
spring-boot
spring-web
spring-webmvc
spring-webflux
spring-security
spring-data-jpa
hibernate
jackson
thymeleaf
freemarker
mysql
postgresql
mongodb
ldap
```

Quick search:

```bash
rg -n -i \
'spring|hibernate|jackson|thymeleaf|freemarker|security|jdbc|mysql|postgres|mongodb|ldap' \
--glob 'pom.xml' \
.
```

---

# Gradle

Inspect:

```text
build.gradle
build.gradle.kts
```

Search:

```bash
rg -n -i \
'spring|hibernate|jackson|thymeleaf|freemarker|security|jdbc|mysql|postgres|mongodb|ldap' \
--glob 'build.gradle' \
--glob 'build.gradle.kts' \
.
```

---

# Repository Structure

A typical Spring Boot application may look like:

```text
src/
└── main/
    ├── java/
    │   └── com/example/application/
    │       ├── Application.java
    │       ├── controller/
    │       ├── service/
    │       ├── repository/
    │       ├── model/
    │       ├── dto/
    │       ├── security/
    │       ├── config/
    │       ├── filter/
    │       └── util/
    │
    └── resources/
        ├── application.properties
        ├── application.yml
        ├── templates/
        └── static/
```

High-value directories include:

```text
controller/
service/
repository/
security/
config/
filter/
model/
dto/
util/
templates/
```

---

# Identify Spring Boot

Search:

```bash
rg -n \
'SpringApplication\.run|@SpringBootApplication|@EnableAutoConfiguration' \
--glob '*.java' \
.
```

Typical application:

```java
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

This usually identifies the root package used for component scanning.

---

# Identify Frameworks

Search annotations:

```bash
rg -n \
'@RestController|@Controller|@Service|@Repository|@Component|@Configuration' \
--glob '*.java' \
.
```

These provide a quick architectural map.

---

# Application Architecture

A common architecture is:

```text
HTTP Request
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
Database
```

Example:

```text
UsersController
       |
       v
UserService
       |
       v
UserRepository
       |
       v
Database
```

Security controls may exist at any of these layers.

---

# Route Discovery

Route enumeration should be one of the first major tasks.

Spring MVC commonly uses:

```text
@RequestMapping
@GetMapping
@PostMapping
@PutMapping
@PatchMapping
@DeleteMapping
```

Search:

```bash
rg -n \
'@(RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping)' \
--glob '*.java' \
.
```

---

# Controller Discovery

Search:

```bash
rg -n \
'@(RestController|Controller)' \
--glob '*.java' \
.
```

Example:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        ...
    }
}
```

Route:

```text
GET /api/users/{id}
```

Remember to combine:

```text
Class-level mapping
+
Method-level mapping
```

---

# RequestMapping

Example:

```java
@RequestMapping(
    value = "/users",
    method = RequestMethod.POST
)
```

Search:

```bash
rg -n \
'RequestMethod\.(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)' \
--glob '*.java' \
.
```

---

# JAX-RS / Jakarta REST

Not every Java web application uses Spring MVC.

JAX-RS applications commonly use:

```text
@Path
@GET
@POST
@PUT
@DELETE
@PATCH
@QueryParam
@PathParam
@HeaderParam
@CookieParam
```

Search:

```bash
rg -n \
'@(Path|GET|POST|PUT|DELETE|PATCH|QueryParam|PathParam|HeaderParam|CookieParam)' \
--glob '*.java' \
.
```

Be careful because annotations such as `@Path` may occur in unrelated libraries.

Review imports.

---

# Servlet Applications

Legacy applications may use:

```text
HttpServlet
doGet()
doPost()
doPut()
doDelete()
@WebServlet
web.xml
```

Search:

```bash
rg -n \
'HttpServlet|doGet\(|doPost\(|doPut\(|doDelete\(|@WebServlet' \
--glob '*.java' \
.
```

Also inspect:

```bash
find . -type f -name 'web.xml' -print
```

---

# Build a Route Inventory

Create a table:

| Method | Route | Handler | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/api/users/{id}` | `getUser()` | Required | Object-level |
| POST | `/api/users` | `createUser()` | Required | Admin |
| POST | `/login` | `login()` | Public | N/A |
| POST | `/upload` | `upload()` | Required | User |
| GET | `/admin` | `admin()` | Required | Admin |

This becomes the basis of the source review.

---

# Sources - Attacker-Controlled Input

Spring applications commonly obtain input using:

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

Search:

```bash
rg -n \
'@(RequestParam|PathVariable|RequestBody|RequestHeader|CookieValue|RequestPart|ModelAttribute)' \
--glob '*.java' \
.
```

---

# Request Parameters

Example:

```java
@GetMapping("/search")
public List<User> search(
        @RequestParam String query) {

    ...
}
```

Source:

```text
query
```

Trace it through:

```text
Controller
Service
Repository
Sink
```

---

# Path Variables

Example:

```java
@GetMapping("/users/{id}")
public User getUser(
        @PathVariable Long id) {

    ...
}
```

Path variables are particularly important for:

```text
IDOR
BOLA
Authorisation
Business logic
Path traversal
```

---

# Request Body

Example:

```java
@PostMapping("/users")
public User create(
        @RequestBody CreateUserRequest request) {

    ...
}
```

Inspect the DTO:

```java
public class CreateUserRequest {

    private String username;
    private String email;
}
```

Determine which properties clients can supply.

---

# Request Headers

Example:

```java
@GetMapping("/example")
public String example(
        @RequestHeader("X-Forwarded-Host") String host) {

    ...
}
```

Search:

```bash
rg -n \
'@RequestHeader|getHeader\(' \
--glob '*.java' \
.
```

Headers may influence:

```text
Authentication
Host handling
Proxy logic
Logging
Redirects
URL generation
Rate limiting
```

---

# Cookies

Search:

```bash
rg -n \
'@CookieValue|getCookies\(|Cookie\b' \
--glob '*.java' \
.
```

Determine whether cookies influence security decisions.

---

# HttpServletRequest

Legacy and modern applications may access request data directly.

Search:

```bash
rg -n \
'HttpServletRequest|getParameter\(|getParameterValues\(|getParameterMap\(|getHeader\(|getCookies\(' \
--glob '*.java' \
.
```

Example:

```java
String username =
    request.getParameter("username");
```

---

# Multipart Files

Search:

```bash
rg -n \
'MultipartFile|getOriginalFilename|getInputStream|transferTo\(' \
--glob '*.java' \
.
```

Uploaded file data should be considered attacker-controlled.

---

# Model Binding

Spring can automatically bind request properties to Java objects.

Example:

```java
@PostMapping("/profile")
public String update(
        @ModelAttribute User user) {

    ...
}
```

Review whether clients can modify fields such as:

```text
role
admin
enabled
verified
tenantId
ownerId
balance
status
```

This is relevant to mass assignment.

---

# Input Validation

Common Jakarta Bean Validation annotations include:

```text
@NotNull
@NotBlank
@NotEmpty
@Size
@Min
@Max
@Pattern
@Email
@Positive
@Negative
@Past
@Future
```

Search:

```bash
rg -n \
'@(NotNull|NotBlank|NotEmpty|Size|Min|Max|Pattern|Email|Positive|Negative|Past|Future)' \
--glob '*.java' \
.
```

---

# @Valid and @Validated

Search:

```bash
rg -n \
'@Valid|@Validated' \
--glob '*.java' \
.
```

Example:

```java
@PostMapping("/users")
public User create(
        @Valid @RequestBody CreateUserRequest request) {

    ...
}
```

The presence of validation annotations on a DTO does not necessarily mean the relevant validation path is executed.

Trace how the object is bound and validated.

---

# Custom Validators

Search:

```bash
rg -n \
'ConstraintValidator|@Constraint|isValid\(' \
--glob '*.java' \
.
```

Inspect custom validation logic.

Questions:

```text
Does validation fail closed?

Can null values bypass it?

Is normalisation performed before or after validation?

Are alternate encodings considered?

Does validation match business requirements?
```

---

# Authentication

Spring Security is commonly used for authentication.

Search:

```bash
rg -n \
'SecurityFilterChain|HttpSecurity|AuthenticationManager|AuthenticationProvider|UserDetailsService|PasswordEncoder|UsernamePasswordAuthenticationFilter' \
--glob '*.java' \
.
```

---

# Spring Security Configuration

Modern configuration commonly includes:

```java
@Bean
SecurityFilterChain securityFilterChain(
        HttpSecurity http) throws Exception {

    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/public/**").permitAll()
            .anyRequest().authenticated()
        );

    return http.build();
}
```

Search:

```bash
rg -n \
'authorizeHttpRequests|requestMatchers|securityMatcher|permitAll|denyAll|authenticated\(' \
--glob '*.java' \
.
```

---

# permitAll

Search:

```bash
rg -n \
'permitAll\(' \
--glob '*.java' \
.
```

Review each occurrence.

Ask:

```text
Which route is public?

Why is it public?

Can it perform state changes?

Does it expose sensitive information?

Is a wildcard too broad?
```

`permitAll()` is not automatically a vulnerability.

---

# anyRequest

Search:

```bash
rg -n \
'anyRequest\(' \
--glob '*.java' \
.
```

A useful security design commonly ends with an intentional catch-all policy rather than accidentally leaving routes outside expected rules.

Determine the actual matcher order and framework configuration.

---

# Legacy Spring Security

Older applications may use:

```text
WebSecurityConfigurerAdapter
configure(HttpSecurity)
antMatchers()
mvcMatchers()
```

Search:

```bash
rg -n \
'WebSecurityConfigurerAdapter|antMatchers|mvcMatchers|authorizeRequests' \
--glob '*.java' \
.
```

Legacy security configuration deserves careful review.

---

# Method Security

Spring applications may enforce authorisation using:

```text
@PreAuthorize
@PostAuthorize
@PreFilter
@PostFilter
@Secured
@RolesAllowed
```

Search:

```bash
rg -n \
'@(PreAuthorize|PostAuthorize|PreFilter|PostFilter|Secured|RolesAllowed|PermitAll|DenyAll)' \
--glob '*.java' \
.
```

---

# Is Method Security Enabled?

This is critical.

Search:

```bash
rg -n \
'@EnableMethodSecurity|@EnableGlobalMethodSecurity' \
--glob '*.java' \
.
```

Do not simply see:

```java
@PreAuthorize(...)
```

and assume that it is effective.

Determine whether the relevant method-security mechanism is enabled and configured.

---

# @PreAuthorize

Example:

```java
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(Long id) {
    ...
}
```

Review:

```text
Expression
Role naming
Claims/authorities
Object ownership
Parameter references
Custom security beans
```

---

# Object-Level Authorisation

Example:

```java
@GetMapping("/documents/{id}")
public Document getDocument(
        @PathVariable Long id) {

    return repository.findById(id)
        .orElseThrow();
}
```

Critical question:

```text
Where is permission checked?
```

A more tightly scoped lookup may be:

```java
repository.findByIdAndOwnerId(
    id,
    currentUserId
);
```

The exact secure implementation depends on the application's authorisation model.

---

# Search Object Lookups

Search:

```bash
rg -n \
'findById\(|getById\(|getReferenceById\(|findOne\(|findAllBy|findBy' \
--glob '*.java' \
.
```

Prioritise object IDs originating from:

```text
@PathVariable
@RequestParam
@RequestBody
```

---

# SecurityContext

Search:

```bash
rg -n \
'SecurityContextHolder|Authentication|getPrincipal\(|getAuthorities\(|getName\(' \
--glob '*.java' \
.
```

Example:

```java
Authentication auth =
    SecurityContextHolder
        .getContext()
        .getAuthentication();
```

Trace how identity influences:

```text
User ID
Roles
Tenant
Object access
Permissions
Business operations
```

---

# Tenant Isolation

Search:

```bash
rg -n -i \
'tenant|tenantid|tenant_id|organization|organisation|companyid|accountid' \
--glob '*.java' \
.
```

Look for:

```text
Object lookup
      |
      v
Tenant condition?
```

Example:

```java
repository.findById(id)
```

versus:

```java
repository.findByIdAndTenantId(
    id,
    currentTenant
);
```

---

# Mass Assignment

Example:

```java
@PostMapping("/users/{id}")
public User update(
        @PathVariable Long id,
        @RequestBody User user) {

    return repository.save(user);
}
```

If the persistence model contains:

```java
private boolean admin;
private String role;
private Long tenantId;
private boolean verified;
```

clients may potentially bind security-sensitive properties.

Prefer dedicated request DTOs.

Example:

```java
public class UpdateProfileRequest {

    private String displayName;
    private String biography;
}
```

Then explicitly map permitted fields.

Refer to:

```text
docs/web/mass-assignment.md
```

---

# SQL Injection

Java applications commonly access SQL databases through:

```text
JDBC
JdbcTemplate
JdbcClient
JPA
Hibernate
Spring Data JPA
MyBatis
jOOQ
```

The key question is:

```text
Can attacker-controlled data alter SQL syntax?
```

---

# JDBC

High-value APIs include:

```text
Statement
PreparedStatement
Connection.createStatement()
execute()
executeQuery()
executeUpdate()
```

Search:

```bash
rg -n \
'createStatement\(|prepareStatement\(|executeQuery\(|executeUpdate\(|\.execute\(' \
--glob '*.java' \
.
```

---

# Unsafe JDBC Example

Review candidate:

```java
String username =
    request.getParameter("username");

String sql =
    "SELECT * FROM users WHERE username = '" +
    username +
    "'";

Statement stmt =
    connection.createStatement();

ResultSet rs =
    stmt.executeQuery(sql);
```

Data flow:

```text
request parameter
      |
      v
username
      |
      v
SQL concatenation
      |
      v
Statement.executeQuery()
```

---

# PreparedStatement

Safer pattern:

```java
PreparedStatement stmt =
    connection.prepareStatement(
        "SELECT * FROM users WHERE username = ?"
    );

stmt.setString(1, username);

ResultSet rs =
    stmt.executeQuery();
```

Parameter binding separates values from SQL syntax when used correctly.

---

# PreparedStatement Is Not Automatically Safe

This can still be unsafe:

```java
String sql =
    "SELECT * FROM users ORDER BY " +
    sortColumn;

PreparedStatement stmt =
    connection.prepareStatement(sql);
```

Structural SQL elements such as:

```text
Table names
Column names
ORDER BY expressions
Sort direction
```

often cannot be parameterised as ordinary values.

Use explicit server-side mappings or allowlists.

---

# JdbcTemplate

Search:

```bash
rg -n \
'JdbcTemplate|NamedParameterJdbcTemplate|JdbcClient' \
--glob '*.java' \
.
```

Review whether values are supplied as parameters rather than concatenated into SQL.

Example:

```java
jdbcTemplate.query(
    "SELECT * FROM users WHERE username = ?",
    rowMapper,
    username
);
```

is different from:

```java
jdbcTemplate.query(
    "SELECT * FROM users WHERE username = '" +
    username +
    "'",
    rowMapper
);
```

---

# JPA

Search:

```bash
rg -n \
'EntityManager|createQuery\(|createNativeQuery\(|@Query\(' \
--glob '*.java' \
.
```

---

# JPQL / HQL Injection

Potentially unsafe:

```java
String query =
    "FROM User u WHERE u.name = '" +
    name +
    "'";

entityManager
    .createQuery(query)
    .getResultList();
```

Safer:

```java
entityManager
    .createQuery(
        "FROM User u WHERE u.name = :name"
    )
    .setParameter("name", name)
    .getResultList();
```

---

# Native Queries

Search:

```bash
rg -n \
'createNativeQuery|nativeQuery\s*=\s*true' \
--glob '*.java' \
.
```

Native SQL deserves particular attention because developers may manually construct query strings.

---

# Spring Data @Query

Example:

```java
@Query(
    "SELECT u FROM User u WHERE u.email = :email"
)
User findByEmail(
    @Param("email") String email
);
```

Binding parameters is preferable to constructing query strings dynamically.

---

# Dynamic Query Construction

Search:

```bash
rg -n \
'StringBuilder.*SELECT|StringBuilder.*WHERE|String\.format.*SELECT|String\.format.*WHERE' \
--glob '*.java' \
.
```

Also search:

```bash
rg -n \
'"SELECT|"INSERT|"UPDATE|"DELETE|"FROM|"WHERE|"ORDER BY' \
--glob '*.java' \
.
```

Expect false positives.

---

# SQL Injection Search

```bash
rg -n \
'createStatement|prepareStatement|executeQuery|executeUpdate|JdbcTemplate|JdbcClient|createQuery|createNativeQuery|@Query' \
--glob '*.java' \
.
```

Then manually trace input into query construction.

Refer to:

```text
docs/web/sql-injection.md
```

---

# NoSQL Injection

Java applications may use:

```text
MongoDB
Spring Data MongoDB
Elasticsearch
Redis
Cassandra
Neo4j
```

Search:

```bash
rg -n \
'MongoTemplate|MongoRepository|Criteria\.where|BasicQuery|Document\(|Elasticsearch|RedisTemplate|CassandraTemplate|Neo4j' \
--glob '*.java' \
.
```

---

# MongoDB

Example review candidate:

```java
BasicQuery query =
    new BasicQuery(userSuppliedJson);
```

Trace whether users can provide query operators or arbitrary query documents.

Review:

```text
Dynamic BSON
Dynamic JSON
Operators
Filters
Aggregation pipelines
```

Refer to:

```text
docs/web/nosql-injection.md
```

---

# LDAP Injection

Common Java LDAP APIs include:

```text
DirContext
InitialDirContext
SearchControls
LdapTemplate
LdapQuery
```

Search:

```bash
rg -n \
'DirContext|InitialDirContext|SearchControls|LdapTemplate|LdapQuery|\.search\(' \
--glob '*.java' \
.
```

---

# LDAP Filter Construction

Review candidate:

```java
String filter =
    "(&(objectClass=user)(uid=" +
    username +
    "))";
```

Data flow:

```text
username
   |
   v
LDAP filter concatenation
   |
   v
LDAP search
```

Review whether attacker-controlled values are properly encoded for their LDAP context.

Refer to:

```text
docs/web/ldap-injection.md
```

---

# OS Command Injection

High-value Java process APIs include:

```text
Runtime.getRuntime().exec()
ProcessBuilder
```

Search:

```bash
rg -n \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder' \
--glob '*.java' \
.
```

---

# Runtime.exec

Review candidate:

```java
String host =
    request.getParameter("host");

Runtime.getRuntime().exec(
    "ping " + host
);
```

Determine:

```text
What overload is used?

Is a shell invoked?

Can executable selection be controlled?

Can arguments be controlled?

Is input validated?

How does the invoked program interpret arguments?
```

Do not infer exploitability solely from the presence of `Runtime.exec()`.

---

# Explicit Shell Invocation

Higher-value search:

```bash
rg -n \
'cmd\.exe|/bin/sh|/bin/bash|powershell|pwsh|Runtime\.getRuntime|ProcessBuilder' \
--glob '*.java' \
.
```

Example:

```java
new ProcessBuilder(
    "/bin/sh",
    "-c",
    command
).start();
```

Attacker-controlled data reaching a shell command deserves particularly careful review.

---

# ProcessBuilder

Prefer structured arguments where process execution is genuinely required.

Example:

```java
new ProcessBuilder(
    "tool",
    userArgument
).start();
```

This avoids building one shell command string, although the called application's own argument semantics must still be reviewed.

---

# Command Injection Data Flow

```text
@RequestParam
     |
     v
host
     |
     v
Service
     |
     v
Command construction
     |
     v
Runtime.exec / ProcessBuilder
```

Refer to:

```text
docs/web/command-injection.md
```

---

# Server-Side Request Forgery

Common Java HTTP clients include:

```text
java.net.URL
URLConnection
HttpURLConnection
java.net.http.HttpClient
Apache HttpClient
OkHttp
RestTemplate
WebClient
RestClient
```

Search:

```bash
rg -n \
'new URL\(|URLConnection|HttpURLConnection|HttpClient|RestTemplate|WebClient|RestClient|OkHttpClient|Request\.Builder' \
--glob '*.java' \
.
```

---

# URL.openConnection

Review candidate:

```java
String url =
    request.getParameter("url");

URL target =
    new URL(url);

URLConnection connection =
    target.openConnection();
```

Data flow:

```text
HTTP Parameter
      |
      v
URL
      |
      v
openConnection()
      |
      v
Network Request
```

---

# Java HttpClient

Search:

```bash
rg -n \
'HttpRequest\.newBuilder|HttpClient\.newHttpClient|HttpClient\.newBuilder|\.send\(|\.sendAsync\(' \
--glob '*.java' \
.
```

Example:

```java
HttpRequest request =
    HttpRequest.newBuilder()
        .uri(URI.create(userUrl))
        .build();
```

Trace:

```text
userUrl
```

---

# RestTemplate

Search:

```bash
rg -n \
'RestTemplate|getForObject|getForEntity|postForObject|postForEntity|exchange\(' \
--glob '*.java' \
.
```

Review attacker influence over:

```text
Base URL
Host
Scheme
Port
Path
Redirect destination
```

---

# WebClient

Search:

```bash
rg -n \
'WebClient|\.uri\(' \
--glob '*.java' \
.
```

Example:

```java
webClient
    .get()
    .uri(userUrl)
    .retrieve();
```

Trace whether `userUrl` can select arbitrary destinations.

---

# SSRF Controls

Review:

```text
Allowed schemes
Allowed hostnames
Allowed ports
DNS resolution
Redirect handling
Proxy behaviour
Network egress
Cloud metadata access
Internal network access
```

A syntactically valid URL is not necessarily an authorised URL.

Refer to:

```text
docs/web/ssrf.md
```

---

# Open Redirect

Common Spring redirect mechanisms include:

```text
redirect:
RedirectView
sendRedirect()
```

Search:

```bash
rg -n \
'redirect:|RedirectView|sendRedirect\(' \
--glob '*.java' \
.
```

---

# Redirect Example

Review candidate:

```java
@GetMapping("/continue")
public String next(
        @RequestParam String url) {

    return "redirect:" + url;
}
```

Trace whether users can select external destinations.

---

# HttpServletResponse.sendRedirect

Example:

```java
response.sendRedirect(returnUrl);
```

Search:

```bash
rg -n \
'sendRedirect\(' \
--glob '*.java' \
.
```

Refer to:

```text
docs/web/open-redirect.md
```

---

# Path Traversal

High-value Java file APIs include:

```text
File
Paths.get()
Path
Files.readAllBytes()
Files.readString()
Files.write()
Files.copy()
FileInputStream
FileOutputStream
RandomAccessFile
```

Search:

```bash
rg -n \
'new File\(|Paths\.get\(|Path\.of\(|Files\.(read|write|copy|move|delete|newInputStream|newOutputStream)|FileInputStream|FileOutputStream|RandomAccessFile' \
--glob '*.java' \
.
```

---

# Path Traversal Example

Review candidate:

```java
String filename =
    request.getParameter("file");

Path path =
    Paths.get(
        "/var/app/files/",
        filename
    );

return Files.readAllBytes(path);
```

Trace:

```text
filename
   |
   v
Path construction
   |
   v
File read
```

---

# Normalisation

Java provides:

```java
path.normalize()
```

and:

```java
path.toRealPath()
```

but simply calling a normalisation function does not automatically enforce directory containment.

A secure design generally needs to ensure the resolved path remains within the intended base directory.

Conceptually:

```text
User Path
    |
    v
Resolve Against Base
    |
    v
Normalise / Canonicalise
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

# File Inclusion

Java does not normally expose PHP-style dynamic `include()` semantics.

However, review attacker-controlled values used for:

```text
Template names
Resource names
Class loaders
File reads
JSP forwarding
Request dispatching
```

Search:

```bash
rg -n \
'getResource|getResourceAsStream|getRequestDispatcher|forward\(|include\(' \
--glob '*.java' \
.
```

Refer to:

```text
docs/web/file-inclusion.md
```

---

# File Upload

Spring commonly represents uploads using:

```text
MultipartFile
```

Search:

```bash
rg -n \
'MultipartFile|getOriginalFilename|transferTo|getInputStream|getBytes\(' \
--glob '*.java' \
.
```

---

# Upload Example

Review candidate:

```java
@PostMapping("/upload")
public void upload(
        @RequestParam MultipartFile file)
        throws IOException {

    Path destination =
        Paths.get(
            uploadDirectory,
            file.getOriginalFilename()
        );

    file.transferTo(destination);
}
```

Review:

```text
Original filename
Path handling
Generated filename
Extension
MIME type
File signature
Content
File size
Storage location
Public accessibility
Execution possibility
Downstream processing
```

---

# Original Filename

Search:

```bash
rg -n \
'getOriginalFilename\(' \
--glob '*.java' \
.
```

Treat original filenames as attacker-controlled metadata.

---

# ZIP and Archive Extraction

Search:

```bash
rg -n \
'ZipInputStream|ZipEntry|ZipFile|JarInputStream|TarArchiveInputStream' \
--glob '*.java' \
.
```

Review extraction logic for archive-entry path traversal.

Conceptually:

```text
Archive Entry Name
        |
        v
Destination Path
        |
        v
Containment Check?
        |
        v
Write File
```

---

# XML External Entity Injection

Java has many XML processing APIs.

High-value classes include:

```text
DocumentBuilderFactory
SAXParserFactory
XMLInputFactory
TransformerFactory
SchemaFactory
SAXBuilder
SAXParser
XPathFactory
```

Search:

```bash
rg -n \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory|SchemaFactory|SAXBuilder|SAXParser|XPathFactory' \
--glob '*.java' \
.
```

---

# DocumentBuilderFactory

Example:

```java
DocumentBuilderFactory factory =
    DocumentBuilderFactory.newInstance();
```

Do not automatically report this as XXE.

Review:

```text
Parser configuration
DTD processing
External entities
External DTD loading
External schema access
Java/runtime version
Input source
```

---

# XMLInputFactory

Search:

```bash
rg -n \
'XMLInputFactory|SUPPORT_DTD|IS_SUPPORTING_EXTERNAL_ENTITIES' \
--glob '*.java' \
.
```

Review whether untrusted XML can trigger external resource resolution.

---

# XML Features

Search:

```bash
rg -n \
'setFeature\(|setProperty\(|ACCESS_EXTERNAL_DTD|ACCESS_EXTERNAL_SCHEMA|disallow-doctype-decl|external-general-entities|external-parameter-entities' \
--glob '*.java' \
.
```

Interpret settings in context.

Refer to:

```text
docs/web/xxe.md
```

---

# Insecure Deserialization

Java native serialization deserves particular attention.

High-value APIs:

```text
ObjectInputStream
readObject()
readUnshared()
XMLDecoder
XStream
Kryo
SnakeYAML
Jackson polymorphic typing
```

Search:

```bash
rg -n \
'ObjectInputStream|readObject\(|readUnshared\(|XMLDecoder|XStream|Kryo|Yaml|SnakeYAML|ObjectMapper|enableDefaultTyping|activateDefaultTyping' \
--glob '*.java' \
.
```

---

# ObjectInputStream

Review candidate:

```java
ObjectInputStream input =
    new ObjectInputStream(
        request.getInputStream()
    );

Object object =
    input.readObject();
```

Data flow:

```text
HTTP Request Body
       |
       v
ObjectInputStream
       |
       v
readObject()
```

Native Java serialization should not be used for untrusted serialized objects.

---

# ObjectInputFilter

Modern Java provides deserialization filtering mechanisms.

Search:

```bash
rg -n \
'ObjectInputFilter|setObjectInputFilter|jdk\.serialFilter' \
.
```

Review whether filters exist and whether their policy actually restricts the types and object graphs that can be created.

---

# XMLDecoder

Search:

```bash
rg -n \
'XMLDecoder' \
--glob '*.java' \
.
```

Untrusted input reaching flexible object-construction mechanisms deserves careful review.

---

# Jackson

Jackson is extremely common.

Search:

```bash
rg -n \
'ObjectMapper|readValue\(|readTree\(|convertValue\(|enableDefaultTyping|activateDefaultTyping|JsonTypeInfo' \
--glob '*.java' \
.
```

Normal Jackson JSON parsing is not automatically insecure deserialization.

Review:

```text
Polymorphic typing
Allowed subtypes
Custom deserializers
Target classes
Input source
Version
```

---

# Jackson Polymorphism

Search:

```bash
rg -n \
'enableDefaultTyping|activateDefaultTyping|JsonTypeInfo|JsonSubTypes|PolymorphicTypeValidator' \
--glob '*.java' \
.
```

Permissive polymorphic type handling with attacker-controlled JSON deserves particular attention.

---

# SnakeYAML

Search:

```bash
rg -n \
'Yaml\(|new Yaml|Constructor\(|SafeConstructor' \
--glob '*.java' \
.
```

Review:

```text
Library version
Constructor configuration
Allowed types
Input source
```

Do not assume all YAML parsing is exploitable.

---

# XStream

Search:

```bash
rg -n \
'XStream|fromXML\(' \
--glob '*.java' \
.
```

Review type permissions and input source.

---

# Deserialization Review Model

```text
Attacker Input
      |
      v
Deserializer
      |
      v
Type Selection
      |
      v
Object Construction
      |
      v
Side Effects?
```

Refer to:

```text
docs/web/deserialization.md
```

---

# Server-Side Template Injection

Common Java template engines include:

```text
Thymeleaf
FreeMarker
Velocity
Pebble
Jinjava
Mustache
Handlebars
Groovy templates
```

Search:

```bash
rg -n -i \
'thymeleaf|freemarker|velocity|pebble|jinjava|mustache|handlebars|templateengine|process\(' \
--glob '*.java' \
--glob '*.xml' \
--glob '*.properties' \
.
```

---

# SSTI Review Model

The important distinction is:

```text
User input passed as template data
```

versus:

```text
User input becomes template source
```

Example:

```text
User Input
    |
    v
Template Compilation
    |
    v
Template Evaluation
```

The latter deserves close review.

---

# FreeMarker

Search:

```bash
rg -n \
'freemarker|Template\(' \
--glob '*.java' \
.
```

Review dynamically constructed templates.

---

# Thymeleaf

Search:

```bash
rg -n \
'TemplateEngine|SpringTemplateEngine|\.process\(' \
--glob '*.java' \
.
```

Also review dynamic view names and expression construction.

---

# Spring Expression Language - SpEL

SpEL is a particularly important Java/Spring review target.

High-value APIs include:

```text
SpelExpressionParser
ExpressionParser
parseExpression()
getValue()
StandardEvaluationContext
SimpleEvaluationContext
```

Search:

```bash
rg -n \
'SpelExpressionParser|ExpressionParser|parseExpression\(|StandardEvaluationContext|SimpleEvaluationContext|getValue\(' \
--glob '*.java' \
.
```

---

# SpEL Review Candidate

```java
ExpressionParser parser =
    new SpelExpressionParser();

Expression expression =
    parser.parseExpression(userInput);

Object result =
    expression.getValue();
```

Trace whether attacker-controlled data can become an expression.

Do not confuse:

```text
User input as expression data
```

with:

```text
User input defining the expression itself
```

---

# SpEL in Security Annotations

Spring Security uses expressions such as:

```java
@PreAuthorize("hasRole('ADMIN')")
```

These are normally developer-defined static expressions.

Do not classify them as injection simply because SpEL is involved.

The interesting case is attacker influence over dynamically parsed expressions.

---

# XSS

Java web applications can produce XSS through:

```text
JSP
Thymeleaf
FreeMarker
Raw servlet output
Custom template rendering
JSON embedded into HTML
```

Output context matters.

---

# JSP

Search:

```bash
find . -type f \( \
-name '*.jsp' \
-o -name '*.jspx' \
\) -print
```

Search JSP expression output:

```bash
rg -n \
'<%=|\$\{' \
--glob '*.jsp' \
--glob '*.jspx' \
.
```

---

# JSP Scriptlets

Example review candidate:

```jsp
<%= request.getParameter("name") %>
```

Trace whether the value is output with appropriate context-specific encoding.

---

# JSTL

Search:

```bash
rg -n \
'<c:out|escapeXml' \
--glob '*.jsp' \
--glob '*.jspx' \
.
```

Example:

```jsp
<c:out value="${user.name}" />
```

Understand the escaping behaviour of the specific rendering mechanism.

---

# Thymeleaf XSS

Thymeleaf distinguishes escaped and unescaped output.

High-value search:

```bash
rg -n \
'th:utext|th:text' \
--glob '*.html' \
.
```

Particularly review:

```text
th:utext
```

when its value can contain attacker-controlled HTML.

Do not classify ordinary escaped output as XSS solely because user data is rendered.

---

# Raw Servlet Output

Search:

```bash
rg -n \
'getWriter\(\)|PrintWriter|\.write\(|\.print\(' \
--glob '*.java' \
.
```

Example:

```java
response
    .getWriter()
    .write(userInput);
```

Determine the response content type and output context.

Refer to:

```text
docs/web/xss.md
docs/web/html-injection.md
```

---

# DOM-Based Vulnerabilities

Java applications often serve JavaScript front ends.

Review browser-side JavaScript separately.

Refer to:

```text
docs/source-code-review/javascript.md
docs/web/dom-based-vulnerabilities.md
```

---

# CSRF

Spring Security provides CSRF protection mechanisms.

Search:

```bash
rg -n \
'csrf\(|CsrfToken|CsrfTokenRepository|CookieCsrfTokenRepository|csrfTokenRepository|ignoringRequestMatchers' \
--glob '*.java' \
.
```

---

# CSRF Disabled

High-value search:

```bash
rg -n \
'csrf.*disable|AbstractHttpConfigurer::disable' \
--glob '*.java' \
.
```

Review why CSRF is disabled.

This may be appropriate for certain stateless APIs.

It may be dangerous for browser applications relying on automatically submitted credentials such as session cookies.

Do not report:

```text
CSRF disabled
```

without determining the authentication model and attack feasibility.

---

# CSRF Ignored Routes

Search:

```bash
rg -n \
'ignoringRequestMatchers|ignoringAntMatchers' \
--glob '*.java' \
.
```

Review excluded endpoints.

---

# CORS

Spring CORS configuration commonly uses:

```text
@CrossOrigin
CorsConfiguration
CorsConfigurationSource
addCorsMappings()
allowedOrigins()
allowedOriginPatterns()
```

Search:

```bash
rg -n \
'@CrossOrigin|CorsConfiguration|CorsConfigurationSource|addCorsMappings|allowedOrigins|allowedOriginPatterns|allowCredentials' \
--glob '*.java' \
.
```

---

# @CrossOrigin

Search:

```bash
rg -n \
'@CrossOrigin' \
--glob '*.java' \
.
```

Review:

```text
Allowed origins
Credentials
Methods
Headers
Endpoint sensitivity
```

Do not automatically report wildcard CORS without demonstrating a meaningful cross-origin security impact.

Refer to:

```text
docs/web/cors.md
```

---

# Host Header Attacks

Servlet/Spring applications may access:

```text
request.getServerName()
request.getServerPort()
request.getHeader("Host")
ServletUriComponentsBuilder
UriComponentsBuilder
```

Search:

```bash
rg -n \
'getServerName\(|getServerPort\(|getHeader\("Host"\)|ServletUriComponentsBuilder|UriComponentsBuilder' \
--glob '*.java' \
.
```

Review host-derived data used in:

```text
Password reset links
Email verification links
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
rg -n -i \
'x-forwarded-host|x-forwarded-for|forwardedheader|forwarded' \
--glob '*.java' \
--glob '*.properties' \
--glob '*.yml' \
--glob '*.yaml' \
.
```

Reverse-proxy trust configuration can affect:

```text
Host
Scheme
Client IP
Rate limiting
URL generation
```

---

# HTTP Security Headers

Spring Security can configure headers through the security chain.

Search:

```bash
rg -n \
'headers\(|contentSecurityPolicy|frameOptions|httpStrictTransportSecurity|referrerPolicy|permissionsPolicy' \
--glob '*.java' \
.
```

Also inspect:

```text
Reverse proxies
Ingress configuration
Web server configuration
API gateways
```

because headers may be applied outside Java.

Refer to:

```text
docs/web/http-security-headers.md
```

---

# Session Management

Search:

```bash
rg -n \
'SessionCreationPolicy|sessionManagement|HttpSession|getSession\(|invalidate\(|changeSessionId\(' \
--glob '*.java' \
.
```

Review:

```text
Session creation
Session fixation protection
Expiration
Invalidation
Concurrent sessions
Cookie configuration
```

---

# Session Fixation

Search:

```bash
rg -n \
'sessionFixation|migrateSession|newSession|changeSessionId' \
--glob '*.java' \
.
```

Understand Spring Security defaults before concluding that explicit configuration is missing.

---

# Session Cookies

Inspect:

```text
application.properties
application.yml
```

Search:

```bash
rg -n -i \
'server\.servlet\.session\.cookie|same-site|httponly|secure|session\.timeout' \
--glob '*.properties' \
--glob '*.yml' \
--glob '*.yaml' \
.
```

---

# JWT

Common Java JWT libraries include:

```text
jjwt
java-jwt
Nimbus JOSE + JWT
Spring Security JWT
```

Search:

```bash
rg -n -i \
'jwt|jsonwebtoken|jjwt|nimbus|JwtDecoder|JwtEncoder|NimbusJwtDecoder|NimbusJwtEncoder' \
--glob '*.java' \
--glob 'pom.xml' \
--glob 'build.gradle*' \
.
```

---

# JWT Validation

Review:

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
'JwtDecoder|JwtEncoder|verify\(|withIssuer|withAudience|setSigningKey|signWith|parseClaims|decode\(' \
--glob '*.java' \
.
```

---

# JWT Claims

Search:

```bash
rg -n \
'getClaim|getClaims|getSubject|getAuthorities|GrantedAuthority|JwtAuthenticationToken' \
--glob '*.java' \
.
```

Determine whether claims influence:

```text
Roles
Tenant
User ID
Permissions
Administrative access
```

Refer to:

```text
docs/web/jwt.md
```

---

# OAuth 2.0 / OpenID Connect

Search:

```bash
rg -n -i \
'oauth2|openid|oidc|clientregistration|oauth2login|oauth2client|issuer-uri|client-id|client-secret' \
.
```

Review:

```text
Issuer
Client ID
Client secret
Redirect URI
State
Nonce
PKCE
Token validation
Account linking
Claims
```

Refer to:

```text
docs/web/oauth-oidc.md
```

---

# SAML

Spring applications may use:

```text
Spring Security SAML
OpenSAML
```

Search:

```bash
rg -n -i \
'saml|opensaml|saml2login|relyingpartyregistration' \
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
'forgotpassword|forgot-password|resetpassword|reset-password|passwordreset|password-reset|resettoken' \
--glob '*.java' \
.
```

Review:

```text
Token generation
Token entropy
Token lifetime
Single use
Account binding
User enumeration
Reset URL construction
Rate limiting
Password-change invalidation
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
'twofactor|two-factor|2fa|mfa|totp|otp|authenticator|recoverycode' \
--glob '*.java' \
.
```

Review:

```text
Enrollment
Verification
Recovery
Reset
Remember-device
Bypass paths
Rate limiting
```

Refer to:

```text
docs/web/mfa.md
```

---

# Password Hashing

Spring Security commonly uses:

```text
PasswordEncoder
BCryptPasswordEncoder
Argon2PasswordEncoder
Pbkdf2PasswordEncoder
SCryptPasswordEncoder
DelegatingPasswordEncoder
```

Search:

```bash
rg -n \
'PasswordEncoder|BCryptPasswordEncoder|Argon2PasswordEncoder|Pbkdf2PasswordEncoder|SCryptPasswordEncoder|DelegatingPasswordEncoder' \
--glob '*.java' \
.
```

---

# Weak Hashing

Search:

```bash
rg -n \
'MessageDigest|getInstance\("MD5"|getInstance\("SHA-1"|DigestUtils\.md5|DigestUtils\.sha1' \
--glob '*.java' \
.
```

Do not report MD5/SHA-1 merely because they exist.

Determine whether they are used for:

```text
Passwords
Integrity
Cache keys
Non-security checksums
Legacy protocol requirements
```

Context matters.

---

# Cryptography

Search:

```bash
rg -n \
'Cipher\.getInstance|KeyGenerator|SecretKeySpec|IvParameterSpec|SecureRandom|MessageDigest|Mac\.getInstance|KeyPairGenerator' \
--glob '*.java' \
.
```

Review:

```text
Algorithm
Mode
Padding
Key source
Key size
Nonce / IV
Random generation
Authentication/integrity
Hard-coded keys
Key reuse
```

---

# ECB Mode

Search:

```bash
rg -n \
'AES/ECB|DES/ECB|Cipher\.getInstance' \
--glob '*.java' \
.
```

Do not report based solely on the presence of a cipher string.

Determine:

```text
What data is encrypted?

What security property is required?

Is confidentiality needed?

Is integrity provided?
```

---

# Randomness

Security-sensitive Java randomness should generally use:

```text
SecureRandom
```

Search:

```bash
rg -n \
'new Random\(|Math\.random\(|SecureRandom|UUID\.randomUUID' \
--glob '*.java' \
.
```

Review ordinary `Random` or `Math.random()` when used for:

```text
Password reset tokens
MFA codes
API keys
Session identifiers
Invitation tokens
Security nonces
```

---

# Hard-Coded Secrets

Search:

```bash
rg -n -i \
'password|passwd|secret|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|token|jdbc:' \
.
```

Inspect:

```text
application.properties
application.yml
application.yaml
bootstrap.yml
pom.xml
build.gradle
Dockerfile
docker-compose.yml
CI/CD configuration
Java source
Tests
```

---

# Spring Configuration

Common files:

```text
application.properties
application.yml
application.yaml
application-dev.yml
application-prod.yml
bootstrap.yml
```

Find:

```bash
find . -type f \( \
-name 'application*.properties' \
-o -name 'application*.yml' \
-o -name 'application*.yaml' \
-o -name 'bootstrap*.yml' \
-o -name 'bootstrap*.yaml' \
\) -print
```

---

# Environment Properties

Search:

```bash
rg -n \
'@Value\(|Environment|getProperty\(|@ConfigurationProperties' \
--glob '*.java' \
.
```

Trace where sensitive configuration originates.

---

# Secrets Through @Value

Example:

```java
@Value("${api.secret}")
private String apiSecret;
```

This does not mean the secret is hard-coded.

Find:

```text
api.secret
```

across:

```text
Properties
YAML
Environment
Deployment configuration
Secret manager integration
```

---

# Spring Boot Actuator

Search:

```bash
rg -n -i \
'actuator|management\.endpoints|management\.endpoint|management\.server' \
.
```

Review exposure of endpoints such as:

```text
health
info
metrics
env
configprops
beans
mappings
loggers
heapdump
threaddump
```

Exposure depends on configuration and security.

Do not report the presence of the Actuator dependency alone.

---

# Management Endpoint Exposure

Search:

```bash
rg -n \
'management\.endpoints\.web\.exposure\.include|management\.endpoints\.web\.exposure\.exclude' \
.
```

Particularly review broad exposure such as:

```text
*
```

but verify actual network reachability and authentication before classifying impact.

---

# Debug and Error Handling

Search:

```bash
rg -n -i \
'debug=true|server\.error|include-stacktrace|include-message|printStackTrace|stacktrace' \
.
```

Review:

```text
Stack traces
Internal paths
SQL details
Credentials
Environment data
Sensitive exception messages
```

---

# printStackTrace

Search:

```bash
rg -n \
'printStackTrace\(' \
--glob '*.java' \
.
```

This is not automatically a vulnerability.

Determine where the output goes and whether sensitive data becomes externally accessible.

---

# Logging

Common Java logging APIs include:

```text
SLF4J
Logback
Log4j
java.util.logging
```

Search:

```bash
rg -n \
'logger\.(trace|debug|info|warn|error)|log\.(trace|debug|info|warn|error)|System\.out\.print|System\.err\.print' \
--glob '*.java' \
.
```

Review whether logs contain:

```text
Passwords
JWTs
Authorization headers
Session IDs
API keys
Secrets
Personal information
Full request bodies
```

---

# Logging Attacker Input

Example:

```java
logger.info(
    "Login attempt: {}",
    username
);
```

Structured logging is generally preferable to constructing log lines manually.

Still consider downstream log consumers and sensitive-data exposure.

---

# Information Disclosure

Search:

```bash
rg -n -i \
'stacktrace|debug|actuator|swagger|openapi|api-docs|h2-console|graphiql|playground' \
.
```

Potentially interesting development interfaces include:

```text
Swagger UI
OpenAPI
H2 Console
GraphiQL
Actuator
Debug endpoints
```

Presence does not automatically mean exposure.

Verify configuration and reachability.

Refer to:

```text
docs/web/information-disclosure.md
```

---

# H2 Console

Search:

```bash
rg -n \
'spring\.h2\.console|h2-console' \
.
```

Determine whether:

```text
Enabled
Externally reachable
Authenticated
Production deployed
```

---

# Swagger / OpenAPI

Search:

```bash
rg -n -i \
'swagger|springdoc|openapi|api-docs' \
.
```

API documentation can significantly improve attack-surface mapping.

---

# Business Logic

Search business-sensitive terms:

```bash
rg -n -i \
'price|amount|balance|quantity|discount|coupon|credit|refund|approved|verified|status|state|role|permission|tenant' \
--glob '*.java' \
.
```

Review:

```text
Financial calculations
Approval workflows
State transitions
Role changes
Ownership transfers
Tenant transitions
Discount logic
Inventory
Refunds
```

Business logic vulnerabilities may have no obvious sink.

Refer to:

```text
docs/web/business-logic.md
```

---

# Race Conditions

Look for:

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

where operations may occur concurrently.

Search:

```bash
rg -n \
'@Transactional|synchronized|ReentrantLock|Semaphore|Atomic|LockModeType|@Version|PESSIMISTIC_WRITE|OPTIMISTIC' \
--glob '*.java' \
.
```

---

# JPA Optimistic Locking

Search:

```bash
rg -n \
'@Version' \
--glob '*.java' \
.
```

Version fields can help detect concurrent modifications.

Their absence does not automatically mean a race vulnerability exists.

---

# Database Transactions

Search:

```bash
rg -n \
'@Transactional|TransactionTemplate|PlatformTransactionManager' \
--glob '*.java' \
.
```

Review transaction boundaries around security-sensitive workflows.

Refer to:

```text
docs/web/race-conditions.md
```

---

# Rate Limiting

Java applications may implement rate limiting through:

```text
Bucket4j
Resilience4j
Redis
API gateways
Reverse proxies
Custom filters
```

Search:

```bash
rg -n -i \
'bucket4j|ratelimit|rate-limit|rate_limit|resilience4j|throttle|throttling' \
.
```

Review protection around:

```text
Login
Password reset
MFA
Registration
OTP
Search
Expensive exports
Reports
API endpoints
```

Refer to:

```text
docs/web/rate-limiting.md
```

---

# Client IP

Search:

```bash
rg -n \
'getRemoteAddr\(|X-Forwarded-For|ForwardedHeaderFilter' \
--glob '*.java' \
.
```

If security controls depend on client IP, review proxy trust carefully.

---

# GraphQL

Common Java GraphQL frameworks include:

```text
Spring for GraphQL
graphql-java
DGS
```

Search:

```bash
rg -n -i \
'graphql|@QueryMapping|@MutationMapping|@SchemaMapping|DataFetcher|DgsQuery|DgsMutation' \
--glob '*.java' \
.
```

---

# GraphQL Review

Map:

```text
Schema
   |
   v
Query / Mutation
   |
   v
Resolver
   |
   v
Authentication
   |
   v
Authorisation
   |
   v
Repository
```

Review:

```text
Object-level authorisation
Mutation permissions
Input validation
Introspection
Query depth
Complexity
Batching
Data loaders
```

Refer to:

```text
docs/web/graphql.md
```

---

# gRPC

Locate:

```bash
find . -type f -name '*.proto' -print
```

Search Java implementations:

```bash
rg -n \
'ImplBase|StreamObserver|ServerInterceptor|BindableService' \
--glob '*.java' \
.
```

Map:

```text
.proto RPC
    |
    v
Service Implementation
    |
    v
Authentication Interceptor
    |
    v
Authorisation
    |
    v
Request Fields
    |
    v
Sensitive Operation
```

Refer to:

```text
docs/web/grpc-security.md
```

---

# WebSockets

Spring supports:

```text
WebSocket
STOMP
SockJS
```

Search:

```bash
rg -n \
'WebSocketConfigurer|WebSocketHandler|EnableWebSocket|EnableWebSocketMessageBroker|MessageMapping|SubscribeMapping|StompEndpointRegistry' \
--glob '*.java' \
.
```

Review:

```text
Connection authentication
Message authentication
Destination authorisation
Object access
Subscription permissions
State-changing messages
```

Refer to:

```text
docs/web/websockets.md
```

---

# WebSocket Message Security

Search:

```bash
rg -n \
'@MessageMapping|@SubscribeMapping|MessageMatcherDelegatingAuthorizationManager|simpDestMatchers' \
--glob '*.java' \
.
```

Do not assume HTTP endpoint security automatically protects every messaging operation.

---

# Cache Security

Common Java caching technologies include:

```text
Spring Cache
Caffeine
Redis
Ehcache
Hazelcast
```

Search:

```bash
rg -n \
'@Cacheable|@CachePut|@CacheEvict|CacheManager|RedisCacheManager|Caffeine|Hazelcast' \
--glob '*.java' \
.
```

Review cache keys for:

```text
User identity
Tenant
Object ID
Authentication state
Request parameters
```

Incorrect cache isolation can cause sensitive-data disclosure.

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# HTTP Request Smuggling

Java application code alone may not reveal the complete parsing chain.

Relevant components may include:

```text
Tomcat
Jetty
Undertow
Netty
Spring Boot
Reverse proxy
Load balancer
API gateway
CDN
```

Review deployment architecture and HTTP parser differences.

Refer to:

```text
docs/web/http-request-smuggling.md
```

---

# Dependency Security

Inspect:

```text
pom.xml
build.gradle
build.gradle.kts
gradle.lockfile
```

Maven dependency tree:

```bash
mvn dependency:tree
```

Gradle:

```bash
./gradlew dependencies
```

These may produce very large outputs in complex projects.

---

# Maven Dependency Search

```bash
rg -n \
'<dependency>|<groupId>|<artifactId>|<version>' \
--glob 'pom.xml' \
.
```

Review:

```text
Unsupported versions
Known vulnerabilities
Unmaintained libraries
Unexpected repositories
Direct dependencies
Transitive dependencies
```

Refer to:

```text
docs/web/dependency-security.md
```

---

# Maven Repositories

Search:

```bash
rg -n \
'<repositories>|<repository>|<url>' \
--glob 'pom.xml' \
.
```

Review unexpected package sources and internal repository configuration.

---

# Gradle Repositories

Search:

```bash
rg -n \
'repositories\s*\{|maven\s*\{|mavenCentral|mavenLocal|url\s*=' \
--glob 'build.gradle' \
--glob 'build.gradle.kts' \
.
```

---

# Third-Party JavaScript

Spring applications may serve JavaScript through:

```text
src/main/resources/static/
src/main/resources/public/
src/main/webapp/
templates/
```

Find package manifests:

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

# Reflection

High-value Java reflection APIs include:

```text
Class.forName()
ClassLoader
Method.invoke()
Constructor.newInstance()
getDeclaredMethod()
getMethod()
```

Search:

```bash
rg -n \
'Class\.forName|ClassLoader|getDeclaredMethod|getMethod\(|\.invoke\(|newInstance\(' \
--glob '*.java' \
.
```

Reflection itself is not a vulnerability.

Review attacker control over:

```text
Class names
Method names
Arguments
JAR locations
Plugin names
```

---

# Dynamic Class Loading

Search:

```bash
rg -n \
'URLClassLoader|ClassLoader|Class\.forName|ServiceLoader' \
--glob '*.java' \
.
```

Review whether attacker-controlled paths, URLs or class names influence code loading.

---

# Script Engines

Java can execute scripting languages through:

```text
ScriptEngine
ScriptEngineManager
eval()
```

Search:

```bash
rg -n \
'ScriptEngine|ScriptEngineManager|\.eval\(' \
--glob '*.java' \
.
```

Example review candidate:

```java
ScriptEngine engine =
    new ScriptEngineManager()
        .getEngineByName("javascript");

engine.eval(userInput);
```

Attacker-controlled script source reaching an execution engine is a high-value candidate.

---

# Expression Languages

Also search for:

```text
SpEL
OGNL
MVEL
JEXL
ELProcessor
ExpressionFactory
```

```bash
rg -n -i \
'spel|ognl|mvel|jexl|ELProcessor|ExpressionFactory|parseExpression' \
--glob '*.java' \
.
```

These expression languages have different capabilities and security models.

---

# ELProcessor

Search:

```bash
rg -n \
'ELProcessor|ExpressionFactory' \
--glob '*.java' \
.
```

Trace attacker-controlled expressions.

---

# Request Dispatching

Search:

```bash
rg -n \
'RequestDispatcher|getRequestDispatcher|forward\(|include\(' \
--glob '*.java' \
.
```

If user input controls dispatch destinations, review:

```text
Internal endpoint access
Path manipulation
Unexpected resource exposure
```

---

# Response Headers

Search:

```bash
rg -n \
'setHeader\(|addHeader\(|setStatus\(|setContentType\(' \
--glob '*.java' \
.
```

Trace attacker-controlled header values.

Potential concerns include:

```text
Redirects
Content-Disposition
CORS
Caching
Header injection
Content type
```

---

# Content-Disposition

Search:

```bash
rg -n -i \
'content-disposition|filename=' \
--glob '*.java' \
.
```

Review attacker-controlled filenames and framework/header encoding behaviour.

---

# HTTP Method Handling

Search:

```bash
rg -n \
'RequestMethod\.|@GetMapping|@PostMapping|@PutMapping|@PatchMapping|@DeleteMapping' \
--glob '*.java' \
.
```

Compare security controls across:

```text
GET
POST
PUT
PATCH
DELETE
```

A common review technique is to identify endpoints where one method is protected but another reaches similar functionality without equivalent controls.

---

# API Versioning

Search:

```bash
rg -n \
'/v1/|/v2/|/api/v1|/api/v2' \
--glob '*.java' \
.
```

Compare old and new versions.

Legacy API versions may contain weaker controls.

---

# Administrative Functionality

Search:

```bash
rg -n -i \
'admin|administrator|superuser|manage|management|privileged' \
--glob '*.java' \
.
```

Trace:

```text
Route
   |
   v
Authentication
   |
   v
Role / Permission Check
   |
   v
Administrative Operation
```

---

# Role Management

Search:

```bash
rg -n -i \
'role|authority|permission|grantedauthority|setrole|addrole|removerole' \
--glob '*.java' \
.
```

Review who can:

```text
Assign roles
Remove roles
Create administrators
Modify permissions
Change tenant ownership
```

---

# Registration

Search:

```bash
rg -n -i \
'register|registration|signup|sign-up|createuser|create-user' \
--glob '*.java' \
.
```

Review:

```text
Role assignment
Tenant assignment
Email verification
Mass assignment
Default privileges
Invitation logic
Duplicate accounts
```

---

# Webhooks

Search:

```bash
rg -n -i \
'webhook|callback|signature|hmac' \
--glob '*.java' \
.
```

Review:

```text
Signature verification
Secret management
Timestamp verification
Replay protection
Payload validation
Authorisation
```

---

# Background Jobs

Java applications may process untrusted data outside HTTP request threads.

Search:

```bash
rg -n \
'@Scheduled|TaskScheduler|ScheduledExecutorService|Quartz|JobExecutionContext' \
--glob '*.java' \
.
```

Background jobs may process:

```text
Database records
Uploaded files
Messages
External data
Stored user input
```

This creates second-order attack paths.

---

# Message Queues

Search:

```bash
rg -n -i \
'kafka|rabbitmq|jms|activemq|sqs|@KafkaListener|@RabbitListener|@JmsListener' \
--glob '*.java' \
.
```

Treat externally influenced messages as untrusted input.

---

# Second-Order Vulnerabilities

Example:

```text
POST /profile
      |
      v
Store displayName
      |
      v
Database
      |
      v
Scheduled Report
      |
      v
Template Rendering
      |
      v
Unsafe Output
```

The vulnerability may occur long after the original input was stored.

---

# Source-to-Sink Example - SQL Injection

```text
GET /search?q=test
       |
       v
@RequestParam q
       |
       v
SearchController
       |
       v
SearchService
       |
       v
SearchRepository
       |
       v
SQL concatenation
       |
       v
Statement.executeQuery()
```

Review:

```text
Is q attacker-controlled?

Is it transformed?

Is it parameterised?

Can it alter SQL syntax?

Is the route reachable?

What authentication is required?
```

---

# Source-to-Sink Example - SSRF

```text
POST /api/import
       |
       v
@RequestBody ImportRequest
       |
       v
request.getUrl()
       |
       v
ImportService
       |
       v
WebClient.uri()
       |
       v
Remote request
```

Review:

```text
Scheme
Host
Port
DNS
Redirects
Network egress
```

---

# Source-to-Sink Example - Command Injection

```text
POST /api/convert
       |
       v
@RequestParam filename
       |
       v
ConversionService
       |
       v
Command construction
       |
       v
ProcessBuilder
       |
       v
Shell / process
```

---

# Source-to-Sink Example - IDOR

```text
GET /api/orders/{id}
       |
       v
@PathVariable id
       |
       v
OrderController
       |
       v
orderRepository.findById(id)
       |
       v
Order returned
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
@RequestBody biography
       |
       v
Database
       |
       v
Profile Controller
       |
       v
Template
       |
       v
Unescaped HTML output
```

---

# Source-to-Sink Example - Path Traversal

```text
GET /download?file=x
       |
       v
@RequestParam file
       |
       v
Paths.get(base, file)
       |
       v
Files.readAllBytes()
```

Review canonicalisation and containment.

---

# Source-to-Sink Example - Deserialization

```text
HTTP Body
    |
    v
ObjectInputStream
    |
    v
readObject()
    |
    v
Object Graph
```

Review whether the body is attacker-controlled and what filtering exists.

---

# ripgrep Quick Review

A broad first-pass Java command:

```bash
rg -n \
'@(RequestParam|PathVariable|RequestBody|RequestHeader|CookieValue|RequestPart)|getParameter\(|getHeader\(|createStatement\(|prepareStatement\(|executeQuery\(|createQuery\(|createNativeQuery\(|Runtime\.getRuntime\(\)\.exec|ProcessBuilder|new URL\(|HttpClient|RestTemplate|WebClient|new File\(|Paths\.get\(|Files\.|MultipartFile|ObjectInputStream|readObject\(|XMLDecoder|ObjectMapper|TypeInfo|SpelExpressionParser|HtmlUtils|sendRedirect\(' \
--glob '*.java' \
.
```

This produces review candidates, not confirmed vulnerabilities.

---

# Route Search

```bash
rg -n \
'@(RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|Path|GET|POST|PUT|DELETE)' \
--glob '*.java' \
.
```

---

# Input Source Search

```bash
rg -n \
'@(RequestParam|PathVariable|RequestBody|RequestHeader|CookieValue|RequestPart|ModelAttribute)|getParameter\(|getHeader\(|getCookies\(' \
--glob '*.java' \
.
```

---

# Authentication Search

```bash
rg -n \
'SecurityFilterChain|HttpSecurity|AuthenticationManager|AuthenticationProvider|UserDetailsService|PasswordEncoder|SecurityContextHolder' \
--glob '*.java' \
.
```

---

# Authorisation Search

```bash
rg -n \
'@(PreAuthorize|PostAuthorize|Secured|RolesAllowed|PermitAll|DenyAll)|authorizeHttpRequests|requestMatchers|permitAll|denyAll|hasRole|hasAuthority' \
--glob '*.java' \
.
```

---

# Method Security Search

```bash
rg -n \
'EnableMethodSecurity|EnableGlobalMethodSecurity|PreAuthorize|PostAuthorize|Secured|RolesAllowed' \
--glob '*.java' \
.
```

---

# SQL Search

```bash
rg -n \
'createStatement|prepareStatement|executeQuery|executeUpdate|JdbcTemplate|JdbcClient|createQuery|createNativeQuery|@Query' \
--glob '*.java' \
.
```

---

# Command Execution Search

```bash
rg -n \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder|cmd\.exe|/bin/sh|/bin/bash|powershell|pwsh' \
--glob '*.java' \
.
```

---

# SSRF Search

```bash
rg -n \
'new URL\(|URI\.create|URLConnection|HttpURLConnection|HttpClient|RestTemplate|WebClient|RestClient|OkHttpClient' \
--glob '*.java' \
.
```

---

# File Search

```bash
rg -n \
'new File\(|Paths\.get\(|Path\.of\(|Files\.|FileInputStream|FileOutputStream|RandomAccessFile|MultipartFile|getOriginalFilename|transferTo' \
--glob '*.java' \
.
```

---

# XML Search

```bash
rg -n \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory|SchemaFactory|SAXBuilder|XPathFactory|setFeature\(|ACCESS_EXTERNAL' \
--glob '*.java' \
.
```

---

# Deserialization Search

```bash
rg -n \
'ObjectInputStream|readObject\(|XMLDecoder|XStream|Kryo|SnakeYAML|new Yaml|ObjectMapper|enableDefaultTyping|activateDefaultTyping|JsonTypeInfo' \
--glob '*.java' \
.
```

---

# SSTI / Expression Search

```bash
rg -n -i \
'TemplateEngine|freemarker|velocity|thymeleaf|pebble|jinjava|SpelExpressionParser|parseExpression|ScriptEngine|ELProcessor|OGNL|MVEL|JEXL' \
--glob '*.java' \
.
```

---

# Redirect Search

```bash
rg -n \
'redirect:|RedirectView|sendRedirect\(' \
--glob '*.java' \
.
```

---

# Secrets Search

```bash
rg -n -i \
'password|passwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|jdbc:' \
.
```

---

# Spring Security Configuration Search

```bash
rg -n \
'SecurityFilterChain|authorizeHttpRequests|requestMatchers|permitAll|denyAll|csrf|cors|sessionManagement|oauth2Login|saml2Login|oauth2ResourceServer' \
--glob '*.java' \
.
```

---

# Spring Configuration Search

```bash
rg -n -i \
'server\.|spring\.|management\.|security\.|datasource\.|jpa\.|session\.' \
--glob '*.properties' \
--glob '*.yml' \
--glob '*.yaml' \
.
```

---

# Suspicious Comments

```bash
rg -n -i \
'todo|fixme|hack|temporary|bypass|disable|disabled|security|auth|workaround' \
--glob '*.java' \
.
```

Comments may identify unfinished or deliberately bypassed controls.

They are leads, not evidence.

---

# Exclude Build and Dependency Noise

For large repositories:

```bash
rg \
-g '!target/**' \
-g '!build/**' \
-g '!node_modules/**' \
-g '!vendor/**' \
-g '!generated/**' \
'pattern' \
.
```

---

# Semgrep

Semgrep can complement manual Java review.

Typical workflow:

```text
Java Repository
      |
      v
Semgrep
      |
      v
Potential Findings
      |
      v
Manual Data-Flow Analysis
```

Check current Semgrep Java support and rules before relying on a particular ruleset.

Official documentation:

```text
https://semgrep.dev/docs/
```

---

# CodeQL

CodeQL supports semantic analysis of Java and Kotlin applications.

It can model:

```text
Sources
Data flow
Taint propagation
Sinks
Call graphs
Annotations
Framework behaviour
```

Conceptually:

```text
HTTP Input
     |
     v
Spring Controller
     |
     v
Service
     |
     v
Repository
     |
     v
Dangerous Sink
```

Official Java/Kotlin documentation:

```text
https://codeql.github.com/docs/codeql-language-guides/codeql-for-java/
```

---

# CodeQL Data Flow

CodeQL can assist with tracing:

```text
@RequestParam
      |
      v
Variable
      |
      v
Method
      |
      v
Service
      |
      v
SQL / File / Network Sink
```

Manual review remains essential for:

```text
Business logic
Authorisation
Tenant isolation
Framework configuration
Reachability
Exploitability
Impact
```

---

# IDE-Assisted Review

Useful IDE functionality includes:

```text
Go to Definition
Find Usages
Find Implementations
Call Hierarchy
Type Hierarchy
Search Everywhere
Data-flow features
```

IntelliJ IDEA is particularly useful for navigating large Java applications.

---

# Trace Interfaces

Spring applications frequently use interfaces.

Example:

```java
private final UserService userService;
```

Find implementation:

```bash
rg -n \
'interface UserService|implements UserService' \
--glob '*.java' \
.
```

Then trace:

```text
Controller
   |
   v
UserService interface
   |
   v
UserServiceImpl
   |
   v
Repository
```

---

# Dependency Injection

Search:

```bash
rg -n \
'@Autowired|@Inject|@Bean|@Component|@Service|@Repository' \
--glob '*.java' \
.
```

Constructor injection may make dependencies easier to trace:

```java
public UserController(
        UserService userService) {

    this.userService = userService;
}
```

---

# Reverse Sink Analysis

For large Java applications, start at dangerous sinks.

Example:

```text
Runtime.exec()
      ^
      |
CommandService
      ^
      |
AdminService
      ^
      |
AdminController
      ^
      |
POST /admin/run
```

High-value starting points:

```text
Runtime.exec
ProcessBuilder

Statement.execute
JdbcTemplate
createNativeQuery

HttpClient
RestTemplate
WebClient

Files.read
Files.write
new File

ObjectInputStream
readObject

SpelExpressionParser
ScriptEngine.eval

sendRedirect
```

---

# Forward Source Analysis

Start from:

```text
@RequestParam
@PathVariable
@RequestBody
@RequestHeader
@CookieValue
MultipartFile
HttpServletRequest
```

Then follow each value forward.

This is especially useful for:

```text
Admin endpoints
Uploads
Imports
Exports
Reports
Password reset
Account management
Payments
Webhooks
Search
```

---

# Variant Analysis

Once one weakness is found:

```text
Finding
   |
   v
Understand Root Cause
   |
   v
Extract Pattern
   |
   v
Search Entire Repository
```

Example:

```text
repository.findById(id)
without ownership check
```

Then search:

```bash
rg -n \
'findById\(' \
--glob '*.java' \
.
```

Review all externally reachable uses.

---

# Compare Similar Controllers

Example:

```text
OrderController
    |
    +--> ownership check

InvoiceController
    |
    +--> ownership check

DocumentController
    |
    +--> no ownership check
```

Security inconsistencies are often valuable leads.

---

# Compare Similar Methods

Look for:

```text
GET /resource/{id}
PUT /resource/{id}
DELETE /resource/{id}
```

It is possible for:

```text
GET
```

to enforce object authorisation while:

```text
PUT
```

or:

```text
DELETE
```

does not.

---

# Compare API Versions

```text
/api/v1/users/{id}
/api/v2/users/{id}
```

Search:

```bash
rg -n \
'/v1/|/v2/|/api/v1|/api/v2' \
--glob '*.java' \
.
```

Legacy versions frequently deserve additional scrutiny.

---

# Security Review Matrix

| Vulnerability | High-Value Java Review Targets |
|---|---|
| SQL Injection | JDBC `Statement`, dynamic JPQL/HQL, native queries, `JdbcTemplate` |
| NoSQL Injection | Dynamic MongoDB/BSON/query construction |
| LDAP Injection | LDAP filter construction, `LdapTemplate`, `DirContext` |
| Command Injection | `Runtime.exec`, `ProcessBuilder`, shell invocation |
| SSTI | Dynamic template construction, SpEL, expression engines |
| XSS | JSP output, unescaped Thymeleaf, servlet response output |
| SSRF | `URL`, `HttpClient`, `RestTemplate`, `WebClient` |
| Path Traversal | `File`, `Path`, `Paths`, `Files` |
| File Upload | `MultipartFile`, original filenames, archive extraction |
| XXE | XML parser factories and external-resource configuration |
| Deserialization | `ObjectInputStream`, Jackson polymorphism, XStream, YAML |
| IDOR/BOLA | Repository lookup by attacker-controlled ID without authz |
| Mass Assignment | Persistence/domain objects bound directly from requests |
| Open Redirect | `sendRedirect`, `RedirectView`, `redirect:` |
| CSRF | Spring Security CSRF configuration |
| CORS | `@CrossOrigin`, `CorsConfiguration` |
| JWT | JWT decoder/verifier configuration and claims |
| OAuth/OIDC | Spring OAuth client/resource-server configuration |
| SAML | Spring Security SAML/OpenSAML |
| Race Conditions | Transactions, state checks, optimistic/pessimistic locking |
| Rate Limiting | Filters, Bucket4j, gateway/proxy controls |
| Secrets | Properties, YAML, Java source, CI/CD, Git history |
| Dependency Security | Maven and Gradle dependencies |
| Information Disclosure | Actuator, debug/error configuration, Swagger, H2 |
| Business Logic | Services, domain logic, state transitions |

---

# Source Code Review Checklist

## Application Structure

```text
[ ] Maven/Gradle files identified
[ ] Java version identified
[ ] Spring version identified
[ ] Application entry point identified
[ ] Modules identified
[ ] Controllers identified
[ ] Services identified
[ ] Repositories identified
[ ] Security configuration identified
[ ] Configuration files identified
```

## Routes

```text
[ ] @RequestMapping mapped
[ ] @GetMapping mapped
[ ] @PostMapping mapped
[ ] @PutMapping mapped
[ ] @PatchMapping mapped
[ ] @DeleteMapping mapped
[ ] JAX-RS routes mapped where present
[ ] Servlets mapped where present
[ ] Admin endpoints identified
[ ] API versions identified
```

## Authentication

```text
[ ] SecurityFilterChain reviewed
[ ] Authentication providers reviewed
[ ] UserDetailsService reviewed
[ ] Password hashing reviewed
[ ] Session authentication reviewed
[ ] JWT reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
```

## Authorisation

```text
[ ] Request-level rules reviewed
[ ] Method security configuration reviewed
[ ] @PreAuthorize reviewed
[ ] @PostAuthorize reviewed
[ ] @Secured reviewed
[ ] @RolesAllowed reviewed
[ ] Object-level checks reviewed
[ ] Tenant isolation reviewed
[ ] Administrative functions reviewed
```

## Input

```text
[ ] @RequestParam reviewed
[ ] @PathVariable reviewed
[ ] @RequestBody reviewed
[ ] @RequestHeader reviewed
[ ] @CookieValue reviewed
[ ] MultipartFile reviewed
[ ] HttpServletRequest reviewed
[ ] Bean Validation reviewed
[ ] Custom validators reviewed
```

## Injection

```text
[ ] JDBC reviewed
[ ] JdbcTemplate/JdbcClient reviewed
[ ] JPA/Hibernate reviewed
[ ] Native SQL reviewed
[ ] NoSQL queries reviewed
[ ] LDAP filters reviewed
[ ] Runtime.exec reviewed
[ ] ProcessBuilder reviewed
[ ] Template evaluation reviewed
[ ] SpEL reviewed
[ ] Script engines reviewed
```

## Server-Side

```text
[ ] HTTP clients reviewed
[ ] URL construction reviewed
[ ] File reads reviewed
[ ] File writes reviewed
[ ] Path construction reviewed
[ ] Uploads reviewed
[ ] Archive extraction reviewed
[ ] XML parsers reviewed
[ ] Deserialization reviewed
```

## Client-Side / HTTP

```text
[ ] JSP output reviewed
[ ] Thymeleaf output reviewed
[ ] Raw servlet output reviewed
[ ] Redirects reviewed
[ ] CSRF reviewed
[ ] CORS reviewed
[ ] Host handling reviewed
[ ] Forwarded headers reviewed
[ ] Security headers reviewed
[ ] Cache behaviour reviewed
```

## Business Logic

```text
[ ] Financial operations reviewed
[ ] State transitions reviewed
[ ] Approval workflows reviewed
[ ] Role transitions reviewed
[ ] Tenant transitions reviewed
[ ] Race conditions considered
[ ] Rate limiting reviewed
```

## Configuration

```text
[ ] application.properties reviewed
[ ] application.yml reviewed
[ ] Environment-specific configuration reviewed
[ ] Actuator reviewed
[ ] Debug configuration reviewed
[ ] Error handling reviewed
[ ] Logging reviewed
[ ] Secrets searched
[ ] Database credentials reviewed
```

## Dependencies

```text
[ ] pom.xml reviewed
[ ] Gradle files reviewed
[ ] Dependency tree reviewed
[ ] Vulnerable dependencies considered
[ ] Unsupported dependencies considered
[ ] Repository sources reviewed
[ ] Third-party JavaScript reviewed
```

## Analysis

```text
[ ] ripgrep searches performed
[ ] IDE references reviewed
[ ] Call hierarchy reviewed
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
'@(RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping)' \
--glob '*.java' \
.
```

## Sources

```bash
rg -n \
'@(RequestParam|PathVariable|RequestBody|RequestHeader|CookieValue|RequestPart|ModelAttribute)|getParameter\(|getHeader\(' \
--glob '*.java' \
.
```

## Authentication / Authorisation

```bash
rg -n \
'SecurityFilterChain|authorizeHttpRequests|requestMatchers|permitAll|denyAll|EnableMethodSecurity|PreAuthorize|PostAuthorize|Secured|RolesAllowed|SecurityContextHolder' \
--glob '*.java' \
.
```

## SQL

```bash
rg -n \
'createStatement|prepareStatement|executeQuery|executeUpdate|JdbcTemplate|JdbcClient|createQuery|createNativeQuery|@Query' \
--glob '*.java' \
.
```

## Commands

```bash
rg -n \
'Runtime\.getRuntime\(\)\.exec|ProcessBuilder|cmd\.exe|/bin/sh|/bin/bash|powershell|pwsh' \
--glob '*.java' \
.
```

## Network

```bash
rg -n \
'new URL\(|URI\.create|URLConnection|HttpClient|RestTemplate|WebClient|RestClient|OkHttpClient' \
--glob '*.java' \
.
```

## Files

```bash
rg -n \
'new File\(|Paths\.get\(|Path\.of\(|Files\.|FileInputStream|FileOutputStream|MultipartFile|getOriginalFilename|transferTo' \
--glob '*.java' \
.
```

## XML

```bash
rg -n \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory|SchemaFactory|SAXBuilder|XPathFactory' \
--glob '*.java' \
.
```

## Deserialization

```bash
rg -n \
'ObjectInputStream|readObject\(|XMLDecoder|XStream|Kryo|SnakeYAML|new Yaml|ObjectMapper|enableDefaultTyping|activateDefaultTyping|JsonTypeInfo' \
--glob '*.java' \
.
```

## Templates / Expressions

```bash
rg -n -i \
'TemplateEngine|freemarker|velocity|thymeleaf|pebble|SpelExpressionParser|parseExpression|ScriptEngine|ELProcessor|OGNL|MVEL|JEXL' \
--glob '*.java' \
.
```

## Redirects

```bash
rg -n \
'redirect:|RedirectView|sendRedirect\(' \
--glob '*.java' \
.
```

## Secrets

```bash
rg -n -i \
'password|passwd|secret|token|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|jdbc:' \
.
```

## Configuration

```bash
rg -n -i \
'management\.|server\.|spring\.security|datasource|csrf|cors|actuator|debug|stacktrace' \
--glob '*.properties' \
--glob '*.yml' \
--glob '*.yaml' \
.
```

---

# Recommended Manual Review Order

For an unfamiliar Java/Spring application:

```text
pom.xml / build.gradle
        |
        v
Application.java
        |
        v
Security Configuration
        |
        v
Filters / Interceptors
        |
        v
Controllers
        |
        v
Request DTOs
        |
        v
Authentication
        |
        v
Authorisation
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
pom.xml
build.gradle
build.gradle.kts

Application.java

SecurityConfig.java
WebSecurityConfig.java

*Controller.java
*Resource.java

*Service.java
*ServiceImpl.java

*Repository.java
*Dao.java

*Filter.java
*Interceptor.java

application.properties
application.yml
application.yaml

templates/

web.xml

Dockerfile
docker-compose.yml

CI/CD configuration
```

---

# High-Value Search Terms

```text
RequestMapping
GetMapping
PostMapping

RequestParam
PathVariable
RequestBody

SecurityFilterChain
permitAll
PreAuthorize

Admin
Role
Permission
Tenant
Owner

createStatement
executeQuery
JdbcTemplate
createNativeQuery

Runtime.exec
ProcessBuilder

HttpClient
RestTemplate
WebClient

File
Path
Files

MultipartFile

ObjectInputStream
readObject

ObjectMapper
JsonTypeInfo

DocumentBuilderFactory
XMLInputFactory

SpelExpressionParser
ScriptEngine

redirect:
sendRedirect

JWT
OAuth
SAML

PasswordReset
MFA

Secret
Token
ApiKey
Password
```

---

# Finding Validation

A Java source-code candidate should move through:

```text
CODE MATCH
    |
    v
REACHABLE?
    |
    +-- No --> Usually discard / contextual note
    |
    v
ATTACKER-CONTROLLED?
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

For every Java source finding record:

```text
Route:

HTTP Method:

Controller / Resource:

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
```

---

# Example Finding - SQL Injection

```text
Title:
SQL Injection in User Search

Route:
GET /api/users/search

Source:
@RequestParam "name"

Data Flow:

@RequestParam name
       |
       v
UserController
       |
       v
UserService
       |
       v
UserRepository
       |
       v
SQL concatenation
       |
       v
Statement.executeQuery()

Security Control:
No parameter binding is applied to the attacker-controlled value.

Impact:
An attacker able to access the endpoint may be able to modify the structure of the database query.

Recommendation:
Use parameterised queries and avoid constructing SQL syntax through concatenation of untrusted values.
```

---

# Example Finding - IDOR / BOLA

```text
Title:
Missing Object-Level Authorisation on Document Endpoint

Route:
GET /api/documents/{id}

Source:
@PathVariable id

Data Flow:

{id}
 |
 v
DocumentController
 |
 v
documentRepository.findById(id)
 |
 v
Document returned

Authentication:
Required.

Authorisation:
No ownership, tenant or permission check was identified before the document was returned.

Impact:
An authenticated user may be able to access documents belonging to another user by modifying the object identifier.

Recommendation:
Enforce object-level authorisation for every document operation. Scope repository queries to objects the authenticated principal is permitted to access or enforce an equivalent policy before returning the object.
```

---

# Example Finding - SSRF

```text
Title:
Server-Side Request Forgery Through Import URL

Route:
POST /api/import

Source:
ImportRequest.url

Data Flow:

@RequestBody
     |
     v
ImportRequest.url
     |
     v
ImportService
     |
     v
WebClient.uri()
     |
     v
Server-side request

Security Control:
No destination restriction was identified.

Impact:
An authenticated user may be able to cause the application to send server-side requests to attacker-selected destinations.

Recommendation:
Where possible, map user choices to server-controlled destinations. Otherwise enforce a strict destination policy, validate resolved destinations, control redirects and apply network-level egress restrictions.
```

---

# Example Finding - Command Injection

```text
Title:
Command Injection Through Conversion Functionality

Route:
POST /api/convert

Source:
@RequestParam filename

Data Flow:

filename
   |
   v
ConversionController
   |
   v
ConversionService
   |
   v
Shell command construction
   |
   v
ProcessBuilder("/bin/sh", "-c", command)

Impact:
If attacker-controlled input can modify shell syntax, the application's process privileges may be exposed to unintended command execution.

Recommendation:
Avoid invoking a shell for operations involving untrusted input. Use fixed executables with structured arguments and validate values according to the application's expected input domain.
```

---

# Common Review Mistakes

## Every Runtime.exec Is Command Injection

Incorrect:

```text
Runtime.exec()
      =
Command Injection
```

Correct:

```text
Runtime.exec()
      |
      v
Trace Input
      |
      v
Attacker Controlled?
      |
      v
Shell?
      |
      v
Argument Semantics?
      |
      v
Controls?
      |
      v
Exploitability
```

---

# Every ObjectMapper Is Insecure Deserialization

Incorrect:

```text
ObjectMapper.readValue()
        =
Insecure Deserialization
```

Normal JSON parsing is common.

Review:

```text
Polymorphism
Type configuration
Custom deserializers
Target classes
Input source
Library version
```

---

# Every XML Parser Is XXE

Incorrect:

```text
DocumentBuilderFactory
        =
XXE
```

Review:

```text
Input controllability
Parser configuration
DTD support
External entity support
External resource access
Runtime defaults
```

---

# Every findById Is IDOR

Incorrect:

```text
findById(id)
    =
IDOR
```

The authorisation check may occur:

```text
Controller
Service
Method security
Repository scope
Policy
Post-authorisation
```

Trace the complete operation.

---

# Every permitAll Is Authentication Bypass

Public routes are expected.

Determine:

```text
What functionality is exposed?

Was public access intentional?

Does the route expose sensitive data?

Does it perform sensitive state changes?
```

---

# Every csrf.disable Is CSRF

A stateless bearer-token API may intentionally disable CSRF protection.

Determine:

```text
How does the browser authenticate?

Are credentials automatically attached?

Can another origin trigger the operation?

Does the endpoint change state?
```

---

# Every @PreAuthorize Is Effective

Verify:

```text
Method security enabled?

Correct bean/proxy path?

Correct expression?

Correct role/authority semantics?

Method actually invoked through the protected proxy?
```

---

# Every @Valid Means Input Is Safe

Validation may enforce:

```text
Length
Format
Range
```

but does not automatically provide:

```text
SQL injection prevention
Authorisation
Output encoding
SSRF prevention
Command injection prevention
Business-rule enforcement
```

Use the appropriate control for the sink.

---

# Final Java Source Review Model

```text
                  JAVA APPLICATION
                         |
                         v
                  ROUTE DISCOVERY
                         |
                         v
               SPRING / JAX-RS INPUT
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
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
      JDBC          ProcessBuilder      HTTP Client
       |                 |                 |
       v                 v                 v
     SQLi        Command Injection        SSRF

       File              XML            Template
        |                 |                 |
        v                 v                 v
   Traversal/Upload      XXE             SSTI/XSS

                  Deserializer
                       |
                       v
             Insecure Deserialization
```

The fundamental Java review question is:

```text
Can attacker-controlled data reach a security-sensitive Java operation
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

## Spring Framework Documentation

```text
https://docs.spring.io/spring-framework/reference/
```

## Spring MVC

```text
https://docs.spring.io/spring-framework/reference/web/webmvc.html
```

## Spring WebFlux

```text
https://docs.spring.io/spring-framework/reference/web/webflux.html
```

## Spring Security

```text
https://docs.spring.io/spring-security/reference/
```

## Spring Security Authorization

```text
https://docs.spring.io/spring-security/reference/servlet/authorization/index.html
```

## Spring Security Method Security

```text
https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html
```

## Spring Security CSRF

```text
https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html
```

## Spring JDBC

```text
https://docs.spring.io/spring-framework/reference/data-access/jdbc.html
```

## Spring Data JPA

```text
https://docs.spring.io/spring-data/jpa/reference/
```

## Java ProcessBuilder

```text
https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ProcessBuilder.html
```

## Java ObjectInputStream

```text
https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputStream.html
```

## Java Object Serialization Filtering

```text
https://docs.oracle.com/en/java/javase/25/core/serialization-filtering1.html
```

## Java Secure Coding Guidelines

```text
https://www.oracle.com/java/technologies/javase/seccodeguide.html
```

## OWASP Code Review Guide

```text
https://owasp.org/www-project-code-review-guide/
```

## OWASP Web Security Testing Guide

```text
https://owasp.org/www-project-web-security-testing-guide/
```

## OWASP Cheat Sheet Series

```text
https://cheatsheetseries.owasp.org/
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
https://semgrep.dev/
```

## CodeQL for Java and Kotlin

```text
https://codeql.github.com/docs/codeql-language-guides/codeql-for-java/
```

## CodeQL Java Data Flow

```text
https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-java/
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
docs/web/grpc-security.md
docs/web/websockets.md
docs/web/mass-assignment.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md
```
