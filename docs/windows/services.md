# Windows Services

Windows services are long-running background processes managed by the Windows Service Control Manager (SCM).

Services are used extensively by Windows itself and by third-party applications for:

- System functionality
- Endpoint security
- Backup software
- Monitoring agents
- Database services
- Web servers
- Deployment software
- Remote management
- Enterprise applications
- Update mechanisms

From a security perspective, services are particularly important because many execute with highly privileged identities such as `LocalSystem`.

A service is not vulnerable simply because it runs with high privileges. The important question is whether a lower-privileged user can influence the service, its executable, its configuration, or another resource consumed by it.

---

# 1. Service Security Model

A useful model is:

```text
Windows Service
      |
      +---- Service Account
      |
      +---- Executable
      |
      +---- Arguments
      |
      +---- Configuration
      |
      +---- Registry
      |
      +---- Files / Directories
      |
      +---- DLLs
      |
      +---- Service ACL
      |
      +---- Dependencies
      |
      +---- Network Listeners
```

For privilege escalation analysis:

```text
Privileged Service
       +
Low-Privileged User Control
       +
Execution Relationship
       =
Potential Privilege Escalation
```

The strongest findings establish all three components.

---

# 2. Service Control Manager

Windows services are managed by the Service Control Manager.

Common administrative interfaces include:

```text
services.msc
sc.exe
PowerShell
CIM
Windows API
```

Open the graphical service manager:

```cmd
services.msc
```

Command-line service controller:

```cmd
sc.exe query
```

PowerShell:

```powershell
Get-Service
```

CIM:

```powershell
Get-CimInstance Win32_Service
```

For security assessments, CIM is particularly useful because it exposes properties such as:

```text
Name
DisplayName
State
StartMode
StartName
PathName
ProcessId
```

---

# 3. Enumerate Services

PowerShell:

```powershell
Get-Service
```

Useful summary:

```powershell
Get-Service |
    Select-Object Name, DisplayName, Status, StartType
```

Running services:

```powershell
Get-Service |
    Where-Object Status -eq "Running"
```

Stopped services:

```powershell
Get-Service |
    Where-Object Status -eq "Stopped"
```

CIM provides more security-relevant information:

```powershell
Get-CimInstance Win32_Service
```

Focused:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, DisplayName, State, StartMode, StartName, PathName
```

---

# 4. Service Configuration

Inspect an individual service:

```cmd
sc.exe qc ServiceName
```

Example:

```cmd
sc.exe qc Spooler
```

Typical output contains:

```text
SERVICE_NAME
TYPE
START_TYPE
ERROR_CONTROL
BINARY_PATH_NAME
LOAD_ORDER_GROUP
DEPENDENCIES
SERVICE_START_NAME
```

PowerShell equivalent:

```powershell
Get-CimInstance Win32_Service -Filter "Name='Spooler'"
```

Focused:

```powershell
Get-CimInstance Win32_Service -Filter "Name='Spooler'" |
    Select-Object Name, State, StartMode, StartName, PathName
```

---

# 5. Service Accounts

Services can run under different identities.

Common built-in identities include:

```text
LocalSystem
NT AUTHORITY\SYSTEM
NT AUTHORITY\LOCAL SERVICE
NT AUTHORITY\NETWORK SERVICE
```

Services may also use:

```text
Local user accounts
Domain user accounts
Managed service accounts
Group Managed Service Accounts
Virtual service accounts
```

Enumerate service identities:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName
```

Unique service accounts:

```powershell
Get-CimInstance Win32_Service |
    Select-Object -ExpandProperty StartName |
    Sort-Object -Unique
```

---

# 6. LocalSystem Services

`LocalSystem` is a highly privileged built-in service identity.

Enumerate LocalSystem services:

```powershell
Get-CimInstance Win32_Service |
    Where-Object StartName -eq "LocalSystem" |
    Select-Object Name, State, StartMode, PathName
```

Depending on representation, also review services whose identity is shown as:

```text
LocalSystem
NT AUTHORITY\SYSTEM
```

A LocalSystem service is normal.

The security question is:

```text
Does a standard user control anything
that this LocalSystem service consumes?
```

---

# 7. Other Privileged Service Accounts

Domain service accounts may also have significant privileges.

Enumerate services not using common built-in service identities:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.StartName -and
        $_.StartName -notmatch '^(LocalSystem|NT AUTHORITY\\LocalService|NT AUTHORITY\\NetworkService)$'
    } |
    Select-Object Name, StartName, State, PathName
```

Review:

```text
Domain account privileges
Local group membership
Resource access
Service permissions
Credential management
Interactive logon rights
Password management
```

For Active Directory environments, consider whether gMSA can replace traditional service accounts.

See [gMSA](../active-directory/gmsa.md).

---

# 8. Service Executable Paths

Enumerate service executable paths:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, PathName
```

Search for third-party paths:

```powershell
Get-CimInstance Win32_Service |
    Where-Object PathName -and
    $_.PathName -notmatch 'C:\\Windows\\' |
    Select-Object Name, StartName, State, PathName
```

This can help identify:

```text
Custom enterprise software
Backup agents
Monitoring agents
Deployment software
Database services
Third-party security software
Vendor applications
```

Do not assume every non-Windows service is insecure.

---

# 9. Service Executable Permissions

Suppose a service uses:

```text
C:\Program Files\Vendor\Service\service.exe
```

Inspect the executable:

```cmd
icacls "C:\Program Files\Vendor\Service\service.exe"
```

PowerShell:

```powershell
Get-Acl "C:\Program Files\Vendor\Service\service.exe" |
    Format-List Owner, AccessToString
```

Detailed:

```powershell
(Get-Acl "C:\Program Files\Vendor\Service\service.exe").Access |
    Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited
```

Potentially dangerous broad principals include:

```text
Everyone
BUILTIN\Users
Authenticated Users
Domain Users
```

Potentially dangerous rights include:

```text
Write
Modify
FullControl
```

---

# 10. Service Directory Permissions

Inspect the directory containing the service executable:

```cmd
icacls "C:\Program Files\Vendor\Service"
```

PowerShell:

```powershell
Get-Acl "C:\Program Files\Vendor\Service" |
    Format-List Owner, AccessToString
```

Detailed:

```powershell
(Get-Acl "C:\Program Files\Vendor\Service").Access |
    Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited
```

Directory permissions can be just as important as permissions on the executable itself.

A writable parent directory may allow modification of:

```text
Executable files
DLLs
Configuration
Plugins
Scripts
Updates
Temporary resources
```

The actual impact depends on how the service uses those resources.

---

# 11. Controlled Write Test

A temporary-file test can safely confirm whether the current user has write access.

```powershell
$folder = "C:\ProgramData\CandidateFolder"
$file = Join-Path $folder "write-test-$PID-$(Get-Random).tmp"

try {
    New-Item -ItemType File -Path $file -ErrorAction Stop | Out-Null
    Write-Host "[+] Write access confirmed: $file"
}
catch {
    Write-Host "[-] Write access denied: $($_.Exception.Message)"
}
finally {
    Remove-Item $file -Force -ErrorAction SilentlyContinue
}
```

This proves:

```text
Current user can write to directory
```

It does not prove:

```text
Current user can obtain SYSTEM
```

The directory must still be correlated with a privileged consumer.

---

# 12. Correlate a Directory with Services

Suppose a writable directory is:

```text
C:\ProgramData\CandidateFolder
```

Search service paths:

```powershell
$folder = "C:\ProgramData\CandidateFolder"

Get-CimInstance Win32_Service |
    Where-Object PathName -Match ([regex]::Escape($folder)) |
    Select-Object Name, StartName, State, PathName
```

Assessment flow:

```text
Writable Directory
       |
       v
Referenced by Service?
       |
       +---- No
       |      |
       |      v
       |   Find other consumers
       |
       +---- Yes
              |
              v
       Service Privileged?
              |
              +---- No
              |
              +---- Yes
                     |
                     v
             What is writable?
                     |
                     v
             What does service load?
                     |
                     v
                Validate Impact
```

---

# 13. Service Binary Replacement Risk

A particularly important condition is:

```text
Privileged Service
        |
        v
Service Executable
        |
        v
Standard User Has Modify / Write
```

Example evidence:

```text
Service:
VendorService

Service account:
LocalSystem

Executable:
C:\ProgramData\Vendor\service.exe

Permissions:
BUILTIN\Users:(M)
```

This represents a potentially serious trust-boundary problem.

During routine assessments, it is often unnecessary to replace the executable to prove the weakness.

The service configuration and ACL may already provide strong evidence.

---

# 14. Service Configuration Permissions

A user may not need filesystem write access if they can modify the service configuration itself.

Query service security:

```cmd
sc.exe sdshow ServiceName
```

Example:

```cmd
sc.exe sdshow Spooler
```

The result is represented using Security Descriptor Definition Language.

Service permissions may control capabilities such as:

```text
Query configuration
Change configuration
Query status
Start
Stop
Pause
Delete
Modify permissions
```

The security significance depends on the exact rights granted to the current user or one of their groups.

---

# 15. Service Security Descriptor

Example structure:

```text
D:(A;;...;;;SY)(A;;...;;;BA)
```

Common SDDL principals include:

```text
SY = LocalSystem
BA = Built-in Administrators
BU = Built-in Users
AU = Authenticated Users
WD = Everyone
```

Do not report an SDDL string merely because a broad principal appears in it.

Determine the exact service rights assigned to that principal.

---

# 16. AccessChk

Microsoft Sysinternals AccessChk can help analyse service permissions.

[AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk){ target="_blank" rel="noopener noreferrer" }

AccessChk can inspect:

```text
Services
Files
Directories
Registry keys
Processes
Named pipes
```

It is useful for identifying cases where standard users have unexpected control over privileged services.

Tool output should always be manually validated.

---

# 17. Service Registry Configuration

Service configuration is stored primarily beneath:

```text
HKLM\SYSTEM\CurrentControlSet\Services
```

Enumerate:

```powershell
Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Services"
```

Specific service:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\Spooler"
```

Common values can include:

```text
ImagePath
Start
Type
ObjectName
DependOnService
DisplayName
Description
```

Not every service uses every value.

---

# 18. Service Registry Permissions

Inspect permissions:

```powershell
Get-Acl "HKLM:\SYSTEM\CurrentControlSet\Services\ServiceName"
```

Detailed:

```powershell
(Get-Acl "HKLM:\SYSTEM\CurrentControlSet\Services\ServiceName").Access |
    Format-Table IdentityReference, RegistryRights, AccessControlType, IsInherited
```

Potentially security-relevant rights include:

```text
SetValue
CreateSubKey
WriteKey
FullControl
```

If a standard user can modify configuration for a privileged service, investigate further.

---

# 19. ImagePath

Inspect a service's registry configuration:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\ServiceName" |
    Select-Object ImagePath, ObjectName, Start, Type
```

Compare this with CIM:

```powershell
Get-CimInstance Win32_Service -Filter "Name='ServiceName'" |
    Select-Object Name, StartName, PathName
```

Using more than one source can help confirm the effective configuration.

---

# 20. Unquoted Service Paths

Windows service executable paths containing spaces should generally be quoted appropriately.

Example candidate:

```text
C:\Program Files\Vendor Application\Service.exe
```

Potential parsing candidates could include portions of the path depending on the exact configuration and Windows path resolution behaviour.

The relevant security model is:

```text
Unquoted Path
      +
Spaces
      +
Privileged Service
      +
Writable Candidate Location
      =
Potential Privilege Escalation
```

All conditions matter.

---

# 21. Enumerate Unquoted Service Path Candidates

PowerShell:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.PathName -and
        $_.PathName -notmatch '^"' -and
        $_.PathName -match '\s'
    } |
    Select-Object Name, StartName, State, PathName
```

This produces candidates only.

Many results will not be exploitable.

---

# 22. Validate Unquoted Service Paths

For each candidate:

```text
1. Determine actual executable path

2. Determine whether arguments are present

3. Determine service account

4. Determine startup behaviour

5. Identify candidate path-resolution locations

6. Inspect permissions on those locations

7. Determine whether current user can create the relevant file

8. Determine whether Windows would actually resolve the path that way

9. Validate safely
```

Do not report:

```text
Path contains spaces
```

as equivalent to:

```text
Privilege escalation possible
```

---

# 23. Extracting Executable Paths

`PathName` may contain:

```text
"C:\Program Files\Vendor\Service.exe" --service
```

or:

```text
C:\Vendor\Service.exe -service
```

Be careful when parsing service paths automatically because:

- Paths can be quoted
- Arguments can be present
- Environment variables may be used
- Executable names can contain spaces
- Drivers differ from user-mode services

Manual verification is often necessary for interesting candidates.

---

# 24. Environment Variables in Service Paths

Service paths may reference environment variables.

Example:

```text
%SystemRoot%\System32\example.exe
```

Display:

```powershell
[Environment]::ExpandEnvironmentVariables("%SystemRoot%\System32\example.exe")
```

Environment expansion should be considered when determining the actual executable location.

---

# 25. Service DLLs

Not every service runs as a standalone executable.

Some services are hosted by shared processes such as:

```text
svchost.exe
```

The service implementation may then be provided through a DLL.

Service-specific configuration can include values under:

```text
HKLM\SYSTEM\CurrentControlSet\Services\ServiceName\Parameters
```

For applicable services, inspect:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\ServiceName\Parameters" -ErrorAction SilentlyContinue
```

Potential values can include:

```text
ServiceDll
```

If a privileged service loads a DLL from a user-writable location, investigate the trust relationship carefully.

---

# 26. Service DLL Permissions

If a service references:

```text
C:\ProgramData\Vendor\Service\service.dll
```

inspect:

```powershell
Get-Acl "C:\ProgramData\Vendor\Service\service.dll" |
    Format-List Owner, AccessToString
```

Directory:

```powershell
Get-Acl "C:\ProgramData\Vendor\Service" |
    Format-List Owner, AccessToString
```

The key relationship remains:

```text
Privileged Service
       +
User-Modifiable DLL
       +
DLL Actually Loaded
       =
Potential Privilege Escalation
```

---

# 27. DLL Search Behaviour

Some services dynamically load libraries.

Potential security risk can arise when:

```text
Privileged Service
       |
       v
Loads DLL
       |
       v
Searches Multiple Locations
       |
       v
User-Writable Location Included
```

The existence of a missing DLL is not sufficient evidence.

Validate:

```text
Actual load attempt
Search path
Writable location
Service identity
Architecture
Application behaviour
Existing mitigations
```

Process Monitor is useful for runtime investigation.

[Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon){ target="_blank" rel="noopener noreferrer" }

---

# 28. Process Monitor for Service Analysis

Process Monitor can observe:

```text
File access
Registry access
Process creation
DLL loading
Configuration access
Missing files
```

For service investigation, useful filters can conceptually include:

```text
Process Name
Process ID
Path
Operation
Result
```

For example, focus on:

```text
NAME NOT FOUND
ACCESS DENIED
CreateFile
Load Image
RegOpenKey
RegQueryValue
```

Interpret events in the context of the specific service.

---

# 29. Service Processes

Running services can be correlated with process IDs.

```powershell
Get-CimInstance Win32_Service |
    Where-Object State -eq "Running" |
    Select-Object Name, ProcessId, StartName, PathName
```

For a specific PID:

```powershell
Get-Process -Id 1234
```

CIM:

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId=1234"
```

This helps correlate:

```text
Service
Process
Executable
Account
Network activity
```

---

# 30. Services and Network Listeners

A service may expose a network listener.

Listening connections:

```powershell
Get-NetTCPConnection -State Listen
```

Map service PIDs:

```powershell
$services = Get-CimInstance Win32_Service |
    Where-Object State -eq "Running"

Get-NetTCPConnection -State Listen | ForEach-Object {
    $connection = $_
    $service = $services | Where-Object ProcessId -eq $connection.OwningProcess

    [PSCustomObject]@{
        LocalAddress = $connection.LocalAddress
        LocalPort = $connection.LocalPort
        PID = $connection.OwningProcess
        Service = ($service.Name -join ", ")
        Account = ($service.StartName -join ", ")
    }
}
```

This can help identify network-facing privileged services.

---

# 31. Shared Service Processes

Multiple services can share the same process.

This is particularly common with:

```text
svchost.exe
```

Therefore:

```text
PID -> Service
```

may be:

```text
PID -> Multiple Services
```

Enumerate:

```powershell
Get-CimInstance Win32_Service |
    Where-Object State -eq "Running" |
    Group-Object ProcessId |
    Where-Object Count -gt 1
```

Do not assume one listener belongs to one service simply because they share a PID.

---

# 32. Service Start Modes

Common start modes include:

```text
Automatic
Manual
Disabled
```

CIM:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartMode, State
```

Automatic services:

```powershell
Get-CimInstance Win32_Service |
    Where-Object StartMode -eq "Auto" |
    Select-Object Name, StartName, State, PathName
```

Startup behaviour affects practical exploitability.

A vulnerable service that starts automatically may present a different risk profile from one that can never be started by the assessed user.

---

# 33. Can the Current User Start a Service?

The fact that a service is stopped does not mean a standard user can start it.

Attempting to start or stop production services may cause disruption.

Prefer inspecting the service ACL first.

Query:

```cmd
sc.exe sdshow ServiceName
```

Use AccessChk where permitted to determine effective service rights.

Only perform state changes when explicitly authorised and operationally safe.

---

# 34. Can the Current User Stop a Service?

Stopping a service can affect:

```text
Business applications
Endpoint protection
Networking
Backups
Monitoring
Databases
Authentication
```

Do not use service-stop attempts merely as a permission test on production systems.

Inspect permissions first.

---

# 35. Service Dependencies

Query:

```cmd
sc.exe qc ServiceName
```

PowerShell:

```powershell
Get-Service -Name ServiceName -DependentServices
```

Services required by the target:

```powershell
Get-Service -Name ServiceName -RequiredServices
```

Dependencies matter because restarting one service may affect others.

They can also reveal relationships between applications.

---

# 36. Driver Services

Windows also represents drivers through the service infrastructure.

Enumerate:

```powershell
Get-CimInstance Win32_SystemDriver
```

Focused:

```powershell
Get-CimInstance Win32_SystemDriver |
    Select-Object Name, State, StartMode, PathName
```

Drivers operate in a highly privileged context.

Driver security analysis requires particular care because unsafe testing can crash or destabilise the operating system.

Do not load, unload, replace, or modify drivers during routine testing unless specifically authorised.

---

# 37. Service Executable Signatures

Inspect the digital signature:

```powershell
Get-AuthenticodeSignature "C:\Path\Service.exe"
```

Focused:

```powershell
Get-AuthenticodeSignature "C:\Path\Service.exe" |
    Select-Object Status, StatusMessage, SignerCertificate
```

Signature status may help determine:

```text
Vendor
Trust
Application-control relevance
Unexpected binary replacement
```

A valid signature does not guarantee that the application is secure.

---

# 38. Service Executable Version

```powershell
(Get-Item "C:\Path\Service.exe").VersionInfo
```

Focused:

```powershell
(Get-Item "C:\Path\Service.exe").VersionInfo |
    Select-Object FileVersion, ProductVersion, CompanyName, ProductName
```

Version information can be used during vulnerability research.

Always verify affected version ranges against authoritative vendor information before reporting a CVE.

---

# 39. Service Executable Hash

```powershell
Get-FileHash "C:\Path\Service.exe" -Algorithm SHA256
```

Hashes are useful for:

```text
Evidence
Integrity verification
Comparison between systems
Malware analysis
Application-control investigation
```

Record hashes when preserving binary evidence.

---

# 40. Service Configuration Files

Services often consume configuration files such as:

```text
*.config
*.ini
*.xml
*.json
*.yml
*.yaml
*.conf
```

Search a specific application directory:

```powershell
Get-ChildItem "C:\ProgramData\Vendor" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object Extension -Match '\.(config|ini|xml|json|yml|yaml|conf)$'
```

Inspect permissions:

```powershell
Get-Acl "C:\ProgramData\Vendor\service.config" |
    Format-List Owner, AccessToString
```

Potential security significance depends on what the service reads from the file.

---

# 41. Sensitive Service Configuration

Configuration may contain:

```text
Database credentials
API credentials
Service-account references
Network shares
Certificate paths
Private keys
Connection strings
Management endpoints
```

Only collect sensitive information required to demonstrate the finding.

Avoid copying secrets unnecessarily into screenshots, tickets, or reports.

---

# 42. Service Command-Line Arguments

Service paths can contain arguments:

```text
"C:\Program Files\Vendor\Service.exe" --config "C:\ProgramData\Vendor\service.conf"
```

This can reveal additional security-relevant resources.

For example:

```text
Privileged Service
       |
       v
--config
       |
       v
C:\ProgramData\Vendor\service.conf
       |
       v
Standard User Can Modify
```

The executable itself may be protected while its configuration remains vulnerable.

---

# 43. Service-Referenced Scripts

Some services invoke or depend on scripts.

Examples may include:

```text
PowerShell
Batch files
Python
JavaScript
Vendor scripting formats
```

If a privileged service consumes a script, inspect:

```text
Script permissions
Parent directory permissions
Interpreter
Service identity
Arguments
Configuration
```

A modifiable script used by a privileged service can represent a significant trust-boundary weakness.

---

# 44. Search for Service-Related Files

Once a service directory is known:

```powershell
Get-ChildItem "C:\ProgramData\Vendor\Service" -Recurse -File -ErrorAction SilentlyContinue |
    Select-Object FullName, Length, LastWriteTime
```

Avoid recursively searching the entire filesystem unless required.

Targeted investigation is faster and generates less unnecessary activity.

---

# 45. Program Files vs ProgramData

Typical application binaries are often stored beneath:

```text
C:\Program Files
C:\Program Files (x86)
```

Application data may be stored beneath:

```text
C:\ProgramData
```

`ProgramData` is not automatically writable by every user.

Permissions vary by application and subdirectory.

Always verify:

```powershell
Get-Acl "C:\ProgramData\Vendor"
```

rather than assuming access.

---

# 46. Custom Service Locations

Pay particular attention to services running from locations such as:

```text
C:\Apps
C:\Tools
C:\Company
C:\Vendor
C:\ProgramData\Vendor
D:\Applications
```

These are not inherently insecure.

However, custom deployment practices sometimes result in weaker ACLs than standard Windows application directories.

---

# 47. User-Writable Locations

Common user-writable locations may include:

```text
User profile directories
%TEMP%
%LOCALAPPDATA%
Some application-specific ProgramData directories
Custom directories with weak ACLs
```

A privileged service referencing one of these locations deserves further investigation.

Do not assume write access without verifying the effective ACL.

---

# 48. Writable Service Path Search Strategy

A practical workflow:

```text
Enumerate Services
      |
      v
Filter Privileged Services
      |
      v
Extract Paths
      |
      v
Identify Third-Party / Custom Paths
      |
      v
Inspect File ACL
      |
      v
Inspect Directory ACL
      |
      v
Inspect Configuration
      |
      v
Inspect Service ACL
      |
      v
Validate Consumer Relationship
```

This is usually more effective than blindly scanning every directory on the host.

---

# 49. Service Permissions vs Filesystem Permissions

These are different security controls.

## Filesystem permission

Controls access to:

```text
service.exe
service.dll
config.ini
application directory
```

## Service permission

Controls access to the SCM service object itself.

Examples:

```text
Start service
Stop service
Change service configuration
Delete service
Modify service ACL
```

A secure filesystem does not compensate for an insecure service ACL.

Likewise, a secure service ACL does not compensate for a user-writable service executable.

---

# 50. Service Misconfiguration Matrix

| Condition | Security Significance |
|---|---|
| SYSTEM service exists | Normal |
| SYSTEM service executable protected | Expected |
| SYSTEM service executable user-writable | High concern |
| SYSTEM service directory user-writable | Investigate |
| SYSTEM service configuration user-writable | High concern |
| Standard user can change privileged service configuration | High concern |
| Unquoted path with no writable candidate | Usually not exploitable |
| Unquoted path with writable candidate | Potential escalation |
| Writable configuration unused by service | Not sufficient |
| Missing DLL with no writable search path | Not sufficient |
| Privileged service loads user-writable DLL | High concern |
| Service uses domain account | Not inherently vulnerable |

---

# 51. Automated Service Enumeration

Tools that can help identify service-related weaknesses include:

```text
WinPEAS
PrivescCheck
SharpUp
Seatbelt
AccessChk
Autoruns
Process Monitor
```

These tools can identify candidates such as:

```text
Weak service ACLs
Writable executables
Writable directories
Unquoted paths
Interesting service accounts
Configuration files
Automatic execution relationships
```

Tool output should be treated as candidate evidence requiring manual validation.

---

# 52. WinPEAS

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

WinPEAS can enumerate:

```text
Services
Service permissions
File permissions
Unquoted paths
Applications
Scheduled tasks
Credentials
Security controls
```

Do not report every highlighted service result.

Verify the actual ACL and execution context.

---

# 53. PrivescCheck

[PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }

PrivescCheck can help identify:

```text
Weak service permissions
Writable service files
Writable directories
Unquoted service paths
Other privilege escalation candidates
```

Manual verification remains necessary.

---

# 54. SharpUp

[SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }

SharpUp focuses on identifying Windows privilege escalation opportunities, including service-related configuration weaknesses.

Use results as investigation leads.

---

# 55. Seatbelt

[Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }

Seatbelt can provide broader host context around services, applications, security controls, and system configuration.

This is useful when a service finding depends on surrounding host configuration.

---

# 56. Autoruns

[Autoruns](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns){ target="_blank" rel="noopener noreferrer" }

Autoruns can expose automatic execution relationships including:

```text
Services
Drivers
Scheduled tasks
Logon entries
Other persistence locations
```

This can help identify privileged execution paths referencing modifiable resources.

---

# 57. Manual Validation Workflow

When an automated tool reports a vulnerable service:

```text
Candidate
    |
    v
Get Service Name
    |
    v
Get Service Account
    |
    v
Get Executable Path
    |
    v
Inspect Executable ACL
    |
    v
Inspect Directory ACL
    |
    v
Inspect Service ACL
    |
    v
Inspect Config / DLLs
    |
    v
Determine Current User Access
    |
    v
Validate Execution Relationship
    |
    v
Assess Impact
```

Do not skip the manual validation stage.

---

# 58. Safe Validation

Prefer validation that does not modify privileged application components.

For example:

```text
whoami /all
        +
Get-CimInstance Win32_Service
        +
Get-Acl
        +
Controlled temporary write test
        =
Strong evidence
```

Avoid unnecessary:

```text
Replacing service executables
Changing service configuration
Restarting production services
Stopping security products
Modifying service registry values
Loading arbitrary DLLs
```

unless specifically authorised and required.

---

# 59. Evidence Collection

For service findings, capture:

```text
Host
Current user
Current groups
Service name
Display name
Service state
Start mode
Service account
Executable path
Executable ACL
Directory ACL
Service ACL
Registry ACL if relevant
Configuration files
Controlled validation
Security impact
```

Example:

```text
Host:
WS01

Current user:
CORP\standarduser

Service:
VendorService

State:
Running

Start mode:
Automatic

Service account:
LocalSystem

Executable:
C:\ProgramData\Vendor\Service\service.exe

Directory:
C:\ProgramData\Vendor\Service

Directory ACL:
BUILTIN\Users - Modify

Validation:
The assessed standard user successfully created and removed a temporary
file within the service directory.
```

---

# 60. Evidence Commands

Identity:

```powershell
whoami /all
```

Service:

```powershell
Get-CimInstance Win32_Service -Filter "Name='VendorService'" |
    Select-Object Name, DisplayName, State, StartMode, StartName, PathName
```

Directory ACL:

```powershell
Get-Acl "C:\ProgramData\Vendor\Service" |
    Format-List Owner, AccessToString
```

Executable ACL:

```powershell
Get-Acl "C:\ProgramData\Vendor\Service\service.exe" |
    Format-List Owner, AccessToString
```

Service security descriptor:

```cmd
sc.exe sdshow VendorService
```

This provides a reproducible evidence chain.

---

# 61. Common False Positive - SYSTEM Service

Observation:

```text
Service runs as LocalSystem.
```

This alone is not a vulnerability.

LocalSystem is intentionally used by services requiring extensive local privileges.

Investigate what lower-privileged users can influence.

---

# 62. Common False Positive - Writable Directory

Observation:

```text
C:\ProgramData\Vendor is writable.
```

This alone does not establish service privilege escalation.

Determine:

```text
Which service uses it?
What file is consumed?
What account runs the service?
When is the resource consumed?
```

---

# 63. Common False Positive - Unquoted Path

Observation:

```text
C:\Program Files\Vendor Application\Service.exe
```

Do not immediately report an unquoted service path vulnerability.

Determine whether:

```text
Path is actually unquoted
Candidate path exists
Current user can create required file
Service is privileged
Service execution reaches candidate
```

---

# 64. Common False Positive - Stopped Service

Observation:

```text
Potentially vulnerable service is stopped.
```

This does not automatically remove the risk.

Determine:

```text
Can it start automatically?
Can the current user start it?
Will it start during boot?
Is it triggered by another application?
Is it obsolete?
```

Practical exploitability affects severity.

---

# 65. Common False Positive - Service Start Permission

A standard user being allowed to start a service is not necessarily a vulnerability.

Some services intentionally permit non-administrative users to start them.

The important question is whether starting the service can be combined with control over a privileged resource.

---

# 66. Common False Positive - Service Stop Permission

Likewise:

```text
User can stop service
```

may create an availability concern without creating privilege escalation.

Separate:

```text
Availability Impact
```

from:

```text
Privilege Escalation
```

when reporting.

---

# 67. Service Finding Severity

Severity depends on practical impact.

Example model:

```text
Current User
      |
      v
Can Control Resource?
      |
      v
Privileged Service Consumes Resource?
      |
      v
Can Trigger Consumption?
      |
      v
Privilege Obtained?
      |
      v
Reliability / User Interaction
      |
      v
Severity
```

Examples:

| Condition | Typical Concern |
|---|---|
| Writable unused service data | Low / informational |
| Writable service config with limited impact | Context dependent |
| Writable SYSTEM service executable | High |
| Change-config rights over SYSTEM service | High |
| Privileged service loads user-controlled DLL | High |
| Exposed privileged service credential | High / critical depending on reuse |

Use the organisation's agreed severity methodology for the final rating.

---

# 68. Remediation - Filesystem Permissions

For service executables and directories:

```text
Remove unnecessary write access
Remove unnecessary Modify access
Restrict FullControl
Use least privilege
Review inherited ACLs
Restrict application directories
Protect configuration files
Protect DLLs and scripts
```

A typical desired relationship is:

```text
SYSTEM / Administrators
        |
        +---- Modify / Full Control

Standard Users
        |
        +---- Read / Execute only
```

Exact permissions depend on application requirements.

---

# 69. Remediation - Service Permissions

Restrict service-control permissions to identities that require them.

Review access to:

```text
Change configuration
Delete service
Modify service security
Start / stop where sensitive
```

Administrative service management should generally remain restricted to trusted administrative identities.

---

# 70. Remediation - Service Accounts

Apply least privilege to service identities.

Consider:

```text
Does the service require LocalSystem?
Can LocalService be used?
Can NetworkService be used?
Can a virtual service account be used?
Can gMSA be used for domain services?
Are interactive logon rights necessary?
```

Do not change service identities without application compatibility testing.

---

# 71. Remediation - Unquoted Service Paths

Where appropriate, quote executable paths containing spaces.

Prefer:

```text
"C:\Program Files\Vendor Application\Service.exe"
```

rather than:

```text
C:\Program Files\Vendor Application\Service.exe
```

Also secure the relevant filesystem locations.

Quoting the path does not compensate for weak executable or directory permissions.

---

# 72. Remediation - Configuration Files

Protect service configuration with restrictive ACLs.

Avoid:

```text
Everyone - Modify
Users - Modify
Authenticated Users - Write
```

where the configuration controls privileged service behaviour.

Store secrets using appropriate credential-management mechanisms rather than plaintext configuration where possible.

---

# 73. Remediation - Monitoring

Monitor sensitive service changes.

Potential telemetry includes:

```text
Service installation
Service configuration changes
Service start / stop activity
Executable replacement
Registry modifications
File modifications
Application-control events
Endpoint-security alerts
```

Centralise relevant telemetry where possible.

---

# 74. Windows Event Logs

Service activity can appear in Windows event logs.

System log:

```powershell
Get-WinEvent -LogName System -MaxEvents 100
```

Filter Service Control Manager:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    ProviderName = 'Service Control Manager'
} -MaxEvents 50
```

Useful events depend on the activity being investigated.

Always interpret event IDs in the context of their provider and Windows version.

---

# 75. Service Installation Monitoring

Service creation is an important security event.

A commonly investigated System event is:

```text
Service Control Manager Event ID 7045
```

Example:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    Id = 7045
} -MaxEvents 20 -ErrorAction SilentlyContinue |
    Select-Object TimeCreated, Id, Message
```

Security telemetry may provide additional visibility depending on audit policy.

---

# 76. Registry Monitoring

Important service configuration resides beneath:

```text
HKLM\SYSTEM\CurrentControlSet\Services
```

Changes to sensitive values such as:

```text
ImagePath
ObjectName
Start
ServiceDll
```

can warrant monitoring, particularly for privileged services.

Endpoint monitoring can provide richer context than registry auditing alone.

---

# 77. File Monitoring

Important service resources include:

```text
Executable
DLLs
Configuration
Scripts
Plugins
Update packages
```

Unexpected modifications to privileged service resources should be investigated.

File monitoring is particularly valuable for custom enterprise applications stored outside standard protected directories.

---

# 78. Application Control

AppLocker or WDAC can provide additional controls around executable content.

However:

```text
Application Control
        !=
Correct Filesystem Permissions
```

A privileged service executable should still have appropriate ACLs.

Application control should complement rather than replace secure permissions.

---

# 79. Defender and EDR

Endpoint protection may detect suspicious service activity such as:

```text
Unexpected service creation
Suspicious service executable
Unusual service configuration changes
Malicious binaries
Unexpected child processes
Credential abuse
```

Do not disable security controls during normal service enumeration.

The defensive environment itself is part of the assessment.

---

# 80. Service Assessment Checklist

## Enumeration

- [ ] Enumerate all services
- [ ] Record service states
- [ ] Record start modes
- [ ] Record service accounts
- [ ] Record executable paths
- [ ] Identify third-party services
- [ ] Identify privileged services

## Filesystem

- [ ] Inspect executable ACLs
- [ ] Inspect parent directory ACLs
- [ ] Inspect configuration ACLs
- [ ] Inspect DLL ACLs
- [ ] Inspect script ACLs
- [ ] Identify user-writable resources

## Service Object

- [ ] Inspect service security descriptor
- [ ] Determine change-config rights
- [ ] Determine start rights where relevant
- [ ] Determine stop rights where relevant
- [ ] Determine delete rights
- [ ] Determine ACL modification rights

## Registry

- [ ] Inspect service registry key
- [ ] Inspect registry ACL
- [ ] Inspect ImagePath
- [ ] Inspect ObjectName
- [ ] Inspect Parameters
- [ ] Inspect ServiceDll where applicable

## Path Analysis

- [ ] Identify unquoted paths
- [ ] Validate candidate path locations
- [ ] Check filesystem permissions
- [ ] Expand environment variables
- [ ] Separate executable from arguments

## Runtime

- [ ] Map service to PID
- [ ] Identify network listeners
- [ ] Identify shared service processes
- [ ] Review dependencies
- [ ] Review runtime file access where necessary

## Validation

- [ ] Confirm current user
- [ ] Confirm effective permissions
- [ ] Confirm privileged context
- [ ] Confirm resource consumption
- [ ] Confirm practical trigger
- [ ] Use non-destructive validation
- [ ] Preserve evidence

## Reporting

- [ ] Explain trust relationship
- [ ] Explain affected privilege boundary
- [ ] Avoid false positives
- [ ] Document practical impact
- [ ] Recommend root-cause remediation

---

# 81. Quick Service Enumeration

PowerShell:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, DisplayName, State, StartMode, StartName, PathName
```

Privileged services:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.StartName -eq "LocalSystem" -or
        $_.StartName -eq "NT AUTHORITY\SYSTEM"
    } |
    Select-Object Name, State, StartMode, StartName, PathName
```

Unquoted candidates:

```powershell
Get-CimInstance Win32_Service |
    Where-Object {
        $_.PathName -and
        $_.PathName -notmatch '^"' -and
        $_.PathName -match '\s'
    } |
    Select-Object Name, StartName, PathName
```

Running services with PIDs:

```powershell
Get-CimInstance Win32_Service |
    Where-Object State -eq "Running" |
    Select-Object Name, ProcessId, StartName, PathName
```

---

# 82. Quick Candidate Validation

Given:

```text
ServiceName = VendorService
```

Configuration:

```powershell
Get-CimInstance Win32_Service -Filter "Name='VendorService'" |
    Select-Object Name, State, StartMode, StartName, PathName
```

Registry:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\VendorService" -ErrorAction SilentlyContinue
```

Registry ACL:

```powershell
Get-Acl "HKLM:\SYSTEM\CurrentControlSet\Services\VendorService" |
    Format-List Owner, AccessToString
```

Service ACL:

```cmd
sc.exe sdshow VendorService
```

Then inspect the exact executable and directory ACLs based on the discovered path.

---

# 83. Service Assessment Decision Tree

```text
Enumerate Service
       |
       v
Privileged Account?
       |
       +---- No ----> Assess according to actual impact
       |
       +---- Yes
              |
              v
       Executable Writable?
              |
              +---- Yes ----> High-priority candidate
              |
              +---- No
                     |
                     v
              Directory Writable?
                     |
                     +---- Yes ----> Determine consumed resources
                     |
                     +---- No
                            |
                            v
                     Service ACL Weak?
                            |
                            +---- Yes ----> Determine exact rights
                            |
                            +---- No
                                   |
                                   v
                            Config Writable?
                                   |
                                   +---- Yes ----> Validate influence
                                   |
                                   +---- No
                                          |
                                          v
                                   DLL / Script Writable?
                                          |
                                          +---- Yes ----> Validate loading
                                          |
                                          +---- No
                                                 |
                                                 v
                                          Unquoted Path?
                                                 |
                                                 +---- Yes ----> Validate candidate path
                                                 |
                                                 +---- No
                                                        |
                                                        v
                                                  Continue Review
```

---

# 84. Full Service Testing Flow

```text
Current User
     |
     v
Enumerate Services
     |
     v
Identify Privileged Services
     |
     +------------------------------+
     |                              |
     v                              v
Service Object                 Filesystem
     |                              |
     v                              v
Service ACL                    Executable ACL
     |                              |
     v                              v
Change Config?                 Directory ACL
     |                              |
     |                              v
     |                         Config / DLL / Script
     |                              |
     +---------------+--------------+
                     |
                     v
                  Registry
                     |
                     v
               Registry ACL
                     |
                     v
                 ImagePath
                     |
                     v
                Parameters
                     |
                     v
                  Runtime
                     |
                     +---- Process
                     +---- DLL loads
                     +---- Files
                     +---- Network
                     |
                     v
             Practical Influence?
                     |
              +------+------+
              |             |
             No            Yes
              |             |
              v             v
          Continue      Safe Validation
                            |
                            v
                         Evidence
                            |
                            v
                          Report
```

---

# 85. Reporting Example - Writable Service Executable

## Title

```text
Standard Users Can Modify a LocalSystem Service Executable
```

## Description

```text
A Windows service running with LocalSystem privileges uses an executable
that can be modified by standard users.

Because the Service Control Manager launches the affected executable in the
LocalSystem security context, unauthorised modification of the executable
could allow a lower-privileged user to influence privileged code execution.
```

## Evidence

```text
Current user:
CORP\standarduser

Service:
VendorService

Service account:
LocalSystem

Executable:
C:\ProgramData\Vendor\Service\service.exe

Permissions:
BUILTIN\Users - Modify
```

## Impact

```text
A standard user may be able to modify code executed by a LocalSystem service,
potentially resulting in elevation of privileges to SYSTEM.
```

## Recommendation

```text
Remove write, modify, and full-control permissions for unprivileged users
from the service executable and its parent directory.

Restrict modification rights to trusted administrative and service
identities and review other privileged service directories for equivalent
permission weaknesses.
```

---

# 86. Reporting Example - Writable Service Directory

## Title

```text
Standard Users Can Modify a Directory Used by a Privileged Windows Service
```

## Description

```text
A directory used by a privileged Windows service grants Modify permissions
to standard users.

The directory contains resources consumed by the service. This trust
relationship may allow lower-privileged users to influence privileged
service behaviour depending on which files can be modified and when they
are loaded.
```

## Evidence

```text
Service:
VendorService

Service account:
LocalSystem

Directory:
C:\ProgramData\Vendor\Service

Permission:
BUILTIN\Users - Modify

Controlled write test:
Successful
```

## Recommendation

```text
Restrict write access to the service directory and its security-sensitive
contents.

Standard users should normally receive only the minimum permissions required
for legitimate application use.
```

---

# 87. Reporting Example - Unquoted Service Path

## Title

```text
Privileged Windows Service Uses an Unquoted Executable Path
```

## Description

```text
A privileged Windows service uses an executable path containing spaces
without appropriate quotation.

A practical privilege escalation condition exists only where the Windows
path-resolution behaviour reaches a location in which a lower-privileged
user can create the relevant executable candidate.
```

## Evidence

```text
Service:
VendorService

Service account:
LocalSystem

Path:
C:\Program Files\Vendor Application\Service.exe

Writable candidate:
Validated during assessment
```

## Recommendation

```text
Enclose the complete executable path in quotation marks and restrict write
permissions on all directories involved in service execution.

Review other service configurations for equivalent path and permission
weaknesses.
```

---

# 88. Reporting Example - Weak Service ACL

## Title

```text
Standard Users Can Modify the Configuration of a LocalSystem Service
```

## Description

```text
The service security descriptor grants a non-administrative principal
permission to modify the configuration of a service running as LocalSystem.

This creates a trust-boundary weakness because a lower-privileged user can
influence how a highly privileged service is configured.
```

## Evidence

```text
Service:
VendorService

Service account:
LocalSystem

Affected principal:
BUILTIN\Users

Service permission:
Configuration modification rights
```

## Recommendation

```text
Restrict service configuration permissions to trusted administrative
identities.

Review the service security descriptor and remove unnecessary control rights
from standard users and broadly assigned groups.
```

---

# 89. Defensive Detection Model

Service-related attacks can generate several forms of telemetry.

```text
Service Change
      |
      +---- SCM Event
      |
      +---- Registry Change
      |
      +---- File Change
      |
      +---- Process Creation
      |
      +---- Application-Control Event
      |
      +---- EDR Telemetry
      |
      v
Central Monitoring
      |
      v
Detection
      |
      v
Investigation
```

Defenders should correlate:

```text
Who changed the service?
What changed?
Which binary executed?
Which account executed it?
Was the binary newly created?
Was the path unusual?
Did the service create unexpected children?
Did the service initiate network connections?
```

---

# 90. Final Testing Model

The most reliable Windows service assessment model is:

```text
1. Identify the service.

2. Determine the service identity.

3. Determine the executable and arguments.

4. Inspect the executable ACL.

5. Inspect parent directory ACLs.

6. Inspect service-object permissions.

7. Inspect registry permissions.

8. Identify configuration, DLLs, scripts, and plugins.

9. Determine what the service actually consumes.

10. Determine whether the current user controls any consumed resource.

11. Determine how and when the service consumes it.

12. Validate the condition safely.

13. Collect reproducible evidence.

14. Determine the privilege boundary crossed.

15. Recommend removal of the underlying trust relationship.
```

Avoid:

```text
Service runs as SYSTEM
       |
       v
Vulnerability
```

Prefer:

```text
Service runs as SYSTEM
       |
       v
Identify resources
       |
       v
Inspect permissions
       |
       v
Identify user control
       |
       v
Validate consumption
       |
       v
Demonstrate security impact
       |
       v
Finding
```

---

# Related Notes

- [Windows](index.md)
- [Windows Enumeration](enumeration.md)
- [Windows Privilege Escalation](privilege-escalation.md)
- [PowerShell](powershell.md)
- [Windows Credentials](credentials.md)
- [Active Directory](../active-directory/index.md)
- [gMSA](../active-directory/gmsa.md)
- [Windows Cheatsheet](../cheatsheets/windows.md)
- [PowerShell Cheatsheet](../cheatsheets/powershell.md)

---

# References

- [Microsoft - Introduction to Windows Service Applications](https://learn.microsoft.com/en-us/dotnet/framework/windows-services/introduction-to-windows-service-applications){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Service Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Service Security and Access Control](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-control){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Service Control Manager](https://learn.microsoft.com/en-us/windows/win32/services/service-control-manager){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Service User Accounts](https://learn.microsoft.com/en-us/windows/win32/services/service-user-accounts){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - sc.exe qc](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/sc-qc){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - sc.exe sdshow](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc742037(v=ws.11)){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals - AccessChk](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals - Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon){ target="_blank" rel="noopener noreferrer" }
- [Microsoft Sysinternals - Autoruns](https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [PrivescCheck](https://github.com/itm4n/PrivescCheck){ target="_blank" rel="noopener noreferrer" }
- [SharpUp](https://github.com/GhostPack/SharpUp){ target="_blank" rel="noopener noreferrer" }
- [Seatbelt](https://github.com/GhostPack/Seatbelt){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Services: Service Execution](https://attack.mitre.org/techniques/T1569/002/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Create or Modify System Process: Windows Service](https://attack.mitre.org/techniques/T1543/003/){ target="_blank" rel="noopener noreferrer" }

---

> Use these techniques only on systems you own or have explicit permission to assess.
