---
title: Red Team Reconnaissance
description: Reconnaissance methodology for authorised red team assessments, covering passive and active reconnaissance, attack surface discovery, domains, DNS, subdomains, certificates, IP space, ASN data, technologies, cloud assets, email infrastructure, identity exposure, public repositories, metadata, breach exposure, validation, evidence, OPSEC, and reporting.
---

# Red Team Reconnaissance

Reconnaissance is the process of collecting and analysing information about a target before and during an authorised red team assessment.

The objective is not simply to collect as much information as possible.

The objective is to transform external and internal observations into an accurate attack-surface model that supports the engagement objectives.

```text
Authorised Scope
      |
      v
Passive Reconnaissance
      |
      v
Asset Discovery
      |
      v
Active Validation
      |
      v
Technology Mapping
      |
      v
Identity Mapping
      |
      v
Attack Surface
      |
      v
Candidate Entry Points
      |
      v
Initial Access
```

Reconnaissance should answer:

```text
What does the organisation expose?

Which assets actually belong to the organisation?

Which systems are alive?

Which technologies are present?

Where are authentication boundaries?

Which identities are externally visible?

Which cloud and SaaS services are used?

Which assets are likely to be security-relevant?

Which observations justify further testing?
```

!!! warning "Authorised testing only"
    Passive discovery may reveal systems belonging to subsidiaries, suppliers, cloud providers, CDNs, SaaS platforms, or unrelated third parties. Discovery does not establish authorisation. Validate ownership and scope before performing active testing.


---

# Reconnaissance Objectives

Typical objectives include:

```text
Identify Internet-facing assets

Discover domains and subdomains

Identify IP ranges and network ownership

Map DNS infrastructure

Identify web applications

Identify remote-access services

Identify authentication portals

Identify externally exposed technologies

Identify cloud infrastructure

Identify public code repositories

Identify exposed documents and metadata

Identify publicly exposed identities

Identify email infrastructure

Identify candidate initial-access paths

Validate scope boundaries
```


---

# Reconnaissance Model

```text
                    ORGANISATION
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Domains          IPs          Identities
          |              |              |
          v              v              v
      Subdomains      Services       Accounts
          |              |              |
          +--------------+--------------+
                         |
                         v
                    Technologies
                         |
                         v
                    Applications
                         |
                         v
                Authentication Surface
                         |
                         v
                   Attack Surface
```


---

# Passive vs Active Reconnaissance

Reconnaissance can broadly be divided into:

```text
Passive Reconnaissance

Active Reconnaissance
```


---

# Passive Reconnaissance

Passive reconnaissance uses information available without directly interacting with the target application or system where practical.

Examples:

```text
Search engines

Certificate Transparency

Public DNS information

WHOIS/RDAP

Public code repositories

Public documents

Job advertisements

Company websites

Public cloud references

Internet archives

Public vulnerability information

Search-engine indexes
```


---

# Active Reconnaissance

Active reconnaissance directly interacts with target infrastructure.

Examples:

```text
DNS queries

HTTP requests

Port scanning

Service identification

TLS inspection

Content discovery

Technology fingerprinting

Application mapping
```

Active reconnaissance should only be performed against authorised targets.


---

# Reconnaissance Workflow

A practical workflow:

```text
Known Domain
    |
    v
Domain Intelligence
    |
    v
Subdomain Enumeration
    |
    v
DNS Resolution
    |
    v
Alive Host Validation
    |
    v
HTTP Probing
    |
    v
Technology Identification
    |
    v
Content Discovery
    |
    v
Authentication Mapping
    |
    v
Candidate Entry Points
```


---

# Create an Engagement Workspace

Keep reconnaissance data separated by engagement.

Example:

```bash
mkdir -p recon/{domains,dns,subdomains,hosts,http,ports,cloud,identities,repositories,evidence}
```

Example structure:

```text
recon/
├── domains/
├── dns/
├── subdomains/
├── hosts/
├── http/
├── ports/
├── cloud/
├── identities/
├── repositories/
└── evidence/
```


---

# Seed Information

Reconnaissance usually begins with known information.

Possible seeds:

```text
Primary domain

Known applications

Known IP addresses

Company name

Known subsidiaries

Cloud tenant

Known email domain

Known authentication portal
```

Example:

```text
example.com
```


---

# Maintain Scope Separately

Keep discovered assets separate from authorised assets.

Example:

```text
scope/
├── domains.txt
├── ips.txt
└── excluded.txt

recon/
└── discovered-assets.txt
```

Do not automatically copy every discovered asset into scope.


---

# Domain Reconnaissance

Start with the primary authorised domain.

Questions:

```text
Who controls the domain?

Which nameservers are authoritative?

Which mail providers are used?

Which TXT records exist?

Which subdomains are visible?

Which certificates reference the domain?

Which external services depend on the domain?
```


---

# Basic DNS Queries

A records:

```bash
dig A example.com
```

AAAA:

```bash
dig AAAA example.com
```

Nameservers:

```bash
dig NS example.com
```

Mail:

```bash
dig MX example.com
```

TXT:

```bash
dig TXT example.com
```

SOA:

```bash
dig SOA example.com
```


---

# Compact DNS Output

```bash
dig +short example.com
```

Nameservers:

```bash
dig +short NS example.com
```

Mail:

```bash
dig +short MX example.com
```


---

# DNS Reconnaissance Model

```text
                     Domain
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
        A             MX             NS
        |              |              |
        v              v              v
     Hosting         Email           DNS
        |
        v
      HTTP
```


---

# DNS TXT Records

TXT records can reveal information about:

```text
SPF

Domain verification

SaaS providers

Cloud services

Email security

Ownership verification
```

Query:

```bash
dig TXT example.com
```

Treat these as infrastructure clues rather than vulnerabilities by themselves.


---

# SPF

An SPF record may identify authorised mail infrastructure.

Example structure:

```text
v=spf1 include:... -all
```

Reviewing SPF can help identify:

```text
Mail providers

Third-party mailing services

SaaS dependencies
```


---

# DMARC

Query:

```bash
dig TXT _dmarc.example.com
```

DMARC information can help understand the organisation's email-security architecture.


---

# DKIM

DKIM selectors are provider-specific and should not be guessed aggressively without a reason.

If a selector is known from authorised email samples or documentation, query:

```bash
dig TXT selector._domainkey.example.com
```


---

# WHOIS and RDAP

Domain registration information may provide:

```text
Registrar

Registration dates

Nameservers

Registration status
```

Traditional query:

```bash
whois example.com
```

Modern registration data is increasingly provided through RDAP.

Registration data may be privacy protected.


---

# Certificate Transparency

Certificate Transparency logs are valuable for discovering hostnames associated with certificates.

Useful sources include:

[crt.sh](https://crt.sh/){ target="_blank" rel="noopener noreferrer" }

Search concept:

```text
%.example.com
```

Certificate data may reveal:

```text
vpn.example.com

mail.example.com

portal.example.com

api.example.com

legacy.example.com
```


---

# Certificate Discovery Limitations

A certificate hostname does not guarantee:

```text
The host still exists

The host is reachable

The organisation still owns it

The system is in scope
```

Treat certificate results as candidates.


---

# Subdomain Enumeration

Subdomain enumeration combines multiple data sources.

Useful tools include:

```text
Subfinder

Amass

Certificate Transparency

DNS data

Search engines

Historical sources
```


---

# Subfinder

[Subfinder](https://github.com/projectdiscovery/subfinder){ target="_blank" rel="noopener noreferrer" } performs passive subdomain discovery.

Basic usage:

```bash
subfinder -d example.com
```

Save results:

```bash
subfinder -d example.com -silent -o subfinder.txt
```


---

# Amass

[OWASP Amass](https://github.com/owasp-amass/amass){ target="_blank" rel="noopener noreferrer" } can be used for attack-surface discovery.

Passive enumeration:

```bash
amass enum -passive -d example.com
```

Save:

```bash
amass enum -passive -d example.com -o amass.txt
```


---

# Combine Enumeration Results

Example:

```bash
cat subfinder.txt amass.txt | sort -u > subdomains.txt
```

Count:

```bash
wc -l subdomains.txt
```


---

# Normalise Results

Remove empty lines:

```bash
sed '/^[[:space:]]*$/d' subdomains.txt | sort -u > subdomains-clean.txt
```

This produces a clean candidate list.


---

# Candidate vs Resolved vs Alive

Do not confuse:

```text
Discovered Subdomain
        |
        v
DNS Resolved
        |
        v
Network Reachable
        |
        v
HTTP Reachable
```

These represent different states.


---

# DNS Resolution

Use [dnsx](https://github.com/projectdiscovery/dnsx){ target="_blank" rel="noopener noreferrer" } to validate DNS candidates.

Example:

```bash
dnsx -l subdomains-clean.txt -silent
```

Save resolved names:

```bash
dnsx -l subdomains-clean.txt -silent -o resolved.txt
```


---

# Resolve with IP Information

```bash
dnsx -l subdomains-clean.txt -silent -a -resp
```

This can help map hostnames to addresses.


---

# HTTP Validation

Use [httpx](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" } to identify HTTP/HTTPS services.

Basic:

```bash
httpx -l resolved.txt -silent
```

Save:

```bash
httpx -l resolved.txt -silent -o alive-http.txt
```


---

# HTTP Metadata

A useful reconnaissance probe:

```bash
httpx -l resolved.txt -silent -status-code -title -tech-detect -ip
```

This may provide:

```text
URL

Status code

Page title

Technology

IP address
```


---

# Example

```text
https://portal.example.com [200] [Customer Portal] [nginx] [203.0.113.10]
https://vpn.example.com [302] [Login] [203.0.113.20]
https://old.example.com [404] [Not Found] [203.0.113.30]
```

A `404` host can still be relevant because the web service itself is alive.


---

# Redirects

Redirects can reveal:

```text
Canonical hostnames

Authentication systems

SSO providers

Application paths

External SaaS dependencies
```

Inspect:

```bash
curl -I https://example.com/
```


---

# HTTP Headers

Headers may reveal:

```text
Server software

Reverse proxies

CDNs

Authentication products

Frameworks

Security controls

Internal naming
```

Inspect:

```bash
curl -I https://example.com/
```

Do not assume a disclosed `Server` header is perfectly accurate.


---

# Technology Identification

Technology identification helps determine which testing methodology is relevant.

Useful tools:

```text
httpx

WhatWeb

Wappalyzer

Nuclei technology templates

Manual inspection
```


---

# WhatWeb

[WhatWeb](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }:

```bash
whatweb https://example.com
```


---

# Technology Mapping

Record technologies by asset.

Example:

| Asset | Technology | Confidence |
|---|---|---|
| `www.example.com` | nginx | High |
| `portal.example.com` | ASP.NET | High |
| `api.example.com` | Unknown API | Medium |
| `auth.example.com` | SSO portal | High |


---

# Technology Confidence

Useful levels:

```text
Low

Medium

High

Confirmed
```

Do not report technology fingerprinting as confirmed merely because one scanner guessed it.


---

# HTTP Screenshots

Screenshots can make large HTTP attack surfaces easier to review.

Useful tools include:

```text
EyeWitness

gowitness
```

Screenshots help identify:

```text
Login pages

Administrative interfaces

Default pages

Legacy applications

Error pages

Development environments

Duplicate applications
```


---

# gowitness

[gowitness](https://github.com/sensepost/gowitness){ target="_blank" rel="noopener noreferrer" } can capture web screenshots.

Review the project's current command syntax before using it because CLI options can change between releases.


---

# HTTP Attack Surface Categories

Classify discovered web assets.

Example:

```text
Corporate Website

Customer Portal

Employee Portal

VPN

SSO

API

Administrative Interface

Development

Testing

Staging

Legacy

File Transfer

Monitoring

Unknown
```


---

# Authentication Surface

Authentication endpoints deserve specific attention.

Look for:

```text
/login

/signin

/auth

/oauth

/saml

/oidc

/admin

/vpn

/remote

/password-reset
```

Do not assume these exact paths exist; identify them through normal application discovery.


---

# Authentication Inventory

Example:

| Asset | Authentication | MFA | Identity Provider |
|---|---|---|---|
| VPN | Username/password | Yes | Entra ID |
| Portal | SSO | Yes | Entra ID |
| Legacy App | Local account | Unknown | Local |
| API | Token | N/A | Application |


---

# Identity Provider Discovery

Common identity systems include:

```text
Microsoft Entra ID

Active Directory Federation Services

Okta

Ping Identity

Auth0

Google Workspace

Custom SAML/OIDC
```

Identity architecture often determines the most important attack surface.


---

# Microsoft Tenant Information

Public authentication behaviour may reveal whether an organisation uses Microsoft cloud identity.

Do not treat the existence of a Microsoft tenant as a vulnerability.

Record it as architecture information.


---

# Remote Access Surface

Look for externally exposed services such as:

```text
VPN

Remote Desktop gateways

VDI

Citrix

SSH

File transfer

Remote support

Web administration
```

These may represent important initial-access boundaries.


---

# Port Discovery

Port scanning is active reconnaissance and should only target authorised addresses.

A basic Nmap scan:

```bash
nmap -sT -Pn -T3 192.0.2.10
```

A targeted service scan:

```bash
nmap -sT -Pn -sV -p 22,80,443,445,3389 192.0.2.10
```

Use conservative timing appropriate to the Rules of Engagement.


---

# Why TCP Connect Scanning?

```text
-sT
```

uses the operating system's TCP connect mechanism.

It is useful when:

```text
Raw socket privileges are unavailable

Traffic is being routed through certain proxy mechanisms

A simple validation scan is sufficient
```


---

# Nmap Output

Save normal output:

```bash
nmap -sT -Pn -sV 192.0.2.10 -oN nmap.txt
```

XML:

```bash
nmap -sT -Pn -sV 192.0.2.10 -oX nmap.xml
```


---

# Port State Interpretation

Common states:

```text
open

closed

filtered
```

`filtered` does not necessarily mean the host is offline.

A firewall may be preventing a definitive response.


---

# Service Identification

Common Internet-facing services:

| Port | Typical Service |
|---:|---|
| 22 | SSH |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 445 | SMB |
| 587 | SMTP Submission |
| 993 | IMAPS |
| 3389 | RDP |

Ports are indicators, not proof of the application protocol.


---

# IP Address Reconnaissance

IP addresses can help identify:

```text
Hosting providers

Cloud infrastructure

CDNs

Dedicated infrastructure

Network ownership

Related assets
```


---

# ASN

An Autonomous System Number identifies a network participating in Internet routing.

ASN information may help determine whether an organisation operates its own address space.

Do not assume all addresses announced by an organisation's ASN are automatically authorised for testing.


---

# ASN Model

```text
Organisation
     |
     v
    ASN
     |
     v
IP Prefixes
     |
     v
Candidate Infrastructure
```


---

# IP Ownership

Differentiate:

```text
Organisation-owned IP

Cloud-hosted IP

CDN IP

SaaS IP

Third-party IP
```

This distinction is important for scope.


---

# CDN and Reverse Proxy

An application's DNS may point to:

```text
Cloudflare

Akamai

Fastly

CloudFront

Azure Front Door

Other reverse proxies
```

The visible edge address may not be the origin server.

Do not attempt to bypass a third-party edge service unless explicitly authorised.


---

# TLS Reconnaissance

Inspect a certificate:

```bash
openssl s_client -connect example.com:443 -servername example.com
```

Useful certificate fields include:

```text
Subject

Issuer

Validity

Subject Alternative Names
```


---

# TLS Certificate Information

A simpler certificate extraction:

```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```


---

# Subject Alternative Names

SANs may reveal additional names associated with the certificate.

Example:

```text
DNS:example.com
DNS:www.example.com
DNS:portal.example.com
```

Again, these are candidates rather than automatically authorised targets.


---

# Cloud Reconnaissance

Modern attack surfaces frequently extend into cloud environments.

Look for evidence of:

```text
AWS

Microsoft Azure

Google Cloud

Cloud storage

Cloud-hosted applications

Serverless services

Container registries

Cloud identity

CI/CD platforms
```


---

# Cloud Asset Classification

```text
Cloud Asset
    |
    +--> Compute
    |
    +--> Storage
    |
    +--> Identity
    |
    +--> Application
    |
    +--> API
    |
    +--> CI/CD
```


---

# Cloud Storage

Public references may identify storage services.

Examples:

```text
Amazon S3

Azure Blob Storage

Google Cloud Storage
```

Discovery does not justify accessing data outside the authorised scope.


---

# Cloud Metadata in Applications

Application code may reference:

```text
Storage names

API endpoints

Tenant IDs

Region names

Cloud resource names

CDN hostnames
```

These are useful for architecture mapping.


---

# Public Code Repositories

Search authorised public sources for repositories associated with the organisation.

Potential sources:

```text
GitHub

GitLab

Bitbucket

Public package registries
```


---

# Repository Reconnaissance

Look for:

```text
Domain references

API endpoints

Infrastructure configuration

Documentation

Cloud resource names

Email formats

Technology information

Accidentally committed secrets
```

Do not use discovered credentials against systems unless credential validation is explicitly authorised.


---

# GitHub Search

Useful search concepts include:

```text
"example.com"

org:example

"@example.com"
```

Search should focus on publicly available information.


---

# Repository Secret Exposure

Potential secret types include:

```text
API keys

Cloud credentials

Passwords

Private keys

Tokens

Database connection strings
```

If discovered during an authorised engagement:

```text
Preserve minimal evidence

Do not unnecessarily expose the secret

Do not commit it into notes

Follow the Rules of Engagement

Coordinate rotation where required
```


---

# Git History

A secret removed from the current branch may remain in repository history.

The security issue is therefore:

```text
Secret exposed in repository history
```

rather than merely:

```text
Secret in current file
```


---

# Public Documents

Publicly available documents can reveal useful architecture information.

Examples:

```text
PDF

DOCX

XLSX

PPTX
```

Potential information:

```text
Author names

Usernames

Software versions

Internal hostnames

File paths

Organisation names

Document templates
```


---

# Metadata Extraction

[ExifTool](https://exiftool.org/){ target="_blank" rel="noopener noreferrer" } can inspect metadata.

Example:

```bash
exiftool document.pdf
```

For multiple files:

```bash
exiftool documents/
```


---

# Metadata Interpretation

Metadata should be treated carefully.

A username in a document may be:

```text
Current employee

Former employee

External contractor

Template author

Generic build account
```

Validate before drawing conclusions.


---

# Identity Reconnaissance

Public information may reveal:

```text
Employee names

Job titles

Departments

Email formats

Technology teams

Administrators

Developers

Security personnel
```

Identity information can be sensitive even when publicly available.


---

# Identity Sources

Possible sources:

```text
Company website

Public professional profiles

Conference presentations

Public repositories

Public documents

Press releases

Job advertisements
```


---

# Email Format

Public addresses may reveal a naming convention.

Examples:

```text
firstname.lastname@example.com

firstinitiallastname@example.com

firstname@example.com
```

Do not automatically generate or test large account lists merely because a pattern is known.


---

# Username Validation

Username enumeration against authentication systems can trigger:

```text
Account lockouts

Security alerts

Rate limits

Privacy concerns
```

Only perform active account validation when explicitly permitted.


---

# Job Advertisements

Job advertisements can provide architecture clues.

Examples:

```text
Microsoft 365

Active Directory

AWS

Azure

Kubernetes

Citrix

VMware

CrowdStrike

Microsoft Defender

Splunk

Sentinel
```

This information helps build hypotheses but does not confirm deployment.


---

# Technology Confidence Example

```text
Job advertisement mentions Kubernetes
            |
            v
Possible Kubernetes Environment
            |
            v
Additional Evidence?
         /       \
       No         Yes
       |           |
       v           v
    Candidate    Higher Confidence
```


---

# Search Engines

Search engines can reveal indexed content such as:

```text
Subdomains

Documents

Login pages

Old applications

Public directories

Error messages
```

Use normal public search functionality within the engagement rules.


---

# Search Examples

Examples of search syntax:

```text
site:example.com

site:example.com filetype:pdf

site:example.com filetype:xlsx

site:example.com login
```

These queries search publicly indexed content.


---

# Internet Archive

Historical web data can reveal:

```text
Old endpoints

Previous applications

Historical paths

Retired technologies

Old documentation
```

Historical existence does not mean the system still exists.


---

# robots.txt

Review:

```bash
curl https://example.com/robots.txt
```

It may identify:

```text
Crawler exclusions

Application paths

Administrative paths

Legacy content
```

`robots.txt` is not an access-control mechanism.


---

# sitemap.xml

Review:

```bash
curl https://example.com/sitemap.xml
```

Sitemaps may reveal application structure.


---

# security.txt

Check:

```bash
curl https://example.com/.well-known/security.txt
```

This may provide:

```text
Security contact

Disclosure policy

Acknowledgement information
```


---

# Content Discovery

Once a web application is confirmed in scope, content discovery may identify:

```text
Directories

Files

APIs

Administrative interfaces

Backup files

Documentation

Hidden application paths
```

See:

[Content Discovery](../web/reconnaissance/content-discovery.md)


---

# Parameter Discovery

Parameters may reveal additional application functionality.

Sources include:

```text
HTML forms

JavaScript

Historical URLs

Application links

API documentation
```

See:

[Parameter Discovery](../web/reconnaissance/parameter-discovery.md)


---

# JavaScript Reconnaissance

JavaScript files can reveal:

```text
API routes

Internal application paths

Feature flags

Service names

Cloud endpoints

Authentication logic

Client-side configuration
```

See:

[JavaScript Analysis](../web/reconnaissance/javascript-analysis.md)


---

# API Discovery

Look for:

```text
/api/

/v1/

/v2/

/graphql

/swagger

/openapi
```

These are common conventions, not guaranteed paths.


---

# OpenAPI

An exposed OpenAPI specification can provide:

```text
Endpoints

Methods

Parameters

Authentication schemes

Schemas
```

The existence of API documentation is not automatically a vulnerability.


---

# GraphQL

GraphQL endpoints may provide a distinct application attack surface.

Common architecture:

```text
Client
  |
  v
GraphQL Endpoint
  |
  v
Resolvers
  |
  v
Backend Services
```

See:

[GraphQL](../web/graphql.md)


---

# Virtual Hosts

Multiple applications may share one address.

Concept:

```text
203.0.113.10
     |
     +--> www.example.com
     |
     +--> portal.example.com
     |
     +--> api.example.com
```

Hostname-based discovery can therefore reveal more than IP-only scanning.


---

# Development and Staging Systems

Look for naming patterns such as:

```text
dev

test

qa

uat

stage

staging

preprod

demo

old

legacy
```

Do not assume such systems have weaker security.

Validate configuration independently.


---

# Environment Classification

Example:

| Host | Environment | Confidence |
|---|---|---|
| `www.example.com` | Production | High |
| `dev.example.com` | Development | Medium |
| `uat.example.com` | UAT | High |
| `old.example.com` | Unknown/legacy | Medium |


---

# Forgotten Assets

Potential forgotten assets include:

```text
Old portals

Temporary applications

Legacy VPNs

Development systems

Deprecated APIs

Old DNS records

Unused cloud resources
```

These can be valuable reconnaissance findings because asset management is itself a security control.


---

# Dangling DNS

A DNS record may reference a resource that no longer exists.

Concept:

```text
sub.example.com
       |
       v
External Service
       |
       v
Resource Removed
```

This may represent a subdomain takeover candidate depending on the provider and exact configuration.

Do not claim takeover until safely confirmed according to scope.


---

# DNS Wildcards

Wildcard DNS can make every tested hostname appear to resolve.

Test random names:

```bash
dig +short random-name-that-should-not-exist.example.com
```

If arbitrary names resolve, account for wildcard behaviour when processing subdomain results.


---

# HTTP Wildcards

Applications may also respond identically to unknown hostnames or paths.

Compare:

```text
Status

Content length

Title

Response body

Redirect destination
```

before treating every response as a unique asset.


---

# Catch-All Authentication

Some identity providers deliberately return similar responses for valid and invalid accounts.

Do not infer account existence solely from one response difference.


---

# Vulnerability Intelligence

Once technologies are identified, research relevant vulnerabilities.

Sources include:

[NIST National Vulnerability Database](https://nvd.nist.gov/){ target="_blank" rel="noopener noreferrer" }

[CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog){ target="_blank" rel="noopener noreferrer" }

[GitHub Security Advisories](https://github.com/advisories){ target="_blank" rel="noopener noreferrer" }


---

# Version Matching

A version banner is not sufficient to confirm vulnerability.

Use:

```text
Observed Version
      |
      v
Affected Version?
      |
      v
Required Configuration?
      |
      v
Reachable Attack Surface?
      |
      v
Safe Validation
```


---

# Do Not Report CVEs from Version Strings Alone

Weak:

```text
nginx version X is vulnerable to CVE-XXXX-XXXX.
```

Better:

```text
The service disclosed a version potentially associated with
CVE-XXXX-XXXX. Exploitability was not confirmed during the
assessment.
```


---

# Automated Template Scanning

Tools such as [Nuclei](https://github.com/projectdiscovery/nuclei){ target="_blank" rel="noopener noreferrer" } can assist with authorised attack-surface validation.

Example against one authorised target:

```bash
nuclei -u https://example.com
```

For a target list:

```bash
nuclei -l alive-http.txt
```

Use appropriate rate limits and template selection for the environment.


---

# Nuclei Results

Treat automated results as:

```text
Candidate Finding
       |
       v
Manual Review
       |
       v
Safe Validation
       |
       v
Confirmed / Rejected
```


---

# Rate Limiting

Reconnaissance tools can generate substantial traffic.

Consider:

```text
Application capacity

WAF thresholds

IDS/IPS

Rate limits

Customer monitoring

Testing window

Rules of Engagement
```

Start conservatively.


---

# OPSEC

Reconnaissance itself generates observable activity.

Defenders may observe:

```text
DNS queries

Sequential connections

HTTP requests

TLS handshakes

Port scans

Directory discovery

Repeated user agents
```

Do not attempt to conceal activity outside the engagement requirements.

Maintain enough logging for deconfliction.


---

# Source Infrastructure

Track which infrastructure performs active reconnaissance.

Example:

| Source | Purpose |
|---|---|
| RT01 | HTTP reconnaissance |
| RT02 | Approved scanning |
| Operator VPN | Manual validation |


---

# Deconfliction

Provide assessment indicators when required:

```text
Source IP addresses

Domains

Testing windows

Operator identifiers

Known payload hashes
```

This helps distinguish authorised reconnaissance from unrelated malicious activity.


---

# Evidence

Reconnaissance evidence may include:

```text
DNS results

Certificate data

HTTP headers

Screenshots

Service banners

Technology fingerprints

Port results

Public repository references

Public document metadata
```


---

# Evidence Record

Example:

```text
Evidence ID:
RECON-014

Asset:
portal.example.com

Source:
Certificate Transparency + DNS validation

Resolution:
203.0.113.10

HTTP:
HTTPS 200

Title:
Customer Portal

Technology:
ASP.NET

Status:
Confirmed active asset

Scope:
Confirmed in scope
```


---

# Asset Inventory

Maintain a central inventory.

Example:

| Asset | Type | IP | Status | Scope | Notes |
|---|---|---|---|---|---|
| `www.example.com` | Web | `203.0.113.10` | Alive | Yes | Corporate |
| `portal.example.com` | Web | `203.0.113.20` | Alive | Yes | Login |
| `legacy.example.com` | Web | `203.0.113.30` | Alive | Pending | Ownership review |
| `cdn.example.com` | CDN | Third party | Alive | No | Provider |


---

# Scope Status

Useful states:

```text
In Scope

Out of Scope

Pending Validation

Third Party

Unknown
```


---

# Asset Status

Useful states:

```text
Discovered

Resolved

Reachable

HTTP Alive

Validated

Retired

Unknown
```


---

# Confidence

Track confidence separately from status.

```text
Low

Medium

High

Confirmed
```


---

# Reconnaissance Database Model

Conceptually:

```text
Asset
 |
 +--> Domain
 |
 +--> IP
 |
 +--> DNS
 |
 +--> Port
 |
 +--> Service
 |
 +--> Technology
 |
 +--> Environment
 |
 +--> Authentication
 |
 +--> Owner
 |
 +--> Scope
 |
 +--> Evidence
```


---

# Deduplication

Multiple sources may identify the same asset.

```text
Subfinder ----+
              |
Amass --------+--> portal.example.com
              |
CT Logs ------+
```

Deduplicate before later processing.


---

# Example Pipeline

For an authorised domain:

```bash
subfinder -d example.com -silent -o subfinder.txt
```

```bash
amass enum -passive -d example.com -o amass.txt
```

Combine:

```bash
cat subfinder.txt amass.txt | sort -u > subdomains.txt
```

Resolve:

```bash
dnsx -l subdomains.txt -silent -o resolved.txt
```

Probe HTTP:

```bash
httpx -l resolved.txt -silent -status-code -title -tech-detect -ip -o http.txt
```

This produces a useful first-pass HTTP attack-surface inventory.


---

# Pipeline Model

```text
              Primary Domain
                    |
          +---------+---------+
          |                   |
          v                   v
      Subfinder             Amass
          |                   |
          +---------+---------+
                    |
                    v
                  sort -u
                    |
                    v
                   dnsx
                    |
                    v
                  httpx
                    |
                    v
            Alive HTTP Assets
                    |
                    v
             Manual Validation
```


---

# Keep Raw Data

Do not overwrite raw discovery results.

Prefer:

```text
raw/
processed/
validated/
```

Example:

```text
recon/
├── raw/
├── processed/
└── validated/
```


---

# Why Keep Raw Results?

Raw data helps with:

```text
Troubleshooting

Reprocessing

Evidence

Tool comparison

False-positive analysis

Reproducibility
```


---

# Reconnaissance Automation

Automation is useful for:

```text
Collection

Deduplication

DNS resolution

HTTP probing

Metadata enrichment
```

Manual analysis remains necessary for:

```text
Ownership

Scope

Context

Security relevance

False positives

Attack-path decisions
```


---

# Automation Model

```text
Automation
    |
    v
Candidates
    |
    v
Human Review
    |
    v
Validated Assets
    |
    v
Testing Decisions
```


---

# Reconnaissance Prioritisation

Not every asset deserves equal attention.

Prioritise based on:

```text
Authentication

Internet exposure

Administrative functionality

Legacy technology

Sensitive business function

Remote access

Development status

Interesting technology

Known vulnerabilities

Weak segmentation

Cloud identity integration
```


---

# Example Prioritisation

```text
                Discovered Asset
                       |
                       v
                Authentication?
                  /          \
                No            Yes
                |              |
                v              v
           Normal Review    Higher Priority
                               |
                               v
                        Remote Access?
                          /        \
                        No          Yes
                        |            |
                        v            v
                     Review      High Priority
```


---

# Candidate Initial Access Paths

Reconnaissance may identify candidates such as:

```text
Internet-facing application

VPN

SSO portal

Remote access gateway

Public API

Cloud application

Exposed development system

Credential exposure

Public repository secret

Known vulnerable service
```

These remain candidates until validated.


---

# Reconnaissance Is Not Exploitation

Maintain a boundary:

```text
Reconnaissance
      |
      v
Candidate
      |
      v
Hypothesis
      |
      v
Authorisation Check
      |
      v
Initial Access Testing
```

See:

[Initial Access](initial-access.md)


---

# Reconnaissance and Infrastructure

Red team infrastructure should be prepared before active reconnaissance.

See:

[Infrastructure](infrastructure.md)

Track:

```text
Source IPs

DNS

VPN

Operator identities

Logs

Testing windows
```


---

# Reconnaissance and OPSEC

See:

[Red Team OPSEC](opsec.md)

Important considerations:

```text
Correct engagement

Correct source infrastructure

Correct target

Scope validation

Logging

Evidence protection

Third-party boundaries
```


---

# Reconnaissance and Reporting

Reconnaissance findings should support later attack-path analysis.

See:

[Red Team Reporting](reporting.md)


---

# Reporting Reconnaissance Findings

Potential reportable issues include:

```text
Unknown Internet-facing assets

Legacy systems

Exposed administrative interfaces

Sensitive metadata

Public credential exposure

Dangling DNS

Unexpected cloud resources

Excessive technology disclosure
```

Not every reconnaissance observation is a vulnerability.


---

# Example Finding

```text
Title:
Unmanaged Internet-Facing Application Identified

Observation:
An externally reachable application was discovered through
Certificate Transparency and confirmed through DNS and HTTPS.

The asset was not present in the customer-provided Internet asset
inventory.

Impact:
Unknown or unmanaged Internet-facing systems may fall outside
normal vulnerability management, monitoring, and patching
processes.

Recommendation:
Validate ownership, assign an asset owner, include the system in
the central asset inventory, and ensure vulnerability management
and monitoring controls apply.
```


---

# Candidate vs Confirmed

Use clear states.

```text
Candidate

Validated Asset

Confirmed Finding
```


---

# Example

```text
Certificate Transparency hostname
          |
          v
       Candidate
          |
          v
    DNS Resolution
          |
          v
    Validated Asset
          |
          v
Configuration Review
          |
          v
    Confirmed Finding
```


---

# Common Reconnaissance Mistakes

## Assuming Every Subdomain Is Alive

Discovery does not equal reachability.

Validate DNS and service state.


---

## Assuming Every IP Is Owned by the Customer

Cloud and CDN addresses may be shared or third-party controlled.


---

## Treating Technology Detection as Proof

Fingerprinting tools can be wrong.


---

## Treating Version Detection as Vulnerability Confirmation

Version matching is only one prerequisite.


---

## Ignoring Redirects

A redirect may reveal the real authentication or application endpoint.


---

## Ignoring Non-200 Responses

Interesting systems may return:

```text
301

302

401

403

404

500
```

A non-200 response does not mean the service is irrelevant.


---

## Ignoring DNS

DNS frequently provides some of the most valuable attack-surface context.


---

## Ignoring Authentication

Authentication surfaces often matter more than static corporate websites.


---

## Ignoring Third Parties

Testing a discovered third-party asset without authorisation creates unnecessary risk.


---

## Collecting Without Analysing

Thousands of subdomains are not useful unless they are:

```text
Resolved

Classified

Scoped

Prioritised

Analysed
```


---

# Reconnaissance Checklist

## Scope

- [ ] Primary domain confirmed
- [ ] Additional domains confirmed
- [ ] IP scope documented
- [ ] Exclusions documented
- [ ] Third-party restrictions understood
- [ ] Active reconnaissance authorised
- [ ] Source infrastructure documented

## Domains

- [ ] WHOIS/RDAP reviewed
- [ ] Nameservers identified
- [ ] A records reviewed
- [ ] AAAA records reviewed
- [ ] MX records reviewed
- [ ] TXT records reviewed
- [ ] SPF reviewed
- [ ] DMARC reviewed
- [ ] Certificate Transparency reviewed

## Subdomains

- [ ] Passive enumeration completed
- [ ] Subfinder results collected
- [ ] Amass results collected
- [ ] Results combined
- [ ] Results deduplicated
- [ ] Wildcard DNS checked
- [ ] DNS resolution performed
- [ ] Scope validated

## HTTP

- [ ] HTTP/HTTPS assets probed
- [ ] Status codes recorded
- [ ] Titles recorded
- [ ] IPs recorded
- [ ] Technologies recorded
- [ ] Redirects reviewed
- [ ] Authentication portals identified
- [ ] Interesting non-200 responses reviewed
- [ ] Screenshots captured where useful

## Network

- [ ] Authorised IPs identified
- [ ] Network ownership reviewed
- [ ] Cloud/CDN addresses identified
- [ ] Approved port discovery completed
- [ ] Services classified
- [ ] Remote-access services identified

## Technology

- [ ] Web technologies identified
- [ ] Frameworks identified where possible
- [ ] Server software identified where possible
- [ ] Cloud providers identified
- [ ] Authentication providers identified
- [ ] Confidence recorded
- [ ] Relevant vulnerability intelligence reviewed

## Public Information

- [ ] Public repositories reviewed
- [ ] Public documents reviewed
- [ ] Metadata reviewed
- [ ] Job advertisements reviewed where relevant
- [ ] Public identity information reviewed
- [ ] Search-engine results reviewed
- [ ] Historical web information reviewed where useful

## Cloud

- [ ] Cloud providers identified
- [ ] Storage references identified
- [ ] Cloud application endpoints recorded
- [ ] Tenant information recorded where appropriate
- [ ] CI/CD references reviewed
- [ ] Third-party boundaries maintained

## Evidence

- [ ] Asset inventory maintained
- [ ] Evidence IDs assigned
- [ ] Raw results retained
- [ ] Processed results separated
- [ ] Scope status recorded
- [ ] Confidence recorded
- [ ] Candidate findings manually reviewed


---

# Quick Reconnaissance Commands

## DNS

```bash
dig A example.com
dig AAAA example.com
dig NS example.com
dig MX example.com
dig TXT example.com
dig TXT _dmarc.example.com
```


## WHOIS

```bash
whois example.com
```


## Subfinder

```bash
subfinder -d example.com -silent -o subfinder.txt
```


## Amass

```bash
amass enum -passive -d example.com -o amass.txt
```


## Combine

```bash
cat subfinder.txt amass.txt | sort -u > subdomains.txt
```


## DNS Resolution

```bash
dnsx -l subdomains.txt -silent -o resolved.txt
```


## HTTP Probe

```bash
httpx -l resolved.txt -silent -status-code -title -tech-detect -ip -o http.txt
```


## HTTP Headers

```bash
curl -I https://example.com/
```


## robots.txt

```bash
curl https://example.com/robots.txt
```


## security.txt

```bash
curl https://example.com/.well-known/security.txt
```


## TLS

```bash
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -noout -subject -issuer -dates
```


## Technology

```bash
whatweb https://example.com
```


## Metadata

```bash
exiftool document.pdf
```


## Nmap

```bash
nmap -sT -Pn -sV -p 22,80,443,445,3389 192.0.2.10
```


---

# Reconnaissance Decision Model

```text
                    Discovered Asset
                           |
                           v
                       In Scope?
                      /        \
                    No          Yes
                    |            |
                   STOP          v
                           Ownership Clear?
                             /       \
                           No         Yes
                           |           |
                       Validate        v
                               DNS Resolves?
                                /      \
                              No        Yes
                              |          |
                           Record        v
                                  Service Alive?
                                   /       \
                                 No         Yes
                                 |           |
                              Record         v
                                      Classify Asset
                                             |
                                             v
                                      Authentication?
                                       /         \
                                     No           Yes
                                     |             |
                                     v             v
                                  Review       Prioritise
                                     |             |
                                     +------+------+
                                            |
                                            v
                                    Candidate Path
                                            |
                                            v
                                   Initial Access
```


---

# Reconnaissance Data Model

```text
                        DOMAIN
                           |
            +--------------+--------------+
            |              |              |
            v              v              v
        SUBDOMAIN         DNS         CERTIFICATE
            |              |              |
            +--------------+--------------+
                           |
                           v
                          IP
                           |
                           v
                        SERVICE
                           |
                           v
                      TECHNOLOGY
                           |
                           v
                      APPLICATION
                           |
            +--------------+--------------+
            |                             |
            v                             v
      AUTHENTICATION                  PUBLIC DATA
            |                             |
            v                             v
        IDENTITY                     REPOSITORY
            |                             |
            +--------------+--------------+
                           |
                           v
                     ATTACK SURFACE
                           |
                           v
                    INITIAL ACCESS
```


---

# Final Reconnaissance Model

```text
                    AUTHORISED SCOPE
                          |
                          v
                       SEEDS
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       DOMAINS            IPS          IDENTITY
          |               |               |
          v               v               v
     SUBDOMAINS        SERVICES       PUBLIC DATA
          |               |               |
          +---------------+---------------+
                          |
                          v
                     VALIDATION
                          |
                          v
                    CLASSIFICATION
                          |
                          v
                   SCOPE CHECK
                          |
                          v
                  PRIORITISATION
                          |
                          v
                  ATTACK SURFACE
                          |
                          v
                 ATTACK HYPOTHESIS
                          |
                          v
                   INITIAL ACCESS
```


---

# Core Principle

Reconnaissance can be reduced to:

```text
Start with known authorised assets.

Collect passive information.

Discover candidate assets.

Resolve and validate them.

Identify live services.

Map technologies.

Map authentication.

Understand identity and cloud dependencies.

Separate customer assets from third parties.

Record confidence.

Prioritise security-relevant systems.

Preserve evidence.

Turn observations into attack hypotheses.

Revalidate scope before active testing.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)
- [Web Reconnaissance](../web/reconnaissance/)
- [Subdomain Enumeration](../web/reconnaissance/subdomain-enumeration.md)
- [Technology Identification](../web/reconnaissance/technology-identification.md)
- [Content Discovery](../web/reconnaissance/content-discovery.md)
- [Parameter Discovery](../web/reconnaissance/parameter-discovery.md)
- [JavaScript Analysis](../web/reconnaissance/javascript-analysis.md)


---

# References

- [MITRE ATT&CK - Reconnaissance](https://attack.mitre.org/tactics/TA0043/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Search Open Websites/Domains](https://attack.mitre.org/techniques/T1593/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Search Open Technical Databases](https://attack.mitre.org/techniques/T1596/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Search Victim-Owned Websites](https://attack.mitre.org/techniques/T1594/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Gather Victim Host Information](https://attack.mitre.org/techniques/T1592/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Gather Victim Network Information](https://attack.mitre.org/techniques/T1590/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Gather Victim Identity Information](https://attack.mitre.org/techniques/T1589/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Amass](https://github.com/owasp-amass/amass){ target="_blank" rel="noopener noreferrer" }
- [ProjectDiscovery Subfinder](https://github.com/projectdiscovery/subfinder){ target="_blank" rel="noopener noreferrer" }
- [ProjectDiscovery dnsx](https://github.com/projectdiscovery/dnsx){ target="_blank" rel="noopener noreferrer" }
- [ProjectDiscovery httpx](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }
- [ProjectDiscovery Nuclei](https://github.com/projectdiscovery/nuclei){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }
- [crt.sh](https://crt.sh/){ target="_blank" rel="noopener noreferrer" }
- [Certificate Transparency](https://certificate.transparency.dev/){ target="_blank" rel="noopener noreferrer" }
- [WhatWeb](https://github.com/urbanadventurer/WhatWeb){ target="_blank" rel="noopener noreferrer" }
- [ExifTool](https://exiftool.org/){ target="_blank" rel="noopener noreferrer" }
- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog){ target="_blank" rel="noopener noreferrer" }
- [NIST National Vulnerability Database](https://nvd.nist.gov/){ target="_blank" rel="noopener noreferrer" }
- [GitHub Security Advisories](https://github.com/advisories){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Reconnaissance should produce decisions"
    A list containing thousands of hostnames is not yet useful reconnaissance. The value comes from resolving, validating, classifying, scoping, enriching, and prioritising those assets until they form an understandable attack surface that can guide the next phase of the assessment.


!!! warning "Discovery does not equal permission"
    Certificate Transparency, DNS, search engines, repositories, ASN information, and cloud metadata can reveal infrastructure beyond the authorised target. Treat newly discovered assets as candidates until ownership and scope have been confirmed. Do not actively test third-party or uncertain infrastructure merely because it appears related to the organisation.
