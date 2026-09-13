# Staged Payloads

Staged payloads separate delivery and execution into multiple components. Instead of transferring all required functionality in a single artifact, an initial component retrieves or receives additional content during a later stage.

This architecture is used by legitimate software installers, management systems, deployment frameworks, security testing tools, and command-and-control frameworks. During an authorised red team or purple team assessment, understanding staged execution is useful because each stage creates a different opportunity for prevention, detection, and investigation.

!!! warning "Authorised Use Only"
    Staged payload testing can involve executable content, network communication, memory allocation, and endpoint security controls. Only perform these tests where explicit authorisation has been obtained and the technique is permitted by the rules of engagement.

---

## Overview

A simplified staged architecture can be represented as:

```text
Initial Component
        |
        v
Establish Communication
        |
        v
Retrieve Additional Content
        |
        v
Validate / Process Content
        |
        v
Load or Execute Next Stage
        |
        v
Runtime Activity
```

A non-staged architecture instead resembles:

```text
Complete Artifact
        |
        v
Execution
        |
        v
Runtime Activity
```

The distinction matters because staged and non-staged approaches produce different:

- network behaviour;
- filesystem artifacts;
- process behaviour;
- memory activity;
- endpoint telemetry;
- detection opportunities.

---

## Terminology

Terminology differs between frameworks, but several terms are commonly encountered.

### Stage

A component delivered after the initial execution step.

### Stager

A small initial component responsible for obtaining or preparing another component.

### Payload

A broad term for the content ultimately processed or executed.

### Stage 0

Sometimes used to describe the initial execution or bootstrap component.

### Stage 1

The next component obtained by the initial loader or stager.

### Loader

A component responsible for preparing another artifact for execution.

### Bootstrapper

A small program that establishes the conditions required for a larger component to operate.

The exact terminology depends on the software being assessed.

---

## Why Staging Exists

Staged architectures can provide several engineering advantages.

Examples include:

- reducing the size of the initial component;
- separating delivery from functionality;
- dynamically selecting later components;
- updating functionality independently;
- retrieving configuration at runtime;
- supporting modular architectures.

These characteristics are not inherently malicious.

Many legitimate applications use comparable bootstrap and update mechanisms.

From a security-testing perspective, however, staging is important because it creates additional security boundaries.

---

## Staged vs Stageless

The fundamental distinction is where the functionality resides.

### Staged

```text
Small Initial Component
        |
        v
Network / IPC / File Retrieval
        |
        v
Additional Component
        |
        v
Execution
```

### Stageless

```text
Complete Component
        |
        v
Execution
```

A staged approach introduces an additional retrieval or transfer event.

A stageless approach generally places more functionality in the initial artifact.

---

## Comparison

| Characteristic | Staged | Stageless |
|---|---|---|
| Initial artifact | Usually smaller | Usually larger |
| Additional retrieval | Typically required | Usually not required |
| Network dependency | Often present | Depends on functionality |
| Delivery stages | Multiple | Usually fewer |
| Detection opportunities | Distributed across stages | Concentrated around initial artifact |
| Troubleshooting | More components | Fewer components |
| Offline execution | May be limited | Potentially easier |
| Architecture complexity | Higher | Lower |

Neither design should automatically be considered more or less detectable.

The surrounding implementation and environment determine the actual security outcome.

---

## Security Boundaries

A staged workflow creates multiple points where controls can intervene.

```text
Initial Delivery
      |
      +---- Web / Email / File Controls
      |
      v
Initial Execution
      |
      +---- Application Control
      +---- Endpoint Protection
      |
      v
Network Retrieval
      |
      +---- Firewall
      +---- Proxy
      +---- DNS
      +---- NDR
      |
      v
Content Processing
      |
      +---- Endpoint Protection
      +---- Memory Monitoring
      |
      v
Runtime Behaviour
      |
      +---- EDR
      +---- Event Logging
      +---- SIEM
```

A good assessment records which layer prevented or detected the activity.

---

## Delivery Is Not Execution

A staged component may successfully reach an endpoint but fail before retrieving another stage.

For example:

```text
Initial file delivered      ALLOWED
Initial process execution   ALLOWED
Outbound connection         BLOCKED
Stage retrieval             NOT REACHED
```

Alternatively:

```text
Initial file delivered      ALLOWED
Initial process execution   BLOCKED
Outbound connection         NOT REACHED
Stage retrieval             NOT REACHED
```

These represent different security outcomes.

Do not report them as the same result.

---

## Stage Retrieval

Additional content may be obtained through different mechanisms depending on the application or framework.

Conceptually these can include:

- HTTP;
- HTTPS;
- internal file services;
- application APIs;
- local files;
- inter-process communication;
- software distribution infrastructure.

Each mechanism exposes different telemetry.

For example, network-based retrieval may generate:

```text
DNS query
TCP connection
TLS handshake
HTTP request
Proxy event
Firewall event
Network detection event
```

File-based staging may instead create:

```text
File creation
File open
File read
Security metadata
Endpoint scanning
```

---

## Network Dependencies

A staged architecture often depends on network availability.

Before troubleshooting the application itself, validate basic connectivity independently.

Windows:

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 443
```

Linux:

```bash
nc -vz 192.0.2.10 443
```

DNS can be checked separately:

```powershell
Resolve-DnsName example.com
```

or:

```bash
dig example.com
```

This helps distinguish application failures from network-control failures.

---

## Proxy Considerations

Enterprise environments may require traffic to traverse a proxy.

Windows:

```powershell
netsh winhttp show proxy
```

Environment variables:

```powershell
Get-ChildItem Env: | Where-Object Name -Match 'proxy'
```

A staged application may behave differently depending on whether it uses:

- WinHTTP;
- WinINet;
- browser configuration;
- environment variables;
- a custom networking implementation.

This can explain why one application reaches a destination while another cannot.

---

## TLS Considerations

HTTPS staging introduces additional dependencies.

These may include:

- certificate validation;
- hostname validation;
- TLS versions;
- enterprise TLS inspection;
- proxy certificates;
- certificate trust stores.

Inspect a TLS endpoint:

```bash
openssl s_client -connect example.com:443 -servername example.com
```

A certificate issued by an organisational certificate authority may indicate TLS inspection.

---

## File-Based Staging

Some architectures store an additional component on disk before processing it.

A simplified workflow is:

```text
Initial Component
        |
        v
Retrieve File
        |
        v
Write File
        |
        v
Read / Validate
        |
        v
Load
```

This creates opportunities for:

- antivirus scanning;
- file reputation;
- Mark of the Web;
- application control;
- filesystem auditing;
- EDR file telemetry.

Record the exact point where a control intervenes.

---

## Memory-Based Staging

Some software processes subsequent components directly in memory rather than creating a conventional executable file.

From a defensive perspective, useful observations may include:

- memory allocation;
- changes to memory permissions;
- module loading;
- thread creation;
- process access;
- unusual call stacks;
- executable private memory;
- endpoint detections.

The implementation details vary considerably between products.

For an assessment, focus on observable behaviour and defensive visibility rather than assuming a particular implementation.

---

## Process Relationships

Staged execution may create relationships between multiple processes.

Record:

```text
Parent process
        |
        v
Initial process
        |
        v
Child process
```

On Windows, basic process information can be inspected with:

```powershell
Get-CimInstance Win32_Process |
    Select-Object ProcessId, ParentProcessId, Name
```

For a specific process:

```powershell
Get-CimInstance Win32_Process -Filter "ProcessId = 1234" |
    Select-Object ProcessId, ParentProcessId, Name, ExecutablePath
```

Process relationships can provide valuable context during detection validation.

---

## Network Connections

When a staged test is performed in an authorised environment, correlate process activity with network connections.

PowerShell:

```powershell
Get-NetTCPConnection |
    Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess
```

For a specific process ID:

```powershell
Get-NetTCPConnection -OwningProcess 1234
```

Then inspect the process:

```powershell
Get-Process -Id 1234
```

This can help establish:

```text
Process
    |
    v
Network Connection
    |
    v
Remote Destination
```

---

## File Integrity

If a stage is stored on disk, record its hash.

Windows:

```powershell
Get-FileHash -Algorithm SHA256 .\artifact.bin
```

Linux:

```bash
sha256sum artifact.bin
```

Hashes help correlate:

- endpoint telemetry;
- SIEM events;
- security product detections;
- assessment evidence.

---

## Artifact Identification

Do not rely exclusively on file extensions.

Linux:

```bash
file artifact.bin
```

For PE files:

```bash
file artifact.dll
```

For COFF objects:

```bash
x86_64-w64-mingw32-objdump -f artifact.o
```

For a short binary artifact:

```bash
xxd -g1 artifact.bin | head
```

These checks are useful when troubleshooting multi-stage build pipelines.

---

## Build Pipelines

A staged architecture may involve several generated artifacts.

For example:

```text
Source
  |
  v
Compiler
  |
  v
Object
  |
  v
Loader / Wrapper
  |
  v
Intermediate Artifact
  |
  v
Delivery Component
```

When troubleshooting, validate each artifact independently rather than jumping directly to the final stage.

Useful checks include:

```bash
test -s artifact.bin && echo "PRESENT" || echo "MISSING"
```

```bash
stat artifact.bin
```

```bash
file artifact.bin
```

```bash
sha256sum artifact.bin
```

This makes it easier to identify the first missing or malformed component.

---

## Dependency Chains

A missing upstream artifact causes downstream failures.

For example:

```text
Artifact A
    |
    v
Artifact B
    |
    v
Artifact C
```

If `Artifact A` was never generated, attempting to build `Artifact C` will usually produce misleading downstream errors.

Troubleshoot from the beginning of the chain:

```text
1. Does the input exist?
2. Is the input non-empty?
3. Is the format correct?
4. Is the architecture correct?
5. Did the transformation succeed?
6. Does the expected output exist?
```

This approach is particularly useful with custom red team build systems.

---

## Architecture Compatibility

Different stages must generally agree on architecture.

Common combinations include:

```text
x86    -> x86
x64    -> x64
ARM64  -> ARM64
```

Inspect a Windows artifact:

```bash
file artifact.dll
```

Inspect a COFF object:

```bash
x86_64-w64-mingw32-objdump -f artifact.o
```

Architecture mismatches can cause:

- loading failures;
- invalid image errors;
- crashes;
- unexpected build failures.

---

## Runtime Dependencies

A staged component may depend on libraries or runtime components that are not present on the destination system.

Examples include:

- .NET runtime;
- Visual C++ runtime;
- Java;
- native DLLs;
- framework-specific libraries.

Document runtime requirements during development.

A successful build on Kali or a development workstation does not guarantee that the resulting component can operate on another system.

---

## Application Control

Application control can affect different stages independently.

For example:

```text
Initial executable        ALLOWED
Downloaded DLL            BLOCKED
Script                    BLOCKED
Child process             ALLOWED
```

Relevant technologies include:

- AppLocker;
- Windows Defender Application Control;
- Software Restriction Policies;
- endpoint application allowlisting.

Evaluate each artifact separately.

---

## Endpoint Protection

Endpoint protection may react at different points.

Possible outcomes include:

```text
Initial artifact blocked
Initial artifact allowed
Network retrieval blocked
Retrieved content quarantined
Runtime behaviour blocked
Runtime behaviour detected
No prevention observed
No alert observed
```

Record the point of intervention.

This provides considerably more useful information than simply stating that a staged test "worked" or "failed."

---

## Detection Engineering

Staged architectures create useful opportunities for detection engineering because several independent telemetry sources can be correlated.

Potential sources include:

- process creation;
- DNS;
- network connections;
- proxy requests;
- file creation;
- module loads;
- endpoint detections;
- memory telemetry;
- SIEM correlation.

A useful detection model is:

```text
Unusual Initial Process
        +
New External Connection
        +
Content Retrieval
        +
Suspicious Runtime Behaviour
```

Individual events may be low-confidence.

Correlation can substantially increase detection quality.

---

## Useful Windows Telemetry

Depending on organisational configuration, useful telemetry may include:

```text
Windows Security logs
PowerShell logs
Microsoft Defender events
Sysmon
AppLocker logs
WDAC events
EDR telemetry
Firewall logs
DNS logs
Proxy logs
```

The availability of these sources should be confirmed before an exercise.

---

## Sysmon Considerations

Where Sysmon is deployed, potentially relevant event categories include:

```text
Process creation
Network connection
Image load
File creation
Process access
DNS query
```

The exact event availability depends on the Sysmon configuration.

Do not assume all event types are enabled.

---

## Timeline Analysis

Staged activity is easier to understand when events are placed on a timeline.

Example:

```text
10:00:01  Initial file created
10:00:05  Initial process started
10:00:06  DNS query observed
10:00:06  TCP connection established
10:00:07  Additional content retrieved
10:00:08  Endpoint event generated
10:00:10  SOC alert created
```

This allows the red and blue teams to compare:

- attacker activity;
- endpoint telemetry;
- network telemetry;
- alert generation;
- analyst response.

---

## Purple Team Validation

A staged workflow is well suited to purple team exercises because each phase can be evaluated independently.

For example:

### Phase 1 - Initial Delivery

Question:

> Can the initial artifact reach the endpoint?

### Phase 2 - Initial Execution

Question:

> Do endpoint controls permit the initial component to start?

### Phase 3 - Network Activity

Question:

> Is subsequent network communication visible and controlled?

### Phase 4 - Additional Content

Question:

> Is retrieval or processing of additional content detected?

### Phase 5 - Runtime Behaviour

Question:

> Are subsequent behaviours detected and correlated?

This produces more actionable results than testing the entire chain as a single binary outcome.

---

## Failure Analysis

When a staged test fails, identify the exact stage.

Use a table such as:

| Stage | Result | Evidence |
|---|---|---|
| Initial delivery | Pass | File present |
| Initial execution | Pass | Process created |
| DNS resolution | Pass | Query observed |
| TCP connection | Fail | Connection blocked |
| Stage retrieval | Not reached | Network unavailable |
| Runtime | Not reached | Stage unavailable |

This prevents downstream stages from being incorrectly classified as failures.

---

## Common Problems

### Initial Component Runs but Nothing Happens

Check:

- network connectivity;
- DNS;
- proxy settings;
- TLS;
- application logs;
- endpoint security events.

Do not immediately assume the initial component is defective.

### Additional Artifact Is Missing

Work backwards through the build or retrieval chain.

Check:

```bash
test -s expected-file.bin && echo "PRESENT" || echo "MISSING"
```

Then identify which preceding operation was responsible for creating it.

### Architecture Mismatch

Verify each component:

```bash
file artifact.dll
```

and:

```bash
x86_64-w64-mingw32-objdump -f artifact.o
```

### Network Connection Is Blocked

Validate independently:

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 443
```

Then investigate:

- firewall;
- proxy;
- routing;
- DNS;
- network security controls.

### Artifact Is Quarantined

Review endpoint protection logs before recreating or retransferring the artifact.

The security control may be functioning as intended.

---

## Evidence Collection

For each staged test, record:

```text
Test identifier:
Timestamp:
Initial artifact:
Initial artifact SHA-256:
Architecture:
Source system:
Destination system:
Initial execution result:
Network destination:
Protocol:
Retrieved artifact:
Retrieved artifact SHA-256:
Endpoint response:
Network response:
Detection response:
SOC response:
Cleanup status:
```

This provides enough context to reconstruct the test later.

---

## Reporting

Avoid describing a multi-stage test only as:

> The payload failed.

Instead identify the security boundary.

For example:

> The initial test component executed successfully, but the subsequent outbound connection was prevented by network controls. As a result, the next stage was not retrieved.

Or:

> The initial component and subsequent network retrieval were permitted. Endpoint monitoring generated telemetry when the additional component was processed.

This makes the result useful to both technical and management audiences.

---

## Cleanup

Staged testing may leave artifacts at several locations.

Potential cleanup items include:

- initial files;
- downloaded components;
- temporary files;
- logs;
- test directories;
- hosted content;
- temporary network services.

Keep a record of created artifacts throughout the test rather than attempting to reconstruct them afterwards.

---

## Staged Payload Testing Checklist

### Preparation

- [ ] Confirm authorisation
- [ ] Confirm permitted technique
- [ ] Identify all expected stages
- [ ] Identify required network paths
- [ ] Confirm architecture
- [ ] Record initial artifact hashes
- [ ] Define cleanup procedure

### Initial Stage

- [ ] Confirm delivery
- [ ] Confirm file integrity
- [ ] Inspect security metadata
- [ ] Record execution result
- [ ] Review endpoint telemetry

### Retrieval

- [ ] Confirm DNS
- [ ] Confirm TCP connectivity
- [ ] Confirm proxy requirements
- [ ] Confirm TLS behaviour
- [ ] Record network telemetry
- [ ] Record retrieval result

### Additional Stage

- [ ] Confirm artifact presence
- [ ] Record size
- [ ] Record SHA-256
- [ ] Confirm architecture
- [ ] Review endpoint response
- [ ] Review application-control response

### Detection

- [ ] Review endpoint events
- [ ] Review DNS logs
- [ ] Review firewall logs
- [ ] Review proxy logs
- [ ] Review EDR telemetry
- [ ] Review SIEM correlation
- [ ] Review SOC response

### Completion

- [ ] Build timeline
- [ ] Record evidence
- [ ] Document exact failure point
- [ ] Remove test artifacts
- [ ] Confirm cleanup

---

## Related Material

- [Red Teaming Methodology](methodology.md)
- [Infrastructure](infrastructure.md)
- [OPSEC](opsec.md)
- [Initial Access](initial-access.md)
- [Payload Delivery](payload-delivery.md)
- [Execution](execution.md)
- [Command and Control](command-and-control.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Cleanup](cleanup.md)

---

## References

- [MITRE ATT&CK - Command and Control](https://attack.mitre.org/tactics/TA0011/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Ingress Tool Transfer](https://attack.mitre.org/techniques/T1105/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Execution](https://attack.mitre.org/tactics/TA0002/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Application Control for Windows](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/){ target="_blank" rel="noopener noreferrer" }
- [Sysinternals - Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon){ target="_blank" rel="noopener noreferrer" }
