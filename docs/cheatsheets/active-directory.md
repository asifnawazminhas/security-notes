# Active Directory Pentesting Cheatsheet

Quick-reference methodology, commands, enumeration paths and security-control checks for authorised Active Directory penetration testing and red-team assessments.

This cheatsheet is designed around an important principle:

```text
Do not assume credentials.
Do not assume domain membership.
Do not assume local access.
Do not assume administrative privileges.
```

Instead, determine where the assessment begins:

```text
                    START
                      |
          +-----------+-----------+
          |                       |
       External                 Internal
          |                       |
    No AD Access          +-------+-------+
                          |               |
                    Unauthenticated   Authenticated
                          |               |
                          |          Domain User
                          |               |
                          +-------+-------+
                                  |
                           AD Enumeration
                                  |
                           Attack Paths
                                  |
                         Host Assessment
                                  |
                      Privilege Escalation
                                  |
                         Lateral Movement
                                  |
                             AD CS
                                  |
                             Trusts
                                  |
                        Controlled Impact
```

!!! warning "Authorised testing only"
    Use these techniques only against Active Directory environments you own or are explicitly authorised to assess. Authentication testing, password spraying, coercion, relay, certificate abuse, credential access, privilege escalation and lateral movement can affect production systems. Follow the agreed scope, rate limits and rules of engagement.

For deeper explanations use:

[Active Directory Notes](../active-directory/index.md)

---

# Assessment Starting Positions

Before running tools, identify your starting position.

| Position | Credentials | Network Access | Typical Objective |
|---|---|---|---|
| External | None | Internet only | Discover exposed AD-related services |
| Internal unauthenticated | None | Internal network | Discover domain infrastructure |
| Internal authenticated | Domain user | Internal network | Enumerate AD and attack paths |
| Local Windows user | Local/domain account | Endpoint | Host + AD enumeration |
| Local administrator | Administrative | Endpoint | Security-control and credential-path assessment |
| Privileged domain user | Elevated AD rights | Internal network | Validate privilege boundaries |

The available attack surface changes dramatically between these positions.

---

# Phase 0 - Scope

Record:

```text
Domains
Forests
IP Ranges
Domain Controllers
Child Domains
Trusted Domains
Cloud / Hybrid Identity
Test Accounts
Allowed Authentication Testing
Password Spray Limits
Lockout Requirements
Excluded Systems
Production Restrictions
Allowed Coercion Testing
Allowed Relay Testing
Allowed AD CS Testing
Allowed Lateral Movement
Credential Handling Requirements
```

---

# Phase 1 - External Position

Starting point:

```text
Internet
   |
   v
No Credentials
   |
   v
No Internal Network Access
```

Do not immediately assume Active Directory is unreachable.

Look for externally exposed identity infrastructure.

---

# External DNS

```bash
dig example.com
```

Name servers:

```bash
dig NS example.com
```

Mail:

```bash
dig MX example.com
```

TXT:

```bash
dig TXT example.com
```

SRV records where publicly exposed:

```bash
dig SRV _ldap._tcp.example.com
```

```bash
dig SRV _kerberos._tcp.example.com
```

---

# External Identity Infrastructure

Look for:

```text
VPN
RD Gateway
OWA
Exchange
AD FS
Microsoft Entra ID
SSO
Remote Desktop Gateway
Citrix
VMware Horizon
Password Reset Portals
Webmail
Hybrid Authentication
Autodiscover
```

The objective is reconnaissance.

Do not attempt credential attacks unless explicitly authorised.

---

# External Port Discovery

Where external infrastructure is in scope:

```bash
nmap -Pn -sV <target>
```

Potential AD-related exposure:

```text
53    DNS
88    Kerberos
135   RPC
389   LDAP
445   SMB
464   Kerberos Password Change
636   LDAPS
3268  Global Catalog
3269  Global Catalog TLS
3389  RDP
5985  WinRM
5986  WinRM TLS
```

Direct exposure of these services to the Internet deserves investigation but is not automatically a vulnerability.

---

# External to Internal Transition

If an authorised foothold is obtained:

```text
External
   |
   v
Foothold
   |
   v
Internal Host
   |
   v
Network Context
   |
   v
Domain Discovery
```

Restart enumeration from the new security context.

---

# Phase 2 - Internal Unauthenticated

Starting point:

```text
Internal Network
      |
      v
No Credentials
      |
      v
Network Discovery
```

Objectives:

```text
Identify Domain
Identify Domain Controllers
Identify DNS
Identify SMB
Identify LDAP
Identify Kerberos
Identify AD CS
Identify Authentication Controls
Identify Reachable Windows Hosts
```

---

# Current Network

Linux:

```bash
ip addr
```

```bash
ip route
```

```bash
ip neigh
```

DNS:

```bash
cat /etc/resolv.conf
```

---

# Windows Network

```cmd
ipconfig /all
```

```cmd
route print
```

```cmd
arp -a
```

---

# DNS Server

Linux:

```bash
cat /etc/resolv.conf
```

Windows:

```cmd
ipconfig /all
```

Internal DNS often provides one of the first clues about the AD domain.

---

# Reverse DNS

```bash
dig -x 10.10.10.10
```

---

# AD DNS Discovery

Once the suspected domain is known:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

Global Catalog:

```bash
dig SRV _ldap._tcp.gc._msdcs.example.local
```

---

# Domain Controller Discovery

```bash
nslookup -type=SRV _ldap._tcp.dc._msdcs.example.local
```

or:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

# Identify AD Services

```bash
nmap -Pn -sV \
    -p 53,88,135,139,389,445,464,636,3268,3269,3389,5985,5986 \
    10.10.10.10
```

---

# SMB Discovery

```bash
nxc smb 10.10.10.0/24
```

This can reveal:

```text
Hostnames
Windows Versions
Domains
SMB Signing
SMB Availability
```

---

# SMB Signing

```bash
nxc smb 10.10.10.0/24 --gen-relay-list relay.txt
```

Nmap:

```bash
nmap -p 445 --script smb2-security-mode 10.10.10.10
```

Important:

```text
SMB Signing Not Required
          !=
Immediate Compromise
```

Relay still requires a usable authentication source and suitable target conditions.

---

# SMBv1

```bash
nmap -p 445 --script smb-protocols 10.10.10.10
```

Review legacy protocol exposure.

---

# LDAP

Check:

```bash
nc -vz 10.10.10.10 389
```

LDAPS:

```bash
nc -vz 10.10.10.10 636
```

---

# Anonymous LDAP

Where explicitly permitted:

```bash
ldapsearch \
    -x \
    -H ldap://10.10.10.10 \
    -s base \
    namingContexts
```

If anonymous queries return useful directory information, determine exactly what is exposed before reporting.

---

# Kerberos

```bash
nc -vz 10.10.10.10 88
```

Kerberos may support limited username validation depending on configuration and tooling.

Avoid high-volume enumeration.

---

# RPC

```bash
rpcclient -U '' -N 10.10.10.10
```

If anonymous/null-session access is permitted, begin with low-impact enumeration.

For example:

```text
Domain Information
Users
Groups
Shares
```

Do not assume null sessions are enabled.

---

# Phase 3 - Authenticated Domain User

A normal domain account is extremely valuable for enumeration.

Starting point:

```text
DOMAIN\user
      |
      v
Authenticated AD Access
      |
      v
Users
Groups
Computers
ACLs
GPOs
Kerberos
Delegation
AD CS
Trusts
Attack Paths
```

A standard domain account is not a low-value position.

Many AD privilege escalation paths begin with ordinary authenticated access.

---

# Current Identity

Windows:

```cmd
whoami
```

```cmd
whoami /all
```

```cmd
whoami /groups
```

```cmd
whoami /priv
```

---

# Domain Environment

```cmd
echo %USERDOMAIN%
```

```cmd
echo %LOGONSERVER%
```

```cmd
echo %COMPUTERNAME%
```

PowerShell:

```powershell
$env:USERDOMAIN
$env:LOGONSERVER
$env:COMPUTERNAME
```

---

# Domain Controller

```cmd
nltest /dsgetdc:example.local
```

All DCs:

```cmd
nltest /dclist:example.local
```

---

# Domain Trusts

```cmd
nltest /domain_trusts
```

---

# Native Domain Users

```cmd
net user /domain
```

Specific user:

```cmd
net user username /domain
```

---

# Native Domain Groups

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

# Password Policy

Before authentication testing:

```cmd
net accounts /domain
```

Review:

```text
Lockout Threshold
Lockout Duration
Lockout Observation Window
Minimum Password Length
Password History
Password Age
```

---

# PowerShell AD Module

Check:

```powershell
Get-Module -ListAvailable ActiveDirectory
```

If available:

```powershell
Import-Module ActiveDirectory
```

---

# Domain

```powershell
Get-ADDomain
```

---

# Forest

```powershell
Get-ADForest
```

---

# Domain Controllers

```powershell
Get-ADDomainController -Filter *
```

---

# Users

```powershell
Get-ADUser -Filter *
```

Useful:

```powershell
Get-ADUser -Filter * -Properties Enabled,PasswordLastSet,LastLogonDate |
    Select-Object SamAccountName,Enabled,PasswordLastSet,LastLogonDate
```

---

# Groups

```powershell
Get-ADGroup -Filter *
```

---

# Group Members

```powershell
Get-ADGroupMember -Identity 'Domain Admins'
```

Recursive:

```powershell
Get-ADGroupMember -Identity 'Domain Admins' -Recursive
```

---

# Computers

```powershell
Get-ADComputer -Filter *
```

Operating systems:

```powershell
Get-ADComputer -Filter * -Properties OperatingSystem |
    Select-Object Name,OperatingSystem
```

---

# Organisational Units

```powershell
Get-ADOrganizationalUnit -Filter *
```

---

# Fine-Grained Password Policies

```powershell
Get-ADFineGrainedPasswordPolicy -Filter *
```

User resultant policy:

```powershell
Get-ADUserResultantPasswordPolicy username
```

---

# LDAP Enumeration

RootDSE:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.example.local \
    -s base \
    namingContexts
```

Authenticated:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.example.local \
    -D 'user@example.local' \
    -W \
    -b 'DC=example,DC=local'
```

Avoid putting passwords directly into command history.

---

# NetExec LDAP

```bash
nxc ldap dc01.example.local \
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

Groups:

```bash
nxc ldap dc01.example.local \
    -u username \
    -p 'Password' \
    --groups
```

---

# NetExec SMB

```bash
nxc smb 10.10.10.0/24 \
    -u username \
    -p 'Password'
```

Look for hosts where the authenticated user has administrative rights.

Do not immediately execute commands.

---

# Shares

```bash
nxc smb 10.10.10.0/24 \
    -u username \
    -p 'Password' \
    --shares
```

---

# Interesting Shares

Look for:

```text
SYSVOL
NETLOGON
IT Shares
Deployment Shares
Software Distribution
Backups
User Shares
Scripts
Configuration Repositories
Administrative Shares
```

---

# SYSVOL

Windows:

```cmd
dir \\example.local\SYSVOL
```

Linux:

```bash
smbclient //dc01.example.local/SYSVOL -U username
```

Review:

```text
Logon Scripts
GPO Files
Configuration
Legacy Credentials
Deployment Scripts
References to Internal Systems
```

---

# NETLOGON

```cmd
dir \\example.local\NETLOGON
```

Look for operational scripts and configuration.

---

# GPP Passwords

Legacy Group Policy Preferences may contain credential material.

Search SYSVOL for:

```text
Groups.xml
Services.xml
Scheduledtasks.xml
DataSources.xml
Printers.xml
Drives.xml
```

Presence alone does not mean credentials are exposed.

---

# Kerberos

Tickets:

```cmd
klist
```

Linux:

```bash
klist
```

---

# SPNs

Native:

```cmd
setspn -Q */*
```

PowerShell:

```powershell
Get-ADUser -Filter * -Properties ServicePrincipalName |
    Where-Object ServicePrincipalName |
    Select-Object SamAccountName,ServicePrincipalName
```

---

# Kerberoasting

Identify accounts with SPNs:

```bash
impacket-GetUserSPNs \
    example.local/username \
    -dc-ip 10.10.10.10
```

Request service tickets where permitted:

```bash
impacket-GetUserSPNs \
    example.local/username \
    -dc-ip 10.10.10.10 \
    -request
```

The underlying issue is normally:

```text
Service Account
      +
Kerberos SPN
      +
Weak Password
```

not simply the existence of an SPN.

---

# AS-REP Roastable Accounts

PowerShell:

```powershell
Get-ADUser \
    -Filter 'DoesNotRequirePreAuth -eq $true' \
    -Properties DoesNotRequirePreAuth
```

Impacket:

```bash
impacket-GetNPUsers \
    example.local/username \
    -dc-ip 10.10.10.10 \
    -request
```

---

# Password Spraying

Never spray before checking lockout policy.

```text
Password Policy
      |
      v
Fine-Grained Policies
      |
      v
Approved Accounts
      |
      v
Small Attempt Set
      |
      v
Observation Window
      |
      v
Controlled Testing
```

---

# BloodHound

BloodHound is valuable because Active Directory privilege escalation often depends on relationships rather than isolated misconfigurations.

Think:

```text
User
 |
 v
Group
 |
 v
ACL
 |
 v
Computer
 |
 v
Session
 |
 v
Admin
```

See:

[BloodHound Cheatsheet](bloodhound.md)

---

# BloodHound Collection

Using SharpHound in an authorised Windows assessment:

```powershell
SharpHound.exe -c All
```

Use collection options appropriate to the assessment.

Some collection methods can generate substantial network traffic.

---

# BloodHound Analysis

Useful starting queries:

```text
Shortest Paths to Domain Admins
Shortest Paths to High Value Targets
Kerberoastable Users
AS-REP Roastable Users
Unconstrained Delegation
Principals with DCSync Rights
Users with Foreign Domain Group Membership
Computers with Unsupported Operating Systems
```

Do not treat every BloodHound edge as directly exploitable.

Validate:

```text
Permission
Context
Reachability
Authentication
Security Controls
```

---

# ACLs

High-value rights can include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
ForceChangePassword
AddMember
AllExtendedRights
DCSync Rights
Validated-SPN
WriteProperty
```

---

# ACL Assessment Model

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
Security Effect
```

Ask:

```text
Who has the right?
What object does it affect?
Can the right change authentication or privilege?
Is inheritance involved?
Is the path actually reachable?
```

---

# Group Membership

Review:

```text
Domain Admins
Enterprise Admins
Administrators
Account Operators
Backup Operators
Server Operators
DNSAdmins
Group Policy Creator Owners
Protected Users
Remote Desktop Users
Remote Management Users
```

Membership is context dependent.

Not every privileged-sounding group produces domain compromise.

---

# MachineAccountQuota

PowerShell:

```powershell
Get-ADDomain |
    Select-Object DistinguishedName
```

Query directly where AD module access permits:

```powershell
Get-ADObject \
    -Identity (Get-ADDomain).DistinguishedName \
    -Properties ms-DS-MachineAccountQuota |
    Select-Object ms-DS-MachineAccountQuota
```

A non-zero MachineAccountQuota is not automatically a vulnerability.

It becomes relevant when combined with another attack path.

---

# Delegation

Identify:

```text
Unconstrained Delegation
Constrained Delegation
Resource-Based Constrained Delegation
S4U
```

---

# Unconstrained Delegation

PowerShell:

```powershell
Get-ADComputer \
    -Filter {TrustedForDelegation -eq $true} \
    -Properties TrustedForDelegation
```

---

# Constrained Delegation

```powershell
Get-ADUser \
    -Filter * \
    -Properties msDS-AllowedToDelegateTo |
    Where-Object { $_.'msDS-AllowedToDelegateTo' }
```

Computers:

```powershell
Get-ADComputer \
    -Filter * \
    -Properties msDS-AllowedToDelegateTo |
    Where-Object { $_.'msDS-AllowedToDelegateTo' }
```

---

# RBCD

Important attribute:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
```

Assess:

```text
Who can modify the target computer?
Who controls a usable security principal?
What SPNs exist?
What Kerberos path is possible?
```

---

# gMSA

Look for:

```text
Group Managed Service Accounts
Principals Allowed to Retrieve Password
Service Usage
Group Membership
ACL Exposure
```

PowerShell:

```powershell
Get-ADServiceAccount -Filter *
```

Do not retrieve password material unless required and authorised.

---

# LAPS

Determine whether the environment uses:

```text
Legacy Microsoft LAPS
Windows LAPS
```

Then assess:

```text
Who can read passwords?
Which computers are covered?
Are passwords rotating?
Are ACLs appropriately restricted?
```

---

# Shadow Credentials

Relevant attribute:

```text
msDS-KeyCredentialLink
```

The key question is:

```text
Who can modify this attribute?
```

rather than simply whether the attribute exists.

---

# AD CS

Active Directory Certificate Services should be treated as a major AD attack surface.

Discovery:

```text
Certificate Authorities
Certificate Templates
Enrollment Services
Web Enrollment
Certificate Permissions
Template Permissions
Enrollment Agent Configuration
Authentication EKUs
```

---

# Certipy Enumeration

Where authorised:

```bash
certipy find \
    -u user@example.local \
    -p 'Password' \
    -dc-ip 10.10.10.10 \
    -stdout
```

Focus potentially vulnerable configurations:

```bash
certipy find \
    -u user@example.local \
    -p 'Password' \
    -dc-ip 10.10.10.10 \
    -vulnerable \
    -stdout
```

Treat automated ESC classifications as leads requiring validation.

---

# AD CS ESC Overview

Keep the major categories in mind:

```text
ESC1
ESC2
ESC3
ESC4
ESC5
ESC6
ESC7
ESC8
ESC9
ESC10
ESC11
ESC12
ESC13
ESC14
ESC15
ESC16
ESC17
```

See the dedicated:

[AD CS Notes](../active-directory/ad-cs/index.md)

---

# AD CS Questions

For every template ask:

```text
Who can enroll?
What EKUs exist?
Can the subject be supplied?
Can SAN be supplied?
Is manager approval required?
Are signatures required?
Who controls the template?
Who controls the CA?
Can authentication certificates be issued?
Can another identity be represented?
```

---

# AD CS Web Enrollment

Look for:

```text
/certsrv/
```

Where present, assess authentication and relay exposure according to scope.

Do not perform coercion or relay automatically.

---

# Trusts

Discover:

```cmd
nltest /domain_trusts
```

PowerShell:

```powershell
Get-ADTrust -Filter *
```

Forest:

```powershell
Get-ADForest
```

---

# Trust Questions

Determine:

```text
Direction
Transitivity
Forest vs Domain Trust
SID Filtering
Selective Authentication
Foreign Group Membership
Authentication Scope
```

---

# SID History

Review SID history where authorised:

```powershell
Get-ADUser -Filter * -Properties SIDHistory |
    Where-Object SIDHistory |
    Select-Object SamAccountName,SIDHistory
```

SIDHistory is legitimate functionality.

The security question is whether unexpected privileged historical SIDs exist.

---

# Host Assessment

Once local access to a Windows system exists, AD enumeration alone is insufficient.

Assess the endpoint.

```text
Identity
   |
   v
Privileges
   |
   v
PowerShell
   |
   v
Application Control
   |
   v
Writable Locations
   |
   v
Services
   |
   v
Scheduled Tasks
   |
   v
Credentials / Configuration
   |
   v
Network Access
```

---

# Host Identity

```cmd
whoami /all
```

```cmd
hostname
```

```cmd
systeminfo
```

---

# Local Users

```cmd
net user
```

---

# Local Groups

```cmd
net localgroup
```

Administrators:

```cmd
net localgroup administrators
```

---

# Current Privileges

```cmd
whoami /priv
```

Pay attention to privileges such as:

```text
SeImpersonatePrivilege
SeAssignPrimaryTokenPrivilege
SeBackupPrivilege
SeRestorePrivilege
SeDebugPrivilege
SeTakeOwnershipPrivilege
SeLoadDriverPrivilege
```

Presence alone is not a vulnerability.

Determine:

```text
Is it enabled?
What security context exists?
What resource can it affect?
Can privilege actually cross a security boundary?
```

---

# PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Possible results:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

Interpret carefully.

```text
FullLanguage
     !=
Vulnerability
```

FullLanguage is the normal PowerShell language mode when application control is not enforcing restrictions.

For hardened workstations, kiosks, jump hosts and other high-security endpoints, FullLanguage may indicate that PowerShell is not being constrained by application-control policy.

---

# PowerShell Version

```powershell
$PSVersionTable
```

---

# Execution Policy

```powershell
Get-ExecutionPolicy -List
```

Important:

```text
Execution Policy
       !=
Security Boundary
```

Do not report a permissive execution policy as an independent privilege escalation vulnerability.

---

# AppLocker

Effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

Summary:

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```

Look for:

```text
Exe
Script
MSI
DLL
Appx
```

---

# AppLocker Rule Collections

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Format-List
```

Important:

```text
Rule Exists
    !=
Secure Policy

Binary Allowed
    !=
Vulnerability

Binary Blocked
    !=
All Execution Prevented
```

Evaluate the complete execution-control model.

---

# Test-AppLockerPolicy

For a known file:

```powershell
Get-AppLockerPolicy -Effective |
    Test-AppLockerPolicy \
        -Path 'C:\Path\To\File.exe' \
        -User "$env:USERDOMAIN\$env:USERNAME"
```

PowerShell does not use Bash-style backslash continuation.

Prefer a one-liner:

```powershell
Get-AppLockerPolicy -Effective | Test-AppLockerPolicy -Path 'C:\Path\To\File.exe' -User "$env:USERDOMAIN\$env:USERNAME"
```

---

# AppLocker Default Path Risk

Pay particular attention to broad path rules such as:

```text
%WINDIR%\*
%PROGRAMFILES%\*
```

These rules are safe only when standard users cannot write attacker-controlled files into allowed locations.

Therefore:

```text
Allowed Path
    +
User Writable
    =
Execution-Control Concern
```

---

# App Control / WDAC

App Control for Business is Microsoft's preferred application-control technology.

Look for deployed policy information using supported administrative tooling available on the endpoint.

Do not conclude WDAC is absent merely because one particular query method fails.

Windows versions and management configurations differ.

---

# PowerShell + Application Control

Important relationship:

```text
Application Control
        |
        v
PowerShell System Lockdown
        |
        v
Constrained Language
```

Therefore check both:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

and:

```powershell
Get-AppLockerPolicy -Effective
```

where available.

---

# PowerShell Logging

Where access permits, assess:

```text
Script Block Logging
Module Logging
Transcription
PowerShell Operational Logs
```

Event log:

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational' -MaxEvents 20
```

Do not disable logging during an assessment.

---

# AMSI

AMSI is another defence layer.

Assess whether security products and PowerShell integrate correctly with AMSI.

Do not treat AMSI as a substitute for:

```text
Application Control
Least Privilege
EDR
Logging
Attack Surface Reduction
```

---

# Defender

Where available:

```powershell
Get-MpComputerStatus
```

Useful fields include:

```text
AntivirusEnabled
RealTimeProtectionEnabled
BehaviorMonitorEnabled
AntispywareEnabled
AMServiceEnabled
```

---

# Defender Preferences

Where permissions allow:

```powershell
Get-MpPreference
```

Review:

```text
Exclusions
ASR Configuration
Cloud Protection
Controlled Folder Access
Network Protection
```

Do not modify these settings during enumeration.

---

# ASR Rules

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,AttackSurfaceReductionRules_Actions
```

Interpret rule IDs against current Microsoft documentation.

---

# Firewall

```cmd
netsh advfirewall show allprofiles
```

Rules:

```cmd
netsh advfirewall firewall show rule name=all
```

---

# Writable Directory Assessment

This is particularly important when application-control policies trust directories.

Common locations to assess include:

```text
C:\Temp
C:\Windows\Temp
C:\ProgramData
C:\Users\Public
%TEMP%
%TMP%
%LOCALAPPDATA%
%APPDATA%
Custom Application Directories
Deployment Directories
Service Directories
Script Directories
```

Do not assume these are writable.

Test permissions.

---

# Current Temporary Directory

CMD:

```cmd
echo %TEMP%
```

```cmd
echo %TMP%
```

PowerShell:

```powershell
$env:TEMP
$env:TMP
```

---

# ACL Inspection

```cmd
icacls C:\Temp
```

```cmd
icacls C:\Windows\Temp
```

```cmd
icacls C:\ProgramData
```

---

# Common ACL Indicators

Look for:

```text
F   Full Control
M   Modify
W   Write
RX  Read and Execute
R   Read
```

Principals of interest:

```text
Everyone
BUILTIN\Users
Authenticated Users
Domain Users
Current User
```

---

# Writable Directory Validation

Permission listings can be complex.

When authorised, a harmless create/delete test is often clearer.

PowerShell:

```powershell
$p='C:\ProgramData\CandidateFolder'; $f=Join-Path $p "write-test-$PID.tmp"; try { New-Item -ItemType File -Path $f -ErrorAction Stop | Out-Null; Write-Host '[+] Writable'; Remove-Item $f -Force } catch { Write-Host '[-] Not writable' }
```

This verifies actual write capability without executing code.

---

# Search Common Writable Locations

PowerShell:

```powershell
$paths = @(
    $env:TEMP,
    'C:\Temp',
    'C:\Windows\Temp',
    'C:\ProgramData',
    'C:\Users\Public'
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Write-Host "`n=== $path ==="
        icacls $path
    }
}
```

---

# Writable PATH Directories

Display PATH:

```cmd
echo %PATH%
```

PowerShell:

```powershell
$env:PATH -split ';'
```

Review whether standard users can modify directories referenced in PATH.

Do not report a writable PATH directory without identifying a privileged process that relies on unsafe path resolution.

---

# Services

List:

```cmd
sc query
```

Detailed:

```cmd
sc qc ServiceName
```

PowerShell:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,PathName
```

---

# Service Assessment

For each interesting service determine:

```text
Service Account
Executable Path
Arguments
Directory Permissions
Binary Permissions
Service ACL
Start Mode
Current State
```

Potential risk:

```text
Privileged Service
      +
User Writable Binary / Directory
      =
Privilege Escalation Candidate
```

---

# Search Services for Candidate Directory

```powershell
$needle = [regex]::Escape('C:\ProgramData\CandidateFolder')

Get-CimInstance Win32_Service |
    Where-Object PathName -Match $needle |
    Select-Object Name,StartName,State,PathName
```

---

# Unquoted Service Paths

Enumerate:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.PathName -match ' ' -and
        $_.PathName -notmatch '^"'
    } |
    Select-Object Name,StartName,PathName
```

Important:

```text
Unquoted Path
     !=
Exploitable
```

You must also identify a location in the resolution chain that the current user can write to.

---

# Scheduled Tasks

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

Review:

```text
Principal
Run Level
Action
Executable
Arguments
Trigger
Writable Script
Writable Binary
Writable Directory
```

---

# Scheduled Task Assessment

Potential path:

```text
Privileged Task
      +
User Writable Action
      =
Privilege Escalation Candidate
```

Do not modify production tasks merely to prove the issue.

---

# Startup Locations

Review:

```text
Startup Folder
Run Keys
RunOnce Keys
Services
Scheduled Tasks
Winlogon
Application Startup Configuration
```

Current user Run key:

```cmd
reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

Machine:

```cmd
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Run
```

---

# AlwaysInstallElevated

Check both locations:

```cmd
reg query HKCU\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

```cmd
reg query HKLM\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

Both configuration conditions matter.

Do not generate or execute an MSI merely to confirm the registry configuration unless explicitly required.

---

# Installed Software

Registry:

```cmd
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall
```

64-bit and 32-bit environments may use additional registry locations.

PowerShell:

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher
```

Avoid `Win32_Product` for routine enumeration because it can trigger MSI consistency checks.

---

# Drivers

```cmd
driverquery /v
```

Review old or unusual third-party drivers as potential security-relevant components.

Version presence alone does not prove vulnerability.

---

# Processes

```cmd
tasklist /v
```

Services:

```cmd
tasklist /svc
```

PowerShell:

```powershell
Get-Process
```

---

# Listening Ports

```cmd
netstat -ano
```

Map PID:

```cmd
tasklist /fi "PID eq 1234"
```

---

# Network Connections

PowerShell:

```powershell
Get-NetTCPConnection
```

---

# RDP

Check service:

```cmd
sc query TermService
```

Port:

```cmd
netstat -ano | findstr :3389
```

---

# WinRM

```cmd
sc query WinRM
```

Ports:

```cmd
netstat -ano | findstr :5985
```

```cmd
netstat -ano | findstr :5986
```

---

# Credential Manager

Safe inventory:

```cmd
cmdkey /list
```

This reveals stored credential targets.

Do not automatically attempt credential extraction.

---

# Configuration Files

Look for security-relevant configuration in:

```text
Web Applications
Deployment Scripts
Backup Scripts
Database Clients
Scheduled Jobs
Automation
Build Systems
Service Configuration
```

Search narrowly rather than recursively reading every user file.

---

# Common File Names

Potentially interesting:

```text
web.config
appsettings.json
application.properties
settings.xml
unattend.xml
unattended.xml
sysprep.xml
*.config
*.ini
*.kdbx
*.rdp
```

Presence does not imply exposed credentials.

---

# PowerShell History

Location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Inspect only where authorised.

History may contain sensitive information.

---

# Environment Variables

CMD:

```cmd
set
```

PowerShell:

```powershell
Get-ChildItem Env:
```

Look for configuration rather than assuming every variable is secret.

---

# Security Products

Services:

```cmd
sc query
```

Processes:

```cmd
tasklist
```

Windows Security Center data may also be available depending on system role and permissions.

Do not disable or tamper with security products.

---

# Application Control Assessment

Think in combinations.

Example:

```text
AppLocker
   |
   +--> EXE Rules
   +--> Script Rules
   +--> MSI Rules
   +--> DLL Rules
           |
           v
Allowed Locations
           |
           v
Writable?
           |
           v
Execution Candidate?
```

A meaningful finding requires the combination.

---

# Common Windows Executables

When reviewing application control, administrators commonly evaluate trusted Windows executables and script hosts.

Examples include:

```text
powershell.exe
pwsh.exe
cmd.exe
wscript.exe
cscript.exe
mshta.exe
rundll32.exe
regsvr32.exe
msbuild.exe
installutil.exe
csc.exe
wmic.exe
forfiles.exe
certutil.exe
bitsadmin.exe
```

Important:

```text
Binary Exists
    !=
Vulnerability

Binary Allowed
    !=
Vulnerability
```

The security issue depends on whether the executable enables an unauthorised security boundary to be crossed.

Use LOLBAS as a reference for understanding legitimate Windows binaries that have security-relevant capabilities.

---

# LOLBAS

LOLBAS documents legitimate Windows binaries, scripts and libraries that may have security-relevant functionality.

Use it for:

```text
Application Control Review
Detection Engineering
Attack Surface Analysis
Blue-Team Validation
Security Research
```

Do not report a system simply because a LOLBin exists.

---

# Local Privilege Escalation Model

```text
Current User
     |
     v
Privileges
     |
     v
Writable Resources
     |
     v
Privileged Consumer
     |
     v
Security Boundary
```

Candidate categories:

```text
Services
Scheduled Tasks
Writable Application Directories
Weak ACLs
Installer Policy
Token Privileges
Credential Exposure
Application Control Gaps
Vulnerable Software
Vulnerable Drivers
```

---

# WinPEAS

WinPEAS can help enumerate privilege escalation candidates.

Treat output as:

```text
Candidate
   |
   v
Manual Validation
   |
   v
Finding
```

not:

```text
Red Output
   =
Vulnerability
```

---

# Seatbelt

Seatbelt is useful for targeted Windows host enumeration.

Potential categories include:

```text
System
Security Controls
Users
Processes
Services
Network
Interesting Files
Configuration
```

Use only collection modules appropriate to scope.

---

# Internal Privilege Escalation Decision Tree

```text
Local Access
    |
    v
whoami /all
    |
    +--> Interesting Privilege?
    |
    +--> Local Admin?
    |
    +--> Writable Service?
    |
    +--> Writable Task?
    |
    +--> Writable Allowed Directory?
    |
    +--> Weak Installer Policy?
    |
    +--> Credential Exposure?
    |
    +--> Vulnerable Software?
    |
    +--> Vulnerable Driver?
    |
    v
Manual Validation
```

---

# Domain Privilege Escalation Decision Tree

```text
Domain User
    |
    +--> Interesting Group?
    |
    +--> ACL Path?
    |
    +--> Kerberoastable Account?
    |
    +--> AS-REP Account?
    |
    +--> Delegation?
    |
    +--> RBCD?
    |
    +--> LAPS / gMSA ACL?
    |
    +--> Shadow Credentials?
    |
    +--> AD CS?
    |
    +--> Trust Path?
    |
    +--> Local Admin Somewhere?
    |
    v
BloodHound
    |
    v
Validate Shortest Path
```

---

# Lateral Movement Assessment

After obtaining authorised access to another identity or host, determine:

```text
Where can this identity authenticate?
Where is it administrator?
Which protocols are available?
Which security controls apply?
```

Possible protocols:

```text
SMB
WinRM
WMI
DCOM
RDP
SSH
MSSQL
```

Do not automatically execute remote commands simply because authentication succeeds.

---

# NetExec Administrative Access

```bash
nxc smb 10.10.10.0/24 \
    -u username \
    -p 'Password'
```

Interpret administrative markers carefully.

Validate the account's intended permissions before treating access as excessive.

---

# WinRM

Check:

```bash
nxc winrm 10.10.10.10 \
    -u username \
    -p 'Password'
```

Successful authentication does not necessarily mean the account has unrestricted administrative rights.

---

# RDP Group

Windows:

```cmd
net localgroup "Remote Desktop Users"
```

---

# Local Administrators

```cmd
net localgroup administrators
```

Remote enumeration may require appropriate privileges.

---

# DCSync Exposure

DCSync-relevant directory replication rights include combinations of replication extended rights.

BloodHound can identify principals with replication privileges.

Treat these rights as highly sensitive.

Do not perform actual credential replication unless explicitly required and authorised.

---

# Domain Admin Is Not the Only Goal

High-impact AD paths can include:

```text
Domain Admin
Enterprise Admin
Domain Controller Control
Certificate Authority Control
DCSync Rights
GPO Control
Tier-0 Server Administration
Identity Infrastructure Control
Backup Infrastructure Control
Deployment Infrastructure Control
```

---

# SCCM

Where present, assess:

```text
Management Points
Distribution Points
Site Servers
Client Push Accounts
Network Access Accounts
Collections
Deployment Permissions
Administrative Roles
```

See detailed SCCM notes in the AD section.

---

# WSUS

Assess:

```text
HTTP vs HTTPS
Update Signing
Server Permissions
Client Configuration
Administrative Access
```

---

# MDT

Review:

```text
Deployment Shares
Bootstrap Configuration
CustomSettings.ini
Scripts
Credentials
Task Sequences
```

Deployment infrastructure frequently contains high-value operational configuration.

---

# SCOM

Assess:

```text
Management Servers
Service Accounts
Agent Configuration
Run As Accounts
Administrative Roles
```

---

# AD FS

Review:

```text
Federation Service
Service Account
Certificates
Token Signing
Token Decryption
Trust Relationships
Endpoints
```

---

# RODC

Assess:

```text
Password Replication Policy
Cached Credentials
Administrative Delegation
RODC Computer Account
Replication Configuration
```

---

# Evidence Collection

For each AD finding record:

```text
Current Principal
Source Host
Target Object
Target Host
Domain
Permission
Protocol
Security Control
Expected Behaviour
Actual Behaviour
Impact
```

---

# ACL Evidence

Record:

```text
Principal
Right
Target Object
Inheritance
Security Effect
```

---

# Host Evidence

Useful baseline:

```cmd
whoami /all
hostname
systeminfo
ipconfig /all
```

PowerShell:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

```powershell
Get-AppLockerPolicy -Effective
```

```powershell
Get-MpComputerStatus
```

where accessible.

---

# Writable Directory Evidence

Record:

```text
Path
Owner
ACL
Writable Principal
Harmless Write Test
Privileged Consumer
Execution Context
```

Without a privileged consumer, a writable directory is usually not a privilege escalation finding.

---

# Service Evidence

Record:

```text
Service
Service Account
Executable
Arguments
ACL
Writable Component
Restart Capability
Security Impact
```

---

# Scheduled Task Evidence

Record:

```text
Task
Principal
Run Level
Action
Writable Component
Trigger
Security Impact
```

---

# AD CS Evidence

Record:

```text
CA
Template
Enrollment Rights
Template Flags
EKUs
Subject Configuration
Manager Approval
Authorised Signatures
Template ACL
CA Configuration
Resulting Security Impact
```

---

# Do Not Overreport

Do not automatically report:

```text
PowerShell FullLanguage
PowerShell Installed
cmd.exe Available
rundll32.exe Available
wscript.exe Available
LOLBins Present
C:\Windows\Temp Writable
C:\ProgramData Exists
SMB Available
LDAP Available
Kerberos Available
Domain User Can Query LDAP
MachineAccountQuota > 0
SPNs Exist
AD CS Exists
BloodHound Finds an Edge
```

Instead establish:

```text
Condition
    +
Permission
    +
Security Boundary
    +
Reachable Consumer
    =
Security Impact
```

---

# Example - Writable Directory

Weak conclusion:

```text
C:\ProgramData\Example is writable.
```

Better analysis:

```text
C:\ProgramData\Example
       |
       v
Writable by standard users
       |
       v
Contains executable used by service
       |
       v
Service runs as LocalSystem
       |
       v
Service consumes user-controlled file
```

Now a security boundary may exist.

---

# Example - AppLocker

Weak conclusion:

```text
rundll32.exe is allowed.
```

Better analysis:

```text
Application Control Policy
        |
        v
rundll32.exe Allowed
        |
        v
Can it consume attacker-controlled content?
        |
        v
Is that content permitted?
        |
        v
Does this cross the intended application-control boundary?
```

---

# Example - CLM

Weak conclusion:

```text
PowerShell runs in FullLanguage.
```

Better analysis:

```text
Endpoint Security Requirement
        |
        v
Application Control Expected?
        |
        v
PowerShell FullLanguage
        |
        v
Untrusted Code Capability
        |
        v
Does this violate intended execution restrictions?
```

---

# Example - Kerberoasting

Weak conclusion:

```text
User has an SPN.
```

Better analysis:

```text
Service Account
      |
      v
SPN
      |
      v
Service Ticket Available
      |
      v
Password Strength
      |
      v
Account Privileges
      |
      v
Impact
```

---

# Example - AD CS

Weak conclusion:

```text
Certificate Services is installed.
```

Better analysis:

```text
Low-Privilege Enrollment
       +
Authentication EKU
       +
Unsafe Subject Configuration
       +
No Approval
       =
Potential Privilege Path
```

---

# Quick Internal Unauthenticated Checklist

- [ ] Identify subnet
- [ ] Identify DNS
- [ ] Identify domain
- [ ] Discover DCs
- [ ] Discover SMB
- [ ] Check SMB signing
- [ ] Check SMB versions
- [ ] Discover LDAP
- [ ] Discover LDAPS
- [ ] Discover Kerberos
- [ ] Check RPC exposure
- [ ] Check anonymous LDAP where permitted
- [ ] Check null-session exposure where permitted
- [ ] Identify AD CS
- [ ] Identify reachable Windows systems

---

# Quick Authenticated Domain User Checklist

- [ ] Confirm identity
- [ ] Enumerate groups
- [ ] Enumerate domain
- [ ] Enumerate forest
- [ ] Enumerate DCs
- [ ] Review password policy
- [ ] Review fine-grained policies
- [ ] Enumerate users
- [ ] Enumerate groups
- [ ] Enumerate computers
- [ ] Enumerate OUs
- [ ] Enumerate shares
- [ ] Review SYSVOL
- [ ] Review NETLOGON
- [ ] Enumerate SPNs
- [ ] Check AS-REP candidates
- [ ] Enumerate delegation
- [ ] Review ACLs
- [ ] Review LAPS
- [ ] Review gMSA
- [ ] Review MachineAccountQuota
- [ ] Review shadow credential paths
- [ ] Enumerate AD CS
- [ ] Enumerate trusts
- [ ] Collect BloodHound data
- [ ] Identify shortest privilege paths
- [ ] Validate paths manually

---

# Quick Windows Host Checklist

- [ ] `whoami /all`
- [ ] `hostname`
- [ ] `systeminfo`
- [ ] `ipconfig /all`
- [ ] `route print`
- [ ] `netstat -ano`
- [ ] Local users
- [ ] Local groups
- [ ] Local administrators
- [ ] Token privileges
- [ ] PowerShell version
- [ ] PowerShell language mode
- [ ] Execution policy
- [ ] AppLocker
- [ ] App Control / WDAC
- [ ] Defender
- [ ] ASR
- [ ] Firewall
- [ ] Processes
- [ ] Services
- [ ] Service paths
- [ ] Service ACLs
- [ ] Scheduled tasks
- [ ] Startup locations
- [ ] Installed software
- [ ] Drivers
- [ ] PATH
- [ ] Writable PATH entries
- [ ] Writable application directories
- [ ] `C:\Temp`
- [ ] `C:\Windows\Temp`
- [ ] `C:\ProgramData`
- [ ] `%TEMP%`
- [ ] `%APPDATA%`
- [ ] `%LOCALAPPDATA%`
- [ ] Credential Manager
- [ ] PowerShell history
- [ ] Configuration files
- [ ] RDP
- [ ] WinRM
- [ ] SMB
- [ ] Security tooling
- [ ] Privileged consumers of writable content

---

# Quick AD Attack-Path Model

```text
Initial Position
      |
      v
Identity
      |
      v
Network
      |
      v
Domain
      |
      v
Users / Groups / Computers
      |
      v
Kerberos / NTLM
      |
      v
ACLs
      |
      v
Delegation
      |
      v
AD CS
      |
      v
Trusts
      |
      v
Host Privileges
      |
      v
BloodHound
      |
      v
Candidate Path
      |
      v
Manual Validation
      |
      v
Controlled Proof
```

---

# Tool Selection

```text
Network Discovery
 |
 +--> Nmap
 +--> NetExec

SMB
 |
 +--> NetExec
 +--> smbclient
 +--> rpcclient
 +--> Impacket

LDAP
 |
 +--> ldapsearch
 +--> NetExec
 +--> PowerShell AD Module

Kerberos
 |
 +--> klist
 +--> Impacket
 +--> Rubeus

AD Graph
 |
 +--> BloodHound
 +--> SharpHound

AD CS
 |
 +--> Certipy
 +--> Certify

Windows Host
 |
 +--> Native Windows Commands
 +--> PowerShell
 +--> WinPEAS
 +--> Seatbelt

Application Control
 |
 +--> AppLocker Cmdlets
 +--> App Control Tooling
 +--> LOLBAS Reference
```

---

# References

## Detailed Local Notes

[Active Directory Notes](../active-directory/index.md)

[AD CS Notes](../active-directory/ad-cs/index.md)

[NetExec Cheatsheet](netexec.md)

[Impacket Cheatsheet](impacket.md)

[BloodHound Cheatsheet](bloodhound.md)

---

## Exploit Notes - Active Directory

[Exploit Notes - Active Directory](https://exploitnotes.org/exploit/windows/active-directory/){ target="_blank" rel="noopener noreferrer" }

Useful as a practical Active Directory enumeration and privilege escalation reference.

---

## Exploit Notes - Windows Privilege Escalation

[Exploit Notes - Windows Privilege Escalation](https://exploitnotes.org/exploit/windows/privilege-escalation/){ target="_blank" rel="noopener noreferrer" }

Useful when transitioning from domain enumeration to host-level privilege analysis.

---

## HackTricks - Active Directory

[HackTricks - Active Directory](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html){ target="_blank" rel="noopener noreferrer" }

Useful as a broad AD methodology and attack-surface reference.

---

## HackTricks - Windows Local Privilege Escalation

[HackTricks - Windows Local Privilege Escalation](https://hacktricks.wiki/en/windows-hardening/windows-local-privilege-escalation/index.html){ target="_blank" rel="noopener noreferrer" }

Useful for host-level privilege escalation methodology and enumeration ideas.

---

## InternalAllTheThings - Windows Privilege Escalation

[InternalAllTheThings - Windows Privilege Escalation](https://swisskyrepo.github.io/InternalAllTheThings/redteam/escalation/windows-privilege-escalation/){ target="_blank" rel="noopener noreferrer" }

Useful as an additional Windows privilege escalation checklist and methodology reference.

---

## Microsoft PowerShell Language Modes

[Microsoft - about_Language_Modes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_language_modes){ target="_blank" rel="noopener noreferrer" }

Use this as the authoritative reference for:

```text
FullLanguage
ConstrainedLanguage
RestrictedLanguage
NoLanguage
```

---

## Microsoft PowerShell Security

[Microsoft - PowerShell Security Features](https://learn.microsoft.com/en-us/powershell/scripting/security/security-features){ target="_blank" rel="noopener noreferrer" }

Useful for:

```text
AMSI
Constrained Language
Application Control
Logging
PowerShell Security
```

---

## Microsoft App Control

[Microsoft - App Control for Business](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }

Microsoft recommends App Control for Business as its preferred Windows application-control technology.

---

## Microsoft AppLocker

[Microsoft - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/){ target="_blank" rel="noopener noreferrer" }

Useful for application-control policy design and rule behaviour.

---

## LOLBAS

[LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }

Useful for understanding security-relevant functionality exposed by legitimate Windows binaries and scripts.

---

## BloodHound

[BloodHound](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

Use BloodHound for relationship and attack-path analysis rather than treating Active Directory objects in isolation.

---

## NetExec

[NetExec](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

---

## Certipy

[Certipy](https://github.com/ly4k/Certipy){ target="_blank" rel="noopener noreferrer" }

---

## PEASS-ng

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

---

## Seatbelt

[GhostPack - Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

---

# Final Assessment Model

Do not approach Active Directory as:

```text
Run BloodHound
Run WinPEAS
Run NetExec
Find Red Output
Report
```

Use:

```text
Starting Position
       |
       v
Security Context
       |
       v
Enumeration
       |
       v
Security Controls
       |
       v
Permissions
       |
       v
Relationships
       |
       v
Candidate Attack Path
       |
       v
Manual Validation
       |
       v
Minimal Proof
       |
       v
Impact
       |
       v
Remediation
```

For an unauthenticated internal assessment:

```text
Network
   ->
Domain
   ->
DC
   ->
Protocols
   ->
Authentication Surface
   ->
Security Configuration
```

For an authenticated domain-user assessment:

```text
Identity
   ->
Groups
   ->
Users
   ->
Computers
   ->
ACLs
   ->
Kerberos
   ->
Delegation
   ->
AD CS
   ->
Trusts
   ->
BloodHound
```

For a compromised Windows endpoint:

```text
whoami /all
   ->
PowerShell Language Mode
   ->
AppLocker / App Control
   ->
Defender / ASR
   ->
Writable Directories
   ->
Services
   ->
Scheduled Tasks
   ->
Credentials / Configuration
   ->
Network Access
   ->
Domain Attack Paths
```

The most important question is not:

```text
What tool can I run?
```

It is:

```text
What security context do I currently have?

What can that identity control?

What security boundary exists?

What other principal or system consumes that control?

Can the relationship be converted into meaningful security impact?
```

That model turns Active Directory enumeration into an actual security assessment rather than a collection of tool output.
