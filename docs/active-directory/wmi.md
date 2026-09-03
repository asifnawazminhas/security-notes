# Active Directory WMI - Enumeration, Remote Administration and Lateral Movement

Windows Management Instrumentation (WMI) is a core Windows management technology that provides a standard interface for querying and managing operating-system components.

Administrators, management platforms and security products use WMI for tasks such as:

```text
System Inventory
Process Management
Service Management
Operating-System Information
Hardware Information
Event Queries
Remote Administration
Configuration Management
Software Inventory
Automation
```

Because WMI can operate remotely and can expose methods capable of creating processes, it is also important during Active Directory lateral-movement assessments.

The fundamental relationship is:

```text
Identity
   |
   v
Remote WMI Access
   |
   v
WMI Namespace
   |
   v
Management Object
   |
   v
Query / Method
```

When sufficient permissions are available, this can become:

```text
Compromised Identity
        |
        v
Remote WMI
        |
        v
Win32_Process
        |
        v
Remote Process Creation
        |
        v
Target System
```

WMI should therefore be assessed as both:

```text
Management Interface
```

and:

```text
Potential Lateral-Movement Channel
```

!!! warning "Authorised testing only"
    Remote WMI can execute commands and modify system state. Only test systems and identities included in the assessment scope. Prefer read-only WMI queries first. If execution must be demonstrated, use harmless commands such as `whoami` or `hostname` and stop once sufficient evidence has been collected.

---

# WMI at a Glance

WMI provides access to management information through:

```text
WMI Namespace
      |
      v
WMI Classes
      |
      v
Instances
      |
      +--> Properties
      |
      +--> Methods
```

Example:

```text
root\cimv2
    |
    v
Win32_OperatingSystem
    |
    +--> Caption
    +--> Version
    +--> BuildNumber
```

Another example:

```text
root\cimv2
    |
    v
Win32_Process
    |
    +--> Name
    +--> ProcessId
    |
    +--> Create()
```

The difference between:

```text
Querying Properties
```

and:

```text
Invoking Methods
```

is important during security testing.

---

# WMI Architecture

A simplified architecture is:

```text
Management Client
       |
       v
WMI API
       |
       v
WMI Service
       |
       v
WMI Provider
       |
       v
Windows Component
```

For remote WMI:

```text
Management Client
       |
       v
RPC / DCOM
       |
       v
Remote Windows Host
       |
       v
WMI Service
       |
       v
Namespace / Provider
```

Modern management interfaces can also access CIM information through:

```text
WS-Management / WinRM
```

which should be distinguished from traditional WMI over DCOM.

---

# WMI vs CIM

WMI and CIM are closely related but should not be treated as identical command interfaces.

Conceptually:

```text
CIM
 |
 v
Management Model
```

and:

```text
WMI
 |
 v
Microsoft Implementation / Infrastructure
```

Modern PowerShell generally favours:

```text
CIM Cmdlets
```

such as:

```powershell
Get-CimInstance
```

over older WMI cmdlets such as:

```powershell
Get-WmiObject
```

---

# WMI vs WMIC

Do not confuse:

```text
WMI
```

with:

```text
WMIC
```

WMI is the management infrastructure.

WMIC is a command-line client historically used to interact with WMI.

Conceptually:

```text
WMI
=
Technology
```

```text
wmic.exe
=
One Client
```

`wmic.exe` is deprecated on modern Windows and is disabled by default on newer Windows 11 releases. Modern assessments should therefore not assume that WMIC is available.

Prefer:

```text
PowerShell CIM Cmdlets
PowerShell WMI APIs
Management APIs
Purpose-Built Assessment Tools
```

where appropriate.

---

# WMI Service

The Windows Management Instrumentation service is:

```text
Winmgmt
```

Check locally:

```powershell
Get-Service Winmgmt
```

Example:

```text
Status   Name     DisplayName
------   ----     -----------
Running  Winmgmt  Windows Management Instrumentation
```

---

# WMI Repository

WMI maintains management information through its providers and repository.

The security assessment should generally focus on:

```text
Remote Access
Namespace Permissions
Available Methods
Authentication
Authorisation
Network Exposure
Logging
```

rather than modifying the WMI repository.

---

# WMI Namespaces

WMI information is organised into namespaces.

A common namespace is:

```text
root\cimv2
```

Other namespaces may exist for:

```text
Security Products
Management Platforms
Applications
Hardware
Virtualisation
Microsoft Components
```

---

# Enumerate WMI Namespaces

PowerShell can query namespaces.

For example:

```powershell
Get-CimInstance -Namespace root -ClassName __Namespace |
    Select-Object Name
```

Example output may include:

```text
cimv2
DEFAULT
Microsoft
SecurityCenter2
subscription
```

Availability varies by Windows version and installed software.

---

# WMI Classes

A WMI class describes a type of manageable object.

Common examples include:

```text
Win32_OperatingSystem
Win32_ComputerSystem
Win32_Process
Win32_Service
Win32_LogicalDisk
Win32_NetworkAdapter
Win32_LoggedOnUser
```

Not every class or property is available on every Windows version.

---

# Basic Local WMI Enumeration

Modern PowerShell:

```powershell
Get-CimInstance -ClassName Win32_OperatingSystem
```

Focused output:

```powershell
Get-CimInstance -ClassName Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber,OSArchitecture
```

---

# Computer Information

```powershell
Get-CimInstance -ClassName Win32_ComputerSystem |
    Select-Object Name,Domain,Manufacturer,Model
```

---

# Process Enumeration

```powershell
Get-CimInstance -ClassName Win32_Process |
    Select-Object ProcessId,Name
```

---

# Service Enumeration

```powershell
Get-CimInstance -ClassName Win32_Service |
    Select-Object Name,State,StartMode,StartName
```

---

# Disk Enumeration

```powershell
Get-CimInstance -ClassName Win32_LogicalDisk |
    Select-Object DeviceID,DriveType,FileSystem,Size,FreeSpace
```

---

# WMI Query Language

WMI supports:

```text
WQL
```

or:

```text
WMI Query Language
```

Its syntax resembles SQL for querying WMI data.

Example:

```text
SELECT * FROM Win32_Process
```

A more focused query:

```text
SELECT Name,ProcessId FROM Win32_Process
```

---

# WQL with PowerShell

```powershell
Get-CimInstance -Query 'SELECT Name,ProcessId FROM Win32_Process'
```

---

# Remote WMI

Traditional remote WMI commonly uses:

```text
DCOM
+
RPC
```

The basic path is:

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
DCOM
  |
  v
WMI
```

This is different from a protocol such as SMB where the primary service normally remains on:

```text
445/TCP
```

---

# RPC Endpoint Mapper

Traditional remote WMI commonly begins with:

```text
TCP 135
```

The RPC Endpoint Mapper then helps the client locate the dynamically assigned endpoint used by the required RPC service.

Therefore:

```text
TCP 135 Reachable
```

does not by itself prove:

```text
Remote WMI Works
```

---

# Dynamic RPC Ports

Modern Windows commonly uses dynamic RPC ports in the high TCP port range.

The exact range depends on:

```text
Windows Version
System Configuration
Firewall Configuration
RPC Configuration
```

Therefore, successful remote WMI normally requires more than simply permitting TCP 135.

---

# Check RPC Connectivity

From Windows:

```powershell
Test-NetConnection srv01.corp.example -Port 135
```

Example:

```text
ComputerName     : srv01.corp.example
RemoteAddress    : 10.10.10.25
RemotePort       : 135
TcpTestSucceeded : True
```

---

# Linux Discovery

```bash
nmap -Pn -p135 srv01.corp.example
```

For a defined target range:

```bash
nmap -Pn -p135 10.10.10.0/24
```

Do not treat:

```text
135/tcp open
```

as proof that WMI remote access is authorised.

---

# Remote WMI Requirements

Traditional remote WMI depends on several security layers:

```text
Network Reachability
        |
        v
RPC / DCOM
        |
        v
Authentication
        |
        v
DCOM Permissions
        |
        v
WMI Namespace Permissions
        |
        v
Object / Method Permissions
```

A failure at any layer may prevent the operation.

---

# Authentication

Remote WMI can use Windows authentication mechanisms including:

```text
Kerberos
NTLM
```

depending on:

```text
Domain Membership
Target Name
Credentials
Trust
Client
Configuration
```

---

# Kerberos

In a normal domain environment:

```text
Domain User
    |
    v
Kerberos
    |
    v
RPC / DCOM
    |
    v
WMI
```

may be used when Kerberos requirements are satisfied.

---

# NTLM

If Kerberos cannot be used and NTLM is available:

```text
Domain User
    |
    v
NTLM
    |
    v
RPC / DCOM
    |
    v
WMI
```

may occur.

This makes WMI relevant when assessing:

```text
NTLM Exposure
Pass-the-Hash
Credential Reuse
Lateral Movement
```

---

# Hostnames vs IP Addresses

When Kerberos is expected, prefer:

```text
srv01.corp.example
```

rather than:

```text
10.10.10.25
```

Using hostnames supports:

```text
DNS Resolution
SPN Resolution
Kerberos Authentication
```

whereas using an IP address may cause authentication behaviour to differ.

---

# Remote WMI Authorisation

Remote WMI access is normally restricted.

Administrators typically have broad WMI access, while non-administrators require specific permissions to be delegated.

The important security question is:

```text
Who Has Remote WMI Rights?
```

not:

```text
Is WMI Running?
```

---

# WMI Namespace Security

Permissions can be assigned to individual WMI namespaces.

Important permissions include:

```text
Enable Account
Execute Methods
Remote Enable
Provider Write
```

The exact permissions depend on the namespace and configuration.

---

# Remote Enable

A principal generally requires:

```text
Remote Enable
```

for the relevant WMI namespace to access it remotely.

This means a non-administrator can potentially be deliberately granted remote WMI access without being made a full local administrator.

---

# Namespace Permissions Matter

Example:

```text
User
 |
 v
DCOM Remote Access
 |
 v
root\cimv2 Remote Enable
 |
 v
WMI Query
```

But another namespace may remain inaccessible:

```text
User
 |
 v
root\OtherNamespace
 |
 X
 |
 v
Access Denied
```

---

# DCOM Permissions

Remote WMI over DCOM can depend on permissions including:

```text
Remote Access
Remote Launch
Remote Activation
```

Administrators normally have the required remote permissions by default.

Custom delegation should be reviewed carefully.

---

# UAC and Remote WMI

User Account Control can affect remote WMI access.

The behaviour differs between:

```text
Domain Accounts
```

and:

```text
Local Accounts
```

---

# Domain Administrator Context

A domain account that is a member of the target system's local Administrators group is generally treated differently from a local non-domain administrator account for remote UAC filtering.

This is important during lateral-movement testing.

---

# Local Account Token Filtering

Local administrative accounts may encounter:

```text
UAC Remote Restrictions
```

and receive a filtered token during remote administration.

Therefore:

```text
Local Administrators Membership
```

does not always guarantee identical remote behaviour for every type of account.

---

# Do Not Disable UAC for Testing

Do not modify:

```text
LocalAccountTokenFilterPolicy
```

or disable UAC merely to make remote WMI work during an assessment.

If access is blocked by the security configuration, that is part of the assessment result.

---

# Read-Only Remote WMI Query

A low-impact validation should begin with a query.

For example, using legacy Windows PowerShell where the WMI cmdlets are available:

```powershell
Get-WmiObject -Class Win32_OperatingSystem -ComputerName srv01.corp.example |
    Select-Object Caption,Version,BuildNumber
```

This demonstrates:

```text
Remote WMI Query Access
```

without creating a process.

---

# Legacy WMI Cmdlets

Windows PowerShell includes cmdlets such as:

```text
Get-WmiObject
Invoke-WmiMethod
Set-WmiInstance
Remove-WmiObject
```

These should be considered legacy interfaces.

Modern PowerShell generally favours:

```text
CIM Cmdlets
```

---

# CIM Cmdlets

Common CIM cmdlets include:

```text
Get-CimInstance
New-CimSession
Invoke-CimMethod
Remove-CimSession
```

---

# Important Transport Difference

Do not assume:

```text
Get-CimInstance
```

and:

```text
Get-WmiObject
```

use the same remote transport.

Traditional WMI remote access commonly uses:

```text
DCOM
```

while modern CIM sessions commonly use:

```text
WS-Management
```

unless configured otherwise.

---

# DCOM CIM Session

If traditional DCOM transport specifically needs to be tested through CIM cmdlets, PowerShell can create a DCOM session option.

Example:

```powershell
$option = New-CimSessionOption -Protocol Dcom
$session = New-CimSession -ComputerName srv01.corp.example -SessionOption $option
```

Query:

```powershell
Get-CimInstance -CimSession $session -ClassName Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber
```

Cleanup:

```powershell
Remove-CimSession $session
```

---

# DCOM CIM Workflow

```text
New-CimSessionOption
        |
        v
Protocol DCOM
        |
        v
New-CimSession
        |
        v
Get-CimInstance
        |
        v
Remove-CimSession
```

---

# WinRM CIM Session

A standard CIM session may instead use WS-Management:

```text
PowerShell
    |
    v
CIM
    |
    v
WS-Man
    |
    v
WinRM
```

See:

[WinRM](winrm.md)

---

# WMI Remote Process Creation

One of the most important WMI capabilities during lateral-movement assessments is:

```text
Win32_Process.Create()
```

Conceptually:

```text
Authorised WMI User
       |
       v
Win32_Process
       |
       v
Create()
       |
       v
Remote Process
```

---

# Safe Process-Creation Validation

If remote process execution must be demonstrated, use a harmless command.

For example, an authorised lab test could create a temporary marker file:

```text
cmd.exe /c echo authorised-wmi-test > C:\Windows\Temp\wmi-test.txt
```

Only use a path where the approved test identity is authorised to write.

Remove the marker after verification.

---

# Why Marker Files Can Be Useful

Remote WMI process creation is generally:

```text
Non-Interactive
```

The process does not automatically return stdout to the operator.

Therefore:

```text
whoami
```

may execute remotely but provide no visible output to the client.

A harmless marker can prove execution without deploying a payload.

---

# Invoke-WmiMethod

In Windows PowerShell environments where the legacy cmdlet is available:

```powershell
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList 'cmd.exe /c echo authorised-wmi-test > C:\Windows\Temp\wmi-test.txt' -ComputerName srv01.corp.example
```

This changes the remote system by creating a process and file.

Only use it when execution validation is explicitly required.

---

# Invoke-CimMethod

For a CIM session:

```powershell
$option = New-CimSessionOption -Protocol Dcom
$session = New-CimSession -ComputerName srv01.corp.example -SessionOption $option
```

Then:

```powershell
Invoke-CimMethod -CimSession $session -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = 'cmd.exe /c echo authorised-wmi-test > C:\Windows\Temp\wmi-test.txt'
}
```

Cleanup:

```powershell
Remove-CimSession $session
```

---

# Verify Marker

Where authorised:

```powershell
Test-Path '\\srv01.corp.example\C$\Windows\Temp\wmi-test.txt'
```

This additionally requires suitable SMB administrative-share access.

Do not interpret failure to access:

```text
C$
```

as proof that the WMI command failed.

The two operations have separate authorisation requirements.

---

# Clean Up Marker

Where the marker was created and SMB access is authorised:

```powershell
Remove-Item '\\srv01.corp.example\C$\Windows\Temp\wmi-test.txt'
```

Record cleanup in the assessment evidence.

---

# WMI Does Not Provide an Interactive Shell

Traditional WMI process creation is better represented as:

```text
Command
   |
   v
Remote Process
```

rather than:

```text
Interactive Terminal
```

Tools may build additional functionality around WMI to create a shell-like experience.

---

# Impacket WMIExec

Impacket provides:

```text
wmiexec
```

for remote command execution through WMI/DCOM.

Check the installed syntax:

```bash
impacket-wmiexec -h
```

Depending on installation, the executable may also be available as:

```bash
wmiexec.py
```

---

# WMIExec Password Authentication

For an explicitly authorised test account:

```bash
impacket-wmiexec 'CORP/audit-admin:PASSWORD@srv01.corp.example'
```

Avoid placing production passwords in shell history where possible.

---

# WMIExec Pass-the-Hash

Where pass-the-hash testing is explicitly authorised:

```bash
impacket-wmiexec -hashes ':NTHASH' 'CORP/audit-admin@srv01.corp.example'
```

See:

[Pass-the-Hash](pass-the-hash.md)

---

# WMIExec Model

Conceptually:

```text
Credential
   |
   v
DCOM / WMI
   |
   v
Remote Process
   |
   v
Command Output Handling
```

The tool provides a shell-like interface, but the underlying mechanism should still be understood.

---

# WMIExec and SMB

Impacket WMIExec can use SMB to retrieve command output.

Conceptually:

```text
WMI
 |
 +--> Execute Command
 |
 v
Remote Output
 |
 v
SMB
 |
 v
Operator
```

Therefore, a WMIExec workflow can involve more than one protocol.

---

# Why This Matters

Suppose:

```text
RPC / WMI Works
```

but:

```text
SMB Is Blocked
```

The behaviour of a particular tool may differ from direct WMI process creation.

Do not conclude:

```text
WMI Is Blocked
```

solely because a tool relying on additional protocols fails.

---

# Impacket Authentication Options

Current Impacket versions support several authentication approaches across many tools.

Always inspect:

```bash
impacket-wmiexec -h
```

before using syntax copied from older notes.

Potential mechanisms can include:

```text
Password
NTLM Hash
Kerberos
```

depending on the tool and environment.

---

# Kerberos with WMIExec

Where Kerberos authentication is required, review the current tool options:

```bash
impacket-wmiexec -h
```

and ensure:

```text
DNS
Time Synchronisation
Kerberos Cache
SPNs
Target Hostname
```

are correct.

---

# Credential Cache

Linux:

```bash
klist
```

Check:

```bash
echo "$KRB5CCNAME"
```

Example:

```bash
export KRB5CCNAME=./audit-admin.ccache
```

Use the hostname rather than an IP address when the Kerberos workflow requires correct SPN resolution.

---

# Pass-the-Hash and WMI

WMI can become a lateral-movement mechanism when an attacker possesses:

```text
NTLM Hash
```

for an account with sufficient remote rights.

The path becomes:

```text
NTLM Hash
    |
    v
Authentication
    |
    v
WMI
    |
    v
Remote Process Creation
```

See:

[Pass-the-Hash](pass-the-hash.md)

---

# Credential Reuse

A common lateral-movement problem is:

```text
Host A
 |
 v
Local Administrator Credential
 |
 v
Same Credential on Host B
 |
 v
Remote WMI
 |
 v
Host B
```

Unique local administrator passwords significantly reduce this attack path.

See:

[LAPS](laps.md)

---

# WMI vs SMB PsExec

PsExec-style execution commonly uses:

```text
SMB
 |
 v
Administrative Share
 |
 v
Service Control Manager
 |
 v
Temporary Service
```

WMI execution instead commonly uses:

```text
RPC / DCOM
 |
 v
WMI
 |
 v
Win32_Process
 |
 v
Remote Process
```

---

# Operational Difference

PsExec-style execution may create:

```text
Temporary Service
Executable File
Service Installation Events
```

WMI process creation does not require the same temporary-service mechanism.

However:

```text
WMI Is Not Stealthy
```

Modern EDR and Windows telemetry can provide significant visibility.

---

# WMI vs WinRM

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

Traditional WMI:

```text
135 + Dynamic RPC
      |
      v
DCOM
      |
      v
WMI
```

See:

[WinRM](winrm.md)

---

# WMI vs DCOM

WMI remote access traditionally uses DCOM.

However:

```text
WMI
```

is not synonymous with:

```text
DCOM
```

DCOM is a broader Windows technology that can expose many COM objects remotely.

WMI is one consumer of DCOM.

The dedicated DCOM lateral-movement page will cover this distinction in more detail.

---

# WMI vs RDP

WMI:

```text
Remote Management API
Non-Interactive Process Creation
Automation Friendly
```

RDP:

```text
Graphical Interactive Session
Desktop Logon
Different Credential Exposure
Different Telemetry
```

Use the least intrusive mechanism necessary to prove the assessment objective.

---

# WMI Enumeration Before Execution

A good WMI assessment should begin with:

```text
Query
```

rather than:

```text
Execute
```

For example:

```powershell
Get-CimInstance -CimSession $session -ClassName Win32_OperatingSystem
```

can prove remote WMI access.

---

# When Is Process Creation Necessary?

Process creation may be necessary when the question is specifically:

```text
Can This Identity Execute Commands Remotely?
```

But if:

```text
Remote WMI Access
+
Administrative Rights
+
Execute Methods Permission
```

is already sufficiently established through configuration evidence, further intrusive validation may not be necessary.

---

# Safe Testing Principle

Use:

```text
Minimum Action
```

required to establish:

```text
Maximum Evidence
```

---

# WMI and BloodHound

BloodHound primarily models relationships and permissions rather than every possible WMI method.

Relevant paths may still identify:

```text
Local Administrator Rights
Group Membership
Remote Access Relationships
Credential Exposure
```

that explain why WMI access is possible.

See:

[BloodHound](bloodhound.md)

---

# Local Administrator Path

Example:

```text
User
 |
 v
MemberOf
 |
 v
Server Admin Group
 |
 v
Local Administrator
 |
 v
Remote WMI
```

The security issue is often:

```text
Excessive Administrative Relationship
```

rather than WMI itself.

---

# WMI and NetExec

NetExec is useful for identifying:

```text
Authentication
Administrative Rights
Target Information
```

through several supported protocols.

See:

[NetExec](netexec.md)

Do not assume that successful administrative authentication through SMB proves that:

```text
WMI Network Path Is Reachable
```

because firewall and RPC configuration may differ.

---

# WMI Network Segmentation

A weak architecture may allow:

```text
Any Workstation
      |
      v
TCP 135 + RPC
      |
      v
Every Server
```

A stronger design may restrict remote management to:

```text
Privileged Admin Workstation
          |
          v
Management Network
          |
          v
RPC / WMI
          |
          v
Managed Server
```

---

# Workstation-to-Workstation WMI

Where operationally unnecessary:

```text
WS01
 |
 v
Remote WMI
 |
 v
WS02
```

should be restricted.

This reduces peer-to-peer lateral-movement opportunities.

---

# WMI Firewall Rules

Windows Firewall contains rules associated with:

```text
Windows Management Instrumentation (WMI)
```

Review them without modifying the system.

For example:

```powershell
Get-NetFirewallRule |
    Where-Object DisplayGroup -Like '*Windows Management Instrumentation*' |
    Select-Object DisplayName,Enabled,Direction,Action
```

Display-group names can vary with system language.

---

# Firewall Address Filters

For identified WMI firewall rules:

```powershell
Get-NetFirewallRule |
    Where-Object DisplayGroup -Like '*Windows Management Instrumentation*' |
    Get-NetFirewallAddressFilter
```

Review:

```text
LocalAddress
RemoteAddress
```

---

# Do Not Enable WMI Firewall Rules During Testing

Commands that enable WMI firewall exceptions modify the security configuration.

Do not run commands such as:

```text
netsh advfirewall firewall set rule group="windows management instrumentation (wmi)" new enable=yes
```

merely to make an assessment test succeed.

If the firewall blocks remote WMI:

```text
That Control Is Working
```

and should be documented accordingly.

---

# Do Not Modify DCOM Permissions

Similarly, do not modify:

```text
Remote Launch
Remote Activation
Remote Access
```

permissions to make WMI testing work.

The existing permissions are part of the security posture being assessed.

---

# Do Not Modify Namespace Permissions

Do not grant yourself:

```text
Remote Enable
Execute Methods
```

on a WMI namespace during an assessment unless configuration changes are explicitly part of the engagement.

---

# WMI Persistence

WMI also supports permanent event subscriptions.

These can involve:

```text
Event Filter
Consumer
Filter-to-Consumer Binding
```

Conceptually:

```text
Event
 |
 v
WMI Filter
 |
 v
Consumer
 |
 v
Action
```

This can be used legitimately for management automation but can also be abused for persistence.

---

# Permanent WMI Event Subscriptions

The relevant architecture is:

```text
__EventFilter
      |
      v
__FilterToConsumerBinding
      |
      v
Event Consumer
```

Potential consumers include classes capable of launching commands or scripts.

---

# Persistence Is Separate from Lateral Movement

Do not confuse:

```text
Remote WMI Process Creation
```

with:

```text
Permanent WMI Event Subscription
```

Remote process creation is typically:

```text
Execution / Lateral Movement
```

while permanent subscriptions may provide:

```text
Persistence
```

The dedicated persistence section should cover permanent WMI subscriptions in greater detail.

---

# Enumerate WMI Subscriptions

Where authorised, defenders and assessors can review:

```text
root\subscription
```

Example:

```powershell
Get-CimInstance -Namespace root\subscription -ClassName __EventFilter
```

---

# Consumers

```powershell
Get-CimInstance -Namespace root\subscription -ClassName __EventConsumer
```

---

# Bindings

```powershell
Get-CimInstance -Namespace root\subscription -ClassName __FilterToConsumerBinding
```

Treat unknown subscriptions as items requiring investigation, not automatically as malicious persistence.

---

# WMI Detection

WMI activity can generate telemetry across:

```text
Security Logs
WMI Activity Logs
Process Creation
PowerShell Logs
RPC Network Telemetry
EDR
Sysmon
```

---

# WMI Activity Operational Log

Important logging exists under:

```text
Microsoft-Windows-WMI-Activity/Operational
```

This can help correlate:

```text
WMI Operations
Client Processes
Providers
Errors
Remote Activity
```

---

# WMI Event 5857

WMI Activity events in the:

```text
5857-5861
```

range can provide useful WMI telemetry depending on Windows version and operation.

Do not rely on a single event ID for all WMI detection.

---

# WMI Event 5858

Event:

```text
5858
```

is commonly useful when investigating WMI operations and errors.

Fields and interpretation depend on the Windows version and activity.

---

# WMI Event 5861

Event:

```text
5861
```

is particularly relevant to permanent WMI event subscription activity.

This can help detect creation or modification of persistence-related WMI bindings.

---

# Process Creation

Remote WMI process creation commonly results in a process relationship involving:

```text
WmiPrvSE.exe
```

Conceptually:

```text
WmiPrvSE.exe
      |
      v
cmd.exe
```

or:

```text
WmiPrvSE.exe
      |
      v
powershell.exe
```

This can be a useful detection signal.

---

# WmiPrvSE.exe

`WmiPrvSE.exe` is a legitimate Windows component.

Therefore:

```text
WmiPrvSE.exe Exists
```

is not suspicious.

The important question is:

```text
What Did It Spawn?
```

---

# Suspicious Parent-Child Patterns

Examples requiring investigation can include:

```text
WmiPrvSE.exe
      |
      v
cmd.exe
```

```text
WmiPrvSE.exe
      |
      v
powershell.exe
```

```text
WmiPrvSE.exe
      |
      v
script interpreter
```

Context remains essential because legitimate management products can produce similar behaviour.

---

# Security Event 4688

With process creation auditing enabled:

```text
4688
```

can provide information about newly created processes.

Useful fields include:

```text
New Process Name
Creator Process
Account
Command Line
```

depending on auditing configuration.

---

# Logon Events

Remote WMI authentication may generate events such as:

```text
4624
4625
4648
4672
```

depending on the authentication workflow.

---

# Logon Type

Remote WMI commonly involves:

```text
Logon Type 3
```

network logons.

Do not expect an interactive:

```text
Logon Type 2
```

simply because a remote process was created.

---

# NTLM Authentication

Where NTLM is used, additional telemetry can include:

```text
4776
NTLM Operational Logs
```

depending on environment and logging configuration.

---

# Kerberos Authentication

Where Kerberos is used:

```text
4768
4769
4771
```

may provide useful authentication context.

---

# Network Telemetry

Traditional remote WMI may generate:

```text
Source
  |
  v
135/TCP
  |
  v
Dynamic RPC
  |
  v
Target
```

This can be detected through:

```text
Firewall Logs
EDR Network Telemetry
NDR
Network Flow Data
```

---

# High Fan-Out WMI

Example:

```text
WS01
 |
 +--> SRV01:135
 +--> SRV02:135
 +--> SRV03:135
 +--> SRV04:135
 +--> SRV05:135
```

within a short period may indicate:

```text
Administrative Automation
Inventory
Management Software
Enumeration
Lateral Movement
```

Baseline legitimate systems before alerting.

---

# Common Legitimate WMI Sources

Examples may include:

```text
SCCM / Configuration Manager
Monitoring Platforms
Asset Inventory
Security Products
Administrative Jump Hosts
Automation Servers
Management Systems
```

These should be identified during detection engineering.

---

# Source-System Context

Compare:

```text
Management Server
      |
      v
100 WMI Connections
```

with:

```text
User Laptop
      |
      v
100 WMI Connections
```

The second pattern is usually much more unusual.

---

# Detect WMI Lateral Movement

A useful correlation is:

```text
4624 Network Logon
        |
        v
RPC / DCOM Connection
        |
        v
WMI Operation
        |
        v
WmiPrvSE.exe
        |
        v
Child Process
```

This provides stronger evidence than detecting:

```text
TCP 135
```

alone.

---

# Sysmon

Where Sysmon is deployed, useful telemetry may include:

```text
Process Creation
Network Connections
WMI Event Filters
WMI Consumers
WMI Bindings
```

depending on Sysmon configuration.

---

# WMI Event Subscription Detection

Monitor for unexpected creation of:

```text
__EventFilter
__EventConsumer
__FilterToConsumerBinding
```

especially when associated with:

```text
Command Execution
Scripts
Unknown Administrative Accounts
Unexpected Hosts
```

---

# WMI Hardening

A practical WMI hardening strategy includes:

```text
Restrict RPC Network Access
Apply Least Privilege
Limit Local Administrators
Restrict WMI Namespace Permissions
Restrict DCOM Remote Access
Use Windows Firewall
Separate Administrative Accounts
Use Privileged Administrative Workstations
Deploy Windows LAPS
Reduce NTLM
Monitor WMI Activity
Use Application Control
Use EDR
```

---

# Restrict RPC Exposure

Do not allow:

```text
Any Workstation
      |
      v
RPC / WMI
      |
      v
All Servers
```

unless operationally necessary.

Prefer:

```text
Approved Management Systems
          |
          v
RPC / WMI
          |
          v
Managed Systems
```

---

# Least Privilege

Review:

```text
Local Administrators
DCOM Permissions
WMI Namespace Permissions
Remote Enable
Execute Methods
```

Remove unnecessary principals.

---

# Protect Local Administrator Accounts

Reusable local administrator credentials can transform remote WMI into an effective lateral-movement path.

Deploy:

```text
Windows LAPS
```

where appropriate.

See:

[LAPS](laps.md)

---

# Reduce NTLM

Where operationally possible:

```text
Reduce NTLM
```

and prefer modern Kerberos-based authentication.

See:

[NTLM](ntlm.md)

---

# Application Control

Application control can help restrict the tools and interpreters available after remote process creation.

Examples include:

```text
WDAC
AppLocker
```

Application control should be designed as part of the broader endpoint-security architecture.

---

# ASR

Microsoft Defender Attack Surface Reduction includes protections that can affect process creation originating from WMI and PsExec.

Before enforcement:

```text
Audit
Evaluate Compatibility
Identify Legitimate Management Tools
Deploy Gradually
Monitor
```

Management products can legitimately rely on WMI.

---

# Do Not Disable WMI Blindly

WMI is deeply integrated into Windows management.

Disabling it without understanding dependencies can affect:

```text
Monitoring
Inventory
Management
Applications
Security Products
Administration
```

The goal should normally be:

```text
Restrict
Monitor
Harden
```

rather than:

```text
Disable Everything
```

---

# Safe Assessment Workflow

A controlled WMI assessment should follow:

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
Test Read-Only WMI Query
      |
      v
Determine Authorisation
      |
      v
Assess Security Impact
      |
      v
Minimal Execution Validation
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

# Step 3 - Read-Only Query

Where DCOM transport is specifically being tested:

```powershell
$option = New-CimSessionOption -Protocol Dcom
$session = New-CimSession -ComputerName srv01.corp.example -SessionOption $option
```

Then:

```powershell
Get-CimInstance -CimSession $session -ClassName Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber
```

---

# Step 4 - Determine Impact

Ask:

```text
Can the identity only query WMI?

Can it invoke methods?

Can it create processes?

Is it a local administrator?

Can it reach other systems?

Is this access required?
```

---

# Step 5 - Minimal Execution

Only if necessary:

```text
Create harmless marker
```

or execute another approved benign operation.

---

# Step 6 - Cleanup

Remove:

```text
Temporary Marker Files
Temporary Sessions
Other Test Artifacts
```

---

# Step 7 - Evidence

Record:

```text
Source
Target
Identity
Authentication
Transport
Namespace
Class
Method
Command
Result
Timestamp
Artifacts
Cleanup
```

---

# Evidence Checklist

Record:

```text
Target Host
Target IP
Domain
Operating System
Source Host
Source IP
Account
Account Type
TCP 135 Reachability
RPC Reachability
Authentication Protocol
WMI Namespace
Namespace Permissions
DCOM Permissions
Remote Enable
Execute Methods
Local Administrator Status
Read-Only Query Result
Remote Execution Result
Process Created
Files Created
Files Removed
Timestamp
Tool
Exact Command
```

Do not place:

```text
Passwords
NTLM Hashes
Kerberos Tickets
Private Keys
Sensitive Business Data
```

directly into reports unless strictly required and appropriately protected.

---

# Reporting WMI Findings

Do not report:

```text
WMI Enabled
```

or:

```text
TCP 135 Open
```

as vulnerabilities by themselves.

WMI and RPC are legitimate Windows management technologies.

Report the actual security weakness.

---

# Example Finding - Excessive WMI Access

```text
Finding:
Standard Domain Account Has Unnecessary Remote WMI Access to Server

Description:
The tested standard domain account was able to remotely access the
root\cimv2 WMI namespace on SRV01.

The account's documented business role did not require remote
management access to this server.

Read-only operating-system information was queried to validate the
access. No configuration changes were made.

Impact:
Compromise of the affected account could provide an attacker with
remote management capabilities against SRV01.

If the account is also permitted to invoke sensitive WMI methods, the
access may permit remote process creation and lateral movement.

Recommendation:
Review WMI namespace permissions, DCOM permissions and local group
membership.

Remove unnecessary Remote Enable and Execute Methods permissions and
restrict remote WMI network access to approved management systems.
```

---

# Example Finding - WMI Remote Execution

```text
Finding:
Domain Account Can Execute Processes Remotely Through WMI

Description:
The tested domain account had sufficient permissions to remotely invoke
the Win32_Process Create method on SRV01.

A harmless test command was used to confirm remote process creation.

No payloads, credential-access techniques or persistence mechanisms
were used.

Impact:
An attacker compromising the affected account could remotely execute
commands on SRV01 through WMI.

This provides a lateral-movement path and could expose server data,
credentials or additional systems depending on the target's role.

Recommendation:
Remove unnecessary administrative and WMI permissions from the
affected account.

Restrict RPC/WMI access to approved management systems and use
dedicated privileged identities for remote administration.
```

---

# Example Finding - Broad RPC Exposure

```text
Finding:
Remote WMI Infrastructure Reachable from Standard Workstation Network

Description:
Standard workstation networks were able to reach the RPC Endpoint
Mapper and associated remote-management services on multiple server
systems.

Although authentication and authorisation are still required, this
network path exposes remote management functionality directly to
lower-trust workstation networks.

Impact:
Compromise of a workstation together with suitable credentials could
provide an attacker with a direct path to attempt WMI-based lateral
movement against affected servers.

Recommendation:
Restrict RPC and WMI traffic using host and network firewalls.

Permit remote management only from approved administrative
workstations, jump hosts and management systems where operationally
possible.
```

---

# Example Finding - Reused Local Administrator Credential

```text
Finding:
Shared Local Administrator Credential Enables WMI Lateral Movement

Description:
The same local administrator credential was valid on multiple Windows
systems included in the assessment.

The credential provided sufficient remote rights to perform WMI
administration on more than one endpoint.

Impact:
Compromise of one affected endpoint could expose a reusable
administrative credential that permits lateral movement to other
systems.

Recommendation:
Deploy Windows LAPS or an equivalent centrally managed solution to
provide unique local administrator passwords.

Restrict workstation-to-workstation RPC/WMI access and monitor remote
administrative activity.
```

---

# Example Finding - Excessive Namespace Permission

```text
Finding:
Non-Administrative Group Has Excessive WMI Namespace Permissions

Description:
A non-administrative domain group was granted Remote Enable and Execute
Methods permissions on a WMI namespace.

The permissions exceeded those required for the group's documented
business function.

Impact:
Members of the group may be able to perform remote management
operations that were not intended by the system's access-control
design.

Depending on the exposed classes and methods, this may include
security-sensitive operations or remote execution.

Recommendation:
Review the namespace ACL and remove unnecessary permissions.

Grant only the minimum WMI rights required for the legitimate
management function and periodically review delegated WMI access.
```

---

# WMI Assessment Checklist

## Discovery

- [ ] Identify TCP 135
- [ ] Identify RPC reachability
- [ ] Identify target hostname
- [ ] Identify domain
- [ ] Identify operating system
- [ ] Identify WMI service state where authorised
- [ ] Identify relevant management networks

## Authentication

- [ ] Determine Kerberos availability
- [ ] Determine NTLM availability
- [ ] Prefer hostname when Kerberos is expected
- [ ] Verify DNS
- [ ] Verify time synchronisation
- [ ] Identify account type
- [ ] Distinguish domain and local accounts
- [ ] Avoid unnecessary credential testing

## Authorisation

- [ ] Review local Administrators
- [ ] Review DCOM remote permissions
- [ ] Review WMI namespace permissions
- [ ] Review Remote Enable
- [ ] Review Execute Methods
- [ ] Review delegated non-admin access
- [ ] Consider UAC remote restrictions
- [ ] Identify whether access is business-required

## Enumeration

- [ ] Query operating-system information
- [ ] Query computer information
- [ ] Query services where required
- [ ] Query processes where required
- [ ] Enumerate relevant namespaces
- [ ] Prefer read-only queries first
- [ ] Avoid unnecessary data collection

## Remote Execution

- [ ] Confirm execution testing is required
- [ ] Confirm target is in scope
- [ ] Confirm account is approved
- [ ] Use harmless command
- [ ] Avoid payload deployment
- [ ] Avoid credential dumping
- [ ] Avoid disabling security controls
- [ ] Record created processes
- [ ] Record temporary files
- [ ] Clean up test artifacts

## PowerShell

- [ ] Prefer modern CIM cmdlets where appropriate
- [ ] Understand CIM transport
- [ ] Use DCOM session option when specifically testing DCOM
- [ ] Remove CIM sessions
- [ ] Do not modify firewall configuration
- [ ] Do not modify DCOM configuration
- [ ] Do not modify namespace permissions

## Impacket

- [ ] Check installed Impacket version
- [ ] Run `impacket-wmiexec -h`
- [ ] Verify authentication mode
- [ ] Protect passwords from shell history
- [ ] Protect hashes
- [ ] Verify Kerberos configuration where applicable
- [ ] Understand SMB output dependency
- [ ] Stop after sufficient validation

## Pass-the-Hash

- [ ] Confirm PTH testing is authorised
- [ ] Determine whether NTLM is accepted
- [ ] Identify administrative rights
- [ ] Use approved test material only
- [ ] Avoid unnecessary host sweeps
- [ ] Protect hashes in evidence
- [ ] Review credential reuse
- [ ] Review Windows LAPS deployment

## Network Segmentation

- [ ] Review workstation-to-server RPC
- [ ] Review workstation-to-workstation RPC
- [ ] Review management-network restrictions
- [ ] Review host firewall
- [ ] Review remote-address restrictions
- [ ] Identify approved WMI management systems
- [ ] Identify unexpected RPC paths

## WMI Persistence

- [ ] Review `root\subscription`
- [ ] Review event filters
- [ ] Review consumers
- [ ] Review bindings
- [ ] Investigate unexpected subscriptions
- [ ] Do not remove unknown subscriptions without validation

## Detection

- [ ] Review WMI Activity Operational logs
- [ ] Monitor WmiPrvSE.exe
- [ ] Monitor child processes
- [ ] Monitor 4688
- [ ] Monitor 4624
- [ ] Monitor 4625
- [ ] Monitor 4648
- [ ] Monitor 4672
- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Monitor 4776
- [ ] Review RPC network telemetry
- [ ] Monitor WMI event subscriptions
- [ ] Monitor unusual source systems
- [ ] Monitor high fan-out RPC/WMI
- [ ] Baseline legitimate management systems

## Hardening

- [ ] Restrict RPC network exposure
- [ ] Restrict WMI to management systems
- [ ] Apply least privilege
- [ ] Review local Administrators
- [ ] Review namespace permissions
- [ ] Review DCOM permissions
- [ ] Deploy Windows LAPS
- [ ] Reduce NTLM
- [ ] Separate administrative identities
- [ ] Use privileged administrative workstations
- [ ] Deploy application control
- [ ] Review ASR protections
- [ ] Monitor WMI activity
- [ ] Avoid disabling WMI without dependency analysis

## Reporting

- [ ] Do not report WMI merely because it is enabled
- [ ] Do not report TCP 135 alone
- [ ] Identify actual excessive permission
- [ ] Identify affected identity
- [ ] Identify affected hosts
- [ ] Identify authentication protocol
- [ ] Identify namespace
- [ ] Identify execution capability
- [ ] Document minimal validation
- [ ] Explain lateral-movement impact
- [ ] Provide targeted remediation

---

# WMI Testing Model

The basic WMI model is:

```text
Client
  |
  v
WMI
  |
  v
Namespace
  |
  v
Class
  |
  v
Property / Method
```

The traditional remote model is:

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
Dynamic RPC
  |
  v
DCOM
  |
  v
WMI
```

The security model is:

```text
Identity
   |
   v
Authentication
   |
   v
DCOM Permission
   |
   v
Namespace Permission
   |
   v
WMI Operation
```

The read-only model is:

```text
Remote Identity
      |
      v
WMI
      |
      v
Win32_OperatingSystem
      |
      v
System Information
```

The execution model is:

```text
Remote Identity
      |
      v
WMI
      |
      v
Win32_Process
      |
      v
Create()
      |
      v
Remote Process
```

The lateral-movement model is:

```text
Compromised Identity
        |
        v
Remote WMI Rights
        |
        v
Target Server
        |
        v
Remote Process
```

The Pass-the-Hash model is:

```text
NTLM Hash
    |
    v
NTLM Authentication
    |
    v
WMI
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
WMI
 |
 v
Remote Execution
```

The WMIExec model is:

```text
Operator
   |
   v
WMI / DCOM
   |
   v
Remote Command
   |
   +--> Process Execution
   |
   +--> SMB Output Handling
   |
   v
Command Result
```

The detection model is:

```text
Remote Authentication
       |
       v
RPC / DCOM
       |
       v
WMI Operation
       |
       v
WmiPrvSE.exe
       |
       v
Child Process
```

The persistence model is:

```text
Event
 |
 v
__EventFilter
 |
 v
Binding
 |
 v
Consumer
 |
 v
Action
```

The hardening model is:

```text
Restricted RPC
      +
Least Privilege
      +
Restricted WMI ACLs
      +
Unique Local Credentials
      +
Administrative Separation
      +
Application Control
      +
WMI Monitoring
      =
Reduced WMI Attack Surface
```

For penetration testers:

```text
Do Not Ask:
"Can I run wmiexec?"

Ask:
"Why can this identity remotely invoke
management operations on this system?"
```

For defenders:

```text
Do Not Ask:
"Can we disable WMI?"

Ask:
"Which systems genuinely require remote WMI,
which identities require it,
and can we enforce that boundary?"
```

The complete WMI relationship is:

```text
Identity
   |
   v
Authentication
   |
   v
RPC / DCOM
   |
   v
WMI Authorisation
   |
   v
Namespace
   |
   v
Management Capability
   |
   v
Potential Remote Execution
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

Credential Access:

[Credential Access](credential-access.md)

The next detailed lateral-movement page is:

```text
docs/active-directory/dcom.md
```

---

# References

## Microsoft - Connecting to WMI on a Remote Computer

[Microsoft - Connecting to WMI on a Remote Computer](https://learn.microsoft.com/en-us/windows/win32/wmisdk/connecting-to-wmi-on-a-remote-computer){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Setting Up a Remote WMI Connection

[Microsoft - Setting Up a Remote WMI Connection](https://learn.microsoft.com/en-us/windows/win32/wmisdk/connecting-to-wmi-remotely-starting-with-vista){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Securing a Remote WMI Connection

[Microsoft - Securing a Remote WMI Connection](https://learn.microsoft.com/en-us/windows/win32/wmisdk/securing-a-remote-wmi-connection){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - User Account Control and WMI

[Microsoft - User Account Control and WMI](https://learn.microsoft.com/en-us/windows/win32/wmisdk/user-account-control-and-wmi){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - WMI Cmdlets

[Microsoft - About WMI Cmdlets](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_wmi_cmdlets?view=powershell-5.1){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

Verify current WMIExec syntax using:

```bash
impacket-wmiexec -h
```

---

## MITRE ATT&CK - Windows Management Instrumentation

[MITRE ATT&CK - T1047 Windows Management Instrumentation](https://attack.mitre.org/techniques/T1047/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

WMI is a legitimate and fundamental Windows management technology.

Its presence should not be treated as a vulnerability.

The important assessment questions are:

```text
Who Can Reach WMI?

Who Can Authenticate?

Which Authentication Protocol Is Used?

Who Has DCOM Remote Access?

Who Has Remote Enable?

Who Can Execute Methods?

Can the Identity Create Processes?

Is That Access Required?

Which Systems Can Initiate WMI Connections?
```

The preferred assessment sequence is:

```text
Discover RPC
     |
     v
Confirm Authentication
     |
     v
Test Read-Only WMI
     |
     v
Determine Permissions
     |
     v
Assess Execution Capability
     |
     v
Minimal Validation
     |
     v
Evidence
     |
     v
Cleanup
```

Do not immediately move from:

```text
TCP 135 Open
```

to:

```text
wmiexec
```

First determine whether the management relationship itself represents a security weakness.

Similarly:

```text
WMI Enabled
```

does not mean:

```text
WMI Vulnerability
```

The real issue may be:

```text
Excessive Administrative Rights
```

or:

```text
Reusable Credentials
```

or:

```text
Unnecessary RPC Exposure
```

or:

```text
Overly Broad WMI Namespace Permissions
```

When remote execution must be validated, use:

```text
Harmless Command
```

rather than:

```text
Payload
```

and stop once the security impact has been demonstrated.

A mature defensive design should aim for:

```text
Approved Administrative Identity
           |
           v
Hardened Management System
           |
           v
Restricted Management Network
           |
           v
RPC / WMI
           |
           v
Approved Managed Host
```

instead of:

```text
Any Workstation
      |
      v
RPC / WMI
      |
      v
Every Windows Server
```

WMI is therefore best understood as:

```text
Powerful Management Capability
            +
Weak Administrative Boundary
            =
Lateral-Movement Opportunity
```

The next page examines the broader remote COM technology underlying many Windows management paths:

```text
DCOM
```
