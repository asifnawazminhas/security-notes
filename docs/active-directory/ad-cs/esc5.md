# AD CS ESC5 - Vulnerable PKI Object Access Control

ESC5 is an Active Directory Certificate Services (AD CS) privilege escalation condition involving excessive permissions over PKI-related Active Directory objects or supporting PKI infrastructure.

Unlike ESC4, which specifically focuses on control over a certificate template, ESC5 covers broader PKI object control.

A simplified relationship is:

```text
Low-Privileged Principal
        |
        v
Excessive Permission
        |
        v
PKI Object / PKI Infrastructure
        |
        v
Modify Certificate Trust or Enrollment
        |
        v
Certificate Abuse
        |
        v
Privilege Escalation
```

Potentially security-sensitive PKI objects include:

```text
Certification Authority Objects
Enrollment Services
NTAuthCertificates
AIA Objects
CDP Objects
OID Objects
Certificate Templates Container
PKI Containers
```

The core ESC5 question is:

```text
Can a principal that should not administer PKI
modify an object that influences certificate
issuance, certificate trust, or authentication?
```

!!! warning "Authorised testing only"
    PKI objects can affect authentication and certificate trust across an entire Active Directory forest. Begin with read-only ACL enumeration. Do not modify production PKI objects, NTAuthCertificates, CA configuration, trust stores, OID objects, AIA/CDP configuration, or other PKI infrastructure merely to prove control. Active validation should use a dedicated lab or explicitly approved test object whenever possible.

---

# ESC5 Concept

The normal model is:

```text
PKI Administrators
       |
       v
PKI Configuration Objects
       |
       v
Certificate Trust
```

The ESC5 model becomes:

```text
Low-Privileged Principal
       |
       v
Dangerous ACL
       |
       v
PKI Configuration Object
       |
       v
Certificate Trust Manipulation
```

ESC5 is therefore fundamentally an:

```text
PKI Control-Plane Access Control
```

problem.

---

# Why PKI Object Control Matters

AD CS is not controlled by a single object.

Enterprise PKI configuration is distributed across:

```text
Active Directory
Certification Authorities
Certificate Templates
CA Configuration
Trust Stores
Enrollment Services
Policy Objects
Revocation Infrastructure
```

A weakness in one of these areas may affect the security of the entire certificate trust model.

---

# PKI as an Authentication Control Plane

Certificates may be used for:

```text
Kerberos PKINIT
Smart Card Logon
Client Authentication
TLS
LDAPS
VPN
Wi-Fi
Device Authentication
Code Signing
Application Authentication
```

Therefore:

```text
PKI Configuration Control
```

can sometimes become:

```text
Authentication Control
```

---

# PKI Objects in Active Directory

Many Enterprise PKI objects are stored under:

```text
CN=Public Key Services,
CN=Services,
CN=Configuration,
DC=...
```

A simplified structure is:

```text
Configuration
    |
    v
Services
    |
    v
Public Key Services
    |
    +--> AIA
    |
    +--> CDP
    |
    +--> Certificate Templates
    |
    +--> Certification Authorities
    |
    +--> Enrollment Services
    |
    +--> KRA
    |
    +--> NTAuthCertificates
    |
    +--> OID
```

These objects should be treated as security-sensitive directory infrastructure.

---

# Configuration Naming Context

Retrieve the Configuration naming context with:

```powershell
(Get-ADRootDSE).configurationNamingContext
```

For example:

```text
CN=Configuration,DC=corp,DC=example
```

The Public Key Services base becomes:

```text
CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example
```

---

# Enumerate Public Key Services

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$pkiBase = "CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $pkiBase -SearchScope OneLevel -Filter * |
    Select-Object Name,ObjectClass,DistinguishedName
```

This provides an initial inventory of the PKI containers and objects visible in Active Directory.

---

# Important ESC5 Targets

ESC5 analysis should consider control over objects such as:

```text
PKI Containers
Certification Authorities
Enrollment Services
NTAuthCertificates
AIA
CDP
OID
```

as well as other PKI-related objects that influence enterprise certificate trust.

---

# ESC5 vs ESC4

ESC4 specifically concerns:

```text
Certificate Template ACL
```

For example:

```text
User
 |
 v
GenericWrite
 |
 v
Certificate Template
```

ESC5 is broader:

```text
User
 |
 v
GenericWrite
 |
 v
PKI Object
```

The affected object determines the classification.

---

# ESC5 vs ESC7

ESC7 concerns dangerous permissions on the Certification Authority service itself.

For example:

```text
ManageCA
ManageCertificates
```

ESC5 generally concerns control over PKI-related objects or supporting PKI infrastructure rather than CA service administrative permissions.

Conceptually:

```text
ESC5
    |
    v
PKI Object Control
```

versus:

```text
ESC7
    |
    v
CA Service Control
```

---

# ESC5 vs ESC13

ESC13 involves issuance policies and their relationship to Active Directory groups.

The relevant infrastructure includes objects under:

```text
CN=OID,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

If an attacker can modify the OID infrastructure itself because of excessive ACLs, that object-control weakness may also represent an ESC5-style control-plane issue.

The final classification should describe the actual root cause and resulting attack path.

---

# Important Permissions

As with other Active Directory objects, dangerous rights may include:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
CreateChild
DeleteChild
Delete
```

The impact depends on:

```text
Affected Object
       +
Specific Permission
       +
Inheritance
       +
Writable Attributes
       +
Resulting PKI Behaviour
```

---

# GenericAll

`GenericAll` provides broad control over an object.

Conceptually:

```text
Principal
   |
   v
GenericAll
   |
   v
PKI Object
   |
   v
Broad Object Control
```

A low-privileged principal with `GenericAll` over a security-sensitive PKI object should be investigated immediately.

---

# GenericWrite

`GenericWrite` may allow modification of writable attributes.

The impact depends on the object.

For example:

```text
GenericWrite
      |
      v
Enrollment Services Object
```

has a different security impact from:

```text
GenericWrite
      |
      v
OID Object
```

Do not report all `GenericWrite` relationships as equivalent.

---

# WriteProperty

`WriteProperty` may apply broadly or to specific attributes.

An object-specific ACE may grant:

```text
WriteProperty
      |
      v
Specific Attribute GUID
```

rather than control over every property.

Resolve the affected attribute before determining exploitability.

---

# WriteDACL

`WriteDACL` can provide indirect object control.

```text
Principal
   |
   v
WriteDACL
   |
   v
Add ACE
   |
   v
Grant Additional Rights
   |
   v
PKI Object Control
```

This is often as important as direct write access.

---

# WriteOwner

`WriteOwner` can create another indirect control path.

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
Grant Rights
    |
    v
PKI Object Control
```

---

# CreateChild

Container permissions deserve particular attention.

A principal with:

```text
CreateChild
```

on a sensitive PKI container may be able to create new PKI-related objects.

The impact depends on:

```text
Container
Object Class
Inheritance
How AD CS Consumes the Object
```

Do not assume object creation automatically produces certificate trust.

---

# Delete and DeleteChild

Deletion rights can also be security relevant.

For example:

```text
Delete PKI Object
```

may cause:

```text
Availability Impact
Enrollment Failure
Trust Failure
Revocation Failure
```

ESC5 analysis therefore includes both:

```text
Privilege Escalation
```

and potentially:

```text
PKI Integrity / Availability
```

concerns.

---

# Ownership

Always record the owner of sensitive PKI objects.

Unexpected owners may include:

```text
Normal Users
Service Accounts
Legacy Deployment Accounts
Application Groups
Helpdesk Groups
Former PKI Administration Groups
```

Ownership can provide a route to DACL modification.

---

# Public Key Services Container

The base PKI container is:

```text
CN=Public Key Services,CN=Services,CN=Configuration,...
```

Inspect its ACL:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$pkiBase = "CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$pkiBase").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

---

# Container-Level Permissions

Container ACLs can be especially important because permissions may:

```text
Apply Directly
Be Inherited
Allow Child Creation
Allow Child Deletion
```

A dangerous permission on the parent container may affect multiple PKI objects.

---

# Enumerate PKI ACLs

A useful read-only inventory can be created with:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$pkiBase = "CN=Public Key Services,CN=Services,$configNC"

Get-ChildItem "AD:$pkiBase" -Recurse |
    ForEach-Object {
        $object = $_
        $acl = Get-Acl $object.PSPath

        $acl.Access |
            Select-Object @{
                Name = 'Object'
                Expression = { $object.DistinguishedName }
            }, IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
    }
```

Large environments may produce substantial output.

Filter and export results where appropriate.

---

# Enumerate Dangerous Rights

A triage approach is:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$pkiBase = "CN=Public Key Services,CN=Services,$configNC"

Get-ChildItem "AD:$pkiBase" -Recurse |
    ForEach-Object {
        $object = $_
        $acl = Get-Acl $object.PSPath

        $acl.Access |
            Where-Object {
                $_.AccessControlType -eq 'Allow' -and
                (
                    $_.ActiveDirectoryRights -match 'GenericAll' -or
                    $_.ActiveDirectoryRights -match 'GenericWrite' -or
                    $_.ActiveDirectoryRights -match 'WriteDacl' -or
                    $_.ActiveDirectoryRights -match 'WriteOwner' -or
                    $_.ActiveDirectoryRights -match 'CreateChild'
                )
            } |
            Select-Object @{
                Name = 'Object'
                Expression = { $object.DistinguishedName }
            }, IdentityReference,ActiveDirectoryRights,ObjectType,InheritedObjectType,IsInherited
    }
```

This is only triage.

Effective permissions must still be determined.

---

# Enrollment Services

Enterprise CA registration information is stored under:

```text
CN=Enrollment Services,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate it:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties * |
    Select-Object Name,dNSHostName,certificateTemplates,DistinguishedName
```

---

# Enrollment Services ACL

Inspect a specific CA enrollment object:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$caDN = "CN=CORP-CA,CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$caDN").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

---

# Why Enrollment Services Matter

Enrollment Services objects describe Enterprise CAs and include information such as:

```text
CA Name
CA Host
Published Templates
CA Certificates
```

Changes to these objects can affect how clients discover or interpret enterprise certificate services.

Do not equate control over the Enrollment Services AD object with:

```text
CA Private-Key Control
```

or:

```text
ManageCA
```

Those are separate security boundaries.

---

# Certification Authorities Container

The Certification Authorities container is:

```text
CN=Certification Authorities,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$caBase = "CN=Certification Authorities,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $caBase -Filter * -Properties * |
    Select-Object Name,ObjectClass,DistinguishedName
```

---

# Certification Authorities ACL

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$caBase = "CN=Certification Authorities,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$caBase").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

Also inspect individual child objects.

---

# NTAuthCertificates

One of the most security-sensitive PKI objects is:

```text
CN=NTAuthCertificates,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

NTAuth participates in determining which enterprise CA certificates are trusted for certain Active Directory authentication scenarios.

Conceptually:

```text
Certificate
    |
    v
Issuing CA
    |
    v
Enterprise Authentication Trust
    |
    v
NTAuth
```

Control over NTAuth should therefore be treated as highly privileged.

---

# Enumerate NTAuthCertificates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$ntAuthDN = "CN=NTAuthCertificates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -Identity $ntAuthDN -Properties *
```

---

# NTAuth ACL

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$ntAuthDN = "CN=NTAuthCertificates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$ntAuthDN").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

Unexpected write permissions should receive immediate investigation.

---

# Why NTAuth Control Is Dangerous

A simplified trust model is:

```text
Certificate Authentication
        |
        v
Certificate Chain
        |
        v
Trusted Enterprise CA
        |
        v
NTAuth / Authentication Trust
```

A principal capable of changing enterprise authentication trust may be able to influence which certificate authorities are accepted for authentication.

This is a control-plane issue, not ordinary certificate enrollment.

---

# Do Not Modify NTAuth During Routine Testing

Do not attempt to prove NTAuth write access by adding an attacker-controlled CA certificate to a production forest.

That can alter authentication trust across the environment.

Read-only evidence such as:

```text
Unexpected GenericWrite
Unexpected GenericAll
WriteDACL
WriteOwner
```

is normally sufficient to demonstrate the security problem.

---

# AIA

Authority Information Access objects can be found under:

```text
CN=AIA,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$aiaBase = "CN=AIA,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $aiaBase -Filter * -Properties * |
    Select-Object Name,ObjectClass,DistinguishedName
```

---

# AIA ACL

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$aiaBase = "CN=AIA,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$aiaBase").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

Inspect child objects as well.

---

# Why AIA Matters

AIA information helps clients locate CA certificates and build certificate chains.

Conceptually:

```text
Certificate
    |
    v
AIA
    |
    v
Issuer Information
    |
    v
Certificate Chain Construction
```

AIA control can therefore affect PKI integrity and certificate validation behaviour.

Its exact security impact depends on how relying parties consume the configuration.

---

# CDP

Certificate Revocation List distribution information is represented through PKI configuration including:

```text
CN=CDP,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$cdpBase = "CN=CDP,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $cdpBase -Filter * -Properties * |
    Select-Object Name,ObjectClass,DistinguishedName
```

---

# CDP ACL

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$cdpBase = "CN=CDP,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$cdpBase").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

---

# Why CDP Matters

CRL Distribution Points support certificate revocation checking.

Conceptually:

```text
Certificate
    |
    v
CDP
    |
    v
CRL
    |
    v
Revoked?
```

Improper control may create:

```text
PKI Integrity Issues
Revocation Availability Issues
Validation Problems
```

The exact impact depends on certificate-chain and revocation configuration.

---

# OID Container

The OID container is:

```text
CN=OID,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$oidBase = "CN=OID,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $oidBase -Filter * -Properties * |
    Select-Object Name,DisplayName,ObjectClass,DistinguishedName
```

---

# OID ACL

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$oidBase = "CN=OID,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$oidBase").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,InheritedObjectType,IsInherited
```

---

# Why OID Objects Matter

OID objects can represent:

```text
Application Policies
Issuance Policies
Certificate Policy Metadata
```

Some AD CS privilege paths depend on relationships between certificate issuance policies and Active Directory security groups.

This becomes especially important in:

```text
ESC13
```

---

# OID Group Linking

Modern AD CS assessments should examine:

```text
msDS-OIDToGroupLink
```

on relevant OID objects.

Conceptually:

```text
Certificate Issuance Policy
        |
        v
OID Object
        |
        v
msDS-OIDToGroupLink
        |
        v
Active Directory Group
```

The detailed abuse model belongs in the ESC13 notes.

---

# KRA

The Key Recovery Agents container may also exist under Public Key Services.

Conceptually:

```text
CN=KRA,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Key archival and recovery are highly sensitive PKI functions.

Review unexpected permissions carefully.

---

# Certificate Templates Container

Although individual template control is normally discussed under ESC4, the parent container itself should also be reviewed.

```text
CN=Certificate Templates,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Dangerous container permissions can potentially influence:

```text
Child Creation
Child Deletion
Inheritance
Template Administration
```

---

# ESC4 or ESC5 for Template Container Control?

Classification depends on the actual path.

If the issue is:

```text
Control over an Individual Certificate Template
```

ESC4 is the natural classification.

If the issue is broader:

```text
Control over PKI Container Infrastructure
```

ESC5 may better describe the root cause.

Do not focus excessively on the ESC number.

Report the actual permission and impact.

---

# Active Directory Sites and Services

PKI objects can also be inspected through tools such as:

```text
ADSI Edit
```

when appropriate.

The Configuration partition can be browsed under:

```text
CN=Services
  |
  v
CN=Public Key Services
```

ADSI Edit is powerful.

Do not make changes during enumeration.

---

# ADSI Edit Safety

Treat:

```text
adsiedit.msc
```

as an administrative configuration tool.

A mistaken change can directly modify Active Directory.

For assessment work:

```text
Browse
Inspect
Record
```

but avoid:

```text
Edit
Delete
Create
```

unless explicitly authorised.

---

# PowerView

PowerView can assist with ACL analysis.

For example:

```powershell
Get-DomainObjectAcl -Identity 'CN=NTAuthCertificates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' -ResolveGUIDs
```

Review:

```text
SecurityIdentifier
ActiveDirectoryRights
ObjectAceType
AceType
IsInherited
```

---

# BloodHound

BloodHound can help identify indirect paths to PKI object control.

For example:

```text
alice
  |
  v
MemberOf
  |
  v
PKI Operators
  |
  v
GenericWrite
  |
  v
PKI Object
```

or:

```text
alice
  |
  v
WriteDACL
  |
  v
Group
  |
  v
PKI Administrative Control
```

Graph results should be manually validated against the actual ACLs.

---

# Certipy Enumeration

Certipy can enumerate AD CS configuration and identify several PKI-related security issues.

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

---

# Certipy and ESC5

Automated tooling may identify certain object-control conditions as:

```text
ESC5
```

but ESC5 is broad.

Always determine:

```text
Which Object?
Which Permission?
Which Principal?
What Can Be Modified?
How Does It Affect PKI Security?
```

before reporting the finding.

---

# LDAP Enumeration from Linux

Enumerate Public Key Services:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(objectClass=*)' \
    dn \
    objectClass \
    cn \
    displayName
```

---

# Enumerate Enrollment Services with LDAP

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

---

# Enumerate OID Objects with LDAP

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=OID,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(objectClass=msPKI-Enterprise-Oid)' \
    cn \
    displayName \
    msPKI-Cert-Template-OID \
    msDS-OIDToGroupLink
```

---

# LDAP Security Descriptor Limitation

A normal LDAP attribute query does not automatically provide a human-friendly interpretation of:

```text
nTSecurityDescriptor
```

Use security-descriptor-aware tooling for reliable ACL analysis.

Do not infer ESC5 solely from ordinary LDAP object output.

---

# Effective Permissions

As with ESC4, direct ACEs are only part of the picture.

A principal may gain control through:

```text
Nested Group Membership
Inherited ACE
Object Ownership
WriteDACL Chain
WriteOwner Chain
Group Control
```

Conceptually:

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
GenericWrite
 |
 v
PKI Object
```

---

# Resolve Nested Groups

For an account:

```powershell
Get-ADPrincipalGroupMembership 'audit-user' |
    Select-Object Name,DistinguishedName
```

For more complex nested relationships, combine:

```text
PowerShell
PowerView
BloodHound
```

as appropriate.

---

# Evaluate Deny ACEs

Effective permission analysis must consider:

```text
Allow
Deny
Explicit
Inherited
Object-Specific
Group Membership
Ownership
```

Do not report an Allow ACE without considering whether it actually results in effective control.

---

# Object-Specific ACEs

An ACE may contain an:

```text
ObjectType
```

GUID.

This may restrict the ACE to:

```text
Specific Property
Specific Extended Right
Specific Child Object Type
```

Resolve these GUIDs before assigning impact.

---

# Parent-Child Inheritance

PKI container permissions may be inherited by child objects.

Conceptually:

```text
Public Key Services
       |
       v
Inherited ACE
       |
       +--> OID
       |
       +--> AIA
       |
       +--> CDP
       |
       +--> Other Children
```

Check:

```text
IsInherited
InheritanceType
InheritedObjectType
```

---

# ESC5 Attack Paths

Because ESC5 is broad, there is no single universal exploitation path.

Potential models include:

```text
PKI Object Control
      |
      v
Trust Configuration Change
      |
      v
Certificate Accepted
```

or:

```text
PKI Object Control
      |
      v
Enrollment Configuration Change
      |
      v
Certificate Issued
```

or:

```text
PKI Object Control
      |
      v
Policy Relationship Change
      |
      v
Privilege Assignment
```

The actual path depends on the object.

---

# ESC5 and NTAuth

A particularly sensitive conceptual path is:

```text
PKI Object Write
      |
      v
NTAuthCertificates
      |
      v
Enterprise Authentication Trust
```

Because of the potential forest-wide impact, production modification is not an appropriate routine validation technique.

---

# ESC5 and OID Objects

Another path may involve:

```text
OID Object Control
      |
      v
Issuance Policy Configuration
      |
      v
Group Relationship
```

This should be analysed together with ESC13 concepts where applicable.

---

# ESC5 and Enrollment Services

Control over Enrollment Services objects may affect:

```text
CA Discovery
Published Template Metadata
Enterprise CA Registration
```

The exact impact must be demonstrated rather than assumed.

Do not state:

```text
Enrollment Services GenericWrite = Domain Admin
```

without establishing a real privilege path.

---

# ESC5 and CA Host Compromise

Some ESC5 taxonomies also discuss security weaknesses involving the systems hosting AD CS.

For example:

```text
CA Server
   |
   v
Local Administrative Control
```

may expose:

```text
CA Configuration
CA Service
CA Private Keys
Certificate Database
```

This is substantially more severe than ordinary directory-object write access.

However, the exact root cause should be reported clearly:

```text
CA Host Compromise
```

rather than hiding the issue behind an ESC number.

---

# CA Private Key

The CA private key is one of the most sensitive assets in the PKI.

Conceptually:

```text
CA Private Key
      |
      v
Sign Certificates
      |
      v
PKI Trust
```

Compromise of an issuing or root CA private key can have consequences far beyond a single certificate template.

---

# Do Not Attempt CA Key Extraction for ESC5 Validation

Do not extract:

```text
CA Private Keys
HSM Keys
CA Backup Keys
```

merely to demonstrate an ESC5 candidate.

If the assessment scope explicitly includes CA host compromise, handle that as a separate high-impact validation activity with appropriate approval.

---

# CA Backup Security

CA backups can contain highly sensitive material.

Review access to:

```text
CA Backup Locations
System State Backups
PKI Backup Shares
Offline Backup Media
Key Backup Files
```

as part of a broader PKI assessment.

---

# HSM Considerations

Hardware Security Modules can significantly reduce the risk of direct CA private-key extraction.

However:

```text
HSM
```

does not automatically solve:

```text
Directory ACL Misconfiguration
CA Administrative Permission Abuse
Template Misconfiguration
Enrollment Abuse
```

PKI security requires multiple layers.

---

# Safe Validation Strategy

The preferred ESC5 validation model is:

```text
Enumerate
   |
   v
Identify Dangerous ACL
   |
   v
Resolve Effective Permission
   |
   v
Identify Affected PKI Object
   |
   v
Determine Security Consequence
   |
   v
Stop if Read-Only Evidence Is Sufficient
```

Only continue if active validation provides necessary additional evidence.

---

# Read-Only Evidence

A strong ESC5 finding can often be established using:

```text
Object Distinguished Name
Object Type
Principal
Effective Permission
ACL Evidence
Inheritance
Potential Security-Sensitive Modification
Resulting Trust Boundary
```

This is usually preferable to modifying production PKI.

---

# Dedicated Test Object

If active validation is required, prefer a dedicated object in a controlled environment.

Conceptually:

```text
Test PKI Object
      |
      v
Delegated Test Principal
      |
      v
Controlled Property Change
      |
      v
Restore
```

This demonstrates write capability without altering production trust.

---

# Do Not Use Production Trust as Proof

Avoid validation such as:

```text
Add Rogue CA to NTAuth
Modify Production OID Mapping
Delete AIA Object
Delete CDP Object
Alter Enterprise CA Registration
```

unless the engagement explicitly requires that specific high-impact test.

---

# Evidence Collection

Record:

```text
Object Name
Distinguished Name
Object Class
Object Owner
Principal
Principal SID
ACE
ActiveDirectoryRights
ObjectType
InheritedObjectType
IsInherited
Effective Permission
Relevant Attributes
Potential Security Impact
```

---

# Evidence Before Any Change

If an approved active test requires modification, record:

```text
Complete Original Object
Original Owner
Original DACL
Original Attributes
Replication State
```

before changing anything.

---

# Detection

ESC5 detection should focus on changes to security-sensitive PKI objects.

A useful model is:

```text
PKI Object Change
      |
      v
Certificate / Trust Change
      |
      v
Authentication or Enrollment Activity
```

---

# Event 5136

When Directory Service Changes auditing is configured, Active Directory object modifications can generate:

```text
5136
```

This is important for monitoring changes under:

```text
CN=Public Key Services
```

---

# Monitor PKI Distinguished Names

High-value monitoring locations include:

```text
CN=Public Key Services,CN=Services,CN=Configuration,...
```

and its child containers.

---

# Monitor NTAuthCertificates

Changes to:

```text
CN=NTAuthCertificates
```

should be extremely rare.

Any unexpected modification should be investigated.

---

# Monitor OID Changes

Monitor:

```text
CN=OID
```

for:

```text
New Objects
Deleted Objects
Changed OIDs
Changed Group Links
Changed ACLs
Changed Owners
```

---

# Monitor Enrollment Services

Monitor changes to:

```text
CN=Enrollment Services
```

including:

```text
CA Objects
Published Template Lists
CA Certificates
Host Information
ACLs
Ownership
```

---

# Monitor AIA and CDP

Changes to:

```text
AIA
CDP
```

may affect:

```text
Chain Building
Revocation
Availability
Certificate Validation
```

Unexpected modifications should be reviewed.

---

# Monitor ACL Changes

Particularly important changes include:

```text
New GenericAll
New GenericWrite
New WriteDACL
New WriteOwner
New CreateChild
New DeleteChild
```

---

# Monitor Ownership Changes

Alert on sensitive PKI objects changing owner to:

```text
Normal User
Unexpected Service Account
Application Group
Helpdesk
Unapproved Administrative Group
```

---

# Monitor Child Object Creation

Unexpected object creation under:

```text
Public Key Services
OID
AIA
CDP
```

should be investigated.

---

# Monitor Child Object Deletion

Likewise, deletion may indicate:

```text
Malicious Modification
Persistence Cleanup
Sabotage
PKI Availability Attack
```

---

# Correlate with Certificate Activity

Where possible correlate:

```text
PKI Configuration Change
       |
       v
Certificate Request
       |
       v
Certificate Issuance
       |
       v
Certificate Authentication
```

---

# Baseline PKI Configuration

Maintain an approved baseline of:

```text
PKI Objects
Object Owners
ACLs
CA Objects
NTAuth Contents
OID Objects
AIA
CDP
Enrollment Services
Published Templates
```

This makes unexpected drift easier to identify.

---

# Hardening ESC5

The core mitigation is:

```text
Protect the PKI Control Plane
```

AD CS configuration should be treated as privileged infrastructure.

---

# Restrict PKI Object Administration

Only dedicated PKI administrators should normally have broad write access under:

```text
CN=Public Key Services
```

Review all delegated access.

---

# Apply Least Privilege

Avoid unnecessary:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
CreateChild
DeleteChild
```

on PKI objects.

---

# Review Parent Containers

Do not only inspect individual objects.

Review:

```text
Public Key Services
Certificate Templates
Enrollment Services
Certification Authorities
OID
AIA
CDP
KRA
```

for inherited delegation.

---

# Separate PKI Administration

Where possible separate:

```text
Certificate Enrollment
```

from:

```text
Certificate Template Administration
```

from:

```text
CA Administration
```

from:

```text
PKI Trust Administration
```

These represent different privilege levels.

---

# Treat Enterprise PKI as Tier 0

Where certificates participate in Active Directory authentication:

```text
Enterprise PKI
```

should generally be considered part of the identity control plane.

Compromise can affect privileged authentication.

---

# Protect PKI Administrative Accounts

Use:

```text
Dedicated Administrative Accounts
Strong Authentication
Privileged Access Workstations
Minimal Group Membership
Administrative Tiering
Monitoring
```

appropriate to the environment.

---

# Protect CA Hosts

Enterprise CA systems should receive strong server hardening.

Consider:

```text
Restricted Interactive Logon
Restricted Administrative Access
Patch Management
Application Control
EDR
Firewall Segmentation
Backup Protection
Service Account Hardening
HSM Where Appropriate
```

---

# Protect CA Private Keys

Use appropriate controls such as:

```text
Non-Exportable Keys
HSM
Strict Key ACLs
Secure Backup
Dual Control
Key Ceremony Procedures
```

depending on the CA tier and organisational requirements.

---

# Protect Backups

PKI backup material should receive protections comparable to the live CA.

A secure production CA with an exposed backup can still be compromised.

---

# Change Management

Require formal change management for modifications to:

```text
NTAuth
OID Objects
Enrollment Services
AIA
CDP
CA Objects
PKI ACLs
PKI Owners
```

---

# Periodic ACL Review

Regularly compare current PKI ACLs against an approved baseline.

Conceptually:

```text
Current PKI ACL
      |
      v
Compare
      |
      v
Approved Baseline
      |
      +--> Expected
      |
      +--> Drift
```

---

# Remove Legacy Delegation

Common sources of unnecessary PKI permissions include:

```text
Old PKI Migrations
Retired Certificate Platforms
Former Administrators
Legacy Service Accounts
Deprecated MDM Systems
Old Smart Card Deployments
Application Migration Accounts
Temporary Project Groups
```

Remove access that is no longer required.

---

# Incident Response

If ESC5 abuse is suspected:

```text
Identify PKI Object
      |
      v
Identify Modification
      |
      v
Identify Actor
      |
      v
Determine Trust Impact
      |
      v
Identify Certificates / Authentication
      |
      v
Restore Configuration
      |
      v
Revoke Where Required
```

---

# Establish Scope

Determine whether the attacker controlled:

```text
One PKI Object
One Container
Multiple PKI Objects
CA Host
CA Service
CA Private Key
```

The response differs significantly between these scenarios.

---

# Identify Changed Objects

Review:

```text
Public Key Services
NTAuthCertificates
Enrollment Services
Certification Authorities
OID
AIA
CDP
KRA
Certificate Templates
```

for unauthorised changes.

---

# Identify ACL Changes

Determine whether the attacker:

```text
Used Existing Permission
```

or:

```text
Created New Permission
```

through:

```text
WriteDACL
WriteOwner
Group Modification
Inherited Delegation
```

---

# Identify Certificates Issued During Exposure

If the change affected certificate issuance or authentication trust, identify certificates issued during the exposure period.

Collect:

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
```

---

# Investigate NTAuth Changes

If NTAuth was modified:

```text
Identify Added Certificates
Identify Removed Certificates
Identify Issuing CAs
Identify Change Time
Identify Actor
Identify Authentication Activity
```

Treat unexpected authentication trust changes as high priority.

---

# Investigate OID Changes

If OID objects were modified:

```text
Identify Modified OID
Identify Group Link
Identify Affected Templates
Identify Certificates Issued
Identify Accounts Receiving Resulting Privilege
```

---

# Investigate CA Host Access

If the CA server itself was compromised, expand the incident scope.

Review:

```text
CA Private Keys
CA Database
CA Configuration
CA Backups
Service Accounts
Administrative Credentials
Issued Certificates
HSM Access
```

A CA host compromise may require broader PKI recovery.

---

# Certificate Revocation

Where malicious certificates were issued:

```text
Identify
   |
   v
Revoke
   |
   v
Publish Updated Revocation Information
   |
   v
Verify Distribution
```

---

# Password Reset Is Not Enough

If certificates were issued:

```text
Password Reset
      |
      X
Certificate Revocation
```

Certificate credentials must be handled separately.

---

# CA Key Compromise

If a CA private key was compromised, revoking individual malicious certificates may not be sufficient.

The organisation may need to consider:

```text
CA Certificate Revocation
CA Re-Key
CA Replacement
Trust Store Changes
Certificate Re-Issuance
Application Remediation
```

This is a major PKI incident and should follow the organisation's PKI recovery procedures.

---

# Reporting ESC5

Avoid reporting only:

```text
ESC5
```

Describe the actual object-control weakness.

Examples:

```text
Low-Privileged Group Can Modify Enterprise PKI Objects
```

```text
Excessive Permissions on NTAuthCertificates Allow Modification of Authentication Trust
```

```text
Delegated Account Has WriteDACL Permission over AD CS PKI Infrastructure
```

```text
Weak PKI Container Permissions Permit Unauthorised Configuration Changes
```

---

# Example Finding

```text
Finding:
Excessive Permissions on Enterprise PKI Objects

Affected Object:
CN=NTAuthCertificates,
CN=Public Key Services,
CN=Services,
CN=Configuration,
DC=corp,
DC=example

Affected Principal:
CORP\PKI-Support

Permission:
GenericWrite

Description:
The CORP\PKI-Support group has GenericWrite permission over the
NTAuthCertificates object in the Active Directory Configuration
partition.

NTAuthCertificates forms part of the enterprise PKI trust
configuration used by Active Directory certificate-based
authentication.

The affected group is not designated as a privileged PKI trust
administrator.

Impact:
A compromised member of CORP\PKI-Support may be able to modify
security-sensitive enterprise PKI trust configuration.

Changes to certificate authentication trust can affect which
certification authorities participate in Active Directory
certificate-based authentication and may therefore impact the
forest's identity control plane.

No modification of the production NTAuthCertificates object was
performed during the assessment because the existing ACL provides
sufficient evidence of unauthorised PKI administrative capability.

Recommendation:
Remove GenericWrite from CORP\PKI-Support unless modification of
enterprise authentication trust is an explicitly required business
function.

Restrict modification of NTAuthCertificates and other sensitive PKI
objects to dedicated PKI administrators.

Review inherited permissions throughout CN=Public Key Services and
remove unnecessary GenericAll, GenericWrite, WriteProperty,
WriteDACL, WriteOwner, CreateChild, and DeleteChild permissions.

Monitor changes to enterprise PKI objects and maintain an approved
baseline of PKI object ownership and ACLs.
```

---

# Severity Assessment

ESC5 severity depends heavily on the affected object.

A useful model is:

```text
Principal Privilege
      +
Effective Permission
      +
PKI Object
      +
Possible Modification
      +
Authentication / Trust Impact
      +
Reachable Privilege
      =
Severity
```

---

# Critical Example

```text
Low-Privileged Principal
        |
        v
Control of Enterprise Authentication Trust
        |
        v
Certificate Trust Manipulation
        |
        v
Privileged Authentication
```

This may represent a critical identity control-plane weakness.

---

# High-Risk Infrastructure Example

```text
Normal User
   |
   v
Administrative Control
   |
   v
Enterprise CA Host
   |
   v
CA Private Key
```

This may represent catastrophic PKI compromise.

---

# Context-Dependent Example

```text
PKI Operations Group
       |
       v
WriteProperty
       |
       v
Non-Security-Sensitive Metadata
```

This should not automatically be treated as equivalent to:

```text
GenericAll over NTAuthCertificates
```

The exact permission and impact must be established.

---

# Evidence Checklist

For an ESC5 finding record:

```text
Object Name
Distinguished Name
Object Class
PKI Function
Object Owner
Principal
Principal SID
Group Membership Path
ACE Type
Active Directory Rights
Object Type GUID
Inherited Object Type
Inherited / Explicit
Effective Permission
Writable Attributes
Parent Container
Inheritance
Potential Trust Impact
Potential Enrollment Impact
Potential Authentication Impact
Validation Performed
Original Configuration
Cleanup Result
```

---

# ESC5 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify Public Key Services container
- [ ] Enumerate PKI child containers
- [ ] Enumerate Enrollment Services
- [ ] Enumerate Certification Authorities
- [ ] Enumerate NTAuthCertificates
- [ ] Enumerate AIA
- [ ] Enumerate CDP
- [ ] Enumerate OID
- [ ] Enumerate KRA where present
- [ ] Enumerate Certificate Templates container

## ACL Analysis

- [ ] Record object owners
- [ ] Identify GenericAll
- [ ] Identify GenericWrite
- [ ] Identify WriteProperty
- [ ] Identify WriteDACL
- [ ] Identify WriteOwner
- [ ] Identify CreateChild
- [ ] Identify DeleteChild
- [ ] Identify Delete
- [ ] Resolve object-specific ACEs
- [ ] Review inherited ACEs
- [ ] Review explicit ACEs
- [ ] Review Deny ACEs
- [ ] Determine effective permissions

## Principal Analysis

- [ ] Resolve SIDs
- [ ] Resolve nested groups
- [ ] Identify low-privileged principals
- [ ] Identify service accounts
- [ ] Identify legacy delegated groups
- [ ] Identify unexpected owners
- [ ] Review indirect BloodHound paths

## NTAuth

- [ ] Locate NTAuthCertificates
- [ ] Review ACL
- [ ] Review owner
- [ ] Identify unexpected writers
- [ ] Identify unexpected DACL control
- [ ] Review current certificates
- [ ] Treat production modification as high impact

## Enrollment Services

- [ ] Enumerate Enterprise CA objects
- [ ] Review published templates
- [ ] Review CA host names
- [ ] Review ACLs
- [ ] Review owners
- [ ] Distinguish AD object control from CA service control

## Certification Authorities

- [ ] Enumerate CA objects
- [ ] Review ACLs
- [ ] Review owners
- [ ] Review inherited permissions
- [ ] Identify low-privileged control

## OID

- [ ] Enumerate OID objects
- [ ] Review OID ACLs
- [ ] Review OID owners
- [ ] Review `msDS-OIDToGroupLink`
- [ ] Identify unusual issuance-policy relationships
- [ ] Correlate with ESC13 where relevant

## AIA / CDP

- [ ] Enumerate AIA
- [ ] Enumerate CDP
- [ ] Review ACLs
- [ ] Review owners
- [ ] Review child creation rights
- [ ] Review deletion rights
- [ ] Determine chain-building impact
- [ ] Determine revocation impact

## Infrastructure

- [ ] Review CA host administrative access
- [ ] Review CA service accounts
- [ ] Review CA backup locations
- [ ] Review CA private-key protection
- [ ] Review HSM use
- [ ] Review PKI backup protection
- [ ] Separate infrastructure compromise from directory-object findings

## Tooling

- [ ] Enumerate with Certipy
- [ ] Enumerate with PowerShell
- [ ] Review with PowerView where available
- [ ] Review with BloodHound
- [ ] Verify objects with LDAP
- [ ] Resolve security descriptors with appropriate tooling
- [ ] Manually validate automated ESC5 classifications

## Validation

- [ ] Prefer read-only evidence
- [ ] Identify exact object
- [ ] Identify exact permission
- [ ] Identify exact writable property
- [ ] Determine security consequence
- [ ] Do not modify NTAuth merely to prove control
- [ ] Do not modify production OID objects unnecessarily
- [ ] Do not delete AIA/CDP objects
- [ ] Do not extract CA keys merely to prove ESC5
- [ ] Use dedicated test object if active proof is necessary
- [ ] Record baseline before any approved change
- [ ] Restore exact state
- [ ] Verify cleanup

## Detection

- [ ] Enable appropriate Directory Service Changes auditing
- [ ] Monitor event 5136 where applicable
- [ ] Monitor Public Key Services
- [ ] Monitor NTAuthCertificates
- [ ] Monitor Enrollment Services
- [ ] Monitor Certification Authorities
- [ ] Monitor OID
- [ ] Monitor AIA
- [ ] Monitor CDP
- [ ] Monitor PKI ACL changes
- [ ] Monitor owner changes
- [ ] Monitor child creation
- [ ] Monitor child deletion
- [ ] Correlate PKI changes with certificate issuance
- [ ] Correlate certificate issuance with authentication

## Hardening

- [ ] Treat PKI as identity control-plane infrastructure
- [ ] Apply least privilege
- [ ] Restrict GenericAll
- [ ] Restrict GenericWrite
- [ ] Restrict WriteProperty
- [ ] Restrict WriteDACL
- [ ] Restrict WriteOwner
- [ ] Restrict CreateChild
- [ ] Restrict DeleteChild
- [ ] Review parent-container inheritance
- [ ] Remove legacy delegation
- [ ] Separate enrollment from PKI administration
- [ ] Separate template administration from CA administration
- [ ] Protect PKI administrative accounts
- [ ] Harden CA hosts
- [ ] Protect CA private keys
- [ ] Protect PKI backups
- [ ] Use HSMs where appropriate
- [ ] Implement PKI change control
- [ ] Maintain ACL baselines
- [ ] Monitor configuration drift

## Incident Response

- [ ] Identify affected PKI objects
- [ ] Establish modification timeline
- [ ] Identify changed attributes
- [ ] Identify ACL changes
- [ ] Identify owner changes
- [ ] Identify actor
- [ ] Identify source host
- [ ] Determine authentication trust impact
- [ ] Determine enrollment impact
- [ ] Identify certificates issued during exposure
- [ ] Identify certificate authentication
- [ ] Investigate NTAuth changes
- [ ] Investigate OID changes
- [ ] Investigate Enrollment Services changes
- [ ] Investigate CA host access
- [ ] Revoke malicious certificates
- [ ] Restore PKI objects
- [ ] Restore ACLs
- [ ] Restore owners
- [ ] Publish revocation information
- [ ] Evaluate CA recovery if CA key compromise occurred

## Cleanup

- [ ] Restore modified test objects
- [ ] Restore original ACLs
- [ ] Restore original owners
- [ ] Remove temporary test permissions
- [ ] Revoke test certificates where required
- [ ] Delete test PFX files
- [ ] Delete private-key material
- [ ] Re-enumerate affected objects
- [ ] Compare against baseline
- [ ] Verify replication
- [ ] Record cleanup evidence

---

# ESC5 Testing Model

The normal PKI model is:

```text
PKI Administrator
       |
       v
PKI Object
       |
       v
Certificate Trust
```

The ESC5 model is:

```text
Low-Privileged Principal
       |
       v
Dangerous ACL
       |
       v
PKI Object
       |
       v
Trust / Enrollment Control
```

The direct-control model is:

```text
GenericAll / GenericWrite
          |
          v
PKI Object
          |
          v
Security-Sensitive Modification
```

The DACL model is:

```text
WriteDACL
    |
    v
Grant Additional Permission
    |
    v
PKI Object Control
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
PKI Object Control
```

The inheritance model is:

```text
PKI Container
      |
      v
Dangerous Inherited ACE
      |
      +--> Child Object A
      |
      +--> Child Object B
      |
      +--> Child Object C
```

The NTAuth model is:

```text
PKI Object Control
      |
      v
NTAuthCertificates
      |
      v
Enterprise Authentication Trust
```

The OID model is:

```text
PKI Object Control
      |
      v
OID Object
      |
      v
Issuance Policy Relationship
      |
      v
Potential Group / Privilege Relationship
```

The infrastructure model is:

```text
CA Host Control
      |
      v
CA Service / Configuration
      |
      v
CA Private Key
      |
      v
Certificate Trust
```

The safe-testing model is:

```text
Enumerate
   |
   v
Identify PKI Object
   |
   v
Resolve ACL
   |
   v
Confirm Effective Permission
   |
   v
Determine Security Impact
   |
   v
Is Active Proof Necessary?
   |
   +--> No -> Report
   |
   +--> Yes
           |
           v
       Dedicated Test Object
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
PKI Object Change
      |
      v
Trust / Enrollment Change
      |
      v
Certificate Issuance
      |
      v
Certificate Authentication
```

The defensive model is:

```text
Restricted PKI Administration
          +
Protected PKI ACLs
          +
Protected Ownership
          +
Protected CA Hosts
          +
Protected CA Keys
          +
Change Control
          +
Monitoring
          =
Reduced ESC5 Risk
```

For penetration testers:

```text
Do Not Ask:
"Does the tool print ESC5?"

Ask:
"Which PKI object can this principal control,
what security-sensitive behaviour does that
object influence, and what authentication or
trust boundary can be crossed?"
```

For defenders:

```text
Do Not Ask:
"Who administers the CA?"

Also Ask:
"Who can modify the directory objects that
define and support enterprise PKI trust?"
```

The complete ESC5 relationship is:

```text
Principal
   |
   v
Permission
   |
   v
PKI Object
   |
   v
Security-Sensitive Configuration
   |
   v
Certificate Trust / Enrollment
   |
   v
Authentication
   |
   v
Privilege
```

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

Active Directory ACL and ACE abuse:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Active Directory Groups:

[Active Directory Groups](groups.md)

BloodHound:

[BloodHound](bloodhound.md)

Credential Access:

[Active Directory Credential Access](credential-access.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs-esc6.md
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

## Microsoft - Public Key Infrastructure

[Microsoft - Public Key Infrastructure](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate-Based Authentication Hardening

[Microsoft - KB5014754 Certificate-Based Authentication Changes](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

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

ESC5 is broader than a vulnerable certificate template.

It concerns control over the infrastructure that defines:

```text
Which CAs Are Trusted
Which PKI Objects Exist
How Enterprise CAs Are Registered
How Certificate Policies Are Represented
How Certificate Chains Are Built
How Revocation Information Is Distributed
```

The central security problem is:

```text
Untrusted Principal
        |
        v
Trusted PKI Configuration
```

The most important assessment question is therefore not:

```text
"Is ESC5 present?"
```

but:

```text
"Which PKI control-plane object can this
principal modify, and what does that object
allow them to influence?"
```

A `GenericWrite` permission over one PKI object may have a very different impact from `GenericWrite` over another.

For example:

```text
Write Access to Metadata
```

is not equivalent to:

```text
Write Access to Authentication Trust
```

Similarly:

```text
Control of an Enrollment Services AD Object
```

is not automatically equivalent to:

```text
Control of the CA Private Key
```

The assessment must preserve those distinctions.

The complete security model is:

```text
Principal
   |
   v
Effective Permission
   |
   v
PKI Object
   |
   v
Security Function
   |
   v
Possible Modification
   |
   v
Certificate / Trust Impact
   |
   v
Authentication Impact
```

ESC5 is especially important because many of the affected objects live in the:

```text
Configuration Naming Context
```

and therefore belong to forest-wide PKI configuration.

For defenders, the entire:

```text
CN=Public Key Services
```

hierarchy should be treated as privileged identity infrastructure.

For penetration testers, read-only ACL evidence will often demonstrate the risk without making dangerous changes to production PKI.

The strongest ESC5 finding identifies:

```text
The Principal
        +
The Effective Permission
        +
The Exact PKI Object
        +
The Security Function
        +
The Resulting Trust Impact
```

rather than relying solely on the ESC5 label.
