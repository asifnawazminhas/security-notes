# Server-Side Template Injection

Server-Side Template Injection (SSTI) occurs when attacker-controlled input is interpreted by a server-side template engine as template syntax rather than being treated purely as data.

Template engines are commonly used to dynamically generate:

```text
HTML
Emails
PDF documents
Reports
Notifications
Configuration files
Documents
Messages
Invoices
Administrative pages
```

A normal template flow looks like:

```text
Template
   +
Application Data
   ↓
Template Engine
   ↓
Rendered Output
```

For example:

```text
Hello {{ username }}
```

with:

```text
username = Asif
```

may produce:

```text
Hello Asif
```

The vulnerability appears when attacker-controlled input becomes part of the template itself:

```text
Attacker Input
      ↓
Template Construction
      ↓
Template Engine
      ↓
Attacker Input Parsed as Template Syntax
```

Depending on the template engine and environment, the impact can range from simple information disclosure to access to server-side objects or, in severe cases, remote code execution.

!!! warning "Authorised Security Testing"
    Perform SSTI testing only against applications for which you have explicit authorisation. Begin with harmless mathematical or string expressions. Do not immediately attempt operating-system command execution. Establish template evaluation first, identify the engine and context, and use the minimum impact necessary to demonstrate the vulnerability.

---

# Mental Model

Consider an application that generates a greeting.

A safe implementation might use:

```text
Template:

Hello {{ name }}

Data:

name = Asif
```

The template engine receives:

```text
Template
+
Data
```

and renders:

```text
Hello Asif
```

The attacker controls only:

```text
Data
```

This is normally safe from SSTI when the template engine treats the value as data.

A vulnerable implementation might instead construct the template dynamically:

```text
template = "Hello " + userInput
```

The resulting flow becomes:

```text
User Input
    ↓
Template Source
    ↓
Template Engine
    ↓
Evaluation
```

If the user supplies template syntax, it may be interpreted.

---

# SSTI vs XSS

SSTI and Cross-Site Scripting are different vulnerability classes.

XSS occurs primarily in the browser:

```text
Attacker Input
      ↓
Application
      ↓
HTML Response
      ↓
Victim Browser
      ↓
JavaScript Execution
```

SSTI occurs on the server:

```text
Attacker Input
      ↓
Application
      ↓
Template Engine
      ↓
Server-Side Evaluation
```

The key distinction is:

```text
XSS
Client-Side Execution

SSTI
Server-Side Template Evaluation
```

An input may potentially be vulnerable to both, but they should be tested and reported separately.

---

# SSTI vs Client-Side Template Injection

Modern JavaScript frameworks may also use template syntax.

Examples include:

```text
Angular
Vue
Handlebars in the browser
Client-side Mustache
```

If the expression is evaluated by JavaScript in the browser, this is not Server-Side Template Injection.

Always determine:

```text
Where is the expression evaluated?
```

The evaluation location matters.

---

# Why SSTI Matters

Template engines frequently have access to application data and runtime objects.

Depending on the engine and configuration, template evaluation may expose:

```text
Application variables
Configuration
Environment information
Framework objects
Request objects
Session objects
File-system functionality
Language runtime objects
Application secrets
Server-side methods
```

In some environments, dangerous object traversal can ultimately reach functionality capable of operating-system command execution.

The potential progression can therefore be:

```text
Template Evaluation
       ↓
Object Access
       ↓
Application Information
       ↓
Runtime Objects
       ↓
Dangerous Functionality
       ↓
Potential RCE
```

This progression is engine-specific and should never be assumed automatically.

---

# Common Template Engines

Template engines vary by programming language and framework.

## Python

Common Python template engines include:

```text
Jinja2
Mako
Django Templates
Tornado Templates
Chameleon
```

Jinja2 is particularly common with Flask applications.

---

## PHP

Common PHP template engines include:

```text
Twig
Smarty
Blade
Latte
```

---

## Java

Common Java template engines include:

```text
FreeMarker
Velocity
Thymeleaf
Pebble
Jinjava
```

---

## Node.js

Common Node.js template engines include:

```text
Pug
EJS
Handlebars
Mustache
Nunjucks
```

---

## Ruby

Common Ruby template engines include:

```text
ERB
Haml
Liquid
Slim
```

---

## .NET

Common .NET template technologies include:

```text
Razor
Scriban
DotLiquid
Fluid
```

---

# Where to Look for SSTI

SSTI can occur anywhere user-controlled data is used to construct templates.

Interesting functionality includes:

```text
Email templates
Notification templates
PDF generation
Report generation
Invoice generation
Document generation
CMS templates
Custom themes
Administrative templates
Message previews
User profiles
Custom greetings
Search results
Error pages
Email subjects
Email bodies
Support tickets
Marketing templates
Print views
Export functionality
Custom dashboards
Signature templates
Webhook templates
Dynamic configuration
```

---

# High-Value Features

Pay particular attention to functionality explicitly allowing users to customise content.

Examples:

```text
Custom email template
Custom notification
Custom report
Custom invoice
Custom message
Custom document
Custom theme
Custom page
Template preview
Email preview
PDF preview
```

The more control the user has over the template source, the more interesting the feature becomes.

---

# Interesting Parameters

Potential parameter names include:

```text
template
content
body
message
text
name
title
subject
description
format
view
page
layout
theme
email
email_body
email_template
notification
notification_template
report
report_template
document
document_template
preview
render
renderer
expression
```

These are discovery hints rather than evidence of SSTI.

---

# SSTI Testing Workflow

A structured workflow can look like:

```text
Identify Reflected / Rendered Input
              ↓
Establish Baseline
              ↓
Determine Rendering Context
              ↓
Insert Harmless Marker
              ↓
Test Harmless Template Expressions
              ↓
Determine Whether Evaluation Occurs
              ↓
Fingerprint Template Engine
              ↓
Determine Accessible Context
              ↓
Assess Sandbox / Restrictions
              ↓
Determine Minimum Demonstrable Impact
              ↓
Review Source Where Available
              ↓
Report
```

---

# Start With a Unique Marker

Before trying template syntax, understand where your input appears.

For example:

```text
AM-SSTI-987654
```

Submit the marker.

Then determine whether it appears in:

```text
HTML
Email
PDF
JSON
Report
Administrative interface
Background-generated document
```

This establishes the source-to-rendering path.

---

# Harmless Detection

The first objective is not command execution.

The first objective is:

> Determine whether the server interprets attacker-controlled input as template syntax.

Use harmless mathematical expressions where appropriate.

A common conceptual test is:

```text
7 × 7
```

If the template engine evaluates an expression containing those values and returns:

```text
49
```

rather than the literal expression, server-side template evaluation may be occurring.

---

# Why Use Arithmetic?

Arithmetic is useful because it has:

```text
No operating-system interaction
No network interaction
No file access
No destructive effect
```

It provides a clean distinction between:

```text
Literal Rendering
```

and:

```text
Expression Evaluation
```

---

# Basic Expression Families

Different template engines use different syntax.

Common expression delimiters include:

```text
{{ ... }}
${ ... }
#{ ... }
<%= ... %>
```

For example, a harmless test might conceptually be:

```text
{{ 7 * 7 }}
```

If the response becomes:

```text
49
```

instead of:

```text
{{ 7 * 7 }}
```

this is a strong SSTI indicator.

---

# Important Detection Principle

Do not assume:

```text
{{7*7}} → 49
```

means:

```text
Jinja2
```

Many template engines use similar syntax.

The correct workflow is:

```text
Expression Evaluation
        ↓
SSTI Candidate
        ↓
Engine Fingerprinting
        ↓
Context Analysis
```

---

# Baseline Testing

Suppose the application accepts:

```http
POST /preview HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

name=Asif
```

and returns:

```html
Hello Asif
```

First establish the baseline.

Then test:

```http
POST /preview HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

name=AM-SSTI-001
```

Confirm:

```html
Hello AM-SSTI-001
```

Then test a harmless template expression appropriate to the suspected environment.

---

# Burp Suite Workflow

Burp Suite is particularly useful for SSTI testing.

A practical workflow is:

```text
Proxy
  ↓
HTTP History
  ↓
Identify Rendered Input
  ↓
Send to Repeater
  ↓
Baseline
  ↓
Unique Marker
  ↓
Harmless Expression
  ↓
Compare Response
  ↓
Fingerprint Engine
  ↓
Investigate Context
```

---

# Burp Repeater

Repeater should normally be the primary manual tool.

Suppose:

```http
POST /api/report/preview HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "title": "Quarterly Report"
}
```

Change:

```json
{
  "title": "AM-SSTI-001"
}
```

Then, where appropriate:

```json
{
  "title": "{{7*7}}"
}
```

Compare the response.

Possible results include:

```text
{{7*7}}
49
500 Internal Server Error
Template syntax error
Input removed
Input encoded
```

Each provides information.

---

# Response Comparison

Record:

```text
Status code
Response length
Response body
Error message
Response time
Generated document
Email output
```

A useful table:

| Input | Output | Interpretation |
|---|---|---|
| `AM-SSTI-001` | `AM-SSTI-001` | Reflection confirmed |
| `{{7*7}}` | `{{7*7}}` | Possibly literal |
| `{{7*7}}` | `49` | Expression evaluation |
| Invalid syntax | Template error | Possible template processing |

---

# Template Errors

Errors can reveal the underlying engine.

Potential information includes:

```text
Template engine name
Framework
Template file
Template line
Expression parser
Class names
Package names
Stack traces
```

For example, an error mentioning:

```text
jinja2
```

is a strong technology indicator.

Likewise:

```text
Twig
FreeMarker
Velocity
Thymeleaf
Smarty
Handlebars
```

may appear in stack traces or error pages.

---

# Do Not Rely Only on Errors

Production applications often suppress stack traces.

Fingerprinting should combine:

```text
Technology identification
Expression behaviour
Syntax behaviour
Error behaviour
Source review
Framework knowledge
```

---

# Technology Identification

Before SSTI testing, identify the application stack.

Useful tools include:

```text
Wappalyzer
WhatWeb
httpx
BuiltWith
Browser DevTools
Burp Suite
Source code
HTTP headers
Error pages
JavaScript bundles
Cookies
```

For example:

```bash
whatweb https://target.example
```

or:

```bash
httpx -u https://target.example -tech-detect
```

If the application appears to use:

```text
Flask
```

then:

```text
Jinja2
```

becomes an interesting candidate.

If it uses:

```text
Symfony
```

then:

```text
Twig
```

may be relevant.

Technology identification narrows the testing space.

---

# Template Engine Fingerprinting

After confirming expression evaluation, determine which engine is responsible.

A conceptual fingerprinting tree looks like:

```text
Expression Evaluates?
       ↓
      Yes
       ↓
Which Syntax Works?
       ↓
Compare Behaviour
       ↓
Identify Engine Family
       ↓
Confirm Through Engine-Specific Behaviour
```

Do not jump directly to dangerous engine-specific expressions.

---

# Fingerprinting Methodology

The process should be:

```text
1. Confirm reflection

2. Confirm template evaluation

3. Test harmless syntax differences

4. Observe output

5. Observe errors

6. Correlate with application technology

7. Identify probable template engine

8. Confirm using non-destructive engine-specific behaviour
```

---

# PortSwigger SSTI Decision Tree

PortSwigger's Server-Side Template Injection research describes a decision-tree approach for identifying template engines.

The idea is to submit expressions whose interpretation differs between template engines.

Conceptually:

```text
Generic Expression
      ↓
Different Engine Behaviour
      ↓
Next Harmless Probe
      ↓
Narrow Engine
      ↓
Confirm
```

This is preferable to blindly sending large payload lists.

---

# Jinja2

Jinja2 is commonly used in Python applications.

It is frequently associated with:

```text
Flask
```

Typical template syntax includes:

```text
{{ expression }}
```

A harmless evaluation check:

```text
{{7*7}}
```

Expected evaluation:

```text
49
```

This proves template expression evaluation but does not alone prove the engine is Jinja2.

---

# Jinja2 Context

Jinja2 templates may have access to application-provided variables and objects.

Potential categories include:

```text
Template variables
Request information
Configuration
Helper functions
Application objects
```

Exactly what is available depends on:

```text
Framework
Application
Template environment
Sandboxing
Custom globals
```

Do not assume every Jinja2 template has access to every Flask object.

---

# Jinja2 and Flask

Flask uses Jinja as its default template engine.

A dangerous design pattern is conceptually:

```python
template = request.args.get("template")
return render_template_string(template)
```

The problem is:

```text
User Input
    ↓
Template Source
    ↓
render_template_string()
    ↓
Jinja Evaluation
```

Compare this with:

```python
return render_template(
    "hello.html",
    username=request.args.get("username")
)
```

where the user input is passed as template data rather than template source.

---

# Twig

Twig is a PHP template engine commonly associated with frameworks such as Symfony.

Typical syntax includes:

```text
{{ expression }}
```

A harmless arithmetic test may evaluate:

```text
{{7*7}}
```

to:

```text
49
```

Again, this syntax overlaps with other engines.

Fingerprint the environment before drawing conclusions.

---

# Smarty

Smarty is another PHP template engine.

Template syntax and capabilities differ by version and configuration.

When Smarty is suspected:

```text
Confirm technology
 ↓
Confirm expression evaluation
 ↓
Identify version where possible
 ↓
Review allowed template functionality
```

Avoid assuming that techniques documented for older Smarty versions apply to modern configurations.

---

# FreeMarker

Apache FreeMarker is commonly found in Java environments.

It uses template expressions such as:

```text
${ ... }
```

A harmless arithmetic concept is:

```text
${7*7}
```

which may render:

```text
49
```

if evaluated.

FreeMarker environments can expose Java-side objects depending on how the application configures the template model.

---

# Velocity

Apache Velocity is another Java template engine.

Its syntax commonly uses:

```text
$variable
```

and:

```text
#set(...)
```

Fingerprint Velocity using harmless template behaviour before exploring accessible objects.

---

# Thymeleaf

Thymeleaf is widely used with:

```text
Spring
Spring Boot
```

Thymeleaf expressions may include:

```text
${...}
```

and other expression types depending on the context.

Thymeleaf SSTI behaviour is heavily dependent on:

```text
Where the attacker input appears
How templates are resolved
Expression preprocessing
Framework configuration
```

Do not treat every reflected `${...}` as SSTI.

---

# Pebble

Pebble is a Java template engine whose syntax resembles Jinja and Twig.

Typical expressions may use:

```text
{{ ... }}
```

This is another reason that:

```text
{{7*7}}
```

alone cannot identify the engine.

---

# Handlebars

Handlebars is commonly associated with JavaScript.

Typical syntax:

```text
{{variable}}
```

Handlebars implementations are designed primarily around variable interpolation and helpers.

Whether dangerous server-side behaviour is possible depends heavily on:

```text
Implementation
Version
Registered helpers
Application objects
Runtime configuration
```

---

# Mustache

Mustache intentionally provides a relatively limited template model.

Typical syntax:

```text
{{variable}}
```

The presence of Mustache-style interpolation does not automatically imply high-impact SSTI.

Assess what the template environment actually permits.

---

# Nunjucks

Nunjucks is a JavaScript template engine inspired by Jinja2.

Typical syntax includes:

```text
{{ ... }}
```

When testing Node.js applications, Nunjucks should be considered if Jinja-like syntax evaluates server-side.

---

# Pug

Pug is a Node.js template engine formerly known as Jade.

Pug uses a different template syntax from Jinja-style engines.

Applications that dynamically compile user-controlled Pug template source can introduce serious server-side risks.

Focus on whether:

```text
User Input
     ↓
Template Source
     ↓
Pug Compilation
```

occurs.

---

# EJS

Embedded JavaScript templates use syntax such as:

```text
<%= ... %>
```

A vulnerable design occurs when attacker-controlled input becomes template source.

The core question remains:

```text
Is user input data?

or

Is user input executable template syntax?
```

---

# ERB

ERB is commonly used in Ruby applications.

Typical syntax includes:

```text
<%= ... %>
```

If attacker-controlled content becomes ERB template source, server-side Ruby expression evaluation may occur.

---

# Liquid

Liquid is used in environments including:

```text
Shopify
Jekyll
Ruby applications
```

Liquid intentionally provides a more restricted template environment than general-purpose code execution engines.

However, security impact still depends on:

```text
Available objects
Custom filters
Custom tags
Application extensions
```

Do not automatically equate template injection with operating-system command execution.

---

# Razor

Razor is commonly associated with ASP.NET.

Razor syntax uses:

```text
@
```

to transition into server-side expressions.

Dynamic compilation of attacker-controlled Razor templates can create significant server-side risk.

However, normal Razor views with safely passed model data are not SSTI.

---

# Context Matters

The same input can behave differently depending on where it is inserted.

Consider:

```text
{{ userInput }}
```

versus dynamically constructing:

```text
{{ <userInput> }}
```

The first treats input as data.

The second may treat it as part of an expression.

Therefore SSTI testing requires understanding:

```text
Template Context
```

---

# Plain-Text Context

User input may be inserted directly into template text:

```text
Hello USER_INPUT
```

If the final template becomes:

```text
Hello {{7*7}}
```

the expression may be evaluated.

---

# Expression Context

Input may appear inside an existing expression.

Conceptually:

```text
{{ user.USER_INPUT }}
```

This creates a different testing problem.

The tester may need to understand:

```text
Existing expression
Quotes
Operators
Delimiters
Template grammar
```

before determining whether injection is possible.

---

# Attribute Context

Input may be rendered inside HTML attributes:

```html
<a title="{{ value }}">
```

This can introduce:

```text
SSTI
XSS
```

as separate potential issues depending on where evaluation occurs and how output is encoded.

---

# Template Code vs Rendered Output

Always distinguish:

```text
Template Source
```

from:

```text
Rendered Output
```

For example:

```text
Template:
{{7*7}}

Rendered:
49
```

The rendered output no longer contains the original syntax.

This is one of the clearest SSTI indicators.

---

# Double Rendering

Some applications render content more than once.

Conceptually:

```text
User Input
   ↓
First Template
   ↓
Intermediate Output
   ↓
Second Template Engine
   ↓
Final Output
```

This can create second-order or nested template injection.

---

# Second-Order SSTI

SSTI may not trigger immediately.

For example:

```text
User Creates Profile
       ↓
Display Name Stored
       ↓
Administrator Generates Report
       ↓
Report Template Includes Display Name
       ↓
Template Engine Evaluates Input
```

The vulnerability is therefore:

```text
Stored Input
    ↓
Later Template Processing
    ↓
SSTI
```

---

# Where Second-Order SSTI Appears

Potential locations include:

```text
Reports
PDFs
Invoices
Emails
Administrative exports
Scheduled notifications
CRM templates
Support systems
Background jobs
Audit reports
```

Use unique markers to track delayed rendering.

---

# SSTI in Email Templates

Email generation frequently uses template engines.

Potential flow:

```text
User Input
   ↓
Database
   ↓
Email Template
   ↓
Template Engine
   ↓
Email
```

Interesting fields include:

```text
Name
Company
Subject
Message
Signature
Profile fields
Custom attributes
```

Test with harmless markers first.

---

# SSTI in PDF Generation

PDF generation may involve:

```text
Template Engine
       ↓
HTML
       ↓
PDF Renderer
       ↓
PDF
```

A vulnerability may occur before the PDF renderer even processes the document.

For example:

```text
User Input
   ↓
Jinja / Twig / Other Template
   ↓
Rendered HTML
   ↓
PDF
```

This is different from SSRF caused by the PDF renderer fetching external resources.

---

# SSTI + SSRF

Template injection may expose functionality capable of making outbound requests.

Conceptually:

```text
SSTI
 ↓
Template Object / Function
 ↓
Network Request
 ↓
SSRF-Like Behaviour
```

However, report the primary root cause correctly.

If arbitrary template evaluation provides access to network functionality, SSTI is usually the underlying issue.

---

# SSTI + File Read

Some template environments expose functions or objects capable of accessing local resources.

Potential progression:

```text
SSTI
 ↓
Runtime Objects
 ↓
File Functionality
 ↓
Local File Read
```

Do not attempt unnecessary file access.

A harmless application or framework value may be enough to demonstrate expanded server-side access.

---

# SSTI + Remote Code Execution

In severe cases:

```text
SSTI
 ↓
Runtime Object Access
 ↓
Dangerous Method
 ↓
Process Execution
 ↓
RCE
```

This is highly engine-specific.

Do not begin testing SSTI by attempting:

```text
whoami
id
cmd.exe
PowerShell
reverse shells
```

First establish:

```text
Template Evaluation
```

Then determine whether additional impact testing is necessary and authorised.

---

# Minimum Necessary Proof

A good SSTI assessment follows:

```text
Lowest Impact
    ↓
Sufficient Evidence
```

For example:

```text
{{7*7}}
      ↓
49
```

may already prove template evaluation.

If severity depends on access to sensitive server-side objects, demonstrate the least sensitive object necessary.

Do not unnecessarily retrieve:

```text
Passwords
API keys
Tokens
Private keys
Customer data
Cloud credentials
```

---

# Template Context Enumeration

After confirming SSTI, determine what data is exposed to the template.

Look for:

```text
Documented variables
Application variables
Request properties
User properties
Configuration values
Template globals
Helper functions
Custom filters
Custom tags
```

Prefer documented or harmless objects.

---

# Object Traversal

Some engines allow properties of exposed objects to be traversed.

Conceptually:

```text
Template Variable
      ↓
Object
      ↓
Property
      ↓
Nested Object
```

This may expose more of the application runtime than intended.

The security question is:

> Can attacker-controlled template expressions escape the intended template data model?

---

# Sandbox

Some template engines provide sandbox functionality.

A sandbox attempts to restrict:

```text
Object access
Method calls
Attributes
Functions
Classes
Modules
Runtime functionality
```

The presence of a sandbox does not automatically mean the environment is secure.

The relevant questions are:

```text
Is sandboxing enabled?
Which objects are exposed?
Which methods are callable?
Are custom helpers available?
Is the engine up to date?
```

---

# Sandbox Escape

Sandbox escapes are highly version and implementation specific.

Do not assume a historical sandbox escape works against:

```text
Current versions
Different frameworks
Custom configurations
```

During authorised testing:

```text
Identify exact engine
 ↓
Identify version
 ↓
Review current documentation
 ↓
Determine sandbox configuration
 ↓
Use minimal safe validation
```

---

# Version Identification

Version information can significantly change SSTI impact.

Possible sources include:

```text
Dependency files
Error pages
Package manifests
Lock files
Build files
Source code
SBOM
HTTP headers
Application documentation
```

Examples:

```text
requirements.txt
poetry.lock
package.json
package-lock.json
composer.json
composer.lock
pom.xml
build.gradle
Gemfile.lock
*.csproj
```

---

# Source Code Review

Source review is extremely effective for SSTI.

The general model is:

```text
SOURCE
  ↓
User-Controlled Input
  ↓
Template Construction
  ↓
Template Compilation / Rendering
  ↓
SINK
```

---

# Python Source Review

Interesting Jinja-related functions include:

```text
render_template
render_template_string
Environment
Template
from_string
```

Search:

```bash
rg -n \
'render_template_string|render_template|Environment\(|Template\(|from_string'
```

Pay particular attention to:

```python
render_template_string(user_input)
```

or:

```python
env.from_string(user_input)
```

These patterns may indicate attacker-controlled template source.

---

# Safe vs Dangerous Python Pattern

Potentially dangerous:

```python
template = request.args.get("template")
return render_template_string(template)
```

Flow:

```text
request.args
    ↓
template
    ↓
render_template_string
```

Safer design:

```python
return render_template(
    "profile.html",
    username=request.args.get("username")
)
```

Flow:

```text
Fixed Template
     +
User Data
     ↓
Render
```

---

# PHP Source Review

For Twig, search for:

```text
Twig\Environment
createTemplate
render
```

Example search:

```bash
rg -n \
'Twig|createTemplate|->render\('
```

Potentially dangerous flow:

```text
User Input
   ↓
createTemplate()
   ↓
render()
```

For Smarty:

```bash
rg -n \
'Smarty|fetch\(|display\('
```

Investigate whether user-controlled strings become template source.

---

# Java Source Review

Search for template engines such as:

```text
FreeMarker
Velocity
Thymeleaf
Pebble
```

Example:

```bash
rg -n \
'FreeMarker|freemarker|Velocity|Thymeleaf|TemplateEngine|Pebble'
```

Interesting APIs may include:

```text
Template
process
evaluate
merge
processTemplate
```

Trace request data into dynamically constructed templates.

---

# Node.js Source Review

Search:

```bash
rg -n \
'ejs|pug|handlebars|mustache|nunjucks|render\(|compile\('
```

Potentially interesting patterns include:

```javascript
ejs.render(userInput)
```

or:

```javascript
Handlebars.compile(userInput)
```

or:

```javascript
nunjucks.renderString(userInput)
```

The important condition is:

```text
User-Controlled Template Source
```

---

# Ruby Source Review

Search:

```bash
rg -n \
'ERB|Liquid|Haml|Slim|render'
```

Potentially dangerous pattern:

```ruby
ERB.new(user_input).result
```

Again:

```text
User Input
 ↓
Template Compilation
```

is the key pattern.

---

# .NET Source Review

Search for:

```text
Razor
RazorLight
Scriban
DotLiquid
Fluid
Parse
Compile
Render
```

Example:

```bash
rg -n \
'Razor|RazorLight|Scriban|DotLiquid|Fluid|Compile|Render'
```

Investigate dynamically compiled user-controlled templates.

---

# Source-to-Sink Example

Consider:

```python
@app.route("/welcome")
def welcome():
    name = request.args.get("name")
    template = "Hello " + name
    return render_template_string(template)
```

The flow is:

```text
SOURCE

request.args.get("name")

        ↓

STRING CONCATENATION

"Hello " + name

        ↓

SINK

render_template_string(template)

        ↓

TEMPLATE EVALUATION
```

This is a classic SSTI pattern.

---

# Secure Equivalent

A safer pattern is:

```python
@app.route("/welcome")
def welcome():
    name = request.args.get("name")
    return render_template("welcome.html", name=name)
```

With:

```html
Hello {{ name }}
```

Here:

```text
Template Source
=
Developer Controlled

User Input
=
Template Data
```

This separation is fundamental.

---

# Search for Dynamic Template Construction

Look for:

```text
String concatenation
String formatting
f-strings
Template literals
Replace operations
Database-stored templates
User-configurable templates
Dynamic compilation
```

Conceptually:

```text
User Input
      ↓
String Construction
      ↓
Template Compile
```

is more interesting than:

```text
User Input
      ↓
Template Variable
```

---

# Database-Stored Templates

Some applications intentionally store templates in a database.

Examples:

```text
Email templates
Invoice templates
Notification templates
CMS pages
```

Ask:

```text
Who can modify the template?

What template syntax is permitted?

Which objects are exposed?

Is the template sandboxed?

Can lower-privileged users control it?
```

In some applications, template editing is intentionally powerful and restricted to trusted administrators.

The security issue depends on the trust boundary.

---

# Trust Boundaries

Not every ability to write template syntax is automatically a vulnerability.

For example:

```text
System Administrator
      ↓
Intentionally Configures Server Template
```

may be expected functionality.

But:

```text
Normal User
      ↓
Controls Template Source
      ↓
Server-Side Evaluation
```

is significantly more concerning.

Determine:

```text
Expected privilege
Actual privilege
Intended capability
Resulting server access
```

---

# Burp Intruder

Intruder can help test a small set of harmless template expressions.

For example:

```text
name=§PAYLOAD§
```

with a focused list:

```text
{{7*7}}
${7*7}
<%= 7*7 %>
```

Compare:

```text
Status
Length
Rendered value
Error
```

Do not use enormous SSTI payload lists against every parameter.

Manual context analysis is more effective.

---

# Automated SSTI Testing

Automation can help identify candidates, but manual confirmation is important.

Potential tools include:

```text
tplmap
SSTImap
Nuclei
Burp Scanner
Custom scripts
```

Automated tools may:

```text
Generate template expressions
Fingerprint engines
Detect evaluation
Test known techniques
```

Results should be manually validated.

---

# SSTImap

SSTImap is a tool designed for detecting and testing Server-Side Template Injection.

Project:

```text
https://github.com/vladko312/SSTImap
```

It supports multiple template engines and can assist with:

```text
Detection
Engine identification
Template evaluation testing
```

Use it only against authorised targets.

Start with detection rather than high-impact exploitation.

---

# tplmap

tplmap is a well-known SSTI testing project.

Project:

```text
https://github.com/epinna/tplmap
```

It has historically been used to automate detection and exploitation of template injection across multiple engines.

Be aware that:

```text
Project age
Engine versions
Framework changes
Python dependencies
```

may affect reliability.

Use it as a reference and supplement rather than relying exclusively on automated output.

---

# Nuclei

Nuclei may identify SSTI patterns through templates.

Project:

```text
https://github.com/projectdiscovery/nuclei
```

A sensible workflow:

```text
Candidate Endpoint
       ↓
Targeted SSTI Check
       ↓
Potential Match
       ↓
Manual Burp Reproduction
       ↓
Engine Fingerprinting
       ↓
Impact Assessment
```

Do not report an SSTI vulnerability solely because a scanner produced a match.

---

# curl

`curl` can reproduce simple SSTI requests outside Burp.

For example:

```bash
curl -i \
  'https://target.example/welcome?name=%7B%7B7*7%7D%7D'
```

The encoded value represents:

```text
{{7*7}}
```

For JSON:

```bash
curl -i \
  -X POST \
  -H 'Content-Type: application/json' \
  --data '{"name":"{{7*7}}"}' \
  https://target.example/api/preview
```

Only use expressions appropriate for the authorised test.

---

# Parameter Discovery

Parameter discovery can uncover hidden template-related functionality.

Useful tools include:

```text
Arjun
ParamSpider
Katana
gau
waybackurls
```

Interesting parameter names include:

```text
template
preview
render
view
layout
theme
format
message
body
subject
content
```

---

# JavaScript Analysis

JavaScript bundles can reveal template functionality.

Search:

```bash
rg -ni \
'template|preview|render|invoice|report|email|notification|document' \
*.js
```

Potential API routes may include:

```text
/api/template
/api/templates
/api/render
/api/preview
/api/report
/api/email/preview
/api/invoice/preview
```

Send interesting endpoints to Burp Repeater.

---

# API Testing

SSTI can occur in APIs even when the API itself returns JSON.

For example:

```http
POST /api/email/preview HTTP/1.1
Content-Type: application/json

{
  "template": "Hello {{name}}"
}
```

The server may return:

```json
{
  "html": "Hello Asif"
}
```

If arbitrary user input controls:

```text
template
```

investigate whether the server interprets expressions.

---

# GraphQL

GraphQL applications can expose template functionality through mutations.

For example:

```text
previewEmail
createTemplate
updateTemplate
renderReport
generateDocument
```

The vulnerability is not caused by GraphQL itself.

GraphQL simply exposes an input path into a server-side template engine.

---

# SSTI in CMS Platforms

CMS functionality frequently contains:

```text
Themes
Templates
Widgets
Custom pages
Email templates
Shortcodes
Dynamic content
```

Determine:

```text
Who can edit templates?
What language is used?
Is execution expected?
Is sandboxing present?
```

Do not report intentionally privileged template editing as SSTI without analysing the trust boundary.

---

# SSTI in SaaS Applications

SaaS platforms often allow customers to customise:

```text
Emails
Invoices
Reports
Notifications
Documents
Landing pages
```

These features may intentionally expose a safe subset of a template language.

The security question becomes:

```text
Can the user escape the intended template sandbox?
```

---

# Template Sandbox Model

A safe SaaS template system might expose only:

```text
customer.name
invoice.number
invoice.total
company.name
```

Conceptually:

```text
User Template
     ↓
Restricted Template Engine
     ↓
Approved Data Model
```

It should not expose:

```text
Application runtime
File system
Environment
Process execution
Internal services
```

---

# Error-Based Detection

Malformed template syntax may produce useful differences.

For example:

```text
Normal Input
    ↓
200 OK

Malformed Template
    ↓
500 / Template Error
```

This can indicate template parsing.

However, errors alone do not prove exploitable SSTI.

Follow up with harmless expression evaluation.

---

# Timing-Based Behaviour

In unusual cases, template evaluation may produce timing differences.

Timing should not be the first SSTI detection technique.

Prefer:

```text
Deterministic Output
```

such as arithmetic evaluation.

Timing introduces uncertainty from:

```text
Network latency
Backend load
Caching
Queues
Rate limiting
```

---

# Blind SSTI

Some template injection occurs in output that the tester cannot directly see.

For example:

```text
User Input
   ↓
Email Template
   ↓
Email Sent Internally
```

or:

```text
User Input
   ↓
Background Report
   ↓
Internal PDF
```

This may be considered blind or second-order SSTI.

Detection becomes more difficult because arithmetic output is not visible.

Where authorised, controlled out-of-band interactions may help establish whether server-side behaviour occurs, but avoid jumping directly to network or command execution solely for detection.

Source review is particularly valuable in these cases.

---

# SSTI in Logs

Logging systems may generate formatted reports or notifications using templates.

Potential flow:

```text
Attacker Input
   ↓
Application Log
   ↓
Reporting System
   ↓
Template Engine
   ↓
Rendered Report
```

This is less common but demonstrates why second-order processing matters.

---

# WAF Behaviour

A Web Application Firewall may block common SSTI syntax.

For example:

```text
{{...}}
${...}
<%=...%>
```

Do not immediately assume:

```text
Blocked = Not Vulnerable
```

Likewise:

```text
Accepted = Vulnerable
```

The objective is to understand the underlying application behaviour, not to bypass controls unnecessarily.

---

# Input Filtering

Applications sometimes attempt to prevent SSTI by blocking characters such as:

```text
{
}
$
%
<
>
```

Character blacklists are generally fragile.

The correct remediation is:

```text
Do not treat attacker-controlled data as template source.
```

---

# Encoding

HTML encoding is not a complete SSTI defence.

For example, SSTI occurs:

```text
Before
```

or during:

```text
Server-Side Template Rendering
```

while HTML encoding primarily protects:

```text
Browser Output
```

These are different security boundaries.

---

# SSTI and Output Encoding

An application may be protected from XSS but still vulnerable to SSTI.

For example:

```text
User Input
   ↓
Template Evaluation
   ↓
HTML Encoding
   ↓
Browser
```

The dangerous server-side evaluation has already occurred before output encoding.

---

# Authentication

Record whether exploitation requires:

```text
Unauthenticated user
Normal authenticated user
Privileged user
Administrator
```

This significantly affects risk.

A normal user controlling server-side template source is typically more concerning than an administrator using an intentionally powerful template editor.

---

# Privilege Boundaries

Ask:

```text
Can a normal user create templates?

Can a tenant administrator create templates?

Can only platform administrators create templates?

Can another user trigger rendering?

Which server privileges does rendering use?
```

SSTI impact depends on both:

```text
Application Privilege
+
Operating-System / Runtime Privilege
```

---

# Multi-Tenant Applications

SSTI in multi-tenant applications can be particularly serious.

Potential impact includes:

```text
Cross-tenant information exposure
Platform configuration exposure
Application secret exposure
Server compromise
```

Do not access another tenant's data merely to prove the vulnerability.

Use controlled test accounts where possible.

---

# SSTI Capability Matrix

Document what was actually demonstrated.

| Capability | Result |
|---|---|
| Input reflected | Yes / No |
| Template evaluation | Yes / No |
| Engine identified | Yes / No |
| Engine version identified | Yes / No |
| Template variables accessible | Yes / No |
| Application objects accessible | Yes / No |
| Sandbox present | Yes / No |
| Sensitive configuration accessible | Yes / No |
| File access demonstrated | Yes / No |
| Network access demonstrated | Yes / No |
| Command execution demonstrated | Yes / No |
| Authentication required | Yes / No |
| Second-order rendering | Yes / No |

This prevents overstating impact.

---

# Evidence Collection

Useful evidence includes:

```text
Affected endpoint
HTTP method
Affected parameter
Authentication requirement
Baseline request
Harmless template expression
Rendered output
Template engine
Template engine version if known
Relevant error
Rendering context
Accessible objects
Required user interaction
Source-to-sink path
Screenshot
```

---

# Strong SSTI Evidence

A simple but strong proof may look like:

```text
Input:

{{7*7}}

Output:

49
```

Combined with:

```text
Server-side response
+
Known server-side template engine
```

this demonstrates expression evaluation.

---

# Avoid Overclaiming

Do not write:

```text
SSTI allows remote code execution
```

unless RCE has actually been demonstrated or can be strongly established from the specific engine and configuration.

Instead:

```text
The application evaluates attacker-controlled template expressions.

Depending on the objects and functionality exposed to the template
environment, SSTI can potentially lead to sensitive information
disclosure and, in some configurations, server-side code execution.
```

This is more accurate.

---

# Example SSTI Finding

```text
Title
Server-Side Template Injection in Report Preview

Affected Endpoint
POST /api/reports/preview

Affected Parameter
title

Authentication Required
Yes

Description
The report preview functionality inserts user-controlled input into
a server-side template before rendering the report.

Testing with a harmless arithmetic template expression demonstrated
that the supplied expression was evaluated by the server rather than
rendered as literal text.

The value:

{{7*7}}

was rendered as:

49

This demonstrates that attacker-controlled input reaches a
server-side template evaluation context.

Impact
An authenticated attacker can evaluate template expressions in the
server-side rendering environment.

The ultimate impact depends on the template engine configuration and
the objects exposed to the template context. In insecure
configurations, Server-Side Template Injection can potentially expose
application data, configuration or dangerous runtime functionality.

Recommendation
Do not construct templates using attacker-controlled strings.

Use fixed developer-controlled templates and pass user-controlled
values strictly as template data.

Where user-editable templates are a business requirement, use a
restricted template environment that exposes only explicitly
approved variables and functions.

Keep the template engine updated and apply sandboxing and least
privilege where supported.
```

---

# Example Second-Order SSTI Finding

```text
Title
Stored Server-Side Template Injection in PDF Reports

Description
User-controlled profile information is stored by the application and
later inserted into a server-side template when an administrative PDF
report is generated.

A harmless template expression stored in the affected profile field
was evaluated when the report was generated.

The vulnerability therefore does not trigger during the original
profile update request and represents a second-order Server-Side
Template Injection condition.

Impact
An authenticated user can cause attacker-controlled template
expressions to be evaluated during server-side report generation.

The practical impact depends on the template engine and the objects
available within the report rendering context.

Recommendation
Treat stored user-controlled values as data rather than template
source.

Do not dynamically concatenate stored values into templates before
rendering.
```

---

# Example Source Code Finding

```text
Title
Server-Side Template Injection Through Dynamic Template Rendering

Source
HTTP parameter: name

Sink
render_template_string()

Description
The application concatenates the user-controlled name parameter into
a string and passes the resulting value to render_template_string().

This causes user-controlled template syntax to be interpreted by the
Jinja template engine.

Data Flow

request.args["name"]
        ↓
String Concatenation
        ↓
render_template_string()
        ↓
Jinja Evaluation

Recommendation
Replace dynamically constructed templates with fixed template files.

Pass the user-controlled value as template data rather than including
it in the template source.
```

---

# Remediation

The primary SSTI defence is architectural:

```text
Never allow untrusted input to become template source.
```

Use:

```text
Developer-Controlled Template
            +
User-Controlled Data
            ↓
Template Engine
```

not:

```text
Developer String
      +
User Input
      ↓
Dynamic Template
      ↓
Template Engine
```

---

# Fixed Templates

Prefer:

```text
Fixed Template
```

with:

```text
Variables
```

For example:

```text
Template:

Hello {{ name }}
```

and:

```text
name = userInput
```

rather than constructing:

```text
Hello USER_INPUT
```

as new template source.

---

# Sandboxing

If users must be able to create templates:

```text
Use sandboxing
```

where supported.

Restrict:

```text
Objects
Methods
Functions
Filters
Tags
Modules
File access
Network access
Runtime access
```

---

# Minimal Template Context

Expose only what the template needs.

Instead of:

```text
Entire Application Object
```

provide:

```text
Customer Name
Invoice Number
Invoice Total
```

A minimal data model significantly reduces impact.

---

# Avoid Runtime Objects

Do not expose unnecessary:

```text
Request objects
Application objects
Framework contexts
Configuration objects
Environment objects
Database handles
HTTP clients
Process APIs
```

to untrusted templates.

---

# Least Privilege

The rendering process should run with minimal privileges.

For example:

```text
Template Renderer
      ↓
Restricted Service Account
      ↓
No Sensitive File Access
      ↓
No Internal Network Access
      ↓
No Process Execution
```

This limits the impact if template restrictions fail.

---

# Isolated Rendering

High-risk user-defined template functionality may benefit from isolation.

Conceptually:

```text
Application
   ↓
Rendering Service
   ↓
Sandbox / Container
```

The renderer should have:

```text
Minimal filesystem access
No secrets
Restricted network
No shell access
Resource limits
Minimal environment variables
```

---

# Keep Engines Updated

Template engines should be kept current.

Security fixes may address:

```text
Sandbox bypasses
Unsafe methods
Parser vulnerabilities
Object traversal
Unexpected runtime access
```

Version-specific security advisories should be reviewed.

---

# Input Validation

Input validation can provide additional defence but should not be the primary SSTI control.

Do not rely solely on blocking:

```text
{{
}}
${
<%
```

because template grammars and contexts differ.

The architectural fix remains:

```text
User input must remain data.
```

---

# Logging

Useful security logging for template functionality may include:

```text
Template ID
User ID
Template modification
Template preview
Template rendering
Rendering errors
Administrative changes
```

Avoid logging sensitive rendered content unnecessarily.

---

# SSTI Testing Checklist

## Discovery

- [ ] Email templates
- [ ] Notification templates
- [ ] PDF generation
- [ ] Report generation
- [ ] Invoice generation
- [ ] Document generation
- [ ] CMS templates
- [ ] Themes
- [ ] Custom pages
- [ ] Message previews
- [ ] Email previews
- [ ] Administrative templates
- [ ] Export functionality
- [ ] Scheduled reports
- [ ] Stored user fields used in templates

## Parameters

- [ ] template
- [ ] content
- [ ] body
- [ ] message
- [ ] text
- [ ] title
- [ ] subject
- [ ] description
- [ ] format
- [ ] view
- [ ] layout
- [ ] theme
- [ ] preview
- [ ] render
- [ ] expression

## Baseline

- [ ] Submit normal input
- [ ] Insert unique marker
- [ ] Confirm rendering location
- [ ] Determine synchronous / asynchronous rendering
- [ ] Determine output format
- [ ] Record baseline response

## Detection

- [ ] Harmless arithmetic expression
- [ ] Literal vs evaluated output
- [ ] Alternative expression syntax
- [ ] Template errors
- [ ] Response differences
- [ ] No destructive operations

## Fingerprinting

- [ ] Identify application language
- [ ] Identify framework
- [ ] Identify likely engine
- [ ] Compare expression behaviour
- [ ] Review errors
- [ ] Confirm engine with harmless behaviour
- [ ] Identify engine version where possible

## Context

- [ ] Plain-text template context
- [ ] Existing expression context
- [ ] HTML context
- [ ] Email context
- [ ] PDF context
- [ ] Report context
- [ ] Stored / second-order context
- [ ] Template preview

## Engine Review

- [ ] Jinja2
- [ ] Twig
- [ ] Smarty
- [ ] FreeMarker
- [ ] Velocity
- [ ] Thymeleaf
- [ ] Pebble
- [ ] Nunjucks
- [ ] Handlebars
- [ ] Mustache
- [ ] Pug
- [ ] EJS
- [ ] ERB
- [ ] Liquid
- [ ] Razor

## Impact

- [ ] Template variables accessible
- [ ] Application objects accessible
- [ ] Configuration accessible
- [ ] Sandbox present
- [ ] Custom helpers available
- [ ] Sensitive information exposure
- [ ] File functionality
- [ ] Network functionality
- [ ] Runtime functionality
- [ ] Minimum necessary proof used

## Burp

- [ ] Proxy
- [ ] HTTP History
- [ ] Repeater
- [ ] Intruder where useful
- [ ] Compare status
- [ ] Compare response length
- [ ] Compare rendered output
- [ ] Review errors

## Source Review

- [ ] Identify template engine
- [ ] Find rendering sinks
- [ ] Find compilation functions
- [ ] Trace request parameters
- [ ] Search dynamic template construction
- [ ] Review database-stored templates
- [ ] Review template context
- [ ] Review sandbox configuration
- [ ] Review custom helpers
- [ ] Review runtime privileges

## Validation

- [ ] Confirm server-side evaluation
- [ ] Exclude client-side template processing
- [ ] Confirm repeatability
- [ ] Determine authentication requirement
- [ ] Determine affected privilege
- [ ] Determine second-order behaviour
- [ ] Do not overstate impact
- [ ] Stop after sufficient evidence

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | Manual SSTI testing |
| Burp Repeater | Expression testing |
| Burp Intruder | Focused syntax testing |
| SSTImap | SSTI detection and engine testing |
| tplmap | SSTI testing reference and automation |
| Nuclei | Targeted automated detection |
| curl | Manual request reproduction |
| Wappalyzer | Technology identification |
| WhatWeb | Technology identification |
| httpx | Technology detection |
| ripgrep | Source-code sink discovery |
| Semgrep | Structured source analysis |
| Arjun | Hidden parameter discovery |
| Katana | Endpoint discovery |

---

# Tool Selection

| Situation | Tool |
|---|---|
| Capture request | Burp Proxy |
| Manual detection | Burp Repeater |
| Small syntax comparison | Burp Intruder |
| Engine detection | Manual tests / SSTImap |
| Automated checks | Nuclei |
| Technology detection | Wappalyzer / WhatWeb / httpx |
| Endpoint discovery | Katana |
| Parameter discovery | Arjun |
| CLI reproduction | curl |
| Source review | ripgrep / Semgrep |

---

# Quick Reference

```text
Interesting Functionality:

Email Templates
PDF Generation
Reports
Invoices
Notifications
CMS Templates
Custom Themes
Message Previews
Document Generation
Administrative Reports
```

```text
Interesting Parameters:

template
content
body
message
title
subject
format
view
layout
theme
preview
render
expression
```

```text
Harmless Detection Concept:

Template Expression
        ↓
Arithmetic
        ↓
Literal or Evaluated?
        ↓
If Evaluated
        ↓
Fingerprint Engine
```

```text
Core SSTI Model:

USER INPUT
    ↓
TEMPLATE SOURCE
    ↓
TEMPLATE ENGINE
    ↓
SERVER-SIDE EVALUATION
```

```text
Secure Model:

FIXED TEMPLATE
      +
USER DATA
      ↓
TEMPLATE ENGINE
      ↓
RENDERED OUTPUT
```

---

# Practical Workflow Summary

```text
                 ┌──────────────────────────┐
                 │ Find Rendered Input      │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Establish Baseline       │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Insert Unique Marker     │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Harmless Expression      │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Expression Evaluated?    │
                 └────────────┬─────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
           ┌────────────────┐   ┌────────────────┐
           │ No             │   │ Yes            │
           │ Reassess       │   │ SSTI Candidate │
           └────────────────┘   └───────┬────────┘
                                        │
                                        ▼
                             ┌──────────────────────┐
                             │ Fingerprint Engine   │
                             └──────────┬───────────┘
                                        │
                                        ▼
                             ┌──────────────────────┐
                             │ Determine Context    │
                             └──────────┬───────────┘
                                        │
                                        ▼
                             ┌──────────────────────┐
                             │ Review Sandbox       │
                             └──────────┬───────────┘
                                        │
                                        ▼
                             ┌──────────────────────┐
                             │ Minimum Safe Impact  │
                             └──────────┬───────────┘
                                        │
                                        ▼
                             ┌──────────────────────┐
                             │ Report               │
                             └──────────────────────┘
```

---

# SSTI Source-to-Sink Model

```text
                 SOURCE
                   │
                   ▼
         ┌────────────────────┐
         │ HTTP Parameter     │
         │ JSON Property      │
         │ Stored User Input  │
         └──────────┬─────────┘
                    │
                    ▼
         ┌────────────────────┐
         │ Application Logic  │
         └──────────┬─────────┘
                    │
                    ▼
         ┌────────────────────┐
         │ String Construction│
         │ Dynamic Template   │
         └──────────┬─────────┘
                    │
                    ▼
         ┌────────────────────┐
         │ Template Engine    │
         │ Compile / Render   │
         └──────────┬─────────┘
                    │
                    ▼
                  SINK
                    │
                    ▼
         ┌────────────────────┐
         │ Server Evaluation  │
         └────────────────────┘
```

---

# References

## PortSwigger Web Security Academy

### Server-Side Template Injection

https://portswigger.net/web-security/server-side-template-injection

This should be one of the primary practical references for SSTI testing.

PortSwigger covers:

```text
Detection
Plain-text context
Code context
Template identification
Exploitation methodology
Sandboxed environments
```

---

## PortSwigger Research

### Server-Side Template Injection

https://portswigger.net/research/server-side-template-injection

James Kettle's research is an important reference for understanding SSTI methodology and template-engine fingerprinting.

The key methodology is:

```text
Detect
 ↓
Identify
 ↓
Exploit
```

For authorised assessments, begin with harmless detection and identification before considering impact testing.

---

## OWASP Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

Useful as a broader reference for server-side application testing methodology.

---

## PayloadsAllTheThings

### Server Side Template Injection

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection

Useful as a reference for:

```text
Template engine identification
Engine-specific syntax
Testing methodology
```

Always identify the engine and context before using engine-specific techniques.

---

## HackTricks

### SSTI

https://book.hacktricks.wiki/en/pentesting-web/ssti-server-side-template-injection/index.html

Useful practical reference for template-engine identification and SSTI behaviour across multiple technologies.

---

## SSTImap

https://github.com/vladko312/SSTImap

Useful for automated SSTI detection and testing across multiple template engines.

---

## tplmap

https://github.com/epinna/tplmap

A well-known SSTI testing project and useful reference for understanding template-engine-specific behaviour.

---

## Jinja Documentation

https://jinja.palletsprojects.com/

Primary documentation for Jinja.

Useful for understanding:

```text
Expressions
Variables
Filters
Template environment
Sandboxing
```

---

## Twig Documentation

https://twig.symfony.com/

Primary documentation for Twig.

---

## Apache FreeMarker

https://freemarker.apache.org/

Primary documentation for FreeMarker.

---

## Apache Velocity

https://velocity.apache.org/

Primary documentation for Apache Velocity.

---

## Thymeleaf

https://www.thymeleaf.org/

Primary documentation for Thymeleaf.

---

## Handlebars

https://handlebarsjs.com/

Primary documentation for Handlebars.

---

## Nunjucks

https://mozilla.github.io/nunjucks/

Primary documentation for Nunjucks.

---

## Liquid

https://shopify.github.io/liquid/

Primary documentation for Liquid.

---

## ProjectDiscovery Nuclei

https://github.com/projectdiscovery/nuclei

Useful for targeted automated SSTI checks followed by manual validation.

---

## Semgrep

https://semgrep.dev/

Useful for locating template rendering sinks and tracing attacker-controlled input through source code.

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
├── Server-Side Request Forgery
├── Server-Side Template Injection
├── Cross-Site Request Forgery
├── XML External Entity Injection
├── Path Traversal
├── File Inclusion
└── File Upload
```

SSTI connects particularly strongly with:

```text
Technology Identification
          ↓
Framework
          ↓
Template Engine
          ↓
SSTI Testing
```

```text
Parameter Discovery
       ↓
template / preview / render
       ↓
SSTI
```

```text
User Input
    ↓
Stored Value
    ↓
Report / Email / PDF
    ↓
Second-Order SSTI
```

```text
SSTI
 ↓
Server Objects
 ↓
Application Information
 ↓
Potential Higher Impact
```

---

# Final Testing Principle

Do not reduce SSTI testing to:

```text
Try {{7*7}}
```

That is only the beginning.

Instead ask:

```text
Where does my input go?
        ↓
Is it rendered?
        ↓
Is rendering client-side or server-side?
        ↓
Does template syntax evaluate?
        ↓
Which syntax is recognised?
        ↓
Which template engine is being used?
        ↓
Which version?
        ↓
What template context am I in?
        ↓
Which variables are intentionally exposed?
        ↓
Are application objects exposed?
        ↓
Is sandboxing enabled?
        ↓
Can the intended sandbox be escaped?
        ↓
What privilege does the renderer have?
        ↓
Is rendering immediate or second-order?
        ↓
What is the minimum evidence required?
```

The complete SSTI chain is:

```text
ATTACKER-CONTROLLED INPUT
          ↓
APPLICATION LOGIC
          ↓
DYNAMIC TEMPLATE CONSTRUCTION
          ↓
TEMPLATE ENGINE
          ↓
SERVER-SIDE EXPRESSION EVALUATION
          ↓
TEMPLATE CONTEXT / OBJECTS
          ↓
POTENTIAL SECURITY IMPACT
```

The most important distinction is:

```text
SAFE

Fixed Template
      +
Untrusted Data
      ↓
Render
```

versus:

```text
DANGEROUS

Untrusted Data
      ↓
Template Source
      ↓
Compile / Render
      ↓
Server-Side Evaluation
```

That is the model to use when assessing Server-Side Template Injection.
