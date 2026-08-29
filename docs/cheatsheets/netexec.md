# NetExec Cheatsheet

Quick-reference commands, syntax, workflows, and troubleshooting for using NetExec during authorised Windows and Active Directory security assessments.

For the detailed explanation of NetExec, its protocols, authentication models, methodology, evidence handling, detection, and reporting, see:

[NetExec](../active-directory/netexec.md)

---

# What Is NetExec?

NetExec, commonly invoked as:

```bash
nxc
```

is a network service assessment tool designed for efficiently testing and enumerating multiple systems.

It is particularly useful for:

```text
Host discovery
SMB enumeration
LDAP enumeration
Credential validation
Administrative access mapping
Share discovery
Password policy review
Kerberos-aware authentication
WinRM assessment
WMI assessment
MSSQL assessment
SSH assessment
RDP assessment
Module-based enumeration
BloodHound collection
Large-scale internal assessment
```

A useful mental model is:

```text
                   NetExec
                      |
          +-----------+-----------+
          |                       |
          v                       v
       Targets                Credentials
          |                       |
          +-----------+-----------+
                      |
                      v
                   Protocol
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
      SMB            LDAP          WinRM
       |              |              |
       +--------------+--------------+
                      |
                      v
                 Enumeration
                      |
                      v
                  Analysis
```

---

# Authorised Use

Use NetExec only for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Training environments
CTFs
Security research
```

Some NetExec operations can:

```text
Validate credentials across many systems
Perform password spraying
Access remote shares
Enumerate sensitive directory information
Dump credential material
Execute commands
Run modules
Modify remote systems
```

Always confirm the operation is permitted by the rules of engagement.

---

# Installation

## Kali Linux

```bash
sudo apt update
sudo apt install netexec
```

Check:

```bash
which nxc
```

Version:

```bash
nxc --version
```

Help:

```bash
nxc --help
```

---

# pipx Installation

Install prerequisites:

```bash
sudo apt install pipx git
```

Configure pipx:

```bash
pipx ensurepath
```

Install NetExec:

```bash
pipx install git+https://github.com/Pennyw0rth/NetExec
```

Open a new shell afterwards.

Check:

```bash
nxc --version
```

---

# Updating NetExec

For a pipx installation:

```bash
pipx upgrade netexec
```

Force installation from the latest repository state:

```bash
pipx reinstall netexec
```

---

# Tab Completion

Install:

```bash
sudo apt install python3-argcomplete
```

For Bash:

```bash
register-python-argcomplete nxc >> ~/.bashrc
```

Reload:

```bash
source ~/.bashrc
```

For Zsh:

```bash
register-python-argcomplete nxc >> ~/.zshrc
```

Reload:

```bash
source ~/.zshrc
```

---

# NetExec Home Directory

Default:

```text
~/.nxc
```

Inspect:

```bash
ls -la ~/.nxc
```

NetExec stores configuration and operational data under this directory.

---

# Custom NetExec Directory

Set:

```bash
export NXC_PATH="/path/to/netexec-data"
```

Check:

```bash
echo "$NXC_PATH"
```

---

# General Syntax

Basic syntax:

```bash
nxc <protocol> <target>
```

With credentials:

```bash
nxc <protocol> <target> -u <username> -p '<password>'
```

Example:

```bash
nxc smb 10.10.20.10 -u alice -p 'Password'
```

---

# Protocol Help

Check available protocols:

```bash
nxc --help
```

Protocol-specific help:

```bash
nxc smb --help
```

```bash
nxc ldap --help
```

```bash
nxc winrm --help
```

Always use the help output from the installed version when syntax differs from older notes.

---

# Common Protocols

Depending on the installed NetExec version, commonly supported protocols include:

```text
SMB
LDAP
WinRM
WMI
MSSQL
SSH
RDP
FTP
NFS
VNC
```

Check:

```bash
nxc --help
```

for the authoritative list on the installed system.

---

# Target Formats

NetExec can work with individual hosts.

```bash
nxc smb 10.10.20.10
```

Hostname:

```bash
nxc smb dc01.example.local
```

Subnet:

```bash
nxc smb 10.10.20.0/24
```

Multiple targets may also be supplied through supported target input formats.

Check:

```bash
nxc smb --help
```

---

# Environment Variables

Useful assessment variables:

```bash
export DOMAIN="example.local"
export DC="dc01.example.local"
export DC_IP="10.10.20.10"
export USER="alice"
```

Check:

```bash
echo "$DOMAIN"
echo "$DC"
echo "$DC_IP"
echo "$USER"
```

---

# Discovery First

A useful NetExec workflow:

```text
Network
   |
   v
SMB Discovery
   |
   v
Windows Hosts
   |
   v
Domain Information
   |
   v
Security Controls
   |
   v
Credentials
   |
   v
Authenticated Enumeration
```

---

# SMB Discovery

Enumerate SMB systems:

```bash
nxc smb 10.10.20.0/24
```

This can quickly reveal information such as:

```text
IP address
Hostname
Domain/workgroup
Operating system information
SMB signing state
SMB-related host information
```

depending on the target and NetExec version.

---

# Single SMB Host

```bash
nxc smb 10.10.20.10
```

Hostname:

```bash
nxc smb dc01.example.local
```

---

# Save Discovery Output

```bash
nxc smb 10.10.20.0/24 |
    tee smb-discovery.txt
```

---

# SMB Signing

SMB signing is important during NTLM relay analysis.

Use SMB discovery output to identify signing state.

Conceptually:

```text
SMB Host
   |
   v
Signing Required?
   |
 +---+---+
 |       |
Yes      No
 |       |
 v       v
Relay   Potential
Blocked Prerequisite
for SMB
```

Remember:

```text
SMB signing not required
        !=
Successful NTLM relay
```

Other prerequisites still matter.

---

# Password Authentication

General syntax:

```bash
nxc <protocol> <target> -u <username> -p '<password>'
```

Example:

```bash
nxc smb 10.10.20.10 \
    -u alice \
    -p 'Password'
```

---

# Domain Authentication

Specify the domain where appropriate:

```bash
nxc smb 10.10.20.10 \
    -d example.local \
    -u alice \
    -p 'Password'
```

---

# Special Characters

Passwords containing shell-sensitive characters should be quoted:

```bash
nxc smb 10.10.20.10 \
    -u alice \
    -p 'Password!'
```

Prefer single quotes where appropriate.

---

# NTLM Hash Authentication

NetExec commonly uses:

```text
-H
```

for NTLM hash authentication.

Example structure:

```bash
nxc smb 10.10.20.10 \
    -u alice \
    -H <NT-HASH>
```

With domain:

```bash
nxc smb 10.10.20.10 \
    -d example.local \
    -u alice \
    -H <NT-HASH>
```

---

# Password vs Hash

```text
Password
   |
   +--> -p

NTLM Hash
   |
   +--> -H
```

Do not confuse:

```text
-p
```

with:

```text
-H
```

---

# Local Accounts

When assessing local accounts, explicitly distinguish them from domain identities.

Conceptually:

```text
EXAMPLE\administrator
```

is different from:

```text
SERVER01\administrator
```

Check protocol help for the current local-authentication option:

```bash
nxc smb --help
```

---

# Credential Validation

Validate a credential against an approved target:

```bash
nxc smb 10.10.20.10 \
    -d example.local \
    -u alice \
    -p 'Password'
```

Interpret the result carefully.

```text
Authentication Success
        |
        v
Identity Valid
        |
        v
Administrative?
        |
    +---+---+
    |       |
   No      Yes
    |       |
    v       v
Normal   Potential
Access   Admin Access
```

Authentication success does not automatically mean administrative access.

---

# Administrative Access

NetExec can indicate elevated access depending on the protocol and target.

Treat this as:

```text
Potential Administrative Relationship
```

that should be understood and documented.

Do not automatically proceed to remote execution.

---

# Credential Files

NetExec supports credential input from files.

General patterns include:

```bash
nxc <protocol> <target> \
    -u users.txt \
    -p passwords.txt
```

or hash files:

```bash
nxc <protocol> <target> \
    -u users.txt \
    -H hashes.txt
```

!!! warning
    File-based credential testing can generate a large number of authentication attempts. Review lockout policy and rules of engagement before using it.

---

# Password Spraying

NetExec supports password spraying and credential testing.

Before performing any spray:

```text
Password Policy
      |
      v
Lockout Threshold
      |
      v
Observation Window
      |
      v
Current Failed Attempts?
      |
      v
Rules of Engagement
      |
      v
Safe Test Plan
```

Do not blindly spray credentials.

---

# Avoiding Full Cartesian Brute Force

NetExec provides:

```text
--no-bruteforce
```

for supported credential-file workflows where credentials should be paired rather than tested in every combination.

Check:

```bash
nxc <protocol> --help
```

before using it.

---

# Database Credential IDs

NetExec can use credentials stored in its database.

General syntax:

```bash
nxc <protocol> <target> -id <credential-id>
```

Review stored credentials through the NetExec database tooling before using IDs.

---

# SMB Share Enumeration

With valid credentials:

```bash
nxc smb 10.10.20.10 \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares
```

---

# Multiple Hosts - Shares

```bash
nxc smb 10.10.20.0/24 \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares
```

---

# Share Analysis

Prioritise:

```text
SYSVOL
NETLOGON
Administrative shares
Department shares
Deployment shares
Backup shares
Software shares
User shares
```

Look for:

```text
Configuration files
Scripts
Backups
Credentials
Connection strings
Certificates
Keys
Deployment files
Administrative documentation
```

---

# SYSVOL

Enumerate shares:

```bash
nxc smb "$DC" \
    -d "$DOMAIN" \
    -u "$USER" \
    -p 'Password' \
    --shares
```

If SYSVOL is accessible, review it deliberately rather than recursively collecting everything.

Potentially interesting content includes:

```text
Group Policy
Logon scripts
Startup scripts
Configuration
Deployment settings
Legacy preference files
```

---

# NETLOGON

NETLOGON may contain:

```text
Logon scripts
Administrative scripts
Deployment scripts
Configuration
```

Use focused review.

---

# SMB Workflow

```text
SMB Discovery
     |
     v
Authentication
     |
     v
Shares
     |
     v
Permissions
     |
     v
Interesting Share
     |
     v
Focused File Review
```

For interactive file access, move to:

```text
smbclient
```

or:

```text
Impacket smbclient
```

when useful.

---

# LDAP

LDAP is useful for directory-oriented enumeration.

Start with:

```bash
nxc ldap "$DC" \
    -d "$DOMAIN" \
    -u "$USER" \
    -p 'Password'
```

Protocol options:

```bash
nxc ldap --help
```

---

# LDAP Users

Current NetExec versions provide directory enumeration options through the LDAP protocol.

Check:

```bash
nxc ldap --help
```

A commonly used user-enumeration option is:

```text
--users
```

Example:

```bash
nxc ldap "$DC" \
    -d "$DOMAIN" \
    -u "$USER" \
    -p 'Password' \
    --users
```

---

# LDAP Workflow

```text
Valid Domain Credential
        |
        v
LDAP
        |
        +--> Users
        +--> Groups
        +--> Computers
        +--> Policy
        +--> Directory Relationships
        |
        v
Attack Path Analysis
```

---

# Password Policy

Review the domain password and lockout policy before password-based testing.

Check LDAP and SMB help for policy-related options available in the installed version:

```bash
nxc ldap --help
```

```bash
nxc smb --help
```

Record:

```text
Minimum password length
Password history
Maximum password age
Lockout threshold
Lockout duration
Observation window
```

---

# Kerberos

Kerberos-aware operations depend on:

```text
DNS
FQDN
Domain
KDC
Time
SPNs
Credentials
Tickets
```

Before troubleshooting NetExec:

```bash
date
```

```bash
dig "$DC"
```

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

---

# Kerberos Authentication

Check protocol-specific Kerberos options:

```bash
nxc smb --help
```

```bash
nxc ldap --help
```

Do not assume IP-based authentication behaves the same as FQDN-based Kerberos authentication.

Prefer correct hostnames when using Kerberos.

---

# Kerberos Mental Model

```text
Credential / Ticket
        |
        v
DNS
        |
        v
KDC
        |
        v
SPN
        |
        v
Target Service
```

If one component is wrong, authentication can fail even when network connectivity works.

---

# Certificate Authentication

Current NetExec versions support certificate-based authentication for supported workflows.

Available forms include certificate containers and PEM certificate/key combinations.

Check:

```bash
nxc smb --help
```

for the exact options in the installed version.

Certificate authentication can result in NetExec creating a Kerberos credential cache under its home directory.

Treat generated ticket material as sensitive.

---

# WinRM

Check WinRM targets:

```bash
nxc winrm 10.10.20.10
```

With credentials:

```bash
nxc winrm 10.10.20.10 \
    -d example.local \
    -u alice \
    -p 'Password'
```

---

# WinRM Workflow

```text
Host
 |
 v
WinRM Reachable?
 |
 v
Credential Valid?
 |
 v
Remote Management Rights?
 |
 v
Authorised Validation
```

Authentication success does not necessarily mean the identity is permitted to use WinRM.

---

# WMI

Check:

```bash
nxc wmi --help
```

WMI commonly depends on:

```text
RPC
DCOM
Administrative permissions
Firewall configuration
```

A credential that works over SMB may still fail through WMI.

---

# MSSQL

Check:

```bash
nxc mssql --help
```

Typical workflow:

```text
MSSQL Service
     |
     v
Authentication
     |
     v
Database Privilege
     |
     v
Server Role
     |
     v
Security Impact
```

Do not equate successful SQL authentication with operating-system administrative access.

---

# SSH

Check:

```bash
nxc ssh --help
```

Basic structure:

```bash
nxc ssh 10.10.20.20 \
    -u user \
    -p 'Password'
```

Useful when Linux or network systems are part of the internal environment.

---

# RDP

Check:

```bash
nxc rdp --help
```

RDP assessment can help identify whether:

```text
Service reachable
Credential valid
Remote desktop access permitted
```

These are separate questions.

---

# Modules

List modules for a protocol:

```bash
nxc smb -L
```

For another protocol:

```bash
nxc ldap -L
```

---

# Run a Module

General syntax:

```bash
nxc <protocol> <target> \
    -u <username> \
    -p '<password>' \
    -M <module>
```

---

# Module Options

Display options:

```bash
nxc smb \
    -M <module> \
    --options
```

---

# Supply Module Options

General syntax:

```bash
nxc smb <target> \
    -u <username> \
    -p '<password>' \
    -M <module> \
    -o KEY=value
```

---

# Multiple Modules

Current NetExec versions support multiple:

```text
-M
```

arguments.

General structure:

```bash
nxc smb <target> \
    -u <username> \
    -p '<password>' \
    -M <module1> \
    -M <module2>
```

!!! warning
    Review each module before running it. Modules can have very different operational impact.

---

# Module Safety

Before running a module:

```text
Module
  |
  v
What Does It Do?
  |
  v
Read Options
  |
  v
Does It Change State?
  |
  v
Does It Access Credentials?
  |
  v
Does It Execute Code?
  |
  v
Is It Authorised?
```

Do not treat:

```bash
nxc smb -L
```

as a list of modules that should all be executed.

---

# NetExec Database

NetExec maintains operational data in its database.

The database shell is:

```bash
nxcdb
```

Launch:

```bash
nxcdb
```

---

# Workspaces

NetExec supports workspaces.

Conceptually:

```text
Assessment
    |
    v
Workspace
    |
    +--> Hosts
    +--> Credentials
    +--> Protocol data
    +--> Relationships
```

Keep client engagements separated.

---

# NetExec Data Directory

Default:

```text
~/.nxc
```

Typical operational data may include:

```text
Configuration
Workspaces
Databases
Logs
Extracted information
Kerberos material
```

Treat this directory as sensitive.

---

# BloodHound

NetExec can integrate with BloodHound-related collection workflows.

Before using collection functionality:

```text
Check installed NetExec version
Check BloodHound edition
Check collection options
Check DNS
Check LDAP
Check domain context
```

NetExec currently defaults its BloodHound ingestor configuration toward BloodHound CE.

Check:

```bash
cat ~/.nxc/nxc.conf
```

before assuming legacy or CE behaviour.

---

# BloodHound Workflow

```text
NetExec
   |
   v
Authenticated Directory Access
   |
   v
Collection
   |
   v
BloodHound
   |
   v
Attack Path Analysis
```

BloodHound should be used for relationship analysis, not simply as a graph of "things to exploit."

---

# NetExec + Impacket

A strong operational pattern is:

```text
NetExec
   |
   v
Broad Discovery
   |
   +--> Hosts
   +--> Credentials
   +--> Shares
   +--> Admin Relationships
   |
   v
Interesting Target
   |
   v
Impacket
   |
   +--> SMB
   +--> RPC
   +--> Kerberos
   +--> Delegation
   +--> Focused Administration
```

Use:

```text
NetExec = breadth

Impacket = focused protocol operations
```

---

# NetExec + BloodHound

```text
NetExec
   |
   v
Host / Credential Context
   |
   v
BloodHound
   |
   v
Relationship Analysis
   |
   v
Potential Path
   |
   v
Controlled Validation
```

---

# NetExec + Responder

Responder can identify or induce authentication scenarios during authorised internal testing.

NetExec can help identify potential targets and security controls.

```text
NetExec
   |
   v
SMB Signing / Target Analysis
   |
   v
Responder
   |
   v
Authentication Attempt
   |
   v
Relay Analysis
```

Remember:

```text
Capture != Relay
```

and:

```text
Signing not required != successful relay
```

---

# NetExec + Certipy

NetExec can help establish:

```text
Domain
Credentials
Domain Controller
LDAP connectivity
```

before moving to dedicated AD CS tooling.

Conceptually:

```text
NetExec
   |
   v
AD Context
   |
   v
AD CS Present?
   |
   v
Certipy
   |
   v
Certificate Services Analysis
```

---

# NetExec Through a Pivot

Before using NetExec through a pivot:

```bash
ip addr
```

```bash
ip route
```

```bash
cat /etc/resolv.conf
```

Then verify:

```text
Target route
DNS
Protocol ports
Kerberos requirements
```

---

# SOCKS Pivot

Some NetExec operations may be used through a SOCKS-aware environment.

However, protocols such as:

```text
RPC
Kerberos
Dynamic RPC
```

can complicate proxy-based operation.

For broad AD testing, routed or TUN-based pivots can sometimes provide a cleaner network model.

---

# Routed Pivot

Conceptually:

```text
Kali
 |
 v
TUN Interface
 |
 v
Pivot
 |
 v
Internal Network
 |
 v
NetExec
```

From NetExec's perspective, the remote subnet behaves more like a directly routed network.

---

# DNS During Pivoting

A working route does not guarantee working AD tooling.

Verify:

```bash
dig "$DC"
```

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

---

# Re-Enumeration

Whenever your security context changes, run relevant NetExec checks again.

```text
New Credential
      |
      v
Re-Enumerate

New Host
      |
      v
Re-Enumerate

New Privilege
      |
      v
Re-Enumerate

New Subnet
      |
      v
Re-Enumerate

New Domain
      |
      v
Re-Enumerate
```

---

# New Credential Workflow

```text
New Credential
      |
      v
Domain or Local?
      |
      v
Validate Against
Approved Targets
      |
      v
SMB
      |
      +--> Shares
      |
      +--> Admin?
      |
      v
LDAP
      |
      +--> Users
      +--> Groups
      +--> Policy
      |
      v
WinRM / WMI
where appropriate
      |
      v
Update BloodHound
      |
      v
New Relationships
```

---

# New Host Workflow

```text
New Host
   |
   v
SMB
   |
   v
Hostname / Domain
   |
   v
Signing
   |
   v
Known Credentials
   |
   v
Shares
   |
   v
Administrative Access
   |
   v
Remote Management
```

---

# New Subnet Workflow

```text
New Subnet
    |
    v
nxc smb
    |
    v
Windows Hosts
    |
    v
Domains
    |
    v
Signing
    |
    v
Known Credentials
    |
    v
Interesting Systems
```

---

# New Domain Workflow

```text
New Domain
    |
    v
Identify DC
    |
    v
DNS
    |
    v
LDAP
    |
    v
Users / Groups
    |
    v
Password Policy
    |
    v
Trusts
    |
    v
BloodHound
```

---

# Common Troubleshooting

## NetExec Not Found

```bash
which nxc
```

If missing:

```bash
sudo apt install netexec
```

or use the pipx installation.

---

# Check Version

```bash
nxc --version
```

---

# Check Global Help

```bash
nxc --help
```

---

# Check Protocol Help

```bash
nxc smb --help
```

---

# Check Modules

```bash
nxc smb -L
```

---

# Check Module Options

```bash
nxc smb \
    -M <module> \
    --options
```

---

# Authentication Failure

If credentials fail, verify:

```text
Username
Password/hash
Domain
Local vs domain account
Target
Protocol
NTLM/Kerberos
Account status
```

---

# Domain vs Local Account

Always distinguish:

```text
EXAMPLE\alice
```

from:

```text
SERVER01\alice
```

A valid local credential may not work as a domain credential and vice versa.

---

# DNS Failure

Check:

```bash
cat /etc/resolv.conf
```

```bash
dig "$DC"
```

For AD:

```bash
dig SRV "_ldap._tcp.dc._msdcs.$DOMAIN"
```

---

# Kerberos Failure

Check:

```bash
date
```

```bash
dig "$DC"
```

```bash
dig SRV "_kerberos._tcp.$DOMAIN"
```

Then verify:

```text
FQDN
SPN
KDC
Ticket
Domain
```

---

# Authentication Works but No Admin

This is normal.

```text
Valid Credential
      |
      v
Authentication
      |
      v
Authorisation
      |
   +--+--+
   |     |
 User   Admin
```

Do not treat successful authentication as a privilege escalation.

---

# SMB Works but WinRM Fails

Possible reasons include:

```text
WinRM disabled
Firewall
User not permitted for remote management
Different authentication configuration
Network restrictions
```

Do not assume the password is wrong.

---

# SMB Works but WMI Fails

Possible reasons:

```text
Insufficient privileges
RPC blocked
DCOM blocked
Dynamic RPC blocked
Firewall
Endpoint security
```

---

# Too Many Authentication Attempts

Stop.

Review:

```text
Password policy
Lockout threshold
Current test strategy
Credential files
--no-bruteforce
Rules of engagement
```

Do not continue blindly.

---

# Evidence Directory

Create:

```bash
mkdir -p evidence/netexec/{discovery,smb,ldap,winrm,wmi,mssql,ssh,modules}
```

Structure:

```text
evidence/
└── netexec/
    ├── discovery/
    ├── smb/
    ├── ldap/
    ├── winrm/
    ├── wmi/
    ├── mssql/
    ├── ssh/
    └── modules/
```

---

# Save Output

Example:

```bash
nxc smb 10.10.20.0/24 |
    tee evidence/netexec/discovery/smb.txt
```

Shares:

```bash
nxc smb 10.10.20.0/24 \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares |
    tee evidence/netexec/smb/shares.txt
```

---

# Sensitive Evidence

Protect output containing:

```text
Passwords
NTLM hashes
Kerberos tickets
Private keys
Certificates
Credential material
Sensitive filenames
Client information
```

Do not put secrets into screenshots or final reports unnecessarily.

---

# Reporting

Report the security condition rather than the NetExec command.

Avoid:

```text
NetExec showed Pwn3d.
```

Prefer:

```text
The tested domain account possessed local administrative
privileges on APP01.
```

Avoid:

```text
NetExec found SMB signing off.
```

Prefer:

```text
The SMB service on APP01 did not require message signing,
which may satisfy one prerequisite for certain NTLM relay
scenarios.
```

---

# Reporting Share Access

Avoid:

```text
nxc --shares showed READ.
```

Prefer:

```text
The tested domain user could read the Finance share on FILE01.
```

If relevant, explain the exposed data and security impact.

---

# Reporting Credential Validation

Avoid:

```text
NetExec accepted the password.
```

Prefer:

```text
The supplied domain credential successfully authenticated to
the SMB service on the tested system.
```

Then separately document whether administrative access existed.

---

# Detection Perspective

NetExec can generate telemetry across:

```text
Authentication logs
SMB logs
LDAP logs
Kerberos logs
WinRM
WMI
MSSQL
SSH
RDP
Network monitoring
EDR
Domain Controller logs
```

The amount of telemetry depends heavily on the selected protocol and operation.

---

# Purple Team Use

NetExec can be useful for controlled purple team exercises.

```text
Action
  |
  v
Authentication / Enumeration
  |
  v
Host Telemetry
  |
  v
Network Telemetry
  |
  v
Detection?
  |
 +---+---+
 |       |
Yes      No
 |       |
 v       v
Tune    Create
Rule    Detection
```

---

# Low-Impact First

Prefer:

```text
Discovery
    |
    v
Enumeration
    |
    v
Analysis
    |
    v
Focused Validation
```

over:

```text
Credential
    |
    v
Execute Everything
```

---

# Quick SMB Workflow

```bash
nxc smb 10.10.20.0/24
```

Then approved credential validation:

```bash
nxc smb 10.10.20.0/24 \
    -d example.local \
    -u alice \
    -p 'Password'
```

Shares:

```bash
nxc smb 10.10.20.0/24 \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares
```

Then:

```text
Review
   |
   v
Interesting Host?
   |
   v
Focused Enumeration
```

---

# Quick LDAP Workflow

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'
```

Users:

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' \
    --users
```

Then:

```text
Users
  |
  v
Groups
  |
  v
Policy
  |
  v
Relationships
  |
  v
BloodHound
```

---

# Quick WinRM Workflow

```bash
nxc winrm 10.10.20.0/24
```

Then:

```bash
nxc winrm 10.10.20.10 \
    -d example.local \
    -u alice \
    -p 'Password'
```

Interpret:

```text
Reachable
   |
   v
Authenticated
   |
   v
Remote Management Authorised?
```

---

# Quick Hash Workflow

Given an authorised NTLM hash:

```bash
nxc smb 10.10.20.10 \
    -d example.local \
    -u alice \
    -H <NT-HASH>
```

Then determine:

```text
Authentication?
      |
      v
Privilege?
      |
      v
Shares?
      |
      v
Administrative Relationship?
```

---

# What Protocol Do I Need?

```text
What am I testing?
       |
       +--> Windows host discovery
       |       |
       |       +--> SMB
       |
       +--> Active Directory
       |       |
       |       +--> LDAP
       |
       +--> Windows remote management
       |       |
       |       +--> WinRM
       |
       +--> Windows management / WMI
       |       |
       |       +--> WMI
       |
       +--> SQL Server
       |       |
       |       +--> MSSQL
       |
       +--> Linux / Unix SSH
       |       |
       |       +--> SSH
       |
       +--> Remote Desktop
               |
               +--> RDP
```

---

# What Do I Run First?

```text
Internal Network
      |
      v
nxc smb <subnet>
      |
      v
Windows Hosts
      |
      v
Domain?
      |
   +--+--+
   |     |
  No    Yes
   |     |
   |     v
   |   Find DC
   |     |
   |     v
   |   LDAP
   |
   v
Known Credentials?
      |
   +--+--+
   |     |
  No    Yes
   |     |
   v     v
Enum   Validate
Only   Carefully
         |
         v
       Shares
         |
         v
       Access
         |
         v
     BloodHound
```

---

# NetExec Assessment Checklist

## Installation

```text
[ ] NetExec installed
[ ] nxc available
[ ] Version checked
[ ] Protocol help checked
```

## Context

```text
[ ] Scope confirmed
[ ] Interface known
[ ] Routes known
[ ] DNS known
[ ] Domain known
[ ] DC identified
```

## SMB

```text
[ ] SMB hosts discovered
[ ] Hostnames recorded
[ ] Domains recorded
[ ] SMB signing reviewed
[ ] Approved credentials validated
[ ] Shares reviewed
[ ] Administrative relationships recorded
```

## LDAP

```text
[ ] LDAP reachable
[ ] Domain credential validated
[ ] Users reviewed
[ ] Groups reviewed where appropriate
[ ] Password policy reviewed
[ ] Directory relationships analysed
```

## Kerberos

```text
[ ] DNS correct
[ ] Time correct
[ ] FQDN correct
[ ] KDC reachable
[ ] Authentication method understood
```

## Remote Management

```text
[ ] WinRM reviewed
[ ] WMI reviewed where relevant
[ ] Administrative rights confirmed
[ ] Remote execution separately authorised
```

## Modules

```text
[ ] Module purpose understood
[ ] Module options reviewed
[ ] Operational impact understood
[ ] Credential access implications understood
[ ] State changes understood
[ ] Module explicitly authorised
```

## Evidence

```text
[ ] Commands recorded
[ ] Targets recorded
[ ] Identities recorded
[ ] Relevant output saved
[ ] Sensitive material protected
```

---

# One-Minute NetExec Reference

```text
Help
    nxc --help

SMB help
    nxc smb --help

SMB discovery
    nxc smb <target>

Password
    nxc smb <target> -u USER -p 'PASSWORD'

Domain
    nxc smb <target> -d DOMAIN -u USER -p 'PASSWORD'

NTLM hash
    nxc smb <target> -d DOMAIN -u USER -H HASH

Shares
    nxc smb <target> -d DOMAIN -u USER -p 'PASSWORD' --shares

LDAP
    nxc ldap <dc> -d DOMAIN -u USER -p 'PASSWORD'

LDAP users
    nxc ldap <dc> -d DOMAIN -u USER -p 'PASSWORD' --users

WinRM
    nxc winrm <target> -d DOMAIN -u USER -p 'PASSWORD'

Modules
    nxc smb -L

Module options
    nxc smb -M MODULE --options

Run module
    nxc smb <target> -u USER -p 'PASSWORD' -M MODULE

Database
    nxcdb
```

---

# Rules to Remember

```text
Authentication != Administration

Administration != Domain Admin

Pwn3d-style indicator != Permission to Execute Commands

Share Access != Sensitive Data Exposure

SMB Signing Not Required != Successful Relay

Valid Password != Safe to Spray Everywhere

Module Available != Module Appropriate

BloodHound Edge != Confirmed Attack Path

Host Reachable != Host In Scope
```

---

# NetExec vs Impacket

```text
Need broad discovery?
        |
        +--> NetExec

Need credential validation across hosts?
        |
        +--> NetExec

Need share mapping?
        |
        +--> NetExec

Need broad admin relationship mapping?
        |
        +--> NetExec

Need focused SMB interaction?
        |
        +--> Impacket smbclient

Need SID / RPC operations?
        |
        +--> Impacket

Need focused Kerberos operations?
        |
        +--> Impacket

Need ticket conversion?
        |
        +--> Impacket

Need specialised protocol operation?
        |
        +--> Impacket
```

---

# NetExec Mental Model

```text
                      NETEXEC
                         |
                         v
                       SCOPE
                         |
                         v
                       TARGET
                         |
            +------------+------------+
            |            |            |
            v            v            v
           SMB          LDAP        WinRM
            |            |            |
            +------------+------------+
                         |
                         v
                    AUTHENTICATION
                         |
              +----------+----------+
              |                     |
              v                     v
           Password                Hash
              |                     |
              +----------+----------+
                         |
                         v
                    AUTHORISATION
                         |
              +----------+----------+
              |                     |
              v                     v
           Standard               Admin
            Access                Access
              |                     |
              +----------+----------+
                         |
                         v
                     ENUMERATE
                         |
            +------------+------------+
            |            |            |
            v            v            v
          Hosts         Shares      Identity
            |            |            |
            +------------+------------+
                         |
                         v
                       ANALYSE
                         |
                         v
                  NEW RELATIONSHIP
                         |
                         v
                    RE-ENUMERATE
```

---

# Detailed Notes

```text
active-directory/netexec.md
active-directory/impacket.md
active-directory/enumeration.md
active-directory/bloodhound.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/password-spraying.md
active-directory/ntlm-relay.md
active-directory/lateral-movement.md
active-directory/pivoting.md
```

---

# Related Cheatsheets

```text
cheatsheets/active-directory.md
cheatsheets/impacket.md
cheatsheets/networking.md
cheatsheets/windows.md
cheatsheets/powershell.md
```

---

# References

## NetExec Official Website

[NetExec Official Website](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

## NetExec GitHub Repository

[NetExec GitHub Repository](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }

## NetExec Wiki Repository

[NetExec Wiki Repository](https://github.com/Pennyw0rth/NetExec-Wiki){ target="_blank" rel="noopener noreferrer" }

## Installation

[NetExec Wiki - installation on unix](https://www.netexec.wiki/getting-started/installation/installation-on-unix){ target="_blank" rel="noopener noreferrer" }

## Using Credentials

[Using Credentials](https://www.netexec.wiki/getting-started/using-credentials){ target="_blank" rel="noopener noreferrer" }

## Using Modules

[Using Modules](https://www.netexec.wiki/getting-started/using-modules){ target="_blank" rel="noopener noreferrer" }

## Certificate Authentication

[Certificate Authentication](https://www.netexec.wiki/getting-started/using-certificates){ target="_blank" rel="noopener noreferrer" }

---

# Final Quick Reference

```text
                         NETEXEC
                            |
                            v
                        DISCOVERY
                            |
                            v
                     nxc smb <range>
                            |
                            v
                         HOSTS
                            |
                +-----------+-----------+
                |                       |
                v                       v
               SMB                    LDAP
                |                       |
                v                       v
             Shares                  Users
                |                    Groups
                |                    Policy
                |                       |
                +-----------+-----------+
                            |
                            v
                       CREDENTIAL
                            |
                +-----------+-----------+
                |                       |
                v                       v
             Password                  Hash
                |                       |
                +-----------+-----------+
                            |
                            v
                      AUTHENTICATION
                            |
                            v
                       AUTHORISATION
                            |
                +-----------+-----------+
                |                       |
                v                       v
              User                    Admin
                |                       |
                +-----------+-----------+
                            |
                            v
                         ANALYSE
                            |
                            v
                    NEW RELATIONSHIP
                            |
                            v
                      RE-ENUMERATE
                            |
                            v
                         EVIDENCE
```

The key principle is:

```text
NetExec gives breadth.

Use it to map hosts, identities, access, and relationships.

Then move to focused tools when deeper protocol-specific analysis is required.
```
