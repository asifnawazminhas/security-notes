---
title: Persistence
description: Persistence methodology for authorised red team assessments, covering Windows, Linux, Active Directory, cloud and application persistence, scheduled tasks, services, startup mechanisms, SSH keys, accounts, Kerberos, certificates, detection, evidence, cleanup, and remediation.
---

# Persistence

Persistence is the process of maintaining authorised access to a system, identity, application, or environment across events that might otherwise remove the original foothold.

Examples include:

```text
User logoff
Process termination
System reboot
Credential rotation
Service restart
Application restart
Temporary session expiry
```

A simplified model is:

```text
Initial Access
      |
      v
Foothold
      |
      v
Persistence Required?
    /       \
  No         Yes
  |           |
  v           v
Continue    Select
Without     Controlled
Persistence Mechanism
              |
              v
          Validate
              |
              v
          Document
              |
              v
           Cleanup
```

Persistence can create long-lived security impact and should only be tested when explicitly permitted by the Rules of Engagement.


---

# Persistence Objectives

Persistence testing should answer questions such as:

```text
Can an attacker maintain access?
Which security boundary enables persistence?
What privilege is required?
Does persistence survive reboot or logon?
Which identity or component is affected?
Was the modification detected?
Would defenders identify the persistence?
Can the change be reliably removed?
```

The objective is not to install every possible persistence mechanism.

Use the minimum persistence required to demonstrate the security control or attack path being assessed.


---

# Persistence vs Initial Access

Initial access establishes the first foothold.

Persistence attempts to retain access.

```text
Initial Access

External
   |
   v
Target


Persistence

Target
  |
  v
Access Survives
Security State Change
```

An engagement can successfully achieve its objectives without persistence.


---

# Persistence vs Privilege Escalation

Persistence and privilege escalation are also separate concepts.

```text
Persistence:
Keep existing access


Privilege Escalation:
Obtain greater privilege
```

A persistence mechanism may run with higher privileges if installed from an already privileged context, but the persistence mechanism itself does not necessarily create that privilege.


---

# Persistence vs C2

Persistence and command and control are different layers.

```text
Persistence
    |
    v
Starts Assessment Component
    |
    v
Command and Control
```

Persistence determines how access is re-established.

C2 determines how the controlled component communicates with the operator.


---

# Persistence Lifecycle

A useful persistence lifecycle is:

```text
Requirement
    |
    v
Select Mechanism
    |
    v
Record Original State
    |
    v
Deploy
    |
    v
Validate
    |
    v
Measure Detection
    |
    v
Use Only as Required
    |
    v
Remove
    |
    v
Verify Original State
```


---

# Before Testing Persistence

Confirm:

```text
Persistence is explicitly permitted
Target is in scope
Current privilege is understood
Mechanism is permitted
Reboot testing is permitted
Account creation is permitted
Credential modification is permitted
Cloud modification is permitted
Directory modification is permitted
Cleanup procedure is known
Emergency contact is available
```

Persistence testing should always have a cleanup plan before deployment.


---

# Persistence Inventory

Maintain an inventory of every persistence change.

Example:

| ID | Host | Mechanism | Location | Created | Cleanup |
|---|---|---|---|---|---|
| `PERS-001` | `TEST-WKS01` | Scheduled task | Task Scheduler | Yes | Required |
| `PERS-002` | `TEST-LNX01` | systemd unit | `/etc/systemd/system/` | Yes | Required |
| `PERS-003` | Test account | SSH key | `authorized_keys` | Yes | Required |

Do not rely on memory for cleanup.


---

# Record Original State

Before changing a persistence location, record its existing state.

For example:

```text
Original file
Original permissions
Original registry value
Original task configuration
Original service configuration
Original account membership
Original SSH authorized_keys
Original cloud role assignment
```

This makes reliable restoration possible.


---

# Windows Persistence

Windows provides many legitimate mechanisms that can start software or maintain access.

Common categories include:

```text
Scheduled tasks
Services
Run keys
Startup folders
User accounts
Group membership
PowerShell profiles
WMI event subscriptions
Application-specific startup
Logon scripts
Authentication material
Remote-management configuration
```


---

# Windows Persistence Model

```text
Windows Persistence
       |
       +--> Scheduled Tasks
       |
       +--> Services
       |
       +--> Registry
       |
       +--> Startup
       |
       +--> Accounts
       |
       +--> PowerShell
       |
       +--> WMI
       |
       +--> Application
       |
       +--> Active Directory
```


---

# Scheduled Tasks

Windows Task Scheduler can execute programs:

```text
At startup
At logon
At a specific time
On an event
On a repeating schedule
```

Enumerate:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

A scheduled task can be legitimate administration or a persistence mechanism depending on context.


---

# Inspect a Scheduled Task

PowerShell:

```powershell
Get-ScheduledTask -TaskName 'TASKNAME'
```

Review actions:

```powershell
(Get-ScheduledTask -TaskName 'TASKNAME').Actions
```

Review:

```text
Task name
Execution identity
Trigger
Action
Arguments
Executable
Working directory
Privilege level
```


---

# Scheduled Task Persistence Assessment

A persistence path can be represented as:

```text
Trigger
   |
   v
Scheduled Task
   |
   v
Configured Action
   |
   v
Assessment Component
```

Important questions include:

```text
Who can create the task?
Who can modify it?
Which identity executes it?
Does it survive reboot?
Is task creation monitored?
Is the action protected from modification?
```


---

# Safe Scheduled Task Validation

Where task creation is explicitly authorised, prefer a harmless proof such as writing a marker file rather than launching a remote-access component.

Example PowerShell:

```powershell
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c echo PersistenceTest > C:\Windows\Temp\persistence-test.txt'
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2)
Register-ScheduledTask -TaskName 'Assessment-Persistence-Test' -Action $action -Trigger $trigger -Description 'Authorised security assessment persistence validation'
```

Verify:

```powershell
Get-ScheduledTask -TaskName 'Assessment-Persistence-Test'
```

After the test:

```powershell
Unregister-ScheduledTask -TaskName 'Assessment-Persistence-Test' -Confirm:$false
```

Remove the marker:

```powershell
Remove-Item 'C:\Windows\Temp\persistence-test.txt' -ErrorAction SilentlyContinue
```


---

# Windows Services

Services can provide persistence because they can start:

```text
Automatically at boot
On demand
Through service dependencies
Through administrative action
```

Enumerate:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, State, StartMode, PathName
```

Services should be assessed together with:

```text
Service permissions
Executable permissions
Directory permissions
Service identity
Startup mode
Configuration protection
```


---

# Service Persistence Model

```text
System Boot
    |
    v
Service Control Manager
    |
    v
Service
    |
    v
Configured Executable
```

A service running as `LocalSystem` represents a particularly sensitive persistence location.


---

# Service Creation

Service creation is a significant system modification.

Where explicitly authorised, a benign test service can validate whether the current security context can create a persistent service without deploying an operational payload.

Example:

```cmd
sc.exe create AssessmentPersistenceTest binPath= "C:\Windows\System32\cmd.exe /c exit 0" start= demand
```

Inspect:

```cmd
sc.exe qc AssessmentPersistenceTest
```

Remove:

```cmd
sc.exe delete AssessmentPersistenceTest
```

Use unique assessment names to make cleanup and detection correlation easier.


---

# Registry Run Keys

Windows supports programs that run when users log on.

Common locations include:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run

HKLM\Software\Microsoft\Windows\CurrentVersion\Run
```

Enumerate:

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
```

System-wide:

```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run'
```

The current-user location generally affects that user, while machine-level locations can have broader impact depending on configuration.


---

# Run Key Validation

Where modification is authorised, a harmless marker command can demonstrate persistence.

Example current-user test:

```powershell
New-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'AssessmentPersistenceTest' -Value 'cmd.exe /c echo PersistenceTest > %TEMP%\persistence-test.txt' -PropertyType String
```

Verify:

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
```

Cleanup:

```powershell
Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'AssessmentPersistenceTest'
```


---

# Startup Folder

Windows also supports startup folders.

Current-user startup folder:

```powershell
[Environment]::GetFolderPath('Startup')
```

Common startup folder:

```powershell
[Environment]::GetFolderPath('CommonStartup')
```

Assess:

```text
Who can write to the directory?
Which users are affected?
What files already exist?
Are changes monitored?
```


---

# Startup Folder Model

```text
User Logon
    |
    v
Startup Folder
    |
    v
Configured File
    |
    v
Execution
```

Writable startup locations can become persistence opportunities when an attacker has sufficient access.


---

# User Accounts

Account creation can provide persistent access.

Review local users:

```powershell
Get-LocalUser
```

Review local groups:

```powershell
Get-LocalGroup
```

Administrators:

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

Account creation should only be tested when explicitly authorised.


---

# Test Accounts

If a temporary assessment account is approved:

```text
Use a recognisable name
Use a unique strong password
Record creation time
Record group membership
Do not reuse the password
Remove the account after testing
Verify removal
```

Prefer customer-provided test identities where possible.


---

# Local Group Persistence

An existing account may gain persistent administrative access through group membership.

Conceptually:

```text
User
  |
  v
Local Administrators
  |
  v
Persistent Administrative Access
```

Monitor changes to sensitive groups such as:

```text
Administrators
Remote Desktop Users
Remote Management Users
Backup Operators
```


---

# PowerShell Profiles

PowerShell profiles can execute PowerShell content when certain PowerShell hosts start.

List profile paths:

```powershell
$PROFILE | Format-List *
```

Current profile:

```powershell
$PROFILE
```

Check whether it exists:

```powershell
Test-Path $PROFILE
```

PowerShell profiles are legitimate customisation mechanisms but can also become persistence locations if writable by an inappropriate user.


---

# PowerShell Profile Assessment

Review:

```text
Profile path
Owner
ACL
Affected user
Affected PowerShell host
Existing content
Application-control policy
PowerShell language mode
```

Do not overwrite an existing profile during testing.


---

# WMI Event Subscription

WMI supports permanent event subscriptions that can react to system events.

The conceptual structure is:

```text
Event Filter
     |
     v
Consumer
     |
     v
Binding
```

Permanent WMI subscriptions are sensitive because they can survive reboots.

Assessment should normally focus on whether such persistence is detectable and whether inappropriate identities can create it.


---

# WMI Persistence Detection

Useful defensive areas include:

```text
WMI-Activity logs
WMI repository changes
Process creation
PowerShell telemetry
EDR telemetry
Unusual permanent event consumers
```


---

# Logon Scripts

Windows and Active Directory can execute scripts during user logon.

Potential locations include:

```text
Local policy
Group Policy
Domain logon scripts
SYSVOL
Application-specific login processes
```

Changes to domain-managed logon scripts can affect many users and should not be performed unless specifically approved.


---

# Application Persistence

Applications may provide their own startup or extension mechanisms.

Examples include:

```text
Plugins
Modules
Startup scripts
Scheduled jobs
Hooks
Extensions
Application services
Administrative automation
```

An application-specific persistence path should be assessed against the application's intended security model.


---

# Linux Persistence

Common Linux persistence mechanisms include:

```text
Cron
systemd
Shell startup files
SSH authorized_keys
User accounts
Sudo configuration
Application startup
Init scripts
Timers
Container configuration
```


---

# Linux Persistence Model

```text
Linux Persistence
      |
      +--> Cron
      |
      +--> systemd
      |
      +--> SSH
      |
      +--> Shell Startup
      |
      +--> Accounts
      |
      +--> Sudo
      |
      +--> Applications
      |
      +--> Containers
```


---

# Cron

Cron executes commands on schedules.

Review system crontab:

```bash
cat /etc/crontab
```

List cron directories:

```bash
ls -la /etc/cron.d/
```

```bash
ls -la /etc/cron.daily/
```

Current user:

```bash
crontab -l
```

Cron persistence depends on:

```text
Who owns the cron entry?
Which identity executes it?
Which command is executed?
Can the command or script be modified?
```


---

# Cron Persistence Model

```text
Cron Scheduler
      |
      v
Cron Entry
      |
      v
Script / Command
      |
      v
Execution
```

A privileged cron entry that references a writable script is also a privilege escalation concern.


---

# Safe Cron Validation

For a dedicated authorised test account, a harmless marker can validate persistence.

Example user crontab entry:

```text
*/5 * * * * /usr/bin/touch /tmp/assessment-persistence-test
```

After validation, remove the entry and marker.

Do not modify production cron jobs merely to prove persistence.


---

# systemd

systemd manages services on many Linux distributions.

List services:

```bash
systemctl list-unit-files --type=service
```

Inspect a specific unit:

```bash
systemctl cat SERVICE
```

Review:

```text
Unit path
ExecStart
User
Group
EnvironmentFile
Restart policy
Enablement
File permissions
```


---

# systemd Persistence Model

```text
Boot
 |
 v
systemd
 |
 v
Unit
 |
 v
ExecStart
 |
 v
Application
```

A service enabled at boot can provide persistent execution.


---

# systemd Timers

systemd timers provide scheduled execution similar to cron.

List:

```bash
systemctl list-timers --all
```

Conceptually:

```text
Timer
  |
  v
Service Unit
  |
  v
Command
```

Review timers together with the service units they trigger.


---

# Shell Startup Files

Shells can execute user configuration during login or interactive startup.

Examples include:

```text
~/.bashrc
~/.bash_profile
~/.profile
~/.zshrc
```

These are normally user-level persistence locations.

Review:

```bash
ls -la ~
```

Inspect only files relevant to the authorised identity.


---

# Shell Startup Persistence Model

```text
User Starts Shell
      |
      v
Startup File
      |
      v
Configured Command
```

The exact startup files depend on the shell and invocation mode.


---

# SSH authorized_keys

SSH public-key authentication commonly uses:

```text
~/.ssh/authorized_keys
```

Review:

```bash
ls -la ~/.ssh/
```

Where authorised:

```bash
cat ~/.ssh/authorized_keys
```

Adding a public key can provide persistent SSH access to that identity.

This is a significant account modification and should only be performed where explicitly permitted.


---

# SSH Key Persistence Model

```text
Operator Public Key
       |
       v
authorized_keys
       |
       v
SSH Authentication
       |
       v
User Account
```

The private key remains with the operator.

Only the public key should be added to the authorised account.


---

# SSH authorized_keys Options

Entries can include restrictions such as:

```text
from=
command=
no-agent-forwarding
no-port-forwarding
no-pty
```

Restricting keys can reduce the impact of specialised automation or service keys.


---

# SSH Persistence Cleanup

If an assessment key is added:

```text
Record exact public key
Record file before modification
Add only one unique line
Validate access
Remove exact line
Verify file
Verify permissions
```

Do not replace the complete `authorized_keys` file.


---

# Linux User Accounts

Review:

```bash
cat /etc/passwd
```

Current identity:

```bash
id
```

Privileged group membership:

```bash
getent group sudo
```

or on some distributions:

```bash
getent group wheel
```

Account creation or privilege modification should only occur when specifically authorised.


---

# Sudo Persistence

Changes to sudo configuration can create long-lived privileged access.

Relevant locations include:

```text
/etc/sudoers
/etc/sudoers.d/
```

Review safely:

```bash
sudo -l
```

Do not modify production sudo policy merely to demonstrate that a privileged user could modify it.


---

# Sudoers Safety

When legitimate sudo configuration must be changed, administrators should use:

```bash
visudo
```

For assessment purposes, prefer configuration review and permission validation rather than changing security-critical policy.


---

# Application Persistence on Linux

Applications may provide:

```text
Plugins
Modules
Startup hooks
Worker services
Scheduled jobs
Configuration callbacks
Custom scripts
```

Assess whether lower-privilege users can modify components executed by more privileged application identities.


---

# Container Persistence

Containers introduce additional persistence considerations.

Examples include:

```text
Restart policies
Mounted host directories
Container images
Orchestrator configuration
Startup commands
Volumes
Secrets
Kubernetes workloads
```

Persistence at the container layer may disappear when the container is replaced.

Persistence at the orchestration layer may survive replacement.


---

# Docker Restart Policies

Docker containers can use restart policies.

Inspect:

```bash
docker inspect CONTAINER
```

A container configured to restart automatically may survive host or daemon restarts depending on configuration.

Do not create persistent containers on production infrastructure unless explicitly authorised.


---

# Kubernetes Persistence

Kubernetes persistence may involve objects such as:

```text
Deployment
DaemonSet
StatefulSet
CronJob
ServiceAccount
RoleBinding
ClusterRoleBinding
Admission configuration
```

These objects can affect many systems.

Kubernetes persistence testing should be restricted to the authorised cluster and namespaces.


---

# Active Directory Persistence

Active Directory persistence can have a significantly larger blast radius than local host persistence.

Potential categories include:

```text
Privileged group membership
Directory ACLs
Kerberos keys
Delegation
Certificates
Authentication configuration
Group Policy
SIDHistory
Service accounts
Machine accounts
Trust relationships
```


---

# Active Directory Persistence Model

```text
Domain Identity
      |
      v
Directory Modification
      |
      v
Persistent Trust / Permission
      |
      v
Future Authentication
```

Directory persistence should only be tested where specifically included in the Rules of Engagement.


---

# Privileged Group Membership

Sensitive groups can include:

```text
Domain Admins
Enterprise Admins
Administrators
Account Operators
Backup Operators
Server Operators
DNSAdmins
```

Membership changes can create straightforward persistent privilege.

Review:

```powershell
Get-ADGroupMember 'Domain Admins'
```

where the Active Directory PowerShell module is available and the query is authorised.


---

# Nested Group Persistence

Privilege may also be inherited through nested groups.

```text
User
 |
 v
Group A
 |
 v
Group B
 |
 v
Privileged Group
```

Reviewing only direct membership can therefore miss persistence paths.

BloodHound can help visualise these relationships.

See:

[BloodHound](../active-directory/bloodhound.md)


---

# ACL-Based Persistence

Active Directory objects have access control lists.

Persistent control can result from rights over objects such as:

```text
Users
Groups
Computers
Organisational Units
Group Policy Objects
Certificate infrastructure
Domain objects
```

Examples of sensitive permissions include:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
Specific attribute write permissions
```

Use:

[ACL and ACE](../active-directory/acl-ace.md)


---

# Group Policy Persistence

Group Policy can affect large numbers of systems and users.

```text
GPO
 |
 +--> Workstations
 |
 +--> Servers
 |
 +--> Users
```

Changes to GPOs can therefore create broad persistence.

During normal assessments, avoid modifying production GPOs unless the scenario explicitly requires it.


---

# SIDHistory

SIDHistory can influence access because Windows authorization can consider historical SIDs associated with an account.

Unexpected privileged SIDHistory values can represent a serious security concern.

Use:

[SIDHistory](../active-directory/sid-history.md)


---

# Kerberos Persistence

Kerberos persistence can involve long-term domain authentication material.

High-impact examples can involve compromise of:

```text
KRBTGT key material
Service account keys
Machine account keys
Trust keys
```

Such testing can have domain-wide implications.


---

# Golden Ticket Concept

A Golden Ticket scenario relates to compromise of the Kerberos Ticket Granting Ticket account key material.

Conceptually:

```text
KRBTGT Key Material
       |
       v
Forged TGT Capability
       |
       v
Domain Authentication Impact
```

This represents extremely sensitive domain-level access.

Do not perform Golden Ticket persistence testing unless explicitly required and approved.


---

# Trust Tickets

Inter-domain trust relationships introduce additional Kerberos trust material.

Use:

[Trust Tickets](../active-directory/trust-tickets.md)

and:

[Trust Relationships](../active-directory/trust-relationships.md)


---

# Shadow Credentials

Active Directory authentication can involve key-based credential attributes.

Improper control of these attributes can provide persistent authentication to an account.

Use:

[Shadow Credentials](../active-directory/shadow-credentials.md)


---

# Resource-Based Constrained Delegation

Resource-Based Constrained Delegation can alter which identities may act to services associated with a computer object.

Misconfigured object permissions can sometimes create durable attack paths.

Use:

[RBCD](../active-directory/rbcd.md)


---

# Machine Accounts

Computer objects are security principals.

Machine account manipulation can sometimes become part of a persistence chain.

Use:

[Machine Account Quota](../active-directory/machine-account-quota.md)


---

# AD CS Persistence

Active Directory Certificate Services can create powerful authentication paths.

A certificate and corresponding private key may continue to authenticate independently of the account password.

```text
Certificate
     +
Private Key
     |
     v
Authentication
```

This makes certificate lifecycle management important during incident response.


---

# Certificate Persistence

A simplified model is:

```text
Privileged Certificate
       |
       v
Password Rotated
       |
       v
Certificate Still Valid?
       |
      Yes
       |
       v
Authentication May Remain Possible
```

This is one reason password rotation alone may be insufficient after certificate-based compromise.


---

# Golden Certificate

Compromise of a certificate authority's signing key can have severe consequences.

Use:

[Golden Certificate](../active-directory/ad-cs/golden-certificate.md)

Testing CA key compromise should be considered exceptionally sensitive and is rarely necessary in production assessments.


---

# AD CS

Use the dedicated AD CS section for certificate-service attack paths:

[Active Directory Certificate Services](../active-directory/ad-cs/)


---

# Cloud Persistence

Cloud persistence can involve:

```text
User accounts
API keys
Application registrations
Service principals
Certificates
Role assignments
Federated identities
Automation accounts
Access policies
CI/CD credentials
OAuth applications
Long-lived tokens
```


---

# Cloud Persistence Model

```text
Cloud Identity
      |
      v
Persistent Credential
      |
      v
Role / Permission
      |
      v
Cloud Resource Access
```

Cloud modifications can affect multiple subscriptions, projects, accounts, or tenants.


---

# Cloud Access Keys

Long-lived access keys can provide persistent programmatic authentication.

Assess:

```text
Owner
Creation date
Last use
Permissions
Expiry
Rotation
Source restrictions
```

Prefer short-lived or managed credentials where possible.


---

# Service Principals

Application identities can provide persistent cloud access.

Potential credential types include:

```text
Client secrets
Certificates
Federated credentials
Managed identities
```

Service principals should have narrowly scoped permissions and controlled credential lifecycle.


---

# OAuth Applications

OAuth applications may receive delegated or application permissions.

Persistence risk depends on:

```text
Consent
Scopes
Application permissions
Refresh tokens
Administrative consent
Publisher trust
Credential lifetime
```

Unexpected high-privilege applications should be investigated.


---

# Cloud Role Assignments

Persistent privilege can also result from assigning an identity a role.

Conceptually:

```text
Identity
   |
   v
Role Assignment
   |
   v
Resource Access
```

Monitor creation and modification of privileged role assignments.


---

# CI/CD Persistence

CI/CD environments can provide durable access through:

```text
Pipeline modifications
Deployment credentials
Repository hooks
Runner configuration
Build agents
Service connections
Automation identities
```

Changes can propagate into production environments.

Treat CI/CD persistence as high impact.


---

# Web Application Persistence

Applications may contain mechanisms such as:

```text
Administrative accounts
API tokens
OAuth clients
Plugins
Scheduled jobs
Webhooks
Extensions
Service integrations
```

If an attacker gains application administration, these legitimate features may provide persistent access.

The root cause should be reported accurately.


---

# Database Persistence

Database environments can contain:

```text
Database users
Roles
Scheduled jobs
Stored procedures
External integrations
Credentials
```

Do not create persistent database objects merely to demonstrate administrative access unless the engagement specifically requires it.


---

# Persistence Through Credentials

Sometimes no startup mechanism is required.

A long-lived credential can itself provide persistence.

```text
Initial Access
      |
      v
Create / Obtain Credential
      |
      v
Original Foothold Removed
      |
      v
Credential Still Valid
      |
      v
Access Restored
```

Examples include:

```text
SSH key
API key
Cloud access key
Certificate
Service-account password
Refresh token
```


---

# Persistence Through Remote Access

Remote access configuration can also provide continued access.

Examples include:

```text
SSH authorization
VPN account
RDP permission
WinRM permission
Remote-management group membership
Cloud administrative role
```

The persistence mechanism is the retained trust or permission rather than the remote protocol itself.


---

# Persistence and Credential Rotation

Credential rotation can remove some persistence mechanisms but not others.

```text
Password Changed
      |
      +--> Old Password Invalid
      |
      +--> Existing Certificate May Still Work
      |
      +--> SSH Key May Still Work
      |
      +--> OAuth Grant May Still Work
      |
      +--> API Key May Still Work
```

Incident response should consider all authentication mechanisms associated with the compromised identity.


---

# Persistence and Lateral Movement

Persistence may be established on a system reached through lateral movement.

```text
Initial Host
     |
     v
Lateral Movement
     |
     v
Server
     |
     v
Persistence
```

Use:

[Lateral Movement](lateral-movement.md)


---

# Persistence and Privilege Escalation

A common attack chain is:

```text
Initial Access
      |
      v
Low Privilege
      |
      v
Privilege Escalation
      |
      v
Administrator / root
      |
      v
Privileged Persistence
```

Use:

- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)


---

# Persistence and C2

A persistence mechanism may restart an authorised C2 component after a reboot or user logon.

```text
System Boot
     |
     v
Persistence Mechanism
     |
     v
Assessment Component
     |
     v
C2
```

Use:

[Command and Control](command-and-control.md)


---

# Persistence and Defence Evasion

Persistence can overlap with defence evasion, but they have different objectives.

```text
Persistence:
Maintain access

Defence Evasion:
Avoid or reduce defensive interference
```

A persistence mechanism should not automatically be made stealthier merely because stealth is technically possible.

Use:

[Defence Evasion](defence-evasion.md)


---

# Detection Opportunities

Persistence can produce telemetry across:

```text
Endpoint
   |
   +--> Process
   |
   +--> File
   |
   +--> Registry
   |
   +--> Services
   |
   +--> Scheduled Tasks
   |
   +--> Accounts
   |
   v
Identity
   |
   v
Cloud
   |
   v
SIEM
```


---

# Windows Scheduled Task Detection

Potential indicators include:

```text
New task creation
Task modification
Unexpected execution identity
Unusual action path
Execution from writable directories
Task started shortly after creation
EDR alerts
```

Useful Windows security telemetry can include event ID:

```text
4698 - Scheduled task created
4699 - Scheduled task deleted
4702 - Scheduled task updated
```

Availability depends on auditing configuration.


---

# Windows Service Detection

Potential indicators include:

```text
New service
Changed service executable
Changed service account
Changed startup type
Unexpected service binary
Service creation followed by execution
```

A commonly investigated System event is:

```text
7045 - A service was installed in the system
```


---

# Registry Persistence Detection

Monitor security-sensitive autostart locations.

Examples include:

```text
Run keys
RunOnce keys
Winlogon-related configuration
Service registry configuration
```

Useful telemetry can come from:

```text
EDR
Sysmon
Registry auditing
Configuration monitoring
```


---

# Account Persistence Detection

Monitor:

```text
Account creation
Account enablement
Password reset
Group membership changes
Privilege assignment
Remote-access group changes
```

Sensitive group changes should receive additional scrutiny.


---

# PowerShell Persistence Detection

Potential telemetry includes:

```text
PowerShell process execution
Script block logging
Module logging
Profile modifications
File monitoring
EDR alerts
```

Monitor unusual modifications to PowerShell profile locations.


---

# WMI Persistence Detection

Monitor:

```text
Permanent event filters
Event consumers
Filter-to-consumer bindings
WMI repository activity
WMI operational logs
Unexpected child processes
```


---

# Linux Cron Detection

Potential indicators include:

```text
Crontab modification
New files under /etc/cron.d/
Unexpected root cron entries
Unexpected scripts
File integrity changes
Audit events
```


---

# Linux systemd Detection

Monitor:

```text
New unit files
Changed unit files
daemon-reload activity
New enabled services
Unexpected ExecStart
Unexpected service users
New timers
```


---

# Linux SSH Persistence Detection

Monitor:

```text
authorized_keys modifications
New SSH keys
SSH login from unusual source
Unexpected key fingerprint
File permission changes
Account changes
```


---

# Linux Account Detection

Monitor:

```text
/etc/passwd changes
/etc/shadow changes
Group membership changes
sudoers changes
New home directories
SSH key creation
```


---

# Active Directory Persistence Detection

Potential high-value events include:

```text
Privileged group membership changes
Directory ACL changes
GPO changes
Certificate changes
Delegation changes
Account modifications
SIDHistory changes
New machine accounts
Authentication policy changes
```


---

# Cloud Persistence Detection

Cloud monitoring should include:

```text
New user
New access key
New service principal credential
New application
New OAuth consent
New role assignment
New federation configuration
New certificate
New API token
Policy modification
```


---

# Persistence Baselines

Defenders should know what normal persistence looks like.

Examples:

```text
Approved scheduled tasks
Approved services
Approved startup applications
Approved systemd units
Approved cron jobs
Approved SSH keys
Approved privileged groups
Approved cloud applications
Approved service principals
```

Baselines make unexpected changes easier to identify.


---

# Persistence Detection Model

```text
Configuration Change
       |
       v
Telemetry
       |
       v
Baseline Comparison
       |
       v
Expected?
   /       \
 Yes        No
  |          |
  v          v
Allow     Investigate
             |
             v
         Persistence?
```


---

# Detection Validation

Track whether the persistence action is visible.

Example:

| Activity | Logged | Alerted | Prevented | Investigated |
|---|---|---|---|---|
| Test scheduled task | Yes | Yes | No | Yes |
| Test service creation | Yes | Yes | Yes | Yes |
| SSH key modification | Yes | No | No | No |
| Cloud role change | Yes | Yes | No | Yes |

This is often more valuable than attempting multiple persistence mechanisms.


---

# Persistence Evidence

Record:

```text
Timestamp
System or identity
Persistence mechanism
Original state
Modified state
Required privilege
Validation result
Detection result
Cleanup action
Cleanup verification
```


---

# Example Evidence

```text
Timestamp:
2026-09-05 14:20 UTC

Host:
TEST-WKS01

Identity:
CORP\test-admin

Mechanism:
Scheduled task

Task:
Assessment-Persistence-Test

Purpose:
Validate detection of scheduled-task persistence

Result:
Marker file created successfully

Detection:
EDR alert generated

Cleanup:
Task and marker file removed

Verification:
Task no longer present
```


---

# Evidence Screenshots

Screenshots should demonstrate:

```text
Persistence location
Assessment-specific identifier
Security context
Validation result
Detection result
Cleanup
```

Avoid capturing unrelated sensitive information.


---

# Candidate vs Confirmed

## Candidate

A location could potentially provide persistence.

Examples:

```text
Writable startup directory
Writable service configuration
Writable systemd unit
Writable authorized_keys
Directory ACL permission
Cloud role-management permission
```

No persistent modification has been demonstrated.


## Likely

The tester has sufficient permission and the mechanism appears capable of surviving the relevant lifecycle event.


## Confirmed

A controlled authorised test demonstrates the persistence mechanism operates as expected.


---

# Persistence Severity

Severity depends on:

```text
Privilege
Affected identity
Affected systems
Duration
Authentication strength
Scope
Ease of creation
Ease of detection
Ability to survive credential rotation
Blast radius
Attack chaining
```

A user-level startup entry is not automatically equivalent to domain-level certificate persistence.


---

# Persistence Hierarchy

A simplified impact model is:

```text
User-Level Host Persistence
           |
           v
Administrative Host Persistence
           |
           v
Server Persistence
           |
           v
Identity Persistence
           |
           v
Domain Persistence
           |
           v
Cloud / Trust Infrastructure Persistence
```

Actual severity remains contextual.


---

# What Not to Report Automatically

Do not automatically report:

```text
Task Scheduler exists
systemd exists
Cron exists
SSH supports authorized_keys
Windows has Run keys
Administrators can create services
Domain Admins can modify the directory
Cloud administrators can create identities
```

These are expected platform capabilities.

A security finding requires an inappropriate permission, trust relationship, control failure, or demonstrated attack path.


---

# Reporting Persistence

Weak:

```text
Scheduled tasks can be used for persistence.
```

Better:

```text
The compromised standard-user account had write access to the
action script executed by a scheduled task running as a privileged
service identity.

A non-destructive marker-file test confirmed that modifying the
script caused code to execute in the privileged task context.
```


---

# Reporting Directory Persistence

Weak:

```text
Active Directory allows persistence.
```

Better:

```text
The delegated support group had WriteDACL permission over a
privileged administrative group.

This permission could allow members of the support group to grant
themselves durable control over the privileged group without
requiring membership at the time of modification.
```


---

# Cleanup

Persistence cleanup is mandatory unless the customer explicitly requests otherwise.

A cleanup workflow is:

```text
Persistence Inventory
       |
       v
Stop Active Component
       |
       v
Remove Persistence Entry
       |
       v
Remove Artifact
       |
       v
Restore Original State
       |
       v
Verify
       |
       v
Record Cleanup
```


---

# Cleanup Verification

Do not assume a deletion command succeeded.

Verify:

```text
Task no longer exists
Service no longer exists
Registry value removed
Startup file removed
SSH key removed
Cron entry removed
systemd unit removed
Account removed
Group membership restored
Cloud role removed
Certificate revoked where required
```


---

# Reboot Validation

Persistence is often defined by surviving reboot, but rebooting production systems can cause disruption.

Only perform reboot validation when explicitly permitted.

Otherwise, document:

```text
Mechanism configured for startup
Configuration verified
Reboot not performed due to availability constraints
```

Do not create operational risk merely to prove an already established configuration property.


---

# Persistence Cleanup Checklist

## Windows

- [ ] Test scheduled tasks removed
- [ ] Test services removed
- [ ] Registry changes restored
- [ ] Startup files removed
- [ ] Temporary accounts removed
- [ ] Group membership restored
- [ ] PowerShell profiles restored
- [ ] WMI subscriptions removed
- [ ] Temporary artifacts removed

## Linux

- [ ] Cron entries removed
- [ ] systemd units removed
- [ ] Timers removed
- [ ] SSH keys removed
- [ ] Shell startup files restored
- [ ] Temporary accounts removed
- [ ] sudo configuration restored
- [ ] Temporary artifacts removed

## Active Directory

- [ ] Group membership restored
- [ ] ACL modifications restored
- [ ] Test accounts removed
- [ ] Delegation changes restored
- [ ] Test certificates handled appropriately
- [ ] GPO changes restored
- [ ] Machine-account changes restored
- [ ] Authentication changes restored

## Cloud

- [ ] Test accounts removed
- [ ] Access keys revoked
- [ ] Application secrets removed
- [ ] Certificates removed
- [ ] Role assignments restored
- [ ] OAuth grants removed
- [ ] Service principal changes restored
- [ ] Temporary automation removed


---

# Persistence Testing Checklist

## Scope

- [ ] Written authorisation confirmed
- [ ] Persistence explicitly permitted
- [ ] Target confirmed
- [ ] Current privilege established
- [ ] Mechanism permitted
- [ ] Reboot rules understood
- [ ] Account-creation rules understood
- [ ] Directory modification rules understood
- [ ] Cloud modification rules understood
- [ ] Cleanup plan documented

## Preparation

- [ ] Original state recorded
- [ ] Unique assessment identifier selected
- [ ] Persistence inventory created
- [ ] Validation method defined
- [ ] Detection objective defined
- [ ] Cleanup command prepared

## Windows

- [ ] Scheduled tasks considered
- [ ] Services considered
- [ ] Run keys considered
- [ ] Startup folders considered
- [ ] Accounts considered
- [ ] Group membership considered
- [ ] PowerShell profiles considered
- [ ] WMI considered where relevant
- [ ] Application persistence considered

## Linux

- [ ] Cron considered
- [ ] systemd considered
- [ ] systemd timers considered
- [ ] SSH authorized_keys considered
- [ ] Shell startup files considered
- [ ] Accounts considered
- [ ] Sudo configuration considered
- [ ] Application persistence considered

## Active Directory

- [ ] Privileged groups considered
- [ ] Nested groups considered
- [ ] ACLs considered
- [ ] GPO considered
- [ ] SIDHistory considered
- [ ] Delegation considered
- [ ] Kerberos persistence considered
- [ ] AD CS considered
- [ ] Shadow Credentials considered
- [ ] Machine accounts considered

## Cloud

- [ ] Access keys considered
- [ ] Service principals considered
- [ ] OAuth applications considered
- [ ] Role assignments considered
- [ ] Certificates considered
- [ ] CI/CD identities considered
- [ ] Cross-tenant boundaries respected

## Detection

- [ ] Endpoint telemetry reviewed
- [ ] Identity telemetry reviewed
- [ ] Directory telemetry reviewed
- [ ] Cloud telemetry reviewed
- [ ] Alerts recorded
- [ ] Prevention recorded
- [ ] SOC response recorded

## Evidence

- [ ] Timestamp recorded
- [ ] Mechanism recorded
- [ ] Identity recorded
- [ ] Required privilege recorded
- [ ] Original state recorded
- [ ] Modified state recorded
- [ ] Validation result recorded
- [ ] Detection result recorded

## Cleanup

- [ ] Persistence removed
- [ ] Artifacts removed
- [ ] Original state restored
- [ ] Credentials revoked where required
- [ ] Cleanup independently verified
- [ ] Customer informed of any remaining changes


---

# Persistence Decision Model

```text
                     Foothold
                        |
                        v
                Persistence Needed?
                  /          \
                No            Yes
                |              |
               STOP            v
                       Explicitly Permitted?
                         /          \
                       No            Yes
                       |              |
                      STOP            v
                           Select Mechanism
                                  |
                                  v
                          Record Original State
                                  |
                                  v
                            Safe to Modify?
                              /       \
                            No         Yes
                            |           |
                         Reassess       v
                                   Deploy
                                      |
                                      v
                                  Validate
                                      |
                                      v
                               Detection Review
                                      |
                                      v
                               Objective Proven?
                                 /          \
                               Yes           No
                               |              |
                               v              v
                            Cleanup      Continue Only
                                         if Required
                                              |
                                              v
                                           Cleanup
                                              |
                                              v
                                        Verify Restore
```


---

# Persistence Attack Path Model

```text
Initial Access
      |
      v
Credential Access
      |
      v
Privilege Escalation
      |
      v
Privileged Context
      |
      v
Persistence
      |
      +----------------------+
      |          |           |
      v          v           v
    Host      Identity      Cloud
      |          |           |
      +----------+-----------+
                 |
                 v
          Original Access Lost
                 |
                 v
          Persistent Mechanism
                 |
                 v
            Access Restored
```


---

# Defensive Persistence Model

```text
                         Persistence
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
          Prevent          Detect           Recover
             |                |                |
             v                v                v
       Least Privilege     EDR/SIEM       Inventory
       Application Control File Monitor   Key Rotation
       ACL Hardening       Identity Logs  Account Removal
       Segmentation        Cloud Audit    Restore Config
       MFA                 Baselines      Certificate Revoke
             |                |                |
             +----------------+----------------+
                              |
                              v
                       Reduced Dwell Time
```


---

# Persistence Validation Model

```text
Create Controlled Change
          |
          v
Trigger Expected Event
          |
          v
Did It Execute?
      /        \
    No          Yes
    |            |
    v            v
Document      Detection?
               /     \
             No       Yes
             |         |
             v         v
          Record     Record
             \         /
              \       /
               v     v
                Cleanup
                   |
                   v
             Verify Removal
```


---

# Quick Reference

## Windows Scheduled Tasks

```cmd
schtasks /query /fo LIST /v
```

```powershell
Get-ScheduledTask
```

## Windows Services

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, State, StartMode, PathName
```

## Run Keys

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
```

```powershell
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run'
```

## Startup Folders

```powershell
[Environment]::GetFolderPath('Startup')
```

```powershell
[Environment]::GetFolderPath('CommonStartup')
```

## Local Users

```powershell
Get-LocalUser
```

## Local Administrators

```powershell
Get-LocalGroupMember -Group 'Administrators'
```

## PowerShell Profiles

```powershell
$PROFILE | Format-List *
```

## Linux Cron

```bash
crontab -l
```

```bash
cat /etc/crontab
```

## systemd Services

```bash
systemctl list-unit-files --type=service
```

## systemd Timers

```bash
systemctl list-timers --all
```

## SSH Keys

```bash
ls -la ~/.ssh/
```

## Linux Identity

```bash
id
```

## Sudo

```bash
sudo -l
```


---

# Related Notes

- [Red Teaming](./)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)
- [Active Directory](../active-directory/)
- [ACL and ACE](../active-directory/acl-ace.md)
- [BloodHound](../active-directory/bloodhound.md)
- [Group Policy](../active-directory/group-policy.md)
- [Kerberos](../active-directory/kerberos.md)
- [SIDHistory](../active-directory/sid-history.md)
- [Shadow Credentials](../active-directory/shadow-credentials.md)
- [RBCD](../active-directory/rbcd.md)
- [Machine Account Quota](../active-directory/machine-account-quota.md)
- [Trust Relationships](../active-directory/trust-relationships.md)
- [Trust Tickets](../active-directory/trust-tickets.md)
- [AD CS](../active-directory/ad-cs/)
- [Golden Certificate](../active-directory/ad-cs/golden-certificate.md)


---

# References

- [MITRE ATT&CK - Persistence](https://attack.mitre.org/tactics/TA0003/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Boot or Logon Autostart Execution](https://attack.mitre.org/techniques/T1547/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Create or Modify System Process](https://attack.mitre.org/techniques/T1543/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Create Account](https://attack.mitre.org/techniques/T1136/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Event Triggered Execution](https://attack.mitre.org/techniques/T1546/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Server Software Component](https://attack.mitre.org/techniques/T1505/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Task Scheduler](https://learn.microsoft.com/windows/win32/taskschd/task-scheduler-start-page){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Service Applications](https://learn.microsoft.com/windows/win32/services/service-programs){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows LAPS](https://learn.microsoft.com/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Group Managed Service Accounts](https://learn.microsoft.com/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Active Directory Domain Services](https://learn.microsoft.com/windows-server/identity/ad-ds/get-started/virtual-dc/active-directory-domain-services-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Microsoft Entra service principals](https://learn.microsoft.com/entra/identity-platform/app-objects-and-service-principals){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH - authorized_keys](https://man.openbsd.org/sshd.8){ target="_blank" rel="noopener noreferrer" }
- [systemd](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Persistence testing creates deliberate changes that may survive logoff, restart, credential changes, or other lifecycle events. Only create accounts, scheduled tasks, services, startup entries, SSH keys, directory permissions, certificates, cloud identities, role assignments, or other persistent changes when explicitly permitted by the Rules of Engagement. Record every modification before deployment, use recognisable assessment identifiers, minimise the blast radius, avoid modifying production-wide controls unless specifically required, and verify complete cleanup at the end of testing.
