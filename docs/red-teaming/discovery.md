---
title: Red Team Discovery
description: Post-compromise discovery methodology for authorised red team assessments, covering host, user, process, network, service, software, security-control, domain, Active Directory, cloud, container and virtualisation discovery with evidence, detection and reporting guidance.
---

# Red Team Discovery

Discovery is the process of understanding the environment after obtaining an authorised foothold.

Reconnaissance primarily asks:

```text
What can be learned before access?
```

Discovery asks:

```text
Where am I?

Who am I?

What can I access?

What systems surround me?

Which security boundaries exist?

Which identities and privileges are present?

Which services and applications are important?

Which defensive controls are operating?

What should I investigate next?
```

A practical model is:

```text
Foothold
   |
   v
Current Context
   |
   v
Host Discovery
   |
   v
Network Discovery
   |
   v
Identity Discovery
   |
   v
Domain Discovery
   |
   v
Security-Control Discovery
   |
   v
Attack-Path Decisions
```

Discovery should be deliberate rather than an uncontrolled collection of system information.

!!! warning "Authorised testing only"
    Discovery can expose sensitive infrastructure, identities, network architecture and business systems. Remain within the authorised scope, minimise unnecessary collection, avoid disruptive scanning, and do not automatically interact with every system discovered from a compromised host.


---

# Discovery Objectives

Typical objectives include:

```text
Identify the current host

Identify the current user

Determine current privileges

Determine domain membership

Identify operating-system details

Identify running processes

Identify installed software

Identify services

Identify network configuration

Identify local routes

Identify DNS configuration

Identify neighbouring systems

Identify remote services

Identify Active Directory relationships

Identify security controls

Identify cloud context

Identify container context

Identify candidate privilege paths

Identify candidate lateral-movement paths

Identify objective-relevant systems
```


---

# Discovery in the Attack Chain

```text
Initial Access
      |
      v
Execution
      |
      v
Foothold
      |
      v
Discovery
      |
      +-------------------+
      |                   |
      v                   v
Privilege Escalation   Credential Access
      |                   |
      +---------+---------+
                |
                v
         Lateral Movement
                |
                v
             Objective
```


---

# Discovery vs Reconnaissance

These phases overlap but occur in different contexts.

## Reconnaissance

Usually performed before obtaining access.

Examples:

```text
Domains

Subdomains

Public IP addresses

Internet-facing applications

Public identities

Cloud services

Public repositories
```

See:

[Reconnaissance](reconnaissance.md)


## Discovery

Usually performed after obtaining access.

Examples:

```text
Hostname

Local users

Domain membership

Processes

Services

Network interfaces

Routes

Internal DNS

Domain controllers

Shares

Security software

Internal applications
```


---

# Discovery Principles

Good discovery should be:

```text
Objective-driven

Scoped

Incremental

Low impact

Evidence-based

Context-aware

Defender-aware
```

Avoid:

```text
Scan everything immediately

Dump every available data source

Query every domain object

Contact every internal host

Collect unrelated sensitive information
```


---

# Discovery Workflow

```text
Foothold
   |
   v
Establish Context
   |
   v
Local Host
   |
   v
Security Controls
   |
   v
Network
   |
   v
Identity
   |
   v
Domain / Directory
   |
   v
Applications / Services
   |
   v
Cloud / Containers
   |
   v
Candidate Paths
   |
   v
Prioritise
```


---

# Phase 1 - Establish Current Context

Immediately record:

```text
Hostname

Username

Privilege

Operating system

Architecture

Domain/workgroup

Shell

Working directory

Timestamp
```

This provides the baseline for all later activity.


---

# Windows Basic Context

Current identity:

```powershell
whoami
```

Detailed identity:

```powershell
whoami /all
```

Hostname:

```powershell
hostname
```

Operating system:

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber,OSArchitecture
```

Computer information:

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain,Manufacturer,Model
```


---

# Windows Environment

```powershell
Get-ChildItem Env:
```

Interesting variables can include:

```text
USERDOMAIN

USERNAME

USERPROFILE

COMPUTERNAME

PATH

TEMP

ProgramFiles
```


---

# Windows PowerShell Context

```powershell
$PSVersionTable
```

Language mode:

```powershell
$ExecutionContext.SessionState.LanguageMode
```

Execution policy:

```powershell
Get-ExecutionPolicy -List
```


---

# Windows Privilege Context

```powershell
whoami /priv
```

Groups:

```powershell
whoami /groups
```

Local administrators:

```powershell
Get-LocalGroupMember -Group Administrators -ErrorAction SilentlyContinue
```


---

# Linux Basic Context

Identity:

```bash
id
```

Current user:

```bash
whoami
```

Hostname:

```bash
hostname
```

System:

```bash
uname -a
```

Distribution:

```bash
cat /etc/os-release
```


---

# Linux Shell Context

```bash
echo "$SHELL"
```

Current process:

```bash
ps -p $$ -o pid,ppid,user,comm,args
```

Environment:

```bash
env
```


---

# Linux Privilege Context

Groups:

```bash
groups
```

Sudo permissions:

```bash
sudo -l
```

This should normally be checked early because it can immediately identify intended or unintended privilege relationships.


---

# Phase 2 - Host Discovery

Understand the system before expanding outward.

Collect:

```text
Operating system

Architecture

Hardware or VM information

Processes

Services

Installed applications

Scheduled execution

Users

Groups

Sessions

Filesystem

Mounted storage
```


---

# Windows Process Discovery

```powershell
Get-Process
```

Detailed process information:

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,ExecutablePath
```

Processes can reveal:

```text
Applications

Security software

Administrative tools

Browsers

Database clients

Management agents

Custom services
```


---

# Process Interpretation

A process name should normally be treated as an indicator.

Example:

```text
MsMpEng.exe
```

strongly suggests Microsoft Defender components are active, but security-control status should still be validated through configuration and telemetry where possible.


---

# Windows Services

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,DisplayName,StartName,State,StartMode,PathName
```

Services can reveal:

```text
Security agents

Backup software

Database software

Management tools

Custom applications

Service accounts

Privileged execution paths
```


---

# Running Services Only

```powershell
Get-Service |
    Where-Object Status -eq Running
```


---

# Scheduled Tasks

```powershell
Get-ScheduledTask |
    Select-Object TaskName,TaskPath,State
```

Scheduled tasks may reveal:

```text
Administrative automation

Maintenance scripts

Backup processes

Custom applications

Service accounts

Potential privilege relationships
```


---

# Installed Software

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```

Also inspect 32-bit applications:

```powershell
Get-ItemProperty HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```


---

# Software Discovery Questions

Ask:

```text
What applications are installed?

Which are business-critical?

Which run privileged services?

Which provide remote administration?

Which security products are installed?

Which appear outdated?

Which contain interesting configuration?
```


---

# Windows Users

```powershell
Get-LocalUser
```

Groups:

```powershell
Get-LocalGroup
```

Membership of a specific group:

```powershell
Get-LocalGroupMember -Group Administrators
```


---

# Current Sessions

```cmd
query user
```

This may reveal interactive sessions on the current host.

Do not assume every visible session should be targeted.


---

# Windows Drives

```powershell
Get-PSDrive -PSProvider FileSystem
```

Alternative:

```powershell
Get-CimInstance Win32_LogicalDisk |
    Select-Object DeviceID,DriveType,FileSystem,Size,FreeSpace
```


---

# Linux Processes

```bash
ps aux
```

Process tree:

```bash
ps -ef --forest
```


---

# Linux Services

```bash
systemctl --type=service --state=running
```

Service files:

```bash
systemctl list-unit-files --type=service
```


---

# Linux Timers

```bash
systemctl list-timers --all
```


---

# Linux Cron

```bash
cat /etc/crontab
```

```bash
ls -la /etc/cron.d/
```

User cron:

```bash
crontab -l
```


---

# Linux Users

```bash
cat /etc/passwd
```

Current groups:

```bash
groups
```

All groups:

```bash
getent group
```


---

# Interactive Linux Users

A simple filter for common interactive shells:

```bash
awk -F: '$7 ~ /(bash|zsh|sh|fish)$/ {print $1 ":" $7}' /etc/passwd
```

This is only an indicator because shell configuration varies.


---

# Linux Installed Packages

Debian-based systems:

```bash
dpkg -l
```

RPM-based systems:

```bash
rpm -qa
```

Use the package manager appropriate to the target.


---

# Linux Filesystems

```bash
df -h
```

Mounts:

```bash
findmnt
```

Block devices:

```bash
lsblk
```


---

# Mount Options

Review:

```text
noexec

nosuid

nodev

rw

ro
```

These can affect later privilege-escalation and execution decisions.


---

# Phase 3 - Network Discovery

Network discovery should answer:

```text
Which interfaces exist?

Which networks are directly connected?

Which routes exist?

Which DNS servers are configured?

Which services are listening locally?

Which systems are already known?

Which internal networks are reachable?
```


---

# Windows Network Configuration

```powershell
Get-NetIPConfiguration
```

Addresses:

```powershell
Get-NetIPAddress
```

Interfaces:

```powershell
Get-NetAdapter
```


---

# Windows Routes

```powershell
Get-NetRoute |
    Sort-Object DestinationPrefix
```

Traditional:

```cmd
route print
```


---

# Windows DNS

```powershell
Get-DnsClientServerAddress
```

DNS suffixes:

```powershell
Get-DnsClient |
    Select-Object InterfaceAlias,ConnectionSpecificSuffix
```


---

# Windows Listening Ports

```powershell
Get-NetTCPConnection -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess
```


---

# Map Port to Process

```powershell
Get-NetTCPConnection -State Listen |
    ForEach-Object {
        $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue

        [PSCustomObject]@{
            Address = $_.LocalAddress
            Port    = $_.LocalPort
            PID     = $_.OwningProcess
            Process = $process.ProcessName
        }
    }
```


---

# Windows Connections

```powershell
Get-NetTCPConnection |
    Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State,OwningProcess
```

Existing connections can reveal systems the host normally communicates with.


---

# ARP / Neighbour Cache

```powershell
Get-NetNeighbor
```

Traditional:

```cmd
arp -a
```

This may reveal recently observed local network neighbours.


---

# Linux Interfaces

```bash
ip addr
```

Compact:

```bash
ip -br addr
```


---

# Linux Routes

```bash
ip route
```


---

# Linux DNS

Depending on the environment:

```bash
cat /etc/resolv.conf
```

On systems using systemd-resolved:

```bash
resolvectl status
```


---

# Linux Listening Services

```bash
ss -lntup
```


---

# Linux Connections

```bash
ss -ntup
```

Existing connections may reveal:

```text
Database servers

Management servers

Proxies

Application backends

Monitoring systems

Directory services
```


---

# Linux Neighbours

```bash
ip neigh
```


---

# Network Discovery Model

```text
Current Host
    |
    +--> Interfaces
    |
    +--> Routes
    |
    +--> DNS
    |
    +--> Listening Services
    |
    +--> Existing Connections
    |
    +--> Neighbours
    |
    v
Reachable Networks
```


---

# Routes Are High-Value

Routes may reveal internal networks unavailable from the original operator system.

Example:

```text
10.10.10.0/24

172.16.20.0/24

192.168.50.0/24
```

This can indicate that the compromised host may later function as a pivot.

See:

[Lateral Movement](lateral-movement.md)


---

# Do Not Scan Every Route Automatically

Finding a route does not mean:

```text
Every host on that network is in scope.
```

Before scanning:

```text
Check scope

Check ROE

Check segmentation objectives

Select appropriate targets

Use conservative discovery
```


---

# Connectivity Validation

Windows:

```powershell
Test-NetConnection TARGET -Port 443
```

Linux:

```bash
nc -vz TARGET 443
```

Use known authorised hosts and ports when possible.


---

# Important Internal Ports

Common services include:

| Port | Typical Service |
|---:|---|
| 22 | SSH |
| 53 | DNS |
| 80 | HTTP |
| 88 | Kerberos |
| 135 | RPC |
| 389 | LDAP |
| 443 | HTTPS |
| 445 | SMB |
| 464 | Kerberos password change |
| 636 | LDAPS |
| 1433 | Microsoft SQL Server |
| 3306 | MySQL |
| 3389 | RDP |
| 5432 | PostgreSQL |
| 5985 | WinRM HTTP |
| 5986 | WinRM HTTPS |

Port numbers are indicators rather than proof of protocol.


---

# Targeted Internal Validation

When authorised, a targeted Nmap scan can validate selected systems:

```bash
nmap -sT -Pn -sV -p 22,80,443,445,3389,5985,5986 192.0.2.10
```

Avoid unnecessary broad scanning when existing host information already answers the question.


---

# Phase 4 - Identity Discovery

Identity discovery determines:

```text
Who is the current user?

Which local groups exist?

Which domain groups apply?

Which sessions exist?

Which service identities exist?

Which administrative identities interact with this host?
```


---

# Windows Current Identity

```powershell
whoami /all
```


---

# Windows Local Groups

```powershell
Get-LocalGroup
```

Administrators:

```powershell
Get-LocalGroupMember -Group Administrators
```


---

# Domain Membership

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain
```


---

# Domain User Context

```cmd
whoami /fqdn
```

```cmd
whoami /user
```

```cmd
whoami /groups
```


---

# Kerberos Tickets

Windows includes:

```cmd
klist
```

This can show Kerberos tickets associated with the current logon session.

Useful information can include:

```text
Client identity

Service principal

Ticket validity

Kerberos realm
```

Treat authentication material carefully.


---

# Linux Identity

```bash
id
```

Logged-in users:

```bash
who
```

Recent login information where authorised:

```bash
last
```


---

# Identity Discovery Questions

Ask:

```text
Is this a normal user?

Is this a service account?

Is this an administrator?

Is the identity domain joined?

What groups apply?

Are privileged sessions present?

What systems does this identity normally access?
```


---

# Phase 5 - Active Directory Discovery

If the host is domain joined, Active Directory becomes a major discovery source.

Determine:

```text
Domain name

Domain controllers

DNS domain

Current user

Current computer

Groups

Trusts

Organisational structure

Privileged groups

Service accounts

Delegation

AD CS

GPO
```


---

# Domain Name

```powershell
$env:USERDNSDOMAIN
```

Or:

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Domain
```


---

# Domain Controller Discovery

Built-in Windows tooling:

```cmd
nltest /dsgetdc:%USERDNSDOMAIN%
```

List domain controllers:

```cmd
nltest /dclist:%USERDNSDOMAIN%
```


---

# DNS SRV Records

Domain controllers can also be discovered through DNS.

```powershell
Resolve-DnsName -Type SRV "_ldap._tcp.dc._msdcs.$env:USERDNSDOMAIN"
```


---

# LDAP and Kerberos

Typical domain services include:

```text
53   DNS

88   Kerberos

389  LDAP

445  SMB

464  Kerberos password services

636  LDAPS
```


---

# Built-In Domain Enumeration

Current domain information:

```cmd
net user /domain
```

Domain groups:

```cmd
net group /domain
```

Domain administrators:

```cmd
net group "Domain Admins" /domain
```

Use targeted queries rather than collecting unnecessary directory information.


---

# PowerShell AD Module

If the ActiveDirectory module is legitimately installed:

```powershell
Get-Module -ListAvailable ActiveDirectory
```

Domain:

```powershell
Get-ADDomain
```

Domain controllers:

```powershell
Get-ADDomainController -Filter *
```

Groups:

```powershell
Get-ADGroup -Filter * |
    Select-Object Name
```

Large directory queries should be performed only when justified.


---

# BloodHound

[BloodHound](../active-directory/bloodhound.md) can help analyse Active Directory relationships.

Examples include:

```text
Group membership

Administrative rights

Sessions

ACLs

Delegation

Trusts

Certificate relationships
```

Use collection modes appropriate to the Rules of Engagement.


---

# BloodHound Model

```text
Current User
     |
     v
Group Membership
     |
     v
Permissions
     |
     v
Computers
     |
     v
Sessions
     |
     v
Privileged Identity
```


---

# BloodHound Is Analysis, Not Proof

A path such as:

```text
User -> Group -> Computer -> Session -> Admin
```

represents relationships.

Validate:

```text
Current permissions

Reachability

Authentication

Host state

Security controls

Scope
```

before treating the path as confirmed.


---

# Domain Trust Discovery

Trusts can influence attack paths.

Built-in query:

```cmd
nltest /domain_trusts
```

See:

[Active Directory Trusts](../active-directory/trusts.md)


---

# Group Discovery

Important groups may include:

```text
Domain Admins

Enterprise Admins

Administrators

Server Operators

Backup Operators

Account Operators

DNSAdmins

Custom administrative groups
```

Custom groups often matter as much as built-in groups.


---

# Service Accounts

Service accounts may be visible through:

```text
Windows services

Scheduled tasks

IIS application pools

SQL services

Domain objects

Application configuration
```

Service accounts can connect:

```text
Host Discovery
      |
      v
Credential Access
      |
      v
Lateral Movement
      |
      v
Privilege Escalation
```


---

# Group Managed Service Accounts

gMSAs may exist in modern Active Directory environments.

See:

[gMSA](../active-directory/gmsa.md)


---

# LAPS

Windows LAPS may manage local administrator passwords.

See:

[LAPS](../active-directory/laps.md)

Its presence generally represents a security improvement when correctly configured.


---

# Group Policy

GPOs can reveal:

```text
Security configuration

Scripts

Software deployment

Application control

Firewall policy

Administrative settings
```

See:

[Group Policy](../active-directory/group-policy.md)


---

# AD CS Discovery

Determine whether Active Directory Certificate Services exists.

Possible indicators include:

```text
Enterprise CA

Certificate templates

Certificate enrolment infrastructure

Certificate-related Active Directory objects
```

See:

[Active Directory Certificate Services](../active-directory/ad-cs/)


---

# Phase 6 - Security-Control Discovery

Understanding defensive controls is a normal part of red team situational awareness.

The objective should be:

```text
Understand the defensive environment
```

rather than:

```text
Immediately disable the defensive environment
```


---

# Security-Control Categories

Look for:

```text
Antivirus

EDR

Application control

Host firewall

PowerShell restrictions

AMSI

ASR

Credential protection

Disk encryption

Logging

SIEM agents

Network security agents
```


---

# Microsoft Defender

```powershell
Get-MpComputerStatus
```

Useful fields:

```powershell
Get-MpComputerStatus |
    Select-Object AntivirusEnabled,
                  RealTimeProtectionEnabled,
                  BehaviorMonitorEnabled,
                  IoavProtectionEnabled
```


---

# Defender Preferences

```powershell
Get-MpPreference
```

Do not alter configuration merely because it can be queried.


---

# ASR

```powershell
Get-MpPreference |
    Select-Object AttackSurfaceReductionRules_Ids,
                  AttackSurfaceReductionRules_Actions
```


---

# PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```


---

# AppLocker

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```


---

# AppLocker Detailed Policy

```powershell
Get-AppLockerPolicy -Effective
```


---

# Code Integrity

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 20
```


---

# Windows Firewall

Profiles:

```powershell
Get-NetFirewallProfile |
    Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction
```

This helps understand host network boundaries.


---

# BitLocker

```powershell
Get-BitLockerVolume -ErrorAction SilentlyContinue
```

Disk encryption is generally relevant to physical/offline access rather than ordinary live-session privilege.


---

# Credential Guard

Credential Guard and LSA protections may materially affect credential-access paths.

Record their presence where relevant rather than assuming credential extraction techniques will work.

See:

[Credential Access](credential-access.md)


---

# Linux Security Controls

Possible controls include:

```text
SELinux

AppArmor

auditd

EDR

Host firewall

Container security

sudo policy
```


---

# SELinux

```bash
getenforce 2>/dev/null
```

Possible results:

```text
Enforcing

Permissive

Disabled
```


---

# AppArmor

```bash
aa-status 2>/dev/null
```

If the command exists and permissions allow it.


---

# Linux Firewall

nftables:

```bash
sudo -n nft list ruleset 2>/dev/null
```

iptables where relevant:

```bash
sudo -n iptables -L -n 2>/dev/null
```

If the current account lacks permission, record that rather than forcing access.


---

# auditd

```bash
systemctl status auditd
```

Rules where authorised:

```bash
auditctl -l
```


---

# Security-Control Discovery Model

```text
Host
 |
 +--> Antivirus
 |
 +--> EDR
 |
 +--> Application Control
 |
 +--> Firewall
 |
 +--> Logging
 |
 +--> Identity Protection
 |
 +--> Script Controls
 |
 v
Defensive Posture
```


---

# Do Not Infer Too Much from Process Names

A security-agent process may be:

```text
Running

Partially functional

Disconnected

Misconfigured

Healthy
```

Likewise, absence of an obvious process does not prove the host lacks EDR.

Correlate multiple sources.


---

# Phase 7 - Application Discovery

Applications can reveal important business systems.

Look for:

```text
Web applications

Databases

Management software

Backup systems

File-transfer applications

Development tools

Administrative consoles

Custom business applications
```


---

# Windows Application Indicators

Sources include:

```text
Installed software

Services

Processes

Scheduled tasks

Listening ports

Configuration files

Browser bookmarks
```

Avoid collecting unrelated personal browser information.


---

# Linux Application Indicators

Sources include:

```text
Processes

systemd services

Listening sockets

Packages

Configuration directories

Web server configuration

Container configuration
```


---

# Web Server Discovery

Possible software includes:

```text
IIS

Apache

nginx

Tomcat

Node.js

Python application servers
```

The presence of a web server may indicate an internal application worth mapping.


---

# IIS

On Windows:

```powershell
Get-Service W3SVC -ErrorAction SilentlyContinue
```

If IIS administration modules are installed and access is authorised, additional site configuration may be available.


---

# Apache and nginx

Linux processes:

```bash
ps aux | grep -E '[a]pache2|[h]ttpd|[n]ginx'
```

Listening ports:

```bash
ss -lntp
```


---

# Database Discovery

Common databases include:

```text
Microsoft SQL Server

PostgreSQL

MySQL

MariaDB

Oracle

MongoDB
```

Processes and listening services can identify candidate database systems.


---

# Database Ports

Typical defaults include:

| Port | Service |
|---:|---|
| 1433 | Microsoft SQL Server |
| 1521 | Oracle |
| 3306 | MySQL/MariaDB |
| 5432 | PostgreSQL |
| 27017 | MongoDB |

Applications may use non-default ports.


---

# Configuration Discovery

Configuration files can contain:

```text
Server names

Database endpoints

API URLs

Authentication providers

Service accounts

Cloud resource names
```

Handle secrets separately under the credential-access methodology.


---

# Phase 8 - Share Discovery

File shares can reveal:

```text
Department data

Deployment files

Scripts

Software

Configuration

Administrative resources
```

Discovery should not become bulk collection.


---

# Windows Shares

Local shares:

```powershell
Get-SmbShare
```

Traditional:

```cmd
net share
```


---

# Remote Share Discovery

For a known authorised server:

```cmd
net view \\SERVER
```

Do not enumerate arbitrary servers simply because their names were discovered.


---

# Share Access Model

```text
Share Discovered
      |
      v
In Scope?
      |
      v
Current User Has Access?
      |
      v
Objective-Relevant?
      |
      v
Minimal Review
```


---

# Active Directory Shares

See:

[Active Directory Shares](../active-directory/shares.md)

Shares may become relevant to:

```text
Credential exposure

Deployment scripts

Lateral movement

Objective data
```


---

# Phase 9 - Virtualisation Discovery

Determine whether the system is:

```text
Physical

Virtual machine

Cloud VM

Container

VDI
```


---

# Windows Virtualisation Indicators

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Manufacturer,Model
```

Possible indicators may reference:

```text
VMware

VirtualBox

Hyper-V

Cloud vendors
```

Treat these as architecture information.


---

# Linux Virtualisation

Where available:

```bash
systemd-detect-virt
```

Possible results include:

```text
kvm

vmware

microsoft

docker

none
```


---

# Why Virtualisation Matters

It can help explain:

```text
Network architecture

Management interfaces

Cloud identity

Snapshot behaviour

Container boundaries

Host/guest relationships
```


---

# Phase 10 - Container Discovery

Containers introduce another security boundary.

Determine:

```text
Am I in a container?

Which runtime exists?

What permissions exist?

Which volumes are mounted?

Which networks exist?

Is host-management access available?
```


---

# Docker Indicator

```bash
test -f /.dockerenv && echo "Docker indicator present"
```


---

# cgroup Information

```bash
cat /proc/1/cgroup
```


---

# Docker CLI

If legitimately available:

```bash
docker version
```

Containers:

```bash
docker ps
```

Only use the daemon if the current identity is authorised to do so.


---

# Docker Socket

```bash
ls -l /var/run/docker.sock
```

Access to the Docker daemon can represent a major security boundary.

See:

[Linux Privilege Escalation](../linux/privilege-escalation.md)


---

# Container Networks

If authorised:

```bash
docker network ls
```

Container network architecture may reveal internal application relationships.


---

# Kubernetes Discovery

Possible indicators include:

```text
KUBERNETES_SERVICE_HOST

Service-account paths

kubectl configuration

Container environment variables
```

Check:

```bash
env | grep -i kubernetes
```

Do not access cluster resources beyond authorised scope.


---

# Phase 11 - Cloud Discovery

Cloud-connected hosts may expose context about:

```text
Cloud provider

Subscription/account/project

Managed identity

Instance role

Storage

Secrets

Management agents

Cloud networking
```


---

# Cloud Discovery Principles

Do not automatically query metadata endpoints simply because a cloud provider is suspected.

First determine:

```text
Cloud testing is in scope?

Metadata interaction is permitted?

Current host belongs to customer?

Identity testing is permitted?
```


---

# Cloud Environment Indicators

Environment variables:

Windows:

```powershell
Get-ChildItem Env:
```

Linux:

```bash
env
```

Look for application and platform indicators without assuming exposed variables are credentials.


---

# Cloud CLI Discovery

Possible clients:

```text
aws

az

gcloud
```

Linux:

```bash
command -v aws
command -v az
command -v gcloud
```

PowerShell:

```powershell
Get-Command aws -ErrorAction SilentlyContinue
Get-Command az -ErrorAction SilentlyContinue
Get-Command gcloud -ErrorAction SilentlyContinue
```


---

# Cloud Configuration

User profiles may contain legitimate CLI configuration.

Examples include:

```text
AWS configuration

Azure CLI context

Google Cloud configuration
```

Treat tokens and credentials as sensitive material.


---

# Phase 12 - Security Boundary Discovery

At this stage, transform raw observations into security boundaries.

Examples:

```text
Standard User -> Administrator

Workstation -> Server

User VLAN -> Management VLAN

Domain User -> Privileged Group

Container -> Host

Application User -> Administrator

On-Premises -> Cloud

Normal Account -> Service Account
```


---

# Boundary Model

```text
Current Context
      |
      v
Observed Relationship
      |
      v
Security Boundary
      |
      v
Required Preconditions
      |
      v
Candidate Attack Path
```


---

# Example

Discovery identifies:

```text
Current host:
WS01

Current user:
CORP\user1

Domain:
corp.example

Route:
10.20.0.0/16

Existing connection:
APP01:443

Local group:
No administrative membership

PowerShell:
FullLanguage

Application control:
Enabled

Domain:
AD environment present
```

This does not yet prove compromise of another system.

It provides the context needed to choose the next tests.


---

# Phase 13 - Attack-Path Prioritisation

Prioritise discovered information based on engagement objectives.

High-value categories often include:

```text
Privileged identities

Administrative systems

Domain controllers

Certificate authorities

Management servers

Backup infrastructure

Identity providers

Cloud management

Database systems

Deployment infrastructure

Security tooling

Objective systems
```


---

# Crown Jewels

The Rules of Engagement may identify systems such as:

```text
Domain controllers

Payment systems

Customer databases

Source-code repositories

Identity infrastructure

Cloud control plane

Backup infrastructure
```

Discovery should help determine a path toward these objectives without unnecessarily compromising unrelated systems.


---

# Prioritisation Model

```text
Discovered Asset
      |
      v
In Scope?
   /      \
 No        Yes
 |          |
Stop        v
       Objective Relevant?
         /         \
       No           Yes
       |             |
       v             v
   Low Priority   Reachable?
                  /      \
                No        Yes
                |          |
                v          v
              Record    Privilege /
                        Credential
                         Relationship?
                          /       \
                        No         Yes
                        |           |
                        v           v
                     Review     High Priority
```


---

# Discovery and Privilege Escalation

Discovery may reveal:

```text
Writable service resources

Interesting privileges

Sudo rules

SUID binaries

Capabilities

Scheduled tasks

Container-management access
```

See:

[Privilege Escalation](privilege-escalation.md)

[PrivEsc Explorer](../privesc/)


---

# Discovery and Credential Access

Discovery may identify potential credential locations without accessing them.

Examples:

```text
Service accounts

Configuration files

Credential Manager

SSH directories

Environment variables

Cloud CLI configuration
```

See:

[Credential Access](credential-access.md)


---

# Discovery and Lateral Movement

Discovery may identify:

```text
Remote hosts

Administrative protocols

Existing connections

Routes

Domain computers

Shares

Remote-management services
```

See:

[Lateral Movement](lateral-movement.md)


---

# Discovery and C2

Network discovery helps determine:

```text
Outbound connectivity

DNS configuration

Proxy configuration

Segmentation

Reachable management infrastructure
```

See:

[Command and Control](command-and-control.md)


---

# Discovery and Persistence

Discovery may identify legitimate mechanisms such as:

```text
Scheduled tasks

Services

Startup locations

Cron

systemd

Cloud automation
```

See:

[Persistence](persistence.md)


---

# Discovery and Defence Evasion

Security-control discovery provides context for defence-evasion validation.

See:

[Defence Evasion](defence-evasion.md)

The objective is to understand:

```text
Which controls exist?

Which controls apply?

Which events are generated?

Which behaviours are prevented?

Which behaviours are detected?
```


---

# Discovery and Collection

Discovery identifies where objective-relevant information may exist.

Collection should remain a separate decision.

```text
Discovery
    |
    v
Interesting Data Location
    |
    v
Objective Relevant?
    |
    v
Collection Decision
```

Do not automatically collect data merely because it was discovered.


---

# Detection Opportunities

Discovery activity can generate significant telemetry.

Potential sources include:

```text
Process creation

PowerShell

Command-line auditing

LDAP

SMB

DNS

Network connections

EDR

Active Directory logs

Cloud audit logs

SIEM
```


---

# Windows Process Telemetry

Commands such as:

```text
whoami

nltest

net

ipconfig

route

systeminfo

PowerShell CIM queries
```

may be visible through process telemetry.

Detection should normally consider behaviour and sequence rather than treating every administrative command as malicious.


---

# PowerShell Telemetry

Potential sources:

```text
Process creation

Script Block Logging

Module Logging

AMSI

Transcription

EDR
```

Review:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-PowerShell/Operational" -MaxEvents 50
```


---

# LDAP Discovery Telemetry

Large directory queries may produce:

```text
LDAP traffic

Directory-service query patterns

EDR telemetry

Network telemetry

Identity analytics
```

This is one reason targeted directory discovery is preferable to unnecessary bulk enumeration.


---

# Network Discovery Telemetry

Defenders may observe:

```text
Sequential connections

Port sweeps

DNS queries

SMB enumeration

LDAP queries

Authentication attempts
```

Use the least amount of activity required to answer the engagement question.


---

# Discovery Detection Hypothesis

Example:

```text
Hypothesis:
A compromised workstation performing unusual domain and network
discovery should generate sufficient telemetry for the SOC to
identify suspicious situational-awareness activity.

Test:
Perform a small approved sequence of host, identity and domain
discovery actions.

Expected:
Endpoint telemetry and relevant network activity are collected.

Result:
Record whether telemetry, detection and analyst response occur.
```


---

# Detection Outcome

Classify:

```text
Prevented

Detected

Logged

No Alert

No Useful Visibility
```


---

# Evidence

Discovery evidence should remain concise.

Capture:

```text
Test ID

Host

User

Timestamp

Command/query

Relevant result

Security significance

Scope status
```


---

# Example Evidence Record

```text
Evidence ID:
DISC-011

Host:
WS01

User:
CORP\test-user

Observation:
The workstation is joined to corp.example.

Domain Controller:
DC01.corp.example

Source:
DNS SRV lookup and nltest

Security Significance:
Confirms Active Directory environment and identifies the
authoritative domain infrastructure.

Scope:
Domain infrastructure confirmed in scope.
```


---

# Network Evidence Example

```text
Evidence ID:
DISC-019

Host:
APP01

Observation:
The host contains a route to 10.20.30.0/24 that was not directly
reachable from the operator network.

Security Significance:
The host provides network reachability into an additional internal
segment.

Validation:
No broad scanning was performed until scope was confirmed.
```


---

# Security-Control Evidence Example

```text
Evidence ID:
DISC-024

Host:
WS01

Observation:
Microsoft Defender real-time protection was enabled.

AppLocker:
Executable and script collections enabled.

PowerShell:
FullLanguage.

Security Significance:
Provides context for later execution and defence-evasion
validation.
```


---

# Candidate vs Finding

Most discovery observations are not findings.

Examples:

```text
Domain controller discovered
```

is architecture information.

```text
Microsoft Defender present
```

is architecture information.

```text
Internal route discovered
```

is architecture information.

A finding requires a security-relevant weakness.


---

# Example Finding - Excessive Network Reachability

```text
Title:
User Workstations Can Directly Reach Administrative Server Network

Observation:
During post-compromise discovery, the assessment workstation was
found to have direct network reachability to the administrative
server segment.

Selected management services on authorised systems were reachable
from the standard workstation network.

Impact:
An attacker who compromises a normal user workstation may be able
to directly interact with higher-value server infrastructure,
increasing opportunities for credential-based lateral movement
and further compromise.

Recommendation:
Review network segmentation between workstation and administrative
server networks. Permit only explicitly required flows and monitor
administrative protocols crossing security zones.
```


---

# Example Finding - Excessive Information Exposure

```text
Title:
Application Configuration Exposes Internal Infrastructure Details

Observation:
A configuration file accessible to the standard assessment user
contained internal server names, service endpoints and environment
information.

No credential material was required to demonstrate the issue.

Impact:
The information significantly reduces the discovery effort
required after initial compromise and provides an attacker with
direct knowledge of internal application dependencies.

Recommendation:
Restrict access to sensitive configuration information and remove
unnecessary infrastructure details from files accessible to
standard users.
```


---

# Common Discovery Mistakes

## Running Everything Immediately

Avoid:

```text
Run every enumeration tool

Scan every subnet

Query every AD object

Enumerate every share
```

Start with context and expand only when justified.


---

## Treating Information as Vulnerability

Example:

```text
Domain Admins group exists
```

is not a vulnerability.


---

## Ignoring Existing Connections

Existing connections can be more useful than scanning.

They reveal systems the host already communicates with.


---

## Ignoring Routes

Routes often explain where the host can reach and whether pivoting may be possible.


---

## Ignoring DNS

Internal DNS can reveal:

```text
Domains

Domain controllers

Application servers

Management systems

Service records
```


---

## Ignoring Security Controls

Knowing which controls are active is necessary to correctly interpret later execution and detection results.


---

## Over-Collecting

Do not collect:

```text
Entire user profiles

All documents

All shares

All browser data

Every domain object
```

unless specifically required and authorised.


---

## Trusting Automated Enumeration Blindly

Automated tools produce candidates.

Always validate important observations manually.


---

# Automated Discovery Tools

Tools commonly used in authorised assessments include:

```text
Seatbelt

WinPEAS

SharpHound

BloodHound

LinPEAS

LinEnum

NetExec

Nmap
```

Each can generate substantial telemetry and output.


---

# Tool Selection Model

```text
Question
   |
   v
Can Built-In Tool Answer?
   /              \
 Yes               No
 |                  |
 v                  v
Use Built-In     Specialist Tool
                     |
                     v
                 Scope / Risk
                     |
                     v
                    Run
```


---

# Built-In First

Built-in commands are often sufficient for initial discovery.

Advantages:

```text
Less deployment

Lower operational complexity

Easier cleanup

Clearer evidence

Reduced tooling dependency
```

Specialist tools remain useful when they provide justified additional value.


---

# Discovery Inventory

Maintain structured notes.

Example:

| Category | Observation | Confidence | Relevance |
|---|---|---|---|
| Host | Windows workstation | Confirmed | High |
| Identity | Domain user | Confirmed | High |
| Domain | `corp.example` | Confirmed | High |
| DC | `DC01` | Confirmed | High |
| EDR | Defender present | High | High |
| Route | `10.20.30.0/24` | Confirmed | High |
| Service | Internal HTTPS app | Confirmed | Medium |
| Cloud | Azure indicators | Medium | Medium |


---

# Discovery Timeline

Record important changes in understanding.

Example:

```text
09:14 - Foothold established on WS01
09:16 - Domain membership confirmed
09:18 - DC01 identified through DNS
09:22 - Additional internal route identified
09:27 - AppLocker policy reviewed
09:34 - Internal APP01 identified from existing connection
09:41 - Scope confirmed for APP01
09:45 - Targeted connectivity validation performed
```


---

# Discovery Checklist

## Context

- [ ] Hostname recorded
- [ ] Current user recorded
- [ ] Groups recorded
- [ ] Privileges recorded
- [ ] Operating system recorded
- [ ] Architecture recorded
- [ ] Domain/workgroup recorded
- [ ] Shell recorded
- [ ] Timestamp recorded

## Host

- [ ] Processes reviewed
- [ ] Services reviewed
- [ ] Scheduled execution reviewed
- [ ] Installed applications reviewed
- [ ] Local users reviewed
- [ ] Local groups reviewed
- [ ] Current sessions reviewed where relevant
- [ ] Drives/mounts reviewed

## Network

- [ ] Interfaces reviewed
- [ ] Addresses recorded
- [ ] Routes reviewed
- [ ] DNS servers reviewed
- [ ] Listening ports reviewed
- [ ] Existing connections reviewed
- [ ] Neighbours reviewed where useful
- [ ] Additional networks recorded
- [ ] Scope checked before active scanning

## Identity

- [ ] Current identity understood
- [ ] Local group membership reviewed
- [ ] Domain identity reviewed
- [ ] Kerberos context reviewed where relevant
- [ ] Service identities identified where relevant
- [ ] Privileged sessions handled carefully

## Active Directory

- [ ] Domain identified
- [ ] Domain controllers identified
- [ ] DNS domain understood
- [ ] Relevant groups reviewed
- [ ] Trusts reviewed where relevant
- [ ] GPO considered
- [ ] AD CS considered
- [ ] BloodHound considered where authorised
- [ ] Bulk enumeration avoided unless justified

## Security Controls

- [ ] Antivirus reviewed
- [ ] EDR considered
- [ ] Application control reviewed
- [ ] PowerShell language mode reviewed
- [ ] ASR reviewed where applicable
- [ ] Host firewall reviewed
- [ ] Logging considered
- [ ] Credential protections considered

## Applications

- [ ] Business applications identified
- [ ] Web servers identified
- [ ] Database services identified
- [ ] Management applications identified
- [ ] Backup systems considered
- [ ] Configuration locations identified
- [ ] Secrets handled under credential-access procedures

## Linux

- [ ] Processes reviewed
- [ ] Services reviewed
- [ ] Cron reviewed
- [ ] systemd timers reviewed
- [ ] Users/groups reviewed
- [ ] Sudo reviewed
- [ ] Mounts reviewed
- [ ] Listening sockets reviewed
- [ ] Security controls reviewed
- [ ] Container context reviewed

## Cloud and Containers

- [ ] Cloud indicators reviewed
- [ ] Cloud scope confirmed
- [ ] CLI tools identified
- [ ] Container context determined
- [ ] Docker access reviewed where applicable
- [ ] Kubernetes indicators reviewed where applicable
- [ ] Host/container boundary understood

## Evidence

- [ ] Relevant observations recorded
- [ ] Confidence recorded
- [ ] Scope status recorded
- [ ] Sensitive information minimised
- [ ] Candidate paths documented
- [ ] Discovery timeline maintained


---

# Quick Reference - Windows

## Identity

```powershell
whoami /all
```


## System

```powershell
Get-CimInstance Win32_OperatingSystem |
    Select-Object Caption,Version,BuildNumber,OSArchitecture
```


## Domain

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain
```


## Processes

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,ExecutablePath
```


## Services

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,StartMode,PathName
```


## Scheduled Tasks

```powershell
Get-ScheduledTask |
    Select-Object TaskName,TaskPath,State
```


## Network

```powershell
Get-NetIPConfiguration
```


## Routes

```powershell
Get-NetRoute |
    Sort-Object DestinationPrefix
```


## DNS

```powershell
Get-DnsClientServerAddress
```


## Listening Ports

```powershell
Get-NetTCPConnection -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess
```


## Connections

```powershell
Get-NetTCPConnection |
    Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State,OwningProcess
```


## Neighbours

```powershell
Get-NetNeighbor
```


## Domain Controller

```cmd
nltest /dsgetdc:%USERDNSDOMAIN%
```


## Domain Controllers

```cmd
nltest /dclist:%USERDNSDOMAIN%
```


## Domain Trusts

```cmd
nltest /domain_trusts
```


## Kerberos Tickets

```cmd
klist
```


## Defender

```powershell
Get-MpComputerStatus
```


## AppLocker

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```


## PowerShell Language Mode

```powershell
$ExecutionContext.SessionState.LanguageMode
```


---

# Quick Reference - Linux

## Identity

```bash
id
```


## System

```bash
uname -a
```


## Distribution

```bash
cat /etc/os-release
```


## Processes

```bash
ps aux
```


## Services

```bash
systemctl --type=service --state=running
```


## Timers

```bash
systemctl list-timers --all
```


## Network

```bash
ip -br addr
```


## Routes

```bash
ip route
```


## DNS

```bash
cat /etc/resolv.conf
```


## Listening Services

```bash
ss -lntup
```


## Connections

```bash
ss -ntup
```


## Neighbours

```bash
ip neigh
```


## Sudo

```bash
sudo -l
```


## Filesystems

```bash
findmnt
```


## SELinux

```bash
getenforce 2>/dev/null
```


## AppArmor

```bash
aa-status 2>/dev/null
```


## Virtualisation

```bash
systemd-detect-virt
```


## Container Indicator

```bash
test -f /.dockerenv && echo "Docker indicator present"
```


---

# Discovery Decision Model

```text
                     Foothold
                        |
                        v
                 Establish Context
                        |
                        v
                  Local Discovery
                        |
                        v
               Security Controls
                        |
                        v
                 Network Context
                        |
                        v
                Identity Context
                        |
                        v
                  Domain Joined?
                   /         \
                 No           Yes
                 |             |
                 v             v
             Local Path     AD Discovery
                 |             |
                 +------+------+
                        |
                        v
                 Candidate Asset
                        |
                        v
                    In Scope?
                    /      \
                  No        Yes
                  |          |
                 STOP        v
                      Objective Relevant?
                        /         \
                      No           Yes
                      |             |
                    Record          v
                              Validate Path
                                   |
                                   v
                              Next Technique
```


---

# Host Discovery Model

```text
                       HOST
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
     Identity        Processes       Network
        |               |               |
        v               v               v
    Privileges       Services         Routes
        |               |               |
        v               v               v
      Groups          Tasks            DNS
        |               |               |
        +---------------+---------------+
                        |
                        v
                Security Controls
                        |
                        v
                 Attack Context
```


---

# Internal Discovery Model

```text
                     CURRENT HOST
                          |
                          v
                       ROUTES
                          |
                          v
                    INTERNAL DNS
                          |
                          v
                 KNOWN CONNECTIONS
                          |
                          v
                    DOMAIN DATA
                          |
                          v
                  RELEVANT SYSTEMS
                          |
             +------------+------------+
             |                         |
             v                         v
       Privilege Path             Lateral Path
             |                         |
             +------------+------------+
                          |
                          v
                       OBJECTIVE
```


---

# Defensive Discovery Model

```text
                   Discovery Activity
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
       Endpoint         Network         Identity
          |               |               |
          v               v               v
       Process           DNS            LDAP
       PowerShell        SMB            Kerberos
       EDR               Scans          Directory
          |               |               |
          +---------------+---------------+
                          |
                          v
                         SIEM
                          |
                          v
                       Detection
                          |
                          v
                        Response
```


---

# Final Discovery Model

```text
                     AUTHORISED FOOTHOLD
                              |
                              v
                        CURRENT CONTEXT
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
        HOST               NETWORK             IDENTITY
          |                   |                   |
          v                   v                   v
      SERVICES             ROUTES              DOMAIN
          |                   |                   |
          v                   v                   v
    APPLICATIONS             DNS              GROUPS
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                     SECURITY CONTROLS
                              |
                              v
                        ENVIRONMENT MAP
                              |
                              v
                       CANDIDATE PATHS
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
           PRIVESC        CREDENTIALS       LATERAL
              |               |               |
              +---------------+---------------+
                              |
                              v
                           OBJECTIVE
                              |
                              v
                           EVIDENCE
```


---

# Core Principle

Discovery can be reduced to:

```text
Understand where you are.

Understand who you are.

Understand what privilege you have.

Understand the host.

Understand the network.

Understand identity.

Understand the domain.

Understand applications.

Understand defensive controls.

Identify security boundaries.

Identify candidate attack paths.

Validate scope before expanding.

Prefer existing context over unnecessary scanning.

Collect only what supports the objective.

Record important observations.

Use discovery to decide what to test next.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Reconnaissance](reconnaissance.md)
- [Initial Access](initial-access.md)
- [Execution](execution.md)
- [Privilege Escalation](privilege-escalation.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Command and Control](command-and-control.md)
- [Detection Validation](detection-validation.md)
- [Red Team OPSEC](opsec.md)
- [Red Team Reporting](reporting.md)
- [Windows Enumeration](../windows/enumeration.md)
- [Linux Enumeration](../linux/enumeration.md)
- [Active Directory Enumeration](../active-directory/enumeration.md)
- [BloodHound](../active-directory/bloodhound.md)
- [Active Directory Shares](../active-directory/shares.md)
- [PrivEsc Explorer](../privesc/)


---

# References

- [MITRE ATT&CK - Discovery](https://attack.mitre.org/tactics/TA0007/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Information Discovery](https://attack.mitre.org/techniques/T1082/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Owner/User Discovery](https://attack.mitre.org/techniques/T1033/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Account Discovery](https://attack.mitre.org/techniques/T1087/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Permission Groups Discovery](https://attack.mitre.org/techniques/T1069/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Process Discovery](https://attack.mitre.org/techniques/T1057/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Network Configuration Discovery](https://attack.mitre.org/techniques/T1016/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Network Connections Discovery](https://attack.mitre.org/techniques/T1049/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Network Service Discovery](https://attack.mitre.org/techniques/T1046/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Remote System Discovery](https://attack.mitre.org/techniques/T1018/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - File and Directory Discovery](https://attack.mitre.org/techniques/T1083/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Software Discovery](https://attack.mitre.org/techniques/T1518/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Security Software Discovery](https://attack.mitre.org/techniques/T1518/001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Service Discovery](https://attack.mitre.org/techniques/T1007/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Query Registry](https://attack.mitre.org/techniques/T1012/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Virtualization/Sandbox Evasion](https://attack.mitre.org/techniques/T1497/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Commands](https://learn.microsoft.com/windows-server/administration/windows-commands/windows-commands){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Documentation](https://learn.microsoft.com/powershell/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Active Directory Domain Services](https://learn.microsoft.com/windows-server/identity/ad-ds/active-directory-domain-services){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Defender](https://learn.microsoft.com/defender-endpoint/microsoft-defender-antivirus-windows){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }
- [Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Discovery should answer a question"
    Before running a discovery command or tool, know what question it is intended to answer. If the result will not change the attack-path decision, the activity may not be necessary.


!!! warning "Discovery is not permission expansion"
    An internal hostname, subnet, domain, cloud resource, share, or administrative system becoming visible from a compromised host does not automatically bring that resource into scope. Revalidate the Rules of Engagement before expanding active testing.
