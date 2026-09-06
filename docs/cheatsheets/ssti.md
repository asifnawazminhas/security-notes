---
title: Server-Side Template Injection (SSTI) Cheatsheet
description: Practical SSTI cheatsheet for authorised web application testing covering discovery, template engine identification, safe arithmetic probes, Jinja2, Twig, Freemarker, Velocity, Thymeleaf, Smarty, source review, Burp Suite, evidence, remediation and retesting.
---

# Server-Side Template Injection (SSTI) Cheatsheet

Server-Side Template Injection occurs when attacker-controlled input is interpreted as template syntax by a server-side template engine instead of being treated purely as data.

A simplified vulnerable flow is:

```text
User Input
    |
    v
Application
    |
    v
Template Source
    |
    v
Template Engine
    |
    v
Rendered Output
```

The important distinction is:

```text
SAFE

Template:
Hello {{ name }}

Data:
name = "Asif"

Result:
Hello Asif
```

versus:

```text
DANGEROUS

Template:
"Hello " + USER_INPUT

        |
        v

Template Engine Compiles User Input
```

The security question is therefore not simply:

```text
Does {{ ... }} appear in the response?
```

It is:

```text
Can attacker-controlled input become part of the
template source interpreted by the server?
```

!!! warning "Authorised Security Testing"

    Perform SSTI testing only against systems explicitly included in the assessment scope. Start with harmless arithmetic expressions and unique markers. Do not use template injection to execute operating-system commands, access secrets, read sensitive files, establish shells or modify the target simply to prove the vulnerability.


# Quick Reference

## Common Candidate Features

```text
Email templates

Notification templates

PDF generation

Invoice generation

Report generation

CMS templates

Preview functionality

Custom messages

Error pages

Search result templates

User profile rendering

Theme systems

Administrative templates

Document generation

Server-rendered pages
```


## Common Input Locations

```text
Query parameters

POST parameters

JSON values

Form fields

Profile fields

Names

Email subjects

Email bodies

Template editors

Report titles

Document fields

CMS content

Headers
```


## Harmless Detection Principle

Prefer:

```text
Arithmetic
```

over:

```text
Command execution
```

Example concept:

```text
7 * 7
```

If evaluated by the template engine:

```text
49
```

may appear in the output.


# SSTI Testing Model

Do not use:

```text
{{7*7}}
   |
   v
49
   |
   v
RCE
```

Use:

```text
Input
  |
  v
Rendered Server-Side?
  |
  v
Template Syntax Interpreted?
  |
  v
Template Engine Identified?
  |
  v
Available Template Capabilities?
  |
  v
Security Boundary Crossed?
```


# SSTI vs Client-Side Template Injection

Server-side:

```text
Browser
   |
   v
Request
   |
   v
Server Template Engine
   |
   v
Rendered HTML
   |
   v
Browser
```

Client-side:

```text
Browser
   |
   v
JavaScript Template Framework
   |
   v
DOM
```

SSTI specifically concerns:

```text
Server-side template evaluation.
```


# SSTI vs XSS

SSTI:

```text
Input
  |
  v
Server Template Engine
```

XSS:

```text
Input
  |
  v
Browser JavaScript / HTML Context
```


# SSTI vs Expression Language Injection

Some frameworks expose:

```text
Expression languages

Template expressions

Binding expressions
```

These may overlap with SSTI but can have different execution models.

Report the actual mechanism where possible.


# SSTI vs Simple Reflection

Input:

```text
{{7*7}}
```

Response:

```text
Hello {{7*7}}
```

means:

```text
Reflection
```

not:

```text
Template evaluation
```


# SSTI vs HTML Encoding

Input:

```text
{{7*7}}
```

Response:

```html
{{7*7}}
```

or encoded equivalents does not establish SSTI unless the server template engine evaluated the expression.


# Establish a Baseline

Suppose the application contains:

```text
Preview message
```

Request:

```http
POST /preview HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

message=Hello
```


# Baseline Response

```html
<div class="preview">
Hello
</div>
```


# Record

Capture:

```text
Endpoint

Method

Parameter

Authentication context

Input

Response

Response length

Response time
```


# Marker First

Start with a unique marker:

```text
SSTI_TEST_7f3a9
```


# Request

```http
POST /preview HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

message=SSTI_TEST_7f3a9
```


# Determine Reflection

If the response contains:

```text
SSTI_TEST_7f3a9
```

determine where the value appears.


# Reflection Context

Possible contexts:

```text
HTML text

HTML attribute

JavaScript

JSON

Email

PDF

Server-generated document
```


# Arithmetic Probe

After establishing reflection, use a harmless expression appropriate to a candidate template engine.


# Common Generic Probe

```text
{{7*7}}
```


# Possible Result

```text
49
```


# Interpretation

If:

```text
Input:
{{7*7}}

Output:
49
```

this strongly suggests server-side expression evaluation.

It does not automatically prove:

```text
Operating-system command execution

File read

Secret access

Remote code execution
```


# Repeat With Different Values

First:

```text
{{7*7}}
```

Expected if evaluated:

```text
49
```

Second:

```text
{{8*8}}
```

Expected:

```text
64
```


# Why Repeat?

This helps distinguish template evaluation from:

```text
Hard-coded content

Coincidental output

Caching

Application-specific transformations
```


# Template Engine Identification

Once expression evaluation is established, determine the engine.

Potential engines include:

```text
Jinja2

Twig

Smarty

FreeMarker

Velocity

Thymeleaf

Pebble

Handlebars

Mustache

Nunjucks

Liquid

ERB

Pug
```


# Identification Sources

Use:

```text
Application technology

Source code

Dependency files

Error messages

Template file extensions

Framework conventions

Harmless syntax differences
```


# Do Not Fingerprint Aggressively

If source code or dependency information already identifies the engine, do not send unnecessary payloads.


# Common Template Syntax Families

## Double Curly Braces

Often associated with engines such as:

```text
Jinja2

Twig

Nunjucks

Handlebars

Mustache

Liquid
```


## Dollar Expressions

Some Java template technologies use forms resembling:

```text
${...}
```


## Hash Expressions

Some Java expression contexts may use:

```text
#{...}
```


## ERB

Ruby ERB commonly uses:

```text
<%= ... %>
```


# Important

Syntax overlap is common.

For example:

```text
{{ ... }}
```

does not uniquely identify Jinja2.


# Error-Based Fingerprinting

Malformed template syntax may trigger errors revealing:

```text
Template engine

Framework

Template filename

Filesystem path

Stack trace

Parser details
```


# Example

A response might mention:

```text
jinja2.exceptions.TemplateSyntaxError
```

This provides stronger engine identification than syntax guessing.


# Do Not Intentionally Generate Large Error Volumes

One or two controlled malformed expressions are normally sufficient.


# Jinja2

Jinja2 is widely used with Python applications.


# Common Stack

```text
Python
  |
  v
Flask
  |
  v
Jinja2
```


# Safe Arithmetic Probe

```text
{{7*7}}
```


# Expected

```text
49
```


# String Operation Probe

A harmless engine-characterisation test can use basic template-supported operations.

Keep testing limited to non-sensitive values.


# Jinja2 Source Review

Search:

```bash
rg -ni 'jinja2|render_template|render_template_string|Environment|Template\(' -g '*.py' .
```


# Flask Safe Pattern

Conceptually:

```python
return render_template(
    "hello.html",
    name=user_input
)
```

Template:

```html
Hello {{ name }}
```


# Data Flow

```text
User Input
    |
    v
Template Variable
    |
    v
Existing Template
```

This is the normal design.


# Flask High-Risk Pattern

```python
from flask import request
from flask import render_template_string

name = request.args.get("name")

return render_template_string(
    "Hello " + name
)
```


# Source-to-Sink

```text
request.args["name"]
        |
        v
String Concatenation
        |
        v
render_template_string()
        |
        v
Jinja2 Compiler
```


# Core Problem

The application has changed:

```text
User Data
```

into:

```text
Template Source
```


# Jinja2 Search With Context

```bash
rg -n -C 8 'render_template_string|Template\(' -g '*.py' .
```


# Search String Construction

```bash
rg -n -C 8 'render_template_string.*\+|Template\(.*\+' -g '*.py' .
```


# Twig

Twig is commonly used in PHP applications.


# Safe Arithmetic Probe

```text
{{7*7}}
```


# Expected

```text
49
```


# Twig Source Search

```bash
rg -ni 'Twig|createTemplate|render\(' -g '*.php' .
```


# Safe Twig Pattern

Conceptually:

```php
$twig->render(
    'profile.html.twig',
    ['name' => $name]
);
```


# Higher-Risk Pattern

Conceptually:

```php
$twig->createTemplate(
    'Hello ' . $name
);
```


# Review Question

Ask:

```text
Is attacker-controlled content passed as template source
or merely as template data?
```


# Smarty

Smarty is another PHP template engine.


# Search

```bash
rg -ni 'Smarty|fetch\(|display\(|assign\(' -g '*.php' .
```


# Review

Determine whether attacker-controlled data is:

```text
Assigned as variable
```

or:

```text
Compiled as template content
```


# FreeMarker

FreeMarker is common in Java applications.


# Typical Syntax Family

```text
${...}
```


# Harmless Arithmetic Concept

```text
${7*7}
```


# Expected

```text
49
```

if evaluated in an applicable FreeMarker expression context.


# Source Search

```bash
rg -ni 'freemarker|Configuration|Template|process\(' -g '*.java' .
```


# Dependency Search

```bash
rg -ni 'freemarker' pom.xml build.gradle build.gradle.kts
```


# Velocity

Apache Velocity is another Java template engine.


# Search

```bash
rg -ni 'VelocityEngine|VelocityContext|evaluate\(|mergeTemplate' -g '*.java' .
```


# High-Priority Sink

Pay particular attention to APIs that:

```text
Evaluate a string as a template.
```


# Thymeleaf

Thymeleaf is commonly used with Spring applications.


# Search

```bash
rg -ni 'thymeleaf|TemplateEngine|process\(' -g '*.java' .
```


# Dependency Search

```bash
rg -ni 'thymeleaf' pom.xml build.gradle build.gradle.kts
```


# Thymeleaf Context

Not every:

```text
${...}
```

observation proves SSTI.

Thymeleaf uses multiple expression types and processing contexts.

Prefer source analysis and controlled evaluation evidence.


# Pebble

Search:

```bash
rg -ni 'PebbleEngine|PebbleTemplate|pebble' -g '*.java' .
```


# Nunjucks

Nunjucks is a JavaScript template engine inspired by Jinja.


# Search

```bash
rg -ni 'nunjucks|renderString|configure\(' -g '*.js' -g '*.ts' .
```


# High-Risk Pattern

```text
renderString(USER_CONTROLLED_TEMPLATE)
```


# Handlebars

Handlebars typically treats template source separately from data.

Search:

```bash
rg -ni 'handlebars|compile\(' -g '*.js' -g '*.ts' .
```


# Review Pattern

```text
User Input
    |
    v
Handlebars.compile()
```

is more interesting than:

```text
User Input
    |
    v
Template Variable
```


# Mustache

Search:

```bash
rg -ni 'mustache|Mustache\.render|render\(' -g '*.js' -g '*.ts' .
```


# Pug

Search:

```bash
rg -ni 'pug|compile\(|render\(|renderFile' -g '*.js' -g '*.ts' .
```


# Liquid

Liquid implementations exist across multiple languages.

Search:

```bash
rg -ni 'liquid|Liquid::Template|parse\(' .
```


# ERB

Ruby ERB uses Ruby expressions inside templates.


# Typical Expression

```text
<%= ... %>
```


# Safe Arithmetic Probe

```text
<%= 7*7 %>
```


# Expected

```text
49
```

if the input is being evaluated as ERB template source.


# Ruby Search

```bash
rg -ni 'ERB|erb\.new|ERB\.new|render.*inline' -g '*.rb' .
```


# Rails Inline Rendering

Review:

```text
render inline:
```

especially when the inline template includes user-controlled content.


# Template File Extensions

Useful repository indicators include:

```text
.jinja

.jinja2

.html.j2

.twig

.ftl

.vm

.mustache

.hbs

.handlebars

.liquid

.erb

.pug
```


# Find Template Files

```bash
find . -type f \( \
  -name '*.jinja' -o \
  -name '*.jinja2' -o \
  -name '*.j2' -o \
  -name '*.twig' -o \
  -name '*.ftl' -o \
  -name '*.vm' -o \
  -name '*.hbs' -o \
  -name '*.handlebars' -o \
  -name '*.liquid' -o \
  -name '*.erb' -o \
  -name '*.pug' \
\)
```


# Dependency Review

Template engine dependencies can identify likely syntax without sending probes.


# Python

```bash
rg -ni 'jinja|mako' requirements*.txt pyproject.toml poetry.lock Pipfile*
```


# Node.js

```bash
rg -ni 'nunjucks|handlebars|mustache|pug|ejs|liquid' package.json package-lock.json yarn.lock pnpm-lock.yaml
```


# Java

```bash
rg -ni 'freemarker|velocity|thymeleaf|pebble' pom.xml build.gradle build.gradle.kts
```


# PHP

```bash
rg -ni 'twig|smarty|blade' composer.json composer.lock
```


# Ruby

```bash
rg -ni 'erb|liquid|haml|slim' Gemfile Gemfile.lock
```


# Template Source vs Template Data

This is the most important source-review distinction.


# Usually Safe Structure

```text
STATIC TEMPLATE
      +
UNTRUSTED DATA
```

Example:

```text
Template:
Hello {{ username }}

Context:
username = user_input
```


# Dangerous Structure

```text
STATIC TEMPLATE
      +
UNTRUSTED DATA
      |
      v
NEW TEMPLATE SOURCE
      |
      v
COMPILE / RENDER
```


# Source-to-Sink Analysis

```text
HTTP Parameter
      |
      v
Variable
      |
      v
String Concatenation
      |
      v
Template Compiler
      |
      v
Rendered Response
```


# Search Template Construction

Generic:

```bash
rg -ni 'render.*string|template.*string|compile\(|evaluate\(|createTemplate|render.*inline' src/
```


# Search User Input Nearby

```bash
rg -n -C 10 'render_template_string|createTemplate|renderString|render.*inline|evaluate\(' src/
```


# Source Review Questions

For every template rendering path ask:

```text
Which template engine is used?

Is the template static?

Can the user select a template?

Can the user modify the template?

Is user input inserted into template source?

Is user input passed only as context data?

Is the template compiled dynamically?

Are sandbox controls enabled?

What objects exist in the template context?

Are helper functions exposed?

Can templates access application objects?

Can templates access filesystem-related objects?

Can templates invoke methods?

Can templates perform network operations?

Are templates administrator-only?

Are tenant-created templates supported?
```


# Dynamic Templates Are Not Automatically Vulnerable

Some applications intentionally allow users to create templates.

Examples:

```text
Email automation platform

CMS

Document generator

Notification system
```

The security requirement may then be:

```text
Safe sandboxed template language
```

rather than:

```text
No template syntax allowed
```


# Template Sandbox

A sandbox may restrict:

```text
Object access

Method calls

Attribute access

Imports

Filesystem access

Process execution
```


# Sandbox Presence Does Not End Testing

Review:

```text
Which objects are exposed?

Which methods are callable?

Are dangerous helpers available?

Can the sandbox be escaped?

Is the sandbox version supported?
```

Do not attempt sandbox escapes beyond the authorised assessment scope.


# Template Context Exposure

Even without OS command execution, SSTI may expose sensitive data.

Possible context objects include:

```text
Current user

Application configuration

Environment values

Request object

Session

Feature flags

Internal objects
```


# Do Not Read Secrets Just to Prove SSTI

A harmless arithmetic expression is normally sufficient to establish server-side template evaluation.

If impact requires additional demonstration, use the minimum non-sensitive context approved by the engagement.


# Template Injection in Emails

A common architecture:

```text
User-Controlled Message
       |
       v
Email Template
       |
       v
Template Engine
       |
       v
Recipient
```


# Test Both Preview and Delivery

The preview engine and actual email-delivery engine may differ.


# Example

```text
Preview:
No evaluation

Delivered email:
Expression evaluated
```

or the reverse.


# Template Injection in PDF Generation

Pipeline:

```text
User Input
   |
   v
Template
   |
   v
HTML
   |
   v
PDF Renderer
```


# Distinguish Layers

Potential issues include:

```text
SSTI

HTML Injection

XSS

SSRF

PDF renderer behaviour
```

Do not collapse them into one finding.


# Template Injection in Reports

Candidate fields:

```text
Report title

Header

Footer

Customer name

Description

Custom fields
```


# Template Injection in CMS Features

Check whether:

```text
Page content

Widget content

Theme settings

Custom layouts
```

are interpreted as template source.


# Template Injection in Error Messages

A risky pattern is dynamically constructing templates from:

```text
Error text

Exception details

User-controlled resource names
```


# Template Injection Through Stored Data

SSTI may be second-order.

Example:

```text
User Updates Profile
        |
        v
Value Stored
        |
        v
Admin Generates Report
        |
        v
Stored Value Added to Template Source
        |
        v
Evaluation
```


# Second-Order SSTI

The initial request may show no immediate effect.

Review downstream consumers such as:

```text
Admin dashboards

Emails

Reports

Invoices

PDFs

Exports

Background jobs
```


# Stored vs Reflected SSTI

Reflected:

```text
Input
  |
  v
Immediate Template Evaluation
```

Stored:

```text
Input
  |
  v
Database
  |
  v
Later Rendering
  |
  v
Template Evaluation
```


# Blind SSTI

Some template evaluation occurs in a context where output is not directly returned.

Examples:

```text
Email generation

Background report generation

Log processing

Notification generation
```


# Blind SSTI Testing

Prefer application-visible harmless effects where possible.

Do not jump immediately to external callbacks.


# Error-Based Detection

A template parser error can support detection.

Example concept:

```text
Input:
{{

Response:
Template syntax error
```


# Interpretation

This suggests the input may reach a template parser.

It is weaker than successful controlled expression evaluation.


# Error Evidence

Capture:

```text
Input

Error type

Template engine name

Template path

Line number

Stack trace
```


# Do Not Publish Sensitive Paths Unnecessarily

Redact unrelated:

```text
Usernames

Secrets

Internal identifiers
```

from screenshots and reports.


# Arithmetic Probe Strategy

Use multiple expressions.

Example:

```text
{{7*7}}

{{8*8}}
```


# Expected

```text
49

64
```


# Why Arithmetic Is Good

Arithmetic is:

```text
Deterministic

Low impact

Easy to correlate

Non-destructive

Usually sufficient for detection
```


# Avoid Dangerous Detection Payloads

Do not begin with:

```text
OS command execution

File reads

Environment dumps

Secret extraction

Reverse shells
```


# Syntax Collision

Some applications legitimately transform:

```text
{{7*7}}
```

through another component.

Therefore verify:

```text
Server-side evaluation

Correct template engine

Repeatability
```


# Mathematical Coincidence

If the page already contains:

```text
49
```

use a unique arithmetic result.

For example:

```text
{{137*41}}
```

Expected:

```text
5617
```


# Use Distinct Values

Avoid common values such as:

```text
1

2

42
```

when they may naturally appear in the page.


# Context Around Expression

Example:

```text
SSTI_A{{137*41}}SSTI_B
```


# Expected if Evaluated

```text
SSTI_A5617SSTI_B
```


# Why Wrappers Help

The surrounding markers make it easier to distinguish:

```text
Evaluation

Reflection

Unrelated page content
```


# JSON Input

Example:

```http
POST /api/preview HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "message": "SSTI_A{{137*41}}SSTI_B"
}
```


# URL Parameter

```http
GET /hello?name=SSTI_A%7B%7B137*41%7D%7DSSTI_B HTTP/1.1
Host: target.example
```


# Form Parameter

```http
POST /hello HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

name=SSTI_A%7B%7B137*41%7D%7DSSTI_B
```


# Headers

Some applications render request metadata into templates.

Candidate headers can include:

```text
User-Agent

Referer

Host-related values

Custom application headers
```

Only test headers that are actually used by the rendering workflow.


# Cookies

Stored cookie values may be inserted into server-rendered pages.

Again, reflection alone does not prove SSTI.


# Burp Suite Workflow

```text
Proxy
  |
  v
Find Reflected / Stored Input
  |
  v
Send to Repeater
  |
  v
Baseline Marker
  |
  v
Arithmetic Probe
  |
  v
Compare Response
  |
  v
Repeat
  |
  v
Identify Engine
  |
  v
Capture Evidence
```


# Burp Repeater Baseline

```http
POST /preview HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

message=SSTI_TEST_7f3a9
```


# Candidate

```http
POST /preview HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

message=SSTI_A%7B%7B137*41%7D%7DSSTI_B
```


# Representative Positive Response

```html
<div class="preview">
SSTI_A5617SSTI_B
</div>
```


# Interpretation

This supports:

```text
Server-side evaluation of attacker-controlled template syntax.
```


# Burp Comparer

Compare:

```text
Baseline response

Arithmetic response

Malformed-expression response
```


# Burp Decoder

Useful for:

```text
URL encoding

HTML encoding

Base64 values
```

when tracing input transformations.


# Burp Intruder

Intruder can test a small engine-fingerprinting set.

Prefer a carefully selected set of harmless expressions rather than a large exploitation payload list.


# Burp Scanner

Automated SSTI findings should be manually validated.

Confirm:

```text
Actual evaluation

Template engine

Input location

Repeatability
```


# curl Baseline

```bash
curl -i \
  -X POST \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'message=SSTI_TEST_7f3a9' \
  'https://target.example/preview'
```


# curl Arithmetic Probe

```bash
curl -i \
  -X POST \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'message=SSTI_A{{137*41}}SSTI_B' \
  'https://target.example/preview'
```


# JSON Request

```bash
curl -i \
  -H 'Content-Type: application/json' \
  --data '{"message":"SSTI_A{{137*41}}SSTI_B"}' \
  'https://target.example/api/preview'
```


# Local Shell Quoting

Use single quotes around JSON or form values where appropriate so your local shell does not unexpectedly transform special characters.


# Template Encoding

The application may:

```text
URL decode

HTML decode

JSON decode

Normalise

Sanitise
```

before template processing.


# Determine the Evaluation Stage

Conceptually:

```text
HTTP Input
   |
   v
Decoder
   |
   v
Validation
   |
   v
Template Engine
   |
   v
Output Encoding
```


# Output Encoding Does Not Fix SSTI

HTML encoding occurs after template evaluation in many rendering pipelines.

Therefore:

```text
HTML escaping
```

and:

```text
Template source safety
```

are separate controls.


# Example

Even if output becomes:

```text
&lt;value&gt;
```

the expression may already have been evaluated server-side.


# WAF Behaviour

A WAF may block:

```text
{{

${

<%=
```

but this does not fix unsafe dynamic template construction.


# Do Not Report WAF Bypass as Root Cause

The root cause remains:

```text
Untrusted input compiled as template source.
```


# Authentication Context

Record whether the vulnerable template functionality is:

```text
Unauthenticated

Normal user

Privileged user

Administrator only
```


# Privileged Template Editors

An administrator-only template editor may intentionally support template expressions.

The assessment then becomes:

```text
Is the template language appropriately sandboxed
for the trust model?
```


# Multi-Tenant Applications

In SaaS applications, ask:

```text
Can Tenant A create templates?

Can templates access Tenant B data?

Are template contexts tenant-scoped?

Are helpers tenant-safe?
```


# Tenant Isolation

A template engine may be functioning as designed but expose objects outside the current tenant.

This can become:

```text
Cross-tenant data exposure
```

rather than generic SSTI alone.


# Template Preview Features

Preview endpoints deserve special attention because they often accept:

```text
Raw template text
```

by design.


# Preview Security Questions

Ask:

```text
Who can use preview?

What template language is available?

Is it sandboxed?

What objects are exposed?

Does preview differ from production rendering?

Can preview access real production data?
```


# Template Engines in CMS Platforms

CMS applications may intentionally expose template functionality to:

```text
Administrators

Theme developers

Content editors
```

The expected security boundary depends on role.


# Do Not Call Intended Admin Code Execution SSTI Automatically

If administrators are explicitly trusted to deploy arbitrary application code, template execution may be part of the intended trust model.

Assess:

```text
Role boundaries

Tenant boundaries

Documented capabilities
```


# Error Handling

Secure applications should avoid exposing unnecessary:

```text
Template paths

Framework versions

Stack traces

Internal objects
```


# Template Cache

Some engines compile and cache templates.

This can affect testing:

```text
Input changed

Old output remains

Cache invalidation delayed
```


# Repeat Carefully

If results appear inconsistent, consider:

```text
Template cache

Application cache

CDN cache

Background processing

Load-balanced instances
```


# False Positive - Reflection

Input:

```text
{{137*41}}
```

Output:

```text
{{137*41}}
```

Conclusion:

```text
No evaluation demonstrated.
```


# False Positive - JavaScript Evaluation

If a browser-side framework evaluates the expression after page load, the issue is not necessarily SSTI.


# Validation

Compare:

```text
Raw HTTP response
```

with:

```text
Rendered browser DOM
```


# If Raw Response Contains Expression

but the browser later transforms it:

```text
Client-side evaluation may be involved.
```


# If Raw Response Contains Result

the server likely evaluated it before delivery.


# False Positive - Static Value

Input:

```text
{{7*7}}
```

Page already contains:

```text
49
```

Use:

```text
SSTI_A{{137*41}}SSTI_B
```


# False Positive - Error Page

A 500 response after template-like input does not prove SSTI.

Determine whether:

```text
Template parser generated the error
```

or another validation component failed.


# False Positive - WAF Block

A WAF rejecting:

```text
{{7*7}}
```

does not prove the application is vulnerable behind the WAF.


# False Positive - Template Syntax Stored

A CMS storing:

```text
{{7*7}}
```

without evaluation is not SSTI.


# False Positive - Intended Template Language

If users are explicitly permitted to author restricted templates, successful arithmetic evaluation may be intended.

The security question becomes:

```text
Can the user exceed the intended sandbox or data boundary?
```


# Impact Assessment

Potential SSTI consequences vary substantially.

Possible impacts include:

```text
Template logic manipulation

Information disclosure

Application object access

Cross-tenant data exposure

Server-side request behaviour

File access

Arbitrary code execution
```

Do not claim the highest theoretical impact without evidence.


# Minimum Proof

For a conventional application where users should not control templates:

```text
Unique arithmetic evaluation
```

is usually sufficient to prove SSTI.


# Additional Impact Testing

Only extend testing if necessary to establish:

```text
Severity

Trust boundary

Data exposure

Sandbox effectiveness
```

Use the least invasive method possible.


# Do Not Dump Environment Variables

Avoid:

```text
Environment enumeration

Credential extraction

Secret dumping
```

when arithmetic evaluation already proves the issue.


# Do Not Read Sensitive Files

Do not retrieve:

```text
/etc/passwd

application secrets

cloud credentials

private keys
```

simply to demonstrate SSTI.


# Do Not Execute OS Commands by Default

SSTI can sometimes lead to code execution depending on:

```text
Template engine

Configuration

Available objects

Sandbox

Language runtime
```

But command execution is not required to validate SSTI.


# Evidence Collection

Capture:

```text
Finding ID

Endpoint

Method

Parameter

Authentication context

Baseline marker

Template expression

Expected arithmetic result

Actual result

Raw HTTP response

Template engine evidence

Error message if relevant

Timestamp
```


# Strong Evidence Pattern

```text
Input:
SSTI_A{{137*41}}SSTI_B

Expected:
SSTI_A5617SSTI_B

Actual:
SSTI_A5617SSTI_B
```


# Repeat

Second input:

```text
SSTI_C{{149*43}}SSTI_D
```

Expected:

```text
SSTI_C6407SSTI_D
```


# Why Two Expressions?

Two distinct controlled results provide strong evidence of deterministic template evaluation.


# Evidence Chain

```text
Attacker-Controlled Input
        |
        v
Template Expression
        |
        v
Server-Side Evaluation
        |
        v
Deterministic Result
```


# Reporting Example - SSTI

> The `message` parameter in the preview functionality is incorporated into server-side template source before rendering. A controlled arithmetic expression supplied through this parameter was evaluated by the server, with `SSTI_A{{137*41}}SSTI_B` being returned as `SSTI_A5617SSTI_B`. A second arithmetic expression produced the corresponding expected result, confirming server-side template injection.


# Reporting Example - Stored SSTI

> User-controlled profile data is stored without immediate template evaluation but is later incorporated into the template source used by the administrative report generator. A harmless arithmetic expression stored in the profile was evaluated when the report was generated, demonstrating second-order server-side template injection.


# Reporting Example - Template Sandbox Issue

> The application intentionally allows authenticated users to create templates. The template language is therefore expected functionality; however, the available template context exposes objects outside the intended user boundary. The finding concerns insufficient template sandboxing and object exposure rather than the mere ability to evaluate template expressions.


# Reporting Example - Source Review

> User-controlled input from the `name` request parameter is concatenated into a string passed to `render_template_string()`. This causes the resulting string, including attacker-controlled content, to be compiled as Jinja2 template source rather than passing the input as template data. The resulting source-to-sink flow creates server-side template injection.


# Avoid Overclaiming

Do not write:

```text
SSTI gives remote code execution.
```

unless command/code execution was actually established and necessary to demonstrate impact.


# Better

```text
The application evaluates attacker-controlled input as
server-side template syntax.
```


# Then State Demonstrated Impact

For example:

```text
The test demonstrated arbitrary template expression evaluation.

Operating-system command execution was not tested because it was
not required to establish the vulnerability.
```


# Severity Considerations

Consider:

```text
Authentication required

User role required

Template engine

Sandbox configuration

Objects exposed

Sensitive data reachable

Cross-tenant access

Available helper functions

Application privileges

Network access

Whether template authoring is intended
```


# Remediation - Keep Templates Static

Preferred architecture:

```text
Static Template
      |
      +--> Trusted Template Syntax
      |
      +--> Untrusted Data
```


# Avoid

```text
Template Source =
"Hello " + user_input
```


# Prefer

Template:

```html
Hello {{ name }}
```

Application:

```text
name = user_input
```


# Separate Code and Data

The core remediation principle is:

```text
USER INPUT
    |
    v
TEMPLATE DATA

NOT

USER INPUT
    |
    v
TEMPLATE SOURCE
```


# Avoid Dynamic Compilation

Do not dynamically compile attacker-controlled strings as templates unless template authoring is an intentional feature with a carefully designed sandbox.


# Jinja2 Remediation

Avoid constructing:

```python
render_template_string(
    "Hello " + user_input
)
```

Prefer a static template:

```python
render_template(
    "hello.html",
    name=user_input
)
```


# Twig Remediation

Avoid dynamically creating template source from user input.

Prefer:

```text
Static Twig template

+

User-controlled context variable
```


# Java Template Engines

Prefer:

```text
Trusted template file

+

Typed context data
```

rather than:

```text
Dynamic template expression assembled from request data
```


# Sandboxing

If user-authored templates are a required feature:

```text
Use a restricted template language

Minimise exposed objects

Disable unsafe functions

Restrict method invocation

Restrict filesystem access

Restrict network access

Apply resource limits
```


# Least Privilege

The template-rendering process should have minimal access to:

```text
Filesystem

Environment secrets

Internal services

Cloud metadata

Administrative APIs
```


# Network Restrictions

If rendering workers do not require outbound network access, restrict it.

This is defence in depth, not a substitute for safe template handling.


# Dedicated Rendering Service

High-risk user-authored template functionality can be isolated:

```text
Application
    |
    v
Restricted Rendering Service
    |
    v
Rendered Output
```

with:

```text
No secrets

No sensitive mounts

Minimal network access

Resource limits
```


# Resource Limits

User-authored templates may consume:

```text
CPU

Memory

Rendering time
```

Apply appropriate limits where template authoring is supported.


# Retesting

Retest the original vulnerable rendering path.


# Retest Baseline

Confirm normal template rendering still works.


# Retest Original Arithmetic

Input:

```text
SSTI_A{{137*41}}SSTI_B
```

should now remain data rather than become:

```text
SSTI_A5617SSTI_B
```


# Expected Safe Result

Depending on context, the application may return:

```text
SSTI_A{{137*41}}SSTI_B
```

as literal text.


# Retest Multiple Syntax Families

If the vulnerable code was replaced correctly, template syntax from other engines should also remain data because attacker-controlled input should never reach template compilation.


# Retest Stored Paths

If the issue was second-order:

```text
Store value

Trigger downstream report/email

Verify no evaluation
```


# Retest Preview and Production

If both exist:

```text
Preview

Actual delivery
```

must be tested separately.


# Retest Role Boundaries

For user-authored templates, verify:

```text
Allowed template capabilities remain functional

Restricted objects remain inaccessible

Tenant isolation is enforced
```


# Retest Source

Verify the source now uses:

```text
Static template

+

Context variable
```

instead of:

```text
String concatenation

+

Dynamic compilation
```


# Root Cause Review

After finding one SSTI path, search for all dynamic template compilation.

Python:

```bash
rg -ni 'render_template_string|jinja2|Template\(' -g '*.py' .
```

PHP:

```bash
rg -ni 'Twig|createTemplate|Smarty|fetch\(|display\(' -g '*.php' .
```

Java:

```bash
rg -ni 'freemarker|VelocityEngine|evaluate\(|TemplateEngine|thymeleaf|PebbleEngine' -g '*.java' .
```

Node.js:

```bash
rg -ni 'nunjucks|renderString|handlebars|compile\(|mustache|pug' -g '*.js' -g '*.ts' .
```

Ruby:

```bash
rg -ni 'ERB|ERB\.new|render.*inline|Liquid::Template' -g '*.rb' .
```


# Search Template Files

```bash
find . -type f \( \
  -name '*.jinja' -o \
  -name '*.jinja2' -o \
  -name '*.j2' -o \
  -name '*.twig' -o \
  -name '*.ftl' -o \
  -name '*.vm' -o \
  -name '*.hbs' -o \
  -name '*.handlebars' -o \
  -name '*.liquid' -o \
  -name '*.erb' -o \
  -name '*.pug' \
\)
```


# Practical SSTI Checklist

## Discovery

- [ ] Server-rendered inputs identified
- [ ] Preview functionality reviewed
- [ ] Email templates reviewed
- [ ] PDF generation reviewed
- [ ] Report generation reviewed
- [ ] CMS templates reviewed
- [ ] Notification templates reviewed
- [ ] Administrative template features reviewed
- [ ] Stored inputs considered
- [ ] Background rendering considered

## Baseline

- [ ] Unique marker submitted
- [ ] Reflection confirmed
- [ ] Raw HTTP response captured
- [ ] Rendering context identified
- [ ] Authentication context recorded
- [ ] Response time recorded

## Detection

- [ ] Harmless arithmetic probe used
- [ ] Unique arithmetic result selected
- [ ] Marker wrappers used
- [ ] Result distinguished from reflection
- [ ] Probe repeated
- [ ] Browser-side evaluation excluded

## Fingerprinting

- [ ] Application stack reviewed
- [ ] Error messages reviewed
- [ ] Dependencies reviewed
- [ ] Template extensions reviewed
- [ ] Template engine identified where possible
- [ ] Unnecessary aggressive probing avoided

## Stored SSTI

- [ ] Stored profile fields reviewed
- [ ] Admin views reviewed
- [ ] Emails reviewed
- [ ] Reports reviewed
- [ ] PDFs reviewed
- [ ] Background jobs reviewed
- [ ] Second-order evaluation considered

## Source Review

- [ ] Template engine identified
- [ ] Template compiler/render APIs located
- [ ] User-controlled sources traced
- [ ] String concatenation reviewed
- [ ] Dynamic template compilation reviewed
- [ ] Context variables reviewed
- [ ] Sandbox configuration reviewed
- [ ] Exposed objects reviewed

## Evidence

- [ ] Endpoint
- [ ] Method
- [ ] Parameter
- [ ] Authentication context
- [ ] Baseline marker
- [ ] Template expression
- [ ] Expected result
- [ ] Actual result
- [ ] Raw response
- [ ] Engine evidence
- [ ] Timestamp
- [ ] Sensitive information redacted

## Remediation

- [ ] Static templates used
- [ ] User input passed as data
- [ ] Dynamic compilation removed
- [ ] Sandbox reviewed where required
- [ ] Exposed objects minimised
- [ ] Renderer privileges reduced
- [ ] Network access restricted where appropriate
- [ ] Resource limits applied where appropriate

## Retest

- [ ] Legitimate rendering works
- [ ] Original arithmetic expression no longer evaluates
- [ ] Stored rendering path retested
- [ ] Preview retested
- [ ] Production delivery retested
- [ ] Role boundaries retested
- [ ] Tenant isolation retested
- [ ] Source fix verified
- [ ] Equivalent template sinks reviewed


# Engine Identification Matrix

| Technology | Common Template Engines |
|---|---|
| Python | Jinja2, Mako |
| PHP | Twig, Smarty |
| Java | FreeMarker, Velocity, Thymeleaf, Pebble |
| Node.js | Nunjucks, Handlebars, Mustache, Pug |
| Ruby | ERB, Liquid |


# Common Syntax Matrix

| Syntax | Possible Engine Families |
|---|---|
| `{{ ... }}` | Jinja2, Twig, Nunjucks and others |
| `${ ... }` | FreeMarker and other expression languages |
| `#{ ... }` | Some Java expression contexts |
| `<%= ... %>` | ERB and similar syntax families |

Syntax alone is not sufficient for reliable engine identification.


# Evidence Matrix

| Observation | Interpretation |
|---|---|
| Expression returned unchanged | Reflection only |
| Expression HTML encoded | Output handling, not SSTI proof |
| Template syntax error | Possible parser reachability |
| Arithmetic evaluated | Strong SSTI evidence |
| Two arithmetic probes evaluated | Strong repeatable evidence |
| Browser evaluates after load | Potential client-side issue |
| Raw HTTP response contains evaluated result | Server-side evaluation strongly supported |
| Source concatenates input into template compiler | Strong white-box evidence |


# Source Review Priority Matrix

| Pattern | Priority |
|---|---:|
| Static template + context data | Lower |
| User selects trusted template ID | Review |
| User controls template filename | High |
| User input concatenated into template source | Very High |
| User input passed to dynamic compile API | Very High |
| User-authored templates with sandbox | Review sandbox |
| User-authored templates without isolation | Very High |


# SSTI vs Related Vulnerabilities

| Behaviour | Likely Classification |
|---|---|
| Server evaluates template expression | SSTI |
| Browser executes injected JavaScript | XSS |
| Browser renders injected markup | HTML Injection |
| SQL parser interprets user syntax | SQL Injection |
| Shell interprets user syntax | Command Injection |
| Backend retrieves attacker-selected URL | SSRF |
| XML parser resolves external entity | XXE |


# Impact Matrix

| Demonstrated Behaviour | Supported Conclusion |
|---|---|
| Arithmetic evaluation | Template expression execution |
| Template parser error | Template parser reachability |
| Non-sensitive context value exposed | Template context access |
| Cross-tenant object exposed | Tenant isolation failure |
| Sensitive application data exposed | Information disclosure |
| OS command execution | Code/command execution through SSTI |


# Remediation Matrix

| Control | Purpose |
|---|---|
| Static templates | Prevent attacker-controlled template source |
| Context variables | Keep data separate from template syntax |
| Avoid dynamic compilation | Remove primary SSTI sink |
| Template sandbox | Restrict intentionally user-authored templates |
| Minimal context | Reduce exposed application objects |
| Least privilege | Reduce renderer impact |
| Network restrictions | Reduce backend reach |
| Resource limits | Reduce template abuse |


# Burp Quick Workflow

```text
                 INPUT LOCATION
                       |
                       v
                  UNIQUE MARKER
                       |
                       v
                   REFLECTED?
                       |
                       v
                ARITHMETIC PROBE
                       |
             +---------+---------+
             |                   |
             v                   v
          LITERAL             EVALUATED
             |                   |
             v                   v
      NO SSTI PROOF        REPEAT PROBE
                                 |
                                 v
                          IDENTIFY ENGINE
                                 |
                                 v
                           CAPTURE EVIDENCE
```


# White-Box Review Model

```text
                   USER INPUT
                       |
                       v
                APPLICATION DATA
                       |
            +----------+----------+
            |                     |
            v                     v
       CONTEXT VARIABLE      STRING CONCATENATION
            |                     |
            v                     v
      STATIC TEMPLATE       DYNAMIC TEMPLATE
            |                     |
            v                     v
        RENDERER               COMPILER
            |                     |
            v                     v
        EXPECTED             SSTI CANDIDATE
```


# Second-Order SSTI Model

```text
                USER INPUT
                    |
                    v
                  STORE
                    |
                    v
             DATABASE / RECORD
                    |
                    v
             LATER CONSUMER
                    |
          +---------+---------+
          |                   |
          v                   v
     SAFE CONTEXT       TEMPLATE SOURCE
          |                   |
          v                   v
        OUTPUT             EVALUATION
```


# Secure Template Model

```text
                 TRUSTED TEMPLATE
                       |
                       |
                       +----------------+
                                        |
                                        v
USER INPUT --> VALIDATION --> CONTEXT VARIABLES
                                        |
                                        v
                                  TEMPLATE ENGINE
                                        |
                                        v
                                     OUTPUT
```


# Practical Validation Model

```text
Prerequisites
     |
     v
Baseline
     |
     v
Unique Marker
     |
     v
Harmless Expression
     |
     v
Representative Result
     |
     v
Interpretation
     |
     v
Repeat
     |
     v
Conclusion
     |
     v
Remediation
     |
     v
Retest
```


# Final Testing Principle

The key question is not:

```text
Does {{7*7}} produce 49?
```

The deeper question is:

```text
WHY WAS ATTACKER-CONTROLLED DATA
              |
              v
INTERPRETED AS TEMPLATE SOURCE
              |
              v
INSTEAD OF TEMPLATE DATA?
```

A strong SSTI workflow is:

```text
Identify Rendering Feature
        |
        v
Establish Baseline
        |
        v
Submit Unique Marker
        |
        v
Determine Reflection
        |
        v
Use Harmless Arithmetic
        |
        v
Confirm Server-Side Evaluation
        |
        v
Repeat With Different Result
        |
        v
Identify Template Engine
        |
        v
Understand Trust Boundary
        |
        v
Capture Evidence
        |
        v
Separate Template From Data
        |
        v
Retest
```

For every SSTI candidate ask:

```text
Where is the value rendered?

Is rendering server-side or client-side?

Does the raw HTTP response contain the evaluated result?

Is the value merely reflected?

Which template engine is used?

Can source or dependencies identify the engine?

Is the template static?

Is user input passed as context data?

Is user input concatenated into template source?

Is a dynamic template compiler used?

Can the result be reproduced?

Could caching explain the result?

Could browser-side JavaScript explain the result?

Is template authoring intentional?

If intentional, is a sandbox present?

Which objects are exposed to the template?

Are templates tenant-isolated?

Does the renderer have unnecessary privileges?

Does the renderer have unnecessary network access?

Is additional impact testing actually required?

Can the issue be proven with arithmetic alone?

Have stored and second-order rendering paths been reviewed?

Have preview and production rendering both been tested?

Has the root cause been removed rather than filtered?
```

The strongest conventional SSTI finding is not:

```text
The application accepts {{7*7}}.
```

It is:

```text
ATTACKER-CONTROLLED INPUT
          |
          v
BECOMES TEMPLATE SOURCE
          |
          v
SERVER EVALUATES EXPRESSION
          |
          v
DETERMINISTIC RESULT
          |
          v
REPEATABLE SSTI
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)
- [SQL Injection Cheatsheet](sql-injection.md)
- [Cross-Site Scripting (XSS) Cheatsheet](xss.md)
- [OS Command Injection Cheatsheet](command-injection.md)
- [Server-Side Request Forgery (SSRF) Cheatsheet](ssrf.md)
- [XML External Entity Injection (XXE) Cheatsheet](xxe.md)


# Related Notes

- [Server-Side Template Injection](../web/ssti.md)
- [OS Command Injection](../web/command-injection.md)
- [Cross-Site Scripting](../web/xss.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - Server-Side Template Injection](https://portswigger.net/web-security/server-side-template-injection){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for Server-Side Template Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server_Side_Template_Injection){ target="_blank" rel="noopener noreferrer" }
- [Jinja Documentation](https://jinja.palletsprojects.com/){ target="_blank" rel="noopener noreferrer" }
- [Twig Documentation](https://twig.symfony.com/doc/){ target="_blank" rel="noopener noreferrer" }
- [Apache FreeMarker](https://freemarker.apache.org/){ target="_blank" rel="noopener noreferrer" }
- [Apache Velocity](https://velocity.apache.org/){ target="_blank" rel="noopener noreferrer" }
- [Thymeleaf](https://www.thymeleaf.org/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Arithmetic first"

    A deterministic arithmetic result is usually enough to establish unintended server-side template evaluation. Start there rather than immediately attempting file access, object traversal or operating-system command execution.


!!! tip "Check the raw response"

    Comparing the raw HTTP response with the browser-rendered DOM helps distinguish server-side template evaluation from client-side template processing.


!!! tip "Source review is especially valuable"

    SSTI becomes much easier to reason about when you can identify the exact template engine and determine whether user input is passed as template data or compiled as template source.


!!! warning "Template evaluation does not automatically mean RCE"

    The impact depends on the template engine, available objects, sandbox configuration and application environment. Report what was actually demonstrated.


!!! warning "Do not fix SSTI with a syntax blacklist"

    Blocking `{{`, `${` or other template delimiters does not address the underlying design problem. Keep attacker-controlled values out of template source and pass them through the engine's data/context mechanism instead.
