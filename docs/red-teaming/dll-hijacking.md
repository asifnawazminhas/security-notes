# DLL Hijacking

DLL hijacking is a Windows security issue that can occur when an application loads a Dynamic Link Library (DLL) without securely controlling where that library is obtained from.

If Windows searches a user-writable location before reaching the legitimate DLL, an attacker may be able to influence which library the application loads. During an authorised penetration test or red team assessment, DLL hijacking testing can be used to identify insecure application configurations and validate application-control and endpoint-detection controls.

!!! warning "Authorised Use Only"
    DLL hijacking testing can affect application execution and operating-system behaviour. Perform these tests only against explicitly authorised systems and applications. Prefer harmless validation methods and controlled laboratory environments.

---

## Overview

A simplified DLL loading process can look like:

```text
Application Starts
        |
        v
Application Requires DLL
        |
        v
Windows Resolves DLL
        |
        v
Search Locations Evaluated
        |
        +---- Application Directory
        |
        +---- System Locations
        |
        +---- Other Search Locations
        |
        v
DLL Located
        |
        v
DLL Loaded
```

The security problem appears when an attacker-controlled location participates in the resolution process.

Conceptually:

```text
Application
    |
    v
Requests example.dll
    |
    v
Search Path
    |
    +---- Writable Location
    |         |
    |         v
    |     example.dll
    |
    +---- Legitimate Location
              |
              v
          example.dll
```

If the writable location takes precedence, the wrong library may be selected.

---

## DLLs

Dynamic Link Libraries are Portable Executable (PE) files containing code or resources that can be shared between Windows applications.

Common examples include:

```text
kernel32.dll
user32.dll
advapi32.dll
version.dll
winhttp.dll
```

DLLs commonly use the `.dll` extension.

Applications can load libraries automatically as part of normal startup or explicitly through Windows APIs.

---

## DLL Loading

Windows applications may load libraries in several ways.

Conceptually, an application can request:

```text
C:\Program Files\Application\example.dll
```

or simply:

```text
example.dll
```

A fully qualified path provides Windows with an explicit location.

A library name without a complete path may require Windows to determine where the library should be obtained from.

That distinction is important during DLL hijacking assessments.

---

## DLL Search Behaviour

Windows DLL search behaviour depends on factors including:

- application configuration;
- Windows version;
- Safe DLL Search Mode;
- whether a full path was supplied;
- packaged vs unpackaged applications;
- loaded-module state;
- KnownDLLs;
- application directories;
- system directories;
- current directory;
- `PATH`;
- APIs used by the application.

Do not assume every application follows an identical search sequence.

Microsoft's DLL search-order documentation should be used when analysing a specific scenario.

---

## KnownDLLs

Windows maintains a set of commonly used system libraries known as `KnownDLLs`.

The configuration can be inspected from:

```powershell
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs"
```

KnownDLL handling can prevent some system libraries from being resolved through ordinary filesystem search behaviour.

Therefore, simply identifying a DLL name is not sufficient evidence of hijackability.

---

## Safe DLL Search Mode

Windows supports Safe DLL Search Mode, which influences the order in which certain locations are searched.

The relevant configuration can be inspected with:

```powershell
Get-ItemProperty `
    "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager" `
    -Name SafeDllSearchMode `
    -ErrorAction SilentlyContinue
```

Absence of a registry value should not automatically be interpreted as an insecure configuration.

Windows defaults and application-specific behaviour must also be considered.

---

## Common DLL Hijacking Conditions

A potential DLL hijacking issue generally requires several conditions.

For example:

```text
Application loads a DLL
        +
DLL is resolved using a searchable name/path
        +
Attacker can influence a searched location
        +
Application loads from that location
        =
Potential DLL Hijacking
```

The presence of only one condition does not establish a vulnerability.

---

## Writable Locations

A key question is whether an unprivileged user can write to a directory involved in library resolution.

Useful Windows permission tools include:

```powershell
Get-Acl "C:\Path\To\Application"
```

For a concise view:

```powershell
(Get-Acl "C:\Path\To\Application").Access |
    Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited
```

`icacls` can also be useful:

```cmd
icacls "C:\Path\To\Application"
```

Look for unexpected write permissions granted to principals such as:

```text
Users
Authenticated Users
Everyone
```

Interpret permissions carefully because inherited ACLs and explicit deny rules can affect the effective result.

---

## Test Actual Write Access

ACL inspection alone does not always establish effective write access.

For an authorised harmless test, attempt to create and remove a temporary text file:

```powershell
$Path = "C:\Path\To\Application"
$Test = Join-Path $Path "write-test-$PID.txt"

try {
    Set-Content -Path $Test -Value "test" -ErrorAction Stop
    Write-Host "[WRITABLE] $Path"
    Remove-Item $Test -Force -ErrorAction SilentlyContinue
}
catch {
    Write-Host "[NOT WRITABLE] $Path"
}
```

This validates write access without introducing executable content.

---

## Application Directories

Applications installed under locations such as:

```text
C:\Program Files
C:\Program Files (x86)
```

would normally be expected to have restrictive permissions for standard users.

Check:

```powershell
Get-Acl "C:\Program Files\Example"
```

A standard user being able to modify application binaries or DLLs in such a directory may indicate a broader permissions issue.

---

## PATH Environment Variable

Some DLL resolution scenarios can involve directories referenced through environment configuration.

Inspect the machine and user `PATH` values:

```powershell
[Environment]::GetEnvironmentVariable("Path", "Machine")
```

```powershell
[Environment]::GetEnvironmentVariable("Path", "User")
```

Current process value:

```powershell
$env:Path
```

Display one entry per line:

```powershell
$env:Path -split ';'
```

These directories can then be reviewed for unexpected user-writable locations.

Do not assume that the presence of a writable `PATH` directory automatically creates a DLL hijacking vulnerability. The application must actually resolve a relevant library through that location.

---

## Process Monitor

Sysinternals Process Monitor is one of the most useful tools for investigating DLL loading behaviour.

Useful event categories include:

```text
Process Name
Operation
Path
Result
```

During controlled testing, filters can be applied for:

```text
Process Name is application.exe
```

and operations such as:

```text
CreateFile
Load Image
```

A useful result to investigate is:

```text
NAME NOT FOUND
```

when an application searches multiple locations for the same DLL.

---

## Missing DLL Search

Conceptually, Process Monitor may show:

```text
application.exe -> C:\Application\example.dll -> NAME NOT FOUND
application.exe -> C:\Windows\System32\example.dll -> NAME NOT FOUND
application.exe -> C:\OtherPath\example.dll -> SUCCESS
```

This reveals the actual filesystem locations considered by the process.

The important questions then become:

1. Is the requested DLL legitimate?
2. Is the application actually attempting to load it?
3. Is any earlier search location writable?
4. What privilege level does the application use?
5. Can the condition be reproduced reliably?

---

## Procmon Filtering Workflow

A practical analysis workflow is:

```text
Start Process Monitor
        |
        v
Clear Existing Events
        |
        v
Apply Process Filter
        |
        v
Start Target Application
        |
        v
Capture DLL/File Activity
        |
        v
Stop Capture
        |
        v
Review NAME NOT FOUND
        |
        v
Review Load Image Events
```

This is generally more reliable than guessing which DLLs an application might attempt to load.

---

## Loaded Modules

PowerShell can display modules loaded into processes where access permits.

For example:

```powershell
Get-Process -Name notepad |
    Select-Object -ExpandProperty Modules |
    Select-Object ModuleName, FileName
```

For the current PowerShell process:

```powershell
(Get-Process -Id $PID).Modules |
    Select-Object ModuleName, FileName
```

This can help confirm the actual location from which a DLL was loaded.

Permissions and process protection may prevent module enumeration for some processes.

---

## Process Architecture

Architecture matters when analysing DLL loading.

Common architectures include:

```text
x86
x64
ARM64
```

A 64-bit process normally requires compatible 64-bit native libraries, while a 32-bit process requires compatible 32-bit libraries.

Architecture mismatches can result in load failures and should not be mistaken for successful security-control intervention.

---

## Inspecting PE Files

On Linux, the `file` command provides a quick format check:

```bash
file application.exe
```

```bash
file example.dll
```

For additional PE information:

```bash
x86_64-w64-mingw32-objdump -f example.dll
```

Imported libraries can be inspected with:

```bash
x86_64-w64-mingw32-objdump -p application.exe | less
```

Search the output for DLL names:

```bash
x86_64-w64-mingw32-objdump -p application.exe |
    grep -i 'DLL Name'
```

This is useful for static analysis, but runtime behaviour should still be verified.

---

## Static vs Runtime Analysis

Static inspection may reveal imported DLLs.

Runtime analysis reveals what actually happens when the application executes.

Use both where appropriate:

```text
Static Analysis
    |
    +---- PE imports
    +---- Strings
    +---- Application files
    |
    v
Runtime Analysis
    |
    +---- Procmon
    +---- Loaded modules
    +---- Filesystem activity
```

Delay-loaded or dynamically loaded libraries may not be obvious from a basic import-table review.

---

## DLL Exports

DLLs can expose exported functions.

On Linux:

```bash
x86_64-w64-mingw32-objdump -p example.dll |
    less
```

On Windows, development and analysis tools can also inspect exports.

Exports matter because some applications expect specific functions to exist in the loaded library.

A DLL merely being found does not guarantee that the application will continue operating correctly.

---

## Safe Validation

The preferred validation approach is to prove the insecure search condition without introducing unnecessary payload behaviour.

Evidence can include:

```text
Application requests DLL by name
        |
        v
Writable directory is searched
        |
        v
Controlled harmless marker DLL is observed loading
        |
        v
No additional action performed
```

Where executable validation is not necessary, combine:

- Procmon evidence;
- filesystem permissions;
- application privilege context;
- search-order analysis.

This can often establish the issue without executing arbitrary commands.

---

## Marker-Based Validation

A laboratory DLL can be designed to create only a harmless observable marker when loaded.

Examples of suitable markers include:

```text
Debugger output
A local test log entry
A temporary marker file
A laboratory-only message
```

Avoid adding:

- command execution;
- network callbacks;
- persistence;
- credential access;
- unrelated system modifications.

The objective is to establish that the library was loaded, not to turn the validation artifact into a general-purpose payload.

---

## Privilege Context

The impact of DLL hijacking depends heavily on the privilege level of the affected application.

Determine which account owns a process:

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId = 1234" |
    Invoke-CimMethod -MethodName GetOwner
```

Basic process details:

```powershell
Get-Process -Id 1234 |
    Select-Object Id, ProcessName, Path
```

Relevant contexts may include:

```text
Standard user
Elevated administrator
LocalSystem
Service account
Application-specific service identity
```

A hijacking condition affecting a standard-user application usually has a different impact from one affecting a privileged service.

---

## Services

Services deserve particular attention because some run with elevated privileges.

Enumerate services:

```powershell
Get-CimInstance Win32_Service |
    Select-Object Name, StartName, State, PathName
```

For a specific service:

```powershell
Get-CimInstance Win32_Service -Filter "Name='ExampleService'" |
    Select-Object Name, StartName, State, PathName
```

Review:

- service identity;
- executable path;
- application directory permissions;
- related DLL search behaviour.

Do not restart production services merely to test a suspected hijacking condition unless explicitly authorised.

---

## Scheduled Applications

Applications started by scheduled tasks can also have different privilege contexts.

Basic scheduled-task enumeration:

```powershell
Get-ScheduledTask |
    Select-Object TaskName, TaskPath, State
```

The presence of a scheduled task alone does not establish a DLL hijacking issue.

The associated executable and DLL-loading behaviour still need to be analysed.

---

## Application Control

DLL hijacking interacts with application-control technologies.

Relevant Windows controls include:

- AppLocker;
- Windows Defender Application Control;
- application allowlisting;
- code-signing policies.

A writable directory does not automatically mean an arbitrary DLL can be loaded.

For example:

```text
Writable Directory       YES
Application Searches It  YES
DLL Created              YES
DLL Load                 BLOCKED
```

This demonstrates that application control provides an additional security boundary.

---

## AppLocker DLL Rules

AppLocker supports a DLL rule collection.

Inspect the effective policy:

```powershell
Get-AppLockerPolicy -Effective
```

XML output can provide additional detail:

```powershell
Get-AppLockerPolicy -Effective -Xml
```

DLL enforcement should be considered separately from executable and script enforcement.

An environment may enforce executable rules while leaving DLL rules unconfigured.

---

## WDAC

Windows Defender Application Control can enforce policies affecting executable code and libraries.

The exact behaviour depends on the deployed policy.

Useful evidence includes:

- Code Integrity event logs;
- policy configuration;
- blocked-load events;
- EDR telemetry.

Do not infer WDAC behaviour solely from whether an application starts successfully.

---

## Detection Opportunities

DLL hijacking can generate several useful defensive signals.

Potential telemetry includes:

```text
DLL creation
DLL modification
Image load
Unexpected module path
Unsigned module
User-writable module path
Application crash
Application-control event
Process execution
```

The most useful signal is often the relationship between the process and the library path.

---

## Suspicious Module Locations

Defenders may want to investigate sensitive applications loading DLLs from locations such as:

```text
User profile directories
Downloads
Temporary directories
Unexpected ProgramData subdirectories
Writable application directories
Network shares
```

These locations are not automatically malicious.

The expected behaviour of the application must be considered.

---

## Sysmon

Where configured, Sysmon can provide image-load telemetry.

Relevant event categories may include:

```text
Process creation
Image load
File creation
File creation time
```

Image-load monitoring can produce substantial event volume and therefore requires careful configuration.

The availability of an event should always be verified against the organisation's Sysmon configuration.

---

## Event Correlation

A useful detection pattern can be:

```text
New DLL Created
        +
DLL Located in User-Writable Directory
        +
Privileged Application Starts
        +
Application Loads DLL
```

Correlation generally provides stronger context than treating each event independently.

---

## Detection Validation

During a purple team exercise, useful questions include:

- Was the DLL creation recorded?
- Was its hash captured?
- Was the path captured?
- Was the loading process identified?
- Was the parent process available?
- Was the signer recorded?
- Was the load prevented?
- Did EDR generate a detection?
- Did the SIEM correlate the events?
- Did the SOC investigate the correct process?
- Was the affected privilege context identified?

These questions evaluate visibility rather than merely whether the test succeeded.

---

## Investigation Workflow

A practical investigation process is:

```text
Identify Application
        |
        v
Observe DLL Requests
        |
        v
Identify Missing / Loaded DLL
        |
        v
Determine Search Locations
        |
        v
Check Directory Permissions
        |
        v
Determine Process Privileges
        |
        v
Review Application Control
        |
        v
Validate Safely
        |
        v
Review Detection
```

This reduces false positives.

---

## False Positives

Not every `NAME NOT FOUND` DLL request is exploitable.

Common reasons include:

- optional application functionality;
- language resources;
- architecture-specific probing;
- fallback behaviour;
- libraries protected through KnownDLLs;
- directories that are not writable;
- application control preventing untrusted libraries;
- DLL name being requested only under conditions not reachable by the tester.

A finding should therefore demonstrate the complete security-relevant condition.

---

## Evidence Collection

For each suspected DLL hijacking issue, record:

```text
Application:
Application path:
Application version:
Process architecture:
Process identity:
Process privilege:
Requested DLL:
Search location:
Writable by:
Observed with:
DLL loaded:
Loaded path:
Application-control result:
Endpoint detection:
Reproduction conditions:
Cleanup status:
```

Where available, also record SHA-256 hashes:

```powershell
Get-FileHash -Algorithm SHA256 "C:\Path\To\Application.exe"
```

---

## Severity Considerations

Severity depends on the actual impact.

Consider:

- Who can write to the relevant location?
- Which process loads the DLL?
- What privilege does that process have?
- Is user interaction required?
- Does the condition occur automatically?
- Is application control present?
- Can the issue cross a privilege boundary?
- Is the application commonly executed?
- Is reliable reproduction possible?

For example:

```text
Standard user -> standard user
```

generally has different impact from:

```text
Standard user -> privileged service
```

Do not assign severity based solely on the phrase "DLL hijacking."

---

## Remediation

The appropriate remediation depends on the root cause.

### Use Explicit Paths

Applications should load libraries from controlled locations where possible.

Avoid relying unnecessarily on ambiguous search paths.

### Restrict Directory Permissions

Standard users should not normally have modification rights to privileged application directories.

Review:

```powershell
Get-Acl "C:\Program Files\Example"
```

Remove unnecessary write permissions.

### Secure Application Installation

Ensure installers create application directories with appropriate ACLs.

### Application Control

Consider application-control technologies such as:

- Windows Defender Application Control;
- AppLocker;
- code-signing requirements.

These provide additional protection when filesystem controls alone are insufficient.

### Monitor Sensitive Applications

Monitor privileged or security-sensitive processes for unexpected DLL loads.

---

## Reporting

A DLL hijacking finding should clearly identify the vulnerable condition.

Avoid:

> DLL hijacking is possible.

Prefer:

> The application searches for a required DLL in a directory writable by standard users before resolving the legitimate library. This allows an unprivileged user to influence which library is loaded when the affected application starts.

Where a privilege boundary exists:

> Because the affected application executes with elevated privileges, successful exploitation of the insecure DLL search condition could result in code running within the application's elevated security context.

Where application control prevents the test:

> Although a user-writable directory was identified in the DLL search path, the tested replacement library was prevented from loading by application-control policy. No privilege escalation was demonstrated.

---

## Remediation Example

A concise recommendation could be:

> Restrict write permissions on application directories and ensure applications load required libraries from explicit, trusted locations. Where appropriate, enforce application-control policies to prevent unsigned or unauthorised DLLs from loading.

---

## DLL Hijacking Testing Checklist

### Application

- [ ] Identify application
- [ ] Record version
- [ ] Record executable path
- [ ] Determine architecture
- [ ] Determine privilege context

### DLL Behaviour

- [ ] Observe runtime DLL activity
- [ ] Identify missing DLL requests
- [ ] Identify loaded DLL paths
- [ ] Review KnownDLLs where relevant
- [ ] Review search behaviour

### Permissions

- [ ] Identify searched directories
- [ ] Review ACLs
- [ ] Test harmless write access where authorised
- [ ] Identify affected user/group
- [ ] Check inherited permissions

### Security Controls

- [ ] Review AppLocker
- [ ] Review WDAC
- [ ] Review endpoint protection
- [ ] Review EDR telemetry
- [ ] Review image-load telemetry

### Validation

- [ ] Prefer harmless validation
- [ ] Confirm actual DLL load
- [ ] Record exact loaded path
- [ ] Record application behaviour
- [ ] Avoid unnecessary system modification

### Reporting

- [ ] Document vulnerable application
- [ ] Document requested DLL
- [ ] Document writable path
- [ ] Document privilege context
- [ ] Document application-control result
- [ ] Document detection result
- [ ] Provide remediation
- [ ] Complete cleanup

---

## Related Material

- [Red Teaming Methodology](methodology.md)
- [Custom Tooling](custom-tooling.md)
- [Payload Delivery](payload-delivery.md)
- [Staged Payloads](staged-payloads.md)
- [Execution](execution.md)
- [Privilege Escalation](privilege-escalation.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Windows](../windows/index.md)

---

## References

- [Microsoft - Dynamic-Link Library Search Order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Dynamic-Link Libraries](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-libraries){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - LoadLibraryEx](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Application Control for Windows](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/){ target="_blank" rel="noopener noreferrer" }
- [Sysinternals - Process Monitor](https://learn.microsoft.com/en-us/sysinternals/downloads/procmon){ target="_blank" rel="noopener noreferrer" }
- [Sysinternals - Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Hijack Execution Flow: DLL](https://attack.mitre.org/techniques/T1574/001/){ target="_blank" rel="noopener noreferrer" }
