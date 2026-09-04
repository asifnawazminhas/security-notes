# AD CS ESC16 - CA-Wide SID Security Extension Disabled

ESC16 is an Active Directory Certificate Services (AD CS) security condition in which a Certification Authority is configured so that certificates it issues do not contain the Active Directory SID security extension:

```text
szOID_NTDS_CA_SECURITY_EXT
```

OID:

```text
1.3.6.1.4.1.311.25.2
```

The SID security extension was introduced as part of Microsoft's certificate-based authentication hardening following:

```text
CVE-2022-26923
```

and:

```text
KB5014754
```

Its purpose is to provide a strong relationship between:

```text
Certificate
```

and:

```text
Active Directory SID
```

Conceptually:

```text
Certificate
    |
    v
SID Security Extension
    |
    v
Active Directory SID
    |
    v
Specific User / Computer
```

ESC16 occurs when the CA suppresses this extension globally.

The important distinction is:

```text
ESC9
=
Individual Template Omits SID Extension
```

whereas:

```text
ESC16
=
CA Omits SID Extension Globally
```

This makes ESC16 particularly significant because the weakness can affect certificates issued from many templates rather than one specific template.

!!! warning "Authorised testing only"
    ESC16 can become part of certificate-based account-impersonation chains. During production assessments, begin with read-only CA configuration, template and certificate inspection. Do not modify user UPNs, enable ESC6, disable certificate extensions, weaken domain-controller certificate mapping, or request certificates for privileged production identities merely to demonstrate impact.

---

# ESC16 at a Glance

The expected certificate issuance model is:

```text
Certificate Request
        |
        v
Enterprise CA
        |
        v
SID Security Extension Added
        |
        v
Issued Certificate
        |
        v
Strong Account Mapping
```

ESC16 changes this to:

```text
Certificate Request
        |
        v
ESC16 CA
        |
        v
SID Security Extension Suppressed
        |
        v
Issued Certificate
        |
        v
No SID Security Extension
```

The practical security impact then depends on:

```text
Certificate Identity
        +
Certificate Mapping
        +
Other AD CS Conditions
        +
Domain Controller Behaviour
```

---

# Why the SID Security Extension Exists

Historically, Windows certificate authentication could map certificates to Active Directory accounts using identity information such as:

```text
UPN
DNS Name
Subject
Issuer
```

Some of these mappings were not cryptographically tied to one specific Active Directory object.

Conceptually:

```text
Certificate
    |
    v
UPN = alice@corp.example
    |
    v
Find Alice
```

If an attacker could manipulate the identity information appearing in the certificate, this could create impersonation opportunities.

---

# Strong Certificate Mapping

Microsoft introduced stronger certificate binding so that a certificate could contain information tied directly to the Active Directory principal.

The important extension is:

```text
1.3.6.1.4.1.311.25.2
```

Conceptually:

```text
Certificate
    |
    v
SID Extension
    |
    v
S-1-5-21-...-1105
    |
    v
CORP\Alice
```

This provides substantially stronger identity binding than relying only on a UPN or DNS name.

---

# Security Extension Name

The Microsoft security extension is commonly referenced as:

```text
szOID_NTDS_CA_SECURITY_EXT
```

OID:

```text
1.3.6.1.4.1.311.25.2
```

During assessment, remember both forms because tools and documentation may display either.

---

# ESC16 Root Cause

ESC16 is associated with the CA's:

```text
DisableExtensionList
```

configuration.

If the SID security extension OID appears in this list:

```text
1.3.6.1.4.1.311.25.2
```

the CA can suppress the SID security extension from certificates it issues.

Conceptually:

```text
CA Policy Module
      |
      v
DisableExtensionList
      |
      v
1.3.6.1.4.1.311.25.2
      |
      v
SID Extension Disabled
```

---

# CA-Wide Scope

The word:

```text
CA-Wide
```

is important.

With ESC9:

```text
Template A -> No SID Extension
Template B -> SID Extension
Template C -> SID Extension
```

With ESC16:

```text
                ESC16 CA
                   |
        +----------+----------+
        |          |          |
        v          v          v
    Template A Template B Template C
        |          |          |
        v          v          v
     No SID      No SID     No SID
```

The CA-level policy affects certificate issuance regardless of the normal template expectation.

---

# ESC9 vs ESC16

```text
+----------------------+-----------------------------+
| Technique            | SID Extension Suppression   |
+----------------------+-----------------------------+
| ESC9                 | Certificate template        |
| ESC16                | Certification Authority     |
+----------------------+-----------------------------+
```

ESC9 is primarily a:

```text
Template Configuration
```

issue.

ESC16 is primarily a:

```text
CA Configuration
```

issue.

---

# ESC9 Configuration

ESC9 is associated with:

```text
CT_FLAG_NO_SECURITY_EXTENSION
```

in:

```text
msPKI-Enrollment-Flag
```

on an individual certificate template.

---

# ESC16 Configuration

ESC16 instead involves:

```text
DisableExtensionList
```

at the CA policy-module level.

The relevant value is:

```text
1.3.6.1.4.1.311.25.2
```

---

# Why ESC16 Matters More Broadly

Consider a CA publishing:

```text
User
Computer
WebServer
VPNUser
WorkstationAuthentication
CustomAuthentication
```

If only:

```text
VPNUser
```

has ESC9, only certificates from that template intentionally omit the SID security extension.

With ESC16:

```text
All Certificates Issued by the CA
```

can be affected by the CA-wide suppression.

This dramatically increases the number of templates that must be reviewed.

---

# ESC16 Does Not Automatically Mean Domain Compromise

Finding:

```text
1.3.6.1.4.1.311.25.2
```

in:

```text
DisableExtensionList
```

is an important security finding.

But it does not mean:

```text
Any Domain User
Can Immediately Become
Domain Administrator
```

Additional conditions determine exploitability.

---

# ESC16 Attack Model

A better model is:

```text
ESC16
   |
   v
Certificate Has No SID Extension
   |
   v
Can Attacker Influence Identity?
   |
   +--> No -> Limited Direct Exploitability
   |
   +--> Yes
           |
           v
    Mapping Path Available?
           |
           +--> No -> Blocked
           |
           +--> Yes
                   |
                   v
             Impersonation Path
```

---

# Important Prerequisites

Potential exploitation can depend on combinations involving:

```text
Enrollment Rights
Authentication-Capable Template
Identity Manipulation
ESC6
Explicit Mapping
Domain Controller Patch State
Certificate Mapping Behaviour
```

Do not analyse ESC16 in isolation.

---

# Modern 2026 Context

ESC16 must be assessed using current certificate-binding behaviour.

Microsoft's KB5014754 rollout substantially changed certificate authentication.

By the current enforcement model, supported and fully patched domain controllers should be operating under Microsoft's strong certificate-binding requirements.

Historical guidance based on permanent compatibility-mode fallback should therefore not be assumed to describe a modern fully patched environment.

---

# Historical Compatibility Mode

Earlier deployments could use:

```text
StrongCertificateBindingEnforcement
```

to control Kerberos certificate-binding enforcement.

Historical values included behaviour corresponding to:

```text
Disabled
Compatibility
Full Enforcement
```

Many older ESC9 and ESC16 attack descriptions rely on compatibility behaviour.

---

# Full Enforcement

Under Full Enforcement, domain controllers require strong certificate mapping rather than freely falling back to historical weak certificate mappings.

This substantially changes simple UPN-manipulation attack paths.

Therefore:

```text
No SID Security Extension
```

does not automatically mean:

```text
UPN Mapping Will Work
```

on a modern fully patched domain.

---

# September 2025 Change

Microsoft's KB5014754 deployment timeline is important for current assessments.

The historical registry-based compatibility mechanism was transitional.

By September 2025, Microsoft removed support for using the legacy registry configuration to return patched domain controllers to the previous compatibility behaviour.

Therefore, in 2026:

```text
Old Lab Assumptions
```

should not be applied blindly to:

```text
Fully Patched Production Domains
```

---

# ESC16 Still Matters

Strong certificate binding does not make ESC16 irrelevant.

The SID security extension exists for a reason.

Globally suppressing it:

```text
Weakens Certificate Identity Binding
```

and can become exploitable when combined with other certificate identity mechanisms.

One particularly important relationship is:

```text
ESC16 + ESC6
```

---

# ESC16 and ESC6

ESC6 occurs when a CA permits requester-supplied SAN information through the CA-wide:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

configuration.

Conceptually:

```text
ESC6
 |
 v
Attacker Influences SAN
```

ESC16 provides:

```text
ESC16
 |
 v
Normal SID Extension Missing
```

Together:

```text
ESC6
   +
ESC16
   |
   v
Attacker-Controlled Certificate Identity
   |
   v
No Normal SID Security Extension
```

This combination requires careful investigation.

---

# SID in SAN URL

Modern certificate mapping introduced a special SAN URL representation that can contain a SID.

Conceptually:

```text
URL=tag:microsoft.com,2022-09-14:sid:<SID>
```

This mechanism is important when analysing modern ESC6 combinations with ESC9 or ESC16.

Do not treat it as equivalent to the normal CA-generated SID security extension.

---

# Normal SID Extension vs SAN SID

Normal strong issuance:

```text
CA
 |
 v
SID Security Extension
 |
 v
Requester SID
```

Potential abuse chain:

```text
Requester
   |
   v
Attacker-Controlled SAN
   |
   v
SID URL
```

The trust boundary is therefore very different.

---

# ESC16 + ESC6 Conceptual Chain

```text
Low-Privilege User
       |
       v
Authentication Template
       |
       v
ESC6 CA
       |
       +--> Target UPN
       |
       +--> Target SID URL
       |
       v
ESC16
       |
       v
Normal SID Extension Suppressed
       |
       v
Certificate
       |
       v
Certificate Authentication
```

This is one reason ESC16 remains security-relevant even with modern certificate-binding protections.

---

# Do Not Enable ESC6 for Testing

If ESC16 exists but ESC6 does not:

```text
Do Not Enable
EDITF_ATTRIBUTESUBJECTALTNAME2
```

to create an attack chain.

That would introduce another CA-wide vulnerability.

Report the existing condition and explain the potential chaining risk.

---

# ESC16 and ESC9

The result of ESC9 and ESC16 can look similar in an issued certificate:

```text
No SID Security Extension
```

But the cause differs.

ESC9:

```text
Template Says:
Do Not Include Security Extension
```

ESC16:

```text
CA Says:
Do Not Include Security Extension
```

---

# ESC16 Can Override Secure Templates

A template may be correctly configured to include the SID security extension.

But if the CA globally disables the extension:

```text
Secure Template
      |
      v
ESC16 CA
      |
      v
Certificate Without SID Extension
```

Therefore template-only auditing can miss ESC16.

---

# ESC16 and ESC10

ESC10 concerns weak certificate mapping configuration.

ESC16 concerns certificate issuance without the normal SID security extension.

Historically:

```text
ESC16
   +
Weak Mapping
   |
   v
Increased Impersonation Risk
```

In a modern environment, evaluate current Microsoft mapping enforcement before claiming the historical chain remains viable.

---

# ESC16 and ESC14

ESC14 concerns:

```text
altSecurityIdentities
```

and explicit certificate mappings.

Explicit strong mappings can provide a valid mapping even when a certificate lacks the normal SID security extension.

Therefore:

```text
ESC16
```

and:

```text
ESC14
```

should be analysed as different security conditions.

---

# ESC16 and ESC1

ESC1 concerns insecure certificate templates where a requester can control certificate identity and obtain an authentication-capable certificate.

ESC16 concerns CA-wide suppression of the SID security extension.

A template vulnerable to ESC1 should be reported based on its own root cause.

ESC16 can increase the overall certificate-identity attack surface but should not replace the ESC1 analysis.

---

# ESC16 and ESC4

ESC4 concerns dangerous ACL permissions over certificate templates.

An attacker with template-control rights may be able to create or expose additional certificate abuse paths.

ESC16 increases the importance of reviewing all authentication-capable templates published by the affected CA.

---

# ESC16 and CA Permissions

ESC16 is usually an administrative CA configuration issue.

Therefore also review:

```text
Who Can Administer the CA?
```

Relevant privilege paths may include:

```text
CA Administrator
Local Administrator on CA
Enterprise PKI Administrators
Dangerous CA ACLs
```

A malicious actor who controls the CA may be able to alter far more than `DisableExtensionList`.

---

# ESC5 Relationship

Dangerous control over PKI infrastructure can fall into the broader:

```text
ESC5
```

category.

If an attacker can modify CA policy-module registry configuration because they control the CA server, the root cause may be:

```text
PKI Infrastructure Compromise
```

rather than merely a static ESC16 misconfiguration.

---

# Enumerating ESC16 with Certipy

Certipy can enumerate CA configuration and identify ESC16.

Check the installed version:

```bash
certipy --version
```

Then review:

```bash
certipy find -h
```

A typical authorised enumeration is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

---

# Certipy ESC16 Indicator

Modern Certipy output can identify:

```text
ESC16
```

when the CA's disabled-extension configuration contains the SID security extension.

A relevant result may conceptually show:

```text
Disabled Extensions:
1.3.6.1.4.1.311.25.2

ESC16:
Security Extension is disabled
```

---

# Treat Tool Output as Evidence, Not the Entire Analysis

Do not stop at:

```text
Certipy Says ESC16
```

Determine:

```text
Which CA?
Which Templates?
Who Can Enroll?
Which Templates Authenticate?
Is ESC6 Present?
What Certificates Are Being Issued?
What Is the Current DC Mapping Behaviour?
```

---

# Native CA Enumeration

On the CA itself, an administrator can inspect the policy-module disabled extension configuration with:

```cmd
certutil -getreg policy\DisableExtensionList
```

This is a read-only command.

---

# What to Look For

Search the output for:

```text
1.3.6.1.4.1.311.25.2
```

If present, investigate ESC16.

---

# Registry Location

The CA policy configuration is stored beneath:

```text
HKLM\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration
```

with CA-specific policy-module configuration below the relevant CA.

Do not hard-code a policy-module subkey name without first enumerating the actual CA configuration because deployments can differ.

---

# Read CA Name

On the CA:

```cmd
certutil -getreg CA\CAName
```

---

# PowerShell Registry Discovery

A read-only approach can begin with:

```powershell
$base = 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration'
Get-ChildItem $base
```

Then inspect the relevant CA configuration.

---

# Search for DisableExtensionList

A controlled administrative audit can search beneath the CA configuration:

```powershell
$base = 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration'

Get-ChildItem $base -Recurse -ErrorAction SilentlyContinue |
    ForEach-Object {
        $item = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
        if ($null -ne $item.DisableExtensionList) {
            [PSCustomObject]@{
                Path                 = $_.PSPath
                DisableExtensionList = $item.DisableExtensionList
            }
        }
    }
```

This avoids changing the CA configuration.

---

# CA Access Requirements

Local registry enumeration usually requires suitable administrative access to the CA.

A penetration tester without CA administrative access should not assume:

```text
Cannot Read Registry
=
Cannot Assess ESC16
```

Remote AD CS tooling such as Certipy may provide the required configuration visibility depending on permissions and protocols available.

---

# Enumerate Published Templates

Once ESC16 is identified, determine which templates are published by the affected CA.

PowerShell:

```powershell
Import-Module ActiveDirectory
```

Determine the Configuration naming context:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
```

Query Enrollment Services:

```powershell
$base = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $base -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties dNSHostName,certificateTemplates |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Why Template Enumeration Matters

ESC16 affects the CA.

Impact depends heavily on what that CA can issue.

For example:

```text
ESC16 CA
   |
   +--> Web Server Only
   |
   +--> Client Authentication
   |
   +--> Computer Authentication
   |
   +--> User Authentication
```

The second group is generally much more interesting for identity abuse.

---

# Authentication-Capable Templates

Prioritise templates containing purposes such as:

```text
Client Authentication
Smart Card Logon
PKINIT Client Authentication
Any Purpose
```

or templates with no restrictive EKU where Windows semantics make them broadly usable.

---

# Client Authentication OID

```text
1.3.6.1.5.5.7.3.2
```

---

# Smart Card Logon OID

```text
1.3.6.1.4.1.311.20.2.2
```

---

# PKINIT Client Authentication OID

```text
1.3.6.1.5.2.3.4
```

---

# Any Purpose OID

```text
2.5.29.37.0
```

---

# Enumerate Template EKUs

```powershell
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"

Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties displayName,pKIExtendedKeyUsage |
    Select-Object Name,displayName,pKIExtendedKeyUsage
```

---

# Enrollment Rights Matter

An ESC16 CA may publish authentication-capable templates.

But the next question is:

```text
Can the Attacker Enroll?
```

Review:

```text
Authenticated Users
Domain Users
Domain Computers
Specific Department Groups
Service Accounts
```

and calculate effective enrollment permissions.

---

# Certificate Inspection

A useful defensive validation is to inspect a certificate legitimately issued to a dedicated test principal.

Windows:

```cmd
certutil -dump test.cer
```

Search for:

```text
1.3.6.1.4.1.311.25.2
```

---

# OpenSSL Inspection

For PEM:

```bash
openssl x509 -in test.pem -text -noout
```

For DER:

```bash
openssl x509 -in test.cer -inform DER -text -noout
```

Microsoft-specific extension decoding may be clearer with Windows tooling.

---

# Compare Expected and Actual Certificates

A strong validation method is:

```text
Template Expected to Include SID
           |
           v
Certificate Issued by CA
           |
           v
SID Extension Present?
```

If:

```text
No
```

then investigate whether:

```text
Template = ESC9
```

or:

```text
CA = ESC16
```

---

# Distinguishing ESC9 from ESC16

Suppose:

```text
Template A -> No SID
```

Check another normal authentication template.

If:

```text
Template B -> SID Present
```

the issue may be template-specific.

If:

```text
Template A -> No SID
Template B -> No SID
Template C -> No SID
```

then investigate the CA-wide configuration.

The authoritative answer should come from configuration review rather than certificate sampling alone.

---

# Legacy Unpatched CAs

An important edge case is a CA that never received the Microsoft updates introducing the SID security extension.

Such a CA may issue certificates without the extension even if:

```text
DisableExtensionList
```

does not explicitly contain the OID.

Conceptually:

```text
Old CA
  |
  v
Does Not Implement SID Extension
  |
  v
Certificates Lack SID Extension
```

Given the age of the relevant 2022 security updates, this should be treated as a serious patch-management concern in a current environment.

---

# Patch Verification

Record:

```text
CA Operating System
Windows Build
Installed Cumulative Update
Assessment Date
```

Do not determine patch status only by searching for one historical KB number because cumulative updates supersede earlier fixes.

---

# ESC16 Candidate Classification

A useful classification is:

```text
Confirmed ESC16 Configuration
```

when:

```text
DisableExtensionList
contains
1.3.6.1.4.1.311.25.2
```

A separate condition is:

```text
Legacy CA Missing SID Extension Support
```

when the CA is too old or unpatched to issue the extension correctly.

Document the actual root cause.

---

# Safe Validation

The preferred production workflow is:

```text
Enumerate CA
     |
     v
Read DisableExtensionList
     |
     v
Confirm SID OID Disabled
     |
     v
Enumerate Published Templates
     |
     v
Identify Authentication Templates
     |
     v
Assess Enrollment Rights
```

This is usually sufficient to report the configuration weakness.

---

# Optional Certificate Validation

If certificate issuance is already approved:

```text
Dedicated Test User
       |
       v
Normal Authentication Template
       |
       v
Affected CA
       |
       v
Test Certificate
       |
       v
Inspect Extensions
```

The purpose is only to verify:

```text
SID Security Extension Missing
```

not to impersonate another account.

---

# Do Not Modify a Victim UPN by Default

Historical ESC9 and ESC16 attack demonstrations often involve changing:

```text
userPrincipalName
```

on an account the attacker controls.

Do not perform such manipulation against production identities unless explicitly approved and necessary.

Read-only evidence is usually sufficient.

---

# Do Not Target Administrator

There is no need to request a certificate representing:

```text
Administrator
```

or another Tier 0 principal merely to prove ESC16.

---

# Do Not Disable the Extension for Testing

Never run a configuration change whose purpose is:

```text
Add SID OID to DisableExtensionList
```

on a secure production CA.

That would intentionally create ESC16.

---

# Remediation

The core remediation is:

```text
Remove
1.3.6.1.4.1.311.25.2
from DisableExtensionList
```

so that the CA can include the SID security extension normally.

---

# Change Control Required

CA configuration changes can affect enterprise authentication.

Therefore remediation should use:

```text
PKI Change Management
Testing
Backup
Rollback Planning
Maintenance Window
Validation
```

---

# Native Remediation

Microsoft CA registry settings can be managed using:

```text
certutil
```

However, do not blindly copy a configuration-changing command into production.

First record the current value:

```cmd
certutil -getreg policy\DisableExtensionList
```

Then follow current Microsoft PKI guidance to remove only:

```text
1.3.6.1.4.1.311.25.2
```

while preserving any legitimate disabled extensions.

---

# Do Not Clear the Entire List

Avoid:

```text
Delete DisableExtensionList
```

without understanding its existing contents.

Other extensions may have been intentionally disabled for legitimate PKI reasons.

The objective is:

```text
Remove the SID Security Extension OID
from the Disabled List
```

not:

```text
Destroy Existing CA Policy Configuration
```

---

# Certificate Services Restart

Some CA policy configuration changes require the Certificate Services service to be restarted before they take effect.

Plan this operationally.

Do not restart a production CA during an assessment unless explicitly authorised.

---

# Patch the CA

If the CA lacks the security updates required to support the SID security extension:

```text
Patch the CA
```

according to the supported Windows servicing path.

A registry fix cannot substitute for missing security functionality in an obsolete or unpatched operating system.

---

# Keep Domain Controllers Patched

ESC16 should not be remediated only at the CA.

Maintain current certificate-binding protections on domain controllers.

The defensive relationship is:

```text
Secure CA Issuance
       +
Strong DC Mapping
       =
Strong Certificate Identity
```

---

# Review ESC6

If ESC16 exists, immediately determine whether the same CA also exposes:

```text
ESC6
```

because the combination materially changes potential impact.

---

# Review ESC9

Check templates for:

```text
CT_FLAG_NO_SECURITY_EXTENSION
```

Even after fixing ESC16, individual templates may continue to omit the SID extension through ESC9.

---

# Review ESC10

Review certificate mapping configuration and legacy mapping dependencies.

ESC16 may have been introduced historically to resolve compatibility problems.

Those compatibility dependencies should be identified and fixed rather than preserving insecure global suppression.

---

# Review ESC14

Inventory explicit certificate mappings:

```text
altSecurityIdentities
```

because some legacy applications may use explicit mapping rather than SID-based implicit mapping.

---

# Why Administrators May Have Created ESC16

A plausible historical cause is:

```text
2022 Certificate Hardening Update
        |
        v
Legacy Authentication Breaks
        |
        v
Administrator Troubleshooting
        |
        v
Globally Disable SID Extension
```

This may have restored compatibility while weakening certificate identity security.

---

# Do Not Preserve Insecure Workarounds

The long-term fix should be:

```text
Identify Legacy Dependency
       |
       v
Fix Certificate Mapping
       |
       v
Restore Strong Security Extension
```

not:

```text
Keep Global Security Feature Disabled
```

---

# Detection

ESC16 detection should include:

```text
CA Configuration
Certificate Content
Template Configuration
Certificate Requests
Certificate Authentication
```

---

# Baseline DisableExtensionList

Defenders should periodically inventory:

```text
DisableExtensionList
```

on every Enterprise CA.

Alert when:

```text
1.3.6.1.4.1.311.25.2
```

appears.

---

# Monitor CA Registry Changes

Changes beneath:

```text
HKLM\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration
```

should be treated as sensitive.

Use:

```text
EDR
Registry Auditing
Configuration Management
Change Management
```

to detect unexpected modification.

---

# Monitor CA Administrative Activity

Unexpected administrative activity on a CA is high risk.

Monitor:

```text
Interactive Administrator Logons
Remote Management
PowerShell
Registry Modification
Service Control
Certificate Services Configuration
```

---

# Certificate Services Events

Where Certificate Services auditing is enabled, useful events include:

```text
4886
4887
```

for certificate requests and issuance.

These events do not directly mean ESC16 exploitation occurred.

They become useful when correlated with:

```text
Affected CA
+
Authentication Template
+
Suspicious Identity Information
```

---

# Directory Service Changes

Certificate-template and PKI object modifications in Active Directory can produce:

```text
5136
```

where appropriate Directory Service Changes auditing is enabled.

ESC16 itself is primarily CA-local configuration, so do not rely on 5136 to detect the CA registry change.

---

# Certificate Authentication

Kerberos certificate authentication can contribute to:

```text
4768
```

telemetry.

Correlate suspicious certificate issuance with subsequent TGT requests.

---

# Detection Model

```text
CA Configuration Change
       |
       v
SID Extension Disabled
       |
       v
Authentication Certificate Issued
       |
       v
Certificate Authentication
       |
       v
Sensitive Account Activity
```

---

# Existing ESC16 Detection

Do not only monitor future changes.

Perform recurring posture assessment for:

```text
Existing ESC16
```

because the configuration may have existed for years before monitoring was deployed.

---

# Certipy Defensive Use

Certipy can be used defensively to identify:

```text
ESC16
```

during periodic PKI reviews.

A practical workflow is:

```text
certipy find
      |
      v
ESC16 Candidate
      |
      v
Native CA Configuration Review
      |
      v
Certificate Inspection
```

---

# BloodHound

BloodHound can provide useful context around:

```text
CA Relationships
Enrollment
Template Exposure
Principal Privileges
```

but direct CA configuration validation remains important for ESC16.

Do not rely on graph data alone.

---

# Incident Response

If malicious ESC16 configuration is suspected:

```text
Preserve CA Configuration
       |
       v
Determine Change Time
       |
       v
Identify Actor
       |
       v
Identify Certificates Issued
       |
       v
Identify Authentication Use
       |
       v
Restore Secure Configuration
```

---

# Preserve Evidence

Record:

```text
CA Name
CA Host
DisableExtensionList
Registry Path
Windows Build
Patch Level
Certificate Services Logs
Administrative Logons
EDR Timeline
```

before changing the configuration.

---

# Determine When ESC16 Was Introduced

Establish:

```text
When was the SID extension disabled?
```

This defines the certificate-issuance exposure window.

Potential sources include:

```text
EDR
Registry Auditing
Configuration Management
Change Tickets
System Backups
CA Backups
Administrative Logs
```

---

# Review Certificates Issued During Exposure

Identify certificates issued while ESC16 was active.

Prioritise:

```text
Authentication Certificates
Privileged Users
Computer Certificates
Domain Controllers
Service Accounts
Enrollment Agents
```

---

# Inspect Certificate Identity

For suspicious certificates, record:

```text
Subject
SAN
UPN
DNS Name
Issuer
Serial Number
Template
Application Policies
EKUs
SID Security Extension
```

---

# Review ESC6 Exposure

If ESC6 was also enabled during the same period:

```text
ESC6 + ESC16
```

should receive high-priority investigation.

Search for suspicious SAN identity information.

---

# Review UPN Changes

Historical ESC16 exploitation paths can involve:

```text
userPrincipalName
```

modification.

Search for suspicious UPN changes during the exposure period.

---

# Review ACL Abuse

Determine whether attackers had rights such as:

```text
GenericWrite
GenericAll
WriteProperty
```

over accounts whose identity attributes were modified.

---

# Review Certificate Authentication

Correlate suspicious certificates with:

```text
4768
```

and other authentication telemetry.

---

# Revoke Malicious Certificates

If suspicious certificates are identified:

```text
Revoke Certificate
       |
       v
Publish Updated CRL
       |
       v
Verify Revocation Distribution
```

---

# Restore the Security Extension

After evidence preservation and change approval, restore normal SID security extension issuance.

Then validate using a dedicated test certificate.

---

# Validate Remediation

The remediation validation model is:

```text
Remove SID OID from Disabled List
       |
       v
Apply Required Service Change
       |
       v
Request Test Certificate
       |
       v
Inspect Certificate
       |
       v
SID Security Extension Present
```

---

# Reassess All Templates

After fixing ESC16:

```text
Do Not Stop
```

Individual templates may still expose:

```text
ESC1
ESC2
ESC3
ESC4
ESC9
ESC15
```

or other AD CS weaknesses.

---

# Reporting ESC16

Avoid a title containing only:

```text
ESC16
```

Prefer a descriptive title.

Examples:

```text
Certification Authority Globally Disables the Active Directory SID Security Extension
```

```text
AD CS Certificate Issuance Lacks Strong SID Binding
```

```text
CA-Wide Configuration Suppresses the NTDS SID Security Extension
```

---

# Example Finding

```text
Finding:
Certification Authority Globally Disables the Active Directory SID
Security Extension

Affected CA:
CORP-CA01

Affected Host:
ca01.corp.example

AD CS Technique:
ESC16

Disabled Extension:
1.3.6.1.4.1.311.25.2

Description:
The Certification Authority is configured to suppress the Microsoft
NTDS CA security extension from certificates it issues.

The affected OID is:

1.3.6.1.4.1.311.25.2

This extension contains the Active Directory SID information used
for strong certificate-to-account binding.

The OID is present in the CA policy module's DisableExtensionList,
causing the security extension to be omitted at the CA level rather
than only from a specific certificate template.

As a result, authentication-capable certificates issued by the CA
may lack the normal SID security extension regardless of whether
their certificate templates are individually configured to include
it.

Impact:
The configuration weakens certificate-to-account identity binding
across certificates issued by the affected CA.

The practical privilege-escalation impact depends on additional
conditions including certificate enrollment permissions, certificate
mapping behaviour, identity-control permissions and other AD CS
configuration such as ESC6.

Where additional certificate identity manipulation paths exist, the
condition can contribute to certificate-based account impersonation.

Recommendation:
Remove OID 1.3.6.1.4.1.311.25.2 from the CA policy module's
DisableExtensionList using an approved PKI change process.

Ensure the CA and domain controllers are fully patched.

After remediation, issue a certificate to a dedicated test identity
and verify that the SID security extension is present.

Review authentication-capable templates published by the affected
CA and assess the environment for related ESC6, ESC9, ESC10 and
certificate-mapping weaknesses.
```

---

# Severity

Severity should reflect the complete environment.

Do not assign:

```text
Critical
```

solely because:

```text
Certipy Reports ESC16
```

Consider:

```text
Who Can Enroll?
What Templates Authenticate?
Is ESC6 Present?
Can Identity Attributes Be Modified?
What Mapping Paths Exist?
How Privileged Are the Reachable Targets?
```

---

# Lower-Risk Example

```text
ESC16 CA
   |
   v
Only Restricted Non-Authentication Templates
   |
   v
Administrators Only
```

Still a security-hardening concern, but the immediate attack path may be limited.

---

# Higher-Risk Example

```text
ESC16 CA
   |
   v
Domain Users Can Enroll
   |
   v
Authentication-Capable Template
   |
   v
Additional Identity Manipulation
```

This warrants deeper investigation.

---

# Critical Chain Example

```text
Low-Privilege User
       |
       v
Authentication Template
       |
       v
ESC6 + ESC16 CA
       |
       v
Attacker-Controlled Identity
       |
       v
Certificate Authentication
       |
       v
Privileged Principal
```

A demonstrated path to a Tier 0 identity can represent critical impact.

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
CA Type
Policy Module
DisableExtensionList
SID Security Extension OID
Published Templates
Authentication-Capable Templates
Template EKUs
Template Enrollment Rights
ESC6 State
ESC9 Templates
ESC10 Conditions
ESC14 Explicit Mappings
Certificate Subject
Certificate SAN
Certificate Template
Certificate Serial Number
Certificate SID Extension
Domain Controller Patch State
Certificate Mapping Behaviour
Validation Method
Cleanup Result
```

---

# ESC16 Assessment Checklist

## Discovery

- [ ] Identify all Enterprise CAs
- [ ] Identify CA hostnames
- [ ] Identify CA operating systems
- [ ] Identify CA builds
- [ ] Identify CA patch levels
- [ ] Identify CA policy modules
- [ ] Enumerate `DisableExtensionList`
- [ ] Search for `1.3.6.1.4.1.311.25.2`
- [ ] Identify legacy unpatched CAs

## CA Analysis

- [ ] Confirm ESC16 on each CA separately
- [ ] Determine whether SID extension is globally disabled
- [ ] Determine whether missing support is caused by obsolete patch level
- [ ] Record exact configuration
- [ ] Review CA administrators
- [ ] Review CA permissions
- [ ] Review local administrative access
- [ ] Review CA change history

## Template Analysis

- [ ] Enumerate published templates
- [ ] Identify authentication-capable templates
- [ ] Identify Client Authentication
- [ ] Identify Smart Card Logon
- [ ] Identify PKINIT Client Authentication
- [ ] Identify Any Purpose
- [ ] Identify templates with no restrictive EKU
- [ ] Review enrollment rights
- [ ] Identify broadly enrollable templates
- [ ] Identify ESC9 templates
- [ ] Identify ESC1 templates
- [ ] Identify ESC4 conditions

## Related AD CS Analysis

- [ ] Review ESC6
- [ ] Review ESC9
- [ ] Review ESC10
- [ ] Review ESC14
- [ ] Review ESC5
- [ ] Review explicit mappings
- [ ] Review certificate identity manipulation
- [ ] Review Enrollment Agent exposure

## Modern Mapping Analysis

- [ ] Review KB5014754
- [ ] Verify DC patch state
- [ ] Use current strong-binding assumptions
- [ ] Do not rely on historical compatibility mode
- [ ] Distinguish SID security extension from SAN SID URL
- [ ] Determine whether a valid strong mapping path exists
- [ ] Document legacy systems separately

## Windows Enumeration

- [ ] Run `certutil -getreg policy\DisableExtensionList`
- [ ] Record CA name
- [ ] Review registry configuration
- [ ] Enumerate published templates
- [ ] Enumerate template EKUs
- [ ] Review CA patch state
- [ ] Inspect dedicated test certificate

## Linux Enumeration

- [ ] Verify Certipy version
- [ ] Run authorised `certipy find`
- [ ] Identify ESC16 output
- [ ] Record disabled extensions
- [ ] Enumerate affected CA
- [ ] Enumerate published templates
- [ ] Identify authentication templates
- [ ] Confirm results with native configuration where possible

## Certificate Validation

- [ ] Use dedicated test identity
- [ ] Use normal authorised template
- [ ] Request certificate only where approved
- [ ] Inspect certificate
- [ ] Search for SID security extension
- [ ] Record template
- [ ] Record issuer
- [ ] Record serial number
- [ ] Do not impersonate privileged account
- [ ] Revoke test certificate if required

## Safe Testing

- [ ] Prefer read-only validation
- [ ] Do not enable ESC6
- [ ] Do not disable SID extension
- [ ] Do not weaken DC mapping
- [ ] Do not modify privileged UPNs
- [ ] Do not target Domain Admin
- [ ] Do not restart production CA without approval
- [ ] Use dedicated test identities
- [ ] Preserve original configuration
- [ ] Verify cleanup

## Detection

- [ ] Baseline `DisableExtensionList`
- [ ] Monitor CA registry
- [ ] Monitor CA administrative activity
- [ ] Monitor configuration management drift
- [ ] Monitor Certificate Services events
- [ ] Monitor 4886 where configured
- [ ] Monitor 4887 where configured
- [ ] Monitor certificate authentication
- [ ] Monitor 4768
- [ ] Monitor suspicious SAN values
- [ ] Monitor UPN changes
- [ ] Monitor template changes
- [ ] Periodically rerun PKI posture assessment

## Hardening

- [ ] Remove SID OID from `DisableExtensionList`
- [ ] Preserve unrelated legitimate entries
- [ ] Use approved PKI change process
- [ ] Patch CA
- [ ] Patch domain controllers
- [ ] Review ESC6
- [ ] Review ESC9
- [ ] Review authentication templates
- [ ] Restrict enrollment
- [ ] Review CA administration
- [ ] Replace insecure legacy compatibility workarounds
- [ ] Validate SID extension after remediation

## Incident Response

- [ ] Preserve CA configuration
- [ ] Determine ESC16 exposure period
- [ ] Identify configuration actor
- [ ] Review CA administrator activity
- [ ] Review certificates issued during exposure
- [ ] Prioritise authentication certificates
- [ ] Review ESC6 during exposure
- [ ] Review suspicious SANs
- [ ] Review UPN modifications
- [ ] Review certificate authentication
- [ ] Review privileged activity
- [ ] Revoke malicious certificates
- [ ] Publish updated revocation information
- [ ] Restore secure CA configuration
- [ ] Patch legacy systems
- [ ] Validate remediation

## Reporting

- [ ] Use descriptive title
- [ ] Identify exact CA
- [ ] Identify exact OID
- [ ] Explain SID security extension
- [ ] Explain CA-wide scope
- [ ] Distinguish ESC16 from ESC9
- [ ] Document authentication templates
- [ ] Document enrollment rights
- [ ] Document ESC6 state
- [ ] Explain modern strong-mapping context
- [ ] Separate configuration weakness from demonstrated exploitation
- [ ] Provide specific remediation
- [ ] Avoid unnecessary active exploitation

---

# ESC16 Testing Model

The secure model is:

```text
Certificate Request
       |
       v
Enterprise CA
       |
       v
SID Security Extension
       |
       v
Issued Certificate
       |
       v
Strong Identity Binding
```

The ESC16 model is:

```text
Certificate Request
       |
       v
Enterprise CA
       |
       v
DisableExtensionList
       |
       v
SID Extension Suppressed
       |
       v
Certificate Without SID Extension
```

The ESC9 comparison is:

```text
ESC9
 |
 v
Template-Level
SID Suppression
```

versus:

```text
ESC16
 |
 v
CA-Level
SID Suppression
```

The scope difference is:

```text
ESC9
 |
 v
One Vulnerable Template
```

versus:

```text
ESC16
 |
 v
CA
 |
 +--> Template A
 +--> Template B
 +--> Template C
 +--> Template D
 |
 v
All Potentially Affected
```

The modern attack analysis is:

```text
ESC16
   |
   v
SID Extension Missing
   |
   v
Identity Manipulation Available?
   |
   +--> No
   |
   +--> Yes
          |
          v
Strong Mapping Path Available?
          |
          +--> No
          |
          +--> Yes
                 |
                 v
          Certificate Impersonation
```

The ESC6 relationship is:

```text
ESC6
 |
 v
Attacker Controls SAN
 |
 +-------------------+
                     |
ESC16                |
 |                   |
 v                   |
Normal SID Missing   |
 |                   |
 +---------+---------+
           |
           v
Attacker-Controlled
Certificate Identity
```

The assessment model is:

```text
Identify CA
    |
    v
Check DisableExtensionList
    |
    v
ESC16 Present?
    |
    +--> No -> Continue AD CS Review
    |
    +--> Yes
            |
            v
     Enumerate Templates
            |
            v
     Authentication Templates?
            |
            v
     Who Can Enroll?
            |
            v
     ESC6 / Mapping Conditions?
            |
            v
       Determine Impact
```

The safe-validation model is:

```text
Read CA Configuration
       |
       v
Confirm SID OID Disabled
       |
       v
Enumerate Templates
       |
       v
Assess Enrollment Rights
       |
       v
Evidence Sufficient?
       |
       +--> Yes -> Report
       |
       +--> No
               |
               v
        Dedicated Test User
               |
               v
        Normal Test Certificate
               |
               v
        Inspect Extension
```

The detection model is:

```text
CA Configuration
      |
      v
SID Extension Disabled
      |
      v
Certificate Issuance
      |
      v
Certificate Authentication
      |
      v
Account Activity
```

The remediation model is:

```text
Preserve Configuration
       |
       v
Remove SID OID from
DisableExtensionList
       |
       v
Apply Required Service Change
       |
       v
Issue Test Certificate
       |
       v
Verify SID Extension
```

The defensive model is:

```text
SID Extension Enabled
       +
Patched CA
       +
Patched DCs
       +
Secure Templates
       +
Restricted Enrollment
       +
Secure Certificate Mapping
       =
Strong Certificate Identity
```

For penetration testers:

```text
Do Not Ask:
"Can I manipulate Administrator and
authenticate with a forged identity?"

Ask:
"Can I prove that the CA globally
suppresses the SID security extension,
identify the affected authentication
templates, and establish the relevant
attack prerequisites?"
```

For defenders:

```text
Do Not Assume:
"Our templates are secure, therefore
certificates contain strong SID binding."

Ask:
"Does the CA itself suppress the
security extension regardless of the
template configuration?"
```

The complete ESC16 relationship is:

```text
Certification Authority
        |
        v
DisableExtensionList
        |
        v
1.3.6.1.4.1.311.25.2
        |
        v
SID Security Extension Disabled
        |
        v
Certificates Lack Normal SID Binding
        |
        v
Certificate Mapping Attack Surface
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC6:

[AD CS ESC6](esc6.md)

ESC9:

[AD CS ESC9](esc9.md)

ESC10:

[AD CS ESC10](esc10.md)

ESC14:

[AD CS ESC14](esc14.md)

ESC15:

[AD CS ESC15](esc15.md)

ACLs and ACEs:

[ACL and ACE](../acl-ace.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs/esc17.md
```

---

# References

## Microsoft - KB5014754

[Microsoft - KB5014754 Certificate-Based Authentication Changes on Windows Domain Controllers](https://support.microsoft.com/help/5014754){ target="_blank" rel="noopener noreferrer" }

Microsoft documents the certificate-binding changes introduced after CVE-2022-26923, including strong certificate mapping and the SID security extension.

The current enforcement timeline is important when evaluating historical ESC9 and ESC16 attack paths.

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Certipy - Privilege Escalation

[Certipy Wiki - Privilege Escalation](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation){ target="_blank" rel="noopener noreferrer" }

Certipy documents ESC16 as:

```text
Security Extension Disabled on CA Globally
```

and identifies the relevant extension as:

```text
1.3.6.1.4.1.311.25.2
```

Certipy can identify the condition through the CA's disabled-extension configuration.

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Current Certipy releases support enumeration of modern AD CS ESC conditions.

Always verify the installed version:

```bash
certipy --version
certipy find -h
```

before relying on command syntax or output format.

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

Certified Pre-Owned provides the foundational research for Active Directory Certificate Services privilege-escalation techniques.

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC16 demonstrates why AD CS assessment cannot stop at:

```text
Certificate Templates
```

A template may appear correctly configured while the issuing CA itself changes the resulting certificate.

The normal security model is:

```text
Template
   |
   v
Certificate Request
   |
   v
CA
   |
   v
SID Security Extension
   |
   v
Strongly Bound Certificate
```

ESC16 changes this to:

```text
Template
   |
   v
Certificate Request
   |
   v
ESC16 CA
   |
   v
SID Extension Removed
   |
   v
Certificate Without Normal SID Binding
```

The most important distinction is:

```text
ESC9 = Template-Level
```

and:

```text
ESC16 = CA-Level
```

This means an ESC16 assessment must expand from:

```text
Which Template Is Vulnerable?
```

to:

```text
Which Templates Are Published
by the Vulnerable CA?
```

Every authentication-capable template on the affected CA becomes relevant to the analysis.

However, ESC16 should not automatically be reported as:

```text
Domain Compromise
```

The practical impact depends on additional conditions.

In a modern environment, evaluate:

```text
ESC16
   +
Enrollment Rights
   +
Authentication Template
   +
Identity Manipulation
   +
ESC6 / Other Certificate Weakness
   +
Current Mapping Behaviour
```

A particularly important combination is:

```text
ESC6 + ESC16
```

because:

```text
ESC6
```

can allow requester-controlled SAN information while:

```text
ESC16
```

removes the normal CA-generated SID security extension.

The defensive priority is straightforward:

```text
The SID security extension should not
be globally suppressed without a
well-understood and justified reason.
```

If it was disabled as a historical compatibility workaround:

```text
Identify the Compatibility Problem
        |
        v
Fix the Underlying Mapping
        |
        v
Restore the SID Security Extension
```

Do not preserve an insecure global workaround indefinitely.

For penetration testers, read-only proof is usually enough:

```text
DisableExtensionList
        |
        v
Contains
1.3.6.1.4.1.311.25.2
        |
        v
Affected CA
        |
        v
Authentication Templates
        |
        v
Relevant Enrollment Rights
```

There is normally no need to manipulate a privileged account or weaken another security control.

For defenders, ESC16 reinforces the broader AD CS principle:

```text
Certificate Security
      =
Template Security
      +
CA Security
      +
Certificate Mapping Security
      +
Active Directory Security
```

All four layers must be reviewed together.
