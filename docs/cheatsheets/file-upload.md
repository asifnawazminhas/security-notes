---
title: File Upload Security Cheatsheet
description: Practical file upload security cheatsheet for authorised web application testing covering validation, extensions, MIME types, signatures, filenames, storage, SVG, archives, image processing, parser risks, access control, source review, Burp Suite, evidence, remediation and retesting.
---

# File Upload Security Cheatsheet

File upload functionality introduces a boundary where attacker-controlled content enters application-controlled storage and processing.

The security question is not simply:

```text
Can I upload a file?
```

The important questions are:

```text
What files are accepted?

How is the file validated?

Where is it stored?

What filename is used?

Can the uploaded file be retrieved?

How is it served?

Is it processed?

Can processing reach dangerous parsers?

Can another user access it?

Can it overwrite another file?

Can uploaded content become executable?
```

A typical upload pipeline is:

```text
Client
  |
  v
Upload Endpoint
  |
  v
Validation
  |
  v
Storage
  |
  v
Processing
  |
  v
Retrieval / Rendering
```

Every stage can introduce a different vulnerability.

!!! warning "Authorised Security Testing"

    Perform file upload testing only against systems explicitly included in the assessment scope. Prefer harmless marker files, non-executable test content and assessment-controlled filenames. Avoid uploading malware, executable payloads, destructive archives or files designed to exhaust server resources unless that testing is explicitly authorised.


# Quick Reference

## Common Upload Endpoints

```text
/upload

/api/upload

/files/upload

/attachments

/documents

/import

/avatar

/profile/image

/media

/images

/files

/api/files
```


## Common Multipart Request

```http
POST /upload HTTP/1.1
Host: target.example
Content-Type: multipart/form-data; boundary=----Boundary

------Boundary
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

UPLOAD_TEST_7f3a9
------Boundary--
```


## Harmless Marker

```text
UPLOAD_TEST_7f3a9
```


## Useful Test Extensions

```text
.txt

.jpg

.png

.pdf

.svg

.xml

.json

.csv

.zip
```


## Common Security Controls

```text
Extension allowlist

MIME validation

Magic-byte validation

Filename generation

Size limits

Storage isolation

Malware scanning

Content sanitisation

Parser hardening

Authorisation

Safe response headers
```


# File Upload Testing Model

Do not use:

```text
File Uploaded
     |
     v
Vulnerable
```

Use:

```text
Upload Feature
     |
     v
Accepted File
     |
     v
Validation Controls
     |
     v
Storage Location
     |
     v
Processing Pipeline
     |
     v
Retrieval Behaviour
     |
     v
Security Boundary
```


# Core Upload Security Model

```text
UNTRUSTED FILE
      |
      v
VALIDATE
      |
      v
RENAME
      |
      v
STORE
      |
      v
PROCESS SAFELY
      |
      v
AUTHORISE ACCESS
      |
      v
SERVE SAFELY
```


# Vulnerability Classes

File uploads can contribute to:

```text
Unrestricted File Upload

Stored XSS

Path Traversal

Arbitrary File Write

File Overwrite

XXE

Server-Side Request Forgery

Parser Vulnerabilities

Archive Extraction Issues

Information Disclosure

Broken Access Control

Malware Distribution

Denial of Service
```

Do not treat all of these as the same finding.


# Start With the Business Function

Determine why the application accepts files.

Examples:

```text
Profile avatar

Support attachment

Invoice upload

Document management

Evidence upload

CSV import

XML import

Backup import

Theme upload

Media library

Report attachment
```


# Understand Expected Files

For each upload feature record:

```text
Expected file type

Expected extension

Expected content

Maximum size

Maximum number of files

Expected processing

Expected storage duration

Who can retrieve the file
```


# Establish a Baseline

Start with a valid expected file.

Example:

```text
test.jpg
```

Record:

```text
Request

Response

File identifier

Returned filename

Retrieval URL

Content-Type

Content-Disposition

Processing delay
```


# Baseline Multipart Request

```http
POST /api/avatar HTTP/1.1
Host: target.example
Content-Type: multipart/form-data; boundary=----TestBoundary

------TestBoundary
Content-Disposition: form-data; name="avatar"; filename="avatar.jpg"
Content-Type: image/jpeg

[valid JPEG content]
------TestBoundary--
```


# Record the Response

Example:

```json
{
  "id": "8a91f7",
  "filename": "avatar.jpg",
  "status": "uploaded"
}
```


# Questions After Baseline

Ask:

```text
Was the original filename retained?

Was a new identifier generated?

Was the extension changed?

Was the file processed?

Was the file resized?

Can it be downloaded?

Can another account retrieve it?

What headers are used when serving it?
```


# Multipart Anatomy

A multipart upload commonly contains:

```http
Content-Disposition: form-data; name="file"; filename="report.pdf"
Content-Type: application/pdf
```

There are several independent pieces of information:

```text
Form field name

Client filename

Client MIME type

File bytes
```


# Do Not Trust Client MIME Type

This value:

```http
Content-Type: image/jpeg
```

is supplied by the client.

It can be changed easily.


# Burp MIME Modification

Original:

```http
Content-Type: text/plain
```

Modified:

```http
Content-Type: image/jpeg
```

If changing only the MIME type bypasses validation, the application is relying too heavily on client-controlled metadata.


# File Extension Validation

An application may allow:

```text
.jpg

.jpeg

.png
```

and reject:

```text
.txt
```

This demonstrates extension validation.

It does not establish that file content is validated.


# Extension Allowlist

Prefer:

```text
Known required extensions
```

over:

```text
Block dangerous extensions
```


# Why Denylists Are Weak

A denylist must anticipate:

```text
Languages

Web server handlers

Platform differences

Alternative extensions

Future configuration changes
```


# Extension Case

Applications should handle extension comparison consistently.

Examples:

```text
image.JPG

image.Jpg

image.PnG
```

Case behaviour can vary by:

```text
Application

Filesystem

Web server

Operating system
```


# Multiple Extensions

Example:

```text
report.txt.jpg
```

Determine which component interprets:

```text
First extension

Last extension

Full filename
```


# Do Not Assume Double Extensions Are Exploitable

A filename such as:

```text
file.php.jpg
```

is only meaningful if some component interprets it in an unsafe way.

Validate actual behaviour rather than reporting the filename alone.


# Trailing Characters

Different platforms can treat trailing:

```text
Spaces

Dots
```

differently.

These cases are relevant primarily when the application's target platform or normalisation behaviour makes them applicable.


# MIME Validation

Applications may inspect:

```text
Multipart Content-Type

Detected content type

File signature

Parser result
```


# Client MIME vs Detected MIME

```text
Client says:
image/jpeg

Actual bytes:
plain text
```

A secure design should not rely solely on the client claim.


# File Signatures

Many formats begin with characteristic bytes.

These are often called:

```text
Magic bytes

File signatures
```


# Examples

JPEG commonly begins with:

```text
FF D8 FF
```

PNG begins with:

```text
89 50 4E 47 0D 0A 1A 0A
```

PDF begins with:

```text
%PDF-
```

ZIP commonly begins with:

```text
PK
```


# Signature Validation

File signatures can help identify obviously mismatched files.

However:

```text
Valid signature != safe file
```

A valid file can still contain:

```text
Malicious active content

Dangerous parser structures

Unexpected metadata

Embedded content
```


# File Command

On Linux:

```bash
file test.pdf
```


# Example

```text
test.pdf: PDF document, version 1.7
```


# MIME Detection

```bash
file --mime-type test.pdf
```


# Example

```text
test.pdf: application/pdf
```


# Hex Inspection

```bash
xxd -l 32 test.pdf
```


# Example

```text
00000000: 2550 4446 2d31 2e37
```

This corresponds to:

```text
%PDF-1.7
```


# Filename Security

Client-supplied filenames are untrusted input.

Example:

```http
filename="report.pdf"
```


# Safer Storage

Prefer:

```text
Original filename:
Quarterly Report.pdf

Stored filename:
8f46c7f0-9c3a-4df1-b4d0.bin
```


# Why Generate Server-Side Names

This helps reduce:

```text
Path manipulation

Name collisions

File overwrite

Special-character issues

Predictable object names
```


# Path Traversal Through Filename

A dangerous pattern is:

```text
filename="../../outside.txt"
```


# Upload Path Model

```text
Client Filename
      |
      v
Upload Directory + Filename
      |
      v
Filesystem Write
```


# Secure Design

```text
Client Filename
      |
      v
Store as Metadata
      |
      v
Generate Server Filename
      |
      v
Approved Upload Directory
```


# Filename Test

A harmless filename test might use:

```text
upload-test-7f3a9.txt
```

and verify whether the application:

```text
Preserves

Changes

Normalises

Rejects
```

the name.


# Special Characters

Relevant filename characters can include:

```text
Spaces

Unicode

Quotes

Parentheses

Ampersands

Angle brackets
```

Testing should focus on how the filename is:

```text
Stored

Displayed

Encoded

Logged

Returned in headers
```


# Filename-Based Stored XSS

A filename may later appear in HTML.

Example filename:

```text
report-7f3a9.txt
```

First determine whether it is rendered safely.

Do not jump directly to active JavaScript payloads if simple HTML encoding analysis is enough.


# Safe Rendering

If the filename:

```text
report<test>.txt
```

appears as:

```text
report&lt;test&gt;.txt
```

the application is HTML-encoding the value in that context.


# Context Matters

A filename may appear in:

```text
HTML text

HTML attribute

JavaScript

JSON

HTTP header

Email

PDF report
```

Each context requires appropriate output encoding.


# Content-Disposition

A download response may use:

```http
Content-Disposition: attachment; filename="report.pdf"
```

This usually encourages download rather than inline rendering.


# Inline Content

A response such as:

```http
Content-Disposition: inline
```

may cause supported formats to render in the browser.


# Content-Type

The response should use an appropriate MIME type.

Example:

```http
Content-Type: application/pdf
```


# `X-Content-Type-Options`

A useful response header is:

```http
X-Content-Type-Options: nosniff
```

This reduces MIME-sniffing behaviour in browsers.


# Storage Location

Determine whether files are stored:

```text
Inside web root

Outside web root

Object storage

Database

Separate file service
```


# Web Root Storage

A risky architecture can be:

```text
Upload
  |
  v
/var/www/html/uploads/
  |
  v
Direct Public URL
```

If the server interprets certain file types, this can increase risk.


# Preferred Model

```text
Upload
  |
  v
Non-Executable Storage
  |
  v
Application Download Handler
  |
  v
Authorisation
```


# Object Storage

Applications frequently use:

```text
Amazon S3

Azure Blob Storage

Google Cloud Storage

S3-compatible storage
```

Security questions include:

```text
Is the object public?

Is the URL predictable?

Are signed URLs used?

How long are signed URLs valid?

Is access tenant-isolated?

Can content type be controlled?
```


# Public Object Storage

An upload being stored in cloud object storage is not itself a vulnerability.

The important question is:

```text
Who can retrieve the object?
```


# Access Control

Test file ownership separately from file type validation.


# Two-Account Model

```text
Account A
   |
   v
Uploads File A
   |
   v
File ID / URL
   |
   v
Account B Attempts Access
```


# Expected Secure Result

Account B should not access Account A's private upload unless sharing is intentionally supported.


# IDOR / BOLA

If another user can retrieve a private file by changing:

```text
File ID

Object key

UUID

Path
```

the primary issue may be:

```text
IDOR / BOLA
```

rather than unrestricted file upload.


# Predictable URLs

Example:

```text
/files/1001

/files/1002

/files/1003
```

Predictability is not itself the vulnerability.

The important control is:

```text
Authorisation on retrieval.
```


# File Replacement

Test whether uploading another file with the same name:

```text
report.pdf
```

causes:

```text
Overwrite

Rename

Versioning

Rejection
```


# Safe Test

Use only files belonging to the assessment account.

Do not attempt to overwrite another user's files unless explicitly authorised.


# Collision Handling

Secure systems commonly use:

```text
Random identifiers

UUIDs

Database IDs

Versioned object keys
```


# Upload Size

Determine:

```text
Maximum file size

Maximum request size

Maximum total storage

Maximum number of files
```


# Size Validation

A response may indicate:

```text
File too large
```

Record the configured behaviour without attempting resource exhaustion.


# Do Not Perform Storage Exhaustion

Avoid repeatedly uploading large files simply to prove that storage limits might be weak.

Denial-of-service testing requires explicit authorisation.


# File Count Limits

A user may be restricted by:

```text
Number of attachments

Daily upload quota

Total account storage
```


# Empty Files

A zero-byte file can reveal validation order.

Example:

```bash
touch empty.txt
```


# Validation Question

Does the application validate:

```text
Extension first?

Size first?

Content first?

Parser first?
```


# Image Uploads

Image functionality often includes server-side processing.

Typical pipeline:

```text
Upload
  |
  v
Image Decoder
  |
  v
Resize
  |
  v
Re-encode
  |
  v
Store
```


# Re-Encoding

Re-encoding uploaded images can remove some unnecessary embedded content.

It is not a universal security solution, but it can reduce attack surface.


# Image Processing Libraries

Potential components include:

```text
ImageMagick

GraphicsMagick

libvips

Pillow

Sharp

GD
```


# Source Search

```bash
rg -ni 'ImageMagick|GraphicsMagick|Pillow|PIL|sharp|libvips|imagecreate|Intervention' .
```


# Image Metadata

Images may contain:

```text
EXIF

GPS information

Camera model

Timestamps

Comments
```

Applications handling privacy-sensitive images may need to remove unnecessary metadata.


# exiftool

Inspect metadata:

```bash
exiftool image.jpg
```


# Metadata Removal Test

Compare metadata before and after application processing.

Do not assume metadata retention is automatically a security vulnerability; evaluate the application's privacy requirements.


# SVG Uploads

SVG deserves special attention because it is XML-based and can contain active or externally referenced content depending on how it is processed and served.


# Minimal SVG

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     width="100"
     height="100">
    <circle cx="50" cy="50" r="40"/>
</svg>
```


# SVG Questions

Ask:

```text
Is SVG allowed?

Is it sanitised?

Is it parsed server-side?

Is it re-rendered?

Is it served inline?

Is it served as an attachment?

What Content-Type is returned?

Does server-side processing resolve external resources?
```


# SVG Security Surfaces

```text
SVG
 |
 +--> Stored active content
 |
 +--> XML parser
 |
 +--> External resource references
 |
 +--> Image conversion library
```


# SVG and XSS

If an uploaded SVG is rendered directly in a browser under the application's origin, active SVG content may create a stored client-side injection risk.

Validate actual browser behaviour and response headers.


# SVG and XXE

If the server parses SVG as XML, parser configuration should be reviewed for XXE.

See:

[XXE Cheatsheet](xxe.md)


# SVG and SSRF

Server-side SVG processing may retrieve external resources in some processing pipelines.

If this occurs, determine whether the root cause is:

```text
XML processing

Image renderer behaviour

Generic URL retrieval
```


# PDF Uploads

PDF files are complex documents that can contain:

```text
Metadata

Embedded objects

Links

Forms

JavaScript features

Attachments
```

depending on the document and viewer.


# PDF Acceptance Is Not a Vulnerability

The fact that an application accepts PDFs does not mean it must reject every PDF containing active features.

Risk depends on:

```text
How the PDF is processed

How it is served

Which viewer opens it

Whether server-side parsers inspect it
```


# PDF Processing

Applications may:

```text
Extract text

Generate thumbnails

Merge documents

Convert to images

Perform OCR

Scan for malware
```


# Parser Attack Surface

Each processing step introduces another parser or library.

Conceptually:

```text
PDF
 |
 v
Parser
 |
 +--> Metadata
 |
 +--> Text extraction
 |
 +--> Thumbnail generation
```


# Office Documents

Formats such as:

```text
DOCX

XLSX

PPTX
```

are ZIP-based document formats containing XML and other resources.


# Office Processing Questions

Ask:

```text
Is the document merely stored?

Is text extracted?

Is it converted?

Is XML parsed?

Are macros relevant to the workflow?

Are external references processed?
```


# Macro-Enabled Formats

Examples include:

```text
.docm

.xlsm

.pptm
```

Whether these should be accepted depends on business requirements.


# Do Not Execute Uploaded Documents

File upload testing normally focuses on server/application handling.

Opening untrusted uploaded documents on analyst workstations introduces unnecessary risk.


# XML Uploads

An application accepting XML should be reviewed for parser configuration.

See:

[XXE Cheatsheet](xxe.md)


# CSV Uploads

CSV imports can introduce:

```text
Parser errors

Formula injection downstream

Data validation issues

Mass assignment

Business logic issues
```


# CSV Formula Injection

If uploaded CSV content is later exported or opened in spreadsheet software, cells beginning with formula syntax may require special handling.

This is separate from the upload mechanism itself.


# Archive Uploads

Applications may accept:

```text
.zip

.tar

.tar.gz

7z
```


# Archive Pipeline

```text
Archive Upload
      |
      v
Extraction
      |
      v
Files Written
      |
      v
Processing
```


# Zip Slip

Archive entries containing traversal paths can potentially escape the extraction directory if the extractor does not validate final paths.

Conceptual entry:

```text
../../outside.txt
```


# Secure Extraction

For every archive entry:

```text
Entry Name
    |
    v
Join Extraction Root
    |
    v
Canonicalise
    |
    v
Verify Inside Root
    |
    v
Extract
```


# Safe Zip Slip Validation

Use:

```text
Harmless marker file

Assessment-controlled extraction directory
```

and avoid overwriting existing application files.


# Archive Bombs

Highly compressed or recursively nested archives can consume substantial resources.

Do not use archive bombs during routine testing.


# Archive Limits

Secure systems should consider:

```text
Compressed size

Uncompressed size

Number of entries

Nested archive depth

Extraction time
```


# Password-Protected Archives

Antivirus or content scanners may not be able to inspect encrypted archives.

Whether these files should be accepted depends on the application's business requirements.


# Malware Scanning

Applications may use antivirus or malware scanning as one layer of upload security.


# EICAR

The EICAR anti-malware test file is a standard harmless test artifact designed to trigger antivirus products.

Use it only where antivirus validation is explicitly in scope and coordinate appropriately because it may generate security alerts.


# Antivirus Is Not File Validation

Even when malware scanning is present, the application still needs controls for:

```text
File type

Filename

Storage

Access control

Parser security

Serving behaviour
```


# Scanner Failure Behaviour

Determine what happens when the malware scanner:

```text
Times out

Is unavailable

Returns an error
```


# Fail Open vs Fail Closed

Security-sensitive upload workflows should deliberately define behaviour when scanning cannot complete.


# Quarantine

A mature pipeline may use:

```text
Upload
  |
  v
Quarantine
  |
  v
Validation
  |
  v
Malware Scan
  |
  v
Processing
  |
  v
Approved Storage
```


# Asynchronous Scanning

The upload may initially return:

```text
Pending
```

while a background worker scans the file.


# Race Condition

A security problem can exist if the file becomes downloadable before scanning finishes.

Model:

```text
Upload
  |
  +------> Publicly Accessible
  |
  v
Scanner
```

Preferred:

```text
Upload
  |
  v
Private Quarantine
  |
  v
Scanner
  |
  v
Release
```


# Test Scan State

Check whether the file can be accessed while its status is:

```text
Pending

Scanning

Quarantined
```


# Processing Failures

Malformed files can cause:

```text
Parser errors

Thumbnail failures

Conversion errors

Worker failures
```

Do not interpret every parser error as a vulnerability.


# Parser Error Information Disclosure

Verbose errors may reveal:

```text
Filesystem paths

Library names

Versions

Internal commands

Storage paths
```


# File Conversion

Common conversions include:

```text
DOCX -> PDF

PDF -> image

SVG -> PNG

Image -> thumbnail

Video -> preview
```


# Conversion Security Model

```text
Untrusted File
     |
     v
Converter
     |
     v
Sandbox / Restricted Worker
     |
     v
Output
```


# Conversion Workers

High-risk parsers should ideally operate with:

```text
Low privileges

Restricted filesystem access

Restricted network access

Resource limits
```


# Temporary Files

Processing may create temporary files.

Review:

```text
Location

Permissions

Filename generation

Cleanup

Cross-user access
```


# Temporary File Race

Predictable temporary filenames can create separate security problems.

Do not assume this from the upload interface alone; inspect source or runtime behaviour.


# Retrieval

After upload, determine how the file is accessed.

Examples:

```text
/files/8a91f7

/download?id=8a91f7

https://storage.example/object

Signed URL
```


# Direct vs Application-Mediated Access

Direct:

```text
Browser
  |
  v
Object Storage
```

Application-mediated:

```text
Browser
  |
  v
Application
  |
  v
Authorisation
  |
  v
Storage
```


# Signed URLs

Review:

```text
Expiration

Object scope

User binding if required

Revocation model
```


# Long-Lived Signed URLs

A signed URL that remains valid longer than necessary can increase exposure if leaked.

Risk depends on the sensitivity and sharing model.


# Cache Behaviour

Sensitive uploaded files should be reviewed for caching.

Potential headers:

```http
Cache-Control:
Pragma:
Expires:
```


# Content Security Policy

For user-controlled content rendered in the browser, CSP can provide defence in depth.

It does not replace correct file-type handling or content isolation.


# Separate Upload Domain

Some architectures serve untrusted user content from a separate origin.

Example:

```text
app.example.com

usercontent.example.net
```


# Why Separate Origin Helps

If active content is accidentally served, origin separation can reduce access to:

```text
Application cookies

Application DOM

Same-origin APIs
```


# Cookie Scope

Ensure application session cookies are not unnecessarily scoped to a parent domain that also includes untrusted content hosts.


# `Content-Disposition: attachment`

For files that should not render inline:

```http
Content-Disposition: attachment
```

can reduce browser execution/rendering risk.


# `nosniff`

Serve:

```http
X-Content-Type-Options: nosniff
```

where appropriate.


# Source Code Review

File upload security benefits from tracing the entire lifecycle.


# Source-to-Sink Model

```text
Multipart Request
       |
       v
Uploaded File Object
       |
       v
Validation
       |
       v
Filename Handling
       |
       v
Storage
       |
       v
Processing
       |
       v
Retrieval
```


# Search Upload Handlers

Generic:

```bash
rg -ni 'upload|multipart|attachment|filename|fileName|originalname|original_filename' src/
```


# Python Search

```bash
rg -ni 'request\.files|FileStorage|save\(|secure_filename|UploadFile' -g '*.py' .
```


# Flask Candidate

```python
file = request.files["file"]

file.save(
    os.path.join(UPLOAD_DIR, file.filename)
)
```


# Review

Ask:

```text
Is file.filename trusted?

Is the filename replaced?

Is the destination canonicalised?

Can an existing file be overwritten?
```


# Werkzeug

Flask applications may use:

```python
secure_filename()
```

This can help sanitise filenames, but filename sanitisation alone is not a complete upload security model.


# FastAPI Candidate

```python
async def upload(file: UploadFile):
    ...
```


# Django Candidate

Search:

```bash
rg -ni 'FileField|ImageField|request\.FILES|upload_to' -g '*.py' .
```


# Node.js Search

```bash
rg -ni 'multer|formidable|busboy|multipart|originalname|mimetype' -g '*.js' -g '*.ts' .
```


# Multer Candidate

```javascript
upload.single("file")
```

Review:

```text
storage

filename callback

fileFilter

limits
```


# Java Search

```bash
rg -ni 'MultipartFile|Part|getOriginalFilename|transferTo' -g '*.java' .
```


# Java Candidate

```java
MultipartFile file
```

with:

```java
file.getOriginalFilename()
```

Review any use of the original filename in filesystem paths.


# .NET Search

```bash
rg -ni 'IFormFile|CopyTo|CopyToAsync|FileName|ContentType' -g '*.cs' .
```


# .NET Candidate

```csharp
IFormFile file
```

Review:

```text
file.FileName

file.ContentType

storage path

generated filename
```


# PHP Search

```bash
rg -ni '\$_FILES|move_uploaded_file|is_uploaded_file' -g '*.php' .
```


# PHP Candidate

```php
$_FILES['file']['name']
```

is client-controlled metadata.


# Go Search

```bash
rg -ni 'FormFile|MultipartReader|multipart\.FileHeader|Filename' -g '*.go' .
```


# Ruby Search

```bash
rg -ni 'ActionDispatch::Http::UploadedFile|original_filename|ActiveStorage|CarrierWave|Paperclip' -g '*.rb' .
```


# Search Storage Paths

```bash
rg -ni 'UPLOAD_DIR|uploadPath|storagePath|mediaRoot|MEDIA_ROOT|uploads/' .
```


# Search Extension Validation

```bash
rg -ni 'extension|extname|allowedExtensions|allowed_types|mime|mimetype|ContentType' src/
```


# Search Processing

```bash
rg -ni 'resize|thumbnail|convert|imagemagick|sharp|Pillow|ffmpeg|pdf|extract|unzip|archive' src/
```


# Search File Serving

```bash
rg -ni 'send_file|sendFile|PhysicalFile|FileResponse|ServeFile|download' src/
```


# Source Review Questions

For every upload path ask:

```text
Who can upload?

What file types are expected?

How is extension validated?

How is MIME type validated?

Is content inspected?

Is the original filename trusted?

Is a server-side filename generated?

Where is the file stored?

Is storage executable?

Can the user control the storage path?

Can existing files be overwritten?

Is the file processed?

Which parsers process it?

Can processors access the network?

Can processors access sensitive files?

Is malware scanning performed?

Is scanning synchronous?

Can the file be accessed before scanning?

Who can retrieve it?

How is retrieval authorised?

What response headers are used?
```


# Burp Suite Workflow

```text
Proxy
  |
  v
Capture Valid Upload
  |
  v
Send to Repeater
  |
  v
Baseline
  |
  +--> Extension
  |
  +--> MIME Type
  |
  +--> Filename
  |
  +--> Content
  |
  +--> Size
  |
  v
Retrieve File
  |
  v
Inspect Headers / Processing
```


# Burp Repeater

A captured multipart request can be modified directly.

Baseline:

```http
POST /upload HTTP/1.1
Host: target.example
Content-Type: multipart/form-data; boundary=----Test

------Test
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

UPLOAD_TEST_7f3a9
------Test--
```


# Change One Variable at a Time

For example:

```text
Test 1:
Change extension only.

Test 2:
Change MIME type only.

Test 3:
Change filename only.

Test 4:
Change content only.
```

This makes the validation logic easier to understand.


# Burp Comparer

Compare responses for:

```text
Accepted valid file

Rejected extension

Rejected MIME

Rejected size

Malformed content
```


# Burp Intruder

Useful for a small controlled list of:

```text
Extensions

MIME types

Filename variants
```

Avoid large indiscriminate payload lists.


# curl Multipart Upload

```bash
curl -i \
  -F 'file=@test.txt;type=text/plain' \
  'https://target.example/upload'
```


# Custom Filename

```bash
curl -i \
  -F 'file=@test.txt;filename=upload-test-7f3a9.txt;type=text/plain' \
  'https://target.example/upload'
```


# Authentication

Example:

```bash
curl -i \
  -H 'Authorization: Bearer REDACTED' \
  -F 'file=@test.txt;type=text/plain' \
  'https://target.example/api/upload'
```


# Avoid Secrets in Shell History

For sensitive assessment credentials, prefer safer token handling rather than embedding long-lived secrets directly in shell commands.


# Response Inspection

After upload:

```bash
curl -I 'https://target.example/files/FILE_ID'
```

Inspect:

```text
Content-Type

Content-Disposition

Content-Length

Cache-Control

X-Content-Type-Options
```


# Download Content

For a harmless test file:

```bash
curl -sS 'https://target.example/files/FILE_ID'
```


# Hash Comparison

Create a hash before upload:

```bash
sha256sum test.jpg
```


# Download and Compare

```bash
sha256sum downloaded.jpg
```


# Interpretation

Matching hashes may indicate:

```text
File stored unchanged
```

Different hashes may indicate:

```text
Re-encoding

Metadata removal

Transformation

Compression
```


# Do Not Assume Transformation Is Security

A changed hash only proves the bytes changed.

Inspect the resulting file and processing behaviour.


# Image Re-Encoding Test

Before:

```bash
file image.jpg
exiftool image.jpg
sha256sum image.jpg
```

After retrieval:

```bash
file downloaded.jpg
exiftool downloaded.jpg
sha256sum downloaded.jpg
```


# Archive Inspection

List ZIP contents without extracting:

```bash
unzip -l archive.zip
```


# TAR Listing

```bash
tar -tf archive.tar
```


# Do Not Extract Untrusted Archives Blindly

Inspect archive entries before extraction in your own testing environment.


# ZIP Entry Review

Look for unexpected paths such as:

```text
../

../../

absolute paths
```


# File Permissions

If you have authorised host access, inspect uploaded-file permissions.

Linux:

```bash
ls -la /path/to/uploads
```


# Questions

Check:

```text
Owner

Group

Read permissions

Write permissions

Execute permissions
```


# Uploaded Files Should Rarely Need Execute Permission

Typical data uploads generally do not require:

```text
+x
```


# Web Server Execution

If uploads are stored under a web server directory, determine whether that directory is configured for:

```text
Static content only
```

or whether server-side execution is possible.


# Do Not Prove Execution With a Reverse Shell

If execution risk is suspected, use the minimum harmless proof authorised by the engagement.

The core security issue can often be established through:

```text
Configuration review

Source review

Non-destructive marker output
```


# File Type Confusion

A file may have:

```text
Extension A

MIME B

Content C
```

Example:

```text
Filename:
test.jpg

Multipart MIME:
image/jpeg

Actual bytes:
plain text
```


# Validation Matrix

| Extension | MIME | Content | Interpretation |
|---|---|---|---|
| Valid | Valid | Valid | Baseline |
| Invalid | Valid | Valid | Tests extension |
| Valid | Invalid | Valid | Tests MIME |
| Valid | Valid | Invalid | Tests content |
| Invalid | Invalid | Invalid | Too many variables changed |


# Better Testing

Change one dimension at a time.


# Polyglot Files

Some files can satisfy the syntax or signature expectations of more than one format.

Polyglots are advanced validation cases.

Do not assume they are required to assess every upload feature.


# Parser Disagreement

A broader security problem occurs when:

```text
Validator sees Format A
        |
        v
Processor sees Format B
```

This is a parser differential.


# Parser Differential Model

```text
Uploaded Bytes
     |
     +--> Validator
     |
     +--> Processor
     |
     +--> Browser
```

Each component may interpret the same bytes differently.


# Filename Reflection

Search the application after upload for the original filename.

Places include:

```text
Upload confirmation

File list

Admin interface

Email notification

Audit log

Download page
```


# Output Encoding

If filenames are displayed in HTML, they must be encoded for the actual HTML context.


# Filename in JSON

Example:

```json
{
  "filename": "report.pdf"
}
```

JSON encoding and later client-side rendering both matter.


# Filename in Header

Example:

```http
Content-Disposition: attachment; filename="report.pdf"
```

Header construction should use safe framework APIs rather than raw string concatenation.


# Content Sniffing

A browser may sometimes infer content type differently from the server declaration.

Using:

```http
X-Content-Type-Options: nosniff
```

provides useful defence in depth.


# HTML Uploads

If HTML files are accepted and served inline from the main application origin, they may execute as same-origin active content.

Whether HTML uploads are legitimate depends on business requirements.


# Safe HTML Storage Model

Where arbitrary documents must be downloadable:

```text
Store outside executable web root

Serve as attachment

Use safe content type

Use separate origin where appropriate
```


# JavaScript Files

A `.js` file being uploadable is not automatically exploitable.

Determine:

```text
Can it be served?

From which origin?

With what MIME?

Can application pages load it?

Can the attacker influence a script URL?
```


# Configuration Files

Uploads such as:

```text
.yaml

.yml

.json

.xml

ini
```

can become dangerous when imported into application configuration.

The issue may be:

```text
Unsafe deserialisation

XXE

Business logic

Configuration injection
```

rather than generic file upload.


# Import Functionality

Distinguish:

```text
Store File
```

from:

```text
Parse and Apply File
```


# Import Model

```text
Upload
  |
  v
Parser
  |
  v
Application Objects
  |
  v
Configuration / Data Changes
```


# Authentication Context

Record whether upload requires:

```text
Unauthenticated user

Normal account

Privileged account

Administrator
```


# Multi-Tenant Systems

For SaaS environments ask:

```text
Can Tenant A access Tenant B uploads?

Are storage prefixes tenant-specific?

Are signed URLs tenant-bound?

Can filenames collide across tenants?
```


# Deletion

Test whether users can delete:

```text
Their own files

Other users' files

Shared files
```

This is primarily an authorisation test.


# Orphaned Files

Deleting a record may not delete the underlying object.

Potential consequences:

```text
Data retention

Storage growth

Unexpected continued access
```


# Retention

Review whether uploaded sensitive files remain accessible after:

```text
Account deletion

Ticket closure

Document replacement

File deletion
```


# Logging

Useful upload audit events include:

```text
User

Timestamp

File ID

Original filename

Detected type

Size

Scan status

Processing result
```


# Avoid Logging File Contents

Sensitive uploaded documents should not be copied unnecessarily into application logs.


# Evidence Collection

For upload findings record:

```text
Finding ID

Endpoint

Method

Authentication context

Original filename

Stored filename if known

Extension

Client MIME type

Detected type if known

File size

Upload response

File identifier

Retrieval URL

Retrieval headers

Processing result

Authorisation result
```


# Evidence for Validation Weakness

Capture:

```text
1. Valid baseline file.

2. Baseline accepted.

3. Change one validation property.

4. Modified file accepted.

5. Demonstrate why the accepted file violates the intended policy.
```


# Evidence for Filename Traversal

Use:

```text
Harmless marker file

Controlled destination
```

and capture the actual resulting path where possible.


# Evidence for Stored XSS

A defensible finding should show:

```text
Uploaded filename/content
        |
        v
Stored
        |
        v
Rendered in browser
        |
        v
Unsafe execution in application origin
```

Do not report merely because an HTML-looking filename was accepted.


# Evidence for Access Control

Use two accounts:

```text
Account A
   |
   v
Upload
   |
   v
File ID
   |
   v
Account B
   |
   v
Access?
```


# Reporting Example - Weak Type Validation

> The document upload endpoint validates the file type using the client-controlled multipart `Content-Type` value. During testing, a file that would normally be rejected was accepted after changing only the multipart MIME type while leaving the file contents unchanged. This demonstrates that the upload policy can be bypassed because the application trusts client-supplied type metadata.


# Reporting Example - Filename Path Traversal

> The upload handler uses the client-supplied filename when constructing the destination filesystem path without adequately enforcing the upload directory boundary. A controlled filename containing a parent-directory reference caused a harmless assessment marker file to be written outside the intended upload directory.


# Reporting Example - Broken File Access Control

> Files uploaded by one authenticated user can be retrieved by another authenticated user by requesting the first user's file identifier. The download endpoint does not enforce ownership or equivalent authorisation before returning the stored object.


# Reporting Example - Unsafe Inline SVG

> The application accepts SVG uploads and serves the uploaded files inline from the primary application origin without sanitising active SVG content. A controlled SVG uploaded through the normal attachment workflow executed browser-side content when viewed, demonstrating stored active-content injection through the upload feature.


# Reporting Example - Quarantine Race

> Uploaded files become retrievable immediately after upload while malware scanning remains in the `pending` state. The application therefore exposes unscanned content before the security validation workflow has completed.


# Avoid Overclaiming

Do not write:

```text
Arbitrary file upload leads to remote code execution.
```

unless execution was actually established.

Prefer:

```text
The application accepts file types outside the documented upload policy.
```

Then describe separately what security consequence was demonstrated.


# Severity Considerations

Consider:

```text
Unauthenticated vs authenticated

Accepted file types

Storage location

Executable storage

Same-origin serving

Inline rendering

Processing pipeline

Parser privileges

Access control

Cross-tenant exposure

File overwrite

Network access from processors

Malware controls
```


# Remediation - Allowlist File Types

Accept only file types required by the business function.

Example:

```text
Avatar:
JPEG
PNG
```

rather than:

```text
Anything except known dangerous extensions
```


# Validate Multiple Signals

Where appropriate validate:

```text
Extension

Detected MIME

File signature

Successful parsing
```

No single check is universally sufficient.


# Generate Server-Side Filenames

Do not use raw client filenames as storage paths.


# Store Original Name as Metadata

Example:

```text
Display name:
Quarterly Report.pdf

Storage object:
c07a6241-f42d-4fb0-9db5
```


# Store Outside Executable Web Root

Uploaded data should not normally reside in directories where the web server or application runtime can execute it.


# Separate Origin

Serve untrusted user content from a separate origin where appropriate.


# Safe Response Headers

Depending on the use case:

```http
Content-Type: application/octet-stream
Content-Disposition: attachment
X-Content-Type-Options: nosniff
```

The correct `Content-Type` depends on whether safe inline rendering is intentionally required.


# Authorise Every Download

Do not rely on:

```text
Unpredictable URL
```

as the only access control.


# Scan Before Release

Preferred:

```text
Upload
  |
  v
Quarantine
  |
  v
Validation
  |
  v
Malware Scan
  |
  v
Safe Processing
  |
  v
Available
```


# Harden Parsers

Any component processing untrusted files should use:

```text
Supported versions

Secure configuration

Least privilege

Resource limits

Restricted network access
```


# Resource Limits

Set limits for:

```text
Upload size

Image dimensions

Archive entries

Uncompressed size

Processing time

Memory

CPU
```


# Archive Extraction

Canonicalise every archive entry and enforce the extraction root.


# Image Re-Encoding

Where appropriate, decode and re-encode images using a hardened supported library rather than preserving arbitrary uploaded bytes.


# SVG

If SVG is not required:

```text
Do not accept it.
```

If required:

```text
Sanitise appropriately

Consider rasterisation

Serve from isolated origin

Use safe response headers
```


# Least Privilege

Upload and conversion workers should not have unnecessary access to:

```text
Application source

Secrets

Administrative directories

Internal networks
```


# Retesting

Retest the original vulnerable workflow rather than only checking the new validation code.


# Retest Baseline

Confirm legitimate files still upload successfully.


# Retest Extension

Verify disallowed extensions are rejected.


# Retest MIME

Changing only client-controlled MIME metadata should not bypass the policy.


# Retest Content

A file with a valid extension but invalid content should be handled according to the intended policy.


# Retest Filename

Verify client filenames cannot:

```text
Escape directories

Overwrite arbitrary files

Create unexpected paths
```


# Retest Storage

Confirm uploaded files are stored in the intended non-executable location.


# Retest Retrieval

Check:

```text
Content-Type

Content-Disposition

nosniff

Authorisation

Caching
```


# Retest Two Accounts

Repeat the ownership test:

```text
Account A upload

Account B access
```

Expected:

```text
Denied
```


# Retest Quarantine

Confirm pending or rejected files are not retrievable.


# Retest SVG

If SVG remains supported, retest:

```text
Sanitisation

Rendering

Response origin

Response headers

Server-side processing
```


# Retest Archives

Verify extraction cannot escape the intended directory.


# Retest Processing Workers

Confirm malformed or unsupported files fail safely without exposing verbose internal errors.


# Root Cause Review

After one upload weakness is found, search for every upload handler.

Generic:

```bash
rg -ni 'upload|multipart|attachment|filename|originalname|original_filename' src/
```

Python:

```bash
rg -ni 'request\.files|FileStorage|UploadFile|FileField|ImageField' -g '*.py' .
```

Node.js:

```bash
rg -ni 'multer|formidable|busboy|originalname|mimetype' -g '*.js' -g '*.ts' .
```

Java:

```bash
rg -ni 'MultipartFile|Part|getOriginalFilename|transferTo' -g '*.java' .
```

.NET:

```bash
rg -ni 'IFormFile|CopyTo|CopyToAsync|FileName|ContentType' -g '*.cs' .
```

PHP:

```bash
rg -ni '\$_FILES|move_uploaded_file|is_uploaded_file' -g '*.php' .
```

Go:

```bash
rg -ni 'FormFile|MultipartReader|multipart\.FileHeader|Filename' -g '*.go' .
```


# Practical File Upload Checklist

## Discovery

- [ ] Upload endpoints identified
- [ ] Avatar upload reviewed
- [ ] Document upload reviewed
- [ ] Attachment upload reviewed
- [ ] Import functionality reviewed
- [ ] Archive upload reviewed
- [ ] Media upload reviewed
- [ ] Admin upload functionality reviewed

## Baseline

- [ ] Valid expected file uploaded
- [ ] Request captured
- [ ] Response captured
- [ ] File ID recorded
- [ ] Retrieval URL recorded
- [ ] Processing behaviour recorded
- [ ] Authentication context recorded

## Type Validation

- [ ] Extension validation reviewed
- [ ] Extension case reviewed where relevant
- [ ] MIME validation reviewed
- [ ] File signature validation reviewed
- [ ] Actual parsing reviewed
- [ ] One variable changed per test

## Filename

- [ ] Original filename handling reviewed
- [ ] Server-generated name identified
- [ ] Special characters reviewed
- [ ] Path traversal considered
- [ ] Collision behaviour reviewed
- [ ] Overwrite behaviour reviewed

## Storage

- [ ] Storage location identified
- [ ] Web-root storage reviewed
- [ ] Execution capability reviewed
- [ ] Object storage permissions reviewed
- [ ] Temporary storage reviewed
- [ ] File permissions reviewed where accessible

## Processing

- [ ] Image processing reviewed
- [ ] PDF processing reviewed
- [ ] Office processing reviewed
- [ ] XML processing reviewed
- [ ] SVG processing reviewed
- [ ] Archive extraction reviewed
- [ ] Conversion workers reviewed
- [ ] Parser errors reviewed

## Malware Controls

- [ ] Scanner presence identified
- [ ] Scanner failure behaviour reviewed
- [ ] Quarantine workflow reviewed
- [ ] Pending files tested for access
- [ ] Rejected files confirmed unavailable

## Retrieval

- [ ] File retrieval tested
- [ ] Content-Type reviewed
- [ ] Content-Disposition reviewed
- [ ] `nosniff` reviewed
- [ ] Cache behaviour reviewed
- [ ] Same-origin rendering reviewed
- [ ] Signed URL behaviour reviewed where applicable

## Authorisation

- [ ] Account A uploaded file
- [ ] Account B attempted access
- [ ] Ownership enforcement reviewed
- [ ] Delete authorisation reviewed
- [ ] Cross-tenant access reviewed

## Source Review

- [ ] Upload handlers identified
- [ ] Client filename traced
- [ ] Storage path identified
- [ ] Extension validation identified
- [ ] MIME validation identified
- [ ] Content validation identified
- [ ] Processing pipeline identified
- [ ] File-serving endpoint identified
- [ ] Authorisation identified
- [ ] Quarantine state identified

## Evidence

- [ ] Endpoint
- [ ] Method
- [ ] Authentication context
- [ ] Filename
- [ ] Extension
- [ ] MIME type
- [ ] File content type
- [ ] File size
- [ ] Upload response
- [ ] File identifier
- [ ] Retrieval response
- [ ] Processing result
- [ ] Authorisation result
- [ ] Sensitive data redacted

## Remediation

- [ ] Required file types allowlisted
- [ ] Client MIME not trusted alone
- [ ] Content validation implemented
- [ ] Server-side filename generated
- [ ] Storage isolated
- [ ] Execution disabled
- [ ] Downloads authorised
- [ ] Safe response headers configured
- [ ] Malware scan before release
- [ ] Parsers hardened
- [ ] Resource limits configured
- [ ] Archive extraction hardened

## Retest

- [ ] Valid upload still works
- [ ] Disallowed extension rejected
- [ ] MIME bypass rejected
- [ ] Invalid content rejected
- [ ] Filename traversal blocked
- [ ] File overwrite blocked
- [ ] Unauthorised retrieval blocked
- [ ] Pending file unavailable
- [ ] SVG handling retested
- [ ] Archive handling retested
- [ ] Processing errors fail safely


# File Validation Matrix

| Check | Useful? | Sufficient Alone? |
|---|---:|---:|
| Extension | Yes | No |
| Client MIME | Limited | No |
| Detected MIME | Yes | No |
| Magic bytes | Yes | No |
| Parser validation | Yes | Usually not alone |
| Malware scanning | Yes | No |
| Server-side filename | Yes | No |
| Storage isolation | Yes | No |
| Access control | Essential | No |


# Upload Risk Matrix

| Behaviour | Potential Risk |
|---|---|
| Arbitrary extensions accepted | Unexpected content types |
| Client MIME trusted | Validation bypass |
| Original filename used as path | Traversal/overwrite |
| Stored in executable web root | Server-side execution risk |
| SVG served inline | Stored active content |
| XML parsed insecurely | XXE |
| Processor has network access | SSRF-like effects |
| Archive extracted unsafely | Zip Slip |
| File publicly retrievable | Data exposure |
| No ownership checks | IDOR/BOLA |
| File accessible before scan | Quarantine bypass |


# File Type Review Matrix

| Type | Important Review Areas |
|---|---|
| JPEG/PNG | Decoder, metadata, re-encoding |
| SVG | XSS, XML, external resources |
| PDF | Parser, conversion, inline serving |
| DOCX/XLSX/PPTX | ZIP/XML processing, conversion |
| XML | XXE, parser configuration |
| CSV | Import validation, formula injection |
| ZIP/TAR | Traversal, extraction limits |
| HTML | Same-origin active content |
| JSON/YAML | Import logic, unsafe parsing |
| Video | Transcoder/parser, resource limits |


# Source Review Matrix

| Pattern | Priority |
|---|---:|
| Upload -> generated filename -> isolated storage | Lower |
| Upload -> original filename -> storage | High |
| Upload -> web root | High |
| Upload -> parser/converter | High |
| Upload -> archive extraction | High |
| Upload -> public object storage | Review access |
| Upload -> quarantine -> scan -> release | Good pattern |
| Upload -> immediately public -> async scan | High |


# Retrieval Matrix

| Behaviour | Review |
|---|---|
| Application download handler | Authorisation |
| Public static URL | Exposure model |
| Signed URL | Expiration/scope |
| Inline rendering | Active content |
| Attachment download | Header safety |
| Separate content origin | Origin isolation |
| Predictable ID | Authorisation, not predictability alone |


# Burp Quick Workflow

```text
                  UPLOAD FEATURE
                        |
                        v
                 VALID BASELINE
                        |
                        v
               CAPTURE IN REPEATER
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      EXTENSION        MIME        FILENAME
          |             |             |
          +-------------+-------------+
                        |
                        v
                     CONTENT
                        |
                        v
                  UPLOAD RESULT
                        |
                        v
                    STORAGE
                        |
                        v
                   PROCESSING
                        |
                        v
                    RETRIEVAL
                        |
              +---------+---------+
              |                   |
              v                   v
         AUTHORISED?         SERVED SAFELY?
              |                   |
              +---------+---------+
                        |
                        v
                     EVIDENCE
```


# Secure Upload Architecture

```text
                    USER FILE
                        |
                        v
                   SIZE LIMIT
                        |
                        v
                TYPE VALIDATION
                        |
                        v
             GENERATED FILE NAME
                        |
                        v
                    QUARANTINE
                        |
             +----------+----------+
             |                     |
             v                     v
       MALWARE SCAN          SAFE PARSING
             |                     |
             +----------+----------+
                        |
                        v
                APPROVED STORAGE
                        |
                        v
                 ACCESS CONTROL
                        |
                        v
                  SAFE DELIVERY
```


# File Processing Model

```text
                 UNTRUSTED FILE
                       |
                       v
                  FILE TYPE
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
      IMAGE           XML          ARCHIVE
        |              |              |
        v              v              v
     DECODER         PARSER        EXTRACTOR
        |              |              |
        +--------------+--------------+
                       |
                       v
               RESTRICTED WORKER
                       |
          +------------+------------+
          |                         |
          X                         X
    Sensitive Files          Internal Network
```


# Final Testing Principle

The key question is not:

```text
Can I upload an unusual extension?
```

The real model is:

```text
WHAT DOES THE APPLICATION TRUST
          |
          v
ABOUT THE FILE
          |
          v
AND WHAT HAPPENS TO THAT FILE
          |
          v
AFTER IT IS ACCEPTED?
```

A strong workflow is:

```text
Understand Upload Function
        |
        v
Upload Valid Baseline
        |
        v
Determine Validation
        |
        v
Change One Property at a Time
        |
        v
Understand Filename Handling
        |
        v
Identify Storage
        |
        v
Identify Processing
        |
        v
Retrieve File
        |
        v
Test Authorisation
        |
        v
Assess Browser Behaviour
        |
        v
Capture Evidence
        |
        v
Remediate Root Cause
        |
        v
Retest Entire Lifecycle
```

For every file upload ask:

```text
Why does the application need uploads?

Which file types are actually required?

Does it trust the extension?

Does it trust client MIME?

Does it inspect file content?

Does it parse the file?

Does it generate a storage filename?

Is the original filename used as a path?

Can the filename traverse directories?

Can a file overwrite another file?

Where is the file stored?

Can uploaded files execute there?

Is storage inside the web root?

Is the file processed?

Which parser processes it?

Does the processor have filesystem access?

Does the processor have network access?

Are archives extracted?

Are archive paths canonicalised?

Is malware scanning performed?

Can the file be accessed before scanning finishes?

Can another user retrieve it?

Can another tenant retrieve it?

How is the file served?

Is it rendered inline?

What Content-Type is returned?

Is `nosniff` present?

Is Content-Disposition appropriate?

Does the application use a separate content origin?

What impact was actually demonstrated?

Was the upload policy bypassed or merely changed?

Has the complete upload lifecycle been retested?
```

The strongest file upload finding is not:

```text
The server accepted test.xyz.
```

It is:

```text
UNTRUSTED FILE
      |
      v
SECURITY CONTROL FAILURE
      |
      v
UNSAFE STORAGE / PROCESSING / RETRIEVAL
      |
      v
REPEATABLE SECURITY IMPACT
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Path Traversal and File Inclusion Cheatsheet](path-traversal-file-inclusion.md)
- [XXE Cheatsheet](xxe.md)
- [SSRF Cheatsheet](ssrf.md)
- [XSS Cheatsheet](xss.md)
- [curl Cheatsheet](curl.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [File Upload](../web/file-upload.md)
- [Path Traversal](../web/path-traversal.md)
- [File Inclusion](../web/file-inclusion.md)
- [XXE](../web/xxe.md)
- [SSRF](../web/ssrf.md)
- [API Security](../web/api-security.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - File Upload Vulnerabilities](https://portswigger.net/web-security/file-upload){ target="_blank" rel="noopener noreferrer" }
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for File Upload](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/09-Test_Upload_of_Unexpected_File_Types){ target="_blank" rel="noopener noreferrer" }
- [OWASP Unrestricted File Upload](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload){ target="_blank" rel="noopener noreferrer" }
- [CWE-434 - Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Change one property at a time"

    If you simultaneously change the filename, extension, MIME type and file bytes, you cannot tell which validation control failed. Start with a valid upload and modify one property per request.


!!! tip "Follow the complete lifecycle"

    Upload acceptance is only the first stage. Storage, processing, malware scanning, retrieval, browser rendering and authorisation often reveal more important weaknesses than the initial extension filter.


!!! tip "Use harmless marker files"

    A unique value such as `UPLOAD_TEST_7f3a9` provides clean evidence for storage, transformation and retrieval testing without introducing executable or malicious content.


!!! tip "Use two accounts"

    File upload testing should include retrieval authorisation. A perfectly validated PDF can still create a serious vulnerability if Account B can retrieve Account A's private document.


!!! warning "Do not equate upload with code execution"

    Accepting an unexpected extension does not demonstrate remote code execution. Establish how the file is stored and served, whether the environment can execute it, and what security consequence actually occurs.


!!! warning "Antivirus is only one layer"

    Malware scanning does not replace extension validation, content inspection, filename safety, storage isolation, parser hardening, authorisation or safe content delivery.
