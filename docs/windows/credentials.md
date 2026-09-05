# Windows Credentials

Windows systems use multiple credential types and authentication mechanisms.

During an authorised security assessment, credential analysis is not limited to searching for plaintext passwords. Credentials and authentication material may exist in:

- Windows Credential Manager
- Local Security Authority (LSA) secrets
- Security Account Manager (SAM)
- LSASS memory
- DPAPI-protected data
- PowerShell history
- Configuration files
- Scripts
- Environment variables
- Registry values
- Scheduled tasks
- Service configuration
- Network share configuration
- Application databases
- Browser data
- Remote Desktop configuration
- SSH configuration
- Certificates and private keys
- Backup files
- Deployment systems
- Active Directory

The objective is to determine whether sensitive authentication material is exposed beyond its intended security boundary.

---

# 1. Credential Assessment Flow

A practical Windows credential assessment workflow is:

```text
Current User
    |
    v
Security Context
    |
    +---- User
    +---- Groups
    +---- Privileges
    +---- Integrity
    |
    v
Credential Sources
    |
    +---- Credential Manager
    +---- DPAPI
    +---- Files
    +---- Registry
    +---- PowerShell
    +---- Services
    +---- Scheduled Tasks
    +---- Applications
    +---- Certificates
    |
    v
Privileged Sources
    |
    +---- SAM
    +---- SECURITY
    +---- SYSTEM
    +---- LSASS
    +---- LSA Secrets
    |
    v
Validate Access
    |
    v
Determine Credential Type
    |
    v
Determine Privilege / Reuse
    |
    v
Minimise Collection
    |
    v
Evidence
    |
    v
Reporting
```

The key question is not simply:

```text
Can a credential be found?
```

Instead determine:

```text
Who can access it?
What does it authenticate to?
What privilege does it provide?
Why is it exposed?
Can the underlying weakness be remediated?
```

---

# 2. Current Security Context

Before investigating credentials, establish the current user.

```powershell
whoami
```

Full token information:

```powershell
whoami /all
```

Privileges:

```powershell
whoami /priv
```

Groups:

```powershell
whoami /groups
```

PowerShell identity:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

SID:

```powershell
[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
```

Credential exposure should always be interpreted relative to the identity that can access it.

---

# 3. Credential Types

Windows environments can contain several types of authentication material.

Examples include:

```text
Plaintext passwords
NTLM password hashes
Kerberos tickets
Cached credentials
DPAPI-protected secrets
Private keys
Certificates
API tokens
Session tokens
Database credentials
SSH private keys
Application passwords
Service-account credentials
```

These credential types have different security properties.

Do not treat them as interchangeable.

---

# 4. Passwords

Plaintext passwords are particularly sensitive because they may be reusable across multiple authentication mechanisms.

Potential sources include:

```text
Scripts
Configuration files
Command history
Deployment files
Scheduled tasks
Documentation
Environment variables
Application databases
Backup files
```

The presence of the word `password` does not necessarily mean a valid password has been exposed.

Always validate context before reporting.

---

# 5. NTLM Hashes

Windows authentication commonly derives NTLM authentication material from user passwords.

An NTLM hash is not plaintext, but possession of an NTLM hash can be security-sensitive because some Windows authentication scenarios can use the hash without recovering the original password.

See:

- [NTLM](../active-directory/ntlm.md)
- [Pass-the-Hash](../active-directory/pass-the-hash.md)

Hash collection should be limited to what is required for the authorised assessment.

---

# 6. Kerberos Credentials

Domain-joined Windows systems may contain Kerberos authentication material such as:

```text
Ticket Granting Tickets
Service tickets
Session keys
Cached tickets
```

List Kerberos tickets using the built-in utility:

```cmd
klist
```

PowerShell:

```powershell
klist
```

The output can include:

```text
Client
Server
Kerberos encryption type
Ticket flags
Start time
End time
Renew time
```

Detailed Kerberos testing belongs in:

- [Kerberos](../active-directory/kerberos.md)
- [Kerberos Tickets](../active-directory/kerberos-tickets.md)
- [Pass-the-Ticket](../active-directory/pass-the-ticket.md)

---

# 7. Credential Manager

Windows Credential Manager can store credentials for applications and network resources.

Enumerate stored credential entries:

```cmd
cmdkey /list
```

Example output may reference:

```text
Domain credentials
Generic credentials
Remote systems
TERMSRV entries
Microsoft services
Applications
```

`cmdkey /list` normally identifies stored credential targets rather than revealing plaintext passwords.

This distinction is important when reporting.

---

# 8. Credential Manager GUI

Credential Manager can also be opened through:

```cmd
control.exe /name Microsoft.CredentialManager
```

The interface commonly separates:

```text
Web Credentials
Windows Credentials
```

Use the GUI only where appropriate for the assessment and avoid unnecessary interaction with stored secrets.

---

# 9. Credential Manager Assessment

Useful questions include:

```text
Which credentials are stored?
        |
        v
Which user owns them?
        |
        v
What systems are targeted?
        |
        v
Are they still required?
        |
        v
What privilege do they represent?
        |
        v
Could exposure enable lateral movement?
```

The existence of stored credentials is not automatically a vulnerability.

Credential Manager exists specifically to store credentials.

The security issue depends on whether another identity can improperly access or abuse them.

---

# 10. DPAPI

Windows Data Protection API (DPAPI) protects many user and system secrets.

Applications can use DPAPI to protect data using cryptographic keys associated with:

```text
User context
Machine context
```

DPAPI is used by Windows and applications for data such as:

```text
Credential Manager data
Application secrets
Browser-related secrets
Certificates
Private keys
Wireless credentials
Other protected application data
```

DPAPI-protected data should not be described as plaintext merely because the current user can access it through an application.

---

# 11. DPAPI Directories

User DPAPI master keys are commonly associated with locations beneath:

```text
%APPDATA%\Microsoft\Protect
```

Inspect:

```powershell
Get-ChildItem "$env:APPDATA\Microsoft\Protect" -Force -Recurse -ErrorAction SilentlyContinue
```

System-level DPAPI material can exist elsewhere and normally requires elevated access.

The presence of DPAPI files is expected Windows behaviour.

---

# 12. DPAPI Security Model

A simplified model:

```text
Protected Secret
      |
      v
DPAPI
      |
      v
Master Key
      |
      v
User / Machine Protection
      |
      v
Authorised Decryption Context
```

Security analysis should focus on whether an attacker has improperly obtained the prerequisites required to access protected material.

---

# 13. PowerShell History

PowerShell history can expose sensitive commands.

Current session:

```powershell
Get-History
```

PSReadLine history location:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Read:

```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath -ErrorAction SilentlyContinue
```

Common location:

```text
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

---

# 14. Search PowerShell History

A targeted search:

```powershell
$history = (Get-PSReadLineOption).HistorySavePath

Select-String -Path $history -Pattern "password|passwd|pwd|credential|secret|token|apikey|api_key" -ErrorAction SilentlyContinue
```

Review matches manually.

For example:

```text
$password = Read-Host -AsSecureString
```

contains the word `password` but does not expose a credential.

Avoid automatically reporting keyword matches.

---

# 15. PowerShell Transcripts

PowerShell transcription may capture administrative commands and output.

Relevant policy configuration can exist under:

```text
HKLM\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription
```

Inspect:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription" -ErrorAction SilentlyContinue
```

Potential configuration includes:

```text
EnableTranscripting
EnableInvocationHeader
OutputDirectory
```

Transcripts should be protected because they can contain sensitive administrative information.

---

# 16. Environment Variables

Enumerate:

```powershell
Get-ChildItem Env:
```

Search variable names:

```powershell
Get-ChildItem Env: |
    Where-Object {
        $_.Name -match 'PASS|PWD|SECRET|TOKEN|KEY|CRED'
    }
```

Development and automation environments sometimes expose:

```text
API keys
Tokens
Database passwords
Cloud credentials
Build credentials
```

Do not assume a variable is sensitive based only on its name.

---

# 17. Process Environment and Command Lines

Process command lines can sometimes expose secrets supplied as arguments.

Enumerate:

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId, Name, ExecutablePath, CommandLine
```

Targeted search:

```powershell
Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -match 'password|passwd|pwd|secret|token|apikey|api_key'
    } |
    Select-Object ProcessId, Name, CommandLine
```

Command-line secrets are particularly problematic because they may be exposed to:

```text
Process inspection
Logging
Monitoring
Crash data
Administrative tools
```

Visibility depends on permissions and Windows configuration.

---

# 18. Filesystem Search Strategy

Avoid immediately searching the entire filesystem.

Start with high-value application locations:

```text
User profile
Desktop
Documents
Downloads
Application directories
ProgramData
Deployment directories
Web roots
Development repositories
Backup directories
```

A targeted search generates less noise and reduces unnecessary access to unrelated data.

---

# 19. Search File Names

Search for potentially interesting file names:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match 'pass|cred|secret|token|config|connection|backup'
    } |
    Select-Object FullName, Length, LastWriteTime
```

This identifies candidates only.

---

# 20. Search File Content

Targeted content search:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern "password|passwd|secret|token|api[_-]?key" -ErrorAction SilentlyContinue
```

Be careful with large or binary files.

Prefer targeting known text-based formats.

---

# 21. Search Configuration Files

Common configuration extensions include:

```text
.config
.conf
.ini
.xml
.json
.yml
.yaml
.properties
.env
```

Example:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -match '^\.(config|conf|ini|xml|json|yml|yaml|properties|env)$'
    } |
    Select-Object FullName
```

Then inspect only relevant files.

---

# 22. Connection Strings

Applications may store database connection strings.

Potential examples include:

```text
Server
Database
User ID
Password
Integrated Security
Trusted_Connection
```

Search:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern "connectionString|User ID|Password|Integrated Security|Trusted_Connection" -ErrorAction SilentlyContinue
```

Integrated authentication configurations should not be misreported as embedded passwords.

---

# 23. Web Configuration Files

Windows-hosted applications may use files such as:

```text
web.config
appsettings.json
applicationHost.config
```

Find:

```powershell
Get-ChildItem "C:\inetpub" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -in @("web.config","appsettings.json")
    } |
    Select-Object FullName
```

Inspect only applications within scope.

Configuration may contain:

```text
Database strings
API keys
Service credentials
Application secrets
Authentication configuration
```

---

# 24. IIS Configuration

Where IIS is installed, configuration can commonly exist beneath:

```text
C:\Windows\System32\inetsrv\config
```

Examples include:

```text
applicationHost.config
administration.config
redirection.config
```

Access permissions vary.

IIS credential assessment should consider:

```text
Application pool identities
Virtual directory credentials
Configuration encryption
Application secrets
Filesystem permissions
```

---

# 25. Application Pool Identities

Where IIS PowerShell tooling is available:

```powershell
Import-Module WebAdministration -ErrorAction SilentlyContinue
```

Application pools:

```powershell
Get-ChildItem IIS:\AppPools -ErrorAction SilentlyContinue
```

Useful information:

```powershell
Get-ChildItem IIS:\AppPools -ErrorAction SilentlyContinue |
    Select-Object Name,
        @{Name='IdentityType';Expression={$_.processModel.identityType}},
        @{Name='UserName';Expression={$_.processModel.userName}}
```

Do not expect plaintext passwords to be directly displayed.

---

# 26. Service Accounts

Enumerate service identities:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, State, PathName
```

Identify services using non-built-in accounts:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.StartName -and
        $_.StartName -notmatch '^(LocalSystem|NT AUTHORITY\\LocalService|NT AUTHORITY\\NetworkService)$'
    } |
    Select-Object Name, StartName, State, PathName
```

Service-account use is not itself a credential exposure.

Investigate:

```text
How is the password managed?
Is gMSA appropriate?
Are credentials embedded in scripts?
Are credentials duplicated elsewhere?
What privileges does the account have?
```

---

# 27. Service Configuration Files

Once a service path is identified:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, PathName
```

Investigate the associated application directory for:

```text
.config
.ini
.xml
.json
.yml
.yaml
.properties
.env
```

See [Windows Services](services.md).

---

# 28. Scheduled Tasks

Scheduled tasks can run under specific user identities.

Enumerate:

```powershell
Get-ScheduledTask
```

Security-oriented summary:

```powershell
Get-ScheduledTask | ForEach-Object {
    [PSCustomObject]@{
        TaskName = $_.TaskName
        TaskPath = $_.TaskPath
        User = $_.Principal.UserId
        LogonType = $_.Principal.LogonType
        RunLevel = $_.Principal.RunLevel
        Actions = ($_.Actions | ForEach-Object {
            "$($_.Execute) $($_.Arguments)"
        }) -join "; "
    }
}
```

Task definitions may reveal:

```text
Privileged identities
Scripts
Application paths
Command arguments
Network resources
```

---

# 29. Scheduled Task Files

Task definitions are associated with:

```text
C:\Windows\System32\Tasks
```

Access depends on permissions.

Do not modify scheduled task definitions during credential enumeration.

The existence of a privileged task does not mean its credentials are exposed.

---

# 30. Batch and PowerShell Scripts

Search targeted locations:

```powershell
Get-ChildItem "C:\Scripts" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -match '^\.(ps1|bat|cmd|vbs)$'
    } |
    Select-Object FullName
```

Search relevant content:

```powershell
Get-ChildItem "C:\Scripts" -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern "password|passwd|credential|secret|token" -ErrorAction SilentlyContinue
```

Manual review is essential.

---

# 31. PowerShell PSCredential

PowerShell frequently uses `PSCredential` objects.

Example legitimate pattern:

```powershell
$credential = Get-Credential
```

This prompts interactively and does not mean the password is stored in plaintext in the script.

Another pattern may use:

```powershell
ConvertTo-SecureString
```

The security properties depend on how the secret was originally stored and protected.

Do not report `SecureString` usage as insecure without analysing the complete implementation.

---

# 32. Hard-Coded Credentials

A stronger finding is:

```powershell
$username = "CORP\ServiceAccount"
$password = "ExamplePassword"
```

Security significance increases when:

```text
File is readable by unprivileged users
        +
Credential is valid
        +
Account has meaningful privileges
```

The root issue is secret storage and access control.

---

# 33. Backup Files

Credentials can remain in old versions of configuration files.

Common patterns include:

```text
*.bak
*.backup
*.old
*.orig
*.save
*.tmp
```

Search targeted application directories:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -match '^\.(bak|backup|old|orig|save|tmp)$'
    } |
    Select-Object FullName, LastWriteTime
```

Backup files can bypass protections applied to the current configuration file.

---

# 34. Unattended Installation Files

Deployment artifacts can sometimes contain configuration or historical credentials.

Potential locations and file names vary by deployment method.

Search targeted deployment directories for:

```text
unattend.xml
unattended.xml
sysprep.inf
sysprep.xml
```

Example:

```powershell
Get-ChildItem C:\ -Filter "unattend.xml" -Recurse -ErrorAction SilentlyContinue
```

Full-drive recursive searches can be expensive.

Prefer known deployment locations first.

---

# 35. Group Policy Artifacts

Domain-joined systems may contain cached or downloaded Group Policy-related files.

Relevant locations can include:

```text
C:\Windows\SYSVOL
C:\ProgramData
```

and domain SYSVOL shares.

Group Policy credential issues should be analysed in the Active Directory context rather than assumed from local file presence.

See [Group Policy](../active-directory/group-policy.md).

---

# 36. Registry Search

Applications sometimes store credentials or secrets in registry values.

Target known application keys first.

Example:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Vendor\Application" -ErrorAction SilentlyContinue
```

Search value names in a targeted branch:

```powershell
Get-ChildItem "HKCU:\Software\Vendor" -Recurse -ErrorAction SilentlyContinue |
    ForEach-Object {
        try {
            $item = Get-ItemProperty $_.PSPath -ErrorAction Stop

            $item.PSObject.Properties |
                Where-Object {
                    $_.Name -match 'password|passwd|secret|token|key|credential'
                } |
                ForEach-Object {
                    [PSCustomObject]@{
                        Path = $_.MemberType
                        Name = $_.Name
                        Value = $_.Value
                    }
                }
        }
        catch {}
    }
```

Large registry-wide searches are noisy and usually unnecessary.

---

# 37. AutoLogon

Windows can be configured for automatic logon.

Relevant registry location:

```text
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
```

Inspect selected values:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" |
    Select-Object AutoAdminLogon, DefaultUserName, DefaultDomainName, DefaultPassword
```

If a plaintext `DefaultPassword` is accessible to an inappropriate user, this can represent significant credential exposure.

Do not modify these values during assessment.

---

# 38. Remote Desktop

Stored Remote Desktop targets may appear through Credential Manager.

```cmd
cmdkey /list
```

Look for entries referencing:

```text
TERMSRV/
```

This identifies stored RDP-related credentials or targets.

It does not necessarily reveal the plaintext password.

RDP configuration should also be evaluated from an access-control perspective.

---

# 39. RDP Files

Search targeted user directories:

```powershell
Get-ChildItem "$env:USERPROFILE" -Filter "*.rdp" -Recurse -ErrorAction SilentlyContinue
```

RDP files may contain:

```text
Target hostname
Username
Display settings
Gateway configuration
Other connection properties
```

A username or target is not equivalent to an exposed password.

---

# 40. SSH Configuration

Windows can use OpenSSH.

User SSH directory:

```powershell
Get-ChildItem "$env:USERPROFILE\.ssh" -Force -ErrorAction SilentlyContinue
```

Potential files include:

```text
config
known_hosts
authorized_keys
id_rsa
id_ed25519
Other private keys
```

Private keys are sensitive authentication material.

---

# 41. SSH Private Key Permissions

Inspect:

```powershell
Get-Acl "$env:USERPROFILE\.ssh" -ErrorAction SilentlyContinue
```

Specific key:

```powershell
Get-Acl "$env:USERPROFILE\.ssh\id_ed25519" -ErrorAction SilentlyContinue |
    Format-List Owner, AccessToString
```

A private key should not be readable by unrelated users.

The actual impact depends on:

```text
Key validity
Target systems
Passphrase protection
Account privileges
Network reachability
```

---

# 42. Certificates

Enumerate current-user certificates:

```powershell
Get-ChildItem Cert:\CurrentUser\My
```

Local-machine certificates:

```powershell
Get-ChildItem Cert:\LocalMachine\My
```

Focused:

```powershell
Get-ChildItem Cert:\CurrentUser\My |
    Select-Object Subject, Issuer, Thumbprint, NotAfter, HasPrivateKey
```

Machine certificate access may depend on permissions.

---

# 43. Certificates with Private Keys

Current user:

```powershell
Get-ChildItem Cert:\CurrentUser\My |
    Where-Object HasPrivateKey |
    Select-Object Subject, Thumbprint, NotAfter
```

Local machine:

```powershell
Get-ChildItem Cert:\LocalMachine\My -ErrorAction SilentlyContinue |
    Where-Object HasPrivateKey |
    Select-Object Subject, Thumbprint, NotAfter
```

A certificate having a private key is expected in many legitimate scenarios.

The security question is whether an unauthorised identity can use or export that key.

---

# 44. Certificate Private-Key Permissions

Private-key security depends on the key storage provider and ACLs.

Do not assume:

```text
HasPrivateKey = True
```

means:

```text
Private key is exportable by everyone
```

Determine:

```text
Who owns the certificate?
Who can use the key?
Is the key exportable?
What authentication does it enable?
What certificate purpose is configured?
```

For Active Directory Certificate Services, see [AD CS](../active-directory/ad-cs/index.md).

---

# 45. PFX and Certificate Files

Search targeted locations:

```powershell
Get-ChildItem "C:\Application" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -match '^\.(pfx|p12|pem|key|crt|cer)$'
    } |
    Select-Object FullName, Length, LastWriteTime
```

Files such as:

```text
.pfx
.p12
.pem
.key
```

may contain private key material.

Do not export or copy private keys unless required and authorised.

---

# 46. Cloud and Developer Credentials

Developer workstations may contain credentials associated with:

```text
Cloud platforms
Source-control platforms
Package repositories
Container registries
CI/CD systems
Infrastructure automation
```

Search should be targeted to technologies actually present on the host.

Do not indiscriminately collect unrelated personal or organisational tokens.

---

# 47. Git Repositories

Locate repositories in expected development locations:

```powershell
Get-ChildItem "$env:USERPROFILE\source" -Directory -Recurse -Filter ".git" -ErrorAction SilentlyContinue
```

Repositories can contain:

```text
Configuration
Historical secrets
Deployment scripts
Environment files
API endpoints
Credentials accidentally committed in the past
```

Credential review should remain within authorised source-code scope.

---

# 48. Environment Files

Search targeted application repositories:

```powershell
Get-ChildItem "C:\Development" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -eq ".env" -or
        $_.Name -like ".env.*"
    } |
    Select-Object FullName
```

Potential contents include:

```text
Database credentials
API tokens
Cloud credentials
Application secrets
```

`.env` files are not inherently vulnerable.

Permissions and secret-management practices determine the risk.

---

# 49. Database Clients and Applications

Installed database software may reference credentials through:

```text
Configuration files
Connection strings
ODBC settings
Environment variables
Application secrets
```

Enumerate ODBC data sources where available:

```powershell
Get-OdbcDsn -ErrorAction SilentlyContinue
```

Do not assume an ODBC DSN contains a stored password.

---

# 50. Network Shares

Enumerate mapped filesystem drives:

```powershell
Get-PSDrive -PSProvider FileSystem
```

Legacy view:

```cmd
net use
```

Shares may expose:

```text
Deployment scripts
Configuration files
Backups
Administrative tools
Documentation
```

Only inspect shares included in the assessment scope.

See [SMB](../active-directory/smb.md) and [Shares](../active-directory/shares.md).

---

# 51. Saved Network Credentials

Credential Manager may contain credentials associated with network resources.

```cmd
cmdkey /list
```

Network sessions:

```cmd
net use
```

These provide different information.

Conceptually:

```text
cmdkey
    |
    +---- Stored credential targets

net use
    |
    +---- Current network connections
```

Do not assume one implies the other.

---

# 52. SAM

The Security Account Manager contains local account authentication data.

The backing registry hive is associated with:

```text
HKLM\SAM
```

and the corresponding protected system file.

Normal standard users should not have direct access to sensitive SAM credential material.

During assessment, a key question is:

```text
Can an unprivileged user improperly access
SAM-derived credential material?
```

If yes, investigate the underlying permission or backup exposure.

---

# 53. SYSTEM Hive

The SYSTEM hive contains system configuration and cryptographic material required by Windows.

It is associated with:

```text
HKLM\SYSTEM
```

The SYSTEM hive is often security-sensitive when considered together with other protected Windows credential stores.

Access to the live protected hive is normally restricted.

---

# 54. SECURITY Hive

The SECURITY hive is associated with:

```text
HKLM\SECURITY
```

It can contain security-sensitive information managed by the Local Security Authority.

Normal users should not have unrestricted access to protected secrets stored there.

---

# 55. Registry Hive Security Model

A simplified relationship is:

```text
SAM
    |
    +---- Local account authentication data

SYSTEM
    |
    +---- System cryptographic/configuration material

SECURITY
    |
    +---- LSA-managed security data
```

Security assessment should focus on unauthorised access to these protected stores rather than their normal existence.

---

# 56. Backup Copies of Registry Hives

Historical or backup copies can sometimes be more exposed than live protected resources.

Potential sources include:

```text
System backups
Administrative exports
Old deployment files
Support bundles
Disk images
Snapshot data
```

A sensitive hive copied into a broadly readable directory may create credential exposure even though the live hive is correctly protected.

---

# 57. Search for Registry Hive Copies

Target likely backup locations rather than searching every file on the system.

Example:

```powershell
Get-ChildItem "C:\Backups" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match '^(SAM|SYSTEM|SECURITY)$'
    } |
    Select-Object FullName, Length, LastWriteTime
```

Validate whether the files are genuine registry hives before reporting.

---

# 58. LSA Secrets

The Local Security Authority manages security-sensitive system information.

LSA secrets can be associated with items such as:

```text
Service-account information
System secrets
Cached security data
Application-managed secrets
```

Access normally requires elevated privileges.

The existence of LSA secrets is normal Windows behaviour.

The security issue is inappropriate access to them.

---

# 59. LSASS

The Local Security Authority Subsystem Service (`lsass.exe`) is a critical Windows security process.

Inspect process presence:

```powershell
Get-Process lsass
```

CIM:

```powershell
Get-CimInstance Win32_Process -Filter "Name='lsass.exe'"
```

LSASS participates in Windows authentication and may hold authentication-related material required for active logon sessions.

Access to LSASS should be tightly controlled.

---

# 60. LSASS Protection

Modern Windows security features can reduce credential exposure from LSASS.

Important protections include:

```text
Credential Guard
LSA protection
Protected Process Light
Endpoint protection
Application control
Least privilege
```

Assessment should focus on whether expected protections are configured and effective.

---

# 61. LSA Protection

LSA protection can configure LSASS to run as a protected process.

A commonly relevant configuration value is associated with:

```text
HKLM\SYSTEM\CurrentControlSet\Control\Lsa
```

Inspect:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -ErrorAction SilentlyContinue |
    Select-Object RunAsPPL, RunAsPPLBoot
```

Interpret values using the applicable Windows version and Microsoft documentation.

Do not conclude protection is ineffective based only on one registry value.

---

# 62. Credential Guard

Credential Guard uses virtualization-based security to isolate selected secrets from the normal operating system environment.

Relevant Windows security information may be available through supported Device Guard and system-management interfaces depending on Windows version.

Useful contextual checks include:

```powershell
Get-ComputerInfo |
    Select-Object DeviceGuard*
```

Not every Windows version exposes identical properties.

Use multiple sources when validating Credential Guard.

---

# 63. Credential Guard Assessment

Conceptually:

```text
Credential Guard
      |
      v
Virtualization-Based Security
      |
      v
Isolated Security Environment
      |
      v
Reduced Exposure of Selected Secrets
```

Credential Guard does not mean:

```text
No credentials can ever be compromised
```

It reduces exposure for specific credential material and attack paths.

---

# 64. Cached Domain Credentials

Domain-joined systems can support cached interactive logons.

This allows users to authenticate when a domain controller is unavailable.

Cached domain logon information is protected and is not equivalent to a plaintext password.

Its presence can be legitimate and operationally necessary.

Assess:

```text
Business requirement
Number of cached logons
Endpoint risk
Administrative account usage
Device protection
```

---

# 65. Local Administrator Passwords

Shared local administrator passwords create significant lateral-movement risk.

A stronger architecture uses unique, automatically managed local administrator passwords.

In Active Directory environments, Windows LAPS can provide this capability.

See [LAPS](../active-directory/laps.md).

The relevant security relationship is:

```text
Same Local Admin Password
        |
        v
Many Computers
        |
        v
One Host Compromised
        |
        v
Credential Reuse
        |
        v
Lateral Movement
```

---

# 66. Service-Account Passwords

Traditional domain service accounts often use manually managed passwords.

Potential risks include:

```text
Long password lifetime
Password reuse
Excessive privileges
Interactive logon
Hard-coded credentials
Documentation exposure
Configuration-file exposure
```

Where appropriate, consider gMSA.

See [gMSA](../active-directory/gmsa.md).

---

# 67. Secrets in Scripts

A common anti-pattern is:

```text
Automation requires authentication
        |
        v
Password embedded in script
        |
        v
Script readable by users
        |
        v
Credential exposure
```

Better approaches depend on the application and can include:

```text
Managed identities
gMSA
Credential vaults
Protected application secrets
Certificate-based authentication
Short-lived tokens
```

---

# 68. Secrets in Command-Line Arguments

Avoid passing passwords directly as command-line arguments where safer mechanisms exist.

Conceptually:

```text
Application.exe --username user --password ExamplePassword
```

may expose the secret through process inspection or telemetry.

Prefer application-supported secure credential handling.

---

# 69. Secrets in Logs

Applications may accidentally log:

```text
Passwords
Tokens
Authorization headers
Connection strings
API keys
Session identifiers
```

Search targeted log directories:

```powershell
Get-ChildItem "C:\Application\Logs" -Recurse -File -ErrorAction SilentlyContinue |
    Select-String -Pattern "password|passwd|secret|token|authorization|api[_-]?key" -ErrorAction SilentlyContinue
```

Avoid copying complete logs when a small redacted excerpt is sufficient evidence.

---

# 70. Secrets in Crash Dumps

Memory dumps can contain sensitive process data.

Potential dump locations depend on application and Windows configuration.

Dump files should therefore be treated as sensitive.

Do not generate memory dumps of security-sensitive processes solely for credential collection unless explicitly authorised.

---

# 71. Browser Data

Browsers can store authentication-related information including:

```text
Cookies
Saved logins
Tokens
Session state
Certificates
```

Modern browsers typically protect saved secrets using operating-system and application security mechanisms.

Browser credential extraction can expose extensive personal and organisational information.

Only assess browser data when explicitly within scope and necessary.

---

# 72. Password Managers

Enterprise and personal password managers may be installed on Windows endpoints.

Their presence is not a vulnerability.

Assessment should focus on:

```text
Vault configuration
Authentication controls
Session locking
Endpoint compromise assumptions
Export permissions
Organisational policy
```

Do not attempt broad password-vault extraction without explicit authorisation.

---

# 73. Sensitive File Permissions

When a potential secret is identified:

```powershell
Get-Acl "C:\Application\config.ini" |
    Format-List Owner, AccessToString
```

Detailed:

```powershell
(Get-Acl "C:\Application\config.ini").Access |
    Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited
```

The strongest finding often combines:

```text
Sensitive Secret
      +
Broad Read Access
      +
Privileged Credential
```

---

# 74. Determine Who Can Read a Secret

Do not report only:

```text
Password stored in file
```

Determine:

```text
Which account owns the file?
Which groups can read it?
Is the file required?
Is the secret encrypted?
Which account does the secret belong to?
What privileges does that account have?
```

A credential stored in a tightly protected system secret store is different from one stored in a world-readable configuration file.

---

# 75. Credential Validation

Avoid unnecessary authentication attempts.

A credential can often be validated through context such as:

```text
Configuration references
Service account identity
Application configuration
Timestamp
Known target
Controlled authentication where authorised
```

If authentication is required to establish impact:

```text
Use the minimum number of attempts
Avoid account lockout
Avoid production disruption
Use only in-scope targets
Record the exact validation performed
```

---

# 76. Password Spraying

Password spraying involves attempting a small number of passwords against multiple accounts.

This is fundamentally different from local credential discovery.

It can trigger:

```text
Account lockouts
Detection alerts
Conditional access
Incident response
```

Only perform spraying when specifically authorised.

See [Password Spraying](../active-directory/password-spraying.md).

---

# 77. Credential Reuse

A credential becomes more significant when reused.

Possible reuse patterns include:

```text
Local administrator across hosts
Service account across servers
Database account across environments
Developer credential across services
Production password reused in test
```

Credential reuse expands the blast radius of a single exposure.

---

# 78. Credential Privilege

Determine what the credential provides access to.

Examples:

```text
Local standard user
Local administrator
Domain user
Server administrator
Service account
Database administrator
Application administrator
Domain administrator
Cloud administrator
```

Severity should be based on demonstrated or strongly evidenced privilege rather than merely the presence of a password.

---

# 79. Credential Scope

Determine whether the credential is:

```text
Local
Domain
Application-specific
Database-specific
Cloud
Certificate-based
API-specific
```

This affects both impact and remediation.

For example:

```text
Local credential
```

may affect one endpoint, while:

```text
Domain credential
```

may provide access across multiple systems.

---

# 80. Credential Lifetime

Consider:

```text
Password expiration
Token expiration
Certificate validity
Kerberos ticket lifetime
Key rotation
Service-account password rotation
```

A short-lived token may present a different risk from a long-lived reusable password.

---

# 81. Credential Exposure Matrix

| Exposure | Potential Significance |
|---|---|
| Username only | Usually informational |
| Stored Credential Manager target | Context dependent |
| Plaintext standard-user password | Significant |
| Plaintext local administrator password | High |
| Reused local administrator password | High |
| Privileged domain password | High / critical |
| API token | Depends on permissions |
| Private SSH key | Depends on targets and protection |
| Certificate private key | Depends on certificate purpose |
| Kerberos ticket | Depends on identity and validity |
| NTLM hash | Significant depending on account |
| DPAPI file without decryption context | Not equivalent to plaintext |
| Password keyword in config | Candidate only |

Use the organisation's agreed severity model for the final rating.

---

# 82. Credential Exposure Decision Tree

```text
Potential Secret
      |
      v
Actually Sensitive?
      |
      +---- No ----> Ignore / document if relevant
      |
      +---- Yes
             |
             v
      Who Can Access It?
             |
             v
      Which Identity?
             |
             v
      Which System / Service?
             |
             v
      What Privilege?
             |
             v
      Still Valid?
             |
             v
      Reused?
             |
             v
      Practical Impact
             |
             v
           Finding
```

---

# 83. Safe Credential Assessment

Prefer:

```text
Metadata
    +
Permissions
    +
Configuration
    +
Minimal validation
    =
Evidence
```

Avoid unnecessary:

```text
Mass credential dumping
Bulk password collection
Password cracking without need
Copying unrelated secrets
Exporting browser vaults
Collecting personal credentials
Repeated authentication attempts
```

Collect only what is necessary to demonstrate the weakness.

---

# 84. Evidence Handling

Credentials are highly sensitive evidence.

Avoid putting complete secrets into:

```text
Screenshots
Issue trackers
Chat systems
Email
Report body
File names
Terminal recordings
```

Prefer redaction.

Example:

```text
Username:
CORP\svc_backup

Password:
S***********7
```

Where possible, avoid recording even a partially recognisable secret if it is unnecessary.

---

# 85. Hashing Evidence Files

If a sensitive evidence file must be collected under the engagement rules, record an integrity hash.

```powershell
Get-FileHash "C:\Evidence\artifact.bin" -Algorithm SHA256
```

Record:

```text
File name
Source host
Collection time
SHA-256
Storage location
Collector
```

Follow the engagement's evidence-handling requirements.

---

# 86. Temporary Files

Avoid leaving credential material in:

```text
C:\Temp
%TEMP%
Desktop
Downloads
World-readable shares
```

If temporary evidence is required:

```text
Use an approved location
Restrict permissions
Encrypt where required
Remove when no longer needed
Document handling
```

---

# 87. Credential Reporting

A credential finding should explain:

```text
Where was the credential exposed?
Who could access it?
Which account did it belong to?
What privileges did it provide?
Was reuse demonstrated?
How was validity established?
What is the root cause?
```

Do not make the report primarily about the credential value itself.

The credential value should normally be redacted.

---

# 88. Reporting Example - Plaintext Service Credential

## Title

```text
Plaintext Service Account Credentials Accessible to Standard Users
```

## Description

```text
A configuration file accessible to standard users contains credentials for
a service account in plaintext.

The affected file permissions allow users who do not require access to the
service credential to read the authentication material.
```

## Evidence

```text
File:
C:\ProgramData\Vendor\Application\service.config

Affected account:
CORP\svc_application

File access:
BUILTIN\Users - Read

Credential:
[REDACTED]
```

## Impact

```text
An unprivileged user with access to the affected endpoint may obtain the
service-account credential and potentially access resources available to
that account.

The final impact depends on the privileges, network access, and reuse of the
affected credential.
```

## Recommendation

```text
Remove plaintext credentials from application configuration where possible.

Use an appropriate managed secret-storage mechanism and restrict access to
the minimum identities required by the application.

Rotate the exposed credential and review whether it has been reused on
other systems or services.
```

---

# 89. Reporting Example - PowerShell History

## Title

```text
Sensitive Credential Material Stored in PowerShell Command History
```

## Description

```text
PowerShell command history accessible to the assessed user contains
authentication material that was previously supplied directly on the
command line.
```

## Evidence

```text
History file:
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt

Affected secret:
[REDACTED]

Associated account:
CORP\example
```

## Recommendation

```text
Avoid supplying passwords and long-lived secrets directly in command-line
arguments or commands that are persisted to history.

Use secure credential prompts, managed identities, protected secret stores,
or other application-supported authentication mechanisms.

Rotate exposed credentials where required.
```

---

# 90. Reporting Example - AutoLogon Credential

## Title

```text
Windows AutoLogon Configuration Exposes Reusable Credentials
```

## Description

```text
The assessed system contains AutoLogon configuration that exposes reusable
authentication material to an inappropriate security context.
```

## Evidence

```text
Registry path:
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon

Configured user:
CORP\example

Credential:
[REDACTED]
```

## Recommendation

```text
Disable plaintext AutoLogon credential storage where it is not operationally
required.

Where automatic sign-in is unavoidable, review supported alternatives,
restrict access to the endpoint, minimise account privileges, and protect
the associated credential.

Rotate the exposed credential after remediation.
```

---

# 91. Reporting Example - Exposed Private Key

## Title

```text
Private Authentication Key Accessible to Unauthorised Users
```

## Description

```text
A private authentication key is stored in a location accessible to users
who do not require access to the key.

The key may allow authentication to systems that trust the corresponding
public key.
```

## Evidence

```text
File:
C:\Users\example\.ssh\id_ed25519

Affected identity:
example

Permissions:
[document relevant ACL]

Private key:
Not reproduced in report
```

## Recommendation

```text
Restrict private-key access to the intended user and trusted administrative
identities.

Revoke or rotate the affected key where unauthorised access may have
occurred and review systems that trust the corresponding public key.
```

---

# 92. Reporting Example - Backup Credential Exposure

## Title

```text
Sensitive Credentials Remain Accessible in Application Backup Files
```

## Description

```text
Historical application configuration files contain credentials that remain
accessible after the active configuration was secured.

The backup files are readable by users who do not require access to the
stored authentication material.
```

## Recommendation

```text
Remove obsolete backup files containing sensitive authentication material.

Apply appropriate permissions to backup locations and ensure secret
rotation processes include credentials exposed through historical copies.
```

---

# 93. Remediation - Secret Storage

Prefer security mechanisms appropriate to the application, such as:

```text
Windows Credential Manager
DPAPI
Enterprise secret vaults
Managed identities
gMSA
Certificate-based authentication
Short-lived tokens
Platform-native secret stores
```

The correct mechanism depends on the application architecture.

Avoid inventing custom encryption schemes for credential storage.

---

# 94. Remediation - Least Privilege

Credential exposure impact is reduced when the affected identity has only the privileges it requires.

Review:

```text
Local administrator membership
Domain groups
Application roles
Database permissions
Share permissions
Logon rights
Service privileges
Cloud roles
```

Credential protection and least privilege should be applied together.

---

# 95. Remediation - Credential Rotation

Rotate credentials when:

```text
Plaintext exposure occurred
Unauthorised access was possible
Credential was committed to source control
Credential was placed in logs
Credential appeared in backups
Private key exposure occurred
Credential reuse expanded the blast radius
```

Rotation should include dependent applications to avoid outages.

---

# 96. Remediation - Unique Local Administrator Passwords

Avoid using one static local administrator password across many endpoints.

Where appropriate, use Windows LAPS to provide:

```text
Unique passwords
Automatic rotation
Controlled retrieval
Central management
```

See [LAPS](../active-directory/laps.md).

---

# 97. Remediation - Service Accounts

Where appropriate:

```text
Use gMSA
Use long automatically managed passwords
Remove interactive logon
Apply least privilege
Limit logon locations
Remove obsolete accounts
Monitor account usage
```

See [gMSA](../active-directory/gmsa.md).

---

# 98. Remediation - Scripts

Avoid:

```text
$username = "admin"
$password = "Password123"
```

Prefer mechanisms where the script does not contain a reusable plaintext secret.

Protect:

```text
Scripts
Configuration
Credential files
Automation directories
Deployment repositories
```

---

# 99. Remediation - Logging

Prevent applications from logging sensitive values.

Redact:

```text
Passwords
Tokens
Authorization headers
Cookies
Private keys
Connection strings containing secrets
```

Ensure logging frameworks and debugging modes do not unintentionally expose authentication material.

---

# 100. Remediation - Command Lines

Where supported, avoid supplying secrets directly in command-line arguments.

Prefer:

```text
Secure interactive prompts
Protected configuration
Secret-store integration
Managed identity
Short-lived authentication
Standard input where application design supports it securely
```

The appropriate method depends on the application.

---

# 101. Defensive Monitoring

Credential-access monitoring can combine:

```text
Authentication Events
       |
       +
Process Telemetry
       |
       +
File Access
       |
       +
Registry Access
       |
       +
PowerShell Logging
       |
       +
Endpoint Security
       |
       +
Identity Monitoring
       |
       v
Central Detection
```

Monitor behaviour rather than relying only on known tool names.

---

# 102. Credential Access Detection

Potential suspicious behaviour includes:

```text
Unexpected access to credential stores
Unusual access to LSASS
Sensitive registry hive access
Credential-related process behaviour
Unexpected certificate export
Access to private keys
Large-scale secret searches
Unexpected Credential Manager interaction
```

Detection should account for legitimate administrative and security software.

---

# 103. PowerShell Detection

Credential discovery performed through PowerShell may generate telemetry through:

```text
PowerShell Operational logs
Script Block Logging
Module Logging
Process telemetry
AMSI / endpoint telemetry
File access telemetry
```

See [PowerShell](powershell.md).

---

# 104. Credential Guard and LSA Protection

Where supported and appropriate, consider:

```text
Credential Guard
LSA protection
Virtualization-Based Security
Application control
Endpoint security
Least privilege
```

These controls reduce particular credential-access attack paths but should be treated as layers rather than complete solutions.

---

# 105. Administrator Logon Hygiene

Highly privileged accounts should not routinely authenticate to lower-trust endpoints.

Conceptually:

```text
Domain Admin
     |
     v
Logs onto Workstation
     |
     v
Privileged Authentication Material
     |
     v
Potential Exposure on Workstation
```

Administrative tiering and privileged access workstations can reduce this risk.

---

# 106. Credential Exposure Checklist

## Context

- [ ] Identify current user
- [ ] Record groups
- [ ] Record privileges
- [ ] Determine host role
- [ ] Determine domain membership

## User Credential Sources

- [ ] Credential Manager
- [ ] PowerShell history
- [ ] PowerShell transcripts
- [ ] Environment variables
- [ ] User configuration files
- [ ] RDP files
- [ ] SSH keys
- [ ] Certificates
- [ ] Developer configuration

## Application Sources

- [ ] Application configuration
- [ ] Web configuration
- [ ] Database connection strings
- [ ] Environment files
- [ ] Backup files
- [ ] Logs
- [ ] Scripts
- [ ] Source repositories

## System Sources

- [ ] Services
- [ ] Scheduled tasks
- [ ] AutoLogon configuration
- [ ] SAM exposure
- [ ] SECURITY exposure
- [ ] SYSTEM exposure
- [ ] LSA protection
- [ ] Credential Guard
- [ ] Sensitive backup copies

## Validation

- [ ] Determine credential type
- [ ] Determine account
- [ ] Determine target
- [ ] Determine privilege
- [ ] Determine validity only if necessary
- [ ] Check reuse only where authorised
- [ ] Avoid unnecessary authentication attempts

## Evidence

- [ ] Redact secrets
- [ ] Record file permissions
- [ ] Record affected identity
- [ ] Record access path
- [ ] Record practical impact
- [ ] Minimise collection
- [ ] Protect evidence
- [ ] Remove temporary copies

---

# 107. Quick Credential Enumeration

Identity:

```powershell
whoami /all
```

Stored credential targets:

```cmd
cmdkey /list
```

Kerberos tickets:

```cmd
klist
```

PowerShell history:

```powershell
Get-History
```

PSReadLine history path:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

Environment variables:

```powershell
Get-ChildItem Env:
```

Service accounts:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, State, PathName
```

Scheduled task identities:

```powershell
Get-ScheduledTask |
    Select-Object TaskName,
        @{Name='User';Expression={$_.Principal.UserId}},
        @{Name='LogonType';Expression={$_.Principal.LogonType}}
```

Certificates:

```powershell
Get-ChildItem Cert:\CurrentUser\My |
    Select-Object Subject, Thumbprint, NotAfter, HasPrivateKey
```

AutoLogon configuration:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" |
    Select-Object AutoAdminLogon, DefaultUserName, DefaultDomainName, DefaultPassword
```

LSA protection context:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Lsa" -ErrorAction SilentlyContinue |
    Select-Object RunAsPPL, RunAsPPLBoot
```

---

# 108. High-Value Targeted Search

Instead of:

```text
Search every file on C:\
```

prefer:

```text
Identify Applications
        |
        v
Identify Config Directories
        |
        v
Identify Scripts
        |
        v
Identify Backup Locations
        |
        v
Search Relevant Files
        |
        v
Inspect Permissions
        |
        v
Validate Secret
```

This approach is faster, quieter, and less likely to collect unrelated sensitive information.

---

# 109. Credential Assessment Decision Tree

```text
Start
  |
  v
Current User / Token
  |
  v
Credential Manager
  |
  v
PowerShell / Environment
  |
  v
Application Configuration
  |
  v
Services / Scheduled Tasks
  |
  v
Certificates / SSH
  |
  v
Backups / Logs
  |
  v
Privileged Stores
  |
  v
Potential Credential Found?
  |
  +---- No ----> Continue targeted enumeration
  |
  +---- Yes
          |
          v
    Actually Sensitive?
          |
          +---- No ----> Document if relevant
          |
          +---- Yes
                  |
                  v
            Who Can Read It?
                  |
                  v
            Which Identity?
                  |
                  v
             What Privilege?
                  |
                  v
             Still Valid?
                  |
                  v
              Reusable?
                  |
                  v
            Minimal Validation
                  |
                  v
            Redacted Evidence
                  |
                  v
                Report
```

---

# 110. Credential Exposure vs Credential Access

Keep these concepts separate.

## Credential Exposure

A weakness causes authentication material to be accessible where it should not be.

Example:

```text
Plaintext password
      |
      v
World-readable configuration file
```

## Credential Access

An actor obtains authentication material from a system.

Example categories can include:

```text
Credentials from files
Credentials from password stores
Credentials from operating-system stores
Credentials from application data
```

A penetration test should ideally identify the root exposure rather than merely demonstrate that credential-access tooling works.

---

# 111. Local-to-Domain Escalation

Credential exposure on one Windows endpoint can become an Active Directory issue.

```text
Standard User
      |
      v
Local Credential Exposure
      |
      v
Privileged Credential
      |
      v
Remote Access
      |
      v
Additional Host
      |
      v
Domain Credential Exposure
      |
      v
Active Directory Impact
```

This is why credential reuse and administrative logon hygiene matter.

---

# 112. Credential Attack Path Model

A useful attack-path model is:

```text
Credential Source
      |
      v
Access Permission
      |
      v
Credential Type
      |
      v
Credential Identity
      |
      v
Credential Privilege
      |
      v
Reachable Resource
      |
      v
Reuse / Delegation
      |
      v
Security Impact
```

Each stage should be supported by evidence.

---

# 113. What Not to Report Automatically

Avoid automatically reporting:

```text
cmdkey contains entries
Kerberos tickets exist
DPAPI files exist
LSASS is running
Credential Manager is enabled
Certificates have private keys
PowerShell history exists
Service accounts exist
Cached domain logons are enabled
SSH configuration exists
```

These are normal capabilities or artefacts in many Windows environments.

Investigate whether they create unauthorised exposure.

---

# 114. Strong Credential Finding Model

Prefer:

```text
Sensitive Credential
       |
       v
Accessible to Unprivileged User
       |
       v
Credential Belongs to Privileged Identity
       |
       v
Credential Is Valid / Relevant
       |
       v
Unauthorised Access Possible
       |
       v
Security Impact
```

rather than:

```text
Credential-related file exists
       |
       v
Vulnerability
```

---

# 115. Purple Team Validation

Credential-access exercises can be useful for testing defensive visibility.

A controlled model:

```text
Authorised Credential Test
        |
        v
Host Activity
        |
        +---- Process
        +---- PowerShell
        +---- File
        +---- Registry
        +---- Authentication
        |
        v
EDR / SIEM
        |
        v
Detection
        |
        v
Analyst Investigation
        |
        v
Feedback
```

Record:

```text
Technique
Credential source
Expected telemetry
Observed telemetry
Detection
Alert quality
Analyst response
Visibility gaps
Improvement
```

Use test accounts and synthetic secrets where possible.

---

# 116. Final Testing Model

Use the following model for Windows credential assessments:

```text
Identify Credential Source
        |
        v
Determine Current Access
        |
        v
Determine Protection Mechanism
        |
        v
Determine Credential Type
        |
        v
Determine Affected Identity
        |
        v
Determine Privilege
        |
        v
Determine Reuse / Scope
        |
        v
Perform Minimum Validation
        |
        v
Protect and Redact Evidence
        |
        v
Identify Root Cause
        |
        v
Recommend Remediation
```

The objective is not to collect as many credentials as possible.

The objective is to identify credential trust failures and demonstrate their security impact with the minimum necessary handling of sensitive authentication material.

---

# Related Notes

- [Windows](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [PowerShell](powershell.md)
- [Windows Services](services.md)
- [Active Directory](../active-directory/index.md)
- [Credential Access](../active-directory/credential-access.md)
- [NTLM](../active-directory/ntlm.md)
- [Kerberos](../active-directory/kerberos.md)
- [Kerberos Tickets](../active-directory/kerberos-tickets.md)
- [Pass-the-Hash](../active-directory/pass-the-hash.md)
- [Pass-the-Ticket](../active-directory/pass-the-ticket.md)
- [Password Spraying](../active-directory/password-spraying.md)
- [LAPS](../active-directory/laps.md)
- [gMSA](../active-directory/gmsa.md)
- [SMB](../active-directory/smb.md)
- [Shares](../active-directory/shares.md)
- [AD CS](../active-directory/ad-cs/index.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)

---

# References

- [Microsoft - Windows Authentication](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/windows-authentication-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Credentials Processes in Windows Authentication](https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/credentials-processes-in-windows-authentication){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Credential Manager](https://support.microsoft.com/en-us/windows/accessing-credential-manager-1b5c916a-6a16-889f-8581-fc16e8165ac0){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Data Protection API](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Credential Guard](https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Configuring Additional LSA Protection](https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/configuring-additional-lsa-protection){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Group Managed Service Accounts](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/group-managed-service-accounts/group-managed-service-accounts/group-managed-service-accounts-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - cmdkey](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmdkey){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - klist](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/klist){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Security](https://learn.microsoft.com/en-us/powershell/scripting/security/security-features){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Credential Access](https://attack.mitre.org/tactics/TA0006/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - OS Credential Dumping](https://attack.mitre.org/techniques/T1003/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Credentials from Password Stores](https://attack.mitre.org/techniques/T1555/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Credentials from Web Browsers](https://attack.mitre.org/techniques/T1555/003/){ target="_blank" rel="noopener noreferrer" }

---

> Use these techniques only on systems you own or have explicit permission to assess. Credential material is highly sensitive. Collect, store, and validate only what is necessary for the authorised assessment.
