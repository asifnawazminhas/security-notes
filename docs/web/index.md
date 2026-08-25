# Web Application Security

Web application security testing focuses on identifying vulnerabilities and weaknesses in web applications, APIs, authentication mechanisms, access controls and the technologies that support them.

This section contains practical notes, methodologies, commands, tools and references that I use when performing authorised web application penetration testing and security research.

!!! warning "Authorised Security Testing"

    The techniques documented in these notes are intended for authorised security assessments, lab environments, security research and responsible vulnerability disclosure.

---

## Web Application Testing

A web application assessment should follow a structured methodology rather than testing individual vulnerabilities at random.

The general workflow used throughout these notes is:

```text
Reconnaissance
      ↓
Technology Identification
      ↓
Attack Surface Mapping
      ↓
Content Discovery
      ↓
Parameter Discovery
      ↓
Authentication Testing
      ↓
Authorisation Testing
      ↓
Input Validation
      ↓
Server-Side Testing
      ↓
Client-Side Testing
      ↓
Business Logic Testing
      ↓
Validation
      ↓
Reporting
```

The methodology provides a repeatable approach while still allowing the assessment to adapt to the application, architecture and scope.

[View the Web Application Testing Methodology](methodology.md)

---

## Reconnaissance

Reconnaissance focuses on understanding the application's external attack surface before deeper testing begins.

Typical activities include:

* Subdomain enumeration
* DNS enumeration
* Technology identification
* Web server identification
* Content discovery
* Parameter discovery
* JavaScript analysis
* API discovery
* Virtual host discovery
* Historical URL discovery

The objective is to identify as much of the accessible attack surface as possible before vulnerability testing begins.

---

## Authentication

Authentication testing focuses on how the application verifies the identity of users.

Areas to investigate include:

* Login functionality
* Username enumeration
* Password policies
* Account lockout mechanisms
* Password reset functionality
* Multi-factor authentication
* Remember-me functionality
* Session creation
* Authentication bypass
* OAuth and SSO implementations

Authentication mechanisms are often one of the most important security boundaries in a web application.

---

## Authorisation

Authorisation testing determines whether users can access functionality or resources outside their intended permissions.

Common areas include:

* Horizontal privilege escalation
* Vertical privilege escalation
* Insecure Direct Object References
* Missing function-level access control
* Role manipulation
* Forced browsing
* API access control
* Administrative functionality exposure

Testing should be performed using accounts with different privilege levels whenever the assessment scope allows it.

---

## Session Management

Session management testing focuses on how authenticated sessions are created, maintained and terminated.

Testing areas include:

* Session token entropy
* Session fixation
* Cookie security attributes
* Session expiration
* Logout behaviour
* Concurrent sessions
* Token invalidation
* JWT handling
* Session replay

Session weaknesses can allow attackers to impersonate authenticated users even when the authentication mechanism itself is secure.

---

## Injection Vulnerabilities

Injection vulnerabilities occur when untrusted input is interpreted as part of a command, query or executable expression.

Important injection classes include:

* SQL Injection
* Command Injection
* Server-Side Template Injection
* LDAP Injection
* XPath Injection
* NoSQL Injection
* Expression Language Injection

Testing should focus on identifying where user-controlled data reaches interpreters or other sensitive processing components.

---

## Client-Side Security

Client-side testing focuses on vulnerabilities that execute or influence behaviour within the user's browser.

Important areas include:

* Cross-Site Scripting
* DOM-based vulnerabilities
* Cross-Site Request Forgery
* CORS misconfigurations
* Web messaging
* Browser storage
* Client-side redirects
* JavaScript analysis
* Prototype pollution

Modern web applications often contain significant functionality within JavaScript, making client-side analysis an important part of the assessment.

---

## Server-Side Security

Server-side testing focuses on functionality processed by the application or supporting infrastructure.

Important areas include:

* Server-Side Request Forgery
* XML External Entity Injection
* Path Traversal
* File Inclusion
* File Upload
* Deserialization
* Command Injection
* Server-Side Template Injection
* HTTP Request Smuggling

These vulnerabilities can sometimes provide access to internal systems or lead to server-side code execution.

---

## Business Logic

Business logic vulnerabilities occur when legitimate application functionality can be abused in ways that were not intended by the developers.

Examples include:

* Workflow bypass
* Price manipulation
* Quantity manipulation
* Race conditions
* Coupon abuse
* Account state manipulation
* Multi-step process bypass
* Trust boundary violations

Business logic testing requires understanding how the application is intended to operate rather than relying solely on automated scanners.

---

## API Security

Modern applications frequently expose APIs that require dedicated security testing.

Areas to investigate include:

* REST APIs
* GraphQL
* SOAP
* API authentication
* Object-level authorisation
* Function-level authorisation
* Mass assignment
* Excessive data exposure
* Rate limiting
* API versioning
* Undocumented endpoints

API testing should include both endpoints used by the application's frontend and endpoints discovered independently.

---

## WebSockets

Applications using WebSockets introduce additional attack surfaces because communication can remain open between the browser and server.

Testing areas include:

* WebSocket authentication
* Origin validation
* Message manipulation
* Authorisation
* Cross-Site WebSocket Hijacking
* Input validation
* Session handling

WebSocket traffic can be intercepted and modified using tools such as Burp Suite.

---

## Testing Checklist

A structured checklist helps ensure important areas are not overlooked during an assessment.

The checklist covers:

* Reconnaissance
* Attack surface discovery
* Authentication
* Authorisation
* Session management
* Input validation
* Injection vulnerabilities
* Client-side security
* Server-side security
* APIs
* Business logic
* Information disclosure
* Security headers
* Cryptography
* Reporting and validation

[Open the Web Application Pentesting Checklist](checklist.md)

---

## Tools

Different stages of web application testing require different tools.

Common tools referenced throughout these notes include:

| Purpose | Tools |
| --- | --- |
| Proxy and manual testing | Burp Suite |
| Subdomain discovery | Subfinder, Amass, Assetfinder |
| HTTP probing | httpx |
| Crawling | Katana |
| Content discovery | ffuf, feroxbuster, dirsearch |
| Parameter discovery | ParamSpider, Arjun |
| Historical URLs | waybackurls, gau |
| Technology detection | Wappalyzer, WhatWeb |
| Vulnerability scanning | Nuclei |
| TLS testing | testssl.sh |
| DNS testing | dnsx |
| JavaScript analysis | LinkFinder, manual review |

Tools should support the testing methodology rather than replace manual analysis.

---

## References

The notes in this section are informed by practical security testing, security research and established web application security methodologies.

Useful reference frameworks include:

* OWASP Web Security Testing Guide
* OWASP Top 10
* OWASP API Security Top 10
* PortSwigger Web Security Academy
* MITRE CWE
* NIST security guidance

These references provide useful baselines, but testing should always be adapted to the target application's architecture, technology and threat model.
