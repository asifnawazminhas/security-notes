# Active Directory Pentesting Cheatsheet

Quick-reference commands and workflows for authorised Active Directory penetration testing, red teaming, purple teaming, labs, and security research.

This cheatsheet is intentionally command-focused.

For methodology and explanations, see:

```text
active-directory/index.md
active-directory/methodology.md
active-directory/enumeration.md
```

---

# Scope and Safety

Before testing:

```text
[ ] Confirm domains in scope
[ ] Confirm IP ranges
[ ] Confirm excluded systems
[ ] Confirm provided credentials
[ ] Confirm password spraying permission
[ ] Confirm credential capture permission
[ ] Confirm NTLM relay permission
[ ] Confirm coercion permission
[ ] Confirm credential dumping permission
[ ] Confirm remote execution permission
[ ] Confirm persistence permission
```

Prefer:

```text
Enumerate
    |
    v
Understand
    |
    v
Analyse
    |
    v
Validate
```

rather than immediately performing intrusive actions.

---

# Quick Workflow

```text
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
Users / Groups / Computers
      |
      v
SPNs / Delegation
      |
      v
Password Policy
      |
      v
Shares / SYSVOL / NETLOGON
      |
      v
GPO / ACL
      |
      v
Trusts
      |
      v
AD CS
      |
      v
BloodHound
      |
      v
Attack Paths
      |
      v
Controlled Validation
      |
      v
New Access
      |
      v
Re-enumerate
      |
      v
Pivot if Required
```

---

# Variables

Useful lab variables:

```bash
export DOMAIN="example.local"
export NETBIOS="EXAMPLE"

export DC="dc01.example.local"
export DCIP="10.10.20.10"

export USER="alice"
```

Avoid storing real passwords directly in shell history.

---

# Linux - Local Context

Identity:

```bash
id
```

Hostname:

```bash
hostname
```

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

Neighbour table:

```bash
ip neigh
```

Current time:

```bash
date
```

---

# Windows - Local Context

Identity:

```cmd
whoami
```

Full token:

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

Kerberos tickets:

```cmd
klist
```

Time synchronisation:

```cmd
w32tm /query /status
```

---

# PowerShell - Local Context

Domain:

```powershell
$env:USERDOMAIN
```

DNS domain:

```powershell
$env:USERDNSDOMAIN
```

Logon server:

```powershell
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

Domain joined:

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain
```

---

# Domain Discovery

Windows:

```cmd
echo %USERDOMAIN%
echo %USERDNSDOMAIN%
echo %LOGONSERVER%
```

Locate a Domain Controller:

```cmd
nltest /dsgetdc:example.local
```

List Domain Controllers:

```cmd
nltest /dclist:example.local
```

Trusts:

```cmd
nltest /domain_trusts
```

---

# PowerShell Domain Discovery

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

# DNS Enumeration

Domain:

```bash
dig "$DOMAIN"
```

Nameservers:

```bash
dig NS "$DOMAIN"
```

Domain Controllers:

```bash
dig SRV _ldap._tcp.dc._msdcs.$DOMAIN
```

Kerberos:

```bash
dig SRV _kerberos._tcp.$DOMAIN
```

Global Catalog:

```bash
dig SRV _gc._tcp.$DOMAIN
```

Kerberos password service:

```bash
dig SRV _kpasswd._tcp.$DOMAIN
```

---

# nslookup

Domain Controllers:

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

Kerberos:

```powershell
Resolve-DnsName -Type SRV _kerberos._tcp.example.local
```

---

# Domain Controller Ports

Useful ports:

```text
53     DNS
88     Kerberos
135    RPC
139    NetBIOS
389    LDAP
445    SMB
464    Kerberos password operations
636    LDAPS
3268   Global Catalog
3269   Global Catalog TLS
3389   RDP
5985   WinRM HTTP
5986   WinRM HTTPS
```

---

# Nmap - AD Ports

Single target:

```bash
nmap -Pn -p 53,88,135,139,389,445,464,636,3268,3269 "$DCIP"
```

Subnet:

```bash
nmap -Pn -p 88,389,445 10.10.20.0/24
```

Management protocols:

```bash
nmap -Pn -p 445,3389,5985,5986 10.10.20.0/24
```

---

# NetExec

NetExec is one of the most useful tools for internal AD enumeration.

General syntax:

```bash
nxc <protocol> <target>
```

Protocols commonly encountered include:

```text
smb
ldap
winrm
rdp
mssql
ssh
```

Available protocols and options depend on the installed NetExec version.

Check:

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

---

# NetExec - SMB Discovery

Single target:

```bash
nxc smb "$DCIP"
```

Subnet:

```bash
nxc smb 10.10.20.0/24
```

Save:

```bash
nxc smb 10.10.20.0/24 | tee smb-discovery.txt
```

---

# NetExec - Password Authentication

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -p 'Password'
```

---

# NetExec - NTLM Hash Authentication

Where authorised:

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -H '<NT-HASH>'
```

---

# NetExec - LDAP

```bash
nxc ldap dc01.example.local \
  -d example.local \
  -u alice \
  -p 'Password'
```

---

# NetExec - Users

Depending on the current NetExec version:

```bash
nxc ldap dc01.example.local \
  -d example.local \
  -u alice \
  -p 'Password' \
  --users
```

Verify available options:

```bash
nxc ldap --help
```

---

# NetExec - Shares

```bash
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -p 'Password' \
  --shares
```

---

# NetExec - Multiple Hosts

```bash
nxc smb 10.10.20.0/24 \
  -d example.local \
  -u alice \
  -p 'Password'
```

Start narrow before expanding credential validation across large networks.

---

# NetExec Interpretation

Remember:

```text
Host reachable
      !=
Credentials valid
```

and:

```text
Credentials valid
      !=
Administrative access
```

and:

```text
Administrative access
      !=
Domain compromise
```

---

# SMB - smbclient

Anonymous listing:

```bash
smbclient -L //10.10.20.10 -N
```

Authenticated listing:

```bash
smbclient -L //FILE01.example.local -U 'EXAMPLE/alice'
```

Connect:

```bash
smbclient //FILE01.example.local/Share -U 'EXAMPLE/alice'
```

---

# Windows SMB

List remote shares:

```cmd
net view \\FILE01
```

SYSVOL:

```cmd
dir \\example.local\SYSVOL
```

NETLOGON:

```cmd
dir \\example.local\NETLOGON
```

---

# LDAP RootDSE

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

---

# LDAP Authentication

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local'
```

Using `-W` prompts for the password instead of placing it directly in the command.

---

# LDAP - Users

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

# LDAP - Computers

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

# LDAP - Groups

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

# LDAP - SPNs

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local' \
  '(servicePrincipalName=*)' \
  sAMAccountName servicePrincipalName
```

---

# LDAP - Machine Account Quota

```bash
ldapsearch -x \
  -H ldap://dc01.example.local \
  -D 'alice@example.local' \
  -W \
  -b 'DC=example,DC=local' \
  '(objectClass=domain)' \
  ms-DS-MachineAccountQuota
```

Remember:

```text
MachineAccountQuota > 0
          !=
Vulnerability
```

---

# RPC

Authenticated:

```bash
rpcclient -U 'EXAMPLE/alice' dc01.example.local
```

Useful commands:

```text
srvinfo
enumdomains
querydominfo
enumdomusers
enumdomgroups
```

---

# rpcclient - Domain Information

Inside:

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

# Impacket

Impacket contains multiple protocol-focused tools.

Common AD-related tools:

```text
GetADUsers.py
GetNPUsers.py
GetUserSPNs.py
findDelegation.py
lookupsid.py
smbclient.py
getTGT.py
getST.py
secretsdump.py
psexec.py
smbexec.py
wmiexec.py
ntlmrelayx.py
```

Depending on installation, commands may be exposed as:

```text
impacket-GetADUsers
impacket-GetNPUsers
impacket-GetUserSPNs
impacket-lookupsid
impacket-findDelegation
impacket-smbclient
impacket-getTGT
impacket-getST
impacket-secretsdump
impacket-psexec
impacket-smbexec
impacket-wmiexec
impacket-ntlmrelayx
```

Find installed names:

```bash
compgen -c | grep '^impacket-' | sort
```

---

# Impacket - Users

```bash
GetADUsers.py \
  -all \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

Alternative packaging:

```bash
impacket-GetADUsers \
  -all \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

---

# Impacket - SID Enumeration

```bash
lookupsid.py 'example.local/alice@dc01.example.local'
```

Alternative:

```bash
impacket-lookupsid 'example.local/alice@dc01.example.local'
```

---

# Impacket - SPNs

```bash
GetUserSPNs.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

Alternative:

```bash
impacket-GetUserSPNs \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

Enumeration alone:

```text
SPN found
   !=
Kerberoasting finding
```

---

# Impacket - Delegation

```bash
findDelegation.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

Alternative:

```bash
impacket-findDelegation \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

---

# Impacket Tool Selection

```text
Users
  |
  +--> GetADUsers

SID / RID
  |
  +--> lookupsid

SPNs
  |
  +--> GetUserSPNs

Delegation
  |
  +--> findDelegation

SMB
  |
  +--> smbclient

Kerberos
  |
  +--> GetNPUsers
  +--> GetUserSPNs
  +--> getTGT
  +--> getST

Credential Extraction
  |
  +--> secretsdump

Remote Administration
  |
  +--> psexec
  +--> smbexec
  +--> wmiexec

Relay
  |
  +--> ntlmrelayx
```

Use intrusive functionality only when permitted by the rules of engagement.

---

# Windows - Users

```cmd
net user /domain
```

Specific user:

```cmd
net user alice /domain
```

---

# PowerShell - Users

```powershell
Get-ADUser -Filter *
```

Useful properties:

```powershell
Get-ADUser -Filter * \
    -Properties DisplayName,Description,Enabled,LastLogonDate,PasswordLastSet |
    Select-Object SamAccountName,DisplayName,Description,Enabled,LastLogonDate,PasswordLastSet
```

---

# User Descriptions

```powershell
Get-ADUser -Filter * -Properties Description |
    Where-Object {$_.Description} |
    Select-Object SamAccountName,Description
```

---

# Disabled Users

```powershell
Get-ADUser -Filter 'Enabled -eq $false'
```

---

# Password Never Expires

```powershell
Get-ADUser -Filter * -Properties PasswordNeverExpires |
    Where-Object {$_.PasswordNeverExpires -eq $true} |
    Select-Object SamAccountName,Enabled
```

---

# Recently Created Users

```powershell
Get-ADUser -Filter * -Properties whenCreated |
    Sort-Object whenCreated -Descending |
    Select-Object -First 20 SamAccountName,whenCreated
```

---

# PowerView - Users

```powershell
Get-DomainUser
```

Specific:

```powershell
Get-DomainUser -Identity alice
```

SPN users:

```powershell
Get-DomainUser -SPN
```

Pre-authentication not required:

```powershell
Get-DomainUser -PreauthNotRequired
```

---

# Windows - Groups

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

# PowerShell - Groups

```powershell
Get-ADGroup -Filter *
```

Members:

```powershell
Get-ADGroupMember -Identity "Domain Admins"
```

Recursive:

```powershell
Get-ADGroupMember -Identity "Domain Admins" -Recursive
```

---

# PowerView - Groups

```powershell
Get-DomainGroup
```

Specific:

```powershell
Get-DomainGroup -Identity "Domain Admins"
```

Members:

```powershell
Get-DomainGroupMember -Identity "Domain Admins"
```

---

# Privileged Groups

Check both default and custom groups.

Default examples:

```text
Domain Admins
Enterprise Admins
Administrators
Schema Admins
Account Operators
Server Operators
Backup Operators
DNSAdmins
Group Policy Creator Owners
```

Organisational examples:

```text
SCCM Admins
SQL Admins
VMware Admins
Backup Admins
Server Admins
Application Admins
Helpdesk
Tier 0
Infrastructure Admins
```

---

# Computers

PowerShell:

```powershell
Get-ADComputer -Filter *
```

Useful properties:

```powershell
Get-ADComputer -Filter * \
    -Properties OperatingSystem,OperatingSystemVersion,IPv4Address |
    Select-Object Name,DNSHostName,OperatingSystem,OperatingSystemVersion,IPv4Address
```

---

# Servers

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem |
    Where-Object {$_.OperatingSystem -like "*Server*"} |
    Select-Object Name,OperatingSystem
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

# PowerView - Computers

```powershell
Get-DomainComputer
```

Selected information:

```powershell
Get-DomainComputer |
    Select-Object Name,DNSHostName,OperatingSystem
```

---

# Password Policy

Windows:

```cmd
net accounts /domain
```

PowerShell:

```powershell
Get-ADDefaultDomainPasswordPolicy
```

Fine-grained policies:

```powershell
Get-ADFineGrainedPasswordPolicy -Filter *
```

Before any authorised password spraying, determine:

```text
Lockout threshold
Lockout duration
Observation window
Minimum password length
Password history
Fine-grained password policies
```

---

# SPNs

Windows:

```cmd
setspn -Q */*
```

PowerShell:

```powershell
Get-ADUser -Filter * -Properties ServicePrincipalName |
    Where-Object {$_.ServicePrincipalName} |
    Select-Object SamAccountName,ServicePrincipalName
```

PowerView:

```powershell
Get-DomainUser -SPN
```

Impacket:

```bash
GetUserSPNs.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

---

# AS-REP Candidate Enumeration

PowerShell:

```powershell
Get-ADUser -Filter * -Properties DoesNotRequirePreAuth |
    Where-Object {$_.DoesNotRequirePreAuth -eq $true} |
    Select-Object SamAccountName,Enabled
```

PowerView:

```powershell
Get-DomainUser -PreauthNotRequired
```

Remember:

```text
Pre-auth disabled
      !=
Password recovered
```

---

# Kerberos Tickets

Windows:

```cmd
klist
```

Purge current tickets only when appropriate:

```cmd
klist purge
```

Be careful because this affects the current authentication context.

---

# Delegation

## Unconstrained Delegation - Computers

```powershell
Get-ADComputer -Filter * -Properties TrustedForDelegation |
    Where-Object {$_.TrustedForDelegation -eq $true} |
    Select-Object Name
```

---

# Unconstrained Delegation - Users

```powershell
Get-ADUser -Filter * -Properties TrustedForDelegation |
    Where-Object {$_.TrustedForDelegation -eq $true} |
    Select-Object SamAccountName
```

---

# Constrained Delegation - Users

```powershell
Get-ADUser -Filter * -Properties msDS-AllowedToDelegateTo |
    Where-Object {$_.'msDS-AllowedToDelegateTo'} |
    Select-Object SamAccountName,'msDS-AllowedToDelegateTo'
```

---

# Constrained Delegation - Computers

```powershell
Get-ADComputer -Filter * -Properties msDS-AllowedToDelegateTo |
    Where-Object {$_.'msDS-AllowedToDelegateTo'} |
    Select-Object Name,'msDS-AllowedToDelegateTo'
```

---

# PowerView - Delegation

Unconstrained:

```powershell
Get-DomainComputer -Unconstrained
```

---

# Impacket - Delegation

```bash
findDelegation.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10
```

---

# Organisational Units

PowerShell:

```powershell
Get-ADOrganizationalUnit -Filter *
```

Selected:

```powershell
Get-ADOrganizationalUnit -Filter * |
    Select-Object Name,DistinguishedName
```

PowerView:

```powershell
Get-DomainOU
```

---

# Group Policy

PowerShell:

```powershell
Get-GPO -All
```

PowerView:

```powershell
Get-DomainGPO
```

---

# SYSVOL

Windows:

```cmd
dir \\example.local\SYSVOL
```

Linux:

```bash
smbclient //dc01.example.local/SYSVOL -U 'EXAMPLE/alice'
```

Look for:

```text
Scripts
Policies
Old configuration
Deployment information
Credential remnants
```

---

# NETLOGON

Windows:

```cmd
dir \\example.local\NETLOGON
```

Linux:

```bash
smbclient //dc01.example.local/NETLOGON -U 'EXAMPLE/alice'
```

Look for:

```text
Logon scripts
Administrative scripts
Internal paths
Server names
Configuration
Credential remnants
```

---

# Group Policy Preferences

Historical files worth recognising:

```text
Groups.xml
Services.xml
Scheduledtasks.xml
DataSources.xml
Printers.xml
Drives.xml
```

Their presence does not automatically prove credential exposure.

---

# ACL Enumeration

PowerView:

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

# Interesting AD Rights

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

Interpret:

```text
Who
 |
 v
Has what permission
 |
 v
Over which object
 |
 v
Affecting which operation
 |
 v
Resulting in what capability
```

---

# ACL Reminder

```text
GenericWrite
    !=
Automatic compromise
```

and:

```text
WriteDACL
    !=
Domain Admin
```

Validate the actual relationship.

---

# Trusts

Windows:

```cmd
nltest /domain_trusts
```

PowerShell:

```powershell
Get-ADTrust -Filter *
```

PowerView:

```powershell
Get-DomainTrust
```

Forest:

```powershell
Get-Forest
```

---

# Trust Questions

```text
What domain is trusted?

What is the direction?

Is it transitive?

Is it a forest trust?

Is selective authentication enabled?

What cross-domain group memberships exist?

Are foreign security principals present?
```

---

# AD Sites

PowerShell:

```powershell
Get-ADReplicationSite -Filter *
```

Subnets:

```powershell
Get-ADReplicationSubnet -Filter *
```

Useful for identifying:

```text
Network segmentation
Remote offices
Domain Controller placement
Potential pivot networks
```

---

# LAPS

Determine:

```text
Is LAPS deployed?

Legacy Microsoft LAPS or Windows LAPS?

Which computers are managed?

Who can read managed passwords?
```

Do not assume legacy LAPS and Windows LAPS use identical attributes or tooling.

---

# gMSA

Enumerate:

```powershell
Get-ADServiceAccount -Filter *
```

Ask:

```text
Who can retrieve the managed password?

Where is the account used?

What privilege does the account have?
```

---

# AD CS

AD CS enumeration should identify:

```text
Certificate Authorities
Certificate Templates
Enrollment permissions
Template permissions
CA permissions
Authentication-enabled templates
Enrollment services
Web enrollment
```

Common tool:

```text
Certipy
```

Treat automated ESC labels as candidates requiring validation.

---

# BloodHound

Use BloodHound to model relationships such as:

```text
MemberOf
AdminTo
HasSession
GenericAll
GenericWrite
WriteDACL
WriteOwner
ForceChangePassword
CanRDP
CanPSRemote
Delegation
Certificate relationships
```

---

# BloodHound Workflow

```text
Collect
   |
   v
Import
   |
   v
Identify Path
   |
   v
Inspect Every Important Edge
   |
   v
Manual Validation
   |
   v
Confirmed Attack Path
```

---

# Useful BloodHound Questions

```text
What can the current user reach?

What can control Domain Admins?

Who can modify privileged groups?

Who can modify privileged users?

Who administers Domain Controllers?

Where are privileged sessions?

Which users have dangerous ACL rights?

Which systems expose remote administration?

Which delegation relationships exist?

Which certificate relationships exist?

What paths lead to Tier 0?
```

---

# BloodHound Reminder

```text
BloodHound edge
      !=
Confirmed vulnerability
```

Validate important edges manually.

---

# Responder

Responder is commonly associated with Windows name-resolution and authentication testing involving mechanisms such as:

```text
LLMNR
NBT-NS
mDNS
```

Before active use:

```text
[ ] Confirm poisoning is authorised
[ ] Confirm correct interface
[ ] Understand enabled responders
[ ] Understand affected protocols
[ ] Consider production impact
[ ] Determine whether capture is permitted
[ ] Determine whether relay is permitted
```

---

# Responder - Interface Discovery

```bash
ip addr
```

Identify the correct assessment interface before running network services.

---

# Responder - Configuration

Review:

```bash
cat /etc/responder/Responder.conf
```

The path can vary depending on installation.

If cloned manually, configuration may be located inside the Responder repository.

---

# Responder - Help

```bash
responder --help
```

or from a cloned repository:

```bash
python3 Responder.py --help
```

Do not blindly enable every responder in a production environment.

---

# Passive Before Active

Prefer:

```text
Observe
   |
   v
Understand Name Resolution
   |
   v
Confirm Scope
   |
   v
Enable Only Required Behaviour
```

A dedicated Responder note should contain the detailed workflows.

---

# SMB Signing

Track:

```text
Host
SMB signing enabled?
SMB signing required?
Role
```

Example:

```text
DC01     Required
FILE01   Not required
APP01    Required
```

Remember:

```text
SMB signing not required
          !=
Successful relay
```

It is one potential prerequisite.

---

# NTLM Relay Analysis

Before testing relay, determine:

```text
Can authentication be obtained?

Can it be relayed?

What destination accepts it?

What protections exist?

What privilege does the relayed identity have?
```

Conceptually:

```text
Authentication
      |
      v
Relay
      |
      v
Target Service
      |
      v
Authorisation
      |
      v
Impact
```

Dedicated NTLM relay notes should contain the detailed testing procedures.

---

# Remote Management

Common protocols:

```text
SMB
WinRM
RDP
WMI
DCOM
MSSQL
SSH
```

---

# WinRM Ports

```text
5985
5986
```

Scan:

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

# Remote Access Matrix

Keep notes such as:

| Host | SMB | WinRM | RDP | MSSQL | Admin |
|---|---|---|---|---|---|
| DC01 | Yes | Yes | Yes | No | No |
| FILE01 | Yes | Yes | Yes | No | Yes |
| SQL01 | Yes | Yes | Yes | Yes | Unknown |

---

# Pivoting

After accessing a new host, immediately check:

```text
Interfaces
Routes
DNS
Neighbours
Listening ports
Connections
Reachable networks
```

---

# Windows Pivot Discovery

Interfaces:

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

Connections:

```cmd
netstat -ano
```

---

# PowerShell Pivot Discovery

```powershell
Get-NetIPConfiguration
```

```powershell
Get-NetRoute
```

```powershell
Get-NetNeighbor
```

```powershell
Get-NetTCPConnection
```

---

# Linux Pivot Discovery

```bash
ip addr
```

```bash
ip route
```

```bash
ip neigh
```

```bash
ss -lntup
```

---

# Pivot Selection

```text
Need one port?
    |
    +--> Port Forward

Need several TCP services?
    |
    +--> SOCKS

Need subnet-like access?
    |
    +--> TUN-based pivot

Need another internal hop?
    |
    +--> Double Pivot
```

Common tools:

```text
SSH
ProxyChains
Ligolo-ng
Chisel
socat
netsh portproxy
```

---

# ProxyChains

Typical configuration:

```text
/etc/proxychains4.conf
```

Example SOCKS entry:

```text
socks5 127.0.0.1 1080
```

Use:

```bash
proxychains nmap ...
```

Be aware that not every Nmap scan type works correctly through a SOCKS proxy.

TCP connect-style workflows are generally more appropriate.

---

# Chisel

Check:

```bash
chisel --help
```

Architecture:

```text
Kali
 |
 | Chisel tunnel
 v
Compromised Host
 |
 v
Internal Network
```

Use the dedicated pivoting note for exact server/client tunnel configurations.

---

# Ligolo-ng

Architecture:

```text
Kali
 |
 | Agent connection
 v
Pivot
 |
 v
Internal Network
```

Ligolo-ng can provide a TUN-style network experience, making many tools easier to use than through application-level SOCKS proxying.

Use the dedicated pivoting note for full setup and routing.

---

# Pivot Documentation

Track:

| Network | Via | Method |
|---|---|---|
| 10.10.20.0/24 | Direct | Local |
| 172.16.20.0/24 | WEB01 | Ligolo-ng |
| 10.50.30.0/24 | APP01 | Second pivot |

---

# DNS During Pivoting

Remember:

```text
Routing works
     !=
DNS works
```

Determine:

```text
Internal DNS server
Reachability
Hostname resolution
FQDN
Kerberos SPN expectations
```

---

# Re-Enumeration Triggers

Re-enumerate after:

```text
[ ] New credential
[ ] New NTLM hash
[ ] New Kerberos ticket
[ ] New certificate
[ ] New user
[ ] New group membership
[ ] New host
[ ] Local administrator access
[ ] New subnet
[ ] New domain
[ ] New forest
[ ] New trust relationship
```

---

# New Credential Workflow

```text
New Credential
      |
      v
Identify Principal
      |
      v
Groups
      |
      v
LDAP Visibility
      |
      v
Shares
      |
      v
Host Access
      |
      v
Administrative Access
      |
      v
BloodHound
      |
      v
AD CS
```

---

# New Host Workflow

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
Local Groups
   |
   v
Sessions
   |
   v
Services
   |
   v
Connections
   |
   v
New Network?
```

---

# New Domain Workflow

```text
New Domain
    |
    v
Domain Controllers
    |
    v
DNS
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
BloodHound
```

---

# High-Value Systems

Do not focus only on Domain Controllers.

Identify:

```text
Domain Controllers
Certificate Authorities
SCCM
WSUS
MDT
ADFS
Backup servers
Virtualisation hosts
Jump servers
Password-management servers
File servers
Database servers
Security-management servers
Deployment servers
```

---

# High-Value Identities

Look beyond Domain Admins.

Examples:

```text
Domain Admins
Enterprise Admins
Administrators
Schema Admins
Certificate administrators
SCCM administrators
Backup administrators
Virtualisation administrators
Server administrators
Tier-0 operators
Service accounts with broad access
```

---

# Sensitive Files on Shares

Useful file types to identify:

```text
*.xml
*.ini
*.config
*.conf
*.ps1
*.bat
*.cmd
*.vbs
*.kdbx
*.pfx
*.p12
*.pem
*.key
*.rdp
*.sql
*.bak
*.zip
*.7z
```

Look for:

```text
Credentials
Connection strings
API keys
Certificates
Private keys
Deployment information
Internal hostnames
Service-account details
Backup information
```

Avoid collecting unnecessary business data.

---

# Evidence Structure

Example:

```text
engagement/
├── evidence/
│   ├── domain/
│   ├── dns/
│   ├── smb/
│   ├── ldap/
│   ├── kerberos/
│   ├── delegation/
│   ├── gpo/
│   ├── acl/
│   ├── shares/
│   ├── trusts/
│   ├── adcs/
│   ├── bloodhound/
│   └── screenshots/
│
├── targets/
├── attack-paths/
├── credentials/
└── notes/
```

Protect the contents appropriately.

---

# Command Logging

Example:

```bash
nxc smb 10.10.20.0/24 |
    tee evidence/smb/discovery.txt
```

LDAP:

```bash
ldapsearch ... |
    tee evidence/ldap/users.txt
```

Avoid writing credentials into evidence unnecessarily.

---

# Attack Path Notes

Document:

```text
Starting Principal:
Target:
Relationship:
Prerequisite:
Technique:
Result:
New Access:
Evidence:
Detection:
Remediation:
```

Example:

```text
alice
 |
 | MemberOf
 v
Helpdesk
 |
 | GenericWrite
 v
svc_backup
 |
 | AdminTo
 v
BACKUP01
```

---

# Tool Result != Vulnerability

Keep this visible during an assessment:

```text
NetExec authentication success
        !=
Administrative compromise

SPN
        !=
Weak service account

BloodHound edge
        !=
Confirmed exploit

GenericWrite
        !=
Domain compromise

SMB signing not required
        !=
Successful NTLM relay

AD CS installed
        !=
ESC vulnerability

Certipy candidate
        !=
Confirmed certificate abuse

LAPS installed
        !=
Readable administrator password

gMSA exists
        !=
Readable managed password

Trust exists
        !=
Cross-domain compromise
```

---

# Fast Kali Enumeration

```bash
# Network
ip addr
ip route
cat /etc/resolv.conf

# DNS
dig SRV _ldap._tcp.dc._msdcs.example.local
dig SRV _kerberos._tcp.example.local

# SMB
nxc smb 10.10.20.0/24

# RootDSE
ldapsearch -x \
  -H ldap://dc01.example.local \
  -s base \
  -b "" \
  defaultNamingContext

# RPC
rpcclient -U 'EXAMPLE/alice' dc01.example.local

# SID enumeration
lookupsid.py 'example.local/alice@dc01.example.local'

# Users
GetADUsers.py \
  -all \
  'example.local/alice' \
  -dc-ip 10.10.20.10

# SPNs
GetUserSPNs.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10

# Delegation
findDelegation.py \
  'example.local/alice' \
  -dc-ip 10.10.20.10

# Shares
nxc smb FILE01.example.local \
  -d example.local \
  -u alice \
  -p 'Password' \
  --shares
```

---

# Fast Windows Enumeration

```cmd
whoami /all
hostname
ipconfig /all
route print
arp -a

echo %USERDOMAIN%
echo %USERDNSDOMAIN%
echo %LOGONSERVER%

nltest /dsgetdc:example.local
nltest /dclist:example.local
nltest /domain_trusts

net user /domain
net group /domain
net group "Domain Admins" /domain

net accounts /domain

klist
setspn -Q */*

dir \\example.local\SYSVOL
dir \\example.local\NETLOGON
```

---

# Fast PowerShell Enumeration

```powershell
Get-ADDomain
Get-ADForest
Get-ADDomainController -Filter *

Get-ADUser -Filter *
Get-ADGroup -Filter *
Get-ADComputer -Filter *

Get-ADGroupMember "Domain Admins" -Recursive

Get-ADDefaultDomainPasswordPolicy
Get-ADFineGrainedPasswordPolicy -Filter *

Get-ADOrganizationalUnit -Filter *
Get-ADTrust -Filter *

Get-ADServiceAccount -Filter *
```

---

# Fast PowerView Enumeration

```powershell
Get-Domain
Get-DomainUser
Get-DomainGroup
Get-DomainComputer
Get-DomainController
Get-DomainOU
Get-DomainGPO
Get-DomainTrust

Get-DomainUser -SPN
Get-DomainUser -PreauthNotRequired

Get-DomainComputer -Unconstrained

Get-DomainObjectAcl -ResolveGUIDs
```

Command availability depends on the PowerView version in use.

---

# What Do I Run Next?

```text
I have no credentials
        |
        +--> Network context
        +--> DNS
        +--> SMB metadata
        +--> LDAP RootDSE
        +--> RPC exposure
        +--> Kerberos-related discovery
        |
        v
I found credentials
        |
        +--> LDAP
        +--> Users
        +--> Groups
        +--> Computers
        +--> Shares
        +--> SPNs
        +--> Delegation
        +--> GPO
        +--> ACL
        +--> Trusts
        +--> AD CS
        |
        v
I found an interesting identity
        |
        +--> Group membership
        +--> ACL rights
        +--> SPNs
        +--> Delegation
        +--> Administrative access
        +--> BloodHound paths
        |
        v
I gained a host
        |
        +--> whoami /all
        +--> Interfaces
        +--> Routes
        +--> DNS
        +--> Sessions
        +--> Local groups
        +--> Connections
        |
        v
I found another network
        |
        +--> Pivot
        |
        v
ENUMERATE AGAIN
```

---

# Active Directory Enumeration Checklist

```text
[ ] Network context
[ ] Domain
[ ] Forest
[ ] Domain Controllers
[ ] DNS
[ ] SMB
[ ] LDAP
[ ] RPC
[ ] Kerberos

[ ] Users
[ ] Groups
[ ] Nested groups
[ ] Computers
[ ] Domain Controllers
[ ] Service accounts
[ ] SPNs

[ ] Password policy
[ ] Fine-grained password policies

[ ] AS-REP candidates
[ ] Unconstrained delegation
[ ] Constrained delegation
[ ] RBCD relationships

[ ] OUs
[ ] GPOs
[ ] SYSVOL
[ ] NETLOGON

[ ] ACLs
[ ] Object ownership
[ ] Custom privileged groups

[ ] Shares
[ ] Share permissions
[ ] Sensitive files

[ ] Sessions
[ ] Administrative relationships
[ ] Remote management

[ ] LAPS
[ ] gMSA
[ ] Machine Account Quota

[ ] Domain trusts
[ ] Forest trusts
[ ] Foreign principals

[ ] AD CS
[ ] Certificate templates
[ ] Certificate permissions

[ ] BloodHound
[ ] Candidate attack paths
[ ] Manual edge validation

[ ] AD sites
[ ] Subnets
[ ] Additional routes
[ ] Pivot opportunities

[ ] Re-enumeration after new access
```

---

# One-Minute Mental Model

When you are unsure what to do next:

```text
WHO AM I?
    |
    v
WHERE AM I?
    |
    v
WHAT DOMAIN?
    |
    v
WHERE ARE THE DCs?
    |
    v
WHAT IDENTITIES EXIST?
    |
    v
WHAT SYSTEMS EXIST?
    |
    v
WHAT CAN I ACCESS?
    |
    v
WHAT CAN I CONTROL?
    |
    v
WHAT TRUSTS ME?
    |
    v
WHAT CAN THAT ACCESS REACH?
    |
    v
DID MY NETWORK POSITION CHANGE?
    |
    v
ENUMERATE AGAIN
```

---

# Final Cheatsheet Model

```text
                         START
                           |
                           v
                  Network + Identity
                           |
                           v
                     Domain + DNS
                           |
                           v
                    Domain Controllers
                           |
            +--------------+--------------+
            |              |              |
            v              v              v
           SMB            LDAP         Kerberos
            |              |              |
            +--------------+--------------+
                           |
                           v
                       DIRECTORY
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
        USERS            GROUPS         COMPUTERS
          |                |                |
          +----------------+----------------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
            SPNs       DELEGATION       GPO
             |             |             |
             +-------------+-------------+
                           |
                           v
                          ACL
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
          SHARES         TRUSTS         AD CS
             |             |             |
             +-------------+-------------+
                           |
                           v
                      BLOODHOUND
                           |
                           v
                     ATTACK PATH
                           |
                           v
                       VALIDATE
                           |
                           v
                      NEW ACCESS
                           |
                           v
                    RE-ENUMERATE
                           |
                 +---------+---------+
                 |                   |
                 v                   v
          LATERAL MOVEMENT        PIVOTING
                 |                   |
                 +---------+---------+
                           |
                           v
                    NEW ENVIRONMENT
                           |
                           v
                    ENUMERATE AGAIN
```

---

# Related Notes

```text
active-directory/index.md
active-directory/methodology.md
active-directory/enumeration.md
active-directory/kerberos.md
active-directory/ntlm.md
active-directory/bloodhound.md
active-directory/lateral-movement.md
active-directory/privilege-escalation.md
active-directory/persistence.md
```

Future dedicated notes:

```text
active-directory/netexec.md
active-directory/impacket.md
active-directory/responder.md
active-directory/powerview.md
active-directory/acls.md
active-directory/group-policy.md
active-directory/kerberoasting.md
active-directory/asrep-roasting.md
active-directory/delegation.md
active-directory/ntlm-relay.md
active-directory/adcs.md
active-directory/trusts.md
active-directory/pivoting.md
active-directory/sccm.md
active-directory/wsus.md
active-directory/mdt.md
active-directory/adfs.md
```

---

# References

## Microsoft Active Directory Domain Services

[Microsoft Active Directory Domain Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/)

## Microsoft Active Directory PowerShell

[Microsoft Active Directory PowerShell](https://learn.microsoft.com/en-us/powershell/module/activedirectory/)

## Microsoft Kerberos

[Microsoft Kerberos](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)

## Microsoft NTLM

[Microsoft NTLM](https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview)

## Microsoft Group Policy

[Microsoft Group Policy](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-policy/group-policy-overview)

## Microsoft AD CS

[Microsoft AD CS](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/active-directory-certificate-services-overview)

## NetExec

[NetExec](https://www.netexec.wiki/)

## NetExec GitHub

[NetExec GitHub](https://github.com/Pennyw0rth/NetExec)

## Impacket

[Impacket](https://github.com/fortra/impacket)

## BloodHound

[BloodHound](https://bloodhound.specterops.io/)

## Certipy

[Certipy](https://github.com/ly4k/Certipy)

## bloodyAD

[bloodyAD](https://github.com/CravateRouge/bloodyAD)

## PowerView

[PowerView](https://github.com/PowerShellMafia/PowerSploit/tree/master/Recon)

## Responder

[Responder](https://github.com/lgandx/Responder)

## Ligolo-ng

[Ligolo-ng](https://github.com/nicocha30/ligolo-ng)

## Chisel

[Chisel](https://github.com/jpillora/chisel)

## InternalAllTheThings - Active Directory

[InternalAllTheThings - Active Directory](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/)

## InternalAllTheThings - AD Enumeration

[InternalAllTheThings - AD Enumeration](https://swisskyrepo.github.io/InternalAllTheThings/active-directory/ad-adds-enumerate/)
