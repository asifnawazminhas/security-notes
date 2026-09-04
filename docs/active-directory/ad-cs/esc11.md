# AD CS ESC11 - NTLM Relay to the RPC Certificate Enrollment Interface

ESC11 is an Active Directory Certificate Services (AD CS) relay condition affecting the Certification Authority's RPC certificate enrollment interface.

The core problem is:

```text
AD CS RPC Enrollment
        |
        v
Packet Privacy Not Required
        |
        v
NTLM Authentication Can Be Relayed
        |
        v
Certificate Requested as Victim
```

AD CS supports certificate enrollment through the Microsoft ICertPassage Remote Protocol:

```text
MS-ICPR
```

This protocol exposes an RPC interface that allows clients to submit certificate requests to a Certification Authority and receive issued X.509 certificates.

Microsoft provides a CA interface flag called:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

When enabled, the CA requires:

```text
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
```

for certificate-request RPC connections.

Packet privacy provides the highest RPC authentication level and protects the RPC exchange by signing and encrypting the packets.

If the CA does not enforce packet privacy, an attacker may be able to relay NTLM authentication to the RPC enrollment interface and request a certificate in the security context of the relayed identity.

Microsoft currently classifies this configuration as:

```text
ESC11
```

The high-level attack chain is:

```text
Victim
  |
  v
NTLM Authentication
  |
  v
Attacker Relay
  |
  v
AD CS RPC Interface
  |
  v
Certificate Request
  |
  v
Certificate Issued as Victim
```

ESC11 is particularly important because the RPC enrollment interface may exist even when the HTTP enrollment endpoints associated with ESC8 are absent.

!!! warning "Authorised testing only"
    Relay testing can capture or forward authentication from real users, computers, servers, and domain controllers. Begin with configuration inspection and controlled test identities. Do not coerce production domain controllers, privileged administrators, or critical servers merely to demonstrate ESC11. Where active validation is required, use an approved test account or computer and stop once certificate issuance in the intended security context has been demonstrated.

---

# ESC11 Concept

Normal RPC certificate enrollment looks like:

```text
Client
  |
  v
Authenticate to CA
  |
  v
MS-ICPR
  |
  v
Certificate Request
  |
  v
Certification Authority
  |
  v
Certificate
```

The client authenticates directly to the Certification Authority.

With ESC11:

```text
Victim
  |
  v
NTLM Authentication
  |
  v
Attacker
  |
  v
Relay Authentication
  |
  v
MS-ICPR
  |
  v
Certification Authority
```

The CA sees the relayed identity.

If the victim has permission to enroll in a suitable certificate template, the attacker may be able to request a certificate as that identity.

---

# ICertPassage Remote Protocol

Microsoft documents the certificate enrollment RPC protocol as:

```text
MS-ICPR
```

The ICertPassage Remote Protocol exposes an RPC interface that allows a client to:

```text
Submit Certificate Request
        |
        v
Certification Authority
        |
        v
Receive X.509 Certificate
```

The protocol is specifically designed for certificate enrollment.

---

# ICertPassage Interface

The RPC interface UUID is:

```text
91ae6020-9e3c-11cf-8d7c-00aa00c091be
```

The interface exposes:

```text
CertServerRequest
```

as:

```text
Opnum 0
```

Conceptually:

```text
ICertPassage
     |
     v
CertServerRequest
     |
     v
Certificate Enrollment
```

---

# Certificate Request Formats

MS-ICPR supports certificate requests using formats including:

```text
PKCS #10
CMS
CMC
```

The request is submitted to the CA through the RPC interface.

---

# The Security Control

The important CA setting is:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

Microsoft documents this as part of the CA:

```text
InterfaceFlags
```

configuration.

When enabled:

```text
IF_ENFORCEENCRYPTICERTREQUEST
        |
        v
Require RPC_C_AUTHN_LEVEL_PKT_PRIVACY
        |
        v
Signed + Encrypted RPC Packets
```

---

# Packet Privacy

The required RPC authentication level is:

```text
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
```

This provides packet-level protection for the RPC connection.

Conceptually:

```text
RPC Authentication
       |
       v
Packet Privacy
       |
       +--> Integrity
       |
       +--> Confidentiality
```

Microsoft describes this as the highest RPC authentication level.

---

# Why Packet Privacy Stops ESC11

Without sufficient RPC protection:

```text
Victim NTLM
    |
    v
Relay
    |
    v
RPC Enrollment
```

may be possible.

With packet privacy enforced:

```text
Victim NTLM
    |
    v
Relay Attempt
    |
    v
RPC Packet Privacy Required
    |
    X
Request Rejected
```

Microsoft's MS-ICPR specification states that when:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

is enabled and the client connection does not use:

```text
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
```

the CA must refuse the connection.

---

# ESC11 Root Cause

The ESC11 root cause is therefore:

```text
AD CS RPC Enrollment Enabled
          +
Packet Privacy Not Enforced
          =
Relayable Enrollment Interface
```

This is fundamentally different from a vulnerable certificate template.

---

# InterfaceFlags

The CA configuration contains:

```text
InterfaceFlags
```

which controls several CA RPC behaviours.

Relevant flags include:

```text
IF_ENFORCEENCRYPTICERTREQUEST
IF_NORPCICERTREQUEST
IF_NOREMOTEICERTREQUEST
```

depending on CA configuration and protocol context.

The most important ESC11 flag is:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

---

# IF_NORPCICERTREQUEST

Microsoft also defines:

```text
IF_NORPCICERTREQUEST
```

which can prevent certificate issuance through the ICertPassage RPC interface.

This is different from:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

Conceptually:

```text
IF_NORPCICERTREQUEST
        |
        v
RPC Certificate Requests Disabled
```

versus:

```text
IF_ENFORCEENCRYPTICERTREQUEST
        |
        v
RPC Certificate Requests Allowed
but Packet Privacy Required
```

---

# Default Configuration

Microsoft states that:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

is enabled by default.

However, it may have been disabled in older environments for compatibility with clients that could not support the required RPC authentication level.

Legacy systems are therefore particularly important during ESC11 assessment.

---

# Historical Compatibility

One reason the flag may have been disabled is support for legacy systems such as:

```text
Windows XP
```

Modern environments should question whether such compatibility settings remain necessary.

A legacy exception created many years ago may remain present long after the original dependency disappeared.

---

# ESC11 vs ESC8

ESC8 and ESC11 are both AD CS relay techniques.

The difference is the enrollment protocol.

ESC8:

```text
Victim NTLM
    |
    v
HTTP Relay
    |
    v
AD CS Web Enrollment
```

ESC11:

```text
Victim NTLM
    |
    v
RPC Relay
    |
    v
AD CS RPC Enrollment
```

---

# ESC8 Surface

ESC8 commonly involves HTTP-based AD CS endpoints such as:

```text
/certsrv/
```

and related enrollment services.

See:

[AD CS ESC8](esc8.md)

---

# ESC11 Surface

ESC11 instead targets:

```text
MS-ICPR
```

over RPC.

Therefore:

```text
No /certsrv/
```

does not mean:

```text
No AD CS Relay Surface
```

The RPC interface must also be assessed.

---

# ESC8 vs ESC11

A useful comparison is:

| Property | ESC8 | ESC11 |
|---|---|---|
| Primary protocol | HTTP / HTTPS | RPC |
| Enrollment surface | Web enrollment | MS-ICPR |
| Relay class | NTLM relay | NTLM relay |
| Primary protection | EPA / HTTPS / NTLM controls | RPC packet privacy |
| AD CS required | Yes | Yes |
| Certificate issued as victim | Potentially | Potentially |

---

# ESC11 Is a Relay Technique

ESC11 does not normally involve:

```text
Cracking NTLM
```

The authentication is:

```text
Captured
```

and:

```text
Forwarded
```

to another service.

Conceptually:

```text
NTLM Authentication
       |
       +--> Capture -> Offline Cracking
       |
       +--> Relay -> Authenticate Elsewhere
```

ESC11 uses the second path.

---

# Capture vs Relay

Do not confuse:

```text
Responder Capture
```

with:

```text
ESC11 Relay
```

Capturing:

```text
NetNTLMv2
```

does not itself demonstrate ESC11.

ESC11 requires:

```text
Authentication
      |
      v
Relayed to AD CS RPC
      |
      v
Certificate Request
```

---

# ESC11 Attack Requirements

A meaningful ESC11 path generally requires:

```text
AD CS Enterprise CA
        +
Reachable RPC Enrollment Interface
        +
Packet Privacy Not Required
        +
NTLM Authentication Available
        +
Authentication Source
        +
Victim Enrollment Rights
        +
Suitable Certificate Template
        =
Potential ESC11
```

Each condition should be validated.

---

# Enterprise CA

First identify Certification Authorities.

Certipy:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review:

```text
Certificate Authorities
Certificate Templates
CA Permissions
Enrollment Services
ESC Findings
```

---

# CA Host

Record:

```text
CA Name
CA Hostname
CA Type
CA Certificate
Published Templates
```

For example:

```text
CA Name:
CORP-CA

Host:
ca01.corp.example
```

---

# RPC Reachability

RPC normally begins through the RPC Endpoint Mapper:

```text
TCP/135
```

with subsequent communication using dynamically assigned RPC ports.

A basic connectivity check from an authorised testing system:

```bash
nmap -Pn -p135 ca01.corp.example
```

This establishes RPC Endpoint Mapper reachability.

It does not prove ESC11.

---

# Windows RPC Check

From Windows:

```powershell
Test-NetConnection ca01.corp.example -Port 135
```

Example:

```text
ComputerName     : ca01.corp.example
RemotePort       : 135
TcpTestSucceeded : True
```

Again:

```text
TCP/135 Reachable
```

does not equal:

```text
ESC11 Vulnerable
```

---

# Dynamic RPC Ports

Modern Windows RPC commonly uses dynamic high ports after endpoint negotiation.

Therefore firewall assessment should consider:

```text
135/tcp
+
Dynamic RPC Range
```

rather than checking only TCP/135.

---

# Enumerate CA InterfaceFlags

On an authorised CA server, use:

```cmd
certutil -getreg CA\InterfaceFlags
```

Record the resulting value.

The important question is whether:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

is enabled.

---

# Registry Location

The CA configuration is stored under:

```text
HKLM\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration\<CA-NAME>
```

The relevant value is:

```text
InterfaceFlags
```

---

# PowerShell Registry Inspection

On the CA:

```powershell
$caBase = 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration'

Get-ChildItem $caBase |
    ForEach-Object {
        Get-ItemProperty $_.PSPath -Name InterfaceFlags -ErrorAction SilentlyContinue |
            Select-Object PSChildName,InterfaceFlags
    }
```

This provides the raw interface flags for each CA configuration on the host.

---

# InterfaceFlags Is a Bitmask

Do not interpret:

```text
InterfaceFlags != 0
```

as meaning packet privacy is enabled.

The value is a bitmask containing multiple CA interface flags.

The specific:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

flag must be evaluated.

---

# Certipy Enumeration

Certipy supports AD CS enumeration and can identify several ESC conditions.

Start with:

```bash
certipy --version
```

Then:

```bash
certipy find -h
```

A typical read-only query:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review any:

```text
ESC11
```

result against the CA's effective RPC configuration.

---

# Manual Verification

The preferred workflow is:

```text
Certipy Finding
      |
      v
Identify CA
      |
      v
Inspect InterfaceFlags
      |
      v
Confirm RPC Enrollment
      |
      v
Confirm Packet Privacy State
```

Do not report solely from automated output.

---

# Remote Enumeration Limitations

Reading CA configuration remotely may depend on:

```text
RPC
Remote Registry
Permissions
Firewall
Service Configuration
```

An inability to retrieve the setting remotely does not establish whether ESC11 is present.

---

# Microsoft Defender for Identity

Microsoft Defender for Identity currently includes a certificate security posture assessment for:

```text
Enforce encryption for RPC certificate enrollment interface (ESC11)
```

This can provide useful defensive visibility where the appropriate AD CS sensor is deployed.

---

# Certificate Template Still Matters

Even if ESC11 is present, certificate issuance still depends on the relayed identity's ability to enroll.

Conceptually:

```text
Relay Works
    |
    v
Can Victim Enroll?
    |
    +--> No -> Certificate Request Fails
    |
    +--> Yes
            |
            v
       Certificate Issued
```

---

# Machine Accounts

Computer accounts commonly have enrollment permissions for machine-oriented certificate templates.

A relayed machine account may therefore be particularly interesting.

For example:

```text
CORP\WS01$
```

may be able to enroll in:

```text
Machine
```

depending on template configuration.

---

# Domain Controllers

Domain controllers may have access to templates such as:

```text
DomainController
DomainControllerAuthentication
KerberosAuthentication
```

depending on the PKI configuration.

This makes coerced domain-controller authentication particularly sensitive.

Do not use production domain controllers for routine proof.

---

# User Accounts

A relayed user may have access to templates such as:

```text
User
```

or organisation-specific authentication templates.

The resulting impact depends on:

```text
Enrollment Rights
EKUs
Certificate Mapping
Victim Privileges
```

---

# Certificate Authentication

If a relayed identity receives a certificate suitable for authentication:

```text
Certificate
     |
     v
PKINIT / Schannel
     |
     v
Victim Identity
```

the certificate can become reusable authentication material.

---

# Why Certificates Change Relay Impact

Traditional NTLM relay may provide:

```text
One Relayed Session
```

ESC11 can potentially transform that session into:

```text
Certificate + Private Key
```

which may remain usable beyond the original NTLM exchange.

---

# Password Changes

Certificate authentication material can remain valid independently of the account password.

Conceptually:

```text
Password Changed
      |
      X
Existing Certificate
```

until certificate expiration, revocation, mapping changes, or other controls prevent its use.

This increases the importance of certificate revocation during incident response.

---

# Authentication Coercion

Relay attacks often need a way to cause the victim to authenticate to infrastructure controlled by the tester or attacker.

This is:

```text
Authentication Coercion
```

See:

[Authentication Coercion](../authentication-coercion.md)

---

# Coercion Model

```text
Attacker
   |
   v
Trigger Authentication
   |
   v
Victim
   |
   v
NTLM Authentication
   |
   v
Relay Listener
```

The relay listener then forwards the authentication to the CA.

---

# Common Coercion Families

Depending on target configuration and patching, coercion techniques historically include families such as:

```text
MS-RPRN
MS-EFSRPC
MS-DFSNM
Other RPC-Based Triggers
Application-Specific Authentication
```

The presence of a coercion technique should be evaluated separately from ESC11.

---

# Coercion != ESC11

This distinction is essential.

```text
Coercion
```

answers:

```text
Can I cause this identity to authenticate?
```

ESC11 answers:

```text
Can I relay that authentication to
AD CS RPC enrollment?
```

---

# Relay != Coercion

A complete attack may require both:

```text
Authentication Source
        +
Relayable Destination
```

Conceptually:

```text
Coercion
   |
   v
NTLM
   |
   v
ESC11
```

---

# Certipy Relay Support

Current Certipy documentation includes RPC relay support for ESC11.

Before testing:

```bash
certipy relay -h
```

The RPC target format is documented as:

```text
rpc://<CA-host>
```

and RPC relay requires the CA name.

---

# Controlled Certipy Listener

For an explicitly authorised lab or dedicated test identity, the structure is:

```bash
certipy relay -target 'rpc://ca01.corp.example' -ca 'CORP-CA'
```

Before using this in an assessment, verify the options supported by the installed version:

```bash
certipy relay -h
```

---

# Template Selection

For controlled testing, specify the intended template when appropriate rather than relying on automatic selection.

Conceptually:

```text
Relayed User
    |
    v
User Test Template
```

or:

```text
Relayed Computer
    |
    v
Machine Test Template
```

---

# Do Not Start with a Domain Controller

A safer test path is:

```text
Dedicated Test Computer
        |
        v
Controlled Authentication
        |
        v
ESC11 Listener
        |
        v
Test Certificate
```

rather than:

```text
Production DC
   |
   v
Coercion
```

---

# Safe Validation Hierarchy

Use the least invasive proof available.

```text
1. Configuration Inspection
          |
          v
2. Confirm RPC Exposure
          |
          v
3. Confirm Packet Privacy State
          |
          v
4. Confirm Enrollment Rights
          |
          v
5. Controlled Relay if Required
          |
          v
6. Stop After Certificate Issuance
```

---

# Level 1 - Configuration Evidence

Strong read-only evidence may include:

```text
CA Identified
RPC Enrollment Enabled
IF_ENFORCEENCRYPTICERTREQUEST Absent / Disabled
Victim-Class Template Available
Enrollment Rights Confirmed
```

For many assessments, this may be sufficient.

---

# Level 2 - Controlled RPC Test

Where additional proof is required, use a dedicated identity to establish that the RPC enrollment interface accepts the relevant authentication level.

Avoid using real privileged accounts.

---

# Level 3 - Controlled Relay

If explicit relay proof is necessary:

```text
Test Account
     |
     v
Controlled Authentication
     |
     v
Relay
     |
     v
CA RPC
     |
     v
Test Certificate
```

Stop after obtaining sufficient evidence.

---

# Level 4 - Certificate Authentication

Authenticating with the resulting certificate is usually unnecessary if certificate issuance as the relayed identity already demonstrates the vulnerability.

Only perform:

```text
Certificate Authentication
```

when the assessment requires end-to-end proof.

---

# Evidence from Certificate

Record:

```text
Requester
Subject
SAN
SID
Template
Issuer
Serial Number
Thumbprint
Validity
EKUs
```

This proves what identity and purpose the CA issued.

---

# Inspect Certificate on Windows

```cmd
certutil -dump esc11-test.cer
```

---

# Inspect Certificate with OpenSSL

PEM:

```bash
openssl x509 -in esc11-test.pem -text -noout
```

DER:

```bash
openssl x509 -in esc11-test.cer -inform DER -text -noout
```

---

# PFX Files

Relay tools may store:

```text
Certificate
+
Private Key
```

inside:

```text
PFX / PKCS#12
```

Treat these files as credentials.

Do not leave them on assessment infrastructure after testing.

---

# Certificate Authentication

If explicitly authorised:

```bash
certipy auth -h
```

Verify the syntax supported by the installed version.

Use only the dedicated test certificate.

---

# ESC11 and NTLM Relay

ESC11 belongs to the broader NTLM relay attack class.

See:

[NTLM Relay](../ntlm-relay.md)

The general model is:

```text
Victim
  |
  v
NTLM
  |
  v
Relay
  |
  v
Target Service
```

For ESC11:

```text
Target Service
     =
AD CS RPC Enrollment
```

---

# SMB Signing Does Not Directly Fix ESC11

SMB signing protects SMB relay targets.

ESC11 targets:

```text
RPC Certificate Enrollment
```

Therefore:

```text
SMB Signing Enabled
```

does not itself mean:

```text
ESC11 Mitigated
```

The CA's RPC packet privacy requirement must be checked directly.

---

# LDAP Signing Does Not Directly Fix ESC11

Likewise:

```text
LDAP Signing
```

protects LDAP.

It does not configure the AD CS RPC interface.

Relay protections must be evaluated per protocol.

---

# EPA Does Not Directly Fix ESC11

Extended Protection for Authentication is important for HTTP-based authentication services and particularly relevant to ESC8 mitigation.

ESC11 instead requires:

```text
RPC Packet Privacy
```

Do not treat the mitigations as interchangeable.

---

# ESC8 and ESC11 Can Coexist

A CA may expose:

```text
HTTP Enrollment
+
RPC Enrollment
```

and both may be insecure.

Therefore assess:

```text
ESC8
+
ESC11
```

independently.

---

# ESC11 and ESC1

ESC1 concerns vulnerable certificate-template identity control.

ESC11 concerns relayed authentication to the enrollment interface.

They can combine, but they are separate conditions.

---

# ESC11 and ESC4

ESC4 may allow modification of a certificate template.

ESC11 may then provide a way to request a certificate through relayed authentication.

Conceptually:

```text
ESC4
 |
 v
Template Modified
 |
 v
ESC11
 |
 v
Relayed Enrollment
```

---

# ESC11 and ESC6

ESC6 concerns CA-wide requester-supplied SAN behaviour.

If ESC6 and ESC11 coexist, additional certificate-request manipulation may become relevant depending on mapping and patch state.

Treat each condition independently before analysing combinations.

---

# ESC11 and ESC9

ESC9 concerns the SID security extension.

ESC11 concerns the enrollment transport.

A certificate obtained through ESC11 can still be affected by:

```text
ESC9
ESC10
ESC16
```

when subsequent certificate mapping is evaluated.

---

# ESC11 and Machine Accounts

A common risk chain is:

```text
Machine Authentication
        |
        v
Relay to CA
        |
        v
Machine Certificate
        |
        v
Authenticate as Machine
```

The impact depends heavily on which machine account was relayed.

---

# ESC11 and Domain Controllers

A particularly dangerous theoretical chain is:

```text
Domain Controller
       |
       v
Coerced NTLM
       |
       v
ESC11 Relay
       |
       v
DC Certificate
       |
       v
DC Authentication Material
```

A domain controller is a Tier 0 identity.

Do not use this chain as routine proof in production.

---

# Why DC Certificates Are Sensitive

A domain-controller certificate may participate in:

```text
Kerberos
LDAP
TLS
Machine Authentication
```

depending on certificate purpose and configuration.

Compromise of a DC certificate can therefore have domain-wide implications.

---

# ESC11 and DCSync

A certificate representing a domain controller may potentially contribute to attack paths that ultimately expose highly privileged domain capabilities.

Do not automatically claim:

```text
ESC11 = DCSync
```

The actual certificate, mapping, authentication result, and subsequent permissions must be demonstrated or carefully reasoned.

---

# ESC11 and Persistence

A certificate obtained through relay can outlive the NTLM authentication event.

Conceptually:

```text
NTLM Relay
   |
   v
Certificate
   |
   v
Reusable Authentication
```

This can convert a transient authentication event into longer-lived credential material.

---

# Detection

ESC11 detection should correlate:

```text
Authentication
      |
      v
RPC Enrollment
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

# Detect Insecure CA Configuration

The first defensive control is configuration monitoring.

Identify CAs where:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

is not enabled.

Microsoft Defender for Identity can identify this condition where its AD CS monitoring requirements are met.

---

# Baseline InterfaceFlags

Maintain a baseline for:

```text
CA\InterfaceFlags
```

and alert on unexpected changes.

---

# Monitor Registry Changes

Monitor:

```text
HKLM\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration\<CA-NAME>\InterfaceFlags
```

for modification.

An attacker with CA administrative control could potentially weaken RPC protections before abusing the enrollment interface.

---

# Certificate Services Auditing

Enable appropriate Certificate Services auditing.

Useful events can include certificate request and issuance activity.

---

# Event 4886

Where auditing is configured:

```text
4886
```

can indicate that Certificate Services received a certificate request.

---

# Event 4887

```text
4887
```

can indicate certificate issuance.

---

# Relay Detection Context

A suspicious pattern may involve:

```text
Unexpected Requester
        |
        v
Unexpected Source
        |
        v
Sensitive Template
        |
        v
Certificate Issued
```

---

# CA Network Telemetry

Monitor unusual RPC traffic to CA servers.

Particularly interesting patterns include:

```text
Workstation -> CA RPC
Pentest / Unknown Host -> CA RPC
Unexpected Segment -> CA RPC
```

depending on normal environment behaviour.

---

# RPC Endpoint Mapper

Network monitoring may observe:

```text
TCP/135
```

followed by:

```text
Dynamic RPC Port
```

to the CA.

This alone is normal in Windows environments.

Detection should rely on context rather than port usage alone.

---

# Authentication Source

Relay investigations should determine:

```text
Who Authenticated?
```

and:

```text
Why Did They Authenticate?
```

Unexpected machine or domain-controller authentication immediately before certificate issuance deserves investigation.

---

# Coercion Detection

Monitor for abnormal RPC activity associated with authentication coercion.

See:

[Authentication Coercion](../authentication-coercion.md)

---

# Certificate Authentication After Relay

If the resulting certificate is used for Kerberos authentication, events such as:

```text
4768
```

may provide additional evidence.

Correlate certificate issuance and subsequent authentication.

---

# Detection Timeline

A useful model is:

```text
Victim Authentication
        |
        v
RPC Connection to CA
        |
        v
4886 - Certificate Request
        |
        v
4887 - Certificate Issued
        |
        v
Certificate Authentication
```

---

# Short-Lived Sequence

A particularly suspicious sequence is:

```text
Coercion
   |
   v
Immediate Certificate Issuance
   |
   v
Immediate Certificate Authentication
```

especially for privileged machine identities.

---

# Hardening ESC11

The direct mitigation is:

```text
Enable IF_ENFORCEENCRYPTICERTREQUEST
```

---

# Microsoft Remediation

Microsoft currently recommends enabling:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

on affected CAs.

The documented command is:

```cmd
certutil -setreg CA\InterfaceFlags +IF_ENFORCEENCRYPTICERTREQUEST
```

The Certificate Services service must then be restarted for the change to take effect.

---

# Service Restart

Microsoft documents:

```cmd
net stop certsvc
net start certsvc
```

Plan the restart through normal change-management procedures.

Do not make this change during an assessment unless remediation activity is explicitly in scope.

---

# Test Before Production

Microsoft recommends testing the configuration in a controlled environment before production deployment.

This is particularly important where legacy certificate-enrollment clients remain.

---

# Identify Legacy Dependencies

Before remediation, identify systems that cannot support:

```text
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
```

Potential examples may include:

```text
Legacy Windows
Legacy Enrollment Software
Old Appliances
Custom PKI Integrations
```

Do not leave the entire CA insecure indefinitely for one legacy dependency without evaluating alternatives.

---

# Segment Legacy PKI

Where a legacy dependency genuinely cannot be removed, consider architectural isolation rather than weakening a high-value enterprise CA.

The exact design should be reviewed with PKI and identity architects.

---

# Restrict CA Network Access

Only systems that require certificate enrollment should be able to reach the CA's enrollment interfaces.

Consider firewall restrictions around:

```text
TCP/135
Dynamic RPC Ports
HTTP / HTTPS Enrollment
```

according to operational requirements.

---

# Reduce NTLM

ESC11 relies on NTLM relay.

Reducing unnecessary NTLM authentication reduces the available relay surface.

However:

```text
Disable NTLM
```

should be treated as a carefully planned identity-hardening programme, not a single pentest remediation command.

---

# Harden Authentication Coercion

Reduce opportunities for attackers to force privileged systems to authenticate externally.

This includes hardening:

```text
Print Spooler
RPC Services
Legacy Protocols
Unnecessary Outbound Authentication
```

according to environment requirements.

---

# Restrict Outbound Authentication

Tier 0 systems should have tightly controlled outbound network communication.

A domain controller should not be able to authenticate arbitrarily to untrusted hosts.

Network segmentation can reduce coercion-to-relay attack paths.

---

# Protect CA Servers

Certification Authorities should be treated as:

```text
Tier 0
```

or equivalent identity-control-plane infrastructure.

Protect them with:

```text
Restricted Administration
Network Segmentation
Current Patching
EDR
Configuration Monitoring
Limited Interactive Logon
Dedicated Administrative Accounts
```

---

# Review Certificate Templates

Even with RPC encryption enabled, certificate templates must still be hardened.

Review:

```text
Enrollment Rights
Authentication EKUs
Manager Approval
Authorized Signatures
Subject Controls
Template ACLs
```

---

# Review Machine Templates

Pay particular attention to templates available to:

```text
Domain Computers
Domain Controllers
Authenticated Users
```

when they provide authentication certificates.

---

# Review ESC8

If ESC11 is identified, also assess:

```text
ESC8
```

because the CA may expose HTTP enrollment services.

---

# Review NTLM Relay Globally

Do not stop at AD CS.

Review whether NTLM authentication can be relayed to:

```text
SMB
LDAP
LDAPS
HTTP
MSSQL
AD CS
Other Services
```

See:

[NTLM Relay](../ntlm-relay.md)

---

# Incident Response

If ESC11 abuse is suspected:

```text
Identify CA
   |
   v
Review InterfaceFlags
   |
   v
Identify Certificate Requests
   |
   v
Identify Relayed Identity
   |
   v
Identify Issued Certificates
   |
   v
Review Authentication
   |
   v
Revoke Certificates
   |
   v
Enable Packet Privacy
```

---

# Verify CA Configuration

Determine whether:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

was:

```text
Never Enabled
```

or:

```text
Recently Disabled
```

The second case may indicate deliberate weakening.

---

# Review Configuration Changes

Inspect administrative and configuration-management records for changes to:

```text
InterfaceFlags
```

and the Certificate Services configuration.

---

# Identify Suspicious Requests

For each suspicious request record:

```text
Request ID
Requester
Template
Subject
SAN
Submission Time
Disposition
```

---

# Identify Issued Certificates

Record:

```text
Serial Number
Thumbprint
Requester
Subject
SAN
Template
EKUs
Validity
```

---

# Determine Private-Key Exposure

If the certificate was generated through a relay tool, assume the corresponding private key may be attacker-controlled.

This means:

```text
Certificate Revocation
```

is important.

---

# Revoke Malicious Certificates

Where unauthorised certificates were issued:

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

# Password Reset Is Not Sufficient

If an attacker possesses:

```text
Certificate + Private Key
```

changing the account password does not automatically invalidate that certificate.

---

# Review Certificate Authentication

Determine whether the certificate was subsequently used for:

```text
Kerberos PKINIT
Schannel
LDAPS
Client TLS
VPN
Other Authentication
```

---

# Review Coercion Source

Determine how the victim's NTLM authentication was obtained.

Possible categories include:

```text
RPC Coercion
Name Resolution
SMB Access
HTTP Access
Application Behaviour
User Interaction
```

---

# Review Privileged Machine Accounts

Pay particular attention to certificates issued to:

```text
Domain Controllers
CA Servers
Management Servers
Backup Servers
SCCM Infrastructure
Tier 0 Systems
```

---

# Restore Secure Configuration

If packet privacy was disabled:

```text
Enable IF_ENFORCEENCRYPTICERTREQUEST
```

after compatibility testing and approved change control.

---

# Reporting ESC11

Avoid reporting only:

```text
ESC11
```

Prefer a descriptive title such as:

```text
AD CS RPC Certificate Enrollment Does Not Require Packet Privacy
```

or:

```text
NTLM Authentication Can Be Relayed to AD CS RPC Enrollment
```

or:

```text
Certificate Authority RPC Interface Permits NTLM Relay
```

---

# Example Finding - Configuration Evidence

```text
Finding:
AD CS RPC Certificate Enrollment Does Not Require Packet Privacy

Affected CA:
CORP-CA

Affected Host:
ca01.corp.example

Description:
The Certification Authority exposes the MS-ICPR RPC certificate
enrollment interface without enforcing RPC packet privacy.

The IF_ENFORCEENCRYPTICERTREQUEST interface flag is not enabled.

Microsoft requires this flag to force certificate enrollment RPC
connections to use RPC_C_AUTHN_LEVEL_PKT_PRIVACY.

Without this protection, NTLM authentication may be relayed to the
certificate enrollment interface.

Impact:
An attacker who can obtain or coerce NTLM authentication from an
identity with certificate enrollment rights may be able to submit a
certificate request in that identity's security context.

If an authentication-capable certificate is issued, the certificate
and corresponding private key may provide reusable authentication
material for the relayed account.

The final impact depends on the identity being relayed, available
certificate templates, enrollment permissions, and certificate
mapping configuration.

Recommendation:
Enable IF_ENFORCEENCRYPTICERTREQUEST on the Certification Authority
and restart Certificate Services through an approved maintenance
process.

Test legacy enrollment clients before production deployment.

Review HTTP-based AD CS enrollment for ESC8 and reduce unnecessary
NTLM and authentication-coercion exposure.
```

---

# Example Finding - Controlled Relay Demonstrated

```text
Finding:
NTLM Authentication Can Be Relayed to AD CS RPC Enrollment

Affected CA:
CORP-CA

Affected Host:
ca01.corp.example

Test Identity:
CORP\ESC11-TEST$

Description:
The Certification Authority does not enforce packet privacy for
MS-ICPR certificate enrollment.

During controlled validation, authentication from a dedicated test
computer account was relayed to the CA RPC enrollment interface.

The CA accepted the relayed authentication and issued a certificate
in the test computer's security context.

No production administrator, domain controller, or other privileged
production identity was coerced during testing.

Impact:
An attacker capable of obtaining NTLM authentication from another
domain identity may be able to relay that authentication to the CA
and obtain certificate credentials for the victim.

The resulting impact depends on the privileges of the relayed
identity and the certificate templates available to it.

Recommendation:
Enable IF_ENFORCEENCRYPTICERTREQUEST to require
RPC_C_AUTHN_LEVEL_PKT_PRIVACY for certificate enrollment.

Review certificate templates and enrollment permissions.

Reduce NTLM usage and authentication-coercion opportunities,
particularly for Tier 0 systems.
```

---

# Severity Assessment

ESC11 severity depends on:

```text
RPC Relay Possible
      +
Authentication Source
      +
Victim Enrollment Rights
      +
Authentication Certificate
      +
Victim Privileges
      =
Severity
```

---

# Example - Lower Impact

```text
Test Workstation
     |
     v
Relay
     |
     v
Machine Certificate
     |
     v
Low-Privilege Computer
```

The configuration is still insecure, but demonstrated impact may be limited.

---

# Example - High Impact

```text
Privileged Server
     |
     v
NTLM Authentication
     |
     v
ESC11
     |
     v
Authentication Certificate
```

Impact can be substantially higher.

---

# Example - Critical Chain

```text
Domain Controller
      |
      v
Coerced NTLM
      |
      v
ESC11 Relay
      |
      v
Domain Controller Certificate
      |
      v
Tier 0 Authentication Material
```

This represents potentially severe domain compromise.

Do not reproduce this chain against a production DC merely to prove severity.

---

# Evidence Checklist

For ESC11 record:

```text
CA Name
CA Hostname
CA Type
CA Certificate
RPC Endpoint Reachability
InterfaceFlags
IF_ENFORCEENCRYPTICERTREQUEST State
IF_NORPCICERTREQUEST State
Published Templates
Victim Identity
Victim Account Type
Victim Enrollment Rights
Template
Template EKUs
Manager Approval
Authorized Signatures
Certificate Request ID
Certificate Serial Number
Certificate Thumbprint
Certificate Subject
Certificate SAN
Certificate SID
Certificate Validity
Authentication Source
Relay Source
Relay Timestamp
Certificate Authentication Result
Cleanup Result
```

---

# ESC11 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify CA hosts
- [ ] Identify CA names
- [ ] Enumerate published templates
- [ ] Identify authentication templates
- [ ] Identify user enrollment
- [ ] Identify computer enrollment
- [ ] Identify domain-controller enrollment
- [ ] Identify RPC reachability
- [ ] Identify HTTP enrollment separately

## RPC Configuration

- [ ] Inspect `InterfaceFlags`
- [ ] Identify `IF_ENFORCEENCRYPTICERTREQUEST`
- [ ] Identify `IF_NORPCICERTREQUEST`
- [ ] Determine whether MS-ICPR is usable
- [ ] Confirm packet privacy requirement
- [ ] Confirm configuration manually
- [ ] Record CA registry configuration
- [ ] Compare against Microsoft guidance

## Tooling

- [ ] Verify Certipy version
- [ ] Review `certipy find -h`
- [ ] Review `certipy relay -h`
- [ ] Enumerate CA with Certipy
- [ ] Confirm ESC11 manually
- [ ] Verify RPC endpoint reachability
- [ ] Use native `certutil` where authorised
- [ ] Review CA registry configuration
- [ ] Do not rely solely on automated ESC labels

## Enrollment

- [ ] Identify victim enrollment rights
- [ ] Identify applicable template
- [ ] Review EKUs
- [ ] Review manager approval
- [ ] Review authorised signatures
- [ ] Review certificate mapping
- [ ] Review machine templates
- [ ] Review domain-controller templates

## Authentication Source

- [ ] Determine whether NTLM is available
- [ ] Identify safe authentication source
- [ ] Review coercion exposure
- [ ] Review name-resolution exposure
- [ ] Review application authentication
- [ ] Avoid privileged production identities
- [ ] Avoid production domain-controller coercion

## Validation

- [ ] Prefer configuration evidence
- [ ] Determine whether relay proof is necessary
- [ ] Obtain explicit approval
- [ ] Use dedicated test identity
- [ ] Use dedicated test computer where possible
- [ ] Start controlled relay listener
- [ ] Generate controlled authentication
- [ ] Request only intended test certificate
- [ ] Record request ID
- [ ] Record certificate metadata
- [ ] Stop after sufficient proof
- [ ] Avoid unnecessary certificate authentication
- [ ] Revoke test certificate where required
- [ ] Delete private-key material

## Related Conditions

- [ ] Review ESC8
- [ ] Review ESC1
- [ ] Review ESC4
- [ ] Review ESC6
- [ ] Review ESC9
- [ ] Review ESC10
- [ ] Review ESC16
- [ ] Review NTLM relay generally
- [ ] Review authentication coercion

## Detection

- [ ] Monitor `InterfaceFlags`
- [ ] Monitor CA registry changes
- [ ] Monitor CA RPC traffic
- [ ] Monitor certificate requests
- [ ] Monitor event 4886 where configured
- [ ] Monitor certificate issuance
- [ ] Monitor event 4887 where configured
- [ ] Monitor privileged machine enrollment
- [ ] Monitor unexpected certificate templates
- [ ] Correlate authentication with issuance
- [ ] Correlate coercion with issuance
- [ ] Monitor subsequent certificate authentication

## Hardening

- [ ] Enable `IF_ENFORCEENCRYPTICERTREQUEST`
- [ ] Require RPC packet privacy
- [ ] Test legacy clients
- [ ] Restart Certificate Services through change control
- [ ] Review legacy dependencies
- [ ] Restrict CA network access
- [ ] Reduce NTLM
- [ ] Reduce coercion opportunities
- [ ] Restrict Tier 0 outbound authentication
- [ ] Harden certificate templates
- [ ] Review machine enrollment
- [ ] Review domain-controller enrollment
- [ ] Review ESC8
- [ ] Treat CA as Tier 0
- [ ] Baseline CA configuration

## Incident Response

- [ ] Identify affected CA
- [ ] Determine ESC11 exposure period
- [ ] Determine whether packet privacy was recently disabled
- [ ] Review configuration changes
- [ ] Identify suspicious requests
- [ ] Identify relayed identities
- [ ] Identify issued certificates
- [ ] Identify exposed private keys
- [ ] Review certificate authentication
- [ ] Review coercion activity
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Restore secure RPC configuration
- [ ] Investigate related relay paths

## Cleanup

- [ ] Stop relay listener
- [ ] Remove test certificates
- [ ] Revoke test certificate where required
- [ ] Delete test PFX
- [ ] Delete private keys
- [ ] Verify CA configuration unchanged
- [ ] Verify test identity unchanged
- [ ] Remove temporary test artifacts
- [ ] Record cleanup evidence

---

# ESC11 Testing Model

The normal RPC enrollment model is:

```text
Client
  |
  v
Authenticated RPC
  |
  v
Packet Privacy
  |
  v
MS-ICPR
  |
  v
Certification Authority
  |
  v
Certificate
```

The vulnerable model is:

```text
Client Authentication
        |
        v
No Required Packet Privacy
        |
        v
Relay Possible
```

The ESC11 attack model is:

```text
Victim
  |
  v
NTLM
  |
  v
Attacker Relay
  |
  v
MS-ICPR
  |
  v
Certification Authority
  |
  v
Certificate as Victim
```

The coercion-to-ESC11 model is:

```text
Attacker
   |
   v
Authentication Coercion
   |
   v
Victim
   |
   v
NTLM
   |
   v
ESC11 Relay
   |
   v
CA RPC
   |
   v
Certificate
```

The machine-account model is:

```text
Computer Account
       |
       v
NTLM Authentication
       |
       v
ESC11
       |
       v
Machine Certificate
       |
       v
Computer Authentication
```

The Tier 0 model is:

```text
Domain Controller
       |
       v
Coerced Authentication
       |
       v
ESC11
       |
       v
DC Certificate
       |
       v
Tier 0 Credential Material
```

The ESC8 comparison is:

```text
                 NTLM Relay
                     |
          +----------+----------+
          |                     |
          v                     v
        ESC8                  ESC11
          |                     |
          v                     v
         HTTP                   RPC
          |                     |
          v                     v
     Web Enrollment          MS-ICPR
```

The mitigation model is:

```text
MS-ICPR
   |
   v
IF_ENFORCEENCRYPTICERTREQUEST
   |
   v
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
   |
   v
Signed + Encrypted RPC
   |
   v
Relay Prevented
```

The safe-testing model is:

```text
Enumerate CA
    |
    v
Inspect InterfaceFlags
    |
    v
Confirm RPC Exposure
    |
    v
Confirm Enrollment Rights
    |
    v
Read-Only Evidence Enough?
    |
    +--> Yes -> Report
    |
    +--> No
            |
            v
      Dedicated Test Identity
            |
            v
      Controlled Authentication
            |
            v
      Controlled Relay
            |
            v
      Test Certificate
            |
            v
      Stop / Cleanup
```

The detection model is:

```text
Victim Authentication
        |
        v
RPC Enrollment
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

The defensive model is:

```text
RPC Packet Privacy
       +
Reduced NTLM
       +
Coercion Hardening
       +
Restricted CA Access
       +
Secure Templates
       +
Tier 0 Protection
       =
Reduced ESC11 Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I coerce a domain controller
and obtain its certificate?"

Ask:
"Can I establish the ESC11 condition
with configuration evidence or a
dedicated test identity without
touching Tier 0 production systems?"
```

For defenders:

```text
Do Not Assume:
"We do not have /certsrv/,
so AD CS cannot be relayed."

Ask:
"Which certificate enrollment
interfaces are exposed, and does
every RPC enrollment request require
packet privacy?"
```

The complete ESC11 relationship is:

```text
Authentication Source
        |
        v
NTLM
        |
        v
RPC Relay
        |
        v
MS-ICPR
        |
        v
Certificate Enrollment
        |
        v
Certificate Credential
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC8:

[AD CS ESC8](esc8.md)

ESC9:

[AD CS ESC9](esc9.md)

ESC10:

[AD CS ESC10](esc10.md)

NTLM Relay:

[NTLM Relay](../ntlm-relay.md)

Authentication Coercion:

[Authentication Coercion](../authentication-coercion.md)

Kerberos:

[Kerberos](../kerberos.md)

BloodHound:

[BloodHound](../bloodhound.md)

The next AD CS page is:

```text
docs/active-directory/ad-cs/esc12.md
```

---

# References

## Microsoft - ESC11 Security Assessment

[Microsoft Defender for Identity - Enforce Encryption for RPC Certificate Enrollment Interface](https://learn.microsoft.com/en-us/defender-for-identity/security-assessment-insecure-adcs-certificate-enrollment){ target="_blank" rel="noopener noreferrer" }

Microsoft describes ESC11 as an AD CS configuration where the RPC enrollment interface does not require packet privacy.

Microsoft states that enabling:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

forces:

```text
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
```

and mitigates the relay condition.

---

## Microsoft - MS-ICPR

[Microsoft - ICertPassage Remote Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-icpr/021b19a6-a8ec-4732-8c76-70933bf53e94){ target="_blank" rel="noopener noreferrer" }

MS-ICPR defines the RPC protocol used by clients to request and receive X.509 certificates from a Certification Authority.

---

## Microsoft - ICertPassage Interface

[Microsoft - ICertPassage Interface](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-icpr/d98e6cfb-87ba-4915-b3ec-a1b7c6129a53){ target="_blank" rel="noopener noreferrer" }

The interface exposes:

```text
CertServerRequest
```

and uses UUID:

```text
91ae6020-9e3c-11cf-8d7c-00aa00c091be
```

---

## Microsoft - CertServerRequest

[Microsoft - MS-ICPR CertServerRequest](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-icpr/0c6f150e-3ead-4006-b37f-ebbf9e2cf2e7){ target="_blank" rel="noopener noreferrer" }

Microsoft specifies that a CA configured with:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

must reject an RPC certificate request when:

```text
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
```

is not used.

---

## Microsoft - MS-WCCE Interface Flags

[Microsoft - MS-WCCE Configuration List](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-wcce/b3ac7b46-8ea7-440d-a4c5-656bb1286d56){ target="_blank" rel="noopener noreferrer" }

This specification defines CA interface flags including:

```text
IF_NORPCICERTREQUEST
IF_ENFORCEENCRYPTICERTREQUEST
IF_ENFORCEENCRYPTICERTADMIN
```

---

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Verify the installed release before operational testing:

```bash
certipy --version
certipy find -h
certipy relay -h
certipy auth -h
```

Current Certipy documentation supports:

```text
http://
```

targets for ESC8 and:

```text
rpc://
```

targets for ESC11.

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC11 demonstrates why AD CS assessment must examine more than certificate templates.

The vulnerable component is:

```text
Certificate Enrollment Transport
```

Specifically:

```text
MS-ICPR
```

over RPC.

The core condition is straightforward:

```text
RPC Enrollment
       |
       v
Packet Privacy Required?
       |
       +--> Yes -> Relay Mitigated
       |
       +--> No -> Investigate ESC11
```

Microsoft explicitly documents the defensive control:

```text
IF_ENFORCEENCRYPTICERTREQUEST
```

which requires:

```text
RPC_C_AUTHN_LEVEL_PKT_PRIVACY
```

for certificate-request RPC connections.

ESC11 is also important because organisations sometimes assess only:

```text
/certsrv/
```

and conclude that AD CS relay is not possible.

A better model is:

```text
AD CS Enrollment
       |
       +--> HTTP
       |     |
       |     v
       |    ESC8
       |
       +--> RPC
             |
             v
            ESC11
```

Both surfaces should be reviewed.

The practical impact of ESC11 depends heavily on the identity being relayed.

For example:

```text
Workstation$
```

and:

```text
DomainController$
```

have dramatically different security implications.

Therefore the correct severity model is:

```text
ESC11
  +
Relay Source
  +
Enrollment Rights
  +
Certificate Purpose
  +
Victim Privileges
  =
Actual Impact
```

For penetration testing, configuration evidence is often sufficient. Where active proof is required, a dedicated test computer provides a substantially safer validation method than coercing a production domain controller.

For defenders, the primary question is simple:

```text
Does every RPC certificate enrollment
connection require packet privacy?
```

If the answer is no, the CA's RPC enrollment configuration should be investigated and hardened.
