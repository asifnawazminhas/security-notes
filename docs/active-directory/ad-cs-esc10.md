# AD CS ESC10 - Weak Certificate Mapping

ESC10 describes Active Directory Certificate Services (AD CS) attack paths caused by weak certificate mapping on domain controllers.

Certificate mapping is the process Windows uses to determine:

```text
Which Active Directory Account
        |
        v
Belongs to This Certificate?
```

A certificate may contain several identity-related values:

```text
Subject
Subject Alternative Name
UPN
DNS Name
Issuer
Serial Number
SID Security Extension
```

The Key Distribution Center (KDC) must map the certificate presented during certificate-based authentication to an Active Directory security principal.

A secure model is:

```text
Certificate
     |
     v
Strong Identity Binding
     |
     v
Active Directory Account
```

ESC10 becomes relevant when domain controllers permit weak mappings that rely on identity information which may be changed, duplicated, spoofed, or otherwise insufficiently bound to the original certificate requester.

Historically, ESC10 was strongly associated with registry settings such as:

```text
StrongCertificateBindingEnforcement
```

and:

```text
CertificateMappingMethods
```

However, Microsoft's certificate-based authentication hardening introduced through KB5014754 significantly changed this area.

In a current, fully patched Active Directory environment, legacy ESC10 techniques must not be assumed to work.

The central assessment question is:

```text
Can a certificate be mapped to a different
Active Directory account because the
environment accepts an insufficiently
strong certificate mapping?
```

!!! warning "Authorised testing only"
    Certificate mapping tests can affect authentication and identity relationships across the domain. Begin with read-only inspection of certificate templates, domain-controller configuration, IIS/Schannel configuration where relevant, and explicit mappings. Do not weaken certificate mapping, modify production identities, or change domain-controller registry settings merely to demonstrate ESC10. Use dedicated test accounts when active validation is explicitly authorised.

---

# Certificate Mapping

Certificate authentication requires Windows to answer:

```text
Who owns this certificate?
```

Conceptually:

```text
Certificate
     |
     v
Identity Information
     |
     v
Certificate Mapping
     |
     v
Active Directory Object
```

If the mapping mechanism is strong:

```text
Certificate A
     |
     v
Account A
```

should not become:

```text
Certificate A
     |
     v
Account B
```

simply because an attacker manipulates a weak name-based identifier.

---

# Why Certificate Mapping Exists

A certificate does not inherently contain an Active Directory object reference that every authentication service automatically understands.

The certificate may instead contain information such as:

```text
UPN
DNS Name
Subject
Issuer
Serial Number
SID
```

Windows must determine how those values correspond to an account.

---

# Strong vs Weak Mapping

The most important ESC10 concept is:

```text
Strong Mapping
```

versus:

```text
Weak Mapping
```

A simplified model is:

```text
Certificate Mapping
      |
      +--> Strong Mapping
      |
      +--> Weak Mapping
```

---

# Weak Mapping

Weak mappings historically included mappings based primarily on certificate names.

Examples include certificate identities derived from:

```text
Subject
UPN
Email
DNS Name
```

depending on authentication mechanism and configuration.

The problem is that names may be:

```text
Changed
Reused
Duplicated
Manipulated
```

more easily than cryptographically or administratively strong identifiers.

---

# Strong Mapping

Strong mappings provide a stronger relationship between:

```text
Certificate
```

and:

```text
Specific Security Principal
```

Examples include mappings involving security identifiers or strong explicit certificate mappings.

Conceptually:

```text
Certificate
     |
     v
Strong Identifier
     |
     v
Specific AD Object
```

---

# ESC10 Historical Definition

ESC10 historically covered two important weak-mapping configurations.

These were commonly separated into:

```text
ESC10 Case 1
```

and:

```text
ESC10 Case 2
```

The two cases involve different Windows components.

---

# ESC10 Case 1

The first historical ESC10 condition involved:

```text
StrongCertificateBindingEnforcement
```

on domain controllers.

Historically, weak settings could permit certificate authentication using mappings that were not sufficiently bound to the original account.

Conceptually:

```text
Certificate
     |
     v
KDC
     |
     v
Weak Mapping Accepted
     |
     v
Different Account
```

---

# StrongCertificateBindingEnforcement

The relevant historical registry location is:

```text
HKLM\SYSTEM\CurrentControlSet\Services\Kdc
```

with the value:

```text
StrongCertificateBindingEnforcement
```

This setting was introduced as part of Microsoft's KB5014754 certificate-authentication hardening.

---

# Historical Modes

Historically the setting supported modes corresponding approximately to:

```text
Disabled
Compatibility
Full Enforcement
```

Older ESC10 guidance frequently focused on environments where strong certificate binding was disabled or not fully enforced.

---

# Current 2026 Context

This historical configuration must be interpreted carefully today.

Microsoft's KB5014754 rollout moved domain controllers toward:

```text
Full Enforcement
```

beginning with the February 2025 security update.

Microsoft also documented that the ability to return to Compatibility mode through the registry setting ended with the:

```text
September 9, 2025
```

Windows security update.

Therefore, on a normally patched domain controller in 2026:

```text
StrongCertificateBindingEnforcement
```

should not be treated as a supported mechanism for returning to the historical weak-mapping state.

---

# Why Old ESC10 Guides Can Mislead

Older write-ups may instruct testers to check:

```text
StrongCertificateBindingEnforcement = 0
```

and immediately classify the domain as vulnerable.

That historical interpretation should not be blindly applied to a current environment.

Instead determine:

```text
Windows Patch State
        |
        v
Current Enforcement Behaviour
        |
        v
Available Certificate Mapping
```

---

# Do Not Change the Registry

Never change:

```text
StrongCertificateBindingEnforcement
```

on a production domain controller merely to recreate a historical ESC10 attack.

That would deliberately weaken domain authentication.

---

# ESC10 Case 2

The second historical ESC10 condition concerns Schannel certificate mapping.

The relevant configuration is commonly associated with:

```text
CertificateMappingMethods
```

under:

```text
HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL
```

---

# Schannel

Schannel is the Windows Secure Channel security package used for TLS.

Certificate authentication through Schannel can appear in services such as:

```text
LDAPS
IIS
Remote Access
Other TLS Client-Certificate Services
```

depending on environment configuration.

---

# CertificateMappingMethods

Historically:

```text
CertificateMappingMethods
```

controls which certificate mapping methods Schannel can use.

This is distinct from:

```text
StrongCertificateBindingEnforcement
```

used in the KDC certificate-authentication context.

Therefore:

```text
KDC Mapping
```

and:

```text
Schannel Mapping
```

must be assessed separately.

---

# ESC10 Mapping Surfaces

A useful model is:

```text
Certificate Authentication
        |
        +--> Kerberos / PKINIT
        |       |
        |       v
        |      KDC
        |
        +--> TLS Client Authentication
                |
                v
             Schannel
```

ESC10 analysis should identify which authentication surface is actually involved.

---

# Kerberos PKINIT

Kerberos can use certificates during:

```text
PKINIT
```

to obtain a Ticket Granting Ticket.

Conceptually:

```text
Certificate
     |
     v
KDC
     |
     v
Certificate Mapping
     |
     v
Account
     |
     v
TGT
```

---

# Schannel Authentication

Schannel can authenticate a client certificate to a Windows service.

Conceptually:

```text
Certificate
     |
     v
TLS
     |
     v
Schannel
     |
     v
Certificate Mapping
     |
     v
Windows Account
```

---

# ESC10 Is Not Only AD CS

This is an important distinction.

The vulnerable component in ESC10 is primarily:

```text
Certificate Mapping Configuration
```

rather than necessarily:

```text
Certificate Authority Configuration
```

AD CS provides the certificates, but the weakness occurs when Windows maps them insecurely.

---

# ESC10 and ESC9

ESC9 disables the SID security extension at the template level.

Conceptually:

```text
ESC9
 |
 v
Certificate Without SID
```

ESC10 asks:

```text
Can Windows Still Accept a Weak Mapping?
```

The combination historically created important attack paths.

---

# ESC9 + ESC10

A simplified relationship is:

```text
ESC9 Template
      |
      v
Certificate Without SID
      |
      v
ESC10 Weak Mapping
      |
      v
Different AD Account
```

In a modern environment, verify whether Full Enforcement blocks the mapping.

---

# ESC10 and ESC16

ESC16 can suppress the SID security extension at the CA level.

Therefore:

```text
ESC16
   |
   v
Certificate Without SID
   |
   v
ESC10 Analysis
```

may become relevant.

---

# ESC10 and ESC6

ESC6 concerns requester-controlled SAN information.

Historically:

```text
Requester-Controlled SAN
        +
Weak Certificate Mapping
```

could produce dangerous identity-mapping scenarios.

Modern strong mapping must still be considered.

---

# ESC10 and ESC1

ESC1 allows an enrollee to supply identity information under vulnerable template conditions.

Conceptually:

```text
ESC1
 |
 v
Attacker-Controlled Certificate Identity
 |
 v
Certificate Mapping
```

ESC10 may influence whether that certificate identity maps successfully.

---

# ESC10 and ESC14

ESC14 concerns weak explicit certificate mappings through:

```text
altSecurityIdentities
```

ESC10 primarily concerns weak mapping behaviour configured at the authentication infrastructure level.

They should be assessed together but reported according to the actual root cause.

---

# ESC10 Preconditions

A meaningful ESC10 path generally requires:

```text
Certificate
      +
Authentication Capability
      +
Weak Mapping Configuration
      +
Manipulable / Reusable Identity
      +
Reachable Target Account
      =
Potential ESC10
```

---

# Certificate Requirement

The attacker first needs a usable certificate.

That certificate might originate from:

```text
Legitimate Enrollment
ESC1
ESC2
ESC3
ESC6
ESC8
ESC9
ESC16
Stolen Certificate
```

ESC10 determines how that certificate maps to an account.

---

# Authentication Capability

The certificate must be useful for the target authentication mechanism.

Relevant EKUs can include:

```text
Client Authentication
1.3.6.1.5.5.7.3.2

Smart Card Logon
1.3.6.1.4.1.311.20.2.2

PKINIT Client Authentication
1.3.6.1.5.2.3.4
```

The exact requirements depend on the authentication path.

---

# Enumerate Domain Controllers

From Windows:

```powershell
Get-ADDomainController -Filter * |
    Select-Object HostName,IPv4Address,OperatingSystem,OperatingSystemVersion
```

This helps establish:

```text
Domain Controllers
Windows Versions
Patch Context
```

---

# Patch State Matters

For modern ESC10 assessment, record:

```text
Operating System
Build
Patch Level
Certificate Mapping Enforcement
```

Do not infer mapping behaviour solely from the OS marketing version.

---

# Check KDC Configuration

On an authorised domain controller:

```powershell
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Kdc' -Name StrongCertificateBindingEnforcement -ErrorAction SilentlyContinue
```

Interpret the result in the context of:

```text
Current Windows Patching
```

and Microsoft's current KB5014754 enforcement behaviour.

---

# Registry Value Missing

Do not automatically interpret:

```text
Value Not Present
```

as:

```text
Vulnerable
```

Default behaviour has changed during Microsoft's multi-year rollout.

The effective behaviour of the patched domain controller matters.

---

# Query with reg.exe

An alternative is:

```cmd
reg query HKLM\SYSTEM\CurrentControlSet\Services\Kdc /v StrongCertificateBindingEnforcement
```

Again, absence of the value is not itself evidence of ESC10.

---

# Check Schannel Mapping

On an authorised target:

```powershell
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL' -Name CertificateMappingMethods -ErrorAction SilentlyContinue
```

or:

```cmd
reg query HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL /v CertificateMappingMethods
```

---

# CertificateMappingMethods Is a Bitmask

The Schannel configuration is a bitmask.

Historically documented mapping methods include categories such as:

```text
Subject / Issuer
Issuer
UPN
S4U-Based Mapping
```

Exact supported behaviour should be checked against the current Microsoft documentation for the Windows version being assessed.

Do not infer vulnerability from the decimal value without decoding the enabled methods.

---

# Inventory Schannel Services

Identify where certificate-based TLS authentication is actually used.

Potential examples include:

```text
LDAPS
IIS
VPN
Remote Access
Custom Windows Services
```

A weak Schannel configuration has limited practical impact if no relevant service accepts client certificates.

---

# LDAPS

LDAP over TLS commonly uses:

```text
636/tcp
```

Discover:

```bash
nmap -Pn -p636 dc01.corp.example
```

This establishes service availability, not certificate mapping vulnerability.

---

# Test TLS

For basic TLS inspection:

```bash
openssl s_client -connect dc01.corp.example:636 -showcerts
```

This inspects the server-side TLS service.

It does not prove that client certificate mapping is weak.

---

# Explicit Certificate Mapping

Active Directory accounts can contain:

```text
altSecurityIdentities
```

which can explicitly associate certificates with accounts.

Enumerate the attribute:

```powershell
Get-ADUser -Filter * -Properties altSecurityIdentities |
    Where-Object { $_.altSecurityIdentities } |
    Select-Object SamAccountName,altSecurityIdentities
```

---

# Computer Explicit Mappings

Also review computer objects:

```powershell
Get-ADComputer -Filter * -Properties altSecurityIdentities |
    Where-Object { $_.altSecurityIdentities } |
    Select-Object Name,SamAccountName,altSecurityIdentities
```

---

# Why altSecurityIdentities Matters

An explicit mapping can override assumptions based solely on certificate names.

Conceptually:

```text
Certificate
     |
     v
Explicit Mapping
     |
     v
Account
```

This may create either:

```text
Strong Mapping
```

or:

```text
Weak Mapping
```

depending on the mapping form.

ESC14 covers weak explicit mappings in more detail.

---

# Certipy Enumeration

Certipy can assist with AD CS and certificate mapping analysis.

Start with:

```bash
certipy --version
```

Then:

```bash
certipy find -h
```

A typical read-only enumeration command is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

---

# Certipy and ESC10

Certipy may identify ESC10-related conditions when it can determine relevant registry or mapping information.

However, tool output should be treated as:

```text
Lead
```

rather than:

```text
Final Proof
```

because:

```text
Patch State
Effective Enforcement
Certificate Type
Authentication Surface
```

all matter.

---

# Remote Registry Limitations

Remote registry enumeration may fail because:

```text
Remote Registry Disabled
Firewall
Permissions
Service State
RPC Restrictions
```

Failure to read the setting does not imply that the system is secure or vulnerable.

---

# BloodHound

BloodHound can help identify certificate attack paths around:

```text
Certificate Templates
Enrollment Rights
Certificate Authorities
Account Control
```

See:

[BloodHound](bloodhound.md)

However, effective certificate mapping behaviour should still be validated directly.

---

# Identity Attribute Control

Historical ESC10 exploitation can depend on the ability to manipulate identity attributes.

Potentially relevant attributes include:

```text
userPrincipalName
dNSHostName
altSecurityIdentities
```

depending on the specific mapping path.

---

# UPN

A user's:

```text
userPrincipalName
```

is commonly represented as:

```text
alice@corp.example
```

Historically, weak UPN mapping created opportunities where certificate identity could be redirected toward another user.

---

# dNSHostName

Computer certificate mapping may involve:

```text
dNSHostName
```

in some certificate and authentication scenarios.

Treat changes to computer identity attributes as security-sensitive.

---

# Historical User Mapping Model

A historical weak-mapping model is:

```text
Attacker Controls User A
        |
        v
Manipulates Identity Attribute
        |
        v
Requests Certificate
        |
        v
Certificate Contains Target Identity
        |
        v
Restores Attribute
        |
        v
Weak Mapping
        |
        v
User B
```

Current Full Enforcement may block this path.

---

# Historical Computer Mapping Model

Conceptually:

```text
Controlled Computer A
        |
        v
Manipulated Computer Identity
        |
        v
Certificate
        |
        v
Weak Mapping
        |
        v
Computer B
```

Again, do not assume this works against current patched systems.

---

# Safe Validation

The preferred approach is:

```text
Read Configuration
       |
       v
Determine Mapping Method
       |
       v
Assess Certificate Source
       |
       v
Assess Identity Control
       |
       v
Determine Whether Active Proof Is Needed
```

Often this is sufficient.

---

# Dedicated Test Accounts

If active validation is necessary, use:

```text
ESC10-Requester
ESC10-Target
```

or equivalent dedicated accounts.

Avoid:

```text
Administrator
Domain Admin
Enterprise Admin
krbtgt
Production Service Accounts
Domain Controllers
```

---

# Record Original Attributes

Before an approved identity modification:

```powershell
Get-ADUser -Identity 'ESC10-Requester' -Properties userPrincipalName,altSecurityIdentities |
    Select-Object SamAccountName,userPrincipalName,altSecurityIdentities
```

Save the values as evidence.

---

# Do Not Weaken Mapping for Testing

Do not change:

```text
StrongCertificateBindingEnforcement
CertificateMappingMethods
```

to create an exploitable condition.

The assessment should test:

```text
Existing Security Posture
```

not manufacture a vulnerability.

---

# Certificate Inspection

For any test certificate record:

```text
Subject
Issuer
Serial Number
Thumbprint
SAN
UPN
DNS Name
EKUs
SID Security Extension
Validity
```

---

# Windows Inspection

```cmd
certutil -dump esc10-test.cer
```

---

# OpenSSL

```bash
openssl x509 -in esc10-test.pem -text -noout
```

For DER:

```bash
openssl x509 -in esc10-test.cer -inform DER -text -noout
```

---

# Certipy Authentication

If certificate authentication is explicitly required:

```bash
certipy auth -h
```

Verify the installed syntax before testing.

Use only the approved test certificate and identity.

---

# Successful Authentication

If a certificate issued to:

```text
ESC10-Requester
```

authenticates as:

```text
ESC10-Target
```

under the environment's existing mapping configuration, the cross-account mapping impact has been demonstrated.

Stop there unless further validation is explicitly required.

---

# Failed Authentication

A failed authentication can be equally informative.

For example:

```text
Certificate
     |
     v
No Acceptable Strong Mapping
     |
     v
KDC Rejects Authentication
```

This may demonstrate that current Full Enforcement mitigates the historical attack path.

---

# Do Not Bypass the Mitigation

If authentication fails because strong mapping is enforced:

```text
Stop
```

Do not weaken the domain controller to continue the attack.

Document:

```text
Historical ESC10 Condition Not Exploitable
Under Current Enforcement
```

where appropriate.

---

# Schannel Validation

If the issue concerns:

```text
CertificateMappingMethods
```

test only the specific service that relies on Schannel client-certificate authentication.

Do not extrapolate a result from:

```text
IIS
```

to:

```text
LDAP
```

or vice versa without evidence.

---

# Mapping Method Matters

A complete finding should identify:

```text
Authentication Service
Mapping Method
Certificate Identity
Mapped Account
```

For example:

```text
Service:
LDAPS

Certificate:
ESC10-Test

Mapping:
UPN

Mapped Account:
ESC10-Target
```

This is much stronger evidence than simply reporting a registry value.

---

# Detection

ESC10 detection should cover:

```text
Mapping Configuration Changes
Identity Attribute Changes
Certificate Enrollment
Explicit Mapping Changes
Certificate Authentication
```

---

# Monitor KDC Configuration

Monitor unexpected changes under:

```text
HKLM\SYSTEM\CurrentControlSet\Services\Kdc
```

particularly historical certificate-binding configuration.

---

# Monitor Schannel Configuration

Monitor:

```text
HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL
```

for changes to certificate mapping configuration.

---

# Registry Monitoring

EDR or configuration-management tooling can detect unexpected changes to:

```text
StrongCertificateBindingEnforcement
CertificateMappingMethods
```

where those values are relevant to the Windows version.

---

# Monitor UPN Changes

Unexpected modifications to:

```text
userPrincipalName
```

should be monitored.

A suspicious sequence can be:

```text
UPN Changed
    |
    v
Certificate Requested
    |
    v
UPN Restored
```

---

# Monitor Computer Identity Changes

Monitor unusual changes to:

```text
dNSHostName
```

and other computer identity attributes.

These attributes should not change frequently in most environments.

---

# Monitor Explicit Mappings

Monitor:

```text
altSecurityIdentities
```

for:

```text
Addition
Modification
Deletion
```

especially on privileged accounts.

---

# Event 5136

Where Directory Service Changes auditing is enabled:

```text
5136
```

can provide visibility into modifications to Active Directory attributes.

Relevant attributes can include:

```text
userPrincipalName
dNSHostName
altSecurityIdentities
```

---

# Event 4738

User account modifications may also produce:

```text
4738
```

depending on the change and audit configuration.

Correlate with certificate issuance.

---

# Certificate Request Monitoring

Where Certificate Services auditing is configured:

```text
4886
```

can indicate receipt of a certificate request.

---

# Certificate Issuance

```text
4887
```

can indicate successful certificate issuance.

---

# Kerberos Authentication

Certificate-based Kerberos authentication can result in:

```text
4768
```

TGT-request telemetry.

Correlate:

```text
Identity Attribute Change
        |
        v
Certificate Request
        |
        v
Certificate Issuance
        |
        v
4768
```

---

# Suspicious Timing

One of the strongest detection patterns is:

```text
Identity Changed
      |
      v
Certificate Issued
      |
      v
Identity Restored
      |
      v
Certificate Authentication
```

within a short period.

---

# Monitor Domain Controllers

Certificate mapping is an identity-control-plane function.

Changes to domain-controller certificate authentication configuration should therefore receive high-priority monitoring.

---

# Hardening ESC10

The primary objective is:

```text
Use Strong Certificate Mapping
```

---

# Maintain Full Enforcement

Keep domain controllers:

```text
Fully Patched
```

and operating with Microsoft's current strong certificate-binding enforcement.

Do not restore obsolete compatibility behaviour.

---

# Do Not Depend on Deprecated Compatibility Modes

Legacy applications should be migrated to supported strong certificate mappings rather than weakening domain-wide authentication.

---

# Review Schannel Mapping

Identify services that use:

```text
Schannel Client Certificate Authentication
```

and verify that weak mapping methods are not unnecessarily enabled.

---

# Review CertificateMappingMethods

Document the effective:

```text
CertificateMappingMethods
```

configuration for systems that rely on Schannel certificate authentication.

Compare against current Microsoft guidance and application requirements.

---

# Use Strong Explicit Mappings

Where explicit mappings are required, prefer strong mapping forms supported by Microsoft.

Avoid weak mappings based only on mutable certificate names.

---

# Review altSecurityIdentities

Audit:

```text
altSecurityIdentities
```

across:

```text
Privileged Users
Service Accounts
Administrators
Computer Accounts
Certificate-Based Accounts
```

---

# Protect Mapping Attributes

Restrict who can modify:

```text
userPrincipalName
dNSHostName
altSecurityIdentities
```

and other identity-related attributes.

---

# Review ACLs

A user may not directly control a privileged account but may have an ACL path allowing modification of a mapping-related attribute.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# Review Group Delegation

Helpdesk or identity-management systems may legitimately have permissions to modify:

```text
UPN
```

or other identity attributes.

Determine whether those permissions can interact with certificate enrollment.

---

# Review Certificate Templates

Strong mapping does not replace secure template configuration.

Continue to review:

```text
ESC1
ESC2
ESC3
ESC4
ESC6
ESC9
ESC15
ESC16
```

where relevant.

---

# Review ESC9

If an authentication template has:

```text
NO_SECURITY_EXTENSION
```

review it immediately.

See:

[AD CS ESC9](ad-cs-esc9.md)

---

# Review ESC16

If certificates across multiple templates unexpectedly lack the SID security extension, investigate CA-wide configuration.

---

# Protect Domain Controllers

Domain controllers should have:

```text
Current Security Updates
Restricted Administrative Access
Configuration Monitoring
EDR
Secure Registry ACLs
Administrative Tiering
```

---

# Baseline Certificate Mapping

Maintain a baseline containing:

```text
Domain Controller
OS Build
Patch Level
Strong Mapping State
Schannel Mapping State
Explicit Mapping Usage
Certificate Authentication Services
```

---

# Incident Response

If weak certificate mapping abuse is suspected:

```text
Identify Certificate
       |
       v
Identify Mapping Method
       |
       v
Identify Mapped Account
       |
       v
Review Identity Changes
       |
       v
Review Certificate Issuance
       |
       v
Review Authentication
       |
       v
Revoke Certificate
       |
       v
Correct Mapping
```

---

# Identify Certificate

Record:

```text
Serial Number
Thumbprint
Issuer
Subject
SAN
UPN
DNS Name
SID Security Extension
Template
Validity
```

---

# Determine Mapping

Determine exactly why Windows accepted the certificate.

Ask:

```text
SID Mapping?
Explicit Mapping?
UPN Mapping?
Issuer / Subject Mapping?
Schannel Mapping?
Other Mapping?
```

---

# Identify Target Account

Record:

```text
SamAccountName
SID
UPN
Distinguished Name
Account Type
Privileges
```

---

# Review Attribute History

Investigate changes to:

```text
userPrincipalName
dNSHostName
altSecurityIdentities
```

around certificate issuance.

---

# Review Replication Metadata

Active Directory replication metadata can help determine:

```text
Attribute
Version
Originating DC
Modification Time
```

for suspicious account changes.

This can help reconstruct temporary identity manipulation.

---

# Review Certificate Requests

Record:

```text
Request ID
Requester
Template
Subject
SAN
Submission Time
Issue Time
```

---

# Review Authentication

Determine whether the certificate was used for:

```text
Kerberos PKINIT
LDAPS
IIS
VPN
Other TLS Client Authentication
```

---

# Revoke Malicious Certificates

If a malicious certificate exists:

```text
Revoke
   |
   v
Publish Updated CRL
   |
   v
Verify Revocation Distribution
```

---

# Correct Explicit Mapping

If a malicious:

```text
altSecurityIdentities
```

mapping was created:

```text
Remove Mapping
```

and determine who had permission to create it.

---

# Correct Mapping Configuration

If weak mapping is still enabled on a supported system:

```text
Move to Supported Strong Mapping
```

following current Microsoft guidance.

---

# Investigate Why Weak Mapping Existed

Common causes include:

```text
Legacy Smart Card Deployment
Old PKI Configuration
Application Compatibility
Migration
Manual Registry Changes
Legacy IIS Authentication
Third-Party Certificate Integration
```

Fix the underlying dependency rather than simply changing a registry value without testing.

---

# Reporting ESC10

Avoid reporting only:

```text
ESC10
```

Prefer a title describing the actual mapping weakness.

Examples:

```text
Weak Certificate Mapping Permits Cross-Account Authentication
```

or:

```text
Schannel Accepts Weak Certificate-to-Account Mapping
```

or:

```text
Legacy Certificate Mapping Configuration Weakens Active Directory Authentication
```

---

# Example Finding - Historical Configuration Present

```text
Finding:
Legacy Certificate Mapping Configuration Identified

Affected Systems:
dc01.corp.example
dc02.corp.example

Description:
Certificate-based authentication configuration associated with
historical weak certificate mapping was identified on the domain
controllers.

Microsoft has significantly changed certificate mapping behaviour
through the KB5014754 rollout, including Full Enforcement and the
removal of the supported Compatibility-mode fallback.

The registry configuration alone therefore does not establish that
cross-account certificate authentication is currently possible.

Impact:
If the effective domain-controller configuration still accepts weak
certificate mappings, a certificate containing manipulable identity
information may potentially map to an unintended Active Directory
security principal.

The practical impact depends on the current Windows patch state,
effective certificate mapping behaviour, available certificates, and
control over identity attributes.

Recommendation:
Confirm that all domain controllers are fully patched and operating
with Microsoft's current Full Enforcement behaviour.

Remove obsolete certificate-mapping compatibility configuration where
appropriate.

Review certificate templates that omit strong identity information
and audit explicit certificate mappings.
```

---

# Example Finding - Exploitable Mapping Demonstrated

```text
Finding:
Weak Certificate Mapping Permits Cross-Account Authentication

Affected Service:
<service>

Affected System:
<hostname>

Requester:
CORP\ESC10-Requester

Mapped Identity:
CORP\ESC10-Target

Description:
The affected certificate-authentication service accepts a weak
certificate mapping that does not sufficiently bind the presented
certificate to the account for which it was issued.

During controlled validation, two dedicated test identities were
used.

A certificate associated with the requester test identity was
accepted as the separate target test identity because of the
effective certificate mapping configuration.

No privileged production identity was used during validation.

Impact:
An attacker who can obtain a suitable certificate and manipulate the
relevant identity or mapping information may be able to authenticate
as another Active Directory account.

The resulting impact depends on the privileges of the mapped account.

Recommendation:
Configure the affected authentication service to use Microsoft's
supported strong certificate mapping mechanisms.

Maintain current Windows security updates and Full Enforcement on
domain controllers.

Review explicit certificate mappings and restrict modification of
identity attributes that influence certificate mapping.
```

---

# Severity Assessment

ESC10 severity depends on:

```text
Weak Mapping
     +
Certificate Source
     +
Authentication EKU
     +
Identity Control
     +
Target Account
     +
Reachable Service
     =
Severity
```

---

# Critical Example

```text
Attacker Certificate
       |
       v
Weak Mapping
       |
       v
Domain Admin
       |
       v
Kerberos Authentication
```

If demonstrated under the environment's existing configuration, this can represent critical impact.

---

# Reduced-Risk Example

```text
Historical Registry Value
       |
       v
Fully Patched DC
       |
       v
Full Enforcement
       |
       v
Weak Mapping Rejected
```

This should not be described as demonstrated domain compromise.

---

# Evidence Checklist

For ESC10 record:

```text
Domain Controller
OS Version
OS Build
Patch State
Authentication Service
KDC Mapping Configuration
Schannel Mapping Configuration
CertificateMappingMethods
Strong Mapping Behaviour
Certificate Source
Certificate Template
Certificate Subject
Certificate SAN
Certificate UPN
Certificate SID Extension
Certificate Serial Number
Certificate Thumbprint
Explicit Mapping
altSecurityIdentities
Original Identity Attributes
Modified Identity Attributes
Mapped Account
Authentication Result
Event Evidence
Cleanup Result
```

---

# ESC10 Assessment Checklist

## Discovery

- [ ] Identify domain controllers
- [ ] Record Windows versions
- [ ] Record patch state
- [ ] Identify certificate-authentication services
- [ ] Identify PKINIT usage
- [ ] Identify Schannel usage
- [ ] Identify LDAPS
- [ ] Identify IIS client-certificate authentication
- [ ] Identify VPN / remote-access certificate authentication

## KDC Mapping

- [ ] Review current KB5014754 behaviour
- [ ] Determine effective Full Enforcement state
- [ ] Review historical `StrongCertificateBindingEnforcement`
- [ ] Do not infer vulnerability from registry presence alone
- [ ] Do not infer vulnerability from missing registry value
- [ ] Do not weaken mapping for testing

## Schannel Mapping

- [ ] Review `CertificateMappingMethods`
- [ ] Decode enabled mapping methods
- [ ] Identify services using Schannel
- [ ] Determine whether client certificates are accepted
- [ ] Determine effective mapping method
- [ ] Compare against current Microsoft guidance

## Explicit Mapping

- [ ] Enumerate `altSecurityIdentities`
- [ ] Review privileged users
- [ ] Review service accounts
- [ ] Review computer accounts
- [ ] Determine whether mappings are strong or weak
- [ ] Review who can modify mappings
- [ ] Evaluate ESC14

## Related AD CS Conditions

- [ ] Review ESC1
- [ ] Review ESC4
- [ ] Review ESC6
- [ ] Review ESC9
- [ ] Review ESC14
- [ ] Review ESC16
- [ ] Determine certificate source
- [ ] Determine SID extension state

## Identity Control

- [ ] Review `userPrincipalName`
- [ ] Review `dNSHostName`
- [ ] Review `altSecurityIdentities`
- [ ] Review ACLs over affected identities
- [ ] Review delegated identity-management permissions
- [ ] Review helpdesk permissions
- [ ] Review service-account management

## Tooling

- [ ] Verify Certipy version
- [ ] Review `certipy find -h`
- [ ] Review `certipy auth -h`
- [ ] Enumerate certificate configuration
- [ ] Review BloodHound attack paths
- [ ] Use native PowerShell for registry/configuration validation
- [ ] Use `certutil` for certificate inspection
- [ ] Use OpenSSL where appropriate
- [ ] Manually validate automated ESC10 findings

## Validation

- [ ] Prefer read-only validation
- [ ] Determine whether active proof is necessary
- [ ] Obtain explicit approval
- [ ] Use dedicated requester account
- [ ] Use dedicated target account
- [ ] Record original identity attributes
- [ ] Avoid privileged production accounts
- [ ] Do not modify DC mapping configuration
- [ ] Do not weaken Full Enforcement
- [ ] Request minimum test certificate
- [ ] Restore temporary identity changes
- [ ] Verify restoration
- [ ] Test only approved authentication service
- [ ] Stop after sufficient proof
- [ ] Revoke test certificate where required
- [ ] Delete private-key material

## Detection

- [ ] Monitor KDC configuration
- [ ] Monitor Schannel configuration
- [ ] Monitor certificate mapping registry changes
- [ ] Monitor UPN changes
- [ ] Monitor `dNSHostName`
- [ ] Monitor `altSecurityIdentities`
- [ ] Monitor event 5136
- [ ] Monitor event 4738 where relevant
- [ ] Monitor certificate requests
- [ ] Monitor event 4886 where configured
- [ ] Monitor certificate issuance
- [ ] Monitor event 4887 where configured
- [ ] Monitor certificate authentication
- [ ] Correlate issuance with 4768
- [ ] Detect change-request-restore sequences

## Hardening

- [ ] Maintain current Windows updates
- [ ] Maintain Full Enforcement
- [ ] Remove obsolete compatibility configuration
- [ ] Review Schannel mapping methods
- [ ] Eliminate weak mappings where possible
- [ ] Use strong explicit mappings
- [ ] Audit `altSecurityIdentities`
- [ ] Protect identity attributes
- [ ] Review delegated ACLs
- [ ] Review ESC9
- [ ] Review ESC14
- [ ] Review ESC16
- [ ] Harden certificate templates
- [ ] Protect domain controllers
- [ ] Baseline certificate mapping

## Incident Response

- [ ] Identify suspicious certificate
- [ ] Determine certificate source
- [ ] Determine mapping method
- [ ] Identify mapped account
- [ ] Review identity attribute changes
- [ ] Review explicit mapping changes
- [ ] Review replication metadata
- [ ] Review certificate requests
- [ ] Review certificate issuance
- [ ] Review certificate authentication
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Remove malicious explicit mappings
- [ ] Restore identity attributes
- [ ] Correct weak mapping
- [ ] Investigate root cause

## Cleanup

- [ ] Restore test identity attributes
- [ ] Verify restoration
- [ ] Remove temporary explicit mappings
- [ ] Revoke test certificate where required
- [ ] Remove test certificate
- [ ] Delete test PFX
- [ ] Delete private-key material
- [ ] Verify DC configuration unchanged
- [ ] Verify Schannel configuration unchanged
- [ ] Record cleanup evidence

---

# ESC10 Testing Model

The secure model is:

```text
Certificate
     |
     v
Strong Mapping
     |
     v
Original AD Account
```

The ESC10 model is:

```text
Certificate
     |
     v
Weak Mapping
     |
     v
Different AD Account
```

The KDC model is:

```text
Certificate
     |
     v
PKINIT
     |
     v
KDC
     |
     v
Certificate Mapping
     |
     v
Account
```

The Schannel model is:

```text
Certificate
     |
     v
TLS
     |
     v
Schannel
     |
     v
Certificate Mapping
     |
     v
Account
```

The historical ESC9 + ESC10 model is:

```text
ESC9
 |
 v
Certificate Without SID
 |
 v
ESC10 Weak Mapping
 |
 v
Target Account
```

The ESC16 + ESC10 model is:

```text
ESC16
 |
 v
CA-Wide SID Extension Suppression
 |
 v
Certificate Without SID
 |
 v
ESC10 Mapping Analysis
```

The explicit mapping model is:

```text
Certificate
     |
     v
altSecurityIdentities
     |
     v
Account
```

The modern enforcement model is:

```text
Certificate
     |
     v
KDC
     |
     v
Strong Mapping Available?
     |
     +--> Yes -> Authenticate According to Mapping
     |
     +--> No
            |
            v
       Reject Authentication
```

The safe-testing model is:

```text
Enumerate
   |
   v
Identify Mapping Configuration
   |
   v
Determine Patch State
   |
   v
Identify Certificate Source
   |
   v
Identify Identity Control
   |
   v
Read-Only Evidence Enough?
   |
   +--> Yes -> Report
   |
   +--> No
           |
           v
       Dedicated Test Accounts
           |
           v
       Minimum Approved Change
           |
           v
       Certificate
           |
           v
       Test Existing Mapping
           |
           v
       Restore
           |
           v
       Revoke / Cleanup
```

The detection model is:

```text
Identity / Mapping Change
        |
        v
Certificate Request
        |
        v
Certificate Issued
        |
        v
Identity Restored
        |
        v
Certificate Authentication
```

The defensive model is:

```text
Current Patching
       +
Full Enforcement
       +
Strong Mapping
       +
Protected Identity Attributes
       +
Secure Templates
       +
Mapping Monitoring
       =
Reduced ESC10 Risk
```

For penetration testers:

```text
Do Not Ask:
"Is StrongCertificateBindingEnforcement
set to a historical weak value?"

Ask:
"What certificate mapping behaviour is
actually accepted by this currently
patched authentication service?"
```

For defenders:

```text
Do Not Assume:
"The registry value looks correct."

Ask:
"Can every accepted certificate be
strongly and uniquely associated with
the intended Active Directory account?"
```

The complete ESC10 relationship is:

```text
Certificate
     |
     v
Authentication Service
     |
     v
Mapping Method
     |
     v
Identity Binding
     |
     v
Active Directory Account
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](ad-cs.md)

AD CS enumeration:

[AD CS Enumeration](ad-cs-enumeration.md)

ESC1:

[AD CS ESC1](ad-cs-esc1.md)

ESC6:

[AD CS ESC6](ad-cs-esc6.md)

ESC9:

[AD CS ESC9](ad-cs-esc9.md)

ACL and ACE Abuse:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Kerberos:

[Kerberos](kerberos.md)

BloodHound:

[BloodHound](bloodhound.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs-esc11.md
```

---

# References

## Microsoft - KB5014754

[Microsoft - KB5014754 Certificate-Based Authentication Changes](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

This is the primary reference for understanding the modern KDC certificate-binding behaviour relevant to historical ESC10 Case 1.

---

## Microsoft - Certificate Mapping

[Microsoft - Client Certificate Mapping Authentication](https://learn.microsoft.com/en-us/iis/configuration/system.webserver/security/authentication/clientcertificatemappingauthentication/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Schannel

[Microsoft - TLS Registry Settings](https://learn.microsoft.com/en-us/windows-server/security/tls/tls-registry-settings){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Verify the installed version before operational testing:

```bash
certipy --version
certipy find -h
certipy auth -h
```

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC10 is fundamentally about the trust decision made after a certificate has already been obtained.

Other AD CS techniques often answer:

```text
How Did the Attacker Obtain the Certificate?
```

ESC10 answers:

```text
Why Did Windows Accept This Certificate
as That Account?
```

That distinction is essential.

The complete chain may be:

```text
Certificate Enrollment Weakness
        |
        v
Certificate Obtained
        |
        v
ESC10 Weak Mapping
        |
        v
Different Security Principal
```

Historically, ESC10 was heavily associated with:

```text
StrongCertificateBindingEnforcement
```

and:

```text
CertificateMappingMethods
```

but those settings must now be interpreted in their modern Windows context.

Microsoft's certificate-authentication hardening substantially changed KDC mapping behaviour, and the supported Compatibility-mode fallback ended in September 2025.

Therefore, in a current assessment:

```text
Old Registry Check
```

is not enough.

The correct workflow is:

```text
Determine Patch State
        |
        v
Determine Authentication Service
        |
        v
Determine Effective Mapping
        |
        v
Inspect Certificate Identity
        |
        v
Determine Mapped Account
```

ESC10 also has important relationships with:

```text
ESC9
ESC14
ESC16
```

because these techniques influence whether strong certificate identity information exists and how certificates can be explicitly mapped.

For example:

```text
ESC9
 |
 v
No SID Security Extension
 |
 v
ESC10
 |
 v
Weak Mapping Accepted
```

was historically powerful.

In a fully patched modern domain:

```text
No SID Security Extension
 |
 v
No Acceptable Strong Mapping
 |
 v
Authentication Rejected
```

may instead be the result.

That difference must appear in the final assessment.

For penetration testers, never weaken domain-controller certificate mapping merely to reproduce a historical exploit chain.

For defenders, the objective is that every certificate accepted for authentication has a strong and unambiguous relationship to the intended Active Directory account.

The central ESC10 question is therefore:

```text
Why does this certificate map
to this security principal?
```

If the answer is based only on identity information that an attacker can manipulate, the certificate-authentication design requires further investigation.
