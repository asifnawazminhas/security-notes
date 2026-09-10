---
title: sqlmap
description: Practical sqlmap reference for authorised SQL injection validation, request preparation, DBMS fingerprinting, parameter testing, evidence collection, false-positive analysis, operational safety, and integration with wider web application testing methodology.
---

# sqlmap

sqlmap is an automated SQL injection testing tool.

It can help identify and validate SQL injection conditions in authorised web applications and APIs.

Typical uses include:

- testing query-string parameters;
- testing form data;
- testing JSON bodies;
- testing cookies;
- testing selected HTTP headers;
- fingerprinting a database management system;
- confirming injectable parameters;
- automating repetitive SQL injection checks.

sqlmap should be used **after a plausible SQL injection candidate has been identified**.

A strong workflow is:

```text
Interesting Parameter
      |
      v
Manual SQLi Hypothesis
      |
      v
Controlled sqlmap Validation
      |
      v
Manual Confirmation
      |
      v
Evidence
      |
      v
Security Conclusion
```

!!! warning "Authorised testing only"
    Use sqlmap only against applications and databases that are explicitly authorised for testing. Some sqlmap capabilities can generate large request volumes, enumerate sensitive database information, modify data, write files, or perform operating-system interaction depending on the database and permissions. Start with low-impact validation and use intrusive functionality only when explicitly required and authorised.

---

# Where sqlmap Fits

sqlmap is not usually the first tool in a web application assessment.

A better sequence is:

```text
Application Mapping
      |
      v
Parameter Discovery
      |
      v
Manual Testing
      |
      v
SQL Injection Candidate
      |
      v
sqlmap
      |
      v
Controlled Validation
```

Related tools:

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

[ffuf](ffuf.md)

[Katana](katana.md)

---

# Official Project

Official project:

[sqlmap - GitHub](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }

Official site:

[sqlmap](https://sqlmap.org/){ target="_blank" rel="noopener noreferrer" }

Because sqlmap evolves over time, verify exact current syntax using:

```bash
sqlmap -h
```

For extended options:

```bash
sqlmap -hh
```

---

# Verify Installation

Check:

```bash
sqlmap --version
```

and:

```bash
sqlmap -h
```

On Kali Linux, sqlmap is commonly available through package management or may already be installed.

---

# What sqlmap Does

sqlmap automates SQL injection testing by sending modified requests and analysing response behaviour.

Conceptually:

```text
HTTP Request
    |
    v
Parameter
    |
    v
sqlmap Payloads
    |
    v
Application
    |
    v
Database
    |
    v
Response Differences
```

It attempts to determine whether user-controlled input can influence SQL execution.

---

# What sqlmap Does Not Prove Automatically

A positive-looking response does not automatically prove:

```text
Critical database compromise
```

The actual impact depends on:

- injectable context;
- database privileges;
- affected query;
- authentication;
- available controls;
- reachable data.

Do not overstate findings.

---

# Manual Testing First

Before using sqlmap, understand the parameter manually.

For example:

```text
GET /product?id=10
```

Questions include:

```text
Does changing id affect database-backed content?

Does a quote produce an application error?

Are there timing differences?

Is input numeric or string-based?

Does the application use an ORM?
```

Use Burp Repeater or curl to establish baseline behaviour.

---

# Baseline Request

A baseline request might be:

```http
GET /product?id=10 HTTP/1.1
Host: example.test
Cookie: session=<REDACTED>
```

Record the normal response before automated testing.

---

# Basic GET Parameter Testing

A simple sqlmap pattern is:

```bash
sqlmap -u "https://example.test/product?id=10"
```

sqlmap will identify parameters in the URL and test according to its selected options and defaults.

For production assessments, use deliberate scope and intensity settings rather than blindly accepting aggressive defaults.

---

# Specify a Parameter

If multiple parameters exist, focus on one.

Example:

```bash
sqlmap -u "https://example.test/product?id=10&lang=en" -p id
```

This reduces unnecessary testing.

---

# Why Parameter Selection Matters

Suppose the request contains:

```text
id
lang
sort
page
```

Testing all four may create unnecessary traffic.

If manual testing points to:

```text
id
```

start there.

---

# POST Form Testing

Example request body:

```text
username=test&search=book
```

A common pattern is:

```bash
sqlmap -u "https://example.test/search" --data="username=test&search=book" -p search
```

Use exact current syntax from:

```bash
sqlmap -h
```

---

# JSON Requests

APIs often use JSON.

Example:

```json
{
  "id": 10,
  "filter": "active"
}
```

For complex JSON, a raw request file from Burp is often clearer than manually reconstructing the request on the command line.

---

# Raw Request Files

One of the most useful sqlmap workflows is testing a raw HTTP request captured from Burp Suite.

Conceptually:

```text
Burp
 |
 v
Capture Valid Request
 |
 v
Save Request
 |
 v
sqlmap
```

This preserves:

- method;
- headers;
- cookies;
- body;
- content type.

---

# Request File Workflow

Save a valid request as:

```text
request.txt
```

Then use the current sqlmap request-file option documented by:

```bash
sqlmap -h
```

This is especially useful for:

- JSON;
- custom headers;
- authenticated requests;
- complex POST bodies.

---

# Burp Suite Integration

A strong workflow is:

```text
Burp Proxy
    |
    v
Capture Valid Request
    |
    v
Repeater
    |
    v
Manual SQLi Candidate
    |
    v
Save Raw Request
    |
    v
sqlmap
    |
    v
Manual Confirmation
```

Related tool:

[Burp Suite](burp-suite.md)

---

# Authentication

Authenticated endpoints require valid session context.

sqlmap may need:

- cookies;
- Authorization headers;
- custom headers.

Use only approved test accounts.

Protect live credentials and session values.

---

# Cookie-Based Sessions

A session might be represented as:

```text
Cookie: session=<REDACTED>
```

If the session expires during testing, results may become unreliable.

Symptoms can include:

```text
302 to login
401
403
generic login page
```

---

# Bearer Tokens

API requests may require:

```text
Authorization: Bearer <REDACTED>
```

Avoid storing live bearer tokens in public notes or shell history.

Prefer raw request files or controlled environment variables where appropriate.

---

# Role Context

A parameter may behave differently for:

```text
Unauthenticated user
Normal user
Administrator
```

Always record the current role.

A SQL injection reachable only by an administrator has a different risk profile than an unauthenticated one.

---

# CSRF Tokens

Some applications require changing CSRF values.

Static request replay may fail when:

```text
token expires
```

or:

```text
token must match session
```

If sqlmap cannot maintain the required workflow, manual testing or custom scripting may be more appropriate.

---

# Stateful Applications

sqlmap works best when a request can be replayed independently.

Complex workflows such as:

```text
Login
Get token
Create object
Submit query
Confirm operation
```

may require custom automation.

Do not force sqlmap into a workflow it cannot model reliably.

---

# Parameter Locations

Potential injectable input locations include:

```text
Query parameters
POST form fields
JSON values
Cookies
Selected headers
URI path segments
```

The input source must eventually influence SQL syntax for SQL injection to exist.

---

# SQL Injection Model

A simplified vulnerable flow is:

```text
User Input
   |
   v
String Concatenation
   |
   v
SQL Query
   |
   v
Database Execution
```

A safer flow is:

```text
User Input
   |
   v
Bound Parameter
   |
   v
Prepared Query
   |
   v
Database Execution
```

---

# ORM Does Not Automatically Prevent SQL Injection

Object-relational mapping libraries often provide safe parameterisation.

However, SQL injection can still occur through:

- raw query APIs;
- string-built filters;
- unsafe query fragments;
- dynamic order clauses;
- framework escape hatches.

Manual source review can help confirm the root cause.

---

# Error-Based Behaviour

One SQL injection indicator is database error behaviour.

Example concept:

```text
Normal input
      |
      v
Normal response

Quote / malformed input
      |
      v
Database-related error
```

A database-looking error is suggestive, not definitive.

---

# Generic Error Pages

Applications may return:

```text
500 Internal Server Error
```

for many malformed inputs.

Do not assume:

```text
500
=
SQL injection
```

Identify database-specific evidence or differential behaviour.

---

# Boolean-Based Behaviour

Boolean-based SQL injection may produce response differences based on a condition.

Conceptually:

```text
Condition TRUE
      |
      v
Response A

Condition FALSE
      |
      v
Response B
```

Differences may involve:

- page content;
- row count;
- status;
- response length.

sqlmap automates this analysis.

---

# Time-Based Behaviour

Time-based SQL injection relies on consistent delay differences.

Conceptually:

```text
Normal request:
~200 ms

Conditional delay request:
~5000 ms
```

Timing is noisy.

Confirm repeated behaviour before drawing conclusions.

---

# Network Noise

Timing can be affected by:

- latency;
- load balancer;
- WAF;
- backend load;
- database load;
- caching.

A single slow response proves nothing.

---

# UNION-Based Behaviour

UNION-based techniques may be possible where a query result is reflected in the application response.

The application context and database query structure determine whether this technique applies.

Do not use aggressive enumeration merely because UNION-based behaviour is possible.

---

# Stacked Queries

Some database/application combinations may allow multiple statements.

Support depends on:

- DBMS;
- driver;
- API;
- query context.

The existence of SQL injection does not mean stacked queries are supported.

---

# DBMS Fingerprinting

sqlmap may attempt to identify the backend DBMS.

Possible database platforms include:

```text
Microsoft SQL Server
MySQL / MariaDB
PostgreSQL
Oracle
SQLite
```

Confirm the result where important.

---

# Why DBMS Matters

Different DBMS platforms have different:

- syntax;
- functions;
- permissions;
- metadata;
- error messages;
- exploitation possibilities.

The backend database affects both testing and remediation.

---

# Version Detection

Database version detection may rely on behavioural or response characteristics.

Do not report an exact database version unless the evidence is sufficiently reliable.

---

# Database Privileges

An injectable query executes with the privileges of the database account used by the application.

This may be:

```text
read-only application account
```

or:

```text
highly privileged database account
```

These create very different impact.

---

# Least Privilege Matters

SQL injection impact is substantially reduced when the application account has only the permissions it requires.

The application should normally not use:

```text
database administrator
```

or equivalent broad privileges for routine operations.

---

# Database Enumeration

sqlmap can support database enumeration.

This is more intrusive than simply confirming injection.

Before enumerating:

```text
Do I need database names to prove the issue?

Do I need table names?

Do I need actual records?
```

Usually the minimum evidence is preferable.

---

# Minimal Proof Principle

Prefer:

```text
Confirm injection
Identify DBMS
Demonstrate controlled database response
```

over:

```text
Dump entire database
```

unless broader impact validation is explicitly required.

---

# Sensitive Data

Database enumeration may expose:

- personal data;
- credentials;
- financial records;
- health information;
- application secrets.

Stop unnecessary collection once the security impact is clear.

---

# Do Not Dump Everything

A vulnerability can often be demonstrated without exporting data.

For example:

```text
Controlled Boolean Difference
+
DBMS Identification
```

may be sufficient to confirm SQL injection.

---

# Metadata Before Data

Where additional validation is required, prefer metadata over real business data.

Conceptually:

```text
Database Version
Schema Name
Table Name
```

before:

```text
Customer Records
```

This reduces exposure.

---

# Row Limiting

If limited data retrieval is explicitly necessary, retrieve the minimum amount needed.

Do not collect thousands of records to demonstrate read access.

---

# Credential Tables

Avoid automatically dumping:

```text
users
credentials
passwords
```

simply because sqlmap can identify them.

The assessment objective should determine whether this is required.

---

# Password Hashes

Database password hashes are sensitive credential material.

Do not export or crack them unless explicitly authorised.

The SQL injection itself may already demonstrate sufficient impact.

---

# File Read Capabilities

Some database platforms and configurations may allow database users to read local files.

This depends on:

- DBMS;
- account permissions;
- database configuration;
- operating-system access.

Do not test filesystem access unless needed and authorised.

---

# File Write Capabilities

Writing files through the database is significantly more intrusive.

Do not use file-write features as routine SQL injection validation.

---

# Operating-System Interaction

Some SQL injection scenarios can potentially lead to operating-system interaction depending on:

- DBMS;
- privileges;
- configuration.

This crosses into a higher-impact test category.

Use only where explicitly authorised and necessary.

---

# SQL Injection vs RCE

Do not automatically write:

```text
SQL injection
=
Remote code execution
```

A more accurate model is:

```text
SQL Injection
      |
      v
Database Context
      |
      v
Database Privileges
      |
      v
Available Features
      |
      v
Possible Additional Impact
```

---

# Test Intensity

sqlmap exposes parameters commonly associated with how broadly and aggressively it tests.

Because exact behaviour and ranges can change, inspect:

```bash
sqlmap -hh
```

before using more aggressive settings.

Start with the lowest level needed to answer the question.

---

# Risk Settings

Some sqlmap options can increase the intrusiveness of payloads.

Do not raise them automatically.

Review what changes before using them against production.

---

# Level Settings

Higher testing levels can include more parameter locations and payload variations.

More is not always better.

If the suspected parameter is already known:

```text
focus on it
```

instead of testing the entire request.

---

# Request Count

sqlmap may send many requests while testing:

- techniques;
- DBMS possibilities;
- encodings;
- payload variations.

Monitor application stability and WAF response.

---

# Rate Limiting

Applications may return:

```text
429 Too Many Requests
```

Reduce test intensity.

Do not attempt to overwhelm defensive controls.

---

# WAF Detection

A WAF may:

- block quotes;
- block keywords;
- return generic 403 pages;
- reset connections;
- challenge requests.

This can produce false negatives or confusing behaviour.

Record the security control.

Do not automatically move into bypass testing.

---

# WAF vs Application Response

Compare:

```text
normal application response
```

with:

```text
blocked request response
```

If all candidate payloads receive the same WAF page, sqlmap may have insufficient visibility to determine the backend behaviour.

---

# Tamper Scripts

sqlmap includes mechanisms historically associated with transforming payloads.

These may be used to alter syntax or encoding.

Do not use them automatically to bypass WAF or filtering controls.

If evasion is specifically authorised, review the exact transformation before use.

---

# Evasion Is Separate From Validation

A useful distinction is:

```text
Can we confirm SQL injection?
```

versus:

```text
Can we evade this WAF?
```

These are different assessment objectives.

---

# Proxies

sqlmap can operate through proxy configurations.

This can be useful for:

- Burp inspection;
- controlled network routing.

Check current proxy syntax with:

```bash
sqlmap -h
```

Do not route high-volume sqlmap traffic through Burp unless there is a clear reason.

---

# Burp Proxying

A useful debugging workflow is:

```text
sqlmap
  |
  v
Burp Proxy
  |
  v
Target
```

This allows selected requests to be inspected.

However, it can create a very large Burp history.

---

# Request Comparison

When sqlmap identifies an injection point, manually compare:

```text
baseline
```

with:

```text
positive condition
```

and:

```text
negative condition
```

This provides understandable evidence.

---

# Manual Reproduction

A strong final finding should ideally be reproducible without depending on sqlmap.

Example:

```text
Normal request
      |
      v
Response A

Modified request
      |
      v
Consistent database-driven difference
```

Use Burp Repeater to demonstrate the smallest reliable difference.

---

# Evidence Quality

Weak:

```text
Screenshot:
sqlmap says injectable
```

Stronger:

```text
Baseline request
Modified request
Observed response difference
DBMS-related behaviour
sqlmap supporting output
```

The finding should remain understandable without the scanner.

---

# sqlmap Session Data

sqlmap may retain local state for tested targets.

This can improve repeated testing but may also cause confusion if:

- target changed;
- application was patched;
- authentication changed.

Be aware of cached session data during retesting.

---

# Fresh Retesting

When confirming remediation, ensure previous sqlmap state does not cause stale conclusions.

Use the tool's current documented mechanisms for fresh testing where necessary.

Also perform manual validation.

---

# Parameter Discovery

Do not use sqlmap as your primary hidden-parameter discovery tool.

Use:

- application analysis;
- Burp;
- ffuf;
- Katana;
- JavaScript analysis.

Then apply sqlmap to plausible SQL-backed parameters.

---

# ffuf Integration

A useful chain is:

```text
ffuf
  |
  v
Hidden Endpoint / Parameter
  |
  v
Manual Validation
  |
  v
SQLi Candidate
  |
  v
sqlmap
```

Related tool:

[ffuf](ffuf.md)

---

# Katana Integration

Katana may reveal:

```text
/report?id=123
/search?q=test
/api/user?uid=15
```

These are parameterized endpoints.

Do not automatically send all of them to sqlmap.

Prioritise based on:

- application behaviour;
- technology;
- manual response differences.

Related tool:

[Katana](katana.md)

---

# Nuclei Integration

Nuclei may flag a SQL injection candidate through a template.

A mature workflow is:

```text
Nuclei Candidate
      |
      v
Manual Review
      |
      v
sqlmap
      |
      v
Manual Confirmation
```

Related tool:

[Nuclei](nuclei.md)

---

# Source Code Review Integration

White-box access can substantially improve SQL injection testing.

Search for:

```text
raw SQL
string concatenation
query builders
unsafe ORM methods
```

Then identify the corresponding HTTP request.

Related section:

[Source Code Review Tools](../source-code-review/index.md)

---

# Source-to-Sink Model

A code-level SQL injection path might be:

```text
request.query["id"]
      |
      v
controller
      |
      v
service
      |
      v
"SELECT ... " + id
      |
      v
database execute
```

Dynamic sqlmap testing can then validate the code-level hypothesis.

---

# Prepared Statements

Prepared statements or parameter binding generally prevent data from altering SQL syntax when correctly used.

Example concept:

```text
SELECT * FROM users WHERE id = ?
```

with:

```text
id passed separately
```

is different from:

```text
"SELECT * FROM users WHERE id = " + id
```

---

# Dynamic Identifiers

Prepared statements may not directly parameterize certain SQL structural elements such as:

- table names;
- column names;
- sort direction.

Applications should use strict allowlists for such values.

sqlmap results should be interpreted in the actual query context.

---

# ORDER BY

User-controlled sorting can be security sensitive.

Example:

```text
sort=name
sort=date
```

If values are inserted directly into SQL syntax, parameter binding may not be sufficient.

Use strict server-side allowlists.

---

# LIMIT / OFFSET

Pagination parameters may also interact with SQL query construction.

Do not assume numeric-looking inputs are automatically safe.

---

# Search Fields

Search features frequently interact with database queries.

Potential parameters include:

```text
q
search
filter
keyword
name
```

Manual response analysis should precede automation.

---

# Login Forms

SQL injection in authentication logic can have different impact from SQL injection in a search function.

Possible impact may involve:

- authentication bypass;
- data access;
- database manipulation.

Test the exact behaviour.

---

# Authentication Bypass

Do not claim authentication bypass simply because the login parameter is injectable.

You must demonstrate that the query logic actually allows bypass of the intended authentication decision.

---

# API SQL Injection

APIs may return:

```text
JSON
```

rather than HTML.

Response differences may involve:

- status;
- field values;
- record count;
- error object;
- timing.

sqlmap can assist, but manual JSON comparison remains useful.

---

# GraphQL

GraphQL variables may eventually reach SQL-backed resolvers.

However, GraphQL introduces an additional abstraction layer.

Test the underlying resolver behaviour rather than blindly scanning every GraphQL request.

Related note:

[GraphQL](../../web/graphql.md)

---

# Second-Order SQL Injection

Some SQL injection conditions occur when data is stored first and used unsafely later.

Conceptually:

```text
User Input
   |
   v
Stored Safely
   |
   v
Later Retrieved
   |
   v
Unsafe SQL Construction
```

These workflows are harder for automated scanners.

Manual application understanding is important.

---

# Blind SQL Injection

Blind SQL injection may not return database errors or records directly.

Potential indicators include:

```text
boolean response differences
```

or:

```text
time differences
```

Automation can help, but reproducibility is critical.

---

# Out-of-Band SQL Injection

Some environments may support database-driven external interactions.

This is platform- and privilege-dependent.

Out-of-band testing is more intrusive and should only be used when explicitly required.

Related tool:

[Interactsh](interactsh.md)

---

# DNS / Network Interaction

If a database causes an external callback, determine:

```text
Which database feature caused it?

Which DB account privilege enabled it?

Which protocol was observed?

Was the interaction unique to the request?
```

Do not overstate the result.

---

# Error Handling

Applications should avoid exposing raw database errors.

However, hiding errors does not fix SQL injection.

Error suppression may turn an error-based injection into blind SQL injection.

The root control is safe query construction.

---

# Database Error Disclosure

Example exposed information may include:

```text
DBMS type
table name
column name
query fragment
filesystem path
```

This may be reportable as information disclosure separately from SQL injection if appropriate.

---

# Logging and Telemetry

sqlmap activity may generate:

- WAF logs;
- web-server logs;
- reverse-proxy logs;
- database errors;
- SIEM alerts.

Large automated runs can be very visible.

---

# Purple Teaming

sqlmap can support controlled detection validation for SQL injection attempts.

```text
Controlled SQLi Test
      |
      v
WAF / Web Logs
      |
      v
Application Logs
      |
      v
SIEM
      |
      v
Detection Review
```

Use a minimal, agreed test case rather than an unrestricted scan.

Related section:

[Purple Teaming](../../purple-teaming/index.md)

---

# Detection Considerations

Useful detection opportunities may include:

- unusual SQL metacharacters;
- repeated parameter mutations;
- error bursts;
- characteristic request patterns;
- high request rates.

Detection should not rely solely on a tool-specific User-Agent.

---

# False Positives

Potential causes include:

- unstable responses;
- dynamic content;
- WAF pages;
- caching;
- random timing variation;
- application errors unrelated to SQL;
- load balancer behaviour.

Manual reproduction is essential.

---

# False Negatives

sqlmap may miss SQL injection because of:

- authentication;
- complex workflows;
- unusual encoding;
- custom protocols;
- second-order behaviour;
- WAF blocking;
- custom query construction;
- uncommon DBMS behaviour.

A clean sqlmap result does not prove a parameter is safe.

---

# Dynamic Content

Pages containing:

```text
timestamps
random IDs
advertisements
personalised content
```

can make response comparison difficult.

Understand which parts of the page are stable.

---

# Caching

Caching can hide request differences.

Possible layers include:

- browser;
- CDN;
- reverse proxy;
- application cache.

Use unique requests or controlled cache behaviour where appropriate.

---

# Retesting

After remediation, test:

1. original manual proof;
2. modified values;
3. sqlmap where useful;
4. source change if white-box access exists.

The expected result is:

```text
User-controlled data can no longer influence SQL syntax.
```

---

# Remediation

Primary remediation usually involves:

- parameterized queries;
- prepared statements;
- safe ORM APIs;
- strict allowlists for SQL structural values;
- least-privileged database accounts.

Input validation can support these controls but should not replace safe query construction.

---

# Do Not Recommend Escaping Alone

Generic escaping can be fragile because SQL syntax differs across:

- DBMS;
- encoding;
- query context.

Use parameter binding wherever possible.

---

# Database Least Privilege

Application database accounts should receive only required permissions.

This reduces impact if SQL injection occurs.

For example:

```text
Read-only application
```

should not normally have:

```text
DROP
ALTER
CREATE USER
filesystem access
```

unless required.

---

# Stored Procedures

Stored procedures are not automatically safe.

They can still construct dynamic SQL unsafely.

Review how parameters are used inside them.

---

# WAF Is Defence in Depth

A WAF may block SQL injection payloads.

It should not be the primary remediation.

Correct the vulnerable query construction.

---

# Evidence Collection

For a confirmed finding, retain:

```text
Target:
Endpoint:
Parameter:
Method:
Authentication context:
Baseline request:
Modified request:
Observed difference:
sqlmap version:
sqlmap command:
DBMS:
Technique:
Timestamp:
Manual validation:
```

Protect sensitive database data.

---

# Evidence Example

```text
Target:
https://example.test

Endpoint:
/product

Parameter:
id

Authentication:
None

Manual validation:
Boolean conditions produced consistent differences in database-backed
content.

sqlmap:
Confirmed the same parameter as injectable.

DBMS:
PostgreSQL

Conclusion:
The id parameter influences SQL query structure without adequate
parameterisation.
```

---

# Reporting

Avoid:

```text
sqlmap found SQL injection.
```

Prefer:

```text
The `id` parameter was incorporated into a database query without
adequate parameterisation. Controlled boolean conditions produced
repeatable differences in the returned database-backed content,
confirming SQL injection.
```

---

# Reporting Limited Impact

If the vulnerable query uses a restricted account:

```text
SQL injection was confirmed, but the application database account was
restricted to read access within the affected schema during testing.
This reduced the demonstrated impact but did not remove the underlying
injection vulnerability.
```

---

# Reporting an Unconfirmed Candidate

Example:

```text
Automated testing initially suggested possible time-based SQL
injection. Repeated manual testing showed similar latency variation for
normal requests, and no deterministic database-controlled timing
difference could be established. The candidate was therefore not
confirmed.
```

---

# Reporting WAF Blocking

Example:

```text
SQL injection-style test inputs were blocked by the web application
firewall before reaching the application during the observed tests.
The result demonstrates current filtering behaviour but does not by
itself establish whether the underlying application query is safely
parameterised.
```

---

# Quick Command Reference

## Help

```bash
sqlmap -h
```

## Extended Help

```bash
sqlmap -hh
```

## Version

```bash
sqlmap --version
```

## Basic GET

```bash
sqlmap -u "https://example.test/product?id=10"
```

## Specific Parameter

```bash
sqlmap -u "https://example.test/product?id=10&lang=en" -p id
```

## POST Form

```bash
sqlmap -u "https://example.test/search" --data="search=book" -p search
```

For complex authenticated or JSON requests, prefer a valid raw HTTP request captured from Burp and use the request-file functionality documented by:

```bash
sqlmap -h
```

---

# sqlmap Checklist

## Preparation

- [ ] Target explicitly authorised.
- [ ] Endpoint understood.
- [ ] Parameter identified.
- [ ] Authentication context recorded.
- [ ] Baseline response captured.
- [ ] Manual SQLi hypothesis exists.
- [ ] sqlmap version recorded.
- [ ] Production sensitivity considered.

## Parameter Testing

- [ ] Specific parameter selected where possible.
- [ ] Query/form/JSON context understood.
- [ ] Data type understood.
- [ ] Dynamic response content considered.
- [ ] Manual baseline retained.

## Authentication

- [ ] Approved test account used.
- [ ] Cookie/token protected.
- [ ] Session expiry monitored.
- [ ] Role context documented.
- [ ] CSRF requirements understood.

## Intensity

- [ ] Lowest necessary test intensity used.
- [ ] Request volume monitored.
- [ ] Rate limiting respected.
- [ ] WAF behaviour observed.
- [ ] 500 spikes monitored.
- [ ] Testing stopped if instability appears.

## Validation

- [ ] sqlmap result manually reproduced.
- [ ] Generic error behaviour ruled out.
- [ ] Timing differences repeated.
- [ ] DBMS identification reviewed.
- [ ] Parameter influence established.
- [ ] Underlying SQL behaviour understood where possible.

## Data Access

- [ ] Database enumeration minimised.
- [ ] Sensitive rows not dumped unnecessarily.
- [ ] Credential tables avoided unless explicitly needed.
- [ ] File read/write avoided unless explicitly authorised.
- [ ] OS interaction avoided unless explicitly authorised.
- [ ] Collected data protected.

## WAF

- [ ] WAF blocking distinguished from application behaviour.
- [ ] Evasion not attempted automatically.
- [ ] Tamper functionality reviewed before use.
- [ ] Underlying vulnerability not assumed fixed by WAF.

## Evidence

- [ ] Endpoint retained.
- [ ] Parameter retained.
- [ ] Baseline request retained.
- [ ] Modified request retained.
- [ ] Response difference retained.
- [ ] sqlmap version retained.
- [ ] Command retained.
- [ ] DBMS retained where confirmed.
- [ ] Sensitive values redacted.
- [ ] Manual validation retained.

## Reporting

- [ ] Finding describes unsafe query behaviour.
- [ ] sqlmap output used only as supporting evidence.
- [ ] Impact not overstated.
- [ ] Database privileges considered.
- [ ] WAF treated as defence in depth.
- [ ] Remediation specifies parameterisation.
- [ ] Retest criteria explicit.

---

# Related Tool Notes

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

[ffuf](ffuf.md)

[Katana](katana.md)

[Nuclei](nuclei.md)

[Interactsh](interactsh.md)

---

# Related Source Review Tools

[Source Code Review Tools](../source-code-review/index.md)

[Semgrep](../../source-code-review/static-analysis/semgrep.md)

[OpenGrep](../../source-code-review/static-analysis/opengrep.md)

[CodeQL](../../source-code-review/static-analysis/codeql.md)

---

# Related Web Notes

[Web Application Security](../../web/index.md)

[Web Testing Methodology](../../web/methodology.md)

[Web Security Checklist](../../web/checklist.md)

[API Security](../../web/api-security.md)

[Authentication Testing](../../web/authentication.md)

[Authorisation Testing](../../web/authorisation.md)

[SQL Injection](../../web/sql-injection.md)

[GraphQL](../../web/graphql.md)

---

# External References

## sqlmap

[sqlmap](https://sqlmap.org/){ target="_blank" rel="noopener noreferrer" }

[sqlmap - GitHub](https://github.com/sqlmapproject/sqlmap){ target="_blank" rel="noopener noreferrer" }

## SQL Injection

[PortSwigger - SQL Injection](https://portswigger.net/web-security/sql-injection){ target="_blank" rel="noopener noreferrer" }

[OWASP - SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

## Practical References

[HackTricks - SQL Injection](https://book.hacktricks.wiki/en/pentesting-web/sql-injection/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use sqlmap like this:

```text
Find Parameter
      |
      v
Run Aggressive sqlmap
      |
      v
Dump Database
      |
      v
Report SQL Injection
```

Use it like this:

```text
Understand Endpoint
      |
      v
Identify Database-Backed Parameter
      |
      v
Capture Baseline Request
      |
      v
Perform Manual SQLi Checks
      |
      v
Form Injection Hypothesis
      |
      v
Run Focused sqlmap Validation
      |
      v
Understand Technique / DBMS
      |
      v
Reproduce Manually
      |
      v
Determine Database Privilege and Impact
      |
      v
Minimise Sensitive Data Access
      |
      v
Capture Evidence
      |
      v
Report Unsafe Query Construction
```

sqlmap is most valuable when it automates repetitive SQL injection testing after the tester already understands the request and suspected data flow.

The tool can help confirm and characterise the injection.

The final finding should be based on the underlying unsafe database interaction and reproducible evidence.
