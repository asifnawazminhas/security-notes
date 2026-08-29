# Node.js and Express Source Code Review

Node.js is widely used for REST APIs, web applications, GraphQL services, WebSocket applications, microservices, background workers and server-side rendering.

Express is one of the most common Node.js web frameworks, but the same review methodology applies to many JavaScript and TypeScript server applications.

Node.js applications are particularly interesting during source-code review because JavaScript applications commonly combine:

- Dynamic typing
- Object merging
- JSON processing
- Asynchronous execution
- Large dependency trees
- Middleware-based security controls
- Multiple data stores
- Server-side template engines
- Client-side and server-side JavaScript
- Background jobs
- WebSockets
- GraphQL
- External APIs

The objective of source-code review is not simply to search for dangerous functions.

The objective is to identify:

```text
Routes
Input sources
Authentication
Authorisation
Validation
Trust boundaries
Data transformations
Dangerous sinks
Security configuration
```

and determine whether attacker-controlled data can reach security-sensitive operations.

The core methodology is:

```text
SOURCE
  |
  v
User-Controlled Input
  |
  v
TRANSFORMATIONS
  |
  +-- parsing
  +-- decoding
  +-- validation
  +-- sanitisation
  +-- object merging
  +-- business logic
  |
  v
SECURITY CONTROLS
  |
  +-- authentication
  +-- authorisation
  +-- tenant isolation
  +-- CSRF
  +-- rate limiting
  |
  v
SINK
  |
  v
Security-Sensitive Operation
```

Remember:

```text
grep match
    !=
vulnerability
```

and:

```text
Dangerous sink found
        !=
Confirmed vulnerability
```

A finding normally requires:

```text
Attacker-controlled source
        +
Reachable code path
        +
Dangerous operation
        +
Missing or ineffective control
        +
Security impact
```

!!! warning "Authorised Security Testing"
    Perform source-code review and dynamic validation only against applications, repositories and environments for which you have explicit authorisation.

---

# Review Strategy

A practical Node.js review can follow:

```text
1. Identify Node.js version

2. Identify package manager

3. Identify dependencies

4. Identify application entry points

5. Identify framework

6. Map middleware

7. Map routers

8. Map routes

9. Identify input sources

10. Map authentication

11. Map authorisation

12. Review object-level access

13. Review validation

14. Review database access

15. Review command execution

16. Review filesystem access

17. Review outbound HTTP requests

18. Review template engines

19. Review redirects

20. Review sessions and cookies

21. Review JWT handling

22. Review CORS

23. Review CSRF

24. Review proxy trust

25. Review file uploads

26. Review object merging and prototype pollution

27. Review GraphQL

28. Review WebSockets

29. Review business logic

30. Review asynchronous workflows

31. Review background jobs

32. Search secrets

33. Review dependencies

34. Run static analysis

35. Perform variant analysis

36. Validate candidates dynamically where authorised
```

---

# Identify the Project

Start with:

```bash
find . -maxdepth 3 -type f \( \
-name 'package.json' \
-o -name 'package-lock.json' \
-o -name 'yarn.lock' \
-o -name 'pnpm-lock.yaml' \
-o -name 'bun.lock' \
-o -name 'bun.lockb' \
-o -name 'tsconfig.json' \
-o -name '.npmrc' \
-o -name '.yarnrc*' \
\) -print
```

High-value files include:

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
tsconfig.json

app.js
server.js
index.js
main.js

app.ts
server.ts
index.ts
main.ts

routes/
controllers/
middleware/
services/
models/
repositories/
graphql/
websocket/
workers/
jobs/
config/
```

---

# package.json

Inspect:

```bash
cat package.json
```

Important sections:

```json
{
  "scripts": {},
  "dependencies": {},
  "devDependencies": {},
  "engines": {}
}
```

Look for:

```text
express
fastify
koa
hapi
nestjs
mongoose
mongodb
sequelize
typeorm
prisma
knex
pg
mysql
mysql2
sqlite
jsonwebtoken
jose
passport
express-session
cookie-session
helmet
cors
csurf
express-rate-limit
multer
axios
got
node-fetch
undici
ejs
pug
handlebars
mustache
socket.io
ws
graphql
apollo
```

Dependencies reveal much of the attack surface.

---

# Node.js Version

Check:

```bash
node --version
```

Project requirements may appear in:

```json
{
  "engines": {
    "node": ">=..."
  }
}
```

Search:

```bash
rg -n \
'"node"\s*:|node-version|NODE_VERSION' \
package.json .nvmrc .node-version Dockerfile* .github 2>/dev/null
```

Also inspect:

```text
Docker images
CI workflows
Deployment manifests
Runtime configuration
```

Do not assume the developer's local Node.js version equals the production version.

---

# JavaScript vs TypeScript

Find:

```bash
find . -type f \( \
-name '*.js' \
-o -name '*.mjs' \
-o -name '*.cjs' \
-o -name '*.ts' \
-o -name '*.tsx' \
\) | head -100
```

TypeScript configuration:

```bash
cat tsconfig.json
```

TypeScript improves type safety but does not automatically prevent security vulnerabilities.

---

# Common Application Structure

A typical Express project may resemble:

```text
src/
├── app.ts
├── server.ts
├── routes/
│   ├── auth.ts
│   ├── users.ts
│   └── admin.ts
├── controllers/
│   ├── authController.ts
│   └── userController.ts
├── middleware/
│   ├── auth.ts
│   └── permissions.ts
├── services/
│   ├── userService.ts
│   └── webhookService.ts
├── models/
│   └── User.ts
├── repositories/
├── jobs/
├── config/
└── views/
```

Trace:

```text
Route
  |
  v
Middleware
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
Database / External System
```

---

# Identify Express

Search:

```bash
rg -n \
'require\(["'\'']express["'\'']\)|from ["'\'']express["'\'']|express\(\)' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Typical:

```javascript
const express = require("express");
const app = express();
```

or:

```typescript
import express from "express";

const app = express();
```

---

# Application Entry Points

Inspect package scripts:

```bash
rg -n \
'"(start|dev|serve)"\s*:' \
package.json
```

Example:

```json
{
  "scripts": {
    "start": "node dist/server.js",
    "dev": "tsx src/server.ts"
  }
}
```

Trace the actual startup file.

---

# Middleware Order

Express security often depends heavily on middleware ordering.

Example:

```javascript
app.use(express.json());

app.use(authenticate);

app.use("/api", apiRouter);

app.use(errorHandler);
```

Middleware order matters.

A route registered before authentication middleware may not receive the expected protection.

Search:

```bash
rg -n \
'app\.use\(|router\.use\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Map middleware sequentially.

---

# Route Discovery

Common Express routes:

```javascript
app.get()
app.post()
app.put()
app.patch()
app.delete()

router.get()
router.post()
router.put()
router.patch()
router.delete()
```

Search:

```bash
rg -n \
'\b(app|router)\.(get|post|put|patch|delete|options|head|all)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Route Example

```javascript
router.get(
    "/users/:id",
    authenticate,
    getUser
);
```

Map:

```text
GET /users/:id
      |
      v
authenticate
      |
      v
getUser
```

---

# Router Mounting

Routes may be split across files.

Example:

```javascript
app.use(
    "/api/users",
    userRouter
);
```

and:

```javascript
router.get(
    "/:id",
    getUser
);
```

Final route:

```text
GET /api/users/:id
```

Search:

```bash
rg -n \
'app\.use\(|router\.use\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Always combine:

```text
Mount path
    +
Router path
    =
Final endpoint
```

---

# Express Router

Search:

```bash
rg -n \
'express\.Router\(\)|Router\(\)' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Typical:

```javascript
const router = express.Router();
```

---

# Dynamic Routes

Route parameters:

```javascript
router.get(
    "/users/:userId",
    handler
);
```

Attacker-controlled source:

```javascript
req.params.userId
```

---

# Route Inventory

Build:

| Method | Route | Handler | Authentication | Authorisation |
|---|---|---|---|---|
| GET | `/users/:id` | `getUser` | JWT | ? |
| POST | `/users` | `createUser` | JWT | Admin? |
| PATCH | `/users/:id` | `updateUser` | JWT | Owner? |
| DELETE | `/users/:id` | `deleteUser` | JWT | Admin? |

This makes inconsistent security controls easier to identify.

---

# User-Controlled Input Sources

The primary Express sources are:

```javascript
req.query
req.params
req.body
req.headers
req.cookies
req.signedCookies
req.file
req.files
```

Other sources include:

```javascript
req.get()
req.header()
req.hostname
req.ip
req.ips
req.protocol
req.originalUrl
req.url
```

---

# Input Search

```bash
rg -n \
'req\.(query|params|body|headers|cookies|signedCookies|file|files|hostname|ip|ips|protocol|originalUrl|url)|req\.(get|header)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Query Parameters

Example:

```javascript
const search = req.query.q;
```

Search:

```bash
rg -n \
'req\.query' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Route Parameters

```javascript
const id = req.params.id;
```

Search:

```bash
rg -n \
'req\.params' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Request Body

```javascript
const data = req.body;
```

Search:

```bash
rg -n \
'req\.body' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Treat nested fields individually.

---

# Headers

```javascript
const token =
    req.headers.authorization;
```

Search:

```bash
rg -n \
'req\.headers|req\.get\(|req\.header\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Potentially attacker-controlled headers include:

```text
Host
Origin
Referer
User-Agent
Authorization
X-Forwarded-For
X-Forwarded-Host
X-Forwarded-Proto
Custom headers
```

---

# Cookies

Search:

```bash
rg -n \
'req\.cookies|req\.signedCookies' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Signed cookies provide integrity when implemented correctly.

They are not automatically secret.

---

# Body Parsers

Search:

```bash
rg -n \
'express\.json\(|express\.urlencoded\(|bodyParser\.' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Body size
Accepted content types
Nested object behaviour
Raw body requirements
Signature verification
```

---

# Raw Bodies

Webhooks may require raw request bodies.

Search:

```bash
rg -n \
'express\.raw\(|express\.text\(|req\.rawBody' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

This is particularly important for:

```text
Webhook signatures
Payment providers
Custom protocols
```

---

# Input Validation

Common validation libraries include:

```text
Joi
Zod
Ajv
express-validator
Yup
class-validator
Valibot
```

Search:

```bash
rg -n -i \
'joi|zod|ajv|express-validator|class-validator|yup|valibot|validate|schema' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Validation Example

```javascript
const schema = z.object({
    email: z.string().email(),
    name: z.string().max(100)
});

const input =
    schema.parse(req.body);
```

Validation establishes constraints.

It does not automatically provide:

```text
Authorisation
Safe SQL construction
Safe command construction
Safe HTML output
Object ownership
```

---

# Unknown Fields

Review whether schemas:

```text
Reject unknown fields
Strip unknown fields
Preserve unknown fields
```

This matters for mass assignment.

---

# Authentication

Search broadly:

```bash
rg -n -i \
'authenticate|authentication|authorize|authorization|passport|jwt|bearer|session|login|logout|api.?key|currentUser|req\.user' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Authentication Middleware

Typical:

```javascript
function authenticate(
    req,
    res,
    next
) {
    ...
}
```

Routes:

```javascript
router.get(
    "/profile",
    authenticate,
    profile
);
```

Search:

```bash
rg -n \
'authenticate|authMiddleware|requireAuth|isAuthenticated|req\.user' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Read middleware implementations.

Do not trust names alone.

---

# Middleware Coverage

Compare:

```javascript
router.get(
    "/account",
    authenticate,
    account
);
```

with:

```javascript
router.post(
    "/account/delete",
    deleteAccount
);
```

The second route deserves investigation.

---

# Router-Level Authentication

Authentication may be applied globally:

```javascript
router.use(authenticate);
```

Therefore:

```text
No route-level middleware
    !=
Unauthenticated
```

Trace parent routers and application middleware.

---

# Authorisation

Search:

```bash
rg -n -i \
'role|permission|authorize|authorise|admin|owner|tenant|organization|organisation|workspace|req\.user' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Role Middleware

Example:

```javascript
function requireAdmin(
    req,
    res,
    next
) {
    if (!req.user.isAdmin) {
        return res.sendStatus(403);
    }

    next();
}
```

Determine where `req.user` originates.

---

# IDOR / BOLA

Candidate:

```javascript
router.get(
    "/documents/:id",
    authenticate,
    async (req, res) => {
        const document =
            await Document.findById(
                req.params.id
            );

        res.json(document);
    }
);
```

Data flow:

```text
req.params.id
      |
      v
Document.findById()
      |
      v
Document
      |
      v
Response
```

Question:

```text
Where is ownership or tenant authorisation?
```

---

# Scoped Lookup

A stronger pattern may resemble:

```javascript
const document =
    await Document.findOne({
        _id: req.params.id,
        ownerId: req.user.id
    });
```

For multi-tenant applications:

```javascript
const document =
    await Document.findOne({
        _id: req.params.id,
        tenantId: req.user.tenantId
    });
```

The correct scope depends on application policy.

---

# Object Lookup Search

MongoDB/Mongoose:

```bash
rg -n \
'\.(findById|findOne|find|findOneAndUpdate|findByIdAndUpdate|findOneAndDelete|findByIdAndDelete)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

SQL ORMs:

```bash
rg -n \
'(findOne|findUnique|findFirst|findByPk|findAll|select|where)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Prioritise attacker-controlled identifiers.

Refer to:

```text
docs/web/idor-bola.md
docs/web/authorisation.md
```

---

# Multi-Tenant Security

Search:

```bash
rg -n -i \
'tenantId|tenant_id|organizationId|organisationId|workspaceId|accountId|ownerId' \
--glob '*.{js,mjs,cjs,ts}' \
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
Tenant Identifier
       |
       v
Database Query
       |
       v
Object
```

Look for queries that omit tenant scope.

---

# SQL Injection

Node.js applications may use:

```text
pg
mysql
mysql2
sqlite
Knex
Sequelize
TypeORM
Prisma
Raw SQL
```

Search:

```bash
rg -n \
'\.(query|execute|raw|queryRaw|executeRaw)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Raw SQL

Candidate:

```javascript
const username =
    req.query.username;

const sql =
    "SELECT * FROM users WHERE username = '" +
    username +
    "'";

db.query(sql);
```

Trace:

```text
req.query.username
        |
        v
SQL String
        |
        v
db.query()
```

---

# Template Literal SQL

Candidate:

```javascript
const sql =
    `SELECT * FROM users
     WHERE username = '${username}'`;
```

Search candidates:

```bash
rg -n \
'`[^`]*(SELECT|INSERT|UPDATE|DELETE)[^`]*\$\{' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# PostgreSQL Parameterisation

Safer style:

```javascript
await pool.query(
    "SELECT * FROM users WHERE id = $1",
    [userId]
);
```

Review dynamic structural elements separately:

```text
Column names
Table names
ORDER BY
Operators
Directions
```

These usually require server-controlled mappings or allowlists.

---

# MySQL Parameterisation

Example:

```javascript
connection.execute(
    "SELECT * FROM users WHERE id = ?",
    [userId]
);
```

Review the actual driver and API semantics.

---

# Sequelize

Search:

```bash
rg -n \
'sequelize\.query|Sequelize\.literal|literal\(|replacements|bind' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Raw query functionality deserves particular attention.

---

# Knex

Search:

```bash
rg -n \
'knex\.raw|\.whereRaw|\.orderByRaw|\.havingRaw|\.joinRaw' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Prisma

Search:

```bash
rg -n \
'\$queryRaw|\$executeRaw|\$queryRawUnsafe|\$executeRawUnsafe' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Raw and explicitly unsafe query APIs deserve investigation.

Do not report normal ORM queries as SQL injection merely because attacker-controlled values are used as query values.

Refer to:

[SQL Injection](../web/sql-injection.md)

---

# NoSQL Injection

NoSQL injection is especially relevant to Node.js applications using MongoDB.

Sources such as:

```javascript
req.body
req.query
```

may contain nested objects rather than only strings.

Candidate:

```javascript
const user =
    await User.findOne({
        username: req.body.username,
        password: req.body.password
    });
```

The security significance depends on:

```text
Parser behaviour
ODM behaviour
Input validation
Object sanitisation
MongoDB operator handling
Library versions
```

Do not assume every object passed to Mongoose is injectable.

---

# Raw Query Object

Higher-risk pattern:

```javascript
const query =
    req.body;

const user =
    await User.findOne(query);
```

Data flow:

```text
req.body
   |
   v
Mongo Query Object
   |
   v
findOne()
```

---

# MongoDB Search

```bash
rg -n \
'\.(find|findOne|findById|aggregate|updateOne|updateMany|deleteOne|deleteMany|findOneAndUpdate)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# MongoDB Operators

Search:

```bash
rg -n \
'\$(where|regex|expr|ne|gt|gte|lt|lte|in|nin|or|and|lookup|function)' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Operator use is not automatically vulnerable.

Trace whether attackers control:

```text
Operator names
Query structure
Expressions
Regular expressions
Aggregation stages
```

Refer to:

[NoSQL Injection](../web/nosql-injection.md)

---

# LDAP Injection

Node.js applications may use:

```text
ldapjs
ldapts
Active Directory libraries
Custom LDAP clients
```

Search:

```bash
rg -n -i \
'ldap|ldapjs|ldapts|searchFilter|filter:' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Candidate:

```javascript
const filter =
    `(uid=${req.body.username})`;
```

Trace attacker-controlled values into LDAP filter syntax.

Refer to:

[LDAP Injection](../web/ldap-injection.md)

---

# Command Injection

Node.js exposes process execution through:

```javascript
child_process.exec()
child_process.execSync()
child_process.spawn()
child_process.spawnSync()
execFile()
execFileSync()
```

Search:

```bash
rg -n \
'child_process|execSync\(|execFileSync\(|execFile\(|spawnSync\(|spawn\(|\bexec\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# exec()

High-risk candidate:

```javascript
const host =
    req.body.host;

exec(
    `ping -c 1 ${host}`,
    callback
);
```

Flow:

```text
req.body.host
      |
      v
Shell Command
      |
      v
exec()
      |
      v
Shell
```

Node.js documentation explicitly warns against passing unsanitised user input to shell-backed child-process execution.

---

# execSync()

Candidate:

```javascript
const output =
    execSync(
        `nslookup ${domain}`
    );
```

Search:

```bash
rg -n \
'execSync\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# spawn()

Prefer argument arrays where possible:

```javascript
spawn(
    "ping",
    [
        "-c",
        "1",
        host
    ]
);
```

This avoids shell parsing by default.

However:

```text
spawn() with argument array
        !=
Automatically secure
```

Review:

```text
Executable control
Argument semantics
Option injection
Working directory
Environment
```

---

# shell: true

Search:

```bash
rg -n \
'shell\s*:\s*true|shell\s*=\s*true' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Example:

```javascript
spawn(
    command,
    {
        shell: true
    }
);
```

Treat attacker-controlled input reaching shell-enabled execution as high priority.

Refer to:

[OS Command Injection](../web/command-injection.md)

---

# Dynamic JavaScript Execution

Search:

```bash
rg -n \
'\beval\(|new Function\(|Function\(|vm\.runIn(New|This)Context|vm\.runInContext|vm\.runInThisContext' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Candidate:

```javascript
const expression =
    req.body.expression;

const result =
    eval(expression);
```

Trace attacker control carefully.

---

# vm Module

The Node.js `vm` module is not a general security boundary for executing hostile code.

Search:

```bash
rg -n \
'node:vm|require\(["'\'']vm["'\'']\)|from ["'\'']node:vm["'\'']|runInNewContext|runInContext' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review any attempt to use it as an untrusted-code sandbox.

---

# Server-Side Template Injection

Common Node.js template engines include:

```text
EJS
Pug
Handlebars
Mustache
Nunjucks
Liquid
```

Search dependencies:

```bash
rg -n -i \
'ejs|pug|handlebars|mustache|nunjucks|liquid' \
package.json package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
```

---

# res.render()

Search:

```bash
rg -n \
'res\.render\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Normal:

```javascript
res.render(
    "profile",
    {
        username
    }
);
```

Passing attacker-controlled values as template data is not the same as allowing the attacker to control template source.

---

# Dynamic Template Names

Candidate:

```javascript
res.render(
    req.query.template,
    data
);
```

Review whether users can select unintended templates or influence template resolution.

---

# EJS

Search:

```bash
rg -n \
'ejs\.render|ejs\.renderFile|<%-' \
--glob '*.{js,mjs,cjs,ts,ejs}' \
.
```

In EJS:

```text
<%= value %>
```

and:

```text
<%- value %>
```

have different escaping behaviour.

Review unescaped output carefully.

---

# Handlebars

Search:

```bash
rg -n \
'Handlebars\.compile|handlebars\.compile|{{{' \
--glob '*.{js,mjs,cjs,ts,hbs,handlebars}' \
.
```

Triple braces can produce unescaped output.

---

# Pug

Search:

```bash
rg -n \
'!=|!{' \
--glob '*.pug' \
.
```

Review unescaped output contexts.

---

# Template Source

Search:

```bash
rg -n \
'\.compile\(|\.render\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Determine whether attacker-controlled data becomes:

```text
Template data
```

or:

```text
Template source
```

This distinction is essential.

Refer to:

[Server-Side Template Injection](../web/ssti.md)

---

# XSS

Server-side Node.js applications can introduce XSS through:

```text
Unescaped templates
HTML string construction
Unsafe redirects into script contexts
Stored data rendered without encoding
Client-side JavaScript
```

---

# res.send()

Search:

```bash
rg -n \
'res\.send\(|res\.end\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Candidate:

```javascript
const name =
    req.query.name;

res.send(
    `<h1>Hello ${name}</h1>`
);
```

Trace:

```text
req.query.name
      |
      v
HTML String
      |
      v
res.send()
      |
      v
Browser
```

---

# HTML Construction

Search:

```bash
rg -n \
'res\.send\(`|res\.send\(".*<|res\.send\('\''.*<' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Manual review is required.

---

# JSON Is Not Automatically XSS

Example:

```javascript
res.json({
    username
});
```

This is not automatically XSS simply because `username` contains HTML characters.

The downstream browser context matters.

Refer to:

```text
docs/web/xss.md
docs/web/html-injection.md
```

---

# Open Redirect

Search:

```bash
rg -n \
'res\.redirect\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Candidate:

```javascript
res.redirect(
    req.query.next
);
```

Trace whether attacker-controlled external destinations are accepted.

---

# Common Redirect Parameters

Search:

```bash
rg -n -i \
'next|redirect|returnUrl|return_url|returnTo|continue|callbackUrl' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Validate destinations using an explicit policy.

Refer to:

```text
docs/web/open-redirect.md
```

---

# SSRF

Common HTTP clients include:

```text
fetch
axios
got
undici
node-fetch
http
https
superagent
```

Search:

```bash
rg -n \
'\bfetch\(|axios\.|got\(|got\.|request\(|http\.request\(|https\.request\(|undici|superagent\.' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# SSRF Candidate

```javascript
const url =
    req.body.url;

const response =
    await fetch(url);
```

Flow:

```text
req.body.url
      |
      v
fetch()
      |
      v
Network
```

Review:

```text
Scheme
Hostname
Port
DNS resolution
IPv4
IPv6
Redirects
Private ranges
Loopback
Link-local
Cloud metadata
Egress controls
```

---

# Axios

Search:

```bash
rg -n \
'axios\.(get|post|put|patch|delete|request)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Stored SSRF

Example:

```text
POST /webhooks
       |
       v
req.body.url
       |
       v
Database
       |
       v
Background Worker
       |
       v
fetch()
```

Search beyond direct request-to-fetch flows.

Refer to:

[Server Side Request Forgery](../web/ssrf.md)

---

# Path Traversal

Common filesystem APIs:

```javascript
fs.readFile()
fs.readFileSync()
fs.writeFile()
fs.writeFileSync()
fs.createReadStream()
fs.createWriteStream()
fs.stat()
fs.unlink()
```

Search:

```bash
rg -n \
'fs\.(readFile|readFileSync|writeFile|writeFileSync|createReadStream|createWriteStream|stat|unlink|rm|readdir)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Path Construction

Search:

```bash
rg -n \
'path\.(join|resolve|normalize)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Candidate:

```javascript
const file =
    req.query.file;

const fullPath =
    path.join(
        "/srv/files",
        file
    );

res.sendFile(fullPath);
```

Do not assume:

```javascript
path.join()
```

or:

```javascript
path.resolve()
```

alone establishes containment.

Review the final canonical path and base-directory boundary.

---

# res.sendFile()

Search:

```bash
rg -n \
'res\.sendFile\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Determine who controls:

```text
Filename
Path
Root
Extension
```

---

# res.download()

Search:

```bash
rg -n \
'res\.download\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Trace attacker-controlled paths.

Refer to:

```text
docs/web/path-traversal.md
```

---

# File Upload

Node.js applications commonly use:

```text
Multer
Busboy
Formidable
express-fileupload
```

Search:

```bash
rg -n -i \
'multer|busboy|formidable|express-fileupload|req\.file|req\.files' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Multer

Search:

```bash
rg -n \
'multer\(|diskStorage|memoryStorage|fileFilter|limits' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Destination
Filename generation
Original filename
Extension
MIME type
Size
Number of files
Memory storage
Serving location
Processing
```

---

# originalname

Search:

```bash
rg -n \
'originalname|mimetype|req\.file\.path|req\.file\.filename' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Candidate:

```javascript
filename:
    (
        req,
        file,
        cb
    ) => {
        cb(
            null,
            file.originalname
        );
    }
```

Review filename handling carefully.

---

# Archive Extraction

Search:

```bash
rg -n -i \
'unzip|extract|adm-zip|unzipper|tar\.extract|extract-zip|decompress' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Zip Slip
Symlinks
Overwrite
Resource exhaustion
File count
Compression ratio
Destination
```

Refer to:

[File Upload Security](../web/file-upload.md)

---

# Deserialization

JSON parsing itself is not equivalent to unsafe native-code deserialization.

However, applications may use dangerous serialization packages or convert untrusted objects into executable structures.

Search:

```bash
rg -n -i \
'serialize|deserialize|node-serialize|unserialize|yaml\.load|js-yaml|JSON\.parse' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Do not flag every:

```javascript
JSON.parse()
```

as insecure deserialization.

Review:

```text
Library
Object type
Revivers
Prototype handling
Dynamic execution
Trust boundary
```

Refer to:

[Insecure Deserialization](../web/deserialization.md)

---

# Prototype Pollution

Prototype pollution is especially important in JavaScript source review.

Potential sources:

```javascript
req.body
req.query
JSON.parse()
```

Potential dangerous operations include:

```javascript
Object.assign()
deep merge libraries
recursive setters
dynamic property assignment
lodash merge functions
```

Search:

```bash
rg -n \
'Object\.assign\(|merge\(|mergeWith\(|defaultsDeep\(|set\(|setWith\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Dynamic Property Assignment

Search:

```bash
rg -n \
'\[[A-Za-z0-9_.$]+\]\s*=' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Candidate:

```javascript
object[
    req.body.key
] = req.body.value;
```

Review whether keys such as:

```text
__proto__
constructor
prototype
```

can affect object prototypes.

---

# Recursive Merge

Candidate:

```javascript
function merge(
    target,
    source
) {
    for (
        const key in source
    ) {
        ...
    }
}
```

Custom recursive merge implementations deserve careful review.

---

# Prototype Pollution Impact

Pollution alone may not establish meaningful impact.

Trace polluted properties into:

```text
Authorisation
Command execution
Template engines
Configuration
HTTP options
Filesystem operations
Privilege checks
```

Refer to:

[Prototype Pollution](../web/prototype-pollution.md)

---

# Mass Assignment

Candidate:

```javascript
const user =
    await User.create(
        req.body
    );
```

Potential attacker-controlled fields:

```text
role
isAdmin
permissions
verified
status
tenantId
ownerId
balance
credits
```

Search:

```bash
rg -n \
'(create|update|findOneAndUpdate|findByIdAndUpdate)\(\s*req\.body|Object\.assign\(.*req\.body|\.\.\.req\.body' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Object Spread

Candidate:

```javascript
const user = {
    ...req.body
};
```

Search:

```bash
rg -n \
'\.\.\.req\.(body|query|params)' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Safer Field Selection

Example:

```javascript
const {
    name,
    email
} = req.body;

await User.updateOne(
    {
        _id: req.user.id
    },
    {
        name,
        email
    }
);
```

Explicit field selection makes the writable model clearer.

Refer to:

[Mass Assignment](../web/mass-assignment.md)

---

# CSRF

CSRF relevance depends heavily on the authentication mechanism.

Cookie-authenticated state-changing routes deserve particular attention.

Bearer tokens supplied explicitly in an Authorization header have a different CSRF threat model.

Search:

```bash
rg -n -i \
'csrf|csurf|csrfToken|sameSite' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# State-Changing Routes

Map:

```text
POST
PUT
PATCH
DELETE
```

against:

```text
Authentication mechanism
Cookie behaviour
SameSite
CSRF controls
Origin validation
```

Do not report missing CSRF middleware without understanding authentication.

Refer to:

[Cross-Site Request Forgery](../web/csrf.md)

---

# CORS

Express applications commonly use the `cors` package.

Search:

```bash
rg -n \
'require\(["'\'']cors["'\'']\)|from ["'\'']cors["'\'']|cors\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Broad CORS

Candidate:

```javascript
app.use(
    cors()
);
```

Do not automatically report this.

Determine:

```text
Sensitive responses
Credentials
Authentication mechanism
Origin policy
Endpoint exposure
```

---

# Dynamic Origin

Candidate:

```javascript
cors({
    origin:
        (
            origin,
            callback
        ) => {
            ...
        }
});
```

Review origin validation.

Dangerous patterns may include:

```text
Substring matching
Suffix matching without boundary checks
Regex mistakes
Reflection of arbitrary Origin
```

Refer to:

[Cross-Origin Resource Sharing (CORS)](../web/cors.md)

---

# Session Management

Common Express session packages include:

```text
express-session
cookie-session
```

Search:

```bash
rg -n \
'express-session|cookie-session|session\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# express-session

Example:

```javascript
app.use(
    session({
        secret:
            process.env.SESSION_SECRET,
        resave: false,
        saveUninitialized: false,
        cookie: {
            httpOnly: true,
            secure: true,
            sameSite: "lax"
        }
    })
);
```

Review:

```text
Secret
Cookie flags
Lifetime
Store
Session regeneration
Logout
Revocation
Proxy configuration
```

---

# Default Session Store

Review whether production deployments use an appropriate session store.

Do not infer production behaviour solely from local development configuration.

---

# Cookie Configuration

Search:

```bash
rg -n \
'httpOnly|secure|sameSite|maxAge|domain|cookie\s*:' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Session Fixation

Search:

```bash
rg -n \
'session\.regenerate|req\.session\.destroy|req\.session\s*=|req\.session\.' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review authentication transitions:

```text
Anonymous
   |
   v
Login
   |
   v
Authenticated Session
```

Determine whether session identifiers and state are appropriately handled.

---

# Logout

Search:

```bash
rg -n \
'logout|session\.destroy|clearCookie' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Refer to:

```text
docs/web/session-management.md
```

---

# JWT

Common libraries:

```text
jsonwebtoken
jose
passport-jwt
express-jwt
```

Search:

```bash
rg -n -i \
'jsonwebtoken|jwt\.sign|jwt\.verify|jwt\.decode|SignJWT|jwtVerify|passport-jwt|express-jwt' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# jwt.verify

Typical:

```javascript
const payload =
    jwt.verify(
        token,
        publicKey,
        options
    );
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
Key management
```

---

# jwt.decode

Search:

```bash
rg -n \
'jwt\.decode\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Decoding a JWT is not equivalent to verifying it.

A high-value pattern is:

```javascript
const claims =
    jwt.decode(token);

if (
    claims.role === "admin"
) {
    ...
}
```

when security decisions occur before cryptographic verification.

---

# JWT Authorisation

Review:

```text
Who issues role claims?
Can roles become stale?
Are revoked accounts still accepted?
Are tenant claims trusted?
Are refresh tokens protected?
```

Refer to:

[JSON Web Token Security](../web/jwt.md)

---

# OAuth / OIDC

Common libraries:

```text
Passport
Auth0 SDKs
openid-client
OAuth provider SDKs
```

Search:

```bash
rg -n -i \
'oauth|openid|oidc|passport|clientId|clientSecret|redirectUri|callbackURL|state|nonce|code_verifier' \
--glob '*.{js,mjs,cjs,ts}' \
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
Callback handling
Account linking
Email trust
Session creation
```

Refer to:

[OAuth 2.0 and OpenID Connect Security](../web/oauth-oidc.md)

---

# SAML

Common packages may include:

```text
passport-saml
@node-saml/passport-saml
node-saml
```

Search:

```bash
rg -n -i \
'saml|passport-saml|node-saml|entryPoint|issuer|callbackUrl|cert' \
--glob '*.{js,mjs,cjs,ts}' \
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

[SAML Security](../web/saml.md)

---

# Password Reset

Search:

```bash
rg -n -i \
'forgot.?password|password.?reset|reset.?password|resetToken|reset_token|passwordReset' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Token entropy
Expiration
Single use
Account binding
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
'crypto\.randomBytes|randomUUID|Math\.random' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

For security tokens, cryptographically secure randomness is required.

`Math.random()` is not appropriate for cryptographic token generation.

Refer to:

```text
docs/web/password-reset.md
```

---

# Password Hashing

Search:

```bash
rg -n -i \
'bcrypt|argon2|scrypt|pbkdf2|createHash|passwordHash|password_hash' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Algorithm
Parameters
Salt
Comparison
Migration
Storage
```

Do not report `createHash()` solely from its presence.

Determine what is being hashed.

---

# MFA

Search:

```bash
rg -n -i \
'totp|hotp|otp|mfa|2fa|two.?factor|speakeasy|otplib|recovery.?code|backup.?code' \
--glob '*.{js,mjs,cjs,ts}' \
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
Remember-device
Bypass routes
```

Refer to:

[Multi-Factor Authentication Security](../web/mfa.md)

---

# Host Header Attacks

Search:

```bash
rg -n \
'req\.hostname|req\.headers\.host|req\.get\(["'\'']host["'\'']\)|req\.protocol|X-Forwarded-Host' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

High-value uses include:

```text
Password reset links
Email verification
OAuth callbacks
Absolute URLs
Security redirects
```

---

# Password Reset Link Example

Candidate:

```javascript
const resetUrl =
    `${req.protocol}://${req.get("host")}/reset/${token}`;
```

Trace:

```text
Host Header
    |
    v
req.get("host")
    |
    v
Password Reset URL
    |
    v
Email
```

Refer to:

[HTTP Host Header Attacks](../web/host-header-attacks.md)

---

# trust proxy

Express provides the `trust proxy` setting for deployments behind reverse proxies.

Search:

```bash
rg -n \
'trust proxy|trustProxy|app\.set\(["'\'']trust proxy' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Example:

```javascript
app.set(
    "trust proxy",
    1
);
```

Review this against the actual proxy topology.

Incorrect proxy trust may affect:

```text
req.ip
req.ips
req.hostname
req.protocol
Secure-cookie behaviour
IP-based access controls
Rate limiting
Logging
Absolute URL generation
```

Do not automatically report `trust proxy`.

Determine whether the configured trust boundary matches deployment.

---

# Forwarded Headers

Search:

```bash
rg -n -i \
'x-forwarded-for|x-forwarded-host|x-forwarded-proto|forwarded' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Map:

```text
Internet
   |
   v
Trusted Reverse Proxy
   |
   v
Forwarded Headers
   |
   v
Express
```

---

# IP-Based Security

Search:

```bash
rg -n \
'req\.ip|req\.ips|socket\.remoteAddress|connection\.remoteAddress' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

If IP addresses control:

```text
Admin access
Rate limits
Allowlisting
Internal-only endpoints
```

review proxy trust carefully.

---

# Rate Limiting

Common packages include:

```text
express-rate-limit
rate-limiter-flexible
Bottleneck
Redis-backed custom limits
```

Search:

```bash
rg -n -i \
'express-rate-limit|rate-limiter|rateLimit|limiter|too many requests|429' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Prioritise:

```text
Login
Password reset
MFA
Registration
OTP
Email verification
Expensive APIs
Exports
```

Do not conclude rate limiting is absent solely from application source.

It may be enforced by:

```text
Nginx
CDN
WAF
API gateway
Load balancer
```

Refer to:

[Rate Limiting and Anti-Automation](../web/rate-limiting.md)

---

# Security Headers

Express applications frequently use Helmet.

Search:

```bash
rg -n \
'helmet\(|Content-Security-Policy|X-Frame-Options|Strict-Transport-Security|X-Content-Type-Options|Referrer-Policy|Permissions-Policy' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Do not assume missing source-level configuration means headers are absent in production.

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
'frameguard|X-Frame-Options|frame-ancestors|helmet' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Refer to:

```text
docs/web/clickjacking.md
```

---

# Information Disclosure

Search:

```bash
rg -n \
'console\.(log|error|debug)|res\.send\(.*err|res\.json\(.*err|err\.stack|error\.stack|stack' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review whether clients receive:

```text
Stack traces
Filesystem paths
Database errors
Tokens
Secrets
Internal hostnames
Dependency details
```

---

# Error Middleware

Express error handlers commonly resemble:

```javascript
app.use(
    (
        err,
        req,
        res,
        next
    ) => {
        ...
    }
);
```

Search:

```bash
rg -n \
'err\.stack|error\.stack|NODE_ENV|app\.use\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Check production behaviour.

---

# Logging

Common libraries:

```text
Winston
Pino
Morgan
Bunyan
Console
```

Search:

```bash
rg -n \
'console\.(log|error|debug|warn)|logger\.(info|debug|warn|error|fatal)|pino\(|winston|morgan\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review for:

```text
Authorization headers
JWTs
Session cookies
Passwords
API keys
Reset tokens
MFA codes
Personal data
Request bodies
```

---

# Log Injection

Candidate:

```javascript
logger.info(
    `Login failed for ${req.body.username}`
);
```

Determine:

```text
Log format
Structured logging
Escaping
Downstream consumers
```

Do not automatically classify user-controlled log content as exploitable log injection.

---

# Business Logic

Search:

```bash
rg -n -i \
'price|amount|balance|credit|discount|coupon|refund|quantity|inventory|approved|verified|status|role|permission' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Prioritise:

```text
Payments
Refunds
Credits
Coupons
Inventory
Subscriptions
Approval workflows
Verification
Role changes
Tenant changes
```

---

# Client-Controlled Price

Candidate:

```javascript
const {
    productId,
    price
} = req.body;

await Order.create({
    productId,
    price
});
```

Question:

```text
Should price come from trusted server-side product data?
```

Refer to:

[Business Logic Vulnerabilities](../web/business-logic.md)

---

# Race Conditions

Node.js being event-driven does not eliminate race conditions.

Example:

```javascript
const account =
    await Account.findById(id);

if (
    account.balance >= amount
) {
    account.balance -= amount;

    await account.save();
}
```

Concurrent requests may interact with the same logical state.

---

# Race Review

Search:

```bash
rg -n -i \
'transaction|startSession|withTransaction|lock|mutex|version|optimistic|increment|decrement|\$inc' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Read-check-write sequences
One-time tokens
Credits
Coupons
Inventory
Balances
Approvals
```

---

# Database Atomic Operations

Look for atomic operations such as:

```text
$inc
findOneAndUpdate
transactions
conditional UPDATE
optimistic locking
```

Their presence does not automatically prove the workflow is race-safe.

Refer to:

[Race Conditions](../web/race-conditions.md)

---

# Promise and Async Control Flow

Search:

```bash
rg -n \
'async |await |Promise\.all|Promise\.race|forEach\(async|map\(async' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Security bugs can occur through incorrect asynchronous assumptions.

---

# forEach(async)

Candidate:

```javascript
items.forEach(
    async item => {
        await authorise(item);
    }
);

performAction();
```

The surrounding code may continue before asynchronous callbacks finish.

Review security-sensitive async flows carefully.

---

# Missing await

Source review should inspect security functions that return promises.

Candidate:

```javascript
if (
    checkPermission(user)
) {
    performSensitiveAction();
}
```

If `checkPermission()` returns a Promise, this logic may not behave as intended.

TypeScript and linting can help identify these mistakes.

---

# Background Jobs

Common systems:

```text
Bull
BullMQ
Agenda
Bee-Queue
RabbitMQ
Kafka
SQS
Custom workers
```

Search:

```bash
rg -n -i \
'bullmq|bull|agenda|queue\.add|worker|consumer|producer|kafka|rabbit|amqp|sqs' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Second-Order Data Flow

Example:

```text
HTTP Request
     |
     v
Database
     |
     v
Queue
     |
     v
Worker
     |
     v
Dangerous Sink
```

This is common with:

```text
Webhook delivery
PDF generation
File processing
Email
Image processing
URL previews
Exports
```

---

# Webhooks

Search:

```bash
rg -n -i \
'webhook|signature|hmac|x-signature|stripe-signature' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review inbound webhooks for:

```text
Signature verification
Raw body handling
Replay
Timestamp
Secret storage
Event authorisation
Idempotency
```

Review outbound webhooks for SSRF.

---

# GraphQL

Common frameworks:

```text
Apollo Server
GraphQL Yoga
Mercurius
express-graphql
graphql-js
```

Search:

```bash
rg -n -i \
'apollo|graphql|resolver|typeDefs|Query:|Mutation:|GraphQLObjectType' \
--glob '*.{js,mjs,cjs,ts,graphql,gql}' \
.
```

---

# Resolver Discovery

Search:

```bash
rg -n \
'Query\s*:|Mutation\s*:|Subscription\s*:|resolve\s*:' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Map:

```text
Query
Mutation
Subscription
Resolver
Service
Database
```

---

# GraphQL Authorisation

Candidate:

```javascript
user:
    async (
        parent,
        { id }
    ) => {
        return User.findById(id);
    }
```

Question:

```text
Where is object-level authorisation?
```

Do not assume HTTP endpoint authentication protects every resolver correctly.

---

# GraphQL Controls

Review:

```text
Authentication
Resolver authorisation
Field-level access
Object-level access
Depth
Complexity
Batching
Introspection
Subscriptions
File uploads
```

Refer to:

[GraphQL API Security](../web/graphql.md)

---

# WebSockets

Common libraries:

```text
socket.io
ws
uWebSockets.js
```

Search:

```bash
rg -n \
'socket\.on\(|io\.on\(|new WebSocket|WebSocketServer|new Server\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Socket.IO

Example:

```javascript
io.on(
    "connection",
    socket => {
        socket.on(
            "join-room",
            handler
        );
    }
);
```

Map each event as an endpoint:

```text
Socket Connection
      |
      +-- join-room
      +-- send-message
      +-- delete-message
      +-- admin-action
```

---

# WebSocket Authentication

Search:

```bash
rg -n \
'io\.use\(|socket\.handshake|socket\.request|socket\.data|socket\.user' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Connection authentication
Event authorisation
Room access
Tenant isolation
Object access
Origin handling
Session lifecycle
```

Refer to:

[WebSocket Security](../web/websockets.md)

---

# gRPC

Node.js gRPC commonly uses:

```text
@grpc/grpc-js
@grpc/proto-loader
```

Search:

```bash
rg -n -i \
'@grpc/grpc-js|proto-loader|loadPackageDefinition|addService|grpc\.' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Find protocol files:

```bash
find . -type f -name '*.proto' -print
```

Review:

```text
Service methods
Authentication metadata
Authorisation
Object-level access
Message validation
TLS
Internal trust assumptions
```

Refer to:

[gRPC Security](../web/grpc-security.md)

---

# HTTP Request Smuggling

Application source alone is usually insufficient to prove HTTP request smuggling.

Review the complete chain:

```text
Client
  |
  v
CDN / WAF
  |
  v
Reverse Proxy
  |
  v
Load Balancer
  |
  v
Node.js / Express
```

Relevant files include:

```text
Nginx configuration
HAProxy configuration
Ingress configuration
Cloud load balancer settings
Node.js version
Express version
Proxy middleware
```

Do not report request smuggling based solely on an Express route.

Refer to:

[HTTP Request Smuggling](../web/http-request-smuggling.md)

---

# Cache Security

Search:

```bash
rg -n -i \
'cache|redis|node-cache|lru-cache|Cache-Control|Vary|etag' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review cache keys for:

```text
User
Tenant
Role
Authorization
Cookie
Host
Query parameters
Language
```

---

# User-Specific Cache

Candidate:

```javascript
const key =
    `profile:${req.params.id}`;
```

Question:

```text
Does this cache entry require tenant or permission context?
```

Refer to:

```text
docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md
```

---

# Secrets Exposure

Search:

```bash
rg -n -i \
'password|passwd|secret|api[_-]?key|client[_-]?secret|access[_-]?key|private[_-]?key|token|database_url|mongodb_uri|redis_url' \
.
```

---

# Common Secret Locations

Inspect:

```text
.env
.env.*
config/
package.json
Dockerfile
docker-compose.yml
Kubernetes manifests
Terraform
CI/CD files
Shell scripts
PM2 configuration
```

Find:

```bash
find . -type f \( \
-name '.env' \
-o -name '.env.*' \
-o -name '*secret*' \
-o -name '*.pem' \
-o -name '*.key' \
-o -name '*.p12' \
-o -name '*.pfx' \
\) -print
```

Handle real secrets carefully.

---

# Environment Variables

Search:

```bash
rg -n \
'process\.env' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Environment variables are a configuration mechanism, not a complete secret-management solution.

Review:

```text
Fallback values
Logging
Deployment configuration
CI/CD
Container manifests
Access permissions
Rotation
```

---

# Git History

Search:

```bash
git log --all --oneline
```

Search history:

```bash
git log -S 'API_KEY' --all
```

or:

```bash
git log -S 'SECRET' --all
```

Refer to:

```text
docs/web/secrets-exposure.md
```

---

# Cryptography

Search:

```bash
rg -n \
'crypto\.|createCipher|createDecipher|createHash|createHmac|randomBytes|randomUUID|pbkdf2|scrypt' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Review:

```text
Algorithm
Mode
Key management
IV / nonce generation
Authentication
Randomness
Password hashing
Hard-coded keys
```

---

# Weak Randomness

Search:

```bash
rg -n \
'Math\.random\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Do not report every use.

Prioritise when used for:

```text
Tokens
Passwords
Reset codes
MFA
Session identifiers
Security nonces
```

---

# Dependencies

Node.js applications often have large dependency trees.

Inspect:

```bash
npm ls
```

Production dependencies:

```bash
npm ls \
--omit=dev
```

---

# npm audit

Run:

```bash
npm audit
```

JSON output:

```bash
npm audit \
--json
```

A dependency advisory is not automatically an exploitable application vulnerability.

Determine:

```text
Installed version
Affected version
Affected functionality
Reachability
Runtime usage
Attacker control
Deployment
```

---

# OSV-Scanner

```bash
osv-scanner scan source -r .
```

---

# Lock Files

Review:

```text
package-lock.json
yarn.lock
pnpm-lock.yaml
```

These help establish the resolved dependency versions.

---

# Supply Chain Review

Review:

```text
Install scripts
postinstall
preinstall
Git dependencies
Local path dependencies
Unpinned Git references
Private registries
.npmrc
Package provenance
CI install commands
```

Search:

```bash
rg -n \
'"(preinstall|install|postinstall|prepare)"\s*:' \
package.json
```

Refer to:

```text
docs/web/dependency-security.md
```

---

# Third-Party JavaScript

If Express serves browser-side JavaScript, also inspect:

```text
public/
static/
assets/
views/
frontend/
```

Review:

```text
External scripts
CDNs
SRI
CSP
Outdated libraries
Source maps
Secrets
DOM sinks
```

Refer to:

```text
docs/web/third-party-javascript.md
docs/source-code-review/javascript.md
```

---

# Source Maps

Find:

```bash
find . -type f -name '*.map' -print
```

Search:

```bash
rg -n \
'sourceMappingURL|sourceMap' \
.
```

Determine whether production source maps expose:

```text
Source code
Internal paths
API endpoints
Comments
Secrets
```

Do not report source maps solely because they exist.

---

# Static Analysis

Useful tools include:

```text
Semgrep
CodeQL
ESLint security plugins
npm audit
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

Semgrep can help identify candidates involving:

```text
Command injection
SQL injection
XSS
Path traversal
SSRF
Prototype pollution
Unsafe deserialization
Hard-coded secrets
```

Manual validation remains required.

---

# CodeQL

CodeQL supports JavaScript and TypeScript and provides data-flow and taint-tracking analysis.

Typical model:

```text
req.body.url
      |
      v
Controller
      |
      v
Service
      |
      v
HTTP Client
```

or:

```text
req.query.cmd
      |
      v
Helper
      |
      v
child_process.exec()
```

CodeQL is particularly useful when source and sink are separated across several functions or modules.

---

# ESLint

If ESLint is configured:

```bash
npx eslint .
```

Inspect:

```text
eslint.config.js
.eslintrc
.eslintrc.js
.eslintrc.json
```

Security-focused ESLint plugins may add useful checks, but lint results still require manual validation.

---

# Broad Node.js Search

```bash
rg -n \
'req\.(query|params|body|headers|cookies|signedCookies|file|files|hostname|ip|protocol)|\b(app|router)\.(get|post|put|patch|delete|all)\(|app\.use\(|router\.use\(|\.query\(|\.execute\(|\.raw\(|\$queryRaw|\$executeRaw|child_process|execSync\(|execFile\(|spawn\(|shell\s*:\s*true|\beval\(|new Function\(|vm\.runIn|res\.render\(|res\.send\(|res\.redirect\(|\bfetch\(|axios\.|got\(|http\.request\(|https\.request\(|fs\.(readFile|writeFile|createReadStream|createWriteStream)\(|res\.sendFile\(|res\.download\(|multer\(|Object\.assign\(|merge\(|\.\.\.req\.body|jwt\.decode\(|jwt\.verify\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

This discovers candidates.

It does not prove vulnerabilities.

---

# Route Search

```bash
rg -n \
'\b(app|router)\.(get|post|put|patch|delete|options|head|all)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Middleware Search

```bash
rg -n \
'app\.use\(|router\.use\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Input Search

```bash
rg -n \
'req\.(query|params|body|headers|cookies|signedCookies|file|files)|req\.(get|header)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Authentication Search

```bash
rg -n -i \
'authenticate|requireAuth|passport|jwt|bearer|session|login|req\.user|api.?key' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Authorisation Search

```bash
rg -n -i \
'authorize|authorise|permission|role|admin|owner|tenant|organization|organisation|workspace|req\.user' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# SQL Search

```bash
rg -n \
'\.(query|execute|raw)\(|\$queryRaw|\$executeRaw|sequelize\.query|knex\.raw|whereRaw|orderByRaw' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# NoSQL Search

```bash
rg -n \
'\.(find|findOne|findById|aggregate|updateOne|updateMany|findOneAndUpdate)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Command Search

```bash
rg -n \
'child_process|execSync\(|execFileSync\(|execFile\(|spawnSync\(|spawn\(|shell\s*:\s*true' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Dynamic Execution Search

```bash
rg -n \
'\beval\(|new Function\(|vm\.runIn(New|This)Context|vm\.runInContext' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# SSTI Search

```bash
rg -n \
'res\.render\(|ejs\.render|Handlebars\.compile|handlebars\.compile|nunjucks|pug\.render|\.compile\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# XSS Search

```bash
rg -n \
'res\.send\(|<%-|{{{|!=|!{' \
--glob '*.{js,mjs,cjs,ts,ejs,hbs,handlebars,pug}' \
.
```

---

# Redirect Search

```bash
rg -n \
'res\.redirect\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# SSRF Search

```bash
rg -n \
'\bfetch\(|axios\.(get|post|put|patch|delete|request)\(|got\(|http\.request\(|https\.request\(|undici' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Filesystem Search

```bash
rg -n \
'fs\.(readFile|readFileSync|writeFile|writeFileSync|createReadStream|createWriteStream)|path\.(join|resolve|normalize)|res\.sendFile\(|res\.download\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Upload Search

```bash
rg -n \
'multer\(|req\.file|req\.files|originalname|diskStorage|fileFilter' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Prototype Pollution Search

```bash
rg -n \
'Object\.assign\(|merge\(|mergeWith\(|defaultsDeep\(|set\(|setWith\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Mass Assignment Search

```bash
rg -n \
'\.\.\.req\.(body|query)|Object\.assign\(.*req\.(body|query)|(create|update|findOneAndUpdate)\(\s*req\.body' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# JWT Search

```bash
rg -n \
'jwt\.(sign|verify|decode)\(|SignJWT|jwtVerify|jsonwebtoken|passport-jwt' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Secret Search

```bash
rg -n -i \
'secret|password|passwd|api[_-]?key|client[_-]?secret|private[_-]?key|access[_-]?token|refresh[_-]?token' \
.
```

---

# Reverse Sink Analysis

For large repositories, starting at dangerous sinks is often efficient.

Example:

```text
child_process.exec()
        ^
        |
Utility
        ^
        |
Service
        ^
        |
Controller
        ^
        |
req.body
```

High-value sinks include:

```text
exec()
execSync()
spawn(shell=true)

eval()
Function()
vm.*

db.query()
raw SQL

Mongo raw query structures

fetch()
axios()
got()

fs.readFile()
fs.writeFile()
res.sendFile()

res.send()
unescaped templates

res.redirect()

Object.assign()
deep merge functions
```

---

# Forward Source Analysis

Start from:

```text
req.query
req.params
req.body
req.headers
req.cookies
req.file
req.files
```

Trace:

```text
SOURCE
  |
  v
ROUTE
  |
  v
MIDDLEWARE
  |
  v
CONTROLLER
  |
  v
SERVICE
  |
  v
REPOSITORY
  |
  v
SINK
```

---

# Source-to-Sink Example - SQL Injection

```text
GET /search?q=admin
       |
       v
req.query.q
       |
       v
Template Literal SQL
       |
       v
db.query()
```

---

# Source-to-Sink Example - NoSQL Injection

```text
POST /search
      |
      v
req.body
      |
      v
Mongo Query Object
      |
      v
User.find()
```

Question:

```text
Can the attacker control MongoDB query structure or operators?
```

---

# Source-to-Sink Example - Command Injection

```text
POST /diagnostics
       |
       v
req.body.host
       |
       v
Template Literal
       |
       v
exec()
       |
       v
Shell
```

---

# Source-to-Sink Example - SSRF

```text
POST /preview
       |
       v
req.body.url
       |
       v
fetch()
       |
       v
Network
```

---

# Source-to-Sink Example - IDOR

```text
GET /documents/:id
       |
       v
req.params.id
       |
       v
Document.findById()
       |
       v
Document
       |
       v
res.json()
```

Question:

```text
Where is object-level authorisation?
```

---

# Source-to-Sink Example - Stored XSS

```text
POST /profile
      |
      v
req.body.bio
      |
      v
Database
      |
      v
EJS <%- bio %>
      |
      v
Browser
```

---

# Source-to-Sink Example - Path Traversal

```text
GET /download?file=...
       |
       v
req.query.file
       |
       v
path.join()
       |
       v
res.sendFile()
```

---

# Source-to-Sink Example - Prototype Pollution

```text
POST /settings
       |
       v
req.body
       |
       v
Deep Merge
       |
       v
Object Prototype
       |
       v
Security-Sensitive Property
```

Impact must be traced separately.

---

# Source-to-Sink Example - Mass Assignment

```text
PATCH /users/me
       |
       v
req.body
       |
       v
User.findByIdAndUpdate(
    id,
    req.body
)
       |
       v
Sensitive Model Fields
```

---

# Source-to-Sink Example - Stored SSRF

```text
POST /webhooks
       |
       v
req.body.url
       |
       v
Database
       |
       v
BullMQ Job
       |
       v
Worker
       |
       v
axios.post()
```

---

# Variant Analysis

Once a vulnerability is confirmed, search for other occurrences of the same root cause.

---

# IDOR Variants

```bash
rg -n \
'\.(findById|findOne|findUnique|findFirst|findByPk)\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

Compare against:

```text
req.user
owner
tenant
permission
role
```

---

# SQL Injection Variants

```bash
rg -n \
'\.(query|execute|raw)\(|\$queryRawUnsafe|\$executeRawUnsafe|whereRaw|orderByRaw' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Command Injection Variants

```bash
rg -n \
'exec\(|execSync\(|spawn\(|shell\s*:\s*true' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# SSRF Variants

```bash
rg -n \
'\bfetch\(|axios\.|got\(|http\.request\(|https\.request\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# XSS Variants

```bash
rg -n \
'res\.send\(|<%-|{{{|!=' \
--glob '*.{js,mjs,cjs,ts,ejs,hbs,pug}' \
.
```

---

# Prototype Pollution Variants

```bash
rg -n \
'Object\.assign\(|merge\(|mergeWith\(|defaultsDeep\(|set\(' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Mass Assignment Variants

```bash
rg -n \
'\.\.\.req\.body|Object\.assign\(.*req\.body|(create|update|findOneAndUpdate)\(\s*req\.body' \
--glob '*.{js,mjs,cjs,ts}' \
.
```

---

# Compare Similar Routes

Example:

```text
GET /documents/:id
    -> authenticate
    -> owner check

PATCH /documents/:id
    -> authenticate
    -> owner check

DELETE /documents/:id
    -> authenticate
    -> no owner check
```

The inconsistency is a strong review signal.

---

# Compare Interfaces

The same object may be exposed through:

```text
REST
GraphQL
WebSocket
Admin API
Background Job
```

Example:

```text
User Object
   |
   +-- GET /api/users/:id
   |
   +-- GraphQL user(id)
   |
   +-- Socket.IO get-user
   |
   +-- Admin API
```

Review security controls across all paths.

---

# Node.js Review Matrix

| Vulnerability | High-Value Targets |
|---|---|
| Authentication | middleware, Passport, JWT, sessions |
| Authorisation | roles, permissions, ownership |
| IDOR / BOLA | database lookups from IDs |
| SQL Injection | raw queries, string construction |
| NoSQL Injection | Mongo query objects |
| LDAP Injection | dynamic LDAP filters |
| Command Injection | `exec`, shell-enabled `spawn` |
| SSTI | template compilation/rendering |
| XSS | unescaped templates, `res.send()` |
| CSRF | cookie-authenticated state changes |
| CORS | `cors()` configuration |
| Open Redirect | `res.redirect()` |
| SSRF | `fetch`, Axios, Got |
| Path Traversal | `fs`, `sendFile`, path construction |
| File Upload | Multer and upload handlers |
| Deserialization | unsafe serialization libraries |
| Prototype Pollution | deep merge and dynamic properties |
| Mass Assignment | `req.body` into models |
| Session Security | express-session, cookie-session |
| JWT | jsonwebtoken, jose |
| OAuth/OIDC | Passport and OIDC clients |
| SAML | node-saml integrations |
| Host Header | `req.hostname`, Host-based URLs |
| Proxy Trust | `trust proxy` |
| Race Conditions | read-check-write workflows |
| Rate Limiting | middleware/infrastructure |
| Business Logic | services and workflows |
| GraphQL | resolvers and mutations |
| WebSockets | Socket.IO events |
| gRPC | service methods |
| Secrets | environment/config/history |
| Dependencies | package manifests/lockfiles |

---

# Node.js Review Checklist

## Project Discovery

```text
[ ] Node.js version identified
[ ] Framework identified
[ ] package.json reviewed
[ ] Lock file reviewed
[ ] Application entry point identified
[ ] TypeScript configuration reviewed
[ ] Routers mapped
[ ] Middleware mapped
[ ] Controllers mapped
[ ] Services mapped
[ ] Models/repositories mapped
[ ] Background jobs mapped
```

## Routes

```text
[ ] app.get reviewed
[ ] app.post reviewed
[ ] app.put reviewed
[ ] app.patch reviewed
[ ] app.delete reviewed
[ ] router routes reviewed
[ ] Router mount paths combined
[ ] Middleware ordering reviewed
```

## Input

```text
[ ] req.query reviewed
[ ] req.params reviewed
[ ] req.body reviewed
[ ] req.headers reviewed
[ ] req.cookies reviewed
[ ] req.file reviewed
[ ] req.files reviewed
[ ] Raw bodies reviewed
```

## Authentication

```text
[ ] Authentication middleware reviewed
[ ] Router-level authentication reviewed
[ ] Sessions reviewed
[ ] JWT reviewed
[ ] API keys reviewed
[ ] Password hashing reviewed
[ ] Password reset reviewed
[ ] MFA reviewed
[ ] OAuth/OIDC reviewed
[ ] SAML reviewed
```

## Authorisation

```text
[ ] Role checks reviewed
[ ] Permission checks reviewed
[ ] Ownership checks reviewed
[ ] Tenant isolation reviewed
[ ] CRUD operations compared
[ ] API interfaces compared
[ ] GraphQL authorisation reviewed
[ ] WebSocket authorisation reviewed
```

## Injection

```text
[ ] Raw SQL reviewed
[ ] ORM raw APIs reviewed
[ ] Mongo query structures reviewed
[ ] LDAP filters reviewed
[ ] exec reviewed
[ ] execSync reviewed
[ ] spawn reviewed
[ ] shell:true reviewed
[ ] eval reviewed
[ ] Function reviewed
[ ] vm usage reviewed
```

## Client-Side and Templates

```text
[ ] Template engine identified
[ ] Unescaped output reviewed
[ ] res.send HTML reviewed
[ ] Dynamic templates reviewed
[ ] Redirects reviewed
[ ] CSRF reviewed
[ ] CORS reviewed
[ ] Security headers reviewed
```

## Server-Side

```text
[ ] Outbound HTTP requests reviewed
[ ] Filesystem reads reviewed
[ ] Filesystem writes reviewed
[ ] sendFile reviewed
[ ] download reviewed
[ ] Uploads reviewed
[ ] Archive extraction reviewed
[ ] Deserialization reviewed
```

## JavaScript-Specific

```text
[ ] Prototype pollution reviewed
[ ] Dynamic properties reviewed
[ ] Deep merges reviewed
[ ] Mass assignment reviewed
[ ] Async security logic reviewed
[ ] Promise handling reviewed
```

## Infrastructure

```text
[ ] trust proxy reviewed
[ ] Forwarded headers reviewed
[ ] Host handling reviewed
[ ] IP-based controls reviewed
[ ] Rate limiting reviewed
[ ] Cache behaviour reviewed
```

## APIs

```text
[ ] REST reviewed
[ ] GraphQL reviewed
[ ] WebSockets reviewed
[ ] gRPC reviewed
[ ] Webhooks reviewed
```

## Business Logic

```text
[ ] Prices reviewed
[ ] Balances reviewed
[ ] Credits reviewed
[ ] Discounts reviewed
[ ] Refunds reviewed
[ ] Inventory reviewed
[ ] Approval flows reviewed
[ ] State transitions reviewed
[ ] Race conditions reviewed
```

## Secrets and Dependencies

```text
[ ] Hard-coded secrets searched
[ ] Environment files reviewed
[ ] Git history considered
[ ] npm dependencies reviewed
[ ] Lock file reviewed
[ ] npm audit considered
[ ] OSV-Scanner considered
[ ] Install scripts reviewed
```

## Static Analysis

```text
[ ] ripgrep searches performed
[ ] Semgrep considered
[ ] CodeQL considered
[ ] ESLint considered
[ ] Findings manually validated
[ ] Variant analysis performed
```

---

# Finding Validation Model

Before reporting:

```text
STATIC MATCH
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
SECURITY IMPACT?
     |
     v
CONFIRMED FINDING
```

---

# Example Finding - IDOR

```text
Title:
Missing Object-Level Authorisation on Document Endpoint

Route:
GET /api/documents/:id

Source:
req.params.id

Data Flow:

req.params.id
      |
      v
Document.findById()
      |
      v
Document
      |
      v
res.json()

Authentication:
Authentication middleware is present.

Authorisation:
No ownership or tenant restriction was identified before returning the document.

Impact:
An authenticated user may be able to access another user's document by supplying its identifier.

Recommendation:
Scope the lookup to objects the authenticated user is authorised to access or perform an equivalent object-level permission check.
```

---

# Example Finding - Command Injection

```text
Title:
OS Command Injection in Diagnostics Endpoint

Route:
POST /api/diagnostics

Source:
req.body.host

Data Flow:

req.body.host
      |
      v
Template Literal
      |
      v
child_process.exec()
      |
      v
Shell

Security Control:
No effective validation prevents attacker-controlled input from altering shell syntax.

Recommendation:
Avoid shell command construction. Invoke the required executable directly with controlled arguments and validate attacker-controlled values according to the expected input format.
```

---

# Example Finding - SSRF

```text
Title:
Server-Side Request Forgery in URL Preview Endpoint

Route:
POST /api/preview

Source:
req.body.url

Data Flow:

req.body.url
      |
      v
fetch()
      |
      v
Network

Security Control:
No effective destination restriction was identified.

Impact:
The application may make server-side requests to destinations selected by the user, potentially including internal services depending on network access.

Recommendation:
Prefer server-controlled destinations. Where arbitrary external URLs are required, implement strict destination validation and network-level egress restrictions.
```

---

# Example Finding - NoSQL Injection

```text
Title:
User-Controlled MongoDB Query Structure

Route:
POST /api/users/search

Source:
req.body

Data Flow:

req.body
      |
      v
User.find(req.body)
      |
      v
MongoDB

Security Concern:
The complete query object is supplied by the client rather than being constructed from server-controlled query structure.

Recommendation:
Define the permitted query structure server-side and copy only explicitly supported fields and operators from validated client input.
```

---

# Example Finding - Mass Assignment

```text
Title:
Mass Assignment in User Profile Update

Route:
PATCH /api/users/me

Source:
req.body

Data Flow:

req.body
      |
      v
User.findByIdAndUpdate(
    req.user.id,
    req.body
)
      |
      v
User Model

Security Concern:
The client may be able to modify fields that were not intended to be user-controlled.

Recommendation:
Define an explicit allowlist of writable profile fields and construct the update object from those validated fields.
```

---

# Example Finding - Stored XSS

```text
Title:
Stored Cross-Site Scripting Through Unescaped EJS Output

Source:
req.body.biography

Data Flow:

POST /profile
      |
      v
req.body.biography
      |
      v
Database
      |
      v
<%- biography %>
      |
      v
Browser

Security Control:
Template output escaping is explicitly bypassed for the stored value.

Recommendation:
Use escaped template output for attacker-controlled values. If rich HTML is required, use an appropriate allowlist-based HTML sanitisation strategy.
```

---

# Common Review Mistakes

## Express Route Without auth Middleware Means Unauthenticated

Incorrect.

Authentication may exist at:

```text
app.use()
router.use()
Parent router
Reverse proxy
API gateway
```

Trace the complete request path.

---

# req.user Means Authorisation Exists

Incorrect.

It usually establishes identity.

You must still check:

```text
Ownership
Role
Permission
Tenant
Action
```

---

# Every db.query() Is SQL Injection

Incorrect.

Review whether values are correctly parameterised.

---

# Every Mongo Query Is NoSQL Injection

Incorrect.

Determine whether attackers control query structure or dangerous operators.

---

# Every exec() Is Command Injection

Incorrect.

Trace attacker control.

However, attacker-controlled data entering shell command construction is a high-priority candidate.

---

# Every spawn() Is Safe

Incorrect.

Review:

```text
shell option
Executable
Arguments
Option injection
Program semantics
```

---

# Every fetch() Is SSRF

Incorrect.

Determine who controls the destination.

---

# Every res.send() Is XSS

Incorrect.

Determine:

```text
Response content type
HTML context
Attacker control
Encoding
Downstream handling
```

---

# Every res.redirect() Is Open Redirect

Incorrect.

Determine whether the attacker can choose an external destination.

---

# Every Object.assign() Is Prototype Pollution

Incorrect.

Trace:

```text
Attacker-controlled keys
Merge semantics
Library behaviour
Prototype targets
Impact
```

---

# Every req.body Model Update Is Mass Assignment

Incorrect.

Schemas, ORM field restrictions or prior field selection may constrain the update.

Trace actual writable fields.

---

# Missing express-rate-limit Means No Rate Limiting

Incorrect.

Infrastructure may enforce it.

---

# Missing Helmet Means Missing Security Headers

Incorrect.

Headers may be supplied by:

```text
Reverse proxy
CDN
WAF
Load balancer
```

Validate deployed responses.

---

# trust proxy Means Vulnerable

Incorrect.

Its correctness depends on the real network topology.

---

# Dependency Advisory Means Exploitable Vulnerability

Incorrect.

Validate:

```text
Version
Reachability
Affected functionality
Attacker control
Deployment
```

---

# Final Node.js Review Model

```text
                       NODE.JS / EXPRESS
                              |
                              v
                            ROUTE
                              |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
    req.query             req.params             req.body
        |                     |                     |
        +---------------------+---------------------+
                              |
                              v
                          MIDDLEWARE
                              |
              +---------------+---------------+
              |                               |
              v                               v
       AUTHENTICATION                   VALIDATION
              |                               |
              +---------------+---------------+
                              |
                              v
                        AUTHORISATION
                              |
                              v
                       BUSINESS LOGIC
                              |
    +-------------+-----------+-----------+-------------+
    |             |           |           |             |
    v             v           v           v             v
 DATABASE      TEMPLATE      FILE       HTTP          PROCESS
    |             |           |           |             |
    v             v           v           v             v
SQL/NoSQL      XSS/SSTI    Traversal     SSRF       Command
                                                   Injection

                    +----------------------+
                    |
                    v
              OBJECT OPERATIONS
                    |
          +---------+---------+
          |                   |
          v                   v
   Mass Assignment      Prototype Pollution

                    +----------------------+
                    |
                    v
              ASYNC / BACKGROUND
                    |
          +---------+---------+
          |                   |
          v                   v
       Queue              Worker
          |                   |
          +---------+---------+
                    |
                    v
              Second-Order Sink
```

The central question is:

```text
Can attacker-controlled data reach a security-sensitive operation
without an effective validation, authentication, authorisation or
other security boundary?
```

Evaluate:

```text
Source
+
Route
+
Middleware
+
Transformations
+
Validation
+
Authentication
+
Authorisation
+
Framework protections
+
Sink
+
Reachability
+
Exploitability
+
Impact
```

Only then classify a candidate as a confirmed vulnerability.

---

# References

## Node.js Documentation

[api](https://nodejs.org/docs/latest/api/){ target="_blank" rel="noopener noreferrer" }

## Node.js Child Processes

[Node.js Child Processes](https://nodejs.org/api/child_process.html){ target="_blank" rel="noopener noreferrer" }

## Node.js File System

[Node.js File System](https://nodejs.org/api/fs.html){ target="_blank" rel="noopener noreferrer" }

## Node.js Crypto

[Node.js Crypto](https://nodejs.org/api/crypto.html){ target="_blank" rel="noopener noreferrer" }

## Node.js HTTP

[Node.js HTTP](https://nodejs.org/api/http.html){ target="_blank" rel="noopener noreferrer" }

## Express Documentation

[expressjs.com](https://expressjs.com/){ target="_blank" rel="noopener noreferrer" }

## Express API

[Express API](https://expressjs.com/en/api.html){ target="_blank" rel="noopener noreferrer" }

## Express Security Best Practices

[Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html){ target="_blank" rel="noopener noreferrer" }

## Express Production Best Practices

[Express Production Best Practices](https://expressjs.com/en/advanced/best-practice-performance.html){ target="_blank" rel="noopener noreferrer" }

## Express Behind Proxies

[Express Behind Proxies](https://expressjs.com/en/guide/behind-proxies.html){ target="_blank" rel="noopener noreferrer" }

## express-session

[express-session](https://expressjs.com/en/resources/middleware/session.html){ target="_blank" rel="noopener noreferrer" }

## Helmet

[Helmet](https://helmetjs.github.io/){ target="_blank" rel="noopener noreferrer" }

## Mongoose

[Mongoose](https://mongoosejs.com/docs/){ target="_blank" rel="noopener noreferrer" }

## MongoDB Node.js Driver

[MongoDB Node.js Driver](https://www.mongodb.com/docs/drivers/node/current/){ target="_blank" rel="noopener noreferrer" }

## Sequelize

[Sequelize](https://sequelize.org/docs/){ target="_blank" rel="noopener noreferrer" }

## Prisma

[Prisma](https://www.prisma.io/docs/){ target="_blank" rel="noopener noreferrer" }

## Knex

[Knex](https://knexjs.org/){ target="_blank" rel="noopener noreferrer" }

## jsonwebtoken

[jsonwebtoken](https://github.com/auth0/node-jsonwebtoken){ target="_blank" rel="noopener noreferrer" }

## OWASP Code Review Guide

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

## OWASP Cheat Sheet Series

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

## OWASP Node.js Security Cheat Sheet

[OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## OWASP ASVS

[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/){ target="_blank" rel="noopener noreferrer" }

## OWASP Web Security Testing Guide

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

## CWE

[CWE](https://cwe.mitre.org/){ target="_blank" rel="noopener noreferrer" }

## Semgrep

[Semgrep](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

## CodeQL for JavaScript and TypeScript

[CodeQL for JavaScript and TypeScript](https://codeql.github.com/docs/codeql-language-guides/codeql-for-javascript/){ target="_blank" rel="noopener noreferrer" }

## CodeQL JavaScript Data Flow

[CodeQL JavaScript Data Flow](https://codeql.github.com/docs/codeql-language-guides/analyzing-data-flow-in-javascript-and-typescript/){ target="_blank" rel="noopener noreferrer" }

## npm audit

[npm audit](https://docs.npmjs.com/cli/commands/npm-audit){ target="_blank" rel="noopener noreferrer" }

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
docs/source-code-review/flask.md
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

docs/web/prototype-pollution.md
docs/web/mass-assignment.md

docs/web/host-header-attacks.md
docs/web/http-security-headers.md
docs/web/http-request-smuggling.md
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

docs/web/web-cache-poisoning.md
docs/web/web-cache-deception.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md
```
