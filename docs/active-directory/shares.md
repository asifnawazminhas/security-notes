# Windows and Active Directory Shares

Windows file shares are one of the most important sources of information during an Active Directory security assessment.

Organisations commonly use SMB shares to store:

```text
Documents
Scripts
Software
Configuration Files
Deployment Packages
Backups
Administrative Tools
User Profiles
Department Data
Application Files
```

From a security perspective, shares frequently reveal information that connects otherwise separate Active Directory attack paths.

A share may expose:

```text
Credentials
Configuration Secrets
Deployment Scripts
Private Keys
Certificates
Connection Strings
Passwords
API Keys
Administrative Scripts
Sensitive Documents
```

The assessment model is:

```text
Active Directory Identity
        |
        v
SMB
        |
        v
Share
        |
        v
Files and Directories
        |
        v
Permissions / Secrets / Information
        |
        v
Potential Security Impact
```

!!! warning "Authorised testing only"
    File-share enumeration can expose confidential business information and credentials. Access only systems and shares within scope. Prefer metadata and targeted searches over bulk downloading. Do not modify, delete or upload files unless explicitly authorised.

---

# Shares at a Glance

A Windows file share exposes a directory through SMB.

Example:

```text
Server:

FILE01
```

Local directory:

```text
D:\Departments\Finance
```

Share:

```text
Finance
```

UNC path:

```text
\\FILE01\Finance
```

Users access:

```text
SMB
 |
 v
FILE01
 |
 v
Finance Share
 |
 v
NTFS Directory
```

---

# SMB

Modern Windows file sharing primarily uses:

```text
SMB
```

Common port:

```text
TCP 445
```

Older environments may also expose NetBIOS-related services such as:

```text
TCP 139
UDP 137
UDP 138
```

See:

[SMB](smb.md)

---

# Share Permissions vs NTFS Permissions

Windows file access commonly involves two permission layers:

```text
Share Permissions
       +
NTFS Permissions
       |
       v
Effective Access
```

These should not be treated as the same control.

---

# Share Permissions

Share permissions apply when accessing a directory through SMB.

Common permissions include:

```text
Read
Change
Full Control
```

---

# NTFS Permissions

NTFS permissions apply to the underlying file-system objects.

Common rights include:

```text
Read
Read and Execute
Write
Modify
Full Control
```

---

# Effective Permissions

When a resource is accessed through a share, both permission sets matter.

Conceptually:

```text
User
 |
 v
Share ACL
 |
 v
NTFS ACL
 |
 v
Effective Permission
```

A permissive share ACL does not automatically mean that every user can modify the underlying files.

---

# Common Administrative Shares

Windows commonly creates administrative shares such as:

```text
C$
ADMIN$
IPC$
```

Additional drives may appear as:

```text
D$
E$
```

These normally require administrative privileges.

---

# C$

```text
\\HOST\C$
```

maps to the system drive.

Example:

```text
C:\
```

---

# ADMIN$

```text
\\HOST\ADMIN$
```

normally maps to the Windows directory.

Typically:

```text
C:\Windows
```

---

# IPC$

```text
\\HOST\IPC$
```

is used for inter-process communication and SMB-related operations.

It is not a conventional file-storage share.

---

# Domain Controller Shares

Domain controllers normally expose important shares including:

```text
SYSVOL
NETLOGON
```

These are expected and necessary for Active Directory.

---

# SYSVOL

SYSVOL contains domain-wide data used by:

```text
Group Policy
Logon Scripts
Startup Scripts
Administrative Templates
Policy Distribution
```

Typical path:

```text
\\corp.example\SYSVOL
```

or:

```text
\\DC01\SYSVOL
```

---

# NETLOGON

NETLOGON commonly exposes logon-related scripts and files.

Typical path:

```text
\\corp.example\NETLOGON
```

---

# SYSVOL Security Relevance

SYSVOL is intentionally readable by domain users in normal Active Directory environments.

The security question is therefore not:

```text
Can Domain Users Read SYSVOL?
```

That is generally expected.

Instead ask:

```text
What Sensitive Information Is Stored There?
```

---

# Common SYSVOL Findings

Potentially interesting content includes:

```text
PowerShell Scripts
Batch Files
VBScript
Configuration Files
Legacy GPP Files
Deployment Scripts
Mapped Drive Scripts
Printer Scripts
Application Installers
Hard-Coded Credentials
Service Account Names
Internal URLs
```

---

# Group Policy Preferences

Historically, Group Policy Preferences could contain passwords encrypted using a publicly documented key.

The relevant value is commonly:

```text
cpassword
```

Potential file names include:

```text
Groups.xml
Services.xml
Scheduledtasks.xml
DataSources.xml
Printers.xml
Drives.xml
```

Modern Windows versions no longer allow administrators to create new GPP password configurations through the normal Group Policy interface, but legacy files may still remain.

If your dedicated page exists, see:

```text
docs/active-directory/gpp-passwords.md
```

---

# Search SYSVOL for cpassword

Windows:

```powershell
Get-ChildItem '\\corp.example\SYSVOL' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'cpassword'
```

This is a read-only search.

---

# Search for Password Keywords

A targeted search can identify suspicious configuration content.

```powershell
Get-ChildItem '\\corp.example\SYSVOL' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','passwd','pwd','secret','credential'
```

Expect false positives.

Do not report keyword matches without examining context.

---

# Enumerating Shares from Windows

Native Windows provides several methods for share enumeration.

---

# net view

Enumerate shares on a server:

```cmd
net view \\FILE01
```

---

# PowerShell Get-SmbShare

When executed locally with appropriate permissions:

```powershell
Get-SmbShare
```

This displays locally configured SMB shares.

---

# Get-SmbShareAccess

Inspect share-level permissions:

```powershell
Get-SmbShareAccess -Name 'Finance'
```

---

# UNC Access

Test an approved share:

```powershell
Get-ChildItem '\\FILE01\Finance'
```

---

# Directory Listing

```cmd
dir \\FILE01\Finance
```

---

# Recursive PowerShell Enumeration

For a small approved directory:

```powershell
Get-ChildItem '\\FILE01\Finance' -Recurse -File -ErrorAction SilentlyContinue
```

Avoid recursive enumeration across very large production shares without considering performance and data volume.

---

# Search by Extension

Example:

```powershell
Get-ChildItem '\\FILE01\Finance' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in '.xml','.ini','.config','.ps1','.bat','.cmd','.vbs' }
```

---

# Search Interesting File Names

```powershell
Get-ChildItem '\\FILE01\Finance' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'password|credential|secret|backup|config|connection'
    }
```

---

# Search File Contents

For approved text-based files:

```powershell
Get-ChildItem '\\FILE01\Finance' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','passwd','secret','apikey','connectionstring' -ErrorAction SilentlyContinue
```

Use targeted extensions or directories where possible to reduce unnecessary access to business data.

---

# Enumerating Shares from Linux

Common tools include:

```text
smbclient
NetExec
Impacket
rpcclient
```

---

# smbclient

List shares:

```bash
smbclient -L //10.20.30.40 -U 'CORP/audituser'
```

---

# Hostname

Prefer hostnames when Kerberos or domain context matters:

```bash
smbclient -L //files01.corp.example -U 'CORP/audituser'
```

---

# Connect to Share

```bash
smbclient //files01.corp.example/Finance -U 'CORP/audituser'
```

Inside the interactive client:

```text
ls
```

---

# Browse Directory

```text
cd Reports
ls
```

---

# Download a Specific Approved File

Inside `smbclient`:

```text
get example.txt
```

Do not bulk-download a share simply because access is available.

---

# Kerberos with smbclient

Where Kerberos is configured, current `smbclient` versions provide Kerberos-related authentication options.

Because syntax can vary between Samba releases, verify the installed version:

```bash
smbclient --help
```

and use the supported Kerberos option for that version.

---

# NetExec Share Enumeration

NetExec is particularly useful for evaluating SMB access across authorised systems.

See:

[NetExec](netexec.md)

Check the installed syntax:

```bash
nxc smb --help
```

---

# Enumerate Shares with NetExec

```bash
nxc smb files01.corp.example -u audituser -p 'PASSWORD' --shares
```

This can show:

```text
Share
Permissions
Description
```

depending on the server and permissions.

---

# Multiple Hosts

Against an explicitly authorised subnet:

```bash
nxc smb 10.20.30.0/24 -u audituser -p 'PASSWORD' --shares
```

Large-scale enumeration can generate substantial authentication and network telemetry.

Use scope-specific target lists where possible.

---

# Domain Credentials

```bash
nxc smb files01.corp.example -d corp.example -u audituser -p 'PASSWORD' --shares
```

---

# Avoid Passwords in Shell History

Where possible, avoid placing production credentials directly in command-line arguments.

Prefer:

```text
Dedicated Assessment Accounts
Environment-Specific Secure Credential Handling
Kerberos Tickets
Tool-Supported Prompts
```

according to the engagement environment.

---

# Null Session Testing

Some legacy or misconfigured SMB servers may expose information without authenticated credentials.

Example:

```bash
smbclient -L //files01.corp.example -N
```

Modern Windows environments normally restrict meaningful anonymous access.

---

# Guest Access

Anonymous and guest access are different concepts.

Possible states include:

```text
Anonymous
Guest
Authenticated User
Domain User
Administrative User
```

Record which security context actually provided access.

---

# rpcclient

`rpcclient` can query certain SMB/RPC information.

Check options:

```bash
rpcclient --help
```

Anonymous connection attempt:

```bash
rpcclient -U '' -N files01.corp.example
```

Whether useful information is exposed depends on server configuration.

---

# Share Enumeration Through Active Directory

Active Directory itself may reveal systems likely to host shares.

Potential sources include:

```text
Computer Objects
DFS Configuration
Group Policy
Logon Scripts
User Home Directories
Profile Paths
Application Configuration
```

---

# User Home Directory Attributes

Active Directory user objects may contain:

```text
homeDirectory
homeDrive
profilePath
scriptPath
```

PowerShell:

```powershell
Get-ADUser -Filter * -Properties homeDirectory,homeDrive,profilePath,scriptPath |
    Select-Object SamAccountName,homeDirectory,homeDrive,profilePath,scriptPath
```

These values can reveal important file servers.

---

# Example

```text
User:
alice

homeDirectory:
\\FILE01\Users\alice

profilePath:
\\FILE02\Profiles\alice
```

This identifies:

```text
FILE01
FILE02
```

as potential infrastructure of interest.

---

# Group Policy Drive Maps

Group Policy can map network shares to users.

Example:

```text
Finance Users
      |
      v
GPO
      |
      v
\\FILE01\Finance
```

This provides useful information about:

```text
Share Purpose
Target Users
File Servers
Department Boundaries
```

See:

[Group Policy](group-policy.md)

---

# Logon Scripts

Logon scripts frequently contain:

```cmd
net use
```

commands.

Example:

```cmd
net use F: \\FILE01\Finance
```

or PowerShell equivalents.

Searching SYSVOL can reveal these mappings.

---

# Distributed File System

Organisations may use:

```text
Distributed File System
```

or:

```text
DFS
```

to provide a unified namespace.

Example:

```text
\\corp.example\Shares
```

may redirect users to several backend servers.

---

# DFS Model

```text
User
 |
 v
DFS Namespace
 |
 +--> FILE01
 +--> FILE02
 +--> FILE03
```

---

# Why DFS Matters

A single visible path may hide:

```text
Multiple File Servers
Replication
Alternative Targets
Different Network Segments
```

Enumerating the namespace can therefore reveal additional infrastructure.

---

# Share Discovery Through SYSVOL

Search scripts for UNC paths.

PowerShell:

```powershell
Get-ChildItem '\\corp.example\SYSVOL' -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern '\\\\[A-Za-z0-9._-]+\\[A-Za-z0-9$._-]+'
```

Review results manually.

---

# Share Discovery Through Local Configuration

Mapped drives:

```cmd
net use
```

PowerShell:

```powershell
Get-SmbMapping
```

These can reveal resources already used by the current user.

---

# PowerShell Drives

```powershell
Get-PSDrive -PSProvider FileSystem
```

Mapped network drives may appear alongside local drives.

---

# File Share Access Model

For each discovered share:

```text
Share
 |
 v
Can List?
 |
 v
Can Read?
 |
 v
Can Write?
 |
 v
Can Modify Existing Files?
 |
 v
Can Delete?
```

Do not treat all accessible shares as equivalent.

---

# Read Access

Read access can expose:

```text
Confidential Information
Credentials
Configuration
Internal Architecture
Source Code
Backups
```

---

# Write Access

Write access may create additional risk if other users or systems consume content from the share.

The important question is:

```text
What Uses This Directory?
```

---

# Writable Share Risk Model

```text
User Can Write
      |
      v
Shared Directory
      |
      v
Another User / Service Reads File
      |
      v
Security-Relevant Behaviour
```

Write permission alone does not prove code execution.

---

# Write vs Modify

A user may be able to:

```text
Create New Files
```

without being able to:

```text
Modify Existing Files
```

or:

```text
Delete Files
```

Always identify the actual effective permission.

---

# Safe Write Test

If write testing is authorised, use a uniquely named temporary text file.

PowerShell:

```powershell
$path = '\\FILE01\TestShare\pentest-write-test.txt'
'Authorised write validation' | Set-Content -Path $path
Test-Path $path
Remove-Item $path
```

Use only an explicitly approved test location.

---

# Verify Cleanup

```powershell
Test-Path '\\FILE01\TestShare\pentest-write-test.txt'
```

Expected:

```text
False
```

---

# Linux Write Validation

Within an approved `smbclient` session, a harmless uniquely named local text file can be uploaded and immediately removed.

Do not perform write validation in:

```text
Software Deployment
Logon Scripts
Startup Scripts
Application Executable Directories
Backup Locations
```

unless the specific impact test is explicitly authorised.

---

# Sensitive File Types

During targeted review, pay attention to files such as:

```text
*.ps1
*.bat
*.cmd
*.vbs
*.xml
*.config
*.ini
*.conf
*.yml
*.yaml
*.json
*.kdbx
*.rdp
*.ppk
*.pem
*.key
*.pfx
*.p12
*.cer
*.crt
*.sql
*.bak
*.zip
*.7z
```

A file extension alone does not make the file sensitive.

---

# Configuration Files

Potentially useful configuration files include:

```text
web.config
appsettings.json
connectionStrings.config
database.ini
settings.xml
config.yml
```

Search carefully and avoid bulk collection.

---

# Connection Strings

Applications may store:

```text
Database Server
Database Name
Username
Password
Integrated Security Settings
```

inside configuration files.

Example conceptual structure:

```text
Server=SQL01
Database=AppDB
User ID=appsvc
Password=<secret>
```

If discovered, protect the evidence and avoid testing the credential outside scope.

---

# PowerShell Scripts

Administrative scripts may contain:

```text
Credentials
Service Accounts
Server Lists
Remote Commands
Backup Paths
API Tokens
```

Search:

```powershell
Get-ChildItem '\\FILE01\Scripts' -Recurse -Filter '*.ps1' -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','credential','secret','token','key'
```

---

# Batch Files

```powershell
Get-ChildItem '\\FILE01\Scripts' -Recurse -Include '*.bat','*.cmd' -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','pass=','pwd=','net use','runas'
```

---

# XML Files

```powershell
Get-ChildItem '\\FILE01\Config' -Recurse -Filter '*.xml' -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','cpassword','credential','connectionString'
```

---

# INI Files

```powershell
Get-ChildItem '\\FILE01\Config' -Recurse -Filter '*.ini' -File -ErrorAction SilentlyContinue |
    Select-String -Pattern 'password','passwd','pwd','secret'
```

---

# Backup Files

Backups may expose older copies of:

```text
Configuration
Credentials
Databases
Scripts
Certificates
Keys
```

Potential names include:

```text
backup
old
archive
copy
previous
.bak
```

---

# Password Databases

Files such as:

```text
*.kdbx
```

may contain password vaults.

Their existence is not automatically a vulnerability.

Assess:

```text
Who Can Read It?
Why?
How Is It Protected?
Is It Intended to Be Shared?
```

---

# Private Keys

Files such as:

```text
*.pem
*.key
*.ppk
```

may contain private cryptographic material.

If a private key is discovered:

```text
Do Not Immediately Use It
```

First determine:

```text
Owner
Purpose
Scope
Protection
Associated System
```

---

# PFX and P12 Files

Files such as:

```text
*.pfx
*.p12
```

can contain:

```text
Certificate
Private Key
Certificate Chain
```

They may be password protected.

Treat them as sensitive credential material.

---

# RDP Files

`.rdp` files may reveal:

```text
Hostnames
Gateways
Usernames
Connection Settings
```

They do not normally contain a reusable plaintext password.

---

# Deployment Shares

Software deployment shares deserve particular attention.

Examples:

```text
\\DEPLOY01\Software
\\SCCM01\Packages
\\MDT01\DeploymentShare$
```

These may contain:

```text
Installers
Scripts
Configuration
Task Sequences
Drivers
Credentials
```

---

# Deployment Share Risk

The security model is:

```text
Writable Deployment Share
          |
          v
Package / Script
          |
          v
Automated Deployment
          |
          v
Many Systems
```

This can produce substantial impact if inappropriate write permissions exist.

Do not modify deployment content during normal testing.

---

# SCCM

Microsoft Configuration Manager environments may expose:

```text
Packages
Applications
Content Libraries
Scripts
Task Sequences
```

through network infrastructure.

See the planned page:

```text
docs/active-directory/sccm.md
```

---

# MDT

Microsoft Deployment Toolkit commonly uses deployment shares.

A typical share might resemble:

```text
\\MDT01\DeploymentShare$
```

See:

```text
docs/active-directory/mdt.md
```

---

# WSUS

Windows Server Update Services can also introduce infrastructure and content-management relationships relevant to Active Directory assessments.

See:

```text
docs/active-directory/wsus.md
```

---

# Backup Shares

Backup shares can be particularly sensitive.

Potential content:

```text
System Backups
Database Backups
VM Images
Configuration Exports
Directory Backups
Private Keys
```

---

# Active Directory Backups

Backups containing:

```text
NTDS.dit
SYSTEM Registry Hive
Domain Controller Images
```

should be treated as Tier 0 material.

See:

[NTDS](ntds.md)

---

# Database Backups

Files such as:

```text
*.bak
*.sql
*.dump
```

may expose application data and credentials.

Do not restore or process production databases unless authorised.

---

# User Home Shares

User home directories may expose:

```text
Documents
Scripts
SSH Keys
RDP Files
Configuration
Browser Exports
Developer Files
```

Privacy and proportionality are especially important.

Do not indiscriminately search user documents.

---

# Department Shares

Examples:

```text
Finance
HR
Legal
Engineering
IT
Security
```

These can contain highly sensitive business information.

A penetration test should minimise access to unrelated content.

---

# Data Minimisation

A good assessment follows:

```text
Find Permission
      |
      v
Identify Relevant File
      |
      v
Collect Minimum Evidence
      |
      v
Stop
```

rather than:

```text
Download Everything
```

---

# File Metadata

Often sufficient evidence can be collected using:

```text
File Name
Path
Owner
Size
Modification Date
ACL
```

without opening the file.

---

# PowerShell Metadata

```powershell
Get-Item '\\FILE01\Finance\sensitive-config.xml' |
    Select-Object FullName,Length,CreationTime,LastWriteTime
```

---

# NTFS ACL

```powershell
Get-Acl '\\FILE01\Finance\sensitive-config.xml' |
    Format-List Owner,AccessToString
```

---

# Directory ACL

```powershell
Get-Acl '\\FILE01\Finance' |
    Format-List Owner,AccessToString
```

---

# icacls

Native Windows:

```cmd
icacls "\\FILE01\Finance"
```

This can provide a compact view of NTFS permissions.

---

# Permission Inheritance

NTFS permissions may be inherited.

Conceptually:

```text
Parent Directory
      |
      v
Inherited ACE
      |
      v
Child Directory
      |
      v
File
```

Identify whether an excessive permission originates from:

```text
Direct ACE
```

or:

```text
Inherited ACE
```

---

# Group-Based Permissions

A user may gain access through nested groups.

Example:

```text
Alice
 |
 v
Finance Users
 |
 v
All Employees
 |
 v
Share ACL
```

See:

[Groups](groups.md)

---

# Domain Local Groups

File-server permissions are commonly assigned through Domain Local groups.

Example:

```text
User
 |
 v
Global Group
 |
 v
Domain Local Group
 |
 v
Resource ACL
```

This is a normal Active Directory design pattern.

---

# AGDLP

A common permissions model is:

```text
Accounts
   |
   v
Global Groups
   |
   v
Domain Local Groups
   |
   v
Permissions
```

Often abbreviated:

```text
AGDLP
```

---

# AGUDLP

Multi-domain environments may use:

```text
Accounts
   |
   v
Global Groups
   |
   v
Universal Groups
   |
   v
Domain Local Groups
   |
   v
Permissions
```

Often abbreviated:

```text
AGUDLP
```

---

# Why Group Resolution Matters

A share may appear restricted to:

```text
FS-Finance-RW
```

but that group may contain:

```text
Finance
Helpdesk
Legacy Migration Group
Foreign Security Principal
```

The full membership chain determines exposure.

---

# Foreign Principals

Trusted-domain users can potentially receive share access through:

```text
Domain Local Groups
Foreign Security Principals
Direct ACL Entries
```

See:

[Trust Relationships](trust-relationships.md)

---

# SID History

Legacy share permissions are a common reason organisations retain:

```text
sIDHistory
```

See:

[SID History](sid-history.md)

A migrated user may continue accessing a share because the ACL references the old SID.

---

# Share Permissions and Lateral Movement

Writable or administratively accessible shares can contribute to lateral movement.

See:

[Lateral Movement](lateral-movement.md)

However:

```text
Share Access
!=
Remote Code Execution
```

Additional conditions are required.

---

# Administrative Shares and Remote Execution

Some Windows remote-management techniques use administrative shares as part of their workflow.

For example:

```text
Administrative Access
      |
      v
ADMIN$ / C$
      |
      v
Remote Service Mechanism
```

The security weakness is usually:

```text
Excessive Administrative Privilege
```

rather than the existence of `ADMIN$`.

---

# Impacket and SMB Shares

Impacket includes SMB-related tooling.

See:

[Impacket](impacket.md)

When testing remote administration, distinguish:

```text
Share Enumeration
```

from:

```text
Remote Execution
```

and use the least intrusive method needed.

---

# Share Access with Kerberos

SMB supports Kerberos authentication when:

```text
DNS
SPN
Realm
Ticket
```

are correctly configured.

Prefer hostnames over raw IP addresses when intentionally validating Kerberos.

---

# Share Access Across Trusts

A trusted-domain identity may access a share when:

```text
Trust Allows Authentication
        |
        v
User Authenticates
        |
        v
Group / ACL Authorises Access
```

The trust itself does not automatically grant access.

---

# Share Access and SID Filtering

For cross-domain access, SID filtering and SID History can influence the SIDs accepted across the trust.

See:

[SID History](sid-history.md)

and:

[Trust Tickets](trust-tickets.md)

---

# SMB Signing

SMB signing protects SMB message integrity and is particularly important when considering NTLM relay.

See:

[NTLM Relay](ntlm-relay.md)

Share enumeration and SMB-signing assessment should be considered together when evaluating SMB security.

---

# SMB Encryption

Modern SMB supports encryption.

This can protect SMB traffic from network interception.

Whether it is required depends on:

```text
Server Configuration
Share Configuration
Data Sensitivity
Windows Version
Operational Requirements
```

---

# Share Discovery Workflow

A structured assessment can follow:

```text
Active Directory
      |
      v
Identify File Servers
      |
      v
Enumerate Shares
      |
      v
Determine Access
      |
      v
Review Permissions
      |
      v
Identify Interesting Paths
      |
      v
Targeted Content Review
      |
      v
Validate Security Impact
      |
      v
Report
```

---

# Step 1 - Identify File Servers

Sources can include:

```text
Active Directory Computer Objects
User Home Directories
Group Policy
Logon Scripts
DFS
DNS
Existing Drive Mappings
BloodHound
```

---

# Step 2 - Enumerate Shares

Windows:

```cmd
net view \\FILE01
```

Linux:

```bash
smbclient -L //files01.corp.example -U 'CORP/audituser'
```

NetExec:

```bash
nxc smb files01.corp.example -d corp.example -u audituser -p 'PASSWORD' --shares
```

---

# Step 3 - Determine Access

Record whether the current identity has:

```text
No Access
List
Read
Write
Modify
Full Control
```

Do not infer permission solely from a tool's abbreviated output if direct validation is required.

---

# Step 4 - Review ACLs

Where accessible:

```powershell
Get-Acl '\\FILE01\Finance'
```

and:

```powershell
Get-SmbShareAccess -Name 'Finance'
```

if querying locally with appropriate permissions.

---

# Step 5 - Identify Interesting Files

Prefer metadata first.

Example:

```powershell
Get-ChildItem '\\FILE01\Finance' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in '.ps1','.bat','.cmd','.xml','.ini','.config','.json','.yml','.yaml','.kdbx','.pfx','.p12','.pem','.key','.bak'
    } |
    Select-Object FullName,Length,LastWriteTime
```

---

# Step 6 - Search Targeted Content

Only after identifying relevant files:

```powershell
Select-String -Path '\\FILE01\Scripts\deploy.ps1' -Pattern 'password','credential','secret','token'
```

---

# Step 7 - Validate Impact

For a discovered credential:

```text
Credential Found
      |
      v
Identify Owner
      |
      v
Identify Intended Use
      |
      v
Confirm Scope
      |
      v
Minimal Authentication Validation
```

Do not automatically test credentials against every reachable service.

---

# Step 8 - Preserve Evidence

Record:

```text
Share
Path
File
Permission
Relevant Content
Identity Used
Timestamp
```

Redact sensitive values where possible.

---

# Step 9 - Cleanup

If a write test was performed:

```text
Verify Test File Removed
```

If no modification was required:

```text
No Cleanup Necessary
```

---

# Searching Large Shares

Large recursive searches can create:

```text
Network Load
File Server Load
EDR Telemetry
Large Result Sets
Privacy Exposure
```

Use targeted filtering.

---

# Better Search Strategy

Instead of:

```text
Search Every File
```

prefer:

```text
Identify Interesting Directory
        |
        v
Filter Extensions
        |
        v
Filter Names
        |
        v
Inspect Metadata
        |
        v
Read Relevant Files
```

---

# File Age

Old files can be highly relevant.

Examples:

```text
Old Deployment Script
Old Backup
Old Password File
Old Configuration
```

But age alone does not prove that the content is still usable.

---

# Credential Validation

If a credential is found:

```text
Found Credential
      |
      v
Is It In Scope?
      |
      v
Is Validation Permitted?
      |
      v
Identify Intended Service
      |
      v
Minimal Test
```

Avoid password spraying with discovered credentials unless explicitly part of the assessment.

---

# Secret Handling

Never place discovered production secrets into:

```text
Public Notes
Screenshots Without Redaction
Git Repositories
Chat Logs
Unencrypted Reports
```

Use redaction.

Example:

```text
Password:
P***********3
```

---

# Evidence Screenshot

A screenshot should show enough context to establish:

```text
Share
Path
Permission
Relevant Finding
```

while hiding unnecessary confidential information.

---

# Writable Share Validation

A safe proof is:

```text
Test Identity
     |
     v
Approved Directory
     |
     v
Create Harmless Text File
     |
     v
Verify
     |
     v
Delete
     |
     v
Verify Cleanup
```

---

# Avoid Executable Uploads

If the finding is simply:

```text
User Can Write to Share
```

there is normally no need to upload:

```text
EXE
DLL
Script Payload
Macro Document
```

A text file proves write access.

---

# Deployment Directory Validation

For a sensitive deployment directory:

```text
Write Permission
```

may already be enough evidence.

Do not replace or modify deployment packages to demonstrate theoretical execution.

---

# Share Detection

Defenders should monitor:

```text
Share Enumeration
Sensitive File Access
Unusual Recursive Reads
Administrative Share Access
File Creation
File Modification
File Deletion
Permission Changes
```

---

# Event 5140

Windows Security event:

```text
5140
```

records:

```text
A network share object was accessed
```

when the relevant auditing is enabled.

---

# Event 5145

Event:

```text
5145
```

provides more detailed share access information and can include:

```text
Share
Relative Target Name
Access Requested
Source Address
Account
```

when Detailed File Share auditing is enabled.

---

# Event 5142

Event:

```text
5142
```

indicates:

```text
A network share object was added
```

---

# Event 5143

Event:

```text
5143
```

indicates:

```text
A network share object was modified
```

---

# Event 5144

Event:

```text
5144
```

indicates:

```text
A network share object was deleted
```

---

# Event 4663

Event:

```text
4663
```

can record access attempts against file-system objects when:

```text
Object Access Auditing
```

and appropriate SACLs are configured.

---

# Authentication Events

Correlate SMB activity with:

```text
4624
4625
```

and other relevant authentication telemetry.

---

# SMB Network Telemetry

Monitor:

```text
TCP 445 Connections
Source Host
Destination Host
Connection Volume
Authentication Identity
```

A workstation suddenly enumerating many file servers can be worth investigating.

---

# Administrative Share Monitoring

High-value patterns include unusual access to:

```text
C$
ADMIN$
```

especially from:

```text
User Workstations
Unexpected Servers
Non-Administrative Accounts
```

---

# Recursive Enumeration Detection

Potential indicators include:

```text
One Account
    |
    v
Many Shares
    |
    v
Many Directories
    |
    v
Large Number of Reads
```

This can indicate:

```text
Inventory
Backup
Indexing
Security Scanning
Adversary Discovery
```

Context is required.

---

# Sensitive File Monitoring

Consider monitoring access to locations containing:

```text
Deployment Scripts
Configuration Secrets
Private Keys
Backups
Password Vaults
Tier 0 Documentation
```

---

# Share Hardening

A strong file-share security model includes:

```text
Least Privilege
Group-Based Access
NTFS ACL Review
Share ACL Review
SMB Signing
SMB Encryption Where Required
Legacy Protocol Removal
Sensitive Data Protection
Monitoring
Lifecycle Management
```

---

# Remove SMBv1

SMBv1 is obsolete and should generally be disabled unless an unavoidable legacy dependency exists.

Modern environments should use supported SMB versions.

---

# Require SMB Signing Where Appropriate

SMB signing can reduce exposure to certain relay and tampering scenarios.

See:

[NTLM Relay](ntlm-relay.md)

---

# SMB Encryption

Consider SMB encryption for:

```text
Sensitive Data
Untrusted Network Segments
Administrative Traffic
```

where operationally appropriate.

---

# Restrict Anonymous Access

Avoid unnecessary:

```text
Anonymous Share Enumeration
Anonymous File Access
Guest Access
```

---

# Use Security Groups

Prefer assigning permissions to:

```text
Security Groups
```

rather than individual users.

Example:

```text
Finance Users
      |
      v
FS-Finance-Read
      |
      v
Finance Share
```

---

# Separate Read and Write Groups

Example:

```text
FS-Finance-RO
FS-Finance-RW
```

This makes access easier to understand and audit.

---

# Avoid Everyone Full Control

A common design may use broad share permissions combined with restrictive NTFS permissions.

This is not automatically vulnerable.

However, effective permissions should still be reviewed carefully.

---

# Review Authenticated Users

Broad groups such as:

```text
Authenticated Users
Domain Users
Everyone
```

should not receive unnecessary access to sensitive directories.

---

# Protect Deployment Shares

Deployment shares should use particularly restrictive write permissions.

A good model is:

```text
Deployment Administrators
          |
          v
Write

Deployment Systems
          |
          v
Read

Ordinary Users
          |
          X
```

depending on operational requirements.

---

# Protect Backup Shares

Backup data should be isolated from ordinary users and ideally from standard administrative compromise paths.

Consider:

```text
Separate Credentials
Restricted Network Access
Encryption
Immutable Copies
Offline Copies
Monitoring
```

---

# Protect Credential Files

Avoid storing:

```text
Plaintext Passwords
Reusable Tokens
Private Keys
Unprotected PFX Files
```

on broadly accessible shares.

---

# Use Managed Identities

Where possible, replace embedded service passwords with technologies such as:

```text
gMSA
Managed Identity
Integrated Authentication
Secret Management Platforms
```

See:

[gMSA](gmsa.md)

---

# Share Lifecycle Management

When:

```text
Project Ends
Department Changes
Server Migrates
Application Retires
```

review:

```text
Share
ACLs
Groups
Data
DNS
Backups
```

---

# Stale Shares

Old shares can expose:

```text
Historical Data
Legacy Credentials
Old Scripts
Forgotten Backups
```

even when the associated application is no longer active.

---

# Hidden Shares

A share ending with:

```text
$
```

is hidden from some casual browsing.

Example:

```text
DeploymentShare$
```

This is not an access-control mechanism.

If a user knows the name and has permission, the share can still be accessed.

---

# Hidden Does Not Mean Secure

```text
Hidden Share
    !=
Protected Share
```

Security must come from:

```text
Authentication
Authorisation
ACLs
Network Controls
```

---

# Reporting Share Findings

Do not report:

```text
SYSVOL Is Readable
```

as a vulnerability by itself.

Do not report:

```text
ADMIN$ Exists
```

as a vulnerability by itself.

Do not report:

```text
Share Exists
```

as a vulnerability.

Report the actual security condition.

---

# Potential Findings

Examples include:

```text
Sensitive File Share Accessible to All Domain Users
```

```text
Plaintext Service Credentials Stored on Shared Drive
```

```text
Deployment Share Writable by Low-Privilege Users
```

```text
Legacy Backup Share Exposes Active Credentials
```

```text
Anonymous SMB Share Exposes Internal Information
```

```text
Excessive NTFS Permissions Permit Unauthorised Modification
```

```text
Legacy GPP Credential File Remains in SYSVOL
```

---

# Example Finding - Sensitive Share

```text
Finding:
Sensitive Department Share Accessible to Unauthorised Domain Users

Description:
A low-privilege domain account was able to read files from a network
share intended for a restricted business department.

The accessible content included documents containing information not
required for the assessment account's business role.

Impact:
Any domain identity with equivalent access may obtain confidential
business information from the affected share.

If a low-privilege account is compromised, the share may therefore
increase the amount of sensitive data exposed to the attacker.

Recommendation:
Review the share and NTFS permissions associated with the affected
directory.

Grant access through dedicated role-based security groups and remove
broad groups that do not require access.

Periodically review group membership and effective permissions.
```

---

# Example Finding - Plaintext Credential

```text
Finding:
Reusable Service Credential Stored in Plaintext on Network Share

Description:
A configuration script stored on an accessible network share contained
a plaintext username and password for a service account.

The file was readable by users who did not require access to the
credential.

Impact:
An attacker who compromises any account with access to the share may
recover the service credential.

The resulting impact depends on the privileges and systems accessible
to the affected service account.

Recommendation:
Immediately rotate the exposed credential after confirming dependent
services.

Remove plaintext credentials from scripts and configuration files.

Use a managed service account, integrated authentication or an
approved secret-management platform where technically appropriate.

Restrict access to the configuration files to identities that require
them.
```

---

# Example Finding - Writable Deployment Share

```text
Finding:
Low-Privilege Users Can Modify Software Deployment Share

Description:
A low-privilege domain identity had write permission to a directory
used to store software deployment content.

No production package was modified during testing.

Impact:
If systems or administrators consume files from the affected directory,
an attacker may potentially influence the deployment process.

The exact impact depends on which files are trusted and how deployment
integrity is validated.

Recommendation:
Restrict modification of deployment content to dedicated deployment
administrators and service identities.

Separate read and write permissions and implement package integrity
validation where supported.
```

---

# Example Finding - Anonymous Share

```text
Finding:
Network Share Accessible Without Authentication

Description:
The SMB server allowed unauthenticated access to a network share from
the assessment network.

The share exposed internal files and directory names without requiring
a domain identity.

Impact:
Any system with network access to the SMB service may obtain the
exposed information.

The information may assist infrastructure reconnaissance or disclose
sensitive business data.

Recommendation:
Disable unnecessary anonymous or guest SMB access.

Require authenticated access and apply least-privilege share and NTFS
permissions.
```

---

# Example Finding - Legacy Backup

```text
Finding:
Legacy Backup Files Expose Sensitive Configuration Data

Description:
A shared backup directory contained historical copies of application
configuration files.

The backup files were readable by a broad domain group and contained
security-sensitive configuration values.

Impact:
Historical backups can preserve credentials or secrets even after the
live application configuration has been remediated.

An attacker may therefore recover previously exposed credentials from
older copies.

Recommendation:
Restrict access to backup repositories, remove obsolete backups
according to retention requirements and rotate any credentials exposed
in historical copies.

Include backup locations in future secret-scanning and access reviews.
```

---

# Share Assessment Checklist

## Discovery

- [ ] Identify file servers
- [ ] Identify domain controllers
- [ ] Identify SYSVOL
- [ ] Identify NETLOGON
- [ ] Identify DFS namespaces
- [ ] Review user home-directory attributes
- [ ] Review profile paths
- [ ] Review logon scripts
- [ ] Review mapped drives
- [ ] Review deployment infrastructure

## Share Enumeration

- [ ] Enumerate SMB shares
- [ ] Identify hidden shares
- [ ] Identify administrative shares
- [ ] Identify department shares
- [ ] Identify backup shares
- [ ] Identify deployment shares
- [ ] Identify user shares
- [ ] Identify anonymous access
- [ ] Identify guest access

## Permissions

- [ ] Review share permissions
- [ ] Review NTFS permissions
- [ ] Determine effective access
- [ ] Identify inherited permissions
- [ ] Identify direct permissions
- [ ] Identify broad groups
- [ ] Review nested groups
- [ ] Review foreign principals
- [ ] Review SID History where relevant

## Access

- [ ] Determine list access
- [ ] Determine read access
- [ ] Determine create access
- [ ] Determine write access
- [ ] Determine modify access
- [ ] Determine delete access
- [ ] Determine Full Control
- [ ] Do not assume write implies execution

## Content

- [ ] Review SYSVOL scripts
- [ ] Search for legacy `cpassword`
- [ ] Review configuration files
- [ ] Review deployment scripts
- [ ] Review backup files
- [ ] Review private keys
- [ ] Review certificates
- [ ] Review password vaults
- [ ] Review database backups
- [ ] Review source-code/configuration exposure where in scope

## Credentials

- [ ] Search targeted files for credential indicators
- [ ] Identify credential owner
- [ ] Identify intended service
- [ ] Confirm credential validation is authorised
- [ ] Use minimal validation
- [ ] Avoid password spraying unless authorised
- [ ] Protect discovered secrets
- [ ] Redact report evidence

## Write Validation

- [ ] Confirm write testing is authorised
- [ ] Use approved directory
- [ ] Use uniquely named harmless file
- [ ] Do not modify existing files
- [ ] Do not upload executable payloads unnecessarily
- [ ] Verify file creation
- [ ] Remove test file
- [ ] Verify cleanup

## SMB Security

- [ ] Review SMB version
- [ ] Identify SMBv1
- [ ] Review SMB signing
- [ ] Review SMB encryption where required
- [ ] Review anonymous access
- [ ] Review guest access
- [ ] Review network exposure

## Detection

- [ ] Monitor 5140
- [ ] Monitor 5145 where appropriate
- [ ] Monitor 5142
- [ ] Monitor 5143
- [ ] Monitor 5144
- [ ] Monitor 4663 for sensitive files where configured
- [ ] Correlate 4624
- [ ] Correlate 4625
- [ ] Monitor administrative shares
- [ ] Monitor unusual recursive reads
- [ ] Monitor sensitive-file access
- [ ] Monitor permission changes

## Hardening

- [ ] Apply least privilege
- [ ] Use role-based groups
- [ ] Separate read and write groups
- [ ] Remove unnecessary anonymous access
- [ ] Remove unnecessary guest access
- [ ] Disable SMBv1
- [ ] Require SMB signing where appropriate
- [ ] Use SMB encryption where appropriate
- [ ] Protect deployment shares
- [ ] Protect backup shares
- [ ] Remove plaintext credentials
- [ ] Use managed identities
- [ ] Review stale shares
- [ ] Review stale groups
- [ ] Review legacy files

## Reporting

- [ ] Do not report share existence alone
- [ ] Do not report normal SYSVOL readability alone
- [ ] Do not report ADMIN$ existence alone
- [ ] Identify affected share
- [ ] Identify affected path
- [ ] Identify identity used
- [ ] Identify effective permission
- [ ] Identify sensitive content
- [ ] Demonstrate realistic impact
- [ ] Minimise collected data
- [ ] Redact sensitive evidence
- [ ] Provide permission-specific remediation

---

# Share Testing Model

The basic model is:

```text
Identity
   |
   v
SMB Server
   |
   v
Share
   |
   v
Directory
   |
   v
File
```

The permission model is:

```text
Identity
   |
   v
Share ACL
   |
   v
NTFS ACL
   |
   v
Effective Access
```

The group model is:

```text
User
 |
 v
Global Group
 |
 v
Domain Local Group
 |
 v
Resource Permission
```

The read-risk model is:

```text
Low-Privilege User
       |
       v
Readable Share
       |
       v
Sensitive File
       |
       v
Information / Credential Exposure
```

The write-risk model is:

```text
Low-Privilege User
       |
       v
Writable Share
       |
       v
Trusted File or Directory
       |
       v
Another User / Service
       |
       v
Potential Security Impact
```

The important qualification is:

```text
Writable Share
     !=
Automatic Code Execution
```

The credential model is:

```text
Share
 |
 v
Configuration File
 |
 v
Credential
 |
 v
Account
 |
 v
Accessible Service
 |
 v
Potential Privilege
```

The migration model is:

```text
Legacy Share ACL
      |
      v
Historical SID
      |
      v
SID History
      |
      v
Current User
      |
      v
Access
```

The cross-domain model is:

```text
Trusted User
     |
     v
Trust Authentication
     |
     v
Group / ACL
     |
     v
Share
```

The detection model is:

```text
Authentication
      |
      v
SMB Connection
      |
      v
Share Access
      |
      v
File Access
      |
      v
Potential Modification
```

The defensive model is:

```text
Least Privilege
      +
Group-Based Access
      +
NTFS Security
      +
SMB Security
      +
Secret Management
      +
Sensitive Data Protection
      +
Monitoring
      +
Lifecycle Management
      =
Reduced Share Risk
```

For penetration testers:

```text
Do Not Ask:
"How much can I download?"

Ask:
"What is the minimum evidence required
to demonstrate the access-control or
secret-management weakness?"
```

For defenders:

```text
Do Not Ask:
"Who can connect to the file server?"

Ask:
"Which identities can access each
sensitive dataset, why do they need
that access, and would we detect
unexpected use?"
```

The complete model is:

```text
Identity
   |
   v
Authentication
   |
   v
Share Permission
   |
   v
NTFS Permission
   |
   v
File / Directory
   |
   v
Sensitive Information or Trusted Content
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

SMB:

[SMB](smb.md)

Groups:

[Groups](groups.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Group Policy:

[Group Policy](group-policy.md)

Credential Access:

[Credential Access](credential-access.md)

gMSA:

[gMSA](gmsa.md)

NTDS:

[NTDS](ntds.md)

NTLM:

[NTLM](ntlm.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

Trust Relationships:

[Trust Relationships](trust-relationships.md)

SID History:

[SID History](sid-history.md)

ADIDNS:

[Active Directory Integrated DNS](adidns.md)

The next infrastructure page is:

```text
docs/active-directory/sccm.md
```

followed by:

```text
docs/active-directory/wsus.md
docs/active-directory/mdt.md
docs/active-directory/scom.md
docs/active-directory/adfs.md
docs/active-directory/rodc.md
```

---

# References

## Microsoft - SMB File Shares

[Microsoft - SMB File Shares](https://learn.microsoft.com/en-us/windows-server/storage/file-server/file-server-smb-overview){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Security

[Microsoft - SMB Security Hardening](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security-hardening){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Signing

[Microsoft - SMB Signing](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SMB Encryption

[Microsoft - SMB Encryption](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-SmbShare

[Microsoft - Get-SmbShare](https://learn.microsoft.com/en-us/powershell/module/smbshare/get-smbshare){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-SmbShareAccess

[Microsoft - Get-SmbShareAccess](https://learn.microsoft.com/en-us/powershell/module/smbshare/get-smbshareaccess){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - SYSVOL

[Microsoft - SYSVOL](https://learn.microsoft.com/en-us/windows-server/storage/dfs-replication/sysvol-dfsr-migration-guide){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Group Policy Preferences Password Behaviour

[Microsoft - MS14-025](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Audit File Share

[Microsoft - Audit File Share](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-file-share){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Audit Detailed File Share

[Microsoft - Audit Detailed File Share](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-detailed-file-share){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 5140

[Microsoft - 5140: A Network Share Object Was Accessed](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5140){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 5145

[Microsoft - 5145: A Network Share Object Was Checked](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5145){ target="_blank" rel="noopener noreferrer" }

---

## Samba - smbclient

[Samba - smbclient](https://www.samba.org/samba/docs/current/man-html/smbclient.1.html){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## Fortra - Impacket

[GitHub - Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Network Share Discovery

[MITRE ATT&CK - T1135 Network Share Discovery](https://attack.mitre.org/techniques/T1135/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Data from Network Shared Drive

[MITRE ATT&CK - T1039 Data from Network Shared Drive](https://attack.mitre.org/techniques/T1039/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Windows shares are much more than file-storage locations.

In Active Directory they often connect:

```text
Users
Groups
Servers
Applications
Deployment
Backups
Credentials
```

The basic assessment model is:

```text
Discover Share
      |
      v
Determine Permission
      |
      v
Understand Purpose
      |
      v
Identify Relevant Content
      |
      v
Validate Minimum Impact
      |
      v
Report
```

The presence of:

```text
SYSVOL
NETLOGON
ADMIN$
C$
```

is not itself a vulnerability.

Likewise:

```text
Readable Share
```

does not automatically mean:

```text
Security Finding
```

The important question is:

```text
Can an identity access or modify
information that it should not?
```

For readable shares, focus on:

```text
Sensitive Data
Credentials
Configuration
Backups
Private Keys
```

For writable shares, focus on:

```text
Who Consumes the Content?
```

The most important distinction is:

```text
Write Access
    !=
Automatic Code Execution
```

A strong assessment demonstrates the actual dependency rather than assuming impact.

The defensive objective is:

```text
Least Privilege
      |
      v
Role-Based Groups
      |
      v
Secure SMB
      |
      v
Protected Sensitive Data
      |
      v
Secret Management
      |
      v
Monitoring
```

The next page moves into enterprise endpoint and software-management infrastructure:

```text
Microsoft Configuration Manager (SCCM)
```
