# Active Directory WinRM - PowerShell Remoting and Lateral Movement

Windows Remote Management (WinRM) is Microsoft's implementation of the WS-Management protocol and is commonly used for remote administration of Windows systems.

In Active Directory environments, WinRM is especially important because it provides a legitimate administrative channel that can also become a lateral-movement path when an attacker controls an identity with remote-management privileges.

Typical uses include:

```text
PowerShell Remoting
Remote Administration
Configuration Management
Server Management
Automation
Command Execution
Administrative Scripting
```

From an offensive-security perspective, the fundamental relationship is:

```text
Compromised Identity
        |
        v
WinRM Access
        |
        v
Remote PowerShell
        |
        v
Target System
```

WinRM access should therefore be analysed as an **authorisation relationship**, not simply as an open network port.

!!! warning "Authorised testing only"
    WinRM provides legitimate remote command execution. Only authenticate to systems included in the assessment scope and only use credentials you are authorised to test. Prefer harmless commands such as `whoami` and `hostname` when execution must be demonstrated.

---

# WinRM at a Glance

The basic architecture is:

```text
Administrator
      |
      v
WinRM Client
      |
      v
WS-Management
      |
      v
WinRM Service
      |
      v
Windows Host
```

PowerShell Remoting commonly uses:

```text
PowerShell
    |
    v
WinRM
    |
    v
Remote PowerShell Session
```

---

# Default WinRM Ports

The standard WinRM ports are:

```text
5985/TCP - HTTP
5986/TCP - HTTPS
```

These are the first ports to check during WinRM discovery.

---

# WinRM HTTP

WinRM commonly listens on:

```text
TCP 5985
```

The transport is HTTP.

This does **not** mean credentials are simply transmitted as plaintext.

Authentication mechanisms such as:

```text
Kerberos
NTLM
Negotiate
```

provide authentication protection independently of the HTTP transport.

However, HTTPS provides additional transport protection and is preferable in environments where TLS is required.

---

# WinRM HTTPS

WinRM over HTTPS normally uses:

```text
TCP 5986
```

and requires a suitable server certificate.

Conceptually:

```text
Client
  |
  v
TLS
  |
  v
WinRM
  |
  v
Target
```

---

# Check WinRM Connectivity from Windows

Test HTTP:

```powershell
Test-NetConnection srv01.corp.example -Port 5985
```

Test HTTPS:

```powershell
Test-NetConnection srv01.corp.example -Port 5986
```

Example:

```text
ComputerName     : srv01.corp.example
RemoteAddress    : 10.10.10.25
RemotePort       : 5985
TcpTestSucceeded : True
```

---

# Check WinRM from Linux

Using Nmap:

```bash
nmap -Pn -p5985,5986 srv01.corp.example
```

For an approved target range:

```bash
nmap -Pn -p5985,5986 10.10.10.0/24
```

---

# WinRM Endpoint

A typical HTTP endpoint is:

```text
http://srv01.corp.example:5985/wsman
```

HTTPS:

```text
https://srv01.corp.example:5986/wsman
```

The `/wsman` endpoint is expected for WinRM.

---

# Test-WSMan

PowerShell provides:

```powershell
Test-WSMan
```

Example:

```powershell
Test-WSMan srv01.corp.example
```

This can verify whether the target responds to WS-Management.

---

# Example Test-WSMan Output

Typical output may contain:

```text
wsmid
ProtocolVersion
ProductVendor
ProductVersion
```

A successful response confirms:

```text
WinRM Reachable
```

It does not prove that the current user has permission to establish a remote PowerShell session.

---

# WinRM Authentication

Common WinRM authentication mechanisms include:

```text
Kerberos
Negotiate
NTLM
Certificate
CredSSP
Basic
```

Availability depends on:

```text
Client Configuration
Server Configuration
Domain Membership
Transport
Policy
Authentication Method
```

---

# Kerberos

In a normal Active Directory environment, Kerberos is generally the preferred authentication mechanism.

Conceptually:

```text
Domain User
    |
    v
KDC
    |
    v
HTTP Service Ticket
    |
    v
WinRM
```

---

# WinRM SPN

Kerberos authentication for WinRM commonly involves HTTP-related SPNs.

Examples can include:

```text
HTTP/srv01
HTTP/srv01.corp.example
```

The exact SPN behaviour depends on the environment and configuration.

---

# Why Hostnames Matter

Prefer:

```text
srv01.corp.example
```

instead of:

```text
10.10.10.25
```

when Kerberos authentication is expected.

Kerberos relies on:

```text
DNS
SPNs
KDC
Time Synchronisation
```

Using an IP address can cause Kerberos authentication to fail or another authentication mechanism to be selected.

---

# NTLM

If Kerberos cannot be used and NTLM is permitted:

```text
WinRM
  |
  v
NTLM
```

may be used.

This becomes relevant for:

```text
Pass-the-Hash
NTLM Reduction
Authentication Monitoring
Relay Analysis
```

---

# Negotiate

PowerShell Remoting frequently uses:

```text
Negotiate
```

which allows Windows to negotiate an appropriate authentication protocol.

In a healthy domain scenario this will often result in:

```text
Kerberos
```

when Kerberos requirements are satisfied.

---

# Basic Authentication

Basic authentication should be treated carefully.

It relies on transport protection such as HTTPS to protect credentials in transit.

Review server configuration rather than assuming Basic authentication is enabled.

---

# CredSSP

Credential Security Support Provider can delegate credentials to a remote system.

Conceptually:

```text
Client Credential
       |
       v
Remote Host
       |
       v
Second Resource
```

This can solve certain multi-hop authentication problems but increases credential exposure considerations.

Use CredSSP only when its delegation behaviour is understood and required.

---

# The Double-Hop Problem

PowerShell Remoting commonly encounters the:

```text
Second Hop Problem
```

Example:

```text
ADMIN-PC
    |
    v
SRV01
    |
    v
FILE01
```

The administrator authenticates to:

```text
SRV01
```

but the remote session may not possess credentials that can automatically authenticate to:

```text
FILE01
```

---

# Why the Second Hop Matters

Suppose:

```powershell
Enter-PSSession -ComputerName srv01.corp.example
```

works.

Inside the remote session:

```powershell
Get-ChildItem '\\files01.corp.example\Finance'
```

may fail because credentials were not delegated for the second network hop.

This behaviour should not automatically be interpreted as:

```text
Access Denied to FILE01
```

The authentication context must be understood.

---

# PowerShell Remoting

The most common native WinRM interface is:

```text
PowerShell Remoting
```

The two important patterns are:

```text
Interactive Session
```

and:

```text
Non-Interactive Remote Command
```

---

# Enter-PSSession

Interactive session:

```powershell
Enter-PSSession -ComputerName srv01.corp.example
```

This attempts to create an interactive PowerShell session on the target.

---

# Exit-PSSession

Leave the remote session:

```powershell
Exit-PSSession
```

---

# Explicit Credentials

Use:

```powershell
$cred = Get-Credential
```

Then:

```powershell
Enter-PSSession -ComputerName srv01.corp.example -Credential $cred
```

This avoids placing the password directly into command history.

---

# Invoke-Command

For a single remote command:

```powershell
Invoke-Command -ComputerName srv01.corp.example -ScriptBlock {
    whoami
}
```

This is often preferable during security testing because:

```text
Connect
   |
   v
Execute Minimal Command
   |
   v
Return Result
   |
   v
Disconnect
```

---

# Multiple Harmless Commands

```powershell
Invoke-Command -ComputerName srv01.corp.example -ScriptBlock {
    hostname
    whoami
}
```

---

# Explicit Credential with Invoke-Command

```powershell
$cred = Get-Credential

Invoke-Command -ComputerName srv01.corp.example -Credential $cred -ScriptBlock {
    hostname
    whoami
}
```

---

# PSSession

Create a reusable session:

```powershell
$session = New-PSSession -ComputerName srv01.corp.example
```

Inspect it:

```powershell
Get-PSSession
```

Use it:

```powershell
Invoke-Command -Session $session -ScriptBlock {
    hostname
}
```

Remove it:

```powershell
Remove-PSSession $session
```

---

# PSSession Lifecycle

```text
New-PSSession
     |
     v
Persistent Remote Session
     |
     +--> Invoke-Command
     |
     +--> Enter-PSSession
     |
     v
Remove-PSSession
```

Clean up test sessions when finished.

---

# WinRM Authorisation

A reachable WinRM service does not mean every domain user can use PowerShell Remoting.

The important question is:

```text
Who Is Authorised?
```

---

# Common Authorised Groups

Depending on configuration, relevant groups can include:

```text
Administrators
Remote Management Users
```

Group Policy and PowerShell session configuration can further restrict access.

---

# Remote Management Users

Check local membership:

```powershell
Get-LocalGroupMember -Group 'Remote Management Users'
```

On systems where `Get-LocalGroupMember` is unavailable:

```cmd
net localgroup "Remote Management Users"
```

---

# Local Administrators

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

or:

```cmd
net localgroup Administrators
```

---

# PowerShell Session Configurations

Inspect:

```powershell
Get-PSSessionConfiguration
```

Common configurations may include:

```text
Microsoft.PowerShell
Microsoft.PowerShell32
```

depending on the system.

---

# Session Configuration Permissions

PowerShell endpoints can have their own permissions.

Therefore:

```text
WinRM Enabled
```

does not necessarily mean:

```text
Every User Can Use Every PowerShell Endpoint
```

---

# Just Enough Administration

PowerShell supports:

```text
JEA
```

or:

```text
Just Enough Administration
```

JEA can expose constrained administrative capabilities without granting unrestricted administrative PowerShell access.

Conceptually:

```text
User
 |
 v
Restricted PowerShell Endpoint
 |
 +--> Approved Command
 +--> Approved Function
 |
 X
 |
 +--> Unrestricted Administration
```

---

# JEA Security Importance

If an organisation uses JEA, do not assume that obtaining a WinRM session means:

```text
Full Shell
```

Review:

```text
Available Commands
Language Restrictions
Run-As Context
Role Capabilities
Endpoint Permissions
```

---

# Check Current PowerShell Language Mode

Inside a session:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible values include:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

Language mode is separate from WinRM authorisation.

---

# NetExec WinRM

NetExec supports WinRM assessment.

Check installed syntax:

```bash
nxc winrm -h
```

Basic authentication validation:

```bash
nxc winrm srv01.corp.example -u 'audit-user' -p 'PASSWORD'
```

---

# NetExec Target List

For an explicitly approved list:

```bash
nxc winrm targets.txt -u 'audit-user' -p 'PASSWORD'
```

Prefer a targeted list rather than unnecessarily authenticating against an entire enterprise range.

---

# Authentication Success vs Administrative Access

Always distinguish:

```text
Valid Credential
```

from:

```text
WinRM Authorised
```

and:

```text
Local Administrator
```

These are different security properties.

---

# Evil-WinRM

Evil-WinRM is commonly used from Linux to interact with Windows systems through WinRM.

Check the installed version and options:

```bash
evil-winrm -h
```

Password authentication:

```bash
evil-winrm -i srv01.corp.example -u 'audit-user' -p 'PASSWORD'
```

---

# Avoid Passwords in Shell History

Where possible, avoid:

```text
-p PASSWORD
```

with real production credentials.

Use secure prompting or approved temporary test credentials when available.

---

# Pass-the-Hash with WinRM

Depending on the authentication configuration and tool, an NTLM hash may be usable for WinRM authentication.

Evil-WinRM supports hash authentication.

Example:

```bash
evil-winrm -i srv01.corp.example -u 'audit-admin' -H 'NTHASH'
```

This is a:

```text
Pass-the-Hash
```

scenario.

See:

[Pass-the-Hash](pass-the-hash.md)

---

# Pass-the-Hash Model

```text
NTLM Hash
    |
    v
NTLM Authentication
    |
    v
WinRM
    |
    v
Remote Session
```

---

# WinRM and Kerberos from Linux

Linux tooling can also authenticate using Kerberos where supported.

Conceptually:

```text
Kerberos Credential Cache
        |
        v
HTTP Service Ticket
        |
        v
WinRM
```

Exact configuration depends on the client tool.

---

# Kerberos Ticket Cache

Check:

```bash
klist
```

Environment:

```bash
echo "$KRB5CCNAME"
```

A credential cache may be configured using:

```bash
export KRB5CCNAME=./audit-user.ccache
```

---

# DNS Requirements

Kerberos-aware WinRM testing depends heavily on correct name resolution.

Check:

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

# Time Synchronisation

Check Linux:

```bash
timedatectl
```

Windows:

```cmd
w32tm /query /status
```

Kerberos authentication can fail when clock skew exceeds acceptable limits.

---

# WinRM TrustedHosts

In workgroup scenarios or situations where Kerberos cannot authenticate the remote system, Windows may use:

```text
TrustedHosts
```

configuration.

Inspect:

```powershell
Get-Item WSMan:\localhost\Client\TrustedHosts
```

---

# TrustedHosts Security

Avoid:

```text
*
```

unless there is a justified and carefully controlled requirement.

A broad TrustedHosts configuration weakens server identity assurance when Kerberos is unavailable.

---

# Do Not Change TrustedHosts Just to Make Testing Easier

During an assessment, do not modify:

```text
TrustedHosts
```

on production systems merely to bypass authentication configuration.

Instead document why the intended authentication method failed.

---

# Inspect WinRM Service

```powershell
Get-Service WinRM
```

Example:

```text
Status   Name   DisplayName
------   ----   -----------
Running  WinRM  Windows Remote Management
```

---

# WinRM Configuration

Display configuration:

```cmd
winrm get winrm/config
```

---

# WinRM Service Configuration

```cmd
winrm get winrm/config/service
```

---

# WinRM Client Configuration

```cmd
winrm get winrm/config/client
```

---

# WinRM Listeners

```cmd
winrm enumerate winrm/config/listener
```

PowerShell alternative:

```powershell
Get-ChildItem WSMan:\localhost\Listener
```

---

# Listener Information

Review:

```text
Transport
Address
Port
Hostname
Certificate Thumbprint
```

---

# HTTP Listener

Typical:

```text
Transport = HTTP
Port = 5985
```

---

# HTTPS Listener

Typical:

```text
Transport = HTTPS
Port = 5986
```

The listener should use an appropriate certificate.

---

# Review Authentication Configuration

```cmd
winrm get winrm/config/service/auth
```

This can reveal whether methods such as:

```text
Basic
Kerberos
Negotiate
Certificate
CredSSP
```

are enabled.

---

# PowerShell WSMan Provider

PowerShell exposes WinRM configuration under:

```text
WSMan:
```

Example:

```powershell
Get-ChildItem WSMan:\localhost\Service\Auth
```

---

# Do Not Use winrm quickconfig During Enumeration

The command:

```cmd
winrm quickconfig
```

can modify the system by:

```text
Starting WinRM
Creating a Listener
Changing Firewall Configuration
```

Therefore, do not run it merely to determine whether WinRM is enabled.

Use read-only commands instead.

---

# Enable-PSRemoting Is Also a Configuration Change

Similarly:

```powershell
Enable-PSRemoting
```

changes the target system.

It may:

```text
Start WinRM
Configure Startup
Create Listeners
Modify Firewall Rules
Enable Session Configurations
```

Do not run it during an assessment unless the change is explicitly authorised.

---

# Remote Command Execution

Once WinRM access has been established:

```text
Remote Command Execution
```

is already proven.

A harmless command is normally sufficient.

---

# Minimal Validation

Recommended:

```powershell
Invoke-Command -ComputerName srv01.corp.example -ScriptBlock {
    whoami
}
```

or:

```powershell
Invoke-Command -ComputerName srv01.corp.example -ScriptBlock {
    hostname
}
```

---

# Why Minimal Validation Matters

If the assessment objective is:

```text
Can This User Execute Commands on SRV01?
```

and the output is:

```text
corp\audit-user
```

then the objective has been proven.

There is usually no need to:

```text
Create User
Disable Defender
Dump Credentials
Deploy Payload
Create Persistence
```

---

# WinRM and Local Administrator Rights

Local administrators frequently have remote-management capabilities, but configuration can affect actual access.

Do not assume:

```text
Local Administrator
=
WinRM Access
```

until tested or confirmed from policy.

---

# UAC Remote Restrictions

Local accounts can be affected by:

```text
UAC Remote Restrictions
```

which may filter administrative tokens during remote access.

This can produce different behaviour between:

```text
Domain Administrator
Domain Account in Local Administrators
Built-In Local Administrator
Other Local Administrator
```

---

# Domain Accounts

A domain account placed in:

```text
Local Administrators
```

on a member server may become a significant lateral-movement identity.

Example:

```text
CORP\Helpdesk
      |
      v
Local Administrators on SRV01
      |
      v
WinRM
      |
      v
Remote Administration
```

---

# Excessive WinRM Rights

An account does not necessarily need full local administrator rights to be security relevant.

For example:

```text
Remote Management Users
```

may provide remote PowerShell access.

The impact depends on what the account can do within that session.

---

# BloodHound

BloodHound can identify WinRM-related relationships.

See:

[BloodHound](bloodhound.md)

A relevant edge can include:

```text
CanPSRemote
```

Conceptually:

```text
User
 |
 v
CanPSRemote
 |
 v
Computer
```

---

# CanPSRemote

A `CanPSRemote` relationship indicates that the principal is expected to have PowerShell Remoting access to the computer based on collected configuration.

Treat it as:

```text
Potential Remote Access
```

and validate only where required.

---

# Example BloodHound Path

```text
Low-Privilege User
        |
        v
CanPSRemote
        |
        v
Application Server
        |
        v
Additional Privilege Path
```

---

# WinRM as a Lateral-Movement Path

A typical sequence:

```text
Compromised User
       |
       v
Enumerate BloodHound
       |
       v
CanPSRemote SRV01
       |
       v
Authenticate through WinRM
       |
       v
Remote Session
       |
       v
Continue Assessment
```

---

# WinRM vs SMB

Both can provide remote administration, but they operate differently.

```text
SMB
 |
 +--> Shares
 +--> Named Pipes
 +--> Service Management
```

WinRM:

```text
WinRM
 |
 +--> WS-Management
 +--> PowerShell Remoting
 +--> Management Operations
```

---

# Prefer Existing Administrative Channels

If WinRM is already legitimately enabled and the account has remote-management rights, WinRM can be a cleaner validation mechanism than creating a temporary service through SMB.

For example:

```text
WinRM
 |
 v
whoami
```

may generate less intrusive system modification than:

```text
SMB
 |
 v
Upload Executable
 |
 v
Create Service
```

This does not mean WinRM is invisible.

It generates extensive telemetry.

---

# WinRM vs RDP

WinRM:

```text
Command-Line / PowerShell
Non-Interactive or Interactive Shell
Automation Friendly
```

RDP:

```text
Graphical Desktop
Interactive Session
Potential User Session Impact
```

For simple command-execution validation, WinRM is often preferable to creating an RDP session.

---

# WinRM vs WMI

WinRM:

```text
WS-Management
PowerShell Remoting
5985 / 5986
```

WMI/DCOM:

```text
RPC / DCOM
135 + Dynamic RPC
```

Modern PowerShell management frequently uses CIM over WS-Man.

---

# CIM over WinRM

PowerShell CIM can use WS-Management.

Example:

```powershell
Get-CimInstance -ClassName Win32_OperatingSystem -ComputerName srv01.corp.example
```

This can provide remote management functionality without an interactive shell.

---

# CIM Session

```powershell
$session = New-CimSession -ComputerName srv01.corp.example
```

Query:

```powershell
Get-CimInstance -CimSession $session -ClassName Win32_OperatingSystem
```

Cleanup:

```powershell
Remove-CimSession $session
```

---

# WinRM and PowerShell Versions

The remote PowerShell environment may differ from the client.

Inside the remote session:

```powershell
$PSVersionTable
```

Review:

```text
PSVersion
PSEdition
OS
WSManStackVersion
```

depending on version.

---

# Constrained Endpoints

A remote session may be intentionally constrained.

For example:

```text
User
 |
 v
WinRM
 |
 v
Restricted Endpoint
 |
 +--> Get-Service
 +--> Restart Approved Service
 |
 X
 |
 +--> Arbitrary Command
```

This can be a valid security design.

---

# Do Not Report WinRM Enabled as a Vulnerability

The presence of:

```text
5985
```

or:

```text
5986
```

is not itself a vulnerability.

WinRM is a legitimate management technology.

Report weaknesses such as:

```text
Excessive WinRM Access
Weak Authentication Configuration
Broad TrustedHosts
Unnecessary Network Exposure
Privileged Credential Exposure
Inadequate Segmentation
Insecure Basic Authentication Configuration
```

---

# WinRM Network Segmentation

A weak architecture:

```text
Every Workstation
      |
      v
Every Server:5985
```

A stronger architecture:

```text
Privileged Admin Workstation
          |
          v
Management Network
          |
          v
Server:5985/5986
```

---

# Restrict Source Systems

Firewall rules can limit WinRM to:

```text
Administrative Jump Hosts
Privileged Access Workstations
Management Servers
Automation Platforms
```

rather than exposing it to every endpoint.

---

# Windows Firewall

Review WinRM-related firewall rules:

```powershell
Get-NetFirewallRule |
    Where-Object DisplayName -Like '*Windows Remote Management*' |
    Select-Object DisplayName,Enabled,Direction,Action
```

---

# Firewall Address Restrictions

Inspect relevant rules in more detail:

```powershell
Get-NetFirewallRule |
    Where-Object DisplayName -Like '*Windows Remote Management*' |
    Get-NetFirewallAddressFilter
```

Review whether remote addresses are:

```text
Any
```

or limited to approved management networks.

---

# WinRM Hardening

A practical WinRM hardening strategy includes:

```text
Restrict Network Exposure
Use Kerberos in Domain Environments
Use HTTPS Where Required
Disable Unnecessary Authentication Methods
Avoid Broad TrustedHosts
Apply Least Privilege
Use JEA Where Appropriate
Separate Administrative Accounts
Use Privileged Administration Workstations
Monitor Remote Sessions
Reduce NTLM
```

---

# Disable Unnecessary Basic Authentication

Review:

```cmd
winrm get winrm/config/service/auth
```

If Basic authentication is unnecessary:

```text
Basic = false
```

is generally preferable.

Any change should be tested for compatibility.

---

# Disable Unnecessary CredSSP

CredSSP should only be enabled where credential delegation is genuinely required.

Review:

```cmd
winrm get winrm/config/service/auth
```

and:

```cmd
winrm get winrm/config/client/auth
```

---

# Avoid Broad TrustedHosts

Review:

```powershell
Get-Item WSMan:\localhost\Client\TrustedHosts
```

Prefer:

```text
Specific Approved Hosts
```

over:

```text
*
```

where TrustedHosts is required.

---

# Least Privilege

Review:

```text
Administrators
Remote Management Users
PowerShell Endpoint ACLs
JEA Roles
Group Policy
```

Remove unnecessary remote-management access.

---

# Dedicated Administrative Identities

Avoid using normal daily accounts for privileged WinRM administration.

Prefer:

```text
Standard User
```

for normal work and:

```text
Dedicated Administrative Identity
```

for server administration.

---

# Privileged Access Workstations

Where appropriate:

```text
Administrative Credential
        |
        v
Privileged Workstation
        |
        v
WinRM
        |
        v
Server
```

Avoid:

```text
Administrative Credential
        |
        v
Normal Internet-Connected Workstation
```

---

# WinRM Detection

WinRM provides useful telemetry across several Windows logging sources.

Important sources include:

```text
Security Log
WinRM Operational Log
PowerShell Operational Log
Process Creation
EDR Telemetry
Network Telemetry
```

---

# WinRM Operational Log

Review:

```text
Microsoft-Windows-WinRM/Operational
```

This log can provide information about WinRM activity and failures.

---

# PowerShell Operational Log

Review:

```text
Microsoft-Windows-PowerShell/Operational
```

This is especially useful when PowerShell Remoting is used.

---

# Script Block Logging

Where enabled, PowerShell Script Block Logging can produce:

```text
4104
```

events.

These can contain executed PowerShell content.

---

# PowerShell Module Logging

Module logging can provide additional visibility into PowerShell command execution.

The exact events depend on logging configuration.

---

# Process Creation

Remote PowerShell sessions commonly involve:

```text
wsmprovhost.exe
```

on the target.

Conceptually:

```text
WinRM
  |
  v
wsmprovhost.exe
  |
  v
Remote PowerShell Activity
```

---

# wsmprovhost.exe

The presence of:

```text
wsmprovhost.exe
```

is not automatically malicious.

It is expected during legitimate PowerShell Remoting.

Detection should consider:

```text
Source Host
User
Parent Process
Commands
Target
Time
Administrative Baseline
```

---

# Authentication Events

Relevant Security events can include:

```text
4624 - Successful Logon
4625 - Failed Logon
4648 - Explicit Credentials
4672 - Special Privileges
```

---

# Network Logons

WinRM authentication commonly produces:

```text
Logon Type 3
```

rather than an interactive desktop logon.

---

# Kerberos Events

Where Kerberos is used:

```text
4768
4769
4771
```

may provide useful context.

---

# NTLM Telemetry

Where NTLM is used, monitor:

```text
NTLM Operational Logs
4624
4776
```

and network telemetry.

---

# Detect Unusual Source Systems

Example:

```text
Normal:
PAW01 -> SRV01:5985

Suspicious:
USER-LAPTOP -> SRV01:5985
```

The same authentication may have very different risk depending on the source system.

---

# Detect WinRM Fan-Out

Potential pattern:

```text
WS01
 |
 +--> SRV01:5985
 +--> SRV02:5985
 +--> SRV03:5985
 +--> SRV04:5985
```

within a short period.

This may indicate:

```text
Automation
Administration
Enumeration
Lateral Movement
```

Context is essential.

---

# Detect New WinRM Usage

A particularly useful detection question is:

```text
Has This User Ever Used WinRM
to This Server Before?
```

New relationships may deserve investigation.

---

# Detect Privileged Account Use

Monitor privileged accounts authenticating through WinRM from unexpected systems.

Example:

```text
Domain Admin
    |
    v
User Workstation
    |
    v
WinRM
    |
    v
Server
```

This may indicate poor privileged-access hygiene even when the activity is legitimate.

---

# WinRM Incident Investigation

When suspicious WinRM activity is identified, investigate:

```text
Source IP
Source Host
Destination Host
Account
Authentication Protocol
Timestamp
Commands
PowerShell Logs
Process Creation
Network Connections
Subsequent Authentication
Credential Access Activity
```

---

# Correlation Model

```text
4624
 |
 v
WinRM Session
 |
 v
wsmprovhost.exe
 |
 v
PowerShell 4104
 |
 v
Command Execution
 |
 v
Subsequent Network Connection
```

This provides much stronger evidence than analysing one event in isolation.

---

# Safe Validation Workflow

A controlled WinRM assessment should follow:

```text
Identify Target
      |
      v
Check 5985 / 5986
      |
      v
Test WSMan
      |
      v
Determine Identity
      |
      v
Determine Authorisation
      |
      v
Minimal Remote Command
      |
      v
Collect Evidence
      |
      v
Disconnect
```

---

# Step 1 - Test Connectivity

```powershell
Test-NetConnection srv01.corp.example -Port 5985
```

---

# Step 2 - Test WSMan

```powershell
Test-WSMan srv01.corp.example
```

---

# Step 3 - Identify Current Identity

```cmd
whoami
```

---

# Step 4 - Review Kerberos

```cmd
klist
```

---

# Step 5 - Attempt Approved Session

```powershell
Enter-PSSession -ComputerName srv01.corp.example
```

---

# Step 6 - Minimal Validation

Inside the session:

```powershell
whoami
hostname
```

---

# Step 7 - Exit

```powershell
Exit-PSSession
```

---

# Step 8 - Record Evidence

Record:

```text
Source Host
Source Account
Target Host
Target IP
Port
Transport
Authentication Method
Authorisation
Command
Result
Timestamp
Changes
```

---

# Example Evidence

```text
Source:
ADMIN-WS01

Identity:
CORP\audit-admin

Target:
SRV01

Port:
5985/TCP

Protocol:
WinRM / WS-Management

Authentication:
Kerberos

Validation:
whoami
hostname

Result:
corp\audit-admin
SRV01

Changes:
None

Session:
Closed after validation
```

---

# Reporting

Avoid findings such as:

```text
WinRM Enabled
```

or:

```text
Port 5985 Open
```

without a security weakness.

Instead report the underlying problem.

---

# Example Finding - Excessive WinRM Rights

```text
Finding:
Standard Domain Account Has Unnecessary WinRM Access to Server

Description:
The tested standard domain account was able to establish a PowerShell
Remoting session to SRV01 through WinRM.

The account's documented business role did not require remote
administration of this server.

A harmless `whoami` command was executed to confirm remote command
execution. No configuration changes were made.

Impact:
Compromise of the affected domain account could provide an attacker
with remote command execution on SRV01.

This could enable access to server data, additional credentials or
further lateral movement depending on the privileges available on the
target.

Recommendation:
Review membership of local administrative and Remote Management Users
groups and remove unnecessary accounts.

Restrict WinRM network access to approved administrative systems and
management networks.

Use dedicated administrative identities for remote server management.
```

---

# Example Finding - Broad WinRM Network Exposure

```text
Finding:
WinRM Administrative Interface Reachable from Standard Workstation Network

Description:
Standard user workstations were able to establish network connections
to the WinRM service on multiple server systems over TCP 5985.

Although authentication is still required, this exposes a remote
administrative interface directly to lower-trust workstation networks.

Impact:
If a workstation or suitable domain credential is compromised, an
attacker can directly attempt WinRM authentication against the affected
servers.

This reduces the network controls available to contain lateral
movement.

Recommendation:
Restrict inbound WinRM access using host and network firewalls.

Permit remote administration only from approved administrative
workstations, jump hosts, management servers or dedicated management
networks where operationally possible.
```

---

# Example Finding - Broad TrustedHosts

```text
Finding:
WinRM TrustedHosts Configuration Trusts All Remote Systems

Description:
The WinRM client configuration contained a wildcard TrustedHosts value.

This configuration permits the client to treat any destination as a
trusted WinRM host in scenarios where Kerberos cannot provide mutual
authentication.

Impact:
The configuration weakens remote-server identity assurance for
non-Kerberos WinRM connections and increases the risk associated with
connecting to untrusted systems.

Recommendation:
Remove the wildcard TrustedHosts configuration.

Where TrustedHosts is genuinely required, restrict it to specific
approved systems and prefer Kerberos or appropriately configured HTTPS
for remote administration.
```

---

# Example Finding - Privileged Account Exposure

```text
Finding:
Privileged Accounts Use WinRM from Lower-Trust Workstations

Description:
Privileged server administration accounts were observed establishing
WinRM sessions from standard user workstations.

These workstations are exposed to normal user activity and therefore
represent a lower-trust administrative environment.

Impact:
Compromise of a workstation may expose privileged authentication
material or provide an attacker with an opportunity to abuse an active
administrative session.

Recommendation:
Perform privileged administration from dedicated hardened
administrative workstations or approved jump hosts.

Separate standard and privileged identities and restrict privileged
WinRM access to designated management systems.
```

---

# WinRM Assessment Checklist

## Discovery

- [ ] Check TCP 5985
- [ ] Check TCP 5986
- [ ] Test WSMan
- [ ] Identify HTTP listener
- [ ] Identify HTTPS listener
- [ ] Record target hostname
- [ ] Record target IP
- [ ] Resolve DNS

## Authentication

- [ ] Determine Kerberos availability
- [ ] Determine NTLM availability
- [ ] Review Negotiate
- [ ] Review Basic authentication
- [ ] Review CredSSP
- [ ] Review certificate authentication
- [ ] Determine actual authentication protocol
- [ ] Avoid unnecessary credential testing

## Kerberos

- [ ] Use hostname rather than IP
- [ ] Verify DNS
- [ ] Verify time synchronisation
- [ ] Review ticket cache
- [ ] Review HTTP service ticket
- [ ] Review SPN configuration where necessary

## Authorisation

- [ ] Review local Administrators
- [ ] Review Remote Management Users
- [ ] Review PowerShell endpoint permissions
- [ ] Review JEA endpoints
- [ ] Review Group Policy
- [ ] Review BloodHound CanPSRemote relationships

## Configuration

- [ ] Review WinRM service
- [ ] Review listeners
- [ ] Review authentication methods
- [ ] Review TrustedHosts
- [ ] Review firewall rules
- [ ] Review allowed source networks
- [ ] Review HTTP vs HTTPS
- [ ] Review certificate configuration for HTTPS

## PowerShell Remoting

- [ ] Test only approved targets
- [ ] Prefer `Invoke-Command` for minimal validation
- [ ] Use `whoami`
- [ ] Use `hostname`
- [ ] Avoid unnecessary interactive sessions
- [ ] Remove PSSessions after testing
- [ ] Record language mode where relevant
- [ ] Identify constrained endpoints

## Linux Tooling

- [ ] Check NetExec version
- [ ] Check `nxc winrm -h`
- [ ] Check Evil-WinRM options
- [ ] Protect passwords from shell history
- [ ] Review Kerberos cache where applicable

## Pass-the-Hash

- [ ] Confirm testing is authorised
- [ ] Determine whether NTLM is permitted
- [ ] Use approved test hash only
- [ ] Record target
- [ ] Record account
- [ ] Stop after sufficient validation
- [ ] Do not expose hashes in reports unnecessarily

## Network Segmentation

- [ ] Determine which networks reach 5985
- [ ] Determine which networks reach 5986
- [ ] Review workstation-to-server access
- [ ] Review workstation-to-workstation access
- [ ] Review management-network restrictions
- [ ] Review firewall source restrictions

## Safe Validation

- [ ] Use authorised credentials
- [ ] Use authorised targets
- [ ] Prefer read-only checks first
- [ ] Execute only harmless commands
- [ ] Avoid payload deployment
- [ ] Avoid credential dumping
- [ ] Avoid persistence
- [ ] Avoid changing WinRM configuration
- [ ] Do not run `winrm quickconfig`
- [ ] Do not run `Enable-PSRemoting`
- [ ] Close sessions
- [ ] Record cleanup

## Detection

- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4648
- [ ] Monitor 4672
- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Monitor 4771
- [ ] Review WinRM Operational logs
- [ ] Review PowerShell Operational logs
- [ ] Review Script Block Logging
- [ ] Monitor `wsmprovhost.exe`
- [ ] Monitor unusual WinRM source systems
- [ ] Monitor WinRM fan-out
- [ ] Monitor privileged WinRM activity

## Hardening

- [ ] Restrict WinRM network exposure
- [ ] Prefer Kerberos in domain environments
- [ ] Use HTTPS where required
- [ ] Disable unnecessary Basic authentication
- [ ] Disable unnecessary CredSSP
- [ ] Restrict TrustedHosts
- [ ] Apply least privilege
- [ ] Review Remote Management Users
- [ ] Review Administrators
- [ ] Use JEA where appropriate
- [ ] Separate administrative identities
- [ ] Use privileged administrative workstations
- [ ] Reduce NTLM
- [ ] Monitor remote administration

## Reporting

- [ ] Do not report WinRM merely because it is enabled
- [ ] Identify the actual security weakness
- [ ] Identify affected account
- [ ] Identify affected systems
- [ ] Identify transport
- [ ] Identify authentication method
- [ ] Identify authorisation level
- [ ] Record minimal validation
- [ ] Explain lateral-movement impact
- [ ] Provide targeted remediation

---

# WinRM Testing Model

The service model is:

```text
Client
  |
  v
5985 / 5986
  |
  v
WinRM
  |
  v
Windows Host
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
WinRM
```

The Kerberos model is:

```text
User
 |
 v
KDC
 |
 v
HTTP Service Ticket
 |
 v
WinRM
```

The PowerShell model is:

```text
PowerShell
    |
    v
WS-Management
    |
    v
WinRM
    |
    v
Remote PowerShell
```

The authorisation model is:

```text
Authenticated User
       |
       v
WinRM Endpoint Permission
       |
       v
Remote Session
```

The BloodHound model is:

```text
User
 |
 v
CanPSRemote
 |
 v
Computer
```

The Pass-the-Hash model is:

```text
NTLM Hash
    |
    v
NTLM
    |
    v
WinRM
    |
    v
Remote Session
```

The second-hop model is:

```text
Client
  |
  v
Server A
  |
  X
  |
  v
Server B
```

unless suitable credential delegation or another authentication strategy is configured.

The safe-testing model is:

```text
Discover WinRM
      |
      v
Test Authentication
      |
      v
Confirm Authorisation
      |
      v
Invoke-Command
      |
      v
whoami
      |
      v
Evidence Sufficient
      |
      v
Stop
```

The network-hardening model is:

```text
Normal Workstation
        |
        X
        |
        v
Server WinRM

Privileged Admin Workstation
        |
        v
Management Network
        |
        v
Server WinRM
```

The defensive model is:

```text
Kerberos
   +
Restricted Network Access
   +
Least Privilege
   +
Administrative Separation
   +
JEA
   +
Secure Authentication
   +
PowerShell Logging
   +
WinRM Monitoring
   =
Reduced WinRM Attack Surface
```

For penetration testers:

```text
Do Not Ask:
"Can I get Evil-WinRM?"

Ask:
"Why is this identity authorised
to remotely manage this system?"
```

For defenders:

```text
Do Not Ask:
"Should we disable WinRM everywhere?"

Ask:
"Which identities and management systems
should be allowed to use WinRM,
and can we enforce that boundary?"
```

The complete relationship is:

```text
Identity
   |
   v
Authentication
   |
   v
WinRM Authorisation
   |
   v
PowerShell / WS-Management
   |
   v
Remote System
   |
   v
Administrative Capability
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Active Directory Enumeration:

[Enumeration](enumeration.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

SMB:

[SMB](smb.md)

NetExec:

[NetExec](netexec.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

BloodHound:

[BloodHound](bloodhound.md)

The next detailed lateral-movement page is:

```text
docs/active-directory/wmi.md
```

---

# References

## Microsoft - Windows Remote Management

[Microsoft - Windows Remote Management](https://learn.microsoft.com/en-us/windows/win32/winrm/portal){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Installation and Configuration for Windows Remote Management

[Microsoft - WinRM Installation and Configuration](https://learn.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - PowerShell Remoting

[Microsoft - About Remote](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_remote){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - PowerShell Remoting Requirements

[Microsoft - About Remote Requirements](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_remote_requirements){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Second Hop

[Microsoft - Making the Second Hop in PowerShell Remoting](https://learn.microsoft.com/en-us/powershell/scripting/security/remoting/ps-remoting-second-hop){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Just Enough Administration

[Microsoft - Just Enough Administration](https://learn.microsoft.com/en-us/powershell/scripting/security/remoting/jea/overview){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }

Verify current syntax using:

```bash
nxc winrm -h
```

---

## Evil-WinRM

[Evil-WinRM](https://github.com/Hackplayers/evil-winrm){ target="_blank" rel="noopener noreferrer" }

Verify installed syntax using:

```bash
evil-winrm -h
```

---

## BloodHound

[BloodHound](https://github.com/SpecterOps/BloodHound){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Windows Remote Management

[MITRE ATT&CK - Windows Remote Management](https://attack.mitre.org/techniques/T1021/006/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - PowerShell

[MITRE ATT&CK - PowerShell](https://attack.mitre.org/techniques/T1059/001/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

WinRM is not inherently insecure.

It is a legitimate Windows administration technology used by:

```text
Administrators
Automation
Configuration Management
Server Management
PowerShell Remoting
```

The security question is not:

```text
Is 5985 Open?
```

The important questions are:

```text
Who Can Reach It?

Who Can Authenticate?

Which Authentication Protocol Is Used?

Who Is Authorised for Remote Management?

What Privileges Does the Remote Session Have?

Which Systems Can Initiate WinRM?

Are Privileged Credentials Properly Separated?
```

A secure architecture should look more like:

```text
Privileged Identity
       |
       v
Hardened Administrative Workstation
       |
       v
Restricted Management Network
       |
       v
WinRM
       |
       v
Approved Server
```

rather than:

```text
Any User Workstation
       |
       v
WinRM
       |
       v
Every Server
```

For authorised testing, the preferred validation sequence is:

```text
5985 / 5986
     |
     v
Test-WSMan
     |
     v
Authentication
     |
     v
Authorisation
     |
     v
whoami
     |
     v
Stop
```

If:

```text
whoami
```

demonstrates remote execution with the affected identity, the lateral-movement capability has normally been proven.

There is no need to deploy additional payloads simply to demonstrate the same access.

The underlying finding should focus on:

```text
Identity
   |
   v
Unnecessary Remote Management Right
   |
   v
Target
```

or:

```text
Lower-Trust Network
       |
       v
Administrative WinRM Interface
```

rather than on the particular client used to access WinRM.

Tools such as:

```text
PowerShell Remoting
NetExec
Evil-WinRM
```

are mechanisms for validating the relationship.

The security issue is the relationship itself.

The next page examines remote administration through:

```text
WMI
```
