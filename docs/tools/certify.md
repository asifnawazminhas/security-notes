# Certify

Certify is a C# Active Directory Certificate Services (AD CS) assessment tool from GhostPack. It is designed to enumerate enterprise certificate authorities, certificate templates, enrollment services, permissions, and certificate-related configurations that may create unintended privilege paths in Active Directory.

Certify is particularly useful during authorised Active Directory assessments because AD CS can introduce trust relationships that are not immediately visible through traditional user, group, ACL, or Kerberos enumeration.

!!! warning "Authorised Testing Only"
    Certificate enrollment can result in authentication material that may provide access as another identity. Use certificate-request functionality only when AD CS exploitation and the affected identities are explicitly within scope.

---

## Overview

Certify can help answer questions such as:

```text
Is AD CS deployed?
        |
        v
Which Enterprise CAs exist?
        |
        v
Which certificate templates exist?
        |
        v
Who can enroll?
        |
        v
What identities can certificates represent?
        |
        v
Which security controls apply?
        |
        v
Can the configuration create an unintended trust path?
```

Typical assessment areas include:

| Area | Purpose |
| --- | --- |
| CA discovery | Identify Enterprise Certificate Authorities |
| Template enumeration | Identify published certificate templates |
| Enrollment permissions | Determine who can request certificates |
| Template permissions | Review who can modify templates |
| Subject configuration | Determine how certificate identities are constructed |
| EKUs | Determine permitted certificate purposes |
| Enrollment agents | Identify certificate request agent configurations |
| CA permissions | Review CA-level administrative permissions |
| Web enrollment | Identify HTTP-based enrollment services |
| Certificate requests | Validate selected AD CS findings |
| Authentication | Determine whether issued certificates can support authentication |

The important assessment model is:

```text
AD CS Observation
        |
        v
Candidate Misconfiguration
        |
        v
Required Preconditions
        |
        v
Certificate Trust Relationship
        |
        v
Controlled Validation
        |
        v
Evidence
        |
        v
Security Conclusion
```

---

# Official Project

Certify is part of GhostPack.

- [Certify - Official GhostPack Repository](https://github.com/GhostPack/Certify){ target="_blank" rel="noopener noreferrer" }
- [Certify README](https://github.com/GhostPack/Certify/blob/main/README.md){ target="_blank" rel="noopener noreferrer" }

Use the upstream project as the primary reference.

Certify is source-oriented, so assessment teams commonly compile it from source.

Record the exact source revision used during testing.

---

# Certify and AD CS

Active Directory Certificate Services provides Public Key Infrastructure functionality for Windows environments.

A simplified architecture is:

```mermaid
flowchart LR
    A[Active Directory] --> B[Enterprise CA]
    B --> C[Certificate Templates]
    D[Domain Principal] --> C
    C --> E[Certificate Request]
    E --> B
    B --> F[Issued Certificate]
    F --> G[Authentication or Other Purpose]
```

The certificate authority trusts Active Directory identities and policies when processing certificate requests.

This creates an important security boundary:

```text
Active Directory Identity
        +
Certificate Template
        +
Enrollment Permission
        +
CA Policy
        =
Certificate Identity
```

If these components are configured incorrectly, certificate issuance may create an unintended privilege path.

---

# Certify vs Certipy

Certify and Certipy overlap significantly but target different operator environments.

| Certify | Certipy |
| --- | --- |
| C# / .NET | Python |
| Primarily Windows | Commonly Linux-based |
| GhostPack | Certipy project |
| Native domain context convenient | Remote assessment workflows convenient |
| AD CS enumeration | AD CS enumeration |
| Certificate requests | Certificate requests |
| Template analysis | Template analysis |
| Windows-centric operation | Broad AD CS workflow automation |

A useful rule of thumb is:

```text
Operating from Windows domain context
        |
        +--> Certify

Operating primarily from Linux
        |
        +--> Certipy
```

This is not absolute.

Using both tools can be useful for validating results independently.

---

# Build from Source

Clone the official repository in an authorised development environment:

```bash
git clone https://github.com/GhostPack/Certify.git
```

Enter the repository:

```bash
cd Certify
```

Record the source revision:

```bash
git rev-parse HEAD
```

Compile using a compatible Visual Studio/.NET development environment.

The resulting executable is typically:

```text
Certify.exe
```

Record:

```text
Source Repository
Commit
Build Environment
SHA256
Assessment Date
```

---

# Record the Executable

Before use:

```powershell
Get-FileHash .\Certify.exe -Algorithm SHA256
```

Example evidence:

```text
Tool: Certify
Source: GhostPack
Revision: <COMMIT>
SHA256: <HASH>
Timestamp: <TIME>
```

This provides reproducibility when the executable was compiled internally.

---

# Basic Usage

Display available commands:

```powershell
.\Certify.exe
```

or:

```powershell
.\Certify.exe --help
```

The exact command syntax depends on the Certify revision.

Always check the build being used rather than relying exclusively on commands from older write-ups.

---

# Establish the Current Context

Before running Certify, record the Windows and Active Directory context.

Identity:

```powershell
whoami
```

Domain:

```powershell
$env:USERDNSDOMAIN
```

Logon server:

```powershell
$env:LOGONSERVER
```

Groups:

```powershell
whoami /groups
```

Privileges:

```powershell
whoami /priv
```

Domain Controller discovery:

```powershell
nltest /dsgetdc:<DOMAIN>
```

This establishes the identity from which AD CS enumeration occurs.

---

# Discover Active Directory Certificate Services

The first question is:

```text
Does the domain use AD CS?
```

Certify can enumerate Enterprise Certificate Authorities.

A commonly used discovery action is:

```powershell
.\Certify.exe cas
```

Review the output for information such as:

```text
CA Name
DNS Hostname
Certificate Subject
Certificate Serial Number
Validity
Enrollment Services
Permissions
Web Enrollment
```

The exact fields depend on the Certify build.

---

# Enterprise Certificate Authorities

An Enterprise CA is integrated with Active Directory.

Conceptually:

```text
Active Directory
        |
        v
Enterprise CA
        |
        v
Certificate Templates
        |
        v
Domain Enrollment
```

Important assessment questions include:

```text
Which CA hosts exist?

Which templates are published?

Who administers the CA?

Who can enroll?

Which authentication-capable templates exist?

Are HTTP enrollment interfaces enabled?
```

Do not assume that the existence of an Enterprise CA is itself a vulnerability.

---

# Enumerate Certificate Templates

Certify can enumerate certificate templates.

A broad template search can be performed using the relevant template enumeration functionality supported by the installed build.

A commonly used action is:

```powershell
.\Certify.exe find
```

This can return information about:

```text
Certificate Authorities
Certificate Templates
Enrollment Rights
Extended Key Usage
Subject Name Configuration
Manager Approval
Authorized Signatures
Validity
Renewal Period
Template Permissions
```

The objective is not merely to identify templates.

The objective is to understand their trust relationships.

---

# Find Potentially Vulnerable Templates

Certify includes filtering intended to identify templates with potentially dangerous configurations.

A commonly encountered workflow is:

```powershell
.\Certify.exe find /vulnerable
```

Treat this as:

```text
Candidate Discovery
```

not:

```text
Confirmed Vulnerability
```

Every result must be validated.

The tool may identify conditions that are exploitable only when additional prerequisites exist.

---

# Current User Perspective

Where supported by the Certify build, vulnerable-template enumeration can be evaluated from the current user's security context.

This is important because:

```text
Template Misconfiguration
        +
No Enrollment Rights
        =
Potentially Not Exploitable by Current User
```

while:

```text
Template Misconfiguration
        +
Current User Can Enroll
        =
Candidate Attack Path
```

Always review both configuration and effective enrollment permissions.

---

# Certificate Template Security Model

A certificate template combines several security properties.

```text
Certificate Template
├── Enrollment Permissions
├── Template ACL
├── Subject Name Rules
├── Extended Key Usage
├── Issuance Requirements
├── Authorized Signatures
├── Manager Approval
├── Validity Period
└── Cryptographic Settings
```

A meaningful finding often depends on several of these properties interacting.

---

# Enrollment Rights

Enrollment permissions determine which principals may request certificates from a template.

Relevant permissions can include concepts such as:

```text
Enroll
Autoenroll
```

Principals may include:

```text
Domain Users
Domain Computers
Authenticated Users
Specific Groups
Specific Users
Service Accounts
```

The existence of enrollment rights is not inherently insecure.

The risk depends on what identity and purpose the resulting certificate can represent.

---

# Template ACLs

Certificate templates are Active Directory objects and therefore have ACLs.

Important permissions may include:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
WriteProperty
```

A principal capable of modifying a certificate template may be able to change security-sensitive properties.

The reasoning chain becomes:

```text
Principal
    |
    v
Template Modification Rights
    |
    v
Security-Sensitive Property Change
    |
    v
Certificate Enrollment
    |
    v
Potential Authentication Path
```

Template ACL findings should therefore be correlated with Active Directory ACL analysis.

---

# Extended Key Usage

Extended Key Usage defines purposes for which a certificate may be used.

Common authentication-related EKUs include concepts such as:

```text
Client Authentication
Smart Card Logon
PKINIT Client Authentication
Any Purpose
```

The security question is:

```text
Can this certificate be used for authentication?
```

not merely:

```text
Does the template issue certificates?
```

Templates used only for narrow non-authentication purposes may have very different security implications.

---

# Subject Alternative Name

Certificate identity may be influenced through the certificate subject or Subject Alternative Name.

Potential identity forms include:

```text
DNS Name
User Principal Name
Email
Distinguished Name
```

The security-sensitive question is:

```text
Who controls the identity placed into the certificate?
```

If an unprivileged requester can influence an authentication identity beyond their own account, the trust relationship requires careful review.

---

# Manager Approval

Some templates require certificate manager approval before issuance.

Conceptually:

```text
Certificate Request
        |
        v
Pending
        |
        v
Manager Approval
        |
        v
Certificate Issued
```

This can significantly change exploitability.

Therefore:

```text
Potentially Dangerous Template
        +
Manager Approval Required
        !=
Immediately Exploitable
```

Validate the actual issuance requirements.

---

# Authorized Signatures

Templates may require one or more authorised signatures before a certificate can be issued.

This creates an additional security boundary.

Record:

```text
Authorized Signature Count
Required Application Policy
Enrollment Agent Requirements
```

when evaluating a candidate template.

---

# Enrollment Agents

Enrollment agents can request certificates on behalf of other users under specific configurations.

Conceptually:

```text
Enrollment Agent
        |
        v
Certificate Request
        |
        v
On Behalf of User
        |
        v
CA
```

This is legitimate enterprise functionality.

The security risk depends on:

- Who can become an enrollment agent
- Which templates permit enrollment-agent use
- Which users can be represented
- Whether restrictions are correctly configured

---

# CA Permissions

Certificate Authority permissions are separate from certificate-template permissions.

Important CA-level roles and permissions may include:

```text
Manage CA
Manage Certificates
Request Certificates
```

A principal with excessive CA-level permissions may have capabilities beyond ordinary certificate enrollment.

Keep these boundaries separate:

```text
Template ACL
        !=
CA ACL
        !=
Enrollment Rights
```

---

# Certificate Enrollment Flow

A simplified enrollment process is:

```mermaid
sequenceDiagram
    participant U as Domain User
    participant AD as Active Directory
    participant CA as Certificate Authority

    U->>AD: Discover CA and Template
    AD-->>U: Template Configuration
    U->>CA: Certificate Request
    CA->>AD: Evaluate Identity and Policy
    AD-->>CA: Directory Information
    CA-->>U: Certificate or Denial
```

A successful certificate request means:

```text
CA Accepted Request
```

It does not automatically mean:

```text
Certificate Can Authenticate
```

The certificate's EKUs, identity, chain, and target authentication mechanism must also be considered.

---

# Certificate Requests

Certify can submit certificate requests using templates available to the current context.

Before requesting a certificate, establish:

```text
Template
CA
Requester
Requested Identity
Purpose
Scope Approval
```

Use the current Certify help to review request syntax:

```powershell
.\Certify.exe request /?
```

Certificate requests can create authentication material.

Do not submit requests against arbitrary privileged identities merely to see whether they work.

---

# Request Validation Model

Use:

```text
Candidate Template
        |
        v
Confirm Enrollment Permission
        |
        v
Confirm Identity Control
        |
        v
Confirm Authentication EKU
        |
        v
Confirm Issuance Requirements
        |
        v
Request Approved Test Certificate
        |
        v
Validate Intended Security Property
```

This produces a controlled proof rather than indiscriminate certificate issuance.

---

# Certificate Output

Certificate enrollment may result in material such as:

```text
Certificate
Private Key
PEM
PFX / PKCS#12
```

Treat this material as credentials.

Never:

- Commit certificates containing private keys to Git
- Store them in documentation repositories
- Include private keys in screenshots
- Upload them to shared services
- Leave them on assessment hosts unnecessarily

---

# PEM and PFX

A certificate and private key may be represented in different formats.

PEM commonly resembles:

```text
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
```

and:

```text
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
```

PKCS#12 containers commonly use:

```text
.pfx
.p12
```

and may contain:

```text
Certificate
+
Private Key
+
Certificate Chain
```

Treat PFX files as sensitive authentication material.

---

# Convert Certificate Material

OpenSSL can be used in an authorised assessment environment to convert certificate formats.

For example, when converting approved test material into a PFX container:

```bash
openssl pkcs12 -export \
  -in certificate.pem \
  -inkey private-key.pem \
  -out certificate.pfx
```

Use a strong temporary export password.

Remove temporary certificate material after testing.

---

# Certificate Authentication

Active Directory can support certificate-based Kerberos authentication through PKINIT when the environment and certificate satisfy the required conditions.

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
Kerberos Authentication
```

Therefore an authentication-capable certificate can become equivalent to powerful credential material.

The complete path must still be validated.

---

# AD CS Attack Paths

AD CS security research commonly categorises certificate-related privilege paths using ESC identifiers.

Examples include:

```text
ESC1
ESC2
ESC3
ESC4
...
```

These identifiers describe different classes of AD CS configuration weakness.

Certify can assist with identifying some of the underlying conditions.

The dedicated AD CS notes should contain the full ESC taxonomy and exploitation prerequisites.

Certify should remain focused on:

```text
Discovery
Enumeration
Validation
Tool Operation
```

---

# ESC1 Concept

A classic certificate-template risk can occur when several conditions combine.

For example:

```text
Low-Privilege Enrollment
        +
Requester Controls Subject Identity
        +
Authentication-Capable EKU
        +
No Additional Approval Barrier
        =
Potential Identity Impersonation Path
```

The important point is that no single property proves the issue.

The complete combination must be validated.

---

# ESC2 Concept

Templates with overly broad certificate purposes can create security concerns.

For example:

```text
Any Purpose
```

or configurations without sufficiently constrained application policies may expand how the resulting certificate can be used.

Exploitability depends on additional environmental conditions.

---

# ESC3 Concept

Enrollment-agent certificate functionality can create an impersonation path when enrollment-agent restrictions are insufficient.

The trust relationship becomes:

```text
Principal
    |
    v
Enrollment Agent Certificate
    |
    v
Request on Behalf of Another Principal
    |
    v
Authentication Certificate
```

Validate all issuance and enrollment-agent restrictions.

---

# ESC4 Concept

Certificate-template ACL weaknesses can allow an attacker-controlled principal to modify template properties.

Conceptually:

```text
Template ACL Control
        |
        v
Modify Template
        |
        v
Create Dangerous Configuration
        |
        v
Enroll
        |
        v
Restore Configuration
```

During production assessments, modifying certificate templates can affect legitimate enrollment and should not be performed casually.

Prefer configuration evidence where it sufficiently demonstrates the risk.

---

# CA-Level Misconfigurations

Not all AD CS issues exist at the template level.

Other security-sensitive areas can include:

```text
CA Permissions
CA Policy
Enrollment Services
HTTP Enrollment
Certificate Mapping
NTLM Authentication
CA Security Extensions
```

Certify output should therefore be correlated with broader AD CS assessment tooling and manual validation.

---

# Web Enrollment

AD CS environments may expose web enrollment interfaces.

Common paths historically include services under:

```text
/certsrv/
```

Do not assume the path exists merely because AD CS is deployed.

Identify the actual service first.

Where web enrollment exists, assess:

```text
Authentication Method
HTTPS Enforcement
Extended Protection for Authentication
NTLM Exposure
Relay Protections
Network Accessibility
```

These conditions are particularly relevant to NTLM relay-related AD CS risks.

---

# Discover HTTP Enrollment

Certify output may provide information about CA enrollment endpoints depending on the build and environment.

Manual validation can also inspect known CA hosts for authorised HTTP/HTTPS services.

From Windows:

```powershell
Test-NetConnection <CA_HOST> -Port 80
```

```powershell
Test-NetConnection <CA_HOST> -Port 443
```

Network reachability alone does not prove web enrollment is enabled.

---

# Certify and LDAP

Much of AD CS discovery depends on Active Directory information stored in LDAP.

Relevant configuration exists under the Configuration naming context.

Conceptually:

```text
Active Directory
        |
        v
Configuration
        |
        v
Public Key Services
        |
        +--> Certificate Templates
        |
        +--> Enrollment Services
        |
        +--> OIDs
```

This is why Certify generally benefits from normal domain connectivity and directory access.

---

# Required Connectivity

Relevant services may include:

| Port | Service |
| ---: | --- |
| 53 | DNS |
| 88 | Kerberos |
| 135 | RPC |
| 389 | LDAP |
| 445 | SMB |
| 636 | LDAPS |
| 3268 | Global Catalog |
| 3269 | Global Catalog over TLS |

Certificate enrollment itself may involve additional RPC/DCOM or HTTP-based services depending on the enrollment method.

---

# DNS

Correct DNS is important.

Check:

```powershell
Resolve-DnsName <DOMAIN>
```

Domain Controller discovery:

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.<DOMAIN>
```

CA hostname:

```powershell
Resolve-DnsName <CA_HOST>
```

Do not interpret a Certify connection error as an AD CS configuration issue until DNS and network connectivity have been validated.

---

# Certify Through a Pivot

Certify is typically run from Windows.

If the Windows host itself can reach the domain and CA, no external pivot may be necessary.

When operating from another network, validate:

```text
DNS
LDAP
Kerberos
CA Enrollment Protocol
```

individually.

A tunnel providing only:

```text
TCP/445
```

is not automatically sufficient for AD CS enumeration and enrollment.

---

# Current User vs Alternate Credentials

Whenever possible, begin enumeration using the current authorised domain context.

This provides an accurate answer to:

```text
What can this principal discover and enroll in?
```

Using higher-privileged credentials can obscure the security boundary being tested.

Maintain the distinction:

```text
Current User Can Enroll
```

versus:

```text
Administrator Can Enroll
```

These have very different security implications.

---

# Template Permissions vs Enrollment Permissions

This distinction is important.

```text
Enrollment Permission
        |
        +--> Can request a certificate

Template Modification Permission
        |
        +--> Can alter how certificates are issued
```

A principal may have:

```text
Enroll
```

without:

```text
Write
```

or:

```text
Write
```

without currently having:

```text
Enroll
```

Both can be security-relevant for different reasons.

---

# Effective Permissions

Group membership can make certificate permissions less obvious.

For example:

```text
User
 |
 v
Group A
 |
 v
Group B
 |
 v
Certificate Template Permission
```

Therefore:

```text
No Direct ACE
```

does not necessarily mean:

```text
No Permission
```

Review nested group membership and effective access.

---

# Machine Certificates

AD CS is not limited to user certificates.

Computer templates can issue certificates representing machine identities.

Potential uses include:

```text
Machine Authentication
TLS
IPsec
Network Authentication
Service Authentication
```

Computer certificate findings should therefore be assessed separately from user certificate findings.

---

# Certificate Validity

Record:

```text
Validity Period
Renewal Period
```

Long-lived authentication certificates can increase the impact of certificate compromise.

The security significance depends on:

- Certificate purpose
- Revocation capability
- Private-key protection
- Identity represented
- Lifetime
- Renewal behaviour

---

# Private Key Protection

Certificate security does not stop at issuance.

Consider:

```text
Where is the private key stored?

Is it exportable?

Which principal can access it?

Is hardware protection used?

Can another process access it?

How long does it remain valid?
```

Certificate-template assessment and endpoint private-key protection are related but separate security boundaries.

---

# Requester Supplied Subject

One security-sensitive template property is whether the requester can supply subject information.

The assessment question is:

```text
Can the requester control the identity?
```

Then:

```text
Can that identity be used for authentication?
```

Then:

```text
Can the requester enroll?
```

Only the complete chain establishes a meaningful privilege path.

---

# Strong Certificate Mapping

Modern Windows environments may enforce stronger certificate mapping behaviour.

This can affect whether a certificate that appears structurally suitable can actually authenticate as the intended Active Directory principal.

Therefore:

```text
Certificate Issued
        !=
Identity Mapping Accepted
        !=
Authentication Successful
```

Always validate the effective environment.

---

# Certify Output Review

Do not read Certify output only for:

```text
Vulnerable
```

Review:

```text
CA Name
Template Name
Enabled State
Enrollment Rights
Template Permissions
Subject Configuration
EKUs
Manager Approval
Authorized Signatures
Validity
Private Key Flags
CA Configuration
```

The most useful output is often the combination of several properties.

---

# Save Output

For evidence collection:

```powershell
.\Certify.exe find | Tee-Object -FilePath .\certify-find.txt
```

For candidate vulnerable configurations:

```powershell
.\Certify.exe find /vulnerable |
    Tee-Object -FilePath .\certify-vulnerable.txt
```

Review files for sensitive information before including them in assessment evidence.

---

# Compare with Certipy

When possible, validate important findings using a second implementation.

For example:

```text
Certify
    |
    v
Candidate Template
    |
    v
Certipy
    |
    v
Independent Enumeration
    |
    v
Manual Validation
```

Agreement between tools increases confidence, but manual interpretation remains necessary.

See:

```text
docs/tools/certipy.md
```

---

# Troubleshooting

## Certify Does Not Start

Check:

```powershell
Get-Item .\Certify.exe
```

Hash:

```powershell
Get-FileHash .\Certify.exe -Algorithm SHA256
```

Potential causes include:

- Defender
- EDR
- WDAC
- AppLocker
- Missing .NET runtime
- Build incompatibility
- File corruption

---

# Domain Cannot Be Found

Check:

```powershell
$env:USERDNSDOMAIN
```

Then:

```powershell
Resolve-DnsName $env:USERDNSDOMAIN
```

Domain Controller:

```powershell
nltest /dsgetdc:<DOMAIN>
```

LDAP:

```powershell
Test-NetConnection <DC> -Port 389
```

Kerberos:

```powershell
Test-NetConnection <DC> -Port 88
```

---

# CA Cannot Be Reached

Resolve the CA:

```powershell
Resolve-DnsName <CA_HOST>
```

Then test the enrollment protocol relevant to the environment.

For HTTP:

```powershell
Test-NetConnection <CA_HOST> -Port 80
```

HTTPS:

```powershell
Test-NetConnection <CA_HOST> -Port 443
```

RPC endpoint mapper:

```powershell
Test-NetConnection <CA_HOST> -Port 135
```

Do not assume one failed port means the CA itself is unavailable.

---

# No Vulnerable Templates Found

This can mean:

```text
No Candidate Configuration Found
```

but it can also mean:

- Current user lacks visibility
- No Enterprise CA is available
- Templates are not published
- Tool version differs
- Permissions differ
- Network access is incomplete
- Modern mitigations affect classification

Validate the environment before concluding:

```text
AD CS Secure
```

---

# Template Appears Vulnerable but Request Fails

Check:

```text
Template Published?
Enrollment Permission?
Manager Approval?
Authorized Signatures?
CA Accepting Template?
Subject Requirements?
Certificate Mapping?
Network Connectivity?
```

A candidate configuration and successful enrollment are separate stages.

---

# Certificate Issued but Authentication Fails

Check:

```text
EKU
Certificate Identity
UPN / SID Mapping
Certificate Chain
KDC Support
PKINIT
Domain Controller Certificate
Certificate Validity
Strong Mapping Enforcement
Clock
```

Do not conclude that certificate authentication is possible solely because enrollment succeeded.

---

# Application Control

Certify execution may be affected by:

```text
Defender
EDR
WDAC
AppLocker
```

If execution fails:

```text
Observed Failure
        |
        v
Identify Enforcement Source
        |
        v
Validate Effective Policy
        |
        v
Security Conclusion
```

Do not label a failure as:

```text
WDAC Block
```

unless WDAC was actually confirmed as the enforcing control.

---

# Evidence Collection

Useful evidence may include:

- Current user
- Domain
- Domain Controller
- CA hostname
- CA name
- Template name
- Template enabled state
- Enrollment permissions
- Template ACL
- EKUs
- Subject configuration
- Manager approval
- Authorized signatures
- Certificate validity
- Certify revision
- Certify SHA256
- Controlled certificate request result
- Authentication validation result
- Timestamp
- Detection telemetry
- Cleanup confirmation

A strong evidence chain is:

```text
Principal
    |
    v
Enrollment / Modification Rights
    |
    v
Template Configuration
    |
    v
CA Issuance Behaviour
    |
    v
Certificate Capability
    |
    v
Authentication / Privilege Impact
```

---

# Security Interpretation

Do not report:

```text
Certify says vulnerable.
```

Instead explain the actual security relationship.

For example:

```text
Authenticated Users
        |
        v
Enroll Permission
        |
        v
Template Allows Requester-Controlled Identity
        |
        v
Authentication EKU
        |
        v
No Approval Requirement
        |
        v
Potential Certificate-Based Impersonation
```

This explains why the configuration matters.

---

# Detection Opportunities

Defenders can monitor AD CS activity at several layers.

## Active Directory

Monitor changes to:

```text
Certificate Templates
Template ACLs
Enrollment Services
CA-related objects
Delegation around CA services
```

---

## Certificate Authority

CA auditing can provide visibility into:

```text
Certificate Requests
Certificate Issuance
Certificate Denials
CA Configuration Changes
Certificate Revocation
```

Enable appropriate CA auditing based on organisational requirements.

---

## Windows Security Events

Relevant certificate-service events can include:

```text
4886
4887
4888
4890
4891
```

The exact events generated depend on auditing configuration and the operation performed.

Correlate certificate events with:

```text
Requester
Template
Certificate Subject
Certificate Serial Number
Timestamp
Source Host
```

---

# Monitor Template Changes

Template modification is particularly important.

A dangerous sequence can resemble:

```text
Template Modified
        |
        v
Certificate Requested
        |
        v
Template Restored
```

A point-in-time configuration review may miss this.

Historical directory-change telemetry can therefore be valuable.

---

# Defensive Recommendations

Relevant controls include:

- Restrict certificate enrollment permissions
- Restrict certificate-template modification rights
- Remove unnecessary requester-supplied subject configuration
- Restrict authentication-capable EKUs
- Require approval where appropriate
- Configure enrollment-agent restrictions
- Review CA administrative permissions
- Protect CA hosts as privileged infrastructure
- Require HTTPS for web enrollment
- Configure Extended Protection for Authentication where supported
- Reduce NTLM exposure
- Monitor certificate issuance
- Monitor certificate-template changes
- Use strong certificate mapping
- Maintain certificate revocation processes
- Review long-lived authentication certificates
- Use managed service identities where appropriate

The defensive objective is:

```text
Controlled Enrollment
        +
Controlled Identity
        +
Restricted Certificate Purpose
        +
Protected CA
        +
Strong Mapping
        +
Monitoring
        =
Reduced AD CS Risk
```

---

# CA Security Tier

Enterprise Certificate Authorities should be treated as high-value infrastructure.

Compromise of a trusted CA can undermine identity controls far beyond one endpoint.

Protect CA systems using controls appropriate to privileged infrastructure:

```text
Restricted Administration
Network Segmentation
Application Control
Privileged Monitoring
Secure Backup
Key Protection
Patch Management
Audit Logging
```

---

# Operational Safety

During production assessments:

- Enumerate before requesting certificates
- Limit requests to approved templates
- Use designated test identities where possible
- Avoid arbitrary privileged-user impersonation
- Avoid modifying production templates unless explicitly authorised
- Avoid CA configuration changes
- Avoid certificate revocation unless authorised
- Protect generated private keys
- Remove test certificates and keys after use where appropriate
- Record certificate serial numbers
- Record every certificate request made during testing

AD CS is identity infrastructure.

Treat changes with the same caution as changes to privileged Active Directory objects.

---

# Cleanup

Remove temporary output:

```powershell
Remove-Item .\certify-find.txt -ErrorAction SilentlyContinue
```

Remove temporary test certificate files where required:

```powershell
Remove-Item .\certificate.pem -ErrorAction SilentlyContinue
Remove-Item .\private-key.pem -ErrorAction SilentlyContinue
Remove-Item .\certificate.pfx -ErrorAction SilentlyContinue
```

If a certificate was installed into a certificate store during testing, identify it by thumbprint before removal.

Example inspection:

```powershell
Get-ChildItem Cert:\CurrentUser\My
```

Do not remove certificates based only on a display name.

Record:

```text
Subject
Thumbprint
Serial Number
Issuer
```

before making changes.

---

# Quick Reference

## Help

```powershell
.\Certify.exe
```

```powershell
.\Certify.exe --help
```

## Hash

```powershell
Get-FileHash .\Certify.exe -Algorithm SHA256
```

## Enumerate CAs

```powershell
.\Certify.exe cas
```

## Enumerate Templates

```powershell
.\Certify.exe find
```

## Candidate Vulnerable Templates

```powershell
.\Certify.exe find /vulnerable
```

## Save Enumeration

```powershell
.\Certify.exe find |
    Tee-Object -FilePath .\certify-find.txt
```

## Save Candidate Findings

```powershell
.\Certify.exe find /vulnerable |
    Tee-Object -FilePath .\certify-vulnerable.txt
```

## Review Request Syntax

```powershell
.\Certify.exe request /?
```

## Domain

```powershell
$env:USERDNSDOMAIN
```

## Domain Controller

```powershell
nltest /dsgetdc:<DOMAIN>
```

## Test LDAP

```powershell
Test-NetConnection <DC> -Port 389
```

## Test Kerberos

```powershell
Test-NetConnection <DC> -Port 88
```

## Test CA HTTP

```powershell
Test-NetConnection <CA_HOST> -Port 80
```

## Test CA HTTPS

```powershell
Test-NetConnection <CA_HOST> -Port 443
```

## Test CA RPC

```powershell
Test-NetConnection <CA_HOST> -Port 135
```

---

# Assessment Checklist

## Preparation

- [ ] AD CS testing explicitly authorised
- [ ] Domain within scope
- [ ] CA systems within scope
- [ ] Certificate-request testing authorised
- [ ] Certify source revision recorded
- [ ] Executable hash recorded
- [ ] Test identities defined

## Discovery

- [ ] Current domain identified
- [ ] Domain Controller identified
- [ ] Enterprise CAs enumerated
- [ ] CA hostnames recorded
- [ ] Enrollment services identified
- [ ] Web enrollment checked where relevant

## Templates

- [ ] Published templates enumerated
- [ ] Enrollment permissions reviewed
- [ ] Template ACLs reviewed
- [ ] Subject configuration reviewed
- [ ] EKUs reviewed
- [ ] Manager approval reviewed
- [ ] Authorized signatures reviewed
- [ ] Validity periods reviewed

## Validation

- [ ] Candidate findings manually reviewed
- [ ] Current-user permissions confirmed
- [ ] Required preconditions confirmed
- [ ] Certificate request limited to approved test case
- [ ] Certificate capability validated
- [ ] Authentication impact separately validated
- [ ] Modern certificate mapping considered

## Evidence

- [ ] CA information captured
- [ ] Template information captured
- [ ] Permissions captured
- [ ] Certificate request recorded
- [ ] Serial number recorded where applicable
- [ ] Security impact documented
- [ ] Sensitive private-key material excluded from report

## Detection

- [ ] CA audit telemetry reviewed where available
- [ ] Directory changes reviewed where relevant
- [ ] Certificate issuance events reviewed
- [ ] Endpoint telemetry reviewed

## Cleanup

- [ ] Temporary output removed
- [ ] Test certificates reviewed
- [ ] Private keys removed
- [ ] Temporary PFX/PEM files removed
- [ ] No template modifications left behind
- [ ] No CA configuration changes left behind
- [ ] Cleanup documented

---

# Related Notes

- [Rubeus](rubeus.md)
- [Mimikatz](mimikatz.md)
- [Impacket](impacket.md)
- [NetExec](netexec.md)
- [BloodHound](bloodhound.md)
- [Active Directory](../active-directory/index.md)
- [Windows](../windows/index.md)

Planned related material:

```text
tools/certipy.md
active-directory/ad-cs/
active-directory/ntlm-relay.md
cheatsheets/certipy.md
```

---

# References

- [Certify - Official GhostPack Repository](https://github.com/GhostPack/Certify){ target="_blank" rel="noopener noreferrer" }
- [Certify README](https://github.com/GhostPack/Certify/blob/main/README.md){ target="_blank" rel="noopener noreferrer" }
- [SpecterOps - Certified Pre-Owned](https://specterops.io/blog/2021/06/17/certified-pre-owned/){ target="_blank" rel="noopener noreferrer" }
- [Certified Pre-Owned Whitepaper](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Active Directory Certificate Services Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Steal Authentication Certificate](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }
