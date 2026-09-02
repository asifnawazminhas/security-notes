# AD CS ESC2 - Any Purpose and Unrestricted Certificate Templates

ESC2 is an Active Directory Certificate Services (AD CS) privilege escalation condition involving certificate templates that issue certificates with excessively broad certificate purposes.

The two configurations most commonly associated with ESC2 are:

```text
Any Purpose EKU
```

or:

```text
No EKU
```

The Any Purpose EKU is:

```text
2.5.29.37.0
```

A certificate issued with an unrestricted purpose can potentially be used for multiple security-sensitive functions rather than being constrained to one intended use.

Depending on the certificate, template, CA, trust configuration, and available target templates, this may include:

```text
Client Authentication
Server Authentication
Enrollment Agent Functionality
Other Certificate-Based Trust Functions
```

A simplified ESC2 relationship is:

```text
Low-Privileged Principal
        |
        v
Can Enroll
        |
        v
Certificate Template
        |
        +--> Any Purpose
        |
        OR
        |
        +--> No EKU
        |
        v
Broadly Usable Certificate
        |
        v
Additional Certificate Trust Paths
```

One important escalation path is the use of an unrestricted certificate as an enrollment agent against a compatible target template:

```text
Low-Privileged User
        |
        v
ESC2 Template
        |
        v
Any Purpose Certificate
        |
        v
Enrollment Agent Function
        |
        v
Compatible Target Template
        |
        v
Certificate for Another Identity
```

ESC2 should therefore be understood as a problem of:

```text
Excessive Certificate Capability
```

rather than simply:

```text
Bad EKU
```

!!! warning "Authorised testing only"
    Requesting certificates, using certificates as enrollment-agent credentials, requesting certificates on behalf of other identities, or authenticating with issued certificates are active actions. Begin with read-only template and permission enumeration. Where active validation is required, use dedicated assessment identities and stop once sufficient evidence has been obtained. Treat PFX files and private keys as credentials.

---

# ESC2 Concept

Certificate EKUs are intended to constrain how a certificate can be used.

For example:

```text
Certificate
    |
    v
Server Authentication
```

should normally be used for a different purpose than:

```text
Certificate
    |
    v
Code Signing
```

or:

```text
Certificate
    |
    v
Client Authentication
```

ESC2 occurs when those restrictions become excessively broad.

Conceptually:

```text
Certificate
    |
    v
Any Purpose
    |
    v
Multiple Security-Sensitive Uses
```

---

# Extended Key Usage

Extended Key Usage:

```text
EKU
```

is a certificate extension describing the purposes for which a certificate's public key is intended to be used.

Examples include:

```text
Server Authentication
Client Authentication
Code Signing
Secure Email
Time Stamping
Smart Card Logon
Certificate Request Agent
```

Certificate applications can use these restrictions when determining whether a certificate is acceptable for a particular purpose.

---

# Why EKUs Matter

A narrowly scoped certificate might look like:

```text
Certificate
    |
    v
Server Authentication
    |
    X
Enrollment Agent
```

A broadly scoped certificate can instead create:

```text
Certificate
    |
    +--> Authentication
    |
    +--> Enrollment Workflows
    |
    +--> Other Certificate Uses
```

depending on the certificate and application.

The principle is:

```text
Certificate Capability
        |
        v
Should Match Business Requirement
```

---

# Any Purpose EKU

The EKU most commonly associated with ESC2 is:

```text
Any Purpose
```

with OID:

```text
2.5.29.37.0
```

Conceptually:

```text
Any Purpose
     |
     v
Certificate Usage Is Not Narrowly Restricted
```

This can make the certificate substantially more powerful than an application-specific certificate.

---

# No EKU

A certificate template with no EKU restriction also requires careful review.

In the ESC2 context, this is commonly described as:

```text
Subordinate CA
```

or:

```text
No EKUs
```

The important point is:

```text
No EKU
   |
   X
No Certificate Capability
```

It can instead mean that certificate usage is not restricted by an EKU extension.

---

# Any Purpose vs No EKU

A useful conceptual distinction is:

```text
Any Purpose
     |
     v
Explicitly Broad Purpose
```

versus:

```text
No EKU
     |
     v
No EKU-Based Usage Restriction
```

Both deserve security review.

However, their exact behaviour and implications are not identical in every application.

---

# Subordinate CA Context

Templates without EKUs are often discussed in ESC2 literature as:

```text
Subordinate CA
```

certificate templates.

A subordinate CA certificate is especially security-sensitive because a CA certificate can potentially sign additional certificates.

Conceptually:

```text
Subordinate CA Certificate
          |
          v
Certificate Signing Capability
          |
          v
Additional Certificates
```

This creates a broader trust concern than ordinary client authentication.

---

# Trust Still Matters

Obtaining a subordinate CA certificate does not automatically mean every certificate signed by it will be accepted for Active Directory authentication.

The trust path matters.

Conceptually:

```text
Attacker-Controlled Subordinate CA
          |
          v
Signs Certificate
          |
          v
Is CA Trusted for Intended Purpose?
          |
          +--> Yes
          |
          +--> No
```

For domain authentication, enterprise authentication trust and certificate mapping remain relevant.

---

# NTAuthCertificates

The enterprise:

```text
NTAuthCertificates
```

store is particularly important for Active Directory certificate authentication.

Conceptually:

```text
CA Certificate
      |
      v
Enterprise Authentication Trust
      |
      v
Certificate-Based Domain Authentication
```

A newly obtained subordinate CA certificate is not automatically added to enterprise authentication trust.

Therefore:

```text
Subordinate CA Certificate
          |
          X
Automatic Domain Authentication Trust
```

---

# ESC2 Is Still Dangerous Without Domain Authentication

Even when a subordinate CA certificate cannot immediately be used for Active Directory logon, certificate-signing capability may affect other systems.

Potential certificate trust consumers can include:

```text
TLS
Internal Applications
IPsec
Federation Infrastructure
Network Authentication
Application-Specific PKI
```

The actual impact depends on which trust stores and certificate policies accept the resulting chain.

---

# Classic ESC2 Conditions

A practical ESC2 candidate usually involves:

```text
Enterprise CA
      |
      v
Template Published
      |
      v
Low-Privileged Principal Can Enroll
      |
      v
Any Purpose or No EKU
      |
      v
No Effective Issuance Barrier
```

Important conditions include:

```text
CA Enrollment Access
Template Enrollment Access
Manager Approval Disabled
No Required Authorized Signature
Any Purpose or No EKU
```

---

# Condition 1 - Enterprise CA

The template must be published by a CA from which the attacker can actually enroll.

Conceptually:

```text
Template Exists
      |
      X
Certificate Can Be Obtained
```

Instead:

```text
Template Exists
      |
      v
CA Publishes Template
      |
      v
Requester Has Enrollment Access
```

---

# Condition 2 - Enrollment Rights

The attacker's effective security context must be able to enroll.

Common broad groups include:

```text
Domain Users
Authenticated Users
Domain Computers
Everyone
Large Business Groups
```

Broad enrollment is especially dangerous when the resulting certificate has unrestricted purposes.

---

# Effective Enrollment

Do not consider only direct ACEs.

An effective path may be:

```text
alice
  |
  v
Domain Users
  |
  v
PKI Users
  |
  v
Enroll
  |
  v
ESC2 Template
```

Nested groups must therefore be resolved.

---

# Condition 3 - Manager Approval

A template may require:

```text
CA Certificate Manager Approval
```

The workflow then becomes:

```text
Request
   |
   v
Pending
   |
   v
CA Manager
   |
   +--> Approve
   |
   +--> Deny
```

This can interrupt straightforward ESC2 abuse.

---

# Condition 4 - Authorized Signatures

A template may require an authorised signature before issuance.

Conceptually:

```text
Request
   |
   v
Required Signature
   |
   X
Requester Cannot Satisfy Requirement
```

This also affects exploitability.

---

# Condition 5 - Unrestricted Certificate Purpose

The defining ESC2 condition is:

```text
Any Purpose
```

or:

```text
No EKU
```

combined with accessible enrollment and insufficient issuance restrictions.

---

# ESC2 Does Not Require Supply in the Request

An important distinction from ESC1 is that ESC2 does not fundamentally depend on:

```text
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT
```

The ESC2 certificate may initially represent:

```text
The Requester
```

rather than another arbitrary identity.

Conceptually:

```text
alice
  |
  v
ESC2 Template
  |
  v
Any Purpose Certificate for Alice
```

The broad capability of that certificate creates the additional attack paths.

---

# ESC1 vs ESC2

ESC1:

```text
Requester
   |
   v
Controls Certificate Identity
   |
   v
Authentication Certificate
   |
   v
Another Account
```

ESC2:

```text
Requester
   |
   v
Obtains Broad-Purpose Certificate
   |
   v
Certificate Has Excessive Capabilities
```

The weaknesses are related but different.

---

# ESC2 and Enrollment Agents

One of the most important ESC2 relationships is:

```text
Any Purpose
     |
     v
Certificate Request Agent Capability
```

An unrestricted certificate may be usable in certificate enrollment-agent workflows under suitable conditions.

This creates a connection between:

```text
ESC2
```

and:

```text
ESC3
```

---

# Certificate Request Agent

The Certificate Request Agent EKU is:

```text
1.3.6.1.4.1.311.20.2.1
```

It is associated with requesting certificates on behalf of another identity.

The normal model is:

```text
Enrollment Agent
      |
      v
Request on Behalf of User
      |
      v
Certificate for User
```

An Any Purpose certificate can satisfy broader usage checks in certain enrollment-agent scenarios.

---

# ESC2 Two-Stage Path

A common conceptual ESC2 escalation path is:

```text
Stage 1

Low-Privileged User
        |
        v
ESC2 Template
        |
        v
Any Purpose Certificate
```

followed by:

```text
Stage 2

Any Purpose Certificate
        |
        v
Enrollment Agent Use
        |
        v
Compatible Target Template
        |
        v
Certificate for Another Identity
```

The second stage requires a compatible target template and enrollment configuration.

---

# Target Template

An ESC2 certificate alone does not prove that arbitrary user impersonation is possible.

The assessment must determine whether there is a target template that can participate in the enrollment-agent workflow.

Conceptually:

```text
ESC2 Certificate
       |
       v
Enrollment Agent
       |
       v
Compatible Target Template?
       |
       +--> No -> Escalation Path Stops
       |
       +--> Yes -> Continue Analysis
```

---

# Schema Version Matters

Certificate template schema version matters in enrollment-agent scenarios.

A particularly important historical observation is that:

```text
Schema Version 1
```

templates do not provide the same issuance-requirement controls introduced with later template versions.

This can make some version 1 templates particularly relevant as ESC2 target templates.

---

# Version 1 Templates

Version 1 templates have fewer configurable issuance controls than later templates.

Conceptually:

```text
Version 1 Template
       |
       v
Limited Modern Issuance Controls
```

This matters when assessing enrollment-agent paths.

Do not assume every version 1 template is vulnerable.

---

# Version 2+ Templates

Later template versions support additional issuance requirements.

These can include:

```text
Authorized Signatures
Application Policies
Other Issuance Controls
```

An enrollment-agent path against a version 2 or later template may therefore require additional conditions.

---

# One Template May Sometimes Play Multiple Roles

Certain configurations can create situations where an unrestricted template is useful both as:

```text
Initial ESC2 Certificate Source
```

and:

```text
Enrollment-Agent Target
```

However, this is configuration-dependent.

Do not assume every Any Purpose template provides a complete privilege escalation path by itself.

---

# Authentication as the Requester

An unrestricted certificate may also be usable to authenticate as the account to which it was legitimately issued.

Conceptually:

```text
alice
  |
  v
ESC2 Certificate
  |
  v
Certificate Authentication
  |
  v
alice
```

This does not by itself provide privilege escalation.

However, it can create an additional reusable credential for the account.

---

# Certificate Persistence

An issued authentication-capable certificate may remain useful even after:

```text
Password Change
```

depending on certificate validity and revocation.

Conceptually:

```text
Certificate
    |
    v
Password Changed
    |
    X
Certificate Automatically Removed
```

This makes unrestricted certificates relevant to credential persistence as well as privilege escalation.

---

# Certificate Capabilities

When reviewing an ESC2 certificate, ask:

```text
Can It Authenticate?
Can It Act as an Enrollment Agent?
Can It Sign Certificates?
Can It Be Used for TLS?
Can It Be Used by Other Enterprise Applications?
```

Do not restrict the assessment to Kerberos.

---

# Any Purpose Is Not Equivalent to Automatic Privilege Escalation

The following conclusion is incomplete:

```text
Any Purpose
    |
    v
Domain Admin
```

The correct model is:

```text
Any Purpose
    |
    v
Broad Certificate Capability
    |
    v
Available Trust / Enrollment Path
    |
    v
Resulting Privilege
```

---

# Enumerating ESC2 with Certipy

Certipy can identify templates with unrestricted certificate purposes.

Begin with:

```bash
certipy --help
```

and:

```bash
certipy find -h
```

A typical read-only authenticated enumeration pattern is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Use an approved assessment identity.

---

# Review Certipy Output

Look for template information such as:

```text
Template Name
Enabled
Certificate Authorities
Enrollment Rights
Extended Key Usage
Certificate Application Policies
Manager Approval
Authorized Signatures
ESC2
```

Exact labels depend on the Certipy version.

---

# Certipy ESC2 Candidate

A tool result should be treated as:

```text
ESC2 Candidate
```

until manually validated.

Use:

```text
Certipy
   |
   v
Potential ESC2
   |
   v
Verify EKU
   |
   v
Verify Enrollment
   |
   v
Verify Publication
   |
   v
Verify Issuance Controls
   |
   v
Identify Useful Certificate Path
```

---

# Native PowerShell Enumeration

Locate the certificate-template container:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage |
    Select-Object Name,DisplayName,pKIExtendedKeyUsage
```

---

# Find Any Purpose Templates

The Any Purpose OID is:

```text
2.5.29.37.0
```

Search for it:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage |
    Where-Object {
        $_.pKIExtendedKeyUsage -contains '2.5.29.37.0'
    } |
    Select-Object Name,DisplayName,pKIExtendedKeyUsage
```

---

# Find Templates Without EKUs

A useful read-only triage query is:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage |
    Where-Object {
        -not $_.pKIExtendedKeyUsage
    } |
    Select-Object Name,DisplayName
```

Review these templates carefully rather than automatically labelling all of them exploitable.

---

# Combined ESC2 Candidate Search

A simple candidate query is:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage |
    Where-Object {
        (-not $_.pKIExtendedKeyUsage) -or
        ($_.pKIExtendedKeyUsage -contains '2.5.29.37.0')
    } |
    Select-Object Name,DisplayName,pKIExtendedKeyUsage
```

This finds candidate templates only.

It does not check:

```text
Publication
Enrollment
Approval
Signatures
Effective Permissions
Target Templates
```

---

# Verify CA Publication

Enumerate Enterprise CAs:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Select-Object Name,dNSHostName,certificateTemplates
```

Confirm the candidate template is actually published.

---

# Find Which CA Publishes the Candidate

```powershell
$templateName = 'CorpAnyPurpose'

$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Where-Object {
        $_.certificateTemplates -contains $templateName
    } |
    Select-Object Name,dNSHostName
```

---

# Enumerate Template Schema Version

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Template-Schema-Version' |
    Select-Object Name,'msPKI-Template-Schema-Version'
```

This becomes especially relevant when analysing enrollment-agent target templates.

---

# Enumerate Issuance Requirements

Retrieve:

```text
msPKI-Enrollment-Flag
msPKI-RA-Signature
msPKI-RA-Application-Policies
```

with:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Enrollment-Flag','msPKI-RA-Signature','msPKI-RA-Application-Policies' |
    Select-Object Name,'msPKI-Enrollment-Flag','msPKI-RA-Signature','msPKI-RA-Application-Policies'
```

Interpret raw flags using Microsoft documentation or trusted AD CS tooling.

---

# Enumerate Template ACL

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpAnyPurpose,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,IsInherited
```

Determine effective enrollment rather than simply reading principal names.

---

# Template Owner

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpAnyPurpose,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Owner
```

Unexpected template ownership should be reviewed.

---

# PowerView

PowerView can assist with ACL analysis:

```powershell
Get-DomainObjectAcl -Identity 'CN=CorpAnyPurpose,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' -ResolveGUIDs
```

Review:

```text
Enroll
Autoenroll
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

as appropriate.

---

# LDAP Enumeration from Linux

Enumerate relevant template attributes:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(objectClass=pKICertificateTemplate)' \
    cn \
    displayName \
    pKIExtendedKeyUsage \
    msPKI-Template-Schema-Version \
    msPKI-Enrollment-Flag \
    msPKI-RA-Signature \
    msPKI-RA-Application-Policies
```

This is useful for independent verification of automated tooling.

---

# BloodHound

BloodHound can help answer:

```text
Who Can Enroll?
Who Controls Those Principals?
Who Can Modify the Template?
Which Privilege Paths Follow?
```

An indirect path might be:

```text
alice
  |
  v
AddMember
  |
  v
PKI-Users
  |
  v
Enroll
  |
  v
ESC2 Template
```

See:

[BloodHound](../bloodhound.md)

---

# Certify

Modern Certify versions can also enumerate AD CS vulnerabilities.

For Certify 2.x, begin with:

```text
Certify.exe --help
```

and inspect the available template-enumeration options.

Certify 2.0 introduced clearer vulnerability classification and filters for:

```text
Enabled Templates
Client Authentication
Vulnerable Templates
Requester-Supplied Subject
Enrollment Agent Targets
Manager Approval
```

Use syntax appropriate to the installed version.

---

# Certify ESC2 Enumeration

A current Certify 2.x enumeration pattern is:

```text
Certify.exe enum-templates --filter-enabled --filter-vulnerable --hide-admins
```

Review results for:

```text
ESC2
Any Purpose
Subordinate CA
No EKUs
Enrollment Rights
Manager Approval
Authorized Signatures
```

Treat automated results as candidates requiring manual verification.

---

# Tool Correlation

A strong assessment uses:

```text
Certipy
   +
Certify
   +
LDAP
   +
ACL Analysis
   +
BloodHound
```

where appropriate.

The purpose is not to maximize tool count.

The purpose is to independently validate:

```text
Configuration
Permissions
Publication
Attack Path
```

---

# Finding the Second-Stage Target

If evaluating the enrollment-agent path, enumerate target templates separately.

Ask:

```text
Which Templates Can Be Requested on Behalf of Another User?
```

Then determine:

```text
Is the Template Published?
Can It Authenticate?
What Schema Version Is It?
What Issuance Requirements Exist?
Are Enrollment Agent Restrictions Configured?
```

---

# Enrollment Agent Restrictions

Enterprise CAs can restrict enrollment-agent behaviour.

Conceptually:

```text
Enrollment Agent
      |
      v
CA Restrictions
      |
      +--> Which Agent?
      |
      +--> Which Target Template?
      |
      +--> Which Target User?
```

These restrictions can materially affect ESC2 exploitation.

---

# Do Not Ignore CA Restrictions

The following is incomplete:

```text
Any Purpose Certificate
        |
        v
Can Request for Anyone
```

Instead:

```text
Any Purpose Certificate
        |
        v
Enrollment Agent Capability
        |
        v
Target Template
        |
        v
CA Restrictions
        |
        v
Issuance Result
```

---

# ESC2 and ESC3

ESC2 and ESC3 can converge on similar second-stage behaviour.

ESC2 starts with:

```text
Any Purpose / No EKU
```

while ESC3 starts with:

```text
Certificate Request Agent EKU
```

Conceptually:

```text
ESC2 Certificate
      |
      +--> Broad Capability
      |
      v
Enrollment Agent Use
```

versus:

```text
ESC3 Certificate
      |
      +--> Explicit Enrollment Agent Capability
      |
      v
Enrollment Agent Use
```

---

# ESC2 and ESC1

ESC1 generally allows the requester to influence the identity directly in the original request.

ESC2 may instead involve:

```text
First Certificate
       |
       v
Enrollment Agent
       |
       v
Second Certificate
```

This is an important operational distinction.

---

# ESC2 and ESC4

If an attacker can modify a template:

```text
ESC4
```

they may potentially introduce:

```text
Any Purpose
```

or remove restrictive EKUs.

The initial weakness is still:

```text
Template Control
```

rather than ESC2.

---

# ESC2 and ESC7

Control over the CA can affect:

```text
Template Publication
Manager Approval
Certificate Issuance
CA Security
```

and may expose additional paths.

The root finding should identify the actual CA permission weakness.

---

# ESC2 and Golden Certificates

ESC2 involving a subordinate CA should not be confused with:

```text
Golden Certificate
```

A Golden Certificate generally refers to certificate forgery after compromise of an already trusted CA signing key.

ESC2 instead concerns:

```text
Certificate Enrollment
```

through a misconfigured template.

---

# ESC2 and PKINIT

If an ESC2 certificate can be used for client authentication:

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
TGT
```

may provide Kerberos authentication as the certificate's mapped identity.

Certificate mapping and current Domain Controller hardening remain relevant.

---

# Certificate Mapping

As with ESC1, modern certificate authentication should not be analysed using outdated assumptions.

Review:

```text
Certificate Identity
SID Security Extension
Certificate Mapping
KDC Behaviour
Domain Controller Patch Level
```

The fact that a certificate is broadly usable does not mean it automatically maps to an arbitrary privileged account.

---

# Controlled Validation

The preferred ESC2 validation model is:

```text
Enumerate Template
       |
       v
Confirm Any Purpose / No EKU
       |
       v
Confirm Enrollment
       |
       v
Confirm Publication
       |
       v
Confirm Issuance Requirements
       |
       v
Request Test Certificate if Needed
       |
       v
Inspect Certificate
       |
       v
Stop
```

Only continue into enrollment-agent testing if that impact specifically requires validation.

---

# Certificate Request

If active certificate enrollment is authorised, first inspect the installed Certipy syntax:

```bash
certipy req -h
```

The assessment normally requires:

```text
CA
Template
Approved Identity
Authentication Material
```

Use a dedicated assessment identity where possible.

---

# Do Not Immediately Request a Privileged Certificate

For ESC2, first prove:

```text
Low-Privileged User
      |
      v
Can Obtain Broad-Purpose Certificate
```

Then separately determine whether a second-stage escalation path exists.

This provides cleaner evidence and reduces unnecessary impact.

---

# Inspect the Issued Certificate

On Windows:

```cmd
certutil -dump test.cer
```

Review:

```text
Subject
Issuer
Serial Number
Validity
Extended Key Usage
Certificate Template
Extensions
```

For a PFX, avoid exposing the private key in screenshots or reports.

---

# OpenSSL Inspection

For a non-sensitive certificate file:

```bash
openssl x509 -in certificate.pem -text -noout
```

Review:

```text
X509v3 Extended Key Usage
Basic Constraints
Subject
Issuer
Validity
```

---

# Any Purpose Evidence

Useful evidence includes:

```text
Template Name
Published CA
Enrollment Principal
Any Purpose OID
Manager Approval
Authorized Signatures
Certificate Serial Number
Issued EKUs
```

The private key is not required as report evidence.

---

# No-EKU Evidence

For a template with no EKU, record:

```text
Template Name
No EKU Restriction
Basic Constraints
Template Purpose
CA Publication
Enrollment Rights
Issuance Requirements
```

Do not describe it as a trusted subordinate CA until the actual certificate and trust relationship have been established.

---

# Second-Stage Validation

If the engagement explicitly requires proving an enrollment-agent path, use:

```text
Dedicated Test Identity A
        |
        v
ESC2 Certificate
        |
        v
Request on Behalf of
        |
        v
Dedicated Test Identity B
```

This proves the identity boundary without using a production administrator.

---

# Certipy On-Behalf-Of Functionality

Certipy versions that support enrollment-agent workflows expose relevant options through the certificate request command.

Always inspect:

```bash
certipy req -h
```

for the installed release.

Do not copy old syntax without verification.

---

# Stop After Authentication Proof

If a second certificate successfully authenticates as the approved target identity:

```text
Certificate
    |
    v
Authentication Success
    |
    v
STOP
```

Do not proceed to:

```text
Credential Dumping
DCSync
Remote Command Execution
Persistence
```

unless separately required by the engagement.

---

# Detection

ESC2 detection should cover:

```text
Template Configuration
Template Changes
Certificate Enrollment
Enrollment-Agent Activity
Certificate Authentication
Subordinate CA Issuance
```

---

# Inventory Unrestricted Templates

Defenders should identify all templates with:

```text
Any Purpose
```

or:

```text
No EKU
```

and determine whether the broad capability is genuinely required.

---

# Correlate Enrollment Rights

Prioritise templates where unrestricted purposes combine with:

```text
Domain Users
Authenticated Users
Everyone
Domain Computers
Large Unprivileged Groups
```

---

# Monitor Template Changes

Certificate-template modifications can generate:

```text
5136
```

when appropriate Directory Service Changes auditing is configured.

Monitor changes to:

```text
pKIExtendedKeyUsage
msPKI-Certificate-Application-Policy
msPKI-Enrollment-Flag
msPKI-RA-Signature
nTSecurityDescriptor
```

---

# Detect EKU Changes

A particularly suspicious sequence is:

```text
Restricted EKU
      |
      v
Template Modification
      |
      v
Any Purpose
      |
      v
Certificate Enrollment
```

Correlate the template change with subsequent issuance.

---

# Detect EKU Removal

Also monitor:

```text
Existing EKUs
      |
      v
Removed
      |
      v
No EKU
```

Removing restrictions can be as important as adding:

```text
Any Purpose
```

---

# Monitor Enrollment-Agent Activity

Where enrollment agents are legitimately used, baseline:

```text
Approved Enrollment Agents
Approved Target Templates
Approved Target Users
Normal Enrollment Hosts
Normal Enrollment Times
```

Unexpected on-behalf-of enrollment should be investigated.

---

# Monitor Certificate Issuance

Record and correlate:

```text
Requester
Template
Subject
SAN
Serial Number
Issuer
Issue Time
Validity
```

High-risk templates should receive stronger monitoring.

---

# Monitor Subordinate CA Certificates

Subordinate CA certificate issuance should be rare in most environments.

Unexpected issuance can indicate a serious PKI event.

Alert on:

```text
Unexpected Subordinate CA Request
Unexpected Subordinate CA Issuance
Unexpected New CA Chain
```

---

# Certificate Authentication Monitoring

If an ESC2 certificate is used for authentication, correlate:

```text
Certificate Issuance
       |
       v
Certificate Authentication
       |
       v
Account
       |
       v
Source Host
```

Unexpected authentication using newly issued broad-purpose certificates warrants investigation.

---

# Hardening ESC2

The primary defensive principle is:

```text
Do Not Issue More Certificate Capability Than Required
```

A template should contain only the certificate purposes required by its business function.

---

# Remove Any Purpose

Where unnecessary:

```text
Any Purpose
    |
    v
Remove
```

and replace it with narrowly scoped EKUs.

For example:

```text
Any Purpose
```

might become:

```text
Server Authentication
```

if the certificate is only intended for TLS servers.

---

# Avoid Unrestricted No-EKU Templates

Do not expose templates with unrestricted certificate purpose to broad enrollment populations.

Subordinate CA templates should be tightly controlled.

---

# Restrict Enrollment

Replace:

```text
Authenticated Users
```

with a dedicated group where possible.

Example:

```text
PKI-Approved-Service-Certificate-Users
```

Only principals with a documented business requirement should be able to enroll.

---

# Require Manager Approval

For sensitive certificate purposes:

```text
CA Certificate Manager Approval
```

can provide an additional control.

The approval workflow must itself be protected.

---

# Require Authorized Signatures

Where appropriate, require authorised signatures before certificate issuance.

This can reduce abuse of sensitive enrollment workflows.

---

# Enrollment Agent Restrictions

Where enrollment-agent functionality is required, configure restrictions controlling:

```text
Which Agents
Which Templates
Which Target Identities
```

Do not allow unrestricted enrollment-agent behaviour without a documented requirement.

---

# Protect Template ACLs

Restrict:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

on certificate templates.

Otherwise an attacker may be able to create an ESC2-like configuration even after the original template has been hardened.

---

# Unpublish Unnecessary Templates

If a template is no longer needed:

```text
Remove from Issuing CA
```

after confirming production dependencies.

This prevents new enrollment while allowing a controlled retirement process.

---

# Do Not Modify Production Templates Blindly

Before changing an EKU, determine which systems consume the template.

Possible dependencies include:

```text
TLS
VPN
Wi-Fi
IPsec
Applications
Device Authentication
Federation
```

A certificate template change can cause significant operational impact.

---

# Certificate Lifetime

Review certificate validity periods.

A broad-purpose certificate valid for:

```text
5 Years
```

creates a larger exposure window than one valid for:

```text
1 Day
```

Use the shortest operationally appropriate lifetime.

---

# Private-Key Protection

Broad-purpose certificates should also have strong private-key protection.

Review:

```text
Exportability
Key Storage Provider
Hardware Protection
ACLs
PFX Handling
Backup
```

A powerful certificate with an easily exportable private key increases credential portability.

---

# Incident Response

If ESC2 abuse is suspected:

```text
Identify Template
      |
      v
Identify CA
      |
      v
Identify Requester
      |
      v
Identify ESC2 Certificate
      |
      v
Identify Subsequent Certificate Requests
      |
      v
Identify Authentication / Trust Use
      |
      v
Revoke Certificates
      |
      v
Fix Template
```

---

# Identify Initial Certificate

Collect:

```text
Serial Number
Thumbprint
Subject
Issuer
Template
Issue Time
Expiration
EKUs
Basic Constraints
Requester
```

---

# Search for Second-Stage Certificates

If the ESC2 certificate could act as an enrollment agent, investigate whether it was subsequently used to request certificates for other identities.

Conceptually:

```text
ESC2 Certificate
      |
      v
Enrollment-Agent Activity
      |
      v
Additional Certificates
```

---

# Identify Target Accounts

Review whether subsequent certificates represent:

```text
Privileged Users
Service Accounts
Administrators
Domain Controllers
PKI Administrators
```

---

# Revoke Malicious Certificates

Revoke:

```text
Initial ESC2 Certificate
```

and any:

```text
Derived Certificates
```

that were issued through the malicious chain.

Ensure revocation information is published and available to relying parties.

---

# Password Reset Is Not Enough

If a certificate has already been issued:

```text
Password Reset
      |
      X
Certificate Automatically Revoked
```

Address the certificate credential separately.

---

# Subordinate CA Incident

If an attacker obtained a subordinate CA certificate and private key, incident response may require broader trust analysis.

Investigate:

```text
Certificates Signed by Subordinate CA
Trust Stores
NTAuthCertificates
Application Trust
TLS Trust
Federation Trust
IPsec Trust
```

The scope can extend beyond Active Directory logon.

---

# Reporting ESC2

Avoid reporting only:

```text
ESC2
```

Use a title describing the actual trust weakness.

Examples:

```text
Low-Privileged Users Can Obtain Unrestricted Any Purpose Certificates
```

```text
Broad Enrollment Rights Expose an Unrestricted Certificate Template
```

```text
Certificate Template Issues Unrestricted Certificates to Unprivileged Domain Users
```

---

# Example Finding

```text
Finding:
Low-Privileged Users Can Obtain Unrestricted Any Purpose Certificates

Affected CA:
CORP-CA01

Affected Template:
CorpAnyPurpose

Affected Principal:
CORP\Domain Users

Description:
The CorpAnyPurpose certificate template is published by the CORP-CA01
Enterprise Certification Authority.

Members of CORP\Domain Users have enrollment rights on the template.

The template specifies the Any Purpose Extended Key Usage
(2.5.29.37.0), allowing certificates issued from the template to be
used for a broader range of purposes than required for a narrowly
scoped certificate.

Certificate manager approval is not required and the template does
not require an authorised signature before issuance.

The resulting certificate may therefore expose additional
authentication and certificate-enrollment trust paths depending on
the available target templates and CA configuration.

Impact:
An attacker who compromises a low-privileged domain account may be
able to obtain a broadly usable certificate.

Under suitable enrollment-agent and target-template conditions, the
certificate may participate in requests made on behalf of other
identities, potentially leading to privilege escalation.

Broad-purpose certificates may also affect other enterprise
certificate trust functions.

Recommendation:
Remove the Any Purpose EKU unless unrestricted certificate usage is
explicitly required.

Replace it with the minimum EKUs necessary for the template's
business function.

Restrict enrollment rights to dedicated authorised groups.

Review manager approval, authorised signature requirements,
enrollment-agent restrictions, certificate validity, and template
ACLs.

Review certificates previously issued from the affected template and
revoke certificates that were issued inappropriately.
```

---

# Severity Assessment

Severity should consider:

```text
Who Can Enroll?
      +
Certificate Capability
      +
Issuance Requirements
      +
Target Templates
      +
Enrollment Agent Restrictions
      +
Trust Relationships
      +
Resulting Privilege
      =
Severity
```

---

# High-Risk Example

```text
Domain User
   |
   v
Any Purpose Certificate
   |
   v
Enrollment Agent
   |
   v
Authentication Target Template
   |
   v
Privileged Identity Certificate
```

This can represent a significant privilege escalation path.

---

# Different Risk Example

```text
Domain User
   |
   v
Subordinate CA Certificate
   |
   v
Certificate Signing
   |
   v
Internal Application Trust
```

Even if Active Directory authentication is not immediately possible, other enterprise trust systems may be affected.

---

# Reduced-Risk Example

```text
Restricted PKI Administrators
        |
        v
Any Purpose Template
        |
        v
Strong Approval Workflow
```

The template may still deserve hardening, but exploitability and severity differ substantially from broad low-privileged enrollment.

---

# Evidence Checklist

For an ESC2 candidate record:

```text
CA Name
CA Host
Template Name
Template DN
Template Published
Template Schema Version
Enrollment Principal
Effective Enrollment Path
EKUs
Application Policies
Any Purpose OID
No-EKU Status
Basic Constraints
Manager Approval
Authorized Signatures
Enrollment Agent Restrictions
Template Owner
Template ACL
Certificate Validity
Issued Certificate Serial Number
Issued Certificate Thumbprint
Second-Stage Target Template
Authentication Result
Cleanup Result
```

Never include private keys in the report.

---

# ESC2 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Enumerate certificate templates
- [ ] Identify published templates
- [ ] Identify Any Purpose templates
- [ ] Identify templates with no EKUs
- [ ] Identify subordinate CA templates

## Certificate Purpose

- [ ] Review `pKIExtendedKeyUsage`
- [ ] Review certificate application policies
- [ ] Identify `2.5.29.37.0`
- [ ] Identify no-EKU templates
- [ ] Review Basic Constraints
- [ ] Determine intended business purpose
- [ ] Compare configured capability to intended capability

## Enrollment

- [ ] Identify Enroll rights
- [ ] Identify Autoenroll rights
- [ ] Resolve nested groups
- [ ] Identify broad enrollment
- [ ] Confirm effective enrollment
- [ ] Confirm CA publication

## Issuance Requirements

- [ ] Review manager approval
- [ ] Review authorized signatures
- [ ] Review `msPKI-RA-Signature`
- [ ] Review application-policy requirements
- [ ] Review enrollment-agent restrictions
- [ ] Review CA restrictions

## Template Version

- [ ] Record schema version
- [ ] Identify version 1 templates
- [ ] Identify version 2+ templates
- [ ] Review issuance requirements by version
- [ ] Identify possible enrollment-agent targets

## ACLs

- [ ] Review template owner
- [ ] Review GenericAll
- [ ] Review GenericWrite
- [ ] Review WriteProperty
- [ ] Review WriteDACL
- [ ] Review WriteOwner
- [ ] Review indirect group-control paths

## Tooling

- [ ] Enumerate with PowerShell
- [ ] Enumerate with LDAP
- [ ] Enumerate with Certipy
- [ ] Enumerate with Certify where available
- [ ] Review BloodHound
- [ ] Correlate results
- [ ] Verify tool versions
- [ ] Manually confirm automated ESC2 results

## Enrollment-Agent Path

- [ ] Determine whether ESC2 certificate can serve as enrollment agent
- [ ] Identify compatible target templates
- [ ] Review target template schema version
- [ ] Review target template EKUs
- [ ] Review target template issuance requirements
- [ ] Review CA enrollment-agent restrictions
- [ ] Determine which target identities are permitted
- [ ] Do not assume arbitrary impersonation

## Authentication

- [ ] Determine whether initial certificate supports authentication
- [ ] Review certificate mapping
- [ ] Review SID security extension
- [ ] Review PKINIT availability
- [ ] Review Domain Controller hardening
- [ ] Determine mapped identity
- [ ] Do not infer privilege escalation from Any Purpose alone

## Subordinate CA

- [ ] Determine whether certificate is a CA certificate
- [ ] Review Basic Constraints
- [ ] Review certificate-signing capability
- [ ] Review trust chain
- [ ] Review NTAuthCertificates
- [ ] Review application trust
- [ ] Review TLS trust
- [ ] Review other PKI consumers

## Validation

- [ ] Prefer read-only evidence first
- [ ] Use dedicated test identities
- [ ] Request only one certificate if required
- [ ] Inspect issued EKUs
- [ ] Protect PFX
- [ ] Record serial number
- [ ] Record thumbprint
- [ ] Test second-stage path only if required
- [ ] Avoid production privileged identities where possible
- [ ] Stop after sufficient proof

## Detection

- [ ] Inventory Any Purpose templates
- [ ] Inventory no-EKU templates
- [ ] Monitor template changes
- [ ] Monitor EKU changes
- [ ] Monitor EKU removal
- [ ] Monitor template ACL changes
- [ ] Monitor certificate issuance
- [ ] Monitor enrollment-agent activity
- [ ] Monitor subordinate CA issuance
- [ ] Correlate certificate authentication

## Hardening

- [ ] Remove unnecessary Any Purpose EKUs
- [ ] Avoid unrestricted no-EKU templates
- [ ] Use narrowly scoped EKUs
- [ ] Restrict enrollment
- [ ] Require approval where appropriate
- [ ] Require signatures where appropriate
- [ ] Configure enrollment-agent restrictions
- [ ] Protect template ACLs
- [ ] Unpublish unused templates
- [ ] Review certificate lifetime
- [ ] Protect private keys
- [ ] Review previously issued certificates

## Incident Response

- [ ] Identify affected template
- [ ] Identify CA
- [ ] Identify requester
- [ ] Identify initial ESC2 certificate
- [ ] Identify serial number
- [ ] Identify thumbprint
- [ ] Identify subsequent enrollment-agent requests
- [ ] Identify derived certificates
- [ ] Identify affected accounts
- [ ] Identify authentication activity
- [ ] Identify subordinate CA trust impact
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Fix template
- [ ] Fix enrollment rights
- [ ] Review other templates

## Cleanup

- [ ] Revoke test certificate where required
- [ ] Revoke derived test certificates
- [ ] Delete PFX files
- [ ] Delete private keys
- [ ] Remove temporary test identities
- [ ] Restore any approved temporary changes
- [ ] Verify certificates are no longer usable
- [ ] Record cleanup evidence

---

# ESC2 Testing Model

The normal EKU model is:

```text
Certificate
    |
    v
Specific EKU
    |
    v
Specific Purpose
```

The ESC2 model is:

```text
Certificate
    |
    v
Any Purpose / No EKU
    |
    v
Broad Certificate Capability
```

The candidate model is:

```text
Low-Privileged Principal
        |
        v
Enroll
        |
        v
Published Template
        |
        v
Any Purpose / No EKU
```

The two-stage escalation model is:

```text
Low-Privileged User
        |
        v
ESC2 Template
        |
        v
Any Purpose Certificate
        |
        v
Enrollment Agent
        |
        v
Target Template
        |
        v
Certificate for Another Identity
```

The target-template model is:

```text
ESC2 Certificate
       |
       v
Compatible Target?
       |
       +--> Published
       |
       +--> Appropriate Template Version
       |
       +--> Suitable Certificate Purpose
       |
       +--> Issuance Requirements Satisfied
       |
       +--> CA Restrictions Permit
```

The subordinate CA model is:

```text
No-EKU / SubCA Template
        |
        v
CA Certificate
        |
        v
Certificate Signing
        |
        v
Additional Trust Analysis
```

The trust model is:

```text
Signed Certificate
       |
       X
Automatically Trusted Everywhere
```

Instead:

```text
Signed Certificate
       |
       v
Certificate Chain
       |
       v
Trust Store
       |
       v
Application Policy
       |
       v
Accepted / Rejected
```

The authentication model is:

```text
ESC2 Certificate
       |
       v
Authentication Capability
       |
       v
Certificate Mapping
       |
       v
Mapped Identity
```

The persistence model is:

```text
Issued Certificate
       |
       v
Password Changed
       |
       X
Certificate Automatically Removed
```

The safe-assessment model is:

```text
Enumerate
   |
   v
Identify Any Purpose / No EKU
   |
   v
Confirm Enrollment
   |
   v
Confirm Publication
   |
   v
Review Issuance Controls
   |
   v
Review Target Templates
   |
   v
Request Test Certificate if Required
   |
   v
Validate Minimum Impact
   |
   v
Stop
   |
   v
Clean Up
```

The defensive model is:

```text
Specific EKUs
    +
Restricted Enrollment
    +
Strong Issuance Controls
    +
Enrollment Agent Restrictions
    +
Protected Template ACL
    +
Monitoring
    =
Reduced ESC2 Risk
```

The central ESC2 question is:

```text
Why does this principal need a certificate
that can be used for almost anything?
```

For penetration testers:

```text
Do Not Ask:
"Does Certipy say ESC2?"

Ask:
"What additional trust or enrollment capability
does this unrestricted certificate provide to
the principal who can obtain it?"
```

For defenders:

```text
Do Not Ask:
"Is Any Purpose technically supported?"

Ask:
"Does the business requirement justify granting
this enrollment population a certificate with
unrestricted capability?"
```

The complete ESC2 relationship is:

```text
Principal
   |
   v
Enrollment Rights
   |
   v
Certificate Template
   |
   v
Any Purpose / No EKU
   |
   v
Broad Certificate Capability
   |
   +--> Authentication
   |
   +--> Enrollment Agent
   |
   +--> Certificate Signing
   |
   +--> Other Trust Functions
   |
   v
Potential Privilege / Trust Impact
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC1:

[AD CS ESC1](esc1.md)

Active Directory ACL and ACE abuse:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

Active Directory groups:

[Active Directory Groups](../groups.md)

Kerberos:

[Kerberos](../kerberos.md)

Credential Access:

[Active Directory Credential Access](../credential-access.md)

BloodHound:

[BloodHound](../bloodhound.md)

The next AD CS page is:

```text
active-directory/ad-cs/esc3.md
```

---

# References

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Templates

[Microsoft - Certificate Template Concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Extended Key Usage

[Microsoft - Certificate Extended Key Usage](https://learn.microsoft.com/en-us/windows/win32/seccrypto/certificate-extended-key-usage){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Services Protocols

[Microsoft - Windows Client Certificate Enrollment Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Defender for Identity - Certificate Security Assessments

[Microsoft - Certificate Security Posture Assessments](https://learn.microsoft.com/en-us/defender-for-identity/security-posture-assessments/certificates){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - ESC2

[SpecterOps - ESC2 Misconfigured Any Purpose Templates](https://docs.specterops.io/ghostpack-docs/Certify.wik-mdx/esc2-misconfigured-any-purpose){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certificates and Pwnage and Patches, Oh My!

[SpecterOps - Certificates and Pwnage and Patches, Oh My!](https://specterops.io/blog/2022/11/09/certificates-and-pwnage-and-patches-oh-my/){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certify 2.0

[SpecterOps - Certify 2.0](https://specterops.io/blog/2025/08/11/certify-2-0/){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC2 is fundamentally a:

```text
Certificate Capability
```

problem.

Certificate templates should normally constrain certificates to the purposes required by the business.

For example:

```text
Web Server Certificate
        |
        v
Server Authentication
```

is easier to reason about than:

```text
Web Server Certificate
        |
        v
Any Purpose
```

The dangerous ESC2 relationship is:

```text
Low-Privileged Enrollment
        +
Unrestricted Certificate Purpose
        =
Excessive Trust
```

The resulting impact must then be determined.

It may involve:

```text
Authentication
Enrollment Agent Behaviour
Certificate Signing
Application Trust
Other PKI Functions
```

The most important ESC2 escalation model is:

```text
Low-Privileged User
        |
        v
Any Purpose Certificate
        |
        v
Enrollment Agent Capability
        |
        v
Compatible Target Template
        |
        v
Certificate for Another Identity
```

However:

```text
Any Purpose
    |
    X
Automatic Domain Admin
```

The complete path still depends on:

```text
Enrollment Rights
CA Publication
Issuance Requirements
Target Template
Template Version
Enrollment Agent Restrictions
Certificate Mapping
Resulting Identity
```

Templates with no EKU deserve equally careful review, especially when they can issue subordinate CA certificates.

The important trust distinction is:

```text
Can Sign Certificates
       |
       X
Automatically Trusted for Every Purpose
```

Trust chains, NTAuth, application policy, and relying-party configuration still matter.

For penetration testers, the correct question is:

```text
What can this unrestricted certificate
actually be used to do in this environment?
```

For defenders, the correct question is:

```text
Why is unrestricted certificate capability
being issued at all?
```

The safest design is:

```text
Specific Business Requirement
        |
        v
Specific Certificate Template
        |
        v
Minimum Required EKUs
        |
        v
Restricted Enrollment Population
        |
        v
Monitored Certificate Issuance
```

This applies the same least-privilege principle used elsewhere in Active Directory to the PKI trust model.

ESC2 demonstrates why certificate purpose is a security boundary rather than merely a certificate-management setting.
