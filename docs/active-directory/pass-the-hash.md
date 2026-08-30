# Pass-the-Hash

Pass-the-Hash (PtH) is an authentication technique in which an attacker uses a user's **NT hash** instead of the plaintext password to authenticate to services that support NTLM authentication.

Normally, a user provides a password and Windows derives the NT hash from that password.

With Pass-the-Hash, possession of the NT hash can be sufficient for authentication.

```text
Normal Authentication

Password
   |
   v
NT hash derived
   |
   v
NTLM authentication
   |
   v
Remote Service


Pass-the-Hash

NT hash
   |
   v
NTLM authentication
   |
   v
Remote Service
```

The attacker therefore does not necessarily need to recover the plaintext password.

This makes NT hashes reusable credential material.

!!! warning "Authorised testing only"
    Pass-the-Hash can provide authenticated access to remote Windows systems and may enable lateral movement or privileged administration. Only perform this technique against systems and accounts explicitly included in the assessment scope. Validate the minimum access necessary to demonstrate impact and avoid unnecessary remote execution.

---

# Pass-the-Hash at a Glance

A typical assessment workflow is:

```text
Obtain authorised NT hash
          |
          v
Identify associated account
          |
          v
Determine account scope
          |
          +--> Local account
          |
          +--> Domain account
          |
          v
Identify authorised target
          |
          v
Determine NTLM availability
          |
          v
Authenticate using NT hash
          |
     +----+----+
     |         |
     v         v
   Failed    Success
               |
               v
       Determine privileges
               |
         +-----+-----+
         |           |
         v           v
     Standard      Administrator
       access         access
         |           |
         +-----+-----+
               |
               v
       Minimum validation
               |
               v
       Evidence / Detection
```

---

# The NT Hash

Windows commonly represents password-derived NT credential material using an NT hash.

Conceptually:

```text
Password
   |
   v
UTF-16LE representation
   |
   v
MD4
   |
   v
NT hash
```

A redacted representation might look like:

```text
User:
alice

NT hash:
<32 hexadecimal characters>
```

The actual hash should be treated as a credential.

---

# NT Hash vs Plaintext Password

These are different credential representations:

```text
Plaintext password
        |
        v
Can derive NT hash


NT hash
        |
        X
Does not directly reveal plaintext password
        |
        v
May still authenticate through NTLM
```

This creates an important security principle:

```text
Password secrecy alone
        X
is not sufficient

NT hash secrecy
        =
equally important
```

---

# Why Pass-the-Hash Works

NTLM authentication is challenge-response based.

A simplified flow is:

```text
Client
  |
  | Authentication request
  v
Server
  |
  | Challenge
  v
Client
  |
  | Response calculated
  | using NT hash
  v
Server
  |
  v
Domain Controller / Local SAM
  |
  v
Authentication decision
```

The plaintext password is not necessarily transmitted to the remote service.

The NT hash provides the cryptographic material required to calculate the NTLM response.

Therefore:

```text
Know password
     |
     v
Can authenticate


Know NT hash
     |
     v
May also authenticate
```

This is the basis of Pass-the-Hash.

---

# Pass-the-Hash Is an NTLM Technique

Pass-the-Hash is primarily associated with NTLM authentication.

```text
NT hash
   |
   v
NTLM
   |
   v
Pass-the-Hash
```

It should not be confused with Kerberos ticket-based attacks.

For detailed NTLM coverage, see:

[NTLM](ntlm.md)

---

# Credential Material Distinctions

Several credential types encountered during Active Directory testing look similar but have different uses.

```text
NT hash
   |
   +--> Pass-the-Hash


NetNTLMv2 challenge/response
   |
   +--> Offline password guessing
   +--> Relay when conditions permit
   |
   X
Direct Pass-the-Hash


Kerberos TGT
   |
   +--> Pass-the-Ticket


Kerberos service ticket
   |
   +--> Service authentication


$krb5asrep$
   |
   +--> AS-REP offline password assessment


$krb5tgs$
   |
   +--> Kerberoasting offline password assessment
```

Keeping these credential forms separate prevents incorrect conclusions during an assessment.

---

# NT Hash vs NetNTLMv2

This is one of the most important distinctions.

An NT hash may look conceptually like:

```text
8846f7...
```

NetNTLMv2 challenge-response material may contain:

```text
username
domain
challenge
response
additional protocol data
```

NetNTLMv2 is not the NT hash.

Therefore:

```text
Captured NetNTLMv2
        |
        X
Pass-the-Hash
```

The NetNTLMv2 response would first need to lead to password recovery or be used in an applicable relay scenario.

---

# Pass-the-Hash vs NTLM Relay

These are different techniques.

Pass-the-Hash:

```text
Attacker possesses NT hash
        |
        v
Attacker initiates authentication
        |
        v
Target service
```

NTLM relay:

```text
Victim authenticates
       |
       v
Attacker receives authentication
       |
       v
Attacker forwards authentication
       |
       v
Different service
```

The key distinction is:

```text
Pass-the-Hash
     =
Possession of reusable NT hash


NTLM Relay
     =
Forwarding live authentication
```

---

# Pass-the-Hash vs Password Spraying

Password spraying:

```text
Candidate plaintext password
          |
          v
Multiple accounts
          |
          v
Online authentication
```

Pass-the-Hash:

```text
Known NT hash
      |
      v
Associated account
      |
      v
NTLM authentication
```

Password spraying attempts to discover valid credentials.

Pass-the-Hash starts with reusable credential material already obtained.

---

# Pass-the-Hash vs Kerberoasting

Kerberoasting:

```text
Service ticket
      |
      v
Offline password guessing
      |
      v
Potential plaintext password
```

Pass-the-Hash:

```text
NT hash
   |
   v
Direct NTLM authentication
```

Kerberoasting does not directly produce an NT hash.

---

# Pass-the-Hash vs OverPass-the-Hash

These techniques begin with similar credential material but use it differently.

Pass-the-Hash:

```text
NT hash
   |
   v
NTLM authentication
```

OverPass-the-Hash:

```text
NT hash / suitable key material
          |
          v
Kerberos authentication material
          |
          v
Kerberos authentication
```

Pass-the-Hash remains within the NTLM authentication path.

OverPass-the-Hash crosses into Kerberos.

This distinction will be covered separately in:

```text
active-directory/overpass-the-hash.md
```

---

# Local vs Domain Accounts

Before using an NT hash, determine whether it belongs to:

```text
Local account
```

or:

```text
Domain account
```

This substantially changes where the credential can be used.

---

# Local Account

A local account exists in the target machine's local account database.

Conceptually:

```text
SERVER01
   |
   v
Local SAM
   |
   +--> Administrator
   +--> LocalUser
```

Authentication context might be:

```text
SERVER01\Administrator
```

---

# Domain Account

A domain account exists in Active Directory.

```text
CORP
 |
 +--> alice
 +--> bob
 +--> svc_sql
```

Authentication context might be:

```text
CORP\alice
```

or:

```text
alice@corp.example
```

---

# Local Password Reuse

Local administrator password reuse historically made Pass-the-Hash particularly effective for lateral movement.

Consider:

```text
SERVER01\Administrator
Password A

SERVER02\Administrator
Password A

SERVER03\Administrator
Password A
```

Because the password is identical:

```text
Password A
    |
    v
Same NT hash
```

An NT hash obtained from one host could potentially authenticate to others using the same local credential.

```text
SERVER01
   |
   | Obtain local Administrator NT hash
   v
Hash
   |
   +--> SERVER02
   |
   +--> SERVER03
```

This is one reason unique local administrator passwords are important.

---

# Windows LAPS

Windows LAPS helps address local administrator password reuse by managing unique local administrator passwords.

Conceptually:

```text
Computer A
   |
   +--> Unique local admin password A

Computer B
   |
   +--> Unique local admin password B

Computer C
   |
   +--> Unique local admin password C
```

Therefore:

```text
Hash from Computer A
        |
        X
Should not authenticate
as the same local account
to Computer B
```

when properly configured with unique credentials.

---

# Where NT Hashes May Be Encountered

During an authorised assessment, NT hashes may be obtained from legitimate testing activities involving:

- credential stores
- local SAM databases
- Active Directory database material
- memory credential exposure
- backup material
- secrets extracted from authorised systems
- previously provided test credentials

Possession of the hash should always be treated as equivalent to possession of a reusable credential where NTLM remains available.

---

# Local SAM

Local Windows account password hashes are stored in the Security Account Manager database.

Conceptually:

```text
Windows Host
    |
    v
SAM
    |
    +--> Local users
    |
    +--> NT hashes
```

Accessing SAM credential material generally requires elevated privileges and should only occur where explicitly authorised.

---

# Active Directory Credential Material

Domain account credential material is maintained by Active Directory.

Conceptually:

```text
Domain Controller
      |
      v
NTDS.dit
      |
      +--> Domain users
      +--> Computer accounts
      +--> Credential material
```

Obtaining domain-wide credential material represents a major security impact and should not be performed merely to demonstrate a simple Pass-the-Hash finding.

---

# Credential Acquisition vs Credential Use

Separate these phases:

```text
Credential Access
      |
      v
NT hash obtained
```

from:

```text
Lateral Movement
      |
      v
Pass-the-Hash
```

This is useful both technically and for reporting.

The vulnerability that exposed the hash may be different from the weakness that allows it to be reused remotely.

---

# Common Services

Pass-the-Hash may be relevant to Windows services that support NTLM authentication.

Examples include:

```text
SMB
WMI
WinRM
Remote Service Management
DCOM-related workflows
```

Actual support depends on:

- protocol
- client
- server
- authentication configuration
- account privileges
- NTLM policy
- local security controls

---

# SMB

SMB is one of the most common protocols associated with Pass-the-Hash.

```text
Tester
   |
   v
TCP/445
   |
   v
SMB
   |
   v
NTLM
   |
   v
Target
```

An NT hash can potentially authenticate an account to SMB without knowing the plaintext password.

---

# NetExec

NetExec is commonly used for controlled Pass-the-Hash validation.

General syntax:

```bash
nxc smb <TARGET> \
    -u '<USER>' \
    -H '<NT_HASH>'
```

For a domain account:

```bash
nxc smb 10.10.10.25 \
    -d CORP \
    -u 'alice' \
    -H '<NT_HASH>'
```

---

# Local Authentication with NetExec

For a local account:

```bash
nxc smb 10.10.10.25 \
    --local-auth \
    -u 'Administrator' \
    -H '<NT_HASH>'
```

The distinction between:

```text
Domain authentication
```

and:

```text
Local authentication
```

is critical.

For detailed NetExec usage, see:

[NetExec](netexec.md)

---

# NetExec Result Interpretation

A successful authentication may indicate:

```text
Credential valid
```

while administrative markers may indicate:

```text
Credential valid
        +
Administrative access
```

Do not treat every successful login as administrative compromise.

Conceptually:

```text
Authentication success
       |
       +--> Standard user
       |
       +--> Administrator
```

These represent different levels of impact.

---

# Testing Multiple Hosts

NetExec supports target lists and network ranges.

For example, a file:

```text
targets.txt
```

might contain:

```text
10.10.10.21
10.10.10.22
10.10.10.23
```

Then:

```bash
nxc smb targets.txt \
    -d CORP \
    -u 'alice' \
    -H '<NT_HASH>'
```

However, during an assessment, avoid unnecessarily testing a credential against every system.

Prefer:

```text
Known hash
   |
   v
Identify likely authorised target
   |
   v
Validate credential
   |
   v
Determine privilege
   |
   v
Stop when impact is proven
```

---

# Impacket

Impacket contains several tools that support NTLM hash authentication.

For detailed Impacket usage, see:

[Impacket](impacket.md)

---

# Impacket Hash Format

Many Impacket tools accept hashes using:

```text
LMHASH:NTHASH
```

Modern environments generally do not require a meaningful LM hash.

A common representation therefore uses an empty LM portion:

```text
:<NT_HASH>
```

or the syntax expected by the specific tool.

Always review:

```bash
<tool> -h
```

for the installed Impacket version.

---

# smbclient.py

Impacket's SMB client can authenticate using hashes.

Example:

```bash
impacket-smbclient \
    -hashes ':<NT_HASH>' \
    'CORP/alice@10.10.10.25'
```

This can provide controlled SMB access validation without immediately executing commands.

That makes it useful when the objective is simply:

```text
Does the hash authenticate?
```

---

# psexec.py

Where remote administrative execution is explicitly authorised:

```bash
impacket-psexec \
    -hashes ':<NT_HASH>' \
    'CORP/Administrator@10.10.10.25'
```

Conceptually:

```text
NT hash
   |
   v
SMB authentication
   |
   v
Administrative access
   |
   v
Remote service execution
```

Remote execution creates substantially more impact and telemetry than simple authentication.

Use it only when required.

---

# wmiexec.py

Where authorised:

```bash
impacket-wmiexec \
    -hashes ':<NT_HASH>' \
    'CORP/Administrator@10.10.10.25'
```

This uses WMI-related remote execution mechanisms.

Again:

```text
Authentication validation
       !=
Remote execution requirement
```

Do not execute commands merely because the tool supports them.

---

# atexec.py

Where explicitly authorised:

```bash
impacket-atexec \
    -hashes ':<NT_HASH>' \
    'CORP/Administrator@10.10.10.25'
```

This represents another remote execution path and should be treated as a separate impact stage.

---

# smbexec.py

Where explicitly authorised:

```bash
impacket-smbexec \
    -hashes ':<NT_HASH>' \
    'CORP/Administrator@10.10.10.25'
```

The specific execution method has different operational and detection characteristics.

Select the least invasive technique necessary for the assessment objective.

---

# Authentication Before Execution

A mature workflow is:

```text
Hash obtained
      |
      v
Authenticate only
      |
      v
Success?
   +--+--+
   |     |
  No    Yes
         |
         v
Determine privileges
         |
         v
Is remote execution required
to demonstrate impact?
      +--+--+
      |     |
     No    Yes
      |     |
      v     v
    Stop   Use approved
           minimal method
```

---

# Local Administrator Restrictions

Windows contains protections that can affect remote use of local administrative accounts.

One important concept is **UAC remote restrictions**.

A local administrator authenticating remotely may receive a filtered administrative token depending on:

- account type
- UAC configuration
- registry settings
- built-in Administrator behaviour

Therefore:

```text
Local Administrator membership
          |
          X
Guaranteed unrestricted
remote administration
```

---

# LocalAccountTokenFilterPolicy

A Windows setting commonly encountered in this context is:

```text
LocalAccountTokenFilterPolicy
```

It is located under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
```

This setting affects remote UAC behaviour for local accounts.

Do not change it merely to make Pass-the-Hash work during an assessment.

The environment's existing configuration is part of the security posture being tested.

---

# Built-in Administrator

The built-in local Administrator account can behave differently from other members of the local Administrators group under remote UAC restrictions.

This means:

```text
Administrator
```

and:

```text
AnotherLocalAdmin
```

may produce different remote-access results even when both belong to the local Administrators group.

---

# Domain Administrators

Domain administrative accounts generally have different remote token behaviour from local accounts.

If a domain account is an administrator on the target:

```text
CORP\AdminUser
      |
      v
Target local Administrators group
      |
      v
Potential remote administration
```

Actual access still depends on protocol and system configuration.

---

# Admin$ and Administrative Shares

SMB administrative access often involves shares such as:

```text
ADMIN$
C$
IPC$
```

Successful access to these shares can help establish the privilege level of an authenticated account.

For example:

```bash
impacket-smbclient \
    -hashes ':<NT_HASH>' \
    'CORP/alice@10.10.10.25'
```

Then inspect available shares using the client's supported commands.

Do not modify files unless required by the assessment.

---

# Pass-the-Hash with Local Accounts

Consider:

```text
SERVER01
Local Administrator
NT hash = HASH-A
```

If:

```text
SERVER02
Local Administrator
NT hash = HASH-A
```

then:

```text
HASH-A
  |
  +--> SERVER01
  |
  +--> SERVER02
```

may provide authentication to both.

This demonstrates the importance of unique local administrator passwords.

---

# Pass-the-Hash with Domain Accounts

For a domain account:

```text
CORP\alice
     |
     v
NT hash
     |
     v
Any authorised service
accepting alice through NTLM
```

Potential exposure depends on:

- where the account may log on
- NTLM availability
- service permissions
- administrative rights
- network segmentation

---

# Machine Accounts

Computer accounts also possess credential material.

They normally appear as:

```text
WORKSTATION01$
SERVER01$
DC01$
```

Machine-account authentication and abuse can be relevant to advanced Active Directory attack paths.

Do not automatically treat machine-account hashes as equivalent to ordinary user credentials.

Their permissions and authentication behaviour should be analysed separately.

---

# Lateral Movement

Pass-the-Hash is frequently associated with lateral movement.

Conceptually:

```text
Compromised Host A
        |
        v
Credential material
        |
        v
NT hash
        |
        v
Host B
        |
        v
Administrative access
        |
        v
Potential Host C
```

This can create credential-based propagation through an environment.

---

# Credential Reuse Chain

A dangerous environment may look like:

```text
WS01
 |
 | Local Administrator hash
 v
SRV01
 |
 | Same local Administrator password
 v
SRV02
 |
 | Privileged credential exposed
 v
Domain resources
```

The root problem may include:

```text
Local password reuse
       +
Credential exposure
       +
Excessive privilege
```

Pass-the-Hash is the mechanism that connects these weaknesses.

---

# Do Not Automatically Chain Hosts

During an authorised assessment:

```text
Host A compromised
      |
      v
Hash obtained
      |
      v
Host B accessible
```

does not automatically justify:

```text
Host B
 |
 v
Dump credentials
 |
 v
Host C
 |
 v
Dump credentials
 |
 v
Host D
```

unless lateral movement and credential-access chaining are explicitly required and authorised.

Demonstrate the minimum necessary path.

---

# BloodHound

BloodHound can help determine where an account has administrative or remote-access relationships before attempting authentication.

Conceptually:

```text
NT hash
   |
   v
Associated account
   |
   v
BloodHound
   |
   +--> AdminTo
   +--> CanRDP
   +--> CanPSRemote
   +--> Group membership
   +--> Paths to high-value systems
```

This can reduce unnecessary network authentication.

For detailed BloodHound coverage, see:

[BloodHound](bloodhound.md)

---

# Pass-the-Hash and Kerberos

If Kerberos authentication is available and functioning normally, Windows may prefer Kerberos over NTLM.

Pass-the-Hash specifically depends on an authentication path where the NT hash can be used through NTLM.

Therefore:

```text
NTLM disabled
     |
     v
Traditional Pass-the-Hash
may be prevented
```

However, other techniques involving Kerberos key material may still be relevant.

---

# Hostname vs IP Address

Authentication behaviour can differ depending on whether a service is accessed using:

```text
Hostname
```

or:

```text
IP address
```

For example:

```text
\\server01.corp.example\share
```

may permit Kerberos negotiation where:

```text
\\10.10.10.25\share
```

may result in different authentication behaviour.

This distinction is useful when interpreting NTLM telemetry.

---

# NTLM Restrictions

Windows environments can implement policies restricting NTLM authentication.

Potential controls include policies related to:

```text
Incoming NTLM traffic
Outgoing NTLM traffic
Domain NTLM authentication
NTLM auditing
```

Reducing NTLM usage can directly reduce traditional Pass-the-Hash exposure.

---

# Protected Users

The **Protected Users** security group provides additional authentication protections for sensitive accounts in supported Active Directory environments.

Members receive restrictions intended to reduce exposure to legacy authentication and credential reuse.

However, organisations should understand compatibility implications before moving accounts into the group.

---

# Credential Guard

Windows Defender Credential Guard uses virtualization-based security to help protect credential material.

Conceptually:

```text
Normal process
      |
      X
Direct access to protected
credential secrets
      |
      v
Isolated security environment
```

Credential Guard primarily helps reduce credential theft.

It does not mean that an NT hash obtained through some other authorised source cannot represent risk.

---

# LSASS Protection

Credential protections around LSASS can reduce opportunities for credential theft.

Controls can include:

- Credential Guard
- LSA protection
- attack surface reduction
- EDR
- administrative isolation

These controls address the credential-access stage preceding Pass-the-Hash.

---

# Windows LAPS

Windows LAPS directly addresses one of the most common lateral-movement enablers:

```text
Same local admin password
across multiple computers
```

With unique passwords:

```text
PC01 Administrator -> Password A
PC02 Administrator -> Password B
PC03 Administrator -> Password C
```

therefore:

```text
Hash A
  |
  X
PC02
```

assuming the passwords and resulting hashes differ.

---

# Tiering and Administrative Separation

Credential exposure becomes more dangerous when privileged accounts authenticate to lower-trust systems.

Example:

```text
Domain Admin
    |
    v
Logs onto workstation
    |
    v
Credential material exposed
    |
    v
Workstation compromise
    |
    v
Domain credential compromise
```

Administrative tiering aims to prevent this path.

---

# Detection

Pass-the-Hash often appears as normal NTLM authentication from the protocol's perspective.

This makes detection more challenging than simply looking for a specific "Pass-the-Hash" event.

Defenders should correlate:

```text
Authentication protocol
       +
Source system
       +
Target system
       +
Account
       +
Privilege
       +
Behaviour
```

---

# Event 4624

Event `4624` records successful logons.

Useful fields include:

```text
Account Name
Account Domain
Logon Type
Workstation Name
Source Network Address
Authentication Package
Logon Process
Elevated Token
```

NTLM-authenticated remote logons can be important during Pass-the-Hash investigations.

---

# Logon Types

Relevant logon types may include:

```text
3  - Network
9  - NewCredentials
10 - RemoteInteractive
```

The exact logon type depends on the technique and protocol.

Do not create detection logic that assumes all Pass-the-Hash activity produces one specific logon type.

---

# Authentication Package

Event data may show authentication packages such as:

```text
NTLM
```

This provides useful context.

However:

```text
NTLM authentication
      X
Pass-the-Hash proof
```

NTLM remains legitimate in many environments.

Detection requires behavioural correlation.

---

# Event 4776

Event `4776` records credential validation using NTLM in domain scenarios.

Useful information can include:

```text
Account
Workstation
Status
```

A suspicious pattern might involve:

```text
Previously compromised workstation
        |
        v
NTLM validation
        |
        v
Privileged account
        |
        v
New server
```

---

# Event 4672

Event `4672` indicates that special privileges were assigned to a new logon.

When correlated with:

```text
4624
```

it can help identify successful privileged authentication.

Conceptually:

```text
4624
 |
 v
Successful logon
 |
 v
4672
 |
 v
Special privileges assigned
```

---

# Remote Service Creation

Some Pass-the-Hash workflows use remote service creation.

This may generate events such as:

```text
7045 - A service was installed
```

and depending on auditing:

```text
4697 - A service was installed
```

These events relate to the remote execution technique, not Pass-the-Hash itself.

---

# WMI Detection

WMI-based remote execution can generate additional telemetry from:

- WMI activity
- process creation
- RPC
- network authentication
- endpoint security products

Again:

```text
Pass-the-Hash
       |
       v
Authentication
```

and:

```text
WMI
       |
       v
Execution
```

should be distinguished.

---

# Process Creation

Where remote execution occurs, Event `4688` may provide process-creation telemetry when appropriate auditing is enabled.

Potential chains include:

```text
Network authentication
       |
       v
Remote management
       |
       v
Process creation
```

Correlating these stages can provide stronger detection than authentication events alone.

---

# Detection Strategy

A useful model is:

```text
NTLM authentication
        |
        v
Was source expected?
        |
        v
Was account expected?
        |
        v
Was target expected?
        |
        v
Was privileged access obtained?
        |
        v
Did remote execution follow?
```

---

# Baseline Administrative Paths

Defenders should understand expected administrative relationships.

For example:

```text
Admin Jump Host
      |
      +--> Server01
      +--> Server02
      +--> Server03
```

Unexpected:

```text
User Workstation
      |
      v
Domain Controller
```

may warrant investigation even if authentication itself is technically valid.

---

# Detecting Local Account Reuse

A particularly useful detection scenario is:

```text
Same local account
       |
       +
Multiple systems
       |
       +
Same source
       |
       +
Short time window
```

This can indicate lateral movement using reused local credentials.

---

# Purple Team Validation

Pass-the-Hash can be validated safely using dedicated test accounts and systems.

Example:

```text
PT-Workstation
      |
      v
Controlled local account
      |
      v
Known test NT hash
      |
      v
PT-Server
```

The red team performs one controlled authentication while the blue team validates telemetry.

---

# Purple Team Exercise Flow

```text
Red Team
   |
   | Pass-the-Hash authentication
   v
Target
   |
   | 4624 / NTLM telemetry
   v
SIEM / EDR
   |
   v
Blue Team
   |
   +--> Identify source?
   +--> Identify target?
   +--> Identify account?
   +--> Identify NTLM?
   +--> Identify privilege?
   +--> Detect remote execution?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect
Time to triage
Source identified?
Target identified?
Account identified?
NTLM identified?
Privilege identified?
Remote execution identified?
Technique correctly classified?
```

---

# Hardening

Pass-the-Hash should be addressed using multiple defensive layers.

```text
Pass-the-Hash
      |
      +--> Protect credentials
      |
      +--> Unique local passwords
      |
      +--> Reduce NTLM
      |
      +--> Restrict administration
      |
      +--> Credential Guard
      |
      +--> Least privilege
      |
      +--> Network segmentation
      |
      +--> Authentication monitoring
```

---

# Deploy Windows LAPS

Windows LAPS is one of the most important controls against lateral movement using reused local administrator credentials.

The goal is:

```text
Every managed endpoint
       |
       v
Different local administrator password
```

This breaks the reusable-hash relationship between systems.

---

# Reduce NTLM

Where compatibility permits:

```text
Inventory NTLM
      |
      v
Audit NTLM
      |
      v
Identify dependencies
      |
      v
Migrate applications
      |
      v
Restrict NTLM
```

Do not disable NTLM blindly in production.

Legacy applications may depend on it.

---

# Protect Administrative Credentials

Privileged credentials should not be exposed to ordinary workstations.

Consider:

- privileged access workstations
- administrative tiering
- dedicated admin accounts
- restricted logon rights
- Remote Credential Guard where applicable
- Credential Guard
- LSA protection

---

# Least Privilege

Users should not have unnecessary local administrator access.

Consider:

```text
Domain User
     |
     X
Local Administrator everywhere
```

Reducing local administrative rights limits what a stolen hash can achieve.

---

# Network Segmentation

Restrict management protocols between network segments.

For example:

```text
User VLAN
   |
   X
SMB / WMI / WinRM
   |
   v
Server Management Network
```

Administrative access should originate from controlled management systems where possible.

---

# Restrict Remote Administration

Review access to:

```text
SMB
WinRM
WMI
RDP
RPC
Administrative shares
```

Allow these protocols only where operationally required.

---

# Disable Unused Local Accounts

Unused local administrative accounts increase attack surface.

Review:

```text
Built-in Administrator
Legacy support accounts
Deployment accounts
Vendor accounts
Temporary admin accounts
```

Disable or remove unnecessary identities.

---

# Strong Domain Credential Hygiene

Pass-the-Hash is often part of a larger credential compromise.

Reduce exposure through:

- strong passwords
- MFA where applicable
- credential isolation
- administrative separation
- managed service accounts
- monitoring
- password rotation after compromise

---

# Credential Rotation

If an NT hash has been exposed:

```text
Hash compromised
      |
      v
Credential considered compromised
      |
      v
Rotate password
      |
      v
Invalidate old NT hash
```

Changing the password produces new NT credential material.

The old NT hash should no longer authenticate once the password change has propagated appropriately.

---

# Incident Response

If Pass-the-Hash is suspected:

```text
Identify account
      |
      v
Identify source host
      |
      v
Identify target hosts
      |
      v
Contain compromised systems
      |
      v
Rotate exposed credentials
      |
      v
Investigate credential source
      |
      v
Review lateral movement
```

Do not only reset the account.

Determine how the hash was obtained.

---

# Reporting

Pass-the-Hash may be either:

```text
A demonstrated attack path
```

or:

```text
Evidence of a broader credential-management weakness
```

The finding title should describe the underlying issue.

Possible titles include:

```text
Local Administrator Password Reuse Enables Lateral Movement
```

```text
NTLM Hash Authentication Enables Pass-the-Hash
```

```text
Compromised Administrative NT Hash Permits Remote Server Access
```

```text
Shared Local Administrator Credentials Enable Cross-System Compromise
```

---

# Avoid Overstatement

Do not report:

```text
NTLM enabled
    =
Pass-the-Hash vulnerability
```

NTLM availability creates exposure to hash-based authentication, but meaningful risk depends on:

```text
Can hashes be obtained?
        |
        v
Are credentials reused?
        |
        v
Where can the account authenticate?
        |
        v
What privileges does it have?
```

---

# Example Finding - Local Password Reuse

```text
Finding:
Local Administrator Password Reuse Enables Lateral Movement

Affected Systems:
SERVER01
SERVER02

Validation:
The NT hash for the authorised local Administrator test account was
obtained from SERVER01 during the assessment.

The same NT hash successfully authenticated to SERVER02 using NTLM
without requiring the plaintext password.

Impact:
An attacker who compromises one system and obtains the local
administrator credential material could reuse that credential to
authenticate to other systems configured with the same local
administrator password.

Recommendation:
Deploy Windows LAPS to maintain unique automatically managed local
administrator passwords. Review local administrative accounts and
restrict remote administrative protocols between systems.
```

---

# Example Finding - Domain Account

```text
Finding:
Compromised Domain Account NT Hash Permits Remote Administrative Access

Affected Account:
CORP\adminuser

Affected System:
SERVER01

Validation:
The authorised NT hash for the affected account successfully
authenticated to SERVER01 through SMB using NTLM.

The account was confirmed to possess administrative access.

Impact:
Possession of the NT hash is sufficient to authenticate as the affected
account without knowledge of the plaintext password, potentially enabling
lateral movement to systems where the account has administrative rights.

Recommendation:
Rotate the compromised credential, investigate the source of credential
exposure, reduce unnecessary administrative rights, restrict NTLM where
possible, and strengthen privileged credential isolation.
```

---

# Evidence Collection

Record:

```text
Source of NT hash
Associated account
Local or domain account
Source assessment host
Target host
Authentication protocol
Target service
Authentication result
Administrative access?
Remote execution performed?
Timestamp
Tool
Command
Relevant event IDs
```

Do not expose the complete hash unnecessarily.

---

# Hash Redaction

Instead of:

```text
Administrator:500:<LM_HASH>:<NT_HASH>:::
```

prefer:

```text
Administrator
NT hash: [REDACTED]
```

or:

```text
NT hash:
8846f7**************************
```

depending on reporting requirements.

---

# Evidence Handling

NT hashes are reusable authentication material.

Treat them like passwords.

They should be:

- encrypted at rest
- access controlled
- excluded from public repositories
- removed according to retention requirements
- redacted from screenshots
- protected in assessment reports

---

# Troubleshooting

## STATUS_LOGON_FAILURE

Possible causes include:

```text
Incorrect hash
Incorrect username
Incorrect domain
Account disabled
Authentication restrictions
NTLM restrictions
```

Verify account context first.

---

# Domain vs Local Authentication

A common mistake is attempting:

```text
CORP\Administrator
```

when the credential actually belongs to:

```text
SERVER01\Administrator
```

With NetExec, local authentication can be explicitly selected:

```bash
nxc smb 10.10.10.25 \
    --local-auth \
    -u Administrator \
    -H '<NT_HASH>'
```

---

# Authentication Works but No Admin Access

This means:

```text
Credential valid
      |
      v
Account authenticated
      |
      X
Administrative privilege
```

Do not report remote administrative compromise unless it was actually demonstrated.

---

# Local Admin but Remote Execution Fails

Possible causes include:

- UAC remote restrictions
- service restrictions
- firewall
- endpoint security
- SMB configuration
- RPC restrictions
- WinRM configuration
- administrative share configuration
- remote service controls

Investigate before assuming the hash is invalid.

---

# SMB Unreachable

Check:

```bash
nc -vz 10.10.10.25 445
```

Then review:

```text
Routing
Firewall
VPN
Target availability
SMB configuration
```

---

# NTLM Disabled or Restricted

If the environment blocks NTLM:

```text
NT hash
   |
   v
NTLM authentication attempt
   |
   X
Policy restriction
```

Traditional Pass-the-Hash may not work.

This is a meaningful defensive result.

Do not weaken the target's policy merely to demonstrate the technique.

---

# Common Mistakes

## Mistake 1 - Confusing NT Hash with NetNTLMv2

Remember:

```text
NT hash
   |
   +--> Pass-the-Hash


NetNTLMv2
   |
   +--> Crack
   +--> Relay
```

They are not interchangeable.

---

## Mistake 2 - Calling Pass-the-Hash Password Cracking

Pass-the-Hash does not require recovering the plaintext password.

```text
NT hash
   |
   v
Authentication
```

is the technique.

---

## Mistake 3 - Confusing Pass-the-Hash with NTLM Relay

Pass-the-Hash uses possessed credential material.

Relay forwards someone else's live authentication.

---

## Mistake 4 - Assuming Any Hash Works Everywhere

A hash is associated with an account.

That account must exist or be recognised in the relevant authentication context and have permission to access the target.

---

## Mistake 5 - Ignoring Local vs Domain Accounts

Always determine:

```text
HOST\User
```

versus:

```text
DOMAIN\User
```

before testing.

---

## Mistake 6 - Assuming Successful Authentication Means Admin

Maintain:

```text
Authenticated
     !=
Administrator
```

---

## Mistake 7 - Executing Commands Immediately

Authentication alone may provide sufficient evidence.

Do not escalate automatically to remote command execution.

---

## Mistake 8 - Testing Every Host

Use BloodHound, directory information, and known administrative relationships to target validation.

Avoid unnecessary authentication noise.

---

## Mistake 9 - Publishing Hashes

An NT hash is reusable credential material.

Never place a real hash in public documentation.

---

## Mistake 10 - Recommending Only Password Changes

If the root cause is local administrator password reuse:

```text
Changing all hosts to
another identical password
```

does not solve the underlying issue.

Use unique credentials such as those managed by Windows LAPS.

---

# Assessment Checklist

## Preparation

- [ ] Confirm Pass-the-Hash testing is authorised
- [ ] Confirm permitted target systems
- [ ] Confirm permitted accounts
- [ ] Determine whether remote execution is authorised
- [ ] Establish evidence-handling requirements
- [ ] Identify stop conditions

## Credential Analysis

- [ ] Confirm material is an NT hash
- [ ] Do not confuse with NetNTLMv2
- [ ] Identify associated username
- [ ] Determine local vs domain account
- [ ] Determine source of credential exposure
- [ ] Protect hash securely

## Target Analysis

- [ ] Identify likely authorised targets
- [ ] Review BloodHound relationships
- [ ] Determine SMB availability
- [ ] Determine WinRM/WMI availability where relevant
- [ ] Determine NTLM restrictions
- [ ] Avoid unnecessary host-wide spraying

## Authentication

- [ ] Attempt minimum required authentication
- [ ] Record target
- [ ] Record source
- [ ] Record account
- [ ] Record protocol
- [ ] Record timestamp
- [ ] Record success/failure

## Privilege

- [ ] Distinguish authentication from administration
- [ ] Determine local administrator status
- [ ] Determine domain privileges
- [ ] Determine remote management rights
- [ ] Review BloodHound attack paths

## Execution

- [ ] Perform remote execution only if required
- [ ] Select least invasive technique
- [ ] Avoid unnecessary file modifications
- [ ] Record execution method
- [ ] Clean up assessment artefacts

## Detection

- [ ] Review Event 4624
- [ ] Review Event 4776
- [ ] Review Event 4672
- [ ] Review remote service events where applicable
- [ ] Review process creation where applicable
- [ ] Correlate source, account and target
- [ ] Review unusual NTLM usage

## Remediation

- [ ] Rotate compromised credentials
- [ ] Deploy Windows LAPS
- [ ] Eliminate local password reuse
- [ ] Reduce NTLM dependencies
- [ ] Restrict remote administration
- [ ] Reduce excessive privileges
- [ ] Protect privileged credentials
- [ ] Review administrative tiering
- [ ] Deploy credential protections where appropriate

---

# Pass-the-Hash Testing Model

A useful mental model is:

```text
                      Credential Material
                              |
                              v
                           NT Hash
                              |
                    +---------+---------+
                    |                   |
                    v                   v
               Local Account       Domain Account
                    |                   |
                    v                   v
             Local SAM context     Active Directory
                    |                   |
                    +---------+---------+
                              |
                              v
                       NTLM Authentication
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                  Failed             Success
                                        |
                                        v
                               Determine privilege
                                        |
                              +---------+---------+
                              |                   |
                              v                   v
                          Standard            Administrator
                           access                access
                              |                   |
                              +---------+---------+
                                        |
                                        v
                               Minimum validation
                                        |
                                        v
                                  Detection
                                        |
                                        v
                                  Remediation
```

The broader lateral-movement model is:

```text
Credential Exposure
        |
        v
NT Hash Obtained
        |
        v
Credential Reuse?
     +--+--+
     |     |
    No    Yes
     |     |
     v     v
 Limited   Additional hosts
 impact        |
               v
        Administrative access?
             +--+--+
             |     |
            No    Yes
             |     |
             v     v
          Limited  Lateral movement
          access       |
                       v
                Further credential
                    exposure
```

The defensive model is:

```text
Pass-the-Hash
      |
      +--> Prevent hash theft
      |       |
      |       +--> Credential Guard
      |       +--> LSA protection
      |       +--> EDR
      |       +--> Admin isolation
      |
      +--> Prevent reuse
      |       |
      |       +--> Windows LAPS
      |       +--> Unique passwords
      |
      +--> Restrict authentication
      |       |
      |       +--> Reduce NTLM
      |       +--> Network segmentation
      |       +--> Management restrictions
      |
      +--> Limit impact
      |       |
      |       +--> Least privilege
      |       +--> Administrative tiering
      |
      +--> Detect
              |
              +--> 4624
              +--> 4776
              +--> 4672
              +--> Remote execution telemetry
```

The assessment should answer:

```text
How was the NT hash exposed?
        |
        v
Which account does it represent?
        |
        v
Is it local or domain-based?
        |
        v
Where can the account authenticate?
        |
        v
Does NTLM accept the hash?
        |
        v
What privileges does the account have?
        |
        v
Is the credential reused?
        |
        v
Can the hash enable lateral movement?
        |
        v
Can defenders detect the authentication?
        |
        v
Which control breaks the attack path?
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

NTLM:

[NTLM](ntlm.md)

Kerberos:

[Kerberos](kerberos.md)

Password spraying:

[Password Spraying](password-spraying.md)

AS-REP Roasting:

[AS-REP Roasting](asrep-roasting.md)

Kerberoasting:

[Kerberoasting](kerberoasting.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

BloodHound:

[BloodHound](bloodhound.md)

The following topics complement Pass-the-Hash and can be linked once their dedicated notes are available:

```text
active-directory/overpass-the-hash.md
active-directory/pass-the-key.md
active-directory/ntlm-relay.md
active-directory/lateral-movement.md
active-directory/smb.md
active-directory/winrm.md
active-directory/wmi.md
active-directory/laps.md
```

---

# References

## Microsoft

[Microsoft - NTLM overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Windows authentication overview](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/windows-authentication-overview){ target="_blank" rel="noopener noreferrer" }

[Microsoft - NTLM blocking and auditing](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/jj865668(v=ws.11)){ target="_blank" rel="noopener noreferrer" }

[Microsoft - User Account Control and remote restrictions](https://learn.microsoft.com/en-us/troubleshoot/windows-server/windows-security/user-account-control-and-remote-restriction){ target="_blank" rel="noopener noreferrer" }

---

## Windows LAPS

[Microsoft - Windows LAPS overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## Credential Guard

[Microsoft - Windows Defender Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

---

## Protected Users

[Microsoft - Protected Users security group](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Use Alternate Authentication Material: Pass the Hash](https://attack.mitre.org/techniques/T1550/002/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

[NetExec SMB Protocol](https://www.netexec.wiki/smb-protocol){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Pass-the-Hash demonstrates why an NT hash must be treated as reusable authentication material rather than merely as a password verifier.

The critical distinctions are:

```text
NT hash != NetNTLMv2

Pass-the-Hash != NTLM relay

Pass-the-Hash != Password cracking

Pass-the-Hash != Kerberoasting

Authentication success != Administrator

Credential access != Lateral movement
```

The fundamental attack path is:

```text
Credential exposure
      |
      v
NT hash obtained
      |
      v
Identify account
      |
      v
Identify authorised target
      |
      v
NTLM authentication
      |
      v
Hash accepted
      |
      v
Account access
      |
      v
Privilege analysis
      |
      v
Potential lateral movement
```

The most effective defence breaks this chain at several points:

```text
Protect credential material
        +
Use unique local passwords
        +
Reduce NTLM
        +
Restrict administrative paths
        +
Apply least privilege
        +
Segment management protocols
        +
Monitor authentication
```

A mature Pass-the-Hash assessment should therefore determine not merely whether a hash can authenticate, but how the hash became exposed, whether the credential is reused, where the associated account has access, what privileges that access provides, whether defenders can identify the authentication path, and which control most effectively prevents the credential from enabling further compromise.
