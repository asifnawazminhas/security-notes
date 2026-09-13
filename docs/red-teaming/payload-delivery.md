# Payload Delivery

Payload delivery is the process of transferring authorised test content, tooling, or execution material to a target environment during a red team, penetration test, adversary emulation exercise, or controlled security assessment.

Delivery is not limited to transferring an executable. Depending on the engagement, the delivered content may be a document, script, archive, library, configuration file, installer, test artifact, or other controlled resource.

The objective is to understand how content reaches an environment, which security controls inspect it, what telemetry is generated, and whether defensive controls prevent or detect the activity.

!!! warning "Authorised Use Only"
    Payload delivery techniques can affect endpoint, email, browser, network, and application security controls. Only perform delivery testing where explicit authorisation has been obtained and the technique is permitted by the rules of engagement.

---

## Overview

A simplified delivery workflow can be represented as:

```text
Payload Preparation
        |
        v
Delivery Channel
        |
        v
Network / Application Controls
        |
        v
Target System
        |
        v
Endpoint Controls
        |
        v
Execution or Validation
        |
        v
Detection Review
        |
        v
Cleanup
```

Each stage can introduce a different security control.

For example, an HTTPS download may involve:

- DNS filtering;
- web proxies;
- TLS inspection;
- URL filtering;
- reputation services;
- browser controls;
- Mark of the Web;
- Microsoft Defender;
- application control;
- EDR;
- behavioural monitoring.

Testing should therefore distinguish **delivery success** from **execution success**.

---

## Delivery vs Execution

These are separate security boundaries.

A file being successfully downloaded does not mean it can be executed.

Likewise, a file being blocked during delivery does not necessarily mean application control would have blocked execution.

Track the stages separately:

```text
Transfer allowed?
        |
        v
File created?
        |
        v
Security metadata applied?
        |
        v
Execution permitted?
        |
        v
Behaviour permitted?
        |
        v
Detection generated?
```

This distinction is particularly important when evaluating layered security controls.

---

## Delivery Objectives

Payload delivery testing can answer questions such as:

- Can files be transferred into the environment?
- Which protocols are permitted?
- Which file types are blocked?
- Are downloads inspected?
- Is Mark of the Web applied?
- Are archives inspected?
- Are scripts treated differently from executables?
- Does application control prevent execution?
- Does endpoint protection quarantine the artifact?
- Does EDR generate telemetry?
- Are network security controls alerted?
- Does the SOC receive a meaningful detection?

The objective should be defined before selecting a delivery technique.

---

## Delivery Channels

Common delivery channels include:

| Channel | Examples |
|---|---|
| Web | HTTP and HTTPS downloads |
| Email | Attachments and links |
| File shares | SMB and mapped drives |
| Remote administration | Approved administrative transfer mechanisms |
| Cloud storage | Organisational or approved external storage |
| Source repositories | Git-based workflows |
| Application upload | Authorised application functionality |
| Removable media | Controlled physical assessments |
| Package systems | Approved software distribution mechanisms |

The permitted channels depend on the engagement scope.

---

## HTTP and HTTPS

Web delivery is commonly used in controlled laboratories because it is simple to observe and produces useful network telemetry.

A harmless file can be hosted locally:

```bash
python3 -m http.server 8000
```

Verify that the server is listening:

```bash
ss -lntp | grep ':8000'
```

From another authorised system:

```bash
curl -I http://192.0.2.10:8000/
```

Download a harmless test file:

```bash
curl -o test.txt http://192.0.2.10:8000/test.txt
```

This can validate:

- routing;
- firewall policy;
- proxy behaviour;
- HTTP access;
- file transfer;
- logging.

Use documentation or harmless test files before introducing executable content.

---

## HTTPS Validation

HTTPS adds TLS and certificate handling to the delivery path.

Useful checks include:

```bash
curl -I https://example.com/
```

Inspect TLS:

```bash
openssl s_client -connect example.com:443 -servername example.com
```

Review:

- certificate chain;
- TLS version;
- proxy interception;
- connection failures;
- hostname validation.

In corporate environments, TLS inspection may result in certificates being issued by an organisational certificate authority.

---

## PowerShell Web Requests

On authorised Windows systems, PowerShell can be used to validate whether web content is reachable.

For example:

```powershell
Invoke-WebRequest -Uri "https://example.com/" -UseBasicParsing
```

Inspect the response without executing downloaded content:

```powershell
$response = Invoke-WebRequest -Uri "https://example.com/" -UseBasicParsing

$response.StatusCode
$response.Headers
```

This is useful for determining whether the PowerShell process itself has outbound web access.

---

## Browser Delivery

Browsers introduce additional security controls that may not apply to command-line downloads.

Potential controls include:

- Safe Browsing;
- SmartScreen;
- download reputation;
- file-type restrictions;
- browser policies;
- enterprise URL filtering;
- Mark of the Web.

Therefore, browser-based and command-line delivery should not automatically be considered equivalent.

Record which application performed the transfer.

---

## Mark of the Web

Windows can associate downloaded content with an Internet security zone using the `Zone.Identifier` alternate data stream.

Inspect a downloaded file:

```powershell
Get-Item -Path ".\test.txt" -Stream *
```

Inspect the zone information:

```powershell
Get-Content -Path ".\test.txt" -Stream Zone.Identifier
```

Typical content may resemble:

```text
[ZoneTransfer]
ZoneId=3
```

`ZoneId=3` commonly represents the Internet zone.

The presence of Mark of the Web can influence:

- Microsoft Office;
- SmartScreen;
- PowerShell;
- archive handling;
- script execution;
- application reputation;
- other Windows security decisions.

---

## Compare Delivery Methods

When permitted, compare how the same harmless artifact behaves when transferred through different mechanisms.

For example:

```text
Browser download
PowerShell web request
curl
File share
Archive extraction
Local copy
```

Then compare:

```powershell
Get-Item -Path ".\test.txt" -Stream *
```

This can reveal differences in security metadata.

---

## File Integrity

Record a hash before and after transfer to confirm that the file was not modified.

Linux:

```bash
sha256sum test.txt
```

Windows:

```powershell
Get-FileHash -Algorithm SHA256 .\test.txt
```

The hashes should match when the transfer is lossless.

This is also useful for documenting exactly which artifact was tested.

---

## File Type Identification

Do not rely exclusively on the filename extension.

On Linux:

```bash
file artifact.bin
```

For Windows PE files:

```bash
file artifact.exe
```

Additional inspection can be performed with:

```bash
x86_64-w64-mingw32-objdump -f artifact.exe
```

This helps identify architecture and file format before controlled testing.

---

## Archives

Archives are frequently used for legitimate software distribution and therefore represent another useful security-control boundary.

Common formats include:

```text
.zip
.7z
.tar
.tar.gz
```

A controlled test may compare:

```text
Direct file transfer
        vs
Archive transfer
        vs
Archive extraction
```

Record whether:

- the archive itself is blocked;
- contents are inspected;
- extracted files inherit security metadata;
- endpoint protection reacts during extraction.

Do not assume that archive handling behaves identically across browsers, utilities, and operating systems.

---

## SMB and File Shares

In internal assessments, authorised file shares may provide another delivery path.

Enumerate an approved share:

```powershell
Get-ChildItem "\\server\share"
```

For a harmless file:

```powershell
Copy-Item "\\server\share\test.txt" ".\test.txt"
```

Record:

- authentication requirements;
- share permissions;
- NTFS permissions;
- network controls;
- security metadata;
- endpoint telemetry.

Do not write to shares unless the location is explicitly authorised for testing.

---

## Local File Copy

A local copy provides a useful baseline because it removes network delivery controls from the test.

PowerShell:

```powershell
Copy-Item "C:\Source\test.txt" "C:\Temp\test.txt"
```

Compare this with an Internet or network-delivered copy.

This can help determine whether observed behaviour is caused by:

- delivery metadata;
- network inspection;
- endpoint inspection;
- application control.

---

## Temporary Locations

Delivery testing frequently involves writable locations.

Examples include:

```text
%TEMP%
%LOCALAPPDATA%
C:\Users\<user>\Downloads
C:\ProgramData
```

A writable directory does not automatically imply that executable content can run from it.

Treat these as separate tests:

```text
Can write?
Can create file?
Can execute?
Can load library?
Can execute script?
```

This distinction is particularly relevant when AppLocker or Windows Defender Application Control is deployed.

---

## Application Control

Application control may permit a file to be downloaded while preventing it from running.

Relevant Windows technologies include:

- AppLocker;
- Windows Defender Application Control;
- Software Restriction Policies;
- application-specific allowlisting.

When testing delivery, record:

```text
Delivery: ALLOWED / BLOCKED
Execution: ALLOWED / BLOCKED / NOT TESTED
```

This prevents an allowed download from being incorrectly reported as an execution-control failure.

---

## Endpoint Protection

Endpoint security products may inspect content at several points:

```text
Network transfer
        |
        v
File creation
        |
        v
File open
        |
        v
Process creation
        |
        v
Runtime behaviour
```

A file may therefore transfer successfully but be quarantined later.

Record when the control reacted.

Useful categories include:

```text
Blocked during transfer
Quarantined after creation
Blocked on access
Blocked on execution
Detected after execution
No prevention
No alert observed
```

---

## Network Controls

Delivery can interact with:

- firewalls;
- secure web gateways;
- DNS filtering;
- proxies;
- TLS inspection;
- IDS/IPS;
- network detection and response;
- egress filtering.

Before investigating a tooling problem, validate the underlying connection.

Windows:

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 443
```

Linux:

```bash
nc -vz 192.0.2.10 443
```

This helps distinguish network restrictions from application-level failures.

---

## Proxy Awareness

Corporate systems may require outbound traffic to traverse a proxy.

On Windows:

```powershell
netsh winhttp show proxy
```

Environment variables may also be relevant:

```powershell
Get-ChildItem Env: | Where-Object Name -Match 'proxy'
```

Different applications may use different proxy configurations.

For example:

```text
Browser
PowerShell
curl
WinHTTP application
Custom application
```

may not follow identical network paths.

---

## DNS Validation

Before troubleshooting HTTP or HTTPS, verify DNS separately.

Windows:

```powershell
Resolve-DnsName example.com
```

Linux:

```bash
dig example.com
```

or:

```bash
host example.com
```

This helps isolate DNS filtering and resolution problems from TCP or application-layer failures.

---

## Delivery Test Matrix

A simple matrix makes results easier to compare.

| Delivery Method | File Created | Security Metadata | Execution | Detection |
|---|---|---|---|---|
| Browser | Yes/No | Present/Absent | Not Tested | Yes/No |
| PowerShell | Yes/No | Present/Absent | Not Tested | Yes/No |
| curl | Yes/No | Present/Absent | Not Tested | Yes/No |
| SMB | Yes/No | Present/Absent | Not Tested | Yes/No |
| Local Copy | Yes/No | Present/Absent | Not Tested | Yes/No |

Expand the matrix based on the engagement.

---

## Delivery Testing Workflow

A practical workflow is:

### 1. Confirm Scope

Identify:

- authorised source;
- authorised destination;
- permitted protocols;
- permitted file types;
- permitted testing window.

### 2. Establish a Harmless Baseline

Start with:

```text
test.txt
```

Confirm basic transfer.

### 3. Record Network Behaviour

Determine whether the connection is:

```text
Allowed
Blocked
Proxied
Inspected
Redirected
```

### 4. Inspect the Resulting File

Record:

- filename;
- size;
- SHA-256;
- security metadata;
- destination path.

### 5. Review Endpoint Telemetry

Determine whether the transfer generated:

- endpoint events;
- Defender events;
- EDR events;
- proxy events;
- SOC alerts.

### 6. Test Additional Permitted Formats

Only after the harmless baseline works should additional authorised file formats be considered.

### 7. Clean Up

Remove test artifacts when they are no longer required.

---

## Detection Validation

Payload delivery is useful for purple team exercises because it can validate several detection layers independently.

Potential telemetry sources include:

```text
DNS logs
Proxy logs
Firewall logs
Web gateway logs
Browser telemetry
Windows event logs
Microsoft Defender
EDR
SIEM
SOC alerts
```

Ask:

- Was the transfer visible?
- Was the source identified?
- Was the destination identified?
- Was the filename recorded?
- Was the file hash captured?
- Was the behaviour correlated with the endpoint?
- Did the SOC receive actionable context?

---

## Evidence Collection

For each delivery test, record:

```text
Timestamp:
Source:
Destination:
Protocol:
URL or share:
Filename:
File type:
File size:
SHA-256:
Delivery result:
Security metadata:
Endpoint response:
Network response:
SOC response:
Cleanup status:
```

Screenshots can supplement this information but should not replace structured evidence.

---

## Cleanup

After testing, identify and remove artifacts created during the assessment.

Potential artifacts include:

- downloaded files;
- archives;
- extracted files;
- temporary files;
- web server content;
- test directories;
- logs containing sensitive data.

Confirm that cleanup does not remove legitimate organisational data.

---

## Common Problems

### File Downloads but Does Not Execute

This may indicate that delivery is permitted while application control blocks execution.

Review:

- AppLocker;
- WDAC;
- endpoint protection;
- file reputation;
- Mark of the Web.

### Browser Blocks but Command-Line Transfer Works

The browser may apply additional reputation or download controls.

Treat the two delivery paths separately.

### PowerShell Cannot Reach the Server

Check:

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 443
```

Then investigate:

- proxy configuration;
- firewall rules;
- DNS;
- TLS;
- PowerShell policy.

### File Disappears After Download

Endpoint protection may have quarantined the file.

Review the relevant security product rather than repeatedly transferring the same artifact.

### Hash Changes

Confirm:

- transfer mode;
- archive/extraction behaviour;
- content encoding;
- whether an intermediary modified the content.

---

## Reporting

Avoid reporting only:

> The payload was downloaded successfully.

Instead describe the security boundary that was tested.

For example:

> The test artifact could be transferred to the endpoint over the assessed delivery channel. The transfer itself was permitted; execution controls were assessed separately.

Where relevant:

> The endpoint accepted the downloaded file, but application control prevented execution from the tested location.

This provides more useful information than combining delivery and execution into a single result.

---

## Payload Delivery Checklist

### Preparation

- [ ] Confirm scope
- [ ] Confirm permitted delivery channels
- [ ] Define expected security controls
- [ ] Prepare harmless baseline artifact
- [ ] Record artifact hash

### Delivery

- [ ] Confirm DNS
- [ ] Confirm TCP connectivity
- [ ] Test permitted delivery channel
- [ ] Record destination path
- [ ] Confirm file integrity
- [ ] Inspect security metadata

### Security Controls

- [ ] Review browser controls
- [ ] Review proxy behaviour
- [ ] Review endpoint protection
- [ ] Review application control
- [ ] Review network telemetry
- [ ] Review SOC visibility

### Completion

- [ ] Record evidence
- [ ] Record hashes
- [ ] Document observed controls
- [ ] Remove test artifacts
- [ ] Confirm cleanup

---

## Related Material

- [Red Teaming Methodology](methodology.md)
- [Infrastructure](infrastructure.md)
- [OPSEC](opsec.md)
- [Initial Access](initial-access.md)
- [Execution](execution.md)
- [Defence Evasion](defence-evasion.md)
- [Detection Validation](detection-validation.md)
- [Cleanup](cleanup.md)
- [Reporting](reporting.md)

---

## References

- [MITRE ATT&CK - Initial Access](https://attack.mitre.org/tactics/TA0001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Command and Control](https://attack.mitre.org/tactics/TA0011/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Mark of the Web](https://learn.microsoft.com/en-us/deployoffice/security/internet-macros-blocked){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Defender Application Control](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview){ target="_blank" rel="noopener noreferrer" }
