---
title: linux-smart-enumeration
description: Practical linux-smart-enumeration reference for authorised Linux privilege escalation enumeration, focused triage, manual validation, evidence collection, false-positive analysis, and integration with wider Linux security review.
---

# linux-smart-enumeration

linux-smart-enumeration, commonly abbreviated as **LSE**, is a Linux enumeration script designed to identify local system conditions that may be relevant to privilege escalation.

It provides a focused way to review areas such as:

- users and groups;
- sudo configuration;
- SUID and SGID binaries;
- Linux capabilities;
- cron and scheduled execution;
- services and processes;
- filesystem permissions;
- writable files and directories;
- environment configuration;
- credentials;
- mounts;
- networking;
- containers;
- security-relevant local configuration.

LSE is best treated as a **triage and enumeration tool**.

It helps answer:

> Which parts of this Linux host deserve closer privilege escalation analysis?

It does not automatically prove exploitability.

```text
Linux Host
   |
   v
LSE
   |
   +-- Identity
   +-- sudo
   +-- SUID / SGID
   +-- Capabilities
   +-- Cron
   +-- Services
   +-- Filesystem
   +-- Credentials
   +-- Mounts
   +-- Environment
   |
   v
Candidate Conditions
   |
   v
Manual Validation
   |
   v
Privilege Escalation Conclusion
```

!!! warning "Authorised testing only"
    Use linux-smart-enumeration only on systems where local security testing is explicitly authorised. Enumeration scripts may access sensitive configuration and generate security telemetry. Review the rules of engagement before transferring or executing third-party tooling.

---

# Where LSE Fits

LSE normally follows initial local access and a basic manual review of the current Linux context.

```text
Initial Access
      |
      v
Current User
      |
      v
Manual Baseline
      |
      v
LSE
      |
      v
Candidate Conditions
      |
      v
Native Linux Validation
      |
      v
Confirm or Reject
```

Related notes:

[Privilege Escalation Tools](index.md)

[Linux Privilege Escalation](../../linux/privilege-escalation.md)

[Linux Enumeration](../../linux/enumeration.md)

[Linux Privilege Escalation Explorer](../../privesc/linux.md)

---

# Official Project

linux-smart-enumeration is maintained in the following repository:

[linux-smart-enumeration - GitHub](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

Use the official project or a trusted internal mirror.

Avoid random modified copies from unknown repositories.

---

# What LSE Does

LSE performs a series of checks intended to highlight potentially interesting local conditions.

Conceptually:

```text
System State
    |
    +-- Users
    +-- Groups
    +-- sudo
    +-- Files
    +-- Permissions
    +-- SUID
    +-- Capabilities
    +-- Cron
    +-- Services
    +-- Environment
    +-- Credentials
    |
    v
LSE Checks
    |
    v
Prioritised Output
```

The output is intended to reduce the amount of manual searching required.

---

# LSE vs LinPEAS

LSE and LinPEAS overlap but have different styles.

```text
LinPEAS
   |
   +-- very broad enumeration
   +-- large output
   +-- extensive heuristics

LSE
   |
   +-- focused enumeration
   +-- structured levels
   +-- easier targeted review
```

A useful workflow is:

```text
LSE
   |
   v
Focused Candidate Set
   |
   v
LinPEAS
   |
   v
Additional Coverage
   |
   v
Manual Validation
```

or the reverse:

```text
LinPEAS
   |
   v
Broad Candidate Set
   |
   v
LSE
   |
   v
Focused Cross-Check
```

Related note:

[LinPEAS](linpeas.md)

---

# Before Running LSE

Always record the current user context first.

Run:

```bash
whoami
```

Then:

```bash
id
```

And:

```bash
groups
```

Useful questions include:

```text
Which user am I?

Which groups do I belong to?

Do I have sudo rights?

Am I inside a container?

Do I belong to a privileged management group?
```

This baseline is essential when interpreting tool output.

---

# Record Host Context

Useful commands include:

```bash
hostname
```

```bash
uname -a
```

```bash
cat /etc/os-release
```

This records:

- hostname;
- kernel;
- operating system;
- distribution;
- architecture context.

---

# Obtaining LSE

Prefer the official repository.

If downloaded to a controlled workstation, preserve:

```text
Source
Revision
Hash where relevant
Transfer path
Execution time
```

Tool provenance improves reproducibility.

---

# Common Script Name

The project is commonly used through:

```text
lse.sh
```

The exact script behaviour can change between revisions.

Always review the version being used.

---

# Basic Execution

If the script is executable:

```bash
./lse.sh
```

Alternatively:

```bash
bash lse.sh
```

If required:

```bash
chmod +x lse.sh
```

Then:

```bash
./lse.sh
```

Use the least intrusive execution approach permitted by the environment.

---

# Help

Inspect the script help:

```bash
./lse.sh -h
```

or:

```bash
bash lse.sh -h
```

Use the tool's built-in help for the exact options supported by the current version.

---

# Level-Based Enumeration

One of LSE's useful concepts is adjusting how much detail is displayed.

Depending on the version, LSE supports levels intended to control the amount or depth of output.

Conceptually:

```text
Lower Level
   |
   +-- more important findings
   +-- less noise

Higher Level
   |
   +-- more detail
   +-- broader context
```

Always verify exact supported values with:

```bash
./lse.sh -h
```

This makes LSE particularly useful when a quick triage pass is preferred before deeper enumeration.

---

# Start Focused

A good workflow is:

```text
Start with focused output
        |
        v
Review high-value candidates
        |
        v
Increase detail if needed
```

rather than immediately generating the maximum possible output.

This reduces analysis noise.

---

# Save Output

For later review:

```bash
./lse.sh | tee lse-output.txt
```

If using options:

```bash
./lse.sh <options> | tee lse-output.txt
```

The output may contain sensitive system information.

Protect it appropriately.

---

# Sensitive Output

LSE may expose:

- usernames;
- group memberships;
- credentials;
- configuration;
- file paths;
- network information;
- sensitive local files.

Do not:

- commit raw output to Git;
- upload it to public services;
- attach full output to reports;
- share it beyond the authorised team.

Extract relevant evidence only.

---

# Identity Checks

LSE can help highlight current user context.

Validate manually:

```bash
id
```

Representative output:

```text
uid=1001(tester) gid=1001(tester) groups=1001(tester),27(sudo)
```

This result may immediately show important group membership.

---

# Groups

Group membership can significantly affect local privilege.

Potentially sensitive group categories may include:

```text
sudo
docker
lxd
disk
backup
adm
```

Exact impact depends on the operating system and environment.

Do not report group membership alone.

Determine what the group can actually control.

---

# sudo

sudo is one of the highest-value Linux privilege escalation areas.

Always validate:

```bash
sudo -l
```

Questions include:

```text
Which commands are allowed?

As which user?

Is a password required?

Are arguments restricted?

Are wildcards used?

Are environment variables preserved?
```

Related note:

[Linux sudo](../../linux/sudo.md)

---

# sudo Candidate Model

```text
sudo Rule
   |
   v
Allowed Binary
   |
   v
Allowed Arguments
   |
   v
Binary Behaviour
   |
   v
Can Privilege Boundary Be Crossed?
```

The sudo entry itself is not always vulnerable.

---

# NOPASSWD

LSE may highlight sudo commands that use:

```text
NOPASSWD
```

This means the user can execute the permitted sudo command without entering a password.

The impact still depends on what that command permits.

---

# sudo Wildcards

Wildcard rules deserve careful analysis.

Example concept:

```text
/usr/local/bin/backup *
```

Investigate:

- argument parsing;
- file path control;
- option injection;
- command behaviour.

A wildcard is only part of the potential chain.

---

# GTFOBins

GTFOBins can help research security-sensitive functionality in Linux binaries.

Examples include:

- sudo behaviour;
- SUID behaviour;
- command execution;
- file read;
- file write.

Reference:

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

Use it as a research aid.

Do not treat a GTFOBins entry as proof that the local configuration is exploitable.

---

# SUID

LSE may highlight SUID binaries.

Enumerate manually:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Typical legitimate examples may include:

```text
/usr/bin/passwd
/usr/bin/su
/usr/bin/sudo
```

The presence of SUID alone is not a vulnerability.

Related note:

[Linux SUID and SGID](../../linux/suid-sgid.md)

---

# Validate SUID

Inspect the binary:

```bash
ls -l /path/to/binary
```

Example:

```text
-rwsr-xr-x 1 root root 123456 Jan 1 12:00 /path/to/binary
```

Then determine:

```text
Who owns it?

What does it do?

Does it retain effective UID?

Does it invoke external commands?

Does it process user-controlled input?
```

---

# Custom SUID Binaries

Custom SUID programs often deserve higher priority than standard distribution binaries.

Examples:

```text
/opt/vendor/helper
/usr/local/bin/custom-tool
```

Review:

- ownership;
- permissions;
- file type;
- strings or source where authorised;
- arguments;
- privileged operations.

---

# SGID

Enumerate SGID binaries:

```bash
find / -perm -2000 -type f 2>/dev/null
```

SGID changes effective group context.

The security impact depends on what access that group provides.

---

# Linux Capabilities

LSE may highlight binaries with file capabilities.

Validate:

```bash
getcap -r / 2>/dev/null
```

For one binary:

```bash
getcap /path/to/binary
```

Related note:

[Linux Capabilities](../../linux/capabilities.md)

---

# Capability Analysis

A useful model is:

```text
Binary
   |
   v
Capability
   |
   v
Available Functionality
   |
   v
User-Controlled Input
   |
   v
Potential Impact
```

A capability name alone does not prove escalation.

---

# Scheduled Jobs

LSE can help identify scheduled execution.

Potential mechanisms include:

```text
cron
anacron
systemd timers
custom application schedulers
```

Related note:

[Linux Scheduled Jobs](../../linux/scheduled-jobs.md)

---

# Cron

Inspect:

```bash
cat /etc/crontab
```

and where authorised:

```bash
ls -la /etc/cron.d/
```

Also:

```bash
crontab -l
```

The key questions are:

```text
Who executes it?

What executes?

Can the current user influence it?

How often does it run?
```

---

# Root Cron Jobs

A root cron job is not automatically vulnerable.

Example:

```text
* * * * * root /opt/scripts/backup.sh
```

Validate:

```bash
ls -l /opt/scripts/backup.sh
```

Then:

```bash
namei -l /opt/scripts/backup.sh
```

Review the entire path.

---

# Parent Directory Analysis

`namei -l` is especially useful.

Example:

```bash
namei -l /opt/scripts/backup.sh
```

This can reveal:

```text
/
opt
scripts
backup.sh
```

with permissions at each level.

A protected file may still be replaceable if the parent directory grants sufficient rights.

---

# systemd Services

LSE may highlight service-related configuration.

List services:

```bash
systemctl list-units --type=service
```

Inspect a specific service:

```bash
systemctl cat example.service
```

Review:

```text
User=
Group=
ExecStart=
Environment=
WorkingDirectory=
```

The key security question is:

> Can the current user influence something that a privileged service consumes?

---

# systemd Timers

List:

```bash
systemctl list-timers --all
```

Inspect the corresponding timer and service units.

A timer alone is not a vulnerability.

Focus on the privileged execution chain.

---

# Filesystem Permissions

LSE can highlight potentially interesting local permissions.

Relevant categories include:

- writable files;
- writable directories;
- executable scripts;
- service resources;
- cron resources;
- configuration.

Related note:

[Linux Filesystem Permissions](../../linux/filesystem-permissions.md)

---

# Basic File Review

Use:

```bash
ls -l /path/to/file
```

and:

```bash
stat /path/to/file
```

This reveals:

- owner;
- group;
- permissions;
- timestamps;
- metadata.

---

# ACLs

POSIX ACLs can grant permissions beyond traditional mode bits.

Inspect:

```bash
getfacl /path/to/file
```

Effective permission analysis should consider ACLs when present.

---

# Writable Files

A writable file is only significant if a privileged process trusts or executes it.

```text
Writable File
    |
    v
Privileged Consumer?
    |
    +-- No -> may be irrelevant
    |
    +-- Yes -> investigate
```

---

# Writable Directories

Common writable directories include:

```text
/tmp
/var/tmp
/dev/shm
```

These are intentionally writable on many Linux systems.

Their presence is not a vulnerability.

The relevant question is whether a privileged component trusts user-controlled content stored there.

---

# Temporary Directory Risks

Potential issues can arise when privileged processes use predictable or insecure temporary files.

Relevant questions include:

```text
Does privileged software create predictable files?

Does it follow symlinks?

Are permissions checked?

Can another user replace the file?
```

Do not perform destructive race-condition testing without explicit approval.

---

# PATH

Inspect:

```bash
echo "$PATH"
```

A clearer view:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

LSE may highlight writable PATH locations.

This is only relevant when a privileged process resolves a command through that PATH.

---

# PATH Hijacking Model

```text
Privileged Script
      |
      v
Calls:
backup
      |
      v
PATH Search
      |
      v
Writable Directory
      |
      v
User-Controlled Executable
```

The entire chain must be demonstrated.

---

# Absolute Paths

Privileged scripts should generally use explicit executable paths where practical.

Compare:

```bash
tar
```

with:

```bash
/usr/bin/tar
```

The latter does not depend on PATH lookup.

This can reduce PATH-based ambiguity.

---

# Environment Variables

Inspect:

```bash
env
```

or:

```bash
printenv
```

Potentially relevant variables include:

- PATH;
- application configuration;
- credentials;
- runtime options.

Security relevance depends on whether privileged processes inherit or trust them.

---

# Credentials

LSE may identify potential secrets in:

- configuration files;
- shell history;
- environment variables;
- scripts;
- backup files;
- application directories.

Related note:

[Linux Credentials](../../linux/credentials.md)

---

# Shell History

Common locations include:

```text
~/.bash_history
~/.zsh_history
```

History can contain:

- administrative commands;
- credentials supplied inline;
- internal paths;
- connection information.

Treat it as sensitive evidence.

---

# SSH Material

Potentially sensitive files include:

```text
~/.ssh/id_rsa
~/.ssh/id_ed25519
~/.ssh/config
~/.ssh/authorized_keys
```

Do not assume a private key is reusable.

Consider:

- passphrase;
- owner;
- destination;
- scope.

---

# Configuration Files

Potential secrets may appear in:

```text
.env
config files
application YAML/JSON
database configuration
service files
```

The finding may be insecure local access to secrets rather than privilege escalation itself.

---

# Processes

Inspect:

```bash
ps aux
```

or:

```bash
ps -ef
```

Look for:

- root-owned custom processes;
- command-line secrets;
- scripts;
- application paths;
- interpreters;
- unusual service commands.

---

# Process Command Lines

A root process may expose an interesting path.

Example:

```text
root /usr/bin/python3 /opt/app/service.py
```

Next inspect:

```bash
ls -l /opt/app/service.py
```

and its parent directories.

The process identifies the privileged consumer.

---

# Listening Services

Inspect:

```bash
ss -lntup
```

where permitted.

Interesting services may include:

- local administration interfaces;
- databases;
- management daemons;
- custom local APIs.

A listening service is not automatically a privilege escalation route.

---

# Unix Domain Sockets

Privileged local services may expose Unix sockets.

Relevant questions include:

```text
Who owns the socket?

Which group can access it?

What functionality does the service expose?
```

A writable or accessible management socket can be more important than a network port.

---

# Mounts

Inspect:

```bash
findmnt
```

or:

```bash
mount
```

Mounts can reveal:

- NFS;
- CIFS;
- bind mounts;
- removable media;
- containers;
- unusual filesystem options.

---

# Mount Options

Relevant options may affect:

- execution;
- device access;
- SUID behaviour;
- write capability.

Examples include:

```text
ro
rw
nosuid
noexec
nodev
```

Do not judge file permissions without considering mount options.

---

# /etc/fstab

Where authorised:

```bash
cat /etc/fstab
```

This can reveal:

- persistent mounts;
- network shares;
- mount options;
- credential references.

Treat credential material carefully.

---

# NFS

NFS mounts may create privilege-related conditions depending on server export configuration and local mount behaviour.

Do not infer server-side configuration from the client mount alone.

Assess the actual trust relationship.

---

# Containers

LSE may identify container-related context.

Potential technologies include:

- Docker;
- LXC;
- LXD;
- containerd;
- Kubernetes.

Root inside a container is not automatically root on the host.

---

# Docker Group

Check:

```bash
id
```

If the current user belongs to:

```text
docker
```

determine whether the Docker daemon is accessible.

Check socket permissions:

```bash
ls -l /var/run/docker.sock
```

Do not modify containers merely to prove access unless explicitly authorised.

---

# Docker Socket

Conceptually:

```text
Current User
     |
     v
Docker Socket
     |
     v
Docker Daemon
     |
     v
Host Resources
```

Access to the Docker daemon can represent a major trust boundary.

The finding should describe that control relationship.

---

# LXD / LXC

Membership in container-management groups may grant powerful host-level capabilities.

Validate actual access before reporting.

Do not assume group membership alone is sufficient.

---

# Kubernetes

Container environments may expose:

- service-account tokens;
- mounted secrets;
- namespace information;
- API endpoints.

Ensure cloud/Kubernetes resources are within assessment scope before further interaction.

---

# Kernel Information

LSE may provide kernel-related clues.

Validate:

```bash
uname -r
```

and:

```bash
cat /etc/os-release
```

Do not map a kernel version directly to exploitability.

Linux distributions often backport security patches.

---

# Kernel Research Workflow

```text
Kernel Version
    |
    v
Distribution
    |
    v
Package Version
    |
    v
Vendor Advisory
    |
    v
Configuration
    |
    v
Applicability
```

Kernel exploitation can destabilise systems and should only be performed when specifically authorised.

---

# Installed Software

LSE may help identify installed software or unusual applications.

Custom privileged applications are often worth prioritising.

Review:

- binary path;
- owner;
- configuration;
- service identity;
- writable resources.

---

# Old Version Does Not Equal Vulnerable

Avoid:

```text
Package version looks old
       |
       v
Report CVE
```

Use:

```text
Installed package
       |
       v
Distribution package revision
       |
       v
Vendor security advisory
       |
       v
Applicability
```

---

# Security Controls

Linux security controls can significantly affect exploitability.

Potential controls include:

- SELinux;
- AppArmor;
- seccomp;
- no_new_privs;
- mount restrictions.

Related note:

[Linux Security Controls](../../linux/security-controls.md)

---

# SELinux

Check where installed:

```bash
getenforce
```

Possible results include:

```text
Enforcing
Permissive
Disabled
```

SELinux can restrict privileged process behaviour.

Its presence should be included in the analysis.

---

# AppArmor

Where available:

```bash
aa-status
```

Some systems may require elevated access for complete output.

Do not assume AppArmor blocks every candidate.

Review the actual profile applied to the privileged process.

---

# no_new_privs

`no_new_privs` can prevent certain privilege transitions.

Its presence may affect:

- SUID;
- capabilities;
- sandboxed applications.

Consider this when a privilege transition does not behave as expected.

---

# seccomp

seccomp may restrict available system calls.

This is common in containers and sandboxed services.

It can change practical exploitability without fixing the underlying permission weakness.

---

# Read-Only Mounts

A path may appear writable according to mode bits but reside on a read-only mount.

Check:

```bash
findmnt
```

Actual write capability is what matters.

---

# LSE Output Levels

LSE's focused output can be useful when triaging a host under time pressure.

A practical approach is:

```text
Low-noise pass
      |
      v
Review strongest candidates
      |
      v
Increase detail
      |
      v
Manual validation
```

Check exact supported options:

```bash
./lse.sh -h
```

---

# Review by Category

A useful review order is:

```text
1. Identity and groups
2. sudo
3. SUID / SGID
4. Capabilities
5. Cron / systemd
6. Filesystem
7. Processes
8. Credentials
9. Containers
10. Mounts
11. Kernel / software
12. Security controls
```

This keeps the analysis structured.

---

# Searching Saved Output

If results are stored in:

```text
lse-output.txt
```

search:

```bash
grep -i "sudo" lse-output.txt
```

```bash
grep -i "suid" lse-output.txt
```

```bash
grep -i "writ" lse-output.txt
```

```bash
grep -i "capab" lse-output.txt
```

Do not remove the surrounding context from interesting matches.

---

# Candidate Evaluation Model

For each LSE result, answer:

| Question | Answer |
|---|---|
| What did LSE identify? | |
| Can the current user influence it? | |
| Which permission proves this? | |
| Which privileged process consumes it? | |
| Which user executes that process? | |
| Can the process be triggered? | |
| Which security controls apply? | |
| What privilege would result? | |

This turns tool output into security analysis.

---

# User Influence

The first major question is:

> Can the current user actually control the candidate resource?

Possible control can include:

- write;
- modify;
- replace;
- delete;
- execute with elevated context;
- interact through socket or daemon;
- change configuration.

Without user influence, the candidate usually does not represent privilege escalation.

---

# Privileged Consumer

The next question is:

> Which higher-privileged component trusts or executes the resource?

Examples include:

```text
root cron
root systemd service
sudo
SUID binary
container daemon
```

A writable file without a privileged consumer may be irrelevant.

---

# Trigger

Determine how the privileged action occurs.

Possible triggers include:

```text
scheduled execution
service restart
system reboot
administrator action
user login
manual sudo execution
```

This affects practical risk.

---

# Security Control Context

Ask:

```text
Does SELinux restrict the process?

Does AppArmor restrict it?

Does no_new_privs apply?

Is filesystem mounted noexec/nosuid/read-only?
```

These controls may affect practical exploitation.

---

# Representative sudo Scenario

LSE highlights:

```text
sudo permission:
(root) NOPASSWD: /usr/local/bin/backup
```

Validate:

```bash
sudo -l
```

Then inspect:

```bash
ls -l /usr/local/bin/backup
```

Determine:

```text
What does the command do?

Can arguments be controlled?

Does it invoke another program?

Does it access user-controlled files?

Does it provide functionality beyond the intended task?
```

Only then determine whether privilege escalation exists.

---

# Representative SUID Scenario

LSE highlights:

```text
/usr/local/bin/helper
```

Validate:

```bash
ls -l /usr/local/bin/helper
```

Suppose:

```text
-rwsr-xr-x 1 root root ...
```

Next determine:

```text
What operations does the helper expose?

Does it retain EUID 0?

Does it trust environment variables?

Does it invoke commands without full paths?
```

Do not report based on SUID alone.

---

# Representative Cron Scenario

LSE identifies:

```text
root cron:
* * * * * /opt/backup/backup.sh
```

Check:

```bash
ls -l /opt/backup/backup.sh
```

Then:

```bash
namei -l /opt/backup/backup.sh
```

If a parent directory is writable by the tested user, that may create a security-relevant execution path.

---

# Representative Capability Scenario

LSE reports:

```text
/usr/local/bin/example cap_dac_override=ep
```

Validate:

```bash
getcap /usr/local/bin/example
```

Then determine whether the executable's functionality allows the current user to misuse that capability.

Do not treat the capability string as a complete finding.

---

# Representative Docker Scenario

LSE highlights Docker access.

Validate:

```bash
id
```

and:

```bash
ls -l /var/run/docker.sock
```

If the current user has access to the host Docker daemon, the risk may be significant.

Document the control relationship rather than merely saying:

```text
User is in docker group.
```

---

# Representative Credential Scenario

LSE identifies:

```text
password=example
```

inside an application configuration file.

Validate:

```text
Who owns the file?

Why can current user read it?

Is the credential active?

Does it provide additional privilege?

Is authentication testing needed?
```

The underlying weakness may be insecure local secret storage.

---

# Representative Negative Scenario

LSE highlights a root-owned script as potentially interesting.

Manual validation:

```bash
ls -l /opt/scripts/backup.sh
```

and:

```bash
namei -l /opt/scripts/backup.sh
```

show that neither the file nor any relevant parent directory is writable.

Conclusion:

```text
The candidate was reviewed, but the tested user could not influence the
resource or its execution path. The suspected privilege escalation
condition was not confirmed.
```

---

# False Positives

LSE can highlight benign or non-exploitable conditions.

Common examples include:

- legitimate SUID binaries;
- intentionally writable temporary directories;
- harmless group membership;
- inactive cron jobs;
- writable files with no privileged consumer;
- capabilities that expose no useful operation;
- stale credentials;
- inaccessible container-management services.

Manual validation is required.

---

# False Negatives

LSE can also miss real privilege escalation paths.

Possible reasons include:

- proprietary applications;
- custom scripts;
- unusual service directories;
- transient resources;
- custom IPC;
- uncommon ACLs;
- application-specific logic.

A clean LSE result does not prove the host is secure.

---

# LSE Does Not Replace Manual Enumeration

Do not stop at:

```text
LSE completed
```

Continue reviewing:

```text
Identity
sudo
SUID
Capabilities
Cron
systemd
Filesystem
Processes
Credentials
Containers
Mounts
Security Controls
```

Manual knowledge remains essential.

---

# LSE and LinPEAS Correlation

Example:

```text
LSE:
Writable cron script

LinPEAS:
Same cron script highlighted

Manual:
Permissions confirm write access

Cron:
Runs as root
```

This provides strong supporting evidence.

The actual finding remains the insecure privileged scheduled execution path.

---

# LSE and Native Tools

A strong model is:

```text
LSE
  |
  v
Candidate
  |
  v
Native Validation
  |
  +-- sudo
  +-- ls
  +-- stat
  +-- namei
  +-- getfacl
  +-- getcap
  +-- systemctl
  +-- findmnt
  |
  v
Conclusion
```

---

# Evidence Collection

For a validated candidate, retain:

```text
Current user:
Groups:
LSE result:
Affected path/object:
Owner:
Group:
Permissions:
ACL:
Privileged consumer:
Execution user:
Trigger:
Security controls:
Observed impact:
```

Example:

```text
Current user:
tester

Candidate:
Writable cron script

Path:
/opt/scripts/backup.sh

Consumer:
root cron

Trigger:
Every minute

Validation:
Current user had group write permission over the script.
```

---

# Evidence Should Explain the Chain

Weak:

```text
Screenshot of LSE warning
```

Strong:

```text
LSE candidate
      |
      v
ls/stat/getfacl
      |
      v
cron/systemd configuration
      |
      v
root execution identity
      |
      v
trigger
      |
      v
impact
```

The evidence should independently support the conclusion.

---

# Reporting

Avoid:

```text
LSE found a privilege escalation vulnerability.
```

Prefer:

```text
A script executed by a root-owned scheduled task was writable by the
tested standard user. Native filesystem permission checks confirmed
that the low-privileged user could influence content subsequently
executed in the root context.
```

The finding describes the actual security condition.

---

# Reporting an Unconfirmed Candidate

Example:

```text
linux-smart-enumeration highlighted a custom SUID binary. Manual review
confirmed the SUID bit was present, but testing did not identify any
user-controlled functionality that could be used to cross the intended
privilege boundary. A privilege escalation condition was therefore not
confirmed.
```

---

# Remediation Principles

The central remediation principle is:

> Low-privileged users should not be able to influence resources or interfaces trusted by higher-privileged processes.

Typical areas include:

- sudo;
- SUID/SGID;
- capabilities;
- cron;
- systemd;
- filesystem permissions;
- credentials;
- container management.

---

# sudo Remediation

Typical measures include:

- minimise allowed commands;
- restrict arguments;
- avoid unnecessary wildcards;
- avoid broad `NOPASSWD`;
- use least privilege.

---

# SUID / SGID Remediation

Typical measures include:

- remove unnecessary SUID/SGID bits;
- restrict execution;
- redesign privileged helpers;
- validate untrusted input;
- drop privileges as early as possible.

---

# Capability Remediation

Typical measures include:

- remove unnecessary capabilities;
- assign minimum capabilities;
- restrict binary execution;
- review custom privileged binaries.

---

# Cron Remediation

Typical measures include:

- protect scripts;
- protect parent directories;
- use absolute executable paths;
- restrict ownership;
- avoid root execution where unnecessary.

---

# systemd Remediation

Typical measures include:

- secure unit files;
- secure referenced scripts;
- use dedicated service identities;
- protect environment files;
- minimise privilege.

---

# Filesystem Remediation

Typical measures include:

- remove unnecessary group/world write;
- correct owner/group;
- review ACLs;
- protect parent directories;
- avoid privileged trust in shared writable locations.

---

# Credential Remediation

Typical measures include:

- remove plaintext credentials;
- rotate exposed secrets;
- restrict local read access;
- use secret-management mechanisms;
- remove stale backups.

---

# Container Remediation

Typical measures include:

- restrict Docker/LXD group membership;
- protect daemon sockets;
- remove unnecessary privileged container access;
- minimise host mounts;
- follow least privilege.

---

# Retesting

Do not retest only by rerunning LSE.

For a corrected file:

```bash
ls -l /path/to/file
```

```bash
getfacl /path/to/file
```

For a corrected cron path:

```bash
namei -l /path/to/script
```

For sudo:

```bash
sudo -l
```

For capabilities:

```bash
getcap /path/to/binary
```

Then optionally rerun LSE as a secondary regression check.

---

# LSE in Purple Teaming

LSE can be useful during purple-team exercises where local enumeration visibility is being evaluated.

```text
LSE
 |
 v
Local Enumeration
 |
 v
Audit / EDR Telemetry
 |
 v
Detection Review
```

Related notes:

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

The activity should be coordinated before execution.

---

# Telemetry

LSE may generate observable activity through:

- filesystem enumeration;
- process enumeration;
- privilege checks;
- configuration reads;
- package queries.

This may be useful defensive telemetry during controlled exercises.

Do not attempt to suppress security logging unless that is specifically part of the authorised test objective.

---

# Tool Transfer

Where the script must be transferred, document:

```text
Tool:
lse.sh

Source:
Official repository

Destination:
Approved temporary directory

Execution:
Authorised

Output:
Stored securely

Cleanup:
Completed
```

---

# Cleanup

Where required, remove:

```text
lse.sh
lse-output.txt
temporary assessment files
```

Do not remove legitimate operating-system or security logs.

---

# Practical LSE Workflow

A strong workflow is:

```text
1. Confirm scope
      |
      v
2. Record current identity
      |
      v
3. Record groups
      |
      v
4. Record OS/kernel context
      |
      v
5. Perform manual baseline
      |
      v
6. Obtain official LSE
      |
      v
7. Review help/options
      |
      v
8. Run focused enumeration
      |
      v
9. Increase detail if needed
      |
      v
10. Save output securely
      |
      v
11. Review high-value categories
      |
      v
12. Validate with native Linux tools
      |
      v
13. Confirm user influence
      |
      v
14. Identify privileged consumer
      |
      v
15. Confirm trigger
      |
      v
16. Consider security controls
      |
      v
17. Confirm or reject candidate
      |
      v
18. Capture evidence
      |
      v
19. Clean up assessment artefacts
```

---

# Quick Command Reference

## Current User

```bash
whoami
```

## Identity and Groups

```bash
id
```

## Groups

```bash
groups
```

## OS Information

```bash
cat /etc/os-release
```

## Kernel

```bash
uname -a
```

## Help

```bash
./lse.sh -h
```

## Run LSE

```bash
./lse.sh
```

## Run Through Bash

```bash
bash lse.sh
```

## Save Output

```bash
./lse.sh | tee lse-output.txt
```

## sudo

```bash
sudo -l
```

## SUID

```bash
find / -perm -4000 -type f 2>/dev/null
```

## SGID

```bash
find / -perm -2000 -type f 2>/dev/null
```

## Capabilities

```bash
getcap -r / 2>/dev/null
```

## File Permissions

```bash
ls -l /path/to/file
```

## File Metadata

```bash
stat /path/to/file
```

## Full Path Permissions

```bash
namei -l /path/to/file
```

## ACL

```bash
getfacl /path/to/file
```

## Processes

```bash
ps aux
```

## Listening Services

```bash
ss -lntup
```

## Services

```bash
systemctl list-units --type=service
```

## Timers

```bash
systemctl list-timers --all
```

## Service Definition

```bash
systemctl cat example.service
```

## Mounts

```bash
findmnt
```

## Environment

```bash
env
```

## PATH

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

---

# LSE Checklist

## Preparation

- [ ] Host explicitly authorised.
- [ ] Current user recorded.
- [ ] Groups recorded.
- [ ] Operating system recorded.
- [ ] Kernel recorded.
- [ ] Official repository used.
- [ ] Tool provenance recorded where useful.
- [ ] Sensitive-output handling understood.

## Execution

- [ ] Help reviewed.
- [ ] Appropriate enumeration level selected.
- [ ] Focused pass performed first where useful.
- [ ] Additional detail enabled only when needed.
- [ ] Output retained securely.
- [ ] Tool execution remained within scope.

## sudo

- [ ] `sudo -l` reviewed.
- [ ] Target user confirmed.
- [ ] Allowed commands reviewed.
- [ ] Arguments reviewed.
- [ ] Wildcards reviewed.
- [ ] `NOPASSWD` interpreted correctly.
- [ ] Command behaviour manually validated.

## SUID / SGID

- [ ] SUID binaries reviewed.
- [ ] SGID binaries reviewed.
- [ ] Ownership confirmed.
- [ ] Custom binaries prioritised.
- [ ] Binary behaviour understood.
- [ ] Legitimate privileged binaries distinguished from risky ones.

## Capabilities

- [ ] Capabilities enumerated.
- [ ] Exact capability confirmed.
- [ ] Associated binary reviewed.
- [ ] Security impact manually validated.

## Scheduled Execution

- [ ] Cron reviewed.
- [ ] systemd services reviewed.
- [ ] systemd timers reviewed.
- [ ] Execution identity confirmed.
- [ ] Referenced files reviewed.
- [ ] Parent directories reviewed.
- [ ] Trigger confirmed.

## Filesystem

- [ ] Writable files validated.
- [ ] Writable directories validated.
- [ ] Parent directories checked.
- [ ] ACLs considered.
- [ ] Mount options considered.
- [ ] Privileged consumer identified.

## Credentials

- [ ] Shell history treated as sensitive.
- [ ] Configuration secrets handled securely.
- [ ] SSH keys handled securely.
- [ ] Stale/example values distinguished from live credentials.
- [ ] Unnecessary authentication attempts avoided.

## Containers

- [ ] Container context identified.
- [ ] Docker membership reviewed.
- [ ] Docker socket reviewed.
- [ ] LXD/LXC access reviewed where relevant.
- [ ] Host/container trust boundary understood.

## Security Controls

- [ ] SELinux considered.
- [ ] AppArmor considered.
- [ ] seccomp considered where relevant.
- [ ] no_new_privs considered where relevant.
- [ ] Mount restrictions considered.

## Validation

- [ ] LSE output treated as candidate evidence.
- [ ] Native Linux validation performed.
- [ ] Effective user influence confirmed.
- [ ] Privileged consumer identified.
- [ ] Trigger confirmed.
- [ ] Security controls considered.
- [ ] False-positive explanations considered.
- [ ] Actual impact established.

## Evidence

- [ ] Current identity retained.
- [ ] Relevant LSE output retained.
- [ ] Native permission evidence retained.
- [ ] Privileged execution context documented.
- [ ] Trigger documented.
- [ ] Sensitive data redacted where appropriate.
- [ ] Finding describes underlying security weakness.

## Cleanup

- [ ] LSE script removed where required.
- [ ] Temporary output removed where required.
- [ ] Evidence retained according to policy.
- [ ] Legitimate system/security logs preserved.

---

# Related Tool Notes

[Privilege Escalation Tools](index.md)

[LinPEAS](linpeas.md)

Windows tools:

[WinPEAS](winpeas.md)

[PowerUp](powerup.md)

[PrivescCheck](privesccheck.md)

---

# Related Linux Notes

[Linux](../../linux/index.md)

[Linux Enumeration](../../linux/enumeration.md)

[Linux Privilege Escalation](../../linux/privilege-escalation.md)

[Linux sudo](../../linux/sudo.md)

[Linux SUID and SGID](../../linux/suid-sgid.md)

[Linux Capabilities](../../linux/capabilities.md)

[Linux Scheduled Jobs](../../linux/scheduled-jobs.md)

[Linux Filesystem Permissions](../../linux/filesystem-permissions.md)

[Linux Credentials](../../linux/credentials.md)

[Linux Security Controls](../../linux/security-controls.md)

[Linux Privilege Escalation Explorer](../../privesc/linux.md)

---

# External References

## Official linux-smart-enumeration Resources

[linux-smart-enumeration - GitHub](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

## Supporting Linux Privilege Escalation References

[HackTricks - Linux Privilege Escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html){ target="_blank" rel="noopener noreferrer" }

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

[Linux man-pages - capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }

[Linux man-pages - sudoers](https://man7.org/linux/man-pages/man5/sudoers.5.html){ target="_blank" rel="noopener noreferrer" }

[systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html){ target="_blank" rel="noopener noreferrer" }

[systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use LSE like this:

```text
Run lse.sh
    |
    v
Look for Warnings
    |
    v
Assume Root
```

Use it like this:

```text
Understand Current Identity
        |
        v
Run Focused LSE Enumeration
        |
        v
Identify Candidate
        |
        v
Understand Why It Was Flagged
        |
        v
Validate With Native Tools
        |
        +-- sudo
        +-- ls
        +-- stat
        +-- namei
        +-- getfacl
        +-- getcap
        +-- systemctl
        +-- findmnt
        |
        v
Confirm User Influence
        |
        v
Identify Privileged Consumer
        |
        v
Confirm Trigger
        |
        v
Consider Security Controls
        |
        v
Determine Actual Impact
        |
        v
Capture Evidence
        |
        v
Report the Underlying Weakness
```

linux-smart-enumeration is valuable because it provides a focused way to identify Linux privilege escalation candidates without replacing manual analysis.

It helps identify where to look.

The tester determines whether the condition actually crosses a privilege boundary.
