# Active Directory Certificate Services

Active Directory Certificate Services (AD CS) is the Microsoft Windows Server role used to build and operate a Public Key Infrastructure (PKI).

AD CS can issue and manage certificates for:

```text
Users
Computers
Servers
Services
Applications
Network Devices
Domain Controllers
Smart Cards
VPN
Wi-Fi
TLS
Code Signing
Document Signing
Authentication
Encryption
```

From an Active Directory security perspective, AD CS is particularly important because certificates can function as authentication credentials.

A simplified model is:

```text
Active Directory Identity
          |
          v
Certificate Enrollment
          |
          v
Certificate + Private Key
          |
          v
Authentication
          |
          v
Active Directory
```

This means that control of a valid authentication certificate may provide an alternative to knowing a user's:

```text
Password
NT Hash
Kerberos Key
```

AD CS therefore introduces another credential and trust system into Active Directory.

The core security relationship is:

```text
Active Directory
      +
Certificate Authority
      +
Certificate Templates
      +
Enrollment Permissions
      +
Certificate Mapping
      =
AD CS Trust
```

Microsoft describes AD CS as the Windows Server role providing PKI capabilities for cryptography, digital certificates, digital signatures, authentication, and related security functions.

!!! warning "Authorised testing only"
    AD CS assessments can involve requesting certificates that authenticate as domain identities. Some certificate misconfigurations can lead to privilege escalation or domain compromise. Begin with enumeration and configuration analysis. Request certificates only through explicitly authorised templates and identities, avoid production-impacting CA changes, and treat issued certificates and private keys as credentials.

---

# Why AD CS Matters

Traditional Active Directory security assessments often focus on:

```text
Passwords
NTLM
Kerberos
ACLs
Delegation
Groups
```

AD CS adds:

```text
Certificates
Private Keys
Certificate Templates
Certification Authorities
Enrollment Services
Certificate Mapping
```

A certificate can potentially authenticate an identity without requiring that identity's password.

Conceptually:

```text
Password
   |
   v
Authentication
```

and:

```text
Certificate + Private Key
          |
          v
Authentication
```

can both establish identity.

---

# Certificates Are Credentials

This is the most important concept when assessing AD CS.

A certificate containing an authentication-capable Extended Key Usage and correctly mapped to an Active Directory identity can potentially be used as reusable authentication material.

Conceptually:

```text
Certificate
    +
Private Key
    |
    v
Identity Authentication
```

Therefore:

```text
Certificate Theft
Certificate Misissuance
Certificate Forgery
Certificate Template Abuse
CA Compromise
```

can become credential attacks.

MITRE ATT&CK tracks the theft or forgery of authentication certificates under:

```text
T1649 - Steal or Forge Authentication Certificates
```

---

# Public Key Infrastructure

PKI provides mechanisms for establishing trust using public-key cryptography.

The simplified relationship is:

```text
Private Key
     |
     +--> Kept Secret
     |
     v
Public Key
     |
     v
Certificate
     |
     v
Signed by CA
```

The certificate binds information such as:

```text
Identity
Public Key
Issuer
Validity Period
Intended Usage
```

together through the CA's digital signature.

---

# Public and Private Keys

A key pair consists of:

```text
Private Key
Public Key
```

The private key must remain secret.

The public key can be distributed.

Conceptually:

```text
Private Key
    |
    X
Must Not Be Shared
```

while:

```text
Public Key
    |
    v
Certificate
    |
    v
Can Be Distributed
```

---

# Certificate Authority

A Certificate Authority:

```text
CA
```

is responsible for issuing and managing certificates.

The CA signs certificates using its own private key.

Conceptually:

```text
Certificate Request
        |
        v
Certificate Authority
        |
        v
CA Signature
        |
        v
Issued Certificate
```

Systems that trust the CA can then validate certificates issued by it.

---

# CA Trust

The fundamental PKI trust model is:

```text
Trusted CA
    |
    v
Signs Certificate
    |
    v
Certificate Trusted
```

This means the security of the CA is extremely important.

If the CA's signing key is compromised:

```text
CA Private Key
      |
      v
Certificate Forgery
      |
      v
Potential Identity Impersonation
```

depending on certificate mapping and usage.

---

# Root Certificate Authority

A Root CA sits at the top of a PKI hierarchy.

```text
Root CA
   |
   v
Trust Anchor
```

The Root CA certificate is normally self-signed.

Conceptually:

```text
Root CA
   |
   +--> Signs Subordinate CA
   |
   v
Subordinate CA
   |
   v
Issues Certificates
```

---

# Offline Root CA

Security-conscious PKI designs commonly keep the Root CA offline.

Example:

```text
Offline Root CA
      |
      v
Issuing CA
      |
      v
Users / Computers / Services
```

The Root CA is only brought online for controlled PKI operations such as:

```text
Signing Subordinate CA Certificates
Publishing Updated CRLs
Key Lifecycle Operations
```

depending on the PKI design.

This reduces exposure of the most sensitive CA key.

---

# Enterprise CA

An Enterprise CA is integrated with Active Directory.

A simplified model is:

```text
Enterprise CA
      |
      v
Active Directory
      |
      v
Certificate Templates
      |
      v
Users / Computers
```

Enterprise CAs can issue certificates based on certificate templates stored in Active Directory.

Certificate templates are a major focus of AD CS penetration testing.

---

# Standalone CA

A Standalone CA does not rely on Active Directory certificate templates in the same way as an Enterprise CA.

Conceptually:

```text
Standalone CA
      |
      v
Certificate Requests
      |
      v
CA Policy
      |
      v
Certificates
```

Standalone CAs are often used for:

```text
Offline Root CAs
Special PKI Functions
Non-Domain Scenarios
```

---

# Enterprise CA vs Standalone CA

A useful distinction is:

```text
Enterprise CA
    |
    +--> AD Integrated
    +--> Certificate Templates
    +--> Domain Enrollment
```

versus:

```text
Standalone CA
    |
    +--> Less AD Integration
    +--> No Enterprise Template Issuance
    +--> Manual / Custom Workflows
```

Only Enterprise CAs issue certificates based on Active Directory certificate templates.

---

# Root vs Subordinate CA

A CA can also be classified by its place in the trust hierarchy.

```text
Root CA
   |
   v
Subordinate CA
```

A subordinate CA receives its CA certificate from another CA.

An organisation might deploy:

```text
Offline Root CA
      |
      v
Enterprise Issuing CA
```

or:

```text
Offline Root CA
      |
      v
Policy CA
      |
      v
Issuing CA
```

depending on PKI complexity.

---

# Issuing CA

An issuing CA directly issues certificates to:

```text
Users
Computers
Servers
Applications
Devices
```

The issuing CA is therefore frequently exposed to domain activity and is a high-value security target.

---

# AD CS Architecture

A simplified Active Directory PKI might look like:

```text
                     Offline Root CA
                           |
                           v
                    Enterprise CA
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
          Users         Computers      Services
             |             |             |
             +-------------+-------------+
                           |
                           v
                  Certificate-Based
                    Authentication
```

---

# AD CS Role Services

AD CS can contain several role services.

Important examples include:

```text
Certification Authority
Certification Authority Web Enrollment
Certificate Enrollment Web Service
Certificate Enrollment Policy Web Service
Network Device Enrollment Service
Online Responder
```

Not every AD CS server has every role installed.

---

# Certification Authority Role Service

The Certification Authority role service provides the core CA functionality.

It can:

```text
Receive Certificate Requests
Issue Certificates
Revoke Certificates
Publish CRLs
Maintain CA Database
Apply CA Policy
```

The CA is the central trust component.

---

# Certification Authority Web Enrollment

CA Web Enrollment provides browser-based certificate enrollment functionality.

A common path is:

```text
https://ca01.corp.example/certsrv/
```

The workflow is:

```text
User
  |
  v
IIS
  |
  v
/certsrv/
  |
  v
Certificate Request
  |
  v
CA
```

Microsoft distinguishes CA Web Enrollment from Certificate Enrollment Web Service; although both may use HTTPS, they are separate technologies.

---

# Why Web Enrollment Matters

Web enrollment expands the AD CS attack surface because certificate requests may be submitted through IIS.

A security assessment should examine:

```text
HTTP vs HTTPS
NTLM Authentication
Extended Protection for Authentication
TLS
Enrollment Permissions
Published Templates
```

Web enrollment has historically been important in NTLM relay scenarios.

---

# Certificate Enrollment Web Service

The Certificate Enrollment Web Service:

```text
CES
```

allows users and computers to enroll for certificates through a web service.

It is different from:

```text
CA Web Enrollment
```

The simplified model is:

```text
Client
  |
  v
Certificate Enrollment Web Service
  |
  v
CA
```

---

# Certificate Enrollment Policy Web Service

The Certificate Enrollment Policy Web Service:

```text
CEP
```

provides certificate enrollment policy information to clients.

Conceptually:

```text
Client
  |
  v
Enrollment Policy
  |
  v
Which Certificates Can Be Requested?
```

CEP and CES can support enrollment for clients that are not directly connected to the domain network.

---

# Network Device Enrollment Service

The Network Device Enrollment Service:

```text
NDES
```

implements the Simple Certificate Enrollment Protocol:

```text
SCEP
```

NDES enables devices that may not possess domain accounts to obtain certificates.

Examples include:

```text
Routers
Switches
Firewalls
Mobile Devices
Network Appliances
```

Conceptually:

```text
Network Device
      |
      v
SCEP
      |
      v
NDES
      |
      v
CA
```

NDES acts as a Registration Authority in the certificate enrollment process.

---

# Online Responder

The Online Responder provides certificate revocation status using:

```text
OCSP
```

or:

```text
Online Certificate Status Protocol
```

Conceptually:

```text
Client
  |
  v
Is Certificate Valid?
  |
  v
Online Responder
  |
  v
Signed Status Response
```

This provides an alternative or complement to downloading Certificate Revocation Lists.

---

# Certificate Revocation List

A Certificate Revocation List:

```text
CRL
```

contains certificates that should no longer be trusted.

Examples of reasons for revocation include:

```text
Private Key Compromise
Certificate Misissuance
User Departure
Device Decommissioning
CA Compromise
```

The simplified model is:

```text
Certificate
    |
    v
Check CRL
    |
    +--> Valid
    |
    +--> Revoked
```

---

# PKI Objects in Active Directory

Enterprise PKI information is stored in Active Directory.

A particularly important configuration partition is:

```text
CN=Public Key Services,
CN=Services,
CN=Configuration,
DC=corp,
DC=example
```

This contains several PKI-related containers.

---

# Public Key Services

Important objects can include:

```text
Certification Authorities
Enrollment Services
Certificate Templates
OID
AIA
CDP
KRA
NTAuthCertificates
```

These objects help describe the enterprise PKI.

---

# Configuration Partition

The PKI configuration is forest-wide.

Conceptually:

```text
Forest
  |
  v
Configuration Partition
  |
  v
Public Key Services
  |
  +--> CAs
  +--> Templates
  +--> Enrollment Services
```

This is why AD CS enumeration often begins through LDAP.

---

# Enrollment Services

Enterprise CA objects are stored beneath:

```text
CN=Enrollment Services,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

These objects can expose information such as:

```text
CA Name
DNS Hostname
Published Certificate Templates
CA Certificate
```

---

# Certificate Templates

Certificate templates are one of the most important AD CS concepts.

A template defines rules for issuing a class of certificate.

Conceptually:

```text
Certificate Template
       |
       +--> Who Can Enroll?
       +--> Who Is the Subject?
       +--> What EKUs Exist?
       +--> Can Subject Be Supplied?
       +--> Is Approval Required?
       +--> Are Signatures Required?
       +--> How Long Is It Valid?
       +--> Can It Authenticate?
```

Microsoft describes certificate templates as sets of rules and settings that a CA applies to incoming requests, while also providing clients with information needed to construct valid requests.

---

# Template Storage

Enterprise certificate templates are stored in:

```text
Active Directory
```

and replicated across the forest.

Conceptually:

```text
Active Directory
      |
      v
Certificate Template
      |
      v
Enterprise CA
```

An Enterprise CA must then be configured to issue a particular template.

---

# Published Templates

A template existing in Active Directory does not automatically mean a particular CA will issue it.

The model is:

```text
Template Exists
      |
      v
CA Publishes Template
      |
      v
Template Can Be Requested from CA
```

Therefore an assessment must determine both:

```text
Template Configuration
```

and:

```text
Which CA Issues It
```

---

# Template Permissions

Certificate templates have Active Directory ACLs.

Important permissions include:

```text
Read
Enroll
Autoenroll
Write
Full Control
WriteDACL
WriteOwner
```

A template can be securely configured in every other respect but still become dangerous if inappropriate principals can modify it.

---

# Enrollment Rights

Two particularly important permissions are:

```text
Enroll
```

and:

```text
Autoenroll
```

Enrollment determines which identities can request certificates from the template.

Examples:

```text
Domain Users
Domain Computers
Authenticated Users
Specific Security Group
Specific Service Account
```

---

# Template Security Model

The template security model can be visualised as:

```text
User / Computer
      |
      v
Has Enroll Permission?
      |
      v
Template Configuration
      |
      v
CA Publishes Template?
      |
      v
Certificate Issued
```

---

# Subject

A certificate contains a:

```text
Subject
```

representing the identity associated with the certificate.

Depending on template configuration, the subject may be:

```text
Built from Active Directory
```

or:

```text
Supplied in the Request
```

This distinction is extremely important during AD CS security assessments.

---

# Subject Alternative Name

Certificates can contain a:

```text
Subject Alternative Name
```

or:

```text
SAN
```

A SAN can identify the certificate subject using forms such as:

```text
DNS Name
User Principal Name
Email Address
IP Address
```

depending on certificate usage and configuration.

For Active Directory authentication, identity information contained in or derived from certificates is security-sensitive.

---

# Extended Key Usage

Extended Key Usage:

```text
EKU
```

defines intended purposes for a certificate.

Examples include:

```text
Client Authentication
Server Authentication
Code Signing
Secure Email
Smart Card Logon
Document Signing
```

---

# Authentication EKUs

From an offensive security perspective, certificates capable of authentication deserve particular attention.

Examples include certificates associated with purposes such as:

```text
Client Authentication
Smart Card Logon
PKINIT Client Authentication
```

depending on configuration and mapping.

The exact ability of a certificate to authenticate must be validated against the environment rather than inferred from a template name alone.

---

# Any Purpose

A certificate configured for:

```text
Any Purpose
```

can have broader security implications because its allowed uses are less constrained.

Templates with broad EKUs require careful review.

---

# No EKU

Certificates without an EKU extension can also have broad usage semantics in some Windows PKI contexts.

Do not assume:

```text
No EKU
   =
Cannot Authenticate
```

Certificate usage must be analysed carefully.

---

# Certificate Enrollment

A normal enterprise enrollment flow may look like:

```text
Domain User
    |
    v
Certificate Template
    |
    v
Enrollment Permission
    |
    v
Certificate Request
    |
    v
Enterprise CA
    |
    v
Certificate
```

---

# Autoenrollment

Active Directory can automatically enroll users or computers for certificates.

Conceptually:

```text
Group Policy
     |
     v
Autoenrollment
     |
     v
Template
     |
     v
Certificate
```

This is commonly used for:

```text
Machine Authentication
Wi-Fi
VPN
TLS
User Authentication
```

---

# Manager Approval

Templates can require:

```text
CA Certificate Manager Approval
```

before issuance.

Conceptually:

```text
Request
   |
   v
Pending
   |
   v
Manager Approval
   |
   v
Certificate
```

This can interrupt otherwise automatic abuse paths.

---

# Authorized Signatures

Templates can also require authorized signatures.

Conceptually:

```text
Certificate Request
       |
       v
Required Signature
       |
       v
Validation
       |
       v
Issuance
```

The number and type of required signatures can significantly affect exploitability.

---

# Private Key

When a certificate is generated, the associated private key is usually at least as important as the certificate itself.

```text
Certificate
    +
Private Key
    |
    v
Credential
```

Possessing only the public certificate normally does not provide authentication capability.

---

# PFX and PKCS#12

Certificates and private keys are commonly packaged in:

```text
PKCS#12
```

files.

Common extensions include:

```text
.pfx
.p12
```

These files may contain:

```text
Certificate
Private Key
Certificate Chain
```

Treat them as credentials.

---

# PEM

Linux tooling commonly represents certificates and keys using PEM encoding.

Examples:

```text
certificate.pem
private-key.pem
```

A private key file should be protected like a password or Kerberos ticket.

---

# Windows Certificate Store

Windows stores certificates in certificate stores.

Useful PowerShell paths include:

```powershell
Cert:\CurrentUser\My
```

and:

```powershell
Cert:\LocalMachine\My
```

Enumerate the current user's personal certificates:

```powershell
Get-ChildItem Cert:\CurrentUser\My
```

Enumerate local-machine personal certificates:

```powershell
Get-ChildItem Cert:\LocalMachine\My
```

---

# Inspect Certificate Properties

```powershell
Get-ChildItem Cert:\CurrentUser\My |
    Select-Object Subject,Issuer,Thumbprint,NotBefore,NotAfter,HasPrivateKey
```

This can identify certificates associated with private keys.

---

# certutil

Windows includes:

```text
certutil.exe
```

for certificate and CA administration.

Basic information:

```cmd
certutil -?
```

Display local certificate stores:

```cmd
certutil -store My
```

Enterprise PKI assessment frequently uses certutil for discovery and troubleshooting.

---

# certreq

Windows also includes:

```text
certreq.exe
```

for certificate requests.

Help:

```cmd
certreq -?
```

It can create, submit, retrieve, and accept certificate requests.

During an assessment, do not submit arbitrary production certificate requests simply because the tool is available.

---

# Certification Authority Console

Administrators can inspect a CA using:

```text
certsrv.msc
```

The Certification Authority console exposes areas such as:

```text
Revoked Certificates
Issued Certificates
Pending Requests
Failed Requests
Certificate Templates
```

Access depends on CA permissions.

---

# Certificate Templates Console

Certificate templates can be managed through:

```text
certtmpl.msc
```

The console exposes template configuration including:

```text
General
Request Handling
Cryptography
Subject Name
Extensions
Security
Issuance Requirements
Superseded Templates
Compatibility
```

These settings are highly relevant to security assessments.

---

# PKI Enterprise Console

Windows also provides:

```text
pkiview.msc
```

Enterprise PKI can help administrators inspect PKI health, including:

```text
CA Certificates
AIA
CRLs
Distribution Points
```

---

# Discovering Enterprise CAs

A basic Windows method is:

```cmd
certutil -config - -ping
```

This can help identify available enterprise CA configurations.

Another useful command is:

```cmd
certutil -dump
```

depending on the certificate or object being inspected.

---

# Active Directory Enumeration

PKI objects can also be enumerated directly from Active Directory.

First obtain the configuration naming context:

```powershell
(Get-ADRootDSE).configurationNamingContext
```

Example:

```text
CN=Configuration,DC=corp,DC=example
```

---

# Public Key Services Path

Build the PKI base:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$pkiBase = "CN=Public Key Services,CN=Services,$configNC"

$pkiBase
```

---

# Enumerate Enrollment Services

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$base = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $base -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties * |
    Select-Object Name,dNSHostName,certificateTemplates
```

This can reveal Enterprise CAs and the templates they publish.

---

# Enumerate Certificate Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$base = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $base -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties * |
    Select-Object Name,DisplayName
```

More detailed template analysis belongs in:

```text
active-directory/ad-cs/enumeration.md
```

---

# LDAP Enumeration from Linux

The same PKI objects can be queried through LDAP.

Example:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Enrollment Services,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(objectClass=pKIEnrollmentService)' \
    cn \
    dNSHostName \
    certificateTemplates
```

Use an approved assessment identity.

---

# Enumerate Templates with LDAP

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(objectClass=pKICertificateTemplate)' \
    cn \
    displayName
```

Raw LDAP enumeration is useful for understanding how AD CS configuration is represented in Active Directory.

---

# Certipy

One of the most widely used tools for authorised AD CS security assessment is:

```text
Certipy
```

Certipy can assist with:

```text
CA Discovery
Template Enumeration
Permission Analysis
Certificate Requests
Certificate Authentication
AD CS Attack-Path Analysis
```

Always verify the syntax against the installed version:

```bash
certipy --help
```

or:

```bash
certipy -h
```

depending on the installed release.

---

# Certipy Enumeration

Modern Certipy versions provide discovery functionality through the:

```text
find
```

command.

Start with:

```bash
certipy find -h
```

rather than copying syntax from an older write-up.

AD CS tooling changes frequently, so version verification is important.

---

# Certipy Output

Enumeration may produce information about:

```text
Certificate Authorities
Certificate Templates
Enrollment Rights
Template Configuration
Web Enrollment
CA Security
Potential ESC Conditions
```

Potential findings identified automatically should be manually verified.

---

# Tool Output Is Not the Finding

Do not report:

```text
Certipy says ESC1
```

as the complete evidence.

Instead determine:

```text
Which CA?
Which Template?
Who Can Enroll?
Which Template Setting Is Dangerous?
Can the Template Authenticate?
Is Approval Required?
Which Identity Can Be Requested?
Can the Certificate Actually Be Issued?
What Privilege Results?
```

---

# BloodHound and AD CS

Modern BloodHound environments can model portions of Active Directory certificate infrastructure and certificate-related attack paths depending on collector and BloodHound versions.

AD CS relationships may involve:

```text
Certificate Authorities
Certificate Templates
Enrollment Rights
Template Control
CA Control
Authentication Paths
```

Treat graph relationships as attack-path hypotheses that require configuration validation.

---

# AD CS Security Assessment Model

A useful model is:

```text
Discover CA
    |
    v
Discover Templates
    |
    v
Identify Enrollment Rights
    |
    v
Analyse Template Configuration
    |
    v
Analyse CA Configuration
    |
    v
Analyse Enrollment Services
    |
    v
Identify Authentication-Capable Certificates
    |
    v
Map Potential ESC Conditions
    |
    v
Validate Minimally
```

---

# What Is an ESC?

AD CS security research commonly categorises certificate-service abuse paths using identifiers such as:

```text
ESC1
ESC2
ESC3
...
```

The term:

```text
ESC
```

is commonly used for:

```text
Escalation
```

conditions involving Active Directory Certificate Services.

These categories were popularised through security research into AD CS attack paths.

---

# ESC Numbers Are Not Vulnerabilities by Themselves

An important reporting principle is:

```text
ESC1
```

is a useful technical classification.

It is not the full business finding.

Instead report the actual configuration problem.

For example:

```text
Low-Privileged Users Can Request Authentication Certificates
for Arbitrary Domain Identities
```

is more informative than:

```text
ESC1
```

alone.

---

# ESC Categories Change

AD CS research continues to evolve.

Therefore:

```text
ESC1-ESC15
```

should not be treated as a permanent or exhaustive list of all possible certificate-service weaknesses.

New attack paths and defensive changes can alter the taxonomy.

Always verify:

```text
Tool Version
Research Version
Windows Version
CA Configuration
Domain Configuration
```

before drawing conclusions.

---

# AD CS Attack Surface

The overall attack surface can be divided into:

```text
Certificate Templates
Certificate Authorities
Enrollment Services
Directory Permissions
Certificate Mapping
Private Keys
CA Keys
Authentication Protocols
Web Services
```

---

# Template Misconfiguration

A template can become dangerous because of combinations involving:

```text
Enrollment Rights
Subject Configuration
EKUs
Issuance Requirements
Template ACLs
CA Publication
```

A single setting should rarely be analysed in isolation.

---

# CA Misconfiguration

The CA itself can also introduce risk through:

```text
CA Permissions
CA Policy
Enrollment Agent Restrictions
Request Disposition
Web Enrollment
RPC Enrollment
Certificate Mapping
CA Key Protection
```

---

# Directory ACL Misconfiguration

AD CS objects exist in Active Directory and therefore inherit the broader AD security model.

Attackers may potentially control:

```text
Certificate Templates
Enterprise CA Objects
PKI Containers
Enrollment Groups
```

through excessive ACLs.

See:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

---

# Certificate Template Control

If an attacker can modify a certificate template, the attack may be:

```text
Safe Template
     |
     v
Attacker Modifies Template
     |
     v
Dangerous Template
     |
     v
Certificate Enrollment
```

Therefore template ownership and ACLs matter just as much as the current template settings.

---

# CA Control

Control over a CA can be substantially more powerful than control over one certificate template.

Conceptually:

```text
CA Control
   |
   v
Certificate Issuance Control
   |
   v
Potential Identity Trust Abuse
```

CA administrative permissions must therefore be treated as highly privileged.

---

# PKI Administrators

PKI administrative roles may include permissions capable of:

```text
Managing CA Configuration
Approving Requests
Issuing Certificates
Managing Templates
Managing CA Security
Managing Revocation
```

These roles should be treated as sensitive.

---

# CA Private Key

The CA private key is among the most sensitive secrets in an enterprise PKI.

```text
CA Private Key
      |
      v
Signs Certificates
      |
      v
Enterprise Trust
```

Compromise may allow certificate forgery depending on the CA and trust relationships.

Protect it using:

```text
Strong ACLs
Hardware Protection
HSM Where Appropriate
Administrative Tiering
Backup Protection
Offline Root Design
```

---

# Hardware Security Modules

High-security PKI deployments may protect CA private keys using:

```text
HSM
```

or:

```text
Hardware Security Module
```

An HSM can reduce the risk of extracting CA private keys directly from the operating system.

It does not fix insecure certificate templates or enrollment permissions.

---

# CA Backup Security

CA backups may contain sensitive material including:

```text
CA Database
CA Configuration
CA Certificate
CA Private Key
```

depending on the backup method.

Therefore:

```text
CA Backup
```

may effectively become:

```text
Tier 0 Secret Material
```

and must be protected accordingly.

---

# Certificate Authentication

Certificates may be used with Active Directory authentication mechanisms such as:

```text
PKINIT
Schannel
Smart Card Logon
```

depending on certificate properties and environment configuration.

---

# PKINIT

PKINIT extends Kerberos to support public-key authentication.

Conceptually:

```text
Certificate + Private Key
          |
          v
PKINIT
          |
          v
KDC
          |
          v
TGT
```

This allows certificate credentials to become Kerberos credentials.

---

# Certificate to TGT

A useful conceptual model is:

```text
Authentication Certificate
          |
          v
PKINIT
          |
          v
Kerberos TGT
          |
          v
Domain Authentication
```

This is why authentication-capable certificate issuance can be so significant.

---

# Schannel

Windows can also use certificates through:

```text
Schannel
```

for TLS client authentication.

Conceptually:

```text
Certificate
    |
    v
TLS Client Authentication
    |
    v
Windows Service
```

Certificate authentication paths are not limited to PKINIT.

---

# Certificate Mapping

For a certificate to authenticate as an Active Directory identity, Windows must determine which identity the certificate represents.

Conceptually:

```text
Certificate
    |
    v
Mapping
    |
    v
Active Directory Account
```

Certificate mapping behaviour is therefore a critical part of modern AD CS security.

---

# Strong Certificate Mapping

Microsoft has introduced significant hardening around certificate-based authentication and certificate mapping.

Modern AD CS assessments must consider:

```text
Certificate Mapping Method
SID Security Extension
KDC Behaviour
Schannel Behaviour
Domain Controller Patching
Compatibility Settings
```

Older AD CS exploitation guidance may not behave identically on current Windows environments.

---

# Historical Guidance Can Be Outdated

Do not assume:

```text
Old ESC PoC
    |
    v
Works on Current Windows
```

Certificate mapping and authentication protections have changed substantially over time.

Always verify current behaviour.

---

# Certificate Lifetime

Certificate validity may be:

```text
Hours
Days
Months
Years
```

depending on template and CA policy.

A long-lived authentication certificate can increase persistence risk.

---

# Password Rotation Does Not Necessarily Revoke Certificates

A critical security concept is:

```text
Password Changed
      |
      X
Certificate Automatically Invalid
```

A previously issued certificate may remain valid until:

```text
Expiration
Revocation
Trust Change
```

depending on authentication and certificate validation behaviour.

Therefore certificate compromise must be handled separately from password compromise.

---

# Certificate Persistence

A certificate can provide persistence because it may survive:

```text
Password Reset
NT Hash Rotation
Kerberos Key Changes
```

until the certificate becomes invalid or unusable.

This makes certificate inventory and revocation important during incident response.

---

# Revocation

If a certificate is compromised:

```text
Certificate
    |
    v
Revoke
    |
    v
Publish Revocation Information
```

may be necessary.

Simply changing the associated user's password may not be sufficient.

---

# Certificate Theft

Certificates may be exposed through:

```text
Windows Certificate Stores
PFX Files
Backups
Configuration Files
Profile Data
Exported Keys
Service Accounts
Application Directories
```

Private-key exportability significantly affects theft risk.

---

# Exportable Private Keys

Some templates allow private keys to be:

```text
Exportable
```

This may be operationally necessary but increases credential portability.

Conceptually:

```text
Certificate Store
      |
      v
Export PFX
      |
      v
Certificate + Private Key
      |
      v
Reusable Elsewhere
```

---

# Non-Exportable Does Not Mean Unusable

A non-exportable private key may still be usable by:

```text
The Local Account
The Service
Cryptographic APIs
Processes with Sufficient Access
```

Therefore:

```text
Non-Exportable
      |
      X
No Credential Risk
```

is incorrect.

---

# Enrollment Agents

AD CS supports enrollment-agent functionality.

An enrollment agent can request certificates on behalf of another identity under configured conditions.

Conceptually:

```text
Enrollment Agent
      |
      v
Request on Behalf of User
      |
      v
Certificate for User
```

This is powerful functionality and must be tightly controlled.

---

# Enrollment Agent Restrictions

Enterprise environments can configure restrictions governing:

```text
Which Enrollment Agents
Can Request
Which Templates
For Which Users
```

Missing or overly broad restrictions can increase risk.

---

# CA Managers

Certificate managers may be able to:

```text
Approve Pending Requests
Deny Requests
Revoke Certificates
Manage Issued Certificates
```

Depending on CA configuration, these permissions can be highly sensitive.

---

# CA Administrators

CA administrators can control CA configuration.

This may include security-sensitive settings affecting certificate issuance.

Treat CA administrative access as privileged infrastructure access.

---

# AD CS and Tier 0

AD CS infrastructure capable of issuing domain authentication certificates should generally be considered part of the highest identity security tier.

Conceptually:

```text
Domain Controller
Certificate Authority
Identity Infrastructure
```

all participate in establishing domain trust.

Compromise of the PKI can potentially undermine Active Directory authentication.

---

# AD CS and NTLM Relay

AD CS web services have historically been important relay targets.

The simplified chain is:

```text
Authentication Coercion
        |
        v
NTLM Authentication
        |
        v
Relay
        |
        v
AD CS HTTP Enrollment
        |
        v
Certificate
```

See:

[Authentication Coercion](../authentication-coercion.md)

[NTLM Relay](../ntlm-relay.md)

---

# ESC8 Context

A common AD CS relay scenario is classified as:

```text
ESC8
```

and involves insecure certificate enrollment web endpoints under suitable conditions.

The full path requires more than simply discovering:

```text
/certsrv/
```

The assessment must consider:

```text
Authentication
EPA
HTTP / HTTPS
Enrollment Permissions
Certificate Template
Victim Identity
Certificate Mapping
```

---

# AD CS and Kerberos

Once a certificate can authenticate through PKINIT:

```text
Certificate
    |
    v
Kerberos
    |
    v
TGT
```

the certificate effectively becomes part of the Kerberos authentication ecosystem.

See:

[Kerberos](../kerberos.md)

---

# AD CS and NTLM

Certificate authentication can provide an alternative to NTLM.

However, NTLM remains relevant because it may be used to:

```text
Authenticate to Enrollment Services
Relay Authentication to AD CS
Access CA Administration
```

See:

[NTLM](../ntlm.md)

---

# AD CS and Shadow Credentials

Shadow Credentials also use certificate-based authentication concepts.

The relationship is:

```text
msDS-KeyCredentialLink
        |
        v
Key Credential
        |
        v
Certificate-Based Authentication
```

Shadow Credentials do not require a traditional AD CS certificate template vulnerability.

See:

[Active Directory Shadow Credentials](../shadow-credentials.md)

---

# AD CS and Credential Access

Certificates and private keys should be included in credential-access assessments.

Credential discovery should therefore consider:

```text
Passwords
Hashes
Tickets
Certificates
Private Keys
PFX Files
```

See:

[Active Directory Credential Access](../credential-access.md)

---

# AD CS and ACLs

AD CS attack paths frequently involve Active Directory ACLs.

Examples:

```text
User
 |
 v
GenericWrite on Template
```

or:

```text
Group
 |
 v
Control of Enrollment Group
```

or:

```text
Principal
 |
 v
Control of CA-Related Object
```

See:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

---

# AD CS and Groups

Certificate enrollment is often granted to groups.

Examples:

```text
Domain Users
Domain Computers
VPN Users
Workstation Administrators
Server Administrators
Certificate Enrollers
```

Nested group membership must be considered.

See:

[Active Directory Groups](../groups.md)

---

# AD CS and Group Policy

Certificate enrollment and autoenrollment can be deployed through Group Policy.

Conceptually:

```text
GPO
 |
 v
Certificate Autoenrollment
 |
 v
Users / Computers
 |
 v
Certificates
```

See:

[Active Directory Group Policy](../group-policy.md)

---

# AD CS Assessment Phases

A complete AD CS assessment can be divided into:

```text
1. Discovery
2. CA Enumeration
3. Template Enumeration
4. Permission Analysis
5. Enrollment-Service Analysis
6. Certificate-Mapping Analysis
7. ESC Classification
8. Attack-Path Mapping
9. Controlled Validation
10. Detection Review
11. Hardening Review
```

---

# Phase 1 - Discovery

Identify whether AD CS exists.

Look for:

```text
Enterprise CA Objects
Certificate Templates
CA Servers
Web Enrollment
Enrollment Services
PKI DNS Names
Certificates Issued by Internal CAs
```

---

# Phase 2 - CA Enumeration

For each CA identify:

```text
CA Name
CA Host
CA Type
Root / Subordinate
Enterprise / Standalone
Published Templates
Web Enrollment
Enrollment Services
CA Permissions
```

---

# Phase 3 - Template Enumeration

For each relevant template identify:

```text
Template Name
Published CA
Enrollment Rights
Autoenrollment Rights
EKUs
Subject Configuration
SAN Behaviour
Manager Approval
Authorized Signatures
Validity Period
Private Key Settings
Template ACL
```

---

# Phase 4 - Permission Analysis

Determine:

```text
Who Can Enroll?
Who Can Autoenroll?
Who Can Modify the Template?
Who Owns the Template?
Who Controls Enrollment Groups?
Who Controls the CA?
```

---

# Phase 5 - Enrollment Services

Identify:

```text
CA Web Enrollment
CES
CEP
NDES
Other Certificate-Related Web Services
```

Review:

```text
HTTP
HTTPS
Authentication
NTLM
EPA
TLS
Access Control
```

---

# Phase 6 - Certificate Mapping

Determine how issued certificates map to identities.

Review:

```text
SAN
UPN
SID Extension
Issuer
Subject
Explicit Mapping
KDC Behaviour
Schannel Behaviour
```

This is essential when validating modern AD CS attack paths.

---

# Phase 7 - ESC Classification

Classify potential weaknesses using the current AD CS research taxonomy.

Examples may include:

```text
ESC1
ESC2
ESC3
ESC4
ESC5
ESC6
ESC7
ESC8
ESC9
ESC10
ESC11
ESC12
ESC13
ESC14
ESC15
```

The dedicated pages should explain each category separately.

---

# Phase 8 - Attack-Path Mapping

Do not examine ESC conditions in isolation.

Map:

```text
Attacker
   |
   v
Enrollment / Control
   |
   v
Certificate
   |
   v
Identity
   |
   v
Privilege
```

BloodHound can assist with this process.

---

# Phase 9 - Controlled Validation

Use the least-impact validation capable of proving the condition.

A preferred hierarchy is:

```text
Configuration Evidence
        |
        v
Tool Correlation
        |
        v
Test Identity
        |
        v
Test Certificate
        |
        v
Authentication Proof
        |
        v
Stop
```

Avoid unnecessary privilege escalation after the issue has been demonstrated.

---

# Phase 10 - Detection Review

Assess whether defenders can detect:

```text
Certificate Requests
Unusual Templates
Privileged Certificate Issuance
CA Configuration Changes
Template Changes
Certificate Authentication
CA Administration
Certificate Theft
```

---

# Phase 11 - Hardening Review

Review:

```text
Template Configuration
Template ACLs
CA ACLs
Enrollment Services
EPA
NTLM
Certificate Mapping
CA Key Protection
PKI Administrative Tiering
Logging
Revocation
```

---

# Safe Validation

AD CS exploitation can create durable credentials.

Therefore the preferred test model is:

```text
Enumerate
   |
   v
Identify Misconfiguration
   |
   v
Confirm Permissions
   |
   v
Request One Test Certificate
   |
   v
Validate Authentication
   |
   v
Stop
   |
   v
Revoke / Remove Test Material
```

---

# Use a Dedicated Test Identity

Where possible use:

```text
CORP\adcs-test
```

or another approved assessment identity.

Avoid requesting certificates impersonating:

```text
Domain Admin
Enterprise Admin
Administrator
Domain Controller
```

unless demonstrating that exact impact is explicitly required.

---

# Protect Issued Test Certificates

A test certificate may itself become a reusable credential.

Store it only in an assessment-controlled location.

Do not:

```text
Commit .pfx Files to Git
Upload Certificates to Public Services
Paste Private Keys into Reports
Leave Certificates on Shared Hosts
```

---

# Clean Up

After testing:

```text
Revoke Test Certificate if Required
Delete Exported PFX
Delete Private Keys
Remove Temporary Requests
Restore Modified Templates
Restore Modified CA Configuration
Remove Temporary Accounts
Document Cleanup
```

Do not leave authentication-capable certificates behind.

---

# Detection

AD CS monitoring should include:

```text
Certificate Issuance
Certificate Requests
Template Changes
CA Configuration Changes
CA Permission Changes
Certificate Authentication
CA Administrative Activity
```

---

# CA Auditing

AD CS provides auditing capabilities for certification authority operations.

Organisations should configure auditing according to their PKI and security-monitoring requirements.

Important categories include operations around:

```text
Certificate Requests
Certificate Issuance
Certificate Revocation
CA Configuration
CA Security
```

---

# Certificate Request Events

Certificate issuance activity can generate CA-related Windows events depending on audit configuration.

Rather than relying on one event ID alone, defenders should correlate:

```text
Requester
Template
Subject
SAN
Issuer
Serial Number
Time
Source
```

---

# Template Changes

Certificate templates are Active Directory objects.

Changes can therefore be monitored through directory-service auditing where appropriate.

Sensitive changes include:

```text
Enrollment Permissions
Subject Name Settings
EKUs
Issuance Requirements
Template Security Descriptor
```

---

# Event 5136

Active Directory object modification may generate:

```text
5136
```

when appropriate Directory Service Changes auditing is configured.

This can be useful for detecting changes to:

```text
Certificate Templates
PKI Objects
Enrollment Configuration
```

---

# Certificate Authentication Monitoring

Certificate-based authentication should be correlated with:

```text
Account
Certificate Issuer
Certificate Subject
Certificate Serial Number
Authentication Protocol
Source Host
Target
```

where the relevant telemetry is available.

---

# Monitor Privileged Certificate Requests

Particular attention should be paid to certificates associated with:

```text
Domain Admins
Enterprise Admins
Domain Controllers
PKI Administrators
Tier 0 Service Accounts
```

Unexpected certificate enrollment for these identities warrants investigation.

---

# Hardening Principles

AD CS hardening should follow:

```text
Least Privilege
Strong Identity Mapping
Minimal Enrollment Rights
Secure Templates
Secure CA
Secure Enrollment Services
Protected Private Keys
Monitoring
Revocation Capability
```

---

# Minimise Enrollment Rights

Do not grant:

```text
Domain Users
Authenticated Users
Everyone
```

enrollment rights on powerful authentication templates unless genuinely required.

Use dedicated groups.

---

# Restrict Template Administration

Only appropriate PKI administrators should be able to modify certificate templates.

Review:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
```

on template objects.

---

# Restrict CA Administration

CA administrative permissions should be tightly controlled.

Avoid granting broad groups unnecessary:

```text
Manage CA
Manage Certificates
```

permissions.

---

# Secure Web Enrollment

Where CA Web Enrollment or other enrollment web services are required:

```text
Use HTTPS
Apply Current Patches
Enable Appropriate EPA Protections
Review NTLM
Restrict Network Access
Harden IIS
Monitor Authentication
```

Follow current Microsoft guidance because enrollment-service protections continue to evolve.

---

# Protect CA Private Keys

Use:

```text
Strong Key Protection
Restricted Administrative Access
HSM Where Appropriate
Secure Backups
Offline Root CA
```

for high-value PKI infrastructure.

---

# Protect Certificate Backups

Treat:

```text
PFX
Private Keys
CA Backups
```

as sensitive credentials.

Encrypt backups and restrict access.

---

# Shorter Certificate Lifetimes

Where operationally appropriate, shorter certificate lifetimes can reduce the window available to abuse compromised credentials.

This must be balanced against:

```text
Availability
Enrollment Reliability
Operational Overhead
```

---

# Revocation Capability

Ensure that:

```text
CRLs
OCSP
Revocation Processes
```

are operational.

A certificate that cannot be reliably revoked creates additional incident-response risk.

---

# Administrative Tiering

PKI administration should be separated from normal workstation administration.

A useful model is:

```text
PKI Admin
   |
   X
Internet Browsing Workstation
```

Instead:

```text
PKI Admin
   |
   v
Dedicated Administrative Workstation
   |
   v
PKI Infrastructure
```

---

# CA Server Hardening

Treat CA servers as highly sensitive.

Apply:

```text
Minimal Installed Roles
Restricted Interactive Logon
Restricted Network Access
Application Control
EDR
Strong Patch Management
Secure Backups
Administrative Tiering
```

---

# Do Not Combine Unnecessary Roles

Where architecture permits, avoid placing unrelated application roles on CA servers.

The CA should not become a general-purpose:

```text
File Server
Web Server
Management Server
Jump Host
```

unless required by the PKI architecture.

---

# Incident Response

If AD CS compromise is suspected:

```text
Identify Certificate
      |
      v
Identify Template
      |
      v
Identify Requester
      |
      v
Identify CA
      |
      v
Identify Private-Key Exposure
      |
      v
Identify Authentication Use
      |
      v
Contain
      |
      v
Revoke
```

---

# Certificate Incident Response

Investigate:

```text
Certificate Serial Number
Thumbprint
Subject
SAN
Issuer
Template
Requester
Issue Time
Expiration
Private Key Location
Authentication Activity
```

---

# Template Incident Response

If a template was modified:

```text
Identify Changed Attributes
      |
      v
Identify Actor
      |
      v
Identify Change Time
      |
      v
Identify Certificates Issued During Window
      |
      v
Revoke Malicious Certificates
      |
      v
Restore Secure Configuration
```

---

# CA Compromise

CA compromise is substantially more serious.

Potential response actions may involve:

```text
CA Key Revocation
CA Certificate Revocation
Trust Store Changes
Certificate Reissuance
PKI Recovery
Domain-Wide Investigation
```

These actions can have major operational consequences and should follow the organisation's PKI incident-response process.

---

# Password Reset Is Not Enough

If an attacker obtained an authentication certificate:

```text
Reset Password
     |
     X
Certificate Removed
```

Investigators must identify and revoke or otherwise invalidate the certificate where appropriate.

---

# Golden Certificate Concept

If an attacker obtains a CA signing key, certificate forgery may become possible.

This is commonly referred to in offensive-security literature as a:

```text
Golden Certificate
```

concept.

The simplified model is:

```text
CA Private Key
      |
      v
Forge Certificate
      |
      v
Trusted CA Signature
      |
      v
Authentication
```

A dedicated page should cover this separately.

---

# AD CS Reporting

Good AD CS findings should describe the actual trust failure.

Avoid reporting only:

```text
ESC1
```

or:

```text
ESC8
```

Instead explain:

```text
Who Can Exploit It?
Which CA?
Which Template / Service?
Which Configuration Is Unsafe?
Which Identity Can Be Obtained?
What Authentication Is Possible?
What Privilege Results?
```

---

# Example Finding Title

```text
Low-Privileged Users Can Request Authentication Certificates for Arbitrary Domain Identities
```

This communicates more than:

```text
ESC1
```

---

# Another Finding Title

```text
Excessive Certificate Template Permissions Allow Security-Sensitive Template Modification
```

rather than only:

```text
ESC4
```

---

# Another Finding Title

```text
AD CS Web Enrollment Is Exposed to NTLM Relay
```

rather than only:

```text
ESC8
```

---

# Example Finding

```text
Finding:
Low-Privileged Users Can Obtain Security-Sensitive Authentication
Certificates

Affected CA:
CORP-CA01

Affected Template:
Example Authentication Template

Description:
The certificate template is published by the enterprise certification
authority and can be enrolled by a broad domain security group.

The template configuration allows certificates to be issued with
identity information that is not sufficiently constrained for the
intended enrollment population.

The issued certificate is suitable for domain authentication under
the tested configuration.

During controlled validation, a dedicated assessment account requested
one certificate and successfully demonstrated certificate-based
authentication.

No privileged production identity was impersonated.

Impact:
An attacker controlling an account with enrollment rights could
potentially obtain authentication material representing an identity
beyond the privileges of the compromised account.

Depending on the affected identity, this could lead to privilege
escalation or broader Active Directory compromise.

Recommendation:
Restrict enrollment permissions to explicitly authorised principals.

Review the template subject-name configuration, EKUs, issuance
requirements, and certificate mapping behaviour.

Remove the template from issuing CAs if it is no longer required.

Review certificates previously issued from the template and revoke
certificates that were issued inappropriately.
```

---

# Severity

Severity depends on the complete trust path.

A useful model is:

```text
Enrollment Accessibility
        +
Template / CA Misconfiguration
        +
Certificate Capability
        +
Identity Mapping
        +
Resulting Identity
        =
Severity
```

---

# Lower-Risk Example

```text
Template
   |
   v
Broad Enrollment
   |
   v
Non-Authentication Certificate
   |
   v
Limited Impact
```

This may represent a hardening issue depending on intended usage.

---

# High-Risk Example

```text
Domain User
    |
    v
Authentication Template
    |
    v
Arbitrary Identity
    |
    v
Privileged User
```

This can represent significant privilege escalation.

---

# Critical Example

```text
Attacker
   |
   v
CA Private Key
   |
   v
Forge Authentication Certificate
   |
   v
Tier 0 Identity
```

This can represent compromise of the PKI trust boundary and potentially the Active Directory environment.

---

# Evidence Checklist

For each AD CS finding record:

```text
CA Name
CA Host
CA Type
Template Name
Template OID
Enrollment Rights
Template ACL
Subject Configuration
SAN Configuration
EKUs
Issuance Requirements
Published CA
Enrollment Endpoint
Certificate Mapping Behaviour
Test Identity
Issued Certificate Serial Number
Authentication Result
Cleanup
```

Do not include reusable private keys in the final report.

---

# AD CS Assessment Checklist

## Preparation

- [ ] Confirm AD CS testing is authorised
- [ ] Confirm certificate enrollment is authorised
- [ ] Confirm privileged identity impersonation restrictions
- [ ] Confirm CA modification restrictions
- [ ] Confirm template modification restrictions
- [ ] Confirm web enrollment testing restrictions
- [ ] Confirm NTLM relay restrictions
- [ ] Define test identity
- [ ] Define cleanup procedure
- [ ] Define stop conditions

## Discovery

- [ ] Identify enterprise CAs
- [ ] Identify standalone CAs
- [ ] Identify Root CAs
- [ ] Identify subordinate CAs
- [ ] Identify issuing CAs
- [ ] Identify CA hostnames
- [ ] Identify PKI DNS names
- [ ] Identify enrollment services
- [ ] Identify certificate templates
- [ ] Identify Online Responders
- [ ] Identify NDES

## CA Enumeration

- [ ] Record CA name
- [ ] Record CA host
- [ ] Determine Enterprise vs Standalone
- [ ] Determine Root vs Subordinate
- [ ] Enumerate published templates
- [ ] Review CA permissions
- [ ] Review certificate-manager permissions
- [ ] Review enrollment-agent restrictions
- [ ] Review request disposition
- [ ] Review web enrollment
- [ ] Review enrollment web services

## Template Enumeration

- [ ] Record template name
- [ ] Record display name
- [ ] Record template version
- [ ] Record template OID
- [ ] Identify issuing CAs
- [ ] Review enrollment rights
- [ ] Review autoenrollment rights
- [ ] Review template ACL
- [ ] Review owner
- [ ] Review subject-name settings
- [ ] Review SAN behaviour
- [ ] Review EKUs
- [ ] Review application policies
- [ ] Review manager approval
- [ ] Review authorized signatures
- [ ] Review private-key settings
- [ ] Review validity period
- [ ] Review renewal period

## Authentication

- [ ] Identify authentication-capable templates
- [ ] Review Client Authentication
- [ ] Review Smart Card Logon
- [ ] Review PKINIT capability
- [ ] Review Any Purpose
- [ ] Review templates without EKUs
- [ ] Review certificate mapping
- [ ] Review SID security extension behaviour
- [ ] Review current Domain Controller hardening

## Permissions

- [ ] Identify broad Enroll rights
- [ ] Identify broad Autoenroll rights
- [ ] Identify GenericAll on templates
- [ ] Identify GenericWrite on templates
- [ ] Identify WriteDACL on templates
- [ ] Identify WriteOwner on templates
- [ ] Identify template ownership
- [ ] Identify CA administrative permissions
- [ ] Identify CA certificate-manager permissions
- [ ] Identify control over enrollment groups

## Enrollment Services

- [ ] Identify `/certsrv/`
- [ ] Identify CA Web Enrollment
- [ ] Identify CES
- [ ] Identify CEP
- [ ] Identify NDES
- [ ] Identify HTTP endpoints
- [ ] Identify HTTPS endpoints
- [ ] Review NTLM authentication
- [ ] Review EPA
- [ ] Review TLS
- [ ] Review network exposure

## ESC Analysis

- [ ] Review ESC1
- [ ] Review ESC2
- [ ] Review ESC3
- [ ] Review ESC4
- [ ] Review ESC5
- [ ] Review ESC6
- [ ] Review ESC7
- [ ] Review ESC8
- [ ] Review ESC9
- [ ] Review ESC10
- [ ] Review ESC11
- [ ] Review ESC12
- [ ] Review ESC13
- [ ] Review ESC14
- [ ] Review ESC15
- [ ] Validate taxonomy against current research
- [ ] Do not rely solely on automated labels

## Tooling

- [ ] Enumerate with native Windows tools
- [ ] Enumerate with LDAP
- [ ] Review certutil output
- [ ] Review certificate stores
- [ ] Enumerate with Certipy
- [ ] Review BloodHound paths
- [ ] Correlate multiple tools
- [ ] Manually validate important findings

## Validation

- [ ] Prefer configuration evidence first
- [ ] Use dedicated test identity
- [ ] Request minimum certificates required
- [ ] Avoid privileged production identities
- [ ] Protect private keys
- [ ] Record certificate serial number
- [ ] Validate authentication only where required
- [ ] Stop after sufficient evidence
- [ ] Revoke test certificate where appropriate
- [ ] Delete exported private keys

## Detection

- [ ] Enable appropriate CA auditing
- [ ] Monitor certificate requests
- [ ] Monitor certificate issuance
- [ ] Monitor certificate revocation
- [ ] Monitor template changes
- [ ] Monitor CA configuration changes
- [ ] Monitor CA permission changes
- [ ] Monitor privileged certificate enrollment
- [ ] Monitor certificate authentication
- [ ] Monitor event 5136 for relevant AD changes
- [ ] Correlate certificate and identity events

## Hardening

- [ ] Restrict enrollment rights
- [ ] Restrict autoenrollment rights
- [ ] Restrict template modification
- [ ] Restrict CA administration
- [ ] Restrict certificate-manager rights
- [ ] Configure enrollment-agent restrictions
- [ ] Secure subject-name configuration
- [ ] Restrict authentication EKUs
- [ ] Require approval where appropriate
- [ ] Require authorized signatures where appropriate
- [ ] Harden certificate mapping
- [ ] Secure web enrollment
- [ ] Enable EPA where applicable
- [ ] Reduce NTLM
- [ ] Protect CA private keys
- [ ] Protect CA backups
- [ ] Use offline Root CA where appropriate
- [ ] Use HSMs where appropriate
- [ ] Apply administrative tiering
- [ ] Monitor PKI infrastructure

## Incident Response

- [ ] Identify suspicious certificate
- [ ] Identify serial number
- [ ] Identify thumbprint
- [ ] Identify requester
- [ ] Identify template
- [ ] Identify CA
- [ ] Identify issue time
- [ ] Identify authentication use
- [ ] Identify private-key exposure
- [ ] Revoke malicious certificate
- [ ] Publish updated revocation information
- [ ] Review template changes
- [ ] Review CA changes
- [ ] Review certificates issued during compromise window
- [ ] Reset credentials where appropriate
- [ ] Do not rely on password reset alone
- [ ] Investigate CA key compromise

## Cleanup

- [ ] Revoke test certificates where required
- [ ] Remove temporary PFX files
- [ ] Remove temporary PEM keys
- [ ] Remove certificate caches
- [ ] Restore template changes
- [ ] Restore CA changes
- [ ] Remove temporary accounts
- [ ] Remove temporary groups
- [ ] Verify no test certificate remains usable
- [ ] Record cleanup evidence

---

# AD CS Testing Model

The basic PKI model is:

```text
Identity
   |
   v
Certificate Request
   |
   v
Certificate Authority
   |
   v
Certificate
```

The cryptographic model is:

```text
Private Key
    +
Public Key
    |
    v
Certificate
    |
    v
CA Signature
```

The trust model is:

```text
Trusted Root
    |
    v
Issuing CA
    |
    v
Certificate
    |
    v
Identity
```

The Enterprise CA model is:

```text
Active Directory
      |
      v
Certificate Templates
      |
      v
Enterprise CA
      |
      v
Certificates
```

The template model is:

```text
Template
   |
   +--> Enrollment Rights
   +--> Subject
   +--> SAN
   +--> EKUs
   +--> Approval
   +--> Signatures
   +--> Private-Key Rules
```

The authentication model is:

```text
Certificate
    +
Private Key
    |
    v
PKINIT / Schannel
    |
    v
Active Directory Identity
```

The PKINIT model is:

```text
Certificate
    |
    v
KDC
    |
    v
TGT
    |
    v
Kerberos
```

The dangerous-template model is:

```text
Low-Privileged Principal
        |
        v
Enroll
        |
        v
Misconfigured Template
        |
        v
Authentication Certificate
        |
        v
Higher-Privileged Identity
```

The template-control model is:

```text
Attacker
   |
   v
Template ACL
   |
   v
Modify Template
   |
   v
Create Dangerous Configuration
   |
   v
Enroll Certificate
```

The web-relay model is:

```text
Authentication Coercion
        |
        v
NTLM
        |
        v
Relay
        |
        v
AD CS Web Enrollment
        |
        v
Certificate
```

The CA-compromise model is:

```text
CA Private Key
      |
      v
Certificate Forgery
      |
      v
Trusted Certificate
      |
      v
Identity Authentication
```

The persistence model is:

```text
Authentication Certificate
          |
          v
Password Reset
          |
          X
Certificate May Remain Valid
```

The safe-assessment model is:

```text
Discover
   |
   v
Enumerate
   |
   v
Analyse
   |
   v
Classify
   |
   v
Validate Minimally
   |
   v
Revoke / Clean Up
```

The defensive model is:

```text
Secure Templates
      +
Secure CA
      +
Secure Enrollment
      +
Strong Certificate Mapping
      +
Protect Private Keys
      +
Monitoring
      =
Secure Enterprise PKI
```

The most important relationship is:

```text
Certificate + Private Key
          =
Credential
```

Another important relationship is:

```text
Certificate Template
        |
        X
Just a PKI Configuration Object
```

A certificate template is also an:

```text
Identity Issuance Policy
```

because it determines:

```text
Who Can Request
What Identity Is Represented
What the Certificate Can Do
```

Another critical relationship is:

```text
Certificate Authority
        |
        X
Just Another Windows Server
```

A CA is part of the identity trust infrastructure.

For penetration testers:

```text
Do Not Ask:
"Does Certipy report an ESC?"

Ask:
"Who can obtain or control a certificate,
which identity can that certificate represent,
how can it authenticate, and what privilege
does that identity provide?"
```

For defenders:

```text
Do Not Ask:
"Is the CA patched?"

Ask:
"Who controls certificate issuance,
which templates can issue authentication
credentials, how are certificates mapped,
and can every privileged certificate be
detected and revoked?"
```

The complete security relationship is:

```text
Principal
   |
   v
Enrollment Permission
   |
   v
Certificate Template
   |
   v
Certificate Authority
   |
   v
Certificate
   |
   v
Certificate Mapping
   |
   v
Authentication
   |
   v
Privilege
```

AD CS must therefore be assessed as part of the Active Directory identity system rather than as a separate certificate-management feature.

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](../methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](../enumeration.md)

Credential Access:

[Active Directory Credential Access](../credential-access.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

Groups:

[Active Directory Groups](../groups.md)

Group Policy:

[Active Directory Group Policy](../group-policy.md)

Kerberos:

[Kerberos](../kerberos.md)

NTLM:

[NTLM](../ntlm.md)

NTLM Relay:

[NTLM Relay](../ntlm-relay.md)

Authentication Coercion:

[Authentication Coercion](../authentication-coercion.md)

Shadow Credentials:

[Active Directory Shadow Credentials](../shadow-credentials.md)

BloodHound:

[BloodHound](../bloodhound.md)

The next page is:

```text
active-directory/ad-cs/enumeration.md
```

After that, the AD CS section can cover the individual ESC attack paths.

---

# References

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services Documentation](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD CS Overview

[Microsoft - What is Active Directory Certificate Services?](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Templates

[Microsoft - Certificate Template Concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Manage Certificate Templates

[Microsoft - Manage Certificate Templates](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/manage-certificate-templates){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - CA Web Enrollment

[Microsoft - Certification Authority Web Enrollment](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-authority-web-enrollment){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Request Certificates Using Web Enrollment

[Microsoft - Request a Certificate Using CA Web Enrollment](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/request-certificate-windows-server){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Network Device Enrollment Service

[Microsoft - Network Device Enrollment Service](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/network-device-enrollment-service-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD CS PowerShell Deployment Module

[Microsoft - ADCSDeployment PowerShell Module](https://learn.microsoft.com/en-us/powershell/module/adcsdeployment/?view=windowsserver2025-ps){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Steal or Forge Authentication Certificates

[MITRE ATT&CK - T1649](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Active Directory Certificate Services should be treated as:

```text
Identity Infrastructure
```

not merely:

```text
Certificate Infrastructure
```

The reason is simple:

```text
Certificate
    +
Private Key
    |
    v
Authentication
```

An organisation may carefully protect:

```text
Passwords
NT Hashes
Kerberos Keys
```

while overlooking:

```text
Certificates
Private Keys
Certificate Templates
CA Permissions
Enrollment Services
```

This creates an alternative identity attack surface.

The fundamental AD CS security model is:

```text
Who Can Enroll?
      |
      v
What Can They Request?
      |
      v
Which Identity Does It Represent?
      |
      v
What Can the Certificate Do?
      |
      v
How Is It Mapped?
      |
      v
What Privilege Results?
```

The CA itself must also be treated as a critical trust system:

```text
CA
 |
 v
Signs Certificate
 |
 v
Establishes Trust
```

Therefore:

```text
CA Compromise
```

can become:

```text
Identity Trust Compromise
```

Certificate templates are equally important because they define the rules governing certificate issuance.

```text
Template
   |
   +--> Who?
   +--> Which Identity?
   +--> Which Purpose?
   +--> Which Approval?
   +--> Which Key?
```

For penetration testers, the correct workflow is:

```text
Discover
   |
   v
Enumerate CAs
   |
   v
Enumerate Templates
   |
   v
Analyse Permissions
   |
   v
Analyse Certificate Capabilities
   |
   v
Analyse Identity Mapping
   |
   v
Map ESC Conditions
   |
   v
Validate Minimally
```

For defenders:

```text
Protect CA
   |
   v
Protect Templates
   |
   v
Restrict Enrollment
   |
   v
Secure Mapping
   |
   v
Protect Private Keys
   |
   v
Monitor Issuance
   |
   v
Maintain Revocation
```

The central lesson is:

```text
Certificate Issuance
       =
Credential Issuance
```

when the certificate can authenticate.

That makes AD CS one of the most important trust systems to include in a comprehensive Active Directory security assessment.
