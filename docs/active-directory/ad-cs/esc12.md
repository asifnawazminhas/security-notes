# AD CS ESC12 - YubiHSM2 and CA Private Key Protection

ESC12 is a specialised Active Directory Certificate Services (AD CS) attack scenario involving Certification Authority private keys protected by a YubiHSM2 Hardware Security Module (HSM).

Unlike many other AD CS ESC techniques, ESC12 is not primarily caused by a vulnerable certificate template, enrollment permission, or Certification Authority flag.

Instead, ESC12 focuses on the security boundary between:

```text
Certification Authority
        |
        v
HSM Software / Connector
        |
        v
YubiHSM2
        |
        v
CA Signing Key
```

The original ESC12 scenario describes circumstances where an attacker who has obtained local access to a CA server may be able to interact with the YubiHSM2 software stack and ultimately gain access to CA signing capabilities that administrators expected to be protected by the HSM.

The central security question is:

```text
Does the HSM actually prevent a
compromised or low-privileged process
on the CA host from abusing the
CA signing key?
```

This is different from simply asking:

```text
Is the CA private key exportable?
```

A properly deployed HSM may prevent direct private-key export while still allowing authorised signing operations.

Therefore, an attacker does not necessarily need to extract the raw private key if they can cause the HSM to perform arbitrary signing operations.

!!! warning "Authorised testing only"
    HSM testing can affect one of the most sensitive cryptographic trust anchors in an Active Directory environment. Do not attempt to extract CA private keys, modify HSM authentication configuration, reset HSM devices, change connector configuration, or perform arbitrary signing with a production CA. Begin with architecture review, configuration inspection, software and firmware inventory, permissions analysis, and vendor guidance. Any active validation should use a dedicated laboratory CA and HSM.

---

# Why the CA Private Key Matters

Every Certification Authority has a signing key.

Conceptually:

```text
Certificate Request
       |
       v
Certification Authority
       |
       v
CA Private Key
       |
       v
Digital Signature
       |
       v
Issued Certificate
```

The CA private key establishes the authenticity of certificates issued by that CA.

If an attacker gains control over this signing capability, they may be able to create certificates that appear to have been legitimately issued by the CA.

---

# CA Trust

A simplified PKI trust chain is:

```text
Root CA
   |
   v
Issuing CA
   |
   v
User / Computer Certificate
```

The signature chain allows clients to determine:

```text
Certificate
    |
    v
Signed by Trusted CA?
    |
    +--> No -> Reject
    |
    +--> Yes
            |
            v
        Continue Validation
```

The CA private key is therefore one of the most sensitive cryptographic assets in the environment.

---

# Enterprise CA and Active Directory

For certificates to participate in Active Directory authentication, several trust conditions may matter.

Conceptually:

```text
Enterprise CA
     |
     v
Trusted Certificate Chain
     |
     v
NT Authentication Trust
     |
     v
Certificate Authentication
```

If an attacker can abuse the signing key of an enterprise CA trusted for Active Directory authentication, the impact can potentially extend far beyond the CA server itself.

---

# Software-Protected CA Keys

Without an HSM, a CA signing key may be stored through Windows cryptographic providers.

Conceptually:

```text
CA Service
    |
    v
Windows Cryptographic Provider
    |
    v
Private Key Material
    |
    v
Disk / Protected Storage
```

Windows protects these keys using operating-system security mechanisms.

However, compromise of the CA host at sufficiently high privilege can potentially expose the key material.

---

# Hardware Security Modules

An HSM changes the architecture.

Instead of storing the private key directly on the CA server:

```text
CA Server
    |
    v
HSM Interface
    |
    v
Hardware Security Module
    |
    v
Private Key
```

The private key should remain inside the HSM.

---

# HSM Security Goal

The desired model is:

```text
CA Host Compromised
       |
       v
Raw CA Private Key
       |
       X
Cannot Be Extracted
```

The private key should remain protected by the hardware security boundary.

---

# Signing Still Has to Work

The CA must still be able to issue certificates.

Therefore:

```text
CA Service
    |
    v
Signing Request
    |
    v
HSM
    |
    v
Sign Using CA Key
```

The HSM performs the cryptographic operation without returning the private key.

---

# Export vs Signing

This creates an important distinction:

```text
Private-Key Extraction
```

and:

```text
Signing-Key Abuse
```

are not the same thing.

An attacker may not need:

```text
Raw Private Key
```

if they can obtain:

```text
Arbitrary Signing Capability
```

---

# ESC12 Concept

The ESC12 scenario focuses on weaknesses in the software and authentication architecture surrounding certain YubiHSM2 deployments.

Conceptually:

```text
Low-Privilege Access to CA
        |
        v
YubiHSM2 Software Stack
        |
        v
HSM Authentication Material
        |
        v
Access to HSM Operations
        |
        v
CA Signing Capability
```

This is substantially different from most other ESC paths.

---

# ESC12 Is Highly Specific

ESC12 should not be treated as:

```text
Every CA Using an HSM Is Vulnerable
```

or:

```text
Every YubiHSM2 Deployment Is Vulnerable
```

The practical risk depends on the exact:

```text
HSM Product
Firmware
Client Software
Connector
Key Storage Provider
Authentication Configuration
Local Permissions
CA Architecture
```

---

# Current Classification

Modern AD CS references continue to list ESC12 as:

```text
YubiHSM2
```

or:

```text
YubiHSM2-related CA key protection weakness
```

However, it is more specialised than common AD CS misconfigurations such as:

```text
ESC1
ESC4
ESC6
ESC8
ESC11
```

It should therefore be assessed only when the relevant HSM architecture exists.

---

# Do Not Report ESC12 Without YubiHSM2

If the CA does not use:

```text
YubiHSM2
```

the specific ESC12 condition does not apply.

A compromised software-protected CA private key is still extremely serious, but it should be reported according to the actual root cause rather than labelled ESC12.

---

# YubiHSM2

YubiHSM2 is a hardware security module produced by Yubico.

It can protect cryptographic keys used for:

```text
Certificate Authorities
Code Signing
TLS
Database Encryption
Cryptographic Applications
```

For AD CS:

```text
AD CS
  |
  v
YubiHSM Key Storage Provider
  |
  v
YubiHSM Connector
  |
  v
YubiHSM2
```

---

# Typical YubiHSM2 Architecture

A simplified deployment may look like:

```text
certsrv.exe
     |
     v
Microsoft CNG
     |
     v
YubiHSM Key Storage Provider
     |
     v
YubiHSM Connector
     |
     v
YubiHSM2
     |
     v
CA Private Key
```

The exact architecture depends on the installed Yubico components and deployment design.

---

# YubiHSM Key Storage Provider

Windows applications can access cryptographic keys through:

```text
Cryptography Next Generation
```

or:

```text
CNG
```

A vendor Key Storage Provider can connect Windows cryptographic operations to an HSM.

Conceptually:

```text
AD CS
  |
  v
CNG
  |
  v
YubiHSM KSP
  |
  v
YubiHSM
```

---

# YubiHSM Connector

The connector provides communication between applications and the YubiHSM device.

Conceptually:

```text
Application
    |
    v
YubiHSM Connector
    |
    v
YubiHSM2
```

This connector and its configuration therefore become part of the security boundary.

---

# HSM Authentication

The HSM must determine:

```text
Who Is Allowed to Use This Key?
```

The security model may involve:

```text
Authentication Keys
Object Permissions
Domains
Capabilities
Delegated Capabilities
```

depending on YubiHSM configuration.

---

# ESC12 Security Boundary

A secure architecture should look like:

```text
Low-Privilege User
       |
       X
HSM Authentication Material
       |
       X
CA Signing Key
```

A dangerous architecture looks more like:

```text
Low-Privilege User
       |
       v
Accessible HSM Credentials
       |
       v
HSM Session
       |
       v
CA Signing Operations
```

---

# HSM Credentials Matter

If authentication material required to access the HSM is available to an attacker who has only low-privileged access to the CA server, the hardware boundary may provide substantially less protection than expected.

This is the central architectural concern behind ESC12.

---

# ESC12 Preconditions

A practical ESC12 scenario generally requires:

```text
AD CS CA
   +
YubiHSM2
   +
Relevant YubiHSM Software Stack
   +
Local Access to CA Host
   +
Weak HSM Authentication Boundary
   +
Access to Sensitive HSM Operations
   =
Potential ESC12
```

---

# Initial Access Is Required

Unlike ESC1 or ESC8, ESC12 generally assumes the attacker already has some level of access to the CA server.

Conceptually:

```text
Initial Access
     |
     v
CA Server Shell
     |
     v
ESC12 Investigation
```

ESC12 is therefore typically:

```text
Post-Compromise
```

rather than a remote unauthenticated AD CS weakness.

---

# Low Privilege Is Important

If the attacker already has:

```text
SYSTEM
```

or:

```text
Local Administrator
```

on an enterprise CA, the environment is already in an extremely dangerous state.

The interesting ESC12 question is whether:

```text
Low-Privilege Local Access
```

can cross the HSM security boundary.

---

# Local Administrator on a CA

Administrative compromise of a CA should already be treated as a major security incident.

A CA administrator may potentially:

```text
Modify CA Configuration
Publish Templates
Approve Requests
Change Enrollment Controls
Interact with Cryptographic Providers
Manipulate CA Services
```

depending on exact privileges.

Therefore:

```text
Admin on CA
```

should not automatically be described as ESC12.

---

# CA Host Is Tier 0

Enterprise CA hosts should be treated as:

```text
Tier 0
```

or equivalent identity-control-plane systems.

A compromise path such as:

```text
User
 |
 v
Local Admin on CA
 |
 v
CA Control
 |
 v
Domain
```

is already extremely important regardless of ESC12.

---

# Golden Certificate

If an attacker obtains the CA signing private key, they may be able to create:

```text
Golden Certificates
```

Conceptually:

```text
CA Private Key
      |
      v
Forge Certificate
      |
      v
Target Identity
      |
      v
Trusted Certificate
```

See the dedicated Golden Certificate notes later in this AD CS section.

---

# Golden Certificate Requirements

For a forged certificate to work for Active Directory authentication, the CA must be appropriately trusted.

Conceptually:

```text
Forged Certificate
       |
       v
Trusted CA Chain?
       |
       +--> No -> Authentication Fails
       |
       +--> Yes
               |
               v
       Trusted for NT Authentication?
               |
               +--> No -> Domain Auth Fails
               |
               +--> Yes
                       |
                       v
                 Potential Authentication
```

---

# HSM May Prevent Key Extraction

An HSM can make:

```text
Export CA Private Key
```

impossible by design.

This is valuable.

However:

```text
Cannot Export Key
```

does not automatically mean:

```text
Cannot Abuse Key
```

---

# Signing Oracle Concept

Suppose an attacker cannot retrieve:

```text
CA_PRIVATE_KEY
```

but can submit arbitrary signing operations:

```text
Attacker-Controlled Data
        |
        v
HSM
        |
        v
Signature with CA Key
```

The attacker effectively has access to a:

```text
Signing Oracle
```

This may still undermine the trust model.

---

# Key Extraction vs Signing Oracle

```text
                CA Key Compromise
                       |
          +------------+------------+
          |                         |
          v                         v
    Key Extraction             Signing Abuse
          |                         |
          v                         v
   Raw Private Key           HSM Performs Signing
```

Both require investigation.

---

# Identify Certification Authorities

Start with normal AD CS enumeration.

Using Certipy:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Record:

```text
CA Name
CA Hostname
CA Type
CA Certificate
Published Templates
```

---

# Native Active Directory Enumeration

From Windows:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentServices = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentServices -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties dNSHostName |
    Select-Object Name,dNSHostName,DistinguishedName
```

This identifies enterprise CA objects and their hosts.

---

# Identify CA Host

The CA object's:

```text
dNSHostName
```

identifies the system hosting the Certification Authority service.

Record this host because ESC12 is primarily a:

```text
CA Host Security
```

issue.

---

# Confirm Certificate Services

On an authorised CA server:

```powershell
Get-Service CertSvc
```

Example:

```text
Status   Name      DisplayName
------   ----      -----------
Running  CertSvc   Active Directory Certificate Services
```

---

# Enumerate CA Configuration

```cmd
certutil -getreg CA
```

Use this for read-only configuration inspection.

Do not modify CA settings during ESC12 discovery.

---

# Identify Cryptographic Provider

The CA certificate can provide information about the cryptographic provider and key association.

List machine certificates:

```powershell
Get-ChildItem Cert:\LocalMachine\My |
    Select-Object Subject,Issuer,Thumbprint,HasPrivateKey,NotAfter
```

Identify the CA certificate carefully.

---

# Inspect Certificate

```cmd
certutil -store my
```

Look for the CA certificate and its private-key provider information.

---

# Provider Information

Depending on provider type and Windows version, certificate information may identify a provider associated with:

```text
YubiHSM
```

or another HSM.

Do not assume:

```text
HasPrivateKey = True
```

means the raw private key is stored on disk.

For HSM-backed certificates, Windows can expose a key handle while the actual private key remains in hardware.

---

# Identify Installed YubiHSM Components

On an authorised CA host:

```powershell
Get-ChildItem 'C:\Program Files' -Directory |
    Where-Object { $_.Name -match 'Yubi|HSM' } |
    Select-Object FullName
```

Also review:

```powershell
Get-ChildItem 'C:\Program Files (x86)' -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match 'Yubi|HSM' } |
    Select-Object FullName
```

---

# Installed Software Inventory

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Where-Object { $_.DisplayName -match 'Yubi|HSM' } |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```

Also inspect the 32-bit uninstall registry path where relevant.

---

# Service Enumeration

Search for YubiHSM-related services:

```powershell
Get-Service |
    Where-Object {
        $_.Name -match 'Yubi|HSM' -or
        $_.DisplayName -match 'Yubi|HSM'
    } |
    Select-Object Status,Name,DisplayName
```

---

# Process Enumeration

```powershell
Get-Process |
    Where-Object { $_.ProcessName -match 'Yubi|HSM' } |
    Select-Object ProcessName,Id,Path
```

Permissions may prevent access to some process metadata.

---

# Listening Ports

Review local listeners:

```powershell
Get-NetTCPConnection -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Correlate relevant process IDs with the YubiHSM connector or related components.

Do not assume a listener is insecure merely because it exists.

---

# Configuration Discovery

Potential YubiHSM configuration may exist in:

```text
ProgramData
Program Files
Service Configuration
Environment Variables
Application Configuration
Registry
```

Search narrowly and carefully.

Avoid recursively dumping an entire CA filesystem for secrets.

---

# File Permission Review

For identified YubiHSM configuration files:

```powershell
Get-Acl 'C:\Path\To\YubiHSM\ConfigFile' |
    Format-List Owner,AccessToString
```

The important question is:

```text
Can an unprivileged principal
read or modify security-sensitive
HSM configuration?
```

---

# Directory Permissions

```powershell
Get-Acl 'C:\Path\To\YubiHSM' |
    Format-List Owner,AccessToString
```

Review permissions for:

```text
Users
Authenticated Users
Everyone
Service Accounts
Administrators
SYSTEM
```

---

# Modification Is Especially Dangerous

A directory writable by low-privileged users may create additional attack opportunities.

Conceptually:

```text
Writable HSM Component
       |
       v
Service / CA Loads Component
       |
       v
Privilege Boundary Crossed
```

This should be assessed as a host-security issue even if it does not directly meet the ESC12 definition.

---

# Service Configuration

Inspect relevant service configuration:

```cmd
sc.exe qc <ServiceName>
```

Review:

```text
SERVICE_START_NAME
BINARY_PATH_NAME
START_TYPE
```

---

# Service Binary Permissions

For an identified service binary:

```powershell
Get-Acl 'C:\Path\To\Service.exe' |
    Format-List Owner,AccessToString
```

Low-privileged write access to a privileged service binary or its directory is independently dangerous.

---

# Service Account

Determine which account runs each relevant component.

Possible identities include:

```text
LocalSystem
NetworkService
LocalService
Dedicated Service Account
```

The account's relationship with HSM credentials is important.

---

# HSM Credential Storage

A key assessment question is:

```text
Where is the authentication material
required to access the HSM?
```

Possible architectures include:

```text
Local Configuration
Protected Windows Storage
Service Account Context
External Secret
Manual Operator Input
HSM Authentication Key
```

Do not extract or display real production secrets merely to prove that they exist.

---

# Search for References, Not Secrets

Prefer searching for:

```text
Configuration File Location
Authentication Method
Object ID
Connector Address
Provider Name
```

rather than printing:

```text
Password
Authentication Key
Private Key
```

to the console.

---

# Environment Variables

Review names only first:

```powershell
Get-ChildItem Env: |
    Where-Object { $_.Name -match 'YUBI|HSM' } |
    Select-Object Name
```

If a variable appears security-sensitive, do not automatically print its value.

---

# HSM Object Model

YubiHSM2 uses objects such as:

```text
Authentication Keys
Asymmetric Keys
Wrap Keys
HMAC Keys
Opaque Objects
```

The CA signing key is typically represented through an asymmetric-key object or equivalent cryptographic object used by the configured provider.

---

# Capabilities

YubiHSM objects use capabilities to control permitted operations.

Conceptually:

```text
Authentication Key
       |
       v
Capabilities
       |
       +--> Sign
       +--> Generate
       +--> Import
       +--> Export Wrapped
       +--> Delete
       +--> Other Operations
```

The exact capability set depends on the deployment.

---

# Least Privilege

The HSM authentication identity used by the CA should have only the capabilities necessary for normal CA operation.

Avoid giving the CA service broad HSM administrative permissions when only signing is required.

---

# HSM Domains

YubiHSM2 also uses domains to separate object access.

Conceptually:

```text
Authentication Key
       |
       v
Domain Membership
       |
       v
Accessible Objects
```

Incorrect domain assignments may expose unrelated cryptographic objects.

---

# Authentication-Key Review

For an authorised architecture review, document:

```text
Authentication Key ID
Purpose
Domains
Capabilities
Delegated Capabilities
Owner
Rotation Procedure
Storage Method
```

Avoid including actual authentication secrets in the penetration-test report.

---

# Default Credentials

Any HSM deployment should be reviewed for:

```text
Default Authentication Credentials
```

Default credentials should be removed during secure provisioning.

Do not attempt default credentials against a production HSM unless specifically authorised.

---

# Firmware Version

Record the HSM firmware version through approved administrative tooling or asset-management information.

Compare against:

```text
Current Vendor Support
Security Advisories
Release Notes
```

---

# Client Software Version

Also record:

```text
YubiHSM SDK
Connector
KSP
Libraries
Management Tools
```

because ESC12 relates to the complete HSM software stack, not merely the hardware device.

---

# Version Inventory

Your evidence should resemble:

```text
Device:
YubiHSM2

Firmware:
<version>

Connector:
<version>

KSP:
<version>

SDK:
<version>

CA:
CORP-CA
```

Do not infer vulnerability from product presence alone.

---

# Certipy and ESC12

Current Certipy documentation describes ESC12 but does not provide a general automatic ESC12 detection mechanism.

This is important.

Do not expect:

```bash
certipy find
```

to reliably determine whether the specific YubiHSM2 security boundary is exploitable.

ESC12 requires:

```text
Architecture Review
+
Host Review
+
HSM Configuration Review
+
Version Review
```

---

# BloodHound

BloodHound can identify the host running an enterprise CA and attack paths leading to that host.

Conceptually:

```text
User
 |
 v
AdminTo
 |
 v
CA Host
 |
 v
GoldenCert / CA Control
 |
 v
Domain
```

See:

[BloodHound](../bloodhound.md)

---

# HostsCAService

Modern BloodHound models the relationship between:

```text
Computer
```

and:

```text
Enterprise CA
```

through the CA-host relationship.

This helps identify which machine must be treated as Tier 0.

---

# GoldenCert Edge

BloodHound may represent situations where compromise of the CA host can lead to control of the domain through a:

```text
GoldenCert
```

relationship.

However, HSM protection may prevent straightforward private-key extraction.

Therefore:

```text
Admin on CA Host
```

and:

```text
CA Private Key Extractable
```

must not automatically be treated as identical.

---

# HSM Changes the Attack Path

Without HSM:

```text
CA Host Compromise
       |
       v
Private Key Extraction
       |
       v
Golden Certificate
```

With effective HSM protection:

```text
CA Host Compromise
       |
       v
Attempt Key Extraction
       |
       X
Private Key Remains in HSM
```

ESC12 asks whether another path exists:

```text
CA Host Access
       |
       v
HSM Software / Authentication Weakness
       |
       v
Signing Capability
```

---

# CA Administrative Control Still Matters

Even if the HSM perfectly protects the private key, an attacker controlling the CA host may still have dangerous capabilities.

For example:

```text
Publish Templates
Approve Requests
Change CA Configuration
Modify Enrollment Controls
Disable Security Features
```

Therefore HSM deployment does not make CA host compromise acceptable.

---

# ESC12 vs Golden Certificate

ESC12:

```text
Weakness in HSM Protection / Integration
```

Golden Certificate:

```text
Attacker Controls CA Signing Key
```

ESC12 may provide a route toward Golden Certificate-like capabilities, but the two concepts should remain distinct.

---

# ESC12 vs ESC5

ESC5 concerns vulnerable access control over PKI objects and infrastructure.

ESC12 specifically concerns the HSM security boundary.

Conceptually:

```text
ESC5
 |
 v
PKI Object / Infrastructure Control
```

versus:

```text
ESC12
 |
 v
HSM / CA Key Protection
```

---

# ESC12 vs ESC7

ESC7 concerns dangerous Certification Authority permissions such as:

```text
ManageCA
ManageCertificates
```

ESC12 does not require those CA permissions if a separate HSM weakness provides signing access.

---

# ESC12 vs ESC4

ESC4 concerns:

```text
Certificate Template ACLs
```

ESC12 concerns:

```text
CA Signing-Key Protection
```

They operate at completely different layers.

---

# ESC12 vs ESC11

ESC11 concerns:

```text
RPC Enrollment Relay
```

ESC12 concerns:

```text
Local CA / HSM Security
```

ESC11 can often be assessed remotely.

ESC12 generally requires host-level or architectural assessment.

---

# Safe ESC12 Assessment

A safe assessment should proceed through increasingly invasive stages.

```text
Architecture Review
      |
      v
Software Inventory
      |
      v
Permission Review
      |
      v
HSM Configuration Review
      |
      v
Version / Advisory Review
      |
      v
Lab Validation if Required
```

---

# Stage 1 - Architecture Review

Determine:

```text
Does the CA use an HSM?
        |
        +--> No -> ESC12 Not Applicable
        |
        +--> Yes
                |
                v
           Which HSM?
```

If:

```text
YubiHSM2
```

continue with ESC12-specific analysis.

---

# Stage 2 - Identify Components

Document:

```text
CA Service
YubiHSM2
YubiHSM Connector
YubiHSM KSP
YubiHSM SDK
Authentication Mechanism
Key Object
```

---

# Stage 3 - Permission Review

Determine whether low-privileged users can:

```text
Read Sensitive Configuration
Modify Sensitive Configuration
Modify Connector Files
Modify KSP Files
Control Services
Access Authentication Material
Interact with Management Interfaces
```

---

# Stage 4 - Authentication Boundary Review

Determine:

```text
How does certsrv.exe authenticate to the HSM?
```

Then ask:

```text
Can another process running as a
low-privileged user obtain the same
authentication capability?
```

This is the central ESC12 question.

---

# Stage 5 - Capability Review

Determine whether the CA's HSM authentication identity can perform more operations than required.

Review:

```text
Sign
Generate
Import
Export
Delete
Change Authentication
Administrative Operations
```

The principle should be:

```text
Minimum Required Capability
```

---

# Stage 6 - Vendor Advisory Review

Compare:

```text
Firmware
Connector
SDK
KSP
```

against current Yubico security advisories and release notes.

A historical ESC12 description should not be assumed to apply unchanged to a fully updated deployment.

---

# Stage 7 - Lab Validation

If exploitation research must be validated:

```text
Dedicated AD Forest
       |
       v
Dedicated CA
       |
       v
Dedicated YubiHSM2
       |
       v
Known Test Keys
       |
       v
Controlled Validation
```

Do not perform destructive HSM testing against the production CA.

---

# Avoid Production Key Extraction

Do not attempt to extract:

```text
Production CA Private Key
```

merely to prove impact.

If the architecture demonstrates that an unauthorised low-privileged user can invoke sensitive HSM operations, that may already provide sufficient evidence.

---

# Avoid Arbitrary Production Signing

Do not use a production CA signing key to sign attacker-controlled authentication certificates merely to demonstrate theoretical impact.

A lab reproduction is substantially safer.

---

# Do Not Reset the HSM

Never perform operations such as:

```text
Factory Reset
Authentication-Key Replacement
Object Deletion
Key Deletion
Connector Reconfiguration
```

during routine penetration testing.

These actions can cause severe PKI outages or permanent loss of cryptographic material.

---

# Do Not Test Lockout Behaviour

Repeated authentication attempts against an HSM may trigger security mechanisms or operational problems.

Do not brute-force HSM credentials.

---

# Evidence Without Exploitation

Strong ESC12 evidence may consist of:

```text
YubiHSM2 Confirmed
       |
       v
Affected Software / Architecture Confirmed
       |
       v
Low-Privilege Access Confirmed
       |
       v
Sensitive HSM Authentication Boundary Exposed
       |
       v
Vendor / Research Condition Matched
```

This is preferable to production key abuse.

---

# CA Private-Key Protection Review

Even where ESC12 does not apply, assess:

```text
Is CA Private Key Exportable?
Is CA Private Key HSM-Protected?
Who Can Use the Key?
Who Can Export the Key?
Who Can Back Up the Key?
Who Can Administer the HSM?
```

---

# certutil Private-Key Context

`certutil` can display certificate and provider information.

Use read-only commands such as:

```cmd
certutil -store my
```

Avoid key export or backup commands during discovery.

---

# Certificate Store Permissions

The CA certificate itself is public information.

The important asset is:

```text
Private Key Access
```

Do not confuse:

```text
Read CA Certificate
```

with:

```text
Read CA Private Key
```

---

# CA Backup

CA backup procedures may include:

```text
CA Database
Configuration
CA Certificate
Private Key
```

depending on architecture.

For HSM-backed keys, backup architecture may differ.

Review:

```text
How Is the HSM Key Backed Up?
```

---

# Backup Security

HSM protection can be undermined if:

```text
Backup Key
```

or:

```text
Wrapped Key Material
```

is stored insecurely elsewhere.

Conceptually:

```text
HSM
 |
 +--> Secure
 |
 +--> Backup
        |
        v
   Weak Storage
```

The overall system is only as secure as its recovery path.

---

# Disaster Recovery

Review:

```text
HSM Backup
Recovery Credentials
Authentication Keys
Recovery Documentation
Offline Copies
Dual Control
```

These are often overlooked attack surfaces.

---

# Dual Control

Sensitive HSM administration should ideally require strong separation of duties.

Conceptually:

```text
Operator A
    +
Operator B
    =
Sensitive HSM Operation
```

where supported by the organisation's HSM design.

---

# Separation of Duties

Avoid architectures where one administrator controls:

```text
CA Host
HSM Administration
HSM Authentication Secrets
CA Backup
Recovery Material
```

without additional controls.

---

# HSM Network Exposure

If the connector communicates over a network interface, review:

```text
Listening Address
Firewall Rules
Authentication
Encryption
Network Segmentation
Remote Reachability
```

The exact relevance depends on deployment architecture.

---

# Loopback Binding

Where architecture permits, a connector intended only for local applications should not unnecessarily expose its interface to remote networks.

Verify vendor-supported configuration before making changes.

---

# Network Segmentation

CA and HSM infrastructure should reside in tightly controlled management zones.

Avoid broad workstation access to:

```text
CA Administrative Interfaces
HSM Management Interfaces
Connector Interfaces
```

---

# Local User Access

A Certification Authority should not be used as:

```text
General-Purpose Server
Jump Host
Administrative Workstation
File Server
Application Server
```

Unnecessary local users increase the attack surface relevant to ESC12.

---

# Interactive Logon

Restrict interactive logon to the CA.

Conceptually:

```text
Normal Domain User
       |
       X
CA Interactive Logon
```

---

# Remote Administration

Restrict:

```text
RDP
WinRM
SMB Administration
Remote Service Control
WMI
```

to approved administrative systems and identities.

---

# Software Installation

Only authorised administrators should be able to install software or drivers on the CA.

HSM providers operate close to the cryptographic trust boundary, making software integrity particularly important.

---

# Application Control

Consider application-control mechanisms such as:

```text
WDAC
AppLocker
```

where operationally appropriate.

The goal is to prevent arbitrary untrusted code from running on the CA host.

---

# EDR

Deploy security monitoring compatible with the CA and HSM environment.

Monitor:

```text
Unexpected Processes
Unexpected DLL Loading
Service Changes
Registry Changes
File Modifications
Credential Access
Cryptographic Operations
```

---

# Cryptographic Auditing

Windows can generate cryptographic auditing events for operations involving cryptographic providers.

Relevant events may include:

```text
5058
5059
5061
```

depending on provider, audit configuration, and operation.

Do not assume every HSM operation produces the same Windows telemetry as a software KSP.

Validate visibility in the actual environment.

---

# Event 5058

Event:

```text
5058
```

can provide information about key-file operations involving cryptographic providers in relevant Windows configurations.

Its usefulness depends on provider and audit configuration.

---

# Event 5059

Event:

```text
5059
```

relates to key migration/export activity in applicable cryptographic-provider scenarios.

An HSM designed to prevent export may behave differently.

---

# Event 5061

Event:

```text
5061
```

can provide visibility into cryptographic operations in applicable Windows configurations.

Establish a baseline before using it as a high-confidence alert.

---

# CA Backup Events

Certificate Services auditing can also provide visibility around CA key backup operations.

Historically relevant events include:

```text
4876
4877
```

where appropriate auditing is enabled.

Unexpected CA backup activity should be investigated.

---

# File Auditing

Where software-protected keys or HSM configuration files exist, SACLs can provide visibility into unexpected access.

For example:

```text
Sensitive HSM Config
        |
        v
Unexpected User Read
        |
        v
4663
```

where Object Access auditing is appropriately configured.

---

# Event 4663

Event:

```text
4663
```

can indicate access to an audited file or object.

Use it selectively because broad filesystem auditing can generate substantial noise.

---

# HSM Audit Logs

Prefer native HSM audit capabilities where available.

HSM audit data can potentially identify:

```text
Authentication
Session Creation
Signing Operations
Object Creation
Object Deletion
Administrative Changes
Failed Operations
```

depending on product configuration.

---

# Baseline Signing Activity

A CA normally performs signing operations as part of certificate issuance.

Therefore:

```text
Signing Event
```

alone is not suspicious.

Detection should correlate:

```text
HSM Signing
      |
      v
Was There a Corresponding
Legitimate CA Request?
```

---

# Signing Without Enrollment

A particularly interesting condition is:

```text
HSM Signing Operation
       |
       v
No Matching CA Request
```

if the HSM and CA telemetry allow this correlation.

This may indicate direct signing-key abuse.

---

# Certificate Issuance Monitoring

Monitor CA events such as:

```text
4886
4887
```

where Certificate Services auditing is enabled.

Correlate:

```text
Certificate Request
Certificate Issuance
HSM Signing
```

---

# Detect Unexpected HSM Processes

Establish which processes should interact with the HSM.

For example:

```text
Expected:
certsrv.exe
Approved HSM Components
Approved Administrative Utilities
```

Unexpected processes establishing HSM sessions should be investigated.

---

# Detect Configuration Access

Monitor sensitive YubiHSM configuration files for:

```text
Read
Write
Delete
Permission Change
Ownership Change
```

especially from low-privileged accounts.

---

# Detect Connector Changes

Monitor:

```text
Connector Binary
Connector Configuration
Connector Service
KSP Libraries
```

for unauthorised modification.

---

# HSM Version Monitoring

Asset management should continuously track:

```text
Firmware Version
Connector Version
SDK Version
KSP Version
```

and compare them against vendor-supported releases.

---

# Hardening ESC12

The overall objective is:

```text
Protect the CA Key
       +
Protect HSM Authentication
       +
Protect CA Host
       +
Restrict HSM Capabilities
       =
Strong CA Trust Boundary
```

---

# Keep HSM Components Updated

Maintain supported versions of:

```text
YubiHSM Firmware
Connector
SDK
KSP
Management Utilities
```

Follow Yubico security advisories.

---

# Remove Default Credentials

Ensure default HSM authentication credentials have been replaced during provisioning.

Use strong, unique authentication material.

---

# Protect Authentication Material

HSM credentials should not be:

```text
World Readable
Stored in Scripts
Stored in Shared Folders
Hardcoded in Deployment Tools
Exposed Through Environment Variables
Committed to Git
Included in Documentation
```

---

# Restrict File Permissions

Only the identities that require access should be able to read HSM configuration.

Example model:

```text
SYSTEM
CA Service
HSM Administrators
```

rather than:

```text
Authenticated Users
```

---

# Restrict Modification

Low-privileged users should not be able to modify:

```text
Connector
KSP
Libraries
Configuration
Service Binary
Service Directory
```

---

# Least HSM Capabilities

The CA authentication key should have only the operations required for certificate issuance.

Avoid unnecessary administrative capabilities.

---

# Separate Administrative Authentication

Use separate HSM authentication identities for:

```text
CA Signing
HSM Administration
Backup
Recovery
```

where the product and organisational design support it.

---

# Protect Recovery Material

Store:

```text
Backup Keys
Recovery Authentication Keys
Wrapped Key Backups
Recovery Documentation
```

with controls appropriate to Tier 0 secrets.

---

# Secure the CA Host

Apply:

```text
Tier 0 Administration
Dedicated Admin Accounts
Privileged Access Workstations
Network Segmentation
Current Patching
Application Control
EDR
Restricted Interactive Logon
```

---

# Minimise Installed Software

The CA should contain only software required for:

```text
Windows
AD CS
HSM Integration
Security Monitoring
Approved Management
```

Every additional application expands the attack surface.

---

# Restrict Outbound Access

CA servers should have tightly controlled outbound network access.

This reduces:

```text
Command and Control
Payload Retrieval
Credential Exfiltration
Unexpected HSM Communication
```

---

# Protect Administrative Workstations

HSM administrators should use hardened administrative workstations.

Compromising an HSM administrator's workstation may expose:

```text
Credentials
Management Sessions
Recovery Information
Configuration
```

even if the HSM itself is secure.

---

# Review HSM Logs

Include HSM audit logs in central monitoring where feasible.

Protect those logs against alteration by CA administrators where architecture permits.

---

# Key Ceremony

High-value PKI operations should use documented:

```text
Key Ceremonies
```

covering:

```text
Key Generation
Backup
Recovery
Rotation
Destruction
Administrative Changes
```

---

# CA Key Rotation

Maintain a documented process for rotating the CA signing key if compromise is suspected.

This can be operationally complex and should be prepared before an incident occurs.

---

# Incident Response

Suspected ESC12 or CA signing-key compromise is a major PKI incident.

A simplified response is:

```text
Detect Suspicious HSM Activity
        |
        v
Isolate CA
        |
        v
Preserve Evidence
        |
        v
Review HSM Logs
        |
        v
Determine Signing-Key Exposure
        |
        v
Identify Forged Certificates
        |
        v
Rebuild / Rotate Trust if Required
```

---

# Do Not Immediately Destroy Evidence

Do not:

```text
Reset HSM
Delete Keys
Reinstall CA
Destroy Connector Logs
```

before preserving evidence.

These actions may eliminate information needed to determine the scope of compromise.

---

# Isolate the CA

If active compromise is suspected, isolate the CA according to the organisation's incident-response process.

Consider the operational consequences before stopping certificate services.

---

# Preserve HSM Logs

Collect:

```text
HSM Audit Logs
Connector Logs
Windows Event Logs
CA Database
CA Logs
EDR Telemetry
Service Configuration
Installed Software Inventory
```

---

# Determine HSM Authentication Exposure

Investigate whether the attacker obtained:

```text
Authentication Key
Authentication Password
Session Access
Management Capability
Signing Capability
```

---

# Determine Key Extraction

Establish whether:

```text
Raw CA Private Key
```

was actually exported.

If the HSM design makes this impossible, investigate whether the attacker nevertheless obtained:

```text
Signing Oracle Capability
```

---

# Identify Unauthorised Signing

Compare:

```text
HSM Signing Operations
```

against:

```text
CA Request Database
```

where possible.

Unmatched signing operations are highly significant.

---

# Identify Forged Certificates

Forged certificates may not appear in the CA database because they were not issued through normal CA enrollment.

This is an important Golden Certificate characteristic.

Conceptually:

```text
Normal Certificate
      |
      v
CA Database Entry

Forged Certificate
      |
      X
No Normal Request Record
```

---

# Review Authentication Logs

Investigate certificate-based authentication for privileged identities.

Relevant telemetry may include:

```text
Kerberos
Schannel
Domain Controller Logs
Application Authentication
```

---

# CA Key Compromise Is Different from User Credential Compromise

If a user's password is compromised:

```text
Reset Password
```

may substantially contain the issue.

If a CA signing key is compromised:

```text
Reset User Password
```

does not repair the PKI trust anchor.

---

# Potential PKI Recovery

Depending on incident scope, recovery may require:

```text
CA Key Rotation
CA Certificate Renewal
Certificate Revocation
Reissuance
Trust Store Updates
NTAuth Updates
HSM Reprovisioning
CA Rebuild
```

This should be coordinated with experienced PKI administrators.

---

# Reporting ESC12

Do not use a generic title such as:

```text
ESC12
```

Prefer a descriptive title based on the demonstrated root cause.

Examples:

```text
Weak YubiHSM2 Integration Exposes CA Signing Capability
```

or:

```text
Low-Privileged CA Users Can Access HSM Authentication Material
```

or:

```text
CA Signing Key Protection Depends on Accessible HSM Credentials
```

---

# Example Finding - Architecture Weakness

```text
Finding:
Low-Privileged CA Users Can Access Security-Sensitive
YubiHSM2 Configuration

Affected Host:
ca01.corp.example

Affected CA:
CORP-CA

Description:
The Certification Authority uses a YubiHSM2 Hardware Security Module
to protect the CA signing key.

During configuration review, security-sensitive HSM integration
material was found to be accessible from a low-privileged local
account on the CA host.

The HSM is intended to provide a cryptographic security boundary
between the CA host and the CA signing key. Access to authentication
or integration material that allows an unauthorised process to
interact with sensitive HSM operations may weaken that boundary.

No production CA private key was extracted and no arbitrary
certificate was signed during testing.

Impact:
If the exposed material provides sufficient HSM capabilities, an
attacker who obtains low-privileged access to the CA server may be
able to interact with the CA signing key despite the key being
hardware protected.

Depending on the HSM capabilities available and the trust assigned
to the CA, this may undermine certificate issuance and potentially
Active Directory certificate authentication.

Recommendation:
Restrict access to YubiHSM configuration and authentication material
to the minimum required service and administrative identities.

Review HSM authentication keys, domains, capabilities and delegated
capabilities according to least privilege.

Update the YubiHSM firmware, connector, KSP and supporting software
to currently supported versions.

Treat the CA host and HSM administration environment as Tier 0.
```

---

# Example Finding - Outdated HSM Components

```text
Finding:
Outdated YubiHSM2 Components Protect Enterprise CA Signing Key

Affected Host:
ca01.corp.example

Affected CA:
CORP-CA

Description:
The enterprise Certification Authority uses YubiHSM2 components that
are no longer aligned with the organisation's approved current
vendor baseline.

Because the HSM software stack forms part of the security boundary
protecting the CA signing key, vulnerabilities in the connector,
KSP, SDK or firmware may undermine the protection expected from the
hardware device.

No attempt was made to exploit the production HSM.

Impact:
Successful compromise of the HSM integration layer could potentially
provide unauthorised access to cryptographic operations involving the
CA signing key.

The resulting impact depends on the specific affected component,
available HSM capabilities and CA trust configuration.

Recommendation:
Validate the installed YubiHSM firmware and software components
against current Yubico security advisories and supported releases.

Upgrade affected components through the organisation's PKI change
process and verify HSM authentication and capability configuration.
```

---

# Do Not Overstate Severity

Finding:

```text
YubiHSM2 Installed
```

does not equal:

```text
Critical ESC12
```

Likewise:

```text
Old Blog Describes YubiHSM2 Attack
```

does not prove:

```text
Current Deployment Vulnerable
```

---

# Severity Assessment

Use:

```text
Local Access
    +
HSM Weakness
    +
Available Capability
    +
CA Trust
    +
Authentication Use
    =
Severity
```

---

# High-Severity Scenario

```text
Low-Privilege CA Shell
        |
        v
HSM Authentication Accessible
        |
        v
CA Signing Capability
        |
        v
Trusted Enterprise CA
```

This can represent a severe breakdown of the expected HSM security boundary.

---

# Critical Scenario

```text
CA Signing Capability
       |
       v
Forge Authentication Certificate
       |
       v
Trusted by AD
       |
       v
Privileged Principal
       |
       v
Forest Compromise
```

Only describe this as demonstrated if the trust conditions and signing capability are actually established.

---

# Lower-Risk Scenario

```text
YubiHSM2 Present
      |
      v
Current Firmware
      |
      v
Current Software
      |
      v
Strong Authentication Boundary
      |
      v
Low-Privilege Access Blocked
```

In this situation ESC12 may not be present.

---

# Evidence Checklist

For ESC12 record:

```text
CA Name
CA Hostname
CA Type
CA Certificate Thumbprint
CA Trust Chain
NTAuth Status
HSM Vendor
HSM Model
HSM Firmware Version
Connector Version
KSP Version
SDK Version
Provider Name
Connector Service
Connector Account
Connector Listener
HSM Authentication Method
Authentication Key ID
Authentication Key Capabilities
Authentication Key Domains
Delegated Capabilities
Configuration Location
Configuration ACL
Binary ACL
Service ACL
Local User Access
Interactive Logon Rights
Administrative Access Paths
HSM Audit Configuration
CA Audit Configuration
Backup Architecture
Recovery Architecture
Vendor Advisory Status
Validation Method
Cleanup Result
```

Do not include:

```text
Actual HSM Password
Authentication Secret
Raw Private Key
Recovery Secret
```

in ordinary pentest evidence.

---

# ESC12 Assessment Checklist

## Applicability

- [ ] Identify Certification Authorities
- [ ] Identify CA hosts
- [ ] Determine whether HSM is used
- [ ] Identify HSM vendor
- [ ] Identify HSM model
- [ ] Confirm YubiHSM2
- [ ] If no YubiHSM2, do not label the condition ESC12

## Architecture

- [ ] Identify CA service
- [ ] Identify cryptographic provider
- [ ] Identify YubiHSM KSP
- [ ] Identify connector
- [ ] Identify SDK
- [ ] Identify HSM device
- [ ] Document signing flow
- [ ] Document authentication flow
- [ ] Document backup flow
- [ ] Document recovery flow

## Version Review

- [ ] Record HSM firmware
- [ ] Record connector version
- [ ] Record KSP version
- [ ] Record SDK version
- [ ] Record management-tool version
- [ ] Compare against vendor support
- [ ] Review current vendor advisories
- [ ] Review historical ESC12 research
- [ ] Do not infer vulnerability solely from product presence

## Host Security

- [ ] Review local users
- [ ] Review local administrators
- [ ] Review interactive logon
- [ ] Review RDP access
- [ ] Review WinRM access
- [ ] Review SMB administrative access
- [ ] Review service permissions
- [ ] Review binary permissions
- [ ] Review configuration permissions
- [ ] Review application control
- [ ] Review EDR coverage
- [ ] Review installed software

## HSM Authentication

- [ ] Identify authentication mechanism
- [ ] Identify authentication-key IDs
- [ ] Review domains
- [ ] Review capabilities
- [ ] Review delegated capabilities
- [ ] Review least privilege
- [ ] Verify default credentials removed
- [ ] Determine credential storage method
- [ ] Review credential-file permissions
- [ ] Review environment variables carefully
- [ ] Avoid exposing secrets during testing

## Key Protection

- [ ] Determine whether CA key is hardware backed
- [ ] Determine whether raw export is possible
- [ ] Determine whether backup export exists
- [ ] Review wrapped-key backups
- [ ] Review recovery material
- [ ] Review administrative signing capability
- [ ] Distinguish key extraction from signing abuse
- [ ] Determine whether arbitrary signing is possible
- [ ] Avoid production signing tests

## BloodHound

- [ ] Identify CA host
- [ ] Review paths to CA host
- [ ] Review administrative control over CA host
- [ ] Review `HostsCAService`
- [ ] Review Golden Certificate paths
- [ ] Consider HSM protection before assuming key extraction
- [ ] Treat CA host as Tier 0

## Safe Validation

- [ ] Begin with architecture review
- [ ] Perform read-only software inventory
- [ ] Perform read-only permission review
- [ ] Review HSM configuration
- [ ] Review vendor advisories
- [ ] Determine whether production exploitation is necessary
- [ ] Prefer laboratory reproduction
- [ ] Do not export production CA key
- [ ] Do not perform arbitrary production signing
- [ ] Do not reset HSM
- [ ] Do not delete HSM objects
- [ ] Do not brute-force HSM authentication
- [ ] Stop when sufficient evidence exists

## Detection

- [ ] Enable appropriate CA auditing
- [ ] Review cryptographic auditing
- [ ] Review HSM audit logs
- [ ] Monitor HSM authentication
- [ ] Monitor unexpected HSM sessions
- [ ] Monitor signing operations
- [ ] Correlate signing with CA requests
- [ ] Monitor connector changes
- [ ] Monitor KSP changes
- [ ] Monitor HSM configuration
- [ ] Monitor service configuration
- [ ] Monitor sensitive file access
- [ ] Monitor CA backup operations
- [ ] Monitor unexpected local access to CA
- [ ] Centralise HSM telemetry where possible

## Hardening

- [ ] Update HSM firmware
- [ ] Update connector
- [ ] Update KSP
- [ ] Update SDK
- [ ] Remove default credentials
- [ ] Protect authentication material
- [ ] Apply least HSM capabilities
- [ ] Apply HSM domain separation
- [ ] Separate signing and administrative identities
- [ ] Protect recovery material
- [ ] Restrict configuration ACLs
- [ ] Restrict binary ACLs
- [ ] Restrict CA logon
- [ ] Segment CA network access
- [ ] Restrict outbound CA traffic
- [ ] Use hardened admin workstations
- [ ] Treat CA and HSM as Tier 0
- [ ] Document key ceremonies
- [ ] Maintain key-rotation procedure

## Incident Response

- [ ] Isolate affected CA if necessary
- [ ] Preserve evidence
- [ ] Preserve HSM logs
- [ ] Preserve CA logs
- [ ] Preserve Windows logs
- [ ] Preserve EDR telemetry
- [ ] Determine HSM authentication exposure
- [ ] Determine key extraction
- [ ] Determine signing abuse
- [ ] Correlate HSM signing with CA requests
- [ ] Search for forged certificates
- [ ] Review certificate authentication
- [ ] Review privileged identities
- [ ] Rotate HSM authentication where required
- [ ] Reprovision HSM where required
- [ ] Rotate CA signing key where required
- [ ] Revoke affected certificates
- [ ] Rebuild PKI trust where necessary

## Reporting

- [ ] Describe actual HSM architecture
- [ ] Describe exact weak security boundary
- [ ] Identify required local privilege
- [ ] Identify affected component versions
- [ ] Identify available HSM capabilities
- [ ] Explain CA trust
- [ ] Separate verified impact from theoretical impact
- [ ] Avoid exposing HSM secrets
- [ ] Avoid generic "ESC12 vulnerable" wording
- [ ] Provide vendor-aligned remediation

---

# ESC12 Testing Model

The normal HSM model is:

```text
AD CS
  |
  v
HSM Interface
  |
  v
YubiHSM2
  |
  v
CA Private Key
```

The expected security boundary is:

```text
Low-Privilege User
       |
       X
HSM Authentication
       |
       X
CA Private Key
```

The ESC12 model is:

```text
Low-Privilege CA Access
       |
       v
HSM Integration Weakness
       |
       v
HSM Authentication / Session
       |
       v
Sensitive HSM Capability
       |
       v
CA Signing Operations
```

The key-extraction model is:

```text
CA Private Key
      |
      v
Extracted
      |
      v
Attacker-Controlled Key
```

The signing-oracle model is:

```text
CA Private Key
      |
      X
Not Extracted
      |
      v
HSM Signs Attacker-Controlled Data
```

The Golden Certificate relationship is:

```text
CA Signing Capability
       |
       v
Forged Certificate
       |
       v
Trusted CA Chain
       |
       v
NT Authentication Trust
       |
       v
Target Principal
```

The host-compromise model is:

```text
Attacker
   |
   v
CA Host Access
   |
   +--> CA Administration
   |
   +--> Configuration Control
   |
   +--> HSM Attack Surface
```

The safe-testing model is:

```text
Identify HSM
    |
    v
Identify Versions
    |
    v
Review Architecture
    |
    v
Review Permissions
    |
    v
Review Authentication Boundary
    |
    v
Review Vendor Advisories
    |
    v
Evidence Sufficient?
    |
    +--> Yes -> Report
    |
    +--> No
            |
            v
      Reproduce in Lab
```

The detection model is:

```text
HSM Authentication
       |
       v
Signing Operation
       |
       v
Matching CA Request?
       |
       +--> Yes -> Expected Workflow
       |
       +--> No
              |
              v
          Investigate
```

The defensive model is:

```text
HSM
 +
Strong Authentication
 +
Least Capability
 +
Secure CA Host
 +
Protected Configuration
 +
Current Software
 +
Audit Logging
 =
Strong CA Key Protection
```

For penetration testers:

```text
Do Not Ask:
"Can I dump the production CA key?"

Ask:
"Does the HSM maintain its intended
security boundary when the CA host
is accessed by an unprivileged
principal?"
```

For defenders:

```text
Do Not Assume:
"The key is in an HSM,
therefore the CA is safe."

Ask:
"Who can authenticate to the HSM,
what operations can they perform,
and can the CA host expose those
capabilities to another process?"
```

The complete ESC12 relationship is:

```text
CA Host
   |
   v
HSM Integration
   |
   v
Authentication Boundary
   |
   v
HSM Capabilities
   |
   v
CA Signing Key
   |
   v
PKI Trust
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

ESC11:

[AD CS ESC11](esc11.md)

Credential Access:

[Credential Access](../credential-access.md)

BloodHound:

[BloodHound](../bloodhound.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs/esc13.md
```

---

# References

## Certipy - ESC12

[Certipy - Privilege Escalation Techniques](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation){ target="_blank" rel="noopener noreferrer" }

Current Certipy documentation describes ESC12 specifically in the context of YubiHSM2 and notes that Certipy does not provide a general automated detection mechanism for this condition.

---

## SpecterOps - AD CS Attack Paths in BloodHound

[SpecterOps - AD CS Attack Paths in BloodHound Part 2](https://specterops.io/blog/2024/05/01/adcs-attack-paths-in-bloodhound-part-2/){ target="_blank" rel="noopener noreferrer" }

SpecterOps discusses the importance of CA hosts, CA private keys, HSM protection, Golden Certificates, and treating enterprise CA systems as Tier 0.

---

## BloodHound - GoldenCert

[BloodHound - GoldenCert](https://bloodhound.specterops.io/resources/edges/golden-cert){ target="_blank" rel="noopener noreferrer" }

BloodHound documents the relationship between control of a CA signing key and the ability to forge certificates for Active Directory authentication, while noting that TPM or HSM protection may prevent straightforward key extraction.

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

Certified Pre-Owned provides foundational research into Active Directory Certificate Services attack paths and CA private-key abuse.

---

## Yubico - YubiHSM2

[Yubico - YubiHSM2](https://www.yubico.com/product/yubihsm-2/){ target="_blank" rel="noopener noreferrer" }

Consult current Yubico documentation, firmware releases and security advisories when assessing an actual YubiHSM2 deployment.

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC12 is one of the most specialised AD CS escalation categories.

It should not be treated like a normal certificate-template vulnerability.

The relevant security boundary is:

```text
Windows CA Host
      |
      v
HSM Integration
      |
      v
Hardware Security Module
      |
      v
CA Signing Key
```

An HSM provides substantial security value because the private key can remain inside dedicated cryptographic hardware.

However:

```text
Key Is Non-Exportable
```

does not automatically mean:

```text
Key Cannot Be Abused
```

The CA still needs a mechanism for requesting signatures.

Therefore the important questions are:

```text
Who Can Authenticate to the HSM?

What HSM Capabilities Do They Receive?

Where Is the Authentication Material Stored?

Can an Unprivileged Process Use It?

Can the HSM Perform Signing Outside
the Intended CA Workflow?
```

ESC12 becomes relevant when the answers demonstrate that the expected HSM security boundary can be crossed from a lower-privileged position on the CA host.

At the same time:

```text
YubiHSM2 Installed
```

must never automatically become:

```text
ESC12 Vulnerable
```

The exact firmware, connector, KSP, authentication architecture, capabilities, permissions and vendor security status must be reviewed.

For a production penetration test, the preferred evidence chain is:

```text
YubiHSM2 Identified
       |
       v
Architecture Documented
       |
       v
Versions Recorded
       |
       v
Permissions Reviewed
       |
       v
Authentication Boundary Reviewed
       |
       v
Vendor Condition Correlated
```

rather than:

```text
Extract Production CA Key
```

The latter creates unnecessary risk.

For defenders, the broader lesson extends beyond YubiHSM2:

```text
Hardware Protection
       |
       v
Is Only as Strong as
       |
       v
The Software, Credentials,
Permissions and Administration
Surrounding the Hardware
```

The CA server, HSM integration components, authentication keys, backup material, recovery procedures and administrative workstations all form part of the cryptographic trust boundary.

Protecting the hardware while leaving those surrounding components exposed does not provide a complete PKI security model.
