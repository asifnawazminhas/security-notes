# AD CS ESC14 - Weak Explicit Certificate Mapping

ESC14 is an Active Directory Certificate Services (AD CS) attack technique involving explicit X.509 certificate mappings stored in the Active Directory attribute:

```text
altSecurityIdentities
```

The attribute can be configured on Active Directory user and computer objects to explicitly associate certificates with those principals for authentication.

The fundamental relationship is:

```text
Active Directory Principal
        |
        v
altSecurityIdentities
        |
        v
Explicit X.509 Mapping
        |
        v
Certificate
        |
        v
Authenticate as Principal
```

ESC14 becomes relevant when either:

```text
An attacker can modify altSecurityIdentities
```

or:

```text
An existing explicit certificate mapping
uses identifiers that can be reproduced
by another certificate
```

The first condition can allow an attacker to map a certificate they control directly to another account.

The second condition involves a weak existing mapping whose certificate identifiers can potentially be reproduced through another enrollment path.

ESC14 is particularly important because strong certificate binding changes introduced by Microsoft do not eliminate every explicit certificate mapping attack. Strong explicit mappings remain intentionally supported, and an attacker who has permission to write `altSecurityIdentities` may be able to create such a mapping themselves.

!!! warning "Authorised testing only"
    Modifying `altSecurityIdentities` changes how Active Directory maps certificates to identities and can create an immediate account-takeover path. During production assessments, prefer read-only enumeration of the attribute and its ACLs. Do not add certificate mappings to privileged production accounts merely to prove impact. Where end-to-end validation is required, use dedicated test accounts and remove all test mappings afterwards.

---

# Explicit Certificate Mapping

Certificate authentication requires Windows to determine:

```text
Which Active Directory account
does this certificate represent?
```

There are two broad approaches:

```text
Certificate Mapping
       |
       +--> Implicit Mapping
       |
       +--> Explicit Mapping
```

---

# Implicit Mapping

Implicit mapping derives the identity from information contained in the certificate.

Historically, examples included:

```text
UPN in SAN
DNS name in SAN
SID security extension
```

Conceptually:

```text
Certificate
    |
    v
Identity Information
    |
    v
Domain Controller
    |
    v
Locate AD Account
```

Several earlier AD CS techniques rely on manipulating this process.

---

# Explicit Mapping

Explicit mapping instead places a certificate reference directly on an Active Directory principal.

Conceptually:

```text
User Object
    |
    v
altSecurityIdentities
    |
    v
Certificate Reference
```

When a certificate matches that reference:

```text
Certificate
    |
    v
Explicit Mapping Match
    |
    v
Target User
```

---

# altSecurityIdentities

The relevant Active Directory attribute is:

```text
altSecurityIdentities
```

Microsoft describes this attribute as containing mappings for X.509 certificates or external Kerberos accounts that can be associated with an account for authentication.

ESC14 focuses on:

```text
X.509 Certificate Mappings
```

---

# Attribute Location

The attribute can exist on:

```text
User Objects
Computer Objects
```

For example:

```text
CN=Alice,
OU=Users,
DC=corp,
DC=example
```

may contain:

```text
altSecurityIdentities:
X509:<I>...<SR>...
```

---

# Multi-Valued Attribute

`altSecurityIdentities` is multi-valued.

A principal may therefore contain:

```text
Mapping 1
Mapping 2
Mapping 3
```

Each value must be reviewed individually.

---

# ESC14 Core Model

A simplified ESC14 attack path is:

```text
Attacker
   |
   v
Certificate
   |
   v
Explicit Mapping
   |
   v
Target Principal
   |
   v
Certificate Authentication
   |
   v
Target Security Context
```

---

# Two Important ESC14 Categories

ESC14 assessment should distinguish between:

```text
Writable Mapping
```

and:

```text
Existing Weak Mapping
```

These are related but technically different conditions.

---

# Category 1 - Writable altSecurityIdentities

The attacker can modify:

```text
altSecurityIdentities
```

on another user or computer.

Conceptually:

```text
Attacker
   |
   v
Write altSecurityIdentities
   |
   v
Target Account
   |
   v
Add Mapping to Attacker Certificate
   |
   v
Authenticate as Target
```

This is one of the most important ESC14 scenarios.

---

# Category 2 - Existing Weak Mapping

The target already contains an explicit mapping based on reusable certificate identifiers.

Conceptually:

```text
Target Account
     |
     v
Weak Existing Mapping
     |
     v
Reusable Identifier
     |
     v
Attacker Obtains Matching Certificate
     |
     v
Authenticate as Target
```

The attacker may not need write access to the target in this scenario.

---

# Strong and Weak Explicit Mappings

Microsoft classifies supported X.509 explicit mapping types as either:

```text
Weak
```

or:

```text
Strong
```

The distinction is extremely important when assessing ESC14.

---

# Weak Mapping Types

The weak explicit mapping formats are:

```text
X509IssuerSubject
X509SubjectOnly
X509RFC822
```

These rely on identifiers that may potentially be reused.

---

# Strong Mapping Types

The strong explicit mapping formats are:

```text
X509IssuerSerialNumber
X509SKI
X509SHA1PublicKey
```

These bind authentication to more specific certificate or key identifiers.

---

# Mapping Summary

```text
+--------------------------+-----------------------------+
| Mapping                  | Classification              |
+--------------------------+-----------------------------+
| X509IssuerSubject        | Weak                        |
| X509SubjectOnly          | Weak                        |
| X509RFC822               | Weak                        |
| X509IssuerSerialNumber   | Strong                      |
| X509SKI                  | Strong                      |
| X509SHA1PublicKey        | Strong                      |
+--------------------------+-----------------------------+
```

---

# X509IssuerSubject

Format:

```text
X509:<I>IssuerDN<S>SubjectDN
```

Conceptually:

```text
Issuer
  +
Subject
  =
Mapping
```

Example structure:

```text
X509:<I>DC=example,DC=corp,CN=CORP-CA<S>CN=Alice
```

Microsoft classifies this as:

```text
Weak
```

---

# Why IssuerSubject Is Weak

The mapping depends on:

```text
Issuer
+
Subject
```

If another certificate can be issued:

```text
by the same issuer
```

with:

```text
the same subject
```

the mapping may potentially be satisfied again.

The exact feasibility depends on certificate-template and account-control conditions.

---

# X509SubjectOnly

Format:

```text
X509:<S>SubjectDN
```

Example:

```text
X509:<S>CN=Alice
```

This is also classified as:

```text
Weak
```

because the subject name is not necessarily unique to one certificate.

---

# X509RFC822

Format:

```text
X509:<RFC822>user@corp.example
```

This mapping relies on an RFC822 email identity.

It is classified as:

```text
Weak
```

because an email-style identifier may potentially be reproduced through another certificate issuance path.

---

# X509IssuerSerialNumber

Format:

```text
X509:<I>IssuerDN<SR>SerialNumber
```

Conceptually:

```text
Issuer
   +
Certificate Serial Number
   =
Specific Certificate
```

Microsoft classifies this as:

```text
Strong
```

and recommends it as a strong explicit mapping option.

---

# X509SKI

Format:

```text
X509:<SKI>SubjectKeyIdentifier
```

The mapping references the certificate's:

```text
Subject Key Identifier
```

This is classified as:

```text
Strong
```

---

# X509SHA1PublicKey

Format:

```text
X509:<SHA1-PUKEY>PublicKeyHash
```

This mapping identifies the certificate through the hash of its public key.

Microsoft classifies this as:

```text
Strong
```

---

# Strong Does Not Mean Safe to Write

An important ESC14 distinction is:

```text
Strong Mapping
```

does not mean:

```text
Safe if an Attacker Can Configure It
```

Suppose an attacker controls a certificate.

They may add a strong mapping for that certificate to a target account:

```text
Attacker Certificate
       |
       v
Issuer + Serial
       |
       v
Target altSecurityIdentities
```

The mapping is cryptographically strong.

But it strongly maps:

```text
Attacker's Certificate
```

to:

```text
Victim Account
```

That is still dangerous.

---

# ESC14 Scenario A - Write altSecurityIdentities

This is the most direct ESC14 scenario.

The attacker has permission to modify:

```text
altSecurityIdentities
```

on the target.

The conceptual chain is:

```text
Attacker Controls Certificate
        |
        v
Write altSecurityIdentities
        |
        v
Target Account
        |
        v
Add Strong Explicit Mapping
        |
        v
Authenticate with Certificate
        |
        v
Target Account
```

This scenario can remain relevant even where strong certificate mapping is enforced.

---

# Scenario A Requirements

The attacker needs a permission path allowing modification of the target's certificate mapping.

Potential rights include:

```text
WriteProperty on altSecurityIdentities
```

and, depending on the target object's ACL and effective rights:

```text
GenericWrite
GenericAll
WriteDACL
WriteOwner
```

Other property-set rights can also matter.

Always calculate effective permissions rather than relying only on the ACE name.

---

# Public-Information Property Set

`altSecurityIdentities` has historically been associated with the:

```text
Public-Information
```

property set.

Therefore an ACE granting write access to that property set may be relevant.

This is easy to overlook when reviewing ACLs.

---

# Scenario A Certificate Requirement

The attacker also needs a certificate they control that can be used for the intended authentication path.

Conceptually:

```text
Controlled Principal
       |
       v
Certificate Enrollment
       |
       v
Attacker Holds Private Key
```

The certificate can then be explicitly mapped to the target if the attacker has the necessary write permission.

---

# Computer Certificates

Computer accounts are especially relevant because default enterprise environments often provide machine certificate enrollment through standard computer templates.

An attacker controlling a computer account or computer session may therefore already have a legitimate route to obtain a certificate for that computer.

The security question then becomes:

```text
Can that certificate be explicitly
mapped to another principal?
```

---

# Scenario A and Strong Mapping Enforcement

A critical point is:

```text
StrongCertificateBindingEnforcement
```

does not automatically prevent Scenario A.

Why?

Because the attacker can create a:

```text
Strong Explicit Mapping
```

to the certificate they already control.

Conceptually:

```text
Certificate A
    |
    v
Strong Mapping
    |
    v
Target User
```

The mapping itself tells Active Directory that the certificate represents the target.

---

# Scenario A Is Primarily an ACL Problem

The root cause is usually:

```text
Dangerous Write Access
```

to:

```text
altSecurityIdentities
```

Therefore ESC14 Scenario A should be analysed alongside:

[ACL and ACE](../acl-ace.md)

---

# ESC14 Scenario B - X509RFC822

Another scenario involves a target account with:

```text
X509RFC822
```

mapping.

Conceptually:

```text
Target
 |
 v
altSecurityIdentities
 |
 v
X509:<RFC822>target@example.com
```

If an attacker can cause a certificate they control to contain the matching RFC822 value under the required template and domain-controller conditions, the certificate may satisfy the target's explicit mapping.

---

# Scenario B Depends on Additional Conditions

This is not simply:

```text
Target Has Email Mapping
=
Immediately Vulnerable
```

The attacker needs a certificate issuance path capable of reproducing the required identifier.

Domain-controller certificate-binding configuration also matters.

Modern strong mapping enforcement significantly changes the feasibility of weak explicit mapping scenarios.

---

# ESC14 Scenario C - X509IssuerSubject

The target contains:

```text
X509IssuerSubject
```

For example:

```text
X509:<I>Issuer<S>Subject
```

An attacker may attempt to obtain a certificate from the same issuer with a matching subject.

The practical attack depends on whether the attacker can influence the certificate subject through another controlled principal or enrollment path.

---

# ESC14 Scenario D - X509SubjectOnly

The target contains:

```text
X509:<S>Subject
```

The attacker attempts to obtain a certificate containing the same subject.

Again:

```text
Weak Mapping Present
```

is only one prerequisite.

The attacker must also have a viable way to obtain the matching certificate.

---

# Weak Mapping Does Not Automatically Mean Exploitable

A useful assessment model is:

```text
Weak Mapping
     |
     v
Can Identifier Be Reproduced?
     |
     +--> No -> Hardening Issue / Limited Exposure
     |
     +--> Yes
             |
             v
     Can Certificate Authenticate?
             |
             +--> No -> Limited
             |
             +--> Yes
                     |
                     v
                Attack Path
```

---

# KB5014754

Microsoft introduced major certificate-based authentication changes through:

```text
KB5014754
```

These changes were designed to address certificate spoofing and weak certificate-to-account mapping.

The changes introduced concepts including:

```text
Strong Certificate Mapping
SID Security Extension
Full Enforcement
```

These changes materially affect several AD CS techniques, including ESC14.

---

# Modern 2026 Context

When assessing ESC14 today, do not use assumptions from an old pre-2022 lab without checking the current environment.

Supported and fully patched domain controllers are expected to use Microsoft's modern certificate-binding protections.

This particularly reduces the relevance of weak mapping paths that depended on older compatibility behaviour.

However:

```text
Writable altSecurityIdentities
```

remains important because an attacker may create a supported strong explicit mapping.

---

# StrongCertificateBindingEnforcement

The historical registry value associated with Kerberos certificate binding is:

```text
StrongCertificateBindingEnforcement
```

under:

```text
HKLM\SYSTEM\CurrentControlSet\Services\Kdc
```

Legacy environments may still warrant configuration review.

Do not assume an old registry-based compatibility configuration remains supported indefinitely.

Use current Microsoft KB5014754 guidance when evaluating a modern environment.

---

# Security Extension

Modern AD CS certificates can contain the Microsoft SID security extension used for strong implicit certificate mapping.

Conceptually:

```text
Certificate
    |
    v
SID Security Extension
    |
    v
Domain Controller
    |
    v
Specific AD Principal
```

This protects against several forms of certificate identity spoofing.

---

# Explicit Mapping Is Different

The SID extension primarily strengthens:

```text
Implicit Mapping
```

ESC14 concerns:

```text
Explicit Mapping
```

through:

```text
altSecurityIdentities
```

Therefore the presence of the SID extension does not make `altSecurityIdentities` irrelevant.

---

# Enumerate altSecurityIdentities

Using the Active Directory PowerShell module:

```powershell
Import-Module ActiveDirectory
```

Enumerate users with explicit certificate mappings:

```powershell
Get-ADUser -LDAPFilter '(altSecurityIdentities=*)' -Properties altSecurityIdentities |
    Select-Object SamAccountName,DistinguishedName,altSecurityIdentities
```

---

# Enumerate Computers

```powershell
Get-ADComputer -LDAPFilter '(altSecurityIdentities=*)' -Properties altSecurityIdentities |
    Select-Object SamAccountName,DistinguishedName,altSecurityIdentities
```

---

# Enumerate Both Object Types

A broader LDAP query can inspect both:

```powershell
Get-ADObject -LDAPFilter '(|(&(objectCategory=person)(objectClass=user))(objectClass=computer))' -Properties altSecurityIdentities |
    Where-Object { $_.altSecurityIdentities } |
    Select-Object Name,ObjectClass,DistinguishedName,altSecurityIdentities
```

---

# Find Weak Mapping Types

A simple audit can classify obvious weak mappings.

```powershell
$objects = Get-ADObject -LDAPFilter '(|(&(objectCategory=person)(objectClass=user))(objectClass=computer))' -Properties altSecurityIdentities |
    Where-Object { $_.altSecurityIdentities }

foreach ($object in $objects) {
    foreach ($mapping in $object.altSecurityIdentities) {
        $classification = switch -Regex ($mapping) {
            '^X509:<I>.*<S>'     { 'Weak - IssuerSubject'; break }
            '^X509:<S>'          { 'Weak - SubjectOnly'; break }
            '^X509:<RFC822>'     { 'Weak - RFC822'; break }
            '^X509:<I>.*<SR>'    { 'Strong - IssuerSerialNumber'; break }
            '^X509:<SKI>'        { 'Strong - SubjectKeyIdentifier'; break }
            '^X509:<SHA1-PUKEY>' { 'Strong - SHA1PublicKey'; break }
            default              { 'Review Manually' }
        }

        [PSCustomObject]@{
            Object         = $object.Name
            ObjectClass    = $object.ObjectClass
            DistinguishedName = $object.DistinguishedName
            Mapping        = $mapping
            Classification = $classification
        }
    }
}
```

This is an audit helper, not an exploitability detector.

---

# Prioritise Privileged Accounts

Start by reviewing mappings on:

```text
Domain Admins
Enterprise Admins
Tier 0 Administrators
PKI Administrators
Service Accounts
Domain Controllers
Sensitive Servers
```

But do not stop there.

A non-privileged account may have an indirect attack path.

---

# Enumerate Privileged Users

One useful starting point:

```powershell
Get-ADUser -LDAPFilter '(&(adminCount=1)(altSecurityIdentities=*))' -Properties altSecurityIdentities,adminCount |
    Select-Object SamAccountName,DistinguishedName,altSecurityIdentities
```

Remember:

```text
adminCount = 1
```

is only a useful signal.

It is not a complete list of privileged accounts.

---

# LDAP Enumeration from Linux

Users:

```bash
ldapsearch -LLL -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=person)(objectClass=user)(altSecurityIdentities=*))' \
    sAMAccountName \
    distinguishedName \
    altSecurityIdentities
```

---

# LDAP Computer Enumeration

```bash
ldapsearch -LLL -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectClass=computer)(altSecurityIdentities=*))' \
    sAMAccountName \
    dNSHostName \
    distinguishedName \
    altSecurityIdentities
```

---

# ACL Enumeration

Finding an empty `altSecurityIdentities` attribute is not enough.

The more important question may be:

```text
Who Can Write It?
```

For a target object:

```powershell
$user = Get-ADUser -Identity 'target-user'
```

Then:

```powershell
Get-Acl "AD:$($user.DistinguishedName)" |
    Format-List Owner,AccessToString
```

Review effective rights carefully.

---

# GenericWrite

If an attacker has:

```text
GenericWrite
```

over a target user, they may have the ability to modify multiple writable attributes.

`altSecurityIdentities` should be included in the analysis.

---

# GenericAll

```text
GenericAll
```

over a target object represents broad control and can expose multiple takeover techniques, potentially including ESC14.

Do not report every possible primitive separately unless that improves the report.

Focus on the clearest attack path and root cause.

---

# WriteProperty

An ACE may specifically grant:

```text
WriteProperty
```

over:

```text
altSecurityIdentities
```

This is a highly relevant ESC14 condition.

---

# Property-Set Rights

An ACE can also grant write access through a:

```text
Property Set
```

rather than naming the attribute directly.

This is why manual ACL analysis must resolve:

```text
ObjectType GUIDs
Property Sets
Inherited Rights
```

---

# WriteDACL

If an attacker has:

```text
WriteDACL
```

they may potentially grant themselves the required write access.

Conceptually:

```text
WriteDACL
    |
    v
Grant WriteProperty
    |
    v
altSecurityIdentities
```

This should generally be reported as an ACL-control path.

---

# WriteOwner

`WriteOwner` can sometimes form part of a path toward changing the object's DACL.

The exact impact depends on object type, ownership behaviour, ACL configuration and protections such as owner-rights handling.

Do not reduce the analysis to:

```text
WriteOwner = Automatic ESC14
```

---

# Public-Information Write Access

Because `altSecurityIdentities` can be associated with the Public-Information property set, audit write access to that property set.

This is less obvious than:

```text
GenericWrite
```

and may be missed by generic ACL reviews.

---

# BloodHound

BloodHound is valuable for finding:

```text
Who Can Control the Target?
```

Review relationships such as:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
```

and other object-control edges.

However, collection and edge modelling for attribute-specific `altSecurityIdentities` permissions can vary by BloodHound version.

Therefore combine BloodHound with:

```text
Native ACL Review
```

for high-confidence ESC14 analysis.

---

# PowerView

Where authorised and available, PowerView can help inspect object ACLs.

Example:

```powershell
Get-DomainObjectAcl -Identity 'target-user' -ResolveGUIDs
```

Review rights involving:

```text
altSecurityIdentities
Public-Information
GenericWrite
GenericAll
WriteDACL
WriteOwner
```

---

# Certificate Enumeration

If an existing mapping is weak, determine whether an attacker has a certificate enrollment path capable of reproducing the mapped identifier.

Start with normal AD CS enumeration:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review:

```text
Certificate Authorities
Templates
Enrollment Rights
Subject Requirements
SAN Requirements
Security Extension
Authentication EKUs
```

---

# Certipy and ESC14

Do not assume:

```bash
certipy find
```

will automatically identify every ESC14 condition.

ESC14 often requires correlation between:

```text
AD Object ACLs
altSecurityIdentities
Certificate Templates
Certificate Fields
DC Mapping Configuration
```

Manual analysis remains important.

---

# Certipy Version

Before using Certipy operationally:

```bash
certipy --version
```

Review current help:

```bash
certipy find -h
certipy req -h
certipy auth -h
```

Tool syntax changes over time.

---

# Certificate Inspection

If a certificate is part of an authorised validation, inspect it rather than guessing how it maps.

Windows:

```cmd
certutil -dump test.cer
```

Look for:

```text
Issuer
Subject
Serial Number
Subject Key Identifier
Subject Alternative Name
```

---

# OpenSSL

PEM:

```bash
openssl x509 -in test.pem -text -noout
```

DER:

```bash
openssl x509 -in test.cer -inform DER -text -noout
```

---

# Mapping Inputs

The mapping type determines which certificate fields matter.

```text
X509IssuerSubject
    -> Issuer + Subject

X509SubjectOnly
    -> Subject

X509RFC822
    -> RFC822 SAN

X509IssuerSerialNumber
    -> Issuer + Serial Number

X509SKI
    -> Subject Key Identifier

X509SHA1PublicKey
    -> Public-Key Hash
```

---

# Distinguished Name Ordering

Explicit mapping strings have formatting requirements that can differ from how certificate tools visually display distinguished names.

Do not manually construct production mappings based on assumptions about DN ordering.

Use documented Microsoft formats and controlled tooling.

---

# Serial Number Formatting

Serial-number formatting in explicit mappings is another area where representation matters.

A value copied directly from a certificate display may not necessarily be the exact string representation required by `altSecurityIdentities`.

For assessment purposes, avoid modifying production mappings merely to test formatting.

---

# Safe Scenario A Validation

The safest production proof is normally:

```text
Attacker-Controlled Principal
        |
        v
Can Obtain Authentication Certificate
        |
        v
Attacker Has Write Access
        |
        v
Target altSecurityIdentities
```

This establishes the attack prerequisites without changing the target.

---

# Lab Scenario A

For end-to-end testing, create:

```text
ESC14-Test-Victim
ESC14-Test-Target
```

Then configure an ACL allowing the victim to modify only the test target's relevant attribute.

Use a test certificate and verify the mapping behaviour.

---

# Do Not Modify a Privileged Production Account

Avoid:

```text
Administrator
Domain Admin
Enterprise Admin
krbtgt
CA Administrator
Domain Controller
```

as ESC14 proof targets.

There is normally no need.

---

# Cleanup

If a test mapping is created in a dedicated test environment, record the original attribute first.

Conceptually:

```text
Original Values
      |
      v
Test Mapping Added
      |
      v
Validation
      |
      v
Test Mapping Removed
      |
      v
Original Values Verified
```

Never use:

```text
Clear Entire Attribute
```

when legitimate mappings may already exist.

---

# Existing Mapping Validation

For a weak existing mapping, a safe validation process is:

```text
Read Mapping
    |
    v
Identify Required Certificate Fields
    |
    v
Identify Enrollment Path
    |
    v
Determine Whether Fields Are Reproducible
    |
    v
Assess DC Mapping Behaviour
```

This may be enough to report the condition.

---

# Do Not Request a Matching Privileged Certificate by Default

If:

```text
Target = Privileged Account
```

and you have already demonstrated:

```text
Weak Mapping
+
Matching Enrollment Path
```

do not request a certificate and authenticate as that account merely to make the screenshot more dramatic.

The risk is already established.

---

# ESC14 and ESC1

ESC1 can provide an attacker with control over certificate identity information.

A weak explicit mapping may therefore combine with another certificate issuance weakness.

Conceptually:

```text
Weak Explicit Mapping
       |
       v
Need Matching Certificate
       |
       v
ESC1 or Other Enrollment Weakness
       |
       v
Matching Certificate
```

Analyse the actual fields required by the mapping.

---

# ESC14 and ESC4

ESC4 can allow modification of a certificate template.

Conceptually:

```text
ESC4
 |
 v
Template Control
 |
 v
Modify Certificate Fields
 |
 v
Create Matching Certificate
 |
 v
Weak Explicit Mapping
```

This may create a combined attack path.

---

# ESC14 and ESC9

ESC9 involves certificate templates configured without the SID security extension.

This historically mattered for weak certificate mapping attacks.

In modern environments, always evaluate the current domain-controller enforcement state rather than assuming an old compatibility-mode chain remains viable.

---

# ESC14 and ESC10

ESC10 concerns weak certificate mapping configuration at the domain-controller level.

ESC14 concerns:

```text
Explicit Mapping
```

on principals.

They are related because domain-controller certificate mapping behaviour affects whether some weak ESC14 scenarios can succeed.

---

# ESC14 and Shadow Credentials

Shadow Credentials use:

```text
msDS-KeyCredentialLink
```

ESC14 uses:

```text
altSecurityIdentities
```

Both can be account-takeover primitives when an attacker has dangerous attribute-write access.

Conceptually:

```text
Target Object Control
       |
       +--> msDS-KeyCredentialLink
       |       |
       |       v
       |   Shadow Credentials
       |
       +--> altSecurityIdentities
               |
               v
             ESC14
```

See:

[Shadow Credentials](../shadow-credentials.md)

---

# ESC14 and GenericWrite

A single:

```text
GenericWrite
```

edge may expose several possible techniques.

For example:

```text
GenericWrite
    |
    +--> Attribute Modification
    |
    +--> Certificate Mapping
    |
    +--> Other Account-Takeover Paths
```

Choose the safest and clearest validation method.

---

# ESC14 and AD CS Availability

An explicit certificate mapping is only useful if the attacker can obtain or otherwise control a certificate suitable for authentication.

In many enterprise environments this is provided through AD CS.

Therefore a practical ESC14 assessment includes:

```text
Certificate Infrastructure Available?
```

and:

```text
Attacker Has Enrollment Path?
```

---

# External Certificates

Explicit mappings can also involve certificates issued outside the immediate enterprise template path, depending on trust and mapping configuration.

Therefore:

```text
No Vulnerable AD CS Template
```

does not universally mean:

```text
No Explicit Mapping Risk
```

The trusted certificate ecosystem must be understood.

---

# PKINIT

Kerberos PKINIT can use certificates for initial authentication.

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
AD Principal
    |
    v
TGT
```

ESC14 can influence the:

```text
Certificate Mapping
```

step.

---

# Schannel

Certificate authentication may also occur through:

```text
Schannel
```

for services supporting TLS client-certificate authentication.

Schannel certificate mapping configuration differs from Kerberos PKINIT.

Therefore:

```text
PKINIT Behaviour
```

and:

```text
Schannel Behaviour
```

should not automatically be treated as identical.

---

# CertificateMappingMethods

Schannel has historically used:

```text
CertificateMappingMethods
```

configuration.

The exact mapping behaviour depends on Windows version, current patch state and configured mapping methods.

Use current Microsoft documentation when evaluating Schannel-specific ESC14 behaviour.

---

# Authentication Testing

If authorised testing requires certificate authentication, first inspect the installed Certipy version:

```bash
certipy auth -h
```

Use only certificates and accounts approved for the test.

The objective is to validate:

```text
Certificate
    |
    v
Maps to Expected Test Account
```

not to compromise a production privileged identity.

---

# Detecting ESC14

Detection should focus on:

```text
altSecurityIdentities Changes
        +
Certificate Enrollment
        +
Certificate Authentication
        +
Target Privilege
```

---

# Event 5136

With Directory Service Changes auditing enabled:

```text
5136
```

can provide visibility into Active Directory attribute modifications.

Monitor changes where:

```text
AttributeLDAPDisplayName
```

or equivalent event information identifies:

```text
altSecurityIdentities
```

---

# Suspicious Sequence

A particularly useful correlation is:

```text
Certificate Enrollment
       |
       v
altSecurityIdentities Modified
       |
       v
Certificate Authentication
       |
       v
Privileged Activity
```

The closer these events occur together, the more interesting the sequence becomes.

---

# Monitor Privileged Accounts

Changes to:

```text
altSecurityIdentities
```

on privileged users and computers should receive high-priority monitoring.

Examples include:

```text
Tier 0 Users
Domain Controllers
CA Servers
Identity Servers
Privileged Service Accounts
```

---

# Baseline Existing Mappings

Before alerting effectively, defenders should know:

```text
Which accounts legitimately use
explicit certificate mappings?
```

Build an inventory containing:

```text
Account
Object Type
Mapping Type
Mapping Value
Business Purpose
Certificate Owner
Expiration
Responsible Team
```

---

# Alert on New Mappings

For accounts that normally have:

```text
altSecurityIdentities = Empty
```

a new value can be highly significant.

---

# Alert on Mapping Replacement

An attacker may:

```text
Remove Legitimate Mapping
```

and:

```text
Add Malicious Mapping
```

Therefore monitor:

```text
Add
Delete
Replace
```

operations.

---

# Certificate Enrollment Events

Where Certificate Services auditing is enabled, monitor events such as:

```text
4886
4887
```

for certificate requests and issuance.

Correlate them with target-account changes.

---

# Kerberos Authentication

Certificate-based Kerberos authentication can contribute to:

```text
4768
```

telemetry.

Modern domain controllers can expose certificate-related information useful for investigations depending on version and audit configuration.

---

# Do Not Expect an "ESC14" Event

Windows does not generate an event saying:

```text
ESC14 Attack Detected
```

Detection requires correlation.

---

# ACL Monitoring

Monitor changes to ACLs on sensitive principals.

A dangerous sequence may be:

```text
DACL Modified
      |
      v
Write altSecurityIdentities Granted
      |
      v
Mapping Added
```

---

# Event 5136 for ACL Changes

Changes to:

```text
nTSecurityDescriptor
```

may also appear through Directory Service Changes auditing depending on configuration.

Correlate object ACL modifications with subsequent attribute changes.

---

# Detect Weak Existing Mappings

Detection is not only about changes.

Periodically search for:

```text
X509IssuerSubject
X509SubjectOnly
X509RFC822
```

in:

```text
altSecurityIdentities
```

These should be reviewed and migrated where still present.

---

# Modern Migration

Microsoft's certificate-binding changes make legacy weak mappings increasingly inappropriate.

Organisations should migrate required explicit mappings to supported strong mapping types and remove mappings that are no longer required.

---

# Hardening ESC14

The defensive model is:

```text
Strong Explicit Mappings
        +
Restricted Attribute Write Access
        +
Modern DC Certificate Binding
        +
Secure Certificate Enrollment
        +
Monitoring
        =
Reduced ESC14 Risk
```

---

# Remove Unnecessary Mappings

If an account no longer requires:

```text
altSecurityIdentities
```

remove the mapping through normal identity-management change control.

Unused mappings create unnecessary authentication paths.

---

# Replace Weak Mappings

Where explicit mapping is still required, migrate away from:

```text
X509IssuerSubject
X509SubjectOnly
X509RFC822
```

toward Microsoft-supported strong mappings.

---

# Preferred Strong Mapping

Microsoft identifies:

```text
X509IssuerSerialNumber
```

as a recommended strong explicit mapping format.

Other strong formats include:

```text
X509SKI
X509SHA1PublicKey
```

Choose the format appropriate to the organisation's certificate lifecycle.

---

# Certificate Renewal

Strong mapping introduces lifecycle considerations.

If a mapping identifies:

```text
One Specific Certificate
```

certificate renewal may require the mapping to be updated.

Document this process.

---

# Do Not Solve Lifecycle Problems with Weak Mapping

Avoid retaining:

```text
SubjectOnly
```

simply because it survives certificate renewal more conveniently.

Operational convenience should not undermine authentication binding.

---

# Restrict Attribute Write Access

Review who can modify:

```text
altSecurityIdentities
```

for all sensitive principals.

Restrict access to explicitly authorised identity or PKI administration processes.

---

# Review Public-Information Rights

Do not review only:

```text
GenericWrite
```

and:

```text
GenericAll
```

Also review property-set permissions that may indirectly grant write access to `altSecurityIdentities`.

---

# Review Delegated Administration

Helpdesk, IAM and application-management groups may have delegated rights over user objects.

Determine whether those delegations unintentionally expose:

```text
altSecurityIdentities
```

---

# Review OU Inheritance

A dangerous ACE may originate from an OU.

Conceptually:

```text
OU ACL
 |
 v
Inherited by User
 |
 v
Write altSecurityIdentities
```

Therefore inspect:

```text
Parent OU ACLs
Inheritance
Protected Objects
```

---

# AdminSDHolder

Privileged accounts protected through AdminSDHolder have different ACL behaviour.

Do not assume an OU delegation applies identically to protected administrative accounts.

Still review the effective ACL directly.

---

# Certificate Template Security

Secure certificate templates so attackers cannot easily obtain certificates containing attacker-controlled identity information.

ESC14 should be assessed together with the rest of the AD CS configuration.

---

# Strong Certificate Binding

Keep domain controllers fully patched and aligned with current Microsoft certificate-binding requirements.

Do not deliberately weaken mapping enforcement to preserve old certificate deployments.

Instead:

```text
Fix the Certificate Mapping
```

---

# Inventory Legacy Applications

Legacy applications may depend on weak certificate mappings.

Before remediation:

```text
Identify Application
Identify Mapping
Identify Certificate
Identify Owner
Plan Migration
```

This prevents unexpected authentication outages.

---

# Incident Response

If malicious ESC14 activity is suspected:

```text
Identify Mapping Change
      |
      v
Identify Certificate
      |
      v
Identify Actor
      |
      v
Determine Authentication Use
      |
      v
Remove Malicious Mapping
      |
      v
Revoke Certificate
      |
      v
Investigate Target Account
```

---

# Preserve the Original Attribute

Before remediation, record:

```text
Target DN
altSecurityIdentities Values
Modification Time
ACL
Owner
```

This preserves evidence.

---

# Identify Who Changed It

Investigate:

```text
5136
Directory Service Logs
EDR
PowerShell Logs
LDAP Activity
Administrative Sessions
```

where available.

Determine:

```text
Account
Source Host
Time
Operation
```

---

# Identify the Mapped Certificate

For strong mappings, information such as:

```text
Issuer
Serial Number
SKI
Public-Key Hash
```

can help identify the specific certificate involved.

---

# Search CA Records

If the certificate came from enterprise AD CS, search the CA database for matching:

```text
Serial Number
Requester
Template
Subject
Request ID
```

---

# Revoke Malicious Certificates

If an unauthorised certificate was issued:

```text
Revoke Certificate
        |
        v
Publish Updated CRL
        |
        v
Verify Distribution
```

Certificate revocation should accompany removal of the malicious mapping where appropriate.

---

# Remove Only the Malicious Value

Because `altSecurityIdentities` is multi-valued:

```text
Do Not Blindly Clear the Attribute
```

Preserve legitimate mappings.

Remove only confirmed unauthorised values unless incident-response scope requires otherwise.

---

# Review Target Activity

Assume that successful ESC14 authentication may have given the attacker the target account's effective privileges.

Investigate:

```text
Kerberos Tickets
Interactive Logons
Remote Management
LDAP Changes
Group Changes
Credential Access
Lateral Movement
Persistence
```

---

# Review Other Objects

If an attacker gained rights capable of modifying:

```text
altSecurityIdentities
```

on one account, determine whether the same ACL delegation applies to:

```text
Other Users
Other Computers
Entire OU
Privileged Accounts
```

---

# Reporting ESC14

Avoid a title containing only:

```text
ESC14
```

Use the actual root cause.

Examples:

```text
Low-Privilege Users Can Modify Explicit Certificate Mappings
```

```text
Weak Explicit Certificate Mapping Allows Account Impersonation
```

```text
Delegated Active Directory Permissions Allow Modification of altSecurityIdentities
```

---

# Example Finding - Writable Mapping

```text
Finding:
Delegated Permissions Allow Modification of Explicit Certificate
Mappings

Affected Object:
CORP\TargetUser

Attribute:
altSecurityIdentities

Description:
The testing account has effective write access to the
altSecurityIdentities attribute of the affected Active Directory
user.

This attribute controls explicit X.509 certificate mappings for the
account.

An attacker with this permission and access to a suitable
authentication certificate may be able to add a strong explicit
mapping referencing a certificate under their control.

The certificate could then be mapped to the target identity during
certificate-based authentication.

The affected account was not modified during testing.

Impact:
Successful abuse could allow an attacker to authenticate as the
affected account without knowing its password.

The resulting impact is equivalent to the privileges available to
the target account and may persist independently of password changes
until the malicious certificate mapping is removed or the associated
certificate becomes unusable.

Recommendation:
Remove unnecessary write permissions over altSecurityIdentities.

Review GenericWrite, GenericAll, WriteProperty, WriteDACL,
WriteOwner and property-set delegations affecting the account.

Restrict explicit certificate mapping administration to authorised
identity-management or PKI administrators.

Monitor changes to altSecurityIdentities and investigate unexpected
certificate authentication involving sensitive accounts.
```

---

# Example Finding - Weak Mapping

```text
Finding:
Weak Explicit Certificate Mapping Configured on Sensitive Account

Affected Account:
CORP\LegacyService

Mapping Type:
X509SubjectOnly

Description:
The affected account uses an explicit X.509 certificate mapping in
the altSecurityIdentities attribute.

The mapping uses X509SubjectOnly, which Microsoft classifies as a
weak explicit certificate mapping because the identifier is not
bound to a unique certificate.

If another certificate trusted for authentication can be obtained
with the same mapped identifier and the domain controller accepts
the weak mapping under the environment's current certificate
mapping configuration, the certificate may map to the affected
account.

Impact:
The practical impact depends on whether the mapped certificate
identifier can be reproduced through an available certificate
issuance path and whether the current domain-controller
configuration permits the mapping.

No matching certificate was requested for the production account
during testing.

Recommendation:
Determine whether the explicit mapping is still required.

Where explicit mapping remains necessary, migrate the account to a
Microsoft-supported strong mapping such as
X509IssuerSerialNumber, X509SKI or X509SHA1PublicKey as appropriate
for the certificate lifecycle.

Keep domain controllers fully patched and aligned with current
Microsoft certificate-binding requirements.
```

---

# Persistence Consideration

An explicit certificate mapping can survive:

```text
Password Reset
```

because the authentication path is:

```text
Certificate
    |
    v
altSecurityIdentities
    |
    v
Account
```

rather than:

```text
Password
```

Therefore ESC14 can function as a persistence mechanism when an attacker can add mappings.

---

# Password Reset Is Not Enough

If malicious mapping is suspected:

```text
Reset Password
```

alone is insufficient.

Also investigate:

```text
altSecurityIdentities
Certificates
Certificate Revocation
Related ACLs
Authentication Logs
```

---

# Computer Accounts

Do not restrict ESC14 auditing to users.

Computer objects can also contain:

```text
altSecurityIdentities
```

and may represent high-value targets.

Examples:

```text
Domain Controllers
Certificate Authorities
Management Servers
Backup Servers
Application Servers
```

---

# Domain Controller Target

A mapping weakness involving a domain-controller computer account should be treated as extremely sensitive.

Do not perform end-to-end impersonation against a production DC solely to prove impact.

---

# Service Accounts

Service accounts can also be valuable ESC14 targets because they may have:

```text
SPNs
Delegated Rights
Application Privileges
Database Access
Local Administrator Rights
Tier 0 Access
```

---

# Evidence Checklist

Record:

```text
Domain
Domain Controller
Target Object
Target Object Type
Target Distinguished Name
Target SID
Target Privilege
altSecurityIdentities Values
Mapping Type
Weak / Strong Classification
Object Owner
Object ACL
Attribute-Specific Write Rights
Property-Set Rights
Inherited Rights
Attacker Group Membership
Certificate Infrastructure
Available Certificate Templates
Enrollment Rights
Certificate Authentication EKUs
Certificate Issuer
Certificate Subject
Certificate Serial Number
Certificate SKI
Certificate Public-Key Mapping Data
Domain Controller Patch State
Certificate Mapping Enforcement
Authentication Protocol
Validation Method
Cleanup Result
```

Do not include unnecessary private-key material in the report.

---

# ESC14 Assessment Checklist

## Discovery

- [ ] Identify enterprise CAs
- [ ] Identify certificate enrollment paths
- [ ] Enumerate users with `altSecurityIdentities`
- [ ] Enumerate computers with `altSecurityIdentities`
- [ ] Identify privileged mapped accounts
- [ ] Identify service accounts
- [ ] Identify mapped domain controllers
- [ ] Identify legacy explicit mappings

## Mapping Classification

- [ ] Identify `X509IssuerSubject`
- [ ] Identify `X509SubjectOnly`
- [ ] Identify `X509RFC822`
- [ ] Identify `X509IssuerSerialNumber`
- [ ] Identify `X509SKI`
- [ ] Identify `X509SHA1PublicKey`
- [ ] Classify weak mappings
- [ ] Classify strong mappings
- [ ] Review unknown mapping formats manually

## ACL Analysis

- [ ] Review target owner
- [ ] Review `GenericAll`
- [ ] Review `GenericWrite`
- [ ] Review `WriteProperty`
- [ ] Review `WriteDACL`
- [ ] Review `WriteOwner`
- [ ] Review attribute-specific rights
- [ ] Review Public-Information property-set rights
- [ ] Review inherited ACEs
- [ ] Review OU delegations
- [ ] Review nested attacker groups
- [ ] Calculate effective permissions

## Certificate Analysis

- [ ] Identify certificate templates
- [ ] Identify enrollment rights
- [ ] Identify authentication EKUs
- [ ] Review subject requirements
- [ ] Review SAN requirements
- [ ] Review SID security extension
- [ ] Identify issuer
- [ ] Identify subject
- [ ] Identify serial number
- [ ] Identify SKI
- [ ] Identify RFC822 SAN where relevant
- [ ] Determine whether weak identifiers can be reproduced

## Modern Mapping Review

- [ ] Review KB5014754
- [ ] Verify current DC patch state
- [ ] Verify certificate-binding enforcement
- [ ] Distinguish implicit mapping from explicit mapping
- [ ] Identify legacy compatibility assumptions
- [ ] Do not assume pre-2022 behaviour
- [ ] Determine whether weak mapping is still accepted
- [ ] Remember strong explicit mapping remains relevant to writable-attribute attacks

## Windows Enumeration

- [ ] Query users
- [ ] Query computers
- [ ] Query privileged users
- [ ] Inspect object ACLs
- [ ] Resolve property GUIDs
- [ ] Review OU inheritance
- [ ] Inspect authorised test certificates

## Linux Enumeration

- [ ] Query users through LDAP
- [ ] Query computers through LDAP
- [ ] Enumerate AD CS with Certipy
- [ ] Verify Certipy version
- [ ] Review certificate templates
- [ ] Correlate enrollment paths
- [ ] Perform manual mapping analysis

## BloodHound

- [ ] Identify control over target
- [ ] Review `GenericWrite`
- [ ] Review `GenericAll`
- [ ] Review `WriteDACL`
- [ ] Review `WriteOwner`
- [ ] Review indirect paths
- [ ] Confirm attribute-specific rights separately where necessary
- [ ] Review target privileges

## Safe Validation

- [ ] Prefer read-only validation
- [ ] Identify controlled certificate path
- [ ] Identify write access
- [ ] Determine whether prerequisites establish impact
- [ ] Avoid modifying privileged accounts
- [ ] Use dedicated test identities
- [ ] Record original mappings
- [ ] Add only controlled test mapping if required
- [ ] Authenticate only as test target
- [ ] Remove test mapping
- [ ] Verify original state
- [ ] Revoke test certificate where appropriate

## Detection

- [ ] Monitor `altSecurityIdentities`
- [ ] Monitor event 5136
- [ ] Monitor privileged account changes
- [ ] Monitor computer-account mappings
- [ ] Monitor ACL changes
- [ ] Monitor certificate enrollment
- [ ] Monitor CA events 4886/4887 where configured
- [ ] Monitor certificate authentication
- [ ] Correlate mapping changes with authentication
- [ ] Baseline legitimate explicit mappings
- [ ] Alert on new mappings
- [ ] Alert on mapping deletion/replacement
- [ ] Periodically scan for weak mappings

## Hardening

- [ ] Remove unused mappings
- [ ] Replace weak mappings
- [ ] Use strong mappings where required
- [ ] Review certificate-renewal lifecycle
- [ ] Restrict `altSecurityIdentities` writes
- [ ] Review Public-Information property-set delegation
- [ ] Review OU ACL inheritance
- [ ] Review helpdesk delegation
- [ ] Review IAM delegation
- [ ] Secure certificate templates
- [ ] Keep DCs fully patched
- [ ] Follow current Microsoft certificate-binding guidance
- [ ] Remove obsolete compatibility configurations
- [ ] Document explicit mapping ownership

## Incident Response

- [ ] Preserve original mapping values
- [ ] Identify mapping change
- [ ] Identify actor
- [ ] Identify source host
- [ ] Identify mapped certificate
- [ ] Search CA database
- [ ] Review certificate issuance
- [ ] Review certificate authentication
- [ ] Review target-account activity
- [ ] Remove malicious mapping
- [ ] Revoke malicious certificate
- [ ] Publish updated revocation data where required
- [ ] Review related object ACLs
- [ ] Review similarly delegated objects
- [ ] Reset credentials where appropriate
- [ ] Remember password reset alone is insufficient

## Reporting

- [ ] Use descriptive title
- [ ] Identify affected object
- [ ] Identify exact mapping type
- [ ] Identify weak or strong classification
- [ ] Identify dangerous write permission
- [ ] Explain certificate enrollment prerequisite
- [ ] Explain current mapping enforcement
- [ ] Explain actual target privilege
- [ ] Separate theoretical and demonstrated impact
- [ ] Avoid exposing private keys
- [ ] Provide specific remediation

---

# ESC14 Testing Model

The explicit mapping model is:

```text
Active Directory Principal
        |
        v
altSecurityIdentities
        |
        v
Certificate Mapping
        |
        v
Certificate Authentication
```

The weak-mapping model is:

```text
Target
  |
  v
Weak Explicit Mapping
  |
  v
Reusable Certificate Identifier
  |
  v
Matching Certificate
  |
  v
Target Authentication
```

The writable-mapping model is:

```text
Attacker
   |
   v
Write altSecurityIdentities
   |
   v
Target
   |
   v
Strong Mapping to Attacker Certificate
   |
   v
Authenticate as Target
```

The ACL relationship is:

```text
Object ACL
   |
   +--> GenericWrite
   |
   +--> GenericAll
   |
   +--> WriteProperty
   |
   +--> Property Set
   |
   +--> WriteDACL
   |
   +--> WriteOwner
           |
           v
altSecurityIdentities Control
```

The certificate relationship is:

```text
Certificate
   |
   +--> Issuer
   |
   +--> Subject
   |
   +--> RFC822
   |
   +--> Serial Number
   |
   +--> SKI
   |
   +--> Public Key
           |
           v
Explicit Mapping
```

The strong-versus-weak model is:

```text
Explicit Mapping
      |
      +--> Weak
      |     |
      |     +--> IssuerSubject
      |     +--> SubjectOnly
      |     +--> RFC822
      |
      +--> Strong
            |
            +--> IssuerSerialNumber
            +--> SKI
            +--> SHA1PublicKey
```

The modern mapping model is:

```text
Certificate Authentication
       |
       +--> Implicit Mapping
       |       |
       |       v
       |   Strong Binding / SID
       |
       +--> Explicit Mapping
               |
               v
        altSecurityIdentities
```

The Scenario A model is:

```text
Controlled Certificate
       |
       v
Write Target Attribute
       |
       v
Strong Explicit Mapping
       |
       v
Target Authentication
```

The existing weak-mapping model is:

```text
Weak Mapping
    |
    v
Identify Required Field
    |
    v
Find Certificate Enrollment Path
    |
    v
Can Field Be Reproduced?
    |
    +--> No -> Limited Exposure
    |
    +--> Yes
            |
            v
      Mapping Accepted?
            |
            +--> No -> Blocked
            |
            +--> Yes -> Attack Path
```

The safe-testing model is:

```text
Enumerate Mapping
      |
      v
Review ACL
      |
      v
Review Certificate Path
      |
      v
Review DC Mapping Behaviour
      |
      v
Evidence Sufficient?
      |
      +--> Yes -> Report
      |
      +--> No
              |
              v
        Dedicated Test Account
              |
              v
        Controlled Mapping
              |
              v
        Controlled Authentication
              |
              v
             Cleanup
```

The detection model is:

```text
Certificate Enrollment
       |
       v
altSecurityIdentities Change
       |
       v
Certificate Authentication
       |
       v
Target Privilege Use
```

The persistence model is:

```text
Attacker Certificate
       |
       v
altSecurityIdentities
       |
       v
Target Account
       |
       +--> Password Changed
       |
       +--> Mapping Remains
               |
               v
        Certificate Authentication
```

The defensive model is:

```text
Strong Mappings
      +
Restricted Attribute ACLs
      +
Secure Enrollment
      +
Modern DC Binding
      +
Monitoring
      =
Reduced ESC14 Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I add my certificate to the
Domain Administrator account?"

Ask:
"Can I prove that my principal has
effective write access to the
certificate-mapping attribute and
that I control a suitable certificate?"
```

For defenders:

```text
Do Not Assume:
"Strong certificate binding means
altSecurityIdentities cannot be abused."

Ask:
"Who can create or modify explicit
certificate mappings on our users
and computers?"
```

The complete ESC14 relationship is:

```text
Active Directory ACL
       |
       v
altSecurityIdentities
       |
       v
Explicit Certificate Mapping
       |
       v
Certificate
       |
       v
PKINIT / Schannel
       |
       v
Target Identity
       |
       v
Target Privilege
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC9:

[AD CS ESC9](esc9.md)

ESC10:

[AD CS ESC10](esc10.md)

ESC13:

[AD CS ESC13](esc13.md)

Shadow Credentials:

[Shadow Credentials](../shadow-credentials.md)

ACLs and ACEs:

[ACL and ACE](../acl-ace.md)

Certificate Templates:

[AD CS Enumeration](enumeration.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs/esc15.md
```

---

# References

## Microsoft - KB5014754

[Microsoft - KB5014754 Certificate-Based Authentication Changes on Windows Domain Controllers](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

Microsoft documents the modern certificate-binding changes and explicitly classifies the six supported `altSecurityIdentities` X.509 mapping types as weak or strong.

The three weak types are:

```text
X509IssuerSubject
X509SubjectOnly
X509RFC822
```

The three strong types are:

```text
X509IssuerSerialNumber
X509SKI
X509SHA1PublicKey
```

---

## Microsoft - altSecurityIdentities

[Microsoft - altSecurityIdentities Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-altsecurityidentities){ target="_blank" rel="noopener noreferrer" }

Microsoft documents the Active Directory attribute used for alternative security identities.

---

## SpecterOps - ESC14

[SpecterOps - ADCS ESC14 Abuse Technique](https://specterops.io/blog/2024/02/28/adcs-esc14-abuse-technique/){ target="_blank" rel="noopener noreferrer" }

SpecterOps provides detailed research into ESC14, including writable `altSecurityIdentities`, weak existing mappings, certificate-template prerequisites, PKINIT, Schannel, ACL requirements and defensive guidance.

---

## SpecterOps - Certificates and Pwnage and Patches, Oh My!

[SpecterOps - Certificates and Pwnage and Patches, Oh My!](https://specterops.io/blog/2022/11/09/certificates-and-pwnage-and-patches-oh-my/){ target="_blank" rel="noopener noreferrer" }

This research explains the certificate-binding changes introduced by KB5014754 and the distinction between strong and weak certificate mappings.

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Certipy is useful for AD CS enumeration, certificate requests and controlled certificate-authentication validation.

Always check the installed version:

```bash
certipy --version
```

and current command help before operational use.

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC14 demonstrates an important difference between:

```text
Certificate Trust
```

and:

```text
Certificate-to-Account Mapping
```

A certificate can be completely legitimate:

```text
Valid Signature
Valid Trust Chain
Valid Private Key
Valid Authentication EKU
```

while still being mapped to the wrong Active Directory principal because of an unsafe explicit mapping.

The core object is:

```text
altSecurityIdentities
```

and every Active Directory security assessment involving certificate authentication should answer two questions:

```text
Which accounts have explicit
certificate mappings?
```

and:

```text
Who can modify those mappings?
```

The first identifies:

```text
Existing Mapping Risk
```

while the second identifies:

```text
Account Takeover Risk
```

Microsoft's modern certificate-binding protections make the distinction between weak and strong explicit mappings particularly important.

Weak mappings are:

```text
X509IssuerSubject
X509SubjectOnly
X509RFC822
```

Strong mappings are:

```text
X509IssuerSerialNumber
X509SKI
X509SHA1PublicKey
```

However, the most important ESC14 lesson is that:

```text
Strong Mapping
```

does not protect an account when:

```text
Attacker Can Write the Mapping
```

An attacker who controls both:

```text
Certificate
```

and:

```text
Target altSecurityIdentities
```

may be able to deliberately create a strong mapping between them.

Therefore:

```text
Strong Certificate Binding
```

must be combined with:

```text
Strong Active Directory ACLs
```

The practical assessment model is:

```text
Enumerate altSecurityIdentities
        |
        v
Classify Mapping
        |
        v
Review Target ACL
        |
        v
Review Certificate Enrollment
        |
        v
Review Current DC Mapping Behaviour
        |
        v
Determine Real Attack Path
```

For weak existing mappings, do not automatically report critical exploitation.

Determine whether:

```text
Mapped Identifier
       |
       v
Can Actually Be Reproduced
       |
       v
Through Available Certificate Enrollment
       |
       v
Under Current DC Enforcement
```

For writable mappings, focus on the ACL root cause.

A read-only proof showing:

```text
Attacker
   |
   v
Effective Write Access
   |
   v
altSecurityIdentities
   |
   v
Sensitive Target
```

combined with a legitimate attacker-controlled authentication certificate can often establish the risk without changing the production target.

Finally, ESC14 should be considered alongside:

```text
Shadow Credentials
ACL Abuse
Certificate Template Abuse
Weak Certificate Mapping
Certificate Authentication
```

because all of these mechanisms can converge on the same security objective:

```text
Control Authentication Mapping
          |
          v
Control Identity
```
