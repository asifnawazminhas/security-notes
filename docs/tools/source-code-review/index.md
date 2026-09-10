---
title: Source Code Review Tools
description: Practical source code review tooling overview for authorised security assessments, including ripgrep, Semgrep, OpenGrep, CodeQL, dependency review, secret scanning, manual source-to-sink analysis, evidence collection, and integration with secure code review methodology.
---

# Source Code Review Tools

Source code review tools help identify potentially security-relevant patterns in application code.

They are useful for:

- locating dangerous functions;
- tracing user-controlled input;
- identifying validation and sanitisation;
- finding authentication and authorisation logic;
- reviewing secrets;
- detecting insecure APIs;
- analysing dependencies;
- finding framework-specific security mistakes;
- identifying candidate sources and sinks;
- scaling manual code review.

No single tool can determine whether an application is secure.

A strong workflow combines:

```text
Repository Understanding
        |
        v
Manual Search
        |
        +-- ripgrep
        |
        v
Pattern-Based Analysis
        |
        +-- Semgrep
        +-- OpenGrep
        |
        v
Deeper Code Analysis
        |
        +-- CodeQL
        |
        v
Manual Source-to-Sink Validation
        |
        v
Security Conclusion
```

!!! warning "Authorised review only"
    Review only repositories, source archives, applications, and codebases that are explicitly authorised. Source code often contains credentials, internal URLs, customer information, cryptographic material, and proprietary implementation details. Treat repositories and analysis output as sensitive assessment data.

---

# Where Source Code Review Tools Fit

Tool-assisted source review usually fits into a wider code-review methodology.

```text
Obtain Authorised Source
        |
        v
Understand Application
        |
        +-- Languages
        +-- Frameworks
        +-- Entry Points
        +-- Dependencies
        +-- Authentication
        |
        v
Identify High-Risk Areas
        |
        v
Tool-Assisted Discovery
        |
        +-- ripgrep
        +-- Semgrep
        +-- OpenGrep
        +-- CodeQL
        |
        v
Manual Data-Flow Analysis
        |
        v
Validate Security Impact
        |
        v
Evidence and Reporting
```

Related methodology:

[Source Code Review](../../source-code-review/index.md)

[Source Code Review Methodology](../../source-code-review/methodology.md)

[Source-to-Sink Analysis](../../source-code-review/source-to-sink-analysis.md)

---

# Tooling Philosophy

The objective is not:

```text
Run static analyser
      |
      v
Export findings
      |
      v
Report everything
```

The objective is:

```text
Security Question
      |
      v
Choose Search / Analysis Method
      |
      v
Identify Candidate
      |
      v
Read Surrounding Code
      |
      v
Trace Data Flow
      |
      v
Understand Controls
      |
      v
Validate Reachability
      |
      v
Determine Impact
```

Tool output should accelerate reasoning.

It should not replace it.

---

# Existing Canonical Tool Pages

Detailed pages for the primary static-analysis tools already exist under the Source Code Review section.

Use those as the canonical references:

[ripgrep](../../source-code-review/static-analysis/ripgrep.md)

[Semgrep](../../source-code-review/static-analysis/semgrep.md)

[OpenGrep](../../source-code-review/static-analysis/opengrep.md)

[CodeQL](../../source-code-review/static-analysis/codeql.md)

[Static Analysis](../../source-code-review/static-analysis/index.md)

This Tools section should connect those capabilities into a broader workflow rather than duplicate them.

---

# Core Tool Categories

| Category | Example Tools |
|---|---|
| Fast textual search | ripgrep |
| Pattern-based static analysis | Semgrep |
| Open-source pattern analysis | OpenGrep |
| Semantic/data-flow analysis | CodeQL |
| Dependency review | language/package tooling, SCA platforms |
| Secret detection | Gitleaks, TruffleHog |
| Manual review | editor, IDE, debugger |
| Runtime validation | application-specific test environment |

Each category answers different questions.

---

# ripgrep

ripgrep is one of the most useful source review tools because it provides extremely fast recursive searching.

It is ideal for locating:

- dangerous APIs;
- authentication checks;
- authorisation checks;
- SQL construction;
- command execution;
- file access;
- deserialisation;
- template rendering;
- redirects;
- HTTP clients;
- secrets;
- security headers;
- framework configuration.

Canonical note:

[ripgrep](../../source-code-review/static-analysis/ripgrep.md)

Official project:

[ripgrep - GitHub](https://github.com/BurntSushi/ripgrep){ target="_blank" rel="noopener noreferrer" }

---

# Why ripgrep Is Important

A source review often begins with questions such as:

```text
Where is user input read?

Where is SQL executed?

Where are operating-system commands launched?

Where are files opened?

Where is access control performed?

Where are redirects generated?
```

ripgrep can answer the first part quickly.

Example workflow:

```text
Security Question
      |
      v
Search Dangerous API
      |
      v
Review Matches
      |
      v
Trace Callers
      |
      v
Trace User Input
```

---

# Search for Sinks

Potential sink categories include:

```text
SQL execution
OS command execution
Filesystem access
Template rendering
Deserialisation
HTTP requests
Redirects
LDAP queries
XPath
XML parsing
Dynamic code execution
```

Do not rely on one universal search string.

Search according to the language and framework being reviewed.

---

# Search for Sources

Potential user-controlled sources include:

```text
HTTP parameters
JSON fields
Headers
Cookies
URL path values
File uploads
Message queues
WebSocket messages
CLI arguments
Environment variables
Database values derived from users
```

The same value can be trusted in one context and untrusted in another.

Trace actual data provenance.

---

# Search for Security Controls

Do not search only for dangerous functions.

Also search for:

```text
Authentication
Authorisation
Validation
Sanitisation
Escaping
Encoding
CSRF protection
Rate limiting
Permission checks
Security middleware
```

Security review is about understanding the entire control path.

---

# Semgrep

Semgrep performs pattern-based static analysis using rules that can match syntactic and semantic code structures.

It is useful for:

- finding known insecure patterns;
- enforcing secure coding rules;
- detecting framework-specific mistakes;
- identifying dangerous API usage;
- running custom organisation-specific checks.

Canonical note:

[Semgrep](../../source-code-review/static-analysis/semgrep.md)

Official documentation:

[Semgrep Documentation](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

---

# Semgrep Mental Model

```text
Source Code
    |
    v
Semgrep Rule
    |
    +-- Pattern
    +-- Context
    +-- Metadata
    |
    v
Candidate Match
```

The rule result means:

```text
This code resembles the condition described by the rule.
```

It does not necessarily mean:

```text
The application is exploitable.
```

---

# Custom Semgrep Rules

Custom rules can be useful when reviewing an organisation-specific application.

Examples include:

- proprietary authentication helpers;
- dangerous internal wrappers;
- insecure logging functions;
- legacy database helpers;
- forbidden cryptographic functions.

A useful workflow is:

```text
Manual Review Finds Pattern
      |
      v
Write Semgrep Rule
      |
      v
Search Entire Repository
      |
      v
Identify Variants
```

This is particularly effective for variant analysis.

---

# OpenGrep

OpenGrep provides a compatible open-source static-analysis workflow for pattern-based source scanning.

It can be useful where:

- open tooling is preferred;
- custom rules are needed;
- repositories are analysed locally;
- automation needs to remain self-hosted.

Canonical note:

[OpenGrep](../../source-code-review/static-analysis/opengrep.md)

Use the exact current OpenGrep documentation and rule syntax for the version being used.

---

# Semgrep vs OpenGrep

These tools occupy a similar role:

```text
Pattern-Based Static Analysis
       |
       +-- Semgrep
       |
       +-- OpenGrep
```

Choose according to:

- environment;
- licensing requirements;
- CI integration;
- existing rule sets;
- organisation tooling;
- desired local workflow.

The review methodology remains the same.

---

# CodeQL

CodeQL provides deeper semantic code analysis using a queryable database representation of source code.

It is particularly useful for:

- data-flow analysis;
- taint tracking;
- complex source-to-sink relationships;
- vulnerability research;
- large repositories;
- repeated variant discovery.

Canonical note:

[CodeQL](../../source-code-review/static-analysis/codeql.md)

Official documentation:

[CodeQL Documentation](https://codeql.github.com/docs/){ target="_blank" rel="noopener noreferrer" }

---

# CodeQL Mental Model

```text
Application Source
       |
       v
CodeQL Database
       |
       v
Query
       |
       +-- Sources
       +-- Sinks
       +-- Sanitizers
       +-- Control Flow
       |
       v
Potential Data Flow
```

This can reveal relationships that simple textual searching cannot.

---

# CodeQL vs Pattern Matching

Pattern matching asks:

```text
Does this code contain a dangerous construct?
```

CodeQL can ask deeper questions such as:

```text
Can data from this HTTP parameter reach this SQL sink without passing
through an appropriate sanitiser?
```

This makes it particularly valuable for complex applications.

---

# Static Analysis Does Not Replace Reading Code

A static-analysis result may miss:

- custom security wrappers;
- dynamic reflection;
- generated code;
- runtime routing;
- framework-specific behaviour;
- business logic;
- configuration-dependent paths.

Therefore:

```text
Static Tool
    |
    v
Candidate
    |
    v
Read Code
```

Always understand the actual implementation.

---

# Source-to-Sink Analysis

Source-to-sink analysis is central to secure code review.

```text
Source
  |
  v
Transformation
  |
  v
Validation?
  |
  v
Sanitisation?
  |
  v
Sink
```

Canonical methodology:

[Source-to-Sink Analysis](../../source-code-review/source-to-sink-analysis.md)

---

# Source Example

A source might be:

```text
HTTP request parameter
```

Then:

```text
request.query["id"]
```

The security question is whether that value can reach a dangerous operation.

---

# Sink Example

A sink might be:

```text
database execution
```

The relevant question is:

```text
Does user-controlled data influence query structure?
```

not merely:

```text
Is SQL used?
```

---

# Sanitizers

A sanitizer or validation step may break an otherwise dangerous data flow.

Examples include:

- parameterised queries;
- strict allowlists;
- canonical path validation;
- framework escaping;
- structured APIs.

Tools may not always model custom controls correctly.

Manual review is required.

---

# Authentication Review

Source review should identify:

```text
Login handlers
Password verification
Session creation
Token validation
MFA logic
Password reset
Account recovery
```

Useful search terms depend on language and framework.

Related web note:

[Authentication Testing](../../web/authentication.md)

---

# Authorisation Review

Authorisation logic deserves especially careful manual review.

Search for:

```text
role
permission
owner
admin
authorize
authorise
policy
access
```

The strongest question is:

> Where is the server-side decision that determines whether this user may perform this action?

Related web note:

[Authorisation Testing](../../web/authorisation.md)

---

# IDOR / BOLA Review

For object-level authorisation:

```text
User-Controlled Object ID
        |
        v
Object Lookup
        |
        v
Ownership / Permission Check?
        |
        v
Response
```

Search for object retrieval followed by missing or inconsistent ownership checks.

Related web note:

[IDOR and BOLA](../../web/idor-bola.md)

---

# SQL Injection Review

Search for:

- raw SQL strings;
- string concatenation;
- string interpolation;
- dynamic query construction;
- unsafe ORM escape hatches.

Then trace user-controlled values.

Related web note:

[SQL Injection](../../web/sql-injection.md)

---

# Command Injection Review

Search for operating-system execution APIs.

Examples vary by language.

The key flow is:

```text
User Input
   |
   v
Command Construction
   |
   v
OS Execution
```

Determine whether:

- arguments are structured;
- shell parsing occurs;
- allowlists exist;
- executable path is controlled.

Related web note:

[OS Command Injection](../../web/command-injection.md)

---

# Path Traversal Review

Search for:

- file opening;
- path joining;
- archive extraction;
- static file serving;
- download handlers.

Trace user-controlled path components.

Related web note:

[Path Traversal](../../web/path-traversal.md)

---

# File Inclusion Review

Identify code that dynamically loads:

- templates;
- modules;
- files;
- includes.

Then determine whether user-controlled values influence the loaded resource.

Related web note:

[File Inclusion](../../web/file-inclusion.md)

---

# File Upload Review

Review:

```text
Filename handling
Storage path
Extension validation
Content validation
MIME type handling
Execution exposure
Access controls
```

Related web note:

[File Upload Security](../../web/file-upload.md)

---

# SSRF Review

Search for HTTP client usage.

Potential areas include:

```text
URL fetch
Webhook
Image retrieval
PDF generation
Import from URL
Callback validation
```

Trace whether user input can control:

- scheme;
- host;
- port;
- path.

Related web note:

[Server Side Request Forgery](../../web/ssrf.md)

---

# XXE Review

Search for XML parser configuration.

The security question is whether external entity resolution or related unsafe XML features are enabled for untrusted input.

Related web note:

[XML External Entity Injection](../../web/xxe.md)

---

# Deserialisation Review

Search for:

- object deserialisation;
- binary formats;
- language-native object serialization;
- unsafe YAML loading;
- polymorphic JSON features.

Related web note:

[Insecure Deserialization](../../web/deserialization.md)

---

# SSTI Review

Search for dynamic template evaluation or user-controlled template construction.

Distinguish:

```text
User input rendered as data
```

from:

```text
User input interpreted as template syntax
```

Related web note:

[Server-Side Template Injection](../../web/ssti.md)

---

# XSS Review

Review how user-controlled content reaches HTML, JavaScript, attributes, URLs, or DOM APIs.

Important questions include:

```text
What context is the data rendered into?

Which escaping function is used?

Is output encoding context appropriate?

Can sanitisation be bypassed?
```

Related web note:

[Cross-Site Scripting](../../web/xss.md)

---

# DOM-Based Review

Client-side code often requires manual source/sink analysis.

Search for sources such as:

```text
location
document.URL
postMessage
storage
```

and sinks such as dynamic HTML or script evaluation APIs.

Related web note:

[DOM-Based Vulnerabilities](../../web/dom-based-vulnerabilities.md)

---

# Open Redirect Review

Search for redirect functionality and determine whether destination values are validated.

Related web note:

[Open Redirect](../../web/open-redirect.md)

---

# CORS Review

Search configuration for:

```text
allowed origins
credentials
wildcards
origin reflection
```

Then compare implementation with runtime behaviour.

Related web note:

[CORS](../../web/cors.md)

---

# CSRF Review

Review:

- CSRF middleware;
- token generation;
- token verification;
- SameSite cookies;
- unsafe method handling.

Related web note:

[Cross-Site Request Forgery](../../web/csrf.md)

---

# JWT Review

Search for:

```text
JWT signing
JWT verification
Algorithm configuration
Key loading
Claim validation
Expiration
Audience
Issuer
```

Related web note:

[JSON Web Token Security](../../web/jwt.md)

---

# OAuth and OIDC Review

Review:

- redirect URI validation;
- state;
- nonce;
- client authentication;
- token validation;
- issuer;
- audience.

Related web note:

[OAuth 2.0 and OpenID Connect Security](../../web/oauth-oidc.md)

---

# Cryptography Review

Search for:

- weak hashes;
- hard-coded keys;
- static IVs;
- ECB mode;
- deprecated algorithms;
- insecure random number generation.

The review should consider why the cryptographic operation exists and what property it is supposed to provide.

---

# Randomness

Security-sensitive randomness may be used for:

```text
Session IDs
Reset tokens
CSRF tokens
API keys
Nonces
```

Search for pseudo-random APIs that are unsuitable for security use.

---

# Hard-Coded Secrets

Source repositories may contain:

- passwords;
- API keys;
- private keys;
- bearer tokens;
- database connection strings.

This is where dedicated secret-scanning tools can help.

---

# Gitleaks

Gitleaks is commonly used to identify potential secrets in Git repositories and files.

Official project:

[Gitleaks - GitHub](https://github.com/gitleaks/gitleaks){ target="_blank" rel="noopener noreferrer" }

It can help identify:

- API keys;
- credentials;
- tokens;
- private material;
- secret patterns.

A match should be validated before reporting.

---

# TruffleHog

TruffleHog is another tool for locating potential secrets in repositories and other supported sources.

Official project:

[TruffleHog - GitHub](https://github.com/trufflesecurity/trufflehog){ target="_blank" rel="noopener noreferrer" }

Secret scanning is useful because repositories may contain sensitive information in:

- current files;
- deleted files;
- historical commits;
- branches.

---

# Secret Match Is Not Always a Live Secret

A scanner result may be:

```text
Example key
Test value
Revoked token
Documentation sample
False positive
```

Therefore:

```text
Secret Scanner Match
      |
      v
Candidate Secret
      |
      v
Context Review
      |
      v
Validation if Necessary and Authorised
```

---

# Git History

Security-sensitive information can remain in Git history even after it is removed from the current branch.

Useful review areas include:

```text
Deleted secrets
Old configuration
Removed endpoints
Legacy code
Previous security checks
```

Git history can provide important context during vulnerability research.

---

# Dependency Analysis

Source review should also inspect dependencies.

Potential package ecosystems include:

```text
npm
pip
Maven
Gradle
NuGet
Composer
Go modules
Rust crates
```

The objective is to understand:

- direct dependencies;
- transitive dependencies;
- version constraints;
- package provenance;
- known security advisories.

---

# Dependency Version Is Not the Whole Story

Avoid:

```text
Package X version Y
       |
       v
CVE exists
       |
       v
Finding
```

Instead:

```text
Package Version
      |
      v
Advisory Applicability
      |
      v
Vulnerable Component Used?
      |
      v
Reachable Code Path?
      |
      v
Actual Risk
```

---

# Dependency Lock Files

Useful files include:

```text
package-lock.json
yarn.lock
poetry.lock
requirements.txt
Pipfile.lock
pom.xml
build.gradle
packages.lock.json
go.mod
go.sum
Cargo.lock
composer.lock
```

These can reveal exact or constrained dependency versions.

---

# Package Manager Audit Tools

Some ecosystems provide built-in security checks.

Examples may include:

```text
npm audit
pip-related vulnerability tooling
NuGet audit functionality
language-specific ecosystem tools
```

Exact capabilities evolve.

Use current official ecosystem documentation when performing dependency scanning.

---

# SCA Platforms

Software Composition Analysis platforms can provide broader dependency intelligence.

Typical functions include:

- dependency inventories;
- CVE mapping;
- license analysis;
- transitive dependency tracking;
- remediation guidance.

Scanner output should still be checked for:

- reachability;
- actual package version;
- false positives;
- environment-specific patching.

---

# Code Ownership and Security Boundaries

Repository structure can reveal security boundaries.

Examples:

```text
frontend/
backend/
auth/
admin/
api/
worker/
shared/
```

Understanding these boundaries helps prioritise review.

---

# Entry Points

Identify how requests enter the application.

Potential entry points include:

```text
HTTP routes
API controllers
GraphQL resolvers
Message handlers
Background jobs
CLI commands
WebSocket handlers
File processors
```

Tooling becomes more effective after entry points are mapped.

---

# Framework Routing

Search for route definitions.

Examples conceptually include:

```text
GET /users/:id
POST /login
DELETE /admin/user/:id
```

Map routes to:

- controller;
- middleware;
- service;
- data-access layer.

---

# Middleware

Middleware often implements important security controls.

Examples include:

- authentication;
- authorisation;
- CSRF;
- rate limiting;
- security headers;
- input validation.

A route may appear insecure until its middleware chain is understood.

---

# Configuration Review

Security behaviour often depends on configuration rather than application logic.

Review:

```text
Environment variables
Framework settings
Deployment configuration
Container configuration
Reverse proxy configuration
Feature flags
```

Static code alone may not reveal the effective runtime setting.

---

# Environment-Specific Security

An application may behave differently in:

```text
Development
Testing
Staging
Production
```

Search for environment branches.

Example concept:

```text
if development:
    enable_debug()
```

Then determine whether production deployment could enter that branch.

---

# Debug Configuration

Search for:

```text
debug
development
trace
verbose errors
stack traces
```

Do not report development settings that are unreachable in production without supporting evidence.

---

# Authentication Bypass Patterns

Review for logic such as:

```text
if internal:
    skip_auth
```

or:

```text
if debug:
    allow_all
```

The key question is whether an attacker can influence or reach that branch.

---

# Feature Flags

Feature flags can expose dormant security-sensitive paths.

Search for:

```text
feature flag
experimental
legacy
beta
disabled
internal
```

A disabled vulnerable feature may still matter if it can be enabled through user-controlled state or configuration.

---

# Business Logic

Static analysis is often weakest at business logic.

Examples include:

- order sequencing;
- approval processes;
- payment flows;
- account linking;
- role transitions;
- entitlement checks.

Manual review is essential.

Related web note:

[Business Logic Vulnerabilities](../../web/business-logic.md)

---

# Race Conditions

Source review can help identify non-atomic workflows.

Look for patterns such as:

```text
Check balance
      |
      v
Perform operation
      |
      v
Update balance
```

without appropriate transactional protection.

Related web note:

[Race Conditions](../../web/race-conditions.md)

---

# Concurrency Controls

Search for:

- transactions;
- locks;
- optimistic concurrency;
- unique constraints;
- idempotency keys.

The absence of an application-level lock is not automatically vulnerable if the database enforces the invariant.

---

# Source Review and Runtime Validation

Static findings often need runtime validation.

```text
Source Candidate
      |
      v
Build Test Hypothesis
      |
      v
Run Application
      |
      v
Send Controlled Input
      |
      v
Observe Behaviour
```

This is especially useful where actual configuration or framework behaviour is uncertain.

---

# White-Box Advantage

Source access allows the tester to understand:

```text
Input path
Control decisions
Dangerous operations
Error handling
Hidden routes
Configuration
```

This can make dynamic testing substantially more focused.

---

# Source Review and Burp Suite

A strong workflow is:

```text
Source Code
    |
    v
Interesting Route
    |
    v
Run Application
    |
    v
Burp Suite
    |
    v
Runtime Validation
```

Related tool:

[Burp Suite](../web-testing/burp-suite.md)

---

# Source Review and Web Methodology

Source findings should connect to the relevant vulnerability methodology.

For example:

```text
Potential SQL flow
      |
      v
SQL Injection methodology

Potential SSRF flow
      |
      v
SSRF methodology
```

This keeps static review tied to actual security behaviour.

---

# Variant Analysis

Once one vulnerability is found, search for similar implementations.

Example:

```text
Confirmed Vulnerable Function
        |
        v
Identify Structural Pattern
        |
        v
ripgrep / Semgrep / CodeQL
        |
        v
Find Similar Call Sites
```

This is one of the highest-value uses of static analysis.

---

# Finding Dangerous Wrapper Functions

Applications often wrap dangerous APIs.

Example:

```text
executeQuery()
    |
    v
database.query()
```

Searching only for:

```text
database.query
```

may miss most application-level usage.

Find wrappers and then search for their callers.

---

# Wrapper Analysis

A useful process is:

```text
Dangerous Sink
      |
      v
Identify Wrapper
      |
      v
Search Wrapper Calls
      |
      v
Trace Sources
```

This reduces duplicate analysis.

---

# Custom Security Functions

Applications may also wrap security controls.

Examples:

```text
requireAdmin()
validateTenant()
safeQuery()
sanitizeHtml()
```

Do not assume a function is safe because of its name.

Read the implementation.

---

# Naming Is Not Security

This function name:

```text
sanitizeInput()
```

does not prove that the output is safe for:

- SQL;
- HTML;
- shell;
- filesystem;
- LDAP.

Security controls are context specific.

---

# IDEs and Editors

A capable IDE can be one of the most useful source review tools.

Useful features include:

- find references;
- go to definition;
- call hierarchy;
- type information;
- data-flow assistance;
- Git history;
- debugger integration.

Examples include:

```text
Visual Studio Code
Visual Studio
JetBrains IDEs
language-specific environments
```

The exact editor is less important than navigation quality.

---

# Language Servers

Language servers can help understand:

```text
Definitions
References
Types
Callers
Implementations
```

This is particularly useful in large codebases where textual search alone creates too much noise.

---

# Call Hierarchy

Call hierarchy can reveal:

```text
HTTP Controller
      |
      v
Service Layer
      |
      v
Repository
      |
      v
Database Sink
```

This is a natural complement to source-to-sink analysis.

---

# Debuggers

Debuggers are useful when static analysis cannot explain runtime behaviour.

They can help inspect:

- variable values;
- actual execution paths;
- validation branches;
- object types;
- function calls.

Use a controlled test environment rather than attaching invasive debugging to production unless explicitly authorised.

---

# Generated Code

Some repositories contain generated code.

Examples include:

- ORM classes;
- API clients;
- protobuf;
- frontend bundles.

Generated code may create large amounts of scanner noise.

Determine whether it should be:

```text
included
```

or:

```text
excluded
```

for the specific analysis.

---

# Third-Party Code

Vendored dependencies can also produce scanner noise.

Examples:

```text
node_modules
vendor
third_party
packages
```

Do not report vulnerabilities in bundled third-party code without confirming:

- it is actually shipped;
- it is used;
- the vulnerable code is reachable;
- remediation ownership.

---

# Test Code

Test directories frequently contain:

- hard-coded credentials;
- deliberately insecure examples;
- mocks;
- fake secrets.

Distinguish:

```text
Production Reachable Code
```

from:

```text
Test Fixture
```

before reporting.

---

# Dead Code

A dangerous function may exist but never be called.

The security question is reachability.

```text
Dangerous Code
      |
      v
Reachable?
      |
      +-- No -> lower/no practical impact
      |
      +-- Yes -> investigate
```

---

# Build-Time vs Runtime Code

Some source executes only:

- during build;
- during tests;
- in developer tooling.

Do not treat all code as production runtime code.

Understand deployment.

---

# Multi-Repository Applications

Modern applications may span multiple repositories.

Example:

```text
Frontend Repo
Backend Repo
Identity Repo
Infrastructure Repo
Shared Libraries
```

A source-to-sink path may cross repository boundaries.

Document which repositories were reviewed.

---

# Infrastructure as Code

Security-relevant source may also include:

```text
Terraform
CloudFormation
Kubernetes YAML
Dockerfiles
CI/CD workflows
Ansible
Helm
```

These can influence application security through:

- network exposure;
- IAM;
- secrets;
- runtime privileges;
- container configuration.

Do not limit source review to application code.

---

# CI/CD Configuration

Review pipeline definitions for:

- secrets handling;
- untrusted pull request execution;
- privileged runners;
- artifact integrity;
- deployment credentials.

The repository itself may reveal significant supply-chain risks.

---

# Dockerfiles

Review:

```text
Base image
User
COPY
RUN
Secrets
Exposed ports
Package installation
```

A container that runs as root is not automatically vulnerable, but it may increase impact when another application flaw exists.

---

# Kubernetes Manifests

Review:

- service accounts;
- host mounts;
- privileged containers;
- capabilities;
- secrets;
- network exposure.

These may affect the runtime security boundary.

---

# Secret Scanning Workflow

A useful process is:

```text
Repository
   |
   +--> Gitleaks
   |
   +--> TruffleHog
   |
   v
Candidate Secrets
   |
   v
Manual Context Review
   |
   v
Validate Only If Necessary
```

Never expose discovered secrets unnecessarily.

---

# Static Analysis Workflow

A practical workflow is:

```text
1. Identify languages and frameworks
      |
      v
2. Map entry points
      |
      v
3. Identify high-risk sinks
      |
      v
4. Search manually with ripgrep
      |
      v
5. Run Semgrep/OpenGrep
      |
      v
6. Use CodeQL where deeper flow analysis helps
      |
      v
7. Review findings manually
      |
      v
8. Trace source-to-sink
      |
      v
9. Validate runtime behaviour where required
      |
      v
10. Perform variant analysis
```

---

# Manual Review Before Broad Scanning

Running a scanner immediately can produce hundreds of findings without context.

A better approach is often:

```text
Understand Repository
      |
      v
Identify Framework
      |
      v
Understand Application Architecture
      |
      v
Then Scan
```

This makes scanner results easier to triage.

---

# Prioritisation

Higher-priority findings often involve:

- unauthenticated entry points;
- privileged functionality;
- central authentication;
- central authorisation;
- dangerous sinks;
- shared utility functions;
- public APIs;
- file processing;
- server-side network access;
- template engines;
- deserialisation.

---

# Triage Questions

For each static-analysis result ask:

```text
Is the code reachable?

Is the input attacker controlled?

Does validation occur?

Is sanitisation context appropriate?

Does the dangerous sink actually execute?

What privilege does it execute with?

Can the behaviour be demonstrated?
```

---

# False Positives

Static-analysis tools can produce false positives because of:

- sanitisation not modelled;
- unreachable code;
- test code;
- generated code;
- framework guarantees;
- safe wrapper functions;
- trusted-only sources.

Manual code review resolves these cases.

---

# False Negatives

Static-analysis tools may miss vulnerabilities because of:

- reflection;
- dynamic dispatch;
- custom frameworks;
- generated runtime behaviour;
- custom wrappers;
- complex cross-service data flow;
- business logic;
- configuration.

A clean scan does not prove the codebase is secure.

---

# Tool Confidence Model

A useful model is:

| Stage | Meaning |
|---|---|
| Match | Tool identified a pattern |
| Candidate | Pattern appears security relevant |
| Reachable | Code can execute in target environment |
| Controllable | Attacker can influence relevant data |
| Validated | Security behaviour confirmed |
| Confirmed | Impact sufficiently demonstrated |

---

# Evidence Collection

For important findings, retain:

```text
Repository:
Commit:
Branch:
File:
Function:
Line range:
Language:
Framework:
Tool:
Tool version:
Rule/query:
Source:
Sink:
Validation:
Security control:
Impact:
```

This improves reproducibility.

---

# Commit Hash

Record the exact revision reviewed.

Example:

```bash
git rev-parse HEAD
```

A finding tied only to:

```text
main branch
```

may become difficult to reproduce after new commits.

---

# Git Status

Confirm whether the working tree contains local changes.

```bash
git status
```

This helps avoid reviewing code that differs from the official assessment revision without documenting it.

---

# File and Line References

A report should include enough code location information for developers to find the issue.

Example:

```text
File:
src/controllers/download.py

Function:
download_file()

Lines:
125-147
```

Line numbers may change between commits, so include the commit identifier.

---

# Evidence Snippets

Include the minimum source necessary to explain the flaw.

Avoid copying large proprietary code sections into reports.

A good evidence snippet shows:

```text
Source
Validation
Sink
```

without unnecessary surrounding implementation.

---

# Reporting

Avoid:

```text
Semgrep found SQL injection.
```

Prefer:

```text
The `search` request parameter was concatenated into a SQL query before
execution. The affected code did not use parameter binding or another
control that separated attacker-controlled data from query structure.
```

The tool may have identified the candidate.

The code behaviour is the finding.

---

# Reporting a Negative Result

Example:

```text
Semgrep flagged a dynamic SQL construction pattern. Manual review showed
that the user-supplied value was passed through a strict allowlist and
was not able to influence SQL syntax. The candidate was therefore not
confirmed as SQL injection.
```

Negative triage is an important part of static-analysis quality.

---

# Reporting Secrets

Avoid exposing the complete secret.

Instead:

```text
A hard-coded production API credential was identified in the repository.
The value has been redacted from this report.
```

Provide:

- file;
- commit;
- secret type;
- affected service;
- remediation.

---

# Remediation Principles

Source review should recommend fixing the underlying trust boundary.

Examples include:

- parameterised queries;
- server-side authorisation;
- strict input validation;
- output encoding;
- safe filesystem APIs;
- safe process APIs;
- trusted URL allowlists;
- secure parser settings;
- secret-management systems.

Avoid generic recommendations such as:

```text
Sanitise input
```

without specifying the required security property.

---

# Retesting

Retest should confirm:

```text
Vulnerable Data Flow Removed
```

not merely:

```text
Scanner No Longer Alerts
```

For example:

```text
Before:
user input -> SQL string concatenation

After:
user input -> bound query parameter
```

Then run:

- manual source review;
- relevant static rule;
- runtime regression test.

---

# Custom Rules for Regression Testing

Once a flaw is fixed, a custom Semgrep/OpenGrep or CodeQL rule may help prevent similar code from returning.

Workflow:

```text
Confirmed Vulnerability
       |
       v
Identify Structural Pattern
       |
       v
Create Rule
       |
       v
Scan Repository
       |
       v
Add CI Check
```

This converts a one-time finding into a repeatable security control.

---

# Source Review and Variant Analysis

A vulnerability rarely exists in isolation when developers reuse patterns.

After confirming one issue:

```text
Find vulnerable helper
      |
      v
Search all call sites
      |
      v
Search similar helpers
      |
      v
Review sibling implementations
```

Canonical vulnerability research note:

[Vulnerability Research](../../vulnerability-research/index.md)

[Variant Analysis](../../vulnerability-research/variant-analysis.md)

---

# Source Review and Vulnerability Research

CodeQL, Semgrep, ripgrep, and manual analysis are also useful for vulnerability research.

A research workflow might be:

```text
Known Bug
   |
   v
Root Cause
   |
   v
Code Pattern
   |
   v
Repository Search
   |
   v
Variants
```

Tool choice depends on how complex the pattern is.

---

# LLM-Assisted Source Review

LLMs can help with:

- explaining unfamiliar code;
- generating search ideas;
- summarising functions;
- suggesting candidate sources/sinks;
- drafting static-analysis rules;
- comparing similar implementations.

However:

```text
LLM Suggestion
      |
      v
Security Hypothesis
      |
      v
Independent Validation
      |
      v
Evidence
      |
      v
Conclusion
```

Never treat:

```text
LLM says vulnerable
```

as a finding.

---

# LLM Limitations

Potential limitations include:

- hallucinated APIs;
- missed control flow;
- incorrect framework assumptions;
- incomplete repository context;
- insecure suggestions;
- inability to know effective runtime configuration.

Use AI as an analysis accelerator.

Do not outsource the security conclusion.

---

# Sensitive Code and AI

Do not send proprietary source code or secrets to external AI services unless organisational policy explicitly permits it.

Consider:

- data classification;
- contractual restrictions;
- source-code ownership;
- customer confidentiality;
- model/provider retention policies.

Local or organisation-approved tooling may be required.

---

# Practical Source Review Workflow

A mature workflow can be:

```text
1. Confirm authorised repository
      |
      v
2. Record commit / branch
      |
      v
3. Identify languages and frameworks
      |
      v
4. Map architecture and entry points
      |
      v
5. Identify security-sensitive components
      |
      v
6. Search with ripgrep
      |
      v
7. Run Semgrep or OpenGrep
      |
      v
8. Run CodeQL where deeper analysis helps
      |
      v
9. Scan secrets and dependencies
      |
      v
10. Manually review candidates
      |
      v
11. Trace source-to-sink
      |
      v
12. Validate runtime behaviour where needed
      |
      v
13. Perform variant analysis
      |
      v
14. Capture evidence
      |
      v
15. Report underlying code weakness
```

---

# Tool Selection Guide

## Need Very Fast Search

Use:

```text
ripgrep
```

---

## Need Pattern-Based Security Rules

Use:

```text
Semgrep
```

or:

```text
OpenGrep
```

---

## Need Complex Data-Flow Analysis

Use:

```text
CodeQL
```

---

## Need Secret Discovery

Use:

```text
Gitleaks
TruffleHog
```

---

## Need Dependency Analysis

Use:

```text
Package manager / SCA tooling
```

---

## Need to Understand an Individual Code Path

Use:

```text
IDE
Manual tracing
Debugger where useful
```

---

# Source Code Review Tool Checklist

## Preparation

- [ ] Repository explicitly authorised.
- [ ] Branch recorded.
- [ ] Commit hash recorded.
- [ ] Working-tree changes checked.
- [ ] Languages identified.
- [ ] Frameworks identified.
- [ ] Build/deployment context understood.
- [ ] Source handled as sensitive information.

## Repository Understanding

- [ ] Entry points mapped.
- [ ] Authentication components identified.
- [ ] Authorisation components identified.
- [ ] Database layer identified.
- [ ] Filesystem operations identified.
- [ ] HTTP client usage identified.
- [ ] Template system identified.
- [ ] Background workers identified.
- [ ] APIs identified.
- [ ] Configuration identified.

## ripgrep

- [ ] Dangerous sinks searched.
- [ ] User-input sources searched.
- [ ] Security controls searched.
- [ ] Wrapper functions identified.
- [ ] Call sites reviewed.
- [ ] Search results manually triaged.

## Semgrep / OpenGrep

- [ ] Appropriate rules selected.
- [ ] Custom rules used where beneficial.
- [ ] Generated/vendor directories considered.
- [ ] Findings manually reviewed.
- [ ] Sanitisation and framework context checked.
- [ ] Tool results not reported directly.

## CodeQL

- [ ] Database built from correct source revision.
- [ ] Relevant queries selected.
- [ ] Data-flow assumptions understood.
- [ ] Sources and sinks reviewed.
- [ ] Custom sanitizers considered.
- [ ] Findings manually validated.

## Secrets

- [ ] Current files scanned.
- [ ] Git history considered.
- [ ] Candidate secrets handled securely.
- [ ] False positives reviewed.
- [ ] Secret values redacted from reports.
- [ ] Validation performed only when necessary and authorised.

## Dependencies

- [ ] Lock files identified.
- [ ] Direct dependencies reviewed.
- [ ] Transitive dependencies considered.
- [ ] Advisories checked.
- [ ] Actual vulnerable code path considered.
- [ ] Old-looking versions not automatically reported.

## Manual Validation

- [ ] Source identified.
- [ ] Sink identified.
- [ ] Complete data flow traced.
- [ ] Validation reviewed.
- [ ] Sanitisation reviewed.
- [ ] Reachability established.
- [ ] Runtime configuration considered.
- [ ] Impact established.

## Evidence

- [ ] Repository recorded.
- [ ] Commit recorded.
- [ ] File recorded.
- [ ] Function recorded.
- [ ] Line range recorded.
- [ ] Relevant code snippet retained.
- [ ] Tool/rule recorded.
- [ ] Sensitive data redacted.
- [ ] Finding describes underlying security condition.

## Retest

- [ ] Root cause reviewed after fix.
- [ ] Source-to-sink path re-evaluated.
- [ ] Relevant scanner/rule rerun.
- [ ] Runtime regression performed where useful.
- [ ] Variant locations reviewed.

---

# Related Canonical Tool Notes

[Static Analysis](../../source-code-review/static-analysis/index.md)

[ripgrep](../../source-code-review/static-analysis/ripgrep.md)

[Semgrep](../../source-code-review/static-analysis/semgrep.md)

[OpenGrep](../../source-code-review/static-analysis/opengrep.md)

[CodeQL](../../source-code-review/static-analysis/codeql.md)

---

# Related Tool Sections

[Security Tools](../index.md)

[Web Application Testing Tools](../web-testing/index.md)

[Burp Suite](../web-testing/burp-suite.md)

[Vulnerability Research Tools](../vulnerability-research/index.md)

[AI-Assisted Security Tools](../ai/index.md)

---

# Related Source Code Review Notes

[Source Code Review](../../source-code-review/index.md)

[Source Code Review Methodology](../../source-code-review/methodology.md)

[Source-to-Sink Analysis](../../source-code-review/source-to-sink-analysis.md)

Use the Source Code Review section as the canonical home for language-specific, framework-specific, and static-analysis methodology.

---

# Related Web Security Notes

[Authentication Testing](../../web/authentication.md)

[Authorisation Testing](../../web/authorisation.md)

[IDOR and BOLA](../../web/idor-bola.md)

[SQL Injection](../../web/sql-injection.md)

[OS Command Injection](../../web/command-injection.md)

[Path Traversal](../../web/path-traversal.md)

[File Inclusion](../../web/file-inclusion.md)

[File Upload Security](../../web/file-upload.md)

[Server Side Request Forgery](../../web/ssrf.md)

[XML External Entity Injection](../../web/xxe.md)

[Insecure Deserialization](../../web/deserialization.md)

[Server-Side Template Injection](../../web/ssti.md)

[Cross-Site Scripting](../../web/xss.md)

[DOM-Based Vulnerabilities](../../web/dom-based-vulnerabilities.md)

[Open Redirect](../../web/open-redirect.md)

[CORS](../../web/cors.md)

[Cross-Site Request Forgery](../../web/csrf.md)

[JSON Web Token Security](../../web/jwt.md)

[OAuth 2.0 and OpenID Connect Security](../../web/oauth-oidc.md)

[Business Logic Vulnerabilities](../../web/business-logic.md)

[Race Conditions](../../web/race-conditions.md)

---

# External References

## ripgrep

[ripgrep - GitHub](https://github.com/BurntSushi/ripgrep){ target="_blank" rel="noopener noreferrer" }

## Semgrep

[Semgrep Documentation](https://semgrep.dev/docs/){ target="_blank" rel="noopener noreferrer" }

## CodeQL

[CodeQL Documentation](https://codeql.github.com/docs/){ target="_blank" rel="noopener noreferrer" }

[GitHub CodeQL](https://github.com/github/codeql){ target="_blank" rel="noopener noreferrer" }

## Secret Scanning

[Gitleaks - GitHub](https://github.com/gitleaks/gitleaks){ target="_blank" rel="noopener noreferrer" }

[TruffleHog - GitHub](https://github.com/trufflesecurity/trufflehog){ target="_blank" rel="noopener noreferrer" }

## Secure Code Review References

[OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use source code review tooling like this:

```text
Run Semgrep
Run CodeQL
Run Secret Scanner
      |
      v
Export Alerts
      |
      v
Report Everything
```

Use it like this:

```text
Understand Repository
        |
        v
Map Entry Points and Trust Boundaries
        |
        v
Identify Security Questions
        |
        v
Choose Appropriate Tool
        |
        +-- ripgrep
        +-- Semgrep
        +-- OpenGrep
        +-- CodeQL
        +-- secret scanner
        |
        v
Identify Candidate Code
        |
        v
Read Surrounding Implementation
        |
        v
Trace Source to Sink
        |
        v
Understand Validation and Sanitisation
        |
        v
Confirm Reachability
        |
        v
Validate Runtime Behaviour Where Needed
        |
        v
Perform Variant Analysis
        |
        v
Capture Evidence
        |
        v
Report the Underlying Code Weakness
```

Source code review tools are most valuable when they reduce the amount of code that must be searched manually and reveal relationships that deserve deeper investigation.

The tools identify patterns.

The tester determines whether those patterns form a real security vulnerability.
