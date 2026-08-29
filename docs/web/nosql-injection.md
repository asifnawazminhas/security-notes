# NoSQL Injection

NoSQL injection occurs when attacker-controlled input changes the structure, meaning, or execution of a query sent to a NoSQL database.

NoSQL databases include technologies such as:

```text
MongoDB
CouchDB
Couchbase
Redis
Amazon DynamoDB
Elasticsearch
Firebase / Firestore
Neo4j
```

The exact injection techniques depend heavily on:

```text
Database
Query language
Driver
Framework
Input format
Application logic
```

MongoDB-style document databases are particularly important during web application testing because application requests frequently contain JSON objects that map closely to database queries.

A simplified data flow is:

```text
User Input
    ↓
Application
    ↓
NoSQL Query Construction
    ↓
Database
    ↓
Result
```

Secure behaviour:

```text
User Input
    ↓
Treated as Data
    ↓
Database Query
```

Vulnerable behaviour:

```text
User Input
    ↓
Interpreted as Query Structure / Operator
    ↓
Modified Database Query
```

Potential impact includes:

```text
Authentication bypass
Authorisation bypass
Sensitive data disclosure
User enumeration
Database record extraction
Query manipulation
Business logic bypass
Modification of database records
Deletion of data
Denial of service
```

!!! warning "Authorised Security Testing"
    NoSQL injection testing should only be performed against systems included in the authorised assessment scope. Begin with harmless query manipulation and controlled test accounts. Avoid destructive database operators, high-volume extraction, expensive regular expressions, or operations that modify or delete production data unless explicitly authorised.

---

# SQL Injection vs NoSQL Injection

Traditional SQL injection targets SQL statements.

For example:

```text
SELECT *
FROM users
WHERE username = 'USER_INPUT'
```

NoSQL databases may instead use structured queries.

Conceptually:

```javascript
db.users.find({
    username: USER_INPUT
})
```

The fundamental problem remains similar:

```text
Application expects:

DATA

Attacker supplies:

QUERY LOGIC
```

However, the syntax and exploitation techniques can be very different.

---

# NoSQL Does Not Mean Injection-Safe

A common misconception is:

```text
No SQL
  ↓
No SQL Injection
  ↓
No Injection
```

This is incorrect.

The more accurate model is:

```text
No SQL
  ↓
Different Query Language / API
  ↓
Different Injection Techniques
```

Applications still need to safely separate:

```text
User-controlled data
```

from:

```text
Database query structure
```

---

# NoSQL Injection Categories

NoSQL injection can broadly involve:

```text
Syntax Injection
Operator Injection
Type Confusion
Query Selector Injection
JavaScript Injection
Filter Manipulation
Search Query Injection
```

The exact terminology varies depending on the database.

For MongoDB-style applications, two especially important categories are:

```text
Syntax Injection
Operator Injection
```

---

# MongoDB Query Model

Consider a MongoDB query:

```javascript
db.users.findOne({
    username: "alice",
    password: "password123"
})
```

Conceptually:

```text
username must equal alice
AND
password must equal password123
```

An application might construct this query from HTTP parameters:

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "username": "alice",
  "password": "password123"
}
```

The application then performs something conceptually similar to:

```javascript
users.findOne({
    username: req.body.username,
    password: req.body.password
})
```

If the application accepts arbitrary objects rather than expected scalar strings, the query structure may potentially be manipulated.

---

# Operator Injection

MongoDB supports query operators beginning with:

```text
$
```

Examples include:

```text
$ne
$eq
$gt
$gte
$lt
$lte
$in
$nin
$regex
$exists
$or
$and
$not
$where
```

These operators are legitimate database functionality.

The security problem occurs when:

```text
Untrusted Input
      ↓
Becomes Database Operator
```

instead of remaining a literal value.

---

# Basic Operator Example

The application expects:

```json
{
  "username": "alice"
}
```

but receives:

```json
{
  "username": {
    "$ne": ""
  }
}
```

Conceptually, the query changes from:

```text
username = "alice"
```

to something similar to:

```text
username != ""
```

Whether this causes a vulnerability depends entirely on:

```text
Application query
Database
Driver
Authentication logic
Result handling
```

A changed response is evidence for further investigation, not automatically proof of authentication bypass.

---

# Authentication Example

Consider vulnerable logic conceptually equivalent to:

```javascript
users.findOne({
    username: req.body.username,
    password: req.body.password
})
```

Normal input:

```json
{
  "username": "alice",
  "password": "CorrectPassword"
}
```

might produce:

```javascript
{
    username: "alice",
    password: "CorrectPassword"
}
```

If arbitrary objects are accepted:

```json
{
  "username": {
    "$ne": ""
  },
  "password": {
    "$ne": ""
  }
}
```

could conceptually become:

```javascript
{
    username: {
        $ne: ""
    },
    password: {
        $ne: ""
    }
}
```

which means:

```text
username is not empty
AND
password is not empty
```

If the application treats the first matching record as authenticated, this can create a serious authentication flaw.

---

# Do Not Assume `$ne` Always Works

Whether an operator injection works depends on implementation details.

Applications may:

```text
Convert values to strings
Validate JSON schemas
Strip dollar-prefixed keys
Use ODM validation
Reject nested objects
Use safe query builders
Sanitise query selectors
```

Therefore the testing process should be:

```text
Baseline
   ↓
Controlled Mutation
   ↓
Observe Difference
   ↓
Understand Query Behaviour
   ↓
Confirm Security Impact
```

---

# URL-Encoded Operator Injection

Some applications receive form data rather than JSON.

Normal request:

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=alice&password=password123
```

Depending on the application's parameter parser, nested parameter syntax may produce objects.

For example:

```text
username[$ne]=invalid
```

or:

```text
password[$ne]=invalid
```

may potentially be interpreted as:

```javascript
username: {
    $ne: "invalid"
}
```

The exact behaviour depends on:

```text
Language
Framework
Parameter parser
Middleware
Database driver
```

---

# JSON Operator Injection

JSON APIs often make operator testing easier because nested structures can be represented directly.

Normal:

```json
{
  "username": "alice"
}
```

Test:

```json
{
  "username": {
    "$ne": "alice"
  }
}
```

Another harmless structural probe:

```json
{
  "username": {
    "$exists": true
  }
}
```

Observe whether the response differs from:

```json
{
  "username": "definitely-not-a-real-user"
}
```

---

# Testing Methodology

A structured methodology is:

```text
Identify Input
      ↓
Determine Input Format
      ↓
Establish Baseline
      ↓
Identify Possible NoSQL Backend
      ↓
Test Syntax Handling
      ↓
Test Type Handling
      ↓
Test Operator Injection
      ↓
Compare Responses
      ↓
Identify Query Behaviour
      ↓
Test Authentication / Authorisation
      ↓
Test Blind Conditions
      ↓
Determine Impact
      ↓
Report
```

---

# Step 1: Identify Candidate Inputs

Prioritise parameters used for:

```text
Authentication
Search
Filtering
User lookup
Product lookup
Account recovery
API queries
Reporting
Sorting
Pagination
Administrative search
```

Example parameters:

```text
username
email
password
user
id
search
query
filter
category
role
status
token
```

---

# Step 2: Establish a Baseline

Before injecting anything, understand normal behaviour.

For example:

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "username": "invalid-user",
  "password": "invalid-password"
}
```

Record:

```text
Status code
Response length
Response body
Headers
Response time
Redirect
Cookie changes
Application state
```

---

# Step 3: Determine Input Type

Ask:

```text
Does the application expect:

String?
Number?
Boolean?
Array?
Object?
Null?
```

Example:

```json
{
  "username": "alice"
}
```

Try controlled type changes:

```json
{
  "username": 123
}
```

```json
{
  "username": true
}
```

```json
{
  "username": null
}
```

```json
{
  "username": []
}
```

```json
{
  "username": {}
}
```

Unexpected differences can reveal weak type validation.

---

# Type Confusion

Suppose the application expects:

```text
String
```

but accepts:

```text
Object
```

Flow:

```text
Expected:
username = String

Received:
username = Object

Application
    ↓
Passes Object Directly to Database
    ↓
Object Becomes Query Structure
```

This is one of the core patterns behind NoSQL operator injection.

---

# Step 4: Test Query Operators

For MongoDB-like backends, carefully test whether structured operators are accepted.

Examples:

```json
{
  "username": {
    "$ne": "definitely-not-this-value"
  }
}
```

```json
{
  "username": {
    "$exists": true
  }
}
```

```json
{
  "username": {
    "$regex": "^a"
  }
}
```

Observe:

```text
Response status
Response body
Result count
Authentication behaviour
Response timing
Error messages
```

---

# `$ne`

`$ne` means:

```text
Not Equal
```

Example:

```javascript
{
    username: {
        $ne: "alice"
    }
}
```

Conceptually:

```text
Return documents where username != alice
```

During testing, `$ne` is useful for understanding whether user input can alter comparison semantics.

---

# `$eq`

`$eq` means:

```text
Equal
```

Example:

```json
{
  "username": {
    "$eq": "alice"
  }
}
```

If the application normally expects:

```json
{
  "username": "alice"
}
```

comparing these behaviours can help determine whether query operators are interpreted.

---

# `$exists`

`$exists` tests whether a field exists.

Example:

```json
{
  "username": {
    "$exists": true
  }
}
```

Conceptually:

```text
username field exists
```

This can be useful as a controlled query-structure probe.

---

# `$regex`

MongoDB supports regular-expression queries.

Example:

```json
{
  "username": {
    "$regex": "^a"
  }
}
```

Conceptually:

```text
username begins with "a"
```

Regular expressions can be useful for determining whether attacker-controlled query operators are being interpreted.

---

# Safe Regex Testing

Start with simple expressions:

```text
^a
^test
^$
```

Avoid deliberately expensive regular expressions.

Certain patterns can consume excessive CPU and potentially cause:

```text
Regular Expression Denial of Service
```

The objective during normal testing is to determine:

```text
Is the regex operator interpreted?
```

not to exhaust database resources.

---

# `$in`

`$in` matches values contained in an array.

Example:

```json
{
  "role": {
    "$in": [
      "user",
      "admin"
    ]
  }
}
```

During testing, this can help determine whether an input is being passed directly into a MongoDB selector.

---

# `$nin`

`$nin` performs the inverse:

```text
Not In
```

Example:

```json
{
  "status": {
    "$nin": [
      "disabled"
    ]
  }
}
```

Again, the important security question is:

> Can a user replace an expected scalar value with database query logic?

---

# Comparison Operators

MongoDB comparison operators include:

```text
$gt
$gte
$lt
$lte
```

For numeric inputs, these may be relevant.

For example:

```json
{
  "price": {
    "$gt": 0
  }
}
```

If the application expects:

```json
{
  "price": 100
}
```

accepting an object containing a database operator may indicate unsafe query construction.

---

# Logical Operators

MongoDB also supports:

```text
$or
$and
$nor
$not
```

These can significantly change query logic if attacker-controlled objects are merged into database selectors.

Example conceptual query:

```javascript
{
    $or: [
        { username: "alice" },
        { username: "bob" }
    ]
}
```

Applications should not allow users to introduce arbitrary query operators unless this functionality is explicitly intended and securely constrained.

---

# Authentication Testing

Authentication endpoints are high-value NoSQL injection targets.

Workflow:

```text
Normal Invalid Login
       ↓
Record Response
       ↓
Modify Username Type
       ↓
Modify Password Type
       ↓
Test Controlled Operators
       ↓
Compare Behaviour
       ↓
Authenticated?
       ↓
Validate With Controlled Accounts
```

---

# Authentication Testing Matrix

| Username | Password | Purpose |
|---|---|---|
| Invalid string | Invalid string | Baseline |
| Valid controlled username | Invalid password | Known-user baseline |
| Object/operator | Invalid password | Username query test |
| Valid controlled username | Object/operator | Password query test |
| Object/operator | Object/operator | Combined query behaviour |

Do not test against accounts outside the assessment scope.

---

# Authentication Bypass Impact

A strong authentication finding requires more than:

```text
Different response
```

Demonstrate that the manipulated query actually results in:

```text
Authenticated session
```

or another concrete security boundary being bypassed.

Evidence may include:

```text
Session cookie
Authenticated dashboard
Current-user API
Account identifier
Protected endpoint access
```

---

# User Enumeration

NoSQL injection can sometimes reveal whether a user exists.

For example, compare:

```text
username starts with A
```

against:

```text
username starts with Z
```

If responses differ consistently, the application may expose information about stored records.

Possible differences include:

```text
Status code
Response length
Error message
Response time
Redirect
JSON field
```

---

# Blind NoSQL Injection

A NoSQL injection is blind when:

```text
Query behaviour changes
```

but:

```text
Database result is not directly displayed
```

Instead, information may be inferred from:

```text
True / false responses
Different status codes
Different page content
Different JSON responses
Different redirects
Timing differences
```

---

# Boolean-Based Blind Testing

Suppose a condition can be controlled.

Conceptually:

```text
Condition TRUE
      ↓
Response A

Condition FALSE
      ↓
Response B
```

For example, a regular expression may be used to test a controlled account value:

```text
Does username start with "a"?
```

Then:

```text
Does username start with "b"?
```

If only one produces the expected response, information about the underlying value may be inferred.

---

# Controlled Blind Extraction

During authorised testing, use a test account or test record where possible.

For example, if the controlled username is:

```text
alice-test
```

a test such as:

```text
^a
```

should behave differently from:

```text
^z
```

if regular-expression operators are being evaluated.

This can prove the issue without extracting another user's information.

---

# Character-by-Character Extraction

In some vulnerable applications, boolean query conditions can theoretically reveal a value character by character.

Conceptually:

```text
Starts with a?
      ↓
NO

Starts with b?
      ↓
NO

Starts with c?
      ↓
YES

Then:

Starts with ca?
Starts with cb?
Starts with cc?
...
```

This can reconstruct hidden values.

For normal production assessments, it is usually unnecessary to extract complete sensitive values.

A minimal proof using controlled data is preferable.

---

# Regex-Based Extraction Model

Conceptually:

```text
Unknown Value
     ↓
Regex ^a
     ↓
TRUE / FALSE
     ↓
Regex ^ab
     ↓
TRUE / FALSE
     ↓
Continue
```

This demonstrates why seemingly simple operator injection can become a confidentiality issue.

---

# Password Extraction

If an application exposes password hashes or secrets indirectly through vulnerable query conditions, blind extraction may theoretically be possible.

Do not extract real user passwords or sensitive secrets merely to prove the vulnerability.

Prefer:

```text
Controlled test account
Known test value
Minimal prefix proof
```

and document the potential impact.

---

# Syntax Injection

Some NoSQL applications construct query expressions by concatenating strings.

Conceptually:

```javascript
query = 'this.username == "' + userInput + '"'
```

User input can potentially break out of the intended string context.

This is analogous to traditional injection:

```text
Expected Data
     ↓
Break Out
     ↓
Modify Expression
```

---

# Syntax Testing

The exact syntax depends on the backend.

Useful initial probes may include characters such as:

```text
'
"
\
{
}
[
]
$
```

The purpose is initially to observe:

```text
Syntax errors
Parsing changes
Database errors
Application exceptions
```

not to immediately construct a complex exploit.

---

# Error-Based Detection

Error messages can reveal the backend.

Look for terms such as:

```text
MongoError
MongoServerError
MongoDB
BSON
ObjectId
mongoose
CastError
Document
Query
CouchDB
Redis
Elasticsearch
```

Example:

```text
Cast to ObjectId failed
```

may indicate:

```text
MongoDB / Mongoose
```

or related tooling.

---

# ObjectId

MongoDB frequently uses identifiers such as:

```text
507f1f77bcf86cd799439011
```

These are commonly represented as:

```text
ObjectId
```

Finding ObjectId-shaped identifiers can be another clue that MongoDB or a compatible document model may be involved.

However:

```text
ObjectId-shaped ID
```

does not by itself prove a vulnerability.

---

# Mongoose

Node.js applications frequently use:

```text
Mongoose
```

as an object data modelling library for MongoDB.

Potential error messages include:

```text
CastError
ValidationError
StrictModeError
DocumentNotFoundError
```

When these appear, investigate:

```text
Type handling
Object parsing
Query operators
Input validation
```

---

# JavaScript-Based Query Execution

Historically, some MongoDB query functionality can execute JavaScript expressions.

One important operator is:

```text
$where
```

Conceptually:

```javascript
{
    $where: "JavaScript expression"
}
```

If attacker-controlled input reaches such functionality, the impact can be more serious than ordinary selector manipulation.

Modern applications should avoid evaluating attacker-controlled JavaScript in database queries.

---

# `$where`

`$where` allows JavaScript expressions in MongoDB query evaluation in environments where the functionality is enabled and supported.

Conceptually:

```javascript
db.users.find({
    $where: "this.username == 'alice'"
})
```

Applications should never construct `$where` expressions using untrusted input.

---

# Safe `$where` Testing

If there is evidence that the application uses `$where`, begin with harmless conditions such as:

```text
Always true
```

versus:

```text
Always false
```

The objective is to determine whether input influences JavaScript query evaluation.

Avoid:

```text
Long-running loops
CPU-intensive expressions
Resource exhaustion
```

---

# Server-Side JavaScript

Server-side JavaScript functionality has historically appeared in MongoDB-related features such as:

```text
$where
mapReduce
```

Support and defaults vary by database version and deployment.

Do not assume server-side JavaScript is available.

First determine:

```text
Database
Version where possible
Application behaviour
Actual query construction
```

---

# NoSQL Injection Through Query Parameters

Example:

```http
GET /api/users?username=alice HTTP/1.1
Host: target.example
```

Depending on parameter parsing, test whether structured input can be introduced.

Examples might include:

```text
username[$ne]=invalid
```

or:

```text
username[$regex]=^a
```

Whether this becomes a database operator depends entirely on the server-side parser.

---

# NoSQL Injection Through JSON

Example:

```http
POST /api/users/search HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "username": "alice"
}
```

Try controlled type mutation:

```json
{
  "username": {
    "$regex": "^a"
  }
}
```

Compare the response.

---

# NoSQL Injection Through GraphQL

GraphQL APIs can also expose NoSQL injection if resolvers pass arguments unsafely into a document database.

Example:

```graphql
query {
    user(username: "alice") {
        id
        username
    }
}
```

Conceptually:

```text
GraphQL Argument
      ↓
Resolver
      ↓
MongoDB Query
```

GraphQL schema validation may reduce some type confusion, but resolver logic must still be secure.

Refer to:

[GraphQL API Security](graphql.md)

---

# Nested GraphQL Inputs

GraphQL input objects may be particularly interesting.

Conceptually:

```graphql
input UserFilter {
    username: String
    status: String
}
```

If the resolver directly transforms user-controlled filter objects into database queries:

```text
GraphQL Filter
      ↓
Database Filter
```

ensure that users cannot introduce unexpected query semantics.

---

# NoSQL Injection Through APIs

JSON APIs deserve particular attention because JSON naturally supports:

```text
Strings
Numbers
Booleans
Arrays
Objects
Null
```

This means a client can often change:

```json
{
  "username": "alice"
}
```

into:

```json
{
  "username": {}
}
```

unless strict server-side validation prevents it.

Refer to:

[API Security](api-security.md)

---

# Array Injection

If an application expects:

```json
{
  "role": "user"
}
```

test whether it accepts:

```json
{
  "role": [
    "user",
    "admin"
  ]
}
```

Unexpected array handling can reveal:

```text
Type confusion
Query construction flaws
Business logic errors
```

---

# Object Injection

Expected:

```json
{
  "status": "active"
}
```

Test:

```json
{
  "status": {}
}
```

Then, where appropriate:

```json
{
  "status": {
    "$ne": "disabled"
  }
}
```

If an object is accepted where a string should be required, investigate further.

---

# Null Handling

Test:

```json
{
  "username": null
}
```

Questions include:

```text
Does null remove a filter?
Does null match unexpected records?
Does the application crash?
Does validation disappear?
```

Null-related behaviour can reveal both injection and general input-validation issues.

---

# Boolean Handling

Test:

```json
{
  "username": true
}
```

and:

```json
{
  "username": false
}
```

Again, the goal is to determine whether:

```text
Strict Type Validation
```

exists.

---

# Numeric Handling

If an identifier is expected to be a string:

```json
{
  "id": "123"
}
```

compare:

```json
{
  "id": 123
}
```

Type coercion can occasionally cause unexpected query behaviour.

---

# Search Functionality

Search endpoints are common NoSQL injection targets.

Example:

```http
POST /api/search HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "search": "laptop"
}
```

The backend might use:

```text
Regex
Full-text search
MongoDB filters
Elasticsearch queries
```

Determine the underlying search technology before assuming MongoDB-specific behaviour.

---

# Filter Functionality

Modern APIs frequently accept filter objects:

```json
{
  "filter": {
    "status": "active",
    "category": "user"
  }
}
```

The critical question is:

> Does the application translate a user-controlled filter directly into the database query?

Dangerous pattern:

```text
User JSON
    ↓
Database Query Object
```

without:

```text
Allowed field validation
Allowed operator validation
Type validation
```

---

# Sorting

Sorting parameters may also reach database APIs.

Example:

```json
{
  "sort": "username"
}
```

Test unexpected types carefully:

```json
{
  "sort": {
    "username": 1
  }
}
```

Whether this represents a vulnerability depends on what the API intentionally supports.

---

# Projection

Some document databases support selecting which fields should be returned.

Conceptually:

```javascript
find(query, projection)
```

If users can control projections, they may potentially request fields the frontend normally hides.

This is primarily an:

```text
Authorisation / Excessive Data Exposure
```

issue rather than automatically NoSQL injection.

Still, it should be considered during NoSQL API testing.

---

# NoSQL Injection and IDOR

Suppose an endpoint normally retrieves:

```text
userId = current user's ID
```

but accepts a flexible query object.

An attacker may potentially broaden:

```text
One object
```

into:

```text
Multiple objects
```

or change the selected object.

This can combine:

```text
NoSQL Injection
       +
Broken Object-Level Authorisation
```

Refer to:

[Authorisation Testing](authorisation.md)

---

# NoSQL Injection and Business Logic

Consider:

```json
{
  "coupon": "WELCOME10"
}
```

If the backend performs a document lookup and accepts query operators, the attacker might alter which coupon record is selected.

The resulting vulnerability may involve:

```text
NoSQL Injection
       ↓
Unexpected Record Selection
       ↓
Business Logic Abuse
```

Refer to:

[Business Logic Vulnerabilities](business-logic.md)

---

# NoSQL Injection and Authentication

Authentication is one of the highest-value areas.

Test:

```text
Login
Password reset
Account recovery
MFA lookup
Magic links
API key lookup
Session lookup
```

The security question is:

> Can query manipulation cause the application to select a different authentication record or accept a condition that should fail?

---

# NoSQL Injection and Password Reset

Consider:

```text
POST /forgot-password
```

with:

```json
{
  "email": "alice@example.com"
}
```

If the email field accepts a database selector, query manipulation may potentially:

```text
Select unintended users
Change account lookup behaviour
Affect enumeration
```

Use controlled accounts when testing.

---

# NoSQL Injection and Authorisation

Suppose an administrative search API accepts:

```json
{
  "role": "user"
}
```

If the role value can be replaced with a query object, the user may potentially retrieve records outside the intended filter.

However, this only becomes a meaningful security issue if the returned records are not independently authorised.

---

# NoSQL Injection and Information Disclosure

Verbose database errors may reveal:

```text
Database type
Collection names
Field names
Query syntax
Driver
Framework
Stack traces
Internal code
```

Refer to:

[Information Disclosure](information-disclosure.md)

---

# NoSQL Injection and Prototype Pollution

JavaScript applications frequently process nested JSON objects before they reach MongoDB.

Therefore a request involving objects may expose separate risks such as:

```text
Prototype Pollution
```

Do not confuse:

```text
NoSQL Operator Injection
```

with:

```text
Prototype Pollution
```

They are different vulnerability classes.

Refer to:

[Prototype Pollution](prototype-pollution.md)

---

# Burp Suite

Burp Suite is one of the most useful tools for manual NoSQL injection testing.

Useful components include:

```text
Proxy
Repeater
Intruder
Comparer
Scanner
Logger
```

---

# Burp Proxy Workflow

Browse the application normally:

```text
Browser
   ↓
Burp Proxy
   ↓
HTTP History
```

Look for:

```text
JSON requests
Search APIs
Login requests
Filters
GraphQL
User lookups
Administrative searches
```

Send interesting requests to:

```text
Repeater
```

---

# Burp Repeater

Repeater should normally be the primary tool.

Start with:

```text
Original Request
```

then change one thing at a time.

For example:

```json
{
  "username": "invalid"
}
```

then:

```json
{
  "username": null
}
```

then:

```json
{
  "username": {}
}
```

then, where appropriate:

```json
{
  "username": {
    "$ne": "invalid"
  }
}
```

This helps identify exactly which change affects behaviour.

---

# Response Comparison

Record:

```text
Status
Length
Words
JSON fields
Redirect
Cookies
Timing
Application state
```

For example:

```text
Baseline:
401
Length 84

Object:
400
Length 221

$ne:
200
Length 437
```

This strongly suggests the operator request deserves further investigation.

---

# Burp Comparer

Comparer is useful when responses are large.

Compare:

```text
Normal Response
      vs
Operator Response
```

or:

```text
TRUE Condition
      vs
FALSE Condition
```

Look for small changes in:

```text
JSON
Error messages
Object count
Identifiers
Response structure
```

---

# Burp Intruder

Intruder can help with controlled testing of:

```text
Operators
Values
Types
Regex prefixes
Object IDs
Search filters
```

For example, mark:

```json
{
  "username": {
    "$regex": "^§a§"
  }
}
```

and use a small controlled payload set.

---

# Intruder Operator Testing

A small payload list might contain:

```text
$eq
$ne
$regex
$exists
$gt
$gte
$lt
$lte
$in
$nin
```

However, inserting only the operator name may not create syntactically valid JSON.

In many cases it is better to mark the complete value or send complete request variants.

---

# Intruder Type Testing

Useful request variants include:

```text
String
Number
Boolean
Null
Array
Object
Operator Object
```

For example:

```json
"alice"
```

```json
123
```

```json
true
```

```json
null
```

```json
[]
```

```json
{}
```

```json
{"$ne":"invalid"}
```

---

# Burp Match and Grep

Useful response indicators include:

```text
Welcome
Invalid credentials
User not found
MongoError
MongoServerError
CastError
ObjectId
mongoose
Unauthorized
Forbidden
```

Configure response matching carefully when testing many variations.

---

# Burp Scanner

Burp Scanner may identify certain server-side injection behaviours and input-validation issues.

However:

```text
No Scanner Finding
```

does not mean:

```text
No NoSQL Injection
```

Manual testing remains important because the vulnerability often depends on:

```text
Application-specific JSON structure
Query logic
Authentication logic
Business rules
```

---

# Content-Type Manipulation

Suppose the application normally receives:

```text
application/x-www-form-urlencoded
```

Try determining whether it also accepts:

```text
application/json
```

or vice versa.

Different parsers may produce different server-side object structures.

For example:

```text
Form Parser
     ↓
String

JSON Parser
     ↓
Object
```

This can materially change the attack surface.

---

# Duplicate Parameters

Different frameworks handle duplicate parameters differently.

Example:

```text
username=alice&username=bob
```

Possible interpretations include:

```text
First value
Last value
Array
Error
```

Although this is not inherently NoSQL injection, parser differences can become relevant when input is later transformed into database queries.

---

# Parameter Pollution

Nested parameters may also interact with parser behaviour.

Example:

```text
username=alice
username[$ne]=bob
```

Different layers may interpret this differently:

```text
Reverse Proxy
Framework
Validation Middleware
Application
Database Layer
```

Parser inconsistencies deserve investigation when behaviour changes.

---

# Identifying MongoDB

Potential indicators include:

```text
MongoDB
MongoError
MongoServerError
ObjectId
BSON
mongoose
mongodb://
mongodb+srv://
```

Technology identification may also reveal:

```text
Node.js
Express
Mongoose
MongoDB
```

Refer to:

[Technology Identification](reconnaissance/technology-identification.md)

---

# JavaScript Analysis

Frontend JavaScript can reveal:

```text
API endpoints
Filter structures
Expected object shapes
GraphQL queries
Search parameters
Hidden fields
MongoDB-style identifiers
```

Search JavaScript for terms such as:

```text
filter
query
search
where
regex
mongo
ObjectId
graphql
```

Refer to:

[JavaScript Analysis](reconnaissance/javascript-analysis.md)

---

# Source Code Review

If source code is available, search for database calls such as:

```text
find
findOne
findById
findOneAndUpdate
updateOne
updateMany
deleteOne
deleteMany
aggregate
match
where
```

For Mongoose:

```javascript
User.findOne(...)
```

```javascript
User.find(...)
```

```javascript
User.findById(...)
```

The key question is:

> Does untrusted input reach the query selector without strict validation?

---

# Dangerous Source Pattern

Conceptually dangerous:

```javascript
User.findOne(req.body)
```

because:

```text
Entire User-Controlled Object
          ↓
Database Query
```

This may allow unexpected fields or operators to influence the query.

---

# Safer Pattern

Prefer explicit extraction:

```javascript
const username = req.body.username;
```

followed by:

```text
Validate type
Validate format
Construct expected query explicitly
```

Conceptually:

```javascript
User.findOne({
    username: validatedUsername
})
```

---

# Mass Assignment vs NoSQL Injection

Consider:

```javascript
User.updateOne(
    { _id: userId },
    req.body
)
```

This may expose:

```text
Mass assignment
```

because users might modify unexpected fields.

Meanwhile:

```javascript
User.findOne(req.body)
```

may expose:

```text
NoSQL query injection
```

The same root problem may be:

```text
Passing untrusted structured objects directly into database APIs
```

but the security consequences differ.

---

# Aggregation Pipelines

MongoDB supports aggregation pipelines.

Conceptually:

```text
Input
 ↓
$match
 ↓
$lookup
 ↓
$project
 ↓
$sort
 ↓
Result
```

If users can directly influence pipeline stages or operators, the attack surface can be significantly broader.

Do not expose arbitrary aggregation pipeline structures to untrusted clients.

---

# `$match`

A secure application may construct:

```javascript
{
    $match: {
        username: validatedUsername
    }
}
```

A dangerous design may accept an arbitrary user-controlled:

```json
{
  "$match": {
    ...
  }
}
```

unless arbitrary query construction is intentionally part of the API and protected accordingly.

---

# `$lookup`

`$lookup` can join documents from another collection.

If arbitrary aggregation stages are exposed to untrusted users, this may potentially allow access to data that the application did not intend to expose.

This should be treated as a serious API design and authorisation issue.

---

# Elasticsearch

Elasticsearch is also a NoSQL-style data store/search engine.

Applications may accept search parameters that eventually become:

```text
Query DSL
```

Conceptually:

```text
User Search
     ↓
Application
     ↓
Elasticsearch Query DSL
```

If arbitrary query DSL objects are accepted, users may be able to change query semantics.

Do not assume MongoDB operators apply to Elasticsearch.

---

# Redis

Redis uses a very different command model.

Potential injection issues can occur when applications construct Redis commands unsafely from user input.

Conceptually:

```text
User Input
    ↓
Redis Command Construction
    ↓
Redis
```

Testing methodology must match the actual database and protocol.

MongoDB-specific `$ne` or `$regex` techniques are not universal NoSQL payloads.

---

# CouchDB

CouchDB uses HTTP and JSON-based query mechanisms.

Potential security issues can involve:

```text
Query selectors
Views
Mango queries
Authentication
Database exposure
```

Again, use backend-specific methodology rather than blindly applying MongoDB operators.

---

# Firebase / Firestore

Firebase and Firestore security is heavily dependent on:

```text
Security rules
Authentication
Document paths
Query restrictions
```

Many Firestore vulnerabilities are more accurately classified as:

```text
Broken access control
```

rather than NoSQL injection.

Do not force every NoSQL-backed vulnerability into the NoSQL injection category.

---

# NoSQLMap

NoSQLMap is an open-source tool designed to assist with NoSQL injection testing.

Project:

```text
https://github.com/codingo/NoSQLMap
```

It has historically focused particularly on:

```text
MongoDB
NoSQL injection testing
Enumeration
Web application testing
```

---

# Using NoSQLMap

Use automated tooling only after understanding the target request manually.

Recommended workflow:

```text
Burp Proxy
    ↓
Identify Candidate
    ↓
Burp Repeater
    ↓
Confirm Suspicious Behaviour
    ↓
NoSQLMap
    ↓
Controlled Automation
    ↓
Manual Validation
```

Do not start with aggressive automated testing against every parameter.

---

# Automated Tooling

Automated tools can assist with:

```text
Payload generation
Operator testing
Response comparison
Blind conditions
Enumeration
```

But they may produce:

```text
False positives
Unexpected traffic
Expensive queries
Large request volumes
```

Always validate manually.

---

# Safe Testing Strategy

Prefer this progression:

```text
1. Invalid string
2. Type change
3. Empty object
4. Simple operator
5. TRUE / FALSE comparison
6. Controlled account proof
7. Minimal impact validation
```

Avoid jumping directly to:

```text
Large extraction
Destructive updates
Expensive regex
Database modification
```

---

# Testing Matrix

| Test | Example | What It Tests |
|---|---|---|
| Baseline | `"alice"` | Normal behaviour |
| Invalid | `"does-not-exist"` | Negative baseline |
| Null | `null` | Null handling |
| Boolean | `true` | Type validation |
| Number | `123` | Type validation |
| Array | `[]` | Type validation |
| Object | `{}` | Object acceptance |
| `$eq` | `{"$eq":"alice"}` | Operator interpretation |
| `$ne` | `{"$ne":"invalid"}` | Query manipulation |
| `$exists` | `{"$exists":true}` | Field existence selector |
| `$regex` | `{"$regex":"^a"}` | Regex selector |

Use only operators appropriate to the suspected backend.

---

# Response Analysis Matrix

| Behaviour | Possible Meaning |
|---|---|
| Same as baseline | Input may be treated literally |
| Validation error | Type/schema validation present |
| Database error | Input reached query/database layer |
| More records | Query semantics may have changed |
| Different user | Serious query manipulation |
| Authenticated session | Potential authentication bypass |
| Timing change | Query evaluation may differ |
| Server error | Investigate safely |

A difference is:

```text
A clue
```

not automatically:

```text
A vulnerability
```

---

# Decision Tree

```text
USER-CONTROLLED INPUT
        ↓
DATABASE-RELATED FUNCTION?
        ↓
       YES
        ↓
DETERMINE EXPECTED TYPE
        ↓
CHANGE INPUT TYPE
        ↓
OBJECT ACCEPTED?
    ↓          ↓
   NO         YES
    ↓          ↓
OTHER       TEST SIMPLE
TESTS       OPERATORS
               ↓
       BEHAVIOUR CHANGES?
          ↓          ↓
         NO         YES
          ↓          ↓
       OTHER      TRUE/FALSE
       INPUTS       TEST
                      ↓
               CONSISTENT?
                 ↓      ↓
                NO     YES
                 ↓      ↓
             REASSESS  SECURITY
                       IMPACT?
                          ↓
                         YES
                          ↓
                  CONTROLLED PROOF
                          ↓
                       REPORT
```

---

# Quick Reference

```text
NoSQL Injection
      ↓
Identify Database-Like Input
      ↓
Baseline
      ↓
Type Mutation
      ↓
String → Object?
      ↓
Operator Injection
      ↓
$eq
$ne
$exists
$regex
      ↓
Response Difference
      ↓
TRUE / FALSE Test
      ↓
Authentication?
Authorisation?
Data Exposure?
Business Logic?
      ↓
Minimal Controlled Proof
      ↓
Report
```

---

# Pentesting Checklist

## Discovery

```text
[ ] Identify JSON endpoints
[ ] Identify authentication endpoints
[ ] Identify search endpoints
[ ] Identify filtering endpoints
[ ] Identify GraphQL endpoints
[ ] Inspect JavaScript
[ ] Inspect error messages
[ ] Identify backend technology
[ ] Look for MongoDB / Mongoose indicators
```

## Input Types

```text
[ ] String
[ ] Number
[ ] Boolean
[ ] Null
[ ] Array
[ ] Object
[ ] Nested object
```

## MongoDB Operators

```text
[ ] $eq
[ ] $ne
[ ] $exists
[ ] $regex
[ ] $gt
[ ] $gte
[ ] $lt
[ ] $lte
[ ] $in
[ ] $nin
```

Only test operators relevant to the identified backend and endpoint.

## Authentication

```text
[ ] Invalid username baseline
[ ] Valid controlled username baseline
[ ] Username object
[ ] Password object
[ ] Username operator
[ ] Password operator
[ ] Combined operator behaviour
[ ] Verify actual authenticated state
```

## Blind Testing

```text
[ ] TRUE condition
[ ] FALSE condition
[ ] Response difference
[ ] Status difference
[ ] Length difference
[ ] Timing difference
[ ] Controlled regex prefix
```

## APIs

```text
[ ] JSON body
[ ] Query parameters
[ ] Form parameters
[ ] Nested objects
[ ] Filter objects
[ ] GraphQL inputs
[ ] Sorting
[ ] Pagination
```

## Impact

```text
[ ] Authentication bypass
[ ] Authorisation bypass
[ ] Data disclosure
[ ] Record selection manipulation
[ ] User enumeration
[ ] Business logic bypass
[ ] Database modification
```

## Burp

```text
[ ] Proxy
[ ] Repeater
[ ] Intruder
[ ] Comparer
[ ] Scanner
[ ] Logger
```

---

# Evidence Collection

For a confirmed finding, record:

```text
Affected endpoint
HTTP method
Parameter
Expected parameter type
Original request
Modified request
Original response
Modified response
Authentication state
User role
Database indicators
Operator used
Security impact
Controlled account used
Reproduction steps
```

---

# Strong Evidence

Strong evidence might show:

```text
Normal Invalid Credentials
        ↓
Authentication Fails

Operator Input
        ↓
Authentication Succeeds
```

or:

```text
Normal Filter
     ↓
1 Authorised Record

Operator Filter
     ↓
Records Outside Intended Filter
```

provided those records are not independently authorised.

---

# Weak Evidence

Examples of weak evidence include:

```text
MongoDB detected

ObjectId present

$ne causes 500 error

Mongoose error displayed
```

These may indicate useful attack-surface information but do not automatically prove exploitable NoSQL injection.

---

# Example Finding: Authentication Bypass

```text
Finding:
NoSQL Operator Injection Allows Authentication Bypass

Affected Endpoint:
POST /login

Observed:
The login endpoint expected the username and password properties to contain string values.

However, the application also accepted JSON objects containing MongoDB query operators.

By replacing the expected scalar values with controlled query objects, the underlying database query semantics could be modified and the application returned an authenticated session without validating the intended username and password combination.

Impact:
An unauthenticated attacker may be able to bypass the application's authentication mechanism and obtain access to an account without knowing the account password.

Recommendation:
Enforce strict server-side types for authentication parameters, reject objects and database operators in user-controlled values, and construct database queries using explicitly validated scalar values.
```

---

# Example Finding: Query Manipulation

```text
Finding:
NoSQL Operator Injection Allows Manipulation of User Search Queries

Affected Endpoint:
POST /api/users/search

Observed:
The username property was expected to contain a string.

The endpoint also accepted an object containing a MongoDB query operator.

This caused the database query to return records that would not be returned when using the intended string value.

Impact:
An authenticated user may manipulate the application's database query and retrieve information outside the intended search criteria.

Recommendation:
Validate the expected type and format of all search parameters and construct an explicit allowlisted database query rather than passing user-controlled objects directly to the database layer.
```

---

# Example Finding: Blind NoSQL Injection

```text
Finding:
Blind NoSQL Injection Allows Inference of Stored Account Data

Affected Endpoint:
POST /api/account/check

Observed:
The endpoint accepted MongoDB regular-expression operators within a parameter that was expected to contain a string.

True and false regular-expression conditions produced consistently distinguishable application responses.

The issue was validated using a controlled test account.

Impact:
An attacker may be able to infer stored database values by repeatedly evaluating boolean query conditions.

Recommendation:
Reject database operators in user-controlled parameters, enforce strict scalar types and construct database queries using validated application-controlled query structures.
```

---

# Example Finding: Verbose Database Error

```text
Finding:
Application Discloses MongoDB Query Errors

Observed:
Unexpected JSON object input caused the application to return verbose MongoDB-related errors including internal query and framework information.

Impact:
The disclosed information assists attackers in identifying the backend database technology and understanding internal query processing.

No successful query manipulation was demonstrated.

Recommendation:
Implement centralised exception handling and return generic production error messages while recording detailed database errors only in protected server-side logs.
```

This should normally be reported as:

```text
Information Disclosure
```

rather than confirmed NoSQL injection unless query manipulation is demonstrated.

---

# Reporting Titles

Useful titles include:

```text
NoSQL Operator Injection Allows Authentication Bypass

NoSQL Injection Allows Unauthorised Database Record Access

Blind NoSQL Injection Allows Inference of Sensitive Account Data

NoSQL Operator Injection Allows Manipulation of Search Filters

NoSQL Injection Allows Authorisation Bypass

MongoDB Query Injection in User Search Functionality

NoSQL Injection in Password Reset Account Lookup

Application Accepts MongoDB Operators in User-Controlled Query Parameters
```

Avoid vague titles such as:

```text
NoSQL Issue
MongoDB Vulnerability
Database Problem
```

Describe the demonstrated impact.

---

# Severity

Severity depends on demonstrated impact.

For example:

```text
MongoDB error disclosure
```

may be:

```text
Informational / Low
```

depending on context.

While:

```text
NoSQL Injection
      ↓
Unauthorised Record Access
```

may be:

```text
Medium / High
```

depending on the data.

And:

```text
NoSQL Injection
      ↓
Authentication Bypass
      ↓
Administrative Account
```

may be:

```text
Critical
```

depending on the environment.

Severity should reflect:

```text
Exploitability
Authentication requirements
Privileges gained
Data exposed
Business impact
```

---

# Remediation

The strongest defence is:

```text
Never allow untrusted input to define database query structure.
```

Instead:

```text
User Input
    ↓
Strict Validation
    ↓
Expected Scalar / Structure
    ↓
Application-Controlled Query
    ↓
Database
```

---

# Strict Type Validation

If the application expects:

```text
username = string
```

reject:

```text
Object
Array
Boolean
Null
Number
```

unless those types are explicitly valid.

Conceptually:

```javascript
if (typeof username !== "string") {
    reject();
}
```

Framework-specific schema validation is preferable for larger applications.

---

# Schema Validation

Use explicit request schemas.

For example:

```text
username:
    type: string
    required: true
    maximum length: 100

password:
    type: string
    required: true
```

Reject unexpected structures before they reach database logic.

---

# Allowlist Fields

If an API supports filtering:

```text
Allowed:
username
status
createdDate
```

reject:

```text
Unknown fields
Database operators
Unexpected nested objects
```

unless explicitly required.

---

# Allowlist Operators

If the application intentionally provides advanced filtering, do not pass arbitrary operators directly to the database.

Instead map application-level operators:

```text
equals
contains
before
after
```

to internally controlled database operations.

For example:

```text
Client:
{
    "operator": "equals"
}

Application:
equals → $eq
```

The client should not directly supply:

```text
$eq
$where
$regex
```

unless there is a carefully designed reason.

---

# Do Not Pass `req.body` Directly

Avoid patterns conceptually equivalent to:

```javascript
db.collection.find(req.body)
```

or:

```javascript
User.findOne(req.body)
```

Instead:

```text
Extract Expected Fields
      ↓
Validate
      ↓
Normalise
      ↓
Construct Explicit Query
```

---

# Sanitisation

MongoDB-focused sanitisation libraries can help remove or reject keys containing dangerous query syntax.

However:

```text
Sanitisation
```

should supplement:

```text
Strict validation
Explicit query construction
Authorisation
```

rather than replace them.

---

# Reject Dollar-Prefixed Keys

Where users should never control MongoDB operators, reject unexpected keys beginning with:

```text
$
```

Also consider unexpected nested object structures.

The exact implementation depends on the framework and database driver.

---

# Validate Nested Objects

Do not validate only top-level keys.

Example:

```json
{
  "profile": {
    "username": {
      "$ne": ""
    }
  }
}
```

Validation must apply recursively to the intended request structure.

---

# Avoid `$where`

Avoid server-side JavaScript query functionality such as:

```text
$where
```

especially when any part of the expression could contain untrusted input.

Use normal query operators and application-controlled query construction instead.

---

# Authentication Queries

Authentication queries should use explicit scalar values.

Conceptually:

```text
Validated Username
       +
Validated Password Handling
       ↓
Explicit Authentication Logic
```

Passwords should normally be:

```text
Hashed
Salted
Verified using password-hashing functions
```

rather than queried as plaintext database values.

---

# Password Storage

Do not implement authentication as:

```javascript
findOne({
    username: username,
    password: password
})
```

Instead:

```text
Find account using validated username
      ↓
Retrieve password hash
      ↓
Verify password with appropriate password hashing algorithm
```

This reduces both:

```text
Password security problems
Query manipulation opportunities
```

---

# Authorisation

Even a perfectly constructed database query must still enforce:

```text
Who may access the returned object?
```

For example:

```text
User requests object
      ↓
Database finds object
      ↓
Authorisation check
      ↓
Return / Reject
```

NoSQL injection prevention does not replace object-level authorisation.

---

# Least Privilege

The database account used by the application should have only the permissions required.

For example, a read-only search service should not necessarily have:

```text
Delete permissions
Administrative permissions
Database management permissions
```

This reduces impact if an injection vulnerability exists.

---

# Error Handling

Do not expose:

```text
MongoDB errors
Query syntax
Collection names
Stack traces
Connection strings
Internal code
```

to users.

Instead:

```text
Client:
Generic error

Server logs:
Detailed diagnostic information
```

---

# Logging and Monitoring

Monitor suspicious patterns such as:

```text
Unexpected nested objects
Dollar-prefixed keys
Repeated query errors
Unusual regex operators
Large filter structures
Authentication anomalies
```

Avoid logging sensitive values unnecessarily.

---

# Rate Limiting

Rate limiting is especially useful for reducing the impact of:

```text
Blind extraction
Authentication attacks
Enumeration
```

However:

```text
Rate Limiting
```

does not fix:

```text
NoSQL Injection
```

The underlying query construction must still be corrected.

---

# Test After Remediation

Repeat:

```text
Original legitimate request
      ↓
Type mutation
      ↓
Object input
      ↓
Operator input
      ↓
TRUE / FALSE conditions
```

Expected secure behaviour:

```text
Unexpected types rejected
Operators treated as invalid input
No database errors
No query semantic changes
```

---

# Tools

Useful tools include:

```text
Burp Suite
Burp Repeater
Burp Intruder
Burp Comparer
Burp Scanner
NoSQLMap
curl
jq
Browser DevTools
```

The strongest workflow remains:

```text
Manual Discovery
      ↓
Manual Confirmation
      ↓
Controlled Automation
      ↓
Manual Validation
```

---

# References

## PortSwigger Web Security Academy: NoSQL Injection

https://portswigger.net/web-security/nosql-injection

Covers:

```text
NoSQL injection concepts
Syntax injection
Operator injection
Authentication bypass
Information extraction
MongoDB-specific techniques
```

---

## PortSwigger NoSQL Injection Labs

https://portswigger.net/web-security/all-labs#nosql-injection

Practical labs covering NoSQL injection techniques.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

See the input-validation testing sections for injection methodology and database-related testing guidance.

---

## OWASP Injection Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html

General guidance for preventing injection vulnerabilities.

---

## MongoDB Query and Projection Operators

https://www.mongodb.com/docs/manual/reference/operator/query/

Official MongoDB documentation describing query operators such as:

```text
Comparison operators
Logical operators
Element operators
Evaluation operators
Array operators
```

---

## MongoDB `$where`

https://www.mongodb.com/docs/manual/reference/operator/query/where/

Official documentation for MongoDB's `$where` query operator.

Review the security and performance implications before using server-side JavaScript query functionality.

---

## Mongoose

https://mongoosejs.com/

Mongoose is a commonly used MongoDB object modelling library for Node.js applications.

---

## NoSQLMap

https://github.com/codingo/NoSQLMap

Open-source NoSQL injection testing tool.

Use automated testing carefully and only against authorised systems.

---

# Final NoSQL Injection Testing Model

```text
                         APPLICATION
                              ↓
                      IDENTIFY INPUT
                              ↓
                  DATABASE-RELATED?
                              ↓
                             YES
                              ↓
                      ESTABLISH BASELINE
                              ↓
                      EXPECTED TYPE?
                              ↓
                            STRING
                              ↓
                     MUTATE INPUT TYPE
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
            NULL            ARRAY           OBJECT
              ↓               ↓               ↓
              └───────────────┼───────────────┘
                              ↓
                     OBJECT ACCEPTED?
                              ↓
                             YES
                              ↓
                  TEST SAFE QUERY OPERATORS
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
             $eq             $ne           $exists
              ↓               ↓               ↓
              └───────────────┼───────────────┘
                              ↓
                           $regex
                              ↓
                     RESPONSE CHANGES?
                              ↓
                             YES
                              ↓
                    TRUE / FALSE TEST
                              ↓
                      CONSISTENT RESULT?
                              ↓
                             YES
                              ↓
                   DETERMINE SECURITY IMPACT
                              ↓
          ┌───────────────────┼───────────────────┐
          ↓                   ↓                   ↓
    AUTHENTICATION       AUTHORISATION           DATA
       BYPASS               BYPASS             EXPOSURE
          ↓                   ↓                   ↓
          └───────────────────┼───────────────────┘
                              ↓
                   CONTROLLED VALIDATION
                              ↓
                       MINIMAL PROOF
                              ↓
                          DOCUMENT
                              ↓
                            REPORT
```

The key principle is:

> Do not approach NoSQL injection as a collection of MongoDB payloads. First determine how the application parses the input, what data type it expects, how that value reaches the database, and whether an attacker can turn an expected value into query structure. Use simple type mutations and controlled operators to establish the behaviour, then demonstrate the smallest possible security impact using controlled data.
