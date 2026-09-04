# AD CS ESC13 - Issuance Policy Group Linking

ESC13 is an Active Directory Certificate Services (AD CS) privilege-escalation condition involving certificate issuance policies that are linked to Active Directory security groups.

The central Active Directory attribute is:

```text
msDS-OIDToGroupLink
```

This attribute can associate an enterprise certificate issuance policy with a universal security group.

When a certificate containing the corresponding issuance-policy Object Identifier (OID) is used for authentication, Active Directory can make the linked group SID available in the authenticated user's access token through Authentication Mechanism Assurance (AMA).

The important security relationship is therefore:

```text
Certificate Template
        |
        v
Issuance Policy OID
        |
        v
Enterprise OID Object
        |
        v
msDS-OIDToGroupLink
        |
        v
Universal Security Group
        |
        v
Additional Authorisation
```

If a low-privileged principal can enroll in a certificate template containing an issuance policy that maps to a privileged group, the certificate may provide privileges associated with that group during certificate-based authentication.

This can create an escalation path even though the user is not permanently added to the group in the normal Active Directory `member` attribute.

!!! warning "Authorised testing only"
    ESC13 validation can affect authentication and authorisation. Begin with read-only enumeration of certificate templates, issuance-policy OIDs, `msDS-OIDToGroupLink`, group privileges and enrollment permissions. Where active validation is required, use dedicated test identities and test groups. Do not request certificates that would grant production administrative privileges merely to demonstrate impact.

---

# ESC13 Concept

A simplified ESC13 configuration looks like:

```text
Low-Privilege User
       |
       v
Can Enroll
       |
       v
Certificate Template
       |
       v
Issuance Policy
       |
       v
Enterprise OID
       |
       v
msDS-OIDToGroupLink
       |
       v
Privileged Group
```

The user does not necessarily need to be:

```text
memberOf = PrivilegedGroup
```

in the conventional Active Directory sense.

Instead, certificate authentication can result in the linked group's SID contributing to the user's security context.

---

# Authentication Mechanism Assurance

ESC13 is closely related to:

```text
Authentication Mechanism Assurance
```

or:

```text
AMA
```

AMA allows organisations to associate authentication mechanisms with additional authorisation information.

Conceptually:

```text
Authentication Method
        |
        v
Certificate Issuance Policy
        |
        v
Mapped Security Group
        |
        v
Additional Group SID
```

This can be used legitimately to distinguish stronger forms of authentication.

---

# Legitimate AMA Example

An organisation might create:

```text
High Assurance Certificate Policy
```

and associate it with:

```text
High Assurance Users
```

The intended model could be:

```text
User
 |
 v
Performs Strong Certificate Authentication
 |
 v
Certificate Contains High Assurance Policy
 |
 v
Authentication Mechanism Assurance
 |
 v
High Assurance Group SID
 |
 v
Access to Sensitive Application
```

This can be a legitimate security design.

---

# Where ESC13 Appears

The problem occurs when:

```text
Low-Privilege Enrollment
```

can obtain a certificate containing an issuance policy mapped to:

```text
High-Privilege Group
```

Conceptually:

```text
Low-Privilege User
       |
       v
Enrolls Certificate
       |
       v
Privileged Issuance Policy
       |
       v
AMA
       |
       v
Privileged Group SID
```

---

# ESC13 Is an Authorisation Problem

ESC13 differs from several earlier AD CS techniques.

For example:

```text
ESC1
```

primarily abuses certificate identity selection.

```text
ESC8
```

primarily abuses NTLM relay to enrollment.

```text
ESC13
```

instead abuses the relationship between:

```text
Certificate Policy
```

and:

```text
Active Directory Authorisation
```

---

# The PKI OID Container

Enterprise OID objects are stored in the Active Directory Configuration partition.

The general location is:

```text
CN=OID,
CN=Public Key Services,
CN=Services,
CN=Configuration,
<Forest DN>
```

Conceptually:

```text
Configuration
   |
   v
Services
   |
   v
Public Key Services
   |
   v
OID
   |
   +--> Policy Object
   |
   +--> Policy Object
   |
   +--> Policy Object
```

---

# Forest-Wide Significance

The Configuration naming context is replicated throughout the forest.

Therefore an issuance-policy configuration can have:

```text
Forest-Wide Security Significance
```

even when the certificate template or CA is used primarily within one domain.

---

# Enterprise OID Objects

Enterprise issuance policies can be represented by objects with class:

```text
msPKI-Enterprise-Oid
```

Important attributes can include:

```text
displayName
msPKI-Cert-Template-OID
msDS-OIDToGroupLink
```

The exact attributes present depend on how the OID object is used.

---

# msDS-OIDToGroupLink

The key ESC13 attribute is:

```text
msDS-OIDToGroupLink
```

Conceptually:

```text
Enterprise OID
      |
      v
msDS-OIDToGroupLink
      |
      v
Group Distinguished Name
```

For example:

```text
CN=High Assurance Policy,
CN=OID,
CN=Public Key Services,
CN=Services,
CN=Configuration,
DC=corp,
DC=example
```

might link to:

```text
CN=High Assurance Users,
OU=Groups,
DC=corp,
DC=example
```

---

# Linked Group Requirements

Authentication Mechanism Assurance group linking has specific Active Directory requirements.

The linked group should be a:

```text
Universal Security Group
```

This matters during enumeration.

Do not treat every arbitrary OID-to-group relationship as a valid exploitable ESC13 path without validating the linked group's configuration.

---

# Group Scope

Check:

```text
GroupScope
```

A typical AMA-linked group should be:

```text
Universal
```

---

# Group Category

Check:

```text
GroupCategory
```

The group should be:

```text
Security
```

rather than a distribution group.

---

# Group Membership Is Different

Traditional group membership looks like:

```text
User
 |
 v
memberOf
 |
 v
Security Group
```

ESC13/AMA is different:

```text
User
 |
 v
Certificate Authentication
 |
 v
Issuance Policy
 |
 v
OIDToGroupLink
 |
 v
Security Token
```

This distinction is important for both testing and detection.

---

# Certificate Policies Extension

X.509 certificates can contain:

```text
Certificate Policies
```

The extension contains one or more policy OIDs.

Conceptually:

```text
Certificate
    |
    v
Certificate Policies
    |
    +--> 1.2.3.4.5
    |
    +--> 1.2.3.4.6
```

An enterprise issuance-policy OID can appear in this extension.

---

# Template Issuance Policies

Certificate templates can define issuance policies.

Conceptually:

```text
Certificate Template
       |
       v
Issuance Policies
       |
       v
Policy OID
```

When the CA issues a certificate from the template, the resulting certificate can contain the configured policy OID.

---

# ESC13 Core Conditions

A useful assessment model is:

```text
Template Published
       +
Low-Privilege Enrollment
       +
Authentication-Capable Certificate
       +
Issuance Policy Present
       +
OID Linked to Group
       +
Linked Group Has Valuable Privileges
       =
Potential ESC13
```

Every condition should be validated.

---

# Condition 1 - Template Is Published

A template normally needs to be available through an Enterprise CA.

Conceptually:

```text
Template Exists
      |
      v
Published by CA?
      |
      +--> No -> No Normal Enrollment Path
      |
      +--> Yes
```

---

# Condition 2 - Low-Privilege Enrollment

Determine who can enroll.

Potentially broad principals include:

```text
Authenticated Users
Domain Users
Domain Computers
Large Organisational Groups
```

Broad enrollment is not automatically vulnerable.

It becomes important when combined with the linked issuance policy.

---

# Condition 3 - Authentication Capability

The resulting certificate must be useful for the relevant authentication path.

Common authentication-related EKUs include:

```text
Client Authentication
1.3.6.1.5.5.7.3.2
```

```text
Smart Card Logon
1.3.6.1.4.1.311.20.2.2
```

```text
PKINIT Client Authentication
1.3.6.1.5.2.3.4
```

Evaluate the complete certificate configuration rather than relying on one field alone.

---

# Condition 4 - Issuance Policy

The template must contain an issuance policy relevant to the AMA configuration.

Conceptually:

```text
Template
   |
   v
Issuance Policy OID
```

---

# Condition 5 - OID-to-Group Link

The issuance-policy object must link to an Active Directory group through:

```text
msDS-OIDToGroupLink
```

---

# Condition 6 - Group Provides Valuable Access

The linked group must actually matter.

For example:

```text
Certificate Policy
       |
       v
Group
       |
       v
No Privileges
```

may have limited security impact.

Whereas:

```text
Certificate Policy
       |
       v
Privileged Group
       |
       v
Sensitive Resource Access
```

can be significant.

---

# Privilege Does Not Mean Domain Admin

A linked group does not need to be:

```text
Domain Admins
```

to create serious impact.

It may provide:

```text
Server Administration
Application Administration
PKI Administration
Database Access
Remote Management
Backup Access
Tier 0 Resource Access
Sensitive File Access
```

---

# Nested Group Relationships

The linked group itself may not look privileged.

For example:

```text
AMA-Certificate-Users
        |
        v
Nested Into
        |
        v
Server-Administrators
```

Therefore group analysis must include:

```text
Nested Membership
```

and:

```text
Effective Permissions
```

---

# ACL-Based Privilege

The linked group may also have dangerous ACL rights.

For example:

```text
AMA Group
   |
   v
GenericAll
   |
   v
Sensitive User
```

or:

```text
AMA Group
   |
   v
WriteDACL
   |
   v
Tier 0 Group
```

BloodHound is particularly useful for identifying these indirect relationships.

---

# Enumerate OID Objects with PowerShell

Load the Active Directory module:

```powershell
Import-Module ActiveDirectory
```

Determine the Configuration naming context:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
```

Build the OID container path:

```powershell
$oidBase = "CN=OID,CN=Public Key Services,CN=Services,$configNC"
```

Enumerate enterprise OID objects:

```powershell
Get-ADObject -SearchBase $oidBase -LDAPFilter '(objectClass=msPKI-Enterprise-Oid)' -Properties displayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink |
    Select-Object Name,displayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink,DistinguishedName
```

---

# Find Only Group-Linked OIDs

A more focused query:

```powershell
Get-ADObject -SearchBase $oidBase -LDAPFilter '(&(objectClass=msPKI-Enterprise-Oid)(msDS-OIDToGroupLink=*))' -Properties displayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink |
    Select-Object Name,displayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink
```

This is a useful read-only ESC13 discovery step.

---

# Resolve Linked Groups

```powershell
$linkedOids = Get-ADObject -SearchBase $oidBase -LDAPFilter '(&(objectClass=msPKI-Enterprise-Oid)(msDS-OIDToGroupLink=*))' -Properties displayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink

foreach ($oid in $linkedOids) {
    $group = Get-ADGroup -Identity $oid.'msDS-OIDToGroupLink' -Properties GroupScope,GroupCategory

    [PSCustomObject]@{
        PolicyName    = $oid.displayName
        PolicyOID     = $oid.'msPKI-Cert-Template-OID'
        LinkedGroup   = $group.Name
        GroupScope    = $group.GroupScope
        GroupCategory = $group.GroupCategory
    }
}
```

This provides:

```text
Policy
OID
Linked Group
Group Scope
Group Category
```

---

# Inspect One Linked Group

```powershell
Get-ADGroup -Identity 'CN=High Assurance Users,OU=Groups,DC=corp,DC=example' -Properties * |
    Select-Object Name,SamAccountName,GroupScope,GroupCategory,DistinguishedName
```

---

# Review Direct Group Members

```powershell
Get-ADGroupMember -Identity 'High Assurance Users'
```

Do not assume the absence of normal members means the group is unused.

AMA may provide group membership dynamically during authentication.

---

# Review Nested Group Membership

```powershell
Get-ADPrincipalGroupMembership 'High Assurance Users' |
    Select-Object Name,GroupScope,GroupCategory
```

This helps identify whether the AMA-linked group belongs to other groups.

---

# Recursive Group Analysis

Where appropriate:

```powershell
Get-ADGroupMember -Identity 'TargetGroup' -Recursive
```

Remember that:

```text
Recursive Members
```

and:

```text
Groups Containing This Group
```

answer different questions.

---

# Enumerate Certificate Templates

The template container is:

```powershell
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"
```

Enumerate templates:

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties * |
    Select-Object Name,displayName,DistinguishedName
```

---

# Template Issuance Policy Attribute

Issuance-policy configuration is commonly represented through:

```text
msPKI-Certificate-Policy
```

Enumerate templates containing certificate policies:

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(&(objectClass=pKICertificateTemplate)(msPKI-Certificate-Policy=*))' -Properties displayName,msPKI-Certificate-Policy |
    Select-Object Name,displayName,msPKI-Certificate-Policy
```

---

# Correlate Templates with Linked OIDs

The important analysis is:

```text
Template Policy OID
       |
       v
Enterprise OID Object
       |
       v
msDS-OIDToGroupLink
```

A PowerShell workflow:

```powershell
$linkedOids = Get-ADObject -SearchBase $oidBase -LDAPFilter '(&(objectClass=msPKI-Enterprise-Oid)(msDS-OIDToGroupLink=*))' -Properties displayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink

$templates = Get-ADObject -SearchBase $templateBase -LDAPFilter '(&(objectClass=pKICertificateTemplate)(msPKI-Certificate-Policy=*))' -Properties displayName,msPKI-Certificate-Policy

foreach ($template in $templates) {
    foreach ($policy in $template.'msPKI-Certificate-Policy') {
        $match = $linkedOids |
            Where-Object { $_.'msPKI-Cert-Template-OID' -eq $policy }

        foreach ($oid in $match) {
            [PSCustomObject]@{
                Template    = $template.displayName
                PolicyOID   = $policy
                PolicyName  = $oid.displayName
                LinkedGroup = $oid.'msDS-OIDToGroupLink'
            }
        }
    }
}
```

This is one of the most useful native ESC13 enumeration workflows.

---

# Important Attribute Distinction

Do not confuse:

```text
msPKI-Cert-Template-OID
```

with:

```text
msPKI-Certificate-Policy
```

Conceptually:

```text
OID Object
  |
  +--> msPKI-Cert-Template-OID
       identifies the OID represented by the object
```

while:

```text
Certificate Template
  |
  +--> msPKI-Certificate-Policy
       references issuance-policy OIDs
```

The correlation between these values creates the relevant relationship.

---

# Enumerate Published Templates

Identify Enterprise CAs:

```powershell
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties dNSHostName,certificateTemplates |
    Select-Object Name,dNSHostName,certificateTemplates
```

This helps determine whether an interesting template is actually published.

---

# Publication Matters

A template may contain an interesting issuance policy but have no usable enrollment path.

Conceptually:

```text
Interesting Template
      |
      v
Published?
      |
      +--> No -> Limited Immediate Exposure
      |
      +--> Yes -> Continue
```

---

# Template Security Descriptor

Inspect the template ACL:

```powershell
$template = Get-ADObject -SearchBase $templateBase -LDAPFilter '(cn=TargetTemplate)' -Properties DistinguishedName
```

Then:

```powershell
Get-Acl "AD:$($template.DistinguishedName)" |
    Format-List Owner,AccessToString
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

---

# Enrollment Rights

ESC13 requires more than an issuance policy.

The attacker must have a usable enrollment path.

Therefore evaluate:

```text
Certificate Template
        |
        v
Enrollment Permissions
        |
        v
Attacker Effective Rights
```

---

# Effective Permissions

Do not evaluate only direct ACEs.

Consider:

```text
Direct Group Membership
Nested Groups
Inherited ACEs
Deny ACEs
Object-Specific ACEs
```

---

# Certipy Enumeration

Certipy can automate much of the AD CS discovery process.

Check the installed version:

```bash
certipy --version
```

Review available options:

```bash
certipy find -h
```

Typical read-only enumeration:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review:

```text
Certificate Authorities
Certificate Templates
Issuance Policies
Permissions
ESC Findings
```

---

# Certipy ESC13 Output

Where Certipy identifies ESC13, manually validate:

```text
Template
Issuance Policy
OID
Linked Group
Enrollment Rights
Authentication Capability
Group Privilege
```

Do not report:

```text
ESC13
```

based solely on a scanner label.

---

# LDAP Enumeration from Linux

The OID container can also be queried directly.

Example:

```bash
ldapsearch -LLL -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=OID,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(&(objectClass=msPKI-Enterprise-Oid)(msDS-OIDToGroupLink=*))' \
    cn \
    displayName \
    msPKI-Cert-Template-OID \
    msDS-OIDToGroupLink
```

---

# LDAP Template Enumeration

```bash
ldapsearch -LLL -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(&(objectClass=pKICertificateTemplate)(msPKI-Certificate-Policy=*))' \
    cn \
    displayName \
    msPKI-Certificate-Policy
```

Correlate:

```text
msPKI-Certificate-Policy
```

with:

```text
msPKI-Cert-Template-OID
```

from the OID objects.

---

# BloodHound Analysis

BloodHound is valuable because ESC13 is ultimately an:

```text
Authorisation Graph
```

problem.

Conceptually:

```text
User
 |
 v
Enroll
 |
 v
Certificate Template
 |
 v
Issuance Policy
 |
 v
Linked Group
 |
 v
Privilege
```

---

# Group Privilege Analysis

Once the linked group is identified, ask:

```text
What can this group actually do?
```

Potential relationships include:

```text
AdminTo
GenericAll
GenericWrite
WriteDACL
WriteOwner
AddMember
ForceChangePassword
AllowedToDelegate
Remote Management
Sensitive Application Access
```

---

# Hidden ESC13 Impact

Consider:

```text
Issuance Policy
       |
       v
Group A
       |
       v
MemberOf
       |
       v
Group B
       |
       v
AdminTo
       |
       v
Tier 0 Server
```

The dangerous privilege may be several graph edges away from the OID link.

---

# ESC13 and Group Membership

One of the unusual characteristics of ESC13 is that:

```text
Get-ADGroupMember
```

may not show the authenticating user as a permanent member of the AMA group.

The authorisation is associated with the certificate authentication mechanism.

This can confuse incident responders who only inspect normal AD membership.

---

# Certificate Inspection

If an authorised test certificate is issued, inspect its certificate policies.

Windows:

```cmd
certutil -dump esc13-test.cer
```

Look for:

```text
Certificate Policies
```

and the expected issuance-policy OID.

---

# OpenSSL Inspection

PEM:

```bash
openssl x509 -in esc13-test.pem -text -noout
```

DER:

```bash
openssl x509 -in esc13-test.cer -inform DER -text -noout
```

Review:

```text
X509v3 Certificate Policies
```

---

# Validate the Policy, Not Just the Template

The strongest evidence is:

```text
Template Configuration
       |
       v
Issued Certificate
       |
       v
Expected Policy OID Present
```

This confirms the CA actually placed the issuance policy into the certificate.

---

# Safe Validation

A safe ESC13 validation should use:

```text
Dedicated Test User
        |
        v
Dedicated Test Template
        |
        v
Non-Privileged Test AMA Group
        |
        v
Controlled Resource
```

This reproduces the security behaviour without granting production administrative rights.

---

# Do Not Use Domain Admins

Avoid linking or testing against:

```text
Domain Admins
Enterprise Admins
Administrators
Account Operators
Backup Operators
```

or other production privileged groups.

Configuration evidence is normally sufficient to establish the risk.

---

# Read-Only Validation

A strong read-only proof may establish:

```text
Low-Privilege User Can Enroll
            |
            v
Template Contains Policy OID
            |
            v
OID Links to Group
            |
            v
Group Has Sensitive Privilege
```

No privileged certificate needs to be requested.

---

# Controlled Enrollment

If active validation is required, use a dedicated test identity and verify the installed Certipy syntax first:

```bash
certipy req -h
```

The objective is only to demonstrate:

```text
Certificate Issued
        |
        v
Expected Issuance Policy Present
```

rather than compromising a privileged account.

---

# Authentication Validation

Where an end-to-end AMA test is explicitly required, authenticate using a dedicated test environment.

The validation question is:

```text
Does certificate authentication
produce the expected additional
authorisation associated with
the linked group?
```

Do not use production privileged resources as the test target.

---

# Test Resource

A safe laboratory model:

```text
ESC13-Test-User
       |
       v
ESC13-Test-Template
       |
       v
ESC13-Test-Policy
       |
       v
ESC13-Test-Group
       |
       v
Read Access to Test Folder
```

Then compare:

```text
Password Authentication
```

with:

```text
Certificate Authentication
```

against the test resource.

---

# Expected Behaviour

Without AMA certificate:

```text
Test User
   |
   X
Test Resource
```

With AMA certificate:

```text
Test User
   |
   v
Certificate Authentication
   |
   v
Test AMA Group
   |
   v
Test Resource
```

This demonstrates the mechanism safely.

---

# ESC13 and ESC1

ESC1 concerns requester-controlled identity information.

ESC13 concerns issuance-policy-to-group mapping.

They can coexist:

```text
ESC1
 +
ESC13
```

but they should be assessed separately.

---

# ESC13 and ESC2

ESC2 concerns Any Purpose or unrestricted certificate usage.

ESC13 specifically requires:

```text
Issuance Policy
       |
       v
Group Link
```

An Any Purpose certificate alone does not establish ESC13.

---

# ESC13 and ESC3

ESC3 involves Enrollment Agent functionality.

ESC13 involves Authentication Mechanism Assurance.

Both can create indirect certificate-based escalation, but through different mechanisms.

---

# ESC13 and ESC4

ESC4 can be particularly relevant.

Suppose an attacker can modify a certificate template:

```text
Attacker
   |
   v
ESC4
   |
   v
Modify Template
   |
   v
Add Issuance Policy
   |
   v
ESC13-Like Path
```

Whether the resulting path is exploitable depends on the OID and linked-group configuration.

---

# ESC13 and ESC5

ESC5 concerns dangerous permissions over broader PKI objects.

Because enterprise OID objects live under:

```text
CN=OID,CN=Public Key Services,...
```

weak ACLs on those objects may affect issuance-policy security.

This can create a relationship between:

```text
ESC5
```

and:

```text
ESC13
```

---

# OID Object ACLs

Inspect the ACL on a linked OID:

```powershell
$oid = Get-ADObject -SearchBase $oidBase -LDAPFilter '(&(objectClass=msPKI-Enterprise-Oid)(msDS-OIDToGroupLink=*))' -Properties * |
    Select-Object -First 1
```

Then:

```powershell
Get-Acl "AD:$($oid.DistinguishedName)" |
    Format-List Owner,AccessToString
```

Review:

```text
GenericAll
GenericWrite
WriteProperty
WriteDACL
WriteOwner
```

---

# Why OID ACLs Matter

If an attacker can modify:

```text
msDS-OIDToGroupLink
```

they may be able to change which group receives the policy's authorisation semantics.

This should be treated as highly sensitive PKI configuration.

---

# Do Not Modify Production OIDs

During routine testing, do not change:

```text
msDS-OIDToGroupLink
```

on production OID objects.

Changing the link can alter authorisation for certificate-based authentication.

Use ACL evidence instead.

---

# ESC13 and ESC15

ESC15 concerns application-policy manipulation in vulnerable schema version 1 certificate templates and is a separate AD CS technique.

Do not confuse:

```text
Application Policies
```

with:

```text
Issuance Policies
```

They are different certificate concepts.

---

# Application Policy vs Issuance Policy

Application policy answers:

```text
What may this certificate be used for?
```

Examples:

```text
Client Authentication
Server Authentication
Code Signing
Enrollment Agent
```

Issuance policy answers more along the lines of:

```text
Under what policy or assurance
conditions was this certificate issued?
```

ESC13 concerns the second category.

---

# EKU vs Certificate Policy

Another useful distinction:

```text
Extended Key Usage
        |
        v
Permitted Certificate Purpose
```

versus:

```text
Certificate Policy
        |
        v
Issuance / Assurance Policy
```

Do not treat policy OIDs as EKUs.

---

# Detecting ESC13

Detection should cover:

```text
OID Configuration
       +
Template Configuration
       +
Certificate Issuance
       +
Authentication
       +
Group Authorisation
```

---

# Monitor msDS-OIDToGroupLink

Changes to:

```text
msDS-OIDToGroupLink
```

should be treated as security-sensitive.

The object resides in the Configuration naming context.

---

# Event 5136

Where Directory Service Changes auditing is enabled:

```text
5136
```

can record modifications to Active Directory objects.

Monitor changes affecting:

```text
msDS-OIDToGroupLink
```

---

# Monitor OID Objects

Monitor changes beneath:

```text
CN=OID,
CN=Public Key Services,
CN=Services,
CN=Configuration
```

especially:

```text
Create
Delete
ACL Change
Owner Change
OID Value Change
Group Link Change
```

---

# Monitor Certificate Templates

Monitor changes to:

```text
msPKI-Certificate-Policy
```

on certificate templates.

A new issuance policy can change the security meaning of certificates issued from that template.

---

# Monitor Template ACLs

Monitor changes to:

```text
nTSecurityDescriptor
```

on certificate templates.

Unexpected ACL changes can enable an attacker to introduce a dangerous issuance policy.

---

# Monitor OID ACLs

Changes to OID object:

```text
Owner
DACL
WriteProperty Rights
```

should also be investigated.

---

# Certificate Services Auditing

Where Certificate Services auditing is enabled, events such as:

```text
4886
4887
```

can help identify certificate requests and issuance.

---

# Correlate Certificate Policy

For sensitive templates, record which policy OIDs should normally appear.

A suspicious sequence could be:

```text
Template Modified
      |
      v
New Issuance Policy
      |
      v
Certificate Requested
      |
      v
Certificate Issued
      |
      v
Privileged Resource Access
```

---

# Authentication Detection

Certificate-based Kerberos authentication may produce:

```text
4768
```

events.

Correlate:

```text
Certificate Issuance
```

with:

```text
Certificate Authentication
```

and subsequent access to resources controlled by the AMA group.

---

# Group Membership Monitoring Limitation

Traditional monitoring may look for:

```text
4728
4732
4756
```

group membership events.

ESC13 can be important precisely because no conventional permanent membership change may occur.

Therefore:

```text
No Add-Member Event
```

does not prove:

```text
No Group-Based Privilege
```

---

# Authentication Context

Detection teams should understand that:

```text
Same User
```

may have different effective authorisation depending on the authentication mechanism.

Conceptually:

```text
User + Password
      |
      v
Token A
```

versus:

```text
User + AMA Certificate
      |
      v
Token B
```

---

# Privileged Group Baseline

Maintain an inventory of groups referenced by:

```text
msDS-OIDToGroupLink
```

For each group record:

```text
Group Name
SID
Scope
Category
Purpose
Owner
Privileges
Nested Groups
Linked OID
Associated Templates
```

---

# Hardening ESC13

The primary defensive objective is:

```text
Only Properly Controlled Certificates
Should Produce High-Assurance Group
Authorisation
```

---

# Review Every OID-to-Group Link

Enumerate:

```text
msDS-OIDToGroupLink
```

throughout the forest.

For every link ask:

```text
Is This Still Required?
```

and:

```text
Does the Linked Group Have
Appropriate Privileges?
```

---

# Minimise Linked-Group Privilege

Do not use an AMA-linked group as a shortcut for broad administrative access.

Prefer narrowly scoped permissions.

For example:

```text
High Assurance Application Access
```

is safer than:

```text
General Server Administrators
```

when the business requirement only concerns one application.

---

# Restrict Template Enrollment

Templates carrying privileged issuance policies should not allow broad enrollment.

Avoid unnecessary enrollment for:

```text
Authenticated Users
Domain Users
Domain Computers
```

---

# Review Manager Approval

Where appropriate, consider:

```text
Certificate Manager Approval
```

for high-assurance templates.

This should complement, not replace, proper enrollment ACLs.

---

# Review Authorised Signatures

Sensitive templates may use authorised-signature requirements where appropriate.

Evaluate operational requirements carefully before changing production templates.

---

# Protect Template ACLs

Only trusted PKI administrators should be able to modify:

```text
msPKI-Certificate-Policy
EKUs
Enrollment Settings
Template ACL
```

on sensitive templates.

---

# Protect OID ACLs

Restrict modification of enterprise OID objects.

Particularly protect:

```text
msDS-OIDToGroupLink
```

---

# Protect the OID Container

Review ACLs on:

```text
CN=OID,CN=Public Key Services,CN=Services,CN=Configuration
```

including inherited rights.

A dangerous parent-container ACL may affect many policy objects.

---

# Separate PKI and Group Administration

Where feasible, avoid allowing ordinary group administrators to modify PKI policy objects and ordinary PKI operators to grant arbitrary privileged group access.

Use separation of duties.

---

# Review Nested Groups

A group may appear low-risk while inheriting powerful privileges through nesting.

Review the complete group graph.

---

# Review Resource ACLs

Determine what resources trust the linked group.

Examples:

```text
Servers
File Shares
Applications
Databases
Remote Management
PKI Infrastructure
Backup Infrastructure
```

---

# Remove Stale AMA Configuration

Legacy issuance policies and linked groups should be removed when no longer required.

Old PKI configurations often survive long after the original business requirement disappears.

---

# Document Business Purpose

Every:

```text
msDS-OIDToGroupLink
```

relationship should have a documented:

```text
Business Owner
Security Owner
Purpose
Associated Template
Expected Users
Expected Resources
Review Date
```

---

# Incident Response

If ESC13 abuse is suspected:

```text
Identify Policy OID
       |
       v
Identify Linked Group
       |
       v
Identify Templates
       |
       v
Identify Issued Certificates
       |
       v
Identify Authentication
       |
       v
Identify Resource Access
```

---

# Preserve OID Configuration

Record:

```text
OID Distinguished Name
displayName
msPKI-Cert-Template-OID
msDS-OIDToGroupLink
Owner
DACL
```

before making changes.

---

# Review OID Modification History

Investigate:

```text
5136
```

and other directory-change telemetry for modifications to:

```text
msDS-OIDToGroupLink
```

---

# Review Template Changes

Investigate changes to:

```text
msPKI-Certificate-Policy
```

and template ACLs.

Determine:

```text
Who Changed It?
When?
From Which Host?
Was It Approved?
```

---

# Identify Certificates

Search CA records for certificates issued from affected templates.

Record:

```text
Request ID
Requester
Template
Serial Number
Subject
SAN
Validity
Disposition
```

---

# Inspect Certificate Policies

For suspicious certificates, inspect:

```text
Certificate Policies
```

and identify whether the dangerous issuance-policy OID is present.

---

# Revoke Suspicious Certificates

Where unauthorised certificates were issued:

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

# Correct the Policy Link

If an OID was maliciously or incorrectly linked:

```text
Remove / Correct Link
```

through controlled PKI and Active Directory change management.

Preserve evidence first.

---

# Review Group Privileges

The linked group may have been granted additional permissions after the OID was configured.

Therefore investigate:

```text
Group ACL Changes
Nested Membership Changes
Resource Permission Changes
```

---

# Review Certificate Authentication

Determine whether affected certificates were used to authenticate.

Correlate:

```text
Certificate Issuance
       |
       v
Kerberos Authentication
       |
       v
Resource Access
```

---

# Reporting ESC13

Avoid a title containing only:

```text
ESC13
```

Prefer descriptive titles such as:

```text
Certificate Issuance Policy Grants Privileged Group Authorisation
```

or:

```text
Low-Privilege Users Can Obtain Certificates Mapped to a Privileged Group
```

or:

```text
AD CS Issuance Policy Is Linked to an Overprivileged Security Group
```

---

# Example Finding

```text
Finding:
Low-Privilege Users Can Obtain Certificates Mapped to a
Privileged Security Group

Affected Template:
HighAssuranceUser

Affected Issuance Policy:
Corporate High Assurance

Policy OID:
1.2.3.4.5.6.7.8

Linked Group:
CORP\High-Assurance-Administrators

Description:
The HighAssuranceUser certificate template contains an issuance
policy that is represented by an enterprise OID object in Active
Directory.

The OID object's msDS-OIDToGroupLink attribute references the
High-Assurance-Administrators universal security group.

Low-privileged domain users have enrollment permission on the
certificate template.

During certificate-based authentication, Authentication Mechanism
Assurance can associate the linked group with the authenticated
security context.

As a result, users who are not conventional members of the linked
group may receive authorisation associated with that group when
authenticating using a certificate containing the issuance policy.

Impact:
The linked group has administrative access to sensitive servers.

A low-privileged domain user able to enroll in the affected template
may therefore obtain certificate-based access associated with the
privileged group.

No production privileged certificate was requested during testing.

Recommendation:
Restrict enrollment on the affected template to principals that are
explicitly authorised to receive the high-assurance policy.

Review the privileges assigned to the linked universal security
group.

Protect the certificate template and enterprise OID object against
unauthorised modification.

Review all msDS-OIDToGroupLink relationships in the forest and remove
stale or unnecessary mappings.
```

---

# Severity Assessment

Use:

```text
Enrollment Accessibility
       +
Authentication Capability
       +
Issuance Policy
       +
Linked Group
       +
Group Privilege
       =
Severity
```

---

# Lower-Risk Example

```text
Domain Users
    |
    v
Certificate Template
    |
    v
Issuance Policy
    |
    v
Group
    |
    v
Access to Non-Sensitive Application
```

This may represent limited impact depending on intended design.

---

# High-Risk Example

```text
Domain Users
    |
    v
Certificate Template
    |
    v
Issuance Policy
    |
    v
Privileged Group
    |
    v
Server Administration
```

This can represent a significant privilege-escalation path.

---

# Critical Example

```text
Low-Privilege User
       |
       v
Certificate Enrollment
       |
       v
Issuance Policy
       |
       v
AMA Group
       |
       v
Tier 0 Control
```

This may represent domain or forest compromise depending on the linked privileges.

---

# Evidence Checklist

Record:

```text
Forest
Domain
CA Name
CA Hostname
Template Name
Template Distinguished Name
Template Published Status
Enrollment Principals
Authentication EKUs
Manager Approval
Authorised Signatures
msPKI-Certificate-Policy
Enterprise OID Name
Enterprise OID Distinguished Name
msPKI-Cert-Template-OID
msDS-OIDToGroupLink
Linked Group Name
Linked Group SID
Group Scope
Group Category
Nested Group Relationships
Group ACL Rights
Resource Privileges
OID Object Owner
OID Object ACL
Template Owner
Template ACL
Certificate Request ID
Certificate Serial Number
Certificate Thumbprint
Certificate Policy OIDs
Validation Method
Cleanup Result
```

---

# ESC13 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify CA hosts
- [ ] Identify published templates
- [ ] Identify authentication templates
- [ ] Identify issuance policies
- [ ] Identify enterprise OID objects
- [ ] Identify `msDS-OIDToGroupLink`
- [ ] Identify linked groups

## OID Analysis

- [ ] Enumerate `msPKI-Enterprise-Oid`
- [ ] Record `displayName`
- [ ] Record `msPKI-Cert-Template-OID`
- [ ] Record `msDS-OIDToGroupLink`
- [ ] Resolve linked group
- [ ] Verify group exists
- [ ] Verify security group
- [ ] Verify universal scope
- [ ] Review OID owner
- [ ] Review OID ACL
- [ ] Review inherited rights

## Template Analysis

- [ ] Identify templates using linked policy OIDs
- [ ] Record `msPKI-Certificate-Policy`
- [ ] Confirm template publication
- [ ] Review enrollment rights
- [ ] Review authentication EKUs
- [ ] Review manager approval
- [ ] Review authorised signatures
- [ ] Review template owner
- [ ] Review template ACL
- [ ] Review ESC4 exposure

## Group Analysis

- [ ] Identify linked group SID
- [ ] Review direct membership
- [ ] Review nested membership
- [ ] Review parent groups
- [ ] Review ACL privileges
- [ ] Review server administration
- [ ] Review application access
- [ ] Review remote-management rights
- [ ] Review Tier 0 access
- [ ] Review BloodHound paths
- [ ] Determine actual privilege

## Native Windows

- [ ] Enumerate Configuration naming context
- [ ] Enumerate OID container
- [ ] Enumerate linked OIDs
- [ ] Resolve linked groups
- [ ] Enumerate template policies
- [ ] Correlate template OIDs
- [ ] Enumerate published templates
- [ ] Review ACLs
- [ ] Inspect test certificate where authorised

## Linux

- [ ] Enumerate AD CS with Certipy
- [ ] Verify Certipy version
- [ ] Review ESC13 output
- [ ] Confirm findings manually
- [ ] Query OID objects with LDAP
- [ ] Query templates with LDAP
- [ ] Correlate policy OIDs
- [ ] Review group privileges

## Validation

- [ ] Prefer read-only validation
- [ ] Confirm low-privilege enrollment
- [ ] Confirm issuance-policy OID
- [ ] Confirm OID-to-group link
- [ ] Confirm linked-group privilege
- [ ] Determine whether active proof is required
- [ ] Use dedicated test identity
- [ ] Use non-privileged test group
- [ ] Use controlled resource
- [ ] Inspect issued certificate
- [ ] Confirm certificate policy
- [ ] Avoid production privileged groups
- [ ] Stop after sufficient proof

## Related Conditions

- [ ] Review ESC1
- [ ] Review ESC2
- [ ] Review ESC3
- [ ] Review ESC4
- [ ] Review ESC5
- [ ] Review ESC15
- [ ] Review certificate mapping
- [ ] Review PKI object ACLs

## Detection

- [ ] Monitor `msDS-OIDToGroupLink`
- [ ] Monitor `msPKI-Certificate-Policy`
- [ ] Monitor OID object creation
- [ ] Monitor OID deletion
- [ ] Monitor OID ACL changes
- [ ] Monitor OID ownership changes
- [ ] Monitor template changes
- [ ] Monitor template ACL changes
- [ ] Monitor event 5136
- [ ] Monitor certificate requests
- [ ] Monitor event 4886 where configured
- [ ] Monitor certificate issuance
- [ ] Monitor event 4887 where configured
- [ ] Monitor certificate authentication
- [ ] Monitor sensitive resource access
- [ ] Do not rely only on group membership events

## Hardening

- [ ] Inventory every OID-to-group link
- [ ] Document business purpose
- [ ] Restrict template enrollment
- [ ] Minimise linked-group privileges
- [ ] Review nested groups
- [ ] Protect template ACLs
- [ ] Protect OID ACLs
- [ ] Protect OID container ACLs
- [ ] Apply separation of duties
- [ ] Remove stale issuance policies
- [ ] Remove unnecessary group links
- [ ] Review high-assurance templates periodically
- [ ] Review resource permissions
- [ ] Treat privileged AMA configuration as Tier 0

## Incident Response

- [ ] Identify affected OID
- [ ] Identify linked group
- [ ] Identify affected templates
- [ ] Preserve current configuration
- [ ] Review directory changes
- [ ] Review template changes
- [ ] Review OID ACL changes
- [ ] Identify issued certificates
- [ ] Inspect certificate policies
- [ ] Review certificate authentication
- [ ] Review resource access
- [ ] Revoke malicious certificates
- [ ] Correct malicious group links
- [ ] Correct template configuration
- [ ] Review group privileges
- [ ] Determine full compromise scope

## Reporting

- [ ] Use descriptive title
- [ ] Identify exact template
- [ ] Identify policy OID
- [ ] Identify OID object
- [ ] Identify linked group
- [ ] Explain AMA
- [ ] Explain enrollment rights
- [ ] Explain actual group privilege
- [ ] Separate theoretical and demonstrated impact
- [ ] Avoid claiming conventional permanent group membership
- [ ] Provide specific remediation

---

# ESC13 Testing Model

The normal issuance-policy model is:

```text
Certificate Template
        |
        v
Issuance Policy
        |
        v
Certificate
```

The AMA model is:

```text
Certificate
    |
    v
Issuance Policy
    |
    v
Enterprise OID
    |
    v
msDS-OIDToGroupLink
    |
    v
Universal Security Group
```

The ESC13 model is:

```text
Low-Privilege User
       |
       v
Can Enroll
       |
       v
Authentication Certificate
       |
       v
Privileged Issuance Policy
       |
       v
AMA
       |
       v
Privileged Group
```

The privilege model is:

```text
Certificate
    |
    v
Policy OID
    |
    v
Linked Group
    |
    +--> Resource Access
    |
    +--> Server Administration
    |
    +--> ACL Rights
    |
    +--> Nested Privilege
```

The indirect path model is:

```text
User
 |
 v
Enroll
 |
 v
Template
 |
 v
Policy
 |
 v
Group A
 |
 v
Group B
 |
 v
Tier 0 Resource
```

The ESC4 relationship is:

```text
Attacker
   |
   v
ESC4 Template Control
   |
   v
Modify Certificate Policy
   |
   v
Linked Enterprise OID
   |
   v
Privileged AMA Group
```

The ESC5 relationship is:

```text
Attacker
   |
   v
ESC5 PKI Object Control
   |
   v
OID Object
   |
   v
msDS-OIDToGroupLink
   |
   v
Privileged Group
```

The safe-testing model is:

```text
Enumerate OIDs
    |
    v
Identify Group Links
    |
    v
Identify Templates
    |
    v
Review Enrollment
    |
    v
Review Group Privilege
    |
    v
Evidence Sufficient?
    |
    +--> Yes -> Report
    |
    +--> No
            |
            v
      Dedicated Test Environment
            |
            v
      Test Certificate
            |
            v
      Test AMA Group
            |
            v
      Controlled Resource
```

The detection model is:

```text
OID Change
   |
   v
Template Policy
   |
   v
Certificate Issuance
   |
   v
Certificate Authentication
   |
   v
AMA Authorisation
   |
   v
Sensitive Resource Access
```

The defensive model is:

```text
Restricted Enrollment
        +
Protected OID Objects
        +
Protected Templates
        +
Least-Privilege AMA Groups
        +
Monitoring
        =
Reduced ESC13 Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I obtain Domain Admin through
this certificate?"

Ask:
"Can I demonstrate the complete
template -> policy -> OID -> group ->
privilege relationship without
granting myself production
administrative access?"
```

For defenders:

```text
Do Not Assume:
"The user is not a member of the
privileged group, so the group
cannot affect them."

Ask:
"Can certificate authentication
cause this group's SID to become
part of the user's authorisation
context?"
```

The complete ESC13 relationship is:

```text
Enrollment
   |
   v
Certificate Template
   |
   v
Issuance Policy
   |
   v
Enterprise OID
   |
   v
msDS-OIDToGroupLink
   |
   v
Security Group
   |
   v
Effective Privilege
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC4:

[AD CS ESC4](esc4.md)

ESC5:

[AD CS ESC5](esc5.md)

ESC12:

[AD CS ESC12](esc12.md)

BloodHound:

[BloodHound](../bloodhound.md)

Groups:

[Active Directory Groups](../groups.md)

ACLs and ACEs:

[ACL and ACE](../acl-ace.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs/esc14.md
```

---

# References

## Microsoft - Authentication Mechanism Assurance

[Microsoft - Authentication Mechanism Assurance for AD DS](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/how-to-configure-authentication-mechanism-assurance){ target="_blank" rel="noopener noreferrer" }

Microsoft documents Authentication Mechanism Assurance and the relationship between certificate issuance policies and universal security groups.

---

## Microsoft - msDS-OIDToGroupLink

[Microsoft - msDS-OIDToGroupLink Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-msds-oidtogrouplink){ target="_blank" rel="noopener noreferrer" }

This attribute links an issuance-policy OID object with an Active Directory group.

---

## Microsoft - msPKI-Certificate-Policy

[Microsoft - msPKI-Certificate-Policy Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-mspki-certificate-policy){ target="_blank" rel="noopener noreferrer" }

This attribute is used on certificate templates to identify certificate policy OIDs.

---

## Microsoft - msPKI-Cert-Template-OID

[Microsoft - msPKI-Cert-Template-OID Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-mspki-cert-template-oid){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Certipy can enumerate AD CS certificate authorities, certificate templates and modern ESC conditions.

Always verify the installed version before using operational syntax:

```bash
certipy --version
certipy find -h
```

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - AD CS Attack Paths in BloodHound

[SpecterOps - AD CS Attack Paths in BloodHound](https://specterops.io/blog/2024/04/25/adcs-attack-paths-in-bloodhound-part-1/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC13 demonstrates that certificate security is not limited to:

```text
Who Is Named in the Certificate?
```

or:

```text
What EKUs Does the Certificate Have?
```

Certificates can also carry information about:

```text
How the Certificate Was Issued
```

through issuance policies.

Active Directory can use those policies through Authentication Mechanism Assurance to provide additional authorisation.

The critical relationship is:

```text
Certificate Template
        |
        v
msPKI-Certificate-Policy
        |
        v
Enterprise OID
        |
        v
msPKI-Cert-Template-OID
        |
        v
msDS-OIDToGroupLink
        |
        v
Universal Security Group
```

This means an AD CS assessment should not stop after reviewing:

```text
Subject Name
SAN
EKUs
Enrollment Rights
```

It should also ask:

```text
Which issuance policies are present?

Do those policies map to groups?

What privileges do those groups have?

Who can obtain certificates containing
those policies?

Who can modify the policy objects?
```

The most important practical lesson is that:

```text
User Is Not Permanently in Group
```

does not necessarily mean:

```text
User Can Never Receive Group-Based
Authorisation
```

Authentication Mechanism Assurance can make the authentication method itself relevant to authorisation.

For penetration testers, the safest ESC13 proof is usually the complete read-only relationship:

```text
Low-Privilege Enrollment
        |
        v
Template
        |
        v
Issuance Policy
        |
        v
OID
        |
        v
Privileged Group
        |
        v
Sensitive Permission
```

Once that chain has been established, requesting a production certificate that grants the privileged authorisation is normally unnecessary.

For defenders, all:

```text
msDS-OIDToGroupLink
```

relationships should be treated as security-sensitive configuration and periodically reviewed alongside certificate templates, enrollment permissions, group nesting, ACLs and resource permissions.
