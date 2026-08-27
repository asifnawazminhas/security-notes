# File Upload Security

File upload functionality creates a boundary where attacker-controlled content enters an application.

A secure upload mechanism must consider significantly more than the file extension.

A file may have:

```text
A permitted extension
A permitted Content-Type
A valid file signature
A valid internal structure
```

while still containing content that becomes dangerous when the file is:

```text
Stored
Parsed
Extracted
Converted
Rendered
Indexed
Downloaded
Opened by another user
Processed by another application
```

File upload testing should therefore examine the complete lifecycle of the uploaded object.

!!! warning "Authorised Security Testing"
    Perform file upload testing only against applications and systems for which you have explicit authorisation. Malware detection tests should use recognised harmless test artefacts such as EICAR wherever possible. Testing with weaponised documents or executable payloads can create client-side execution and callback behaviour and should only be performed in an isolated environment where this is explicitly authorised.

---

# Mental Model

Do not think of file upload security as:

```text
Upload
  ↓
Allowed / Blocked
```

Think of it as:

```text
User-Controlled File
        ↓
HTTP Request
        ↓
Extension Validation
        ↓
Content-Type Validation
        ↓
File Signature Validation
        ↓
Structural Validation
        ↓
Malware Scanning
        ↓
Content Disarm / Reconstruction
        ↓
Filename Handling
        ↓
Storage
        ↓
Backend Processing
        ↓
Retrieval
        ↓
Browser / Application Processing
        ↓
Security Impact
```

A weakness can exist at any stage.

---

# Core Security Questions

For every upload feature, determine:

```text
What file types are intended?

Which extensions are accepted?

Is the extension actually validated?

Is Content-Type trusted?

Are magic bytes checked?

Is the internal file structure validated?

Are files scanned for malware?

Is scanning synchronous?

What happens if scanning fails?

Are files processed before scanning?

Are archives extracted?

Are images transformed?

Are documents converted?

Can SVG or XML be uploaded?

How are filenames handled?

Can filenames contain HTML?

Can filenames contain path separators?

Can duplicate extensions be used?

Where are files stored?

Can uploaded files execute?

Can uploaded files be requested directly?

Is Content-Disposition safe?

Is Content-Type safe on download?

Can another user access the file?

Can administrators view the file?

Are uploads deleted correctly?
```

---

# OWASP File Upload Principles

The OWASP File Upload Cheat Sheet recommends a defence-in-depth approach rather than relying on one validation mechanism.

Important principles include:

```text
Allowlist permitted extensions
Validate the extension after decoding the filename
Do not trust Content-Type alone
Validate file signatures where appropriate
Generate application-controlled filenames
Apply filename restrictions
Set file size limits
Allow uploads only to authorised users
Store files outside the web root where possible
Apply least-privilege filesystem permissions
Scan files for malicious content where appropriate
Use Content Disarm and Reconstruction where appropriate
Protect upload functionality against CSRF
Keep processing libraries updated
```

The important principle is:

> No single upload validation control should be treated as sufficient.

---

# File Upload Testing Workflow

A structured workflow can look like:

```text
Identify Upload Function
        ↓
Upload Known Good File
        ↓
Capture Request
        ↓
Understand Accepted Types
        ↓
Test Extension Validation
        ↓
Test Content-Type Validation
        ↓
Test Signature Validation
        ↓
Test Structural Validation
        ↓
Test Filename Handling
        ↓
Test Malware Detection
        ↓
Test Parser Behaviour
        ↓
Test Storage
        ↓
Test Retrieval
        ↓
Test Access Control
        ↓
Test Browser Behaviour
        ↓
Determine Impact
        ↓
Collect Evidence
        ↓
Report
```

---

# Where to Look

File uploads appear in many different application features.

Examples include:

```text
Profile pictures
Avatars
Documents
Attachments
Support tickets
Invoices
Receipts
Reports
CV uploads
Identity documents
PDF uploads
Image galleries
Import functionality
Backup restoration
XML imports
CSV imports
Spreadsheet imports
ZIP uploads
Email attachments
Media uploads
CMS functionality
Administrative portals
```

Do not assume two upload features use the same validation pipeline.

Test each distinct workflow.

---

# Establish a Baseline

Start with an expected file.

For example:

```text
test.pdf
```

or:

```text
test.jpg
```

Record:

```text
Endpoint
HTTP method
Authentication
CSRF protection
Multipart field name
Filename
Content-Type
File size
Response
Returned identifier
Storage path if exposed
Retrieval URL
```

Example:

```http
POST /api/upload HTTP/1.1
Host: target.example
Content-Type: multipart/form-data; boundary=BOUNDARY

--BOUNDARY
Content-Disposition: form-data; name="file"; filename="test.pdf"
Content-Type: application/pdf

[FILE DATA]
--BOUNDARY--
```

Send the request to Burp Repeater before changing anything.

---

# File Extension Validation

The first question is usually:

> Which extensions are accepted?

Suppose the application claims to allow:

```text
.pdf
.jpg
.jpeg
.png
```

Test whether the server actually enforces this.

Do not rely on:

```html
accept=".pdf,.jpg,.png"
```

in the browser.

That is client-side guidance.

The server must independently enforce the policy.

---

# Client-Side Extension Restrictions

An HTML upload control may contain:

```html
<input type="file" accept=".pdf,.jpg,.png">
```

This can improve usability but should never be considered a security boundary.

Burp can modify the request independently of the browser interface.

The real test is:

```text
What does the server accept?
```

---

# Extension Allowlisting

For a PDF-only upload function, the expected logic should conceptually resemble:

```text
Uploaded File
      ↓
Canonicalise Filename
      ↓
Extract Final Extension
      ↓
Extension == .pdf?
      ↓
Continue Validation
```

The application should not rely only on:

```text
Does filename contain ".pdf"?
```

---

# Double Extensions

Test how the application interprets multiple extensions.

Examples:

```text
document.pdf.txt
document.txt.pdf
image.jpg.txt
image.txt.jpg
```

The objective is to determine:

```text
Which extension does validation use?

Which extension does storage use?

Which extension does the web server use?

Does the application rename the file?
```

A mismatch between these layers can create vulnerabilities.

---

# Multiple Dots

Test filenames containing multiple periods.

Examples:

```text
report.final.pdf
report.backup.final.pdf
```

A secure implementation should correctly identify:

```text
.pdf
```

as the final extension.

Do not assume every multiple-dot filename is malicious.

They are useful for understanding parsing behaviour.

---

# Case Sensitivity

Test whether extension validation is case-sensitive.

Examples:

```text
test.pdf
test.PDF
test.Pdf
test.pDf
```

The application should have deterministic behaviour.

This is particularly relevant when:

```text
Application validation
```

and:

```text
Filesystem / web server behaviour
```

have different case sensitivity.

---

# Trailing Characters

File systems and frameworks may treat trailing characters differently.

Interesting filename variations include:

```text
test.pdf.
test.pdf 
```

Behaviour varies significantly by:

```text
Operating system
Framework
Filesystem
Storage service
Proxy
Application
```

The objective is to identify normalisation differences.

---

# Encoded Filenames

Filenames may be decoded or normalised at different layers.

Determine how the application handles:

```text
URL encoding
Unicode
Percent encoding
HTML entities
Multipart filename encoding
```

The important question is:

```text
Which filename does validation see?
```

versus:

```text
Which filename is eventually stored?
```

---

# Filename Length

Test unusually long but non-destructive filenames.

Potential problems include:

```text
Database truncation
Filesystem truncation
UI corruption
Extension truncation
Logging issues
Application exceptions
```

For example:

```text
AAAA...[long value]...AAAA.pdf
```

Observe whether the filename is:

```text
Rejected
Truncated
Renamed
Stored unchanged
```

---

# Filename Special Characters

Interesting filename characters include:

```text
'
"
<
>
&
;
#
%
+
=
(
)
[
]
{
}
```

Start with harmless markers.

For example:

```text
AM-FILENAME-12345.pdf
```

Then determine where the filename appears.

Potential rendering locations include:

```text
Upload confirmation
File list
Download page
Administrative portal
Support dashboard
Audit log
Email notification
API response
```

---

# Filename XSS

An upload can become an XSS source when the filename is later rendered unsafely.

Conceptually:

```text
Attacker-Controlled Filename
          ↓
Upload
          ↓
Database
          ↓
File Management Interface
          ↓
Filename Rendered as HTML
          ↓
Potential Stored XSS
```

This may also become Blind XSS if the filename is viewed only by an administrator.

Start with a unique harmless marker:

```text
AM-FILENAME-XSS-987654.pdf
```

Determine where it appears before testing execution.

See:

```text
Cross-Site Scripting
Blind XSS
```

for the full testing methodology.

---

# Filename HTML Injection

Even if script execution is blocked, filenames may be interpreted as HTML.

The relevant question is:

```text
Is the filename HTML encoded before rendering?
```

A secure application should render the filename as text.

---

# Filename Path Traversal

File names can also become path traversal inputs.

Conceptually:

```text
Uploaded Filename
       ↓
Application Storage Path
       ↓
BASE + filename
       ↓
Filesystem
```

Unsafe handling of values containing:

```text
../
..\
```

could cause files to be written outside the intended upload directory.

This is especially relevant when applications preserve original filenames.

See:

```text
Path Traversal
```

for the complete methodology.

---

# Generate Server-Side Filenames

A safer design is:

```text
Original:

Quarterly Report.pdf

        ↓

Application Generates:

550e8400-e29b-41d4-a716-446655440000.pdf
```

The original filename can be stored separately as metadata for display.

This separates:

```text
User-Controlled Display Name
```

from:

```text
Filesystem Name
```

---

# Content-Type Validation

Multipart uploads normally include a Content-Type.

Example:

```http
Content-Disposition: form-data; name="file"; filename="test.pdf"
Content-Type: application/pdf
```

This value is supplied by the client.

Therefore:

> Content-Type alone is not proof of the actual file type.

---

# Content-Type Manipulation

Suppose a text file is rejected:

```http
Content-Type: text/plain
```

Changing only the header to:

```http
Content-Type: application/pdf
```

tests whether the application trusts the multipart header.

If the file is then accepted, validation may rely too heavily on attacker-controlled metadata.

---

# Common MIME Types

Examples include:

```text
PDF
application/pdf

JPEG
image/jpeg

PNG
image/png

GIF
image/gif

SVG
image/svg+xml

ZIP
application/zip

XML
application/xml
text/xml

CSV
text/csv

DOCX
application/vnd.openxmlformats-officedocument.wordprocessingml.document

XLSX
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

MIME types are useful validation signals, but they should not be trusted independently.

---

# File Signatures and Magic Bytes

Many file formats begin with characteristic bytes.

Examples:

```text
PDF
%PDF-

PNG
89 50 4E 47 0D 0A 1A 0A

JPEG
FF D8 FF

GIF
GIF87a
GIF89a

ZIP
PK
```

DOCX, XLSX and PPTX are ZIP-based formats and therefore commonly begin with ZIP signatures.

---

# Magic Byte Validation

An application may check:

```text
Extension
+
Content-Type
+
Magic Bytes
```

This is stronger than checking the extension alone.

However:

> Valid magic bytes do not prove that the complete file is safe.

A file can have a legitimate signature and still contain malicious or unexpected internal content.

---

# Structural Validation

Where possible, validate the complete file structure.

For example:

```text
PDF
  ↓
PDF Parser

JPEG
  ↓
Image Decoder

DOCX
  ↓
ZIP + OOXML Validation
```

This provides stronger assurance than:

```text
First four bytes look correct
```

---

# Polyglot Files

A polyglot file is structured so that it may be interpreted as more than one file format.

This matters because:

```text
Upload Validator
```

may interpret the file differently from:

```text
Browser
Backend Parser
Image Library
Document Processor
Web Server
```

Testing should therefore consider:

```text
How does each component interpret the uploaded object?
```

---

# Images

Image uploads deserve their own testing.

Potential concerns include:

```text
Extension validation
MIME validation
Image parser vulnerabilities
Metadata
Stored XSS through metadata
Oversized dimensions
Resource consumption
Image conversion
Filename handling
SVG
```

---

# Image Re-Encoding

A useful defensive control is:

```text
Uploaded Image
      ↓
Decode
      ↓
Validate
      ↓
Re-encode
      ↓
Store New Image
```

This can remove unexpected data from image files.

It also confirms that the file can actually be decoded as the expected image format.

---

# Image Metadata

Images may contain metadata such as:

```text
EXIF
IPTC
XMP
Comments
Title
Author
Description
GPS data
```

Applications that extract and display metadata must encode it safely.

Potential flow:

```text
Image
  ↓
Metadata Parser
  ↓
Database
  ↓
Administrative Interface
```

Metadata can therefore become another stored input source.

---

# SVG Uploads

SVG deserves special attention because:

> SVG is XML.

An SVG may contain:

```text
XML
Links
External resources
Scripts
Event handlers
```

depending on how it is processed and delivered.

Potential security concerns include:

```text
Stored XSS
XXE
External resource loading
Information disclosure
Browser execution
```

---

# SVG Workflow

```text
Upload SVG
    ↓
Does Server Accept It?
    ↓
Is It Parsed?
    ↓
Is It Sanitised?
    ↓
Is It Re-Encoded?
    ↓
How Is It Served?
    ↓
What Content-Type?
    ↓
Inline or Attachment?
```

If SVG is unnecessary, consider rejecting it.

---

# XML Uploads

XML files should be assessed for:

```text
XXE
External DTD loading
XInclude
Entity expansion
Parser vulnerabilities
Schema validation
```

See:

```text
XML External Entity Injection
```

for the full methodology.

---

# PDF Uploads

PDF upload validation should not stop at:

```text
.pdf extension
```

or:

```text
%PDF-
```

PDF is a complex document format.

Potential risks depend on what happens to the document after upload.

For example:

```text
PDF Uploaded
     ↓
Stored
     ↓
Antivirus Scan
     ↓
PDF Parser
     ↓
Thumbnail Generator
     ↓
Text Extraction
     ↓
User Download
     ↓
PDF Reader
```

Each component creates a different security boundary.

---

# PDF Security Questions

For PDF uploads, determine:

```text
Is the extension validated?

Is Content-Type validated?

Is the PDF structure parsed?

Is malware scanning performed?

Is JavaScript inside PDFs permitted?

Are embedded files permitted?

Are launch actions permitted?

Are external links rewritten?

Is Content Disarm and Reconstruction used?

Are thumbnails generated?

Is text extracted?

Is the original PDF preserved?

Can another user download it?

Is it opened inline in the browser?

Is it forced as an attachment?
```

---

# PDF Validation vs PDF Safety

A PDF can be:

```text
Structurally valid
```

while still being:

```text
Unsafe for a vulnerable PDF reader
```

Therefore:

```text
File Type Validation
```

and:

```text
Malware / Exploit Detection
```

are separate controls.

This distinction is important during security assessments.

---

# Antivirus Testing

If the application claims to perform antivirus or malware scanning, a safe standard test is:

```text
EICAR
```

EICAR provides a harmless test file specifically designed to verify antivirus detection.

It does not contain real malware.

---

# EICAR Test String

The standard EICAR test string is:

```text
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

Save it as:

```text
eicar.com
```

or another filename appropriate to the authorised test.

The file should contain exactly the test string.

---

# Creating an EICAR Test File on Linux

For example:

```bash
printf '%s' 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar.com
```

Then verify:

```bash
cat eicar.com
```

Your local antivirus may immediately quarantine or delete it.

That is expected behaviour.

---

# Creating EICAR with PowerShell

For example:

```powershell
Set-Content `
  -Path ".\eicar.com" `
  -NoNewline `
  -Value 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
```

Microsoft Defender or another endpoint security product may immediately detect the file.

---

# EICAR Upload Workflow

A useful test is:

```text
Create EICAR
     ↓
Upload Through Normal Interface
     ↓
Observe Response
     ↓
Was Upload Blocked?
     ↓
Was File Quarantined?
     ↓
Can File Be Retrieved?
     ↓
Check Application Logs if Available
```

Expected secure behaviour may include:

```text
Upload rejected
File quarantined
File unavailable to users
Security event generated
```

---

# EICAR Inside an Allowed File Type

A useful distinction is between:

```text
Extension Validation
```

and:

```text
Content Scanning
```

For example, if an application allows `.txt`, placing the EICAR test string inside:

```text
eicar.txt
```

can help determine whether scanning is based on actual file content rather than extension alone.

Do this only when malware detection testing is explicitly within scope.

---

# EICAR and Archives

Another useful antivirus validation scenario is an EICAR file inside a permitted archive.

Conceptually:

```text
ZIP
 ↓
EICAR Test File
```

This can determine whether the security pipeline inspects archive contents.

Important questions include:

```text
Are archives scanned recursively?

How many levels?

Are encrypted archives accepted?

What happens if extraction fails?

Is the archive available before scanning completes?
```

---

# Malware Scanning Workflow

A secure upload pipeline may look like:

```text
Upload
  ↓
Temporary Quarantine
  ↓
Type Validation
  ↓
Malware Scan
  ↓
Optional CDR
  ↓
Approved?
  ↓
Permanent Storage
```

The file should not become available to other users before the security pipeline completes.

---

# Fail Open vs Fail Closed

An important test is what happens when the scanning service fails.

Conceptually:

```text
Upload
  ↓
Scanner Unavailable
  ↓
?
```

Secure behaviour should generally be:

```text
Quarantine / Reject / Retry
```

rather than:

```text
Scanner Failed
     ↓
Assume Safe
```

This is commonly described as:

```text
Fail Closed
```

rather than:

```text
Fail Open
```

---

# Race Conditions

Check whether an uploaded file becomes available before scanning finishes.

Potential flow:

```text
Upload
   ↓
File Stored
   ↓
Public URL Created
   ↓
Scanner Runs Later
```

This creates a window where:

```text
Unscanned File
```

may be retrievable.

A safer design is:

```text
Upload
   ↓
Quarantine
   ↓
Scan
   ↓
Approve
   ↓
Publish
```

---

# Malicious Document Detection

EICAR validates antivirus integration, but it does not prove that the system detects every malicious document.

A separate security question is:

> Does the upload pipeline identify weaponised but structurally valid documents?

This is particularly relevant for:

```text
PDF
Office documents
Archives
Images
```

because these formats are frequently processed or opened by other software.

---

# Legacy Client-Side PDF Exploit Example

A historical example is the Metasploit module:

```text
exploit/windows/fileformat/adobe_utilprintf
```

OffSec's Metasploit Unleashed documentation demonstrates this as a client-side file format exploit against:

```text
Adobe Reader v8.1.2
Windows XP SP3 English
```

This is useful for understanding an important upload-security distinction:

```text
Valid PDF
   ↓
Accepted by Upload Validation
   ↓
Document Delivered to User
   ↓
Vulnerable Reader Opens Document
   ↓
Client-Side Exploitation
```

The vulnerable component in this scenario is the legacy Adobe Reader client.

---

# Historical Metasploit Example

The historical workflow documented by OffSec uses:

```text
msfconsole
```

and selects:

```text
exploit/windows/fileformat/adobe_utilprintf
```

The module allows an output filename to be configured, for example:

```text
BestComputers-UpgradeInstructions.pdf
```

The OffSec example demonstrates the broader class of:

```text
Client-Side File Format Exploitation
```

where a crafted document targets a vulnerability in software used to open the document.

For modern authorised assessments, reproduce this type of test only in an isolated lab containing the intended vulnerable client.

---

# Why This Matters for Upload Testing

Suppose an application performs:

```text
Extension Check      → PASS
MIME Check           → PASS
Magic Byte Check     → PASS
PDF Structure Check  → PASS
```

A crafted PDF might still present risk to downstream software.

Therefore:

```text
Valid File Type
```

does not necessarily mean:

```text
Safe Content
```

The security pipeline should consider the application's threat model.

---

# Safe Testing Hierarchy

For an upload assessment, use progressively stronger testing only when necessary.

```text
1. Harmless valid file

2. Extension manipulation

3. Content-Type manipulation

4. Signature mismatch

5. Harmless filename markers

6. EICAR

7. Parser-specific malformed test file

8. Controlled security research artefact

9. Weaponised client-side document
```

Steps involving actual exploitation should require explicit scope and isolated systems.

In most upload assessments:

```text
EICAR
+
Validation testing
+
Parser testing
```

provides sufficient evidence.

---

# Do Not Confuse Antivirus With File Validation

These controls answer different questions.

```text
Extension Validation
      ↓
Is this extension permitted?

MIME Validation
      ↓
Does the claimed media type match policy?

Signature Validation
      ↓
Does the file resemble the expected format?

Structural Validation
      ↓
Is this a valid instance of the format?

Antivirus
      ↓
Does security tooling recognise malicious content?

CDR
      ↓
Can potentially dangerous active content be removed?
```

A secure upload system may need several of these.

---

# Content Disarm and Reconstruction

For complex document formats, Content Disarm and Reconstruction can provide additional protection.

Conceptually:

```text
Original Document
       ↓
Parse
       ↓
Extract Safe Content
       ↓
Remove Active / Unexpected Content
       ↓
Rebuild Document
       ↓
Safe Version
```

CDR may be appropriate for:

```text
PDF
DOCX
XLSX
PPTX
```

depending on application requirements.

---

# Office Documents

Office formats deserve particular attention.

Examples:

```text
.docx
.xlsx
.pptx
```

These formats are ZIP containers containing structured XML and other resources.

Testing should consider:

```text
Extension
MIME
ZIP structure
OOXML structure
Macros where applicable
External relationships
Embedded files
Malware scanning
Parser behaviour
```

---

# Macro-Enabled Office Formats

Examples include:

```text
.docm
.xlsm
.pptm
```

If macros are unnecessary, they should normally not be accepted.

A policy that permits:

```text
.docx
```

should not automatically permit:

```text
.docm
```

The extensions represent materially different security characteristics.

---

# XLSX Uploads

XLSX is:

```text
ZIP
  ↓
OOXML Files
```

Applications may:

```text
Parse worksheets
Extract formulas
Import data
Read metadata
Process external relationships
```

Testing should therefore examine the backend spreadsheet parser rather than only the `.xlsx` extension.

---

# CSV Uploads

CSV files are simple, but downstream spreadsheet software may interpret cells beginning with certain characters as formulas.

Potential flow:

```text
User Uploads CSV
      ↓
Application Stores Data
      ↓
Administrator Exports / Opens Data
      ↓
Spreadsheet Application
```

This is commonly known as:

```text
CSV Injection
Formula Injection
```

It deserves separate testing when uploaded or exported CSV data will be opened in spreadsheet software.

---

# ZIP Uploads

Archive uploads create additional attack surfaces.

Questions include:

```text
Are archive contents inspected?

Are nested archives allowed?

Are encrypted archives allowed?

Are extracted paths validated?

Are symlinks permitted?

Are file counts limited?

Is decompressed size limited?

Are extracted file types validated?
```

---

# Zip Slip

Archive entries can contain paths.

Conceptually:

```text
Archive Entry
../../some-file
```

If extraction does not verify the final destination:

```text
ZIP
 ↓
Extract
 ↓
Traversal
 ↓
File Written Outside Destination
```

This is known as:

```text
Zip Slip
```

See:

```text
Path Traversal
```

for related filesystem methodology.

---

# ZIP Bombs

Compressed archives can expand to extremely large sizes.

Potential impact includes:

```text
Disk exhaustion
Memory exhaustion
CPU consumption
Application instability
Scanner exhaustion
```

Controls should consider:

```text
Compressed size
Decompressed size
Compression ratio
Number of entries
Nested archive depth
Processing time
```

Do not test destructive decompression ratios against production systems without explicit authorisation.

---

# Password-Protected Archives

Encrypted archives can prevent malware scanners from inspecting the contents.

Questions include:

```text
Are encrypted ZIPs accepted?

Can the scanner inspect them?

Are they quarantined?

Does the application ask for a password?

Are they delivered unchanged to another user?
```

If content inspection is mandatory, encrypted archives may need to be rejected.

---

# Archive Symlinks

Archive formats can potentially contain symbolic links.

Unsafe extraction may cause unexpected filesystem access.

Secure extraction should validate:

```text
Entry path
Canonical destination
Symlink behaviour
Hard links
Final filesystem location
```

---

# File Size Validation

Test:

```text
Maximum allowed size
Zero-byte files
Very small files
Boundary values
Slightly over limit
```

For example, if the documented maximum is:

```text
5 MB
```

test:

```text
4.9 MB
5.0 MB
5.1 MB
```

Determine whether the limit is enforced:

```text
Client side
Reverse proxy
Application
Storage layer
```

---

# Empty Files

Upload:

```text
0-byte file
```

and observe behaviour.

Potential issues include:

```text
Parser exceptions
Unhandled errors
Broken preview generation
Incorrect validation
```

---

# File Count Limits

If multiple files can be uploaded, determine:

```text
Maximum files per request
Maximum files per account
Maximum aggregate size
Rate limits
Storage quotas
```

This is relevant to denial-of-service resistance.

---

# Duplicate Files

Upload the same file multiple times.

Observe whether the application:

```text
Creates duplicates
Overwrites
Versions
Rejects
Renames
Deduplicates
```

This helps understand storage behaviour.

---

# Filename Collisions

Test two harmless files with the same filename.

For example:

```text
test.pdf
test.pdf
```

Questions include:

```text
Does the second overwrite the first?

Does the application generate a new name?

Can one user overwrite another user's file?

Does the database point to the correct object?
```

---

# Storage Location

Determine where uploads are stored conceptually.

Preferred architecture:

```text
Application
    ↓
Upload Storage
    ↓
Outside Web Root
```

Rather than:

```text
Web Root
   ↓
/uploads/
   ↓
User-Controlled Files
```

If files must be web-accessible, they should be served through a controlled retrieval mechanism.

---

# Separate Storage Host

A stronger architecture may use:

```text
Main Application
       ↓
Object Storage / Dedicated File Host
```

with:

```text
No script execution
Restricted Content-Type
Controlled Content-Disposition
Random object names
Access control
```

This reduces the consequences of upload validation failures.

---

# Direct File Access

After uploading, determine whether the file receives a predictable URL.

Example:

```text
/uploads/test.pdf
```

Questions include:

```text
Can it be accessed without authentication?

Can another user access it?

Is the URL predictable?

Is authorisation checked?

Does deletion actually remove access?

Can old versions still be accessed?
```

---

# Access Control

Upload security includes authorisation.

Test whether:

```text
User A uploads file
        ↓
User B guesses / obtains identifier
        ↓
Can User B retrieve it?
```

This is an IDOR / broken access control question rather than an upload validation issue, but it belongs in the upload workflow.

---

# File Deletion

Test:

```text
Upload
  ↓
Delete
  ↓
Request Old URL
```

Determine whether the file is:

```text
Actually deleted
Soft deleted
Still directly accessible
Cached
Retained in object storage
```

---

# Content-Disposition

Files should often be delivered with:

```http
Content-Disposition: attachment
```

where inline rendering is unnecessary.

A response such as:

```http
Content-Disposition: attachment; filename="report.pdf"
```

encourages download rather than inline browser rendering.

This can reduce browser-based attack surface for some file types.

---

# Content-Type on Retrieval

Check whether the application returns the correct Content-Type.

A file uploaded as:

```text
test.txt
```

should not unexpectedly be returned as:

```text
text/html
```

if that creates active browser interpretation.

Consider:

```http
X-Content-Type-Options: nosniff
```

where appropriate.

---

# Content Sniffing

Browsers may historically attempt to infer content type.

A defensive header is:

```http
X-Content-Type-Options: nosniff
```

This helps prevent browsers from interpreting content as a different MIME type than declared.

---

# HTML Uploads

If HTML uploads are allowed and later served from the application's origin, they can create a stored content execution risk.

Conceptually:

```text
Upload HTML
    ↓
Same Origin Storage
    ↓
Victim Opens File
    ↓
Browser Processes HTML
```

Consider whether HTML needs to be accepted at all.

---

# JavaScript Files

Similarly, accepting:

```text
.js
```

may be dangerous if the file can later be served from a trusted application origin.

File extension policies should reflect the intended business use case.

---

# Server-Side Executable Extensions

Applications should generally reject server-side executable file types from untrusted upload functionality.

Examples vary by platform and include categories such as:

```text
Server-side scripts
Executable binaries
Web server configuration files
Application packages
```

The safest policy is:

```text
Allow only explicitly required business file types.
```

---

# Upload Location and Execution

A particularly dangerous architecture is:

```text
User Upload
    ↓
Web Root
    ↓
Executable Directory
```

A safer design is:

```text
User Upload
    ↓
Non-Executable Storage
    ↓
Controlled Download Handler
```

Filesystem and web server permissions should prevent execution from upload storage.

---

# Web Server Configuration

Upload directories should not permit:

```text
Script execution
Server-side includes
Dynamic handler execution
Directory listing
Configuration overrides
```

unless explicitly required.

This provides defence in depth if validation fails.

---

# Parser Attack Surface

Even when files are never directly served, backend processing can create vulnerabilities.

Examples:

```text
ImageMagick
PDF libraries
Office parsers
XML parsers
Archive libraries
Video processors
OCR engines
Document converters
Antivirus engines
```

The processing pipeline itself must therefore be patched and isolated.

---

# Thumbnail Generation

Image and PDF uploads often trigger:

```text
Thumbnail Generation
```

Conceptually:

```text
Upload
  ↓
Parser
  ↓
Renderer
  ↓
Thumbnail
```

This means an upload can attack the server-side rendering library even if the original file is never directly exposed.

---

# PDF Conversion

Applications may convert:

```text
DOCX → PDF
HTML → PDF
PDF → Image
```

Each converter introduces additional security considerations.

Questions include:

```text
Can the converter access the network?

Can it access local files?

Does it execute active content?

Is it sandboxed?

Is it patched?
```

This can overlap with:

```text
SSRF
Local File Read
Command Injection
Parser Vulnerabilities
```

---

# Asynchronous Processing

Uploads may be processed after the HTTP response.

Example:

```text
Upload
  ↓
202 Accepted
  ↓
Queue
  ↓
Background Worker
  ↓
Parser
```

Therefore, security testing may require monitoring behaviour after the initial request.

This is particularly relevant for:

```text
Antivirus
Thumbnail generation
OCR
Document conversion
Indexing
Metadata extraction
```

---

# Blind Interactions

Backend document processors may make external requests.

Where authorised, controlled callback infrastructure can help determine whether uploaded content causes server-side interactions.

Examples include:

```text
Burp Collaborator
Interactsh
```

This overlaps with:

```text
Blind XXE
SSRF
Document parser testing
```

Use unique identifiers to correlate callbacks.

---

# Burp Suite Workflow

Burp is extremely useful for file upload testing.

```text
Browser
  ↓
Upload Valid File
  ↓
Burp Proxy
  ↓
HTTP History
  ↓
Send to Repeater
  ↓
Modify One Property
  ↓
Send
  ↓
Observe Server Behaviour
```

---

# Burp Repeater

Repeater should be the primary manual tool.

Useful modifications include:

```text
Filename
Extension
Content-Type
File content
Multipart field name
Additional form fields
Boundary conditions
```

Change one dimension at a time.

---

# Example Multipart Request

```http
POST /upload HTTP/1.1
Host: target.example
Content-Type: multipart/form-data; boundary=BOUNDARY

--BOUNDARY
Content-Disposition: form-data; name="file"; filename="test.pdf"
Content-Type: application/pdf

%PDF-
TEST
--BOUNDARY--
```

This is useful for understanding which part of the request the server validates.

---

# Extension vs Content-Type Matrix

A useful testing matrix is:

| Filename | Content-Type | Actual Content | Purpose |
|---|---|---|---|
| `test.pdf` | `application/pdf` | PDF | Baseline |
| `test.pdf` | `text/plain` | PDF | MIME validation |
| `test.txt` | `application/pdf` | Text | Header trust |
| `test.pdf` | `application/pdf` | Text | Structural validation |
| `test.PDF` | `application/pdf` | PDF | Case handling |
| `test.txt.pdf` | `application/pdf` | PDF | Multiple extension handling |

The objective is to determine which validation layers actually exist.

---

# Burp Intruder

Intruder can help test filename and extension handling systematically.

Potential payload positions include:

```text
filename="§test.pdf§"
```

or only the extension:

```text
filename="test.§pdf§"
```

Use a focused payload list.

For example:

```text
pdf
PDF
Pdf
txt
jpg
png
svg
xml
zip
```

Analyse:

```text
Status
Length
Response message
Upload identifier
```

---

# Burp Match and Replace

For repetitive testing, Burp Match and Replace can help modify headers such as:

```text
Content-Type
```

Use carefully so that you understand which requests are being changed.

---

# Browser DevTools

DevTools can reveal:

```text
Accepted extensions
JavaScript validation
Upload API
File size restrictions
Preview functionality
Client-side MIME checks
```

But client-side validation is not a security boundary.

Always verify server-side behaviour.

---

# curl Upload Testing

A normal multipart upload can be reproduced with:

```bash
curl -i \
  -F 'file=@test.pdf;type=application/pdf' \
  https://target.example/upload
```

For authenticated endpoints:

```bash
curl -i \
  -H 'Cookie: session=REDACTED' \
  -F 'file=@test.pdf;type=application/pdf' \
  https://target.example/upload
```

Never place real session credentials in public documentation.

---

# File Command

On Linux, identify a file with:

```bash
file test.pdf
```

Example:

```text
test.pdf: PDF document
```

This is useful when checking whether a test file actually has the intended structure.

---

# xxd

Inspect the beginning of a file:

```bash
xxd -l 32 test.pdf
```

This is useful for checking signatures.

For example, a PDF should normally begin with something resembling:

```text
%PDF-
```

---

# unzip

For ZIP-based formats:

```bash
unzip -l test.xlsx
```

or:

```bash
unzip -l test.docx
```

This helps inspect the internal OOXML structure.

---

# exiftool

Metadata can be inspected with:

```bash
exiftool image.jpg
```

or:

```bash
exiftool document.pdf
```

This helps determine which metadata fields may later be processed or displayed by the application.

---

# ClamAV

In a local lab, ClamAV can be used to understand antivirus behaviour.

For example:

```bash
clamscan eicar.com
```

Expected result:

```text
Eicar-Test-Signature FOUND
```

This provides a useful baseline before testing an application's scanning pipeline.

---

# Source Code Review

When source code is available, trace the complete upload path.

```text
HTTP Upload
    ↓
Controller
    ↓
Validation
    ↓
Filename Generation
    ↓
Storage
    ↓
Scanner
    ↓
Processing
    ↓
Retrieval
```

Do not stop at the upload controller.

---

# Interesting Source Code Terms

Search for:

```text
upload
multipart
filename
extension
mime
content-type
move
save
store
write
temp
scan
virus
clamav
thumbnail
resize
convert
extract
zip
pdf
image
```

---

# PHP Upload Review

Interesting PHP functionality includes:

```text
$_FILES
move_uploaded_file()
pathinfo()
mime_content_type()
finfo_file()
```

Look for unsafe patterns such as relying only on:

```php
$_FILES['file']['type']
```

because this value originates from the request.

---

# Java Upload Review

Interesting Java / Spring functionality includes:

```text
MultipartFile
getOriginalFilename()
getContentType()
transferTo()
Files.copy()
Paths.get()
```

Pay particular attention to:

```text
getOriginalFilename()
```

because the original filename is attacker-controlled.

---

# .NET Upload Review

Interesting ASP.NET functionality includes:

```text
IFormFile
FileName
ContentType
CopyTo
CopyToAsync
Path.GetExtension
```

Review whether:

```text
FileName
```

is used directly in filesystem paths.

---

# Node.js Upload Review

Common libraries and APIs include:

```text
multer
formidable
busboy
express-fileupload
fs.writeFile
fs.createWriteStream
```

Review:

```text
originalname
mimetype
destination
filename
```

and determine which values originate from the user.

---

# Python Upload Review

Common functionality includes:

```text
request.files
FileStorage
save()
secure_filename()
UploadFile
SpooledTemporaryFile
```

For Flask / Werkzeug, functions such as:

```text
secure_filename()
```

can help normalise filenames, but should still be part of a broader secure upload design.

---

# Ruby Upload Review

Look for:

```text
ActionDispatch::Http::UploadedFile
original_filename
content_type
tempfile
ActiveStorage
CarrierWave
Paperclip
```

Review how filenames, content types and storage locations are handled.

---

# Go Upload Review

Interesting Go functionality includes:

```text
FormFile()
multipart.FileHeader
Filename
io.Copy()
os.Create()
filepath.Join()
```

Trace:

```text
FileHeader.Filename
```

to the final storage path.

---

# Source-to-Sink Analysis

A useful model is:

```text
SOURCE
  ↓
Multipart Filename
  ↓
Upload Controller
  ↓
Validation
  ↓
Path Construction
  ↓
Filesystem Write
```

Another:

```text
SOURCE
  ↓
Uploaded File Content
  ↓
Storage
  ↓
PDF Parser
  ↓
Document Converter
```

And:

```text
SOURCE
  ↓
Original Filename
  ↓
Database
  ↓
Admin Interface
  ↓
HTML Rendering
```

These represent three completely different attack surfaces from one upload.

---

# Secure Upload Architecture

A robust architecture can look like:

```text
                 User Upload
                     ↓
              Authentication
                     ↓
              Authorisation
                     ↓
                Size Limit
                     ↓
          Canonicalise Filename
                     ↓
           Extension Allowlist
                     ↓
              MIME Validation
                     ↓
          Signature Validation
                     ↓
         Structural Validation
                     ↓
            Quarantine Storage
                     ↓
              Malware Scan
                     ↓
               CDR if Needed
                     ↓
         Generate Random Filename
                     ↓
          Non-Executable Storage
                     ↓
          Controlled Retrieval
                     ↓
             Authorisation
```

---

# File Upload Validation Checklist

## Discovery

- [ ] Identify every upload feature
- [ ] Identify accepted file types
- [ ] Identify maximum size
- [ ] Identify upload API
- [ ] Identify retrieval API
- [ ] Identify preview functionality
- [ ] Identify backend processing
- [ ] Identify administrative viewers

## Baseline

- [ ] Upload valid file
- [ ] Capture request
- [ ] Record multipart field
- [ ] Record filename
- [ ] Record Content-Type
- [ ] Record response
- [ ] Record returned identifier
- [ ] Locate retrieval URL

## Extension Validation

- [ ] Allowed extension
- [ ] Disallowed extension
- [ ] Uppercase extension
- [ ] Mixed-case extension
- [ ] Double extension
- [ ] Multiple dots
- [ ] Trailing dot
- [ ] Trailing space
- [ ] Long filename
- [ ] Encoded filename

## MIME Validation

- [ ] Correct MIME
- [ ] Incorrect MIME
- [ ] Allowed MIME with incorrect content
- [ ] Disallowed MIME with correct content
- [ ] Determine whether multipart Content-Type is trusted

## Signature Validation

- [ ] Valid signature
- [ ] Invalid signature
- [ ] Correct extension with incorrect signature
- [ ] Incorrect extension with correct signature
- [ ] Determine whether complete structure is parsed

## Filename Handling

- [ ] Special characters
- [ ] HTML characters
- [ ] Unique marker
- [ ] Stored filename
- [ ] Displayed filename
- [ ] Admin interface
- [ ] Download filename
- [ ] Path separators
- [ ] Collision handling
- [ ] Server-generated filename

## Malware Detection

- [ ] Confirm scanning is in scope
- [ ] EICAR test
- [ ] EICAR with permitted extension where appropriate
- [ ] EICAR inside permitted archive where appropriate
- [ ] Verify rejection
- [ ] Verify quarantine
- [ ] Verify file cannot be retrieved
- [ ] Determine fail-open / fail-closed behaviour
- [ ] Determine whether scanning occurs before publication

## PDF

- [ ] `.pdf` extension validation
- [ ] `application/pdf`
- [ ] `%PDF-` signature
- [ ] Structural validation
- [ ] Malware scanning
- [ ] JavaScript policy
- [ ] Embedded file policy
- [ ] CDR where appropriate
- [ ] Thumbnail processing
- [ ] Text extraction
- [ ] Safe retrieval

## Images

- [ ] JPEG
- [ ] PNG
- [ ] GIF
- [ ] SVG
- [ ] Re-encoding
- [ ] Metadata
- [ ] EXIF
- [ ] Image dimensions
- [ ] Parser behaviour
- [ ] Thumbnail generation

## XML / SVG

- [ ] XML parsing
- [ ] DTD processing
- [ ] XXE
- [ ] External resources
- [ ] Browser rendering
- [ ] Sanitisation

## Office

- [ ] DOCX
- [ ] XLSX
- [ ] PPTX
- [ ] Macro-enabled formats
- [ ] External relationships
- [ ] Embedded content
- [ ] Malware scanning
- [ ] CDR

## Archives

- [ ] ZIP
- [ ] TAR
- [ ] Nested archives
- [ ] Encrypted archives
- [ ] Entry count
- [ ] Decompressed size
- [ ] Compression ratio
- [ ] Zip Slip
- [ ] Symlinks
- [ ] Extracted extension validation

## Storage

- [ ] Outside web root
- [ ] Non-executable
- [ ] Random server-side name
- [ ] Least privilege
- [ ] No directory listing
- [ ] No configuration override
- [ ] Quarantine before approval

## Retrieval

- [ ] Authentication
- [ ] Authorisation
- [ ] IDOR
- [ ] Predictable URL
- [ ] Content-Type
- [ ] Content-Disposition
- [ ] `X-Content-Type-Options`
- [ ] Deleted file behaviour
- [ ] Cache behaviour

## Processing

- [ ] Antivirus
- [ ] CDR
- [ ] Thumbnail generation
- [ ] PDF parser
- [ ] Image parser
- [ ] Office parser
- [ ] Archive extraction
- [ ] OCR
- [ ] Conversion
- [ ] Indexing
- [ ] Asynchronous processing

## Burp

- [ ] Proxy
- [ ] HTTP History
- [ ] Repeater
- [ ] Intruder
- [ ] Filename manipulation
- [ ] Content-Type manipulation
- [ ] File content manipulation
- [ ] Compare responses

## Source Review

- [ ] Find upload controller
- [ ] Trace original filename
- [ ] Trace MIME type
- [ ] Trace extension validation
- [ ] Trace signature validation
- [ ] Trace storage path
- [ ] Trace antivirus integration
- [ ] Trace parser pipeline
- [ ] Trace retrieval endpoint
- [ ] Review authorisation

## Validation

- [ ] Confirm server-side weakness
- [ ] Confirm repeatability
- [ ] Use harmless artefacts first
- [ ] Use EICAR for antivirus validation
- [ ] Avoid unnecessary weaponisation
- [ ] Collect minimal evidence
- [ ] Stop after sufficient proof

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | Intercept and manipulate uploads |
| Burp Repeater | Manual upload validation |
| Burp Intruder | Extension and filename testing |
| curl | Reproduce multipart requests |
| EICAR | Safe antivirus validation |
| `file` | File type identification |
| `xxd` | Signature inspection |
| `unzip` | ZIP / OOXML inspection |
| ExifTool | Metadata inspection |
| ClamAV | Local antivirus testing |
| Interactsh | Controlled backend interaction detection |
| Burp Collaborator | OOB processing tests |
| Nuclei | Targeted automated checks |
| grep / ripgrep | Upload sink discovery |
| Semgrep | Structured source review |

---

# Tool Selection

| Situation | Tool |
|---|---|
| Understand upload request | Burp Proxy |
| Manual validation | Burp Repeater |
| Extension matrix | Burp Intruder |
| CLI reproduction | curl |
| AV validation | EICAR |
| Inspect type | `file` |
| Inspect magic bytes | `xxd` |
| Inspect Office files | `unzip` |
| Inspect metadata | ExifTool |
| Local AV baseline | ClamAV |
| Blind backend behaviour | Collaborator / Interactsh |
| Source review | grep / ripgrep / Semgrep |

---

# Quick Reference

```text
UPLOAD SECURITY

Extension
   +
MIME
   +
Signature
   +
Structure
   +
Filename
   +
Size
   +
Malware Scan
   +
CDR
   +
Storage
   +
Processing
   +
Retrieval
   +
Authorisation
```

```text
Useful Test Files

Normal PDF
Normal JPEG
Normal PNG
Normal TXT
Normal ZIP
EICAR
```

```text
Useful Filename Tests

test.pdf
test.PDF
test.Pdf
test.txt.pdf
test.pdf.txt
test.pdf.
AM-FILENAME-12345.pdf
```

```text
PDF

.pdf
 ↓
application/pdf
 ↓
%PDF-
 ↓
Structural validation
 ↓
Malware scan
 ↓
CDR if required
 ↓
Safe storage
```

```text
Antivirus

Upload
 ↓
Quarantine
 ↓
EICAR
 ↓
Scanner
 ↓
Detection
 ↓
Reject / Quarantine
```

```text
Always establish:

FILE
 ↓
VALIDATION
 ↓
STORAGE
 ↓
PROCESSING
 ↓
RETRIEVAL
 ↓
SECURITY IMPACT
```

---

# Practical Workflow Summary

```text
                 ┌───────────────────────┐
                 │ Find Upload Function  │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Upload Valid File     │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Capture with Burp     │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Extension Validation  │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ MIME Validation       │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Signature / Structure │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Filename Handling     │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Malware Detection     │
                 │ EICAR                 │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Backend Processing    │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Storage / Retrieval   │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Access Control        │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Determine Impact      │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Report                │
                 └───────────────────────┘
```

---

# Example Finding: Insufficient File Type Validation

```text
Title
Insufficient Server-Side File Type Validation

Affected Function
Document Upload

Description
The application does not sufficiently validate uploaded files.

Testing demonstrated that validation relied on attacker-controlled
file metadata rather than independently validating the actual file
format.

Impact
An authenticated attacker may be able to store files outside the
intended set of permitted document types.

The resulting impact depends on how uploaded files are stored,
processed and subsequently delivered to users.

Recommendation
Implement defence-in-depth upload validation.

Validate the final extension against an explicit allowlist, verify
the expected file signature and structure, generate server-side
filenames and store uploaded objects in non-executable storage.

Complex document formats should additionally be scanned for
malicious content before becoming available to users.
```

---

# Example Finding: Malware Detection Missing

```text
Title
Uploaded Files Are Not Scanned for Malicious Content

Affected Function
Document Upload

Description
The application accepts user-controlled documents that can
subsequently be downloaded by other users.

Testing using the standard EICAR antivirus test file demonstrated
that recognised malicious test content was accepted, stored and
remained available for retrieval.

Impact
The application may be used as a distribution mechanism for
malicious files.

Users who trust documents delivered through the application could
be exposed to malicious content.

Recommendation
Integrate malware scanning into the upload pipeline.

Uploaded files should remain quarantined until scanning completes
successfully.

If the scanner is unavailable or returns an error, the file should
remain unavailable rather than being automatically treated as safe.
```

---

# Example Finding: Unsafe Filename Rendering

```text
Title
Uploaded Filenames Are Rendered Without Sufficient Output Encoding

Affected Function
Document Management

Description
User-controlled filenames are stored and subsequently displayed in
the application.

The application does not consistently encode the filename for the
HTML context in which it is rendered.

Impact
Depending on the affected rendering context, attacker-controlled
filenames may alter application content or potentially create a
stored cross-site scripting condition.

Recommendation
Treat original filenames as untrusted data.

Generate separate server-side storage names and apply
context-appropriate output encoding whenever original filenames are
displayed.
```

---

# Example Finding: Upload Published Before Scan

```text
Title
Uploaded Files Become Accessible Before Malware Scanning Completes

Description
Uploaded documents become retrievable immediately after upload,
while malware scanning occurs asynchronously.

This creates a period during which an unscanned document can be
downloaded by another user.

Recommendation
Store newly uploaded files in a quarantine state.

Only publish or expose the file after all required validation and
malware scanning stages complete successfully.
```

---

# Reporting File Upload Findings

Avoid reporting:

```text
The application allows PDF uploads.
```

That is expected functionality.

Instead establish the failed security control:

```text
Extension validation bypass

Content-Type trusted without verification

File signature not validated

File structure not validated

Malware scanning absent

EICAR accepted and retrievable

Unsafe filename rendering

Path traversal through filename

Upload stored in executable location

File accessible without authorisation

SVG rendered unsafely

Archive extraction traversal

Scanner failure causes fail-open behaviour
```

A useful reporting model is:

```text
INPUT
  ↓
FAILED CONTROL
  ↓
PROCESSING / STORAGE
  ↓
EXPOSURE
  ↓
SECURITY IMPACT
```

---

# References

## OWASP File Upload Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html

This should be the primary defensive reference for this page.

OWASP recommends a defence-in-depth upload strategy including extension allowlisting, not trusting Content-Type alone, filename controls, file size restrictions, storage outside the web root where possible, antivirus or sandbox analysis where appropriate, CDR for applicable document types and appropriate access controls.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

Useful for the wider web application testing methodology surrounding upload functionality.

---

## PortSwigger Web Security Academy

### File Upload Vulnerabilities

https://portswigger.net/web-security/file-upload

PortSwigger provides practical material covering file upload validation, content types, extensions and server-side file handling.

---

## EICAR

### Anti-Malware Test File

https://www.eicar.org/download-anti-malware-testfile/

EICAR provides the standard harmless antivirus test file used to verify malware detection systems without using real malicious software.

---

## OffSec Metasploit Unleashed

### Client Side Exploits

https://www.offsec.com/metasploit-unleashed/client-side-exploits/

The OffSec documentation demonstrates client-side exploitation using Metasploit file-format modules, including the historical Adobe `util.printf()` PDF example.

The documented target is:

```text
Adobe Reader v8.1.2
Windows XP SP3 English
```

This example is useful for understanding why:

```text
Valid File Format
```

does not automatically mean:

```text
Safe File
```

It should be reproduced only in an isolated authorised lab containing the intentionally vulnerable client.

---

## PayloadsAllTheThings

### Upload Insecure Files

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files

Useful reference for file upload validation and application-specific behaviours.

---

## HackTricks

### File Upload

https://book.hacktricks.wiki/en/pentesting-web/file-upload/index.html

Additional practical reference covering file upload security testing.

---

## ProjectDiscovery Nuclei

https://github.com/projectdiscovery/nuclei

Useful for targeted automated checks with manual validation.

---

## Interactsh

https://github.com/projectdiscovery/interactsh

Useful when authorised backend file processing tests require controlled out-of-band interaction detection.

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
├── Path Traversal
├── File Inclusion
└── File Upload
```

File Upload connects particularly strongly with:

```text
File Upload
    │
    ├── Filename
    │      ↓
    │   Stored / Blind XSS
    │
    ├── Storage Path
    │      ↓
    │   Path Traversal
    │
    ├── SVG / XML
    │      ↓
    │   XXE / XSS
    │
    ├── Backend URL Fetching
    │      ↓
    │   SSRF
    │
    ├── File Inclusion
    │      ↓
    │   Uploaded File + LFI
    │
    ├── ZIP Extraction
    │      ↓
    │   Zip Slip
    │
    ├── Document Processing
    │      ↓
    │   Parser Attack Surface
    │
    └── Retrieval
           ↓
        Authorisation / IDOR
```

---

# Final Testing Principle

Do not reduce file upload testing to:

```text
Can I upload a forbidden extension?
```

Instead ask:

```text
What can I upload?
        ↓
How is the extension validated?
        ↓
How is the actual format validated?
        ↓
Is the content scanned?
        ↓
How is the filename handled?
        ↓
Where is the file stored?
        ↓
What processes the file?
        ↓
When does it become available?
        ↓
Who can retrieve it?
        ↓
How does the browser handle it?
        ↓
What happens when it is deleted?
        ↓
What is the actual security impact?
```

The complete security boundary is:

```text
UNTRUSTED FILE
      ↓
VALIDATION
      ↓
QUARANTINE
      ↓
SCANNING
      ↓
PROCESSING
      ↓
STORAGE
      ↓
RETRIEVAL
      ↓
CONSUMER
```

That is the model to use when assessing file upload functionality.
