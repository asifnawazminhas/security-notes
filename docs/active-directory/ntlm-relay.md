# NTLM Relay

NTLM relay is an authentication attack in which an attacker receives an NTLM authentication attempt from one system and forwards that authentication to another service.

The attacker does not necessarily need to know, recover, or crack the victim's password.

The core concept is:

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
Target Service
```

If the target accepts the relayed authentication and the victim account has useful privileges on that target, the attacker may be able to perform actions using the victim's identity.

NTLM relay should therefore be understood as:

```text
Authentication Forwarding
```

rather than:

```text
Password Cracking
```

or:

```text
Pass-the-Hash
```

A successful relay commonly depends on several conditions:

```text
Obtain NTLM Authentication
        +
Relay-Compatible Target
        +
Missing / Insufficient Protocol Protection
        +
Useful Victim Privileges
        =
Potential NTLM Relay
```

!!! warning "Authorised testing only"
    NTLM relay can cause authentication attempts to be forwarded to other systems and may result in actions being performed under another identity. During an authorised assessment, identify relay-compatible services and authentication paths before attempting active coercion or poisoning. Use dedicated test identities and targets where possible, avoid broad poisoning on production networks, and stop once sufficient evidence has been obtained.

---

# Core Concept

Consider:

```text
Victim
  |
  | NTLM authentication
  v
Attacker
  |
  | forwarded authentication
  v
Server
```

The target sees an authentication exchange associated with the victim.

The attacker acts as an intermediary.

Conceptually:

```text
Client                Attacker                Target
  |                       |                      |
  |---- Negotiate ------->|                      |
  |                       |---- Negotiate ------>|
  |                       |<--- Challenge -------|
  |<--- Challenge --------|                      |
  |---- Response -------->|                      |
  |                       |---- Response ------->|
  |                       |                      |
  |                       |<--- Result ----------|
```

The attacker forwards the authentication exchange rather than independently authenticating with the victim's password.

---

# Relay Is Not Hash Cracking

A common misunderstanding is:

```text
Capture NTLM
    |
    v
Crack Hash
    |
    v
Relay
```

This is not required.

Relay and cracking are separate paths:

```text
NTLM Authentication
        |
        +--> Capture
        |      |
        |      v
        |   Offline Password Guessing
        |
        +--> Relay
               |
               v
           Target Service
```

A captured NetNTLM challenge-response value may be suitable for offline password guessing.

A live authentication exchange may instead be relayed to another compatible service.

---

# Relay vs Pass-the-Hash

These techniques are different.

## Pass-the-Hash

```text
NT Hash
   |
   v
Authenticate Directly
   |
   v
Target
```

The attacker possesses an NT hash.

See:

[Pass-the-Hash](pass-the-hash.md)

## NTLM Relay

```text
Victim Authentication
        |
        v
Attacker
        |
        v
Forward Authentication
        |
        v
Target
```

The attacker does not necessarily possess the victim's NT hash.

---

# Relay vs Responder

Responder and NTLM relay are related but not equivalent.

Responder can be used to answer local name-resolution requests and capture authentication attempts.

Conceptually:

```text
Client Cannot Resolve Resource
          |
          v
Local Name Resolution
          |
          v
Attacker-Controlled Response
          |
          v
Authentication Attempt
          |
          +--> Capture
          |
          +--> Relay
                  |
                  v
              ntlmrelayx
```

Therefore:

```text
Responder
   !=
NTLM Relay
```

Responder can help generate or receive authentication traffic.

A relay tool forwards that authentication to another service.

A dedicated Responder page should cover poisoning and capture workflows separately.

---

# Why NTLM Relay Works

NTLM authentication historically does not always provide strong cryptographic binding between:

```text
Authentication Exchange
```

and:

```text
Intended Destination
```

at the NTLM layer alone.

Protocol-specific protections compensate for this weakness.

Examples include:

```text
SMB Signing
LDAP Signing
LDAP Channel Binding
EPA
HTTPS
Service-Specific Integrity Protections
```

When appropriate protections are absent, an attacker may be able to forward authentication to another endpoint.

---

# Basic Relay Requirements

A useful assessment model is:

```text
1. Authentication Source
2. Authentication Transport
3. Relay Target
4. Protocol Protection
5. Victim Privilege
6. Reachability
```

All should be analysed.

---

# Requirement 1 - Obtain Authentication

The attacker first needs an NTLM authentication attempt.

Possible sources include:

```text
Name Resolution Poisoning
Authentication Coercion
UNC Path Access
Web Content
Application Behaviour
Misconfigured Services
User Interaction
```

The authentication source should be tested separately from the relay target.

---

# Requirement 2 - Relay-Compatible Target

The attacker needs a service that accepts NTLM authentication and does not enforce protections that prevent the relay.

Commonly assessed services include:

```text
SMB
LDAP
LDAPS
HTTP
HTTPS
MSSQL
RPC-Related Services
```

Support varies significantly by protocol, target configuration, operating system, and relay tooling.

---

# Requirement 3 - Useful Victim Privilege

Successful authentication does not automatically produce useful impact.

Example:

```text
Victim
  |
  v
Relay to SMB
  |
  v
Authentication Succeeds
  |
  X
No Administrative Privilege
```

Compare:

```text
Administrator
     |
     v
Relay to SMB
     |
     v
Administrative Access
```

Therefore:

```text
Relay Success
     !=
Privilege Escalation
```

The victim's privileges on the target determine the resulting impact.

---

# Requirement 4 - Protocol Protection

The target must not enforce a protection that invalidates the relayed authentication.

Important examples include:

```text
SMB Signing
LDAP Signing
LDAP Channel Binding
Extended Protection for Authentication
TLS Channel Binding
```

The exact control depends on the protocol.

---

# Requirement 5 - Reachability

The relay system must be able to communicate with the intended target.

```text
Attacker
   |
   v
TCP / Service Reachability
   |
   v
Target
```

Network segmentation can therefore influence relay feasibility.

---

# Relay Attack Surface

A useful high-level workflow is:

```text
Enumerate NTLM
      |
      v
Enumerate Services
      |
      v
Check Signing / Binding
      |
      v
Identify Relay-Compatible Targets
      |
      v
Map Victim Privileges
      |
      v
Identify Authentication Source
      |
      v
Controlled Validation
```

---

# SMB Relay

SMB is one of the best-known NTLM relay targets.

Conceptually:

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
SMB Target
```

The critical control is:

```text
SMB Signing
```

---

# SMB Signing

SMB signing provides message integrity and helps prevent modification or relay of SMB traffic.

A simplified model is:

```text
SMB Signing Required
        |
        v
Relay Mitigated
```

versus:

```text
SMB Signing Not Required
        |
        v
Potential Relay Target
```

The exact behaviour depends on SMB version and configuration.

---

# Important SMB Signing Distinction

Do not confuse:

```text
Signing Enabled
```

with:

```text
Signing Required
```

A system may support signing without requiring it for every connection.

For relay analysis, the important question is usually:

```text
Is Signing Required?
```

---

# Enumerating SMB Signing with NetExec

NetExec can enumerate SMB configuration across authorised targets.

Example:

```bash
nxc smb 10.10.10.0/24
```

Typical output can include information such as:

```text
signing:True
```

or:

```text
signing:False
```

depending on the NetExec version.

Check the installed version:

```bash
nxc smb --help
```

---

# NetExec Relay Target Enumeration

NetExec versions may provide options for identifying hosts where SMB signing is not required.

Inspect the installed version:

```bash
nxc smb --help
```

Do not rely on historical CrackMapExec syntax without checking the current NetExec release.

A relay target list conceptually contains:

```text
10.10.10.21
10.10.10.24
10.10.10.31
```

These should be validated individually before active relay testing.

---

# Nmap SMB Signing Enumeration

Nmap includes SMB security-mode scripts that can help assess signing.

Example:

```bash
nmap \
    -p445 \
    --script smb2-security-mode \
    10.10.10.21
```

Possible output may indicate whether signing is:

```text
enabled
```

and whether it is:

```text
required
```

Use current Nmap script documentation when interpreting results.

---

# PowerShell SMB Signing Review

On a Windows SMB server:

```powershell
Get-SmbServerConfiguration |
    Select-Object EnableSecuritySignature,RequireSecuritySignature
```

On a Windows SMB client:

```powershell
Get-SmbClientConfiguration |
    Select-Object EnableSecuritySignature,RequireSecuritySignature
```

Administrative privileges may be required to inspect or change some configuration.

---

# SMB Client and Server Roles

A Windows system may operate as both:

```text
SMB Client
```

and:

```text
SMB Server
```

The relevant signing policy depends on the direction of communication.

Therefore assess both:

```text
Client Signing Requirements
Server Signing Requirements
```

where appropriate.

---

# SMB Relay Target Selection

A useful model is:

```text
SMB Reachable
      |
      v
NTLM Accepted
      |
      v
SMB Signing Not Required
      |
      v
Victim Has Useful Rights
      |
      v
Potential Relay Target
```

Do not create a target list based solely on port `445` being open.

---

# SMB Relay Impact

If an administrative account is successfully relayed to an SMB target, potential impact may include administrative operations supported by the relay tooling and target.

The important relationship is:

```text
Relayed Identity
      |
      v
Administrative Rights on Target
      |
      v
High Impact
```

If the identity is not privileged:

```text
Successful Authentication
      |
      v
Limited Access
```

may be the only result.

---

# Avoid Unnecessary Remote Execution

For an authorised assessment, successful authenticated access may already demonstrate the weakness.

Do not automatically proceed to:

```text
Service Creation
Command Execution
Credential Dumping
```

unless required by the rules of engagement.

A safer model is:

```text
Relay
  |
  v
Confirm Authentication
  |
  v
Confirm Privilege
  |
  v
Stop
```

---

# LDAP Relay

LDAP is another important NTLM relay target in Active Directory environments.

Conceptually:

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
LDAP
  |
  v
Active Directory
```

The resulting impact depends heavily on:

```text
LDAP Signing
Channel Binding
Victim Directory Permissions
```

---

# LDAP Signing

LDAP signing protects the integrity of LDAP communications.

A Domain Controller can be configured to require signing.

Conceptually:

```text
Unsigned LDAP
      |
      v
Potential Relay Surface
```

versus:

```text
LDAP Signing Required
      |
      v
Reduced Relay Surface
```

---

# LDAP Signing Policy

On Domain Controllers, the relevant policy is commonly associated with:

```text
Domain controller: LDAP server signing requirements
```

The secure configuration should be evaluated against current Microsoft guidance and application compatibility requirements.

---

# LDAP Channel Binding

LDAP channel binding provides additional protection for LDAP authentication over TLS.

This is particularly relevant to:

```text
LDAPS
```

and NTLM authentication.

Conceptually:

```text
NTLM Authentication
       |
       v
TLS Channel
       |
       v
Channel Binding Token
       |
       v
Authentication Bound to TLS
```

This makes forwarding authentication into a different TLS channel significantly more difficult.

---

# LDAP Signing vs Channel Binding

These are different controls.

```text
LDAP Signing
```

protects LDAP message integrity.

```text
LDAP Channel Binding
```

binds authentication to the TLS channel.

Both should be considered when evaluating relay risk.

---

# LDAP Relay Impact

LDAP relay can be particularly significant because Active Directory modifications may become possible when the relayed identity has sufficient permissions.

Potential categories include:

```text
Group Modification
ACL Modification
Computer Object Modification
Delegation Configuration
Other Directory Writes
```

The exact operation depends on the victim's effective directory rights.

---

# LDAP Relay and RBCD

A significant attack path can involve:

```text
Privileged Authentication
        |
        v
LDAP Relay
        |
        v
Write Computer Object
        |
        v
Configure RBCD
```

This requires the relayed principal to possess the necessary directory permission.

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# LDAP Relay and Machine Account Quota

Some historical and environment-dependent relay chains may combine:

```text
Machine Account Creation
        +
Directory Write
        +
RBCD
```

Machine Account Quota should not be treated as sufficient by itself.

See:

[Active Directory Machine Account Quota](machine-account-quota.md)

---

# LDAP Relay and ACLs

Always identify the actual directory permission enabling the resulting operation.

For example:

```text
Relay
  |
  v
Victim Identity
  |
  v
GenericWrite on Computer
  |
  v
Directory Modification
```

The vulnerability is not merely:

```text
LDAP Exists
```

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# LDAPS Relay

LDAPS uses LDAP over TLS.

The presence of TLS does not automatically mean:

```text
Relay Impossible
```

The effectiveness of relay protections depends on authentication and channel-binding configuration.

Therefore:

```text
LDAPS
   !=
Automatically Relay-Safe
```

Assess:

```text
Channel Binding
Signing Requirements
Authentication Type
```

---

# HTTP Relay

NTLM may also be accepted by HTTP applications.

Examples can include:

```text
IIS
Management Interfaces
Enterprise Applications
Certificate Services
Internal Portals
```

The impact depends on the application's authentication and authorisation model.

---

# HTTP Integrated Authentication

Windows-integrated applications may support:

```text
Negotiate
NTLM
```

Conceptually:

```text
Browser / Client
      |
      v
HTTP 401
      |
      v
WWW-Authenticate
      |
      v
Negotiate / NTLM
```

If NTLM is selected and protections are insufficient, relay may be relevant.

---

# Extended Protection for Authentication

Extended Protection for Authentication, commonly:

```text
EPA
```

provides mechanisms intended to protect integrated authentication from credential forwarding and relay.

EPA can use concepts such as:

```text
Channel Binding
Service Binding
```

to associate authentication with the intended connection or service.

---

# EPA

Conceptually:

```text
NTLM Credential
      |
      v
Expected Service / TLS Channel
      |
      v
Binding Verification
      |
      v
Authentication
```

A forwarded authentication attempt may fail if it does not match the expected binding.

---

# HTTP Relay and AD CS

A particularly important historical and current-hardening area involves HTTP-based Active Directory Certificate Services enrollment endpoints.

Conceptually:

```text
Privileged Machine Authentication
        |
        v
HTTP Relay
        |
        v
Certificate Enrollment Endpoint
        |
        v
Certificate
        |
        v
Alternative Authentication
```

This class of attack is commonly associated with:

```text
AD CS ESC8
```

A dedicated AD CS page should cover ESC8 in detail.

---

# Do Not Treat All IIS as Relayable

An IIS server may have:

```text
Windows Authentication
```

but still be protected through:

```text
Kerberos
EPA
TLS
Application Configuration
Authorization
```

Always validate the actual authentication configuration.

---

# MSSQL Relay

SQL Server environments may support Windows authentication.

Conceptually:

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
MSSQL
```

The resulting impact depends on the victim's SQL Server permissions.

Examples include:

```text
Database Read
Database Write
Server Roles
sysadmin
```

Do not assume domain privilege maps directly to SQL privilege.

---

# Cross-Protocol Relay

NTLM authentication may sometimes be received over one protocol and relayed to another.

Conceptually:

```text
Authentication Source
        |
        v
      NTLM
        |
        v
Relay Infrastructure
        |
        +--> SMB
        |
        +--> LDAP
        |
        +--> HTTP
        |
        +--> MSSQL
```

Whether a specific cross-protocol path works depends on protocol details and protections.

---

# Same-Host Relay

Relaying authentication back to the same host is subject to additional Windows protections and protocol behaviour.

Do not assume:

```text
Victim Host
    |
    v
Relay Back to Victim Host
```

will work merely because a service accepts NTLM.

Loopback protections, signing, EPA, and authentication context may prevent it.

---

# Reflection vs Relay

Historically, authentication reflection attacks involved returning authentication to the same system.

Relay usually refers more broadly to forwarding authentication to another service or target.

Modern Windows protections have significantly changed many historical reflection scenarios.

Keep:

```text
Reflection
```

and:

```text
Relay
```

conceptually separate.

---

# ntlmrelayx

Impacket provides:

```text
ntlmrelayx.py
```

for authorised NTLM relay testing.

Modern package installations commonly expose:

```bash
impacket-ntlmrelayx
```

Check the installed version:

```bash
impacket-ntlmrelayx -h
```

---

# Basic Targeted Relay Model

The safest assessment approach is:

```text
One Controlled Authentication Source
             |
             v
One Approved Relay Target
             |
             v
One Expected Action
```

rather than:

```text
Whole Network
     |
     v
Relay Everywhere
```

---

# Single Target

A conceptual single-target invocation is:

```bash
impacket-ntlmrelayx \
    -t smb://10.10.10.21
```

This starts relay infrastructure targeting the specified service.

Actual successful authentication still requires an authorised authentication source to reach the relay listener.

---

# Target File

For multiple approved targets, `ntlmrelayx` supports target-list workflows.

Conceptually:

```bash
impacket-ntlmrelayx \
    -tf relay-targets.txt
```

Before using a target file, ensure every host is explicitly in scope and has already been assessed for relay compatibility.

---

# Target File Example

```text
smb://10.10.10.21
smb://10.10.10.24
ldap://dc01.corp.example
```

Do not blindly populate a relay file from every discovered host.

---

# Protocol-Specific Help

Because `ntlmrelayx` evolves, always inspect:

```bash
impacket-ntlmrelayx -h
```

before using protocol-specific functionality.

Do not copy syntax from old tutorials without validating it against the installed Impacket version.

---

# SOCKS Mode

`ntlmrelayx` versions may support a SOCKS mode that maintains authenticated sessions for subsequent use.

Conceptually:

```text
Relayed Authentication
        |
        v
Authenticated Session
        |
        v
SOCKS Proxy
        |
        v
Compatible Client Tool
```

This can increase assessment impact and should only be used when explicitly required.

---

# Why SOCKS Matters

Without session reuse:

```text
Relay
  |
  v
Immediate Action
```

With session reuse:

```text
Relay
  |
  v
Authenticated Session
  |
  v
Additional Operations
```

The latter should be considered a higher-impact validation step.

---

# Responder and ntlmrelayx

A common authorised lab architecture is:

```text
Victim
  |
  v
Name Resolution / Authentication
  |
  v
Responder Host
  |
  v
ntlmrelayx
  |
  v
Target
```

However, when Responder is used alongside a dedicated relay listener, services that compete for the same ports may need to be disabled in Responder.

Exact configuration depends on the workflow and version.

---

# Responder Configuration

Responder commonly uses:

```text
Responder.conf
```

to enable or disable listeners.

For relay workflows, practitioners often ensure that the services required by the relay tool are not simultaneously occupied by Responder.

Do not change a shared assessment host blindly.

Check:

```bash
sudo ss -lntup
```

to identify listening services and port conflicts.

---

# Authentication Coercion

Rather than waiting for accidental authentication, some Active Directory attack paths can cause a remote system to authenticate to an attacker-controlled endpoint.

This is known broadly as:

```text
Authentication Coercion
```

Conceptually:

```text
Attacker
   |
   v
Trigger Remote Behaviour
   |
   v
Victim System
   |
   v
Authenticates to Attacker
   |
   v
Relay
```

A dedicated page should cover coercion techniques separately.

---

# Coercion Is Not Relay

This distinction is important.

```text
Coercion
```

answers:

```text
How do we cause authentication?
```

Relay answers:

```text
Where can that authentication be forwarded?
```

The complete chain is:

```text
Coercion
   |
   v
Authentication
   |
   v
Relay
   |
   v
Target
```

---

# Machine Authentication

Authentication coercion may produce authentication from a computer account.

Example:

```text
DC01$
```

Computer accounts can have significant privileges.

Therefore:

```text
Machine Account
      |
      X
Low Value
```

is an unsafe assumption.

---

# Domain Controller Authentication

A coerced Domain Controller authentication can be particularly sensitive.

Conceptually:

```text
DC01$
  |
  v
Authentication
  |
  v
Relay
  |
  v
Directory / Certificate / Other Service
```

The resulting impact depends on the relay destination and available protocol protections.

---

# Relay to the Originating Domain Controller

Do not assume a Domain Controller can simply be coerced and relayed back to every service on itself.

Protections such as:

```text
LDAP Signing
Channel Binding
EPA
SMB Signing
Loopback Protections
```

may prevent particular paths.

Assess each protocol independently.

---

# Privilege Mapping

Before active relay testing, determine:

```text
Who Might Authenticate?
```

and:

```text
What Can They Access?
```

Example:

```text
HELPDESK01$
      |
      v
Relay
      |
      v
FILE01
      |
      X
No Useful Rights
```

versus:

```text
ADMIN-WS$
      |
      v
Relay
      |
      v
Management Service
      |
      v
Useful Privilege
```

---

# BloodHound and Relay Analysis

BloodHound does not replace protocol configuration analysis, but it can help identify:

```text
Administrative Relationships
Computer Control
Group Membership
ACL Paths
Delegation Paths
```

which can help determine the value of a relayed identity.

See:

[BloodHound](bloodhound.md)

---

# Relay Target Inventory

A useful inventory can include:

```text
Host
IP
Protocol
Port
NTLM Accepted
Signing Required
Channel Binding
EPA
Victim Privilege
Relay Tested
Result
```

Example:

```text
FILE01
10.10.10.21
SMB
445
Yes
Signing Not Required
N/A
N/A
Admin Relationship Present
Not Tested
```

---

# Do Not Equate Configuration with Exploitation

Finding:

```text
SMB Signing Not Required
```

does not by itself prove:

```text
Successful NTLM Relay
```

The complete chain still requires:

```text
NTLM Authentication
        +
Reachability
        +
Useful Victim
        +
Compatible Target
```

---

# SMB Signing Finding

A valid finding may simply be:

```text
SMB Signing Is Not Required
```

The impact explanation can state that this increases exposure to NTLM relay where an attacker can obtain suitable authentication.

Do not claim:

```text
Domain Compromise
```

unless an actual attack path supports it.

---

# LDAP Signing Finding

Likewise:

```text
LDAP Signing Not Required
```

is a configuration weakness.

The resulting risk depends on:

```text
NTLM Usage
Channel Binding
Relay Path
Victim Permissions
```

---

# EPA Finding

For HTTP applications using Windows Integrated Authentication, lack of EPA can increase relay exposure.

The finding should identify:

```text
Affected Endpoint
Authentication Method
EPA Configuration
TLS Configuration
Potential Authentication Source
Resulting Privilege
```

---

# Safe Validation Strategy

Use:

```text
Level 1
Enumerate Services

Level 2
Enumerate Signing / Binding

Level 3
Identify Potential Relay Targets

Level 4
Map Victim Privileges

Level 5
Use Controlled Authentication

Level 6
Relay to One Target

Level 7
Confirm Authentication

Level 8
Stop
```

Only proceed further if the assessment requires impact validation.

---

# Preferred Authentication Source

Where possible, use:

```text
Dedicated Test User
```

or:

```text
Dedicated Test Computer
```

instead of coercing a privileged production identity.

This allows the relay mechanism to be validated without creating unnecessary credential or privilege exposure.

---

# Controlled Lab Model

```text
TESTUSER
   |
   v
Controlled Authentication
   |
   v
Relay Host
   |
   v
TESTSERVER
```

Grant the test identity a harmless resource permission if demonstrating authorisation is necessary.

---

# Avoid Broad Poisoning

Broadcast or multicast poisoning can affect unrelated systems.

Avoid:

```text
Listen Everywhere
Respond to Everything
Relay Every Authentication
```

on production networks unless specifically authorised.

A targeted validation is preferable.

---

# Avoid Relaying Real Administrator Authentication

Do not intentionally wait for or induce:

```text
Domain Admin
Enterprise Admin
Tier 0 Administrator
```

authentication merely to prove that relay is possible.

Use lower-impact evidence whenever possible.

---

# Stop After Authentication

If the objective is:

```text
Demonstrate NTLM Relay
```

then:

```text
Successful Relay Authentication
```

may already be sufficient.

Do not automatically proceed to:

```text
Credential Dumping
Remote Command Execution
Account Creation
ACL Modification
RBCD
Certificate Enrollment
```

---

# Detection

NTLM relay detection requires correlation across:

```text
Authentication
Network
Endpoint
Directory
Protocol Configuration
```

There is no single universal:

```text
NTLM Relay Event
```

that identifies every relay attack.

---

# NTLM Authentication Events

Windows authentication telemetry can include:

```text
4624
4776
```

depending on the authentication path.

These events should be interpreted together with:

```text
Source Address
Workstation
Logon Type
Account
Target
Protocol
```

---

# Event 4624

Event:

```text
4624
```

records successful logons.

Useful fields can include:

```text
Account Name
Account Domain
Logon Type
Authentication Package
Workstation Name
Source Network Address
Process Information
```

Unexpected combinations can support relay investigations.

---

# Event 4776

Event:

```text
4776
```

records credential validation using NTLM for domain accounts.

It can provide useful information about:

```text
Account
Source Workstation
Validation Result
```

but does not independently prove relay.

---

# NTLM Operational Logging

Windows provides NTLM auditing capabilities that can help organisations understand:

```text
Where NTLM Is Used
Which Systems Depend on NTLM
Which Accounts Authenticate with NTLM
```

This is important before attempting to restrict NTLM.

---

# Network Detection

Network monitoring can help identify unusual authentication flows.

Conceptually:

```text
Victim
  |
  v
Attacker Host
  |
  v
Target
```

Correlate authentication timing and source relationships.

---

# Relay Timing

Relay often produces closely timed activity:

```text
20:15:31 Victim -> Attacker
20:15:31 Attacker -> Target
```

This timing relationship can be useful when combined with network and authentication logs.

---

# Unexpected Source Hosts

Suppose:

```text
ADMIN01
```

normally accesses:

```text
FILE01
```

directly.

A relay may cause the target to observe network activity originating from:

```text
Pentest Host
```

while authentication is associated with:

```text
ADMIN01's Identity
```

This discrepancy can be useful for detection.

---

# SMB Detection

Potential SMB relay indicators include:

```text
NTLM Authentication
+
Unexpected Source
+
Administrative Access
+
SMB Signing Not Required
```

No single field is sufficient.

---

# LDAP Detection

LDAP relay may result in directory changes.

Monitor events such as:

```text
5136
```

for modifications to important attributes.

Potentially sensitive changes include:

```text
Group Membership
ACLs
Delegation
msDS-AllowedToActOnBehalfOfOtherIdentity
msDS-KeyCredentialLink
```

depending on the attack path.

---

# Event 5136

Directory Service Changes auditing can record modifications to Active Directory objects.

For relay investigations, correlate:

```text
5136
      |
      v
Modified Attribute
      |
      v
Authenticated Principal
      |
      v
Source / Timing
```

---

# Event 4741

Computer account creation may generate:

```text
4741
```

This can be relevant where a relay chain results in computer-account creation.

Correlate:

```text
Who Created It?
When?
From Which Workflow?
Was It Expected?
```

---

# Event 4728 / 4732 / 4756

Group membership changes may generate events such as:

```text
4728
4732
4756
```

depending on group scope.

These can be relevant where relayed LDAP authentication results in group modification.

---

# Certificate Enrollment Detection

Where relay targets certificate enrollment services, certificate issuance and CA audit logs become important.

A dedicated AD CS section should cover:

```text
Certificate Request Events
Template
Requester
SAN
EKU
Issuance
Authentication
```

---

# Detect Authentication Coercion Separately

The authentication source may itself create telemetry.

Therefore investigate:

```text
Coercion Event
      |
      v
Outbound Authentication
      |
      v
Relay
      |
      v
Target Activity
```

rather than only the final target action.

---

# Detection Model

```text
Unexpected Authentication
        |
        v
Unexpected Network Path
        |
        v
NTLM
        |
        v
Sensitive Target
        |
        v
Privileged Operation
```

---

# Detect Relay Infrastructure

Potential signals from an unauthorised relay host include:

```text
Listening SMB / HTTP Services
Connections from Multiple Internal Hosts
Immediate Connections to Other Internal Services
Unusual Python Processes
Impacket-Like Network Behaviour
```

Do not rely solely on:

```text
Process Name
```

or:

```text
Tool Signature
```

because implementations can vary.

---

# Hardening

The strongest long-term strategy is:

```text
Reduce NTLM
+
Enforce Protocol Protections
+
Reduce Coercion Paths
+
Apply Least Privilege
```

---

# Require SMB Signing

Where operationally supported, require SMB signing on systems that should not accept unsigned SMB sessions.

Review both:

```text
SMB Server
SMB Client
```

configuration.

---

# SMB Signing Through Group Policy

Relevant policy settings include SMB client and server signing requirements.

Use current Microsoft guidance and test application compatibility before broad deployment.

Group Policy can centrally enforce these settings.

See:

[Active Directory Group Policy](group-policy.md)

---

# Require LDAP Signing

Configure Domain Controllers to require LDAP signing where compatible with organisational applications.

Before enforcement:

```text
Audit
   |
   v
Identify Unsigned LDAP Clients
   |
   v
Remediate
   |
   v
Enforce
```

Do not enable enforcement blindly in a production environment without identifying legacy dependencies.

---

# LDAP Channel Binding

Configure LDAP channel binding according to current Microsoft guidance.

A sensible migration approach is:

```text
Audit
   |
   v
Identify Compatibility Issues
   |
   v
Remediate Applications
   |
   v
Increase Enforcement
```

---

# Extended Protection for Authentication

Enable EPA for supported Windows-authenticated HTTP services, particularly sensitive administrative and certificate-related endpoints.

Validate application compatibility.

---

# Prefer Kerberos

Where possible:

```text
Kerberos
```

should be preferred over:

```text
NTLM
```

for domain authentication.

However, simply enabling Kerberos does not guarantee that clients will never fall back to NTLM.

Monitor actual authentication behaviour.

---

# Reduce NTLM

A mature hardening programme should inventory NTLM before restricting it.

```text
Audit NTLM
   |
   v
Identify Dependencies
   |
   v
Fix Applications
   |
   v
Restrict NTLM
```

---

# Do Not Disable NTLM Blindly

Immediate NTLM disablement may break:

```text
Legacy Applications
Appliances
File Services
Management Tools
Old Authentication Workflows
```

Use auditing and staged enforcement.

---

# Disable LLMNR Where Appropriate

Where local name-resolution protocols are unnecessary, disabling:

```text
LLMNR
```

can reduce poisoning opportunities.

This addresses an authentication-source path rather than fixing relay at the target.

---

# Disable NetBIOS Name Resolution Where Appropriate

Where operationally feasible, reducing reliance on:

```text
NBT-NS
```

can further reduce local name-resolution poisoning opportunities.

Again:

```text
Disable Poisoning Source
```

and:

```text
Prevent Relay
```

are complementary controls.

---

# mDNS

Multicast DNS may also be relevant in local network name-resolution attacks.

Its role depends on:

```text
Operating System
Applications
Network
Responder Configuration
```

Assess whether it is required before restricting it.

---

# Network Segmentation

Restrict unnecessary communication between:

```text
User Workstations
Servers
Domain Controllers
Administrative Systems
```

A relay host cannot forward authentication to a service it cannot reach.

---

# Host Firewalling

Host firewalls can restrict:

```text
SMB
LDAP
HTTP Management
RPC
WinRM
MSSQL
```

to authorised management and application networks.

---

# Least Privilege

Relay impact depends heavily on the victim's privileges.

Reducing:

```text
Local Administrator Reuse
Broad Server Administration
Over-Privileged Service Accounts
Excessive Directory ACLs
```

limits the impact of successful relay.

---

# Local Administrator Management

Avoid using the same privileged local administrator credentials across many systems.

LAPS can help manage unique local administrator passwords.

See:

[Active Directory LAPS](laps.md)

---

# Protect Privileged Accounts

Privileged accounts should not routinely authenticate to:

```text
User Workstations
Untrusted Servers
Low-Trust Applications
```

This reduces the opportunities for their authentication to be captured or relayed.

---

# Administrative Tiering

A simplified model is:

```text
Tier 0
  |
  X
Tier 1 / Tier 2 Authentication

Tier 1
  |
  X
User Workstations
```

The exact architecture should reflect the organisation's privileged-access model.

---

# Protected Users

The:

```text
Protected Users
```

group provides additional authentication protections for suitable privileged accounts.

It can reduce use of older authentication mechanisms, but it should be deployed only after compatibility testing.

It is not a substitute for protocol hardening.

---

# Disable Unnecessary Services

Reduce exposed services that accept:

```text
NTLM
```

where they are not operationally required.

This reduces potential relay destinations.

---

# AD CS Hardening

Where AD CS web enrollment endpoints exist:

```text
Require HTTPS
Enable EPA Where Supported
Review NTLM Authentication
Review Enrollment Permissions
Review Templates
```

A dedicated AD CS section should provide the full hardening model.

---

# Relay Hardening Model

```text
Authentication Source
        |
        v
Can We Prevent It?
        |
        +--> Disable LLMNR
        +--> Reduce NBT-NS
        +--> Reduce Coercion
        |
        v
Can We Prevent Forwarding?
        |
        +--> SMB Signing
        +--> LDAP Signing
        +--> Channel Binding
        +--> EPA
        |
        v
Can We Reduce Impact?
        |
        +--> Least Privilege
        +--> Segmentation
        +--> Administrative Tiering
```

Defence should address all three layers.

---

# Incident Response

If NTLM relay is suspected:

```text
Identify Authentication Source
        |
        v
Identify Relay Host
        |
        v
Identify Relay Target
        |
        v
Identify Victim Identity
        |
        v
Determine Actions Performed
        |
        v
Contain
        |
        v
Remediate Protocol Weakness
```

---

# Identify the Relay Host

Investigate:

```text
Source IP
Listening Services
Network Connections
Processes
Authentication Timing
```

A system receiving authentication and immediately initiating connections to internal services deserves scrutiny.

---

# Identify the Victim

Determine:

```text
Which User / Computer Authenticated?
```

Then establish:

```text
Why Did It Authenticate?
```

Possible causes include:

```text
Poisoning
Coercion
UNC Access
Application Behaviour
User Interaction
```

---

# Identify the Target

Determine:

```text
Which Service Received the Relay?
```

Examples:

```text
SMB
LDAP
LDAPS
HTTP
MSSQL
```

Then review actions performed under the relayed identity.

---

# Review Directory Changes

If LDAP was involved, review:

```text
Group Changes
ACL Changes
Computer Objects
Delegation
KeyCredentialLink
SPNs
Other Attributes
```

---

# Review Host Changes

If SMB or another administrative protocol was involved, review:

```text
Services
Scheduled Tasks
Files
Registry
Local Groups
Processes
Remote Sessions
Credential Access
```

---

# Review Certificate Issuance

If an AD CS endpoint was targeted, determine whether certificates were issued.

If a malicious certificate exists, password rotation alone may not invalidate the attacker's certificate.

This requires certificate-specific incident response.

---

# Credential Rotation

Do not automatically assume:

```text
NTLM Relay
      =
Password Stolen
```

Relay does not necessarily reveal the plaintext password or NT hash.

Credential rotation may still be appropriate depending on subsequent actions, compromise scope, and evidence.

---

# Remove Persistence

The relayed authentication may have been used to create persistence through:

```text
Group Membership
ACL
RBCD
Shadow Credentials
Certificate
Account Creation
Scheduled Task
Service
```

Investigate the resulting actions, not only the original authentication.

---

# Reporting

Good finding titles include:

```text
SMB Signing Is Not Required on Internal Servers
```

```text
LDAP Signing Is Not Enforced on Domain Controllers
```

```text
NTLM Relay Allows Authentication to Internal SMB Services
```

```text
NTLM Relay Enables Active Directory Modification
```

```text
Windows Integrated Authentication Endpoint Lacks Relay Protection
```

Choose the title that matches the evidence.

---

# Example Finding - SMB Signing

```text
Finding:
SMB Signing Is Not Required on Internal Servers

Affected Systems:
FILE01
APP01
MGMT01

Description:
The affected systems accept SMB sessions without requiring SMB message
signing.

SMB signing provides integrity protection for SMB communications and
helps prevent authentication relay attacks.

An attacker capable of obtaining a suitable NTLM authentication attempt
could potentially relay that authentication to an affected SMB service.

Impact:
The resulting impact depends on the privileges of the relayed identity
on the target system.

If an administrative identity is relayed to a system on which it has
administrative rights, the attack may result in unauthorised
administrative access.

Recommendation:
Require SMB signing on affected systems where operationally supported.

Review both SMB server and SMB client signing policies and deploy the
configuration through centrally managed policy.

Reduce NTLM usage and restrict privileged accounts from authenticating
to lower-trust systems.
```

---

# Example Finding - LDAP Relay

```text
Finding:
LDAP Configuration Permits NTLM Relay to Active Directory

Affected Systems:
DC01.corp.example
DC02.corp.example

Description:
The assessed Domain Controllers accept an LDAP authentication path
without sufficient signing or binding protection to prevent the tested
NTLM relay scenario.

During controlled validation, authentication from a dedicated test
identity was relayed to LDAP.

No privileged production identity was used and no persistent directory
changes were made.

Impact:
An attacker capable of obtaining NTLM authentication from an identity
with directory write permissions may be able to perform Active
Directory operations using the relayed identity.

The exact impact depends on the permissions of the authentication
source.

Recommendation:
Enforce LDAP signing and configure LDAP channel binding according to
current Microsoft guidance.

Audit existing LDAP clients before enforcement to identify incompatible
applications.

Reduce NTLM usage and review directory permissions assigned to users,
computers, and service accounts.
```

---

# Example Finding - Relay Chain

```text
Finding:
NTLM Relay Enables Modification of Server Computer Object

Source Identity:
CORP\svc-management

Target:
APP01$

Description:
The svc-management account can be induced to authenticate using NTLM.

The resulting authentication can be relayed to an Active Directory
service where the account has write permissions over the APP01$
computer object.

The combination of NTLM relay exposure and excessive directory
permissions creates an attack path that can result in unauthorised
modification of APP01$.

Impact:
An attacker with network access to the authentication source and relay
target may be able to act using the directory permissions assigned to
svc-management.

The resulting impact depends on the attributes that can be modified and
the downstream privileges associated with APP01$.

Recommendation:
Remove unnecessary write permissions from svc-management.

Enforce appropriate signing, channel-binding, and Extended Protection
controls on services accepting Windows Integrated Authentication.

Reduce or eliminate unnecessary NTLM authentication and restrict
authentication coercion paths.
```

---

# Severity

Severity should be based on the complete path.

```text
Authentication Source
      +
Relay-Compatible Target
      +
Missing Protection
      +
Victim Privilege
      +
Resulting Action
      =
Severity
```

For example:

```text
SMB Signing Not Required
        |
        v
No Identified Authentication Source
```

may be reported as a hardening weakness.

Compare:

```text
Coercible Privileged Account
        |
        v
NTLM Relay
        |
        v
Sensitive Service
        |
        v
Administrative Action
```

which can represent a high or critical attack path.

---

# Evidence Checklist

Record:

```text
Authentication Source
Victim Identity
Victim Type
Relay Host
Relay Target
Target Protocol
Target Port
NTLM Accepted
Signing Configuration
Channel Binding Configuration
EPA Configuration
Victim Privilege
Relay Result
Resulting Action
Timestamp
Relevant Events
Cleanup
```

Do not include:

```text
Reusable Credentials
Captured Passwords
NT Hashes
Kerberos Tickets
Private Keys
```

unless strictly required and handled according to the engagement rules.

---

# NTLM Relay Assessment Checklist

## Preparation

- [ ] Confirm NTLM relay testing is authorised
- [ ] Confirm poisoning restrictions
- [ ] Confirm authentication coercion restrictions
- [ ] Confirm privileged-account restrictions
- [ ] Confirm target systems
- [ ] Confirm allowed protocols
- [ ] Define stop conditions
- [ ] Define cleanup requirements

## Discovery

- [ ] Identify Domain Controllers
- [ ] Identify SMB servers
- [ ] Identify LDAP services
- [ ] Identify LDAPS
- [ ] Identify Windows-authenticated HTTP services
- [ ] Identify MSSQL
- [ ] Identify NTLM usage
- [ ] Identify administrative relationships
- [ ] Identify potential authentication sources

## SMB

- [ ] Enumerate TCP 445
- [ ] Check SMB version
- [ ] Check SMB signing support
- [ ] Check whether signing is required
- [ ] Identify victim privileges
- [ ] Build approved relay target list
- [ ] Avoid assuming every SMB server is relayable

## LDAP

- [ ] Identify LDAP
- [ ] Identify LDAPS
- [ ] Review LDAP signing
- [ ] Review LDAP channel binding
- [ ] Review NTLM acceptance
- [ ] Identify directory rights of potential victims
- [ ] Review RBCD relationships
- [ ] Review ACL relationships

## HTTP

- [ ] Identify Windows Integrated Authentication
- [ ] Identify NTLM
- [ ] Identify HTTPS
- [ ] Review EPA
- [ ] Review channel binding
- [ ] Identify sensitive management endpoints
- [ ] Identify AD CS web endpoints where applicable
- [ ] Review application authorisation

## Authentication Sources

- [ ] Identify LLMNR exposure
- [ ] Identify NBT-NS exposure
- [ ] Identify mDNS exposure
- [ ] Identify UNC-triggered authentication
- [ ] Identify application-triggered authentication
- [ ] Identify coercion paths
- [ ] Prefer controlled test authentication
- [ ] Avoid broad production poisoning

## Privilege Mapping

- [ ] Identify expected victim
- [ ] Determine target privileges
- [ ] Identify local administrator relationships
- [ ] Identify directory write permissions
- [ ] Identify SQL privileges
- [ ] Identify certificate enrollment rights
- [ ] Identify downstream attack paths

## Validation

- [ ] Use one controlled target
- [ ] Use dedicated test identity where possible
- [ ] Confirm authentication
- [ ] Confirm relay
- [ ] Confirm minimum required impact
- [ ] Avoid remote execution unless required
- [ ] Avoid credential dumping unless required
- [ ] Avoid persistent directory changes
- [ ] Stop when sufficient evidence exists

## Detection

- [ ] Review event 4624
- [ ] Review event 4776
- [ ] Review NTLM operational logs
- [ ] Review network authentication flows
- [ ] Identify unexpected source systems
- [ ] Monitor event 5136
- [ ] Monitor event 4741
- [ ] Monitor group membership changes
- [ ] Monitor RBCD changes
- [ ] Monitor certificate issuance
- [ ] Monitor suspicious relay infrastructure
- [ ] Correlate coercion with relay

## Hardening

- [ ] Require SMB signing
- [ ] Review SMB client signing
- [ ] Require LDAP signing
- [ ] Configure LDAP channel binding
- [ ] Enable EPA where supported
- [ ] Prefer Kerberos
- [ ] Audit NTLM usage
- [ ] Reduce NTLM
- [ ] Disable unnecessary LLMNR
- [ ] Reduce unnecessary NBT-NS
- [ ] Review mDNS requirements
- [ ] Reduce authentication coercion paths
- [ ] Apply network segmentation
- [ ] Apply host firewalling
- [ ] Reduce administrative credential exposure
- [ ] Apply administrative tiering
- [ ] Review AD CS HTTP endpoints

## Incident Response

- [ ] Identify authentication source
- [ ] Identify relay host
- [ ] Identify relay target
- [ ] Identify victim identity
- [ ] Identify target protocol
- [ ] Identify resulting action
- [ ] Review directory changes
- [ ] Review host changes
- [ ] Review certificate issuance
- [ ] Identify persistence
- [ ] Contain relay infrastructure
- [ ] Remediate protocol configuration
- [ ] Review NTLM dependencies

## Cleanup

- [ ] Stop relay listeners
- [ ] Stop poisoning listeners
- [ ] Remove test target lists
- [ ] Remove temporary credentials
- [ ] Remove temporary certificates
- [ ] Revert authorised test directory changes
- [ ] Verify no test computer objects remain
- [ ] Verify no RBCD changes remain
- [ ] Verify no group changes remain
- [ ] Verify no test services or tasks remain
- [ ] Record cleanup evidence

---

# NTLM Relay Testing Model

The basic model is:

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
Target
```

The capture model is:

```text
Victim
  |
  v
NetNTLM Challenge / Response
  |
  v
Capture
  |
  v
Offline Password Guessing
```

The relay model is:

```text
Victim
  |
  v
Live NTLM Authentication
  |
  v
Forward Exchange
  |
  v
Target Authentication
```

The complete attack-path model is:

```text
Authentication Source
        |
        v
NTLM
        |
        v
Relay Host
        |
        v
Relay-Compatible Target
        |
        v
Victim Privilege
        |
        v
Resulting Action
```

The poisoning model is:

```text
Name Resolution Failure
        |
        v
LLMNR / NBT-NS / mDNS
        |
        v
Attacker Response
        |
        v
NTLM Authentication
        |
        +--> Capture
        |
        +--> Relay
```

The coercion model is:

```text
Attacker
   |
   v
Coercion Primitive
   |
   v
Victim
   |
   v
Outbound Authentication
   |
   v
Relay
```

The SMB protection model is:

```text
NTLM
  |
  v
SMB
  |
  v
Signing Required?
  |
  +--> Yes -> Relay Mitigated
  |
  +--> No  -> Potential Relay Surface
```

The LDAP protection model is:

```text
NTLM
  |
  v
LDAP / LDAPS
  |
  +--> Signing
  |
  +--> Channel Binding
  |
  v
Relay Feasibility
```

The HTTP protection model is:

```text
Windows Integrated Authentication
          |
          v
NTLM
          |
          v
EPA / Channel Binding
          |
          v
Relay Resistance
```

The privilege model is:

```text
Successful Relay
      |
      v
Victim Privilege
      |
      +--> Low Privilege -> Limited Impact
      |
      +--> High Privilege -> High Impact
```

The safe-testing model is:

```text
Enumerate
   |
   v
Identify Weak Configuration
   |
   v
Map Privilege
   |
   v
Controlled Authentication
   |
   v
Single Relay
   |
   v
Confirm
   |
   v
Stop
```

The defensive model is:

```text
Reduce Authentication Sources
          |
          +
Enforce Signing / Binding
          |
          +
Reduce NTLM
          |
          +
Least Privilege
          |
          +
Segmentation
          |
          v
Reduced Relay Risk
```

The most important distinction is:

```text
Captured NTLM Authentication
        |
        X
NT Hash Obtained
```

A NetNTLM challenge-response is not the same thing as the underlying NT password hash.

Another important distinction is:

```text
NTLM Relay
    |
    X
Pass-the-Hash
```

Relay forwards a live authentication exchange.

Pass-the-Hash uses an already obtained NT hash.

Another important distinction is:

```text
SMB Signing Not Required
        |
        X
Guaranteed Domain Compromise
```

The complete path still depends on:

```text
Authentication
+
Victim
+
Target
+
Privilege
```

For penetration testers:

```text
Do Not Ask:
"How many hosts can I relay to?"

Ask:
"Which authentication sources can be relayed
to which targets, and what privilege would
the relayed identity provide?"
```

For defenders:

```text
Do Not Ask:
"Do we still use NTLM?"

Ask:
"Where is NTLM used, which services accept it,
which protections are enforced, and which
privileged identities can reach those services?"
```

The final relay relationship is:

```text
Authentication Source
      |
      v
NTLM
      |
      v
Protocol Protection
      |
      v
Target
      |
      v
Identity Privilege
      |
      v
Impact
```

NTLM relay risk should always be evaluated across that complete chain.

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

NTLM:

[NTLM](ntlm.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Groups:

[Active Directory Groups](groups.md)

Group Policy:

[Active Directory Group Policy](group-policy.md)

Machine Account Quota:

[Active Directory Machine Account Quota](machine-account-quota.md)

RBCD:

[Resource-Based Constrained Delegation](rbcd.md)

Shadow Credentials:

[Active Directory Shadow Credentials](shadow-credentials.md)

LAPS:

[Active Directory LAPS](laps.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The next pages in this section are:

```text
active-directory/kerberos-relay.md
active-directory/authentication-coercion.md
```

---

# References

## Microsoft - SMB Signing

[Microsoft - SMB Signing](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Security

[Microsoft - SMB Security Hardening](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security-hardening){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - LDAP Signing

[Microsoft - LDAP Signing](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - LDAP Channel Binding

[Microsoft - LDAP Channel Binding and LDAP Signing Requirements](https://support.microsoft.com/en-us/topic/2020-2023-and-2024-ldap-channel-binding-and-ldap-signing-requirements-for-windows-kb4520412-ef185fb8-00f7-167d-744c-f299a66fc00a){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Extended Protection for Authentication

[Microsoft - Extended Protection for Authentication](https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/extended-protection-for-authentication-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - NTLM Auditing

[Microsoft - Network Security: Restrict NTLM](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/jj852207(v=ws.11)){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 4624

[Microsoft - Event 4624](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4624){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 4776

[Microsoft - Event 4776](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4776){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 5136

[Microsoft - Event 5136](https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-5136){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket - ntlmrelayx.py](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## Responder

[Responder](https://github.com/lgandx/Responder){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning and SMB Relay](https://attack.mitre.org/techniques/T1557/001/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Forced Authentication](https://attack.mitre.org/techniques/T1187/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

NTLM relay is best understood as an attack against:

```text
Authentication Trust
```

rather than simply:

```text
Password Strength
```

A victim may have:

```text
Long Password
Complex Password
No Password Reuse
```

and still be exposed to relay if:

```text
NTLM Authentication
        |
        v
Attacker
        |
        v
Unprotected Target
```

The password does not need to be cracked.

The key security relationship is:

```text
Authentication Source
        +
Relay-Compatible Service
        +
Missing Protocol Protection
        +
Victim Privilege
        =
Relay Risk
```

This explains why:

```text
SMB Signing
LDAP Signing
LDAP Channel Binding
EPA
```

are important controls.

It also explains why eliminating one poisoning mechanism does not eliminate the complete problem.

For example:

```text
Disable LLMNR
      |
      X
All NTLM Relay Eliminated
```

because authentication may still originate from:

```text
Coercion
Applications
UNC Paths
Other Name Resolution
User Interaction
```

Likewise:

```text
Require SMB Signing
      |
      X
All NTLM Relay Eliminated
```

because other relay destinations may remain.

The defensive objective should therefore be layered:

```text
Reduce NTLM
    |
    v
Reduce Authentication Sources
    |
    v
Enforce Protocol Protection
    |
    v
Reduce Privilege
    |
    v
Segment Services
```

For an authorised penetration test, the preferred approach is:

```text
Discover
   |
   v
Understand
   |
   v
Map
   |
   v
Validate Minimally
   |
   v
Report
```

rather than:

```text
Poison Entire Network
      |
      v
Relay Everything
      |
      v
Execute Everywhere
```

The central offensive-security question is:

```text
Can authentication from identity A
be forwarded to service B?
```

The next question is:

```text
What can identity A do on service B?
```

Those two questions determine whether a relay condition is merely a hardening issue or a meaningful attack path.

The complete security model is:

```text
Identity
   |
   v
Authentication
   |
   v
NTLM
   |
   v
Relay Protection
   |
   v
Service
   |
   v
Authorisation
   |
   v
Impact
```

NTLM relay should therefore always be analysed as an end-to-end authentication and authorisation problem, not merely as the presence of NTLM on a network.
