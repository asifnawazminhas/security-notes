# File Inclusion

File Inclusion vulnerabilities occur when an application uses attacker-controlled input to determine which file is loaded or included by the application.

The most common forms are:

```text
Local File Inclusion (LFI)
Remote File Inclusion (RFI)
```

Local File Inclusion causes the application to include a file available to the server.

Remote File Inclusion occurs when the application can include content from a remote location.

File inclusion is closely related to Path Traversal, but the vulnerabilities are not identical.

!!! warning "Authorised Security Testing"
    Perform file inclusion testing only against applications and systems for which you have explicit authorisation. Start with minimally sensitive files and non-destructive validation. Stop once sufficient evidence has been collected.

---

# Mental Model

Consider an application that loads pages dynamically:

```text
?page=home
```

The backend might conceptually perform:

```php
include("pages/" . $_GET["page"] . ".php");
```

Normal behaviour:

```text
page=home

        ↓

pages/home.php
```

Attacker-controlled behaviour could become:

```text
page=../../some-file

        ↓

pages/../../some-file.php
```

The important difference from ordinary path traversal is what happens after the file is located.

```text
Path Traversal

INPUT
  ↓
Filesystem Path
  ↓
File Read


File Inclusion

INPUT
  ↓
Filesystem Path
  ↓
Include / Template Function
  ↓
File Processed by Application
```

This distinction can significantly change the impact.

---

# LFI vs RFI

## Local File Inclusion

LFI references a resource accessible locally to the application.

Conceptually:

```text
User Input
    ↓
Application
    ↓
Include Function
    ↓
Local File
```

Potential consequences include:

```text
Local file disclosure
Source code disclosure
Configuration disclosure
Application information disclosure
Unexpected template inclusion
Potential code execution in specific circumstances
```

---

## Remote File Inclusion

RFI occurs when the application accepts a remote resource as the file to include.

Conceptually:

```text
User Input
    ↓
Application
    ↓
Include Function
    ↓
Remote Resource
```

RFI depends heavily on:

```text
Programming language
Runtime configuration
Include mechanism
URL handler configuration
Network access
Application logic
```

Modern frameworks and secure configurations make classic RFI less common than LFI.

---

# File Inclusion Testing Workflow

A structured workflow can look like:

```text
Map Application
      ↓
Identify File / Template Parameters
      ↓
Establish Baseline
      ↓
Identify Technology
      ↓
Test Path Manipulation
      ↓
Determine Traversal Behaviour
      ↓
Determine Inclusion Behaviour
      ↓
Test Absolute Paths
      ↓
Investigate Filtering
      ↓
Investigate Relevant Wrappers
      ↓
Determine Impact
      ↓
Collect Minimal Evidence
      ↓
Report
```

The objective is not simply to make `/etc/passwd` appear.

Understand:

```text
SOURCE
  ↓
PATH CONSTRUCTION
  ↓
FILE SELECTION
  ↓
INCLUSION SINK
  ↓
APPLICATION BEHAVIOUR
```

---

# Where to Look

File inclusion commonly appears in functionality involving dynamic resources.

Interesting functionality includes:

```text
Page selection
Templates
Themes
Languages
Localisation
Views
Layouts
Modules
Plugins
Documents
Reports
Help pages
Content rendering
Email templates
PDF templates
Configuration imports
Legacy PHP applications
CMS functionality
```

---

# Interesting Parameters

Common parameter names include:

```text
page
file
filename
path
include
inc
template
tpl
view
layout
module
theme
skin
lang
language
locale
content
document
doc
folder
directory
resource
```

Examples:

```text
?page=home
```

```text
?template=invoice
```

```text
?lang=en
```

```text
?view=profile
```

```text
?module=dashboard
```

These are discovery hints rather than proof of vulnerability.

---

# Establish a Baseline

Start with the application's intended behaviour.

Example:

```http
GET /index.php?page=home HTTP/1.1
Host: target.example
```

Record:

```text
Status
Content-Length
Content-Type
Response body
Response time
Errors
Rendered page
```

Then change only the suspected file parameter.

For example:

```text
page=home
```

to:

```text
page=invalid-test-value
```

Observe how the application responds.

---

# Error Messages

File inclusion vulnerabilities frequently reveal useful information through errors.

Potential messages include:

```text
failed to open stream
No such file or directory
include()
require()
FileNotFoundException
Template not found
Unable to load template
View not found
Permission denied
```

A PHP application might reveal something conceptually similar to:

```text
Warning: include(pages/test.php):
failed to open stream
```

This reveals that:

```text
pages/
```

is part of the constructed path.

It may also reveal whether:

```text
.php
```

is automatically appended.

---

# Technology Identification

Technology identification is particularly important for file inclusion.

Determine:

```text
Language
Framework
Operating system
Web server
Template engine
Application server
Runtime version
```

Examples:

```text
PHP
Java
.NET
Python
Node.js
Ruby
```

Classic LFI techniques involving PHP wrappers are obviously relevant only when PHP is involved.

Do not apply technology-specific payloads blindly.

---

# Basic Linux LFI Testing

A Linux application using an unsafe include path may allow traversal sequences such as:

```text
../../../etc/hostname
```

Conceptually:

```text
?page=../../../etc/hostname
```

If the application directly includes the path, the referenced file may become accessible.

Prefer minimally sensitive validation files.

Examples:

```text
/etc/hostname
/etc/os-release
```

A commonly used traditional proof is:

```text
/etc/passwd
```

but it is often unnecessary if a less sensitive file demonstrates the issue.

---

# Basic Windows LFI Testing

For Windows systems, a minimally sensitive validation target may be:

```text
C:\Windows\win.ini
```

Traversal might conceptually use:

```text
..\..\..\Windows\win.ini
```

or, depending on the API:

```text
../../../Windows/win.ini
```

Many Windows filesystem APIs accept both slash styles.

---

# Absolute Paths

Sometimes traversal is unnecessary.

Linux:

```text
/etc/hostname
```

Windows:

```text
C:\Windows\win.ini
```

If attacker-controlled input is passed directly to an include or template function, absolute paths may be accepted.

Test this only after understanding the application's path construction.

---

# Determine Traversal Depth

If the base directory is unknown, traversal depth may need to be determined.

Conceptually:

```text
../
../../
../../../
../../../../
../../../../../
```

Application errors may reveal the underlying path.

For example:

```text
/var/www/application/templates/pages/test.php
```

provides significantly more information than blindly increasing traversal depth.

---

# Excess Traversal

On many systems, traversal beyond the filesystem root may still resolve successfully.

For example:

```text
../../../../../../../../etc/hostname
```

may eventually resolve to:

```text
/etc/hostname
```

This depends on how the application and filesystem APIs process the path.

---

# URL Encoding

Traversal characters may be encoded.

Examples:

```text
../
```

may appear as:

```text
%2e%2e%2f
```

or:

```text
..%2f
```

Windows backslashes may appear as:

```text
%5c
```

Potential representations include:

```text
..%2f..%2f
%2e%2e%2f
.%2e/
%2e./
```

The important question is:

> Which component performs decoding, and when?

---

# Double Encoding

Multiple decoding layers can create situations where:

```text
%252e%252e%252f
```

becomes:

```text
%2e%2e%2f
```

and later:

```text
../
```

The processing chain might look like:

```text
Client
  ↓
WAF
  ↓
Reverse Proxy
  ↓
Framework
  ↓
Application
  ↓
Include Function
```

Different layers may decode the input at different stages.

---

# Nested Traversal

Weak filters sometimes remove literal traversal sequences once.

For example:

```text
replace("../", "")
```

Overlapping sequences may behave unexpectedly after the replacement.

Conceptually:

```text
....//
```

may become:

```text
../
```

after an unsafe transformation.

This is another reason string replacement is not an adequate filesystem security control.

---

# Appended Extensions

A common pattern is:

```php
include("pages/" . $page . ".php");
```

Input:

```text
home
```

becomes:

```text
pages/home.php
```

A traversal attempt therefore also receives:

```text
.php
```

at the end.

Understanding whether an extension is:

```text
Required
Appended
Validated
Replaced
```

is important.

---

# Required Prefixes

Applications may prepend a fixed directory:

```text
/templates/
```

For example:

```text
/templates/ + USER_INPUT
```

Traversal may still be possible if the final canonical path is not validated.

Conceptually:

```text
/templates/../../../some-file
```

The security decision should be based on the final resolved path.

---

# LFI vs Path Traversal

Consider:

```http
GET /download?file=../../../etc/hostname
```

If the server performs:

```text
read file
    ↓
return bytes
```

this is primarily:

```text
Path Traversal / Arbitrary File Read
```

Now consider:

```http
GET /index.php?page=../../../some-file
```

where the server performs:

```php
include($page);
```

The vulnerability is:

```text
Local File Inclusion
```

The path manipulation may be similar.

The sink is different.

---

# Why the Sink Matters

Consider these PHP functions:

```php
readfile($path);
```

versus:

```php
include($path);
```

The first primarily reads a file.

The second may cause the PHP interpreter to process the included resource.

Therefore:

```text
Same attacker-controlled path
```

can produce:

```text
Different vulnerability
Different impact
Different exploitation conditions
```

---

# PHP File Inclusion

PHP is particularly associated with classic LFI because functions such as:

```php
include()
require()
include_once()
require_once()
```

can load files dynamically.

Example unsafe pattern:

```php
$page = $_GET['page'];

include($page);
```

Another common pattern:

```php
$page = $_GET['page'];

include("pages/" . $page . ".php");
```

---

# PHP Include Functions

The relevant functions include:

```text
include
include_once
require
require_once
```

The differences in application behaviour when loading fails do not fundamentally remove the security issue.

User-controlled paths should not reach these functions without strict controls.

---

# PHP Wrappers

PHP provides stream wrappers that change how resources are accessed.

Examples include:

```text
file://
php://
data://
http://
https://
zip://
phar://
```

Wrapper availability and behaviour depend on:

```text
PHP version
Configuration
Installed extensions
Application logic
Function used
```

Do not assume every wrapper is available.

---

# php://filter

One particularly useful wrapper during authorised source disclosure testing is:

```text
php://filter
```

It can transform a resource before the application receives it.

A common use is reading PHP source without causing the referenced PHP file to execute.

Conceptually:

```text
php://filter
      ↓
Transformation
      ↓
PHP Source File
      ↓
Encoded Output
```

---

# php://filter Base64 Source Disclosure

A commonly used form is:

```text
php://filter/convert.base64-encode/resource=index.php
```

For example:

```http
GET /index.php?page=php://filter/convert.base64-encode/resource=index.php HTTP/1.1
Host: target.example
```

If the vulnerable include mechanism returns the transformed content, the response may contain Base64.

Decode locally:

```bash
echo 'BASE64_DATA' | base64 -d
```

This can expose application source code.

Use this technique only against files required to demonstrate impact.

---

# Why php://filter Is Useful

Directly including:

```text
index.php
```

may execute the PHP file.

Using:

```text
php://filter/convert.base64-encode/resource=index.php
```

can cause PHP to transform the source before inclusion.

Conceptually:

```text
index.php
   ↓
Base64 Filter
   ↓
Encoded PHP Source
   ↓
Application Response
```

This can make source code review possible through an LFI vulnerability.

---

# Source Disclosure Workflow

A controlled workflow is:

```text
Confirm LFI
    ↓
Identify PHP
    ↓
Identify Known Application File
    ↓
php://filter
    ↓
Retrieve Encoded Source
    ↓
Decode Locally
    ↓
Review Minimal Required Source
```

Interesting source files may include:

```text
index.php
Router files
Controller files
Configuration loaders
```

Avoid downloading an entire application unnecessarily.

---

# Reviewing Disclosed Source

Source disclosure can reveal additional security-relevant information.

Look for:

```text
Routes
Authentication logic
Authorisation logic
File handling
Database queries
Input validation
API endpoints
Template loading
Configuration paths
```

Be careful with secrets.

If sensitive credentials appear during authorised testing:

```text
Stop unnecessary collection
Protect evidence
Do not reuse credentials unless explicitly in scope
Document exposure appropriately
```

---

# PHP data Wrapper

PHP may support:

```text
data://
```

depending on runtime configuration.

This wrapper can represent inline data as a stream.

Whether it can affect an include sink depends on configuration and should not be assumed.

From a defensive perspective, arbitrary wrapper schemes should not be accepted as user-controlled include paths.

---

# Remote URLs

PHP configurations historically allowed URL-aware file operations.

Relevant configuration includes:

```text
allow_url_fopen
allow_url_include
```

Classic RFI depends on several conditions, including whether remote URL inclusion is enabled.

Do not assume:

```text
LFI = RFI
```

They should be tested and reported separately.

---

# RFI Testing

If application behaviour suggests remote resources may be accepted, use a harmless controlled resource.

Conceptually:

```text
https://controlled.example/test.txt
```

The objective is initially to establish:

```text
Does the server retrieve or include the remote resource?
```

rather than executing code.

A safe test resource might contain:

```text
AM-RFI-TEST-987654
```

If that marker appears in the application's output, remote inclusion behaviour may exist.

---

# RFI Mental Model

```text
User Input
    ↓
Include Function
    ↓
Remote URL
    ↓
Server Retrieves Resource
    ↓
Resource Included
```

Potential impact depends on whether the remote content is:

```text
Returned
Parsed
Interpreted
Executed
```

Do not assume code execution without evidence.

---

# LFI and Application Logs

Application and web server logs can contain attacker-controlled data.

Potential sources include:

```text
Request paths
User-Agent
Referer
Error messages
Application parameters
```

Conceptually:

```text
HTTP Request
     ↓
Log File
     ↓
LFI
     ↓
Application Includes Log
```

Historically, this combination has sometimes been used to turn LFI into code execution when attacker-controlled content is stored in a file that an interpreter subsequently includes.

---

# Log Inclusion Risk

The conceptual chain is:

```text
Attacker-Controlled Log Entry
        ↓
Log File
        ↓
Local File Inclusion
        ↓
Interpreter Processes File
```

Whether this results in execution depends on:

```text
Log location
Log permissions
Log format
Include function
Interpreter
Input sanitisation
Runtime configuration
```

During a normal assessment, demonstrating arbitrary local file inclusion may already be sufficient.

Do not attempt code execution unless explicitly necessary and authorised.

---

# Common Log Locations

Exact log locations vary by platform and configuration.

Linux environments may use directories such as:

```text
/var/log/
```

Web server logs may exist beneath server-specific directories.

Do not blindly enumerate large numbers of log paths.

Use:

```text
Technology Identification
Error Messages
Configuration
Source Code
```

to identify likely paths.

---

# Session Files

Some frameworks store session state in filesystem files.

Conceptually:

```text
User-Controlled Session Data
       ↓
Session File
       ↓
LFI
       ↓
File Included
```

This can become relevant when:

```text
Session storage is file based
Session path is known
Attacker controls stored session data
Application includes arbitrary local files
```

Again, this is highly technology and configuration dependent.

---

# PHP Session Files

PHP can use filesystem-backed sessions.

Configuration may define a session storage path.

Conceptually:

```text
PHPSESSID
    ↓
Session File
    ↓
Stored Session Data
```

If an LFI can include that file, attacker-controlled session content may become security relevant.

The presence of PHP sessions alone does not prove exploitability.

---

# Temporary Files

Applications frequently create temporary files.

Potential sources include:

```text
Uploads
Import jobs
Generated documents
Temporary archives
Cache files
Session files
```

A file inclusion vulnerability may interact with these resources.

The important questions are:

```text
Can the attacker influence the contents?

Can the path be determined?

Can the file be included?
```

---

# File Upload + LFI

File upload functionality can sometimes interact with LFI.

Conceptually:

```text
Upload File
    ↓
Server Stores File
    ↓
Determine Stored Path
    ↓
LFI References File
```

This combination may significantly increase impact depending on how the included file is interpreted.

Do not assume an uploaded file is executable merely because it can be included.

---

# File Name Testing

User-controlled file names can reveal filesystem behaviour.

A workflow might be:

```text
Upload Harmless File
       ↓
Observe Response
       ↓
Determine Stored Name
       ↓
Locate Retrieval Endpoint
       ↓
Understand Filesystem Mapping
```

This information can assist LFI analysis without attempting dangerous behaviour.

---

# /proc Files on Linux

Linux exposes process information through:

```text
/proc/
```

Some files may reveal runtime information.

Examples include:

```text
/proc/self/status
/proc/self/cmdline
/proc/self/environ
```

These can contain sensitive information.

Use them only when necessary and authorised.

A basic file such as:

```text
/etc/hostname
```

is usually preferable for initial proof.

---

# Environment Variables

Application environment variables can contain:

```text
Database credentials
API keys
Cloud configuration
Application secrets
Runtime settings
```

Therefore, files exposing process environments should be treated as sensitive.

Do not retrieve environment information simply because an LFI exists.

---

# Configuration Files

Potentially sensitive application configuration may contain:

```text
Database credentials
API credentials
Encryption keys
Application secrets
Internal endpoints
Service credentials
```

The exact configuration location depends on the application.

Source disclosure may reveal where configuration is loaded.

Again, minimal evidence is preferred.

---

# LFI in Template Engines

Modern applications may dynamically load templates.

Conceptually:

```text
template=invoice
       ↓
Template Loader
       ↓
templates/invoice.html
```

If attacker-controlled input can escape the template directory:

```text
Template Path Traversal
```

or:

```text
Local File Inclusion
```

may result.

The terminology depends on whether the resource is simply read or actually processed as a template.

---

# Java File Inclusion

Java applications may dynamically load resources using APIs such as:

```text
File
Path
Files
ClassPathResource
FileSystemResource
ResourceLoader
TemplateResolver
```

Potential flow:

```text
Request Parameter
      ↓
Resource Name
      ↓
Template / Resource Loader
```

Review whether the final resolved path is constrained to an approved location.

---

# .NET File Inclusion

Relevant .NET functionality may include:

```text
File
FileStream
Path.Combine
PhysicalFile
Razor views
Template loading
```

The vulnerability may manifest as:

```text
Path Traversal
File Disclosure
Dynamic View Selection
Template Inclusion
```

depending on the sink.

---

# Python File Inclusion

Python applications may use:

```text
open()
pathlib
Template loaders
render_template()
FileSystemLoader
```

For example, dynamic template names should not be accepted from untrusted users without restriction.

Framework-specific template loaders may implement their own path controls.

---

# Node.js File Inclusion

Relevant Node.js functionality includes:

```text
fs.readFile()
fs.createReadStream()
require()
Template engines
res.render()
res.sendFile()
```

Trace attacker-controlled input to the actual sink.

For example:

```javascript
res.render(req.query.template);
```

deserves careful review.

---

# Ruby File Inclusion

Relevant Ruby functionality may include:

```text
File.read
File.open
render
send_file
Template loaders
```

Again, distinguish:

```text
File Read
```

from:

```text
Template / Code Inclusion
```

---

# Burp Suite Workflow

Burp Suite provides a practical LFI testing workflow.

```text
Proxy
  ↓
HTTP History
  ↓
Identify Dynamic Resource
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Modify File Parameter
  ↓
Test Traversal
  ↓
Identify Include Behaviour
  ↓
Test Technology-Specific Behaviour
  ↓
Confirm Minimal Impact
```

---

# Burp Repeater

Repeater should be the primary manual testing tool.

A useful sequence is:

```text
1. Capture legitimate request

2. Send to Repeater

3. Record baseline

4. Supply invalid resource

5. Review error

6. Test traversal

7. Test harmless local file

8. Determine whether content is read or included

9. Test relevant technology-specific behaviour

10. Collect minimal evidence
```

---

# Burp Intruder

Intruder can help test a small set of controlled file paths.

For Linux:

```text
../etc/hostname
../../etc/hostname
../../../etc/hostname
../../../../etc/hostname
/etc/hostname
```

For Windows:

```text
..\Windows\win.ini
..\..\Windows\win.ini
..\..\..\Windows\win.ini
C:\Windows\win.ini
```

Analyse:

```text
Status
Length
Words
Lines
Content-Type
```

Investigate outliers manually.

---

# ffuf

`ffuf` can help with targeted testing once the vulnerable parameter has been identified.

Project:

```text
https://github.com/ffuf/ffuf
```

Example:

```bash
ffuf \
  -u 'https://target.example/index.php?page=FUZZ' \
  -w lfi.txt
```

Use response filtering based on the baseline.

For example:

```bash
ffuf \
  -u 'https://target.example/index.php?page=FUZZ' \
  -w lfi.txt \
  -fc 404
```

Keep payload lists focused.

---

# LFISuite

LFISuite is a specialised tool designed around LFI testing.

Project:

```text
https://github.com/D35m0nd142/LFISuite
```

As with other automated tools:

```text
Manual Discovery
      ↓
Understand Behaviour
      ↓
Targeted Automation
      ↓
Manual Verification
```

is preferable to starting with automation.

---

# liffy

Another historical LFI exploitation tool is:

```text
liffy
```

Project:

```text
https://github.com/mzfr/liffy
```

It includes functionality for testing several LFI-related techniques.

Treat specialised exploitation tools as supporting tools rather than replacements for understanding the vulnerable request.

---

# Nuclei

Nuclei can identify some file disclosure and LFI behaviours through targeted templates.

Project:

```text
https://github.com/projectdiscovery/nuclei
```

A useful methodology is:

```text
Recon
  ↓
Identify Interesting Endpoint
  ↓
Targeted Nuclei Check
  ↓
Review Match
  ↓
Manual Reproduction
```

Never report an LFI solely from automated output.

---

# curl

`curl` is useful for reproducing findings outside Burp.

Example:

```bash
curl -i \
  'https://target.example/index.php?page=../../../etc/hostname'
```

For authenticated functionality:

```bash
curl -i \
  -H 'Cookie: session=REDACTED' \
  'https://target.example/index.php?page=../../../etc/hostname'
```

Never store real authentication tokens in public notes or repositories.

---

# JavaScript Analysis

Search JavaScript for:

```text
page
template
view
layout
theme
lang
locale
file
path
module
include
```

For example:

```javascript
fetch("/api/render?template=" + templateName)
```

could reveal a hidden template endpoint.

Client-side JavaScript can also reveal:

```text
Internal API paths
Expected template names
File extensions
Download routes
Rendering functionality
```

---

# Parameter Discovery

Parameter discovery is particularly useful for finding hidden LFI candidates.

Interesting parameters include:

```text
page
template
view
include
file
path
lang
locale
module
```

Combine:

```text
Crawling
   +
JavaScript Analysis
   +
Historical URLs
   +
Parameter Discovery
```

before aggressive testing.

---

# Source Code Review

When source code is available, identify dynamic file-loading functions.

General flow:

```text
SOURCE
  ↓
Request Parameter
  ↓
Path Construction
  ↓
Include / Template Function
  ↓
FILE
```

The important distinction is whether the sink:

```text
Reads
Includes
Executes
Renders
Imports
```

the selected resource.

---

# PHP Source Review

Search for:

```text
include
include_once
require
require_once
readfile
file_get_contents
fopen
```

Example:

```bash
rg -n \
'include\s*\(|include_once\s*\(|require\s*\(|require_once\s*\(|readfile\s*\(|file_get_contents\s*\(|fopen\s*\('
```

Pay particular attention to:

```php
include($_GET['page']);
```

and:

```php
include("pages/" . $_GET['page']);
```

---

# Cross-Language Source Search

A broader search:

```bash
rg -n \
'include\s*\(|require\s*\(|readfile|file_get_contents|fopen|FileInputStream|Files\.read|Path\.Combine|File\.Read|fs\.readFile|fs\.createReadStream|res\.render|sendFile|render_template|FileSystemLoader|File\.read|send_file'
```

Then trace each potential sink back to user input.

---

# Source to Sink Analysis

A useful model:

```text
SOURCE
  ↓
req.query.page
  ↓
Controller
  ↓
Path Construction
  ↓
Include Function
  ↓
FILE
```

For example:

```text
$_GET['page']
     ↓
$page
     ↓
"pages/" . $page
     ↓
include()
```

Then ask:

```text
Can page contain separators?

Is traversal normalised?

Is an extension appended?

Are wrappers accepted?

Is the final path restricted?

Is an allowlist used?
```

---

# Secure Design

The safest design is usually to avoid user-controlled file paths entirely.

Instead of:

```text
?page=templates/home.php
```

use:

```text
?page=home
```

and map it internally:

```text
home     → /templates/home.php
profile  → /templates/profile.php
contact  → /templates/contact.php
```

Conceptually:

```text
User Identifier
      ↓
Strict Allowlist
      ↓
Internal Resource Mapping
      ↓
Include
```

---

# Allowlist Example

A conceptual secure pattern:

```php
$pages = [
    'home' => 'pages/home.php',
    'contact' => 'pages/contact.php',
    'about' => 'pages/about.php'
];

if (!isset($pages[$_GET['page']])) {
    exit('Invalid page');
}

include($pages[$_GET['page']]);
```

The user controls:

```text
home
```

rather than:

```text
pages/home.php
```

This greatly reduces filesystem exposure.

---

# Canonical Path Validation

If dynamic filesystem paths are genuinely required:

```text
Input
 ↓
Resolve
 ↓
Canonicalise
 ↓
Check Against Approved Base
 ↓
Access
```

The final canonical path must remain inside the approved directory.

Do not rely solely on:

```text
Removing ../
```

---

# Disable Unnecessary URL Inclusion

For PHP environments, unnecessary remote inclusion capabilities should be disabled.

Review:

```text
allow_url_include
```

and related runtime configuration according to application requirements.

Applications should not depend on user-controlled remote resources for includes.

---

# Least Privilege

The application account should only be able to access files it genuinely requires.

Restrict access to:

```text
Application secrets
SSH keys
System configuration
User files
Backup files
Cloud credentials
Private keys
```

Least privilege does not fix LFI but can reduce its impact.

---

# File Inclusion and Containers

Containerised applications can still be vulnerable to LFI.

The filesystem may expose:

```text
Application files
Container configuration
Mounted secrets
Environment-related files
Service account material
Mounted volumes
```

Do not assume:

```text
Container = harmless LFI
```

The impact depends on what the application process can access.

---

# File Inclusion and Cloud Environments

Cloud workloads may have access to:

```text
Mounted secrets
Configuration
Service account files
Application credentials
Runtime metadata
```

LFI should therefore be assessed in the context of the workload's privileges.

Avoid retrieving cloud credentials merely to demonstrate the issue.

---

# False Positives

Potential false positives include:

```text
Generic 404 pages
Framework routing
Client-side template selection
Static file routing
WAF responses
Cached content
Error pages containing the requested value
```

Do not conclude LFI simply because:

```text
../../../etc/hostname
```

appears somewhere in the response.

You need evidence that the server actually accessed or included the unintended resource.

---

# Validation

A strong LFI finding establishes:

```text
ATTACKER INPUT
      ↓
PATH MANIPULATION
      ↓
INCLUDE / TEMPLATE SINK
      ↓
UNINTENDED LOCAL FILE
      ↓
OBSERVABLE RESULT
      ↓
SECURITY IMPACT
```

For example:

```text
page
 ↓
../../../etc/hostname
 ↓
include()
 ↓
/etc/hostname
 ↓
Contents returned
```

---

# Minimal Evidence

Once LFI is confirmed, stop unnecessary file retrieval.

Prefer:

```text
/etc/hostname
/etc/os-release
C:\Windows\win.ini
```

where sufficient.

Avoid retrieving:

```text
Private keys
Password databases
Cloud credentials
Database passwords
API tokens
User documents
Environment secrets
```

unless specifically required, authorised and necessary to establish an otherwise uncertain impact.

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
Response
Included file
Operating system
Technology
Traversal depth
Encoding required
Wrapper used if relevant
Relevant screenshot
```

If source code is disclosed, include only the portion required to demonstrate impact.

---

# File Inclusion Reporting

A report should explain:

```text
Which endpoint is affected
Which parameter controls the included resource
How attacker input reaches the inclusion sink
Whether traversal is required
Which minimally sensitive file demonstrated the issue
Whether source disclosure is possible
Whether remote inclusion is possible
What application privileges determine the impact
How the issue should be remediated
```

---

# Example LFI Finding

```text
Title
Local File Inclusion in Dynamic Page Functionality

Affected Endpoint
GET /index.php

Affected Parameter
page

Authentication Required
No

Description
The application uses the user-controlled page parameter when
selecting a server-side file without sufficiently restricting
the final resolved resource.

Directory traversal sequences can escape the intended page
directory and cause an unintended local file to be included.

Validation
The vulnerability was demonstrated using a non-sensitive
operating system file.

Impact
An attacker may be able to access files readable by the
application process.

Depending on application configuration, this may expose source
code, configuration information or other sensitive resources.

Recommendation
Do not pass user-controlled filesystem paths directly to include
or template functions.

Map user-controlled identifiers to a strict allowlist of
server-side resources and ensure the final resolved path remains
inside the intended directory.
```

---

# Example RFI Finding

```text
Title
Remote File Inclusion in Dynamic Template Functionality

Affected Endpoint
GET /render

Affected Parameter
template

Description
The application accepts a user-controlled remote URL as the
resource used by the server-side inclusion mechanism.

Testing with a controlled external resource confirmed that the
application retrieved and processed remote content.

Impact
The exact impact depends on how the retrieved resource is
processed by the application runtime.

Recommendation
Do not permit user-controlled remote resources in server-side
include operations.

Use an explicit allowlist of local templates and disable
unnecessary remote resource inclusion functionality.
```

---

# Remediation

Recommended controls include:

```text
Avoid user-controlled file paths
Use indirect identifiers
Use strict allowlists
Canonicalise filesystem paths
Verify final paths remain inside approved directories
Disable unnecessary remote inclusion
Restrict URL wrappers where unnecessary
Apply least privilege
Do not expose verbose filesystem errors
Keep frameworks and runtimes updated
```

---

# File Inclusion Testing Checklist

## Discovery

- [ ] Dynamic pages
- [ ] Templates
- [ ] Views
- [ ] Themes
- [ ] Languages
- [ ] Localisation
- [ ] Modules
- [ ] Plugins
- [ ] Reports
- [ ] Help pages
- [ ] Email templates
- [ ] PDF templates
- [ ] XML / configuration imports
- [ ] File upload workflows

## Parameters

- [ ] page
- [ ] file
- [ ] filename
- [ ] path
- [ ] include
- [ ] template
- [ ] tpl
- [ ] view
- [ ] layout
- [ ] module
- [ ] theme
- [ ] lang
- [ ] language
- [ ] locale
- [ ] resource

## Baseline

- [ ] Capture legitimate request
- [ ] Record response
- [ ] Test invalid resource
- [ ] Review errors
- [ ] Identify appended extensions
- [ ] Identify required prefixes
- [ ] Identify operating system
- [ ] Identify technology

## Basic LFI

- [ ] Test relative paths
- [ ] Determine traversal depth
- [ ] Test absolute paths
- [ ] Use harmless local file
- [ ] Confirm server-side file access
- [ ] Confirm repeatability

## Encoding

- [ ] URL encoding
- [ ] Partial encoding
- [ ] Double encoding where justified
- [ ] Mixed path separators
- [ ] Determine decoding layers
- [ ] Determine normalisation behaviour

## PHP

- [ ] Identify PHP
- [ ] Determine include sink
- [ ] Check appended `.php`
- [ ] Test `php://filter` where relevant
- [ ] Test source disclosure
- [ ] Review wrapper behaviour
- [ ] Determine whether remote URLs are accepted
- [ ] Do not assume wrapper availability

## Advanced Impact

- [ ] Determine whether logs are includable
- [ ] Determine whether sessions are file based
- [ ] Review upload + include workflow
- [ ] Identify temporary files if relevant
- [ ] Stop before code execution if file disclosure is sufficient proof

## RFI

- [ ] Determine whether remote resources are accepted
- [ ] Use controlled harmless resource
- [ ] Use unique marker
- [ ] Determine whether content is retrieved
- [ ] Determine whether content is processed
- [ ] Do not assume execution

## Burp

- [ ] Proxy
- [ ] HTTP History
- [ ] Repeater
- [ ] Intruder where useful
- [ ] Compare response lengths
- [ ] Compare error messages

## Automation

- [ ] Understand behaviour manually first
- [ ] Use focused payload list
- [ ] ffuf where useful
- [ ] LFISuite where appropriate
- [ ] Nuclei where appropriate
- [ ] Manually validate results

## Source Review

- [ ] Search include functions
- [ ] Search template loaders
- [ ] Search filesystem functions
- [ ] Identify user-controlled sources
- [ ] Trace source to sink
- [ ] Review path validation
- [ ] Review allowlists
- [ ] Review wrapper handling

## Validation

- [ ] Confirm local file inclusion
- [ ] Distinguish from path traversal
- [ ] Distinguish from normal file download
- [ ] Confirm repeatability
- [ ] Use minimal evidence
- [ ] Avoid unnecessary sensitive files
- [ ] Record request and response
- [ ] Stop after sufficient proof

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | Request interception and LFI testing |
| Burp Repeater | Manual inclusion testing |
| Burp Intruder | Controlled file path testing |
| ffuf | Targeted LFI fuzzing |
| LFISuite | LFI-specific testing |
| liffy | LFI testing and research |
| Nuclei | Targeted automated detection |
| curl | Manual HTTP reproduction |
| grep / ripgrep | Inclusion sink discovery |
| Semgrep | Structured source analysis |

---

# Tool Selection

| Situation | Tool |
|---|---|
| Understand request | Burp Proxy |
| Manual LFI | Burp Repeater |
| Compare path variations | Burp Intruder |
| Targeted fuzzing | ffuf |
| LFI-specific automation | LFISuite |
| Automated detection | Nuclei |
| HTTP reproduction | curl |
| Source review | grep / ripgrep |
| Structured source analysis | Semgrep |

---

# Quick Reference

```text
High Value Functionality:

Dynamic pages
Templates
Views
Themes
Languages
Modules
Reports
Help pages
Uploads
Configuration imports

Interesting Parameters:

page
file
filename
path
include
template
view
layout
module
theme
lang
locale
resource

Linux Validation:

/etc/hostname
/etc/os-release

Windows Validation:

C:\Windows\win.ini

PHP Inclusion Sinks:

include()
include_once()
require()
require_once()

PHP Source Disclosure:

php://filter/convert.base64-encode/resource=index.php

Manual:

Burp Repeater

Automation:

Burp Intruder
ffuf
LFISuite
Nuclei

Always establish:

INPUT → PATH → INCLUSION SINK → RESOURCE → EVIDENCE → IMPACT
```

---

# Practical Workflow Summary

```text
                  ┌───────────────────────┐
                  │ Find Dynamic Resource │
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
                  │ Identify Technology   │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Test Path Handling    │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Inclusion Confirmed?  │
                  └───────────┬───────────┘
                              │
                              ▼
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
     ┌─────────────────┐             ┌─────────────────┐
     │ Local Resource  │             │ Remote Resource │
     │      LFI        │             │      RFI        │
     └────────┬────────┘             └────────┬────────┘
              │                               │
              ▼                               ▼
     ┌─────────────────┐             ┌─────────────────┐
     │ Minimal File    │             │ Controlled      │
     │ Validation      │             │ Marker          │
     └────────┬────────┘             └────────┬────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Determine Impact      │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Collect Evidence      │
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

PortSwigger's path traversal material is particularly relevant because traversal frequently provides the path manipulation required to reach unintended files through an inclusion sink.

---

## OWASP Web Security Testing Guide

### Testing Directory Traversal File Include

https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Input_Validation_Testing/01-Testing_Directory_Traversal_File_Include

OWASP provides methodology covering directory traversal and file inclusion testing.

---

## PayloadsAllTheThings

### File Inclusion

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion

Useful reference covering:

```text
LFI
PHP wrappers
Encoding
Log files
Session files
File upload interactions
RFI
```

Use payload collections after understanding the affected technology and inclusion behaviour.

---

## HackTricks

### File Inclusion

https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html

A useful practical reference covering LFI, PHP wrappers, file disclosure and related techniques.

---

## PHP Documentation

### Supported Protocols and Wrappers

https://www.php.net/manual/en/wrappers.php

Useful for understanding PHP stream wrapper behaviour.

---

## ffuf

https://github.com/ffuf/ffuf

Useful for focused parameter fuzzing after an interesting file inclusion location has been identified.

---

## LFISuite

https://github.com/D35m0nd142/LFISuite

Specialised LFI testing tool.

---

## liffy

https://github.com/mzfr/liffy

LFI exploitation and research tool.

---

## Nuclei

https://github.com/projectdiscovery/nuclei

Useful for targeted automated checks, with manual validation required.

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
└── File Inclusion
```

The strongest workflow connections are:

```text
Technology Identification
          ↓
Identify language and framework
          ↓
File Inclusion

Parameter Discovery
          ↓
Find page / template / file parameters
          ↓
File Inclusion

Path Traversal
          ↓
Escape intended directory
          ↓
File Inclusion

File Inclusion
          ↓
Potential source disclosure
          ↓
Source Code Review
```

---

# Final Testing Principle

Do not reduce LFI testing to:

```text
Try ../../../../etc/passwd
```

Instead think:

```text
What does this parameter control?
        ↓
How is the path constructed?
        ↓
What filesystem is involved?
        ↓
Is the resource read or included?
        ↓
What language / framework is involved?
        ↓
Are transformations or wrappers supported?
        ↓
Can I demonstrate the issue minimally?
        ↓
What is the actual security impact?
```

The most useful evidence is the complete chain:

```text
SOURCE
  ↓
PATH CONSTRUCTION
  ↓
INCLUSION SINK
  ↓
UNINTENDED RESOURCE
  ↓
OBSERVABLE RESULT
  ↓
IMPACT
```
