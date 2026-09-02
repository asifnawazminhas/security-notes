# AD CS ESC7 - Vulnerable Certification Authority Permissions

ESC7 is an Active Directory Certificate Services (AD CS) privilege escalation condition involving excessive administrative permissions on a Certification Authority (CA).

The two permissions most commonly associated with ESC7 are:

```text
ManageCA
ManageCertificates
```

These permissions are significantly different from ordinary certificate enrollment rights.

They provide administrative control over the CA or its certificate requests.

A simplified ESC7 relationship is:

```text
Low-Privileged Principal
        |
        v
Dangerous CA Permission
        |
        +--> ManageCA
        |
        +--> ManageCertificates
        |
        v
Certification Authority
        |
        v
Administrative CA Actions
        |
        v
Certificate Abuse
        |
        v
Potential Privilege Escalation
```

The key assessment question is:

```text
Can a principal that should not administer
the Certification Authority perform privileged
CA management operations?
```

!!! warning "Authorised testing only"
    CA administrative permissions can affect certificate issuance and authentication across an Active Directory environment. Begin with read-only enumeration. Do not change CA configuration, enable certificate templates, approve production certificate requests, alter CA security descriptors, or restart Certificate Services merely to demonstrate ESC7. Where active validation is required, use dedicated test identities and obtain explicit approval for the specific CA operation.

---

# ESC7 Concept

AD CS separates several types of access.

For example:

```text
Certificate Enrollment
        |
        v
Request Certificate
```

is different from:

```text
CA Administration
        |
        v
Manage CA
```

and:

```text
Certificate Management
        |
        v
Manage Certificate Requests
```

ESC7 concerns the latter administrative capabilities.

---

# Certification Authority Permissions

Important CA permissions include:

```text
Read
Issue and Manage Certificates
Manage CA
Request Certificates
```

The exact names shown by tools may vary.

For ESC7, the most important permissions are commonly represented as:

```text
ManageCA
ManageCertificates
```

---

# ManageCA

`ManageCA` represents CA administrative control.

Conceptually:

```text
Principal
   |
   v
ManageCA
   |
   v
CA Configuration
```

Depending on the CA configuration and the principal's effective rights, this can expose security-sensitive administrative operations.

---

# ManageCertificates

`ManageCertificates` is commonly associated with:

```text
Issue and Manage Certificates
```

Conceptually:

```text
Principal
   |
   v
ManageCertificates
   |
   v
Certificate Requests
   |
   v
Issue / Deny / Manage
```

This can become particularly dangerous when combined with other CA or template conditions.

---

# ESC7 Is About Effective Permissions

Do not assess only direct user permissions.

The effective path may be:

```text
User
 |
 v
Group
 |
 v
Nested Group
 |
 v
ManageCA
```

or:

```text
User
 |
 v
Group
 |
 v
ManageCertificates
```

Therefore always resolve:

```text
Direct Permissions
Group Membership
Nested Groups
Inherited Administrative Roles
```

---

# ESC7 vs Enrollment Rights

A principal that can:

```text
Enroll
```

does not necessarily have ESC7.

Enrollment means:

```text
Request a Certificate
```

ESC7 concerns:

```text
Administer the CA
```

or:

```text
Manage Certificate Requests
```

These are different trust boundaries.

---

# ESC7 vs ESC4

ESC4 concerns:

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

ESC7 concerns:

```text
CA Permission
```

For example:

```text
User
 |
 v
ManageCA
 |
 v
Certification Authority
```

---

# ESC7 vs ESC5

ESC5 concerns control over broader PKI objects or infrastructure.

For example:

```text
User
 |
 v
GenericWrite
 |
 v
PKI Object
```

ESC7 specifically focuses on:

```text
Certification Authority Administrative Permissions
```

A finding should identify the actual permission rather than relying only on the ESC number.

---

# ESC7 vs ESC6

ESC6 concerns a CA configured with:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

ESC7 may provide a route to changing CA configuration.

Conceptually:

```text
ESC7
 |
 v
ManageCA
 |
 v
CA Configuration Change
 |
 v
Enable Dangerous Behaviour
```

This creates an important relationship between:

```text
ESC7
```

and:

```text
ESC6
```

---

# CA Security Descriptor

Certification Authorities maintain a security descriptor controlling administrative access.

Conceptually:

```text
Certification Authority
        |
        v
Security Descriptor
        |
        +--> CA Administrators
        |
        +--> Certificate Managers
        |
        +--> Certificate Requesters
```

ESC7 occurs when these permissions are assigned too broadly.

---

# Common Principals to Review

Look carefully for permissions assigned to:

```text
Domain Users
Authenticated Users
Domain Computers
Helpdesk Groups
Application Teams
Service Accounts
Legacy PKI Groups
Deployment Accounts
Certificate Enrollment Groups
Non-PKI Administrators
```

Not every non-default principal represents a vulnerability.

The question is whether the administrative permission is appropriate for that principal's role.

---

# Discover Certification Authorities

Certipy provides convenient AD CS enumeration.

Begin with:

```bash
certipy --version
```

Then review discovery options:

```bash
certipy find -h
```

A typical authenticated read-only discovery command is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

---

# Review CA Permissions with Certipy

Certipy output can include CA permissions such as:

```text
Owner
Access Rights
ManageCa
ManageCertificates
Enroll
```

Field names can vary between releases.

Always record:

```text
CA
Principal
Permission
Effective Group Path
```

---

# Example Enumeration Result

Conceptually, a problematic result might resemble:

```text
Certificate Authority:
CORP-CA

Permissions:
  ManageCa:
    CORP\PKI-Operators

  ManageCertificates:
    CORP\Certificate-Managers
```

The next question is:

```text
Who can become a member of these groups?
```

---

# Resolve Group Membership

From Windows:

```powershell
Get-ADGroupMember -Identity 'PKI-Operators' -Recursive |
    Select-Object Name,SamAccountName,ObjectClass
```

Also inspect the group itself:

```powershell
Get-ADGroup 'PKI-Operators' -Properties * |
    Select-Object Name,GroupScope,GroupCategory,DistinguishedName
```

---

# Determine Current User Membership

```powershell
whoami /groups
```

This can help identify security groups represented in the current access token.

---

# Native CA Discovery

Windows provides native certificate utilities.

Discover available CA configurations with:

```cmd
certutil -config - -ping
```

This can identify Enterprise CAs reachable from the current environment.

---

# Certification Authority Console

On authorised administrative systems, the Certification Authority management console can be opened with:

```text
certsrv.msc
```

The console exposes administrative areas such as:

```text
Revoked Certificates
Issued Certificates
Pending Requests
Failed Requests
Certificate Templates
```

Do not perform changes during routine enumeration.

---

# CA Properties

CA security settings can be reviewed through the Certification Authority management console.

Conceptually:

```text
Certification Authority
       |
       v
Properties
       |
       v
Security
```

Review which principals possess:

```text
Manage CA
Issue and Manage Certificates
Request Certificates
```

---

# Read-Only Validation

For most assessments, evidence such as:

```text
Low-Privileged Principal
        |
        v
ManageCA
```

or:

```text
Low-Privileged Principal
        |
        v
ManageCertificates
```

combined with documentation of the available administrative capability may be sufficient.

Do not modify CA configuration merely to prove that the permission works.

---

# CA Permissions vs Active Directory ACLs

This distinction is important.

Certificate templates are Active Directory objects.

CA permissions are associated with the Certification Authority itself.

Therefore:

```text
Get-Acl AD:<template DN>
```

is useful for:

```text
ESC4
```

but does not by itself establish:

```text
ESC7
```

---

# CA Object in Active Directory

Enterprise CA registration information also exists under:

```text
CN=Enrollment Services,
CN=Public Key Services,
CN=Services,
CN=Configuration,...
```

However:

```text
Control of Enrollment Services AD Object
```

is not automatically equivalent to:

```text
ManageCA
```

These are separate security boundaries.

---

# ManageCA Capabilities

The exact operations available through `ManageCA` depend on the CA configuration and Windows behaviour.

Security-sensitive examples may include management of:

```text
CA Configuration
CA Security
Certificate Managers
Policy Module Settings
Exit Module Settings
Published Templates
Other CA Properties
```

Do not assume every administrative operation is available through every interface.

Verify the target configuration.

---

# Why ManageCA Is Dangerous

A CA is part of the identity trust infrastructure.

Conceptually:

```text
ManageCA
    |
    v
CA Configuration
    |
    v
Certificate Issuance Behaviour
    |
    v
Authentication
```

Therefore inappropriate `ManageCA` assignment can expose a powerful control-plane path.

---

# ManageCA and CA Security

One particularly important question is whether a CA manager can change:

```text
CA Security Permissions
```

If so, an existing administrative permission may be used to grant additional CA rights.

Conceptually:

```text
ManageCA
    |
    v
Modify CA Security
    |
    v
Additional CA Permission
```

The exact operation should be verified against the target CA and current tooling before active testing.

---

# ManageCA and ManageCertificates

A historically important ESC7 chain involves combining:

```text
ManageCA
```

with:

```text
ManageCertificates
```

because CA administration may allow a principal to gain or assign certificate-management capability depending on the effective CA security configuration.

Conceptually:

```text
ManageCA
    |
    v
CA Administrative Control
    |
    v
Certificate Management Capability
```

Do not perform this permission change in production merely to demonstrate the theoretical path.

---

# ManageCertificates

`ManageCertificates` gives a principal certificate-manager capabilities.

This commonly affects requests that are:

```text
Pending
```

rather than automatically issued.

Conceptually:

```text
Certificate Request
       |
       v
Pending
       |
       v
Certificate Manager
       |
       +--> Issue
       |
       +--> Deny
```

---

# Certificate Manager Approval

Some templates require:

```text
Certificate Manager Approval
```

This is normally a security control.

The normal workflow is:

```text
User Requests Certificate
        |
        v
Request Pending
        |
        v
Certificate Manager Reviews
        |
        v
Issue / Deny
```

---

# Why ManageCertificates Changes the Model

If an attacker is themselves a certificate manager:

```text
Attacker Requests
      |
      v
Pending
      |
      v
Attacker Approves
```

the manager-approval control may no longer provide meaningful separation.

This is why inappropriate certificate-manager permissions are dangerous.

---

# SubCA Template

Historical ESC7 research often discusses the built-in:

```text
SubCA
```

certificate template.

The SubCA template is important because it can provide powerful certificate capabilities.

However, several conditions matter:

```text
Template Availability
Enrollment Rights
Request Disposition
Certificate Manager Rights
CA Configuration
Current Windows Behaviour
```

Do not assume the presence of the template automatically creates an exploitable path.

---

# Historical ESC7 Certificate Manager Path

A classic model is:

```text
Attacker
   |
   v
ManageCertificates
   |
   v
Submit Certificate Request
   |
   v
Request Becomes Pending
   |
   v
Issue Pending Request
   |
   v
Certificate
```

This becomes dangerous if the resulting certificate can be used for unintended authentication or certificate issuance purposes.

---

# Certificate Manager Restrictions

AD CS can support restrictions on certificate managers.

Conceptually:

```text
Certificate Manager
       |
       v
Restricted to
       |
       +--> Specific Templates
       |
       +--> Specific Subjects / Groups
```

Review whether certificate-manager permissions are broadly scoped.

---

# Do Not Assume All Certificate Managers Are Equal

A principal may have:

```text
ManageCertificates
```

but still be restricted by certificate-manager restrictions.

Therefore assess:

```text
Permission
     +
Manager Restrictions
     +
Template
     +
Request
```

before determining impact.

---

# Enumerate Published Templates

Use Active Directory to determine templates published by Enterprise CAs.

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$enrollmentBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $enrollmentBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties certificateTemplates,dNSHostName |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Enumerate Certificate Templates

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties displayName,pKIExtendedKeyUsage,'msPKI-Certificate-Application-Policy','msPKI-Enrollment-Flag' |
    Select-Object Name,displayName,pKIExtendedKeyUsage,'msPKI-Certificate-Application-Policy','msPKI-Enrollment-Flag'
```

---

# Evaluate Authentication Capability

If ESC7 could result in certificate issuance, determine what the certificate can actually do.

Relevant EKUs may include:

```text
Client Authentication
1.3.6.1.5.5.7.3.2

Smart Card Logon
1.3.6.1.4.1.311.20.2.2

PKINIT Client Authentication
1.3.6.1.5.2.3.4

Any Purpose
2.5.29.37.0
```

Do not infer authentication capability solely from the template name.

---

# Certificate Mapping Still Matters

As with other AD CS techniques, modern certificate authentication must be evaluated against Microsoft's strong certificate mapping protections.

Therefore:

```text
Certificate Issued
```

does not automatically mean:

```text
Privileged Account Compromised
```

Evaluate:

```text
Certificate Identity
SID Security Extension
Certificate Mapping
Domain Controller Behaviour
```

---

# ESC7 and Strong Certificate Mapping

Strong certificate mapping does not eliminate the underlying ESC7 permission problem.

ESC7 concerns:

```text
Who Can Administer the CA?
```

Strong mapping concerns:

```text
How Does a Certificate Map to an Account?
```

These are separate controls.

---

# ESC7 and ESC6

A CA administrator may have the ability to alter policy-module settings.

One historically dangerous setting is:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

Conceptually:

```text
ManageCA
    |
    v
Modify CA Policy
    |
    v
ESC6 Condition
```

Current strong mapping and SID-extension protections must still be considered before claiming alternate-identity authentication.

---

# ESC7 and ESC9

ESC9 is associated with certificate templates that omit the SID security extension.

An ESC7 path may become more dangerous when other template weaknesses already exist.

Conceptually:

```text
ESC7
 |
 v
CA Administrative Control
 |
 +--> Existing ESC9 Template
 |
 v
Certificate Abuse Path
```

---

# ESC7 and ESC16

ESC16 concerns CA-wide suppression of the SID security extension.

Because ESC16 is CA-wide, inappropriate CA administrative access is particularly relevant.

Conceptually:

```text
ESC7
 |
 v
CA Administrative Control
 |
 v
Security-Sensitive CA Configuration
 |
 v
Potential ESC16-Related Condition
```

Do not alter SID-extension configuration during routine validation.

---

# ESC7 and ESC8

ESC8 concerns NTLM relay to AD CS HTTP enrollment endpoints.

ESC7 concerns:

```text
CA Administrative Permissions
```

These can coexist but are separate weaknesses.

---

# ESC7 and ESC11

ESC11 concerns NTLM relay to AD CS RPC enrollment under vulnerable conditions.

Again:

```text
ESC7 = CA Administration
ESC11 = Enrollment Relay
```

The attack paths can interact but should be reported separately when they have different root causes.

---

# ESC7 and ESC4

Another possible relationship is:

```text
ESC4
 |
 v
Template Control
```

combined with:

```text
ESC7
 |
 v
CA Control
```

A principal controlling both certificate-template configuration and CA administration has significantly greater PKI influence.

---

# ESC7 and ESC5

ESC5 and ESC7 together can indicate broader PKI control-plane compromise.

For example:

```text
PKI Object Control
        +
CA Administrative Control
        =
Broad PKI Administrative Capability
```

This should be treated as a major identity-security concern.

---

# Certipy ESC7 Enumeration

Certipy can identify dangerous CA permissions.

A typical discovery command is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Look for output identifying:

```text
ESC7
```

and inspect the associated:

```text
Principal
CA
Permission
```

---

# Verify Certipy Version

Before using operational commands:

```bash
certipy --version
```

Review:

```bash
certipy ca -h
```

and:

```bash
certipy req -h
```

Certipy syntax changes between releases.

Do not rely blindly on commands from older AD CS write-ups.

---

# Certipy CA Functionality

The `ca` command family can expose CA management functionality supported by the installed Certipy release.

Review:

```bash
certipy ca -h
```

before performing any operation.

Potential administrative functions can be security-sensitive.

Do not execute modification options unless they are explicitly within scope.

---

# Safe Certipy Use

For routine assessment:

```text
find
```

should generally come before:

```text
ca
```

or:

```text
req
```

The workflow should be:

```text
Discover
   |
   v
Analyse
   |
   v
Determine Whether Active Proof Is Needed
```

---

# Do Not Enable Templates Merely to Prove ESC7

Some historical ESC7 exploitation chains involve enabling a certificate template on the CA.

Do not do this in production merely to demonstrate:

```text
ManageCA
```

Enabling a template can expose certificate enrollment to other users and systems.

---

# Do Not Change CA Security Merely to Prove ESC7

Likewise, avoid changing:

```text
CA ACL
```

to grant yourself:

```text
ManageCertificates
```

during routine validation.

The existing permission plus documented administrative capability may already provide sufficient evidence.

---

# Do Not Restart CertSvc Casually

Some CA configuration changes require restarting:

```text
CertSvc
```

Restarting Certificate Services can affect production certificate enrollment.

Do not restart the CA service unless explicitly authorised and operational impact has been considered.

---

# Safe Validation Strategy

A preferred ESC7 workflow is:

```text
Enumerate CA
    |
    v
Identify Dangerous Permission
    |
    v
Resolve Effective Principal
    |
    v
Determine Administrative Capability
    |
    v
Review Existing CA Configuration
    |
    v
Can Impact Be Demonstrated Read-Only?
    |
    +--> Yes -> Stop and Report
    |
    +--> No
           |
           v
       Obtain Explicit Approval
           |
           v
       Controlled Test
```

---

# Controlled Test Accounts

If certificate-manager functionality must be demonstrated, use:

```text
Dedicated Requester Account
Dedicated Certificate Manager Account
Dedicated Test Template
Dedicated Test Certificate
```

where possible.

Avoid:

```text
Administrator
Domain Admin
Enterprise Admin
Domain Controller
Production Service Account
```

as target identities.

---

# Minimum-Impact Validation

A controlled validation might demonstrate only that the authorised test principal can:

```text
View Pending Request
```

or another non-destructive administrative action.

The exact validation should be agreed with the organisation before testing.

---

# Certificate Request Approval

If explicitly approved, certificate-manager capability can be validated against a dedicated test request.

Conceptually:

```text
Test Account
    |
    v
Submit Test Request
    |
    v
Pending Request
    |
    v
Approved Test Certificate Manager
    |
    v
Controlled Administrative Action
```

Do not use production user requests for validation.

---

# Record Request IDs

Certificate requests have request identifiers.

For approved testing, record:

```text
Request ID
Requester
Template
Subject
SAN
Submission Time
Disposition
Manager
Issue Time
```

This helps with evidence and cleanup.

---

# Detection

ESC7 detection should focus on:

```text
CA Permission Changes
CA Administrative Actions
Certificate Manager Activity
CA Configuration Changes
Certificate Issuance
```

---

# CA Security Changes

Monitor changes to the CA security descriptor.

Unexpected additions of:

```text
Manage CA
Issue and Manage Certificates
```

should be investigated.

---

# CA Administrative Groups

Maintain a baseline of principals authorised to administer the CA.

For example:

```text
Approved PKI Administrators
Approved Certificate Managers
Approved Enrollment Groups
```

Alert on unexpected additions.

---

# Event 4880

Where Certificate Services auditing is configured, Windows can generate CA-related auditing events.

One important category includes changes to Certificate Services configuration.

Exact event availability depends on:

```text
Windows Version
CA Role
Audit Configuration
Action Performed
```

Do not rely on a single event ID for ESC7 detection.

---

# Event 4886

Certificate Services can log:

```text
4886
```

when it receives a certificate request.

This can provide useful context for certificate-manager abuse.

---

# Event 4887

Certificate Services can log:

```text
4887
```

when a certificate request is approved and a certificate is issued.

Correlate:

```text
Requester
Template
Request ID
Issue Time
```

---

# Event 4888

Certificate Services auditing can also record denial of a certificate request.

This can provide additional request-management context.

---

# Event 4889

Certificate Services auditing can record a certificate request being set to pending.

This is particularly relevant when analysing certificate-manager workflows.

---

# Pending to Issued Correlation

A useful detection model is:

```text
Request Submitted
      |
      v
Pending
      |
      v
Certificate Manager Action
      |
      v
Issued
```

Investigate unexpected managers approving their own requests or requests associated with unusual identities.

---

# Monitor CA Configuration

Changes to:

```text
EditFlags
Request Disposition
Policy Module
Exit Module
CA Security
Published Templates
```

should be monitored and subject to change control.

---

# Monitor Template Publication

Unexpected publication of a sensitive certificate template can indicate CA administrative abuse.

Conceptually:

```text
CA Administrator
      |
      v
Enable Template
      |
      v
New Enrollment Path
```

---

# Monitor CA Service Restarts

Correlate unexpected:

```text
CertSvc Restart
```

with:

```text
CA Configuration Change
CA Permission Change
Template Publication
```

---

# Monitor Administrative Logons

CA servers should have a very small administrative population.

Monitor:

```text
Interactive Logons
Remote Interactive Logons
Remote Administration
PowerShell Remoting
Service Creation
Scheduled Tasks
```

according to organisational monitoring capabilities.

---

# Monitor Certipy-Like Activity Carefully

Do not attempt to detect only a specific tool name.

Focus on behaviour:

```text
CA Enumeration
CA Permission Change
Template Publication
Certificate Request
Request Approval
Certificate Authentication
```

Tools can change while the underlying activity remains the same.

---

# Correlate with Kerberos

Where issued certificates are used for PKINIT, correlate certificate issuance with:

```text
4768
```

Ticket Granting Ticket requests.

This can help connect:

```text
Certificate Administration
```

to:

```text
Certificate Authentication
```

---

# Hardening ESC7

The primary mitigation is:

```text
Restrict CA Administrative Permissions
```

Only dedicated PKI administrators should normally possess:

```text
ManageCA
```

Only approved certificate managers should possess:

```text
ManageCertificates
```

---

# Review ManageCA

Identify every principal with:

```text
ManageCA
```

For each principal ask:

```text
Why Is This Required?
Who Are the Members?
Can Membership Be Modified?
Is It Still Needed?
Is the Account Tiered?
Is It Monitored?
```

---

# Review ManageCertificates

Likewise review every principal with:

```text
ManageCertificates
```

Certificate managers can participate directly in issuance decisions.

Treat this as privileged access.

---

# Avoid Broad Groups

Administrative CA permissions should not normally be assigned to broad principals such as:

```text
Domain Users
Authenticated Users
Domain Computers
Everyone
```

Any such configuration requires immediate investigation.

---

# Review Nested Groups

A seemingly secure assignment may still be vulnerable.

For example:

```text
PKI-Admins
    |
    v
Contains
    |
    v
Helpdesk
```

If Helpdesk membership is broad:

```text
ManageCA
```

may effectively be broad as well.

---

# Review Group Management

Also ask:

```text
Who Can Modify PKI-Admins?
```

A user may not directly possess `ManageCA` but may control a group that does.

Conceptually:

```text
alice
 |
 v
GenericWrite
 |
 v
PKI-Admins
 |
 v
ManageCA
 |
 v
CA
```

---

# Use BloodHound for Indirect Paths

BloodHound can help identify relationships such as:

```text
User
 |
 v
Group Control
 |
 v
PKI Admin Group
 |
 v
CA Permission
```

Always verify graph-derived relationships directly.

---

# Separate CA Administration

Where operationally possible, separate:

```text
CA Administrators
Certificate Managers
Template Administrators
Enrollment Operators
Server Administrators
```

This reduces the blast radius of a single compromised role.

---

# Protect CA Administrative Accounts

Use appropriate controls such as:

```text
Dedicated Admin Accounts
Privileged Access Workstations
Strong Authentication
Restricted Logon
No Internet Browsing
No Email
Minimal Group Membership
Administrative Tiering
```

---

# Treat Enterprise CA as Tier 0

Where the CA issues certificates used for Active Directory authentication, compromise of the CA can affect the identity control plane.

Therefore Enterprise PKI should generally receive protections comparable to other highly privileged identity infrastructure.

---

# Protect CA Hosts

Apply:

```text
Server Hardening
Patch Management
EDR
Application Control
Firewall Restrictions
Administrative Tiering
Secure Remote Administration
Backup Protection
```

---

# Protect CA Private Keys

ESC7 is not the same as CA private-key compromise.

However, CA administrators may operate on systems containing extremely sensitive key material.

Protect keys using controls such as:

```text
Non-Exportable Keys
HSM
Strict Key ACLs
Secure Backup
Dual Control
Auditing
```

where appropriate.

---

# Certificate Manager Restrictions

Where certificate managers are required, configure restrictions appropriate to organisational needs.

Limit which managers can manage:

```text
Specific Templates
Specific Requesters
Specific Certificate Classes
```

where supported.

---

# Require Separation of Duties

A sensitive workflow should avoid:

```text
Requester
    =
Approver
```

where practical.

The preferred model is:

```text
Requester
    |
    v
Independent Approval
    |
    v
Certificate Issuance
```

---

# Change Control

Require formal change control for:

```text
CA Security Changes
ManageCA Assignment
ManageCertificates Assignment
Template Publication
Policy Module Changes
EditFlags Changes
Certificate Manager Restrictions
```

---

# Baseline CA Permissions

Maintain a baseline containing:

```text
CA
Owner
ManageCA Principals
ManageCertificates Principals
Enrollment Principals
Published Templates
Certificate Manager Restrictions
```

Regularly compare the live configuration against the baseline.

---

# Remove Legacy Permissions

ESC7 commonly appears because of:

```text
Old PKI Deployments
Migration Accounts
Former Administrators
Legacy Service Accounts
Application Teams
Temporary Project Groups
Deprecated Certificate Workflows
```

Remove privileges that no longer have a documented requirement.

---

# Incident Response

If ESC7 abuse is suspected:

```text
Identify Principal
      |
      v
Determine CA Permission
      |
      v
Establish Timeline
      |
      v
Identify Administrative Actions
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
Restore CA Configuration
```

---

# Determine the Initial Access Path

Establish whether the attacker obtained CA administration through:

```text
Direct CA Permission
Group Membership
Nested Group
Group ACL Abuse
Credential Compromise
CA Host Compromise
```

This determines the remediation scope.

---

# Review CA Security Descriptor

Compare the current CA security descriptor with:

```text
Known-Good Baseline
```

Identify:

```text
Added Principals
Removed Principals
Changed Rights
Unexpected Administrators
Unexpected Certificate Managers
```

---

# Review CA Configuration Changes

Investigate:

```text
EditFlags
Policy Module
Request Disposition
Published Templates
Certificate Manager Restrictions
CA Security
```

for unauthorised modifications.

---

# Review Template Publication

Determine whether the attacker enabled or disabled templates.

Record:

```text
Template
Time
Actor
Previous State
Current State
```

---

# Review Pending Requests

Determine whether certificate requests were:

```text
Approved
Denied
Resubmitted
Issued
```

by the suspicious principal.

---

# Review Issued Certificates

For suspicious certificates record:

```text
Request ID
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
SID Security Extension
```

---

# Review Certificate Authentication

Correlate suspicious issuance with:

```text
Kerberos PKINIT
Smart Card Logon
TLS Client Authentication
VPN Authentication
Application Authentication
```

depending on certificate purpose.

---

# Revoke Malicious Certificates

If unauthorised certificates were issued:

```text
Identify
   |
   v
Revoke
   |
   v
Publish Updated CRL
   |
   v
Verify Distribution
```

---

# Remove Unauthorised CA Permissions

Remove:

```text
ManageCA
ManageCertificates
```

from principals that do not require them.

Also investigate how the permissions were obtained.

---

# Restore CA Configuration

If CA configuration was changed:

```text
Compare with Baseline
      |
      v
Validate Business Requirement
      |
      v
Restore Approved Configuration
```

Use the organisation's PKI recovery and change-control procedures.

---

# Investigate CA Host Compromise

If the attacker obtained operating-system administrative access to the CA server, ESC7 may no longer represent the full incident.

Investigate:

```text
CA Private Keys
CA Database
CA Backups
Service Accounts
Administrative Credentials
HSM Access
Malware
Persistence
```

---

# CA Key Compromise

If the CA private key may have been compromised, the incident becomes significantly more severe.

Potential recovery may include:

```text
CA Re-Key
CA Replacement
Certificate Revocation
Certificate Re-Issuance
Trust Store Changes
```

Follow the organisation's PKI recovery procedures.

---

# Reporting ESC7

Avoid finding titles such as:

```text
ESC7 Found
```

Prefer:

```text
Low-Privileged Group Has Manage CA Permission
```

or:

```text
Excessive Certification Authority Permissions Allow Certificate Management
```

or:

```text
Non-PKI Administrators Can Manage Enterprise Certification Authority
```

---

# Example Finding - ManageCA

```text
Finding:
Low-Privileged Group Has Manage CA Permission

Affected CA:
CORP-CA01

Affected Principal:
CORP\PKI-Operators

Permission:
ManageCA

Description:
The CORP\PKI-Operators group has Manage CA permission over the
Enterprise Certification Authority CORP-CA01.

Membership of CORP\PKI-Operators includes accounts that are not
designated PKI administrators.

Manage CA provides security-sensitive administrative capability over
the Certification Authority and can affect CA configuration and
certificate issuance behaviour.

Impact:
Compromise of a member of CORP\PKI-Operators may provide
administrative influence over the enterprise certificate authority.

Depending on the CA configuration and other certificate-service
controls, this may permit additional certificate-management
capabilities or changes that create certificate-based privilege
escalation paths.

No CA configuration was modified during the assessment because the
existing effective permission provides sufficient evidence of the
administrative control weakness.

Recommendation:
Remove Manage CA from CORP\PKI-Operators unless CA administration is
an explicitly required business function.

Restrict Manage CA to dedicated PKI administrators and review nested
group membership and control over all groups receiving CA
administrative permissions.

Monitor changes to CA permissions and maintain an approved baseline
of CA administrators.
```

---

# Example Finding - ManageCertificates

```text
Finding:
Excessive Certificate Manager Permissions on Enterprise CA

Affected CA:
CORP-CA01

Affected Principal:
CORP\Helpdesk-Certificates

Permission:
Issue and Manage Certificates

Description:
The CORP\Helpdesk-Certificates group has certificate-manager
permissions on the Enterprise Certification Authority.

The affected group contains accounts that do not require unrestricted
certificate approval capabilities.

Certificate managers can participate in certificate request
disposition and may be able to approve pending certificate requests
depending on configured certificate-manager restrictions.

Impact:
Compromise of an affected account may allow unauthorised certificate
requests to be approved.

The resulting impact depends on the certificate template, certificate
purpose, request identity, SID security extension, certificate
mapping, and certificate-manager restrictions.

Recommendation:
Restrict certificate-manager permissions to dedicated PKI personnel.

Configure certificate-manager restrictions where supported and
maintain separation between certificate requesters and approvers.

Review historical certificate approvals performed by members of the
affected group.
```

---

# Severity Assessment

ESC7 severity depends on:

```text
Principal
    +
Effective CA Permission
    +
Group Control
    +
CA Configuration
    +
Available Templates
    +
Certificate Manager Restrictions
    +
Other ESC Conditions
    +
Reachable Authentication Path
    =
Severity
```

---

# Critical Example

```text
Domain Users
    |
    v
ManageCA
    |
    v
Enterprise CA
    |
    v
Security-Sensitive Configuration
    |
    v
Certificate Privilege Path
```

This would represent an extremely serious PKI configuration issue.

---

# High-Risk Example

```text
Helpdesk
   |
   v
ManageCertificates
   |
   v
Sensitive Pending Requests
   |
   v
Certificate Approval
```

The impact depends on certificate-manager restrictions and available certificate workflows.

---

# Indirect Critical Path

```text
alice
 |
 v
GenericWrite
 |
 v
PKI-Admins
 |
 v
ManageCA
 |
 v
Enterprise CA
```

The root cause includes both:

```text
Group Control
```

and:

```text
CA Administrative Permission
```

---

# Evidence Checklist

For an ESC7 finding record:

```text
CA Name
CA Host
Principal
Principal SID
Permission
ManageCA
ManageCertificates
Direct / Group-Derived
Nested Group Path
Group Control Path
CA Security Descriptor
Published Templates
Certificate Manager Restrictions
Request Disposition
Relevant CA Configuration
Relevant ESC Conditions
Potential Administrative Actions
Validation Performed
Certificate Request IDs
Certificate Serial Numbers
Cleanup Result
```

---

# ESC7 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify CA hosts
- [ ] Enumerate CA permissions
- [ ] Enumerate published templates
- [ ] Identify CA owner where applicable
- [ ] Identify certificate managers
- [ ] Identify CA administrators

## Permission Analysis

- [ ] Identify ManageCA
- [ ] Identify ManageCertificates
- [ ] Identify enrollment rights
- [ ] Resolve direct permissions
- [ ] Resolve group-derived permissions
- [ ] Resolve nested groups
- [ ] Review group-control paths
- [ ] Identify broad principals
- [ ] Identify legacy accounts
- [ ] Identify service accounts
- [ ] Determine effective permissions

## ManageCA Analysis

- [ ] Identify every ManageCA principal
- [ ] Determine business requirement
- [ ] Review group membership
- [ ] Review who can modify the group
- [ ] Determine available CA administrative operations
- [ ] Review CA security configuration
- [ ] Review policy-module configuration
- [ ] Review published templates
- [ ] Review potential relationship with ESC6
- [ ] Review potential relationship with ESC16

## ManageCertificates Analysis

- [ ] Identify every certificate manager
- [ ] Review certificate-manager restrictions
- [ ] Review pending-request workflows
- [ ] Identify sensitive templates
- [ ] Determine whether requester and approver are separated
- [ ] Review historical approval activity
- [ ] Determine potential certificate impact

## Related ESC Conditions

- [ ] Review ESC1
- [ ] Review ESC4
- [ ] Review ESC5
- [ ] Review ESC6
- [ ] Review ESC8
- [ ] Review ESC9
- [ ] Review ESC10
- [ ] Review ESC11
- [ ] Review ESC16

## Tooling

- [ ] Check Certipy version
- [ ] Review `certipy find -h`
- [ ] Enumerate CA with Certipy
- [ ] Review `certipy ca -h`
- [ ] Review `certipy req -h`
- [ ] Use native CA tools where appropriate
- [ ] Use PowerShell for group analysis
- [ ] Use BloodHound for indirect paths
- [ ] Manually validate automated ESC7 results

## Validation

- [ ] Prefer read-only validation
- [ ] Record effective permission
- [ ] Determine whether active proof is necessary
- [ ] Obtain explicit approval before CA changes
- [ ] Do not modify CA ACL merely to prove control
- [ ] Do not enable templates merely to prove control
- [ ] Do not change EditFlags merely to prove control
- [ ] Do not restart CertSvc without approval
- [ ] Use dedicated test request where required
- [ ] Record request ID
- [ ] Restore any approved change
- [ ] Verify cleanup

## Detection

- [ ] Monitor CA permission changes
- [ ] Monitor ManageCA assignments
- [ ] Monitor ManageCertificates assignments
- [ ] Monitor certificate-manager activity
- [ ] Monitor CA configuration changes
- [ ] Monitor template publication
- [ ] Monitor CertSvc restarts
- [ ] Monitor event 4886 where configured
- [ ] Monitor event 4887 where configured
- [ ] Monitor pending-request activity
- [ ] Correlate issuance with certificate authentication
- [ ] Monitor privileged logons to CA servers

## Hardening

- [ ] Restrict ManageCA
- [ ] Restrict ManageCertificates
- [ ] Remove broad principals
- [ ] Review nested groups
- [ ] Review control over PKI groups
- [ ] Separate CA administrators and certificate managers
- [ ] Configure certificate-manager restrictions
- [ ] Maintain separation of duties
- [ ] Use dedicated PKI admin accounts
- [ ] Protect CA servers
- [ ] Protect CA private keys
- [ ] Baseline CA permissions
- [ ] Baseline CA configuration
- [ ] Require change control
- [ ] Remove legacy delegation

## Incident Response

- [ ] Identify affected principal
- [ ] Determine how CA permission was obtained
- [ ] Establish timeline
- [ ] Review CA security changes
- [ ] Review CA configuration changes
- [ ] Review template publication
- [ ] Review pending requests
- [ ] Review approved requests
- [ ] Review issued certificates
- [ ] Review certificate authentication
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Remove unauthorised permissions
- [ ] Restore CA configuration
- [ ] Investigate CA host compromise
- [ ] Assess CA private-key exposure

## Cleanup

- [ ] Restore approved CA configuration
- [ ] Restore CA permissions
- [ ] Remove temporary test permissions
- [ ] Revoke test certificates where required
- [ ] Remove test requests where appropriate
- [ ] Delete test PFX files
- [ ] Delete private-key material
- [ ] Verify CertSvc state
- [ ] Compare configuration with baseline
- [ ] Record cleanup evidence

---

# ESC7 Testing Model

The normal model is:

```text
PKI Administrator
       |
       v
ManageCA
       |
       v
Certification Authority
```

The ESC7 model is:

```text
Low-Privileged Principal
       |
       v
ManageCA / ManageCertificates
       |
       v
Certification Authority
```

The direct ManageCA model is:

```text
Principal
   |
   v
ManageCA
   |
   v
CA Administrative Control
```

The certificate-manager model is:

```text
Principal
   |
   v
ManageCertificates
   |
   v
Pending Certificate Request
   |
   v
Issue / Deny
```

The indirect model is:

```text
User
 |
 v
Group Control
 |
 v
PKI Admin Group
 |
 v
ManageCA
 |
 v
Enterprise CA
```

The ESC7-to-ESC6 relationship is:

```text
ESC7
 |
 v
CA Administrative Control
 |
 v
Policy Configuration
 |
 v
Potential ESC6 Condition
```

The combined PKI-control model is:

```text
ESC4
 |
 +--> Template Control
 |
ESC5
 |
 +--> PKI Object Control
 |
ESC7
 |
 +--> CA Control
 |
 v
Broad AD CS Control Plane
```

The certificate-manager workflow is:

```text
Certificate Request
       |
       v
Pending
       |
       v
Certificate Manager
       |
       v
Issue
       |
       v
Certificate
       |
       v
Authentication / Other Use
```

The safe-testing model is:

```text
Enumerate
   |
   v
Identify ESC7 Permission
   |
   v
Resolve Effective Principal
   |
   v
Determine Administrative Capability
   |
   v
Read-Only Evidence Sufficient?
   |
   +--> Yes -> Report
   |
   +--> No
           |
           v
       Explicit Approval
           |
           v
       Dedicated Test
           |
           v
       Minimum Administrative Action
           |
           v
       Evidence
           |
           v
       Restore
```

The detection model is:

```text
CA Permission Change
       |
       v
CA Administrative Action
       |
       v
Certificate Request / Configuration Change
       |
       v
Certificate Issuance
       |
       v
Authentication
```

The defensive model is:

```text
Restricted ManageCA
        +
Restricted ManageCertificates
        +
Protected PKI Groups
        +
Separation of Duties
        +
CA Hardening
        +
Change Control
        +
Monitoring
        =
Reduced ESC7 Risk
```

For penetration testers:

```text
Do Not Ask:
"Does Certipy report ESC7?"

Ask:
"Which principal has which effective CA
administrative permission, what can that
permission actually change, and what
certificate or trust path becomes reachable?"
```

For defenders:

```text
Do Not Only Ask:
"Who is a CA administrator?"

Also Ask:
"Who can become a CA administrator,
who controls the groups containing those
administrators, and who can manage
certificate requests?"
```

The complete ESC7 relationship is:

```text
Principal
   |
   v
Effective Permission
   |
   v
Certification Authority
   |
   v
Administrative Capability
   |
   v
Certificate / Configuration Change
   |
   v
Authentication or Trust Impact
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

ESC5:

[AD CS ESC5](ad-cs-esc5.md)

ESC6:

[AD CS ESC6](ad-cs-esc6.md)

ACL and ACE Abuse:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Groups:

[Active Directory Groups](groups.md)

BloodHound:

[BloodHound](bloodhound.md)

Kerberos:

[Kerberos](kerberos.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs-esc8.md
```

---

# References

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certification Authority Role

[Microsoft - Certification Authority](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certification-authority-role){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Template Concepts

[Microsoft - Certificate Template Concepts](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Secure AD CS

[Microsoft - Securing PKI and Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate-Based Authentication Hardening

[Microsoft - KB5014754 Certificate-Based Authentication Changes](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Before using operational Certipy commands, verify the syntax supported by the installed release:

```bash
certipy --version
certipy find -h
certipy ca -h
certipy req -h
```

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

ESC7 is fundamentally an administrative delegation problem.

The core relationship is:

```text
Untrusted Principal
        |
        v
Trusted CA Administrative Permission
```

This is different from ordinary certificate enrollment.

A user who can request a certificate has:

```text
Enrollment Capability
```

A user with ESC7 may have:

```text
CA Administrative Capability
```

or:

```text
Certificate Management Capability
```

Those capabilities can influence the certificate trust and issuance infrastructure itself.

The most important permissions to investigate are:

```text
ManageCA
ManageCertificates
```

but the assessment should not stop at identifying their names.

Determine:

```text
Who Has the Permission?
        |
        v
How Did They Receive It?
        |
        v
Can Their Group Membership Be Controlled?
        |
        v
What Administrative Actions Are Available?
        |
        v
Which Templates and Requests Are Affected?
        |
        v
Can a Certificate Privilege Path Be Reached?
```

Modern certificate mapping protections must still be considered when the final attack path involves certificate authentication.

However:

```text
Strong Certificate Mapping
```

does not fix:

```text
Excessive CA Administrative Permissions
```

The two controls operate at different layers.

ESC7 also demonstrates why AD CS findings should be analysed as chains rather than isolated configuration flags.

For example:

```text
Group ACL Weakness
       |
       v
PKI Admin Group
       |
       v
ESC7
       |
       v
CA Administrative Control
       |
       v
Other AD CS Condition
       |
       v
Certificate Privilege Path
```

For defenders, the CA should be treated as part of the identity control plane.

For penetration testers, read-only evidence is often enough. There is rarely a need to alter a production CA merely to prove that an inappropriate principal possesses administrative control.

The strongest ESC7 finding documents:

```text
Principal
    +
Effective Permission
    +
CA
    +
Administrative Capability
    +
Reachable Certificate Impact
```

rather than simply stating that an automated tool reported:

```text
ESC7
```
