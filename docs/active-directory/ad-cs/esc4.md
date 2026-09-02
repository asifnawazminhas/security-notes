# AD CS ESC4 - Vulnerable Certificate Template Access Control

ESC4 is an Active Directory Certificate Services (AD CS) privilege escalation condition involving insecure permissions on certificate template objects.

Certificate templates are Active Directory objects.

Like users, groups, computers, Group Policy Objects, and other directory objects, certificate templates have security descriptors that determine who can:

```text
Read
Enroll
Modify Properties
Modify Permissions
Take Ownership
Fully Control
```

a template.

ESC4 occurs when a principal has excessive control over a certificate template and can modify it into a configuration that enables another AD CS attack path.

A simplified ESC4 relationship is:

```text
Low-Privileged Principal
        |
        v
Excessive Template Permission
        |
        v
Certificate Template
        |
        v
Modify Security-Sensitive Properties
        |
        v
Create Vulnerable Enrollment Configuration
        |
        v
Request Certificate
        |
        v
Certificate-Based Privilege Escalation
```

Common dangerous permissions include:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

The important distinction is:

```text
ESC1 / ESC2 / ESC3
        |
        v
Template Is Already Misconfigured
```

versus:

```text
ESC4
        |
        v
Attacker Can Modify the Template
```

ESC4 is therefore fundamentally an:

```text
Active Directory Access Control
```

problem affecting PKI configuration.

!!! warning "Authorised testing only"
    Modifying a production certificate template can affect certificate enrollment across the forest and may disrupt authentication, autoenrollment, VPN, Wi-Fi, TLS, smart card, device, or application workflows. Begin with read-only ACL analysis. Do not modify production templates merely to prove ESC4. If active validation is explicitly required, use a dedicated test template or an approved temporary change, record the complete original configuration, make the minimum necessary change, and restore it immediately after testing.

---

# ESC4 Concept

The normal security model is:

```text
PKI Administrators
       |
       v
Manage Certificate Template
```

The dangerous model is:

```text
Low-Privileged User
       |
       v
Can Modify Certificate Template
```

The attacker may then change security-sensitive properties.

For example:

```text
Safe Template
     |
     v
Attacker Modifies Template
     |
     v
Supply Subject Enabled
     |
     v
Authentication EKU Added
     |
     v
Certificate Requested
```

This can transform an ACL weakness into an ESC1-style certificate path.

---

# Certificate Templates Are Active Directory Objects

Enterprise certificate templates are stored in the Configuration naming context.

The template container is:

```text
CN=Certificate Templates,
CN=Public Key Services,
CN=Services,
CN=Configuration,
DC=...
```

Conceptually:

```text
Active Directory Forest
        |
        v
Configuration
        |
        v
Services
        |
        v
Public Key Services
        |
        v
Certificate Templates
        |
        v
Individual Template Objects
```

Because the objects are stored in Active Directory, normal Active Directory ACL concepts apply.

---

# Forest-Wide Significance

Certificate templates are stored in the forest Configuration partition.

This means template security should not be viewed as a single-domain configuration issue.

Conceptually:

```text
Certificate Template
       |
       v
Configuration Partition
       |
       v
Forest-Wide PKI Configuration
```

A dangerous delegated permission may therefore have consequences beyond the domain containing the account that holds the permission.

---

# Template Security Descriptor

Each certificate template has a security descriptor containing:

```text
Owner
DACL
ACEs
Inheritance
Object-Specific Rights
```

The assessment should determine:

```text
Who Owns the Template?
Who Can Modify It?
Who Can Modify Its ACL?
Who Can Enroll?
```

---

# ESC4 Is Not Enroll Permission

This distinction is important.

The ability to:

```text
Enroll
```

does not mean the principal can modify the template.

Likewise:

```text
Read
```

does not mean the principal can modify it.

ESC4 concerns permissions that provide control over the template itself.

---

# Important Template Permissions

Potentially dangerous permissions include:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

Depending on the ACE and object scope, these rights can enable direct or indirect template control.

---

# GenericAll

`GenericAll` represents broad control over the object.

Conceptually:

```text
Principal
   |
   v
GenericAll
   |
   v
Certificate Template
   |
   +--> Modify Properties
   |
   +--> Modify Permissions
   |
   +--> Other Object Control
```

A low-privileged principal with `GenericAll` over a certificate template should receive immediate attention.

---

# GenericWrite

`GenericWrite` can permit modification of writable properties on the template.

Conceptually:

```text
Principal
   |
   v
GenericWrite
   |
   v
Security-Sensitive Template Attributes
```

This may be sufficient to alter certificate behaviour.

---

# WriteProperty

`WriteProperty` can be especially important when it applies to security-sensitive template attributes.

Examples include properties controlling:

```text
Subject Name
Extended Key Usage
Application Policies
Enrollment Flags
Issuance Requirements
Private-Key Behaviour
```

An object-specific ACE may grant permission over only particular attributes.

Therefore:

```text
WriteProperty
```

must be interpreted together with:

```text
ObjectType GUID
```

---

# WriteDACL

`WriteDACL` allows modification of the object's discretionary access control list.

Conceptually:

```text
Attacker
   |
   v
WriteDACL
   |
   v
Add New ACE
   |
   v
Grant Self Additional Rights
   |
   v
Control Template
```

For example:

```text
WriteDACL
    |
    v
Grant GenericAll
    |
    v
Modify Template
```

This makes `WriteDACL` a powerful indirect ESC4 primitive.

---

# WriteOwner

`WriteOwner` permits changing the owner of the object.

Object ownership matters because an owner can generally modify the object's DACL.

Conceptually:

```text
WriteOwner
    |
    v
Become Owner
    |
    v
Modify DACL
    |
    v
Grant Additional Rights
    |
    v
Modify Template
```

Therefore:

```text
WriteOwner
```

can become:

```text
WriteOwner
    ->
WriteDACL
    ->
Template Control
```

---

# Ownership

Always inspect the template owner.

Expected owners commonly involve appropriately privileged administrative groups.

Unexpected ownership by:

```text
Normal User
Service Account
Application Group
Legacy Administration Group
Broad Delegated Group
```

should be investigated.

---

# ESC4 Attack Chain

The complete ESC4 model is usually:

```text
Principal
   |
   v
Template Control
   |
   v
Modify Template
   |
   v
Create Another ESC Condition
   |
   v
Enroll
   |
   v
Certificate
   |
   v
Authentication / Trust Abuse
```

The modification alone is not normally the final objective.

---

# ESC4 to ESC1

One of the clearest ESC4 chains is:

```text
ESC4
 |
 v
Modify Template
 |
 +--> Enable Supply in the Request
 |
 +--> Add Authentication Capability
 |
 +--> Remove Issuance Restrictions
 |
 +--> Grant Enrollment if Required
 |
 v
ESC1-Like Configuration
```

The original root cause remains:

```text
ESC4
```

because template control made the vulnerable configuration possible.

---

# ESC4 to ESC2

Template control may also permit changes that create:

```text
Any Purpose
```

or remove restrictive certificate purposes.

Conceptually:

```text
ESC4
 |
 v
Modify EKUs
 |
 v
Any Purpose / No Restriction
 |
 v
ESC2-Like Configuration
```

---

# ESC4 to ESC3

An attacker controlling a template may potentially configure it to issue certificates with:

```text
Certificate Request Agent
```

capability.

Conceptually:

```text
ESC4
 |
 v
Modify Application Policy
 |
 v
Certificate Request Agent
 |
 v
ESC3-Style Capability
```

A compatible target template and CA configuration are still required for a complete ESC3 chain.

---

# ESC4 and Enrollment Rights

An attacker may control a template but initially lack enrollment rights.

For example:

```text
alice
  |
  v
GenericWrite
  |
  v
Template
```

but:

```text
alice
  |
  X
Enroll
```

The attacker may need another path to enrollment.

---

# ACL Modification Can Solve Enrollment

If the attacker has:

```text
WriteDACL
```

or sufficiently broad control, they may be able to grant enrollment rights to themselves or a controlled group.

Conceptually:

```text
Template Control
      |
      v
Modify DACL
      |
      v
Grant Enroll
```

This is another reason template ACL analysis must consider combinations of rights.

---

# Publication Still Matters

A certificate template can exist in Active Directory without being published by an issuing CA.

Conceptually:

```text
Vulnerable Template
       |
       X
Published
```

means the certificate cannot simply be requested from that CA.

Therefore ESC4 analysis should determine:

```text
Template Exists
      |
      v
Template Controlled
      |
      v
Published by Enterprise CA?
```

---

# Template Publication

Enterprise CAs publish a list of certificate templates they are configured to issue.

Conceptually:

```text
Enterprise CA
     |
     v
Published Templates
     |
     v
Certificate Enrollment
```

Template control and CA publication are separate security boundaries.

---

# ESC4 Does Not Automatically Give CA Control

Controlling a certificate template does not mean the attacker can:

```text
Publish Template to CA
Modify CA Configuration
Approve Pending Requests
Issue Arbitrary Certificates
Manage CA
```

Those are separate permissions.

This distinction becomes important when analysing ESC5 and ESC7.

---

# ESC4 vs ESC5

ESC4 concerns:

```text
Certificate Template Object Control
```

ESC5 concerns broader:

```text
PKI Object Control
```

such as dangerous permissions over other AD CS-related Active Directory objects.

The precise affected object should drive classification.

---

# ESC4 vs ESC7

ESC7 concerns dangerous permissions on the Certification Authority itself.

Conceptually:

```text
ESC4
Template Control
```

versus:

```text
ESC7
CA Control
```

Do not classify CA administrative permissions as ESC4.

---

# Security-Sensitive Template Attributes

Important template properties include:

```text
msPKI-Certificate-Name-Flag
msPKI-Enrollment-Flag
pKIExtendedKeyUsage
msPKI-Certificate-Application-Policy
msPKI-RA-Signature
msPKI-RA-Application-Policies
msPKI-Private-Key-Flag
pKIExpirationPeriod
pKIOverlapPeriod
nTSecurityDescriptor
```

The exact security impact depends on which properties the attacker can modify.

---

# Subject Name Configuration

The attribute:

```text
msPKI-Certificate-Name-Flag
```

controls important subject-name behaviour.

A particularly important setting is:

```text
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT
```

which can allow the requester to provide subject information in the certificate request.

This setting is central to ESC1 analysis.

---

# EKU Modification

Template control may permit modification of:

```text
pKIExtendedKeyUsage
```

or certificate application policies.

An attacker might attempt to introduce:

```text
Client Authentication
Smart Card Logon
Certificate Request Agent
Any Purpose
```

depending on the intended chain.

---

# Enrollment Flags

The attribute:

```text
msPKI-Enrollment-Flag
```

contains template enrollment settings.

These can influence behaviour such as:

```text
Pending Requests
Certificate Publication
Enrollment Behaviour
```

Raw bitmask values should be interpreted carefully.

---

# Authorized Signature Requirements

The attribute:

```text
msPKI-RA-Signature
```

can specify the number of required authorised signatures.

A secure template might require:

```text
1 or more authorized signatures
```

before issuance.

An attacker with sufficient template control may attempt to weaken such requirements.

---

# Application Policy Requirements

The attribute:

```text
msPKI-RA-Application-Policies
```

can define application policies associated with registration authority signatures.

These settings are particularly relevant to Enrollment Agent workflows.

---

# Private-Key Settings

The attribute:

```text
msPKI-Private-Key-Flag
```

controls aspects of private-key behaviour.

Security review should consider whether modifications could affect:

```text
Exportability
Archival
Key Protection
Key Reuse
```

depending on the template configuration.

---

# Certificate Validity

Template control can also affect certificate lifetime.

Relevant attributes include:

```text
pKIExpirationPeriod
pKIOverlapPeriod
```

Long-lived authentication certificates can increase persistence risk.

However, modifying validity alone does not constitute a complete privilege escalation path.

---

# Enumerating ESC4 with Certipy

Certipy can identify vulnerable certificate-template permissions.

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

# Certipy Vulnerable Templates

To focus on candidate vulnerabilities, review the options exposed by:

```bash
certipy find -h
```

Modern Certipy versions can identify templates where the current principal has dangerous permissions and classify applicable conditions such as:

```text
ESC4
```

Treat automated classifications as candidates requiring manual verification.

---

# What to Review in Certipy Output

Look for information such as:

```text
Template Name
Enabled
Certificate Authorities
Permissions
Enrollment Permissions
Object Control Permissions
Owner
ESC4
```

Exact labels can vary between Certipy releases.

---

# Certipy ACL Analysis

An ESC4 candidate might conceptually appear as:

```text
Template:
CorpUserCertificate

Object Control Permissions:
CORP\Helpdesk
    GenericAll

Vulnerabilities:
ESC4
```

The important evidence is:

```text
Who
  +
Which Permission
  +
Which Template
```

---

# Do Not Rely Only on the ESC Label

The assessment should independently establish:

```text
Principal
   |
   v
Effective Permission
   |
   v
Template Object
   |
   v
Security-Sensitive Modification Possible
```

This is stronger evidence than:

```text
Tool says ESC4
```

---

# Native PowerShell Enumeration

First locate the certificate-template container:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties displayName |
    Select-Object Name,DisplayName,DistinguishedName
```

---

# Inspect One Template

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpUserCertificate,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -Identity $templateDN -Properties *
```

This provides the template configuration but not a convenient effective-permission interpretation.

---

# Enumerate Template ACL

If the Active Directory PowerShell provider is available:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpUserCertificate,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

$acl = Get-Acl "AD:$templateDN"

$acl.Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

---

# Enumerate Template Owner

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpUserCertificate,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Owner
```

Unexpected ownership should be investigated.

---

# Search for Broad Rights

A useful triage query is:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ChildItem "AD:$templateBase" |
    ForEach-Object {
        $template = $_
        $acl = Get-Acl $template.PSPath

        $acl.Access |
            Where-Object {
                $_.AccessControlType -eq 'Allow' -and
                (
                    $_.ActiveDirectoryRights -match 'GenericAll' -or
                    $_.ActiveDirectoryRights -match 'GenericWrite' -or
                    $_.ActiveDirectoryRights -match 'WriteDacl' -or
                    $_.ActiveDirectoryRights -match 'WriteOwner'
                )
            } |
            Select-Object @{
                Name = 'Template'
                Expression = { $template.Name }
            }, IdentityReference,ActiveDirectoryRights,ObjectType,IsInherited
    }
```

This is a triage technique.

It does not replace effective-permission analysis.

---

# Why Effective Permissions Matter

An ACE might apply to:

```text
Domain Users
```

rather than directly to:

```text
alice
```

The effective path may be:

```text
alice
  |
  v
Domain Users
  |
  v
PKI Operators
  |
  v
GenericWrite
  |
  v
Template
```

Nested groups must therefore be considered.

---

# Deny ACEs

ACL analysis must also account for:

```text
Deny
```

entries.

The existence of an Allow ACE does not always mean the principal has the effective permission.

Consider:

```text
Explicit Allow
Inherited Allow
Explicit Deny
Object-Specific ACE
Group Membership
Ownership
```

when determining effective control.

---

# Object-Specific WriteProperty

Not every `WriteProperty` ACE gives control over every template property.

An ACE can target a particular attribute.

Conceptually:

```text
WriteProperty
      |
      v
ObjectType GUID
      |
      v
Specific Attribute
```

Therefore:

```text
WriteProperty
```

must not automatically be reported as full ESC4 without resolving the affected property.

---

# PowerView

PowerView can assist with resolving Active Directory ACLs.

For example:

```powershell
Get-DomainObjectAcl -Identity 'CN=CorpUserCertificate,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' -ResolveGUIDs
```

Review:

```text
ActiveDirectoryRights
ObjectAceType
SecurityIdentifier
AceType
```

---

# Resolve SIDs

If the ACL output contains SIDs, resolve them before reporting.

For example:

```powershell
ConvertFrom-SID 'S-1-5-21-...'
```

when using PowerView.

Native Active Directory cmdlets can also be used to resolve known SIDs.

---

# BloodHound

BloodHound is particularly useful for ESC4 because template control may be part of a larger privilege path.

Conceptually:

```text
alice
  |
  v
MemberOf
  |
  v
Helpdesk
  |
  v
GenericWrite
  |
  v
Certificate Template
```

or:

```text
alice
  |
  v
WriteDACL
  |
  v
PKI Group
  |
  v
Template Control
```

See:

[BloodHound](../bloodhound.md)

---

# BloodHound Template Control

Depending on collector and BloodHound versions, AD CS relationships can expose paths involving certificate templates and PKI objects.

Useful questions include:

```text
Who Controls This Template?
Who Can Enroll?
Who Can Modify Its Permissions?
Which Groups Provide the Control?
What Privileged Path Follows?
```

Always verify graph-derived paths against the actual directory ACL.

---

# LDAP Enumeration from Linux

The template objects can be enumerated with LDAP.

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
    msPKI-Certificate-Name-Flag \
    msPKI-Enrollment-Flag \
    pKIExtendedKeyUsage \
    msPKI-Certificate-Application-Policy \
    msPKI-RA-Signature \
    msPKI-RA-Application-Policies \
    msPKI-Template-Schema-Version
```

LDAP attribute enumeration is useful for configuration verification.

ACL parsing requires security-descriptor-aware tooling.

---

# Certify

Certify can also enumerate certificate-template configuration and permissions from Windows.

Start with:

```text
Certify.exe --help
```

because Certify syntax differs between major releases.

Review the installed version's enumeration functionality for:

```text
Template Permissions
Enrollment Permissions
Object Control
Vulnerable Templates
```

---

# Correlate Multiple Sources

A strong ESC4 assessment can combine:

```text
Certipy
   +
PowerShell
   +
PowerView
   +
BloodHound
   +
LDAP
```

The objective is not to use every tool.

The objective is to confirm:

```text
Object
Permission
Principal
Effective Path
Security Impact
```

---

# Identify Published Templates

Determine whether the controlled template is published by an Enterprise CA.

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Find Which CA Publishes the Template

```powershell
$templateName = 'CorpUserCertificate'

$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Where-Object {
        $_.certificateTemplates -contains $templateName
    } |
    Select-Object Name,dNSHostName
```

---

# Snapshot the Original Configuration

If active validation is approved, capture the complete original configuration first.

Record:

```text
Template DN
Owner
DACL
Subject Name Flags
Enrollment Flags
EKUs
Application Policies
RA Signatures
RA Application Policies
Private-Key Flags
Validity
Schema Version
Published CAs
Enrollment Rights
```

This is essential for safe restoration.

---

# Export ACL Evidence

For an approved template:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpEsc4Test,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-Acl "AD:$templateDN" |
    Format-List
```

Store evidence securely.

---

# Active Validation Strategy

The preferred ESC4 validation hierarchy is:

```text
Read-Only ACL Enumeration
        |
        v
Confirm Dangerous Permission
        |
        v
Determine Security-Sensitive Attributes Writable
        |
        v
Model Resulting ESC Path
        |
        v
Use Dedicated Test Template if Proof Required
        |
        v
Make Minimum Change
        |
        v
Verify
        |
        v
Restore Immediately
```

---

# Read-Only Proof Is Often Sufficient

If an assessment demonstrates:

```text
Low-Privileged Principal
        |
        v
GenericAll
        |
        v
Published Authentication Template
```

then modifying the production template may provide little additional security value.

The ACL itself can be sufficient evidence of the trust-boundary failure.

---

# Do Not Modify Production Templates Unnecessarily

Avoid changing:

```text
User
Machine
DomainController
KerberosAuthentication
WebServer
SmartcardUser
```

or other production templates merely to demonstrate control.

These templates may support critical enterprise services.

---

# Dedicated Test Template

Where active proof is required, prefer:

```text
Dedicated ESC4 Test Template
```

with:

```text
Approved Test Account
Approved CA
Short Validity
No Production Autoenrollment
Documented Cleanup
```

This demonstrates the mechanism without modifying a production certificate workflow.

---

# Minimal Proof Model

A safe proof may consist of:

```text
Before:
Test User Cannot Modify Selected Property

Delegated ESC4 Permission:
Test User Can Modify Selected Property

After:
Property Change Visible

Cleanup:
Original Value Restored
```

This can prove template control without requesting a privileged certificate.

---

# Avoid Full Exploitation When Unnecessary

A complete attack might involve:

```text
Modify Template
      |
      v
Create ESC1
      |
      v
Request Administrator Certificate
      |
      v
Authenticate
```

But a professional assessment should ask whether every stage is necessary.

Often:

```text
ACL Evidence
   +
Controlled Property Change
```

is sufficient.

---

# Potential ESC4 Modification Categories

If a controlled test requires demonstrating security impact, possible categories include:

```text
Subject Identity Control
Certificate Purpose
Issuance Requirements
Enrollment Permissions
Certificate Lifetime
Private-Key Behaviour
```

The minimum-impact property should be selected.

---

# ESC4 and ESC1 Conversion

Conceptually, an attacker could attempt to produce:

```text
Enrollee Supplies Subject
        +
Authentication EKU
        +
Enrollment Permission
        +
No Approval
        +
No Required Signature
```

This creates an ESC1-style configuration.

Do not perform this against a production template without explicit approval.

---

# Template Replication

Certificate template changes are Active Directory changes.

They may need to replicate before all relevant systems observe the new configuration.

Conceptually:

```text
Template Modification
       |
       v
Active Directory Replication
       |
       v
CA / Client Observes Change
```

This is another reason rapid production modification and rollback can be risky.

---

# Existing Certificates Are Not Automatically Changed

Changing a certificate template affects future enrollment behaviour.

It does not automatically rewrite certificates that were previously issued.

Conceptually:

```text
Template Changed
      |
      X
Existing Certificate Rewritten
```

---

# Restore Exact Original State

Cleanup should not merely create a configuration that "looks similar."

Restore:

```text
Original Attributes
Original Owner
Original DACL
Original Enrollment Rights
Original Issuance Requirements
```

exactly where possible.

---

# Verify Cleanup

After restoration:

```text
Re-enumerate Template
       |
       v
Compare with Baseline
       |
       v
Confirm Exact State
```

Do not assume a successful command means restoration was complete.

---

# Detection

ESC4 detection should focus heavily on:

```text
Certificate Template Changes
```

because exploitation requires changing Active Directory configuration unless the dangerous change was made previously.

---

# Event 5136

When Directory Service Changes auditing is appropriately configured, changes to Active Directory objects can generate:

```text
5136
```

Certificate-template modifications are therefore candidates for this telemetry.

Monitor the template container:

```text
CN=Certificate Templates,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

---

# High-Value Attributes to Monitor

Changes to the following deserve particular attention:

```text
msPKI-Certificate-Name-Flag
msPKI-Enrollment-Flag
pKIExtendedKeyUsage
msPKI-Certificate-Application-Policy
msPKI-RA-Signature
msPKI-RA-Application-Policies
msPKI-Private-Key-Flag
pKIExpirationPeriod
nTSecurityDescriptor
```

---

# Detect ACL Changes

Changes to:

```text
nTSecurityDescriptor
```

can indicate:

```text
New Enrollment Permission
New GenericWrite
New GenericAll
New WriteDACL
Ownership-Related Changes
```

PKI ACL changes should be centrally monitored.

---

# Detect Owner Changes

Unexpected ownership changes are especially important.

Conceptually:

```text
Template Owner
     |
     v
Normal PKI Admin
```

changing to:

```text
Normal User
Service Account
Unexpected Group
```

should trigger investigation.

---

# Correlate Template Change with Enrollment

A high-value detection sequence is:

```text
Template Modification
       |
       v
Certificate Enrollment
       |
       v
Certificate Authentication
```

especially when the events occur close together.

---

# Example Detection Sequence

```text
T0
Helpdesk user modifies template

T0 + 2 minutes
Same user requests certificate

T0 + 3 minutes
Certificate maps to privileged identity

T0 + 4 minutes
Certificate-based Kerberos authentication
```

This sequence is much stronger than any event viewed independently.

---

# Monitor EKU Changes

Alert on sensitive additions such as:

```text
Client Authentication
Smart Card Logon
Certificate Request Agent
Any Purpose
```

where those purposes were not previously configured.

---

# Monitor EKU Removal

Removing EKU restrictions may also be dangerous.

Conceptually:

```text
Restricted EKUs
      |
      v
Removed
      |
      v
Unrestricted Certificate Purpose
```

---

# Monitor Subject Name Changes

Changes enabling requester-controlled identity should be investigated.

Conceptually:

```text
Directory-Built Subject
        |
        v
Template Modified
        |
        v
Requester-Supplied Subject
```

This can indicate preparation for an ESC1-style path.

---

# Monitor Approval Changes

Changes that remove:

```text
Manager Approval
```

or:

```text
Authorized Signatures
```

can weaken issuance controls.

---

# Monitor Enrollment Permission Changes

A suspicious sequence is:

```text
Template
   |
   v
New Enroll ACE for Domain Users
   |
   v
Certificate Request
```

Broad enrollment changes should be rare and reviewed.

---

# Monitor Template Publication

If a previously unpublished template becomes available through an issuing CA, investigate whether the publication was authorised.

Template publication and template modification together can create a new attack path.

---

# Hardening ESC4

The primary mitigation is:

```text
Protect Certificate Template ACLs
```

Certificate templates should be treated as privileged identity infrastructure.

---

# Least Privilege

Only principals that genuinely require template administration should receive modification rights.

Normal users generally need only:

```text
Read
Enroll
Autoenroll
```

where appropriate.

They should not require:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
```

---

# Separate Enrollment from Administration

A secure model separates:

```text
Can Request Certificate
```

from:

```text
Can Configure Certificate Template
```

For example:

```text
Employees
   |
   v
Enroll
```

while:

```text
PKI Administrators
   |
   v
Manage Template
```

---

# Restrict WriteDACL

`WriteDACL` should be tightly controlled.

It can allow a principal to transform limited access into broader control.

Conceptually:

```text
WriteDACL
    |
    v
Grant Rights
    |
    v
Template Control
```

---

# Restrict WriteOwner

`WriteOwner` should also be considered highly privileged.

Ownership can provide a path to DACL modification.

---

# Review Delegated Groups

Organisations often intentionally delegate PKI management.

Review groups such as:

```text
PKI Admins
Certificate Managers
Helpdesk
Infrastructure Admins
Application Administrators
MDM Administrators
```

Determine whether their template permissions remain necessary.

---

# Remove Legacy Delegation

ESC4 often appears because permissions were granted for an old deployment and never removed.

Examples include:

```text
Retired MDM Platform
Old Smart Card Project
Legacy VPN
Previous PKI Team
Decommissioned Application
Migration Account
```

Review historical delegation regularly.

---

# Protect the Certificate Templates Container

Do not review only individual templates.

Also inspect permissions on:

```text
CN=Certificate Templates,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Container-level delegation can affect existing or newly created template objects depending on inheritance and permissions.

---

# Protect OID Infrastructure

PKI security reviews should also examine:

```text
CN=OID,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

because application policies and issuance policies are represented through PKI-related directory objects.

This broader object-control problem becomes particularly relevant to ESC5 and ESC13.

---

# Tier PKI Administration

Certificate-template administration should be treated as highly privileged.

In environments using administrative tiering:

```text
Enterprise PKI
```

should generally be treated as:

```text
Tier 0 / Control Plane
```

because certificate configuration can affect domain authentication.

---

# Protect Administrative Workstations

PKI administrators should use hardened administrative systems appropriate to their privilege level.

Avoid managing sensitive templates from ordinary:

```text
Email
Web Browsing
General Productivity
```

workstations.

---

# Change Control

Template changes should follow formal change management.

Record:

```text
Who
What
Why
When
Approved By
Previous Configuration
New Configuration
Rollback Plan
```

---

# Periodic ACL Review

Regularly enumerate template ACLs and compare them with an approved baseline.

Conceptually:

```text
Current ACL
    |
    v
Compare
    |
    v
Approved ACL Baseline
    |
    +--> Match
    |
    +--> Drift
```

---

# Configuration Drift

PKI configuration drift should be treated seriously.

Examples include:

```text
New Write Permission
New Owner
New Enrollment Group
New EKU
Removed Approval
Changed Subject Flag
```

---

# Incident Response

If ESC4 abuse is suspected:

```text
Identify Template
      |
      v
Identify Modification
      |
      v
Identify Actor
      |
      v
Recover Previous Configuration
      |
      v
Identify Certificates Issued After Change
      |
      v
Identify Authentication
      |
      v
Revoke Malicious Certificates
      |
      v
Restore Template
```

---

# Establish the Change Window

Determine:

```text
When Was Template First Modified?
```

Then define the investigation window from:

```text
Modification Time
```

through:

```text
Restoration / Containment Time
```

---

# Identify Modified Attributes

Determine exactly what changed.

Examples:

```text
Subject Name Flags
EKUs
Application Policies
Enrollment Flags
RA Signatures
Private-Key Flags
Validity
ACL
Owner
```

---

# Identify the Actor

Correlate:

```text
Directory Service Change Logs
Administrative Logons
Source Host
PowerShell Logging
LDAP Activity
BloodHound / AD CS Tool Activity
```

where available.

---

# Identify Certificates Issued During Exposure

If the template was made vulnerable between:

```text
T1
```

and:

```text
T2
```

review every certificate issued from that template during that period.

---

# Certificate Investigation

For each suspicious certificate collect:

```text
Serial Number
Thumbprint
Requester
Subject
SAN
Template
Issue Time
Expiration
EKUs
Issuer
```

---

# Revoke Malicious Certificates

If unauthorised certificates were issued:

```text
Revoke
   |
   v
Publish Updated CRL / Revocation Data
   |
   v
Verify Relying Parties Can Obtain It
```

---

# Password Reset Is Not Sufficient

If an attacker obtained an authentication certificate:

```text
Password Reset
      |
      X
Certificate Automatically Revoked
```

Address the certificate independently.

---

# Check for Additional PKI Persistence

An attacker with template control may have made additional changes.

Review:

```text
Other Templates
Template ACLs
Template Owners
OID Objects
Enrollment Services
CA Permissions
Enrollment Agent Restrictions
NTAuthCertificates
```

depending on the privileges involved.

---

# Reporting ESC4

Avoid a title containing only:

```text
ESC4
```

Prefer a title that describes the access-control weakness.

Examples:

```text
Low-Privileged Users Can Modify an Authentication Certificate Template
```

```text
Excessive Certificate Template Permissions Enable AD CS Privilege Escalation
```

```text
Delegated Group Has Unnecessary GenericWrite Access to Certificate Template
```

```text
Certificate Template ACL Allows Unprivileged Users to Modify PKI Security Controls
```

---

# Example Finding

```text
Finding:
Excessive Certificate Template Permissions Enable AD CS Privilege
Escalation

Affected Template:
CorpUserAuthentication

Affected Principal:
CORP\Helpdesk

Permission:
GenericWrite

Description:
The CORP\Helpdesk group has GenericWrite permission over the
CorpUserAuthentication certificate template stored in Active
Directory.

Certificate templates define security-sensitive certificate
properties including subject-name handling, certificate purposes,
issuance requirements, and other enrollment controls.

The affected template is published by the CORP-CA01 Enterprise
Certification Authority.

Members of the Helpdesk group can therefore modify security-sensitive
properties of the template despite not being designated PKI
administrators.

Impact:
A compromised Helpdesk account may be able to alter the certificate
template into a vulnerable configuration.

Depending on the properties modified, this could enable certificate
enrollment conditions associated with other AD CS escalation paths,
including requester-controlled certificate identities or
authentication-capable certificate issuance.

A successfully issued authentication certificate could provide an
additional credential that is independent of the affected account's
password and may result in privilege escalation where a more
privileged identity can be represented.

Recommendation:
Remove GenericWrite from CORP\Helpdesk unless template administration
is an explicit business requirement.

Delegate only the minimum Read, Enroll, or Autoenroll permissions
required for certificate enrollment.

Restrict certificate-template modification rights, ownership, and ACL
administration to dedicated PKI administrators.

Review all certificate-template ACLs for GenericAll, GenericWrite,
WriteProperty, WriteDACL, WriteOwner, unexpected ownership, and
legacy delegated access.

Enable monitoring for certificate-template configuration and ACL
changes and review certificates issued following unauthorised
template modifications.
```

---

# Severity Assessment

Severity should consider:

```text
Who Has Control?
       +
Which Permission?
       +
Which Properties Can Be Modified?
       +
Is Template Published?
       +
Who Can Enroll?
       +
What Certificate Can Be Created?
       +
What Identity Can Be Reached?
       =
Severity
```

---

# High-Risk Example

```text
Domain Users
     |
     v
GenericAll
     |
     v
Published User Authentication Template
```

This can represent a severe PKI control failure.

---

# High-Risk Indirect Example

```text
Helpdesk
   |
   v
WriteDACL
   |
   v
Certificate Template
   |
   v
Grant Self GenericAll
   |
   v
Modify Authentication Controls
```

The indirect nature does not materially reduce the potential impact.

---

# Context-Dependent Example

```text
Application PKI Team
       |
       v
WriteProperty
       |
       v
One Non-Security-Sensitive Property
```

This should not automatically be rated the same as:

```text
GenericAll
```

on an authentication template.

Resolve the exact object-specific permission before assigning severity.

---

# Evidence Checklist

For an ESC4 candidate record:

```text
Template Name
Template DN
Template Display Name
Template Schema Version
Published CA
Template Owner
Principal
Principal SID
Group Membership Path
ACE Type
Active Directory Rights
Object Type GUID
Inherited / Explicit
Effective Permission
Enrollment Rights
Subject Name Flags
Enrollment Flags
EKUs
Application Policies
RA Signature Requirement
RA Application Policies
Private-Key Flags
Validity Period
Original ACL
Original Configuration
Potential Resulting ESC Path
Validation Performed
Restoration Result
Certificates Issued During Test
Cleanup Result
```

---

# ESC4 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Enumerate certificate templates
- [ ] Identify published templates
- [ ] Identify authentication-capable templates
- [ ] Identify template owners
- [ ] Enumerate template ACLs
- [ ] Enumerate Certificate Templates container ACL

## Dangerous Permissions

- [ ] Identify GenericAll
- [ ] Identify GenericWrite
- [ ] Identify WriteProperty
- [ ] Identify WriteDACL
- [ ] Identify WriteOwner
- [ ] Resolve object-specific WriteProperty rights
- [ ] Review inherited ACEs
- [ ] Review explicit ACEs
- [ ] Review Deny ACEs
- [ ] Determine effective permissions

## Principal Analysis

- [ ] Resolve SIDs
- [ ] Resolve nested groups
- [ ] Identify low-privileged principals
- [ ] Identify service accounts
- [ ] Identify legacy administration groups
- [ ] Identify indirect control paths
- [ ] Review BloodHound relationships

## Template Configuration

- [ ] Review `msPKI-Certificate-Name-Flag`
- [ ] Review `msPKI-Enrollment-Flag`
- [ ] Review `pKIExtendedKeyUsage`
- [ ] Review application policies
- [ ] Review `msPKI-RA-Signature`
- [ ] Review `msPKI-RA-Application-Policies`
- [ ] Review `msPKI-Private-Key-Flag`
- [ ] Review validity
- [ ] Review schema version
- [ ] Review enrollment rights

## Publication

- [ ] Determine whether template is published
- [ ] Identify issuing CA
- [ ] Identify all CAs publishing template
- [ ] Distinguish template control from CA control
- [ ] Do not assume template control permits publication

## Attack-Path Analysis

- [ ] Determine whether ESC4 could create ESC1 conditions
- [ ] Determine whether ESC4 could create ESC2 conditions
- [ ] Determine whether ESC4 could create ESC3 conditions
- [ ] Determine whether enrollment can be obtained
- [ ] Determine whether approval can be weakened
- [ ] Determine whether signature requirements can be weakened
- [ ] Determine potential resulting identity
- [ ] Determine certificate authentication impact

## Tooling

- [ ] Enumerate with Certipy
- [ ] Enumerate with PowerShell
- [ ] Review with PowerView where available
- [ ] Review with BloodHound
- [ ] Verify configuration with LDAP
- [ ] Review with Certify where available
- [ ] Verify installed tool versions
- [ ] Manually validate automated ESC4 classifications

## Validation

- [ ] Prefer read-only evidence
- [ ] Determine whether active modification is necessary
- [ ] Obtain explicit approval before modifying templates
- [ ] Prefer dedicated test template
- [ ] Capture complete baseline
- [ ] Capture owner
- [ ] Capture DACL
- [ ] Capture security-sensitive attributes
- [ ] Make minimum required change
- [ ] Avoid production templates where possible
- [ ] Avoid privileged certificate issuance unless required
- [ ] Restore immediately
- [ ] Compare restored configuration to baseline

## Detection

- [ ] Monitor template object changes
- [ ] Monitor event 5136 where applicable
- [ ] Monitor subject-name flag changes
- [ ] Monitor EKU changes
- [ ] Monitor application-policy changes
- [ ] Monitor enrollment-flag changes
- [ ] Monitor approval changes
- [ ] Monitor ACL changes
- [ ] Monitor owner changes
- [ ] Monitor template publication
- [ ] Correlate template changes with enrollment
- [ ] Correlate enrollment with certificate authentication

## Hardening

- [ ] Apply least privilege
- [ ] Separate enrollment from administration
- [ ] Remove unnecessary GenericAll
- [ ] Remove unnecessary GenericWrite
- [ ] Remove unnecessary WriteProperty
- [ ] Restrict WriteDACL
- [ ] Restrict WriteOwner
- [ ] Review template owners
- [ ] Review delegated PKI groups
- [ ] Remove legacy delegation
- [ ] Protect Certificate Templates container
- [ ] Protect OID container
- [ ] Tier PKI administration
- [ ] Use hardened administrative workstations
- [ ] Implement change control
- [ ] Baseline template ACLs
- [ ] Monitor configuration drift

## Incident Response

- [ ] Identify affected template
- [ ] Establish modification time
- [ ] Identify changed attributes
- [ ] Identify ACL changes
- [ ] Identify owner changes
- [ ] Identify actor
- [ ] Identify source host
- [ ] Identify certificates issued during exposure
- [ ] Identify suspicious subjects and SANs
- [ ] Identify certificate authentication
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Restore original template
- [ ] Restore original ACL
- [ ] Restore original owner
- [ ] Review other templates
- [ ] Review broader PKI objects
- [ ] Do not rely on password reset alone

## Cleanup

- [ ] Restore all modified properties
- [ ] Restore original DACL
- [ ] Restore original owner
- [ ] Remove temporary enrollment rights
- [ ] Revoke test certificates where required
- [ ] Delete test PFX files
- [ ] Delete private keys
- [ ] Re-enumerate template
- [ ] Compare against baseline
- [ ] Confirm no unexpected certificates remain
- [ ] Record cleanup evidence

---

# ESC4 Testing Model

The normal template model is:

```text
PKI Administrator
       |
       v
Certificate Template
```

The ESC4 model is:

```text
Low-Privileged Principal
       |
       v
Dangerous ACL
       |
       v
Certificate Template
```

The direct-control model is:

```text
GenericAll / GenericWrite
          |
          v
Modify Template
```

The DACL model is:

```text
WriteDACL
    |
    v
Grant Additional Permission
    |
    v
Template Control
```

The ownership model is:

```text
WriteOwner
    |
    v
Become Owner
    |
    v
Modify DACL
    |
    v
Template Control
```

The object-specific model is:

```text
WriteProperty
     |
     v
ObjectType GUID
     |
     v
Specific Template Attribute
     |
     v
Actual Security Impact
```

The ESC1 conversion model is:

```text
ESC4
 |
 v
Template Control
 |
 +--> Requester-Supplied Identity
 |
 +--> Authentication Purpose
 |
 +--> Weak Issuance Requirements
 |
 +--> Enrollment Access
 |
 v
ESC1-Like Path
```

The ESC2 conversion model is:

```text
ESC4
 |
 v
Modify Certificate Purpose
 |
 v
Any Purpose / Unrestricted Purpose
 |
 v
ESC2-Like Path
```

The ESC3 conversion model is:

```text
ESC4
 |
 v
Certificate Request Agent Capability
 |
 v
Enrollment Agent Certificate
 |
 v
ESC3-Style Path
```

The publication model is:

```text
Template Control
       |
       v
Template Modified
       |
       X
Not Published
```

versus:

```text
Template Control
       |
       v
Published Template
       |
       v
Certificate Enrollment
```

The safe-testing model is:

```text
Enumerate ACL
    |
    v
Confirm Effective Control
    |
    v
Determine Writable Properties
    |
    v
Model Security Impact
    |
    v
Is Active Proof Necessary?
    |
    +--> No -> Report
    |
    +--> Yes
           |
           v
       Test Template
           |
           v
       Capture Baseline
           |
           v
       Minimum Change
           |
           v
       Verify
           |
           v
       Restore
```

The detection model is:

```text
Template Change
      |
      v
Certificate Request
      |
      v
Certificate Issued
      |
      v
Certificate Authentication
```

The defensive model is:

```text
Restricted Template Administration
          +
Least Privilege
          +
Protected ACLs
          +
Protected Ownership
          +
Change Control
          +
Monitoring
          =
Reduced ESC4 Risk
```

For penetration testers:

```text
Do Not Ask:
"Does Certipy print ESC4?"

Ask:
"What effective control does this principal
have over the certificate template, which
security-sensitive properties can that control
change, and what certificate trust path could
result?"
```

For defenders:

```text
Do Not Ask:
"Who can enroll?"

Also Ask:
"Who can change what enrollment means?"
```

That distinction is the core of ESC4.

The complete relationship is:

```text
Principal
   |
   v
ACL
   |
   v
Template Control
   |
   v
Security-Sensitive Configuration
   |
   v
Certificate Enrollment Behaviour
   |
   v
Certificate Trust
   |
   v
Potential Privilege
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC1:

[AD CS ESC1](esc1.md)

ESC2:

[AD CS ESC2](esc2.md)

ESC3:

[AD CS ESC3](esc3.md)

Active Directory ACL and ACE abuse:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

Active Directory Groups:

[Active Directory Groups](../groups.md)

BloodHound:

[BloodHound](../bloodhound.md)

Credential Access:

[Active Directory Credential Access](../credential-access.md)

The next AD CS page is:

```text
active-directory/ad-cs/esc5.md
```

---

# References

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - AD CS Overview

[Microsoft - Active Directory Certificate Services Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Template Concepts

[Microsoft - Certificate Template Concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Manage Certificate Templates

[Microsoft - Manage Certificate Templates](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/manage-certificate-templates){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Permissions on Certificate Templates

[Microsoft - MS-WCCE Permissions on Templates](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/75d6d6d3-9fa0-4f20-85c6-64e4d2ff854e){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

---

## Certify

[GhostPack Certify](https://github.com/GhostPack/Certify){ target="_blank" rel="noopener noreferrer" }

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

ESC4 is fundamentally an:

```text
Access Control
```

problem.

The certificate template itself does not need to begin in a vulnerable state.

Instead:

```text
Safe Template
    |
    v
Weak ACL
    |
    v
Attacker-Controlled Configuration
```

creates the security issue.

The dangerous permissions commonly include:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

but each permission must be interpreted correctly.

In particular:

```text
WriteProperty
```

does not automatically mean:

```text
Full Template Control
```

because object-specific ACEs can restrict which properties are writable.

Likewise:

```text
Template Control
```

does not automatically mean:

```text
Certificate Can Be Issued
```

because CA publication and enrollment remain separate requirements.

The complete assessment therefore asks:

```text
Who Controls the Template?
        |
        v
What Can They Change?
        |
        v
Is the Template Published?
        |
        v
Can a Certificate Be Obtained?
        |
        v
What Security Property Results?
        |
        v
What Identity or Trust Boundary Is Crossed?
```

ESC4 can become a precursor to several other AD CS paths:

```text
ESC4
 |
 +--> ESC1-like configuration
 |
 +--> ESC2-like configuration
 |
 +--> ESC3-like configuration
```

but the root cause remains:

```text
Excessive Certificate Template Permissions
```

For penetration testers, production template modification should normally be unnecessary when the effective ACL and resulting security impact can already be demonstrated.

For defenders, certificate-template ACLs should receive the same level of attention as other privileged Active Directory control-plane objects.

A principal that can change:

```text
Who a certificate represents
```

or:

```text
What a certificate can be used for
```

may effectively be able to change the organisation's authentication policy.

That is why certificate-template administration belongs within the privileged Active Directory and PKI security boundary.
