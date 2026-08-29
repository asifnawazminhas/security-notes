# Active Directory Enumeration

Active Directory enumeration is the process of discovering and mapping the identities, computers, services, permissions, authentication mechanisms, trust relationships, and infrastructure that make up an Active Directory environment.

Enumeration should answer questions such as:

```text
What domain am I connected to?

Where are the Domain Controllers?

Which users and groups exist?

Which accounts are privileged?

Which computers and servers exist?

Which accounts run services?

Which shares are accessible?

Which accounts have administrative access?

Which Kerberos configurations are security-relevant?

Which ACLs create control relationships?

Which GPOs exist?

Which trusts connect the domain to other domains?

Is AD CS deployed?

Which systems expose management protocols?

What relationships create attack paths?
```

Active Directory enumeration should not be treated as:

```text
Run BloodHound
Run NetExec
Done
```

A better model is:

```text
Network
   |
   v
Domain
   |
   v
Directory
   |
   +--> Users
   +--> Groups
   +--> Computers
   +--> OUs
   +--> GPOs
   +--> SPNs
   +--> Delegation
   +--> ACLs
   +--> Trusts
   +--> AD CS
   |
   v
Host Relationships
   |
   +--> Shares
   +--> Sessions
   +--> Local Administrators
   +--> Remote Management
   |
   v
Attack Graph
```

---

# Authorised Testing

These techniques are intended for:

```text
Authorised penetration testing
Internal security assessments
Red team exercises
Purple team exercises
Training laboratories
CTFs
Security research
```

Enumeration can still create substantial security telemetry.

Activities such as:

```text
Large LDAP queries
Large SMB sweeps
User enumeration
Kerberos ticket requests
Session enumeration
Remote registry queries
BloodHound collection
Password policy enumeration
```

may be detected.

Start with the least intrusive techniques and expand deliberately.

---

# Enumeration Philosophy

The objective is not to collect the largest possible amount of data.

The objective is to collect information that helps answer:

```text
Where am I?

Who am I?

What exists?

What can I access?

What does my identity control?

What trusts my identity?

Where are privileged identities?

What security relationships connect these objects?
```

Use:

```text
Discovery
   |
   v
Focused Enumeration
   |
   v
Relationship Analysis
   |
   v
Attack Path Identification
   |
   v
Manual Validation
```

---

# Enumeration Workflow

```text
START
  |
  v
Network Context
  |
  v
Domain Discovery
  |
  v
Domain Controllers
  |
  v
DNS
  |
  v
SMB / LDAP / Kerberos / RPC
  |
  v
Credentials Available?
  |
  +-------------------+
  |                   |
  No                 Yes
  |                   |
  v                   v
Unauthenticated    Authenticated
Enumeration       Enumeration
  |                   |
  +---------+---------+
            |
            v
          Users
            |
            v
          Groups
            |
            v
        Computers
            |
            v
           SPNs
            |
            v
       Delegation
            |
            v
           GPOs
            |
            v
           ACLs
            |
            v
          Trusts
            |
            v
         Shares
            |
            v
        Sessions
            |
            v
       Admin Rights
            |
            v
          AD CS
            |
            v
        BloodHound
            |
            v
       Attack Paths
```

---

# Keep an Enumeration Notebook

Record important environment information as it is discovered.

Example:

```text
DOMAIN=example.local
NETBIOS=EXAMPLE

DC01=dc01.example.local
DC01_IP=10.10.20.10

DC02=dc02.example.local
DC02_IP=10.10.20.11

DNS=10.10.20.10

USER=alice
```

For shell usage:

```bash
export DOMAIN="example.local"
export DC="dc01.example.local"
export DCIP="10.10.20.10"
export USER="alice"
```

Avoid putting plaintext passwords directly into shell history where possible.

---

# Phase 1 - Local Context

Before querying Active Directory, understand the system from which the assessment is being performed.

---

# Linux - Current Network

Interfaces:

```bash
ip addr
```

Routes:

```bash
ip route
```

DNS:

```bash
cat /etc/resolv.conf
```

Neighbour cache:

```bash
ip neigh
```

Hostname:

```bash
hostname
```

Identity:

```bash
id
```

---

# Windows - Current Context

Identity:

```cmd
whoami
```

Detailed identity:

```cmd
whoami /all
```

Hostname:

```cmd
hostname
```

Network:

```cmd
ipconfig /all
```

Routes:

```cmd
route print
```

ARP:

```cmd
arp -a
```

Environment:

```cmd
set
```

---

# PowerShell - Current Context

```powershell
$env:USERDOMAIN
$env:USERDNSDOMAIN
$env:LOGONSERVER
```

Network:

```powershell
Get-NetIPConfiguration
```

Interfaces:

```powershell
Get-NetAdapter
```

Routes:

```powershell
Get-NetRoute
```

DNS:

```powershell
Get-DnsClientServerAddress
```

---

# Determine Whether the Windows Host Is Domain Joined

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name, Domain, PartOfDomain
```

Alternative:

```cmd
systeminfo
```

Look for the domain information.

---

# Phase 2 - Domain Discovery

Determine:

```text
Domain name
NetBIOS domain name
Forest
Domain Controllers
DNS namespace
AD site
```

---

# Windows - Domain Environment

```cmd
echo %USERDOMAIN%
```

```cmd
echo %USERDNSDOMAIN%
```

```cmd
echo %LOGONSERVER%
```

---

# nltest

Locate a Domain Controller:

```cmd
nltest /dsgetdc:example.local
```

List Domain Controllers:

```cmd
nltest /dclist:example.local
```

Domain trusts:

```cmd
nltest /domain_trusts
```

---

# PowerShell Domain Discovery

If the ActiveDirectory PowerShell module is installed:

```powershell
Get-ADDomain
```

Forest:

```powershell
Get-ADForest
```

Domain Controllers:

```powershell
Get-ADDomainController -Filter *
```

---

# Phase 3 - DNS Enumeration

DNS is one of the most important sources of AD infrastructure information.

Active Directory relies heavily on SRV records.

---

# Identify DNS Server

Linux:

```bash
cat /etc/resolv.conf
```

Windows:

```cmd
ipconfig /all
```

PowerShell:

```powershell
Get-DnsClientServerAddress
```

---

# Query Domain

```bash
dig "$DOMAIN"
```

Nameservers:

```bash
dig NS "$DOMAIN"
```

---

# Locate Domain Controllers

```bash
dig SRV _ldap._tcp.dc._msdcs.$DOMAIN
```

---

# Locate Kerberos

```bash
dig SRV _kerberos._tcp.$DOMAIN
```

---

# Global Catalog

```bash
dig SRV _gc._tcp.$DOMAIN
```

---

# Kerberos Password Service

```bash
dig SRV _kpasswd._tcp.$DOMAIN
```

---

# Windows DNS Queries

```cmd
nslookup -type=SRV _ldap._tcp.dc._msdcs.example.local
```

Kerberos:

```cmd
nslookup -type=SRV _kerberos._tcp.example.local
```

---

# PowerShell DNS

```powershell
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.example.local
```

---

# Phase 4 - Domain Controller Identification

A Domain Controller commonly exposes:

```text
53    DNS
88    Kerberos
135   RPC
389   LDAP
445   SMB
464   Kerberos password operations
636   LDAPS
3268  Global Catalog
3269  Global Catalog TLS
```

Do not identify a Domain Controller solely from one open port.

Combine:

```text
DNS
LDAP
SMB metadata
Kerberos
RPC
```

---

# Nmap - Focused DC Discovery

Where network scanning is authorised:

```bash
nmap -Pn -p 53,88,135,389,445,464,636,3268,3269 10.10.20.10
```

For a subnet:

```bash
nmap -Pn -p 88,389,445 10.10.20.0/24
```

Keep scan volume appropriate for the environment.

---

# Phase 5 - SMB Enumeration

SMB can reveal substantial information about Windows hosts.

Questions include:

```text
Which hosts expose SMB?

What hostname is associated with the host?

What domain does the host belong to?

Is SMB signing required?

Which shares exist?

Can the current identity authenticate?

Where does the identity have administrative access?
```

---

# NetExec - SMB Discovery

Single host:

```bash
nxc smb 10.10.20.10
```

Subnet:

```bash
nxc smb 10.10.20.0/24
```

Typical output may help identify:

```text
Hostname
Domain
Operating system information
SMB signing configuration
SMB version-related information
```

depending on the target and NetExec version.

---

# Save SMB Discovery

```bash
nxc smb 10.10.20.0/24 | tee smb-discovery.txt
```

---

# smbclient - List Shares

Anonymous, where permitted:

```bash
smbclient -L //10.10.20.10 -N
```

Authenticated:

```bash
smbclient -L //FILE01.example.local -U 'EXAMPLE/alice'
```

---

# NetExec - Authenticated SMB

```bash
nxc smb 10.10.20.0/24 \
  -d example.local \
  -u alice \
  -p 'Password'
```

Avoid unnecessarily testing credentials across very large ranges.

---

# NetExec - NTLM Hash Authentication

Where authorised:

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -H '<NT-HASH>'
```

The presence of valid NTLM credential material does not automatically imply administrative access.

---

# Authentication State

Distinguish:

```text
Host reachable
      |
      v
Authentication accepted
      |
      v
Resource accessible
      |
      v
Administrative access
```

These are not equivalent states.

---

# Phase 6 - LDAP Enumeration

LDAP provides direct access to Active Directory directory information.

Typical targets:

```text
Users
Groups
Computers
OUs
SPNs
Delegation
GPOs
Trusts
ACL-related attributes
Certificate infrastructure
```

---

# LDAP RootDSE

Start with RootDSE.

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -s base \
  -b "" \
  defaultNamingContext \
  rootDomainNamingContext \
  configurationNamingContext \
  schemaNamingContext \
  dnsHostName
```

This can help determine the correct LDAP base DN.

For:

```text
example.local
```

the base DN is normally:

```text
DC=example,DC=local
```

---

# Authenticated ldapsearch

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local'
```

Using `-W` avoids putting the password directly on the command line.

---

# Search Specific Object Classes

Users:

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local' \
  '(&(objectCategory=person)(objectClass=user))' \
  sAMAccountName
```

---

# Computers

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local' \
  '(objectClass=computer)' \
  sAMAccountName dNSHostName operatingSystem
```

---

# Groups

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local' \
  '(objectClass=group)' \
  cn member
```

---

# Service Principal Names

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local' \
  '(servicePrincipalName=*)' \
  sAMAccountName servicePrincipalName
```

An SPN does not automatically mean an account is exploitable.

---

# Phase 7 - RPC Enumeration

RPC can provide identity and domain information depending on target configuration.

---

# rpcclient

Authenticated:

```bash
rpcclient -U 'EXAMPLE/alice' dc01.example.local
```

It will prompt for the password.

Useful interactive commands can include:

```text
srvinfo
enumdomains
querydominfo
enumdomusers
enumdomgroups
```

Availability depends on the target and account permissions.

---

# Query Domain Information

Inside `rpcclient`:

```text
querydominfo
```

Users:

```text
enumdomusers
```

Groups:

```text
enumdomgroups
```

---

# SID Enumeration with Impacket

Impacket includes `lookupsid.py` for SID/RID-based enumeration over DCE/RPC.

Example authenticated use:

```bash
lookupsid.py 'example.local/alice@dc01.example.local'
```

The tool will prompt for the password when required.

Depending on installation, the command may instead be exposed with an `impacket-` prefix:

```bash
impacket-lookupsid 'example.local/alice@dc01.example.local'
```

Check:

```bash
which lookupsid.py
which impacket-lookupsid
```

---

# Phase 8 - Enumerating Users

Users are one of the central AD object types.

Collect:

```text
sAMAccountName
Display name
Description
Enabled/disabled state
Group membership
Password last set
Last logon information
SPNs
UserAccountControl
Delegation configuration
```

---

# Windows Native

```cmd
net user /domain
```

Specific user:

```cmd
net user alice /domain
```

---

# PowerShell AD Module

```powershell
Get-ADUser -Filter *
```

Selected properties:

```powershell
Get-ADUser -Filter * -Properties DisplayName,Description,Enabled,LastLogonDate,PasswordLastSet |
    Select-Object SamAccountName,DisplayName,Description,Enabled,LastLogonDate,PasswordLastSet
```

---

# PowerView

If PowerView is available in an authorised environment:

```powershell
Get-DomainUser
```

Specific user:

```powershell
Get-DomainUser -Identity alice
```

Useful fields may include:

```text
samaccountname
memberof
serviceprincipalname
useraccountcontrol
description
pwdlastset
lastlogon
```

---

# NetExec User Enumeration

NetExec can query domain users through appropriate protocols.

For example, using LDAP:

```bash
nxc ldap dc01.example.local \
  -d example.local \
  -u alice \
  -p 'Password' \
  --users
```

NetExec options can change between versions.

Confirm current syntax with:

```bash
nxc ldap --help
```

---

# Impacket GetADUsers

Impacket provides `GetADUsers.py`.

Example:

```bash
GetADUsers.py \
  -all \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

The tool can return information such as:

```text
Username
Email
Password last set
Last logon
```

depending on directory data and options.

If installed through a distribution package, check whether it is exposed as:

```bash
impacket-GetADUsers
```

---

# User Descriptions

User descriptions are worth reviewing because administrators sometimes place operational information in them.

PowerShell:

```powershell
Get-ADUser -Filter * -Properties Description |
    Where-Object {$_.Description} |
    Select-Object SamAccountName,Description
```

Do not assume that a description containing a password-like string is valid.

Validate carefully and only when authorised.

---

# Disabled Accounts

```powershell
Get-ADUser -Filter 'Enabled -eq $false'
```

Disabled accounts may still matter for:

```text
Historical privileges
ACL ownership
Group membership
Service configuration
Stale attack paths
```

---

# Recently Created Users

```powershell
Get-ADUser -Filter * -Properties whenCreated |
    Sort-Object whenCreated -Descending |
    Select-Object -First 20 SamAccountName,whenCreated
```

This can help identify:

```text
New service accounts
Temporary accounts
Recently provisioned administrators
```

It is not inherently evidence of a vulnerability.

---

# Password Never Expires

```powershell
Get-ADUser -Filter * -Properties PasswordNeverExpires |
    Where-Object {$_.PasswordNeverExpires -eq $true} |
    Select-Object SamAccountName,Enabled
```

This is a configuration observation that requires context.

---

# Phase 9 - Enumerating Groups

Groups frequently define effective privilege.

---

# Windows Native

```cmd
net group /domain
```

Domain Admins:

```cmd
net group "Domain Admins" /domain
```

Enterprise Admins:

```cmd
net group "Enterprise Admins" /domain
```

---

# PowerShell

```powershell
Get-ADGroup -Filter *
```

Group members:

```powershell
Get-ADGroupMember -Identity "Domain Admins"
```

Recursive membership:

```powershell
Get-ADGroupMember -Identity "Domain Admins" -Recursive
```

---

# PowerView

```powershell
Get-DomainGroup
```

Specific group:

```powershell
Get-DomainGroup -Identity "Domain Admins"
```

Members:

```powershell
Get-DomainGroupMember -Identity "Domain Admins"
```

---

# Custom Privileged Groups

Do not inspect only:

```text
Domain Admins
Enterprise Admins
Administrators
```

Search for organisational groups such as:

```text
Server Admins
SQL Admins
SCCM Admins
VMware Admins
Backup Admins
Citrix Admins
Helpdesk
Application Admins
Tier 0
Infrastructure Admins
```

Privilege often exists outside default AD groups.

---

# Group Nesting

Example:

```text
alice
  |
  v
Helpdesk
  |
  v
Server Support
  |
  v
Production Admins
```

Always evaluate nested group membership.

---

# Phase 10 - Enumerating Computers

Computer objects reveal the structure of the environment.

Collect:

```text
Hostname
Operating system
Operating system version
OU
DNS hostname
Service Principal Names
Delegation configuration
Last logon
```

---

# Windows AD Module

```powershell
Get-ADComputer -Filter *
```

With properties:

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem,OperatingSystemVersion,IPv4Address |
    Select-Object Name,DNSHostName,OperatingSystem,OperatingSystemVersion,IPv4Address
```

---

# PowerView

```powershell
Get-DomainComputer
```

Operating systems:

```powershell
Get-DomainComputer |
    Select-Object Name,DNSHostName,OperatingSystem
```

---

# Domain Controllers

```powershell
Get-ADDomainController -Filter *
```

PowerView:

```powershell
Get-DomainController
```

---

# Identify Servers

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem |
    Where-Object {$_.OperatingSystem -like "*Server*"} |
    Select-Object Name,OperatingSystem
```

---

# Identify Potential Legacy Systems

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem |
    Select-Object Name,OperatingSystem
```

Do not classify a host as vulnerable based solely on the OS string stored in AD.

Confirm the actual system and patch state separately.

---

# Phase 11 - Password Policy

Before any authorised password testing, understand the password and lockout policy.

Questions:

```text
What is the lockout threshold?

What is the lockout duration?

What is the observation window?

What is the minimum password length?

What is the password history?

Are fine-grained password policies used?
```

---

# Windows

```cmd
net accounts /domain
```

---

# PowerShell

```powershell
Get-ADDefaultDomainPasswordPolicy
```

Fine-grained password policies:

```powershell
Get-ADFineGrainedPasswordPolicy -Filter *
```

---

# NetExec

Depending on the current NetExec version and protocol, password-policy enumeration may be available.

Always check:

```bash
nxc smb --help
```

and:

```bash
nxc ldap --help
```

before relying on remembered option names.

---

# Password Policy Before Spraying

Never perform a password spray simply because:

```text
Valid usernames discovered
```

First establish:

```text
Rules of engagement
Lockout threshold
Lockout duration
Observation window
Monitoring concerns
Number of candidate accounts
Number of attempts
```

---

# Phase 12 - SPN Enumeration

Service Principal Names associate services with AD principals.

They are important for:

```text
Service discovery
Service account identification
Kerberos analysis
Delegation analysis
Kerberoasting assessment
```

---

# Windows setspn

Query all SPNs:

```cmd
setspn -Q */*
```

This can produce substantial output in large domains.

---

# PowerShell

```powershell
Get-ADUser -Filter * -Properties ServicePrincipalName |
    Where-Object {$_.ServicePrincipalName} |
    Select-Object SamAccountName,ServicePrincipalName
```

---

# PowerView

```powershell
Get-DomainUser -SPN
```

---

# Impacket GetUserSPNs

Enumeration:

```bash
GetUserSPNs.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

Depending on installation:

```bash
impacket-GetUserSPNs \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

This can identify user accounts associated with SPNs.

Requesting service tickets for offline analysis is a separate testing step and will be covered in the Kerberoasting note.

---

# Important Distinction

```text
SPN exists
   !=
Kerberoasting finding
```

A useful assessment also considers:

```text
Account privilege
Password strength
Password age
Service role
Encryption configuration
Business impact
```

---

# Phase 13 - AS-REP Candidates

Accounts configured without Kerberos pre-authentication are relevant to AS-REP roasting analysis.

---

# PowerShell

The `DONT_REQ_PREAUTH` flag can be identified through `UserAccountControl`.

For example:

```powershell
Get-ADUser -Filter * -Properties DoesNotRequirePreAuth |
    Where-Object {$_.DoesNotRequirePreAuth -eq $true} |
    Select-Object SamAccountName,Enabled
```

---

# PowerView

```powershell
Get-DomainUser -PreauthNotRequired
```

---

# Enumeration vs Ticket Request

Keep these separate:

```text
Identify account configuration
          |
          v
Candidate
```

versus:

```text
Request AS-REP material
          |
          v
Active validation
```

The latter is covered in the dedicated AS-REP Roasting note.

---

# Phase 14 - Delegation Enumeration

Kerberos delegation should always be reviewed.

Important types:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
```

---

# PowerShell - Unconstrained Delegation

```powershell
Get-ADComputer -Filter * -Properties TrustedForDelegation |
    Where-Object {$_.TrustedForDelegation -eq $true} |
    Select-Object Name
```

---

# User Accounts Trusted for Delegation

```powershell
Get-ADUser -Filter * -Properties TrustedForDelegation |
    Where-Object {$_.TrustedForDelegation -eq $true} |
    Select-Object SamAccountName
```

---

# Constrained Delegation

```powershell
Get-ADUser -Filter * -Properties msDS-AllowedToDelegateTo |
    Where-Object {$_.'msDS-AllowedToDelegateTo'} |
    Select-Object SamAccountName,'msDS-AllowedToDelegateTo'
```

Computers:

```powershell
Get-ADComputer -Filter * -Properties msDS-AllowedToDelegateTo |
    Where-Object {$_.'msDS-AllowedToDelegateTo'} |
    Select-Object Name,'msDS-AllowedToDelegateTo'
```

---

# PowerView Delegation Enumeration

Depending on PowerView version:

```powershell
Get-DomainComputer -Unconstrained
```

Constrained delegation can also be identified by examining:

```text
msDS-AllowedToDelegateTo
```

---

# Impacket findDelegation

Impacket provides `findDelegation.py` for identifying delegation relationships.

Example:

```bash
findDelegation.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

Depending on installation:

```bash
impacket-findDelegation \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

The dedicated delegation notes will cover interpretation and validation.

---

# Phase 15 - Organisational Units

OUs help reveal administrative structure.

---

# PowerShell

```powershell
Get-ADOrganizationalUnit -Filter *
```

Selected properties:

```powershell
Get-ADOrganizationalUnit -Filter * |
    Select-Object Name,DistinguishedName
```

---

# PowerView

```powershell
Get-DomainOU
```

---

# Why OUs Matter

OUs can reveal:

```text
Administrative boundaries
Server groups
Workstation groups
Privileged systems
Delegated permissions
GPO application
```

Example:

```text
example.local
│
├── Domain Controllers
├── Servers
│   ├── Production
│   └── Development
├── Workstations
└── Users
    ├── Administrators
    └── Employees
```

---

# Phase 16 - Group Policy Enumeration

Group Policy can control security-sensitive configuration across many systems.

Enumerate:

```text
GPO names
GUIDs
Links
Affected OUs
Permissions
SYSVOL content
Scripts
Preferences
```

---

# PowerShell

```powershell
Get-GPO -All
```

Requires the GroupPolicy module.

---

# PowerView

```powershell
Get-DomainGPO
```

---

# GPO Links

PowerView can assist with understanding where GPOs apply.

The important relationship is:

```text
GPO
 |
 v
Site / Domain / OU
 |
 v
Users / Computers
```

---

# SYSVOL

SYSVOL commonly contains:

```text
Group Policy files
Scripts
Configuration
Policy data
```

Typical UNC path:

```text
\\example.local\SYSVOL
```

List using:

```cmd
dir \\example.local\SYSVOL
```

or:

```bash
smbclient //dc01.example.local/SYSVOL -U 'EXAMPLE/alice'
```

---

# Group Policy Preferences

Legacy Group Policy Preferences credential exposure should still be considered when reviewing older environments or historical SYSVOL content.

Search for files such as:

```text
Groups.xml
Services.xml
Scheduledtasks.xml
DataSources.xml
Printers.xml
Drives.xml
```

A dedicated GPP note will cover the issue.

---

# Phase 17 - ACL Enumeration

ACL analysis identifies which principals can control AD objects.

Important permissions include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
WriteProperty
ForceChangePassword
AddMember
CreateChild
DeleteChild
Extended Rights
```

---

# PowerView ACL Enumeration

```powershell
Get-DomainObjectAcl
```

Resolve GUIDs:

```powershell
Get-DomainObjectAcl -ResolveGUIDs
```

Specific object:

```powershell
Get-DomainObjectAcl -Identity alice -ResolveGUIDs
```

---

# ACL Analysis Model

For every interesting ACE:

```text
Principal
    |
    v
Permission
    |
    v
Target
    |
    v
Affected Attribute / Operation
    |
    v
Resulting Capability
```

---

# Example

```text
Helpdesk
    |
    | GenericWrite
    v
svc_backup
```

Do not stop at:

```text
GenericWrite found
```

Determine exactly what effective capability the permission provides.

---

# Ownership

Object ownership matters because owners may have the ability to alter permissions under applicable security semantics.

Track:

```text
Owner
ACL
Inheritance
Explicit ACEs
Inherited ACEs
```

---

# Phase 18 - Trust Enumeration

Trusts connect domains and forests.

Determine:

```text
Trust partner
Direction
Type
Transitivity
Forest relationship
SID filtering
Selective authentication
```

---

# nltest

```cmd
nltest /domain_trusts
```

---

# PowerShell

```powershell
Get-ADTrust -Filter *
```

---

# PowerView

```powershell
Get-DomainTrust
```

Forest information:

```powershell
Get-Forest
```

---

# Trust Direction

Conceptually:

```text
Domain A
   |
   | Trust
   v
Domain B
```

Always determine:

```text
Who trusts whom?
```

A trust existing does not automatically mean useful access exists across it.

---

# Phase 19 - SMB Share Enumeration

Shares can expose sensitive operational information.

---

# NetExec

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -p 'Password' \
  --shares
```

---

# smbclient

```bash
smbclient -L //FILE01.example.local -U 'EXAMPLE/alice'
```

Connect:

```bash
smbclient //FILE01.example.local/Share -U 'EXAMPLE/alice'
```

---

# Windows

```cmd
net view \\FILE01
```

---

# PowerShell

```powershell
Get-SmbShare
```

`Get-SmbShare` enumerates shares on the local system unless remote management or another mechanism is used to query a remote host.

---

# What to Look For

```text
Deployment scripts
Configuration
Backups
Password databases
Private keys
Certificates
Source code
Database backups
Administrative scripts
Unattended installation files
Remote desktop files
Documentation containing credentials
```

---

# Share Permissions

Distinguish:

```text
Share exists
```

from:

```text
Can list
Can read
Can write
Can modify
```

Writable shares may be particularly security-sensitive depending on how their contents are consumed.

---

# Phase 20 - Session Enumeration

Sessions help identify where users are currently or recently authenticated.

This matters because:

```text
Privileged User
      |
      v
Session on Server
      |
      v
Server Compromise
      |
      v
Potential Credential / Token Exposure
```

Session data should be treated carefully because visibility varies by Windows version, permissions, EDR controls, and collection technique.

---

# BloodHound

BloodHound collectors can gather certain session and local privilege relationships where permitted and technically available.

Treat session information as time-sensitive.

A session discovered ten minutes ago may no longer exist.

---

# Native Windows

Current local users:

```cmd
query user
```

or:

```cmd
quser
```

These commands describe sessions on the queried Windows system and require appropriate access for remote use.

---

# Phase 21 - Local Administrator Relationships

One of the most valuable questions is:

```text
Where is my current identity an administrator?
```

This relationship can turn:

```text
One Credential
```

into:

```text
Many Hosts
```

---

# NetExec

Focused example:

```bash
nxc smb 10.10.20.0/24 \
  -d example.local \
  -u alice \
  -p 'Password'
```

Interpret the output carefully.

Authentication success and administrative access are different.

---

# BloodHound

BloodHound can model relationships such as:

```text
AdminTo
CanRDP
CanPSRemote
```

depending on collected data.

Validate important relationships manually.

---

# Phase 22 - Remote Management Exposure

Enumerate management protocols such as:

```text
SMB
WinRM
RDP
WMI
DCOM
SSH
MSSQL
```

---

# WinRM

Common ports:

```text
5985
5986
```

Nmap:

```bash
nmap -Pn -p 5985,5986 10.10.20.0/24
```

---

# RDP

```bash
nmap -Pn -p 3389 10.10.20.0/24
```

---

# MSSQL

```bash
nmap -Pn -p 1433 10.10.20.0/24
```

---

# Management Protocol Matrix

Maintain:

| Host | SMB | WinRM | RDP | MSSQL | Notes |
|---|---|---|---|---|---|
| DC01 | Yes | Yes | Yes | No | Domain Controller |
| FILE01 | Yes | Yes | Yes | No | File server |
| SQL01 | Yes | Yes | Yes | Yes | Database server |

This becomes useful later during lateral movement.

---

# Phase 23 - LAPS Enumeration

If LAPS is deployed, determine:

```text
Which systems use LAPS?

Which implementation is deployed?

Who can read managed passwords?

Are permissions appropriately restricted?
```

The objective at enumeration stage is primarily to map the configuration and read permissions.

---

# PowerShell

For Windows LAPS environments, the available cmdlets depend on installed management components and deployment model.

Do not assume the legacy Microsoft LAPS and Windows LAPS expose identical attributes or tooling.

Enumerate the actual environment before drawing conclusions.

---

# BloodHound

Modern BloodHound data may help identify LAPS-related read relationships depending on the collector and environment.

Validate the underlying directory permissions before reporting them.

---

# Phase 24 - gMSA Enumeration

Group Managed Service Accounts should be identified.

PowerShell:

```powershell
Get-ADServiceAccount -Filter *
```

Questions:

```text
Which gMSAs exist?

Which systems use them?

Who can retrieve their managed password?

What privilege does each account have?
```

The existence of a gMSA is not a vulnerability.

The important relationship is:

```text
Principal
    |
    | Can retrieve managed password
    v
gMSA
    |
    v
Privileges / Services
```

---

# Phase 25 - Machine Account Quota

Determine the domain's machine account quota.

PowerShell:

```powershell
Get-ADDomain |
    Select-Object DistinguishedName
```

The quota itself is stored in:

```text
ms-DS-MachineAccountQuota
```

Using LDAP:

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local' \
  '(objectClass=domain)' \
  ms-DS-MachineAccountQuota
```

---

# Important Distinction

```text
MachineAccountQuota > 0
          !=
Vulnerability
```

It becomes relevant when combined with other relationships or misconfigurations.

---

# Phase 26 - AD CS Discovery

Determine whether Active Directory Certificate Services is deployed.

Look for:

```text
Enterprise Certificate Authorities
Certificate Templates
Enrollment Services
Web Enrollment
Certificate-related directory objects
```

---

# Certipy

Where authorised and available, Certipy can assist with AD CS discovery.

The detailed syntax will be covered in the dedicated Certipy and AD CS notes.

At enumeration stage the workflow is:

```text
Discover CA
    |
    v
Discover Templates
    |
    v
Map Permissions
    |
    v
Identify Candidate Misconfigurations
```

Do not automatically report every tool-identified ESC candidate without understanding its prerequisites.

---

# Phase 27 - BloodHound Collection

After manual baseline enumeration, collect graph data.

This ordering matters.

If BloodHound is run first without understanding the environment, it is easy to treat graph edges as magic rather than understanding the underlying AD relationship.

---

# Collection Model

```text
Active Directory
       |
       v
Collector
       |
       v
BloodHound Data
       |
       v
Graph
       |
       v
Candidate Attack Paths
       |
       v
Manual Validation
```

---

# Windows Collection

SharpHound is commonly used for Windows-based collection.

Use collection options appropriate to the assessment and environment.

Do not automatically select the broadest collection mode without considering:

```text
Scope
Network traffic
Session enumeration
Local group queries
EDR visibility
Assessment objectives
```

---

# Linux Collection

BloodHound-compatible collection from Linux is possible using supported collectors.

Check the collector documentation and BloodHound version because collection capabilities and compatibility can change.

---

# BloodHound Questions

Useful analysis questions include:

```text
What can my current user reach?

Who controls privileged groups?

Who can modify privileged users?

Who can administer Domain Controllers?

Where are privileged sessions?

Which principals have dangerous ACL rights?

Which GPOs influence privileged systems?

Which delegation relationships exist?

Which AD CS relationships exist?

What paths lead from low privilege to Tier 0?
```

---

# Shortest Path Is Not Always Best Path

A path:

```text
User
 |
 v
Host
 |
 v
Domain Admin
```

may look attractive but require a noisy or disruptive technique.

A longer path may be:

```text
User
 |
 v
ACL
 |
 v
Service Account
 |
 v
Server
 |
 v
Privileged Session
```

and may be more realistic.

Evaluate:

```text
Reliability
Intrusiveness
Detection
Prerequisites
Business impact
```

not merely graph length.

---

# Phase 28 - Name Resolution Enumeration

Internal Windows environments may use:

```text
DNS
LLMNR
NBT-NS
mDNS
```

Determine which mechanisms are present before considering tools such as Responder.

---

# Passive First

Prefer understanding normal traffic before enabling active poisoning behaviour.

Questions:

```text
Are clients generating LLMNR requests?

Are NBT-NS broadcasts visible?

Is mDNS present?

Are WPAD-related requests visible?

Which systems generate the traffic?
```

Responder will receive a dedicated note because capture, poisoning and relay require careful separation.

---

# Phase 29 - SMB Signing Enumeration

SMB signing is important for relay analysis.

NetExec SMB discovery can help identify signing configuration.

Conceptually record:

| Host | SMB | Signing | Role |
|---|---|---|---|
| DC01 | Yes | Required | DC |
| FILE01 | Yes | Not required | File server |
| APP01 | Yes | Required | Application |

Do not conclude:

```text
Signing not required
      =
Compromise
```

It represents one potential prerequisite in certain relay scenarios.

---

# Phase 30 - LDAP Security Controls

For Domain Controllers, review controls relevant to LDAP authentication and relay scenarios.

Consider:

```text
LDAP signing
LDAPS availability
Channel binding
Extended Protection where applicable
Authentication methods
```

This will be covered in greater detail in the NTLM relay notes.

---

# Phase 31 - SYSVOL Enumeration

SYSVOL deserves explicit review.

Typical path:

```text
\\example.local\SYSVOL
```

Linux:

```bash
smbclient //dc01.example.local/SYSVOL -U 'EXAMPLE/alice'
```

Windows:

```cmd
dir \\example.local\SYSVOL
```

Look for:

```text
Scripts
Policies
Configuration
Old files
Credential remnants
Deployment information
```

---

# Phase 32 - NETLOGON Enumeration

NETLOGON can contain logon scripts and other operational content.

Windows:

```cmd
dir \\example.local\NETLOGON
```

Linux:

```bash
smbclient //dc01.example.local/NETLOGON -U 'EXAMPLE/alice'
```

Review scripts for:

```text
Hard-coded credentials
Internal paths
Server names
Deployment commands
Administrative tooling
```

---

# Phase 33 - Service Account Discovery

Service accounts deserve special attention.

Indicators include:

```text
SPNs
Naming conventions
Descriptions
PasswordNeverExpires
Delegation
Group membership
Service-related groups
```

Example naming conventions:

```text
svc_sql
svc_backup
svc_web
svc_sccm
sa_app
app_service
```

Naming alone is not proof that an account is a service account.

---

# Phase 34 - Privileged Identity Discovery

Identify high-value identities beyond Domain Admins.

Examples:

```text
Enterprise Admins
Administrators
Schema Admins
Backup Operators
Server Operators
Account Operators
DNSAdmins
Certificate administrators
SCCM administrators
Backup administrators
Virtualisation administrators
Tier-0 operators
```

Also identify users who can indirectly control these identities.

---

# Privilege Graph

```text
Direct Privilege
      |
      +--> Group Membership
      |
      +--> Administrative Access

Indirect Privilege
      |
      +--> ACL
      +--> GPO
      +--> Credential Access
      +--> Session
      +--> Delegation
      +--> AD CS
```

Indirect privilege is often more interesting.

---

# Phase 35 - Recently Logged-On / Session Context

Where authorised and technically available, understand:

```text
Where are administrators logging in?

Where are service accounts active?

Which systems are used as management hosts?

Where do privileged identities overlap with lower-tier systems?
```

This helps identify tiering weaknesses.

---

# Phase 36 - Domain Trusts and Foreign Principals

When trusts exist, look for:

```text
ForeignSecurityPrincipals
Cross-domain group memberships
SIDHistory
Users from trusted domains
Groups containing foreign principals
```

These relationships may create unexpected privilege.

---

# Phase 37 - AD Sites and Subnets

Large environments often use AD Sites and Services.

Sites can reveal:

```text
Geographical structure
Network segmentation
Domain Controller placement
Subnets
Remote locations
```

PowerShell:

```powershell
Get-ADReplicationSite -Filter *
```

Subnets:

```powershell
Get-ADReplicationSubnet -Filter *
```

This can help inform network and pivoting analysis.

---

# Phase 38 - Identify Additional Network Segments

Computer objects, DNS records, sites, routing information and compromised hosts can reveal networks not visible from the initial position.

Maintain:

```text
10.10.20.0/24   - Initial network
172.16.10.0/24  - Server network
172.16.20.0/24  - Management network
10.50.30.0/24   - Remote site
```

These networks become inputs to the pivoting methodology.

---

# Re-Enumerate After Every New Host

When a new Windows host is accessed:

```text
New Host
   |
   v
whoami /all
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
Sessions
   |
   v
Local Groups
   |
   v
Services
   |
   v
Network Connections
   |
   v
New Network?
```

---

# Re-Enumerate After Every New Credential

```text
New Credential
      |
      v
What identity is this?
      |
      v
Groups
      |
      v
LDAP visibility
      |
      v
Shares
      |
      v
Administrative access
      |
      v
BloodHound paths
      |
      v
AD CS rights
```

---

# Re-Enumerate After Every New Domain

```text
New Domain
    |
    v
Domain Controllers
    |
    v
Users
    |
    v
Groups
    |
    v
Computers
    |
    v
Trusts
    |
    v
AD CS
    |
    v
Attack Paths
```

---

# Enumeration Tool Map

```text
                        ENUMERATION
                             |
       +---------------------+---------------------+
       |                     |                     |
       v                     v                     v
     Native                Linux                 Graph
       |                     |                     |
       v                     v                     v
whoami                  NetExec               BloodHound
net                     Impacket              SharpHound
nltest                  ldapsearch            Collectors
setspn                  smbclient
klist                   rpcclient
PowerShell              Certipy
AD Module               bloodyAD
PowerView
```

---

# Which Tool Should I Use?

## Domain discovery

```text
DNS
nltest
LDAP RootDSE
NetExec
```

## Users and groups

```text
LDAP
PowerShell AD module
PowerView
NetExec
Impacket
```

## Computers

```text
LDAP
PowerShell
PowerView
NetExec
BloodHound
```

## SPNs

```text
setspn
LDAP
PowerView
GetUserSPNs.py
```

## Delegation

```text
LDAP
PowerShell
PowerView
findDelegation.py
BloodHound
```

## ACLs

```text
PowerView
BloodHound
bloodyAD
LDAP/security descriptor tooling
```

## Shares

```text
NetExec
smbclient
Windows net commands
```

## AD CS

```text
Certipy
BloodHound
Native certificate tooling
```

## Trusts

```text
nltest
PowerShell
PowerView
LDAP
BloodHound
```

---

# Enumeration Evidence

Save evidence systematically.

Example:

```text
evidence/
├── domain/
├── dns/
├── smb/
├── ldap/
├── users/
├── groups/
├── computers/
├── kerberos/
├── delegation/
├── gpo/
├── acl/
├── shares/
├── trusts/
├── adcs/
└── bloodhound/
```

---

# Suggested File Names

```text
domain-info.txt
domain-controllers.txt
dns-srv.txt
smb-hosts.txt
ldap-rootdse.txt
users.txt
groups.txt
computers.txt
spns.txt
delegation.txt
password-policy.txt
gpos.txt
shares.txt
trusts.txt
adcs.txt
```

---

# Avoid Credential Leakage in Evidence

Be careful with commands such as:

```bash
tool -u alice -p 'ActualPassword'
```

because the credential may appear in:

```text
Shell history
Process listings
Terminal logs
Evidence files
Screenshots
Screen recordings
```

Prefer password prompts or secure environment-specific mechanisms where practical.

---

# Common Enumeration Mistakes

## Running BloodHound First

Problem:

```text
Graph produced
    |
    v
Tester does not understand environment
```

Better:

```text
Manual baseline
    |
    v
BloodHound
    |
    v
Graph interpretation
```

---

## Confusing Authentication with Admin Access

```text
Credentials work
      !=
Administrator
```

---

## Reporting Tool Labels Directly

```text
Tool says "ESC"
      !=
Confirmed AD CS finding
```

or:

```text
BloodHound edge
      !=
Confirmed exploitable attack path
```

---

## Ignoring Custom Groups

```text
Domain Admins
```

is only one source of privilege.

Custom operational groups can control critical infrastructure.

---

## Ignoring Computer Accounts

Computer accounts:

```text
Authenticate
Have credentials
Have SPNs
Can have ACL rights
Can participate in delegation
```

Do not enumerate only users.

---

## Ignoring DNS

Many AD problems during testing are actually:

```text
DNS problems
```

This is particularly important for Kerberos.

---

## Using IP Addresses Everywhere

Kerberos often expects correct hostname/SPN relationships.

Prefer understanding:

```text
Hostname
FQDN
Domain
DNS
SPN
```

rather than replacing everything with IP addresses.

---

## Forgetting Time Synchronisation

Kerberos depends on acceptable clock synchronisation.

Check Linux time:

```bash
date
```

Windows:

```cmd
w32tm /query /status
```

If Kerberos authentication fails unexpectedly, investigate time as well as credentials and DNS.

---

# False Positives and Interpretation

## SPN Found

Does not automatically mean:

```text
Weak password
```

---

## Pre-Auth Disabled

Does not automatically mean:

```text
Password can be recovered
```

---

## SMB Signing Not Required

Does not automatically mean:

```text
Relay will succeed
```

---

## GenericWrite

Does not automatically mean:

```text
Domain Admin
```

---

## LAPS Exists

Does not automatically mean:

```text
Current user can read passwords
```

---

## gMSA Exists

Does not automatically mean:

```text
Current user can retrieve managed credentials
```

---

## Trust Exists

Does not automatically mean:

```text
Cross-domain compromise
```

---

## AD CS Exists

Does not automatically mean:

```text
ESC vulnerability
```

---

# Enumeration Checklist

## Starting Context

```text
[ ] Current identity
[ ] Hostname
[ ] Domain membership
[ ] Interfaces
[ ] Routes
[ ] DNS
[ ] Current privileges
```

## Domain Discovery

```text
[ ] Domain
[ ] NetBIOS name
[ ] Forest
[ ] Domain Controllers
[ ] AD site
[ ] DNS namespace
```

## DNS

```text
[ ] Domain records
[ ] Domain Controller SRV records
[ ] Kerberos SRV records
[ ] Global Catalog records
[ ] Additional internal hostnames
```

## SMB

```text
[ ] SMB hosts
[ ] Hostnames
[ ] Domains
[ ] SMB signing
[ ] Authentication
[ ] Shares
[ ] Share permissions
[ ] Administrative access relationships
```

## LDAP

```text
[ ] RootDSE
[ ] Base DN
[ ] Users
[ ] Groups
[ ] Computers
[ ] OUs
[ ] SPNs
[ ] Delegation
[ ] Trusts
```

## Users

```text
[ ] All users
[ ] Disabled users
[ ] Privileged users
[ ] Service accounts
[ ] User descriptions
[ ] PasswordNeverExpires
[ ] PasswordLastSet
[ ] Pre-auth configuration
[ ] SPNs
```

## Groups

```text
[ ] Default privileged groups
[ ] Custom privileged groups
[ ] Nested groups
[ ] Foreign members
[ ] Service-management groups
```

## Computers

```text
[ ] Domain Controllers
[ ] Servers
[ ] Workstations
[ ] Operating systems
[ ] Legacy systems
[ ] Management systems
[ ] Certificate infrastructure
```

## Kerberos

```text
[ ] SPNs
[ ] AS-REP candidates
[ ] Unconstrained delegation
[ ] Constrained delegation
[ ] RBCD relationships
[ ] Current tickets
```

## Policy

```text
[ ] Password policy
[ ] Lockout threshold
[ ] Lockout duration
[ ] Fine-grained policies
[ ] GPOs
[ ] SYSVOL
[ ] NETLOGON
```

## Permissions

```text
[ ] ACLs
[ ] Object owners
[ ] GenericAll
[ ] GenericWrite
[ ] WriteDACL
[ ] WriteOwner
[ ] Password reset rights
[ ] Group modification rights
```

## Credentials

```text
[ ] Shares
[ ] Scripts
[ ] Configuration
[ ] LAPS
[ ] gMSA
[ ] User descriptions
[ ] Deployment infrastructure
```

## AD CS

```text
[ ] CA discovered
[ ] Templates discovered
[ ] Enrolment permissions
[ ] Template permissions
[ ] CA permissions
[ ] Candidate ESC conditions
```

## Trusts

```text
[ ] Domain trusts
[ ] Forest trusts
[ ] Direction
[ ] Transitivity
[ ] Foreign principals
[ ] Cross-domain groups
```

## Attack Graph

```text
[ ] BloodHound collected where appropriate
[ ] Current-user paths reviewed
[ ] Privileged paths reviewed
[ ] ACL paths reviewed
[ ] Administrative relationships reviewed
[ ] Session relationships considered
[ ] Important edges manually validated
```

## Network Expansion

```text
[ ] AD sites reviewed
[ ] Subnets reviewed
[ ] Additional interfaces checked
[ ] Additional routes checked
[ ] New networks documented
[ ] Pivot opportunities documented
```

---

# Fast Enumeration Workflow - Windows

```text
whoami /all
      |
      v
ipconfig /all
      |
      v
route print
      |
      v
Domain / DC
      |
      v
Users
      |
      v
Groups
      |
      v
Computers
      |
      v
SPNs
      |
      v
Delegation
      |
      v
GPO
      |
      v
ACL
      |
      v
Trusts
      |
      v
SharpHound
      |
      v
BloodHound
```

---

# Fast Enumeration Workflow - Kali

```text
ip addr / ip route
        |
        v
DNS
        |
        v
DC Discovery
        |
        v
NetExec SMB
        |
        v
LDAP RootDSE
        |
        v
Authenticated LDAP
        |
        v
Users / Groups / Computers
        |
        v
SPNs / Delegation
        |
        v
Shares
        |
        v
Trusts
        |
        v
AD CS
        |
        v
BloodHound Collection
        |
        v
Attack Path Analysis
```

---

# Enumeration Decision Tree

```text
START
  |
  v
Do I know the domain?
  |
  +-- No
  |    |
  |    +--> DNS
  |    +--> SMB metadata
  |    +--> RootDSE
  |
  +-- Yes
       |
       v
Do I know the DC?
       |
       +-- No
       |    |
       |    +--> DNS SRV
       |    +--> nltest
       |    +--> SMB/LDAP discovery
       |
       +-- Yes
            |
            v
Do I have credentials?
            |
      +-----+-----+
      |           |
     No          Yes
      |           |
      v           v
 DNS / SMB      LDAP
 RootDSE        Users
 RPC where      Groups
 exposed        Computers
 Kerberos       SPNs
                Delegation
                GPO
                ACL
                Trusts
                Shares
                AD CS
                  |
                  v
              BloodHound
                  |
                  v
            Interesting Path?
                  |
             +----+----+
             |         |
            No        Yes
             |         |
             v         v
        Expand       Manually
        Analysis     Validate
                         |
                         v
                    New Access?
                         |
                    +----+----+
                    |         |
                   No        Yes
                    |         |
                    |         v
                    |   Re-enumerate
                    |         |
                    |         v
                    |    New Network?
                    |         |
                    |    +----+----+
                    |    |         |
                    |   No        Yes
                    |    |         |
                    |    |         v
                    |    |       Pivot
                    |    |         |
                    +----+---------+
                         |
                         v
                    Re-enumerate
```

---

# Final Enumeration Model

```text
                         NETWORK
                            |
                            v
                           DNS
                            |
                            v
                    DOMAIN CONTROLLERS
                            |
                            v
                  +---------+---------+
                  |         |         |
                  v         v         v
                 SMB       LDAP    KERBEROS
                  |         |         |
                  +---------+---------+
                            |
                            v
                       DIRECTORY
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
      USERS               GROUPS            COMPUTERS
        |                   |                   |
        +-------------------+-------------------+
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
            SPNs        DELEGATION        GPOs
             |              |              |
             +--------------+--------------+
                            |
                            v
                           ACLs
                            |
                +-----------+-----------+
                |                       |
                v                       v
              SHARES                  TRUSTS
                |                       |
                +-----------+-----------+
                            |
                            v
                           AD CS
                            |
                            v
                       BLOODHOUND
                            |
                            v
                      ATTACK PATHS
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

The core rule is:

```text
Enumeration is not a one-time phase.
```

It is a loop:

```text
Enumerate
   |
   v
Gain Context
   |
   v
Enumerate Again
   |
   v
Gain Access
   |
   v
Enumerate Again
   |
   v
Reach New Network
   |
   v
Enumerate Again
```

---

# Related Notes

```text
active-directory/index.md
active-directory/methodology.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/bloodhound.md
active-directory/lateral-movement.md
active-directory/privilege-escalation.md
active-directory/persistence.md
```

Future dedicated notes will cover:

```text
NetExec
Impacket
Responder
BloodHound
PowerView
ACL / ACE
Group Policy
Kerberoasting
AS-REP Roasting
Delegation
NTLM Relay
AD CS
Trusts
Pivoting
SCCM
WSUS
MDT
ADFS
```

---

# References

## Microsoft - Active Directory Domain Services

[Microsoft - Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/){ target="_blank" rel="noopener noreferrer" }

## Microsoft - Active Directory PowerShell

[Microsoft - Active Directory PowerShell](https://learn.microsoft.com/en-us/powershell/module/activedirectory/){ target="_blank" rel="noopener noreferrer" }

## Microsoft - Kerberos Authentication

[Microsoft - Kerberos Authentication](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview){ target="_blank" rel="noopener noreferrer" }

## Microsoft - NTLM

[Microsoft - NTLM](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview){ target="_blank" rel="noopener noreferrer" }

## Microsoft - Group Policy

[Microsoft - Group Policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview){ target="_blank" rel="noopener noreferrer" }

## Microsoft - Active Directory Certificate Services

[Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview){ target="_blank" rel="noopener noreferrer" }

## NetExec

[NetExec](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

## NetExec GitHub

[NetExec GitHub](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

## BloodHound

[BloodHound](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

## bloodyAD

[bloodyAD](https://github.com/CravateRouge/bloodyAD){ target="_blank" rel="noopener noreferrer" }

## PowerView

[PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon){ target="_blank" rel="noopener noreferrer" }

## InternalAllTheThings - Active Directory Enumeration

[InternalAllTheThings - Active Directory Enumeration](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/ad-adds-enumerate/){ target="_blank" rel="noopener noreferrer" }
