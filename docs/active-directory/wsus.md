# Windows Server Update Services - WSUS

Windows Server Update Services, commonly abbreviated:

```text
WSUS
```

is a Microsoft server role used to centrally manage the distribution and approval of Microsoft updates inside an organisation.

Instead of every Windows endpoint independently obtaining updates from Microsoft Update, organisations can use WSUS to control:

```text
Which Updates Are Approved
Which Computers Receive Them
When Updates Are Deployed
Which Products Are Managed
Which Update Classifications Are Synchronised
```

A simplified model is:

```text
Microsoft Update
       |
       v
Upstream WSUS
       |
       +-------------------+
       |                   |
       v                   v
Downstream WSUS         Clients
       |
       v
    Clients
```

WSUS is security relevant because it participates in the software-update trust chain for potentially large numbers of Windows systems.

As of 2026, WSUS is deprecated and is no longer receiving new feature development. However, Microsoft continues to support existing WSUS capabilities for production deployments and provides security and quality updates according to the applicable Windows Server lifecycle.

!!! warning "Authorised testing only"
    WSUS controls software updates across managed Windows systems. Do not approve, decline, modify, publish or deploy updates during a production assessment unless explicitly authorised. Prefer read-only discovery, configuration review and policy analysis.

---

# Why WSUS Matters

Software-update infrastructure occupies a sensitive position.

Conceptually:

```text
Administrator
      |
      v
WSUS
      |
      v
Approved Update
      |
      v
Managed Computers
```

If update-management infrastructure is improperly protected, the potential impact can extend beyond the WSUS server itself.

Important assessment questions include:

```text
Who Administers WSUS?
Which Computers Use It?
How Do Clients Connect?
Is TLS Used?
How Is WSUS Configured?
Is WSUS Integrated with SCCM?
Who Can Modify Update Policy?
Is the Server Properly Segmented?
```

---

# WSUS Is Not Automatically a Vulnerability

The presence of WSUS is not a security finding.

Do not report:

```text
WSUS Is Installed
```

as a vulnerability.

Likewise:

```text
TCP 8530 Open
```

does not automatically prove exploitable update manipulation.

The assessment should determine the actual security configuration.

---

# WSUS Architecture

A basic deployment can look like:

```text
Internet
   |
   v
Microsoft Update
   |
   v
WSUS01
   |
   +--> Workstations
   +--> Servers
   +--> Test Systems
```

Larger environments may contain:

```text
Upstream WSUS Server
Downstream WSUS Servers
Replica Servers
Autonomous Servers
SQL Database
Windows Internal Database
Configuration Manager Software Update Point
```

---

# Upstream WSUS Server

A WSUS server can obtain update metadata and content from:

```text
Microsoft Update
```

or:

```text
Another WSUS Server
```

A server providing updates to another WSUS server is known as an:

```text
Upstream Server
```

---

# Downstream WSUS Server

A downstream server synchronises from another WSUS server.

Example:

```text
Microsoft Update
       |
       v
WSUS-HQ
       |
       +--> WSUS-EU
       |
       +--> WSUS-US
```

This can reduce:

```text
Internet Bandwidth
Administrative Duplication
WAN Traffic
```

and provide delegated update management.

---

# Autonomous Downstream Server

An autonomous downstream server can synchronise update information from an upstream WSUS server while maintaining independent control over certain configuration and approval decisions.

Conceptually:

```text
Upstream
   |
   v
Update Metadata
   |
   v
Autonomous WSUS
   |
   v
Local Approval Decisions
```

---

# Replica Server

A replica server inherits configuration and approvals from its upstream WSUS server.

Conceptually:

```text
Upstream WSUS
      |
      +--> Approvals
      +--> Groups
      +--> Configuration
      |
      v
Replica WSUS
```

This creates a stronger administrative dependency on the upstream server.

---

# WSUS Database

WSUS requires a database.

Depending on the environment, this may be:

```text
Windows Internal Database - WID
```

or:

```text
SQL Server
```

The database commonly contains:

```text
Update Metadata
Computer Information
Approval Information
Configuration
Synchronization State
```

---

# SUSDB

The WSUS database is commonly named:

```text
SUSDB
```

Conceptually:

```text
WSUS
 |
 v
SUSDB
 |
 +--> Updates
 +--> Computers
 +--> Approvals
 +--> Configuration
```

---

# Windows Internal Database

Smaller or standalone deployments commonly use:

```text
Windows Internal Database
```

Microsoft has deprecated Windows Internal Database in Windows Server and states that it will be removed in a future Windows release.

This should be considered during long-term WSUS architecture planning.

---

# SQL Server

Larger deployments may use SQL Server.

This introduces another security relationship:

```text
WSUS
 |
 v
SQL Server
 |
 v
SUSDB
```

Assess:

```text
SQL Network Exposure
SQL Authentication
Administrative Rights
Service Accounts
Database Permissions
Backup Security
```

---

# WSUS and IIS

WSUS uses:

```text
Internet Information Services - IIS
```

for web-based communication.

The WSUS web services provide functionality used by clients and other WSUS servers.

This makes IIS configuration part of the WSUS security model.

---

# Common WSUS Ports

Since Windows Server 2012, default WSUS ports are commonly:

```text
TCP 8530 - HTTP
TCP 8531 - HTTPS
```

Older or customised environments may use:

```text
TCP 80
TCP 443
```

Custom configurations are also possible.

Never assume the port based only on product defaults.

---

# Port Model

```text
Client
 |
 +--> TCP 8530 - HTTP
 |
 +--> TCP 8531 - HTTPS
 |
 v
WSUS
```

Where Configuration Manager integrates with WSUS, both HTTP and HTTPS ports may still have specific roles depending on the configuration.

---

# WSUS URL

A typical HTTP WSUS address might resemble:

```text
http://wsus01.corp.example:8530
```

A TLS-protected configuration may resemble:

```text
https://wsus01.corp.example:8531
```

---

# WSUS and Group Policy

Domain-joined Windows clients are commonly configured to use WSUS through Group Policy.

Conceptually:

```text
Active Directory
      |
      v
Group Policy
      |
      v
Windows Update Policy
      |
      v
WSUS Server
```

This means that Group Policy configuration is a major source of WSUS discovery information.

See:

[Group Policy](group-policy.md)

---

# Intranet Update Service Policy

An important Windows Update policy is:

```text
Specify intranet Microsoft update service location
```

This can identify the internal WSUS server.

Example configuration:

```text
https://wsus01.corp.example:8531
```

---

# Windows Registry

On systems configured through traditional Windows Update policy, relevant configuration commonly appears beneath:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate
```

---

# Read WSUS Configuration

PowerShell:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue
```

Interesting values can include:

```text
WUServer
WUStatusServer
```

---

# Example

```text
WUServer:
https://wsus01.corp.example:8531

WUStatusServer:
https://wsus01.corp.example:8531
```

This provides immediate infrastructure discovery.

---

# Windows Update AU Policy

Additional policy may exist beneath:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU
```

Query:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU' -ErrorAction SilentlyContinue
```

---

# UseWUServer

Historically, the value:

```text
UseWUServer
```

has indicated whether the Windows Update Agent should use the configured intranet update service.

Do not interpret one registry value in isolation on modern Windows.

Windows Update for Business, Configuration Manager and newer policy models can affect update behaviour.

---

# PowerShell Discovery

A simple local discovery workflow is:

```powershell
$wu = Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue

$wu |
    Select-Object WUServer,WUStatusServer
```

---

# Determine Whether WSUS Is Configured

```powershell
$wu = Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue

if ($wu.WUServer) {
    $wu.WUServer
}
```

---

# Group Policy Result

Use:

```cmd
gpresult /r
```

for a general applied-policy summary.

For a more detailed report:

```cmd
gpresult /h gpresult.html
```

Review the resulting report for Windows Update policy.

---

# RSOP

Where available:

```cmd
rsop.msc
```

can help inspect Resultant Set of Policy.

---

# Search SYSVOL

Group Policy files can also be reviewed from SYSVOL.

Example:

```powershell
Get-ChildItem '\\corp.example\SYSVOL' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'WUServer','WUStatusServer','8530','8531'
```

This is useful when tracing how WSUS configuration is delivered.

---

# Search GPO XML Reports

Administrators or authorised assessors with the Active Directory Group Policy module can generate GPO reports.

Example:

```powershell
Get-GPOReport -All -ReportType Xml -Path '.\gpo-report.xml'
```

Then search:

```powershell
Select-String -Path '.\gpo-report.xml' -Pattern 'WUServer','WUStatusServer','Windows Update'
```

---

# Identify WSUS Servers Through AD

Unlike some technologies such as SCCM, WSUS does not normally provide a dedicated Active Directory publication container comparable to:

```text
CN=System Management
```

for direct infrastructure discovery.

Instead, useful sources include:

```text
Group Policy
DNS
Computer Names
Configuration Manager
Local Registry
Network Services
Administrative Documentation
```

---

# Computer Naming

Search Active Directory for likely names:

```powershell
Get-ADComputer -Filter * |
    Where-Object {
        $_.Name -match 'WSUS|UPDATE|SUP'
    } |
    Select-Object Name,DNSHostName
```

Treat this only as discovery.

A hostname containing:

```text
WSUS
```

does not prove that the server currently provides WSUS.

---

# DNS

Once a WSUS hostname is discovered:

```powershell
Resolve-DnsName 'wsus01.corp.example'
```

Linux:

```bash
dig wsus01.corp.example
```

See:

[Active Directory Integrated DNS](adidns.md)

---

# Network Connectivity

From Windows:

```powershell
Test-NetConnection 'wsus01.corp.example' -Port 8530
```

TLS:

```powershell
Test-NetConnection 'wsus01.corp.example' -Port 8531
```

This confirms only TCP connectivity.

It does not prove:

```text
WSUS Vulnerability
```

---

# HTTP Response

For an authorised connectivity check:

```powershell
Invoke-WebRequest -Uri 'http://wsus01.corp.example:8530/' -UseBasicParsing
```

A response, redirect or error can still provide useful confirmation that an HTTP service exists.

Do not infer WSUS solely from the response.

---

# HTTPS Response

```powershell
Invoke-WebRequest -Uri 'https://wsus01.corp.example:8531/' -UseBasicParsing
```

Certificate validation errors should be investigated rather than bypassed automatically.

---

# TLS Certificate

Inspect the certificate presented by the HTTPS service.

Linux:

```bash
openssl s_client -connect wsus01.corp.example:8531 -servername wsus01.corp.example
```

Review:

```text
Subject
Issuer
Subject Alternative Names
Validity
Trust Chain
Protocol
Cipher
```

---

# WSUS Administration Console

WSUS administrators commonly manage the server through:

```text
Update Services
```

or the WSUS Administration Console.

The console provides management of:

```text
Updates
Computers
Synchronizations
Reports
Options
Approvals
```

Administrative access should be tightly controlled.

---

# WSUS PowerShell Module

Windows Server includes WSUS-related PowerShell functionality when the relevant administration components are installed.

Discover commands:

```powershell
Get-Command -Module UpdateServices
```

---

# Get-WsusServer

Where the UpdateServices module is installed:

```powershell
Get-Command Get-WsusServer -ErrorAction SilentlyContinue
```

A local administrative query may resemble:

```powershell
Get-WsusServer
```

The required permissions depend on the environment.

---

# Remote WSUS API Connection

The WSUS administration API can also connect to a specified server.

A common pattern is:

```powershell
[void][Reflection.Assembly]::LoadWithPartialName('Microsoft.UpdateServices.Administration')

$wsus = [Microsoft.UpdateServices.Administration.AdminProxy]::GetUpdateServer(
    'wsus01.corp.example',
    $true,
    8531
)
```

Here:

```text
$true
```

means SSL is expected.

Use:

```text
8530 / $false
```

only when assessing a known HTTP configuration.

---

# Read-Only Server Information

If the current account is authorised to query WSUS:

```powershell
$wsus.Name
```

and:

```powershell
$wsus.Version
```

can provide basic server information.

---

# Avoid Configuration Changes

Do not use WSUS administrative APIs during a normal assessment to:

```text
Approve Updates
Decline Updates
Change Computer Groups
Modify Synchronization
Change Products
Change Classifications
```

unless specifically authorised.

---

# WSUS Computer Groups

WSUS can organise clients into computer groups.

Example:

```text
All Computers
 |
 +--> Workstations
 |
 +--> Servers
 |
 +--> Test
 |
 +--> Production
```

Administrators can approve updates for specific groups.

---

# Why Computer Groups Matter

Computer groups influence deployment scope.

Conceptually:

```text
Update
  |
  v
Approval
  |
  v
Computer Group
  |
  v
Managed Systems
```

An administrator capable of approving updates for:

```text
Domain Controllers
```

has a more sensitive role than one restricted to:

```text
Test Workstations
```

---

# WSUS and Tier 0

Determine whether WSUS supplies updates to:

```text
Domain Controllers
Certificate Authorities
ADFS Servers
Privileged Access Workstations
Identity Management Servers
```

If so, WSUS should receive protection appropriate to the sensitivity of the systems it influences.

---

# Update Trust Model

The Windows update model includes cryptographic validation of Microsoft update content.

Conceptually:

```text
Microsoft
    |
    v
Signed Update
    |
    v
WSUS
    |
    v
Windows Client
    |
    v
Signature Validation
```

This is an important distinction.

Control of an ordinary WSUS server does not automatically mean an attacker can simply create an arbitrary executable and have Windows accept it as a legitimate Microsoft update.

---

# Why Signing Matters

Windows Update relies on signed content.

Therefore:

```text
WSUS Administrative Control
      !=
Arbitrary Microsoft Update Signing
```

Security assessment should distinguish between:

```text
Update Approval Control
Transport Security
Policy Configuration
Third-Party Publishing
Signing Infrastructure
Client Trust
```

---

# Third-Party Updates

Some environments use WSUS-related infrastructure to distribute third-party software updates.

This may involve additional:

```text
Signing Certificates
Publishing Services
Configuration Manager
Vendor Products
```

Third-party update signing deserves separate review because the trust model may differ from Microsoft-signed updates.

---

# Third-Party Publishing Risk Model

```text
Publishing Authority
       |
       v
Signing Certificate
       |
       v
Published Update
       |
       v
Managed Clients
```

Protect any certificate capable of signing trusted enterprise update content.

---

# WSUS and TLS

Microsoft recommends securing WSUS client communication with SSL/TLS.

A common hardened configuration uses:

```text
HTTPS
TCP 8531
```

for protected WSUS communication.

---

# Why TLS Matters

Without appropriate transport protection, the network path may expose WSUS communications to:

```text
Observation
Modification Attempts
Authentication Attacks
Infrastructure Impersonation
```

depending on the protocol and client configuration.

TLS strengthens server authentication and protects applicable WSUS web-service communication.

---

# TLS Does Not Mean Every Byte Uses HTTPS

WSUS architecture has historically used separate communication paths for metadata and update content.

In Configuration Manager-integrated WSUS environments, Microsoft documentation notes that HTTP may still be required for certain unencrypted content even when the Software Update Point is configured for HTTPS.

Therefore do not make a simplistic assumption that:

```text
8530 Open
=
WSUS Misconfigured
```

Assess the actual architecture.

---

# Certificate Requirements

For TLS-protected WSUS, the server certificate should correctly represent the names clients use.

Common considerations include:

```text
FQDN
Short Name
Aliases
Subject Alternative Names
Trusted Issuer
Validity
Private Key Protection
```

---

# Example

Clients use:

```text
wsus01.corp.example
```

The certificate should support that identity.

A mismatch can cause:

```text
Certificate Errors
Client Failures
Administrative Workarounds
```

---

# Self-Signed Certificates

A self-signed certificate can technically be used if clients explicitly trust it.

However, Microsoft recommends using a certificate from:

```text
Internal PKI
```

or:

```text
Trusted Certificate Provider
```

where appropriate.

---

# Internal PKI

An organisation using Active Directory Certificate Services may issue the WSUS web certificate.

See:

[Active Directory Certificate Services](ad-cs/index.md)

The security chain becomes:

```text
Enterprise CA
     |
     v
WSUS Certificate
     |
     v
WSUS
     |
     v
Clients
```

---

# WSUS and HTTP

Legacy deployments may use:

```text
http://wsus01.corp.example:8530
```

Microsoft's current WSUS best-practice guidance recommends configuring SSL for client communication.

Therefore, a production HTTP-only deployment deserves review.

However, the actual finding and severity should consider:

```text
Network Segmentation
Authentication
Update Signing
Client Configuration
Attack Preconditions
SCCM Integration
```

---

# WSUS Policy Security

Because clients learn their update service from policy, control of that policy is security sensitive.

Conceptually:

```text
GPO Control
    |
    v
Windows Update Policy
    |
    v
WSUS Location
    |
    v
Clients
```

An identity that can modify the relevant GPO may potentially redirect update infrastructure configuration.

See:

[ACL and ACE](acl-ace.md)

and:

[Group Policy](group-policy.md)

---

# Identify WSUS GPO

A useful workflow is:

```text
Client
 |
 v
Read WUServer
 |
 v
Identify GPO
 |
 v
Review GPO ACL
 |
 v
Identify Who Can Modify It
```

---

# GPO ACL Review

If a WSUS policy is identified, review who can modify it.

Example:

```powershell
Get-GPPermission -Name 'WSUS Policy' -All
```

Look for unnecessary:

```text
GpoEdit
GpoEditDeleteModifySecurity
```

permissions.

---

# WSUS Policy Attack Path

A security-relevant relationship may look like:

```text
Low-Privilege Group
       |
       v
Can Modify WSUS GPO
       |
       v
Windows Update Configuration
       |
       v
Large Computer Population
```

The exact impact requires careful validation.

---

# WSUS Administrative Groups

On a WSUS server, administrative delegation may involve local groups associated with WSUS administration and reporting.

A commonly encountered group is:

```text
WSUS Administrators
```

and environments may also contain:

```text
WSUS Reporters
```

Review the actual local groups on the server rather than assuming they exist.

---

# Local Group Enumeration

On the WSUS server:

```powershell
Get-LocalGroup |
    Where-Object {
        $_.Name -match 'WSUS'
    }
```

---

# Group Membership

```powershell
Get-LocalGroupMember -Group 'WSUS Administrators' -ErrorAction SilentlyContinue
```

Record:

```text
Direct Users
Domain Groups
Nested Groups
Service Accounts
```

---

# Why WSUS Administrators Matter

An administrator can influence:

```text
Update Approvals
Synchronization
Computer Groups
WSUS Configuration
```

depending on assigned rights.

These identities should therefore be treated as privileged update-management accounts.

---

# WSUS Administrator Is Not Automatically Domain Admin

The distinction is:

```text
WSUS Administrator
       !=
Domain Administrator
```

However, if the WSUS server manages privileged systems, WSUS administration may still create an important security path.

---

# Service Accounts

Standalone WSUS deployments do not necessarily require a dedicated privileged domain service account.

However, surrounding infrastructure may introduce:

```text
SQL Accounts
IIS Application Pool Identities
Configuration Manager Accounts
Backup Accounts
Monitoring Accounts
```

Review actual identities and privileges.

---

# IIS Application Pools

WSUS uses IIS application pools.

A well-known example is:

```text
WsusPool
```

Inspect locally:

```powershell
Import-Module WebAdministration

Get-ChildItem IIS:\AppPools |
    Where-Object {
        $_.Name -match 'WSUS'
    }
```

---

# IIS Sites

Inspect:

```powershell
Get-Website
```

Look for WSUS-related sites and bindings.

---

# IIS Bindings

```powershell
Get-WebBinding
```

Review:

```text
HTTP
HTTPS
Port
Hostname
Certificate Binding
```

---

# Do Not Modify IIS During Discovery

Avoid changing:

```text
Bindings
Certificates
Authentication
Application Pools
SSL Requirements
```

during an assessment unless the engagement explicitly includes configuration remediation.

---

# WSUS Content Directory

WSUS can store downloaded update files locally.

The content directory is selected during configuration.

Example conceptual path:

```text
D:\WSUS\WsusContent
```

Do not assume a specific path.

---

# Discover WSUS Content Path

Administrators can inspect WSUS configuration or filesystem structure.

A common WSUS installation may contain directories such as:

```text
WSUS
WsusContent
UpdateServicesPackages
```

Treat discovered content directories as server infrastructure rather than ordinary writable shares.

---

# Content Directory Permissions

Review:

```text
Owner
NTFS Permissions
Inherited Permissions
Unexpected Write Access
```

Do not modify update content.

---

# Safe ACL Review

```powershell
Get-Acl 'D:\WSUS' |
    Format-List Owner,AccessToString
```

Adjust the path to the actual installation.

---

# Why Content Permissions Matter

The basic question is:

```text
Can an Unauthorised Identity Modify
Update-Related Server Content?
```

However, remember that Microsoft update signature verification significantly affects the practical impact of raw file modification.

Do not automatically claim arbitrary code execution merely because a content directory is writable.

---

# WSUS and SCCM

Microsoft Configuration Manager uses WSUS as part of its software-update infrastructure.

The Configuration Manager role is called:

```text
Software Update Point - SUP
```

Conceptually:

```text
Microsoft Update
      |
      v
WSUS
      |
      v
Software Update Point
      |
      v
Configuration Manager
      |
      v
Managed Clients
```

See:

[Microsoft Configuration Manager - SCCM](sccm.md)

---

# Software Update Point

When Configuration Manager is present, WSUS is typically managed through Configuration Manager rather than directly through the WSUS console.

Do not treat a Configuration Manager-managed WSUS server as a standalone WSUS deployment.

---

# SCCM and WSUS Administration

Microsoft recommends that administrators avoid manually managing update approvals through the WSUS console when WSUS is being used by Configuration Manager.

Configuration Manager should control the software-update workflow.

---

# SCCM Port Considerations

For Configuration Manager Software Update Points, common WSUS ports remain:

```text
8530
8531
```

Custom ports can be configured.

When HTTPS is enabled for the Software Update Point, Microsoft documents that the HTTP port may still need to remain open for certain unencrypted data such as specific update EULAs.

---

# WSUS and Proxy Servers

A WSUS server may use an outbound proxy to reach Microsoft Update.

Assess:

```text
Proxy Configuration
Authentication
Network Reachability
Credential Handling
```

Do not assume proxy credentials exist.

---

# Synchronization

WSUS periodically synchronises:

```text
Update Metadata
Product Information
Classification Information
```

from its configured upstream source.

The upstream source may be:

```text
Microsoft Update
```

or:

```text
Another WSUS Server
```

---

# Synchronization Chain

```text
Microsoft Update
       |
       v
WSUS-HQ
       |
       v
WSUS-BRANCH
       |
       v
Clients
```

A security assessment should identify the authoritative upstream source.

---

# Disconnected WSUS

Some high-security environments use disconnected WSUS architectures.

Conceptually:

```text
Internet-Connected WSUS
        |
        v
Export
        |
        v
Controlled Transfer
        |
        v
Disconnected WSUS
```

Such environments require different assessment assumptions.

Do not expect direct Microsoft Update connectivity.

---

# Update Classifications

WSUS can synchronise different update classifications.

Examples can include:

```text
Critical Updates
Security Updates
Definition Updates
Updates
Update Rollups
Upgrades
```

The exact available classifications depend on Microsoft Update metadata.

---

# Products

Administrators also choose which Microsoft products to synchronise.

Overly broad selections can increase:

```text
Database Size
Synchronization Time
Maintenance Requirements
Storage Use
```

This is primarily an operational concern unless it creates a security consequence.

---

# WSUS Maintenance

WSUS requires regular maintenance.

Important activities include:

```text
Declining Superseded Updates
Removing Obsolete Updates
Database Maintenance
Server Cleanup
Reindexing Where Appropriate
Monitoring Synchronization
```

Poor maintenance can lead to:

```text
Slow Console
Client Scan Failures
Database Growth
Synchronization Problems
Application Pool Recycling
```

---

# Availability Is Security Relevant

For patch infrastructure:

```text
Availability
```

matters.

A failing WSUS service can result in:

```text
Delayed Patching
Missing Security Updates
Reduced Compliance Visibility
```

Therefore operational health can have direct security consequences.

---

# WsusPool Memory

Large WSUS environments may require careful IIS application-pool configuration.

Microsoft's current best-practice guidance includes recommendations for improving WSUS stability.

Do not blindly copy tuning values between environments.

Capacity depends on:

```text
Number of Clients
Products
Classifications
Update History
SCCM Integration
Server Resources
```

---

# WSUS Server Cleanup

The WSUS Server Cleanup Wizard and related administrative functions can remove obsolete data.

This is an administrative operation.

Do not run cleanup during a penetration test unless explicitly requested.

---

# Update Approval

WSUS administrators can approve updates for deployment.

Conceptually:

```text
Update
 |
 v
Approval
 |
 v
Computer Group
 |
 v
Client
```

Approval is legitimate administrative functionality.

The security issue is:

```text
Who Can Approve What for Whom?
```

---

# Declining Updates

WSUS administrators can also decline updates.

Misuse could affect patch availability.

Therefore unauthorised administrative access can create:

```text
Confidentiality Risk
Integrity Risk
Availability Risk
```

depending on the capability obtained.

---

# WSUS Security Model

A useful model is:

```text
Microsoft Update
      |
      v
Signed Update
      |
      v
WSUS
      |
      v
Approval
      |
      v
Computer Group
      |
      v
Windows Client
```

Security controls exist at multiple layers:

```text
Microsoft Signing
TLS
IIS
WSUS Administration
Group Policy
Windows Update Agent
Network Segmentation
```

---

# HTTP WSUS Assessment

If clients use:

```text
http://wsus01:8530
```

record the configuration.

Then determine:

```text
Is HTTPS Available?
Is HTTP Required?
Is SCCM Involved?
Which Web Services Use TLS?
Which Networks Can Reach WSUS?
What Authentication Is Used?
```

Do not jump directly from:

```text
HTTP
```

to:

```text
Remote Code Execution
```

---

# Historical WSUS Attack Research

Security research has historically demonstrated attacks against improperly secured WSUS configurations, especially where clients communicated with WSUS over HTTP and an attacker could obtain a privileged network position.

This class of research demonstrates why:

```text
Transport Security
Network Segmentation
Policy Protection
```

matter.

However, modern assessment should validate current Windows behaviour and configuration rather than assuming historical techniques still work unchanged.

---

# WSUS Attack Preconditions

A conceptual attack chain might require:

```text
Network Position
      |
      v
Client Uses Insecure WSUS Transport
      |
      v
Traffic Manipulation Opportunity
      |
      v
Suitable Trusted Update Behaviour
      |
      v
Security Impact
```

Each step must be demonstrated or supported.

---

# Do Not Overstate MITM Risk

Finding:

```text
HTTP WSUS
```

does not by itself prove:

```text
Any User Can Compromise Every Client
```

Consider:

```text
Network Position
Routing
Segmentation
Update Signing
Client Configuration
Authentication
Publishing Configuration
```

---

# WSUS and NTLM

IIS-based WSUS services may participate in Windows authentication depending on the endpoint and configuration.

Where NTLM is observed, assess it within the broader Windows authentication model.

See:

[NTLM](ntlm.md)

---

# WSUS and NTLM Relay

Do not assume:

```text
WSUS Uses IIS
      |
      v
NTLM Relay Works
```

Relay feasibility depends on:

```text
Authentication
Endpoint
EPA
TLS
Signing
Target Service
Identity
Network Position
```

See:

[NTLM Relay](ntlm-relay.md)

---

# Extended Protection for Authentication

Where Windows authentication is used with IIS, Extended Protection for Authentication can reduce certain credential-relay risks.

Whether it is supported and appropriate must be evaluated for the specific WSUS and Windows Server configuration.

Do not enable it blindly without compatibility testing.

---

# WSUS and Kerberos

Where Windows Integrated Authentication is used, Kerberos may be preferred over NTLM when the service identity and SPNs are configured correctly.

See:

[Kerberos](kerberos.md)

---

# WSUS and DNS

Clients normally connect to a WSUS hostname.

Therefore:

```text
DNS
```

is part of the trust path.

Conceptually:

```text
Client
 |
 v
DNS
 |
 v
WSUS Hostname
 |
 v
WSUS Server
```

See:

[Active Directory Integrated DNS](adidns.md)

---

# DNS Security Questions

Assess:

```text
Who Can Modify the WSUS DNS Record?
Is Dynamic Update Appropriately Restricted?
Are Stale Records Present?
Are Aliases Used?
Does the TLS Certificate Match the Name?
```

---

# WSUS and AD CS

If WSUS uses an enterprise-issued TLS certificate:

```text
AD CS
 |
 v
WSUS Certificate
 |
 v
IIS
 |
 v
Clients
```

Certificate-template security therefore indirectly affects WSUS transport security.

See:

[Active Directory Certificate Services](ad-cs/index.md)

---

# WSUS and Shares

WSUS servers may contain:

```text
Content Directories
Backup Locations
SQL Backups
Administrative Files
```

Review accessible shares carefully.

See:

[Windows and Active Directory Shares](shares.md)

---

# WSUS and Backup Security

WSUS backup infrastructure may contain:

```text
SUSDB Backups
Server Configuration
IIS Configuration
Certificates
Operational Information
```

Protect backups using the same principles as other management infrastructure.

---

# WSUS Discovery Workflow

A safe workflow is:

```text
Endpoint
   |
   v
Read Windows Update Policy
   |
   v
Identify WSUS Hostname
   |
   v
Resolve DNS
   |
   v
Check Connectivity
   |
   v
Determine HTTP / HTTPS
   |
   v
Identify GPO
   |
   v
Review GPO Permissions
   |
   v
Review WSUS Administration
   |
   v
Map Managed Systems
```

---

# Step 1 - Inspect Local Policy

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' -ErrorAction SilentlyContinue
```

Record:

```text
WUServer
WUStatusServer
```

---

# Step 2 - Identify Update Policy

```cmd
gpresult /h gpresult.html
```

Determine which GPO supplies the WSUS configuration.

---

# Step 3 - Resolve Server

```powershell
Resolve-DnsName 'wsus01.corp.example'
```

---

# Step 4 - Test Connectivity

```powershell
Test-NetConnection 'wsus01.corp.example' -Port 8530
```

and:

```powershell
Test-NetConnection 'wsus01.corp.example' -Port 8531
```

---

# Step 5 - Determine Transport

Identify whether clients are configured for:

```text
HTTP
HTTPS
```

Do not infer this solely from open ports.

Use the actual Windows Update policy.

---

# Step 6 - Review Certificate

For HTTPS:

```bash
openssl s_client -connect wsus01.corp.example:8531 -servername wsus01.corp.example
```

Review:

```text
Name
Issuer
Validity
Trust
```

---

# Step 7 - Review GPO ACL

```powershell
Get-GPPermission -Name 'WSUS Policy' -All
```

Identify unexpected principals with modification rights.

---

# Step 8 - Identify Administrators

On the authorised WSUS server:

```powershell
Get-LocalGroup |
    Where-Object {
        $_.Name -match 'WSUS'
    }
```

Then review relevant membership.

---

# Step 9 - Determine SCCM Integration

Check whether WSUS operates as a:

```text
Software Update Point
```

See:

[Microsoft Configuration Manager - SCCM](sccm.md)

---

# Step 10 - Determine Managed Scope

Identify whether WSUS services:

```text
Workstations
Servers
Domain Controllers
Tier 0 Systems
```

This influences impact.

---

# Step 11 - Review Server Security

Assess:

```text
Local Administrators
IIS Configuration
TLS
Firewall
Database
Content Permissions
Backup
Patch Level
Monitoring
```

---

# Step 12 - Report Actual Weaknesses

Examples:

```text
HTTP-Only WSUS Client Communication
Excessive WSUS Administrative Membership
Weak WSUS GPO Permissions
Unnecessary Network Exposure
Insecure Third-Party Update Signing
Unsupported or Poorly Maintained WSUS Architecture
```

---

# Safe Validation

Prefer evidence such as:

```text
Registry Policy
GPO Configuration
IIS Binding
Certificate Information
Group Membership
ACL
Network Connectivity
WSUS Version
```

rather than manipulating updates.

---

# Avoid Update Manipulation

Do not demonstrate a finding by:

```text
Publishing a Fake Update
Approving an Unexpected Update
Declining Security Updates
Redirecting Production Clients
Changing WSUS GPO
Replacing Content
```

unless the engagement explicitly authorises such testing in a controlled environment.

---

# Lab Validation

If active update-manipulation testing is necessary, use:

```text
Dedicated WSUS Lab
Dedicated Client
Test Certificate
Isolated Network
Non-Production GPO
Snapshot / Rollback
```

---

# Detection

Defensive monitoring should cover:

```text
WSUS Administration
IIS
Group Policy
DNS
Database
Server Logons
Update Approvals
Synchronization
Configuration Changes
```

---

# Windows Logons

Monitor relevant authentication events such as:

```text
4624
4625
4648
4672
```

where appropriate.

Unexpected privileged logons to a WSUS server should be investigated.

---

# Process Creation

Where enabled:

```text
4688
```

can provide process-creation visibility.

Unexpected administrative tools or scripting engines on a WSUS server may warrant investigation.

---

# Group Membership Changes

Monitor privileged group changes affecting:

```text
WSUS Administrators
Local Administrators
Server Administration Groups
```

---

# Group Policy Changes

WSUS client configuration is often delivered by GPO.

Security event:

```text
5136
```

may provide visibility into Active Directory object modifications when Directory Service Changes auditing is enabled.

GPO modification should also be monitored through appropriate AD and SYSVOL telemetry.

---

# DNS Changes

Monitor unexpected modification of the WSUS hostname or aliases.

A change to:

```text
wsus01.corp.example
```

could affect large numbers of systems.

---

# IIS Monitoring

Monitor:

```text
Binding Changes
Certificate Changes
Authentication Changes
Application Pool Changes
Unexpected Web Content
```

on the WSUS server.

---

# WSUS Logs

WSUS and IIS provide operational logs useful for investigation.

Relevant sources can include:

```text
IIS Logs
WSUS Logs
Windows Event Logs
Configuration Manager Logs
```

depending on architecture.

---

# Windows Update Client Logs

Modern Windows can generate a readable Windows Update log using:

```powershell
Get-WindowsUpdateLog
```

This reconstructs Windows Update ETL data into a readable log.

Use it for troubleshooting and forensic analysis.

---

# IIS Logs

IIS logs can provide:

```text
Client Address
Request Path
HTTP Status
User Agent
Timestamp
```

Useful patterns include:

```text
Unexpected Administrative Access
Large Request Volume
Unusual Source Networks
Repeated Errors
```

---

# WSUS Synchronization Monitoring

Monitor:

```text
Synchronization Failures
Unexpected Upstream Changes
Unexpected Product Changes
Unexpected Classification Changes
```

---

# Approval Monitoring

Changes to update approvals are particularly security relevant.

Investigate:

```text
Unexpected Approval
Unexpected Decline
Unexpected Target Group
Unexpected Administrator
```

---

# Database Monitoring

Where SQL Server hosts SUSDB, consider monitoring:

```text
Administrative Logons
Database Permission Changes
Unexpected Queries
Backup Access
Configuration Changes
```

---

# WSUS Hardening

A strong WSUS security model includes:

```text
TLS
Least Privilege
Secure Group Policy
Network Segmentation
Protected DNS
Protected IIS
Protected Database
Protected Signing Keys
Monitoring
Regular Maintenance
```

---

# Configure SSL

Microsoft's current WSUS best-practice guidance recommends configuring SSL for WSUS client communication.

Prefer:

```text
https://wsus01.corp.example:8531
```

where supported by the architecture.

---

# Use Trusted Certificates

Use certificates issued by:

```text
Enterprise PKI
```

or another trusted provider.

Ensure:

```text
Correct Hostnames
Valid Trust Chain
Protected Private Key
Appropriate Lifetime
```

---

# Protect WSUS GPO

Restrict modification of the GPO that configures:

```text
WUServer
WUStatusServer
Windows Update Behaviour
```

to authorised administrators.

---

# Protect DNS

Restrict modification of WSUS DNS records.

Review:

```text
Dynamic Update
Record Ownership
ACLs
Stale Records
```

---

# Protect WSUS Administrators

Use:

```text
Dedicated Administrative Accounts
Least Privilege
Strong Authentication
Privileged Workstations
Monitoring
```

according to organisational requirements.

---

# Protect Local Administrators

Review all members of:

```text
Administrators
```

on the WSUS server.

Avoid broad domain groups unless operationally necessary.

---

# Protect IIS

Harden:

```text
TLS
Authentication
Application Pools
Bindings
Certificates
Modules
Logging
```

according to supported WSUS requirements.

---

# Network Segmentation

Allow only necessary systems to communicate with WSUS.

Conceptually:

```text
Managed Clients
      |
      v
Firewall
      |
      v
WSUS
```

Do not expose WSUS administration unnecessarily to:

```text
Guest Networks
Untrusted User Networks
Internet
```

---

# Restrict Administrative Access

Management protocols such as:

```text
RDP
WinRM
SMB
PowerShell Remoting
SQL
```

should be restricted to approved administrative networks and identities.

---

# Protect SUSDB

Whether using:

```text
WID
```

or:

```text
SQL Server
```

restrict database access.

---

# Protect Backups

WSUS and SQL backups should not be readable by ordinary domain users.

See:

[Windows and Active Directory Shares](shares.md)

---

# Protect Third-Party Signing Keys

If the environment publishes trusted third-party updates:

```text
Signing Key
```

becomes highly sensitive.

Protect it using:

```text
Restricted Access
Secure Key Storage
Certificate Lifecycle Management
Monitoring
```

---

# Remove Unnecessary Third-Party Trust

Review whether clients trust certificates or publishers that are no longer required for software deployment.

---

# Maintain WSUS

Perform documented maintenance appropriate to the environment.

This includes reviewing:

```text
Superseded Updates
Obsolete Updates
Database Health
Synchronization
Storage
IIS Health
```

---

# WSUS Deprecation

As of 2026:

```text
WSUS Is Deprecated
```

Microsoft no longer actively develops new WSUS features.

However:

```text
Deprecated
!=
Unsupported
```

Existing WSUS capabilities remain available for supported deployments and continue receiving applicable security and quality updates under the Windows Server lifecycle.

---

# What Deprecation Means for Security

Organisations should not immediately remove WSUS solely because it is deprecated.

Instead:

```text
Inventory Dependencies
      |
      v
Understand Current Architecture
      |
      v
Maintain Supported Deployment
      |
      v
Plan Long-Term Migration
```

---

# Future Planning

Organisations should evaluate modern update-management approaches according to their requirements.

Potential Microsoft technologies include cloud-based update-management capabilities and Configuration Manager depending on the environment.

Migration should consider:

```text
Server Workloads
Client Workloads
Disconnected Networks
Compliance
Bandwidth
Approval Requirements
Operational Control
```

---

# Reporting WSUS Findings

Do not report:

```text
WSUS Is Deprecated
```

as a vulnerability by itself.

Deprecation is an architectural lifecycle consideration.

Likewise, do not report:

```text
Port 8530 Is Open
```

without demonstrating the actual security weakness.

---

# Potential Findings

Examples include:

```text
WSUS Client Communication Uses HTTP Instead of TLS
```

```text
Excessive Membership in WSUS Administrative Groups
```

```text
Low-Privilege Group Can Modify WSUS Client Configuration GPO
```

```text
WSUS Administrative Interfaces Accessible from Untrusted Networks
```

```text
Weak Permissions Protect Third-Party Update Signing Material
```

```text
WSUS Server Has Excessive Local Administrative Membership
```

```text
WSUS Infrastructure Is Not Appropriately Protected Despite Managing Tier 0 Systems
```

---

# Example Finding - HTTP Communication

```text
Finding:
WSUS Client Communication Is Not Protected with TLS

Description:
Domain systems were configured to communicate with the internal WSUS
server using HTTP on TCP port 8530.

Microsoft's current WSUS best-practice guidance recommends configuring
SSL for client communication.

Impact:
An attacker with an appropriate network position may have increased
visibility into or ability to interfere with WSUS-related communication.

The practical impact depends on the affected WSUS endpoints, update
signing, authentication configuration and the attacker's network
position.

Recommendation:
Configure WSUS to use SSL/TLS according to Microsoft's current WSUS
deployment guidance.

Deploy a trusted server certificate containing the names used by
clients and update the relevant Windows Update policy to reference the
HTTPS WSUS endpoint.

Validate the change in a test group before production rollout.
```

---

# Example Finding - Weak GPO Permissions

```text
Finding:
Low-Privilege Group Can Modify WSUS Client Configuration Policy

Description:
A Group Policy Object responsible for configuring the organisation's
WSUS server was modifiable by a group that did not require Group Policy
administration rights.

The policy applies to a large population of domain computers.

Impact:
A compromised member of the affected group could modify Windows Update
configuration delivered to systems within the GPO scope.

The resulting impact depends on the modified settings, client
configuration and other security controls.

Recommendation:
Remove unnecessary GPO modification permissions.

Restrict WSUS policy administration to dedicated authorised
administrators.

Review other Group Policy Objects for equivalent delegated permissions
and monitor future changes to Windows Update policy.
```

---

# Example Finding - Excessive WSUS Administrators

```text
Finding:
Excessive Membership in WSUS Administrative Group

Description:
The WSUS administrative group contained identities that did not require
update-management privileges for their business responsibilities.

Impact:
Compromise of any unnecessarily privileged identity could allow an
attacker to influence WSUS configuration and update approvals.

The impact is increased where WSUS manages servers or Tier 0 systems.

Recommendation:
Review all WSUS administrative identities and remove accounts that do
not require administrative access.

Use dedicated administrative accounts and periodically recertify WSUS
privileges.
```

---

# Example Finding - Network Exposure

```text
Finding:
WSUS Administrative Server Is Accessible from Untrusted User Networks

Description:
The WSUS server exposed administrative Windows services to user
workstation networks that did not require management access.

Client access to the WSUS update service was operationally required,
but administrative services were unnecessarily reachable.

Impact:
A compromised workstation could directly reach additional management
services on the WSUS server, increasing the attack surface of the
update-management infrastructure.

Recommendation:
Separate client update connectivity from administrative access.

Restrict RDP, WinRM, SMB, SQL and other management interfaces to
dedicated administrative networks and authorised systems.
```

---

# Example Finding - Tier 0

```text
Finding:
WSUS Infrastructure Managing Tier 0 Systems Is Insufficiently Protected

Description:
The same WSUS infrastructure provided update management for ordinary
workstations and Active Directory Tier 0 systems.

The WSUS server was administered by identities and from networks that
were not protected to a Tier 0 standard.

Impact:
Compromise of the update-management infrastructure may create an
administrative or operational path affecting security-critical
identity systems.

Recommendation:
Review the organisation's update-management architecture for Tier 0
systems.

Ensure any infrastructure capable of influencing Tier 0 patching is
protected using appropriately privileged identities, administrative
workstations, network segmentation and monitoring.
```

---

# WSUS Assessment Checklist

## Discovery

- [ ] Check local Windows Update policy
- [ ] Identify `WUServer`
- [ ] Identify `WUStatusServer`
- [ ] Identify WSUS hostname
- [ ] Resolve DNS
- [ ] Identify HTTP port
- [ ] Identify HTTPS port
- [ ] Identify upstream server
- [ ] Identify downstream servers
- [ ] Determine SCCM integration

## Group Policy

- [ ] Identify WSUS GPO
- [ ] Review GPO scope
- [ ] Review GPO permissions
- [ ] Review inheritance
- [ ] Review security filtering
- [ ] Review WMI filters
- [ ] Identify who can modify WSUS settings
- [ ] Review SYSVOL permissions

## Network

- [ ] Test approved WSUS connectivity
- [ ] Review TCP 8530
- [ ] Review TCP 8531
- [ ] Identify custom ports
- [ ] Review firewall rules
- [ ] Review administrative service exposure
- [ ] Review segmentation
- [ ] Review proxy configuration

## TLS

- [ ] Determine whether TLS is used
- [ ] Review certificate subject
- [ ] Review SANs
- [ ] Review issuer
- [ ] Review expiration
- [ ] Review trust chain
- [ ] Review protocol support
- [ ] Review IIS bindings

## Server

- [ ] Identify Windows Server version
- [ ] Identify WSUS role
- [ ] Review local administrators
- [ ] Review WSUS administrators
- [ ] Review IIS
- [ ] Review application pools
- [ ] Review server patch level
- [ ] Review management interfaces

## Database

- [ ] Identify WID or SQL
- [ ] Identify SUSDB
- [ ] Review database permissions
- [ ] Review SQL network exposure
- [ ] Review service accounts
- [ ] Review database backups
- [ ] Consider WID deprecation in lifecycle planning

## Content

- [ ] Identify content directory
- [ ] Review NTFS permissions
- [ ] Review unexpected write access
- [ ] Do not modify update content
- [ ] Review third-party publishing
- [ ] Identify signing certificates where applicable
- [ ] Protect signing private keys

## Administration

- [ ] Identify WSUS administrators
- [ ] Identify unnecessary administrators
- [ ] Review delegated administration
- [ ] Review update approval authority
- [ ] Review computer groups
- [ ] Identify Tier 0 groups
- [ ] Review dedicated administrative accounts

## SCCM

- [ ] Determine whether WSUS is a Software Update Point
- [ ] Identify SCCM site
- [ ] Review SUP configuration
- [ ] Avoid direct WSUS changes where SCCM manages WSUS
- [ ] Review HTTP/HTTPS requirements
- [ ] Review SCCM administrative paths

## Tier 0

- [ ] Determine whether WSUS manages domain controllers
- [ ] Determine whether WSUS manages certificate authorities
- [ ] Determine whether WSUS manages ADFS
- [ ] Determine whether WSUS manages privileged workstations
- [ ] Review administrative tiering
- [ ] Review network tiering

## Authentication

- [ ] Review Windows authentication where applicable
- [ ] Identify NTLM use
- [ ] Prefer Kerberos where supported
- [ ] Review relay protections where applicable
- [ ] Review IIS authentication
- [ ] Review administrative authentication

## Detection

- [ ] Monitor privileged WSUS logons
- [ ] Monitor administrator changes
- [ ] Monitor update approvals
- [ ] Monitor declined updates
- [ ] Monitor synchronization changes
- [ ] Monitor GPO changes
- [ ] Monitor DNS changes
- [ ] Monitor IIS configuration
- [ ] Monitor certificate changes
- [ ] Monitor database access
- [ ] Monitor third-party publishing

## Maintenance

- [ ] Review synchronization health
- [ ] Review obsolete updates
- [ ] Review superseded updates
- [ ] Review database health
- [ ] Review content storage
- [ ] Review IIS health
- [ ] Review backups
- [ ] Review WSUS lifecycle strategy

## Hardening

- [ ] Configure TLS according to Microsoft guidance
- [ ] Use trusted certificates
- [ ] Protect WSUS GPO
- [ ] Protect DNS
- [ ] Restrict WSUS administrators
- [ ] Restrict local administrators
- [ ] Segment management interfaces
- [ ] Protect IIS
- [ ] Protect SUSDB
- [ ] Protect backups
- [ ] Protect third-party signing keys
- [ ] Maintain WSUS
- [ ] Plan for long-term WSUS deprecation

## Reporting

- [ ] Do not report WSUS presence alone
- [ ] Do not report deprecation alone as a vulnerability
- [ ] Do not report TCP 8530 alone
- [ ] Identify actual configuration weakness
- [ ] Identify affected clients
- [ ] Identify managed server population
- [ ] Identify Tier 0 exposure
- [ ] Identify attack prerequisites
- [ ] Avoid overstating unsigned-update risk
- [ ] Provide architecture-specific remediation

---

# WSUS Testing Model

The basic model is:

```text
Microsoft Update
      |
      v
WSUS
      |
      v
Windows Client
```

The hierarchical model is:

```text
Microsoft Update
      |
      v
Upstream WSUS
      |
      v
Downstream WSUS
      |
      v
Clients
```

The policy model is:

```text
Active Directory
      |
      v
Group Policy
      |
      v
WUServer
      |
      v
Windows Client
```

The transport model is:

```text
Client
 |
 v
DNS
 |
 v
WSUS
 |
 +--> HTTP
 |
 +--> HTTPS
```

The approval model is:

```text
Administrator
      |
      v
Update Approval
      |
      v
Computer Group
      |
      v
Managed Systems
```

The signing model is:

```text
Microsoft
    |
    v
Signed Update
    |
    v
WSUS
    |
    v
Client Validation
```

The important distinction is:

```text
WSUS Control
    !=
Microsoft Signing Authority
```

The Group Policy attack-path model is:

```text
Principal
   |
   v
GPO Modification
   |
   v
Windows Update Policy
   |
   v
Managed Computers
```

The administrative model is:

```text
WSUS Administrator
        |
        v
WSUS Configuration
        |
        v
Update Management
        |
        v
Managed Estate
```

The SCCM model is:

```text
Configuration Manager
        |
        v
Software Update Point
        |
        v
WSUS
        |
        v
Managed Clients
```

The Tier 0 model is:

```text
WSUS
 |
 v
Domain Controllers
 |
 v
Active Directory
```

The security model is:

```text
TLS
 +
Least Privilege
 +
Secure GPO
 +
Secure DNS
 +
Protected IIS
 +
Protected Database
 +
Network Segmentation
 +
Monitoring
 =
Reduced WSUS Risk
```

For penetration testers:

```text
Do Not Ask:
"Is port 8530 open?"

Ask:
"How is the update trust path protected,
who controls it, and which systems depend
on it?"
```

For defenders:

```text
Do Not Ask:
"Does WSUS deliver updates?"

Ask:
"Can an unauthorised identity influence
the update-management path without being
detected?"
```

The complete model is:

```text
Administrator
      |
      v
Policy / WSUS
      |
      v
Update Decision
      |
      v
Transport
      |
      v
Client
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

Group Policy:

[Group Policy](group-policy.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

SMB:

[SMB](smb.md)

Shares:

[Windows and Active Directory Shares](shares.md)

SCCM:

[Microsoft Configuration Manager - SCCM](sccm.md)

ADIDNS:

[Active Directory Integrated DNS](adidns.md)

AD CS:

[Active Directory Certificate Services](ad-cs/index.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

The next infrastructure page is:

```text
docs/active-directory/mdt.md
```

followed by:

```text
docs/active-directory/scom.md
docs/active-directory/adfs.md
docs/active-directory/rodc.md
```

---

# References

## Microsoft - Windows Server Update Services

[Microsoft - WSUS Overview](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/get-started/windows-server-update-services-wsus){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - WSUS Best Practices

[Microsoft - WSUS Best Practices](https://learn.microsoft.com/en-us/troubleshoot/mem/configmgr/update-management/windows-server-update-services-best-practices){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Deploy WSUS

[Microsoft - Deploy Windows Server Update Services](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/deploy-windows-server-update-services){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Configure WSUS

[Microsoft - Configure WSUS](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/2-configure-wsus){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - WSUS Security

[Microsoft - Secure WSUS with SSL](https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/deploy/2-configure-wsus#configure-ssl-on-the-wsus-server){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - WSUS PowerShell

[Microsoft - UpdateServices PowerShell Module](https://learn.microsoft.com/en-us/powershell/module/updateservices/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-WsusServer

[Microsoft - Get-WsusServer](https://learn.microsoft.com/en-us/powershell/module/updateservices/get-wsusserver){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - WSUS and Configuration Manager Ports

[Microsoft - Ports Used in Configuration Manager](https://learn.microsoft.com/en-us/intune/configmgr/core/plan-design/hierarchy/ports){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows Server Deprecated Features

[Microsoft - Features Removed or No Longer Developed in Windows Server](https://learn.microsoft.com/en-us/windows-server/get-started/removed-deprecated-features-windows-server){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows Update

[Microsoft - Windows Update Documentation](https://learn.microsoft.com/en-us/windows/deployment/update/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-WindowsUpdateLog

[Microsoft - Get-WindowsUpdateLog](https://learn.microsoft.com/en-us/powershell/module/windowsupdate/get-windowsupdatelog){ target="_blank" rel="noopener noreferrer" }

---

# Current WSUS Status

As of September 2026, Microsoft's documentation states that WSUS is deprecated and no longer receives new feature development.

However, existing WSUS capabilities and content remain available for production deployments, and the component continues to receive security and quality updates according to the applicable product lifecycle.

Windows Server 2025 still includes WSUS.

Microsoft has separately deprecated Windows Internal Database, which is used by WSUS and several other Windows Server roles, and states that WID will be removed in a future Windows release.

Organisations operating WSUS should therefore distinguish:

```text
WSUS Deprecation
```

from:

```text
WSUS Removal
```

and:

```text
Windows Internal Database Deprecation
```

These are related lifecycle considerations but are not the same event.

---

# Final Notes

WSUS occupies an important position in Windows enterprise infrastructure because it influences how systems receive security updates.

The fundamental relationship is:

```text
Microsoft Update
      |
      v
WSUS
      |
      v
Managed Systems
```

The important security question is not:

```text
Does WSUS Exist?
```

It is:

```text
Who Controls It?
      |
      v
How Do Clients Trust It?
      |
      v
How Is Communication Protected?
      |
      v
Which Systems Depend on It?
```

A secure deployment should consider:

```text
TLS
Group Policy
DNS
Administrative Access
IIS
Database Security
Network Segmentation
Update Signing
Monitoring
```

The signing model is particularly important:

```text
Control of WSUS
      !=
Ability to Arbitrarily Sign
Microsoft Updates
```

Therefore findings should be based on demonstrated weaknesses rather than assumptions about update execution.

Microsoft's current guidance recommends SSL for WSUS client communication, and default modern WSUS deployments commonly use TCP 8530 for HTTP and TCP 8531 for HTTPS.

As of 2026:

```text
WSUS
 |
 v
Deprecated
 |
 v
Still Supported for Existing Production Deployments
```

Deprecation should therefore drive:

```text
Architecture Review
Migration Planning
Lifecycle Management
```

rather than an unsupported claim that WSUS itself is a vulnerability.

The defensive objective is:

```text
Secure Policy
     |
     v
Secure Transport
     |
     v
Protected Administration
     |
     v
Protected Update Infrastructure
     |
     v
Trusted Client Configuration
     |
     v
Monitored Update Management
```

The next infrastructure page covers Microsoft Deployment Toolkit:

```text
MDT
```
