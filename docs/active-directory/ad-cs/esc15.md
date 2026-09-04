# AD CS ESC15 - Arbitrary Application Policies (EKUwu)

ESC15 is an Active Directory Certificate Services (AD CS) privilege-escalation technique associated with:

```text
CVE-2024-49019
```

The technique became widely known as:

```text
EKUwu
```

ESC15 affects vulnerable AD CS environments where certificate requests based on certain certificate templates can influence the resulting certificate's:

```text
Application Policies
```

in ways that were not intended by the template administrator.

The security significance is substantial because Application Policies determine what a certificate may be used for.

A certificate template intended for a limited purpose could potentially result in a certificate containing a more privileged application policy.

Conceptually:

```text
Low-Privilege User
        |
        v
Vulnerable Certificate Template
        |
        v
Certificate Request
        |
        v
Arbitrary Application Policy
        |
        v
Certificate with Additional Capability
        |
        v
Privilege Escalation
```

Microsoft tracks the underlying vulnerability as:

```text
CVE-2024-49019
```

and Microsoft Defender for Identity identifies the corresponding AD CS configuration as:

```text
ESC15
```

Microsoft describes vulnerable configurations as allowing an attacker to issue certificates containing arbitrary Application Policies and Subject Alternative Names, potentially leading to privilege escalation and domain compromise.

!!! danger "Patch state matters"
    ESC15 is not simply a certificate-template misconfiguration. Exploitability depends on the AD CS server being vulnerable to CVE-2024-49019. A template that historically met ESC15 prerequisites should not automatically be reported as exploitable when every issuing CA has received the relevant security update.

!!! warning "Authorised testing only"
    ESC15 can potentially transform low-privilege certificate enrollment into authentication or enrollment-agent capabilities. Begin with CA patch verification and read-only template enumeration. Do not request certificates containing privileged Application Policies for production administrative identities merely to prove impact.

---

# ESC15 at a Glance

The core ESC15 relationship is:

```text
Schema Version 1 Template
        |
        v
Low-Privilege Enrollment
        |
        v
Supply Subject Information
        |
        v
Unpatched AD CS
        |
        v
Application Policy Injection
        |
        v
More Powerful Certificate
```

The vulnerability breaks an important assumption:

```text
Template Defines Certificate Purpose
```

because under vulnerable conditions:

```text
Requester Influences Certificate Purpose
```

---

# CVE-2024-49019

CVE-2024-49019 concerns Active Directory Certificate Services.

Microsoft addressed the vulnerability through security updates released in:

```text
November 2024
```

The vulnerability relates to how AD CS processes certificate requests and Application Policies.

For modern assessments, the first question should therefore be:

```text
Is the issuing CA patched?
```

before attempting to establish an ESC15 attack path.

---

# Why ESC15 Is Different

Many AD CS escalation techniques involve:

```text
Identity
```

For example:

```text
ESC1
```

can allow control over who a certificate represents.

ESC15 instead introduces another important dimension:

```text
What is the certificate allowed to do?
```

Conceptually:

```text
Identity
   +
Certificate Purpose
   =
Authentication Capability
```

ESC15 can affect the:

```text
Certificate Purpose
```

part of this relationship.

---

# Extended Key Usage

X.509 certificates can contain an:

```text
Extended Key Usage
```

extension.

Common EKUs include:

```text
Client Authentication
Server Authentication
Code Signing
Smart Card Logon
Certificate Request Agent
```

An EKU describes the intended purposes for which a certificate can be used.

---

# Application Policies

Windows also uses:

```text
Application Policies
```

to describe certificate purposes.

Application Policies can contain OIDs representing capabilities such as:

```text
Client Authentication
Certificate Request Agent
Code Signing
```

In many normal certificate configurations, the effective Application Policies correspond closely to the EKUs defined by the certificate template.

---

# Why Application Policies Matter

Suppose a template is intended only for:

```text
Server Authentication
```

The expected certificate should not suddenly provide:

```text
Client Authentication
```

or:

```text
Certificate Request Agent
```

capabilities.

The intended security boundary is:

```text
Template
   |
   v
Approved Certificate Purpose
```

ESC15 can violate that boundary.

---

# EKU vs Application Policies

These concepts are related but should not be treated as identical.

Conceptually:

```text
Certificate Purpose
      |
      +--> Extended Key Usage
      |
      +--> Application Policies
```

Windows certificate processing can use Application Policies when determining certificate capabilities.

ESC15 specifically focuses on the ability to influence:

```text
Application Policies
```

during certificate issuance.

---

# Why "EKUwu"?

The research community nicknamed ESC15:

```text
EKUwu
```

because the technique effectively enables manipulation of certificate-purpose semantics normally associated with EKUs and Application Policies.

For reporting, however, prefer descriptive terminology such as:

```text
Arbitrary Application Policies in AD CS Certificate Requests
```

rather than relying only on the nickname.

---

# Certificate Template Schema Versions

Certificate templates have schema versions.

Common versions include:

```text
Version 1
Version 2
Version 3
Version 4
```

ESC15 is particularly associated with:

```text
Schema Version 1
```

certificate templates.

---

# Why Version 1 Matters

Version 1 certificate templates originate from older Active Directory certificate-template designs.

They have different configuration and request-processing semantics from later template versions.

The vulnerable interaction that became ESC15 involves how Application Policies can be supplied when using these templates on an unpatched CA.

---

# Template Schema Version Attribute

The template schema version can be identified through:

```text
msPKI-Template-Schema-Version
```

For ESC15, pay particular attention to:

```text
msPKI-Template-Schema-Version = 1
```

---

# Enumerate Schema Versions

PowerShell:

```powershell
Import-Module ActiveDirectory
```

Determine the Configuration naming context:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
```

Build the certificate-template container:

```powershell
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"
```

Enumerate templates and schema versions:

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties displayName,msPKI-Template-Schema-Version |
    Select-Object Name,displayName,msPKI-Template-Schema-Version
```

---

# Find Version 1 Templates

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(&(objectClass=pKICertificateTemplate)(msPKI-Template-Schema-Version=1))' -Properties displayName,msPKI-Template-Schema-Version |
    Select-Object Name,displayName,msPKI-Template-Schema-Version,DistinguishedName
```

This is a useful first read-only ESC15 discovery step.

---

# Version 1 Alone Is Not ESC15

Do not report:

```text
Schema Version 1
=
ESC15
```

A Version 1 template is only one part of the attack path.

Further conditions must be evaluated.

---

# ESC15 Core Preconditions

A useful assessment model is:

```text
Schema Version 1 Template
        +
Template Published
        +
Low-Privilege Enrollment
        +
Supply in Request
        +
No Blocking Approval Controls
        +
Unpatched Issuing CA
        =
Potential ESC15
```

Additional certificate and authentication conditions determine the final impact.

---

# Condition 1 - Schema Version 1

Check:

```text
msPKI-Template-Schema-Version
```

The classic ESC15 condition focuses on:

```text
1
```

---

# Condition 2 - Template Is Published

The certificate template must normally be available through an Enterprise CA.

Conceptually:

```text
Template
   |
   v
Published?
   |
   +--> No -> No Normal Enrollment Path
   |
   +--> Yes
```

---

# Enumerate Enterprise CAs

```powershell
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"
```

Then:

```powershell
Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties dNSHostName,certificateTemplates |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Condition 3 - Low-Privilege Enrollment

Determine who can enroll.

Potentially broad principals include:

```text
Authenticated Users
Domain Users
Domain Computers
Everyone
Large Departmental Groups
```

Broad enrollment does not automatically mean ESC15.

It becomes dangerous when combined with the remaining conditions.

---

# Template ACL Review

Retrieve a template:

```powershell
$template = Get-ADObject -SearchBase $templateBase -LDAPFilter '(cn=TargetTemplate)'
```

Inspect its ACL:

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
WriteDACL
WriteOwner
```

---

# Condition 4 - Supply in the Request

Microsoft specifically recommends disabling:

```text
Supply in the request
```

when remediating vulnerable ESC15 templates.

The relevant template name flag is associated with:

```text
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT
```

This setting allows the requester to supply subject information in the certificate request.

---

# msPKI-Certificate-Name-Flag

The relevant template attribute is:

```text
msPKI-Certificate-Name-Flag
```

Inspect it:

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(cn=TargetTemplate)' -Properties msPKI-Certificate-Name-Flag |
    Select-Object Name,msPKI-Certificate-Name-Flag
```

---

# Supply-in-Request Significance

Conceptually:

```text
Requester
   |
   v
Controls Certificate Request
   |
   +--> Subject Information
   |
   +--> SAN Information
   |
   +--> Vulnerable Application Policy Processing
```

The exact behaviour depends on CA patch state.

---

# Condition 5 - No Manager Approval

A certificate template requiring:

```text
CA Certificate Manager Approval
```

adds an administrative approval step.

This can disrupt a straightforward low-privilege ESC15 path.

Do not assume:

```text
Manager Approval Enabled
=
Impossible Forever
```

but it materially changes exploitability.

---

# Condition 6 - No Required Authorised Signatures

Templates may require authorised signatures.

If:

```text
Authorised Signatures > 0
```

the attacker needs additional prerequisites before enrollment succeeds.

Therefore this setting must be included in the assessment.

---

# Condition 7 - Vulnerable CA

This is the defining modern ESC15 condition.

The issuing CA must be vulnerable to:

```text
CVE-2024-49019
```

A template that looks vulnerable from LDAP alone is not sufficient evidence.

You must correlate:

```text
Template Configuration
```

with:

```text
Issuing CA Patch State
```

---

# Modern Assessment Rule

In a current assessment:

```text
Interesting Template
        |
        v
Which CA Publishes It?
        |
        v
Is That CA Patched?
        |
        +--> Yes -> Historical ESC15 Path Blocked
        |
        +--> No -> Investigate Further
```

This prevents false positives.

---

# Multiple CAs Matter

A template may be published by:

```text
CA01
CA02
CA03
```

If:

```text
CA01 = Patched
CA02 = Patched
CA03 = Unpatched
```

the template may still have an exploitable enrollment path through:

```text
CA03
```

Therefore assess every CA publishing the template.

---

# Patch State Is Per CA

Do not evaluate CVE-2024-49019 only at the domain level.

The important asset is:

```text
Certificate Authority Server
```

because that system processes the certificate request.

---

# Checking Windows Patch State

On an authorised CA host, basic patch inventory can be reviewed with:

```powershell
Get-HotFix |
    Sort-Object InstalledOn -Descending |
    Select-Object -First 20 HotFixID,InstalledOn,Description
```

However, cumulative Windows servicing means:

```text
Specific KB Missing
```

does not necessarily prove:

```text
System Vulnerable
```

A later cumulative update may contain the fix.

---

# Better Patch Validation

Use:

```text
Windows Version
Build Number
Installed Cumulative Update
Microsoft Security Update Guidance
```

together.

Record:

```text
CA Operating System
Build
Patch Level
Assessment Date
```

---

# Do Not Remove Patches for Testing

Never:

```text
Uninstall Security Update
```

or:

```text
Roll Back CA
```

to prove ESC15.

If the CA is patched, report the template configuration as a hardening consideration only where appropriate.

Do not report CVE-2024-49019 exploitation as currently possible.

---

# Certipy Enumeration

Certipy can identify AD CS configuration and modern ESC conditions.

Check the version first:

```bash
certipy --version
```

Then:

```bash
certipy find -h
```

A typical authorised enumeration:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review:

```text
Certificate Authorities
Certificate Templates
Schema Versions
Enrollment Rights
Subject Name Flags
Application Policies
ESC Findings
```

---

# Certipy ESC15

Modern Certipy versions can identify templates associated with ESC15 conditions.

Treat scanner output as:

```text
Candidate
```

not:

```text
Final Finding
```

Manually validate:

```text
Template Version
Published CA
Enrollment Rights
Supply in Request
Approval Controls
CA Patch State
```

---

# Certipy Vulnerability Context

A tool may identify:

```text
ESC15
```

because the directory configuration matches known prerequisites.

But LDAP enumeration alone cannot always prove the issuing Windows CA lacks the CVE-2024-49019 patch.

Therefore:

```text
Certipy Finding
       |
       v
Verify CA Patch State
       |
       v
Determine Exploitability
```

---

# LDAP Enumeration from Linux

Enumerate Version 1 templates:

```bash
ldapsearch -LLL -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(&(objectClass=pKICertificateTemplate)(msPKI-Template-Schema-Version=1))' \
    cn \
    displayName \
    msPKI-Template-Schema-Version \
    msPKI-Certificate-Name-Flag \
    pKIExtendedKeyUsage
```

---

# Enumerate Published Templates from Linux

Query Enrollment Services:

```bash
ldapsearch -LLL -x \
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

# Certificate Application Policy OID

Application Policies are represented by OIDs.

One especially important example is:

```text
Certificate Request Agent
```

OID:

```text
1.3.6.1.4.1.311.20.2.1
```

This is associated with enrollment-agent functionality.

---

# Client Authentication

A commonly important authentication EKU is:

```text
Client Authentication
```

OID:

```text
1.3.6.1.5.5.7.3.2
```

---

# Smart Card Logon

```text
Smart Card Logon
```

OID:

```text
1.3.6.1.4.1.311.20.2.2
```

---

# PKINIT Client Authentication

Another authentication-related OID is:

```text
1.3.6.1.5.2.3.4
```

associated with PKINIT client authentication.

---

# ESC15 Application-Policy Injection

The important conceptual issue is that a vulnerable CA may accept requester-controlled Application Policies that are not authorised by the certificate template.

Conceptually:

```text
Template Says:
Server Authentication
       |
       v
Request Adds:
Client Authentication
       |
       v
Vulnerable CA
       |
       v
Issued Certificate Contains
Unexpected Application Policy
```

---

# Why This Is Dangerous

The requester may transform:

```text
Limited Certificate
```

into:

```text
Authentication Certificate
```

or potentially:

```text
Enrollment Agent Certificate
```

depending on the environment and request.

This can turn an otherwise low-risk template into a privilege-escalation primitive.

---

# ESC15 Path 1 - Authentication Capability

Conceptually:

```text
Low-Privilege User
       |
       v
Vulnerable V1 Template
       |
       v
Supply Request Data
       |
       v
Add Authentication Application Policy
       |
       v
Certificate
       |
       v
Certificate Authentication
```

Additional identity-mapping requirements still apply.

---

# ESC15 Path 2 - Enrollment Agent Capability

Another important conceptual chain is:

```text
Low-Privilege User
       |
       v
Vulnerable V1 Template
       |
       v
Add Certificate Request Agent Policy
       |
       v
Enrollment Agent Certificate
       |
       v
Request Certificate on Behalf of Another Principal
```

This creates a relationship between:

```text
ESC15
```

and concepts normally associated with:

```text
ESC3
```

---

# Enrollment Agent

An Enrollment Agent certificate allows a principal to participate in:

```text
Enroll on Behalf Of
```

workflows.

Conceptually:

```text
Enrollment Agent
       |
       v
Signs Request
       |
       v
Certificate for Another User
```

This is legitimate functionality when properly restricted.

---

# ESC15 to ESC3-Like Chain

A vulnerable environment can conceptually allow:

```text
ESC15
   |
   v
Obtain Enrollment Agent Capability
   |
   v
Enrollment-on-Behalf-of Workflow
   |
   v
Authentication Certificate for Target
```

Whether this succeeds depends on the second template, enrollment-agent restrictions and CA configuration.

---

# Second Template Matters

Obtaining an Enrollment Agent certificate does not automatically grant:

```text
Certificate for Any User
```

A second template must permit the relevant enrollment-on-behalf-of workflow.

Therefore assess:

```text
Agent Template
      +
Target Template
      +
Enrollment Agent Restrictions
      +
CA Configuration
```

---

# Enrollment Agent Restrictions

Enterprise CAs can restrict:

```text
Which Enrollment Agents
```

may request:

```text
Which Templates
```

for:

```text
Which Users
```

These restrictions can materially reduce impact.

---

# ESC15 and ESC1

ESC1 generally involves:

```text
Requester-Controlled Subject/SAN
+
Authentication-Capable Template
```

ESC15 can involve:

```text
Requester-Controlled Subject/SAN
+
Requester-Controlled Application Policy
```

on a vulnerable CA.

---

# Key Difference

ESC1:

```text
Template Already Permits Authentication
```

ESC15:

```text
Requester May Be Able to Add
Authentication Capability
```

This distinction is critical.

---

# ESC15 and ESC2

ESC2 involves:

```text
Any Purpose
```

or:

```text
No EKU
```

certificate templates.

ESC15 instead abuses request processing to introduce arbitrary Application Policies.

---

# ESC15 and ESC3

ESC3 involves legitimate Enrollment Agent capability exposed through insecure template configuration.

ESC15 may allow a requester to introduce:

```text
Certificate Request Agent
```

as an Application Policy under vulnerable conditions.

---

# ESC15 and ESC4

ESC4 involves dangerous ACL permissions over a certificate template.

If an attacker can modify a template directly:

```text
ESC4
```

may already provide a path to change its security properties.

ESC15 differs because the requester may not need template-write access.

---

# ESC15 and ESC6

ESC6 concerns CA-level SAN configuration through:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

ESC15 concerns:

```text
Application Policies
```

and vulnerable request processing.

Do not merge them into one finding.

---

# ESC15 and ESC9

ESC9 concerns:

```text
No SID Security Extension
```

on a template.

ESC15 concerns:

```text
Arbitrary Application Policies
```

through CVE-2024-49019.

Both may interact with certificate authentication, but their root causes differ.

---

# ESC15 and ESC10

ESC10 concerns weak certificate mapping configuration.

ESC15 concerns certificate issuance and certificate purpose.

A certificate obtained through ESC15 still needs to be mapped to an account for authentication.

---

# ESC15 and ESC14

ESC14 concerns:

```text
altSecurityIdentities
```

explicit certificate mappings.

ESC15 concerns:

```text
Application Policy Injection
```

They can potentially form parts of the same larger certificate-authentication attack graph.

---

# ESC15 and ESC13

ESC13 involves:

```text
Issuance Policies
```

linked to Active Directory groups.

ESC15 involves:

```text
Application Policies
```

These are different certificate extensions and security concepts.

Do not confuse them.

---

# Application Policy vs Issuance Policy

A useful distinction:

```text
Application Policy
       |
       v
What May This Certificate Do?
```

versus:

```text
Issuance Policy
       |
       v
Under What Policy Was
This Certificate Issued?
```

ESC15 concerns:

```text
Application Policy
```

ESC13 concerns:

```text
Issuance Policy
```

---

# Safe Validation Strategy

For production assessments, prefer:

```text
Template Enumeration
        |
        v
Identify ESC15 Candidate
        |
        v
Identify Publishing CA
        |
        v
Verify Patch State
        |
        v
Determine Exposure
```

This usually provides sufficient evidence.

---

# Read-Only Proof

A strong read-only proof can demonstrate:

```text
Template = Version 1
Template = Published
Low-Privilege User = Enroll
Supply in Request = Enabled
Approval = Not Required
CA = Vulnerable / Unpatched
```

This is often enough to establish ESC15 exposure without requesting a malicious certificate.

---

# Do Not Inject Privileged Policies by Default

Avoid requesting production certificates containing arbitrary:

```text
Client Authentication
```

or:

```text
Certificate Request Agent
```

policies solely to prove the vulnerability.

This can create a real credential with unintended privileges.

---

# Controlled Laboratory Validation

If end-to-end proof is required:

```text
Dedicated Test CA
       |
       v
Dedicated V1 Template
       |
       v
Dedicated Test User
       |
       v
Controlled Application Policy
       |
       v
Test Certificate
```

Do not use:

```text
Administrator
Domain Admin
Enterprise Admin
Production Service Account
```

as the target.

---

# Certificate Inspection

If an authorised test certificate has been issued, inspect it.

Windows:

```cmd
certutil -dump esc15-test.cer
```

Review:

```text
Enhanced Key Usage
Application Policies
Subject
Subject Alternative Name
Certificate Template
Issuer
```

---

# OpenSSL Inspection

For PEM:

```bash
openssl x509 -in esc15-test.pem -text -noout
```

For DER:

```bash
openssl x509 -in esc15-test.cer -inform DER -text -noout
```

Remember that Microsoft-specific certificate extensions may be easier to interpret with Windows certificate tooling.

---

# Expected vs Actual Policy

The most useful evidence is:

```text
Template Expected Policy
          |
          v
Compare
          |
          v
Issued Certificate Policy
```

If the issued certificate contains capabilities not authorised by the template, that is significant.

---

# Certificate Request Archive

Where available and authorised, CA request records can help determine:

```text
What Was Requested?
```

and:

```text
What Was Issued?
```

This is useful for both assessment and incident response.

---

# Detecting ESC15

Detection should combine:

```text
CA Patch State
       +
Template Configuration
       +
Certificate Requests
       +
Issued Certificate Policies
       +
Authentication Activity
```

---

# Microsoft Defender for Identity

Microsoft Defender for Identity includes a security posture assessment named:

```text
Prevent Certificate Enrollment with arbitrary Application Policies (ESC15)
```

The assessment identifies vulnerable templates associated with unpatched AD CS servers.

---

# MDI Remediation Guidance

Microsoft's current guidance includes:

```text
Remove enrollment permission
for unprivileged users
```

and:

```text
Disable "Supply in the request"
```

and:

```text
Patch vulnerable AD CS servers
```

The CA patch is the critical CVE remediation.

---

# Certificate Services Auditing

Where Certificate Services auditing is enabled, monitor:

```text
4886
```

for certificate requests and:

```text
4887
```

for certificate issuance.

---

# Suspicious Request Pattern

A useful detection concept is:

```text
Low-Privilege Requester
       |
       v
Version 1 Template
       |
       v
Unexpected Request Attributes
       |
       v
Certificate Issued
       |
       v
Authentication / Enrollment Agent Use
```

---

# Monitor Version 1 Templates

Maintain an inventory of:

```text
Schema Version 1 Templates
```

especially those that are:

```text
Published
Broadly Enrollable
Supply in Request
```

---

# Monitor Template Publication

A previously unused template can become dangerous if an administrator suddenly publishes it.

Monitor changes to:

```text
certificateTemplates
```

on Enrollment Services objects.

---

# Monitor Template ACLs

A safe template today may become dangerous if:

```text
Enrollment Rights
```

are broadened.

Monitor changes to:

```text
nTSecurityDescriptor
```

on certificate templates.

---

# Monitor Name Flags

Changes to:

```text
msPKI-Certificate-Name-Flag
```

can affect whether requesters can supply identity information.

---

# Event 5136

With Directory Service Changes auditing enabled:

```text
5136
```

may provide visibility into modifications to certificate-template objects and related PKI configuration stored in Active Directory.

---

# Monitor CA Patch Compliance

Because ESC15 includes a software vulnerability component, configuration monitoring alone is insufficient.

Maintain:

```text
CA Asset Inventory
+
OS Version
+
Build
+
Security Update Compliance
```

---

# Hardening ESC15

The strongest mitigation is:

```text
Patch Every AD CS Server
```

affected by CVE-2024-49019.

Do not rely only on certificate-template changes.

---

# Patch All Enterprise CAs

Inventory every issuing CA:

```text
Root CA
Issuing CA
Enterprise CA
Online Subordinate CA
```

Determine whether the operating system requires the relevant security update.

---

# Offline Root CAs

An offline root CA may not process ordinary enterprise certificate requests, but it should still be maintained according to the organisation's patching and PKI lifecycle procedures.

Focus ESC15 exposure analysis on:

```text
CAs Processing Attacker-Reachable Requests
```

---

# Restrict Enrollment

Remove unnecessary enrollment permissions from:

```text
Authenticated Users
Domain Users
Domain Computers
Everyone
```

for sensitive templates.

---

# Disable Supply in the Request

Where not required:

```text
Supply in the request
```

should be disabled.

Microsoft specifically recommends this for vulnerable ESC15 template configurations.

---

# Use Modern Templates

Where operationally feasible, migrate legacy:

```text
Version 1
```

templates to modern template designs.

Do not simply duplicate a template and assume the resulting configuration is secure.

Review:

```text
Enrollment Rights
Name Flags
EKUs
Application Policies
Approval
Signatures
Validity
Private-Key Settings
```

---

# Require Approval Where Appropriate

For sensitive certificate types, consider:

```text
CA Certificate Manager Approval
```

where operationally appropriate.

This should complement patching and least-privilege enrollment.

---

# Authorised Signatures

Sensitive workflows may benefit from:

```text
Authorised Signature Requirements
```

depending on the certificate use case.

---

# Review Enrollment Agent Templates

Because ESC15 can potentially introduce:

```text
Certificate Request Agent
```

capability, review all templates and CA restrictions related to enrollment agents.

---

# Review Enrollment Agent Restrictions

Confirm that enrollment agents cannot indiscriminately request certificates:

```text
For Any User
```

using:

```text
Any Template
```

unless this is explicitly required and strongly controlled.

---

# Least Privilege

Certificate enrollment should follow:

```text
Need to Enroll
```

rather than:

```text
Convenient to Enroll
```

Broad enrollment increases the impact of future template or CA vulnerabilities.

---

# Incident Response

If ESC15 exploitation is suspected:

```text
Identify Vulnerable CA
       |
       v
Identify Vulnerable Templates
       |
       v
Identify Requests
       |
       v
Identify Issued Certificates
       |
       v
Inspect Application Policies
       |
       v
Identify Authentication / Agent Use
       |
       v
Revoke Malicious Certificates
```

---

# Determine Exposure Window

Establish:

```text
When Was CA Vulnerable?
```

and:

```text
When Was Patch Installed?
```

Then review certificate requests during that period.

---

# Identify Relevant Templates

Search for templates that were:

```text
Version 1
Published
Broadly Enrollable
Supply in Request
```

during the vulnerable period.

---

# Search CA Database

Review requests for affected templates.

Capture:

```text
Request ID
Requester
Template
Subject
SAN
Disposition
Serial Number
Request Time
Issue Time
```

---

# Inspect Suspicious Certificates

Review:

```text
Application Policies
Extended Key Usage
Subject
SAN
Requester
Template
```

Look for policies inconsistent with the intended template purpose.

---

# Enrollment Agent Investigation

If a suspicious certificate contains:

```text
Certificate Request Agent
```

determine whether it was subsequently used to request certificates on behalf of other principals.

---

# Authentication Investigation

If a suspicious certificate contains authentication capabilities, review:

```text
4768
```

and related Kerberos activity where available.

Correlate:

```text
Certificate Issuance
       |
       v
Certificate Authentication
       |
       v
Privileged Activity
```

---

# Revoke Suspicious Certificates

Where malicious certificates are identified:

```text
Revoke
   |
   v
Publish Updated CRL
   |
   v
Verify Revocation Availability
```

---

# Patch the CA

Incident containment should include applying the appropriate Microsoft security updates to affected CA servers.

Do not only revoke certificates while leaving the issuance vulnerability available.

---

# Review Template Configuration

After patching, also remediate dangerous template configuration.

For example:

```text
Remove Broad Enrollment
Disable Supply in Request
Review Legacy V1 Templates
```

This provides defence in depth.

---

# Reporting ESC15

Avoid a title containing only:

```text
ESC15
```

Prefer:

```text
Unpatched AD CS Allows Arbitrary Certificate Application Policies
```

or:

```text
Low-Privilege Users Can Request Certificates with Arbitrary Application Policies
```

or:

```text
AD CS Vulnerable to CVE-2024-49019 Through Legacy Certificate Template
```

---

# Example Finding

```text
Finding:
AD CS Allows Low-Privilege Certificate Enrollment with Arbitrary
Application Policies

CVE:
CVE-2024-49019

AD CS Technique:
ESC15

Affected CA:
CORP-CA01

Affected Template:
LegacyWebServer

Template Schema:
Version 1

Description:
The LegacyWebServer certificate template is published by CORP-CA01
and permits enrollment by low-privileged domain users.

The template is a schema version 1 template and permits requesters
to supply subject information in the certificate request.

The issuing Certificate Authority has not received the security
update addressing CVE-2024-49019.

Under this configuration, a low-privileged requester may be able to
influence Application Policies in certificates issued from the
affected template.

This could allow a certificate intended for a limited purpose to
receive additional capabilities such as authentication or
Certificate Request Agent functionality.

Impact:
Successful exploitation could enable certificate-based privilege
escalation.

Depending on the available certificate templates, certificate
mapping configuration and Enrollment Agent restrictions, the
resulting certificate could potentially be used to impersonate
higher-privileged identities and compromise sensitive Active
Directory resources.

Testing:
The finding was validated through read-only template enumeration,
enrollment-permission analysis and CA patch-state verification.

No certificate containing unauthorised Application Policies was
requested from the production CA.

Recommendation:
Apply the Microsoft security update addressing CVE-2024-49019 to
all affected AD CS servers.

Remove unnecessary enrollment permissions for low-privileged
principals.

Disable "Supply in the request" on templates where requester-defined
subject information is not required.

Review legacy schema version 1 certificate templates and migrate
them to appropriately secured modern templates where possible.

Review Enrollment Agent templates and restrictions for additional
certificate-based escalation paths.
```

---

# Patched Environment Reporting

If:

```text
Template Matches Historical ESC15 Conditions
```

but:

```text
All Publishing CAs Are Patched
```

do not report:

```text
Exploitable CVE-2024-49019
```

Instead consider whether the remaining template configuration warrants a separate hardening observation.

---

# False-Positive Avoidance

Do not determine ESC15 from:

```text
Version 1 Template
```

alone.

Do not determine ESC15 from:

```text
Supply in Request
```

alone.

Do not determine ESC15 from:

```text
Broad Enrollment
```

alone.

Do not determine ESC15 from:

```text
Certipy Label
```

alone.

Correlate the complete path.

---

# ESC15 Severity Model

Use:

```text
Unpatched CA
      +
Vulnerable Template
      +
Low-Privilege Enrollment
      +
Attacker-Controlled Request
      +
Useful Application Policy
      +
Usable Identity Path
      =
Impact
```

---

# Lower-Risk Example

```text
Version 1 Template
       |
       v
Administrators Only
       |
       v
Patched CA
```

This does not represent a practical low-privilege ESC15 path.

---

# High-Risk Example

```text
Domain Users
     |
     v
Version 1 Template
     |
     v
Supply in Request
     |
     v
Unpatched CA
     |
     v
Authentication Capability
```

This requires serious investigation.

---

# Critical Example

```text
Low-Privilege User
       |
       v
Vulnerable Template
       |
       v
Unpatched Enterprise CA
       |
       v
Arbitrary Application Policy
       |
       v
Enrollment Agent / Authentication
       |
       v
Privileged Identity
       |
       v
Domain Compromise
```

This may represent critical impact.

---

# Evidence Checklist

Record:

```text
Forest
Domain
CA Name
CA Hostname
CA Operating System
CA Build
CA Patch Level
CVE-2024-49019 Patch Status
Template Name
Template Distinguished Name
Template Schema Version
Template Publication
Publishing CAs
Enrollment Principals
Enrollment Rights
msPKI-Certificate-Name-Flag
Supply in Request
Manager Approval
Authorised Signatures
EKUs
Application Policies
Template Owner
Template ACL
Certificate Request ID
Certificate Serial Number
Certificate Subject
Certificate SAN
Issued Application Policies
Validation Method
Cleanup Result
```

Do not store private keys in normal report evidence unless explicitly required by evidence-handling procedures.

---

# ESC15 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify CA hostnames
- [ ] Identify CA operating systems
- [ ] Identify CA patch levels
- [ ] Identify published templates
- [ ] Identify Version 1 templates
- [ ] Identify broadly enrollable templates
- [ ] Identify templates using Supply in Request
- [ ] Identify manager approval
- [ ] Identify authorised signature requirements

## Template Analysis

- [ ] Record `msPKI-Template-Schema-Version`
- [ ] Confirm Version 1
- [ ] Record `msPKI-Certificate-Name-Flag`
- [ ] Confirm Supply in Request
- [ ] Review enrollment ACL
- [ ] Review template owner
- [ ] Review template DACL
- [ ] Review EKUs
- [ ] Review Application Policies
- [ ] Review publication
- [ ] Identify every publishing CA

## CA Analysis

- [ ] Identify CA operating system
- [ ] Identify Windows build
- [ ] Identify cumulative security updates
- [ ] Determine CVE-2024-49019 patch state
- [ ] Review all publishing CAs
- [ ] Do not infer vulnerability from template configuration alone
- [ ] Do not remove patches for testing

## Windows Enumeration

- [ ] Enumerate Configuration naming context
- [ ] Enumerate certificate templates
- [ ] Enumerate Version 1 templates
- [ ] Enumerate Enrollment Services
- [ ] Correlate templates with CAs
- [ ] Review template ACLs
- [ ] Review CA patch inventory

## Linux Enumeration

- [ ] Enumerate templates through LDAP
- [ ] Enumerate CAs through LDAP
- [ ] Enumerate AD CS with Certipy
- [ ] Verify Certipy version
- [ ] Review ESC15 candidates
- [ ] Confirm candidates manually
- [ ] Verify CA patch state separately

## Application Policy Analysis

- [ ] Identify intended certificate purpose
- [ ] Identify expected EKUs
- [ ] Identify expected Application Policies
- [ ] Identify authentication policies
- [ ] Identify Certificate Request Agent policy
- [ ] Distinguish Application Policies from Issuance Policies
- [ ] Determine whether added capability would create escalation

## Related Conditions

- [ ] Review ESC1
- [ ] Review ESC2
- [ ] Review ESC3
- [ ] Review ESC4
- [ ] Review ESC6
- [ ] Review ESC9
- [ ] Review ESC10
- [ ] Review ESC13
- [ ] Review ESC14
- [ ] Review Enrollment Agent restrictions
- [ ] Review certificate mapping

## Safe Validation

- [ ] Prefer read-only validation
- [ ] Confirm vulnerable template
- [ ] Confirm low-privilege enrollment
- [ ] Confirm publishing CA
- [ ] Confirm CA patch state
- [ ] Determine whether evidence is sufficient
- [ ] Avoid arbitrary privileged Application Policies in production
- [ ] Use dedicated test CA where active proof is required
- [ ] Use dedicated test user
- [ ] Use dedicated test template
- [ ] Inspect resulting test certificate
- [ ] Clean up test certificates

## Detection

- [ ] Inventory Version 1 templates
- [ ] Monitor template publication
- [ ] Monitor enrollment ACL changes
- [ ] Monitor `msPKI-Certificate-Name-Flag`
- [ ] Monitor template security descriptors
- [ ] Monitor event 5136
- [ ] Monitor certificate requests
- [ ] Monitor event 4886 where configured
- [ ] Monitor certificate issuance
- [ ] Monitor event 4887 where configured
- [ ] Inspect suspicious Application Policies
- [ ] Monitor certificate authentication
- [ ] Monitor Enrollment Agent activity
- [ ] Maintain CA patch compliance

## Hardening

- [ ] Patch CVE-2024-49019
- [ ] Patch every issuing CA
- [ ] Remove unnecessary broad enrollment
- [ ] Disable Supply in Request where unnecessary
- [ ] Review Version 1 templates
- [ ] Migrate legacy templates where appropriate
- [ ] Use least-privilege enrollment
- [ ] Consider manager approval for sensitive templates
- [ ] Consider authorised signatures
- [ ] Review Enrollment Agent restrictions
- [ ] Monitor template changes
- [ ] Maintain CA asset inventory

## Incident Response

- [ ] Identify vulnerable CAs
- [ ] Determine exposure window
- [ ] Identify vulnerable templates
- [ ] Search CA database
- [ ] Identify suspicious requests
- [ ] Identify issued certificates
- [ ] Inspect Application Policies
- [ ] Inspect SANs
- [ ] Identify Enrollment Agent certificates
- [ ] Review on-behalf-of requests
- [ ] Review certificate authentication
- [ ] Review privileged activity
- [ ] Revoke malicious certificates
- [ ] Publish updated revocation information
- [ ] Patch affected CAs
- [ ] Harden affected templates
- [ ] Determine full compromise scope

## Reporting

- [ ] Use descriptive finding title
- [ ] Include CVE-2024-49019
- [ ] Identify exact CA
- [ ] Identify exact template
- [ ] Record template schema version
- [ ] Record enrollment rights
- [ ] Record Supply in Request
- [ ] Record CA patch state
- [ ] Explain Application Policy impact
- [ ] Separate candidate from confirmed exposure
- [ ] Separate historical from current exploitability
- [ ] Avoid unnecessary active exploitation
- [ ] Provide patch and configuration remediation

---

# ESC15 Testing Model

The normal certificate model is:

```text
Certificate Template
       |
       v
Defined Certificate Purpose
       |
       v
Certificate
```

The ESC15 model is:

```text
Certificate Template
       |
       v
Vulnerable Request Processing
       |
       v
Requester-Controlled Application Policy
       |
       v
Certificate with Additional Capability
```

The authentication model is:

```text
Low-Privilege User
       |
       v
Version 1 Template
       |
       v
Unpatched CA
       |
       v
Authentication Application Policy
       |
       v
Authentication Certificate
```

The Enrollment Agent model is:

```text
Low-Privilege User
       |
       v
ESC15
       |
       v
Certificate Request Agent Policy
       |
       v
Enrollment Agent Certificate
       |
       v
On-Behalf-Of Enrollment
       |
       v
Target Certificate
```

The patch model is:

```text
Potential ESC15 Template
       |
       v
Publishing CA
       |
       v
CVE-2024-49019 Patched?
       |
       +--> Yes
       |     |
       |     v
       | Historical Exploit Path Blocked
       |
       +--> No
             |
             v
        Continue Analysis
```

The multi-CA model is:

```text
Template
   |
   +--> CA01 -> Patched
   |
   +--> CA02 -> Patched
   |
   +--> CA03 -> Unpatched
                    |
                    v
              Exposure Remains
```

The safe-testing model is:

```text
Enumerate Template
       |
       v
Identify Publishing CA
       |
       v
Verify Patch State
       |
       v
Validate Permissions
       |
       v
Evidence Sufficient?
       |
       +--> Yes -> Report
       |
       +--> No
               |
               v
         Dedicated Test CA
               |
               v
         Controlled Request
               |
               v
         Inspect Certificate
```

The detection model is:

```text
Vulnerable CA
     +
Vulnerable Template
     |
     v
Certificate Request
     |
     v
Unexpected Application Policy
     |
     v
Certificate Issuance
     |
     v
Authentication / Agent Use
```

The defensive model is:

```text
Patched CA
   +
Restricted Enrollment
   +
No Unnecessary Supply-in-Request
   +
Modern Templates
   +
Enrollment Agent Restrictions
   +
Monitoring
   =
Reduced ESC15 Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I issue myself a Domain Admin
authentication certificate?"

Ask:
"Can I establish that an unpatched
CA processes a vulnerable Version 1
template available to my principal?"
```

For defenders:

```text
Do Not Assume:
"The template only contains a harmless
EKU, so certificates from it are harmless."

Ask:
"Can the requester influence the
Application Policies that the CA places
into the resulting certificate?"
```

The complete ESC15 relationship is:

```text
Low-Privilege Enrollment
        |
        v
Schema Version 1 Template
        |
        v
Supply in Request
        |
        v
Unpatched AD CS
        |
        v
CVE-2024-49019
        |
        v
Arbitrary Application Policies
        |
        v
Certificate Capability
        |
        v
Privilege Escalation
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC1:

[AD CS ESC1](esc1.md)

ESC3:

[AD CS ESC3](esc3.md)

ESC4:

[AD CS ESC4](esc4.md)

ESC9:

[AD CS ESC9](esc9.md)

ESC10:

[AD CS ESC10](esc10.md)

ESC13:

[AD CS ESC13](esc13.md)

ESC14:

[AD CS ESC14](esc14.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs/esc16.md
```

---

# References

## Microsoft - ESC15 Security Posture Assessment

[Microsoft Defender for Identity - Certificate Security Posture Assessments](https://learn.microsoft.com/en-us/defender-for-identity/security-posture-assessments/certificates){ target="_blank" rel="noopener noreferrer" }

Microsoft Defender for Identity includes the:

```text
Prevent Certificate Enrollment with arbitrary Application Policies (ESC15)
```

assessment.

Microsoft states that the recommendation directly addresses:

```text
CVE-2024-49019
```

and identifies vulnerable certificate templates associated with unpatched AD CS servers.

Microsoft's remediation guidance includes:

```text
Remove enrollment permission for unprivileged users
Disable "Supply in the request"
Patch vulnerable AD CS servers
```

---

## Microsoft - CVE-2024-49019

[Microsoft Security Response Center - CVE-2024-49019](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-49019){ target="_blank" rel="noopener noreferrer" }

Use the Microsoft Security Response Center information together with the CA operating-system version and current cumulative update to determine whether the issuing CA is vulnerable.

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Templates

[Microsoft - Certificate Templates Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Certipy supports AD CS enumeration and modern ESC analysis.

Always verify the installed version:

```bash
certipy --version
certipy find -h
```

before relying on command syntax or vulnerability classification.

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

Certified Pre-Owned provides the foundational AD CS privilege-escalation model from which the ESC taxonomy developed.

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC15 introduced another important question into AD CS assessments.

Historically, testers commonly asked:

```text
Who Can Enroll?
```

```text
Who Can the Certificate Represent?
```

and:

```text
What EKUs Does the Template Have?
```

ESC15 adds:

```text
Can the Requester Influence the
Application Policies of the
Issued Certificate?
```

The expected security model is:

```text
Template
   |
   v
Defines Certificate Purpose
   |
   v
CA Enforces Purpose
   |
   v
Certificate
```

ESC15 breaks this model under vulnerable conditions:

```text
Template
   |
   v
Requester Influences Purpose
   |
   v
Vulnerable CA
   |
   v
More Powerful Certificate
```

The technique is especially important because a template that initially appears harmless may become security-sensitive if the requester can introduce:

```text
Client Authentication
```

or:

```text
Certificate Request Agent
```

capabilities.

However, ESC15 assessment in modern environments must always include:

```text
CA Patch State
```

CVE-2024-49019 is a patched software vulnerability.

Therefore:

```text
Vulnerable-Looking Template
```

does not automatically mean:

```text
Exploitable ESC15
```

The complete assessment should establish:

```text
Schema Version
       |
       v
Enrollment Rights
       |
       v
Supply in Request
       |
       v
Publishing CA
       |
       v
Patch State
       |
       v
Application Policy Impact
```

Microsoft currently recommends three particularly important defensive actions:

```text
Patch the AD CS server

Remove unnecessary enrollment
permissions for unprivileged users

Disable Supply in the request
where it is not required
```

For penetration testers, the safest evidence is normally:

```text
Low-Privilege Enrollment
        +
Vulnerable Template Configuration
        +
Unpatched Publishing CA
```

rather than issuing a certificate containing a privileged Application Policy.

For defenders, ESC15 is another reason AD CS should be treated as:

```text
Tier 0 Infrastructure
```

and managed through:

```text
Patch Management
Template Governance
Least-Privilege Enrollment
Configuration Monitoring
Certificate Auditing
```

The next technique to assess is:

```text
ESC16
```

which moves from a template-specific missing SID security extension to a **CA-wide configuration that can suppress the SID security extension across certificates issued by the CA**.
