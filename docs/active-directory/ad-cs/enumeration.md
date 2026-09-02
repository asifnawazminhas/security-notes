# Active Directory Certificate Services Enumeration

Active Directory Certificate Services (AD CS) enumeration is the process of discovering and analysing the Public Key Infrastructure (PKI) components connected to an Active Directory environment.

The objective is not simply to answer:

```text
Does AD CS exist?
```

A useful assessment must determine:

```text
Which Certificate Authorities exist?
Which CAs are Enterprise CAs?
Which certificate templates exist?
Which templates are enabled?
Who can enroll?
Who can modify templates?
Which certificates can authenticate?
Which enrollment services are exposed?
How are certificates mapped to identities?
Which CA permissions are delegated?
Which potential ESC conditions exist?
```

A practical workflow is:

```text
Domain Access
     |
     v
Discover PKI
     |
     v
Enumerate CAs
     |
     v
Enumerate Templates
     |
     v
Enumerate Enrollment Rights
     |
     v
Analyse Template Configuration
     |
     v
Analyse CA Configuration
     |
     v
Discover Enrollment Services
     |
     v
Analyse Permissions
     |
     v
Identify Potential ESC Paths
     |
     v
Controlled Validation
```

!!! warning "Authorised testing only"
    AD CS enumeration is usually low impact when limited to LDAP queries and configuration inspection. Certificate requests, CA changes, template modifications, relay testing, and certificate-based authentication are active actions and should only be performed when explicitly authorised.

---

# Enumeration Objectives

A complete AD CS enumeration should identify five major areas:

```text
PKI Infrastructure
Certificate Authorities
Certificate Templates
Enrollment Services
Permissions
```

These combine into the effective trust model:

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
Certification Authority
   |
   v
Certificate
   |
   v
Identity Mapping
   |
   v
Authentication
```

---

# Start with Passive Discovery

Prefer discovery before requesting certificates.

A good sequence is:

```text
LDAP Enumeration
      |
      v
CA Enumeration
      |
      v
Template Enumeration
      |
      v
ACL Analysis
      |
      v
Web Service Discovery
      |
      v
Automated Correlation
```

Only after understanding the environment should active certificate enrollment be considered.

---

# Active Directory PKI Storage

Enterprise PKI configuration is stored within the Active Directory Configuration naming context.

The important base path is:

```text
CN=Public Key Services,
CN=Services,
CN=Configuration,
DC=corp,
DC=example
```

The configuration naming context is forest-wide.

This means:

```text
Forest
  |
  v
Configuration Partition
  |
  v
Public Key Services
  |
  +--> Certification Authorities
  +--> Enrollment Services
  +--> Certificate Templates
  +--> AIA
  +--> CDP
  +--> OID
  +--> KRA
  +--> NTAuthCertificates
```

---

# Obtain the Configuration Naming Context

From a domain-joined Windows system with the Active Directory PowerShell module:

```powershell
(Get-ADRootDSE).configurationNamingContext
```

Example:

```text
CN=Configuration,DC=corp,DC=example
```

Store it:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
```

Build the PKI path:

```powershell
$pkiBase = "CN=Public Key Services,CN=Services,$configNC"

$pkiBase
```

---

# Enumerate Public Key Services

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$pkiBase = "CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $pkiBase -SearchScope OneLevel -Filter * |
    Select-Object Name,ObjectClass,DistinguishedName
```

This provides a useful first view of the PKI containers.

---

# Important PKI Containers

Common containers include:

```text
AIA
CDP
Certificate Templates
Certification Authorities
Enrollment Services
KRA
OID
NTAuthCertificates
```

Each has a different role.

---

# Certification Authorities Container

The following path contains trusted enterprise CA information:

```text
CN=Certification Authorities,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate it:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$caBase = "CN=Certification Authorities,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $caBase -Filter * -Properties * |
    Select-Object Name,ObjectClass,DistinguishedName
```

---

# Enrollment Services Container

Enterprise CA objects are particularly important under:

```text
CN=Enrollment Services,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties * |
    Select-Object Name,dNSHostName,certificateTemplates,DistinguishedName
```

This can reveal:

```text
CA Name
CA Host
Published Templates
Directory Object
```

---

# Why Enrollment Services Matters

The Enrollment Services objects connect:

```text
Enterprise CA
     |
     v
Active Directory
     |
     v
Published Templates
```

A certificate template may exist in Active Directory but still not be issued by a particular CA.

Therefore:

```text
Template Exists
      |
      X
Template Is Necessarily Issued
```

You must identify which CA publishes it.

---

# Enumerate CA Names

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties dNSHostName |
    Select-Object Name,dNSHostName
```

Example:

```text
Name          dNSHostName
----          -----------
CORP-CA01     ca01.corp.example
CORP-CA02     ca02.corp.example
```

---

# Enumerate Published Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates |
    Select-Object Name,certificateTemplates
```

The:

```text
certificateTemplates
```

attribute lists templates published by the Enterprise CA.

---

# Flatten Published Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

$cas = Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates

foreach ($ca in $cas) {
    foreach ($template in $ca.certificateTemplates) {
        [PSCustomObject]@{
            CA       = $ca.Name
            Template = $template
        }
    }
}
```

This makes it easier to correlate:

```text
CA
 |
 v
Template
```

---

# Native CA Discovery

Windows provides:

```text
certutil.exe
```

for certificate and CA administration.

Start with:

```cmd
certutil -?
```

A useful enterprise CA discovery command is:

```cmd
certutil -config - -ping
```

This can help identify available Enterprise CA configurations.

---

# Enumerate CA Configuration

If a CA is known:

```cmd
certutil -config "ca01.corp.example\CORP-CA01" -ping
```

This verifies connectivity to the CA configuration.

Use the exact CA configuration discovered in the environment.

---

# certutil CA Information

Depending on permissions and environment configuration, useful commands include:

```cmd
certutil -CAInfo
```

and:

```cmd
certutil -getreg
```

The latter is administrative and may expose substantial CA configuration.

Do not assume every assessment identity can query every CA registry setting remotely.

---

# Certification Authority Console

Where administrative GUI access is authorised:

```text
certsrv.msc
```

can expose:

```text
Issued Certificates
Revoked Certificates
Pending Requests
Failed Requests
Certificate Templates
CA Properties
Security
```

This is useful during white-box assessments.

---

# Certificate Templates Console

Certificate templates can be reviewed with:

```text
certtmpl.msc
```

Important tabs include:

```text
General
Compatibility
Request Handling
Cryptography
Subject Name
Extensions
Security
Issuance Requirements
Superseded Templates
```

For a security review, do not examine only:

```text
Security
```

The dangerous conditions often arise from combinations of several tabs.

---

# Certificate Templates Container

Templates are stored beneath:

```text
CN=Certificate Templates,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

Enumerate them:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties * |
    Select-Object Name,DisplayName,DistinguishedName
```

---

# Count Certificate Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)').Count
```

This provides a quick idea of PKI size.

---

# Template Versions

Certificate template versions determine available capabilities.

Common versions encountered include:

```text
Version 1
Version 2
Version 3
Version 4
```

Version alone does not determine whether a template is vulnerable.

Security analysis must examine the actual configuration.

---

# Template Schema Version

One useful attribute is:

```text
msPKI-Template-Schema-Version
```

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Template-Schema-Version' |
    Select-Object Name,'msPKI-Template-Schema-Version'
```

---

# Important Template Attributes

AD CS template analysis commonly requires attributes such as:

```text
displayName
pKIExtendedKeyUsage
msPKI-Certificate-Name-Flag
msPKI-Enrollment-Flag
msPKI-Private-Key-Flag
msPKI-RA-Signature
msPKI-RA-Application-Policies
msPKI-Certificate-Application-Policy
pKIExpirationPeriod
pKIOverlapPeriod
nTSecurityDescriptor
```

The exact interpretation of bit flags should be based on Microsoft protocol and schema documentation rather than guessed from raw decimal values.

---

# Enumerate Extended Key Usage

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage |
    Select-Object Name,pKIExtendedKeyUsage
```

---

# Common EKU OIDs

Common values include:

```text
1.3.6.1.5.5.7.3.1
Server Authentication

1.3.6.1.5.5.7.3.2
Client Authentication

1.3.6.1.5.5.7.3.3
Code Signing

1.3.6.1.5.5.7.3.4
Secure Email

1.3.6.1.4.1.311.20.2.2
Smart Card Logon

1.3.6.1.4.1.311.20.2.1
Certificate Request Agent
```

During assessment, authentication-related EKUs deserve particular attention.

---

# Client Authentication

A common authentication EKU is:

```text
1.3.6.1.5.5.7.3.2
```

which represents:

```text
Client Authentication
```

A template containing this EKU may potentially issue certificates usable for client authentication.

That does not automatically make the template vulnerable.

---

# Smart Card Logon

Another important OID is:

```text
1.3.6.1.4.1.311.20.2.2
```

representing:

```text
Smart Card Logon
```

This is relevant to Windows certificate-based authentication.

---

# Certificate Request Agent

The OID:

```text
1.3.6.1.4.1.311.20.2.1
```

represents:

```text
Certificate Request Agent
```

This is particularly important when reviewing enrollment-agent functionality.

---

# Any Purpose

The Any Purpose EKU is:

```text
2.5.29.37.0
```

Templates configured for broad usage require careful review.

---

# No EKU

Do not assume:

```text
No EKU
   =
No Security Impact
```

In Windows PKI, certificates without an EKU restriction may have broad applicability depending on context.

Analyse the certificate and authentication path rather than relying only on the presence of a specific EKU.

---

# Enumerate Authentication-Capable Templates

A basic LDAP filter can help locate templates explicitly containing the Client Authentication EKU:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(pKIExtendedKeyUsage=1.3.6.1.5.5.7.3.2)' -Properties pKIExtendedKeyUsage |
    Select-Object Name,pKIExtendedKeyUsage
```

This is only one discovery method.

It will not identify every potentially authentication-capable configuration.

---

# Subject Name Configuration

A critical template property is:

```text
msPKI-Certificate-Name-Flag
```

This controls aspects of how certificate subject information is constructed.

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Certificate-Name-Flag' |
    Select-Object Name,'msPKI-Certificate-Name-Flag'
```

---

# Supply Subject in Request

One security-sensitive configuration allows the requester to provide subject information.

Conceptually:

```text
Requester
   |
   v
Certificate Request
   |
   +--> Subject
   +--> SAN
```

rather than the CA deriving all identity information from Active Directory.

This capability becomes dangerous when combined with:

```text
Broad Enrollment
+
Authentication Capability
+
No Sufficient Approval
+
Unsafe Identity Mapping
```

---

# Do Not Analyse Subject Flags Alone

The following is incomplete:

```text
Supply Subject
      |
      v
Vulnerable
```

Instead analyse:

```text
Supply Subject
      +
Enrollment Rights
      +
EKU / Application Policy
      +
Issuance Requirements
      +
CA Configuration
      +
Certificate Mapping
      =
Potential Impact
```

---

# Enrollment Flags

Another important attribute is:

```text
msPKI-Enrollment-Flag
```

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Enrollment-Flag' |
    Select-Object Name,'msPKI-Enrollment-Flag'
```

Enrollment flags influence certificate issuance behaviour.

---

# Manager Approval

Certificate templates can require:

```text
CA Certificate Manager Approval
```

A request may then remain:

```text
Pending
```

instead of being immediately issued.

Conceptually:

```text
Request
   |
   v
Pending
   |
   v
CA Manager
   |
   v
Approve / Deny
```

This can significantly affect exploitability.

---

# Authorized Signatures

Templates may require authorized signatures.

The attribute:

```text
msPKI-RA-Signature
```

is relevant.

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-RA-Signature' |
    Select-Object Name,'msPKI-RA-Signature'
```

A non-zero required-signature count can materially change an attack path.

---

# Enrollment Agent Policies

Enrollment-agent templates and restrictions deserve separate analysis.

Look for:

```text
Certificate Request Agent EKU
Enrollment Agent Restrictions
RA Application Policies
Authorized Signatures
```

These relationships become important for ESC3-style paths.

---

# Private Key Configuration

The attribute:

```text
msPKI-Private-Key-Flag
```

contains private-key related template settings.

Enumerate:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Private-Key-Flag' |
    Select-Object Name,'msPKI-Private-Key-Flag'
```

Private-key exportability may increase credential portability.

---

# Template Validity Period

Certificate validity is stored using attributes such as:

```text
pKIExpirationPeriod
```

and renewal overlap through:

```text
pKIOverlapPeriod
```

Raw values are encoded intervals.

Tools such as Certipy can make these easier to interpret.

Long certificate lifetimes increase the duration of potential credential exposure.

---

# Template ACLs

Certificate templates are Active Directory objects.

Therefore they have:

```text
Owner
DACL
ACEs
```

just like other directory objects.

This means an otherwise secure template may become exploitable if an attacker can modify it.

---

# Retrieve Template ACL

Using the Active Directory provider:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=User,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-Acl "AD:$templateDN" |
    Format-List
```

Replace:

```text
User
```

with the actual template CN.

---

# Enumerate Template ACEs

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=User,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,IsInherited
```

Look for excessive rights assigned to low-privileged principals.

---

# Important Template Rights

Security-sensitive rights include:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

These may enable modification of certificate-template security-sensitive properties.

---

# Enrollment Extended Rights

Enrollment permissions are represented through Active Directory extended rights.

A template ACL may therefore contain rights corresponding to:

```text
Enroll
Autoenroll
```

These should be interpreted carefully rather than treating every extended right as equivalent.

---

# PowerView

PowerView can help inspect certificate-template ACLs because templates are Active Directory objects.

For example:

```powershell
Get-DomainObjectAcl -Identity 'CN=User,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' -ResolveGUIDs
```

Exact behaviour depends on the PowerView version being used.

See:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

---

# Template Ownership

Determine who owns security-sensitive templates.

Using PowerShell:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=User,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Owner
```

Unexpected ownership should be investigated.

---

# CA Object ACL

Enterprise CA objects in:

```text
Enrollment Services
```

also have Active Directory security descriptors.

Enumerate an object:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$caDN = "CN=CORP-CA01,CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-Acl "AD:$caDN" |
    Format-List
```

Remember that directory-object control is not necessarily identical to administrative control of the CA service itself.

Both should be reviewed.

---

# CA Service Permissions

CA service permissions can include powerful administrative capabilities such as:

```text
Manage CA
Manage Certificates
```

These are distinct from template enrollment rights.

Certipy can help enumerate and correlate these permissions.

---

# NTAuthCertificates

The:

```text
NTAuthCertificates
```

enterprise object is important to Windows certificate-based authentication.

Conceptually:

```text
Enterprise CA Certificate
        |
        v
NTAuth Store
        |
        v
Enterprise Authentication Trust
```

Enumerate the container:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$ntAuthBase = "CN=NTAuthCertificates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -Identity $ntAuthBase -Properties *
```

Changes to enterprise authentication trust should be treated as highly sensitive.

---

# AIA

Authority Information Access:

```text
AIA
```

helps clients locate CA certificates and related issuer information.

The Active Directory AIA container is:

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

# CDP

CRL Distribution Points:

```text
CDP
```

identify locations from which certificate revocation information can be obtained.

The Active Directory container is:

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

# OID Container

Certificate templates and application policies use:

```text
Object Identifiers
```

or:

```text
OIDs
```

Enterprise OID objects can be found beneath:

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
    Select-Object Name,DisplayName,DistinguishedName
```

OID relationships become particularly important for some advanced AD CS attack paths.

---

# KRA

Key Recovery Agent functionality may also appear within the PKI configuration.

KRA-related configuration deserves review where organisations use:

```text
Private Key Archival
Key Recovery
```

These mechanisms can involve highly sensitive private-key material.

---

# LDAP Enumeration from Linux

AD CS can be enumerated without Windows tooling because the relevant Enterprise PKI configuration is stored in Active Directory.

First determine the configuration naming context.

Example:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b '' \
    -s base \
    configurationNamingContext
```

Expected result:

```text
configurationNamingContext: CN=Configuration,DC=corp,DC=example
```

---

# Enumerate Enterprise CAs with ldapsearch

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

This can identify Enterprise CA objects and published templates.

---

# Enumerate Templates with ldapsearch

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
    msPKI-Certificate-Name-Flag \
    msPKI-Enrollment-Flag \
    msPKI-Private-Key-Flag \
    msPKI-RA-Signature
```

---

# LDAP over TLS

Where LDAPS is available:

```bash
ldapsearch \
    -x \
    -H ldaps://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(objectClass=pKICertificateTemplate)' \
    cn \
    displayName
```

Use the authentication and TLS configuration appropriate to the assessment environment.

---

# Certipy

Certipy is one of the primary tools used for AD CS security enumeration.

Its:

```text
find
```

command can discover and analyse:

```text
Certificate Authorities
Certificate Templates
Enrollment Permissions
CA Permissions
Template Configuration
Potential ESC Conditions
```

Always begin with:

```bash
certipy find -h
```

because command-line options change between releases.

---

# Certipy Basic Enumeration

A common authenticated workflow is conceptually:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10
```

Use an approved assessment identity.

Avoid placing real passwords in shell history when safer authentication methods are available.

---

# Certipy JSON Output

For structured analysis:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -json
```

Structured output is useful for:

```text
Evidence Review
Automation
Comparisons
Reporting
```

---

# Certipy Text Output

Where supported by the installed version:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -text
```

Check:

```bash
certipy find -h
```

for exact output options.

---

# Certipy Standard Output

For quick review:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

This can be useful during manual analysis.

---

# Enabled Templates

Modern Certipy versions support filtering around enabled templates.

Inspect:

```bash
certipy find -h
```

and use the enabled-template filter supported by the installed release.

This is useful because:

```text
Template Exists
      |
      X
Template Is Currently Issuable
```

---

# Potentially Vulnerable Templates

Certipy can also filter or highlight configurations it considers potentially vulnerable.

Use:

```bash
certipy find -h
```

to confirm the current syntax.

Treat the result as:

```text
Candidate Finding
```

not:

```text
Confirmed Vulnerability
```

---

# Certipy Authentication Options

Depending on version and environment, Certipy may support authentication using:

```text
Password
NT Hash
Kerberos
AES Key
Existing Ticket
SSPI
```

Inspect:

```bash
certipy find -h
```

before selecting the method.

---

# Kerberos Enumeration

Where Kerberos authentication is appropriate, Certipy can use Kerberos-capable authentication options supported by the installed release.

This is useful in environments where:

```text
NTLM Is Restricted
```

or where an existing Kerberos context is already available.

---

# Certipy and DNS

AD CS tooling is sensitive to:

```text
DNS
Domain Names
CA Hostnames
Domain Controller Names
```

If Certipy cannot resolve the environment correctly, do not immediately conclude that AD CS is absent.

Verify:

```bash
nslookup dc01.corp.example
```

or:

```bash
dig dc01.corp.example
```

and review the Certipy target and DNS options shown by:

```bash
certipy find -h
```

---

# Certipy CA Enumeration

Certipy output should be reviewed for each CA.

Important fields include:

```text
CA Name
DNS Name
Certificate Subject
Certificate Serial Number
Validity
Web Enrollment
Request Disposition
CA Permissions
Published Templates
```

Exact fields depend on Certipy version.

---

# Certipy Template Enumeration

For each template review:

```text
Template Name
Display Name
Certificate Authorities
Enabled
Client Authentication
Enrollment Rights
Extended Key Usage
Subject Name Flags
Enrollment Flags
Private Key Flags
Authorized Signatures
Manager Approval
Template Permissions
```

---

# Do Not Blindly Trust ESC Labels

Automated tools are extremely useful, but the assessment workflow should be:

```text
Certipy Candidate
      |
      v
Manual Template Review
      |
      v
Permission Validation
      |
      v
CA Publication Validation
      |
      v
Certificate Mapping Review
      |
      v
Impact Determination
```

This is especially important on modern Windows environments where certificate mapping behaviour and security updates can affect exploitability.

---

# Certipy and BloodHound

Depending on versions, AD CS enumeration data may be integrated into BloodHound workflows.

BloodHound can help visualise relationships such as:

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
Certificate Authority
   |
   v
Authentication Path
```

Always confirm graph assumptions against the actual PKI configuration.

---

# BloodHound

BloodHound is particularly valuable when AD CS permissions interact with broader Active Directory relationships.

For example:

```text
User
 |
 v
MemberOf
 |
 v
PKI Enrollment Group
 |
 v
Enroll
 |
 v
Authentication Template
```

or:

```text
User
 |
 v
GenericWrite
 |
 v
Certificate Template
```

---

# BloodHound Collection

Use the collector version appropriate to the BloodHound deployment.

Do not assume an old SharpHound or community collector captures every modern AD CS relationship.

Verify current collector documentation before relying on AD CS graph coverage.

See:

[BloodHound](../bloodhound.md)

---

# Manual Web Enrollment Discovery

A CA host may expose:

```text
/certsrv/
```

through CA Web Enrollment.

For example:

```text
https://ca01.corp.example/certsrv/
```

The existence of this endpoint should be recorded.

Do not assume its existence alone means:

```text
ESC8
```

---

# Test Web Reachability

From Linux:

```bash
curl -k -I https://ca01.corp.example/certsrv/
```

or:

```bash
curl -I http://ca01.corp.example/certsrv/
```

Use only against authorised hosts.

A response such as:

```text
401 Unauthorized
```

may still confirm that the endpoint exists and requires authentication.

---

# HTTP vs HTTPS

Record whether enrollment services are exposed over:

```text
HTTP
```

or:

```text
HTTPS
```

This matters when analysing relay exposure and transport security.

---

# IIS Authentication

Where authorised, inspect whether the endpoint supports:

```text
Negotiate
NTLM
Basic
Certificate Authentication
```

The presence of Windows Authentication should trigger further analysis of relay protections.

---

# Extended Protection for Authentication

For Windows-authenticated web services, determine whether:

```text
Extended Protection for Authentication
```

or:

```text
EPA
```

is configured where applicable.

This is important when analysing NTLM relay exposure.

---

# Web Enrollment Is Not Automatically ESC8

The following conclusion is incorrect:

```text
/certsrv/ Exists
      |
      v
ESC8
```

Instead analyse:

```text
Enrollment Endpoint
      +
Authentication
      +
NTLM
      +
EPA
      +
Enrollment Rights
      +
Victim Identity
      +
Template Availability
      =
Relay Exposure
```

---

# Certificate Enrollment Web Service

Look for:

```text
Certificate Enrollment Web Service
```

or:

```text
CES
```

This is separate from classic:

```text
/certsrv/
```

web enrollment.

---

# Certificate Enrollment Policy Web Service

Also identify:

```text
CEP
```

or:

```text
Certificate Enrollment Policy Web Service
```

CEP provides enrollment policy information.

CES performs certificate enrollment.

The distinction is:

```text
CEP
 |
 v
Which Certificates Can I Request?
```

versus:

```text
CES
 |
 v
Submit Certificate Request
```

---

# NDES

Identify whether:

```text
Network Device Enrollment Service
```

is deployed.

NDES implements:

```text
SCEP
```

and can create additional certificate enrollment paths.

A complete AD CS assessment should record:

```text
NDES Host
Authentication
Network Exposure
SCEP Configuration
Service Account
Certificate Templates
```

---

# Network Enumeration

After identifying CA hosts, enumerate only the relevant services.

For example:

```bash
nmap -Pn -p 80,443,135,445 ca01.corp.example
```

This can identify:

```text
HTTP
HTTPS
RPC
SMB
```

associated with common AD CS administration and enrollment paths.

Do not broadly scan outside the authorised scope.

---

# DNS Enumeration

Resolve CA hosts:

```bash
dig ca01.corp.example
```

or:

```bash
nslookup ca01.corp.example
```

Verify that tool failures are not caused by incorrect DNS configuration.

---

# Enumerate Current User Certificates

On Windows:

```powershell
Get-ChildItem Cert:\CurrentUser\My |
    Select-Object Subject,Issuer,Thumbprint,NotBefore,NotAfter,HasPrivateKey
```

This can reveal certificates already issued to the current user.

---

# Enumerate Machine Certificates

```powershell
Get-ChildItem Cert:\LocalMachine\My |
    Select-Object Subject,Issuer,Thumbprint,NotBefore,NotAfter,HasPrivateKey
```

Administrative permissions may be required to access some private-key material, but certificate metadata is often available.

---

# Identify Internal CA Issuers

Search certificate stores for internal issuers:

```powershell
Get-ChildItem Cert:\CurrentUser\My,Cert:\LocalMachine\My |
    Select-Object Subject,Issuer,Thumbprint,NotAfter
```

Internal issuer names can provide useful PKI discovery clues.

---

# Enumerate Root Certificates

```powershell
Get-ChildItem Cert:\LocalMachine\Root |
    Select-Object Subject,Issuer,Thumbprint,NotAfter
```

This can reveal enterprise trust anchors.

Do not assume every trusted root belongs to AD CS.

---

# Enumerate Enterprise Trust

```cmd
certutil -enterprise -viewstore Root
```

and related certutil store operations can assist administrators and assessors in understanding enterprise certificate trust.

Review:

```cmd
certutil -?
```

for the installed Windows version.

---

# Enumerate Certificate Details

For a certificate file:

```cmd
certutil -dump certificate.cer
```

This can reveal:

```text
Subject
Issuer
Serial Number
Validity
Extensions
EKUs
SAN
Template Information
```

---

# Certificate Template Information in Issued Certificates

Issued enterprise certificates may contain template information.

This can help correlate:

```text
Certificate
   |
   v
Template
   |
   v
CA
```

Useful during incident response and assessment validation.

---

# Search for PFX Files

During an authorised credential exposure review, certificate files may exist on endpoints or shares.

Common extensions include:

```text
.pfx
.p12
.pem
.key
.cer
.crt
```

The existence of a certificate file does not mean it contains a private key.

---

# PFX Files

A:

```text
.pfx
```

or:

```text
.p12
```

file may contain:

```text
Certificate
Private Key
Certificate Chain
```

Treat such files as potentially sensitive credentials.

---

# Do Not Collect Private Keys Unnecessarily

For enumeration, you usually need:

```text
Metadata
Configuration
Permissions
```

not:

```text
Private Keys
```

Prefer:

```text
Identify
```

over:

```text
Extract
```

unless credential-access testing is explicitly required.

---

# CA Certificate

Retrieve and inspect CA certificates only through approved methods.

Important properties include:

```text
Subject
Issuer
Serial Number
Validity
Public Key
Signature Algorithm
CA Extensions
CRL Distribution Points
AIA
```

The public CA certificate is not itself a secret.

---

# CA Private Key

The corresponding:

```text
CA Private Key
```

is highly sensitive.

Do not attempt to export it during ordinary AD CS enumeration.

CA private-key access belongs to a separate high-impact assessment category.

---

# CRL Distribution Points

Inspect certificates for:

```text
CRL Distribution Points
```

These may reveal PKI infrastructure hostnames and URLs.

For a certificate:

```cmd
certutil -dump certificate.cer
```

Review:

```text
CRL Distribution Points
```

---

# Authority Information Access

Likewise inspect:

```text
Authority Information Access
```

for issuer and OCSP information.

This can reveal:

```text
CA URLs
OCSP URLs
PKI Hostnames
```

---

# PKI DNS Names

During enumeration, maintain a list such as:

```text
ca01.corp.example
pki.corp.example
ocsp.corp.example
scep.corp.example
enroll.corp.example
```

Resolve and classify each system.

---

# PKI Inventory

Create an inventory such as:

```text
Host                Role
----                ----
ca01                Enterprise Issuing CA
rootca01            Offline Root CA
pki01               Web Enrollment
ocsp01              Online Responder
ndes01              NDES
```

Do not assume all services are hosted on the CA itself.

---

# Template Inventory

Create a separate template inventory:

```text
Template             Enabled    Authentication    Broad Enroll
--------             -------    --------------    ------------
User                 Yes        Yes               No
WorkstationAuth      Yes        Yes               Yes
WebServer            Yes        No                No
CodeSigning          No         No                No
```

Then investigate the interesting combinations.

---

# Prioritising Templates

Prioritise templates with combinations such as:

```text
Broad Enrollment
+
Authentication Capability
```

or:

```text
Low-Privilege Write Access
+
Template Enabled
```

or:

```text
Enrollment Agent Capability
+
Broad Enrollment
```

or:

```text
Weak Issuance Requirements
+
Sensitive Certificate Purpose
```

---

# Broad Enrollment

Broad principals may include:

```text
Domain Users
Domain Computers
Authenticated Users
Everyone
Large Business Groups
```

Broad enrollment is not automatically a vulnerability.

It becomes important when combined with dangerous certificate capabilities.

---

# Template Modification Paths

A useful model is:

```text
Attacker
   |
   v
GenericWrite / GenericAll
   |
   v
Certificate Template
   |
   v
Modify Security-Sensitive Setting
   |
   v
Enroll
```

This is why ACL analysis belongs in AD CS enumeration.

---

# Enrollment Group Control

An attacker may not directly have:

```text
Enroll
```

but may control a group that does.

Example:

```text
Attacker
   |
   v
AddMember
   |
   v
PKI-Enrollment-Users
   |
   v
Enroll
   |
   v
Template
```

BloodHound is useful for identifying these indirect relationships.

---

# Nested Group Membership

Always resolve nested group membership.

A template might grant enrollment to:

```text
PKI-Users
```

while:

```text
Domain Users
```

is nested into:

```text
PKI-Users
```

The effective enrollment population is therefore larger than the ACL initially suggests.

---

# Effective Permissions

The question is not:

```text
What does the template ACL say?
```

The question is:

```text
Who effectively has the right?
```

Consider:

```text
Direct ACEs
Inherited ACEs
Nested Groups
Object Ownership
WriteDACL
WriteOwner
Group Control
```

---

# CA Publication

After identifying an interesting template, verify whether it is actually published by an Enterprise CA.

Conceptually:

```text
Interesting Template
       |
       v
Published?
       |
       +--> No -> Not Currently Issuable Through That CA
       |
       +--> Yes -> Continue Analysis
```

---

# Multiple CAs

A forest may contain multiple CAs.

Example:

```text
Template A
   |
   +--> CA01
   |
   +--> CA02
```

The CA configurations may differ.

Therefore analyse each:

```text
Template + CA
```

combination rather than the template alone.

---

# Certificate Mapping

Modern AD CS assessments must include certificate mapping.

A certificate may contain:

```text
Subject
SAN
UPN
SID Extension
Issuer Information
```

but the actual authentication result depends on how Windows maps the certificate to an account.

---

# Strong Mapping

Current Windows hardening places greater emphasis on strong certificate mapping.

Do not rely on older assumptions that arbitrary:

```text
UPN
```

or:

```text
Subject
```

information will always map directly to a privileged identity.

Validate against the actual patched environment.

---

# SID Security Extension

Modern Windows certificate authentication can make use of SID-related certificate information for stronger mapping.

This has materially changed some historical AD CS abuse assumptions.

Therefore:

```text
Template Looks Like Old ESC Path
        |
        X
Guaranteed Exploitation
```

Always analyse current certificate mapping behaviour.

---

# Domain Controller Certificates

Domain Controllers often possess certificates used for:

```text
Kerberos PKINIT
LDAPS
Smart Card Authentication Infrastructure
```

depending on deployment.

Enumerating DC certificate capability helps explain whether certificate-based domain authentication is available.

---

# PKINIT Availability

Certificate-based Kerberos authentication commonly depends on the KDC possessing a suitable certificate.

Conceptually:

```text
Client Certificate
       |
       v
PKINIT
       |
       v
Domain Controller / KDC
       |
       v
TGT
```

Do not assume PKINIT works merely because an Enterprise CA exists.

---

# LDAPS

Domain Controller certificates may also enable:

```text
LDAPS
```

commonly on:

```text
TCP/636
```

and Global Catalog TLS on:

```text
TCP/3269
```

Check connectivity:

```powershell
Test-NetConnection dc01.corp.example -Port 636
```

or from Linux:

```bash
nmap -Pn -p 636,3269 dc01.corp.example
```

---

# AD CS and Authentication Coercion

During enumeration, identify enrollment services that could become relay destinations.

The relationship is:

```text
Coercion Source
      |
      v
Authentication
      |
      v
Enrollment Service
      |
      v
Certificate
```

See:

[Authentication Coercion](../authentication-coercion.md)

---

# AD CS and NTLM Relay

Record:

```text
Web Enrollment
HTTP / HTTPS
NTLM
EPA
Template Availability
```

because these influence relay feasibility.

See:

[NTLM Relay](../ntlm-relay.md)

---

# AD CS and ACL Enumeration

Certificate templates should be incorporated into the broader ACL assessment.

Review:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
Owner
Enroll
Autoenroll
```

See:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

---

# AD CS and Credential Access

Enumeration may identify:

```text
Existing Certificates
PFX Files
Private-Key Locations
Service Certificates
```

Do not automatically extract them.

See:

[Active Directory Credential Access](../credential-access.md)

---

# AD CS and Shadow Credentials

Shadow Credentials use:

```text
msDS-KeyCredentialLink
```

rather than certificate templates.

However, both techniques involve certificate or public-key based Active Directory authentication concepts.

Do not classify Shadow Credentials as an ESC template vulnerability.

See:

[Active Directory Shadow Credentials](../shadow-credentials.md)

---

# AD CS and BloodHound

Use BloodHound to answer:

```text
Who Can Enroll?
Who Can Modify the Template?
Who Controls Those Groups?
What Privilege Does the Resulting Identity Have?
```

This moves the assessment from:

```text
PKI Misconfiguration
```

to:

```text
Active Directory Attack Path
```

---

# ESC Triage

After enumeration, organise candidate paths.

A useful worksheet is:

```text
ESC    Candidate    CA    Template    Principal    Validated
---    ---------    --    --------    ---------    ---------
1      Yes          CA1   TemplateA   Domain Users No
4      Yes          CA1   TemplateB   Helpdesk     No
8      Yes          CA1   N/A         N/A          No
```

Do not mark a candidate as validated until the required conditions are confirmed.

---

# ESC1 Triage

Look for combinations involving:

```text
Enrollment Rights
+
Requester-Controlled Subject Information
+
Authentication Capability
+
No Sufficient Approval Barrier
```

Modern certificate mapping behaviour must also be considered.

---

# ESC2 Triage

Look for certificates with unusually broad purposes such as:

```text
Any Purpose
```

or configurations whose usage is insufficiently constrained.

The exact impact depends on the resulting certificate and environment.

---

# ESC3 Triage

Identify:

```text
Certificate Request Agent
```

capability and enrollment-agent workflows.

Then determine:

```text
Who Can Obtain Agent Certificate?
What Templates Can Agent Request?
For Which Identities?
What Restrictions Exist?
```

---

# ESC4 Triage

Review whether low-privileged principals can modify a certificate template.

Look for:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

A safe template may become dangerous after modification.

---

# ESC5 Triage

Review control over broader PKI infrastructure and AD CS-related objects.

This includes permissions outside one individual template.

---

# ESC6 Triage

Review CA-wide settings affecting subject alternative name handling and certificate requests.

Do not change CA configuration merely to prove the condition.

Configuration evidence should normally be sufficient.

---

# ESC7 Triage

Review:

```text
CA Administrative Rights
Certificate Manager Rights
```

and determine what those permissions permit under the current CA configuration.

---

# ESC8 Triage

Review:

```text
HTTP Enrollment
Windows Authentication
NTLM
EPA
Relay Feasibility
Victim Enrollment Rights
```

Do not classify every `/certsrv/` endpoint as ESC8.

---

# ESC9 and ESC10 Triage

These categories depend heavily on certificate mapping and authentication behaviour.

Because Microsoft has hardened certificate mapping over time, assess them against:

```text
Current Domain Controller Patches
Current Mapping Mode
Certificate Extensions
Template Configuration
```

rather than relying on old examples.

---

# ESC11 Triage

Review certificate enrollment RPC security and whether authentication to certificate enrollment interfaces can be relayed under the current configuration.

Confirm current platform and tool behaviour before active testing.

---

# ESC12 Triage

Review CA private-key protection and storage architecture.

This may include:

```text
Software Key Storage
HSM
CA Backups
Hardware Protection
```

Do not attempt private-key extraction during routine enumeration.

---

# ESC13 Triage

Review issuance policies and OID-linked group relationships.

This requires careful correlation of:

```text
Template
Application / Issuance Policy
OID Object
Group
```

Do not infer the path solely from an OID name.

---

# ESC14 Triage

Review explicit certificate mapping and directory permissions that can affect mapping configuration.

This is an advanced certificate-mapping attack path and should be analysed separately.

---

# ESC15 Triage

Review schema-version and application-policy behaviour associated with current ESC15 research.

Because this category is newer than the original Certified Pre-Owned taxonomy, verify current research and tooling before testing.

---

# Do Not Force Every Environment into ESC Numbers

The ESC taxonomy is useful, but the broader goal is:

```text
Identify Certificate Trust Failure
```

An organisation may have a certificate-related security problem that does not cleanly map to one ESC number.

Report the underlying condition.

---

# Safe Validation Hierarchy

Use:

```text
1. LDAP Evidence
2. ACL Evidence
3. CA Publication Evidence
4. Tool Correlation
5. Test Account Enrollment
6. Certificate Authentication
7. Stop
```

Avoid jumping directly to:

```text
Privileged Certificate
```

when configuration evidence already demonstrates the issue.

---

# Example Low-Impact Validation

Suppose enumeration identifies:

```text
Template:
CorpUserAuth

Enrollment:
ADCS-Testers

Subject:
Requester supplied

EKU:
Client Authentication
```

If a dedicated test identity belongs to:

```text
ADCS-Testers
```

a controlled test may request a certificate representing only the approved test identity.

This confirms:

```text
Enrollment Works
```

without impersonating a privileged user.

---

# When Privileged Impersonation Is Necessary

Sometimes the finding specifically concerns the ability to request a certificate for another identity.

Before testing:

```text
Confirm Written Authorisation
Use Minimum Privileged Target Necessary
Avoid Domain Administrator Where Possible
Request One Certificate
Authenticate Once
Stop
Revoke / Remove Test Material
```

---

# Evidence Collection

For every candidate template record:

```text
CA
Template
Template DN
Published
Enrollment Rights
Template Owner
Template ACL
EKUs
Application Policies
Subject Name Flags
Enrollment Flags
Private Key Flags
Manager Approval
Authorized Signatures
Validity
Potential ESC
```

---

# Evidence for Web Services

Record:

```text
Host
URL
HTTP / HTTPS
Status Code
Authentication Methods
EPA
TLS
CA Association
Enrollment Function
```

Do not include reusable credentials in screenshots or reports.

---

# Evidence for CA Permissions

Record:

```text
CA
Principal
Permission
Inherited?
Source
Potential Impact
```

Examples:

```text
Manage CA
Manage Certificates
```

should be treated as sensitive.

---

# Evidence for Template ACLs

Record:

```text
Template
Principal
Right
Inherited?
Effective Through Group?
Owner
Potential Modification
```

This makes the attack path reproducible without modifying the template.

---

# Detection Opportunities

Enumeration itself may be relatively quiet, especially when performed through ordinary LDAP reads.

Active AD CS activity can generate more useful telemetry.

Monitor:

```text
Certificate Requests
Certificate Issuance
Template Changes
CA Changes
PKI ACL Changes
Web Enrollment Authentication
Certificate Authentication
```

---

# Directory Service Changes

Changes to PKI objects can produce:

```text
5136
```

when appropriate Directory Service Changes auditing is configured.

Monitor sensitive attributes on:

```text
Certificate Templates
Enrollment Services
OID Objects
NTAuthCertificates
```

---

# Template ACL Changes

Changes involving:

```text
nTSecurityDescriptor
```

or ownership of certificate templates should be treated as security-sensitive.

Monitor for unexpected:

```text
WriteDACL
WriteOwner
Permission Changes
```

---

# CA Configuration Changes

CA-level security changes should be monitored separately from directory template changes.

Important examples include:

```text
CA Security
Request Disposition
Enrollment Agent Restrictions
Subject Alternative Name Behaviour
Web Enrollment Configuration
```

---

# Baseline the PKI

A strong defensive practice is maintaining an approved PKI inventory.

For example:

```text
Approved CAs
Approved Templates
Approved Enrollment Groups
Approved Template Owners
Approved CA Administrators
Approved Enrollment Services
Approved EKUs
```

Then detect deviations.

---

# Compare Over Time

PKI configuration should be periodically compared against a known-good baseline.

Conceptually:

```text
Known Good PKI
      |
      v
Current PKI
      |
      v
Difference
      |
      v
Review
```

This is particularly valuable because template modifications may be subtle.

---

# Hardening from Enumeration Results

Enumeration should produce actionable remediation.

For each risky path determine whether to:

```text
Remove Template
Disable Template
Remove CA Publication
Restrict Enrollment
Restrict Autoenrollment
Change Subject Configuration
Change EKUs
Require Approval
Require Signatures
Fix Template ACL
Fix CA ACL
Harden Enrollment Service
Enable EPA
Reduce NTLM
Improve Certificate Mapping
```

---

# Do Not Delete Templates Blindly

A template may support critical infrastructure such as:

```text
Wi-Fi
VPN
LDAPS
Smart Cards
Web Servers
Device Authentication
```

Before disabling or removing it:

```text
Identify Consumers
Identify Autoenrollment
Identify Existing Certificates
Plan Replacement
Test
Deploy
Then Retire
```

---

# Template Naming Can Be Misleading

Do not assume a template called:

```text
WebServer
```

only provides server authentication.

Likewise:

```text
UserCertificate
```

does not tell you whether the certificate can authenticate.

Inspect the actual:

```text
EKUs
Application Policies
Subject Configuration
Permissions
```

---

# Default Templates

Default templates are not automatically vulnerable.

Likewise:

```text
Custom Template
```

does not automatically mean insecure.

Security depends on configuration and permissions.

---

# Duplicate Templates

Many organisations duplicate a Microsoft template and modify it.

Example:

```text
User
  |
  v
Duplicate
  |
  v
CorpUserAuthentication
```

The new template can have very different:

```text
ACLs
EKUs
Subject Rules
Issuance Requirements
```

Always enumerate custom templates carefully.

---

# Stale Templates

Templates may remain in Active Directory long after they stop being used.

Distinguish:

```text
Template Exists
```

from:

```text
Template Published
```

and:

```text
Template Actively Used
```

---

# Stale Published Templates

A template may still be published even though administrators believe it has been retired.

Therefore:

```text
Documentation Says Retired
       |
       X
CA No Longer Issues It
```

Verify directly.

---

# Certificate Inventory

Where the assessment permits, compare templates against actual issued certificates.

Questions include:

```text
Which Templates Are Actively Used?
Which Accounts Receive Certificates?
Which Certificates Have Long Lifetimes?
Which Privileged Accounts Have Certificates?
```

This may require CA database access or administrative cooperation.

---

# White-Box Assessment

In a white-box AD CS review, request:

```text
PKI Architecture Diagram
CA Inventory
Template Inventory
PKI Security Groups
CA Security Configuration
Enrollment Agent Configuration
Web Enrollment Configuration
Certificate Policies
CA Backup Procedures
HSM Configuration
Revocation Procedures
```

Then compare documentation to actual configuration.

---

# Black-Box / Grey-Box Assessment

With ordinary domain credentials, focus first on:

```text
LDAP
Certipy
DNS
Web Discovery
BloodHound
ACLs
```

This often provides enough information to identify high-value candidate paths without CA administrative access.

---

# AD CS Enumeration Workflow

A practical workflow is:

```text
Domain Credentials
      |
      v
Get Configuration NC
      |
      v
Enumerate Public Key Services
      |
      v
Enumerate Enrollment Services
      |
      v
Identify CA Hosts
      |
      v
Enumerate Published Templates
      |
      v
Enumerate All Templates
      |
      v
Analyse EKUs
      |
      v
Analyse Subject Rules
      |
      v
Analyse Issuance Requirements
      |
      v
Analyse Template ACLs
      |
      v
Analyse CA Permissions
      |
      v
Discover Web Services
      |
      v
Run Certipy
      |
      v
Correlate BloodHound
      |
      v
Triage ESC Candidates
      |
      v
Validate Minimally
```

---

# AD CS Enumeration Checklist

## Discovery

- [ ] Obtain configuration naming context
- [ ] Locate Public Key Services
- [ ] Enumerate Certification Authorities
- [ ] Enumerate Enrollment Services
- [ ] Identify Enterprise CAs
- [ ] Identify CA DNS hostnames
- [ ] Identify Root CAs
- [ ] Identify subordinate CAs
- [ ] Identify issuing CAs
- [ ] Identify Online Responders
- [ ] Identify NDES
- [ ] Identify CEP
- [ ] Identify CES
- [ ] Identify CA Web Enrollment

## Certificate Authorities

- [ ] Record CA name
- [ ] Record CA host
- [ ] Record CA certificate
- [ ] Record CA validity
- [ ] Record published templates
- [ ] Review CA permissions
- [ ] Review certificate-manager permissions
- [ ] Review CA administrators
- [ ] Review request disposition
- [ ] Review enrollment-agent restrictions
- [ ] Review CA-wide security-sensitive settings

## Templates

- [ ] Enumerate all templates
- [ ] Identify enabled templates
- [ ] Identify issuing CAs
- [ ] Record template version
- [ ] Record template OID
- [ ] Review EKUs
- [ ] Review application policies
- [ ] Review subject-name flags
- [ ] Review enrollment flags
- [ ] Review private-key flags
- [ ] Review validity
- [ ] Review renewal period
- [ ] Review manager approval
- [ ] Review authorized signatures
- [ ] Review enrollment-agent capability

## Template Permissions

- [ ] Enumerate template owner
- [ ] Enumerate DACL
- [ ] Identify Enroll
- [ ] Identify Autoenroll
- [ ] Identify GenericAll
- [ ] Identify GenericWrite
- [ ] Identify WriteProperty
- [ ] Identify WriteDACL
- [ ] Identify WriteOwner
- [ ] Resolve nested groups
- [ ] Identify indirect group-control paths

## Authentication

- [ ] Identify Client Authentication EKU
- [ ] Identify Smart Card Logon
- [ ] Identify Certificate Request Agent
- [ ] Identify Any Purpose
- [ ] Identify templates without EKUs
- [ ] Review PKINIT availability
- [ ] Review Domain Controller certificates
- [ ] Review certificate mapping
- [ ] Review SID security extension behaviour
- [ ] Review current Domain Controller hardening

## Enrollment Services

- [ ] Check `/certsrv/`
- [ ] Check HTTP
- [ ] Check HTTPS
- [ ] Identify IIS authentication
- [ ] Identify NTLM
- [ ] Review EPA
- [ ] Identify CES
- [ ] Identify CEP
- [ ] Identify NDES
- [ ] Identify SCEP
- [ ] Record network exposure

## Active Directory PKI

- [ ] Enumerate AIA
- [ ] Enumerate CDP
- [ ] Enumerate OID
- [ ] Enumerate NTAuthCertificates
- [ ] Review PKI ACLs
- [ ] Review PKI object owners
- [ ] Review trust relationships

## Tooling

- [ ] Use native PowerShell
- [ ] Use certutil
- [ ] Use certtmpl.msc where available
- [ ] Use certsrv.msc where available
- [ ] Use ldapsearch
- [ ] Use Certipy
- [ ] Use BloodHound
- [ ] Correlate results
- [ ] Verify tool version
- [ ] Manually confirm important candidates

## ESC Triage

- [ ] Triage ESC1
- [ ] Triage ESC2
- [ ] Triage ESC3
- [ ] Triage ESC4
- [ ] Triage ESC5
- [ ] Triage ESC6
- [ ] Triage ESC7
- [ ] Triage ESC8
- [ ] Triage ESC9
- [ ] Triage ESC10
- [ ] Triage ESC11
- [ ] Triage ESC12
- [ ] Triage ESC13
- [ ] Triage ESC14
- [ ] Triage ESC15
- [ ] Verify taxonomy against current research

## Validation

- [ ] Prefer read-only evidence
- [ ] Use dedicated test identity
- [ ] Verify CA publication
- [ ] Verify effective enrollment rights
- [ ] Verify issuance requirements
- [ ] Verify certificate mapping
- [ ] Request minimum certificates necessary
- [ ] Avoid privileged identity impersonation unless required
- [ ] Protect private keys
- [ ] Stop after sufficient evidence
- [ ] Revoke test certificates where appropriate

## Detection

- [ ] Monitor certificate requests
- [ ] Monitor certificate issuance
- [ ] Monitor template changes
- [ ] Monitor PKI ACL changes
- [ ] Monitor CA changes
- [ ] Monitor web enrollment
- [ ] Monitor privileged certificate issuance
- [ ] Monitor certificate authentication
- [ ] Monitor event 5136 for relevant directory changes
- [ ] Baseline PKI configuration

## Hardening

- [ ] Remove unused templates
- [ ] Unpublish unnecessary templates
- [ ] Restrict enrollment
- [ ] Restrict autoenrollment
- [ ] Restrict template modification
- [ ] Restrict CA administration
- [ ] Restrict certificate-manager rights
- [ ] Configure enrollment-agent restrictions
- [ ] Review authentication EKUs
- [ ] Review subject-name configuration
- [ ] Require approval where appropriate
- [ ] Require signatures where appropriate
- [ ] Harden certificate mapping
- [ ] Secure enrollment web services
- [ ] Enable EPA where applicable
- [ ] Reduce NTLM
- [ ] Protect CA private keys
- [ ] Protect CA backups

## Reporting

- [ ] Report actual configuration weakness
- [ ] Include CA
- [ ] Include template
- [ ] Include affected principal
- [ ] Include effective permission
- [ ] Include relevant template settings
- [ ] Include authentication capability
- [ ] Include resulting identity
- [ ] Include validated impact
- [ ] Include remediation
- [ ] Avoid reporting only an ESC number

---

# Reporting Example

```text
Finding:
Broad Enrollment Rights on Authentication Certificate Template

Affected CA:
CORP-CA01

Affected Template:
CorpUserAuthentication

Observation:
The CorpUserAuthentication certificate template is published by the
CORP-CA01 Enterprise Certification Authority.

The template grants enrollment rights to a broad domain group and
issues certificates capable of client authentication.

The template's identity, issuance, and mapping configuration should
therefore be reviewed to determine whether certificate requests can
represent identities outside the intended enrollment population.

Impact:
If certificate identity controls are insufficient, a compromised
low-privileged account may potentially obtain authentication material
with privileges beyond those of the original account.

Recommendation:
Restrict enrollment to principals with a documented business
requirement.

Review the template's subject-name configuration, EKUs, application
policies, issuance requirements, certificate mapping behaviour, and
security descriptor.

Remove the template from issuing CAs if it is no longer required.
```

---

# Enumeration Model

The discovery model is:

```text
Active Directory
      |
      v
Configuration Partition
      |
      v
Public Key Services
      |
      v
Enterprise PKI
```

The CA model is:

```text
Enrollment Services
      |
      v
Enterprise CA
      |
      v
Published Templates
```

The template model is:

```text
Certificate Template
       |
       +--> Enrollment Rights
       +--> Subject Rules
       +--> EKUs
       +--> Issuance Requirements
       +--> Private-Key Rules
       +--> ACL
```

The permission model is:

```text
Principal
   |
   v
Direct / Nested Group
   |
   v
Enroll
   |
   v
Template
```

The template-control model is:

```text
Principal
   |
   v
GenericWrite / GenericAll
   |
   v
Template
   |
   v
Security-Sensitive Modification
```

The publication model is:

```text
Template Exists
      |
      v
CA Publishes Template
      |
      v
Certificate Can Be Requested
```

The authentication model is:

```text
Template
   |
   v
Authentication-Capable Certificate
   |
   v
Certificate Mapping
   |
   v
Identity
```

The web enrollment model is:

```text
CA
 |
 v
IIS
 |
 v
Enrollment Endpoint
 |
 v
Authentication
 |
 v
Certificate Request
```

The relay-analysis model is:

```text
Enrollment Endpoint
       |
       v
NTLM Available?
       |
       v
EPA?
       |
       v
Relay Feasible?
       |
       v
Useful Template?
```

The Certipy model is:

```text
Certipy
   |
   v
Candidate ESC
   |
   v
Manual Validation
   |
   v
Confirmed Condition
```

The BloodHound model is:

```text
Principal
   |
   v
AD Relationship
   |
   v
PKI Permission
   |
   v
Certificate Path
   |
   v
Privilege
```

The safe testing model is:

```text
Enumerate
   |
   v
Analyse
   |
   v
Correlate
   |
   v
Validate Minimally
   |
   v
Stop
```

The central question is not:

```text
Does the organisation use AD CS?
```

The useful question is:

```text
Who controls certificate issuance,
what identities can certificates represent,
and what authentication privileges result?
```

For penetration testers:

```text
Do Not Ask:
"Which ESC numbers does Certipy print?"

Ask:
"Which certificate trust relationships can
my current identity influence, and what
additional identity or privilege could that
influence provide?"
```

For defenders:

```text
Do Not Ask:
"Which templates exist?"

Ask:
"Which templates are issued, who can enroll,
who can modify them, which certificates can
authenticate, and can we detect changes?"
```

The complete enumeration relationship is:

```text
Forest
  |
  v
PKI Infrastructure
  |
  v
Certificate Authority
  |
  v
Certificate Template
  |
  v
Permissions
  |
  v
Certificate Capability
  |
  v
Identity Mapping
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

[Active Directory Certificate Services](index.md)

Active Directory methodology:

[Active Directory Penetration Testing Methodology](../methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](../enumeration.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

Groups:

[Active Directory Groups](../groups.md)

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

The next AD CS page is:

```text
active-directory/ad-cs/esc1.md
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

## Microsoft - AD CS Protocol Documentation

[Microsoft - Certificate Services Remote Administration Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-csra/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Enrollment Policy

[Microsoft - Certificate Enrollment Policy Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-xcep/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Enrollment

[Microsoft - Windows Client Certificate Enrollment Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/){ target="_blank" rel="noopener noreferrer" }

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

AD CS enumeration should not be reduced to:

```text
certipy find
```

A proper assessment combines:

```text
Active Directory
+
PKI
+
Permissions
+
Certificate Semantics
+
Authentication
```

The most important workflow is:

```text
Discover CA
   |
   v
Discover Templates
   |
   v
Determine Who Can Enroll
   |
   v
Determine Who Can Modify
   |
   v
Determine Certificate Capability
   |
   v
Determine Identity Mapping
   |
   v
Determine Resulting Privilege
```

The important distinction is:

```text
Template Exists
      |
      X
Template Is Exploitable
```

and:

```text
Template Published
      |
      X
Template Is Vulnerable
```

and:

```text
Certipy Candidate
      |
      X
Confirmed Finding
```

The final determination requires:

```text
Template Configuration
        +
Effective Permissions
        +
CA Publication
        +
CA Configuration
        +
Certificate Mapping
        +
Resulting Identity
```

For offensive security assessments, enumeration should therefore produce an:

```text
Attack Path Map
```

rather than merely an:

```text
ESC List
```

For defensive assessments, it should produce a:

```text
PKI Trust Map
```

showing:

```text
Who Can Request
Who Can Modify
Who Can Approve
Who Can Administer
Which Certificates Authenticate
Which CAs Establish Trust
```

That map becomes the foundation for assessing ESC1 through ESC15 and any certificate-related attack paths that do not fit neatly into the ESC taxonomy.
