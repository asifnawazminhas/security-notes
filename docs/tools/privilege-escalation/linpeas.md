---
title: LinPEAS
description: Practical LinPEAS reference for authorised Linux privilege escalation enumeration, interpretation, validation, evidence collection, false-positive analysis, and integration with manual Linux security review.
---

# LinPEAS

LinPEAS is part of the PEASS-ng project and is designed to enumerate Linux systems for conditions that may be relevant to local privilege escalation.

It can inspect a broad range of areas, including:

- users and groups;
- sudo configuration;
- SUID and SGID binaries;
- Linux capabilities;
- cron jobs;
- systemd services and timers;
- filesystem permissions;
- writable directories;
- environment variables;
- PATH configuration;
- credentials;
- processes;
- network configuration;
- mounted filesystems;
- containers;
- installed software;
- security controls;
- interesting files.

LinPEAS is most useful as an **enumeration accelerator**.

It does not automatically determine whether every highlighted condition is exploitable.

```text
Linux Host
   |
   v
LinPEAS
   |
   +-- Identity
   +-- sudo
   +-- SUID / SGID
   +-- Capabilities
   +-- Cron / systemd
   +-- Filesystem
   +-- Credentials
   +-- Processes
   +-- Mounts
   +-- Containers
   +-- Security Controls
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
    Run LinPEAS only on Linux systems where local security enumeration is explicitly authorised. It performs many checks across the host and may generate security telemetry or access sensitive configuration locations. Review the rules of engagement before transferring or executing third-party enumeration tooling.

---

# Where LinPEAS Fits

LinPEAS normally follows initial access to a Linux system.

A useful workflow is:

```text
Initial Local Access
        |
        v
Identify Current User
        |
        v
Manual Baseline
        |
        v
Run LinPEAS
        |
        v
Review Interesting Results
        |
        v
Validate With Native Tools
        |
        v
Confirm or Reject Candidate
```

Related notes:

[Privilege Escalation Tools](index.md)

[Linux Privilege Escalation](../../linux/privilege-escalation.md)

[Linux Enumeration](../../linux/enumeration.md)

[Linux Privilege Escalation Explorer](../../privesc/linux.md)

---

# What LinPEAS Does

LinPEAS automates many checks that would otherwise need to be performed manually.

Conceptually:

```text
System State
    |
    +-- Users
    +-- Groups
    +-- sudo
    +-- SUID / SGID
    +-- Capabilities
    +-- Cron
    +-- systemd
    +-- Files
    +-- Credentials
    +-- Processes
    +-- Mounts
    +-- Containers
    |
    v
LinPEAS Checks
    |
    v
Prioritised Output
```

The tool attempts to highlight items that may deserve additional investigation.

The key principle is:

```text
Highlighted
    !=
Exploitable
```

---

# Official Project

LinPEAS is maintained as part of PEASS-ng.

Official project:

[PEASS-ng - GitHub](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Official releases:

[PEASS-ng Releases](https://github.com/peass-ng/PEASS-ng/releases){ target="_blank" rel="noopener noreferrer" }

Use the official project or trusted internal mirrors.

Avoid unknown modified copies.

---

# Before Running LinPEAS

Understand the current user context first.

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

Am I already privileged?

Do I belong to sudo-related groups?

Do I belong to Docker, LXD, disk, or similar sensitive groups?
```

Without this baseline, tool output is harder to interpret.

---

# Record System Context

Capture basic host information.

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

```bash
id
```

This provides context for:

- operating system;
- kernel;
- distribution;
- current identity;
- later evidence.

---

# Obtaining LinPEAS

Prefer the official PEASS-ng release or repository.

Verify:

- source;
- release provenance;
- file integrity where appropriate;
- engagement approval;
- internal malware-handling procedures.

Security products may identify offensive-security tooling even when it is being used legitimately.

---

# Common LinPEAS Form

LinPEAS is commonly distributed as a shell script:

```text
linpeas.sh
```

The exact content and checks evolve over time.

Do not assume an old copy provides complete coverage.

---

# Basic Execution

A common authorised workflow is:

```bash
chmod +x linpeas.sh
```

Then:

```bash
./linpeas.sh
```

It can also be invoked through a shell:

```bash
bash linpeas.sh
```

Use the method permitted by the environment.

---

# Save Output

Large LinPEAS runs can produce substantial output.

Saving the results makes later review easier.

Example:

```bash
./linpeas.sh | tee linpeas-output.txt
```

This allows:

- later searching;
- comparison;
- evidence extraction;
- review outside the terminal.

Protect the resulting file because it may contain sensitive information.

---

# Output May Contain Secrets

LinPEAS can expose:

- passwords;
- API keys;
- tokens;
- database credentials;
- private keys;
- configuration secrets;
- shell history;
- environment variables;
- usernames;
- internal paths.

Do not:

- commit raw output to Git;
- upload it to public services;
- include full output in reports;
- share it outside the authorised assessment team.

Retain only what is necessary.

---

# Colour Coding

LinPEAS uses colour and formatting to draw attention to interesting results.

Do not interpret colour as certainty.

Bad model:

```text
Red
 |
 v
Confirmed vulnerability
```

Better:

```text
Highlighted
   |
   v
Investigate
```

Colour is a triage mechanism.

---

# Major Enumeration Areas

LinPEAS may inspect categories such as:

```text
Users
Groups
sudo
SUID / SGID
Capabilities
Cron
systemd
Filesystem
Processes
Credentials
Network
Mounts
Containers
Environment
Security Controls
```

Each area requires different manual validation.

---

# Current User

Start with:

```bash
id
```

Representative result:

```text
uid=1001tester gid=1001tester groups=1001tester,27sudo
```

The result immediately provides context.

If the user is already a member of a highly privileged group, that may be more relevant than later enumeration findings.

---

# Groups

Group membership can significantly change privilege.

Inspect:

```bash
groups
```

and:

```bash
id
```

Potentially sensitive groups depend on the environment but may include groups controlling:

- sudo;
- containers;
- storage devices;
- logs;
- privileged services;
- virtualisation.

Do not assume group membership alone is exploitable.

Understand what that group can actually control.

---

# sudo

sudo is one of the most important Linux privilege escalation areas.

Always inspect manually:

```bash
sudo -l
```

Questions include:

```text
Which commands are allowed?

Which target user?

Is a password required?

Are wildcards present?

Are arguments restricted?

Are environment variables preserved?
```

Related note:

[Linux sudo](../../linux/sudo.md)

---

# Interpreting sudo Output

Suppose LinPEAS highlights:

```text
User may run /usr/bin/example as root
```

Do not stop there.

Determine:

```text
What exactly can the binary do?

Are arguments unrestricted?

Does it load configuration?

Can it write files?

Can it spawn another process?

Does it invoke external commands?
```

The privilege escalation condition depends on the actual behaviour.

---

# sudo NOPASSWD

A rule containing:

```text
NOPASSWD
```

means the command can be executed without entering the user's password.

This may increase practical reachability.

It does not automatically mean privilege escalation is possible.

The allowed command still needs analysis.

---

# sudo Wildcards

Wildcard-based sudo rules deserve careful review.

Example concept:

```text
/usr/bin/example *
```

Questions include:

```text
What arguments can be supplied?

Are paths controlled?

Does the command interpret options?

Can additional files be referenced?
```

A wildcard itself is not automatically a vulnerability.

---

# sudo Environment

Environment handling may matter for certain privileged commands.

Review sudo configuration rather than assuming inherited variables are trusted.

Useful command:

```bash
sudo -V
```

and configuration review where authorised.

The relevant question is whether an environment-controlled value influences privileged execution.

---

# SUID

SUID binaries execute with the effective user identity of the file owner.

Find them manually:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Typical output might include:

```text
/usr/bin/passwd
/usr/bin/sudo
/usr/bin/su
```

Many legitimate Linux utilities require SUID.

Therefore:

```text
SUID
  !=
Vulnerable
```

Related note:

[Linux SUID and SGID](../../linux/suid-sgid.md)

---

# Validate SUID Permissions

Inspect a candidate:

```bash
ls -l /path/to/binary
```

Representative:

```text
-rwsr-xr-x 1 root root 123456 Jan 1 12:00 /path/to/binary
```

The `s` in the owner's execute position indicates SUID.

Next investigate:

- owner;
- binary purpose;
- supported arguments;
- configuration;
- external commands;
- environment handling;
- version;
- whether privileges are dropped.

---

# SGID

SGID binaries execute with the effective group identity associated with the file.

Enumerate:

```bash
find / -perm -2000 -type f 2>/dev/null
```

SGID is often legitimate.

Assess whether the group privilege creates meaningful access.

---

# GTFOBins as a Research Aid

For known Linux utilities, GTFOBins can help identify security-sensitive functionality such as:

- sudo abuse;
- SUID behaviour;
- file read;
- file write;
- command execution.

Use it as a reference, not proof that a path is exploitable.

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

The actual binary, permissions, arguments, and environment must still be validated.

---

# Linux Capabilities

Linux capabilities divide traditional root privileges into smaller units.

Enumerate:

```bash
getcap -r / 2>/dev/null
```

Representative output:

```text
/usr/bin/example cap_net_raw=ep
```

Potential security impact depends on:

- capability;
- executable;
- effective/permitted state;
- command functionality;
- configuration.

Related note:

[Linux Capabilities](../../linux/capabilities.md)

---

# Capability Validation

Inspect the exact capability:

```bash
getcap /path/to/binary
```

Then determine what the binary can do with it.

For example:

```text
Capability
    |
    v
Binary Functionality
    |
    v
Current User Control
    |
    v
Security Impact
```

The capability name alone is not enough.

---

# Scheduled Jobs

LinPEAS can identify scheduled execution.

Relevant mechanisms include:

- cron;
- system cron directories;
- user crontabs;
- systemd timers;
- custom schedulers.

Related note:

[Linux Scheduled Jobs](../../linux/scheduled-jobs.md)

---

# Cron

Inspect cron configuration manually.

Examples:

```bash
cat /etc/crontab
```

```bash
ls -la /etc/cron.d/
```

```bash
ls -la /etc/cron.daily/
```

where access is permitted.

The important questions are:

```text
Who executes the command?

What is executed?

Can the current user modify it?

Can the current user modify a parent directory?

Can PATH influence command resolution?
```

---

# Root Cron Jobs

A root cron job is not automatically a vulnerability.

Example:

```text
root executes /opt/scripts/backup.sh
```

Validate:

```bash
ls -l /opt/scripts/backup.sh
```

and:

```bash
namei -l /opt/scripts/backup.sh
```

If the current user cannot influence the script or execution path, the condition may be secure.

---

# User Crontabs

Inspect authorised user crontabs with:

```bash
crontab -l
```

System-level cron jobs may be visible through:

```bash
/etc/crontab
/etc/cron.d/
```

Do not modify scheduled jobs during validation unless explicitly authorised.

---

# systemd Services

systemd services may provide privileged execution paths.

List relevant units:

```bash
systemctl list-units --type=service
```

Inspect a specific unit:

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

The question is whether the current user can influence something consumed by the privileged service.

---

# systemd Timers

Timers provide scheduled systemd execution.

List timers:

```bash
systemctl list-timers --all
```

Inspect the timer and corresponding service.

A timer itself is not vulnerable.

The security question is whether a low-privileged user can influence the privileged execution chain.

---

# Service Files

Typical systemd unit locations include:

```text
/etc/systemd/system/
/usr/lib/systemd/system/
/lib/systemd/system/
```

Actual locations vary by distribution.

Check permissions rather than assuming.

---

# Filesystem Permissions

Weak filesystem permissions are central to Linux privilege escalation.

Review:

- files;
- directories;
- scripts;
- configuration;
- service resources;
- cron resources;
- binaries;
- application data.

Related note:

[Linux Filesystem Permissions](../../linux/filesystem-permissions.md)

---

# Basic Permission Inspection

Use:

```bash
ls -l /path/to/file
```

Example:

```text
-rwxrwxr-x 1 root developers 1024 Jan 1 12:00 /opt/app/start.sh
```

Interpret:

```text
Owner
Group
Mode bits
```

Then compare those permissions with the current user's identity and groups.

---

# namei

`namei -l` is very useful for analysing complete path permissions.

Example:

```bash
namei -l /opt/app/scripts/backup.sh
```

This helps reveal whether a parent directory is writable even if the final file is protected.

---

# ACLs

Traditional mode bits may not show the entire permission picture.

Inspect ACLs:

```bash
getfacl /path/to/file
```

ACLs can grant additional permissions to specific users or groups.

Always consider effective permissions.

---

# Writable Directories

Findings such as:

```text
World-writable directory
```

must be interpreted carefully.

Ask:

```text
Does a privileged process use this directory?

Does it load executables from here?

Does it source scripts?

Does it load configuration?

Can files be replaced?
```

A writable directory without a privileged consumer may not create escalation.

---

# World-Writable Files

A world-writable file may be highly relevant if consumed by root.

It may be irrelevant if it is only user data.

The security significance depends on:

```text
Who can modify it?
+
Who trusts it?
+
How is it used?
```

---

# Parent Directories

Always inspect parent directories.

Example:

```text
/opt/app/config/settings.conf
```

The file itself might be protected while:

```text
/opt/app/config/
```

is writable.

Depending on filesystem permissions, the user may be able to replace the file.

---

# Ownership

Inspect:

```bash
stat /path/to/file
```

Useful properties include:

- owner;
- group;
- mode;
- timestamps.

Ownership helps explain expected trust boundaries.

---

# PATH

PATH-based issues occur when privileged scripts or programs execute commands without absolute paths.

Inspect:

```bash
echo "$PATH"
```

Then:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

Questions include:

```text
Which directory is searched first?

Is it writable?

Does a privileged process inherit this PATH?

Does the privileged script call a command without an absolute path?
```

A writable PATH directory is only one part of the chain.

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
Writable Directory First
      |
      v
Attacker-Controlled Binary
```

Every step must be validated.

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

Environment variables may contain:

- tokens;
- credentials;
- application paths;
- configuration;
- runtime settings.

Security relevance depends on who can read them and whether privileged processes trust them.

---

# Shell History

LinPEAS may inspect shell history files.

Examples include:

```text
~/.bash_history
~/.zsh_history
```

History may contain:

- commands;
- passwords accidentally supplied inline;
- URLs;
- administrative actions;
- database commands.

Treat shell history as sensitive data.

---

# Credentials

LinPEAS may identify possible credentials in:

- configuration files;
- shell history;
- environment variables;
- scripts;
- application directories;
- backup files;
- SSH material.

Related note:

[Linux Credentials](../../linux/credentials.md)

---

# Credential Validation

A string that resembles a password may be:

- example data;
- expired;
- fake;
- encrypted;
- unused;
- a hash rather than plaintext.

Do not automatically attempt to authenticate with every discovered secret.

First determine whether validation is necessary and authorised.

---

# SSH Keys

Interesting files may include:

```text
id_rsa
id_ed25519
authorized_keys
known_hosts
```

The presence of a private key does not automatically mean it can be used elsewhere.

Consider:

- ownership;
- permissions;
- passphrase;
- authorised scope;
- associated account;
- destination systems.

---

# Configuration Files

Application configuration may expose:

- database credentials;
- service accounts;
- API keys;
- internal endpoints.

Common locations vary by application.

The relevant security issue may be:

```text
Low-privileged user can read sensitive configuration
```

rather than:

```text
LinPEAS found password
```

---

# Processes

Running processes reveal valuable context.

Use:

```bash
ps aux
```

or:

```bash
ps -ef
```

Review:

- privileged services;
- custom applications;
- root processes;
- service commands;
- interpreters;
- unusual working directories.

---

# Process Command Lines

Process arguments may expose:

- passwords;
- tokens;
- configuration paths;
- scripts.

Example:

```text
root  /usr/bin/example --config /opt/app/config.yml
```

This may identify a privileged configuration path worth reviewing.

---

# Process Ownership

A root-owned process is only interesting if the current user can influence something it uses.

Possible influence points include:

- configuration;
- executable;
- script;
- socket;
- writable working directory;
- plugin directory.

---

# Services

List services:

```bash
systemctl --type=service
```

or inspect running processes.

Custom root-owned services deserve particular attention.

The objective is to trace:

```text
Service
  |
  v
Executable
  |
  v
Configuration
  |
  v
Files / Environment
```

and identify user-controlled components.

---

# Network Services

Local services can be security relevant.

Inspect:

```bash
ss -lntup
```

where permissions allow.

Potentially interesting services include:

- local-only administration APIs;
- databases;
- development interfaces;
- management sockets.

Do not assume access to a local port creates privilege escalation.

Validate authentication and privilege context.

---

# Unix Sockets

Privileged services may expose Unix-domain sockets.

Find them with appropriate filesystem and process inspection.

A socket may be relevant if the current user has permission to interact with a privileged service that exposes sensitive functionality.

---

# Mounts

Mount configuration can expose security-relevant conditions.

Inspect:

```bash
mount
```

and:

```bash
findmnt
```

Potential areas include:

- NFS;
- CIFS;
- bind mounts;
- container mounts;
- removable storage;
- shared filesystems.

Related privilege depends on the mount and its options.

---

# /etc/fstab

Review where authorised:

```bash
cat /etc/fstab
```

This may reveal:

- network shares;
- mount credentials;
- filesystem options;
- custom mount points.

Treat embedded credentials as sensitive.

---

# NFS

NFS configuration can have security implications.

The local client view alone may not reveal server-side export configuration.

Do not infer a server-side weakness purely from the fact that an NFS mount exists.

---

# Containers

LinPEAS may identify whether the host or current process is running inside a container.

Useful clues include:

- Docker;
- containerd;
- Kubernetes;
- LXC;
- cgroups;
- namespaces.

Root inside a container is not automatically root on the host.

---

# Docker Group

Membership in the Docker group can be highly privileged because Docker can control host resources.

First validate:

```bash
id
```

and:

```bash
groups
```

Then determine whether the Docker daemon is accessible:

```bash
docker info
```

where authorised.

The security conclusion should describe the excessive privilege associated with daemon access, not simply group membership.

---

# Docker Socket

A common local resource is:

```text
/var/run/docker.sock
```

Inspect:

```bash
ls -l /var/run/docker.sock
```

Questions include:

```text
Which group owns it?

Can the current user access it?

Does it control the host Docker daemon?
```

Avoid modifying containers during validation unless explicitly authorised.

---

# LXD / LXC

Container-management groups can also provide substantial privileges.

As with Docker:

```text
Group Membership
       |
       v
Management Access
       |
       v
Host Resource Control
```

Manual validation is required.

---

# Kubernetes Context

On containerised systems, LinPEAS may surface:

- service-account tokens;
- mounted secrets;
- Kubernetes environment variables;
- container metadata.

These may belong to a different security domain and must be assessed against engagement scope.

---

# Kernel Information

LinPEAS may identify kernel version information.

Check manually:

```bash
uname -r
```

Do not immediately map a kernel version to a local exploit.

Instead determine:

```text
Kernel version
    |
    v
Distribution package
    |
    v
Vendor patch status
    |
    v
Configuration
    |
    v
Applicability
```

Linux distributions frequently backport security fixes.

---

# Kernel Exploit Candidates

Treat automated kernel exploit suggestions as research leads.

A version match is insufficient.

Validate:

- architecture;
- exact kernel;
- distribution;
- patch level;
- configuration;
- required namespace or capability;
- stability risk.

Kernel exploitation can destabilise a system and should only be attempted where explicitly authorised.

---

# Installed Packages

Enumerate package information with distribution-appropriate tools.

Examples:

```bash
dpkg -l
```

or:

```bash
rpm -qa
```

depending on the platform.

Old-looking versions may still contain backported fixes.

---

# Custom Applications

Custom root-run applications can be more important than standard packages.

Review:

- binary location;
- scripts;
- configuration;
- working directories;
- update mechanisms;
- plugin directories.

LinPEAS may provide clues, but custom logic usually requires manual analysis.

---

# Sensitive Groups

Some groups deserve closer review because membership may grant control over privileged resources.

Examples can include groups related to:

```text
sudo
docker
lxd
disk
adm
backup
```

Exact impact is environment-specific.

Do not report group membership without understanding the permissions it grants.

---

# Disk Access

Membership in a group with raw block-device access can represent substantial privilege.

Validate:

- actual device permissions;
- current group membership;
- mounted resources;
- assessment rules.

Raw-disk operations can damage systems and should not be used casually for validation.

---

# Log Access

Groups that grant access to logs may expose:

- tokens;
- credentials;
- sensitive application data.

This may be an information-disclosure issue even if it does not directly provide root access.

---

# Backup Files

LinPEAS may locate files such as:

```text
*.bak
*.old
*.backup
~
```

Backup files can expose:

- configuration;
- credentials;
- previous permissions;
- source code.

Validate relevance before reporting.

---

# Temporary Directories

Common writable locations include:

```text
/tmp
/var/tmp
/dev/shm
```

These are intentionally writable on many systems.

A writable temporary directory is not itself a vulnerability.

It becomes relevant only when a privileged component trusts or executes user-controlled content from it.

---

# /tmp Misinterpretation

Bad:

```text
/tmp is writable
    |
    v
Privilege escalation
```

Correct:

```text
/tmp is writable
    |
    v
Expected behaviour

Need additional condition:
Privileged process consumes predictable/user-controlled file
```

---

# File Race Conditions

Some privileged programs may create or access files in unsafe shared locations.

This can create race-condition or symlink-related risks.

Such conditions require careful, low-impact validation.

Do not perform destructive race testing on production systems unless explicitly approved.

---

# Home Directories

Review whether one user can improperly access another user's home directory.

Potentially sensitive data includes:

- SSH keys;
- shell history;
- configuration;
- application credentials.

The finding may be excessive local file access rather than privilege escalation.

---

# Root-Owned Files

Root ownership does not imply security by itself.

Check:

```text
Owner
Group
Mode
ACL
Parent Directory
```

A root-owned file can still be modifiable by another group or ACL entry.

---

# World-Readable Files

World-readable files are common.

The important question is what the file contains.

For example:

```text
/etc/passwd
```

is normally world-readable.

That is not a vulnerability.

Context matters.

---

# /etc/passwd

Normal permissions generally allow users to read:

```text
/etc/passwd
```

Sensitive password hashes should normally be stored in:

```text
/etc/shadow
```

A tool highlighting `/etc/passwd` simply because it is readable should not be interpreted as a security issue.

---

# /etc/shadow

Access to:

```text
/etc/shadow
```

is much more security sensitive.

Check permissions:

```bash
ls -l /etc/shadow
```

Do not collect or crack password hashes unless explicitly authorised and necessary for the assessment.

---

# Shells

Inspect:

```bash
cat /etc/shells
```

and user account entries where relevant.

This provides context about interactive users and available shells.

---

# Current Shell

Check:

```bash
echo "$SHELL"
```

and:

```bash
ps -p $$ -o comm=
```

This can help explain script behaviour and environment differences.

---

# SELinux

Security controls may constrain a technically interesting path.

Check:

```bash
getenforce
```

where SELinux is installed.

Possible states include:

```text
Enforcing
Permissive
Disabled
```

Do not assume `Enforcing` means all privilege escalation paths are prevented.

It is one security layer.

Related note:

[Linux Security Controls](../../linux/security-controls.md)

---

# AppArmor

AppArmor may restrict application behaviour.

Check where available:

```bash
aa-status
```

The exact command may require additional privileges.

As with SELinux, application confinement affects exploitability but does not automatically remove an underlying permission weakness.

---

# no_new_privs

Linux processes can use the `no_new_privs` security attribute to prevent gaining additional privileges through certain execution mechanisms.

Where relevant, inspect process security context.

This can affect the practical behaviour of SUID or file-capability execution.

Related note:

[Linux Security Controls](../../linux/security-controls.md)

---

# Seccomp

Containers and sandboxed processes may use seccomp filters.

This can restrict system calls.

Its presence can affect exploitability.

Do not assume an automated candidate remains fully usable within a heavily constrained execution environment.

---

# Read-Only Filesystems

A filesystem or mount may be read-only even when traditional permissions appear writable.

Check:

```bash
findmnt
```

and mount options.

Effective write capability depends on both permissions and mount state.

---

# ACL vs Mode Bits

A file might show:

```text
-rw-r-----
```

but ACLs may grant additional access.

Check:

```bash
getfacl /path/to/file
```

Effective permission analysis should include both.

---

# Capabilities vs SUID

Capabilities and SUID are different privilege mechanisms.

```text
SUID
  |
  v
Effective user identity changes
```

Capabilities:

```text
Capability
  |
  v
Specific privilege granted
```

Review both independently.

---

# LinPEAS and LSE

LinPEAS and linux-smart-enumeration overlap in several areas.

A useful workflow is:

```text
LinPEAS
   |
   v
Broad Candidate Set
   |
   v
LSE / Manual Review
   |
   v
Confirm Important Conditions
```

Related tool:

[linux-smart-enumeration](linux-smart-enumeration.md)

---

# LinPEAS and Manual Enumeration

Automated and manual approaches complement each other.

```text
LinPEAS
   |
   +-- breadth
   +-- fast triage

Manual Tools
   |
   +-- precision
   +-- context
   +-- evidence
```

Native Linux commands should validate important findings.

---

# Native Validation Tools

Useful commands include:

```text
id
sudo
find
ls
stat
namei
getfacl
getcap
ps
systemctl
findmnt
ss
```

LinPEAS should guide which manual checks matter.

---

# Searching Saved Output

If results were saved:

```text
linpeas-output.txt
```

search them:

```bash
grep -i "sudo" linpeas-output.txt
```

```bash
grep -i "capabil" linpeas-output.txt
```

```bash
grep -i "writable" linpeas-output.txt
```

Retain surrounding context when interpreting matches.

---

# Review by Category

A practical result-review sequence is:

```text
1. User and groups
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

This is easier than scrolling randomly through the entire output.

---

# Prioritising Findings

High-value candidates usually combine:

```text
User Influence
      +
Privileged Consumer
      +
Reachable Trigger
```

For example:

```text
Writable script
      +
Executed by root cron
      +
Runs every minute
```

This deserves closer review.

---

# Candidate Evaluation Table

For each candidate, ask:

| Question | Answer |
|---|---|
| Can current user influence the object? | |
| Which privileged user/process consumes it? | |
| Is the path active? | |
| Can execution be triggered? | |
| Are additional conditions required? | |
| Do SELinux/AppArmor/no_new_privs affect it? | |
| What privilege would be obtained? | |

This prevents overreporting.

---

# Representative sudo Scenario

LinPEAS highlights:

```text
User can run /usr/local/bin/backup with sudo
```

Validate:

```bash
sudo -l
```

Then inspect:

```bash
ls -l /usr/local/bin/backup
```

If readable and permitted:

```bash
file /usr/local/bin/backup
```

Determine:

- arguments;
- configuration;
- files accessed;
- external commands;
- whether the program intentionally drops privileges.

Only then determine security impact.

---

# Representative SUID Scenario

LinPEAS highlights:

```text
/opt/custom/helper
```

Validate:

```bash
ls -l /opt/custom/helper
```

Suppose:

```text
-rwsr-xr-x 1 root root ...
```

Next determine:

```text
What does the binary do?

Does it retain elevated EUID?

Does it process user-controlled files?

Does it invoke external commands?

Does it validate arguments?
```

Do not report merely because it is SUID.

---

# Representative Capability Scenario

LinPEAS reports:

```text
/usr/local/bin/example cap_dac_read_search=ep
```

Validate:

```bash
getcap /usr/local/bin/example
```

Then determine whether the executable exposes functionality that permits the current user to misuse that capability.

The security condition depends on the binary, not just the capability label.

---

# Representative Cron Scenario

LinPEAS identifies:

```text
root cron:
* * * * * /opt/scripts/backup.sh
```

Check:

```bash
ls -l /opt/scripts/backup.sh
```

Then:

```bash
namei -l /opt/scripts/backup.sh
```

Suppose the script is:

```text
root:root
-rwxr-xr-x
```

but the parent directory is writable by the current user.

That parent-directory permission may be the relevant condition.

---

# Representative systemd Scenario

LinPEAS identifies:

```text
example.service
```

running as root.

Inspect:

```bash
systemctl cat example.service
```

Suppose:

```text
ExecStart=/opt/example/start.sh
```

Then:

```bash
ls -l /opt/example/start.sh
```

and:

```bash
namei -l /opt/example/start.sh
```

Again, validate the whole execution chain.

---

# Representative Credential Scenario

LinPEAS finds:

```text
DB_PASSWORD=examplevalue
```

in an application configuration file.

The next questions are:

```text
Is this an actual secret?

Which service uses it?

Does the current user already have legitimate access?

Is validation necessary?

Does the credential provide additional privilege?
```

The finding may be:

```text
Sensitive credential accessible to local low-privileged users
```

rather than:

```text
Privilege escalation via LinPEAS
```

---

# Representative Docker Scenario

LinPEAS highlights Docker-related access.

Validate:

```bash
id
```

and:

```bash
ls -l /var/run/docker.sock
```

If the current user can control the host Docker daemon, document the trust implication.

Avoid making state-changing container modifications solely for proof unless required and authorised.

---

# Representative Kernel Scenario

LinPEAS suggests a possible kernel-related issue.

Do not immediately run a kernel exploit.

First establish:

```bash
uname -a
```

```bash
cat /etc/os-release
```

Then verify:

- distribution advisory;
- installed package version;
- required kernel configuration;
- applicability;
- stability impact.

Kernel exploitation should be considered a high-risk validation step.

---

# False Positives

LinPEAS can highlight conditions that are not exploitable.

Common examples include:

- legitimate SUID programs;
- harmless world-writable temporary directories;
- inactive cron entries;
- writable files not used by root;
- capabilities with no useful interface;
- stale credentials;
- kernel-version heuristics;
- expected container configuration.

Manual validation is mandatory.

---

# False Negatives

LinPEAS can miss real privilege escalation paths.

Possible reasons include:

- custom applications;
- unusual directories;
- proprietary services;
- transient files;
- uncommon ACLs;
- custom IPC;
- dynamically created resources;
- application-specific logic.

A clean LinPEAS run does not prove that no local privilege escalation path exists.

---

# Security Controls Can Change Exploitability

A candidate may appear strong but be constrained by:

- SELinux;
- AppArmor;
- seccomp;
- no_new_privs;
- read-only mounts;
- container namespaces.

Separate:

```text
Underlying Weak Configuration
```

from:

```text
Practical Exploitability
```

Both matter.

---

# Do Not Disable Security Controls

During ordinary privilege escalation testing, do not disable:

```text
SELinux
AppArmor
seccomp
security agents
```

merely to make a candidate path easier to exploit.

Their presence is part of the environment being assessed.

---

# Evidence Collection

For each validated candidate, retain:

```text
Current user:
Groups:
Relevant LinPEAS section:
Affected object:
Owner:
Group:
Permissions:
ACL:
Privileged consumer:
Trigger:
Security controls:
Manual validation:
Observed impact:
```

For example:

```text
Current user:
tester

Candidate:
Writable root cron script

File:
 /opt/scripts/backup.sh

Owner:
root

Consumer:
root cron

Trigger:
Every minute

Validation:
Current user had write access through group permission.
```

---

# Evidence Should Show the Chain

Weak:

```text
Screenshot of red LinPEAS output
```

Strong:

```text
LinPEAS candidate
      |
      v
ls/stat/getfacl evidence
      |
      v
cron/systemd configuration
      |
      v
root execution context
      |
      v
trigger
      |
      v
impact
```

The reader should understand why the condition matters.

---

# Reporting a Cron Weakness

Avoid:

```text
LinPEAS found an insecure cron job.
```

Prefer:

```text
A scheduled task executed by root referenced a script located in a
directory that was modifiable by the tested standard user. This allowed
the low-privileged user to influence content consumed by a privileged
scheduled process.
```

The finding describes the security weakness.

---

# Reporting a sudo Weakness

Avoid:

```text
LinPEAS found sudo privilege escalation.
```

Prefer:

```text
The tested user was permitted to execute the specified application as
root through sudo. The application exposed functionality that allowed
the user to perform operations outside the intended administrative
task, resulting in an effective privilege boundary bypass.
```

---

# Reporting a Negative Result

Example:

```text
LinPEAS highlighted a root-owned scheduled script as potentially
interesting. Manual validation showed that neither the script nor its
parent directories were writable by the tested user. The suspected
privilege escalation path was therefore not confirmed.
```

Negative validation is useful evidence.

---

# Remediation Principles

The general principle is:

> Low-privileged users should not be able to modify resources that are trusted or executed by higher-privileged processes.

Common remediation areas include:

- sudo;
- file permissions;
- cron;
- systemd;
- SUID/SGID;
- capabilities;
- credentials;
- container-management permissions.

---

# sudo Remediation

Typical measures include:

- minimise allowed commands;
- avoid unnecessary wildcards;
- restrict arguments;
- avoid unnecessarily broad `NOPASSWD`;
- use least privilege;
- remove shell-capable or overly flexible binaries where inappropriate.

---

# SUID / SGID Remediation

Typical measures include:

- remove unnecessary SUID/SGID bits;
- replace privileged helper logic with safer designs;
- validate user-controlled input;
- use least privilege.

---

# Capability Remediation

Typical measures include:

- remove unnecessary file capabilities;
- assign the minimum required capability;
- restrict execution permissions.

---

# Cron Remediation

Typical measures include:

- protect scripts;
- protect parent directories;
- use absolute paths;
- set safe ownership;
- avoid executing user-controlled content;
- minimise privileged scheduled jobs.

---

# systemd Remediation

Typical measures include:

- protect unit files;
- protect referenced scripts/binaries;
- use dedicated low-privileged service accounts;
- protect environment files;
- avoid writable working directories where they influence execution.

---

# Credential Remediation

Typical measures include:

- remove plaintext secrets;
- rotate exposed credentials;
- use appropriate secret storage;
- tighten filesystem permissions;
- remove obsolete backup/configuration files.

---

# Container Remediation

Typical measures include:

- restrict Docker/LXD group membership;
- protect management sockets;
- avoid unnecessary privileged containers;
- minimise host filesystem mounts;
- apply least privilege.

---

# Retesting

Do not retest only by rerunning LinPEAS.

For a corrected file permission:

```bash
ls -l /path/to/file
```

and:

```bash
getfacl /path/to/file
```

For a corrected cron path:

```bash
namei -l /path/to/script
```

For corrected sudo configuration:

```bash
sudo -l
```

Confirm that the underlying weakness has been removed.

Then optionally rerun LinPEAS as a secondary regression check.

---

# Tool Transfer Considerations

If LinPEAS must be transferred to the target, document:

```text
Source
Destination
Hash where relevant
Execution time
Output location
Cleanup status
```

Use approved temporary locations.

Do not leave unnecessary tooling behind.

---

# Cleanup

Where required, remove:

```text
linpeas.sh
linpeas-output.txt
temporary test files
```

Do not remove legitimate system logs.

Assessment evidence should be retained according to policy.

---

# Telemetry

Running LinPEAS can generate activity such as:

- filesystem enumeration;
- process inspection;
- permission checks;
- package queries;
- configuration reads;
- system calls.

In a purple-team exercise, this may be intentionally useful for validating defensive visibility.

Related notes:

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

---

# LinPEAS in Purple Teaming

A controlled exercise might use:

```text
LinPEAS
   |
   v
Host Enumeration
   |
   v
Linux Audit / EDR Telemetry
   |
   v
Detection Review
   |
   v
Detection Improvement
```

The expected activity should be coordinated in advance.

---

# LinPEAS Review Workflow

A strong review process is:

```text
1. Confirm scope
      |
      v
2. Record current identity
      |
      v
3. Record host context
      |
      v
4. Perform basic manual checks
      |
      v
5. Obtain official LinPEAS
      |
      v
6. Run approved enumeration
      |
      v
7. Save output securely
      |
      v
8. Review by category
      |
      v
9. Prioritise real execution paths
      |
      v
10. Validate with native commands
      |
      v
11. Consider security controls
      |
      v
12. Confirm or reject candidates
      |
      v
13. Capture evidence
      |
      v
14. Clean up assessment artefacts
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

## Run LinPEAS

```bash
./linpeas.sh
```

## Run Through Bash

```bash
bash linpeas.sh
```

## Save Output

```bash
./linpeas.sh | tee linpeas-output.txt
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

## Full Path Permissions

```bash
namei -l /path/to/file
```

## ACL

```bash
getfacl /path/to/file
```

## File Metadata

```bash
stat /path/to/file
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

# LinPEAS Checklist

## Preparation

- [ ] Host explicitly authorised.
- [ ] Current user recorded.
- [ ] Groups recorded.
- [ ] Operating system recorded.
- [ ] Kernel recorded.
- [ ] Official PEASS-ng source used.
- [ ] Tool transfer approved where required.
- [ ] Sensitive-output handling understood.

## Execution

- [ ] Appropriate LinPEAS copy used.
- [ ] Output stored securely.
- [ ] Tool execution remained within scope.
- [ ] Endpoint/security telemetry considered.
- [ ] Tool version/revision recorded where useful.

## sudo

- [ ] `sudo -l` reviewed.
- [ ] Allowed command identified.
- [ ] Target user identified.
- [ ] Argument restrictions reviewed.
- [ ] Wildcards reviewed.
- [ ] `NOPASSWD` interpreted correctly.
- [ ] Environment behaviour considered.
- [ ] Actual command behaviour validated.

## SUID / SGID

- [ ] SUID binaries enumerated.
- [ ] SGID binaries enumerated.
- [ ] Ownership confirmed.
- [ ] Custom binaries prioritised.
- [ ] Arguments and behaviour reviewed.
- [ ] Legitimate SUID use distinguished from exploitable use.

## Capabilities

- [ ] File capabilities enumerated.
- [ ] Exact capability confirmed.
- [ ] Binary functionality understood.
- [ ] Actual security impact validated.

## Scheduled Execution

- [ ] `/etc/crontab` reviewed where permitted.
- [ ] `/etc/cron.d/` reviewed where relevant.
- [ ] systemd services reviewed.
- [ ] systemd timers reviewed.
- [ ] Execution identity confirmed.
- [ ] Script/binary permissions checked.
- [ ] Parent directories checked.
- [ ] Trigger confirmed.

## Filesystem

- [ ] Interesting writable files validated.
- [ ] Writable directories validated.
- [ ] Parent directories reviewed.
- [ ] ACLs considered.
- [ ] Ownership confirmed.
- [ ] Mount state considered.

## Processes and Services

- [ ] Root-owned custom processes reviewed.
- [ ] Service configuration reviewed.
- [ ] Referenced scripts/binaries reviewed.
- [ ] Local listening services reviewed where relevant.

## Credentials

- [ ] Potential secrets reviewed carefully.
- [ ] Shell history treated as sensitive.
- [ ] SSH keys handled securely.
- [ ] Stale/example credentials distinguished from real secrets.
- [ ] Unnecessary authentication attempts avoided.

## Containers

- [ ] Container context identified.
- [ ] Docker group reviewed.
- [ ] Docker socket permissions reviewed.
- [ ] LXD/LXC access reviewed where relevant.
- [ ] Host/container privilege boundary understood.

## Security Controls

- [ ] SELinux considered.
- [ ] AppArmor considered.
- [ ] no_new_privs considered where relevant.
- [ ] seccomp considered where relevant.
- [ ] Read-only mounts considered.

## Validation

- [ ] LinPEAS output treated as candidate evidence.
- [ ] Native validation performed.
- [ ] Effective permissions confirmed.
- [ ] Privileged consumer identified.
- [ ] Trigger identified.
- [ ] Security controls considered.
- [ ] False-positive explanations considered.
- [ ] Security impact established.

## Evidence

- [ ] Current identity retained.
- [ ] Relevant LinPEAS output retained.
- [ ] Native command evidence retained.
- [ ] Permissions retained.
- [ ] Privileged execution context documented.
- [ ] Trigger documented.
- [ ] Sensitive data redacted where appropriate.
- [ ] Finding describes underlying weakness rather than LinPEAS.

## Cleanup

- [ ] LinPEAS script removed where required.
- [ ] Temporary output removed where required.
- [ ] Assessment evidence retained appropriately.
- [ ] Legitimate system logs preserved.

---

# Related Tool Notes

[Privilege Escalation Tools](index.md)

[linux-smart-enumeration](linux-smart-enumeration.md)

Windows equivalents:

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

## Official PEASS-ng Resources

[PEASS-ng - GitHub](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

[PEASS-ng Releases](https://github.com/peass-ng/PEASS-ng/releases){ target="_blank" rel="noopener noreferrer" }

---

## Supporting Linux Privilege Escalation References

[HackTricks - Linux Privilege Escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html){ target="_blank" rel="noopener noreferrer" }

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

[Linux man-pages - capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }

[Linux man-pages - sudoers](https://man7.org/linux/man-pages/man5/sudoers.5.html){ target="_blank" rel="noopener noreferrer" }

[systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html){ target="_blank" rel="noopener noreferrer" }

[systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use LinPEAS like this:

```text
Run LinPEAS
    |
    v
Look for Red Text
    |
    v
Assume Root
```

Use it like this:

```text
Understand Current Identity
        |
        v
Run LinPEAS
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

LinPEAS is valuable because it quickly surveys a large number of Linux privilege escalation areas.

It identifies where to investigate.

The tester determines whether those observations form a real path to additional privilege.
