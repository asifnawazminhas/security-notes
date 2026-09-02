# AD CS ESC1 - Enrollee-Supplied Subject for Authentication Certificates

ESC1 is an Active Directory Certificate Services (AD CS) privilege escalation condition where a certificate template allows an authorised enrollee to supply identity information in the certificate request and the resulting certificate can be used for authentication.

The classic attack path is:

```text
Low-Privileged Principal
        |
        v
Can Enroll
        |
        v
Certificate Template
        |
        +--> Enrollee Supplies Subject
        |
        +--> Authentication Capability
        |
        +--> No Effective Approval Barrier
        |
        v
Certificate Request
        |
        v
Certificate Representing Another Identity
        |
        v
Certificate-Based Authentication
        |
        v
Privilege Escalation
```

ESC1 is dangerous because the attacker does not necessarily need to:

```text
Know Victim Password
Steal Victim NT Hash
Steal Victim Kerberos Ticket
Reset Victim Password
```

Instead, the certificate infrastructure may issue new authentication material that represents another Active Directory identity.

!!! warning "Authorised testing only"
    Requesting a certificate representing another account is an active identity-impersonation action. Begin with template, ACL, CA publication, issuance, and certificate-mapping analysis. Where proof is required, use an approved test identity wherever possible and request only the minimum certificate necessary to demonstrate the issue. Treat generated PFX files and private keys as credentials.

---

# ESC1 Concept

The fundamental problem is a dangerous combination of certificate-template properties.

Conceptually:

```text
Template
   |
   +--> Attacker Can Enroll
   |
   +--> Attacker Controls Subject Information
   |
   +--> Certificate Supports Authentication
   |
   +--> Request Can Be Issued
   |
   v
Potential Identity Impersonation
```

No single setting should normally be analysed in isolation.

---

# The Normal Certificate Enrollment Model

A securely designed authentication template commonly derives identity information from Active Directory.

Conceptually:

```text
CORP\alice
    |
    v
Certificate Request
    |
    v
CA Reads Alice's AD Identity
    |
    v
Certificate for Alice
```

The requester cannot simply decide:

```text
I want to be Administrator
```

because the identity is derived from the requester's directory object.

---

# The ESC1 Model

With an unsafe enrollee-supplied subject configuration:

```text
CORP\alice
    |
    v
Certificate Request
    |
    +--> Requester Supplies Identity Information
    |
    v
Certificate Authority
    |
    v
Certificate
```

If other conditions permit, the supplied identity may represent a different account.

Conceptually:

```text
alice
  |
  v
Certificate Request
  |
  +--> Identity = privileged-user@corp.example
  |
  v
Authentication Certificate
```

This creates an identity issuance problem.

---

# Why ESC1 Matters

ESC1 can turn:

```text
Certificate Enrollment Permission
```

into:

```text
Account Impersonation
```

and potentially:

```text
Privilege Escalation
```

The resulting severity depends heavily on which identity can be represented.

For example:

```text
Domain User
   |
   v
ESC1 Template
   |
   v
Privileged User Certificate
   |
   v
Privileged Authentication
```

can represent a severe trust-boundary failure.

---

# ESC1 Preconditions

A classic ESC1 candidate generally involves several conditions.

A useful assessment model is:

```text
1. Enterprise CA Exists
2. CA Publishes Template
3. Attacker Has Enrollment Rights
4. Enrollee Can Supply Subject Information
5. Certificate Can Be Used for Authentication
6. Issuance Requirements Do Not Block Request
7. Certificate Mapping Permits the Intended Identity
```

Every relevant condition should be validated.

---

# Condition 1 - Enterprise CA

The template must be usable through an issuing Enterprise CA.

Conceptually:

```text
Template Exists
      |
      X
Automatically Exploitable
```

Instead:

```text
Template Exists
      |
      v
CA Publishes Template
      |
      v
Certificate Can Be Requested
```

---

# Condition 2 - Enrollment Permission

The attacker's effective security context must be able to request the certificate.

Enrollment might be granted directly to:

```text
User
Group
Computer
Service Account
```

or indirectly through nested groups.

Example:

```text
alice
  |
  v
Domain Users
  |
  v
Enroll
  |
  v
ESC1 Template
```

---

# Broad Enrollment Groups

Common groups requiring attention include:

```text
Domain Users
Authenticated Users
Domain Computers
Everyone
Large Department Groups
Large VPN Groups
Large Application Groups
```

Broad enrollment is not automatically a vulnerability.

The risk comes from its combination with security-sensitive template settings.

---

# Condition 3 - Enrollee Supplies Subject

The central ESC1 template setting is commonly represented by:

```text
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT
```

with value:

```text
0x00000001
```

in:

```text
msPKI-Certificate-Name-Flag
```

In the Certificate Templates console this is associated with:

```text
Subject Name
    |
    v
Supply in the request
```

This means identity information can originate from the certificate request rather than being entirely constructed from the requester's Active Directory object.

---

# Microsoft Processing Model

At a high level:

```text
Enrollee Supplies Subject Disabled
        |
        v
CA Uses Directory-Derived Identity Rules
```

versus:

```text
Enrollee Supplies Subject Enabled
        |
        v
Request Contains Subject Information
        |
        v
CA Processes Request-Supplied Identity
```

This distinction is central to ESC1.

---

# Subject Alternative Name

The:

```text
Subject Alternative Name
```

or:

```text
SAN
```

can contain identity information.

Examples include:

```text
UPN
DNS Name
Email Address
```

depending on certificate type and request.

For Active Directory authentication, UPN and other mapping information can become security-sensitive.

---

# UPN SAN

A User Principal Name might look like:

```text
alice@corp.example
```

A dangerous identity substitution could conceptually be:

```text
Requesting User:
alice@corp.example

Requested Identity:
privileged-user@corp.example
```

Whether the resulting certificate authenticates as that account depends on the complete certificate mapping and security configuration.

---

# DNS SAN

Computer-oriented certificate paths may involve DNS identities.

Example:

```text
dc01.corp.example
```

The exact authentication implications differ from user UPN mappings and must be analysed separately.

---

# Condition 4 - Authentication Capability

Supplying another identity is not enough.

The certificate must also be useful for authentication.

Important EKUs and application policies can include:

```text
Client Authentication
Smart Card Logon
PKINIT Client Authentication
Any Purpose
```

Certificates with no restrictive EKU may also require careful analysis depending on the Windows PKI context.

---

# Client Authentication

The Client Authentication EKU is:

```text
1.3.6.1.5.5.7.3.2
```

A template containing this EKU may issue certificates suitable for client authentication.

---

# Smart Card Logon

The Smart Card Logon EKU is:

```text
1.3.6.1.4.1.311.20.2.2
```

This is directly relevant to Windows certificate-based logon scenarios.

---

# PKINIT Client Authentication

The PKINIT Client Authentication EKU is:

```text
1.3.6.1.5.2.3.4
```

PKINIT allows public-key credentials to participate in Kerberos authentication.

---

# Any Purpose

The Any Purpose EKU is:

```text
2.5.29.37.0
```

A broadly usable certificate deserves careful review because its purposes are not narrowly constrained.

---

# No EKU

Do not assume:

```text
No EKU
   =
Cannot Authenticate
```

Certificates without restrictive EKUs can have broad usage semantics in some Windows PKI contexts.

Always evaluate the complete certificate and authentication path.

---

# Condition 5 - Issuance Requirements

A dangerous subject configuration may still be protected by issuance controls.

Review:

```text
CA Certificate Manager Approval
Authorized Signatures
Enrollment Agent Requirements
Other Issuance Policies
```

---

# Manager Approval

If the template requires:

```text
CA Certificate Manager Approval
```

the workflow becomes:

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

This can prevent immediate certificate issuance.

---

# Authorized Signatures

A template can require one or more authorised signatures before issuance.

Conceptually:

```text
Attacker Request
      |
      v
Required Signature
      |
      X
No Appropriate Signer
```

This may prevent the straightforward ESC1 path.

---

# Condition 6 - Certificate Mapping

Modern ESC1 assessment must account for certificate mapping.

The old simplified assumption was:

```text
Certificate Contains Victim UPN
        |
        v
Authenticate as Victim
```

Modern Windows environments can enforce stronger certificate-to-account mapping.

Therefore the actual model is:

```text
Certificate
    |
    v
Identity Information
    |
    v
Certificate Mapping Rules
    |
    v
Mapped AD Account
    |
    v
Authentication
```

---

# Strong Certificate Mapping

Microsoft introduced stronger certificate-based authentication mapping requirements following security hardening associated with KB5014754.

Current assessments should consider:

```text
Domain Controller Patch Level
Strong Certificate Mapping
SID Security Extension
Certificate Mapping Method
Certificate Issuance Date
Certificate Properties
```

Do not assume an old ESC1 proof of concept behaves identically on a current environment.

---

# Full Enforcement

Current Windows certificate-based authentication hardening means weak certificate mapping assumptions from older AD CS research may no longer apply unchanged.

The assessment should therefore distinguish:

```text
Template Misconfiguration
```

from:

```text
Successfully Mapped Authentication Certificate
```

A template may still represent a serious configuration weakness even where a particular historical authentication path has been mitigated by current mapping enforcement.

---

# SID Security Extension

Modern Enterprise CA-issued certificates may contain a security extension linking the certificate to the requester's Active Directory SID.

Conceptually:

```text
Certificate
   |
   +--> Requested Identity Information
   |
   +--> SID Security Information
```

This additional identity binding affects modern certificate mapping behaviour.

---

# Do Not Ignore the SID Extension

A legacy assessment model might only inspect:

```text
UPN SAN
```

A modern assessment should inspect:

```text
UPN / SAN
SID Security Extension
Issuer
Template
Mapping Behaviour
KDC Behaviour
```

---

# ESC1 vs Certificate Mapping Hardening

Think of these as different layers:

```text
Layer 1
Template permits dangerous identity input

Layer 2
CA issues certificate

Layer 3
Authentication service maps certificate

Layer 4
Identity receives access
```

A weakness at Layer 1 does not automatically prove successful Layer 4 compromise.

---

# Enumerating ESC1 with Certipy

Certipy can identify certificate templates that appear to satisfy ESC1-related conditions.

Start by checking the installed version:

```bash
certipy --help
```

Then:

```bash
certipy find -h
```

A typical authenticated enumeration pattern is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Use an approved assessment identity.

---

# Review Certipy Output

Look for fields relating to:

```text
Certificate Authorities
Template Name
Enabled
Enrollment Rights
Enrollee Supplies Subject
Client Authentication
Extended Key Usage
Manager Approval
Authorized Signatures
Potential ESC1
```

Exact labels vary between Certipy versions.

---

# Certipy Candidate

A Certipy result should be treated as:

```text
Potential ESC1
```

until manually confirmed.

The workflow is:

```text
Certipy
   |
   v
ESC1 Candidate
   |
   v
Verify Template
   |
   v
Verify Enrollment
   |
   v
Verify CA Publication
   |
   v
Verify Issuance Requirements
   |
   v
Verify Mapping
   |
   v
Determine Impact
```

---

# Native PowerShell Enumeration

Start with the template container:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties * |
    Select-Object Name,DisplayName
```

---

# Enumerate Subject Name Flags

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Certificate-Name-Flag' |
    Select-Object Name,'msPKI-Certificate-Name-Flag'
```

---

# Identify Enrollee-Supplied Subject Flag

The relevant bit is:

```text
0x00000001
```

PowerShell can test it:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Certificate-Name-Flag' |
    Where-Object {
        ([int]$_.'msPKI-Certificate-Name-Flag' -band 0x00000001) -ne 0
    } |
    Select-Object Name,DisplayName,'msPKI-Certificate-Name-Flag'
```

This identifies templates where the relevant subject-supply bit is present.

It does not by itself prove ESC1.

---

# Enumerate EKUs

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage |
    Select-Object Name,pKIExtendedKeyUsage
```

---

# Find Client Authentication Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(pKIExtendedKeyUsage=1.3.6.1.5.5.7.3.2)' -Properties pKIExtendedKeyUsage |
    Select-Object Name,pKIExtendedKeyUsage
```

Remember that this is not the only potentially relevant authentication capability.

---

# Correlate Subject Flag and Client Authentication

A basic read-only triage query can combine both conditions:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Certificate-Name-Flag',pKIExtendedKeyUsage |
    Where-Object {
        (([int]$_.'msPKI-Certificate-Name-Flag' -band 0x00000001) -ne 0) -and
        ($_.pKIExtendedKeyUsage -contains '1.3.6.1.5.5.7.3.2')
    } |
    Select-Object Name,DisplayName,'msPKI-Certificate-Name-Flag',pKIExtendedKeyUsage
```

This is useful for candidate discovery.

It still does not evaluate:

```text
Enrollment Rights
CA Publication
Approval
Signatures
Certificate Mapping
```

---

# Enumerate Issuance Requirements

Retrieve:

```text
msPKI-Enrollment-Flag
msPKI-RA-Signature
```

with:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Enrollment-Flag','msPKI-RA-Signature' |
    Select-Object Name,'msPKI-Enrollment-Flag','msPKI-RA-Signature'
```

Interpret the flags against Microsoft protocol documentation or trusted tooling.

---

# Verify CA Publication

Find Enterprise CAs:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Select-Object Name,dNSHostName,certificateTemplates
```

Confirm the candidate template appears in:

```text
certificateTemplates
```

for an issuing CA.

---

# Find Which CA Publishes a Template

Example:

```powershell
$templateName = 'CorpUserAuth'

$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Where-Object {
        $_.certificateTemplates -contains $templateName
    } |
    Select-Object Name,dNSHostName
```

---

# Enumerate Template ACL

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpUserAuth,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,IsInherited
```

This provides raw ACL information.

---

# Effective Enrollment Rights

Do not stop at direct ACEs.

Consider:

```text
Direct Group Membership
Nested Group Membership
Inherited Permissions
Extended Rights
Ownership
```

The actual question is:

```text
Can the assessment identity effectively enroll?
```

---

# PowerView

PowerView can help inspect template ACLs.

Example:

```powershell
Get-DomainObjectAcl -Identity 'CN=CorpUserAuth,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' -ResolveGUIDs
```

Look for relevant enrollment and object-control rights.

Exact output depends on PowerView version.

---

# LDAP Enumeration from Linux

Templates can be inspected directly over LDAP.

Example:

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
    msPKI-RA-Signature
```

This is a low-impact way to collect the core configuration.

---

# Search for Enrollee-Supplied Subject

Raw LDAP values can be difficult to interpret because:

```text
msPKI-Certificate-Name-Flag
```

is a bit field.

Use tooling or locally decode the values rather than matching one decimal value exactly, because multiple flags can be combined.

---

# BloodHound

BloodHound can help connect:

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
```

and broader AD privilege relationships.

The useful question is:

```text
Who can reach the template?
```

not simply:

```text
Is the template unsafe?
```

---

# Indirect ESC1 Path

Consider:

```text
alice
  |
  v
AddMember
  |
  v
PKI-Enrollment
  |
  v
Enroll
  |
  v
ESC1 Template
```

The attacker may not have direct enrollment permission but still have an effective path to it.

---

# Another Indirect Path

```text
alice
  |
  v
GenericWrite
  |
  v
bob
  |
  v
PKI-Enrollment
  |
  v
ESC1 Template
```

This demonstrates why AD CS findings should be integrated with general Active Directory attack-path analysis.

---

# Template Control vs ESC1

Do not confuse:

```text
ESC1
```

with:

```text
ESC4
```

A simplified distinction is:

```text
ESC1
Existing template configuration is dangerous
```

versus:

```text
ESC4
Attacker can modify a template
```

ESC4 may potentially be used to create an ESC1-like configuration, but the initial weakness is different.

---

# ESC1 vs ESC2

ESC1 focuses on:

```text
Enrollee-Supplied Identity
+
Authentication Capability
```

ESC2 focuses on overly broad certificate purposes such as:

```text
Any Purpose
```

or similarly unconstrained usage.

The conditions and exploitation paths differ.

---

# ESC1 vs ESC3

ESC3 concerns:

```text
Enrollment Agent
```

functionality.

The conceptual model is:

```text
ESC1
Requester controls identity information
```

versus:

```text
ESC3
Enrollment Agent requests on behalf of another identity
```

---

# ESC1 vs ESC6

ESC1 is primarily a:

```text
Certificate Template
```

condition.

ESC6 historically concerns:

```text
CA-Wide Configuration
```

affecting SAN processing.

Do not treat the two as interchangeable.

---

# ESC1 vs Shadow Credentials

ESC1:

```text
Certificate Template
      |
      v
CA Issues Certificate
```

Shadow Credentials:

```text
Write msDS-KeyCredentialLink
      |
      v
Add Key Credential
```

Both can involve certificate-based authentication, but the trust path is different.

See:

[Active Directory Shadow Credentials](../shadow-credentials.md)

---

# ESC1 vs Password Reset

Password reset:

```text
Attacker
   |
   v
Changes Victim Password
   |
   v
Victim Secret Replaced
```

ESC1:

```text
Attacker
   |
   v
Obtains Alternate Authentication Credential
   |
   v
Victim Password Unchanged
```

This difference matters for both detection and incident response.

---

# Certificate Request Validation

When explicit validation is authorised, Certipy can request certificates.

Before doing so:

```bash
certipy req -h
```

Confirm syntax against the installed version.

A request requires information such as:

```text
CA
Template
Authentication Identity
CA Target
Requested Certificate Identity
```

---

# Avoid Copying Old Certipy Syntax Blindly

Certipy has changed significantly across releases.

Always begin with:

```bash
certipy --help
certipy req -h
certipy auth -h
```

before following an older blog post.

---

# Controlled ESC1 Validation

The preferred validation hierarchy is:

```text
Template Configuration
        |
        v
Enrollment Permission
        |
        v
CA Publication
        |
        v
Issuance Requirements
        |
        v
Mapping Analysis
        |
        v
Test Certificate
        |
        v
Authentication Proof
```

Stop as soon as sufficient evidence exists.

---

# Test Account Strategy

Where possible create or use:

```text
adcs-test-user
```

and another approved:

```text
adcs-test-target
```

Then demonstrate the identity boundary using test accounts rather than production privileged identities.

For example:

```text
adcs-test-user
      |
      v
Requests Certificate
      |
      v
adcs-test-target
```

This proves cross-account certificate issuance without affecting a real administrator.

---

# Privileged Identity Validation

If the engagement specifically requires proving impact against a privileged identity:

```text
Obtain Written Approval
Use One Certificate
Authenticate Once
Do Not Perform Additional Privileged Actions
Record Evidence
Revoke Certificate
Delete Private Key
```

Avoid unnecessary actions after authentication succeeds.

---

# Certificate Authentication

If an authorised test certificate has been issued, authentication can be validated using tooling that supports certificate-based Kerberos or Schannel authentication.

Certipy provides:

```text
auth
```

functionality.

Check:

```bash
certipy auth -h
```

before use.

The conceptual path is:

```text
PFX
 |
 v
Certificate + Private Key
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

---

# Authentication Is the Strongest Proof

The strongest technical validation is:

```text
Certificate Issued
      |
      v
Certificate Maps to Target
      |
      v
Authentication Succeeds
```

However, it is not always necessary.

If the risk is already demonstrated by configuration and approved architectural evidence, avoid creating additional reusable credentials.

---

# Do Not Retrieve More Credentials Than Necessary

Some certificate authentication tooling can also derive or expose additional credential material under suitable conditions.

For a normal ESC1 validation, the assessment may only need to prove:

```text
Certificate-Based Authentication
```

Do not retrieve:

```text
NT Hashes
Additional Tickets
Service Credentials
```

unless required by the engagement objective.

---

# Protect PFX Files

A PFX generated during testing may contain:

```text
Certificate
Private Key
Certificate Chain
```

Treat it as a credential.

Never:

```text
Commit It to Git
Upload It to a Public Scanner
Attach It to the Report
Paste Its Private Key into Notes
Leave It in /tmp
```

---

# Certificate Evidence

Record non-secret evidence such as:

```text
Certificate Subject
SAN
Issuer
Serial Number
Thumbprint
Template
Validity
Authentication Result
```

Avoid recording the private key.

---

# Certificate Lifetime

Record:

```text
Not Before
Not After
```

because the lifetime affects persistence risk.

A certificate valid for:

```text
2 Years
```

has a different exposure window than one valid for:

```text
8 Hours
```

---

# Password Reset and ESC1 Certificates

An important consequence of certificate-based authentication is that changing the account password does not inherently remove an already issued certificate.

Conceptually:

```text
Certificate
    |
    v
Issued Credential
    |
    +---------------------+
    |                     |
Password Changed      Certificate Exists
                          |
                          v
                    May Remain Usable
```

Incident response must address the certificate itself.

---

# Persistence Risk

If an attacker obtains a long-lived authentication certificate:

```text
Authentication Certificate
          |
          v
Password Rotation
          |
          X
Certificate Automatically Removed
```

The certificate may remain usable until:

```text
Expiration
Revocation
Trust Change
Other Authentication Control
```

depending on the environment.

---

# Detection

ESC1 detection should consider several stages:

```text
Template Configuration
Certificate Request
Certificate Issuance
Certificate Authentication
Subsequent Privileged Activity
```

---

# Detect Dangerous Templates

Defenders should continuously inventory templates with combinations involving:

```text
Enrollee Supplies Subject
+
Authentication EKU
+
Broad Enrollment
```

Then evaluate:

```text
Approval
Signatures
Mapping
CA Publication
```

---

# Monitor Template Changes

Certificate templates are Active Directory objects.

Changes can be detected using Directory Service Changes auditing where configured.

Relevant events can include:

```text
5136
```

for directory object modifications.

---

# Event 5136

Monitor changes to:

```text
msPKI-Certificate-Name-Flag
pKIExtendedKeyUsage
msPKI-Certificate-Application-Policy
msPKI-Enrollment-Flag
msPKI-RA-Signature
nTSecurityDescriptor
```

on certificate-template objects.

A change such as:

```text
Build from Active Directory
        |
        v
Supply in the request
```

should receive particular attention.

---

# Monitor Template ACL Changes

A secure template may be converted into an unsafe one if an attacker obtains control over it.

Monitor changes involving:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
Enroll
Autoenroll
```

---

# Certificate Issuance Monitoring

Monitor certificates where:

```text
Requester
```

does not logically correspond to:

```text
Certificate Identity
```

especially for privileged identities.

For example:

```text
Requester:
CORP\alice

Certificate Identity:
privileged-user@corp.example
```

should warrant investigation unless explicitly expected.

---

# Monitor Privileged Certificates

Pay particular attention to certificates representing:

```text
Domain Admins
Enterprise Admins
Administrators
Domain Controllers
PKI Administrators
Tier 0 Service Accounts
```

Unexpected issuance should be investigated.

---

# Certificate Authentication Monitoring

Certificate-based Kerberos authentication can generate Kerberos authentication telemetry.

Correlate:

```text
Account
Source
Certificate Information
Certificate Issuer
Serial Number
Thumbprint
Authentication Time
```

where available.

---

# Event 4768

Kerberos TGT requests can generate:

```text
4768
```

on Domain Controllers.

Certificate-based pre-authentication may provide certificate-related information depending on Windows version and event configuration.

Use current Microsoft event documentation when building production detections.

---

# Correlate Issuance and Authentication

A powerful detection model is:

```text
Certificate Issued
       |
       v
Privileged Identity
       |
       v
Short Time Window
       |
       v
Certificate Authentication
       |
       v
Unexpected Source
```

This provides stronger context than either event alone.

---

# Baseline Legitimate Enrollment

Some organisations legitimately issue authentication certificates to many users.

Therefore:

```text
Authentication Certificate Issued
```

is not automatically malicious.

Baseline:

```text
Normal Templates
Normal Requesters
Normal Subjects
Normal CAs
Normal Enrollment Hosts
Normal Authentication Sources
```

---

# Hardening ESC1

The best remediation is to remove the unsafe trust relationship.

Possible controls include:

```text
Disable Enrollee-Supplied Subject
Restrict Enrollment
Remove Authentication EKUs
Require Manager Approval
Require Authorized Signatures
Fix Template ACLs
Unpublish Unnecessary Template
Use Strong Certificate Mapping
Monitor Certificate Issuance
```

The correct combination depends on the template's business purpose.

---

# Disable Supply in the Request

Where not required, configure the template to derive identity from Active Directory.

Conceptually:

```text
Supply in the Request
        |
        v
Disable
        |
        v
Build from Active Directory
```

This removes the classic attacker-controlled identity input.

---

# Restrict Enrollment

Replace broad groups such as:

```text
Domain Users
Authenticated Users
```

with narrowly scoped groups where possible.

Example:

```text
Corp-VPN-Certificate-Users
```

The group should contain only identities that genuinely require the certificate.

---

# Remove Unnecessary Authentication EKUs

If a certificate exists only for:

```text
Server TLS
Document Signing
Code Signing
Encryption
```

it should not also provide unnecessary:

```text
Client Authentication
```

capability.

Apply least privilege to certificate purposes.

---

# Require Approval

For highly sensitive certificate workflows:

```text
Manager Approval
```

may provide an additional control.

However, approval processes must themselves be secured.

---

# Require Authorized Signatures

Sensitive enrollment workflows may require:

```text
Authorized Signatures
```

where appropriate.

This adds another trust requirement before certificate issuance.

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

A secure template is only secure while its configuration cannot be altered by inappropriate principals.

---

# Remove Unused Templates from CAs

If a template is no longer required:

```text
Unpublish
```

it from issuing CAs.

After appropriate dependency analysis, retire the template if it is obsolete.

---

# Do Not Break Production PKI

Before modifying a template, determine whether it supports:

```text
VPN
Wi-Fi
Smart Cards
LDAPS
Machine Authentication
Applications
Service Authentication
```

Changes to certificate templates can cause significant outages.

---

# Certificate Mapping Hardening

Maintain current Microsoft certificate-mapping protections.

Do not weaken strong certificate mapping simply to preserve compatibility with poorly configured legacy certificate workflows.

Instead:

```text
Identify Legacy Dependency
Update Certificate Issuance
Fix Mapping
Test
Deploy
```

---

# Incident Response

If ESC1 abuse is suspected:

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
Identify Issued Certificates
      |
      v
Identify Represented Accounts
      |
      v
Identify Authentication Activity
      |
      v
Revoke Malicious Certificates
      |
      v
Fix Template
```

---

# Identify the Certificate

Collect:

```text
Serial Number
Thumbprint
Subject
SAN
Issuer
Template
Requester
Issue Time
Expiration
```

---

# Identify All Certificates Issued During Exposure

If the template was unsafe for a long period:

```text
Misconfiguration Start
       |
       v
Current Time
```

review certificates issued during that window.

Do not assume the certificate discovered during the incident is the only malicious one.

---

# Revoke Malicious Certificates

Where appropriate:

```text
Revoke Certificate
      |
      v
Publish Updated Revocation Information
```

Ensure relying systems can obtain current revocation information.

---

# Fix the Template

Possible actions include:

```text
Disable Enrollee-Supplied Subject
Restrict Enrollment
Change EKUs
Require Approval
Require Signatures
Fix ACL
Unpublish Template
```

---

# Password Reset Alone Is Insufficient

If an attacker possesses an issued certificate:

```text
Reset Victim Password
      |
      X
Issued Certificate Automatically Removed
```

The malicious certificate must also be addressed.

---

# Investigate the Requesting Principal

Determine how the attacker obtained:

```text
Enrollment Rights
```

The root cause might be:

```text
Compromised User
Nested Group
Excessive Group Membership
Compromised Service Account
Template ACL Abuse
```

---

# Investigate Related AD CS Paths

An ESC1 incident should trigger review of:

```text
Other Templates
Other CAs
Template ACLs
CA Permissions
Enrollment Services
Certificate Mapping
Other Issued Certificates
```

The discovered certificate may be only one part of a larger PKI compromise.

---

# Reporting ESC1

Avoid reporting only:

```text
ESC1
```

A better title describes the actual trust failure.

Examples:

```text
Low-Privileged Users Can Request Authentication Certificates for Arbitrary Domain Identities
```

```text
Certificate Template Allows Requester-Controlled Identity in Authentication Certificates
```

```text
Broad Enrollment Rights and Enrollee-Supplied Subject Enable Account Impersonation
```

---

# Example Finding

```text
Finding:
Certificate Template Allows Requester-Controlled Identity in
Authentication Certificates

Affected CA:
CORP-CA01

Affected Template:
CorpUserAuthentication

Affected Principal:
CORP\Domain Users

Description:
The CorpUserAuthentication certificate template is published by the
CORP-CA01 Enterprise Certification Authority.

Members of CORP\Domain Users have enrollment rights on the template.

The template permits the enrollee to supply certificate subject
information and is configured to issue certificates suitable for
authentication.

The template does not provide sufficient issuance restrictions to
prevent low-privileged users from requesting certificates containing
security-sensitive identity information.

The certificate mapping configuration and current Domain Controller
hardening were also reviewed when determining exploitability.

Impact:
A compromised low-privileged domain account may be able to obtain
certificate-based authentication material representing another
Active Directory identity.

If a privileged identity can be represented and successfully mapped,
this may result in privilege escalation and potentially compromise of
high-value Active Directory resources.

Certificate-based access may also survive a password change until the
certificate is revoked, expires, or is otherwise made unusable.

Recommendation:
Configure the template to derive identity information from Active
Directory unless requester-supplied subject information is explicitly
required.

Restrict enrollment rights to a dedicated group containing only
authorised principals.

Remove unnecessary authentication EKUs.

Where appropriate, require certificate manager approval or authorised
signatures.

Review the template ACL and remove unnecessary modification rights.

Review previously issued certificates from the affected template and
revoke any certificates issued inappropriately.
```

---

# Severity Assessment

Severity depends on:

```text
Who Can Enroll?
      +
Which Identity Can Be Represented?
      +
Can the Certificate Authenticate?
      +
Does Mapping Succeed?
      +
What Privilege Does the Target Have?
      =
Severity
```

---

# Example High-Severity Path

```text
Domain User
   |
   v
ESC1 Template
   |
   v
Privileged Identity Certificate
   |
   v
Successful Authentication
   |
   v
Tier 0 Access
```

This may warrant a critical severity depending on the environment and demonstrated impact.

---

# Example Reduced-Impact Path

```text
Restricted Enrollment Group
      |
      v
Requester-Supplied Subject
      |
      v
Non-Authentication Certificate
```

This may represent a configuration concern but not the classic ESC1 privilege escalation path.

---

# Evidence Checklist

For an ESC1 finding record:

```text
CA Name
CA Host
Template Name
Template DN
Template Enabled
CA Publishes Template
Enrollment Principal
Effective Enrollment Path
Subject Name Flags
EKUs
Application Policies
Manager Approval
Authorized Signatures
Template ACL
Template Owner
Certificate Mapping Behaviour
Test Identity
Requested Identity
Certificate Serial Number
Certificate Thumbprint
Authentication Result
Cleanup Result
```

Never include the private key in the report.

---

# ESC1 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify issuing CAs
- [ ] Enumerate certificate templates
- [ ] Identify published templates
- [ ] Identify authentication-capable templates
- [ ] Identify enrollee-supplied subject templates

## Template Configuration

- [ ] Review `msPKI-Certificate-Name-Flag`
- [ ] Check `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`
- [ ] Review subject-name configuration
- [ ] Review SAN configuration
- [ ] Review EKUs
- [ ] Review application policies
- [ ] Review Client Authentication
- [ ] Review Smart Card Logon
- [ ] Review PKINIT Client Authentication
- [ ] Review Any Purpose
- [ ] Review no-EKU templates

## Enrollment

- [ ] Identify Enroll rights
- [ ] Identify Autoenroll rights
- [ ] Resolve nested groups
- [ ] Identify broad enrollment groups
- [ ] Verify assessment identity can enroll
- [ ] Verify CA publishes template

## Issuance Requirements

- [ ] Review manager approval
- [ ] Review authorized signatures
- [ ] Review enrollment-agent requirements
- [ ] Review issuance policies
- [ ] Confirm request can actually be issued

## ACLs

- [ ] Review template owner
- [ ] Review GenericAll
- [ ] Review GenericWrite
- [ ] Review WriteProperty
- [ ] Review WriteDACL
- [ ] Review WriteOwner
- [ ] Review group-control paths

## Certificate Mapping

- [ ] Review Domain Controller patch level
- [ ] Review strong certificate mapping
- [ ] Review SID security extension
- [ ] Review UPN mapping
- [ ] Review certificate identity information
- [ ] Do not rely solely on historical mapping assumptions

## Tooling

- [ ] Enumerate with PowerShell
- [ ] Enumerate with LDAP
- [ ] Enumerate with Certipy
- [ ] Review BloodHound paths
- [ ] Verify Certipy version
- [ ] Manually confirm automated ESC1 result

## Validation

- [ ] Prefer configuration evidence
- [ ] Use dedicated test identities
- [ ] Obtain approval before impersonating another account
- [ ] Request one certificate
- [ ] Protect PFX
- [ ] Record serial number
- [ ] Record thumbprint
- [ ] Validate authentication only if required
- [ ] Avoid unnecessary credential extraction
- [ ] Stop after sufficient proof

## Detection

- [ ] Inventory enrollee-supplied subject templates
- [ ] Monitor template changes
- [ ] Monitor template ACL changes
- [ ] Monitor certificate requests
- [ ] Monitor certificate issuance
- [ ] Monitor privileged identity certificates
- [ ] Monitor certificate authentication
- [ ] Correlate requester and certificate identity
- [ ] Monitor relevant 5136 events
- [ ] Review Kerberos 4768 telemetry where applicable

## Hardening

- [ ] Disable requester-supplied identity where unnecessary
- [ ] Restrict enrollment
- [ ] Remove unnecessary authentication EKUs
- [ ] Require approval where appropriate
- [ ] Require signatures where appropriate
- [ ] Protect template ACL
- [ ] Remove unnecessary CA publication
- [ ] Maintain strong certificate mapping
- [ ] Review existing issued certificates
- [ ] Monitor PKI continuously

## Incident Response

- [ ] Identify affected template
- [ ] Identify affected CA
- [ ] Identify requesting account
- [ ] Identify certificate identity
- [ ] Identify serial number
- [ ] Identify thumbprint
- [ ] Identify issue time
- [ ] Identify expiration
- [ ] Identify authentication activity
- [ ] Identify all certificates issued during exposure
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Fix template
- [ ] Fix enrollment rights
- [ ] Fix template ACL
- [ ] Do not rely on password reset alone

## Cleanup

- [ ] Revoke test certificate where required
- [ ] Delete PFX
- [ ] Delete PEM private keys
- [ ] Remove temporary certificate stores
- [ ] Remove temporary test identities
- [ ] Verify certificate is no longer usable
- [ ] Record cleanup evidence

---

# ESC1 Testing Model

The normal enrollment model is:

```text
User
 |
 v
Template
 |
 v
Identity Derived from AD
 |
 v
Certificate for User
```

The ESC1 model is:

```text
User
 |
 v
Template
 |
 v
Requester Supplies Identity
 |
 v
Certificate
```

The dangerous combination is:

```text
Enroll
  +
Enrollee Supplies Subject
  +
Authentication Capability
  +
Weak Issuance Restrictions
  +
Successful Certificate Mapping
  =
Potential Account Impersonation
```

The attack-path model is:

```text
Low-Privileged User
        |
        v
Enroll
        |
        v
ESC1 Template
        |
        v
Requested Identity
        |
        v
Certificate
        |
        v
Certificate Mapping
        |
        v
Target Account
```

The PKINIT model is:

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
TGT
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

The modern assessment model is:

```text
Template Configuration
        |
        v
Certificate Issuance
        |
        v
Certificate Mapping
        |
        v
Authentication
```

The safe-testing model is:

```text
Enumerate
   |
   v
Confirm Template
   |
   v
Confirm Enrollment
   |
   v
Confirm CA Publication
   |
   v
Analyse Mapping
   |
   v
Use Test Identity
   |
   v
Request One Certificate
   |
   v
Authenticate if Required
   |
   v
Stop
   |
   v
Clean Up
```

The defensive model is:

```text
Secure Subject Configuration
          +
Restricted Enrollment
          +
Restricted EKUs
          +
Strong Issuance Requirements
          +
Protected Template ACL
          +
Strong Certificate Mapping
          =
Reduced ESC1 Risk
```

The most important relationship is:

```text
Who Can Request
      |
      v
Which Identity Can They Place in the Request
      |
      v
What Can the Certificate Do
      |
      v
Which Account Will Windows Map It To
```

For penetration testers:

```text
Do Not Ask:
"Does Certipy print ESC1?"

Ask:
"Can my effective security context obtain an
authentication certificate that Windows will
accept as another identity?"
```

For defenders:

```text
Do Not Ask:
"Do we have Supply in the Request enabled?"

Ask:
"Who can use that capability, what certificates
can they obtain, which identities can those
certificates represent, and how will Windows
map them?"
```

The complete ESC1 trust relationship is:

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
Requester-Controlled Identity
   |
   v
Certificate Authority
   |
   v
Authentication Certificate
   |
   v
Certificate Mapping
   |
   v
Active Directory Account
   |
   v
Privilege
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

Active Directory ACL and ACE abuse:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

Active Directory groups:

[Active Directory Groups](../groups.md)

Kerberos:

[Kerberos](../kerberos.md)

Kerberos tickets:

[Kerberos Tickets](../kerberos-tickets.md)

Credential Access:

[Active Directory Credential Access](../credential-access.md)

Shadow Credentials:

[Active Directory Shadow Credentials](../shadow-credentials.md)

BloodHound:

[BloodHound](../bloodhound.md)

The next AD CS page is:

```text
active-directory/ad-cs/esc2.md
```

---

# References

## Microsoft - msPKI-Certificate-Name-Flag

[Microsoft - msPKI-Certificate-Name-Flag Attribute](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-crtd/1192823c-d839-4bc3-9b6b-fa8c53507ae1){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Name Flag Processing

[Microsoft - Certificate.Template.msPKI-Certificate-Name-Flag](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/cf805c29-6f58-4087-a395-3d0233a89f3c){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Template Subject Name Flags

[Microsoft - X509CertificateTemplateSubjectNameFlag](https://learn.microsoft.com/en-us/windows/win32/api/certenroll/ne-certenroll-x509certificatetemplatesubjectnameflag){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Templates

[Microsoft - Certificate Template Concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate-Based Authentication Hardening

[Microsoft - KB5014754 Certificate-Based Authentication Changes](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC1 is fundamentally an:

```text
Identity Issuance Failure
```

The dangerous configuration allows the certificate requester to influence:

```text
Who the Certificate Represents
```

while the certificate may also provide:

```text
Authentication
```

The classic relationship is:

```text
Low-Privileged User
      |
      v
Can Enroll
      |
      v
Supply in the Request
      |
      v
Authentication Certificate
      |
      v
Another Identity
```

However, modern Windows environments require another critical layer:

```text
Certificate Mapping
```

Therefore the modern model is:

```text
Enrollment
    +
Requester-Controlled Identity
    +
Authentication Capability
    +
Issuance
    +
Successful Mapping
    =
ESC1 Impact
```

Do not treat:

```text
Supply in the Request
```

alone as proof of compromise.

Likewise, do not treat:

```text
Certipy: ESC1
```

as the entire finding.

The assessment must determine:

```text
Who Can Enroll?
Which CA Issues It?
What Identity Can Be Requested?
What EKUs Exist?
Is Approval Required?
Are Signatures Required?
What SID Information Is Present?
How Does Windows Map the Certificate?
What Privilege Does the Target Identity Have?
```

For defenders, the most effective strategy is to remove unnecessary flexibility from certificate issuance.

```text
Directory-Derived Identity
        +
Restricted Enrollment
        +
Minimal EKUs
        +
Protected Template ACL
        +
Strong Certificate Mapping
        =
Safer Authentication Template
```

For penetration testers, the strongest finding is not:

```text
ESC1 exists
```

but:

```text
A low-privileged principal can cause the
enterprise PKI to issue authentication
material that the domain accepts as a
higher-privileged identity.
```

That is the actual trust failure represented by a successfully exploitable ESC1 condition.
