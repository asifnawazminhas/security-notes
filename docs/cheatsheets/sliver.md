# Sliver Cheatsheet

Sliver is an open-source command-and-control framework developed by Bishop Fox for authorised red team operations and adversary emulation.

This cheatsheet provides a quick reference for installation, server administration, operator management, navigation, session inspection, profiles, extensions, and troubleshooting. For detailed concepts and background, see the [Sliver tool page](../tools/sliver.md).

!!! warning "Authorised Use Only"
    Sliver is a command-and-control framework. Only use it against systems and infrastructure for which explicit authorisation has been obtained and within the agreed rules of engagement.

---

## Quick Reference

| Task | Command |
|---|---|
| Show help | `help` |
| Show version | `version` |
| Show operators | `operators` |
| Show sessions | `sessions` |
| Show beacons | `beacons` |
| Show jobs | `jobs` |
| Show profiles | `profiles` |
| Show extensions | `extensions` |
| Show current session info | `info` |
| Show environment | `env` |
| Show processes | `ps` |
| Show network interfaces | `ifconfig` |
| Show working directory | `pwd` |
| List directory | `ls` |

!!! note
    Sliver commands and flags can change between releases. Use the built-in `help` and `<command> --help` output for the installed version when a command differs from this reference.

---

# Architecture

A simplified Sliver architecture is:

```text
Operator
   |
   v
Sliver Client
   |
   v
Sliver Server
   |
   v
Authorised Test Infrastructure
```

The server provides central management while operators connect through Sliver clients.

This separation allows multiple authorised operators to use the same team infrastructure.

---

# Server

Start by checking the installed version.

```bash
sliver-server version
```

Start the server:

```bash
sliver-server
```

The server console should then become available.

---

## Server Help

```text
help
```

For help with a specific command:

```text
help <command>
```

Depending on the command, this form may also be available:

```text
<command> --help
```

Always prefer the help output from the installed Sliver version when documentation and local syntax differ.

---

# Client

Check the client version:

```bash
sliver-client version
```

Start the client:

```bash
sliver-client
```

A client normally connects using an operator configuration created by the Sliver server.

---

# Operators

Sliver supports multiple operators.

From the server console:

```text
operators
```

This displays configured operators.

Operator configurations should be protected because they provide access to the Sliver server.

---

## Create Operator Configuration

Operator creation syntax can differ between Sliver releases.

Inspect the installed version:

```text
new-operator --help
```

Record:

```text
Operator name
Server
Port
Configuration location
Creation date
```

Store operator configuration files securely.

---

# Sessions

List active sessions:

```text
sessions
```

A session generally represents an interactive connection available to the operator.

Useful information may include:

```text
ID
Name
Transport
Remote address
Hostname
Username
Operating system
Architecture
Last activity
```

The exact fields depend on the installed version.

---

## Session Help

After selecting an authorised laboratory session:

```text
help
```

Session context can expose commands that are not available from the top-level console.

This distinction is important when troubleshooting:

```text
Server command
      !=
Session command
```

---

## Session Information

Within an authorised session:

```text
info
```

Typical information includes:

```text
Hostname
Username
Operating system
Architecture
Process
PID
Transport
```

---

# Beacons

List beacons:

```text
beacons
```

Beacon-based communication differs from an interactive session because tasks and results may be asynchronous.

Conceptually:

```text
Operator
   |
   v
Task Queued
   |
   v
Beacon Checks In
   |
   v
Task Processed
   |
   v
Result Returned
```

This distinction is useful when interpreting delayed command results.

---

# Jobs

Display server jobs:

```text
jobs
```

Jobs commonly represent server-side listeners or related background services.

For command-specific options:

```text
jobs --help
```

Do not stop jobs belonging to another operator without coordination.

---

# Profiles

Profiles allow reusable generation settings to be stored.

List profiles:

```text
profiles
```

Inspect available profile commands:

```text
profiles --help
```

Because profile syntax has changed between Sliver versions, confirm the locally installed command syntax before following older examples.

---

## Version Differences

Older documentation may show command syntax that no longer matches the current release.

When this occurs:

```text
Documentation
     |
     v
Check Installed Version
     |
     v
Run --help
     |
     v
Map Old Arguments to Current Syntax
```

Useful commands:

```text
version
```

```text
profiles --help
```

```text
profiles generate --help
```

This is preferable to assuming a historical command remains valid.

---

# Extensions

List installed extensions:

```text
extensions
```

Display extension help:

```text
extensions --help
```

Extensions can add additional functionality to the Sliver client.

Before installing a third-party extension:

- review its source;
- verify its origin;
- inspect its manifest;
- inspect included binaries;
- record hashes;
- test it in a laboratory;
- document the version.

---

## Extension Structure

A Sliver extension package may conceptually contain:

```text
extension/
|
+-- extension.json
+-- supporting files
+-- architecture-specific artifacts
```

The exact structure depends on the extension.

---

## Inspect an Extension Archive

Before installation:

```bash
tar -tzf extension.tar.gz
```

Extract to a temporary directory:

```bash
mkdir extension-review
tar -xzf extension.tar.gz -C extension-review
```

Inspect the resulting files:

```bash
find extension-review -maxdepth 2 -type f -print
```

---

## Inspect the Manifest

If the package contains `extension.json`:

```bash
cat extension-review/extension.json
```

For formatted JSON:

```bash
jq . extension-review/extension.json
```

Review:

```text
Extension name
Commands
Entry points
Architecture
Required files
Arguments
Help text
```

Do not install an unknown extension solely because the archive extracts successfully.

---

## Hash Extension Files

```bash
sha256sum extension-review/*
```

For recursive hashing:

```bash
find extension-review -type f -exec sha256sum {} \;
```

Keep hashes with assessment notes where reproducibility is required.

---

# Basic Session Reconnaissance

Within an authorised laboratory session, several commands provide basic host context.

## Current Directory

```text
pwd
```

---

## List Directory

```text
ls
```

For help:

```text
ls --help
```

---

## Current Identity

```text
whoami
```

---

## Environment

```text
env
```

Environment information can help identify:

```text
TEMP
TMP
PATH
USERPROFILE
COMPUTERNAME
PROCESSOR_ARCHITECTURE
```

---

## Network Interfaces

```text
ifconfig
```

Record:

```text
Interface
IP address
Subnet
```

---

## Processes

```text
ps
```

Process information can provide useful context for validating endpoint telemetry.

Record only the information required by the engagement.

---

# Filesystem

Sliver session commands may provide filesystem navigation similar to other command-line environments.

Typical commands include:

```text
pwd
ls
cd
```

Use:

```text
help
```

or:

```text
<command> --help
```

to confirm available options for the installed version.

---

# Upload and Download

File-transfer functionality should be used only where permitted by the rules of engagement.

Before transferring any assessment artifact, record:

```text
Source
Destination
Filename
SHA-256
Purpose
Cleanup requirement
```

Verify local hashes before transfer:

```bash
sha256sum artifact.bin
```

On Windows, a received artifact can be verified with:

```powershell
Get-FileHash -Algorithm SHA256 .\artifact.bin
```

This confirms that the intended file was transferred without modification.

---

# Host Information

When documenting an authorised session, useful context includes:

```text
Hostname
Username
Operating system
Architecture
Process
Process ID
Network addresses
Session ID
Transport
```

Collect only what is required for the assessment.

---

# Process Context

The process hosting a session can affect:

- privilege;
- architecture;
- endpoint telemetry;
- application control;
- stability.

Use:

```text
info
```

and:

```text
ps
```

to understand the current context.

Do not assume that the account name alone establishes the process integrity or privilege level.

---

# Architecture

Always verify architecture when working with architecture-specific extensions or assessment artifacts.

Typical values include:

```text
x86
x64
ARM64
```

Within Sliver:

```text
info
```

On Linux, inspect an external artifact with:

```bash
file artifact.dll
```

For Windows PE files:

```bash
x86_64-w64-mingw32-objdump -f artifact.dll
```

Architecture mismatches are a common source of extension and loader failures.

---

# Third-Party Tooling

Sliver can be extended with third-party tooling, but external components should be treated as untrusted until reviewed.

Before use:

```text
Source Review
      |
      v
Build Review
      |
      v
Static Inspection
      |
      v
Hash
      |
      v
Laboratory Validation
      |
      v
Authorised Use
```

Do not introduce an unknown binary directly into an assessment environment.

---

# Static Inspection

Useful Linux commands for inspecting third-party artifacts include:

```bash
file artifact
```

```bash
sha256sum artifact
```

```bash
strings artifact | less
```

For PE files:

```bash
x86_64-w64-mingw32-objdump -f artifact.dll
```

For PE metadata:

```bash
x86_64-w64-mingw32-objdump -p artifact.dll | less
```

---

# COFF Objects

Some Sliver extensions and related red-team tooling use COFF object files.

Identify an object:

```bash
file artifact.o
```

Inspect it:

```bash
x86_64-w64-mingw32-objdump -f artifact.o
```

Display sections:

```bash
x86_64-w64-mingw32-objdump -h artifact.o
```

Display symbols:

```bash
x86_64-w64-mingw32-objdump -t artifact.o
```

This provides static validation without executing the object.

---

# PE vs COFF

A Windows DLL and a raw COFF object are not the same format.

Typical PE/DLL identification:

```text
PE32+ executable (DLL)
```

Typical COFF object identification:

```text
Intel amd64 COFF object file
```

A parser designed for raw COFF input should therefore not be expected to accept an ordinary PE DLL.

Check first:

```bash
file artifact
```

This simple step prevents many misleading parser errors.

---

# Extension Troubleshooting

When an extension does not behave as expected, troubleshoot it layer by layer.

```text
Extension Installed?
       |
       v
Manifest Valid?
       |
       v
Command Registered?
       |
       v
Correct Console Context?
       |
       v
Required Session Present?
       |
       v
Architecture Compatible?
       |
       v
Required Artifact Present?
```

Avoid assuming the extension itself is broken before checking these dependencies.

---

## Command Not Found

If a command is unavailable:

```text
help
```

Then:

```text
extensions
```

Check:

1. Is the extension installed?
2. Does its manifest register the command?
3. Is the command available only within a session?
4. Is the correct client configuration being used?
5. Does the extension support the installed Sliver version?

---

## Top-Level vs Session Commands

A common source of confusion is attempting to use a session-specific command from the top-level console.

Conceptually:

```text
Sliver Console
    |
    +---- Server Commands
    |
    +---- Session Selected
              |
              +---- Session Commands
              +---- Extension Commands
```

Always check the current context.

---

## Missing Artifact

If an extension expects a local file:

```bash
test -s artifact.bin && echo "[OK] artifact present" || echo "[MISSING] artifact"
```

Inspect:

```bash
stat artifact.bin
```

Identify:

```bash
file artifact.bin
```

Hash:

```bash
sha256sum artifact.bin
```

Do not continue troubleshooting downstream components until the required input exists.

---

## Archive Problems

List archive contents:

```bash
tar -tzf extension.tar.gz
```

Test archive integrity:

```bash
gzip -t extension.tar.gz
```

Extract manually:

```bash
mkdir /tmp/extension-check
tar -xzf extension.tar.gz -C /tmp/extension-check
```

Then inspect:

```bash
find /tmp/extension-check -type f -print
```

---

## JSON Problems

Validate a manifest:

```bash
jq . extension.json
```

If valid, `jq` prints the parsed document.

A syntax error indicates malformed JSON.

---

# Build Troubleshooting

For custom Sliver-related extensions, validate the build environment separately from Sliver itself.

Useful checks include:

```bash
gcc --version
```

```bash
x86_64-w64-mingw32-gcc --version
```

```bash
nasm --version
```

```bash
java -version
```

Only check dependencies that are actually required by the project.

---

## Validate Build Output

After compilation:

```bash
find build -maxdepth 2 -type f -print
```

Then:

```bash
file build/*
```

Hash:

```bash
sha256sum build/*
```

A successful compiler exit does not automatically mean the expected final artifact was created.

---

# Evidence Collection

For an authorised Sliver exercise, record relevant operational evidence.

A useful template is:

```text
Date:
Operator:
Sliver version:
Server:
Assessment:
Session ID:
Hostname:
Username:
Operating system:
Architecture:
Transport:
Test performed:
Expected control:
Observed result:
Detection:
Cleanup:
```

Avoid placing credentials, operator secrets, private keys, or authentication material in general assessment notes.

---

# Detection Validation

Sliver activity can generate telemetry across multiple layers.

Potential sources include:

```text
Process telemetry
Network connections
DNS
Proxy logs
Firewall logs
File creation
Module loading
Endpoint protection
EDR
SIEM
SOC alerts
```

During a purple team exercise, evaluate the complete chain:

```text
Activity
   |
   v
Endpoint Event
   |
   v
EDR
   |
   v
SIEM
   |
   v
Detection
   |
   v
SOC Investigation
```

A successful detection should provide enough context for an analyst to understand what occurred.

---

# Network Validation

Before troubleshooting Sliver-specific behaviour, verify basic connectivity independently.

Windows:

```powershell
Test-NetConnection -ComputerName 192.0.2.10 -Port 443
```

Linux:

```bash
nc -vz 192.0.2.10 443
```

DNS:

```powershell
Resolve-DnsName example.com
```

or:

```bash
dig example.com
```

This helps separate infrastructure problems from framework problems.

---

# Operational Security

Red team infrastructure should be treated as sensitive.

Protect:

- operator configurations;
- server access;
- private keys;
- assessment artifacts;
- logs;
- credentials;
- client configuration;
- infrastructure metadata.

Apply:

- least privilege;
- restricted administrative access;
- encrypted transport;
- strong authentication;
- host hardening;
- controlled firewall rules;
- timely patching;
- secure backups where required.

---

# Multi-Operator Environments

When multiple testers use the same Sliver server, coordination becomes important.

Record:

```text
Operator
Assigned systems
Testing window
Active sessions
Infrastructure
Cleanup responsibility
```

Avoid:

- stopping another operator's jobs;
- modifying shared configuration unexpectedly;
- deleting shared artifacts;
- testing against systems assigned to another operator.

---

# Cleanup

At the end of an authorised exercise, identify assessment artifacts and infrastructure that require cleanup.

Potential items include:

```text
Transferred test files
Temporary files
Test directories
Operator configurations
Temporary listeners
Temporary infrastructure
Assessment-specific logs
Generated artifacts
```

Do not delete evidence required for reporting or incident-review purposes.

---

# Quick Troubleshooting

## Sliver Does Not Start

Check:

```bash
sliver-server version
```

Then verify the binary:

```bash
which sliver-server
```

Inspect permissions:

```bash
ls -l "$(which sliver-server)"
```

---

## Client Cannot Connect

Check:

```text
Operator configuration
Server address
Server port
Firewall
Routing
Server process
Version compatibility
```

Validate network reachability separately before troubleshooting the client.

---

## Extension Is Installed but Command Is Missing

Check:

```text
extensions
```

Then:

```text
help
```

Confirm:

```text
Extension manifest
Command registration
Console context
Session requirement
Architecture
Version compatibility
```

---

## Command Syntax Differs from Documentation

Run:

```text
<command> --help
```

and:

```text
version
```

The locally installed version is authoritative for command syntax.

---

## Expected File Does Not Exist

Check:

```bash
test -e expected-file && echo "[EXISTS]" || echo "[MISSING]"
```

For a required non-empty artifact:

```bash
test -s expected-file && echo "[OK]" || echo "[MISSING OR EMPTY]"
```

Then trace backwards through the build process.

---

# Sliver Assessment Checklist

## Infrastructure

- [ ] Record Sliver version
- [ ] Secure server access
- [ ] Restrict firewall exposure
- [ ] Protect operator configurations
- [ ] Document authorised infrastructure
- [ ] Define cleanup responsibility

## Operators

- [ ] Create only required operators
- [ ] Protect configuration files
- [ ] Record operator ownership
- [ ] Remove obsolete access after assessment

## Sessions

- [ ] Confirm target is in scope
- [ ] Record session ID
- [ ] Record hostname
- [ ] Record username
- [ ] Record architecture
- [ ] Record process context
- [ ] Record transport where required

## Extensions

- [ ] Verify source
- [ ] Review manifest
- [ ] Inspect package contents
- [ ] Check architecture
- [ ] Record SHA-256
- [ ] Test in laboratory first
- [ ] Confirm Sliver version compatibility

## Detection

- [ ] Review endpoint telemetry
- [ ] Review network telemetry
- [ ] Review DNS
- [ ] Review firewall/proxy logs
- [ ] Review EDR
- [ ] Review SIEM
- [ ] Review SOC response
- [ ] Separate prevention from detection

## Completion

- [ ] Record evidence
- [ ] Record relevant hashes
- [ ] Stop assessment-specific jobs where appropriate
- [ ] Remove test artifacts
- [ ] Remove temporary infrastructure
- [ ] Confirm cleanup

---

# Related Material

- [Sliver](../tools/sliver.md)
- [Cobalt Strike](../tools/cobalt-strike.md)
- [Red Teaming](../red-teaming/index.md)
- [Infrastructure](../red-teaming/infrastructure.md)
- [Custom Tooling](../red-teaming/custom-tooling.md)
- [Payload Delivery](../red-teaming/payload-delivery.md)
- [Staged Payloads](../red-teaming/staged-payloads.md)
- [Execution](../red-teaming/execution.md)
- [Command and Control](../red-teaming/command-and-control.md)
- [Defence Evasion](../red-teaming/defence-evasion.md)
- [Detection Validation](../red-teaming/detection-validation.md)
- [Cleanup](../red-teaming/cleanup.md)

---

# References

- [Sliver - GitHub](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }
- [Sliver Documentation](https://sliver.sh/docs){ target="_blank" rel="noopener noreferrer" }
- [Bishop Fox](https://bishopfox.com/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Command and Control](https://attack.mitre.org/tactics/TA0011/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Application Layer Protocol](https://attack.mitre.org/techniques/T1071/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Ingress Tool Transfer](https://attack.mitre.org/techniques/T1105/){ target="_blank" rel="noopener noreferrer" }
