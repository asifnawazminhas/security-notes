# Web Application Pentesting Checklist

This checklist provides a structured reference for web application security assessments.

It is designed to complement the [Web Application Testing Methodology](methodology.md) and can be used to track areas that have been reviewed during an authorised penetration test.

!!! warning "Authorised Security Testing"

    Use this checklist only for systems you own or have explicit permission to test.

---

## Reconnaissance

### Domain and Infrastructure

- [ ] Identify the primary domain
- [ ] Enumerate subdomains
- [ ] Resolve discovered domains
- [ ] Identify live HTTP and HTTPS services
- [ ] Identify exposed ports and services
- [ ] Identify IP addresses and hosting providers
- [ ] Review DNS records
- [ ] Check certificate transparency logs
- [ ] Identify CDN usage
- [ ] Identify reverse proxies
- [ ] Identify WAF protection
- [ ] Search for development and staging environments

### Historical Discovery

- [ ] Search historical URLs
- [ ] Review archived application versions
- [ ] Identify historical parameters
- [ ] Identify deprecated endpoints
- [ ] Search for old API endpoints
- [ ] Look for exposed backup files
- [ ] Review historical JavaScript files

---

## Technology Identification

- [ ] Identify web server
- [ ] Identify application framework
- [ ] Identify programming language
- [ ] Identify CMS
- [ ] Identify JavaScript frameworks
- [ ] Identify API technologies
- [ ] Identify authentication technologies
- [ ] Identify third-party services
- [ ] Identify exposed software versions
- [ ] Check for outdated components
- [ ] Review HTTP response headers
- [ ] Review error messages for technology disclosure

---

## Attack Surface Mapping

- [ ] Map applications and sub-applications
- [ ] Map authentication boundaries
- [ ] Identify user roles
- [ ] Identify administrative functionality
- [ ] Identify API endpoints
- [ ] Identify upload functionality
- [ ] Identify download functionality
- [ ] Identify import functionality
- [ ] Identify export functionality
- [ ] Identify search functionality
- [ ] Identify integrations
- [ ] Identify webhooks
- [ ] Identify redirects
- [ ] Identify URL processing functionality

---

## Content Discovery

- [ ] Enumerate directories
- [ ] Enumerate files
- [ ] Search for hidden endpoints
- [ ] Search for administrative interfaces
- [ ] Search for debug interfaces
- [ ] Search for API documentation
- [ ] Search for Swagger/OpenAPI documentation
- [ ] Search for GraphQL endpoints
- [ ] Search for source maps
- [ ] Search for configuration files
- [ ] Search for backup files
- [ ] Search for temporary files
- [ ] Search for log files
- [ ] Review `robots.txt`
- [ ] Review `sitemap.xml`
- [ ] Review `.well-known` resources

---

## Parameter Discovery

- [ ] Identify GET parameters
- [ ] Identify POST parameters
- [ ] Identify JSON properties
- [ ] Identify XML input
- [ ] Identify path parameters
- [ ] Identify HTTP header input
- [ ] Identify cookie values
- [ ] Identify multipart form fields
- [ ] Identify file name input
- [ ] Identify hidden form fields
- [ ] Identify WebSocket messages
- [ ] Extract parameters from JavaScript
- [ ] Extract parameters from historical URLs

---

## JavaScript Analysis

- [ ] Collect JavaScript files
- [ ] Review application JavaScript
- [ ] Review minified JavaScript where relevant
- [ ] Search for hidden endpoints
- [ ] Search for API routes
- [ ] Search for parameter names
- [ ] Search for internal URLs
- [ ] Search for hard-coded credentials
- [ ] Search for API keys and tokens
- [ ] Search for sensitive comments
- [ ] Review client-side authentication logic
- [ ] Review client-side authorisation logic
- [ ] Check for source maps
- [ ] Review third-party JavaScript dependencies

---

## Authentication

### Login

- [ ] Test username enumeration
- [ ] Test password enumeration behaviour
- [ ] Review password policy
- [ ] Test account lockout
- [ ] Test rate limiting
- [ ] Test brute-force protections
- [ ] Test default credentials where applicable
- [ ] Test authentication bypass conditions
- [ ] Compare responses for valid and invalid accounts
- [ ] Test alternative authentication endpoints

### Password Reset

- [ ] Test username enumeration
- [ ] Review reset token entropy
- [ ] Test reset token expiration
- [ ] Test reset token reuse
- [ ] Test token invalidation
- [ ] Test host header handling
- [ ] Test password reset poisoning
- [ ] Check whether old sessions remain valid
- [ ] Test account recovery functionality

### Multi-Factor Authentication

- [ ] Verify MFA is enforced
- [ ] Test MFA workflow bypass
- [ ] Test direct access after primary authentication
- [ ] Test code reuse
- [ ] Test rate limiting
- [ ] Test recovery mechanisms
- [ ] Test trusted-device functionality
- [ ] Test session state before MFA completion

### SSO and OAuth

- [ ] Identify supported identity providers
- [ ] Review redirect URI validation
- [ ] Review `state` handling
- [ ] Review `nonce` handling
- [ ] Test account linking
- [ ] Test authentication flow manipulation
- [ ] Review token exposure
- [ ] Review logout behaviour

---

## Authorisation

- [ ] Identify different user roles
- [ ] Compare functionality between roles
- [ ] Test horizontal privilege escalation
- [ ] Test vertical privilege escalation
- [ ] Test IDOR/BOLA
- [ ] Modify object identifiers
- [ ] Test forced browsing
- [ ] Test administrative endpoints
- [ ] Test hidden functionality
- [ ] Test role parameter manipulation
- [ ] Test HTTP method changes
- [ ] Test API authorisation independently
- [ ] Test access after account state changes
- [ ] Verify server-side access controls

---

## Session Management

- [ ] Review session cookie attributes
- [ ] Check `Secure`
- [ ] Check `HttpOnly`
- [ ] Check `SameSite`
- [ ] Review session token entropy
- [ ] Test session fixation
- [ ] Test session expiration
- [ ] Test idle timeout
- [ ] Test logout invalidation
- [ ] Test password-change invalidation
- [ ] Test password-reset invalidation
- [ ] Test concurrent sessions
- [ ] Test session replay
- [ ] Review remember-me tokens
- [ ] Review JWT implementation where applicable

---

## Cross-Site Scripting

- [ ] Test reflected input
- [ ] Test stored input
- [ ] Test DOM-based input
- [ ] Identify reflection contexts
- [ ] Review HTML context
- [ ] Review attribute context
- [ ] Review JavaScript context
- [ ] Review URL context
- [ ] Review DOM sinks
- [ ] Review sanitisation
- [ ] Review encoding
- [ ] Review Content Security Policy
- [ ] Test file names and metadata where displayed
- [ ] Test client-side rendering

---

## SQL Injection

- [ ] Identify database-backed parameters
- [ ] Test query parameters
- [ ] Test POST parameters
- [ ] Test JSON input
- [ ] Test cookies where relevant
- [ ] Test headers where relevant
- [ ] Check error behaviour
- [ ] Test Boolean-based behaviour
- [ ] Test time-based behaviour
- [ ] Test UNION conditions where appropriate
- [ ] Review second-order input
- [ ] Determine database technology where possible

---

## Command Injection

- [ ] Identify functionality interacting with operating system commands
- [ ] Test user-controlled command arguments
- [ ] Test file-processing functionality
- [ ] Test network utilities exposed through the application
- [ ] Test asynchronous processing
- [ ] Review command output handling
- [ ] Review blind execution indicators
- [ ] Review shell metacharacter handling
- [ ] Review input sanitisation

---

## Server-Side Request Forgery

- [ ] Identify URL parameters
- [ ] Identify webhook functionality
- [ ] Identify URL preview functionality
- [ ] Identify import-by-URL functionality
- [ ] Identify image or document fetching
- [ ] Test redirect handling
- [ ] Test protocol restrictions
- [ ] Test hostname validation
- [ ] Test IP address validation
- [ ] Review DNS resolution behaviour
- [ ] Test internal resource access within authorised scope
- [ ] Review blind SSRF indicators

---

## Server-Side Template Injection

- [ ] Identify dynamically rendered templates
- [ ] Determine template engine where possible
- [ ] Test whether expressions are evaluated
- [ ] Review user-controlled template values
- [ ] Review email/template functionality
- [ ] Review document generation
- [ ] Review error messages
- [ ] Determine sandbox restrictions where applicable

---

## Cross-Site Request Forgery

- [ ] Identify state-changing requests
- [ ] Review CSRF tokens
- [ ] Test missing CSRF tokens
- [ ] Test token validation
- [ ] Test token reuse
- [ ] Review `SameSite` cookie configuration
- [ ] Review Origin validation
- [ ] Review Referer validation
- [ ] Test alternate content types where applicable
- [ ] Review sensitive account actions

---

## File Upload

- [ ] Identify all upload functionality
- [ ] Review allowed file extensions
- [ ] Review MIME type validation
- [ ] Review file signature validation
- [ ] Review file size restrictions
- [ ] Review file name handling
- [ ] Test duplicate file names
- [ ] Test special characters in file names
- [ ] Review storage location
- [ ] Determine whether uploaded files are publicly accessible
- [ ] Review content transformation
- [ ] Review image processing
- [ ] Review document processing
- [ ] Review archive extraction
- [ ] Check for path traversal in file names
- [ ] Verify uploaded content is served safely

---

## Path Traversal

- [ ] Identify file retrieval functionality
- [ ] Identify download parameters
- [ ] Identify template or resource parameters
- [ ] Review path normalisation
- [ ] Review encoded path handling
- [ ] Review absolute and relative path handling
- [ ] Review filename validation
- [ ] Review archive extraction paths
- [ ] Test traversal within the authorised environment

---

## XML External Entity Injection

- [ ] Identify XML endpoints
- [ ] Identify SOAP services
- [ ] Identify XML file uploads
- [ ] Identify document parsers
- [ ] Review external entity processing
- [ ] Review DTD processing
- [ ] Review parser configuration
- [ ] Review error behaviour
- [ ] Review out-of-band behaviour where authorised

---

## Deserialization

- [ ] Identify serialized data
- [ ] Identify encoded object structures
- [ ] Review cookies
- [ ] Review hidden parameters
- [ ] Review API payloads
- [ ] Identify serialization technology
- [ ] Review integrity protections
- [ ] Review type handling
- [ ] Review application libraries
- [ ] Review unsafe deserialization patterns

---

## HTTP Request Smuggling

- [ ] Identify reverse proxy architecture
- [ ] Compare frontend and backend parsing
- [ ] Review `Content-Length` handling
- [ ] Review `Transfer-Encoding` handling
- [ ] Test ambiguous requests only where explicitly authorised
- [ ] Review HTTP/1.1 behaviour
- [ ] Review HTTP/2 translation
- [ ] Check for response desynchronisation indicators

---

## Business Logic

- [ ] Understand intended workflow
- [ ] Test steps out of sequence
- [ ] Test repeated actions
- [ ] Test skipped steps
- [ ] Test negative values
- [ ] Test unusual quantities
- [ ] Test boundary values
- [ ] Test price calculations
- [ ] Test discounts and coupons
- [ ] Test account state transitions
- [ ] Test approval workflows
- [ ] Test race conditions
- [ ] Test trust assumptions between components

---

## API Security

- [ ] Discover API endpoints
- [ ] Identify API versions
- [ ] Review API documentation
- [ ] Review authentication
- [ ] Test BOLA/IDOR
- [ ] Test function-level authorisation
- [ ] Review excessive data exposure
- [ ] Review mass assignment
- [ ] Review input validation
- [ ] Review rate limiting
- [ ] Review pagination
- [ ] Review filtering
- [ ] Review error handling
- [ ] Test undocumented endpoints
- [ ] Review deprecated API versions

---

## GraphQL

- [ ] Identify GraphQL endpoint
- [ ] Review introspection
- [ ] Map available queries
- [ ] Map mutations
- [ ] Review object-level authorisation
- [ ] Review field-level authorisation
- [ ] Review excessive data exposure
- [ ] Review batching
- [ ] Review query depth controls
- [ ] Review complexity limits

---

## WebSockets

- [ ] Identify WebSocket endpoints
- [ ] Review authentication
- [ ] Review authorisation
- [ ] Review Origin validation
- [ ] Inspect messages
- [ ] Modify messages
- [ ] Test input validation
- [ ] Review session handling
- [ ] Test Cross-Site WebSocket Hijacking conditions

---

## HTTP Security Headers

Review:

- [ ] Content-Security-Policy
- [ ] Strict-Transport-Security
- [ ] X-Content-Type-Options
- [ ] Referrer-Policy
- [ ] Permissions-Policy
- [ ] Cross-Origin-Opener-Policy
- [ ] Cross-Origin-Resource-Policy
- [ ] Cross-Origin-Embedder-Policy
- [ ] Cache-Control where sensitive content is present

Also review obsolete or ineffective header configurations where encountered.

---

## CORS

- [ ] Review `Access-Control-Allow-Origin`
- [ ] Test Origin reflection
- [ ] Review credential support
- [ ] Review trusted origins
- [ ] Review `null` Origin behaviour
- [ ] Review subdomain trust
- [ ] Review preflight behaviour
- [ ] Determine whether sensitive responses are accessible cross-origin

---

## Information Disclosure

- [ ] Review HTTP headers
- [ ] Review verbose errors
- [ ] Review stack traces
- [ ] Review software versions
- [ ] Review internal hostnames
- [ ] Review internal IP addresses
- [ ] Review source maps
- [ ] Review comments
- [ ] Review JavaScript
- [ ] Review metadata
- [ ] Review debug endpoints
- [ ] Review API responses for excessive data
- [ ] Review publicly accessible files
- [ ] Review directory listings

---

## TLS and Transport Security

- [ ] Verify HTTPS enforcement
- [ ] Review supported TLS versions
- [ ] Review cipher suites
- [ ] Review certificate validity
- [ ] Review certificate hostname coverage
- [ ] Review HSTS
- [ ] Check for mixed content
- [ ] Review insecure redirects
- [ ] Review sensitive data transmitted over insecure channels

---

## Error Handling

- [ ] Trigger application errors safely
- [ ] Review stack traces
- [ ] Review database errors
- [ ] Review framework errors
- [ ] Review filesystem paths
- [ ] Review internal hostnames
- [ ] Review debugging information
- [ ] Compare authenticated and unauthenticated errors

---

## Validation

For each potential finding:

- [ ] Reproduce the behaviour
- [ ] Confirm the affected endpoint
- [ ] Confirm affected parameters
- [ ] Determine required privileges
- [ ] Determine required user interaction
- [ ] Determine affected users
- [ ] Determine realistic impact
- [ ] Check related endpoints
- [ ] Check whether the issue can be chained
- [ ] Capture sufficient evidence
- [ ] Remove test artefacts where applicable

---

## Reporting

For each confirmed finding:

- [ ] Write a clear title
- [ ] Describe the vulnerability
- [ ] Identify the affected component
- [ ] Document prerequisites
- [ ] Document reproduction steps
- [ ] Include relevant HTTP evidence
- [ ] Include screenshots where useful
- [ ] Explain technical impact
- [ ] Explain realistic business impact
- [ ] Assign severity
- [ ] Provide remediation guidance
- [ ] Include relevant references

---

## Retesting

- [ ] Reproduce the original test
- [ ] Verify the original vulnerability is resolved
- [ ] Test related endpoints
- [ ] Test alternative inputs
- [ ] Verify server-side enforcement
- [ ] Check for bypasses
- [ ] Check for regression
- [ ] Record retest evidence
- [ ] Update finding status

---

## Assessment Completion

Before completing the assessment:

- [ ] Review the original scope
- [ ] Confirm all in-scope applications were assessed
- [ ] Review notes for untested functionality
- [ ] Review scanner results requiring manual validation
- [ ] Review discovered endpoints
- [ ] Review discovered parameters
- [ ] Review all user roles
- [ ] Review evidence
- [ ] Remove testing artefacts
- [ ] Verify findings are reproducible
- [ ] Complete final report
