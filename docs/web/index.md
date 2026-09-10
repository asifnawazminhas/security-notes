---
title: Web Application Security
description: Practical web application security testing notes covering reconnaissance, authentication, authorisation, session management, injection, client-side and server-side vulnerabilities, APIs, business logic, tooling, validation, evidence, remediation, and retesting.
---

# Web Application Security

Web application security testing focuses on identifying weaknesses in applications, APIs, authentication mechanisms, access controls, client-side behaviour, server-side processing and the infrastructure supporting them.

This section combines:

- methodology;
- reconnaissance;
- manual testing;
- tooling;
- vulnerability-specific techniques;
- evidence collection;
- interpretation;
- remediation;
- retesting.

The objective is not simply to identify unusual behaviour.

It is to determine whether a meaningful security boundary can be crossed and whether the available evidence supports a defensible finding.

!!! warning "Authorised Security Testing"
    The techniques documented in these notes are intended for authorised security assessments, lab environments, security research and responsible vulnerability disclosure. Confirm scope, testing restrictions, rate limits, account requirements and operational risk before testing.

---

## Start Here

<div class="grid cards" markdown>

-   :material-map-search-outline:{ .lg .middle } **Reconnaissance**

    ---

    Map the exposed application surface, technologies, endpoints, parameters, JavaScript, APIs and supporting infrastructure.

    [:octicons-arrow-right-24: Web Reconnaissance](reconnaissance/index.md)

-   :material-account-key:{ .lg .middle } **Authentication and Access Control**

    ---

    Test login flows, sessions, MFA, password reset, authorisation, IDOR/BOLA, role boundaries and protected functionality.

    [:octicons-arrow-right-24: Authentication](authentication.md)

-   :material-code-braces:{ .lg .middle } **Injection**

    ---

    Investigate SQL, NoSQL, LDAP, command, template and XML parser injection paths.

    [:octicons-arrow-right-24: SQL Injection](sql-injection.md)

-   :material-server-security:{ .lg .middle } **Server-Side Security**

    ---

    Test SSRF, path traversal, file inclusion, file upload, deserialization, input validation and backend processing behaviour.

    [:octicons-arrow-right-24: SSRF](ssrf.md)

-   :material-monitor-dashboard:{ .lg .middle } **Client-Side Security**

    ---

    Investigate XSS, DOM-based vulnerabilities, CSRF, CORS, clickjacking, browser storage, redirects and prototype pollution.

    [:octicons-arrow-right-24: XSS](xss.md)

-   :material-api:{ .lg .middle } **API Security**

    ---

    Test REST APIs, GraphQL, gRPC, WebSockets, mass assignment, authentication and object-level authorisation.

    [:octicons-arrow-right-24: API Security](api-security.md)

-   :material-briefcase-search-outline:{ .lg .middle } **Business Logic**

    ---

    Assess workflows, trust boundaries, race conditions, rate limits, multi-step processes and application-specific abuse cases.

    [:octicons-arrow-right-24: Business Logic](business-logic.md)

-   :material-tools:{ .lg .middle } **Web Testing Tools**

    ---

    Use Burp Suite, ffuf, Katana, Nuclei, sqlmap, Interactsh, WhatWeb, Wappalyzer and httpx as part of structured testing workflows.

    [:octicons-arrow-right-24: Web Testing Tools](../tools/web-testing/index.md)

</div>

---

# Web Application Testing Methodology

A web application assessment should follow a structured methodology rather than testing vulnerabilities at random.

A useful lifecycle is:

```text
Scope and Rules
      |
      v
Reconnaissance
      |
      v
Technology Identification
      |
      v
Attack Surface Mapping
      |
      v
Content and Endpoint Discovery
      |
      v
Parameter Discovery
      |
      v
Authentication Testing
      |
      v
Authorisation Testing
      |
      v
Session Management
      |
      v
Input Validation
      |
      v
Injection Testing
      |
      v
Server-Side Testing
      |
      v
Client-Side Testing
      |
      v
API Testing
      |
      v
Business Logic Testing
      |
      v
Manual Validation
      |
      v
Impact Assessment
      |
      v
Evidence Collection
      |
      v
Reporting
      |
      v
Remediation
      |
      v
Retest
```

The methodology should remain flexible.

Different applications may require different emphasis depending on:

- architecture;
- authentication model;
- API design;
- application state;
- technology;
- role structure;
- business logic;
- deployment model.

[View the Web Application Testing Methodology](methodology.md)

[Open the Web Application Pentesting Checklist](checklist.md)

---

# Reconnaissance and Attack Surface

Reconnaissance focuses on understanding what is exposed before deeper testing begins.

Typical activities include:

- subdomain enumeration;
- DNS enumeration;
- HTTP probing;
- technology identification;
- content discovery;
- parameter discovery;
- JavaScript analysis;
- API discovery;
- virtual host discovery;
- historical URL analysis;
- default error-page fingerprinting.

A useful flow is:

```text
Domain / Application
      |
      v
Subdomains and Hosts
      |
      v
HTTP Services
      |
      v
Technology Indicators
      |
      v
Content and Endpoints
      |
      v
Parameters
      |
      v
Prioritised Attack Surface
```

Related notes:

[Web Reconnaissance](reconnaissance/index.md)

[Attack Surface Analysis](attack-surface-analysis.md)

[Subdomain Enumeration](reconnaissance/subdomain-enumeration.md)

[Technology Identification](reconnaissance/technology-identification.md)

[Content Discovery](reconnaissance/content-discovery.md)

[Parameter Discovery](reconnaissance/parameter-discovery.md)

[JavaScript Analysis](reconnaissance/javascript-analysis.md)

---

# Reconnaissance Tooling

Useful tools include:

```text
WhatWeb
Wappalyzer
httpx
Katana
ffuf
```

A practical sequence can be:

```text
Assets
  |
  v
httpx
  |
  v
WhatWeb / Wappalyzer
  |
  v
Katana
  |
  v
ffuf
  |
  v
Manual Review
```

Detailed tool notes:

[Web Enumeration Tools](../tools/web-enumeration/index.md)

[WhatWeb](../tools/web-enumeration/whatweb.md)

[Wappalyzer](../tools/web-enumeration/wappalyzer.md)

[httpx](../tools/web-enumeration/httpx.md)

[Katana](../tools/web-testing/katana.md)

[ffuf](../tools/web-testing/ffuf.md)

---

# Authentication

Authentication testing focuses on how the application verifies identity.

Areas include:

- login functionality;
- username enumeration;
- password policy;
- account lockout;
- password reset;
- MFA;
- remember-me functionality;
- authentication state;
- session creation;
- authentication bypass;
- SSO;
- OAuth;
- SAML.

Authentication should be tested as a complete workflow rather than only as a login form.

A useful model is:

```text
Identity Claim
      |
      v
Authentication Mechanism
      |
      v
Session / Token
      |
      v
Authenticated State
```

Related notes:

[Authentication](authentication.md)

[Password Reset](password-reset.md)

[Multi-Factor Authentication](mfa.md)

[SAML Security](saml.md)

[OAuth 2.0 and OpenID Connect](oauth-oidc.md)

---

# Authorisation

Authorisation determines what an authenticated identity is allowed to access or perform.

Important areas include:

- horizontal privilege escalation;
- vertical privilege escalation;
- IDOR;
- BOLA;
- missing function-level access control;
- role manipulation;
- forced browsing;
- administrative functions;
- API access control;
- multi-tenant isolation.

A useful model is:

```text
Authenticated Identity
      |
      v
Requested Resource / Function
      |
      v
Authorisation Decision
      |
      +-- Allow
      |
      +-- Deny
```

Testing should use multiple controlled roles where scope permits.

Related notes:

[Authorisation](authorisation.md)

[IDOR / BOLA](idor-bola.md)

---

# Session Management

Session management controls how authenticated state is maintained.

Important areas include:

- cookie security;
- session fixation;
- expiration;
- logout;
- token invalidation;
- concurrent sessions;
- replay;
- remember-me tokens;
- JWT handling.

A strong authentication mechanism can still be undermined by weak session handling.

Related notes:

[Session Management](session-management.md)

[JSON Web Tokens](jwt.md)

---

# Injection

Injection vulnerabilities occur when untrusted input is interpreted as part of a command, query or executable expression.

Important classes include:

- SQL injection;
- NoSQL injection;
- LDAP injection;
- OS command injection;
- server-side template injection;
- XML external entity injection.

The core model is:

```text
User-Controlled Input
      |
      v
Insufficient Separation / Validation
      |
      v
Interpreter / Parser / Query Engine
      |
      v
Unexpected Execution
```

Related notes:

[SQL Injection](sql-injection.md)

[NoSQL Injection](nosql-injection.md)

[LDAP Injection](ldap-injection.md)

[OS Command Injection](command-injection.md)

[Server-Side Template Injection](ssti.md)

[XML External Entity Injection](xxe.md)

---

# SQL Injection and sqlmap

Manual testing should generally come first.

A useful flow is:

```text
Interesting Parameter
      |
      v
Manual SQLi Hypothesis
      |
      v
Burp Repeater
      |
      v
Focused sqlmap Validation
      |
      v
Manual Confirmation
```

Related tool:

[sqlmap](../tools/web-testing/sqlmap.md)

---

# Client-Side Security

Client-side testing focuses on behaviour within the browser.

Important areas include:

- cross-site scripting;
- DOM-based vulnerabilities;
- HTML injection;
- CSRF;
- CORS;
- clickjacking;
- open redirects;
- XS-Leaks;
- third-party JavaScript;
- prototype pollution.

Modern applications often move significant logic into JavaScript, making client-side analysis a central part of testing.

Related notes:

[Cross-Site Scripting](xss.md)

[DOM-Based Vulnerabilities](dom-based-vulnerabilities.md)

[HTML Injection](html-injection.md)

[Cross-Site Request Forgery](csrf.md)

[CORS](cors.md)

[Clickjacking](clickjacking.md)

[Open Redirect](open-redirect.md)

[XS-Leaks](xs-leaks.md)

[Third-Party JavaScript](third-party-javascript.md)

[Prototype Pollution](prototype-pollution.md)

---

# Server-Side Security

Server-side testing focuses on backend processing and server-side trust boundaries.

Important areas include:

- SSRF;
- XXE;
- path traversal;
- file inclusion;
- file upload;
- insecure deserialization;
- command injection;
- template injection;
- input validation.

Potential consequences can include:

- sensitive data access;
- backend service interaction;
- internal network access;
- file access;
- code execution;
- privilege boundary violations.

Actual impact must be demonstrated rather than assumed.

Related notes:

[Server-Side Request Forgery](ssrf.md)

[XML External Entity Injection](xxe.md)

[Path Traversal](path-traversal.md)

[File Inclusion](file-inclusion.md)

[File Upload Vulnerabilities](file-upload.md)

[Insecure Deserialization](deserialization.md)

[Input Validation](input-validation.md)

---

# Out-of-Band Testing

Some server-side vulnerabilities do not create a visible response.

In these cases:

```text
Application Request
      |
      v
Backend Processing
      |
      v
External DNS / HTTP Interaction
      |
      v
OOB Service
```

Interactsh can support controlled validation of such behaviour.

Related tool:

[Interactsh](../tools/web-testing/interactsh.md)

A callback proves that an interaction occurred.

It does not automatically prove the full vulnerability impact.

---

# HTTP and Infrastructure

Web application security also depends on HTTP behaviour and supporting infrastructure.

Areas include:

- HTTP security headers;
- request smuggling;
- Host header attacks;
- cache poisoning;
- cache deception;
- information disclosure.

Related notes:

[HTTP Security Headers](http-security-headers.md)

[HTTP Request Smuggling](http-request-smuggling.md)

[HTTP Host Header Attacks](host-header-attacks.md)

[Web Cache Poisoning](web-cache-poisoning.md)

[Web Cache Deception](web-cache-deception.md)

[Information Disclosure](information-disclosure.md)

---

# Business Logic

Business logic vulnerabilities occur when legitimate functionality can be used in unintended ways.

Examples include:

- workflow bypass;
- price manipulation;
- quantity manipulation;
- race conditions;
- coupon abuse;
- account state manipulation;
- multi-step process bypass;
- trust-boundary violations.

Business logic testing requires understanding:

```text
How should this process work?
```

then asking:

```text
What happens if the expected sequence changes?
```

Related notes:

[Business Logic Vulnerabilities](business-logic.md)

[Race Conditions](race-conditions.md)

[Rate Limiting and Anti-Automation](rate-limiting.md)

---

# API Security

Modern web applications frequently expose APIs.

Testing should include:

- REST APIs;
- GraphQL;
- gRPC;
- WebSockets;
- authentication;
- object-level authorisation;
- function-level authorisation;
- mass assignment;
- rate limiting;
- undocumented endpoints.

A useful model is:

```text
API Endpoint
    |
    v
Authentication
    |
    v
Authorisation
    |
    v
Input Processing
    |
    v
Business Logic
    |
    v
Response
```

Related notes:

[API Security](api-security.md)

[GraphQL](graphql.md)

[gRPC Security](grpc-security.md)

[WebSockets](websockets.md)

[Mass Assignment](mass-assignment.md)

---

# WebSockets

WebSockets create persistent two-way communication between client and server.

Testing areas include:

- authentication;
- Origin validation;
- message manipulation;
- authorisation;
- session handling;
- Cross-Site WebSocket Hijacking;
- input validation.

Burp Suite can be used to inspect and modify WebSocket traffic.

Related note:

[WebSockets](websockets.md)

---

# Identity and Tokens

Modern web applications often rely on token-based or federated identity systems.

Important areas include:

- OAuth 2.0;
- OpenID Connect;
- JWT;
- SAML.

Related notes:

[OAuth 2.0 and OpenID Connect](oauth-oidc.md)

[JSON Web Tokens](jwt.md)

[SAML Security](saml.md)

---

# Software Supply Chain and Secrets

Application security also depends on:

- third-party packages;
- dependencies;
- secrets;
- build systems;
- configuration.

Related notes:

[Dependency Security](dependency-security.md)

[Secrets Exposure](secrets-exposure.md)

---

# Modern Web Security

Modern attack surfaces increasingly include:

- prototype pollution;
- LLM-enabled web functionality;
- client-heavy applications;
- third-party integrations.

Related notes:

[Prototype Pollution](prototype-pollution.md)

[Web LLM Attacks](web-llm-attacks.md)

---

# Web Testing Tools

Tools should support the methodology rather than replace it.

| Objective | Useful Tools |
|---|---|
| Technology identification | WhatWeb, Wappalyzer, httpx |
| HTTP probing | httpx |
| Content discovery | ffuf |
| Crawling | Katana |
| Manual request testing | Burp Suite |
| Repeatable security checks | Nuclei |
| SQL injection validation | sqlmap |
| Out-of-band validation | Interactsh |
| Packet analysis | Wireshark, TShark |
| TLS investigation | OpenSSL and dedicated TLS tooling |

Detailed tool sections:

[Web Enumeration Tools](../tools/web-enumeration/index.md)

[Web Application Testing Tools](../tools/web-testing/index.md)

---

# Burp Suite

Burp Suite is the central interactive tool used throughout many of these notes.

A useful manual workflow is:

```text
Browser
  |
  v
Burp Proxy
  |
  v
HTTP History
  |
  v
Repeater
  |
  v
Controlled Modification
  |
  v
Compare Response
  |
  v
Interpret Behaviour
```

Related tool note:

[Burp Suite](../tools/web-testing/burp-suite.md)

Related Burp notes:

[Burp Suite Extensions](burp-suite/extensions.md)

[Burp Suite Testing Workflows](burp-suite/workflows.md)

---

# Automated Discovery vs Manual Validation

Automation provides breadth.

Manual testing provides context.

```text
Automation
    |
    +-- Discovery
    +-- Repetition
    +-- Coverage

Manual Testing
    |
    +-- Context
    +-- Business Logic
    +-- Reproduction
    +-- Impact

Together
    |
    v
Stronger Assessment
```

Do not rely on one alone.

---

# Tool Output Is Not a Finding

This principle applies throughout the web section.

```text
Nuclei Match
      !=
Confirmed Vulnerability
```

```text
Wappalyzer Detection
      !=
Certain Technology Identification
```

```text
sqlmap Candidate
      !=
Final Security Conclusion
```

```text
HTTP 500
      !=
Confirmed Injection
```

A tool result is an observation that requires interpretation.

---

# Evidence Before Conclusions

A useful confidence model is:

| State | Meaning |
|---|---|
| Observation | Something potentially relevant was observed |
| Indicator | Evidence suggests a specific condition |
| Candidate | The condition warrants testing |
| Validated | Behaviour was reproduced |
| Confirmed | Evidence demonstrates the security condition and impact |

For example:

```text
Scanner reports possible SSRF
      |
      v
Candidate
      |
      v
Controlled OOB callback
      |
      v
Validated server-side interaction
      |
      v
Destination control confirmed
      |
      v
Confirmed security condition
```

---

# Baseline First

Many web-testing mistakes happen because the tester does not understand the normal response.

Before fuzzing or modifying a request, record:

```text
Status
Length
Body
Headers
Redirect
Timing
Authentication state
```

Then compare modified behaviour against the baseline.

---

# One Variable at a Time

Where practical:

```text
Baseline
   |
   v
Change One Input
   |
   v
Observe
```

Changing too many values at once makes interpretation difficult.

---

# Authentication Context Matters

The same request may behave differently as:

```text
Unauthenticated user
Standard user
Privileged user
Administrator
```

Always record the role used during testing.

---

# State Matters

Web applications can be stateful.

Testing may depend on:

- session;
- CSRF tokens;
- previous workflow steps;
- object ownership;
- transaction state;
- tenant;
- account status.

A request should be interpreted within that state.

---

# False Positives

False positives may result from:

- generic 500 responses;
- authentication redirects;
- wildcard routing;
- WAF behaviour;
- CDN responses;
- dynamic content;
- caching;
- scanner assumptions;
- soft 404 responses.

A useful process is:

```text
Tool Match
    |
    v
Inspect Raw Request / Response
    |
    v
Establish Baseline
    |
    v
Reproduce Manually
    |
    v
Compare Behaviour
    |
    v
Confirm or Reject
```

---

# False Negatives

Automated testing may miss vulnerabilities because of:

- authentication;
- stateful workflows;
- JavaScript;
- custom APIs;
- business logic;
- WAF interference;
- unusual parameter formats;
- multi-step attacks;
- role requirements.

A clean scan does not prove that the application is secure.

---

# Evidence Collection

Useful evidence includes:

```text
Target
Endpoint
Method
Parameter
Authentication context
Baseline request
Modified request
Baseline response
Modified response
Timestamp
Tool version
Manual reproduction
Observed impact
```

Protect:

- session cookies;
- bearer tokens;
- passwords;
- personal data;
- API keys.

---

# Reporting

A strong finding should describe the underlying security condition.

Avoid:

```text
Burp found an issue.
```

or:

```text
Nuclei reported a vulnerability.
```

Prefer:

```text
The application accepts an object identifier controlled by the user and
returns the requested object without verifying that it belongs to the
authenticated account.
```

The tool supports the evidence.

It is not the finding.

---

# Impact Assessment

The demonstrated behaviour should be translated into actual security impact.

Consider:

```text
Confidentiality
Integrity
Availability
Authentication
Authorisation
Privilege
Tenant isolation
Backend reachability
User interaction
```

Do not assume maximum impact.

---

# Remediation

Remediation should address the root cause.

Examples include:

- parameterised database queries;
- centralised authorisation checks;
- secure session handling;
- strict destination validation;
- safe file handling;
- output encoding;
- CSRF protection;
- secure parser configuration;
- least privilege;
- secure framework APIs.

WAF rules and signatures should usually be treated as defence in depth rather than the root fix.

---

# Retesting

After remediation:

```text
Original Test
      |
      v
Patched Application
      |
      v
Expected Safe Behaviour
```

Retesting should confirm:

- the original issue no longer reproduces;
- the root cause has been addressed;
- alternative variants are not still present;
- legitimate functionality still works.

---

# Web Testing Checklist

Use the full checklist for detailed assessment coverage:

[Web Application Pentesting Checklist](checklist.md)

A high-level review should include:

- [ ] Scope confirmed.
- [ ] Attack surface mapped.
- [ ] Technologies identified.
- [ ] Content discovered.
- [ ] Parameters discovered.
- [ ] Authentication tested.
- [ ] Authorisation tested.
- [ ] Sessions tested.
- [ ] Injection tested.
- [ ] Server-side behaviour tested.
- [ ] Client-side behaviour tested.
- [ ] API security tested.
- [ ] Business logic tested.
- [ ] Rate limiting reviewed.
- [ ] HTTP behaviour reviewed.
- [ ] Information disclosure reviewed.
- [ ] Automated candidates manually validated.
- [ ] Evidence captured.
- [ ] Impact assessed.
- [ ] Remediation provided.
- [ ] Retest criteria defined.

---

# Related Sections

[Web Application Testing Methodology](methodology.md)

[Web Application Pentesting Checklist](checklist.md)

[Web Reconnaissance](reconnaissance/index.md)

[Burp Suite Testing Workflows](burp-suite/workflows.md)

[Web Enumeration Tools](../tools/web-enumeration/index.md)

[Web Application Testing Tools](../tools/web-testing/index.md)

[Source Code Review](../source-code-review/index.md)

[Cheatsheets](../cheatsheets/index.md)

---

# External References

## OWASP

[OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }

[OWASP Top 10](https://owasp.org/www-project-top-ten/){ target="_blank" rel="noopener noreferrer" }

[OWASP API Security Top 10](https://owasp.org/API-Security/){ target="_blank" rel="noopener noreferrer" }

[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/){ target="_blank" rel="noopener noreferrer" }

## PortSwigger

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

[Burp Suite Documentation](https://portswigger.net/burp/documentation){ target="_blank" rel="noopener noreferrer" }

## Weakness Classification

[MITRE CWE](https://cwe.mitre.org/){ target="_blank" rel="noopener noreferrer" }

## Additional Practical Reference

[HackTricks - Web](https://book.hacktricks.wiki/en/pentesting-web/index.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Web Testing Model

Do not test web applications like this:

```text
Run Scanner
    |
    v
Collect Alerts
    |
    v
Report Findings
```

Use this model:

```text
Understand Scope
      |
      v
Map Attack Surface
      |
      v
Understand Application Behaviour
      |
      v
Identify Security Hypothesis
      |
      v
Use Appropriate Tool
      |
      v
Modify One Controlled Variable
      |
      v
Compare Against Baseline
      |
      v
Reproduce Manually
      |
      v
Determine Security Boundary
      |
      v
Validate Impact
      |
      v
Capture Evidence
      |
      v
Report Root Cause
      |
      v
Remediate
      |
      v
Retest
```

Strong web application testing is not defined by the number of payloads or tools used.

It is defined by how well the tester understands the application, identifies meaningful security boundaries, validates behaviour, and supports conclusions with reproducible evidence.
