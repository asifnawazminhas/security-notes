# Active Directory SMB - Enumeration, Authentication and Lateral Movement

Server Message Block (SMB) is one of the most important protocols encountered during Windows and Active Directory security assessments.

SMB is used for:

```text
File Sharing
Printer Sharing
Named Pipes
Remote Administration
Administrative Shares
Group Policy Distribution
SYSVOL
NETLOGON
Service Management
Remote Registry
RPC Transport
```

In Active Directory environments, SMB is especially important because it frequently provides the connection between:

```text
Identity
   |
   v
Authentication
   |
   v
Remote Windows Host
   |
   v
Files / Shares / Administration
```

SMB can therefore appear during:

```text
Enumeration
Credential Validation
Share Discovery
Sensitive File Discovery
Lateral Movement
Remote Administration
NTLM Relay
Authentication Coercion
Domain Controller Enumeration
```

!!! warning "Authorised testing only"
    SMB authentication and remote administration can generate significant security telemetry and may affect production systems. Only test hosts and credentials included in the assessment scope. Prefer read-only enumeration before attempting file writes or remote execution.

---

# SMB at a Glance

The basic model is:

```text
Client
  |
  v
TCP 445
  |
  v
SMB Server
  |
  +--> Authentication
  |
  +--> Shares
  |
  +--> Files
  |
  +--> Named Pipes
  |
  +--> Remote Administration
```

In an Active Directory environment:

```text
Domain Account
      |
      v
Kerberos / NTLM
      |
      v
SMB
      |
      v
Windows Host
```

---

# SMB Ports

Modern SMB primarily uses:

```text
TCP 445
```

Older environments may also expose:

```text
TCP 139
```

which is associated with SMB over NetBIOS.

During modern Active Directory assessments, the primary port is normally:

```text
445/TCP
```

---

# Check SMB Connectivity

From Windows:

```powershell
Test-NetConnection srv01.corp.example -Port 445
```

Example:

```text
ComputerName     : srv01.corp.example
RemoteAddress    : 10.10.10.25
RemotePort       : 445
TcpTestSucceeded : True
```

From Linux:

```bash
nmap -Pn -p445 srv01.corp.example
```

For a defined subnet:

```bash
nmap -Pn -p445 10.10.10.0/24
```

---

# SMB Versions

The major SMB generations are:

```text
SMBv1
SMBv2
SMBv3
```

SMBv1 is obsolete and should generally be disabled.

Modern Windows environments should use:

```text
SMBv2
SMBv3
```

---

# Why SMBv1 Matters

SMBv1 lacks many protections available in later SMB versions and has historically been associated with serious security weaknesses.

During an assessment, the important question is usually:

```text
Is SMBv1 Enabled?
```

rather than:

```text
Can I exploit SMBv1?
```

---

# Check SMBv1 on Windows

On a Windows server:

```powershell
Get-SmbServerConfiguration |
    Select-Object EnableSMB1Protocol,EnableSMB2Protocol
```

Example:

```text
EnableSMB1Protocol EnableSMB2Protocol
------------------ ------------------
False              True
```

---

# Check SMB Client Configuration

```powershell
Get-SmbClientConfiguration
```

Useful properties include:

```text
EnableSecuritySignature
RequireSecuritySignature
EnableInsecureGuestLogons
```

---

# Check SMB Server Configuration

```powershell
Get-SmbServerConfiguration
```

Useful properties include:

```text
EnableSMB1Protocol
EnableSMB2Protocol
EnableSecuritySignature
RequireSecuritySignature
EncryptData
RejectUnencryptedAccess
EnableAuthenticateUserSharing
```

Exact properties can vary by Windows version.

---

# SMB Authentication

SMB commonly uses:

```text
Kerberos
```

or:

```text
NTLM
```

in Active Directory environments.

Conceptually:

```text
SMB Client
    |
    v
Authentication
    |
    +--> Kerberos
    |
    +--> NTLM
    |
    v
SMB Server
```

---

# Kerberos Authentication

When the client accesses a domain host by its hostname and Kerberos requirements are satisfied:

```text
Client
  |
  v
KDC
  |
  v
CIFS Service Ticket
  |
  v
SMB Server
```

The service principal typically resembles:

```text
cifs/srv01.corp.example
```

---

# SMB and SPNs

Kerberos authentication to SMB normally uses the:

```text
CIFS
```

service class.

Example:

```text
cifs/fileserver.corp.example
```

You can inspect Kerberos tickets on Windows:

```cmd
klist
```

Look for:

```text
cifs/
```

service tickets.

---

# Hostnames vs IP Addresses

When Kerberos is expected, prefer:

```text
\\srv01.corp.example\share
```

rather than:

```text
\\10.10.10.25\share
```

Using an IP address may prevent normal SPN matching and can result in NTLM authentication or authentication failure.

---

# NTLM Authentication

When Kerberos cannot be used, SMB may fall back to NTLM if NTLM is permitted.

Conceptually:

```text
Client
  |
  v
NTLM Challenge / Response
  |
  v
SMB Server
```

This becomes important for:

```text
Pass-the-Hash
NTLM Relay
Credential Exposure
Legacy Authentication
```

---

# Identify Authentication Protocol

Do not assume that successful SMB authentication means Kerberos was used.

Determine whether the session used:

```text
Kerberos
```

or:

```text
NTLM
```

using:

```text
Windows Event Logs
Kerberos Ticket Cache
NTLM Operational Logs
Network Telemetry
```

---

# SMB Signing

SMB signing protects the integrity of SMB messages.

Conceptually:

```text
SMB Message
    |
    v
Cryptographic Signature
    |
    v
Receiver Verifies Signature
```

This helps prevent an attacker from modifying or relaying SMB authentication in certain scenarios.

---

# SMB Signing States

A system can broadly be considered:

```text
Signing Supported
```

and:

```text
Signing Required
```

These are not the same thing.

The important security question for relay resistance is usually:

```text
Is SMB Signing Required?
```

---

# Why SMB Signing Matters

Without required SMB signing:

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
Relay
  |
  v
SMB Target
```

may become possible if the other relay requirements are satisfied.

With signing required:

```text
Victim
  |
  v
Attacker
  |
  X
  |
  v
SMB Target
```

the classic SMB relay path is substantially restricted because the attacker cannot produce the required message signatures without the appropriate session key.

See:

[NTLM Relay](ntlm-relay.md)

---

# Check SMB Signing with PowerShell

Server configuration:

```powershell
Get-SmbServerConfiguration |
    Select-Object EnableSecuritySignature,RequireSecuritySignature
```

Client configuration:

```powershell
Get-SmbClientConfiguration |
    Select-Object EnableSecuritySignature,RequireSecuritySignature
```

---

# SMB Signing with NetExec

NetExec can help identify SMB hosts and their signing configuration.

Check your installed version:

```bash
nxc --version
```

SMB help:

```bash
nxc smb -h
```

Basic discovery:

```bash
nxc smb 10.10.10.0/24
```

Example conceptual output:

```text
SMB  10.10.10.10  445  DC01   Windows Server
SMB  10.10.10.20  445  SRV01  Windows Server
SMB  10.10.10.30  445  WS01   Windows
```

Depending on the NetExec version, output may also show:

```text
signing
SMB version
domain
hostname
```

---

# NetExec SMB Signing Enumeration

NetExec provides SMB modules and options that can help identify systems where signing is not required.

Because command options can change between releases, first use:

```bash
nxc smb -h
```

Do not rely on an old CrackMapExec command without confirming that the equivalent exists in the installed NetExec release.

---

# Nmap SMB Security Modes

Nmap SMB scripts can provide additional protocol information.

For example:

```bash
nmap -Pn -p445 --script smb2-security-mode srv01.corp.example
```

This can help determine SMB signing behaviour.

---

# SMB Dialect Enumeration

Nmap:

```bash
nmap -Pn -p445 --script smb-protocols srv01.corp.example
```

This can help identify supported SMB dialects.

---

# SMB Encryption

SMB 3 supports encryption.

Conceptually:

```text
SMB Data
   |
   v
Encryption
   |
   v
Network
```

SMB encryption protects SMB data confidentiality in transit.

---

# Signing vs Encryption

Do not confuse:

```text
SMB Signing
```

with:

```text
SMB Encryption
```

Signing primarily provides:

```text
Integrity
Authentication Protection
```

Encryption provides:

```text
Confidentiality
```

Modern SMB configurations can use both.

---

# SMB Share Enumeration

One of the first authenticated SMB activities should normally be:

```text
Enumerate Shares
```

rather than:

```text
Remote Execution
```

---

# Windows Share Enumeration

Local system:

```powershell
Get-SmbShare
```

Traditional command:

```cmd
net share
```

---

# Remote Share Enumeration

From Windows:

```cmd
net view \\srv01.corp.example
```

Depending on permissions and system configuration, this may list accessible shares.

---

# NetExec Share Enumeration

```bash
nxc smb srv01.corp.example -u 'audit-user' -p 'PASSWORD' --shares
```

Example conceptual result:

```text
Share        Permissions
-----        -----------
IPC$         READ
Shared       READ
Projects     READ,WRITE
```

---

# smbclient

List available shares:

```bash
smbclient -L //srv01.corp.example -U 'CORP/audit-user'
```

The password can be entered interactively.

This is preferable to placing production passwords directly in shell history.

---

# Connect to a Share

```bash
smbclient //srv01.corp.example/Shared -U 'CORP/audit-user'
```

Useful commands inside smbclient include:

```text
ls
cd
pwd
get
```

Only upload or modify files when explicitly required.

---

# Anonymous SMB Access

Some SMB servers may permit:

```text
Anonymous
```

or:

```text
Guest
```

access.

Test carefully:

```bash
smbclient -L //srv01.corp.example -N
```

`-N` means:

```text
No Password
```

---

# Null Sessions

Historically, Windows systems sometimes exposed significant information through:

```text
Null Sessions
```

Modern Windows environments are generally more restrictive.

However, third-party SMB implementations, appliances and legacy systems may still expose anonymous information.

---

# Anonymous Access Is Not Automatically a Vulnerability

If anonymous access exists, determine:

```text
What Is Actually Accessible?
```

For example:

```text
Public Software Share
```

may intentionally allow read access.

Whereas:

```text
HR Documents
Credentials
Backups
Configuration Files
```

would represent a much more serious issue.

---

# Common SMB Shares

Typical shares include:

```text
IPC$
ADMIN$
C$
NETLOGON
SYSVOL
Shared
Users
Software
Backups
Projects
```

---

# IPC$

```text
IPC$
```

is used for inter-process communication and named pipes.

It is frequently involved in:

```text
RPC
Remote Administration
Authentication
Enumeration
```

---

# ADMIN$

```text
ADMIN$
```

normally maps to the Windows directory.

Typically:

```text
C:\Windows
```

Access generally requires administrative privileges.

---

# C$

```text
C$
```

is the administrative share for the system drive.

Access generally indicates significant local administrative rights.

---

# Administrative Share Model

```text
Administrative Credential
        |
        v
SMB
        |
        +--> ADMIN$
        |
        +--> C$
```

This can provide:

```text
File Access
File Write
Remote Administration Support
```

---

# NETLOGON

Domain controllers commonly expose:

```text
NETLOGON
```

The share contains scripts and files associated with domain logon processes.

Example:

```text
\\dc01.corp.example\NETLOGON
```

---

# SYSVOL

Domain controllers expose:

```text
SYSVOL
```

which contains:

```text
Group Policy
Logon Scripts
Domain-Wide Configuration
```

Example:

```text
\\dc01.corp.example\SYSVOL
```

---

# SYSVOL Security Review

During an authorised assessment, inspect SYSVOL for:

```text
Scripts
Configuration Files
Hardcoded Credentials
Legacy Passwords
Deployment Commands
Mapped Drive Scripts
Software Installation Parameters
```

---

# GPP Passwords

Historically, Group Policy Preferences could expose encrypted passwords through:

```text
cpassword
```

values in SYSVOL.

See:

`GPP Passwords`

---

# Search SYSVOL

Using smbclient:

```bash
smbclient //dc01.corp.example/SYSVOL -U 'CORP/audit-user'
```

Navigate read-only and inspect relevant files.

---

# NetExec SYSVOL Review

NetExec functionality changes between releases.

Inspect available modules:

```bash
nxc smb -L
```

and SMB options:

```bash
nxc smb -h
```

Use only modules relevant to the authorised assessment.

---

# Sensitive Files in SMB Shares

Common high-value file types include:

```text
.ps1
.bat
.cmd
.vbs
.xml
.ini
.config
.conf
.txt
.csv
.xlsx
.docx
.kdbx
.rdp
.ppk
.pem
.key
.pfx
.p12
```

The presence of these files is not itself a vulnerability.

Review:

```text
Content
Permissions
Business Need
Sensitivity
```

---

# Common Credential Indicators

Search authorised copies or accessible shares for terms such as:

```text
password
passwd
pwd
credential
secret
token
apikey
api_key
connectionstring
username
user=
pass=
```

Avoid downloading large volumes of unrelated user data.

---

# Share Permissions

SMB access is controlled by multiple permission layers.

Conceptually:

```text
User
 |
 v
Share Permissions
 |
 v
NTFS Permissions
 |
 v
Effective Access
```

Both must be considered.

---

# Share Permissions vs NTFS Permissions

A user may have:

```text
Share = Full Control
```

but:

```text
NTFS = Read
```

Result:

```text
Read
```

Similarly:

```text
Share = Read
NTFS = Full Control
```

still results in:

```text
Read
```

for network access.

The effective access is constrained by both layers.

---

# Enumerate Local SMB Shares

PowerShell:

```powershell
Get-SmbShare |
    Select-Object Name,Path,Description
```

---

# Review Share Access

```powershell
Get-SmbShareAccess -Name Shared
```

Example:

```text
Name    ScopeName AccountName       AccessControlType AccessRight
----    --------- -----------       ----------------- -----------
Shared  *         CORP\Domain Users Allow             Read
```

---

# Review NTFS ACL

```powershell
Get-Acl 'D:\Shared' |
    Format-List
```

More focused:

```powershell
(Get-Acl 'D:\Shared').Access |
    Select-Object IdentityReference,FileSystemRights,AccessControlType,IsInherited
```

---

# Writable Shares

Writable shares are important because they may allow:

```text
File Modification
Script Replacement
Configuration Modification
Software Replacement
Data Tampering
```

But:

```text
Writable Share
```

does not automatically mean:

```text
Remote Code Execution
```

The security impact depends on how files in the share are consumed.

---

# Safe Write Testing

If write permission must be validated, use an approved temporary file.

Example from an authorised Windows client:

```powershell
$path = '\\srv01.corp.example\Shared\write-test.txt'

'Authorised security test' | Set-Content -LiteralPath $path

Test-Path -LiteralPath $path

Remove-Item -LiteralPath $path
```

Record:

```text
Creation
Verification
Cleanup
```

Do not overwrite an existing file.

---

# Safe smbclient Write Test

If explicitly authorised:

```text
put
```

can upload a temporary test file.

Use a uniquely named harmless file and remove it immediately after validation.

---

# Dangerous Writable Share Patterns

Writable shares become especially important when they contain:

```text
Logon Scripts
Deployment Scripts
Application Binaries
Scheduled Task Scripts
Service Executables
Configuration Files
Web Content
Software Packages
Administrative Tools
```

---

# Example Attack Path

```text
Domain User
    |
    v
Write Access
    |
    v
Deployment Share
    |
    v
Script Executed by Administrators
```

The real vulnerability is:

```text
Untrusted User Can Modify
Privileged Execution Content
```

not simply:

```text
SMB Share Is Writable
```

---

# Named Pipes

SMB transports many Windows named pipes.

Examples can include:

```text
svcctl
samr
lsarpc
netlogon
spoolss
```

Named pipes are used by Windows RPC services and remote administration mechanisms.

---

# Named Pipe Model

```text
SMB
 |
 v
IPC$
 |
 v
Named Pipe
 |
 v
RPC Service
```

This relationship explains why SMB appears in many Windows remote-management techniques.

---

# Service Control Manager

The Service Control Manager can be remotely accessed through RPC.

Conceptually:

```text
SMB / RPC
    |
    v
svcctl
    |
    v
Service Control Manager
```

Administrative access can enable:

```text
Service Enumeration
Service Management
Remote Service Creation
```

---

# PsExec

PsExec-style lateral movement commonly uses:

```text
SMB
+
Administrative Share
+
Service Control Manager
```

Conceptually:

```text
Attacker
   |
   v
SMB
   |
   v
ADMIN$
   |
   v
Upload Component
   |
   v
SCM
   |
   v
Temporary Service
   |
   v
Execution
```

---

# Impacket PsExec

Check syntax:

```bash
impacket-psexec -h
```

Authorised example:

```bash
impacket-psexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

Prefer password prompting or another secure credential-handling method where supported.

---

# PsExec with NTLM Hash

Where pass-the-hash testing is explicitly authorised:

```bash
impacket-psexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

See:

[Pass-the-Hash](pass-the-hash.md)

---

# PsExec Is Intrusive

PsExec-style execution can create:

```text
Temporary Executable
Temporary Service
Service Events
File Events
Process Events
SMB Events
```

Do not use it simply because:

```text
Pwn3d!
```

appears in NetExec output.

---

# SMBExec

Impacket also provides:

```text
smbexec
```

Check syntax:

```bash
impacket-smbexec -h
```

Example:

```bash
impacket-smbexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

Hash authentication:

```bash
impacket-smbexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

---

# PsExec vs SMBExec

Conceptually:

```text
PsExec
  |
  +--> SMB
  +--> File Transfer
  +--> Service Creation
```

while:

```text
SMBExec
  |
  +--> SMB
  +--> Service Control
  +--> Command Execution
```

Exact implementation and artifacts depend on the tool version.

---

# ATExec

Impacket:

```bash
impacket-atexec -h
```

Example:

```bash
impacket-atexec 'CORP/audit-admin:PASSWORD@srv01.corp.example' 'whoami'
```

ATExec uses Task Scheduler mechanisms rather than the same service workflow as PsExec.

---

# WMIExec

Although WMIExec is primarily a WMI/DCOM technique, SMB may still be involved in retrieving command output depending on tool behaviour.

Check:

```bash
impacket-wmiexec -h
```

Example:

```bash
impacket-wmiexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

---

# NetExec Credential Validation

Password:

```bash
nxc smb srv01.corp.example -u 'audit-user' -p 'PASSWORD'
```

Hash:

```bash
nxc smb srv01.corp.example -u 'audit-admin' -H 'NTHASH'
```

---

# Target Lists

Prefer:

```bash
nxc smb targets.txt -u 'audit-user' -p 'PASSWORD'
```

over unnecessarily scanning:

```text
Entire Corporate Network
```

---

# Local Accounts

When validating a local account rather than a domain identity, inspect the current NetExec options:

```bash
nxc smb -h
```

Typical versions support:

```text
--local-auth
```

Example:

```bash
nxc smb srv01.corp.example -u 'Administrator' -p 'PASSWORD' --local-auth
```

---

# Domain vs Local Authentication

Domain account:

```text
CORP\audit-user
```

Local account:

```text
SRV01\Administrator
```

Always document which security authority owns the account.

---

# Pass-the-Hash

SMB is one of the classic protocols associated with:

```text
Pass-the-Hash
```

Conceptually:

```text
NTLM Hash
    |
    v
NTLM Authentication
    |
    v
SMB
```

The plaintext password is not required.

See:

[Pass-the-Hash](pass-the-hash.md)

---

# Local Administrator Password Reuse

Suppose:

```text
WS01\Administrator
```

and:

```text
WS02\Administrator
```

use the same password.

Their NTLM hashes will also match.

This creates:

```text
Compromise WS01
      |
      v
Local Admin Hash
      |
      v
Authenticate to WS02
      |
      v
Lateral Movement
```

---

# Windows LAPS

Windows LAPS mitigates this problem by maintaining unique local administrator passwords.

See:

[LAPS](laps.md)

Conceptually:

```text
WS01 -> Password A
WS02 -> Password B
WS03 -> Password C
```

rather than:

```text
WS01 -> Shared Password
WS02 -> Shared Password
WS03 -> Shared Password
```

---

# SMB and NTLM Relay

SMB is also a major NTLM relay target.

See:

[NTLM Relay](ntlm-relay.md)

The basic path is:

```text
Victim
  |
  v
NTLM Authentication
  |
  v
Relay Host
  |
  v
SMB Target
```

---

# Relay Requirements

Successful SMB relay depends on multiple conditions, including:

```text
NTLM Authentication Available
Attacker Can Receive Authentication
Target Accepts Relayed Authentication
SMB Signing Not Required
Victim Identity Has Useful Target Rights
Authentication Is Not Reflected Back Improperly
Other Protocol Protections Do Not Block the Path
```

Do not report:

```text
SMB Signing Not Required
```

as equivalent to:

```text
Domain Compromise
```

---

# Relay Target Identification

The assessment question is:

```text
Which Hosts Do Not Require SMB Signing?
```

Then:

```text
Which Identities Could Authenticate?
```

Then:

```text
What Rights Would Those Identities Have?
```

---

# ntlmrelayx

Impacket provides:

```text
ntlmrelayx
```

for authorised NTLM relay testing.

Check current syntax:

```bash
impacket-ntlmrelayx -h
```

The complete relay workflow is covered in:

[NTLM Relay](ntlm-relay.md)

---

# Authentication Coercion

SMB frequently appears in authentication coercion scenarios.

See:

[Authentication Coercion](authentication-coercion.md)

Conceptually:

```text
Target
  |
  v
Coerced Authentication
  |
  v
Attacker Listener
  |
  v
Relay
```

---

# Responder

Responder can interact with SMB-related authentication during authorised name-resolution and credential-capture testing.

A dedicated page will cover:

```text
docs/active-directory/responder.md
```

Always distinguish:

```text
Capture
```

from:

```text
Relay
```

---

# Capture vs Relay

Capture:

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
Capture Challenge / Response
```

Relay:

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
Target Service
```

These are different attack paths.

---

# SMB and Domain Controllers

SMB is particularly important on domain controllers because DCs expose:

```text
SYSVOL
NETLOGON
IPC$
```

and provide RPC services used throughout Active Directory.

---

# Do Not Disable SMB on Domain Controllers Blindly

Active Directory relies on SMB functionality.

Hardening should focus on:

```text
SMBv1 Removal
Signing
Encryption Where Appropriate
NTLM Reduction
Firewalling
Least Privilege
Monitoring
```

rather than simply disabling SMB everywhere.

---

# SYSVOL Permissions

SYSVOL should normally be readable by domain users because Group Policy requires access.

Therefore:

```text
Domain Users Can Read SYSVOL
```

is normally expected.

The security question is:

```text
Can Unauthorised Users Modify Sensitive SYSVOL Content?
```

---

# NETLOGON Permissions

Similarly:

```text
NETLOGON
```

may legitimately expose logon-related content.

Review the content and modification permissions rather than reporting normal read access as a vulnerability.

---

# SMB Enumeration with rpcclient

Samba's:

```text
rpcclient
```

can communicate with Windows RPC services over SMB.

Example:

```bash
rpcclient -U 'CORP/audit-user' dc01.corp.example
```

Enter the password interactively.

---

# rpcclient Commands

Depending on permissions, useful read-only commands may include:

```text
srvinfo
enumdomusers
enumdomgroups
querydominfo
```

Modern Active Directory environments may restrict some enumeration.

---

# rpcclient Anonymous Test

Where anonymous SMB/RPC access is in scope:

```bash
rpcclient -U '' -N dc01.corp.example
```

Do not assume anonymous connection means useful information is exposed.

---

# enum4linux-ng

`enum4linux-ng` can automate SMB/RPC enumeration.

Check:

```bash
enum4linux-ng -h
```

Example:

```bash
enum4linux-ng -A srv01.corp.example
```

Use authenticated enumeration where appropriate rather than relying only on anonymous access.

---

# NetExec Host Information

A basic NetExec SMB connection may reveal:

```text
Hostname
Domain
Operating System
SMB Signing
SMB Version
```

depending on target and tool version.

Example:

```bash
nxc smb srv01.corp.example
```

---

# SMB Session Enumeration

On a Windows SMB server:

```powershell
Get-SmbSession
```

This can show active SMB client sessions.

Useful properties include:

```text
ClientComputerName
ClientUserName
NumOpens
Dialect
Encrypted
Signed
```

depending on Windows version.

---

# SMB Open Files

Administrators can inspect open SMB files:

```powershell
Get-SmbOpenFile
```

This can provide useful defensive visibility.

---

# SMB Connections on Client

PowerShell:

```powershell
Get-SmbConnection
```

This can reveal:

```text
ServerName
ShareName
UserName
Dialect
Signed
Encrypted
```

depending on system version.

---

# Windows net use

Existing network connections:

```cmd
net use
```

Connect to a share:

```cmd
net use \\srv01.corp.example\Shared
```

Disconnect:

```cmd
net use \\srv01.corp.example\Shared /delete
```

---

# Explicit Credentials

Windows can establish an SMB connection using explicit credentials.

Avoid placing sensitive passwords directly into command history when alternatives are available.

PowerShell:

```powershell
$cred = Get-Credential
```

For administrative scripting, use secure credential-management mechanisms rather than embedding passwords in scripts.

---

# SMB Credential Conflicts

Windows may return errors when multiple connections to the same server are attempted using different credentials.

Review existing sessions:

```cmd
net use
```

Remove only your own test connection when necessary.

Do not disrupt legitimate user mappings.

---

# SMB Enumeration with PowerShell

Remote share discovery can also use CIM or management interfaces where authorised.

However, do not assume that:

```text
SMB Access
```

automatically grants:

```text
Remote WMI
```

or:

```text
WinRM
```

Each management protocol has its own authorisation requirements.

---

# SMB and Firewalling

SMB should generally not be exposed:

```text
Internet -> TCP 445
```

unless an exceptional architecture specifically requires and securely protects it.

Internally, access should also be restricted.

---

# East-West SMB

A common weak architecture is:

```text
WS01
 |
 +--> WS02:445
 |
 +--> WS03:445
 |
 +--> WS04:445
```

This creates unnecessary workstation-to-workstation lateral-movement opportunities.

---

# Better Workstation Segmentation

Where operationally possible:

```text
WS01
 |
 X
 |
 v
WS02:445
```

Peer workstation SMB administration should be restricted.

---

# Server Administration

A stronger model is:

```text
Privileged Admin Workstation
          |
          v
Management Network
          |
          v
Server:445
```

rather than:

```text
Any Workstation
      |
      v
Server:445
```

---

# SMB Hardening

A practical SMB hardening strategy includes:

```text
Disable SMBv1
Require SMB Signing Where Appropriate
Use SMB Encryption Where Appropriate
Restrict TCP 445
Reduce NTLM
Deploy Windows LAPS
Remove Credential Reuse
Apply Least Privilege
Restrict Administrative Shares
Monitor Remote Service Creation
Protect Privileged Accounts
```

---

# SMBv1

Verify:

```powershell
Get-SmbServerConfiguration |
    Select-Object EnableSMB1Protocol
```

Expected modern configuration:

```text
False
```

---

# SMB Signing

Review:

```powershell
Get-SmbServerConfiguration |
    Select-Object EnableSecuritySignature,RequireSecuritySignature
```

The desired configuration depends on Windows version, organisational requirements and compatibility.

For systems where relay resistance is required:

```text
Require Signing
```

is the important property.

---

# SMB Encryption

Review:

```powershell
Get-SmbServerConfiguration |
    Select-Object EncryptData,RejectUnencryptedAccess
```

Do not enable organisation-wide encryption without considering compatibility and performance.

---

# NTLM Reduction

SMB hardening should form part of a broader:

```text
NTLM Reduction
```

strategy.

See:

[NTLM](ntlm.md)

---

# Local Administrator Passwords

Deploy:

```text
Windows LAPS
```

to reduce reusable local administrator credentials.

See:

[LAPS](laps.md)

---

# Administrative Rights

Review membership of:

```text
Administrators
```

on servers and workstations.

Avoid broad groups such as:

```text
Domain Users
Authenticated Users
Large Helpdesk Groups
```

having unnecessary administrative access.

---

# Share Permissions

Review shares for:

```text
Everyone
Authenticated Users
Domain Users
Anonymous
Guest
```

permissions.

These principals are not automatically inappropriate.

The decision depends on:

```text
Share Purpose
Data Sensitivity
Write Capability
Execution Context
```

---

# Everyone Read

Example:

```text
Everyone -> Read
```

may be acceptable for:

```text
Public Software Distribution
```

but inappropriate for:

```text
HR
Finance
Backups
Secrets
Administrative Scripts
```

---

# Everyone Write

Broad write access deserves much closer review.

Especially dangerous:

```text
Everyone -> Modify
```

on content later executed by:

```text
Administrator
SYSTEM
Deployment Service
Scheduled Task
```

---

# Detection - Logon Events

SMB authentication commonly creates:

```text
4624
```

successful logon events.

Network logons commonly use:

```text
Logon Type 3
```

---

# Failed Authentication

Failed SMB authentication can generate:

```text
4625
```

Repeated failures may indicate:

```text
Password Spraying
Credential Guessing
Stale Credentials
Misconfigured Services
```

---

# Explicit Credentials

Event:

```text
4648
```

can indicate use of explicit credentials in relevant Windows authentication workflows.

---

# Special Privileges

Event:

```text
4672
```

may occur when a privileged account receives special privileges during logon.

---

# Share Access Auditing

Windows can audit network share access.

Relevant events include:

```text
5140
5145
```

---

# Event 5140

```text
5140
```

indicates that a network share object was accessed.

Useful fields can include:

```text
Account Name
Source Address
Share Name
```

---

# Event 5145

```text
5145
```

can provide detailed share-access checks.

This can help identify access to:

```text
ADMIN$
C$
Sensitive Shares
```

---

# Service Creation

PsExec-style lateral movement may generate:

```text
7045
```

for service installation.

With suitable auditing:

```text
4697
```

may also provide service-installation visibility.

---

# File Creation

Monitor unexpected executable or script creation in:

```text
ADMIN$
C$
Windows
Temp
ProgramData
```

especially when correlated with remote SMB access.

---

# Named Pipe Detection

EDR products may provide visibility into unusual named-pipe activity.

Named-pipe telemetry should be correlated with:

```text
Source Host
Account
Process
Remote Connection
Service Creation
```

---

# Detect Administrative Share Access

High-value pattern:

```text
User Workstation
       |
       v
ADMIN$
       |
       v
Server
```

Ask whether the source system is an approved administrative workstation.

---

# SMB Relay Detection

Potential indicators include:

```text
Unexpected NTLM Authentication
Unusual Source Systems
Authentication to Systems Not Normally Used
SMB Connections Following Coercion Activity
Privileged Machine Account Authentication
```

Detection should be correlated with:

[NTLM Relay](ntlm-relay.md)

and:

[Authentication Coercion](authentication-coercion.md)

---

# Network Detection

Monitor:

```text
445/TCP
```

for unusual:

```text
East-West Connections
Workstation-to-Workstation SMB
User VLAN-to-Server SMB
High Fan-Out Authentication
```

---

# High Fan-Out SMB

Example:

```text
WS01
 |
 +--> SRV01
 +--> SRV02
 +--> SRV03
 +--> SRV04
 +--> SRV05
```

within a short period may indicate:

```text
Enumeration
Credential Validation
Lateral Movement
```

although legitimate management tools can create similar patterns.

---

# Baseline Administrative Systems

Defenders should know which systems legitimately generate large amounts of SMB administration traffic.

Examples:

```text
SCCM
Backup Servers
Software Deployment
Monitoring
Patch Management
Administrative Jump Hosts
```

---

# Reporting SMB Findings

Avoid reporting:

```text
Port 445 Open
```

as a vulnerability by itself.

SMB is required for many Windows and Active Directory functions.

Report the actual weakness.

Examples:

```text
SMBv1 Enabled
```

```text
SMB Signing Not Required
```

```text
Shared Local Administrator Credentials Permit SMB Lateral Movement
```

```text
Sensitive SMB Share Accessible to Unauthorised Users
```

```text
Unprivileged Users Can Modify Privileged Deployment Scripts
```

```text
Workstation Network Can Reach Administrative SMB Services on Servers
```

---

# Example Finding - SMB Signing

```text
Finding:
SMB Signing Is Not Required on Multiple Windows Systems

Description:
Multiple Windows systems accepted SMB connections without requiring
SMB message signing.

SMB signing provides integrity protection for SMB sessions and is an
important mitigation against NTLM relay attacks targeting SMB.

The identified systems may therefore be usable as SMB relay targets if
an attacker can obtain or coerce suitable NTLM authentication from an
identity with useful privileges on those systems.

Impact:
An attacker positioned to receive NTLM authentication may be able to
relay that authentication to an affected SMB service.

The actual impact depends on the privileges of the relayed identity and
the availability of other relay prerequisites.

Recommendation:
Require SMB signing on systems where compatible with the organisation's
Windows environment and security baseline.

Prioritise domain controllers, servers and administrative systems.

In addition, reduce NTLM usage, restrict SMB network access and address
authentication-coercion paths.
```

---

# Example Finding - Sensitive Share

```text
Finding:
Sensitive Information Exposed Through Excessive SMB Share Permissions

Affected Host:
files01.corp.example

Affected Share:
Finance

Description:
The tested standard domain user could access files within the Finance
SMB share despite having no documented business requirement for this
access.

The accessible content included information classified as sensitive by
the organisation.

Impact:
Any compromised standard domain account with equivalent permissions
could access the affected information through SMB.

Recommendation:
Review both share-level and NTFS permissions and restrict access to the
minimum groups required for the business function.

Periodically review share permissions and remove stale or overly broad
group assignments.
```

---

# Example Finding - Writable Deployment Share

```text
Finding:
Unprivileged Users Can Modify Files Used by Privileged Deployment Process

Affected Host:
deploy01.corp.example

Affected Share:
Software

Description:
Standard domain users had modification rights to files within an SMB
share used by an administrative software deployment process.

Files from the share are subsequently accessed or executed by systems
operating with elevated privileges.

Impact:
An attacker compromising a standard domain account could potentially
modify deployment content and influence code or configuration consumed
by privileged systems.

This may provide a path from a low-privileged domain account to
privileged code execution depending on the deployment workflow.

Recommendation:
Restrict modification rights to dedicated deployment administrators and
service identities.

Separate read-only software distribution paths from administrative
staging locations and implement integrity validation for deployed
content.
```

---

# Example Finding - Local Administrator Reuse

```text
Finding:
Shared Local Administrator Credentials Enable SMB Lateral Movement

Description:
The same local administrator credential was valid on multiple Windows
systems.

The credential provided administrative SMB access to more than one
approved test endpoint.

Impact:
Compromise of one affected endpoint may expose reusable administrative
credentials that permit lateral movement to other systems.

Recommendation:
Deploy Windows LAPS or another centrally managed mechanism providing
unique local administrator passwords per endpoint.

Restrict remote SMB administration between peer systems and monitor
administrative share access.
```

---

# Evidence Checklist

Record:

```text
Target Host
Target IP
Domain
Operating System
SMB Port
SMB Dialect
SMBv1 Status
Signing Supported
Signing Required
Encryption
Authentication Protocol
Account
Account Type
Accessible Shares
Share Permissions
NTFS Permissions
Anonymous Access
Guest Access
Administrative Share Access
Sensitive Files
Write Access
Remote Administration Rights
Relay Relevance
Source Host
Timestamp
Commands Used
Files Created
Files Removed
```

Never place:

```text
Passwords
NTLM Hashes
Private Keys
Sensitive File Contents
```

directly into a report unless strictly necessary and appropriately protected.

---

# SMB Assessment Checklist

## Discovery

- [ ] Identify TCP 445
- [ ] Identify TCP 139 where relevant
- [ ] Identify hostname
- [ ] Identify domain
- [ ] Identify operating system
- [ ] Identify SMB dialects
- [ ] Check SMBv1
- [ ] Check SMBv2/SMBv3

## Signing and Encryption

- [ ] Determine signing support
- [ ] Determine whether signing is required
- [ ] Review client signing configuration
- [ ] Review server signing configuration
- [ ] Determine SMB encryption support
- [ ] Determine whether encryption is required
- [ ] Identify relay relevance

## Authentication

- [ ] Test only approved credentials
- [ ] Identify domain vs local account
- [ ] Determine Kerberos vs NTLM
- [ ] Review CIFS ticket
- [ ] Prefer hostname for Kerberos
- [ ] Avoid unnecessary authentication sweeps
- [ ] Avoid account lockouts

## Shares

- [ ] Enumerate shares
- [ ] Review IPC$
- [ ] Review ADMIN$
- [ ] Review C$
- [ ] Review SYSVOL
- [ ] Review NETLOGON
- [ ] Review business shares
- [ ] Review anonymous access
- [ ] Review guest access

## Permissions

- [ ] Review share permissions
- [ ] Review NTFS permissions
- [ ] Determine effective access
- [ ] Identify broad read access
- [ ] Identify broad write access
- [ ] Identify privileged writable content
- [ ] Review inheritance

## Sensitive Data

- [ ] Review scripts
- [ ] Review configuration files
- [ ] Review deployment files
- [ ] Review backup files
- [ ] Review credential files
- [ ] Review certificate files
- [ ] Review database configuration
- [ ] Minimise collection of unrelated data

## SYSVOL

- [ ] Review Group Policy files
- [ ] Review logon scripts
- [ ] Search for legacy GPP passwords
- [ ] Review hardcoded credentials
- [ ] Review writable content
- [ ] Do not report expected read access alone

## Lateral Movement

- [ ] Determine administrative share access
- [ ] Determine local administrator rights
- [ ] Review credential reuse
- [ ] Review Pass-the-Hash exposure
- [ ] Review service-control access
- [ ] Use minimal validation
- [ ] Avoid unnecessary remote shells

## NTLM Relay

- [ ] Identify systems not requiring SMB signing
- [ ] Determine whether NTLM is available
- [ ] Identify possible authentication sources
- [ ] Determine privileges of potential relayed identities
- [ ] Review coercion paths
- [ ] Avoid overstating impact

## Safe Validation

- [ ] Use approved hosts
- [ ] Use approved credentials
- [ ] Prefer read-only enumeration
- [ ] Use unique test filenames
- [ ] Remove test files
- [ ] Avoid modifying existing files
- [ ] Avoid production payloads
- [ ] Avoid unnecessary service creation
- [ ] Stop when sufficient evidence exists

## Detection

- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4648
- [ ] Monitor 4672
- [ ] Monitor 5140
- [ ] Monitor 5145
- [ ] Monitor 7045
- [ ] Monitor 4697
- [ ] Monitor ADMIN$
- [ ] Monitor C$
- [ ] Monitor service creation
- [ ] Monitor executable creation
- [ ] Monitor named pipes
- [ ] Monitor high fan-out SMB
- [ ] Monitor workstation-to-workstation SMB
- [ ] Monitor privileged account SMB activity

## Hardening

- [ ] Disable SMBv1
- [ ] Require SMB signing where appropriate
- [ ] Use SMB encryption where appropriate
- [ ] Reduce NTLM
- [ ] Restrict TCP 445
- [ ] Restrict workstation-to-workstation SMB
- [ ] Restrict administrative shares
- [ ] Apply least privilege
- [ ] Deploy Windows LAPS
- [ ] Remove local administrator password reuse
- [ ] Protect privileged identities
- [ ] Segment management traffic
- [ ] Monitor SMB administration

## Reporting

- [ ] Report actual weakness
- [ ] Do not report TCP 445 alone
- [ ] Identify affected systems
- [ ] Identify account permissions
- [ ] Identify signing state
- [ ] Identify relay prerequisites
- [ ] Identify accessible data
- [ ] Identify write implications
- [ ] Document safe validation
- [ ] Provide specific remediation

---

# SMB Testing Model

The protocol model is:

```text
Client
  |
  v
TCP 445
  |
  v
SMB
```

The authentication model is:

```text
Domain Identity
      |
      +--> Kerberos
      |
      +--> NTLM
      |
      v
SMB Server
```

The Kerberos model is:

```text
User
 |
 v
KDC
 |
 v
cifs/server
 |
 v
SMB
```

The share model is:

```text
Authenticated User
       |
       v
Share Permission
       |
       v
NTFS Permission
       |
       v
Effective Access
```

The administrative model is:

```text
Administrator
      |
      v
SMB
      |
      +--> ADMIN$
      |
      +--> C$
      |
      +--> IPC$
      |
      v
Remote Administration
```

The PsExec model is:

```text
Administrative SMB
       |
       v
ADMIN$
       |
       v
Service Control Manager
       |
       v
Temporary Service
       |
       v
Execution
```

The Pass-the-Hash model is:

```text
NTLM Hash
    |
    v
NTLM Authentication
    |
    v
SMB
    |
    v
Remote Host
```

The relay model is:

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
Unsigned SMB Target
```

The signing model is:

```text
SMB Signing Required
        |
        v
Message Must Be Signed
        |
        v
Classic SMB Relay Restricted
```

The sensitive-share model is:

```text
Domain User
    |
    v
SMB Share
    |
    v
Sensitive File
```

The writable-share model is:

```text
Low-Privilege User
       |
       v
Writable SMB Share
       |
       v
Privileged Script / Binary
       |
       v
Privileged Execution
```

The lateral-movement model is:

```text
Compromised Host
      |
      v
Reusable Credential
      |
      v
SMB
      |
      v
Second Host
      |
      v
Administrative Access
```

The defensive model is:

```text
SMBv1 Disabled
      +
SMB Signing
      +
NTLM Reduction
      +
Unique Local Credentials
      +
Least Privilege
      +
Network Segmentation
      +
Monitoring
      =
Reduced SMB Attack Surface
```

For penetration testers:

```text
Do Not Ask:
"Can I get a shell through SMB?"

Ask:
"What access does this identity have
through SMB, and what security boundary
does that access cross?"
```

For defenders:

```text
Do Not Ask:
"Is port 445 open?"

Ask:
"Who can authenticate to SMB,
what can they access, is signing required,
and which systems are allowed to administer
each other?"
```

The complete SMB relationship is:

```text
Identity
   |
   v
Kerberos / NTLM
   |
   v
SMB
   |
   +--> Shares
   |
   +--> Files
   |
   +--> Named Pipes
   |
   +--> Administrative Shares
   |
   +--> Remote Administration
   |
   v
Potential Lateral Movement
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Active Directory Enumeration:

[Enumeration](enumeration.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

LAPS:

[LAPS](laps.md)

GPP Passwords:

`GPP Passwords`

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

Authentication Coercion:

[Authentication Coercion](authentication-coercion.md)

The next detailed lateral-movement page is:

```text
docs/active-directory/winrm.md
```

---

# References

## Microsoft - SMB Overview

[Microsoft - SMB Overview](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Security Hardening

[Microsoft - SMB Security Hardening](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security-hardening){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Signing

[Microsoft - Control SMB Signing Behavior](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Encryption

[Microsoft - SMB Security Enhancements](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }

Verify installed syntax with:

```bash
nxc --version
nxc smb -h
```

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

Relevant tools include:

```text
psexec
smbexec
atexec
wmiexec
ntlmrelayx
```

depending on the assessment objective.

---

## Samba smbclient

[Samba - smbclient](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - SMB/Windows Admin Shares

[MITRE ATT&CK - SMB/Windows Admin Shares](https://attack.mitre.org/techniques/T1021/002/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Network Share Discovery

[MITRE ATT&CK - Network Share Discovery](https://attack.mitre.org/techniques/T1135/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

SMB should not be treated simply as:

```text
Port 445
```

It is a major Windows infrastructure protocol connecting:

```text
Authentication
File Access
RPC
Administration
Group Policy
Domain Services
```

The most useful SMB assessment sequence is:

```text
Discover SMB
     |
     v
Determine Version
     |
     v
Check Signing
     |
     v
Determine Authentication
     |
     v
Enumerate Shares
     |
     v
Review Permissions
     |
     v
Identify Sensitive Access
     |
     v
Determine Administrative Rights
     |
     v
Assess Lateral Movement
```

For many assessments, the most important SMB questions are:

```text
Is SMBv1 enabled?

Is SMB signing required?

Is NTLM still accepted?

Which shares can this user access?

Which shares can this user modify?

Can this identity access ADMIN$ or C$?

Are local administrator credentials reused?

Can workstations directly administer each other?

Can an attacker relay authentication to this host?
```

Do not assume:

```text
SMB Signing Not Required
=
Immediate Compromise
```

The complete relay chain still requires:

```text
Authentication Source
       +
Relay-Compatible Target
       +
Useful Victim Privileges
```

Similarly:

```text
Writable Share
```

does not automatically mean:

```text
Code Execution
```

The critical question is:

```text
Who Consumes the Writable Content?
```

A writable public-document share may have limited security impact.

A writable share containing:

```text
SYSTEM Deployment Script
```

may provide a serious privilege-escalation path.

For lateral movement, SMB frequently becomes dangerous when combined with:

```text
Reusable Administrative Credentials
```

because:

```text
Compromise One Host
      |
      v
Recover Local Admin Credential
      |
      v
Credential Reused
      |
      v
Authenticate Through SMB
      |
      v
Compromise Additional Hosts
```

Windows LAPS, administrative separation and network segmentation can significantly reduce this blast radius.

During authorised testing, begin with:

```text
Read-Only Enumeration
```

and escalate validation only when necessary.

If:

```text
ADMIN$ Access
```

already proves administrative access, a remote shell may provide little additional evidence.

The purpose of SMB testing is not to execute as many remote administration techniques as possible.

It is to determine:

```text
Identity
   |
   v
SMB Access
   |
   v
Effective Permission
   |
   v
Security Impact
```

and provide the organisation with a clear explanation of how to reduce that attack path.

The next page examines another major Windows remote-management protocol:

```text
WinRM
```
