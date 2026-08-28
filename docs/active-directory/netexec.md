# NetExec

NetExec, commonly invoked as `nxc`, is a network service assessment tool widely used during authorised internal penetration tests and Active Directory security assessments.

It is the community-maintained successor to CrackMapExec and provides a consistent interface for interacting with multiple network protocols.

NetExec is particularly useful for answering questions such as:

```text
Which Windows systems are reachable?

Which hosts expose SMB?

What domain does each host belong to?

Is SMB signing required?

Do the supplied credentials authenticate?

Where does an account have administrative access?

Which SMB shares can the account access?

Which users and groups exist?

Which Domain Controllers exist?

What LDAP information can be queried?

Which systems expose WinRM?

Which SQL servers are reachable?

Which systems expose SSH or RDP?

What relationships should be investigated next?
```

NetExec should not be treated simply as:

```text
Password
   |
   v
Spray entire network
```

A better model is:

```text
Discover
   |
   v
Enumerate
   |
   v
Authenticate
   |
   v
Authorise
   |
   v
Map Access
   |
   v
Analyse
   |
   v
Validate
```

---

# Authorised Testing

The commands in this note are intended for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Training laboratories
CTFs
Security research
```

NetExec can generate significant authentication and network telemetry.

Before using functionality involving:

```text
Credential testing
Password spraying
NTLM hashes
Remote execution
Credential extraction
SAM / LSA access
DPAPI
Modules
Large network ranges
```

confirm that the activity is permitted by the rules of engagement.

---

# NetExec in the AD Workflow

NetExec fits naturally into the Active Directory assessment workflow.

```text
Initial Network Access
        |
        v
Network Discovery
        |
        v
NetExec SMB
        |
        +--> Hostnames
        +--> Domains
        +--> Operating Systems
        +--> SMB Signing
        |
        v
Credentials Available?
        |
    +---+---+
    |       |
   No      Yes
    |       |
    v       v
Continue   Validate
Discovery  Authentication
            |
            v
       Enumerate Access
            |
       +----+----+
       |         |
       v         v
     LDAP       SMB
       |         |
       v         v
 Directory     Shares
       |         |
       +----+----+
            |
            v
      Access Mapping
            |
            v
       BloodHound
            |
            v
      Attack Paths
```

---

# Installation

## Kali Linux

NetExec is available through Kali's package repositories.

```bash
sudo apt update
sudo apt install netexec
```

Verify:

```bash
nxc --help
```

Check the installed binary:

```bash
which nxc
```

Version:

```bash
nxc --version
```

---

# Install Using pipx

The NetExec project recommends `pipx` for Unix-like systems when installing directly from the upstream repository.

Install dependencies:

```bash
sudo apt install pipx git
```

Ensure the pipx binary directory is available:

```bash
pipx ensurepath
```

Install NetExec:

```bash
pipx install git+https://github.com/Pennyw0rth/NetExec
```

Open a new terminal and verify:

```bash
nxc --help
```

---

# Updating a pipx Installation

Update:

```bash
pipx upgrade netexec
```

Force reinstall from the current upstream source:

```bash
pipx reinstall netexec
```

---

# Keep NetExec Updated

NetExec changes frequently.

This matters because:

```text
Protocols change
Modules change
CLI options change
Dependencies change
Bugs are fixed
Security issues are fixed
```

Before relying on remembered syntax:

```bash
nxc --help
```

and:

```bash
nxc <protocol> --help
```

For example:

```bash
nxc smb --help
```

---

# NetExec Home Directory

By default NetExec stores its configuration and operational data under:

```text
~/.nxc
```

Inspect:

```bash
ls -la ~/.nxc
```

Workspaces are normally stored under:

```text
~/.nxc/workspaces
```

The location can be changed using the `NXC_PATH` environment variable.

Example:

```bash
export NXC_PATH="$HOME/.nxc"
```

---

# Tab Completion

NetExec supports shell completion through `argcomplete`.

Install:

```bash
sudo apt install python3-argcomplete
```

Bash:

```bash
register-python-argcomplete nxc >> ~/.bashrc
```

Zsh:

```bash
register-python-argcomplete nxc >> ~/.zshrc
```

Reload the shell.

Bash:

```bash
source ~/.bashrc
```

Zsh:

```bash
source ~/.zshrc
```

---

# Basic Syntax

The general pattern is:

```bash
nxc <protocol> <target> [options]
```

Example:

```bash
nxc smb 10.10.20.10
```

A subnet:

```bash
nxc smb 10.10.20.0/24
```

A hostname:

```bash
nxc smb file01.example.local
```

A list of targets:

```bash
nxc smb targets.txt
```

---

# Protocol Discovery

Start with:

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

```bash
nxc mssql --help
```

```bash
nxc ssh --help
```

Do not assume that every protocol supports the same options.

---

# Common Protocols

Depending on the installed version, NetExec supports multiple protocols.

Common protocols relevant to internal assessments include:

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

Think of NetExec as:

```text
                 NetExec
                    |
       +------------+------------+
       |            |            |
       v            v            v
      SMB          LDAP        WinRM
       |            |            |
       v            v            v
 Windows        Directory      Remote
 Systems          Data        Management
       |
       +------------+------------+
       |            |            |
       v            v            v
     MSSQL         SSH          RDP
```

---

# Target Formats

A single IP:

```bash
nxc smb 10.10.20.10
```

CIDR:

```bash
nxc smb 10.10.20.0/24
```

Hostname:

```bash
nxc smb file01.example.local
```

Multiple targets from a file:

```bash
nxc smb targets.txt
```

---

# Build a Target File

Example:

```text
10.10.20.10
10.10.20.11
10.10.20.20
10.10.20.30
```

Save as:

```text
targets.txt
```

Then:

```bash
nxc smb targets.txt
```

This is often preferable to repeatedly scanning an entire subnet.

---

# SMB Discovery

One of the most useful first NetExec commands is:

```bash
nxc smb 10.10.20.0/24
```

Depending on the environment and NetExec version, output may reveal information such as:

```text
IP address
Hostname
Domain
Operating system information
SMB signing configuration
SMB-related metadata
```

---

# Save SMB Discovery

```bash
nxc smb 10.10.20.0/24 |
    tee smb-discovery.txt
```

For structured engagement evidence:

```bash
mkdir -p evidence/netexec
```

Then:

```bash
nxc smb 10.10.20.0/24 |
    tee evidence/netexec/smb-discovery.txt
```

---

# SMB Signing

SMB discovery is particularly useful when reviewing SMB signing.

Record:

| Host | Role | Signing |
|---|---|---|
| DC01 | Domain Controller | Required |
| FILE01 | File Server | Review |
| APP01 | Application Server | Review |

Do not interpret:

```text
Signing not required
```

as:

```text
Host compromised
```

The correct model is:

```text
SMB Signing Configuration
          |
          v
Potential Relay Prerequisite
          |
          v
Additional Conditions Required
          |
          v
Controlled Validation
```

---

# Authentication

NetExec can validate credentials against supported services.

The important distinction is:

```text
Authentication
```

versus:

```text
Authorisation
```

A credential may successfully authenticate without having administrative access.

---

# Domain Password Authentication

Example:

```bash
nxc smb file01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'
```

---

# Authentication Against a Subnet

Where explicitly authorised:

```bash
nxc smb 10.10.20.0/24 \
    -d example.local \
    -u alice \
    -p 'Password'
```

Use network-wide credential validation deliberately.

A better workflow is often:

```text
Identify Hosts
      |
      v
Reduce Target Set
      |
      v
Validate Credential
      |
      v
Map Access
```

rather than testing every available service indiscriminately.

---

# Avoid Passwords in Shell History

Commands such as:

```bash
nxc smb 10.10.20.10 \
    -u alice \
    -p 'ActualPassword'
```

may expose the credential through:

```text
Shell history
Process listings
Terminal logging
Screenshots
Screen recordings
Evidence files
```

Use secure credential-handling practices appropriate to the engagement.

---

# NTLM Hash Authentication

Where authorised, NetExec supports NTLM hash authentication for applicable protocols.

Example:

```bash
nxc smb file01.example.local \
    -d example.local \
    -u alice \
    -H '<NT-HASH>'
```

This is commonly described as:

```text
Pass-the-Hash
```

The dedicated Pass-the-Hash note should cover the technique in detail.

---

# Local Accounts

Domain and local authentication must be distinguished.

Conceptually:

```text
EXAMPLE\alice
```

is different from:

```text
FILE01\alice
```

Do not assume an account with the same username on multiple machines represents the same security principal.

Check the current SMB help for local-authentication options:

```bash
nxc smb --help
```

---

# Authentication Interpretation

Think in stages:

```text
Target Reachable
      |
      v
Service Available
      |
      v
Credential Accepted
      |
      v
Identity Established
      |
      v
Authorisation Evaluated
      |
      v
Accessible Resources
```

Never collapse all of these into:

```text
Credential works = compromised
```

---

# Administrative Access

NetExec can help determine whether the supplied account has administrative privileges over a target.

The exact output formatting can vary between versions.

Treat an administrative indicator as:

```text
Account
   |
   v
Administrative Access
   |
   v
Specific Host
```

not:

```text
Account
   |
   v
Domain Admin
```

---

# Mapping Administrative Access

Example workflow:

```bash
nxc smb targets.txt \
    -d example.local \
    -u alice \
    -p 'Password'
```

Record:

| Host | Authentication | Administrative Access |
|---|---|---|
| DC01 | Yes | No |
| FILE01 | Yes | Yes |
| APP01 | Yes | No |
| WEB01 | Yes | Yes |

This creates an access graph:

```text
alice
 |
 +--> FILE01
 |
 +--> WEB01
```

---

# SMB Share Enumeration

Enumerate shares:

```bash
nxc smb file01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares
```

---

# What to Record

For each share:

```text
Share name
Read access
Write access
Purpose
Sensitive content
Business function
```

Example:

| Share | Read | Write | Notes |
|---|---:|---:|---|
| Public | Yes | No | General documents |
| Deploy | Yes | Yes | Deployment files |
| Backups | Yes | No | Backup data |
| Software | Yes | Yes | Software deployment |

---

# Interesting Shares

Look for names such as:

```text
Backup
Backups
Deploy
Deployment
Install
Installer
Software
Scripts
Admin
IT
Users
Profiles
Home
Finance
HR
Development
Dev
Projects
SYSVOL
NETLOGON
```

Names alone do not imply sensitive content.

---

# Share Analysis

The key relationship is:

```text
Identity
   |
   v
Share Permission
   |
   v
File Permission
   |
   v
Content
   |
   v
How Content Is Used
```

A writable share becomes more interesting if privileged systems automatically execute or consume its contents.

---

# SMB Share Workflow

```text
Discover SMB Hosts
        |
        v
Authenticate
        |
        v
Enumerate Shares
        |
        v
Identify Readable Shares
        |
        v
Identify Writable Shares
        |
        v
Review Relevant Content
        |
        v
Understand Consumption
        |
        v
Determine Security Impact
```

---

# SYSVOL

Domain users commonly have legitimate read access to SYSVOL.

Enumerate shares:

```bash
nxc smb dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares
```

SYSVOL may contain:

```text
Group Policy
Scripts
Configuration
Deployment information
Historical artefacts
```

---

# NETLOGON

NETLOGON may contain:

```text
Logon scripts
Batch files
PowerShell scripts
Configuration
Internal server references
Deployment logic
```

Review it as part of the domain configuration rather than assuming sensitive information will necessarily exist.

---

# LDAP

LDAP is one of the most important NetExec protocols during Active Directory assessments.

Basic connection:

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'
```

---

# LDAP Against the DC IP

```bash
nxc ldap 10.10.20.10 \
    -d example.local \
    -u alice \
    -p 'Password'
```

For Kerberos-oriented workflows, correct DNS and hostname resolution are generally preferable to relying entirely on IP addresses.

---

# Enumerate Users

Current NetExec versions provide LDAP user enumeration options.

Check:

```bash
nxc ldap --help
```

A commonly available form is:

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' \
    --users
```

---

# Active Users

Some current NetExec versions also provide filtering for active users.

Always verify:

```bash
nxc ldap --help
```

before documenting results from a remembered option.

---

# Why LDAP Enumeration Matters

LDAP can help answer:

```text
Who exists?

Which users are active?

Which groups exist?

Which computers exist?

Which accounts have SPNs?

Which delegation relationships exist?

Which privileged identities exist?
```

---

# Domain Controllers

LDAP and SMB discovery can help identify Domain Controllers.

Always corroborate with:

```text
DNS SRV records
LDAP
SMB metadata
Kerberos
```

rather than relying on one tool result.

---

# Password Policy

Before performing any password-based testing, determine:

```text
Lockout threshold
Lockout duration
Observation window
Password requirements
Fine-grained password policies
```

Check available protocol options:

```bash
nxc smb --help
```

```bash
nxc ldap --help
```

Do not perform password spraying based solely on a discovered user list.

---

# Password Spraying

NetExec can perform credential testing across multiple users and hosts.

Because this can:

```text
Lock accounts
Trigger monitoring
Impact users
Generate large authentication volumes
```

it should only be performed when explicitly permitted.

The dedicated `password-spraying.md` note should contain the operational methodology.

Use this page primarily to remember:

```text
ENUMERATE POLICY FIRST
```

---

# Kerberos

NetExec supports Kerberos-aware workflows for appropriate protocols.

Before using Kerberos:

```text
DNS must be correct
Hostname resolution must work
Domain must be correct
Clock skew must be acceptable
SPNs must match
```

Check protocol-specific options:

```bash
nxc smb --help
```

or:

```bash
nxc ldap --help
```

---

# Kerberos Troubleshooting

When Kerberos unexpectedly fails, check:

```bash
date
```

DNS:

```bash
dig dc01.example.local
```

Kerberos SRV records:

```bash
dig SRV _kerberos._tcp.example.local
```

Then confirm:

```text
Username
Domain
Hostname
DC
Time
DNS
```

---

# WinRM

WinRM is commonly exposed on:

```text
5985/tcp
5986/tcp
```

Basic discovery:

```bash
nxc winrm 10.10.20.20
```

Credential validation:

```bash
nxc winrm 10.10.20.20 \
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
 +-- No --> Continue
 |
 +-- Yes
       |
       v
Credential Valid?
       |
       v
Authorised for Remote Management?
       |
       v
Potential Lateral Movement Path
```

Remote execution should be treated as a separate, more intrusive validation step.

---

# MSSQL

NetExec can assess Microsoft SQL Server environments.

Basic discovery:

```bash
nxc mssql 10.10.20.30
```

Authentication:

```bash
nxc mssql sql01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'
```

Check:

```bash
nxc mssql --help
```

for current authentication and enumeration options.

---

# Why MSSQL Matters in AD

SQL Server environments may involve:

```text
Domain service accounts
Privileged service identities
Linked servers
Windows authentication
Delegation
Database-level privilege
Operating-system-level privilege
```

Therefore:

```text
SQL Access
   |
   v
Database Context
   |
   v
Service Identity
   |
   v
AD Relationship
```

may create an attack path.

---

# SSH

Where SSH is used internally:

```bash
nxc ssh 10.10.20.40
```

Credential validation:

```bash
nxc ssh 10.10.20.40 \
    -u alice \
    -p 'Password'
```

SSH may be relevant for:

```text
Linux servers
Network appliances
Administrative infrastructure
Mixed Windows/Linux environments
```

---

# RDP

Check current RDP functionality:

```bash
nxc rdp --help
```

RDP-related assessment can help determine whether remote interactive access is available to an identity.

Remember:

```text
3389 open
    !=
User allowed to RDP
```

---

# WMI

Current NetExec versions may expose WMI as its own protocol.

Check:

```bash
nxc wmi --help
```

WMI is particularly relevant for:

```text
Remote administration
System information
Lateral movement
Administrative validation
```

Remote execution is more intrusive than simple enumeration and should be separated in the testing methodology.

---

# Modules

NetExec includes modules that extend protocol functionality.

List modules for a protocol:

```bash
nxc smb -L
```

LDAP:

```bash
nxc ldap -L
```

---

# Run a Module

General syntax:

```bash
nxc <protocol> <target> \
    -u <user> \
    -p <password> \
    -M <module>
```

---

# Module Help

Inspect module options:

```bash
nxc smb -M <module> --options
```

Example workflow:

```text
Find Module
    |
    v
Read Description
    |
    v
Read Options
    |
    v
Understand Actions
    |
    v
Confirm Authorisation
    |
    v
Run
```

---

# Module Options

Module parameters use:

```text
KEY=value
```

with the `-o` option.

General form:

```bash
nxc smb <target> \
    -u <user> \
    -p <password> \
    -M <module> \
    -o KEY=value
```

---

# Multiple Modules

Current NetExec supports specifying multiple modules using multiple `-M` options.

Conceptually:

```bash
nxc smb <target> \
    -u <user> \
    -p <password> \
    -M <module1> \
    -M <module2>
```

Do not run multiple modules simply because the feature exists.

Each module may create different:

```text
Network traffic
Host artefacts
Authentication events
EDR telemetry
Operational impact
```

---

# Module Safety

Before running a module, ask:

```text
What protocol does it use?

Does it require administrator access?

Does it execute code?

Does it write files?

Does it dump credentials?

Does it change configuration?

Does it start a service?

Does it create a scheduled task?

Does it touch LSASS?

What evidence will it leave?
```

---

# NetExec Database

NetExec automatically stores discovered information in its database.

This may include:

```text
Hosts
Credentials
Shares
Groups
Protocol-specific information
```

depending on what was collected.

---

# nxcdb

Launch:

```bash
nxcdb
```

Typical prompt:

```text
nxcdb (default) >
```

Help:

```text
help
```

---

# Workspaces

Workspaces allow separate engagements to be isolated.

Conceptually:

```text
NetExec
   |
   +--> client-a
   |
   +--> client-b
   |
   +--> lab
```

This is important because assessment data can include sensitive:

```text
Hostnames
Usernames
Credentials
Hashes
Share information
```

Never mix client data unnecessarily.

---

# Workspace Storage

By default:

```text
~/.nxc/workspaces
```

Inspect:

```bash
find ~/.nxc/workspaces -maxdepth 2 -type f
```

Treat the directory as sensitive evidence.

---

# NetExec Database Security

The NetExec database may contain sensitive material.

Protect:

```text
~/.nxc
```

using appropriate:

```text
Filesystem permissions
Disk encryption
Evidence handling
Engagement separation
Secure deletion procedures
```

---

# BloodHound Integration

NetExec has BloodHound-related integration capabilities.

The current default configuration is oriented toward BloodHound Community Edition.

Configuration is stored in:

```text
~/.nxc/nxc.conf
```

Inspect:

```bash
cat ~/.nxc/nxc.conf
```

Do not modify BloodHound-related settings without understanding whether the engagement uses:

```text
BloodHound CE
```

or:

```text
Legacy BloodHound
```

---

# NetExec and BloodHound

Use NetExec and BloodHound together rather than treating them as competing tools.

```text
NetExec
   |
   +--> Host Discovery
   +--> Authentication
   +--> Shares
   +--> Protocol Access
   |
   v
Operational View

BloodHound
   |
   +--> Identity Relationships
   +--> ACL Relationships
   +--> Administrative Paths
   +--> Group Relationships
   |
   v
Graph View
```

Together:

```text
Operational Access
        +
Identity Relationships
        |
        v
Better Attack Path Analysis
```

---

# Audit Mode

Current NetExec documentation includes an audit mode.

Before using it, review:

```bash
nxc --help
```

and the current official documentation.

Audit-oriented operation can be useful when the objective is:

```text
Security assessment
Configuration review
Exposure mapping
```

rather than exploitation.

---

# Logging Output

Save relevant output:

```bash
nxc smb 10.10.20.0/24 |
    tee evidence/netexec/smb.txt
```

LDAP:

```bash
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' |
    tee evidence/netexec/ldap.txt
```

Shares:

```bash
nxc smb file01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares |
    tee evidence/netexec/file01-shares.txt
```

---

# Suggested Evidence Structure

```text
evidence/
└── netexec/
    ├── discovery/
    ├── smb/
    ├── ldap/
    ├── winrm/
    ├── mssql/
    ├── shares/
    ├── authentication/
    └── modules/
```

---

# Naming Output Files

Examples:

```text
smb-discovery.txt
dc01-ldap.txt
file01-shares.txt
alice-access.txt
winrm-hosts.txt
mssql-hosts.txt
smb-signing.txt
```

---

# Credential Validation Workflow

A controlled credential-validation workflow is:

```text
Credential Obtained
        |
        v
Identify Account Type
        |
        +--> Domain
        +--> Local
        +--> Service
        |
        v
Choose Relevant Protocol
        |
        v
Choose Small Target Set
        |
        v
Authenticate
        |
        v
Record Success
        |
        v
Determine Privilege
        |
        v
Expand Only If Needed
```

---

# New Credential Checklist

When a new credential is obtained:

```text
[ ] Identify domain
[ ] Identify username
[ ] Determine account type
[ ] Determine group memberships
[ ] Validate against appropriate service
[ ] Check LDAP visibility
[ ] Check SMB access
[ ] Check shares
[ ] Check administrative relationships
[ ] Check WinRM where relevant
[ ] Check MSSQL where relevant
[ ] Update BloodHound analysis
```

---

# Host Discovery Workflow

```text
Subnet
  |
  v
nxc smb
  |
  +--> Windows Hosts
  |
  +--> Hostnames
  |
  +--> Domains
  |
  +--> SMB Signing
  |
  v
Create Target Lists
```

Example:

```bash
nxc smb 10.10.20.0/24 |
    tee smb-discovery.txt
```

Then build:

```text
domain-controllers.txt
servers.txt
workstations.txt
interesting-hosts.txt
```

---

# Protocol Matrix

Maintain a simple matrix:

| Host | SMB | LDAP | WinRM | MSSQL | SSH | RDP |
|---|---|---|---|---|---|---|
| DC01 | Yes | Yes | Yes | No | No | Yes |
| FILE01 | Yes | No | Yes | No | No | Yes |
| SQL01 | Yes | No | Yes | Yes | No | Yes |
| LINUX01 | No | No | No | No | Yes | No |

This helps avoid repeatedly probing services that are already understood.

---

# Access Matrix

Track credentials separately:

| Identity | Host | Protocol | Auth | Admin |
|---|---|---|---|---|
| alice | FILE01 | SMB | Yes | No |
| alice | APP01 | SMB | Yes | Yes |
| svc_sql | SQL01 | MSSQL | Yes | Review |

This becomes especially useful after multiple credentials are discovered.

---

# NetExec During Lateral Movement

NetExec can help answer:

```text
Where can this identity authenticate?

Where is this identity privileged?

Which remote-management protocol is available?

What is the next useful host?
```

The workflow should be:

```text
Credential
   |
   v
Access Mapping
   |
   v
Candidate Host
   |
   v
Business / Security Context
   |
   v
Controlled Validation
   |
   v
New Host
```

not:

```text
Credential
   |
   v
Execute Everywhere
```

---

# Re-Enumerate After New Access

After obtaining access to a new host:

```text
New Host
   |
   v
Local Identity
   |
   v
Interfaces
   |
   v
Routes
   |
   v
DNS
   |
   v
Connections
   |
   v
New Networks
   |
   v
NetExec Against New Segment
```

NetExec becomes particularly useful after pivoting because the same assessment workflow can be repeated against a newly reachable network.

---

# NetExec Through a Pivot

Conceptually:

```text
Kali
 |
 v
Pivot
 |
 v
Internal Segment
 |
 v
NetExec
```

The exact configuration depends on the pivot technology.

Examples include:

```text
Ligolo-ng
SSH tunnels
SOCKS proxies
Chisel
```

Not every protocol or operation behaves identically through every type of proxy.

For broad internal assessment work, a routed/TUN-style pivot can often be easier than forcing all traffic through application-level SOCKS.

See:

```text
active-directory/pivoting.md
```

---

# DNS Through a Pivot

Remember:

```text
Network route works
        !=
DNS works
```

NetExec operations involving:

```text
LDAP
Kerberos
Domain Controllers
Hostnames
SPNs
```

may depend on correct internal DNS resolution.

Always document:

```text
Internal DNS server
Domain
Domain Controller FQDN
Reachability
Name resolution
```

---

# Kerberos Through a Pivot

Kerberos is particularly sensitive to:

```text
DNS
Hostnames
SPNs
Time
Routing
```

A working TCP route to the Domain Controller does not guarantee that Kerberos-based tooling will work correctly.

---

# NetExec and Responder

NetExec and Responder have different roles.

```text
Responder
    |
    v
Authentication / Name Resolution Analysis

NetExec
    |
    v
Service and Access Assessment
```

Potential workflow:

```text
Authentication Material
        |
        v
Understand Identity
        |
        v
NetExec Validation
        |
        v
Map Authorised Access
```

Credential capture and relay require their own rules-of-engagement checks.

---

# NetExec and Impacket

NetExec and Impacket complement each other.

```text
NetExec
   |
   +--> Broad Assessment
   +--> Multiple Hosts
   +--> Access Mapping
   +--> Protocol Enumeration

Impacket
   |
   +--> Focused Protocol Operations
   +--> Kerberos Workflows
   +--> SMB / RPC Operations
   +--> Specific AD Techniques
```

Example methodology:

```text
NetExec
   |
   v
Find Interesting Relationship
   |
   v
Impacket
   |
   v
Focused Validation
```

---

# NetExec and PowerView

PowerView is useful from a Windows/domain context for directory-focused enumeration.

NetExec is useful from the assessment system for network/protocol-focused enumeration.

```text
PowerView
   |
   v
Directory Relationships

NetExec
   |
   v
Network Relationships
```

Combine both perspectives.

---

# NetExec and Certipy

NetExec can identify domain infrastructure and authenticated LDAP access.

Certipy can then perform focused AD CS enumeration.

```text
NetExec
   |
   v
Domain / DC / Credentials
   |
   v
Certipy
   |
   v
CA / Template Analysis
```

---

# Common Mistake - Scanning Everything

Avoid:

```bash
nxc smb 10.0.0.0/8 ...
```

without a clear reason.

Instead:

```text
Understand Scope
      |
      v
Identify Subnets
      |
      v
Discover Services
      |
      v
Build Target Lists
      |
      v
Run Focused Checks
```

---

# Common Mistake - Credential Spray by Default

Do not treat NetExec as:

```text
user.txt + password.txt + /16
```

Credential testing can have operational consequences.

Determine:

```text
Lockout policy
Scope
Permitted accounts
Permitted attempts
Monitoring expectations
Timing
```

first.

---

# Common Mistake - Confusing Authentication and Administration

This is one of the most important NetExec interpretation mistakes.

```text
[+] Authentication
```

does not necessarily mean:

```text
Local Administrator
```

and local administrator does not mean:

```text
Domain Administrator
```

---

# Common Mistake - Running Modules Blindly

Do not:

```text
See interesting module
        |
        v
Run it
```

Instead:

```text
Read Module
    |
    v
Understand Actions
    |
    v
Understand Privileges
    |
    v
Understand Artefacts
    |
    v
Confirm Scope
    |
    v
Run if Needed
```

---

# Common Mistake - Ignoring NetExec's Database

Repeated assessments can become confusing if you ignore stored state.

Know where NetExec stores:

```text
Workspaces
Hosts
Credentials
Shares
Configuration
```

and keep client engagements separated.

---

# Common Mistake - Stale NetExec Installation

NetExec evolves quickly.

If a command from documentation does not work:

```bash
nxc --version
```

Then:

```bash
nxc <protocol> --help
```

Compare against the current official documentation.

Do not assume the syntax in an old CrackMapExec write-up applies unchanged.

---

# Common Mistake - Calling It CrackMapExec

Older material frequently uses:

```text
crackmapexec
cme
```

Current NetExec uses:

```text
NetExec
nxc
```

When translating older notes:

```text
Old CME workflow
      |
      v
Check Current NetExec Documentation
      |
      v
Confirm Current Option
```

Do not mechanically replace `crackmapexec` with `nxc` and assume every option is identical.

---

# Troubleshooting

## Command Not Found

Check:

```bash
which nxc
```

If installed with pipx:

```bash
pipx list
```

Then:

```bash
pipx ensurepath
```

Open a new terminal.

---

# Check Installation

```bash
nxc --version
```

```bash
nxc --help
```

---

# Check Protocol

```bash
nxc smb --help
```

---

# DNS Problems

Check:

```bash
cat /etc/resolv.conf
```

Then:

```bash
dig example.local
```

DC:

```bash
dig dc01.example.local
```

SRV:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

# Kerberos Problems

Check:

```bash
date
```

Then:

```text
Domain
Username
DNS
FQDN
DC
Clock
SPN
```

---

# Authentication Problems

Verify whether the credential is:

```text
DOMAIN\User

or

HOST\User
```

Then determine whether the target expects:

```text
Domain authentication
Local authentication
Kerberos
NTLM
Certificate authentication
```

---

# Target Resolution

If:

```bash
nxc smb file01.example.local
```

fails but:

```bash
nxc smb 10.10.20.20
```

works, investigate DNS before continuing.

Do not permanently work around broken DNS with IP addresses if Kerberos testing is required later.

---

# Operational Noise

NetExec can generate:

```text
SMB connections
LDAP queries
Authentication attempts
RPC activity
Remote-management traffic
Service interactions
```

Depending on the selected options and modules, telemetry can increase significantly.

Use the least intrusive command that answers the assessment question.

---

# Detection Perspective

Defenders may observe:

```text
Authentication events
Failed logons
SMB connections
LDAP query patterns
Remote service access
WinRM activity
WMI activity
Network connections from unusual systems
Repeated connections across many hosts
```

This makes NetExec useful during purple team exercises as well.

---

# Purple Team Use

A useful purple team exercise can compare:

```text
Action
   |
   v
Expected Telemetry
   |
   v
Observed Telemetry
   |
   v
Detection?
   |
   +--> Yes --> Validate Quality
   |
   +--> No --> Detection Gap
```

Example activities:

```text
SMB discovery
LDAP enumeration
Share enumeration
Credential validation
WinRM access
```

---

# Evidence to Capture

For each meaningful NetExec finding record:

```text
Date/time
Source system
Target
Protocol
Identity
Command category
Result
Privilege level
Security relevance
```

Avoid storing plaintext credentials in screenshots or report evidence.

---

# Reporting Authentication Results

Instead of:

```text
NetExec showed [+].
```

write:

```text
The supplied domain account successfully authenticated to the SMB
service on FILE01.
```

If administrative access was confirmed:

```text
The account possessed local administrative privileges on FILE01.
```

This describes the security condition rather than the tool output.

---

# Reporting SMB Signing

Avoid:

```text
NetExec says signing False.
```

Prefer:

```text
SMB message signing was not required by the tested server.
```

Then explain the relevance and prerequisites for any relay-related risk separately.

---

# Reporting Share Access

Avoid:

```text
--shares found Deploy.
```

Prefer:

```text
The tested domain account had write access to the Deploy SMB share
on FILE01.
```

Then determine how that share is used before assigning impact.

---

# Reporting Access Relationships

Example:

```text
The standard domain account alice possessed local administrative
access to APP01 through SMB-accessible administrative interfaces.
```

Then document:

```text
Source identity
Target
Privilege
Validation
Potential impact
```

---

# Remediation Themes

NetExec findings frequently lead to remediation involving:

```text
Least privilege
Local administrator management
Credential hygiene
SMB signing
Network segmentation
Remote management restrictions
Share permissions
Service account privilege
LDAP protections
Authentication hardening
Password policy
Tiering
Monitoring
```

The recommendation should address the underlying security condition rather than NetExec itself.

---

# Quick Reference - Discovery

```bash
# SMB host discovery
nxc smb 10.10.20.0/24

# Save output
nxc smb 10.10.20.0/24 |
    tee smb-discovery.txt

# Single host
nxc smb 10.10.20.10

# Target list
nxc smb targets.txt
```

---

# Quick Reference - Authentication

```bash
# Domain credential
nxc smb file01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'

# NTLM hash
nxc smb file01.example.local \
    -d example.local \
    -u alice \
    -H '<NT-HASH>'
```

---

# Quick Reference - Shares

```bash
nxc smb file01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' \
    --shares
```

---

# Quick Reference - LDAP

```bash
# Authentication / basic LDAP access
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'

# Users
nxc ldap dc01.example.local \
    -d example.local \
    -u alice \
    -p 'Password' \
    --users
```

Always verify current LDAP options:

```bash
nxc ldap --help
```

---

# Quick Reference - WinRM

```bash
# Discovery
nxc winrm 10.10.20.20

# Authentication
nxc winrm 10.10.20.20 \
    -d example.local \
    -u alice \
    -p 'Password'
```

---

# Quick Reference - MSSQL

```bash
# Discovery
nxc mssql 10.10.20.30

# Authentication
nxc mssql sql01.example.local \
    -d example.local \
    -u alice \
    -p 'Password'
```

---

# Quick Reference - Modules

```bash
# List SMB modules
nxc smb -L

# Module options
nxc smb -M <module> --options

# Run module
nxc smb <target> \
    -u <user> \
    -p <password> \
    -M <module>

# Module options
nxc smb <target> \
    -u <user> \
    -p <password> \
    -M <module> \
    -o KEY=value
```

---

# Quick Reference - Database

```bash
nxcdb
```

NetExec home:

```bash
ls -la ~/.nxc
```

Workspaces:

```bash
ls -la ~/.nxc/workspaces
```

Configuration:

```bash
cat ~/.nxc/nxc.conf
```

---

# Quick Reference - Help

```bash
nxc --help

nxc smb --help
nxc ldap --help
nxc winrm --help
nxc wmi --help
nxc mssql --help
nxc ssh --help
nxc rdp --help
```

---

# Assessment Checklist

## Installation

```text
[ ] NetExec installed
[ ] Version checked
[ ] Current documentation checked
[ ] ~/.nxc understood
[ ] Engagement workspace separated
```

## Discovery

```text
[ ] SMB hosts identified
[ ] Hostnames recorded
[ ] Domains recorded
[ ] Operating-system information reviewed
[ ] SMB signing reviewed
```

## Authentication

```text
[ ] Account type identified
[ ] Domain/local context understood
[ ] Credential testing authorised
[ ] Target set limited
[ ] Authentication results recorded
[ ] Administrative access distinguished from authentication
```

## SMB

```text
[ ] Shares enumerated
[ ] Read permissions reviewed
[ ] Write permissions reviewed
[ ] SYSVOL reviewed where relevant
[ ] NETLOGON reviewed where relevant
[ ] Sensitive content assessed carefully
```

## LDAP

```text
[ ] Domain Controller identified
[ ] LDAP access validated
[ ] Users enumerated where appropriate
[ ] Active users considered
[ ] Directory relationships passed to deeper AD analysis
```

## Remote Management

```text
[ ] WinRM reviewed
[ ] WMI reviewed
[ ] RDP reviewed
[ ] MSSQL reviewed
[ ] SSH reviewed where relevant
```

## Modules

```text
[ ] Module purpose understood
[ ] Module options reviewed
[ ] Privilege requirements understood
[ ] Operational impact understood
[ ] Authorisation confirmed
[ ] Evidence captured
```

## Data Handling

```text
[ ] NetExec database protected
[ ] Client workspaces separated
[ ] Credentials excluded from unnecessary screenshots
[ ] Evidence stored securely
```

## Analysis

```text
[ ] Authentication mapped
[ ] Administrative access mapped
[ ] Shares mapped
[ ] Protocol access mapped
[ ] BloodHound updated
[ ] New credentials re-enumerated
[ ] New hosts re-enumerated
[ ] New networks identified
```

---

# NetExec Decision Tree

```text
START
  |
  v
Do I know the target network?
  |
  +-- No
  |    |
  |    +--> Network discovery
  |    +--> DNS
  |    +--> Routing
  |
  +-- Yes
       |
       v
Run SMB Discovery
       |
       v
Windows Hosts Found?
       |
   +---+---+
   |       |
  No      Yes
   |       |
   |       v
   |   Record Hosts
   |       |
   |       v
   |   Credentials?
   |       |
   |   +---+---+
   |   |       |
   |  No      Yes
   |   |       |
   |   |       v
   |   |   Validate
   |   |   Authentication
   |   |       |
   |   |       v
   |   |   Enumerate Shares
   |   |       |
   |   |       v
   |   |   LDAP Access?
   |   |       |
   |   |   +---+---+
   |   |   |       |
   |   |  No      Yes
   |   |   |       |
   |   |   |       v
   |   |   |   Directory
   |   |   |   Enumeration
   |   |   |       |
   |   |   +-------+
   |   |           |
   |   +-----------+
   |               |
   |               v
   |          Admin Access?
   |               |
   |           +---+---+
   |           |       |
   |          No      Yes
   |           |       |
   |           |       v
   |           |   Candidate
   |           |   Lateral Path
   |           |       |
   |           +-------+
   |               |
   +---------------+
                   |
                   v
             Update Graph
                   |
                   v
             New Access?
                   |
               +---+---+
               |       |
              No      Yes
               |       |
               |       v
               |   Re-enumerate
               |       |
               |       v
               |   New Network?
               |       |
               |   +---+---+
               |   |       |
               |  No      Yes
               |   |       |
               |   |       v
               |   |     Pivot
               |   |       |
               +---+-------+
                   |
                   v
                  END
```

---

# Final NetExec Testing Model

```text
                         NETEXEC
                            |
                            v
                         TARGETS
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
             SMB           LDAP        MANAGEMENT
              |             |             |
              v             v             |
          Host Data     Directory          |
              |             |              |
              v             v              |
          SMB Signing     Users            |
              |           Groups           |
              v          Computers         |
           Shares            |             |
              |              |             |
              +------+-------+             |
                     |                     |
                     v                     v
                 CREDENTIALS         WinRM / WMI
                     |               MSSQL / SSH
                     |                     |
                     +----------+----------+
                                |
                                v
                        ACCESS MAPPING
                                |
                                v
                         ADMINISTRATIVE?
                                |
                     +----------+----------+
                     |                     |
                    No                    Yes
                     |                     |
                     v                     v
               Continue Analysis    Candidate Path
                     |                     |
                     +----------+----------+
                                |
                                v
                           BLOODHOUND
                                |
                                v
                          ATTACK PATH
                                |
                                v
                       MANUAL VALIDATION
                                |
                                v
                           NEW ACCESS
                                |
                                v
                         RE-ENUMERATION
                                |
                                v
                            PIVOTING
```

The key principle is:

```text
NetExec should map access before it is used to exercise access.
```

Use it to understand:

```text
Who can authenticate?

Where can they authenticate?

What can they access?

Where are they privileged?

What protocol provides that access?

What relationship does that create?
```

Then validate only the relationships relevant to the assessment.

---

# Related Notes

```text
active-directory/index.md
active-directory/methodology.md
active-directory/enumeration.md
active-directory/impacket.md
active-directory/responder.md
active-directory/powerview.md
active-directory/bloodhound.md
active-directory/ntlm.md
active-directory/kerberos.md
active-directory/password-spraying.md
active-directory/ntlm-relay.md
active-directory/lateral-movement.md
active-directory/pivoting.md
```

---

# References

## NetExec Documentation

```text
https://www.netexec.wiki/
```

## NetExec GitHub

```text
https://github.com/Pennyw0rth/NetExec
```

## NetExec Wiki Repository

```text
https://github.com/Pennyw0rth/NetExec-Wiki
```

## NetExec Installation

```text
https://www.netexec.wiki/getting-started/installation
```

## NetExec Releases

```text
https://github.com/Pennyw0rth/NetExec/releases
```

## BloodHound

```text
https://bloodhound.specterops.io/
```

## InternalAllTheThings - Active Directory

```text
https://swisskyrepo.github.io/InternalAllTheThings/active-directory/
```
