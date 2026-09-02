# AD CS ESC6 - CA Allows Requester-Supplied Subject Alternative Names

ESC6 is an Active Directory Certificate Services (AD CS) configuration weakness involving the Certification Authority setting:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

When this CA-wide flag is enabled, the Enterprise Certification Authority can accept Subject Alternative Name (SAN) information supplied through certificate request attributes.

Historically, this could allow a requester who could enroll in an authentication-capable certificate template to request a certificate containing another account's identity.

The classic ESC6 relationship is:

```text
Low-Privileged User
        |
        v
Can Enroll in Authentication Template
        |
        v
Enterprise CA
        |
        v
EDITF_ATTRIBUTESUBJECTALTNAME2 Enabled
        |
        v
Requester Supplies SAN
        |
        v
Certificate Contains Alternate Identity
        |
        v
Certificate Authentication
        |
        v
Potential Privilege Escalation
```

However, ESC6 must now be understood together with Microsoft's certificate-based authentication hardening.

Modern, fully patched Active Directory environments enforce stronger certificate mappings. Microsoft moved domain controllers to Full Enforcement beginning with the February 2025 security update and ended support for the `StrongCertificateBindingEnforcement` compatibility-mode registry fallback with the September 9, 2025 security update.

Therefore:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2 Enabled
```

does **not automatically mean**:

```text
Arbitrary Domain Authentication
```

in a current environment.

The certificate's SID security extension, certificate mapping behaviour, template configuration, CA configuration, and domain controller patch state must all be considered.

!!! warning "Authorised testing only"
    ESC6 testing can involve requesting authentication certificates containing alternative identities. Begin with read-only CA and template enumeration. Where active validation is explicitly authorised, use dedicated test accounts and the minimum privilege necessary. Do not request certificates representing production administrators or other privileged users merely to demonstrate the configuration weakness.

---

# ESC6 Concept

ESC1 and ESC6 are related but operate at different levels.

ESC1 concerns the:

```text
Certificate Template
```

whereas ESC6 concerns the:

```text
Certification Authority
```

The distinction is:

```text
ESC1
 |
 v
Template Allows Requester-Supplied Subject
```

versus:

```text
ESC6
 |
 v
CA Allows Requester-Supplied SAN Attributes
```

ESC6 is therefore primarily a:

```text
CA-Wide Configuration Weakness
```

---

# The Important Flag

The key configuration flag is:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

It belongs to the CA's policy-module configuration.

Conceptually:

```text
Certification Authority
        |
        v
Policy Module
        |
        v
EditFlags
        |
        v
EDITF_ATTRIBUTESUBJECTALTNAME2
```

When enabled, SAN information supplied as request attributes may be included in issued certificates.

---

# Why ESC6 Is CA-Wide

This distinction is extremely important.

ESC1 is normally associated with:

```text
One Certificate Template
```

ESC6 affects behaviour at the:

```text
Certification Authority
```

level.

Conceptually:

```text
CA
 |
 +--> Template A
 |
 +--> Template B
 |
 +--> Template C
 |
 +--> Template D
```

If the CA accepts requester-supplied SAN attributes, multiple templates may need to be evaluated.

Therefore an ESC6 assessment should not stop after finding one template.

---

# Subject Alternative Name

The Subject Alternative Name extension can contain several identity forms.

Examples include:

```text
UPN
DNS Name
Email Address
IP Address
OtherName
```

For Active Directory certificate authentication, a UPN is particularly important.

Example:

```text
administrator@corp.example
```

---

# SAN and Certificate Identity

A simplified certificate identity model is:

```text
Certificate
    |
    +--> Subject
    |
    +--> SAN
           |
           +--> UPN
           |
           +--> DNS
           |
           +--> Other Identity Data
```

Windows certificate authentication may use certificate identity information when mapping the certificate to an Active Directory security principal.

Modern strong certificate mapping significantly changes how safely this information can be used.

---

# ESC6 vs ESC1

The classic ESC1 requirement includes a template configuration allowing requester-controlled subject information.

Conceptually:

```text
Certificate Template
       |
       v
ENROLLEE_SUPPLIES_SUBJECT
```

ESC6 instead relies on:

```text
Certification Authority
       |
       v
EDITF_ATTRIBUTESUBJECTALTNAME2
```

Therefore:

```text
ESC1 = Template-Level
ESC6 = CA-Level
```

---

# Why ESC6 Was Historically Dangerous

Historically, an attacker could potentially combine:

```text
Low-Privileged Enrollment
        +
Authentication-Capable Template
        +
ESC6 CA Configuration
```

and request a certificate containing a privileged user's UPN.

For example:

```text
Attacker
   |
   v
Enroll
   |
   v
User Template
   |
   v
CA Accepts SAN Attribute
   |
   v
SAN UPN:
administrator@corp.example
```

If certificate mapping accepted the supplied identity:

```text
Certificate
    |
    v
Administrator
```

the attacker could authenticate as the privileged account.

---

# Historical ESC6 Attack Model

The traditional chain was:

```text
Low-Privileged User
       |
       v
Authentication Template
       |
       v
Certificate Request
       |
       v
Requester-Supplied SAN
       |
       v
Enterprise CA
       |
       v
EDITF_ATTRIBUTESUBJECTALTNAME2
       |
       v
Certificate with Privileged UPN
       |
       v
PKINIT
       |
       v
Privileged TGT
```

This historical model is no longer sufficient by itself when assessing a modern patched environment.

---

# Modern ESC6

Microsoft's certificate-based authentication hardening introduced stronger mappings between certificates and Active Directory accounts.

The important conceptual change is:

```text
Certificate Identity
       |
       v
Must Strongly Map
       |
       v
Active Directory Account
```

rather than relying only on weaker identity information such as:

```text
UPN
Subject
Issuer + Subject
```

---

# KB5014754

Microsoft introduced certificate-based authentication hardening through:

```text
KB5014754
```

The changes were designed to address certificate spoofing and weak certificate-to-account mappings.

The deployment evolved through:

```text
Compatibility
     |
     v
Enforcement
     |
     v
Full Enforcement
```

---

# Current Enforcement Timeline

For modern assessments, the timeline matters.

Microsoft states that domain controllers moved to Full Enforcement when the February 2025 Windows security update was installed unless administrators had explicitly configured a supported override.

Support for returning to Compatibility mode remained temporarily available.

That compatibility mechanism ended with the:

```text
September 9, 2025
```

Windows security update.

After that point, Microsoft no longer supports the:

```text
StrongCertificateBindingEnforcement
```

registry key for returning domain controllers to the older compatibility behaviour.

Therefore, in a normally patched environment in 2026:

```text
Strong Certificate Mapping
```

should be treated as the expected baseline.

---

# Why This Matters for ESC6

Historically:

```text
Attacker Certificate
       |
       v
SAN = Administrator UPN
       |
       v
Administrator Authentication
```

Modern mapping can instead produce:

```text
Attacker Certificate
       |
       +--> SAN = Administrator UPN
       |
       +--> SID Extension = Attacker SID
       |
       v
Strong Mapping
       |
       v
Mismatch
       |
       v
Authentication Fails
```

This is a critical difference.

---

# SID Security Extension

Modern Enterprise CA-issued certificates can contain a security extension identifying the requester's SID.

The extension is commonly referred to as the:

```text
SID Security Extension
```

and is associated with:

```text
szOID_NTDS_CA_SECURITY_EXT
```

The extension binds the certificate more strongly to the Active Directory security principal associated with the request.

Conceptually:

```text
Certificate
    |
    +--> SAN UPN
    |
    +--> SID Security Extension
             |
             v
        Requester SID
```

---

# ESC6 and SID Binding

Suppose:

```text
Requester:
CORP\alice
```

with SID:

```text
S-1-5-21-...-1105
```

attempts to supply:

```text
administrator@corp.example
```

as the SAN UPN.

The issued certificate may conceptually contain:

```text
SAN:
administrator@corp.example

SID Security Extension:
S-1-5-21-...-1105
```

Strong certificate mapping can use the SID extension to prevent the certificate from being mapped to the administrator account.

---

# ESC6 Is Not Necessarily Gone

Do not conclude:

```text
KB5014754
    =
ESC6 Can Never Matter
```

That is too broad.

ESC6 remains an important security configuration because its impact depends on factors such as:

```text
Template Configuration
SID Security Extension
Certificate Mapping
CA Configuration
Domain Controller Patch State
Explicit Certificate Mappings
Other ESC Conditions
```

---

# ESC6 and ESC9

ESC9 involves certificate templates configured to omit the SID security extension.

Conceptually:

```text
ESC6
 |
 v
Requester-Supplied SAN
```

combined with:

```text
ESC9
 |
 v
No SID Security Extension
```

can materially change the certificate mapping analysis.

This is why modern AD CS testing must consider combinations of ESC conditions.

---

# ESC6 and ESC16

ESC16 concerns CA-wide suppression of the SID security extension.

Conceptually:

```text
ESC6
 |
 +--> CA Accepts SAN
 |
ESC16
 |
 +--> CA Does Not Add SID Security Extension
 |
 v
Certificate Mapping Risk
```

This can make ESC6 significantly more relevant in modern environments.

ESC16 should therefore be evaluated whenever ESC6 is identified.

---

# ESC6 and ESC10

ESC10 concerns weak certificate mapping configurations.

Conceptually:

```text
ESC6
 |
 v
Attacker-Controlled SAN
 |
 v
Weak Certificate Mapping
 |
 v
Potential Alternate Identity
```

Modern assessments should evaluate certificate mapping rather than assuming default legacy behaviour.

---

# ESC6 and ESC1

ESC6 can coexist with ESC1.

For example:

```text
Template
 |
 +--> ENROLLEE_SUPPLIES_SUBJECT
 |
CA
 |
 +--> EDITF_ATTRIBUTESUBJECTALTNAME2
```

In this case, multiple mechanisms may permit requester-controlled certificate identity.

Report the actual configuration rather than treating the ESC labels as mutually exclusive.

---

# ESC6 and ESC7

ESC7 concerns dangerous CA permissions.

A principal with sufficient CA administrative rights may potentially change CA configuration.

Conceptually:

```text
ESC7
 |
 v
CA Administrative Control
 |
 v
Change EditFlags
 |
 v
Enable ESC6
```

This creates an important relationship:

```text
ESC7
    ->
ESC6
```

where authorised CA management rights are misdelegated.

---

# ESC6 Preconditions

A meaningful ESC6 assessment generally considers:

```text
Enterprise CA
        +
EDITF_ATTRIBUTESUBJECTALTNAME2 Enabled
        +
Attacker Can Enroll
        +
Suitable Certificate Template
        +
Certificate Can Be Issued
        +
Authentication / Trust Use
        +
Relevant Mapping Behaviour
```

Not every enabled flag results in privilege escalation.

---

# Enterprise CA

First identify Enterprise Certification Authorities.

Using Certipy:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review discovered:

```text
Certificate Authorities
Certificate Templates
CA Configuration
Vulnerabilities
```

---

# Certipy Enumeration

Begin by checking the installed version:

```bash
certipy --version
```

and available discovery options:

```bash
certipy find -h
```

A common read-only enumeration pattern is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

---

# Certipy ESC6 Output

Depending on the Certipy release, CA vulnerability analysis may identify:

```text
ESC6
```

when the CA permits requester-supplied SAN attributes.

Review:

```text
CA Name
DNS Name
Web Enrollment
User Specified SAN
Request Disposition
Permissions
Vulnerabilities
```

Exact field names vary between releases.

---

# Certipy JSON Output

Structured output can make larger assessments easier to analyse.

Review the installed version's options:

```bash
certipy find -h
```

and store results securely.

Certificate infrastructure enumeration may contain sensitive information about:

```text
CA Names
Templates
Permissions
PKI Configuration
```

---

# Native CA Enumeration

From an authorised Windows system, CA configuration can be queried using:

```cmd
certutil -config - -ping
```

This can assist with identifying available Certification Authorities.

---

# Query CA Policy Configuration

Where administrative access and scope permit, `certutil` can query CA policy configuration.

The relevant policy-module configuration contains:

```text
EditFlags
```

and should be reviewed for:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

Do not modify the setting during enumeration.

---

# CA Registry Location

On the CA server, policy-module configuration is associated with the CA registry hierarchy under:

```text
HKLM\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration
```

The exact CA instance appears beneath the configuration key.

Conceptually:

```text
CertSvc
  |
  v
Configuration
  |
  v
<CA Name>
  |
  v
PolicyModules
  |
  v
CertificateAuthority_MicrosoftDefault.Policy
  |
  v
EditFlags
```

---

# Read EditFlags with PowerShell

On an authorised CA server, first identify the CA configuration:

```powershell
Get-ChildItem 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration'
```

Then inspect the relevant policy-module key.

For example:

```powershell
$caName = 'CORP-CA'

$policyPath = "HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration\$caName\PolicyModules\CertificateAuthority_MicrosoftDefault.Policy"

Get-ItemProperty -Path $policyPath -Name EditFlags
```

This is read-only.

---

# Do Not Modify EditFlags During Enumeration

Avoid commands that change:

```text
EditFlags
```

during normal testing.

Changing CA policy behaviour can affect certificate requests from multiple templates and applications.

---

# Certutil Policy Query

Where supported by the installed Windows version and administrative context, inspect CA configuration using `certutil`.

Start with:

```cmd
certutil -?
```

and:

```cmd
certutil -getreg
```

Then query the relevant policy-module configuration according to the installed version.

Prefer read-only queries.

---

# CA Configuration vs Active Directory Configuration

An important distinction is:

```text
Certificate Template
       |
       v
Stored in Active Directory
```

while:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
       |
       v
CA Policy Configuration
```

Therefore ordinary LDAP enumeration of certificate templates does not by itself establish ESC6.

---

# Enumerate Templates Published by the CA

Once an ESC6 CA is identified, enumerate the templates it publishes.

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Identify Authentication Templates

For each published template, determine whether certificates can be used for authentication.

Relevant EKUs can include:

```text
Client Authentication
1.3.6.1.5.5.7.3.2

Smart Card Logon
1.3.6.1.4.1.311.20.2.2

PKINIT Client Authentication
1.3.6.1.5.2.3.4
```

Other certificate-purpose configurations may also require analysis.

---

# Enumerate Template EKUs

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage,'msPKI-Certificate-Application-Policy' |
    Select-Object Name,pKIExtendedKeyUsage,'msPKI-Certificate-Application-Policy'
```

---

# Enrollment Rights

The attacker must normally be able to request a certificate from a relevant template.

Review:

```text
Enroll
Autoenroll
```

permissions.

Enrollment rights may be assigned to:

```text
Domain Users
Domain Computers
Authenticated Users
Specific Groups
Application Groups
Service Accounts
```

---

# Manager Approval

A template may require certificate manager approval.

Conceptually:

```text
Request
   |
   v
Pending
   |
   v
Certificate Manager Approval
   |
   v
Issued
```

This can interrupt a straightforward ESC6 path.

---

# Authorized Signatures

Templates may also require authorised signatures.

Review:

```text
msPKI-RA-Signature
```

A value requiring one or more authorised signatures can prevent direct issuance.

---

# Request Disposition

CA request disposition should also be considered.

If certificate requests are:

```text
Pending
```

rather than automatically issued, the attack path changes.

Do not infer automatic issuance from template enrollment rights alone.

---

# ESC6 Enumeration Model

A good enumeration workflow is:

```text
Identify Enterprise CAs
        |
        v
Check CA EditFlags
        |
        v
Is EDITF_ATTRIBUTESUBJECTALTNAME2 Enabled?
        |
        +--> No -> ESC6 Not Identified
        |
        +--> Yes
                |
                v
        Enumerate Published Templates
                |
                v
        Identify Enrollable Templates
                |
                v
        Identify Authentication Capability
                |
                v
        Check Issuance Requirements
                |
                v
        Check SID Extension
                |
                v
        Check Certificate Mapping
```

---

# Modern Validation Strategy

Do not immediately attempt:

```text
Administrator UPN
```

Instead use two controlled accounts.

For example:

```text
CORP\esc6-requester
CORP\esc6-target
```

Both should be dedicated assessment accounts.

---

# Controlled Test Model

A safe validation model is:

```text
esc6-requester
       |
       v
Certificate Request
       |
       v
SAN = esc6-target@corp.example
       |
       v
Certificate Issued
       |
       v
Inspect Certificate
       |
       v
Determine SID Extension
       |
       v
Test Mapping Only If Approved
```

This demonstrates the relevant behaviour without involving a privileged production account.

---

# Inspect the Certificate Before Authentication

After obtaining an approved test certificate, inspect:

```text
Subject
SAN
UPN
Issuer
Serial Number
EKUs
SID Security Extension
Validity
Template
```

Do not jump directly from issuance to authentication.

---

# Windows Certificate Inspection

For an exported certificate:

```cmd
certutil -dump test.cer
```

For a PFX:

```cmd
certutil -dump test.pfx
```

Protect any private-key material.

---

# OpenSSL Inspection

Where appropriate:

```bash
openssl x509 -in test.cer -inform DER -text -noout
```

or for PEM:

```bash
openssl x509 -in test.pem -text -noout
```

Review:

```text
X509v3 extensions
Subject Alternative Name
Extended Key Usage
Other Microsoft-specific extensions
```

---

# Check SID Extension

The important question is:

```text
Which SID Is Bound to the Certificate?
```

For a modern CA-issued certificate, determine whether the SID corresponds to:

```text
Requester
```

or whether the relevant security extension is absent.

---

# Expected Modern Behaviour

A common modern result is:

```text
Requester:
alice

Requested SAN:
administrator@corp.example

Certificate SID:
alice SID
```

Strong mapping should prevent the certificate from simply becoming an Administrator certificate.

This should be documented as:

```text
ESC6 Configuration Present
but
Classic Privilege Escalation Mitigated by Strong Mapping
```

if that is what testing establishes.

---

# Do Not Overstate ESC6

Avoid reporting:

```text
Domain Admin Compromise
```

solely because:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

is enabled.

Instead determine:

```text
Is Alternate SAN Accepted?
Is SID Extension Present?
Which SID Is Embedded?
Which Mapping Method Is Used?
Can Authentication Actually Map to Another Account?
```

---

# Strong Certificate Mapping

Modern certificate mapping considers strong identifiers.

Microsoft distinguishes stronger mappings from legacy weaker name-based mappings.

The objective is to prevent:

```text
Certificate Name
       |
       v
Arbitrary Account
```

without a cryptographically or administratively stronger relationship.

---

# Current 2026 Baseline

For a fully patched Active Directory environment in 2026:

```text
Full Enforcement
```

should be expected.

Microsoft's compatibility fallback through:

```text
StrongCertificateBindingEnforcement
```

ceased to be supported after the September 9, 2025 security update.

Therefore legacy ESC6 write-ups should not be copied directly into modern findings.

---

# Legacy Systems

An assessment may still encounter:

```text
Unpatched Domain Controllers
Unsupported Windows Server Versions
Delayed Security Updates
Isolated Legacy Domains
Special Compatibility Configurations
```

Document actual patch state rather than assuming modern behaviour.

---

# Check Domain Controller Versions

```powershell
Get-ADDomainController -Filter * |
    Select-Object HostName,OperatingSystem,OperatingSystemVersion
```

Operating system version alone does not establish patch level.

---

# Check Installed Updates

On an authorised domain controller:

```powershell
Get-HotFix |
    Sort-Object InstalledOn -Descending |
    Select-Object -First 20 HotFixID,InstalledOn,Description
```

For modern Windows versions, update inventory may also require the organisation's patch-management or servicing records.

---

# Registry Checks

Older ESC6 guidance frequently recommends checking:

```text
StrongCertificateBindingEnforcement
```

to determine certificate mapping behaviour.

In current patched environments, this registry setting should not be treated as a supported method for reverting to legacy compatibility behaviour after the September 2025 enforcement transition.

Use actual:

```text
Patch State
Authentication Behaviour
Microsoft-Supported Configuration
```

when assessing current systems.

---

# ESC6 and Explicit Certificate Mapping

Explicit certificate mappings may also influence authentication.

Active Directory supports certificate mappings through:

```text
altSecurityIdentities
```

This becomes particularly relevant to:

```text
ESC14
```

and weak explicit mapping configurations.

---

# ESC6 and UPN Mapping

Legacy certificate authentication often relied heavily on:

```text
SAN UPN
```

mapping.

Modern environments should not be assessed as though UPN alone is always sufficient.

This is one of the largest differences between historical and current ESC6 testing.

---

# ESC6 and Computer Accounts

SAN manipulation is not limited conceptually to user UPNs.

Certificate identity may also involve:

```text
DNS Names
Computer Accounts
Machine Authentication
```

depending on certificate type and authentication protocol.

Again, modern mapping must be evaluated.

---

# ESC6 and Domain Controllers

Do not request certificates representing:

```text
Domain Controllers
```

during routine validation.

Domain controller certificates participate in critical services including:

```text
Kerberos
LDAPS
Smart Card Authentication
PKINIT
```

Use dedicated test systems where proof is required.

---

# Certipy Request Syntax

Certipy changes over time.

Before requesting a certificate, inspect the installed version:

```bash
certipy req -h
```

and:

```bash
certipy auth -h
```

For an authorised ESC6 assessment, use the syntax documented by the installed release to:

```text
Select CA
Select Template
Supply Approved Test SAN
Request Certificate
Inspect Result
```

Do not copy request syntax from old ESC6 write-ups without checking the installed Certipy version.

---

# Why We Verify Tool Syntax

AD CS tooling evolves alongside Microsoft's certificate hardening.

Commands from older research may assume:

```text
Legacy Mapping
Legacy Certipy CLI
Legacy Windows Behaviour
```

A modern assessment should verify both:

```text
Tool Version
```

and:

```text
Target Behaviour
```

---

# BloodHound

BloodHound can provide useful context around:

```text
Enrollment Rights
CA Relationships
Template Relationships
PKI Privilege Paths
```

See:

[BloodHound](bloodhound.md)

Graph data should complement, not replace, direct CA configuration verification.

---

# PowerView

PowerView is useful for:

```text
Template ACLs
Group Membership
Object Control
```

but ESC6 itself is a CA policy configuration.

Therefore:

```text
PowerView Template Enumeration
```

alone cannot prove:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

is enabled.

---

# LDAP Enumeration

LDAP can enumerate:

```text
Certificate Templates
Enrollment Services
Template Permissions
PKI Objects
```

but the ESC6 flag is associated with CA policy configuration.

Therefore:

```text
LDAP
```

should be combined with:

```text
CA Configuration Enumeration
```

---

# ESC6 and Web Enrollment

Web Enrollment is not required for ESC6.

Do not confuse:

```text
ESC6
```

with:

```text
ESC8
```

ESC8 concerns NTLM relay to AD CS HTTP enrollment endpoints.

ESC6 concerns:

```text
Requester-Supplied SAN Attributes
```

at the CA policy level.

---

# ESC6 and RPC Enrollment

Certificate requests can reach a CA through mechanisms other than Web Enrollment.

Therefore:

```text
No /certsrv/
```

does not mean:

```text
ESC6 Cannot Exist
```

---

# Detection

ESC6 detection has two major components:

```text
Configuration Monitoring
```

and:

```text
Certificate Request / Issuance Monitoring
```

---

# Detect CA Configuration Changes

Monitor changes to the CA policy-module configuration.

Particularly important:

```text
EditFlags
```

Changes enabling:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

should be investigated.

---

# Registry Monitoring

On CA systems, monitor changes beneath:

```text
HKLM\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration
```

especially policy-module configuration.

Use:

```text
EDR
Registry Auditing
Configuration Management
Change Control
```

as appropriate.

---

# CA Service Restart

Some CA configuration changes may require:

```text
Certificate Services Restart
```

to become effective.

Unexpected CA service restarts near policy configuration changes can therefore provide useful investigation context.

---

# Certificate Services Events

Where Certificate Services auditing is enabled, relevant events can include:

```text
4886 - Certificate Services received a certificate request

4887 - Certificate Services approved a certificate request and issued a certificate
```

Event availability depends on auditing configuration.

---

# Monitor Request Attributes

Where telemetry permits, inspect certificate requests for unexpected:

```text
SAN
UPN
DNS
Subject
```

values.

A particularly useful comparison is:

```text
Requester Identity
        |
        v
Requested Certificate Identity
```

---

# Suspicious Identity Mismatch

For example:

```text
Requester:
CORP\alice

Requested SAN:
administrator@corp.example
```

should receive investigation even if strong mapping ultimately prevents successful authentication.

The request itself indicates suspicious activity.

---

# Correlate Certificate Issuance

A useful detection chain is:

```text
Certificate Request
       |
       v
Unexpected SAN
       |
       v
Certificate Issued
       |
       v
Certificate Authentication Attempt
```

---

# Kerberos Authentication

Certificate-based Kerberos authentication can generate:

```text
4768
```

for a Ticket Granting Ticket request.

Certificate-related information in authentication telemetry can help correlate:

```text
Certificate Issuance
```

with:

```text
PKINIT Authentication
```

depending on logging and Windows version.

---

# Monitor CA Administrative Activity

Changes to ESC6 configuration should normally be performed only by authorised PKI administrators.

Correlate:

```text
Administrative Logon
Registry Modification
CA Configuration Change
CertSvc Restart
```

---

# Detect ESC7 to ESC6

If a principal with inappropriate CA administrative permissions enables the ESC6 flag, the sequence may look like:

```text
CA Administrative Access
       |
       v
EditFlags Modified
       |
       v
CA Service Restart
       |
       v
Certificate Request with SAN
```

This is a high-value detection chain.

---

# Hardening ESC6

The primary remediation is:

```text
Disable EDITF_ATTRIBUTESUBJECTALTNAME2
```

unless there is a documented and justified requirement for CA-wide requester-supplied SAN attributes.

---

# Prefer Template-Level Controls

If an application genuinely requires requester-supplied identity information, prefer tightly scoped template controls rather than enabling broad CA-wide behaviour.

Conceptually:

```text
One Controlled Template
```

is preferable to:

```text
Every Template Processed by the CA
```

where technically feasible.

---

# Review Business Requirement

Before retaining ESC6 configuration, establish:

```text
Which Application Requires It?
Which Template Uses It?
Who Can Enroll?
Why Is CA-Wide Behaviour Necessary?
Can It Be Replaced?
```

Legacy requirements should not automatically remain enabled indefinitely.

---

# Review All Published Templates

If ESC6 is enabled, review every template published by that CA for:

```text
Enrollment Rights
Authentication EKUs
Issuance Requirements
SID Extension Behaviour
Approval
Authorized Signatures
```

Do not evaluate ESC6 in isolation.

---

# Restrict Enrollment

Reduce unnecessary enrollment rights.

Avoid broad access such as:

```text
Domain Users
Authenticated Users
Domain Computers
```

unless genuinely required.

---

# Restrict Authentication Templates

Authentication-capable templates deserve particular attention.

Examples include certificates used for:

```text
Client Authentication
Smart Card Logon
PKINIT
```

---

# Require Approval Where Appropriate

Sensitive certificate workflows may use:

```text
Certificate Manager Approval
```

to introduce an additional control.

This should not be treated as a substitute for correcting an unnecessary ESC6 configuration.

---

# Authorized Signatures

High-value templates may require:

```text
Authorized Signatures
```

where organisational workflows support them.

Again, this is defence in depth rather than justification for unsafe CA-wide SAN behaviour.

---

# Maintain Current Windows Patching

Domain controllers and CA servers should remain fully patched.

Certificate authentication security depends on:

```text
CA Behaviour
Domain Controller Behaviour
Certificate Mapping
```

not just template configuration.

---

# Strong Certificate Mapping

Modern environments should maintain Microsoft's strong certificate mapping protections.

Do not weaken certificate mapping to preserve legacy workflows without a detailed security review.

---

# Review ESC9

If ESC6 exists, explicitly review templates for:

```text
CT_FLAG_NO_SECURITY_EXTENSION
```

because this can remove the SID security extension.

See the future ESC9 notes.

---

# Review ESC10

Review domain certificate mapping configuration for weak mappings.

This becomes especially important when requester-controlled certificate identity exists.

---

# Review ESC16

Review whether the CA itself is configured to suppress the SID security extension.

This is especially important because:

```text
ESC6 + ESC16
```

may recreate a much more dangerous certificate identity manipulation path.

---

# Protect CA Administrative Permissions

Because CA administrators may be able to modify CA configuration, review:

```text
ManageCA
```

and other CA administrative rights.

This is covered in detail under ESC7.

---

# Change Control

Changes to:

```text
EditFlags
```

should require documented PKI change control.

Record:

```text
Who
What
Why
When
Approved By
Previous Value
New Value
Rollback Plan
```

---

# Baseline CA Configuration

Maintain a baseline of:

```text
CA Name
CA Host
Policy Module
EditFlags
Request Disposition
Published Templates
CA Permissions
Enrollment Endpoints
```

Compare periodically for drift.

---

# Incident Response

If ESC6 abuse is suspected:

```text
Identify CA
    |
    v
Confirm ESC6 Configuration
    |
    v
Determine When Enabled
    |
    v
Identify Requests with Supplied SANs
    |
    v
Identify Issued Certificates
    |
    v
Determine SID Extension
    |
    v
Identify Authentication
    |
    v
Revoke Malicious Certificates
```

---

# Determine When the Flag Was Enabled

Establish whether:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

was:

```text
Long-Standing Configuration
```

or:

```text
Recently Enabled
```

A recent unexpected change may indicate active compromise.

---

# Identify Certificate Requests

Review requests during the exposure period for unusual:

```text
SAN UPN
SAN DNS
Subject
Requester
Template
```

combinations.

---

# Identify Requester and Certificate Identity

Compare:

```text
Requester
```

with:

```text
Certificate SAN
```

and:

```text
SID Security Extension
```

This helps determine whether attempted identity substitution occurred.

---

# Identify Issued Certificates

For suspicious certificates record:

```text
Serial Number
Thumbprint
Requester
Subject
SAN
Template
Issuer
Issue Time
Expiration
EKUs
SID Extension
```

---

# Identify Authentication

Correlate suspicious certificates with:

```text
Kerberos TGT Requests
Smart Card Authentication
Client Certificate Authentication
Application Authentication
```

depending on certificate purpose.

---

# Revoke Malicious Certificates

Where malicious certificates were issued:

```text
Revoke Certificate
       |
       v
Publish Updated CRL
       |
       v
Verify Revocation Distribution
```

---

# Password Reset Is Not Enough

As with other AD CS abuse:

```text
Password Reset
      |
      X
Certificate Revocation
```

An issued certificate remains separate credential material until it expires or is revoked and revocation is enforced.

---

# Disable Unnecessary ESC6 Configuration

If the setting is not required:

```text
Disable
EDITF_ATTRIBUTESUBJECTALTNAME2
```

through the organisation's approved PKI change process.

Do not make emergency CA changes without understanding application dependencies.

---

# Review Other ESC Conditions

Following suspected ESC6 abuse, review:

```text
ESC1
ESC4
ESC5
ESC7
ESC9
ESC10
ESC16
```

because attackers may combine multiple PKI weaknesses.

---

# Reporting ESC6

Avoid reporting only:

```text
ESC6
```

A clearer finding title is:

```text
Certification Authority Accepts Requester-Supplied Subject Alternative Names
```

or:

```text
CA-Wide SAN Configuration Permits Requester-Controlled Certificate Identity
```

---

# Example Finding - Configuration Present, Modern Mapping Mitigates Exploitation

```text
Finding:
Certification Authority Accepts Requester-Supplied Subject
Alternative Names

Affected CA:
CORP-CA01

Configuration:
EDITF_ATTRIBUTESUBJECTALTNAME2 enabled

Description:
The Enterprise Certification Authority CORP-CA01 is configured to
accept Subject Alternative Name information supplied through
certificate request attributes.

This behaviour applies at the CA level rather than being limited to
a single certificate template.

Historically, this configuration could allow a requester with
enrollment rights over an authentication-capable template to request
a certificate containing another Active Directory account's UPN.

During controlled validation, a certificate request submitted by the
approved test account was able to include the UPN of a second test
account.

The issued certificate retained the requester's SID security
extension. Authentication as the alternate test identity was not
possible under the domain's enforced strong certificate mapping
configuration.

Impact:
The CA exposes unnecessary requester-controlled SAN functionality
across certificate templates processed by the CA.

The classic ESC6 arbitrary-identity authentication path was not
demonstrated because strong certificate mapping bound the issued
certificate to the requester's SID.

The configuration nevertheless increases PKI attack surface and may
become exploitable when combined with other weaknesses that remove
the SID security extension or weaken certificate mappings.

Recommendation:
Disable EDITF_ATTRIBUTESUBJECTALTNAME2 unless there is a documented
business requirement for CA-wide requester-supplied SAN attributes.

Review all templates published by the affected CA and identify
whether any omit the SID security extension or otherwise permit weak
certificate mappings.

Maintain current Windows security updates and strong certificate
mapping enforcement.

Where requester-supplied SAN information is legitimately required,
use the most narrowly scoped certificate enrollment design supported
by the application.
```

---

# Example Finding - Exploitable Combination

Where testing demonstrates a real alternate-identity authentication path, document the complete chain.

```text
Finding:
Requester-Supplied SAN Configuration Enables Certificate-Based
Privilege Escalation

Affected CA:
CORP-CA01

Affected Template:
CorpAuthentication

Description:
The Enterprise Certification Authority accepts requester-supplied
Subject Alternative Name attributes.

The CorpAuthentication certificate template is available to the
affected low-privileged principal and issues certificates suitable
for Active Directory authentication.

Additional certificate mapping controls in the environment do not
prevent the issued certificate from mapping to the alternate
identity supplied in the approved test request.

Impact:
A principal with enrollment rights may be able to obtain certificate
credentials representing another Active Directory identity.

Where a privileged identity is reachable, this may result in
privilege escalation without knowledge of the target account's
password.

Recommendation:
Disable the CA-wide requester-supplied SAN configuration.

Review certificate templates published by the CA, restrict enrollment
rights, ensure the SID security extension is present where required,
and maintain strong certificate mapping enforcement.

Revoke certificates issued through unauthorised identity substitution
and investigate certificate-based authentication during the exposure
period.
```

---

# Severity Assessment

ESC6 severity should consider:

```text
CA Flag Enabled
      +
Enrollable Template
      +
Authentication Capability
      +
Issuance Requirements
      +
SID Extension Behaviour
      +
Certificate Mapping
      +
Reachable Identity
      =
Severity
```

---

# Do Not Rate on Flag Alone

For example:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
       |
       v
Enabled
```

does not automatically establish:

```text
Critical
```

The actual authentication path matters.

---

# High-Risk Combination

A significantly more dangerous combination may look like:

```text
ESC6
 |
 +--> Requester-Controlled SAN
 |
ESC9 / ESC16
 |
 +--> SID Security Extension Missing
 |
Weak / Applicable Mapping
 |
 +--> Alternate Identity Accepted
 |
 v
Privilege Escalation
```

---

# Reduced Exploitability Example

```text
ESC6 Enabled
      |
      v
Authentication Template
      |
      v
Certificate Issued
      |
      v
Requester SID Extension Present
      |
      v
Strong Mapping Enforced
      |
      v
Alternate Identity Rejected
```

The unsafe CA configuration still deserves review, but the demonstrated impact differs substantially.

---

# Evidence Checklist

For an ESC6 assessment record:

```text
CA Name
CA Host
CA Type
Policy Module
EditFlags
EDITF_ATTRIBUTESUBJECTALTNAME2 State
Published Templates
Template Name
Enrollment Rights
Authentication EKUs
Manager Approval
Authorized Signatures
Request Disposition
Requester
Requested SAN
Issued Subject
Issued SAN
SID Security Extension
SID Value
Certificate Serial Number
Certificate Thumbprint
Domain Controller Patch State
Certificate Mapping Behaviour
Authentication Result
Validation Accounts
Cleanup Result
```

---

# ESC6 Assessment Checklist

## CA Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify CA hosts
- [ ] Identify policy modules
- [ ] Enumerate published templates
- [ ] Record CA configuration
- [ ] Record CA permissions

## ESC6 Configuration

- [ ] Inspect `EditFlags`
- [ ] Determine whether `EDITF_ATTRIBUTESUBJECTALTNAME2` is enabled
- [ ] Confirm configuration directly where possible
- [ ] Do not rely solely on automated classification
- [ ] Determine whether configuration is documented
- [ ] Determine business requirement

## Template Analysis

- [ ] Enumerate templates published by affected CA
- [ ] Identify enrollment rights
- [ ] Identify Client Authentication
- [ ] Identify Smart Card Logon
- [ ] Identify PKINIT capability
- [ ] Review application policies
- [ ] Review manager approval
- [ ] Review authorised signatures
- [ ] Review request disposition
- [ ] Review SID security-extension behaviour

## Modern Mapping

- [ ] Determine domain controller versions
- [ ] Determine actual patch state
- [ ] Account for February 2025 Full Enforcement
- [ ] Account for September 9, 2025 compatibility fallback removal
- [ ] Determine whether SID security extension is present
- [ ] Determine which SID is embedded
- [ ] Review explicit certificate mappings
- [ ] Review weak mapping conditions
- [ ] Evaluate ESC9
- [ ] Evaluate ESC10
- [ ] Evaluate ESC16

## Tooling

- [ ] Enumerate with Certipy
- [ ] Verify installed Certipy version
- [ ] Review `certipy find -h`
- [ ] Review `certipy req -h` before active testing
- [ ] Review `certipy auth -h` before authentication testing
- [ ] Inspect CA configuration with native tools
- [ ] Inspect templates with PowerShell
- [ ] Use BloodHound for relationship context
- [ ] Use LDAP for template and PKI object verification

## Validation

- [ ] Prefer read-only enumeration
- [ ] Obtain approval before certificate requests
- [ ] Use dedicated requester test account
- [ ] Use dedicated target test account
- [ ] Do not use production administrator identity
- [ ] Request minimum necessary certificate
- [ ] Inspect certificate before authentication
- [ ] Record SAN
- [ ] Record SID extension
- [ ] Verify mapping behaviour only if required
- [ ] Stop once sufficient evidence exists
- [ ] Revoke test certificate if required
- [ ] Remove private-key material

## Detection

- [ ] Monitor CA `EditFlags`
- [ ] Monitor CA registry configuration
- [ ] Monitor CertSvc restarts
- [ ] Monitor certificate requests
- [ ] Monitor certificate issuance
- [ ] Monitor event 4886 where configured
- [ ] Monitor event 4887 where configured
- [ ] Identify unusual SAN values
- [ ] Compare requester with requested identity
- [ ] Correlate issuance with PKINIT
- [ ] Monitor event 4768 where relevant
- [ ] Monitor CA administrative activity

## Hardening

- [ ] Disable unnecessary `EDITF_ATTRIBUTESUBJECTALTNAME2`
- [ ] Prefer narrowly scoped template controls
- [ ] Restrict enrollment
- [ ] Review authentication templates
- [ ] Review approval requirements
- [ ] Review authorised signatures
- [ ] Maintain strong certificate mapping
- [ ] Maintain Windows patching
- [ ] Review ESC9
- [ ] Review ESC10
- [ ] Review ESC16
- [ ] Restrict CA administrative permissions
- [ ] Baseline CA configuration
- [ ] Implement PKI change control

## Incident Response

- [ ] Identify affected CA
- [ ] Establish when ESC6 was enabled
- [ ] Identify who changed configuration
- [ ] Review CA administrative activity
- [ ] Review CertSvc restarts
- [ ] Identify certificate requests
- [ ] Identify unusual SAN values
- [ ] Identify issued certificates
- [ ] Record requester
- [ ] Record SAN
- [ ] Record SID extension
- [ ] Identify certificate authentication
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Disable unnecessary configuration
- [ ] Review related ESC conditions

## Cleanup

- [ ] Revoke approved test certificates where required
- [ ] Delete test PFX files
- [ ] Delete exported private keys
- [ ] Remove temporary certificate-store entries
- [ ] Verify CA configuration unchanged
- [ ] Verify no production template was modified
- [ ] Record cleanup evidence

---

# ESC6 Testing Model

The ESC1 model is:

```text
Template
   |
   v
Requester-Supplied Subject
```

The ESC6 model is:

```text
CA
 |
 v
EDITF_ATTRIBUTESUBJECTALTNAME2
 |
 v
Requester-Supplied SAN Attribute
```

The historical attack model is:

```text
Low-Privileged User
       |
       v
Enroll
       |
       v
Authentication Template
       |
       v
ESC6 CA
       |
       v
SAN = Administrator
       |
       v
Certificate
       |
       v
Administrator Authentication
```

The modern model is:

```text
Requester
   |
   v
Certificate Request
   |
   +--> Alternate SAN
   |
   v
Enterprise CA
   |
   +--> SID Security Extension
   |
   v
Certificate
   |
   v
Strong Mapping
   |
   +--> Identity Matches -> Authentication
   |
   +--> Identity Mismatch -> Rejected
```

The ESC6 + ESC9 model is:

```text
ESC6
 |
 +--> Requester-Supplied SAN
 |
ESC9
 |
 +--> Template Omits SID Extension
 |
 v
Certificate Mapping Analysis
```

The ESC6 + ESC16 model is:

```text
ESC6
 |
 +--> Requester-Supplied SAN
 |
ESC16
 |
 +--> CA-Wide SID Extension Disabled
 |
 v
Alternate Identity Risk
```

The ESC7 relationship is:

```text
ESC7
 |
 v
CA Administrative Control
 |
 v
Modify EditFlags
 |
 v
Enable ESC6
```

The safe validation model is:

```text
Enumerate CA
    |
    v
Confirm ESC6 Flag
    |
    v
Enumerate Templates
    |
    v
Identify Candidate
    |
    v
Evaluate Modern Mapping
    |
    v
Need Active Proof?
    |
    +--> No -> Report
    |
    +--> Yes
           |
           v
       Test Requester
           |
           v
       Test Target
           |
           v
       Request Certificate
           |
           v
       Inspect SAN + SID
           |
           v
       Controlled Mapping Test
           |
           v
       Revoke / Cleanup
```

The detection model is:

```text
EditFlags Change
      |
      v
CA Service Restart
      |
      v
Certificate Request
      |
      v
Unexpected SAN
      |
      v
Certificate Issuance
      |
      v
Authentication Attempt
```

The defensive model is:

```text
ESC6 Disabled
      +
Restricted Enrollment
      +
Strong Mapping
      +
SID Security Extension
      +
Current Patching
      +
Restricted CA Administration
      +
Monitoring
      =
Reduced ESC6 Risk
```

For penetration testers:

```text
Do Not Ask:
"Is EDITF_ATTRIBUTESUBJECTALTNAME2 enabled?"

Also Ask:
"Can an enrolled certificate actually map to
another security principal under the target's
current certificate mapping configuration?"
```

For defenders:

```text
Do Not Assume:
"Strong mapping means ESC6 can be ignored."

Instead Ask:
"Why does the CA accept requester-controlled
SAN information at all, and could another PKI
weakness remove the protection we currently
depend on?"
```

That distinction is central to modern ESC6 testing.

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](ad-cs.md)

AD CS enumeration:

[AD CS Enumeration](ad-cs-enumeration.md)

ESC1:

[AD CS ESC1](ad-cs-esc1.md)

ESC2:

[AD CS ESC2](ad-cs-esc2.md)

ESC3:

[AD CS ESC3](ad-cs-esc3.md)

ESC4:

[AD CS ESC4](ad-cs-esc4.md)

ESC5:

[AD CS ESC5](ad-cs-esc5.md)

Kerberos:

[Kerberos](kerberos.md)

Active Directory ACL and ACE Abuse:

[Active Directory ACL and ACE Abuse](acl-ace.md)

BloodHound:

[BloodHound](bloodhound.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs-esc7.md
```

---

# References

## Microsoft - KB5014754

[Microsoft - KB5014754 Certificate-Based Authentication Changes](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

This is essential reading for modern ESC6 assessments because Microsoft's enforcement timeline materially changed the classic certificate mapping attack path.

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Template Concepts

[Microsoft - Certificate Template Concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Manage Certificate Templates

[Microsoft - Manage Certificate Templates](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/manage-certificate-templates){ target="_blank" rel="noopener noreferrer" }

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

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC6 is one of the AD CS techniques where historical exploitation guidance must be interpreted in the context of modern Windows security changes.

The old mental model was:

```text
ESC6
 |
 v
Supply Administrator UPN
 |
 v
Get Administrator Certificate
```

That is no longer an accurate universal model.

The modern model is:

```text
Requester-Controlled SAN
        |
        v
Certificate Issuance
        |
        v
SID Security Extension
        |
        v
Strong Certificate Mapping
        |
        v
Actual Account Mapping
```

Microsoft's certificate-based authentication hardening materially changed the final stage of this chain.

In a fully patched 2026 environment, Full Enforcement should be expected, and the legacy `StrongCertificateBindingEnforcement` compatibility fallback is no longer supported after the September 9, 2025 security update.

Therefore:

```text
ESC6 Flag Present
```

and:

```text
ESC6 Privilege Escalation Demonstrated
```

are not the same statement.

A strong assessment determines:

```text
Is the Flag Enabled?
        |
        v
Which Templates Are Published?
        |
        v
Who Can Enroll?
        |
        v
Can the Certificate Authenticate?
        |
        v
Is the SID Extension Present?
        |
        v
Which SID Is Embedded?
        |
        v
How Does the DC Map the Certificate?
        |
        v
Can Another Identity Actually Be Reached?
```

ESC6 becomes especially important when combined with other AD CS weaknesses.

In particular:

```text
ESC6 + ESC9
```

or:

```text
ESC6 + ESC16
```

may alter the strong-mapping protection provided by the SID security extension.

Similarly:

```text
ESC7
```

may provide a route to enabling ESC6 through inappropriate CA administrative control.

For penetration testers, the correct approach is therefore to test the entire certificate identity chain rather than reproducing an old SAN impersonation command and assuming success.

For defenders, the safest configuration remains to disable unnecessary CA-wide requester-supplied SAN behaviour even when strong mapping currently prevents the classic exploitation path.

Defence in depth should ensure:

```text
ESC6 Disabled
        +
SID Security Extension Present
        +
Strong Mapping Enforced
        +
Templates Hardened
        +
CA Permissions Restricted
        +
Current Windows Updates
```

rather than depending on a single mitigation to protect an unnecessarily permissive CA configuration.
