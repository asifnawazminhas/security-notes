# AD CS ESC8 - NTLM Relay to AD CS Web Enrollment

ESC8 is an Active Directory Certificate Services (AD CS) privilege escalation technique involving NTLM relay to an HTTP-based certificate enrollment endpoint.

Instead of stealing a password or NTLM hash, the attacker relays a victim's live NTLM authentication to an AD CS enrollment service.

If the enrollment endpoint accepts the relayed authentication and the victim can enroll in a certificate suitable for authentication, the attacker may obtain a certificate representing that victim.

A simplified ESC8 relationship is:

```text
Victim
  |
  v
NTLM Authentication
  |
  v
Attacker-Controlled Relay
  |
  v
AD CS HTTP Enrollment Endpoint
  |
  v
Certificate Request as Victim
  |
  v
Authentication Certificate
  |
  v
Certificate-Based Authentication
```

The classic target is:

```text
/certsrv/
```

provided by the Certification Authority Web Enrollment role service.

Modern ESC8 assessments should also examine other IIS-hosted AD CS enrollment services, including Certificate Enrollment Web Service (CES), where NTLM is accepted without adequate relay protection.

The central ESC8 question is:

```text
Can NTLM authentication from another domain
principal be relayed to an AD CS enrollment
endpoint and converted into a certificate
representing that principal?
```

!!! warning "Authorised testing only"
    NTLM relay can impersonate users and computers without obtaining their passwords. Begin with read-only endpoint, IIS, CA, and template enumeration. Do not coerce production domain controllers, relay production privileged identities, or request certificates for privileged systems merely to prove ESC8. Where active validation is explicitly authorised, use dedicated test identities and the minimum-impact authentication source available.

---

# ESC8 Concept

ESC8 combines two security mechanisms:

```text
NTLM Authentication
```

and:

```text
Certificate Enrollment
```

The attack converts:

```text
Temporary Authentication
```

into:

```text
Reusable Certificate Credential
```

Conceptually:

```text
NTLM Authentication
       |
       v
Relay
       |
       v
Certificate Enrollment
       |
       v
Certificate
```

This conversion is what makes ESC8 particularly important.

---

# NTLM Relay

NTLM relay is different from:

```text
NTLM Cracking
```

and:

```text
Pass-the-Hash
```

In an NTLM relay attack, the attacker forwards authentication messages between:

```text
Victim
```

and:

```text
Target Service
```

without needing to recover the victim's password.

---

# Relay Model

The normal authentication model is:

```text
Client
  |
  v
Server
```

The relay model is:

```text
Client
  |
  v
Attacker
  |
  v
Target Server
```

The attacker acts as an intermediary.

---

# ESC8 Relay Model

For ESC8:

```text
Victim
  |
  v
Attacker
  |
  v
AD CS Web Enrollment
  |
  v
Certificate Authority
```

The target web service believes the relayed NTLM authentication belongs to the legitimate victim.

---

# Why Certificates Make ESC8 Powerful

A normal relayed NTLM session is temporary.

ESC8 can potentially transform that session into:

```text
Certificate
```

which may remain valid for:

```text
Hours
Days
Months
Years
```

depending on the template.

Conceptually:

```text
One NTLM Authentication
       |
       v
Certificate Issuance
       |
       v
Longer-Lived Credential
```

---

# Certificate Authentication

If the resulting certificate supports Active Directory authentication, it may potentially be used for:

```text
Kerberos PKINIT
Schannel Authentication
Client Certificate Authentication
```

depending on the certificate and environment.

---

# ESC8 Prerequisites

A successful ESC8 path generally requires:

```text
AD CS Enrollment Endpoint
        +
Windows Integrated Authentication / NTLM
        +
Insufficient Relay Protection
        +
Relayable NTLM Authentication
        +
Victim Enrollment Rights
        +
Suitable Certificate Template
        +
Certificate Authentication Capability
        =
Potential ESC8
```

Every component should be validated.

---

# HTTP Enrollment Endpoints

AD CS can expose multiple web-based certificate services.

Important examples include:

```text
Certification Authority Web Enrollment
Certificate Enrollment Web Service
Certificate Enrollment Policy Web Service
```

Their roles and protocols differ.

Do not assume they are interchangeable.

---

# Certification Authority Web Enrollment

The classic Web Enrollment interface is normally available at:

```text
https://ca01.corp.example/certsrv/
```

or in older/insecure deployments:

```text
http://ca01.corp.example/certsrv/
```

Microsoft documents the Web Enrollment pages at:

```text
https://<servername>/certsrv
```

The role allows users with appropriate permissions to perform certificate enrollment operations through IIS.

---

# Common Web Enrollment Paths

During authorised enumeration, useful paths include:

```text
/certsrv/
/certsrv/certfnsh.asp
/certsrv/certnew.cer
/certsrv/certcarc.asp
```

The presence of:

```text
/certsrv/
```

is usually the primary indicator that classic CA Web Enrollment is installed.

---

# Certificate Enrollment Web Service

Certificate Enrollment Web Service is commonly abbreviated:

```text
CES
```

It provides HTTPS-based certificate enrollment and supports scenarios such as:

```text
Cross-Forest Enrollment
Extranet Enrollment
Automated Enrollment
```

CES can support Windows Integrated Authentication.

When NTLM is accepted without appropriate protection, relay exposure must be evaluated.

---

# Certificate Enrollment Policy Web Service

Certificate Enrollment Policy Web Service is commonly abbreviated:

```text
CEP
```

CEP helps clients obtain certificate enrollment policy.

It should be inventoried during AD CS web-service assessment.

However, do not assume:

```text
CEP
```

has the same certificate issuance behaviour as:

```text
CA Web Enrollment
```

or:

```text
CES
```

---

# Current Certipy Scope

Current Certipy ESC8 documentation is particularly important here.

Certipy's:

```text
relay
```

function for ESC8 specifically targets the classic Web Enrollment service, including the:

```text
/certsrv/certfnsh.asp
```

workflow.

Do not assume Certipy's ESC8 relay implementation automatically supports every CES or CEP deployment.

Always check:

```bash
certipy relay -h
```

for the installed release.

---

# ESC8 and HTTP

Plain HTTP provides no TLS channel to which authentication can be bound.

Conceptually:

```text
HTTP
 |
 v
NTLM
 |
 v
No TLS Channel Binding
 |
 v
Relay Exposure
```

Therefore an AD CS enrollment endpoint that accepts NTLM over plain HTTP is a major ESC8 concern.

---

# ESC8 and HTTPS

HTTPS alone is not necessarily enough.

A deployment may have:

```text
HTTPS
```

but still allow NTLM relay if:

```text
Extended Protection for Authentication
```

is not appropriately enforced.

Conceptually:

```text
HTTPS
  |
  v
NTLM
  |
  v
EPA Disabled
  |
  v
Potential Relay
```

---

# Extended Protection for Authentication

Extended Protection for Authentication is commonly abbreviated:

```text
EPA
```

EPA provides additional protection against credential forwarding and relay attacks by binding authentication to properties of the protected connection.

Conceptually:

```text
NTLM Authentication
        |
        v
TLS Connection
        |
        v
Channel Binding
        |
        v
Authentication Bound to Channel
```

---

# Channel Binding

Channel Binding Tokens can associate authentication with the underlying secure TLS channel.

This makes:

```text
Authentication Captured on Connection A
```

less useful when forwarded to:

```text
Connection B
```

Conceptually:

```text
Victim TLS Channel
       |
       v
Authentication
       |
       X
Different Relay TLS Channel
```

---

# HTTP Cannot Provide TLS Channel Binding

Because plain HTTP has no TLS channel:

```text
HTTP
 |
 v
No TLS
 |
 v
No TLS Channel Binding
```

This is one reason Microsoft recommends HTTPS together with EPA for AD CS IIS enrollment services.

---

# ESC8 Vulnerable Pattern

A typical vulnerable pattern is:

```text
AD CS Web Enrollment
       |
       v
Windows Authentication
       |
       v
NTLM Accepted
       |
       v
HTTP
```

or:

```text
AD CS Web Enrollment
       |
       v
Windows Authentication
       |
       v
NTLM Accepted
       |
       v
HTTPS
       |
       v
EPA Not Enforced
```

---

# Current Windows Server Context

ESC8 configuration defaults have evolved.

SpecterOps reported in 2025 that insecure NTLM-relay behaviour remained the default for older Windows Server generations such as Windows Server 2022 and earlier, while Windows Server 2025 changed the default posture for new deployments.

Therefore:

```text
Windows Server Version
```

is useful context, but it is not proof of vulnerability.

Always inspect the actual IIS configuration.

---

# Microsoft Defender for Identity

Microsoft Defender for Identity currently includes a security posture assessment specifically for:

```text
Insecure ADCS certificate enrollment IIS endpoints (ESC8)
```

Microsoft describes an endpoint as vulnerable when it allows NTLM authentication without appropriate protections such as HTTPS and EPA.

This reinforces that ESC8 remains a current configuration issue rather than only a historical technique.

---

# ESC8 vs ESC6

ESC6 concerns:

```text
Requester-Supplied SAN
```

at the CA policy level.

ESC8 concerns:

```text
NTLM Relay
```

to certificate enrollment.

They are different attack paths.

---

# ESC8 vs ESC7

ESC7 concerns:

```text
CA Administrative Permissions
```

ESC8 does not require the attacker to administer the CA.

Instead:

```text
Victim's Enrollment Rights
```

are used through relayed authentication.

---

# ESC8 vs ESC11

ESC8 and ESC11 are closely related but target different enrollment transports.

Conceptually:

```text
ESC8
 |
 v
HTTP / HTTPS Enrollment
```

versus:

```text
ESC11
 |
 v
RPC Certificate Enrollment
```

ESC11 becomes relevant where RPC enrollment does not enforce the required packet privacy protections.

---

# ESC8 vs NTLM Relay to LDAP

Traditional relay may target:

```text
LDAP
LDAPS
SMB
HTTP
MSSQL
```

ESC8 specifically targets:

```text
AD CS HTTP-Based Enrollment
```

The post-authentication action is:

```text
Request Certificate
```

---

# ESC8 Attack Chain

A generic chain is:

```text
Victim
  |
  v
NTLM Authentication
  |
  v
Relay Listener
  |
  v
AD CS Enrollment Endpoint
  |
  v
Victim Authenticated
  |
  v
Certificate Request
  |
  v
Certificate Issued
```

The certificate may then become an authentication credential.

---

# Authentication Source

ESC8 requires an NTLM authentication source.

This may occur naturally or through an explicitly authorised coercion test.

Potential sources include:

```text
User Authentication
Computer Authentication
Application Authentication
Authentication Coercion
```

---

# Authentication Coercion

Authentication coercion causes a Windows system to authenticate to another host.

The relationship is:

```text
Attacker
   |
   v
Coercion Trigger
   |
   v
Victim
   |
   v
Outbound NTLM Authentication
```

That authentication may then become relayable.

See:

[Authentication Coercion](../authentication-coercion.md)

---

# Common Coercion Families

Historically relevant coercion techniques include:

```text
MS-RPRN / PrinterBug
MS-EFSRPC / PetitPotam
MS-DFSNM / DFSCoerce
Other RPC-Based Coercion
WebDAV-Based Authentication Paths
Application-Specific Coercion
```

The available technique depends on:

```text
Victim Services
Patching
Firewall
RPC Exposure
WebClient
Protocol Configuration
```

---

# Do Not Treat Coercion as ESC8

Coercion and ESC8 are separate stages.

```text
Authentication Coercion
       |
       v
Produces Authentication
```

while:

```text
ESC8
       |
       v
Relays Authentication to AD CS
```

A complete attack may combine both.

---

# High-Value Victims

Machine accounts can be particularly important.

For example:

```text
Domain Controller$
```

may have enrollment rights for a machine or domain-controller authentication certificate.

Conceptually:

```text
DC01$
  |
  v
NTLM Authentication
  |
  v
Relay to AD CS
  |
  v
Certificate for DC01$
```

This can have severe consequences.

---

# Do Not Coerce Domain Controllers by Default

A domain controller is a critical production system.

Do not perform:

```text
DC Coercion
```

merely because a tool indicates that it may work.

Use:

```text
Dedicated Test Computer
```

where possible.

---

# Machine Templates

Machine accounts commonly have access to templates such as:

```text
Machine
Computer
Domain Controller
Domain Controller Authentication
Kerberos Authentication
```

depending on environment configuration.

The exact template must be enumerated.

---

# User Templates

Users may have access to:

```text
User
Smartcard User
Custom Authentication Templates
VPN Certificates
Client Authentication Certificates
```

Again, the resulting certificate purpose matters.

---

# Template Requirement

The relayed victim must be authorised to enroll in the selected template.

Conceptually:

```text
Relay Victim
      |
      v
Template ACL
      |
      v
Enroll?
```

If:

```text
No
```

then the certificate request should fail.

---

# Authentication-Capable Certificate

A certificate useful for Active Directory authentication typically needs appropriate certificate purposes.

Relevant EKUs may include:

```text
Client Authentication
1.3.6.1.5.5.7.3.2

Smart Card Logon
1.3.6.1.4.1.311.20.2.2

PKINIT Client Authentication
1.3.6.1.5.2.3.4
```

The complete certificate configuration should be evaluated.

---

# NTAuth Trust

For certificate-based domain authentication, the issuing CA must also participate appropriately in the domain's certificate trust model.

This can include:

```text
NTAuthCertificates
```

where relevant.

A certificate issued by an unrelated CA does not automatically become a valid Active Directory authentication credential.

---

# Enumerating Web Enrollment

Start with normal HTTPS/HTTP service discovery.

For example:

```bash
curl -k -I https://ca01.corp.example/certsrv/
```

and, where HTTP is exposed:

```bash
curl -I http://ca01.corp.example/certsrv/
```

---

# Expected Responses

Possible responses include:

```text
200 OK
401 Unauthorized
302 Redirect
403 Forbidden
404 Not Found
```

A:

```text
401
```

can still be useful because authentication headers may reveal the supported mechanisms.

---

# Inspect Authentication Headers

Use:

```bash
curl -k -I https://ca01.corp.example/certsrv/
```

Review:

```text
WWW-Authenticate
```

Potential values include:

```text
Negotiate
NTLM
```

---

# Example

Conceptually:

```text
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Negotiate
WWW-Authenticate: NTLM
```

This indicates Windows Integrated Authentication mechanisms are being offered.

It does not by itself prove relayability.

---

# Discover with Nmap

For authorised service discovery:

```bash
nmap -Pn -p80,443 ca01.corp.example
```

Relevant services may include:

```text
80/tcp
443/tcp
```

---

# HTTP Enumeration

Where approved:

```bash
nmap -Pn -p80,443 --script http-title ca01.corp.example
```

This may help identify IIS-hosted services.

---

# IIS Enumeration

From an authorised administrative session on the server:

```powershell
Import-Module WebAdministration

Get-Website |
    Select-Object Name,State,PhysicalPath,Bindings
```

---

# Enumerate IIS Applications

```powershell
Get-WebApplication |
    Select-Object Path,ApplicationPool,PhysicalPath
```

Look for AD CS-related applications.

---

# Windows Authentication

Inspect IIS Windows Authentication configuration.

For example:

```powershell
Get-WebConfigurationProperty `
    -Filter '/system.webServer/security/authentication/windowsAuthentication' `
    -Name enabled `
    -PSPath 'IIS:\'
```

For production assessment, use IIS Manager or configuration-management tooling to verify the specific enrollment application's effective configuration.

---

# IIS Manager

The relevant configuration is typically under:

```text
IIS Manager
   |
   v
Site / AD CS Enrollment Application
   |
   v
Authentication
   |
   v
Windows Authentication
```

Review:

```text
Enabled / Disabled
Providers
Extended Protection
```

---

# Extended Protection

For the AD CS enrollment application, inspect:

```text
Extended Protection
```

The secure target state should enforce the organisation's supported EPA configuration.

For ESC8 analysis, the important question is whether EPA is actually enforced on the relevant endpoint.

---

# Require SSL

Also inspect whether IIS requires:

```text
SSL
```

for the enrollment application.

Conceptually:

```text
Require SSL
    +
EPA
    =
Stronger Relay Protection
```

---

# Do Not Check Only Port 443

The presence of HTTPS does not mean HTTP has been disabled.

Test both:

```text
80
443
```

where in scope.

A deployment may expose:

```text
HTTPS Securely
```

while accidentally leaving:

```text
HTTP
```

available.

---

# Redirect Is Not the Same as Protection

An HTTP-to-HTTPS redirect should not automatically be treated as equivalent to preventing NTLM authentication over HTTP.

Verify the actual authentication flow.

The secure objective is:

```text
No Relayable Authentication over HTTP
```

not merely:

```text
Browser Eventually Lands on HTTPS
```

---

# Certipy Discovery

Use:

```bash
certipy find -u 'audit-user@corp.example' -p 'PASSWORD' -dc-ip 10.10.10.10 -stdout
```

Review CA information for:

```text
Web Enrollment
Enrollment Services
ESC8
```

depending on the installed Certipy release.

---

# Verify Certipy Version

```bash
certipy --version
```

Then:

```bash
certipy find -h
```

and:

```bash
certipy relay -h
```

This is especially important because relay behaviour and supported endpoint types can change between releases.

---

# Certipy Relay

Certipy provides:

```text
relay
```

functionality for authorised ESC8 testing.

Before using it:

```bash
certipy relay -h
```

Review the exact syntax supported by the installed version.

Current Certipy documentation notes that its ESC8 relay implementation targets classic Web Enrollment rather than assuming support for every CES/CEP endpoint.

---

# Impacket ntlmrelayx

Impacket includes:

```text
ntlmrelayx.py
```

which supports NTLM relay testing against multiple protocols and services.

Check the installed version:

```bash
ntlmrelayx.py -h
```

or:

```bash
impacket-ntlmrelayx -h
```

depending on packaging.

---

# Why Version Checking Matters

Relay tooling changes frequently.

Older guides may use options that:

```text
No Longer Exist
Have Changed Names
Have Different Defaults
Support Different AD CS Endpoints
```

Always verify local help before active testing.

---

# Safe Relay Validation

The preferred validation model is:

```text
Dedicated Test Computer
       |
       v
Approved NTLM Authentication
       |
       v
Relay Listener
       |
       v
Test AD CS Enrollment
       |
       v
Test Certificate
```

Do not begin with:

```text
Domain Controller
```

or:

```text
Privileged User
```

---

# Test Account Model

For example:

```text
CORP\ESC8-TEST$
```

can represent a dedicated test computer.

The objective is to determine:

```text
Can Its Authentication Be Relayed?
```

and:

```text
Can Its Enrollment Rights Be Used?
```

without affecting a privileged production identity.

---

# Minimum Proof

A useful proof may establish:

```text
NTLM Accepted
        +
EPA Not Enforced
        +
Test Authentication Relayed
        +
Test Certificate Issued
```

There is normally no need to escalate further once the vulnerability is proven.

---

# Stop After Certificate Issuance

If a certificate for the approved test account is successfully issued:

```text
Certificate Obtained
       |
       v
ESC8 Proven
```

In many assessments this is sufficient.

Authentication with the certificate should only be performed when needed to establish impact.

---

# Certificate Inspection

Inspect the issued certificate.

Record:

```text
Subject
SAN
Issuer
Serial Number
Thumbprint
Template
EKUs
Validity
SID Security Extension
```

---

# Windows Inspection

```cmd
certutil -dump esc8-test.cer
```

---

# OpenSSL Inspection

For DER:

```bash
openssl x509 -in esc8-test.cer -inform DER -text -noout
```

For PEM:

```bash
openssl x509 -in esc8-test.pem -text -noout
```

---

# Certificate Authentication

If authentication validation is explicitly required, review:

```bash
certipy auth -h
```

before testing.

Use only the approved test identity.

---

# ESC8 and Computer Accounts

Machine-account relay is important because computer certificates may enable:

```text
PKINIT
Schannel
Machine Authentication
```

The resulting permissions depend on the computer account.

---

# Computer Account Does Not Mean Low Impact

A machine account may have access to:

```text
Its Own Host
Network Services
Delegated Resources
Active Directory Objects
SCCM Infrastructure
Other Application Resources
```

Therefore evaluate the actual victim.

---

# Domain Controller Certificates

A certificate representing a domain controller is particularly sensitive.

Potential consequences can extend into:

```text
Kerberos
Directory Services
Replication-Related Access
Domain Authentication
```

Do not actively demonstrate these effects unless explicitly required.

---

# ESC8 and S4U

A machine certificate may enable authentication as the machine account.

Depending on the environment and host relationship, subsequent Kerberos operations can potentially provide access to services on that machine.

This is a post-ESC8 impact path rather than part of the ESC8 configuration itself.

---

# ESC8 and SCCM

Modern enterprise environments may contain additional attack paths involving computer accounts with privileged access to systems such as:

```text
Microsoft Configuration Manager
```

A relayed machine identity should therefore be evaluated based on its actual permissions rather than assuming all machine accounts have equal impact.

---

# ESC8 and Authentication Coercion

A common complete attack chain is:

```text
Attacker
   |
   v
Coerce Victim
   |
   v
Victim NTLM
   |
   v
Relay
   |
   v
AD CS
   |
   v
Certificate
```

See:

[Authentication Coercion](../authentication-coercion.md)

---

# ESC8 and PrinterBug

Historically:

```text
MS-RPRN
```

could be used to trigger machine authentication from systems exposing the relevant print-spooler functionality.

Conceptually:

```text
PrinterBug
    |
    v
Machine NTLM
    |
    v
ESC8 Relay
```

Availability depends on the target's configuration and hardening.

---

# ESC8 and PetitPotam

PetitPotam demonstrated authentication coercion through:

```text
MS-EFSRPC
```

Conceptually:

```text
EFSRPC
   |
   v
Victim Authentication
   |
   v
ESC8
```

Microsoft introduced mitigations and organisations may have additional controls.

Do not assume a specific coercion method is available.

---

# ESC8 and DFSCoerce

DFS-related RPC interfaces have also been used in authentication coercion research.

Again:

```text
Coercion
```

is the authentication source.

```text
ESC8
```

is the relay destination and certificate conversion.

---

# Coercer

Coercer can help identify authentication coercion opportunities in authorised environments.

Before using it:

```bash
coercer --help
```

Tool support and technique coverage evolve over time.

Use test systems before production infrastructure.

---

# Responder

Responder is frequently associated with NTLM capture and relay workflows.

However:

```text
Capture
```

and:

```text
Relay
```

are different objectives.

Conceptually:

```text
NTLM Authentication
       |
       +--> Capture
       |
       +--> Relay
```

Do not unnecessarily collect or crack credentials when the assessment objective is relay validation.

---

# NTLM Relay Reflection Restrictions

NTLM contains protections that prevent several simple reflection scenarios.

The attacker generally relays authentication:

```text
From One Security Context / Service
```

to:

```text
Another Suitable Service
```

rather than simply reflecting authentication back to the exact same protected context.

---

# Signing and Relay Protection

Different protocols use different anti-relay controls.

Examples include:

```text
SMB Signing
LDAP Signing
LDAP Channel Binding
HTTP EPA
```

For ESC8 the most important control is:

```text
HTTP(S) Extended Protection
```

together with secure transport and authentication configuration.

---

# HTTPS Alone Is Insufficient

Remember:

```text
HTTPS
   !=
Automatic NTLM Relay Protection
```

The stronger model is:

```text
HTTPS
   +
EPA
```

where NTLM must remain enabled.

---

# Kerberos vs NTLM

Where possible, organisations should reduce reliance on:

```text
NTLM
```

and prefer stronger authentication such as:

```text
Kerberos
```

However, simply seeing:

```text
Negotiate
```

does not prove that NTLM cannot be used.

The effective IIS provider and authentication configuration must be examined.

---

# NTLM Provider

IIS Windows Authentication may expose providers such as:

```text
Negotiate
NTLM
```

If NTLM is unnecessary, removing or disabling its use can reduce relay exposure.

Test compatibility before changing production enrollment services.

---

# Endpoint Enumeration Workflow

A practical read-only workflow is:

```text
Identify Enterprise CAs
       |
       v
Identify HTTP / HTTPS Services
       |
       v
Locate AD CS Enrollment Applications
       |
       v
Inspect Authentication
       |
       v
Is NTLM Accepted?
       |
       v
Is HTTP Available?
       |
       v
Is HTTPS Required?
       |
       v
Is EPA Enforced?
       |
       v
Enumerate Victim Enrollment Rights
       |
       v
Assess ESC8
```

---

# Template Enumeration Workflow

For each vulnerable enrollment endpoint:

```text
Identify Target CA
       |
       v
Enumerate Published Templates
       |
       v
Who Can Enroll?
       |
       v
Authentication EKU?
       |
       v
Potential Relay Victims
```

---

# BloodHound

BloodHound can help represent AD CS relay relationships.

Modern BloodHound data can expose paths associated with:

```text
CoerceAndRelayNTLMToADCS
```

and relationships between:

```text
Principal
Certificate Template
Enterprise CA
Vulnerable Enrollment Endpoint
```

See:

[BloodHound](../bloodhound.md)

---

# BloodHound Interpretation

A graph relationship may conceptually show:

```text
Domain Computers
       |
       v
Enroll
       |
       v
Machine Template
       |
       v
Enterprise CA
       |
       v
Vulnerable ESC8 Endpoint
```

This does not mean every computer can automatically be compromised.

The attacker still requires:

```text
Relayable Authentication
```

from the victim.

---

# Detection

ESC8 detection requires visibility across multiple stages.

A useful model is:

```text
Coercion
   |
   v
NTLM Authentication
   |
   v
AD CS Enrollment
   |
   v
Certificate Issuance
   |
   v
Certificate Authentication
```

---

# Detect NTLM to AD CS

Monitor NTLM authentication to servers hosting AD CS enrollment endpoints.

Questions include:

```text
Which Account?
Which Source?
Which CA Endpoint?
Was NTLM Expected?
Was the Source Unusual?
```

---

# Detect Unexpected Machine Enrollment

A suspicious pattern can be:

```text
Machine Account
       |
       v
Web Enrollment
```

especially when machine certificate enrollment normally occurs through:

```text
Autoenrollment
RPC
```

rather than interactive web enrollment.

---

# Event 4886

Where Certificate Services auditing is configured:

```text
4886
```

can indicate that Certificate Services received a certificate request.

---

# Event 4887

```text
4887
```

can indicate that Certificate Services approved a request and issued a certificate.

---

# Correlate Requester and Source

Where telemetry permits, correlate:

```text
Requester
       |
       v
Certificate Request
```

with:

```text
Network Source
```

An unusual source can indicate relay.

---

# Example Suspicious Pattern

Conceptually:

```text
Requester:
DC01$

Enrollment:
Machine Certificate

HTTP Source:
Workstation Subnet

Time:
Immediately after RPC activity against DC01
```

This deserves investigation.

---

# IIS Logging

IIS logs can provide valuable ESC8 evidence.

Review:

```text
Client IP
URI
Username
HTTP Method
Status Code
User Agent
Timestamp
```

for enrollment endpoints.

---

# Important URI

For classic Web Enrollment, monitor access to:

```text
/certsrv/
```

and certificate-request processing pages.

---

# Correlate IIS and CA Logs

A strong detection correlation is:

```text
IIS Authentication
       |
       v
/certsrv/ Request
       |
       v
CA Request
       |
       v
Certificate Issued
```

---

# Network Detection

Monitor unexpected NTLM authentication flows involving:

```text
Workstation -> CA Web Server
Server -> CA Web Server
Domain Controller -> CA Web Server
```

based on expected architecture.

---

# Detect Authentication Coercion

Coercion detection may include:

```text
Unexpected RPC Calls
Unusual SMB Connections
Outbound Authentication
Print Spooler Activity
EFSRPC Activity
DFS RPC Activity
```

Exact telemetry depends on the coercion method.

---

# Detect Certificate Authentication

If the issued certificate is subsequently used for Kerberos PKINIT, authentication telemetry may include:

```text
4768
```

Correlate:

```text
Certificate Issuance
```

with:

```text
TGT Request
```

---

# Certificate Lifetime

A certificate can remain useful after the original NTLM relay session ends.

Therefore incident investigations should extend beyond:

```text
Time of Relay
```

through:

```text
Certificate Expiration
```

unless the certificate has been revoked and revocation is reliably enforced.

---

# Hardening ESC8

The primary defence is:

```text
Remove or Protect HTTP-Based Enrollment
```

---

# Remove Web Enrollment If Unnecessary

If:

```text
Certification Authority Web Enrollment
```

is not required, remove the role service.

This eliminates the classic:

```text
/certsrv/
```

ESC8 target.

---

# Require HTTPS

Where web enrollment is required:

```text
Require HTTPS
```

Do not permit authentication to the enrollment application over plain HTTP.

---

# Enable Extended Protection

Where Windows Authentication is required:

```text
Enable Extended Protection for Authentication
```

and use the strongest setting supported by the environment.

Microsoft specifically recommends EPA as a mitigation for AD CS NTLM relay exposure.

---

# IIS Conceptual Hardening

The desired configuration is:

```text
AD CS Enrollment
       |
       v
HTTPS Required
       |
       v
Windows Authentication
       |
       v
EPA Enforced
```

---

# IIS Manager

For CA Web Enrollment, the relevant controls are found around:

```text
IIS Manager
   |
   v
AD CS Web Enrollment Site / Application
   |
   v
Authentication
   |
   v
Windows Authentication
   |
   v
Advanced Settings
   |
   v
Extended Protection
```

Test changes before production deployment.

---

# Certificate Enrollment Web Service

CES requires its own hardening review.

Do not assume that securing:

```text
/certsrv/
```

also secures:

```text
CES
```

Inventory every installed AD CS enrollment role service.

---

# Disable NTLM Where Possible

If business requirements permit:

```text
Disable NTLM
```

for the enrollment endpoint.

This removes the authentication mechanism used by classic NTLM relay.

Compatibility testing is essential.

---

# Prefer Kerberos

Where supported:

```text
Kerberos
```

provides a stronger authentication model than NTLM for integrated domain authentication.

However, provider configuration must ensure that clients cannot silently fall back to NTLM where that would recreate relay exposure.

---

# Restrict Enrollment Rights

Even with endpoint hardening, certificate templates should follow least privilege.

Review:

```text
Domain Users
Domain Computers
Authenticated Users
Service Accounts
Custom Groups
```

for unnecessary enrollment rights.

---

# Harden Authentication Templates

Templates capable of:

```text
Client Authentication
Smart Card Logon
PKINIT
```

deserve additional scrutiny.

---

# Disable Unnecessary Templates

If a template is not required:

```text
Unpublish
```

or retire it according to organisational PKI procedures.

---

# Restrict Authentication Coercion

ESC8 becomes substantially harder if attackers cannot obtain relayable authentication.

Defensive controls include:

```text
Disable Unnecessary Print Spooler
Restrict RPC Exposure
Harden EFSRPC Exposure
Restrict WebClient
Segment Networks
Restrict Outbound SMB
Restrict Inbound Services
```

according to business requirements.

---

# Restrict Outbound SMB

Where appropriate, block:

```text
TCP/445
```

from internal systems to unnecessary destinations, particularly public networks.

This reduces several coercion and relay paths.

---

# Host Firewalling

Restrict unnecessary inbound access to:

```text
RPC
SMB
HTTP
Other Coercion-Relevant Services
```

especially on sensitive systems.

---

# Domain Controllers

Domain controllers deserve particularly strict controls.

Consider:

```text
Disable Print Spooler if not required
Restrict outbound authentication paths
Restrict unnecessary RPC exposure
Monitor certificate enrollment
Protect machine certificate templates
```

---

# EPA Validation

After remediation, do not assume the IIS setting is correct simply because:

```text
HTTPS Works
```

Validate:

```text
HTTP Rejected / Unavailable
NTLM Behaviour
EPA Enforcement
Normal Enrollment Functionality
```

---

# Microsoft Defender for Identity

Where available, Microsoft Defender for Identity's certificate security posture assessments can help identify:

```text
Insecure AD CS Certificate Enrollment IIS Endpoints
```

This can provide continuous defensive visibility into ESC8 configuration.

---

# Baseline Enrollment Endpoints

Maintain an inventory of:

```text
CA
Enrollment Server
Web Enrollment
CES
CEP
HTTP
HTTPS
Authentication Providers
EPA State
Templates
```

---

# Incident Response

If ESC8 abuse is suspected:

```text
Identify Enrollment Endpoint
       |
       v
Identify Relayed Identity
       |
       v
Identify Certificate Request
       |
       v
Identify Issued Certificate
       |
       v
Identify Authentication
       |
       v
Revoke Certificate
       |
       v
Remove Relay Condition
```

---

# Identify the Victim

Determine whether the relayed identity was:

```text
User
Computer
Server
Domain Controller
Service Account
```

The potential impact differs significantly.

---

# Identify the Authentication Source

Determine how NTLM authentication was obtained.

Possible sources include:

```text
Natural Authentication
Coercion
Poisoning
Application Behaviour
WebDAV
SMB
RPC
```

---

# Identify Certificate Requests

Review CA records for the affected account.

Record:

```text
Request ID
Requester
Template
Subject
SAN
Issue Time
Disposition
```

---

# Identify Issued Certificate

Record:

```text
Serial Number
Thumbprint
Issuer
Template
Subject
SAN
EKUs
Validity
```

---

# Review IIS Logs

Look for the corresponding web enrollment activity.

Correlate:

```text
Timestamp
Username
Source IP
URI
HTTP Status
```

with the CA request.

---

# Identify Certificate Authentication

Review whether the certificate was subsequently used for:

```text
Kerberos PKINIT
Schannel
Client TLS
VPN
Other Certificate Authentication
```

---

# Revoke the Certificate

If a malicious certificate was issued:

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

# Password Reset Is Not Enough

ESC8 demonstrates why certificate compromise differs from password compromise.

```text
Reset Password
     |
     X
Issued Certificate
```

A password reset does not inherently invalidate an already issued certificate.

---

# Disable the Relay Path

Remediation may include:

```text
Remove Web Enrollment
Require HTTPS
Enable EPA
Disable NTLM
Restrict Coercion
Restrict Enrollment
```

depending on the architecture.

---

# Investigate Other Victims

Do not assume only one identity was relayed.

Review the exposure period for:

```text
Other Users
Other Computers
Other Domain Controllers
```

that authenticated to the vulnerable endpoint.

---

# Review Other AD CS Endpoints

If one vulnerable IIS enrollment endpoint exists, inventory:

```text
Other CAs
Other Web Enrollment Servers
CES
CEP
Legacy Enrollment Servers
```

for similar configuration.

---

# Reporting ESC8

Avoid finding titles such as:

```text
ESC8 Found
```

Prefer:

```text
AD CS Web Enrollment Is Vulnerable to NTLM Relay
```

or:

```text
Missing Extended Protection Allows NTLM Relay to Certificate Enrollment
```

or:

```text
Insecure AD CS HTTP Enrollment Permits Certificate-Based Identity Impersonation
```

---

# Example Finding

```text
Finding:
AD CS Web Enrollment Is Vulnerable to NTLM Relay

Affected Host:
ca01.corp.example

Affected Endpoint:
https://ca01.corp.example/certsrv/

Affected CA:
CORP-CA01

Description:
The Active Directory Certificate Services Web Enrollment interface
accepts Windows Integrated Authentication and permits NTLM
authentication without enforcing Extended Protection for
Authentication.

This allows NTLM authentication from another domain principal to be
relayed to the certificate enrollment endpoint.

During controlled validation, authentication from a dedicated test
computer account was relayed to the Web Enrollment service.

The relayed identity was able to request a certificate from a
template for which the test computer possessed enrollment rights.

No privileged production identity was used during validation.

Impact:
An attacker able to obtain or coerce NTLM authentication from a user
or computer may be able to relay that authentication to AD CS and
request a certificate representing the victim.

Where the certificate supports Active Directory authentication, it
may provide reusable certificate credentials for the relayed
identity.

The severity depends on which identities can be coerced and what
permissions those identities possess.

A successfully relayed privileged computer or domain controller may
result in severe domain compromise.

Recommendation:
Remove the Certification Authority Web Enrollment role service if it
is not required.

Where web enrollment is required, enforce HTTPS and Extended
Protection for Authentication on the IIS enrollment application.

Disable NTLM for the enrollment endpoint where operationally
possible.

Review certificate-template enrollment permissions and restrict
authentication-capable templates according to least privilege.

Reduce authentication coercion opportunities and monitor NTLM
authentication, IIS enrollment activity, certificate issuance, and
subsequent certificate-based authentication.
```

---

# Severity Assessment

ESC8 severity depends on:

```text
Vulnerable Endpoint
       +
Relayable NTLM
       +
Coercion / Authentication Source
       +
Victim Identity
       +
Enrollment Rights
       +
Certificate Purpose
       +
Victim Privileges
       =
Severity
```

---

# Critical Example

```text
Domain Controller
      |
      v
Coerced NTLM
      |
      v
ESC8
      |
      v
Domain Controller Certificate
      |
      v
Certificate Authentication
```

This may represent a critical domain-level attack path.

---

# High-Risk Server Example

```text
Privileged Server$
      |
      v
NTLM Relay
      |
      v
Machine Certificate
      |
      v
Machine Authentication
      |
      v
Privileged Resource Access
```

---

# Lower-Impact Example

```text
Dedicated Test User
      |
      v
Relay
      |
      v
Certificate
      |
      v
No Privileged Access
```

This may prove the vulnerability without demonstrating high-impact compromise.

---

# Evidence Checklist

For an ESC8 finding record:

```text
CA Name
CA Host
Enrollment Host
Enrollment Endpoint
HTTP / HTTPS
Windows Authentication
NTLM Accepted
EPA State
TLS Requirement
Victim Identity
Victim SID
Authentication Source
Coercion Method if Used
Certificate Template
Enrollment Rights
Authentication EKUs
Request ID
Certificate Serial Number
Certificate Thumbprint
Certificate Subject
Certificate SAN
Certificate Validity
SID Security Extension
Authentication Result
IIS Log Evidence
CA Log Evidence
Cleanup Result
```

---

# ESC8 Assessment Checklist

## Discovery

- [ ] Identify Enterprise CAs
- [ ] Identify CA hosts
- [ ] Identify enrollment servers
- [ ] Identify `/certsrv/`
- [ ] Identify CES
- [ ] Identify CEP
- [ ] Enumerate HTTP
- [ ] Enumerate HTTPS
- [ ] Identify IIS applications

## Authentication

- [ ] Determine whether Windows Authentication is enabled
- [ ] Determine whether NTLM is accepted
- [ ] Inspect `WWW-Authenticate`
- [ ] Determine whether Kerberos is available
- [ ] Determine whether NTLM fallback is possible
- [ ] Do not assume `Negotiate` means Kerberos only

## Relay Protection

- [ ] Determine whether HTTP is exposed
- [ ] Determine whether HTTPS is required
- [ ] Determine whether EPA is enabled
- [ ] Determine whether EPA is enforced
- [ ] Check each enrollment application separately
- [ ] Do not treat redirects as equivalent to protection

## Templates

- [ ] Enumerate templates published by target CA
- [ ] Identify user enrollment rights
- [ ] Identify computer enrollment rights
- [ ] Identify Client Authentication
- [ ] Identify Smart Card Logon
- [ ] Identify PKINIT capability
- [ ] Review certificate validity
- [ ] Review SID security extension
- [ ] Identify high-value eligible principals

## Authentication Sources

- [ ] Identify natural NTLM flows
- [ ] Review authentication coercion exposure
- [ ] Review Print Spooler exposure
- [ ] Review EFSRPC exposure
- [ ] Review DFS-related coercion
- [ ] Review WebDAV where relevant
- [ ] Review application-specific coercion
- [ ] Do not coerce critical production systems unnecessarily

## Tooling

- [ ] Verify Certipy version
- [ ] Review `certipy find -h`
- [ ] Review `certipy relay -h`
- [ ] Verify current Certipy endpoint support
- [ ] Review `ntlmrelayx.py -h`
- [ ] Use `curl` for endpoint inspection
- [ ] Use Nmap for service discovery
- [ ] Use BloodHound for attack-path context
- [ ] Use Coercer only within authorised scope
- [ ] Manually verify automated ESC8 findings

## Validation

- [ ] Prefer read-only validation first
- [ ] Obtain explicit approval for relay testing
- [ ] Use dedicated test identity
- [ ] Prefer dedicated test computer
- [ ] Do not begin with domain controller
- [ ] Relay only approved authentication
- [ ] Request only approved test certificate
- [ ] Stop after sufficient proof
- [ ] Inspect certificate
- [ ] Authenticate only if required
- [ ] Revoke test certificate where appropriate
- [ ] Delete private-key material

## Detection

- [ ] Monitor NTLM to enrollment servers
- [ ] Monitor IIS `/certsrv/` access
- [ ] Monitor unusual machine enrollment
- [ ] Monitor event 4886 where configured
- [ ] Monitor event 4887 where configured
- [ ] Correlate requester with network source
- [ ] Correlate IIS and CA logs
- [ ] Monitor coercion activity
- [ ] Monitor certificate authentication
- [ ] Correlate issuance with event 4768 where relevant
- [ ] Monitor CA configuration changes

## Hardening

- [ ] Remove Web Enrollment if unnecessary
- [ ] Require HTTPS
- [ ] Enable EPA
- [ ] Enforce EPA
- [ ] Disable NTLM where possible
- [ ] Prefer Kerberos
- [ ] Review CES independently
- [ ] Review CEP independently
- [ ] Restrict enrollment rights
- [ ] Harden authentication templates
- [ ] Remove unnecessary templates
- [ ] Reduce authentication coercion
- [ ] Disable unnecessary Print Spooler
- [ ] Restrict RPC exposure
- [ ] Restrict outbound SMB
- [ ] Apply host firewalling
- [ ] Protect domain controllers
- [ ] Baseline enrollment services
- [ ] Use Defender for Identity posture assessments where available

## Incident Response

- [ ] Identify vulnerable endpoint
- [ ] Identify relayed identity
- [ ] Identify authentication source
- [ ] Identify coercion technique
- [ ] Identify certificate request
- [ ] Identify request ID
- [ ] Identify issued certificate
- [ ] Record serial number
- [ ] Record thumbprint
- [ ] Review IIS logs
- [ ] Review CA logs
- [ ] Identify certificate authentication
- [ ] Revoke malicious certificates
- [ ] Publish revocation information
- [ ] Remove relay condition
- [ ] Review additional victims
- [ ] Review other enrollment endpoints

## Cleanup

- [ ] Revoke approved test certificate where required
- [ ] Remove test PFX
- [ ] Remove private key
- [ ] Remove temporary relay infrastructure
- [ ] Remove temporary listener configuration
- [ ] Verify no CA configuration changed
- [ ] Verify no template configuration changed
- [ ] Verify test account state
- [ ] Record cleanup evidence

---

# ESC8 Testing Model

The normal enrollment model is:

```text
User / Computer
      |
      v
AD CS Enrollment
      |
      v
Certificate
```

The relay model is:

```text
Victim
  |
  v
NTLM
  |
  v
Attacker
  |
  v
Target Service
```

The ESC8 model is:

```text
Victim
  |
  v
NTLM Authentication
  |
  v
Relay
  |
  v
AD CS Web Enrollment
  |
  v
Certificate
```

The coercion model is:

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
Relay
```

The complete model is:

```text
Coercion
   |
   v
Victim NTLM
   |
   v
Relay Listener
   |
   v
AD CS Enrollment
   |
   v
Certificate Request
   |
   v
Certificate
   |
   v
Certificate Authentication
```

The HTTP weakness model is:

```text
HTTP
 |
 v
NTLM
 |
 v
No TLS Channel Binding
 |
 v
Relay Exposure
```

The HTTPS weakness model is:

```text
HTTPS
  |
  v
NTLM
  |
  v
EPA Not Enforced
  |
  v
Relay Exposure
```

The secure model is:

```text
HTTPS
  +
EPA
  +
Restricted NTLM
  +
Restricted Enrollment
  =
Reduced ESC8 Risk
```

The machine-account model is:

```text
Computer$
    |
    v
NTLM
    |
    v
ESC8
    |
    v
Machine Certificate
    |
    v
Machine Authentication
```

The high-impact model is:

```text
Domain Controller$
       |
       v
Coercion
       |
       v
NTLM Relay
       |
       v
AD CS
       |
       v
DC Certificate
       |
       v
Domain-Level Impact
```

The safe-testing model is:

```text
Enumerate
   |
   v
Confirm Endpoint
   |
   v
Confirm NTLM
   |
   v
Confirm Missing Relay Protection
   |
   v
Identify Test Template
   |
   v
Use Test Identity
   |
   v
Controlled Relay
   |
   v
Test Certificate Issued
   |
   v
Stop
   |
   v
Revoke / Cleanup
```

The detection model is:

```text
Coercion
   |
   v
Unexpected NTLM
   |
   v
IIS Enrollment
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
Remove Unneeded Enrollment
          +
HTTPS
          +
EPA
          +
Reduced NTLM
          +
Template Least Privilege
          +
Coercion Hardening
          +
Monitoring
          =
Reduced ESC8 Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I coerce the domain controller?"

First Ask:
"Is the enrollment endpoint relayable,
and can I prove that safely using a
dedicated test identity?"
```

For defenders:

```text
Do Not Assume:
"We use HTTPS, so NTLM relay is fixed."

Ask:
"Is HTTPS required, is NTLM still accepted,
and is Extended Protection actually enforced?"
```

The complete ESC8 relationship is:

```text
Authentication Source
        |
        v
NTLM
        |
        v
Relayability
        |
        v
AD CS Enrollment Endpoint
        |
        v
Victim Enrollment Rights
        |
        v
Certificate
        |
        v
Victim Privileges
```

---

# Related Notes

AD CS overview:

[Active Directory Certificate Services](index.md)

AD CS enumeration:

[AD CS Enumeration](enumeration.md)

ESC1:

[AD CS ESC1](esc1.md)

ESC6:

[AD CS ESC6](esc6.md)

ESC7:

[AD CS ESC7](esc7.md)

NTLM:

[NTLM](../ntlm.md)

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
docs/active-directory/ad-cs/esc9.md
```

---

# References

## Microsoft - Certification Authority Web Enrollment

[Microsoft - Certification Authority Web Enrollment](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-authority-web-enrollment){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Certificate Enrollment Web Service

[Microsoft - Certificate Enrollment Web Service](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-enrollment-web-service){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - KB5005413

[Microsoft - KB5005413: Mitigating NTLM Relay Attacks on AD CS](https://support.microsoft.com/topic/kb5005413-mitigating-ntlm-relay-attacks-on-active-directory-certificate-services-ad-cs-3612b773-4043-4aa9-b23d-b87910cd3429){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Defender for Identity - ESC8 Assessment

[Microsoft Defender for Identity - Insecure AD CS Certificate Enrollment IIS Endpoints](https://learn.microsoft.com/en-us/defender-for-identity/security-assessment-insecure-adcs-certificate-enrollment){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Before operational testing, verify the installed release:

```bash
certipy --version
certipy find -h
certipy relay -h
certipy auth -h
```

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Certified Pre-Owned

[SpecterOps - Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - The Renaissance of NTLM Relay Attacks

[SpecterOps - The Renaissance of NTLM Relay Attacks](https://specterops.io/blog/2025/04/08/the-renaissance-of-ntlm-relay-attacks-everything-you-need-to-know/){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - There and Back Again

[SpecterOps - There and Back Again: An Operator's Guide on NTLM Relaying Egress](https://specterops.io/blog/2026/07/15/there-and-back-again-an-operators-guide-on-ntlm-relaying-egress/){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Steal or Forge Authentication Certificates](https://attack.mitre.org/techniques/T1649/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

ESC8 is fundamentally an authentication relay problem combined with certificate enrollment.

The important transformation is:

```text
NTLM Authentication
       |
       v
Certificate Credential
```

This distinguishes ESC8 from many ordinary NTLM relay attacks.

A successful relay session may last only briefly.

The certificate obtained through that session may remain valid significantly longer.

Therefore:

```text
Relay Session Ends
```

does not necessarily mean:

```text
Attacker Access Ends
```

ESC8 also demonstrates why AD CS cannot be assessed only by reviewing certificate templates.

A template may be securely configured while the enrollment transport remains vulnerable:

```text
Secure Template
      |
      v
Insecure Enrollment Endpoint
      |
      v
NTLM Relay
```

Likewise, simply deploying HTTPS does not automatically remediate ESC8.

The modern defensive question is:

```text
Is HTTPS Required?
        |
        v
Is NTLM Accepted?
        |
        v
Is EPA Enforced?
```

Microsoft's current Defender for Identity security posture guidance explicitly continues to assess insecure AD CS IIS enrollment endpoints as ESC8 when NTLM is accepted without the appropriate HTTPS/EPA protections.

Current relay research also shows that ESC8 remains operationally relevant in modern Active Directory environments.

The complete assessment should therefore examine:

```text
Enrollment Endpoint
       +
Authentication Protocol
       +
Relay Protection
       +
Authentication Source
       +
Victim Enrollment Rights
       +
Certificate Purpose
       +
Victim Privileges
```

Do not assess ESC8 solely by asking:

```text
Does /certsrv/ Exist?
```

and do not assess it solely by asking:

```text
Does Certipy Print ESC8?
```

Instead determine the complete path:

```text
Can Authentication Be Relayed?
        |
        v
Can the Relayed Identity Enroll?
        |
        v
What Certificate Can It Obtain?
        |
        v
What Can That Certificate Authenticate As?
        |
        v
What Privilege Does That Identity Have?
```

For penetration testers, a dedicated test machine account can often demonstrate the vulnerability without coercing a domain controller.

For defenders, the strongest approach is defence in depth:

```text
Remove Unnecessary Enrollment Services
        +
Require HTTPS
        +
Enforce EPA
        +
Reduce NTLM
        +
Harden Certificate Templates
        +
Reduce Authentication Coercion
        +
Monitor Enrollment
```

rather than depending on only one control.

ESC8 should ultimately be understood as a trust conversion:

```text
Relayable NTLM
      |
      v
Trusted Certificate
```

Preventing that conversion is the core objective.
