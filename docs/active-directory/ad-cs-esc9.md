# AD CS ESC9 - Certificate Template Omits the SID Security Extension

ESC9 is an Active Directory Certificate Services (AD CS) certificate-template misconfiguration where certificates issued from a template do not contain the Active Directory SID security extension.

The condition is associated with the certificate template enrollment flag:

```text
CT_FLAG_NO_SECURITY_EXTENSION
```

When this flag is enabled, the Certification Authority does not include the SID security extension in certificates issued from that template.

The simplified relationship is:

```text
Certificate Template
        |
        v
CT_FLAG_NO_SECURITY_EXTENSION
        |
        v
Certificate Issued
        |
        v
No SID Security Extension
        |
        v
Certificate Mapping Must Rely
on Other Identity Information
```

ESC9 became particularly important following Microsoft's certificate-based authentication hardening introduced through KB5014754.

The SID security extension provides a strong relationship between:

```text
Certificate
```

and:

```text
Active Directory Security Principal
```

Removing that extension can cause certificate authentication to depend on other mapping mechanisms.

However, modern fully patched domain controllers operate under Microsoft's Full Enforcement model. Therefore:

```text
ESC9 Present
```

does not automatically mean:

```text
Arbitrary User Impersonation
```

The actual certificate mapping path must be evaluated.

!!! warning "Authorised testing only"
    ESC9 validation can involve temporary changes to Active Directory identity attributes and certificate requests. Begin with read-only certificate-template enumeration. Do not modify the UPN or other mapping attributes of production users, administrators, service accounts, or domain controllers merely to demonstrate ESC9. Where active validation is required, use dedicated test identities and restore every changed attribute immediately after the approved test.

---

# ESC9 Concept

Modern AD CS certificates issued by an Enterprise CA can contain an extension linking the certificate to the SID of the Active Directory account that requested it.

Conceptually:

```text
Certificate
    |
    +--> Subject
    |
    +--> SAN
    |
    +--> EKUs
    |
    +--> SID Security Extension
              |
              v
          Account SID
```

ESC9 removes the final component:

```text
Certificate
    |
    +--> Subject
    |
    +--> SAN
    |
    +--> EKUs
    |
    X--> SID Security Extension
```

This weakens the certificate's built-in relationship to the requesting security principal.

---

# Why the SID Matters

Consider a user:

```text
CORP\alice
```

with SID:

```text
S-1-5-21-111111111-222222222-333333333-1105
```

A normally issued authentication certificate may conceptually contain:

```text
UPN:
alice@corp.example

SID:
S-1-5-21-111111111-222222222-333333333-1105
```

The SID gives the domain controller a stronger way to associate the certificate with:

```text
CORP\alice
```

rather than relying only on a name.

---

# ESC9 Certificate

With ESC9:

```text
UPN:
alice@corp.example

SID Security Extension:
Not Present
```

The domain controller must therefore determine whether another acceptable certificate mapping exists.

That mapping behaviour is central to modern ESC9 analysis.

---

# The Important Flag

ESC9 is associated with:

```text
CT_FLAG_NO_SECURITY_EXTENSION
```

in:

```text
msPKI-Enrollment-Flag
```

on the certificate template.

Conceptually:

```text
Certificate Template
       |
       v
msPKI-Enrollment-Flag
       |
       v
CT_FLAG_NO_SECURITY_EXTENSION
```

---

# Certificate Template Object

Certificate templates are stored in the Configuration naming context under:

```text
CN=Certificate Templates,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

The relevant attribute is:

```text
msPKI-Enrollment-Flag
```

---

# ESC9 Is Template-Level

ESC9 applies to:

```text
Certificate Template
```

rather than:

```text
Entire Certification Authority
```

This distinguishes ESC9 from ESC16.

Conceptually:

```text
ESC9
 |
 v
Template-Level
```

versus:

```text
ESC16
 |
 v
CA-Level
```

---

# ESC9 vs ESC16

The distinction is important.

ESC9:

```text
Template
 |
 v
NO_SECURITY_EXTENSION
 |
 v
Certificates from This Template
Lack SID Security Extension
```

ESC16:

```text
Certification Authority
 |
 v
CA-Wide Security Extension Suppression
 |
 v
Certificates Across Affected Templates
May Lack SID Security Extension
```

ESC16 will be covered separately.

---

# ESC9 vs ESC6

ESC6 concerns:

```text
Requester-Supplied SAN
```

through CA configuration.

ESC9 concerns:

```text
Missing SID Security Extension
```

through template configuration.

The two can interact.

Conceptually:

```text
ESC6
 |
 +--> Requester-Controlled Identity
 |
ESC9
 |
 +--> No SID Security Extension
 |
 v
Certificate Mapping Risk
```

---

# ESC9 vs ESC10

ESC10 concerns weak certificate mapping configurations.

ESC9 removes one of the strong certificate identifiers.

ESC10 determines whether weaker certificate mapping can still succeed.

Conceptually:

```text
ESC9
 |
 v
No SID Extension
 |
 v
ESC10
 |
 v
Weak Mapping Accepted
 |
 v
Potential Identity Impersonation
```

Therefore ESC9 and ESC10 should often be evaluated together.

---

# ESC9 vs ESC1

ESC1 normally involves:

```text
Requester Controls Certificate Subject / SAN
```

ESC9 does not inherently require:

```text
ENROLLEE_SUPPLIES_SUBJECT
```

Instead, historical ESC9 exploitation can involve manipulating an Active Directory identity attribute that the CA automatically places into the certificate.

This distinction is important.

---

# ESC9 vs ESC4

ESC4 concerns control over a certificate-template object.

A principal with sufficient template modification rights may potentially create ESC9 by changing:

```text
msPKI-Enrollment-Flag
```

Conceptually:

```text
ESC4
 |
 v
Template Write Access
 |
 v
Enable NO_SECURITY_EXTENSION
 |
 v
ESC9
```

Therefore template ACLs should also be reviewed.

---

# ESC9 vs ESC5

ESC5 concerns control over broader PKI objects or infrastructure.

ESC9 is specifically:

```text
Certificate Template Configuration
```

The two may coexist but have different root causes.

---

# KB5014754

Microsoft introduced certificate-based authentication hardening through:

```text
KB5014754
```

The changes were designed to address certificate spoofing and weak certificate mappings.

One important component was stronger binding between:

```text
Certificate
```

and:

```text
Active Directory Account
```

---

# SID Security Extension

Enterprise CAs can place the requester's object SID into the issued certificate.

Conceptually:

```text
Requester
   |
   v
Active Directory SID
   |
   v
Certification Authority
   |
   v
Certificate SID Extension
```

This creates a strong identity relationship.

---

# Normal Certificate Mapping

A simplified normal model is:

```text
alice
  |
  v
Request Certificate
  |
  v
Certificate
  |
  +--> alice@corp.example
  |
  +--> Alice SID
  |
  v
Domain Controller
  |
  v
Alice
```

---

# ESC9 Mapping Model

With ESC9:

```text
alice
  |
  v
Request Certificate
  |
  v
Certificate
  |
  +--> alice@corp.example
  |
  X--> SID Extension
  |
  v
Domain Controller
  |
  v
Other Mapping Required
```

---

# Strong and Weak Certificate Mapping

Microsoft distinguishes stronger mappings from weaker name-based mappings.

Strong mappings provide a stronger relationship between the certificate and the intended account.

Weak mappings can depend on identity information such as:

```text
Subject
UPN
Email
Issuer / Subject combinations
```

depending on the mapping mechanism.

ESC9 matters because:

```text
No SID Extension
```

can force the authentication process to consider other mapping mechanisms.

---

# Current 2026 Enforcement Context

Microsoft's KB5014754 rollout reached Full Enforcement beginning with the February 2025 security update.

Microsoft states that certificates that cannot be strongly mapped are denied authentication in Full Enforcement mode.

The temporary ability to return to Compatibility mode through:

```text
StrongCertificateBindingEnforcement
```

remained available until the:

```text
September 9, 2025
```

Windows security update.

After that update, Microsoft no longer supports that registry key as a compatibility fallback.

Therefore a normally patched Active Directory environment in 2026 should be assessed assuming:

```text
Full Enforcement
```

unless evidence shows otherwise.

---

# Why This Changes ESC9 Testing

Historical ESC9 attack chains often relied on:

```text
Certificate Without SID
        |
        v
Weak UPN Mapping
        |
        v
Target Account
```

That should not be assumed to work in a current environment.

The modern question is:

```text
What Strong Mapping, If Any,
Can the Domain Controller Use?
```

---

# ESC9 Still Matters

Do not conclude:

```text
Full Enforcement
    =
ESC9 Irrelevant
```

The missing SID extension remains a security-relevant certificate-template configuration.

The final impact depends on:

```text
Certificate Mapping
Explicit Mapping
Template Configuration
Account Attributes
CA Configuration
Domain Controller State
Other ESC Conditions
```

---

# ESC9 Preconditions

A meaningful ESC9 path generally includes:

```text
Enterprise CA
        +
Published Certificate Template
        +
Attacker Enrollment Rights
        +
Authentication-Capable Certificate
        +
NO_SECURITY_EXTENSION
        +
No Manager Approval
        +
No Required Authorized Signature
        +
Usable Certificate Mapping Path
```

Not every ESC9 template results in privilege escalation.

---

# Enterprise CA

Identify Enterprise Certification Authorities.

Using Certipy:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review:

```text
Certificate Authorities
Certificate Templates
Permissions
Vulnerabilities
```

---

# Certipy ESC9 Enumeration

Current Certipy releases can identify templates where the security extension is disabled.

Begin with:

```bash
certipy --version
```

Then:

```bash
certipy find -h
```

A typical enumeration command is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Look for:

```text
ESC9
```

and verify the underlying template configuration manually.

---

# Do Not Trust the Label Alone

An automated result such as:

```text
ESC9
```

should lead to:

```text
Inspect Template
        |
        v
Confirm NO_SECURITY_EXTENSION
        |
        v
Confirm Enrollment
        |
        v
Confirm Authentication EKU
        |
        v
Analyse Mapping
```

Do not report privilege escalation solely because the label appears.

---

# PowerShell Enumeration

Enumerate certificate templates:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties displayName,'msPKI-Enrollment-Flag' |
    Select-Object Name,displayName,'msPKI-Enrollment-Flag'
```

---

# Inspect One Template

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(cn=ESC9-Test)' -Properties * |
    Select-Object Name,displayName,'msPKI-Enrollment-Flag',pKIExtendedKeyUsage,'msPKI-Certificate-Application-Policy'
```

---

# Enrollment Flag Is a Bitmask

`msPKI-Enrollment-Flag` contains multiple flags.

Therefore:

```text
Value != 0
```

does not automatically mean:

```text
ESC9
```

The specific:

```text
CT_FLAG_NO_SECURITY_EXTENSION
```

bit must be present.

---

# PowerShell Bitmask Analysis

When performing detailed analysis, decode the template's enrollment flags rather than relying only on the raw decimal value.

Conceptually:

```text
msPKI-Enrollment-Flag
        |
        v
Bitmask
        |
        +--> Flag A
        +--> Flag B
        +--> NO_SECURITY_EXTENSION
```

---

# Certipy Output

Certipy may represent the condition using fields similar to:

```text
No Security Extension
```

or:

```text
ESC9
```

depending on release.

Verify the raw template attribute where important.

---

# BloodHound

BloodHound represents certificate-template properties including security-extension configuration.

See:

[BloodHound](bloodhound.md)

A template node may expose information related to:

```text
No Security Extension
Enrollment Rights
Authentication EKUs
Template ACLs
```

---

# BloodHound Attack Paths

BloodHound can help connect:

```text
User
 |
 v
Enroll
 |
 v
ESC9 Template
```

with other identity-control relationships.

However, the final certificate mapping behaviour still requires target-specific validation.

---

# Published Template Requirement

A vulnerable template must normally be published by a CA before it can be used for enrollment.

Enumerate Enterprise CAs and their published templates:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Enrollment Rights

The requesting principal must normally have:

```text
Enroll
```

rights over the template.

Common broad groups include:

```text
Domain Users
Domain Computers
Authenticated Users
```

but broad enrollment is not automatically vulnerable.

It becomes significant when combined with the other ESC9 conditions.

---

# Manager Approval

Check whether:

```text
Certificate Manager Approval
```

is required.

Conceptually:

```text
Request
   |
   v
Pending
   |
   v
Manual Approval
```

This can interrupt straightforward exploitation.

---

# Authorized Signatures

Review:

```text
msPKI-RA-Signature
```

A template requiring authorised signatures introduces an additional issuance requirement.

---

# Authentication EKUs

For certificate-based authentication, relevant EKUs can include:

```text
Client Authentication
1.3.6.1.5.5.7.3.2

PKINIT Client Authentication
1.3.6.1.5.2.3.4

Smart Card Logon
1.3.6.1.4.1.311.20.2.2

Any Purpose
2.5.29.37.0
```

No-EKU templates require additional contextual analysis and should not be treated simplistically.

---

# Subject Alternative Name Source

An important ESC9 question is:

```text
Where Does the Certificate Identity Come From?
```

For some templates, the CA builds certificate identity information from Active Directory attributes.

For example:

```text
userPrincipalName
```

may become certificate identity information.

This is why historical ESC9 exploitation often involved temporary UPN manipulation.

---

# Historical ESC9 Chain

A classic historical chain can be represented as:

```text
Attacker Controls Account
       |
       v
Can Modify Own UPN
       |
       v
UPN Temporarily Changed
       |
       v
Request ESC9 Certificate
       |
       v
Certificate Contains Target-Like UPN
       |
       v
No SID Security Extension
       |
       v
Restore Original UPN
       |
       v
Certificate Mapping
       |
       v
Target Identity
```

This should be understood as a mapping technique, not a guarantee of success in a fully patched 2026 environment.

---

# Why UPN Restoration Matters Historically

Suppose a test account is:

```text
esc9-user@corp.example
```

and an approved second test account is:

```text
esc9-target@corp.example
```

Historical validation might temporarily alter the requester's UPN so that the issued certificate contains the target-like identity.

After certificate issuance, the original UPN is restored.

The certificate then retains the identity information captured at issuance time.

---

# Do Not Use Administrator

Do not perform a routine test using:

```text
Administrator
```

as the alternate identity.

Use:

```text
ESC9-Requester
ESC9-Target
```

or equivalent dedicated assessment accounts.

---

# UPN Uniqueness

UPN manipulation can affect authentication and application behaviour.

Before any approved test:

```text
Record Original UPN
Verify Target UPN
Confirm No Production Dependency
Define Rollback
```

---

# Read Original UPN

For an approved test account:

```powershell
Get-ADUser -Identity 'ESC9-Requester' -Properties userPrincipalName |
    Select-Object SamAccountName,userPrincipalName
```

Record the result before making any change.

---

# Safe Active Validation

Prefer:

```text
Read-Only Evidence
```

where sufficient.

If active proof is necessary:

```text
Dedicated Test Requester
       |
       v
Dedicated Test Target
       |
       v
Approved Temporary Attribute Change
       |
       v
Certificate Request
       |
       v
Immediate Attribute Restoration
       |
       v
Certificate Inspection
       |
       v
Optional Mapping Test
```

---

# Change Only What Is Necessary

Do not combine ESC9 validation with unrelated changes such as:

```text
Template Modification
CA Configuration Changes
CA Permission Changes
Production Account Changes
```

unless those are separately authorised assessment objectives.

---

# Request Certificate

Before using Certipy operationally:

```bash
certipy req -h
```

Verify the installed release's syntax.

For approved testing, request a certificate only from the identified test template and using the dedicated test account.

---

# Inspect Certificate Before Authentication

After issuance, inspect:

```text
Subject
SAN
UPN
Issuer
Serial Number
Thumbprint
Template
EKUs
Validity
SID Security Extension
```

The critical ESC9 validation question is:

```text
Is the SID Security Extension Absent?
```

---

# Windows Certificate Inspection

```cmd
certutil -dump esc9-test.cer
```

---

# OpenSSL Inspection

For DER:

```bash
openssl x509 -in esc9-test.cer -inform DER -text -noout
```

For PEM:

```bash
openssl x509 -in esc9-test.pem -text -noout
```

---

# Expected ESC9 Certificate

Conceptually:

```text
Subject Alternative Name:
esc9-target@corp.example

Extended Key Usage:
Client Authentication

SID Security Extension:
Absent
```

This proves the template omitted the SID extension.

It does not by itself prove authentication as the target.

---

# Restore Identity Attributes Immediately

After the certificate request:

```text
Restore Original UPN
```

before proceeding with any further approved validation.

Verify the restoration independently.

---

# Verify Restoration

```powershell
Get-ADUser -Identity 'ESC9-Requester' -Properties userPrincipalName |
    Select-Object SamAccountName,userPrincipalName
```

Compare against the value recorded before testing.

---

# Certificate Authentication

If authentication testing is required:

```bash
certipy auth -h
```

Verify the syntax supported by the installed Certipy release.

Only use the approved test identity.

---

# Authentication Failure Is Useful Evidence

In a modern environment, authentication may fail because:

```text
Certificate Cannot Be Strongly Mapped
```

That result is valuable.

Report:

```text
ESC9 Template Misconfiguration Present
```

but:

```text
Cross-Account Authentication Not Demonstrated
Under Current Strong Mapping Enforcement
```

if that is what testing establishes.

---

# Do Not Force Legacy Mapping

Do not weaken:

```text
Strong Certificate Mapping
```

merely to demonstrate what ESC9 would have done historically.

That changes the security posture of the domain and is unnecessary for most assessments.

---

# ESC9 and Full Enforcement

In Full Enforcement:

```text
Certificate
      |
      v
Strong Mapping Available?
      |
      +--> Yes -> Evaluate Mapping
      |
      +--> No -> Authentication Denied
```

This is the expected modern security model.

---

# ESC9 and Explicit Strong Mapping

A certificate without the SID extension may still have an explicit strong mapping configured.

Therefore:

```text
No SID Extension
```

does not necessarily mean:

```text
No Strong Mapping
```

Inspect the actual account and certificate mapping configuration.

---

# altSecurityIdentities

Explicit certificate mappings can be stored using:

```text
altSecurityIdentities
```

This becomes especially important when analysing:

```text
ESC10
ESC14
```

and other certificate mapping conditions.

---

# ESC9 and ESC14

ESC14 concerns weak explicit certificate mappings.

Conceptually:

```text
ESC9
 |
 v
No SID Security Extension
 |
 v
Explicit Certificate Mapping
 |
 v
ESC14 Analysis
```

These conditions should not be conflated, but they can interact.

---

# ESC9 and ESC6

If the CA also accepts requester-controlled SAN attributes:

```text
ESC6
```

the attack surface becomes more complex.

Conceptually:

```text
ESC6
 |
 +--> Identity Manipulation
 |
ESC9
 |
 +--> No SID Extension
 |
 v
Certificate Mapping
```

---

# ESC9 and ESC16

ESC16 is the CA-wide analogue that should always be checked when ESC9-like certificates are observed.

If many unrelated templates unexpectedly omit the SID security extension:

```text
Investigate ESC16
```

rather than assuming every template independently has ESC9.

---

# ESC9 Enumeration Workflow

A good workflow is:

```text
Enumerate Enterprise CAs
        |
        v
Enumerate Published Templates
        |
        v
Check Enrollment Rights
        |
        v
Check Authentication EKUs
        |
        v
Check Manager Approval
        |
        v
Check Authorized Signatures
        |
        v
Check NO_SECURITY_EXTENSION
        |
        v
Analyse Certificate Identity Source
        |
        v
Analyse Strong Mapping
```

---

# Modern Validation Workflow

```text
ESC9 Template Identified
        |
        v
Is Read-Only Evidence Enough?
        |
        +--> Yes -> Report
        |
        +--> No
               |
               v
        Use Test Accounts
               |
               v
        Record Original Attributes
               |
               v
        Approved Identity Change
               |
               v
        Request Certificate
               |
               v
        Restore Attributes
               |
               v
        Inspect Certificate
               |
               v
        Test Mapping If Required
```

---

# Detection

ESC9 detection should focus on:

```text
Template Configuration
Identity Attribute Changes
Certificate Requests
Certificate Issuance
Certificate Authentication
```

---

# Detect Template Configuration

Monitor certificate templates for:

```text
CT_FLAG_NO_SECURITY_EXTENSION
```

and changes to:

```text
msPKI-Enrollment-Flag
```

---

# Event 5136

Changes to certificate-template objects in Active Directory can generate:

```text
5136
```

when Directory Service Changes auditing is appropriately configured.

Monitor changes under:

```text
CN=Certificate Templates,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

---

# Monitor Enrollment Flag Changes

A suspicious sequence is:

```text
Template Modified
       |
       v
NO_SECURITY_EXTENSION Enabled
       |
       v
Certificate Requested
       |
       v
Template Restored
```

This may indicate an ESC4-to-ESC9 chain.

---

# Detect UPN Changes

Historical ESC9 abuse may involve changes to:

```text
userPrincipalName
```

Monitor unexpected UPN modifications.

A particularly suspicious pattern is:

```text
UPN Changed
    |
    v
Certificate Requested
    |
    v
UPN Restored
```

within a short period.

---

# Event 5136 and User Attributes

Where auditing is configured, changes to user objects may also be visible through Directory Service Changes telemetry.

Focus on changes to:

```text
userPrincipalName
altSecurityIdentities
```

and other certificate mapping attributes.

---

# Event 4738

Changes to user accounts may generate:

```text
4738
```

depending on the modified attributes and audit configuration.

Correlate account-change events with certificate enrollment.

---

# Certificate Request Events

Where Certificate Services auditing is enabled:

```text
4886
```

can indicate receipt of a certificate request.

---

# Certificate Issuance

```text
4887
```

can indicate that Certificate Services approved a request and issued a certificate.

---

# Correlate Events

A useful ESC9 detection chain is:

```text
UPN Change
    |
    v
Certificate Request
    |
    v
Certificate Issued
    |
    v
UPN Restored
    |
    v
Certificate Authentication
```

---

# Detect Certificate Authentication

Kerberos certificate authentication may produce:

```text
4768
```

for TGT requests.

Where certificate information is available, correlate authentication with recently issued ESC9 certificates.

---

# Monitor Template ACLs

Because ESC4 can be used to create ESC9, also monitor:

```text
WriteDACL
WriteOwner
GenericWrite
GenericAll
WriteProperty
```

over certificate templates.

See:

[AD CS ESC4](ad-cs-esc4.md)

---

# BloodHound Monitoring

BloodHound can help identify principals that can:

```text
Enroll in ESC9 Template
```

or:

```text
Modify ESC9 Template
```

Use graph analysis alongside direct configuration monitoring.

---

# Hardening ESC9

The primary remediation is:

```text
Remove CT_FLAG_NO_SECURITY_EXTENSION
```

from templates unless there is a documented and technically justified requirement.

---

# Restore SID Security Extension

Authentication-capable certificates should normally retain the SID security extension where supported.

Conceptually:

```text
Certificate
   |
   +--> Identity
   |
   +--> SID
```

provides stronger binding than:

```text
Certificate
   |
   +--> Name Only
```

---

# Review Authentication Templates

Prioritise templates containing:

```text
Client Authentication
Smart Card Logon
PKINIT Client Authentication
Any Purpose
```

and other configurations that can participate in authentication.

---

# Review Enrollment Rights

Remove unnecessary:

```text
Enroll
```

rights from broad groups.

Use least privilege.

---

# Review Manager Approval

For sensitive certificate workflows, determine whether:

```text
Certificate Manager Approval
```

is appropriate.

This is defence in depth and does not replace correcting ESC9.

---

# Review Authorized Signatures

Sensitive templates may require:

```text
Authorized Signatures
```

where operationally appropriate.

Again, correct the root cause rather than depending solely on additional issuance barriers.

---

# Maintain Full Enforcement

Keep domain controllers fully patched and maintain Microsoft's strong certificate mapping enforcement.

Do not weaken certificate mapping to support unnecessary legacy certificate workflows.

---

# Review Explicit Mappings

Audit:

```text
altSecurityIdentities
```

for weak or unexpected certificate mappings.

This is particularly important when templates omit the SID security extension.

---

# Review ESC10

Whenever ESC9 is identified, evaluate:

```text
ESC10
```

because weak mapping configuration may determine whether the missing SID extension becomes exploitable.

---

# Review ESC14

Also review:

```text
ESC14
```

for weak explicit certificate mappings.

---

# Review ESC16

Determine whether the missing SID extension is caused by:

```text
Template Configuration
```

or:

```text
CA-Wide Configuration
```

If the latter:

```text
ESC16
```

may be the more appropriate classification.

---

# Protect Template ACLs

Only authorised PKI administrators should be able to modify:

```text
msPKI-Enrollment-Flag
```

or other security-sensitive template attributes.

---

# Baseline Templates

Maintain a baseline containing:

```text
Template Name
Enrollment Flags
Name Flags
EKUs
Application Policies
Enrollment Rights
Manager Approval
Authorized Signatures
Template ACL
Published CAs
```

Compare regularly for drift.

---

# Change Control

Changes to:

```text
NO_SECURITY_EXTENSION
```

should require formal PKI change control.

Record:

```text
Who
Why
Template
Previous Value
New Value
Approval
Rollback Plan
```

---

# Incident Response

If ESC9 abuse is suspected:

```text
Identify Template
      |
      v
Determine Exposure Period
      |
      v
Review Template Changes
      |
      v
Review UPN Changes
      |
      v
Identify Certificate Requests
      |
      v
Identify Issued Certificates
      |
      v
Identify Authentication
      |
      v
Revoke Malicious Certificates
```

---

# Determine Whether ESC9 Was Intentional

Establish whether:

```text
NO_SECURITY_EXTENSION
```

was:

```text
Long-Standing Configuration
```

or:

```text
Recently Enabled
```

A recent unexpected change may indicate abuse.

---

# Review Replication Metadata

For suspicious template changes, Active Directory replication metadata can help establish:

```text
When
```

and:

```text
Where
```

an attribute was changed.

On an authorised administrative system, tools such as:

```text
repadmin
```

can assist with replication metadata analysis.

---

# Review Template Modification

Determine whether an attacker used an ESC4-like path to enable:

```text
NO_SECURITY_EXTENSION
```

temporarily.

Compare against:

```text
Known-Good Template Configuration
```

---

# Review User Attribute Changes

Search for temporary changes to:

```text
userPrincipalName
```

around suspicious certificate requests.

Also inspect:

```text
altSecurityIdentities
```

where relevant.

---

# Identify Certificate Requests

For suspicious requests record:

```text
Request ID
Requester
Template
Subject
SAN
Submission Time
Disposition
```

---

# Identify Issued Certificates

Record:

```text
Serial Number
Thumbprint
Issuer
Subject
SAN
Template
EKUs
Validity
SID Extension State
```

---

# Determine Whether Certificate Was Used

Review:

```text
Kerberos PKINIT
Schannel Authentication
Client TLS Authentication
VPN Authentication
Application Authentication
```

depending on certificate purpose.

---

# Revoke Malicious Certificates

Where unauthorised certificates were issued:

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
Issued Certificate
```

A certificate remains separate authentication material until it expires or is revoked and revocation is enforced.

---

# Restore Template Configuration

If ESC9 was introduced maliciously:

```text
Restore Approved Enrollment Flags
```

and verify:

```text
Template ACL
Enrollment Rights
Name Flags
EKUs
Issuance Requirements
```

for additional modifications.

---

# Investigate ESC4

If the attacker modified the template, identify how they obtained:

```text
Template Write Access
```

See:

[AD CS ESC4](ad-cs-esc4.md)

---

# Reporting ESC9

Avoid reporting only:

```text
ESC9
```

Prefer:

```text
Authentication Certificate Template Omits SID Security Extension
```

or:

```text
Certificate Template Disables Strong SID Binding
```

or:

```text
Low-Privileged Users Can Enroll in Authentication Certificates Without SID Security Extension
```

---

# Example Finding - Configuration Present

```text
Finding:
Authentication Certificate Template Omits SID Security Extension

Affected Template:
CorpLegacyAuthentication

Affected CA:
CORP-CA01

Description:
The CorpLegacyAuthentication certificate template is configured with
the NO_SECURITY_EXTENSION enrollment flag.

Certificates issued from this template therefore do not contain the
Active Directory SID security extension normally used to strongly
associate an Enterprise CA-issued certificate with the requesting
security principal.

Authenticated domain users can enroll in the affected template, and
the template issues certificates suitable for client
authentication.

Impact:
The absence of the SID security extension weakens the certificate's
built-in binding to the requesting Active Directory account.

Whether this results in cross-account impersonation depends on the
certificate mapping mechanisms available to domain controllers and
any explicit mappings configured in the environment.

The domain's current strong certificate mapping configuration should
therefore be evaluated before claiming privilege escalation.

Recommendation:
Remove CT_FLAG_NO_SECURITY_EXTENSION from the affected certificate
template unless there is a documented technical requirement.

Review all authentication-capable certificate templates for the same
configuration.

Maintain fully patched domain controllers and strong certificate
mapping enforcement.

Review weak and explicit certificate mappings, including relevant
altSecurityIdentities configurations.
```

---

# Example Finding - Controlled Mapping Demonstrated

```text
Finding:
Certificate Template Configuration Permits Cross-Account Certificate
Mapping

Affected Template:
CorpLegacyAuthentication

Affected CA:
CORP-CA01

Description:
The CorpLegacyAuthentication template omits the SID security
extension from issued certificates.

During controlled validation, two dedicated assessment accounts were
used.

The requester account was able to enroll in the affected template,
and the resulting certificate did not contain the requester's SID
security extension.

The approved test demonstrated that the certificate could map to the
second test identity under the environment's certificate mapping
configuration.

No privileged production identity was used.

Impact:
A principal with enrollment rights may be able to obtain certificate
credentials that map to another Active Directory identity when the
required mapping conditions are satisfied.

The resulting impact depends on the privileges of the impersonated
identity.

Recommendation:
Remove the NO_SECURITY_EXTENSION flag from the affected template.

Review certificate mapping configuration and eliminate weak mappings
where possible.

Review enrollment permissions, explicit certificate mappings, and
other authentication-capable templates for similar conditions.

Revoke certificates issued through unauthorised identity mapping.
```

---

# Severity Assessment

ESC9 severity depends on:

```text
NO_SECURITY_EXTENSION
        +
Enrollment Rights
        +
Authentication Capability
        +
Identity Manipulation Path
        +
Certificate Mapping
        +
Reachable Identity
        =
Severity
```

---

# Do Not Rate ESC9 on Flag Alone

For example:

```text
NO_SECURITY_EXTENSION
        |
        v
Enabled
```

does not automatically mean:

```text
Critical
```

The complete certificate mapping path matters.

---

# High-Risk Combination

A dangerous chain can look like:

```text
Low-Privileged User
       |
       v
Enroll
       |
       v
ESC9 Template
       |
       v
Certificate Without SID
       |
       v
Usable Mapping Condition
       |
       v
Privileged Identity
```

---

# Reduced Exploitability

A modern result may instead be:

```text
ESC9 Template
       |
       v
Certificate Without SID
       |
       v
No Valid Strong Mapping
       |
       v
Full Enforcement
       |
       v
Authentication Rejected
```

This is still a template-hardening issue, but the demonstrated impact is different.

---

# Evidence Checklist

For an ESC9 assessment record:

```text
CA Name
CA Host
Template Name
Template OID
Published State
Enrollment Rights
Authentication EKUs
msPKI-Enrollment-Flag
NO_SECURITY_EXTENSION State
Manager Approval
Authorized Signatures
Certificate Identity Source
Requester
Requester SID
Original UPN
Test UPN
Request ID
Certificate Serial Number
Certificate Thumbprint
Certificate Subject
Certificate SAN
SID Security Extension Present / Absent
Domain Controller Patch State
Mapping Behaviour
Authentication Result
Attribute Restoration
Certificate Revocation
Cleanup Result
```

---

# ESC9 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Enumerate published templates
- [ ] Identify authentication-capable templates
- [ ] Identify enrollment rights
- [ ] Identify broad enrollment groups
- [ ] Identify template owners
- [ ] Identify template write permissions

## ESC9 Configuration

- [ ] Inspect `msPKI-Enrollment-Flag`
- [ ] Decode enrollment flags
- [ ] Identify `CT_FLAG_NO_SECURITY_EXTENSION`
- [ ] Confirm automated ESC9 findings manually
- [ ] Determine whether the template is published
- [ ] Determine business requirement

## Issuance Requirements

- [ ] Check manager approval
- [ ] Check authorised signatures
- [ ] Check CA enrollment rights
- [ ] Check template enrollment rights
- [ ] Review EKUs
- [ ] Review application policies
- [ ] Determine certificate identity source

## Modern Mapping

- [ ] Determine domain controller patch state
- [ ] Account for Full Enforcement
- [ ] Account for September 9, 2025 compatibility fallback removal
- [ ] Determine whether strong mapping exists
- [ ] Review explicit mappings
- [ ] Review `altSecurityIdentities`
- [ ] Evaluate ESC10
- [ ] Evaluate ESC14
- [ ] Evaluate ESC16
- [ ] Do not assume legacy UPN mapping works

## Tooling

- [ ] Verify Certipy version
- [ ] Review `certipy find -h`
- [ ] Enumerate ESC9 with Certipy
- [ ] Verify template through PowerShell / LDAP
- [ ] Review BloodHound template properties
- [ ] Review BloodHound enrollment relationships
- [ ] Review template ACLs
- [ ] Manually validate automated findings

## Validation

- [ ] Prefer read-only evidence
- [ ] Determine whether active proof is necessary
- [ ] Obtain explicit approval
- [ ] Use dedicated requester
- [ ] Use dedicated target
- [ ] Record original UPN
- [ ] Avoid production identities
- [ ] Make minimum approved attribute change
- [ ] Request one test certificate
- [ ] Restore UPN immediately
- [ ] Verify restoration
- [ ] Inspect certificate
- [ ] Confirm SID extension is absent
- [ ] Test authentication only if required
- [ ] Do not weaken strong mapping
- [ ] Revoke test certificate where required
- [ ] Delete private-key material

## Detection

- [ ] Monitor template configuration
- [ ] Monitor `msPKI-Enrollment-Flag`
- [ ] Monitor `NO_SECURITY_EXTENSION`
- [ ] Monitor event 5136
- [ ] Monitor UPN changes
- [ ] Monitor event 4738 where relevant
- [ ] Monitor certificate requests
- [ ] Monitor event 4886 where configured
- [ ] Monitor certificate issuance
- [ ] Monitor event 4887 where configured
- [ ] Correlate UPN change with certificate issuance
- [ ] Correlate issuance with authentication
- [ ] Monitor template ACL changes

## Hardening

- [ ] Remove `NO_SECURITY_EXTENSION`
- [ ] Restore SID security extension
- [ ] Review authentication templates
- [ ] Restrict enrollment
- [ ] Review manager approval
- [ ] Review authorised signatures
- [ ] Maintain Full Enforcement
- [ ] Maintain Windows patching
- [ ] Review explicit mappings
- [ ] Review ESC10
- [ ] Review ESC14
- [ ] Review ESC16
- [ ] Protect template ACLs
- [ ] Baseline template configuration
- [ ] Require PKI change control

## Incident Response

- [ ] Identify affected template
- [ ] Determine exposure period
- [ ] Determine when ESC9 was enabled
- [ ] Review replication metadata
- [ ] Review template changes
- [ ] Review template ACL changes
- [ ] Review UPN modifications
- [ ] Review explicit mapping changes
- [ ] Identify certificate requests
- [ ] Identify issued certificates
- [ ] Identify certificate authentication
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Restore template configuration
- [ ] Investigate ESC4
- [ ] Review related ESC conditions

## Cleanup

- [ ] Restore original UPN
- [ ] Verify UPN restoration
- [ ] Restore any approved test attributes
- [ ] Revoke test certificate where required
- [ ] Remove test certificate
- [ ] Delete test PFX
- [ ] Delete private-key material
- [ ] Verify template unchanged
- [ ] Verify CA unchanged
- [ ] Record cleanup evidence

---

# ESC9 Testing Model

The normal certificate model is:

```text
Requester
   |
   v
Enterprise CA
   |
   v
Certificate
   |
   +--> Identity
   |
   +--> Requester SID
```

The ESC9 model is:

```text
Requester
   |
   v
ESC9 Template
   |
   v
Certificate
   |
   +--> Identity
   |
   X--> SID Security Extension
```

The historical mapping model is:

```text
Requester
   |
   v
Identity Attribute Change
   |
   v
ESC9 Certificate Request
   |
   v
Certificate Without SID
   |
   v
Restore Identity Attribute
   |
   v
Weak Certificate Mapping
   |
   v
Target Account
```

The modern Full Enforcement model is:

```text
Certificate Without SID
        |
        v
Strong Mapping Available?
        |
        +--> Yes
        |      |
        |      v
        |   Evaluate Mapping
        |
        +--> No
               |
               v
        Authentication Denied
```

The ESC9 + ESC10 model is:

```text
ESC9
 |
 +--> No SID Security Extension
 |
ESC10
 |
 +--> Weak Mapping Configuration
 |
 v
Potential Identity Mapping
```

The ESC9 + ESC6 model is:

```text
ESC6
 |
 +--> Requester-Controlled SAN
 |
ESC9
 |
 +--> No SID Extension
 |
 v
Certificate Mapping Risk
```

The ESC4-to-ESC9 model is:

```text
ESC4
 |
 v
Template Write Access
 |
 v
Modify Enrollment Flags
 |
 v
Enable NO_SECURITY_EXTENSION
 |
 v
ESC9
```

The ESC9 vs ESC16 model is:

```text
Template-Level
     |
     v
ESC9
```

versus:

```text
CA-Level
   |
   v
ESC16
```

The safe-validation model is:

```text
Enumerate
   |
   v
Identify ESC9
   |
   v
Read-Only Evidence Enough?
   |
   +--> Yes -> Report
   |
   +--> No
           |
           v
       Test Requester
           |
           v
       Test Target
           |
           v
       Record Original Attributes
           |
           v
       Approved Temporary Change
           |
           v
       Request Certificate
           |
           v
       Restore Attributes
           |
           v
       Inspect Certificate
           |
           v
       Mapping Test If Required
           |
           v
       Revoke / Cleanup
```

The detection model is:

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
Identity Attribute Restored
        |
        v
Certificate Authentication
```

The defensive model is:

```text
SID Security Extension
        +
Strong Mapping
        +
Restricted Enrollment
        +
Protected Template ACLs
        +
Current Patching
        +
Monitoring
        =
Reduced ESC9 Risk
```

For penetration testers:

```text
Do Not Ask:
"Does the template have ESC9?"

Ask:
"Does the template omit the SID security
extension, and does the target's current
certificate mapping configuration provide
a usable cross-account mapping path?"
```

For defenders:

```text
Do Not Assume:
"Full Enforcement means the template
configuration no longer matters."

Ask:
"Why is the SID security extension disabled,
which identities can enroll, and what other
certificate mappings exist?"
```

The complete ESC9 relationship is:

```text
Template Configuration
        |
        v
SID Extension State
        |
        v
Certificate Identity
        |
        v
Certificate Mapping
        |
        v
Active Directory Principal
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](ad-cs.md)

AD CS enumeration:

[AD CS Enumeration](ad-cs-enumeration.md)

ESC1:

[AD CS ESC1](ad-cs-esc1.md)

ESC4:

[AD CS ESC4](ad-cs-esc4.md)

ESC6:

[AD CS ESC6](ad-cs-esc6.md)

ESC8:

[AD CS ESC8](ad-cs-esc8.md)

Kerberos:

[Kerberos](kerberos.md)

ACL and ACE Abuse:

[Active Directory ACL and ACE Abuse](acl-ace.md)

BloodHound:

[BloodHound](bloodhound.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs-esc10.md
```

---

# References

## Microsoft - KB5014754

[Microsoft - KB5014754 Certificate-Based Authentication Changes](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

Microsoft's current guidance is essential when evaluating ESC9 because Full Enforcement changes whether certificates without the SID security extension can authenticate through legacy mappings.

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

## SpecterOps - ESC9

[SpecterOps - ESC9 Security Extension Disabled on Certificate Template](https://docs.specterops.io/ghostpack-docs/Certify.wik-mdx/esc9-security-extension-disabled-on-certificate-template){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Before using operational commands, verify the installed version:

```bash
certipy --version
certipy find -h
certipy req -h
certipy auth -h
```

---

## BloodHound - Certificate Templates

[BloodHound - CertTemplate](https://bloodhound.specterops.io/resources/nodes/cert-template){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC9 is fundamentally about removing one of the strongest identity-binding mechanisms available to Enterprise CA-issued certificates.

The normal model is:

```text
Certificate
     |
     v
SID Security Extension
     |
     v
Active Directory SID
     |
     v
Security Principal
```

ESC9 changes that to:

```text
Certificate
     |
     X
SID Security Extension
     |
     v
Other Mapping Required
```

This distinction became especially important after Microsoft's certificate-based authentication hardening.

Microsoft's current KB5014754 guidance confirms that domain controllers moved to Full Enforcement with the February 2025 security update and that the supported compatibility fallback ended with the September 9, 2025 security update.

Therefore, in a current environment:

```text
No SID Security Extension
```

does not automatically imply:

```text
Weak UPN Mapping Will Succeed
```

A modern assessment must determine the actual mapping path.

The correct analysis is:

```text
ESC9 Template
      |
      v
Who Can Enroll?
      |
      v
What Certificate Is Issued?
      |
      v
Is SID Extension Missing?
      |
      v
What Mapping Is Available?
      |
      v
Does Full Enforcement Accept It?
      |
      v
Which Identity Is Reached?
```

This also explains why ESC9 should rarely be assessed in isolation.

It has important relationships with:

```text
ESC4
ESC6
ESC10
ESC14
ESC16
```

For example:

```text
ESC4
 |
 v
Template Modification
 |
 v
ESC9
 |
 v
No SID Extension
 |
 v
ESC10
 |
 v
Weak Mapping
```

can represent a much more meaningful attack chain than any one ESC condition alone.

For penetration testers, read-only evidence should be preferred. If active validation is required, two dedicated test accounts provide a much safer model than manipulating a production administrator's UPN.

For defenders, the preferred configuration is straightforward:

```text
Authentication Certificate
        |
        v
SID Security Extension Present
        |
        v
Strong Certificate Mapping
```

rather than relying on weaker name-based identity information.

The central ESC9 question is therefore not merely:

```text
Is NO_SECURITY_EXTENSION Enabled?
```

It is:

```text
What prevents a certificate without its
requester's SID from mapping to a different
Active Directory security principal?
```

That is the distinction between identifying the ESC9 configuration and demonstrating its actual security impact.
