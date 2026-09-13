# Custom Tooling

Custom tooling is software developed or adapted for a specific red team, penetration testing, adversary emulation, or security research requirement. It can range from small automation scripts to purpose-built utilities that support reconnaissance, execution, data processing, testing workflows, or integration with existing security tooling.

Unlike general-purpose offensive security tools, custom tooling can be designed around the exact requirements of an engagement, laboratory, target environment, or research objective.

!!! warning "Authorised Use Only"
    Custom tooling should only be developed and used against systems for which explicit authorisation has been obtained. Define the scope, rules of engagement, permitted techniques, and cleanup requirements before testing.

---

## Overview

Custom tooling can be useful when existing tools do not provide the required functionality or when a workflow needs to be automated.

Typical use cases include:

- automating repetitive assessment tasks;
- processing reconnaissance or enumeration data;
- interacting with APIs and protocols;
- validating security controls;
- integrating multiple tools into a single workflow;
- creating purpose-built laboratory utilities;
- collecting structured evidence;
- reproducing vulnerabilities;
- supporting adversary emulation exercises.

Custom tooling does not necessarily need to be complex. A short Python, PowerShell, Bash, C#, Go, or C program can sometimes provide more value than a large framework when it addresses a specific requirement.

---

## Why Develop Custom Tooling?

Existing security tools are useful because they provide mature implementations of common techniques. However, relying exclusively on public tooling can introduce limitations.

Custom tooling can provide greater control over:

- input and output formats;
- execution flow;
- error handling;
- protocol behaviour;
- logging;
- automation;
- integration;
- dependencies;
- performance;
- portability.

It also helps the tester understand the underlying technique rather than treating an existing tool as a black box.

---

## Development Workflow

A structured development process helps keep custom tooling understandable and maintainable.

```text
Requirement
    |
    v
Research
    |
    v
Minimal Prototype
    |
    v
Local Testing
    |
    v
Error Handling
    |
    v
Logging and Output
    |
    v
Controlled Validation
    |
    v
Documentation
```

Start with the smallest implementation that demonstrates the required behaviour.

Additional functionality can then be added after the core behaviour has been validated.

---

## Define the Requirement

Before writing code, define exactly what the tool needs to accomplish.

Useful questions include:

- What problem is being solved?
- What input does the tool require?
- What output should it produce?
- Which operating systems must be supported?
- Which protocols or APIs are involved?
- Does the tool require elevated privileges?
- What dependencies are required?
- How will failures be handled?
- What evidence needs to be retained?

A clear requirement prevents unnecessary functionality from being added.

---

## Language Selection

The appropriate programming language depends on the environment and objective.

| Language | Common Uses |
|---|---|
| Python | Automation, APIs, parsing, reconnaissance and rapid prototyping |
| PowerShell | Windows administration, enumeration and security testing |
| Bash | Linux automation and tool orchestration |
| C | Native utilities and low-level Windows/Linux research |
| C++ | Native tooling and complex low-level applications |
| C# | Windows and .NET tooling |
| Go | Portable networking and command-line utilities |
| Rust | Memory-safe systems and networking tools |

There is rarely a single correct language. Choose the language that best matches the target environment and development requirement.

---

## Start with a Minimal Prototype

Avoid building a large framework before validating the underlying idea.

For example, a prototype may initially:

1. accept a single argument;
2. perform one operation;
3. display the result;
4. exit cleanly.

Once this works reliably, additional functionality can be introduced.

This makes troubleshooting considerably easier.

---

## Input Validation

Custom tools should validate user-controlled input before processing it.

Examples include:

- file paths;
- IP addresses;
- hostnames;
- URLs;
- port numbers;
- usernames;
- configuration files;
- command-line arguments.

Invalid input should result in a clear error rather than unpredictable behaviour.

Example:

```python
import ipaddress

target = "192.0.2.10"

try:
    address = ipaddress.ip_address(target)
    print(f"Valid address: {address}")
except ValueError:
    print("Invalid IP address")
```

---

## Configuration

Avoid hard-coding environment-specific values directly into source code.

Prefer:

- command-line arguments;
- configuration files;
- environment variables;
- clearly defined constants.

For example:

```bash
python3 tool.py --target 192.0.2.10 --port 443
```

This makes the tool easier to reuse across controlled environments.

---

## Logging

Logging becomes increasingly important as tooling becomes more complex.

Useful information to record includes:

- timestamps;
- target identifiers;
- operations performed;
- warnings;
- errors;
- result summaries.

Python example:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logging.info("Starting validation")
```

Avoid writing credentials, tokens, private keys, or other sensitive information to logs unless there is a specific authorised requirement.

---

## Structured Output

Machine-readable output makes custom tooling easier to integrate with other workflows.

Useful formats include:

- JSON;
- CSV;
- JSON Lines;
- XML.

Example:

```json
{
  "target": "192.0.2.10",
  "port": 443,
  "status": "reachable"
}
```

Structured output can later be processed using tools such as `jq`, Python, PowerShell, or reporting pipelines.

---

## Error Handling

A tool should fail predictably.

Handle conditions such as:

- connection failures;
- timeouts;
- missing files;
- invalid arguments;
- unavailable dependencies;
- permission errors;
- unexpected responses.

Python example:

```python
try:
    with open("targets.txt", "r", encoding="utf-8") as handle:
        targets = handle.readlines()
except FileNotFoundError:
    print("targets.txt was not found")
```

Clear error messages reduce troubleshooting time during an assessment.

---

## Dependency Management

Document all external dependencies.

For Python projects, a virtual environment can help isolate packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Dependencies can then be recorded:

```bash
pip freeze > requirements.txt
```

For compiled projects, document:

- compiler version;
- architecture;
- required libraries;
- build commands;
- runtime requirements.

---

## Architecture Awareness

When developing native tooling, confirm the intended architecture.

On Linux:

```bash
file ./tool
```

For Windows PE files:

```bash
file ./tool.exe
```

Common architectures include:

```text
x86
x86-64
ARM
ARM64
```

Architecture mismatches are a common source of failures when testing native tooling.

---

## Hashing Build Artifacts

Hashing compiled artifacts provides a simple way to identify the exact build used during testing.

```bash
sha256sum ./tool
```

For multiple artifacts:

```bash
sha256sum build/*
```

Hashes can be retained alongside assessment notes when reproducibility is important.

---

## Static Inspection

Before using a compiled artifact, inspect its basic properties.

```bash
file ./tool.exe
```

For PE files:

```bash
x86_64-w64-mingw32-objdump -f ./tool.exe
```

Strings can provide additional context:

```bash
strings ./tool.exe | less
```

Static inspection is particularly useful when working with third-party code or externally supplied build artifacts.

---

## Source Review

Review source code before compiling third-party tooling where practical.

Look for:

- unexpected network connections;
- hard-coded credentials;
- destructive operations;
- telemetry;
- automatic updates;
- embedded URLs;
- file modification;
- persistence mechanisms;
- external command execution.

Useful search tools include:

```bash
rg -n "http|https|socket|connect|exec|system|password|token" .
```

The results require manual interpretation, but this provides a useful starting point.

---

## Build Reproducibility

Where possible, record the exact build process.

Example:

```text
Tool version:
Git commit:
Compiler:
Architecture:
Dependencies:
Build command:
SHA-256:
```

This helps reproduce results and identify differences between builds.

---

## Testing Strategy

Custom tooling should be validated progressively.

### Stage 1 - Local Validation

Confirm:

- arguments work;
- files are created correctly;
- parsing behaves correctly;
- errors are handled;
- output is understandable.

### Stage 2 - Laboratory Validation

Test against controlled infrastructure that represents the intended environment.

Confirm:

- protocol compatibility;
- architecture compatibility;
- expected privileges;
- network behaviour;
- logging behaviour.

### Stage 3 - Authorised Engagement Validation

Only after local and laboratory testing should the tool be considered for use within an authorised assessment.

---

## Network Testing

When developing network-aware tooling, test basic connectivity separately from application logic.

Examples:

```bash
curl -I https://example.com
```

```bash
nc -vz 192.0.2.10 443
```

```bash
openssl s_client -connect example.com:443
```

This helps distinguish application bugs from connectivity problems.

---

## Temporary Files

Custom tooling may create temporary files during execution.

Document:

- where files are written;
- naming conventions;
- cleanup behaviour;
- whether sensitive data is stored.

Temporary artifacts should be removed after testing when they are no longer required.

---

## Cleanup

Cleanup should be considered during development rather than after the tool has already been deployed.

Potential artifacts include:

- temporary files;
- generated binaries;
- configuration files;
- logs;
- test accounts;
- scheduled tasks;
- services;
- registry modifications;
- network listeners.

Keep a record of any changes made during controlled testing.

---

## Documentation

Every reusable custom tool should have basic documentation.

At minimum, document:

```text
Purpose
Requirements
Installation
Usage
Arguments
Examples
Expected output
Known limitations
Cleanup
```

Good documentation reduces the risk of a tool being used incorrectly.

---

## Version Control

Store source code in version control where appropriate.

Useful Git commands include:

```bash
git status
```

```bash
git diff
```

```bash
git log --oneline
```

Tagging stable versions can help distinguish assessment builds from development versions.

---

## Operational Considerations

Before using custom tooling during an authorised engagement, consider:

- rules of engagement;
- permitted systems;
- permitted accounts;
- permitted testing windows;
- potential production impact;
- endpoint security controls;
- network monitoring;
- rollback procedures;
- cleanup requirements.

A technically successful test can still create unnecessary operational risk if these factors are ignored.

---

## Evidence Collection

Record enough information to reproduce important observations.

Useful evidence may include:

- command executed;
- timestamp;
- relevant output;
- artifact hash;
- affected host;
- tool version;
- configuration;
- screenshot where appropriate.

Avoid collecting unnecessary sensitive information.

---

## Common Mistakes

### Building Too Much Too Early

Large projects are harder to debug.

Start with the smallest functional implementation.

### Hard-Coded Environment Values

Hard-coded addresses and paths reduce portability.

Use arguments or configuration instead.

### Poor Error Handling

Unhandled errors make troubleshooting difficult.

Provide clear failure messages.

### No Cleanup Process

Testing artifacts can remain after an engagement.

Design cleanup alongside the functionality.

### Missing Documentation

Undocumented tools become difficult to maintain and safely reuse.

### Testing Directly in Production

Validate new tooling in an isolated environment first.

---

## Tooling Checklist

Before considering a custom tool ready for controlled use, verify:

- [ ] Purpose is clearly defined
- [ ] Scope is understood
- [ ] Input is validated
- [ ] Errors are handled
- [ ] Dependencies are documented
- [ ] Architecture is correct
- [ ] Build process is reproducible
- [ ] Artifact hashes are recorded
- [ ] Logging is appropriate
- [ ] Sensitive information is protected
- [ ] Laboratory testing has been completed
- [ ] Cleanup requirements are documented
- [ ] Usage documentation exists

---

## Related Material

- [Red Teaming Methodology](methodology.md)
- [Infrastructure](infrastructure.md)
- [OPSEC](opsec.md)
- [Execution](execution.md)
- [Detection Validation](detection-validation.md)
- [Reporting](reporting.md)

---

## References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [Python Documentation](https://docs.python.org/3/){ target="_blank" rel="noopener noreferrer" }
- [Go Documentation](https://go.dev/doc/){ target="_blank" rel="noopener noreferrer" }
- [Rust Documentation](https://doc.rust-lang.org/){ target="_blank" rel="noopener noreferrer" }
