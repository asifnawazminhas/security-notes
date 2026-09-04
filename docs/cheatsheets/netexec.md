# NetExec Cheatsheet

Quick-reference guide for using NetExec during authorised internal penetration tests, Active Directory assessments and red-team engagements.

NetExec, commonly invoked as `nxc`, is a network service enumeration and assessment framework descended from CrackMapExec.

It supports multiple protocols and can be used for:

```text
Host Discovery
Service Enumeration
Authentication Validation
SMB Assessment
LDAP Enumeration
WinRM Assessment
MSSQL Enumeration
SSH Assessment
RDP Assessment
NFS Assessment
FTP Assessment
WMI Assessment
VNC Assessment
Security Configuration Review
Share Enumeration
Active Directory Enumeration
BloodHound Collection
Module-Based Enumeration
```

!!! warning "Authorised testing only"
    NetExec can authenticate to many systems quickly and can perform actions that generate significant authentication traffic or modify remote systems. Use it only against systems you own or are explicitly authorised to assess. Understand account lockout policy and the rules of engagement before authentication testing.

For deeper Active Directory methodology see:

[Active Directory Cheatsheet](active-directory.md)

---

# Quick Start

A useful NetExec workflow:

```text
Targets
   |
   v
Protocol Discovery
   |
   v
Unauthenticated Enumeration
   |
   v
Security Configuration
   |
   v
Authorised Credentials
   |
   v
Authentication Validation
   |
   v
Users / Groups / Shares
   |
   v
LDAP / AD Enumeration
   |
   v
Administrative Access Mapping
   |
   v
Modules
   |
   v
Manual Validation
```

Typical starting commands:

```bash
nxc smb 10.10.10.0/24
```

```bash
nxc ldap dc01.example.local
```

```bash
nxc winrm 10.10.10.0/24
```

---

# Help

Global help:

```bash
nxc --help
```

Protocol help:

```bash
nxc smb --help
```

```bash
nxc ldap --help
```

```bash
nxc winrm --help
```

Always check the installed version's help before relying on an option copied from an older cheatsheet.

---

# Version

```bash
nxc --version
```

NetExec changes regularly.

Commands and modules may differ between releases.

---

# Installed Protocols

Run:

```bash
nxc --help
```

The available protocols depend on the installed NetExec version.

Common protocols include:

```text
SMB
LDAP
WINRM
WMI
MSSQL
SSH
FTP
RDP
NFS
VNC
```

---

# Target Formats

NetExec accepts several target forms.

Single IP:

```bash
nxc smb 10.10.10.10
```

Hostname:

```bash
nxc smb server01.example.local
```

CIDR:

```bash
nxc smb 10.10.10.0/24
```

Range:

```bash
nxc smb 10.10.10.10-20
```

Target file:

```bash
nxc smb targets.txt
```

---

# Target File

Example:

```text
10.10.10.10
10.10.10.11
server01.example.local
server02.example.local
```

Run:

```bash
nxc smb targets.txt
```

Target files are useful for separating discovery from later authenticated testing.

---

# DNS Resolution

Active Directory testing depends heavily on DNS.

Before troubleshooting Kerberos or LDAP, confirm:

```bash
dig dc01.example.local
```

```bash
nslookup dc01.example.local
```

Check your resolver:

```bash
cat /etc/resolv.conf
```

A large percentage of Kerberos problems are actually:

```text
DNS
Time
Hostname
Realm
SPN
```

problems.

---

# Starting Position - No Credentials

A common internal assessment begins with:

```text
Internal Network
      |
      v
No Credentials
      |
      v
NetExec SMB Discovery
```

Start with:

```bash
nxc smb 10.10.10.0/24
```

This can provide useful host and SMB information without assuming domain credentials.

---

# SMB Host Discovery

```bash
nxc smb 10.10.10.0/24
```

Useful output may include:

```text
IP
Hostname
Domain
Operating System
SMB Signing
SMB Version Information
```

This is one of the most useful initial NetExec commands during an internal Windows assessment.

---

# Save Discovery Output

Standard shell redirection:

```bash
nxc smb 10.10.10.0/24 | tee smb-discovery.txt
```

Preserve raw evidence before filtering.

---

# Extract Hosts

Example shell processing:

```bash
grep 'SMB' smb-discovery.txt
```

For complex engagements, prefer NetExec's database and workspaces rather than relying entirely on text parsing.

---

# SMB Signing

SMB signing is particularly important when assessing NTLM relay exposure.

Generate a relay candidate list:

```bash
nxc smb 10.10.10.0/24 --gen-relay-list relay.txt
```

Review:

```bash
cat relay.txt
```

Important:

```text
SMB Signing Not Required
          !=
NTLM Relay Vulnerability
```

A complete relay path still depends on:

```text
Authentication Source
Target Protocol
Target Authentication
Signing / Binding
Privileges
Network Reachability
Protocol Configuration
```

Treat the relay list as a candidate list.

---

# SMBv1

Check protocol help first:

```bash
nxc smb --help
```

For dedicated SMB protocol-version validation, Nmap is also useful:

```bash
nmap -p 445 --script smb-protocols 10.10.10.10
```

Do not infer SMBv1 status from unrelated SMB output.

---

# SMB Shares - Authenticated

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    --shares
```

Subnet:

```bash
nxc smb 10.10.10.0/24 \
    -u username \
    -p 'Password' \
    --shares
```

Look for:

```text
Readable Shares
Writable Shares
Administrative Shares
Deployment Shares
Backup Shares
User Shares
Software Shares
SYSVOL
NETLOGON
```

---

# Avoid Passwords in Shell History

This:

```bash
nxc smb 10.10.10.10 -u username -p 'Password'
```

is convenient for examples but may expose credentials through:

```text
Shell History
Process Listings
Terminal Logging
Assessment Notes
Screenshots
```

Use credential-handling methods appropriate to the engagement.

---

# Domain Authentication

```bash
nxc smb 10.10.10.10 \
    -d example.local \
    -u username \
    -p 'Password'
```

The domain can also often be represented through other accepted username formats.

Check:

```bash
nxc smb --help
```

for the installed version.

---

# Multiple Targets

```bash
nxc smb targets.txt \
    -d example.local \
    -u username \
    -p 'Password'
```

NetExec is designed for parallel network assessment.

This is powerful but can create substantial authentication traffic.

---

# Authentication Safety

Before testing credentials determine:

```text
Domain Password Policy
Fine-Grained Password Policies
Account Lockout Threshold
Lockout Observation Window
Lockout Duration
Approved Accounts
Approved Passwords
Allowed Rate
```

Do not use NetExec as a blind password-spraying engine.

---

# Single Credential Validation

Prefer validating one approved credential against one target first:

```bash
nxc smb 10.10.10.10 \
    -d example.local \
    -u username \
    -p 'Password'
```

Then expand only where necessary.

---

# Username File

Where explicitly authorised:

```bash
nxc smb 10.10.10.10 \
    -u users.txt \
    -p 'ApprovedPassword'
```

This may generate many authentication attempts.

Understand lockout behaviour first.

---

# Password File

Similarly:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p passwords.txt
```

Do not use uncontrolled password lists against production accounts.

---

# Username + Password Lists

NetExec can work with lists, but this can quickly become a high-volume authentication test.

Before doing so:

```text
STOP
 |
 v
Check Lockout Policy
 |
 v
Check Scope
 |
 v
Check Attempt Count
 |
 v
Check Rate
 |
 v
Proceed Only If Approved
```

---

# Local Authentication

When assessing a local account rather than a domain account, check the protocol help for the current local-authentication option:

```bash
nxc smb --help
```

Keep local and domain credentials clearly separated in notes.

A reused local administrator credential can have a very different impact from a domain credential.

---

# Pass-the-Hash Validation

Where NTLM hash authentication is explicitly authorised, NetExec supports NTLM-based authentication workflows.

Check the installed syntax:

```bash
nxc smb --help
```

Example form:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -H '<NTLM_HASH>'
```

Do not collect or use password hashes outside the approved credential-access scope.

The existence of NTLM authentication does not itself constitute a vulnerability.

---

# Kerberos Authentication

Kerberos should be preferred where the assessment requires testing Kerberos-specific behaviour.

Check:

```bash
nxc smb --help
```

and:

```bash
nxc ldap --help
```

for current Kerberos options.

Before troubleshooting Kerberos verify:

```bash
date
```

```bash
dig dc01.example.local
```

```bash
klist
```

---

# Kerberos Troubleshooting

Think:

```text
Kerberos Failure
      |
      +--> DNS?
      |
      +--> Time?
      |
      +--> Realm?
      |
      +--> Hostname?
      |
      +--> SPN?
      |
      +--> Ticket?
      |
      +--> Credential?
```

Do not immediately assume the account password is wrong.

---

# SMB Users

Authenticated enumeration:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    --users
```

Availability and behaviour can depend on target configuration and NetExec version.

---

# SMB Groups

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    --groups
```

---

# Logged-On Users

Where supported and authorised:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    --loggedon-users
```

This can reveal sensitive session information.

Use only where required by scope.

---

# Sessions

Session enumeration can be security sensitive because it helps map credential and lateral-movement paths.

Check current options:

```bash
nxc smb --help
```

Collect only what is required for the assessment.

---

# Local Administrators

When authenticated with appropriate rights, identify local administrative relationships rather than immediately performing remote execution.

A useful assessment question is:

```text
Where is this identity an administrator?
```

rather than:

```text
Where can I execute commands?
```

---

# Administrative Access

NetExec output may identify elevated access.

Interpret this as:

```text
Credential
   |
   v
Target
   |
   v
Administrative Relationship
```

Then determine whether that relationship is intended.

Do not automatically perform command execution.

---

# SYSVOL

Enumerate shares:

```bash
nxc smb dc01.example.local \
    -u username \
    -p 'Password' \
    --shares
```

Then use a dedicated SMB client for careful file inspection:

```bash
smbclient //dc01.example.local/SYSVOL -U username
```

Look for:

```text
Logon Scripts
Group Policy Files
Deployment Scripts
Configuration
Legacy Credentials
Internal Hostnames
```

---

# NETLOGON

Similarly:

```bash
smbclient //dc01.example.local/NETLOGON -U username
```

Review scripts carefully.

Do not modify domain logon scripts during enumeration.

---

# Spidering Shares

NetExec includes modules and capabilities that can search accessible SMB content.

Before using broad spidering:

```text
How large is the share?
Is sensitive user data present?
Will the operation generate excessive traffic?
Is downloading allowed?
```

Prefer targeted searches over indiscriminate collection.

---

# Important spider_plus Security Note

Keep NetExec updated.

Older NetExec versions had a security issue affecting the `spider_plus` module that was fixed in the 1.5.1 release.

Check:

```bash
nxc --version
```

and update according to the official project documentation before using the tool in an engagement.

---

# LDAP

LDAP is one of the most useful NetExec protocols for authenticated Active Directory enumeration.

Basic:

```bash
nxc ldap dc01.example.local
```

Authenticated:

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password'
```

---

# LDAP Domain

Specify domain where required:

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u username \
    -p 'Password'
```

---

# LDAP Users

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' \
    --users
```

---

# LDAP Active Users

Current NetExec versions may provide filtering for active users.

Check:

```bash
nxc ldap --help
```

Where supported:

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' \
    --active-users
```

This is useful for reducing noise from disabled accounts.

---

# LDAP Groups

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' \
    --groups
```

---

# LDAP Computers

Check current LDAP options:

```bash
nxc ldap --help
```

NetExec capabilities evolve, so use built-in help rather than relying on old CrackMapExec syntax.

---

# LDAP Password Policy

Password-policy enumeration is particularly useful before authentication testing.

Check:

```bash
nxc ldap --help
```

and use the current password-policy option supported by the installed version.

Cross-check important lockout values with native AD tooling where possible.

---

# LDAP AS-REP Candidates

NetExec can assist with identifying Active Directory account configurations relevant to Kerberos assessment.

Check:

```bash
nxc ldap --help
```

Validate candidate accounts manually before reporting.

The relevant condition is:

```text
Kerberos Preauthentication Disabled
```

not merely whether a tool labels an account interesting.

---

# LDAP Kerberoasting Candidates

Service Principal Names can be enumerated through LDAP.

Think:

```text
User
 |
 v
SPN
 |
 v
Service Account
 |
 v
Password Strength
 |
 v
Privileges
```

An SPN is normal Active Directory functionality.

The security risk depends on account password strength and privileges.

---

# LDAP Delegation

Review current LDAP options and modules for delegation-related enumeration:

```bash
nxc ldap --help
```

Look for:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

Validate relationships against AD attributes and BloodHound.

---

# LDAP Trusts

Trust enumeration should determine:

```text
Trusted Domain
Direction
Transitivity
Trust Type
Forest Relationship
```

Check current LDAP capabilities:

```bash
nxc ldap --help
```

Cross-check with:

```cmd
nltest /domain_trusts
```

or:

```powershell
Get-ADTrust -Filter *
```

where available.

---

# LDAP AD CS Discovery

NetExec includes LDAP modules and functionality that can assist with Active Directory Certificate Services assessment.

List LDAP modules:

```bash
nxc ldap -L
```

Search for relevant certificate and AD CS modules in the installed version.

For comprehensive AD CS enumeration also use:

```text
Certipy
Certify
Native Certificate Tools
LDAP
```

See:

[Active Directory Cheatsheet](active-directory.md)

---

# LDAP Security Controls

When assessing LDAP, think beyond directory objects.

Review:

```text
LDAP Signing
LDAP Channel Binding
LDAPS
NTLM Authentication
Certificate Configuration
Relay Exposure
```

Do not infer LDAP security solely from port 636 being open.

---

# WinRM

Discovery:

```bash
nxc winrm 10.10.10.0/24
```

Authenticated validation:

```bash
nxc winrm 10.10.10.10 \
    -u username \
    -p 'Password'
```

---

# WinRM Interpretation

Successful WinRM authentication indicates remote management access.

Determine:

```text
Which user?
Which target?
Which group grants access?
Is access expected?
Is the account administrative?
```

Do not automatically treat WinRM access as a vulnerability.

---

# Remote Management Users

On Windows:

```cmd
net localgroup "Remote Management Users"
```

Membership may explain intended WinRM access.

---

# RDP

Check current protocol support:

```bash
nxc rdp --help
```

Basic discovery:

```bash
nxc rdp 10.10.10.0/24
```

Authentication testing should follow the same lockout precautions as SMB and WinRM.

---

# MSSQL

Discovery:

```bash
nxc mssql 10.10.10.0/24
```

Authenticated assessment:

```bash
nxc mssql 10.10.10.10 \
    -u username \
    -p 'Password'
```

SQL Server authentication and Windows authentication may behave differently.

Check:

```bash
nxc mssql --help
```

---

# MSSQL Assessment Questions

Determine:

```text
Authentication Method
Database Role
Server Role
Linked Servers
Service Account
Domain Context
Impersonation Rights
Network Reachability
```

Do not immediately enable or invoke command-execution features.

---

# SSH

Discovery:

```bash
nxc ssh 10.10.10.0/24
```

Authenticated:

```bash
nxc ssh 10.10.10.10 \
    -u username \
    -p 'Password'
```

Use only approved credentials.

---

# FTP

Discovery:

```bash
nxc ftp 10.10.10.0/24
```

Check:

```bash
nxc ftp --help
```

Assess:

```text
Anonymous Access
Authentication
Readable Files
Writable Locations
Sensitive Files
```

Do not upload test files unless permitted.

---

# NFS

Where supported:

```bash
nxc nfs 10.10.10.0/24
```

Check:

```bash
nxc nfs --help
```

Review:

```text
Exports
Permissions
Root Squashing
Writable Exports
Sensitive Data
```

---

# WMI

Check:

```bash
nxc wmi --help
```

WMI can provide remote-management functionality.

Successful authentication or management access should first be treated as an access-control relationship.

Do not automatically perform command execution.

---

# VNC

Check:

```bash
nxc vnc --help
```

Use VNC protocol assessment only where the service is in scope.

---

# Modules

NetExec modules extend protocol functionality.

List SMB modules:

```bash
nxc smb -L
```

LDAP:

```bash
nxc ldap -L
```

MSSQL:

```bash
nxc mssql -L
```

The available module set depends on the installed NetExec version.

---

# Module Help

Module options:

```bash
nxc smb -M <module> --options
```

Example structure:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    -M <module>
```

---

# Module Options

Options generally use:

```bash
-o KEY=value
```

Example structure:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    -M <module> \
    -o OPTION=value
```

Always inspect:

```bash
nxc smb -M <module> --options
```

before running a module.

---

# Multiple Modules

Current NetExec versions support specifying multiple modules.

General form:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    -M module1 \
    -M module2
```

However, running many modules simultaneously can generate unnecessary traffic and complicate evidence collection.

Prefer targeted execution.

---

# Module Categories

Modules may perform different classes of operations.

Examples include:

```text
Enumeration
Privilege Escalation
Credential Access
Remote Interaction
Configuration Assessment
```

Read the module description before execution.

Do not assume a module is read-only.

---

# Safe Module Workflow

Use:

```text
List Modules
    |
    v
Read Description
    |
    v
Check Options
    |
    v
Understand Privileges
    |
    v
Understand Side Effects
    |
    v
Run Against One Target
    |
    v
Review Output
    |
    v
Expand If Necessary
```

---

# Audit Mode

Recent NetExec documentation includes an audit mode.

Check the installed version:

```bash
nxc --help
```

and the protocol-specific help.

Audit-oriented operation is useful when the engagement prioritises enumeration and configuration assessment over invasive actions.

---

# BloodHound Integration

NetExec supports integration with BloodHound-oriented workflows.

Check current LDAP options:

```bash
nxc ldap --help
```

and the official NetExec documentation.

BloodHound should be used to analyse relationships rather than as proof that every discovered edge is exploitable.

See:

[BloodHound Cheatsheet](bloodhound.md)

---

# BloodHound Workflow

```text
NetExec / LDAP
      |
      v
AD Information
      |
      v
BloodHound Collection
      |
      v
Graph
      |
      v
Candidate Path
      |
      v
Manual Validation
```

---

# NetExec Database

NetExec stores assessment information in its own database.

Launch:

```bash
nxcdb
```

This is particularly useful during larger engagements.

---

# Workspaces

Workspaces separate engagement data.

Launch:

```bash
nxcdb
```

Then:

```text
workspace list
```

Create:

```text
workspace create assessment
```

Switch:

```text
workspace assessment
```

Use separate workspaces for separate engagements.

---

# Database Location

NetExec workspaces are normally stored under:

```text
~/.nxc/workspaces/
```

Protect this directory.

It may contain sensitive assessment data and credentials.

---

# Protocol Database

Inside `nxcdb`:

```text
proto smb
```

Return:

```text
back
```

Another protocol:

```text
proto ldap
```

---

# Database Help

Inside:

```text
help
```

Protocol-specific database commands differ.

Always inspect help before exporting or deleting data.

---

# Database Credentials

NetExec can store credentials discovered or used during an assessment.

Treat:

```text
~/.nxc/
```

as sensitive engagement material.

Protect:

```text
Permissions
Backups
Screenshots
Exports
Terminal Logs
```

---

# Database Export

NetExec supports exporting information from its database.

Inside the SMB database:

```text
help export
```

Example structure:

```text
export shares detailed shares.csv
```

Export only the data required for reporting or analysis.

---

# Workspace Hygiene

Recommended:

```text
One Engagement
      =
One Workspace
```

Avoid mixing:

```text
Customer A
Customer B
Lab Data
CTF Data
Personal Testing
```

in the same workspace.

---

# Authentication Mapping

A useful NetExec workflow is to build an access matrix.

Example:

| Identity | Host | SMB | WinRM | Admin |
|---|---|---|---|---|
| user1 | WS01 | Yes | No | No |
| user1 | SRV01 | Yes | Yes | No |
| admin1 | SRV01 | Yes | Yes | Yes |

This is more useful than immediately executing commands.

---

# Access Mapping Model

```text
Credential
    |
    v
Targets
    |
    v
Authentication
    |
    v
Access Level
    |
    v
Expected?
```

---

# Local Administrator Reuse

If an approved local administrative credential is available, assess whether it is reused across multiple hosts.

The security issue is:

```text
Same Local Administrative Secret
              |
              v
Multiple Hosts
              |
              v
Lateral Movement Risk
```

Do not perform uncontrolled authentication attempts.

---

# Domain Administrator Exposure

Do not routinely test highly privileged credentials across every workstation.

This creates unnecessary authentication exposure and may generate credentials on systems where they should never appear.

Prefer:

```text
Least Privileged Test Account
      |
      v
Targeted Validation
```

---

# Authentication Failure Analysis

Common errors can indicate:

```text
Bad Password
Disabled Account
Expired Password
Locked Account
Logon Restriction
Protocol Restriction
Signing Requirement
Authentication Policy
Network Failure
DNS Failure
```

Do not retry repeatedly without understanding the error.

---

# Password Spraying with NetExec

NetExec can perform high-volume authentication testing.

That does not mean it should be used blindly.

Before spraying:

```text
Get Password Policy
        |
        v
Get Fine-Grained Policies
        |
        v
Determine Lockout Threshold
        |
        v
Determine Observation Window
        |
        v
Define Approved Accounts
        |
        v
Define Attempt Count
        |
        v
Obtain Approval
```

Prefer dedicated controlled spray procedures where the assessment specifically includes password auditing.

---

# Credential Types

Keep credential types distinct:

```text
Domain Password
Local Password
NTLM Hash
Kerberos Ticket
Certificate
SSH Key
Database Credential
```

They have different security implications.

---

# Certificates

Modern NetExec versions include certificate-related authentication functionality for supported protocols.

Check:

```bash
nxc <protocol> --help
```

Use certificate authentication only where the certificate and associated identity are within scope.

---

# Kerberos Tickets

If using an existing authorised Kerberos credential cache:

```bash
klist
```

Check:

```bash
echo "$KRB5CCNAME"
```

Then consult:

```bash
nxc <protocol> --help
```

for current Kerberos options.

---

# Relay Candidate Discovery

A safe early relay workflow is:

```text
Discover Hosts
      |
      v
Check SMB Signing
      |
      v
Identify Candidates
      |
      v
Review LDAP Protections
      |
      v
Review HTTP Endpoints
      |
      v
Determine Authentication Source
      |
      v
Obtain Approval
      |
      v
Controlled Validation
```

NetExec can help with the discovery stages.

Do not jump directly from:

```text
Signing Not Required
```

to:

```text
Perform Relay
```

---

# LDAP Relay Considerations

Assess:

```text
LDAP Signing
LDAP Channel Binding
LDAPS
EPA
Authentication Method
Target Privileges
```

Relay viability depends on the complete chain.

---

# Coercion Considerations

Authentication coercion can affect production services.

Before testing:

```text
Is coercion in scope?
Which protocol is triggered?
Which account authenticates?
Where will authentication go?
Could the service become unstable?
Is relay also authorised?
```

Discovery and exploitation are separate phases.

---

# AD CS Relay Considerations

When AD CS is present, investigate:

```text
Certificate Authority
Web Enrollment
Enrollment Services
HTTP vs HTTPS
Extended Protection
Authentication
Templates
Enrollment Rights
```

Use dedicated AD CS tooling for comprehensive analysis.

See:

[Active Directory Cheatsheet](active-directory.md)

---

# Logging

For evidence:

```bash
nxc smb 10.10.10.0/24 | tee smb.txt
```

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' |
    tee ldap.txt
```

Be aware that logs may contain:

```text
Usernames
Domains
Hostnames
Credentials
Hashes
Share Names
Sensitive Paths
```

Protect them appropriately.

---

# Timestamp Evidence

Before important tests:

```bash
date -Is
```

Record:

```text
Timestamp
Source
Target
Identity
Command
Result
```

This helps correlate testing with:

```text
SIEM
EDR
Windows Event Logs
Firewall Logs
SOC Alerts
```

---

# Evidence Model

For each important NetExec result record:

```text
Source Host
Source IP
Target Host
Target IP
Protocol
Identity
Authentication Type
Observed Access
Security Control
Impact
```

---

# Example - SMB Signing

Weak evidence:

```text
Signing: False
```

Better:

```text
Host: WS01
IP: 10.10.10.25
Protocol: SMB
SMB signing required: No
Authentication source available: Not yet established
Relay path: Not validated
```

Conclusion:

```text
Potential relay target requiring additional validation.
```

---

# Example - Administrative Access

Weak:

```text
Pwn3d!
```

Better:

```text
Identity:
EXAMPLE\user1

Target:
SRV01

Protocol:
SMB

Observed:
Administrative access

Expected:
User should not administer server

Impact:
Potential excessive privilege and lateral movement path
```

---

# Example - Writable Share

Weak:

```text
Share is writable.
```

Better:

```text
Identity
   |
   v
Writable Share
   |
   v
What consumes files?
   |
   v
Privileged deployment process?
   |
   v
Security boundary?
```

A writable share is not automatically privilege escalation.

---

# Example - WinRM

Weak:

```text
WinRM login successful.
```

Better:

```text
Domain User
     |
     v
WinRM Authentication
     |
     v
Remote Management Group?
     |
     v
Administrative Rights?
     |
     v
Expected Access?
```

---

# Example - Kerberoast Candidate

Weak:

```text
SPN found.
```

Better:

```text
Account
   |
   v
SPN
   |
   v
Service Ticket
   |
   v
Password Strength
   |
   v
Privileges
   |
   v
Security Impact
```

---

# Common Mistakes

Avoid:

```text
Running password lists without checking lockout policy
Testing Domain Admin credentials everywhere
Assuming Pwn3d means a vulnerability
Assuming SMB signing disabled means relay is guaranteed
Running every module
Dumping credentials by default
Spidering every share recursively
Mixing customer data in the same workspace
Using old CrackMapExec syntax without checking help
Ignoring DNS during Kerberos troubleshooting
Treating tool output as final evidence
```

---

# NetExec vs CrackMapExec

NetExec is the actively maintained continuation/fork of the CrackMapExec project lineage.

Modern documentation and commands use:

```text
nxc
```

rather than relying on old:

```text
crackmapexec
cme
```

examples.

When an old write-up says:

```bash
crackmapexec smb ...
```

look for the equivalent current NetExec syntax:

```bash
nxc smb ...
```

and verify options using:

```bash
nxc smb --help
```

---

# NetExec vs Impacket

Think:

```text
NetExec
   =
Network-Scale Enumeration
Authentication Mapping
Protocol Assessment
Modules
AD Enumeration

Impacket
   =
Protocol Utilities
Kerberos Operations
SMB / RPC Tools
Targeted Remote Administration
Specialised AD Operations
```

They complement each other.

See:

[Impacket Cheatsheet](impacket.md)

---

# NetExec vs BloodHound

```text
NetExec
   |
   v
Hosts / Authentication / AD Information
   |
   v
BloodHound
   |
   v
Relationships / Paths
```

Use BloodHound when the question becomes:

```text
How does this identity reach that privilege?
```

See:

[BloodHound Cheatsheet](bloodhound.md)

---

# NetExec vs Nmap

```text
Nmap
 |
 +--> Network Discovery
 +--> Port Discovery
 +--> Service Fingerprinting
 +--> NSE

NetExec
 |
 +--> Protocol-Aware Enumeration
 +--> Authentication
 +--> Windows / AD Context
 +--> Access Mapping
```

A useful workflow:

```text
Nmap
  ->
NetExec
  ->
LDAP / SMB Enumeration
  ->
BloodHound
  ->
Manual Validation
```

---

# Internal Unauthenticated Workflow

```text
1. Identify network
2. Identify DNS
3. Discover SMB hosts
4. Identify domains
5. Identify DCs
6. Check SMB signing
7. Identify LDAP
8. Identify Kerberos
9. Identify WinRM
10. Build target lists
```

Example:

```bash
nxc smb 10.10.10.0/24
```

Then:

```bash
nxc smb 10.10.10.0/24 --gen-relay-list relay.txt
```

Then investigate identified DCs with:

```bash
nxc ldap dc01.example.local
```

---

# Authenticated Domain User Workflow

```text
1. Validate one credential
2. Enumerate SMB
3. Enumerate shares
4. Enumerate LDAP
5. Enumerate users
6. Enumerate groups
7. Identify Kerberos candidates
8. Identify delegation
9. Identify AD CS
10. Collect graph data
11. Map administrative access
12. Validate candidate paths
```

---

# Local Administrator Workflow

When an authorised local administrator credential is provided:

```text
1. Test one target
2. Determine local vs domain context
3. Map where credential works
4. Identify credential reuse
5. Determine whether reuse is intended
6. Avoid unnecessary command execution
7. Document lateral movement exposure
```

---

# Post-Compromise Workflow

If the engagement has reached an authorised Windows foothold:

```text
Windows Host
    |
    v
Identity
    |
    v
Domain
    |
    v
NetExec from Assessment Host
    |
    v
Access Mapping
    |
    v
LDAP Enumeration
    |
    v
BloodHound
    |
    v
Candidate Lateral Path
```

Do not assume a foothold means unrestricted testing is permitted.

---

# Quick SMB Commands

Discovery:

```bash
nxc smb 10.10.10.0/24
```

Credential validation:

```bash
nxc smb 10.10.10.10 \
    -d example.local \
    -u username \
    -p 'Password'
```

Shares:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    --shares
```

Users:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    --users
```

Groups:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    --groups
```

Signing candidates:

```bash
nxc smb 10.10.10.0/24 --gen-relay-list relay.txt
```

Modules:

```bash
nxc smb -L
```

---

# Quick LDAP Commands

Basic:

```bash
nxc ldap dc01.example.local
```

Authenticated:

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u username \
    -p 'Password'
```

Users:

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' \
    --users
```

Active users where supported:

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' \
    --active-users
```

Groups:

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' \
    --groups
```

Modules:

```bash
nxc ldap -L
```

---

# Quick WinRM Commands

Discovery:

```bash
nxc winrm 10.10.10.0/24
```

Authentication:

```bash
nxc winrm 10.10.10.10 \
    -u username \
    -p 'Password'
```

Help:

```bash
nxc winrm --help
```

---

# Quick MSSQL Commands

Discovery:

```bash
nxc mssql 10.10.10.0/24
```

Authentication:

```bash
nxc mssql 10.10.10.10 \
    -u username \
    -p 'Password'
```

Help:

```bash
nxc mssql --help
```

---

# Quick SSH Commands

Discovery:

```bash
nxc ssh 10.10.10.0/24
```

Authentication:

```bash
nxc ssh 10.10.10.10 \
    -u username \
    -p 'Password'
```

---

# Quick Module Commands

List:

```bash
nxc smb -L
```

Options:

```bash
nxc smb -M <module> --options
```

Run:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    -M <module>
```

With options:

```bash
nxc smb 10.10.10.10 \
    -u username \
    -p 'Password' \
    -M <module> \
    -o KEY=value
```

---

# Quick Database Commands

Launch:

```bash
nxcdb
```

Then:

```text
workspace list
workspace create assessment
workspace assessment
proto smb
help
back
proto ldap
help
```

---

# Assessment Checklist

- [ ] Check NetExec version
- [ ] Confirm engagement workspace
- [ ] Confirm target scope
- [ ] Confirm credential scope
- [ ] Check password lockout policy
- [ ] Identify DNS
- [ ] Identify domain
- [ ] Identify DCs
- [ ] Enumerate SMB hosts
- [ ] Check SMB signing
- [ ] Identify SMB shares
- [ ] Identify LDAP
- [ ] Enumerate domain users
- [ ] Enumerate active users
- [ ] Enumerate groups
- [ ] Identify Kerberos candidates
- [ ] Review delegation
- [ ] Review AD CS
- [ ] Identify WinRM
- [ ] Identify MSSQL
- [ ] Map administrative relationships
- [ ] Review NetExec modules before use
- [ ] Avoid unnecessary credential collection
- [ ] Avoid unnecessary remote execution
- [ ] Preserve evidence
- [ ] Validate important findings manually
- [ ] Protect the NetExec database
- [ ] Remove engagement data according to retention requirements

---

# Reporting Checklist

For each result ask:

```text
What did NetExec observe?

What identity was used?

What target was tested?

Was authentication required?

What permissions were present?

Is the access expected?

What security boundary exists?

Can the result be reproduced manually?

What is the actual security impact?
```

---

# Do Not Overreport

Do not automatically report:

```text
SMB Is Open
LDAP Is Open
WinRM Is Open
A Domain User Can Authenticate
A Share Exists
An SPN Exists
A User Appears in LDAP
SMB Signing Is Not Required
WinRM Authentication Works
NetExec Shows Administrative Access
A Module Produces Red Output
```

Instead determine:

```text
Configuration
     +
Identity
     +
Permission
     +
Reachability
     +
Security Boundary
     =
Security Impact
```

---

# Recommended Tool Chain

A practical internal AD assessment often looks like:

```text
Nmap
  |
  v
NetExec
  |
  +--> SMB
  |
  +--> LDAP
  |
  +--> WinRM
  |
  +--> MSSQL
  |
  v
Impacket
  |
  v
BloodHound
  |
  v
Certipy
  |
  v
Manual Validation
```

No single tool should determine the final finding.

---

# References

## NetExec Official Documentation

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

Primary reference for current NetExec usage, protocols, credentials, modules, databases, BloodHound integration and other features.

---

## NetExec GitHub

[NetExec - GitHub](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }

Use the official repository for source code, releases, installation information and current development.

---

## NetExec Wiki Source

[NetExec Wiki - GitHub](https://github.com/Pennyw0rth/NetExec-Wiki){ target="_blank" rel="noopener noreferrer" }

Useful when reviewing documentation changes and current examples.

---

## NetExec Lab

[NetExec Lab](https://github.com/Pennyw0rth/NetExec-Lab){ target="_blank" rel="noopener noreferrer" }

Official training lab for practising NetExec and related Active Directory assessment workflows in a controlled environment.

---

## Exploit Notes - Active Directory

[Exploit Notes - Active Directory](https://exploitnotes.org/exploit/windows/active-directory/){ target="_blank" rel="noopener noreferrer" }

Useful as an additional Active Directory methodology and enumeration reference.

---

## HackTricks - Active Directory

[HackTricks - Active Directory Methodology](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html){ target="_blank" rel="noopener noreferrer" }

Useful as a broad AD methodology reference.

---

## InternalAllTheThings

[InternalAllTheThings - Active Directory](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/){ target="_blank" rel="noopener noreferrer" }

Useful as an additional Active Directory technique and command reference.

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

Use alongside NetExec for protocol-specific Active Directory and Windows operations.

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

Use for Active Directory relationship and attack-path analysis.

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

Useful for Active Directory Certificate Services enumeration and authorised security assessment.

---

# Final NetExec Model

Do not use NetExec as:

```text
Get Credentials
      |
      v
Spray Entire Network
      |
      v
Run Every Module
      |
      v
Dump Everything
```

Use:

```text
Understand Scope
      |
      v
Identify Network
      |
      v
Discover Services
      |
      v
Identify Security Controls
      |
      v
Validate One Credential
      |
      v
Enumerate Relevant Data
      |
      v
Map Access
      |
      v
Identify Candidate Paths
      |
      v
Manual Validation
      |
      v
Minimal Proof
      |
      v
Report Impact
```

NetExec is most valuable when it answers questions such as:

```text
Which Windows hosts exist?

Which domain do they belong to?

Where is SMB signing not required?

Which shares can this identity access?

Which systems accept this approved credential?

Where does this identity have elevated access?

Which domain objects should be investigated further?

Which protocols expose additional attack paths?
```

The goal is not:

```text
Run as many NetExec commands as possible.
```

The goal is:

```text
Turn network-scale Windows and Active Directory information
into a validated map of identities, systems, permissions,
security controls and attack paths.
```
