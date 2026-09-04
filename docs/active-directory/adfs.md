# Active Directory Federation Services - AD FS

Active Directory Federation Services, commonly abbreviated:

```text
AD FS
```

is a Microsoft identity federation service that provides authentication and single sign-on capabilities across applications and security boundaries.

AD FS allows an organisation to authenticate a user against an identity provider and issue security tokens that applications can trust.

A simplified model is:

```text
User
 |
 v
Application
 |
 v
AD FS
 |
 v
Active Directory
 |
 v
Authentication
 |
 v
Security Token
 |
 v
Application
```

AD FS is particularly important during Active Directory security assessments because it can become a bridge between:

```text
Active Directory
Cloud Applications
Microsoft 365
SaaS Applications
Partner Organisations
Internal Applications
External Applications
```

A compromise of federation infrastructure can therefore have consequences beyond a single Windows server.

!!! warning "Authorised testing only"
    AD FS is identity infrastructure. Actions affecting token-signing certificates, federation configuration, service accounts, relying-party trusts or the AD FS configuration database can disrupt authentication across an organisation. During production assessments, prefer read-only enumeration and configuration review unless explicit authorisation exists for active federation testing.

---

# Why AD FS Matters

Traditional Active Directory authentication often looks like:

```text
User
 |
 v
Domain Controller
 |
 v
Kerberos / NTLM
 |
 v
Resource
```

Federated authentication introduces another layer:

```text
User
 |
 v
Identity Provider
 |
 v
Token
 |
 v
Relying Party
```

With AD FS:

```text
Identity Provider
=
AD FS
```

The relying party trusts AD FS to make authentication claims about users.

This creates a powerful trust relationship.

---

# AD FS Is Not Automatically a Vulnerability

Do not report:

```text
AD FS Exists
```

as a vulnerability.

Instead determine:

```text
Who Administers AD FS?
Which Applications Trust It?
Which Certificates Protect It?
Which Accounts Run It?
How Is the Farm Protected?
Is the Configuration Database Protected?
Is MFA Required?
Is Extranet Access Restricted?
Are Legacy Authentication Methods Enabled?
Are Federation Certificates Properly Protected?
```

---

# Core Federation Concept

Federation separates:

```text
Authentication
```

from:

```text
Application Access
```

The application does not necessarily authenticate the user directly.

Instead:

```text
Application
    |
    v
Trusts AD FS
    |
    v
AD FS Authenticates User
    |
    v
AD FS Issues Token
    |
    v
Application Accepts Token
```

---

# Identity Provider

AD FS acts as an:

```text
Identity Provider - IdP
```

or:

```text
Security Token Service - STS
```

depending on terminology and protocol.

It authenticates users and issues tokens containing claims.

---

# Relying Party

An application that trusts AD FS is commonly represented as a:

```text
Relying Party Trust
```

Conceptually:

```text
AD FS
 |
 | Signed Token
 v
Relying Party
```

The relying party trusts the token because it trusts the AD FS signing key.

---

# Claims Provider

AD FS can also trust another identity source through a:

```text
Claims Provider Trust
```

Conceptually:

```text
External Identity Provider
        |
        v
      AD FS
        |
        v
Relying Party
```

---

# Claims

AD FS uses:

```text
Claims
```

to describe properties of an authenticated identity.

Examples include:

```text
User Principal Name
Email Address
Name
Group Membership
Role
SID
Authentication Method
```

Applications can use these claims for authorisation.

---

# Claims Model

```text
Active Directory
       |
       v
User Attributes
       |
       v
AD FS Claims Rules
       |
       v
Claims
       |
       v
Security Token
       |
       v
Application
```

---

# Security Tokens

Depending on the application and protocol, AD FS can issue tokens using technologies such as:

```text
SAML
WS-Federation
OAuth
OpenID Connect
```

Support depends on AD FS version and application configuration.

---

# SAML

Security Assertion Markup Language:

```text
SAML
```

is commonly used for enterprise federation.

A simplified flow is:

```text
User
 |
 v
Service Provider
 |
 v
AD FS
 |
 v
Authentication
 |
 v
SAML Assertion
 |
 v
Service Provider
```

---

# WS-Federation

AD FS has historically been heavily associated with:

```text
WS-Federation
```

for browser-based federated authentication.

---

# OAuth

Modern AD FS versions support:

```text
OAuth 2.0
```

for application authorisation scenarios.

---

# OpenID Connect

Modern AD FS versions can also support:

```text
OpenID Connect
```

for authentication built on OAuth-related flows.

---

# Federation Service

The central AD FS service is the:

```text
Federation Service
```

It provides token issuance and federation functionality.

A deployment commonly has a federation service name resembling:

```text
fs.corp.example
```

---

# AD FS Farm

Production AD FS environments commonly consist of a:

```text
Farm
```

rather than a single independent server.

Conceptually:

```text
                 Load Balancer
                      |
            +---------+---------+
            |                   |
            v                   v
         ADFS01               ADFS02
            |                   |
            +---------+---------+
                      |
                      v
            Configuration Database
```

Multiple servers improve:

```text
Availability
Scalability
Resilience
```

---

# Primary and Secondary Servers

In Windows Internal Database based AD FS farms, historical AD FS architecture distinguishes between:

```text
Primary Federation Server
Secondary Federation Servers
```

The exact administrative behaviour depends on the AD FS version and database architecture.

Do not assume every farm uses the same primary-server model.

---

# Configuration Database

AD FS stores farm configuration in either:

```text
Windows Internal Database - WID
```

or:

```text
Microsoft SQL Server
```

depending on deployment architecture.

---

# Windows Internal Database

A common deployment uses:

```text
WID
```

for the AD FS configuration database.

Conceptually:

```text
ADFS01
   |
   v
WID
   |
   v
AD FS Configuration
```

---

# SQL Server

Larger or specialised deployments can use:

```text
SQL Server
```

for AD FS configuration.

Conceptually:

```text
ADFS01 ----+
           |
ADFS02 ----+--> SQL Server
           |
ADFS03 ----+
```

---

# Why the Configuration Database Matters

The AD FS configuration database contains sensitive federation configuration.

This can include information relating to:

```text
Relying Party Trusts
Claims Provider Trusts
Certificates
Endpoints
Authentication Policies
Claims Rules
Application Configuration
Farm Configuration
```

Access should therefore be tightly restricted.

---

# AD FS Service Account

AD FS runs using a service identity.

Modern deployments commonly use:

```text
Group Managed Service Account - gMSA
```

or another dedicated service account depending on architecture and version.

See:

[gMSA](gmsa.md)

---

# Service Account Security

Determine:

```text
Account Type
Account Name
Group Membership
SPNs
Logon Rights
Local Administrator Rights
Delegated Rights
Password Management
```

The AD FS service account should not automatically require:

```text
Domain Admin
```

or:

```text
Enterprise Admin
```

membership.

---

# Service Account Discovery

On an authorised AD FS server:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.Name -eq 'adfssrv'
    } |
    Select-Object Name,StartName,State,PathName
```

---

# AD FS Service

The primary Windows service is commonly:

```text
adfssrv
```

Check:

```powershell
Get-Service -Name adfssrv -ErrorAction SilentlyContinue
```

---

# Installed AD FS Role

On Windows Server:

```powershell
Get-WindowsFeature ADFS-Federation
```

A system with the AD FS role installed should show the feature state.

---

# AD FS PowerShell Module

AD FS provides a PowerShell module.

Check:

```powershell
Get-Module -ListAvailable ADFS
```

Import where necessary:

```powershell
Import-Module ADFS
```

---

# Enumerate Farm Information

From an authorised AD FS administrative context:

```powershell
Get-AdfsFarmInformation
```

This can provide information about the federation farm.

---

# Enumerate AD FS Properties

```powershell
Get-AdfsProperties
```

This is one of the most useful read-only AD FS enumeration commands.

Review configuration such as:

```text
Host Name
Federation Service Identifier
Certificate Rollover
Authentication Settings
Extranet Settings
Audit Configuration
```

available for the deployed version.

---

# Federation Service Name

Identify the federation service name:

```powershell
(Get-AdfsProperties).HostName
```

A result may resemble:

```text
fs.corp.example
```

---

# DNS

Resolve the federation service:

```powershell
Resolve-DnsName 'fs.corp.example'
```

Linux:

```bash
dig fs.corp.example
```

See:

[Active Directory Integrated DNS](adidns.md)

---

# Federation Metadata

AD FS normally exposes federation metadata.

A commonly encountered endpoint is:

```text
/FederationMetadata/2007-06/FederationMetadata.xml
```

Example:

```text
https://fs.corp.example/FederationMetadata/2007-06/FederationMetadata.xml
```

Metadata can provide information about:

```text
Federation Service
Endpoints
Certificates
Identifiers
Supported Protocols
```

---

# Metadata Is Not Automatically Sensitive

Federation metadata is intentionally published in many deployments.

Do not report:

```text
Federation Metadata Is Accessible
```

as a vulnerability by itself.

Instead use it to understand the federation architecture.

---

# Metadata Discovery

Linux:

```bash
curl -k 'https://fs.corp.example/FederationMetadata/2007-06/FederationMetadata.xml'
```

For evidence collection, avoid:

```text
-k
```

when validating certificate trust is part of the assessment.

---

# OpenID Configuration

Modern AD FS deployments may expose OpenID Connect discovery metadata.

A commonly used discovery path is:

```text
/adfs/.well-known/openid-configuration
```

Example:

```text
https://fs.corp.example/adfs/.well-known/openid-configuration
```

---

# OpenID Discovery

```bash
curl 'https://fs.corp.example/adfs/.well-known/openid-configuration'
```

This can reveal:

```text
Issuer
Authorization Endpoint
Token Endpoint
JWKS URI
Supported Algorithms
Supported Scopes
```

---

# JWKS

OAuth and OpenID Connect deployments can expose public signing keys through a:

```text
JSON Web Key Set - JWKS
```

Public signing keys are intentionally public.

Do not report public keys as secret exposure.

---

# AD FS Endpoints

AD FS exposes multiple endpoints depending on:

```text
Protocol
Authentication
Application
Version
Configuration
```

Enumerate configured endpoints using:

```powershell
Get-AdfsEndpoint
```

---

# Endpoint Review

Review:

```text
Protocol
Path
Enabled
Proxy Enabled
Authentication
```

where available.

Look for endpoints that are:

```text
Unused
Legacy
Externally Exposed
Unexpectedly Enabled
```

---

# Relying Party Trusts

Enumerate relying party trusts:

```powershell
Get-AdfsRelyingPartyTrust
```

Useful properties include:

```text
Name
Identifier
Enabled
ProtocolProfile
WSFedEndpoint
SamlEndpoint
IssuanceTransformRules
IssuanceAuthorizationRules
AccessControlPolicyName
```

depending on version and configuration.

---

# Relying Party Security

For each relying party determine:

```text
Application Owner
Protocol
Identifier
Endpoints
Claims
Authorisation Policy
MFA Requirements
Token Lifetime
Current Business Requirement
```

---

# Stale Relying Parties

Old relying-party trusts can remain after applications are retired.

Example:

```text
Legacy Application
      |
      v
Still Trusted by AD FS
```

Review whether each relying party is still required.

---

# Claims Provider Trusts

Enumerate:

```powershell
Get-AdfsClaimsProviderTrust
```

Review:

```text
Name
Identifier
Enabled State
Endpoints
Acceptance Transform Rules
```

---

# Trust Direction

Federation trust should not be confused with an Active Directory domain trust.

```text
AD Domain Trust
```

and:

```text
AD FS Federation Trust
```

are different security mechanisms.

See:

[Trusts](trusts.md)

---

# Claims Rules

Claims rules transform identity information.

Conceptually:

```text
Incoming Claims
      |
      v
Claims Rules
      |
      v
Outgoing Claims
      |
      v
Application
```

---

# Claims Rule Risk

Poorly designed claims rules can:

```text
Expose Excessive Attributes
Grant Excessive Roles
Incorrectly Transform Identity
Permit Unintended Access
```

Review rules carefully.

---

# Enumerating Claims Rules

Relying-party configuration can expose claims rules:

```powershell
Get-AdfsRelyingPartyTrust |
    Select-Object Name,IssuanceTransformRules,IssuanceAuthorizationRules
```

Treat claims rules as security-sensitive configuration.

---

# Claims Rule Example

A conceptual rule might map:

```text
Active Directory Group
       |
       v
Role Claim
       |
       v
Application Administrator
```

The important question is:

```text
Who Controls the Source Group?
```

See:

[Groups](groups.md)

---

# Group-Based Claims

When AD groups influence application roles:

```text
AD Group
   |
   v
AD FS Claim
   |
   v
Application Role
```

review:

```text
Group Membership
Nested Membership
ACLs
Delegated Management
Application Privilege
```

---

# Authentication Policies

AD FS supports different authentication mechanisms depending on version and configuration.

These can include:

```text
Windows Integrated Authentication
Forms Authentication
Certificate Authentication
Device Authentication
MFA
```

---

# Authentication Policy Enumeration

Review:

```powershell
Get-AdfsGlobalAuthenticationPolicy
```

This can reveal configured primary and additional authentication methods.

---

# Primary Authentication

Determine which methods are enabled for:

```text
Intranet
Extranet
```

because the authentication surface can differ.

---

# Extranet Authentication

External authentication deserves particular scrutiny.

Assess:

```text
MFA
Account Lockout Protection
Password Spraying Resistance
Legacy Authentication
External Exposure
Conditional Access Architecture
```

---

# Extranet Smart Lockout

Modern AD FS versions provide:

```text
Extranet Smart Lockout
```

to help protect users from password-spray and brute-force activity originating through externally exposed AD FS authentication.

Review whether appropriate extranet lockout protections are enabled.

---

# Password Spraying

An externally exposed federation endpoint can become a target for:

```text
Password Spraying
```

See:

[Password Spraying](password-spraying.md)

Do not conduct password spraying unless explicitly authorised.

---

# MFA

Multi-factor authentication can significantly reduce the impact of compromised passwords.

Review:

```text
Which Applications Require MFA?
Which Users Require MFA?
Is MFA Required Externally?
Are Privileged Applications Protected?
Are Exemptions Present?
```

---

# MFA Is Not Universal Protection

MFA does not compensate for compromise of:

```text
Token-Signing Private Key
Federation Server
Privileged Federation Configuration
```

These operate at a different trust layer.

---

# Access Control Policies

Modern AD FS versions support:

```text
Access Control Policies
```

for relying parties.

Enumerate:

```powershell
Get-AdfsAccessControlPolicy
```

Review which policies are assigned to sensitive relying parties.

---

# Token-Signing Certificate

One of the most security-sensitive AD FS assets is the:

```text
Token-Signing Certificate
```

Its private key is used to sign tokens issued by AD FS.

Conceptually:

```text
AD FS
 |
 v
Token
 |
 v
Sign with Private Key
 |
 v
Relying Party Verifies Signature
```

---

# Why Token-Signing Keys Matter

The relying party trusts:

```text
Signature
```

not the internal process that generated the identity information.

Therefore:

```text
Trusted Signing Key
       |
       v
Trusted Token
       |
       v
Application Access
```

The private signing key must be treated as highly sensitive.

---

# Golden SAML

A commonly discussed federation persistence technique is:

```text
Golden SAML
```

Conceptually:

```text
Compromised AD FS Token-Signing Key
              |
              v
        Forged SAML Token
              |
              v
         Relying Party
              |
              v
      Federated Identity
```

The name is analogous to:

```text
Golden Ticket
```

but the mechanisms are fundamentally different.

---

# Golden SAML vs Golden Ticket

```text
Golden Ticket
    |
    v
Kerberos
    |
    v
KRBTGT Secret
```

Compared with:

```text
Golden SAML
    |
    v
Federation
    |
    v
AD FS Token-Signing Key
```

---

# Important Golden SAML Distinction

Golden SAML generally requires compromise of trusted federation signing material.

It is not simply:

```text
Domain User
+
AD FS URL
=
Golden SAML
```

The critical prerequisite is control of the signing trust or equivalent federation infrastructure.

---

# Golden SAML Impact

Depending on relying-party configuration, compromise of token-signing material can potentially affect:

```text
SaaS Applications
Internal Applications
Partner Applications
Cloud Services
Federated Services
```

that trust the compromised federation service.

---

# Do Not Forge Production Tokens

During ordinary security assessments, do not generate forged production federation tokens merely to demonstrate that possession of a signing private key is dangerous.

Evidence such as:

```text
Private Key Access
Certificate Identification
Relying Party Trust
Key Exportability
Privilege Path
```

may be sufficient.

---

# Token-Signing Certificate Enumeration

From an authorised AD FS administrative context:

```powershell
Get-AdfsCertificate -CertificateType Token-Signing
```

Review:

```text
Thumbprint
Subject
NotBefore
NotAfter
IsPrimary
CertificateType
```

---

# Token-Decrypting Certificate

AD FS also uses:

```text
Token-Decrypting Certificates
```

for scenarios involving encrypted tokens.

Enumerate:

```powershell
Get-AdfsCertificate -CertificateType Token-Decrypting
```

---

# Service Communications Certificate

AD FS also relies on TLS/service communication certificates.

Review the federation service's TLS certificate separately from token-signing certificates.

These serve different purposes.

---

# Certificate Roles

```text
TLS Certificate
    |
    v
Protect Network Communication

Token-Signing Certificate
    |
    v
Prove Token Authenticity

Token-Decrypting Certificate
    |
    v
Decrypt Encrypted Tokens
```

Do not confuse these roles.

---

# Automatic Certificate Rollover

AD FS supports automatic certificate rollover for token-signing and token-decrypting certificates.

Review:

```powershell
Get-AdfsProperties |
    Select-Object AutoCertificateRollover
```

---

# Certificate Rollover

Conceptually:

```text
Current Certificate
       |
       v
New Secondary Certificate
       |
       v
Relying Parties Learn New Key
       |
       v
New Certificate Becomes Primary
```

This helps maintain federation continuity.

---

# Rollover Security

Certificate rollover is not a substitute for incident response after private-key compromise.

If signing material is compromised, administrators must evaluate:

```text
Key Replacement
Trust Update
Certificate Revocation
Federation Configuration
Relying Parties
Session / Token Impact
```

---

# Certificate Private Key

A certificate itself is not secret.

The sensitive asset is:

```text
Private Key
```

Therefore:

```text
Public Token-Signing Certificate
!=
Signing Capability
```

---

# Private Key Protection

Review:

```text
Key Exportability
Private Key ACL
Key Storage Provider
Machine Access
Backup Copies
Certificate Backups
Administrative Access
```

---

# Hardware Protection

High-security federation environments may protect keys using stronger cryptographic key-storage mechanisms.

The appropriate architecture depends on AD FS version, organisational requirements and supported key-management design.

---

# AD FS Certificate Discovery

List AD FS certificates:

```powershell
Get-AdfsCertificate
```

---

# Local Certificate Store

From the AD FS server:

```powershell
Get-ChildItem Cert:\LocalMachine\My
```

Correlate certificate thumbprints with:

```powershell
Get-AdfsCertificate
```

---

# Private Key Presence

PowerShell can indicate whether a certificate has an associated private key:

```powershell
Get-ChildItem Cert:\LocalMachine\My |
    Select-Object Subject,Thumbprint,HasPrivateKey,NotAfter
```

Do not attempt to export private keys unless explicitly authorised.

---

# Certificate Permissions

Private-key permissions should be restricted to identities that genuinely require access.

Broad local administrative access to federation servers can therefore become highly significant.

---

# AD FS Server Administrators

Determine who can administer federation servers locally.

Example:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

Resolve domain-group membership separately.

---

# Local Admin Risk

Conceptually:

```text
Local Administrator
      |
      v
AD FS Server
      |
      v
Federation Configuration / Key Material
      |
      v
Federation Trust
```

The exact capabilities depend on configuration and key protection.

---

# Domain Admin Risk

Domain administrators often have practical paths to control domain-joined federation infrastructure.

Therefore federation security should be considered in the wider Active Directory privilege model.

---

# AD FS and Tier 0

AD FS is commonly considered identity infrastructure and should be protected accordingly.

Conceptually:

```text
AD FS
 |
 v
Authentication Trust
 |
 v
Applications
```

Compromise can undermine authentication decisions made by relying parties.

---

# Tier 0 Model

```text
Privileged Identity
      |
      v
AD FS Administration
      |
      v
Federation Trust
      |
      v
Applications
```

---

# Web Application Proxy

Externally accessible AD FS deployments commonly use:

```text
Web Application Proxy - WAP
```

Conceptually:

```text
Internet
   |
   v
WAP
   |
   v
AD FS
   |
   v
Active Directory
```

---

# Why WAP Matters

The WAP allows external clients to access federation functionality without directly exposing internal AD FS servers.

This creates an important boundary:

```text
Internet
   |
   v
WAP
   |
   X
Internal AD FS
```

Internal AD FS servers should generally not require direct Internet exposure.

---

# WAP Security Review

Assess:

```text
Patch Level
TLS
Certificates
External Exposure
Administrative Access
Network Segmentation
Federation Relationship
Logging
```

---

# WAP Is Not a Domain Controller

A Web Application Proxy is a federation proxy.

It should not be treated as equivalent to:

```text
Domain Controller
```

but compromise can still expose important federation capabilities.

---

# Federation Service Identifier

AD FS has a federation service identifier.

Review:

```powershell
(Get-AdfsProperties).Identifier
```

This is often represented as a URI.

---

# Identifiers Are Not Secrets

Federation identifiers are used as protocol identifiers and should not be treated as credentials.

---

# Federation Metadata Security

Metadata may expose:

```text
Service Name
Certificate
Endpoints
Entity Identifier
```

This information is usually necessary for federation interoperability.

The risk lies in weak configuration, not the existence of metadata itself.

---

# External Discovery

An authorised external assessment can identify AD FS through:

```text
DNS
TLS Certificates
Federation Metadata
OpenID Discovery
Application Redirects
HTTP Headers
Authentication Pages
```

---

# DNS Names

Common naming conventions include:

```text
adfs.example.com
fs.example.com
sts.example.com
login.example.com
```

These are conventions only.

Do not assume a hostname based solely on naming patterns.

---

# TLS Certificate Discovery

A federation TLS certificate can reveal:

```text
Common Name
Subject Alternative Names
Issuer
Validity
```

Example:

```bash
openssl s_client -connect fs.example.com:443 -servername fs.example.com
```

---

# HTTP Headers

Basic authorised discovery:

```bash
curl -I 'https://fs.example.com/'
```

Do not rely on banners alone to determine version.

---

# Version Enumeration

Avoid assuming an exact AD FS version from:

```text
HTML
URL
Headers
```

alone.

Prefer authenticated server-side inventory where available.

---

# Server Version

From an authorised server context:

```powershell
Get-ComputerInfo |
    Select-Object WindowsProductName,WindowsVersion,OsBuildNumber
```

AD FS capabilities depend heavily on the Windows Server release.

---

# Patch Level

Review installed updates:

```powershell
Get-HotFix |
    Sort-Object InstalledOn -Descending
```

For modern Windows versions, supplement this with enterprise patch-management records because `Get-HotFix` does not represent every servicing component.

---

# AD FS Auditing

AD FS supports auditing that can record federation and authentication activity.

Review:

```powershell
Get-AdfsProperties |
    Select-Object AuditLevel
```

Available values depend on version.

---

# Windows Audit Policy

AD FS auditing also depends on Windows audit policy.

Review:

```cmd
auditpol /get /category:*
```

---

# AD FS Event Logs

Relevant event logs can include:

```text
Applications and Services Logs
    |
    v
AD FS
    |
    v
Admin
```

and security auditing where configured.

---

# Authentication Events

AD FS can produce events associated with:

```text
Successful Authentication
Failed Authentication
Token Issuance
Configuration Changes
Account Lockout
Federation Errors
```

Exact event IDs vary by AD FS version and audit configuration.

---

# Avoid Over-Relying on Event IDs

AD FS logging behaviour has changed across Windows Server releases.

When building detections:

```text
Event Provider
+
Event Meaning
+
AD FS Version
```

is more reliable than memorising a single event number.

---

# Security Event 1200

AD FS auditing can generate event:

```text
1200
```

for successful token issuance in relevant auditing configurations.

Verify behaviour against the deployed AD FS version.

---

# Security Event 1201

Event:

```text
1201
```

can be associated with failed token issuance in relevant AD FS auditing configurations.

Again, verify against the deployed version.

---

# AD FS Event 307

Depending on version and audit configuration, AD FS event:

```text
307
```

can contain token-related auditing information.

Detection engineering should be validated in the actual environment.

---

# AD FS Event 411

AD FS event:

```text
411
```

is commonly relevant to failed authentication activity and can be useful when investigating password-spray attempts.

Verify the exact fields available in the deployed version.

---

# Windows Security Events

Correlate federation activity with relevant Windows events such as:

```text
4624
4625
4648
4672
4768
4769
4771
4776
```

depending on authentication path.

---

# Password Spray Detection

Potential signals include:

```text
Many Users
+
Same Source
+
Repeated Failures
+
AD FS Authentication
```

Correlate AD FS and domain-controller telemetry.

---

# Golden SAML Detection

Golden SAML detection is challenging because forged tokens can potentially be generated outside AD FS.

Conceptually:

```text
Legitimate Token
    |
    v
AD FS Issuance Evidence
    |
    v
Application

Forged Token
    |
    X
No Corresponding AD FS Issuance
    |
    v
Application
```

This creates an important detection opportunity:

```text
Application Accepts Federation Token
+
No Expected AD FS Issuance Evidence
```

---

# Golden SAML Detection Challenges

A forged token may:

```text
Contain Plausible Claims
Use Valid Signature
Reference Legitimate Issuer
Appear Structurally Correct
```

because the attacker controls trusted signing material.

Detection should therefore combine:

```text
AD FS Logs
Application Logs
Cloud Logs
Certificate Changes
Privileged Access
Token Characteristics
```

---

# Signing-Key Access Monitoring

Monitor administrative activity around:

```text
AD FS Servers
Certificate Stores
Private Key Files
Backups
Service Accounts
Federation Configuration
```

---

# Certificate Export Monitoring

Where applicable, monitor private-key access and certificate-management operations.

Relevant telemetry can include:

```text
CAPI2
CNG
Certificate Services
Object Access
Process Creation
PowerShell
EDR
```

depending on key storage and auditing.

---

# Configuration Changes

Changes to:

```text
Relying Party Trusts
Claims Provider Trusts
Certificates
Authentication Policies
Endpoints
Claims Rules
Access Control Policies
```

should be centrally logged and correlated with authorised change records.

---

# PowerShell Logging

Because AD FS administration frequently uses PowerShell, enable appropriate:

```text
PowerShell Script Block Logging
Module Logging
Process Creation
```

according to organisational policy.

---

# Administrative Logons

Monitor privileged access to:

```text
AD FS Servers
WAP Servers
SQL Servers
Management Interfaces
```

especially from unusual systems.

---

# AD FS and Active Directory Authentication

AD FS commonly authenticates users against Active Directory.

Conceptually:

```text
User
 |
 v
AD FS
 |
 v
Active Directory
 |
 v
Authentication
```

This means AD FS security depends partly on:

```text
Domain Security
Service Account Security
Authentication Policy
Federation Configuration
```

---

# Kerberos

Internal Windows Integrated Authentication can use Kerberos.

See:

[Kerberos](kerberos.md)

---

# NTLM

Depending on configuration and client conditions, NTLM may also be involved in Windows authentication.

See:

[NTLM](ntlm.md)

---

# LDAP

AD FS and claims rules may rely on directory information.

Review LDAP security according to the broader Active Directory architecture.

---

# AD FS and Password Spraying

Externally reachable AD FS authentication can expose domain-backed authentication to Internet-originated attempts.

See:

[Password Spraying](password-spraying.md)

Use:

```text
MFA
Extranet Smart Lockout
Monitoring
Network Controls
Strong Password Policy
```

as complementary protections.

---

# AD FS and Account Lockout

Poorly controlled external authentication can result in:

```text
Account Lockout
```

or denial-of-service risk.

Extranet Smart Lockout helps distinguish familiar and unfamiliar sources and can reduce the impact of malicious authentication attempts.

---

# AD FS and Conditional Access

Do not automatically assume that Microsoft Entra Conditional Access protects every AD FS authentication path.

The actual control path depends on:

```text
Federation Configuration
Application
Protocol
Cloud Integration
Authentication Location
```

Validate the architecture.

---

# AD FS and Microsoft Entra ID

Historically, organisations have used AD FS to federate authentication with Microsoft cloud services.

Modern Microsoft identity architecture increasingly favours cloud-based authentication models where appropriate.

An assessment should identify whether AD FS is still required.

---

# Federation Dependency Review

Ask:

```text
Which Applications Still Depend on AD FS?
Which Partners Still Depend on AD FS?
Does Microsoft 365 Still Depend on AD FS?
Can Applications Use Modern Cloud Authentication?
```

---

# Legacy AD FS

An old federation deployment may remain operational because one application still depends on it.

This creates:

```text
Legacy Identity Infrastructure
+
High Trust
+
Limited Business Visibility
```

which deserves review.

---

# Decommissioning Candidates

Identify:

```text
Unused Relying Parties
Unused Claims Providers
Unused Endpoints
Unused Applications
Old Certificates
Old Federation Servers
Legacy WAP Servers
```

---

# AD FS and AD CS

AD FS certificates may be issued by:

```text
Enterprise CA
Public CA
Other Trusted CA
```

depending on certificate purpose.

See:

[Active Directory Certificate Services](ad-cs/index.md)

Do not confuse compromise of an AD CS CA key with compromise of an AD FS token-signing key.

---

# AD FS vs AD CS Trust

```text
AD CS
 |
 v
Certificate Trust
```

Compared with:

```text
AD FS
 |
 v
Federation Token Trust
```

Both rely heavily on cryptographic trust, but they solve different problems.

---

# AD FS and Golden Certificate

A:

```text
Golden Certificate
```

involves forging certificates using a compromised CA signing key.

A:

```text
Golden SAML
```

involves forging federation tokens using compromised federation signing material.

See:

[Golden Certificate](ad-cs/golden-certificate.md)

---

# AD FS and Kerberos Golden Ticket

A Golden Ticket targets:

```text
Kerberos
```

whereas Golden SAML targets:

```text
Federation
```

The distinction is important for both detection and incident response.

---

# AD FS and Trusts

AD FS can federate identities across organisations without creating a traditional AD domain trust.

Therefore:

```text
Federation Trust
!=
Domain Trust
```

See:

[Trusts](trusts.md)

---

# AD FS and Lateral Movement

Compromise of an AD FS server may expose paths to:

```text
Service Accounts
Certificates
Applications
Federation Trusts
```

but AD FS should not be treated as a generic lateral-movement mechanism.

See:

[Lateral Movement](lateral-movement.md)

---

# AD FS and Credential Access

Relevant credential material can include:

```text
Service Account Credentials
Token-Signing Private Keys
Token-Decrypting Private Keys
Database Credentials
WAP Trust Material
```

See:

[Credential Access](credential-access.md)

Do not extract these during ordinary assessment without explicit authorisation.

---

# AD FS and gMSA

Modern AD FS deployments can use:

```text
gMSA
```

for service identity management.

See:

[gMSA](gmsa.md)

This avoids manually managing a static service-account password.

---

# AD FS and Group Membership

Claims can be generated from AD group membership.

Therefore excessive or incorrectly delegated group membership can become application privilege.

See:

[Groups](groups.md)

---

# AD FS and ACLs

Review ACLs controlling:

```text
Federation Service Account
Relevant AD Groups
Certificate Keys
Configuration Files
Service Objects
```

See:

[ACL and ACE](acl-ace.md)

---

# AD FS and Web Security

The AD FS web interface is security-sensitive but should not be tested as though it were an ordinary custom web application without considering authentication impact.

Avoid:

```text
High-Volume Fuzzing
Authentication Flooding
Account Lockout
Uncontrolled Payloads
```

against production federation endpoints.

---

# Safe External Enumeration

A low-impact external review can include:

```text
DNS
TLS
Federation Metadata
OpenID Metadata
HTTP Headers
Authentication Method Identification
```

---

# Safe Internal Enumeration

An authorised administrative review can include:

```text
Get-AdfsProperties
Get-AdfsFarmInformation
Get-AdfsCertificate
Get-AdfsEndpoint
Get-AdfsRelyingPartyTrust
Get-AdfsClaimsProviderTrust
Get-AdfsGlobalAuthenticationPolicy
Get-AdfsAccessControlPolicy
```

These are primarily configuration-enumeration operations.

---

# Useful Read-Only PowerShell Collection

```powershell
Get-AdfsProperties
```

```powershell
Get-AdfsFarmInformation
```

```powershell
Get-AdfsCertificate
```

```powershell
Get-AdfsEndpoint
```

```powershell
Get-AdfsRelyingPartyTrust
```

```powershell
Get-AdfsClaimsProviderTrust
```

```powershell
Get-AdfsGlobalAuthenticationPolicy
```

```powershell
Get-AdfsAccessControlPolicy
```

---

# Export Assessment Evidence

For example:

```powershell
Get-AdfsRelyingPartyTrust |
    Select-Object Name,Enabled,Identifier,ProtocolProfile
```

Avoid exporting secrets or private-key material.

---

# Certificate Evidence

```powershell
Get-AdfsCertificate |
    Select-Object CertificateType,Thumbprint,IsPrimary
```

Record certificate expiry separately where necessary.

---

# Service Account Evidence

```powershell
Get-CimInstance Win32_Service -Filter "Name='adfssrv'" |
    Select-Object Name,StartName,State
```

---

# Local Administrator Evidence

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

---

# Network Evidence

```powershell
Get-NetTCPConnection -State Listen |
    Sort-Object LocalPort |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

---

# TLS Evidence

Linux:

```bash
openssl s_client -connect fs.example.com:443 -servername fs.example.com
```

Record:

```text
Certificate Subject
Issuer
SAN
Expiry
Protocol
Cipher
```

---

# Safe Assessment Workflow

A structured AD FS assessment can follow:

```text
Discover Federation
       |
       v
Identify Farm
       |
       v
Identify Service Account
       |
       v
Enumerate Certificates
       |
       v
Enumerate Trusts
       |
       v
Review Authentication
       |
       v
Review Claims
       |
       v
Review Administrative Access
       |
       v
Review External Exposure
       |
       v
Review Logging
       |
       v
Report
```

---

# Phase 1 - Discovery

Identify:

```text
Federation Service Name
AD FS Servers
WAP Servers
DNS
Load Balancer
Configuration Database
```

---

# Phase 2 - Farm Review

Determine:

```text
Farm Size
Server Versions
Database Type
Patch Level
High Availability
Network Architecture
```

---

# Phase 3 - Service Account Review

Determine:

```text
Service Account
Account Type
Group Membership
SPNs
Local Rights
Domain Rights
```

---

# Phase 4 - Certificate Review

Review:

```text
Token-Signing
Token-Decrypting
TLS
Private Key Protection
Rollover
Expiry
Backup Practices
```

---

# Phase 5 - Trust Review

Enumerate:

```text
Relying Party Trusts
Claims Provider Trusts
Application Groups
OAuth Clients
```

where relevant.

---

# Phase 6 - Claims Review

Review:

```text
Issuance Rules
Authorisation Rules
Group-Based Claims
Privileged Claims
Sensitive Attributes
```

---

# Phase 7 - Authentication Review

Assess:

```text
Intranet Authentication
Extranet Authentication
MFA
Extranet Smart Lockout
Legacy Authentication
Access Control Policies
```

---

# Phase 8 - External Exposure

Review:

```text
WAP
TLS
Metadata
Endpoints
Authentication Pages
Internet Reachability
```

---

# Phase 9 - Administrative Review

Identify:

```text
Local Administrators
AD FS Administrators
Service Account Control
Certificate Administrators
SQL Administrators
WAP Administrators
```

---

# Phase 10 - Logging

Verify:

```text
AD FS Auditing
Windows Security Auditing
PowerShell Logging
WAP Logging
Application Logging
Cloud Logging
SIEM Integration
```

---

# Phase 11 - Minimal Validation

Prefer:

```text
Configuration Evidence
Permission Evidence
Certificate Metadata
Trust Relationships
Claims Rules
Authentication Policies
Logging Configuration
```

over:

```text
Exporting Signing Keys
Forging Tokens
Changing Claims
Changing Relying Parties
Disabling Authentication
```

---

# Phase 12 - Cleanup

Read-only assessment should require no federation cleanup.

If an explicitly approved test configuration was created:

```text
Remove Test Configuration
Verify Federation
Verify Applications
Record Cleanup
```

---

# Common Security Weaknesses

Potential AD FS weaknesses include:

```text
Excessive Local Administrators
Overprivileged Service Account
Weak Token-Signing Key Protection
Exportable Signing Private Keys
Insecure Certificate Backups
Insufficient MFA
Weak Extranet Lockout Protection
Stale Relying Party Trusts
Excessive Claims
Weak Claims Rules
Legacy Endpoints
Direct Internet Exposure of Federation Servers
Weak WAP Segmentation
Insufficient Auditing
Legacy Unsupported Server Versions
```

---

# Excessive Local Administrators

Example:

```text
Broad IT Group
     |
     v
Local Administrators
     |
     v
AD FS Server
```

Because federation servers protect highly trusted identity material, local administrative membership should be tightly controlled.

---

# Overprivileged Service Account

Example:

```text
AD FS Service Account
       |
       v
Domain Admins
```

This should trigger immediate privilege review.

The AD FS service function should not ordinarily require broad domain administration.

---

# Weak Token-Signing Key Protection

Example:

```text
Token-Signing Key
      |
      v
Exportable
      |
      v
Broad Local Admin Access
```

The combination can materially increase federation compromise risk.

---

# Insecure Certificate Backups

A securely configured live server does not compensate for:

```text
PFX Backup
   |
   v
Weak File Share
```

Search authorised backup processes for federation signing material.

Do not perform broad filesystem searches outside scope.

---

# Weak Extranet Authentication

Example:

```text
Internet
   |
   v
AD FS
   |
   +--> Password Only
   |
   +--> Weak Lockout Protection
```

This can increase exposure to password spraying.

---

# Direct AD FS Internet Exposure

A common architecture is:

```text
Internet
   |
   v
WAP
   |
   v
AD FS
```

If internal federation servers are directly Internet accessible, determine whether this is intentional and appropriately hardened.

Do not automatically report direct exposure without understanding the architecture.

---

# Stale Relying Party

Example:

```text
Retired Application
      |
      v
Relying Party Still Enabled
```

Remove unused trust relationships to reduce attack surface and configuration complexity.

---

# Excessive Claims

Applications should receive only the claims they require.

Avoid unnecessarily exposing:

```text
Group Membership
Internal Identifiers
Privileged Roles
Sensitive Attributes
```

---

# Weak Claims Mapping

Example:

```text
Broad AD Group
      |
      v
Administrator Role Claim
      |
      v
Critical Application
```

The source group may become part of the application's privileged security boundary.

---

# Detection Strategy

A useful detection model is:

```text
Authentication
     |
     v
AD FS Logs
     |
     +--> Success
     +--> Failure
     |
     v
Token Issuance
     |
     v
Relying Party
```

Correlate this with:

```text
Application Logs
Cloud Logs
Domain Controller Logs
WAP Logs
EDR
Certificate Events
Administrative Changes
```

---

# Configuration Change Detection

Alert on unexpected changes to:

```text
Token-Signing Certificates
Token-Decrypting Certificates
Relying Party Trusts
Claims Provider Trusts
Claims Rules
Authentication Policies
Endpoints
Access Control Policies
```

---

# Privileged Server Detection

Monitor:

```text
Interactive Logon
RDP
PowerShell
Remote Service Creation
WMI
WinRM
Scheduled Tasks
Certificate Operations
```

on federation servers.

---

# Certificate Change Detection

A token-signing certificate change should correspond with:

```text
Expected Rollover
```

or:

```text
Approved Change
```

Unexpected changes deserve immediate investigation.

---

# Golden SAML Detection Model

```text
Application Token
      |
      v
Valid Signature
      |
      v
Expected Issuer
      |
      v
Compare with AD FS Evidence
      |
      +--> Matching Issuance
      |
      +--> No Matching Issuance
                 |
                 v
             Investigate
```

---

# Incident Response

Suspected AD FS compromise should be treated as an identity-security incident.

Potentially affected components include:

```text
Federation Servers
WAP Servers
Service Accounts
Signing Keys
Decrypting Keys
Relying Parties
Claims Providers
Cloud Federation
Applications
Sessions
```

---

# Signing-Key Compromise

If the token-signing private key is compromised, simply changing the AD FS service-account password is insufficient.

The trust problem is:

```text
Compromised Signing Key
       |
       v
Relying Parties Trust Key
```

Incident response must address the signing trust itself.

---

# Federation Incident Model

```text
Contain Servers
      |
      v
Investigate Key Exposure
      |
      v
Replace Signing Material
      |
      v
Update Trust
      |
      v
Review Applications
      |
      v
Review Sessions / Tokens
      |
      v
Monitor for Abuse
```

Exact recovery procedures should follow current Microsoft guidance and organisational incident-response procedures.

---

# AD FS Hardening

A secure AD FS architecture should include:

```text
Restricted Administration
Least Privilege
Strong Key Protection
MFA
Extranet Protection
WAP
Network Segmentation
Strong TLS
Auditing
Patch Management
Trust Governance
```

---

# Restrict Administrators

Limit local administrative access on:

```text
AD FS Servers
WAP Servers
SQL Servers
```

to dedicated authorised administrators.

---

# Protect Token-Signing Keys

Treat token-signing private keys as critical identity assets.

Review:

```text
Exportability
ACLs
Backups
Administrative Access
Key Storage
Rollover
Monitoring
```

---

# Protect Token-Decrypting Keys

Apply similar controls to token-decrypting private keys.

---

# Use gMSA

Where supported and appropriate, use:

```text
gMSA
```

for the AD FS service account rather than manually managed reusable passwords.

See:

[gMSA](gmsa.md)

---

# Apply MFA

Require MFA according to risk, particularly for:

```text
External Access
Privileged Users
Administrative Applications
Sensitive Relying Parties
```

---

# Configure Extranet Smart Lockout

Use appropriate extranet lockout protection to reduce password-spray and account-lockout risk.

---

# Minimise Endpoints

Disable federation endpoints that are not required.

Maintain an inventory explaining:

```text
Endpoint
Protocol
Application
Owner
External Exposure
Business Requirement
```

---

# Remove Stale Trusts

Periodically review:

```text
Relying Party Trusts
Claims Provider Trusts
Application Groups
OAuth Clients
```

and remove obsolete configuration.

---

# Minimise Claims

Provide applications only the claims required for their function.

---

# Protect Claims Rules

Treat claims-rule modification as a privileged identity change.

Apply:

```text
Change Control
Peer Review
Administrative Restrictions
Auditing
```

---

# Segment Federation Infrastructure

A simplified architecture is:

```text
Internet
   |
   v
WAP
   |
   v
Firewall
   |
   v
AD FS
   |
   +--> Domain Controllers
   |
   +--> Database
```

Allow only required communication.

---

# Restrict Administrative Access

Administrative protocols such as:

```text
RDP
WinRM
SMB
PowerShell Remoting
SQL Administration
```

should originate only from authorised management systems where possible.

---

# Patch AD FS

Maintain supported Windows Server versions and current security updates.

Federation servers are inappropriate places for unsupported operating systems.

---

# Secure TLS

Use:

```text
Trusted Certificates
Modern TLS
Strong Cipher Suites
Correct Hostnames
Certificate Monitoring
```

according to current organisational and Microsoft guidance.

---

# Enable Auditing

Ensure AD FS auditing provides sufficient visibility into:

```text
Authentication
Token Issuance
Failures
Configuration
Administrative Activity
```

---

# Centralise Logs

Send federation logs to a central logging or SIEM platform.

Federation-server compromise can otherwise affect local evidence.

---

# Protect WAP

Treat WAP as part of the identity perimeter.

Apply:

```text
Patch Management
EDR
Restricted Administration
Network Segmentation
TLS Monitoring
Central Logging
```

---

# Protect the Configuration Database

Restrict database administration and backups.

Do not expose SQL unnecessarily.

---

# Review Federation Necessity

For each AD FS dependency ask:

```text
Is Federation Still Required?
```

Legacy federation infrastructure should not remain indefinitely without a business requirement.

---

# Reporting AD FS Findings

Do not report:

```text
Federation Metadata Is Public
```

or:

```text
AD FS Exists
```

without demonstrating an actual security issue.

Report the weakness in the underlying trust model.

---

# Potential Findings

Examples include:

```text
AD FS Token-Signing Private Key Is Insufficiently Protected
```

```text
Excessive Users Have Local Administrative Access to AD FS Servers
```

```text
AD FS Service Account Has Excessive Active Directory Privileges
```

```text
Externally Accessible AD FS Authentication Does Not Enforce MFA for Sensitive Applications
```

```text
AD FS Extranet Authentication Lacks Appropriate Password-Spray Protection
```

```text
Stale AD FS Relying Party Trusts Remain Enabled
```

```text
AD FS Claims Rules Grant Excessive Application Privileges
```

```text
AD FS Administrative Interfaces Are Accessible from Untrusted Networks
```

```text
Legacy AD FS Infrastructure Remains Operational Without Business Requirement
```

---

# Example Finding - Signing Key Protection

```text
Finding:
AD FS Token-Signing Private Key Is Insufficiently Protected

Description:
The AD FS token-signing certificate used to sign federation tokens was
accessible through an administrative path broader than required for
federation operations.

The assessment did not export or use the private key to generate
federation tokens.

Impact:
An attacker who obtains trusted AD FS signing material may potentially
forge federation tokens accepted by relying parties that trust the
affected federation service.

This could undermine application authentication independently of the
victim user's password.

Recommendation:
Restrict administrative access to the AD FS servers and token-signing
private key.

Review private-key exportability, key ACLs, backups and administrative
access.

Where compromise is suspected, follow Microsoft's federation recovery
guidance and replace affected signing material across all relying
parties.
```

---

# Example Finding - Excessive Local Administrators

```text
Finding:
Excessive Users Have Local Administrative Access to AD FS Servers

Description:
A broad Active Directory group was a member of the local Administrators
group on production federation servers.

Several members did not require administrative access to AD FS.

Impact:
Local administrative access to federation servers can provide
significant control over identity infrastructure and may expose
federation configuration or cryptographic material.

Recommendation:
Restrict local administrative access to dedicated federation
administrators.

Resolve nested group membership and remove users who do not require
administrative access.

Use dedicated administrative accounts and controlled management
workstations for federation administration.
```

---

# Example Finding - Service Account

```text
Finding:
AD FS Service Account Has Excessive Active Directory Privileges

Description:
The service identity used by AD FS was a member of a highly privileged
Active Directory group.

The federation service did not require the associated domain-wide
administrative rights.

Impact:
Compromise of the AD FS service account could provide privileges
substantially exceeding those required to operate the federation
service.

Recommendation:
Remove unnecessary privileged group membership.

Where supported and appropriate, use a dedicated gMSA for the AD FS
service and grant only the permissions required by the deployed
architecture.
```

---

# Example Finding - MFA

```text
Finding:
Sensitive Federated Application Does Not Require Multi-Factor
Authentication for External Access

Description:
A sensitive relying party was accessible through externally exposed
AD FS authentication using only username and password.

No additional authentication requirement was applied to the affected
external access path.

Impact:
Compromise of a user's password may provide access to the federated
application without an additional authentication factor.

Recommendation:
Require appropriate multi-factor authentication for external access
and sensitive relying parties.

Review AD FS access control policies and application-specific
authentication requirements.
```

---

# Example Finding - Stale Trust

```text
Finding:
Stale AD FS Relying Party Trust Remains Enabled

Description:
An enabled relying party trust referenced an application that had been
retired and no longer had a documented business owner.

Impact:
Unused federation relationships unnecessarily increase configuration
complexity and attack surface and may preserve unexpected trust paths.

Recommendation:
Validate the relying party with the application owner.

If no longer required, disable and remove the trust through the
organisation's federation change-management process.
```

---

# Example Finding - Claims Rule

```text
Finding:
AD FS Claims Rule Grants Excessive Application Privilege

Description:
A relying party trust generated an administrative role claim based on
membership of a broad Active Directory group.

The group contained users who did not require administrative access to
the federated application.

Impact:
Members of the affected group could receive application privileges
beyond their business requirements.

Recommendation:
Restrict the source Active Directory group or redesign the claims rule
to use a dedicated least-privileged group.

Review nested membership and delegated control over the source group.
```

---

# AD FS Assessment Checklist

## Discovery

- [ ] Identify federation service name
- [ ] Identify AD FS servers
- [ ] Identify farm members
- [ ] Identify WAP servers
- [ ] Identify load balancer
- [ ] Identify DNS records
- [ ] Identify external endpoints
- [ ] Identify configuration database
- [ ] Identify Windows Server versions

## Service Account

- [ ] Identify AD FS service account
- [ ] Determine whether gMSA is used
- [ ] Review group membership
- [ ] Review SPNs
- [ ] Review local rights
- [ ] Review domain rights
- [ ] Review interactive logon
- [ ] Review administrative rights
- [ ] Review credential lifecycle

## Farm

- [ ] Run `Get-AdfsFarmInformation`
- [ ] Run `Get-AdfsProperties`
- [ ] Identify database architecture
- [ ] Review high availability
- [ ] Review patch level
- [ ] Review administrative model

## Certificates

- [ ] Enumerate token-signing certificates
- [ ] Enumerate token-decrypting certificates
- [ ] Identify TLS certificate
- [ ] Review certificate expiry
- [ ] Review rollover
- [ ] Review private-key access
- [ ] Review exportability
- [ ] Review backups
- [ ] Review key storage
- [ ] Review certificate monitoring

## Relying Parties

- [ ] Enumerate relying party trusts
- [ ] Identify application owner
- [ ] Identify protocol
- [ ] Identify endpoints
- [ ] Review enabled state
- [ ] Review claims rules
- [ ] Review authorisation
- [ ] Review MFA
- [ ] Review access control policy
- [ ] Identify stale trusts

## Claims Providers

- [ ] Enumerate claims provider trusts
- [ ] Identify external identity providers
- [ ] Review acceptance rules
- [ ] Review endpoints
- [ ] Identify stale providers

## Claims

- [ ] Review issuance transform rules
- [ ] Review authorisation rules
- [ ] Identify group-based claims
- [ ] Identify role claims
- [ ] Review sensitive attributes
- [ ] Review source-group membership
- [ ] Review nested groups
- [ ] Review source-group ACLs

## Authentication

- [ ] Review intranet authentication
- [ ] Review extranet authentication
- [ ] Review MFA
- [ ] Review certificate authentication
- [ ] Review Windows Integrated Authentication
- [ ] Review Forms Authentication
- [ ] Review Extranet Smart Lockout
- [ ] Review password-spray protections
- [ ] Review legacy authentication

## Endpoints

- [ ] Enumerate AD FS endpoints
- [ ] Identify externally exposed endpoints
- [ ] Identify proxy-enabled endpoints
- [ ] Identify legacy endpoints
- [ ] Disable unused endpoints
- [ ] Review federation metadata
- [ ] Review OpenID discovery

## WAP

- [ ] Identify WAP servers
- [ ] Review external exposure
- [ ] Review TLS
- [ ] Review certificates
- [ ] Review patch level
- [ ] Review local administrators
- [ ] Review network segmentation
- [ ] Review logging

## Network

- [ ] Review Internet exposure
- [ ] Review WAP-to-AD FS connectivity
- [ ] Review AD FS-to-DC connectivity
- [ ] Review database connectivity
- [ ] Review RDP
- [ ] Review WinRM
- [ ] Review SMB
- [ ] Review administrative network restrictions
- [ ] Review load balancer configuration

## Administration

- [ ] Review local Administrators
- [ ] Resolve nested groups
- [ ] Review federation administrators
- [ ] Review SQL administrators
- [ ] Review WAP administrators
- [ ] Review certificate administrators
- [ ] Review dedicated administrative accounts
- [ ] Review privileged workstation use

## Logging

- [ ] Review AD FS audit level
- [ ] Review Windows audit policy
- [ ] Review AD FS Admin log
- [ ] Review Security log
- [ ] Review WAP logs
- [ ] Review PowerShell logging
- [ ] Review application logs
- [ ] Review cloud logs
- [ ] Verify SIEM forwarding
- [ ] Verify retention

## Golden SAML Resilience

- [ ] Protect token-signing private key
- [ ] Review private-key ACL
- [ ] Review key exportability
- [ ] Review certificate backups
- [ ] Review local administrators
- [ ] Monitor certificate operations
- [ ] Correlate application and AD FS logs
- [ ] Maintain signing-key compromise procedure
- [ ] Avoid production token forgery during routine assessment

## Hardening

- [ ] Restrict administrators
- [ ] Apply least privilege
- [ ] Use gMSA where appropriate
- [ ] Protect signing keys
- [ ] Protect decrypting keys
- [ ] Protect TLS keys
- [ ] Apply MFA
- [ ] Configure extranet lockout protection
- [ ] Remove stale trusts
- [ ] Remove unused endpoints
- [ ] Minimise claims
- [ ] Protect claims rules
- [ ] Segment federation infrastructure
- [ ] Protect WAP
- [ ] Protect database
- [ ] Patch servers
- [ ] Enable auditing
- [ ] Centralise logs
- [ ] Review continuing AD FS requirement

## Reporting

- [ ] Do not report AD FS presence alone
- [ ] Do not report public metadata alone
- [ ] Identify actual trust weakness
- [ ] Identify affected application
- [ ] Identify affected account or certificate
- [ ] Identify privilege level
- [ ] Identify attack prerequisites
- [ ] Redact sensitive information
- [ ] Avoid exporting production signing keys
- [ ] Avoid forging production tokens
- [ ] Provide identity-aware remediation

---

# AD FS Testing Model

The basic federation model is:

```text
User
 |
 v
AD FS
 |
 v
Token
 |
 v
Application
```

The authentication model is:

```text
User
 |
 v
AD FS
 |
 v
Active Directory
 |
 v
Authentication
```

The relying-party model is:

```text
AD FS
 |
 v
Signed Token
 |
 v
Relying Party
 |
 v
Application Access
```

The claims model is:

```text
AD Attribute
     |
     v
Claims Rule
     |
     v
Claim
     |
     v
Application Privilege
```

The signing model is:

```text
Token-Signing Private Key
          |
          v
       Signature
          |
          v
     Trusted Token
          |
          v
    Relying Party
```

The Golden SAML model is:

```text
Compromised Signing Material
           |
           v
      Forged Token
           |
           v
      Relying Party
           |
           v
     Federated Access
```

The perimeter model is:

```text
Internet
   |
   v
WAP
   |
   v
AD FS
   |
   v
Active Directory
```

The privilege model is:

```text
Administrator
      |
      v
AD FS Server
      |
      v
Federation Configuration
      |
      v
Applications
```

The certificate model is:

```text
Public Certificate
      !=
Private Key
```

and:

```text
Private Key
    |
    v
Signing Capability
```

The most important distinction is:

```text
AD FS Presence
    !=
Vulnerability
```

Another important distinction is:

```text
Public Federation Metadata
    !=
Secret Exposure
```

The actual security model is:

```text
Identity
   |
   v
Authentication
   |
   v
AD FS
   |
   v
Claims
   |
   v
Signed Token
   |
   v
Relying Party
   |
   v
Application Privilege
```

For penetration testers:

```text
Do Not Ask:
"Can I forge a token?"

Ask:
"Who controls the federation trust,
what signing material protects it,
which applications trust it, and
what evidence demonstrates the risk
without disrupting authentication?"
```

For defenders:

```text
Do Not Ask:
"Is AD FS patched?"

Ask:
"Who can administer AD FS, who can
access the signing keys, which
applications trust those keys, and
would we detect abuse of that trust?"
```

The complete assessment model is:

```text
Active Directory
      |
      v
Authentication
      |
      v
AD FS
      |
      +--> Claims
      |
      +--> Policies
      |
      +--> Signing Key
      |
      v
Federation Token
      |
      v
Relying Parties
      |
      v
Applications
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Enumeration:

[Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Password Spraying:

[Password Spraying](password-spraying.md)

Groups:

[Groups](groups.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Credential Access:

[Credential Access](credential-access.md)

gMSA:

[gMSA](gmsa.md)

Trusts:

[Trusts](trusts.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

AD CS:

[Active Directory Certificate Services](ad-cs/index.md)

Golden Certificate:

[Golden Certificate](ad-cs/golden-certificate.md)

SCOM:

[System Center Operations Manager - SCOM](scom.md)

The next infrastructure page is:

```text
docs/active-directory/rodc.md
```

---

# References

## Microsoft - AD FS Overview

[Microsoft Learn - Active Directory Federation Services Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/ad-fs-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD FS Design

[Microsoft Learn - AD FS Design Guide](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/design/ad-fs-design-guide){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD FS Deployment

[Microsoft Learn - Deploy Active Directory Federation Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/deployment/deploying-a-federation-server-farm){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD FS PowerShell

[Microsoft Learn - ADFS PowerShell Module](https://learn.microsoft.com/en-us/powershell/module/adfs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-AdfsProperties

[Microsoft Learn - Get-AdfsProperties](https://learn.microsoft.com/en-us/powershell/module/adfs/get-adfsproperties){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-AdfsRelyingPartyTrust

[Microsoft Learn - Get-AdfsRelyingPartyTrust](https://learn.microsoft.com/en-us/powershell/module/adfs/get-adfsrelyingpartytrust){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-AdfsCertificate

[Microsoft Learn - Get-AdfsCertificate](https://learn.microsoft.com/en-us/powershell/module/adfs/get-adfscertificate){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD FS Certificates

[Microsoft Learn - Certificates Used by AD FS](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/design/certificate-requirements-for-federation-servers){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD FS Extranet Smart Lockout

[Microsoft Learn - AD FS Extranet Smart Lockout](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/operations/configure-ad-fs-extranet-smart-lockout-protection){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD FS Auditing

[Microsoft Learn - AD FS Troubleshooting - Events and Logging](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/troubleshooting/ad-fs-tshoot-logging){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Web Application Proxy

[Microsoft Learn - Web Application Proxy](https://learn.microsoft.com/en-us/windows-server/remote/remote-access/web-application-proxy/web-application-proxy-windows-server){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Golden SAML

[MITRE ATT&CK - Forge Web Credentials: SAML Tokens](https://attack.mitre.org/techniques/T1606/002/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Steal Authentication Certificate

[MITRE ATT&CK - Steal Authentication Certificate](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

AD FS is part of the identity trust chain.

The core relationship is:

```text
Active Directory
      |
      v
AD FS
      |
      v
Federation Token
      |
      v
Application
```

The relying party does not need to know how the user originally authenticated.

It trusts:

```text
AD FS
```

and particularly:

```text
AD FS Signing Material
```

to make trustworthy identity assertions.

The critical trust path is therefore:

```text
Token-Signing Private Key
          |
          v
      Signed Token
          |
          v
     Relying Party
          |
          v
      Application
```

This makes protection of federation signing keys one of the most important AD FS security requirements.

The authentication perimeter should also be reviewed:

```text
Internet
   |
   v
WAP
   |
   v
AD FS
   |
   v
Active Directory
```

Controls such as:

```text
MFA
Extranet Smart Lockout
Network Segmentation
Strong TLS
Auditing
Restricted Administration
```

reduce different parts of the attack surface.

The strongest AD FS assessment does not require production token forgery.

Instead establish:

```text
Administrative Control
        +
Key Access
        +
Federation Trust
        +
Relying Party Scope
        =
Federation Risk
```

For claims-related weaknesses:

```text
Source Identity
      |
      v
Claims Rule
      |
      v
Privileged Claim
      |
      v
Application Access
```

For externally exposed authentication:

```text
Internet
   |
   v
AD FS / WAP
   |
   v
Authentication Policy
   |
   +--> MFA
   +--> Smart Lockout
   +--> Access Control
```

The primary assessment questions are:

```text
Who Administers AD FS?

Who Can Access the Signing Keys?

Which Applications Trust AD FS?

Which Claims Produce Privilege?

How Is External Authentication Protected?

Would Forged Federation Activity Be Detected?

Is AD FS Still Required?
```

AD FS should therefore be treated as critical identity infrastructure whenever important applications depend on its federation trust.

The next infrastructure topic is:

```text
Read-Only Domain Controller - RODC
```
