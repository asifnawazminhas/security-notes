---
title: Git and ripgrep Cheatsheet
description: Practical Git and ripgrep reference for authorised source-code security review covering repository reconnaissance, history analysis, secret discovery, security-focused searches, code tracing, commit analysis, result interpretation, evidence collection and retesting.
---

# Git and ripgrep Cheatsheet

Git and ripgrep (`rg`) are two of the most useful tools for manual source-code security review.

Git answers questions such as:

```text
What changed?

Who changed it?

When was it changed?

What did the previous implementation look like?

Was sensitive information committed historically?

Which commit introduced this behaviour?

Which branches contain this code?
```

ripgrep answers questions such as:

```text
Where is this function used?

Where does this parameter enter the application?

Where are commands executed?

Where are database queries constructed?

Where are files opened?

Where are HTTP requests made?

Where are authentication checks performed?

Where are authorisation decisions made?

Where are secrets referenced?
```

Used together:

```text
Repository
    |
    v
Git Reconnaissance
    |
    v
Understand Structure and History
    |
    v
ripgrep Search
    |
    v
Security-Relevant Candidate
    |
    v
Read Surrounding Code
    |
    v
Trace Input to Sensitive Operation
    |
    v
Git History
    |
    v
Understand Why / When It Changed
    |
    v
Validate Security Assumptions
    |
    v
Evidence
    |
    v
Finding or Dismissal
```

!!! warning "Authorised Security Review"

    Review only source code and repositories that you are authorised to access. Repositories may contain credentials, API keys, customer information, proprietary code, internal infrastructure details and historical secrets. Treat cloned repositories and extracted evidence as sensitive assessment material.


# Quick Reference

## Repository Status

```bash
git status
```

## Current Branch

```bash
git branch --show-current
```

## Branches

```bash
git branch -a
```

## Recent History

```bash
git log --oneline --decorate -20
```

## Files

```bash
rg --files
```

## Search Text

```bash
rg -n 'search_term' .
```

## Case-Insensitive Search

```bash
rg -ni 'password' .
```

## Fixed-String Search

```bash
rg -nF 'Authorization: Bearer' .
```

## Search With Context

```bash
rg -n -C 4 'subprocess\.run' .
```

## Search Specific File Type

```bash
rg -n -t py 'subprocess' .
```

## Search Specific Glob

```bash
rg -n -g '*.js' 'fetch\(' .
```

## List Matching Files

```bash
rg -l 'password' .
```

## Commit History for File

```bash
git log --oneline -- path/to/file
```

## Show Commit

```bash
git show <commit>
```

## Blame Lines

```bash
git blame path/to/file
```

## Compare Commits

```bash
git diff <commit1> <commit2>
```


# Install ripgrep

Kali/Debian:

```bash
sudo apt update
sudo apt install ripgrep
```

Verify:

```bash
rg --version
```

Help:

```bash
rg --help
```

Git:

```bash
git --version
```


# Security Review Philosophy

A regex match is not a vulnerability.

Use:

```text
Search Match
    |
    v
Candidate
    |
    v
Read Code
    |
    v
Understand Input
    |
    v
Understand Sensitive Operation
    |
    v
Understand Existing Controls
    |
    v
Determine Reachability
    |
    v
Validate Security Consequence
```

Avoid:

```text
rg finds "password"
       |
       v
Report hardcoded password
```

or:

```text
rg finds "subprocess"
       |
       v
Report command injection
```

The search result tells you where to investigate.


# Source-Code Review Workflow

```text
REPOSITORY
    |
    v
Identify Technology
    |
    v
Map Structure
    |
    v
Identify Entry Points
    |
    v
Identify Authentication
    |
    v
Identify Authorisation
    |
    v
Identify User-Controlled Input
    |
    v
Identify Sensitive Operations
    |
    v
Trace Data Flow
    |
    v
Review Security Controls
    |
    v
Review Git History
    |
    v
Validate Candidate
    |
    v
Document Evidence
```


# Repository Reconnaissance

Start by understanding what you have.

```bash
pwd
```

```bash
ls -la
```

Then:

```bash
git status
```

```bash
git branch --show-current
```

```bash
git remote -v
```

```bash
git log --oneline --decorate -20
```


# Repository Root

Find the Git repository root:

```bash
git rev-parse --show-toplevel
```

Change to it:

```bash
cd "$(git rev-parse --show-toplevel)"
```


# Record Commit Under Review

Before beginning a formal review:

```bash
git rev-parse HEAD
```

Representative output:

```text
7b61a8c53cce0a80e5d60c08f31a65d991234567
```

This gives the review a reproducible code reference.

Record it in the assessment notes.


# Short Commit Hash

```bash
git rev-parse --short HEAD
```

Example:

```text
7b61a8c
```


# Repository Metadata

Useful:

```bash
git remote -v
```

```bash
git branch -a
```

```bash
git tag
```

```bash
git log --oneline --all --decorate --graph -30
```


# List Files With ripgrep

```bash
rg --files
```

This is an excellent first look at a repository.


# Count Files

```bash
rg --files | wc -l
```


# Directory Overview

```bash
find . -maxdepth 2 -type d | sort
```

Useful directories may include:

```text
src/

app/

api/

routes/

controllers/

services/

models/

middleware/

config/

templates/

tests/

scripts/

deploy/

infra/

terraform/

.github/
```


# Identify Technology

Search for common dependency files:

```bash
find . -maxdepth 3 -type f \( \
  -name 'package.json' -o \
  -name 'requirements.txt' -o \
  -name 'pyproject.toml' -o \
  -name 'pom.xml' -o \
  -name 'build.gradle' -o \
  -name 'go.mod' -o \
  -name 'Cargo.toml' -o \
  -name '*.csproj' \
\) -print
```


# Common Technology Files

```text
package.json
    -> Node.js / JavaScript / TypeScript

requirements.txt
pyproject.toml
    -> Python

pom.xml
build.gradle
    -> Java

go.mod
    -> Go

Cargo.toml
    -> Rust

*.csproj
    -> .NET
```


# ripgrep Basics

General syntax:

```bash
rg [OPTIONS] PATTERN [PATH]
```

Example:

```bash
rg 'password' .
```


# Show Line Numbers

```bash
rg -n 'password' .
```


# Case Insensitive

```bash
rg -ni 'password' .
```


# Smart Case

```bash
rg -S 'password' .
```

Smart case can be convenient when searching interactively.


# Fixed String

Use `-F` when the search value should not be interpreted as a regular expression:

```bash
rg -nF 'request.headers["Authorization"]' .
```


# Context

Three lines before and after:

```bash
rg -n -C 3 'subprocess\.run' .
```

Before:

```bash
rg -n -B 5 'subprocess\.run' .
```

After:

```bash
rg -n -A 5 'subprocess\.run' .
```


# Matching Files Only

```bash
rg -l 'subprocess\.run' .
```


# Files Without Matches

```bash
rg -L 'authorize' app/
```


# Count Matches

```bash
rg -c 'TODO' .
```


# Search Specific Extension

```bash
rg -n -g '*.py' 'subprocess' .
```

JavaScript:

```bash
rg -n -g '*.js' 'child_process' .
```

TypeScript:

```bash
rg -n -g '*.ts' 'child_process' .
```


# Search by ripgrep Type

Python:

```bash
rg -n -t py 'subprocess' .
```

JavaScript:

```bash
rg -n -t js 'fetch\(' .
```

Rust:

```bash
rg -n -t rust 'Command::new' .
```


# Available Types

```bash
rg --type-list
```


# Exclude Directories

Example:

```bash
rg -n 'password' . \
  -g '!node_modules/**' \
  -g '!vendor/**' \
  -g '!dist/**' \
  -g '!build/**'
```


# Common Exclusions

```text
.git/

node_modules/

vendor/

dist/

build/

coverage/

target/

bin/

obj/
```

Generated or vendored code can create enormous amounts of noise.


# Gitignore Behaviour

ripgrep normally respects ignore files such as:

```text
.gitignore
```

This is useful for normal code review, but it can hide files that are interesting during a security assessment.


# Search Ignored Files

Where appropriate:

```bash
rg --no-ignore -n 'password' .
```

Be prepared for significantly more output.


# Hidden Files

Include hidden files:

```bash
rg --hidden -n 'password' .
```

This can reveal security-relevant files such as:

```text
.env

.github/

.gitlab/

.hidden-config
```


# Hidden and Ignored

For a deliberate broader search:

```bash
rg --hidden --no-ignore -n 'password' .
```

Use this selectively because it may search:

```text
Dependencies

Build output

Generated code

Large caches
```


# Exclude .git During Broad Search

```bash
rg --hidden --no-ignore \
  -g '!.git/**' \
  -n 'password' .
```


# Search Multiple Patterns

```bash
rg -n -e 'password' -e 'passwd' -e 'secret' .
```


# Regex Alternation

```bash
rg -ni 'password|passwd|secret|token' .
```


# Search TODO and FIXME

```bash
rg -ni 'TODO|FIXME|HACK|XXX' .
```

These can reveal:

```text
Temporary security controls

Disabled validation

Incomplete authentication

Known technical debt

Debug functionality
```

But most TODO comments are not security issues.


# Security Review Categories

A practical manual review can search for:

```text
Secrets

Authentication

Authorisation

Command execution

SQL/database access

File operations

Network requests

Deserialization

Template rendering

Cryptography

Logging

Debug functionality

Configuration

Redirects

CORS

Uploads

Token handling
```


# Secret Discovery

Start broad:

```bash
rg --hidden \
  -g '!.git/**' \
  -ni 'password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key' .
```


# Search Environment Files

```bash
find . -type f \( \
  -name '.env' -o \
  -name '.env.*' -o \
  -name '*secret*' -o \
  -name '*credential*' \
\) -print
```


# Search Configuration Files

```bash
rg --files | rg '\.(yml|yaml|json|toml|ini|conf|config|properties)$'
```


# Search for Password Assignments

Example heuristic:

```bash
rg -ni 'password\s*[:=]' .
```

This may find:

```text
Real credentials

Configuration variables

Test fixtures

Documentation

Examples

Empty defaults
```

Each result needs interpretation.


# Example Search Result

Suppose:

```bash
rg -n 'password\s*=' .
```

returns:

```text
tests/test_login.py:18:password = "test123"
config/example.py:7:password = "changeme"
app/settings.py:32:password = os.environ["DB_PASSWORD"]
```

Interpretation:

```text
tests/test_login.py
    |
    +--> Test credential candidate
    |
    +--> Determine whether test-only

config/example.py
    |
    +--> Example/default value
    |
    +--> Determine whether deployed

app/settings.py
    |
    +--> Reads environment variable
    |
    +--> Not a hardcoded password
```

Do not classify all three equally.


# Private Keys

Search for PEM markers:

```bash
rg --hidden -nF 'BEGIN PRIVATE KEY' .
```

RSA:

```bash
rg --hidden -nF 'BEGIN RSA PRIVATE KEY' .
```

OpenSSH:

```bash
rg --hidden -nF 'BEGIN OPENSSH PRIVATE KEY' .
```


# Private Key Interpretation

If found:

```text
Is it a test key?

Is it documentation?

Is it active?

Was it committed?

Is it used by production?

Has it been rotated?

Does Git history contain older copies?
```

Do not attempt to use discovered credentials unless that activity is explicitly authorised.


# Authentication Search

Search for authentication-related terms:

```bash
rg -ni 'authenticate|authentication|login|signin|sign_in|session|jwt|bearer' .
```


# Authorisation Search

```bash
rg -ni 'authorize|authorization|permission|role|is_admin|admin_only|access_control' .
```


# Middleware

```bash
rg -ni 'middleware|before_request|before_action|guard|interceptor' .
```

Security controls are often centralised in middleware.


# Routes

Route discovery is framework dependent.

Generic searches:

```bash
rg -n 'route|router|endpoint|mapping' .
```


# Flask Routes

```bash
rg -n '@.*\.route\(' -g '*.py' .
```


# FastAPI Routes

```bash
rg -n '@.*\.(get|post|put|patch|delete)\(' -g '*.py' .
```


# Express Routes

```bash
rg -n '\.(get|post|put|patch|delete)\(' -g '*.js' -g '*.ts' .
```


# Spring Routes

```bash
rg -n '@(RequestMapping|GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping)' -g '*.java' .
```


# ASP.NET Routes

Useful starting terms:

```bash
rg -n '\[Http(Get|Post|Put|Patch|Delete)' -g '*.cs' .
```


# Route Review Model

For each sensitive route determine:

```text
Route
  |
  v
Authentication?
  |
  v
Authorisation?
  |
  v
Input
  |
  v
Business Logic
  |
  v
Sensitive Operation
```


# Command Execution Search

Command execution is a high-value review category.

Python:

```bash
rg -n 'os\.system|subprocess\.(run|Popen|call|check_output|check_call)' -g '*.py' .
```

Node.js:

```bash
rg -n 'exec\(|execSync\(|spawn\(|spawnSync\(' -g '*.js' -g '*.ts' .
```

PHP:

```bash
rg -n '\b(system|exec|shell_exec|passthru|popen|proc_open)\s*\(' -g '*.php' .
```

Java:

```bash
rg -n 'Runtime\.getRuntime\(\)\.exec|ProcessBuilder' -g '*.java' .
```

.NET:

```bash
rg -n 'Process\.Start|ProcessStartInfo' -g '*.cs' .
```


# Command Execution Does Not Equal Command Injection

Example:

```python
subprocess.run(["uptime"], check=True)
```

This executes a command.

It does not show user-controlled command construction.


# Worked Example - Command Injection Candidate

Assume the repository contains:

```python
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.get("/diagnostics/ping")
def ping():
    host = request.args.get("host", "")
    result = subprocess.run(
        "ping -c 1 " + host,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout
```


# Step 1 - Find Command Execution

```bash
rg -n -g '*.py' 'subprocess\.(run|Popen)|os\.system' .
```

Representative output:

```text
app/health.py:18:    subprocess.run(["uptime"], check=True)
app/diagnostics.py:9:    result = subprocess.run(
```


# Step 2 - Interpret Matches

First result:

```python
subprocess.run(["uptime"], check=True)
```

Observation:

```text
Fixed command.

No user input visible.

No shell invocation visible.
```

Initial classification:

```text
Low-priority candidate.
```

Second result requires more context.


# Step 3 - Read Context

```bash
rg -n -C 8 'subprocess\.run' app/diagnostics.py
```

Representative output:

```text
3-app = Flask(__name__)
4-
5-@app.get("/diagnostics/ping")
6-def ping():
7-    host = request.args.get("host", "")
8-    result = subprocess.run(
9-        "ping -c 1 " + host,
10-        shell=True,
11-        capture_output=True,
12-        text=True
13-    )
14-    return result.stdout
```


# Step 4 - Identify Source

Potential source:

```python
request.args.get("host", "")
```

This indicates:

```text
HTTP query parameter
       |
       v
host
```


# Step 5 - Identify Sink

Sensitive operation:

```python
subprocess.run(...)
```

with:

```python
shell=True
```


# Step 6 - Trace Data Flow

```text
HTTP Request
    |
    v
?host=
    |
    v
request.args.get()
    |
    v
host
    |
    v
String Concatenation
    |
    v
subprocess.run()
    |
    v
shell=True
```


# Step 7 - Search for Validation

Search for the variable and related validation:

```bash
rg -n -C 5 '\bhost\b|validate|allowlist|regex|hostname' app/diagnostics.py
```

Questions:

```text
Is host validated?

Is there an allowlist?

Is input canonicalised?

Is the route authenticated?

Is the route reachable?

Does another middleware restrict access?
```


# Step 8 - Security Interpretation

The source code provides evidence of a potentially dangerous data flow:

```text
User-controlled input
        |
        v
Shell command string
        |
        v
Shell interpreter
```

However, before writing a final finding determine:

```text
Is this code reachable?

Is the route deployed?

Does middleware restrict access?

Does upstream validation exist?

Does configuration disable the feature?

What account executes the process?

Can the behaviour be reproduced safely?
```


# Stronger Conclusion

A source review conclusion could state:

> The `/diagnostics/ping` handler obtains the `host` query parameter and concatenates it directly into a command string executed through `subprocess.run()` with `shell=True`. No validation is present in the reviewed function. This creates a command-injection candidate that requires confirmation of route reachability, upstream controls and runtime behaviour before final severity is assigned.


# Safer Implementation Pattern

Where possible, avoid shell interpretation.

For example:

```python
subprocess.run(
    ["ping", "-c", "1", host],
    shell=False,
    capture_output=True,
    text=True
)
```

Input should still be validated according to the application's intended hostname/IP requirements.


# SQL Search

Python:

```bash
rg -ni 'execute\(|executemany\(|raw\(' -g '*.py' .
```

Java:

```bash
rg -n 'createStatement|prepareStatement|executeQuery|executeUpdate' -g '*.java' .
```

PHP:

```bash
rg -n 'mysqli_query|->query\(|->prepare\(' -g '*.php' .
```

.NET:

```bash
rg -n 'SqlCommand|ExecuteReader|ExecuteNonQuery|FromSqlRaw' -g '*.cs' .
```


# SQL Candidate

Potentially interesting:

```python
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)
```

Safer pattern:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,)
)
```

Exact parameter syntax depends on the database library.


# SQL Interpretation

Do not search only for:

```text
SELECT
```

Instead trace:

```text
Request Input
      |
      v
Query Construction
      |
      v
Database API
```

Determine whether parameterisation occurs.


# File Operations

Python:

```bash
rg -n '\b(open|send_file|send_from_directory)\s*\(' -g '*.py' .
```

Node.js:

```bash
rg -n 'readFile|readFileSync|createReadStream|writeFile|writeFileSync' -g '*.js' -g '*.ts' .
```

Java:

```bash
rg -n 'new File\(|Files\.(read|write|copy|move)' -g '*.java' .
```

.NET:

```bash
rg -n 'File\.(Read|Write|Open|Delete|Copy|Move)|FileStream' -g '*.cs' .
```


# File Review Model

```text
User Input
    |
    v
Filename / Path
    |
    v
Normalisation?
    |
    v
Base Directory?
    |
    v
Access Control?
    |
    v
File Operation
```


# Path Construction

Search:

```bash
rg -ni 'path\.join|os\.path\.join|Path\(|filepath|filename|upload|download' .
```

Determine whether user input controls filesystem paths.


# Upload Handling

```bash
rg -ni 'upload|multipart|filename|content-type|mimetype|extension' .
```

Review:

```text
Extension checks

Content checks

Storage directory

Filename generation

Permissions

Serving behaviour

Authorisation
```


# Network Requests / SSRF Review

Python:

```bash
rg -n 'requests\.(get|post|put|patch|delete)|httpx\.|urllib\.request' -g '*.py' .
```

Node.js:

```bash
rg -n 'fetch\(|axios\.|http\.request|https\.request' -g '*.js' -g '*.ts' .
```

Java:

```bash
rg -n 'HttpClient|HttpURLConnection|RestTemplate|WebClient' -g '*.java' .
```

.NET:

```bash
rg -n 'HttpClient|WebRequest|WebClient' -g '*.cs' .
```


# SSRF Review Model

```text
User-Controlled URL?
       |
       v
URL Parser
       |
       v
Scheme Restrictions?
       |
       v
Hostname Validation?
       |
       v
DNS Resolution
       |
       v
IP Validation?
       |
       v
Redirect Handling?
       |
       v
Outbound Request
```


# SSRF Candidate Example

```python
url = request.json["url"]
response = requests.get(url)
```

This is security relevant because request input directly influences an outbound request.

But determine:

```text
Authentication required?

URL allowlist?

Network egress controls?

Redirect handling?

DNS rebinding protections?

Response returned to user?

Blind or non-blind behaviour?
```


# Deserialization Search

Python:

```bash
rg -n 'pickle\.loads?|yaml\.load|marshal\.loads?' -g '*.py' .
```

Java:

```bash
rg -n 'ObjectInputStream|readObject\(' -g '*.java' .
```

PHP:

```bash
rg -n '\bunserialize\s*\(' -g '*.php' .
```

.NET:

```bash
rg -n 'BinaryFormatter|LosFormatter|ObjectStateFormatter' -g '*.cs' .
```

A match requires analysis of:

```text
Input trust

Serializer configuration

Object types

Reachability

Existing integrity controls
```


# Template Rendering

Python:

```bash
rg -n 'render_template_string|Template\(' -g '*.py' .
```

Node:

```bash
rg -ni 'render\(|ejs|handlebars|pug|nunjucks' -g '*.js' -g '*.ts' .
```

PHP:

```bash
rg -ni 'twig|blade|smarty' -g '*.php' .
```

Review whether user-controlled input becomes:

```text
Template data
```

or:

```text
Template source
```

These are very different security situations.


# Redirects

Search:

```bash
rg -ni 'redirect|returnUrl|return_url|nextUrl|next_url|callbackUrl|callback_url' .
```

Trace:

```text
User Input
    |
    v
Destination Validation
    |
    v
Redirect
```


# CORS

Search:

```bash
rg -ni 'cors|access-control-allow-origin|allowed_origins|allow_origins' .
```

Review:

```text
Allowed origins

Credential support

Wildcard behaviour

Environment-specific configuration
```


# Cryptography

Search:

```bash
rg -ni 'md5|sha1|aes|des|ecb|encrypt|decrypt|cipher|random|rand\(' .
```

Do not report every occurrence of:

```text
MD5

SHA-1
```

Determine purpose.

For example:

```text
File integrity identifier
```

is different from:

```text
Password storage.
```


# Password Hashing

Search:

```bash
rg -ni 'bcrypt|argon2|scrypt|pbkdf2|password_hash|hash_password' .
```

Trace where passwords are:

```text
Received

Processed

Hashed

Stored

Compared
```


# Randomness

Search:

```bash
rg -ni 'random|rand\(|Math\.random|Random\(' .
```

Determine whether the value protects:

```text
Sessions

Password reset

CSRF

API credentials

Cryptographic keys
```

Non-security randomness has different requirements.


# Logging

Search:

```bash
rg -ni 'logger\.|logging\.|console\.log|print\(' .
```

Look for sensitive values being logged:

```text
Passwords

Tokens

Session identifiers

API keys

Personal data
```


# Debug Functionality

```bash
rg -ni 'debug|development|dev_mode|trace|verbose' .
```

Also inspect configuration files.


# Flask Debug

```bash
rg -n 'debug\s*=\s*True|FLASK_DEBUG' -g '*.py' -g '*.env*' .
```


# Django Debug

```bash
rg -n 'DEBUG\s*=\s*True' -g '*.py' .
```


# Environment-Specific Configuration

Find:

```bash
find . -type f \( \
  -name '*.env*' -o \
  -name '*prod*' -o \
  -name '*production*' -o \
  -name '*staging*' -o \
  -name '*development*' \
\) -print
```

Security behaviour may differ significantly between environments.


# Infrastructure as Code

Search repository files:

```bash
rg --files | rg '\.(tf|tfvars|ya?ml|json)$'
```

Look for:

```text
Public exposure

IAM permissions

Secrets

Security groups

Storage permissions

Container privileges

Network configuration
```


# Docker

Find Dockerfiles:

```bash
find . -type f \( -name 'Dockerfile' -o -name 'Dockerfile.*' \) -print
```

Search:

```bash
rg -ni 'USER|EXPOSE|COPY|ADD|ENTRYPOINT|CMD' -g 'Dockerfile*' .
```


# Docker Security Questions

```text
Does the container run as root?

Are secrets copied into the image?

Is unnecessary software installed?

Are sensitive files copied?

Are dangerous capabilities required?

What ports are exposed?
```


# Kubernetes

Search:

```bash
rg -ni 'privileged:|runAsUser:|runAsNonRoot:|hostNetwork:|hostPID:|hostPath:' -g '*.yaml' -g '*.yml' .
```


# CI/CD

Inspect:

```text
.github/workflows/

.gitlab-ci.yml

Jenkinsfile

azure-pipelines.yml
```

Search:

```bash
rg -ni 'secret|token|password|credential|curl|wget|docker|sudo' .github/ 2>/dev/null
```


# Git History

Current code is only part of the story.

Git history may reveal:

```text
Removed credentials

Old endpoints

Security fixes

Temporary bypasses

Previous implementations

Deleted validation

Configuration changes
```


# Recent Commits

```bash
git log --oneline -20
```


# Graph

```bash
git log --oneline --all --decorate --graph -30
```


# Commit Details

```bash
git show <commit>
```


# Specific File History

```bash
git log --oneline -- path/to/file
```


# Show File Changes

```bash
git log -p -- path/to/file
```


# Follow Renames

```bash
git log --follow -- path/to/file
```


# Search Commit Messages

```bash
git log --oneline --all --grep='security'
```

Case insensitive:

```bash
git log --oneline --all --regexp-ignore-case --grep='auth'
```


# Useful Commit Terms

Search commit messages for:

```text
security

auth

authentication

authorization

permission

fix

hotfix

password

secret

token

admin

validation

sanitize

escape

CVE
```


# Example

```bash
git log --oneline --all --regexp-ignore-case --grep='security\|auth\|permission\|validation'
```

Commit messages are hints, not proof.


# Search Historical Content

Git can search revisions for text.

Example:

```bash
git log -S'API_KEY' --oneline --all
```

This searches for commits where the number of occurrences of the specified string changed.


# Search Password History

```bash
git log -S'password' --oneline --all
```


# Search Function History

```bash
git log -S'authorize_user' --oneline --all
```


# Regex Diff Search

`-G` searches changed lines matching a regex.

Example:

```bash
git log -G'password|secret|token' --oneline --all
```


# -S vs -G

Conceptually:

```text
-S
 |
 v
Did the number of occurrences of this string change?

-G
 |
 v
Did changed lines match this regex?
```


# Show Matching Historical Commit

```bash
git show <commit>
```


# Git Blame

```bash
git blame path/to/file
```

Useful for identifying the commit responsible for specific lines.


# Blame Selected Lines

```bash
git blame -L 40,60 app/auth.py
```


# Then Inspect Commit

```bash
git show <commit>
```


# Security Use of Blame

Suppose you find:

```python
if user:
    return admin_data()
```

Use:

```bash
git blame -L 120,125 app/admin.py
```

Then inspect the associated commit:

```bash
git show <commit>
```

This may reveal:

```text
Why the check changed

Previous implementation

Related files

Tests

Developer intent
```


# Do Not Use Blame for Attribution

During security review, `git blame` is primarily a technical history tool.

The goal is:

```text
Understand Code History
```

not:

```text
Assign Personal Fault
```


# Compare Branches

```bash
git diff main..develop
```


# Compare Specific File

```bash
git diff main..develop -- app/auth.py
```


# Compare Commits

```bash
git diff <old_commit> <new_commit>
```


# Changed Files

```bash
git diff --name-only <old_commit> <new_commit>
```


# Security-Focused Diff Review

For a release or pull-request review:

```text
Changed Files
     |
     v
Security-Relevant Changes?
     |
     +--> Authentication
     +--> Authorisation
     +--> Input Handling
     +--> Cryptography
     +--> Network Requests
     +--> File Handling
     +--> Configuration
     +--> Dependencies
```


# Review Current Changes

Unstaged:

```bash
git diff
```

Staged:

```bash
git diff --cached
```


# Statistics

```bash
git diff --stat
```


# Word-Level Diff

```bash
git diff --word-diff
```


# History of Deleted Secret

Suppose current search returns nothing:

```bash
rg -nF 'SECRET_KEY=' .
```

That does not prove the repository never contained it.

Search history:

```bash
git log -S'SECRET_KEY=' --oneline --all
```

Then:

```bash
git show <commit>
```


# Secret Removed From Current Branch

If a real credential was historically committed:

```text
Deleting it from the latest file
```

does not necessarily invalidate it.

Security response may require:

```text
Credential rotation

Repository history review

Access-log review

Secret-management migration
```

History rewriting alone is not equivalent to credential rotation.


# Branch Review

List:

```bash
git branch -a
```

Security-relevant code or secrets may exist in branches not currently checked out.


# Tags

```bash
git tag
```

Inspect:

```bash
git show <tag>
```

Tags may contain older release code.


# Git Objects and History

Avoid manually manipulating `.git` during routine review.

Prefer Git commands because they preserve context and reduce accidental repository corruption.


# Dependency Files

Search:

```bash
rg --files | rg '(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|requirements\.txt|poetry\.lock|Pipfile\.lock|pom\.xml|go\.sum|Cargo\.lock)$'
```

These files help identify dependencies for separate dependency-vulnerability analysis.


# Search Dependency Usage

Suppose a security-sensitive package appears in dependencies.

Search:

```bash
rg -n 'package_name' .
```

Determine whether it is actually used and where.


# Search Configuration Keys

Example:

```bash
rg -ni 'verify_ssl|verify_tls|certificate|tls|ssl' .
```

Potentially interesting:

```python
requests.get(url, verify=False)
```

But determine:

```text
Production code?

Test code?

Development environment?

Controlled internal endpoint?

Actual deployment configuration?
```


# Search Disabled TLS Verification

Python:

```bash
rg -n 'verify\s*=\s*False' -g '*.py' .
```

Node.js:

```bash
rg -n 'rejectUnauthorized\s*:\s*false' -g '*.js' -g '*.ts' .
```


# Search Security Headers

```bash
rg -ni 'content-security-policy|strict-transport-security|x-frame-options|x-content-type-options' .
```

Absence in source code does not prove the deployed application lacks the header.

It may be added by:

```text
Reverse proxy

Load balancer

CDN

Web server

Ingress controller
```


# Search Authentication Bypass Logic

Useful terms:

```bash
rg -ni 'skip_auth|disable_auth|bypass_auth|no_auth|anonymous|allow_anonymous' .
```

Interpret carefully because legitimate public routes may use similar terminology.


# Search Role Checks

```bash
rg -ni 'is_admin|role\s*==|roles\.contains|has_role|permission' .
```

Trace whether security decisions occur:

```text
Only in UI

Client side

Server side

Middleware

Database layer
```


# Client-Side Authorisation

Search JavaScript/TypeScript:

```bash
rg -ni 'isAdmin|role|permission|canAccess|hasPermission' -g '*.js' -g '*.ts' -g '*.tsx' .
```

Client-side checks can improve UX but should not be the sole enforcement mechanism for server-side resources.


# API Endpoint Inventory

Examples:

```bash
rg -n '@.*\.route\(' -g '*.py' .
```

```bash
rg -n '\.(get|post|put|patch|delete)\(' -g '*.js' -g '*.ts' .
```

Export if useful:

```bash
rg -n '@.*\.route\(' -g '*.py' > flask-routes.txt
```


# Search Query Parameters

Python:

```bash
rg -n 'request\.(args|form|json|files|headers|cookies)' -g '*.py' .
```

Node:

```bash
rg -n 'req\.(query|body|params|headers|cookies)' -g '*.js' -g '*.ts' .
```


# Source-to-Sink Review

This is one of the most important manual review techniques.

```text
SOURCE
  |
  v
TRANSFORMATIONS
  |
  v
VALIDATION
  |
  v
SECURITY CONTROL
  |
  v
SINK
```


# Common Sources

```text
HTTP query parameters

POST body

JSON body

Headers

Cookies

Uploaded files

Database content

Message queues

Environment variables

External APIs
```


# Common Sensitive Sinks

```text
Shell execution

SQL queries

File operations

Template engines

Deserializers

Redirects

Outbound HTTP requests

LDAP queries

XML parsers

Logging

HTML output
```


# Trace a Variable

Suppose:

```python
filename = request.args["file"]
```

Search:

```bash
rg -n '\bfilename\b' .
```

Then inspect each use.


# Search Exact Function

```bash
rg -nF 'download_file(' .
```


# Search Definition and Calls

Python:

```bash
rg -n 'def download_file|download_file\(' -g '*.py' .
```


# Context Is Essential

Do not only collect:

```text
app/files.py:77: open(filename)
```

Collect enough surrounding code to understand:

```text
Where filename came from

Whether it was validated

Whether it was normalised

Whether a base directory was enforced
```


# Representative Output vs Proof

Suppose:

```bash
rg -n 'open\(' app/
```

returns:

```text
app/config.py:20:with open("config.json") as f:
app/files.py:77:with open(filename, "rb") as f:
```

Interpretation:

```text
config.py
    |
    +--> Fixed path
    |
    +--> Likely low priority

files.py
    |
    +--> Variable path
    |
    +--> Trace filename
```

This prioritisation is where manual review becomes valuable.


# Search Result Classification

A useful classification model:

| Classification | Meaning |
|---|---|
| Informational | Match exists but no immediate security relevance |
| Review Candidate | Security-sensitive API or control identified |
| Strong Candidate | User-controlled data appears to reach sensitive operation |
| Validated Finding | Security consequence has been established |
| False Positive | Match does not create the suspected condition |


# False Positives

Common reasons:

```text
Test code

Documentation

Examples

Dead code

Vendored code

Generated code

Unreachable route

Safe API usage

Fixed values

Input validation elsewhere

Framework protection

Feature disabled in production

Environment-specific configuration
```


# Tests Can Be Valuable

Do not automatically ignore:

```text
tests/
```

Tests can explain:

```text
Expected security behaviour

Authorisation requirements

Edge cases

Security regressions

Developer assumptions
```


# Search Security Tests

```bash
rg -ni 'unauthorized|forbidden|permission|authentication|csrf|xss|injection' tests/ 2>/dev/null
```


# Review Test Expectations

Example:

```python
def test_other_user_cannot_read_order():
    response = client.get("/orders/2001")
    assert response.status_code == 403
```

This gives useful information about intended authorisation behaviour.

It does not prove production enforcement without reviewing the implementation and, where appropriate, runtime behaviour.


# Documentation

Search:

```bash
rg -ni 'security|authentication|authorization|permission|admin' README* docs/ 2>/dev/null
```

Documentation can clarify intended design.


# Security Assumption Mismatch

An important finding pattern is:

```text
Documentation Says
       |
       v
Only Administrators
       |
       X
       |
Implementation Checks
       |
       v
Any Authenticated User
```

This can strengthen the interpretation of an access-control issue.


# Commit-Level Security Review

For a pull request or patch:

```bash
git diff <base>...<head>
```

Review:

```text
New routes

Changed permissions

New external requests

New file operations

New dependencies

Configuration changes

Removed validation

Changed authentication
```


# Identify Security-Relevant Changed Files

```bash
git diff --name-only <base>...<head>
```

Then focus on relevant areas.


# Search Only Changed Files

One practical workflow:

```bash
git diff --name-only <base>...<head> > changed-files.txt
```

Review the list before processing it further.


# Security Fix Review

When reviewing a security fix:

```text
Original Vulnerability
       |
       v
Root Cause
       |
       v
Patch
       |
       v
Does Patch Address Root Cause?
       |
       v
Alternative Paths?
       |
       v
Regression Tests?
```


# Patch Example

Before:

```python
if user:
    return get_admin_report()
```

After:

```python
if user and user.is_admin:
    return get_admin_report()
```

Review further:

```text
Is user.is_admin trustworthy?

Is this the only route?

Are related endpoints protected?

Is role information server-controlled?

Are tests present?
```


# Evidence Collection

For a source-code finding record:

```text
Finding ID

Repository

Branch

Commit

File

Line number

Function/class

Relevant source

Input source

Sensitive sink

Existing controls

Missing/insufficient control

Reachability

Runtime validation

Security consequence
```


# Record Repository State

```bash
git remote -v
```

```bash
git branch --show-current
```

```bash
git rev-parse HEAD
```


# Save Search Results

Example:

```bash
rg -n -C 5 'subprocess\.(run|Popen)|os\.system' \
  -g '*.py' . > command-execution-review.txt
```


# Evidence Should Include Context

Avoid evidence containing only:

```text
app/diagnostics.py:8:subprocess.run(...)
```

Prefer:

```text
File:
app/diagnostics.py

Lines:
5-13

Source:
request.args.get("host")

Sink:
subprocess.run(..., shell=True)

Observed validation:
None in reviewed function.

Additional validation:
Middleware and route configuration reviewed separately.
```


# Record Search Command

Keeping the exact command makes review reproducible.

Example:

```text
Search:
rg -n -C 8 'subprocess\.run' app/diagnostics.py
```


# Evidence and Sensitive Code

Do not unnecessarily copy entire proprietary source files into reports.

Capture only enough code to establish:

```text
Source

Data flow

Control

Sink

Security consequence
```


# Reporting Example - Command Injection Candidate

Weak:

> `subprocess.run` is insecure.

Better:

> The diagnostics handler reads the `host` query parameter and concatenates it into a command string passed to `subprocess.run()` with `shell=True`. No input validation was identified in the reviewed function. Runtime validation should confirm route reachability and upstream controls before the issue is assigned final severity.


# Reporting Example - Hardcoded Credential

Weak:

> Password found in Git.

Better:

> A credential was committed directly to the repository in `config/production.yml` and remained present in the reviewed revision. The value was configured for the production database account. The credential should be rotated and migrated to the organisation's approved secret-management mechanism.


# Historical Credential Reporting

If only history contains it:

> Repository history contains a previously committed credential that was removed from the current source tree. Removal from the latest revision does not invalidate the credential. Confirm whether the credential was rotated and whether historical repository access could have exposed it.


# Reporting Example - Missing Authorisation

Weak:

> No role check.

Better:

> The administrative export endpoint requires authentication but does not perform the role check applied to other administrative routes. As a result, any authenticated user reaching this handler enters the export workflow. Controlled runtime testing should confirm whether the endpoint returns administrative data to a standard user.


# Remediation Principles

Fix the underlying security boundary.

Examples:

```text
Command injection
    -> Avoid shell interpretation and validate structured input.

SQL injection
    -> Use parameterised queries.

Path traversal
    -> Enforce server-controlled base paths and validate file identifiers.

SSRF
    -> Restrict destinations and protocols using robust server-side controls.

Authorisation
    -> Enforce access decisions server side for every protected operation.

Secrets
    -> Rotate exposed credentials and use approved secret management.
```


# Retesting Source Changes

After remediation:

```text
Original Candidate
      |
      v
Review New Code
      |
      v
Repeat Original Search
      |
      v
Trace New Data Flow
      |
      v
Review Alternative Paths
      |
      v
Run Relevant Tests
      |
      v
Runtime Retest Where Appropriate
```


# Search Disappearance Is Not Proof

Suppose the original code contained:

```python
os.system(command)
```

After remediation:

```bash
rg -n 'os\.system' .
```

returns nothing.

This only proves:

```text
That exact pattern is no longer present.
```

The code might now use:

```python
subprocess.run(command, shell=True)
```

Therefore retesting must verify the root cause.


# Retest the Root Cause

For command injection:

```text
User Input
    |
    v
Can it still influence shell syntax?
```

For authorisation:

```text
Unauthorised Identity
    |
    v
Can it still access protected object/function?
```

For SSRF:

```text
User-Controlled Destination
    |
    v
Can server still reach prohibited destination?
```


# Useful Combined Searches

## Potential Secrets

```bash
rg --hidden \
  -g '!.git/**' \
  -ni 'password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key' .
```

## Authentication and Authorisation

```bash
rg -ni 'authenticate|authorize|permission|role|session|jwt|login' .
```

## Python Command Execution

```bash
rg -n -g '*.py' 'os\.system|subprocess\.(run|Popen|call|check_output|check_call)' .
```

## Python Request Input

```bash
rg -n -g '*.py' 'request\.(args|form|json|files|headers|cookies)' .
```

## Python HTTP Requests

```bash
rg -n -g '*.py' 'requests\.(get|post|put|patch|delete)|httpx\.' .
```

## JavaScript Process Execution

```bash
rg -n -g '*.js' -g '*.ts' 'exec\(|execSync\(|spawn\(|spawnSync\(' .
```

## JavaScript Request Input

```bash
rg -n -g '*.js' -g '*.ts' 'req\.(query|body|params|headers|cookies)' .
```

## File Handling

```bash
rg -ni 'filename|filepath|upload|download|path\.join|os\.path\.join' .
```

## Redirects

```bash
rg -ni 'redirect|return_url|returnUrl|next_url|nextUrl|callback_url|callbackUrl' .
```

## Debug

```bash
rg -ni 'debug|development|dev_mode|trace' .
```

## TLS Verification

```bash
rg -ni 'verify\s*=\s*False|rejectUnauthorized\s*:\s*false' .
```


# Git Quick Reference

| Objective | Command |
|---|---|
| Status | `git status` |
| Current branch | `git branch --show-current` |
| All branches | `git branch -a` |
| Current commit | `git rev-parse HEAD` |
| Short commit | `git rev-parse --short HEAD` |
| Recent history | `git log --oneline -20` |
| History graph | `git log --oneline --all --decorate --graph -30` |
| Show commit | `git show <commit>` |
| File history | `git log --oneline -- path/to/file` |
| File history with patches | `git log -p -- path/to/file` |
| Follow renamed file | `git log --follow -- path/to/file` |
| Blame file | `git blame path/to/file` |
| Blame lines | `git blame -L 20,40 path/to/file` |
| Current unstaged diff | `git diff` |
| Staged diff | `git diff --cached` |
| Compare revisions | `git diff <old> <new>` |
| Changed files | `git diff --name-only <old> <new>` |
| String history | `git log -S'text' --oneline --all` |
| Regex diff history | `git log -G'regex' --oneline --all` |
| Search commit message | `git log --grep='text' --oneline --all` |


# ripgrep Quick Reference

| Objective | Command |
|---|---|
| Search | `rg 'pattern' .` |
| Line numbers | `rg -n 'pattern' .` |
| Ignore case | `rg -ni 'pattern' .` |
| Fixed string | `rg -nF 'text' .` |
| Context | `rg -n -C 5 'pattern' .` |
| Before context | `rg -n -B 5 'pattern' .` |
| After context | `rg -n -A 5 'pattern' .` |
| Matching files | `rg -l 'pattern' .` |
| Count | `rg -c 'pattern' .` |
| Python only | `rg -n -t py 'pattern' .` |
| Glob | `rg -n -g '*.js' 'pattern' .` |
| Hidden files | `rg --hidden -n 'pattern' .` |
| Ignore ignore-files | `rg --no-ignore -n 'pattern' .` |
| List files | `rg --files` |
| File types | `rg --type-list` |
| Multiple patterns | `rg -e 'one' -e 'two' .` |


# Security Search Matrix

| Review Area | Useful Starting Terms |
|---|---|
| Secrets | `password`, `secret`, `token`, `api_key` |
| Authentication | `login`, `authenticate`, `session`, `jwt` |
| Authorisation | `authorize`, `role`, `permission`, `is_admin` |
| Commands | `subprocess`, `os.system`, `exec`, `Process.Start` |
| SQL | `execute`, `query`, `SqlCommand`, `prepareStatement` |
| Files | `open`, `filename`, `filepath`, `upload`, `download` |
| SSRF | `requests.get`, `fetch`, `HttpClient`, `WebClient` |
| Deserialization | `pickle`, `unserialize`, `readObject` |
| Templates | `render_template_string`, `Template`, `render` |
| Redirects | `redirect`, `next`, `returnUrl`, `callbackUrl` |
| Crypto | `md5`, `sha1`, `encrypt`, `random` |
| Logging | `logger`, `logging`, `console.log` |
| Debug | `debug`, `development`, `trace` |
| CORS | `cors`, `allow_origins` |
| TLS | `verify=False`, `rejectUnauthorized: false` |


# Result Interpretation Matrix

| Search Result | Initial Interpretation | Further Question |
|---|---|---|
| `subprocess.run(["uptime"])` | Command execution | Is input variable? |
| `subprocess.run(cmd, shell=True)` | Strong review candidate | Can untrusted input reach `cmd`? |
| `cursor.execute(query)` | Database operation | How was `query` constructed? |
| `open(filename)` | File operation | Who controls `filename`? |
| `requests.get(url)` | Outbound request | Who controls `url`? |
| `password = os.environ[...]` | External secret source | How is environment secret managed? |
| `password = "..."` | Potential hardcoded secret | Test/example/real credential? |
| `redirect(next_url)` | Redirect candidate | Is destination validated? |
| `is_admin` | Authorisation-related logic | Is check server side and complete? |
| `verify=False` | TLS verification disabled | Production path or test code? |
| `DEBUG=True` | Debug configuration candidate | Is it deployed? |
| `MD5` | Weak-algorithm keyword | What is it used for? |


# Source Review Checklist

## Repository

- [ ] Repository root identified
- [ ] Remote recorded
- [ ] Branch recorded
- [ ] Commit hash recorded
- [ ] Repository structure mapped
- [ ] Languages/frameworks identified
- [ ] Dependency files identified
- [ ] Configuration files identified
- [ ] CI/CD configuration identified

## Attack Surface

- [ ] Routes identified
- [ ] API endpoints identified
- [ ] Authentication identified
- [ ] Authorisation identified
- [ ] Administrative functionality identified
- [ ] Upload/download functionality identified
- [ ] External network requests identified
- [ ] Sensitive file operations identified

## Input

- [ ] Query parameters identified
- [ ] Form input identified
- [ ] JSON input identified
- [ ] Headers identified
- [ ] Cookies identified
- [ ] File uploads identified
- [ ] External data sources identified

## Sensitive Operations

- [ ] Command execution reviewed
- [ ] SQL/database operations reviewed
- [ ] File operations reviewed
- [ ] Template rendering reviewed
- [ ] Deserialization reviewed
- [ ] Redirects reviewed
- [ ] Outbound requests reviewed
- [ ] Cryptographic operations reviewed

## Secrets

- [ ] Current tree searched
- [ ] Hidden files considered
- [ ] Environment files reviewed
- [ ] Configuration files reviewed
- [ ] Private keys searched
- [ ] Git history considered
- [ ] Branches considered
- [ ] Credential rotation considered where relevant

## Git

- [ ] Recent commits reviewed
- [ ] Security-related commits searched
- [ ] Sensitive file history reviewed
- [ ] Relevant lines blamed to commit
- [ ] Historical implementation reviewed
- [ ] Relevant branches reviewed

## Validation

- [ ] Search result contextualised
- [ ] Input source identified
- [ ] Sensitive sink identified
- [ ] Data flow understood
- [ ] Validation identified
- [ ] Authentication considered
- [ ] Authorisation considered
- [ ] Reachability considered
- [ ] Environment considered
- [ ] Alternative explanation considered
- [ ] Runtime validation performed where authorised and necessary

## Evidence

- [ ] Repository recorded
- [ ] Branch recorded
- [ ] Commit recorded
- [ ] File recorded
- [ ] Lines recorded
- [ ] Search command recorded
- [ ] Relevant code captured
- [ ] Sensitive information redacted
- [ ] Security consequence documented

## Retest

- [ ] Remediated code reviewed
- [ ] Original search repeated
- [ ] Alternative sinks reviewed
- [ ] Data flow retraced
- [ ] Security tests reviewed
- [ ] Runtime behaviour retested where appropriate
- [ ] Root cause confirmed resolved


# Practical Review Model

```text
                    SOURCE CODE
                         |
                         v
                 REPOSITORY CONTEXT
                         |
                         v
                    ENTRY POINT
                         |
                         v
                  UNTRUSTED INPUT
                         |
                         v
                  TRANSFORMATIONS
                         |
                         v
                SECURITY CONTROLS
                         |
                         v
                 SENSITIVE SINK
                         |
              +----------+----------+
              |                     |
              v                     v
         SAFE FLOW              CANDIDATE
                                    |
                                    v
                             GIT HISTORY
                                    |
                                    v
                              REACHABILITY
                                    |
                                    v
                               VALIDATION
                                    |
                                    v
                               EVIDENCE
```


# Final Testing Principle

The most important rule when using ripgrep for security review is:

```text
A MATCH IS A LEAD.
```

Not:

```text
A MATCH IS A VULNERABILITY.
```

For every interesting search result ask:

```text
What exactly matched?

Is this application code?

Is it production code?

Is the code reachable?

What data enters this function?

Who controls that data?

How is the data transformed?

Is validation performed?

Is authentication required?

Is authorisation enforced?

What sensitive operation receives the data?

Does the framework provide protection?

Does configuration change the behaviour?

What does Git history reveal?

Can the security consequence be demonstrated?

What evidence supports the conclusion?
```

The strongest workflow is:

```text
rg
 |
 v
Find Candidate
 |
 v
Read Context
 |
 v
Trace Source
 |
 v
Trace Sink
 |
 v
Identify Controls
 |
 v
Review Git History
 |
 v
Validate
 |
 v
Conclude
```

This prevents the common source-review mistake of converting security-sensitive API usage directly into findings.


# Related Cheatsheets

- [Burp Suite Cheatsheet](burp-suite.md)
- [Web Application Security Cheatsheet](web.md)
- [Linux Cheatsheet](linux.md)
- [Windows Cheatsheet](windows.md)
- [PowerShell Cheatsheet](powershell.md)
- [Networking Cheatsheet](networking.md)
- [curl Cheatsheet](curl.md)


# Related Notes

- [Source Code Review](../source-code-review/index.md)
- [Static Analysis](../source-code-review/static-analysis/index.md)
- [ripgrep](../source-code-review/static-analysis/ripgrep.md)
- [Web Application Security](../web/index.md)
- [Command Injection](../web/command-injection.md)
- [Path Traversal](../web/path-traversal.md)
- [File Upload](../web/file-upload.md)
- [SSRF](../web/ssrf.md)
- [Deserialization](../web/deserialization.md)
- [Open Redirect](../web/open-redirect.md)


# References

- [ripgrep GitHub Repository](https://github.com/BurntSushi/ripgrep){ target="_blank" rel="noopener noreferrer" }
- [ripgrep User Guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md){ target="_blank" rel="noopener noreferrer" }
- [Git Documentation](https://git-scm.com/doc){ target="_blank" rel="noopener noreferrer" }
- [git-log Documentation](https://git-scm.com/docs/git-log){ target="_blank" rel="noopener noreferrer" }
- [git-diff Documentation](https://git-scm.com/docs/git-diff){ target="_blank" rel="noopener noreferrer" }
- [git-show Documentation](https://git-scm.com/docs/git-show){ target="_blank" rel="noopener noreferrer" }
- [git-blame Documentation](https://git-scm.com/docs/git-blame){ target="_blank" rel="noopener noreferrer" }
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }


!!! tip "Search broadly, validate narrowly"

    Broad searches are useful for identifying candidates. Once a security-sensitive match is found, narrow the review to the relevant function, data flow, security control and runtime context.


!!! tip "Record the commit hash"

    A file and line number can change after the assessment. Recording the repository commit makes source-code evidence reproducible.


!!! tip "Use Git history as context"

    Git history can explain why a security-sensitive implementation exists, identify earlier versions and reveal whether a credential or vulnerable pattern previously existed even after it disappears from the current tree.


!!! warning "Do not report regex matches as vulnerabilities"

    `subprocess`, `open`, `requests.get`, `MD5`, `password` and similar terms identify areas worth reviewing. The security conclusion depends on how the code is actually used.


!!! warning "Removed secrets may still matter"

    Deleting a credential from the latest source revision does not invalidate it. If a real secret was committed, credential rotation and exposure analysis are generally more important than simply removing the string from the current file.
