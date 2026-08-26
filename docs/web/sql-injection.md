# SQL Injection

SQL Injection (SQLi) occurs when attacker-controlled input influences a database query in an unsafe manner.

SQL injection testing should not consist only of submitting common payloads. A structured approach first determines how an input affects application behaviour, whether the input is likely to interact with a database, what type of query may be involved, and how the application responds to controlled changes.

!!! warning "Authorised Security Testing"
    Perform SQL injection testing only against applications and systems for which you have explicit authorisation. These notes are intended for authorised penetration testing, lab environments, security research and responsible vulnerability disclosure.

---

## Objectives

The primary objectives of SQL injection testing are to determine:

- whether user-controlled input reaches a database query
- whether input is safely parameterised
- whether query structure can be influenced
- whether database errors are exposed
- whether responses change based on Boolean conditions
- whether query execution time can be influenced
- whether results from additional queries can be returned
- whether injection exists in less obvious locations such as headers or JSON
- which database technology is in use
- what security impact can be demonstrated safely

A useful mental model is:

```text
User Input
    ↓
Application
    ↓
Validation / Transformation
    ↓
Database Query
    ↓
Database
    ↓
Result
    ↓
Application Response
```

---

# SQL Injection Testing Workflow

A structured SQL injection assessment can generally follow:

```text
Discover Input
      ↓
Establish Baseline
      ↓
Determine Input Type
      ↓
Introduce Controlled Changes
      ↓
Compare Responses
      ↓
Look for SQL Behaviour
      ↓
Identify Injection Technique
      ↓
Fingerprint Database if Necessary
      ↓
Determine Impact
      ↓
Manually Verify
      ↓
Document
```

The important principle is:

> Understand how the parameter behaves before attempting complex SQL injection techniques.

---

# Common SQL Injection Locations

SQL injection may occur anywhere user-controlled data reaches a database query.

Common locations include:

```text
GET parameters
POST parameters
JSON properties
Search fields
Filters
Sorting parameters
Object identifiers
Login forms
Registration forms
API parameters
GraphQL arguments
Cookies
HTTP headers
Stored application data
```

Example:

```http
GET /products?id=123 HTTP/1.1
Host: target.example
```

Potential backend logic:

```sql
SELECT * FROM products WHERE id = 123;
```

The security question is whether the application safely separates the parameter value from the SQL query structure.

---

# Types of SQL Injection

Common SQL injection categories include:

```text
Error-Based SQL Injection
Boolean-Based Blind SQL Injection
Time-Based Blind SQL Injection
UNION-Based SQL Injection
Stacked Queries
Second-Order SQL Injection
Out-of-Band SQL Injection
```

Not every database or application architecture supports every technique.

---

# Start With a Baseline

Before modifying a parameter, send the original request.

Example:

```http
GET /product?id=10 HTTP/1.1
Host: target.example
```

Record:

```text
Status code
Response length
Response body
Response time
Error messages
Returned records
Redirect behaviour
```

Example:

```text
Status: 200
Length: 4821
Response Time: 142 ms
Product: Test Product
```

This becomes the baseline.

---

# Input Type Identification

Determine the apparent data type.

Examples:

```text
?id=123
```

likely represents a numeric value.

```text
?username=alice
```

likely represents a string.

```text
?date=2026-08-26
```

may be handled as a date.

```text
?sort=name
```

may influence an SQL identifier or `ORDER BY` clause.

The apparent type can help you reason about the likely backend query.

---

# Controlled Character Testing

Start with small changes rather than complicated payloads.

Interesting characters can include:

```text
'
"
`
\
;
(
)
```

For example:

```text
?id=10'
```

Compare the result with:

```text
?id=10
```

Look for:

```text
Database errors
HTTP 500
Different content
Different response length
Different record count
Unexpected redirects
Different response time
```

A single quote causing an error is an indicator, not proof of SQL injection.

---

# Error-Based SQL Injection

Error-based SQL injection occurs when database errors reveal information about query processing.

Malformed input may result in messages containing references to:

```text
SQL syntax
Database drivers
Table names
Column names
Query fragments
Database functions
```

Potential database indicators include:

```text
MySQL
MariaDB
PostgreSQL
Microsoft SQL Server
Oracle
SQLite
```

---

## Error-Based Workflow

```text
Baseline Request
      ↓
Modify Parameter
      ↓
Application Error?
      ↓
Database Error?
      ↓
Identify DBMS Clues
      ↓
Determine Whether Query Structure Is Influenced
      ↓
Manual Verification
```

Do not rely solely on verbose error messages.

Production applications often suppress database errors.

---

# Boolean-Based SQL Injection

Boolean-based SQL injection identifies situations where application behaviour changes depending on whether an injected condition evaluates to true or false.

The general concept is:

```text
Original Query
     ↓
TRUE Condition
     ↓
Response A

Original Query
     ↓
FALSE Condition
     ↓
Response B
```

You are looking for a reliable difference between the two responses.

---

## Boolean Comparison

Compare:

```text
Baseline
TRUE condition
FALSE condition
```

Observe:

```text
Status
Length
Words
Lines
Returned objects
Page content
Redirects
JSON fields
```

A useful pattern is:

```text
Baseline ≈ TRUE
FALSE ≠ Baseline
```

This may indicate that the condition is influencing database logic.

---

# Blind SQL Injection

Blind SQL injection occurs when the application does not directly display database errors or injected query output.

Information is instead inferred from application behaviour.

Common forms include:

```text
Boolean-Based Blind SQL Injection
Time-Based Blind SQL Injection
Out-of-Band SQL Injection
```

The absence of database errors does not mean SQL injection is absent.

---

# Time-Based Blind SQL Injection

Time-based testing determines whether database processing can influence response time.

Conceptually:

```text
Normal Request
     ↓
Normal Response Time

Controlled Database Delay
     ↓
Consistently Delayed Response
```

A single slow response is not sufficient evidence.

Network latency, application load, caching and backend processing can all affect timing.

---

## Time-Based Testing Workflow

```text
Measure Baseline
      ↓
Repeat Baseline
      ↓
Determine Normal Variation
      ↓
Introduce Controlled Timing Test
      ↓
Repeat Test
      ↓
Compare Results
      ↓
Verify Correlation
```

Collect several measurements before reaching a conclusion.

---

# UNION-Based SQL Injection

`UNION` allows results from compatible SQL queries to be combined.

Conceptually:

```sql
SELECT name, price
FROM products

UNION

SELECT value1, value2;
```

For `UNION` injection to work, the queries generally need compatible:

```text
Column counts
Data types
Query structure
```

A typical testing process therefore involves determining the structure of the original result set.

---

# Determining Column Count

Two common concepts used during authorised testing are:

```text
ORDER BY behaviour
UNION column matching
```

The objective is to understand how many columns are present in the original query.

Conceptually:

```text
Original Query
      ↓
Determine Column Count
      ↓
Determine Displayed Columns
      ↓
Determine Compatible Types
      ↓
Assess Accessible Data
```

Avoid extracting unnecessary sensitive data.

Proof should be limited to what is required to demonstrate the vulnerability.

---

# Displayed Columns

Even if a query contains several columns, not all values may be displayed in the HTTP response.

Conceptually:

```text
Database Result
   ↓
Application Processing
   ↓
Selected Values
   ↓
HTML / JSON Response
```

Identify which output positions are actually observable.

---

# Stacked Queries

Some database technologies and drivers permit multiple statements within one database call.

Conceptually:

```sql
QUERY 1;
QUERY 2;
```

Support varies by:

```text
DBMS
Driver
Application framework
Database API
Configuration
```

Because stacked queries may perform state-changing operations, avoid destructive validation.

---

# Second-Order SQL Injection

Second-order SQL injection occurs when malicious or unsafe input is stored safely at one point but later used unsafely in another database query.

Example:

```text
User Input
    ↓
Stored in Database
    ↓
No Immediate Vulnerability
    ↓
Different Application Function
    ↓
Stored Value Used in SQL Query
    ↓
SQL Injection
```

This is conceptually similar to stored XSS because the vulnerable processing occurs later.

---

## Second-Order Testing Locations

Interesting areas include:

```text
Usernames
Display names
Profile information
Organisation names
Address fields
Imported data
CSV data
Administrative notes
Stored search filters
Application configuration
```

The key question is:

> Where is this value used later?

---

# SQL Injection in Authentication

Login functionality frequently interacts directly with database queries.

Example:

```http
POST /login HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

username=test&password=Password123
```

A secure application should use parameterised queries.

Unsafe conceptual logic might resemble:

```sql
SELECT *
FROM users
WHERE username = 'USER_INPUT'
AND password = 'PASSWORD_INPUT';
```

Testing should determine whether user input can alter the intended authentication query.

---

# Search Functionality

Search endpoints are common SQL injection candidates.

Example:

```http
GET /search?q=laptop HTTP/1.1
```

Potential backend logic:

```sql
SELECT *
FROM products
WHERE name LIKE '%USER_INPUT%';
```

Search functionality may place input inside:

```text
LIKE expressions
Full-text queries
Dynamic filters
Multiple database conditions
```

The surrounding query context may differ from a simple object identifier.

---

# Filter Parameters

Modern applications frequently expose filtering functionality:

```text
category
status
type
price
date
country
role
```

Example:

```text
/products?category=laptops&sort=price
```

Each parameter may influence a different part of the query.

Do not test only obvious identifiers.

---

# ORDER BY Injection

Sorting parameters deserve separate attention.

Example:

```text
?sort=name
```

Potential backend logic:

```sql
SELECT *
FROM users
ORDER BY name;
```

Applications sometimes parameterise values correctly while dynamically concatenating:

```text
Column names
Sort directions
Table names
```

These locations require careful review because SQL parameterisation works differently for identifiers than for normal values.

---

# JSON SQL Injection

Modern APIs frequently receive JSON.

Example:

```http
POST /api/search HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "query": "laptop",
  "category": "electronics"
}
```

Test each property independently.

```text
query
category
sort
filter
page
limit
```

Do not assume JSON input is inherently safe.

---

# Nested JSON

Input may be nested:

```json
{
  "filter": {
    "username": "alice",
    "status": "active"
  }
}
```

Map each controllable value:

```text
filter.username
filter.status
```

Automated tools sometimes require additional configuration to correctly test nested structures.

---

# SQL Injection in HTTP Headers

Applications may use HTTP headers in database operations.

Potential candidates include:

```text
User-Agent
Referer
X-Forwarded-For
X-Real-IP
X-Forwarded-Host
Custom application headers
Tracking headers
```

Example:

```text
HTTP Request
     ↓
User-Agent
     ↓
Application Logging
     ↓
Database INSERT
```

Start with harmless markers and controlled syntax changes.

---

# SQL Injection in Cookies

Cookies may also reach database queries.

Example:

```http
Cookie: trackingId=12345
```

Potential uses include:

```text
Tracking
Preferences
Session lookup
Analytics
Shopping carts
A/B testing
```

Do not restrict SQL injection testing to URL and body parameters.

---

# SQL Injection in APIs

API testing should include:

```text
REST
GraphQL
JSON APIs
XML APIs
Mobile backends
Internal APIs
```

A practical API workflow:

```text
Map Endpoint
      ↓
Identify Parameters
      ↓
Determine Types
      ↓
Baseline
      ↓
Controlled Input Changes
      ↓
Compare Responses
      ↓
Investigate Database Behaviour
```

---

# GraphQL and SQL Injection

GraphQL provides structured queries but backend resolvers may still construct unsafe database queries.

Example:

```graphql
query {
  user(name: "alice") {
    id
    email
  }
}
```

The GraphQL layer itself does not automatically guarantee safe database access.

Trace:

```text
GraphQL Argument
      ↓
Resolver
      ↓
ORM / Database Query
```

---

# ORM Considerations

Applications frequently use Object Relational Mapping libraries.

Examples include:

```text
Hibernate
Entity Framework
SQLAlchemy
Sequelize
Prisma
Django ORM
ActiveRecord
Doctrine
```

ORM usage reduces some SQL injection risks when used correctly, but unsafe raw queries can still introduce vulnerabilities.

Look for:

```text
Raw SQL
String concatenation
Dynamic query construction
Unsafe filters
Dynamic ORDER BY
Custom database functions
```

---

# Source Code Review

When source code is available, identify where user-controlled input reaches database operations.

Conceptually:

```text
Source
  ↓
Transformation
  ↓
Validation
  ↓
Database Sink
```

Example:

```text
request parameter
      ↓
controller
      ↓
service
      ↓
repository
      ↓
SQL query
```

---

# Search Source Code for SQL Operations

Useful search terms include:

```text
SELECT
INSERT
UPDATE
DELETE
execute
query
rawQuery
createNativeQuery
Statement
PreparedStatement
```

Example:

```bash
grep -RniE \
'SELECT|INSERT|UPDATE|DELETE|execute\(|query\(|rawQuery|createNativeQuery|Statement|PreparedStatement' \
.
```

Then determine whether attacker-controlled data reaches those locations.

---

# Dangerous Pattern

Conceptual unsafe pattern:

```python
query = "SELECT * FROM users WHERE username = '" + username + "'"
```

The problem is that user-controlled data becomes part of SQL syntax.

---

# Safer Pattern

Use parameterised queries.

Conceptually:

```python
cursor.execute(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)
```

The exact syntax depends on the database library.

The important principle is:

```text
SQL Structure
      +
Parameter Values
```

should remain separate.

---

# Burp Suite SQL Injection Workflow

A practical Burp workflow:

```text
Proxy
  ↓
HTTP History
  ↓
Identify Interesting Request
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Modify One Parameter
  ↓
Compare Response
  ↓
Identify SQL Behaviour
  ↓
Manual Verification
```

---

# Burp Repeater

Repeater should generally be the primary manual testing tool.

For each parameter:

```text
1. Send original request
2. Record baseline
3. Modify one value
4. Send again
5. Compare
6. Restore original
7. Test next hypothesis
```

Keep testing controlled.

---

# Burp Comparer

Comparer can help identify subtle response differences.

Compare:

```text
Baseline vs modified input

TRUE condition vs FALSE condition

Normal request vs suspected SQL behaviour
```

Useful differences include:

```text
Words
HTML
JSON
Headers
Returned records
```

---

# Burp Intruder

Intruder can help test multiple controlled values.

```text
Repeater
   ↓
Understand Parameter
   ↓
Send to Intruder
   ↓
Select Payload Position
   ↓
Configure Small Payload Set
   ↓
Run
   ↓
Sort Responses
   ↓
Identify Outliers
   ↓
Repeater
   ↓
Manual Verification
```

Useful columns include:

```text
Status
Length
Words
Lines
Time
```

---

# Response Analysis

Do not look only at HTTP status codes.

Compare:

```text
Status
Content length
Word count
Line count
Response body
JSON properties
Record count
Error message
Redirect location
Response time
Application state
```

A SQL injection indicator may be extremely subtle.

---

# Database Fingerprinting

If SQL injection has been established, identifying the DBMS may help select appropriate validation techniques.

Potential technologies include:

```text
MySQL
MariaDB
PostgreSQL
Microsoft SQL Server
Oracle
SQLite
```

Fingerprinting can use:

```text
Error messages
Database-specific syntax
Application technology
HTTP headers
Source code
Dependency files
Known platform architecture
```

Avoid unnecessary fingerprinting if the vulnerability can already be demonstrated safely.

---

# SQLMap

`sqlmap` can automate SQL injection detection and validation during authorised testing.

Basic usage:

```bash
sqlmap -u "https://target.example/product?id=10"
```

Specify the parameter:

```bash
sqlmap -u "https://target.example/product?id=10" -p id
```

---

## SQLMap With a Burp Request

Save a complete HTTP request from Burp as:

```text
request.txt
```

Then:

```bash
sqlmap -r request.txt
```

This preserves:

```text
Method
Headers
Cookies
POST body
JSON
Authentication
Parameters
```

Specify a particular parameter:

```bash
sqlmap -r request.txt -p id
```

---

## SQLMap Workflow

```text
Manual Discovery
      ↓
Burp Repeater
      ↓
Suspicious Parameter
      ↓
Save request.txt
      ↓
sqlmap
      ↓
Review Results
      ↓
Manual Verification
      ↓
Minimal Impact Demonstration
```

Do not automatically report a finding solely because sqlmap identifies a parameter as potentially injectable.

---

# Ghauri

Ghauri is an automated SQL injection detection and exploitation tool.

It can be useful as an alternative or complementary tool to sqlmap when investigating suspected SQL injection.

GitHub:

https://github.com/r0oth3x49/ghauri

---

## Install Ghauri

Clone the repository:

```bash
git clone https://github.com/r0oth3x49/ghauri.git
cd ghauri
```

Install:

```bash
python3 -m pip install -e .
```

Check:

```bash
ghauri -h
```

---

## Basic Ghauri Testing

Test an authorised target:

```bash
ghauri -u "https://target.example/product?id=10"
```

Specify the parameter:

```bash
ghauri -u "https://target.example/product?id=10" -p id
```

---

## Ghauri With a Burp Request

Save the request from Burp as:

```text
request.txt
```

Then:

```bash
ghauri -r request.txt
```

Specify the interesting parameter:

```bash
ghauri -r request.txt -p id
```

This can be particularly useful for requests containing:

```text
POST parameters
Cookies
Authentication
Custom headers
JSON
Complex request bodies
```

---

## Ghauri Workflow

```text
Application
     ↓
Burp Proxy
     ↓
Identify Interesting Parameter
     ↓
Burp Repeater
     ↓
Manual SQLi Testing
     ↓
Save Request
     ↓
Ghauri
     ↓
Review Detection
     ↓
Manual Verification
     ↓
Document Finding
```

---

# HBSQLI

HBSQLI is another SQL injection testing project that can complement manual SQL injection testing and other automated tools.

GitHub:

https://github.com/SAPT01/HBSQLI

Because specialist SQL injection tools can differ in the techniques and request patterns they handle, HBSQLI can provide an additional testing option when manually observed behaviour deserves further investigation.

Always review the project's current documentation and supported options before using it because command-line interfaces and capabilities may change between versions.

---

## Install HBSQLI

Clone the repository:

```bash
git clone https://github.com/SAPT01/HBSQLI.git
cd HBSQLI
```

Review the project files:

```bash
ls -la
```

Read the current documentation:

```bash
cat README.md
```

Then follow the installation instructions provided by the project.

Do not assume installation or command-line options from unrelated SQL injection tools are compatible with HBSQLI.

---

## HBSQLI Workflow

A sensible workflow is:

```text
Interesting Parameter
        ↓
Burp Repeater
        ↓
Manual SQLi Analysis
        ↓
Suspicious Behaviour
        ↓
HBSQLI
        ↓
Review Results
        ↓
Manual Verification
        ↓
Document Evidence
```

HBSQLI should complement rather than replace manual analysis.

---

# Using Multiple SQL Injection Tools

Different SQL injection tools may produce different results depending on:

```text
Request format
Injection context
Database technology
Response behaviour
Authentication
Filtering
WAF behaviour
Timing
Tool detection logic
```

Therefore, a useful workflow is:

```text
                    Burp Suite
                        ↓
                  Manual Testing
                        ↓
              Suspicious Parameter
                        ↓
              ┌─────────┼─────────┐
              │         │         │
              ▼         ▼         ▼
           sqlmap     Ghauri     HBSQLI
              │         │         │
              └─────────┼─────────┘
                        ↓
                 Compare Results
                        ↓
               Manual Verification
                        ↓
               Minimal Evidence
                        ↓
                     Report
```

Do not simply run every tool against every parameter.

Use automation after manual testing identifies something worth investigating.

---

# Recommended SQLi Tool Workflow

```text
Burp Proxy
     ↓
Map Parameters
     ↓
Burp Repeater
     ↓
Baseline
     ↓
Manual SQLi Testing
     ↓
Suspicious Behaviour?
     ↓
Save request.txt
     ↓
┌──────────┬──────────┬──────────┐
│          │          │          │
▼          ▼          ▼          │
sqlmap   Ghauri     HBSQLI       │
│          │          │          │
└──────────┴──────────┴──────────┘
               ↓
        Compare Findings
               ↓
        Manual Reproduction
               ↓
      Determine Actual Impact
               ↓
       Collect Minimal Evidence
               ↓
             Report
```

---

# Data Extraction

Once SQL injection is confirmed, it may technically be possible to retrieve database information.

During professional testing, apply data minimisation.

Prefer demonstrating:

```text
Current database name
Database version
Current database user
Known test record
```

rather than retrieving:

```text
Password databases
Personal information
Production customer data
Large tables
Sensitive business information
```

Stop once sufficient evidence has been collected.

---

# Out-of-Band SQL Injection

Some database systems can generate network interactions.

Conceptually:

```text
SQL Injection
     ↓
Database
     ↓
Network Interaction
     ↓
Controlled Callback Service
```

This can sometimes help identify blind SQL injection when HTTP responses provide no useful signal.

Out-of-band techniques depend heavily on:

```text
DBMS
Privileges
Network access
Configuration
Environment
```

Use controlled callback infrastructure during authorised testing.

---

# WAF Behaviour

A WAF may interfere with SQL injection testing.

Indicators include:

```text
403 responses
Connection termination
Generic security pages
Parameter-specific blocking
Rate limiting
Different behaviour for SQL keywords
```

Separate:

```text
WAF Behaviour
```

from:

```text
Application Behaviour
```

A WAF blocking one test does not prove that the underlying query is safe.

---

# Encoding and Normalisation

Applications may perform:

```text
URL decoding
Unicode normalisation
JSON decoding
HTML entity decoding
Framework-specific transformations
Database driver escaping
```

Think about the complete processing chain:

```text
HTTP Request
      ↓
Reverse Proxy
      ↓
Web Framework
      ↓
Validation
      ↓
Transformation
      ↓
ORM / Database Library
      ↓
Database
```

Different layers may interpret the same input differently.

---

# False Positives

Common causes of false SQL injection indicators include:

```text
Generic application errors
WAF blocking
Input validation
Template errors
Backend API failures
Caching
Network latency
Rate limiting
Search engine behaviour
Application-specific filtering
```

Always reproduce manually.

---

# Validation

A high-quality SQL injection finding should establish:

```text
Source
 ↓
Affected Parameter
 ↓
Database Interaction
 ↓
Controllable Query Behaviour
 ↓
Security Impact
```

Avoid relying solely on:

```text
A quote caused HTTP 500
```

or:

```text
An automated tool reported SQL injection
```

Demonstrate reliable database-dependent behaviour.

---

# Evidence Collection

Useful evidence includes:

```text
Affected endpoint
HTTP method
Affected parameter
Authentication requirement
Baseline request
Modified request
Baseline response
Modified response
Database error if relevant
Boolean difference if relevant
Timing measurements if relevant
Identified DBMS
Tool output if used
Manual reproduction
Security impact
```

---

# Timing Evidence

For time-based findings, record multiple measurements.

Example:

| Request | Baseline | Test |
|---|---:|---:|
| 1 | 140 ms | 5.1 s |
| 2 | 153 ms | 5.2 s |
| 3 | 147 ms | 5.1 s |
| 4 | 161 ms | 5.2 s |

Repeated and predictable behaviour is considerably stronger evidence than a single slow request.

---

# SQL Injection Reporting

A report should explain:

```text
Where input originates
Which parameter is affected
How the input reaches the database
Which SQL injection technique was confirmed
How the behaviour was validated
Which DBMS is involved if known
What an attacker could achieve
What evidence was collected
How the vulnerability should be remediated
```

---

# Example Finding Structure

```text
Title
SQL Injection in Product Identifier

Affected Endpoint
GET /product

Affected Parameter
id

Authentication Required
No

Technique
Boolean-Based SQL Injection

Description
The product identifier is incorporated into a database query without
sufficient separation between user-controlled input and SQL syntax.

Testing demonstrated repeatable differences between logically true and
false database conditions.

Impact
An attacker may be able to influence database queries and access
information outside the intended application functionality.

Recommendation
Replace dynamically constructed SQL queries with parameterised queries
or prepared statements and ensure database permissions follow the
principle of least privilege.
```

---

# Remediation

The primary defence against SQL injection is:

```text
Parameterised Queries
Prepared Statements
```

Additional controls include:

```text
Safe ORM usage
Input validation
Least-privileged database accounts
Avoiding dynamic SQL
Safe handling of ORDER BY and identifiers
Secure error handling
Database segmentation
Monitoring
WAF as defence in depth
```

---

# Dynamic SQL Identifiers

Prepared statements generally protect values, but developers sometimes need dynamic:

```text
Column names
Table names
Sort directions
```

Do not concatenate arbitrary user input.

Use an allowlist:

```text
User requests sort=name
      ↓
Application checks allowlist
      ↓
name → approved database column
```

Example allowlist:

```text
name
price
created_at
```

Anything else should be rejected.

---

# Least Privilege

The application database account should have only the permissions required by the application.

Avoid unnecessary:

```text
Administrative database privileges
Filesystem access
Operating-system integration
Cross-database access
Schema modification
User creation
```

SQL injection impact can be significantly reduced by appropriate database permissions.

---

# Error Handling

Avoid exposing verbose database errors to users.

Instead of:

```text
SQL syntax error near ...
```

return a generic application error while recording technical details securely in server-side logs.

Error suppression does not fix SQL injection, but it reduces unnecessary information disclosure.

---

# SQL Injection Testing Checklist

## Discovery

- [ ] Identify GET parameters
- [ ] Identify POST parameters
- [ ] Identify JSON properties
- [ ] Identify GraphQL arguments
- [ ] Identify cookies
- [ ] Identify interesting HTTP headers
- [ ] Identify search functionality
- [ ] Identify filters
- [ ] Identify sorting
- [ ] Identify login functionality
- [ ] Identify stored input
- [ ] Identify API endpoints

## Baseline

- [ ] Record status
- [ ] Record response length
- [ ] Record response body
- [ ] Record response time
- [ ] Record returned objects
- [ ] Record normal errors

## Initial Testing

- [ ] Determine input type
- [ ] Test controlled syntax changes
- [ ] Test single quote handling
- [ ] Test double quote handling where relevant
- [ ] Compare response differences
- [ ] Look for database errors
- [ ] Look for application errors

## Techniques

- [ ] Error-based behaviour
- [ ] Boolean-based behaviour
- [ ] Time-based behaviour
- [ ] UNION behaviour where relevant
- [ ] Second-order behaviour
- [ ] Out-of-band behaviour where appropriate

## Locations

- [ ] Query parameters
- [ ] POST body
- [ ] JSON
- [ ] Cookies
- [ ] HTTP headers
- [ ] Search
- [ ] Filters
- [ ] Sorting
- [ ] APIs
- [ ] GraphQL
- [ ] Stored values

## Automation

- [ ] Confirm parameter manually
- [ ] Save Burp request
- [ ] Test with sqlmap where appropriate
- [ ] Test with Ghauri where appropriate
- [ ] Consider HBSQLI where appropriate
- [ ] Start conservatively
- [ ] Review automated output
- [ ] Compare tool results
- [ ] Manually reproduce findings

## Validation

- [ ] Confirm repeatability
- [ ] Exclude WAF behaviour
- [ ] Exclude network timing variation
- [ ] Confirm database-dependent behaviour
- [ ] Minimise extracted data
- [ ] Determine actual impact
- [ ] Capture evidence

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | Request interception and SQL injection testing |
| Burp Repeater | Manual SQL injection validation |
| Burp Intruder | Controlled parameter testing |
| Burp Comparer | Response comparison |
| Burp Scanner | Automated testing where available |
| sqlmap | Automated SQL injection detection and validation |
| Ghauri | Automated SQL injection detection and exploitation |
| HBSQLI | Additional SQL injection testing and research |
| Browser DevTools | Frontend and API analysis |
| curl | Manual HTTP requests |
| grep / ripgrep | Source code and SQL sink discovery |

---

# Quick Reference

```text
A quote causing an error does not prove SQL injection.

An HTTP 500 response does not prove SQL injection.

A slow request does not prove time-based SQL injection.

Automated tool output should be manually verified.

A WAF blocking SQL syntax does not prove the application is secure.

ORM usage does not automatically eliminate SQL injection.

JSON APIs can still contain SQL injection.

GraphQL can still contain SQL injection.

Always establish:

INPUT → APPLICATION → QUERY → DATABASE BEHAVIOUR → IMPACT
```

---

# Practical Workflow Summary

```text
                    ┌─────────────────────┐
                    │   Discover Input    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Establish Baseline  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Determine Type      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Controlled Changes  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Compare Responses   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Identify Technique  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Targeted Automation │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Manual Verification │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Evidence + Report   │
                    └─────────────────────┘
```

---

# References

## PortSwigger Web Security Academy

### SQL Injection

https://portswigger.net/web-security/sql-injection

PortSwigger's SQL injection material covering detection, exploitation concepts, database-specific behaviour and practical labs.

### SQL Injection Cheat Sheet

https://portswigger.net/web-security/sql-injection/cheat-sheet

Useful database-specific SQL syntax reference.

---

## OWASP

### SQL Injection Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

### Query Parameterization Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Query_Parameterization_Cheat_Sheet.html

### Injection Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html

---

## PayloadsAllTheThings

### SQL Injection

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection

Use large payload collections as references after understanding the affected query context rather than blindly sending every payload.

---

## HackTricks

### SQL Injection

https://book.hacktricks.wiki/en/pentesting-web/sql-injection/index.html

---

## sqlmap

Official project:

https://github.com/sqlmapproject/sqlmap

Documentation:

https://github.com/sqlmapproject/sqlmap/wiki

---

## Ghauri

Official project:

https://github.com/r0oth3x49/ghauri

Ghauri provides automated SQL injection detection and exploitation capabilities and can complement sqlmap during authorised testing.

---

## HBSQLI

Project:

https://github.com/SAPT01/HBSQLI

Review the project's current README and documentation for installation, supported SQL injection techniques and current command-line usage.

---

# Related Notes

```text
Web Application Security
├── Methodology
├── Pentesting Checklist
├── Reconnaissance
│   ├── Subdomain Enumeration
│   ├── Technology Identification
│   ├── Content Discovery
│   ├── Parameter Discovery
│   └── JavaScript Analysis
├── Authentication
├── Authorisation
├── Session Management
├── Burp Suite
│   ├── Extensions
│   └── Testing Workflows
├── Cross-Site Scripting
└── SQL Injection
```

The methodology, parameter discovery, technology identification and Burp Suite workflow notes are particularly useful before SQL injection testing.
