---
title: SQL Injection Cheatsheet
description: Detailed practical SQL injection reference for authorised web application security testing covering detection, manual validation, UNION, error-based, boolean-based, time-based and second-order SQL injection, DBMS differences, Burp Suite, SQLMap, evidence, remediation and retesting.
---

# SQL Injection Cheatsheet

SQL injection occurs when untrusted input influences the structure of a database query instead of being handled purely as data.

A simplified vulnerable flow is:

```text
User Input
    |
    v
Application
    |
    v
SQL String Construction
    |
    v
Database
```

For example:

```python
username = request.form["username"]

query = "SELECT * FROM users WHERE username = '" + username + "'"

cursor.execute(query)
```

Input is inserted directly into the SQL statement.

The intended query might be:

```sql
SELECT * FROM users
WHERE username = 'alice';
```

A security tester should determine whether supplied input can alter the SQL syntax or query logic.

!!! warning "Authorised Security Testing"

    Perform SQL injection testing only against applications and databases that are explicitly within scope. Start with low-impact detection and validation. Database extraction, file access, operating-system interaction, destructive queries and high-volume automation can materially affect systems and should only be performed when specifically authorised.


# Quick Reference

## Initial Character Tests

```text
'

"

`

)

'))
```

These are probes, not proof of SQL injection.


## Boolean Comparison

```text
AND 1=1

AND 1=2
```

String context may require different syntax.


## ORDER BY

```text
ORDER BY 1

ORDER BY 2

ORDER BY 3
```


## UNION Shape

```text
UNION SELECT NULL

UNION SELECT NULL,NULL

UNION SELECT NULL,NULL,NULL
```


## Comments

Common SQL comment syntax includes:

```text
--

#

/* */
```

Support depends on the DBMS and query context.


## SQLMap Basic

```bash
sqlmap -u 'https://example.com/product?id=1'
```


## SQLMap Specific Parameter

```bash
sqlmap -u 'https://example.com/product?id=1' -p id
```


## SQLMap From Burp Request

```bash
sqlmap -r request.txt
```


# SQL Injection Testing Model

Do not use:

```text
Payload
   |
   v
Different Response
   |
   v
SQL Injection
```

Use:

```text
Baseline
   |
   v
Controlled Input
   |
   v
Response Difference
   |
   v
Repeat
   |
   v
True / False Comparison
   |
   v
Understand Context
   |
   v
Confirm Database Influence
   |
   v
Determine Impact
   |
   v
Evidence
```


# Where to Test

Potential SQL-backed inputs include:

```text
Query parameters

POST parameters

JSON properties

Path parameters

Cookies

HTTP headers

Search fields

Filters

Sorting parameters

Pagination

Login forms

Registration forms

Reporting functions

Export functions

Administrative interfaces

API parameters
```


# Example Parameters

```text
?id=42

?user=alice

?category=books

?sort=name

?order=asc

?page=2

?filter=active
```


# Do Not Ignore Non-Numeric Inputs

SQL injection is not limited to:

```text
?id=1
```

Inputs such as:

```text
?username=alice

?category=laptops

?status=active
```

may also influence database queries.


# HTTP Headers

Applications may store or query values from:

```text
User-Agent

Referer

X-Forwarded-For

X-Client-ID

Custom application headers
```

These are lower-probability inputs but can matter in logging, analytics and administrative workflows.


# Establish a Baseline

Before modifying a parameter, capture the normal response.

Example:

```http
GET /product?id=10 HTTP/1.1
Host: example.com
```

Record:

```text
Status code

Response length

Response body

Response time

Redirects

Displayed records

Application errors
```


# Baseline Example

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 4821
```

Page:

```text
Product: Security Handbook
Price: 49.99
```


# First Probe

A simple quote can test whether the input reaches a string-sensitive query:

```http
GET /product?id=10' HTTP/1.1
Host: example.com
```

Possible outcomes:

```text
Same response

Different response

Application error

Database error

500 response

Empty result

Redirect

WAF response
```


# Quote Error Is Not Proof

Suppose:

```text
?id=10'
```

returns:

```text
500 Internal Server Error
```

This does not prove SQL injection.

The quote may cause:

```text
Input validation failure

Framework parsing error

Application exception

WAF behaviour

Database syntax error
```

Further validation is required.


# Error-Based Clues

Database errors may expose strings such as:

```text
SQL syntax

ODBC

JDBC

ORA-

PostgreSQL

SQLite

MySQL

SQL Server

Unclosed quotation mark

unterminated quoted string
```

These can indicate that database syntax was affected, but a controlled confirmation is still preferable.


# Burp Suite Workflow

A practical manual workflow:

```text
Proxy
  |
  v
Capture Request
  |
  v
Send to Repeater
  |
  v
Baseline
  |
  v
Modify One Input
  |
  v
Compare
  |
  v
Repeat
  |
  v
Document
```


# Send to Repeater

In Burp:

```text
Proxy
  -> HTTP history
  -> Select request
  -> Send to Repeater
```

Then modify only the suspected input.


# Change One Variable at a Time

Bad methodology:

```text
Change parameter

Change cookie

Change header

Change method

Change path
```

all in one request.

Better:

```text
Baseline
   |
   v
Change One Parameter
   |
   v
Observe
```


# Numeric Context

Suppose the application constructs:

```sql
SELECT name, price
FROM products
WHERE id = 10;
```

Potential user input occupies:

```text
10
```

without quotes.

This is a numeric context.


# String Context

Suppose:

```sql
SELECT id, username
FROM users
WHERE username = 'alice';
```

The input occupies:

```text
'alice'
```

A successful test must account for the surrounding quote.


# Context Matters

The same payload will not work in every query.

Potential contexts include:

```text
Numeric

Single-quoted string

Double-quoted identifier/string depending on DBMS

LIKE expression

ORDER BY

LIMIT/OFFSET

INSERT

UPDATE

Nested subquery
```


# Boolean-Based Validation

A useful low-impact approach is comparing logically true and false expressions.

Conceptually:

```text
Original Request
      |
      v
True Condition
      |
      v
Response A

False Condition
      |
      v
Response B
```

If the application consistently behaves differently, investigate further.


# Numeric Boolean Example

Baseline:

```text
?id=10
```

True condition:

```text
?id=10 AND 1=1
```

False condition:

```text
?id=10 AND 1=2
```


# Expected Pattern

Potentially vulnerable behaviour:

```text
?id=10
        -> Product returned

?id=10 AND 1=1
        -> Same product returned

?id=10 AND 1=2
        -> Product not returned
```

This is much stronger evidence than a single error response.


# Repeatability

Repeat each request.

For example:

```text
Baseline
True
False
True
False
Baseline
```

This helps distinguish deterministic database behaviour from:

```text
Caching

Dynamic content

Load balancing

Random application errors

Rate limiting
```


# String Boolean Example

A string parameter may require closing the original string before adding a condition.

Conceptually:

```sql
WHERE category = '<INPUT>'
```

A test must preserve valid SQL syntax while producing controlled true and false conditions.

Exact syntax depends on the query and DBMS.


# Response Comparison

Compare:

```text
Status

Length

Words

Lines

Specific text

Number of records

JSON properties

Redirects
```


# Example

True:

```http
HTTP/1.1 200 OK
Content-Length: 5821
```

Contains:

```text
12 products found
```

False:

```http
HTTP/1.1 200 OK
Content-Length: 2910
```

Contains:

```text
No products found
```

The status remains:

```text
200
```

but the application state differs.


# Burp Comparer

Burp Comparer can help compare responses where differences are subtle.

Useful workflow:

```text
True Response
     |
     v
Send to Comparer

False Response
     |
     v
Send to Comparer
     |
     v
Compare
```


# Dynamic Responses

Response length alone may be unreliable when pages contain:

```text
CSRF tokens

Timestamps

Request IDs

Random recommendations

Advertisements

User-specific content
```

Look for stable semantic differences.


# Stable Response Markers

Examples:

```text
"productFound": true

"count": 12

"No results"

"Welcome alice"

Specific table row
```


# ORDER BY Technique

`ORDER BY` can sometimes help determine the number of selected columns.

Example sequence:

```text
ORDER BY 1

ORDER BY 2

ORDER BY 3

ORDER BY 4
```

Conceptually:

```text
ORDER BY 1
    -> Valid

ORDER BY 2
    -> Valid

ORDER BY 3
    -> Valid

ORDER BY 4
    -> Error
```

This may suggest:

```text
3 selected columns
```

provided the behaviour is caused by SQL ordering rather than application logic.


# ORDER BY Interpretation

Do not conclude column count from one failed request.

Confirm:

```text
ORDER BY 3 consistently works

ORDER BY 4 consistently fails
```


# UNION-Based SQL Injection

`UNION` combines the result sets of compatible `SELECT` statements.

Conceptually:

```sql
SELECT a,b
FROM products

UNION

SELECT c,d
FROM another_table;
```

The result sets generally need compatible column counts and data types.


# Determine Column Count

A common controlled approach uses `NULL`:

```text
UNION SELECT NULL

UNION SELECT NULL,NULL

UNION SELECT NULL,NULL,NULL
```

Increase until the query shape is accepted.


# Why NULL?

`NULL` is often useful because it can be compatible with multiple data types.

It is not guaranteed to work in every context.


# UNION Example

Suppose:

```text
UNION SELECT NULL,NULL
```

fails but:

```text
UNION SELECT NULL,NULL,NULL
```

succeeds.

This suggests a three-column result may be involved.


# Determine Reflected Column

After determining the query shape, a harmless marker can help determine which output column is rendered.

Conceptually:

```text
UNION SELECT NULL,'TEST123',NULL
```

If:

```text
TEST123
```

appears in the page, that column is reflected.


# Do Not Jump Directly to Data Extraction

For many assessments, proving:

```text
Controlled UNION data can be returned
```

is enough to demonstrate the vulnerability.

Bulk database extraction may not be necessary and may exceed scope.


# UNION Validation Model

```text
Determine Column Count
        |
        v
Determine Compatible Columns
        |
        v
Place Harmless Marker
        |
        v
Marker Appears
        |
        v
SQL Query Influence Confirmed
```


# Error-Based SQL Injection

Some DBMS operations can cause controlled database errors that include query-derived information.

The exact functions and behaviour differ substantially between:

```text
MySQL

MariaDB

PostgreSQL

Microsoft SQL Server

Oracle

SQLite
```

For normal assessments, prefer the least invasive proof necessary.


# Error-Based Testing Principle

A useful error-based proof demonstrates:

```text
Input
  |
  v
Database Expression
  |
  v
Controlled Database Error
```

rather than merely crashing the application.


# Boolean Blind SQL Injection

Blind SQL injection occurs when query results are not directly displayed.

Instead, the tester infers database behaviour from differences such as:

```text
Content

Status

Redirect

Boolean state
```


# Boolean Blind Model

```text
Condition True
     |
     v
Response A

Condition False
     |
     v
Response B
```

If this is repeatable, individual facts can theoretically be inferred through true/false questions.


# Keep Blind Validation Minimal

A formal assessment usually does not require extracting an entire database.

A minimal proof can demonstrate:

```text
True expression produces state A.

False expression produces state B.
```

This is often sufficient to establish query control.


# Time-Based Blind SQL Injection

Time-based testing is useful when:

```text
Response body does not change

Status does not change

No errors are shown
```

but database-controlled delay can influence response time.


# Time-Based Model

```text
Normal Request
      |
      v
Baseline Timing

Conditional Delay Request
      |
      v
Longer Timing

Control Request
      |
      v
Normal Timing
```


# Timing Requires Repetition

Do not use:

```text
One request took 5 seconds
```

as proof.

Network latency can vary.


# Better Timing Test

Collect multiple measurements:

```text
Baseline:
0.31
0.28
0.34
0.30
0.29

Control:
0.33
0.30
0.31

Conditional delay:
5.31
5.29
5.34
```

A repeated, controlled delay is much stronger evidence.


# Timing Noise

Possible causes:

```text
Network latency

Database load

Application load

Rate limiting

Queueing

CDN behaviour

WAF processing

Garbage collection
```


# Keep Delays Short

Do not use unnecessarily long delays.

A small repeatable difference is preferable to repeatedly holding database connections open for long periods.


# DBMS Identification

Identifying the DBMS can help select appropriate syntax.

Possible systems:

```text
MySQL / MariaDB

PostgreSQL

Microsoft SQL Server

Oracle Database

SQLite
```


# Do Not Rely Only on Server Errors

DBMS identification can also come from:

```text
Application stack

Dependency files

Connection strings

Source code

Database drivers

SQL syntax

SQLMap fingerprinting
```


# Common DBMS Characteristics

| DBMS | Common Indicators |
|---|---|
| MySQL/MariaDB | MySQL drivers, backticks, `LIMIT` |
| PostgreSQL | PostgreSQL drivers, `::type`, `RETURNING` |
| SQL Server | `SqlClient`, T-SQL, `TOP`, brackets |
| Oracle | Oracle drivers, PL/SQL, `DUAL` |
| SQLite | SQLite libraries, local `.db` files |


# SQL Comments

Common syntax:

## Standard SQL-Style

```sql
-- comment
```

Some DBMSs require whitespace after `--` in particular contexts.


## MySQL-Style

```sql
# comment
```


## Block Comment

```sql
/* comment */
```


# Comment Syntax Matters

If the application appends SQL after user input, correctly terminating or balancing the remainder of the original query may be necessary for controlled testing.

Do not assume one comment form works everywhere.


# Authentication Forms

Login queries are a classic SQL injection location.

Conceptually vulnerable code:

```sql
SELECT id
FROM users
WHERE username = '<username>'
AND password = '<password>';
```

Modern applications should not construct authentication queries this way and should not store passwords in directly comparable plaintext form.


# Authentication Testing

During authorised testing, focus on whether:

```text
Input alters authentication query logic
```

rather than attempting access to arbitrary real accounts.


# Search Functionality

Search functions commonly produce queries using:

```sql
LIKE
```

Example:

```sql
SELECT id, title
FROM articles
WHERE title LIKE '%<search>%';
```

The surrounding `%` and quotes affect injection context.


# Filtering

Filters may generate:

```sql
WHERE status = ?
AND category = ?
```

or dynamically concatenate conditions.

Dynamic query builders deserve careful review.


# Sorting

Sorting parameters can be interesting because identifiers often cannot be parameterised in the same way as normal values.

Example application logic:

```text
?sort=name
```

may influence:

```sql
ORDER BY name
```

Safe implementations should map user choices to known server-side column identifiers.


# Safe Sort Mapping

Example:

```python
allowed_sort = {
    "name": "name",
    "date": "created_at",
    "price": "price"
}

column = allowed_sort.get(request.args.get("sort"), "name")
```

The user selects a logical option rather than supplying arbitrary SQL.


# Pagination

Review:

```text
page

limit

offset

size
```

These values may influence:

```sql
LIMIT

OFFSET

TOP
```

depending on DBMS.


# JSON APIs

Example:

```http
POST /api/search HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "query": "laptop",
  "sort": "price"
}
```

Test each field independently.


# Nested JSON

Do not overlook:

```json
{
  "filter": {
    "category": "books",
    "owner": "alice"
  }
}
```

Nested properties can reach separate database operations.


# GraphQL

GraphQL resolvers may ultimately construct database queries.

Test the application's GraphQL inputs and resolver behaviour rather than assuming GraphQL itself prevents SQL injection.

See:

[GraphQL Notes](../web/graphql.md)


# REST APIs

Potential parameters exist in:

```text
Path

Query

JSON body

Headers

Cookies
```

Example:

```http
GET /api/users/42
```

The path value:

```text
42
```

may become a database identifier.


# Stored / Second-Order SQL Injection

Second-order SQL injection occurs when malicious or malformed input is stored safely at one stage but later used unsafely in a different SQL query.

Conceptually:

```text
Input
  |
  v
Stored in Database
  |
  v
Later Retrieved
  |
  v
Concatenated Into New SQL
  |
  v
Injection
```


# Example Workflow

```text
Registration
     |
     v
Display Name Stored
     |
     v
Admin Reporting Function
     |
     v
Display Name Added to Dynamic SQL
```

The vulnerable behaviour occurs later, not during initial storage.


# Second-Order Testing

Track user-controlled values across workflows:

```text
Create

Store

Read

Update

Search

Export

Admin view

Reporting
```


# Common Second-Order Locations

```text
User profiles

Organisation names

Saved searches

Report names

Imported records

CSV data

Administrative dashboards

Audit/log viewers
```


# Out-of-Band Behaviour

Some database environments can perform external network interactions through database or extension functionality.

Out-of-band testing can have broader operational consequences and should only be used when specifically authorised.

For normal SQL injection validation, prefer:

```text
Boolean

Error

UNION marker

Controlled timing
```

where possible.


# Stored Procedures

Stored procedures do not automatically prevent SQL injection.

Safe:

```text
Stored procedure
    |
    v
Parameters
    |
    v
Static SQL
```

Potentially unsafe:

```text
Stored procedure
    |
    v
Dynamic SQL String
    |
    v
EXECUTE
```


# ORM Does Not Automatically Prevent SQL Injection

ORMs reduce many SQL injection risks when their normal parameterised APIs are used.

Risk can return through:

```text
Raw queries

String concatenation

Dynamic filters

Dynamic sorting

Unsafe query fragments
```


# Source-Code Review

Search for database operations using ripgrep.

Python:

```bash
rg -ni 'execute\(|executemany\(|raw\(' -g '*.py' .
```

Java:

```bash
rg -ni 'createStatement|prepareStatement|executeQuery|executeUpdate' -g '*.java' .
```

PHP:

```bash
rg -ni 'mysqli_query|->query\(|->prepare\(' -g '*.php' .
```

.NET:

```bash
rg -ni 'SqlCommand|ExecuteReader|ExecuteNonQuery|FromSqlRaw' -g '*.cs' .
```


# Source-to-Sink Review

```text
HTTP Input
    |
    v
Variable
    |
    v
Transformation
    |
    v
Query Construction
    |
    v
Database API
```


# Vulnerable Source Example

```python
user_id = request.args["id"]

query = "SELECT username FROM users WHERE id = " + user_id

cursor.execute(query)
```


# Safer Source Example

```python
user_id = request.args["id"]

cursor.execute(
    "SELECT username FROM users WHERE id = %s",
    (user_id,)
)
```

Exact placeholder syntax depends on the database driver.


# Important Distinction

This:

```python
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
```

is different from:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)
```

The second separates:

```text
SQL structure
```

from:

```text
data.
```


# Search String Formatting

Python:

```bash
rg -n 'execute\(.*f"|execute\(.*format|execute\(.*\+' -g '*.py' .
```

This is heuristic only.

A match requires manual review.


# Search Raw SQL in ORMs

Examples:

```bash
rg -ni 'raw\(|execute\(|FromSqlRaw|createNativeQuery' .
```

Again:

```text
Raw SQL
```

does not automatically mean:

```text
SQL injection.
```


# Validation Questions

For every candidate ask:

```text
Is user input involved?

Can the user control SQL structure?

Is parameterisation used?

Is an allowlist used for identifiers?

Does validation occur before the query?

Is the code reachable?

Which database driver is used?

Is the affected query read-only?

What privileges does the database account have?
```


# Database Privileges Matter

SQL injection impact depends partly on the application's database account.

Potential privileges:

```text
SELECT

INSERT

UPDATE

DELETE

CREATE

DROP

EXECUTE
```

A least-privileged account can reduce impact.


# Do Not Assume DBA Privileges

A SQL injection vulnerability does not automatically imply:

```text
Database administrator

Operating-system access

File-system access
```

Determine actual privileges only as far as authorised and necessary.


# SQLMap

SQLMap can automate SQL injection detection and validation.

Use it after understanding the request and obtaining a manual baseline where possible.


# Basic GET Request

```bash
sqlmap -u 'https://example.com/product?id=10'
```


# Specific Parameter

```bash
sqlmap -u 'https://example.com/product?id=10' -p id
```


# POST Data

```bash
sqlmap -u 'https://example.com/search' --data='q=test'
```


# JSON Request

```bash
sqlmap -u 'https://example.com/api/search' \
  --method POST \
  --data='{"query":"test"}' \
  --headers='Content-Type: application/json'
```


# Burp Request File

Save the raw HTTP request as:

```text
request.txt
```

Then:

```bash
sqlmap -r request.txt
```


# Why `-r` Is Useful

It preserves complex request details such as:

```text
Method

Path

Cookies

Headers

POST body

JSON

Authentication
```


# Select Parameter With Request File

```bash
sqlmap -r request.txt -p id
```


# Batch Mode

```bash
sqlmap -r request.txt -p id --batch
```

Use automation cautiously because automatic choices may increase test volume.


# SQLMap Level

SQLMap provides increasing test levels.

Check installed help:

```bash
sqlmap -hh
```

Higher levels can test additional inputs and send more requests.


# SQLMap Risk

SQLMap also has a risk setting.

Before increasing it, review:

```bash
sqlmap -hh
```

Higher-risk tests may include queries with greater operational impact.

Do not increase settings simply because the default did not find anything.


# Technique Selection

SQLMap supports technique selection.

Common technique letters include categories for:

```text
Boolean-based blind

Error-based

UNION query

Stacked queries

Time-based blind

Inline queries
```

Check:

```bash
sqlmap -hh
```

for the exact syntax supported by your installed version.


# Restrict Automation

A better workflow is:

```text
Understand Request
      |
      v
Identify Candidate Parameter
      |
      v
Manual Validation
      |
      v
SQLMap Against Specific Parameter
```

rather than:

```text
Run SQLMap Everywhere
```


# SQLMap Through Proxy

When you need to observe a small controlled SQLMap test in Burp, review SQLMap's current proxy options:

```bash
sqlmap -hh
```

Large automated scans through Burp can create substantial proxy history.


# SQLMap Output Interpretation

Do not report:

```text
SQLMap says parameter is injectable.
```

Capture:

```text
Parameter

Injection type

DBMS

Representative request

Representative response

Manual confirmation

Security consequence
```


# SQLMap False Positives

Automation can be confused by:

```text
Dynamic pages

Unstable responses

WAFs

Rate limiting

Caching

Random server errors

Authentication expiry
```

Manually validate important findings.


# WAF Behaviour

SQL injection probes may trigger:

```text
403

406

429

Connection reset

Challenge page
```

This demonstrates defensive behaviour, not necessarily the presence or absence of SQL injection.


# Do Not Treat WAF Blocking as Proof of Safety

A WAF may block:

```text
obvious test string
```

while the underlying application still constructs unsafe queries.

The appropriate conclusion is:

```text
The tested request was blocked by a defensive control.
```

not:

```text
The application is not vulnerable.
```


# Do Not Automatically Evade WAFs

If WAF bypass testing is not explicitly part of scope, do not escalate into obfuscation or bypass techniques simply to continue automated testing.

Document the control and coordinate where necessary.


# Authentication Expiry

Automated testing may fail because:

```text
Session expires

CSRF token changes

JWT expires

Anti-automation token rotates
```

Reconfirm the request remains valid.


# CSRF Tokens

If a request requires a dynamic CSRF token, manual Repeater testing may be easier.

For automation, use tool-supported token handling only when necessary and within scope.


# Cookies

Authenticated request:

```http
Cookie: session=<session>
```

Treat session values as credentials.

Do not expose them in screenshots or reports unnecessarily.


# HTTP Parameter Pollution

Applications may behave differently when a parameter is supplied more than once:

```text
?id=1&id=2
```

This is not SQL injection itself but can affect which value reaches the query.


# Encoding

Burp normally helps URL-encode request parameters.

Remember:

```text
URL syntax

Application decoding

Framework parsing

Database syntax
```

are separate processing stages.


# Prepared Statements

Prepared statements are the primary defence for data values.

Conceptually:

```text
SQL Template
      +
Parameter Values
      |
      v
Database Driver
```

The values are not interpreted as query structure.


# Java Example

Safer:

```java
PreparedStatement stmt =
    connection.prepareStatement(
        "SELECT id, username FROM users WHERE username = ?"
    );

stmt.setString(1, username);
```


# C# Example

Safer:

```csharp
using var command = new SqlCommand(
    "SELECT Id, Username FROM Users WHERE Username = @username",
    connection
);

command.Parameters.AddWithValue("@username", username);
```


# PHP PDO Example

Safer:

```php
$stmt = $pdo->prepare(
    "SELECT id, username FROM users WHERE username = ?"
);

$stmt->execute([$username]);
```


# Python Example

Driver syntax varies.

Conceptually:

```python
cursor.execute(
    "SELECT id, username FROM users WHERE username = %s",
    (username,)
)
```


# Dynamic Identifiers

Parameters often cannot directly represent SQL identifiers such as:

```text
Table names

Column names

ASC / DESC
```

Use allowlists.


# Sort Direction Example

```python
direction = request.args.get("direction", "asc").lower()

if direction not in {"asc", "desc"}:
    direction = "asc"
```

Then map only known server-controlled values into the query.


# Input Validation Is Secondary

Validation is useful, but do not use it as the sole SQL injection defence.

Prefer:

```text
Parameterised Query
        +
Input Validation
        +
Least Privilege
```


# Escaping Alone Is Fragile

Manually escaping:

```text
'
```

or other SQL characters is error-prone because behaviour depends on:

```text
DBMS

Encoding

Connection settings

Query context
```

Use the database driver's parameterisation facilities.


# Stored Procedures

Stored procedures should use parameters internally.

Avoid:

```text
Stored Procedure
      |
      v
String Concatenation
      |
      v
Dynamic SQL
```


# Least Privilege

Application database accounts should receive only required permissions.

For example:

```text
Reporting Application

Needs:
SELECT

Does not need:
DROP
CREATE
ALTER
```


# Separate Accounts

Where appropriate:

```text
Read-only component
      -> Read-only DB account

Write component
      -> Limited write account

Administration
      -> Separate privileged workflow
```


# Error Handling

Production applications should not expose raw database errors.

Bad:

```text
SQLSTATE[42000] ...

ORA-00933 ...

Unclosed quotation mark ...
```

Prefer controlled application errors while retaining useful server-side logging.


# Logging

Log enough to investigate suspicious behaviour without logging:

```text
Passwords

Full authentication tokens

Sensitive query results

Unnecessary personal information
```


# Detection

Potential SQL injection indicators include:

```text
Repeated syntax errors

Unusual SQL keywords in parameters

High request volume against one parameter

Repeated true/false patterns

Repeated delayed requests

Database errors
```


# Detection Limitations

Do not rely only on keyword matching such as:

```text
UNION SELECT
```

because:

```text
Legitimate requests may contain SQL terminology

Attack strings can vary

Application context matters
```


# Database Monitoring

Useful defensive telemetry can include:

```text
Database errors

Query failures

Unusual query shapes

Unexpected database account activity

Slow queries

Privilege violations
```


# Application Telemetry

Capture:

```text
Request ID

Route

User/account

Parameter names

Status

Response time

Application exception
```

Avoid storing sensitive parameter values unless necessary and approved.


# Evidence Collection

For a SQL injection finding record:

```text
Finding ID

Target

Endpoint

Method

Parameter

Authentication context

Baseline request

Baseline response

True request

True response

False request

False response

Injection technique

DBMS if established

Security impact

Database privileges if relevant

Timestamp
```


# Minimal Evidence

A strong proof might contain:

```text
1. Baseline request returns product.

2. True SQL condition returns same product.

3. False SQL condition returns no product.

4. Behaviour is repeatable.

5. Only the tested parameter changes.
```


# Avoid Sensitive Database Dumps

Do not place large extracted datasets in a report.

Prefer the minimum evidence necessary to prove impact.


# Sensitive Data

If limited data access must be demonstrated:

```text
Use a controlled test record where possible.

Minimise rows.

Redact unnecessary values.

Stop once impact is established.
```


# Reporting Example - Boolean SQL Injection

Weak:

> The `id` parameter is vulnerable to SQL injection.

Better:

> The `id` parameter on `GET /product` influences the application's database query. A logically true condition produced the normal product response, while an equivalent false condition consistently produced the application's no-result state. Repeated control requests produced the original response, demonstrating that the parameter can alter database query logic.


# Reporting Example - UNION SQL Injection

> The `category` parameter was confirmed to influence a SQL query. After determining the result shape, a controlled `UNION SELECT` test caused a harmless marker supplied by the tester to be returned in the application response. This demonstrates that attacker-controlled SQL result data can be incorporated into the application's query output.


# Reporting Example - Time-Based SQL Injection

> The tested parameter produced a repeatable database-controlled timing difference. Baseline and false-condition requests consistently completed within the normal response range, while the conditional-delay expression introduced the expected additional delay across repeated trials. No bulk database extraction was performed.


# Reporting Example - Source Review

> The application constructs the product lookup query by concatenating the `id` request parameter directly into the SQL statement before passing the resulting string to the database driver. No parameterisation was identified in the reviewed data flow. Runtime validation confirmed that controlled boolean expressions alter the query result.


# Remediation

Primary recommendation:

```text
Use parameterised queries / prepared statements.
```

Also:

```text
Allowlist dynamic identifiers.

Validate input according to business requirements.

Use least-privileged database accounts.

Avoid exposing raw database errors.

Review similar query construction throughout the application.

Add regression tests.
```


# Root Cause Review

Do not remediate only:

```text
/product?id=
```

Search for the coding pattern.

For example:

```text
String concatenation
      |
      v
Database execution
```

may exist in multiple endpoints.


# Source Search During Remediation

Python:

```bash
rg -ni 'execute\(|executemany\(|raw\(' -g '*.py' .
```

.NET:

```bash
rg -ni 'SqlCommand|FromSqlRaw|ExecuteSqlRaw' -g '*.cs' .
```

Java:

```bash
rg -ni 'createStatement|prepareStatement|createNativeQuery' -g '*.java' .
```


# Retesting

Retest the exact original endpoint and parameter first.

```text
Original Request
      |
      v
Original True Condition
      |
      v
Original False Condition
      |
      v
No SQL-Controlled Difference
      |
      v
Normal Functionality Works
```


# Do Not Retest Only the Original String

A developer may block one test string without fixing the query.

For example:

```text
Block "UNION"
```

does not fix:

```text
String concatenation into SQL.
```

Retest the root cause.


# Source-Level Retest

Confirm the code now uses:

```text
Parameterised query
```

rather than:

```text
User input concatenated into SQL.
```


# Functional Retest

Also verify:

```text
Valid product lookup works

Search works

Sorting works

Filtering works

Pagination works
```

Security remediation should not unnecessarily break intended functionality.


# Regression Testing

Add tests such as:

```text
Normal input returns expected data.

Special characters are treated as data.

Boolean SQL syntax does not alter query logic.

Invalid identifiers are rejected.

Authorised functionality remains available.
```


# Common False Positives

## Generic 500 Error

```text
'
   -> 500
```

Could be:

```text
Application parser

Validation

WAF

Unhandled exception
```

Need controlled SQL-specific confirmation.


## Different Response Length

Could be:

```text
Dynamic token

Timestamp

Random content

Cache

Personalisation
```


## Slow Response

Could be:

```text
Network

Load

Rate limit

Database contention
```

Need repeated controlled timing.


## SQL Keyword Blocked

Could indicate:

```text
WAF rule
```

not necessarily SQL injection.


## SQL Error in Page

A database error confirms database-related processing but does not always prove attacker-controlled query structure.

Validate further.


# Common Testing Mistakes

## Testing Only Quotes

```text
'
```

is a probe, not a complete methodology.


## Testing Only Numeric IDs

Search, sorting, filters and JSON APIs are also important.


## Trusting SQLMap Without Manual Validation

Automation should support analysis, not replace it.


## Dumping the Database Immediately

Usually unnecessary for proving SQL injection.


## Ignoring Authentication Context

A vulnerability available only to:

```text
Administrator
```

has a different threat model from one available to:

```text
Unauthenticated Internet User.
```


## Ignoring Query Privileges

Database permissions influence impact.


## Ignoring Second-Order Behaviour

Stored data can become dangerous later.


## Ignoring Source Code

When white-box access exists, source review can quickly identify unsafe query construction.


# Practical Testing Sequence

```text
                    ENDPOINT
                       |
                       v
                   BASELINE
                       |
                       v
                 SIMPLE PROBE
                       |
                       v
               RESPONSE CHANGE?
                  /          \
                No            Yes
                |              |
                v              v
         Other Inputs      CONTROL TEST
                               |
                               v
                       TRUE / FALSE PAIR
                               |
                               v
                         REPEATABLE?
                          /       \
                        No         Yes
                        |           |
                        v           v
                 INVESTIGATE     IDENTIFY
                    NOISE         CONTEXT
                                      |
                                      v
                                  DBMS?
                                      |
                                      v
                              MINIMAL PROOF
                                      |
                                      v
                                   IMPACT
                                      |
                                      v
                                  EVIDENCE
```


# Practical Manual Checklist

## Reconnaissance

- [ ] Endpoint identified
- [ ] Method identified
- [ ] Parameters identified
- [ ] Authentication context recorded
- [ ] Request baseline captured
- [ ] Response baseline captured
- [ ] Technology identified where possible

## Detection

- [ ] Quote behaviour tested where appropriate
- [ ] Numeric context considered
- [ ] String context considered
- [ ] Boolean comparison performed
- [ ] True condition tested
- [ ] False condition tested
- [ ] Tests repeated
- [ ] Dynamic content considered
- [ ] WAF behaviour considered

## Query Shape

- [ ] Column-count testing performed only where relevant
- [ ] `ORDER BY` behaviour compared
- [ ] `UNION` shape tested where appropriate
- [ ] Harmless marker used
- [ ] Data extraction minimised

## Blind Testing

- [ ] Stable true state identified
- [ ] Stable false state identified
- [ ] Timing baseline established if required
- [ ] Multiple timing measurements captured
- [ ] Delay kept reasonable
- [ ] Network noise considered

## Input Locations

- [ ] Query parameters
- [ ] POST form fields
- [ ] JSON fields
- [ ] Path values
- [ ] Cookies where relevant
- [ ] Headers where relevant
- [ ] Search
- [ ] Filter
- [ ] Sort
- [ ] Pagination

## Second Order

- [ ] Stored user input identified
- [ ] Later processing reviewed
- [ ] Administrative workflows considered
- [ ] Reporting/export workflows considered

## Automation

- [ ] Manual baseline established before SQLMap
- [ ] Correct parameter selected
- [ ] Request file used where useful
- [ ] Test volume considered
- [ ] High-risk automation avoided unless authorised
- [ ] Automated finding manually validated

## Source Review

- [ ] Input source identified
- [ ] Query construction identified
- [ ] Database API identified
- [ ] Parameterisation reviewed
- [ ] Dynamic identifiers reviewed
- [ ] ORM raw queries reviewed
- [ ] Reachability confirmed
- [ ] Similar patterns searched

## Impact

- [ ] Authentication context considered
- [ ] Database privileges considered
- [ ] Data sensitivity considered
- [ ] Read/write impact considered
- [ ] Application role considered
- [ ] Minimal proof used

## Evidence

- [ ] Endpoint
- [ ] Parameter
- [ ] Method
- [ ] Baseline
- [ ] True condition
- [ ] False condition
- [ ] Representative responses
- [ ] Timestamp
- [ ] DBMS if established
- [ ] Tool version if automation used
- [ ] Sensitive values redacted

## Retest

- [ ] Exact endpoint retested
- [ ] Original parameter retested
- [ ] Root cause retested
- [ ] Parameterisation confirmed where source available
- [ ] Similar query paths reviewed
- [ ] Normal functionality verified
- [ ] Regression test recommended


# Technique Comparison

| Technique | Primary Signal | Useful When | Main Caution |
|---|---|---|---|
| Error-based | Database error | Errors exposed | Error alone may be ambiguous |
| Boolean-based | Content/state difference | Stable response states | Dynamic content can create noise |
| UNION-based | Controlled output | Query results displayed | Query shape must be compatible |
| Time-based | Response delay | No visible output difference | Network/load noise |
| Second-order | Later SQL behaviour | Input stored first | Requires multi-step workflow |


# Input Context Matrix

| Context | Example | Main Question |
|---|---|---|
| Numeric | `id=10` | Can input alter numeric expression? |
| String | `name=alice` | Is value placed inside quotes? |
| Search | `q=laptop` | Is input used in `LIKE` or search query? |
| Sort | `sort=name` | Is identifier allowlisted? |
| Filter | `status=active` | Is dynamic condition constructed safely? |
| Pagination | `limit=20` | Is numeric value safely handled? |
| JSON | `{"id":10}` | Which property reaches SQL? |
| Path | `/users/10` | Is route value used as database identifier? |
| Stored | profile value | Is it later concatenated into SQL? |


# Result Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| Quote causes 500 | Input affects processing | SQL injection |
| SQL error displayed | Database processing involved | Exploitable SQL injection |
| True/false responses differ | Input may alter logic | SQLi without repeatability/context |
| `ORDER BY n` changes behaviour | Query ordering may be affected | Exact column count from one request |
| UNION marker appears | Controlled query output | Full database compromise |
| Controlled delay repeats | Query may influence timing | SQLi if controls/noise not excluded |
| SQLMap reports injectable | Automated detection | Finding without manual confirmation |
| WAF blocks payload | Defensive rule triggered | Underlying query is safe |
| Raw SQL exists in source | SQL is manually written | Injection without untrusted input |
| String concatenation reaches query | Strong source candidate | Runtime exploitability without reachability |


# DBMS Review Matrix

| Area | MySQL/MariaDB | PostgreSQL | SQL Server | Oracle | SQLite |
|---|---|---|---|---|---|
| Common web use | Yes | Yes | Yes | Enterprise | Embedded/smaller apps |
| Parameterisation available | Yes | Yes | Yes | Yes | Yes |
| Error syntax differs | Yes | Yes | Yes | Yes | Yes |
| Timing functions differ | Yes | Yes | Yes | Yes | Yes |
| Metadata syntax differs | Yes | Yes | Yes | Yes | Yes |
| Comment behaviour can differ | Yes | Yes | Yes | Yes | Yes |

Do not blindly reuse DBMS-specific syntax across systems.


# SQLMap Quick Reference

| Objective | Command |
|---|---|
| Basic GET | `sqlmap -u 'https://example.com/item?id=1'` |
| Specific parameter | `sqlmap -u 'https://example.com/item?id=1' -p id` |
| POST | `sqlmap -u 'https://example.com/search' --data='q=test'` |
| Burp request | `sqlmap -r request.txt` |
| Burp request parameter | `sqlmap -r request.txt -p id` |
| Non-interactive | `sqlmap -r request.txt -p id --batch` |
| Detailed help | `sqlmap -hh` |


# Burp Suite Quick Workflow

```text
Proxy
  |
  v
HTTP History
  |
  v
Interesting Database-Backed Request
  |
  v
Repeater
  |
  +--> Baseline
  |
  +--> Quote Probe
  |
  +--> True Condition
  |
  +--> False Condition
  |
  v
Comparer
  |
  v
Interpretation
  |
  v
Minimal Confirmation
```


# Source-Code Review Model

```text
                HTTP REQUEST
                     |
                     v
                  INPUT
                     |
                     v
               APPLICATION
                     |
                     v
              QUERY BUILDER
                     |
          +----------+----------+
          |                     |
          v                     v
   PARAMETERISED          CONCATENATED
       QUERY                  SQL
          |                     |
          v                     v
       LOWER RISK         REVIEW CANDIDATE
                                |
                                v
                         DATABASE EXECUTION
                                |
                                v
                           VALIDATION
```


# Secure Development Model

```text
                 USER INPUT
                     |
                     v
            BUSINESS VALIDATION
                     |
                     v
             SERVER-SIDE MAPPING
            /                   \
           /                     \
          v                       v
      DATA VALUE             IDENTIFIER
          |                       |
          v                       v
   PARAMETERISED QUERY        ALLOWLIST
          \                       /
           \                     /
            +---------+---------+
                      |
                      v
              DATABASE DRIVER
                      |
                      v
           LEAST-PRIVILEGED DB
```


# Final Testing Principle

The goal is not to send the largest number of SQL payloads.

The goal is to establish whether:

```text
USER-CONTROLLED DATA
        |
        v
CAN ALTER
        |
        v
DATABASE QUERY STRUCTURE
```

A defensible workflow is:

```text
Baseline
   |
   v
Identify Input
   |
   v
Controlled Probe
   |
   v
True / False Comparison
   |
   v
Repeat
   |
   v
Understand SQL Context
   |
   v
Minimal Confirmation
   |
   v
Determine Impact
   |
   v
Evidence
   |
   v
Remediation
   |
   v
Retest Root Cause
```

For every candidate ask:

```text
What parameter is being tested?

What was the baseline?

What exactly changed?

Can the behaviour be reproduced?

Does a true condition behave differently from a false condition?

Could application validation explain the difference?

Could a WAF explain it?

Could dynamic content explain it?

What SQL context is likely involved?

Which DBMS is involved?

What is the minimum evidence needed?

What privileges does the database account have?

Is sensitive data actually exposed?

Does the issue require authentication?

Is there a second-order path?

Does source code confirm unsafe construction?

Has the root cause been fixed with parameterisation?
```

The strongest SQL injection finding is not:

```text
SQLMap found SQLi.
```

It is:

```text
Input
  |
  v
Controlled SQL Behaviour
  |
  v
Repeatable Evidence
  |
  v
Security Consequence
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [curl Cheatsheet](curl.md)
- [Content Discovery Cheatsheet](content-discovery.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [Authentication](../web/authentication.md)
- [Authorisation](../web/authorisation.md)
- [API Security](../web/api-security.md)
- [GraphQL](../web/graphql.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - SQL Injection](https://portswigger.net/web-security/sql-injection){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for SQL Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection){ target="_blank" rel="noopener noreferrer" }
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [SQLMap Documentation](https://github.com/sqlmapproject/sqlmap/wiki){ target="_blank" rel="noopener noreferrer" }
- [SQLMap GitHub Repository](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }


!!! tip "Prove control, not just errors"

    A quote causing an error is a useful lead. A repeatable true/false comparison showing that the tested input controls database query behaviour is much stronger evidence.


!!! tip "Use the minimum proof necessary"

    Once SQL injection has been established, large-scale database extraction usually adds unnecessary risk. Demonstrate the security consequence with the smallest amount of data and activity required by the assessment.


!!! tip "Use source code when available"

    During white-box testing, trace request input into query construction and the database API. Parameterised execution is fundamentally different from concatenating user input into SQL strings.


!!! warning "Be careful with automation"

    SQLMap can generate substantial traffic and may test techniques with greater operational impact as its settings are increased. Understand the request and target before increasing automation levels or risk.


!!! warning "A WAF is not the root-cause fix"

    Blocking known SQL syntax can reduce exposure, but the application should still use parameterised queries and least-privileged database accounts. Retest the underlying query construction rather than only the original test string.
