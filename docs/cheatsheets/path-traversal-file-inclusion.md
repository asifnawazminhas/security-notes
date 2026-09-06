---
title: Path Traversal and File Inclusion Cheatsheet
description: Practical path traversal, local file inclusion and remote file inclusion cheatsheet for authorised web application security testing, covering discovery, encoding, validation, source review, Burp Suite workflows, evidence, remediation and retesting.
---

# Path Traversal and File Inclusion Cheatsheet

Path traversal occurs when attacker-controlled input influences a filesystem path and allows access outside the directory intended by the application.

Related vulnerabilities include:

```text
Path Traversal

Directory Traversal

Local File Inclusion (LFI)

Remote File Inclusion (RFI)

Arbitrary File Read

Unsafe File Download

Unsafe File Write
```

These issues are related but should not automatically be treated as equivalent.

A simplified path traversal flow is:

```text
User Input
    |
    v
File Parameter
    |
    v
Application Path Construction
    |
    v
Filesystem
    |
    v
Unexpected File
```

Example:

```text
GET /download?file=report.pdf
```

Application logic:

```text
/var/www/files/ + report.pdf
```

Expected result:

```text
/var/www/files/report.pdf
```

If traversal is possible:

```text
/var/www/files/ + ../../etc/hostname
```

the resolved path may become:

```text
/etc/hostname
```

!!! warning "Authorised Security Testing"

    Perform path traversal and file inclusion testing only against systems explicitly included in the assessment scope. Start with harmless known files and application-owned resources. Do not access credentials, private keys, tokens, personal data or other sensitive files unless that level of validation is explicitly authorised.


# Quick Reference

## Common Parameters

```text
file

filename

path

filepath

page

template

include

document

download

attachment

resource

folder

directory

dir

image

img

view

theme

lang

language

locale

content
```


## Basic Linux Traversal

```text
../../../etc/hostname
```


## Basic Windows Traversal

```text
..\..\..\Windows\win.ini
```


## URL-Encoded Traversal

```text
..%2f..%2f..%2f
```

Windows-style:

```text
..%5c..%5c..%5c
```


## Double-Encoded Traversal

```text
..%252f..%252f..%252f
```


## Absolute Linux Path

```text
/etc/hostname
```


## Absolute Windows Path

```text
C:\Windows\win.ini
```


# Testing Model

Do not use:

```text
../ accepted
     |
     v
Vulnerable
```

Use:

```text
Identify File Operation
        |
        v
Establish Baseline
        |
        v
Understand Expected Directory
        |
        v
Use Controlled Traversal
        |
        v
Observe Known File Content
        |
        v
Determine Normalisation
        |
        v
Determine Security Boundary
        |
        v
Evidence
```


# Vulnerability Classes

## Path Traversal

Path traversal allows a user to escape the intended filesystem directory.

```text
Intended Directory
      |
      v
/var/www/files/
      |
      v
../../../
      |
      v
Outside Directory
```


## Arbitrary File Read

Arbitrary file read describes the resulting capability when an attacker can retrieve files from unintended locations.

Path traversal is one possible cause.


## Local File Inclusion

Local File Inclusion usually means attacker-controlled input causes the application to include or interpret a local file.

Conceptually:

```text
User Input
    |
    v
include()
    |
    v
Local File
    |
    v
Application Processing
```


## Remote File Inclusion

Remote File Inclusion involves loading or including content from a remote location.

Whether RFI is possible depends heavily on:

```text
Language

Runtime configuration

Application code

Network access
```


## Unsafe File Download

An endpoint may allow arbitrary local files to be downloaded without actually including or executing them.

Example:

```text
/download?file=...
```

This may be better described as:

```text
Path Traversal leading to Arbitrary File Read
```

rather than LFI.


# Path Traversal vs LFI

These terms are frequently used interchangeably, but they describe different aspects.

```text
Path Traversal
      |
      v
Filesystem Path Escaped
```

versus:

```text
Local File Inclusion
      |
      v
Application Includes Local File
```


# Example Path Traversal

Request:

```http
GET /download?file=report.pdf HTTP/1.1
Host: target.example
```

Application:

```python
path = "/var/www/files/" + request.args["file"]

return send_file(path)
```


# Expected Path

```text
/var/www/files/report.pdf
```


# Traversal Input

```text
../../../etc/hostname
```


# Resulting Path

Conceptually:

```text
/var/www/files/../../../etc/hostname
```

Normalised:

```text
/etc/hostname
```


# Discovery

Look for functionality involving:

```text
Downloads

Attachments

Images

Templates

Language files

Themes

Reports

Exports

Documents

Static resources

Log viewers

File previews

Configuration files

Backup retrieval
```


# Candidate URLs

Examples:

```text
/download?file=report.pdf

/view?page=home.html

/image?path=logo.png

/document?id=manual.pdf

/template?name=default

/lang?file=en.json

/export?filename=report.csv
```


# Candidate JSON

```json
{
  "file": "report.pdf"
}
```


# Nested JSON

```json
{
  "document": {
    "path": "reports/2026/report.pdf"
  }
}
```


# REST-Style Paths

Traversal input may also appear directly in a route.

Example:

```text
/files/report.pdf
```

or:

```text
/api/files/reports/2026/report.pdf
```


# Headers

Less commonly, file names may be influenced through:

```text
Content-Disposition

X-Original-URL

X-Rewrite-URL

Custom application headers
```

Only test headers that are relevant to the application's behaviour.


# Step 1 - Establish Baseline

Start with a legitimate file.

```http
GET /download?file=manual.pdf HTTP/1.1
Host: target.example
```


# Record Baseline

Capture:

```text
Status code

Content-Type

Content-Length

Content-Disposition

Response body

Response time
```


# Step 2 - Identify Expected Directory

Where possible, determine the intended storage location.

Source code might reveal:

```python
DOWNLOAD_DIR = "/srv/app/downloads"
```


# White-Box Advantage

Knowing the expected base directory lets you design a minimal traversal rather than guessing excessive directory depth.


# Step 3 - Use a Harmless Known File

For Linux, a low-impact system identification file may be appropriate when authorised.

A better white-box test is an assessment-created file such as:

```text
/tmp/traversal-test.txt
```

containing:

```text
TRAVERSAL_TEST_7f3a9
```


# Controlled Linux Example

Suppose the application base directory is:

```text
/srv/app/downloads/
```

and the test file is:

```text
/srv/app/traversal-test.txt
```

A minimal candidate might be:

```text
../traversal-test.txt
```


# Controlled Evidence

Expected returned content:

```text
TRAVERSAL_TEST_7f3a9
```

This provides clean evidence without retrieving sensitive operating-system files.


# Windows Controlled File

Example controlled file:

```text
C:\Temp\traversal-test.txt
```

containing:

```text
TRAVERSAL_TEST_7f3a9
```


# Windows Traversal Syntax

```text
..\..\..\Temp\traversal-test.txt
```

The correct number of traversal segments depends on the application's base directory.


# Separator Differences

Linux normally uses:

```text
/
```

Windows normally uses:

```text
\
```

Many frameworks and libraries may accept more than one separator representation.


# Basic Linux Traversal

```text
../
```


# Basic Windows Traversal

```text
..\
```


# Multiple Levels

```text
../../
```

```text
../../../
```

```text
../../../../
```


# Do Not Guess Excessive Depth Immediately

Start with the minimum traversal necessary when architecture or source information is available.


# Absolute Paths

Some applications may accept absolute paths directly.

Linux:

```text
/etc/hostname
```

Windows:

```text
C:\Windows\win.ini
```


# Absolute Path Interpretation

If an application accepts an absolute path, the issue may not require `../` traversal at all.

The root cause is still:

```text
User-controlled filesystem path without adequate restriction.
```


# URL Encoding

HTTP clients and frameworks may decode URL parameters before application processing.

Basic encoded slash:

```text
%2f
```

Encoded backslash:

```text
%5c
```


# Encoded Traversal

```text
..%2f..%2f..%2f
```


# Fully Encoded Dots and Slash

```text
%2e%2e%2f
```


# Encoded Windows Traversal

```text
%2e%2e%5c
```


# Why Encoding Matters

A request may pass through several layers:

```text
Browser / Client
      |
      v
Reverse Proxy
      |
      v
Web Server
      |
      v
Framework
      |
      v
Application
```

Each layer may:

```text
Decode

Normalise

Reject

Rewrite
```

the path differently.


# Double Encoding

A double-encoded slash may appear as:

```text
%252f
```

because:

```text
%25
```

represents:

```text
%
```


# Double-Decoding Model

```text
..%252f
    |
    v
..%2f
    |
    v
../
```


# When Double Encoding Matters

Only test double encoding when there is evidence that:

```text
Multiple decoding stages exist

A filter operates before a later decode

The architecture makes it relevant
```


# Do Not Blindly Spray Encodings

Use controlled variations and compare responses.


# Normalisation

A secure implementation should reason about the canonical filesystem path rather than the raw user string.

Conceptually:

```text
User Path
    |
    v
Join With Base Directory
    |
    v
Canonicalise
    |
    v
Verify Still Inside Base
    |
    v
Open File
```


# Weak Validation

Example:

```python
if "../" in filename:
    reject()
```

This is fragile because it reasons about a string rather than the resolved filesystem path.


# Stronger Model

```text
BASE DIRECTORY
      |
      v
Join User-Supplied Relative Name
      |
      v
Resolve Canonical Path
      |
      v
Is Result Inside BASE?
      |
    Yes / No
```


# Prefix Removal

Some applications attempt to remove traversal sequences.

Example concept:

```text
Input:
../../test.txt

Filter removes:
../

Result:
../test.txt
```

A transformation-based filter can therefore behave unexpectedly.


# Filtering vs Canonicalisation

Prefer:

```text
Canonicalise then enforce boundary
```

over:

```text
Repeatedly replace suspicious strings.
```


# File Extensions

Applications may append an extension.

Example:

```python
filename = request.args["page"] + ".html"
```


# Result

Input:

```text
help
```

becomes:

```text
help.html
```


# Extension Restrictions

Determine whether the application:

```text
Appends extension

Requires extension

Checks extension

Replaces extension
```


# Do Not Assume Extension Checks Are Security Boundaries

An extension allowlist may be useful for business logic, but filesystem containment must still be enforced independently.


# Null Bytes

Historical applications and language/runtime combinations sometimes treated null bytes specially.

Modern runtimes generally handle this differently or reject them.

Do not treat null-byte techniques as universally applicable.


# Legacy Candidate

Historical notation:

```text
%00
```

Use only when testing a relevant legacy stack and when there is a technical reason to do so.


# Path Prefix Requirements

An application may expect:

```text
images/
```

before a file name.

Example:

```text
images/logo.png
```


# Validation Question

Determine whether the application validates:

```text
Raw input
```

or:

```text
Canonical resolved path.
```


# File Download Example

Baseline:

```http
GET /api/download?file=report.pdf HTTP/1.1
Host: target.example
```


# Traversal Test

```http
GET /api/download?file=../traversal-test.txt HTTP/1.1
Host: target.example
```


# Representative Positive Result

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Disposition: attachment; filename="traversal-test.txt"

TRAVERSAL_TEST_7f3a9
```


# Interpretation

This demonstrates:

```text
The user-controlled file parameter escaped the intended download directory and accessed a file outside that directory.
```


# Representative Negative Result

```http
HTTP/1.1 400 Bad Request

Invalid file path
```


# Negative Result Interpretation

This may indicate:

```text
Traversal validation

Canonical path containment

Application-level block
```

Further testing may still be required to understand the control.


# File Not Found

Example:

```http
HTTP/1.1 404 Not Found
```

This does not prove traversal was blocked.

Possible explanations:

```text
File genuinely absent

Wrong traversal depth

Path normalised differently

Application rewrote input

Access denied translated to 404
```


# Permission Denied

Example:

```text
Permission denied
```

This may indicate:

```text
The path reached filesystem access but the application account could not read the target.
```

It does not demonstrate successful disclosure.


# Different Error Messages

Compare:

```text
File does not exist

Invalid path

Permission denied

Directory not allowed

Path outside root
```

These can help understand where validation occurs.


# Response Length

Traversal responses may differ in:

```text
Content length

Content type

Content disposition

Status
```

Use Burp Comparer or response comparison when differences are subtle.


# File Inclusion

File inclusion is particularly associated with applications that dynamically load templates or scripts based on user input.


# Conceptual PHP Example

```php
$page = $_GET['page'];

include($page);
```


# Input

```text
?page=about.php
```


# Application Behaviour

```text
include("about.php")
```


# Unsafe Input

If arbitrary local paths are accepted, the application may include unintended files.


# LFI vs Arbitrary File Read

An endpoint that performs:

```php
readfile($path);
```

is different from:

```php
include($path);
```

The first reads data.

The second may interpret the file according to the runtime's inclusion semantics.


# Report the Actual Sink

Prefer precise descriptions such as:

```text
Path Traversal in File Download

Arbitrary Local File Read

Local File Inclusion
```

rather than using `LFI` for every filesystem issue.


# Remote File Inclusion

RFI requires a runtime or application that supports remote resources in the relevant inclusion operation.

Conceptually:

```text
User URL
   |
   v
include()
   |
   v
Remote Resource
```


# Controlled RFI Validation

If remote inclusion is relevant and explicitly authorised, use only a harmless controlled resource.

Example conceptual content:

```text
RFI_TEST_7f3a9
```

Do not use executable payloads simply to prove remote resource retrieval.


# RFI vs SSRF

If the application merely retrieves a remote resource:

```text
User URL
   |
   v
HTTP Client
```

that is more likely SSRF.

If the runtime:

```text
includes/interprets remote content
```

the classification may be RFI.


# Path Traversal in APIs

API request:

```http
POST /api/document HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "path": "reports/annual.pdf"
}
```


# Candidate

```json
{
  "path": "../traversal-test.txt"
}
```


# Nested Object

```json
{
  "options": {
    "template": "../templates/test.html"
  }
}
```


# GraphQL

A GraphQL argument can also become a filesystem path.

Example:

```graphql
query {
  download(file: "report.pdf")
}
```


# Security Question

The transport mechanism does not matter.

The important flow is:

```text
GraphQL Argument
      |
      v
Resolver
      |
      v
Filesystem Path
```


# Path Traversal in Archives

Archive extraction introduces a related vulnerability commonly called:

```text
Zip Slip
```

Conceptually:

```text
ZIP Entry
   |
   v
../../outside.txt
   |
   v
Extraction
   |
   v
File Written Outside Destination
```


# Zip Slip Is a Write Problem

Traditional path traversal often concerns reading files.

Zip Slip commonly concerns writing extracted files outside the intended extraction directory.


# Archive Entry Example

Conceptual malicious archive entry:

```text
../../outside.txt
```

The secure extractor must ensure the canonical output path remains inside the extraction root.


# Do Not Test Destructive Archive Writes

Use an assessment-controlled directory and harmless marker files where archive extraction testing is authorised.


# File Upload Path Manipulation

Applications may use the supplied filename when saving uploads.

Example:

```text
filename="../../outside.txt"
```


# Upload Model

```text
Multipart Filename
       |
       v
Application Save Path
       |
       v
Filesystem
```


# Security Question

Does the application:

```text
Discard client filename?

Generate its own filename?

Use basename only?

Canonicalise output path?

Enforce upload directory containment?
```


# Multipart Filename

Example:

```http
Content-Disposition: form-data; name="file"; filename="report.pdf"
```


# Filename Trust

Client-supplied filenames should not determine arbitrary filesystem locations.


# Path Traversal in Log Viewers

Example:

```text
/logs?file=application.log
```

These endpoints deserve attention because logs may exist in predictable filesystem directories.


# Path Traversal in Image Endpoints

Example:

```text
/image?name=avatar.png
```

Check whether:

```text
Image ID
```

or:

```text
Raw filesystem path
```

is used internally.


# Path Traversal in Templates

Example:

```text
/template?name=invoice
```

Source:

```python
render_template(request.args["name"])
```

Review how the template engine resolves names and whether directory boundaries are enforced.


# Language Files

Example:

```text
?lang=en
```

Application:

```text
languages/en.json
```

If the user controls the full path rather than a known language identifier, traversal may become possible.


# Safer Language Design

Prefer:

```text
en -> /app/languages/en.json

nl -> /app/languages/nl.json
```

using a server-side mapping.


# File IDs vs File Paths

Prefer:

```text
GET /download?id=7812
```

where:

```text
7812
```

maps server-side to an authorised file.

Avoid exposing raw filesystem paths when unnecessary.


# Indirect References

```text
User
 |
 v
File ID
 |
 v
Database Lookup
 |
 v
Authorisation Check
 |
 v
Server-Controlled Path
 |
 v
File
```


# Path Traversal and Authorisation

Even when path containment is secure, file access may still have an authorisation problem.

Example:

```text
/download?id=1001
```

may allow access to another user's document.

That is typically:

```text
IDOR / BOLA
```

rather than path traversal.


# Keep Findings Separate

```text
Filesystem Boundary
      |
      v
Path Traversal
```

versus:

```text
Object Ownership Boundary
      |
      v
IDOR / BOLA
```


# Path Traversal and Symlinks

Symbolic links can complicate path validation.

Example:

```text
/downloads/public-link
          |
          v
/etc/sensitive-directory
```


# Symlink Security Model

A path may appear to be inside the allowed directory before filesystem resolution.

Secure designs should account for filesystem semantics and symlink behaviour.


# Race Conditions

A check such as:

```text
Validate Path
     |
     v
Open File
```

may be vulnerable to race conditions if filesystem state can change between those operations.

This is especially relevant in environments where attackers can create or modify files or symlinks.


# TOCTOU

```text
Time of Check
     |
     v
Filesystem Changes
     |
     v
Time of Use
```


# Source Code Review

Path traversal is particularly suitable for source-to-sink analysis.


# Sources

Common attacker-controlled sources:

```text
Query parameter

Path parameter

JSON property

Form field

Multipart filename

Cookie

Header

Database value derived from user input
```


# Sinks

Common filesystem sinks:

```text
open()

readFile()

readFileSync()

sendFile()

File()

FileInputStream()

Files.readAllBytes()

File.ReadAllText()

File.Open()

include()

require()

readfile()

fopen()
```


# Python Search

```bash
rg -ni 'open\(|send_file|send_from_directory|Path\(|read_text|read_bytes' -g '*.py' .
```


# Python Candidate

```python
filename = request.args.get("file")

return send_file(
    "/srv/app/downloads/" + filename
)
```


# Source-to-Sink

```text
request.args["file"]
        |
        v
String Concatenation
        |
        v
send_file()
```


# Python pathlib

Potential path construction:

```python
path = Path(BASE_DIR) / user_input
```

This is not automatically vulnerable.

Review whether the resolved path is constrained to the intended base.


# JavaScript / Node.js Search

```bash
rg -ni 'readFile|readFileSync|createReadStream|sendFile|path\.join|path\.resolve' -g '*.js' -g '*.ts' .
```


# Node.js Candidate

```javascript
const file = req.query.file;

res.sendFile(
    path.join("/srv/app/downloads", file)
);
```


# Important Node.js Review

Do not assume:

```text
path.join()
```

provides a security boundary.

Review the final resolved path and containment check.


# Java Search

```bash
rg -ni 'FileInputStream|Files\.read|Paths\.get|new File|Path\.of' -g '*.java' .
```


# Java Candidate

```java
String file = request.getParameter("file");

Path path = Paths.get("/srv/app/downloads", file);
```


# .NET Search

```bash
rg -ni 'File\.Read|File\.Open|FileStream|Path\.Combine|PhysicalFile' -g '*.cs' .
```


# .NET Candidate

```csharp
var path = Path.Combine(
    downloadDirectory,
    userFile
);

return PhysicalFile(path, "application/octet-stream");
```


# PHP Search

```bash
rg -ni 'include|require|readfile|file_get_contents|fopen' -g '*.php' .
```


# PHP Candidate

```php
$file = $_GET['file'];

readfile("/srv/app/downloads/" . $file);
```


# Go Search

```bash
rg -ni 'os\.Open|os\.ReadFile|filepath\.Join|filepath\.Clean|http\.ServeFile' -g '*.go' .
```


# Go Candidate

```go
file := r.URL.Query().Get("file")

path := filepath.Join(baseDir, file)

http.ServeFile(w, r, path)
```


# Ruby Search

```bash
rg -ni 'File\.read|File\.open|send_file|File\.join|Pathname' -g '*.rb' .
```


# Source Review Workflow

```text
Find File Operations
       |
       v
Identify Path Argument
       |
       v
Trace Backwards
       |
       v
User Controlled?
       |
       v
Path Construction
       |
       v
Canonicalisation
       |
       v
Containment Check
       |
       v
Authorisation
       |
       v
Filesystem Operation
```


# Search Path Parameters

```bash
rg -ni 'file|filename|filepath|path|directory|folder|template|document|download' src/
```


# Search Concatenation Near File Operations

```bash
rg -n -C 5 'open\(|readFile|sendFile|FileInputStream|File\.Read|readfile|fopen' src/
```


# Search Path Helpers

```bash
rg -ni 'path\.join|path\.resolve|Path\.Combine|filepath\.Join|Paths\.get|Path\(' src/
```


# Candidate Classification

## Low Concern

```text
Server-Controlled Constant Path
          |
          v
Filesystem
```


## Medium Candidate

```text
User File ID
     |
     v
Database Mapping
     |
     v
Server-Controlled Path
```

Review authorisation and mapping integrity.


## High-Priority Candidate

```text
User Filename
      |
      v
Base + Filename
      |
      v
Filesystem
```


## Very High-Priority Candidate

```text
User Path
    |
    v
Filesystem API
```

with no visible containment check.


# Canonicalisation

A strong containment check should operate on canonical paths.

Conceptually:

```text
BASE:
/srv/app/downloads

INPUT:
../traversal-test.txt

JOIN:
/srv/app/downloads/../traversal-test.txt

RESOLVE:
/srv/app/traversal-test.txt

CHECK:
Is resolved path inside /srv/app/downloads?

NO -> Reject
```


# Python Conceptual Defence

```python
from pathlib import Path

BASE = Path("/srv/app/downloads").resolve()

candidate = (BASE / user_filename).resolve()

if BASE not in candidate.parents:
    raise ValueError("Invalid file path")
```


# Important Edge Case

The base directory itself may also be a valid target depending on application behaviour.

Production code should implement containment carefully and account for:

```text
Exact base path

Children

Symlinks

Platform semantics
```


# Java Conceptual Defence

```java
Path base = Paths.get("/srv/app/downloads")
                 .toRealPath();

Path candidate = base.resolve(userInput)
                     .normalize();

if (!candidate.startsWith(base)) {
    throw new SecurityException("Invalid path");
}
```


# Important Java Note

`normalize()` resolves path syntax such as:

```text
..

.
```

but filesystem-specific symlink behaviour may require additional consideration.


# .NET Conceptual Defence

```csharp
var basePath = Path.GetFullPath(downloadDirectory);

var candidate = Path.GetFullPath(
    Path.Combine(basePath, userFile)
);
```

Then enforce that the canonical candidate belongs to the intended base directory using platform-appropriate path comparison.


# Node.js Conceptual Defence

```javascript
const base = path.resolve("/srv/app/downloads");

const candidate = path.resolve(base, userFile);
```

Then verify that the final path is contained within the intended directory.


# Do Not Use Naive Prefix Checks

Example fragile logic:

```text
candidate.startsWith("/srv/app/download")
```

could potentially confuse:

```text
/srv/app/download

/srv/app/download-backup
```

Boundary-aware path comparison is required.


# Server-Side Mapping

The strongest design often avoids user-controlled paths entirely.

```text
User:
invoice-template
      |
      v
Server Mapping
      |
      v
/templates/invoice.html
```


# Example Mapping

```python
TEMPLATES = {
    "invoice": "/srv/app/templates/invoice.html",
    "receipt": "/srv/app/templates/receipt.html",
}
```


# Benefits

```text
No arbitrary path

Small allowlist

Clear business intent

Easier authorisation
```


# Burp Suite Workflow

```text
Proxy
  |
  v
Identify File Parameter
  |
  v
Repeater
  |
  v
Baseline File
  |
  v
Minimal Traversal
  |
  v
Encoding Variation if Needed
  |
  v
Compare Responses
  |
  v
Confirm Known File
```


# Burp Repeater Baseline

```http
GET /download?file=manual.pdf HTTP/1.1
Host: target.example
Cookie: session=REDACTED
```


# Controlled Traversal

```http
GET /download?file=../traversal-test.txt HTTP/1.1
Host: target.example
Cookie: session=REDACTED
```


# Encoded Candidate

```http
GET /download?file=..%2ftraversal-test.txt HTTP/1.1
Host: target.example
Cookie: session=REDACTED
```


# Burp Decoder

Useful for:

```text
URL encoding

Double encoding

Comparing encoded path representations
```


# Burp Comparer

Compare:

```text
Legitimate file response

Non-existent file response

Traversal response

Encoded traversal response
```


# Burp Intruder

Intruder can test a small controlled set of path representations.

Example payload set:

```text
../traversal-test.txt

..%2ftraversal-test.txt

%2e%2e%2ftraversal-test.txt
```

Use only a small targeted list.


# Do Not Use Huge Traversal Lists by Default

Large payload lists create noise and make interpretation harder.

Understand the application's path handling first.


# curl Baseline

```bash
curl -i 'https://target.example/download?file=manual.pdf'
```


# curl Traversal

Use URL encoding carefully because curl may interpret or normalise URL components differently depending on how the request is constructed.

For query parameters:

```bash
curl -i 'https://target.example/download?file=..%2ftraversal-test.txt'
```


# Preserve Path Segments

When testing traversal directly inside a URL path, curl provides:

```text
--path-as-is
```

to avoid normalising sequences such as `../` before sending them.


# curl Path Example

```bash
curl --path-as-is -i 'https://target.example/files/../traversal-test.txt'
```


# Why `--path-as-is` Matters

Without it, the client may normalise:

```text
/files/../test
```

before the request reaches the server.


# Browser Behaviour

Browsers can also normalise URL paths.

For precise traversal testing, Burp Repeater or curl with appropriate options is usually easier to reason about.


# Reverse Proxies

Architecture may include:

```text
Client

Reverse Proxy

Web Server

Framework

Application
```

Traversal handling can differ at each layer.


# Proxy Normalisation

A reverse proxy may:

```text
Decode paths

Collapse dot segments

Reject encoded separators

Rewrite routes
```


# Application vs Proxy Finding

Determine which layer actually allows or blocks the traversal.

This matters for remediation.


# Web Server Static Files

Static file servers typically have built-in path handling.

Custom file-serving endpoints deserve particular attention because application code may bypass framework protections.


# Framework Helpers

Functions such as:

```text
send_from_directory()

safe_join()
```

may provide security protections when used correctly.

Do not classify framework usage as vulnerable without tracing actual behaviour.


# File Permissions

Successful traversal still operates under application process permissions.

```text
Application Account
       |
       v
Filesystem Permissions
       |
       v
Readable?
```


# Least Privilege

Filesystem permissions provide an important secondary control.

The application should not be able to read:

```text
Private keys

Deployment secrets

Unrelated application data

System administration files
```

unless required.


# Containers

A containerised application's filesystem view may differ from the host.

Traversal may expose:

```text
Container filesystem

Mounted configuration

Mounted secrets

Application files
```

rather than the host filesystem.


# Do Not Assume Host Access

A path such as:

```text
/etc/...
```

inside a container generally refers to the container's filesystem namespace unless host paths are mounted.


# Kubernetes

Application containers may have mounted:

```text
Configuration

Secrets

Service account data

Volumes
```

The actual exposure depends on pod configuration and filesystem permissions.

Do not access sensitive mounted data unless explicitly authorised.


# Chroot / Sandbox

A process may operate inside a restricted filesystem environment.

Traversal may escape an application subdirectory while still remaining inside:

```text
Container

chroot

sandbox
```


# Impact Should Reflect the Actual Boundary

Do not write:

```text
Full server filesystem access
```

when testing only demonstrated:

```text
Read access outside the application's intended download directory.
```


# Error-Based Discovery

Application errors can reveal path information.

Example:

```text
FileNotFoundError:
/srv/app/downloads/../../../test.txt
```


# Information Learned

This may reveal:

```text
Base directory

Framework

Filesystem structure
```

but an error alone is not proof that arbitrary files can be read.


# Directory Access

A file endpoint may behave differently when given a directory.

Possible results:

```text
403

404

Directory listing

Application error
```

Directory listing is a separate issue if exposed.


# File Existence Oracle

Different responses for:

```text
Existing file

Non-existing file
```

may create a file existence oracle even if contents cannot be retrieved.


# Example

```text
Existing:
403 Forbidden

Missing:
404 Not Found
```

This can disclose filesystem state.


# Report Separately When Appropriate

A file existence oracle is generally weaker than arbitrary file read.


# Path Traversal and Write Operations

Path traversal can also affect:

```text
Upload destinations

Export paths

Backup paths

Archive extraction

Log creation

Generated reports
```


# Write Traversal Model

```text
User Filename
     |
     v
Output Directory
     |
     v
../
     |
     v
Unexpected Write Location
```


# Controlled Write Testing

If authorised, write only:

```text
Harmless uniquely named marker file
```

to an approved assessment directory.


# Do Not Overwrite Existing Files

Avoid testing paths that could:

```text
Replace configuration

Overwrite application code

Modify startup files

Affect other users
```


# Filename Sanitisation

For uploads, applications should generally:

```text
Generate server-side filename

Store original filename as metadata

Avoid using client filename as filesystem path
```


# Original Filename

A database may safely store:

```text
Quarterly Report.pdf
```

for display while the actual file is stored as:

```text
9f47f8d0-...bin
```


# Evidence Collection

For a path traversal finding capture:

```text
Endpoint

HTTP method

Parameter

Authentication context

Expected file

Expected base directory if known

Traversal input

Encoding used

Returned controlled marker

Status code

Response headers

Response body

Timestamp
```


# Strong Evidence Chain

```text
1. Retrieve legitimate file.

2. Show expected endpoint behaviour.

3. Submit minimal traversal.

4. Retrieve harmless known file outside intended directory.

5. Capture unique known marker.

6. Repeat if necessary.

7. Stop once the security boundary is demonstrated.
```


# Reporting Example - Path Traversal

> The `file` parameter used by the document download endpoint is incorporated into a filesystem path without adequately enforcing the intended download directory boundary. During testing, a relative path containing a parent-directory reference caused the application to retrieve an assessment-created file located outside the configured download directory. This demonstrates path traversal leading to unauthorised local file read.


# Reporting Example - Arbitrary File Read

> The download endpoint accepts an absolute filesystem path supplied by the authenticated user. A request referencing an assessment-created file outside the application's document directory returned the known file contents. The application therefore permits local file reads outside the intended storage location.


# Reporting Example - LFI

> The `page` parameter controls the local file passed to the application's inclusion mechanism. A relative traversal sequence caused the application to include a controlled local file outside the intended template directory, demonstrating local file inclusion.


# Reporting Example - Encoded Traversal

> Direct parent-directory sequences were rejected by the application; however, URL-encoded path separators were decoded after the validation step. Supplying the same traversal using encoded separators allowed the resulting canonical path to escape the intended directory and retrieve a controlled test file.


# Reporting Example - Write Traversal

> The application uses the client-supplied filename when constructing the output path for generated files. Parent-directory references in the filename caused a harmless assessment marker file to be written outside the intended output directory, demonstrating path traversal in a filesystem write operation.


# Avoid Overclaiming

Do not write:

```text
The attacker can read every file on the server.
```

unless permissions and testing actually support that conclusion.

Prefer:

```text
The application can read files outside the intended document directory that are accessible to the application process.
```


# Severity Considerations

Consider:

```text
Authentication required

Read vs write capability

Application process privileges

Accessible file sensitivity

Containerisation

Filesystem isolation

Path restrictions

Response visibility

Multi-tenant impact

Ability to include vs only read
```


# Remediation - Avoid Raw Paths

The best design is often to avoid user-controlled filesystem paths entirely.


# Use File Identifiers

Prefer:

```text
/download?id=7812
```

instead of:

```text
/download?file=/srv/data/user/report.pdf
```


# Server-Side Mapping

```text
File ID
   |
   v
Database
   |
   v
Authorisation
   |
   v
Server-Controlled Path
```


# Canonicalise Paths

When relative filenames are required:

```text
Base Directory
      |
      v
Join
      |
      v
Canonicalise
      |
      v
Containment Check
      |
      v
Open
```


# Enforce Directory Boundary

The canonical target must remain inside the approved base directory.


# Reject Absolute Paths

If only relative file names are required:

```text
Reject absolute paths.
```


# Restrict File Names

Where possible, accept:

```text
Simple file identifiers
```

rather than arbitrary nested paths.


# Generate Upload Filenames

Do not use raw client filenames as storage paths.


# Least Privilege

Run the application with only the filesystem permissions it requires.


# Separate Sensitive Data

Do not store unrelated sensitive configuration in locations readable by a public-facing application unless required.


# Framework APIs

Use framework-provided secure file-serving helpers correctly where available.


# Avoid String Replacement Defences

Do not rely solely on:

```text
replace("../", "")
```

or:

```text
if "../" in path
```

because these do not enforce the actual filesystem boundary.


# Retesting

Retest the exact original endpoint and path.


# Retest Baseline

Confirm normal downloads still work:

```text
manual.pdf
```


# Retest Original Traversal

Example:

```text
../traversal-test.txt
```

Expected:

```text
Rejected
```

or:

```text
Not accessible
```


# Retest Encoded Variants

Where relevant:

```text
..%2ftraversal-test.txt

%2e%2e%2ftraversal-test.txt
```


# Retest Windows Separators

On relevant platforms:

```text
..\traversal-test.txt

..%5ctraversal-test.txt
```


# Retest Absolute Paths

If the original application accepted absolute paths, confirm they are rejected unless explicitly required.


# Retest Normalisation

Verify that canonical paths outside the base directory are rejected regardless of raw representation.


# Retest Symlinks

Where symlink behaviour contributed to the original issue and the assessment permits it, verify the final filesystem resolution cannot escape the approved directory.


# Retest Write Operations

If the original issue affected uploads or generated files, verify that output paths remain inside the approved directory.


# Retest Authorisation

Do not stop at traversal remediation.

Confirm legitimate file access still enforces ownership and role permissions.


# Root Cause Review

After finding one path traversal issue, search for equivalent file operations across the codebase.

Python:

```bash
rg -ni 'open\(|send_file|send_from_directory|Path\(' -g '*.py' .
```

Node.js:

```bash
rg -ni 'readFile|readFileSync|createReadStream|sendFile|path\.join|path\.resolve' -g '*.js' -g '*.ts' .
```

Java:

```bash
rg -ni 'FileInputStream|Files\.read|Paths\.get|new File|Path\.of' -g '*.java' .
```

.NET:

```bash
rg -ni 'File\.Read|File\.Open|FileStream|Path\.Combine|PhysicalFile' -g '*.cs' .
```

PHP:

```bash
rg -ni 'include|require|readfile|file_get_contents|fopen' -g '*.php' .
```

Go:

```bash
rg -ni 'os\.Open|os\.ReadFile|filepath\.Join|filepath\.Clean|http\.ServeFile' -g '*.go' .
```


# Practical Testing Checklist

## Discovery

- [ ] Download endpoints identified
- [ ] File preview endpoints identified
- [ ] Image endpoints reviewed
- [ ] Template parameters reviewed
- [ ] Language parameters reviewed
- [ ] Report/export functionality reviewed
- [ ] Upload filenames reviewed
- [ ] Archive extraction reviewed
- [ ] Log viewers reviewed
- [ ] Configuration imports reviewed

## Baseline

- [ ] Legitimate file retrieved
- [ ] Status code recorded
- [ ] Content-Type recorded
- [ ] Content-Disposition recorded
- [ ] Response length recorded
- [ ] Authentication context recorded

## Traversal

- [ ] Minimal parent traversal tested
- [ ] Correct platform separator tested
- [ ] Controlled test file preferred
- [ ] Absolute path handling reviewed
- [ ] URL encoding reviewed where relevant
- [ ] Double decoding considered only where justified
- [ ] Path normalisation understood

## File Inclusion

- [ ] Read operation distinguished from include operation
- [ ] Local inclusion reviewed where relevant
- [ ] Remote inclusion considered only when technically applicable
- [ ] SSRF distinguished from RFI
- [ ] Template handling reviewed

## Upload and Write

- [ ] Client filename handling reviewed
- [ ] Output path construction reviewed
- [ ] Archive entry paths reviewed
- [ ] Controlled marker used for write testing
- [ ] Existing files not overwritten

## Source Review

- [ ] Filesystem sinks identified
- [ ] Path argument traced backwards
- [ ] User-controlled source identified
- [ ] Base directory identified
- [ ] Canonicalisation reviewed
- [ ] Directory containment reviewed
- [ ] Absolute paths reviewed
- [ ] Symlink behaviour considered
- [ ] Authorisation reviewed

## Evidence

- [ ] Endpoint recorded
- [ ] Method recorded
- [ ] Parameter recorded
- [ ] Authentication context recorded
- [ ] Baseline file recorded
- [ ] Traversal input recorded
- [ ] Encoding recorded
- [ ] Controlled file marker recorded
- [ ] Response captured
- [ ] Timestamp captured
- [ ] Sensitive information redacted

## Remediation

- [ ] Raw paths removed where possible
- [ ] File IDs considered
- [ ] Server-side mapping implemented
- [ ] Canonical path enforcement implemented
- [ ] Directory containment implemented
- [ ] Absolute paths rejected where unnecessary
- [ ] Upload filenames server-generated
- [ ] Least privilege reviewed
- [ ] Framework secure APIs used

## Retest

- [ ] Legitimate functionality works
- [ ] Original traversal blocked
- [ ] Encoded traversal blocked
- [ ] Alternative separators blocked
- [ ] Absolute path access blocked
- [ ] Symlink path reviewed where relevant
- [ ] Write traversal blocked
- [ ] Authorisation still enforced


# Traversal Representation Table

| Representation | Example |
|---|---|
| Linux parent | `../` |
| Windows parent | `..\` |
| Encoded slash | `..%2f` |
| Encoded backslash | `..%5c` |
| Fully encoded | `%2e%2e%2f` |
| Double encoded slash | `..%252f` |
| Absolute Linux | `/path/to/file` |
| Absolute Windows | `C:\path\to\file` |


# Result Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| `file` parameter exists | File-related functionality | Traversal |
| `../` causes 400 | Input validation | Complete protection |
| Controlled outside file returned | Path traversal/file read | Access to every file |
| Absolute path works | User-controlled filesystem access | Elevated privileges |
| Permission denied | Filesystem access may have occurred | File disclosure |
| Different 404/403 | Possible file existence oracle | File read |
| Encoded path works | Normalisation/filter weakness | Double-decoding |
| Scanner flags traversal | Candidate | Confirmed vulnerability |
| `path.join()` found | Path construction | Vulnerability |
| `open(user_input)` found | Strong source-review candidate | Runtime exploitability |


# Vulnerability Classification Matrix

| Behaviour | Likely Classification |
|---|---|
| Escape directory and download file | Path Traversal / Arbitrary File Read |
| Include unintended local file | Local File Inclusion |
| Include remote resource | Remote File Inclusion |
| Fetch remote URL | SSRF |
| Write outside upload directory | Path Traversal / Arbitrary File Write |
| Extract archive outside target | Zip Slip |
| Access another user's valid file ID | IDOR / BOLA |
| Discover whether local file exists | File Existence Oracle |


# Source Review Matrix

| Pattern | Priority |
|---|---:|
| Constant path -> filesystem | Low |
| File ID -> authorised server mapping | Low |
| User filename -> secure helper | Medium |
| User filename -> base path concatenation | High |
| User path -> filesystem API | High |
| User path -> include/require | High |
| Archive entry -> output path | High |
| Multipart filename -> storage path | High |


# Secure Design Matrix

| Control | Purpose |
|---|---|
| File IDs | Avoid exposing filesystem paths |
| Server-side mapping | Limit accessible resources |
| Canonicalisation | Resolve path semantics |
| Containment check | Keep target inside approved root |
| Server-generated filenames | Prevent upload path manipulation |
| Least privilege | Limit filesystem exposure |
| Secure framework APIs | Reduce custom path handling |
| Authorisation | Enforce object ownership |
| Processing isolation | Reduce impact of file-processing flaws |


# Burp Quick Workflow

```text
             FILE FUNCTION
                  |
                  v
            IDENTIFY PARAMETER
                  |
                  v
                REPEATER
                  |
                  v
             BASELINE FILE
                  |
                  v
          MINIMAL TRAVERSAL
                  |
          +-------+-------+
          |               |
          v               v
      REJECTED         DIFFERENT
          |               |
          v               v
   REVIEW CONTROL    KNOWN TEST FILE
                          |
                          v
                   CONTENT RETURNED?
                     /         \
                    /           \
                   v             v
                 YES             NO
                  |               |
                  v               v
             CONFIRMED       INVESTIGATE
                  |
                  v
               EVIDENCE
```


# Source-to-Sink Model

```text
                   USER INPUT
                       |
                       v
                FILE / PATH VALUE
                       |
                       v
                PATH CONSTRUCTION
                       |
                       v
                  CANONICALISE
                       |
                       v
               CONTAINMENT CHECK
                  /          \
                 /            \
                v              v
             INSIDE          OUTSIDE
                |              |
                v              v
         AUTHORISATION       REJECT
                |
                v
          FILE OPERATION
                |
        +-------+-------+
        |               |
        v               v
       READ            WRITE
```


# Secure Download Model

```text
                   USER
                     |
                     v
                  FILE ID
                     |
                     v
              DATABASE LOOKUP
                     |
                     v
             AUTHORISATION CHECK
                     |
                     v
            SERVER-CONTROLLED PATH
                     |
                     v
               APPROVED STORAGE
                     |
                     v
                   FILE
```


# Final Testing Principle

The key question is:

```text
CAN USER-CONTROLLED INPUT
          |
          v
INFLUENCE A FILESYSTEM PATH
          |
          v
SO THAT THE FINAL RESOLVED PATH
          |
          v
ESCAPES THE INTENDED SECURITY BOUNDARY?
```

A strong path traversal workflow is:

```text
Find File Function
       |
       v
Establish Baseline
       |
       v
Identify Intended Directory
       |
       v
Use Minimal Traversal
       |
       v
Retrieve Harmless Known File
       |
       v
Test Relevant Normalisation
       |
       v
Determine Actual Capability
       |
       v
Capture Evidence
       |
       v
Fix Path Handling
       |
       v
Retest
```

For every candidate ask:

```text
What file operation occurs?

Does the user control a filename or a full path?

What is the intended base directory?

Is the path relative or absolute?

How is the path constructed?

Which component decodes the input?

Is URL decoding performed more than once?

Are path separators normalised?

Is the path canonicalised?

Is the canonical path checked against the intended root?

Are symbolic links relevant?

Does the application read, include or write the file?

Does the application use the client-supplied upload filename?

Does a file ID map to a server-controlled path?

Is authorisation checked independently?

What filesystem permissions does the application process have?

Is the application containerised?

Did I retrieve a known controlled file?

Did I demonstrate read access or only different errors?

Am I describing path traversal, LFI, RFI, SSRF or IDOR accurately?

What impact was actually demonstrated?

Was the root cause fixed or was one payload merely blocked?
```

The strongest evidence is not:

```text
../ changed the response.
```

It is:

```text
CONTROLLED FILE REFERENCE
          |
          v
PATH ESCAPES APPROVED DIRECTORY
          |
          v
KNOWN OUTSIDE FILE
          |
          v
KNOWN CONTENT RETURNED
          |
          v
REPEATABLE SECURITY BOUNDARY FAILURE
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [SSRF Cheatsheet](ssrf.md)
- [XXE Cheatsheet](xxe.md)
- [XSS Cheatsheet](xss.md)
- [SQL Injection Cheatsheet](sql-injection.md)
- [curl Cheatsheet](curl.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [Path Traversal](../web/path-traversal.md)
- [File Inclusion](../web/file-inclusion.md)
- [File Upload](../web/file-upload.md)
- [SSRF](../web/ssrf.md)
- [API Security](../web/api-security.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - Path Traversal](https://portswigger.net/web-security/file-path-traversal){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing Directory Traversal File Include](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11-Testing_for_File_Inclusion){ target="_blank" rel="noopener noreferrer" }
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal){ target="_blank" rel="noopener noreferrer" }
- [CWE-22 - Improper Limitation of a Pathname to a Restricted Directory](https://cwe.mitre.org/data/definitions/22.html){ target="_blank" rel="noopener noreferrer" }
- [CWE-23 - Relative Path Traversal](https://cwe.mitre.org/data/definitions/23.html){ target="_blank" rel="noopener noreferrer" }
- [CWE-36 - Absolute Path Traversal](https://cwe.mitre.org/data/definitions/36.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Use a controlled file when possible"

    If source access or a cooperative assessment allows it, create a harmless marker file outside the intended application directory and use that for validation. Retrieving `TRAVERSAL_TEST_7f3a9` is cleaner evidence than unnecessarily reading operating-system or application secrets.


!!! tip "Canonical paths matter"

    A filter that searches for `../` is not equivalent to filesystem containment. Security decisions should be based on the final canonical path and whether that path remains inside the approved directory.


!!! tip "Classify the sink accurately"

    Reading a file, including a file, fetching a remote URL and accessing another user's document are different behaviours. Distinguishing path traversal, LFI, RFI, SSRF and IDOR makes both the technical analysis and remediation more precise.


!!! warning "Do not prove impact by collecting secrets"

    Once a harmless file outside the intended directory has been retrieved, the core security boundary failure is established. Access sensitive files only when additional impact validation is explicitly required by the assessment.


!!! warning "Do not fix individual payload strings"

    Blocking `../`, `%2f` or one known system path does not address the root cause. Remove unnecessary user-controlled paths or canonicalise the final path and enforce that it remains within the approved filesystem root.
