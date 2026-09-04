# System Center Operations Manager - SCOM

System Center Operations Manager, commonly abbreviated:

```text
SCOM
```

is Microsoft's enterprise monitoring platform within the System Center product family.

SCOM provides centralised monitoring for:

```text
Windows Servers
Windows Clients
Linux / UNIX Systems
Applications
Services
Databases
Network Devices
Infrastructure
Performance
Availability
Events
```

A simplified model is:

```text
Monitored System
      |
      v
SCOM Agent
      |
      v
Management Server
      |
      +--> Operational Database
      |
      +--> Data Warehouse
      |
      +--> Operations Console
      |
      +--> Web Console
```

SCOM is security relevant because the monitoring infrastructure maintains trusted relationships with potentially large numbers of systems and can execute monitoring workflows, scripts, tasks and recovery actions through agents.

!!! warning "Authorised testing only"
    SCOM is central management infrastructure. Do not execute arbitrary tasks, modify management packs, redistribute Run As accounts, alter monitoring configuration or deploy agents during a production assessment unless explicitly authorised. Prefer read-only enumeration, permission analysis and configuration review.

---

# Current SCOM Status

SCOM remains an actively supported System Center component.

As of 2026, Microsoft provides:

```text
System Center 2025 Operations Manager
```

with support for environments including Windows Server 2025.

System Center 2025 Operations Manager entered support on:

```text
1 November 2024
```

and Microsoft's current lifecycle lists:

```text
Mainstream Support End:
9 January 2030

Extended Support End:
10 January 2035
```

Therefore:

```text
SCOM
!=
Deprecated Technology
```

This is different from infrastructure such as MDT, which Microsoft has retired.

---

# Why SCOM Matters

SCOM can perform more than passive network monitoring.

Monitoring workflows can:

```text
Read Event Logs
Read Performance Counters
Query WMI
Execute Scripts
Execute Commands
Run Tasks
Run Recovery Actions
Access Applications
Access Databases
```

The security model can therefore resemble:

```text
SCOM
 |
 v
Monitoring Credential
 |
 v
Managed System
 |
 v
Monitoring / Task Capability
```

---

# SCOM Is Not Automatically a Vulnerability

Do not report:

```text
SCOM Is Installed
```

as a vulnerability.

Likewise:

```text
TCP 5723 Open
```

does not automatically represent a security weakness.

Instead determine:

```text
Who Administers SCOM?
Which Systems Are Monitored?
Which Credentials Are Stored?
How Are Run As Accounts Distributed?
What Privileges Do Agents Have?
Who Can Execute Tasks?
Who Can Modify Management Packs?
Which Systems Trust the Management Servers?
```

---

# SCOM Architecture

A typical SCOM environment contains a:

```text
Management Group
```

The management group is the fundamental SCOM administrative boundary.

Conceptually:

```text
Management Group
      |
      +--> Management Servers
      |
      +--> Gateway Servers
      |
      +--> Agents
      |
      +--> Operational Database
      |
      +--> Data Warehouse
      |
      +--> Reporting
      |
      +--> Operations Console
      |
      +--> Web Console
```

---

# Management Group

A management group contains the core SCOM infrastructure responsible for monitoring an environment.

At minimum, Microsoft describes a management group as containing:

```text
Management Server
Operational Database
Reporting Data Warehouse Database
```

Larger environments may contain multiple management servers and gateway servers.

---

# Management Server

The:

```text
Management Server
```

is a central SCOM component.

It:

```text
Communicates with Agents
Processes Monitoring Data
Coordinates Monitoring Workflows
Communicates with Databases
Provides Management Group Services
Supports Console Connections
```

A management group can contain multiple management servers.

---

# Management Server Security

Management servers should be treated as privileged infrastructure because they can interact with many monitored systems.

Conceptually:

```text
SCOM Management Server
       |
       +--> Server01
       +--> Server02
       +--> SQL01
       +--> DC01
       +--> Linux01
       +--> Application01
```

Compromise of a management server can therefore create significant operational and security impact.

---

# SCOM Agent

Windows systems are commonly monitored using the:

```text
Microsoft Monitoring Agent
```

or Operations Manager agent associated with the deployed SCOM version.

The agent receives monitoring configuration from SCOM and executes monitoring workflows locally.

Conceptually:

```text
Management Server
       |
       v
SCOM Agent
       |
       v
MonitoringHost.exe
       |
       v
Monitoring Workflow
```

---

# MonitoringHost.exe

An important SCOM process is:

```text
MonitoringHost.exe
```

Microsoft documents that this process performs monitoring activities such as:

```text
Reading Windows Event Logs
Reading Performance Counters
Querying WMI
Executing Monitors
Executing Scripts
Running Tasks
```

The account under which a particular instance runs determines its security context.

---

# Action Accounts

The account used by:

```text
MonitoringHost.exe
```

is known as an:

```text
Action Account
```

Different components can have different action accounts.

Examples include:

```text
Agent Action Account
Management Server Action Account
Gateway Server Action Account
```

---

# Agent Action Account

The:

```text
Agent Action Account
```

provides the default security context for monitoring workflows running on an agent.

Depending on configuration, this may be:

```text
Local System
```

or a lower-privileged account.

---

# Local System

Many SCOM agents historically operate using:

```text
NT AUTHORITY\SYSTEM
```

as the default action account.

This creates an important security relationship:

```text
SCOM Workflow
      |
      v
MonitoringHost.exe
      |
      v
SYSTEM
      |
      v
Monitored Computer
```

However, not every SCOM workflow necessarily executes as SYSTEM.

Run As profiles can provide different credentials.

---

# Least Privilege Action Accounts

Microsoft supports using lower-privileged action accounts.

The required permissions depend on:

```text
Management Packs
Monitoring Requirements
Tasks
Recoveries
Applications
```

Do not assume every agent requires local administrator privileges.

---

# Run As Accounts

SCOM supports:

```text
Run As Accounts
```

to provide credentials for workflows that require privileges different from the default action account.

Conceptually:

```text
Monitoring Workflow
       |
       v
Run As Profile
       |
       v
Run As Account
       |
       v
Target System
```

---

# Run As Profiles

A:

```text
Run As Profile
```

defines which security context should be used for particular monitoring workflows.

Management packs can define profiles for monitoring specific technologies.

Examples might involve:

```text
SQL Server
Active Directory
Applications
UNIX / Linux
Network Devices
```

---

# Why Run As Accounts Matter

Run As accounts can contain credentials for privileged identities.

Potential examples include:

```text
Database Monitoring Account
Application Monitoring Account
UNIX Monitoring Account
Privileged UNIX Account
Service Monitoring Account
```

The actual privileges depend on the environment.

---

# Run As Credential Distribution

SCOM can distribute Run As credentials to selected managed computers.

Microsoft specifically recommends distributing credentials only to the computers that require them.

Conceptually:

```text
Run As Account
      |
      v
SCOM
      |
      +--> Agent01
      |
      +--> Agent02
      |
      X--> Agent03
```

The principle is:

```text
Credential Distribution
Should Be Restricted
To Required Systems
```

---

# Credential Distribution Risk

Poorly scoped Run As account distribution can increase the credential exposure surface.

Conceptually:

```text
Privileged Credential
        |
        v
Distributed Broadly
        |
        v
Many Managed Systems
        |
        v
Increased Exposure
```

Therefore assess:

```text
Which Account?
Which Targets?
Which Profile?
Which Privileges?
Why Is Distribution Required?
```

---

# Do Not Extract SCOM Credentials During Routine Assessment

The presence of stored Run As credentials is normal SCOM functionality.

Do not attempt to extract or decrypt stored SCOM credentials from production systems unless the engagement explicitly authorises credential-access testing.

Prefer reviewing:

```text
Account Identity
Distribution Scope
Privileges
Run As Profile
Target Systems
```

---

# Default Run As Accounts

SCOM includes built-in Run As account concepts such as:

```text
Local System Windows Account
Network Service Windows Account
```

Management packs can introduce additional profiles.

---

# Management Server Action Account

The:

```text
Management Server Action Account
```

provides the default action context for workflows executed on management servers.

Microsoft recommends carefully selecting the privileges assigned to this account.

---

# Service Accounts

SCOM uses several service and operational accounts.

Depending on deployment architecture, these can include:

```text
Management Server Action Account
System Center Data Access Service Account
System Center Configuration Service Account
Data Warehouse Write Account
Data Reader Account
Agent Installation Account
Notification Action Account
```

The exact configuration varies by SCOM version and deployment.

---

# Service Account Security

For every SCOM-related account determine:

```text
Account Name
Account Type
Domain / Local
Group Membership
Logon Rights
Local Administrator Rights
SQL Permissions
Password Management
Interactive Logon Rights
Service Usage
```

---

# Do Not Assume Service Accounts Are Domain Admins

A SCOM service account should not automatically require:

```text
Domain Admins
```

membership.

If a SCOM service identity has excessive domain privilege, report the excessive privilege rather than simply reporting that it is a SCOM account.

---

# Operational Database

SCOM maintains an:

```text
Operational Database
```

on SQL Server.

The database stores:

```text
Management Group Configuration
Monitoring Configuration
Collected Monitoring Data
Operational State
```

---

# Data Warehouse

SCOM also uses a:

```text
Data Warehouse
```

for longer-term reporting and historical information.

Conceptually:

```text
Agents
  |
  v
Management Server
  |
  +--> OperationsManager Database
  |
  +--> OperationsManagerDW
```

Database names can vary, but commonly encountered defaults include:

```text
OperationsManager
OperationsManagerDW
```

---

# SQL Server

SQL Server is therefore a critical dependency.

Assess:

```text
SQL Server Location
Authentication
Service Accounts
Database Permissions
Network Exposure
TLS
Backups
Administrative Access
```

---

# SQL Security Relationship

```text
SCOM
 |
 v
SQL Server
 |
 +--> Operational Database
 |
 +--> Data Warehouse
```

Compromise of the database layer may affect:

```text
Monitoring Integrity
Configuration
Historical Data
Availability
```

---

# Gateway Server

SCOM can use:

```text
Gateway Servers
```

to monitor systems across trust boundaries or network boundaries.

Conceptually:

```text
Management Server
       |
       v
Gateway Server
       |
       v
Agents
```

Gateway servers reduce the need for direct management-server connectivity to every remote agent.

---

# Gateway Security

A gateway should also be treated as privileged monitoring infrastructure.

Review:

```text
Local Administrators
Certificates
Agent Relationships
Network Exposure
Service Accounts
Patch Level
```

---

# SCOM Certificates

Certificates can be used where Kerberos authentication is unavailable.

This is particularly relevant for:

```text
Untrusted Domains
Workgroups
Gateway Servers
Cross-Forest Monitoring
```

---

# Certificate Trust Model

```text
Certificate Authority
       |
       v
SCOM Certificate
       |
       v
Management / Gateway / Agent
       |
       v
Authenticated Communication
```

Certificate-template and private-key security therefore matter.

See:

[Active Directory Certificate Services](ad-cs/index.md)

---

# SCOM and Active Directory

SCOM can integrate with Active Directory for agent assignment.

Conceptually:

```text
Active Directory
      |
      v
SCOM Assignment Information
      |
      v
Agent
      |
      v
Management Server
```

---

# Active Directory Agent Assignment

SCOM supports Active Directory-based agent assignment.

Microsoft documents the use of:

```text
MOMADAdmin.exe
```

to prepare Active Directory for this functionality.

The process creates Active Directory objects used to publish management-group assignment information.

---

# Service Connection Points

SCOM can use:

```text
Service Connection Points - SCPs
```

for Active Directory-based assignment.

These objects can contain management-server connection information such as:

```text
FQDN
Port
Management Group Information
```

---

# Why SCPs Matter

SCOM-related Active Directory objects can help identify monitoring infrastructure.

Conceptually:

```text
Active Directory
      |
      v
SCOM SCP
      |
      v
Management Server
```

This is useful during authorised infrastructure discovery.

---

# Search Active Directory

A general authorised search can look for SCOM-related objects:

```powershell
Get-ADObject -LDAPFilter '(|(name=*SCOM*)(name=*MOM*)(name=*OperationsManager*))' -Properties *
```

Treat results as discovery leads.

Do not assume every:

```text
MOM
```

string represents current SCOM infrastructure.

---

# Search Computers

```powershell
Get-ADComputer -Filter * |
    Where-Object {
        $_.Name -match 'SCOM|MOM|OPS'
    } |
    Select-Object Name,DNSHostName
```

Hostname-based discovery is inherently incomplete.

---

# DNS Discovery

For a suspected management server:

```powershell
Resolve-DnsName 'scom01.corp.example'
```

Linux:

```bash
dig scom01.corp.example
```

See:

[Active Directory Integrated DNS](adidns.md)

---

# Installed SCOM Agent

On Windows, inspect installed software.

Example:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Where-Object {
        $_.DisplayName -match 'Operations Manager|Monitoring Agent'
    } |
    Select-Object DisplayName,DisplayVersion,Publisher
```

Also inspect the 32-bit registry view where relevant:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
    Where-Object {
        $_.DisplayName -match 'Operations Manager|Monitoring Agent'
    } |
    Select-Object DisplayName,DisplayVersion,Publisher
```

---

# SCOM Services

SCOM-related services may reveal installed components.

Search:

```powershell
Get-Service |
    Where-Object {
        $_.DisplayName -match 'System Center|Operations Manager'
    }
```

---

# HealthService

A commonly encountered SCOM agent service is:

```text
HealthService
```

Check:

```powershell
Get-Service -Name HealthService -ErrorAction SilentlyContinue
```

---

# Process Discovery

Check:

```powershell
Get-Process MonitoringHost -ErrorAction SilentlyContinue
```

Multiple:

```text
MonitoringHost.exe
```

processes can exist because SCOM can create instances for different monitoring credentials.

---

# Process Ownership

From an authorised administrative context:

```powershell
Get-CimInstance Win32_Process -Filter "Name='MonitoringHost.exe'" |
    ForEach-Object {
        $owner = Invoke-CimMethod -InputObject $_ -MethodName GetOwner

        [PSCustomObject]@{
            ProcessId = $_.ProcessId
            User      = $owner.User
            Domain    = $owner.Domain
        }
    }
```

This can help identify different monitoring contexts without accessing credential material.

---

# Agent Configuration

SCOM agents maintain configuration identifying their management group and management servers.

Exact registry locations can vary by SCOM version and deployment.

Prefer inspecting the local product configuration rather than hard-coding assumptions.

---

# Search Registry

A useful starting point is:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Microsoft Operations Manager' -ErrorAction SilentlyContinue
```

---

# Agent Management Groups

A commonly useful area is:

```text
HKLM\SOFTWARE\Microsoft\Microsoft Operations Manager\3.0\Agent Management Groups
```

Inspect:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Microsoft Operations Manager\3.0\Agent Management Groups' -ErrorAction SilentlyContinue
```

This can reveal configured management groups.

---

# Management Server Discovery

Recursively inspect the relevant agent configuration:

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Microsoft Operations Manager\3.0\Agent Management Groups' -Recurse -ErrorAction SilentlyContinue |
    Select-Object Name
```

Use this for discovery rather than modifying registry configuration.

---

# SCOM Network Ports

SCOM uses several network ports depending on architecture.

One of the most important is:

```text
TCP 5723
```

commonly used for agent-to-management-server communication.

---

# Agent Communication

Conceptually:

```text
SCOM Agent
    |
    | TCP 5723
    v
Management Server
```

The connection is normally initiated by the agent.

---

# Operations Console

The Operations console commonly communicates with a management server using:

```text
TCP 5724
```

Conceptually:

```text
Operations Console
       |
       | TCP 5724
       v
Management Server
```

---

# Connected Management Groups

SCOM can use:

```text
TCP 5724
```

for certain communication involving connected management servers.

Architecture should always be verified against the deployed SCOM version.

---

# Agent Push Installation

Agent push deployment requires additional Windows management protocols.

Microsoft documents requirements including:

```text
TCP 135
TCP 445
RPC Dynamic Ports
```

and legacy NetBIOS-related ports depending on configuration.

Modern Windows RPC dynamic ports commonly use:

```text
TCP 49152-65535
```

---

# Do Not Expose Push-Installation Ports Broadly

Agent push functionality can require significant remote-management connectivity.

Restrict:

```text
RPC
SMB
Administrative Services
```

to appropriate management infrastructure.

---

# UNIX and Linux Monitoring

SCOM can monitor:

```text
UNIX
Linux
```

systems.

Microsoft documents different communication requirements for cross-platform monitoring.

---

# UNIX / Linux Agent Maintenance

SCOM uses:

```text
SSH
```

for certain UNIX/Linux agent operations such as:

```text
Installation
Upgrade
Removal
Recovery
```

The default SSH port is typically:

```text
TCP 22
```

---

# UNIX / Linux Monitoring

SCOM also uses:

```text
WS-Management
```

for UNIX/Linux monitoring operations.

Microsoft's current SCOM firewall documentation lists:

```text
TCP 1270
```

for UNIX/Linux agent monitoring.

---

# UNIX / Linux Credential Security

SCOM supports:

```text
Unprivileged Monitoring Accounts
Privileged Accounts
Maintenance Accounts
```

depending on the required operation.

Do not unnecessarily configure:

```text
root
```

credentials where lower privilege and controlled elevation can satisfy the requirement.

---

# Sudo

SCOM supports controlled elevation for UNIX/Linux management.

A safer architecture can resemble:

```text
SCOM Account
    |
    v
Unprivileged Login
    |
    v
Restricted sudo
    |
    v
Required Monitoring Action
```

Review actual sudo rules rather than assuming privilege.

---

# SCOM Web Console

SCOM provides a:

```text
Web Console
```

for browser-based access to monitoring information.

The Web console provides less administrative functionality than the full Operations console.

---

# Operations Console vs Web Console

The:

```text
Operations Console
```

is the primary administrative interface.

The:

```text
Web Console
```

primarily provides access to monitoring data and tasks exposed through the monitoring workspace.

---

# Web Console Security

Assess:

```text
TLS
Authentication
Authorization
Network Exposure
IIS Configuration
Certificate
Session Security
Administrative Reachability
```

---

# Web Console Discovery

If a SCOM web endpoint is identified, perform normal authorised HTTP discovery.

Example:

```powershell
Test-NetConnection 'scomweb.corp.example' -Port 443
```

---

# TLS Inspection

Linux:

```bash
openssl s_client -connect scomweb.corp.example:443 -servername scomweb.corp.example
```

Review:

```text
Subject
Issuer
SAN
Validity
Trust Chain
```

---

# Do Not Assume the Web Console Is on 443

SCOM Web Console ports depend on installation choices and authentication configuration.

Microsoft documents specific defaults for certain deployment models, but organisations may use custom IIS bindings.

Always inspect the actual environment.

---

# SCOM Console Permissions

SCOM implements role-based access.

Users can be assigned roles controlling what they can:

```text
View
Monitor
Administer
Author
Operate
```

within the management group.

---

# User Roles

Review SCOM user roles for excessive membership.

Questions include:

```text
Who Has Full Administration?
Who Can Run Tasks?
Who Can Modify Monitoring?
Who Can Import Management Packs?
Who Can Access Sensitive Monitoring Data?
```

---

# Operations Manager Administrators

SCOM includes an administrative role with broad control over the management group.

Membership should be tightly restricted.

Conceptually:

```text
SCOM Administrator
       |
       v
Management Group
       |
       v
Monitoring Infrastructure
```

---

# SCOM Administrator Is Not Automatically Domain Admin

The distinction is important:

```text
SCOM Administrator
       !=
Domain Administrator
```

However, SCOM administrative capability can still be highly sensitive because of:

```text
Agents
Tasks
Run As Accounts
Management Packs
Monitored Servers
```

---

# Task Execution

SCOM can expose:

```text
Tasks
```

that operators can run against monitored objects.

Tasks may perform actions on managed systems.

Conceptually:

```text
SCOM Operator
      |
      v
Task
      |
      v
Agent
      |
      v
Target System
```

---

# Task Security Context

A task may run under:

```text
Default Action Account
```

or:

```text
Run As Profile
```

depending on its configuration.

Therefore:

```text
Task Permission
+
Execution Context
+
Target Scope
```

determines risk.

---

# Do Not Execute Arbitrary SCOM Tasks

During a production assessment, do not use SCOM as an execution platform merely because you have console access.

First determine:

```text
Task Function
Target
Security Context
Operational Impact
Authorisation
```

---

# Recovery Actions

SCOM management packs can define:

```text
Recovery Actions
```

that run when monitored conditions occur.

Examples might:

```text
Restart Service
Run Script
Perform Application Recovery
```

These capabilities make management-pack integrity important.

---

# Management Packs

A:

```text
Management Pack
```

defines monitoring logic for applications and infrastructure.

Management packs can contain:

```text
Discoveries
Rules
Monitors
Tasks
Recoveries
Views
Classes
Overrides
Scripts
```

---

# Management Pack Security

A simplified model is:

```text
Management Pack
      |
      v
Monitoring Workflow
      |
      v
SCOM Agent
      |
      v
Target System
```

Therefore, control over management-pack content can become security sensitive.

---

# Trusted Management Packs

Organisations should obtain management packs from trusted sources and maintain controlled import processes.

Assess:

```text
Source
Version
Publisher
Change Control
Administrative Permissions
Custom Management Packs
```

---

# Custom Management Packs

Custom management packs deserve particular review because they may contain organisation-specific:

```text
Scripts
Commands
Credentials References
Monitoring Logic
Recovery Logic
```

---

# Management Pack Modification

Do not modify a production management pack to demonstrate impact.

Instead establish:

```text
Who Can Modify / Import?
       |
       v
What Workflow Can Be Changed?
       |
       v
Where Is It Distributed?
       |
       v
Which Security Context Runs It?
```

---

# SCOM as a Management Plane

A useful security model is:

```text
SCOM
 |
 +--> Observe
 |
 +--> Query
 |
 +--> Execute Approved Tasks
 |
 +--> Run Monitoring Scripts
 |
 +--> Perform Recoveries
```

This means SCOM should be assessed as:

```text
Management Infrastructure
```

rather than simply:

```text
Monitoring Software
```

---

# SCOM and Tier 0

Determine whether SCOM monitors:

```text
Domain Controllers
Certificate Authorities
ADFS Servers
Privileged Access Workstations
Identity Servers
```

If so, determine which SCOM capabilities can interact with those systems.

---

# Domain Controller Agents

Special care is required when monitoring domain controllers.

Microsoft notes an important security consideration: Local System on a domain controller has domain-level privileges unavailable to Local System on an ordinary member server.

Therefore:

```text
SCOM Agent
      |
      v
Local System
      |
      v
Domain Controller
```

deserves careful security analysis.

---

# Tier 0 Model

```text
SCOM Administrator
       |
       v
Monitoring Workflow
       |
       v
Domain Controller Agent
       |
       v
Privileged Execution Context
```

The exact path depends on SCOM roles, management packs and task permissions.

Do not assume automatic Domain Admin capability without validating the actual configuration.

---

# Tier 0 Questions

Determine:

```text
Can SCOM Administrators Run Tasks on DCs?
Can They Modify Management Packs Applied to DCs?
Which Run As Accounts Reach DCs?
Which Action Account Is Used?
Who Controls the Management Servers?
```

---

# SCOM and Active Directory Monitoring

SCOM management packs can monitor Active Directory components.

This can require access to:

```text
Domain Controllers
Directory Services
DNS
Replication
Performance Counters
Event Logs
```

Review the privileges required by the specific management pack.

---

# SCOM and SQL Monitoring

SQL management packs may use dedicated:

```text
Run As Accounts
```

for database monitoring.

These accounts should receive only the permissions required by the management pack.

---

# SQL Monitoring Account

Conceptually:

```text
SCOM
 |
 v
SQL Run As Profile
 |
 v
SQL Monitoring Account
 |
 v
SQL Server
```

Review:

```text
SQL Role
Windows Rights
Distribution Scope
Credential Lifecycle
```

---

# SCOM and Network Devices

SCOM can monitor network devices through protocols such as:

```text
SNMP
```

depending on the management pack and configuration.

Assess:

```text
SNMP Version
Community Strings
Credentials
Network Reachability
Device Privileges
```

---

# SNMP

Legacy:

```text
SNMPv1
SNMPv2c
```

rely on community strings and provide weaker security than:

```text
SNMPv3
```

where supported.

Do not report SNMP merely because SCOM monitors a network device.

Report the actual insecure configuration.

---

# SCOM and Notifications

SCOM can generate notifications through mechanisms such as:

```text
Email
Scripts
Connectors
```

depending on configuration.

Notification infrastructure can introduce additional:

```text
Credentials
SMTP Servers
Scripts
External Integrations
```

---

# Notification Action Account

SCOM can use a:

```text
Notification Action Account
```

for notification-related operations.

Review its privileges and whether interactive access is necessary.

---

# SCOM Connectors

SCOM can integrate with external management systems through connectors and integrations.

Examples may include:

```text
ITSM
Ticketing
Automation
Monitoring Platforms
```

Every integration introduces another trust relationship.

---

# Integration Model

```text
SCOM
 |
 v
Connector
 |
 v
External Platform
```

Review:

```text
Authentication
Credentials
API Permissions
Network Access
TLS
Data Exposure
```

---

# SCOM Discovery from an Endpoint

A useful authorised workflow is:

```text
Endpoint
   |
   v
Check HealthService
   |
   v
Inspect Agent Configuration
   |
   v
Identify Management Group
   |
   v
Identify Management Server
   |
   v
Resolve DNS
   |
   v
Check Connectivity
```

---

# Step 1 - Check Agent

```powershell
Get-Service HealthService -ErrorAction SilentlyContinue
```

---

# Step 2 - Check Monitoring Processes

```powershell
Get-Process MonitoringHost -ErrorAction SilentlyContinue
```

---

# Step 3 - Identify Management Groups

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Microsoft Operations Manager\3.0\Agent Management Groups' -ErrorAction SilentlyContinue
```

---

# Step 4 - Inspect Configuration

```powershell
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Microsoft Operations Manager\3.0\Agent Management Groups' -Recurse -ErrorAction SilentlyContinue |
    Select-Object Name
```

---

# Step 5 - Resolve Management Server

```powershell
Resolve-DnsName 'scom01.corp.example'
```

---

# Step 6 - Test Agent Port

```powershell
Test-NetConnection 'scom01.corp.example' -Port 5723
```

This confirms only TCP connectivity.

---

# Step 7 - Identify Local Agent Context

```powershell
Get-CimInstance Win32_Service -Filter "Name='HealthService'" |
    Select-Object Name,StartName,State,PathName
```

---

# Step 8 - Identify MonitoringHost Contexts

From an authorised administrative context:

```powershell
Get-CimInstance Win32_Process -Filter "Name='MonitoringHost.exe'" |
    ForEach-Object {
        $owner = Invoke-CimMethod -InputObject $_ -MethodName GetOwner

        [PSCustomObject]@{
            PID    = $_.ProcessId
            Domain = $owner.Domain
            User   = $owner.User
        }
    }
```

---

# Step 9 - Identify SCOM Infrastructure

From AD, DNS and local configuration determine:

```text
Management Servers
Gateway Servers
Web Console
SQL Servers
Reporting Servers
```

---

# Step 10 - Review Administrative Model

Determine:

```text
SCOM Administrators
Operators
Authors
Read-Only Operators
Custom Roles
```

and their assigned scope.

---

# SCOM User Role Review

The Operations console provides the authoritative administrative view of configured SCOM user roles.

During assessment record:

```text
Role
Members
Profile
Scope
Tasks
Views
```

---

# Excessive Administrative Membership

A potential weakness is:

```text
Broad AD Group
      |
      v
SCOM Administrator Role
      |
      v
Management Group
```

Determine whether membership is justified.

---

# Nested Group Membership

Do not review only direct members.

A SCOM role might contain:

```text
CORP\Monitoring-Admins
```

which itself contains additional groups.

Resolve nested membership when determining effective access.

---

# Active Directory Group Enumeration

Example:

```powershell
Get-ADGroupMember -Identity 'Monitoring-Admins' -Recursive |
    Select-Object Name,SamAccountName,ObjectClass
```

Use the actual group identified in SCOM.

---

# Run As Account Review

For each Run As account document:

```text
Name
Type
Purpose
Run As Profile
Distribution
Privilege
Managed Systems
Owner
```

---

# Run As Distribution Review

The key question is:

```text
Does This Credential Need to Exist
on Every System Receiving It?
```

Prefer:

```text
Specific Distribution
```

over unnecessarily broad distribution.

---

# Run As Account Privilege Review

Determine whether accounts possess:

```text
Domain Admin
Local Administrator
SQL sysadmin
Database Owner
Application Administrator
Root / sudo
```

rights.

Do not assume such privileges are required.

---

# Credential Scope Model

```text
Run As Account
      |
      +--> Privilege
      |
      +--> Distribution
      |
      +--> Target Scope
      |
      v
Effective Risk
```

---

# SCOM Database Discovery

From authorised infrastructure documentation or server configuration identify:

```text
Operational Database Server
Data Warehouse Server
Reporting Server
```

Avoid indiscriminate SQL scanning across the environment.

---

# SQL Connectivity

Where explicitly in scope:

```powershell
Test-NetConnection 'sql01.corp.example' -Port 1433
```

The SQL instance may use a different or dynamic port.

---

# Database Permissions

SCOM setup configures required SQL permissions.

Review whether additional:

```text
sysadmin
db_owner
Server Administrator
```

rights have been granted unnecessarily.

---

# Database Backups

SCOM database backups can contain:

```text
Monitoring Data
Infrastructure Names
Configuration
Historical Information
```

Protect backup locations.

See:

[Windows and Active Directory Shares](shares.md)

---

# Monitoring Data Sensitivity

SCOM can collect sensitive operational data such as:

```text
Server Names
Application Names
Network Relationships
Events
Performance Data
Service State
Infrastructure Topology
```

Access to SCOM can therefore provide valuable reconnaissance even without task execution.

---

# Information Disclosure Model

```text
SCOM Read Access
      |
      v
Infrastructure Inventory
      |
      +--> Servers
      +--> Applications
      +--> Databases
      +--> Alerts
      +--> Network Devices
```

This can materially assist an attacker.

---

# Read-Only Operator

Even legitimate read-only monitoring access should be reviewed according to business need.

A read-only role may still expose significant infrastructure information.

---

# Management Pack Enumeration

During authorised review identify:

```text
Microsoft Management Packs
Vendor Management Packs
Custom Management Packs
Unsigned / Untrusted Content
Legacy Packs
```

---

# Custom Script Review

Custom management packs may contain:

```text
PowerShell
VBScript
Command Lines
Executable References
```

Review these for:

```text
Hard-Coded Credentials
Unsafe Paths
Writable Dependencies
Untrusted Downloads
Excessive Privilege
```

---

# Writable Script Dependency

A potential path is:

```text
Low-Privilege User
       |
       v
Modify Script
       |
       v
SCOM Workflow References Script
       |
       v
MonitoringHost.exe
       |
       v
Privileged Context
```

Do not modify the script in production.

Establish:

```text
Write Permission
+
Workflow Reference
+
Execution Context
+
Target Scope
```

---

# Unquoted or Unsafe Paths

Custom SCOM scripts and external executable references should be reviewed using normal Windows service and script-security principles.

The existence of a custom path is not automatically vulnerable.

Determine actual permissions and execution behaviour.

---

# SCOM Task Review

For sensitive tasks determine:

```text
Who Can Execute It?
What Does It Do?
Where Can It Run?
Which Account Runs It?
Does It Require Parameters?
```

---

# Recovery Review

Recovery workflows can automatically perform actions.

Determine:

```text
Trigger
Action
Security Context
Target
Frequency
```

---

# Do Not Trigger Production Recoveries

Avoid intentionally creating failure conditions to trigger recovery workflows unless the engagement specifically includes controlled resilience testing.

---

# SCOM and PowerShell

SCOM management packs and tasks may use PowerShell.

PowerShell itself is not the security weakness.

Assess:

```text
Script Source
Write Permissions
Execution Context
Credential Use
Parameters
Target Scope
```

---

# SCOM and WMI

MonitoringHost.exe can query WMI as part of monitoring.

See:

[WMI](wmi.md)

Do not assume that because SCOM uses WMI, ordinary users automatically gain remote WMI execution.

---

# SCOM and WinRM

SCOM infrastructure may coexist with WinRM for administrative or cross-platform functionality.

See:

[WinRM](winrm.md)

Assess actual configuration rather than inferring WinRM exposure from SCOM presence.

---

# SCOM and SMB

Agent push deployment can require SMB and RPC connectivity.

See:

[SMB](smb.md)

This makes network segmentation of management servers important.

---

# SCOM and NTLM

Depending on architecture and authentication conditions, Windows authentication may involve:

```text
Kerberos
NTLM
```

See:

[NTLM](ntlm.md)

---

# SCOM and Kerberos

Domain-connected SCOM infrastructure commonly benefits from Kerberos authentication where supported.

See:

[Kerberos](kerberos.md)

---

# SCOM and NTLM Relay

Do not assume SCOM is automatically vulnerable to NTLM relay.

Relay feasibility depends on:

```text
Authentication
Target Protocol
Signing
Channel Binding
EPA
Network Position
Credential Context
```

See:

[NTLM Relay](ntlm-relay.md)

---

# SCOM and AD CS

Certificate-authenticated SCOM relationships may depend on enterprise PKI.

See:

[Active Directory Certificate Services](ad-cs/index.md)

Review:

```text
Certificate Template
Private Key Protection
Enrollment Rights
EKU
Certificate Lifetime
Renewal
```

where relevant.

---

# SCOM and Trusts

SCOM may monitor systems across:

```text
Domains
Forests
Workgroups
Untrusted Networks
```

See:

[Trusts](trusts.md)

Gateway servers and certificates are particularly relevant where Kerberos trust cannot be used.

---

# SCOM and Lateral Movement

Compromised SCOM infrastructure can potentially create lateral-management paths because it communicates with large numbers of systems.

See:

[Lateral Movement](lateral-movement.md)

The important question is not merely:

```text
Can SCOM Reach the Host?
```

but:

```text
What Capability Does SCOM Have on the Host?
```

---

# SCOM and Pivoting

Management servers may have network access across multiple segments.

See:

[Pivoting](pivoting.md)

Do not use SCOM infrastructure as a pivot during a production assessment unless explicitly authorised.

Instead document unnecessary network reachability.

---

# SCOM and Credential Access

Run As accounts and service accounts make SCOM relevant to credential-access assessment.

See:

[Credential Access](credential-access.md)

Prefer privilege and distribution analysis over credential extraction.

---

# SCOM and SCCM

SCOM and Configuration Manager are different System Center products.

```text
SCOM
=
Monitoring

SCCM / Configuration Manager
=
Endpoint and Configuration Management
```

They may coexist in the same enterprise.

See:

[Microsoft Configuration Manager - SCCM](sccm.md)

---

# SCOM and WSUS

SCOM may monitor WSUS infrastructure but is not itself the update-distribution platform.

See:

[Windows Server Update Services - WSUS](wsus.md)

---

# Common Security Weaknesses

Potential SCOM weaknesses include:

```text
Excessive SCOM Administrator Membership
Overprivileged Service Accounts
Overprivileged Action Accounts
Overprivileged Run As Accounts
Broad Run As Credential Distribution
Weak Management Server Segmentation
Excessive Agent Push Connectivity
Insecure Custom Management Packs
Writable Monitoring Scripts
Excessive Task Permissions
Weak Certificate Management
Unnecessary Web Console Exposure
Overprivileged SQL Accounts
Weak UNIX / Linux Monitoring Credentials
Poorly Protected SCOM Backups
```

---

# Excessive SCOM Administration

Example:

```text
Helpdesk Group
     |
     v
SCOM Administrators
     |
     v
Management Group
```

If helpdesk staff require only alert visibility, full SCOM administration may violate least privilege.

---

# Overprivileged Run As Account

Example:

```text
SQL Monitoring
      |
      v
Run As Account
      |
      v
Domain Admin
```

The monitoring requirement may not justify domain-wide administrative privilege.

---

# Broad Credential Distribution

Example:

```text
Privileged Run As Account
       |
       v
Distributed to All Agents
       |
       v
500 Servers
```

If the credential is needed on only:

```text
5 SQL Servers
```

the distribution scope should be reduced.

---

# Overprivileged Agent Installation Account

Agent push deployment may use credentials with administrative rights on target systems.

Review whether:

```text
One Account
```

has unnecessary administrator access across the entire server estate.

---

# Weak Management Server Segmentation

Example:

```text
User VLAN
   |
   +--> RDP
   +--> SMB
   +--> WinRM
   +--> SQL
   |
   v
SCOM Management Server
```

Client or agent communication requirements do not automatically justify broad access to administrative interfaces.

---

# Writable Management Pack Dependency

Example:

```text
Domain User
    |
    v
Modify External Script
    |
    v
SCOM Management Pack
    |
    v
Agent
    |
    v
Privileged Execution
```

Validate the path without modifying production content.

---

# Excessive Task Permissions

A role may have permission to run operational tasks against systems beyond its intended responsibility.

Example:

```text
Application Operator
       |
       v
SCOM Task
       |
       v
Unrelated Production Servers
```

Review task scope and execution context.

---

# Weak UNIX Credential Configuration

Example:

```text
SCOM
 |
 v
Root Credential
 |
 v
Every Linux Server
```

If monitoring can be performed with an unprivileged account and restricted sudo, direct root credential usage may create unnecessary risk.

---

# Safe Assessment Workflow

A safe SCOM assessment can follow:

```text
Discover SCOM
     |
     v
Map Architecture
     |
     v
Identify Roles
     |
     v
Review Accounts
     |
     v
Review Run As Distribution
     |
     v
Review Tasks
     |
     v
Review Management Packs
     |
     v
Map Agent Scope
     |
     v
Review Network Exposure
     |
     v
Report
```

---

# Phase 1 - Discovery

Identify:

```text
Management Group
Management Servers
Gateway Servers
Agents
SQL Servers
Web Console
Reporting Server
```

---

# Phase 2 - Account Review

Identify:

```text
Action Accounts
Service Accounts
Run As Accounts
Agent Installation Accounts
Notification Accounts
SQL Accounts
```

---

# Phase 3 - Privilege Review

For each account determine:

```text
Domain Groups
Local Groups
SQL Roles
Logon Rights
Target Systems
Delegated Rights
```

---

# Phase 4 - Run As Review

Document:

```text
Profile
Account
Distribution
Privilege
Purpose
```

---

# Phase 5 - Role Review

Identify:

```text
Administrators
Operators
Authors
Read-Only Operators
Custom Roles
```

and resolve nested AD membership.

---

# Phase 6 - Management Pack Review

Prioritise:

```text
Custom Management Packs
Legacy Management Packs
Third-Party Management Packs
Scripts
Tasks
Recoveries
```

---

# Phase 7 - Agent Scope

Determine whether SCOM manages:

```text
Workstations
Member Servers
Domain Controllers
Certificate Authorities
SQL Servers
Linux Servers
Network Devices
```

---

# Phase 8 - Network Review

Assess:

```text
TCP 5723
TCP 5724
RPC
SMB
SQL
Web Console
SSH
WS-Management
Administrative Services
```

according to architecture.

---

# Phase 9 - Minimal Validation

Prefer:

```text
Configuration Evidence
Role Membership
ACL Evidence
Run As Distribution
Network Reachability
Task Configuration
Management Pack Content
```

over:

```text
Executing Tasks
Changing Management Packs
Extracting Credentials
Triggering Recoveries
Deploying Agents
```

---

# Phase 10 - Cleanup

Read-only assessment normally requires no SCOM cleanup.

If explicitly authorised temporary configuration was created:

```text
Remove Test Configuration
Verify Original State
Record Cleanup
```

---

# Detection

Defensive monitoring should cover:

```text
SCOM Administrative Logons
User Role Changes
Management Pack Changes
Run As Account Changes
Run As Distribution Changes
Task Execution
Management Server Activity
Agent Changes
SQL Changes
Web Console Access
```

---

# Windows Authentication Events

Useful events can include:

```text
4624
4625
4648
4672
```

depending on audit configuration and activity.

Unexpected privileged logons to SCOM infrastructure should be investigated.

---

# Process Creation

Where enabled:

```text
4688
```

can provide visibility into process execution on management servers and agents.

Particularly interesting relationships may involve:

```text
MonitoringHost.exe
      |
      v
Unexpected Child Process
```

Context matters because legitimate management packs can execute scripts and commands.

---

# MonitoringHost Child Processes

Possible legitimate children can include scripting or command interpreters depending on management packs.

Therefore:

```text
MonitoringHost.exe -> powershell.exe
```

is not automatically malicious.

Correlate:

```text
Management Pack
Task
Operator
Time
Target
Command
```

---

# PowerShell Logging

Where PowerShell-based management packs or tasks are used, appropriate PowerShell logging can provide additional visibility.

See:

[PowerShell](../windows/powershell.md)

if that page exists in the current documentation structure.

---

# SCOM Audit Trail

SCOM administrative changes should be correlated with:

```text
Operations Manager Logs
Windows Event Logs
SQL Activity
Active Directory Changes
Change Management
```

---

# Agent Changes

Monitor unexpected:

```text
Agent Installation
Agent Removal
Management Group Changes
Management Server Changes
```

---

# Active Directory Changes

Where AD-based agent assignment is used, monitor modifications to SCOM-related:

```text
Containers
Service Connection Points
Security Groups
```

Directory Service Changes auditing can provide event:

```text
5136
```

when appropriately configured.

---

# SQL Monitoring

Monitor SCOM database administration for:

```text
Unexpected Logons
Permission Changes
Backup Access
Configuration Changes
Database Availability
```

---

# Web Console Monitoring

Monitor:

```text
Authentication Failures
Unexpected Source Networks
Privileged Sessions
TLS Changes
IIS Configuration Changes
```

---

# Run As Changes

Changes to:

```text
Run As Account
Run As Profile
Distribution Scope
```

should receive particular attention.

A distribution change can alter where privileged credentials are made available for monitoring workflows.

---

# Management Pack Changes

Monitor:

```text
Import
Delete
Update
Override
Custom Script Changes
```

especially for management packs affecting privileged systems.

---

# Task Execution Monitoring

For sensitive SCOM tasks, capture:

```text
Operator
Task
Target
Timestamp
Result
```

where supported.

---

# SCOM Hardening

A strong SCOM deployment should include:

```text
Least Privilege
Restricted Administration
Restricted Run As Distribution
Secure Management Servers
Secure Gateway Servers
Secure SQL
Protected Certificates
Network Segmentation
Management Pack Governance
Monitoring
```

---

# Apply Least Privilege

Avoid granting:

```text
Domain Admin
Enterprise Admin
SQL sysadmin
Local Administrator
root
```

unless the specific monitoring requirement genuinely requires it.

---

# Restrict SCOM Administrators

Keep SCOM administrative membership small.

Use separate roles for:

```text
Monitoring
Application Operations
Authoring
Administration
Read-Only Access
```

where appropriate.

---

# Restrict Run As Distribution

Prefer:

```text
Specific Target Distribution
```

for privileged Run As accounts.

Avoid unnecessarily distributing sensitive credentials to all agents.

---

# Review Run As Accounts Regularly

Periodically verify:

```text
Account Still Required?
Privilege Still Required?
Distribution Still Required?
Owner Still Valid?
Password / Credential Lifecycle Current?
```

---

# Protect Management Servers

Management servers should have:

```text
Restricted Local Administrators
Restricted RDP
Restricted WinRM
Restricted SMB
EDR
Patch Management
Application Control Where Appropriate
Central Logging
```

---

# Protect Gateway Servers

Apply comparable controls to gateway servers.

They participate directly in the SCOM trust chain.

---

# Protect SQL

Restrict SQL access to required:

```text
SCOM Servers
Reporting Servers
Administrators
Backup Systems
```

---

# Protect Web Console

Use:

```text
TLS
Trusted Certificates
Restricted Network Exposure
Strong Authentication
Least Privilege
IIS Hardening
```

---

# Protect Certificates

For certificate-authenticated SCOM components:

```text
Protect Private Keys
Restrict Enrollment
Use Appropriate Templates
Monitor Renewal
Remove Expired Certificates
Revoke Compromised Certificates
```

---

# Secure Agent Push

Restrict the management server's ability to use:

```text
RPC
SMB
Administrative Shares
```

to only the systems requiring agent deployment or repair.

---

# Prefer Controlled Agent Deployment

Where operationally suitable, controlled software deployment may reduce the need for broad push-installation connectivity.

The appropriate method depends on enterprise architecture.

---

# Protect Management Packs

Use:

```text
Trusted Sources
Change Control
Code Review
Restricted Import Rights
Version Control for Custom Packs
Integrity Monitoring
```

---

# Review Custom Scripts

Custom monitoring scripts should not contain:

```text
Plaintext Passwords
API Secrets
Private Keys
Reusable Tokens
```

---

# Protect External Script Paths

If a management pack executes an external script, ensure ordinary users cannot modify:

```text
Script
Parent Directory
Referenced Executable
Configuration
```

---

# Restrict Task Execution

Grant task permissions only to users who require them.

High-impact tasks should have particularly limited scope.

---

# Secure UNIX / Linux Monitoring

Prefer:

```text
Unprivileged Monitoring
+
Restricted Elevation
```

over unnecessarily broad root-level access.

---

# Segment SCOM

A useful conceptual model is:

```text
Agents
  |
  | Required Monitoring Ports
  v
Management Servers
  |
  +--> SQL
  |
  +--> Gateway
  |
  +--> Administrative Network
```

Do not expose unrelated management services broadly.

---

# Tier SCOM Appropriately

If SCOM can execute privileged workflows on Tier 0 systems, protect the relevant SCOM infrastructure accordingly.

Do not treat:

```text
Monitoring Server
```

as low-value merely because its primary function is observation.

---

# Protect Backups

SCOM backups may contain:

```text
Database Content
Management Pack Configuration
Infrastructure Information
Historical Monitoring Data
```

Restrict access and protect backup credentials.

---

# Reporting SCOM Findings

Do not report:

```text
SCOM Is Installed
```

or:

```text
TCP 5723 Is Open
```

without identifying an actual security weakness.

---

# Potential Findings

Examples include:

```text
Excessive Membership in SCOM Administrators
```

```text
Privileged SCOM Run As Account Is Distributed to Unnecessary Agents
```

```text
SCOM Monitoring Account Has Excessive Domain Privileges
```

```text
Low-Privilege Users Can Modify a Script Executed by SCOM
```

```text
SCOM Management Server Administrative Services Are Accessible from User Networks
```

```text
SCOM Task Permissions Permit Excessive Management of Sensitive Servers
```

```text
SCOM Infrastructure Managing Tier 0 Systems Is Insufficiently Protected
```

```text
SCOM UNIX Monitoring Uses Unnecessarily Privileged Credentials
```

---

# Example Finding - Excessive SCOM Administrators

```text
Finding:
Excessive Membership in SCOM Administrative Role

Description:
The Operations Manager Administrators role contained a broad Active
Directory group whose members did not require full management-group
administrative privileges.

Impact:
Compromise of an unnecessarily privileged account could provide
administrative control over the SCOM management group.

Depending on the environment, this may provide access to monitoring
configuration, management packs, tasks, Run As configuration and
managed systems.

Recommendation:
Restrict SCOM administrative membership to dedicated authorised
administrators.

Create lower-privileged SCOM roles for operators who require only
monitoring, alert handling or application-specific access.

Periodically review nested Active Directory membership to identify
privilege expansion.
```

---

# Example Finding - Broad Run As Distribution

```text
Finding:
Privileged SCOM Run As Account Is Distributed to Unnecessary Agents

Description:
A privileged Run As account used for application monitoring was
distributed to substantially more SCOM agents than required for the
associated monitoring workflow.

The account was required only by a limited server population.

Impact:
Unnecessary credential distribution increases the number of systems
associated with the privileged monitoring credential and expands the
potential exposure surface.

Recommendation:
Configure explicit Run As account distribution and restrict the
credential to only the agents that require it.

Review the privileges of the account itself and reduce them to the
minimum required by the relevant management pack.
```

---

# Example Finding - Overprivileged Account

```text
Finding:
SCOM Monitoring Account Has Excessive Active Directory Privileges

Description:
A domain account used by SCOM for monitoring was a member of a
highly privileged Active Directory group.

The monitoring function did not require domain-wide administrative
rights.

Impact:
Compromise or misuse of the monitoring credential could provide
privileges substantially beyond those required for monitoring.

Recommendation:
Remove unnecessary privileged group membership.

Create a dedicated monitoring identity with only the rights documented
as necessary for the relevant SCOM management pack.

Review other SCOM service and Run As accounts for equivalent excessive
privilege.
```

---

# Example Finding - Writable Script

```text
Finding:
Low-Privilege Users Can Modify Script Executed by SCOM

Description:
A custom script referenced by an active SCOM monitoring workflow was
stored in a location writable by a broad domain principal.

The assessment verified the file permissions, workflow reference and
execution context without modifying the production script.

Impact:
An attacker with write access to the script could potentially influence
commands executed by the SCOM monitoring workflow.

The resulting impact depends on the workflow security context and the
systems to which the management pack is distributed.

Recommendation:
Restrict modification of SCOM scripts and their parent directories to
authorised SCOM administrators.

Store custom monitoring code in controlled locations and apply change
control, source control and integrity monitoring.
```

---

# Example Finding - Network Exposure

```text
Finding:
SCOM Management Server Administrative Interfaces Are Accessible from
User Networks

Description:
The SCOM management server exposed administrative services such as
RDP, SMB and WinRM to ordinary workstation networks.

These services were not required for normal agent-to-management-server
monitoring communication.

Impact:
A compromised workstation could directly interact with additional
administrative services on security-sensitive monitoring
infrastructure.

Recommendation:
Restrict administrative protocols to dedicated management networks and
approved administrative systems.

Permit only the SCOM communication paths required by the deployed
architecture between agents, gateways and management servers.
```

---

# Example Finding - Tier 0

```text
Finding:
SCOM Infrastructure Managing Tier 0 Systems Is Insufficiently Protected

Description:
SCOM agents were deployed to Active Directory Tier 0 systems,
including domain controllers.

The SCOM administrative and management-server security model did not
provide protection equivalent to the sensitivity of those monitored
systems.

Impact:
SCOM can execute monitoring workflows and approved tasks on managed
systems under configured action or Run As security contexts.

Compromise of sufficiently privileged SCOM infrastructure could
therefore affect security-critical identity systems.

Recommendation:
Review SCOM workflows, task permissions, action accounts and Run As
accounts that apply to Tier 0 systems.

Restrict SCOM administration, management-server access and relevant
monitoring credentials according to the privilege level of the systems
being managed.
```

---

# SCOM Assessment Checklist

## Discovery

- [ ] Identify SCOM management group
- [ ] Identify management servers
- [ ] Identify gateway servers
- [ ] Identify Windows agents
- [ ] Identify UNIX/Linux agents
- [ ] Identify operational database
- [ ] Identify data warehouse
- [ ] Identify reporting infrastructure
- [ ] Identify Operations console access
- [ ] Identify Web console

## Active Directory

- [ ] Search for SCOM-related infrastructure
- [ ] Identify AD-based agent assignment
- [ ] Identify SCOM SCPs where used
- [ ] Review SCOM-related security groups
- [ ] Review nested group membership
- [ ] Review relevant AD permissions

## Agents

- [ ] Identify `HealthService`
- [ ] Identify `MonitoringHost.exe`
- [ ] Identify management groups
- [ ] Identify management servers
- [ ] Determine action account
- [ ] Determine sensitive Run As contexts
- [ ] Identify agent version
- [ ] Identify Tier 0 agents

## Accounts

- [ ] Identify Management Server Action Account
- [ ] Identify Agent Action Accounts
- [ ] Identify Gateway Action Account
- [ ] Identify Data Access account
- [ ] Identify Configuration Service account
- [ ] Identify Data Warehouse Write account
- [ ] Identify Data Reader account
- [ ] Identify Agent Installation account
- [ ] Identify Notification Action account
- [ ] Identify UNIX/Linux accounts

## Account Privileges

- [ ] Review Domain Admin membership
- [ ] Review local administrator rights
- [ ] Review SQL privileges
- [ ] Review interactive logon
- [ ] Review RDP access
- [ ] Review WinRM access
- [ ] Review service logon
- [ ] Review account ownership
- [ ] Review credential lifecycle

## Run As Accounts

- [ ] Enumerate Run As accounts
- [ ] Identify Run As profiles
- [ ] Identify distribution scope
- [ ] Identify target systems
- [ ] Identify account privileges
- [ ] Identify account purpose
- [ ] Review unnecessary distribution
- [ ] Review stale accounts

## User Roles

- [ ] Identify SCOM Administrators
- [ ] Identify Operators
- [ ] Identify Authors
- [ ] Identify Read-Only Operators
- [ ] Identify custom roles
- [ ] Resolve nested AD groups
- [ ] Review role scope
- [ ] Review task permissions

## Management Packs

- [ ] Enumerate management packs
- [ ] Identify Microsoft packs
- [ ] Identify vendor packs
- [ ] Identify custom packs
- [ ] Identify legacy packs
- [ ] Review scripts
- [ ] Review tasks
- [ ] Review recoveries
- [ ] Review external dependencies
- [ ] Review import permissions

## Scripts

- [ ] Search for plaintext credentials
- [ ] Search for tokens
- [ ] Search for API keys
- [ ] Review file permissions
- [ ] Review parent-directory permissions
- [ ] Review execution context
- [ ] Review target scope
- [ ] Review change control

## Tasks

- [ ] Identify sensitive tasks
- [ ] Determine who can execute tasks
- [ ] Determine target scope
- [ ] Determine execution account
- [ ] Review parameters
- [ ] Avoid executing production tasks unnecessarily

## Recoveries

- [ ] Identify automatic recoveries
- [ ] Determine trigger
- [ ] Determine action
- [ ] Determine execution account
- [ ] Determine target scope
- [ ] Review potential operational impact

## SQL

- [ ] Identify SQL servers
- [ ] Identify databases
- [ ] Review SQL authentication
- [ ] Review SCOM SQL accounts
- [ ] Review excessive SQL roles
- [ ] Review network exposure
- [ ] Review TLS
- [ ] Review backups

## Network

- [ ] Review TCP 5723
- [ ] Review TCP 5724
- [ ] Review RPC requirements
- [ ] Review SMB requirements
- [ ] Review SQL connectivity
- [ ] Review Web console
- [ ] Review SSH for UNIX/Linux
- [ ] Review TCP 1270 where applicable
- [ ] Review administrative service exposure
- [ ] Review network segmentation

## Certificates

- [ ] Identify certificate-authenticated relationships
- [ ] Review issuing CA
- [ ] Review templates
- [ ] Review private-key protection
- [ ] Review enrollment rights
- [ ] Review expiration
- [ ] Review renewal
- [ ] Review revocation

## UNIX / Linux

- [ ] Identify monitoring accounts
- [ ] Identify privileged accounts
- [ ] Identify maintenance accounts
- [ ] Review SSH authentication
- [ ] Review sudo
- [ ] Review root usage
- [ ] Review credential distribution
- [ ] Review network exposure

## Tier 0

- [ ] Identify monitored domain controllers
- [ ] Identify monitored certificate authorities
- [ ] Identify monitored ADFS systems
- [ ] Identify privileged workstations
- [ ] Review action accounts
- [ ] Review Run As accounts
- [ ] Review task permissions
- [ ] Review management-pack scope
- [ ] Review SCOM administrator privilege
- [ ] Protect relevant SCOM infrastructure accordingly

## Detection

- [ ] Monitor SCOM administrative logons
- [ ] Monitor user-role changes
- [ ] Monitor Run As changes
- [ ] Monitor Run As distribution
- [ ] Monitor management-pack imports
- [ ] Monitor management-pack changes
- [ ] Monitor task execution
- [ ] Monitor agent changes
- [ ] Monitor management-group changes
- [ ] Monitor SQL administration
- [ ] Monitor Web console access
- [ ] Monitor unusual `MonitoringHost.exe` children

## Hardening

- [ ] Apply least privilege
- [ ] Restrict SCOM Administrators
- [ ] Restrict Run As distribution
- [ ] Reduce service-account privilege
- [ ] Protect management servers
- [ ] Protect gateway servers
- [ ] Protect SQL
- [ ] Protect Web console
- [ ] Protect certificates
- [ ] Secure agent push
- [ ] Protect management packs
- [ ] Protect scripts
- [ ] Restrict task execution
- [ ] Secure UNIX/Linux monitoring
- [ ] Segment SCOM infrastructure
- [ ] Protect backups
- [ ] Review Tier 0 implications

## Reporting

- [ ] Do not report SCOM presence alone
- [ ] Do not report TCP 5723 alone
- [ ] Identify actual privilege
- [ ] Identify actual distribution
- [ ] Identify affected systems
- [ ] Identify attack prerequisites
- [ ] Identify execution context
- [ ] Avoid extracting credentials unnecessarily
- [ ] Avoid modifying production management packs
- [ ] Provide architecture-specific remediation

---

# SCOM Testing Model

The basic model is:

```text
Monitored System
      |
      v
SCOM Agent
      |
      v
Management Server
      |
      v
SCOM
```

The workflow model is:

```text
Management Pack
      |
      v
Workflow
      |
      v
MonitoringHost.exe
      |
      v
Target
```

The credential model is:

```text
Run As Account
      |
      v
Run As Profile
      |
      v
Workflow
      |
      v
Target System
```

The distribution model is:

```text
Credential
    |
    v
SCOM
    |
    +--> Required Agent
    |
    +--> Required Agent
    |
    X--> Unnecessary Agent
```

The task model is:

```text
Operator
   |
   v
SCOM Task
   |
   v
Agent
   |
   v
Execution Context
   |
   v
Target
```

The management-pack integrity model is:

```text
Author
   |
   v
Management Pack
   |
   v
Script / Workflow
   |
   v
Agents
   |
   v
Managed Systems
```

The database model is:

```text
SCOM
 |
 +--> Operational Database
 |
 +--> Data Warehouse
```

The cross-domain model is:

```text
Management Server
       |
       v
Gateway
       |
       v
Remote Agents
```

The Tier 0 model is:

```text
SCOM Administrator
       |
       v
SCOM Capability
       |
       v
Agent on Tier 0
       |
       v
Identity Infrastructure
```

The most important distinction is:

```text
Monitoring
    !=
Passive Only
```

SCOM can perform:

```text
Monitoring
+
Tasks
+
Scripts
+
Recoveries
```

depending on configuration.

Another important distinction is:

```text
SCOM Administrator
    !=
Domain Administrator
```

but:

```text
SCOM Capability
+
Privileged Agent Context
+
Sensitive Target
```

can still create a significant security relationship.

For penetration testers:

```text
Do Not Ask:
"Can I use SCOM to execute something?"

Ask:
"Which authorised SCOM capabilities can
influence managed systems, under which
security context, and who controls them?"
```

For defenders:

```text
Do Not Ask:
"Is SCOM only monitoring?"

Ask:
"Which credentials, tasks, management
packs and execution contexts are trusted
across the monitored estate?"
```

The complete assessment model is:

```text
Identity
   |
   v
SCOM Role
   |
   v
Capability
   |
   +--> View
   |
   +--> Configure
   |
   +--> Task
   |
   +--> Management Pack
   |
   v
Execution Context
   |
   v
Managed Systems
   |
   v
Security Impact
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Enumeration:

[Enumeration](enumeration.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Credential Access:

[Credential Access](credential-access.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

SMB:

[SMB](smb.md)

WinRM:

[WinRM](winrm.md)

WMI:

[WMI](wmi.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

Pivoting:

[Pivoting](pivoting.md)

Trusts:

[Trusts](trusts.md)

AD CS:

[Active Directory Certificate Services](ad-cs/index.md)

Shares:

[Windows and Active Directory Shares](shares.md)

SCCM:

[Microsoft Configuration Manager - SCCM](sccm.md)

WSUS:

[Windows Server Update Services - WSUS](wsus.md)

MDT:

[Microsoft Deployment Toolkit - MDT](mdt.md)

The next infrastructure page is:

```text
docs/active-directory/adfs.md
```

followed by:

```text
docs/active-directory/rodc.md
```

---

# References

## Microsoft - Operations Manager

[Microsoft Learn - System Center Operations Manager](https://learn.microsoft.com/en-us/system-center/scom/welcome?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Operations Manager Key Concepts

[Microsoft Learn - Operations Manager Key Concepts](https://learn.microsoft.com/en-us/system-center/scom/key-concepts?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Service, User and Security Accounts

[Microsoft Learn - Operations Manager Service and Security Accounts](https://learn.microsoft.com/en-us/system-center/scom/plan-security-accounts?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Run As Accounts and Profiles

[Microsoft Learn - Run As Accounts and Profiles](https://learn.microsoft.com/en-us/system-center/scom/plan-security-runas-accounts-profiles?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Manage Run As Accounts

[Microsoft Learn - Manage Run As Accounts and Profiles](https://learn.microsoft.com/en-us/system-center/scom/manage-security-maintain-runas-profiles?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Operations Manager Agents

[Microsoft Learn - Operations Manager Agents](https://learn.microsoft.com/en-us/system-center/scom/plan-planning-agent-deployment?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Firewall Configuration

[Microsoft Learn - Configure a Firewall for Operations Manager](https://learn.microsoft.com/en-us/system-center/scom/plan-security-config-firewall?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Operations and Web Consoles

[Microsoft Learn - Compare the Operations and Web Console](https://learn.microsoft.com/en-us/system-center/scom/manage-consoles-comparison?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - UNIX and Linux Credentials

[Microsoft Learn - Security Credentials for UNIX and Linux Computers](https://learn.microsoft.com/en-us/system-center/scom/plan-security-crossplat-credentials?view=sc-om-2025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - System Center 2025 Operations Manager Lifecycle

[Microsoft Learn - System Center 2025 Operations Manager Lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/system-center-2025-operations-manager){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

SCOM should be treated as enterprise management infrastructure rather than merely a dashboard.

The basic relationship is:

```text
SCOM
 |
 v
Monitoring Infrastructure
 |
 v
Agents
 |
 v
Enterprise Systems
```

SCOM can perform:

```text
Observation
+
Collection
+
Script Execution
+
Task Execution
+
Recovery Actions
```

depending on management-pack and security configuration.

The credential relationship is:

```text
Run As Account
      |
      v
Run As Profile
      |
      v
Monitoring Workflow
      |
      v
Managed System
```

The security objective is therefore to minimise:

```text
Privilege
+
Credential Distribution
+
Administrative Scope
+
Network Exposure
```

while maintaining the required monitoring capability.

A secure SCOM deployment should answer:

```text
Who Controls SCOM?
      |
      v
Which Credentials Does It Use?
      |
      v
Where Are Those Credentials Distributed?
      |
      v
Which Tasks Can Be Executed?
      |
      v
Which Systems Are Managed?
      |
      v
What Security Context Is Used?
```

For high-value systems:

```text
Domain Controllers
Certificate Authorities
ADFS
Privileged Workstations
```

the monitoring relationship deserves particular scrutiny.

The strongest assessment does not use SCOM to execute arbitrary commands merely to demonstrate theoretical impact.

Instead establish:

```text
Administrative Permission
        +
SCOM Capability
        +
Execution Context
        +
Target Scope
        =
Demonstrated Risk
```

As of 2026, SCOM remains a supported Microsoft System Center product. System Center 2025 Operations Manager is under Microsoft's Fixed Lifecycle Policy, with mainstream support scheduled through January 2030 and extended support through January 2035.

The next infrastructure topic is:

```text
Active Directory Federation Services - AD FS
```
