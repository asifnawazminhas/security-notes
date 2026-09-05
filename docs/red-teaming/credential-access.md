---
title: Credential Access
description: Credential access methodology for authorised red team assessments, covering passwords, hashes, Kerberos tickets, tokens, secrets, credential stores, Windows and Linux sources, cloud credentials, detection, evidence, remediation, and safe handling.
---

# Credential Access

Credential access is the process of identifying and validating authentication material that may provide access to systems, applications, services, or identities during an authorised security assessment.

Credential material can include much more than passwords.

```text
Credential Material
        |
        +--> Passwords
        |
        +--> Password Hashes
        |
        +--> Kerberos Tickets
        |
        +--> Access Tokens
        |
        +--> API Keys
        |
        +--> SSH Keys
        |
        +--> Cloud Credentials
        |
        +--> Application Secrets
        |
        +--> Service Credentials
        |
        +--> Certificates
        |
        +--> Session Material
```

Credential access is often one of the most sensitive phases of a red team assessment.

A credential obtained from one authorised system may provide technical access to systems outside the approved scope.

Technical access does not extend authorisation.


---

# Credential Access Objectives

Credential access testing should answer questions such as:

```text
Where is authentication material exposed?
Which identities are affected?
Why was the material accessible?
What privilege was required to access it?
Can the material actually be used?
What systems trust the credential?
What defensive controls observed access?
How should the exposure be remediated?
```

The objective is not to collect the largest possible number of credentials.

Collect and validate only what is necessary to demonstrate the agreed security impact.


---

# Credential Access Model

A useful workflow is:

```text
Current Access
      |
      v
Identify Credential Sources
      |
      v
Credential Candidate
      |
      v
Determine Owner
      |
      v
Determine Scope
      |
      v
Validation Authorised?
    /       \
  No         Yes
  |           |
  v           v
Document   Minimal Validation
              |
              v
         Determine Impact
              |
              v
         Protect Evidence
              |
              v
            Cleanup
```


---

# Credential Types

Credential material can be divided into several broad categories.

| Type | Examples |
|---|---|
| Password | User or service password |
| Hash | NTLM or application password hash |
| Kerberos material | TGT, TGS, key material |
| Token | OAuth, API, session or access token |
| Private key | SSH or application key |
| Certificate | Client or authentication certificate |
| Cloud credential | Access key, secret, service principal |
| Application secret | Database password, connection string |
| Browser/session material | Session token or stored credential |
| Configuration secret | Secret embedded in a file or deployment configuration |

The security impact depends on what trusts the credential.


---

# Credential Sources

Potential credential sources include:

```text
Files
Configuration
Environment variables
Shell history
PowerShell history
Credential stores
Browser storage
Process environment
Service configuration
Scheduled tasks
Deployment scripts
Repositories
CI/CD systems
Backups
Shares
Cloud configuration
Application databases
Memory
Directory services
```

Not every source should be accessed during every assessment.


---

# Credential Discovery Workflow

```text
Host Access
    |
    v
Establish Current Privilege
    |
    v
Identify Applications and Services
    |
    v
Review Likely Credential Locations
    |
    v
Find Candidate Secret
    |
    v
Determine Identity
    |
    v
Determine Trust Boundary
    |
    v
Minimal Validation
```


---

# Credential Handling

Treat discovered credentials as sensitive information.

Do not:

```text
Paste credentials into public tickets
Store credentials in public Git repositories
Send credentials through unapproved messaging systems
Reuse credentials outside scope
Keep unnecessary copies
Include plaintext passwords in reports unless required
```

Prefer evidence that proves the issue without unnecessarily exposing the complete secret.


---

# Credential Inventory

During a substantial engagement, maintain a controlled inventory.

Example:

| ID | Type | Identity | Source | Validation | Cleanup |
|---|---|---|---|---|---|
| `CRED-001` | Password | Test service account | Configuration | Validated | Rotation required |
| `CRED-002` | SSH key | Test administrator | Home directory | Not validated | Customer review |
| `CRED-003` | API token | Test application | Environment | Validated | Revoke |

Avoid storing plaintext secrets in the inventory itself.


---

# Credential Validation

A discovered secret is not automatically valid.

```text
Secret Found
    |
    v
Identify Type
    |
    v
Identify Owner
    |
    v
Identify Intended Service
    |
    v
Check Scope
    |
    v
Minimal Authentication Test
    |
    +--> Fails
    |
    +--> Works
```

Record the result without performing unnecessary follow-on actions.


---

# Minimal Validation

If a credential is believed to provide access to an authorised service, minimal validation may be sufficient.

Examples include:

```text
Successful authentication
Identity confirmation
Permission query
Access to an approved synthetic object
```

Avoid downloading data merely to prove that authentication succeeded.


---

# Windows Credential Sources

Windows systems may expose authentication material through several locations.

Common assessment areas include:

```text
Credential Manager
PowerShell history
Environment variables
Configuration files
Unattended installation files
Service configuration
Scheduled tasks
Registry
Application configuration
Browser storage
Network shares
Backup files
Process context
LSA-managed secrets
Kerberos material
Local account material
```


---

# Windows Identity Context

Before investigating credentials, establish the current identity.

```cmd
whoami
```

```cmd
whoami /all
```

PowerShell:

```powershell
whoami /all
```

Review current privileges:

```powershell
whoami /priv
```

Review groups:

```powershell
whoami /groups
```

Credential accessibility often depends heavily on the current security context.


---

# Windows Credential Manager

Windows Credential Manager can contain stored credentials used by applications and network resources.

Enumerate stored credential targets using:

```cmd
cmdkey /list
```

The output may identify:

```text
Target
Credential type
Username
Persistence
```

A listed credential should be treated as a credential-access candidate rather than automatic proof that the secret can be extracted or reused.


---

# PowerShell History

PowerShell command history can unintentionally contain:

```text
Passwords
Tokens
Connection strings
Administrative commands
API keys
Remote hostnames
Credentials passed as arguments
```

The commonly used PSReadLine history path can be obtained with:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Review the configured path:

```powershell
$historyPath = (Get-PSReadLineOption).HistorySavePath
$historyPath
```

If authorised to inspect it:

```powershell
Get-Content -LiteralPath (Get-PSReadLineOption).HistorySavePath
```

Do not assume every password-like string remains valid.


---

# Environment Variables

Applications and deployment processes sometimes expose secrets through environment variables.

PowerShell:

```powershell
Get-ChildItem Env:
```

Command Prompt:

```cmd
set
```

Look for variables associated with:

```text
API
TOKEN
SECRET
PASSWORD
PASS
KEY
DATABASE
AWS
AZURE
GITHUB
CI
```

Context is required because many values are identifiers rather than secrets.


---

# Configuration Files

Potential Windows configuration files include:

```text
web.config
app.config
*.config
*.xml
*.json
*.ini
*.yml
*.yaml
.env
connectionStrings.config
```

Common locations include:

```text
C:\inetpub\
C:\ProgramData\
C:\Program Files\
C:\Program Files (x86)\
Application-specific directories
User profile directories
```

Search should be targeted rather than recursively reading every file on the host.


---

# Unattended Installation Files

Windows deployment processes may leave configuration files containing historical credentials.

Potential filenames include:

```text
Unattend.xml
Autounattend.xml
sysprep.xml
sysprep.inf
```

Possible locations can include:

```text
C:\Windows\Panther\
C:\Windows\Panther\Unattend\
C:\Windows\System32\Sysprep\
```

The presence of a file does not mean it contains credentials.


---

# Services

Windows services can reveal useful identity information.

Enumerate:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, State, PathName
```

Service identities may include:

```text
LocalSystem
LocalService
NetworkService
Domain service accounts
Managed service accounts
Custom local accounts
```

A service running as a privileged identity does not mean its password is retrievable.


---

# Scheduled Tasks

Scheduled tasks can reveal:

```text
Execution identity
Scripts
Arguments
Executable paths
Configuration references
Network paths
```

Enumerate:

```cmd
schtasks /query /fo LIST /v
```

PowerShell:

```powershell
Get-ScheduledTask
```

Focus on tasks relevant to the current attack path.


---

# Registry

The Windows Registry may contain application or deployment configuration.

Searches should be targeted to known applications or specific candidate locations.

Examples of useful contextual information include:

```text
Service configuration
Application configuration
AutoLogon configuration
Software settings
Installed products
```

Registry access should not be treated as unrestricted credential discovery.


---

# AutoLogon

Windows can be configured for automatic logon.

Relevant configuration may exist under:

```text
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
```

Inspect selected values:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' |
    Select-Object AutoAdminLogon, DefaultUserName, DefaultDomainName
```

If sensitive values are exposed to the current user, document the access condition and impact.

Do not assume AutoLogon is enabled solely because a username value exists.


---

# Network Shares

Configuration and deployment shares can contain sensitive information.

Examples include:

```text
Scripts
Configuration files
Backups
Deployment packages
Documentation
Legacy installers
```

Access should be limited to shares within scope and to material relevant to the assessment.


---

# Windows Credential Stores and Memory

Some Windows authentication material is protected by privileged operating-system components.

Examples can include:

```text
LSASS-managed authentication material
Kerberos tickets
LSA secrets
Local account hashes
DPAPI-protected secrets
```

Accessing these areas can require elevated privileges and may trigger defensive controls.

Use such testing only when explicitly required by the engagement objective.


---

# LSASS

The Local Security Authority Subsystem Service is central to Windows authentication.

Defensive technologies may monitor or protect access using controls such as:

```text
EDR
Microsoft Defender
Credential Guard
LSA protection
Attack Surface Reduction
Process access monitoring
```

From a red team perspective, the important questions are:

```text
Is credential material adequately protected?
Can an inappropriate process access sensitive authentication state?
Was the attempt prevented?
Was it detected?
```


---

# Credential Guard

Credential Guard uses virtualization-based security to help isolate certain authentication secrets.

Check relevant security configuration through approved system-management interfaces and defensive tooling.

Do not report the absence of Credential Guard as a vulnerability by itself.

Evaluate it as part of the overall credential protection model.


---

# LSA Protection

LSA protection can provide additional protection for LSASS.

It should be considered together with:

```text
Credential Guard
EDR
Application control
Administrative privilege management
Attack Surface Reduction
Patch management
```


---

# Kerberos Credentials

In Active Directory environments, authentication material may include:

```text
Ticket Granting Tickets
Service Tickets
Session keys
Long-term account keys
```

Kerberos material can have substantial security impact.

Use the dedicated Active Directory notes for detailed Kerberos assessment.

[Kerberos](../active-directory/kerberos.md)

[Kerberos Tickets](../active-directory/kerberos-tickets.md)


---

# NTLM

NTLM-related authentication material may include password-derived hashes or challenge-response material.

The impact depends on:

```text
Protocol
Credential type
Target
Signing requirements
Authentication policy
Account privilege
Network controls
```

Use:

[NTLM](../active-directory/ntlm.md)


---

# Linux Credential Sources

Linux systems may expose credentials through:

```text
Shell history
Environment variables
Configuration files
SSH keys
Service configuration
Application configuration
Cron jobs
systemd units
Backup files
Git repositories
Cloud configuration
Container configuration
Mounted filesystems
Process environments
```


---

# Linux Identity Context

Start with:

```bash
whoami
```

```bash
id
```

Review groups:

```bash
groups
```

Determine the home directory:

```bash
echo "$HOME"
```

Understand the current user's permissions before inspecting credential sources.


---

# Shell History

Shell history may contain security-sensitive commands.

Potential files include:

```text
~/.bash_history
~/.zsh_history
~/.python_history
```

Review your authorised user's Bash history:

```bash
cat ~/.bash_history
```

History may reveal:

```text
Passwords passed on command lines
SSH destinations
Database commands
API tokens
Administrative commands
Internal hostnames
```

Historical entries should be validated carefully because they may be obsolete.


---

# Linux Environment Variables

Inspect:

```bash
env
```

or:

```bash
printenv
```

Potentially sensitive variable names can include:

```text
PASSWORD
TOKEN
SECRET
KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
DATABASE_URL
GITHUB_TOKEN
```

Do not assume a variable is sensitive based solely on its name.


---

# Linux Configuration Files

Common locations include:

```text
/etc/
/opt/
/srv/
/var/www/
/home/
/usr/local/
```

Application configuration may use:

```text
.env
config.php
settings.py
application.yml
application.yaml
config.json
database.yml
*.ini
*.conf
```

Search should remain targeted.


---

# SSH Keys

SSH credentials may exist under:

```text
~/.ssh/
```

Common files include:

```text
id_rsa
id_ed25519
id_ecdsa
authorized_keys
known_hosts
config
```

List:

```bash
ls -la ~/.ssh/
```

Private keys are sensitive authentication material.

Do not attempt to use a discovered key until its ownership, target, and scope are understood.


---

# SSH Configuration

SSH configuration can identify infrastructure relationships.

Review:

```bash
cat ~/.ssh/config
```

Potentially useful information includes:

```text
Host aliases
Usernames
Jump hosts
Identity files
Internal systems
Ports
```

This information may be valuable even when no private key is exposed.


---

# Service Configuration

Linux services frequently obtain credentials from:

```text
Environment files
Configuration files
systemd unit variables
Secret stores
Container configuration
```

Inspect service metadata where authorised:

```bash
systemctl list-units --type=service
```

For a specific service:

```bash
systemctl cat SERVICE
```

Look for references to configuration rather than assuming secrets are embedded directly in the unit.


---

# systemd Environment Files

A service unit may reference an environment file.

Conceptually:

```text
Service Unit
     |
     v
EnvironmentFile
     |
     v
Application Secret
```

If the current user can read a privileged service's environment file, evaluate whether sensitive information is actually exposed.


---

# Cron

Cron jobs may reference:

```text
Scripts
Configuration
Backup credentials
Database credentials
Remote systems
```

Review:

```bash
cat /etc/crontab
```

and relevant files under:

```text
/etc/cron.d/
```

The focus should be on relevant credential paths rather than broad data collection.


---

# Git Repositories

Git repositories can expose secrets in:

```text
Current files
Previous commits
Deleted files
Branches
Configuration
Remote URLs
```

Check repository status:

```bash
git status
```

Review remotes:

```bash
git remote -v
```

Secret exposure can remain in repository history even after deletion from the latest version.


---

# Application Credentials

Applications often require credentials for:

```text
Databases
Message queues
APIs
Cloud services
SMTP
Storage
Directory services
Third-party integrations
```

A common trust chain is:

```text
Application
    |
    v
Configuration
    |
    v
Credential
    |
    v
Backend Service
```

The security impact depends on the privileges of the backend identity.


---

# Database Credentials

Database credentials may appear in:

```text
Connection strings
Environment variables
Application configuration
Deployment scripts
Secret stores
```

When discovered:

```text
Identify Database
      |
      v
Identify Account
      |
      v
Confirm Scope
      |
      v
Minimal Authentication
      |
      v
Determine Privilege
```

Avoid enumerating or exporting production datasets unnecessarily.


---

# API Keys

API keys can provide access to:

```text
Cloud services
SaaS platforms
Internal APIs
CI/CD systems
Monitoring systems
Developer platforms
Third-party services
```

Determine:

```text
Provider
Owner
Scope
Permissions
Expiry
Environment
```

A production third-party API key may cross an engagement boundary.


---

# Tokens

Tokens may represent:

```text
Application sessions
OAuth access
API authentication
CI/CD authentication
Cloud sessions
Service-to-service authentication
```

Unlike passwords, some tokens may be:

```text
Short lived
Scoped
Device bound
Audience restricted
Revocable
```

Understand the token before attempting validation.


---

# OAuth Tokens

OAuth environments may involve:

```text
Access token
Refresh token
ID token
Client secret
Authorization code
```

These objects have different purposes.

An ID token, for example, should not automatically be treated as equivalent to an API access token.


---

# JWTs

JSON Web Tokens can contain useful claims such as:

```text
Issuer
Audience
Subject
Roles
Scopes
Expiry
```

Decode for inspection using approved tooling without assuming that decoding implies compromise.

The security impact depends on signature validation, claims handling, token scope, and application behaviour.

Use:

[JWT](../web/jwt/)


---

# Cloud Credentials

Cloud authentication material can include:

```text
Access keys
Secret keys
Session tokens
Service principals
Application secrets
Certificates
Managed identity tokens
CLI credentials
Federated tokens
```

Cloud credentials can have a very large blast radius.

Always identify the account or tenant before validation.


---

# AWS Credential Locations

Potential developer-side AWS configuration can exist under:

```text
~/.aws/credentials
~/.aws/config
```

Inspect only where authorised:

```bash
ls -la ~/.aws/
```

Environment variables may also contain temporary AWS authentication material.


---

# Azure and Entra ID Credentials

Potential credential material can include:

```text
User tokens
Service principal secrets
Application certificates
CLI authentication state
Managed identity tokens
Automation credentials
```

Cloud identity testing should remain restricted to the explicitly authorised tenant.


---

# CI/CD Credentials

CI/CD systems frequently require powerful credentials.

Potential examples include:

```text
Repository tokens
Cloud deployment credentials
Container registry credentials
Package registry tokens
SSH deployment keys
Signing credentials
API tokens
```

These credentials can bridge development and production environments.


---

# CI/CD Trust Chain

```text
Developer
    |
    v
Repository
    |
    v
CI/CD
    |
    v
Deployment Credential
    |
    v
Production
```

A credential exposed at the CI/CD layer can therefore have significantly greater impact than a normal developer credential.


---

# Containers

Containers may expose secrets through:

```text
Environment variables
Mounted files
Configuration
Orchestration secrets
Image layers
Build arguments
Application files
```

Inspect only resources accessible from the authorised container context.


---

# Docker

Useful contextual information includes:

```bash
docker ps
```

where the current user is authorised to access Docker.

Container inspection may reveal environment configuration:

```bash
docker inspect CONTAINER
```

Docker access itself can be highly privileged on many systems, so use the dedicated Linux privilege escalation notes when assessing that condition.


---

# Kubernetes

Kubernetes environments can involve:

```text
Service account tokens
Kubeconfig
Secrets
Cloud identities
Registry credentials
Certificates
```

Credential access in Kubernetes should be assessed within the authorised cluster and namespace scope.

Do not assume cluster-wide access is authorised simply because a token technically permits it.


---

# Browser Credentials and Sessions

Browsers may store:

```text
Saved passwords
Cookies
Session tokens
Client certificates
Autofill information
Application state
```

Browser credential testing is highly sensitive.

It should only be performed when directly relevant to the engagement objective and explicitly permitted.


---

# Password Managers

Enterprise password managers can significantly reduce insecure credential storage.

However, their security depends on:

```text
Authentication
MFA
Vault policy
Session controls
Device trust
Sharing configuration
Administrative roles
Recovery process
```

The presence of a password manager is generally a positive control and should not itself be treated as an attack target unless included in scope.


---

# Password Reuse

Password reuse can turn one exposed credential into a broader attack path.

```text
Credential Exposure
       |
       v
Account A
       |
       +--> Service 1
       |
       +--> Service 2
       |
       +--> Service 3
```

Reuse testing should be carefully scoped because the same credential may work against unrelated or third-party services.


---

# Service Accounts

Service accounts often deserve additional attention because they may have:

```text
Long-lived credentials
Non-interactive use
Broad access
Weak rotation
Legacy configurations
Elevated privileges
Multiple dependent systems
```

Prefer managed identities or managed service-account technologies where available.


---

# gMSA

Group Managed Service Accounts can reduce risks associated with manually managed service-account passwords in Active Directory.

Benefits include:

```text
Automatic password management
Long random passwords
Reduced manual handling
Controlled password retrieval
```

Use the dedicated notes:

[gMSA](../active-directory/gmsa.md)


---

# LAPS

Windows LAPS helps manage unique local administrator passwords.

A strong LAPS deployment reduces the blast radius of local administrator credential reuse.

Use:

[LAPS](../active-directory/laps.md)


---

# Credential Reuse and Lateral Movement

Credential access frequently connects directly to lateral movement.

```text
Credential
    |
    v
Identify Trust
    |
    v
Scope Check
    |
    v
Remote Authentication
    |
    v
Lateral Movement
```

Use:

[Lateral Movement](lateral-movement.md)


---

# Credential Access and Privilege Escalation

Credentials can also provide privilege escalation.

```text
Low-Privilege User
       |
       v
Exposed Credential
       |
       v
Privileged Local Account
       |
       v
Elevated Access
```

Use:

- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)


---

# Credential Access and Active Directory

Active Directory introduces additional credential and authentication concepts:

```text
NTLM
Kerberos
Service accounts
Machine accounts
Delegation
gMSA
LAPS
Certificates
Directory ACLs
Trust relationships
```

Use:

[Active Directory](../active-directory/)


---

# Credential Access and AD CS

Certificates and private keys may themselves function as authentication material.

In Active Directory Certificate Services environments:

```text
Certificate
     +
Private Key
     |
     v
Authentication
```

Use:

[Active Directory Certificate Services](../active-directory/ad-cs/)


---

# Credential Access and C2

C2 agents can sometimes operate in security contexts where credential material becomes accessible.

The relevant question is not:

```text
Can the framework dump everything?
```

Instead:

```text
What credential material should this security context be able to access?

Can inappropriate credential access occur?

Was it prevented?

Was it detected?
```

Use:

[Command and Control](command-and-control.md)


---

# Detection Opportunities

Credential access can produce telemetry across:

```text
Endpoint
   |
   v
Identity
   |
   v
Application
   |
   v
Network
   |
   v
Cloud
   |
   v
SIEM
```


---

# Windows Detection

Potential signals include:

```text
Sensitive process access
Registry access
Credential-store access
PowerShell activity
File access
Authentication events
Security-control alerts
Unusual process relationships
Access to protected authentication components
```

The available telemetry depends on the endpoint security configuration.


---

# Linux Detection

Potential signals include:

```text
Sensitive file access
Unexpected shell commands
Audit events
Authentication logs
sudo activity
SSH authentication
Process execution
Access to application secrets
```

Linux audit frameworks can provide additional visibility where configured.


---

# Cloud Detection

Cloud platforms can provide telemetry such as:

```text
Authentication
Token issuance
API activity
Secret access
Role assumption
Service principal activity
New device
New location
Permission changes
Key creation
Credential use
```

Cloud audit logging should be centralised and monitored.


---

# Credential Honeytokens

Defenders may deploy synthetic credentials or honeytokens that should never be used legitimately.

Any attempted use can provide a high-value alert.

Conceptually:

```text
Synthetic Secret
      |
      v
Unexpected Use
      |
      v
High-Confidence Alert
```

Honeytokens should be carefully managed so they do not create unintended access.


---

# Detection Validation

For each controlled credential-access action, record:

| Activity | Logged | Alerted | Prevented | Investigated |
|---|---|---|---|---|
| Configuration secret read | Yes | No | No | No |
| Sensitive credential-store access | Yes | Yes | Yes | Yes |
| Test credential authentication | Yes | Yes | No | Yes |

This provides useful defensive measurement.


---

# Evidence Collection

Credential-access evidence should minimise exposure of the secret itself.

Prefer:

```text
Credential type
Identity
Source location
Access permissions
Redacted value
Successful validation result
Privilege demonstrated
Relevant telemetry
```

Instead of:

```text
Full plaintext password copied into every screenshot and report section
```


---

# Redaction

Example:

```text
Username:
CORP\svc-app

Password:
Sup**************

Source:
Application configuration

Validation:
Successful authentication to approved test service
```

Where possible, retain the full secret only in the controlled evidence location if it is genuinely required.


---

# Screenshots

Screenshots can accidentally capture:

```text
Passwords
Tokens
Customer information
Browser sessions
Internal hostnames
Personal information
Unrelated credentials
```

Review and redact screenshots before including them in reports.


---

# Reporting Credential Exposure

A credential finding should explain the root cause.

Weak:

```text
Password found.
```

Better:

```text
A domain service-account credential was stored in a configuration
file readable by standard users.

The credential was minimally validated against the authorised
service and provided access as the service identity.
```


---

# Finding Structure

A credential-access finding can use:

```text
Title
Severity
Affected System
Affected Identity
Credential Type
Source
Required Access
Description
Validation
Impact
Attack Path
Detection
Remediation
Evidence
References
```


---

# Severity

Credential exposure severity depends on:

```text
Credential privilege
Credential scope
Required access
Ease of discovery
Credential lifetime
MFA
Network restrictions
Affected systems
Data access
Attack chaining
Detection
```

A plaintext password is not automatically critical.

A low-privilege test credential limited to one isolated service may have substantially less impact than a broadly privileged service credential.


---

# Candidate vs Confirmed

## Candidate

Potential authentication material is identified.

Examples:

```text
Credential Manager entry
Private-key file
Password-like configuration value
Token-like environment variable
```

Validity has not been established.


## Likely

Context strongly indicates usable authentication material.

Examples:

```text
Credential format valid
Associated account identified
Target service identified
Credential appears current
```


## Confirmed

Minimal authorised testing demonstrates successful authentication or equivalent security impact.


---

# Remediation Model

```text
Credential Exposure
       |
       v
Remove Exposure
       |
       v
Rotate / Revoke Secret
       |
       v
Identify Where Else It Was Used
       |
       v
Reduce Privilege
       |
       v
Improve Secret Storage
       |
       v
Improve Authentication
       |
       v
Improve Monitoring
       |
       v
Validate Again
```


---

# Secret Rotation

When a credential is exposed:

```text
Identify Credential
      |
      v
Identify Dependencies
      |
      v
Create Replacement
      |
      v
Update Applications
      |
      v
Revoke Old Credential
      |
      v
Verify
```

Blindly rotating a service credential without understanding dependencies can cause outages.


---

# Secret Management

Prefer managed secret-storage solutions over plaintext configuration where appropriate.

Potential approaches include:

```text
Cloud secret managers
Enterprise vaults
Managed identities
gMSA
Short-lived tokens
Workload identities
Protected configuration
CI/CD secret stores
```

The correct approach depends on the platform and application architecture.


---

# Least Privilege

Credentials should have only the permissions required.

```text
Application
    |
    v
Service Identity
    |
    +--> Required Database
    |
    X--> Domain Administration
    |
    X--> Unrelated Servers
```

Excessive privilege increases the blast radius of credential exposure.


---

# Short-Lived Credentials

Where possible, prefer:

```text
Short-lived tokens
Temporary cloud sessions
Automatic certificate rotation
Managed service identities
Dynamic secrets
```

over:

```text
Static passwords
Permanent API keys
Long-lived shared secrets
```


---

# Credential Access Checklist

## Context

- [ ] Written authorisation confirmed
- [ ] Current identity established
- [ ] Current privilege established
- [ ] Host role understood
- [ ] Credential testing permitted
- [ ] Scope understood

## Windows

- [ ] Credential Manager considered
- [ ] PowerShell history considered
- [ ] Environment variables considered
- [ ] Application configuration considered
- [ ] Service configuration considered
- [ ] Scheduled tasks considered
- [ ] Unattended files considered where relevant
- [ ] AutoLogon configuration considered
- [ ] Network shares considered
- [ ] Credential protection controls identified

## Linux

- [ ] Shell history considered
- [ ] Environment variables considered
- [ ] SSH configuration considered
- [ ] SSH keys considered
- [ ] Application configuration considered
- [ ] Service configuration considered
- [ ] systemd environment files considered
- [ ] Cron configuration considered
- [ ] Git repositories considered
- [ ] Backup configuration considered

## Applications

- [ ] Database credentials considered
- [ ] API keys considered
- [ ] Tokens considered
- [ ] Configuration secrets considered
- [ ] Deployment scripts considered
- [ ] Secret stores identified

## Cloud

- [ ] Authorised account/tenant identified
- [ ] Cloud configuration considered
- [ ] Access keys handled securely
- [ ] Tokens handled securely
- [ ] Service identities considered
- [ ] CI/CD credentials considered
- [ ] Cross-account boundaries respected

## Validation

- [ ] Credential owner identified
- [ ] Credential type identified
- [ ] Target identified
- [ ] Scope checked
- [ ] Validation explicitly permitted
- [ ] Minimal validation used
- [ ] Privilege documented
- [ ] Unnecessary data access avoided

## Evidence

- [ ] Credential redacted
- [ ] Source documented
- [ ] Required access documented
- [ ] Validation result documented
- [ ] Impact documented
- [ ] Detection result documented
- [ ] Evidence stored securely

## Cleanup

- [ ] Temporary copies removed
- [ ] Test artifacts removed
- [ ] Exposed credentials reported
- [ ] Rotation/revocation recommended
- [ ] Temporary test credentials revoked where required
- [ ] Evidence retention policy followed


---

# Credential Access Decision Model

```text
                    Credential Candidate
                            |
                            v
                       In Scope?
                       /      \
                     No        Yes
                     |          |
                    STOP        v
                         Identify Credential
                                |
                                v
                         Identify Identity
                                |
                                v
                          Identify Target
                                |
                                v
                      Validation Permitted?
                          /          \
                        No            Yes
                        |              |
                        v              v
                    Document       Minimal
                                  Validation
                                      |
                                      v
                                Authentication
                                  Successful?
                                  /        \
                                No          Yes
                                |            |
                                v            v
                            Document     Determine
                                         Privilege
                                            |
                                            v
                                      Objective Proven?
                                       /          \
                                     Yes           No
                                     |              |
                                     v              v
                                    STOP       Continue Only
                                               if Required
```


---

# Credential Attack Path Model

```text
Initial Access
      |
      v
Low-Privilege Context
      |
      v
Credential Discovery
      |
      v
Exposed Secret
      |
      v
Scope Validation
      |
      v
Authentication
      |
      v
New Identity
      |
      +----------------+
      |                |
      v                v
Higher Privilege   New System
      |                |
      +--------+-------+
               |
               v
          Attack Path
               |
               v
            Objective
```


---

# Defensive Credential Model

```text
                         Credentials
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
        Storage           Authentication      Monitoring
            |                 |                 |
            v                 v                 v
      Secret Manager         MFA             Identity Logs
      Managed Identity       PAM             EDR
      Encryption             LAPS            SIEM
      ACLs                   gMSA            Cloud Audit
            |                 |                 |
            +-----------------+-----------------+
                              |
                              v
                      Reduced Blast Radius
```


---

# Final Testing Model

```text
Authorisation
      |
      v
Establish Context
      |
      v
Identify Credential Sources
      |
      v
Find Candidate
      |
      v
Identify Owner and Target
      |
      v
Confirm Scope
      |
      v
Minimal Validation
      |
      v
Determine Privilege
      |
      v
Assess Attack Path
      |
      v
Review Detection
      |
      v
Collect Redacted Evidence
      |
      v
Recommend Rotation / Hardening
      |
      v
Cleanup
```


---

# Related Notes

- [Red Teaming](./)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Active Directory](../active-directory/)
- [Kerberos](../active-directory/kerberos.md)
- [NTLM](../active-directory/ntlm.md)
- [gMSA](../active-directory/gmsa.md)
- [LAPS](../active-directory/laps.md)
- [AD CS](../active-directory/ad-cs/)
- [PrivEsc Explorer](../privesc/)


---

# References

- [MITRE ATT&CK - Credential Access](https://attack.mitre.org/tactics/TA0006/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Credentials from Password Stores](https://attack.mitre.org/techniques/T1555/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - OS Credential Dumping](https://attack.mitre.org/techniques/T1003/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Steal Web Session Cookie](https://attack.mitre.org/techniques/T1539/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Steal Application Access Token](https://attack.mitre.org/techniques/T1528/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows authentication documentation](https://learn.microsoft.com/windows-server/security/windows-authentication/windows-authentication-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Credential Guard](https://learn.microsoft.com/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows LAPS](https://learn.microsoft.com/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH](https://www.openssh.com/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Credential access testing can expose passwords, hashes, authentication tokens, private keys, certificates, cloud credentials, application secrets, and other highly sensitive material. Only access and validate credentials when explicitly permitted by the Rules of Engagement. Confirm the identity, target, tenant, account, and scope before using discovered authentication material. Minimise collection, redact evidence where possible, protect retained secrets, and never use credentials against unrelated or third-party systems.
