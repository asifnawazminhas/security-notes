---
title: Red Team Privilege Escalation
description: Privilege escalation methodology for authorised red team assessments, covering Windows, Linux, Active Directory, cloud and application privilege boundaries, enumeration, attack-path analysis, safe validation, credential relationships, application control, detection, evidence, remediation, cleanup, and reporting.
---

# Red Team Privilege Escalation

Privilege escalation is the process of moving from the current security context to one with additional permissions or authority.

In a red team assessment, privilege escalation is not limited to:

```text
User -> Administrator
```

or:

```text
User -> root
```

Privilege boundaries can exist across:

```text
Operating systems

Applications

Active Directory

Cloud platforms

Containers

Databases

Service accounts

Administrative tiers

Security tooling
```

A useful model is:

```text
Current Context
      |
      v
Enumerate Privilege Boundaries
      |
      v
Identify Candidate Paths
      |
      v
Validate Preconditions
      |
      v
Minimal Safe Validation
      |
      v
Higher Privilege
      |
      v
Reassess Attack Path
```

The objective is to determine whether an attacker who already has an authorised foothold can cross a security boundary that should prevent access to more privileged resources.

!!! warning "Authorised testing only"
    Privilege escalation can affect highly sensitive operating-system and identity controls. Validate only the minimum conditions required to demonstrate the security boundary. Avoid destructive changes, production disruption, unnecessary credential access, or persistent privileged modifications.


---

# Privilege Escalation Objectives

Common objectives include:

```text
Determine current privilege

Identify local privilege boundaries

Identify misconfigured services

Identify scheduled execution paths

Identify writable privileged resources

Identify excessive user rights

Identify credential-based escalation paths

Identify identity and group escalation paths

Identify Active Directory privilege paths

Identify cloud privilege paths

Validate application-control assumptions

Determine defensive visibility

Reach an engagement objective
```


---

# Privilege Escalation Model

```text
                     FOOTHOLD
                        |
                        v
                  Current Identity
                        |
                        v
                 Current Privilege
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      Operating      Identity      Application
       System         System        Privilege
          |             |             |
          +-------------+-------------+
                        |
                        v
                 Candidate Paths
                        |
                        v
                   Validation
                        |
                        v
                Elevated Context
```


---

# Privilege Is Contextual

Privilege should not be treated as one universal level.

Examples:

```text
Local standard user

Local administrator

Domain user

Server operator

Database administrator

Cloud contributor

Cloud owner

Application administrator

Service account

Domain administrator
```

An identity may be privileged in one system while unprivileged in another.


---

# Privilege Boundary Examples

```text
Standard User -> Local Administrator

Local Administrator -> SYSTEM

Application User -> Application Administrator

Domain User -> Server Administrator

Domain User -> Domain Administrator

Cloud User -> Subscription Administrator

Container User -> Host

Database User -> Database Administrator
```


---

# Privilege Escalation vs Lateral Movement

Privilege escalation:

```text
HOST A

User
 |
 v
Administrator
```

Lateral movement:

```text
HOST A
  |
  v
HOST B
```

An attack path may combine both:

```text
HOST A
Standard User
     |
     v
Local Administrator
     |
     v
HOST B
     |
     v
Domain Privilege
```


---

# Privilege Escalation vs Credential Access

Credential access may enable privilege escalation.

```text
Standard User
     |
     v
Credential Exposure
     |
     v
Privileged Credential
     |
     v
Higher Privilege
```

However:

```text
Credential Found
```

does not automatically mean:

```text
Privilege Escalation Confirmed
```

The credential must provide additional authorised access.


---

# Privilege Escalation vs Persistence

Privilege escalation obtains additional authority.

Persistence maintains access.

```text
Privilege Escalation
        |
        v
Higher Privilege
        |
        v
Persistence
```

Do not introduce persistence merely to prove privilege escalation.


---

# Privilege Escalation Workflow

```text
Establish Context
      |
      v
Enumerate
      |
      v
Identify Candidate
      |
      v
Validate Preconditions
      |
      v
Assess Risk
      |
      v
Minimal Validation
      |
      v
Confirm Privilege
      |
      v
Capture Evidence
      |
      v
Cleanup
      |
      v
Continue Attack Path
```


---

# Phase 1 - Establish Current Context

Before looking for escalation paths, understand the current identity.

Record:

```text
Host

User

Groups

Privileges

Integrity level

Domain

Session type

Operating system

Architecture

Security controls
```


---

# Windows Identity

```powershell
whoami
```

Detailed:

```powershell
whoami /all
```

Groups:

```powershell
whoami /groups
```

Privileges:

```powershell
whoami /priv
```


---

# Windows Integrity Level

`whoami /groups` can reveal integrity information.

Common levels include:

```text
Low

Medium

High

System
```


---

# Local Administrators

```powershell
Get-LocalGroupMember -Group Administrators
```

If unavailable:

```cmd
net localgroup administrators
```


---

# Domain Context

```powershell
whoami /fqdn
```

Environment:

```powershell
$env:USERDOMAIN
```

Domain information:

```powershell
Get-CimInstance Win32_ComputerSystem |
    Select-Object Name,Domain,PartOfDomain
```


---

# Linux Identity

```bash
id
```

Current user:

```bash
whoami
```

Groups:

```bash
groups
```

Hostname:

```bash
hostname
```


---

# Linux Sudo

```bash
sudo -l
```

This is one of the highest-value Linux privilege escalation checks.


---

# Phase 2 - System Enumeration

Privilege escalation should begin with enumeration rather than exploitation.

Look for:

```text
Services

Scheduled tasks

Permissions

Privileges

Installed software

Credentials

Configuration files

Environment variables

Processes

Sockets

Mounts

Containers

Security controls
```


---

# Enumeration Model

```text
                    CURRENT HOST
                         |
       +-----------------+-----------------+
       |                 |                 |
       v                 v                 v
   Processes          Services          Files
       |                 |                 |
       v                 v                 v
   Privileges         Tasks           Credentials
       |                 |                 |
       +-----------------+-----------------+
                         |
                         v
                 Candidate Paths
```


---

# Candidate vs Confirmed

Use clear states.

```text
Candidate

Likely

Confirmed
```


---

# Candidate

A potentially interesting configuration exists.

Example:

```text
Service uses a path that may be writable.
```


---

# Likely

Required preconditions appear to exist.

Example:

```text
The service executes as SYSTEM and a referenced directory appears
writable by the assessment user.
```


---

# Confirmed

Minimal authorised validation demonstrates the boundary.

Example:

```text
The assessment confirmed that the standard user could modify the
privileged service resource and that the service executes the
resource under a higher-privileged context.
```


---

# Do Not Skip Preconditions

Use:

```text
Interesting Configuration
        |
        v
Required Privilege?
        |
        v
Writable?
        |
        v
Privileged Consumer?
        |
        v
Trigger Available?
        |
        v
Safe Validation
```

This prevents false positives.


---

# Windows Privilege Escalation

Common Windows areas include:

```text
Services

Scheduled tasks

File permissions

Directory permissions

Registry permissions

User privileges

Stored credentials

Application configuration

Installer policy

DLL loading

PATH configuration

PowerShell

Application control

UAC

Named pipes

Processes
```

For detailed techniques see:

[Windows Privilege Escalation](../windows/privilege-escalation.md)

[Windows PrivEsc Explorer](../privesc/windows.md)


---

# Windows Service Enumeration

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name,StartName,State,StartMode,PathName
```

Look for:

```text
Privileged service account

Writable executable

Writable directory

Writable configuration

Unquoted paths

Unusual binaries

Custom software
```


---

# Service Context

Important accounts include:

```text
LocalSystem

NT AUTHORITY\LocalService

NT AUTHORITY\NetworkService

Domain service account

Custom local account
```


---

# Service Path Review

Example:

```powershell
Get-CimInstance Win32_Service |
    Where-Object PathName |
    Select-Object Name,StartName,PathName
```

Do not assume a service is vulnerable merely because its path appears unusual.


---

# Service Permission Model

```text
Service
   |
   v
Privileged Account?
   |
   v
Executable / Config
   |
   v
User Writable?
   |
   v
Can Privileged Execution Occur?
```


---

# File Permissions

Inspect:

```powershell
Get-Acl "C:\Path\To\File.exe" |
    Format-List Owner,AccessToString
```

Directory:

```powershell
Get-Acl "C:\Path\To\Directory" |
    Format-List Owner,AccessToString
```


---

# Safe Write Validation

When write access is uncertain:

```powershell
$folder = "C:\ProgramData\CandidateFolder"
$file = Join-Path $folder "write-test-$PID-$(Get-Random).tmp"

try {
    New-Item -ItemType File -Path $file -ErrorAction Stop | Out-Null
    Write-Output "Write succeeded: $file"
}
catch {
    Write-Output "Write failed: $($_.Exception.Message)"
}
finally {
    Remove-Item $file -Force -ErrorAction SilentlyContinue
}
```

This validates write access without replacing privileged files.


---

# Scheduled Tasks

Enumerate:

```powershell
Get-ScheduledTask |
    Select-Object TaskName,TaskPath,State
```

Actions:

```powershell
Get-ScheduledTask |
    ForEach-Object {
        $task = $_

        foreach ($action in $task.Actions) {
            [PSCustomObject]@{
                TaskName  = $task.TaskName
                TaskPath  = $task.TaskPath
                Execute   = $action.Execute
                Arguments = $action.Arguments
            }
        }
    }
```


---

# Scheduled Task Model

```text
Scheduled Task
      |
      v
Privileged Context?
      |
      v
Referenced Resource
      |
      v
User Writable?
      |
      v
Privileged Execution
```


---

# Windows Privileges

```powershell
whoami /priv
```

Interesting privileges can include:

```text
SeBackupPrivilege

SeRestorePrivilege

SeImpersonatePrivilege

SeAssignPrimaryTokenPrivilege

SeTakeOwnershipPrivilege

SeDebugPrivilege

SeLoadDriverPrivilege
```

The presence of a privilege does not automatically mean it is exploitable in the current environment.


---

# Privilege Assessment

For each privilege determine:

```text
Present?

Enabled?

Required access available?

Security boundary affected?

Safe validation possible?

Detection expected?
```


---

# Registry Permissions

Potentially relevant locations include configuration associated with:

```text
Services

Applications

Startup

Installers

Security policy
```

Inspect a known key:

```powershell
Get-Acl "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Example" |
    Format-List Owner,AccessToString
```

Only inspect keys relevant to the identified candidate path.


---

# Installed Applications

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```

Also:

```powershell
Get-ItemProperty HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
    Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation
```

Custom applications deserve attention because they may introduce privileged services or writable resources.


---

# Running Processes

```powershell
Get-Process
```

Detailed:

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,ExecutablePath
```


---

# Environment Variables

```powershell
Get-ChildItem Env:
```

Review:

```text
PATH

TEMP

TMP

Application-specific variables
```


---

# PATH

```powershell
$env:PATH -split ';'
```

For each relevant path consider:

```text
Who can write there?

Which privileged process uses it?

Is executable search behaviour relevant?
```


---

# Credentials

Potential credential sources include:

```text
Configuration files

Environment variables

PowerShell history

Application secrets

Service accounts

Scheduled task configuration

Credential Manager
```

See:

[Credential Access](credential-access.md)


---

# PowerShell History

```powershell
(Get-PSReadLineOption).HistorySavePath
```

If authorised:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath -ErrorAction SilentlyContinue
```

Handle discovered secrets carefully.


---

# Credential Manager

```cmd
cmdkey /list
```

This enumerates stored credential targets without dumping credential material.


---

# Application Control

Privilege escalation tooling may be affected by:

```text
AppLocker

WDAC

PowerShell CLM

AMSI

ASR

EDR
```

See:

[Execution](execution.md)

[Defence Evasion](defence-evasion.md)


---

# UAC

User Account Control separates administrative sessions from elevated administrative execution.

Check current identity first:

```powershell
whoami /groups
```

A user belonging to the local Administrators group does not necessarily mean the current process is elevated.


---

# UAC Interpretation

```text
Administrator Account
       |
       v
Filtered Token
       |
       v
UAC Elevation
       |
       v
Elevated Token
```

Do not describe normal UAC behaviour as a vulnerability.


---

# Linux Privilege Escalation

Common Linux areas include:

```text
sudo

SUID

SGID

Capabilities

Cron

systemd

File permissions

Writable scripts

PATH

Environment variables

Credentials

SSH keys

Containers

Docker

NFS

Mounted filesystems

Kernel exposure

Custom applications
```

For detailed techniques see:

[Linux Privilege Escalation](../linux/privilege-escalation.md)

[Linux PrivEsc Explorer](../privesc/linux.md)


---

# Linux System Context

```bash
uname -a
```

Distribution:

```bash
cat /etc/os-release
```

Kernel:

```bash
uname -r
```


---

# Sudo

```bash
sudo -l
```

Review:

```text
Allowed commands

NOPASSWD

Environment preservation

Command arguments

Wildcards

Run-as users
```


---

# Sudo Model

```text
Current User
     |
     v
sudo -l
     |
     v
Allowed Command
     |
     v
Privileged Functionality?
     |
     v
Higher Privilege
```


---

# SUID

Find SUID executables:

```bash
find / -perm -4000 -type f 2>/dev/null
```

SGID:

```bash
find / -perm -2000 -type f 2>/dev/null
```


---

# SUID Analysis

Do not report every SUID binary.

Determine:

```text
Expected?

Standard operating-system binary?

Custom binary?

Writable?

Known dangerous functionality?

Privilege boundary actually reachable?
```


---

# GTFOBins

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" } documents legitimate Unix binaries that can provide security-relevant functionality under specific configurations.

Use it to understand:

```text
Sudo behaviour

SUID behaviour

Capabilities

File read/write

Shell functionality
```

A GTFOBins entry does not mean the host is vulnerable.


---

# Linux Capabilities

Enumerate:

```bash
getcap -r / 2>/dev/null
```

Capabilities can grant specific privileged operations without full root access.

Examples include:

```text
cap_setuid

cap_dac_override

cap_sys_admin

cap_net_admin

cap_sys_ptrace
```


---

# Capability Model

```text
Executable
    |
    v
Capability
    |
    v
Privileged Operation
    |
    v
Can Current User Execute?
    |
    v
Security Boundary
```


---

# Cron

System cron:

```bash
cat /etc/crontab
```

Directories:

```bash
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
```

User cron:

```bash
crontab -l
```


---

# Cron Analysis

Look for:

```text
Privileged user

Writable script

Writable directory

Relative command path

Environment dependency

Custom application
```


---

# systemd

Running services:

```bash
systemctl --type=service --state=running
```

Timers:

```bash
systemctl list-timers --all
```

Inspect a relevant unit:

```bash
systemctl cat SERVICE
```


---

# systemd Analysis

Review:

```text
User=

Group=

ExecStart=

Environment=

EnvironmentFile=

WorkingDirectory=
```

Then inspect ownership and permissions of referenced resources.


---

# File Permissions

```bash
ls -la /path/to/file
```

Full path:

```bash
namei -l /path/to/file
```

ACLs where available:

```bash
getfacl /path/to/file
```


---

# Writable Directories

A writable directory is not automatically a privilege escalation issue.

The important relationship is:

```text
Writable Directory
       |
       v
Privileged Process Uses Content?
       |
       v
Attacker-Controlled Input?
       |
       v
Higher Privilege?
```


---

# Linux PATH

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

For relevant entries:

```bash
ls -ld /path
```

A writable PATH directory only matters when a privileged process performs unsafe command resolution.


---

# Processes

```bash
ps aux
```

Process tree:

```bash
ps -ef --forest
```

Look for:

```text
Privileged custom applications

Interesting command lines

Credentials in arguments

Scripts executed as root

Unusual service accounts
```


---

# Listening Services

```bash
ss -lntup
```

Local-only services may expose privileged application functionality that is not reachable externally.


---

# Environment

```bash
env
```

Potentially sensitive variables include:

```text
Passwords

API keys

Database credentials

Cloud tokens

Application secrets
```

Do not unnecessarily expose discovered secrets in evidence.


---

# SSH

Review:

```bash
ls -la ~/.ssh/
```

Possible files:

```text
authorized_keys

config

id_rsa

id_ed25519

known_hosts
```

Credential handling rules apply.


---

# Containers

Determine whether the current session is containerised:

```bash
cat /proc/1/cgroup
```

Docker indicator:

```bash
test -f /.dockerenv && echo "Docker indicator present"
```


---

# Docker

Check:

```bash
docker version
```

Current containers:

```bash
docker ps
```

Access to a container-management socket or daemon can represent a major privilege boundary and should be assessed carefully.


---

# Docker Socket

Inspect:

```bash
ls -l /var/run/docker.sock
```

Determine:

```text
Owner

Group

Current user membership

Whether access is intended
```


---

# Container vs Host Privilege

Always distinguish:

```text
Container root
```

from:

```text
Host root
```

They are not automatically equivalent.


---

# Kernel Vulnerabilities

Kernel vulnerabilities may provide local privilege escalation under specific versions and configurations.

Workflow:

```text
Kernel Version
     |
     v
Candidate Vulnerability
     |
     v
Affected Version?
     |
     v
Required Configuration?
     |
     v
Mitigations?
     |
     v
Safe Validation Decision
```

Do not execute kernel exploits simply because a version appears potentially affected.


---

# Kernel Validation

Collect:

```bash
uname -a
```

```bash
uname -r
```

Then research:

```text
Distribution patches

Backported fixes

Kernel configuration

Vendor advisories
```

Version strings alone can produce false positives.


---

# Active Directory Privilege Escalation

Privilege escalation in Active Directory often involves relationships rather than a local software flaw.

Examples:

```text
Group membership

ACLs

Delegation

Credential reuse

Service accounts

Kerberos

GPO

AD CS

Machine accounts

Trusts

Shadow credentials

RBCD
```


---

# AD Attack Path Model

```text
Current Domain User
       |
       v
Group / ACL / Credential
       |
       v
Intermediate Principal
       |
       v
Privileged Resource
       |
       v
Administrative Identity
```


---

# BloodHound

[BloodHound](../active-directory/bloodhound.md) is useful for understanding privilege relationships.

Conceptually:

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
Privileged User
```


---

# BloodHound Interpretation

A graph edge represents a relationship.

It does not automatically prove that the complete path is exploitable.

Validate:

```text
Edge prerequisites

Current permissions

Network reachability

Authentication

Security controls

Scope
```


---

# Active Directory Groups

Review direct and nested group memberships.

See:

[Active Directory Groups](../active-directory/groups.md)


---

# ACLs

Active Directory permissions can create escalation paths.

Examples include control over:

```text
Users

Groups

Computers

Organisational Units

Group Policy Objects

Certificate objects
```

See:

[ACL and ACE Abuse](../active-directory/acl-ace.md)


---

# Delegation

Relevant delegation models include:

```text
Unconstrained Delegation

Constrained Delegation

Resource-Based Constrained Delegation
```

See:

[Unconstrained Delegation](../active-directory/unconstrained-delegation.md)

[Constrained Delegation](../active-directory/constrained-delegation.md)

[Resource-Based Constrained Delegation](../active-directory/rbcd.md)


---

# Kerberos

Privilege paths may involve:

```text
Service tickets

Delegation

Credential material

Ticket-based authentication

Service accounts
```

See:

[Kerberos](../active-directory/kerberos.md)


---

# AD CS

Active Directory Certificate Services can create identity privilege paths through certificate-template and CA configurations.

See:

[Active Directory Certificate Services](../active-directory/ad-cs/)


---

# AD CS Model

```text
Current Principal
       |
       v
Certificate Permission
       |
       v
Certificate
       |
       v
Authentication
       |
       v
Higher Privilege Identity
```

Not every certificate template is vulnerable.

Evaluate the exact configuration.


---

# Group Policy

GPO permissions and configuration can create broad privilege relationships.

See:

[Group Policy](../active-directory/group-policy.md)


---

# Cloud Privilege Escalation

Cloud privilege escalation commonly involves:

```text
IAM roles

Role assignments

Service principals

Managed identities

API permissions

Access keys

Secrets

Automation accounts

CI/CD identities

Resource policies
```


---

# Cloud Privilege Model

```text
Cloud Identity
      |
      v
Current Permissions
      |
      v
Assignable Role?
      |
      v
Credential / Token Access?
      |
      v
Resource Control?
      |
      v
Higher Privilege
```


---

# Cloud Questions

Ask:

```text
What identity am I?

Which roles do I have?

Which resources can I modify?

Can I assign permissions?

Can I create credentials?

Can I control an identity?

Can I modify automation?

Can I access secrets?

Can I impersonate another identity?
```


---

# Cloud Scope

Cloud environments require careful scope validation because:

```text
Tenant

Subscription

Project

Account

Resource group

Individual resource
```

may each have different authorisation boundaries.


---

# Application Privilege Escalation

Applications may contain their own privilege models.

Examples:

```text
User

Moderator

Support

Administrator

Super Administrator

Tenant Administrator
```


---

# Application Model

```text
Normal User
     |
     v
Authorisation Boundary
     |
     v
Administrative Function
```

Privilege escalation can therefore be caused by:

```text
Broken access control

Role manipulation

IDOR

Mass assignment

JWT claim trust

API authorisation failure
```

See:

[Authorisation](../web/authorisation.md)


---

# Database Privilege Escalation

Database privilege boundaries may include:

```text
Read-only user

Application user

Schema owner

Database administrator

Operating-system integration
```

Determine whether database permissions can cross into:

```text
Other databases

Administrative roles

Operating-system context

Cloud identity
```


---

# Credential-Based Privilege Escalation

Credentials are often the shortest privilege path.

Potential sources:

```text
Configuration files

Scripts

Environment variables

Repositories

Service accounts

Scheduled tasks

Shell history

Cloud metadata

Application secrets
```

See:

[Credential Access](credential-access.md)


---

# Credential Reuse

```text
Low-Privilege Context
       |
       v
Credential Found
       |
       v
Credential Belongs to
Privileged Identity?
       |
       v
Authorised Validation
       |
       v
Higher Privilege
```

Avoid unnecessary password reuse testing across large numbers of systems.


---

# Service Accounts

Service accounts often deserve attention because they may have:

```text
Local administrative access

Server access

Database access

Application privileges

Domain privileges

Cloud permissions
```

The finding should focus on excessive privilege or credential exposure rather than the existence of the service account.


---

# Automated Enumeration

Automated tools can help identify candidate paths.

Examples include:

```text
WinPEAS

Seatbelt

SharpUp

LinPEAS

LinEnum

BloodHound
```

Use tools only where permitted by the Rules of Engagement.


---

# Automation Does Not Replace Analysis

```text
Scanner Output
     |
     v
Candidate
     |
     v
Manual Review
     |
     v
Preconditions
     |
     v
Safe Validation
     |
     v
Finding
```


---

# PrivEsc Explorer

Your integrated PrivEsc Explorer can be used as a fast decision layer:

[PrivEsc Explorer](../privesc/)

Windows:

[Windows PrivEsc Explorer](../privesc/windows.md)

Linux:

[Linux PrivEsc Explorer](../privesc/linux.md)

Use it to move from:

```text
"What did I find?"
```

to:

```text
"What should I validate next?"
```


---

# Privilege Escalation Prioritisation

Prioritise candidates based on:

```text
Privilege gained

Reliability

Required access

Operational risk

Need for restart

Need for user interaction

Security-control impact

Detection risk

Business criticality

Reversibility
```


---

# Preferred Path

When multiple paths exist, prefer:

```text
Lowest Risk

Least Modification

Most Reversible

Strongest Evidence

Lowest Business Impact
```


---

# Example

Suppose enumeration identifies:

```text
Candidate A:
Writable SYSTEM service executable

Candidate B:
Potential kernel vulnerability

Candidate C:
Exposed administrative credential
```

A reasonable decision model is:

```text
Can C safely demonstrate privilege?
        |
       Yes
        |
        v
Use C before attempting a kernel exploit.
```

The goal is proof, not maximum exploitation complexity.


---

# Safe Validation Ladder

```text
1. Configuration Review

2. Permission Review

3. Read Test

4. Temporary Write Test

5. Policy Query

6. Harmless Execution Test

7. Controlled Privilege Validation

8. Higher-Risk Technique Only If Necessary
```


---

# Minimal Proof

Examples of sufficient proof may include:

```text
Reading a protected test marker

Creating a harmless file in an authorised protected test location

Demonstrating elevated identity

Accessing a customer-provided objective marker
```

Avoid accessing unrelated sensitive information merely because elevated privilege permits it.


---

# Windows Elevated Identity

After authorised elevation:

```powershell
whoami
```

```powershell
whoami /all
```

Record the changed security context.


---

# Linux Elevated Identity

```bash
id
```

A result containing:

```text
uid=0(root)
```

demonstrates root context.

Further destructive proof is unnecessary.


---

# Proof Marker

A customer can pre-position a harmless marker.

Windows example:

```text
C:\RedTeamValidation\privilege-objective.txt
```

Linux:

```text
/opt/redteam-validation/privilege-objective.txt
```

The objective can then be:

```text
Demonstrate authorised read access to the marker.
```

This avoids accessing real sensitive data.


---

# Detection Validation

Privilege escalation should also test defensive visibility.

Relevant telemetry may include:

```text
Process creation

Service modification

Scheduled tasks

Privilege use

Authentication

Group modification

Sudo

File modification

Registry modification

Directory-service changes

Cloud audit logs
```


---

# Windows Security Events

Potentially useful events include:

```text
4672 - Special privileges assigned to new logon

4688 - New process created

4697 - Service installed

4698 - Scheduled task created

4728 - Member added to global security group

4732 - Member added to local security group

4756 - Member added to universal security group
```

Exact relevance depends on the technique and audit configuration.


---

# Service Telemetry

Defenders should monitor:

```text
Service creation

Service configuration changes

Service executable changes

Unusual service accounts

Unexpected service starts
```


---

# Scheduled Task Telemetry

Monitor:

```text
Task creation

Task modification

Execution identity

Referenced executable

Command line

Task origin
```


---

# Linux Detection

Potential sources:

```text
auth.log

secure

auditd

journald

sudo logs

EDR

File-integrity monitoring
```


---

# sudo Logging

Depending on the distribution:

```bash
journalctl _COMM=sudo
```

or:

```bash
grep sudo /var/log/auth.log
```

Use only where the log exists and access is authorised.


---

# Active Directory Detection

Monitor:

```text
Group membership changes

Directory ACL changes

GPO modifications

Certificate enrolment

Delegation changes

Computer-object changes

Privileged authentication
```


---

# Cloud Detection

Monitor:

```text
Role assignments

Policy modifications

New credentials

Service-principal changes

Secret access

Token activity

Resource modifications

Audit-log changes
```


---

# Detection Outcome

Classify:

```text
Prevented

Allowed and Detected

Allowed and Logged

Allowed without Alert

No Useful Visibility
```


---

# Evidence

For each validated escalation path record:

```text
Finding ID

Host

Starting Identity

Starting Privilege

Candidate

Preconditions

Validation

Resulting Identity

Resulting Privilege

Timestamp

Security Control

Telemetry

Alert

Cleanup
```


---

# Evidence Example

```text
Finding:
PRIV-003

Host:
APP01

Starting Identity:
CORP\test-user

Starting Privilege:
Standard user

Condition:
Privileged service referenced a user-writable application
directory.

Validation:
Temporary harmless validation artifact used.

Result:
Privileged execution boundary confirmed.

Resulting Context:
SYSTEM

Detection:
Process telemetry present.

Alert:
No alert observed.

Cleanup:
Validation artifact removed.
```


---

# Attack Path Evidence

Privilege escalation should be connected to the wider attack path.

Example:

```text
External Access
      |
      v
WS01 Standard User
      |
      v
Credential Exposure
      |
      v
APP01 Standard User
      |
      v
Writable Service Resource
      |
      v
APP01 SYSTEM
      |
      v
Privileged Credential
      |
      v
Server Environment
```


---

# Finding Titles

Good:

```text
Standard Users Can Modify Resource Executed by SYSTEM Service

Privileged Scheduled Task References User-Writable Script

Excessive Sudo Permission Enables Root-Level Operations

Docker Daemon Access Grants Host-Level Administrative Control

Active Directory ACL Grants Unintended Control Over Privileged Group
```

Avoid:

```text
WinPEAS Finding

GTFOBins Exploit

PowerShell PrivEsc

BloodHound Vulnerability
```


---

# Impact

Explain the actual boundary crossed.

Example:

```text
A standard user who gains execution on the affected server can
modify a resource subsequently executed by a service running as
LocalSystem.

Successful exploitation provides operating-system-level
administrative control of the affected server.
```


---

# Root Cause

Common root causes include:

```text
Excessive file permissions

Excessive directory permissions

Overprivileged service account

Unsafe scheduled execution

Excessive sudo permission

Unnecessary capabilities

Weak administrative tiering

Credential reuse

Excessive group membership

Overly permissive ACL

Cloud IAM misconfiguration

Application authorisation failure
```


---

# Severity

Consider:

```text
Starting privilege

Resulting privilege

Asset criticality

Required interaction

Reliability

Network prerequisites

Credential prerequisites

Detection

Attack-path significance
```


---

# Severity Example

A local escalation from:

```text
Standard User -> SYSTEM
```

may be High in one environment.

But if the affected system is:

```text
Domain Controller
```

and the path materially enables domain compromise, the overall attack-path impact may be Critical.

Severity should reflect context.


---

# Remediation - Windows

Common improvements:

```text
Correct service permissions

Correct file permissions

Correct directory permissions

Secure scheduled tasks

Remove unnecessary privileges

Restrict local administrator membership

Deploy LAPS

Enforce application control

Reduce credential exposure

Patch vulnerable software

Monitor privileged execution
```


---

# Remediation - Linux

Common improvements:

```text
Restrict sudo rules

Remove unnecessary SUID/SGID

Remove unnecessary capabilities

Correct file ownership

Correct directory permissions

Secure cron jobs

Secure systemd units

Protect secrets

Restrict Docker access

Patch vulnerable components

Monitor privileged execution
```


---

# Remediation - Active Directory

Common improvements:

```text
Reduce privileged group membership

Correct ACLs

Implement administrative tiering

Protect service accounts

Use gMSA where appropriate

Deploy LAPS

Review delegation

Harden AD CS

Protect GPOs

Monitor privileged changes
```


---

# Remediation - Cloud

Common improvements:

```text
Least-privilege IAM

Restrict role assignment

Protect service principals

Use managed identities

Rotate exposed credentials

Use short-lived credentials

Restrict secret access

Monitor privilege changes

Separate administrative identities
```


---

# Retesting

After remediation:

```text
Repeat Enumeration
      |
      v
Confirm Permission Changed
      |
      v
Repeat Minimal Validation
      |
      v
Boundary Prevented?
      |
      v
Detection Verified?
```


---

# Retest Status

Use:

```text
Resolved

Partially Resolved

Not Resolved

Not Retested

Risk Accepted
```


---

# Cleanup

Remove all artifacts introduced during validation.

Possible artifacts:

```text
Temporary files

Test binaries

Scripts

Services

Scheduled tasks

Registry values

Accounts

Group membership

SSH keys

Cloud identities

Certificates

Permission changes
```


---

# Cleanup Verification

Do not assume cleanup succeeded.

Verify:

```text
Artifact removed

Original permissions restored

Original service configuration restored

Original task configuration restored

Temporary account removed

Temporary role removed

No active session remains
```


---

# Privilege Escalation Checklist

## Context

- [ ] Current user recorded
- [ ] Current groups recorded
- [ ] Current privileges recorded
- [ ] Host recorded
- [ ] Domain recorded
- [ ] Operating system recorded
- [ ] Security controls recorded

## Windows

- [ ] Services reviewed
- [ ] Service accounts reviewed
- [ ] Service paths reviewed
- [ ] File permissions reviewed
- [ ] Directory permissions reviewed
- [ ] Scheduled tasks reviewed
- [ ] User privileges reviewed
- [ ] Local groups reviewed
- [ ] Registry permissions reviewed where relevant
- [ ] Installed applications reviewed
- [ ] Processes reviewed
- [ ] PATH reviewed
- [ ] Credential sources reviewed
- [ ] Application control considered
- [ ] UAC context understood

## Linux

- [ ] `sudo -l` reviewed
- [ ] SUID reviewed
- [ ] SGID reviewed
- [ ] Capabilities reviewed
- [ ] Cron reviewed
- [ ] systemd reviewed
- [ ] File permissions reviewed
- [ ] PATH reviewed
- [ ] Processes reviewed
- [ ] Listening services reviewed
- [ ] Environment reviewed
- [ ] Credentials reviewed
- [ ] SSH configuration reviewed
- [ ] Container context reviewed
- [ ] Docker access reviewed
- [ ] Kernel exposure considered

## Active Directory

- [ ] Group memberships reviewed
- [ ] Nested groups considered
- [ ] ACL paths reviewed
- [ ] BloodHound paths reviewed
- [ ] Delegation reviewed where relevant
- [ ] Kerberos relationships reviewed
- [ ] GPO permissions reviewed
- [ ] AD CS reviewed where present
- [ ] Credential paths considered

## Cloud

- [ ] Current identity identified
- [ ] Current roles identified
- [ ] Resource permissions reviewed
- [ ] Role-assignment permissions reviewed
- [ ] Service identities reviewed
- [ ] Secret access reviewed
- [ ] Automation identities reviewed
- [ ] Scope boundaries confirmed

## Validation

- [ ] Candidate identified
- [ ] Preconditions validated
- [ ] Security boundary identified
- [ ] Lowest-risk validation selected
- [ ] Customer impact considered
- [ ] Stop condition understood
- [ ] Resulting privilege confirmed

## Detection

- [ ] Timestamp recorded
- [ ] Endpoint telemetry reviewed
- [ ] Authentication telemetry reviewed
- [ ] SIEM visibility reviewed
- [ ] Alert status recorded
- [ ] SOC response recorded
- [ ] Detection gap classified

## Evidence

- [ ] Starting context recorded
- [ ] Candidate recorded
- [ ] Preconditions recorded
- [ ] Validation recorded
- [ ] Resulting context recorded
- [ ] Evidence captured
- [ ] Sensitive data redacted
- [ ] Cleanup recorded


---

# Quick Reference - Windows

## Identity

```powershell
whoami /all
```


## Local Administrators

```powershell
Get-LocalGroupMember -Group Administrators
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


## Privileges

```powershell
whoami /priv
```


## Processes

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId,ParentProcessId,Name,ExecutablePath
```


## PATH

```powershell
$env:PATH -split ';'
```


## Credential Manager

```cmd
cmdkey /list
```


## AppLocker

```powershell
(Get-AppLockerPolicy -Effective).RuleCollections |
    Select-Object CollectionType,EnforcementMode
```


---

# Quick Reference - Linux

## Identity

```bash
id
```


## Sudo

```bash
sudo -l
```


## SUID

```bash
find / -perm -4000 -type f 2>/dev/null
```


## SGID

```bash
find / -perm -2000 -type f 2>/dev/null
```


## Capabilities

```bash
getcap -r / 2>/dev/null
```


## Cron

```bash
cat /etc/crontab
```


## systemd Services

```bash
systemctl --type=service --state=running
```


## systemd Timers

```bash
systemctl list-timers --all
```


## Processes

```bash
ps aux
```


## Network

```bash
ss -lntup
```


## PATH

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```


## Docker Socket

```bash
ls -l /var/run/docker.sock
```


---

# Privilege Escalation Decision Model

```text
                    Current Context
                          |
                          v
                      Enumerate
                          |
                          v
                  Candidate Found?
                    /          \
                  No            Yes
                  |              |
                  v              v
             Continue Recon   Preconditions
                                 Present?
                                /       \
                              No         Yes
                              |           |
                              v           v
                           Reject      Boundary?
                                        /    \
                                      No      Yes
                                      |        |
                                      v        v
                                   Record   Risk Acceptable?
                                             /       \
                                           No         Yes
                                           |           |
                                          STOP         v
                                               Minimal Validation
                                                      |
                                                      v
                                                  Success?
                                                  /     \
                                                No       Yes
                                                |         |
                                                v         v
                                             Record    Confirm
                                                       Privilege
                                                          |
                                                          v
                                                       Evidence
                                                          |
                                                          v
                                                       Cleanup
```


---

# Attack Path Decision Model

```text
                  Privilege Obtained
                         |
                         v
                 Engagement Objective?
                    /           \
                  Yes            No
                  |               |
                  v               v
              Validate          New Access?
              Objective         /       \
                              No         Yes
                              |           |
                              v           v
                            Stop      Re-Enumerate
                                         |
                                         v
                                  Credential Access
                                         |
                                         v
                                  Lateral Movement
                                         |
                                         v
                                     Objective
```


---

# Defensive Model

```text
                  PRIVILEGE ESCALATION
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
       Prevent           Detect          Respond
           |               |               |
           v               v               v
      Permissions      Processes        Investigate
      Least Privilege  Services         Contain
      Patching         Tasks            Revoke
      App Control      Auth             Remediate
      Segmentation     IAM
           |               |               |
           +---------------+---------------+
                           |
                           v
                      Risk Reduction
```


---

# Final Privilege Escalation Model

```text
                       FOOTHOLD
                          |
                          v
                    CURRENT USER
                          |
                          v
                  CURRENT PRIVILEGE
                          |
                          v
                     ENUMERATION
                          |
                          v
                 CANDIDATE PATHS
                          |
                          v
                    PRECONDITIONS
                          |
                          v
                   SECURITY BOUNDARY
                          |
                          v
                   MINIMAL VALIDATION
                          |
                          v
                  ELEVATED CONTEXT
                          |
             +------------+------------+
             |                         |
             v                         v
         TELEMETRY                 ATTACK PATH
             |                         |
             v                         v
         DETECTION                 OBJECTIVE
             |                         |
             +------------+------------+
                          |
                          v
                       EVIDENCE
                          |
                          v
                       CLEANUP
                          |
                          v
                      REPORTING
```


---

# Core Principle

Privilege escalation testing can be reduced to:

```text
Understand the current identity.

Understand the current privilege.

Enumerate before exploiting.

Identify the exact security boundary.

Validate every prerequisite.

Separate candidates from confirmed findings.

Prefer the lowest-risk path.

Use harmless validation where possible.

Do not access sensitive data unnecessarily.

Confirm the resulting privilege.

Determine what defenders observed.

Preserve sufficient evidence.

Remove introduced artifacts.

Explain the root cause.

Connect the escalation to the wider attack path.
```


---

# Related Notes

- [Red Teaming](./)
- [Red Team Methodology](methodology.md)
- [Reconnaissance](reconnaissance.md)
- [Initial Access](initial-access.md)
- [Execution](execution.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Red Team Reporting](reporting.md)
- [Windows Privilege Escalation](../windows/privilege-escalation.md)
- [Linux Privilege Escalation](../linux/privilege-escalation.md)
- [PrivEsc Explorer](../privesc/)
- [Windows PrivEsc Explorer](../privesc/windows.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Active Directory](../active-directory/)
- [BloodHound](../active-directory/bloodhound.md)
- [AD ACL and ACE](../active-directory/acl-ace.md)
- [AD CS](../active-directory/ad-cs/)


---

# References

- [MITRE ATT&CK - Privilege Escalation](https://attack.mitre.org/tactics/TA0004/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Abuse Elevation Control Mechanism](https://attack.mitre.org/techniques/T1548/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Valid Accounts](https://attack.mitre.org/techniques/T1078/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Services](https://attack.mitre.org/techniques/T1569/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Exploitation for Privilege Escalation](https://attack.mitre.org/techniques/T1068/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Account Manipulation](https://attack.mitre.org/techniques/T1098/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [LOLBAS](https://lolbas-project.github.io/){ target="_blank" rel="noopener noreferrer" }
- [BloodHound](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Security](https://learn.microsoft.com/windows/security/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - User Account Control](https://learn.microsoft.com/windows/security/application-security/application-control/user-account-control/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - App Control for Business](https://learn.microsoft.com/windows/security/application-security/application-control/app-control-for-business/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows LAPS](https://learn.microsoft.com/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Active Directory Domain Services](https://learn.microsoft.com/windows-server/identity/ad-ds/active-directory-domain-services){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Active Directory Certificate Services](https://learn.microsoft.com/windows-server/identity/ad-cs/active-directory-certificate-services-overview){ target="_blank" rel="noopener noreferrer" }
- [Linux capabilities - capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [sudo](https://www.sudo.ws/){ target="_blank" rel="noopener noreferrer" }
- [Docker Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }


---

!!! tip "Privilege escalation is a relationship"
    A writable file, SUID binary, Windows privilege, sudo rule, Active Directory ACL, or cloud role is not automatically a vulnerability. The important question is whether the current identity can use that condition to cross a security boundary and obtain authority it should not possess.


!!! warning "Stop when the boundary is proven"
    Obtaining SYSTEM, root, a privileged domain identity, or an equivalent cloud or application privilege is usually sufficient evidence that the escalation path exists. Do not perform additional destructive actions or access unrelated sensitive information simply because the elevated context makes it possible.
