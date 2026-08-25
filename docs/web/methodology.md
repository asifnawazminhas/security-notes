# Web Application Testing Methodology

A structured web application penetration test follows a repeatable process for discovering the attack surface, identifying vulnerabilities, validating their impact and documenting the results.

The exact methodology depends on the application, architecture, technologies and assessment scope.

!!! warning "Authorised Security Testing"

    The techniques documented in these notes are intended for authorised security assessments, lab environments, security research and responsible vulnerability disclosure.

---

## Testing Workflow

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

The workflow should not be treated as strictly linear. Discoveries made during later stages frequently require returning to earlier stages.

---

## 1. Reconnaissance

The first stage is understanding the application's externally accessible attack surface.

### Objectives

Identify:

* Domains and subdomains
* IP addresses
* Web applications
* APIs
* Administrative interfaces
* Development and staging environments
* Authentication portals
* Exposed services
* Historical endpoints
* Third-party integrations

### Typical Activities

```text
Domain
  ↓
Subdomain Enumeration
  ↓
DNS Resolution
  ↓
HTTP Probing
  ↓
Technology Identification
  ↓
Crawling
  ↓
Content Discovery
  ↓
Parameter Discovery
  ↓
Attack Surface
```

Reconnaissance should continue throughout the assessment as new infrastructure and application components are discovered.

---

## 2. Technology Identification

Understanding the technologies used by the target helps determine which testing techniques are relevant.

Identify where possible:

* Web server
* Application framework
* Programming language
* CMS
* JavaScript frameworks
* Reverse proxies
* CDN
* WAF
* Authentication technologies
* API technologies
* Third-party components
* Software versions

Technology identification can also reveal outdated or unsupported components requiring further investigation.

---

## 3. Attack Surface Mapping

The discovered assets should be converted into an organised attack surface.

Map:

* Applications
* Hosts
* Ports
* Endpoints
* Parameters
* APIs
* Authentication boundaries
* User roles
* Administrative functionality
* Upload functionality
* Import and export functionality
* External integrations

The objective is to understand where user-controlled input enters the application and where security boundaries exist.

---

## 4. Content Discovery

Content discovery identifies resources that may not be directly linked from the application's normal interface.

Look for:

* Directories
* Files
* Backup files
* Configuration files
* Administrative panels
* API endpoints
* Debug interfaces
* Development endpoints
* Documentation
* Source maps
* Temporary files
* Old application versions

Automated discovery should be combined with manual inspection and crawling.

---

## 5. Parameter Discovery

Parameters represent potential input points into the application.

Investigate:

* GET parameters
* POST parameters
* JSON properties
* XML elements
* HTTP headers
* Cookies
* Path parameters
* Multipart fields
* API parameters
* WebSocket messages

Parameters discovered through JavaScript, historical URLs and API documentation can reveal functionality that is not immediately visible.

---

## 6. Authentication Testing

Authentication testing evaluates how the application verifies user identities.

Review:

* Login functionality
* Username enumeration
* Password policies
* Account lockout
* Brute-force protections
* Password reset
* Multi-factor authentication
* Remember-me functionality
* OAuth
* SSO
* Authentication tokens
* Authentication bypass opportunities

Authentication should also be tested across different application components and APIs.

---

## 7. Authorisation Testing

Authentication establishes identity. Authorisation determines what that identity is permitted to access.

Test for:

* Horizontal privilege escalation
* Vertical privilege escalation
* Insecure Direct Object References
* Missing access controls
* Administrative endpoint exposure
* Forced browsing
* Role manipulation
* API authorisation weaknesses

Where possible, use multiple accounts with different privilege levels to compare application behaviour.

---

## 8. Session Management Testing

Review how sessions are created, maintained and destroyed.

Investigate:

* Session cookies
* Cookie attributes
* Session identifiers
* Session fixation
* Session expiration
* Logout invalidation
* Concurrent sessions
* Token rotation
* JWT handling
* Session replay

Session handling should be tested alongside authentication and authorisation.

---

## 9. Input Validation

Identify locations where user-controlled input is processed.

Potential input sources include:

```text
URL parameters
POST bodies
JSON
XML
Cookies
HTTP headers
File names
Uploaded files
WebSocket messages
API parameters
```

Trace how these values are validated, transformed, stored and returned.

Input points become candidates for more specialised vulnerability testing.

---

## 10. Server-Side Testing

Server-side testing focuses on vulnerabilities processed by the application or supporting infrastructure.

Test for areas such as:

* SQL Injection
* Command Injection
* Server-Side Request Forgery
* Server-Side Template Injection
* XML External Entity Injection
* Path Traversal
* File Inclusion
* File Upload
* Deserialization
* HTTP Request Smuggling

Pay particular attention to functionality that interacts with operating system commands, databases, file systems, parsers and internal network resources.

---

## 11. Client-Side Testing

Analyse functionality executed or processed within the browser.

Test for:

* Cross-Site Scripting
* DOM-based vulnerabilities
* Cross-Site Request Forgery
* CORS weaknesses
* Open Redirect
* Prototype Pollution
* Browser storage issues
* Web messaging
* Client-side access controls

JavaScript should be reviewed for hidden endpoints, parameters, secrets, API calls and client-side security logic.

---

## 12. Business Logic Testing

Business logic vulnerabilities often require understanding how the application is intended to operate.

Investigate:

* Workflow bypass
* State manipulation
* Price manipulation
* Quantity manipulation
* Race conditions
* Repeated actions
* Coupon or discount abuse
* Multi-step process bypass
* Trust assumptions
* Limit bypasses

These vulnerabilities are difficult to detect using automated scanning alone.

---

## 13. API Testing

APIs should be treated as a separate attack surface even when they support the same web application.

Review:

* Endpoint discovery
* Authentication
* Object-level authorisation
* Function-level authorisation
* Input validation
* Mass assignment
* Excessive data exposure
* Rate limiting
* API versioning
* GraphQL
* REST
* SOAP

Compare API behaviour between unauthenticated users and users with different privilege levels.

---

## 14. Validation

Potential vulnerabilities should be manually validated before reporting.

Determine:

* Is the behaviour reproducible?
* What conditions are required?
* Which users are affected?
* What privileges are required?
* What data or functionality is exposed?
* Can the vulnerability be chained with another weakness?
* What is the realistic security impact?

Avoid relying solely on scanner classifications.

---

## 15. Impact Assessment

Technical findings should be translated into realistic security impact.

Consider:

* Confidentiality
* Integrity
* Availability
* Required privileges
* User interaction
* Exploitability
* Scope
* Business impact
* Potential attack chains

Where appropriate, CVSS can be used as one component of the severity assessment.

---

## 16. Reporting

Each confirmed vulnerability should contain enough information for another tester or developer to reproduce and understand the issue.

A finding should normally include:

```text
Title
Description
Affected Component
Technical Details
Steps to Reproduce
Evidence
Security Impact
Severity
Recommendation
References
```

Screenshots, HTTP requests and responses should be included where they improve reproducibility.

---

## 17. Retesting

After remediation, previously identified vulnerabilities should be tested again.

Verify that:

* The original vulnerability is resolved
* The fix applies to all affected endpoints
* Alternative attack paths are addressed
* The remediation did not introduce another vulnerability
* Related functionality remains secure

A vulnerability should only be considered resolved after the remediation has been validated.

---

## Continuous Discovery

Web application penetration testing is iterative.

A useful mental model is:

```text
Discover
   ↓
Map
   ↓
Test
   ↓
Validate
   ↓
Discover More
   ↓
Test Again
   ↓
Report
```

New endpoints, parameters, roles and technologies discovered during testing should continuously feed back into the assessment methodology.

---

## Related Notes

* [Web Application Security Overview](index.md)
* [Pentesting Checklist](checklist.md)
* [Reconnaissance](reconnaissance/index.md)
