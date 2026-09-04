# AD CS Golden Certificates - CA Private Key Compromise

A Golden Certificate is a forged certificate created using the private key of a trusted Active Directory Certificate Services (AD CS) Certification Authority.

Unlike many AD CS ESC techniques, Golden Certificates do not primarily depend on a vulnerable certificate template.

The core problem is:

```text
Enterprise CA Private Key Compromised
                |
                v
Attacker Can Sign Certificates
                |
                v
Certificates Chain to Trusted CA
                |
                v
Forged Enterprise Identities
```

If an attacker obtains the private key belonging to an Enterprise CA trusted for Active Directory authentication, they may be able to create certificates representing users or computers without submitting normal certificate requests to the CA.

Conceptually:

```text
CA Certificate
      +
CA Private Key
      |
      v
Attacker-Controlled Certificate Signing
      |
      v
Forged Certificate
      |
      v
Trusted by Domain
```

This is commonly called:

```text
Golden Certificate
```

The concept is similar to a Golden Ticket in that compromise of a high-value trust key allows authentication material to be generated independently of the normal issuance workflow.

However:

```text
Golden Ticket
```

and:

```text
Golden Certificate
```

attack different trust systems.

!!! danger "Tier 0 compromise"
    Compromise of an Enterprise CA signing key should generally be treated as a Tier 0 security incident. An attacker capable of signing trusted authentication certificates may retain access independently of passwords, normal certificate-template controls and ordinary certificate enrollment monitoring.

!!! warning "Authorised testing only"
    Do not extract production CA private keys or generate certificates for privileged production identities merely to prove impact. During assessments, begin with CA architecture, key-protection, permissions, backup controls and configuration. If cryptographic validation is explicitly required, use a dedicated lab CA or an approved test CA and test identity.

---

# Golden Certificate at a Glance

Normal certificate issuance:

```text
User
 |
 v
Certificate Request
 |
 v
Certificate Template
 |
 v
Enterprise CA
 |
 v
Policy Validation
 |
 v
Certificate Issued
```

Golden Certificate:

```text
Attacker
 |
 v
CA Private Key
 |
 v
Offline Certificate Generation
 |
 v
No Normal Enrollment
 |
 v
No Template Approval
 |
 v
Trusted Certificate
```

The critical difference is:

```text
Normal Certificate
=
CA Decides What to Sign
```

whereas:

```text
Golden Certificate
=
Attacker Possessing CA Key
Decides What to Sign
```

---

# Why the CA Private Key Matters

Every CA certificate contains:

```text
Public Key
```

The corresponding:

```text
Private Key
```

is used by the CA to cryptographically sign certificates.

Conceptually:

```text
CA Private Key
      |
      v
Signature
      |
      v
Issued Certificate
      |
      v
CA Public Key Verifies Signature
```

Clients trust certificates because they trust the issuing CA.

If the private key is stolen:

```text
Trust in the CA
```

can potentially be abused by whoever possesses the key.

---

# PKI Trust Model

Consider:

```text
Root CA
   |
   v
Enterprise Issuing CA
   |
   v
User Certificate
```

A domain controller does not normally contact the CA and ask:

```text
"Did you really issue this certificate?"
```

for every authentication attempt.

Instead, it validates properties such as:

```text
Certificate Signature
Certificate Chain
Validity
Revocation
EKUs
Identity Mapping
```

If an attacker can generate a cryptographically valid certificate using the CA private key, the certificate can appear legitimate from the perspective of signature validation.

---

# Golden Certificate Concept

The attack is:

```text
Compromise CA Signing Key
        |
        v
Create Certificate
        |
        v
Sign with CA Private Key
        |
        v
Certificate Chains to Trusted CA
        |
        v
Use Certificate
```

The certificate may never have been:

```text
Requested from CA
Approved by CA
Recorded in CA Database
```

That distinction has major detection implications.

---

# Golden Certificate vs Normal Certificate Abuse

Normal AD CS abuse:

```text
Attacker
   |
   v
Vulnerable Template / CA
   |
   v
Certificate Request
   |
   v
CA Issues Certificate
```

Golden Certificate:

```text
Attacker
   |
   v
CA Private Key
   |
   v
Attacker Signs Certificate
```

The second path bypasses the normal enrollment process entirely.

---

# Golden Certificate vs Golden Ticket

Golden Ticket:

```text
KRBTGT Key
   |
   v
Forge TGT
```

Golden Certificate:

```text
CA Private Key
   |
   v
Forge Certificate
   |
   v
Certificate Authentication
   |
   v
Obtain TGT
```

---

# Trust Root Comparison

```text
Golden Ticket
     |
     v
Kerberos Trust
     |
     v
KRBTGT
```

```text
Golden Certificate
     |
     v
PKI Trust
     |
     v
CA Signing Key
```

Both involve compromise of high-value cryptographic trust material.

---

# Why Golden Certificates Are Powerful

A Golden Certificate can potentially bypass controls around:

```text
Password Changes
Password Rotation
Account Password Complexity
NTLM Restrictions
Certificate Enrollment Permissions
Certificate Template Permissions
Manager Approval
Authorised Signatures
```

because the attacker is no longer requesting a certificate through the normal CA workflow.

---

# Password Reset Does Not Fix the CA Key

Suppose an attacker forges a certificate for:

```text
alice@corp.example
```

Then Alice's password is changed.

The attacker's certificate may still remain useful because:

```text
Certificate Authentication
```

does not depend on Alice's password.

---

# Template Remediation Does Not Fix the CA Key

Suppose the organisation fixes:

```text
ESC1
```

and removes:

```text
Domain Users -> Enroll
```

from a vulnerable template.

If the CA private key has already been compromised:

```text
Template Remediation
```

does not remove the attacker's ability to sign certificates.

---

# CA Key Compromise Is the Root Cause

The fundamental issue is:

```text
Attacker Possesses
Trusted CA Signing Key
```

Therefore remediation must address:

```text
The CA Trust Key
```

not merely the certificate template.

---

# Potential Sources of CA Private Key Compromise

A CA private key can become exposed through several paths.

Examples include:

```text
CA Server Compromise
CA Backup Exposure
Private Key Export
Weak File Permissions
Weak Backup Permissions
Virtual Machine Snapshot
System-State Backup
CA Database Backup Workflow
HSM Misconfiguration
Cloud Backup Exposure
Administrator Credential Compromise
Malicious PKI Administrator
```

---

# CA Server Compromise

If the attacker obtains:

```text
Local Administrator
```

or:

```text
SYSTEM
```

on an Enterprise CA, the security impact is already extremely serious.

The attacker may potentially:

```text
Modify CA Configuration
Issue Certificates
Access Backup Material
Interact with Key Storage
Modify Certificate Services
Manipulate Audit Configuration
```

Whether the private key itself can be exported depends on how it is protected.

---

# Exportable CA Keys

During CA setup or key generation, private-key properties determine whether the key can be exported.

A software-protected exportable CA key creates a substantially different risk profile from:

```text
Non-Exportable HSM-Protected Key
```

However:

```text
Non-Exportable
```

does not automatically mean:

```text
Cannot Be Abused
```

An attacker controlling the CA may still be able to invoke signing operations.

---

# Software Key Storage

A CA key may be protected through Windows cryptographic providers such as:

```text
CSP
```

or:

```text
KSP
```

depending on the CA configuration and operating system.

The exact security properties depend on:

```text
Provider
Key Storage
Export Policy
ACLs
Machine Protection
Credential Protection
Hardware Protection
```

---

# Hardware Security Modules

High-value CAs may store signing keys in:

```text
HSM
```

or another hardware-backed key-protection system.

Conceptually:

```text
certsrv.exe
     |
     v
Crypto Provider
     |
     v
HSM
     |
     v
CA Private Key
```

The intended security property is:

```text
Private Key Never Leaves HSM
```

---

# HSM Does Not Eliminate All Risk

Even when the key cannot be extracted:

```text
Attacker Controls CA
```

may still mean:

```text
Attacker Can Request Signing Operations
```

depending on HSM policy and CA architecture.

Therefore distinguish:

```text
Key Extraction
```

from:

```text
Signing-Key Abuse
```

---

# ESC12 Relationship

ESC12 specifically concerns certain AD CS deployments using:

```text
YubiHSM2
```

and weaknesses affecting CA private-key protection.

ESC12 can therefore become one path toward:

```text
CA Signing Capability
```

or potentially:

```text
CA Key Compromise
```

depending on the exact deployment.

See:

[AD CS ESC12](esc12.md)

---

# CA Backup Exposure

CA backup material is especially sensitive.

A CA backup can include:

```text
CA Certificate
CA Private Key
CA Database
Configuration
```

depending on the backup method.

If a backup containing the CA private key is stolen:

```text
CA Server Can Be Secure
```

while:

```text
CA Trust Is Still Compromised
```

---

# Backup Security Model

```text
Enterprise CA
     |
     v
CA Backup
     |
     v
Backup Server
     |
     v
Backup Repository
```

Every system in this chain can become part of the CA security boundary.

---

# Virtual Machine Snapshots

If the CA is virtualised:

```text
VM Snapshot
```

or:

```text
Hypervisor Backup
```

may contain sensitive CA state.

Therefore:

```text
Virtualisation Administrators
```

and:

```text
Backup Administrators
```

can become highly privileged in the PKI trust model.

---

# Offline Root CA vs Enterprise Issuing CA

Many enterprise PKI architectures use:

```text
Offline Root CA
      |
      v
Enterprise Issuing CA
```

The offline root should normally remain:

```text
Powered Off
Disconnected
Physically Protected
```

except when required for controlled PKI operations.

---

# Root CA Compromise

Compromise of the root CA private key can be even more severe than compromise of one issuing CA.

Conceptually:

```text
Root CA Key
    |
    +--> Issuing CA 1
    |
    +--> Issuing CA 2
    |
    +--> Issuing CA 3
```

An attacker controlling the root trust key can potentially undermine the entire PKI hierarchy.

---

# Enterprise Issuing CA Compromise

Compromise of an Enterprise issuing CA typically affects:

```text
Certificates Trusted
Through That CA
```

This can still represent domain-wide or forest-wide impact depending on the PKI architecture.

---

# Certificate Authentication Requirements

A forged certificate must still satisfy the authentication system's requirements.

These may include:

```text
Trusted Chain
Valid Time
Suitable EKU
Identity Information
Certificate Mapping
Revocation Behaviour
Domain Controller Certificate
PKINIT Support
```

A CA private key is extraordinarily powerful, but certificate authentication still follows protocol validation rules.

---

# Authentication EKUs

Relevant EKUs can include:

```text
Client Authentication
Smart Card Logon
PKINIT Client Authentication
```

---

# Client Authentication

OID:

```text
1.3.6.1.5.5.7.3.2
```

---

# Smart Card Logon

OID:

```text
1.3.6.1.4.1.311.20.2.2
```

---

# PKINIT Client Authentication

OID:

```text
1.3.6.1.5.2.3.4
```

---

# Modern Certificate Mapping

Golden Certificate analysis must account for modern strong certificate mapping.

Microsoft's certificate-based authentication hardening introduced stronger relationships between certificates and Active Directory identities.

Therefore a current assessment should not blindly reproduce historical:

```text
UPN Only
```

certificate-forging techniques.

---

# SID Security Extension

The Microsoft NTDS CA security extension uses:

```text
1.3.6.1.4.1.311.25.2
```

and can provide strong certificate-to-account binding.

---

# Forged Certificate Identity

An attacker controlling a CA private key can control certificate contents during offline certificate creation.

However, the exact identity information required for successful authentication depends on:

```text
Domain Controller Version
Patch Level
Certificate Mapping
Strong Binding
Certificate Extensions
Authentication Protocol
```

---

# Current 2026 Assessment Principle

Do not assume:

```text
Old Golden Certificate PoC
=
Works Unchanged Today
```

Instead determine:

```text
Current DC Behaviour
```

and:

```text
Current Certificate Mapping Requirements
```

before evaluating authentication impact.

---

# CA Certificate Enumeration

Before assessing Golden Certificate risk, identify the Enterprise CAs.

PowerShell:

```powershell
Import-Module ActiveDirectory
```

Retrieve the Configuration naming context:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
```

Enumerate Enterprise CAs:

```powershell
$base = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $base -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties dNSHostName,cACertificate,certificateTemplates |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Certipy Enumeration

Certipy provides useful AD CS discovery.

Check the installed version:

```bash
certipy --version
```

Then:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Use:

```bash
certipy find -h
```

to confirm options for the installed release.

---

# Identify CA Host

Record:

```text
CA Name
CA Hostname
CA Type
CA Certificate
Published Templates
```

Example:

```text
CA Name:
CORP-CA

Hostname:
ca01.corp.example
```

---

# Native CA Configuration

On an authorised CA host:

```cmd
certutil -getreg CA
```

This provides CA configuration information without changing the system.

---

# CA Certificate Store

On the CA:

```cmd
certutil -store my
```

PowerShell:

```powershell
Get-ChildItem Cert:\LocalMachine\My
```

Review certificates associated with:

```text
Certificate Services
```

---

# Identify CA Certificate

Useful properties include:

```text
Subject
Issuer
Serial Number
Thumbprint
Validity
Public Key Algorithm
Signature Algorithm
```

---

# Determine Private Key Presence

PowerShell:

```powershell
Get-ChildItem Cert:\LocalMachine\My |
    Select-Object Subject,Thumbprint,HasPrivateKey,NotAfter
```

For the CA certificate, expect:

```text
HasPrivateKey = True
```

on the active CA host.

This confirms the host has access to the signing key.

It does not prove that the key is exportable.

---

# Identify Cryptographic Provider

Use CA configuration and certificate information to determine the provider protecting the key.

Useful questions include:

```text
Software Provider?
Legacy CSP?
CNG KSP?
Hardware Provider?
HSM?
```

---

# certutil Key Information

Administrators can use:

```cmd
certutil -store my
```

and relevant CA configuration commands to inspect key-provider information.

The objective during assessment is:

```text
Determine Protection Model
```

not:

```text
Extract the Key
```

---

# Private Key Exportability

Determine whether the CA key was configured as exportable.

This may be available through:

```text
PKI Documentation
CA Build Records
Key Ceremony Records
Provider Configuration
HSM Configuration
Backup Procedures
```

Avoid attempting private-key export merely to answer this question in production.

---

# CA Backup Configuration

Review:

```text
Backup Product
Backup Destination
Backup Encryption
Backup ACLs
Backup Operators
Retention
Offline Copies
Recovery Procedures
```

---

# Key Backup Procedures

Ask:

```text
Is the CA private key backed up?

Where?

How is the backup encrypted?

Who knows the password?

Who can retrieve the backup?

Is access logged?

Is the backup offline?

Is the backup periodically tested?
```

---

# CA Private Key Protection Review

A strong assessment should evaluate:

```text
Key Storage
      |
      +--> Software
      |
      +--> TPM / Hardware
      |
      +--> HSM
```

Then:

```text
Exportability
Access Control
Administrative Access
Backup
Recovery
Auditing
```

---

# Tier 0 Classification

Enterprise CA systems should generally be treated as:

```text
Tier 0
```

because compromise can affect:

```text
Authentication
Identity
Trust
Code Signing
Server Identity
Client Identity
```

depending on the PKI.

---

# CA Administrator Review

Identify:

```text
Local Administrators
Enterprise Admins
CA Administrators
Certificate Managers
Backup Operators
PKI Service Accounts
HSM Administrators
Hypervisor Administrators
```

where relevant.

---

# CA Network Exposure

Review whether the CA exposes unnecessary services.

Examples:

```text
SMB
RDP
WinRM
RPC
Web Enrollment
Remote Registry
Third-Party Management Agents
Backup Agents
```

Every additional service increases the attack surface of a Tier 0 system.

---

# CA Application Control

Consider:

```text
WDAC
AppLocker
EDR
Privileged Access Workstations
Restricted Administrative Logon
```

for Enterprise CA hosts.

---

# CA Interactive Logon

Administrative interactive logon to an Enterprise CA should be tightly restricted.

Review:

```text
Who Can RDP?
Who Can WinRM?
Who Can Log On Locally?
Who Can Access Through Management Platforms?
```

---

# Safe Assessment Workflow

A production-safe Golden Certificate assessment can normally stop before private-key extraction.

Use:

```text
Identify CA
    |
    v
Determine Trust Scope
    |
    v
Review CA Host Security
    |
    v
Review Key Protection
    |
    v
Review Exportability
    |
    v
Review Backup Security
    |
    v
Review Administrative Paths
    |
    v
Determine Potential Impact
```

---

# When Active Validation Is Necessary

If the engagement explicitly requires proof of cryptographic impact:

```text
Use Dedicated Lab CA
```

or:

```text
Approved Test CA
```

rather than extracting a production signing key.

---

# Lab Validation Model

```text
Lab Enterprise CA
      |
      v
Export Test CA Key
      |
      v
Generate Test Certificate
      |
      v
Sign with Test CA
      |
      v
Authenticate Test Account
```

This demonstrates the Golden Certificate principle without compromising production trust.

---

# Certipy Golden Certificate Functionality

Certipy includes functionality for working with CA certificates and forging certificates.

Before any lab validation, inspect the current syntax:

```bash
certipy forge -h
```

A conceptual workflow is:

```text
CA PFX
   |
   v
Certipy Forge
   |
   v
Forged PFX
```

Do not point this workflow at a production CA private key unless the engagement explicitly authorises CA-key compromise testing.

---

# Lab-Only Forge Example

In an isolated lab with a test CA key:

```bash
certipy forge \
    -ca-pfx lab-ca.pfx \
    -upn 'test-admin@lab.example' \
    -sid 'S-1-5-21-111111111-222222222-333333333-1105' \
    -out test-admin.pfx
```

Confirm current options first:

```bash
certipy forge -h
```

Tool syntax can change between releases.

---

# Why the SID Matters

Modern certificate mapping may require stronger identity information than:

```text
UPN
```

alone.

The SID represents the specific Active Directory security principal.

Conceptually:

```text
test-admin@lab.example
        |
        v
SID
        |
        v
S-1-5-21-...-1105
```

---

# Lab Authentication

After generating a test certificate in a controlled lab, Certipy can be used to test certificate authentication:

```bash
certipy auth -pfx test-admin.pfx -dc-ip 10.10.10.10
```

This should only target the approved test domain.

---

# Authentication Result

A successful certificate authentication may obtain:

```text
TGT
```

and depending on the tooling and account conditions, additional authentication material may be recoverable.

The important Golden Certificate proof is:

```text
Forged Certificate
       |
       v
Trusted by Domain
       |
       v
Authentication Accepted
```

---

# Golden Certificate Persistence

Suppose an attacker compromises:

```text
CORP-CA
```

and obtains its signing key.

The organisation then:

```text
Resets Administrator Password
```

The attacker's signing key remains valid.

They can potentially create another certificate.

---

# Persistence Model

```text
CA Private Key
     |
     v
Forge Certificate A
     |
     v
Use Access
     |
     v
Certificate Revoked
     |
     v
Forge Certificate B
```

This continues until the underlying CA trust is remediated.

---

# Why Revoking One Certificate Is Insufficient

If the attacker controls the CA key:

```text
Revoke Forged Certificate
```

does not solve:

```text
Attacker Can Forge Another
```

The trust anchor itself is compromised.

---

# Forged Certificates May Not Be in the CA Database

A normal certificate:

```text
Request
   |
   v
CA Database
   |
   v
Issued Certificate
```

A Golden Certificate:

```text
Attacker
   |
   v
Offline Signing
   |
   v
Certificate
```

The forged certificate may therefore have:

```text
No Corresponding CA Request
```

---

# Detection Challenge

This means:

```text
Certificate Used
```

may exist without:

```text
4886 Request Event
```

or:

```text
4887 Issuance Event
```

for the certificate.

This mismatch can be a valuable detection signal.

---

# Detection Model

```text
Certificate Authentication
        |
        v
Certificate Serial / Issuer
        |
        v
Search CA Database
        |
        +--> Found -> Normal Investigation
        |
        +--> Missing
                |
                v
         Possible Forgery
```

---

# Certificate Serial Numbers

Forged certificates may contain attacker-selected or tool-generated serial numbers.

Defenders should not rely solely on:

```text
Serial Number Looks Strange
```

because legitimate CA serial-number behaviour varies.

Instead correlate:

```text
Issuer
Serial
Certificate
CA Database
Authentication
```

---

# Certificate Validity

Attackers forging certificates can potentially select unusual validity periods.

Look for:

```text
Unexpected NotBefore
Unexpected NotAfter
Excessive Lifetime
```

relative to the organisation's normal certificate policy.

---

# Certificate Template Information

Normal Enterprise CA-issued certificates may contain template-related information.

An offline forged certificate may differ from normal certificates in:

```text
Extensions
Template Metadata
Issuance Policies
Serial Behaviour
Validity
CRL Distribution Points
Authority Information Access
```

depending on how it was generated.

---

# Avoid Single-Indicator Detection

Do not detect Golden Certificates only through:

```text
Missing Template Extension
```

Attackers may attempt to mimic legitimate certificates.

Use multiple signals.

---

# Event 4768

Certificate-based Kerberos authentication can generate:

```text
4768
```

TGT request events.

Modern Windows versions can expose certificate-related information useful for investigation.

---

# Correlate Authentication with CA Records

A high-value detection workflow is:

```text
4768
  |
  v
Certificate Information
  |
  v
Issuer / Serial
  |
  v
CA Database Search
```

If the CA says:

```text
Never Issued
```

the certificate deserves immediate investigation.

---

# CA Certificate Services Events

Useful CA auditing includes events such as:

```text
4886
4887
```

for certificate requests and issuance.

Additional CA auditing should be enabled according to organisational requirements.

---

# CA Backup Events

Windows Certificate Services auditing can also provide visibility into CA backup and restore operations.

Events commonly associated with CA backup and restore include:

```text
4876
4877
```

where relevant auditing is enabled.

Unexpected CA backup activity should be investigated.

---

# Private Key Access

Where supported by the provider and audit configuration, cryptographic activity can generate events such as:

```text
5058
5059
5061
```

These can provide useful context around key-file or cryptographic operations.

Exact event availability depends on:

```text
Provider
Audit Policy
Windows Version
Key Type
Operation
```

---

# File Access Auditing

If software key material or backup files are protected by filesystem ACLs, event:

```text
4663
```

may provide access telemetry when appropriate object-access auditing and SACLs are configured.

---

# HSM Auditing

Hardware-protected CAs should use:

```text
HSM Native Audit Logs
```

to monitor:

```text
Authentication
Key Operations
Administrative Changes
Signing
Backup
Restore
Configuration
```

---

# CA EDR Monitoring

Enterprise CA hosts should receive strong endpoint monitoring.

High-signal behaviours include:

```text
Unexpected PowerShell
Unexpected certutil
Private-Key Backup
PFX Creation
Registry Modification
New Administrative Tools
Credential Dumping
Security Tool Tampering
Unexpected Network Connections
```

---

# certutil Is Not Automatically Malicious

Administrators legitimately use:

```text
certutil
```

for CA management.

Detection should therefore consider:

```text
User
Command Line
Host
Time
Change Ticket
Parent Process
Related Activity
```

rather than alerting solely on process name.

---

# Monitor PFX Creation

Unexpected:

```text
.pfx
```

or:

```text
.p12
```

files on a CA are high-value signals.

Especially investigate files created in:

```text
Temp
User Profiles
Public Directories
Network Shares
Backup Staging Areas
```

---

# Monitor CA Key Backup

A CA private-key backup should be:

```text
Rare
Planned
Documented
Controlled
Audited
```

Unexpected key backup is a major incident indicator.

---

# Monitor CA Configuration Changes

Monitor:

```text
HKLM\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration
```

for unexpected changes.

---

# Monitor Certificate Services

Watch for unexpected:

```text
CertSvc Stop
CertSvc Start
Configuration Changes
Backup Operations
Provider Changes
```

---

# Monitor Administrative Logons

Unexpected privileged logons to:

```text
CA Server
```

should receive high priority.

Especially investigate:

```text
Domain Admin
Enterprise Admin
Backup Administrator
Unusual Service Account
New Local Administrator
```

---

# BloodHound

BloodHound can help identify attack paths leading to:

```text
Enterprise CA
```

or PKI administration.

Important relationships can include:

```text
Administrative Rights
Remote Access
PKI Object Control
Template Control
CA Control
```

---

# GoldenCert Concept in BloodHound

Modern BloodHound AD CS modelling includes the concept of:

```text
GoldenCert
```

representing control capable of enabling CA-certificate/private-key compromise or equivalent CA-level certificate forgery.

Use BloodHound as:

```text
Attack Path Context
```

rather than proof that a private key has actually been extracted.

---

# GoldenCert Does Not Mean Key Already Stolen

A graph edge may indicate:

```text
Principal Has Sufficient Control
```

to compromise the CA trust.

It does not necessarily mean:

```text
CA Private Key Has Already Been Exported
```

Keep:

```text
Potential
```

and:

```text
Observed Compromise
```

separate.

---

# Protect the CA Host

The CA host should receive Tier 0 protections.

Recommended controls include:

```text
Dedicated Administration
Privileged Access Workstations
Restricted RDP
Restricted WinRM
Host Firewall
EDR
Application Control
Credential Guard where appropriate
Secure Boot
Patch Management
Minimal Software
Network Segmentation
```

---

# Avoid General-Purpose Use

Do not use an Enterprise CA as:

```text
File Server
Web Browsing Workstation
Administrative Jump Box
Software Development Host
General Management Server
```

Reduce the attack surface.

---

# Protect CA Administrators

CA administrators should use dedicated privileged identities.

Avoid:

```text
Email
Web Browsing
Office Applications
General User Activity
```

from CA administrative accounts.

---

# Protect Backups

CA backups should use:

```text
Strong Encryption
Restricted ACLs
Offline Protection
Separate Administrative Boundary
Access Logging
Secure Recovery Process
```

---

# Backup Passwords

If a CA private key is stored in a password-protected PFX:

```text
The Password Becomes Tier 0 Material
```

Protect it accordingly.

Do not store the PFX and its password together.

---

# HSM Recommendations

For high-value enterprise CAs, consider hardware-backed key protection.

A strong design includes:

```text
Non-Exportable CA Key
       |
       v
HSM
       |
       v
Restricted Authentication
       |
       v
Least Capabilities
       |
       v
Audited Signing
```

---

# HSM Administrative Separation

Where supported, separate:

```text
CA Administrator
```

from:

```text
HSM Administrator
```

and:

```text
Backup / Recovery Administrator
```

to reduce single-person compromise.

---

# Root CA Protection

Offline roots should remain:

```text
Offline
Physically Protected
Access Controlled
Audited
Used Only When Required
```

---

# Issuing CA Lifetime

Long-lived CA keys increase the potential persistence window following compromise.

CA lifetime and key-rotation strategy should be part of PKI governance.

---

# Incident Response - Suspected CA Key Theft

If CA private-key theft is suspected:

```text
Treat as Major Identity Incident
```

The response may require:

```text
CA Isolation
Forensic Preservation
Key Rotation
CA Certificate Replacement
Certificate Reissuance
Trust Store Updates
Revocation
CRL Publication
Application Validation
```

This is significantly more complex than resetting an account password.

---

# Do Not Immediately Destroy Evidence

Before rebuilding or rotating:

```text
Preserve Evidence
```

where operationally possible.

Capture:

```text
CA Configuration
Event Logs
EDR Telemetry
Registry
CA Database
CA Certificates
Backup Logs
HSM Logs
Administrative Logs
Network Telemetry
```

---

# Determine Compromise Type

Establish whether the attacker obtained:

```text
CA Host Control
```

only,

```text
Signing Capability
```

or:

```text
Actual CA Private Key Material
```

These have different recovery implications.

---

# Key Extraction vs Signing Oracle

```text
CA Host Compromised
       |
       v
Can Attacker Sign?
       |
       +--> Yes
       |
       v
Can Attacker Export Key?
       |
       +--> No -> Signing Abuse
       |
       +--> Yes -> Key Theft
```

Both are serious.

Key theft is especially dangerous because the attacker can continue signing:

```text
Offline
```

after losing access to the CA host.

---

# Determine Key Exposure Window

Establish:

```text
When Could the Key First Have Been Stolen?
```

Review:

```text
Initial CA Compromise
Backup Exposure
Administrator Compromise
HSM Events
Key Backup Operations
PFX Creation
File Access
```

---

# Search for Forged Certificates

Do not search only the CA database.

A Golden Certificate may not appear there.

Instead review:

```text
Certificate Authentication
TLS Telemetry
Endpoint Certificate Stores
Kerberos Events
Application Authentication
Network Captures
EDR
```

---

# Issuer and Serial Correlation

Build an inventory:

```text
Observed Certificate
       |
       +--> Issuer
       +--> Serial
       +--> Subject
       +--> SAN
       +--> EKU
       +--> Validity
```

Then compare against:

```text
CA Database
```

---

# Revocation Challenges

If a forged certificate's serial number is known, it may potentially be revoked.

But:

```text
Attacker Still Has CA Key
```

means another certificate can be created.

Therefore revocation alone is not sufficient.

---

# CA Key Rotation

If the CA private key is confirmed compromised, the organisation may need to:

```text
Generate New CA Key
```

and potentially:

```text
Renew CA Certificate
```

depending on the architecture and incident-response plan.

This should be performed by qualified PKI administrators.

---

# CA Replacement

In severe cases:

```text
Rebuild / Replace CA
```

may be required.

The exact procedure depends on:

```text
Root vs Issuing CA
PKI Hierarchy
Applications
Certificate Lifetimes
Revocation Infrastructure
Trust Distribution
HSM
```

---

# Reissue Certificates

Certificates issued under the compromised CA may need to be:

```text
Reissued
```

under a new trust configuration.

This can include:

```text
User Certificates
Computer Certificates
Domain Controller Certificates
Web Certificates
VPN Certificates
802.1X Certificates
Code-Signing Certificates
Service Certificates
```

depending on the CA's usage.

---

# Trust Store Updates

If the compromised CA certificate must be removed from trust:

```text
Windows Trust Stores
Applications
Network Appliances
VPN Infrastructure
Linux Systems
Java Trust Stores
Browsers
Mobile Devices
```

may require updates.

---

# Domain Controller Certificates

Pay special attention to certificates used by:

```text
Domain Controllers
```

because AD certificate authentication depends on PKI trust.

---

# CRL and Revocation Infrastructure

Review:

```text
CRL Distribution Points
Authority Information Access
OCSP
CRL Publication
Replication
Availability
```

during recovery.

---

# CA Compromise Is an Enterprise Recovery Problem

A useful mental model is:

```text
User Password Compromise
        |
        v
Reset User Password
```

versus:

```text
CA Private Key Compromise
        |
        v
Repair Enterprise Trust
```

The second is substantially more complex.

---

# Reporting Golden Certificate Risk

Avoid a finding title such as:

```text
Golden Certificate
```

without explaining the root cause.

Prefer:

```text
Enterprise CA Private Key Can Be Compromised
```

or:

```text
Insufficient Protection of Enterprise Certification Authority Signing Key
```

or:

```text
Compromise of Enterprise CA Enables Trusted Certificate Forgery
```

---

# Example Finding - Exportable CA Key

```text
Finding:
Enterprise Certification Authority Signing Key Is Insufficiently
Protected

Affected Host:
ca01.corp.example

Affected CA:
CORP-CA

Description:
The Enterprise Certification Authority signing key is protected by
software-based key storage and is configured in a manner that permits
private-key export by sufficiently privileged administrators.

The CA is trusted for Active Directory certificate authentication.

Compromise of the CA host or an account with sufficient administrative
rights could therefore expose the CA signing key.

Possession of this key would allow an attacker to generate certificates
that cryptographically chain to the organisation's trusted Enterprise
CA without submitting the certificates through the normal enrollment
workflow.

Impact:
An attacker obtaining the CA private key could potentially create
trusted authentication certificates for Active Directory principals.

Such certificates may remain useful independently of account password
changes and certificate-template remediation.

Because forged certificates can be generated offline, they may not
produce corresponding certificate request or issuance records in the
CA database.

Compromise of the signing key should therefore be treated as compromise
of a Tier 0 trust asset.

Recommendation:
Protect Enterprise CA signing keys using a hardware-backed,
non-exportable key where appropriate to the organisation's PKI
architecture.

Restrict administrative access to the CA, protect CA backups as Tier 0
assets, separate PKI administration roles and monitor private-key and
CA backup operations.

Develop and test a documented CA key-compromise recovery procedure.
```

---

# Example Finding - Exposed CA Backup

```text
Finding:
Enterprise CA Private Key Exposed Through Insecure Backup Storage

Affected CA:
CORP-CA

Description:
A backup of the Enterprise Certification Authority containing private
key material was accessible to principals outside the intended PKI
administrative boundary.

The backup contains cryptographic material capable of representing the
trusted Enterprise CA.

Impact:
An attacker obtaining the backup and associated protection material may
be able to recover the CA signing key.

This could permit offline creation of certificates that chain to the
trusted CA, potentially enabling long-term certificate-based
impersonation.

The attacker would no longer require access to the CA server to
generate additional certificates.

Recommendation:
Immediately restrict access to the affected backup and investigate
whether it has been accessed.

Protect CA backup material using strong encryption and Tier 0 access
controls.

If compromise of the CA private key cannot be ruled out, initiate the
organisation's CA key-compromise recovery process and evaluate CA key
rotation or replacement.
```

---

# Example Finding - CA Host Compromise

```text
Finding:
Administrative Control of Enterprise CA Enables PKI Trust Compromise

Affected Host:
ca01.corp.example

Affected CA:
CORP-CA

Description:
The tested security principal can obtain administrative control of the
Enterprise Certification Authority host.

The CA is trusted for Active Directory authentication and represents a
Tier 0 security asset.

Administrative control of the CA can permit modification of
Certificate Services configuration, unauthorised certificate issuance,
access to backup material and potentially abuse or extraction of the CA
signing key depending on the configured cryptographic provider.

Impact:
Successful compromise could allow an attacker to issue or forge trusted
certificates and impersonate Active Directory identities.

If the CA signing key can be extracted, the attacker may continue
creating certificates offline after access to the CA server has been
removed.

Recommendation:
Remove the identified administrative attack path and treat the
Enterprise CA as Tier 0 infrastructure.

Restrict administrative access, segment the CA, use dedicated privileged
administration, deploy application control and endpoint monitoring, and
review CA key protection and backup procedures.
```

---

# Severity

Confirmed theft of an Enterprise CA private key used for Active Directory authentication should normally be treated as:

```text
Critical
```

because the fundamental PKI trust boundary has been compromised.

---

# Potential vs Confirmed Compromise

Distinguish:

```text
CA Key Could Be Exported
```

from:

```text
CA Key Was Exported
```

and:

```text
Attacker Possesses CA Key
```

These represent different evidence levels.

---

# Example Severity Model

```text
Weak CA Hardening
       |
       v
Potential Key Exposure
       |
       v
High
```

versus:

```text
CA Key Confirmed Stolen
       |
       v
Trusted Authentication Certificates
Can Be Forged
       |
       v
Critical
```

Severity should reflect the actual demonstrated conditions.

---

# Evidence Checklist

Record:

```text
Forest
Domain
PKI Hierarchy
CA Name
CA Hostname
CA Type
Root / Issuing CA
CA Certificate Subject
CA Certificate Issuer
CA Certificate Serial
CA Certificate Thumbprint
CA Certificate Validity
Key Algorithm
Key Length
Cryptographic Provider
Software / Hardware Protection
HSM Vendor
Private Key Exportability
CA Administrative Principals
Local Administrators
Remote Access
Backup Product
Backup Location
Backup Encryption
Backup ACLs
Key Backup Procedures
HSM Authentication Model
CA Auditing
Certificate Services Logs
EDR Coverage
Application Control
Network Segmentation
Observed Key Access
Observed Key Export
Observed PFX Creation
Observed Forged Certificate
Observed Certificate Authentication
CA Database Correlation
Incident Exposure Window
```

Do not place:

```text
CA Private Key
PFX Password
HSM Authentication Secret
```

in the report.

---

# Golden Certificate Assessment Checklist

## PKI Discovery

- [ ] Identify PKI hierarchy
- [ ] Identify root CAs
- [ ] Identify Enterprise issuing CAs
- [ ] Identify CA hostnames
- [ ] Identify CA trust scope
- [ ] Identify certificates used for AD authentication
- [ ] Identify offline vs online CAs
- [ ] Identify CA operating systems
- [ ] Identify CA patch levels

## CA Certificate

- [ ] Record CA certificate subject
- [ ] Record issuer
- [ ] Record serial number
- [ ] Record thumbprint
- [ ] Record validity
- [ ] Record public-key algorithm
- [ ] Record signature algorithm
- [ ] Determine private-key availability
- [ ] Determine cryptographic provider

## Key Protection

- [ ] Determine software vs hardware protection
- [ ] Determine CSP or KSP
- [ ] Determine HSM use
- [ ] Determine key exportability
- [ ] Review provider configuration
- [ ] Review key ACLs where applicable
- [ ] Review HSM authentication
- [ ] Review HSM capabilities
- [ ] Review HSM audit configuration
- [ ] Review key ceremony documentation

## Administrative Security

- [ ] Identify CA administrators
- [ ] Identify certificate managers
- [ ] Identify local administrators
- [ ] Identify Enterprise Admin access
- [ ] Identify backup administrators
- [ ] Identify hypervisor administrators
- [ ] Identify HSM administrators
- [ ] Review RDP
- [ ] Review WinRM
- [ ] Review SMB
- [ ] Review unnecessary services
- [ ] Review privileged logon restrictions
- [ ] Review PAW usage

## Backup Security

- [ ] Identify CA backups
- [ ] Determine whether private key is included
- [ ] Identify backup locations
- [ ] Review backup ACLs
- [ ] Review backup encryption
- [ ] Review PFX protection
- [ ] Review backup passwords
- [ ] Review backup operators
- [ ] Review offline copies
- [ ] Review cloud copies
- [ ] Review VM snapshots
- [ ] Review recovery procedures
- [ ] Review backup auditing

## BloodHound

- [ ] Identify CA-related attack paths
- [ ] Review CA control
- [ ] Review GoldenCert context
- [ ] Review administrative paths
- [ ] Review PKI object control
- [ ] Distinguish potential control from confirmed key theft

## Safe Validation

- [ ] Prefer configuration review
- [ ] Do not export production CA key
- [ ] Do not create production Golden Certificate
- [ ] Do not target privileged production identity
- [ ] Use dedicated lab CA
- [ ] Use dedicated test identity
- [ ] Verify Certipy version
- [ ] Inspect `certipy forge -h`
- [ ] Protect lab PFX files
- [ ] Delete lab artifacts after testing
- [ ] Document cleanup

## Detection

- [ ] Enable appropriate CA auditing
- [ ] Monitor 4886
- [ ] Monitor 4887
- [ ] Monitor CA backup activity
- [ ] Review 4876/4877 where applicable
- [ ] Monitor cryptographic operations
- [ ] Review 5058/5059/5061 where applicable
- [ ] Monitor private-key file access
- [ ] Review 4663 where applicable
- [ ] Monitor HSM audit logs
- [ ] Monitor PFX creation
- [ ] Monitor certutil activity
- [ ] Monitor CA administrative logons
- [ ] Monitor CertSvc changes
- [ ] Monitor CA registry changes
- [ ] Monitor EDR telemetry
- [ ] Monitor certificate authentication
- [ ] Review 4768
- [ ] Correlate certificate serial with CA database
- [ ] Investigate certificates absent from CA database

## Hardening

- [ ] Treat CA as Tier 0
- [ ] Restrict CA administrative access
- [ ] Use dedicated admin accounts
- [ ] Use privileged access workstations
- [ ] Restrict RDP
- [ ] Restrict WinRM
- [ ] Restrict SMB
- [ ] Segment CA network
- [ ] Remove unnecessary software
- [ ] Deploy EDR
- [ ] Deploy application control
- [ ] Patch CA
- [ ] Protect backups
- [ ] Encrypt backups
- [ ] Separate backup administration
- [ ] Consider HSM
- [ ] Use non-exportable keys where appropriate
- [ ] Separate HSM administration
- [ ] Protect offline root
- [ ] Maintain key ceremony documentation
- [ ] Maintain CA compromise recovery plan

## Incident Response

- [ ] Isolate affected CA carefully
- [ ] Preserve forensic evidence
- [ ] Preserve CA database
- [ ] Preserve CA configuration
- [ ] Preserve event logs
- [ ] Preserve EDR telemetry
- [ ] Preserve HSM logs
- [ ] Preserve backup logs
- [ ] Determine initial compromise
- [ ] Determine key access
- [ ] Determine signing abuse
- [ ] Determine key extraction
- [ ] Determine exposure window
- [ ] Search for forged certificates
- [ ] Correlate certificates with CA database
- [ ] Review certificate authentication
- [ ] Review privileged account activity
- [ ] Revoke suspicious certificates
- [ ] Publish revocation information
- [ ] Rotate CA key where required
- [ ] Replace CA where required
- [ ] Reissue affected certificates
- [ ] Update trust stores
- [ ] Validate applications
- [ ] Monitor for continued certificate abuse

## Reporting

- [ ] Describe CA trust impact
- [ ] Identify exact CA
- [ ] Identify key-protection mechanism
- [ ] Identify administrative path
- [ ] Identify backup exposure
- [ ] Distinguish exportability from actual export
- [ ] Distinguish signing abuse from key theft
- [ ] Explain offline certificate forgery
- [ ] Explain persistence
- [ ] Explain CA database detection gap
- [ ] Avoid including private key material
- [ ] Provide PKI-specific remediation
- [ ] Recommend incident response if compromise suspected

---

# Golden Certificate Testing Model

The normal PKI model is:

```text
Certificate Request
       |
       v
Certificate Template
       |
       v
CA Policy
       |
       v
CA Private Key
       |
       v
Certificate
```

The Golden Certificate model is:

```text
CA Private Key
       |
       v
Attacker
       |
       v
Offline Certificate
       |
       v
Trusted Signature
```

The authentication model is:

```text
Forged Certificate
       |
       v
Certificate Chain Validation
       |
       v
Trusted Enterprise CA
       |
       v
Identity Mapping
       |
       v
Certificate Authentication
       |
       v
Kerberos TGT
```

The persistence model is:

```text
Compromise CA Key
       |
       v
Forge Certificate
       |
       v
Password Reset
       |
       v
Forge Another Certificate
       |
       v
Continued Access
```

The detection model is:

```text
Certificate Authentication
       |
       v
Issuer + Serial
       |
       v
CA Database
       |
       +--> Matching Issuance
       |
       +--> No Matching Issuance
                |
                v
        Investigate Forgery
```

The compromise model is:

```text
CA Host Access
      |
      v
Signing Capability?
      |
      +--> No
      |
      +--> Yes
             |
             v
       Key Exportable?
             |
             +--> No
             |     |
             |     v
             | Signing-Key Abuse
             |
             +--> Yes
                   |
                   v
              Offline Key Theft
```

The recovery model is:

```text
CA Key Compromise
       |
       v
Preserve Evidence
       |
       v
Determine Exposure
       |
       v
Replace / Rotate Key
       |
       v
Reissue Certificates
       |
       v
Update Trust
       |
       v
Monitor for Old Certificates
```

The backup attack model is:

```text
Secure CA
   |
   v
Insecure Backup
   |
   v
CA Private Key
   |
   v
Attacker
   |
   v
Golden Certificate
```

The HSM model is:

```text
CA
 |
 v
HSM
 |
 +--> Key Cannot Be Exported
 |
 +--> Signing Operations Restricted
 |
 +--> Authentication Protected
 |
 +--> Audit Logs
```

The Tier 0 model is:

```text
Domain Controllers
       +
KRBTGT
       +
Enterprise PKI
       +
Identity Infrastructure
       =
Tier 0
```

For penetration testers:

```text
Do Not Ask:
"Can I dump the production CA key
and forge Domain Admin certificates?"

Ask:
"Can I establish whether an attacker
with the identified access could
compromise the CA signing capability
without unnecessarily extracting
Tier 0 cryptographic material?"
```

For defenders:

```text
Do Not Assume:
"Our certificate templates are secure,
therefore our PKI is secure."

Ask:
"Who can access, use, export, back up
or recover the private key that signs
every certificate we trust?"
```

The complete Golden Certificate relationship is:

```text
Enterprise CA
      |
      v
CA Private Key
      |
      v
Key Compromise
      |
      v
Offline Certificate Forgery
      |
      v
Trusted Certificate
      |
      v
Certificate Authentication
      |
      v
Persistent Identity Compromise
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC5:

[AD CS ESC5](esc5.md)

ESC7:

[AD CS ESC7](esc7.md)

ESC12:

[AD CS ESC12](esc12.md)

ESC16:

[AD CS ESC16](esc16.md)

Kerberos:

[Kerberos](../kerberos.md)

Kerberos tickets:

[Kerberos Tickets](../kerberos-tickets.md)

Pass the Ticket:

[Pass the Ticket](../pass-the-ticket.md)

Credential Access:

[Credential Access](../credential-access.md)

NTDS:

[NTDS](../ntds.md)

The next Active Directory topic is:

```text
docs/active-directory/lateral-movement.md
```

---

# References

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

Certified Pre-Owned describes the security consequences of compromising an Enterprise CA and the CA private key, including certificate forgery and persistence.

---

## BloodHound - Golden Certificate

[BloodHound - Golden Certificate](https://bloodhound.specterops.io/resources/edges/golden-cert){ target="_blank" rel="noopener noreferrer" }

BloodHound documents the Golden Certificate attack relationship and CA-level control that can enable certificate forgery.

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Certipy provides AD CS enumeration, certificate authentication and certificate-forging functionality useful for authorised laboratory validation.

Always verify the installed version:

```bash
certipy --version
certipy forge -h
certipy auth -h
```

before relying on specific syntax.

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Securing PKI

[Microsoft - Securing PKI](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/plan-for-pki){ target="_blank" rel="noopener noreferrer" }

Use current Microsoft PKI architecture and security guidance when designing CA trust, key protection, recovery and administrative boundaries.

---

## Microsoft - KB5014754

[Microsoft - KB5014754 Certificate-Based Authentication Changes](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

Current certificate-mapping behaviour should be considered when evaluating forged authentication certificates.

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Golden Certificates represent a fundamentally different class of AD CS risk from ordinary certificate-template vulnerabilities.

With a template vulnerability:

```text
Attacker
   |
   v
Abuses CA Policy
```

With a Golden Certificate:

```text
Attacker
   |
   v
Becomes the CA
```

from the perspective of certificate signing.

The critical trust relationship is:

```text
CA Private Key
      |
      v
Trusted Certificate Signature
```

Once the private key is compromised, normal enrollment controls such as:

```text
Template Permissions
Manager Approval
Authorised Signatures
Enrollment Restrictions
```

cannot prevent the attacker from creating certificates offline.

This is why:

```text
Enterprise CA Private Key
```

must be treated as one of the most sensitive cryptographic assets in an Active Directory environment.

The most important assessment distinction is:

```text
CA Administrative Access
```

versus:

```text
CA Signing Capability
```

versus:

```text
CA Private Key Extraction
```

These are related but not identical.

A hardware-protected key may prevent straightforward extraction while still allowing an attacker controlling the CA to misuse signing operations.

Conversely, compromise of an old CA backup may expose the private key without requiring any access to the current CA server.

Therefore assess the entire trust chain:

```text
CA Host
   +
CA Administrators
   +
Cryptographic Provider
   +
HSM
   +
Backups
   +
Virtualisation
   +
Recovery Material
   =
CA Key Security
```

From a detection perspective, remember the defining property of Golden Certificates:

```text
Forged Offline
```

A certificate may therefore authenticate successfully even though:

```text
The CA Has No Record
of Issuing It
```

Correlating certificate-authentication telemetry with CA issuance records can provide valuable evidence of certificate forgery.

From an incident-response perspective:

```text
Resetting Passwords
```

is not enough.

```text
Revoking One Certificate
```

is not enough.

```text
Fixing Certificate Templates
```

is not enough.

If the CA signing key has been stolen:

```text
The Trust Key Itself
Must Be Recovered
```

through an appropriate PKI key-compromise recovery process.

For penetration testers, production validation should therefore stop well before unnecessary key extraction whenever the risk can already be demonstrated through:

```text
CA Control
       |
       v
Key Protection Analysis
       |
       v
Export / Signing Capability
       |
       v
Trusted Authentication Scope
```

For defenders, the central question is simple:

```text
If someone compromises this CA,
can we still trust certificates
signed by it?
```

If the CA private key has been compromised, the answer is:

```text
No.
```

That is why Golden Certificate capability represents one of the highest-impact compromise scenarios in an Active Directory PKI.
