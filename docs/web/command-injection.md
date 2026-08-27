# OS Command Injection

OS Command Injection occurs when attacker-controlled input is incorporated into an operating system command in an unsafe manner.

If an application passes user-controlled data to a shell or operating system command interpreter without appropriate controls, an attacker may be able to alter the intended command.

Command injection testing should not begin with large payload lists or automated tools. First determine where user input enters the application, what functionality may invoke operating system commands, how the input is transformed, and whether application behaviour indicates command execution.

!!! warning "Authorised Security Testing"
    Perform command injection testing only against applications and systems for which you have explicit authorisation. These notes are intended for authorised penetration testing, lab environments, security research and responsible vulnerability disclosure.

---

## Objectives

The primary objectives are to determine:

- whether user-controlled input reaches an operating system command
- whether a shell is involved
- whether command structure can be influenced
- which operating system is likely involved
- which shell or command interpreter may be used
- whether command output is returned
- whether execution can be inferred through timing
- whether execution can be confirmed through an authorised callback
- whether argument injection is possible
- whether input validation can be bypassed
- what privileges the affected process has
- what security impact can be demonstrated safely

A useful mental model is:

```text
User Input
    ↓
Application
    ↓
Validation / Transformation
    ↓
Command Construction
    ↓
Shell / Process API
    ↓
Operating System
    ↓
Command Execution
```

The most important question is:

> Can attacker-controlled input alter the command that the application intended to execute?

---

# Command Injection Testing Workflow

A structured workflow can look like:

```text
Discover Input
      ↓
Understand Functionality
      ↓
Establish Baseline
      ↓
Identify Possible OS Interaction
      ↓
Test Command Metacharacters
      ↓
Observe Response
      ↓
Determine OS / Shell
      ↓
Confirm Execution
      ↓
Targeted Automation
      ↓
Determine Execution Context
      ↓
Assess Impact
      ↓
Collect Minimal Evidence
      ↓
Report
```

Start with the application's intended functionality.

For example:

```text
Ping utility
DNS lookup
File conversion
Image processing
Archive creation
PDF generation
Video processing
Backup functionality
Network diagnostics
System administration
Git operations
Build systems
Import / export
Monitoring functionality
```

These features are often more interesting than arbitrary text fields.

---

# Common Command Injection Locations

Potential locations include:

```text
GET parameters
POST parameters
JSON properties
HTTP headers
Cookies
File names
File paths
Host names
IP addresses
URLs
Email addresses
Export parameters
Import parameters
Search parameters
Diagnostic tools
Administrative functionality
API parameters
```

Examples:

```text
?host=127.0.0.1
```

```text
?domain=example.com
```

```text
?file=report.pdf
```

```text
?url=https://example.com
```

```text
?format=pdf
```

The parameter name alone does not prove that an operating system command is involved.

---

# High Value Functionality

Pay particular attention to functionality performing tasks such as:

```text
Ping
Traceroute
DNS lookup
WHOIS
Network diagnostics
File conversion
Image resizing
Archive extraction
Archive creation
PDF generation
Video conversion
Backup creation
Log processing
Git operations
Package management
System monitoring
Printer interaction
External program execution
```

A useful thought process is:

```text
Application Feature
       ↓
Could this require an external program?
       ↓
Could user input become an argument?
       ↓
How is that process started?
```

---

# Establish a Baseline

Before modifying the parameter, send the normal request.

Example:

```http
POST /api/ping HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "host": "127.0.0.1"
}
```

Record:

```text
Status code
Response length
Response body
Response time
Application message
Returned command output
```

Example:

```text
Status: 200
Time: 230 ms
Result: Host reachable
```

The baseline gives you something to compare subsequent tests against.

---

# Identify the Operating System

Technology identification can help determine whether the backend is likely running:

```text
Linux
Unix
Windows
macOS
Containerised Linux
```

Potential indicators include:

```text
Server headers
Error messages
File paths
Framework behaviour
Technology stack
Source code
Application documentation
Command output
```

Examples:

```text
/var/www/
/home/
/tmp/
```

suggest a Unix-like environment.

Paths such as:

```text
C:\Windows\
C:\Users\
C:\Program Files\
```

suggest Windows.

Do not rely on a single indicator.

---

# Shell Metacharacters

Shells interpret certain characters as having special meaning.

On Unix-like systems, interesting characters and constructs may include:

```text
;
|
||
&&
&
`
$()
>
>>
<
```

On Windows command interpreters, interesting characters may include:

```text
&
&&
|
||
>
>>
<
```

Support and behaviour depend on:

```text
Operating system
Shell
Execution API
Quoting
Application framework
Input validation
```

Test characters individually to understand how they are handled.

---

# Character Testing

Start with controlled syntax changes.

Determine how the application handles:

```text
;
```

then:

```text
|
```

then:

```text
&
```

then:

```text
'
```

then:

```text
"
```

Observe:

```text
HTTP status
Response length
Application errors
Validation errors
Timing
Output changes
```

This can reveal whether characters are:

```text
Accepted
Rejected
Encoded
Removed
Escaped
Normalised
Interpreted
```

---

# Linux Command Injection

Suppose an application performs functionality conceptually similar to:

```bash
ping -c 1 USER_INPUT
```

If `USER_INPUT` is concatenated directly into a shell command, shell metacharacters may alter the intended command.

A harmless authorised validation might conceptually test:

```text
127.0.0.1; id
```

If command output is returned, you might observe:

```text
uid=...
gid=...
groups=...
```

For authorised testing, prefer commands that demonstrate execution without modifying the system.

Examples:

```bash
id
```

```bash
whoami
```

```bash
hostname
```

```bash
uname -a
```

Avoid destructive commands.

---

# Windows Command Injection

A Windows application might conceptually execute:

```cmd
ping USER_INPUT
```

If user-controlled input reaches `cmd.exe` unsafely, command separators may alter execution.

A benign validation might use:

```cmd
whoami
```

or:

```cmd
hostname
```

The objective is to demonstrate execution, not to modify the host.

---

# Output Based Command Injection

Output based command injection occurs when output from the injected command is returned through the application.

Example:

```text
Input
 ↓
Command Construction
 ↓
Operating System
 ↓
Command Output
 ↓
Application Response
```

This is usually easier to validate than blind command injection.

Look for:

```text
Username
Hostname
Operating system information
Command errors
Unexpected output
```

---

# Blind Command Injection

Blind command injection occurs when commands execute but their output is not returned in the HTTP response.

The application might simply return:

```text
Operation completed successfully
```

regardless of what occurred on the backend.

Potential confirmation techniques include:

```text
Timing differences
Controlled DNS interaction
Controlled HTTP interaction
Application state changes
```

Avoid unnecessary state changes where timing or controlled callbacks are sufficient.

---

# Time Based Blind Command Injection

Timing can be used to infer command execution when output is not visible.

The general concept is:

```text
Normal Input
     ↓
Normal Response Time

Controlled Delay
     ↓
Delayed Response
```

For a Unix-like environment, a controlled test may use a short delay:

```bash
sleep 5
```

For Windows:

```cmd
timeout /t 5
```

The exact syntax depends on how input reaches the command interpreter.

---

## Timing Workflow

```text
Send Baseline
      ↓
Measure Response
      ↓
Repeat Baseline
      ↓
Determine Normal Variation
      ↓
Introduce Controlled Delay
      ↓
Repeat Test
      ↓
Compare Timing
      ↓
Confirm Correlation
```

Do not treat a single slow request as proof.

---

## Timing Evidence

Record several measurements.

| Request | Baseline | Controlled Test |
|---|---:|---:|
| 1 | 210 ms | 5.2 s |
| 2 | 195 ms | 5.1 s |
| 3 | 224 ms | 5.2 s |
| 4 | 203 ms | 5.1 s |

A predictable delay that repeatedly correlates with the test is significantly stronger evidence than one slow request.

---

# Out of Band Command Injection

When command output is unavailable, an authorised callback service can sometimes confirm execution.

Conceptually:

```text
Application
     ↓
Command Injection
     ↓
Operating System
     ↓
DNS / HTTP Request
     ↓
Controlled Callback Infrastructure
```

This can be useful when:

```text
Output is hidden
Timing is unreliable
Commands execute asynchronously
Background jobs process the input
```

---

# Burp Collaborator

Burp Collaborator can be useful for detecting out of band interactions during authorised testing.

Workflow:

```text
Burp Repeater
      ↓
Generate Collaborator Domain
      ↓
Use Controlled Callback
      ↓
Send Request
      ↓
Poll Collaborator
      ↓
Interaction?
      ↓
Correlate With Request
```

Potential interaction types include:

```text
DNS
HTTP
HTTPS
SMTP
```

A callback should be correlated with the exact request that triggered it.

---

# Interactsh

Interactsh is another useful out of band interaction service.

Project:

https://github.com/projectdiscovery/interactsh

A typical authorised workflow is:

```text
Start interactsh-client
        ↓
Receive Unique Domain
        ↓
Use Domain in Controlled Test
        ↓
Send Request
        ↓
Monitor Interactions
        ↓
Correlate Callback
```

Start the client:

```bash
interactsh-client
```

The client provides a unique interaction domain that can be used for controlled testing.

---

# DNS Based Verification

DNS callbacks can be useful because outbound DNS resolution is sometimes available even when outbound HTTP is restricted.

Conceptually:

```text
Command Execution
      ↓
DNS Resolution
      ↓
Controlled Domain
      ↓
Callback Logged
```

When using callbacks, assign unique identifiers to each injection location.

For example:

```text
CMD-001 → host parameter
CMD-002 → filename parameter
CMD-003 → User-Agent
CMD-004 → JSON url property
```

This makes callback correlation significantly easier.

---

# HTTP Based Verification

HTTP interactions can provide another confirmation mechanism.

Conceptually:

```text
Command Injection
      ↓
Operating System Utility
      ↓
HTTP Request
      ↓
Controlled Server
```

Use infrastructure that is explicitly authorised for the assessment.

Do not collect unnecessary information from the target.

---

# Asynchronous Command Execution

Some application functionality runs asynchronously.

Examples include:

```text
Background workers
Job queues
File processing
Image conversion
PDF generation
Email processing
Scheduled tasks
Import jobs
CI/CD pipelines
```

The flow may be:

```text
HTTP Request
     ↓
Queue
     ↓
HTTP Response
     ↓
Worker Processes Job Later
     ↓
Command Execution
```

Therefore, an immediate HTTP response may not reveal whether command execution occurred.

Out of band callbacks can be particularly useful in these situations.

---

# Argument Injection

Command injection and argument injection are related but not identical.

Consider:

```text
program USER_INPUT
```

Even when shell metacharacters are not interpreted, attacker-controlled input may influence the arguments passed to the program.

For example:

```text
Application
    ↓
External Utility
    ↓
Attacker Controls Argument
    ↓
Unexpected Program Behaviour
```

This is often called:

```text
Argument Injection
Option Injection
Parameter Injection
```

---

# Option Injection

Many command-line programs treat values beginning with:

```text
-
```

or:

```text
--
```

as options.

If attacker-controlled input becomes a command-line argument, it may be possible to influence the external utility even without shell command separators.

The security question is:

> Can user-controlled data become an option rather than ordinary data?

---

# End of Options Marker

Many Unix command-line utilities support:

```text
--
```

to indicate the end of command options.

For example:

```bash
some-command -- USER_INPUT
```

This can help prevent user-controlled values beginning with `-` from being interpreted as options.

Support depends on the specific utility.

---

# Command Substitution

Unix shells may support command substitution using constructs such as:

```text
$(...)
```

or:

```text
`...`
```

Whether these are interpreted depends on whether the application invokes a shell.

For example:

```text
Process API
   ↓
Direct Executable Invocation
```

behaves differently from:

```text
Application
   ↓
Shell
   ↓
Command String
```

This distinction is important when determining exploitability.

---

# Direct Process Execution vs Shell Execution

Consider two conceptual designs.

Direct process execution:

```text
Application
     ↓
Process API
     ↓
Executable + Separate Arguments
```

versus shell execution:

```text
Application
     ↓
/bin/sh -c
     ↓
Constructed Command String
```

The second design introduces shell parsing.

Avoid invoking a shell when it is not necessary.

---

# Quoting

Applications sometimes attempt to make command execution safe by surrounding user input with quotes.

Example:

```text
command "USER_INPUT"
```

Quoting alone should not be considered a complete defence.

Questions include:

```text
Which quote is used?
Can the quote be terminated?
Are backslashes handled?
Does another decoding layer exist?
Does the shell perform expansion?
```

The safest approach is generally to avoid shell command construction entirely.

---

# Environment Variables

Shell environments may expand variables.

Unix-like examples include:

```text
$HOME
$PATH
$USER
```

Windows examples include:

```text
%PATH%
%USERNAME%
%TEMP%
```

Environment variable expansion can affect how input is interpreted.

---

# Whitespace

Input validation sometimes blocks normal spaces.

Rather than immediately attempting bypasses, determine:

```text
Is whitespace blocked?
Is it encoded?
Is it normalised?
Does the application split arguments itself?
Is a shell involved?
```

Understanding the parser is more useful than blindly trying alternative syntax.

---

# URL Encoding

Characters may be transformed by URL encoding.

Examples:

```text
;       → %3B
&       → %26
|       → %7C
space   → %20
```

Applications may decode input at different layers:

```text
Browser
 ↓
Reverse Proxy
 ↓
Web Server
 ↓
Framework
 ↓
Application
 ↓
Shell
```

Determine which layer performs decoding.

---

# Double Encoding

Multiple decoding layers may introduce unexpected behaviour.

Conceptually:

```text
%3B
```

represents:

```text
;
```

while:

```text
%253B
```

may become `%3B` after one decoding stage and `;` after another.

Do not assume that the value observed in Burp is exactly what reaches the eventual sink.

---

# Command Injection Through File Names

File names are frequently passed to external utilities.

Examples:

```text
Image conversion
PDF conversion
Archive creation
Archive extraction
Antivirus scanning
Media processing
Document processing
Backup operations
```

A flow might look like:

```text
Upload
  ↓
File Name Stored
  ↓
Processing Worker
  ↓
External Program
  ↓
File Name Used as Argument
```

This can introduce:

```text
Command injection
Argument injection
Option injection
```

Start with harmless file names that reveal how special characters are processed.

---

# Command Injection Through URLs

Applications may pass URLs to utilities such as:

```text
curl
wget
ffmpeg
git
custom downloaders
```

Example functionality:

```text
Import from URL
Webhook validation
Image fetch
Repository clone
Remote document processing
```

These locations may overlap with SSRF testing.

The underlying issue depends on where the user-controlled URL ultimately goes.

---

# HTTP Headers

HTTP headers can occasionally reach operating system commands through:

```text
Logging utilities
Monitoring scripts
Administrative tools
Automation
Custom shell scripts
CI/CD pipelines
```

Interesting headers can include:

```text
User-Agent
Referer
X-Forwarded-For
X-Forwarded-Host
X-Real-IP
Custom application headers
```

Start with a harmless marker:

```http
User-Agent: AM-CMD-987654
```

Determine where it travels before performing further testing.

---

# JSON Command Injection

Modern APIs commonly receive JSON.

Example:

```http
POST /api/diagnostics HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "host": "127.0.0.1"
}
```

Test each controllable property independently.

For example:

```text
host
url
file
path
format
command
repository
destination
```

Do not assume JSON prevents command injection.

---

# Command Injection in APIs

Potentially interesting API functionality includes:

```text
Diagnostics
File conversion
PDF generation
Export
Import
Repository operations
Backup
System health checks
Image processing
Network utilities
```

Map:

```text
Endpoint
 ↓
Parameter
 ↓
Application Function
 ↓
Potential External Process
```

---

# Burp Suite Workflow

Burp Suite is ideal for controlled command injection testing.

```text
Proxy
  ↓
HTTP History
  ↓
Identify Interesting Function
  ↓
Send to Repeater
  ↓
Establish Baseline
  ↓
Test One Character
  ↓
Compare Response
  ↓
Test Execution Hypothesis
  ↓
Confirm Safely
```

---

# Burp Repeater

For each interesting parameter:

```text
1. Send the original request

2. Record baseline behaviour

3. Insert a unique marker

4. Test individual metacharacters

5. Observe validation and errors

6. Determine likely execution context

7. Perform minimal command execution validation

8. Repeat to confirm
```

Avoid changing several variables simultaneously.

---

# Burp Intruder

Intruder can help determine how the application handles command-related characters.

Example payload position:

```http
POST /api/ping HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

host=127.0.0.1§PAYLOAD§
```

A small payload set might contain:

```text
;
|
&
'
"
`
$
(
)
```

Compare:

```text
Status
Length
Words
Lines
Response time
```

Interesting outliers can then be investigated manually in Repeater.

---

# Burp Collaborator Workflow

For suspected blind command injection:

```text
Repeater
   ↓
Create Collaborator Payload
   ↓
Insert Controlled Interaction
   ↓
Send Request
   ↓
Poll Collaborator
   ↓
Interaction Received?
   ↓
Correlate
   ↓
Reproduce
```

Use unique callback identifiers for each test location.

---

# Commix

Commix, short for **Command Injection Exploiter**, is an automated tool for detecting and testing command injection vulnerabilities.

Project:

https://github.com/commixproject/commix

Commix can complement manual Burp Suite testing when a parameter appears likely to reach an operating system command.

The preferred workflow is:

```text
Manual Discovery
       ↓
Burp Repeater
       ↓
Suspicious Parameter
       ↓
Commix
       ↓
Review Detection
       ↓
Manual Verification
       ↓
Minimal Evidence
       ↓
Report
```

Do not use automation as a substitute for understanding the affected request.

---

## Install Commix

Clone the official repository:

```bash
git clone https://github.com/commixproject/commix.git
```

Enter the directory:

```bash
cd commix
```

Check the available options:

```bash
python3 commix.py --help
```

The repository can later be updated with:

```bash
git pull
```

---

## Basic Commix Testing

For an authorised target with a query parameter:

```bash
python3 commix.py \
  --url="https://target.example/ping?host=127.0.0.1"
```

Commix can then analyse the request for command injection behaviour.

When multiple parameters exist, focus testing on the parameter that has already been identified as interesting during manual analysis.

---

## Commix With POST Data

For an authorised POST endpoint:

```bash
python3 commix.py \
  --url="https://target.example/api/ping" \
  --data="host=127.0.0.1"
```

This can be useful for:

```text
Forms
API requests
Diagnostic functions
Administrative functions
File-processing requests
```

---

## Commix With Cookies

Authenticated functionality may require session cookies.

Conceptually:

```bash
python3 commix.py \
  --url="https://target.example/ping?host=127.0.0.1" \
  --cookie="session=YOUR_SESSION_COOKIE"
```

Use your authorised assessment session.

Avoid placing real credentials or session values in documentation, screenshots, or repositories.

---

## Commix With Headers

Applications may require custom headers.

For example, APIs may require:

```text
Authorization
Content-Type
X-CSRF-Token
Custom application headers
```

Review Commix's current help output for the supported header options:

```bash
python3 commix.py --help
```

This is preferable to assuming command-line options remain unchanged between releases.

---

## Commix and Burp Suite

A useful workflow is:

```text
Browser
   ↓
Burp Proxy
   ↓
HTTP History
   ↓
Interesting Request
   ↓
Burp Repeater
   ↓
Manual Analysis
   ↓
Commix
   ↓
Manual Verification
```

Burp should generally be used first to understand:

```text
Endpoint
Method
Parameter
Authentication
Headers
Cookies
Request body
Normal response
```

Automation becomes significantly more useful after this context is known.

---

## Commix and Blind Command Injection

Automated tooling can also help investigate suspected blind command injection.

The overall methodology remains:

```text
Baseline
   ↓
Manual Timing Test
   ↓
Possible Command Execution
   ↓
Commix
   ↓
Compare Detection
   ↓
Manual Confirmation
```

If the application has unstable response times, do not rely solely on automated timing detection.

---

## Commix Results

Do not report a command injection finding solely because Commix reports a potentially injectable parameter.

Verify:

```text
Which endpoint?
Which parameter?
Which technique?
Which operating system?
What behaviour changed?
Can execution be reproduced manually?
What is the actual security impact?
```

The strongest evidence remains a manually reproducible source-to-execution path.

---

# Manual Testing vs Commix

Commix should complement rather than replace manual testing.

Use manual testing for:

```text
Understanding application behaviour
Identifying interesting functionality
Determining parameter context
Character filtering
WAF behaviour
Argument injection
Complex authentication
Second-stage processing
False-positive elimination
Impact validation
```

Use Commix for:

```text
Targeted automated command injection testing
Testing a suspicious parameter
Technique discovery
Confirming manually observed behaviour
Reducing repetitive testing
```

A good combination is:

```text
Manual Understanding
        +
Targeted Commix Testing
        +
Manual Verification
        =
Reliable Finding
```

---

# Recommended Command Injection Tool Workflow

```text
                   Application
                        ↓
                   Burp Proxy
                        ↓
                 HTTP History
                        ↓
             Interesting Function
                        ↓
                  Burp Repeater
                        ↓
               Establish Baseline
                        ↓
               Character Testing
                        ↓
                Suspicious Input?
                        ↓
                 ┌──────┴──────┐
                 │             │
                 ▼             ▼
              Commix      Manual Testing
                 │             │
                 └──────┬──────┘
                        ↓
                 Blind Behaviour?
                        ↓
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
     Burp Collaborator        Interactsh
              │                   │
              └─────────┬─────────┘
                        ↓
                Manual Verification
                        ↓
                Minimal Evidence
                        ↓
                      Report
```

---

# Source Code Review

When source code is available, look for operating system execution APIs.

The general pattern is:

```text
User Input
   ↓
Controller / Route
   ↓
Application Logic
   ↓
Process Execution API
   ↓
Operating System
```

The objective is to trace attacker-controlled data from source to sink.

---

# Python Command Execution Sinks

Interesting Python APIs include:

```python
os.system()
os.popen()
subprocess.run()
subprocess.call()
subprocess.Popen()
subprocess.check_output()
```

Pay particular attention to:

```python
shell=True
```

Example unsafe pattern:

```python
os.system("ping -c 1 " + host)
```

A safer pattern is to avoid the shell:

```python
subprocess.run(
    ["ping", "-c", "1", host],
    shell=False
)
```

Validation should still be applied to `host`.

---

# PHP Command Execution Sinks

Interesting PHP functions include:

```php
system()
exec()
shell_exec()
passthru()
popen()
proc_open()
```

Example unsafe pattern:

```php
system("ping -c 1 " . $_GET["host"]);
```

Trace user-controlled input reaching these functions.

---

# Java Command Execution Sinks

Interesting Java APIs include:

```java
Runtime.getRuntime().exec()
ProcessBuilder
```

Example:

```java
Runtime.getRuntime().exec(command);
```

Determine:

```text
Where does command originate?
Is user input concatenated?
Is a shell explicitly invoked?
Are arguments passed separately?
```

`ProcessBuilder` is not automatically vulnerable. How it is used matters.

---

# .NET Command Execution Sinks

Interesting .NET APIs include:

```text
System.Diagnostics.Process
Process.Start
ProcessStartInfo
```

Review properties such as:

```text
FileName
Arguments
ArgumentList
UseShellExecute
```

Trace attacker-controlled values into process execution.

---

# Node.js Command Execution Sinks

Interesting Node.js APIs include:

```javascript
child_process.exec()
child_process.execSync()
child_process.spawn()
child_process.spawnSync()
child_process.execFile()
```

`exec()` is particularly interesting because it executes a command through a shell.

Example:

```javascript
exec("ping -c 1 " + req.query.host);
```

Prefer APIs that execute a known executable with separately supplied arguments where possible.

---

# Ruby Command Execution Sinks

Interesting Ruby functionality includes:

```text
system
exec
spawn
IO.popen
Backticks
%x{}
```

Trace user-controlled input reaching these operations.

---

# Go Command Execution Sinks

Interesting Go functionality includes:

```go
os/exec
exec.Command()
```

For example:

```go
exec.Command("sh", "-c", userInput)
```

is significantly more dangerous than executing a fixed program with separate controlled arguments.

---

# Search Source Code for Command Execution

A quick first pass can use `grep` or `ripgrep`.

Example:

```bash
grep -RniE \
'os\.system|os\.popen|subprocess|shell=True|Runtime\.getRuntime\(\)\.exec|ProcessBuilder|Process\.Start|child_process|execSync|shell_exec|passthru|proc_open|exec\.Command' \
.
```

With ripgrep:

```bash
rg -n \
'os\.system|os\.popen|subprocess|shell=True|Runtime\.getRuntime\(\)\.exec|ProcessBuilder|Process\.Start|child_process|execSync|shell_exec|passthru|proc_open|exec\.Command'
```

Search results are only potential sinks.

Trace whether user-controlled input reaches them.

---

# Source to Sink Analysis

A useful model is:

```text
SOURCE
  ↓
Request Parameter
  ↓
Controller
  ↓
Validation
  ↓
Transformation
  ↓
Command Construction
  ↓
SINK
  ↓
Process Execution
```

For example:

```text
req.query.host
      ↓
Controller
      ↓
Utility Function
      ↓
String Concatenation
      ↓
child_process.exec()
```

This provides much stronger evidence than merely finding `exec()` somewhere in the source code.

---

# Safe Validation Commands

During authorised testing, use minimal commands that demonstrate execution without changing the system.

Linux examples:

```bash
id
```

```bash
whoami
```

```bash
hostname
```

Windows examples:

```cmd
whoami
```

```cmd
hostname
```

The goal is:

```text
Proof of execution
```

not:

```text
Persistence
Privilege escalation
Data destruction
```

Stop when sufficient evidence exists.

---

# Determine Execution Context

If command execution is confirmed, determine the security context only to the extent required to understand impact.

Potential information includes:

```text
Operating system
Process user
Hostname
Container environment
Application directory
```

For example:

```bash
whoami
```

or:

```bash
id
```

may be sufficient.

Avoid unnecessary enumeration once the vulnerability has been demonstrated.

---

# Containers

Modern applications frequently run inside containers.

Command execution might therefore initially occur inside:

```text
Docker
Kubernetes workload
Container runtime
Application sandbox
```

Command injection inside a container is still a serious vulnerability.

Do not assume:

```text
Container = no impact
```

Impact depends on:

```text
Container privileges
Mounted volumes
Secrets
Network access
Service accounts
Runtime configuration
Host exposure
```

Do not attempt container escape unless explicitly authorised.

---

# WAF Behaviour

A WAF may block common command injection syntax.

Indicators include:

```text
403
406
Connection reset
Generic security page
Different response length
Parameter-specific blocking
```

Separate:

```text
WAF Behaviour
```

from:

```text
Application Behaviour
```

A blocked semicolon does not prove that the underlying command construction is safe.

---

# Input Validation

Applications may allow only specific input formats.

For example, a host parameter might be intended to accept:

```text
IPv4
IPv6
DNS hostnames
```

Strong allowlist validation can substantially reduce risk.

For an IPv4-only field, input should be parsed and validated as an actual IP address rather than treated as an arbitrary string.

---

# False Positives

Potential causes of false positives include:

```text
Normal application latency
Backend timeouts
DNS resolution delays
Input validation
WAF behaviour
Application errors
Rate limiting
Asynchronous processing
Network instability
```

A reliable finding should demonstrate repeatable command-dependent behaviour.

---

# Validation

A strong command injection finding should establish:

```text
SOURCE
  ↓
Affected Input
  ↓
Command Construction
  ↓
Operating System Execution
  ↓
Observable Evidence
  ↓
Security Impact
```

For example:

```text
host parameter
      ↓
Diagnostic endpoint
      ↓
Unsafely constructed ping command
      ↓
Shell execution
      ↓
Controlled timing difference
```

---

# Evidence Collection

Useful evidence includes:

```text
Affected endpoint
HTTP method
Affected parameter
Authentication requirement
Original request
Modified request
Baseline response
Modified response
Response timing
Command output if visible
Callback evidence if used
Commix output if used
Operating system if known
Execution user if necessary
Required privileges
Relevant screenshot
```

Keep evidence minimal.

---

# Command Injection Reporting

A report should explain:

```text
Which input is affected
How the input reaches an operating system command
Whether a shell is involved
How execution was confirmed
What privileges the application process has
What an attacker could achieve
What evidence was collected
How the issue should be remediated
```

---

# Example Finding Structure

```text
Title
OS Command Injection in Network Diagnostic Function

Affected Endpoint
POST /api/diagnostics/ping

Affected Parameter
host

Authentication Required
Yes

Description
The application incorporates the host parameter into an operating
system command without safely separating user-controlled data from
the command structure.

Controlled testing demonstrated that additional operating system
commands could be executed in the context of the application process.

Impact
An attacker with access to the affected functionality may be able
to execute operating system commands with the privileges of the
application service account.

Recommendation
Avoid constructing operating system commands using user-controlled
strings. Invoke the required executable directly with separately
supplied arguments and apply strict allowlist validation to the
host parameter.
```

---

# Remediation

The preferred remediation is:

```text
Do not invoke a shell unless absolutely necessary.
```

Prefer:

```text
Known Executable
      +
Separate Arguments
```

instead of:

```text
Constructed Shell Command String
```

Additional controls include:

```text
Strict allowlist validation
Safe process execution APIs
Argument separation
Least privilege
Container isolation
Application sandboxing
Restricted network access
Secure error handling
Monitoring
```

---

# Avoid Shell Execution

Unsafe conceptual pattern:

```python
os.system("ping -c 1 " + host)
```

Better:

```python
subprocess.run(
    ["ping", "-c", "1", host],
    shell=False
)
```

The input should also be validated as the expected type.

For example, if only IP addresses are expected:

```text
Input
 ↓
IP Address Parser
 ↓
Valid?
 ↓
Pass as Separate Argument
```

---

# Allowlist Validation

If the application expects a particular format, enforce that format.

Examples:

```text
IP address
Hostname
File extension
Known output format
Known command option
```

Avoid relying solely on blocklists such as:

```text
Remove ;
Remove &
Remove |
```

Shell syntax is complex and platform-dependent.

---

# Least Privilege

The application process should run with the minimum permissions required.

Avoid unnecessary:

```text
root
Administrator
SYSTEM
Privileged containers
Writable system directories
Sensitive mounted volumes
Cloud administrative credentials
```

Least privilege does not fix command injection, but it can significantly reduce impact.

---

# Command Injection Testing Checklist

## Discovery

- [ ] Identify diagnostic functionality
- [ ] Identify network utilities
- [ ] Identify file conversion
- [ ] Identify image processing
- [ ] Identify PDF generation
- [ ] Identify archive functionality
- [ ] Identify import/export
- [ ] Identify Git operations
- [ ] Identify backup functionality
- [ ] Identify administrative tools
- [ ] Identify background workers
- [ ] Identify APIs invoking external programs

## Inputs

- [ ] GET parameters
- [ ] POST parameters
- [ ] JSON properties
- [ ] HTTP headers
- [ ] Cookies
- [ ] File names
- [ ] File paths
- [ ] URLs
- [ ] Hostnames
- [ ] IP addresses

## Baseline

- [ ] Record status
- [ ] Record response length
- [ ] Record response time
- [ ] Record normal output
- [ ] Record expected errors

## Character Testing

- [ ] Semicolon
- [ ] Pipe
- [ ] Ampersand
- [ ] Quotes
- [ ] Backticks where relevant
- [ ] Parentheses where relevant
- [ ] Dollar sign where relevant
- [ ] Redirection characters where relevant

## Execution

- [ ] Determine likely operating system
- [ ] Determine whether a shell is involved
- [ ] Test harmless execution
- [ ] Test timing if output is hidden
- [ ] Consider controlled OOB callback
- [ ] Repeat to confirm
- [ ] Determine execution context only if necessary

## Argument Injection

- [ ] Determine whether input becomes an argument
- [ ] Test leading option characters where appropriate
- [ ] Review external utility options
- [ ] Determine whether `--` is supported
- [ ] Distinguish argument injection from shell injection

## Burp

- [ ] Proxy
- [ ] Repeater
- [ ] Intruder where useful
- [ ] Collaborator for OOB testing
- [ ] Compare responses
- [ ] Record timing

## Automation

- [ ] Understand the request manually first
- [ ] Identify the suspected parameter
- [ ] Test with Commix where appropriate
- [ ] Preserve required authentication
- [ ] Review automated findings
- [ ] Compare automated results with manual observations
- [ ] Manually reproduce the vulnerability
- [ ] Do not report solely from automated output

## Source Review

- [ ] Search Python process APIs
- [ ] Search PHP command functions
- [ ] Search Java process APIs
- [ ] Search .NET Process APIs
- [ ] Search Node.js child_process
- [ ] Search Ruby execution APIs
- [ ] Search Go os/exec
- [ ] Trace source to sink
- [ ] Look for string concatenation
- [ ] Look for shell invocation

## Validation

- [ ] Confirm repeatability
- [ ] Exclude network latency
- [ ] Exclude WAF behaviour
- [ ] Exclude normal application timeout
- [ ] Use minimal proof
- [ ] Stop after sufficient evidence
- [ ] Capture request and response
- [ ] Record callback evidence if applicable
- [ ] Record Commix evidence if applicable

---

# Useful Tools

| Tool | Purpose |
|---|---|
| Burp Suite | HTTP interception and manual testing |
| Burp Repeater | Controlled command injection testing |
| Burp Intruder | Character and parameter testing |
| Burp Collaborator | Out of band interaction detection |
| Commix | Automated command injection detection and testing |
| Interactsh | Controlled out of band interaction detection |
| curl | Manual HTTP requests |
| Browser DevTools | Client and API analysis |
| grep | Source code sink discovery |
| ripgrep | Fast source code searching |
| Semgrep | Pattern based source code analysis |

---

# Tool Selection

A practical way to select tooling is:

| Situation | Tool |
|---|---|
| Understand the request | Burp Proxy |
| Manual parameter testing | Burp Repeater |
| Test multiple characters | Burp Intruder |
| Automated command injection testing | Commix |
| Blind interaction testing | Burp Collaborator |
| External OOB interaction testing | Interactsh |
| Reproduce HTTP requests | curl |
| Source code sink discovery | grep / ripgrep |
| Structured source analysis | Semgrep |

The tooling should follow the methodology rather than determine it.

---

# Quick Reference

```text
Interesting functionality:

Ping
DNS lookup
Traceroute
File conversion
Image processing
PDF generation
Archives
Backup
Git
Import/export
System administration

Interesting sinks:

Python      → os.system, subprocess
PHP         → system, exec, shell_exec
Java        → Runtime.exec, ProcessBuilder
.NET        → Process.Start
Node.js     → child_process
Ruby        → system, exec, spawn
Go          → os/exec

Manual Testing:

Burp Proxy
Burp Repeater
Burp Intruder

Automation:

Commix

Blind Testing:

Burp Collaborator
Interactsh

Validation:

Visible Output
      OR
Reliable Timing
      OR
Controlled OOB Interaction

Always establish:

INPUT → COMMAND CONSTRUCTION → PROCESS/SHELL → EXECUTION → IMPACT
```

---

# Practical Workflow Summary

```text
                    ┌─────────────────────┐
                    │ Identify Function   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Identify Input    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Establish Baseline  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Character Testing   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ OS / Shell Analysis │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Manual Confirmation │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Commix if Useful    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Blind / OOB Testing │
                    │     if Required     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Manual Verification │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Minimal Evidence    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Report        │
                    └─────────────────────┘
```

---

# References

## PortSwigger Web Security Academy

### OS Command Injection

https://portswigger.net/web-security/os-command-injection

PortSwigger provides methodology and practical labs covering visible and blind OS command injection.

---

## OWASP

### OS Command Injection Defense Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html

Defensive guidance covering command injection, argument injection, safe APIs and parameterisation.

### Web Security Testing Guide

https://owasp.org/www-project-web-security-testing-guide/

The Web Security Testing Guide contains broader methodology for testing injection vulnerabilities.

---

## Commix

### Command Injection Exploiter

https://github.com/commixproject/commix

Commix is an automated command injection detection and exploitation tool.

Use it as a complement to manual Burp Suite testing rather than as a replacement for understanding and manually validating the vulnerability.

---

## PayloadsAllTheThings

### Command Injection

https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Command%20Injection

Useful reference covering command injection syntax across operating systems and different execution contexts.

Use payload collections after understanding the affected execution context rather than blindly sending every payload.

---

## HackTricks

### Command Injection

https://book.hacktricks.wiki/en/pentesting-web/command-injection.html

Additional practical reference covering command injection behaviour and operating system differences.

---

## Interactsh

### ProjectDiscovery Interactsh

https://github.com/projectdiscovery/interactsh

Useful for detecting controlled out of band interactions during authorised security testing.

---

## Burp Collaborator

### PortSwigger Burp Collaborator

https://portswigger.net/burp/documentation/collaborator

Useful for detecting DNS, HTTP and other out of band interactions from applications being tested.

---

# Related Notes

```text
Web Application Security
├── Methodology
├── Pentesting Checklist
├── Reconnaissance
│   ├── Subdomain Enumeration
│   ├── Technology Identification
│   ├── Content Discovery
│   ├── Parameter Discovery
│   └── JavaScript Analysis
├── Authentication
├── Authorisation
├── Session Management
├── Burp Suite
│   ├── Extensions
│   └── Testing Workflows
├── Cross-Site Scripting
├── SQL Injection
└── OS Command Injection
```

The methodology, technology identification, parameter discovery and Burp Suite workflow notes are particularly useful before command injection testing.
