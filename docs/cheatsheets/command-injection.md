---
title: Command Injection Cheatsheet
description: Practical OS command injection cheatsheet for authorised web application security testing covering discovery, shell metacharacters, blind command injection, argument injection, operating system differences, Burp Suite, source code review, evidence, remediation and retesting.
---

# Command Injection Cheatsheet

OS command injection occurs when attacker-controlled input reaches an operating-system command execution mechanism without being safely separated from the command itself.

A simplified vulnerable flow is:

```text
User Input
    |
    v
Application
    |
    v
Command String
    |
    v
Shell
    |
    v
Operating System
```

Example concept:

```text
User supplies:
example.com

Application builds:
ping -c 1 example.com
```

If the application constructs a shell command directly from user input, the security boundary becomes:

```text
DATA
 |
 v
COMMAND STRING
```

The important question is:

```text
Can attacker-controlled data change the structure or meaning
of the command executed by the operating system?
```

!!! warning "Authorised Security Testing"

    Perform command injection testing only against systems explicitly included in the assessment scope. Start with harmless commands that produce deterministic output or short timing changes. Do not use reverse shells, persistence, destructive commands, credential access or system modification simply to prove command execution.


# Quick Reference

## Common Candidate Parameters

```text
host

hostname

ip

address

domain

url

path

file

filename

directory

interface

command

cmd

query

target

destination

server
```


## Common Candidate Features

```text
Ping tools

DNS lookup

Traceroute

Network diagnostics

File conversion

Image processing

PDF generation

Backup functions

Archive functions

Git integrations

Administrative utilities

Monitoring

Import/export

Video processing
```


## Common Shell Metacharacters

Unix-like shells may interpret characters such as:

```text
;

|

||

&&

&

$

`

>

<
```

Windows command processing has different semantics and must be tested according to the actual execution environment.


# Command Injection Testing Model

Do not use:

```text
Parameter contains "host"
        |
        v
Command Injection
```

Use:

```text
Input
  |
  v
Application Function
  |
  v
OS Command?
  |
  v
Shell Involved?
  |
  v
User Data Reaches Command?
  |
  v
Can Command Structure Change?
  |
  v
Observable Execution
```


# Command Injection vs Argument Injection

These are related but different.


## Command Injection

Command injection changes the command structure.

Conceptually:

```text
Expected:

tool USER_INPUT
```

becomes:

```text
tool value ; second-command
```


## Argument Injection

Argument injection occurs when attacker-controlled data remains part of the intended process invocation but introduces unintended command-line options.

Conceptually:

```text
tool USER_INPUT
```

becomes:

```text
tool --unexpected-option
```

No second shell command is necessarily required.


# Shell vs Direct Process Execution

This distinction is extremely important.

## Shell Execution

Conceptually:

```text
Application
    |
    v
/bin/sh -c "command USER_INPUT"
```

The shell interprets metacharacters.


## Direct Process Execution

Conceptually:

```text
Application
    |
    v
execve()
    |
    v
["command", "USER_INPUT"]
```

There may be no shell parsing.

This substantially reduces classic shell injection risk, although argument injection may still be relevant.


# First Question: Is an OS Command Used?

Do not assume a network diagnostic feature necessarily calls:

```text
ping
```

The application may use:

```text
Native networking library

Framework API

DNS library

HTTP client
```

Source review is especially valuable here.


# Establish a Baseline

Suppose the application exposes:

```http
POST /api/diagnostics HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "host": "127.0.0.1"
}
```


# Baseline Response

Representative result:

```text
PING 127.0.0.1
64 bytes from 127.0.0.1
```

This suggests that a system utility may be involved.

It does not prove command injection.


# Record the Baseline

Capture:

```text
Endpoint

Method

Parameter

Authentication context

Input

Response status

Response body

Response time
```


# Determine the Operating System

Useful indicators include:

```text
Response format

Error messages

Path syntax

Server headers

Source code

Application stack

Known deployment environment
```


# Do Not Guess OS From One String

A Linux-hosted application could call a Windows service and vice versa.

Use multiple pieces of evidence.


# Harmless Marker Commands

Where command execution testing is authorised, use commands with minimal impact.


# Unix-Like Systems

Examples of low-impact commands include:

```bash
id
```

```bash
whoami
```

```bash
printf CMD_TEST_7f3a9
```


# Windows

Low-impact examples include:

```cmd
whoami
```

or:

```cmd
echo CMD_TEST_7f3a9
```


# Prefer Unique Markers

A marker such as:

```text
CMD_TEST_7f3a9
```

makes response correlation easier.


# Basic Unix Shell Separators

A semicolon can separate commands in many Unix-like shells:

```text
;
```

Conceptually:

```text
expected-command input ; harmless-command
```


# Logical AND

```text
&&
```

The second command normally executes only if the first succeeds.


# Logical OR

```text
||
```

The second command normally executes if the first command fails.


# Pipe

```text
|
```

The output of one command can become input to another.


# Background Operator

```text
&
```

Shell behaviour varies depending on placement and environment.


# Newline

A newline can sometimes separate commands when the input reaches a shell.

Encoding may be relevant when the input travels through HTTP parameters.


# Controlled Testing Principle

Start with:

```text
One operator

One harmless marker

One request
```

Do not spray dozens of command separators before understanding the application.


# Example Controlled Test

Baseline input:

```text
127.0.0.1
```

Candidate concept:

```text
127.0.0.1 ; printf CMD_TEST_7f3a9
```


# Representative Positive Response

```text
PING 127.0.0.1
...

CMD_TEST_7f3a9
```


# Interpretation

If the unique marker appears because the second command executed, this provides strong evidence that attacker-controlled input changed the shell command structure.


# Repeat the Test

Use another unique marker:

```text
CMD_TEST_91bc2
```

A repeatable result reduces ambiguity.


# Command Substitution

Unix-like shells may support command substitution using:

```text
$(...)
```

and, in some shells:

```text
`...`
```


# Example Concept

```text
value$(printf CMD_TEST_7f3a9)
```


# Applicability

Command substitution matters only if the user input reaches a shell that supports the syntax.


# Do Not Assume Bash

The application may invoke:

```text
/bin/sh

dash

bash

zsh

busybox sh

another shell
```


# Quoting Context

Input may appear inside:

```text
Unquoted argument

Single quotes

Double quotes

Command substitution

Environment variable
```

Understanding the surrounding command matters.


# Example Unquoted Context

Application:

```text
ping -c 1 USER_INPUT
```


# Example Double-Quoted Context

Application:

```text
ping -c 1 "USER_INPUT"
```


# Example Single-Quoted Context

Application:

```text
ping -c 1 'USER_INPUT'
```


# Why Context Matters

Different shell characters have different meaning depending on quoting.


# White-Box Review

If source is available, determine the exact command construction rather than blindly trying payload variations.


# Blind Command Injection

Sometimes the command executes but its output is not returned.

Model:

```text
Input
  |
  v
OS Command
  |
  v
Execution
  |
  X
No Output Returned
```


# Blind Validation Methods

Common low-impact methods include:

```text
Timing

Controlled DNS callback

Controlled HTTP callback
```

Use only assessment-controlled infrastructure.


# Timing Validation

A short controlled delay can demonstrate execution when response content is unavailable.

Conceptually:

```text
Baseline:
~200 ms

Candidate:
~3 seconds
```


# Timing Evidence Requires Repetition

Network latency varies.

Use:

```text
Multiple baseline requests

Multiple candidate requests

Consistent timing difference
```


# Do Not Use Excessive Delays

A few seconds is usually sufficient.

Avoid long sleeps that consume application workers unnecessarily.


# Timing Test Model

```text
Baseline
   |
   v
Measure
   |
   v
Short Delay Candidate
   |
   v
Measure
   |
   v
Repeat
```


# Timing Is Supporting Evidence

A single slow request does not prove command execution.

Possible alternatives include:

```text
Network latency

Backend timeout

Rate limiting

Database delay

Application load
```


# Out-of-Band Validation

Where authorised, a command may cause a harmless lookup or request to assessment-controlled infrastructure.


# OOB Model

```text
Application
    |
    v
OS Command
    |
    v
Controlled Domain
```


# Use Unique Identifiers

Example:

```text
cmd-7f3a9.assessment.example
```

Then repeat with:

```text
cmd-91bc2.assessment.example
```


# DNS vs HTTP

DNS interaction supports:

```text
Hostname resolution occurred.
```

HTTP interaction provides evidence that an HTTP client or command reached the controlled server.

Determine which process actually caused the interaction.


# Do Not Overclaim OOB Evidence

A DNS callback alone does not necessarily establish:

```text
Interactive shell access

Arbitrary file read

Privilege escalation
```


# Windows Command Processing

Windows applications may invoke:

```text
cmd.exe

PowerShell

Direct process APIs
```


# `cmd.exe`

Common command separators include:

```text
&

&&

||
```

Exact behaviour depends on command context.


# PowerShell

PowerShell has its own parsing and command semantics.

Do not assume that a payload designed for:

```text
cmd.exe
```

will behave identically in:

```text
powershell.exe

pwsh.exe
```


# Determine the Interpreter

Source or process information may reveal:

```text
cmd.exe /c

powershell.exe -Command

/bin/sh -c

bash -c
```


# Command Injection vs PowerShell Injection

If attacker-controlled input is inserted into a PowerShell script or command string, analyse the PowerShell parsing context specifically.


# Environment Variables

Shell commands may use environment variables.

Unix examples:

```text
$PATH

$HOME
```

Windows examples:

```text
%PATH%

%TEMP%
```

PowerShell:

```text
$env:PATH
```

Do not use environment manipulation unless it is relevant to the actual source-to-sink flow.


# PATH Resolution

A process invocation using:

```text
tool
```

rather than:

```text
/usr/bin/tool
```

may depend on `PATH`.

This can create separate execution risks in certain local or privileged contexts.

It is not automatically remote command injection.


# Argument Injection

Consider:

```text
Application executes:
tool USER_INPUT
```

If the process is launched safely without a shell, an input beginning with:

```text
-
```

may still be interpreted as a command-line option by the called program.


# Example Concept

```text
tool --unexpected-option
```


# Argument Injection Questions

Ask:

```text
Does the program accept dangerous options?

Can options specify files?

Can options specify configuration?

Can options trigger network requests?

Can options execute helper programs?
```


# End-of-Options Marker

Many Unix utilities support:

```text
--
```

to mark the end of command-line options.

Example concept:

```text
tool -- USER_INPUT
```

This can help prevent attacker-controlled values from being interpreted as options when supported by the utility.


# Do Not Assume Every Tool Supports `--`

Verify the called program's documentation.


# Input Validation

If a parameter should contain an IP address, validate it as an IP address.

Do not merely remove:

```text
;

|

&
```


# Example Business Constraint

Expected:

```text
IPv4 or IPv6 address
```

Then the application should parse the input as an IP address rather than attempt to sanitise arbitrary shell syntax.


# Allowlist Model

```text
User Input
    |
    v
Parse Expected Data Type
    |
    +--> Valid -> Continue
    |
    +--> Invalid -> Reject
```


# Shell Escaping

Shell escaping is difficult to implement correctly across:

```text
Shells

Platforms

Quoting contexts

Encodings
```

The preferred remediation is usually:

```text
Do not invoke a shell.
```


# Direct Process Invocation

Preferred:

```text
Application
    |
    v
Executable + Argument Array
    |
    v
Operating System
```

rather than:

```text
Application
    |
    v
String Concatenation
    |
    v
Shell
```


# Python Vulnerable Pattern

```python
import os

host = request.args.get("host")

os.system("ping -c 1 " + host)
```


# Source-to-Sink

```text
request.args["host"]
        |
        v
String Concatenation
        |
        v
os.system()
```


# Python Search

```bash
rg -ni 'os\.system|os\.popen|subprocess\.|commands\.' -g '*.py' .
```


# Python `shell=True`

High-priority candidate:

```python
subprocess.run(
    command,
    shell=True
)
```


# Search

```bash
rg -n -C 5 'shell\s*=\s*True' -g '*.py' .
```


# Safer Python Pattern

Prefer an argument list:

```python
subprocess.run(
    ["/usr/bin/ping", "-c", "1", host],
    check=True
)
```

with strict validation of `host`.


# Important

Using an argument array substantially reduces shell injection risk because the input is passed as an argument rather than interpreted by a shell.

Argument-specific risks should still be considered.


# Node.js Child Processes

Common APIs include:

```text
exec()

execSync()

spawn()

spawnSync()

execFile()

execFileSync()
```


# Node.js Search

```bash
rg -ni 'child_process|exec\(|execSync|spawn\(|spawnSync|execFile' -g '*.js' -g '*.ts' .
```


# Node.js High-Risk Pattern

```javascript
exec("ping -c 1 " + req.query.host);
```


# Source-to-Sink

```text
req.query.host
      |
      v
String Concatenation
      |
      v
exec()
```


# Node.js Safer Pattern

Conceptually:

```javascript
spawn("/usr/bin/ping", ["-c", "1", host]);
```

with validation of `host`.


# `exec` vs `spawn`

The important question is not simply which API name appears.

Review whether:

```text
A shell is invoked

A command string is built

Arguments are passed separately
```


# Java Command Execution

Common APIs:

```text
Runtime.getRuntime().exec()

ProcessBuilder
```


# Java Search

```bash
rg -ni 'Runtime\.getRuntime\(\)\.exec|ProcessBuilder' -g '*.java' .
```


# Java Candidate

```java
Runtime.getRuntime().exec(
    "ping " + host
);
```


# ProcessBuilder

A safer structure generally passes arguments separately:

```java
new ProcessBuilder(
    "ping",
    "-c",
    "1",
    host
);
```

The application must still validate the intended data type and consider argument injection.


# .NET Process Execution

Common APIs include:

```text
Process.Start

ProcessStartInfo
```


# .NET Search

```bash
rg -ni 'Process\.Start|ProcessStartInfo' -g '*.cs' .
```


# Candidate

```csharp
var psi = new ProcessStartInfo();
psi.FileName = "/bin/sh";
psi.Arguments = "-c \"ping " + host + "\"";
```


# High-Risk Signal

Look for:

```text
cmd.exe /c

powershell.exe

pwsh.exe

/bin/sh -c

bash -c
```

combined with attacker-controlled strings.


# PHP Command Execution

Potential sinks include:

```text
system()

exec()

shell_exec()

passthru()

popen()

proc_open()
```


# PHP Search

```bash
rg -ni 'system\(|exec\(|shell_exec|passthru|popen|proc_open' -g '*.php' .
```


# PHP Candidate

```php
system("ping -c 1 " . $_GET["host"]);
```


# PHP Source-to-Sink

```text
$_GET["host"]
      |
      v
Concatenation
      |
      v
system()
```


# Ruby Command Execution

Potential sinks include:

```text
system()

exec()

Open3

backticks
```


# Search

```bash
rg -ni 'system\(|exec\(|Open3|IO\.popen' -g '*.rb' .
```


# Go Command Execution

Go commonly uses:

```text
os/exec
```


# Search

```bash
rg -ni 'os/exec|exec\.Command|exec\.CommandContext' -g '*.go' .
```


# Go Safer Pattern

```go
exec.Command(
    "/usr/bin/ping",
    "-c",
    "1",
    host,
)
```

This passes arguments separately rather than using a shell command string.


# Dangerous Go Pattern

A high-risk design may explicitly invoke:

```text
sh -c
```

with user-controlled command content.


# Search Shell Invocation

```bash
rg -ni 'sh.*-c|bash.*-c|cmd\.exe|powershell' .
```


# Generic Source Review Search

```bash
rg -ni 'exec|system|shell|spawn|ProcessBuilder|ProcessStartInfo|os\.system|subprocess|child_process' src/
```


# Search With Context

```bash
rg -n -C 8 'os\.system|shell=True|child_process|ProcessBuilder|ProcessStartInfo|shell_exec|exec\.Command' src/
```


# Source Review Workflow

```text
Find Command Sink
      |
      v
Identify Executable
      |
      v
Shell Involved?
      |
      v
Identify Arguments
      |
      v
Trace User Input
      |
      v
Validation?
      |
      v
Can Structure Change?
      |
      v
Can Arguments Change Meaning?
```


# High-Priority Source Pattern

```text
HTTP Input
    |
    v
String Concatenation
    |
    v
Shell Command
```


# Lower-Risk Pattern

```text
HTTP Input
    |
    v
Strict Data Validation
    |
    v
Argument Array
    |
    v
Direct Process API
```


# Burp Suite Workflow

```text
Proxy
  |
  v
Identify Candidate Parameter
  |
  v
Send to Repeater
  |
  v
Baseline
  |
  v
Harmless Marker
  |
  +--> Output?
  |
  +--> Timing?
  |
  +--> OOB?
  |
  v
Repeat
  |
  v
Evidence
```


# Repeater Baseline

```http
POST /api/diagnostics HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "host": "127.0.0.1"
}
```


# Controlled Modification

Conceptually:

```json
{
  "host": "127.0.0.1 ; printf CMD_TEST_7f3a9"
}
```

Use syntax appropriate to the confirmed environment.


# Compare Responses

Record:

```text
Status

Length

Body

Timing

Errors
```


# Burp Comparer

Useful when candidate responses differ subtly from baseline.


# Burp Intruder

Intruder can test a small controlled set of separators or input positions.

Do not use a huge command injection payload list by default.


# Collaborator

For blind command injection, Burp Collaborator can provide controlled OOB evidence where outbound interaction testing is authorised.


# OOB Correlation

Use a different identifier for every request.

Example concept:

```text
cmd-001

cmd-002

cmd-003
```


# curl Baseline

```bash
curl -i \
  -H 'Content-Type: application/json' \
  --data '{"host":"127.0.0.1"}' \
  'https://target.example/api/diagnostics'
```


# Shell Quoting Warning

When testing command syntax through curl, your local shell may interpret characters before curl sends them.

Use appropriate quoting so the intended bytes reach the target.


# Inspect Exact Request

Burp Suite is often easier for command injection testing because the request can be edited without local shell interpretation.


# URL Parameters

Example:

```bash
curl -i \
  --get \
  --data-urlencode 'host=127.0.0.1' \
  'https://target.example/diagnostics'
```


# URL Encoding

When testing metacharacters in query parameters, using:

```text
--data-urlencode
```

can help ensure they are transmitted as parameter data.


# Error Messages

Command-related errors can provide useful clues.

Examples:

```text
command not found

unknown option

invalid argument

No such file or directory

The system cannot find the file specified
```


# Shell Error

An error mentioning:

```text
sh

bash

cmd.exe

PowerShell
```

may help identify the execution context.


# Utility Error

Example:

```text
ping: invalid option
```

may indicate that user input reached the command as an argument.

This can support argument-injection analysis.


# Error Does Not Equal Exploitability

An unexpected utility error proves only that input influenced program behaviour.

Determine whether the influence crosses a meaningful security boundary.


# Input Filtering

Applications may block specific characters.

Examples:

```text
;

|

&
```


# Character Blocking Is Not Root-Cause Remediation

A blacklist may be bypassable through:

```text
Different syntax

Different interpreter behaviour

Encoding

Alternative execution paths
```

The preferred control is to avoid shell interpretation.


# Whitespace

Shells support several ways of separating tokens.

Do not build a finding around bypass tricks unless the underlying unsafe command construction has been established.


# Encoding Layers

Input may pass through:

```text
URL decoder

JSON parser

Framework

Application validation

Shell
```

Understand where transformations occur.


# Double Encoding

Do not automatically try double encoding.

Use it when architecture suggests multiple decoding stages.


# Command Injection in File Names

File-processing functions may invoke external utilities with uploaded filenames.

Example flow:

```text
Uploaded Filename
       |
       v
Image Converter Command
       |
       v
Shell
```


# Review Uploaded Filenames

Source code may contain:

```text
convert " + filename

ffmpeg ... " + filename

unzip " + filename
```


# Safer Design

Use:

```text
Generated storage filename

Argument array

No shell
```


# Command Injection in Git Integrations

Applications may execute utilities such as:

```text
git
```

for repository operations.

Review whether attacker-controlled:

```text
Repository name

Branch

Path

URL

Commit reference
```

becomes command-line input.


# Command Injection in Backup Features

Potential commands include:

```text
tar

zip

gzip

database dump utilities
```

Review all user-controlled arguments.


# Command Injection in Network Tools

Common utilities include:

```text
ping

traceroute

nslookup

dig

curl

wget
```

A network diagnostics feature should ideally use native APIs rather than constructing shell commands.


# Command Injection in Media Processing

Potential utilities:

```text
ffmpeg

ImageMagick

GraphicsMagick
```

Review both:

```text
Command construction

Parser vulnerabilities
```

as separate attack surfaces.


# Command Injection in PDF Generation

Applications sometimes invoke external document converters.

Potential architecture:

```text
User Input
   |
   v
Document Generator
   |
   v
Command-Line Converter
```


# Command Injection in Admin Interfaces

Administrative functionality may expose powerful system-management operations.

Authentication does not make unsafe command construction acceptable.


# Privilege Context

Determine which account executes the command.

Examples:

```text
www-data

app

nginx

IIS application pool identity

container user

service account
```


# Do Not Assume Root

Command injection typically executes with the privileges of the application process.


# Container Context

If the application runs in a container:

```text
Command Injection
      |
      v
Container Process
```

This does not automatically mean:

```text
Host Command Execution
```


# Container Impact

Still assess:

```text
Mounted secrets

Mounted volumes

Network access

Service credentials

Container privileges
```


# Cloud Environment

Command execution inside a cloud workload may expose additional resources depending on:

```text
Workload identity

Instance role

Managed identity

Network access

Mounted credentials
```

Do not access cloud credentials unless explicitly authorised.


# Privilege Escalation Is Separate

A command injection finding should normally establish:

```text
Application-level OS command execution
```

You do not need to escalate privileges to prove it.


# Do Not Add Persistence

Persistence is not required for command injection validation.


# Do Not Deploy Reverse Shells by Default

A reverse shell usually adds little evidentiary value once arbitrary command execution has been safely demonstrated.

Prefer:

```text
Unique marker

Identity command

Controlled timing

Controlled callback
```


# False Positive - Reflection

Input:

```text
; CMD_TEST_7f3a9
```

may simply be reflected in the response.

That does not prove command execution.


# False Positive - Validation Error

A response such as:

```text
Invalid host: ; CMD_TEST_7f3a9
```

shows input handling, not execution.


# False Positive - Timing

One slow request is not sufficient evidence.


# False Positive - OOB Callback

Ensure the callback originated from the command execution path rather than:

```text
URL validation

Application HTTP client

Security scanner

Monitoring component
```


# False Positive - Scanner Alert

Automated scanner findings require manual validation.


# False Positive - Source Sink Without Reachability

Source review may reveal:

```text
os.system(command)
```

but the command may use only trusted constants.

Trace actual attacker control.


# False Positive - Shell-Looking Code

Example:

```python
subprocess.run(
    ["/usr/bin/tool", trusted_value]
)
```

is not equivalent to:

```python
subprocess.run(
    "/usr/bin/tool " + user_value,
    shell=True
)
```


# Evidence Collection

Capture:

```text
Finding ID

Endpoint

Method

Parameter

Authentication context

Baseline input

Candidate input

Operating system evidence

Interpreter evidence

Unique marker

Response output

Response timing

OOB interaction

Timestamp

Application privilege context if known
```


# Strong Output-Based Evidence

```text
1. Establish baseline.

2. Submit harmless second command.

3. Unique marker appears in response.

4. Repeat with different marker.

5. Stop.
```


# Strong Blind Evidence

```text
1. Establish timing baseline.

2. Submit short-delay candidate.

3. Observe repeatable delay.

4. Repeat baseline.

5. Repeat candidate.

6. Optionally correlate controlled OOB interaction.

7. Stop.
```


# Evidence Should Demonstrate Causality

The goal is:

```text
Specific Input
     |
     v
Specific Execution Effect
     |
     v
Repeatable Observation
```


# Reporting Example - Output-Based Command Injection

> The `host` parameter in the network diagnostics endpoint is incorporated into an operating-system command that is executed through a shell. During testing, a harmless command separator followed by a unique marker command caused the marker `CMD_TEST_7f3a9` to appear in the application response. Repeating the test with a second unique marker produced the corresponding output, confirming OS command injection.


# Reporting Example - Blind Command Injection

> The diagnostics endpoint incorporates attacker-controlled input into an operating-system command. Command output is not returned directly; however, introducing a short controlled delay caused a repeatable increase in response time compared with baseline requests. The behaviour was reproduced across multiple requests, supporting blind OS command injection.


# Reporting Example - OOB Command Injection

> A unique command-injection test caused the application environment to initiate a correlated request to assessment-controlled infrastructure. The interaction used a unique per-request identifier and was reproduced with a second identifier, confirming that attacker-controlled input reaches an operating-system command execution path.


# Reporting Example - Argument Injection

> The application invokes the external utility using attacker-controlled input as a command-line argument without restricting option-like values. Although no shell command separator was required, user input could introduce unintended options to the invoked utility. The demonstrated impact is therefore command-line argument injection rather than classic shell command injection.


# Reporting Example - Source Review

> User-controlled input from the `host` request parameter is concatenated into a command string passed to `os.system()`. No strict host validation or argument separation is performed before execution. This creates an OS command injection path because the shell interprets attacker-controlled command syntax.


# Remediation - Avoid Shell Execution

The preferred remediation is:

```text
Do not construct shell commands from user input.
```


# Use Native APIs

Instead of:

```text
Application
    |
    v
ping command
```

consider:

```text
Application
    |
    v
Networking library
```


# Use Argument Arrays

If an external executable is genuinely required:

```text
Executable

Argument 1

Argument 2

User Value
```

should be passed separately through a direct process API.


# Avoid

```text
"command " + user_input
```


# Prefer

Conceptually:

```text
["command", "fixed-argument", validated_user_value]
```


# Strict Data Validation

Validate according to business meaning.

Examples:

```text
IP address -> parse as IP address

Port -> integer within allowed range

Filename -> server-side mapping

Hostname -> defined hostname grammar
```


# Avoid Shell Escaping as Primary Defence

Escaping is fragile and interpreter-specific.

Removing the shell is safer.


# Fixed Executable Paths

Where practical, use explicit executable paths:

```text
/usr/bin/ping
```

instead of relying unnecessarily on environment search paths.


# Least Privilege

The application should run with minimal operating-system permissions.


# Network Restrictions

If application workers do not need arbitrary outbound access, restrict it.

This can reduce the impact of command execution but does not fix command injection.


# Container Isolation

Use:

```text
Non-root container user

Read-only filesystem where practical

Minimal capabilities

Restricted mounts

Network restrictions
```

as defence in depth.


# Logging

Log security-relevant failures without recording sensitive user data unnecessarily.


# Retesting

Retest the exact original input path.


# Retest Baseline

Confirm legitimate functionality still works.


# Retest Original Separator

The original injection string should no longer alter command structure.


# Retest Alternative Shell Syntax

Where a shell has been removed entirely, alternative separators should have no command interpretation.


# Retest Argument Injection

If direct process execution replaced shell execution, verify attacker-controlled values cannot introduce unsafe options to the called utility.


# Retest Timing

The original short-delay technique should no longer affect response time beyond normal variation.


# Retest OOB

No controlled DNS or HTTP interaction should occur from command injection attempts.


# Retest Errors

Input should be rejected with an application-level validation error rather than reaching shell or utility parsing.


# Retest Source

Verify:

```text
No shell command concatenation

Arguments passed separately

Strict validation present
```


# Root Cause Review

After finding one command injection path, search the entire codebase for other command execution sinks.

Python:

```bash
rg -ni 'os\.system|os\.popen|subprocess\.|shell\s*=\s*True' -g '*.py' .
```

Node.js:

```bash
rg -ni 'child_process|exec\(|execSync|spawn\(|execFile' -g '*.js' -g '*.ts' .
```

Java:

```bash
rg -ni 'Runtime\.getRuntime\(\)\.exec|ProcessBuilder' -g '*.java' .
```

.NET:

```bash
rg -ni 'Process\.Start|ProcessStartInfo' -g '*.cs' .
```

PHP:

```bash
rg -ni 'system\(|exec\(|shell_exec|passthru|popen|proc_open' -g '*.php' .
```

Ruby:

```bash
rg -ni 'system\(|exec\(|Open3|IO\.popen' -g '*.rb' .
```

Go:

```bash
rg -ni 'os/exec|exec\.Command|exec\.CommandContext' -g '*.go' .
```


# Practical Command Injection Checklist

## Discovery

- [ ] Network diagnostic features reviewed
- [ ] File conversion reviewed
- [ ] Image processing reviewed
- [ ] PDF/document generation reviewed
- [ ] Backup functionality reviewed
- [ ] Archive functionality reviewed
- [ ] Git integrations reviewed
- [ ] Monitoring tools reviewed
- [ ] Administrative utilities reviewed
- [ ] Import/export processing reviewed

## Baseline

- [ ] Legitimate request captured
- [ ] Parameter identified
- [ ] Response captured
- [ ] Response time measured
- [ ] Authentication context recorded
- [ ] Operating system considered
- [ ] Execution mechanism considered

## Output-Based Testing

- [ ] Harmless command selected
- [ ] Unique marker used
- [ ] One separator tested at a time
- [ ] Output distinguished from reflection
- [ ] Test repeated
- [ ] No destructive commands used

## Blind Testing

- [ ] Baseline timing measured repeatedly
- [ ] Short delay used
- [ ] Candidate repeated
- [ ] Network variance considered
- [ ] OOB used only where authorised
- [ ] Unique OOB identifier used

## Argument Injection

- [ ] Direct process execution considered
- [ ] Option-like values considered
- [ ] Called utility understood
- [ ] `--` support reviewed where relevant
- [ ] Impact demonstrated separately from shell injection

## Source Review

- [ ] Command execution sinks identified
- [ ] Shell invocation identified
- [ ] User-controlled source traced
- [ ] String concatenation reviewed
- [ ] Argument arrays reviewed
- [ ] Input validation reviewed
- [ ] Executable path reviewed
- [ ] Privilege context reviewed

## Evidence

- [ ] Endpoint
- [ ] Method
- [ ] Parameter
- [ ] Authentication context
- [ ] Baseline
- [ ] Candidate
- [ ] Unique marker
- [ ] Output
- [ ] Timing
- [ ] OOB interaction
- [ ] Timestamp
- [ ] Execution privilege where known

## Remediation

- [ ] Shell removed where possible
- [ ] Native API considered
- [ ] Argument array used
- [ ] Input parsed as expected data type
- [ ] Dangerous option handling reviewed
- [ ] Fixed executable path considered
- [ ] Least privilege reviewed
- [ ] Network restrictions considered

## Retest

- [ ] Legitimate functionality works
- [ ] Original injection blocked
- [ ] Alternative separators ineffective
- [ ] Argument injection reviewed
- [ ] Timing effect absent
- [ ] OOB interaction absent
- [ ] Source fix verified
- [ ] Equivalent command sinks reviewed


# Command Execution API Matrix

| Language | High-Interest APIs |
|---|---|
| Python | `os.system`, `os.popen`, `subprocess` |
| Node.js | `exec`, `execSync`, `spawn`, `execFile` |
| Java | `Runtime.exec`, `ProcessBuilder` |
| .NET | `Process.Start`, `ProcessStartInfo` |
| PHP | `system`, `exec`, `shell_exec`, `passthru` |
| Ruby | `system`, `exec`, `Open3`, `IO.popen` |
| Go | `exec.Command`, `exec.CommandContext` |


# Result Interpretation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| Input reflected | Reflection | Command execution |
| Shell error returned | Possible shell interaction | Arbitrary command execution |
| Utility option error | Argument influence | Shell injection |
| Unique marker returned | Command execution | Elevated privileges |
| Repeatable short delay | Blind execution candidate | Interactive shell |
| DNS callback | External interaction | HTTP access |
| HTTP callback | Outbound request | Privilege escalation |
| Command sink in source | Review candidate | Attacker reachability |
| `shell=True` + user data | Strong candidate | Runtime exploitability until traced |


# Injection Type Matrix

| Behaviour | Classification |
|---|---|
| User data introduces second shell command | OS Command Injection |
| User data introduces utility option | Argument Injection |
| User data modifies SQL syntax | SQL Injection |
| User data modifies template expression | SSTI |
| User data changes filesystem path | Path Traversal |
| User URL causes backend request | SSRF |


# Source Review Priority Matrix

| Pattern | Priority |
|---|---:|
| Constant command, no user data | Low |
| Validated user value, direct argument array | Lower |
| User value in argument array | Review argument injection |
| User value concatenated into command string | High |
| User value passed to `shell=True` | Very High |
| User value passed to `sh -c` / `cmd /c` | Very High |
| Uploaded filename concatenated into shell command | Very High |


# Remediation Matrix

| Control | Purpose |
|---|---|
| Native library/API | Avoid OS command entirely |
| Direct process API | Avoid shell interpretation |
| Argument array | Separate command from data |
| Strict validation | Enforce business data type |
| End-of-options marker | Reduce option injection where supported |
| Fixed executable path | Reduce PATH ambiguity |
| Least privilege | Reduce execution impact |
| Network restrictions | Limit post-execution reach |
| Container isolation | Reduce blast radius |


# Burp Quick Workflow

```text
                CANDIDATE INPUT
                       |
                       v
                    REPEATER
                       |
                       v
                    BASELINE
                       |
                       v
               HARMLESS MARKER
                       |
          +------------+------------+
          |            |            |
          v            v            v
        OUTPUT       TIMING         OOB
          |            |            |
          +------------+------------+
                       |
                       v
                    REPEAT
                       |
                       v
                INTERPRET RESULT
                       |
                       v
                   EVIDENCE
```


# Source-to-Sink Model

```text
                   USER INPUT
                       |
                       v
                 APPLICATION
                       |
                       v
              COMMAND CONSTRUCTION
                       |
            +----------+----------+
            |                     |
            v                     v
       ARGUMENT ARRAY        COMMAND STRING
            |                     |
            v                     v
      DIRECT PROCESS             SHELL
            |                     |
            v                     v
    ARGUMENT INJECTION?     COMMAND INJECTION?
```


# Secure Execution Model

```text
                 USER INPUT
                     |
                     v
              STRICT PARSING
                     |
                     v
             EXPECTED DATA TYPE
                     |
                     v
               ARGUMENT ARRAY
                     |
                     v
              DIRECT PROCESS
                     |
                     v
             LOW-PRIVILEGE USER
```


# Practical Validation Model

```text
Prerequisites
     |
     v
Baseline Request
     |
     v
Controlled Input Change
     |
     v
Representative Result
     |
     v
Interpretation
     |
     v
Repeat / Correlate
     |
     v
Security Conclusion
     |
     v
Remediation
     |
     v
Retest
```


# Final Testing Principle

The key question is not:

```text
Does the parameter accept a semicolon?
```

It is:

```text
CAN ATTACKER-CONTROLLED DATA
           |
           v
REACH AN OPERATING-SYSTEM EXECUTION SINK
           |
           v
AND CHANGE THE MEANING OF THE EXECUTED COMMAND?
```

A strong workflow is:

```text
Identify Candidate Function
        |
        v
Establish Baseline
        |
        v
Determine Execution Mechanism
        |
        v
Identify Shell / Direct Process
        |
        v
Use Harmless Marker
        |
        v
Observe Output / Timing / OOB
        |
        v
Repeat
        |
        v
Determine Actual Privilege Context
        |
        v
Capture Evidence
        |
        v
Remove Unsafe Command Construction
        |
        v
Retest
```

For every command injection candidate ask:

```text
Does the application actually execute an OS command?

Could the functionality use a native API instead?

Which executable is invoked?

Is a shell involved?

Which shell?

Does user input reach the command string?

Where is the user input placed?

Is it quoted?

Can the input change command structure?

Can the input introduce command-line options?

Is output returned?

Is the issue blind?

Can a short timing test establish execution?

Can a controlled callback establish execution?

Did the application itself generate the callback?

Can the result be reproduced?

What user executes the process?

Is the application containerised?

What privileges were actually demonstrated?

Am I confusing reflection with execution?

Am I confusing argument injection with shell injection?

Did I use the minimum command required to prove the issue?

Does remediation remove the shell?

Are arguments passed separately?

Is the input validated according to its business type?

Have equivalent execution sinks been reviewed?
```

The strongest conclusion is not:

```text
A command separator changed the response.
```

It is:

```text
CONTROLLED INPUT
      |
      v
COMMAND STRUCTURE CHANGED
      |
      v
UNIQUE EXECUTION EFFECT
      |
      v
REPEATABLE OBSERVATION
      |
      v
CONFIRMED COMMAND INJECTION
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)
- [Content Discovery Cheatsheet](content-discovery.md)
- [Path Traversal and File Inclusion Cheatsheet](path-traversal-file-inclusion.md)
- [File Upload Security Cheatsheet](file-upload.md)
- [SSRF Cheatsheet](ssrf.md)
- [XXE Cheatsheet](xxe.md)


# Related Notes

The deeper notes relevant to this cheatsheet are expected under:

```text
docs/web/command-injection.md
docs/source-code-review/
```

Use the corresponding notes page for longer explanations and keep this cheatsheet as the operational assessment reference.


# References

- [PortSwigger Web Security Academy - OS Command Injection](https://portswigger.net/web-security/os-command-injection){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide - Testing for Command Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/12-Testing_for_Command_Injection){ target="_blank" rel="noopener noreferrer" }
- [OWASP Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [CWE-78 - Improper Neutralization of Special Elements used in an OS Command](https://cwe.mitre.org/data/definitions/78.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Prove execution, not payload acceptance"

    A semicolon being accepted or an error changing does not establish command injection. Prefer a unique harmless marker, a repeatable short timing effect or a correlated assessment-controlled callback.


!!! tip "Find out whether a shell exists"

    The difference between `shell command + user input` and a direct process call with an argument array is fundamental. Source review can eliminate a large amount of unnecessary payload guessing.


!!! tip "Separate command injection from argument injection"

    An attacker-controlled value becoming an unintended option to the intended executable is not necessarily shell command injection. Report the mechanism you actually demonstrate.


!!! warning "A reverse shell is unnecessary"

    Once a unique harmless command can be executed reliably, arbitrary command execution has been demonstrated. A reverse shell adds operational risk without normally adding meaningful evidence.


!!! warning "Do not fix command injection with a character blacklist"

    Blocking `;`, `|` or `&` does not address unsafe command construction. Remove unnecessary shell invocation, pass arguments separately and strictly validate input according to its intended business type.
