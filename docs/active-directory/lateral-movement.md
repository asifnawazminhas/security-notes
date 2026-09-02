# Active Directory Lateral Movement

Lateral movement is the process of using access to one identity or system to reach additional systems within an environment.

In an Active Directory assessment, lateral movement normally begins after an attacker has obtained some form of authenticated access.

Examples include:

```text
Password
NTLM Hash
Kerberos Ticket
Certificate
Access Token
Existing Session
Local Administrator Rights
Domain Account
Service Account
Computer Account
```

The objective is not necessarily privilege escalation.

Instead:

```text
Current Access
      |
      v
Reach Another System
      |
      v
Establish Access
      |
      v
Continue Enumeration
      |
      v
Identify Additional Attack Paths
```

Lateral movement becomes particularly important in Active Directory because credentials, administrative relationships, sessions, services and trust relationships frequently connect many systems together.

!!! warning "Authorised testing only"
    Lateral movement can affect production endpoints, administrative systems and domain infrastructure. Only authenticate to, execute commands on or modify systems explicitly included in the assessment scope. Prefer low-impact validation and avoid disrupting active user sessions or production services.

---

# Lateral Movement at a Glance

A typical attack path looks like:

```text
Initial Foothold
      |
      v
Credential Access
      |
      v
Identify Reachable Systems
      |
      v
Identify Administrative Rights
      |
      v
Choose Authentication Method
      |
      v
Choose Remote Management Protocol
      |
      v
Authenticate
      |
      v
Remote Access / Execution
      |
      v
Repeat
```

Examples:

```text
Workstation
   |
   v
File Server
   |
   v
Application Server
   |
   v
Management Server
```

or:

```text
Compromised User
      |
      v
Local Admin on WS01
      |
      v
Credential Exposure
      |
      v
Admin on SRV01
      |
      v
Additional Privileges
```

---

# Lateral Movement Is an Attack Path

Do not think of lateral movement as:

```text
One Command
```

Instead think:

```text
Identity
   |
   v
Credential
   |
   v
Permission
   |
   v
Protocol
   |
   v
Target
   |
   v
Execution
```

Every stage matters.

---

# Core Questions

During an authorised assessment, determine:

```text
Who am I?

What credentials do I control?

Where is this identity privileged?

Which systems are reachable?

Which protocols are available?

Which authentication methods are accepted?

Can I execute commands?

Can I access data without execution?

What additional identities become reachable?
```

---

# Lateral Movement vs Privilege Escalation

These concepts are related but different.

Privilege escalation:

```text
Low Privilege
     |
     v
Higher Privilege
```

Lateral movement:

```text
Host A
  |
  v
Host B
```

An attacker can move laterally without gaining privilege.

Example:

```text
User on WS01
     |
     v
Same User on WS02
```

---

# Privilege Escalation During Lateral Movement

The two frequently interact:

```text
WS01
 |
 v
Local Privilege Escalation
 |
 v
Administrator
 |
 v
Credential Access
 |
 v
SRV01
 |
 v
Lateral Movement
```

Then:

```text
SRV01
 |
 v
New Privilege Path
 |
 v
Further Escalation
```

---

# Active Directory Lateral Movement Model

```text
Domain Identity
      |
      v
Authentication
      |
      +--> Kerberos
      |
      +--> NTLM
      |
      v
Remote Protocol
      |
      +--> SMB
      +--> WinRM
      +--> WMI
      +--> DCOM
      +--> RDP
      +--> MSSQL
      +--> SSH
      +--> Application Protocol
      |
      v
Target System
```

---

# Common Authentication Material

Lateral movement can use different credential types.

```text
Plaintext Password
NTLM Hash
Kerberos TGT
Kerberos TGS
AES Kerberos Key
Certificate
Existing Access Token
SSH Key
Application Credential
```

The available credential determines which techniques are possible.

---

# Password Authentication

The simplest case:

```text
DOMAIN\user
      +
Password
      |
      v
Remote Authentication
```

Potential protocols include:

```text
SMB
WinRM
RDP
WMI
MSSQL
LDAP
HTTP
SSH
```

depending on the environment.

---

# NTLM Hashes

If an NTLM hash is available, some protocols support authentication without knowing the plaintext password.

This is commonly associated with:

[Pass-the-Hash](pass-the-hash.md)

Conceptually:

```text
NTLM Hash
    |
    v
NTLM Authentication
    |
    v
Remote Service
```

---

# Kerberos Tickets

Existing Kerberos tickets may also provide lateral movement opportunities.

See:

[Kerberos Tickets](kerberos-tickets.md)

and:

[Pass the Ticket](pass-the-ticket.md)

Conceptually:

```text
TGT / TGS
    |
    v
Kerberos
    |
    v
Remote Service
```

---

# Kerberos Keys

AES keys may be used to obtain or authenticate with Kerberos tickets where appropriate.

See:

[Pass-the-Key](pass-the-key.md)

---

# Certificates

Certificate-based authentication may provide access to Active Directory identities.

Conceptually:

```text
Certificate
    |
    v
PKINIT
    |
    v
Kerberos TGT
    |
    v
Remote Services
```

Certificate abuse is covered in the AD CS notes.

---

# Existing Sessions

Sometimes the most valuable credential is not stored as a reusable password or hash.

Instead:

```text
Privileged User
      |
      v
Logged-On Session
      |
      v
Compromised Host
```

The host itself becomes strategically important.

---

# Administrative Relationships

Before attempting remote execution, determine:

```text
Where Is My Account Administrator?
```

This is much more efficient than blindly attempting authentication against every system.

---

# BloodHound

BloodHound is particularly useful for lateral movement analysis.

See:

[BloodHound](bloodhound.md)

Useful relationships can include:

```text
AdminTo
CanRDP
CanPSRemote
HasSession
ExecuteDCOM
SQLAdmin
```

depending on the collected data and BloodHound version.

---

# Conceptual BloodHound Path

```text
User
 |
 v
AdminTo
 |
 v
Computer
 |
 v
HasSession
 |
 v
Privileged User
```

This can reveal:

```text
Current Identity
      |
      v
Reachable Computer
      |
      v
Higher-Value Session
```

---

# Do Not Treat HasSession as Guaranteed Credential Theft

A session relationship means:

```text
User Has or Had a Session
```

It does not automatically mean:

```text
Credential Can Be Extracted
```

Modern Windows protections can significantly affect credential exposure.

---

# NetExec

NetExec is one of the most useful tools for authorised Active Directory lateral-movement assessment.

See:

[NetExec](netexec.md)

Check the installed version:

```bash
nxc --version
```

Help:

```bash
nxc --help
```

---

# SMB Authentication Sweep

A controlled SMB authentication test can identify systems where credentials are valid.

Example:

```bash
nxc smb 10.10.10.0/24 -u 'audit-user' -p 'PASSWORD'
```

Prefer a defined target list where possible:

```bash
nxc smb targets.txt -u 'audit-user' -p 'PASSWORD'
```

---

# Successful Authentication

NetExec may indicate:

```text
[+]
```

for successful authentication.

If the account also has administrative access, output may include:

```text
Pwn3d!
```

Treat tool output as a lead and verify the actual privilege level.

---

# Avoid Unnecessary Network-Wide Authentication

Do not immediately run credentials across:

```text
Entire Enterprise
```

if the assessment only requires testing a specific segment.

Prefer:

```text
BloodHound
      |
      v
Known Administrative Targets
      |
      v
Controlled Authentication
```

---

# Password Spraying vs Lateral Movement

These should not be confused.

Password spraying:

```text
One Password
     |
     v
Many Accounts
```

Lateral movement commonly involves:

```text
Known Credential
     |
     v
Known Systems
```

See:

[Password Spraying](password-spraying.md)

---

# Authentication Scope

Repeated authentication can create:

```text
Account Lockouts
SIEM Alerts
EDR Alerts
Network Load
Authentication Noise
```

Use the minimum target set required.

---

# SMB

SMB is one of the most common Windows lateral-movement protocols.

Typical ports:

```text
TCP 445
```

and historically:

```text
TCP 139
```

Modern domain environments primarily use:

```text
TCP 445
```

---

# SMB Capabilities

Depending on privileges, SMB can provide:

```text
Share Access
File Transfer
Remote Administration
Named Pipes
Service Management
Remote Execution Support
```

---

# SMB Connectivity

PowerShell:

```powershell
Test-NetConnection srv01.corp.example -Port 445
```

Linux:

```bash
nmap -Pn -p445 srv01.corp.example
```

---

# SMB Enumeration with NetExec

```bash
nxc smb srv01.corp.example -u 'audit-user' -p 'PASSWORD'
```

Enumerate shares:

```bash
nxc smb srv01.corp.example -u 'audit-user' -p 'PASSWORD' --shares
```

---

# smbclient

List shares:

```bash
smbclient -L //srv01.corp.example -U 'CORP/audit-user'
```

Connect to a share:

```bash
smbclient //srv01.corp.example/Shared -U 'CORP/audit-user'
```

---

# Administrative Shares

Windows commonly provides administrative shares such as:

```text
ADMIN$
C$
IPC$
```

Access to:

```text
C$
```

or:

```text
ADMIN$
```

often indicates significant local privileges.

However, access alone does not necessarily mean every remote execution technique will work.

---

# SMB Remote Execution

Common Impacket techniques include:

```text
psexec.py
smbexec.py
atexec.py
```

Modern installations may expose them without the `.py` suffix.

Check:

```bash
impacket-psexec -h
```

```bash
impacket-smbexec -h
```

```bash
impacket-atexec -h
```

---

# PsExec Model

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
Service Control Manager
   |
   v
Temporary Service
   |
   v
Command Execution
```

This technique is highly visible.

---

# Impacket PsExec

Authorised example:

```bash
impacket-psexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

---

# Pass-the-Hash with PsExec

Where explicitly authorised:

```bash
impacket-psexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

See:

[Pass-the-Hash](pass-the-hash.md)

---

# PsExec Operational Impact

PsExec-style execution may create:

```text
Service
Executable
SMB Activity
Service Control Manager Activity
Process Creation
```

It is therefore not the lowest-noise validation method.

---

# SMBExec

Impacket SMBExec uses SMB and service-management mechanisms differently from PsExec.

Example:

```bash
impacket-smbexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

Hash authentication:

```bash
impacket-smbexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

---

# ATExec

ATExec uses the Task Scheduler RPC interface.

Example:

```bash
impacket-atexec 'CORP/audit-admin:PASSWORD@srv01.corp.example' 'whoami'
```

This can produce different telemetry from service-based execution.

---

# WinRM

Windows Remote Management provides another common lateral-movement path.

Typical ports:

```text
5985 - HTTP
5986 - HTTPS
```

---

# WinRM Connectivity

PowerShell:

```powershell
Test-NetConnection srv01.corp.example -Port 5985
```

and:

```powershell
Test-NetConnection srv01.corp.example -Port 5986
```

---

# PowerShell Remoting

From Windows:

```powershell
Test-WSMan srv01.corp.example
```

Create a session:

```powershell
Enter-PSSession -ComputerName srv01.corp.example
```

Using explicit credentials:

```powershell
$cred = Get-Credential
Enter-PSSession -ComputerName srv01.corp.example -Credential $cred
```

---

# Invoke-Command

For a single authorised command:

```powershell
Invoke-Command -ComputerName srv01.corp.example -ScriptBlock {
    whoami
}
```

With explicit credentials:

```powershell
$cred = Get-Credential

Invoke-Command -ComputerName srv01.corp.example -Credential $cred -ScriptBlock {
    hostname
    whoami
}
```

---

# Evil-WinRM

From Kali:

```bash
evil-winrm -i srv01.corp.example -u 'audit-user' -p 'PASSWORD'
```

Hash authentication may be supported:

```bash
evil-winrm -i srv01.corp.example -u 'audit-user' -H 'NTHASH'
```

Check the installed version:

```bash
evil-winrm -h
```

---

# NetExec WinRM

```bash
nxc winrm srv01.corp.example -u 'audit-user' -p 'PASSWORD'
```

This can help determine whether the account can authenticate through WinRM.

---

# WinRM Authorisation

Successful domain authentication does not necessarily imply:

```text
PowerShell Remoting Allowed
```

The account must also have suitable local rights.

Commonly relevant groups include:

```text
Administrators
Remote Management Users
```

depending on configuration.

---

# WMI

Windows Management Instrumentation can support remote administration and command execution.

Typical architecture:

```text
Attacker
   |
   v
DCOM / RPC
   |
   v
WMI
   |
   v
Target
```

---

# WMI Connectivity

WMI commonly relies on:

```text
TCP 135
```

plus dynamic RPC ports.

Therefore:

```text
135 Open
```

does not by itself prove that WMI remote execution will succeed.

---

# Native PowerShell WMI/CIM

Modern PowerShell generally favours CIM cmdlets.

Example:

```powershell
Get-CimInstance -ClassName Win32_OperatingSystem -ComputerName srv01.corp.example
```

Depending on the environment, authentication and protocol configuration may require a CIM session.

---

# Impacket WMIExec

```bash
impacket-wmiexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

Pass-the-Hash:

```bash
impacket-wmiexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

---

# WMIExec Model

```text
Remote Authentication
       |
       v
DCOM / WMI
       |
       v
Win32_Process
       |
       v
Command Execution
```

The exact implementation varies by tool.

---

# DCOM

Distributed Component Object Model can expose remote execution capabilities through certain COM objects.

Conceptually:

```text
Attacker
   |
   v
RPC Endpoint Mapper
   |
   v
DCOM
   |
   v
Remote COM Object
   |
   v
Execution
```

---

# DCOM Requirements

Typical requirements include:

```text
Network Connectivity
RPC Access
Suitable Authentication
Remote Activation Rights
Applicable COM Object
Firewall Permission
```

---

# DCOM Is Environment Dependent

Do not assume:

```text
Local Administrator
=
Every DCOM Technique Works
```

Windows version, hardening, firewall policy and COM permissions all matter.

---

# RDP

Remote Desktop Protocol is another lateral-movement mechanism.

Default port:

```text
TCP 3389
```

---

# RDP Connectivity

PowerShell:

```powershell
Test-NetConnection srv01.corp.example -Port 3389
```

Linux:

```bash
nmap -Pn -p3389 srv01.corp.example
```

---

# RDP Rights

Potentially relevant local groups include:

```text
Administrators
Remote Desktop Users
```

Group Policy may further control RDP logon rights.

---

# RDP with xfreerdp

Depending on the installed FreeRDP version:

```bash
xfreerdp /v:srv01.corp.example /u:audit-user /d:CORP
```

Let the tool prompt for the password where possible rather than exposing it in shell history.

Check syntax:

```bash
xfreerdp /help
```

---

# RDP Operational Considerations

RDP can:

```text
Create Interactive Sessions
Affect Existing Sessions
Generate User-Visible Activity
Expose Clipboard Data
Create Drive Mappings
Trigger MFA
```

Use it carefully during production assessments.

---

# MSSQL

SQL Server can become an important lateral-movement path.

Common port:

```text
TCP 1433
```

although SQL Server may use different or dynamic ports.

---

# NetExec MSSQL

```bash
nxc mssql sql01.corp.example -u 'audit-user' -p 'PASSWORD'
```

---

# Impacket mssqlclient

```bash
impacket-mssqlclient 'CORP/audit-user@sql01.corp.example' -windows-auth
```

The client can be used to inspect the SQL Server privileges associated with the authenticated account.

---

# SQL Administrative Relationships

A domain account may have:

```text
sysadmin
```

rights on SQL Server without being:

```text
Local Administrator
```

on the Windows host.

This creates another privilege relationship:

```text
AD User
   |
   v
SQL Server
   |
   v
Database Privilege
```

---

# Linked SQL Servers

SQL Server environments may contain:

```text
Linked Servers
```

which can create additional lateral paths.

Conceptually:

```text
SQL01
 |
 v
Linked Server
 |
 v
SQL02
```

The effective privilege may change at each hop.

---

# SSH on Windows

Modern Windows environments may expose OpenSSH.

Typical port:

```text
TCP 22
```

If enabled:

```text
Domain Credential
      |
      v
SSH
      |
      v
Windows Host
```

may become another lateral-movement path.

---

# Test SSH

```bash
ssh 'audit-user@srv01.corp.example'
```

Domain username syntax depends on server configuration.

---

# Remote Service Creation

Windows Service Control Manager can support remote service creation when the attacker has sufficient rights.

Conceptually:

```text
Administrative Access
       |
       v
Service Control Manager
       |
       v
Create Service
       |
       v
Start Service
       |
       v
Execution
```

This is one reason local administrator rights are so valuable.

---

# sc.exe

In an authorised Windows environment, service visibility can be checked with:

```cmd
sc.exe \\srv01 query
```

Remote service creation is much more intrusive and should not be used merely to prove that administrative access exists.

---

# Scheduled Tasks

Task Scheduler can also support remote execution.

Conceptually:

```text
Administrative Credential
       |
       v
Task Scheduler RPC
       |
       v
Remote Task
       |
       v
Execution
```

This is the basis for tools such as:

```text
atexec
```

---

# Remote Registry

Remote Registry does not itself represent a general command-execution mechanism, but access may expose valuable system information.

Potential uses include:

```text
Configuration Enumeration
Security Policy Review
Software Discovery
Credential-Related Configuration
```

Avoid starting disabled services merely for convenience unless authorised.

---

# Administrative Shares Without Execution

Sometimes proving:

```text
Write Access to C$
```

is sufficient to establish excessive administrative access.

You do not always need:

```text
Remote Shell
```

to demonstrate the risk.

---

# Safe Validation Hierarchy

Prefer:

```text
Authentication
      |
      v
Authorisation Check
      |
      v
Read-Only Enumeration
      |
      v
Minimal Command
      |
      v
Interactive Session
```

Only move further down the chain when necessary.

---

# Minimal Command Execution

If remote execution is required, prefer low-impact commands such as:

```cmd
whoami
```

```cmd
hostname
```

```cmd
whoami /groups
```

```cmd
echo %COMPUTERNAME%
```

These prove execution without changing meaningful system state.

---

# Avoid Payload Deployment for Simple Validation

If:

```text
whoami
```

proves administrative remote execution, there is usually no reason to deploy:

```text
Beacon
Meterpreter
Reverse Shell
Custom Loader
Persistence
```

unless explicitly required by the engagement objectives.

---

# Local Administrator Reuse

One of the classic lateral-movement problems is reuse of local administrator credentials.

Conceptually:

```text
WS01
Local Administrator Password
        |
        +--> WS02
        +--> WS03
        +--> WS04
        +--> SRV01
```

One credential compromise becomes:

```text
Many Host Compromise
```

---

# Windows LAPS

Windows LAPS reduces this risk by providing:

```text
Unique Local Administrator Password
Per Managed Device
```

See:

[LAPS](laps.md)

---

# LAPS Model

Without LAPS:

```text
Same Local Admin Password
        |
        +--> Host A
        +--> Host B
        +--> Host C
```

With properly configured LAPS:

```text
Host A -> Password A
Host B -> Password B
Host C -> Password C
```

---

# Domain Administrator Sessions

Privileged domain accounts should not routinely log on to lower-trust workstations.

Bad model:

```text
Domain Admin
    |
    v
User Workstation
```

If the workstation becomes compromised, the privileged session may become part of an attack path.

---

# Administrative Tiering

A stronger model separates:

```text
Tier 0
Tier 1
Tier 2
```

or equivalent modern privileged-access boundaries.

Conceptually:

```text
Tier 0 Admin
     |
     +--> Domain Controllers
     +--> PKI
     +--> Identity Infrastructure

Tier 1 Admin
     |
     +--> Servers

Tier 2 Admin
     |
     +--> Workstations
```

The exact model should reflect current organisational architecture rather than relying mechanically on legacy tier terminology.

---

# Privileged Access Workstations

High-value administrators should use dedicated hardened administrative systems where appropriate.

Conceptually:

```text
Normal Workstation
       X
       |
       v
Tier 0 Administration
```

Instead:

```text
Privileged Access Workstation
       |
       v
Tier 0 Administration
```

---

# Credential Exposure and Lateral Movement

Lateral movement often creates new credential-access opportunities.

```text
Host A
 |
 v
Move to Host B
 |
 v
Find Credential
 |
 v
Move to Host C
```

This creates:

```text
Credential Cascade
```

---

# Credential Access

See:

[Credential Access](credential-access.md)

Potential sources can include:

```text
LSASS
Registry Secrets
Credential Manager
DPAPI
Configuration Files
Scheduled Tasks
Services
Browser Data
Application Secrets
Backups
Scripts
```

---

# Avoid Automatic Credential Dumping

Do not make:

```text
Remote Access
      |
      v
Immediately Dump LSASS
```

your default workflow.

First determine:

```text
What Access Do I Already Have?

What Is the Assessment Objective?

Is Credential Extraction Necessary?
```

---

# Computer Accounts

Computer accounts can also participate in lateral-movement chains.

A computer account has:

```text
Password
NTLM Key
Kerberos Keys
SPNs
Domain Identity
```

Compromising a machine account can therefore enable domain authentication as that computer.

---

# Machine Account Relationships

Machine identities may have access to:

```text
LDAP
SMB
AD CS
Other Computers
Management Infrastructure
```

depending on configuration.

---

# RBCD

Resource-Based Constrained Delegation can transform control of a computer or suitable AD object into a lateral-movement path.

See:

[Resource-Based Constrained Delegation](rbcd.md)

Conceptually:

```text
Controlled Principal
       |
       v
RBCD
       |
       v
S4U
       |
       v
Target Service
```

---

# S4U

See:

[S4U](s4u.md)

Delegation-based access may allow service tickets to be obtained for another user under specific conditions.

---

# Shadow Credentials

Control over:

```text
msDS-KeyCredentialLink
```

may allow certificate-based takeover of a user or computer.

See:

[Shadow Credentials](shadow-credentials.md)

That identity can then become another lateral-movement credential.

---

# NTLM Relay

NTLM relay can also establish access to another system without obtaining the victim's plaintext password.

See:

[NTLM Relay](ntlm-relay.md)

Conceptually:

```text
Victim Authentication
       |
       v
Attacker
       |
       v
Relay
       |
       v
Target
```

---

# Authentication Coercion

Relay paths are often combined with authentication coercion.

See:

[Authentication Coercion](authentication-coercion.md)

Conceptually:

```text
Coerce Authentication
       |
       v
Receive Authentication
       |
       v
Relay
       |
       v
Target Service
```

---

# Kerberos Relay

Kerberos authentication can also participate in certain relay scenarios.

See:

[Kerberos Relay](kerberos-relay.md)

Kerberos relay has different constraints from NTLM relay because Kerberos tickets are service-specific.

---

# Name Resolution

Hostname resolution is important when using Kerberos.

Prefer:

```text
srv01.corp.example
```

over:

```text
10.10.10.25
```

when Kerberos authentication is expected.

---

# Why Hostnames Matter

Kerberos service tickets are issued for SPNs such as:

```text
cifs/srv01.corp.example
```

```text
http/srv01.corp.example
```

```text
host/srv01.corp.example
```

Using an IP address can cause authentication to fall back to another mechanism or fail.

---

# Kerberos vs NTLM

A useful troubleshooting question is:

```text
Which Authentication Protocol
Was Actually Used?
```

Do not assume:

```text
Domain Credential
=
Kerberos
```

---

# Kerberos Requirements

Typical Kerberos requirements include:

```text
DNS
SPN
Time Synchronisation
KDC Reachability
Correct Domain
Valid Ticket
```

---

# Time Synchronisation

Kerberos is sensitive to clock skew.

Linux:

```bash
timedatectl
```

Windows:

```cmd
w32tm /query /status
```

---

# DNS

Linux:

```bash
nslookup srv01.corp.example
```

or:

```bash
dig srv01.corp.example
```

Windows:

```powershell
Resolve-DnsName srv01.corp.example
```

---

# Kerberos Ticket Cache

Windows:

```cmd
klist
```

Linux:

```bash
klist
```

Check:

```text
Principal
Ticket Lifetime
Service Principal
Encryption Type
```

---

# Pass-the-Ticket Workflow

Conceptually:

```text
Existing Ticket
      |
      v
Ticket Cache
      |
      v
Kerberos-Aware Tool
      |
      v
Remote Service
```

See:

[Pass the Ticket](pass-the-ticket.md)

---

# Impacket Kerberos Authentication

Many Impacket tools support:

```text
-k
```

for Kerberos authentication.

They may also use:

```text
KRB5CCNAME
```

to locate a Kerberos credential cache.

Example:

```bash
export KRB5CCNAME=./audit-user.ccache
```

Then, depending on the tool:

```bash
impacket-wmiexec -k -no-pass 'CORP.EXAMPLE/audit-user@srv01.corp.example'
```

Always confirm syntax with:

```bash
impacket-wmiexec -h
```

---

# Pass-the-Hash Workflow

```text
NTLM Hash
    |
    v
NTLM-Compatible Protocol
    |
    v
Target
```

Common tools include:

```text
NetExec
Impacket
Evil-WinRM
```

depending on protocol support.

---

# NetExec Pass-the-Hash

```bash
nxc smb srv01.corp.example -u 'audit-admin' -H 'NTHASH'
```

---

# WMIExec Pass-the-Hash

```bash
impacket-wmiexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

---

# Evil-WinRM Pass-the-Hash

```bash
evil-winrm -i srv01.corp.example -u 'audit-admin' -H 'NTHASH'
```

---

# Local vs Domain Accounts

Always determine whether a credential represents:

```text
Local Account
```

or:

```text
Domain Account
```

Example local account:

```text
SRV01\Administrator
```

Domain account:

```text
CORP\Administrator
```

These have very different lateral-movement implications.

---

# NetExec Local Authentication

When testing a local account with NetExec, use the appropriate local-authentication option supported by the installed version.

Check:

```bash
nxc smb -h
```

Look for:

```text
--local-auth
```

A typical pattern is:

```bash
nxc smb srv01.corp.example -u 'Administrator' -p 'PASSWORD' --local-auth
```

---

# UAC Remote Restrictions

Windows applies additional restrictions to some remote administrative operations involving local accounts.

This means:

```text
Local Administrators Group Membership
```

does not always translate directly into:

```text
Full Remote Administrative Token
```

for every account and protocol.

---

# Built-In Administrator

The built-in:

```text
Administrator
```

account can behave differently from other local administrator accounts under UAC remote restrictions.

Account configuration and Windows policy should be evaluated rather than assumed.

---

# Remote Protocol Selection

Do not use one remote-execution method for every target.

Choose based on:

```text
Available Protocol
Credential Type
Privilege
Operational Impact
Detection Objectives
Target Role
Assessment Scope
```

---

# Example Decision Tree

```text
Have Valid Credential?
        |
        +--> No -> Do Not Attempt Remote Execution
        |
        +--> Yes
                |
                v
        Know Administrative Target?
                |
                +--> No -> Enumerate Relationships
                |
                +--> Yes
                        |
                        v
                WinRM Available?
                  |           |
                 Yes          No
                  |           |
                  v           v
               WinRM       SMB Available?
                               |
                         +-----+-----+
                         |           |
                        Yes          No
                         |           |
                         v           v
                     SMB/WMI      Other Protocol
```

---

# Protocol Comparison

| Protocol | Typical Port | Common Use |
|---|---:|---|
| SMB | 445 | File access and remote administration |
| WinRM | 5985/5986 | PowerShell remoting |
| WMI | 135 + RPC | Remote management |
| DCOM | 135 + RPC | COM-based remote management |
| RDP | 3389 | Interactive desktop |
| MSSQL | 1433 or dynamic | Database administration |
| SSH | 22 | Remote shell |
| HTTPS | 443 | Application-specific management |

Ports can be changed.

---

# Prefer Existing Management Channels

If an organisation already permits:

```text
WinRM
```

for administration and your test account is legitimately granted access, using that existing channel may be less intrusive than creating:

```text
Temporary Services
```

through SMB.

---

# Detection - Authentication

Useful Windows events can include:

```text
4624 - Successful Logon
4625 - Failed Logon
4648 - Logon Using Explicit Credentials
4672 - Special Privileges Assigned
```

Interpret them together with:

```text
Logon Type
Source Address
Account
Target
Authentication Package
```

---

# Logon Type 3

Network authentication commonly produces:

```text
Logon Type 3
```

Examples can include:

```text
SMB
Network Resource Access
Remote Administration
```

---

# Logon Type 10

RDP commonly produces:

```text
Logon Type 10
```

for RemoteInteractive logons.

---

# Kerberos Events

Important events include:

```text
4768 - TGT Requested
4769 - Service Ticket Requested
4771 - Kerberos Pre-Authentication Failed
```

---

# NTLM Events

Depending on logging configuration, defenders can use:

```text
NTLM Operational Logs
4624
4776
```

and related telemetry to identify NTLM authentication patterns.

---

# SMB Detection

Useful signals include:

```text
Remote ADMIN$ Access
Remote C$ Access
Service Creation
Named Pipe Activity
File Creation
Remote Process Execution
```

---

# Event 7045

Service installation can generate:

```text
7045
```

in the System log.

This is useful for detecting PsExec-style service creation.

---

# Event 4697

With appropriate auditing:

```text
4697
```

records installation of a service.

---

# Task Scheduler Detection

Remote scheduled-task execution may generate task-related events.

Useful logs include:

```text
Microsoft-Windows-TaskScheduler/Operational
```

and Security auditing where configured.

---

# WMI Detection

Useful sources include:

```text
Microsoft-Windows-WMI-Activity/Operational
Process Creation
Network Telemetry
RPC Activity
```

---

# WinRM Detection

Useful sources include:

```text
Microsoft-Windows-WinRM/Operational
PowerShell Operational
PowerShell Script Block Logging
Process Creation
4624
```

---

# PowerShell Remoting

Remote PowerShell can produce:

```text
wsmprovhost.exe
```

on the target.

This can be useful context when correlating WinRM activity.

---

# RDP Detection

Monitor:

```text
4624 Logon Type 10
RemoteConnectionManager Logs
LocalSessionManager Logs
Network Connections to 3389
```

---

# Detecting Credential Reuse

Look for:

```text
Same Account
      |
      +--> Many Workstations
      +--> Many Servers
      +--> Short Time Window
```

especially where the account does not normally administer those systems.

---

# Detecting Lateral Movement as a Graph

Instead of alerting on isolated events:

```text
Login A
Login B
Login C
```

correlate:

```text
Compromised Host
       |
       v
New Credential
       |
       v
Remote Authentication
       |
       v
New Host
       |
       v
New Privileged Session
```

---

# Administrative Baselines

Defenders should know:

```text
Which Admins Manage Which Systems?
```

Without this baseline, distinguishing legitimate remote administration from lateral movement becomes much harder.

---

# Local Administrator Inventory

Maintain visibility into:

```text
Local Administrators
Remote Desktop Users
Remote Management Users
Service Accounts
Scheduled Task Accounts
```

across endpoints.

---

# Hardening - SMB

Important controls include:

```text
SMB Signing
Host Firewall
Administrative Share Governance
Local Administrator Password Uniqueness
NTLM Reduction
Network Segmentation
```

SMB signing is especially important against:

[NTLM Relay](ntlm-relay.md)

---

# Hardening - WinRM

Restrict:

```text
Who Can Use WinRM
Where WinRM Is Reachable From
Which Authentication Methods Are Allowed
```

Use firewall rules and privileged management networks where appropriate.

---

# Hardening - RDP

Consider:

```text
Network Level Authentication
MFA
Restricted Admin Groups
Privileged Access Workstations
Firewall Restrictions
Jump Hosts
Session Monitoring
```

depending on organisational requirements.

---

# Hardening - WMI and DCOM

Limit remote management access using:

```text
Windows Firewall
Administrative Groups
Network Segmentation
DCOM Hardening
Endpoint Monitoring
```

Do not disable required enterprise management functionality without understanding operational dependencies.

---

# Hardening - Credential Reuse

Use:

```text
Windows LAPS
Managed Service Accounts
gMSA
Unique Service Credentials
Password Rotation
Privileged Identity Separation
```

See:

[LAPS](laps.md)

and:

[gMSA](gmsa.md)

---

# Hardening - NTLM

Reducing NTLM usage limits many:

```text
Pass-the-Hash
Relay
Legacy Authentication
```

attack paths.

However, NTLM restrictions require careful compatibility assessment.

---

# Hardening - Privileged Sessions

Avoid privileged authentication to lower-trust systems.

Conceptually:

```text
Tier 0 Credential
        X
        |
        v
Normal User Workstation
```

---

# Hardening - Network Segmentation

Workstations should not necessarily be able to initiate administrative protocols to:

```text
Every Other Workstation
```

Likewise:

```text
User VLAN
```

should not automatically reach all:

```text
Server Management Ports
```

---

# East-West Filtering

Traditional perimeter security focuses on:

```text
Internet
   |
   v
Enterprise
```

Lateral movement requires attention to:

```text
Host
 |
 v
Host
```

or:

```text
Network Segment
      |
      v
Network Segment
```

This is often called:

```text
East-West Traffic
```

---

# Windows Firewall

Host-based firewall rules can significantly reduce lateral-movement opportunities.

Restrict inbound:

```text
445
5985
5986
3389
135
Dynamic RPC
```

to legitimate management sources.

---

# Management Networks

A stronger model is:

```text
Admin Workstation
       |
       v
Management Network
       |
       v
Server
```

rather than:

```text
Any Workstation
       |
       v
Server Management Port
```

---

# Service Accounts

Service accounts often become important lateral-movement identities because they may have:

```text
Local Administrator Rights
Server Logon Rights
Database Privileges
Network Share Access
Scheduled Tasks
Service Logons
```

---

# gMSA

Where supported, Group Managed Service Accounts can reduce risks associated with reusable service-account passwords.

See:

[gMSA](gmsa.md)

---

# Domain Admin Restrictions

Domain Admins should not be used for routine server administration.

A compromised member server should not automatically expose:

```text
Domain Admin
```

credentials.

---

# Protected Users

The:

```text
Protected Users
```

group can provide additional protections for highly privileged accounts.

Its effects and compatibility should be carefully evaluated before deployment.

---

# Credential Guard

Windows Defender Credential Guard can reduce exposure of certain credentials on compromised endpoints.

It does not eliminate all lateral-movement techniques.

---

# Remote Credential Guard

Remote Credential Guard can help reduce credential exposure during RDP administration in supported scenarios.

---

# Restricted Admin Mode

RDP Restricted Admin mode changes how credentials are handled during remote administration.

It can reduce some credential exposure but also changes authentication behaviour and may have security trade-offs.

Evaluate it within the complete privileged-access design.

---

# Local Administrator Attack Path

A common chain:

```text
Compromised User
      |
      v
Local Admin on WS01
      |
      v
Local Admin Credential Reuse
      |
      v
WS02
      |
      v
Privileged User Session
      |
      v
Higher Privilege
```

---

# Service Account Attack Path

```text
Compromised Server
      |
      v
Service Credential
      |
      v
Same Service Account
on Multiple Servers
      |
      v
Server Estate
```

---

# Kerberos Attack Path

```text
Compromised Identity
      |
      v
Kerberos Ticket
      |
      v
Remote Service
      |
      v
Target Host
```

---

# Relay Attack Path

```text
Authentication Coercion
       |
       v
NTLM Authentication
       |
       v
Relay
       |
       v
Target Service
       |
       v
Privilege
```

---

# Certificate Attack Path

```text
AD CS Abuse
    |
    v
Certificate
    |
    v
Kerberos Authentication
    |
    v
Target Services
```

---

# Graph-Based Lateral Movement

The most effective way to understand lateral movement is often:

```text
Identity Graph
```

rather than:

```text
Host List
```

Example:

```text
Alice
 |
 +--> AdminTo WS01
 |
 v
WS01
 |
 +--> HasSession Bob
 |
 v
Bob
 |
 +--> AdminTo SRV01
 |
 v
SRV01
```

This reveals why seemingly low-value machines can become critical.

---

# Choke Points

Identify systems that connect multiple administrative boundaries.

Examples:

```text
Jump Servers
Management Servers
SCCM
Backup Servers
Monitoring Servers
Virtualisation Platforms
Software Deployment Systems
```

These often provide broader lateral-movement opportunities than ordinary endpoints.

---

# SCCM

Microsoft Configuration Manager can represent a high-value administrative platform because it manages large numbers of systems.

A compromised SCCM administrative path may provide broad endpoint control.

A dedicated SCCM page will cover this in detail:

```text
docs/active-directory/sccm.md
```

---

# Backup Infrastructure

Backup platforms often have privileged access to many servers.

Therefore:

```text
Backup Server
```

should be treated as high-value infrastructure during attack-path analysis.

---

# Virtualisation Infrastructure

Hypervisors and virtualisation management platforms can control:

```text
Domain Controllers
Certificate Authorities
Application Servers
Management Servers
```

Compromise can bypass many guest-level controls.

---

# Monitoring Infrastructure

Monitoring platforms may contain:

```text
Administrative Credentials
Agents
Remote Execution Capability
API Tokens
Service Accounts
```

and should be included in lateral-movement analysis where in scope.

---

# Safe Lateral Movement Workflow

A disciplined workflow is:

```text
Current Identity
      |
      v
Enumerate Rights
      |
      v
Identify Specific Target
      |
      v
Check Network Reachability
      |
      v
Determine Protocol
      |
      v
Test Authentication
      |
      v
Determine Authorisation
      |
      v
Minimal Validation
      |
      v
Record Evidence
      |
      v
Continue Only If Necessary
```

---

# Step 1 - Record Current Identity

Windows:

```cmd
whoami
```

Groups:

```cmd
whoami /groups
```

Privileges:

```cmd
whoami /priv
```

Kerberos tickets:

```cmd
klist
```

---

# Step 2 - Identify Administrative Relationships

Use:

```text
BloodHound
NetExec
Active Directory Queries
Known Server Groups
Local Administrator Enumeration
```

Prefer targeted analysis over blind authentication.

---

# Step 3 - Identify Reachable Protocols

PowerShell:

```powershell
$ports = 445,5985,5986,3389,135

foreach ($port in $ports) {
    Test-NetConnection srv01.corp.example -Port $port -InformationLevel Quiet
}
```

---

# Step 4 - Choose Authentication Material

Determine whether you have:

```text
Password
Hash
Ticket
Key
Certificate
Existing Session
```

Do not unnecessarily convert one credential type into another.

---

# Step 5 - Validate Authentication

Example:

```bash
nxc smb srv01.corp.example -u 'audit-user' -p 'PASSWORD'
```

Authentication success is evidence by itself.

---

# Step 6 - Validate Authorisation

Example:

```bash
nxc smb srv01.corp.example -u 'audit-user' -p 'PASSWORD' --shares
```

Ask:

```text
What Can the Account Actually Access?
```

---

# Step 7 - Minimal Execution

Only if needed:

```bash
impacket-wmiexec 'CORP/audit-admin:PASSWORD@srv01.corp.example' 'whoami'
```

or an equivalent low-impact technique.

---

# Step 8 - Stop When Proven

If the objective was:

```text
Demonstrate Lateral Administrative Access
```

and:

```text
whoami
```

on the remote host proves it:

```text
Stop
```

unless further exploitation is explicitly required.

---

# Evidence Collection

For each lateral-movement path record:

```text
Source Host
Source Identity
Credential Type
Target Host
Target IP
Protocol
Port
Authentication Method
Privilege Level
Command Executed
Result
Timestamp
Security Controls Encountered
Operational Impact
Cleanup
```

---

# Example Evidence

```text
Source:
WS01

Identity:
CORP\audit-admin

Target:
SRV01

Protocol:
WinRM

Port:
5985/TCP

Authentication:
Kerberos

Authorisation:
Local Administrator

Validation:
whoami

Result:
corp\audit-admin

Changes:
None
```

---

# Reporting

Avoid vague findings such as:

```text
Lateral Movement Possible
```

Describe the underlying weakness.

Examples:

```text
Shared Local Administrator Credentials Permit Lateral Movement
```

```text
Excessive Local Administrator Rights Enable Server-to-Server Movement
```

```text
Workstations Can Directly Access Administrative Services on Server Network
```

```text
Privileged Domain Accounts Authenticate to Lower-Trust Workstations
```

---

# Example Finding - Credential Reuse

```text
Finding:
Shared Local Administrator Credentials Permit Lateral Movement

Description:
The same local administrator credential was valid on multiple Windows
systems within the assessed network.

After obtaining administrative access to one test endpoint, the
credential was validated against another approved test endpoint and
provided administrative access.

Impact:
Compromise of a single endpoint may expose credentials that can be
reused to compromise additional systems.

This increases the blast radius of an endpoint compromise and can allow
an attacker to move laterally through the Windows estate.

Recommendation:
Deploy Windows LAPS or another approved mechanism that provides unique,
automatically rotated local administrator credentials for managed
systems.

Restrict remote administrative protocols between peer workstations and
monitor remote administrative authentication.
```

---

# Example Finding - Excessive Domain Rights

```text
Finding:
Domain Account Has Excessive Local Administrative Access Across Servers

Description:
The tested domain account was a local administrator on multiple servers
that were not required for its documented business function.

The account could authenticate remotely and obtain administrative
access to the affected systems.

Impact:
Compromise of the account could allow an attacker to move laterally
across multiple servers, access sensitive data and potentially obtain
additional credentials or privileges.

Recommendation:
Apply least privilege to local administrator membership.

Use dedicated administrative identities and centralised privileged
access management where appropriate.

Review local administrator membership regularly and remove unnecessary
domain users and groups.
```

---

# Example Finding - Network Segmentation

```text
Finding:
User Workstations Can Reach Administrative Services Across Server Network

Description:
Systems in the standard user workstation network were able to directly
reach administrative services on multiple server systems, including
SMB and WinRM.

Impact:
If a workstation is compromised and suitable credentials are obtained,
the attacker can directly attempt lateral movement into the server
environment.

Recommendation:
Restrict administrative protocols using host and network firewalls.

Permit management traffic only from authorised administrative systems
or management networks where operationally possible.
```

---

# Lateral Movement Checklist

## Identity

- [ ] Record current user
- [ ] Record current groups
- [ ] Record current privileges
- [ ] Identify local vs domain identity
- [ ] Review Kerberos tickets
- [ ] Identify available credential material

## Attack Path Analysis

- [ ] Collect BloodHound data where authorised
- [ ] Review AdminTo relationships
- [ ] Review CanRDP relationships
- [ ] Review CanPSRemote relationships
- [ ] Review ExecuteDCOM relationships
- [ ] Review session relationships
- [ ] Identify management servers
- [ ] Identify privileged choke points

## Network

- [ ] Identify target hostname
- [ ] Resolve DNS
- [ ] Check SMB
- [ ] Check WinRM
- [ ] Check RDP
- [ ] Check RPC
- [ ] Check MSSQL where relevant
- [ ] Check SSH where relevant
- [ ] Identify firewall restrictions

## Authentication

- [ ] Determine plaintext credentials
- [ ] Determine NTLM hashes
- [ ] Determine Kerberos tickets
- [ ] Determine Kerberos keys
- [ ] Determine certificates
- [ ] Determine local vs domain credentials
- [ ] Prefer Kerberos where appropriate
- [ ] Avoid unnecessary password spraying

## SMB

- [ ] Test authentication
- [ ] Enumerate shares
- [ ] Check administrative access
- [ ] Identify signing requirements
- [ ] Avoid unnecessary file writes
- [ ] Use remote execution only when required

## WinRM

- [ ] Check 5985
- [ ] Check 5986
- [ ] Test WSMan
- [ ] Determine remoting rights
- [ ] Use minimal commands
- [ ] Record authentication mechanism

## WMI

- [ ] Check RPC reachability
- [ ] Determine WMI access
- [ ] Validate only where required
- [ ] Record remote process activity

## DCOM

- [ ] Check RPC
- [ ] Determine remote activation rights
- [ ] Consider Windows hardening
- [ ] Avoid unnecessary execution

## RDP

- [ ] Check 3389
- [ ] Determine RDP rights
- [ ] Review NLA
- [ ] Review MFA
- [ ] Avoid disrupting existing sessions
- [ ] Avoid unnecessary clipboard or drive sharing

## MSSQL

- [ ] Identify SQL servers
- [ ] Test Windows authentication
- [ ] Determine SQL role
- [ ] Review sysadmin membership
- [ ] Review linked servers
- [ ] Separate database privilege from OS privilege

## Credential Reuse

- [ ] Review local administrator reuse
- [ ] Review service-account reuse
- [ ] Review domain administrator exposure
- [ ] Review LAPS deployment
- [ ] Review gMSA usage

## Safe Validation

- [ ] Use approved targets only
- [ ] Prefer targeted authentication
- [ ] Avoid network-wide credential testing
- [ ] Prefer read-only validation
- [ ] Use `whoami` or `hostname`
- [ ] Avoid payload deployment
- [ ] Avoid persistence
- [ ] Avoid unnecessary credential dumping
- [ ] Avoid production disruption
- [ ] Record cleanup

## Detection

- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4648
- [ ] Monitor 4672
- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Monitor 4771
- [ ] Review NTLM telemetry
- [ ] Monitor ADMIN$ and C$
- [ ] Monitor service creation
- [ ] Monitor 7045
- [ ] Monitor 4697
- [ ] Monitor Task Scheduler
- [ ] Monitor WMI
- [ ] Monitor WinRM
- [ ] Monitor PowerShell
- [ ] Monitor RDP
- [ ] Correlate source and target systems

## Hardening

- [ ] Deploy Windows LAPS
- [ ] Use gMSA where appropriate
- [ ] Remove shared local administrator passwords
- [ ] Apply least privilege
- [ ] Restrict privileged logons
- [ ] Separate administrative identities
- [ ] Use privileged access workstations
- [ ] Segment management traffic
- [ ] Restrict SMB
- [ ] Restrict WinRM
- [ ] Restrict RDP
- [ ] Restrict RPC
- [ ] Harden WMI/DCOM
- [ ] Reduce NTLM
- [ ] Enable SMB signing
- [ ] Deploy Credential Guard where appropriate
- [ ] Monitor privileged sessions
- [ ] Maintain administrative relationship inventory

## Reporting

- [ ] Identify source identity
- [ ] Identify source system
- [ ] Identify target
- [ ] Identify credential type
- [ ] Identify protocol
- [ ] Identify privilege level
- [ ] Explain underlying weakness
- [ ] Document minimal validation
- [ ] Document affected systems
- [ ] Describe realistic attack chain
- [ ] Avoid overstating domain compromise
- [ ] Provide specific remediation

---

# Lateral Movement Testing Model

The fundamental model is:

```text
Identity
   |
   v
Credential
   |
   v
Permission
   |
   v
Protocol
   |
   v
Target
```

The administrative model is:

```text
Compromised User
      |
      v
AdminTo
      |
      v
Computer
      |
      v
Remote Management
      |
      v
Administrative Access
```

The credential cascade is:

```text
Host A
 |
 v
Credential A
 |
 v
Host B
 |
 v
Credential B
 |
 v
Host C
```

The BloodHound model is:

```text
User
 |
 +--> AdminTo
 |
 v
Computer A
 |
 +--> HasSession
 |
 v
Privileged User
 |
 +--> AdminTo
 |
 v
Computer B
```

The protocol model is:

```text
Credential
    |
    +--> SMB
    |
    +--> WinRM
    |
    +--> WMI
    |
    +--> DCOM
    |
    +--> RDP
    |
    +--> MSSQL
    |
    +--> SSH
```

The authentication model is:

```text
Password
   |
   +--> Kerberos
   |
   +--> NTLM
```

or:

```text
NTLM Hash
   |
   v
NTLM
```

or:

```text
Kerberos Ticket
   |
   v
Kerberos
```

or:

```text
Certificate
   |
   v
PKINIT
   |
   v
Kerberos
```

The safe-validation model is:

```text
Find Target
    |
    v
Test Authentication
    |
    v
Confirm Authorisation
    |
    v
Evidence Sufficient?
    |
    +--> Yes -> Stop
    |
    +--> No
            |
            v
      Minimal Execution
            |
            v
         whoami
            |
            v
           Stop
```

The defensive model is:

```text
Unique Credentials
       +
Least Privilege
       +
Administrative Tiering
       +
Network Segmentation
       +
Protocol Hardening
       +
Credential Protection
       +
Detection
       =
Reduced Lateral Movement
```

For penetration testers:

```text
Do Not Ask:
"Which remote execution tool
can I run everywhere?"

Ask:
"Which identity-to-system relationship
allows my current principal to reach
the next security boundary?"
```

For defenders:

```text
Do Not Ask:
"Did someone run PsExec?"

Ask:
"Can one compromised identity or host
cross administrative boundaries that
should be isolated?"
```

The complete lateral-movement relationship is:

```text
Initial Access
      |
      v
Identity / Credential
      |
      v
Administrative Relationship
      |
      v
Remote Protocol
      |
      v
Target System
      |
      v
Additional Access
      |
      v
New Identity / Credential
      |
      v
Further Movement
```

---

# Related Notes

Active Directory overview:

[Active Directory](index.md)

Active Directory enumeration:

[Enumeration](enumeration.md)

BloodHound:

[BloodHound](bloodhound.md)

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

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

Credential Access:

[Credential Access](credential-access.md)

LAPS:

[LAPS](laps.md)

gMSA:

[gMSA](gmsa.md)

RBCD:

[RBCD](rbcd.md)

S4U:

[S4U](s4u.md)

Shadow Credentials:

[Shadow Credentials](shadow-credentials.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

Kerberos Relay:

[Kerberos Relay](kerberos-relay.md)

Authentication Coercion:

[Authentication Coercion](authentication-coercion.md)

The next detailed lateral-movement page is:

```text
docs/active-directory/smb.md
```

---

# References

## Microsoft - Windows Authentication

[Microsoft - Windows Authentication Technical Overview](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/windows-authentication-technical-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - PowerShell Remoting

[Microsoft - About Remote Requirements](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_remote_requirements){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows Remote Management

[Microsoft - Windows Remote Management](https://learn.microsoft.com/en-us/windows/win32/winrm/portal){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows LAPS

[Microsoft - Windows LAPS Overview](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Credential Guard

[Microsoft - Credential Guard Overview](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Remote Credential Guard

[Microsoft - Remote Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/remote-credential-guard){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }

Use:

```bash
nxc --version
nxc --help
```

to verify syntax for the installed version.

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

Relevant utilities include:

```text
psexec
smbexec
wmiexec
atexec
mssqlclient
```

depending on the required protocol and validation objective.

---

## Evil-WinRM

[Evil-WinRM](https://github.com/Hackplayers/evil-winrm){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound](https://github.com/SpecterOps/BloodHound){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Lateral Movement

[MITRE ATT&CK - Lateral Movement](https://attack.mitre.org/tactics/TA0008/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Remote Services

[MITRE ATT&CK - Remote Services](https://attack.mitre.org/techniques/T1021/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Lateral movement is not fundamentally about:

```text
PsExec
```

or:

```text
WinRM
```

or:

```text
WMI
```

Those are merely mechanisms.

The underlying security relationship is:

```text
Identity
   |
   v
Credential
   |
   v
Administrative Permission
   |
   v
Reachable Remote Service
```

A mature Active Directory assessment therefore starts by understanding:

```text
Who Can Administer What?
```

rather than blindly attempting remote execution.

BloodHound, Active Directory enumeration and controlled authentication can reveal these relationships before intrusive activity is required.

The most important defensive principle is reducing:

```text
Blast Radius
```

A single compromised workstation should not automatically provide a path to:

```text
Other Workstations
Servers
Management Infrastructure
Domain Controllers
Certificate Authorities
```

The strongest defensive model combines:

```text
Unique Credentials
        |
        v
Least Privilege
        |
        v
Administrative Separation
        |
        v
Network Segmentation
        |
        v
Credential Protection
        |
        v
Monitoring
```

For authorised testing, always use the least intrusive technique that proves the attack path.

If:

```text
Authentication Success
```

proves the weakness, stop there.

If:

```text
Administrative Share Access
```

proves it, stop there.

If remote execution is required:

```text
whoami
```

or:

```text
hostname
```

is usually enough.

The goal is not to create the largest possible footprint.

The goal is to establish:

```text
Current Identity
      |
      v
Can Cross Security Boundary
      |
      v
Target System
```

and then explain why that boundary exists, how an attacker could abuse it and how the organisation can prevent the same movement.

The next page focuses specifically on one of the most important Windows protocols in this process:

```text
SMB
```
