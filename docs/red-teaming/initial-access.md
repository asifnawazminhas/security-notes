---
title: Initial Access
description: Initial access methodology for authorised red team assessments, covering attack surface analysis, exposed applications, remote services, credentials, cloud identities, phishing considerations, delivery infrastructure, validation, detection, evidence, and remediation.
---

# Initial Access

Initial access is the stage of a red team assessment where an authorised tester establishes the first controlled foothold in the target environment.

The objective is not simply to obtain execution.

Initial access should answer questions such as:

```text
Which external security boundary was crossed?
What weakness or trust relationship enabled access?
Which identity or system was affected?
What privilege level was obtained?
Which defensive controls observed the activity?
Was the activity detected?
What business systems became reachable?
```

A simplified model is:

```text
Reconnaissance
      |
      v
Attack Surface
      |
      v
Candidate Entry Point
      |
      v
Validate
      |
      v
Initial Access
      |
      v
Establish Context
      |
      v
Controlled Foothold
```

Initial access techniques must remain within the approved scope and Rules of Engagement.


---

# Initial Access Objectives

The purpose of initial access depends on the engagement.

Potential objectives include:

```text
Obtain access to a test workstation
Authenticate to an exposed service
Establish access to a web application
Access an approved cloud identity
Reach a controlled internal system
Evaluate phishing controls
Evaluate remote-access controls
Evaluate external application security
Measure detection and response
```

Initial access should normally stop once sufficient access has been obtained to continue the agreed attack path.


---

# Initial Access Model

A useful methodology is:

```text
External Attack Surface
         |
         v
Identify Entry Points
         |
         +--> Web Applications
         |
         +--> Remote Services
         |
         +--> Identity
         |
         +--> Cloud
         |
         +--> Email
         |
         +--> VPN
         |
         +--> Third Parties
         |
         v
Prioritise
         |
         v
Validate
         |
         v
Initial Foothold
         |
         v
Document
```


---

# Before Testing

Before attempting initial access, confirm:

```text
Written authorisation
Target scope
Permitted techniques
Testing window
Source infrastructure
Credential-use rules
Social-engineering permissions
Payload restrictions
Data-access restrictions
Third-party exclusions
Availability restrictions
Emergency contacts
Stop conditions
```

Do not infer authorisation from a system being internet accessible.


---

# Attack Surface Mapping

Initial access begins with understanding the external attack surface.

Potential assets include:

```text
Domains
Subdomains
IP addresses
Web applications
APIs
VPN gateways
Remote desktop gateways
SSH services
Email infrastructure
Identity providers
Cloud services
Administrative portals
File-transfer services
Developer portals
CI/CD systems
Third-party integrations
```

The objective is to transform raw reconnaissance into candidate entry points.


---

# Attack Surface Workflow

```text
Domains
   |
   v
Subdomains
   |
   v
Resolve DNS
   |
   v
Identify Live Services
   |
   v
Fingerprint Technology
   |
   v
Identify Authentication
   |
   v
Prioritise Entry Points
```


---

# Domain Discovery

Start with the authorised root domains.

Examples:

```text
example.com
example.nl
example.org
```

Potential sources for subdomain discovery include:

```text
Certificate transparency
DNS records
Search engines
Public repositories
Passive DNS
Internet datasets
Cloud references
Organisation documentation
```

Subdomain enumeration should be covered in the dedicated reconnaissance notes where applicable.


---

# DNS Resolution

Resolve discovered names before deeper testing.

Examples:

```bash
dig +short portal.example.com
```

```bash
host portal.example.com
```

```bash
nslookup portal.example.com
```

Record the relationship:

```text
Hostname
   |
   v
IP Address
   |
   v
Hosting Provider / ASN
   |
   v
Observed Service
```


---

# HTTP Probing

For an authorised list of discovered hosts, HTTP probing can identify reachable web services.

Useful information includes:

```text
URL
Status code
Page title
Technology
Web server
Redirect
TLS
IP address
```

A typical ProjectDiscovery workflow can use `httpx`.

Example:

```bash
httpx -l subdomains.txt -title -tech-detect -status-code
```

Save results where required:

```bash
httpx -l subdomains.txt -title -tech-detect -status-code -o httpx-results.txt
```

Review results rather than treating every responsive host equally.


---

# Technology Identification

Technology identification helps prioritise testing.

Potential technologies include:

```text
IIS
Nginx
Apache
Tomcat
Next.js
WordPress
SharePoint
Exchange
Citrix
Fortinet
Palo Alto
VMware
Jenkins
GitLab
Grafana
Kibana
Custom applications
```

Useful tools can include:

```text
httpx
WhatWeb
Wappalyzer
Nmap
Manual inspection
```

Example:

```bash
whatweb https://portal.example.com
```

Technology detection is a starting point, not proof of vulnerability.


---

# Authentication Surface

Identify which external services require authentication.

Examples:

```text
VPN
SSO
Microsoft 365
Citrix
RDP gateway
Webmail
Administrative portals
Developer portals
Cloud consoles
Git services
File-transfer services
```

For each authentication surface, record:

```text
Authentication method
MFA
SSO provider
Username format
Password policy observations
Rate limiting
Lockout behaviour
Federation
External identity support
```


---

# Initial Access Categories

Initial access can broadly originate from:

```text
Application Weakness
Credential Access
Remote Service
Cloud Identity
Misconfiguration
Approved Social Engineering
Approved Physical Access
Third-Party Trust
Supply-Chain Scenario
```

The exact categories tested depend on the engagement.


---

# External Web Applications

Internet-facing applications are common initial access surfaces.

Testing may identify weaknesses involving:

```text
Authentication
Authorisation
File upload
Command injection
Deserialization
Server-side request forgery
SQL injection
Path traversal
File inclusion
Business logic
API security
Known vulnerable components
Administrative functionality
```

Use the dedicated web application security notes for detailed testing.

[Web Application Security](../web/)


---

# Application Initial Access Model

```text
External Application
        |
        v
Identify Weakness
        |
        v
Validate Impact
        |
        v
Does It Cross a Security Boundary?
        |
       Yes
        |
        v
Controlled Access
        |
        v
Establish Context
```

Do not unnecessarily escalate a web vulnerability into operating-system access when the engagement objective has already been met.


---

# Known Vulnerabilities

Exposed software should be checked against known security issues where relevant.

A responsible workflow is:

```text
Identify Product
      |
      v
Identify Version
      |
      v
Verify Configuration
      |
      v
Research Advisory
      |
      v
Check Preconditions
      |
      v
Validate Safely
```

Do not rely solely on version banners.

Backported patches and vendor-specific builds can invalidate simple version comparisons.


---

# Vulnerability Research Sources

Useful sources include:

```text
Vendor advisories
NVD
CISA Known Exploited Vulnerabilities Catalog
GitHub Security Advisories
Project repositories
Security research publications
```

Prefer primary vendor information when determining whether a particular version or configuration is affected.


---

# Remote Services

Externally exposed remote services can provide initial access where valid credentials or an authorised vulnerability are available.

Examples include:

```text
VPN
SSH
RDP
Remote Desktop Gateway
Citrix
WinRM
SMB
VNC
Administrative web interfaces
File-transfer services
```

Exposure alone is not automatically a vulnerability.


---

# Remote Service Assessment

For each service:

```text
Identify Service
      |
      v
Identify Version
      |
      v
Identify Authentication
      |
      v
Identify MFA
      |
      v
Check Configuration
      |
      v
Check Known Vulnerabilities
      |
      v
Assess Credential Risk
```


---

# SSH

SSH may be externally exposed for legitimate administration.

Identify:

```text
Version
Authentication methods
Password authentication
Public-key authentication
Source restrictions
MFA
Rate limiting
Administrative accounts
```

Basic service identification:

```bash
nmap -sV -p 22 TARGET
```

Do not perform password guessing unless explicitly authorised.


---

# RDP

RDP exposure should be evaluated in context.

Potential considerations include:

```text
Internet exposure
Network Level Authentication
MFA
RD Gateway
Account lockout
Administrative access
Source restrictions
Version and patching
```

Basic service identification:

```bash
nmap -sV -p 3389 TARGET
```

Direct internet exposure can increase attack surface, but the final finding should reflect the actual controls present.


---

# VPN

VPN gateways are important initial access surfaces because successful authentication may provide internal network access.

Assess:

```text
Product
Version
Authentication
MFA
Certificate requirements
Account lockout
Conditional access
Device compliance
Split tunnelling
Accessible networks
```

A valid credential without MFA can have significantly different impact from the same credential protected by strong MFA and device controls.


---

# File Transfer Services

Externally accessible file-transfer infrastructure may include:

```text
SFTP
FTPS
Managed File Transfer
Web-based upload portals
Vendor file-transfer products
```

Assess:

```text
Authentication
Anonymous access
Version
Administrative interfaces
Upload controls
Access boundaries
Known vulnerabilities
```


---

# Credential-Based Initial Access

Valid credentials may provide initial access without exploiting a software vulnerability.

Potential sources during an authorised assessment include:

```text
Customer-provided test credentials
Credentials discovered during approved testing
Approved password-spray results
Previously compromised test identities
Configuration exposure
Approved credential reuse scenarios
```

Credential handling should follow the Rules of Engagement.


---

# Password Spraying

Password spraying tests whether a small number of candidate passwords work across multiple accounts.

It differs from traditional brute force:

```text
Brute Force

One Account
    |
    +--> Password 1
    +--> Password 2
    +--> Password 3
    +--> Password 4


Password Spray

Password 1
    |
    +--> User A
    +--> User B
    +--> User C
    +--> User D
```

Password spraying can lock accounts or trigger defensive controls.

It should only be performed when explicitly authorised.


---

# Password Spray Planning

Before an approved spray, understand:

```text
Account lockout threshold
Lockout duration
Authentication provider
MFA
Conditional access
Excluded accounts
Testing window
Maximum attempts
Monitoring requirements
Emergency stop procedure
```

Do not guess safe spray rates without understanding the target policy.


---

# Username Enumeration

Authentication systems may expose whether an account exists through differences in:

```text
Error messages
HTTP status
Response size
Response timing
Password-reset workflow
Registration workflow
SSO behaviour
```

Where observed, determine whether the difference provides meaningful security impact.


---

# Multi-Factor Authentication

MFA significantly changes the initial access model.

```text
Password
   |
   v
Correct
   |
   v
MFA
   |
   +--> Failed --> Access Denied
   |
   +--> Passed --> Access Granted
```

Assess the actual MFA implementation rather than simply recording that MFA exists.


---

# MFA Considerations

Potential areas include:

```text
Coverage
Enrolment
Recovery
Legacy authentication
Trusted devices
Conditional access
Session lifetime
Remembered sessions
Administrative accounts
Break-glass accounts
```

MFA testing should remain within explicitly authorised scenarios.


---

# Identity Provider

Common identity platforms can include:

```text
Microsoft Entra ID
Active Directory Federation Services
Okta
Ping Identity
Google Workspace
Custom SAML providers
OIDC providers
```

Identity architecture can become a central initial access boundary.


---

# SSO

Single sign-on can connect one authentication event to many applications.

```text
Identity Provider
       |
       +--> Application A
       |
       +--> Application B
       |
       +--> Application C
       |
       +--> VPN
```

Compromise of one identity may therefore have broader impact than compromise of a standalone application account.


---

# Cloud Initial Access

Cloud environments introduce additional initial access surfaces.

Potential examples include:

```text
Cloud console
Cloud API
Access keys
Service principals
Application registrations
Federated identities
CI/CD secrets
Storage credentials
Managed identities
Developer credentials
```

Cloud access should be tested against the explicitly authorised tenant and subscriptions/accounts.


---

# Cloud Credential Exposure

Potential credential locations may include:

```text
Public repositories
CI/CD configuration
Environment files
Application configuration
Developer workstations
Shell history
Deployment scripts
Infrastructure-as-code files
```

If credentials are discovered, first determine:

```text
Which tenant/account do they belong to?
Are they still valid?
What permissions do they have?
Is validation authorised?
```

Do not use discovered credentials against unrelated environments.


---

# Public Repositories

Public repositories can unintentionally expose security-sensitive information.

Review authorised organisational repositories for:

```text
API keys
Tokens
Passwords
Connection strings
Internal hostnames
Cloud identifiers
Deployment scripts
Private endpoints
Configuration files
Historical secrets
```

Secret scanning should include repository history where appropriate.


---

# Secret Validation

A discovered secret should not automatically be used.

Use:

```text
Secret Found
    |
    v
Identify Owner
    |
    v
Identify Scope
    |
    v
Confirm Validation Is Authorised
    |
   Yes
    |
    v
Minimal Validation
    |
    v
Document
```

Avoid accessing unnecessary data after proving the credential is valid.


---

# Email as an Initial Access Surface

Email infrastructure may be relevant when social engineering is explicitly authorised.

Potential assessment areas include:

```text
Phishing resilience
Attachment controls
URL filtering
Authentication
MFA
Email gateway detection
User reporting
Security awareness
Incident response
```

Social engineering requires explicit Rules of Engagement because it involves human participants.


---

# Phishing

A phishing simulation should have a defined objective.

Examples:

```text
Measure delivery
Measure link interaction
Measure credential submission to a synthetic portal
Measure attachment blocking
Measure user reporting
Measure SOC response
```

Avoid collecting real passwords where synthetic validation can achieve the same objective.


---

# Phishing Safety

A controlled phishing exercise should define:

```text
Target population
Excluded users
Approved pretext
Approved sender infrastructure
Permitted attachment types
Permitted links
Credential-handling policy
Testing window
Emergency contact
Data retention
Success criteria
```

Sensitive groups may require exclusion depending on the engagement.


---

# Synthetic Credential Collection

Where credential-entry behaviour is being measured, prefer synthetic collection models.

For example:

```text
User Opens Test Page
       |
       v
User Submits Form
       |
       v
Record Event
       |
       v
Discard Password Value
```

Often it is sufficient to record that submission occurred rather than storing the entered secret.


---

# Payload Delivery

Some authorised assessments may involve delivery of a controlled assessment artifact.

Delivery mechanisms can include:

```text
Approved web download
Approved email attachment
Customer-provided transfer mechanism
Existing authorised foothold
Controlled shared location
```

Every delivered file should be tracked.


---

# Payload Inventory

Example:

| Artifact | Purpose | SHA-256 | Target | Cleanup |
|---|---|---|---|---|
| `assessment.bin` | Controlled execution test | `<hash>` | Test workstation | Required |
| `enum.ps1` | Enumeration | `<hash>` | Test workstation | Required |

Calculate a hash on Linux:

```bash
sha256sum assessment.bin
```

PowerShell:

```powershell
Get-FileHash .\assessment.bin -Algorithm SHA256
```


---

# Payload Hosting

Payload infrastructure should be controlled.

A typical architecture is:

```text
Operator Repository
       |
       v
Controlled HTTPS Server
       |
       v
Authorised Target
```

Do not expose:

```text
Customer evidence
Operator SSH keys
C2 credentials
Infrastructure secrets
Unrelated tooling
Internal reports
```


---

# Initial Execution

Once an approved artifact reaches a target, execution itself may cross an important defensive boundary.

Relevant controls can include:

```text
Application control
Antivirus
EDR
Attack Surface Reduction
Script controls
AMSI
Browser protections
Email security
Mark-of-the-Web
User privilege
```

Record which controls permit, block, or alert on the action.


---

# Windows Initial Context

After obtaining authorised Windows access, establish the security context before further action.

```cmd
whoami
```

```cmd
whoami /all
```

```cmd
hostname
```

```cmd
ipconfig /all
```

PowerShell:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Do not immediately begin broad internal enumeration before understanding the host.


---

# Linux Initial Context

For Linux:

```bash
whoami
```

```bash
id
```

```bash
hostname
```

```bash
uname -a
```

```bash
cat /etc/os-release
```

```bash
ip addr
```

Determine:

```text
Current user
Groups
Host
Operating system
Network interfaces
Privilege level
```


---

# Establishing the Foothold

A useful post-access workflow is:

```text
Initial Access
      |
      v
Identify User
      |
      v
Identify Host
      |
      v
Identify Privilege
      |
      v
Identify Security Controls
      |
      v
Confirm Scope
      |
      v
Record Evidence
      |
      v
Continue Only as Required
```


---

# Scope Revalidation

Initial access can reveal systems that were not visible during external reconnaissance.

For example:

```text
External Application
        |
        v
Initial Access
        |
        v
Internal Network
        |
        +--> Server A
        +--> Server B
        +--> Third Party
        +--> Management Network
```

Do not assume every newly reachable system is in scope.

Revalidate the scope before interacting with uncertain assets.


---

# Third-Party Boundaries

Modern organisations depend heavily on third parties.

Examples include:

```text
SaaS
Cloud providers
Managed service providers
Payment providers
CDNs
Email providers
Identity providers
External developers
Suppliers
```

Technical connectivity does not establish testing authorisation.

Third-party systems require appropriate permission.


---

# Detection Opportunities

Initial access can generate telemetry across several layers.

```text
Internet
   |
   v
Firewall
   |
   v
WAF / Proxy
   |
   v
Application
   |
   v
Identity
   |
   v
Endpoint
   |
   v
EDR
   |
   v
SIEM
```


---

# Web Detection

Potential web telemetry includes:

```text
HTTP requests
Authentication failures
Application errors
WAF events
Suspicious parameters
File uploads
Administrative access
New sessions
Unusual user agents
Source addresses
```

Application telemetry should be correlated with infrastructure and identity logs where possible.


---

# Identity Detection

Potential identity signals include:

```text
Failed authentication
Successful authentication
New device
New location
Impossible travel
MFA challenge
MFA failure
Password spray
Account lockout
Risky sign-in
Legacy authentication
Token issuance
```

Cloud identity providers can provide particularly rich authentication telemetry.


---

# Endpoint Detection

Where initial access results in endpoint execution, telemetry can include:

```text
Process creation
File creation
Network connections
Script execution
Module loads
Security-control events
User logon
Child processes
Application-control events
```

The exact data depends on the defensive stack.


---

# Network Detection

Network controls may observe:

```text
External source
Destination
Port
DNS query
TLS metadata
Proxy request
Connection duration
Bytes transferred
Connection frequency
```


---

# Detection Validation

Track the defensive outcome of important actions.

Example:

| Activity | Logged | Alerted | Investigated | Prevented |
|---|---|---|---|---|
| External authentication | Yes | No | No | No |
| Test artifact download | Yes | Yes | Yes | No |
| Controlled execution | Yes | Yes | Yes | Yes |

This turns initial access testing into measurable security-control validation.


---

# Initial Access Evidence

Evidence should establish:

```text
Timestamp
Source
Target
Technique
Affected identity
Affected system
Result
Privilege obtained
Security control response
Objective relationship
```

For example:

```text
Timestamp:
2026-09-05 10:14 UTC

Source:
Authorised assessment infrastructure

Target:
TEST-WKS01

Identity:
CORP\testuser

Result:
Controlled access established

Privilege:
Standard user

Detection:
Endpoint alert generated
```


---

# Minimal Evidence

After proving initial access, avoid unnecessary actions.

```text
Access Established
       |
       v
Objective Proven?
    /       \
  Yes        No
   |          |
   v          v
 Stop      Continue
           Minimally
```

The ability to access additional information does not mean it must be collected.


---

# Candidate vs Confirmed

Use clear confidence levels.

## Candidate

Evidence suggests a possible initial access path.

```text
Exposed service
Potential credential
Interesting configuration
Potential vulnerability
```

Further validation is required.


## Likely

Multiple conditions support practical initial access.

```text
Affected version confirmed
Required configuration confirmed
Authentication weakness confirmed
```

Minimal validation may still be required.


## Confirmed

Controlled testing demonstrates the security boundary can actually be crossed.

```text
Authentication succeeded
Controlled execution occurred
Approved account accessed
Approved objective reached
```


---

# Initial Access Does Not Mean Domain Compromise

A foothold should be reported accurately.

For example:

```text
Internet
   |
   v
Web Application
   |
   v
Low-Privilege Service Account
```

does not automatically mean:

```text
Domain Compromise
```

The report should reflect the actual privilege and reachability demonstrated.


---

# Initial Access Does Not Mean Administrator

Likewise:

```text
Standard User Access
```

should not be described as:

```text
Administrative Access
```

unless that privilege boundary was actually crossed.


---

# Common Assessment Mistakes

Avoid:

```text
Testing hosts outside scope
Assuming every exposed service is vulnerable
Using discovered credentials without checking scope
Running uncontrolled password attacks
Ignoring MFA
Collecting unnecessary sensitive data
Deploying untracked artifacts
Ignoring third-party boundaries
Continuing after the objective is proven
Failing to record defensive response
```


---

# Remediation Model

Initial access remediation depends on the entry path.

A general model is:

```text
Reduce Attack Surface
        |
        v
Patch External Services
        |
        v
Harden Authentication
        |
        v
Enforce MFA
        |
        v
Apply Conditional Access
        |
        v
Restrict Administrative Interfaces
        |
        v
Remove Exposed Secrets
        |
        v
Improve Application Security
        |
        v
Improve Endpoint Controls
        |
        v
Improve Detection
        |
        v
Test Again
```


---

# External Service Hardening

Potential controls include:

```text
Remove unnecessary internet exposure
Restrict source networks
Use VPN or zero-trust access
Patch promptly
Disable legacy protocols
Enforce MFA
Use strong authentication
Monitor authentication
Rate limit where appropriate
Use account lockout carefully
```


---

# Credential Hardening

Potential improvements include:

```text
MFA
Unique passwords
Password managers
Credential rotation
Secret scanning
Conditional access
Risk-based authentication
Removal of legacy authentication
Privileged access management
Short-lived credentials
```


---

# Application Hardening

Potential improvements include:

```text
Secure development lifecycle
Dependency management
Authentication hardening
Authorisation testing
Input validation
Secure file handling
Secret management
Security headers
Logging
WAF where appropriate
Regular penetration testing
```


---

# Phishing Resilience

Where phishing is part of the threat model:

```text
Email filtering
URL analysis
Attachment controls
MFA
Phishing-resistant authentication
User reporting
Security awareness
Browser protections
Endpoint controls
SOC monitoring
```

User awareness should complement technical controls rather than replace them.


---

# Initial Access Checklist

## Scope

- [ ] Written authorisation confirmed
- [ ] External scope confirmed
- [ ] Source infrastructure approved
- [ ] Testing window confirmed
- [ ] Exclusions documented
- [ ] Third-party boundaries understood
- [ ] Stop conditions understood

## Reconnaissance

- [ ] Root domains identified
- [ ] Subdomains enumerated
- [ ] DNS resolution performed
- [ ] Live services identified
- [ ] Technologies fingerprinted
- [ ] Authentication surfaces mapped
- [ ] Cloud surfaces considered
- [ ] Remote-access services identified

## Applications

- [ ] Authentication reviewed
- [ ] Authorisation reviewed
- [ ] High-impact vulnerability classes considered
- [ ] Known vulnerabilities researched
- [ ] Administrative functionality identified
- [ ] APIs considered

## Remote Services

- [ ] VPN reviewed
- [ ] SSH reviewed where exposed
- [ ] RDP/RD Gateway reviewed where exposed
- [ ] File-transfer services reviewed
- [ ] Administrative interfaces reviewed
- [ ] MFA coverage understood

## Credentials

- [ ] Credential testing explicitly authorised
- [ ] Lockout policy understood
- [ ] MFA considered
- [ ] Discovered secrets scoped before validation
- [ ] Credential use recorded
- [ ] Sensitive credential material protected

## Cloud

- [ ] Authorised tenant identified
- [ ] Cloud identities reviewed where in scope
- [ ] Public repositories considered
- [ ] Exposed secrets considered
- [ ] Access keys handled safely
- [ ] Cross-tenant boundaries respected

## Social Engineering

- [ ] Explicit approval obtained
- [ ] Target population approved
- [ ] Exclusions documented
- [ ] Pretext approved
- [ ] Infrastructure approved
- [ ] Credential handling defined
- [ ] Data retention defined
- [ ] Emergency contact available

## Payloads

- [ ] Artifact purpose documented
- [ ] SHA-256 recorded
- [ ] Delivery method approved
- [ ] Target recorded
- [ ] Deployment recorded
- [ ] Cleanup requirement recorded

## Foothold

- [ ] Current identity established
- [ ] Host identified
- [ ] Privilege level identified
- [ ] Security controls identified
- [ ] Scope revalidated
- [ ] Minimum evidence collected

## Detection

- [ ] Authentication telemetry considered
- [ ] Endpoint telemetry considered
- [ ] Network telemetry considered
- [ ] Proxy telemetry considered
- [ ] Application telemetry considered
- [ ] Alerts recorded
- [ ] Response recorded

## Reporting

- [ ] Initial access path documented
- [ ] Entry weakness identified
- [ ] Privilege accurately described
- [ ] Evidence retained
- [ ] Detection result included
- [ ] Remediation included
- [ ] Cleanup verified


---

# Initial Access Decision Model

```text
                    START
                      |
                      v
               Target In Scope?
                 /        \
               No          Yes
               |            |
              STOP          v
                       Identify Surface
                            |
                            v
                     Entry Candidate?
                       /         \
                     No           Yes
                     |             |
               Continue Recon      v
                               Technique
                               Permitted?
                              /        \
                            No          Yes
                            |            |
                           STOP          v
                                  Minimal Validation
                                        |
                                        v
                                  Access Obtained?
                                    /        \
                                  No          Yes
                                  |            |
                             Document          v
                                         Establish
                                          Context
                                             |
                                             v
                                      Scope Still Valid?
                                        /         \
                                      No           Yes
                                      |             |
                                     STOP           v
                                             Record Evidence
                                                   |
                                                   v
                                            Objective Requires
                                             More Activity?
                                             /          \
                                           No            Yes
                                           |              |
                                           v              v
                                         STOP        Continue
                                                    Carefully
```


---

# Initial Access Testing Model

```text
Authorisation
      |
      v
External Reconnaissance
      |
      v
Attack Surface Mapping
      |
      v
Technology Identification
      |
      v
Authentication Mapping
      |
      v
Prioritisation
      |
      +-----------------------+
      |                       |
      v                       v
Application               Identity
      |                       |
      +-----------+-----------+
                  |
                  v
             Remote Access
                  |
                  v
           Minimal Validation
                  |
                  v
            Initial Foothold
                  |
                  v
          Establish Context
                  |
                  v
           Detection Review
                  |
                  v
             Evidence
                  |
                  v
              Cleanup
```


---

# Initial Access and C2

Initial access and C2 are separate concepts.

```text
Initial Access
      |
      v
Execution / Authentication
      |
      v
Controlled Foothold
      |
      v
C2 if Required
```

An engagement may successfully establish initial access without deploying a C2 agent.

Where C2 is required, use the dedicated notes:

[Command and Control](command-and-control.md)


---

# Initial Access and Privilege Escalation

Initial access often begins with limited privileges.

```text
Initial Access
      |
      v
Standard User
      |
      v
Local Enumeration
      |
      v
Privilege Escalation Candidate
```

Use:

- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)


---

# Initial Access and Active Directory

If the foothold is domain joined:

```text
Initial Access
      |
      v
Domain User
      |
      v
Active Directory Enumeration
      |
      v
Attack Path Analysis
```

Use the dedicated:

[Active Directory Notes](../active-directory/)


---

# Initial Access and Web Security

Where the entry path begins with an internet-facing application, use the dedicated:

[Web Application Security Notes](../web/)

The web vulnerability should remain documented separately from any later host or identity compromise it enables.


---

# Related Notes

- [Red Teaming](./)
- [Infrastructure](infrastructure.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Active Directory](../active-directory/)
- [PrivEsc Explorer](../privesc/)
- [Web Application Security](../web/)


---

# References

- [MITRE ATT&CK - Initial Access](https://attack.mitre.org/tactics/TA0001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Reconnaissance](https://attack.mitre.org/tactics/TA0043/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog){ target="_blank" rel="noopener noreferrer" }
- [NIST National Vulnerability Database](https://nvd.nist.gov/){ target="_blank" rel="noopener noreferrer" }
- [ProjectDiscovery httpx](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }
- [Nmap](https://nmap.org/){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Initial access testing can affect internet-facing applications, identities, remote-access services, cloud environments, endpoints, email systems, and human participants. Perform only techniques explicitly permitted by the Rules of Engagement. Password attacks, social engineering, payload delivery, credential use, and access to third-party systems require particularly clear authorisation. Collect only the evidence required to demonstrate the agreed security impact.
