# Reconnaissance

Reconnaissance is the process of discovering and mapping the externally accessible attack surface of a target.

During a web application penetration test, reconnaissance helps identify domains, subdomains, applications, technologies, endpoints and other assets that may require further investigation.

The objective is not simply to collect information. The collected information should be transformed into an organised view of the attack surface that guides the rest of the assessment.

!!! warning "Authorised Security Testing"

    Perform reconnaissance only against systems that are within the authorised scope of the security assessment.

---

## Reconnaissance Workflow

A practical reconnaissance workflow can be organised as:

```text
Target Domain
      ↓
Passive Reconnaissance
      ↓
Subdomain Enumeration
      ↓
DNS Resolution
      ↓
HTTP Probing
      ↓
Technology Identification
      ↓
Content Discovery
      ↓
Crawling
      ↓
Historical URL Discovery
      ↓
Parameter Discovery
      ↓
JavaScript Analysis
      ↓
Attack Surface
```

The workflow is iterative. New domains, endpoints and technologies discovered during testing should be fed back into the reconnaissance process.

---

## Passive Reconnaissance

Passive reconnaissance gathers information without directly interacting with the target application where possible.

Useful sources may include:

* Search engines
* Certificate Transparency logs
* DNS information
* Public code repositories
* Internet archives
* Public documentation
* Search engine caches
* Publicly indexed files
* Historical URLs
* Internet-wide scanning databases

Passive reconnaissance can reveal assets that are difficult to discover through direct enumeration.

---

## Subdomain Enumeration

Subdomain enumeration expands the known attack surface beyond the primary domain.

For example:

```text
example.com
│
├── www.example.com
├── api.example.com
├── portal.example.com
├── login.example.com
├── dev.example.com
├── staging.example.com
└── admin.example.com
```

Subdomains may expose:

* Additional applications
* APIs
* Administrative interfaces
* Development environments
* Staging environments
* Legacy systems
* Third-party services

Multiple enumeration sources should normally be combined because individual tools and data sources may return different results.

[Subdomain Enumeration](subdomain-enumeration.md)

---

## DNS Resolution

Discovered hostnames should be validated through DNS resolution.

This separates potential hostnames from domains that currently resolve.

Useful information includes:

* A records
* AAAA records
* CNAME records
* MX records
* TXT records
* NS records

CNAME records are particularly useful for identifying externally hosted services and third-party infrastructure.

---

## HTTP Probing

A resolving hostname does not necessarily expose a web application.

HTTP probing can determine:

* Whether HTTP or HTTPS responds
* HTTP status code
* Page title
* Web server
* Redirect location
* Content type
* Technology information
* IP address

A reconnaissance pipeline may therefore follow:

```text
Enumerated Subdomains
        ↓
DNS Resolution
        ↓
HTTP Probing
        ↓
Live Web Applications
```

This creates a more useful list for subsequent web application testing.

---

## Technology Identification

Identifying the technologies used by an application helps determine which testing techniques may be relevant.

Look for:

* Web servers
* Programming languages
* Application frameworks
* Content management systems
* JavaScript frameworks
* Reverse proxies
* CDNs
* WAFs
* Authentication technologies
* API technologies
* Third-party libraries

Version information can also help identify outdated or unsupported components that require further investigation.

[Technology Identification](technology-identification.md)

---

## Content Discovery

Content discovery attempts to identify resources that may not be visible through normal application navigation.

Examples include:

```text
/admin/
/api/
/backup/
/debug/
/internal/
/old/
/uploads/
/swagger/
/robots.txt
/sitemap.xml
```

Interesting resources may include:

* Administrative interfaces
* APIs
* Backup files
* Configuration files
* Debug endpoints
* Development interfaces
* Documentation
* Source maps
* Temporary files
* Legacy functionality

[Content Discovery](content-discovery.md)

---

## Crawling

Crawling follows links and application references to build a more complete picture of the accessible application.

Crawlers may discover:

* URLs
* Parameters
* Forms
* JavaScript files
* API endpoints
* Static resources
* Hidden application routes

Crawling should complement content discovery rather than replace it.

---

## Historical URL Discovery

Historical data can reveal endpoints that are no longer linked from the current application.

Potential discoveries include:

* Legacy endpoints
* Old API versions
* Historical parameters
* Removed functionality
* Backup resources
* JavaScript files
* Previously exposed directories

Historical URLs should be validated before being treated as part of the current attack surface.

---

## Parameter Discovery

Parameters are particularly important because they represent locations where user-controlled data enters an application.

Sources include:

```text
GET parameters
POST parameters
JSON properties
XML elements
HTTP headers
Cookies
Path parameters
Multipart fields
WebSocket messages
```

Parameter names can also be discovered through:

* Crawling
* JavaScript
* Historical URLs
* API documentation
* HTML forms
* Automated parameter discovery

[Parameter Discovery](parameter-discovery.md)

---

## JavaScript Analysis

Modern applications frequently expose significant information through JavaScript.

JavaScript files can reveal:

* API endpoints
* Hidden routes
* Parameter names
* Internal URLs
* Feature flags
* Authentication logic
* Client-side access controls
* Third-party services
* Source maps
* Potential secrets

JavaScript analysis should therefore be part of the standard reconnaissance workflow.

[JavaScript Analysis](javascript-analysis.md)

---

## Building the Attack Surface

Reconnaissance results become more useful when they are organised into a structured attack surface.

For example:

```text
Target
│
├── Domains
│   ├── Main
│   ├── API
│   ├── Authentication
│   └── Development
│
├── Technologies
│   ├── Web Server
│   ├── Framework
│   ├── JavaScript
│   └── Infrastructure
│
├── Endpoints
│   ├── Public
│   ├── Authenticated
│   ├── Administrative
│   └── API
│
├── Input
│   ├── Parameters
│   ├── Headers
│   ├── Cookies
│   ├── Files
│   └── JSON / XML
│
└── Security Boundaries
    ├── Authentication
    ├── Authorisation
    ├── Roles
    └── Trust Relationships
```

This provides a foundation for the vulnerability testing phases that follow.

---

## Common Reconnaissance Tools

| Purpose | Tools |
| --- | --- |
| Subdomain enumeration | Subfinder, Amass, Assetfinder |
| DNS resolution | dnsx |
| HTTP probing | httpx |
| Crawling | Katana |
| Content discovery | ffuf, feroxbuster, dirsearch |
| Historical URLs | waybackurls, gau |
| Parameter discovery | ParamSpider, Arjun |
| Technology identification | Wappalyzer, WhatWeb |
| Vulnerability discovery | Nuclei |
| JavaScript analysis | LinkFinder, manual review |

No single tool provides complete coverage. Combining different data sources generally produces better results.

---

## Reconnaissance Output

At the end of reconnaissance, useful outputs may include:

```text
subdomains.txt
resolved-subdomains.txt
alive-hosts.txt
urls.txt
historical-urls.txt
parameters.txt
javascript-files.txt
technologies.txt
endpoints.txt
```

Keeping reconnaissance data organised makes it easier to reproduce the assessment and feed results into subsequent testing.

---

## Related Notes

* [Web Application Security](../index.md)
* [Web Application Testing Methodology](../methodology.md)
* [Web Application Pentesting Checklist](../checklist.md)
* [Subdomain Enumeration](subdomain-enumeration.md)
* [Technology Identification](technology-identification.md)
* [Content Discovery](content-discovery.md)
* [Parameter Discovery](parameter-discovery.md)
* [JavaScript Analysis](javascript-analysis.md)
