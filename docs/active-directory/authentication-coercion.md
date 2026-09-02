# Active Directory Authentication Coercion

Authentication coercion is the process of causing a Windows user, computer, server, or service to initiate authentication to a destination chosen or influenced by an attacker.

The fundamental concept is:

```text
Attacker
   |
   v
Trigger Remote Behaviour
   |
   v
Victim
   |
   v
Outbound Authentication
   |
   v
Attacker-Controlled Destination
```

Authentication coercion is important in Active Directory because the resulting authentication can potentially be:

```text
Captured
```

or:

```text
Relayed
```

to another service.

A complete relay chain may therefore look like:

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
Target Service
   |
   v
Victim Privileges
   |
   v
Impact
```

The distinction is essential:

```text
Coercion
   !=
Relay
```

Coercion answers:

```text
How can authentication be triggered?
```

Relay answers:

```text
Where can that authentication be forwarded?
```

MITRE ATT&CK tracks forced authentication as:

```text
T1187 - Forced Authentication
```

!!! warning "Authorised testing only"
    Authentication coercion can cause production systems, including servers and Domain Controllers, to authenticate to an assessment host. Perform active coercion only when it is explicitly permitted by the rules of engagement. Prefer controlled test systems and identities, avoid broad or repeated triggering, and do not automatically relay captured authentication into privileged actions.

---

# Core Concept

Consider a Windows server:

```text
APP01$
```

An attacker interacts with a remote service on APP01 and provides a path referencing another host.

Conceptually:

```text
Attacker
   |
   | RPC / Service Request
   v
APP01
   |
   | Access Remote Resource
   v
\\ATTACKER\share
   |
   v
Authentication Attempt
```

If the operation executes under the computer's security context, the authentication may originate as:

```text
CORP\APP01$
```

The attacker has not necessarily:

```text
Stolen APP01$ Password
```

or:

```text
Obtained APP01$ NT Hash
```

Instead, the attacker caused APP01 to authenticate.

---

# Authentication Coercion Is a Primitive

Authentication coercion should usually be treated as one component of a larger attack path.

```text
Coercion Primitive
        |
        v
Authentication
        |
        +--> Capture
        |
        +--> Relay
        |
        +--> Detection / Validation
```

The coercion primitive by itself may have limited impact.

The importance depends on what can be done with the resulting authentication.

---

# Coercion vs Credential Theft

Do not automatically interpret forced authentication as:

```text
Credential Theft
```

The attacker may receive:

```text
NTLM Authentication
```

without obtaining the underlying:

```text
Password
```

or:

```text
NT Hash
```

The authentication may instead be relayed immediately.

---

# Coercion vs NetNTLM Capture

If the attacker receives NTLM authentication and stores the challenge-response:

```text
Victim
  |
  v
NTLM Authentication
  |
  v
Capture
  |
  v
NetNTLM Challenge / Response
```

the captured material may potentially be used for offline password guessing.

This is different from relay:

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
Target
```

See:

[NTLM](ntlm.md)

[NTLM Relay](ntlm-relay.md)

---

# Coercion vs Kerberos Relay

Authentication coercion does not inherently mean NTLM.

Depending on:

```text
Target Name
SPN
DNS
Service
Protocol
Windows Authentication Behaviour
```

the victim may attempt:

```text
Kerberos
```

or:

```text
NTLM
```

Therefore:

```text
Coercion
   |
   v
Authentication
   |
   +--> Kerberos
   |
   +--> NTLM
```

See:

[Kerberos Relay](kerberos-relay.md)

---

# Why Windows Systems Authenticate Automatically

Windows environments are designed to provide transparent access to domain resources.

A user accessing:

```text
\\FILE01\Finance
```

should not normally need to type credentials repeatedly.

Windows can automatically use the current security context.

This behaviour enables seamless enterprise authentication but also creates security-sensitive situations where applications or services are instructed to access attacker-controlled resources.

---

# UNC Paths

A UNC path commonly looks like:

```text
\\SERVER\share
```

For example:

```text
\\FILE01\Finance
```

If a Windows process attempts to access:

```text
\\ATTACKER\share
```

Windows may attempt authentication to the remote system.

The exact behaviour depends on:

```text
Security Context
Protocol
Network Configuration
NTLM Policy
Kerberos Availability
WebClient
Zone Configuration
Service Behaviour
```

---

# Computer Account Authentication

One of the most important coercion scenarios involves a Windows service running as:

```text
SYSTEM
```

or:

```text
NETWORK SERVICE
```

When such a service accesses a remote resource using the machine identity, authentication may occur as:

```text
DOMAIN\COMPUTER$
```

Example:

```text
CORP\APP01$
```

This is known as:

```text
Computer Account Authentication Coercion
```

---

# Machine Accounts Are Security Principals

A machine account should not be treated as:

```text
Just a Computer Name
```

It is an Active Directory security principal.

Examples include:

```text
WS01$
APP01$
SQL01$
DC01$
```

Machine accounts can have:

```text
Group Memberships
Directory Permissions
Local Administrative Rights
Service Permissions
Kerberos Keys
Certificates
Delegation Rights
```

Therefore machine authentication can be highly valuable.

---

# Domain Controller Authentication

A particularly sensitive coercion target is a Domain Controller.

Example:

```text
CORP\DC01$
```

A Domain Controller computer account participates in privileged Active Directory operations.

Therefore:

```text
DC Authentication
       |
       v
Potential High-Value Relay Source
```

depending on the destination.

---

# Do Not Equate DC Authentication with Domain Compromise

The following is incorrect:

```text
Coerce DC
   |
   v
Domain Compromise
```

The complete chain still requires:

```text
Coercion
   +
Authentication Protocol
   +
Relay-Compatible Target
   +
Missing Protection
   +
Useful Privilege
```

---

# Authentication Coercion Families

Several Windows components have historically provided coercion primitives.

Common names encountered in Active Directory security research include:

```text
PrinterBug
PetitPotam
DFSCoerce
ShadowCoerce
MSEven
WebDAV-Based Coercion
Application-Specific Coercion
```

These are not all equivalent.

Each relies on different:

```text
RPC Interfaces
Services
Functions
Permissions
Network Paths
Windows Versions
Mitigations
```

---

# Coercion Methodology

A useful methodology is:

```text
Identify Target
      |
      v
Identify Exposed Services
      |
      v
Identify Potential Coercion Interface
      |
      v
Determine Required Authentication
      |
      v
Determine Resulting Security Context
      |
      v
Determine Authentication Protocol
      |
      v
Determine Relay Destination
      |
      v
Controlled Validation
```

---

# RPC and Authentication Coercion

Many well-known coercion techniques involve:

```text
MS-RPC
```

Remote Procedure Call allows Windows systems to expose functions remotely.

Conceptually:

```text
Client
  |
  v
RPC Endpoint
  |
  v
Remote Function
  |
  v
Service Performs Operation
```

If the function accepts a remote path:

```text
\\ATTACKER\resource
```

the remote service may attempt to access it.

---

# Named Pipes

RPC interfaces may be reachable through named pipes over SMB.

Examples encountered in Windows environments include:

```text
\PIPE\spoolss
\PIPE\lsarpc
\PIPE\efsrpc
\PIPE\netdfs
```

Availability and access depend on the service and Windows configuration.

The presence of a named pipe alone does not prove coercion is possible.

---

# RPC Endpoint Enumeration

From Windows, RPC-related information can be investigated with built-in administrative and diagnostic tooling.

From Linux, Impacket and other assessment utilities can enumerate RPC interfaces.

For example:

```bash
impacket-rpcdump 10.10.10.20
```

Authenticated environments may require credentials depending on the target and interface.

Check:

```bash
impacket-rpcdump -h
```

for current syntax.

---

# RPC Endpoint Mapper

RPC commonly uses:

```text
TCP/135
```

for endpoint mapping.

Some RPC interfaces are subsequently reached through:

```text
Dynamic RPC Ports
```

while others may be transported over:

```text
SMB Named Pipes
```

Network filtering therefore matters.

---

# PrinterBug

One of the classic authentication-coercion techniques is commonly called:

```text
PrinterBug
```

or:

```text
SpoolSample
```

The technique abuses behaviour exposed through the Windows Print Spooler RPC interface.

At a high level:

```text
Attacker
   |
   v
Print Spooler RPC
   |
   v
Victim
   |
   v
Printer Change Notification
   |
   v
Remote Path
   |
   v
Victim Authentication
```

---

# PrinterBug Concept

The Print Spooler supports remote printer-related operations.

A notification mechanism can cause the target to communicate with a specified system.

Conceptually:

```text
RPC Request
    |
    v
Victim Spooler
    |
    v
Notification Destination
    |
    v
Attacker Host
```

The resulting connection may authenticate using the victim computer account.

---

# Print Spooler Service

On Windows:

```powershell
Get-Service Spooler
```

Example output:

```text
Status   Name     DisplayName
------   ----     -----------
Running  Spooler  Print Spooler
```

A running Spooler service does not automatically prove that remote coercion is possible.

---

# Remote Spooler Exposure

The relevant questions include:

```text
Is Spooler Running?
Is the RPC Interface Reachable?
Can the Caller Access the Interface?
Does the Target Permit the Relevant Operation?
Can the Target Reach the Listener?
```

---

# Domain Controllers and Print Spooler

Domain Controllers generally should not provide unnecessary print services.

If printing is not required on a Domain Controller, disabling the Print Spooler can reduce attack surface.

Before changing production systems, confirm operational requirements.

---

# PetitPotam

Another important coercion technique is commonly called:

```text
PetitPotam
```

PetitPotam demonstrated authentication coercion through the:

```text
Encrypting File System Remote Protocol
```

commonly:

```text
MS-EFSRPC
```

---

# PetitPotam Concept

The simplified model is:

```text
Attacker
   |
   v
EFSRPC Request
   |
   v
Victim
   |
   v
Attempts Remote File Operation
   |
   v
\\ATTACKER\resource
   |
   v
Authentication
```

The attack became particularly important when combined with NTLM relay to certificate enrollment services.

---

# EFSRPC

EFSRPC provides remote functionality related to:

```text
Encrypting File System
```

operations.

Security research demonstrated that certain EFSRPC operations could cause a remote system to access an arbitrary network path.

That network access could trigger authentication.

---

# PetitPotam Is Not an AD CS Vulnerability

This distinction matters.

```text
PetitPotam
```

provides:

```text
Authentication Coercion
```

It does not itself provide:

```text
Certificate Enrollment
```

A complete historical attack path could be:

```text
PetitPotam
     |
     v
DC Authentication
     |
     v
NTLM Relay
     |
     v
AD CS Web Enrollment
     |
     v
Certificate
```

The relay portion is commonly associated with:

```text
ESC8
```

when the AD CS web enrollment configuration is susceptible.

---

# PetitPotam Is Not NTLM Relay

Likewise:

```text
PetitPotam
    !=
ntlmrelayx
```

The first can trigger authentication.

The second can relay suitable authentication.

---

# DFSCoerce

Another coercion technique is commonly called:

```text
DFSCoerce
```

It involves the:

```text
Distributed File System Namespace Management Protocol
```

or:

```text
MS-DFSNM
```

The underlying concept is again:

```text
Remote RPC Operation
       |
       v
Victim Accesses Remote Resource
       |
       v
Authentication
```

---

# DFSCoerce Security Model

Conceptually:

```text
Attacker
   |
   v
DFS RPC
   |
   v
Victim
   |
   v
Remote DFS-Related Operation
   |
   v
Attacker-Controlled Path
   |
   v
Authentication
```

As with other coercion techniques, success depends on:

```text
Interface Availability
Caller Permissions
Patching
Service Configuration
Network Reachability
Authentication Policy
```

---

# ShadowCoerce

Security research has also identified coercion paths involving Microsoft File Server Shadow Copy functionality.

These are often referred to as:

```text
ShadowCoerce
```

The high-level pattern remains:

```text
RPC Operation
    |
    v
Victim
    |
    v
Remote Path
    |
    v
Authentication
```

Do not assume every Windows server exposes every coercion primitive.

---

# MSEven

Other research has demonstrated forced-authentication behaviour involving Windows event-related RPC functionality.

The important lesson is not to memorise one tool name.

Instead understand the generic pattern:

```text
Remote Interface
      |
      v
Attacker-Controlled Path
      |
      v
Victim Accesses Path
      |
      v
Authentication
```

New coercion primitives may continue to be discovered.

---

# Coercer

A commonly used assessment tool for identifying and testing Windows authentication-coercion methods is:

```text
Coercer
```

The project consolidates multiple known coercion techniques.

Always review the installed version and project documentation before testing.

Start with:

```bash
coercer --help
```

The exact supported interfaces and syntax can change between versions.

---

# Why Coercer Is Useful

Instead of manually testing each historical coercion primitive:

```text
PrinterBug
PetitPotam
DFSCoerce
ShadowCoerce
...
```

a framework can help determine which known RPC methods are reachable.

However:

```text
Tool Says Vulnerable
      |
      X
Complete Relay Attack Proven
```

You must still analyse the resulting authentication and target protections.

---

# Safe Coercer Usage

On a production assessment, avoid immediately testing every coercion method against every host.

Prefer:

```text
Enumerate
   |
   v
Select Test Host
   |
   v
Select Listener
   |
   v
Run Minimal Test
   |
   v
Confirm Authentication
   |
   v
Stop
```

---

# Impacket and Coercion

Impacket provides RPC and authentication tooling used by many coercion research projects.

Useful supporting utilities include:

```text
rpcdump
rpcmap
ntlmrelayx
```

Modern installations commonly expose commands such as:

```bash
impacket-rpcdump
```

and:

```bash
impacket-ntlmrelayx
```

Check:

```bash
impacket-rpcdump -h
impacket-ntlmrelayx -h
```

before using version-specific options.

See:

[Impacket](impacket.md)

---

# Authentication Listener

For safe validation, the assessment host can simply observe whether authentication occurs.

The initial objective may be:

```text
Trigger
   |
   v
Observe Connection
```

rather than:

```text
Trigger
   |
   v
Relay
   |
   v
Modify Target
```

---

# Responder Analyze Mode

Responder can be useful for observing local authentication behaviour.

When the objective is discovery rather than active poisoning, use the project's passive or analysis capabilities where appropriate.

Always inspect the installed version:

```bash
responder --help
```

Avoid broad poisoning when the assessment only requires confirmation of a specific coercion path.

---

# Packet Capture

Network capture can provide lower-impact evidence.

For example:

```bash
sudo tcpdump -ni eth0 host 10.10.10.20
```

A more focused filter can be applied based on the expected protocol.

This can confirm:

```text
Victim
   |
   v
Assessment Host
```

communication without automatically attempting relay.

---

# SMB Authentication

A common coercion result is:

```text
Victim
   |
   v
SMB
   |
   v
TCP/445
   |
   v
Assessment Host
```

The authentication may be NTLM depending on naming and environment configuration.

---

# HTTP / WebDAV Authentication

Forced authentication can also occur over:

```text
HTTP
```

through Windows WebDAV behaviour.

This matters because:

```text
SMB Coercion
```

and:

```text
HTTP Coercion
```

can interact differently with relay targets and security controls.

---

# WebClient Service

Windows WebDAV functionality is associated with the:

```text
WebClient
```

service.

Check locally:

```powershell
Get-Service WebClient -ErrorAction SilentlyContinue
```

A running WebClient service can expand the available authentication paths.

It does not automatically prove a useful coercion-and-relay chain.

---

# WebDAV UNC Syntax

Windows can represent WebDAV destinations using UNC-style paths.

Conceptually:

```text
\\SERVER@PORT\DavWWWRoot\resource
```

or other WebDAV-compatible path forms depending on the application and service.

This allows some coercion paths to generate HTTP-based authentication instead of direct SMB authentication.

---

# Why HTTP Coercion Matters

Consider:

```text
Victim
  |
  v
HTTP Authentication
  |
  v
Relay Host
  |
  v
LDAP
```

The relay characteristics may differ from:

```text
Victim
  |
  v
SMB Authentication
  |
  v
Relay Host
  |
  v
LDAP
```

This is why the resulting authentication transport must be identified.

---

# WebClient and Relay Analysis

A useful model is:

```text
WebClient Running?
       |
       v
Can HTTP Authentication Be Triggered?
       |
       v
Can Authentication Reach Relay Host?
       |
       v
Can It Be Relayed?
       |
       v
Does Victim Have Useful Rights?
```

---

# Authentication Protocol Selection

After triggering authentication, determine whether the victim uses:

```text
NTLM
```

or:

```text
Kerberos
```

Do not assume.

Factors include:

```text
Destination Name
DNS
SPN
IP Address vs Hostname
Protocol
Authentication Policy
Service Configuration
```

---

# IP Address vs Hostname

Kerberos generally relies on SPNs associated with names.

An authentication attempt to:

```text
10.10.10.50
```

may behave differently from:

```text
relay01.corp.example
```

This can influence whether authentication uses:

```text
Kerberos
```

or falls back to:

```text
NTLM
```

---

# Coercion Listener Naming

Listener naming can therefore matter.

A relay host might be referenced through:

```text
IP Address
NetBIOS Name
FQDN
DNS Alias
```

Each can produce different authentication behaviour.

During an assessment, record the exact name used.

---

# NTLM Coercion

The classic attack chain is:

```text
Victim
   |
   v
Forced NTLM Authentication
   |
   v
Relay Host
```

The relay host can potentially forward the authentication to:

```text
SMB
LDAP
LDAPS
HTTP
HTTPS
MSSQL
```

depending on target protections and tool support.

See:

[NTLM Relay](ntlm-relay.md)

---

# Kerberos Coercion

A victim may instead authenticate using Kerberos when the destination name and SPN conditions support it.

The resulting attack surface is more constrained because Kerberos tickets are service-bound.

See:

[Kerberos Relay](kerberos-relay.md)

---

# Coercion to SMB Relay

One possible chain is:

```text
Coercion
   |
   v
Victim NTLM
   |
   v
Relay
   |
   v
SMB Server
```

For SMB, a key target-side control is:

```text
SMB Signing
```

If SMB signing is required, common NTLM relay scenarios to SMB are mitigated.

---

# Coercion to LDAP

Another important chain is:

```text
Coercion
   |
   v
Victim Authentication
   |
   v
Relay
   |
   v
LDAP
   |
   v
Active Directory
```

The resulting impact depends on:

```text
LDAP Signing
Channel Binding
Authentication Transport
Victim Directory Rights
```

---

# Coercion to AD CS

A historically significant attack chain is:

```text
Coercion
   |
   v
Machine Authentication
   |
   v
NTLM Relay
   |
   v
AD CS HTTP Enrollment
   |
   v
Certificate
```

This is associated with AD CS relay exposure such as:

```text
ESC8
```

when the relevant prerequisites are present.

---

# AD CS Changes the Impact Model

Without a relay target:

```text
Coercion
   |
   v
Authentication Attempt
```

may be limited.

With a vulnerable certificate enrollment path:

```text
Coercion
   |
   v
Machine Authentication
   |
   v
Certificate Enrollment
   |
   v
Certificate-Based Authentication
```

the resulting certificate can become reusable authentication material.

This is why AD CS must be included in relay assessments.

---

# Coercion to RBCD

Another possible downstream chain is:

```text
Coercion
   |
   v
Relay to LDAP
   |
   v
Write Computer Object
   |
   v
Configure RBCD
   |
   v
S4U
```

This requires the relayed principal to have the necessary directory rights.

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# Coercion to Shadow Credentials

If the relayed identity can modify:

```text
msDS-KeyCredentialLink
```

a downstream path may involve Shadow Credentials.

```text
Coercion
   |
   v
Relay
   |
   v
Directory Write
   |
   v
Key Credential
```

See:

[Active Directory Shadow Credentials](shadow-credentials.md)

---

# Coercion and Machine Account Quota

Some relay chains may combine:

```text
Machine Account Creation
```

with:

```text
RBCD
```

Machine Account Quota can therefore become one supporting primitive.

However:

```text
MAQ > 0
   |
   X
Authentication Coercion Vulnerability
```

These are separate security conditions.

See:

[Active Directory Machine Account Quota](machine-account-quota.md)

---

# Coercion and Directory ACLs

A relayed identity may have useful rights because of an Active Directory ACL.

Examples include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
AddMember
```

Therefore:

```text
Coercion
   |
   v
Relay
   |
   v
ACL Abuse
```

may form a complete attack path.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# Coercion and BloodHound

BloodHound can help model attack paths involving coercion and relay.

Modern BloodHound versions can represent relationships where authentication from a computer can potentially be coerced and relayed under particular conditions.

Exact edge support depends on:

```text
BloodHound Version
Collector Version
Collected Data
Target Configuration
```

Do not assume a graph edge replaces validation.

---

# CoerceAndRelay Relationships

A BloodHound path may conceptually represent:

```text
Authenticated Users
        |
        v
Can Coerce Computer
        |
        v
Computer Authentication
        |
        v
Relay
        |
        v
LDAP / AD CS / Other Target
```

The graph should be treated as:

```text
Attack Path Hypothesis
```

that must be verified against the environment.

---

# BloodHound Workflow

A useful workflow is:

```text
Collect
   |
   v
Identify Coercible Systems
   |
   v
Identify Relay Paths
   |
   v
Review Victim Permissions
   |
   v
Review Target Protections
   |
   v
Controlled Validation
```

See:

[BloodHound](bloodhound.md)

---

# Coercion Target Selection

Do not begin with:

```text
Coerce Every Host
```

Instead identify high-value or representative systems.

Examples:

```text
Test Workstation
Test Member Server
Application Server
Management Server
Domain Controller
Certificate Server
```

Use the least sensitive system capable of demonstrating the condition.

---

# Identify the Victim Context

Before coercion, determine what identity is expected to authenticate.

Possible identities include:

```text
Logged-On User
Computer Account
Service Account
Application Identity
```

This dramatically affects impact.

---

# SYSTEM Context

If a remote operation runs as:

```text
NT AUTHORITY\SYSTEM
```

network authentication normally uses the computer's domain identity when appropriate.

Conceptually:

```text
SYSTEM
   |
   v
Network Authentication
   |
   v
DOMAIN\COMPUTER$
```

---

# NETWORK SERVICE Context

Services running as:

```text
NETWORK SERVICE
```

can also authenticate to remote resources using the machine account in common domain scenarios.

Again, verify actual behaviour.

---

# User Context

Some coercion primitives may cause an operation to execute using:

```text
Logged-On User
```

or another impersonated context.

The resulting authentication could therefore belong to a user rather than the machine.

---

# Service Accounts

Applications running under domain service accounts may generate authentication as:

```text
CORP\svc-application
```

These identities may have significant access to:

```text
Databases
Shares
Servers
Applications
Directory Objects
```

---

# Determine Expected Privilege

Before active testing, answer:

```text
If this identity authenticates, what can it do?
```

This can often be answered through:

```text
BloodHound
Group Membership
Local Administrator Mapping
Directory ACL Analysis
Application Permissions
```

---

# Reachability

A successful coercion primitive is useless if the victim cannot reach the listener.

Assess:

```text
Victim
  |
  v
Outbound Network
  |
  v
Listener
```

Potential controls include:

```text
Host Firewall
Network Firewall
Segmentation
Egress Filtering
SMB Blocking
HTTP Restrictions
```

---

# SMB Egress

Blocking unnecessary outbound:

```text
TCP/445
```

from sensitive servers can significantly reduce SMB-based forced-authentication exposure.

This is particularly valuable for:

```text
Domain Controllers
Certificate Authorities
Management Servers
Application Servers
```

where business requirements permit.

---

# Internet SMB Egress

Organisations should generally prevent internal Windows systems from sending SMB authentication directly to the Internet unless there is an explicit requirement.

A useful boundary is:

```text
Internal Host
     |
     X
Internet TCP/445
```

---

# Internal Segmentation

Internet filtering alone is insufficient.

An attacker may already have:

```text
Internal Network Access
```

Therefore consider:

```text
Workstation -> Server
Server -> Workstation
Server -> Server
Server -> DC
```

communication requirements.

---

# Authentication Coercion Enumeration

A practical assessment can begin with:

```text
1. Identify Windows hosts
2. Identify sensitive roles
3. Enumerate RPC
4. Identify Spooler
5. Identify WebClient
6. Identify SMB reachability
7. Identify NTLM use
8. Identify relay targets
9. Map privileges
10. Validate selectively
```

---

# Windows Service Enumeration

Check Print Spooler:

```powershell
Get-Service Spooler -ErrorAction SilentlyContinue
```

Check WebClient:

```powershell
Get-Service WebClient -ErrorAction SilentlyContinue
```

Check multiple relevant services:

```powershell
Get-Service Spooler,WebClient -ErrorAction SilentlyContinue |
    Select-Object Name,Status,StartType
```

---

# Remote Service Enumeration

With appropriate administrative access:

```powershell
Get-Service -ComputerName SERVER01 -Name Spooler -ErrorAction SilentlyContinue
```

Support for remote service enumeration depends on environment configuration and PowerShell version.

Avoid requiring privileged access merely to enumerate when lower-impact methods are available.

---

# Service Configuration

Inspect locally:

```powershell
Get-CimInstance Win32_Service |
    Where-Object { $_.Name -in @('Spooler','WebClient') } |
    Select-Object Name,State,StartMode,StartName
```

---

# SMB Reachability

From PowerShell:

```powershell
Test-NetConnection SERVER01 -Port 445
```

For RPC endpoint mapper:

```powershell
Test-NetConnection SERVER01 -Port 135
```

These checks demonstrate reachability only.

They do not prove a coercion primitive is available.

---

# Linux Reachability

From Linux:

```bash
nmap -Pn -p 135,445 10.10.10.20
```

For multiple authorised targets:

```bash
nmap -Pn -p 135,445 -iL targets.txt
```

---

# RPC Enumeration with Impacket

```bash
impacket-rpcdump 10.10.10.20
```

For an authenticated query where required, inspect the current help:

```bash
impacket-rpcdump -h
```

Avoid embedding real passwords in shell history.

---

# NetExec

NetExec can help inventory:

```text
Windows Hosts
SMB
Signing
Domain Information
Authentication
```

Example:

```bash
nxc smb 10.10.10.0/24
```

This can help identify systems relevant to subsequent relay analysis.

See:

[NetExec](netexec.md)

---

# Check SMB Signing

The coercion and relay workflow should include:

```text
Coercion Source
```

and separately:

```text
Relay Target
```

A relay target using SMB should be assessed for signing requirements.

Do not assume the coercion victim must also be the relay target.

---

# Coercion Source vs Relay Target

Example:

```text
DC01
 |
 | Coerced Authentication
 v
ATTACKER
 |
 | Relay
 v
FILE01
```

Here:

```text
DC01
```

is the:

```text
Coercion Source
```

and:

```text
FILE01
```

is the:

```text
Relay Target
```

They are different roles.

---

# Coercion Listener vs Relay Target

Similarly:

```text
Assessment Host
```

receives the authentication.

It may then connect to:

```text
Relay Target
```

The architecture is:

```text
Victim
  |
  v
Listener / Relay Host
  |
  v
Target
```

---

# Safe Validation Without Relay

The lowest-impact active test is:

```text
Coercion
   |
   v
Connection to Assessment Host
   |
   v
Stop
```

Evidence can include:

```text
Timestamp
Source IP
Victim Hostname
Expected Security Context
Network Trace
Listener Log
```

No authentication needs to be relayed.

---

# Safe Validation with Relay

If relay validation is required:

```text
One Victim
   |
   v
One Controlled Authentication
   |
   v
One Approved Target
   |
   v
Non-Destructive Authentication
   |
   v
Stop
```

Avoid broad:

```text
MultiRelay
```

testing against production systems.

---

# Coercion Tools Are Not Vulnerabilities

A report should not state:

```text
Server Is Vulnerable to Coercer
```

Instead describe the actual condition:

```text
Remote Authentication Can Be Forced Through the Print Spooler
```

or:

```text
Server Can Be Induced to Authenticate to an Arbitrary SMB Destination
```

or the complete validated path:

```text
Forced Machine Authentication Can Be Relayed to an Unsigned SMB Service
```

---

# Tool Success Is Not Impact

Likewise:

```text
[+] Exploit worked!
```

from a research tool does not automatically mean:

```text
Privilege Escalation
```

The result may only mean:

```text
Authentication Triggered
```

Always determine what happened after the trigger.

---

# Detection

Authentication coercion can produce telemetry across:

```text
RPC
SMB
HTTP
Authentication
Network
Directory
Endpoint
```

No single event universally identifies every coercion method.

---

# Detection Model

A useful model is:

```text
Unusual RPC Request
       |
       v
Sensitive Server
       |
       v
Outbound Authentication
       |
       v
Unexpected Host
       |
       v
Possible Relay Activity
```

---

# Event 4624

A relayed authentication may produce:

```text
4624
```

on the destination.

Useful fields include:

```text
Account Name
Account Domain
Logon Type
Source Network Address
Workstation Name
Authentication Package
```

---

# Detect Machine Authentication from the Wrong Host

One useful relay detection idea is:

```text
Account:
APP01$

Source IP:
10.10.10.50
```

when:

```text
APP01
```

actually uses:

```text
10.10.10.20
```

This discrepancy can indicate that APP01's authentication was relayed through another system.

It is not conclusive by itself.

---

# Event 4776

For NTLM domain credential validation:

```text
4776
```

may provide useful context.

Correlate:

```text
Account
Workstation
Time
Target
```

---

# Event 4768 and 4769

If Kerberos is involved, review:

```text
4768
```

and:

```text
4769
```

for TGT and service-ticket activity.

See:

[Kerberos](kerberos.md)

---

# Network Detection

Network telemetry is particularly useful.

Look for:

```text
Sensitive Server
      |
      v
Unexpected Workstation / Host
```

over:

```text
SMB
HTTP
HTTPS
```

immediately after unusual RPC traffic.

---

# Coercion Timing

A coercion attack may produce a sequence such as:

```text
20:10:01 ATTACKER -> DC01 RPC
20:10:01 DC01 -> ATTACKER SMB
20:10:01 ATTACKER -> TARGET LDAP
```

Correlating these flows can provide strong evidence of coercion and relay.

---

# Print Spooler Detection

Monitor unexpected remote interactions with the Print Spooler on systems where remote printing is unnecessary.

Particularly sensitive systems include:

```text
Domain Controllers
Certificate Authorities
Management Servers
```

---

# EFSRPC Detection

Monitor unusual EFSRPC-related network behaviour when possible.

The useful behavioural pattern is:

```text
Remote RPC Request
      |
      v
Server Initiates Unexpected SMB / HTTP
```

rather than relying solely on a particular PetitPotam signature.

---

# DFS Detection

Likewise, monitor unusual DFS management RPC activity followed by unexpected outbound authentication.

---

# Endpoint Detection

Endpoint telemetry may expose:

```text
Service Activity
RPC Calls
Network Connections
Authentication
Process Context
```

Correlating these can identify coercion even when the tool or method changes.

---

# Detect Relay After Coercion

If coercion is followed by relay, additional events may appear.

For LDAP relay:

```text
5136
```

may show directory changes.

For computer creation:

```text
4741
```

may be relevant.

For group changes:

```text
4728
4732
4756
```

may be relevant depending on group scope.

---

# Detect RBCD Changes

Monitor:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

for unexpected modification.

A chain may look like:

```text
Coercion
   |
   v
Relay
   |
   v
5136
   |
   v
RBCD Attribute Change
```

---

# Detect Shadow Credentials

Monitor changes to:

```text
msDS-KeyCredentialLink
```

on sensitive objects.

Unexpected changes may indicate Shadow Credentials abuse following relay.

---

# Detect AD CS Relay

For certificate-based relay paths, monitor:

```text
Certificate Requests
Requester
Template
Source
Authentication
Certificate Issuance
```

and correlate with preceding forced authentication.

---

# Authentication Coercion Hardening

There is no single:

```text
Disable Authentication Coercion
```

switch.

Defence should address:

```text
Coercion Source
+
Authentication
+
Network Reachability
+
Relay Destination
+
Victim Privilege
```

---

# Hardening Model

```text
Remove Unnecessary Coercion Interfaces
              |
              v
Restrict Network Reachability
              |
              v
Reduce NTLM
              |
              v
Enforce Relay Protections
              |
              v
Reduce Victim Privilege
```

---

# Disable Unnecessary Print Spooler

If a system does not require printing:

```powershell
Stop-Service Spooler
```

and:

```powershell
Set-Service Spooler -StartupType Disabled
```

may be appropriate administrative actions.

!!! warning
    Do not disable production services during a penetration test unless configuration changes are explicitly authorised.

For Domain Controllers and other sensitive servers, review whether the Print Spooler is required at all.

---

# Group Policy for Print Spooler

Organisations can centrally manage printer-related security settings through Group Policy.

A particularly important defensive objective is:

```text
Prevent Unnecessary Remote Print Spooler Access
```

while preserving legitimate printing where required.

See:

[Active Directory Group Policy](group-policy.md)

---

# Restrict RPC

Network controls can restrict unnecessary RPC access to sensitive systems.

Consider:

```text
Who Actually Needs RPC Access?
```

for:

```text
Domain Controllers
Certificate Authorities
Management Servers
Database Servers
```

Do not block required Active Directory traffic without understanding dependencies.

---

# Restrict SMB Egress

Where operationally feasible:

```text
Sensitive Server
      |
      X
Untrusted SMB Destination
```

can prevent many forced SMB authentication paths.

---

# Restrict HTTP Egress

HTTP-based coercion may use WebDAV or other mechanisms.

Sensitive servers should not have unrestricted outbound access merely because:

```text
TCP/80
```

or:

```text
TCP/443
```

is commonly allowed.

Apply destination-aware controls where practical.

---

# Disable WebClient Where Not Required

If WebDAV functionality is unnecessary on a sensitive server, review whether the:

```text
WebClient
```

service should be available.

This can reduce HTTP/WebDAV-based authentication paths.

---

# Reduce NTLM

A major defensive objective is reducing reliance on:

```text
NTLM
```

Use a staged process:

```text
Audit
  |
  v
Identify Dependencies
  |
  v
Remediate
  |
  v
Restrict
```

Do not disable NTLM blindly in production.

---

# Restrict Outgoing NTLM

Windows provides policy controls for restricting outgoing NTLM authentication.

These controls can significantly reduce forced-authentication risk.

Deploy through a staged process:

```text
Audit
  |
  v
Identify Required Destinations
  |
  v
Remediate
  |
  v
Restrict
```

---

# Restrict Incoming NTLM

Services can also be hardened to reduce acceptance of NTLM.

This reduces relay destinations.

Again, inventory dependencies before enforcement.

---

# Require SMB Signing

For SMB relay targets:

```text
Require SMB Signing
```

where appropriate.

See:

[NTLM Relay](ntlm-relay.md)

---

# Require LDAP Signing

Domain Controllers should be hardened according to current Microsoft LDAP signing guidance.

The objective is to prevent insecure LDAP authentication and relay paths.

---

# LDAP Channel Binding

Configure LDAP channel binding according to current Microsoft guidance.

This is especially important for LDAPS authentication.

---

# Extended Protection for Authentication

Enable:

```text
EPA
```

for supported Windows-authenticated HTTP services.

This is particularly important for sensitive services such as certificate enrollment endpoints.

---

# AD CS Hardening

For AD CS:

```text
Use HTTPS
Enable EPA
Review NTLM
Review Web Enrollment
Review Certificate Enrollment Web Services
Review Templates
Review Enrollment Permissions
```

A later AD CS section should cover these controls in detail.

---

# Reduce Computer Account Privilege

A coerced computer account becomes more dangerous when it has broad permissions.

Review:

```text
Computer -> Computer ACLs
Computer -> Group Rights
Computer -> Local Administrator
Computer -> Application Permissions
Computer -> Directory Writes
```

---

# Protect Domain Controller Authentication

Domain Controllers should have particularly restrictive outbound communication.

A useful principle is:

```text
DC
 |
 +--> Required Infrastructure
 |
 X
Untrusted Workstations
```

where operationally feasible.

---

# Network Segmentation

Segmentation can break coercion and relay chains.

Example:

```text
DC01
 |
 X
Assessment / Workstation VLAN TCP/445
```

Even if a coercion primitive exists, the victim cannot authenticate to an unreachable listener.

---

# Host Firewalling

Host-based firewall rules can provide additional protection.

Consider restricting outbound:

```text
SMB
WebDAV
HTTP
```

from sensitive servers to only required destinations.

---

# Administrative Tiering

Privileged accounts should not authenticate unnecessarily to lower-trust systems.

Although computer-account coercion does not depend on interactive administrator activity, tiering still reduces user-authentication coercion and downstream relay impact.

---

# Least Privilege

Relay impact depends on the coerced identity.

Therefore:

```text
Coercible Identity
       +
No Useful Rights
       =
Limited Impact
```

while:

```text
Coercible Identity
       +
Sensitive Rights
       =
High Impact
```

Review the rights assigned to:

```text
Computer Accounts
Service Accounts
Management Servers
Domain Controllers
```

---

# Authentication Coercion and SCCM

Management infrastructure can create particularly sensitive machine-to-machine trust relationships.

For example, Microsoft Configuration Manager environments may include:

```text
Site Servers
SMS Providers
Site Databases
Management Points
Clients
```

Machine accounts associated with these systems can have powerful rights on other site systems.

As a result:

```text
Coercion
   |
   v
Site Server Authentication
   |
   v
Relay
   |
   v
Another Site System
```

can become significantly more impactful than coercion of an ordinary workstation.

Always assess the resulting identity privileges.

---

# Application-Specific Coercion

Do not limit coercion testing to famous RPC techniques.

Applications may perform operations such as:

```text
Fetch File
Import URL
Read UNC Path
Load Configuration
Validate Share
Access Backup Path
Retrieve Template
Query Remote Resource
```

If these operations run under a privileged Windows identity, they may trigger authentication.

---

# Example Application Path

```text
Internal Application
        |
        v
"Import configuration from UNC"
        |
        v
\\ATTACKER\config.xml
        |
        v
Application Service Account Authentication
```

This is conceptually an authentication-coercion condition even if no named exploit is involved.

---

# SQL Server

SQL Server functionality may interact with network resources depending on:

```text
Features
Stored Procedures
Service Account
Permissions
Configuration
```

Any server-side operation that accesses an attacker-controlled UNC path should be reviewed for forced-authentication risk.

---

# Backup Software

Backup products frequently access:

```text
Network Shares
Remote Repositories
UNC Paths
```

under privileged service identities.

A path-injection or configuration weakness could potentially trigger service-account authentication.

---

# Monitoring Software

Monitoring and management systems may similarly:

```text
Fetch Remote Files
Query UNC Paths
Connect to Agents
Load Scripts
```

under powerful identities.

These systems deserve special attention because their service accounts may have broad administrative access.

---

# Reporting Authentication Coercion

A finding should explain:

```text
What Trigger Exists?
Which Identity Authenticates?
Where Can It Authenticate?
Which Protocol Is Used?
Can It Be Relayed?
What Is the Resulting Impact?
```

---

# Finding Titles

Possible titles include:

```text
Remote Authentication Can Be Forced from Domain Controllers
```

```text
Print Spooler Allows Forced Machine Authentication
```

```text
EFSRPC Allows Forced Authentication to Arbitrary Network Hosts
```

```text
Application Functionality Exposes Service Account Authentication
```

```text
Forced NTLM Authentication Can Be Relayed to Internal Services
```

```text
Authentication Coercion and Relay Enable Active Directory Modification
```

Choose the title that matches the validated condition.

---

# Example Finding - Coercion Only

```text
Finding:
Remote Authentication Can Be Forced from APP01

Affected System:
APP01.corp.example

Description:
The affected server exposes a remote Windows service that can be
instructed by an authenticated domain user to access an arbitrary
network path.

During controlled testing, APP01 was instructed to access a resource
hosted on the assessment system.

APP01 subsequently initiated authentication to the assessment host
using its domain computer identity:

CORP\APP01$

No authentication was relayed and no credential material was cracked.

Impact:
An attacker with suitable domain access and network positioning may be
able to cause APP01 to authenticate to an attacker-controlled service.

Depending on protocol configuration elsewhere in the environment, this
authentication could potentially be captured for offline password
guessing or relayed to another service.

The final impact depends on the privileges of APP01$ and the security
controls implemented by potential relay targets.

Recommendation:
Disable unnecessary services capable of triggering outbound
authentication.

Restrict SMB and WebDAV egress from sensitive servers.

Reduce NTLM usage and enforce relay protections such as SMB signing,
LDAP signing, LDAP channel binding, and Extended Protection for
Authentication where applicable.
```

---

# Example Finding - Coercion and Relay

```text
Finding:
Forced Machine Authentication Can Be Relayed to Internal SMB Services

Affected Authentication Source:
APP01.corp.example

Affected Relay Target:
FILE01.corp.example

Description:
APP01 can be remotely induced to initiate NTLM authentication to an
assessment-controlled system.

FILE01 accepts SMB connections without requiring SMB signing.

During controlled validation, a single authentication attempt from the
APP01$ computer account was relayed to FILE01.

No command execution or credential dumping was performed.

Impact:
An attacker able to reach both systems may be able to authenticate to
FILE01 using APP01$ without knowing the computer account password.

The resulting impact depends on the privileges assigned to APP01$ on
FILE01.

Recommendation:
Require SMB signing on FILE01 and other applicable SMB servers.

Restrict unnecessary outbound SMB authentication from APP01.

Review why APP01$ requires access to other systems and remove
unnecessary privileges.

Reduce NTLM usage and remediate the coercion primitive where
operationally possible.
```

---

# Example Finding - High-Impact Chain

```text
Finding:
Authentication Coercion and NTLM Relay Enable Active Directory
Computer Object Modification

Authentication Source:
MGMT01$

Relay Target:
Domain Controller LDAP Service

Description:
MGMT01 can be induced to authenticate to an attacker-controlled
network endpoint.

The resulting NTLM authentication can be relayed to an Active
Directory LDAP service under the tested configuration.

MGMT01$ possesses write permissions over the designated computer
object.

During controlled validation, the assessment confirmed an approved
non-persistent directory modification and immediately reverted it.

Impact:
An attacker with internal network access and suitable domain
credentials could potentially use the MGMT01$ identity to perform
directory operations without obtaining the underlying machine account
password.

Depending on the affected ACL, this could enable additional attack
paths such as resource-based constrained delegation or credential
persistence.

Recommendation:
Remove unnecessary directory permissions from MGMT01$.

Enforce LDAP signing and applicable channel-binding requirements.

Restrict outgoing NTLM authentication from sensitive servers.

Remediate the authentication-coercion primitive and restrict
unnecessary RPC access.
```

---

# Severity

Severity should reflect the complete path.

A useful model is:

```text
Coercion Accessibility
        +
Victim Identity
        +
Authentication Protocol
        +
Relay Feasibility
        +
Victim Privilege
        +
Target Sensitivity
        =
Severity
```

---

# Low-Impact Example

```text
Test Workstation
     |
     v
Forced Authentication
     |
     X
No Relay Target
```

This may primarily represent a hardening issue.

---

# Higher-Impact Example

```text
Management Server
       |
       v
Forced Machine Authentication
       |
       v
NTLM Relay
       |
       v
Server Where Machine Is Admin
```

This may provide lateral movement.

---

# Critical-Path Example

```text
Privileged Server / DC
        |
        v
Forced Authentication
        |
        v
Relay
        |
        v
Sensitive AD / AD CS Service
        |
        v
Reusable Privileged Authentication
```

Depending on the exact result, this may represent a severe domain-level attack path.

---

# Evidence Checklist

Record:

```text
Coercion Target
Coercion Method
Required Privilege
RPC / Service Interface
Victim Identity
Victim IP
Listener IP
Listener Name
Authentication Protocol
Authentication Transport
Timestamp
Relay Target
Relay Protection
Resulting Privilege
Resulting Action
Cleanup
```

---

# Protect Sensitive Evidence

Do not place reusable authentication material in reports or repositories.

Avoid storing:

```text
NetNTLM Captures
NT Hashes
Kerberos Tickets
Certificates
Private Keys
Passwords
```

unless required by the engagement.

If stored temporarily:

```text
Restrict Access
Encrypt
Track
Delete Securely
```

after the engagement.

---

# Authentication Coercion Assessment Checklist

## Preparation

- [ ] Confirm coercion testing is explicitly authorised
- [ ] Confirm relay testing separately
- [ ] Confirm poisoning restrictions
- [ ] Confirm Domain Controller testing restrictions
- [ ] Confirm AD CS testing restrictions
- [ ] Confirm production service restrictions
- [ ] Define test listener
- [ ] Define test identity
- [ ] Define stop conditions
- [ ] Define cleanup procedure

## Discovery

- [ ] Identify Windows hosts
- [ ] Identify Domain Controllers
- [ ] Identify Certificate Authorities
- [ ] Identify management servers
- [ ] Identify application servers
- [ ] Identify database servers
- [ ] Identify sensitive service accounts
- [ ] Identify machine-account privileges

## Network

- [ ] Check TCP/135
- [ ] Check TCP/445
- [ ] Identify RPC reachability
- [ ] Identify dynamic RPC exposure
- [ ] Identify outbound SMB reachability
- [ ] Identify outbound HTTP reachability
- [ ] Identify segmentation
- [ ] Identify host firewall controls

## Services

- [ ] Check Print Spooler
- [ ] Check WebClient
- [ ] Identify EFSRPC availability
- [ ] Identify DFS-related RPC
- [ ] Identify other exposed RPC interfaces
- [ ] Identify application-specific UNC functionality

## Authentication

- [ ] Determine expected security context
- [ ] Determine expected computer account
- [ ] Determine expected service account
- [ ] Determine whether Kerberos is possible
- [ ] Determine whether NTLM fallback is possible
- [ ] Record exact listener name
- [ ] Record exact authentication protocol

## Relay Analysis

- [ ] Identify SMB relay targets
- [ ] Check SMB signing
- [ ] Identify LDAP relay targets
- [ ] Check LDAP signing
- [ ] Check LDAP channel binding
- [ ] Identify HTTP relay targets
- [ ] Check EPA
- [ ] Identify AD CS endpoints
- [ ] Identify MSSQL targets
- [ ] Map victim privileges

## Active Validation

- [ ] Select one representative victim
- [ ] Select one coercion method
- [ ] Use one assessment listener
- [ ] Trigger once
- [ ] Confirm outbound connection
- [ ] Confirm victim identity
- [ ] Stop if coercion evidence is sufficient
- [ ] Relay only if required
- [ ] Use one approved relay target
- [ ] Avoid destructive actions
- [ ] Stop after sufficient evidence

## BloodHound

- [ ] Review machine-account relationships
- [ ] Review local admin relationships
- [ ] Review ACL paths
- [ ] Review RBCD paths
- [ ] Review Shadow Credential paths
- [ ] Review coercion-and-relay edges where collected
- [ ] Validate graph assumptions manually

## Detection

- [ ] Monitor unusual RPC activity
- [ ] Monitor unexpected outbound SMB
- [ ] Monitor unexpected outbound HTTP
- [ ] Review event 4624
- [ ] Review event 4776
- [ ] Review events 4768 and 4769
- [ ] Compare machine account to source IP
- [ ] Correlate coercion and relay timing
- [ ] Monitor event 5136
- [ ] Monitor RBCD changes
- [ ] Monitor KeyCredentialLink changes
- [ ] Monitor certificate issuance

## Hardening

- [ ] Disable unnecessary Print Spooler
- [ ] Restrict remote printing
- [ ] Disable WebClient where unnecessary
- [ ] Restrict RPC exposure
- [ ] Restrict outbound SMB
- [ ] Restrict outbound WebDAV
- [ ] Restrict unnecessary HTTP egress
- [ ] Reduce NTLM
- [ ] Review outgoing NTLM restrictions
- [ ] Require SMB signing
- [ ] Require LDAP signing
- [ ] Configure LDAP channel binding
- [ ] Enable EPA
- [ ] Harden AD CS
- [ ] Reduce machine-account privileges
- [ ] Segment sensitive servers
- [ ] Apply least privilege

## Incident Response

- [ ] Identify coercion source
- [ ] Identify coercion method
- [ ] Identify listener
- [ ] Identify victim identity
- [ ] Determine authentication protocol
- [ ] Identify relay destination
- [ ] Identify resulting operations
- [ ] Review directory modifications
- [ ] Review host modifications
- [ ] Review certificate issuance
- [ ] Review RBCD
- [ ] Review Shadow Credentials
- [ ] Remove persistence
- [ ] Preserve forensic evidence

## Cleanup

- [ ] Stop listener
- [ ] Stop relay services
- [ ] Remove temporary DNS entries
- [ ] Remove test computer objects
- [ ] Revert test ACL changes
- [ ] Revert RBCD
- [ ] Revert KeyCredentialLink
- [ ] Revoke temporary certificates
- [ ] Delete captured authentication material
- [ ] Verify no test persistence remains
- [ ] Record cleanup evidence

---

# Authentication Coercion Testing Model

The basic model is:

```text
Attacker
   |
   v
Trigger
   |
   v
Victim
   |
   v
Outbound Authentication
```

The capture model is:

```text
Coercion
   |
   v
NTLM Authentication
   |
   v
Capture
   |
   v
Offline Password Guessing
```

The relay model is:

```text
Coercion
   |
   v
NTLM Authentication
   |
   v
Relay
   |
   v
Target
```

The computer-account model is:

```text
Remote Service
     |
     v
Runs as SYSTEM
     |
     v
Remote Resource Access
     |
     v
DOMAIN\COMPUTER$
```

The user-context model is:

```text
Application
    |
    v
Runs / Impersonates User
    |
    v
Remote Resource
    |
    v
DOMAIN\User
```

The service-account model is:

```text
Application Service
       |
       v
DOMAIN\svc-app
       |
       v
Remote Resource
       |
       v
Service Account Authentication
```

The RPC model is:

```text
Attacker
   |
   v
RPC Function
   |
   v
Victim Service
   |
   v
Attacker-Controlled UNC
   |
   v
Authentication
```

The PrinterBug model is:

```text
Attacker
   |
   v
Print Spooler RPC
   |
   v
Victim
   |
   v
Notification Destination
   |
   v
Authentication
```

The PetitPotam model is:

```text
Attacker
   |
   v
EFSRPC
   |
   v
Victim
   |
   v
Remote File Path
   |
   v
Authentication
```

The DFSCoerce model is:

```text
Attacker
   |
   v
DFS RPC
   |
   v
Victim
   |
   v
Remote Resource
   |
   v
Authentication
```

The WebDAV model is:

```text
Coercion
   |
   v
WebClient
   |
   v
HTTP / WebDAV
   |
   v
Authentication
```

The protocol-selection model is:

```text
Authentication
      |
      +--> Kerberos
      |
      +--> NTLM
```

The complete NTLM attack path is:

```text
Coercion
   |
   v
Victim NTLM Authentication
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
Impact
```

The AD CS model is:

```text
Coercion
   |
   v
Machine Authentication
   |
   v
NTLM Relay
   |
   v
AD CS Enrollment
   |
   v
Certificate
   |
   v
Authentication
```

The RBCD model is:

```text
Coercion
   |
   v
Relay to LDAP
   |
   v
Computer Object Write
   |
   v
RBCD
   |
   v
S4U
```

The detection model is:

```text
Inbound RPC
    |
    v
Sensitive Server
    |
    v
Immediate Outbound Authentication
    |
    v
Unexpected Destination
    |
    v
Possible Coercion
```

The relay detection model is:

```text
Victim Authentication
        |
        v
Unexpected Source Host
        |
        v
Sensitive Target
        |
        v
Privileged Operation
```

The hardening model is:

```text
Reduce Coercion Interfaces
         +
Restrict Egress
         +
Reduce NTLM
         +
Enforce Relay Protections
         +
Least Privilege
         =
Reduced Risk
```

The most important distinction is:

```text
Authentication Coercion
        |
        X
Credential Compromise
```

A system can be forced to authenticate without exposing its plaintext password.

Another important distinction is:

```text
Authentication Coercion
        |
        X
NTLM Relay
```

Coercion generates authentication.

Relay forwards authentication.

Another important distinction is:

```text
Coercion Successful
       |
       X
Privilege Escalation Successful
```

The victim still requires useful rights on a compatible relay destination.

For penetration testers:

```text
Do Not Ask:
"Can PetitPotam or Coercer trigger this host?"

Ask:
"Which identity can be forced to authenticate,
which protocol will it use, where can that
authentication be relayed, and what can the
identity do there?"
```

For defenders:

```text
Do Not Ask:
"Did we patch PetitPotam?"

Ask:
"Which systems can be forced to authenticate,
where are they permitted to authenticate,
which protocols are available, and which
relay protections prevent that authentication
from becoming useful?"
```

The complete relationship is:

```text
Remote Interface
      |
      v
Service Context
      |
      v
Outbound Authentication
      |
      v
Authentication Protocol
      |
      v
Network Reachability
      |
      v
Relay Protection
      |
      v
Identity Privilege
      |
      v
Impact
```

Authentication coercion should therefore be assessed as an end-to-end identity and network trust problem rather than as a collection of individual exploit names.

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

NTLM:

[NTLM](ntlm.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Relay:

[Kerberos Relay](kerberos-relay.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Machine Account Quota:

[Active Directory Machine Account Quota](machine-account-quota.md)

RBCD:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[Kerberos S4U](s4u.md)

Shadow Credentials:

[Active Directory Shadow Credentials](shadow-credentials.md)

BloodHound:

[BloodHound](bloodhound.md)

Impacket:

[Impacket](impacket.md)

NetExec:

[NetExec](netexec.md)

The next major Active Directory section is:

```text
active-directory/ad-cs/
```

with the Active Directory Certificate Services overview followed by certificate-service enumeration and ESC attack paths.

---

# References

## MITRE ATT&CK - Forced Authentication

[MITRE ATT&CK - T1187 Forced Authentication](https://attack.mitre.org/techniques/T1187/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - NTLM

[Microsoft - NTLM Overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Signing

[Microsoft - SMB Signing](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - LDAP Signing

[Microsoft - LDAP Signing](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - LDAP Channel Binding

[Microsoft - LDAP Channel Binding and LDAP Signing Requirements](https://support.microsoft.com/en-us/topic/2020-2023-and-2024-ldap-channel-binding-and-ldap-signing-requirements-for-windows-kb4520412-ef185fb8-00f7-167d-744c-f299a66fc00a){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Print Spooler

[Microsoft - Print Spooler Service](https://learn.microsoft.com/en-us/windows-server/security/windows-services/security-guidelines-for-disabling-system-services-in-windows-server#print-spooler){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - EFSRPC

[Microsoft - Encrypting File System Remote Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-efsr/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DFS Namespace Management Protocol

[Microsoft - Distributed File System Namespace Management Protocol](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dfsnm/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Restrict NTLM

[Microsoft - Network Security: Restrict NTLM](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/jj852207(v=ws.11)){ target="_blank" rel="noopener noreferrer" }

---

## SpecterOps - Authentication Coercion

[SpecterOps - Authentication Coercion](https://specterops.io/wp-content/uploads/sites/3/2025/04/SPO_NTLM_WhitePaper_Updated.pdf){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound - Coerce and Relay NTLM to LDAP

[BloodHound - CoerceAndRelayNTLMToLDAP](https://bloodhound.specterops.io/resources/edges/coerce-and-relay-ntlm-to-ldap){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## Responder

[Responder](https://github.com/lgandx/Responder){ target="_blank" rel="noopener noreferrer" }

---

## Coercer

[Coercer](https://github.com/p0dalirius/Coercer){ target="_blank" rel="noopener noreferrer" }

---

## PetitPotam

[PetitPotam](https://github.com/topotam/PetitPotam){ target="_blank" rel="noopener noreferrer" }

---

## DFSCoerce

[DFSCoerce](https://github.com/Wh04m1001/DFSCoerce){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Adversary-in-the-Middle

[MITRE ATT&CK - Adversary-in-the-Middle](https://attack.mitre.org/techniques/T1557/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Authentication coercion is best understood as:

```text
Attacker-Controlled Authentication Trigger
```

rather than:

```text
Password Theft
```

The attacker exploits legitimate Windows behaviour:

```text
Service
  |
  v
Access Remote Resource
  |
  v
Authenticate Automatically
```

The resulting authentication becomes dangerous when combined with another weakness.

The complete relationship is:

```text
Coercion Primitive
        |
        v
Victim Identity
        |
        v
Authentication
        |
        v
Relay Opportunity
        |
        v
Target
        |
        v
Victim Privilege
        |
        v
Impact
```

This means that fixing only one named coercion technique does not necessarily remove the overall attack class.

For example:

```text
PetitPotam Mitigated
        |
        X
All Authentication Coercion Eliminated
```

Other:

```text
RPC Interfaces
Applications
Management Platforms
UNC Functions
WebDAV Workflows
```

may still cause outbound authentication.

Likewise:

```text
Print Spooler Disabled
        |
        X
NTLM Relay Eliminated
```

because other authentication sources may remain.

The defensive objective is therefore broader:

```text
Reduce Coercion
     |
     v
Restrict Outbound Authentication
     |
     v
Reduce NTLM
     |
     v
Enforce Relay Protections
     |
     v
Reduce Identity Privilege
```

For penetration testers, the preferred workflow is:

```text
Enumerate
   |
   v
Understand the Primitive
   |
   v
Identify the Victim Identity
   |
   v
Determine the Protocol
   |
   v
Map Relay Targets
   |
   v
Map Privileges
   |
   v
Validate Minimally
   |
   v
Stop
```

rather than:

```text
Run Every Coercion Tool
        |
        v
Against Every Server
        |
        v
Relay Every Authentication
```

The central assessment questions are:

```text
Can this system be forced to authenticate?
```

```text
Which identity authenticates?
```

```text
Which protocol does it use?
```

```text
Where can that authentication go?
```

```text
What can that identity do there?
```

For defenders, the equivalent questions are:

```text
Which systems expose coercion-capable interfaces?

Which systems can send SMB or WebDAV authentication
to untrusted destinations?

Where is NTLM still required?

Which services accept relayable authentication?

Which computer and service accounts have powerful
rights on other systems?

Which protocol protections are enforced?
```

The final model is:

```text
Trigger
  |
  v
Service
  |
  v
Security Context
  |
  v
Authentication
  |
  v
Network Path
  |
  v
Relay Protection
  |
  v
Authorisation
  |
  v
Impact
```

Authentication coercion is therefore not merely an RPC problem.

It is a Windows authentication, network segmentation, service configuration, identity privilege, and protocol-hardening problem.
