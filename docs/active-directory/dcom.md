# Active Directory DCOM - Remote Administration and Lateral Movement

Distributed Component Object Model (DCOM) is Microsoft's technology for allowing Component Object Model (COM) objects to communicate across process and network boundaries.

DCOM is used by legitimate Windows components and management technologies for:

```text
Remote Administration
Distributed Applications
Management Services
Enterprise Software
WMI
Microsoft Management Console
Application Automation
RPC-Based Communication
```

During an Active Directory security assessment, DCOM is important because an identity with sufficient remote permissions may be able to activate or interact with COM objects on another Windows system.

Some COM objects expose methods that can indirectly start processes or applications.

The resulting relationship can become:

```text
Compromised Identity
        |
        v
Remote DCOM Access
        |
        v
Remote COM Object
        |
        v
Exposed Method
        |
        v
Process / Application
        |
        v
Target System
```

DCOM should therefore be understood as a legitimate Windows infrastructure technology that can become a lateral-movement mechanism when combined with excessive privileges and network reachability.

!!! warning "Authorised testing only"
    DCOM can invoke functionality on remote Windows systems and may create processes or applications. Begin with configuration and permission review. Only perform remote activation or execution testing against systems explicitly included in the assessment scope, and stop after sufficient evidence has been collected.

---

# DCOM at a Glance

The basic architecture is:

```text
Client
  |
  v
COM Request
  |
  v
RPC
  |
  v
DCOM
  |
  v
Remote COM Object
  |
  v
Windows Component
```

From a lateral-movement perspective:

```text
Identity
   |
   v
Network Reachability
   |
   v
Authentication
   |
   v
DCOM Permissions
   |
   v
Remote Activation
   |
   v
COM Method
   |
   v
Remote Action
```

---

# COM

COM stands for:

```text
Component Object Model
```

COM allows software components to expose:

```text
Objects
Interfaces
Methods
Properties
```

to other applications.

Conceptually:

```text
Application
    |
    v
COM Object
    |
    +--> Method A
    +--> Method B
    +--> Property A
```

---

# DCOM

DCOM extends COM across machine boundaries.

Conceptually:

```text
COM
 |
 v
Local Component Interaction
```

becomes:

```text
DCOM
 |
 v
Remote Component Interaction
```

---

# COM vs DCOM

A useful distinction is:

```text
COM
=
Component interaction
```

while:

```text
DCOM
=
Distributed COM interaction over RPC
```

A COM object may support local activation without being remotely usable through DCOM.

---

# DCOM and Active Directory

DCOM is not an Active Directory protocol itself.

However, in domain environments it frequently relies on:

```text
Domain Identities
Kerberos
NTLM
Windows Groups
Local Administrators
Group Policy
RPC
```

This makes it relevant to Active Directory lateral movement.

---

# DCOM and RPC

DCOM uses:

```text
RPC
```

for remote communication.

A simplified network flow is:

```text
Client
  |
  v
TCP 135
  |
  v
RPC Endpoint Mapper
  |
  v
Dynamic RPC Port
  |
  v
DCOM Server
```

---

# TCP 135

The RPC Endpoint Mapper commonly listens on:

```text
135/TCP
```

Test from Windows:

```powershell
Test-NetConnection srv01.corp.example -Port 135
```

From Linux:

```bash
nmap -Pn -p135 srv01.corp.example
```

---

# TCP 135 Does Not Prove DCOM Access

An open:

```text
135/TCP
```

only indicates that the RPC Endpoint Mapper is reachable.

Successful DCOM interaction still depends on:

```text
Dynamic RPC Reachability
Authentication
Launch Permissions
Activation Permissions
Access Permissions
Object Availability
Object-Specific Security
```

---

# Dynamic RPC

After contacting the RPC Endpoint Mapper, the client may be directed to another TCP port.

Conceptually:

```text
Client
  |
  v
135/TCP
  |
  v
Endpoint Mapper
  |
  v
Dynamic Port
  |
  v
Remote COM Server
```

This is why allowing only:

```text
135/TCP
```

is generally insufficient for full DCOM functionality.

---

# DCOM Authentication

DCOM uses Windows authentication.

Depending on the environment, authentication may involve:

```text
Kerberos
NTLM
```

---

# Kerberos

In a properly functioning domain environment:

```text
Domain Identity
      |
      v
Kerberos
      |
      v
RPC / DCOM
      |
      v
Remote Host
```

may be used.

Correct:

```text
DNS
SPNs
Time Synchronisation
Domain Trust
```

remain important.

---

# NTLM

Where Kerberos cannot be used and NTLM remains available:

```text
Identity
   |
   v
NTLM
   |
   v
RPC / DCOM
```

may occur.

This makes DCOM relevant to broader:

```text
NTLM Reduction
Credential Reuse
Pass-the-Hash
Lateral Movement
```

analysis.

See:

[NTLM](ntlm.md)

---

# Hostnames vs IP Addresses

When Kerberos is expected, prefer:

```text
srv01.corp.example
```

instead of:

```text
10.10.10.25
```

Using an IP address can alter authentication behaviour because Kerberos normally depends on service names rather than raw IP addresses.

---

# DCOM Security

DCOM access is controlled through several permission categories.

Important concepts include:

```text
Access Permissions
Launch Permissions
Activation Permissions
```

---

# Remote Access

Remote Access determines whether a principal can access a running COM server remotely.

Conceptually:

```text
User
 |
 v
Remote Access Permission
 |
 v
Running COM Object
```

---

# Remote Launch

Remote Launch determines whether a principal can remotely start the COM server.

Conceptually:

```text
User
 |
 v
Remote Launch
 |
 v
COM Server Starts
```

---

# Remote Activation

Remote Activation determines whether a principal can remotely activate a COM object.

Conceptually:

```text
User
 |
 v
Remote Activation
 |
 v
COM Object Instance
```

---

# Permission Model

The effective DCOM path can therefore resemble:

```text
Identity
   |
   v
Authentication
   |
   v
Remote Launch
   |
   v
Remote Activation
   |
   v
Remote Access
   |
   v
COM Object
```

Object-specific security can add further restrictions.

---

# Local Administrators

Members of:

```text
Administrators
```

typically have broad remote management capabilities.

A compromised account with local administrator rights on another Windows host should therefore be evaluated for multiple lateral-movement mechanisms, including:

```text
SMB
WinRM
WMI
DCOM
RDP
```

depending on network and system configuration.

---

# DCOM Is Not the Root Cause

If a domain group has:

```text
Local Administrator
```

rights across hundreds of servers, the primary issue is usually:

```text
Excessive Administrative Privilege
```

rather than:

```text
DCOM Exists
```

DCOM is one mechanism through which that privilege may be exercised.

---

# DCOM Configuration

Windows provides:

```text
Component Services
```

for viewing COM and DCOM configuration.

The graphical path is commonly:

```text
Component Services
  |
  v
Computers
  |
  v
My Computer
  |
  v
DCOM Config
```

---

# DCOMCNFG

The Component Services interface can be opened with:

```cmd
dcomcnfg.exe
```

During an assessment, use it for inspection rather than modifying permissions.

---

# Registry Locations

COM and DCOM registrations are represented in the Windows Registry.

Important areas include:

```text
HKEY_CLASSES_ROOT\CLSID
HKEY_LOCAL_MACHINE\SOFTWARE\Classes\CLSID
HKEY_CLASSES_ROOT\AppID
HKEY_LOCAL_MACHINE\SOFTWARE\Classes\AppID
```

---

# CLSID

A:

```text
CLSID
```

identifies a COM class.

Example format:

```text
{00000000-0000-0000-0000-000000000000}
```

The actual value uniquely identifies a registered COM class.

---

# AppID

An:

```text
AppID
```

can associate COM classes with configuration including DCOM security settings.

Conceptually:

```text
CLSID
  |
  v
COM Class
  |
  v
AppID
  |
  v
DCOM Configuration
```

---

# Enumerate COM Registrations

PowerShell can inspect registered COM classes through the Registry.

Example:

```powershell
Get-ChildItem 'Registry::HKEY_CLASSES_ROOT\CLSID' |
    Select-Object -First 20
```

This is local enumeration.

Do not treat every registered COM class as remotely exploitable.

---

# Why COM Enumeration Is Difficult

Windows contains a very large number of COM registrations.

Most are:

```text
Not Useful for Remote Execution
Not Remotely Activatable
Restricted
Application-Specific
Version-Specific
```

Therefore:

```text
Enumerate Every CLSID
```

is usually less useful than:

```text
Understand the Target
Review Permissions
Identify Known Administrative Components
Validate Only Relevant Objects
```

---

# DCOM Lateral Movement

DCOM lateral movement generally requires:

```text
Valid Credential
      +
Network Reachability
      +
Remote DCOM Permissions
      +
Suitable COM Object
```

Conceptually:

```text
Credential
   |
   v
Remote Authentication
   |
   v
DCOM
   |
   v
COM Object
   |
   v
Execution-Capable Method
```

---

# Commonly Discussed DCOM Objects

Security research has historically identified several COM objects that can expose methods useful for remote execution in certain Windows versions and configurations.

Examples include objects associated with:

```text
MMC20.Application
ShellWindows
ShellBrowserWindow
```

Availability and behaviour can vary significantly between:

```text
Windows Versions
Desktop vs Server
Installed Components
Session State
Security Configuration
```

Do not assume that an object documented in an old technique is present or remotely usable on a current target.

---

# MMC20.Application

One historically well-known DCOM lateral-movement technique uses:

```text
MMC20.Application
```

The conceptual chain is:

```text
Remote DCOM
    |
    v
MMC20.Application
    |
    v
Document.ActiveView
    |
    v
ExecuteShellCommand
    |
    v
Process
```

This technique should only be validated where remote execution testing is explicitly authorised.

---

# PowerShell DCOM Object Creation

PowerShell can request a COM object on another system using the .NET `System.Activator` class.

Conceptually:

```text
Get COM Type
      |
      v
Remote Activator
      |
      v
COM Instance
```

A common pattern is:

```powershell
$type = [type]::GetTypeFromProgID('MMC20.Application', 'srv01.corp.example')
```

Then:

```powershell
$object = [Activator]::CreateInstance($type)
```

This attempts remote activation.

Do not invoke execution-capable methods unless required by the approved test plan.

---

# Safe DCOM Validation

A safe sequence is:

```text
Confirm RPC Reachability
        |
        v
Confirm Identity
        |
        v
Attempt Remote Object Activation
        |
        v
Determine Whether Activation Succeeds
        |
        v
Stop if Evidence Is Sufficient
```

Remote object activation itself may already demonstrate excessive DCOM permissions.

---

# Execution Validation

If command execution must specifically be proven, use a harmless command.

For example, in an authorised lab:

```text
cmd.exe /c echo authorised-dcom-test > C:\Windows\Temp\dcom-test.txt
```

Do not use:

```text
Reverse Shell
Credential Dumper
Security-Control Disablement
Persistence Payload
```

when a harmless marker provides sufficient evidence.

---

# MMC ExecuteShellCommand

Where explicitly authorised, the relevant MMC object exposes functionality conceptually similar to:

```text
Document.ActiveView.ExecuteShellCommand
```

A lab-only PowerShell example is:

```powershell
$type = [type]::GetTypeFromProgID('MMC20.Application', 'srv01.corp.example')
$object = [Activator]::CreateInstance($type)
$object.Document.ActiveView.ExecuteShellCommand(
    'cmd.exe',
    $null,
    '/c echo authorised-dcom-test > C:\Windows\Temp\dcom-test.txt',
    '7'
)
```

This changes the target by creating a process and marker file.

Use only when remote execution validation is explicitly required.

---

# Cleanup

Where authorised administrative SMB access exists:

```powershell
Remove-Item '\\srv01.corp.example\C$\Windows\Temp\dcom-test.txt'
```

Do not assume failure to access:

```text
C$
```

means the DCOM execution failed.

SMB and DCOM have separate network and authorisation requirements.

---

# Why DCOM May Be Non-Interactive

DCOM execution generally does not provide:

```text
Interactive Shell
```

by itself.

The model is closer to:

```text
Remote Method
     |
     v
Remote Process
```

Tooling may add command-output handling around this mechanism.

---

# Impacket DCOMExec

Impacket provides:

```text
dcomexec
```

for authorised DCOM-based remote execution testing.

Check current syntax:

```bash
impacket-dcomexec -h
```

Depending on installation, the script may also be available as:

```bash
dcomexec.py
```

---

# DCOMExec Password Authentication

For an approved test account:

```bash
impacket-dcomexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

Avoid placing production credentials directly in shell history where possible.

---

# DCOMExec Pass-the-Hash

Where pass-the-hash testing is explicitly authorised:

```bash
impacket-dcomexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

See:

[Pass-the-Hash](pass-the-hash.md)

---

# DCOMExec Authentication Model

```text
Credential
   |
   +--> Password
   |
   +--> NTLM Hash
   |
   +--> Kerberos where supported/configured
   |
   v
DCOM
   |
   v
Remote COM Object
   |
   v
Command Execution
```

Always verify options against:

```bash
impacket-dcomexec -h
```

because tool syntax can change.

---

# DCOMExec Object Selection

Impacket's DCOMExec implementation can support different DCOM object approaches depending on the installed version.

Do not assume an older object's availability.

Review:

```bash
impacket-dcomexec -h
```

before testing.

---

# Pass-the-Hash with DCOM

If NTLM is available and the account has sufficient remote rights:

```text
NTLM Hash
    |
    v
Authentication
    |
    v
DCOM
    |
    v
Remote Object
    |
    v
Remote Execution
```

may be possible.

The underlying security weakness may be:

```text
Reusable Administrative Credential
```

rather than DCOM itself.

---

# Local Administrator Reuse

Example:

```text
WS01
 |
 v
Local Administrator Hash
 |
 v
Same Credential on WS02
 |
 v
DCOM
 |
 v
Remote Execution
```

This is another reason to deploy:

```text
Windows LAPS
```

See:

[LAPS](laps.md)

---

# DCOM and Kerberos

Where Kerberos authentication is supported by the client and environment, ensure:

```text
DNS
Time
Domain
SPNs
Credential Cache
```

are correct.

Linux:

```bash
klist
```

Check:

```bash
echo "$KRB5CCNAME"
```

---

# DCOM vs WMI

WMI commonly uses DCOM for traditional remote communication.

The relationship is:

```text
WMI
 |
 v
DCOM
 |
 v
RPC
```

But DCOM can expose many COM objects unrelated to WMI.

Therefore:

```text
WMI Lateral Movement
```

and:

```text
DCOM Lateral Movement
```

are related but distinct.

See:

[WMI](wmi.md)

---

# DCOM vs SMB

SMB lateral movement commonly involves:

```text
445/TCP
Administrative Shares
Named Pipes
Service Control Manager
```

DCOM commonly involves:

```text
135/TCP
Dynamic RPC
Remote COM Activation
```

See:

[SMB](smb.md)

---

# DCOM vs WinRM

WinRM:

```text
5985 / 5986
      |
      v
WS-Management
      |
      v
PowerShell Remoting
```

DCOM:

```text
135 + Dynamic RPC
      |
      v
RPC
      |
      v
Remote COM
```

See:

[WinRM](winrm.md)

---

# DCOM vs PsExec

PsExec-style execution:

```text
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
```

DCOM execution:

```text
RPC
 |
 v
DCOM
 |
 v
COM Object
 |
 v
Method
 |
 v
Process
```

---

# DCOM vs WMIExec

WMIExec:

```text
RPC / DCOM
      |
      v
WMI
      |
      v
Win32_Process
```

DCOMExec:

```text
RPC / DCOM
      |
      v
COM Application
      |
      v
Application-Specific Method
```

Both may ultimately create remote processes, but the execution path differs.

---

# DCOM vs RDP

DCOM:

```text
Remote Object Invocation
Non-Interactive
RPC-Based
```

RDP:

```text
Interactive Desktop
GUI Session
3389/TCP
```

For simple execution validation, creating an interactive desktop session is often unnecessary.

---

# DCOM and Microsoft Management Console

Microsoft Management Console:

```text
MMC
```

is used by many Windows administrative tools.

Examples include:

```text
Computer Management
Event Viewer
Services
Certificates
Group Policy
```

The existence of MMC-related COM components is therefore expected.

The security concern arises when:

```text
Remote Activation
+
Execution-Capable Method
+
Excessive Privilege
```

are combined.

---

# DCOM and Office

COM automation is also heavily used by Microsoft Office and other desktop applications.

Do not treat:

```text
Office COM Object Exists
```

as evidence of a lateral-movement path.

Remote usability depends on:

```text
Object Registration
Remote Activation
Session Context
Permissions
Application Behaviour
Windows Version
```

---

# DCOM and Server Core

Some COM-based lateral-movement techniques depend on components that may not exist on:

```text
Server Core
```

or may behave differently from full desktop installations.

Always validate the actual environment.

---

# Version Dependence

DCOM techniques can be highly:

```text
Version Dependent
```

A method that works on:

```text
Windows 10
```

may not behave identically on:

```text
Windows 11
Windows Server 2022
Windows Server 2025
```

or later releases.

Do not build findings around assumptions from old offensive-security documentation.

---

# Object Availability

Before considering an object useful, establish:

```text
Is It Registered?

Can It Be Remotely Activated?

Does the Identity Have Permission?

Does the Required Method Exist?

Does the Method Behave as Expected?

Is the Technique Necessary to Prove the Finding?
```

---

# DCOM Network Exposure

A weak network model may allow:

```text
Any Workstation
      |
      v
RPC / DCOM
      |
      v
Every Server
```

A stronger design may restrict:

```text
Privileged Admin Workstation
          |
          v
Management Network
          |
          v
RPC / DCOM
          |
          v
Managed Server
```

---

# Workstation-to-Workstation DCOM

Where not operationally required:

```text
WS01
 |
 v
DCOM
 |
 v
WS02
```

should be restricted.

This can reduce lateral-movement opportunities after endpoint compromise.

---

# Windows Firewall

Windows Firewall should be used to restrict remote administration.

During an assessment, inspect existing firewall rules rather than enabling new ones.

Example:

```powershell
Get-NetFirewallRule |
    Where-Object Enabled -EQ 'True' |
    Select-Object DisplayName,Direction,Action
```

Filter as needed for the specific RPC/DCOM service under review.

---

# Remote Address Restrictions

Firewall rules should ideally limit management traffic to approved source systems.

Review:

```text
RemoteAddress
```

rather than checking only:

```text
Enabled
```

---

# Do Not Enable DCOM for Testing

Do not modify DCOM settings merely to demonstrate a technique.

If DCOM is disabled or restricted:

```text
The Control Is Working
```

and that should form part of the assessment evidence.

---

# DCOM Hardening

A practical DCOM hardening strategy includes:

```text
Restrict RPC Network Exposure
Apply Least Privilege
Restrict Remote Launch
Restrict Remote Activation
Restrict Remote Access
Reduce Local Administrators
Deploy Windows LAPS
Separate Administrative Identities
Use Privileged Administrative Workstations
Reduce NTLM
Monitor RPC and DCOM
Use EDR
Use Application Control
```

---

# Least Privilege

Review which principals genuinely require:

```text
Remote Access
Remote Launch
Remote Activation
```

Remove unnecessary rights.

---

# Administrative Group Review

Review:

```text
Local Administrators
Server Administrator Groups
Helpdesk Groups
Application Support Groups
Service Accounts
```

for unnecessary administrative rights across large numbers of systems.

---

# Windows LAPS

Unique local administrator credentials reduce the ability to reuse credentials for DCOM lateral movement.

See:

[LAPS](laps.md)

---

# Reduce NTLM

Where possible:

```text
Prefer Kerberos
Reduce NTLM
```

as part of a broader domain-hardening programme.

See:

[NTLM](ntlm.md)

---

# Network Segmentation

Restrict RPC/DCOM traffic between security zones.

Examples:

```text
User VLAN
   |
   X
   |
   v
Server Management RPC
```

while allowing:

```text
Management VLAN
      |
      v
Server Management RPC
```

where required.

---

# Privileged Access Workstations

A mature administrative model can use:

```text
Privileged Identity
       |
       v
Privileged Access Workstation
       |
       v
Management Network
       |
       v
DCOM
       |
       v
Managed System
```

---

# DCOM Hardening Changes

Microsoft has strengthened DCOM authentication requirements through modern Windows security updates.

Modern supported Windows systems enforce stronger DCOM authentication behaviour than older legacy environments.

This means historical DCOM techniques should not automatically be assumed to behave identically on current Windows versions.

Keep systems fully patched and validate legacy application compatibility before changing DCOM security configuration.

---

# Application Control

Application control technologies such as:

```text
WDAC
AppLocker
```

can limit what processes may execute after a remote management mechanism is abused.

This provides another security boundary after remote access.

---

# EDR

Modern endpoint security products can observe:

```text
RPC Connections
COM Activation
Parent-Child Process Relationships
Command Lines
Authentication
Network Connections
```

DCOM should not be considered an invisible lateral-movement technique.

---

# DCOM Detection

Detection should combine:

```text
Authentication
RPC Network Activity
COM Activation
Process Creation
Source System
Account
Target
```

rather than relying on a single event.

---

# Authentication Events

Relevant Security events may include:

```text
4624
4625
4648
4672
```

depending on the authentication workflow.

---

# Network Logon

Remote DCOM authentication commonly results in:

```text
Logon Type 3
```

network authentication.

---

# Kerberos Events

Where Kerberos is used:

```text
4768
4769
4771
```

can provide useful context.

---

# NTLM Events

Where NTLM is used:

```text
4776
```

and NTLM Operational logging can provide additional visibility.

---

# Process Creation

If a DCOM object launches a process:

```text
4688
```

may provide useful evidence where process creation auditing is enabled.

---

# Parent Process

The parent process depends on:

```text
COM Object
COM Server
Activation Model
Windows Version
```

Do not create a detection rule that assumes all DCOM execution has the same parent process.

---

# MMC-Based DCOM Detection

For MMC-based techniques, investigate unusual relationships involving:

```text
mmc.exe
```

followed by unexpected child processes.

Conceptually:

```text
Remote DCOM
    |
    v
mmc.exe
    |
    v
cmd.exe / powershell.exe / other process
```

The exact behaviour should be validated against the organisation's Windows versions.

---

# Suspicious Child Processes

Examples requiring investigation can include administrative COM server processes launching:

```text
cmd.exe
powershell.exe
wscript.exe
cscript.exe
rundll32.exe
```

when that behaviour is unusual for the environment.

These executables are legitimate Windows components and should not be treated as malicious solely by name.

---

# RPC Network Detection

Monitor:

```text
135/TCP
```

and dynamic RPC connections.

High-value questions include:

```text
Which Source Initiated the Connection?

Is It an Approved Management System?

Which Account Authenticated?

What Process Followed the Connection?
```

---

# High Fan-Out DCOM

Example:

```text
USER-PC
 |
 +--> SRV01:135
 +--> SRV02:135
 +--> SRV03:135
 +--> SRV04:135
 +--> SRV05:135
```

within a short period can indicate:

```text
Enumeration
Administrative Automation
Management Software
Lateral Movement
```

Context is essential.

---

# Baseline Legitimate Management Systems

Legitimate high-volume RPC/DCOM sources may include:

```text
Configuration Management
Monitoring Platforms
Asset Inventory
Security Management
Administrative Jump Hosts
Backup Systems
Enterprise Applications
```

These should be baselined before creating detection rules.

---

# Detection Correlation

A useful model is:

```text
Source Host
    |
    v
RPC 135
    |
    v
Dynamic RPC
    |
    v
Remote Authentication
    |
    v
COM Activation
    |
    v
Unexpected Process
```

---

# Source-System Context

Compare:

```text
ADMIN-JUMP01
      |
      v
SRV01 DCOM
```

with:

```text
USER-LAPTOP
      |
      v
SRV01 DCOM
```

The second relationship may deserve significantly more scrutiny.

---

# Safe Assessment Workflow

A controlled DCOM assessment should follow:

```text
Identify Target
      |
      v
Check RPC Reachability
      |
      v
Determine Identity
      |
      v
Review Administrative Rights
      |
      v
Review DCOM Permissions
      |
      v
Identify Relevant COM Object
      |
      v
Attempt Minimal Activation
      |
      v
Determine Impact
      |
      v
Minimal Execution if Required
      |
      v
Collect Evidence
      |
      v
Cleanup
```

---

# Step 1 - Check RPC

```powershell
Test-NetConnection srv01.corp.example -Port 135
```

---

# Step 2 - Confirm Identity

```cmd
whoami
```

---

# Step 3 - Review Local Rights

Where authorised on the target:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

---

# Step 4 - Review Network Boundary

Determine:

```text
Why Can the Source Reach RPC?

Is the Source an Approved Management System?

Is Workstation-to-Server RPC Required?

Is Workstation-to-Workstation RPC Required?
```

---

# Step 5 - Identify Relevant Object

Do not randomly activate large numbers of COM objects.

Select only an object relevant to the test objective and target configuration.

---

# Step 6 - Minimal Activation

Where sufficient:

```text
Remote COM Activation Successful
```

may already prove the permission boundary.

---

# Step 7 - Minimal Execution

Only when necessary:

```text
Harmless Marker
```

or another approved command.

---

# Step 8 - Cleanup

Remove:

```text
Temporary Files
Temporary Objects
Test Artifacts
```

where applicable.

Do not delete legitimate COM registrations or modify production DCOM configuration.

---

# Evidence Checklist

Record:

```text
Source Host
Source IP
Target Host
Target IP
Domain
Account
Account Type
TCP 135 Reachability
Dynamic RPC Reachability
Authentication Protocol
Local Administrator Status
DCOM Remote Access
DCOM Remote Launch
DCOM Remote Activation
COM Object
CLSID
ProgID
Method
Command
Process Created
Files Created
Files Removed
Timestamp
Tool
Exact Validation Performed
```

Do not place:

```text
Passwords
NTLM Hashes
Kerberos Tickets
Sensitive Credentials
```

directly into reports unless necessary and appropriately protected.

---

# Reporting DCOM Findings

Do not report:

```text
DCOM Enabled
```

or:

```text
TCP 135 Open
```

as vulnerabilities by themselves.

Report the actual weakness.

Examples:

```text
Standard User Has Excessive Remote DCOM Rights
```

```text
Shared Local Administrator Credentials Permit DCOM Lateral Movement
```

```text
RPC/DCOM Management Interfaces Are Exposed to Standard Workstation Networks
```

```text
Broad Administrative Group Membership Enables Remote DCOM Execution
```

---

# Example Finding - Excessive DCOM Rights

```text
Finding:
Domain Account Has Unnecessary Remote DCOM Execution Rights

Description:
The tested domain account was able to remotely activate a DCOM object
on SRV01 and invoke functionality capable of starting a process.

The account's documented role did not require remote administration of
the affected server.

A harmless command was used to validate the execution capability. No
credentials were collected and no persistence was created.

Impact:
Compromise of the affected account could allow an attacker to remotely
execute commands on SRV01 through legitimate Windows DCOM
functionality.

This provides a lateral-movement path and may expose additional systems
or credentials depending on the server's role.

Recommendation:
Review local administrative membership and DCOM access, launch and
activation permissions.

Remove unnecessary remote-management rights and restrict RPC/DCOM
network access to approved management systems.
```

---

# Example Finding - Broad RPC/DCOM Exposure

```text
Finding:
RPC/DCOM Administrative Interfaces Reachable from Standard Workstations

Description:
Standard workstation networks were able to reach RPC/DCOM services on
multiple Windows servers.

Although authentication and authorisation are still required, the
network design exposes remote-management functionality directly to
lower-trust workstation systems.

Impact:
If a workstation and suitable administrative credential are
compromised, an attacker may have a direct network path for DCOM, WMI
or other RPC-based lateral-movement techniques.

Recommendation:
Restrict RPC/DCOM management traffic using network and host firewalls.

Permit remote administrative traffic only from approved jump hosts,
management servers and privileged administrative workstations where
operationally possible.
```

---

# Example Finding - Shared Administrator Credential

```text
Finding:
Shared Local Administrator Credential Enables DCOM Lateral Movement

Description:
The same local administrator credential was valid on multiple Windows
systems.

The credential provided sufficient remote administrative rights to
activate DCOM functionality on more than one approved test system.

Impact:
Compromise of one affected endpoint may expose a reusable
administrative credential capable of providing lateral movement to
additional systems.

Recommendation:
Deploy Windows LAPS or an equivalent centrally managed solution to
provide unique local administrator passwords.

Restrict peer-to-peer RPC/DCOM administration and monitor remote
administrative activity.
```

---

# Example Finding - Broad Administrative Group

```text
Finding:
Broad Domain Group Has Local Administrator Rights Across Servers

Description:
A domain group containing a large number of users was configured as a
local administrator across multiple Windows servers.

The resulting rights allowed members of the group to use remote
administration mechanisms including DCOM where network access was
available.

Impact:
Compromise of any group member could provide administrative access to
multiple servers and significantly increase the lateral-movement blast
radius.

Recommendation:
Remove broad groups from local Administrators and replace them with
role-specific administrative groups.

Apply administrative tiering and restrict privileged remote access to
dedicated management systems.
```

---

# DCOM Assessment Checklist

## Discovery

- [ ] Identify TCP 135
- [ ] Identify RPC reachability
- [ ] Identify target hostname
- [ ] Identify domain
- [ ] Identify operating system
- [ ] Identify management network
- [ ] Determine whether DCOM is required

## Authentication

- [ ] Determine Kerberos availability
- [ ] Determine NTLM availability
- [ ] Prefer hostname for Kerberos
- [ ] Verify DNS
- [ ] Verify time synchronisation
- [ ] Identify domain vs local account
- [ ] Avoid unnecessary authentication attempts

## Authorisation

- [ ] Review local Administrators
- [ ] Review DCOM Access Permissions
- [ ] Review Remote Access
- [ ] Review Launch Permissions
- [ ] Review Remote Launch
- [ ] Review Activation Permissions
- [ ] Review Remote Activation
- [ ] Identify delegated non-admin access
- [ ] Determine whether rights are business-required

## COM Objects

- [ ] Identify relevant COM object
- [ ] Record ProgID
- [ ] Record CLSID
- [ ] Record AppID where relevant
- [ ] Confirm object exists
- [ ] Confirm remote activation
- [ ] Confirm required method exists
- [ ] Consider Windows version
- [ ] Avoid mass object activation

## Remote Execution

- [ ] Confirm execution testing is required
- [ ] Use authorised target
- [ ] Use authorised account
- [ ] Use harmless command
- [ ] Avoid reverse shells
- [ ] Avoid credential dumping
- [ ] Avoid persistence
- [ ] Avoid disabling controls
- [ ] Record created process
- [ ] Remove marker files

## Impacket

- [ ] Check installed Impacket version
- [ ] Run `impacket-dcomexec -h`
- [ ] Verify available object options
- [ ] Verify authentication mode
- [ ] Protect passwords
- [ ] Protect NTLM hashes
- [ ] Verify Kerberos configuration where required
- [ ] Stop after sufficient evidence

## Pass-the-Hash

- [ ] Confirm PTH testing is authorised
- [ ] Determine whether NTLM is available
- [ ] Determine administrative rights
- [ ] Use approved test material
- [ ] Avoid broad authentication sweeps
- [ ] Review local password reuse
- [ ] Review Windows LAPS

## Network Segmentation

- [ ] Review workstation-to-server RPC
- [ ] Review workstation-to-workstation RPC
- [ ] Review server-to-server RPC
- [ ] Identify approved management sources
- [ ] Review host firewall
- [ ] Review network firewall
- [ ] Review remote-address restrictions
- [ ] Identify unexpected RPC paths

## Safe Validation

- [ ] Start with network discovery
- [ ] Review permissions
- [ ] Prefer activation before execution
- [ ] Execute only if necessary
- [ ] Use harmless marker
- [ ] Avoid production payloads
- [ ] Do not modify DCOM permissions
- [ ] Do not enable firewall rules
- [ ] Do not weaken UAC
- [ ] Remove artifacts
- [ ] Record cleanup

## Detection

- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4648
- [ ] Monitor 4672
- [ ] Monitor 4688
- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Monitor 4776
- [ ] Monitor RPC connections
- [ ] Monitor dynamic RPC
- [ ] Monitor COM-related process creation
- [ ] Monitor unusual MMC child processes
- [ ] Monitor unusual source systems
- [ ] Monitor high fan-out RPC
- [ ] Baseline legitimate management platforms
- [ ] Correlate network, authentication and process telemetry

## Hardening

- [ ] Restrict RPC network exposure
- [ ] Restrict DCOM to approved management systems
- [ ] Apply least privilege
- [ ] Review local Administrators
- [ ] Review DCOM permissions
- [ ] Remove unnecessary Remote Launch
- [ ] Remove unnecessary Remote Activation
- [ ] Deploy Windows LAPS
- [ ] Reduce NTLM
- [ ] Separate privileged identities
- [ ] Use privileged administrative workstations
- [ ] Segment management networks
- [ ] Keep Windows patched
- [ ] Deploy application control
- [ ] Deploy EDR
- [ ] Monitor remote administration

## Reporting

- [ ] Do not report DCOM merely because it exists
- [ ] Do not report TCP 135 alone
- [ ] Identify actual excessive privilege
- [ ] Identify affected identity
- [ ] Identify affected systems
- [ ] Identify authentication method
- [ ] Identify DCOM permissions
- [ ] Identify COM object
- [ ] Identify execution capability
- [ ] Document minimal validation
- [ ] Explain lateral-movement impact
- [ ] Provide targeted remediation

---

# DCOM Testing Model

The basic COM model is:

```text
Application
    |
    v
COM Object
    |
    v
Method
```

The distributed model is:

```text
Client
  |
  v
RPC
  |
  v
DCOM
  |
  v
Remote COM Object
```

The network model is:

```text
Client
  |
  v
135/TCP
  |
  v
RPC Endpoint Mapper
  |
  v
Dynamic RPC
  |
  v
DCOM
```

The security model is:

```text
Identity
   |
   v
Authentication
   |
   v
Remote Access
   |
   v
Remote Launch
   |
   v
Remote Activation
   |
   v
COM Object
```

The execution model is:

```text
Remote Identity
      |
      v
DCOM
      |
      v
COM Object
      |
      v
Execution-Capable Method
      |
      v
Remote Process
```

The MMC model is:

```text
Remote DCOM
    |
    v
MMC20.Application
    |
    v
ActiveView
    |
    v
ExecuteShellCommand
    |
    v
Process
```

The Pass-the-Hash model is:

```text
NTLM Hash
    |
    v
NTLM Authentication
    |
    v
DCOM
    |
    v
Remote Execution
```

The credential-reuse model is:

```text
Host A
 |
 v
Reusable Local Admin
 |
 v
Host B
 |
 v
DCOM
 |
 v
Remote Execution
```

The WMI relationship is:

```text
WMI
 |
 v
DCOM
 |
 v
RPC
```

The DCOMExec model is:

```text
Operator
   |
   v
Credential
   |
   v
RPC / DCOM
   |
   v
Remote COM Object
   |
   v
Remote Process
```

The detection model is:

```text
Source Host
    |
    v
RPC
    |
    v
Authentication
    |
    v
COM Activation
    |
    v
Process Creation
```

The network-hardening model is:

```text
User Workstation
      |
      X
      |
      v
Server RPC / DCOM

Admin Workstation
      |
      v
Management Network
      |
      v
Server RPC / DCOM
```

The defensive model is:

```text
Restricted RPC
      +
Least Privilege
      +
Restricted DCOM Permissions
      +
Unique Local Credentials
      +
Administrative Separation
      +
Application Control
      +
Monitoring
      =
Reduced DCOM Attack Surface
```

For penetration testers:

```text
Do Not Ask:
"Which DCOM object gives me execution?"

Ask:
"Why is this identity allowed to remotely
activate administrative components
on this system?"
```

For defenders:

```text
Do Not Ask:
"Can we block all DCOM?"

Ask:
"Which systems require DCOM,
which identities require remote activation,
and can those relationships be restricted?"
```

The complete relationship is:

```text
Identity
   |
   v
Network Reachability
   |
   v
Authentication
   |
   v
DCOM Permission
   |
   v
Remote COM Object
   |
   v
Method
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

WinRM:

[WinRM](winrm.md)

WMI:

[WMI](wmi.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

BloodHound:

[BloodHound](bloodhound.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

LAPS:

[LAPS](laps.md)

The next lateral-movement page is:

```text
docs/active-directory/pivoting.md
```

---

# References

## Microsoft - Distributed Component Object Model

[Microsoft - Distributed Component Object Model](https://learn.microsoft.com/en-us/windows/win32/com/distributed-component-object-model--dcom-){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - COM Security

[Microsoft - COM Security](https://learn.microsoft.com/en-us/windows/win32/com/com-security){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Setting Process-Wide Security Using DCOMCNFG

[Microsoft - Setting Process-Wide Security Using DCOMCNFG](https://learn.microsoft.com/en-us/windows/win32/com/setting-processwide-security-using-dcomcnfg){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - RPC

[Microsoft - Remote Procedure Call](https://learn.microsoft.com/en-us/windows/win32/rpc/rpc-start-page){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DCOM Hardening

[Microsoft - KB5004442 Manage Changes for Windows DCOM Server Security Feature Bypass](https://support.microsoft.com/help/5004442){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

Verify current DCOMExec syntax with:

```bash
impacket-dcomexec -h
```

---

## MITRE ATT&CK - Distributed Component Object Model

[MITRE ATT&CK - Distributed Component Object Model](https://attack.mitre.org/techniques/T1021/003/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

DCOM is a legitimate Windows technology.

Its existence is not a vulnerability.

The important questions are:

```text
Who Can Reach RPC/DCOM?

Who Can Authenticate?

Who Has Remote Access?

Who Has Remote Launch?

Who Has Remote Activation?

Which COM Objects Are Available?

Can Those Objects Perform Security-Sensitive Actions?

Is That Administrative Relationship Required?
```

The preferred assessment sequence is:

```text
Discover RPC
     |
     v
Determine Identity
     |
     v
Review Administrative Rights
     |
     v
Review DCOM Permissions
     |
     v
Identify Relevant Object
     |
     v
Minimal Activation
     |
     v
Minimal Execution if Required
     |
     v
Evidence
     |
     v
Cleanup
```

Do not move directly from:

```text
135/TCP Open
```

to:

```text
Remote Execution
```

An open RPC Endpoint Mapper is not proof of a DCOM vulnerability.

Likewise:

```text
DCOM Enabled
```

does not mean:

```text
DCOM Vulnerability
```

The actual weakness is more likely to be:

```text
Excessive Administrative Rights
```

or:

```text
Reusable Credentials
```

or:

```text
Overly Broad DCOM Permissions
```

or:

```text
Unnecessary RPC Network Exposure
```

When remote execution testing is necessary:

```text
Use Minimum Impact
```

and stop when:

```text
Security Impact Is Proven
```

A mature architecture should aim for:

```text
Approved Administrative Identity
           |
           v
Hardened Administrative Workstation
           |
           v
Restricted Management Network
           |
           v
RPC / DCOM
           |
           v
Approved Managed System
```

rather than:

```text
Any Compromised Workstation
          |
          v
RPC / DCOM
          |
          v
Every Windows Server
```

DCOM should therefore be viewed as:

```text
Legitimate Remote Management
            +
Excessive Privilege
            +
Unrestricted Network Path
            =
Potential Lateral Movement
```

The next page moves from individual remote-management protocols to moving traffic through segmented networks:

```text
Pivoting
```
