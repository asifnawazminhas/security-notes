# NTLM

NTLM is a family of Microsoft authentication protocols used by Windows systems for local and network authentication.

In modern Active Directory environments, Kerberos is generally the preferred authentication protocol. NTLM remains important because it is still encountered when Kerberos cannot be used, when applications explicitly use NTLM, when local accounts are involved, and in workgroup or legacy scenarios.

From a penetration testing and defensive perspective, understanding NTLM is essential because several different attack techniques are frequently grouped together incorrectly.

The most important distinction is:

```text
NT hash
   |
   +--> Pass-the-Hash
   |
   X
NetNTLMv2 challenge/response
   |
   +--> Capture
   +--> Offline password cracking
   +--> Relay when conditions permit
```

An **NT hash** and a captured **NetNTLMv2 challenge-response** are not the same thing.

This page explains NTLM architecture, authentication flows, NT hashes, NTLMv1 and NTLMv2, NTLMSSP, local and domain authentication, NTLM fallback, protocol interactions, capture, relay, Pass-the-Hash, security controls, detection, hardening, and authorised validation.

!!! warning "Authorised testing only"
    NTLM authentication testing can generate account lockouts, authentication events, network connections, captured authentication material, and privileged sessions. Perform testing only within explicitly authorised systems and scopes. Prefer controlled test accounts and lab systems when validating capture, relay, credential, or authentication behaviour.

---

## NTLM at a Glance

A simplified NTLM authentication flow is:

```text
Client
   |
   | 1. Negotiate
   v
Server
   |
   | 2. Challenge
   v
Client
   |
   | 3. Authentication response
   v
Server
   |
   +--> Local account?
   |       |
   |       +--> Validate against local account database
   |
   +--> Domain account?
           |
           +--> Domain Controller
                    |
                    +--> Validate authentication
```

The user's password is not normally transmitted directly across the network during NTLM challenge-response authentication.

Instead, authentication is based on proving knowledge of credential material by calculating a response to a server-generated challenge.

---

# Why NTLM Still Matters

Active Directory environments normally prefer Kerberos, but NTLM continues to appear in real networks.

Common situations include:

- local account authentication
- workgroup systems
- applications without Kerberos support
- applications explicitly configured for NTLM
- authentication using an IP address
- Kerberos configuration failures
- missing or incorrect Service Principal Names
- legacy applications
- SMB authentication
- HTTP Integrated Windows Authentication
- some LDAP authentication scenarios
- WinRM configurations
- proxy authentication
- network appliances
- third-party software
- fallback through the Negotiate security package

A penetration tester should therefore understand both:

```text
Kerberos
```

and:

```text
NTLM
```

They represent different authentication architectures and expose different security properties.

For detailed Kerberos coverage, see:

[Kerberos](kerberos.md)

---

# NTLM Terminology

NTLM terminology is frequently confusing because several related concepts use similar names.

A useful model is:

| Term | Meaning |
|---|---|
| LM | Legacy LAN Manager authentication/hash mechanism |
| NT hash | Hash derived from a Windows account password |
| NTLM | Microsoft authentication protocol family |
| NTLMv1 | Older NTLM challenge-response mechanism |
| NTLMv2 | Newer NTLM challenge-response mechanism |
| NTLMSSP | NTLM Security Support Provider protocol messaging |
| NetNTLMv1 | Common security-tool term for captured NTLMv1 network challenge-response material |
| NetNTLMv2 | Common security-tool term for captured NTLMv2 network challenge-response material |
| Pass-the-Hash | Authentication using an NT hash rather than the plaintext password |
| NTLM relay | Forwarding NTLM authentication to another service |
| NTLM capture | Obtaining NTLM challenge-response authentication material |

Do not treat these terms as interchangeable.

---

# NT Hash

Windows authentication commonly relies on a password-derived value referred to as the **NT hash**.

Conceptually:

```text
Password
   |
   v
Password transformation
   |
   v
NT hash
```

The NT hash is derived from the password and can be used by Windows authentication mechanisms.

A commonly encountered representation is:

```text
LMHASH:NTHASH
```

Modern tooling often uses a placeholder for the LM component when only the NT hash is relevant:

```text
aad3b435b51404eeaad3b435b51404ee:<NT_HASH>
```

The important security property is that possession of the NT hash may itself be sufficient for certain authentication operations.

This is the foundation of **Pass-the-Hash**.

```text
Plaintext password
       |
       v
     NT hash
       |
       +--------------------+
       |                    |
       v                    v
Normal authentication   Pass-the-Hash
```

An attacker does not necessarily need to recover the original plaintext password if a protocol or service accepts authentication derived from the hash.

---

# NT Hash vs NetNTLMv2

This distinction is critical.

## NT Hash

An NT hash is credential material derived from the account password.

Example conceptual form:

```text
Administrator
    |
    v
NT hash
    |
    +--> Pass-the-Hash
    +--> Credential reuse
    +--> Potential offline password recovery
```

## NetNTLMv2

NetNTLMv2 is a commonly used security-tool term for NTLMv2 challenge-response material captured during network authentication.

Conceptually:

```text
Server challenge
       +
Client credential material
       +
Authentication metadata
       |
       v
NTLMv2 response
```

Captured NetNTLMv2 material is typically associated with:

```text
NetNTLMv2
   |
   +--> Offline password cracking
   |
   +--> NTLM relay
   |
   X
Direct Pass-the-Hash
```

Therefore:

```text
NT hash != NetNTLMv2 response
```

This distinction should be maintained throughout testing and reporting.

---

# LM Authentication

LAN Manager authentication predates NTLM.

LM password hashing has severe cryptographic weaknesses and should be considered obsolete.

Historically:

```text
Password
   |
   v
LM transformation
   |
   v
LM hash
```

Legacy LM behaviour is significantly weaker than modern Windows authentication mechanisms.

Modern environments should not rely on LM authentication.

During an assessment, evidence of LM compatibility should trigger additional investigation into:

- legacy systems
- legacy applications
- old authentication policies
- domain compatibility settings
- password storage policy
- NTLM compatibility configuration

---

# NTLMv1

NTLMv1 improved upon older LM authentication but is itself considered weak by modern security standards.

Simplified:

```text
Client                       Server
  |                             |
  |--------- request ---------->|
  |                             |
  |<-------- challenge ---------|
  |                             |
  |------ NTLMv1 response ----->|
  |                             |
```

NTLMv1 has known cryptographic weaknesses and should normally be disabled in modern environments where compatibility permits.

Its presence can significantly increase the risk associated with captured authentication traffic.

During an assessment, determine whether:

```text
NTLMv1 accepted?
      |
      +--> Yes
      |      |
      |      +--> Legacy authentication exposure
      |      +--> Increased credential attack risk
      |
      +--> No
             |
             +--> NTLMv2 or stronger mechanisms required
```

---

# NTLMv2

NTLMv2 strengthens the challenge-response construction compared with NTLMv1.

At a high level:

```text
Client                                      Server
  |                                            |
  |------------- authentication ------------->|
  |                                            |
  |<--------------- challenge ----------------|
  |                                            |
  |                                           |
  | Calculate NTLMv2 response                 |
  | using credential-derived material         |
  |                                           |
  |--------------- response ----------------->|
  |                                            |
  |                               Validate response
  |                                            |
```

For domain accounts, validation commonly involves a domain controller.

For local accounts, the server can validate authentication using its local account database.

NTLMv2 should not be interpreted as eliminating all NTLM-related risks.

Even where NTLMv2 is used, environments can still be exposed to:

- password cracking against captured challenge-response material
- NTLM relay
- credential coercion
- weak service configuration
- local account password reuse
- authentication downgrade scenarios
- legacy dependencies

---

# NTLMSSP

NTLMSSP refers to the NTLM Security Support Provider protocol used to carry NTLM authentication messages.

A simplified NTLMSSP exchange contains three primary message types:

```text
NEGOTIATE_MESSAGE
        |
        v
CHALLENGE_MESSAGE
        |
        v
AUTHENTICATE_MESSAGE
```

These are often described as:

```text
Type 1 - Negotiate
Type 2 - Challenge
Type 3 - Authenticate
```

---

## Type 1 - Negotiate

The client begins the authentication exchange.

Conceptually:

```text
Client
   |
   | NTLMSSP_NEGOTIATE
   v
Server
```

The message advertises capabilities and negotiation flags.

---

## Type 2 - Challenge

The server returns a challenge.

```text
Client
   ^
   |
   | NTLMSSP_CHALLENGE
   |
Server
```

The server challenge is a key component of the challenge-response authentication process.

---

## Type 3 - Authenticate

The client calculates and returns authentication material.

```text
Client
   |
   | NTLMSSP_AUTH
   v
Server
```

The message can contain information including:

- user name
- domain/workstation information
- authentication response
- negotiated session information

The server then validates the response.

---

# Domain Authentication

For a domain account, NTLM authentication may involve:

```text
Domain User
    |
    v
Client
    |
    v
Resource Server
    |
    v
Domain Controller
    |
    v
Account validation
```

A simplified flow is:

```text
1. Client requests access.

2. Server generates a challenge.

3. Client calculates a response.

4. Server forwards authentication information for validation.

5. Domain Controller validates the response.

6. Authentication succeeds or fails.
```

This is commonly described as NTLM pass-through authentication.

---

# Local Account Authentication

NTLM is also important outside Active Directory domain authentication.

For a local account:

```text
Client
   |
   v
Server
   |
   v
Local SAM
```

The server may validate the account using its local account database.

This distinction matters during penetration testing.

For example:

```text
CORP\alice
```

is different from:

```text
SERVER01\alice
```

Even if both accounts happen to use the same password.

---

# Local Account Password Reuse

Local account password reuse can significantly increase lateral movement risk.

Consider:

```text
SERVER01
Local Administrator
Password: SamePassword
        |
        |
        +----------------+
                         |
                         v
SERVER02
Local Administrator
Password: SamePassword
```

If local administrative credentials are reused across multiple systems, compromise of one host can potentially affect others.

Modern Windows environments should use mechanisms such as Windows LAPS where appropriate to provide unique managed local administrator passwords.

---

# Kerberos vs NTLM

Kerberos and NTLM use fundamentally different authentication models.

| Property | Kerberos | NTLM |
|---|---|---|
| Primary AD authentication | Yes | Fallback/legacy/local scenarios |
| Architecture | Ticket-based | Challenge-response |
| KDC required | Yes | No for local authentication |
| SPNs important | Yes | Not in the same way |
| Mutual authentication | Supported | More limited |
| Delegation model | Extensive | Different/limited |
| Relay considerations | Different | Major security concern |
| Hash-based authentication attacks | Possible through related techniques | Pass-the-Hash commonly associated |
| Local accounts | Not typical | Common |

Simplified:

```text
Kerberos

Client
   |
   v
KDC
   |
   v
Ticket
   |
   v
Service
```

Compared with:

```text
NTLM

Client
   |
   v
Server Challenge
   |
   v
Client Response
   |
   v
Validation
```

---

# Negotiate

Windows applications often use the **Negotiate** security package rather than directly selecting NTLM.

Conceptually:

```text
Application
    |
    v
Negotiate
    |
    +--> Kerberos available?
    |        |
    |        +--> Yes --> Kerberos
    |
    +--> Otherwise --> NTLM
```

This means observing NTLM in an Active Directory environment may indicate that Kerberos could not be used.

That can be diagnostically useful.

---

# Why Kerberos May Fall Back to NTLM

Common causes include:

- connecting using an IP address rather than a hostname
- missing SPNs
- incorrect SPNs
- duplicate SPNs
- DNS problems
- workgroup systems
- local accounts
- non-domain systems
- applications explicitly requesting NTLM
- Kerberos-incompatible software
- trust/configuration problems
- legacy authentication implementations

A useful investigation model is:

```text
Expected Kerberos
       |
       v
Observed NTLM
       |
       +--> IP used?
       |
       +--> DNS correct?
       |
       +--> SPN present?
       |
       +--> SPN duplicate?
       |
       +--> Service account correct?
       |
       +--> Application forcing NTLM?
       |
       +--> Local account?
       |
       +--> Workgroup/non-domain system?
```

---

# Hostnames vs IP Addresses

One common cause of unexpected NTLM authentication is connecting to a service by IP address.

For example:

```text
\\fileserver.corp.example\share
```

may permit Kerberos when the required SPN and DNS configuration are correct.

Whereas:

```text
\\10.10.10.25\share
```

may result in different authentication behaviour.

Do not automatically conclude that IP-based access always results in NTLM under every modern Windows configuration. Windows authentication behaviour can be affected by configuration and newer platform capabilities.

During an assessment, compare:

```text
Hostname
FQDN
IP address
Alias
CNAME
```

and determine which authentication protocol is actually negotiated.

---

# NTLM over SMB

SMB is one of the most important protocols when assessing NTLM.

Typical SMB authentication can involve:

```text
Client
   |
   v
TCP/445
   |
   v
SMB
   |
   v
NTLM / Kerberos
```

Important SMB security properties include:

- SMB dialect
- SMB signing
- signing required vs optional
- authentication protocol
- local vs domain account
- administrative privileges
- guest access
- share permissions

---

# SMB Signing

SMB signing provides integrity protection for SMB communications.

From an NTLM relay perspective, whether SMB signing is required is particularly important.

Conceptually:

```text
NTLM authentication
        |
        v
Target SMB service
        |
        +--> Signing required
        |       |
        |       +--> Common SMB relay path constrained
        |
        +--> Signing not required
                |
                +--> Relay exposure may exist
```

Do not report:

```text
SMB signing not required = compromised
```

Instead report the actual condition:

```text
SMB signing is not required
        +
NTLM authentication is available
        +
a viable authentication source exists
        +
relay prerequisites are satisfied
```

Security findings should reflect the complete attack path rather than a single configuration property.

---

# Enumerating SMB Signing with NetExec

Within an authorised assessment:

```bash
nxc smb 10.10.10.0/24
```

NetExec output can help identify:

- operating system information
- SMB dialect information
- domain/workgroup information
- SMB signing configuration
- SMB availability

The exact output varies by version and target.

For detailed NetExec coverage, see:

[NetExec](netexec.md)

---

# NTLM over HTTP

NTLM can also be used through HTTP authentication.

A simplified flow is:

```text
Browser
   |
   v
Web Server
   |
   +--> WWW-Authenticate: Negotiate
   |
   +--> WWW-Authenticate: NTLM
```

Integrated Windows Authentication may therefore involve Kerberos or NTLM depending on the environment and configuration.

HTTP services are important when assessing relay exposure because authentication may potentially be forwarded between compatible services where protections are absent.

Examples include:

- IIS
- management interfaces
- enterprise web applications
- certificate services
- internal portals
- proxy services

---

# NTLM over LDAP

LDAP can participate in Windows authentication workflows.

Relevant security controls can include:

- LDAP signing
- LDAP channel binding
- TLS
- authentication mechanism
- server configuration

A tester should distinguish between:

```text
LDAP
LDAPS
LDAP signing
Channel binding
Authentication protocol
```

These are related but separate controls.

---

# NTLM and WinRM

WinRM can use Windows authentication mechanisms including Negotiate and NTLM depending on configuration.

Common endpoints include:

```text
5985/tcp - HTTP
5986/tcp - HTTPS
```

When evaluating WinRM, determine:

- whether the service is exposed
- whether authentication is permitted
- whether Kerberos or NTLM is used
- whether HTTPS is configured
- whether the account is authorised for remote management
- whether administrative privileges exist

Authentication success alone does not imply remote administrative execution rights.

---

# NTLM Capture

NTLM capture refers to obtaining NTLM challenge-response authentication material when a system authenticates to an attacker-controlled or assessment-controlled service.

Conceptually:

```text
Victim
   |
   | Authentication attempt
   v
Assessment-controlled listener
   |
   v
NTLM challenge-response captured
```

The captured material may then be evaluated for:

```text
Capture
   |
   +--> Password strength assessment
   |
   +--> Offline cracking in an authorised test
   |
   +--> Relay feasibility assessment
```

Capture does **not** automatically reveal the NT hash.

---

# Name Resolution and NTLM

NTLM capture is often discussed alongside local name-resolution protocols.

Examples historically include:

- LLMNR
- NBT-NS
- mDNS
- DNS-related behaviour

Conceptually:

```text
User requests resource
        |
        v
Normal resolution fails
        |
        v
Alternative/local resolution
        |
        v
Attacker-controlled response
        |
        v
Authentication attempt
```

Responder is a commonly used assessment tool for examining these behaviours.

Detailed Responder coverage belongs in:

```text
active-directory/responder.md
```

---

# Capture vs Relay

These concepts must remain separate.

```text
                    NTLM authentication
                            |
              +-------------+-------------+
              |                           |
              v                           v
           Capture                      Relay
              |                           |
              v                           v
Challenge-response stored        Authentication forwarded
              |                           |
              v                           v
Potential offline cracking       Target service authenticates
```

Capture asks:

> Can authentication material be obtained?

Relay asks:

> Can that authentication be forwarded to another service and accepted?

The conditions are different.

---

# NTLM Relay

NTLM relay involves forwarding an authentication exchange to another service rather than attempting to recover the password.

Conceptually:

```text
Victim
   |
   | NTLM authentication
   v
Relay system
   |
   | Forward authentication
   v
Target service
   |
   v
Authentication accepted?
```

A relay attack does not necessarily require knowing:

- the plaintext password
- the NT hash

Instead, the authentication exchange itself is forwarded.

---

# Relay Prerequisites

Successful NTLM relay depends on several conditions.

A simplified model:

```text
Authentication source
        |
        v
Can NTLM be obtained/coerced?
        |
       Yes
        |
        v
Compatible target
        |
        v
Does target require protections?
        |
        +--> Signing
        +--> Channel binding
        +--> EPA
        +--> Protocol-specific controls
        |
        v
Are authentication and privileges useful?
```

Therefore:

```text
NTLM enabled
```

does not automatically mean:

```text
NTLM relay exploitable
```

The complete path must be validated.

---

# Protocol Relay

NTLM authentication can appear across multiple protocols.

Conceptually:

```text
        Authentication
              |
     +--------+--------+
     |        |        |
     v        v        v
    SMB      HTTP     LDAP
     |        |        |
     +--------+--------+
              |
              v
        Relay analysis
```

Cross-protocol relay may be possible in some configurations.

Security controls must therefore be considered per service rather than only per host.

---

# Extended Protection for Authentication

Extended Protection for Authentication (EPA) provides additional protection against certain credential-forwarding and relay scenarios by binding authentication to properties of the protected channel or service.

Conceptually:

```text
Authentication
      |
      v
Secure channel
      |
      v
Channel/service binding
      |
      v
Server validates relationship
```

Where supported and correctly configured, EPA can significantly reduce relay exposure for applicable services.

During an assessment, determine:

- whether the application supports EPA
- whether EPA is enabled
- whether it is required
- whether TLS is used where appropriate
- whether channel binding is enforced
- whether legacy clients require exceptions

Do not recommend enabling EPA blindly without compatibility testing.

---

# Channel Binding

Channel binding helps associate an authentication exchange with the underlying secure transport.

Simplified:

```text
TLS connection
     |
     v
Channel information
     |
     v
Authentication exchange
     |
     v
Server validates binding
```

This helps prevent authentication captured from one channel being reused through another unrelated channel.

Channel binding is especially relevant when assessing:

- LDAP
- HTTPS
- IIS
- Integrated Windows Authentication
- enterprise applications

---

# LDAP Channel Binding

LDAP channel binding is an important Active Directory hardening control.

The assessment should distinguish:

```text
LDAP signing
       |
       X
LDAP channel binding
```

They solve different security problems.

Both may contribute to reducing authentication relay opportunities.

---

# Pass-the-Hash

Pass-the-Hash uses an NT hash as authentication material without requiring the original plaintext password.

Conceptually:

```text
NT hash obtained
      |
      v
Authentication protocol
      |
      v
Target service
      |
      v
Authentication succeeds
```

This is fundamentally different from relaying a captured NetNTLMv2 response.

```text
Pass-the-Hash

NT hash
   |
   v
Authentication


NTLM Relay

Live NTLM exchange
   |
   v
Forward authentication
```

Detailed Pass-the-Hash coverage belongs in:

```text
active-directory/pass-the-hash.md
```

---

# Pass-the-Hash with NetExec

Within an authorised environment, NetExec supports hash-based authentication for protocols where applicable.

A typical SMB syntax is:

```bash
nxc smb 10.10.10.25 -u Administrator -H <NT_HASH>
```

Domain context can be specified where required:

```bash
nxc smb 10.10.10.25 -d CORP -u administrator -H <NT_HASH>
```

Local account authentication can be explicitly selected:

```bash
nxc smb 10.10.10.25 -u Administrator -H <NT_HASH> --local-auth
```

The exact behaviour depends on:

- target configuration
- account privileges
- protocol
- local/domain context
- security controls
- NetExec version

Do not interpret successful authentication as proof of administrative privileges.

---

# Pass-the-Hash with Impacket

Impacket supports NTLM authentication using hashes across several applicable tools.

A common credential format is:

```text
LMHASH:NTHASH
```

For example, tools may expose:

```text
-hashes LMHASH:NTHASH
```

When the LM hash is unavailable, the LM field can commonly be represented using the standard empty LM hash value.

Example pattern:

```bash
impacket-smbclient -hashes aad3b435b51404eeaad3b435b51404ee:<NT_HASH> 'DOMAIN/user@target'
```

Tool names can differ depending on installation and packaging.

For detailed Impacket coverage, see:

[Impacket](impacket.md)

---

# Validate Credentials Carefully

During authorised testing, avoid unnecessarily authenticating one credential across the entire environment.

Prefer:

```text
Known account
     |
     v
Known authorised target
     |
     v
Single authentication attempt
     |
     v
Observe result
     |
     v
Expand only if scope permits
```

This reduces:

- account lockout risk
- unnecessary authentication noise
- accidental access
- operational impact

---

# Password Spraying Relationship

NTLM is frequently involved in password-spraying assessments.

Conceptually:

```text
Small password set
       |
       v
Many accounts
       |
       v
Authentication service
       |
       v
Success / failure
```

Password spraying differs from traditional brute force because it generally attempts a small number of candidate passwords across multiple accounts to reduce lockout risk.

Detailed coverage belongs in:

```text
active-directory/password-spraying.md
```

---

# Authentication Coercion

Authentication coercion refers to causing a Windows system to authenticate to another system.

Conceptually:

```text
Assessment system
       |
       | Trigger authorised test condition
       v
Windows host
       |
       | Outbound authentication
       v
Controlled listener
       |
       +--> Capture
       |
       +--> Relay validation
```

Coercion is important because relay attacks require an authentication source.

Detailed coercion techniques should be treated separately from the NTLM protocol itself.

---

# NTLM Security Controls

A strong NTLM security posture is not based on a single configuration.

Think in layers:

```text
Reduce NTLM
    |
    +--> Prefer Kerberos
    |
    +--> Remove legacy dependencies
    |
    +--> Restrict NTLM
    |
    +--> Require SMB signing
    |
    +--> LDAP signing
    |
    +--> LDAP channel binding
    |
    +--> EPA
    |
    +--> Disable LLMNR where appropriate
    |
    +--> Reduce NBT-NS dependency
    |
    +--> Unique local passwords
    |
    +--> LAPS
    |
    +--> Strong passwords
    |
    +--> Network segmentation
    |
    +--> Monitor authentication
```

---

# NTLM Restriction Policies

Windows provides policies for auditing and restricting NTLM authentication.

Relevant policy areas include:

```text
Computer Configuration
   |
   v
Windows Settings
   |
   v
Security Settings
   |
   v
Local Policies
   |
   v
Security Options
```

Policies can be used to:

- audit NTLM usage
- restrict incoming NTLM
- restrict outgoing NTLM
- restrict NTLM within a domain
- create exceptions where required

A safe migration strategy is:

```text
Audit
  |
  v
Identify dependencies
  |
  v
Remediate applications
  |
  v
Pilot restrictions
  |
  v
Monitor failures
  |
  v
Expand restrictions
```

Do not immediately disable NTLM across a production environment without understanding application dependencies.

---

# Windows Inspection

Several Windows-native commands can help investigate authentication configuration.

---

## Current Identity

```powershell
whoami
```

Detailed token information:

```powershell
whoami /all
```

---

## Domain Information

```powershell
whoami /fqdn
```

Environment information:

```powershell
$env:USERDOMAIN
$env:USERNAME
$env:LOGONSERVER
```

---

## Domain Controller Discovery

```cmd
nltest /dsgetdc:corp.example
```

List domain controllers:

```cmd
nltest /dclist:corp.example
```

---

## Kerberos Tickets

Because determining whether Kerberos is being used helps identify NTLM fallback, inspect Kerberos tickets:

```cmd
klist
```

Purge tickets in a controlled lab if specifically required for authentication testing:

```cmd
klist purge
```

!!! warning
    Purging Kerberos tickets changes the user's authentication state and can affect active sessions. Use it only in controlled authorised testing where the impact is understood.

---

# PowerShell Inspection

Current identity:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

Current domain:

```powershell
$env:USERDOMAIN
```

Logon server:

```powershell
$env:LOGONSERVER
```

Computer domain:

```powershell
(Get-CimInstance Win32_ComputerSystem).Domain
```

Domain membership:

```powershell
(Get-CimInstance Win32_ComputerSystem).PartOfDomain
```

---

# Security Policy Inspection

Export local security policy where authorised:

```cmd
secedit /export /cfg C:\Windows\Temp\security-policy.cfg
```

Search relevant settings:

```cmd
findstr /i "LmCompatibilityLevel" C:\Windows\Temp\security-policy.cfg
```

Registry inspection may also provide relevant local policy information:

```cmd
reg query HKLM\SYSTEM\CurrentControlSet\Control\Lsa
```

Specific NTLM-related settings should be interpreted in combination with:

- local policy
- domain Group Policy
- effective policy
- operating system version
- application configuration

---

# LmCompatibilityLevel

The `LmCompatibilityLevel` setting historically controls aspects of LM and NTLM authentication behaviour.

Inspect:

```cmd
reg query HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v LmCompatibilityLevel
```

PowerShell:

```powershell
Get-ItemProperty `
    -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa' `
    -Name LmCompatibilityLevel `
    -ErrorAction SilentlyContinue
```

Do not interpret this setting in isolation.

Effective authentication behaviour can also depend on:

- Group Policy
- domain policy
- target service
- client configuration
- operating system version
- application authentication configuration

---

# Network Observation

Packet analysis can help determine whether NTLM is being negotiated.

Useful display filters in Wireshark include:

```text
ntlmssp
```

SMB:

```text
smb2
```

Kerberos:

```text
kerberos
```

LDAP:

```text
ldap
```

HTTP authentication:

```text
http.authbasic || ntlmssp
```

A useful workflow is:

```text
Generate controlled authentication
        |
        v
Capture traffic
        |
        v
Identify protocol
        |
        +--> Kerberos
        |
        +--> NTLMSSP
        |
        +--> Other
        |
        v
Determine why
```

Only capture network traffic where explicitly authorised.

---

# NTLMSSP in Wireshark

A captured NTLM authentication exchange may show:

```text
NTLMSSP_NEGOTIATE
NTLMSSP_CHALLENGE
NTLMSSP_AUTH
```

Useful fields can include:

- negotiated flags
- server challenge
- domain information
- workstation information
- user information
- NTLM version information

Avoid including reusable credential material unnecessarily in assessment reports.

---

# NetExec for NTLM Assessment

NetExec is useful for several NTLM-related assessment tasks.

Basic SMB discovery:

```bash
nxc smb 10.10.10.0/24
```

Authenticate with a controlled account:

```bash
nxc smb 10.10.10.25 -u testuser -p '<PASSWORD>'
```

Specify a domain:

```bash
nxc smb 10.10.10.25 -d CORP -u testuser -p '<PASSWORD>'
```

Local authentication:

```bash
nxc smb 10.10.10.25 --local-auth -u Administrator -p '<PASSWORD>'
```

Hash authentication:

```bash
nxc smb 10.10.10.25 -u Administrator -H <NT_HASH>
```

Detailed NetExec usage is documented in:

[NetExec](netexec.md)

---

# Impacket and NTLM

Impacket provides protocol implementations and tools supporting both NTLM and Kerberos authentication.

Common assessment areas include:

```text
Impacket
   |
   +--> SMB
   +--> LDAP
   +--> RPC
   +--> WMI
   +--> DCOM
   +--> MSSQL
   +--> NTLM
   +--> Kerberos
```

Impacket tools frequently support options such as:

```text
-hashes
-k
-aesKey
-no-pass
```

These correspond to different authentication mechanisms.

Do not assume:

```text
-hashes == Kerberos
```

or:

```text
-k == NTLM
```

They represent different credential/authentication paths.

For detailed usage:

[Impacket](impacket.md)

---

# Responder Relationship

Responder is commonly used to investigate name-resolution poisoning and authentication capture.

Conceptually:

```text
Resolution request
       |
       v
Assessment-controlled response
       |
       v
Victim connects
       |
       v
NTLM authentication
       |
       +--> Capture
       |
       +--> Potential relay workflow
```

Responder itself should be treated as a separate topic because understanding the underlying name-resolution protocols is essential.

Detailed coverage belongs in:

```text
active-directory/responder.md
```

---

# ntlmrelayx Relationship

Impacket's `ntlmrelayx` is commonly used during authorised NTLM relay testing.

Conceptually:

```text
Authentication source
       |
       v
ntlmrelayx
       |
       v
Target service
       |
       v
Authentication accepted
       |
       v
Authorised validation action
```

Potential target protocols and capabilities depend on:

- Impacket version
- target service
- target configuration
- signing requirements
- channel binding
- EPA
- authentication privileges

Detailed relay testing belongs in:

```text
active-directory/ntlm-relay.md
```

---

# Credential Exposure vs Exploitability

A useful reporting distinction is:

```text
NTLM observed
     |
     v
Is authentication exposed?
     |
     v
Can authentication be captured?
     |
     v
Can it be cracked?
     |
     v
Can it be relayed?
     |
     v
Does successful authentication provide useful privileges?
```

Each step represents a different level of risk.

Avoid collapsing them into a single conclusion.

---

# Assessment Workflow

A structured NTLM assessment can follow:

```text
Identify Environment
        |
        v
Determine Authentication Protocols
        |
        +--> Kerberos
        |
        +--> NTLM
        |
        v
Identify NTLM Dependencies
        |
        v
Inspect Security Controls
        |
        +--> SMB signing
        +--> LDAP signing
        +--> Channel binding
        +--> EPA
        +--> NTLM restrictions
        |
        v
Identify Authentication Sources
        |
        +--> User activity
        +--> Name resolution
        +--> Applications
        +--> Controlled coercion
        |
        v
Assess Exposure
        |
        +--> Capture
        +--> Cracking
        +--> Relay
        +--> Pass-the-Hash
        |
        v
Validate Impact
        |
        v
Collect Evidence
        |
        v
Recommend Hardening
```

---

# Phase 1 - Identify NTLM Usage

Determine where NTLM is actually used.

Investigate:

- domain controllers
- member servers
- workstations
- file servers
- IIS servers
- LDAP services
- WinRM
- SQL servers
- proxies
- appliances
- legacy applications
- local accounts

The objective is:

```text
Where is NTLM required?
```

not merely:

```text
Is NTLM enabled somewhere?
```

---

# Phase 2 - Determine Why NTLM Is Used

For each NTLM authentication event, ask:

```text
Why NTLM?
```

Possible reasons include:

```text
Local account
IP-based connection
Missing SPN
Incorrect DNS
Legacy application
Workgroup host
Explicit NTLM configuration
Kerberos failure
Cross-domain/trust issue
```

This distinction helps identify remediation opportunities.

---

# Phase 3 - Assess Protocol Protections

Review:

```text
SMB
 |
 +--> Signing required?


LDAP
 |
 +--> Signing?
 +--> Channel binding?


HTTP
 |
 +--> TLS?
 +--> EPA?


NTLM
 |
 +--> Audit?
 +--> Restriction policies?
```

This establishes whether NTLM use can be safely reduced and whether relay paths may exist.

---

# Phase 4 - Assess Credential Exposure

Determine whether systems can unintentionally authenticate to attacker-controlled locations.

Possible causes include:

- local name-resolution behaviour
- application functionality
- file references
- remote resource access
- misconfigured services
- authentication coercion

Use controlled systems and test accounts.

---

# Phase 5 - Validate Impact

If an NTLM-related weakness is identified, validate only the minimum impact required.

For example:

```text
Weakness
   |
   v
Controlled authentication
   |
   v
Confirm security control missing
   |
   v
Demonstrate limited impact
   |
   v
Stop
```

Avoid unnecessary lateral movement or privilege escalation if the security finding has already been demonstrated.

---

# Detection

NTLM monitoring should combine multiple data sources.

Potential sources include:

- Windows Security logs
- NTLM operational logs
- domain controller logs
- SMB logs
- LDAP logs
- IIS logs
- EDR telemetry
- network monitoring
- authentication telemetry
- firewall logs

---

# Windows Security Events

Useful authentication events can include:

```text
4624 - Successful logon
4625 - Failed logon
4648 - Logon using explicit credentials
4776 - Credential validation
```

Event interpretation depends on:

- system role
- authentication package
- logon type
- source address
- account
- workstation
- domain
- operating system version

Do not use a single event ID as proof of a specific attack.

---

# Event 4624

Successful logons can contain useful fields including:

- account name
- account domain
- logon type
- authentication package
- source network address
- workstation
- process information

Look for authentication package information such as:

```text
NTLM
```

Correlate with:

- source host
- destination host
- account privileges
- timing
- service accessed

---

# Event 4625

Failed logons can help identify:

- password spraying
- brute force
- stale credentials
- service misconfiguration
- unexpected NTLM usage

Look for patterns such as:

```text
One source
    |
    +--> Many users
```

or:

```text
One user
    |
    +--> Many hosts
```

Context is essential because legitimate management and service activity can produce similar patterns.

---

# Event 4776

Credential validation events can be particularly useful for NTLM authentication analysis.

Correlate:

```text
Account
   +
Source workstation
   +
Time
   +
Target activity
```

to identify suspicious patterns.

---

# NTLM Operational Logging

Windows provides NTLM-specific operational logging and auditing capabilities that can help organisations understand NTLM dependencies before restricting the protocol.

A recommended defensive process is:

```text
Enable auditing
      |
      v
Collect NTLM usage
      |
      v
Identify legitimate dependencies
      |
      v
Remove unnecessary NTLM
      |
      v
Test restrictions
      |
      v
Enforce
```

This is safer than immediately blocking NTLM without understanding business dependencies.

---

# Detection Opportunities

Potential suspicious patterns include:

- NTLM where Kerberos is normally expected
- authentication from unusual hosts
- workstation-to-workstation NTLM
- privileged accounts using NTLM unexpectedly
- sudden NTLM activity following name-resolution failures
- many authentication attempts to one assessment-like host
- repeated NTLM failures
- authentication to unusual SMB servers
- unusual HTTP Integrated Authentication
- privileged accounts authenticating to untrusted systems
- authentication immediately followed by remote service activity

---

# Purple Team Validation

NTLM provides useful purple-team exercise opportunities because both offensive and defensive controls can be measured.

Example:

```text
Red Team
   |
   | Controlled NTLM authentication
   v
Blue Team
   |
   +--> Detect protocol?
   +--> Identify source?
   +--> Identify account?
   +--> Identify target?
   +--> Determine why NTLM occurred?
   +--> Identify missing protection?
   +--> Contain if required?
```

Metrics can include:

- time to detect
- time to investigate
- source attribution accuracy
- affected account identification
- target identification
- protocol identification
- escalation quality
- remediation accuracy

---

# Hardening

NTLM hardening should follow a layered approach.

---

## Prefer Kerberos

Where possible:

```text
NTLM
  |
  v
Identify dependency
  |
  v
Fix Kerberos/application configuration
  |
  v
Kerberos
```

Investigate:

- DNS
- SPNs
- service accounts
- aliases
- application configuration
- domain membership
- trust configuration

---

## Audit Before Restricting NTLM

Before enforcement:

```text
Audit
  |
  v
Inventory
  |
  v
Remediate
  |
  v
Pilot
  |
  v
Restrict
```

This reduces the risk of breaking legitimate applications.

---

## Disable NTLMv1

Where compatibility permits, NTLMv1 should not be accepted.

Legacy dependencies should be identified and remediated rather than permanently preserving weak authentication.

---

## Disable LM

LM authentication and LM password storage should not be relied upon in modern environments.

---

## Require SMB Signing

Where appropriate, require SMB signing to provide integrity protection and reduce applicable SMB relay opportunities.

Assess compatibility before organisation-wide enforcement.

---

## LDAP Signing

Require LDAP signing where supported and appropriate.

This helps protect LDAP communications from certain manipulation and relay scenarios.

---

## LDAP Channel Binding

Configure LDAP channel binding according to Microsoft guidance and application compatibility requirements.

---

## Extended Protection for Authentication

Enable EPA on supported services where practical.

Particularly review:

- IIS
- AD CS web services
- Exchange-related services
- enterprise applications using Windows authentication

Compatibility testing is important.

---

## Disable Unnecessary Name-Resolution Protocols

Where not required, reduce dependence on legacy local name-resolution protocols such as:

```text
LLMNR
NBT-NS
```

Ensure DNS is correctly configured before disabling fallback mechanisms.

---

## Windows LAPS

Use Windows LAPS or equivalent controls to avoid local administrator password reuse.

Conceptually:

```text
Host A
Administrator -> unique password

Host B
Administrator -> different password

Host C
Administrator -> different password
```

This significantly limits the value of a compromised local administrator credential across multiple systems.

---

## Restrict Privileged Account Authentication

Privileged accounts should not routinely authenticate to low-trust systems.

Consider administrative tiering and dedicated management systems.

```text
Domain Admin
     |
     X
Normal workstation
```

Reducing where privileged credentials are exposed reduces the impact of credential capture and theft.

---

## Network Segmentation

Restrict unnecessary east-west access to services such as:

```text
445/TCP
135/TCP
5985/TCP
5986/TCP
389/TCP
636/TCP
```

Segmentation can reduce both authentication exposure and lateral movement opportunities.

---

## Strong Passwords

Strong passwords remain important because captured NTLM challenge-response material may be subjected to offline password guessing.

Long, unique passwords substantially increase resistance to offline recovery.

---

# Reporting

NTLM-related findings should describe the actual weakness.

Avoid vague findings such as:

```text
NTLM is vulnerable
```

Prefer specific findings such as:

```text
NTLMv1 authentication is permitted
```

```text
SMB signing is not required on multiple servers
```

```text
NTLM authentication can be relayed to an LDAP service because required protections are absent
```

```text
LLMNR permits controlled interception of NTLM authentication
```

```text
Local administrator credentials are reused across multiple systems
```

```text
A privileged account authenticates using NTLM to lower-trust systems
```

The finding title should reflect the validated condition.

---

# Evidence Collection

Useful evidence can include:

```text
Target
Hostname
IP address
Domain
Protocol
Port
Authentication protocol
Account type
NTLM version
Signing status
Channel binding status
EPA status
Relevant policy
Relevant event IDs
Timestamp
Tool command
Sanitised output
Validated impact
```

Avoid storing unnecessary reusable credentials in reports.

Redact:

- plaintext passwords
- NT hashes
- captured challenge-response material
- session tokens
- sensitive account information

unless explicitly required by the engagement and protected appropriately.

---

# Example Evidence Structure

```text
Finding:
SMB signing not required

Target:
FILE01.corp.example

Address:
10.10.10.25

Protocol:
SMB

Port:
445/TCP

Authentication:
NTLM supported

SMB signing:
Supported but not required

Validation:
Controlled authentication demonstrated that the service accepted
NTLM authentication without requiring SMB signing.

Impact:
The configuration may contribute to NTLM relay exposure where a
compatible authentication source and relay path are available.

Recommendation:
Require SMB signing where compatible and reduce unnecessary NTLM
authentication.
```

This is more accurate than claiming that lack of SMB signing alone results in compromise.

---

# Troubleshooting

## Authentication Works by IP but Not Hostname

Investigate:

```text
DNS
SPN
Kerberos
Name resolution
Aliases
```

---

## Authentication Works by Hostname but Uses NTLM

Investigate:

```text
SPN configuration
Application behaviour
Negotiate configuration
Kerberos tickets
DNS
Service account
```

---

## NetExec Authentication Fails

Check:

```text
Username
Password/hash
Domain
Local vs domain account
Target hostname
Target IP
SMB availability
Account lockout
Firewall
Signing/configuration
```

Try explicitly specifying domain context when appropriate.

---

## Local Account Authentication Fails

Ensure the account context is correct.

Conceptually:

```text
DOMAIN\User
```

is not the same as:

```text
HOST\User
```

For NetExec, local authentication can be selected using:

```bash
nxc smb 10.10.10.25 --local-auth -u Administrator -p '<PASSWORD>'
```

---

## Kerberos Expected but NTLM Observed

Use:

```cmd
klist
```

Then investigate:

```text
DNS
SPNs
Hostname vs IP
Domain membership
Application configuration
Time synchronisation
Trust
```

---

# Common Mistakes

## Mistake 1 - Calling NetNTLMv2 an NT Hash

Incorrect:

```text
Captured NT hash from Responder
```

when the captured value is actually NTLMv2 challenge-response material.

Better:

```text
Captured NetNTLMv2 challenge-response authentication material
```

---

## Mistake 2 - Treating Capture as Relay

```text
Capture != Relay
```

Capturing authentication proves that authentication material can reach the controlled system.

Relay requires additional conditions.

---

## Mistake 3 - Treating SMB Signing as the Only Relay Control

Relay exposure can also depend on:

- protocol
- EPA
- channel binding
- LDAP signing
- authentication target
- service configuration
- privileges

---

## Mistake 4 - Treating Successful Authentication as Administrative Access

```text
Authentication success
        |
        X
Administrator
```

Always validate actual privileges separately.

---

## Mistake 5 - Assuming NTLM Means NTLMv1

NTLM authentication may use NTLMv2.

Determine the actual protocol version before reporting.

---

## Mistake 6 - Assuming NTLM Can Simply Be Disabled

Legacy applications may depend on NTLM.

Use:

```text
Audit
  |
  v
Inventory
  |
  v
Remediation
  |
  v
Restriction
```

---

# Quick Assessment Checklist

## Discovery

- [ ] Identify domain and workgroup systems
- [ ] Identify SMB services
- [ ] Identify LDAP services
- [ ] Identify HTTP Integrated Authentication
- [ ] Identify WinRM
- [ ] Determine where NTLM is used
- [ ] Determine where Kerberos is expected

## Protocol Analysis

- [ ] Identify NTLM version
- [ ] Distinguish NT hash from NetNTLM challenge-response
- [ ] Identify local vs domain authentication
- [ ] Review Negotiate behaviour
- [ ] Compare hostname vs IP authentication where relevant

## SMB

- [ ] Check SMB signing
- [ ] Determine whether signing is required
- [ ] Identify administrative shares
- [ ] Determine account context
- [ ] Review SMB authentication protocol

## LDAP

- [ ] Review LDAP signing
- [ ] Review LDAP channel binding
- [ ] Review TLS configuration
- [ ] Determine authentication mechanisms

## HTTP

- [ ] Identify Integrated Windows Authentication
- [ ] Determine Negotiate/NTLM behaviour
- [ ] Review TLS
- [ ] Review EPA
- [ ] Review channel binding where applicable

## Credential Exposure

- [ ] Review LLMNR
- [ ] Review NBT-NS
- [ ] Review name-resolution behaviour
- [ ] Review outbound authentication paths
- [ ] Review coercion exposure where authorised

## Relay

- [ ] Identify potential authentication sources
- [ ] Identify potential targets
- [ ] Check SMB signing
- [ ] Check LDAP protections
- [ ] Check EPA
- [ ] Check channel binding
- [ ] Validate privileges
- [ ] Avoid assuming NTLM enabled equals relay vulnerable

## Pass-the-Hash

- [ ] Distinguish NT hash from NetNTLMv2
- [ ] Identify local/domain account context
- [ ] Test only controlled credentials
- [ ] Validate minimum required impact
- [ ] Avoid unnecessary lateral movement

## Detection

- [ ] Review Event 4624
- [ ] Review Event 4625
- [ ] Review Event 4648
- [ ] Review Event 4776
- [ ] Review NTLM operational logging
- [ ] Correlate network telemetry
- [ ] Correlate EDR telemetry
- [ ] Identify unexpected privileged NTLM authentication

## Hardening

- [ ] Prefer Kerberos
- [ ] Audit NTLM dependencies
- [ ] Disable NTLMv1 where possible
- [ ] Disable LM
- [ ] Require SMB signing where appropriate
- [ ] Require LDAP signing
- [ ] Configure LDAP channel binding
- [ ] Enable EPA where supported
- [ ] Reduce LLMNR/NBT-NS dependency
- [ ] Deploy Windows LAPS
- [ ] Prevent local password reuse
- [ ] Restrict privileged authentication
- [ ] Segment management protocols
- [ ] Monitor NTLM usage

---

# NTLM Testing Model

A useful mental model for NTLM assessments is:

```text
                     NTLM
                       |
        +--------------+--------------+
        |                             |
        v                             v
 Credential Material             Network Authentication
        |                             |
        v                             v
     NT Hash                    Challenge/Response
        |                             |
        |                       +-----+-----+
        |                       |           |
        v                       v           v
 Pass-the-Hash               Capture      Relay
                                |
                                v
                         Offline Cracking
```

Add the defensive layer:

```text
NTLM
 |
 +--> Reduce usage
 |
 +--> Prefer Kerberos
 |
 +--> Protect authentication
 |      |
 |      +--> SMB signing
 |      +--> LDAP signing
 |      +--> Channel binding
 |      +--> EPA
 |
 +--> Protect credentials
 |      |
 |      +--> LAPS
 |      +--> Strong passwords
 |      +--> Privileged account isolation
 |
 +--> Reduce authentication triggers
 |      |
 |      +--> DNS hygiene
 |      +--> Disable unnecessary LLMNR
 |      +--> Disable unnecessary NBT-NS
 |
 +--> Detect
        |
        +--> Security logs
        +--> NTLM auditing
        +--> EDR
        +--> Network telemetry
```

The key assessment question is therefore not simply:

```text
Is NTLM enabled?
```

Instead ask:

```text
Where is NTLM used?
        |
        v
Why is it used?
        |
        v
Can it be reduced?
        |
        v
Can authentication be captured?
        |
        v
Can it be cracked or relayed?
        |
        v
Can an NT hash be reused?
        |
        v
What security controls prevent exploitation?
        |
        v
Can defenders detect the activity?
```

This produces a more accurate assessment of NTLM exposure than treating NTLM as a single vulnerability.

---

# Related Notes

Detailed Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Kerberos:

[Kerberos](kerberos.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement this page and can be linked once their dedicated notes are available:

```text
active-directory/password-spraying.md
active-directory/pass-the-hash.md
active-directory/overpass-the-hash.md
active-directory/pass-the-key.md
active-directory/responder.md
active-directory/ntlm-relay.md
active-directory/kerberos-relay.md
active-directory/coercion.md
active-directory/lateral-movement.md
```

---

# References

## Microsoft NTLM

[Microsoft NTLM - Win32 apps](https://learn.microsoft.com/en-us/windows/win32/secauthn/microsoft-ntlm){ target="_blank" rel="noopener noreferrer" }

[NTLM overview in Windows Server](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }

[NTLM user authentication](https://learn.microsoft.com/en-us/troubleshoot/windows-server/windows-security/ntlm-user-authentication){ target="_blank" rel="noopener noreferrer" }

[Windows Authentication Overview](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/windows-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## NTLM Protocol Specification

[MS-NLMP - NT LAN Manager Authentication Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/1fbf5c3b-04c1-4591-a4be-9dc232c4744b){ target="_blank" rel="noopener noreferrer" }

---

## Extended Protection

[Extended Protection](https://learn.microsoft.com/en-us/windows/win32/wsw/extended-protection){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

[NetExec SMB Protocol](https://www.netexec.wiki/smb-protocol){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

NTLM remains an important part of Windows security assessments even though Kerberos is the preferred authentication protocol in Active Directory environments.

The most important concepts to remember are:

```text
NT hash != NetNTLMv2

Capture != Relay

Authentication != Administrative Access

NTLM enabled != Relay vulnerable

SMB signing not required != Automatic compromise
```

A mature assessment therefore evaluates the complete authentication path:

```text
Credential
    |
    v
Authentication Trigger
    |
    v
NTLM Exchange
    |
    v
Protocol
    |
    v
Security Controls
    |
    +--> Signing
    +--> Channel Binding
    +--> EPA
    +--> NTLM Restrictions
    |
    v
Potential Attack
    |
    +--> Capture
    +--> Cracking
    +--> Relay
    +--> Pass-the-Hash
    |
    v
Actual Privileges
    |
    v
Validated Impact
    |
    v
Detection
    |
    v
Remediation
```

Understanding these distinctions makes NTLM testing more accurate, safer, and considerably more useful to both offensive and defensive teams.
