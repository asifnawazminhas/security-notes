# AD CS ESC17 - Enrollee-Supplied Subject for Server Authentication

ESC17 is an Active Directory Certificate Services (AD CS) abuse condition where a certificate template allows a requester to supply arbitrary subject information while the resulting certificate is valid for:

```text
Server Authentication
```

The technique is closely related to ESC1, but the security objective is different.

ESC1 focuses primarily on:

```text
Client Authentication
        |
        v
Impersonate a User or Computer
```

ESC17 focuses on:

```text
Server Authentication
        |
        v
Impersonate a Server or Service
```

Conceptually:

```text
Low-Privilege User
        |
        v
Vulnerable Certificate Template
        |
        +--> Enrollee Supplies Subject
        |
        +--> Server Authentication
        |
        +--> Low-Privilege Enrollment
        |
        +--> No Manager Approval
        |
        +--> No Authorised Signatures
        |
        v
Certificate for Arbitrary DNS Name
        |
        v
Impersonate Internal TLS Service
```

A commonly discussed example is impersonation of an internal:

```text
WSUS
```

server.

However, ESC17 is not inherently a WSUS vulnerability.

The underlying problem is broader:

```text
Can an untrusted requester obtain
a server-authentication certificate
for a DNS identity they do not own?
```

If the answer is yes, the certificate can potentially be used against any suitable TLS service where the attacker can also redirect, intercept or otherwise influence client connectivity.

!!! warning "Authorised testing only"
    ESC17 can result in certificates capable of impersonating trusted internal servers. During production assessments, begin with read-only template enumeration. If certificate issuance must be demonstrated, use a dedicated test DNS name and test service. Do not impersonate production WSUS, management, authentication, update, proxy or other critical infrastructure without explicit approval.

---

# ESC17 at a Glance

The normal server-certificate model is:

```text
Server Administrator
        |
        v
Certificate Request
        |
        v
Identity = Server They Control
        |
        v
CA
        |
        v
Server Authentication Certificate
```

ESC17 changes the trust boundary:

```text
Low-Privilege User
        |
        v
Supply in Request
        |
        v
DNS = arbitrary.corp.example
        |
        v
CA
        |
        v
Valid Server Certificate
for Arbitrary DNS Name
```

The certificate itself may be cryptographically legitimate.

The problem is:

```text
The requester was not authorised
to represent that server identity.
```

---

# ESC17 Core Concept

ESC17 combines two important properties:

```text
Requester Controls Identity
```

and:

```text
Certificate Can Authenticate a Server
```

Together:

```text
Requester-Controlled DNS Identity
            +
Server Authentication EKU
            =
Potential Server Impersonation
```

---

# ESC17 Preconditions

A typical vulnerable template has:

```text
Enrollee Supplies Subject = True

Server Authentication = Present

Low-Privilege Principal Can Enroll

Manager Approval = False

Authorised Signatures = 0

Template = Published
```

The full attack path additionally requires:

```text
Useful Target Service

Client Trusts Issuing CA

Traffic Can Reach Attacker

No Effective Certificate Pinning

Protocol / Application Can Be Abused
```

Therefore:

```text
Vulnerable Template
```

does not automatically mean:

```text
Immediate Domain Compromise
```

---

# Condition 1 - Enrollee Supplies Subject

The critical certificate-template setting is:

```text
Supply in the request
```

Internally this is associated with:

```text
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT
```

in:

```text
msPKI-Certificate-Name-Flag
```

This allows the requester to provide certificate identity information.

---

# Why Supply in the Request Exists

The setting is not inherently malicious.

It is common for certificate templates intended for services where the CA cannot automatically determine all required DNS identities.

For example:

```text
Web Server
```

may require certificates containing:

```text
www.corp.example
api.corp.example
portal.corp.example
```

The certificate requester may therefore need to specify:

```text
Subject Alternative Names
```

The vulnerability arises when this capability is exposed to principals that should not be allowed to claim arbitrary server identities.

---

# Subject Alternative Name

For server authentication, the most important identity is usually the:

```text
DNS Subject Alternative Name
```

For example:

```text
DNS:portal.corp.example
```

or:

```text
DNS:wsus.corp.example
```

Modern TLS clients generally validate the hostname against the certificate's SAN.

---

# Example Certificate Identity

A certificate may contain:

```text
Subject:
CN=wsus.corp.example

Subject Alternative Name:
DNS Name=wsus.corp.example

Extended Key Usage:
Server Authentication
```

If the certificate chains to an Enterprise CA trusted by domain systems, clients may accept it as a legitimate certificate for that server.

---

# Condition 2 - Server Authentication

The relevant EKU is:

```text
Server Authentication
```

OID:

```text
1.3.6.1.5.5.7.3.1
```

This indicates that the certificate can be used to authenticate the server side of a TLS connection.

---

# Server Authentication OID

```text
1.3.6.1.5.5.7.3.1
```

During enumeration, search for:

```text
Server Authentication
```

or the OID directly.

---

# Condition 3 - Enrollment Rights

An attacker must be able to request a certificate from the template.

Potentially dangerous enrollment principals include:

```text
Authenticated Users
Domain Users
Domain Computers
Everyone
Large Departmental Groups
```

The effective security question is:

```text
Can a Low-Privilege Principal
Enroll for This Template?
```

---

# Condition 4 - No Manager Approval

A template requiring:

```text
CA Certificate Manager Approval
```

introduces a manual approval stage.

The simple attack path becomes:

```text
Attacker Request
      |
      v
Pending
      |
      v
Certificate Manager Review
```

rather than:

```text
Attacker Request
      |
      v
Certificate Issued
```

---

# Condition 5 - No Authorised Signatures

Certificate templates can require authorised signatures before issuance.

For the straightforward ESC17 path:

```text
Authorised Signatures Required = 0
```

is expected.

---

# Condition 6 - Template Is Published

A certificate template stored in Active Directory cannot normally be used for enrollment unless an Enterprise CA publishes it.

Conceptually:

```text
Template Exists
      |
      v
Published by CA?
      |
      +--> No -> No Normal Enrollment
      |
      +--> Yes -> Continue Analysis
```

---

# Condition 7 - Client Trusts the CA

A forged server identity is only useful if the client accepts the certificate chain.

In an Active Directory environment, Enterprise CA certificates are often distributed into trusted certificate stores.

Conceptually:

```text
Attacker Certificate
      |
      v
Issued by CORP-CA
      |
      v
Client Trusts CORP-CA
      |
      v
TLS Certificate Accepted
```

---

# Condition 8 - Traffic Influence

Possessing a certificate does not automatically redirect traffic.

The attacker also needs some mechanism causing the client to connect to infrastructure controlled by the attacker.

Examples may involve:

```text
DNS
Proxy Configuration
Routing
Service Configuration
Name Resolution
Application Configuration
Network Position
```

These are separate attack prerequisites.

---

# Important Security Boundary

ESC17 gives:

```text
Certificate Identity
```

It does not automatically give:

```text
Network Position
```

The complete attack requires both.

---

# ESC17 Attack Model

```text
Vulnerable Template
       |
       v
Arbitrary Server Certificate
       |
       v
Traffic Redirection / Interception
       |
       v
Client Establishes TLS
       |
       v
Certificate Accepted
       |
       v
Server Impersonation
```

---

# Why Server Impersonation Matters

Many enterprise applications assume:

```text
TLS Certificate Valid
=
Server Is Trusted
```

If an attacker can obtain a legitimate certificate for the expected server name, that assumption may fail.

Potential consequences depend entirely on the protocol.

They can include:

```text
Credential Exposure
Authentication Relay Opportunities
Sensitive Data Disclosure
Malicious Configuration Delivery
Software Distribution Abuse
Service Impersonation
```

---

# ESC17 and WSUS

One important ESC17 scenario involves:

```text
Windows Server Update Services
```

or:

```text
WSUS
```

WSUS is used by organisations to distribute Microsoft updates internally.

Conceptually:

```text
Windows Client
      |
      v
Internal WSUS Server
      |
      v
Update Metadata / Content
```

If the organisation uses TLS to protect WSUS communication, clients rely on the certificate presented by the configured WSUS service.

---

# ESC17 WSUS Concept

A conceptual ESC17 chain is:

```text
Low-Privilege User
       |
       v
ESC17 Template
       |
       v
Certificate for
wsus.corp.example
       |
       v
Traffic Redirected
       |
       v
Client Connects to Attacker
       |
       v
TLS Certificate Accepted
       |
       v
Attacker Impersonates WSUS
```

The exact impact depends heavily on WSUS configuration and additional security controls.

---

# ESC17 Is Not "WSUS = Vulnerable"

Do not report:

```text
WSUS Present
=
ESC17 Exploitable
```

You must establish:

```text
Vulnerable Template
        +
Enrollment
        +
Arbitrary DNS Certificate
        +
Trusted CA
        +
Reachable Target Service
        +
Traffic Influence
        +
Useful Protocol Behaviour
```

---

# Other Potential Services

ESC17 is not conceptually restricted to WSUS.

Other TLS services could potentially matter if:

```text
1. Client validates a DNS identity

2. Enterprise CA is trusted

3. Attacker can influence traffic

4. Service protocol provides useful impact
```

Examples could include internal:

```text
HTTPS Applications
Management Services
Software Distribution Systems
Configuration Services
Proxies
APIs
Custom Enterprise Applications
```

Each must be assessed individually.

---

# Certificate Pinning

Certificate pinning can significantly affect ESC17.

A client may require:

```text
Specific Certificate
```

or:

```text
Specific Public Key
```

rather than merely:

```text
Any Certificate from Trusted CA
for Correct DNS Name
```

Conceptually:

```text
ESC17 Certificate
       |
       v
Correct DNS Name
       |
       v
Trusted CA
       |
       v
Pinned Certificate?
       |
       +--> Yes -> Attack May Fail
       |
       +--> No -> Continue Analysis
```

---

# Mutual TLS

Some services use:

```text
Mutual TLS
```

where both:

```text
Client
```

and:

```text
Server
```

authenticate using certificates.

ESC17 provides potential server identity.

It does not automatically provide:

```text
Valid Client Authentication
```

unless the certificate contains suitable additional purposes and the protocol accepts them.

---

# ESC17 vs ESC1

ESC1:

```text
Enrollee Supplies Subject
        +
Client Authentication
        =
Client Identity Impersonation
```

ESC17:

```text
Enrollee Supplies Subject
        +
Server Authentication
        =
Server Identity Impersonation
```

---

# ESC1 Target

Typical ESC1 thinking:

```text
Administrator
Domain Admin
Computer Account
Service Account
```

The attacker wants to become:

```text
A Client Principal
```

---

# ESC17 Target

Typical ESC17 thinking:

```text
WSUS Server
Management Server
Internal Web Server
Software Distribution Server
```

The attacker wants to become:

```text
A Server
```

---

# Template May Be ESC1 and ESC17

A template may contain both:

```text
Client Authentication
```

and:

```text
Server Authentication
```

while allowing:

```text
Enrollee Supplies Subject
```

Such a template may expose:

```text
ESC1
```

and:

```text
ESC17
```

simultaneously.

---

# Prioritise ESC1 When Appropriate

If a template already permits direct privileged client impersonation through ESC1:

```text
ESC1
```

may provide a more direct Active Directory privilege-escalation path than server impersonation.

Still record the server-authentication exposure where relevant because it represents a separate trust boundary.

---

# ESC17 vs ESC2

ESC2 concerns:

```text
Any Purpose
```

or:

```text
No EKU
```

templates.

Such certificates may have broad usage.

ESC17 specifically identifies templates with server-authentication capability combined with requester-controlled identity.

---

# ESC17 vs ESC3

ESC3 concerns:

```text
Certificate Request Agent
```

and enrollment-on-behalf-of workflows.

ESC17 concerns:

```text
Server Authentication
```

and server impersonation.

---

# ESC17 vs ESC4

ESC4 concerns:

```text
Dangerous Template ACLs
```

An attacker with template-write rights may potentially modify a template to create ESC17-like conditions.

The root cause in that situation is:

```text
ESC4
```

followed by a template configuration change.

---

# ESC17 vs ESC6

ESC6 concerns a CA-wide configuration:

```text
EDITF_ATTRIBUTESUBJECTALTNAME2
```

which can allow SAN values supplied through request attributes.

ESC17 concerns:

```text
Certificate Template
```

configuration permitting enrollee-supplied subject information for a server-authentication certificate.

Both involve requester-controlled identity but at different layers.

---

# ESC17 vs ESC15

ESC15 concerns:

```text
Arbitrary Application Policies
```

under vulnerable CVE-2024-49019 conditions.

ESC17 concerns:

```text
Server Authentication
```

already being authorised by the certificate template.

The ESC17 issue is therefore not dependent on CVE-2024-49019.

---

# ESC17 vs ESC16

ESC16 concerns:

```text
CA-Wide SID Security Extension Suppression
```

This primarily affects certificate-to-account mapping.

ESC17 focuses on:

```text
TLS Server Identity
```

where DNS SAN validation is usually central.

Therefore ESC17 is conceptually distinct from SID-based user/computer mapping attacks.

---

# Enumerating ESC17 with Certipy

Current Certipy versions support ESC17 identification.

First check the installed version:

```bash
certipy --version
```

Review current options:

```bash
certipy find -h
```

A typical authorised enumeration is:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

---

# Certipy Indicators

Look for output containing:

```text
Enrollee Supplies Subject : True
```

and:

```text
Extended Key Usage
    Server Authentication
```

together with:

```text
Requires Manager Approval : False
```

and:

```text
Authorized Signatures Required : 0
```

and low-privilege enrollment rights.

Current Certipy versions may explicitly flag:

```text
ESC17
```

---

# Example Certipy Interpretation

Conceptually:

```text
Template Name:
InternalWebServer

Enrollee Supplies Subject:
True

Extended Key Usage:
Server Authentication

Requires Manager Approval:
False

Authorized Signatures Required:
0

Enrollment Rights:
CORP\Domain Users

Vulnerabilities:
ESC17
```

This is a strong candidate.

---

# Do Not Stop at the Scanner Label

After Certipy identifies ESC17, determine:

```text
Which CA publishes the template?

Who can enroll?

What DNS names can be requested?

Which services could be impersonated?

Does the client trust the CA?

Can traffic actually be influenced?

Does the service use certificate pinning?

What is the realistic impact?
```

---

# Windows Enumeration

PowerShell can be used for read-only certificate-template enumeration.

Import Active Directory:

```powershell
Import-Module ActiveDirectory
```

Retrieve the Configuration naming context:

```powershell
$configNC = (Get-ADRootDSE).configurationNamingContext
```

Build the template path:

```powershell
$templateBase = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$configNC"
```

---

# Enumerate Certificate Templates

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties displayName,msPKI-Certificate-Name-Flag,pKIExtendedKeyUsage |
    Select-Object Name,displayName,msPKI-Certificate-Name-Flag,pKIExtendedKeyUsage
```

---

# Find Server Authentication Templates

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties displayName,msPKI-Certificate-Name-Flag,pKIExtendedKeyUsage |
    Where-Object {
        $_.pKIExtendedKeyUsage -contains '1.3.6.1.5.5.7.3.1'
    } |
    Select-Object Name,displayName,msPKI-Certificate-Name-Flag,pKIExtendedKeyUsage
```

---

# Review Name Flags

For a target template:

```powershell
Get-ADObject -SearchBase $templateBase -LDAPFilter '(cn=InternalWebServer)' -Properties msPKI-Certificate-Name-Flag |
    Select-Object Name,msPKI-Certificate-Name-Flag
```

Determine whether:

```text
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT
```

is enabled.

---

# Enumerate Publishing CAs

Build the Enrollment Services path:

```powershell
$caBase = "CN=Enrollment Services,CN=Public Key Services,CN=Services,$configNC"
```

Enumerate:

```powershell
Get-ADObject -SearchBase $caBase -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties dNSHostName,certificateTemplates |
    Select-Object Name,dNSHostName,certificateTemplates
```

---

# Correlate Template to CA

The important relationship is:

```text
Template
   |
   v
Published By
   |
   v
Enterprise CA
```

A vulnerable template that is not published does not provide a normal enrollment path.

---

# Template ACL Review

Retrieve the template:

```powershell
$template = Get-ADObject -SearchBase $templateBase -LDAPFilter '(cn=InternalWebServer)'
```

Inspect ACL:

```powershell
Get-Acl "AD:$($template.DistinguishedName)" |
    Format-List Owner,AccessToString
```

Review which principals receive:

```text
Enroll
Autoenroll
GenericAll
GenericWrite
WriteDACL
WriteOwner
```

---

# Linux LDAP Enumeration

From an authorised Linux host:

```bash
ldapsearch -LLL -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\audit-user' \
    -W \
    -b 'CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=corp,DC=example' \
    '(objectClass=pKICertificateTemplate)' \
    cn \
    displayName \
    msPKI-Certificate-Name-Flag \
    pKIExtendedKeyUsage
```

---

# Search Server Authentication OID

The important OID is:

```text
1.3.6.1.5.5.7.3.1
```

Filter the LDAP output or query templates containing the OID.

---

# Enumerate CAs from Linux

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

# Safe Certificate Validation

If active validation is authorised, use:

```text
Dedicated Test DNS Name
```

For example:

```text
esc17-test.corp.example
```

rather than:

```text
wsus.corp.example
```

or another real production service.

---

# Controlled Test Model

```text
Test User
   |
   v
ESC17 Template
   |
   v
DNS:
esc17-test.corp.example
   |
   v
Certificate
   |
   v
Inspect Only
```

This proves that the requester can control a server identity without impersonating a production system.

---

# Certificate Request

Current Certipy supports specifying a DNS identity during an authorised certificate request.

The conceptual syntax is:

```bash
certipy req \
    -u 'audit-user@corp.example' \
    -p 'PASSWORD' \
    -dc-ip 10.10.10.10 \
    -target 'ca01.corp.example' \
    -ca 'CORP-CA' \
    -template 'InternalWebServer' \
    -dns 'esc17-test.corp.example'
```

Always confirm the syntax for the installed version:

```bash
certipy req -h
```

---

# What This Test Proves

A successful request can establish:

```text
Low-Privilege User
       |
       v
Controls DNS SAN
       |
       v
Receives Certificate
       |
       v
Server Authentication
```

That is sufficient to demonstrate the certificate-template trust failure.

---

# What This Test Does Not Prove

It does not automatically establish:

```text
WSUS Compromise
```

or:

```text
Credential Theft
```

or:

```text
Domain Compromise
```

Those require additional attack prerequisites.

---

# Inspect the Certificate

Windows:

```cmd
certutil -dump esc17-test.cer
```

Review:

```text
Subject
Subject Alternative Name
Enhanced Key Usage
Certificate Template
Issuer
Validity
```

---

# OpenSSL Inspection

For PEM:

```bash
openssl x509 -in esc17-test.pem -text -noout
```

For DER:

```bash
openssl x509 -in esc17-test.cer -inform DER -text -noout
```

---

# Expected Evidence

Useful evidence might show:

```text
Requester:
CORP\audit-user

Template:
InternalWebServer

SAN:
DNS Name=esc17-test.corp.example

EKU:
TLS Web Server Authentication

Issuer:
CORP-CA
```

This demonstrates the core ESC17 issue without targeting a production server.

---

# Avoid Real Server Names During Initial Validation

Do not begin with:

```text
wsus.corp.example
```

```text
sccm.corp.example
```

```text
vpn.corp.example
```

```text
adfs.corp.example
```

```text
portal.corp.example
```

Use an approved test identity.

---

# Why a Real Server Certificate Is Sensitive

A certificate for a real internal server may become a reusable credential.

Even if no interception is performed during the assessment, possession of:

```text
Private Key
+
Trusted Certificate
+
Production DNS Identity
```

creates unnecessary risk.

---

# Private Key Handling

Treat ESC17 private keys as sensitive assessment artifacts.

Do not:

```text
Commit to Git
Upload to Ticketing Systems Unencrypted
Paste into Reports
Leave in /tmp
Store in Shared Folders
```

Follow the engagement evidence-handling procedure.

---

# Cleanup

After controlled validation:

```text
Delete Test PFX
Delete Exported Private Key
Remove Temporary Test Service
Revoke Test Certificate if Required
Remove Temporary DNS Entry if Created
Document Cleanup
```

---

# Service Discovery

After identifying ESC17, determine whether useful TLS services exist.

This should begin with inventory and architecture review rather than interception.

Examples:

```text
WSUS
SCCM / MECM
Internal HTTPS
Management Platforms
Deployment Platforms
Configuration Management
Custom Enterprise Services
```

---

# DNS Enumeration

Review DNS for likely management infrastructure.

PowerShell:

```powershell
Resolve-DnsName wsus.corp.example
```

For known names only.

Broader DNS discovery should remain within the authorised scope.

---

# WSUS Configuration Discovery

On an authorised Windows endpoint, administrators can inspect WSUS-related policy configuration under:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate
```

Read-only PowerShell:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue
```

Potential values may identify configured update infrastructure.

---

# WSUS Client Configuration

Useful values can include:

```text
WUServer
WUStatusServer
```

For example:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue |
    Select-Object WUServer,WUStatusServer
```

This is a read-only check.

---

# HTTP vs HTTPS WSUS

If WSUS is configured using:

```text
http://
```

a server-authentication certificate is not involved in the same way.

ESC17 becomes especially relevant when clients expect:

```text
https://wsus.corp.example
```

and validate the server certificate.

---

# TLS Validation

For an authorised HTTPS service, OpenSSL can inspect the certificate chain:

```bash
openssl s_client -connect wsus.corp.example:8531 -servername wsus.corp.example
```

This is useful for understanding:

```text
Certificate Issuer
SAN
TLS Version
Certificate Chain
```

without attempting impersonation.

---

# Port 8531

WSUS commonly uses:

```text
8530
```

for HTTP and:

```text
8531
```

for HTTPS in common deployments.

Do not assume these ports are universal.

Verify the actual environment.

---

# Traffic Influence Assessment

After proving the certificate issue, assess whether an attacker could realistically influence traffic.

Possible questions include:

```text
Can DNS records be modified?

Can the attacker control DHCP?

Can proxy settings be modified?

Can Group Policy be modified?

Can routing be influenced?

Can local name resolution be abused?

Does the attacker already control a network segment?

Can service configuration be changed?
```

Each of these is a separate security issue or prerequisite.

---

# Do Not Create Another Vulnerability to Prove ESC17

If the attacker cannot influence DNS:

```text
Do Not Modify DNS
```

using administrative privileges merely to complete the chain.

If the attacker cannot modify proxy configuration:

```text
Do Not Modify GPO
```

with administrator access merely to complete the chain.

Report the prerequisites accurately.

---

# Attack-Path Thinking

A strong assessment asks:

```text
What Can My Current Principal Do?
```

rather than:

```text
What Could Domain Admin Configure
to Make This Exploitable?
```

---

# BloodHound Context

BloodHound may help identify relationships around:

```text
Certificate Enrollment
Template Control
DNS Control
GPO Control
Computer Control
Administrative Infrastructure
```

Use graph relationships to determine whether an ESC17 certificate can realistically be combined with another privilege path.

---

# DNS Control

If an attacker can modify a DNS record corresponding to the target service:

```text
Target DNS
   |
   v
Attacker IP
```

while possessing:

```text
Valid Certificate
for Target DNS
```

the server impersonation path becomes substantially more realistic.

---

# GPO Control

If an attacker controls a GPO that configures:

```text
WSUS
Proxy
Service Endpoint
```

the attacker may already possess a significant privilege path independent of ESC17.

Avoid double-counting impact.

---

# Network Position

An attacker positioned between clients and the target service may potentially influence traffic without modifying DNS.

Again, this is a separate prerequisite.

---

# Service-Specific Analysis

Once the attacker can impersonate a TLS server, the next question is:

```text
What Does the Client Send
or Trust Over This Channel?
```

Potentially interesting behaviours include:

```text
Credentials
NTLM Authentication
Configuration
Commands
Update Metadata
Secrets
API Tokens
Management Data
```

Do not assume all HTTPS services expose sensitive information merely because their TLS identity can be impersonated.

---

# NTLM Authentication

Some internal HTTP services may negotiate:

```text
Negotiate
```

or:

```text
NTLM
```

authentication.

If a client authenticates to an attacker-controlled server, additional relay or credential exposure risks may exist.

These should be analysed separately under:

[NTLM Relay](../ntlm-relay.md)

---

# Relay Preconditions Still Apply

Possessing an ESC17 certificate does not bypass normal NTLM relay protections.

Relay still depends on controls such as:

```text
SMB Signing
LDAP Signing
LDAP Channel Binding
EPA
Protocol Compatibility
Target Authentication Configuration
```

---

# Server Authentication Is Not Client Authentication

Do not assume a certificate containing only:

```text
Server Authentication
```

can be used with:

```text
certipy auth
```

to authenticate as a domain user.

ESC17 is specifically about:

```text
Server Impersonation
```

not ordinary PKINIT client authentication.

---

# This Is a Critical Distinction

Incorrect:

```text
ESC17 Certificate
      |
      v
certipy auth
      |
      v
Domain Admin
```

Correct:

```text
ESC17 Certificate
      |
      v
TLS Server Identity
      |
      v
Service Impersonation
      |
      v
Service-Specific Impact
```

---

# Detection

ESC17 detection should combine:

```text
Template Configuration
Certificate Enrollment
Certificate Contents
DNS / Network Changes
Service Authentication
```

---

# Inventory ESC17 Templates

Defenders should identify templates containing:

```text
Enrollee Supplies Subject
```

and:

```text
Server Authentication
```

especially where enrollment is granted broadly.

---

# Monitor Template Changes

Changes to:

```text
msPKI-Certificate-Name-Flag
```

can enable:

```text
Supply in the request
```

Monitor certificate-template modifications.

---

# Event 5136

With appropriate Directory Service Changes auditing:

```text
5136
```

can provide visibility into changes to certificate-template objects in Active Directory.

Monitor changes involving:

```text
msPKI-Certificate-Name-Flag
pKIExtendedKeyUsage
nTSecurityDescriptor
```

and other security-sensitive template properties.

---

# Certificate Request Auditing

Where Certificate Services auditing is enabled:

```text
4886
```

can provide visibility into certificate requests.

---

# Certificate Issuance Auditing

```text
4887
```

can provide visibility into certificate issuance.

---

# Detection Questions

For broadly enrollable server templates, ask:

```text
Who requested the certificate?

What DNS SAN was requested?

Does the requester own that DNS identity?

Is the DNS name a production server?

Was the request expected?

Was the certificate subsequently used?
```

---

# Detect Identity Mismatch

A useful detection model is:

```text
Requester:
CORP\Alice

Requested SAN:
DNS=wsus.corp.example
```

Ask:

```text
Why is Alice authorised to
request a certificate for WSUS?
```

The mismatch between:

```text
Requester Identity
```

and:

```text
Requested Server Identity
```

is often the important signal.

---

# Certificate Transparency Is Usually Not Enough

Internal Enterprise CA certificates are generally not publicly logged in the same way as public Web PKI certificates.

Organisations therefore need their own:

```text
CA Logging
Certificate Inventory
SIEM
PKI Monitoring
```

---

# Monitor High-Value DNS Names

Consider enhanced monitoring for certificates issued for:

```text
WSUS
SCCM
ADFS
VPN
Management Servers
Software Repositories
Internal Proxies
Privileged Web Portals
```

where appropriate to the organisation.

---

# Monitor DNS Changes

If an attacker combines ESC17 with DNS manipulation, correlate certificate issuance with:

```text
DNS Record Changes
```

for the same hostname.

---

# Monitor GPO Changes

If service endpoints are controlled by Group Policy, monitor unexpected changes to:

```text
WSUS Settings
Proxy Settings
Service Configuration
```

---

# Monitor TLS Certificate Changes

Infrastructure monitoring can identify when a known internal service suddenly presents:

```text
Different Serial Number
Different Public Key
Different Certificate
```

even when the replacement chains to the same trusted Enterprise CA.

---

# Certificate Pinning for Critical Services

Where technically feasible, critical internal management systems may benefit from stronger server identity controls.

Depending on the application, these can include:

```text
Certificate Pinning
Public-Key Pinning at Application Level
Dedicated Private CA
Restricted Issuance
Mutual TLS
```

Do not implement obsolete browser HPKP mechanisms.

---

# Hardening ESC17

The strongest template-level remediation is:

```text
Disable Supply in the request
```

where it is not required.

Configure the template to derive identity from Active Directory where possible.

---

# Build from Active Directory Information

For templates associated with specific domain principals, prefer:

```text
Build from this Active Directory information
```

where appropriate.

This removes requester control over arbitrary subject identities.

---

# Web Server Templates May Need Supply in Request

Some server-certificate workflows legitimately require:

```text
Supply in the request
```

because DNS names cannot be automatically derived from the requester's AD account.

In that situation:

```text
Do Not Simply Grant
Domain Users Enroll
```

Instead restrict enrollment.

---

# Restrict Enrollment

Grant enrollment only to:

```text
Dedicated PKI Enrollment Group
Server Administrators
Automation Service Accounts
Approved Certificate Management Platform
```

as required by the environment.

---

# Separate Enrollment Roles

A good enterprise design can separate:

```text
User Authentication Templates
```

from:

```text
Server TLS Templates
```

and tightly control who can use each.

---

# Manager Approval

For high-risk server certificates, consider:

```text
CA Certificate Manager Approval
```

where operationally feasible.

This introduces a review before issuance.

---

# Authorised Signatures

Sensitive certificate workflows can also require:

```text
Authorised Signatures
```

depending on organisational PKI design.

---

# Dedicated Templates

Avoid one broad template for:

```text
Every Internal Server
```

where possible.

Consider dedicated templates for:

```text
Web Servers
Management Infrastructure
Update Infrastructure
Application Gateways
```

with appropriate enrollment groups.

---

# Protect High-Value Names

High-value server identities deserve stronger issuance governance.

Examples:

```text
wsus.corp.example
adfs.corp.example
vpn.corp.example
sccm.corp.example
proxy.corp.example
```

Certificate issuance for these names should be restricted and monitored.

---

# CA Governance

ESC17 demonstrates that certificate issuance is effectively:

```text
Identity Issuance
```

A CA administrator is not merely issuing encryption material.

They are issuing statements such as:

```text
"This public key represents
wsus.corp.example."
```

That assertion must be protected accordingly.

---

# Automate Certificate Enrollment Carefully

Automated server-certificate enrollment can be secure when the automation strongly verifies:

```text
Requester
Server Ownership
DNS Ownership
Requested SANs
Template
Approval Policy
```

Automation should not mean:

```text
Any Domain User Can Request Any DNS Name
```

---

# Incident Response

If ESC17 exploitation is suspected:

```text
Identify Vulnerable Template
       |
       v
Identify Certificates Issued
       |
       v
Identify Suspicious DNS SANs
       |
       v
Identify Private-Key Holder
       |
       v
Review DNS / Network Changes
       |
       v
Review Service Connections
       |
       v
Revoke Certificates
```

---

# Identify Exposure Window

Determine:

```text
When Was Template Vulnerable?
```

Review:

```text
Template Creation
Template Modification
Enrollment ACL Changes
Supply-in-Request Changes
EKU Changes
Template Publication
```

---

# Search CA Database

Review certificates issued from the vulnerable template.

Record:

```text
Request ID
Requester
Template
Subject
SAN
Serial Number
Issue Time
Expiration Time
Disposition
```

---

# Find Suspicious SANs

Look for certificate DNS identities associated with:

```text
Management Infrastructure
Update Infrastructure
Authentication Services
Security Systems
Software Distribution
High-Value Applications
```

---

# Requester-to-DNS Correlation

A useful investigation question is:

```text
Does the Requester
Have a Legitimate Relationship
with the Requested DNS Name?
```

For example:

```text
Requester:
WebServerAutomation$

SAN:
api01.corp.example
```

may be expected.

But:

```text
Requester:
ordinary-user

SAN:
wsus.corp.example
```

requires immediate investigation.

---

# Review DNS History

If suspicious certificates exist, determine whether the corresponding DNS names were redirected during the certificate's validity period.

---

# Review Proxy History

For applications using proxies, determine whether proxy settings were modified to redirect traffic.

---

# Review GPO History

Investigate GPO changes that could alter:

```text
WSUS
Proxy
Service Endpoints
Trusted Roots
Network Configuration
```

---

# Review Network Telemetry

Search for clients connecting to unexpected IP addresses while using:

```text
Expected Internal Hostname
```

during the suspicious period.

---

# Review TLS Telemetry

Where available, compare:

```text
Certificate Serial Numbers
Certificate Fingerprints
Public Keys
Issuers
```

presented by the legitimate service and suspected attacker infrastructure.

---

# Revoke Suspicious Certificates

If an unauthorised server certificate is identified:

```text
Revoke Certificate
       |
       v
Publish Updated CRL
       |
       v
Verify Revocation Availability
```

---

# Private Key Assumption

If an unauthorised certificate was issued to an attacker-controlled request:

```text
Assume the Attacker
Possesses the Private Key
```

Revoking the certificate is therefore necessary.

---

# Fix the Template

Containment is incomplete if the certificate is revoked but the vulnerable template remains available.

Remediate:

```text
Enrollment Rights
Supply in Request
Approval Requirements
Template Publication
```

as appropriate.

---

# Reporting ESC17

Avoid reporting only:

```text
ESC17
```

Use a descriptive title.

Examples:

```text
Low-Privilege Users Can Obtain Trusted Certificates for Arbitrary Internal Servers
```

```text
Certificate Template Allows Unauthorised Server Identity Impersonation
```

```text
AD CS Template Permits Arbitrary Server Authentication Certificates
```

---

# Example Finding

```text
Finding:
Low-Privilege Users Can Obtain Trusted Certificates for Arbitrary
Internal Server Identities

AD CS Technique:
ESC17

Affected CA:
CORP-CA

Affected Template:
InternalWebServer

Description:
The InternalWebServer certificate template permits members of
Domain Users to enroll for certificates.

The template is configured with "Supply in the request" and includes
the Server Authentication Extended Key Usage.

Certificate Manager approval and authorised signatures are not
required.

As a result, a low-privileged domain user can request a certificate
containing a DNS Subject Alternative Name that they do not control.

During testing, the assessment account successfully requested a
certificate for the dedicated test identity:

esc17-test.corp.example

The resulting certificate was issued by the organisation's trusted
Enterprise CA and contained the Server Authentication EKU.

No production server identity was requested and no production
traffic was intercepted.

Impact:
An attacker with domain credentials may be able to obtain trusted
TLS certificates for internal server identities.

If the attacker can additionally influence DNS, routing, proxy
configuration or another mechanism that directs client traffic,
the certificate could be used to impersonate an internal TLS
service.

The resulting impact depends on the targeted service and may
include credential exposure, authentication relay opportunities,
sensitive information disclosure or abuse of trusted management
infrastructure.

Recommendation:
Disable "Supply in the request" where requester-controlled server
identity information is not required.

Where requester-supplied SANs are operationally necessary, restrict
enrollment permissions to dedicated and trusted server-enrollment
principals.

Consider manager approval or other certificate issuance controls for
high-value server certificates.

Monitor certificate requests for high-value internal DNS names and
correlate certificate issuance with the identity of the requester.
```

---

# Severity Model

Severity should reflect the complete attack path.

Use:

```text
Template Exposure
      +
Server Identity Control
      +
CA Trust
      +
Traffic Influence
      +
Service Impact
      =
Severity
```

---

# Lower-Risk Example

```text
ESC17 Template
       |
       v
Restricted Server Admin Group
       |
       v
Dedicated Low-Value Development CA
```

The practical risk may be limited.

---

# Medium-to-High Risk Example

```text
Domain Users
      |
      v
ESC17 Template
      |
      v
Production Enterprise CA
      |
      v
Arbitrary Internal DNS Certificate
```

This is a serious PKI trust weakness even before a complete service-impersonation chain is demonstrated.

---

# Critical Chain Example

```text
Low-Privilege User
       |
       v
ESC17 Template
       |
       v
Certificate for Critical Service
       |
       v
Attacker Controls Traffic
       |
       v
Client Trusts Certificate
       |
       v
Critical Management Protocol
       |
       v
Code Execution / Privileged Credential Exposure
```

A demonstrated path of this type may justify critical severity.

---

# Avoid Severity Inflation

Do not claim:

```text
ESC17 = Domain Admin
```

without proving the service-specific path.

Instead report:

```text
Certificate Issuance Capability
```

and separately explain:

```text
Reachable Attack Chains
```

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
Template Schema Version
Template Publication
Enrollment Principals
Effective Enrollment Rights
msPKI-Certificate-Name-Flag
Enrollee Supplies Subject
pKIExtendedKeyUsage
Server Authentication OID
Manager Approval
Authorised Signatures
Template Owner
Template ACL
Test Requester
Test DNS SAN
Certificate Serial Number
Certificate Issuer
Certificate Subject
Certificate SAN
Certificate EKUs
Certificate Validity
Potential Target Services
CA Trust
Traffic Influence Preconditions
Certificate Pinning
Validation Method
Cleanup Result
```

Do not include private keys in the final report.

---

# ESC17 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify published templates
- [ ] Identify templates with Server Authentication
- [ ] Identify templates with Supply in the request
- [ ] Identify broadly enrollable templates
- [ ] Identify manager approval
- [ ] Identify authorised signature requirements
- [ ] Identify template owners
- [ ] Identify template ACLs

## Template Analysis

- [ ] Record template name
- [ ] Record schema version
- [ ] Record `msPKI-Certificate-Name-Flag`
- [ ] Confirm Enrollee Supplies Subject
- [ ] Record `pKIExtendedKeyUsage`
- [ ] Confirm Server Authentication
- [ ] Record enrollment rights
- [ ] Confirm template publication
- [ ] Identify publishing CA
- [ ] Review approval controls

## Certipy

- [ ] Verify Certipy version
- [ ] Review `certipy find -h`
- [ ] Run authorised enumeration
- [ ] Identify ESC17 candidates
- [ ] Confirm Enrollee Supplies Subject
- [ ] Confirm Server Authentication
- [ ] Confirm enrollment rights
- [ ] Confirm approval settings
- [ ] Manually validate tool findings

## Windows

- [ ] Enumerate certificate templates
- [ ] Enumerate Server Authentication EKU
- [ ] Review name flags
- [ ] Enumerate publishing CAs
- [ ] Review template ACL
- [ ] Identify effective enrollment principals

## Linux

- [ ] Enumerate templates through LDAP
- [ ] Search Server Authentication OID
- [ ] Enumerate Enrollment Services
- [ ] Correlate templates to CAs
- [ ] Review Certipy results

## Service Analysis

- [ ] Identify potentially valuable TLS services
- [ ] Identify WSUS where relevant
- [ ] Identify management platforms
- [ ] Identify software distribution services
- [ ] Identify internal HTTPS services
- [ ] Determine client CA trust
- [ ] Determine certificate pinning
- [ ] Determine mutual TLS
- [ ] Determine traffic influence requirements
- [ ] Determine realistic protocol impact

## WSUS Analysis

- [ ] Identify WSUS server
- [ ] Identify configured WSUS URL
- [ ] Determine HTTP vs HTTPS
- [ ] Identify actual WSUS ports
- [ ] Inspect legitimate TLS certificate
- [ ] Determine whether certificate pinning exists
- [ ] Do not impersonate production WSUS without explicit approval

## Safe Validation

- [ ] Prefer read-only template analysis
- [ ] Use dedicated test account
- [ ] Use dedicated test DNS name
- [ ] Do not request production server identity
- [ ] Do not modify production DNS
- [ ] Do not modify production proxy settings
- [ ] Do not modify GPO to create traffic influence
- [ ] Do not intercept production management traffic
- [ ] Inspect certificate only
- [ ] Protect test private key
- [ ] Revoke certificate where required
- [ ] Delete test private key
- [ ] Document cleanup

## Detection

- [ ] Inventory ESC17 templates
- [ ] Monitor template configuration
- [ ] Monitor `msPKI-Certificate-Name-Flag`
- [ ] Monitor `pKIExtendedKeyUsage`
- [ ] Monitor template ACLs
- [ ] Monitor event 5136
- [ ] Monitor certificate requests
- [ ] Monitor event 4886 where configured
- [ ] Monitor certificate issuance
- [ ] Monitor event 4887 where configured
- [ ] Correlate requester with DNS SAN
- [ ] Monitor high-value DNS identities
- [ ] Monitor DNS changes
- [ ] Monitor GPO changes
- [ ] Monitor proxy changes
- [ ] Monitor unexpected TLS certificate changes

## Hardening

- [ ] Disable Supply in the request where unnecessary
- [ ] Restrict enrollment rights
- [ ] Remove broad enrollment
- [ ] Use dedicated enrollment groups
- [ ] Review Server Authentication templates
- [ ] Consider manager approval
- [ ] Consider authorised signatures
- [ ] Separate high-value server templates
- [ ] Protect high-value DNS identities
- [ ] Review automated certificate issuance
- [ ] Monitor Enterprise CA activity
- [ ] Consider stronger identity validation for critical services

## Incident Response

- [ ] Identify vulnerable templates
- [ ] Determine exposure period
- [ ] Search CA request database
- [ ] Identify suspicious certificates
- [ ] Identify suspicious DNS SANs
- [ ] Correlate requester identities
- [ ] Review DNS history
- [ ] Review proxy changes
- [ ] Review GPO changes
- [ ] Review network telemetry
- [ ] Review TLS telemetry
- [ ] Identify service authentication
- [ ] Determine credential exposure
- [ ] Determine relay activity
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Remediate template
- [ ] Validate remediation

## Reporting

- [ ] Use descriptive finding title
- [ ] Identify ESC17
- [ ] Identify exact CA
- [ ] Identify exact template
- [ ] Record enrollment rights
- [ ] Record Supply in the request
- [ ] Record Server Authentication EKU
- [ ] Record approval controls
- [ ] Explain server impersonation
- [ ] Explain additional traffic prerequisite
- [ ] Explain service-specific impact
- [ ] Separate template exposure from full exploitation
- [ ] Avoid claiming automatic Domain Admin
- [ ] Document safe validation
- [ ] Provide specific remediation

---

# ESC17 Testing Model

The secure server-certificate model is:

```text
Authorised Server
       |
       v
Certificate Request
       |
       v
Approved DNS Identity
       |
       v
Enterprise CA
       |
       v
Server Certificate
```

The ESC17 model is:

```text
Low-Privilege User
       |
       v
Enrollee Supplies Subject
       |
       v
Arbitrary DNS Identity
       |
       v
Server Authentication
       |
       v
Trusted Server Certificate
```

The TLS model is:

```text
Client
   |
   v
Connects to
service.corp.example
   |
   v
Server Presents Certificate
   |
   v
DNS SAN Matches?
   |
   +--> No -> Reject
   |
   +--> Yes
           |
           v
       CA Trusted?
           |
           +--> No -> Reject
           |
           +--> Yes
                   |
                   v
              TLS Accepted
```

ESC17 attacks the identity issuance stage:

```text
Attacker
   |
   v
Obtains Certificate
for service.corp.example
   |
   v
DNS SAN Matches
   |
   v
Enterprise CA Trusted
```

The remaining requirement is:

```text
Make Client Reach Attacker
```

The complete attack model is:

```text
ESC17 Template
       |
       v
Arbitrary Server Certificate
       |
       v
Traffic Influence
       |
       v
TLS Server Impersonation
       |
       v
Service-Specific Attack
```

The ESC1 comparison is:

```text
ESC1
 |
 v
Who Is the Client?
```

versus:

```text
ESC17
 |
 v
Who Is the Server?
```

The WSUS model is:

```text
Windows Client
      |
      v
Configured WSUS Name
      |
      v
Traffic Redirected
      |
      v
Attacker
      |
      v
ESC17 Certificate
      |
      v
TLS Identity Accepted
      |
      v
WSUS Protocol Interaction
```

The safe-testing model is:

```text
Enumerate Template
       |
       v
Confirm ESC17 Conditions
       |
       v
Evidence Sufficient?
       |
       +--> Yes -> Report
       |
       +--> No
               |
               v
        Dedicated Test DNS
               |
               v
        Controlled Certificate
               |
               v
        Inspect Certificate
               |
               v
             Cleanup
```

The detection model is:

```text
Low-Privilege Requester
       |
       v
Server Template
       |
       v
High-Value DNS SAN
       |
       v
Certificate Issued
       |
       v
DNS / Network Change
       |
       v
Client Connections
```

The defensive model is:

```text
Restricted Enrollment
       +
Controlled Subject Names
       +
Approval
       +
Certificate Monitoring
       +
DNS Security
       +
Service Identity Validation
       =
Reduced ESC17 Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I impersonate production WSUS
and redirect domain clients?"

Ask:
"Can my low-privilege principal obtain
a trusted Server Authentication
certificate for a DNS identity it
does not control?"
```

For defenders:

```text
Do Not Assume:
"Server Authentication certificates
are less dangerous than user
authentication certificates."

Ask:
"Who is allowed to make the Enterprise
CA assert ownership of an internal
server identity?"
```

The complete ESC17 relationship is:

```text
Low-Privilege Enrollment
        |
        v
Supply in the Request
        |
        v
Server Authentication
        |
        v
Arbitrary DNS SAN
        |
        v
Enterprise CA Signature
        |
        v
Trusted Server Identity
        |
        v
Potential Service Impersonation
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

ESC4:

[AD CS ESC4](esc4.md)

ESC6:

[AD CS ESC6](esc6.md)

ESC15:

[AD CS ESC15](esc15.md)

ESC16:

[AD CS ESC16](esc16.md)

NTLM relay:

[NTLM Relay](../ntlm-relay.md)

Group Policy:

[Group Policy](../group-policy.md)

The ESC1-ESC17 sequence is now complete.

The next AD CS topic is:

```text
docs/active-directory/ad-cs/golden-certificate.md
```

---

# References

## Certipy - ESC17

[Certipy Wiki - Privilege Escalation](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation){ target="_blank" rel="noopener noreferrer" }

Current Certipy documentation defines ESC17 as:

```text
Enrollee-Supplied Subject for Server Authentication
```

and identifies the primary template conditions as:

```text
Enrollee Supplies Subject
Server Authentication
Low-Privilege Enrollment
No Manager Approval
No Authorised Signatures
```

The documentation also discusses server impersonation scenarios including WSUS and notes that additional prerequisites are required for a complete attack path.

---

## Certipy - Terminology

[Certipy Wiki - Terminology](https://github.com/ly4k/Certipy/wiki/02-%E2%80%90-Terminology){ target="_blank" rel="noopener noreferrer" }

The Certipy terminology documentation describes ESC17 SAN control and its use for arbitrary domain names during TLS establishment.

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Current Certipy releases support identification and exploitation analysis for:

```text
ESC1 - ESC17
```

Always verify the installed version:

```bash
certipy --version
certipy find -h
certipy req -h
```

before relying on command syntax.

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Templates

[Microsoft - Certificate Templates Overview](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-template-concepts){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - WSUS

[Microsoft - Windows Server Update Services](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/get-started/windows-server-update-services-wsus){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

Certified Pre-Owned introduced the foundational AD CS escalation taxonomy and remains important background for understanding AD CS trust relationships.

ESC17 itself was added to the taxonomy later.

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC17 expands AD CS assessment beyond:

```text
Can I impersonate a user?
```

and introduces another important question:

```text
Can I impersonate a server?
```

The core problem is straightforward:

```text
Enterprise CA
```

is trusted to assert:

```text
This Public Key Belongs to
server.corp.example
```

If a low-privilege user can cause the CA to make that assertion for an arbitrary server:

```text
PKI Server Identity
```

has been compromised.

The essential ESC17 relationship is:

```text
Enrollee Supplies Subject
        +
Server Authentication
        +
Low-Privilege Enrollment
        =
Arbitrary Server Certificate
```

But exploitation normally requires more:

```text
Arbitrary Server Certificate
        +
Client Trust
        +
Traffic Influence
        +
Useful Service
        =
Server Impersonation Impact
```

This distinction is essential during penetration testing.

Finding an ESC17 template does not automatically establish:

```text
Domain Compromise
```

and it does not automatically establish:

```text
WSUS Compromise
```

The correct process is:

```text
Identify Template
       |
       v
Validate Enrollment
       |
       v
Confirm Arbitrary DNS Identity
       |
       v
Identify Relevant Services
       |
       v
Determine Traffic Prerequisites
       |
       v
Determine Service-Specific Impact
```

For production testing, a dedicated test identity such as:

```text
esc17-test.corp.example
```

is normally enough to demonstrate the certificate issuance weakness.

There is usually no reason to request:

```text
wsus.corp.example
```

or another real production identity unless end-to-end exploitation is explicitly required and approved.

From the defensive perspective, ESC17 demonstrates that:

```text
Server Certificates Are Credentials
```

An organisation should therefore know:

```text
Who Can Request Them?

Which Names Can They Request?

Which CA Signs Them?

Which Clients Trust Them?

Which Critical Services Depend on Them?
```

The strongest defensive model is:

```text
Restricted Enrollment
       |
       v
Validated Server Ownership
       |
       v
Controlled SANs
       |
       v
Enterprise CA
       |
       v
Monitored Certificate Issuance
```

With ESC17 complete, the current Certipy **ESC1 through ESC17** sequence is complete.

The next AD CS topic is:

```text
Golden Certificates
```

which moves away from certificate-template misconfiguration and into one of the highest-impact PKI compromise scenarios:

```text
CA Private Key Compromise
        |
        v
Offline Certificate Forgery
        |
        v
Golden Certificate
```
